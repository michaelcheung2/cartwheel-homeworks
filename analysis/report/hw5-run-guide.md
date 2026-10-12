# HW5 runner and review guide

Main judge: local `ollama_chat/llama3.1:8b`, chosen by the student. The handout
requires `gpt-4o-mini`; this submission must disclose the departure. Llama
and Qwen3 8B are installed. The optional Qwen development comparison is
complete; results are in hw5-model-comparison.md.

## Saved preparation

106 confirmed labels retain all accepted evidence and source decisions.
After collapsing related records, 95 eligible conversations remain:
65 Pass and 30 Fail. Failure examples were deliberately enriched; this
dataset cannot estimate population prevalence.

| Split | Pass | Fail | Total |
| --- | ---: | ---: | ---: |
| Training | 13 | 6 | 19 |
| Development | 26 | 12 | 38 |
| Test | 26 | 12 | 38 |

The split uses seed 7 and 20/40/40 fractions. Fixed inputs contain original
trace IDs and observed messages through the selected reply, including
earlier session turns and actual tool/retrieval results. Labels, review notes
and scenario expectations are excluded. Input and split hashes detect changes.

Prompt v0 uses three training-only examples. The exact prompt is in
`analysis/prompts/unsupported_policy_claim-v0.txt`. The judge assesses only
the last assistant reply; earlier replies provide context.

## Development and interruptions

The registered judge ID is `unsupported_policy_claim-v0`. Continue an
interrupted run with:

```bash
uv run python -m analysis.run_judges --resume unsupported_policy_claim-v0 --split dev
```

Do not register v0 again, split again, or regenerate the fixed inputs.
Completed ten-record batches are cached. An unfinished batch can repeat
calls, but it does not become a completed prediction batch automatically.

Use the **HW5 judge** tab at <http://localhost:8020> to compare saved verdicts
and critiques with human labels. Filter for disagreements. Every disagreement
needs a human decision: judge wrong, label wrong, or boundary unclear, with
evidence. Selecting label wrong records the decision; label correction and
metric recalculation remain explicit follow-up work.

The runner uses the supplied `run_judge` and `judge_alignment` helpers. Its
live classifier runs the supplied DocETL map with explicit local routing,
temperature 0, maximum output 1,024 tokens, context 16,384, and one worker.
The map uses DocETL's structured JSON output mode. The initial tool-output
attempt failed before saving any predictions; the transport fix and resume
are recorded in hw5-execution-notes.json. The map helper gained optional
completion settings, output mode and a worker limit;
default behavior for other callers is preserved. There are no stubbed
predictions in the live judge path.

## Final test and recording

After reviewing development disagreements and at most two prompt revisions,
the student chooses the final judge. Record that explicit choice in
`analysis/state/hw5_final_decision.json` before freezing/testing. Do not
choose the prompt from test results. No numerical acceptance threshold is
required.

```bash
uv run python -m analysis.run_judges --test <chosen-judge-id>
```

If interrupted, resume the same ID with `--resume <chosen-judge-id> --split test`.
Freezing happens once. Recalculate saved test predictions on camera with:

```bash
uv run python -m analysis.run_judges --metrics unsupported_policy_claim-v2 --split test
```

Report TP, FN, TN, FP, TPR (agreement with human Pass), TNR (agreement with
human Fail), class counts and 95% Wilson intervals. The student decides
whether to use the judge and records the continuous video of at most five
minutes.

The selected v2 judge is already frozen and all 38 test predictions are
saved. Use the metrics command above for your recording; it runs offline
and makes no new model calls.

## Suggested continuous recording

1. Explain the unsupported-policy-claim boundary using hw5-summary.md.
2. Show support-0090 in hw5-v0-disagreement-review.md: the critique invented
   a refund restriction absent from the reply. Explain retaining human Pass
   and requiring quoted evidence in the first revision.
3. Show the development table and explain stopping after two revisions.
4. Run the exact metrics command above live. Explain that Pass is positive:
   TPR 42.31% concerns passing replies; TNR 83.33% concerns failures. Show
   both 95% intervals and the 15 false alarms / two missed failures.
5. Give your own decision about using the judge. Keep the entire recording
   within five minutes in one take.

The student has confirmed the assessment: no automatic decisions; use only
to suggest cases for human review. Explain that position in your own words
in the recording. The recording remains pending.
