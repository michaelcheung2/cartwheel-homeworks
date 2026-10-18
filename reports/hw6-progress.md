# HW6 status

**Technical deliverables are complete. The student's recording and personal
assessment remain pending.**

[Draft PR #1](https://github.com/michaelcheung2/cartwheel-homeworks/pull/1)
contains the cases, metrics, Docker/Ollama workflow, and observed evidence.
The temporary agent instruction has been reverted. The restored agent file
matches original-prompt commit `cf132d7` exactly.

## Cases and accepted classifications

Ten reviewed cases cover two HW4 failure modes: refund approval not requested
and required human handoff missing. Each uses its original opening request,
verified authorization and order facts, and a fresh seeded database inside
Docker. Source scenarios, HW4 labels, and checked starting facts are recorded
in `eval_cases/hw6-provenance.json`, separate from agent inputs.

Code checks require the exact tool/state behavior: full refund approval
without marking the order refunded, or a successful human ticket matching
the database and actual tool arguments. Dispute tickets also identify the
order. These checks do not score reply quality or policy claims. The
student's HW5 frozen judge and decision to keep it for human review suggestions
were preserved; this homework uses zero LLM judges.

| Cases | Baseline | Student-confirmed kind |
| --- | ---: | --- |
| e-001–e-008 | 0/5 each | capability, baseline_pass_rate 0.0 |
| e-009–e-010 | 5/5 each | regression |

The student accepted these classifications with "yes" before later experiments.
Five baseline trial records per case are in `eval_results/hw6-baseline.json`;
the review is in `reports/hw6-baseline-review.md`.

## Observed live experiments

All experiments used the same pinned `ollama_chat/llama3.1:8b` model through
Ollama on standard GitHub-hosted runners for this public repository. Model
digest: `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
The workflow uses pinned Harbor 0.23.0 and Ollama, verifies the model digest,
sets 8192-token context, and runs one trial at a time in fresh Docker
sandboxes. No hosted model API keys were supplied.

| Experiment | Trials | Observed result |
| --- | ---: | --- |
| [Baseline](https://github.com/michaelcheung2/cartwheel-homeworks/actions/runs/39165524413) | 50 | Eight cases 0/5; two cases 5/5 |
| [Intentional instruction](https://github.com/michaelcheung2/cartwheel-homeworks/actions/runs/39171132968) | 50 | e-010 4/5 blocked CI; e-009 5/5 |
| [After revert](https://github.com/michaelcheung2/cartwheel-homeworks/actions/runs/39172424810) | 50 | Both regression cases 5/5; CI passed |
| [Capability e-005](https://github.com/michaelcheung2/cartwheel-homeworks/actions/runs/39171101278) | 15 | 0/15; capability workflow passed |

**165 valid agent trials, zero trial exceptions, zero retries, zero judge
calls, and zero paid model API calls.** Recorded usage totals: 253,410 input
tokens and 17,240 output tokens. Harbor's cost field was null and remains
null; no billing measurement was invented. Phase totals and evidence links
are in `eval_results/hw6-run-totals.json`.

### Intentional regression and recovery

Both full CI runs came from PR #1. Temporary commit `0a22a59` instructed the
agent to answer account profile requests without tools. It covered both
account cases. The originally intended e-009 still passed 5/5; e-010 failed
once and is the observed Part D regression. Failed trial `e-010__pNLhduf`
made no tool calls and answered exactly "Please contact support to change
your account details." This matches the temporary instruction.

For e-010, 4/5 passes gave pass@1 = 0.8, pass@3 = pass@5 = 1.0, and
pass^5 = 0.0. The reliability gate correctly blocked on the failure.
The Harbor-trial step and artifact upload succeeded; the summary step failed
for the actual regression. The first commit was not rerun.

Revert commit `7b5035c` restored the original agent. All five e-010 trials
successfully called `escalate_to_human` and passed. E-009 also passed 5/5;
all eight capability cases remained 0/5 and did not block CI. This shows
recovery in this sample, without guaranteeing future reliability.
`ci-runs.json` records both URLs, commits, selection explanation and outcomes.
The two `eval_results/hw6-ci-*.json` files retain all 100 trial records and
the account-case replies and tool results.

### Capability trial-count comparison

The separate 15-trial experiment used original-prompt commit `cf132d7`,
before the temporary regression. E-005 passed 0/15. Pass@1, pass@3 and
pass@5 were all zero after the first 5, 10 and 15 trials; pass@10 and pass@15
were also zero at n=15. No estimates moved in this sample. This does not
prove the agent can never succeed.

The required file is `eval_results/e-005-15.json`. Its interpretation is in
`reports/hw6-capability-analysis.md`, and all source trials and usage are in
`eval_results/hw6-capability-evidence.json`.

## Offline verification and reporting compatibility

- Focused handout checks: **3 passed** with `--runxfail`.
- Configured offline CI selection: **91 passed, 13 skipped, 4 xfailed,
  12 xpassed**, locally with `OTEL_SDK_DISABLED=false` and on GitHub.
  These checks include isolated tool/state, adapter, replay, metric and
  Harbor-layout tests. Remaining homework markers were preserved.
- The lecture analysis tests now copy the preserved starter demo backup and
  its matching store traces into their isolated fixture. Student analysis
  records, labels, settings and test assertions were preserved.
- Both CI summaries and the capability analysis were reproduced offline
  from saved results. Every trial input, model identity, usage, exception
  field and reward was checked against the individual files.

The initial baseline workflow completed all 50 verifier rewards but failed
in reporting: Harbor 0.23 saves separate trial files rather than embedding
`trial_results` in its aggregate. The compatibility reader preserves the raw
summary as `harbor-result.json`, then indexes the exact records by started_at
and trial name in `result.json`. Ordering provenance is explicit, failures
remain intact, and no baseline agents were rerun.

Local macOS Docker startup failed with a virtualization error, so all live
agent trials used GitHub's runners. Local tests and saved-evidence analysis
made no model calls. Existing local data was not regenerated. Generated
Harbor tasks, raw job directories, database copies and credentials are ignored
and are not submission files.

The final evidence/documentation commit uses `[skip ci]` to avoid a third
unchanged 50-trial batch. Both required PR runs are already observed and
saved; no runtime, case, workflow or test changes are in that final commit.

## Student submission step

Record one continuous video of no more than five minutes, using
`reports/hw6-video-guide.md`. Show the cases, baseline classifications,
metrics, two CI runs, and capability comparison. Give your own assessment.
The recording remains unverified and pending.
