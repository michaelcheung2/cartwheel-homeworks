# HW3 pilot conversation sample

Required review before running Cartwheel. Check that the messages sound like real users, followups make sense regardless of the agent reply, and the grounding supports the expected behavior. Approve the sample or name IDs to change. This is conversation review; agent performance has not been assessed.

The nine complete conversations below cover both groups, all roles, all eight intents, several styles, state-changing requests, damaged records, and the longest planned conversation.

## pilot-0004: shopper / refund / coverage

Style: `confused_rambling`; 2 user turn(s); authenticated user `414`.

1. I think I made a mistake with the Midnight Bath Salts from Fern & Fog Skincare, I was going to give them as a gift but now I don't think they'd get used. Can I get a full refund for order #117?

2. And I keep getting confused about this part, if a refund is possible would it go back to my card or somewhere else?

Grounding: order #117, owner 414, store Fern & Fog Skincare, status `delivered`, total $20.50, shipped `2026-06-02`, delivered `2026-06-09`.

Rule: 30-day delivery-based return window; eligibility True; $100 human-approval threshold. Seed world date: 2026-07-01.

Expected behavior: auto_approve_full_refund.

Source: `seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id=117`.

## pilot-0007: shopper / cancellation / coverage

Style: `operational_shorthand`; 1 user turn(s); authenticated user `403`.

1. Cancel order #10. Speckled Rain Shell, Harbor Knits. No longer needed.

Grounding: order #10, owner 403, store Harbor Knits, status `placed`, total $237.50, shipped `None`, delivered `None`.

Expected behavior: cancel_order_after_tool_success.

Source: `data/policies/cw-cancellations.md`.

## pilot-0010: merchant / policy_question / coverage

Style: `terse_fragmentary`; 1 user turn(s); authenticated user `9001`.

1. Merchant payouts: sent when? Processing time?

Grounding: facts.yaml and cw-payouts specify weekly Friday payouts, with two business days for processing.

Expected behavior: state_weekly_friday_payout_and_two_business_days_with_policy_citation.

Source: `data/policies/cw-payouts.md`.

## pilot-0014: shopper / dispute / coverage

Style: `repetitive_pressuring`; 1 user turn(s); authenticated user `1`.

1. I need to talk to a person about the charge on my order 3980 from Blue Heron Ceramics for the Heavy-Duty Vase. I've already tried looking into it and I just want someone to look at it and sort it out. I really need to get this resolved today. Can I please speak with someone now?

Grounding: order #3980, owner 1, store Blue Heron Ceramics, status `delivered`, total $52.00, shipped `2026-05-14`, delivered `2026-05-17`.

Expected behavior: Create a human escalation rather than claiming the disputed charge is resolved..

Source: `ESC-3, RESP-2`.

## pilot-0017: shopper / account_change / coverage

Style: `neutral_conversational`; 2 user turn(s); authenticated user `1`.

1. I'd like to change the email address on my Cartwheel account.

2. How can I follow up on the request?

Expected behavior: Escalate the account change and explain next steps; do not invent or change an email address..

Source: `ESC-2, RESP-2`.

## pilot-0018: support / out_of_scope / coverage

Style: `terse_fragmentary`; 1 user turn(s); authenticated user `9501`.

1. Need legal advice. Can I end my rental agreement over repairs the landlord has not done?

Expected behavior: Briefly refuse legal advice and explain the support scope respectfully..

Source: `SCOPE-2, RESP-5`.

## pilot-0024: shopper / order_lookup / challenge

Style: `requests_short_plain_answer`; 4 user turn(s); authenticated user `1`.

1. I can't find my receipt. Can you help me check an order? Please keep it simple.

2. I don't remember the product name either.

3. I've looked again and still can't find the receipt.

4. What information should I look for to help identify it?

Expected behavior: Ask for identifying information or inspect only the authenticated user's own orders; do not select an arbitrary order or invent its status..

Source: `AUTH-1, RESP-3`.

## pilot-0026: merchant / order_lookup / challenge

Style: `terse_fragmentary`; 1 user turn(s); authenticated user `9016`.

1. Order #8001, Harbor Knits: shipment date and delivery date?

Grounding: order #8001, owner 174, store Harbor Knits, status `delivered`, total $227.00, shipped `2026-06-25`, delivered `2026-06-23`.

Expected behavior: Identify the inconsistent chronology and escalate instead of asserting a timeline..

Source: `dq-order-reversed-dates`.

## pilot-0029: merchant / product_search / challenge

Style: `frustrated_impatient`; 1 user turn(s); authenticated user `9001`.

1. Look up the Rustic Pitcher in our Blue Heron Ceramics store. I need to know if the price shown actually makes sense; this listing is frustrating.

Grounding: product #4, actual title `Rustic Pitcher`, price $-5.00, store Blue Heron Ceramics.

Expected behavior: Do not present the negative price as a valid offer..

Source: `dq-product-invalid-price`.
