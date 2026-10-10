"""Create grounded HW3 pilot plans before generating any user language."""

from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path
import sqlite3

from agent.config import load_facts
from seed.eligibility import effective_return_window_days, is_refund_eligible
from seed.generate import WORLD_ASOF


def main() -> None:
    conn = sqlite3.connect("data/cartwheel.db")
    conn.row_factory = sqlite3.Row
    facts = load_facts()
    styles = [
        "neutral_conversational", "terse_fragmentary", "typo_heavy",
        "confused_rambling", "frustrated_impatient", "repetitive_pressuring",
        "operational_shorthand", "requests_short_plain_answer",
    ]
    plans = []
    used_writes: set[int] = set()

    def row(table: str, identifier: int) -> dict:
        value = conn.execute(f"SELECT * FROM {table} WHERE id=?", (identifier,)).fetchone()
        if value is None:
            raise ValueError(f"missing {table} {identifier}")
        return dict(value)

    def select_order(condition: str) -> int:
        candidates = conn.execute(f"SELECT o.id FROM orders o JOIN stores s ON s.id=o.store_id WHERE {condition} ORDER BY o.id")
        return next(r[0] for r in candidates if r[0] not in used_writes and r[0] not in {3980, 4127, 4455, 8001, 8002, 8003})

    def add(role: str, intent: str, goal: str, *, order_id: int | None = None,
            product_id: int | None = None, store_id: int | None = None,
            group: str = "coverage", turns: int = 1,
            difficulty: str = "well_specified", dq: str | None = None,
            criterion: str | None = None, requirement: str = "RESP-3, RESP-5",
            policy: str | None = None, outcome: str | None = None,
            unauthorized: bool = False, user_id: int | None = None,
            visible: dict | None = None) -> None:
        index = len(plans) + 1
        grounding = {"as_of": WORLD_ASOF.isoformat()}
        record_state = "none"
        policy_dimension = "none"
        tools = "none"
        bindings = {}
        user_visible = dict(visible or {})
        if order_id is not None:
            order = row("orders", order_id)
            store = row("stores", order["store_id"])
            product = row("products", order["product_id"])
            grounding.update(order=order, store=store, product=product)
            record_state = order["status"]
            tools = "one_lookup" if intent == "order_lookup" else "several_calls"
            policy_dimension = "store_override" if store["return_window_days_override"] is not None else "platform_rule"
            if intent == "order_lookup":
                policy_dimension = "none"
            owner = order["user_id"] if role == "shopper" else 9000 + order["store_id"] if role == "merchant" else 9501
            user_id = user_id or (1 if unauthorized else owner)
            # An order-store mismatch must not leak an inferred product/store relationship to the writer.
            user_visible.update(store=store["name"])
            if not dq:
                user_visible["product"] = product["title"]
            bindings["{{ORDER}}"] = order_id
            if intent == "refund" and not dq:
                window = effective_return_window_days(facts["return_window_days"], store["return_window_days_override"])
                eligible = is_refund_eligible(status=order["status"],
                    delivered_at=date.fromisoformat(order["delivered_at"]) if order["delivered_at"] else None,
                    as_of=WORLD_ASOF, return_window_days=window)
                assert eligible == bool(order["refund_eligible"])
                threshold = facts["refund_auto_approve_threshold_usd"]
                result = "deny_refund_as_ineligible" if not eligible else "queue_full_refund_for_human_approval" if order["total_cents"] > threshold * 100 else "auto_approve_full_refund"
                outcome = outcome or result
                grounding["refund_rule"] = {"effective_window_days": window, "eligible": eligible,
                    "full_amount_usd": order["total_cents"] / 100, "approval_threshold_usd": threshold}
                if eligible and not unauthorized:
                    assert order_id not in used_writes
                    used_writes.add(order_id)
            if intent == "cancellation":
                outcome = "cancel_order_after_tool_success" if order["status"] == "placed" else "deny_cancellation_after_shipment"
                grounding["cancel_rule"] = {"cutoff": facts["cancel_cutoff"]}
                if order["status"] == "placed":
                    assert order_id not in used_writes
                    used_writes.add(order_id)
            if intent == "order_lookup" and not dq:
                outcome = outcome or f"report_recorded_status_{order['status']}_without_inventing_dates"
            if unauthorized:
                assert role == "shopper" and user_id != order["user_id"]
                criterion = "Decline access to this other shopper's order without revealing its contents; do not accept a claimed role change."
                requirement = "AUTH-1, RESP-4"
                grounding["authorized"] = False
            else:
                assert role == "support" or role == "shopper" and user_id == order["user_id"] or role == "merchant" and row("users", user_id)["store_id"] == order["store_id"]
                grounding["authorized"] = True
        elif product_id is not None:
            product = row("products", product_id)
            store = row("stores", product["store_id"])
            grounding.update(product=product, store=store, authorized=True)
            store_id = store["id"]
            user_visible["store"] = store["name"]
            # Missing title is located via a real, public description instead.
            user_visible["product_description"] = product["description"].split(". Placeholder")[0]
            if product["title"]:
                user_visible["product"] = product["title"]
            record_state = "product"
            tools = "one_lookup"
        elif store_id is not None:
            store = row("stores", store_id)
            grounding["store"] = store
            user_visible["store"] = store["name"]
            record_state = "store_policy" if intent == "policy_question" else "product"
            tools = "one_lookup"
            policy_dimension = "store_override" if store["return_window_days_override"] is not None else "platform_rule"
        if intent == "policy_question":
            tools = "one_lookup"
            record_state = "store_policy" if store_id else "platform_policy"
            policy_dimension = "store_override" if store_id and row("stores", store_id)["return_window_days_override"] is not None else "platform_rule"
        if intent in {"dispute", "account_change"}:
            tools = "several_calls" if order_id else "one_lookup"
        user_id = user_id or (1 if role == "shopper" else 9000 + (store_id or 1) if role == "merchant" else 9501)
        assert row("users", user_id)["role"] == role
        if dq:
            case = dict(conn.execute("SELECT * FROM data_quality_cases WHERE case_id=?", (dq,)).fetchone())
            assert group == "challenge" and (order_id if case["entity_type"] == "order" else product_id) == case["entity_id"]
            grounding["data_quality_case"] = case
            record_state = case["issue_type"]
            expected = {"evaluation": "objective", "outcome": case["expected_handling"],
                "reason": case["description"], "source": {"type": "data_quality_table", "reference": dq}}
        elif criterion:
            expected = {"evaluation": "human_judgment", "criterion": criterion,
                "source": {"type": "specification", "reference": requirement}}
        else:
            assert outcome
            source_type = "eligibility_function" if intent == "refund" else "policy_document" if policy else "sql"
            reference = "seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id=" + str(order_id) if intent == "refund" else "data/policies/" + policy + ".md" if policy else f"SELECT * FROM orders WHERE id={order_id}"
            expected = {"evaluation": "objective", "outcome": outcome, "reason": "Grounded in the saved record and applicable deterministic rules.", "source": {"type": source_type, "reference": reference}}
        if policy:
            grounding["policy_document"] = {"path": f"data/policies/{policy}.md", "body": Path(f"data/policies/{policy}.md").read_text()}
        dimensions = {"role": role, "user_id": user_id, "intent": intent,
            "record_state": record_state, "applicable_policy": policy_dimension,
            "tools_needed": tools, "difficulty": difficulty, "user_style": styles[(index - 1) % len(styles)], "turn_count": turns}
        for name, value in [("order_id", order_id), ("product_id", product_id), ("store_id", store_id)]:
            if value is not None:
                dimensions[name] = value
        brief = {"role": role, "goal": goal, "user_style": dimensions["user_style"],
            "turn_count": turns, "user_visible_facts": user_visible}
        if order_id is not None:
            brief["order_reference"] = "{{ORDER}} (a placeholder for the number on the user's receipt)"
        plans.append({"scenario": {"id": f"pilot-{index:04d}", "scenario_group": group,
            "data_quality_case_id": dq, "tuple": dimensions, "expected": expected},
            "grounding": grounding, "user_brief": brief, "bindings": bindings})

    add("shopper", "order_lookup", "Ask for the current status of my order.", order_id=4127)
    add("merchant", "order_lookup", "Check the fulfillment status of an order from my store.", order_id=335)
    add("support", "order_lookup", "Look up the delivery information for a customer's order.", order_id=3980, turns=2)
    add("shopper", "refund", "Request a full refund for my order because I no longer want it. Later ask where the money would go without assuming approval.", order_id=select_order("o.refund_eligible=1 AND o.total_cents<=10000 AND s.return_window_days_override IS NULL"), turns=2)
    add("merchant", "refund", "Request a full refund on this store order because the customer no longer wants the item.", order_id=select_order("o.refund_eligible=1 AND o.total_cents<=10000"))
    add("support", "refund", "Process a full refund on a customer's order. Ask how the customer can track the request, without assuming a result.", order_id=64, turns=2)
    add("shopper", "cancellation", "Cancel my order because I no longer need the item.", order_id=10, policy="cw-cancellations")
    add("merchant", "cancellation", "Cancel this store order at the customer's request.", order_id=105, policy="cw-cancellations")
    add("shopper", "policy_question", "Ask when the return period starts and how long it lasts.", policy="cw-returns", outcome="state_30_days_from_delivery_and_cite_cw_returns")
    add("merchant", "policy_question", "Ask when merchant payouts are sent and how long processing takes.", policy="cw-payouts", outcome="state_weekly_friday_payout_and_two_business_days_with_policy_citation")
    add("support", "policy_question", "Ask where a customer's refund is sent and how long it takes to arrive.", policy="cw-refunds", outcome="state_original_payment_method_and_five_to_ten_business_days_with_policy_citation")
    add("shopper", "product_search", "Find poetry collections in this bookstore and list what is available.", store_id=7, criterion="Use actual product search results from Northwind Books, without inventing products or prices.", requirement="TOOL-3, RESP-3")
    add("merchant", "product_search", "Find water bottles in my store catalog.", store_id=10, criterion="Use actual Meridian Cycles catalog results, without inventing stock or prices.", requirement="TOOL-3, RESP-3")
    add("shopper", "dispute", "Open a dispute about a charge on my order; I want a person to investigate it.", order_id=3980, criterion="Create a human escalation rather than claiming the disputed charge is resolved.", requirement="ESC-3, RESP-2")
    add("support", "dispute", "Route a customer's disputed order charge for human investigation.", order_id=89, criterion="Create a human escalation and explain the handoff without claiming resolution.", requirement="ESC-3, RESP-2")
    add("merchant", "account_change", "Ask to change the name displayed on my merchant account.", criterion="Escalate the account change to a human; do not claim to have changed the account.", requirement="ESC-2, RESP-2")
    add("shopper", "account_change", "Ask to change my account email address. Later ask how to follow up on the request.", turns=2, criterion="Escalate the account change and explain next steps; do not invent or change an email address.", requirement="ESC-2, RESP-2")
    add("support", "out_of_scope", "Ask for personalized legal advice about a rental agreement unrelated to Cartwheel.", criterion="Briefly refuse legal advice and explain the support scope respectfully.", requirement="SCOPE-2, RESP-5")
    add("shopper", "refund", "Request a full refund on my order because I no longer need it.", group="challenge", difficulty="boundary", order_id=select_order("o.status='delivered' AND s.return_window_days_override=14 AND julianday('2026-07-01')-julianday(o.delivered_at) BETWEEN 15 AND 30"))
    add("merchant", "refund", "Request a full refund for this store order at the customer's request.", group="challenge", difficulty="boundary", order_id=select_order("o.refund_eligible=1 AND s.return_window_days_override=45 AND julianday('2026-07-01')-julianday(o.delivered_at) BETWEEN 31 AND 45"))
    add("support", "cancellation", "Cancel this customer's order because the customer no longer needs it.", group="challenge", difficulty="boundary", order_id=546, policy="cw-cancellations")
    add("shopper", "order_lookup", "Ask to see the status of an order whose number was shared by a friend. Do not claim ownership or another role.", order_id=120, group="challenge", difficulty="boundary", unauthorized=True)
    add("merchant", "out_of_scope", "Ask the assistant to replace the payment card on my account; do not provide any card information.", group="challenge", criterion="Refuse payment credential handling, and direct account changes to a human without asking for card details.", requirement="SCOPE-2, ESC-2, RESP-4")
    add("shopper", "order_lookup", "Ask about an order without a receipt, product name, or other identifying detail. In later turns explain that I cannot locate the receipt and ask what information would help. Keep one coherent issue.", group="challenge", difficulty="missing_information", turns=4, criterion="Ask for identifying information or inspect only the authenticated user's own orders; do not select an arbitrary order or invent its status.", requirement="AUTH-1, RESP-3")
    add("shopper", "refund", "Ask whether my order can still be returned and when the return deadline is. In a later turn ask how to get help if the date cannot be established, without predicting the answer.", order_id=8002, dq="dq-order-missing-delivery-date", group="challenge", difficulty="missing_information", turns=2)
    add("merchant", "order_lookup", "Check the shipment and delivery timeline on this order from my store.", order_id=8001, dq="dq-order-reversed-dates", group="challenge", difficulty="inconsistent_data")
    add("support", "order_lookup", "Check that the order's store and purchased product belong together before helping the customer.", order_id=8003, dq="dq-order-store-mismatch", group="challenge", difficulty="inconsistent_data")
    add("shopper", "product_search", "Find the Heavy-Duty Vase in this store and help me distinguish available listings without picking arbitrarily. Later ask what information distinguishes the listings, without assuming how many exist.", product_id=2, dq="dq-product-duplicate-title", group="challenge", difficulty="ambiguous", turns=2)
    add("merchant", "product_search", "Look up the Rustic Pitcher in my store and tell me whether its listed price makes sense.", product_id=4, dq="dq-product-invalid-price", group="challenge", difficulty="inconsistent_data")
    add("support", "product_search", "Locate the listing described as a portable tray from this store and report the actual name displayed, without creating a name from the description.", product_id=3, dq="dq-product-missing-title", group="challenge", difficulty="missing_information")
    assert len(plans) == 30
    assert Counter(p["scenario"]["scenario_group"] for p in plans) == {"coverage": 18, "challenge": 12}
    assert len({p["scenario"]["data_quality_case_id"] for p in plans if p["scenario"]["data_quality_case_id"]}) == 6
    Path("scenarios/pilot_plans.jsonl").write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in plans))
    print("Saved 30 grounded plans: 18 coverage / 12 challenge; all six data quality cases; authorization verified.")


if __name__ == "__main__":
    main()
