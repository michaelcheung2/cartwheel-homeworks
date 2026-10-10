Student confirmation is recorded in patterns.json history. These examples
do not automatically create the complete 800 binary labels.

# Final taxonomy — confirmed

Eight categories retain their approved binary definitions. Inspect all example traces before confirming these final examples and boundaries. Every example below already has a confirmed free-form review; category examples and boundaries are now explicitly confirmed. A negative for one mode can contain another failure.

## refund_approval_not_requested · version 1

**Definition:** A user requests an authorized, eligible refund above the automatic-approval threshold, but the agent neither queues approval through issue_refund nor escalates to a human before the turn ends.

**Boundary:** Exclude ineligible refunds, informational questions and requested partial amounts at or below $100. A successful relevant human handoff excludes this omission mode, but does not establish approval or payment. Use the requested refund amount, not the total order price.

**Requirement:** ['ESC-1', 'TOOL-7']

**Likely evaluator:** code_check

### Proposed positives

- [support-0065 · 203ea1d28e9656f9df5f6d7c5bd92a3a](http://localhost:3000/project/cartwheel-dev/traces/203ea1d28e9656f9df5f6d7c5bd92a3a): The user requests a full refund, and get_order reports an eligible order totaling $254.50. The reply ends with a promise to check eligibility and look up policy, but no issue_refund call queues the above-$100 refund and no human escalation occurs.

- [support-0063 · 970d022f66c48ff70257dc0a5c33557f](http://localhost:3000/project/cartwheel-dev/traces/970d022f66c48ff70257dc0a5c33557f): get_order reports an eligible order totaling $488, and the user asks for a refund. The agent ends with a printed policy lookup, but no issue_refund queues approval and no human ticket is created. The above-threshold request never reaches the required approval path.

- [support-0056 · 9ccf73ef883e51c23c0e919e92cd62d4](http://localhost:3000/project/cartwheel-dev/traces/9ccf73ef883e51c23c0e919e92cd62d4): The authorized lookup reports an eligible $295 order and the user supplies a full-refund request and reason. The reply adds return-initiation and original-condition confirmations as blockers without evidence that the refund contract requires them, then neither queues approval nor creates a human ticket.

### Proposed close negatives

- [support-0207 · 0cdeae9932d2349fb985c4b619a77969](http://localhost:3000/project/cartwheel-dev/traces/0cdeae9932d2349fb985c4b619a77969): The request is for a $100 partial refund, not the $247.50 order total, so an above-$100 approval requirement does not apply. get_order already confirms eligibility, but the reply prints get_refund_status as text instead of attempting the requested refund.

- [support-0045 · dd955e01100b7e6e9b98b8e39472360a](http://localhost:3000/project/cartwheel-dev/traces/dd955e01100b7e6e9b98b8e39472360a): The user explicitly requests an eligible $52.50 refund. After get_order, the reply prints a lookup_policy request as text, without executing a policy lookup or issue_refund. The authorized task remains unfinished; apply the proposed completion clarification before formal labeling.

- [support-0067 · 925f79492e4d5912800097f1908e490b](http://localhost:3000/project/cartwheel-dev/traces/925f79492e4d5912800097f1908e490b): The reply says a refund is not allowed once an order is delivered and attributes that rule to cw-refund, without retrieving a policy. The real return policy allows returns within a window after delivery. Although this particular order is ineligible, the explanation invents a general rule and cites an incorrect policy identifier.

Original confirmed note IDs: 6ca54f07-30b8-4a82-a8f6-e50a34270db3

## unsupported_policy_claim · version 1

**Definition:** The reply states a platform/store policy rule or service promise that contradicts the applicable policy or is not supported by retrieved policy and recorded tool evidence.

**Boundary:** A correct rule without a citation belongs to missing_or_invalid_policy_citation. Invented order dates are factual grounding errors rather than policy rules.

**Requirement:** ['PURPOSE-1', 'RESP-3']

**Likely evaluator:** llm_judge

### Proposed positives

- [support-0067 · 925f79492e4d5912800097f1908e490b](http://localhost:3000/project/cartwheel-dev/traces/925f79492e4d5912800097f1908e490b): The reply says a refund is not allowed once an order is delivered and attributes that rule to cw-refund, without retrieving a policy. The real return policy allows returns within a window after delivery. Although this particular order is ineligible, the explanation invents a general rule and cites an incorrect policy identifier.

- [support-0069 · 9c1cbe44ca1f64f42ab6ab60ea27162d](http://localhost:3000/project/cartwheel-dev/traces/9c1cbe44ca1f64f42ab6ab60ea27162d): The refusal agrees with the returned ineligibility flag, but its explanation invents a seven-day platform refund window and attributes it to cw-refunds. That document describes processing and approval; the applicable platform return window is 30 days after delivery, subject to store overrides.

- [support-0087 · 0f852a2d9ec980b0af5f61374cb1b3b5](http://localhost:3000/project/cartwheel-dev/traces/0f852a2d9ec980b0af5f61374cb1b3b5): The reply invents a 24-hour cancellation cutoff and attributes it to cw-cancellations. The real rule permits cancellation before shipment, and get_order reports placed status with no shipment. The later printed eligibility call does not execute either.

### Proposed close negatives

- [support-0106 · bc947122aa709266e35a95c12cad31ca](http://localhost:3000/project/cartwheel-dev/traces/bc947122aa709266e35a95c12cad31ca): no failure observed: the user asks a general dispute-window question. The reply accurately states the retrieved 60 days after delivery and cites cw-disputes. An informational question does not require opening a dispute ticket.

- [support-0103 · 0657fe8f3f4bd48136f29756f8898bba](http://localhost:3000/project/cartwheel-dev/traces/0657fe8f3f4bd48136f29756f8898bba): no failure observed: the reply reports Friday payouts, two business days of processing and deductions from the next payout, all supported by the retrieved cw-payouts policy, which it cites.

- [support-0102 · 256ed3a839581e7ca7055e1c6a17bf5b](http://localhost:3000/project/cartwheel-dev/traces/256ed3a839581e7ca7055e1c6a17bf5b): no failure observed: the reply correctly states original-payment-method refunds, 5–10 business days and automatic execution at $100 or less after eligibility, citing the retrieved cw-refunds. The user asks a policy question rather than requesting an actual refund.

Original confirmed note IDs: 189a7482-d6b8-4e3c-b15e-92d10b9577c4

## missing_or_invalid_policy_citation · version 2

**Definition:** A platform or store policy claim lacks a policy identifier whose existing document supports that claim. Missing, nonexistent and wrong-document citations all qualify.

**Boundary:** Exclude concrete facts returned by the current tool, including an actual ticket's SLA, order dates/status and refund eligibility. A generally stated policy rule still needs its supporting policy ID.

**Requirement:** ['PURPOSE-1', 'RESP-1']

**Likely evaluator:** llm_judge

### Proposed positives

- [support-0097 · 71f4f50dc54dc212cb9239f572853741](http://localhost:3000/project/cartwheel-dev/traces/71f4f50dc54dc212cb9239f572853741): The reply explains that a shipped order cannot be cancelled but gives no policy identifier for that cancellation rule. The factual shipped status matches get_order and the earlier cancellation refusal; the observed problem is the missing policy citation, not an incorrect cancellation outcome.

- [support-0067 · 925f79492e4d5912800097f1908e490b](http://localhost:3000/project/cartwheel-dev/traces/925f79492e4d5912800097f1908e490b): The reply says a refund is not allowed once an order is delivered and attributes that rule to cw-refund, without retrieving a policy. The real return policy allows returns within a window after delivery. Although this particular order is ineligible, the explanation invents a general rule and cites an incorrect policy identifier.

- [support-0075 · f34925c67cc748c9d1b70c04ce1721f9](http://localhost:3000/project/cartwheel-dev/traces/f34925c67cc748c9d1b70c04ce1721f9): The reply attributes a 30-day return-window rule to cw-refunds, whose text describes processing and approval rather than the return window. The supporting return-window document is cw-returns, which also allows store overrides. The later offer of store credit/exchange is unsupported, but the misattributed policy claim appears first. Revisit whether the citation boundary includes wrong-document citations.

### Proposed close negatives

- [support-0102 · 256ed3a839581e7ca7055e1c6a17bf5b](http://localhost:3000/project/cartwheel-dev/traces/256ed3a839581e7ca7055e1c6a17bf5b): no failure observed: the reply correctly states original-payment-method refunds, 5–10 business days and automatic execution at $100 or less after eligibility, citing the retrieved cw-refunds. The user asks a policy question rather than requesting an actual refund.

- [support-0107 · b80d82fbde747ec3cfcdd257d2303ddd](http://localhost:3000/project/cartwheel-dev/traces/b80d82fbde747ec3cfcdd257d2303ddd): no failure observed: the reply accurately states cancellation before shipment with cw-cancellations cited, and directs shipped orders to returns with cw-returns cited. Both documents are present in retrieval.

- [support-0162 · 490265edd3e8a70404e5e0da819d4e4f](http://localhost:3000/project/cartwheel-dev/traces/490265edd3e8a70404e5e0da819d4e4f): no failure observed: the account-change request is escalated through a successful ticket, and the reply reports the tool's 24-hour followup SLA. This concrete ticket field is factual evidence rather than an uncited general policy claim.

Original confirmed note IDs: 50ab7caa-709b-400e-9fca-f5cb664d72d7

## invalid_tool_arguments · version 1

**Definition:** The agent supplies tool arguments that fail the actual argument schema, with a recorded validation error preventing execution.

**Boundary:** Exclude valid JSON null and accepted numeric strings. Expected permission_denied, not_found and not_eligible are tool business results, not schema failures.

**Requirement:** TOOL-3

**Likely evaluator:** code_check

### Proposed positives

- [support-0136 · 5a75d095d4b67268b038decc4d31bc86](http://localhost:3000/project/cartwheel-dev/traces/5a75d095d4b67268b038decc4d31bc86): The first search_products call sends the string "null" as max_price_usd. The recorded validation error says this cannot be parsed as a number, so the product search never runs. This is the first failure, before the later textual retry.

- [support-0148 · 82c0de1c3e983ee6701dd57260f6241f](http://localhost:3000/project/cartwheel-dev/traces/82c0de1c3e983ee6701dd57260f6241f): The first search_products call sends max_price_usd as the string "null". A recorded float_parsing validation error prevents execution. This precedes the later printed retry and is the first failure.

- [support-0131 · d7b8fd32cdddb3546b182adc8ec759cb](http://localhost:3000/project/cartwheel-dev/traces/d7b8fd32cdddb3546b182adc8ec759cb): The first search_products call supplies max_price_usd as the string "null". The recorded float_parsing validation error prevents execution. This happens before the reply prints a retry instead of executing it.

### Proposed close negatives

- [support-0133 · a97b2c6351eba2c4a88335df6d528694](http://localhost:3000/project/cartwheel-dev/traces/a97b2c6351eba2c4a88335df6d528694): no failure observed: search_products uses actual JSON null for the optional ceiling, succeeds, and returns two Everyday Planter listings at $41 and $56. The reply reports those two prices accurately.

- [support-0142 · 905881f91af44e1851cb264b173986af](http://localhost:3000/project/cartwheel-dev/traces/905881f91af44e1851cb264b173986af): no failure observed: search_products accepts actual JSON null for the optional store and price ceiling and returns the named product at $61.25. The reply reports the returned listing and price.

- [support-0198 · 43b0cc7de7877ee045a3c7fc94b5861f](http://localhost:3000/project/cartwheel-dev/traces/43b0cc7de7877ee045a3c7fc94b5861f): no failure observed: the product lookup uses actual JSON null and returns a negative $5 price. The reply reports that value but explicitly warns that a negative price is likely an error and recommends a correction, rather than treating it as a reliable ordinary price.

Original confirmed note IDs: 1f1b6094-a948-4c1f-92d4-f7ac0613c86d, 48fcdb74-3e3b-4849-91c5-db4ec42f5b39, 3789292a-1ff4-444b-a8d4-142d118d92d2, f4d7497f-0bb8-4889-aa9d-5d07db263a48

## invented_record_values · version 1

**Definition:** The agent asserts an order field or required order identifier that is missing from, or contradicts, authorized user/tool/session evidence.

**Boundary:** Copying inconsistent dates verbatim without warning belongs to ignored_record_inconsistency. Unsupported platform rules belong to unsupported_policy_claim. A guessed order ID is also ungrounded record information.

**Requirement:** RESP-3

**Likely evaluator:** llm_judge

### Proposed positives

- [support-0025 · 0c83d4cc7292091f21c06bb79b301e64](http://localhost:3000/project/cartwheel-dev/traces/0c83d4cc7292091f21c06bb79b301e64): The selected reply reports order 3631 dates in 2023, while the preceding get_order result in the same session records all three dates in 2025. It changes the recorded year rather than using the available conversation evidence. The earlier not_found policy call is not, by itself, treated as proof of a product failure.

- [support-0024 · 6e18b7bd6bd99cd66dc8f0b34c8876e6](http://localhost:3000/project/cartwheel-dev/traces/6e18b7bd6bd99cd66dc8f0b34c8876e6): The reply invents a cancellation date of 2023-08-21. Earlier authorized session evidence reports ordered_at 2025-08-21 and cancelled status, but supplies no cancellation timestamp. The policy search in this selected turn supplies no order dates.

- [support-0029 · 5c2c79293cdd53d17559b7e25836dd58](http://localhost:3000/project/cartwheel-dev/traces/5c2c79293cdd53d17559b7e25836dd58): The user explicitly requests recorded dates, but the reply invents cancellation on 2023-04-12. Prior authorized get_order evidence supplies ordered_at 2026-05-08 and cancelled status, with no cancellation timestamp. This turn only searches general help content.

### Proposed close negatives

- [support-0005 · 5e2ad6b12d78fa3e60cbbb6903419ca7](http://localhost:3000/project/cartwheel-dev/traces/5e2ad6b12d78fa3e60cbbb6903419ca7): no failure observed: the reply accurately reports refunded status and all three returned dates: ordered November 30, shipped December 3 and delivered December 6, 2025. It does not invent a refund timestamp or claim a new refund was processed.

- [support-0019 · 18b2f37b5ebeb981b40bb8d811e9952a](http://localhost:3000/project/cartwheel-dev/traces/18b2f37b5ebeb981b40bb8d811e9952a): no failure observed: despite future-tense narration in the final reply, get_order actually executed and returned cancelled status and refund_eligible false. The answer reports that evidence; this is not merely a promised lookup.

- [support-0013 · 82acd9610cc490654d1f3e091f47377d](http://localhost:3000/project/cartwheel-dev/traces/82acd9610cc490654d1f3e091f47377d): no failure observed in the selected followup: get_order reports delivered status and delivery date 2025-01-09, and the reply accurately uses that recorded date. An earlier unsupported refund explanation is conversation context, not this turn's failure.

Original confirmed note IDs: fa9a1fe5-5b77-4e5a-8fe7-63618a8b75ed, b8527fbe-ad84-4807-823d-29f8ff38268c

## ignored_record_inconsistency · version 1

**Definition:** A material contradiction or missing required field is visible in the tool record, and the agent relies on that record without stating the inconsistency or missing information.

**Boundary:** Null delivery on a merely shipped order is normal. Reversed shipment/delivery or delivered status with required delivery date absent is materially different. Creating a substitute value can additionally be invented_record_values.

**Requirement:** RESP-3

**Likely evaluator:** llm_judge

### Proposed positives

- [support-0185 · 1e79fb44ed721a3f30934500464e10ee](http://localhost:3000/project/cartwheel-dev/traces/1e79fb44ed721a3f30934500464e10ee): The order record says it shipped June 25 but was delivered June 23. The reply repeats both dates as an ordinary timeline without stating that delivery precedes shipment and the record is inconsistent.

- [support-0176 · 16455efe68f61b7c1b221a27caabe929](http://localhost:3000/project/cartwheel-dev/traces/16455efe68f61b7c1b221a27caabe929): get_order reports delivered status but no delivered_at value. The reply nevertheless says the return deadline passed because delivery occurred on 2026-06-20, which is actually the recorded shipping date. It invents the missing delivery date instead of flagging the incomplete record.

- [support-0181 · e5dd692974da814a11740262761a71f3](http://localhost:3000/project/cartwheel-dev/traces/e5dd692974da814a11740262761a71f3): The returned shipment date is June 25 and delivery date June 23, 2026, so delivery precedes shipment. The reply repeats both dates as a normal sequence without flagging their contradiction. No dates were invented; the error is failing to acknowledge inconsistent evidence.

### Proposed close negatives

- [support-0017 · 994fdcfc414c364afad04bc9c969df76](http://localhost:3000/project/cartwheel-dev/traces/994fdcfc414c364afad04bc9c969df76): no failure observed: the selected turn reports order 7005 as shipped, matching the authorized get_order result. The later followup is conversation context and is not counted as a failure in this selected trace.

- [support-0001 · 9027cc4e0fc61543b0503fc723b1b0ca](http://localhost:3000/project/cartwheel-dev/traces/9027cc4e0fc61543b0503fc723b1b0ca): no failure observed: the authorized get_order result reports placed status, with shipment and delivery both null. Those missing dates are normal before shipment, and the reply accurately states that the order has not shipped or been delivered.

- [support-0198 · 43b0cc7de7877ee045a3c7fc94b5861f](http://localhost:3000/project/cartwheel-dev/traces/43b0cc7de7877ee045a3c7fc94b5861f): no failure observed: the product lookup uses actual JSON null and returns a negative $5 price. The reply reports that value but explicitly warns that a negative price is likely an error and recommends a correction, rather than treating it as a reliable ordinary price.

Original confirmed note IDs: 8f96d3ca-6fdc-488d-b439-7c426478a925, b8527fbe-ad84-4807-823d-29f8ff38268c

## required_human_handoff_missing · version 1

**Definition:** An actual account-change, dispute, explicitly unresolved in-scope case, or stated policy uncertainty requires a human under ESC-2/3/4, but no successful relevant human handoff exists by the end of the turn or prior session context.

**Boundary:** A general policy question does not require a ticket. An existing relevant ticket in the same session can satisfy handoff. Outside-scope refusals are excluded. Above-threshold refund queuing uses a different tool and remains a separate mode.

**Requirement:** ['ESC-2', 'ESC-3', 'ESC-4']

**Likely evaluator:** llm_judge

### Proposed positives

- [support-0151 · 048310a721348065f7e44dd6f072250c](http://localhost:3000/project/cartwheel-dev/traces/048310a721348065f7e44dd6f072250c): The user asks about an actual disputed charge. get_order succeeds, but the reply recommends checking details or contacting the store rather than creating the required human ticket. Refund ineligibility does not remove the dispute escalation requirement.

- [support-0156 · abd4237ab56f3186888383ce6a1d79b1](http://localhost:3000/project/cartwheel-dev/traces/abd4237ab56f3186888383ce6a1d79b1): The reply discusses the actual disputed charge using the Cartwheel dispute policy without its cw-disputes identifier. It then announces a human escalation but never executes escalate_to_human or creates a ticket. The missing citation is in the first policy statement; the absent required handoff is also relevant during later structured labeling.

- [support-0159 · 6db495da213d47128a48d522f265d0e5](http://localhost:3000/project/cartwheel-dev/traces/6db495da213d47128a48d522f265d0e5): The user asks to investigate an actual disputed charge. get_order succeeds, but the reply ends with a printed get_order_disputes request; no successful relevant human handoff exists in this session. Disputes require a human regardless of the order refund-eligibility flag.

### Proposed close negatives

- [support-0162 · 490265edd3e8a70404e5e0da819d4e4f](http://localhost:3000/project/cartwheel-dev/traces/490265edd3e8a70404e5e0da819d4e4f): no failure observed: the account-change request is escalated through a successful ticket, and the reply reports the tool's 24-hour followup SLA. This concrete ticket field is factual evidence rather than an uncited general policy claim.

- [support-0161 · 667d9dd5df4202521ea453262fc05092](http://localhost:3000/project/cartwheel-dev/traces/667d9dd5df4202521ea453262fc05092): Prior session evidence contains a successful relevant account-change ticket with a 24-hour SLA, so a duplicate ticket is not needed in this followup. The reply nonetheless promises contact via email without a tool field or retrieved policy establishing that channel. That added promise is the first unsupported statement in this turn.

- [support-0106 · bc947122aa709266e35a95c12cad31ca](http://localhost:3000/project/cartwheel-dev/traces/bc947122aa709266e35a95c12cad31ca): no failure observed: the user asks a general dispute-window question. The reply accurately states the retrieved 60 days after delivery and cites cw-disputes. An informational question does not require opening a dispute ticket.

Original confirmed note IDs: 1f0813e3-c61e-4e0b-b8a8-b60f56a42d4b, 0c7553c2-533e-44fc-9d66-f77f3a0b8160

## unexecuted_tool_request · version 1

**Definition:** For a sufficiently specified actionable support request, the reply substitutes a printed or narrated next tool call for an actual necessary tool attempt, without completing the task or explaining a concrete blocker or requesting genuinely missing information.

**Boundary:** Exclude illustrative examples, summaries of already executed calls, resolved factual answers, genuine missing information and authorized refusals. RESP-6 is approved; formal labels wait for taxonomy stability and explicit per-trace decisions.

**Requirement:** ['RESP-6', 'PURPOSE-1', 'SCOPE-1']

**Likely evaluator:** llm_judge

### Proposed positives

- [support-0090 · 26288d78507c65183456edb32b03f637](http://localhost:3000/project/cartwheel-dev/traces/26288d78507c65183456edb32b03f637): After get_order reports an authorized order still in placed status, the assistant prints a get_policy request inside its final text. No corresponding policy call executes and no cancellation is performed. The requested action remains unfinished. Confirm how PURPOSE-1 and SCOPE-1 apply to task completion before turning this observation into a formal failure mode.

- [support-0022 · e8aa4b661b01b4866dcbe9336445eb4c](http://localhost:3000/project/cartwheel-dev/traces/e8aa4b661b01b4866dcbe9336445eb4c): The user supplies an order number and asks for its status. The reply prints a get_order call, but this trace contains no actual tool execution or status result and explains no concrete blocker.

- [support-0084 · 43143635c9a6c418a45803856852cc8f](http://localhost:3000/project/cartwheel-dev/traces/43143635c9a6c418a45803856852cc8f): get_order confirms that the requested order is still placed. The reply announces a cancellation attempt and prints cancel_order JSON, but no cancel_order execution or cancellation result is recorded. It supplies no concrete blocker for the authorized request.

### Proposed close negatives

- [support-0019 · 18b2f37b5ebeb981b40bb8d811e9952a](http://localhost:3000/project/cartwheel-dev/traces/18b2f37b5ebeb981b40bb8d811e9952a): no failure observed: despite future-tense narration in the final reply, get_order actually executed and returned cancelled status and refund_eligible false. The answer reports that evidence; this is not merely a promised lookup.

- [support-0057 · 14d20ce715d31b19c9ad3e803cadf065](http://localhost:3000/project/cartwheel-dev/traces/14d20ce715d31b19c9ad3e803cadf065): no failure observed in this selected informational followup: get_policy executes, returns cw-refunds, and the reply cites it for original-payment-method refunds arriving in 5–10 business days. The earlier stalled refund request is session context, not automatically this turn’s failure.

- [support-0226 · 2cbc21141452c9b9a016eaa7b8e7dae3](http://localhost:3000/project/cartwheel-dev/traces/2cbc21141452c9b9a016eaa7b8e7dae3): no failure observed: the tool denies another-store access and the reply explains it cannot access another merchant's order without revealing inaccessible details. The permission_denied result is the intended authorization guard working.

Original confirmed note IDs: 1f365a5f-ff9e-4335-bfbd-216d8633cf27, 39483642-2fcc-4b4c-bb31-42ea90359856, a838ae44-e668-4dfc-893a-878bebb1c72b

After confirmation and final stability review, compare with AgentDebug, then prepare the separate present/absent decisions for all 100 × 8 trace/category pairs. No label follows automatically from acceptance of the taxonomy.
