# Approved task-completion clarification — RESP-6

## Motivating accepted observations

- `support-0090`, trace `26288d78507c65183456edb32b03f637`:
  a cancellation request ends with printed `get_policy` JSON and no cancellation.
- `support-0081`, trace `30df41a4cb3eec2f2e6bc05afe859561`:
  the reply prints malformed `get_order` JSON; no tool executes.
- `support-0068`, trace `1773373a0030fb84dddd757de1fb4f37`:
  the reply prints `lookup_policy`, an unavailable tool, and leaves refund
  next steps unanswered.

The originating human-confirmed annotation IDs are preserved in the
`unexecuted_tool_request` candidate under `analysis/state/patterns.json`.

## Why a clarification is proposed

PURPOSE-1 says the agent acts through tools, and SCOPE-1 lists supported
actions. They do not state a precise stopping rule distinguishing an
acceptable explanation from a response that announces work and never
performs it. A deterministic evaluator should not invent this requirement.

## Approved addition to SPEC section 6

> **RESP-6.** For an authorized, actionable request within support scope
> that has the required information, attempt the requested operation
> through its tool, submit it to the required approval path, or hand it off
> to a human as policy requires, and report the observed result. If the
> request cannot proceed, explain the concrete blocker or ask for genuinely
> missing required information. Do not end with a promised, narrated or
> printed tool call as a substitute for actual execution. Existing
> authorization checks, eligibility rules, approval thresholds and pause
> protections still govern every action.

This applies to a tool attempt and honest result, rather than guaranteeing
success. Proper refusals, paused writes, permission denials and genuine
clarifications remain valid outcomes. General informational questions do
not require a write. Prior relevant session evidence and existing handoffs
remain available to the reviewer.

## Status

The student explicitly confirmed the displayed clarification package. RESP-6
is now added to SPEC.md, with the motivating annotation IDs preserved in
patterns.json. This revision changes intended behavior for evaluation; the
running application and historical traces are unchanged. Final structured
labels remain pending the final taxonomy and human judgments.
