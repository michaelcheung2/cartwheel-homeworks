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

## Pending

1. Execute the baseline workflow using local Llama on the GitHub runner.
2. Five valid Harbor baseline trials per case: **50 agent runs, 0 judge calls**.
   Before a paid batch, show the chosen model and counts and obtain approval.
3. Student review and final classification from observed baseline rewards.
   No case has `kind` or `baseline_pass_rate` yet; add cases if needed to
   obtain at least one regression and one capability.
4. Verify Part C in Actions, complete Part D two observed CI runs on one PR,
   Part E capability analysis, and the student's video.

No live agent runs, judge calls, paid batches, CI runs, or observed baseline
classifications have been performed during this preparation.
