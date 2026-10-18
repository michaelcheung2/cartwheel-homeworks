"""Index Harbor 0.23's separate trial files for the course reporting format."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_job_result(job_dir: Path) -> dict[str, Any]:
    """Preserve the raw summary and index observed trials in start-time order.

    Older course fixtures already include trial_results. Harbor 0.23 instead
    writes each trial to <trial_name>/result.json. Retain every outcome and
    exception; never infer rewards from aggregate means or retry a trial.
    """
    path = job_dir / "result.json"
    result = json.loads(path.read_text())
    if "trial_results" in result:
        return result
    trials = [json.loads(p.read_text()) for p in job_dir.glob("*/result.json")]
    if not trials or len(trials) != result.get("n_total_trials"):
        raise ValueError("Harbor trial files do not match the job's total trial count")
    names = [trial.get("trial_name") for trial in trials]
    if any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError("Harbor trial files need distinct trial names")
    trials.sort(key=lambda trial: (
        datetime.fromisoformat(trial["started_at"]), trial["trial_name"]
    ))
    raw_path = job_dir / "harbor-result.json"
    if raw_path.exists() and json.loads(raw_path.read_text()) != result:
        raise ValueError("Preserved Harbor summary differs from the current raw summary")
    if not raw_path.exists():
        raw_path.write_bytes(path.read_bytes())
    result["trial_results"] = trials
    result["cartwheel_raw_result"] = raw_path.name
    result["cartwheel_trial_order"] = "per-trial started_at, then trial_name; indexed in result.json"
    temporary = job_dir / "result.json.tmp"
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(path)
    return result
