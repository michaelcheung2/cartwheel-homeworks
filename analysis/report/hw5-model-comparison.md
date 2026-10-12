# HW5 optional model comparison

This compares local Llama 3.1 8B and Qwen3 8B as judges of unsupported policy
claims. It is an additional development experiment, not a second calibrated
submission judge.

## Controlled inputs

- Exact prompt: unsupported_policy_claim-v2.txt, unchanged after freezing.
- Same 38 development records: 26 human Pass and 12 human Fail.
- Same fixed evidence export and human labels; no test records for Qwen.
- DocETL structured JSON output, temperature 0, 1,024 maximum output tokens,
  16,384 context, one worker, local Ollama endpoint.
- Llama digest prefix 46e0c10c039e; Qwen digest prefix 500a1f067a9f.
- Both installations are Q4_K_M. Llama is 8.0B parameters; Qwen is 8.2B.
- Qwen additionally uses reasoning_effort="none" (Ollama think=false).
  This compares Qwen without its thinking mode.

## Observed development results

Pass is the positive class. FN denotes a false alarm; FP denotes a missed
failure.

| Model | TP | FN | TN | FP | TPR | 95% Wilson interval | TNR | 95% Wilson interval |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| Llama 3.1 8B, v2 | 14 | 12 | 11 | 1 | 53.85% | 35.46–71.24% | 91.67% | 64.61–98.51% |
| Qwen3 8B, same prompt | 21 | 5 | 9 | 3 | 80.77% | 62.12–91.49% | 75.00% | 46.77–91.11% |

Qwen raised fewer false alarms and missed more failures. The uncertainty
intervals overlap, and the data are a small curated sample enriched for
failures. These observations do not establish a general model ranking or
population failure prevalence. They also do not justify substituting Qwen
for the selected Llama judge after seeing Llama test results.

## Records and reproducibility

Llama metrics: analysis/report/dev-unsupported_policy_claim-v2.json.
Qwen metrics: analysis/report/hw5-qwen-development-comparison.json.
Qwen predictions/critiques: analysis/state/model_comparison/qwen3_8b/judges/.
The comparison's internal version ID is v0 within that separate directory;
its prompt is exactly the main judge's v2, not a fourth prompt revision.
All 38 Qwen critiques are saved. Qwen disagreements have not received an
additional student review and are not new human labels.

Resuming the comparison reuses its registration and completed predictions:

```bash
uv run python -m analysis.run_judges --compare unsupported_policy_claim-v2
```

All model calls in both experiments were live local calls with no paid API
credits. Metric calculations and integrity checks were offline.
