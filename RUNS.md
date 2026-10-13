# Runs

One entry per eval or benchmark run, newest first. Raw results are in `evals/results/`, and each attempt links to its Langfuse trace by `trace_id`.

| Date | Run | Release | Result | Cost |
|---|---|---|---|---|
| 2026-10-12 | τ²-bench airline, all 50 tasks, 1 trial | `v1-efe062d5` | pass^1 **78%** (39/50), gate passed | $16.47 |

## 2026-10-12: τ²-bench airline, full set

Result file: [`evals/results/tau2-airline-v1-efe062d5.json`](evals/results/tau2-airline-v1-efe062d5.json)

**Setup**

| | |
|---|---|
| Agent | `claude-opus-5-5`, effort `medium`, prompt `prompts/tau2.v1.md` + airline policy |
| Simulated customer | `anthropic/claude-sonnet-5-5` |
| τ²-bench | commit `4ce7c03` (includes the February 2026 task fixes) |
| Guardrails | `max_steps` 8 per customer turn, `max_cost_usd` $0.50 per task |
| Trials | 1 per task |
| Duration | about 31 minutes, sequential |

**Result:** 39 of 50 tasks passed, pass^1 78%, for $16.47 in agent cost (the simulated customer is billed separately). Tasks cost $0.31 at the median and $0.56 at most. Every conversation ended with the customer stopping. All 11 failures failed the database check, meaning the final bookings didn't match the expected state, and all 39 passes matched.

**Compared with published scores.** With one trial on 50 tasks, the uncertainty is about ±11 points, so this run is level with published results for the same model rather than ahead of them. The published boards also use a different customer model, and some predate the task fixes.

| Source | Model | Airline pass^1 |
|---|---|---|
| This run | Claude Opus 5.5 | 78% |
| [OpenRouter τ²-Bench Airline](https://openrouter.ai/benchmarks/tau2-bench-airline) (Oct 2026) | Claude Opus 5.5 | 75.8% ± 2.2 |
| Same board, top entry | Claude Fable 5 | 80.0% |
| [Amazon τ²-bench-verified](https://github.com/amazon-agi/tau2-bench-verified) | Claude Opus 4.5 | 74.4% |

**Failures.** The guardrail column is read from each task's Langfuse trace.

| Task | Cost | Guardrail fired | Cause |
|---|---|---|---|
| 14 | $0.51 | `max_cost` | Hit the cost cap and handed off before finishing |
| 23 | $0.53 | `max_cost` | Hit the cost cap and handed off before finishing |
| 33 | $0.51 | `max_cost` | Hit the cost cap and handed off before finishing |
| 35 | $0.50 | `max_cost` | Hit the cost cap and handed off before finishing |
| 7 | $0.43 | — | Wrong final database state |
| 25 | $0.19 | — | Wrong final database state |
| 29 | $0.26 | — | Wrong final database state |
| 31 | $0.43 | — | Wrong final database state |
| 32 | $0.36 | — | Wrong final database state |
| 39 | $0.33 | — | Wrong final database state |
| 44 | $0.54 | — | Wrong final database state; it went over $0.50 only on its last reply |

The cost cap fired on 6 tasks. Two of them (10 and 21) still passed because the agent had finished the required changes before the cap hit. The `max_steps` guardrail never fired.

**What this means**

- **The cost cap is the cheapest fix.** It caused 4 failures. If all 4 pass with a higher cap, pass^1 rises to 86% (43/50).
- **7 failures are real mistakes** in policy or reasoning. Their traces show what to change in `prompts/tau2.v1.md`.

**Next**

1. Raise `max_cost_usd` to 1.0 and rerun tasks 14, 23, 33 and 35 (about $3).
2. Read the traces for tasks 7, 25, 29, 31, 32, 39 and 44, group them by failure type, and fix the prompt.
3. Run `--trials 4` for a more reliable pass^1 and for pass^k.
