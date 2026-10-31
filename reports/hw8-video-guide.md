# HW8 video guide (at most five minutes)

Record one continuous screen video. Give your own interpretation of the
results and explain why you selected the final prompt.

1. **0:00–0:40 — Target.** Show `optimize/results/target.json`, the confirmed
   missing-handoff examples, ESC-3/RESP-6 and why a prompt could fix the behavior.
2. **0:40–1:20 — Preparation.** Show local model choices, fixed split, starting
   version and 14.3% baseline. Explain that cases/judges were preserved and
   every data-changing case received five fresh-world trials.
3. **1:20–2:30 — Experiments.** Show `manual.csv` and `improve-loop.jsonl`:
   prompt improvement, reverted tool/harness changes, and 140/150 search runs.
   Explain your selected candidate and the final 77.1% development rerun.
4. **2:30–3:30 — Test comparison.** Show `final_version.json`, the reviewed
   four-configuration plan, `frontier.csv` and `reports/hw8-frontier.svg`.
   Compare starting/final Llama: 33.3% to 93.3%. The final refund still failed
   once; all fees are zero and hardware/electricity are excluded.
5. **3:30–4:20 — Regenerate a number.** Run:
   `uv run python -m optimize.reproduce`. It recalculates the committed test
   scores and write_pass_5 from saved pass counts without running new models.
6. **4:20–5:00 — Your assessment.** Discuss the three-case sample, partial
   refund reliability, and the distinction between successful tool execution
   and correct wording/policy claims. Explain what additional evidence you
   would want before using the change more broadly.

The recording is the student's deliverable and remains pending until made.
Do not rerun test cases or change the frozen agent to improve these results.
