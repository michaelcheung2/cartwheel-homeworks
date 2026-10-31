# HW7 progress

## Completed

- Preserved the frozen student-selected HW5 judge and local Llama 3.1 8B.
- Implemented sampling, Rogan–Gladen correction/bootstrap, monitoring,
  stable score writes, two-period history/chart, and daily/manual workflow.
- Docker and local Langfuse are healthy. Seeded an isolated temporary world,
  preserving existing data and policies. All 50 new scenarios completed
  once, with 68 traced turns. Both live periods passed completeness checks.
- Judged 27 unique conversations per period: 10 random, 20 risk, seven
  overlaps. Random and risk evidence remain separate.
- Both raw random rates are 50%; corrected estimates are 0%, with 95%
  intervals of 0–100%. Risk flags are 10/20 before and 14/20 after.
  Judge flags are not confirmed failures. The uncertain estimates do not
  establish improvement or absence of failures.
- Wrote and read back 31 stable IDs/names/values per period. Repeated after
  reused exact judgments and created no duplicates (62 total named scores).
  Current Langfuse requires batch scores to target a monitoring session;
  synchronous Scores API writes propagate errors with OTel disabled.
- Created and read back the three-widget dashboard. Browser rendering
  remains unverified because local Chrome launch failed.
- A real empty rolling window succeeded with zero judge calls.
  No paid model APIs were used.

See `hw7-monitoring-evidence.json`, `hw7-dashboard.json`, scenario results,
and `monitoring/history.jsonl` / `prevalence.svg`. Raw exports, generated
worlds, and credentials stay out of commits.

## Checks

- Offline focused handout HW7 checks: **3 passed**.
- Offline monitor checks after score fix: **13 passed**; one dependency
  deprecation warning.
- Earlier expanded offline CI: **103 passed, 13 skipped, 1 xfailed,
  15 xpassed**. Remaining homework placeholders were preserved.
- Live checks used local Ollama/Langfuse: both comparison periods, score
  write/readback, cached after repeat, empty window, dashboard API.
- Initial fresh preflight: 2,724 input tokens, 148 output tokens, 5.56
  seconds (`hw7-judge-preflight.json`). Period provider-request totals were
  not measured; DocETL can reuse exact caches.

## Remaining

The workflow exists on `hw7/monitoring`. GitHub requires it on the default
branch before dispatch; attempted branch dispatch returned 404. No local
GitHub runner is registered. User decision requested before publishing
HW6/HW7 to main and enabling daily jobs on the Mac.

The student supplies four interpretations in `monitoring/README.md`,
inspects the dashboard, and records a video of at most five minutes.
Successful manual workflow dispatch remains pending infrastructure.
