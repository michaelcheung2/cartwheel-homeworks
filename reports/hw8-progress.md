# HW8 progress

## Preparation and starting baseline complete

Current assignment: `homework/module-5/hw8.md`, accuracy improvement and
Pareto frontier. The checkout contained older HW9 optimization mechanics
and outdated HW8 safety comments. Imported the current upstream handout
and optimization commands without changing the agent or evaluation rules.

The ten existing HW6 cases (two regression, eight capability) satisfy the
minimum. Three installed local models each finished the pre-split model
check: Qwen3 8B passed e-001; Qwen3 0.6B and Llama 3.1 8B completed but
failed its checks. Llama remains the development model. Local model API
fees are zero; electricity/hardware costs are excluded. Resource comparisons
must also show tokens and latency, because the API-cost axis is flat.

The fixed split contains seven development cases and three test cases.
The search budget is 150 runs, with zero used. Preparation and starting
version are committed. No test-set execution has occurred.

A compatibility correction makes the custom HW6 `escalation_created`
check count as an expected write, requiring five trials. The preliminary
19-trial result remains saved and is superseded; one uncommitted attempt
was interrupted without a saved result. The frozen split was preserved.
No agent, case, test, human label, or frozen judge was changed.

The committed starting agent was then evaluated on 35 development trials
(five per case): mean score **0.142857**, `write_pass_5` **0.142857**,
API cost per 100 conversations **$0**, median latency **1.4593 seconds**.
All observed replies and failed checks are in the dated development result.
The exact commit/prompt/split/model selection is locked in
`optimize/state/starting_version.json`.

## Verification

- Seven existing optimization unit tests passed offline.
- Protected agent/case/test/judge file hashes match the pre-preparation
  manifest. Grader hashes exclude generated Python bytecode.
- Model checks and baseline used live local Ollama. No paid model API calls
  and no judge calls were used. Partial/interrupted attempts are documented;
  no missing result was invented.

## Required student choices and remaining work

The handout reserves the target failure mode and final candidate selection
for the student. Asked which mode to target: missing required human handoff
(observed review sample fraction 10%) or missed refund approval (4%). These
are deliberately selected sample frequencies, not population prevalence.
Higher-frequency policy/citation modes are not scored by the existing HW6
cases. The source taxonomy and labels remain unchanged.

After the target is chosen: save its three trace examples, test one manual
change at each layer on development only, run the supplied improve loop
within the 150-run budget, and present candidates for final selection.
Save the selected final configuration before the one test batch. Then
create the four-configuration frontier and prepare the recording guide.
The student's final selection and <=5-minute video remain pending.
