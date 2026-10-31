# HW9: reducing cost — local submission; paid caching checks skipped

The authorized local work is complete. Parts A, B and the local Part D
experiment are saved; Part E includes completed runs only. The student
requested that checks costing money be skipped, so the required live OpenAI
Part C comparison is **skipped and unverified**. This submission does not
fulfill that handout requirement. The student configuration assessment and
continuous video remain pending.

## Part A: call-site costs

Regenerate: `uv run python profile/scripts/costs.py`.

| Category / call site | Recorded calls or verdicts | Input tokens | Output tokens | API fee |
| --- | ---: | ---: | ---: | ---: |
| Customer, `server/app.py:202` | 815 actual generations | 709,183 | 39,563 | $0 |
| HW5 judge, `analysis/helpers/scale.py:267` | 152 saved verdicts | ~374,015 | ~17,597 | $0 |
| HW7 judge, `monitoring/run_judges.py:138` | 54 saved verdicts | ~134,271 | ≤55,296 configured output cap | $0 |

Customer counts use API usage and deduplicate observation IDs across HW3
and HW7 exports. All sites tie at zero model API fees. Customer calls and
HW5 judge dispatch have the largest token totals within their categories.
Judge usage was not saved: input/output estimates and the HW7 per-verdict
output cap are labeled in `profile/results/costs.csv`. Saved verdict counts
do not establish provider request counts, cache misses, or retry counts.
These fees exclude electricity and hardware. No dollar reduction is claimed.

## Part B: concise replies, rejected and reverted

One prompt change requested at most two concise sentences after required
tools, preserving the observed outcome, required next steps and citations.
It was committed before 35 local development trials; zero judge calls.

| Metric | HW8 final | Concise replies |
| --- | ---: | ---: |
| Development score | 77.14% | 74.29% |
| write_pass_5 | 57.14% | 57.14% |
| Input tokens | 72,875 | 76,177 |
| Output tokens | 3,942 | 3,111 |
| API cost per 100 conversations | $0 | $0 |
| Median latency | 1.5244 s | 1.4221 s |

Output tokens fell 21.1%, but input tokens rose 4.5%. The score dropped,
so the change was reverted under the handout's acceptance rule. Latency
improvement alone cannot justify that score drop. No favorable reruns were
used to override the observed outcome.

## Part C: caching, skipped at student request

No paid OpenAI calls have run. The student superseded the earlier approval
with: “but skip any checks that cost money - since I don't have an API key”.
Neither the compatibility check nor the 70-trial comparison was started.
The unrun proposal remains saved for context; it grants no active permission.
The prompt order remains the HW8 order. No OpenAI score, cost, cached
fraction or before/after result is available. A missing measurement is not
an observed result of zero cached tokens.

Official prices checked October 31, 2026: $0.15 input, $0.075 cached input,
$0.60 output per million tokens. Sources:
[model pricing](https://developers.openai.com/api/docs/models/gpt-4o-mini)
and [caching guide](https://developers.openai.com/api/docs/guides/prompt-caching).
No cached fraction is claimed for an unrun OpenAI experiment.

## Part D: smaller-model cascade, rejected

Proxy: local Qwen3 0.6B. Oracle: saved frozen HW5 Llama 3.1 8B verdicts.
Both API fees are zero. Fewer parameters provide a resource-cost motivation,
but this differs from the handout's expected cheaper API model.

The 95% agreement requirement was recorded as an agent assumption before
proxy runs or calculations; it is not a student-confirmed assessment.
No tested threshold met it. The lowest threshold reaching the best observed
development agreement was **0.9**, frozen and committed before test calls.
It was checked as an already rejected candidate; no test retuning occurred.

| Metric | Development | Test |
| --- | ---: | ---: |
| Examples | 38 | 38 |
| Agreement with oracle | 71.05% | 50.00% |
| Oracle disagreements | 11 | 19 |
| Agreement with human labels | 63.16% | 73.68% |
| Proxy share | 57.89% (22/38) | 68.42% (26/38) |
| Cost per 1,000 verdicts, API fees only | $0 | $0 |

76 actual local proxy requests completed; no oracle reruns and no paid
requests. The proxy received only the frozen prompt and observed evidence,
plus a confidence instruction. It frequently expressed full confidence in
incorrect oracle comparisons. Invalid structured outputs would fall back;
none occurred. Self-reported confidence was not calibrated.

The student's HW5 assessment already restricts the oracle to suggestions
for human review. The cascade inherits that restriction; human agreement
does not make it ready for automatic CI or monitoring decisions.

## Part E: frontier so far

Regenerate: `uv run python profile/scripts/frontier.py`.
`profile/results/frontier.csv` contains the HW8 final and rejected Part B run.
HW8 final is on the frontier; concise replies are dominated because they
have a lower score at equal API cost. write_pass_5 and latency do not alter
the required score/cost dominance rule. Unrun Part C configurations have
no rows in the measured frontier.

Agent recommendation: retain the HW8 final agent and the existing human
review process. The student's final configuration decision is pending.

## Verification and remaining deliverables

- Offline: 23 focused authorization, tool, prompt and optimization tests
  passed; proxy parser validation passed; saved scores reproduced.
- Live local models: 35 agent development trials and 76 proxy requests.
- Paid models: zero.
- Evaluation cases, existing tests, frozen judges and `optimize/state/`
  match the preparation hashes; no HW8 held-out agent cases were reused.
- Skipped by student instruction: paid OpenAI compatibility and Part C
  caching comparison. This required handout measurement remains unverified.
- Remaining student deliverables: configuration assessment and continuous
  video of at most 5 minutes.
