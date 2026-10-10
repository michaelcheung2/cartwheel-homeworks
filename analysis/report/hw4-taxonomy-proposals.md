# Taxonomy review package — candidates, not final labels

The student explicitly approved all eight candidate groupings, the citation
version-2 revision and RESP-6 after reviewing the displayed package. The
additional groups derive from accepted initial-batch observations. Each mode's full definition,
boundaries, requirement sources and originating annotation IDs appear in
`analysis/state/patterns.json` and the Taxonomy screen.

| Candidate | Status | Main evidence |
| --- | --- | --- |
| refund_approval_not_requested | Approved candidate | Eligible $254.50 refund never queued |
| unsupported_policy_claim | Approved candidate | Delivered status incorrectly forbids refunds |
| missing_or_invalid_policy_citation | Approved candidate, version 2 | Correct cancellation rule lacks citation |
| invalid_tool_arguments | Approved candidate | String `"null"` causes product-search validation failures |
| invented_record_values | Approved candidate | 2025 dates changed to 2023; missing delivery date filled with shipment date |
| ignored_record_inconsistency | Approved candidate | Delivery precedes shipment; delivered status lacks required date |
| required_human_handoff_missing | Approved candidate | Actual disputes and unresolved product queries lack human tickets |
| unexecuted_tool_request | Approved candidate; RESP-6 recorded | Printed tool JSON replaces execution |

## Approved citation revision

Renamed `missing_policy_citation` to `missing_or_invalid_policy_citation` and
revised its binary rule to cover missing, nonexistent and wrong-document
citations. Exclude concrete tool facts: reporting a created ticket's actual
24-hour SLA is different from claiming a general platform response policy.

The approved boundary is supported by these confirmed role-batch cases:

- `support-0162`, trace `490265edd3e8a70404e5e0da819d4e4f`: the tool returns
  `sla_hours: 24`, and the reply accurately reports that concrete value.
- `support-0075`, trace `f34925c67cc748c9d1b70c04ce1721f9`: the reply cites
  `cw-refunds` for a return-window claim, whose supporting document is
  `cw-returns`.

The old name, definition and version are preserved in patterns.json history.
A fresh version-2 search examined all 344 records and returned 15 hypotheses.
All 60 earlier reviewed traces were rechecked; proposed results are preserved
in citation_revision_recheck.json, with uncertainty explicit and no labels
inferred. The original open codes remain unchanged.

## Task-completion decision

RESP-6 is explicitly approved and recorded in SPEC. It makes the desired
stopping rule precise while preserving authorization, eligibility, approval
and pause protections. `hw4-spec-clarification.md` records the decision and
its motivating accepted annotations. Historical traces and application
behavior are unchanged.

## Still required

All eight are candidates until the remaining sampling batches and boundary
checks are complete. Each final mode needs at least three confirmed
positives, three close negatives when available, and every trace/mode
judgment. Search signals and accepted free-form notes do not automatically
assign those final labels.
