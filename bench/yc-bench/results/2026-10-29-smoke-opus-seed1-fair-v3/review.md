# Review: Opus 5.5 smoke run on the fair v3 prompts

Run settings: Opus 5.5 as the agent, Haiku summarizer, seed 1, 10 checkpoints. Code is main at 639cb32, with prompts `*.v3.md`. This matches [the Sonnet fair-v3 run](../2026-10-29-smoke-sonnet-seed1-fair-v3/) except for the agent model. A Sonnet agent reviewed the transcript line by line, and I spot-checked its main claims against the log.

## Results vs the Sonnet fair-v3 run

| | Sonnet 5.5 | Opus 5.5 |
|---|---|---|
| cost | $1.34 (59 calls) | $2.97 (69 calls) |
| final funds | $205,976 | $353,906 |
| sim end | 2025-03-03 (2 payrolls) | 2025-02-05 (1 payroll) |
| tasks | 6 ok, 2 failed, 3 cancelled | 12 ok, 0 failed, 2 cancelled |
| Vanguard ML | Task-10 failed late; blamed on staffing | Task-10 grew from 564 to 2,256 units after accept; spotted at cp1, cancelled at cp2 |
| Equinox Labs | Task-191 failed late; blamed on staffing | Task-119 grew from 860 to 3,440 units after accept; cancelled in the same checkpoint (cp4) |
| facts at end | 17 | 28 |

The sim end dates differ because the runner jumps from one event to the next. Opus's two parallel teams finished a task about every 6 days, so 10 checkpoints covered 35 sim days. For Sonnet they covered 61.

## Agent play

- **Rate units (good):** Opus assumed skill rates are per hour from cp1, using its prior, not a measurement. Its feasibility arithmetic was correct throughout; for example, 783 units at 15 per hour comes to 52 hours. Its first completion, Task-162 finishing 53 hours ahead, matched the prediction. Throughput was always computed from summed rates, never fitted from observed progress.
- **Wrong fact (medium):** it stored "the team works about 8 to 9 work hours per calendar day" (cp3). Work actually happens on weekdays only.
- **Unreliable clients (good):** it re-inspected tasks right after accepting them, which is how it caught both inflations. It never accepted from Vanguard ML or Equinox Labs again, and accused no one falsely. It correctly attributed shrinking tasks at Helix and Cortex to trust.
- **Slow cancel (medium):** at cp1 it computed about 160 hours needed for Task-10 against 63 available. It still kept three employees on it until cp2, about 6 sim days, or roughly one lost task.
- **Equinox probe (low):** accepting Equinox Task-119 cost 0.06 research prestige when cancelled.
- **Staffing (good):** from cp2 it ran two 4-person teams in parallel, with almost no idle time. Money units were correct everywhere.
- **Diversification (medium):** it repeatedly said it would spread work to Stratos, Cortex and Prism, but kept taking Helix tasks. Trust with the others slipped: Cortex 2.93 to 2.82, Stratos 1.49 to 1.17.

## Memory (summarizer v3)

- **Retrieval crowded out by duplicates (high):** from cp4 on, the agent saw only the top 10 of up to 28 facts (`semantic_top_k`). Near-duplicates pushed out the Equinox fact and the trust-shrink fact at cp8 and cp10. The agent kept avoiding Equinox only because its own previous note said so.
- **Duplicates (high):** "restate in the same wording" does not dedupe. The duplicate clusters are:
  - Cortex Task-110 shrink: 3 facts.
  - Helix shrink: 2 facts.
  - Emp_6/Emp_7 data_environment: 2 facts.
  - "Re-check size after accept": 2 facts.
  - Vanguard growth: 2 facts.
  - Prism unchanged: 2 facts.

  The summarizer already receives the existing facts, so this is a prompt-following problem, not a missing input.
- **Misleading facts (medium):**
  - Task shrinkage is stored as a client trait ("Helix shrinks 15-39%"), when it really comes from trust.
  - "Prism sizes have not changed" will stop being true as Prism trust grows.
  - "Cortex sizes otherwise stayed the same" contradicts the Cortex shrink facts.
- **Values that go stale (medium):** trust levels, per-task trust gains, skill values (Emp_4 9.84), team rates, and a single prestige-penalty number.
- **Task-id facts (medium):** most client facts list task ids and hours-ahead figures that will never matter again.
- **Missing lessons:**
  - "Accept, re-inspect, cancel at once if it grew" is not stored.
  - The work-hours fact is wrong.
- **Rule compliance:** no dollar figures and no "unknown" facts.

## Leaks

None found in the prompts or memory. Memory content came from observed events. One leak predates this run: `summarizer.v3.md:13` still uses the real seed-1 "Task-10 … 183 hours" example. It is fixed in #9 (summarizer v4).

## Suggested fixes

1. **Dedup, so retrieval shows the facts that matter.** Summarizer v4 (#9) adds subject prefixes and one fact per task, which should cut duplicates. If top-10 still crowds out client facts, also inject every client fact (they're few) and use top-k only for the rest.
2. **Summarizer v5 on top of #9:**
   - Client facts should be record-level ("N on time, M failed, grew after accept"), with no task ids or hours-ahead figures.
   - Store trust-driven shrinkage as a trust effect, not a client trait.
   - Don't store trust values, skill values or penalty numbers.
3. **Store the "re-inspect after accept, cancel at once if it grew" lesson once it's observed.** Measured throughput (#9) should replace guesses such as "8 to 9 hours per calendar day". Both are learned from the run itself, so neither prompt tells the agent the answer.
