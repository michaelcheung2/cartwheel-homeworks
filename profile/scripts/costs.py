"""Rebuild HW9 call-site costs from saved evidence, without model calls."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from analysis.helpers.normalization import normalize_trace
from monitoring.run import conversation_records, utc

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads((ROOT / path).read_text())


def estimate(text):
    # Historical judge runs saved no API usage. This is explicitly an estimate,
    # not a model tokenizer or a reconstructed provider invoice.
    return math.ceil(len(text.encode("utf-8")) / 4)


def main():
    config = read("optimize/config.json")
    rows, seen, examples = [], set(), []
    source_names = ["traces/support_traces.json",
                    "monitoring/output/before-live-traces.json",
                    "monitoring/output/after-live-traces.json"]
    observations = []
    for name in source_names:
        for trace in read(name)["traces"]:
            for obs in trace.get("observations", []):
                if obs.get("type") != "GENERATION" or obs["id"] in seen:
                    continue
                seen.add(obs["id"])
                observations.append(obs)
    for model in sorted({o["model"] for o in observations}):
        group = [o for o in observations if o["model"] == model]
        inputs = sum(int(o["promptTokens"]) for o in group)
        outputs = sum(int(o["completionTokens"]) for o in group)
        price = config["prices_per_million_tokens_usd"][model]
        rows.append(["customer_conversation", "server/app.py:202",
                     "SDK customer model generations; API token counts; observation IDs deduplicated across exports",
                     model, len(group), inputs, outputs,
                     (inputs * price["input"] + outputs * price["output"]) / 1e6])
        for obs in sorted(group, key=lambda o: o["promptTokens"] + o["completionTokens"], reverse=True)[:3]:
            examples.append({"observation_id": obs["id"], "trace_id": obs["traceId"],
                             "input_tokens": obs["promptTokens"], "output_tokens": obs["completionTokens"]})
    inputs_by_id = {r["trace_id"]: normalize_trace(r)["text"]
                    for r in read("analysis/state/hw5_trace_inputs.json")}
    hw5_in = hw5_out = hw5_calls = 0
    for path in sorted((ROOT / "analysis/state/judges").glob("unsupported_policy_claim-v*.json")):
        judge = json.loads(path.read_text())
        for prompt_hash, predictions in judge["predictions"].items():
            critiques = judge.get("critiques", {}).get(prompt_hash, {})
            for tid, verdict in predictions.items():
                hw5_calls += 1
                hw5_in += estimate(judge["prompt_text"] + inputs_by_id[tid])
                hw5_out += estimate(critiques.get(tid, "") + ("Pass" if verdict else "Fail"))
    rows.append(["judge", "analysis/helpers/scale.py:267",
                 "HW5 saved logical verdicts across versions; tokens ESTIMATED UTF-8 bytes/4; excludes unknown schema overhead and retries/cache reuse",
                 "ollama_chat/llama3.1:8b", hw5_calls, hw5_in, hw5_out, 0.0])
    judge = read("analysis/state/judges/unsupported_policy_claim-v2.json")
    hw7_in = hw7_calls = 0
    for period in ("before", "after"):
        plan = read(f"monitoring/output/{period}/plan.json")
        results = read(f"monitoring/output/{period}/judge-results.json")
        raw = read(f"monitoring/output/{period}-live-traces.json")["traces"]
        conversations, _ = conversation_records(raw, plan["model"], utc(plan["from"]), utc(plan["to"]))
        by_id = {c["id"]: c["text"] for c in conversations}
        for tid in results["verdicts"]:
            hw7_calls += 1
            hw7_in += estimate(judge["prompt_text"] + by_id[tid])
    rows.append(["judge", "monitoring/run_judges.py:138",
                 "HW7 saved logical verdicts; input tokens ESTIMATED UTF-8 bytes/4; output ESTIMATED 1024-token configured cap per verdict (upper bound); provider requests/cache hits unknown",
                 judge["model"], hw7_calls, hw7_in, hw7_calls * 1024, 0.0])
    target = ROOT / "profile/results"
    target.mkdir(parents=True, exist_ok=True)
    with (target / "costs.csv").open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["cost_category", "call_site", "purpose", "model", "calls", "input_tokens", "output_tokens", "cost_usd"])
        writer.writerows(rows)
    (target / "cost-evidence.json").write_text(json.dumps({
        "source_exports": source_names, "customer_examples": examples,
        "cost_basis": "Local Ollama API fees only; excludes hardware/electricity. All call sites tie at $0. Tokens rank resource usage, not measured dollar savings.",
        "historical_judge_usage": "Missing API usage; estimates are labeled in CSV. Logical saved verdict counts are not provider request counts.",
        "call_site_mapping": "Customer exports identify chat generations, not source lines. Mapped to the verified server Runner.run entry point; judges mapped to their DocETL dispatch sites.",
    }, indent=2) + "\n")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
