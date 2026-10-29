# YC-Bench run: seed 1, claude-opus-5-5

- started: 2026-10-28 23:14:57
- config: default
- release: prompt_version v4, agent_model claude-opus-5-5, agent_effort medium, summarizer_model claude-haiku-5-5, max_steps 30, max_cost_usd 2.0, history_turns 10, semantic_top_k 10, episodic_top_k 5, episodic_recent_k 3, consolidate_every_n_chats 1, prompts_dir bench/yc-bench/prompts

## Checkpoint 1 · 2025-01-01T09:00:00

Funds $200,000.00 → $229,391.04, sim time → 2025-01-08T12:09:26.709215

**Commands**

- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-10", "client_name": "Vanguard ML", "required_pres…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 397260, "skill_rates": { "data_environ…
- $ `yc-bench task inspect --task-id Task-10` → { "task_id": "Task-10", "title": "Task-10", "status": "market", "client_name": "Vanguard ML", "required_prestige": 1, "r…
- $ `yc-bench task accept --task-id Task-10` → { "task_id": "Task-10", "status": "planned", "accepted_at": "2025-01-01T09:00:00", "deadline": "2025-01-09T18:00:00", "r…
- $ `yc-bench task accept --task-id Task-128` → { "task_id": "Task-128", "status": "planned", "accepted_at": "2025-01-01T09:00:00", "deadline": "2025-01-09T18:00:00", "…
- $ `yc-bench task accept --task-id Task-162` → { "task_id": "Task-162", "status": "planned", "accepted_at": "2025-01-01T09:00:00", "deadline": "2025-01-09T18:00:00", "…
- $ `yc-bench task assign --task-id Task-10 --employees Emp_4,Emp_8` → { "task_id": "Task-10", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8" ], "total_assigned": [ "Emp_4", "Emp_8…
- $ `yc-bench task assign --task-id Task-128 --employees Emp_7,Emp_2,Emp_5` → { "task_id": "Task-128", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_2", "Emp_5" ], "total_assigned": [ "Emp_…
- $ `yc-bench task assign --task-id Task-162 --employees Emp_6,Emp_1,Emp_3` → { "task_id": "Task-162", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_1", "Emp_3" ], "total_assigned": [ "Emp_…
- $ `yc-bench task dispatch --task-id Task-10` → { "task_id": "Task-10", "status": "active", "assignment_count": 2, "assigned_employees": [ "Emp_4", "Emp_8" ] }
- $ `yc-bench task dispatch --task-id Task-128` → { "task_id": "Task-128", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_7", "Emp_5", "Emp_2" ] …
- $ `yc-bench task dispatch --task-id Task-162` → { "task_id": "Task-162", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_3", "Emp_1", "Emp_6" ] …

**Note**

> I accepted, assigned and dispatched three tasks. All are due 2025-01-09 18:00 and no reward has come in yet.
> - **Task-10** (research, $20.9k, Vanguard ML): Emp_4 and Emp_8, about 10.2 units/hr for 564 units, roughly 55 hours of work.
> - **Task-128** (inference, $15.2k, Cortex Intelligence): Emp_7, Emp_2 and Emp_5, about 12.1 units/hr for 581 units, roughly 48 hours.
> - **Task-162** (data_environment, $14.2k, Stratos Cloud): Emp_6, Emp_1 and Emp_3, about 13 units/hr for 768 units, roughly 59 hours.
> 
> What I learned: the deadline (about 8.4 days here) only appears after you accept, so check work hours against it before committing. I don't know yet whether skill rates are per working hour or per clock hour, so I can't be sure these deadlines are safe. Payroll is about $38k a month against $200k in funds.

done, 6 steps, 7 model calls, $0.2085 (total $0.2085)

**Memory it saw:** 0 facts, 0 recalled episodes

**Events when time advanced**

- task_completed: {"task_id": "cc623b33-a741-4cd8-92b3-5a2ca6d1984c", "task_title": "Task-128", "client_name": "Cortex Intelligence", "success": true, "funds_delta_usd": 15229.36, "listed_reward_usd": 15229.36, "trust_delta": 1.6, "deadline_margin": "ahead by 30h", "employees_assigned": 3, "salary_bump_total_usd": 125.2, "bankrupt": false}
- task_completed: {"task_id": "b395a08e-144d-4387-9a97-f50d0fe2c988", "task_title": "Task-162", "client_name": "Stratos Cloud", "success": true, "funds_delta_usd": 14161.68, "listed_reward_usd": 14161.68, "trust_delta": 1.6, "deadline_margin": "ahead by 30h", "employees_assigned": 3, "salary_bump_total_usd": 142.39, "bankrupt": false}

## Checkpoint 2 · 2025-01-08T12:09:26.709215

Funds $229,391.04 → $278,852.11, sim time → 2025-01-16T12:58:01.944506

**Commands**

- $ `yc-bench task list --status active` → { "count": 1, "tasks": [ { "task_id": "Task-10", "title": "Task-10", "status": "active", "client_name": "Vanguard ML", "…
- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-8", "client_name": "Cortex Intelligence", "requir…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 400260, "skill_rates": { "data_environ…
- $ `yc-bench task inspect --task-id Task-10` → { "task_id": "Task-10", "title": "Task-10", "status": "active", "client_name": "Vanguard ML", "required_prestige": 1, "r…
- $ `yc-bench task inspect --task-id Task-8` → { "task_id": "Task-8", "title": "Task-8", "status": "market", "client_name": "Cortex Intelligence", "required_prestige":…
- $ `yc-bench task cancel --task-id Task-10 --reason "Cannot meet deadline"` → { "task_id": "Task-10", "status": "cancelled", "reason": "Cannot meet deadline", "cancel_penalty_per_domain": 0.165, "pr…
- $ `yc-bench task accept --task-id Task-8` → { "task_id": "Task-8", "status": "planned", "accepted_at": "2025-01-08T12:09:26.709215", "deadline": "2025-01-17T12:09:2…
- $ `yc-bench task inspect --task-id Task-8` → { "task_id": "Task-8", "title": "Task-8", "status": "planned", "client_name": "Cortex Intelligence", "required_prestige"…
- $ `yc-bench task assign --task-id Task-8 --employees Emp_4,Emp_8,Emp_2` → { "task_id": "Task-8", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_2" ], "total_assigned": [ "Emp_4"…
- $ `yc-bench task accept --task-id Task-183` → { "task_id": "Task-183", "status": "planned", "accepted_at": "2025-01-08T12:09:26.709215", "deadline": "2025-01-20T12:09…
- $ `yc-bench task accept --task-id Task-191` → { "task_id": "Task-191", "status": "planned", "accepted_at": "2025-01-08T12:09:26.709215", "deadline": "2025-01-17T12:09…
- $ `yc-bench task assign --task-id Task-183 --employees Emp_6,Emp_1,Emp_3` → { "task_id": "Task-183", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_1", "Emp_3" ], "total_assigned": [ "Emp_…
- $ `yc-bench task assign --task-id Task-191 --employees Emp_7,Emp_5` → { "task_id": "Task-191", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_5" ], "total_assigned": [ "Emp_7", "Emp_…
- $ `yc-bench task dispatch --task-id Task-8` → { "task_id": "Task-8", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_4", "Emp_2", "Emp_8" ] }
- $ `yc-bench task dispatch --task-id Task-183` → { "task_id": "Task-183", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_3", "Emp_1", "Emp_6" ] …
- $ `yc-bench task dispatch --task-id Task-191` → { "task_id": "Task-191", "status": "active", "assignment_count": 2, "assigned_employees": [ "Emp_7", "Emp_5" ] }
- $ `yc-bench task inspect --task-id Task-191` → { "task_id": "Task-191", "title": "Task-191", "status": "active", "client_name": "Equinox Labs", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-183` → { "task_id": "Task-183", "title": "Task-183", "status": "active", "client_name": "Prism Analytics", "required_prestige":…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 1.582, "tasks_succeeded": 1, "t…
- $ `yc-bench task cancel --task-id Task-191 --reason "Scope inflated 4x after accept"` → { "task_id": "Task-191", "status": "cancelled", "reason": "Scope inflated 4x after accept", "cancel_penalty_per_domain":…
- $ `yc-bench task accept --task-id Task-1` → { "task_id": "Task-1", "status": "planned", "accepted_at": "2025-01-08T12:09:26.709215", "deadline": "2025-01-17T12:09:2…
- $ `yc-bench task inspect --task-id Task-1` → { "task_id": "Task-1", "title": "Task-1", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1, "…
- $ `yc-bench task assign --task-id Task-1 --employees Emp_7,Emp_5,Emp_2` → { "task_id": "Task-1", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_5", "Emp_2" ], "total_assigned": [ "Emp_7"…
- $ `yc-bench task --help` → Usage: yc-bench task [OPTIONS] COMMAND [ARGS]... Task management commands. ╭─ Options ──────────────────────────────────…
- $ `yc-bench task dispatch --task-id Task-1` → { "task_id": "Task-1", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_7", "Emp_5", "Emp_2" ] }

**Note**

> I cancelled one task that was going to miss its deadline and one I had just taken on, and now have three tasks running. Funds are $229k after two successful tasks.
> 
> - **Done:** Task-128 (Cortex) and Task-162 (Stratos) both finished 30h early and paid $29.4k in total.
> - **Cancelled:** Task-10 (Vanguard) was 35% done with about 30h left, so it couldn't finish. I also cancelled Task-191 (Equinox) right after accepting, because its work grew to 4x the listed amount once accepted. Prestige drops only 0.051–0.165 per domain, and none was lost here because we're at the minimum of 1.
> - **Running:** Task-8 (Cortex research, due Jan 17) with Emp_4, Emp_8 and Emp_2; Task-183 (Prism data_environment, due Jan 20) with Emp_6, Emp_1 and Emp_3; Task-1 (Helix inference, due Jan 17, risky) with Emp_7, Emp_5 and Emp_2. There's no unassign command, so Emp_2 is split between Task-8 and Task-1.
> - **Lessons:** Vanguard and Equinox inflate work about 4x after accept, so avoid them, and always inspect the work amount right after accepting. Cortex cut it after one completed task. Work speed is roughly 8–11 units per day for each point of skill rate.

done, 15 steps, 16 model calls, $0.8981 (total $1.1066)

**Memory it saw:** 1 facts, 2 recalled episodes
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.

**Events when time advanced**

- task_completed: {"task_id": "62c03b3d-690e-4038-ae50-6366377f5644", "task_title": "Task-8", "client_name": "Cortex Intelligence", "success": true, "funds_delta_usd": 18530.02, "listed_reward_usd": 18530.02, "trust_delta": 0.9330461315069047, "deadline_margin": "ahead by 23h", "employees_assigned": 3, "salary_bump_total_usd": 148.1, "bankrupt": false}
- task_completed: {"task_id": "f14cd761-0caa-49c3-a8a1-629ef76fe252", "task_title": "Task-183", "client_name": "Prism Analytics", "success": true, "funds_delta_usd": 17380.37, "listed_reward_usd": 17380.37, "trust_delta": 1.6, "deadline_margin": "ahead by 95h", "employees_assigned": 3, "salary_bump_total_usd": 143.69, "bankrupt": false}
- task_completed: {"task_id": "e61c31e3-60aa-471e-9e18-a41538a095f2", "task_title": "Task-1", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 13550.68, "listed_reward_usd": 13550.68, "trust_delta": 1.6, "deadline_margin": "ahead by 23h", "employees_assigned": 3, "salary_bump_total_usd": 126.8, "bankrupt": false}

## Checkpoint 3 · 2025-01-16T12:58:01.944506

Funds $278,852.11 → $323,490.49, sim time → 2025-01-22T17:50:04.774609

**Commands**

- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 403260, "skill_rates": { "data_environ…
- $ `yc-bench task accept --task-id Task-110` → { "task_id": "Task-110", "status": "planned", "accepted_at": "2025-01-16T12:58:01.944506", "deadline": "2025-01-27T12:58…
- $ `yc-bench task accept --task-id Task-49` → { "task_id": "Task-49", "status": "planned", "accepted_at": "2025-01-16T12:58:01.944506", "deadline": "2025-01-27T12:58:…
- $ `yc-bench task accept --task-id Task-174` → { "task_id": "Task-174", "status": "planned", "accepted_at": "2025-01-16T12:58:01.944506", "deadline": "2025-01-27T12:58…
- $ `yc-bench task inspect --task-id Task-110` → { "task_id": "Task-110", "title": "Task-110", "status": "planned", "client_name": "Cortex Intelligence", "required_prest…
- $ `yc-bench task inspect --task-id Task-49` → { "task_id": "Task-49", "title": "Task-49", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-174` → { "task_id": "Task-174", "title": "Task-174", "status": "planned", "client_name": "Stratos Cloud", "required_prestige": …
- $ `yc-bench task assign --task-id Task-110 --employees Emp_7,Emp_2,Emp_5` → { "task_id": "Task-110", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_2", "Emp_5" ], "total_assigned": [ "Emp_…
- $ `yc-bench task assign --task-id Task-49 --employees Emp_4,Emp_8,Emp_3` → { "task_id": "Task-49", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_3" ], "total_assigned": [ "Emp_3…
- $ `yc-bench task assign --task-id Task-174 --employees Emp_6,Emp_1` → { "task_id": "Task-174", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_1" ], "total_assigned": [ "Emp_1", "Emp_…
- $ `yc-bench task dispatch --task-id Task-110` → { "task_id": "Task-110", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_7", "Emp_5", "Emp_2" ] …
- $ `yc-bench task dispatch --task-id Task-49` → { "task_id": "Task-49", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_3", "Emp_4", "Emp_8" ] }
- $ `yc-bench task dispatch --task-id Task-174` → { "task_id": "Task-174", "status": "active", "assignment_count": 2, "assigned_employees": [ "Emp_1", "Emp_6" ] }

**Note**

> I have three tasks running, all due 2025-01-27 12:58. Funds are $278.9k after all three previous tasks (Task-8, Task-183, Task-1) finished early and paid $49.5k together.
> - **Task-110** (Cortex inference, $16.9k): Emp_7, Emp_2 and Emp_5.
> - **Task-49** (Helix research, $16.5k): Emp_4, Emp_8 and Emp_3.
> - **Task-174** (Stratos data_environment, $11.2k): Emp_6 and Emp_1.
> 
> What I learned: after accepting, the work came in lower than listed on all three: Cortex 851→646, Helix 798→670 and Stratos 661→563. Our past success with these clients seems to be cutting the work, which makes them worth sticking with. I'm still avoiding Vanguard and Equinox, and next time I want to try Prism's training tasks.

done, 6 steps, 7 model calls, $0.2945 (total $1.4011)

**Memory it saw:** 8 facts, 4 recalled episodes
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.
- Throughput: teams of 3 employees finished two completed tasks 30 hours ahead of their deadlines.
- Cortex Intelligence: Task-128 was completed 30 hours ahead of its deadline and paid in full.
- Stratos Cloud: Task-162 was completed 30 hours ahead of its deadline and paid in full.
- Rule: cancellation penalty: cancelling an accepted task lowered prestige in that domain by about 0.05 to 0.17, and prestige does not drop below 1.
- Rule: work inspection: check the actual work amount immediately after accepting a task, since some clients inflate it after acceptance.

**Events when time advanced**

- task_completed: {"task_id": "38934e31-105c-4920-87dd-7f1dfc88411a", "task_title": "Task-110", "client_name": "Cortex Intelligence", "success": true, "funds_delta_usd": 16932.52, "listed_reward_usd": 16932.52, "trust_delta": 0.6170039063049115, "deadline_margin": "ahead by 115h", "employees_assigned": 3, "salary_bump_total_usd": 128.1, "bankrupt": false}
- task_completed: {"task_id": "0041a7f1-4216-4666-9278-6eb920bbd138", "task_title": "Task-49", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 16478.64, "listed_reward_usd": 16478.64, "trust_delta": 0.9266371280514936, "deadline_margin": "ahead by 115h", "employees_assigned": 3, "salary_bump_total_usd": 141.61, "bankrupt": false}
- task_completed: {"task_id": "d239d2bc-cc8a-4aef-ae5a-144cab5399d0", "task_title": "Task-174", "client_name": "Stratos Cloud", "success": true, "funds_delta_usd": 11227.22, "listed_reward_usd": 11227.22, "trust_delta": 0.9848448539010397, "deadline_margin": "ahead by 115h", "employees_assigned": 2, "salary_bump_total_usd": 120.41, "bankrupt": false}

## Checkpoint 4 · 2025-01-22T17:50:04.774609

Funds $323,490.49 → $353,012.44, sim time → 2025-01-28T17:22:52.711054

**Commands**

- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 406260, "skill_rates": { "data_environ…
- $ `yc-bench task accept --task-id Task-85` → { "task_id": "Task-85", "status": "planned", "accepted_at": "2025-01-22T17:50:04.774609", "deadline": "2025-01-31T17:50:…
- $ `yc-bench task accept --task-id Task-31` → { "task_id": "Task-31", "status": "planned", "accepted_at": "2025-01-22T17:50:04.774609", "deadline": "2025-01-31T17:50:…
- $ `yc-bench task accept --task-id Task-18` → { "task_id": "Task-18", "status": "planned", "accepted_at": "2025-01-22T17:50:04.774609", "deadline": "2025-01-31T17:50:…
- $ `yc-bench task inspect --task-id Task-85` → { "task_id": "Task-85", "title": "Task-85", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-31` → { "task_id": "Task-31", "title": "Task-31", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-18` → { "task_id": "Task-18", "title": "Task-18", "status": "planned", "client_name": "Stratos Cloud", "required_prestige": 1,…
- $ `yc-bench task assign --task-id Task-85 --employees Emp_7,Emp_2,Emp_5` → { "task_id": "Task-85", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_2", "Emp_5" ], "total_assigned": [ "Emp_7…
- $ `yc-bench task assign --task-id Task-31 --employees Emp_4,Emp_8,Emp_3` → { "task_id": "Task-31", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_3" ], "total_assigned": [ "Emp_3…
- $ `yc-bench task assign --task-id Task-18 --employees Emp_6,Emp_1` → { "task_id": "Task-18", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_1" ], "total_assigned": [ "Emp_1", "Emp_6…
- $ `yc-bench task dispatch --task-id Task-85` → { "task_id": "Task-85", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_7", "Emp_5", "Emp_2" ] }
- $ `yc-bench task dispatch --task-id Task-31` → { "task_id": "Task-31", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_3", "Emp_4", "Emp_8" ] }
- $ `yc-bench task dispatch --task-id Task-18` → { "task_id": "Task-18", "status": "active", "assignment_count": 2, "assigned_employees": [ "Emp_1", "Emp_6" ] }

**Note**

> I have three tasks running, all due 2025-01-31 17:50. Funds are $323.5k after last round's Task-110, Task-49 and Task-174 all paid in full, 115h early.
> - **Task-85** (Helix inference, $15.6k): Emp_7, Emp_2 and Emp_5 on 596 units (listed 789). Should finish with time to spare.
> - **Task-31** (Helix research, $15.7k): Emp_4, Emp_8 and Emp_3 on 935 units (listed 1236). This is the tight one: going by this team's last task, it needs about 8.6 of the 9 days.
> - **Task-18** (Stratos data_environment, $14k): Emp_6 and Emp_1 on 657 units (listed 861), about 7.2 days of work.
> 
> What I learned: the work came in about 24% under the listed amount on all three, and trust 2 opened up Helix and Stratos tasks. I'm still avoiding Vanguard and Equinox, and Prism's training tasks are next to try.

done, 6 steps, 7 model calls, $0.3238 (total $1.7249)

**Memory it saw:** 10 facts, 5 recalled episodes
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Helix Systems: Task-1 completed 23 hours ahead of its deadline and paid in full.
- Stratos Cloud: work amount came in lower than listed after acceptance on a recent task (661 to 563 units).
- Helix Systems: work amount came in lower than listed after acceptance on a recent task (798 to 670 units).
- Cortex Intelligence: Task-8 completed 23 hours ahead of its deadline and paid in full, so it has two on-time completions.
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Cortex Intelligence: work amount came in lower than listed after acceptance on a recent task (851 to 646 units).
- Rule: work inspection: check the actual work amount immediately after accepting a task, since some clients inflate it after acceptance.

**Events when time advanced**

- task_completed: {"task_id": "94272afe-d2bb-4839-a400-e503e3b9ce06", "task_title": "Task-85", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 15552.25, "listed_reward_usd": 15552.25, "trust_delta": 0.6065522579764417, "deadline_margin": "ahead by 72h", "employees_assigned": 3, "salary_bump_total_usd": 129.4, "bankrupt": false}
- task_completed: {"task_id": "9979e29c-78ca-426c-bee3-165fafb18cb3", "task_title": "Task-18", "client_name": "Stratos Cloud", "success": true, "funds_delta_usd": 13969.7, "listed_reward_usd": 13969.7, "trust_delta": 0.6366721901889543, "deadline_margin": "ahead by 72h", "employees_assigned": 2, "salary_bump_total_usd": 121.41, "bankrupt": false}

## Checkpoint 5 · 2025-01-28T17:22:52.711054

Funds $353,012.44 → $368,670.78, sim time → 2025-01-29T13:05:55.447734

**Commands**

- $ `yc-bench task list --status active` → { "count": 1, "tasks": [ { "task_id": "Task-31", "title": "Task-31", "status": "active", "client_name": "Helix Systems",…
- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 409260, "skill_rates": { "data_environ…
- $ `yc-bench task accept --task-id Task-199` → { "task_id": "Task-199", "status": "planned", "accepted_at": "2025-01-28T17:22:52.711054", "deadline": "2025-02-06T17:22…
- $ `yc-bench task accept --task-id Task-84` → { "task_id": "Task-84", "status": "planned", "accepted_at": "2025-01-28T17:22:52.711054", "deadline": "2025-02-06T17:22:…
- $ `yc-bench task inspect --task-id Task-84` → { "task_id": "Task-84", "title": "Task-84", "status": "planned", "client_name": "Stratos Cloud", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-199` → { "task_id": "Task-199", "title": "Task-199", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task assign --task-id Task-84 --employees Emp_6,Emp_1` → { "task_id": "Task-84", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_1" ], "total_assigned": [ "Emp_1", "Emp_6…
- $ `yc-bench task assign --task-id Task-199 --employees Emp_7,Emp_2,Emp_5` → { "task_id": "Task-199", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_2", "Emp_5" ], "total_assigned": [ "Emp_…
- $ `yc-bench task accept --task-id Task-25` → { "task_id": "Task-25", "status": "planned", "accepted_at": "2025-01-28T17:22:52.711054", "deadline": "2025-02-06T17:22:…
- $ `yc-bench task assign --task-id Task-25 --employees Emp_4,Emp_8,Emp_3` → { "task_id": "Task-25", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_3" ], "total_assigned": [ "Emp_3…
- $ `yc-bench task dispatch --task-id Task-84` → { "task_id": "Task-84", "status": "active", "assignment_count": 2, "assigned_employees": [ "Emp_1", "Emp_6" ] }
- $ `yc-bench task dispatch --task-id Task-199` → { "task_id": "Task-199", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_7", "Emp_5", "Emp_2" ] …
- $ `yc-bench task dispatch --task-id Task-25` → { "task_id": "Task-25", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_3", "Emp_4", "Emp_8" ] }
- $ `yc-bench task inspect --task-id Task-25` → { "task_id": "Task-25", "title": "Task-25", "status": "active", "client_name": "Helix Systems", "required_prestige": 1, …

**Note**

> I now have four tasks running and funds are $353k. Task-85 and Task-18 both paid in full (72h early, about $29.5k together). The three new tasks are all due 2025-02-06 17:22.
> - **Task-31** (Helix research): 96% done, due Jan 31. Its team, Emp_4, Emp_8 and Emp_3, is now also on Task-25, so their speed is split between the two until Task-31 finishes. With so little left, Task-31 should still make its deadline.
> - **Task-199** (Helix inference, $14.2k, needed trust 2): Emp_7, Emp_2 and Emp_5 on 426 units (listed 607).
> - **Task-84** (Stratos data_environment, $12.5k): Emp_6 and Emp_1 on 758 units (listed 1073). This pair did 657 units in about 6 days, so this should take about 7 of the 9 days.
> - **Task-25** (Helix research, $12.4k): Emp_4, Emp_8 and Emp_3 on 420 units (listed 598).
> 
> What I learned: after accepting, work came in about 30% under the listed amount with Helix and Stratos. I'm still avoiding Vanguard and Equinox, and Prism's training tasks are still untried.

done, 7 steps, 8 model calls, $0.4128 (total $2.1377)

**Memory it saw:** 10 facts, 5 recalled episodes
- Helix Systems: work amount came in lower than listed after acceptance on Task-85 (789 to 596 units) and Task-31 (1236 to 935 units).
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Rule: client trust: completing tasks on time raises client trust, and reaching trust level 2 unlocked more tasks from Helix Systems and Stratos Cloud.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Cortex Intelligence: work amount came in lower than listed after acceptance on a recent task (851 to 646 units).
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Helix Systems: Task-49 completed 115 hours ahead of its deadline and paid in full, so it has three on-time completions.
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.
- Stratos Cloud: Task-174 completed 115 hours ahead of its deadline and paid in full.

**Events when time advanced**

- task_completed: {"task_id": "017ab6d5-659e-4462-a1b4-39183337442a", "task_title": "Task-31", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 15658.34, "listed_reward_usd": 15658.34, "trust_delta": 0.41605574157009295, "deadline_margin": "ahead by 53h", "employees_assigned": 3, "salary_bump_total_usd": 142.91, "bankrupt": false}

## Checkpoint 6 · 2025-01-29T13:05:55.447734

Funds $368,670.78 → $382,890.99, sim time → 2025-01-30T15:33:06.611374

**Commands**

- $ `yc-bench task list --status active` → { "count": 3, "tasks": [ { "task_id": "Task-25", "title": "Task-25", "status": "active", "client_name": "Helix Systems",…

**Note**

> I didn't start anything new this checkpoint. All three running tasks are on track, and all 8 employees are already busy.
> 
> - **Done:** Task-31 (Helix research) paid $15.7k in full, 53h early. Funds are $368.7k and payroll is $39.4k a month.
> - **Running, all due Feb 6:** Task-199 (Helix inference) is 48% done and should finish in about a day. Task-84 (Stratos data_environment) is 22% done and Task-25 (Helix research) is 19% done. None are marked at risk.
> - **Why I held off:** a fourth task would split someone's speed. Once Task-199 finishes, its team (Emp_7, Emp_2, Emp_5) is free for a new Helix or Stratos task, or my first try at Prism's training tasks.
> - **Still true:** avoid Vanguard and Equinox, and check the work amount right after accepting.

done, 2 steps, 3 model calls, $0.0718 (total $2.2096)

**Memory it saw:** 10 facts, 6 recalled episodes
- Helix Systems: work amount came in lower than listed after acceptance on Task-85 (789 to 596 units) and Task-31 (1236 to 935 units).
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Rule: client trust: completing tasks on time raises client trust, and reaching trust level 2 unlocked more tasks from Helix Systems and Stratos Cloud.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Throughput: a team of 2 employees finished Task-18 (657 units) 72 hours ahead of its deadline.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).
- Throughput: a team of 3 employees finished Task-85 (596 units) 72 hours ahead of its deadline.
- Helix Systems: Task-85 completed 72 hours ahead of its deadline and paid in full, giving four on-time completions.
- Cortex Intelligence: work amount came in lower than listed after acceptance on a recent task (851 to 646 units).

**Events when time advanced**

- task_completed: {"task_id": "0b6c42e8-1502-4bf2-8759-5fce4ec6f9fa", "task_title": "Task-199", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 14220.21, "listed_reward_usd": 14220.21, "trust_delta": 0.29808897776281507, "deadline_margin": "ahead by 170h", "employees_assigned": 3, "salary_bump_total_usd": 130.7, "bankrupt": false}

## Checkpoint 7 · 2025-01-30T15:33:06.611374

Funds $382,890.99 → $395,268.82, sim time → 2025-01-30T17:07:46.991249

**Commands**

- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-133", "client_name": "Helix Systems", "required_p…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 409260, "skill_rates": { "data_environ…
- $ `yc-bench task accept --task-id Task-133` → { "task_id": "Task-133", "status": "planned", "accepted_at": "2025-01-30T15:33:06.611374", "deadline": "2025-02-10T15:33…
- $ `yc-bench task inspect --task-id Task-133` → { "task_id": "Task-133", "title": "Task-133", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task assign --task-id Task-133 --employees Emp_7,Emp_2,Emp_5` → { "task_id": "Task-133", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_2", "Emp_5" ], "total_assigned": [ "Emp_…
- $ `yc-bench task dispatch --task-id Task-133` → { "task_id": "Task-133", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_7", "Emp_5", "Emp_2" ] …

**Note**

> I started one new task. All 8 employees are now on one task each, so nobody's speed is split.
> 
> - **Done:** Task-199 (Helix inference) paid $14.2k in full, 170h early. Funds are $382.9k and payroll is $39.5k a month.
> - **New:** Task-133 (Helix inference, $21.6k, due Feb 10) with Emp_7, Emp_2 and Emp_5. It needs Helix trust 3, and we already have that. After accepting, the work dropped from 1130 to 715 units (about 37% less), so it should finish well before the deadline.
> - **Still running:** Task-84 (Stratos data_environment) and Task-25 (Helix research), both due Feb 6.
> - **Learned:** Helix trust 3 opens bigger-paying tasks, and the cut in work after accepting keeps getting larger. Still avoiding Vanguard and Equinox, and Prism's training tasks are still untried.

done, 5 steps, 6 model calls, $0.2478 (total $2.4574)

**Memory it saw:** 10 facts, 5 recalled episodes
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Rule: client trust: completing tasks on time raises client trust, and reaching trust level 2 unlocked more tasks from Helix Systems and Stratos Cloud.
- Helix Systems: work amount came in lower than listed after acceptance on Task-85 (789 to 596 units) and Task-31 (1236 to 935 units).
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Helix Systems: Task-31 completed 53 hours ahead of its deadline and paid in full, after its work amount dropped from 1236 to 935 units.
- Helix Systems: Task-85 completed 72 hours ahead of its deadline and paid in full, giving four on-time completions.
- Throughput: a team of 2 employees finished Task-18 (657 units) 72 hours ahead of its deadline.
- Stratos Cloud: Task-18 completed 72 hours ahead of its deadline and paid in full, giving two on-time completions.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).

**Events when time advanced**

- task_completed: {"task_id": "3528adea-801b-4824-b66e-4ecac992d0c2", "task_title": "Task-25", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 12377.83, "listed_reward_usd": 12377.83, "trust_delta": 0.22049498719453942, "deadline_margin": "ahead by 168h", "employees_assigned": 3, "salary_bump_total_usd": 144.21, "bankrupt": false}

## Checkpoint 8 · 2025-01-30T17:07:46.991249

Funds $395,268.82 → $355,633.79, sim time → 2025-02-03T09:00:00

**Commands**

- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench client list` → { "count": 6, "clients": [ { "client_id": "3b0742f5-cc3b-4d8f-acbf-830c8c8805e5", "name": "Cortex Intelligence", "trust_…
- $ `yc-bench market browse --domain research --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench task accept --task-id Task-163` → { "task_id": "Task-163", "status": "planned", "accepted_at": "2025-01-30T17:07:46.991249", "deadline": "2025-02-10T17:07…
- $ `yc-bench task inspect --task-id Task-163` → { "task_id": "Task-163", "title": "Task-163", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task assign --task-id Task-163 --employees Emp_4,Emp_8,Emp_3` → { "task_id": "Task-163", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_3" ], "total_assigned": [ "Emp_…
- $ `yc-bench task dispatch --task-id Task-163` → { "task_id": "Task-163", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_3", "Emp_4", "Emp_8" ] …

**Note**

> I started Task-163 with the team that finished Task-25, so all 8 employees are on one task each again.
> 
> - **Done:** Task-25 (Helix research) paid $12.4k in full, 168h early. Funds are $395.3k and payroll is $39.6k a month.
> - **New:** Task-163 (Helix inference, $15.6k, due Feb 10) with Emp_4, Emp_8 and Emp_3. After accepting, the work dropped from 1294 to 791 units (39% less), which should leave plenty of time.
> - **Still running:** Task-133 (Helix inference, due Feb 10) and Task-84 (Stratos data_environment, due Feb 6).
> - **Learned:** Helix trust is now 3.89 and the cut in work after accepting is holding near 40%. Most of the market is Vanguard and Equinox tasks, which I'm still avoiding. Prism's training tasks are still untried (Prism trust is 1.31).

done, 6 steps, 7 model calls, $0.3052 (total $2.7625)

**Memory it saw:** 10 facts, 5 recalled episodes
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Rule: client trust: reaching Helix trust level 3 unlocked bigger-paying Helix Systems tasks.
- Helix Systems: Task-133's work amount came in lower after acceptance (1130 to 715 units).
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Helix Systems: Task-199 completed 170 hours ahead of its deadline and paid in full, with a team of 3 employees, giving five on-time completions.
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).
- Throughput: a team of 2 employees finished Task-18 (657 units) 72 hours ahead of its deadline.
- Helix Systems: Task-31 completed 53 hours ahead of its deadline and paid in full, after its work amount dropped from 1236 to 935 units.

**Events when time advanced**

- monthly_payroll: {"funds_after_usd": 355633.79}

## Checkpoint 9 · 2025-02-03T09:00:00

Funds $355,633.79 → $368,117.11, sim time → 2025-02-03T09:00:00

**Commands**

- $ `yc-bench task list` → { "count": 18, "tasks": [ { "task_id": "Task-163", "title": "Task-163", "status": "active", "client_name": "Helix System…
- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench task accept --task-id Task-145` → { "task_id": "Task-145", "status": "planned", "accepted_at": "2025-02-03T09:00:00", "deadline": "2025-02-11T18:00:00", "…
- $ `yc-bench task inspect --task-id Task-145` → { "task_id": "Task-145", "title": "Task-145", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task assign --task-id Task-145 --employees Emp_6,Emp_1` → { "task_id": "Task-145", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_1" ], "total_assigned": [ "Emp_1", "Emp_…
- $ `yc-bench task dispatch --task-id Task-145` → { "task_id": "Task-145", "status": "active", "assignment_count": 2, "assigned_employees": [ "Emp_1", "Emp_6" ] }

**Note**

> I started Task-145 for Emp_6 and Emp_1. Their current job, Task-84, shows 100% done but hasn't been marked complete yet.
> 
> - **Payroll:** this month's payroll of $39.6k came out, so funds are $355.6k (about 9 months of runway).
> - **New:** Task-145 (Helix inference, $13.6k, due Feb 11) with Emp_6 and Emp_1. After accepting, the work dropped from 849 to 521 units (39% less). This pair did 657 units in about 6 days, so this should finish well before the deadline.
> - **Running:** Task-133 (Helix inference, 67% done) and Task-163 (Helix inference, 33% done) are both due Feb 10 and neither is marked at risk.
> - **Learned:** Helix keeps cutting work by about 39% after acceptance. Most of the market is still Vanguard and Equinox tasks, which I'm avoiding. Prism's training tasks (Task-39 and Task-99) are options for the next team that frees up.

done, 6 steps, 7 model calls, $0.2657 (total $3.0282)

**Memory it saw:** 10 facts, 5 recalled episodes
- Helix Systems: work amount came in lower after acceptance on Task-25 and Task-133, with cuts of roughly 37% to 40% in recent tasks.
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Rule: client trust: Helix Systems trust grows with each on-time completion, and trust 3 is needed for Helix inference tasks.
- Helix Systems: Task-25 completed 168 hours ahead of its deadline and paid in full, with a team of 3 employees.
- Helix Systems: Task-31 completed 53 hours ahead of its deadline and paid in full, after its work amount dropped from 1236 to 935 units.
- Throughput: a team of 2 employees finished Task-18 (657 units) 72 hours ahead of its deadline.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).
- Cortex Intelligence: work amount came in lower than listed after acceptance on a recent task (851 to 646 units).

**Events when time advanced**

- task_completed: {"task_id": "195e9fc0-0b14-4f34-9b83-e15e59c51be5", "task_title": "Task-84", "client_name": "Stratos Cloud", "success": true, "funds_delta_usd": 12483.32, "listed_reward_usd": 12483.32, "trust_delta": 0.45841050943904005, "deadline_margin": "ahead by 80h", "employees_assigned": 2, "salary_bump_total_usd": 122.41, "bankrupt": false}

## Checkpoint 10 · 2025-02-03T09:00:00

Funds $368,117.11 → $389,696.90, sim time → 2025-02-04T11:26:21.885783

**Commands**

- $ `yc-bench task list --status active` → { "count": 3, "tasks": [ { "task_id": "Task-145", "title": "Task-145", "status": "active", "client_name": "Helix Systems…

**Note**

> I didn't start anything new this checkpoint. All 8 employees are on one task each, so a fourth task would split someone's speed.
> 
> - **Done:** Task-84 (Stratos data_environment) paid $12.5k in full, 80h early. Funds are $368.1k and payroll is $39.7k a month.
> - **Running (none at risk):** Task-133 (Helix inference, Emp_7, Emp_2, Emp_5) is 67% done, due Feb 10. Task-163 (Helix inference, Emp_4, Emp_8, Emp_3) is 33% done, due Feb 10. Task-145 (Helix inference, Emp_6, Emp_1) is at 0%, due Feb 11.
> - **Next:** when Task-133's team frees up, they can try Prism's training tasks or take another Helix task that needs trust 3.
> - **Still true:** avoid Vanguard and Equinox, and check the work amount right after accepting.

done, 2 steps, 3 model calls, $0.0626 (total $3.0908)

**Memory it saw:** 10 facts, 6 recalled episodes
- Helix Systems: work amount came in lower after acceptance on Task-25, Task-31, Task-133, Task-163 and Task-145, with cuts of roughly 37% to 40% each time, so the work amount should be checked right after accepting.
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.
- Rule: client trust: Helix Systems trust grows with each on-time completion, and trust 3 is needed for Helix inference tasks.
- Helix Systems: Task-25 completed 168 hours ahead of its deadline and paid in full, with a team of 3 employees.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).
- Throughput: a team of 2 employees finished Task-18 (657 units) 72 hours ahead of its deadline.
- Helix Systems: Task-31 completed 53 hours ahead of its deadline and paid in full, after its work amount dropped from 1236 to 935 units.

**Events when time advanced**

- task_completed: {"task_id": "2fa4169b-c810-4f2e-9264-7523a929b335", "task_title": "Task-133", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 21579.79, "listed_reward_usd": 21579.79, "trust_delta": 0.1822727626388536, "deadline_margin": "ahead by 148h", "employees_assigned": 3, "salary_bump_total_usd": 132.0, "bankrupt": false}

## Summary

- terminal reason: max_checkpoints
- checkpoints: 10, sim time 2025-02-04T11:26:21.885783
- final funds: $389,696.90
- cost: $3.0908 over 71 model calls

**Facts in memory at the end (15)**

- Stratos Cloud: Task-84 completed 80 hours ahead of its deadline and paid in full, with a team of 2 employees.
- Helix Systems: work amount came in lower after acceptance on Task-25, Task-31, Task-133, Task-163 and Task-145, with cuts of roughly 37% to 40% each time, so the work amount should be checked right after accepting.
- Rule: client trust: Helix Systems trust grows with each on-time completion, and trust 3 is needed for Helix inference tasks.
- Throughput: 3 employees finished Task-25 (research) 168 hours ahead of its deadline.
- Helix Systems: Task-31 completed 53 hours ahead of its deadline and paid in full, after its work amount dropped from 1236 to 935 units.
- Throughput: a team of 2 employees finished Task-18 (657 units) 72 hours ahead of its deadline.
- Stratos Cloud: Task-18 completed 72 hours ahead of its deadline and paid in full, giving two on-time completions.
- Stratos Cloud: work amount came in lower than listed after acceptance on Task-18 (861 to 657 units).
- Cortex Intelligence: work amount came in lower than listed after acceptance on a recent task (851 to 646 units).
- Throughput: teams of 3 employees finished tasks 23 to 95 hours ahead of their deadlines across Task-8, Task-183 and Task-1.
- Rule: work inspection: check the actual work amount immediately after accepting a task, since some clients inflate it after acceptance.
- Rule: cancellation penalty: cancelling an accepted task lowered prestige in that domain by about 0.05 to 0.17, and prestige does not drop below 1.
- Equinox: work grew to about 4x the listed amount after acceptance (Task-191), so the task was cancelled right after accepting.
- Vanguard ML: work grew to about 4x the listed amount after acceptance (Task-10), so the task was cancelled unfinished at 35% done.
- Rule: deadline visibility: a task's deadline is only shown after the task is accepted, so work hours must be checked against the deadline before committing.
