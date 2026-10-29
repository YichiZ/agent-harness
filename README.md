# agent-harness

A small agent with memory and no framework: an agent loop plus the four memories from the "Harness + LLM Ops" diagram, in three files. `agent.py` is the config, model client and loop; `memory.py` is storage, embeddings, the four memories and consolidation; `tools.py` is the demo domain, a customer-success agent that looks up complaints in a CRM, books follow-up meetings and issues refunds.

## Agent + memory → code

| Part | Where | Smallest working version chosen |
|---|---|---|
| System prompt | `prompts/system.v1.md` | Versioned file, picked by `prompt_version` (and `prompts_dir`) in `release.json` |
| Current chat history | `memory.py` `EpisodicMemory.history` | Last `history_turns` messages of this chat, replayed as plain text |
| User prompt → working memory / context RAM | `memory.py` `build_working_memory` | System prompt + matched skills + facts + past chats + history + prompt |
| Procedural memory (Skill.md) | `skills/*.md`, `memory.py` `ProceduralMemory` | Frontmatter `triggers`; a skill loads only when the request matches one |
| Semantic memory (vector store, durable facts) | `memory.py` `facts` table, `SemanticMemory` | Top-k by cosine, with a similarity floor so irrelevant facts stay out |
| Episodic memory (SQL + vectors) | `memory.py` `episodes` table, `EpisodicMemory.recall` | SQL for the last N chats + vector top-k for relevant older messages |
| Save the messages | `agent.py` `Agent.run` | Prompt and reply appended to `episodes` after every run |
| Consolidate after N new chats → summarizer (cheaper model) → facts | `memory.py` `Consolidator`, `prompts/summarizer.v1.md` | Watermark per user; Haiku 5.5 extracts facts; a near-duplicate fact is replaced, not appended |
| LLM (Q&A agent) ↔ agentic tools | `agent.py`, `tools.py` | Manual tool loop on Claude Opus 5.5; tools run on an in-memory CRM/calendar/payments backend |
| End-loop guardrails | `agent.py` | `max_steps`, `max_cost_usd`, `ask_user` (asks instead of guessing), approval gate on refunds over $500, refusal |

Storage is SQLite and the embedder is a hashed bag-of-words (`memory.py` `HashingEmbedder`), so everything runs offline. In production these become Postgres + pgvector and a real embedding model, behind the same interfaces (`Store`, `Embedder`).

## Run it

```bash
uv sync
uv run pytest -q                          # offline; a scripted fake model drives every path

cp .env.example .env                      # add ANTHROPIC_API_KEY; loaded automatically
uv run python -m harness chat --user op-1        # memory persists in harness.db across chats
uv run python -m harness consolidate --user op-1 # run the summarizer now instead of waiting for N chats
```

Example chat prompts: "Find complaints from the last 60 days that were never reimbursed and book follow-ups" (loop + skills), "Refund A-1004" (approval gate, $640), "Deal with the complaints" (should ask, not act).

## Run on YC-Bench

[YC-Bench](https://github.com/collinear-ai/yc-bench) puts the agent in charge of a simulated startup for a year: accept tasks from clients, assign employees, avoid bankruptcy. The runner seeds the world with YC-Bench's own code and gives the agent one tool, `run_command`, for its `yc-bench` CLI.

The system prompt (`bench/yc-bench/prompts/system.v4.md`) is the stock YC-Bench agent prompt ([arXiv 2604.01212](https://arxiv.org/abs/2604.01212), Appendix C; `yc_bench/agent/prompt.py` in upstream `collinear-ai/yc-bench` at `97ca2b8`), with memory. The harness's memory replaces YC-Bench's 20-turn history window and scratchpad, so the scratchpad instructions and commands are gone and the agent ends each checkpoint with a short note, which becomes episodic memory. Because the runner owns `sim resume`, that step and command are gone too. Everything else (workflow, commands, key mechanics, the client warning) is stock wording. The checkpoint messages carry the same idle and undispatched warnings as stock's per-turn context. v3 also told the agent to check deadline feasibility before accepting and explained cents in a Money section; v4 drops both.

```bash
uv run python bench/yc-bench/run.py --fake --max-checkpoints 3                 # offline, scripted model, no API cost
uv run python bench/yc-bench/run.py --seed 1 --max-checkpoints 10 --max-cost 5 # real model, short run
uv run python bench/yc-bench/run.py --seed 1                                   # full horizon, capped at $30
```

Each checkpoint is one harness chat (`cp-001`, `cp-002`, ...) for the same user (`ycbench-seed<N>`). The prompt is the company state plus the events since the last checkpoint; the agent sets up work, then replies with a short note of what it did and learned. The runner then calls `yc-bench sim resume` to advance time, so the agent never does. Those notes are episodic memory, recalled at later checkpoints, and after every checkpoint the summarizer (`bench/yc-bench/prompts/summarizer.v4.md`) distills them into lasting facts about this company, such as which clients have failed tasks and which employees are fast in which domain. That replaces YC-Bench's scratchpad. Settings are in `bench/yc-bench/release.json` (its `prompts_dir` points at `bench/yc-bench/prompts/`); each run writes to `bench/yc-bench/runs/<timestamp>-seed<N>/`: `run.md` (a readable log; `--render <run_dir>` rebuilds it), `checkpoints/cp-NNN.json` (prompt, every command and result, note, costs, the memory the agent saw), `system_prompt.md`, `summary.json`, and the `world.db` and `memory.db` databases. Logged runs are in [`bench/yc-bench/results/`](bench/yc-bench/results/). Known memory problems and planned fixes are in [`roadmap.md`](roadmap.md).

The agent may run only the observe and act groups (`company`, `employee`, `market`, `task`, `client`, `finance`, `report`); `sim`, `scratchpad` and the run commands belong to the runner. Money in events is converted from cents to dollars before the agent sees it. A run stops at `--max-checkpoints`, at `--max-cost` (each checkpoint's own cap is the budget left), on bankruptcy or horizon end, or as `stalled` after 3 failed `sim resume` calls in a row.

Known upstream quirk: YC-Bench's `business_hours_between` (in `yc_bench/core/business_time.py`, used for task progress) counts 09:00 to midnight on a weekday, 15 hours, when an interval crosses midnight, while deadlines are set with 9-hour days. Work therefore progresses faster than 9-hour days would suggest. Prompts v1 and v2 told the agent to plan with 9-hour days; v3 does not, since the stock prompt doesn't. The runner does not patch YC-Bench.

## Choices worth defending

- **No framework.** The loop is about 100 lines, so every guardrail is visible and testable.
- **Consolidation is gated by volume.** It reads every message since the watermark, so it runs on the cheap model and only every N chats.
- **Approval comes before the irreversible step.** A refund over the limit is never executed by the model. The run stops, and the operator re-runs it with approval.
- **Retrieval has a similarity floor.** Irrelevant memories are left out instead of padding the context.

The LLM Ops layer (Langfuse tracing, the eval set and gate, the τ²-bench adapter and its results) was removed to keep the repo to the agent and its memory. It is in the git history before this change.
