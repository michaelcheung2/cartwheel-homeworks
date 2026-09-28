"""Regression test for the Homework 1 Part C prompt improvement."""

from agent.agent import render_system_prompt
from agent.auth import AuthContext


def test_account_changes_require_tool_based_escalation() -> None:
    prompt = render_system_prompt(AuthContext(user_id=1, role="shopper"))
    normalized = " ".join(prompt.split())

    assert "account changes of any kind" in normalized
    assert "always call escalate_to_human" in normalized
    assert "do not merely tell the user to contact support" in normalized
