"""Offline checks for HW6 grading against real tool writes in isolated worlds."""

import json
from pathlib import Path

import pytest

from agent.agent import escalate_to_human_logic, get_order_logic, issue_refund_logic
from agent.auth import AuthContext
from replay.rollout import apply_checks


def _transcript(calls):
    return {"final_reply": "A human will follow up.", "turns": [{"tool_calls": calls}]}


@pytest.mark.parametrize("encoded", [False, True])
def test_ticket_check_requires_success_and_a_matching_database_write(world_copy, encoded):
    ctx = AuthContext(user_id=9502, role="support")
    args = {"summary": "Disputed charge on order 9045", "context": "Investigate order 9045"}
    check = {"check": "escalation_created", "user_id": 9502, "order_id": 9045}
    case = {"expected": {"checks": [check]}}
    # Narration and a failed call do not satisfy a required handoff.
    assert not apply_checks(case, _transcript([]), world_copy)["passed"]
    failed_call = {"name": "escalate_to_human", "args": args, "result": {"ok": False}}
    assert not apply_checks(case, _transcript([failed_call]), world_copy)["passed"]

    result = escalate_to_human_logic(ctx, **args)
    call = {"name": "escalate_to_human", "args": args, "result": json.dumps(result) if encoded else result}
    assert apply_checks(case, _transcript([call]), world_copy)["passed"]
    # A ticket for another user/order, an invented ID, or mismatched tool
    # arguments cannot satisfy this case.
    check["user_id"] = 9503
    assert not apply_checks(case, _transcript([call]), world_copy)["passed"]
    check["user_id"] = 9502
    check["order_id"] = 904
    assert not apply_checks(case, _transcript([call]), world_copy)["passed"]
    check["order_id"] = 9045
    call["result"] = {"ok": True, "ticket_id": 999999}
    assert not apply_checks(case, _transcript([call]), world_copy)["passed"]
    call["result"] = result
    call["args"] = {**args, "context": "An unrelated issue"}
    assert not apply_checks(case, _transcript([call]), world_copy)["passed"]


def test_queued_full_refund_check_rejects_partial_amount(world_copy):
    case = {"expected": {"checks": [{
        "check": "refund_status", "order_id": 4455,
        "status": "queued_for_approval", "amount_cents": 24000,
    }]}}
    ctx = AuthContext(user_id=1, role="shopper")
    transcript = _transcript([])
    assert not apply_checks(case, transcript, world_copy)["passed"]
    assert issue_refund_logic(ctx, 4455, 120, "damaged")["status"] == "queued_for_approval"
    assert not apply_checks(case, transcript, world_copy)["passed"]
    assert issue_refund_logic(ctx, 4455, 240, "damaged")["status"] == "queued_for_approval"
    assert apply_checks(case, transcript, world_copy)["passed"]


def test_drafted_cases_are_satisfied_by_real_authorized_tool_writes(world_copy):
    cases = [json.loads(line) for line in Path("eval_cases/cases.jsonl").read_text().splitlines()]
    for case in cases:
        ci = case["input"]
        ctx = AuthContext(user_id=ci["user_id"], role=ci["role"], store_id=ci.get("store_id"))
        calls = []
        refund = next((c for c in case["expected"]["checks"] if c["check"] == "refund_status"), None)
        if refund:
            args = {"order_id": refund["order_id"], "amount_usd": refund["amount_cents"] / 100, "reason": "no longer wanted"}
            order_result = get_order_logic(ctx, args["order_id"])
            assert order_result["ok"] is True
            result = issue_refund_logic(ctx, **args)
            assert result["ok"] is True
            calls = [{"name": "get_order", "args": {"order_id": args["order_id"]}, "result": order_result},
                     {"name": "issue_refund", "args": args, "result": result}]
        else:
            args = {"summary": ci["message"], "context": ci["message"]}
            result = escalate_to_human_logic(ctx, **args)
            calls = [{"name": "escalate_to_human", "args": args, "result": result}]
        assert apply_checks(case, _transcript(calls), world_copy)["passed"], case["id"]
