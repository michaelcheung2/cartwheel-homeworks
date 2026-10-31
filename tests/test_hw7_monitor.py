"""Offline HW7 checks; synthetic fixtures are never monitoring evidence."""
import json
from copy import deepcopy
from datetime import datetime, timezone

import pytest

from monitoring import run
from monitoring.correct import corrected_mode_prevalence

START = datetime(2026, 10, 10, tzinfo=timezone.utc)
END = datetime(2026, 10, 11, tzinfo=timezone.utc)
MODEL = "ollama_chat/llama3.1:8b"


def trace(i, scenario="scenario-1", session="session-1", message="hello", tool=False):
    observations = [{"id": f"generation-{i}", "type": "GENERATION", "model": MODEL,
                     "name": "chat", "startTime": START.isoformat(), "output": []}]
    if tool:
        observations.append({"id": f"tool-{i}", "type": "TOOL", "name": "get_policy",
                             "input": {"policy_id": "cw-returns"}, "output": {"ok": True},
                             "startTime": START.isoformat(), "statusMessage": None})
    return {"id": f"{i:032x}", "timestamp": START.isoformat(), "input": message,
            "output": "observed reply", "observations": observations,
            "metadata": {"cartwheel.scenario_id": scenario, "cartwheel.session_id": session,
                         "human_label": "DO NOT INCLUDE", "expected": "DO NOT INCLUDE"}}


def test_comparison_orders_turns_targets_final_trace_and_omits_labels():
    rows = [trace(2, message="follow up", tool=True), trace(1)]
    original = deepcopy(rows)
    scenarios = [{"id": "scenario-1", "opening_message": "hello", "followups": ["follow up"]}]
    records, count = run.conversation_records(rows, MODEL, START, END, scenarios)
    assert count == 2 and len(records) == 1
    record = records[0]
    assert record["id"] == f"{2:032x}"
    assert record["turn_count"] == 2 and record["tools"] == ["get_policy"]
    assert record["text"].index("user: hello") < record["text"].index("user: follow up")
    assert 'tool: {"name": "get_policy", "input":' in record["text"]
    assert "DO NOT INCLUDE" not in record["text"] and "scenario-1" not in record["text"]
    assert rows == original


@pytest.mark.parametrize("defect", ["missing", "missing_turn", "model", "retry", "duplicate"])
def test_comparison_rejects_incomparable_periods(defect):
    scenarios = [{"id": "scenario-1", "opening_message": "hello", "followups": ["follow up"]}]
    rows = [trace(1), trace(2, message="follow up")]
    if defect == "missing": rows = []
    if defect == "missing_turn": rows.pop()
    if defect == "model": rows[0]["observations"][0]["model"] = "other-model"
    if defect == "retry": rows[1]["metadata"]["cartwheel.session_id"] = "retry-session"
    if defect == "duplicate": rows.append(deepcopy(rows[0]))
    with pytest.raises(ValueError):
        run.conversation_records(rows, MODEL, START, END, scenarios)


def test_rolling_window_groups_by_session_instead_of_reused_scenario_id():
    rows = [trace(1, session="one"), trace(2, session="two")]
    records, count = run.conversation_records(rows, MODEL, START, END)
    assert len(records) == count == 2


def test_empty_window_never_calls_judge_or_scores(tmp_path):
    config = {"model": MODEL, "judge_id": "unused", "random_rate": .2,
              "risk_groups": ["policy_lookup"], "threshold": .15}
    def forbidden(*args): pytest.fail("empty windows must not call judges or scores")
    result = run.monitor(config, "empty", START, END, [], comparison=False,
                         output_dir=tmp_path, judge_fn=forbidden, score_fn=forbidden)
    assert result["status"] == "empty" and result["conversation_count"] == result["judge_calls"] == 0
    assert json.loads((tmp_path / "result.json").read_text())["corrected"] is None


def test_repeat_reuses_judged_union_and_updates_same_score_ids(monkeypatch, tmp_path):
    config = {"model": MODEL, "judge_id": "test", "judge_mode": "mode", "judge_sha256": "test",
              "random_rate": .2, "risk_groups": ["policy_lookup"], "threshold": .15,
              "bootstrap_iterations": 100, "seed": 7}
    monkeypatch.setattr(run, "frozen_judge", lambda config: {"model": MODEL})
    monkeypatch.setattr(run, "judge_test_data", lambda jid: ([1, 1, 0, 0], [1, 1, 0, 0]))
    judged, written = [], []
    def judge(jid, selected):
        judged.append([t["id"] for t in selected])
        return {t["id"]: 0 for t in selected}
    def scores(records):
        written.append(records)
        return len(records)
    rows = [trace(i, session=f"session-{i}", tool=True) for i in range(1, 11)]
    first = run.monitor(config, "after", START, END, rows, comparison=False,
                        output_dir=tmp_path, judge_fn=judge, score_fn=scores)
    second = run.monitor(config, "after", START, END, rows, comparison=False,
                         output_dir=tmp_path, judge_fn=judge, score_fn=scores)
    assert len(judged) == 1 and len(judged[0]) == 10
    assert first["judge_calls"] == 10 and second["judge_calls"] == 0
    assert written[0] == written[1]
    assert first["random_sample_count"] == first["n_sample"] == 2
    assert first["risk_sample_count"] == 10
    assert first["corrected"] == 0
    rows[0]["output"] = "changed evidence"
    with pytest.raises(ValueError, match="saved judge evidence differs"):
        run.monitor(config, "after", START, END, rows, comparison=False,
                    output_dir=tmp_path, judge_fn=judge, score_fn=scores)


def test_prevalence_rejects_unusable_held_out_judge():
    with pytest.raises(ValueError, match="no usable"):
        corrected_mode_prevalence([1, 0], [1, 0], [0, 1], bootstrap_iterations=10)


def test_history_repeat_replaces_same_period(tmp_path):
    path = tmp_path / "history.jsonl"
    row = {"period": "after", "judge_id": "test", "model": MODEL, "from": START.isoformat()}
    run.update_history(path, row)
    run.update_history(path, {**row, "scores_written": 3})
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(records) == 1 and records[0]["scores_written"] == 3


def test_score_api_targets_batch_session_and_propagates_rejected_writes(monkeypatch):
    from types import SimpleNamespace
    import langfuse
    from analysis.helpers import langfuse_io
    from monitoring.write_scores import build_score_records, post_scores

    requests = []
    def create(*, request):
        requests.append(request)
        return SimpleNamespace(id=request.id)
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    monkeypatch.setattr(langfuse_io, "is_configured", lambda: True)
    monkeypatch.setattr(langfuse, "get_client", lambda: SimpleNamespace(
        api=SimpleNamespace(score=SimpleNamespace(create=create))))
    estimate = dict(corrected=.1, ci_low=0, ci_high=.5, raw=.2, n_sample=10)
    records = build_score_records("mode", {"trace-1": 1}, {}, estimate, "after")
    assert post_scores(records) == 2
    assert requests[0].trace_id == "trace-1" and requests[0].session_id is None
    assert requests[1].trace_id is None
    assert requests[1].session_id == "cartwheel-monitor-mode-after"
    assert [r.id for r in requests] == [r["score_id"] for r in records]
    def rejected(*, request):
        raise RuntimeError("score request rejected")
    monkeypatch.setattr(langfuse, "get_client", lambda: SimpleNamespace(
        api=SimpleNamespace(score=SimpleNamespace(create=rejected))))
    with pytest.raises(RuntimeError, match="score request rejected"):
        post_scores(records)


def test_frozen_docetl_settings_wrapper_and_parser_are_preserved(monkeypatch):
    from docetl import api
    from monitoring.run_judges import judge_sample
    captured = {}
    class Pipeline:
        def __init__(self, **kwargs):
            captured.update(kwargs)
        def run(self, **kwargs):
            captured["run_kwargs"] = kwargs
            rows = [{"trace_id": "trace-1", "critique": "Observed evidence", "result": "Pass"}]
            from pathlib import Path
            Path(captured["output"].path).write_text(json.dumps(rows))
    monkeypatch.setattr(api, "Pipeline", Pipeline)
    result = judge_sample("unsupported_policy_claim-v2", [{"id": "trace-1", "text": "user: hello"}])
    operation = captured["operations"][0]
    assert operation.model == MODEL
    assert operation.litellm_completion_kwargs == {
        "api_base": "http://localhost:11434", "temperature": 0, "max_tokens": 1024, "num_ctx": 16384,
    }
    assert operation.output["mode"] == "structured_output"
    assert "--- Trace to evaluate ---\n{{ input.content }}" in operation.prompt
    assert captured["run_kwargs"] == {"max_threads": 1}
    assert result == {"trace-1": 0}  # HW5 Pass=1 becomes monitoring failure=0.
