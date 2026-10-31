# HW7 progress

Started on branch `hw7/monitoring`, preserving all committed HW6 work.

## Implemented and verified

- Read the handout, monitoring contracts, specification, and the student's
  HW3/HW5/HW6 artifacts. No reference patches or new judges were introduced.
- Confirmed the original monitoring set: 50 scenarios, 68 original HW3
  traces, one complete period and the same local Llama model.
- Sampling, Rogan–Gladen correction with both bootstrap uncertainty sources,
  and stable Langfuse score records implemented.
- Monitor command validates scenario/model/turn completeness, rejects
  separate session retries, preserves ordered HW5 conversation/tool evidence,
  uses the final trace for scores, and keeps random/risk verdicts separate.
- Repeated periods reuse exact saved verdicts and send the same score IDs.
  Empty rolling windows record zero conversations without judge calls.
- Frozen prompt/model/wrapper/parser preserved. Restored the supplied
  monitoring adapter's missing frozen completion settings, including the
  student's structured output mode, context size, temperature and threads.
- All 15 overlapping original final-trace inputs match the student's HW5
  input bytes when prepared from the original live cache. The frozen local
  model digest was verified.
- Configured 20% random sampling, policy lookup and multi-turn risk groups,
  and threshold 0.15 before monitoring-period judgments. The original plan
  contains 10 random, 20 unique risk, 27 unique selected records; risk groups
  overlap. No period failure rate was calculated from this plan.
- A fresh preflight succeeded through DocETL and local Ollama: 2,724 input
  tokens, 148 output tokens, 5.56 seconds. An initial pipeline check reused
  an exact HW5 cache entry. Neither is a completed monitoring period or
  human assessment. Details are in `reports/hw7-judge-preflight.json`.
- Daily/manual workflow scaffold uses a self-hosted runner labelled
  `hw7-monitor` for local Langfuse and the frozen local Ollama judge. It
  uploads output even after failure and needs no paid provider key.

## Checks

All tests and planning checks below ran offline, with no model calls:

- Focused handout HW7 checks with `--runxfail`: **3 passed**.
- Added monitor checks: **12 passed**, including incomplete periods, mixed
  models, retries, sampling/prevalence separation, stable repeated score
  payloads, empty windows, and frozen DocETL settings.
- Expanded CI selection with process-only `OTEL_SDK_DISABLED=false`:
  **103 passed, 13 skipped, 1 xfailed, 15 xpassed**. One DocETL dependency
  deprecation warning. Remaining homework placeholders were preserved.
- Before-period dry-run succeeded; after-period invocation correctly
  rejects its pending timestamps.

The preflight above is the only fresh live model evaluation so far.
No paid model APIs were called. Existing database, scenario results, student
labels, frozen judge and local settings were preserved.

## Pending infrastructure and deliverables

Docker is unavailable: no daemon socket, and launching Docker Desktop returns
macOS error -54. Local Langfuse on port 3000 is offline. The student has been
asked whether to restore local Langfuse with a self-hosted runner or use an
existing reachable Langfuse host. No runner was registered and no new service
was purchased.

After Langfuse is available:

1. Seed an isolated temporary database with the supplied tool, preserving
   local data. Start the traced server against it and run all 50 monitoring
   scenarios once with the same Cartwheel model.
2. Verify both live periods, record the actual after UTC timestamps, and
   commit `scenarios/hw7-after-results.jsonl`.
3. Execute both periods, save actual `monitoring/history.jsonl` and
   `monitoring/prevalence.svg`, and rerun after to verify score IDs update in
   Langfuse. Offline idempotency tests do not establish remote behavior.
4. Configure the reachable host/runner and secrets locally, create the three
   required dashboard views, manually dispatch and verify the workflow.
   Daily scheduling starts only after the workflow is on the default branch.
5. The student writes the four interpretations in `monitoring/README.md`
   after inspecting actual results and records the required ≤5-minute video.

Missing histories, charts, scores, dashboard and scenario results remain
pending. No synthetic test data was recorded as homework evidence.
