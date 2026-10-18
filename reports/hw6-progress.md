# HW6 progress

## Preparation and Part A

- Read the online HW6 handout, local handout, SPEC, facts.yaml, case format,
  supplied adapters, and the student's HW4/HW5 records before editing.
- The online handout recommends a small model, preferably the HW3 model.
  HW3 and the current local configuration use `ollama_chat/llama3.1:8b`.
  The student selected continuing without paid model API calls. Keep Llama
  throughout; the workflow starts Ollama on the GitHub runner.
- Preserved the HW5 frozen judge and the student's decision to use it only
  for human review suggestions. The initial cases use zero LLM judges.
- `uv sync` completed; Harbor 0.23.0 installed with `uv tool install`.
- Drafted 10 cases in `eval_cases/cases.jsonl`: four refund-approval cases,
  four dispute-handoff cases, and two account-change handoff cases. All use
  reviewed HW4 scenarios, including both failure examples and successful
  handoff examples. Trace IDs, labels, and starting facts are recorded in
  `eval_cases/hw6-provenance.json`, separate from the user inputs.
- Verified authorization, users, and order facts against a fresh temporary
  development seed. The existing local database and policy corpus were not
  regenerated. Original HW4 and HW5 artifacts remain unchanged.
- The code checks cover narrower exact actions/state than the full semantic
  taxonomy. Refund cases require the full amount in the approval queue and
  no refunded order status. Handoff cases require a successful tool result
  with a matching database ticket; dispute tickets include the exact order ID.
  Reply quality and policy claims are not scored by these cases.
- The supplied exporter generated all 10 unclassified Harbor tasks with
  `uv run python scripts/export_harbor_tasks.py --baseline`. Generated tasks
  remain ignored and are not submission artifacts.

## Observed verification

Offline command:

```bash
uv run pytest -q tests/test_hw6_case_checks.py tests/test_harbor_adapter.py \
  tests/test_replay_harness.py tests/eval/test_integration.py tests/eval/test_unit.py
```

Result: **28 passed**. Tests use isolated databases and scripted/tool-only
evidence; they are not live agent conversations or baseline measurements.
`git diff --check` passed.

Harbor's `--dry-run` preflight stopped because the Docker daemon is not
running. macOS rejected automatic Docker Desktop launch with error -54.
Local Ollama was initially unavailable, then started successfully. Its Llama
digest is `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
Direct Docker backend startup reached the VM but failed with a macOS
virtualization error: "Failed to issue Fuse sandbox extension."

## Parts B and C

Implemented pass@k, pass^k and the regression/capability CI decision. The
handout's focused `--runxfail` command passed all three tests.

Configured GitHub Actions with pinned Harbor and Ollama, digest verification
of the same Llama model, 8192-token context, one trial at a time, fresh Docker
sandboxes, and summary/artifact steps that always run. The public repository
uses standard GitHub-hosted runners. The workflow makes no paid API calls and
rejects cases that introduce LLM judges. Manual dispatch runs unclassified
baselines; pull requests require classified cases.

The offline CI command initially found the student's finalized records in
tests that pin the lecture demo. Corrected their isolated fixture source to
the preserved original demo backup and its local store trace export. No
assertions or student labels were changed. The local shell also sets
`OTEL_SDK_DISABLED=true`; tracing tests require `OTEL_SDK_DISABLED=false` to
exercise their in-memory exporters. With that process-only override the
configured offline CI selection reports **88 passed, 4 skipped, 4 xfailed,
12 xpassed**. The unfinished markers concern other homework functions.

## Observed baseline run

[Baseline Actions run](https://github.com/michaelcheung2/cartwheel-homeworks/actions/runs/39165524413)
used commit `cb9fa5b`. All **50 agent trials reached the verifier**, with
zero trial exceptions, zero retries, and zero judge calls. Recorded usage:
76,285 input tokens and 5,208 output tokens through local Ollama. No paid
model API calls were made. GitHub's separate offline job passed.

Each of e-001 through e-008 passed 0/5; e-009 and e-010 each passed 5/5.
These support eight capability cases (baseline 0.0) and two regression cases.
The student's final classification confirmation is pending. The full review
is in `reports/hw6-baseline-review.md`; all trial names, rewards, model, usage,
and observed tool names are in `eval_results/hw6-baseline.json`.

The workflow failed only after the agent trials, in the supplied summarizer:
Harbor 0.23 stores trial results separately rather than embedding them in its
aggregate `result.json`. Added a compatibility reader that preserves the raw
summary as `harbor-result.json` and indexes the exact per-trial records in
start-time order in `result.json`. It retains failures, exceptions, and rewards,
checks trial counts, and does not rerun agents. Trial ordering provenance is
explicit in the index and the Part E analysis. The corrected local summary
reports all ten cases successfully. The latest offline CI selection reports
**91 passed, 4 skipped, 4 xfailed, 12 xpassed**, including result-layout tests.

Prepared a manual `capability-15` workflow stage. Proposed case: e-005.
Its baseline is zero passes; the comparison will report the actual outcomes,
including zero estimates if all 15 new observations also fail.

## Pending

1. Student review and final classification from observed baseline rewards.
   No case has `kind` or `baseline_pass_rate` yet; add cases if needed to
   obtain at least one regression and one capability.
2. Verify Part C in Actions, complete Part D two observed CI runs on one PR,
   Part E capability analysis, and the student's video.

The baseline was run live with local Llama on GitHub's runner. Offline checks
and evidence recalculation used saved results. No hosted model API calls or
LLM judge calls were made. Required intentional-regression and reverted CI
runs and the 15-run capability experiment have not been performed yet.
