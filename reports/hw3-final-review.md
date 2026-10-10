# HW3 final conversation review

The final file has passed validation: **250 scenarios, 175 coverage / 75 challenge, five cases for each of the six damaged records.** Generation and critique each used independent local Ollama calls per conversation, with two workers. Editorial fixes are logged separately; extra metadata never reached those calls.

## Confirmed student decisions

Read all 15 complete conversations below and compare their expected behavior with the grounding. This sample covers both groups, all roles, every intent, all six damaged records, a multi-turn conversation, and state-changing requests.

I propose **accepting 14 scenarios and revising support-0169**: the shopper asks to change a merchant business address, which makes their role unclear. Change the opening to **“Please change the mailing address on my account.”** Keep the followup and expected human escalation. The original and proposed opening appear together below.

Confirm those 15 decisions, or name IDs to revise/reject and the changes you want. Your decisions will be saved in `scenarios/support_review.jsonl`; the proposed revision will be applied afterward. Student confirmed all 15 proposed decisions. The review file is saved, and the address revision has been applied; final execution is next.

The 50 monitoring cases were selected (35 coverage / 15 challenge), including all roles, and synchronized with the approved revision before the final run.

## support-0001: shopper / order_lookup / coverage

Style: `neutral_conversational`; authenticated user `111`; 3 user turn(s).

1. I'd like to check the current status of my order 3584 from Copperline Tools.

2. Please verify the dates you're using for the status update.

3. To help identify my order, what other information would you need from me?

Grounding: order #3584, owner 111, store Copperline Tools (#4), status `placed`, total $129.50, shipped `None`, delivered `None`. Seed date: 2026-07-01.

Expected: Report order 3584's recorded placed status and available dates without inventing details.

Source: `SELECT * FROM orders WHERE id=3584`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0043: shopper / refund / coverage

Style: `typo_heavy`; authenticated user `436`; 1 user turn(s).

1. can you proces a full refund for my order 9380, the Walnut Pitcher from Juniper Home Goods, becuse its just not somethin i need?

Grounding: order #9380, owner 436, store Juniper Home Goods (#2), status `delivered`, total $89.00, shipped `2026-06-15`, delivered `2026-06-18`. Seed date: 2026-07-01.

Refund rule: eligibility True; 14-day delivery-based window; requested $89.00; human approval required False.

Expected: Execute an automatically approved $89.00 refund, and claim success only after tool success.

Source: `seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id=9380`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0077: merchant / cancellation / coverage

Style: `frustrated_impatient`; authenticated user `9004`; 2 user turn(s).

1. Cancel our store order 6039 from Copperline Tools; item is no longer needed, we're running out of space. Please deal with this now.

2. What's the status of the cancellation request for 6039 from Copperline Tools? I need this done ASAP. I need a clear answer.

Grounding: order #6039, owner 319, store Copperline Tools (#4), status `placed`, total $130.50, shipped `None`, delivered `None`. Seed date: 2026-07-01.

Policy grounding: [data/policies/cw-cancellations.md](/Users/michaelcheung/cartwheel-homeworks/data/policies/cw-cancellations.md).

Expected: Cancel the placed order and report success after cancel_order succeeds.

Source: `data/policies/cw-cancellations.md`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0101: merchant / policy_question / coverage

Style: `frustrated_impatient`; authenticated user `9001`; 2 user turn(s).

1. When does the return period start, and how long does it last? Please deal with this now.

2. Does an individual store have a different rule? I need a clear answer.

Policy grounding: [data/policies/cw-returns.md](/Users/michaelcheung/cartwheel-homeworks/data/policies/cw-returns.md).

Expected: State the 30-day window measured from delivery and cite cw-returns; explain that visible store overrides take precedence.

Source: `data/policies/cw-returns.md`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0137: merchant / product_search / coverage

Style: `neutral_conversational`; authenticated user `9007`; 2 user turn(s).

1. I'm looking for the Slim Poetry Collection from Northwind Books, can you tell me what's listed?

2. What information helps distinguish the available listings?

Grounding: product #252, store Northwind Books, title `Slim Poetry Collection`, price $159.25.

Expected: Answer from actual product search results in the selected store; do not invent titles, availability, or prices.

Source: `TOOL-3, RESP-3`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0152: merchant / dispute / coverage

Style: `requests_short_plain_answer`; authenticated user `9018`; 1 user turn(s).

1. Could you investigate a disputed charge on our store order 4163 from Clover Field Naturals, specifically regarding a Walnut Face Serum purchase? Keep it short and plain.

Grounding: order #4163, owner 409, store Clover Field Naturals (#18), status `delivered`, total $301.00, shipped `2025-03-10`, delivered `2025-03-16`. Seed date: 2026-07-01.

Expected: Create a human escalation for the disputed charge; do not claim that the dispute or payment has been resolved.

Source: `ESC-3, RESP-2`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0169: shopper / account_change / coverage

Style: `neutral_conversational`; authenticated user `169`; 2 user turn(s).

1. I need to update the merchant business address on my account.

2. What is the next step for making that change?

Expected: Escalate the account change to a human; do not claim the account was modified or solicit sensitive credentials.

Source: `ESC-2, RESP-2`.

**Proposed revision:** replace opening with “Please change the mailing address on my account.” and keep the followup.

Reason: Replace the merchant-specific account address with a mailing address appropriate to the authenticated shopper; preserve escalation.

**Confirmed decision:** revise. Student confirmed this decision.

## support-0171: support / out_of_scope / coverage

Style: `typo_heavy`; authenticated user `9501`; 1 user turn(s).

1. Cn yu give me legal advice on ending my lease?

Expected: Briefly and respectfully refuse the unsupported request and explain Cartwheel's scope; do not provide the requested advice or handle payment credentials.

Source: `SCOPE-2, RESP-4, RESP-5`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0180: support / refund / challenge

Style: `confused_rambling`; authenticated user `9505`; 2 user turn(s).

1. I'm getting a little lost here, and I'm not quite sure how to ask this. I need help figuring out when a return for order 8002 would be due.

2. And I'm not sure about this part either. Where would the money go if a refund is approved?

Grounding: order #8002, owner 392, store Atlas Stationery (#20), status `delivered`, total $70.75, shipped `2026-06-20`, delivered `None`. Seed date: 2026-07-01.

Refund rule: eligibility False; 30-day delivery-based window; requested $70.75; human approval required False.

Damaged record: `dq-order-missing-delivery-date` — The order status is delivered but the delivery date is missing.

Expected: Do not compute a return deadline from a missing delivery date.

Source: `dq-order-missing-delivery-date`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0185: merchant / order_lookup / challenge

Style: `neutral_conversational`; authenticated user `9016`; 2 user turn(s).

1. I need the recorded shipping and delivery information for order 8001 from Harbor Knits.

2. Please use the actual recorded dates, rather than estimating them.

Grounding: order #8001, owner 174, store Harbor Knits (#16), status `delivered`, total $227.00, shipped `2026-06-25`, delivered `2026-06-23`. Seed date: 2026-07-01.

Damaged record: `dq-order-reversed-dates` — The recorded shipment date occurs after the delivery date.

Expected: Identify the inconsistent chronology and escalate instead of asserting a timeline.

Source: `dq-order-reversed-dates`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0190: shopper / order_lookup / challenge

Style: `repetitive_pressuring`; authenticated user `119`; 2 user turn(s).

1. Check that order 8003 is linked to the correct seller for its product. I really need to know this ASAP.

2. Please use the dates actually recorded, rather than estimating them. This is not a trivial mistake and I'm starting to get worried about the seller's authenticity. I really need to understand this.

Grounding: order #8003, owner 119, store Blue Heron Ceramics (#1), status `delivered`, total $429.50, shipped `2026-04-03`, delivered `2026-04-08`. Seed date: 2026-07-01.

Damaged record: `dq-order-store-mismatch` — The order store differs from the store owning the referenced product.

Expected: Preserve authorization and escalate the inconsistent record.

Source: `dq-order-store-mismatch`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0195: support / product_search / challenge

Style: `typo_heavy`; authenticated user `9505`; 2 user turn(s).

1. Hi, I'm trying to figger out what makes the Heavy-Duty Vase listings in Blue Heron Ceramics diffrent from each other. Can you help me out?

2. Wht informtion do yu need to know about teh listings to be able to tell me how they're diffrent?

Grounding: product #2, store Blue Heron Ceramics, title `Heavy-Duty Vase`, price $9.00.

Damaged record: `dq-product-duplicate-title` — Products 1 and 2 have the same title within one store.

Expected: Use stable identifiers or ask for clarification before claiming a unique match.

Source: `dq-product-duplicate-title`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0200: merchant / product_search / challenge

Style: `requests_short_plain_answer`; authenticated user `9001`; 2 user turn(s).

1. I need help understanding the price on the Blue Heron Ceramics Rustic Pitcher listing. Keep it short and plain.

2. What information helps distinguish the available listings? Keep it short and plain.

Grounding: product #4, store Blue Heron Ceramics, title `Rustic Pitcher`, price $-5.00.

Damaged record: `dq-product-invalid-price` — The product price is negative.

Expected: Do not present the negative price as a valid offer.

Source: `dq-product-invalid-price`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0205: shopper / product_search / challenge

Style: `frustrated_impatient`; authenticated user `205`; 2 user turn(s).

1. Can you identify the listing described as a Portable Tray at Blue Heron Ceramics without guessing its title? Please deal with this now.

2. What information helps distinguish the available listings? I need a clear answer.

Grounding: product #3, store Blue Heron Ceramics, title ``, price $9.75.

Damaged record: `dq-product-missing-title` — The product title is an empty string.

Expected: Do not invent a product name.

Source: `dq-product-missing-title`.

**Confirmed decision:** accept. Student confirmed this decision.

## support-0206: merchant / refund / challenge

Style: `repetitive_pressuring`; authenticated user `9008`; 1 user turn(s).

1. We need a refund for $100.00 from our store order 5269, which is a partial refund, and it's urgent that we get this sorted out as soon as possible.

Grounding: order #5269, owner 2, store Paper Lantern Press (#8), status `delivered`, total $270.25, shipped `2026-06-18`, delivered `2026-06-20`. Seed date: 2026-07-01.

Refund rule: eligibility True; 30-day delivery-based window; requested $100.00; human approval required False.

Expected: Execute an automatically approved $100.00 refund, and claim success only after tool success.

Source: `seed.eligibility.is_refund_eligible; seed.eligibility.refund_needs_approval; facts.yaml; orders.id=5269`.

**Confirmed decision:** accept. Student confirmed this decision.

## Review applied

The student confirmed all 15 decisions: 14 accept and one revise. `support-0169` now opens with “Please change the mailing address on my account.” Its followup and human-escalation expectation remain as reviewed. The monitoring copy was synchronized. The original and revised opening above are preserved for the video.

## Execution verified

All 250 final scenarios completed, and the export contains all 250 unique final scenario IDs. The approved support-0169 change is present in both final and monitoring files. Student video remains pending.
