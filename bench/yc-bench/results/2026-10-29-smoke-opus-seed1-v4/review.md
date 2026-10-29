# Review: Opus 5.5 smoke run on prompts v4

Run settings: Opus 5.5 as the agent, Haiku summarizer, seed 1, 10 checkpoints. The code is main at fdb66d5, which includes #8, #9 and #10. `system.v4.md` is #10's stock prompt (sha256 `952ac06f…8835`) and `summarizer.v4.md` comes from #9. Only the prompts differ from [the Opus fair-v3 run](../2026-10-29-smoke-opus-seed1-fair-v3/). A Sonnet agent reviewed the transcript line by line. I checked its main claims against the log and `harness/memory.py`.

## Results vs Opus v3

| | Opus v3 (fair v3 prompts) | Opus v4 |
|---|---|---|
| cost | $2.97 (69 calls) | $3.09 (71 calls) |
| final funds | $353,906 at 2025-02-05 | $389,697 at 2025-02-04 |
| tasks | 12 ok, 0 failed, 2 cancelled | 15 ok, 0 failed, 2 cancelled |
| Vanguard ML | Task-10 grew 4x; found cp1, cancelled cp2 | Task-10 grew 4x; found and cancelled at cp2 (35% done) |
| Equinox Labs | Task-119 grew 4x; cancelled same checkpoint (cp4) | Task-191 grew 4x; cancelled same checkpoint (cp2) |
| facts at end | 28 | 15 |

This run ended a day earlier in sim time, so the comparison at the same date favours v4 slightly more. Both runs paid the one February payroll.

## Why v4 did better

- Revenue was $229k over 15 tasks, against about $194k over 12. Payroll was the same in both.
- Most of the lead came early: v4 ran 3 tasks in parallel from cp1, where v3 ran 2 and left one employee idle.
- v4 kept domain-matched teams of 3, 3 and 2 people. Its early work was spread over four clients, so tasks shrank sooner as trust grew.
- None of this came from memory. The agent's decisions came from its own notes. Memory added only the avoid-Vanguard/Equinox and inspect-after-accept facts, and both runs had those habits anyway.

## Agent play

- **Bad clients (good):**
  - Vanguard Task-10 wasn't inspected after accept at cp1, so 2 employees spent about 7 days on it, the same loss as v3.
  - Equinox Task-191 was caught in the same checkpoint, though only after dispatch.
  - It never accepted from either client again and accused no one falsely. It attributed shrinking tasks to trust.
- **Rate reasoning (medium):** it never settled on a per-hour model and planned by scaling "this team's last task" in calendar days. That was conservative and caused no failures, but it is less exact than v3's arithmetic.
- **Diversification (medium):**
  - "Prism training next" appears in six notes and was never done.
  - Five Helix tasks in a row pushed Helix trust to 3.89, while Cortex sat at 2.77 and Prism at 1.31.
- **Money units:** correct throughout.

## Memory (summarizer v4)

**Improved over v3:**
- No exact duplicates: 15 facts, against 28.
- The Equinox and Vanguard facts stayed in view at every checkpoint.
- No wrong work-hours fact, no false client blame, and no dollar amounts.

**Still bad:**
- **Facts overwritten across clients (high):** `harness/memory.py:343` replaces the nearest fact by embedding similarity (≥0.6) and ignores v4's subject prefixes. Similar "X: Task-N completed H hours ahead" facts therefore overwrite each other across clients: one slot went from Cortex to Helix to Stratos. The final memory has no Cortex record, no Prism record and no Helix on-time count. This is a code issue, not a prompt one.
- **Task-id event logs instead of track records (high):** 8 of the 10 facts shown at cp7–cp10 name a task id, and 4 give "hours ahead". Hours ahead is also unreliable: tasks that finish together are all credited at the same event time.
- **Throughput not measured (high):** no Throughput fact has an elapsed time, and only one has a size. Haiku ignored v4's size, team and time rule.
- **Shrinking stored as a client trait, and wrong (medium):** "Helix cuts 37-40% each time" is wrong. Its listed tasks actually shrank 24% to 39%, rising with trust.
- **Wrong rule (medium):** "Rule: client trust: … trust 3 is needed for Helix inference tasks". Gating is set per task: Helix inference tasks required trust 0, 2 or 3.
- **Stale facts (medium):** "Stratos: two on-time completions"; Stratos actually had 4. Task-18 appears in 3 facts.
- **Final 15 facts:** 4 good, 1 mostly good, 1 partial, 9 bad or wrong. The good ones are the Vanguard, Equinox, work-inspection and deadline-visibility facts.

## Leaks

None found. `system.v4.md` is the stock prompt text. The "some clients inflate it after acceptance" fact came from what the agent observed at cp2 (564 to 2,256 units, and 504 to 2,016), not from a prompt.

## Suggested fixes

1. **Replace facts by subject, not similarity:** in `harness/memory.py`, replace on an exact match of the text before the first colon, and fall back to cosine similarity only when no subject matches. Alternatively, have the summarizer return `{subject, fact}`.
2. **Summarizer v5:**
   - Client facts as track records ("N on time, M failed, grew Nx after accept"), with no task ids or hours ahead.
   - One rule that work shrinks as trust rises, and one that gating is per task.
   - Always show client and rule facts, and use top-k only for the rest, or raise `semantic_top_k`.
3. **Throughput:** either give completion events a dispatch time and the true finish time (`completed_at` is a credit time, batched at events), or drop Throughput facts.
