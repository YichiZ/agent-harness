# Roadmap

## Stale memory

Found in the YC-Bench smoke runs (`bench/yc-bench/results/2026-10-28-smoke-sonnet-seed1-v2/`): at the end of 10 checkpoints, 12 of the 25 semantic facts were out of date. Examples: "Currently: Task-10 (Vanguard ML) is in progress" long after it failed, "Vanguard ML has no track record yet" after its task failed, and "Helix Systems has no track record yet" next to "Helix Systems is a reliable client".

**Cause.** `Consolidator.run` replaces an existing fact only when the new one scores at least `REPLACE_SIMILARITY` (0.6) against it with the hashing embedder. A reworded update ("Helix Systems is reliable" vs "Helix Systems has no track record") rarely reaches that, so it is appended and the old fact stays. The YC-Bench summarizer prompt asks for "Currently:" on current-state facts so they can be replaced, but nothing replaces them.

**Changes, smallest first:**

1. **No current-state facts (prompt only).** Tell the YC-Bench summarizer not to store current state at all: each checkpoint prompt already shows funds, payroll, tasks and the previous note. Removes most of the stale facts.
2. **Drop "Currently:" facts on each consolidation (harness).** In `Consolidator.run`, delete the user's facts that start with "Currently:" before adding the new ones, so only the latest snapshot survives.
3. **Let the summarizer update and delete by id (harness).** Show existing facts with ids and change the output schema to `{"add": [...], "update": [{"id", "fact"}], "delete": [ids]}`, so a contradicted fact is replaced or removed by the model instead of by a similarity threshold.
4. **Real embeddings (harness).** Swap `HashingEmbedder` for an embedding model behind `Embedder`, so near-duplicates and rewordings are recognised; retune `REPLACE_SIMILARITY` and `MIN_SIMILARITY`.
5. **Measure it.** Add a check to the YC-Bench summary: number of facts, how many contradict the world (for example a client called reliable that `time_series.clients` marks `is_rat`), and how many repeat an entity. Compare before and after each change.

Related, not memory: the agent never re-checked Vanguard ML's task size after accepting it, so the inflated task failed instead of being cancelled. A checkpoint-prompt line listing each active task's units now vs at accept would surface inflation without relying on memory.
