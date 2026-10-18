# HW6 capability trial-count comparison

Case `e-005` requests investigation of a disputed charge and requires a
successful human ticket. Its accepted baseline was 0/5.

[The separate 15-trial run](https://github.com/michaelcheung2/cartwheel-homeworks/actions/runs/39171101278)
used the original prompt on commit `cf132d7` and the same pinned local
`ollama_chat/llama3.1:8b` model. All 15 trials reached the verifier, with
no trial exceptions. None passed. These are 15 new observations, rather
than the original five baseline trials plus ten additions.

| Observed runs | Passes | pass@1 | pass@3 | pass@5 |
| --- | ---: | ---: | ---: | ---: |
| 5 | 0 | 0.0 | 0.0 | 0.0 |
| 10 | 0 | 0.0 | 0.0 | 0.0 |
| 15 | 0 | 0.0 | 0.0 | 0.0 |

At n=15, pass@10 and pass@15 are also zero. At a fixed n the estimates
do not decrease as k grows. At a fixed k they did not move as observations
increased, because no subset contains a success. This records stable zero
estimates in this sample; it does not prove the agent can never succeed.

The supplied analysis command reproduced the downloaded analysis exactly
using the saved rewards, without model calls. Trial names and order are in
`eval_results/e-005-15.json`; the source run, usage, and observed tool names
are in `eval_results/hw6-capability-evidence.json`.

Harbor 0.23 saves per-trial files. The adapter preserves its raw summary and
indexes observed trials by started_at, then trial name, in result.json. The
analysis records that ordering provenance explicitly.
