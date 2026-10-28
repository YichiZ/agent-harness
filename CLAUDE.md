# agent-harness

## Rule: work in a worktree

Make all code changes in a git worktree at `.claude/worktrees/<name>` on its own branch, never in the main checkout or a cloud copy:

```bash
git worktree add .claude/worktrees/<name> -b <branch>
```

`.claude/worktrees/` is git-ignored. Copy `.env` into the worktree if you need API calls.

## Layout

- `harness/agent.py`: config (`Release`), model client, the agent loop
- `harness/memory.py`: SQLite store, the four memories, consolidation
- `harness/tools.py`: demo customer-service tools over an in-memory backend
- `harness/__main__.py`: CLI
- `prompts/`: versioned system, summarizer and section-heading prompts (`Release.prompts_dir`)
- `skills/`: procedural-memory skill files
- `bench/yc-bench/`: YC-Bench runner (`run.py`, `release.json`, `prompts/`, logged `results/`)
- `release.json`: models, budgets and memory knobs for the demo agent

## Commands

```bash
uv sync
uv run pytest -q
uv run python -m harness chat --user op-1
uv run python -m harness consolidate --user op-1
uv run python bench/yc-bench/run.py --fake --max-checkpoints 3
uv run python bench/yc-bench/run.py --seed 1 --max-checkpoints 10 --max-cost 5
```
