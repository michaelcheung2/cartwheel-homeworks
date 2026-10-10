# HW3 progress

## Current position

- Model: local Ollama `llama3.1:8b`; Cartwheel/runner name `ollama_chat/llama3.1:8b`.
- Application and tracing preflight passed: trace `cd00528c9f6d9282f54f8a7e46a6cecb` contained messages, model identity, tools/results, scenario ID, and measured usage.
- Student contributed role, intent, record, policy, and tools dimensions and approved the combined plan.
- Seed reset succeeded; all 18 policy documents validated. Previous database preserved at ignored local path `scenarios/results/hw3/database-before-hw3.db` (includes one previous extra escalation).
- Grounded 30 pilot plans saved before conversation generation: 18 coverage and 12 challenge, all roles/intents/styles and all six damaged records. Order access and refund eligibility checked against actual rows and deterministic helpers. State-changing refund/cancellation targets are distinct.
- Pilot conversation generation and independent critique completed with two workers. Calls went directly to Ollama, separately from application execution. Only user briefs reached the writer/critic. Actual receipt identifiers were bound locally afterward. Raw call outputs are saved under ignored `scenarios/results/hw3/pilot-generation/`.
- The local writer and critic frequently lost the assigned role, intent, or style, or invented entities. Structural checks rejected malformed drafts; 26 final editorial corrections restore the approved plans and are documented with before/after messages in `scenarios/pilot_edits.json`. These are conversation edits, not student assessments. Catalog snapshots were supplemented during the final grounding check.
- Pilot validator passed offline: 30 records, 30 unique IDs, 18 coverage / 12 challenge, six data quality cases.
- Student approved the pilot conversation sample. Seed data was reset immediately before running the 30 scenarios against the live Cartwheel endpoint with local Ollama.
- Pilot execution completed: all 30 results have status `completed` (18 coverage / 12 challenge). Summed scenario duration: 61.43 seconds, using local Ollama.
- Export succeeded to ignored diagnostic file `scenarios/results/hw3/pilot-traces.json`: 39 traces, all 30 unique scenario IDs. Per-scenario trace counts match scripted user turns. Every trace contains conversation messages and captured model messages/usage; tool observations contain inputs and outputs.
- Prepared ten cases with full observed conversations, tool results, and Langfuse links in `reports/hw3-pilot-review.md`. The student confirmed all ten scenarios valid, eight failures and two matching outcomes, with no requested scenario changes. Draft proposals are in `reports/hw3-pilot-review-draft.jsonl`, separate from the required human review file.
- Observed post-run states preserved in `reports/hw3-pilot-state.json`; orders 117/64 remain delivered with no refund records, and orders 10/105 remain placed.
- **Current:** student-confirmed judgments are saved in `scenarios/pilot_review.jsonl` (10 valid / 8 confirmed failures). Final generation and independent critique completed for all 250 scenarios, with two workers; 128 documented editorial corrections restore intent, role, style, and plausible followups. Full authoritative extra metadata is included in each final scenario and remained out of generation payloads. Final and monitoring validators passed offline; authentication, distinct write targets, per-conversation call records, and exact monitoring subset were checked.
- **Final execution complete:** all 250 scenarios completed using local Ollama, 175 coverage / 75 challenge. Summed scenario duration: 580.31 seconds. No scenario reruns were needed.
- The first export missed the last scenario while tracing ingestion was still finishing. Its trace appeared after a short wait; retrying the export succeeded without re-executing any scenario.
- Export: `traces/support_traces.json`, 344 traces covering exactly 250 unique final scenario IDs and all 344 user turns. Every trace conversation was compared with saved results; role/user ID, scenario attribute, model/messages/usage, and tool outputs/errors were verified.
- Smoke report saved and refreshed after ingestion: `reports/smoke-output.txt`. This report includes the whole local project; final-only counts are in `reports/hw3-final-summary.json`.
- Three scenario examples (including challenge and multi-turn cases) inspected in the export: support-0001, support-0185, support-0169. Actual trace links and tool results are recorded in the summary and video guide.
- All nine files in the handout's Files to commit list exist and are nonempty. Offline checks and live-model runs are listed in `reports/hw3-submission-check.json`.
- **Next:** student records the continuous video (at most five minutes), following `reports/hw3-video-guide.md` if useful. HW3 submission destination: `origin/main` in `michaelcheung2/cartwheel-homeworks`; push status is verified separately after this submission commit. No final correctness labels or failure taxonomy were created.


## Approved dimensions

| Dimension | Values | Source/reason |
| --- | --- | --- |
| Role | shopper, merchant, support | SPEC AUTH-1: access and available tools vary. |
| Intent | order_lookup, refund, cancellation, policy_question, product_search, dispute, account_change, out_of_scope | SPEC SCOPE-1/2, ESC-2/3: different actions and escalation/refusal requirements. |
| Record involved | orders in different states, products, platform/store policy pages, none, six damaged records | SQL records and data_quality_cases determine the answer and required handling. |
| Applicable policy | platform_rule, store_override, none | facts.yaml: store overrides take precedence; some tasks make no policy claim. |
| Tools needed | none, one_lookup, several_calls | SPEC TOOL-1 through TOOL-9: distinguishes direct clarification/refusal, retrieval, and action workflows. |
| Difficulty | well_specified, ambiguous, missing_information, boundary, inconsistent_data | SPEC AUTH-1, RESP-3, ESC-4; damaged records and deterministic thresholds/windows. |
| User language | neutral_conversational, terse_fragmentary, typo_heavy, confused_rambling, frustrated_impatient, repetitive_pressuring, operational_shorthand, requests_short_plain_answer | SPEC RESP-4/5: clarity and respect should survive different language styles. |

Turn count is recorded per conversation, not a separate dimension. Final plan: 175 coverage / 75 challenge, including five scenarios for each damaged record. Final IDs must differ from pilot IDs.

## Deliverables

- [x] `scenarios/pilot_scenarios.jsonl`: 30 generated and validated conversations; human sample approved.
- [x] `scenarios/pilot-results.jsonl`: all 30 observed application runs completed.
- [x] `scenarios/pilot_review.jsonl`: student confirmed 10 valid scenarios and 8 failures.
- [x] `scenarios/support_scenarios.jsonl`: generated and validated 250 scenarios, 175 coverage / 75 challenge; five per damaged record. Human review confirmed and revision applied.
- [x] `scenarios/support_review.jsonl`: 15 confirmed decisions, 14 accept / one revise; revision applied.
- [x] `scenarios/monitoring_scenarios.jsonl`: selected and validated 50 cases (35 coverage / 15 challenge), all roles and intents; approved revision synchronized.
- [x] `scenarios/final-results.jsonl`: all 250 completed runs.
- [x] `reports/smoke-output.txt`: observed tracing report, refreshed after the final trace became visible.
- [x] `traces/support_traces.json`: 344 complete traces, 250 unique final scenario IDs; conversations/content checked, including three scenario examples with challenge and multi-turn cases.
- [ ] Student video (at most five minutes), including an actual revised final scenario and verified trace/ID count.

## Checks and review gates

- [x] Live application/tracing preflight with local Ollama.
- [x] Offline database generation and policy validation.
- [x] Dimension plan approved by student.
- [x] `uv run python -m scenarios.validate scenarios/pilot_scenarios.jsonl` (offline; passed).
- [x] Human pilot conversation sample approval (required by scenarios/skill/SKILL.md).
- [x] Pilot execution: 30 completed live-model runs; trace export verified.
- [x] Student review of 10 observed pilot results / eight confirmed failures.
- [x] Human final conversation review of 15 scenarios, covering both groups, all roles, every intent; revision applied.
- [x] `uv run python -m scenarios.validate scenarios/support_scenarios.jsonl --final` (offline; passed again after approved revision).
- [x] Reset mutable state immediately before final execution.
- [x] 250 completed final runs; summaries separate coverage/challenge.
- [x] Smoke report, successful export, 250 unique IDs and three scenario trace content inspections.

Pilot assessments were explicitly confirmed by the student and recorded. Final scenario review is confirmed; the student recording remains pending. No human labels have been invented.

## Reproduce the pilot conversation file

The plans are saved separately from user-message generation. Preserve the existing audit and edits before changing any briefs.

```bash
uv run python -m scenarios.generate_conversations \
  scenarios/pilot_plans.jsonl scenarios/pilot_scenarios.jsonl \
  --model llama3.1:8b --workers 2 \
  --audit scenarios/results/hw3/pilot-generation \
  --edits scenarios/pilot_edits.json
uv run python -m scenarios.validate scenarios/pilot_scenarios.jsonl
```

The model calls above generate users; they do not execute scenarios against Cartwheel. Reusing the saved audit avoids repeating local model calls. Removing the audit regenerates different drafts, which need new editorial review rather than blindly applying old edits.

## Reproduce the final conversation file

```bash
uv run python -m scenarios.generate_conversations \
  scenarios/support_plans.jsonl scenarios/support_scenarios.jsonl \
  --model llama3.1:8b --workers 2 \
  --audit scenarios/results/hw3/final-generation \
  --edits scenarios/support_edits.json
uv run python -m scenarios.validate scenarios/support_scenarios.jsonl --final
```

Cached-call reproduction matched the complete final JSON records. Preserve student-approved revisions alongside editorial edits before reproducing after review. Final execution, result completeness, and trace content/completeness checks passed. Student-approved support-0169 revision is included in the saved editorial edits and preserved by the editor.
