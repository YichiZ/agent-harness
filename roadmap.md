# Roadmap

## Stale memory

**Problem.** In the v2 YC-Bench smoke run of 2026-10-28 ([`bench/yc-bench/results/2026-10-28-smoke-sonnet-seed1-v2/`](bench/yc-bench/results/2026-10-28-smoke-sonnet-seed1-v2/)), 25 facts were stored at the end. 11 were "Currently:" snapshots, and all 11 were stale, such as "Currently: Task-10 (Vanguard ML) is in progress" long after it failed. Some facts contradicted others ("Helix Systems has no track record yet" next to "Helix Systems is a reliable client"), and Vanguard ML was still recorded as having "no track record" after its task failed. At checkpoint 10, 8 of the 10 facts retrieved for the agent were stale, and none of the useful client facts were retrieved.

**Cause.** `Consolidator` replaces an existing fact only when the new one's cosine similarity under the hashing embedder is at least 0.6 (`REPLACE_SIMILARITY`); a reworded update is appended and the old fact stays. Nothing expires, caps or drops stale facts. Retrieval ranks facts by similarity to the checkpoint prompt, which is a dump of state, so state-like facts win over lessons.

**Done now.** The YC-Bench summarizer prompt v2 (`bench/yc-bench/prompts/summarizer.v2.md`) no longer stores current state, "no track record" facts or dollar figures, records failures and inflation under the client's name, and restates a corrected fact in the same wording so it replaces the old one.

**Planned harness changes, not yet built:**

- (a) Expire state facts: replace all "Currently:"/state facts on each consolidation, or give them a TTL.
- (b) Detect contradictions: when a new fact is about the same entity (for example a client name), have the summarizer decide whether it replaces the old fact, instead of relying on the similarity threshold.
- (c) Use a better embedder than hashing, or match facts by an entity key.
- (d) Cap the number of facts and prune by usefulness or recency.
- (e) Split retrieval so durable lessons are not crowded out by similarity to the state dump.
- (f) Do not inject the previous note twice, once as its own block and again through recalled episodes; keep the recalled-episodes section small.
- (g) Count the summarizer's cost against the per-checkpoint cost cap.

**Done after the seed 2 year run** ([`bench/yc-bench/results/2026-11-02-year-sonnet-seed2-v4/review.md`](bench/yc-bench/results/2026-11-02-year-sonnet-seed2-v4/review.md)):

- (b), (c): with `subject_keys` (on for YC-Bench, off for the demo), facts that start with `Subject:` replace only the fact with the same subject (`harness/memory.py`, `replacement_for`). Cosine replacement is now limited to facts with no subject, so a client fact can no longer overwrite another client's fact.
- Recall shows every subject fact, and top-k applies only to facts with no subject. In that run, k=10 hid avoid-facts at 3 bad-client accepts.
- Prompts v5: client facts are track records with counts, rules need a proving event and their own topic, and Throughput facts, task ids and unfinished-task facts are banned. `checkpoint.v5.md` no longer implies daily payroll. `system.v5.md` is unchanged from v4.

**Still planned:** (a) and (d) are now bounded by one fact per subject, but there is still no TTL or cap. (e), (f) and (g) are unchanged. A structured `{subject, fact}` summarizer schema would remove the prefix regex. Subject facts are recalled uncapped. The other suggestions from that review: count client outcomes in code from `task_completed` events instead of trusting the summarizer, and log the store size per checkpoint.
