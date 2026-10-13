# agent-harness

A small agent harness with no framework, built to match the "Harness + LLM Ops" diagram. Every box in the diagram maps to one file you can read in a few minutes. The demo domain is a customer-success agent that looks up complaints in a CRM, books follow-up meetings and issues refunds, as in the video's running example.

## Diagram → code

| Diagram box | Where | Smallest working version chosen |
|---|---|---|
| System prompt | `prompts/system.v1.md` | Versioned file; the version is part of the release |
| Current chat history | `memory.py` `EpisodicMemory.history` | Last `history_turns` messages of this chat, replayed as plain text |
| User prompt → working memory / context RAM | `memory.py` `build_working_memory` | System prompt + matched skills + facts + past chats + history + prompt |
| Procedural memory (Skill.md) | `skills/*.md`, `memory.py` `ProceduralMemory` | Frontmatter `triggers`; a skill loads only when the request matches one |
| Semantic memory (vector store, durable facts) | `store.py` `facts`, `memory.py` `SemanticMemory` | Top-k by cosine, with a similarity floor so irrelevant facts stay out |
| Episodic memory (SQL + vectors) | `store.py` `episodes`, `memory.py` `EpisodicMemory.recall` | SQL for the last N chats + vector top-k for relevant older messages |
| Save the messages | `loop.py` `Agent.run` | Prompt and reply appended to `episodes` after every run |
| Only consolidate after N new chats → summarizer agent (cheaper model) → distill into facts | `consolidate.py` | Watermark per user; Haiku 5.5 extracts facts; a near-duplicate fact is replaced, not appended |
| LLM (Q&A agent) ↔ agentic tools | `loop.py`, `tools.py` | Manual tool loop on Claude Opus 5.5; tools run on an in-memory CRM/calendar/payments backend |
| End-loop guardrails | `loop.py` | `max_steps`, `max_cost_usd`, `ask_user` (asks instead of guessing), approval gate on refunds over $500, refusal |
| Trace (1 per run) / Observe | `tracing.py` | Langfuse trace per run: working-memory retrieval, each LLM call (tokens, cost), each tool call, guardrail hits |
| Eval (LLM-as-judge → scores) | `evals.py` | Code checks on backend state + Haiku judge (1–5); both written to the trace as Langfuse scores |
| Diagnose | `evals/results/<release>.json` + Langfuse + [RUNS.md](RUNS.md) | Failed checks, stop reason, tool calls and the judge's reason per case; RUNS.md logs each run and what was learned |
| Gate | `uv run python -m harness eval` / `uv run python -m harness tau2` exit code | Built-in set: check pass rate ≥ 80% and mean judge ≥ 3.5. τ²-bench: pass^1 ≥ `tau2_gate_min_pass` |
| Release (prompt version, model config, tool change, RAG top-k) | `release.json` | Everything a fix may change lives here; its hash (`release.tag`) is stamped on every trace |

Storage is SQLite and the embedder is a hashed bag-of-words, so everything runs offline. In production these become Postgres + pgvector and a real embedding model, behind the same interfaces (`Store`, `Embedder`).

## Run it

```bash
uv sync
uv run pytest -q                          # offline; a scripted fake model drives every path

cp .env.example .env                      # add ANTHROPIC_API_KEY (+ Langfuse keys for tracing); loaded automatically
uv run python -m harness chat --user op-1        # memory persists in harness.db across chats
uv run python -m harness eval                    # runs evals/dataset.jsonl; exit 1 = gate failed
uv run python -m harness consolidate --user op-1 # run the summarizer now instead of waiting for N chats
```

Example chat prompts: "Find complaints from the last 60 days that were never reimbursed and book follow-ups" (loop + skills), "Refund A-1004" (approval gate, $640), "Deal with the complaints" (should ask, not act).

## Benchmark: τ²-bench airline

`harness/bench/tau2.py` runs the harness on [τ²-bench](https://github.com/sierra-research/tau2-bench) as the agent under test. τ²-bench provides 50 airline tasks, the tools, the policy, an LLM-simulated customer and a grader. The grader checks the final database state, so "did it actually cancel, or correctly refuse to?" is checked in code. Airline is used rather than retail, where top models are near saturation.

```bash
# tau2 is installed by `uv sync`, but its tasks and DB aren't in the package:
# clone the repo and set TAU2_DATA_DIR in .env to its absolute data/ path.
git clone --depth 1 https://github.com/sierra-research/tau2-bench ../tau2-bench
uv run python -m harness tau2 --tasks 0,1,2   # a few tasks first: each costs real tokens (agent + simulated user)
uv run python -m harness tau2 --trials 4      # all 50 tasks x4 for pass^1..pass^4
```

- **Agent:** the release's agent model with the harness system prompt (`prompts/tau2.v1.md`) and the domain policy. The guardrails are the same: a step budget per customer turn and a cost budget, after which it hands off to a human instead of looping.
- **Simulated user:** `tau2_user_model` in `release.json` (default `anthropic/claude-sonnet-5-5`, via litellm). Published leaderboards use a different user model, so compare your own releases with each other, not with the leaderboard.
- **LLM Ops:** each task attempt is one Langfuse trace tagged `tau2`, `airline` and the release, scored `tau2_reward`. Results go to `evals/results/tau2-airline-<release>.json`, which is committed. The command exits 1 when pass^1 is under `tau2_gate_min_pass`.
- **Results so far:** release `v1-efe062d5` scored pass^1 **78%** (39/50) on airline for $16.47. See [RUNS.md](RUNS.md) for each run, the failures and how it compares with published scores.
- **Offline tests:** `tests/test_tau2.py` drives the real τ² environment and grader with a scripted model and a scripted customer. It covers task 0: refusing a disallowed cancellation scores 1, and cancelling anyway fails the DB check.

This benchmark is single-session, so it exercises the loop, tools, policy and guardrails, not long-term memory. For the memory layer, the next step is a multi-session benchmark (Mem2ActBench, or LongMemEval for pure recall). For retrieval, use τ³'s `banking_knowledge` domain. For the interview targets, swap the domain: CRMArena-Pro (GTM/sales) or MedAgentBench (healthcare).

## The LLM Ops loop, concretely

1. **Trace.** Every `agent.run` is one Langfuse trace tagged with the release (for example `v1-3fa2c91b`), user and chat.
2. **Eval.** `uv run python -m harness eval` runs the dataset, scores each trace (`checks_passed`, `judge_quality`) and writes `evals/results/<release>.json`. Commit the result and add an entry to [RUNS.md](RUNS.md).
3. **Diagnose.** Open a failing case's trace: was the right skill loaded, did retrieval bring in noise, which tool call went wrong, did a guardrail fire?
4. **Fix.** Cheap fixes first: edit the prompt (save it as `system.v2.md`), a skill, a tool description, or `release.json` (top-k, max steps, model). Code changes come last.
5. **Gate → Release.** Re-run the eval. The new release tag gets its own traces, so before and after are directly comparable in Langfuse. Ship only if the gate passes.

## Choices worth defending in an interview

- **No framework.** The loop is about 100 lines, so every guardrail is visible and testable. LangGraph or Pydantic AI would wrap the same parts.
- **Code checks before the judge.** Whether a meeting was booked or a refund issued is checked against backend state. The LLM judge only covers what code can't check.
- **Consolidation is gated by volume.** It reads every message since the watermark, so it runs on the cheap model and only every N chats.
- **Approval comes before the irreversible step.** A refund over the limit is never executed by the model. The run stops, and the operator re-runs it with approval.
- **Retrieval has a similarity floor.** Irrelevant memories are left out instead of padding the context.
