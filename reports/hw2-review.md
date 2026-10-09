# HW2 progress and recording reference

The code, offline checks, five complete local-model traces, and controlled prompt
comparison are complete. Your explanation of the selected traces and your video
remain pending. No response-quality labels or student assessments were assigned.

## Deliverables

- [x] `observability/instrument.py`: tool identity and permission attributes;
  compatibility adapter for measured LiteLLM generation outputs and usage.
- [x] `server/app.py`: authenticated session creation and traced messages.
- [x] `tests/test_observability.py`: required authentication tests, plus generation
  output, token-usage, and content-capture regression checks.
- [x] `hw2-traces.json`: exactly two observed trace records.
- [x] Five requests from `hw1-session.jsonl`, using the matching authenticated users.
- [x] Root messages, model messages and token counts, tool arguments and results,
  trace relationships, and application attributes verified through Langfuse's API.
- [x] Controlled prompt comparison; original `agent/agent.py` restored byte for byte.
- [x] Span count regenerated: six spans for each selected trace.
- [ ] Your review and explanation of the selected traces.
- [ ] Your continuous screen video, at most five minutes.

The supplemental `reports/hw2-evidence.json` records the observed evidence,
including the five complete traces, comparison conditions, and selected span data.

## Selected traces

Sign in at <http://localhost:3000> as `student@example.com` with the course password
`cartwheel-dev-pass`. Choose **Cartwheel Course → Cartwheel Dev**.

| Trace | Authenticated caller | Tool | Recorded result |
| --- | --- | --- | --- |
| [Shopper order lookup](http://localhost:3000/project/cartwheel-dev/traces/9282d8a72a3b8fa73cd5d4d212c61219) | shopper `1` | `get_order(4127)` | Authorized; order status `delivered` |
| [Merchant order lookup](http://localhost:3000/project/cartwheel-dev/traces/7edeb499cf57ecb7a2c891ab136f860a) | merchant `9002`, store `2` | `get_order(4127)` | `permission_denied` |

Both requests finished with HTTP 200. A permission denial is a structured tool
result within a completed request; it does not mean the server crashed.

Each selected trace contains this observed tree:

```text
cartwheel.session_message
└── Agent Workflow
    └── cartwheel-support.agent
        ├── openai.response  (first Ollama model call; selects get_order)
        ├── get_order       (arguments and structured result)
        └── openai.response  (second Ollama model call; final reply)
```

The integration's model span name remains `openai.response`; the recorded model
is `ollama_chat/llama3.1:8b` and its provider attribute is `ollama`.

The shopper tool returned order `4127`, store `1`, total `$84`, status `delivered`,
delivery date `2026-06-19`, and `refund_eligible: true`. Its permission attribute is
false and no denial reason is recorded. The root reply reports the delivered status.

The merchant tool returned `ok: false`, `error: permission_denied`, and reason
`role 'merchant' (user 9002) may not view order #4127`. Its permission attribute is
true, with the same reason. The root reply is:
“I cannot show you order #4127. Is there anything else I can help you with?”

| Selected trace | Model call | Input tokens | Output tokens |
| --- | --- | ---: | ---: |
| Shopper | First | 983 | 19 |
| Shopper | Second | 546 | 59 |
| Merchant | First | 981 | 19 |
| Merchant | Second | 469 | 20 |

These are recorded measurements from the completed Ollama calls.

## Concepts to explain in your own words

A **trace** connects all operations for one request. A **span** records one
operation, with its timing and parent relationship. **Attributes** are named values
attached to spans. The workflow and agent spans group operations; they are not
additional model calls.

Standard `gen_ai.*` attributes describe AI operations: model identity, messages,
tool calls, and token usage. Application `cartwheel.*` attributes describe the
verified caller, permission decision, prompt version, and scenario. Both namespaces
appear on the same tool span. Langfuse displays captured message attributes in
its input/output fields and stores the other attributes in metadata.

`create_session` loads the user from the database, rejects a claimed role mismatch,
constructs an `AuthContext`, stores it with conversation history, and signs a token.
`post_message` authorizes that token and uses the stored context when running the
agent. A chat message claiming a different role cannot change that context.

## Controlled prompt comparison

| Prompt | Recorded hash | Trace |
| --- | --- | --- |
| Current HW1 revision | `93d784362dc4` | [Current](http://localhost:3000/project/cartwheel-dev/traces/9282d8a72a3b8fa73cd5d4d212c61219) |
| Pre-revision HW1 template | `d108f6949e5e` | [Previous](http://localhost:3000/project/cartwheel-dev/traces/a6b8a11b11f838adb1d6fd00fc109bec) |

Both runs used “What's the status of my order 4127?”, shopper `1`,
`ollama_chat/llama3.1:8b`, and new sessions with empty history. The database SHA-256
matched before and after both runs. The earlier template came from
`git show c91415c^:agent/agent.py`. Only the template was temporarily replaced;
the saved original file was restored and the server restarted afterward.

The hash uses the system prompt template before injecting user identity. It lets
later analysis group traces by instruction version. Different hashes establish
that the template changed; this comparison does not establish which prompt is better.

## Checks and reproducible commands

All tests ran offline using temporary data and simulated model behavior.
Langfuse inspection and the prompt comparison used live local Ollama inference.

- Supplied HW2 contract: **1 passed** with `--runxfail`.
- `tests/test_observability.py`: **4 passed**.
- Complete suite: **157 passed, 4 skipped, 18 expected failures, 9 unexpected passes**.
  The expected failures are unfinished homework placeholders. Unexpected passes
  are implemented functions whose tests retain the starter's expected-failure marker.
- `git diff --check`: passed.

One test-client dependency deprecation warning remains; it did not affect checks.
The launcher supplies `OTEL_SDK_DISABLED=true`; removing it for these commands
enables span recording. The explicit judge trace source keeps the Module 2 test
on its supplied demonstration data. These settings do not modify `.env`.

```bash
env -u OTEL_SDK_DISABLED uv run pytest --runxfail tests/test_hw_holes.py -k hw2
env -u OTEL_SDK_DISABLED uv run pytest tests/test_observability.py
env -u OTEL_SDK_DISABLED \
  CARTWHEEL_JUDGE_TRACE_SOURCE=analysis/state/store_traces.json uv run pytest
```

For the video's authentication check:

```bash
env -u OTEL_SDK_DISABLED uv run pytest -q tests/test_observability.py \
  -k token_cannot_authorize_another_session
```

Regenerate the span count from Langfuse during the video:

```bash
env -u OTEL_SDK_DISABLED uv run python - <<'PY'
import json
from pathlib import Path
from observability.instrument import load_env
from langfuse import Langfuse
load_env()
selected = json.loads(Path("hw2-traces.json").read_text())[0]
trace = Langfuse().api.trace.get(selected["trace_id"])
print(f"{trace.id}: {len(trace.observations)} spans")
PY
```

The original command regenerated **6 spans** for both selected traces.

Docker, Langfuse, Ollama, and the restored server were left running. If the agent
server needs restarting, use:

```bash
env -u OTEL_SDK_DISABLED -u OPENAI_API_KEY \
  uv run uvicorn server.app:app --port 8010
```

Removing the inherited API key lets the existing `.env` settings load correctly.
The saved model setting remains `ollama_chat/llama3.1:8b`.

## Video checklist

Record one continuous video of at most five minutes:

1. Run one authentication test.
2. Open both selected traces and follow each from root to final response.
3. Explain how the server established the authenticated identities.
4. Explain each tool's arguments and returned result.
5. Show both controlled-comparison prompt hashes.
6. Regenerate the span count for one selected trace.

Use the observations above as a reference; your explanation and assessment remain yours.
