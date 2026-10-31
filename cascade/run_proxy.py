"""Local HW9 proxy, development threshold selection, and one frozen test check.

Oracle verdicts are read from HW5; they are never regenerated. No human
labels or oracle predictions enter the proxy request.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import urllib.request
from pathlib import Path

from analysis.helpers.normalization import normalize_trace

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "cascade/results"
JUDGE_PATH = ROOT / "analysis/state/judges/unsupported_policy_claim-v2.json"
INPUTS_PATH = ROOT / "analysis/state/hw5_trace_inputs.json"
SPLITS_PATH = ROOT / "analysis/state/splits.json"
MODEL = "qwen3:0.6b"
INSTRUCTION = (
    "\n\n--- Trace to evaluate ---\n{content}\n\n"
    "First write a critique of the trace against the criterion. "
    "Use specific evidence from the provided trace. Then return result "
    "as exactly Pass when the named failure is absent, or Fail when present."
    "\nAlso state confidence in your verdict as a number from 0 to 1."
)
SCHEMA = {"type": "object", "properties": {
    "critique": {"type": "string"},
    "result": {"type": "string", "enum": ["Pass", "Fail"]},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1}},
    "required": ["critique", "result", "confidence"], "additionalProperties": False}


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context():
    judge = read(JUDGE_PATH)
    assert judge["status"] == "frozen"
    inputs = {r["trace_id"]: normalize_trace(r)["text"] for r in read(INPUTS_PATH)}
    splits = read(SPLITS_PATH)[judge["mode"]]
    oracle = judge["predictions"][judge["prompt_hash"]]
    labels = {}
    for line in (ROOT / "analysis/state/hw5_labels/unsupported_policy_claim.jsonl").read_text().splitlines():
        row = json.loads(line)
        if not row.get("superseded_by"):
            assert row["human_confirmed"] and row["label_convention"] == "pass_positive"
            labels[row["trace_id"]] = row["label"]
    return judge, inputs, splits, oracle, labels


def predict(prompt):
    request = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps({
        "model": MODEL, "stream": False, "think": False,
        "messages": [{"role": "user", "content": prompt}], "format": SCHEMA,
        "options": {"temperature": 0, "num_ctx": 16384, "num_predict": 1024},
    }).encode(), headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response:
        raw = json.load(response)
    usage = {"input_tokens": int(raw["prompt_eval_count"]),
             "output_tokens": int(raw["eval_count"]),
             "latency_seconds": round(time.perf_counter() - started, 4)}
    try:
        value = json.loads(raw["message"]["content"])
        confidence = value["confidence"]
        if (value["result"] not in ("Pass", "Fail") or
                not isinstance(value.get("critique"), str) or not value["critique"].strip() or
                isinstance(confidence, bool) or not isinstance(confidence, (float, int)) or
                not 0 <= confidence <= 1):
            raise ValueError("invalid structured verdict")
        return {**usage, "verdict": int(value["result"] == "Pass"),
                "confidence": confidence, "critique": value["critique"], "error": None}
    except (ValueError, KeyError, TypeError) as error:
        # Invalid proxy output always falls back, even at threshold zero.
        return {**usage, "verdict": None, "confidence": None,
                "error": type(error).__name__ + ": invalid proxy output"}


def run(split):
    judge, inputs, splits, _, _ = context()
    if split == "test":
        selection = read(RESULTS / "selection.json")
        assert selection["development_results_sha256"] == sha(RESULTS / "proxy-dev.json")
        assert selection["config_sha256"] == sha(RESULTS / "config.json")
    config = read(RESULTS / "config.json")
    identity = {"model": MODEL, "judge_sha256": sha(JUDGE_PATH),
                "inputs_sha256": sha(INPUTS_PATH), "splits_sha256": sha(SPLITS_PATH),
                "config_sha256": sha(RESULTS / "config.json"), "split": split,
                "trace_ids": splits[split]}
    path = RESULTS / f"proxy-{split}.json"
    result = read(path) if path.exists() else {"identity": identity, "records": {}}
    if result["identity"] != identity:
        raise ValueError("Saved proxy run differs; refusing to overwrite")
    for tid in splits[split]:
        if tid in result["records"]:
            continue
        prompt = judge["prompt_text"] + INSTRUCTION.format(content=inputs[tid])
        result["records"][tid] = predict(prompt)
        save(path, result)
    print(json.dumps({"split": split, "completed_proxy_calls": len(result["records"]),
                      "oracle_calls": 0, "paid_calls": 0}))


def metrics(split, threshold):
    _, _, splits, oracle, human = context()
    records = read(RESULTS / f"proxy-{split}.json")["records"]
    if set(records) != set(splits[split]):
        raise ValueError("Proxy run is incomplete")
    disagreements, human_disagreements, proxy_count = [], [], 0
    for tid, row in records.items():
        use_proxy = row["error"] is None and row["confidence"] >= threshold
        verdict = row["verdict"] if use_proxy else oracle[tid]
        proxy_count += use_proxy
        if verdict != oracle[tid]:
            disagreements.append(tid)
        if verdict != human[tid]:
            human_disagreements.append(tid)
    n = len(records)
    return {"threshold": threshold, "n": n,
            "agreement_with_oracle": (n - len(disagreements)) / n,
            "agreement_with_human_labels": (n - len(human_disagreements)) / n,
            "proxy_share": proxy_count / n, "proxy_count": proxy_count,
            "oracle_fallback_count": n - proxy_count,
            "disagreement_count": len(disagreements), "disagreement_trace_ids": disagreements,
            "human_disagreement_count": len(human_disagreements),
            "cost_per_1000_verdicts_usd": 0.0,
            "cost_basis": "Local model API fees only. Qwen 0.6B uses fewer parameters than Llama 8B; neither has an API fee. No demonstrated dollar savings. Oracle fallback cost uses saved verdicts at zero API fee; actual production fallbacks would make calls.",
            "proxy_input_tokens": sum(r["input_tokens"] for r in records.values()),
            "proxy_output_tokens": sum(r["output_tokens"] for r in records.values())}


def thresholds():
    config = read(RESULTS / "config.json")
    rows = [metrics("dev", t) for t in config["thresholds"]]
    fields = ["threshold", "agreement_with_oracle", "agreement_with_human_labels",
              "proxy_share", "cost_per_1000_verdicts_usd"]
    with (RESULTS / "thresholds.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    eligible = [r for r in rows if r["agreement_with_oracle"] >= config["minimum_agreement"]]
    recommendation = min(eligible, key=lambda r: r["threshold"]) if eligible else None
    best = max(r["agreement_with_oracle"] for r in rows)
    rejected_candidate = min((r for r in rows if r["agreement_with_oracle"] == best),
                             key=lambda r: r["threshold"]) if not eligible else None
    save(RESULTS / "development-review.json", {"rows": rows, "recommended": recommendation,
         "rejected_candidate_for_test_check": rejected_candidate})
    print(json.dumps({"recommended": recommendation,
                      "rejected_candidate_for_test_check": rejected_candidate}, indent=2))


def select(threshold):
    if (RESULTS / "proxy-test.json").exists() or (RESULTS / "selection.json").exists():
        raise ValueError("Threshold already frozen or test started")
    config = read(RESULTS / "config.json")
    review = read(RESULTS / "development-review.json")
    recommended = review["recommended"]
    candidate = recommended or review["rejected_candidate_for_test_check"]
    if candidate is None or threshold != candidate["threshold"]:
        raise ValueError("Select the recorded development candidate without accessing test results")
    save(RESULTS / "selection.json", {"threshold": threshold,
         "minimum_agreement": config["minimum_agreement"],
         "development_results_sha256": sha(RESULTS / "proxy-dev.json"),
         "config_sha256": sha(RESULTS / "config.json"),
         "selected_before_test": True, "selected_at_epoch": time.time(),
         "development_requirement_met": recommended is not None,
         "decision_basis": "Lowest threshold meeting requirement" if recommended else
         "No threshold met requirement: reject cascade; test the lowest threshold at best development agreement without retuning"})


def check():
    selection = read(RESULTS / "selection.json")
    assert selection["development_results_sha256"] == sha(RESULTS / "proxy-dev.json")
    assert selection["config_sha256"] == sha(RESULTS / "config.json")
    value = metrics("test", selection["threshold"])
    value["minimum_agreement"] = selection["minimum_agreement"]
    value["agreement_requirement_met"] = value["agreement_with_oracle"] >= value["minimum_agreement"]
    value["development_requirement_met"] = selection["development_requirement_met"]
    value["cascade_accepted"] = value["agreement_requirement_met"] and value["development_requirement_met"]
    value["deployment_ready"] = False
    value["deployment_reason"] = "The student-approved HW5 oracle is restricted to human review suggestions; the cascade inherits its errors."
    save(RESULTS / "check.json", value)
    print(json.dumps(value, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run-dev", "thresholds", "select", "run-test", "check"])
    parser.add_argument("--threshold", type=float)
    args = parser.parse_args()
    if args.command == "run-dev": run("dev")
    elif args.command == "thresholds": thresholds()
    elif args.command == "select": select(args.threshold)
    elif args.command == "run-test": run("test")
    else: check()


if __name__ == "__main__":
    main()
