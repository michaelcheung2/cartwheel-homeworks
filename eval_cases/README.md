# Evaluation cases

`cases.jsonl` contains the evaluation cases used by the Homework 6 CI workflow. Each line contains one JSON record. The adapter converts each record into one Harbor task.

Homework 6 requires at least 10 cases from at least two failure modes observed in Homework 4. The final set must contain at least one regression case and one capability case. Expanding the set to 30 cases is a stretch goal.

## Case fields

Each case contains:

1. `id`, a unique identifier such as `e-001`.
2. `mode`, the Homework 4 failure mode covered by the case.
3. `input`, including the authenticated role, user ID, first message, and any scripted follow-up messages.
4. `initial_state`, including `world: "reseed"`, `fixture: null`, and a short description of the facts the case assumes.
5. `expected.assertions`, which explain the intended behavior to a reader.
6. `expected.checks`, which contains exact checks on tool calls, replies, or database state.
7. `expected.judges`, which names an accepted Homework 5 judge when a code check cannot decide the result.

Harbor decides whether a run passed from `checks` and `judges`. The `assertions` field does not produce a reward.

## Baseline classification

Write a new case without `kind` or `baseline_pass_rate`. Export that case with `--baseline`, run it five times, and use the baseline summary to record its classification.

1. Five passes means `kind` is `regression`.
2. Any failure means `kind` is `capability`.
3. A capability case also records `baseline_pass_rate`. Five runs can produce `0.0`, `0.2`, `0.4`, `0.6`, or `0.8`.

The normal exporter rejects cases without a classification. Do not change an observed classification to produce the required mix. Add another reviewed case when you need a regression or capability case.

## Checks and judges

Use a code check for exact facts such as a tool call or final database value. Use an accepted Homework 5 judge when the expected result depends on the meaning of the reply.

The adapter copies the accepted judge's frozen prompt and model into the Harbor verifier. It formats the conversation and tool trace like the Homework 5 normalized input, then uses the same DocETL prompt wrapper and Pass or Fail parser.

## HW6 draft cases

The current 10 unclassified drafts cover `refund_approval_not_requested`
(four cases) and `required_human_handoff_missing` (six cases). Source scenarios,
confirmed HW4 labels and verified starting facts are in `hw6-provenance.json`.
Each case uses the original opening request with no prior conversation.

These are narrower checks for exact actions and state, not judges of the full
semantic failure definitions or reply quality. They make no LLM judge calls.
Refund cases require the full refund to enter the approval queue. Dispute and
account-change cases require a successful human ticket.

Two check details support these cases:

- `refund_status` accepts optional `amount_cents` to require the requested amount.
- `escalation_created` requires a successful `escalate_to_human` result whose
  ticket ID matches a database row, authenticated `user_id` and optional
  `store_id`, and the actual tool arguments. Optional `order_id` must appear
  as an exact numeric identifier in that ticket's summary or context.

Keep classifications absent until five Harbor trials finish with valid rewards.

## Harbor result layout

Harbor 0.23 writes an aggregate job summary plus separate trial result files.
The course reporting reader preserves that raw summary as `harbor-result.json`
and indexes each observed trial in `result.json`, ordered by `started_at` and
then trial name. The capability analysis records this ordering provenance.
Existing inline trial lists keep their original order. No rewards are inferred
from aggregate means, and completed failures are never rerun by this reader.
