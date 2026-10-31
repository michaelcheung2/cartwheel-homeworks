# HW7 monitor

## Current status

Both comparable periods, the history/chart, 62 Langfuse scores, and the
three-widget dashboard are complete. All 50 new scenarios completed in 68
traced turns using local Ollama. No paid model API calls were used.
Scheduling, successful workflow dispatch, and student interpretations/video
remain pending.

| Observation | Before | After |
|---|---:|---:|
| Conversations / traces | 50 / 68 | 50 / 68 |
| Random flags | 5 / 10 | 5 / 10 |
| Risk flags (inspection only) | 10 / 20 | 14 / 20 |
| Risk flags outside random sample | 9 | 11 |
| Raw random flag rate | 50% | 50% |
| Corrected prevalence | 0% | 0% |
| 95% bootstrap interval | 0%–100% | 0%–100% |

These are judge flags, not confirmed failures. The correction clamps an
otherwise negative estimate to zero because the measured false-positive
rate exceeds the observed random flag rate. The full-range intervals do
not establish improvement or absence of failures. Failure sensitivity is
0.8333 and pass specificity is 0.4231. Neither point estimate crosses the
preselected 0.15 threshold. Observed evidence is summarized in
`reports/hw7-monitoring-evidence.json`.

The configuration keeps the HW3/HW6 Cartwheel model
`ollama_chat/llama3.1:8b` and the student-selected frozen judge
`unsupported_policy_claim-v2`. Its prompt, model, structured output settings,
wrapper, and Pass/Fail parser remain pinned. The SHA-256 in the configuration
checks the frozen artifact before use. The judge supports human review
suggestions; scores and threshold crossings do not make customer decisions.

The original HW3 period contains all 50 selected scenarios in 68 traces.
The new period's verified timestamps are recorded in `config.json`.
The comparison rejects missing scenarios or turns, changed requests, missing
models, mixed models, duplicate trace IDs, and sessions from separate retries.

## Sampling and correction

- Seeded uniform random sample: 20%, or 10 of 50 conversations.
- Risk groups: `policy_lookup` and `multi_turn`, using actual tools/user turns.
- Judge the union once; preserve both memberships for overlapping records.
- Use only random verdicts for Rogan–Gladen prevalence and its seeded
  percentile bootstrap, resampling both the paired held-out data and random
  predictions. Failure sensitivity is HW5 test TNR; pass specificity is
  HW5 test TPR.
- Threshold selected before either period's monitoring results: **0.15**.
  Crossing it starts human error analysis. Confirmed failures can become HW6
  cases; an unreviewed judge flag does not become a confirmed failure.

The saved before-period plan selects 10 random and 20 unique risk records,
with 27 unique records total. Risk counts overlap: policy lookup 14,
multi-turn 17. These are selection counts, not observed failure rates.

`judge_calls` counts conversation evaluations submitted to the supplied
batch judge. DocETL may reuse exact cached calls; the monitor does not claim
that this is a measured provider-request count. A repeated period reuses
its own exact evidence cache and writes the same score IDs again. Changed
evidence requires a separate output directory.

## Commands

Offline planning from the saved HW3 export makes no model calls:

```bash
uv run python -m monitoring.run --period before \
  --trace-file traces/support_traces.json --dry-run
uv run pytest --runxfail tests/test_hw_holes.py -k 'hw7_sampling or hw7_corrected or hw7_score'
uv run pytest tests/test_hw7_monitor.py -q
```

The original HW5 live cache was also checked: all 15 overlapping final-trace
inputs match HW5 byte for byte. The sorted archived export preserves the
same fields and evidence but orders nested JSON keys differently.

To repeat the completed live comparison:

```bash
uv run python -m monitoring.run --period before
uv run python -m monitoring.run --period after
uv run python -m monitoring.run --period after
```

The second after run reuses saved verdicts and rewrites stable score IDs.
Verify those IDs and values through Langfuse's Scores API; offline tests
alone do not establish that the remote service updated them.

`monitoring/history.jsonl` receives one record per completed period.
`monitoring/prevalence.svg` is created when both completed periods exist.
Plans, separate random/risk verdicts, score payloads, caches, and errors are
kept under ignored `monitoring/output/`. Saved exports are accepted only
for dry runs; actual monitoring must read Langfuse.

## New scenario run

Preserve the current database and seed a separate temporary world with the
supplied seed tool. Start the server using `CARTWHEEL_DB` and
`CARTWHEEL_POLICIES_DIR` pointing to that world, with Langfuse capture enabled.
Record UTC start/end around this command:

```bash
uv run python -m scenarios.runner scenarios/monitoring_scenarios.jsonl \
  --model ollama_chat/llama3.1:8b --output scenarios/hw7-after-results.jsonl
```

Run all 50 scenarios once. Check every completion, trace, scenario ID,
model, and scripted turn before adding the after-period timestamps. Do not
combine separate retries into the comparison period.

## Scheduler and dashboard

`.github/workflows/monitor.yml` has daily and manual triggers. It uses a
self-hosted runner labelled `hw7-monitor`, because both Langfuse and the
frozen judge are local. Runner registration remains pending the student's
hosting choice. Set `LANGFUSE_HOST` as a repository variable and
`LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` as repository secrets. The local
judge needs no provider key. Secrets stay in `.env` locally; never paste
values into chat or committed files.

The command `uv run python -m monitoring.run --last-hours 24` groups traces
by session ID. Empty windows save a zero count and succeed without calling
the judge. The workflow uploads outputs even after failure. Scheduling takes
effect only after the workflow is on the default branch.

The [local dashboard](http://localhost:3000/project/cartwheel-dev/dashboards/cmvwu5tz8000cs307uf1wi72a) contains:

1. `unsupported_policy_claim_verdict` over time (random sample).
2. `unsupported_policy_claim_risk_verdict` over time (risk groups).
3. Traces with either score equal to 1, for human inspection.

Dashboard and widget definitions were created and verified through the
Langfuse public API; browser rendering remains unverified because local
Chrome failed to launch. Select a date range including October 10 and
October 31, 2026. Definitions are in `reports/hw7-dashboard.json`.

Langfuse v3.225.11 requires period scores to target a monitoring batch
session, `cartwheel-monitor-<mode>-<period>`. Verdicts target actual final
traces. Synchronous public score writes propagate errors with tracing
disabled. Readback verified 31 IDs/names/values per period; repeating after
left 62 total named scores with no duplicates.

## Student interpretation — pending

The student completes these four answers after inspecting the actual results:

1. Did the corrected estimate move between periods? **Pending.**
2. Do the intervals support a conclusion, or is it uncertain? **Pending.**
3. What did risk groups reveal beyond the random estimate? **Pending.**
4. What should happen after a threshold crossing? **Student's answer pending.**

Record a video of no more than five minutes after the two estimates,
dashboard, and successful workflow run are available. Show the common
scenario set/model, sample memberships, rates/intervals, dashboard, workflow,
and your proposed response to a threshold crossing.
