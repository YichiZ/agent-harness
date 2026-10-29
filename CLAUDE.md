# agent-harness

## Rule: work in a worktree

Make all code changes in a git worktree at `.claude/worktrees/<name>` on its own branch, never in the main checkout or a cloud copy:

```bash
git worktree add .claude/worktrees/<name> -b <branch>
```

`.claude/worktrees/` is git-ignored. Copy `.env` into the worktree if you need API calls.

## Rule: fair YC-Bench prompts

For ethical reasons (no benchmaxxing) and to keep results comparable with the published YC-Bench leaderboard, prompts under `bench/yc-bench/prompts/` may only use information stock YC-Bench agents get:

- No descriptions of hidden mechanics, e.g. how unreliable clients behave. Stock agents get only "Not all clients are reliable. Check `client history` for failure patterns."
- No real client names from the simulator (`_CLIENT_NAME_POOL` in `yc_bench/services/generate_clients.py`), not even in examples.
- No seed-specific rules. Every seed shares one world (`_FIXED_WORLD_SEED = 1`), so tuning on any seed is tuning on the test set.

Past results cite their prompt files by version, so change prompts by adding a new version (`*.vN.md`) and bumping `prompt_version` in `bench/yc-bench/release.json`, never by editing an old one. `tests/test_ycbench.py` checks the current version for client names and leak phrases.

## Layout

- `harness/agent.py`: config (`Release`), model client, the agent loop
- `harness/memory.py`: SQLite store, the four memories, consolidation
- `harness/tools.py`: demo customer-service tools over an in-memory backend
- `harness/__main__.py`: CLI
- `prompts/`: versioned system and summarizer prompts
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
