# HW3 video guide (student recording pending)

The files and technical checks are ready. Record your own continuous screen video of no more than five minutes. No video or final performance assessment has been generated on your behalf.

## Suggested sequence

### 0:00–1:15 — Show one confirmed pilot failure

Open `scenarios/pilot_scenarios.jsonl`, `scenarios/pilot_review.jsonl`, and this [pilot-0007 trace](http://localhost:3000/project/cartwheel-dev/traces/a3b1657998257c2d41993d5e9d68763d).

- The shopper asks to cancel order 10.
- The observed `get_order` result says `status: placed` and `shipped_at: null`.
- The expected behavior permits cancellation before shipment (`cw-cancellations`).
- Only `get_order` actually ran; no `cancel_order` ran. The displayed JSON in the assistant reply is text, not an executed tool.
- Your confirmed review marks this valid scenario as a failure.

The historical post-pilot state is saved in `reports/hw3-pilot-state.json`; the final run used a fresh seed, so use the recorded tool result and saved snapshot for this historical evidence.

### 1:15–2:15 — Show the final scenario you revised

Open `reports/hw3-final-review.md` and the `support-0169` record in `scenarios/support_review.jsonl` and `scenarios/support_scenarios.jsonl`.

- Original opening: “I need to update the merchant business address on my account.”
- Approved opening: “Please change the mailing address on my account.”
- Reason: the authenticated caller is a shopper; the revision removes ambiguity about a merchant business account.
- The followup and human-escalation expectation remain as reviewed.

### 2:15–3:45 — Show a complete final trace

Open the [first turn of revised support-0169](http://localhost:3000/project/cartwheel-dev/traces/ecc32ba020398fbe6dbb8b22fa3bf2cf). Show:

- `cartwheel.scenario_id = support-0169` in metadata, and `cartwheel_scenario_id` in the exported JSON.
- The actual revised user message and the agent reply.
- Model `ollama_chat/llama3.1:8b`, captured messages, and measured usage.
- The executed `escalate_to_human` tool with its inputs and returned ticket.

Additional verified examples: [ordinary multi-turn support-0001](http://localhost:3000/project/cartwheel-dev/traces/9027cc4e0fc61543b0503fc723b1b0ca) and [challenge multi-turn support-0185](http://localhost:3000/project/cartwheel-dev/traces/1e79fb44ed721a3f30934500464e10ee).

### 3:45–4:30 — Regenerate the final ID count

Run from the repository root:

```bash
jq '[.traces[].cartwheel_scenario_id] | unique | length' traces/support_traces.json
```

Observed output:

```text
250
```

Also show the completed-run count if useful:

```bash
jq -s 'group_by(.status) | map({status: .[0].status, count: length})' scenarios/final-results.jsonl
```

Observed: one `completed` group with count 250.

## Verified dataset facts

| Group | Scenarios completed | Exported traces |
| --- | ---: | ---: |
| Coverage | 175 | 232 |
| Challenge | 75 | 112 |
| Total | 250 | 344 |

There are 344 traces because the scripted conversations contain 344 user turns. The export contains exactly 250 unique final scenario IDs. All trace conversations were compared with saved results; roles/user IDs, model identity/usage, and tool outputs/errors were verified. Completion counts describe execution, not correctness.

The smoke report covers the entire local project, including earlier HW2 and pilot traces. `reports/hw3-final-summary.json` summarizes only the final scenario IDs. Model/tool errors inside completed runs are retained for later analysis; no final failure labels or taxonomy were created.
