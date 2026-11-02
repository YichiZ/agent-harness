# Review: Sonnet 5.5 full-year run on prompts v4

Run settings: claude-sonnet-5-5 at medium effort as the agent, Haiku summarizer, seed 2, default config, the full 2025 horizon (125 checkpoints, `horizon_end`). The run's `git_sha` is 5f6d395: main at 22c934e plus a `.superset/config.toml` that is not on main and does not affect the run; the prompt hashes in `summary.json` match `bench/yc-bench/prompts/*.v4.md`. This is the first full-year run, so the earlier 10-checkpoint smokes could not show the things below. I computed every number from the raw `checkpoints/cp-*.json` and `summary.json` with scripts and checked the quotes against the log. Ground truth for which clients are unreliable comes from `summary.json` (`time_series.clients[].is_rat`): Equinox Labs and Vanguard ML. They are the same two clients the Opus seed 1 smoke ran into, because every seed shares one world.

## Results

Final funds $1,473,616 from $200,000 (cost $11.83, 669 calls, about 5.4 calls per checkpoint, never near the 30-step cap).

| Client | accepted | ok | failed | cancelled | revenue | failure penalty | task-days | revenue per task-day |
|---|---|---|---|---|---|---|---|---|
| Helix Systems | 42 (1 unfinished) | 41 | 0 | 0 | $597,217 | 0 | 119.5 | $4,998 |
| Cortex Intelligence | 40 | 40 | 0 | 0 | $585,362 | 0 | 109.0 | $5,370 |
| Stratos Cloud | 39 | 39 | 0 | 0 | $543,518 | 0 | 113.8 | $4,776 |
| Prism Analytics | 12 | 12 | 0 | 0 | $157,252 | 0 | 50.7 | $3,104 |
| Equinox Labs | 15 | 3 | 12 | 0 | $37,754 | -$56,188 | 209.0 | $181 |
| Vanguard ML | 8 | 1 | 7 | 0 | $11,217 | -$41,861 | 133.9 | $84 |
| Total | 155 (+1 unfinished at the horizon) | 136 | 19 | 0 | $1,932,320 | -$98,049 | 735.9 | |

- **Every failure is a bad client.** All 19 failed tasks came from Equinox or Vanguard, each with a penalty of exactly 35% of the listed reward and no revenue. Failed tasks took a median of 14.8 days (max 30.1, Vanguard Task-106) and finished 4 to 507 hours late. Tasks for the four good clients took about 2 to 4 days.
- **The two bad clients took 47% of all task-days.** That is 343 of 736 task-days, for a net of -$49k. The four good clients earned about $4,800 per task-day. If only part of that time had gone to good tasks the run would have ended far above $1.47M. The upper bound is limited by how many good tasks were on the market; see the browse-window finding below.
- **Months:** the month with no bad-client task was the best one. April had 23 completions and $385k revenue. Bad clients took 55 to 70% of task-days in May, June, August, September and November, and revenue in those months was $120k to $160k.
- **Funds curve (month end):** Jan $335k, Feb $501k, Mar $614k, Apr $955k, May $1.03M, Jun $1.11M, Jul $1.19M, Aug $1.30M, Sep $1.35M, Oct $1.42M, Nov $1.49M, Dec $1.47M. Growth averaged about $190k per month in Jan to Apr and about $65k per month after.
- **Revenue vs payroll:** revenue $1,932k, penalties $98k, payroll $561k (11 monthly payrolls). The 11 charged payrolls rose from $39,245 (2025-02-03) to $61,205 (2025-12-01), +56%, through salary bumps.
- **Idle time:** small. The two teams were busy 359.5 and 355.8 of 365 days, about 2% idle, almost all in the last 12 days (team B idle 6.1 days from 2025-12-19 and again about 1.7 days after Task-13 finished on 2025-12-30; team A idle 5.0 days from 2025-12-25).
- **Other seeds:** at 2025-02-04 the Opus seed 1 smoke had $389,697 and this run had $304,315 (cp8), about $85k behind. Different seed and model, so this is only a rough reference.

## Bad clients

Both were first identified by their own behaviour early. Vanguard Task-46 failed (event at cp5, visible cp6) and Task-112 failed (visible cp9). Equinox Task-5 failed at cp16 (visible cp17).

**After that the agent accepted 20 more tasks from them (Vanguard 6, Equinox 14).** Only 4 succeeded. Together they cost $79,326 in penalties and 297 task-days against $48,972 revenue. Both lists are the complete accept lists.

- **Vanguard, accepts after two visible failures:** Task-58 (cp59, ok), Task-88 (cp61), Task-106 (cp62), Task-196 (cp85), Task-16 (cp111), Task-64 (cp117).
- **Equinox, accepts after the first visible failure:** cp23, cp50 (two), cp68, cp69, cp86, cp89, cp92, cp96, cp97, cp99, cp112, cp113, cp114. Memory called Equinox "unreliable overall" from cp52. From cp53 on the agent accepted it 11 more times and 8 of those failed.

**Was the avoid fact in the memory it saw?** I compared `facts` at each accept checkpoint.
- Equinox: a negative Equinox fact was in view at all 14 accepts.
- Vanguard: a negative fact was in view at 3 of 6 (cp62, cp85, cp117) and absent at cp59, cp61 and cp111. The store held Vanguard facts all along. They were outranked by the top-10 cap (`memory.py:239-240`) because recall ranks by similarity to the checkpoint prompt, which has no market information. The recalled set also held 10 facts from cp10 to the end while the store grew to 29, and 13 of the final 29 were never shown at any checkpoint.

**Why it still accepted: mostly the agent, not the memory.** The memory was often present and the agent often said so in the same note.
- **It dropped the avoidance on one lucky win.** cp61: "Task-58 finished ahead of deadline and trust rose by 1.6, so I'm no longer avoiding this client. Its research tasks pay well." Then Task-88 and Task-106 failed. cp62: "Vanguard ML research tasks dominate the market and pay well, so I'm continuing with them."
- **It read the memory wording backwards.** The summarizer wrote "failure is suspect as client blame". The agent took that as a reason to try again: cp50: "The earlier Equinox failure looked like client blame, so these two are a test of whether they're reliable." (cp92 repeats this.) The suspicion was correct, since both are rat clients, but "suspect" reads as doubt.
- **It named the risk and accepted anyway** (cp85: "Vanguard has failed for me before, so this is a risk"; cp111: "Vanguard has failed us before, so this one is a risk"; cp117: "Vanguard has failed five tasks, so this one is a risk").
- **Gated tasks tempted it.** cp97: "Equinox trust was high enough for this gated task" (cp96 has similar wording: "probably what let me take this gated task").
- **Its notes copied "still avoiding" forward while accepting.** cp70 (right after taking Equinox at cp68 and cp69): "I'm still avoiding Equinox Labs and Vanguard ML, which keep failing." cp117: "Equinox Labs has failed every task I gave it", yet Task-101, Task-107 and Task-35 had succeeded.
- **The "market has nothing else" claim is a browse-window artifact.** `market browse` is sorted by reward descending in all 110 unfiltered browses, and the two bad clients are the highest-paying. They made up 69% of every listing on average (79% in the last 30). The agent always used `--limit 8` to `20` and never `--offset`, and used `--domain` only 5 times. In 13 of the 23 bad-client accepts the same listing still held an eligible good task that was not taken. For the other 10 the window had none, and I cannot say whether the market had more beyond it. Same sim time 2025-12-29T10:01:52: cp122 browsed with `--limit 10` (8 Vanguard, 1 Equinox, 1 Stratos), declined, and noted "almost all Vanguard ML research work"; cp123 browsed with `--limit 20`, found Helix Task-13 and took it. It paid $9,082.
- **It never looked at the stock tools meant for this.** Across all 125 checkpoints there were 0 `client history`, 0 `client list`, 0 `company status`, 0 `task inspect` and 0 `task cancel` calls. The commands were accept, assign and dispatch 156 times each, browse 115, `employee list` 31 and `task list` 29. The cp1 note said "Next time: Inspect a task's deadline and required work before accepting it." and it never did. In the Opus seed 1 smoke the agent inspected after accepting and cancelled both bad tasks early, with 0 failures; here Task-106 ran 30 days and was 507 hours late.
- **A stuck failing task held the team for weeks.** Task-106 was past its deadline from 2025-06-27 and was flagged at risk, but not finished until 2025-07-18. The agent put three more tasks onto the same four employees (Task-54, Task-41, Task-121), so the rate was split. Task-112 and Task-133 (26 h) overlapped the same way.

## Agent play

- **Parallelism and team size:** exactly two teams of four every time (A = Emp_4, Emp_2, Emp_8, Emp_5; B = Emp_6, Emp_7, Emp_1, Emp_3; 153 of 156 accepts), at most 2 active tasks, never another split. No evidence either way on 2-person teams. The agent noted team B is weak at research (rates 1.4 to 5.4) and sent research to A.
- **Deadline misses not caused by client behaviour:** one candidate. Task-5 (Equinox, cp13) was 97.96% done with 77 minutes to its deadline when cp16 dispatched Task-174 onto the same four employees, which halved their rate ("Their rate is split between the two tasks until Task-5 finishes"). It finished 4 hours late. Equinox is a rat client, so this is not proven, but it is the only failure within hours of its deadline. All 18 other failures were 22 hours or more late.
- **Deadlines never bound good work:** good-client tasks mostly finished 95 to 240 hours ahead (minimum 25) of windows of about 9 days, so the limit was team time, not speed. The agent's per-hour estimates were never checked ("I didn't check their rate against the units" recurs in many notes), and it caused no good-client failure.
- **End of horizon (cp120 to cp125) was poor:**
  - The agent believed "Tasks whose deadlines fall after the simulation horizon end cannot pay out". Task-13 was accepted at cp123 with a deadline of 2026-01-07, finished 2025-12-30, and paid $9,081.96 (funds 146,453,434 to 147,361,630 cents).
  - At cp124 it wrote "Task-13 is already running", although the prompt said 0 active tasks and the resume failed with "No active tasks". Task-13 had already finished.
  - cp125 accepted Helix Task-163 (1,368 units, due 2026-01-08) and funds stayed unchanged at `horizon_end`.
  - cp125 said the Stratos and Cortex tasks "need prestige or trust I don't have". From the prestige and trust series, data_environment prestige was 4.86 and Stratos trust was above 4. Task-6 (Stratos, 894 units, needs prestige 1), Task-157001 and Task-151000 (Cortex, needs prestige 1 and no trust) were listed and open to it. The agent never ran `company status`. At cp89 it said the same ("Stratos's open tasks need prestige 3") when data_environment prestige was 3.59, and took Equinox Task-29 instead (it failed).
  - Loss is small, at most one or two payouts of about $9k each, under 1.3% of final funds.
- **Money units:** correct throughout.

## Memory (summarizer v4)

**Shape over time:** the agent saw 0, 0, 4, 5, 6, 6, 7, 8, 9 facts at cp1 to cp9 and 10 at every checkpoint from cp10 on (the `semantic_top_k` cap). Of 1,205 fact slots shown over the run, 83% named a task id; 553 were single-task client logs, 305 client roll-ups, 275 rules, 65 Throughput and 7 employee facts. 209 distinct fact strings passed through a store that ended at 29. The final 29 contain 4 false or stale facts, 1 misleading, about 5 redundant, and 13 were never shown.

**Task ids are not hallucinated.** Every `Task-N` in all 209 facts exists in the log. `Task-90001` and `Task-157000` are real: when task N is accepted the simulator issues `replacement_task_id` `Task-N000` (then `N001`, `N002`). Task-90001 (Helix, accepted cp101) and Task-157000 (Cortex, accepted cp118) were both completed. A regex check of every single-task fact found 0 mismatches in hours margin, units, trust deltas or team members, and there was no false blame on a good client and no dollar figures. The facts about individual tasks are accurate; the bugs below are in what survives, what is shown and what is stated as a rule.

**Bugs, each tied to code or prompt:**
1. **Top-k recall hides client facts (high).** `memory.py:239-240` and `:284` rank by similarity to a prompt with no market information, with k=10. Cortex was last shown at cp102 (it had 40 successes), Prism at cp121; Vanguard facts were missing at three Vanguard accepts.
2. **Replace-by-similarity overwrites facts and loses evidence (high).** `memory.py:342-344` replaces the nearest fact at cosine 0.6 or more, and `existing` (`:329`) is not refreshed within a run. The Vanguard Task-16 fact (cp114 to 121) was replaced by Task-64 (cos 0.943) at cp122; Equinox Task-149 (cp110 to 117) was replaced by Task-143 (cos 0.602) at cp117. Vanguard's only success, Task-58, and Equinox's successes Task-101 and Task-35 are gone. Roll-ups drift: Vanguard lists 5 of its 7 failures, Equinox 6 of 12 with no counts, Stratos is frozen at 4 of 39 tasks from cp63 to the end, Prism at 2 of 12.
3. **Stale state facts that are never removed (high).** Summarizer v4 says "Never store current state" and "Never store 'no track record yet'", yet the final store has "Helix Systems: Task-90001 is not yet finished, so no completion record exists" (it was accepted at cp101 and completed 191 hours early at that same checkpoint's resume) and "Vanguard ML: Task-196 was still unfinished at 61% progress" (it failed late at cp89). The code can only replace at cosine 0.6 or more, so a differently worded later fact never removes them.
4. **Wrong rules (high).**
   - "Payroll is charged every day even when no tasks are running" contradicts the stock prompt ("deducted monthly") and the 11 `monthly_payroll` events. It likely comes from the harness text in `checkpoint.v4.md`, "payroll is being spent with no revenue".
   - "Tasks whose deadlines fall after the horizon cannot pay out" came from the agent's own guess at cp123 and was disproved by Task-13. The summarizer prompt asks for mechanics "learned by experience" but not for evidence in the events.
   - "Raises client trust by 1.6" (cp3 to cp6) was over-generalised from two tasks and corrected at cp6.
   - The gating fact says "Stratos Cloud's open tasks required prestige 3 and Cortex's open task required trust 3", a snapshot that was no longer true when written.
5. **Throughput facts carry no throughput (medium).** All 26 distinct Throughput facts say "N hours before the deadline"; none has dispatch-to-finish time, which summarizer v4 requires. The log does not contain dispatch time, so Haiku fell back to margins.
6. **Prefix "Rule: Game mechanic:" breaks one-fact-per-subject (medium).** About 9 different rules share it, and two near-identical "pays its listed reward in full; trust gain varies" facts sat in the same recall at cp123 to 125 (cos 0.81). Equinox flipped at cp52 ("suspicion withdrawn") and cp53 ("each failure is suspect as client blame").
7. **No employee strengths (low):** 3 distinct employee facts, last shown at cp89.

## Leaks

None found. `system.v4.md` is the stock prompt plus one sentence, `tests/test_ycbench.py` passes (25 tests), and no client names or mechanics numbers appear in the three v4 prompt files. Real client names, hours and task ids in facts come from the log, which is allowed. Nits: the summarizer example "Throughput: 4 employees finished 600 units" uses 4 employees; the agent chose 4 at cp1 with empty memory, so it did not cause it. `memory.py:292` titles the section "What you know about this operator", at odds with "treat them as your own notes". The 35% penalty, task-days and reward-sorted listing above are my reconstruction from logs and must not go into any prompt.

## Suggested fixes (ranked)

Code:
1. **Show client facts every time.** In `build_working_memory`, always include one fact per client (or all facts whose subject is a client) and use top-k only for the rest. This fixes Vanguard's missing facts at 3 accepts and Cortex's disappearance.
2. **Build a deterministic per-client ledger from the events.** The checkpoint prompt already contains structured `task_completed` lines (client, success, margin). Code can count ok, failed and last failure per client and store one fact per client, replacing the Haiku roll-ups (which listed 5 of 7 and 6 of 12 failures). It also removes stale per-task facts.
3. **Replace by subject key, not whole-sentence cosine.** Key on the text before the first colon, or before the second for `Rule:` facts, and refresh `existing` inside the loop (`memory.py:329`, `:342-344`).
4. **Delete state facts when the task completes.** On a completion event for Task-N, drop any fact that names Task-N and says unfinished or in progress.
5. Log store size and the summarizer output per checkpoint in the checkpoint JSON; I could only observe the recalled 10.

Prompt (new `*.v5.md` files for all three plus `release.json` bump; never edit v4):
1. **summarizer v5:**
   - Client facts as counts ("N finished early, M failed"), no task lists.
   - Replace "suspect as client blame" with plain "avoid" wording.
   - Rules only when an event in the log proves them, each under its own subject.
   - Remove the Throughput bullet or require elapsed time.
   - Ban "not yet finished" wording.
2. **checkpoint v5:** reword the idle line so it does not imply daily payroll.
3. **system v5 (optional, trade-off against "stock plus memory"):** advise running `client history` before taking work from a client with any failure, using `--domain` filters and a larger `--limit` when the listing looks thin, and not putting a second task on a team that is still on a running one. Do not describe work growth, the reward-sorted listing or the penalty size: those are leaks.
