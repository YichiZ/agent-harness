# Review: first smoke run on the fair v3 prompts

Run: Sonnet 5.5, seed 1, 10 checkpoints, main at 639cb32 (PR #7), prompts `*.v3.md`. Three Sonnet agents reviewed it line by line: one read the run transcript, and two read the PR #7 diff (one the prompts and docs, one the test and runner). I checked their main claims against the files.

## Results vs the earlier v3 smoke run

The earlier run, `2026-10-29-smoke-sonnet-seed1-v3/`, used `prompt_version` v2, which still had the leaked mechanics.

| | earlier run (leaky v2 prompts) | this run (fair v3 prompts) |
|---|---|---|
| cost | $1.06 | $1.34 (59 model calls) |
| final funds | $376,509 (sim ended 2025-02-25) | $205,976 (sim ended 2025-03-03, after the ~$40k March payroll) |
| tasks | 13 ok, 1 failed, 2 cancelled | 6 ok, 2 failed, 3 cancelled, 1 still active |
| Vanguard ML | Task-10 failed | Task-10 failed (late 185h), blamed on staffing |
| Equinox Labs | 2 cancelled | Task-191 failed (late 147h), blamed on staffing |
| facts at end | 9 | 17 |

Allowing for the extra payroll, this run ends about $130k behind. The drop is expected: the agent no longer knows the throughput rules it was given before. The stock YC-Bench agent doesn't know them either.

## Transcript (agent decisions)

- **cp1 (high):** The agent accepted Vanguard Task-10 sight unseen: it was listed first and had the highest reward. It didn't run `task inspect`. It put 6 employees on the task and left 2 idle. The task failed.
- **cp2 (high):** It accepted Task-128, Task-27 and Task-8 just to see their deadlines, then cancelled all three. That cost prestige (Task-8's penalty was 0.38 research). Task-8, from Cortex, was a clean win in the earlier run.
- **Root cause (high):** The agent read `skill_rates` as units per *day*, when they are per business hour. Every feasibility estimate in cp2 and cp4 is off by about 9x, for example "29.5 units/day for 8 people". `employee list` prints `skill_rates` without a unit; the field is `rate_domain_per_hour` in `yc_bench/cli/employee_commands.py`. The stock agent faces the same ambiguity.
- **cp2:** Because of that, the agent took Equinox Task-191 while saying it would likely miss, on the grounds that idle payroll earns nothing. It failed.
- **cp1–cp3:** About 33 sim days with no revenue: two penalties ($7.3k and $4.4k) and a $38k payroll.
- **cp4:** Helix Task-25 finished 142h early even though the agent predicted it would fail. That success rescued the run.
- **cp4–cp10 (medium):** The agent ran one task at a time, always with all 8 employees, and only for Helix. With no second task running in parallel, it also paid about twice the salary bumps of the earlier run's 4-person teams. At cp5, cp6, cp7, cp9 and cp10 the agent skipped `task inspect` or `employee list`, or said it hadn't checked feasibility.
- **Client detection (high):** The agent never inferred that Vanguard or Equinox might be unreliable. It blamed both failures on capacity, even after the same team finished larger tasks (798 to 1,294 units) within similar deadlines. It stopped taking work from those two clients only because it preferred Helix.
- **Money units:** no errors. Cents were converted correctly.

## Memory (summarizer v3)

- **Contradiction (high):** These two facts both stay in memory from cp5 to cp10:
  - "a task whose required days are about double the days left ... has failed every time"
  - "the earlier rule ... was contradicted ... should not be relied on"

  The summarizer's "restate in the same wording" rule fails when the new fact is worded differently.
- **Wrong mechanics and numbers (high):**
  - The "divide units by combined rate, fits within days left" rule treats per-hour rates as per day.
  - The per-day rate estimates (29.5, 6.7, 6.3) come from the same mistake.
  - Throughput estimates swing between 29, 137, 285 and 190 units a day.
- **Misattributed failures (high):** Both adversarial clients are stored as staffing failures. The summarizer rule "blame a client only when the team had capacity on paper" took the agent's wrong capacity maths at face value.
- **Duplicates (medium):**
  - Task-10 is stored twice, once as a client fact and once as a staffing fact.
  - Helix trust appears twice.
  - In cp4–cp7, a run-state-style Equinox fact sits alongside the failure fact.
- **Rule compliance:** no dollar figures; one mild state fact ("trust has reached 3.0", cp8).

## PR #7 diff

No high-severity findings. The suite passes (39). The v3 files load and are hashed into `summary.json`, and the system prompt has no dangling references.

- **summarizer.v3.md:13 (medium):** The example "Acme Widgets: Task-10 failed, late by 183 hours" still uses the real seed-1 failure: Task-10, late by 183h, appears in `2026-10-28-smoke-sonnet-seed1/`. That is seed-specific detail, which the new rule bans. This run used that prompt, though the agent's own Task-10 failure was 185h. Fix: use a generic example such as "Task-3 failed, late by 40 hours" in a v4, since this run now cites v3.
- **summarizer.v3.md:14 (low):** "Blame a client only when its task failed with a team that had the capacity on paper" echoes the old hint about inflation. It is defensible as attribution hygiene.
- **tests/test_ycbench.py leak test (medium):** It matches literal phrases only, so "35 %", "/150", "top 4" or "9am" would get through. It doesn't scan strings hardcoded in `run.py`. It also passes if only one prompt file exists. Cheap fixes:
  - normalize whitespace, and use a few regexes such as `\b150\b` and `\b35\s*(%|percent)`
  - assert that all three prompt kinds are present
  - scan `run.py` for the client-name pool
- **tests/test_ycbench.py:77 (low):** It hardcodes `summarizer.v3.md`. Derive the name from `release.json` and assert that all three files are hashed.
- **CLAUDE.md (low):** The fair-prompts rule should also ban task ids and numbers taken from logged runs.
- **No leaks** in the v3 system or checkpoint prompts. Every Key mechanics bullet matches the stock prompt. The agent worked out the 35% penalty itself, from the events.

## Needs a decision

1. **Rate units:** Should the system prompt say that `skill_rates` are units per business hour? The stock prompt doesn't say it, so under the fair-prompts rule this would be a leak. But it's the root error in this run. Fair alternatives:
   - Have the summarizer measure throughput from completed tasks.
   - Accept the stock-level ambiguity.
2. **Summarizer v4:** a generic example, and superseding facts that contradict each other. Should it also stop storing the agent's own rate estimates, and cross-check client failures against the same team's later successes? Changing the summarizer is fair game, because it's our harness, not hidden information.
3. **Leak test hardening:** the regexes, the presence check for all three prompt kinds, and scanning `run.py`.
