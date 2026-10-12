"""Offline checks for HW5 evidence boundaries and resume protections."""
import json

import pytest

from analysis import run_judges as hw5
from analysis.helpers import _state, judge_alignment, register_judge, run_judge


def test_evidence_keeps_tool_name_error_and_excludes_future_and_review_data():
    corpus = {
        "before": {"trace_id": "before", "timestamp": "1", "metadata": {
            "cartwheel.session_id": "session", "answer": "Fail"}, "steps": [
            {"role": "user", "text": "Prior request"},
            {"role": "tool", "name": "escalate_to_human", "input": {"summary": "request"},
             "output": {"ticket_id": 1, "sla_hours": 24}, "error": None},
            {"role": "assistant", "text": "A human will respond"}]},
        "selected": {"trace_id": "selected", "timestamp": "2", "metadata": {
            "cartwheel.session_id": "session"}, "note": "human Fail label", "steps": [
            {"role": "user", "text": "Follow-up"},
            {"role": "tool", "name": "get_policy", "input": {"policy_id": "missing"},
             "output": None, "error": "Actual retrieval exception"},
            {"role": "assistant", "text": "Selected reply"}]},
        "future": {"trace_id": "future", "timestamp": "3", "metadata": {
            "cartwheel.session_id": "session"}, "steps": [
            {"role": "assistant", "text": "Future evidence must be excluded"}]},
    }
    messages = hw5.evidence_messages("selected", corpus)
    assert messages[-1] == {"role": "assistant", "text": "Selected reply"}
    text = json.dumps(messages)
    assert "escalate_to_human" in text and "Actual retrieval exception" in text
    assert "Future evidence" not in text and "human Fail label" not in text
    assert "metadata" not in text and '"answer"' not in text


def test_fixed_inputs_hash_detects_mutation(tmp_path, monkeypatch):
    path = tmp_path / "inputs.json"
    path.write_text('[{"trace_id":"a","trace":[]}]')
    (tmp_path / "hw5_input_manifest.json").write_text(json.dumps({
        "inputs_sha256": hw5.digest(path)}))
    monkeypatch.setattr(hw5, "STATE", tmp_path)
    monkeypatch.setattr(hw5, "INPUTS", path)
    hw5.check_inputs()
    path.write_text('[]')
    with pytest.raises(ValueError, match="Fixed inputs changed"):
        hw5.check_inputs()


def test_pass_positive_metrics_and_cached_resume(tmp_path, monkeypatch):
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", str(tmp_path))
    _state.write_jsonl(tmp_path / "hw5_labels/mode.jsonl", [
        {"trace_id": "p1", "label": 1}, {"trace_id": "p2", "label": 1},
        {"trace_id": "f1", "label": 0}, {"trace_id": "f2", "label": 0}])
    _state.write_json(tmp_path / "splits.json", {"mode": {
        "dev": ["p1", "p2", "f1", "f2"], "test": ["p1"]}})
    judge = register_judge("mode", "Test prompt", "ollama_chat/llama3.1:8b")
    calls = []
    def classify(prompt, ids):
        calls.append(ids)
        return {tid: {"p1": 1, "p2": 0, "f1": 0, "f2": 1}[tid] for tid in ids}
    run_judge(judge["judge_id"], split="dev", classify=classify)
    run_judge(judge["judge_id"], split="dev", classify=classify)
    assert len(calls) == 1
    metrics = judge_alignment(judge["judge_id"], "dev")
    assert (metrics["tp"], metrics["fn"], metrics["tn"], metrics["fp"]) == (1, 1, 1, 1)
    assert metrics["tpr"] == metrics["tnr"] == .5
    assert metrics["tpr_interval"][0] < .5 < metrics["tpr_interval"][1]


def test_runner_blocks_unfrozen_test_before_classifier(tmp_path, monkeypatch):
    monkeypatch.setattr(hw5, "STATE", tmp_path)
    monkeypatch.setattr(hw5, "configure", lambda: None)
    _state.write_json(tmp_path / "judges/draft.json", {
        "status": "draft", "model": "ollama_chat/llama3.1:8b"})
    monkeypatch.setattr(hw5, "run_judge", lambda *a, **kw: pytest.fail("Test model called"))
    with pytest.raises(ValueError, match="before accessing test"):
        hw5.execute("draft", "test")


def test_saved_split_cannot_be_recreated(tmp_path, monkeypatch):
    monkeypatch.setattr(hw5, "STATE", tmp_path)
    monkeypatch.setattr(hw5, "check_inputs", lambda: None)
    _state.write_json(tmp_path / "splits.json", {"mode": {"train": ["a"]}})
    monkeypatch.setattr(hw5, "split_labels", lambda *a, **kw: pytest.fail("Split overwritten"))
    with pytest.raises(ValueError, match="do not split again"):
        hw5.split_data("mode")


def test_review_view_excludes_test_predictions_and_requires_inspection(tmp_path, monkeypatch):
    from analysis.review_app import hw5 as ui
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", str(tmp_path))
    mode = ui.MODE
    jid = mode + "-v0"
    _state.write_json(tmp_path / "hw5_trace_inputs.json", [
        {"trace_id": "dev", "trace": [{"role": "assistant", "text": "Reply"}]},
        {"trace_id": "test", "trace": [{"role": "assistant", "text": "Hidden test"}]}])
    _state.write_jsonl(tmp_path / "hw5_labels" / (mode + ".jsonl"), [
        {"trace_id": "dev", "label": 0, "note": "Human evidence"},
        {"trace_id": "test", "label": 1, "note": "Test label"}])
    _state.write_json(tmp_path / "splits.json", {mode: {"dev": ["dev"], "test": ["test"]}})
    _state.write_json(tmp_path / "judges" / ("_history_" + mode + ".json"), {
        "versions": [{"judge_id": jid}]})
    _state.write_json(tmp_path / "judges" / (jid + ".json"), {
        "judge_id": jid, "prompt_hash": "hash", "status": "draft", "model": hw5.MODEL,
        "predictions": {"hash": {"dev": 1, "test": 0}},
        "critiques": {"hash": {"dev": "Dev critique", "test": "Secret test critique"}}})
    snapshot = ui.snapshot()
    assert snapshot["versions"][0]["predictions"] == {"dev": 1}
    assert "Secret test critique" not in json.dumps(snapshot)
    payload = {"judge_id": jid, "trace_id": "dev", "decision": "judge_wrong", "note": "Evidence"}
    with pytest.raises(ValueError, match="inspected"):
        ui.review(payload)
    assert not (tmp_path / "hw5_development_reviews.json").exists()
    row = ui.review({**payload, "inspected_complete_trace": True})
    assert row["human_confirmed"] and row["decision"] == "judge_wrong"


def test_docetl_local_schema_and_worker_settings_are_forwarded(monkeypatch):
    import sys
    import types
    from analysis.helpers import scale
    captured = {}
    class Config:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    class Pipeline(Config):
        def run(self, **kwargs):
            captured["run"] = kwargs
            captured["map"] = self.operations[0]
            rows = json.loads(open(self.datasets["traces"].path).read())
            for row in rows:
                row.update(critique="Offline test evidence", result="Pass")
            with open(self.output.path, "w") as handle:
                json.dump(rows, handle)
    api = types.ModuleType("docetl.api")
    for name in ("Dataset", "MapOp", "PipelineStep", "PipelineOutput"):
        setattr(api, name, Config)
    api.Pipeline = Pipeline
    monkeypatch.setitem(sys.modules, "docetl", types.ModuleType("docetl"))
    monkeypatch.setitem(sys.modules, "docetl.api", api)
    monkeypatch.setattr(scale, "load_store_traces", lambda: [
        {"trace_id": "a", "text": "Observed tool name and result"}])
    batch = scale._run_docetl_map("Criterion", ["a"], hw5.MODEL,
                                  completion_kwargs=hw5.COMPLETION, max_threads=1,
                                  output_mode="structured_output")
    assert captured["run"] == {"max_threads": 1}
    assert captured["map"].output["mode"] == "structured_output"
    assert captured["map"].litellm_completion_kwargs == hw5.COMPLETION
    assert batch == {"a": 1} and batch.critiques["a"] == "Offline test evidence"


def test_revision_requires_human_review_of_all_disagreements(tmp_path, monkeypatch):
    monkeypatch.setattr(hw5, "STATE", tmp_path)
    monkeypatch.setattr(hw5, "REPORT", tmp_path)
    _state.write_json(tmp_path / "dev-mode-v0.json", {"disagreements": ["a", "b"]})
    _state.write_json(tmp_path / "hw5_development_reviews.json", {"rows": [
        {"judge_id": "mode-v0", "trace_id": "a", "human_confirmed": True},
        {"judge_id": "mode-v0", "trace_id": "b", "human_confirmed": False}]})
    with pytest.raises(ValueError, match="every development disagreement"):
        hw5.require_reviewed_disagreements("mode-v0")
    _state.write_json(tmp_path / "hw5_development_reviews.json", {"rows": [
        {"judge_id": "mode-v0", "trace_id": t, "human_confirmed": True} for t in ("a", "b")]})
    hw5.require_reviewed_disagreements("mode-v0")


def test_comparison_restores_primary_state_even_after_error(tmp_path, monkeypatch):
    import os
    primary = str(tmp_path / "primary")
    monkeypatch.setenv("CARTWHEEL_ANALYSIS_STATE", primary)
    with pytest.raises(RuntimeError):
        with hw5.comparison_state(tmp_path / "comparison"):
            assert _state.state_root() == tmp_path / "comparison"
            raise RuntimeError("Interrupted comparison")
    assert os.environ["CARTWHEEL_ANALYSIS_STATE"] == primary


def test_comparison_requires_fixed_final_prompt(tmp_path, monkeypatch):
    monkeypatch.setattr(hw5, "STATE", tmp_path)
    monkeypatch.setattr(hw5, "configure", lambda: None)
    _state.write_json(tmp_path / "judges/draft.json", {"status": "draft"})
    with pytest.raises(ValueError, match="freeze the main judge"):
        hw5.run_comparison("draft")
