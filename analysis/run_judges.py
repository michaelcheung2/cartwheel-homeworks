"""HW5: fixed evidence, confirmed labels, DocETL runs and saved metrics.

Run from the repository root: uv run python -m analysis.run_judges --help.
Human decisions are read from durable files, never inferred from predictions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from contextlib import contextmanager
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from analysis.helpers import (
    freeze_judge, judge_alignment, register_judge, run_judge, split_labels,
)
from analysis.helpers import _state, scale
from observability.instrument import load_env

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "analysis/state"
REPORT = ROOT / "analysis/report"
MODE = "unsupported_policy_claim"
MODEL = "ollama_chat/llama3.1:8b"
INPUTS = STATE / "hw5_trace_inputs.json"
COMPLETION = {"api_base": "http://localhost:11434", "temperature": 0,
              "max_tokens": 1024, "num_ctx": 16384}


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def labels(mode):
    live = {}
    for row in _state.read_jsonl(STATE / "hw5_labels" / f"{mode}.jsonl"):
        if row.get("superseded_by"):
            continue
        if row.get("label_convention") != "pass_positive" or row.get("label") not in (0, 1):
            raise ValueError("HW5 labels must use 1=Pass, 0=Fail")
        if not row.get("human_confirmed"):
            raise ValueError("A proposed label cannot enter evaluation")
        live[row["trace_id"]] = row
    return live


def independent_records(mode, corpus, scenarios):
    """Curate independent representatives; preserve excluded labels/history."""
    grouped = defaultdict(list)
    for tid, label in labels(mode).items():
        trace = corpus[tid]
        scenario = scenarios[trace["metadata"]["cartwheel.scenario_id"]]
        dimensions = scenario["tuple"]
        if scenario.get("data_quality_case_id"):
            group = ["data_quality_case", scenario["data_quality_case_id"]]
        elif dimensions.get("order_id"):
            group = ["order_intent", dimensions["order_id"], dimensions["intent"]]
        else:
            group = ["scenario", scenario["id"]]
        grouped[json.dumps(group)].append(label)
    selected, groups = [], []
    for key, candidates in sorted(grouped.items()):
        # Human-confirmed failures are deliberately enriched for validation.
        chosen = min(candidates, key=lambda r: (
            r["label"], corpus[r["trace_id"]]["timestamp"], r["trace_id"],
        ))
        selected.append(chosen["trace_id"])
        groups.append({"group": json.loads(key), "selected_trace_id": chosen["trace_id"],
                       "excluded_trace_ids": [r["trace_id"] for r in candidates if r != chosen]})
    return selected, groups


def evidence_messages(selected, corpus):
    """Only observed turns through the selected reply; no review metadata."""
    target = corpus[selected]
    session = target["metadata"]["cartwheel.session_id"]
    turns = sorted((t for t in corpus.values()
                    if t["metadata"]["cartwheel.session_id"] == session),
                   key=lambda t: (t["timestamp"], t["trace_id"]))
    messages = []
    for turn in turns:
        for step in turn["steps"]:
            if step["role"] == "tool":
                data = {k: step.get(k) for k in ("name", "input", "output", "error")}
                # The shared normalizer reads text. Include the tool name and
                # full result in that text, preserving call/result pairing.
                messages.append({"role": "tool", "text": json.dumps(data, ensure_ascii=False)})
            elif step["role"] in ("user", "assistant"):
                messages.append({"role": step["role"], "text": step.get("text", "")})
        if turn["trace_id"] == selected:
            break
    if not messages or messages[-1]["role"] != "assistant":
        raise ValueError(f"Missing selected reply for {selected}")
    return messages


def prepare_inputs(mode=MODE):
    source = ROOT / "analysis/review_app/.cache/traces.json"
    corpus = {r["trace_id"]: r for r in read(source)}
    scenarios = {r["id"]: r for r in _state.read_jsonl(ROOT / "scenarios/support_scenarios.jsonl")}
    eligible, groups = independent_records(mode, corpus, scenarios)
    current = labels(mode)
    counts = {"Pass": sum(current[t]["label"] == 1 for t in eligible),
              "Fail": sum(current[t]["label"] == 0 for t in eligible)}
    if min(counts.values()) < 30:
        raise ValueError(f"Need 30 independent labels per class before splitting: {counts}")
    records = [{"trace_id": tid, "trace": evidence_messages(tid, corpus)} for tid in sorted(eligible)]
    sessions = [corpus[t]["metadata"]["cartwheel.session_id"] for t in eligible]
    if len(set(sessions)) != len(sessions):
        raise ValueError("More than one selected record in a conversation")
    if INPUTS.exists():
        if read(INPUTS) != records:
            raise ValueError("Saved judge inputs differ; refusing to replace the fixed export")
        return {"status": "reused_fixed_export", "records": len(records), "classes": counts}
    _state.write_json(INPUTS, records)
    _state.write_json(STATE / "hw5_eligibility.json", {
        "mode": mode, "status": "ready", "created_at": now(),
        "selection_rule": "One per scenario; collapse same-order/same-intent and documented data-quality-case variants. Prefer confirmed Fail, then earliest timestamp/ID. Curated validation sample, not prevalence. No predictions used.",
        "all_confirmed_labels": len(current), "eligible_counts": counts,
        "eligible_trace_ids": sorted(eligible), "groups": groups,
    })
    _state.write_json(STATE / "hw5_input_manifest.json", {
        "created_at": now(), "source": str(source.relative_to(ROOT)),
        "source_sha256": digest(source), "source_details": read(STATE / "corpus_source.json"),
        "inputs_sha256": digest(INPUTS), "records": len(records), "mode": mode,
        "policy": "Observed earlier turns through selected reply; actual tool results/retrieval passages. No labels, annotations, expected outcomes or scenario metadata in judge input.",
    })
    return {"status": "prepared", "records": len(records), "classes": counts}


def check_inputs():
    manifest = read(STATE / "hw5_input_manifest.json")
    if digest(INPUTS) != manifest["inputs_sha256"]:
        raise ValueError("Fixed inputs changed after preparation")
    if manifest.get("splits_sha256") and digest(STATE / "splits.json") != manifest["splits_sha256"]:
        raise ValueError("Saved splits changed after assignment")
    os.environ["CARTWHEEL_JUDGE_TRACE_SOURCE"] = str(INPUTS)


def split_data(mode=MODE):
    check_inputs()
    existing = _state.read_json(STATE / "splits.json", {})
    if mode in existing:
        raise ValueError("Split already saved; do not split again")
    records = read(INPUTS)
    assignment = split_labels(mode, fractions=(.20, .40, .40), seed=7,
                              min_per_class=10, eligible_trace_ids=[r["trace_id"] for r in records])
    current = labels(mode)
    counts = {name: {"Pass": sum(current[t]["label"] == 1 for t in ids),
                     "Fail": sum(current[t]["label"] == 0 for t in ids)}
              for name, ids in assignment.items()}
    _state.write_json(REPORT / "hw5-split-counts.json", counts)
    manifest = read(STATE / "hw5_input_manifest.json")
    manifest["splits_sha256"] = digest(STATE / "splits.json")
    _state.write_json(STATE / "hw5_input_manifest.json", manifest)
    return counts


def configure():
    load_env()
    check_inputs()
    # The supplied helpers otherwise require a paid-provider key before
    # dispatching. A live classifier below still uses their DocETL map,
    # while explicitly routing the chosen model to local Ollama.
    os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"


def execute(judge_id, split):
    configure()
    judge = read(STATE / "judges" / f"{judge_id}.json")
    if split == "test" and judge.get("status") != "frozen":
        raise ValueError("Freeze the student-selected judge before accessing test")
    if not judge["model"].startswith("ollama_chat/"):
        raise ValueError("This runner is authorized for local Ollama only")
    settings = judge.get("execution_settings", {})
    if any(settings.get(k) != v for k, v in COMPLETION.items()):
        raise ValueError("Execution settings differ from the registered judge")
    run_judge(judge_id, split=split, batch_size=10,
              classify=lambda prompt, ids: scale._run_docetl_map(
                  prompt, ids, judge["model"], completion_kwargs=COMPLETION,
                  max_threads=1, output_mode="structured_output"))
    return save_metrics(judge_id, split)


def save_metrics(judge_id, split):
    check_inputs()
    judge = read(STATE / "judges" / f"{judge_id}.json")
    metrics = judge_alignment(judge_id, split=split)
    metrics["class_counts"] = {"Pass": metrics["tp"] + metrics["fn"],
                               "Fail": metrics["tn"] + metrics["fp"]}
    metrics["model"] = judge["model"]
    metrics["inputs_sha256"] = digest(INPUTS)
    _state.write_json(REPORT / f"{split}-{judge_id}.json", metrics)
    return metrics


def run_development(mode, prompt_path):
    check_inputs()
    history = _state.read_json(STATE / "judges" / f"_history_{mode}.json", {"versions": []})
    if len(history["versions"]) >= 3:
        raise ValueError("HW5 permits the initial prompt and at most two revisions")
    if history["versions"]:
        require_reviewed_disagreements(history["versions"][-1]["judge_id"])
    record = register_judge(mode, Path(prompt_path).read_text(), judge_model=MODEL)
    path = STATE / "judges" / f"{record['judge_id']}.json"
    judge = read(path)
    judge["execution_settings"] = {**COMPLETION, "max_threads": 1,
                                   "output_mode": "structured_output",
                                   "model_digest_prefix": "46e0c10c039e"}
    judge["handout_model_departure"] = "Student chose local Llama instead of required gpt-4o-mini."
    _state.write_json(path, judge)
    # Registration persists the ID before calls; resume that ID on failure.
    print(json.dumps({"registered": record, "resume": f"--resume {record['judge_id']} --split dev"}), flush=True)
    return execute(record["judge_id"], "dev")


def require_reviewed_disagreements(judge_id):
    metrics_path = REPORT / f"dev-{judge_id}.json"
    if not metrics_path.exists():
        raise ValueError("Resume and complete the registered development run before revising")
    metrics = read(metrics_path)
    reviews = _state.read_json(STATE / "hw5_development_reviews.json", {"rows": []})
    reviewed = {r["trace_id"] for r in reviews["rows"]
                if r["judge_id"] == judge_id and r.get("human_confirmed")}
    if set(metrics["disagreements"]) - reviewed:
        raise ValueError("Human review of every development disagreement is required before revising or freezing")


def run_test(judge_id):
    judge = read(STATE / "judges" / f"{judge_id}.json")
    if judge.get("status") != "frozen":
        decision = _state.read_json(STATE / "hw5_final_decision.json", {})
        if not decision.get("human_confirmed") or decision.get("judge_id") != judge_id:
            raise ValueError("Student must select this final judge before freezing")
        require_reviewed_disagreements(judge_id)
        freeze_judge(judge_id)
    return execute(judge_id, "test")


@contextmanager
def comparison_state(path):
    previous = os.environ.get("CARTWHEEL_ANALYSIS_STATE")
    os.environ["CARTWHEEL_ANALYSIS_STATE"] = str(path)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("CARTWHEEL_ANALYSIS_STATE", None)
        else:
            os.environ["CARTWHEEL_ANALYSIS_STATE"] = previous


def run_comparison(source_judge_id):
    """Compare Qwen on dev only, without altering the primary judge history."""
    configure()
    source = read(STATE / "judges" / f"{source_judge_id}.json")
    if source["status"] != "frozen":
        raise ValueError("Choose and freeze the main judge before the model comparison")
    model = "ollama_chat/qwen3:8b"
    root = STATE / "model_comparison/qwen3_8b"
    options = {**COMPLETION, "reasoning_effort": "none"}
    with comparison_state(root):
        history = _state.read_json(_state.state_path("judges", f"_history_{source['mode']}.json"))
        if history:
            judge_id = history["versions"][0]["judge_id"]
            comparison = _state.read_json(_state.state_path("judges", judge_id + ".json"))
            if comparison["prompt_text"] != source["prompt_text"] or comparison["model"] != model:
                raise ValueError("Existing comparison differs; preserve it")
        else:
            _state.write_json(_state.state_path("splits.json"), read(STATE / "splits.json"))
            _state.write_jsonl(_state.state_path("hw5_labels", source["mode"] + ".jsonl"),
                               _state.read_jsonl(STATE / "hw5_labels" / (source["mode"] + ".jsonl")))
            record = register_judge(source["mode"], source["prompt_text"], model)
            judge_id = record["judge_id"]
            comparison = _state.read_json(_state.state_path("judges", judge_id + ".json"))
            comparison.update(source_judge_id=source_judge_id, comparison_scope="development_only",
                              execution_settings={**options, "max_threads": 1,
                                                  "output_mode": "structured_output",
                                                  "model_digest_prefix": "500a1f067a9f"})
            _state.write_json(_state.state_path("judges", judge_id + ".json"), comparison)
        print(json.dumps({"comparison_model": model, "split": "dev", "source_prompt": source_judge_id,
                          "resume": f"--compare {source_judge_id}"}), flush=True)
        run_judge(judge_id, split="dev", batch_size=10,
                  classify=lambda prompt, ids: scale._run_docetl_map(
                      prompt, ids, model, completion_kwargs=options,
                      max_threads=1, output_mode="structured_output"))
        metrics = judge_alignment(judge_id, split="dev")
        metrics.update(model=model, source_judge_id=source_judge_id,
                       comparison_scope="development_only", inputs_sha256=digest(INPUTS),
                       prompt_text_sha256=hashlib.sha256(source["prompt_text"].encode()).hexdigest(),
                       class_counts={"Pass": metrics["tp"] + metrics["fn"],
                                     "Fail": metrics["tn"] + metrics["fp"]})
    _state.write_json(REPORT / "hw5-qwen-development-comparison.json", metrics)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--split-data", action="store_true")
    action.add_argument("--develop", type=Path)
    action.add_argument("--resume")
    action.add_argument("--test")
    action.add_argument("--metrics")
    action.add_argument("--compare")
    parser.add_argument("--mode", default=MODE)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    args = parser.parse_args()
    if args.prepare:
        result = prepare_inputs(args.mode)
    elif args.split_data:
        result = split_data(args.mode)
    elif args.develop:
        result = run_development(args.mode, args.develop)
    elif args.resume:
        result = execute(args.resume, args.split)
    elif args.test:
        result = run_test(args.test)
    elif args.compare:
        result = run_comparison(args.compare)
    else:
        result = save_metrics(args.metrics, args.split)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
