# HW9 Part B: shorter replies

Prediction recorded before evaluation: ask for at most two concise sentences
after required tool execution. Retain the observed action status, necessary
next steps and policy citations. This should reduce output tokens and latency;
input tokens may rise because the instruction itself adds text.

Observed historical reply `9027cc4e0fc61543b0503fc723b1b0ca` repeated order
status, listed other information the user could check, and offered generic
help. The three largest saved requests also contain repeated conversation
and tool evidence; none of that evidence or authorization logic is removed.

Baseline: `development-final-ollama_chat_llama3.1:8b-20261031-164040.json`.
Model: `ollama_chat/llama3.1:8b`; 7 development cases, 5 trials each,
35 evaluated case runs, zero judge calls, zero paid API calls.

Keep only if cost or median latency falls and neither development score nor
write_pass_5 falls. Local API fees are already zero, so latency is the
applicable acceptance measure; token reductions alone do not establish savings.

Result: **reverted**, because the development score fell.

| Metric | HW8 final | Shorter replies |
| --- | ---: | ---: |
| score | 0.771429 | 0.742857 |
| write_pass_5 | 0.571429 | 0.571429 |
| input_tokens | 72875 | 76177 |
| output_tokens | 3942 | 3111 |
| cost_per_100_conversations_usd | 0.0 | 0.0 |
| median_latency_seconds | 1.5244 | 1.4221 |

The run used live local Ollama, not paid APIs. This is a small stochastic
comparison; a score drop is sufficient to reject under the handout rule.
No extra runs were used to search for a favorable outcome. The exact HW8
agent prompt has been restored; evaluation data and scorers were untouched.
