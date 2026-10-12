"""Development-only judge evidence and explicit human review decisions."""
from datetime import datetime, timezone
import re

from analysis.helpers import _state

MODE = "unsupported_policy_claim"


def snapshot():
    inputs = _state.read_json(_state.state_path("hw5_trace_inputs.json"), [])
    current = {}
    for row in _state.read_jsonl(_state.state_path("hw5_labels", MODE + ".jsonl")):
        if not row.get("superseded_by"):
            current[row["trace_id"]] = row
    dev = _state.read_json(_state.state_path("splits.json"), {}).get(MODE, {}).get("dev", [])
    history = _state.read_json(_state.state_path("judges", "_history_" + MODE + ".json"), {}).get("versions", [])
    versions = []
    for item in history:
        judge = _state.read_json(_state.state_path("judges", item["judge_id"] + ".json"))
        cache = judge.get("predictions", {}).get(judge["prompt_hash"], {})
        critiques = judge.get("critiques", {}).get(judge["prompt_hash"], {})
        # Never expose the complete cache: it may include held-out results.
        versions.append({"judge_id": judge["judge_id"], "status": judge["status"],
                         "model": judge["model"], "predictions": {t: cache[t] for t in dev if t in cache},
                         "critiques": {t: critiques[t] for t in dev if t in critiques}})
    return {"mode": MODE, "versions": versions,
            "records": [{"trace_id": r["trace_id"], "trace": r["trace"],
                         "human_label": current[r["trace_id"]]["label"],
                         "human_note": current[r["trace_id"]]["note"]}
                        for r in inputs if r["trace_id"] in dev],
            "reviews": _state.read_json(_state.state_path("hw5_development_reviews.json"), {"rows": []})}


def review(payload):
    jid, tid = payload.get("judge_id", ""), payload.get("trace_id", "")
    if not re.fullmatch(MODE + r"-v[0-2]", jid):
        raise ValueError("Invalid HW5 judge version")
    data = snapshot()
    judge = next((j for j in data["versions"] if j["judge_id"] == jid), None)
    record = next((r for r in data["records"] if r["trace_id"] == tid), None)
    if not judge or not record or tid not in judge["predictions"]:
        raise ValueError("Review requires a saved development prediction")
    if judge["status"] == "frozen":
        raise ValueError("Development decisions are locked for the frozen judge")
    if judge["predictions"][tid] == record["human_label"]:
        raise ValueError("This trace is not a development disagreement")
    if not payload.get("inspected_complete_trace"):
        raise ValueError("Confirm that you inspected the complete evidence")
    decision = payload.get("decision")
    if decision not in ("judge_wrong", "label_wrong", "boundary_unclear"):
        raise ValueError("Choose who is wrong or whether the boundary needs clarification")
    note = str(payload.get("note", "")).strip()
    if not note:
        raise ValueError("Explain your decision with trace evidence")
    row = {"judge_id": jid, "trace_id": tid, "decision": decision, "note": note,
           "human_confirmed": True, "created_at": datetime.now(timezone.utc).isoformat()}
    reviews = data["reviews"]
    reviews.setdefault("rows", []).append(row)
    _state.write_json(_state.state_path("hw5_development_reviews.json"), reviews)
    return row
