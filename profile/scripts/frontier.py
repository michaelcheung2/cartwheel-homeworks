"""Regenerate the HW9 development frontier from completed saved runs."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "optimize/results/development-final-ollama_chat_llama3.1:8b-20261031-164040.json"


def main():
    paths = [BASELINE, *sorted((ROOT / "optimize/results").glob("development-hw9-*.json"))]
    results = [json.loads(p.read_text()) for p in paths]
    if any(r["split"] != "development" for r in results):
        raise ValueError("HW9 uses development cases only")
    rows = []
    for result in results:
        score, cost = result["score"], result["cost_per_100_conversations_usd"]
        dominated = any(r["score"] >= score and r["cost_per_100_conversations_usd"] <= cost
                        and (r["score"] > score or r["cost_per_100_conversations_usd"] < cost)
                        for r in results)
        rows.append({"candidate": "hw8-final" if result is results[0] else result["candidate"],
                     "model": result["model"], "development_score": score,
                     "write_pass_5": result["write_pass_5"],
                     "cost_per_100_conversations_usd": cost,
                     "median_latency_seconds": result["median_latency_seconds"],
                     "frontier_status": "dominated" if dominated else "frontier"})
    path = ROOT / "profile/results/frontier.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
