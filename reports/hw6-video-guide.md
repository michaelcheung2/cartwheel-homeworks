# HW6 recording guide

The student records one continuous video of no more than five minutes.
Use the observed evidence and give your own assessment.

## Suggested screen sequence

1. **0:00–0:45:** Show `eval_cases/cases.jsonl`: 10 cases, four refund-approval
   cases and six human-handoff cases. The source HW4 conversations and
   confirmed labels are in `eval_cases/hw6-provenance.json`.
2. **0:45–1:30:** Show the saved baseline results in
   `eval_results/hw6-baseline.json`. Explain why e-005 (0/5) is capability
   and e-010 (5/5) is regression. These classifications were accepted before
   the later experiments.
3. **1:30–2:15:** Show `tests/eval/passk.py`. Explain:
   - pass@k = `1 - C(n-c, k) / C(n, k)`: at least one success in k attempts.
   - pass^k = `C(c, k) / C(n, k)`: all k attempts succeed.
   - In the intentional run, e-010's 4/5 gives pass@5 = 1.0 but
     pass^5 = 0.0, so the reliability gate blocks.
   - A regression blocks CI on any failure; a capability reports its results
     without blocking. Baseline 5/5 does not guarantee future reliability.
4. **2:15–3:30:** Open the two observed Actions URLs in `ci-runs.json`, from
   the same PR. Show the selected regression case reaching the verifier,
   the temporary prompt change, and the second run after reverting it.
   E-010 passed 4/5 with the temporary instruction and blocked CI, then
   passed 5/5 after the revert. Mention that the initially intended e-009
   stayed 5/5; the observed failure was e-010. Show the actual failed trial
   and its empty tool-call list.
5. **3:30–4:45:** Show `eval_results/e-005-15.json`. Compare pass@1, pass@3,
   and pass@5 after 5, 10, and 15 observed runs. Explain whether the estimates
   moved, and what this sample does and does not tell you.
6. **4:45–5:00:** Give your own short assessment of the evaluation setup.

## Evidence and limitations

- All model trials use the pinned local Llama 3.1 8B model, through Ollama
  on GitHub's runners. Code checks make no LLM judge calls.
- The baseline workflow's initial reporting error did not invalidate its
  50 verifier rewards. The corrected reader used saved trial files; agents
  were not rerun.
- Harbor 0.23 stores separate trial files. The reporting adapter preserves
  the raw summary and indexes trial records in recorded start-time order.
- API keys, local environment files, and generated task directories are not
  presentation or submission artifacts.
- The recording and your final assessment remain your work.
