# HW4 review summary

## Corpus and reviewed sample

Source: live Langfuse, project cartwheel-dev. The corpus contains 344 stable
trace IDs from the student's 250 final HW3 scenarios. Review uses the stable
trace ID as the unit; adjacent session turns are context, not counted reviews.

| Required batch | Confirmed reviews | Selection |
| --- | ---: | --- |
| Initial breadth | 30 | 15 uniform; 15 representatives of eight structural clusters |
| Authenticated role | 30 | 10 per role; dimension chosen before outcome review |
| Depth search | 25 | Candidate positives and close negatives across eight modes |
| Final stability | 15 | Fresh uniform draw after the draft taxonomy |

All 100 selected IDs are distinct. The manifest preserves methods, seeds
and selection reasons. The sample contains 30 shopper, 29 merchant and 41
support traces. Initial seed: 20261010. The final uniform seed is 20261013;
it draws from all 259 previously unused records without outcome filtering.

All 100 free-form reviews are explicitly confirmed and verified as Langfuse
TEXT scores: 67 first-failure notes and 33 no-failure observations. Original
AI drafts, student acceptance and prior notes remain inspectable. The later
complete-trace labeling pass records additional failures beyond the initial
first-failure stopping point.

## Final taxonomy and binary judgments

Eight final categories, definitions, boundaries and example sets are
confirmed. Each has three confirmed positive examples and three close
negatives. patterns.json records SPEC sources, originating human-confirmed
annotation IDs and the likely evaluator type. Category examples do not
replace the full labeling pass: all 100 × 8 = 800 separate current-version
judgments have now been explicitly confirmed, saved in the eight JSONL label
files and read back from Langfuse. Zero judgments or synchronizations remain
pending. Corrections use append-only local history and stable remote score IDs.

The complete labeling package included 23 flagged boundary interpretations,
which the student explicitly confirmed. Original open codes were preserved
when later interpretation changed: for example, the vague dispute-policy
attribution in support-0156 is excluded from the final citation mode while
its missing human handoff and unsupported service promise are present.
Pure redundant confirmation does not meet the narrower printed/narrated
next-tool-call mode, though another category can apply.

## Taxonomy revision and repeated search

The student approved renaming missing_policy_citation v1 to
missing_or_invalid_policy_citation v2. The revised rule includes missing,
nonexistent and wrong-document identifiers, and excludes concrete recorded
tool facts. The previous name, definition and version remain in history.
Motivating confirmed cases:

- 490265edd3e8a70404e5e0da819d4e4f, support-0162: actual successful ticket
  SLA24 supports the reply's 24-hour followup without a policy citation.
- f34925c67cc748c9d1b70c04ce1721f9, support-0075: cw-refunds is incorrectly
  cited for the return window whose supporting document is cw-returns.

Eight initial searches produced 121 hypotheses. A fresh citation search
under v2 inspected all 344 traces and produced 15 more. All 60 earlier
accepted traces were individually rechecked; their initial 11 present,
44 absent and five uncertain AI hypotheses are preserved in
citation_revision_recheck.json alongside reconciliation to accepted v2
labels. The final complete labeling pass rechecked all 100 traces.

All 136 canonical search suggestions are explicitly adjudicated: 129
accepted and seven rejected. The 49 suggested IDs outside the selected 100
are search-only evidence for specific hypotheses; they are not added to the
full open-code sample or its all-category scores. AI retrieval decisions
never automatically became human annotations or population statistics.

## Rejected search evidence

Suggestion hw4-search-v1-ded7efd7abe4307c was rejected after inspection of
trace 01994e8ae186fc97b029be687ae706f6, support-0047. The quoted 24-hour
followup matches actual ticket151, sla_hours24. Citation v2 excludes that
concrete tool fact. The later portal-tracking advice is a separate unsupported
capability claim; it does not make the SLA quote valid citation-failure
evidence. The v2 SLA suggestion was also rejected. Full reasons and student
decisions remain in suggestions.json.

## SPEC decision

RESP-6 is approved and added to SPEC. A sufficiently specified actionable
support request requires a necessary tool attempt, required approval/handoff,
or a concrete blocker/genuine clarification. A printed/promised call is not
execution. Existing access, eligibility, approval and pause guards remain
intact. Historical outputs and running agent behavior were not changed.

Motivating accepted annotations:

- 1f365a5f-ff9e-4335-bfbd-216d8633cf27 → 26288d78507c65183456edb32b03f637.
- 39483642-2fcc-4b4c-bb31-42ea90359856 → 30df41a4cb3eec2f2e6bc05afe859561.
- a838ae44-e668-4dfc-893a-878bebb1c72b → 1773373a0030fb84dddd757de1fb4f37.

## Sample fractions

These fractions describe the deliberately selected 100-trace review sample.
They are not prevalence estimates for the 344-trace corpus. A trace can
contain several categories, so category counts overlap.

| Final category | Fail (present) | Pass (absent) | Sample fraction |
| --- | ---: | ---: | ---: |
| refund_approval_not_requested | 4 | 96 | 4% |
| unsupported_policy_claim | 25 | 75 | 25% |
| missing_or_invalid_policy_citation | 27 | 73 | 27% |
| invalid_tool_arguments | 9 | 91 | 9% |
| invented_record_values | 6 | 94 | 6% |
| ignored_record_inconsistency | 4 | 96 | 4% |
| required_human_handoff_missing | 10 | 90 | 10% |
| unexecuted_tool_request | 28 | 72 | 28% |

## Final-batch stability and AgentDebug

The student confirmed zero previously unseen consequential modes in the
final 15 uniform traces. Their 13 first failures and two no-failure notes
repeat existing categories: malformed arguments, policy/citation errors,
printed unexecuted calls and invented identifiers. No extra stability batch
was needed under the handout's several-new-modes rule.

After that confirmation, the taxonomy was compared with AgentDebug,
arXiv:2509.25370v1, section2.1 and AppendixA.2/Table2. The mapping and possible
omissions are in agentdebug_comparison.md. No published category was copied
without supporting Cartwheel human observations. External system failures
and fabricated completed tool results were considered separately from
model-argument failures and stalled calls.

## Verification and remaining student work

Fourteen focused offline app tests passed using isolated state and mock
clients. State checks verified four disjoint batches, all 800 trace/category
pairs, eight complete label files, sources/example boundaries, current
versions and saved search decisions. QuickJS syntax/DOM-stub checks use
actual live API state; they do not claim visual browser verification.
Live Langfuse readback matched all 100 TEXT notes and 800 numeric scores,
including trace/score IDs, values, current definition versions and evidence
notes. No new live Cartwheel model calls were used in HW4.

Real Chrome visual verification remains unavailable because macOS denied
headless startup. Trace-review feedback is written in interface_comparison.md
at the student's request, grounded in assistant-inspected traces and the
recorded workflow. The student's personal preliminary standard Langfuse
inspection remains unverified. Workshop is skipped and
workshop_notes.md is omitted. HW5 label shortfalls are recorded in
hw5-readiness.md. The student's continuous video (at most five minutes) is
still required. HW4 is not called complete while student work is pending.
