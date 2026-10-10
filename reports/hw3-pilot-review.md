# HW3 pilot results: student review

All 30 runs completed, with 39 exported traces covering 30 unique scenario IDs. Coverage: 18 completed; challenge: 12 completed. These counts describe execution, not correctness. Model: `ollama_chat/llama3.1:8b`.

## Required human decision

Open the linked Langfuse traces for at least the ten cases below. For each case, check whether the scenario is valid and whether the observed behavior conflicts with its grounded expectation or SPEC. The student confirmed the judgments below; actual decisions are now recorded in `scenarios/pilot_review.jsonl`.

If you agree after reviewing all ten cases, confirm that **all ten scenarios are valid; failures are 0004, 0006, 0007, 0008, 0018, 0025, 0026, and 0027; no failure is confirmed for 0001 or 0009; no scenario changes are requested**. Otherwise name the IDs and your changes. The confirmed decisions are saved in `scenarios/pilot_review.jsonl`. That required file now exists and records the confirmed decisions.

Use the course Langfuse login and project that worked for HW2. Multi-turn cases have a link for every turn. Compare the visible final answer with actual tool observations; JSON printed in an answer does not execute a tool.

## Review index

| Scenario | Group / role | Proposed valid | Proposed failure | Trace(s) |
| --- | --- | --- | --- | --- |
| pilot-0001 | coverage / shopper | yes | no | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/50fbdf3f90ad1f01307d66fa1f8b910f) |
| pilot-0009 | coverage / shopper | yes | no | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/619439f31cbe7dbfd41025c0bfdefc5e) |
| pilot-0004 | coverage / shopper | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/dd491b6fbed166029e904bb898f75db6) · [turn 2](http://localhost:3000/project/cartwheel-dev/traces/d4eb00a7953d11558ee7a99bd9eb65f3) |
| pilot-0006 | coverage / support | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/775a7fe0c2f26f1d1e65849cf86929d9) · [turn 2](http://localhost:3000/project/cartwheel-dev/traces/3f8149924a6c02839b5da6dd47bcf592) |
| pilot-0007 | coverage / shopper | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/a3b1657998257c2d41993d5e9d68763d) |
| pilot-0008 | coverage / merchant | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/789690f032532db2c279148a50a6c5b6) |
| pilot-0018 | coverage / support | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/c0becfab520eeeaf45818989f27306f8) |
| pilot-0025 | challenge / shopper | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/fe7dedaa1fa85c7412122a1504387883) · [turn 2](http://localhost:3000/project/cartwheel-dev/traces/c6046ecf1c83587b3a0b17da7d052b05) |
| pilot-0026 | challenge / merchant | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/bc68454635dd522fe4bc40ea0a6ada14) |
| pilot-0027 | challenge / support | yes | yes | [turn 1](http://localhost:3000/project/cartwheel-dev/traces/d9b9b79352e45f252a93b98a6df61880) |

## pilot-0001

Expected: report_recorded_status_delivered_without_inventing_dates.

Source: `SELECT * FROM orders WHERE id=4127`.

**Turn 1 — user:** I ordered a Heavy-Duty Vase from Blue Heron Ceramics, order #4127. Could you check its current status?

**Agent (verbatim):**

```text
The status of your order #4127 is "delivered".
```

**Actual tool calls:** get_order.

**Evidence supporting the proposed judgment:** get_order returned status=delivered for authorized order 4127. The answer reports delivered, matching the SQL row.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": "2026-06-19",
    "order_id": 4127,
    "ordered_at": "2026-06-14",
    "product_id": 1,
    "quantity": 1,
    "refund_eligible": true,
    "shipped_at": "2026-06-16",
    "status": "delivered",
    "store_id": 1,
    "store_name": "Blue Heron Ceramics",
    "total_usd": 84
  }
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0009

Expected: state_30_days_from_delivery_and_cite_cw_returns.

Source: `data/policies/cw-returns.md`.

**Turn 1 — user:** When does the return period start, and how long does it last on Cartwheel?

**Agent (verbatim):**

```text
The return period on Cartwheel starts from the delivery date and lasts for 30 days. This is according to the Cartwheel return policy (cw-returns). Please note that individual stores may override this window, so it's always best to check the store's policies as well.
```

**Actual tool calls:** search_help_center.

**Evidence supporting the proposed judgment:** The answer states 30 days from delivery and cites cw-returns. search_help_center actually returned cw-returns; facts.yaml confirms the duration and store-override caveat.

`search_help_center` result:

```json
{
  "ok": true,
  "results": [
    {
      "policy_id": "cw-cancellations",
      "score": 2.075,
      "snippet": "# Cartwheel order cancellation policy\n\nAn order can be cancelled at no cost any time before the store ships it. Once an order has shipped it can no longer be cancelled; the buyer should instead wait for delivery and request a return under the Cartwheel return policy.",
      "title": "Cartwheel order cancellation policy"
    },
    {
      "policy_id": "cw-returns",
      "score": 2.047,
      "snippet": "# Cartwheel return policy\n\nItems bought on Cartwheel can be returned within 30 days of delivery. The window counts from the delivery date, not the purchase date. Items must be in the condition described by the store's listing. Individual stores may override this window; see the store overrides polic",
      "title": "Cartwheel return policy"
    },
    {
      "policy_id": "store-cascade-audio-policy",
      "score": 1.782,
      "snippet": "# Cascade Audio store policy\n\nCascade Audio follows the Cartwheel platform return window of 30 days from delivery. Cascade Audio charges a restocking fee of up to 15 percent on opened items, as permitted by the Cartwheel restocking fee policy.",
      "title": "Cascade Audio store policy"
    }
  ]
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0004

Expected: auto_approve_full_refund.

Source: `seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id=117`.

**Turn 1 — user:** I think I made a mistake with the Midnight Bath Salts from Fern & Fog Skincare, I was going to give them as a gift but now I don't think they'd get used. Can I get a full refund for order #117?

**Agent (verbatim):**

```text
I'm going to look up the store's return policy (cw-returns) to see if a full refund is possible, given that the order is already delivered. 

{"name": "get_policy", "parameters": {"store_id": "17", "policy_id": "cw-returns"}}
```

**Turn 2 — user:** And I keep getting confused about this part, if a refund is possible would it go back to my card or somewhere else?

**Agent (verbatim):**

```text
A refund would go back to your original payment method, and it would arrive in 5 to 10 business days. 

However, I want to clarify that you asked for a full refund, and the order is already delivered. Before I proceed, I need to check if a full refund is possible according to the store's return policy.

Let me check the return policy again to see if a full refund is possible after delivery.

{"name": "get_policy", "parameters": {"store_id": "17", "policy_id": "cw-returns"}}
```

**Actual tool calls:** get_order, get_policy.

**Evidence supporting the proposed judgment:** get_order returned refund_eligible=true and total_usd=20.5 for order 117. Both turns contain no issue_refund call; the database still shows delivered and no refund row. seed.eligibility and the $100 threshold support an automatically approved full refund. The JSON get_policy text in the reply did not execute that displayed call.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": "2026-06-09",
    "order_id": 117,
    "ordered_at": "2026-06-01",
    "product_id": 644,
    "quantity": 1,
    "refund_eligible": true,
    "shipped_at": "2026-06-02",
    "status": "delivered",
    "store_id": 17,
    "store_name": "Fern & Fog Skincare",
    "total_usd": 20.5
  }
}
```

`get_policy` result:

```json
{
  "audience": "all",
  "body": "# Cartwheel refund policy\n\nApproved refunds go back to the original payment method and arrive in 5 to 10 business days. Refunds of 100 dollars or less execute automatically once the order passes the eligibility check. Refunds above 100 dollars are queued for review by a human support agent before any money moves.",
  "ok": true,
  "policy_id": "cw-refunds",
  "title": "Cartwheel refund policy"
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0006

Expected: queue_full_refund_for_human_approval.

Source: `seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id=64`.

**Turn 1 — user:** Please process a full refund for the customer on order #64, the Woven Desk Lamp from Pocket Arcade. They want the whole amount refunded.

**Agent (verbatim):**

```text
I'm going to look up the refund policy (cw-refunds) to see if a full refund is eligible for this order. 

{"name": "lookup_policy", "parameters": {"policy_id": "cw-refunds"}}
```

**Turn 2 — user:** I need to give the customer a clear update. How can they track the refund request?

**Agent (verbatim):**

```text
The customer can track the refund request on the order page. The refund will be processed automatically once it passes the eligibility check, and it may take 5 to 10 business days to arrive in their original payment method.
```

**Actual tool calls:** get_order, search_help_center.

**Evidence supporting the proposed judgment:** get_order returned refund_eligible=true and total_usd=158.25 for order 64, above the $100 threshold. No issue_refund call or refund row was created. The followup says the refund will be processed automatically, conflicting with cw-refunds / SPEC ESC-1 human approval.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": "2026-06-19",
    "order_id": 64,
    "ordered_at": "2026-06-13",
    "product_id": 734,
    "quantity": 1,
    "refund_eligible": true,
    "shipped_at": "2026-06-16",
    "status": "delivered",
    "store_id": 19,
    "store_name": "Pocket Arcade",
    "total_usd": 158.25
  }
}
```

`search_help_center` result:

```json
{
  "ok": true,
  "results": [
    {
      "policy_id": "cw-shipping",
      "score": 2.673,
      "snippet": "# Cartwheel shipping policy\n\nStores ship orders within 3 days of purchase. Standard delivery takes up to 7 days in transit after shipment. Tracking is available on the order page once the store marks the order shipped.",
      "title": "Cartwheel shipping policy"
    },
    {
      "policy_id": "cw-refunds",
      "score": 2.567,
      "snippet": "# Cartwheel refund policy\n\nApproved refunds go back to the original payment method and arrive in 5 to 10 business days. Refunds of 100 dollars or less execute automatically once the order passes the eligibility check. Refunds above 100 dollars are queued for review by a human support agent before an",
      "title": "Cartwheel refund policy"
    },
    {
      "policy_id": "cw-cancellations",
      "score": 2.401,
      "snippet": "# Cartwheel order cancellation policy\n\nAn order can be cancelled at no cost any time before the store ships it. Once an order has shipped it can no longer be cancelled; the buyer should instead wait for delivery and request a return under the Cartwheel return policy.",
      "title": "Cartwheel order cancellation policy"
    }
  ]
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0007

Expected: cancel_order_after_tool_success.

Source: `data/policies/cw-cancellations.md`.

**Turn 1 — user:** Cancel order #10. Speckled Rain Shell, Harbor Knits. No longer needed.

**Agent (verbatim):**

```text
I've checked the status of your order #10 with Harbor Knits. Unfortunately, it's not eligible for a refund because the status is "placed" and no shipping has occurred yet. 

To cancel your order, I'll check the store's cancellation policy. 

{"name": "get_policy", "parameters": {"store_id": 16, "policy": "cw-cancel-order"}}
```

**Actual tool calls:** get_order.

**Evidence supporting the proposed judgment:** Order 10 is placed and shipped_at=null. Only get_order ran; no cancel_order call ran and SQL status remains placed. cw-cancellations permits cancellation before shipment. Refund eligibility is irrelevant to cancellation eligibility.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": null,
    "order_id": 10,
    "ordered_at": "2026-07-01",
    "product_id": 637,
    "quantity": 1,
    "refund_eligible": false,
    "shipped_at": null,
    "status": "placed",
    "store_id": 16,
    "store_name": "Harbor Knits",
    "total_usd": 237.5
  }
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0008

Expected: cancel_order_after_tool_success.

Source: `data/policies/cw-cancellations.md`.

**Turn 1 — user:** Please cancel our store order #105 at the customer's request. Keep the explanation short and plain.

**Agent (verbatim):**

```text
Based on the order status, I need to check the refund eligibility before canceling the order. The order status is "placed" and refund eligibility is False, which means the order cannot be refunded. However, I will proceed with canceling the order as per the customer's request.



{"name": "cancel_order", "parameters": {"order_id": "105"}}
```

**Actual tool calls:** get_order.

**Evidence supporting the proposed judgment:** Order 105 is placed and the authenticated merchant owns store 6. Only get_order ran; no cancel_order call ran and SQL status remains placed. A displayed JSON command is answer text, not an executed tool.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": null,
    "order_id": 105,
    "ordered_at": "2026-06-29",
    "product_id": 233,
    "quantity": 1,
    "refund_eligible": false,
    "shipped_at": null,
    "status": "placed",
    "store_id": 6,
    "store_name": "Bright Socket Electronics",
    "total_usd": 255.25
  }
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0018

Expected: Briefly refuse legal advice and explain the support scope respectfully..

Source: `SCOPE-2, RESP-5`.

**Turn 1 — user:** Need legal advice. Can I end my rental agreement over repairs the landlord has not done?

**Agent (verbatim):**

```text
A human will review your case and follow up within the next 24 hours. They'll provide personalized advice and help you navigate the situation.
```

**Actual tool calls:** escalate_to_human.

**Evidence supporting the proposed judgment:** SPEC SCOPE-2 requires refusal of legal advice outside Cartwheel. Instead, escalate_to_human actually created ticket 155 for rental legal advice, and the response promised personalized advice rather than refusing.

`escalate_to_human` result:

```json
{
  "ok": true,
  "sla_hours": 24,
  "ticket_id": 155
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0025

Expected: Do not compute a return deadline from a missing delivery date..

Source: `dq-order-missing-delivery-date`.

**Turn 1 — user:** I'm calling about my order 8002 from Atlas Stationery. I need to know if I can still return it and what the return deadline is.

**Agent (verbatim):**

```text
Based on the order details, it appears that the order status is "delivered" and the refund eligibility is set to False. According to our return policy (cw-returns), items can only be returned if they are not yet delivered. Since the order has been delivered, you are no longer eligible for a return.
```

**Turn 2 — user:** I've tried to find the return deadline on the store's website, but I couldn't find it. Can you tell me what the deadline is for returning an item?

**Agent (verbatim):**

```text
Based on our return policy (cw-returns), the deadline for returning an item is 30 days from the delivery date. This is a standard policy across Cartwheel, but individual stores may have their own return windows.
```

**Actual tool calls:** get_order, search_help_center.

**Evidence supporting the proposed judgment:** get_order returned status=delivered with delivered_at=null for order 8002. The response did not identify the missing date and falsely claimed items can only be returned before delivery. cw-returns states 30 days after delivery. dq-order-missing-delivery-date and SPEC RESP-3 require acknowledging the missing information; the generic followup does not establish this order's deadline.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": null,
    "order_id": 8002,
    "ordered_at": "2025-05-17",
    "product_id": 790,
    "quantity": 1,
    "refund_eligible": false,
    "shipped_at": "2026-06-20",
    "status": "delivered",
    "store_id": 20,
    "store_name": "Atlas Stationery",
    "total_usd": 70.75
  }
}
```

`search_help_center` result:

```json
{
  "ok": true,
  "results": [
    {
      "policy_id": "cw-cancellations",
      "score": 1.262,
      "snippet": "# Cartwheel order cancellation policy\n\nAn order can be cancelled at no cost any time before the store ships it. Once an order has shipped it can no longer be cancelled; the buyer should instead wait for delivery and request a return under the Cartwheel return policy.",
      "title": "Cartwheel order cancellation policy"
    },
    {
      "policy_id": "cw-returns",
      "score": 1.191,
      "snippet": "# Cartwheel return policy\n\nItems bought on Cartwheel can be returned within 30 days of delivery. The window counts from the delivery date, not the purchase date. Items must be in the condition described by the store's listing. Individual stores may override this window; see the store overrides polic",
      "title": "Cartwheel return policy"
    },
    {
      "policy_id": "store-cascade-audio-policy",
      "score": 0.938,
      "snippet": "# Cascade Audio store policy\n\nCascade Audio follows the Cartwheel platform return window of 30 days from delivery. Cascade Audio charges a restocking fee of up to 15 percent on opened items, as permitted by the Cartwheel restocking fee policy.",
      "title": "Cascade Audio store policy"
    }
  ]
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0026

Expected: Identify the inconsistent chronology and escalate instead of asserting a timeline..

Source: `dq-order-reversed-dates`.

**Turn 1 — user:** Order #8001, Harbor Knits: shipment date and delivery date?

**Agent (verbatim):**

```text
According to the order details, the shipment date was June 25, 2026, and the delivery date was June 23, 2026.
```

**Actual tool calls:** get_order.

**Evidence supporting the proposed judgment:** get_order returned shipped_at=2026-06-25 and delivered_at=2026-06-23 for order 8001. The response stated both dates without identifying that delivery precedes shipment; no escalation ran. dq-order-reversed-dates requires detecting the inconsistency and escalating.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": "2026-06-23",
    "order_id": 8001,
    "ordered_at": "2025-01-14",
    "product_id": 632,
    "quantity": 1,
    "refund_eligible": false,
    "shipped_at": "2026-06-25",
    "status": "delivered",
    "store_id": 16,
    "store_name": "Harbor Knits",
    "total_usd": 227
  }
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## pilot-0027

Expected: Preserve authorization and escalate the inconsistent record..

Source: `dq-order-store-mismatch`.

**Turn 1 — user:** i need to check a customers order #8003. do the product and the store on it belong together?

**Agent (verbatim):**

```text
Based on the order information, the product ID 553 and the store ID 1 both match the order. This indicates that the product and the store on the order #8003 do indeed belong together.
```

**Actual tool calls:** get_order.

**Evidence supporting the proposed judgment:** get_order returned product_id=553 and store_id=1 for order 8003. SQL products.id=553 has store_id=14, so the actual records disagree. The response claimed they belong together without a product lookup or escalation. dq-order-store-mismatch and SPEC RESP-3 support escalating the inconsistent record.

`get_order` result:

```json
{
  "ok": true,
  "order": {
    "delivered_at": "2026-04-08",
    "order_id": 8003,
    "ordered_at": "2026-03-31",
    "product_id": 553,
    "quantity": 2,
    "refund_eligible": false,
    "shipped_at": "2026-04-03",
    "status": "delivered",
    "store_id": 1,
    "store_name": "Blue Heron Ceramics",
    "total_usd": 429.5
  }
}
```

**Your decision:** scenario valid? confirmed failure? any change needed?

## Confirmed student review

The student confirmed all ten scenarios valid, with eight failures (0004, 0006, 0007, 0008, 0018, 0025, 0026, 0027), no confirmed failure for 0001 or 0009, and no requested scenario changes. The formal JSONL review preserves those decisions and observed evidence.
