# HW8 candidate selection (pre-test record)

Target chosen by the student: missing required human handoff (ESC-3/RESP-6).
Development has seven fixed cases; every case runs five times. No test-set
case has been executed. All experiments use local Llama 3.1 8B and zero model
API fees. Hardware/electricity cost is excluded.

| Configuration | Development score | write_pass_5 | Disposition |
|---|---:|---:|---|
| Starting agent | 14.3% | 14.3% | Baseline |
| Explicit dispute handoff + actual tool execution | 57.1%, repeated 57.1% | 57.1% | Kept |
| Expanded handoff tool description | 54.3% | 42.9% | Reverted |
| Temperature zero | 57.1% | 57.1% | Reverted; no accuracy gain |
| Explicit refund invocation | 68.6%, repeated 65.7% | 57.1% | Kept |
| Tools before narration | 77.1% | 57.1% | Proposed final candidate |

## Recommendation

Select **tools before narration**, commit `8158c28`. This prompt combines
the reliable handoff fix with explicit approved refund invocation and tool
calls before prose. All four handoff cases passed 5/5. Refund cases passed
3/5, 0/5 and 4/5, so no refund case passed all five runs. Permission checks,
refund thresholds, approval handling and kill switches are unchanged.

The latest score gain has not been repeated. Search used 140/150 runs; the
remaining ten cannot cover a complete 35-run batch. The required final
35-run development evaluation will follow the student's selection, before
saving the final version and running the held-out comparison. A small
seven-case experiment does not establish general performance.

The alternatives are the repeated prompt-only handoff candidate `8d79474`
or the repeated refund-invocation candidate `0b5407a`. All address the target;
the latest candidate has the highest observed development score.

## Next steps after selection

Apply and commit the selected agent, run `optimize.runner --split development
--candidate final`, then save and commit `final_version.json`. Review the four
commit/model mappings and run the fixed test batch once. Models remain
Qwen3 8B, Qwen3 0.6B and Llama 3.1 8B; only the fourth configuration uses the
selected improved agent. No candidate changes follow test results.

Detailed dated results, every attempt/decision, source hashes, token usage,
and exceptions are in `hw8-candidate-review.json`, `optimize/results/manual.csv`
and `optimize/results/improve-loop.jsonl`. Superseded preliminary evidence and
one interrupted attempt are recorded separately. Student final selection
and the <=5-minute video remain pending.

Final selection and testing are now complete. This document preserves the
pre-test recommendation; see `hw8-summary.md` for observed final results.
