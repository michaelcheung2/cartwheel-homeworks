# Depth batch — 25 AI review drafts

These selected traces test approved candidates and their boundaries. Drafts remain AI suggestions until you inspect and confirm them; they do not assign final binary labels.

## support-0056 · merchant · 9ccf73ef883e51c23c0e919e92cd62d4

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/9ccf73ef883e51c23c0e919e92cd62d4)

**Proposed observation:** The authorized lookup reports an eligible $295 order and the user supplies a full-refund request and reason. The reply adds return-initiation and original-condition confirmations as blockers without evidence that the refund contract requires them, then neither queues approval nor creates a human ticket.

**Evidence:** Could you please confirm that you have initiated the return process through our platform

**Requirements:** ESC-1, TOOL-7, RESP-6

## support-0207 · support · 0cdeae9932d2349fb985c4b619a77969

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/0cdeae9932d2349fb985c4b619a77969)

**Proposed observation:** The request is for a $100 partial refund, not the $247.50 order total, so an above-$100 approval requirement does not apply. get_order already confirms eligibility, but the reply prints get_refund_status as text instead of attempting the requested refund.

**Evidence:** {"name": "get_refund_status"

**Requirements:** RESP-6, TOOL-7

## support-0069 · support · 9c1cbe44ca1f64f42ab6ab60ea27162d

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/9c1cbe44ca1f64f42ab6ab60ea27162d)

**Proposed observation:** The refusal agrees with the returned ineligibility flag, but its explanation invents a seven-day platform refund window and attributes it to cw-refunds. That document describes processing and approval; the applicable platform return window is 30 days after delivery, subject to store overrides.

**Evidence:** orders are only eligible for refunds within 7 days of delivery.

**Requirements:** PURPOSE-1, RESP-3

## support-0110 · merchant · add1636aad08b6b894ece4a01a31defe

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/add1636aad08b6b894ece4a01a31defe)

**Proposed observation:** The reply first repeats retrieved payout rules without citing cw-payouts. This is the first failure. It later promises payment by Monday after a Friday run even though the policy allows two business days, so the later deadline is also unsupported.

**Evidence:** merchant payouts run weekly on Fridays and take 2 business days to process after the run.

**Requirements:** RESP-1

## support-0087 · support · 0f852a2d9ec980b0af5f61374cb1b3b5

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/0f852a2d9ec980b0af5f61374cb1b3b5)

**Proposed observation:** The reply invents a 24-hour cancellation cutoff and attributes it to cw-cancellations. The real rule permits cancellation before shipment, and get_order reports placed status with no shipment. The later printed eligibility call does not execute either.

**Evidence:** orders can be cancelled within 24 hours of being placed.

**Requirements:** PURPOSE-1, RESP-1

## support-0116 · merchant · 9caf585ae582fca3bcca46102f8fd3c0

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/9caf585ae582fca3bcca46102f8fd3c0)

**Proposed observation:** The reply accurately summarizes retrieved refund destination, timing and approval threshold, but does not name cw-refunds or another supporting policy identifier.

**Evidence:** approved refunds go back to the original payment method and take 5 to 10 business days to arrive.

**Requirements:** RESP-1

## support-0102 · support · 256ed3a839581e7ca7055e1c6a17bf5b

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/256ed3a839581e7ca7055e1c6a17bf5b)

**Proposed observation:** no failure observed: the reply correctly states original-payment-method refunds, 5–10 business days and automatic execution at $100 or less after eligibility, citing the retrieved cw-refunds. The user asks a policy question rather than requesting an actual refund.

**Evidence:** According to our refund policy (cw-refunds)

**Requirements:** No failure requirement applies.

## support-0107 · merchant · b80d82fbde747ec3cfcdd257d2303ddd

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/b80d82fbde747ec3cfcdd257d2303ddd)

**Proposed observation:** no failure observed: the reply accurately states cancellation before shipment with cw-cancellations cited, and directs shipped orders to returns with cw-returns cited. Both documents are present in retrieval.

**Evidence:** an order can be cancelled at no cost any time before the store ships it.

**Requirements:** No failure requirement applies.

## support-0047 · merchant · 01994e8ae186fc97b029be687ae706f6

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/01994e8ae186fc97b029be687ae706f6)

**Proposed observation:** The successful ticket tool supplies a 24-hour SLA, so the first followup sentence is grounded and is not missing a policy citation. The next sentence claims the customer can track the refund by logging into their account and checking order status; neither recorded tool evidence nor retrieved policy establishes that tracking capability. The draft flags that later advice, while proposing rejection of the separate SLA search hypothesis.

**Evidence:** by logging in to their account and checking the order status.

**Requirements:** RESP-3

## support-0131 · merchant · d7b8fd32cdddb3546b182adc8ec759cb

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/d7b8fd32cdddb3546b182adc8ec759cb)

**Proposed observation:** The first search_products call supplies max_price_usd as the string "null". The recorded float_parsing validation error prevents execution. This happens before the reply prints a retry instead of executing it.

**Evidence:** "null"

**Requirements:** TOOL-3

## support-0133 · shopper · a97b2c6351eba2c4a88335df6d528694

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/a97b2c6351eba2c4a88335df6d528694)

**Proposed observation:** no failure observed: search_products uses actual JSON null for the optional ceiling, succeeds, and returns two Everyday Planter listings at $41 and $56. The reply reports those two prices accurately.

**Evidence:** $41.00 and $56.00.

**Requirements:** No failure requirement applies.

## support-0142 · shopper · 905881f91af44e1851cb264b173986af

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/905881f91af44e1851cb264b173986af)

**Proposed observation:** no failure observed: search_products accepts actual JSON null for the optional store and price ceiling and returns the named product at $61.25. The reply reports the returned listing and price.

**Evidence:** The current price is $61.25.

**Requirements:** No failure requirement applies.

## support-0001 · shopper · 9027cc4e0fc61543b0503fc723b1b0ca

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/9027cc4e0fc61543b0503fc723b1b0ca)

**Proposed observation:** no failure observed: the authorized get_order result reports placed status, with shipment and delivery both null. Those missing dates are normal before shipment, and the reply accurately states that the order has not shipped or been delivered.

**Evidence:** it has not been shipped or delivered yet.

**Requirements:** No failure requirement applies.

## support-0024 · support · 6e18b7bd6bd99cd66dc8f0b34c8876e6

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/6e18b7bd6bd99cd66dc8f0b34c8876e6)

**Proposed observation:** The reply invents a cancellation date of 2023-08-21. Earlier authorized session evidence reports ordered_at 2025-08-21 and cancelled status, but supplies no cancellation timestamp. The policy search in this selected turn supplies no order dates.

**Evidence:** the order was cancelled on 2023-08-21.

**Requirements:** RESP-3

## support-0029 · merchant · 5c2c79293cdd53d17559b7e25836dd58

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/5c2c79293cdd53d17559b7e25836dd58)

**Proposed observation:** The user explicitly requests recorded dates, but the reply invents cancellation on 2023-04-12. Prior authorized get_order evidence supplies ordered_at 2026-05-08 and cancelled status, with no cancellation timestamp. This turn only searches general help content.

**Evidence:** it was cancelled on 2023-04-12.

**Requirements:** RESP-3

## support-0005 · merchant · 5e2ad6b12d78fa3e60cbbb6903419ca7

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/5e2ad6b12d78fa3e60cbbb6903419ca7)

**Proposed observation:** no failure observed: the reply accurately reports refunded status and all three returned dates: ordered November 30, shipped December 3 and delivered December 6, 2025. It does not invent a refund timestamp or claim a new refund was processed.

**Evidence:** The order was placed on November 30, 2025, shipped on December 3, 2025, and delivered on December 6, 2025.

**Requirements:** No failure requirement applies.

## support-0179 · merchant · 9367bda3271226a8f5c5470f7cbfd0d6

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/9367bda3271226a8f5c5470f7cbfd0d6)

**Proposed observation:** get_order reports delivered status but no delivery date. The reply immediately concludes the return period has ended instead of stating that the required delivery date is missing. It then invents a standard 90-day period and uses shipment as the clock, but the first failure is deciding eligibility without acknowledging the missing date.

**Evidence:** order 8002 is no longer within the return period.

**Requirements:** RESP-3

## support-0181 · shopper · e5dd692974da814a11740262761a71f3

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/e5dd692974da814a11740262761a71f3)

**Proposed observation:** The returned shipment date is June 25 and delivery date June 23, 2026, so delivery precedes shipment. The reply repeats both dates as a normal sequence without flagging their contradiction. No dates were invented; the error is failing to acknowledge inconsistent evidence.

**Evidence:** the shipment date was June 25, 2026, and the delivery date was June 23, 2026.

**Requirements:** RESP-3

## support-0198 · support · 43b0cc7de7877ee045a3c7fc94b5861f

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/43b0cc7de7877ee045a3c7fc94b5861f)

**Proposed observation:** no failure observed: the product lookup uses actual JSON null and returns a negative $5 price. The reply reports that value but explicitly warns that a negative price is likely an error and recommends a correction, rather than treating it as a reliable ordinary price.

**Evidence:** a negative price is likely an error

**Requirements:** No failure requirement applies.

## support-0159 · support · 6db495da213d47128a48d522f265d0e5

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/6db495da213d47128a48d522f265d0e5)

**Proposed observation:** The user asks to investigate an actual disputed charge. get_order succeeds, but the reply ends with a printed get_order_disputes request; no successful relevant human handoff exists in this session. Disputes require a human regardless of the order refund-eligibility flag.

**Evidence:** {"name": "get_order_disputes"

**Requirements:** ESC-3

## support-0161 · merchant · 667d9dd5df4202521ea453262fc05092

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/667d9dd5df4202521ea453262fc05092)

**Proposed observation:** Prior session evidence contains a successful relevant account-change ticket with a 24-hour SLA, so a duplicate ticket is not needed in this followup. The reply nonetheless promises contact via email without a tool field or retrieved policy establishing that channel. That added promise is the first unsupported statement in this turn.

**Evidence:** They will contact you via email with next steps.

**Requirements:** RESP-3

## support-0022 · shopper · e8aa4b661b01b4866dcbe9336445eb4c

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/e8aa4b661b01b4866dcbe9336445eb4c)

**Proposed observation:** The user supplies an order number and asks for its status. The reply prints a get_order call, but this trace contains no actual tool execution or status result and explains no concrete blocker.

**Evidence:** {"name": "get_order", "parameters": {"order_id": 8915}}

**Requirements:** RESP-6

## support-0084 · support · 43143635c9a6c418a45803856852cc8f

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/43143635c9a6c418a45803856852cc8f)

**Proposed observation:** get_order confirms that the requested order is still placed. The reply announces a cancellation attempt and prints cancel_order JSON, but no cancel_order execution or cancellation result is recorded. It supplies no concrete blocker for the authorized request.

**Evidence:** {"name": "cancel_order", "parameters": {"order_id":"4453"}}

**Requirements:** RESP-6, TOOL-8

## support-0019 · shopper · 18b2f37b5ebeb981b40bb8d811e9952a

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/18b2f37b5ebeb981b40bb8d811e9952a)

**Proposed observation:** no failure observed: despite future-tense narration in the final reply, get_order actually executed and returned cancelled status and refund_eligible false. The answer reports that evidence; this is not merely a promised lookup.

**Evidence:** the status of your order 8367 from Petal & Stem is currently "cancelled".

**Requirements:** No failure requirement applies.

## support-0057 · support · 14d20ce715d31b19c9ad3e803cadf065

[Inspect trace](http://localhost:3000/project/cartwheel-dev/traces/14d20ce715d31b19c9ad3e803cadf065)

**Proposed observation:** no failure observed in this selected informational followup: get_policy executes, returns cw-refunds, and the reply cites it for original-payment-method refunds arriving in 5–10 business days. The earlier stalled refund request is session context, not automatically this turn’s failure.

**Evidence:** According to our refund policy (cw-refunds)

**Requirements:** No failure requirement applies.

## Separate proposed search decision

Suggestion `hw4-search-v1-ded7efd7abe4307c` remains pending.

**Proposed decision: reject.** Reject the quoted 24-hour followup sentence as evidence of a citation failure: actual successful escalate_to_human returns ticket_id 151 and sla_hours 24, so it reports a concrete tool fact excluded by citation v2. Later refund-tracking advice is a separate issue and does not make this quoted SLA evidence valid.

Confirming the 25 review drafts does not automatically accept every exploratory search or assign final labels. This specific rejection also requires your decision.
