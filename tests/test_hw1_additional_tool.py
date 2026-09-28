"""Tests for the additional support tool identified during Homework 1 Part B."""

from __future__ import annotations

import pytest

from agent import db, tools
from agent.agent import TOOLS_BY_ROLE
from agent.auth import AuthContext

SHOPPER_1 = AuthContext(user_id=1, role="shopper")
MERCHANT_STORE_2 = AuthContext(user_id=9002, role="merchant", store_id=2)
SUPPORT = AuthContext(user_id=9501, role="support")


def test_support_lists_customer_orders_newest_first(world: dict) -> None:
    with db.connection() as conn:
        expected = db.list_orders_for_user(conn, 1, tools.DEFAULT_ORDER_LIMIT)

    result = tools.list_customer_orders(SUPPORT, 1)

    assert result["ok"] is True
    assert result["user_id"] == 1
    assert result["count"] == len(expected)
    assert result["count"] <= tools.DEFAULT_ORDER_LIMIT
    assert [order["order_id"] for order in result["orders"]] == [
        order.id for order in expected
    ]


@pytest.mark.parametrize("ctx", [SHOPPER_1, MERCHANT_STORE_2])
def test_non_support_is_denied_before_target_disclosure(
    world: dict, ctx: AuthContext
) -> None:
    result = tools.list_customer_orders(ctx, 999_999)

    assert result["ok"] is False
    assert result["error"] == "permission_denied"
    assert "999999" not in result["reason"]


def test_support_gets_structured_target_errors(world: dict) -> None:
    missing = tools.list_customer_orders(SUPPORT, 999_999)
    assert missing["ok"] is False
    assert missing["error"] == "not_found"

    merchant = tools.list_customer_orders(SUPPORT, 9002)
    assert merchant["ok"] is False
    assert merchant["error"] == "invalid_argument"


def test_tool_is_registered_only_for_support() -> None:
    names_by_role = {
        role: {tool.name for tool in registered_tools}
        for role, registered_tools in TOOLS_BY_ROLE.items()
    }

    assert "list_customer_orders" in names_by_role["support"]
    assert "list_customer_orders" not in names_by_role["shopper"]
    assert "list_customer_orders" not in names_by_role["merchant"]
