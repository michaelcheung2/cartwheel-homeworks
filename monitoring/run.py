"""HW7: validate conversations, sample, judge, correct, and write scores.

Use --dry-run with a saved trace export for offline planning. Actual monitoring
reads Langfuse. This student's configuration permits local Ollama judges only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from analysis.helpers import _state, langfuse_io
from analysis.helpers.normalization import normalize_trace
from analysis.review_app.server import prepare_record
from monitoring.chart import prevalence_chart
from monitoring.correct import corrected_mode_prevalence
from monitoring.run_judges import judge_sample, judge_test_data, load_monitoring_judge
from monitoring.sample import DEFAULT_RISK_GROUPS, select_traces
from monitoring.write_scores import build_score_records, post_scores
from observability.instrument import load_env
from scenarios.export_langfuse import _jsonable
from scenarios.runner import load_scenarios

ROOT = Path(__file__).resolve().parents[1]


def utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("period timestamps must include a timezone")
    return result.astimezone(timezone.utc)


def fetch_period(start: datetime, end: datetime, client: Any = None) -> list[dict]:
    """Fetch full records with pagination; never silently truncate a period."""
    client = client or langfuse_io._client()
    records, page, seen = [], 1, set()
    while True:
        response = client.api.trace.list(
            page=page, limit=100, from_timestamp=start, to_timestamp=end,
            order_by="timestamp.asc",
        )
        batch = list(response.data or [])
        for summary in batch:
            if summary.id in seen:
                raise ValueError("duplicate trace across API pages; retry the read")
            seen.add(summary.id)
            records.append(_jsonable(client.api.trace.get(summary.id)))
        if len(batch) < 100:
            return records
        page += 1


def conversation_records(
    raw_traces: list[dict], model: str, start: datetime, end: datetime,
    scenarios: list[dict] | None = None,
) -> tuple[list[dict], int]:
    """Group comparison periods by scenario, rolling windows by session.

    Render exactly HW5's ordered user/assistant/tool evidence format. Neither
    labels nor scenario metadata enter the judge's text. The last trace is the
    score target. Comparison periods reject missing turns and separate retries.
    """
    expected = {s["id"]: s for s in scenarios} if scenarios is not None else None
    groups = defaultdict(list)
    seen = set()
    for raw in raw_traces:
        normalized = normalize_trace(raw)
        timestamp = utc(normalized["timestamp"])
        if not start <= timestamp < end:
            continue
        meta = normalized["meta"]
        scenario_id, session_id = meta.get("scenario_id"), meta.get("session_id")
        if expected is not None and scenario_id not in expected:
            continue
        if expected is None and not session_id:
            continue
        if not session_id:
            raise ValueError("eligible trace has no session id")
        if normalized["id"] in seen:
            raise ValueError("duplicate eligible trace id")
        seen.add(normalized["id"])
        if set(normalized["models"]) != {model}:
            raise ValueError("eligible trace has a missing or different Cartwheel model")
        # prepare_record is also used to prepare the student's HW5 evidence.
        record = prepare_record(raw)
        groups[scenario_id if expected is not None else session_id].append(record)
    if expected is not None and set(groups) != set(expected):
        missing = sorted(set(expected) - set(groups))
        raise ValueError(f"period is missing {len(missing)} scenarios: {missing[:5]}")
    conversations = []
    for key, group in sorted(groups.items()):
        group.sort(key=lambda t: (utc(t["timestamp"]), t["id"]))
        if len({t["meta"]["session_id"] for t in group}) != 1:
            raise ValueError(f"scenario {key} contains separate session retries")
        messages, tools = [], []
        for trace in group:
            tools.extend(trace["tool_names"])
            for step in trace["steps"]:
                if step["role"] == "tool":
                    data = {k: step.get(k) for k in ("name", "input", "output", "error")}
                    messages.append({"role": "tool", "text": json.dumps(data, ensure_ascii=False)})
                elif step["role"] in ("user", "assistant"):
                    messages.append({"role": step["role"], "text": step.get("text", "")})
        users = [m["text"] for m in messages if m["role"] == "user"]
        if expected is not None:
            s = expected[key]
            if users != [s["opening_message"], *(s.get("followups") or [])]:
                raise ValueError(f"scenario {key} has missing, duplicate, or changed turns")
        if not messages or messages[-1]["role"] != "assistant":
            raise ValueError("conversation has no final assistant reply")
        text = normalize_trace({"id": group[-1]["id"], "trace": messages})["text"]
        conversations.append({
            "id": group[-1]["id"], "text": text, "tools": list(dict.fromkeys(tools)),
            "turn_count": len(users), "trace_ids": [t["id"] for t in group],
            "scenario_id": group[-1]["meta"].get("scenario_id"),
            "session_id": group[-1]["meta"]["session_id"],
        })
    return conversations, len(seen)


def frozen_judge(config: dict) -> dict:
    judge = load_monitoring_judge(config["judge_id"])
    if judge["mode"] != config["judge_mode"]:
        raise ValueError("configured failure mode differs from the frozen judge")
    encoded = json.dumps(judge, sort_keys=True, ensure_ascii=False).encode()
    if hashlib.sha256(encoded).hexdigest() != config["judge_sha256"]:
        raise ValueError("frozen judge changed; preserve and review its provenance")
    if not judge["model"].startswith("ollama_chat/"):
        raise ValueError("this no-paid-API monitor permits local Ollama judges only")
    return judge


def confirm_local_model(judge: dict) -> None:
    settings = judge["execution_settings"]
    endpoint = settings["api_base"].rstrip("/") + "/api/tags"
    with urllib.request.urlopen(endpoint, timeout=10) as response:
        models = json.load(response)["models"]
    name = judge["model"].split("/", 1)[1]
    if not any(m["name"] == name and m["digest"].startswith(settings["model_digest_prefix"])
               for m in models):
        raise ValueError("local frozen judge model is missing or its digest changed")


def update_history(path: Path, record: dict) -> None:
    history = _state.read_jsonl(path)
    key = (record["period"], record["judge_id"], record["model"])
    history = [r for r in history if (r["period"], r["judge_id"], r["model"]) != key]
    history.append(record)
    history.sort(key=lambda r: (r["from"], r["period"]))
    _state.write_jsonl(path, history)


def monitor(
    config: dict, label: str, start: datetime, end: datetime, raw_traces: list[dict],
    *, comparison: bool, output_dir: Path, dry_run: bool = False,
    judge_fn=None, score_fn=None,
) -> dict:
    """Run one period; injection points are for offline tests, never evidence."""
    if start >= end:
        raise ValueError("period start must be earlier than its end")
    scenarios = load_scenarios(ROOT / config["scenarios_path"]) if comparison else None
    if comparison and len(scenarios) != 50:
        raise ValueError("comparison requires exactly 50 scenarios")
    records, trace_count = conversation_records(raw_traces, config["model"], start, end, scenarios)
    names = config["risk_groups"]
    if not names or len(set(names)) != len(names) or any(n not in DEFAULT_RISK_GROUPS for n in names):
        raise ValueError("choose at least one distinct supplied risk group")
    if comparison and config["random_rate"] != 0.2:
        raise ValueError("comparison requires a 20 percent random sample")
    if not math.isfinite(config["threshold"]) or not 0 <= config["threshold"] <= 1:
        raise ValueError("threshold must be in [0, 1]")
    plan = select_traces(records, config["random_rate"],
                         {n: DEFAULT_RISK_GROUPS[n] for n in names}, config.get("seed", 7))
    random_ids = [t["id"] for t in plan["random"]]
    risk_ids = {n: [t["id"] for t in ts] for n, ts in plan["risk_groups"].items()}
    risk_union = list(dict.fromkeys(tid for ids in risk_ids.values() for tid in ids))
    record = {
        "period": label, "judge_id": config["judge_id"], "model": config["model"],
        "from": start.isoformat(), "to": end.isoformat(), "threshold": config["threshold"],
        "scope": "comparison" if comparison else "rolling_window",
        "trace_count": trace_count, "conversation_count": len(records),
        "random_sample_count": len(random_ids), "risk_sample_count": len(risk_union),
        "risk_group_counts": {n: len(ids) for n, ids in risk_ids.items()},
        "selected_count": len(plan["to_judge"]), "judge_calls": 0,
        "judge_call_count_definition": "conversation evaluations submitted to the judge; "
        "DocETL may reuse exact cached calls. Provider request count is not measured.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_file = output_dir / "plan.json"
    _state.write_json(plan_file, {**record, "random_ids": random_ids, "risk_ids": risk_ids})
    if not records:
        record.update(status="empty", raw=None, corrected=None, ci_low=None, ci_high=None)
        _state.write_json(output_dir / "result.json", record)
        return record
    judge = frozen_judge(config)
    # Validate correction data before any potentially long model work.
    labels, predictions = judge_test_data(config["judge_id"])
    if not labels or not any(labels) or all(labels):
        raise ValueError("held-out data must contain both classes")
    se = sum(p for y, p in zip(labels, predictions) if y) / sum(labels)
    sp = sum(1 - p for y, p in zip(labels, predictions) if not y) / (len(labels) - sum(labels))
    if se + sp <= 1:
        raise ValueError("frozen judge has no usable prevalence correction")
    identity = hashlib.sha256(json.dumps({
        "judge_sha256": config["judge_sha256"],
        "selected": [{"id": t["id"], "text": t["text"]} for t in plan["to_judge"]],
    }, sort_keys=True).encode()).hexdigest()
    cache_path = output_dir / "judge-results.json"
    cached = _state.read_json(cache_path)
    if cached is not None and cached["identity"] != identity:
        raise ValueError("saved judge evidence differs; use a separate output directory")
    calls = 0 if cached else len(plan["to_judge"])
    print(f"{label}: {len(records)} conversations; {len(random_ids)} random; "
          f"{len(risk_union)} risk; {len(plan['to_judge'])} unique selected; "
          f"{calls} judge evaluations using {judge['model']} (DocETL may reuse cached calls)", flush=True)
    if dry_run:
        record.update(status="planned", planned_judge_calls=calls)
        _state.write_json(output_dir / "dry-run.json", record)
        return record
    if cached:
        verdicts = cached["verdicts"]
    else:
        if judge_fn is None:
            confirm_local_model(judge)
        verdicts = (judge_fn or judge_sample)(config["judge_id"], plan["to_judge"])
        if set(verdicts) != {t["id"] for t in plan["to_judge"]} or any(v not in (0, 1) for v in verdicts.values()):
            raise ValueError("judge did not return one binary verdict for every selected conversation")
        _state.write_json(cache_path, {"identity": identity, "verdicts": verdicts, "judge_calls": calls})
    random_verdicts = {tid: verdicts[tid] for tid in random_ids}
    risk_verdicts = {tid: verdicts[tid] for tid in risk_union}
    _state.write_json(output_dir / "verdicts.json", {
        "random": random_verdicts, "risk": risk_verdicts, "risk_groups": risk_ids,
    })
    estimate = corrected_mode_prevalence(
        list(random_verdicts.values()), labels, predictions,
        seed=config.get("seed", 7), bootstrap_iterations=config.get("bootstrap_iterations", 20000),
    )
    scores = build_score_records(config["judge_mode"], random_verdicts, risk_verdicts, estimate, label)
    _state.write_json(output_dir / "scores.json", scores)
    record.update(estimate, judge_calls=calls, threshold_crossed=estimate["corrected"] >= config["threshold"],
                  action="human_error_analysis" if estimate["corrected"] >= config["threshold"] else "continue_monitoring",
                  status="scores_pending")
    _state.write_json(output_dir / "result.json", record)
    record["scores_written"] = (score_fn or post_scores)(scores)
    if record["scores_written"] != len(scores):
        raise ValueError("not all score writes completed")
    record["status"] = "completed"
    _state.write_json(output_dir / "result.json", record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "monitoring/config.json")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--period", choices=("before", "after"))
    scope.add_argument("--last-hours", type=float)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--trace-file", type=Path, help="saved export, permitted only with --dry-run")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    load_env()
    config = json.loads(args.config.read_text())
    if args.trace_file and not args.dry_run:
        parser.error("saved exports support offline planning only; actual monitoring reads Langfuse")
    if args.period:
        period = next(p for p in config["periods"] if p["label"] == args.period)
        if not period.get("from") or not period.get("to"):
            parser.error(f"{args.period} period is pending a complete observed run")
        start, end, label = utc(period["from"]), utc(period["to"]), args.period
    else:
        if not math.isfinite(args.last_hours) or args.last_hours <= 0:
            parser.error("--last-hours must be positive and finite")
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=args.last_hours)
        label = f"window-{start.isoformat()}-{end.isoformat()}"
    output = args.output_dir or ROOT / "monitoring/output" / label.replace(":", "-")
    output.mkdir(parents=True, exist_ok=True)
    try:
        if args.trace_file:
            data = json.loads(args.trace_file.read_text())
            traces = data["traces"] if isinstance(data, dict) else data
        else:
            traces = fetch_period(start, end)
        result = monitor(config, label, start, end, traces, comparison=bool(args.period),
                         output_dir=output, dry_run=args.dry_run)
        if not args.dry_run:
            history = ROOT / "monitoring/history.jsonl" if args.period else ROOT / "monitoring/output/window-history.jsonl"
            update_history(history, result)
            if args.period:
                points = [r for r in _state.read_jsonl(history) if r.get("status") == "completed"]
                if {r["period"] for r in points} == {"before", "after"}:
                    svg = prevalence_chart([{**r, "label": r["period"]} for r in points],
                                           config["threshold"], config["judge_mode"])
                    (ROOT / "monitoring/prevalence.svg").write_text(svg)
        print(json.dumps(result, indent=2))
    except Exception as error:
        _state.write_json(output / "error.json", {"error_type": type(error).__name__, "message": str(error)})
        raise


if __name__ == "__main__":
    main()
