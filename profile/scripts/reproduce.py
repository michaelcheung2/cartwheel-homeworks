"""Recalculate saved development scores and check protected HW9 inputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    preparation = json.loads((ROOT / "reports/hw9-preparation.json").read_text())
    for relative, expected in preparation["protected_sha256"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Protected file changed: {relative}")
    paths = [ROOT / preparation["hw8_baseline"],
             *sorted((ROOT / "optimize/results").glob("development-hw9-*.json"))]
    for path in paths:
        result = json.loads(path.read_text())
        cases = result["cases"]
        score = round(sum(r["passes"] / r["runs"] for r in cases) / len(cases), 6)
        writes = [r for r in cases if r["expected_write"]]
        reliability = round(sum(r["passes"] == 5 for r in writes) / len(writes), 6)
        assert result["split"] == "development"
        assert result["score"] == score and result["write_pass_5"] == reliability
        assert sum(r["runs"] for r in cases) == result["evaluated_case_runs"]
        print(f"{path.name}: score={score}, write_pass_5={reliability}")
    print("Protected evaluation cases, tests, frozen judges and optimization state unchanged.")


if __name__ == "__main__":
    main()
