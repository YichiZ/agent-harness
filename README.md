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

## Choices worth defending

- **No framework.** The loop is about 100 lines, so every guardrail is visible and testable.
- **Consolidation is gated by volume.** It reads every message since the watermark, so it runs on the cheap model and only every N chats.
- **Approval comes before the irreversible step.** A refund over the limit is never executed by the model. The run stops, and the operator re-runs it with approval.
- **Retrieval has a similarity floor.** Irrelevant memories are left out instead of padding the context.

The LLM Ops layer (Langfuse tracing, the eval set and gate, the τ²-bench adapter and its results) was removed to keep the repo to the agent and its memory. It is in the git history before this change.
