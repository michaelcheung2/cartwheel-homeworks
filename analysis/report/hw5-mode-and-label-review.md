# HW5 Part A: mode and additional-label review

Status: student confirmed the boundary and all five proposed Fail labels.
Accepted decisions are saved in analysis/state/hw5_labels/unsupported_policy_claim.jsonl.
The original proposal wording and recorded evidence below are retained for provenance.
No splits or judge calls have been made.

## Proposed judge

Mode: `unsupported_policy_claim` (existing HW4 definition v1).

Question: Does the selected final reply state a platform/store policy rule or service promise that contradicts applicable policy or lacks support in the retrieved policy and actual tool results?

- **Fail:** at least one such unsupported or contradicted rule/promise.
- **Pass:** none of those claims in the selected reply. Other failures may still exist.
- **Boundary:** a supported rule with a missing citation belongs to the citation mode; an invented order date belongs to factual grounding. A real ticket SLA supports a response-time statement, not guaranteed completion, priority, an email channel, or a tracking portal.
- **Evidence:** selected user request/reply, relevant earlier turns, actual tool calls/results, and retrieved policy passages.
- **Why a model judge:** code can check a document identifier or the presence of a tool result, but deciding whether a paraphrased claim is supported requires comparing its meaning with the evidence.

## Model choice

Main judge: local `ollama_chat/llama3.1:8b`, explicitly chosen by the student. This departs from HW5’s required `gpt-4o-mini`; report the departure. Optional Qwen comparison is available using installed `qwen3:8b`, but no comparison or judge call has run.

## Label readiness

HW4 has 75 Pass and 25 Fail across 100 labeled turns in 95 sessions. Select one eligible record per conversation and exclude duplicate runs/close variants before splitting. Counts below are candidates, not a verified 30/30 independent dataset.

Four candidates already have human-accepted positive search hypotheses from HW4. Adopting those findings as final HW5 labels still needs an explicit decision. The fifth is a new AI proposal. All proposed labels are **Fail (HW5 value 0)**. Original HW4 labels will remain unchanged.

## Candidate 1: support-0086

Trace: `88bd075cb70e95dc14ec6832d0b70e43`

[Open recorded trace](http://localhost:3000/project/cartwheel-dev/traces/88bd075cb70e95dc14ec6832d0b70e43)

**Proposed label: Fail — awaiting HW5 confirmation.**

Prior provenance: human accepted a positive HW4 search hypothesis; no final all-mode label for this trace.

Quoted claim: However, the order is no longer refund eligible (refund_eligible: False), which means it cannot be cancelled.

Reason: get_order returns placed, shipped_at=null, delivered_at=null for order 5473, with refund_eligible=false. TOOL-8 and cw-cancellations allow cancellation before shipment; refund eligibility is a distinct condition. This claim invents a cancellation prerequisite rather than merely reporting the flag. Rechecked complete selected reply and full model history under final definition; this decision applies to the specific quoted evidence. Correct SLA from a recorded current/prior ticket is exempt; offers of help are not guaranteed outcomes.

### Selected turn: `88bd075cb70e95dc14ec6832d0b70e43`

**User**

Please, please cancel our store order 5473 from Petal & Stem immediately as the item is no longer needed.

**Tool — get_order**

```json
{
  "input": {
    "order_id": "5473"
  },
  "output": {
    "ok": true,
    "order": {
      "order_id": 5473,
      "store_id": 3,
      "product_id": 92,
      "quantity": 1,
      "total_usd": 41,
      "status": "placed",
      "ordered_at": "2026-06-30",
      "shipped_at": null,
      "delivered_at": null,
      "refund_eligible": false,
      "store_name": "Petal & Stem"
    }
  },
  "error": null
}
```

**Assistant**

I'm going to check the order status and see if it can be cancelled.

After checking, I found that the order is currently placed and not yet shipped. However, the order is no longer refund eligible (refund_eligible: False), which means it cannot be cancelled.

I'd like to check if there's a way to proceed with the cancellation. Can I call escalate_to_human to check if a human can assist with cancelling the order?

## Candidate 2: support-0163

Trace: `a2eb40520bea917e94b350b2226a3d48`

[Open recorded trace](http://localhost:3000/project/cartwheel-dev/traces/a2eb40520bea917e94b350b2226a3d48)

**Proposed label: Fail — awaiting HW5 confirmation.**

Prior provenance: human accepted a positive HW4 search hypothesis; no final all-mode label for this trace.

Quoted claim: In the meantime, please do not attempt to make any changes to your account phone number through your account settings.

Reason: Retrieved cw-account-security says account and payment changes happen only through account settings. cw-escalations and cw-getting-help promise a human response, and the earlier session turn has a successful escalation. None introduces a ban on using settings while awaiting contact. This instruction contradicts the documented channel for changes. Rechecked complete selected reply and full model history under final definition; this decision applies to the specific quoted evidence. Correct SLA from a recorded current/prior ticket is exempt; offers of help are not guaranteed outcomes.

### Earlier context turn: `ad26d59674c6b2ff02820e960b47c041`

**User**

Plese chnge teh account phone number on my account.

**Tool — escalate_to_human**

```json
{
  "input": {
    "context": "User id: 163, Store id: none",
    "summary": "Account phone number change request"
  },
  "output": {
    "ok": true,
    "ticket_id": 162,
    "sla_hours": 24
  },
  "error": null
}
```

**Assistant**

I'm not able to make changes to your account phone number directly. However, a human support representative will follow up with you shortly to assist with this request. You can expect a response within the next 24 hours. If you have any other questions or concerns, feel free to ask.

### Selected turn: `a2eb40520bea917e94b350b2226a3d48`

**User**

Wht is teh next step for making that chnge?

**Tool — search_help_center**

```json
{
  "input": {
    "query": "changing account phone number on Cartwheel"
  },
  "output": {
    "ok": true,
    "results": [
      {
        "policy_id": "cw-account-security",
        "title": "Account and payment security",
        "snippet": "# Account and payment security\n\nCartwheel support assistants never change payment cards, passwords, or account details in chat, and never ask for full card numbers. Account and payment changes happen only through account settings. Requests for legal advice are outside support's scope and are decline",
        "score": 4.097
      },
      {
        "policy_id": "cw-escalations",
        "title": "When a case goes to a human",
        "snippet": "# When a case goes to a human\n\nSome cases always go to a human support agent: refunds above 100 dollars, account changes, disputes, and anything the assistant cannot resolve from policy and the order record. A human responds to an escalation within 24 hours.",
        "score": 1.828
      },
      {
        "policy_id": "cw-getting-help",
        "title": "Getting help on Cartwheel",
        "snippet": "# Getting help on Cartwheel\n\nThe Cartwheel support assistant answers questions about orders, returns, refunds, products, and platform policy, and it cites the policy page behind every policy answer. If the assistant cannot resolve a case it opens a ticket for a human agent, who responds within 24 ho",
        "score": 1.49
      }
    ]
  },
  "error": null
}
```

**Assistant**

Since the support assistant is unable to make changes to your account phone number directly, a human support representative will follow up with you shortly to assist with this request. In the meantime, please do not attempt to make any changes to your account phone number through your account settings. The human representative will guide you through the next steps in the process.

## Candidate 3: support-0177

Trace: `929f48ec1adaaaa49007bd22eb50737a`

[Open recorded trace](http://localhost:3000/project/cartwheel-dev/traces/929f48ec1adaaaa49007bd22eb50737a)

**Proposed label: Fail — awaiting HW5 confirmation.**

Prior provenance: human accepted a positive HW4 search hypothesis; no final all-mode label for this trace.

Quoted claim: According to Cartwheel's return policy (cw-returns), you have 30 days from the shipped date to initiate a return.

Reason: get_order returns shipped_at=2026-06-20 but delivered_at=null for order 8002. cw-returns explicitly counts from delivery, not shipment or purchase. The reply then calculates July 20 from shipment despite the missing delivery date. This has a policy contradiction independently of the neighboring missing-information mode. Rechecked complete selected reply and full model history under final definition; this decision applies to the specific quoted evidence. Correct SLA from a recorded current/prior ticket is exempt; offers of help are not guaranteed outcomes.

### Selected turn: `929f48ec1adaaaa49007bd22eb50737a`

**User**

How much time do I have to return order 8002?

**Tool — get_order**

```json
{
  "input": {
    "order_id": "8002"
  },
  "output": {
    "ok": true,
    "order": {
      "order_id": 8002,
      "store_id": 20,
      "product_id": 790,
      "quantity": 1,
      "total_usd": 70.75,
      "status": "delivered",
      "ordered_at": "2025-05-17",
      "shipped_at": "2026-06-20",
      "delivered_at": null,
      "refund_eligible": false,
      "store_name": "Atlas Stationery"
    }
  },
  "error": null
}
```

**Assistant**

According to Cartwheel's return policy (cw-returns), you have 30 days from the shipped date to initiate a return. In this case, the shipped date was June 20, 2026. Since the order was delivered, you have until July 20, 2026, to return the product.

## Candidate 4: support-0165

Trace: `1f8736c3a48d2c1bbe3fbce733936cda`

[Open recorded trace](http://localhost:3000/project/cartwheel-dev/traces/1f8736c3a48d2c1bbe3fbce733936cda)

**Proposed label: Fail — awaiting HW5 confirmation.**

Prior provenance: human accepted a positive HW4 search hypothesis; no final all-mode label for this trace.

Quoted claim: Please note that this is a high-priority request, and a human will be in touch with you within the next 24 hours to complete the update.

Reason: escalate_to_human succeeds with ticket_id=164 and sla_hours=24; its inputs do not assign priority, and its result does not promise completion. cw-escalations gives a human response within 24 hours. The reply adds both high priority and completion of the update within that time. This is a policy-derived service promise, not a claim the update already succeeded. Rechecked complete selected reply and full model history under final definition; this decision applies to the specific quoted evidence. Correct SLA from a recorded current/prior ticket is exempt; offers of help are not guaranteed outcomes.

### Selected turn: `1f8736c3a48d2c1bbe3fbce733936cda`

**User**

I need to change my notification contact email ASAP. Please update it.

**Tool — escalate_to_human**

```json
{
  "input": {
    "summary": "Customer needs to update their notification contact email",
    "context": "Account change request"
  },
  "output": {
    "ok": true,
    "ticket_id": 164,
    "sla_hours": 24
  },
  "error": null
}
```

**Assistant**

A human support specialist will follow up with you to update your notification contact email as soon as possible. Please note that this is a high-priority request, and a human will be in touch with you within the next 24 hours to complete the update.

## Candidate 5: support-0157

Trace: `86c39b64458b4c0bd8466a6aab997e92`

[Open recorded trace](http://localhost:3000/project/cartwheel-dev/traces/86c39b64458b4c0bd8466a6aab997e92)

**Proposed label: Fail — awaiting HW5 confirmation.**

New AI proposal: the reply guarantees an email with ticket 157 and asks the user to reply to that email. The escalation output supplies ticket 157 and SLA 24, without establishing an email notification or reply channel. Check earlier turns for support before deciding.

### Selected turn: `86c39b64458b4c0bd8466a6aab997e92`

**User**

I need a person to investigate a disputed charge on my order 850 from Paper Lantern Press. Please deal with this now.

**Tool — escalate_to_human**

```json
{
  "input": {
    "context": "disputed charge on order 850 from Paper Lantern Press",
    "summary": "Disputed charge on order 850 from Paper Lantern Press"
  },
  "output": {
    "ok": true,
    "ticket_id": 157,
    "sla_hours": 24
  },
  "error": null
}
```

**Assistant**

I've escalated the issue to a human support specialist. They will review the disputed charge on your order 850 from Paper Lantern Press and will contact you within 24 hours to discuss the next steps.

You will receive an email with the ticket number 157. Please reply to the email with any additional information or context regarding the dispute. A human support specialist will review the case and contact you as soon as possible.

Thank you for your patience and understanding. If you have any further questions or concerns, please don't hesitate to reach out.

## Decisions requested

Confirm or change the proposed mode boundary and each candidate’s Pass/Fail label. If a claim is supported by evidence in the conversation, mark it Pass for this mode or explain another unsupported claim. Do not use these notes as judge inputs.

## Next after review

Audit independent conversations and close variants, export confirmed HW5 labels using 1=Pass/0=Fail, prepare fixed evidence-only inputs, then split once into 20% training, 40% development, 40% test before choosing prompt examples.
