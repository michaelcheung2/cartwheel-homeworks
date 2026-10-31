"""Recalculate HW8 scores from saved observations without rerunning models."""

from __future__ import annotations

import json
import statistics

from optimize.workflow import RESULTS_DIR, read_json


def main() -> None:
    rows = []
    for number in range(1, 5):
        result = read_json(RESULTS_DIR / f"test-configuration-{number}.json")
        cases = result["cases"]
        score = round(statistics.mean(c["passes"] / c["runs"] for c in cases), 6)
        writes = [c for c in cases if c["expected_write"]]
        write_pass_5 = round(statistics.mean(c["passes"] == 5 for c in writes), 6)
        assert score == result["score"]
        assert write_pass_5 == result["write_pass_5"]
        rows.append({"configuration": number, "model": result["model"],
                     "recalculated_score": score, "recalculated_write_pass_5": write_pass_5})
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
