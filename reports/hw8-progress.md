# HW8 progress

Preparation, baseline, manual experiments and automated development search
are complete. Student accepted missing required human handoff as the target.
Current handout: `homework/module-5/hw8.md`. Cases, tests and frozen judges
were preserved; no held-out optimization case has run.

- Three local models checked; Llama 3.1 8B retained throughout development.
- Fixed seven development / three test cases; starting version committed.
- Manual prompt/tool/harness experiments recorded, including reverts and a
  repeat of the prompt improvement.
- Improve-loop skill used with `optimize/program.md`; 140/150 budgeted runs.
  Ten remaining runs cannot cover a full batch, so search stopped.
- Starting score: 14.3%. Proposed prompt candidate: 77.1%, write_pass_5 57.1%.
  Four handoff cases passed 5/5; refund cases passed 3/5, 0/5 and 4/5.
- Zero paid model API calls and zero judge calls. Usage from completed batches
  is recorded; an interrupted attempt has no invented count or usage.
- Existing authorization, thresholds, approval and pause logic unchanged.

See `hw8-candidate-review.md` / `.json` for concrete alternatives, observed
results, uncertainty and the recommended final selection. The small latest
gain was not repeated within the search budget. The student's selection
precedes the required final development rerun and one held-out test batch.

Remaining: student final selection, final-version save, four-configuration
test frontier, recording guide, and student's <=5-minute video.
