# HW5: unsupported policy claim judge

## Scope and human labels

The judge checks whether the selected final reply states a platform/store
policy rule or service promise contradicted by applicable policy or
unsupported by retrieved policy and actual tool results. Earlier turns
provide context. A trace can Pass this criterion while failing factual
grounding, citation, tool execution or human-handoff requirements.

The student confirmed the HW4-derived definition and six additional Fail
labels. HW5 preserves 106 confirmed labels and their evidence; 95 independent
representatives enter evaluation (65 Pass, 30 Fail). Eleven related labels
are excluded from the split and retained in history. Variants of the same
documented data-quality case and same-order/same-intent requests are grouped.
Confirmed failures are deliberately enriched, so these data do not measure
population failure prevalence.

HW5 labels use **1=Pass, 0=Fail**; original HW4 failure flags remain unchanged.
The student clarified that generic advice to verify a potentially changing
policy is not itself a concrete new policy rule or service promise.

## Inputs, model and split

Fixed inputs contain original trace IDs, observed user/assistant messages,
relevant earlier turns, and full paired tool/retrieval results through the
selected reply. Labels, human review notes, scenario expectations and other
extra metadata are excluded. Input/split hashes protect the saved export.

| Split | Pass | Fail | Total |
| --- | ---: | ---: | ---: |
| Training | 13 | 6 | 19 |
| Development | 26 | 12 | 38 |
| Test | 26 | 12 | 38 |

The one-time split uses 20/40/40 fractions and seed 7. All prompt examples
come from training. Development and test examples were never copied into
prompts.

The primary judge is local **Llama 3.1 8B** through Ollama, explicitly chosen
by the student. This is a departure from the handout's required
`gpt-4o-mini`. Execution uses DocETL through the Cartwheel helpers, structured
JSON output, temperature 0, context 16,384, maximum output 1,024 tokens, and
one worker. No paid provider model was used. Installed model digest prefix:
`46e0c10c039e`; quantization: Q4_K_M.

## Development and revisions

| Version | TP | FN | TN | FP | TPR | 95% Wilson interval | TNR | 95% Wilson interval |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| v0 | 12 | 14 | 11 | 1 | 46.15% | 28.76–64.54% | 91.67% | 64.61–98.51% |
| v1 | 12 | 14 | 10 | 2 | 46.15% | 28.76–64.54% | 83.33% | 55.20–95.30% |
| v2 | 14 | 12 | 11 | 1 | 53.85% | 35.46–71.24% | 91.67% | 64.61–98.51% |

All 44 version-specific development disagreements (15 + 16 + 13) received
explicit student-confirmed decisions. The underlying human labels stayed
unchanged. Original AI recommendations and their acceptance provenance are
retained beside observed verdicts and critiques.

An illustrative disagreement is `support-0090`, trace
`26288d78507c65183456edb32b03f637`: the assistant proposed looking up a
cancellation policy, but v0's critique attributed a refund-eligibility
prerequisite to it. That prerequisite was absent from the selected reply.
The student retained Pass for this policy mode. The unexecuted lookup is a
different failure. Revision 1 required an actual quoted claim and separated
policy judging from overall task success. It did not improve the aggregate
rates; its result is preserved rather than reported as a successful fix.

Revision 2 shortened the rubric, added relevant SPEC refusal rules, and
replaced examples with two Pass and two Fail cases from training. It had the
best observed development TPR and tied the best TNR. Confidence intervals
overlap, so this is not a demonstrated statistically significant improvement.

The student selected v2 before seeing test predictions. Revisions stopped
at the handout's two-revision limit. No numerical acceptance target was used.

## Frozen held-out test

Judge: `unsupported_policy_claim-v2`. Frozen once, then evaluated on all 38
held-out records. No prompt changes followed the test.

| | Human Pass | Human Fail |
| --- | ---: | ---: |
| Judge Pass | TP = 11 | FP = 2 |
| Judge Fail | FN = 15 | TN = 10 |

- **TPR:** 11/26 = 42.31%; 95% Wilson interval **25.54–61.05%**.
- **TNR:** 10/12 = 83.33%; 95% Wilson interval **55.20–95.30%**.

The judge flagged 15 passing records and missed two failures. False alarms
are substantial, and 12 human Fail cases leave wide uncertainty about failure
detection. These measurements support caution about automatic decisions;
they do not invalidate completion of the homework experiment.

**Student's assessment:** Do not use the judge for automatic decisions
because of its false alarms. Use it only to suggest cases for human review,
with a person checking every flagged reply. The student explicitly accepted
both conclusions after seeing the test results.

## Checks and submission

27 focused offline tests pass, covering evidence boundaries, Pass-positive
metrics, cache/resume behavior, fixed-input protection, test locking, human
review gates and comparison-state isolation. QuickJS syntax checking passed.
The local review API exposes development results beside human labels;
test predictions are excluded from that interface. Actual visual browser
verification has not been performed for HW5.

Judge verdicts and critiques came from live local model calls. Statistics
and integrity checks run offline. The initial DocETL tool-output transport
failed before any prediction batch was saved; structured JSON output fixed
the transport, and the same judge ID resumed. No missing or malformed output
was converted into a passing prediction. Saved test metrics were recalculated
from cached predictions without another model call.

## Optional Qwen comparison

Both models used the exact frozen v2 prompt and the same 38 development
records (26 Pass, 12 Fail). Qwen ran separately after the Llama final test.

| Model | False alarms | Missed failures | TPR (95% Wilson interval) | TNR (95% Wilson interval) |
| --- | ---: | ---: | --- | --- |
| Llama 3.1 8B | 12 | 1 | 53.85% (35.46–71.24%) | 91.67% (64.61–98.51%) |
| Qwen3 8B | 5 | 3 | 80.77% (62.12–91.49%) | 75.00% (46.77–91.11%) |

Qwen produced fewer false alarms while missing more failures. This small
development comparison does not establish which model is generally better.
Qwen's thinking mode was disabled; execution settings and saved critiques
are documented in hw5-model-comparison.md. Qwen was not tested on held-out
records, and it does not replace the student's frozen Llama judge.

The student's continuous screen recording (at most five minutes) remains
pending. Required technical files and video guidance are listed in
hw5-progress.md and hw5-run-guide.md. HW5 is not called complete while the
student's recording remains pending.
