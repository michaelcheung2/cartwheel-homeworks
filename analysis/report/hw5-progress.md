# HW5 progress

## Preparation

- Read AGENTS.md, README.md, SPEC.md and the current HW5 handout.
- Read the course write-judge-prompt and validate-evaluator skills.
- Preserve HW4 work; do not apply the reference patch.
- Confirmed mode: unsupported_policy_claim; student accepted the boundary.
  Existing labels: 75 Pass / 25 Fail across 100 trace IDs and 95 sessions.
  Five sessions contain multiple selected turns. Close scenario variants
  still need checking before selecting one record per independent conversation.
- Alternative: missing_or_invalid_policy_citation, 73 Pass / 27 Fail,
  also 95 sessions before checking close variants.
- Student chose local Llama for the main judge and is interested in a Qwen
  comparison. This departs from the handout's required gpt-4o-mini model.
  At the student's request, qwen3:8b was downloaded with ollama pull;
  Ollama verified its digest and reported success. Installed models verified
  with ollama list: llama3.1:8b (4.9 GB), qwen3:8b (5.2 GB, digest prefix
  500a1f067a9f), and the retained qwen3:0.6b (522 MB).
  The two 8B models can be compared on the same development examples.
  Local judge calls are now recorded under analysis/state/judges/.
- Prepared hw5-mode-and-label-review.md with four prior human-accepted
  positive search hypotheses and one new candidate, with recorded evidence
  and earlier session context. Student confirmed all five proposed Fail labels.
- Saved 105 confirmed HW5 labels using 1=Pass/0=Fail, preserving HW4 files.
  Independence audit selects 94 representatives: 65 Pass / 29 Fail, excluding
  11 related records. Variants of the same documented data-quality case and
  same-order/same-intent requests are grouped; Fail representatives enrich
  the class deliberately. This is not a prevalence sample.
  Audit: analysis/state/hw5_eligibility.json. One further independent Fail
  needs human review before preparing fixed inputs and splitting.
- Student confirmed the final ticket-email-link Fail candidate. There are
  now 106 confirmed labels; 95 eligible independent representatives have
  65 Pass / 30 Fail. The 11 excluded related labels remain preserved.
- Fixed evidence-only inputs prepared with hash protection. One-time seed-7
  20/40/40 split saved: training 13 Pass/6 Fail, dev 26/12, test 26/12.
- Runner, three-example training-only prompt v0, and development review UI
  implemented. Judge ID unsupported_policy_claim-v0 registered; local
  DocETL development run in progress. No held-out test calls have run.
- 23 focused offline tests pass; QuickJS syntax check passes using a
  temporary package environment. Live review API returns 38 development
  records and excludes held-out predictions. Actual visual browser
  verification has not been performed for HW5.
- Initial DocETL tool-output transport failed before saving predictions.
  Switched to DocETL structured JSON output, correctly applied the worker
  limit and resumed the same judge ID; prompt/model/input/split unchanged.
- v0 development completed: 38 predictions/critiques saved. TP 12, FN 14,
  TN 11, FP 1; TPR .4615 (Wilson .2876–.6454), TNR .9167 (.6461–.9851).
  All 15 disagreements were inspected by the assistant and prepared with
  full fixed inputs for student review in hw5-v0-disagreement-review.md.
  Proposed decisions: 14 judge errors and one caveat-boundary clarification.
  Student subsequently confirmed all 15 decisions and the caveat boundary;
  saved acceptance provenance preserves the AI proposals. Labels unchanged.
- First prompt revision v1 saved with four training-only examples; its
  local Llama development run completed on the same 38 records.
  Fixed inputs and split remain unchanged. No held-out test calls have run.
- v1 did not improve alignment: TP 12, FN 14, TN 10, FP 2; TPR .4615
  (Wilson .2876–.6454), TNR .8333 (.5520–.9530). All 16 disagreements
  inspected by the assistant and proposed for student review in
  hw5-v1-disagreement-review.md. Eleven repeat v0; five are new; four v0
  disagreements resolved. Recommend keeping labels and marking judge errors.
  Student subsequently confirmed all 16 judge-error decisions and the final
  revision. Accepted decisions are saved with AI proposal provenance.
- Second/final revision v2 saved with two Pass and two Fail training examples.
  Relevant SPEC refusal rules added and the rubric shortened. v2 development
  completed on the same 38 records; no labels, inputs or splits changed.
  No further prompt revisions are allowed under the handout.
- v2 results: TP 14, FN 12, TN 11, FP 1; TPR .5385 (Wilson .3546–.7124),
  TNR .9167 (.6461–.9851). All 13 disagreements inspected by the assistant
  and prepared in hw5-v2-review-and-final-choice.md. Proposed final choice
  is v2: highest observed dev TPR and tied highest TNR, with material false
  alarms and overlapping intervals. All 13 decisions and final choice need
  student confirmation at that point. Student subsequently confirmed all
  13 decisions and selected v2 before any test predictions were available.
- v2 frozen once and tested on 38 held-out records: TP 11, FN 15, TN 10,
  FP 2. TPR .4231 (Wilson .2554–.6105), TNR .8333 (.5520–.9530).
  Test metrics and all verdicts/critiques saved. No prompt edits after test.
  Student's decision about using this judge remains pending.
- Optional Qwen3 8B comparison is running on the same development records
  with the frozen v2 prompt, in separate model_comparison state. Qwen's
  thinking mode is disabled for structured output; no Qwen test calls.
- 27 focused offline tests pass, including comparison-state isolation and
  the fixed-final-prompt gate.
- 24 focused offline tests now pass, including JSON transport/worker setting
  forwarding. git diff --check passed.
- 25 focused offline tests now pass, including the gate that requires all
  development disagreements to be human reviewed before revising/freezing.

## Next

The Qwen comparison is complete: 38 development records, TP 21 / FN 5 /
TN 9 / FP 3; TPR .8077 (Wilson .6212–.9149), TNR .7500 (.4677–.9111).
It used the unchanged v2 prompt and separate state; no Qwen test calls.
Technical files are packaged in one local HW5 commit. Next, obtain the
student's recording; GitHub push is pending. The student confirmed rejecting
automatic decisions while allowing suggestions for human review.
The student's video remains pending. Preserve fixed inputs/splits and original HW4 labels. See
hw5-run-guide.md for interruption/resume commands.

## Deliverables

- [x] Confirmed mode definition, boundary and required evidence.
- [x] Human-reviewed labels/evidence: analysis/state/hw5_labels/<mode>.jsonl.
- [x] Exact fixed inputs: analysis/state/hw5_trace_inputs.json.
- [x] One-time 20/40/40 split with actual class counts: analysis/state/splits.json.
- [x] Runner: analysis/run_judges.py.
- [x] Initial prompt with training examples only: analysis/prompts/.
- [x] Initial judge version, cached development predictions and critiques.
- [x] Initial development metrics with confusion counts, TPR/TNR and Wilson intervals.
- [x] All development disagreements reviewed; two prompt revisions completed.
- [x] Student's final prompt choice, freeze and held-out test.
- [x] Test metrics and saved verdicts/critiques; offline recalculation verified.
- [x] Optional Qwen comparison on development only.
- [x] Student's decision: no automatic decisions; suggestions for human review only.
- [x] Commit required technical files, preserving HW4 artifacts.
- [ ] Student's continuous video, at most five minutes.

No numerical acceptance target is required. Show model and trace count and
obtain approval before each paid batch. Keep test predictions hidden until
the selected judge is frozen. Resume interrupted runs with the same judge ID,
without repeating registration, splitting or freezing.
