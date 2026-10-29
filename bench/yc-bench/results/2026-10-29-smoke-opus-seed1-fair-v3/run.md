# YC-Bench run: seed 1, claude-opus-5-5

- started: 2026-10-28 22:50:18
- config: default
- release: prompt_version v3, agent_model claude-opus-5-5, agent_effort medium, summarizer_model claude-haiku-5-5, max_steps 30, max_cost_usd 2.0, history_turns 10, semantic_top_k 10, episodic_top_k 5, episodic_recent_k 3, consolidate_every_n_chats 1, prompts_dir bench/yc-bench/prompts

## Checkpoint 1 · 2025-01-01T09:00:00

Funds $200,000.00 → $214,161.68, sim time → 2025-01-07T13:12:02.102993

**Commands**

- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 397260, "skill_rates": { "data_environ…
- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-10", "client_name": "Vanguard ML", "required_pres…
- $ `yc-bench task inspect --task-id Task-10` → { "task_id": "Task-10", "title": "Task-10", "status": "market", "client_name": "Vanguard ML", "required_prestige": 1, "r…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 0.0, "tasks_succeeded": 0, "tas…
- $ `yc-bench task accept --task-id Task-10` → { "task_id": "Task-10", "status": "planned", "accepted_at": "2025-01-01T09:00:00", "deadline": "2025-01-09T18:00:00", "r…
- $ `yc-bench task accept --task-id Task-162` → { "task_id": "Task-162", "status": "planned", "accepted_at": "2025-01-01T09:00:00", "deadline": "2025-01-09T18:00:00", "…
- $ `yc-bench task assign --task-id Task-10 --employees Emp_4,Emp_2,Emp_8` → { "task_id": "Task-10", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_2", "Emp_8" ], "total_assigned": [ "Emp_4…
- $ `yc-bench task assign --task-id Task-162 --employees Emp_6,Emp_7,Emp_1,Emp_3` → { "task_id": "Task-162", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_7", "Emp_1", "Emp_3" ], "total_assigned"…
- $ `yc-bench task dispatch --task-id Task-10` → { "task_id": "Task-10", "status": "active", "assignment_count": 3, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_2" ] }
- $ `yc-bench task dispatch --task-id Task-162` → { "task_id": "Task-162", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_1", "Emp_3", "Emp_6", "…
- $ `yc-bench task inspect --task-id Task-10` → { "task_id": "Task-10", "title": "Task-10", "status": "active", "client_name": "Vanguard ML", "required_prestige": 1, "r…
- $ `yc-bench task inspect --task-id Task-162` → { "task_id": "Task-162", "title": "Task-162", "status": "active", "client_name": "Stratos Cloud", "required_prestige": 1…

**Note**

> I've started two tasks. Task-10 got four times bigger after I accepted it, so I'll move people onto it when Task-162 finishes.
> 
> - **Running:** Task-10 for Vanguard ML (research, $20,919.43, due Jan 9) is staffed by Emp_4, Emp_2 and Emp_8. Task-162 for Stratos Cloud (data_environment, $14,161.68, due Jan 9) is staffed by Emp_6, Emp_7, Emp_1 and Emp_3. Emp_5 is idle because all of their skills are weak.
> - **Problem:** Task-10's research requirement jumped from 564 to 2,256 units once accepted. At about 13.9/hr that's roughly 160 hours, so it may miss the deadline. I'm guessing Vanguard inflates scope; its client history is still empty, so I can't confirm.
> - **Next:** Task-162 should finish in about 40 work-hours. I'll then put Emp_6 and Emp_7 on Task-10. From now on I'll re-check task size right after accepting anything.
> - **Team:** Emp_4 is strongest at research (6.32), Emp_6 and Emp_7 at data_environment (6.67 / 6.13), and Emp_4 and Emp_7 at inference (5.85 / 5.63).

done, 8 steps, 9 model calls, $0.3262 (total $0.3262)

**Memory it saw:** 0 facts, 0 recalled episodes

**Events when time advanced**

- task_completed: {"task_id": "d9361a5f-ef7d-451a-b2ed-75dd90a9493d", "task_title": "Task-162", "client_name": "Stratos Cloud", "success": true, "funds_delta_usd": 14161.68, "listed_reward_usd": 14161.68, "trust_delta": 1.6, "deadline_margin": "ahead by 53h", "employees_assigned": 4, "salary_bump_total_usd": 209.56, "bankrupt": false}

## Checkpoint 2 · 2025-01-07T13:12:02.102993

Funds $214,161.68 → $250,072.07, sim time → 2025-01-15T10:56:23.138041

**Commands**

- $ `yc-bench task list` → { "count": 2, "tasks": [ { "task_id": "Task-10", "title": "Task-10", "status": "active", "client_name": "Vanguard ML", "…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 400260, "skill_rates": { "data_environ…
- $ `yc-bench task inspect --task-id Task-10` → { "task_id": "Task-10", "title": "Task-10", "status": "active", "client_name": "Vanguard ML", "required_prestige": 1, "r…
- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-8", "client_name": "Cortex Intelligence", "requir…
- $ `yc-bench task inspect --task-id Task-8` → { "task_id": "Task-8", "title": "Task-8", "status": "market", "client_name": "Cortex Intelligence", "required_prestige":…
- $ `yc-bench task inspect --task-id Task-183` → { "task_id": "Task-183", "title": "Task-183", "status": "market", "client_name": "Prism Analytics", "required_prestige":…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 0.0, "tasks_succeeded": 0, "tas…
- $ `yc-bench task accept --task-id Task-183` → { "task_id": "Task-183", "status": "planned", "accepted_at": "2025-01-07T13:12:02.102993", "deadline": "2025-01-17T13:12…
- $ `yc-bench task inspect --task-id Task-183` → { "task_id": "Task-183", "title": "Task-183", "status": "planned", "client_name": "Prism Analytics", "required_prestige"…
- $ `yc-bench task assign --task-id Task-183 --employees Emp_6,Emp_7,Emp_1,Emp_3` → { "task_id": "Task-183", "status": "planned", "newly_assigned": [ "Emp_6", "Emp_7", "Emp_1", "Emp_3" ], "total_assigned"…
- $ `yc-bench task dispatch --task-id Task-183` → { "task_id": "Task-183", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_1", "Emp_3", "Emp_6", "…
- $ `yc-bench task cancel --task-id Task-10 --reason "Scope quadrupled after acceptance; cannot meet deadline"` → { "task_id": "Task-10", "status": "cancelled", "reason": "Scope quadrupled after acceptance; cannot meet deadline", "can…
- $ `yc-bench task accept --task-id Task-8` → { "task_id": "Task-8", "status": "planned", "accepted_at": "2025-01-07T13:12:02.102993", "deadline": "2025-01-16T13:12:0…
- $ `yc-bench task inspect --task-id Task-8` → { "task_id": "Task-8", "title": "Task-8", "status": "planned", "client_name": "Cortex Intelligence", "required_prestige"…
- $ `yc-bench task assign --task-id Task-8 --employees Emp_4,Emp_2,Emp_8,Emp_5` → { "task_id": "Task-8", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_2", "Emp_8", "Emp_5" ], "total_assigned": …
- $ `yc-bench task dispatch --task-id Task-8` → { "task_id": "Task-8", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_5", "Em…

**Note**

> I cancelled Task-10 and started two new tasks, so all 8 employees are now working. Funds are $214,161.68 after Stratos Cloud paid $14,161.68 for Task-162, which finished 53 hours early.
> 
> - **Cancelled Task-10 (Vanguard ML):** it had 1,365 research units left with about 23 work hours to go. That needed about 59/hr, roughly double what the whole team can do. The cancel cost nothing because research prestige was already at its floor of 1.0. I still don't trust Vanguard ML, since the task grew 4× after I accepted it.
> - **Started Task-183 (Prism Analytics):** data_environment, 1,201 units, $17,380.37, due Jan 17. Emp_6, Emp_7, Emp_1 and Emp_3 are on it at about 20/hr, so roughly 60 work hours, well inside the deadline.
> - **Started Task-8 (Cortex Intelligence):** research, 783 units, $18,530.02, +0.255 prestige, due Jan 16. Emp_4, Emp_2, Emp_8 and Emp_5 are on it at about 15/hr, so roughly 52 work hours.
> - **Learned:** Neither new task changed size after I accepted it, so so far only the Vanguard ML task grew. Deadlines only show after accepting, and they've been about 9–10 days out. Stratos Cloud has been reliable (trust 1.6).

done, 10 steps, 11 model calls, $0.5115 (total $0.8377)

**Memory it saw:** 5 facts, 2 recalled episodes
- Emp_6 and Emp_7 are strongest at data_environment (skill about 6.67 and 6.13).
- Emp_4 and Emp_7 are strongest at inference (skill about 5.85 and 5.63).
- Emp_4 is strongest at research among the team (skill about 6.32).
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after the task was accepted, so task size can grow after acceptance.
- Re-check task size right after accepting a task, because requirements can change once accepted.

**Events when time advanced**

- task_completed: {"task_id": "4913cafa-44cc-4307-8b38-e1d0f84c3d03", "task_title": "Task-8", "client_name": "Cortex Intelligence", "success": true, "funds_delta_usd": 18530.02, "listed_reward_usd": 18530.02, "trust_delta": 1.6, "deadline_margin": "ahead by 26h", "employees_assigned": 4, "salary_bump_total_usd": 174.06, "bankrupt": false}
- task_completed: {"task_id": "7cf54f9c-7669-4f47-b40c-36a08b5564f8", "task_title": "Task-183", "client_name": "Prism Analytics", "success": true, "funds_delta_usd": 17380.37, "listed_reward_usd": 17380.37, "trust_delta": 1.6, "deadline_margin": "ahead by 50h", "employees_assigned": 4, "salary_bump_total_usd": 211.56, "bankrupt": false}

## Checkpoint 3 · 2025-01-15T10:56:23.138041

Funds $250,072.07 → $281,780.07, sim time → 2025-01-20T16:44:29.764415

**Commands**

- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 403260, "skill_rates": { "data_environ…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 1.582, "tasks_succeeded": 1, "t…
- $ `yc-bench task accept --task-id Task-49` → { "task_id": "Task-49", "status": "planned", "accepted_at": "2025-01-15T10:56:23.138041", "deadline": "2025-01-24T10:56:…
- $ `yc-bench task accept --task-id Task-128` → { "task_id": "Task-128", "status": "planned", "accepted_at": "2025-01-15T10:56:23.138041", "deadline": "2025-01-24T10:56…
- $ `yc-bench task inspect --task-id Task-49` → { "task_id": "Task-49", "title": "Task-49", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-128` → { "task_id": "Task-128", "title": "Task-128", "status": "planned", "client_name": "Cortex Intelligence", "required_prest…
- $ `yc-bench task assign --task-id Task-49 --employees Emp_4,Emp_2,Emp_8,Emp_1` → { "task_id": "Task-49", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_2", "Emp_8", "Emp_1" ], "total_assigned":…
- $ `yc-bench task assign --task-id Task-128 --employees Emp_7,Emp_6,Emp_3,Emp_5` → { "task_id": "Task-128", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_6", "Emp_3", "Emp_5" ], "total_assigned"…
- $ `yc-bench task dispatch --task-id Task-49` → { "task_id": "Task-49", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_1", "E…
- $ `yc-bench task dispatch --task-id Task-128` → { "task_id": "Task-128", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_5", "Emp_3", "Emp_6", "…

**Note**

> I started two new tasks, so all 8 employees are working again. Funds are $250,072.07 after Cortex Intelligence paid $18,530.02 for Task-8 (finished 26 hours early) and Prism Analytics paid $17,380.37 for Task-183 (finished 50 hours early).
> 
> - **Task-49 (Helix Systems, a new client):** research, 798 units, $16,478.64, +0.118 prestige, due Jan 24. Emp_4, Emp_2, Emp_8 and Emp_1 are on it at about 17/hr, so roughly 47 work hours. Its size didn't change after I accepted it.
> - **Task-128 (Cortex Intelligence):** inference, $15,229.36, due Jan 24. It was listed at 581 units but dropped to 489 after I accepted it, likely because we've built trust with Cortex (1.58). Emp_7, Emp_6, Emp_3 and Emp_5 are on it at about 15/hr, so roughly 33 work hours.
> - **Learned:** Trust can make a task smaller after acceptance, so going back to clients that trust us (Cortex, Prism, Stratos) pays off. No client has failed on us yet. Vanguard ML is still the only one whose task grew, so I'm still avoiding it.
> - **Pace:** We seem to get about 8–9 work hours per calendar day, so a deadline 9 days out gives roughly 70 work hours.
> - **Team:** Skills have grown: Emp_6 is now 7.7 at data_environment, Emp_7 is 7.08, and Emp_4 is 6.67 at research.

done, 6 steps, 7 model calls, $0.2974 (total $1.1351)

**Memory it saw:** 9 facts, 4 recalled episodes
- Stratos Cloud: Task-162 was completed successfully, 53 hours ahead of its deadline, and paid in full, raising trust to 1.6.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after the task was accepted, and the CEO cancelled it because it needed about double the whole team's capacity.
- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.
- Cancelling a task cost nothing when research prestige was already at its floor of 1.0.
- Re-check task size right after accepting a task, because requirements can change once accepted.
- Prism Analytics and Cortex Intelligence tasks did not change size after acceptance.
- Emp_4 is strongest at research among the team (skill about 6.32).
- Emp_6 and Emp_7 are strongest at data_environment (skill about 6.67 and 6.13).
- Emp_4 and Emp_7 are strongest at inference (skill about 5.85 and 5.63).

**Events when time advanced**

- task_completed: {"task_id": "2bda1527-be70-467f-99f9-2c67d9f47bbe", "task_title": "Task-128", "client_name": "Cortex Intelligence", "success": true, "funds_delta_usd": 15229.36, "listed_reward_usd": 15229.36, "trust_delta": 0.9230385397804366, "deadline_margin": "ahead by 90h", "employees_assigned": 4, "salary_bump_total_usd": 199.5, "bankrupt": false}
- task_completed: {"task_id": "75a0b010-0400-4bea-a156-b7e1a7ccf79d", "task_title": "Task-49", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 16478.64, "listed_reward_usd": 16478.64, "trust_delta": 1.6, "deadline_margin": "ahead by 90h", "employees_assigned": 4, "salary_bump_total_usd": 189.72, "bankrupt": false}

## Checkpoint 4 · 2025-01-20T16:44:29.764415

Funds $281,780.07 → $314,370.93, sim time → 2025-01-27T09:21:32.829862

**Commands**

- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-119", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 406260, "skill_rates": { "data_environ…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 2.44, "tasks_succeeded": 2, "ta…
- $ `yc-bench task accept --task-id Task-110` → { "task_id": "Task-110", "status": "planned", "accepted_at": "2025-01-20T16:44:29.764415", "deadline": "2025-01-29T16:44…
- $ `yc-bench task accept --task-id Task-119` → { "task_id": "Task-119", "status": "planned", "accepted_at": "2025-01-20T16:44:29.764415", "deadline": "2025-01-29T16:44…
- $ `yc-bench task inspect --task-id Task-110` → { "task_id": "Task-110", "title": "Task-110", "status": "planned", "client_name": "Cortex Intelligence", "required_prest…
- $ `yc-bench task inspect --task-id Task-119` → { "task_id": "Task-119", "title": "Task-119", "status": "planned", "client_name": "Equinox Labs", "required_prestige": 1…
- $ `yc-bench task cancel --task-id Task-119 --reason "Scope grew 4x after acceptance; infeasible"` → { "task_id": "Task-119", "status": "cancelled", "reason": "Scope grew 4x after acceptance; infeasible", "cancel_penalty_…
- $ `yc-bench task accept --task-id Task-31` → { "task_id": "Task-31", "status": "planned", "accepted_at": "2025-01-20T16:44:29.764415", "deadline": "2025-01-29T16:44:…
- $ `yc-bench task inspect --task-id Task-31` → { "task_id": "Task-31", "title": "Task-31", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task assign --task-id Task-31 --employees Emp_4,Emp_8,Emp_2,Emp_1` → { "task_id": "Task-31", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_2", "Emp_1" ], "total_assigned":…
- $ `yc-bench task assign --task-id Task-110 --employees Emp_7,Emp_6,Emp_3,Emp_5` → { "task_id": "Task-110", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_6", "Emp_3", "Emp_5" ], "total_assigned"…
- $ `yc-bench task dispatch --task-id Task-31` → { "task_id": "Task-31", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_1", "E…
- $ `yc-bench task dispatch --task-id Task-110` → { "task_id": "Task-110", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_5", "Emp_3", "Emp_6", "…

**Note**

> I started two tasks, so all 8 employees are working again (funds $281,780.07). I also accepted and then cancelled one task, which cost a small amount of research prestige.
> 
> - **Task-110 (Cortex, inference, $16,932.52, due Jan 29):** only open to us because Cortex trust is now 2.44, and it shrank from 851 to 643 units after I accepted it. Emp_7, Emp_6, Emp_3 and Emp_5 do about 17 units/hr together, so roughly 38 work hours.
> - **Task-31 (Helix, research, $15,658.34, +0.157 prestige, due Jan 29):** shrank from 1,236 to 1,038 units after I accepted it. Emp_4, Emp_8, Emp_2 and Emp_1 do about 21 units/hr together, so roughly 49 work hours.
> - **Cancelled Task-119 (Equinox Labs):** it grew 4× after I accepted it (860 → 3,440 units), which we couldn't finish in time. Cancelling cost 0.06 research prestige (1.373 → 1.313). Equinox Labs inflates scope the same way Vanguard ML does, so I'll avoid both.
> - **Learned:** Clients that trust us (Cortex, Helix) shrink tasks by about 15–25% after we accept them. Emp_4's research skill is up to 8.34 and Emp_7's inference to 6.46.

done, 9 steps, 10 model calls, $0.5021 (total $1.6373)

**Memory it saw:** 10 facts, 6 recalled episodes
- Cortex Intelligence: Task-8 was completed successfully, 26 hours ahead of its deadline, and paid in full, raising trust to 1.6.
- Cortex Intelligence: Task-128 shrank after acceptance, from 581 listed units to 489, when trust was about 1.58.
- Cortex Intelligence task sizes have otherwise stayed the same after acceptance, with Task-128 the exception.
- Vanguard ML task sizes have grown after acceptance, so new Vanguard tasks are risky to accept.
- Trust can shrink a task after acceptance, so repeat work for trusted clients may come in smaller.
- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance, and the CEO cancelled it because it needed about double the whole team's capacity.
- Emp_4 is strongest at research among the team (skill about 6.32).
- The team works about 8 to 9 work hours per calendar day, so a deadline 9 days out gives roughly 70 work hours.
- Emp_6 is strongest at data_environment (skill about 7.7).

**Events when time advanced**

- task_completed: {"task_id": "691964d2-141a-4639-a111-2d06153d0f0d", "task_title": "Task-110", "client_name": "Cortex Intelligence", "success": true, "funds_delta_usd": 16932.52, "listed_reward_usd": 16932.52, "trust_delta": 0.606899686472155, "deadline_margin": "ahead by 55h", "employees_assigned": 4, "salary_bump_total_usd": 201.5, "bankrupt": false}
- task_completed: {"task_id": "1cfef0d0-7248-487e-b1cd-a0e8e8093c36", "task_title": "Task-31", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 15658.34, "listed_reward_usd": 15658.34, "trust_delta": 0.9282379981927911, "deadline_margin": "ahead by 55h", "employees_assigned": 4, "salary_bump_total_usd": 191.32, "bankrupt": false}

## Checkpoint 5 · 2025-01-27T09:21:32.829862

Funds $314,370.93 → $326,748.76, sim time → 2025-01-29T09:25:00.537415

**Commands**

- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-101", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 409260, "skill_rates": { "data_environ…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 2.969, "tasks_succeeded": 3, "t…
- $ `yc-bench task accept --task-id Task-85` → { "task_id": "Task-85", "status": "planned", "accepted_at": "2025-01-27T09:21:32.829862", "deadline": "2025-02-05T09:21:…
- $ `yc-bench task accept --task-id Task-25` → { "task_id": "Task-25", "status": "planned", "accepted_at": "2025-01-27T09:21:32.829862", "deadline": "2025-02-05T09:21:…
- $ `yc-bench task inspect --task-id Task-85` → { "task_id": "Task-85", "title": "Task-85", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task inspect --task-id Task-25` → { "task_id": "Task-25", "title": "Task-25", "status": "planned", "client_name": "Helix Systems", "required_prestige": 1,…
- $ `yc-bench task assign --task-id Task-85 --employees Emp_7,Emp_6,Emp_3,Emp_5` → { "task_id": "Task-85", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_6", "Emp_3", "Emp_5" ], "total_assigned":…
- $ `yc-bench task assign --task-id Task-25 --employees Emp_4,Emp_8,Emp_2,Emp_1` → { "task_id": "Task-25", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_8", "Emp_2", "Emp_1" ], "total_assigned":…
- $ `yc-bench task dispatch --task-id Task-85` → { "task_id": "Task-85", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_5", "Emp_3", "Emp_6", "E…
- $ `yc-bench task dispatch --task-id Task-25` → { "task_id": "Task-25", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_1", "E…

**Note**

> I started two Helix Systems tasks, so all 8 employees are working again. Funds are $314,370.93 after Cortex paid $16,932.52 for Task-110 and Helix paid $15,658.34 for Task-31.
> 
> - **Task-85 (inference, $15,552.25, +0.21 prestige, due Feb 5):** we could only take it because Helix trust is 2.45, and it shrank from 789 to 595 units after I accepted it. Emp_7, Emp_6, Emp_3 and Emp_5 do about 18 units/hr together, so roughly 33 work hours.
> - **Task-25 (research, $12,377.83, +0.135 prestige, due Feb 5):** shrank from 598 to 451 units. Emp_4, Emp_8, Emp_2 and Emp_1 do about 25 units/hr together, so roughly 18 work hours. They'll finish early, so I'll restaff them next checkpoint.
> - **Learned:** Both trusted clients again shrank tasks by about 25%. Client history still shows no failures, and I'm still avoiding Vanguard ML and Equinox Labs. Emp_4's research skill is now 9.84 and Emp_7's inference 6.85.

done, 6 steps, 7 model calls, $0.3310 (total $1.9682)

**Memory it saw:** 10 facts, 5 recalled episodes
- Cortex Intelligence: Task-110 shrank after acceptance, from 851 listed units to 643, when trust was about 2.44.
- Helix Systems: Task-31 shrank after acceptance, from 1,236 listed units to 1,038.
- Cortex Intelligence task sizes have otherwise stayed the same after acceptance, with Task-128 and Task-110 the exceptions.
- Equinox Labs: Task-119 grew 4x after acceptance, from 860 to 3,440 units, so it was cancelled.
- Clients that trust us (Cortex Intelligence, Helix Systems) shrank tasks by about 15-25% after acceptance.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance, and the CEO cancelled it because it needed about double the whole team's capacity.
- A four-person team at about 17 units per hour finished a 798-unit research task (Helix Systems) with about 47 work hours, ahead of its deadline.
- Vanguard ML task sizes have grown after acceptance, so new Vanguard tasks are risky to accept.
- Cancelling a task above the prestige floor costs research prestige, e.g. 0.06 at 1.373.
- Trust can shrink a task after acceptance, so repeat work for trusted clients may come in smaller.

**Events when time advanced**

- task_completed: {"task_id": "a46e0199-858f-43b1-a1cf-a34b740f30c5", "task_title": "Task-25", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 12377.83, "listed_reward_usd": 12377.83, "trust_delta": 0.5889216297329893, "deadline_margin": "ahead by 168h", "employees_assigned": 4, "salary_bump_total_usd": 192.92, "bankrupt": false}

## Checkpoint 6 · 2025-01-29T09:25:00.537415

Funds $326,748.76 → $342,301.01, sim time → 2025-01-29T14:56:09.427199

**Commands**

- $ `yc-bench market browse --limit 15` → { "total": 15, "offset": 0, "limit": 15, "tasks": [ { "task_id": "Task-133", "client_name": "Helix Systems", "required_p…
- $ `yc-bench client list` → { "count": 6, "clients": [ { "client_id": "61d77b28-d16c-4623-a71b-ae0bb207dfac", "name": "Cortex Intelligence", "trust_…
- $ `yc-bench employee list` → { "count": 8, "employees": [ { "name": "Emp_1", "tier": "junior", "salary_cents": 412260, "skill_rates": { "data_environ…
- $ `yc-bench task accept --task-id Task-133` → { "task_id": "Task-133", "status": "planned", "accepted_at": "2025-01-29T09:25:00.537415", "deadline": "2025-02-07T09:25…
- $ `yc-bench task inspect --task-id Task-133` → { "task_id": "Task-133", "title": "Task-133", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task inspect --task-id Task-85` → { "task_id": "Task-85", "title": "Task-85", "status": "active", "client_name": "Helix Systems", "required_prestige": 1, …
- $ `yc-bench task assign --task-id Task-133 --employees Emp_4,Emp_2,Emp_8,Emp_1` → { "task_id": "Task-133", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_2", "Emp_8", "Emp_1" ], "total_assigned"…
- $ `yc-bench task accept --task-id Task-199` → { "task_id": "Task-199", "status": "planned", "accepted_at": "2025-01-29T09:25:00.537415", "deadline": "2025-02-07T09:25…
- $ `yc-bench task dispatch --task-id Task-133` → { "task_id": "Task-133", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_1", "…
- $ `yc-bench task inspect --task-id Task-199` → { "task_id": "Task-199", "title": "Task-199", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task assign --task-id Task-199 --employees Emp_7,Emp_6,Emp_3,Emp_5` → { "task_id": "Task-199", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_6", "Emp_3", "Emp_5" ], "total_assigned"…
- $ `yc-bench task dispatch --task-id Task-199` → { "task_id": "Task-199", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_5", "Emp_3", "Emp_6", "…

**Note**

> I started two new Helix Systems inference tasks, so all 8 employees are working. Funds are $326,748.76 after Helix paid $12,377.83 for Task-25, which finished 168 hours early.
> 
> - **Task-133 ($21,579.79, due Feb 7):** shrank from 1,130 to 788 units after I accepted it. The research team (Emp_4, Emp_2, Emp_8, Emp_1) is on it, but they're weaker at inference, about 14.6 units/hr, so roughly 54 work hours. That fits the deadline but is tighter than usual.
> - **Task-199 ($14,220.21, due Feb 7):** shrank from 607 to 423 units. The inference team (Emp_7, Emp_6, Emp_3, Emp_5) is on it. They're also finishing Task-85 (92% done, 50 units left), so their time is split between the two for a few hours.
> - **Learned:** Helix trust is now 3.02 and Cortex 2.93. Helix now shrinks tasks by about 30%, and trust 3 opened up larger, better-paid tasks. Most tasks on the market are inference. I'm still avoiding Vanguard ML and Equinox Labs.
> - **Watch:** Working only for Helix may lower our trust with Stratos and Prism, so a Stratos data_environment task (for example Task-84) would suit Emp_6 and Emp_7 later.

done, 7 steps, 8 model calls, $0.4140 (total $2.3822)

**Memory it saw:** 10 facts, 5 recalled episodes
- Helix Systems: Task-31 finished successfully 55 hours ahead of its deadline and was paid in full, after shrinking from 1,236 to 1,038 units; Task-25 shrank from 598 to 451 and Task-85 from 789 to 595 after acceptance; a 798-unit research task finished ahead of deadline; no failures are on record.
- A four-person research team of Emp_4, Emp_8, Emp_2 and Emp_1 does about 21-25 units per hour.
- A four-person inference team of Emp_7, Emp_6, Emp_3 and Emp_5 does about 17-18 units per hour.
- Trusted clients (Cortex Intelligence, Helix Systems) shrink accepted tasks by about 15-25%, recently about 25%, so re-check task size right after accepting.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance and was cancelled; new Vanguard ML tasks are risky to accept.
- Cortex Intelligence: Task-110 finished successfully 55 hours ahead of its deadline and was paid in full, but it shrank from 851 to 643 units after acceptance; Task-128 also changed after acceptance and no failures are on record.
- Cortex Intelligence: Task-110 shrank after acceptance, from 851 listed units to 643, when trust was about 2.44.
- Cortex Intelligence task sizes have otherwise stayed the same after acceptance, with Task-128 and Task-110 the exceptions.
- A four-person team at about 17 units per hour finished a 798-unit research task (Helix Systems) with about 47 work hours, ahead of its deadline.
- Equinox Labs: Task-119 grew 4x after acceptance, from 860 to 3,440 units, and was cancelled; avoid accepting Equinox Labs tasks.

**Events when time advanced**

- task_completed: {"task_id": "406072fb-e403-45b9-b7c0-79831d44085e", "task_title": "Task-85", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 15552.25, "listed_reward_usd": 15552.25, "trust_delta": 0.39901726680393157, "deadline_margin": "ahead by 162h", "employees_assigned": 4, "salary_bump_total_usd": 203.5, "bankrupt": false}

## Checkpoint 7 · 2025-01-29T14:56:09.427199

Funds $342,301.01 → $356,521.22, sim time → 2025-01-31T14:53:10.706744

**Commands**

- $ `yc-bench task list --status active` → { "count": 2, "tasks": [ { "task_id": "Task-133", "title": "Task-133", "status": "active", "client_name": "Helix Systems…

**Note**

> I didn't start anything new this checkpoint. Both running tasks are on track and all 8 employees are busy, so a third task would only split their time. Funds are $342,301.01 after Helix Systems paid $15,552.25 for Task-85, which finished 162 hours early.
> 
> - **Task-133 (Helix, inference, due Feb 7):** 10.2% done with the research team (Emp_4, Emp_2, Emp_8, Emp_1). It's flagged as not at risk.
> - **Task-199 (Helix, inference, due Feb 7):** 11.8% done with the inference team (Emp_7, Emp_6, Emp_3, Emp_5). It should take about 24 more work hours, which leaves plenty of time.
> - **Next:** When Task-199 finishes, I'll give the inference team a Stratos or Prism data_environment task to keep trust with those clients up. I'm still avoiding Vanguard ML and Equinox Labs.
> - **Learned:** Helix keeps paying on time and finishing well early, and none of our clients has failed a task yet.

done, 2 steps, 3 model calls, $0.0778 (total $2.4600)

**Memory it saw:** 10 facts, 6 recalled episodes
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance and was cancelled; avoid new Vanguard ML tasks.
- A four-person inference team of Emp_7, Emp_6, Emp_3 and Emp_5 does about 17-18 units per hour.
- Cortex Intelligence: task sizes have otherwise stayed the same after acceptance, with Task-110 and Task-128 the exceptions.
- A four-person research team of Emp_4, Emp_8, Emp_2 and Emp_1 does about 21-25 units per hour on research work.
- The research team is weaker at inference, at about 14.6 units per hour, so inference tasks given to it need extra time margin.
- Cortex Intelligence: Task-110 shrank after acceptance, from 851 listed units to 643, when trust was about 2.44.
- Equinox Labs: Task-119 grew 4x after acceptance, from 860 to 3,440 units, and was cancelled; avoid Equinox Labs tasks.
- Vanguard ML task sizes have grown after acceptance, so new Vanguard tasks are risky to accept.
- Helix Systems: a 798-unit research task finished ahead of its deadline, and no failures are on record.
- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.

**Events when time advanced**

- task_completed: {"task_id": "df89c4f6-131c-4dbd-94f5-c27aa6219505", "task_title": "Task-199", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 14220.21, "listed_reward_usd": 14220.21, "trust_delta": 0.2896309375740098, "deadline_margin": "ahead by 163h", "employees_assigned": 4, "salary_bump_total_usd": 205.5, "bankrupt": false}

## Checkpoint 8 · 2025-01-31T14:53:10.706744

Funds $356,521.22 → $316,676.19, sim time → 2025-02-03T09:00:00

**Commands**

- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-101", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench task list --status active` → { "count": 1, "tasks": [ { "task_id": "Task-133", "title": "Task-133", "status": "active", "client_name": "Helix Systems…
- $ `yc-bench task accept --task-id Task-163` → { "task_id": "Task-163", "status": "planned", "accepted_at": "2025-01-31T14:53:10.706744", "deadline": "2025-02-11T14:53…
- $ `yc-bench task inspect --task-id Task-163` → { "task_id": "Task-163", "title": "Task-163", "status": "planned", "client_name": "Helix Systems", "required_prestige": …
- $ `yc-bench task assign --task-id Task-163 --employees Emp_7,Emp_6,Emp_3,Emp_5` → { "task_id": "Task-163", "status": "planned", "newly_assigned": [ "Emp_7", "Emp_6", "Emp_3", "Emp_5" ], "total_assigned"…
- $ `yc-bench task dispatch --task-id Task-163` → { "task_id": "Task-163", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_5", "Emp_3", "Emp_6", "…

**Note**

> I started Helix Task-163 with the inference team, so all 8 employees are working again. Funds are $356,521.22 after Helix paid $14,220.21 for Task-199, which finished 163 hours early.
> - **Task-163 (Helix, inference, $15,650.08, due Feb 11):** shrank from 1,294 to 816 units after I accepted it, about 37% smaller. Emp_7, Emp_6, Emp_3 and Emp_5 do about 18/hr, so roughly 45 work hours. That leaves plenty of slack.
> - **Task-133 (Helix, inference, research team, due Feb 7):** 65.5% done and not flagged as at risk.
> - **Learned:** Helix now shrinks tasks by about 37%, making it our best client. Helix's trust gain per task keeps falling (now +0.29), so I'll fit in a Stratos task (Task-84 or Task-174, data_environment) or a Cortex task next to keep those clients' trust up.
> - **Still avoiding:** Vanguard ML and Equinox Labs, which have many tasks listed.

done, 5 steps, 6 model calls, $0.2537 (total $2.7137)

**Memory it saw:** 10 facts, 6 recalled episodes
- Inference team Emp_7, Emp_6, Emp_3 and Emp_5 completed Helix Systems Task-85 162 hours ahead of its deadline.
- Completing a Helix Systems task ahead of its deadline raised Helix trust by about 0.4.
- Helix Systems: Task-85 finished 162 hours ahead of its deadline and was paid in full, with Task-25 also finished 168 hours early and no failures on record.
- Cortex Intelligence: task sizes have otherwise stayed the same after acceptance, with Task-110 and Task-128 the exceptions.
- A four-person research team of Emp_4, Emp_8, Emp_2 and Emp_1 does about 21-25 units per hour on research work.
- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance and was cancelled; avoid new Vanguard ML tasks.
- With 8 employees, two four-person teams fully occupy the staff, so a third concurrent task only splits time between teams.
- Higher trust with a trusted client unlocks larger, better-paid tasks.
- The research team is weaker at inference, at about 14.6 units per hour, so inference tasks given to it need extra time margin.

**Events when time advanced**

- monthly_payroll: {"funds_after_usd": 316676.19}

## Checkpoint 9 · 2025-02-03T09:00:00

Funds $316,676.19 → $338,255.98, sim time → 2025-02-04T15:32:39.779844

**Commands**

- $ `yc-bench task list` → { "count": 14, "tasks": [ { "task_id": "Task-163", "title": "Task-163", "status": "active", "client_name": "Helix System…

**Note**

> I didn't start anything new this checkpoint. Both running tasks are on track and all 8 employees are busy, so a third task would only split their time. Funds are $316,676.19 after the monthly payroll of $39,845.03 went out.
> 
> - **Task-133 (Helix, research team, due Feb 7):** 82.4% done and not flagged as at risk. At about 14.6 units/hr it has roughly 10 work hours left.
> - **Task-163 (Helix, inference team, due Feb 11):** 24.8% done and not flagged as at risk, with plenty of slack.
> - **Next:** When Task-133 finishes, I'll give the research team a Stratos, Prism or Cortex task to keep trust with those clients up. I'm still avoiding Vanguard ML and Equinox Labs.
> - **Learned:** Funds drop by about $40k each month for payroll, so I need to keep both teams on paid work.

done, 2 steps, 3 model calls, $0.0684 (total $2.7821)

**Memory it saw:** 10 facts, 5 recalled episodes
- Helix Systems: Task-85, Task-25 and Task-199 finished 162, 168 and 163 hours ahead of their deadlines and were paid in full, with no failures on record.
- Cortex Intelligence: task sizes have otherwise stayed the same after acceptance, with Task-110 and Task-128 the exceptions.
- Completing a Helix Systems task ahead of its deadline raised Helix trust by about 0.4 early on, but later gains have fallen to about 0.29 per task.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance and was cancelled; avoid new Vanguard ML tasks.
- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.
- Helix Systems: task sizes shrink after acceptance, by about 15-30% earlier and about 37% for Task-163, so re-check size right after accepting.
- Vanguard ML task sizes have grown after acceptance, so new Vanguard tasks are risky to accept.
- The research team is weaker at inference, at about 14.6 units per hour, so inference tasks given to it need extra time margin.
- Inference team Emp_7, Emp_6, Emp_3 and Emp_5 works at about 18 units per hour on inference work.
- Equinox Labs: Task-119 grew 4x after acceptance, from 860 to 3,440 units, and was cancelled; avoid Equinox Labs tasks.

**Events when time advanced**

- task_completed: {"task_id": "b3dce787-3ca8-42fd-91e1-92a9a8db1e06", "task_title": "Task-133", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 21579.79, "listed_reward_usd": 21579.79, "trust_delta": 0.2234768627694601, "deadline_margin": "ahead by 66h", "employees_assigned": 4, "salary_bump_total_usd": 194.52, "bankrupt": false}

## Checkpoint 10 · 2025-02-04T15:32:39.779844

Funds $338,255.98 → $353,906.06, sim time → 2025-02-05T12:42:24.902692

**Commands**

- $ `yc-bench market browse --limit 20` → { "total": 20, "offset": 0, "limit": 20, "tasks": [ { "task_id": "Task-101", "client_name": "Equinox Labs", "required_pr…
- $ `yc-bench client history` → { "count": 6, "client_history": [ { "client_name": "Cortex Intelligence", "trust_level": 2.823, "tasks_succeeded": 3, "t…
- $ `yc-bench task accept --task-id Task-1` → { "task_id": "Task-1", "status": "planned", "accepted_at": "2025-02-04T15:32:39.779844", "deadline": "2025-02-13T15:32:3…
- $ `yc-bench task assign --task-id Task-1 --employees Emp_4,Emp_2,Emp_8,Emp_1` → { "task_id": "Task-1", "status": "planned", "newly_assigned": [ "Emp_4", "Emp_2", "Emp_8", "Emp_1" ], "total_assigned": …
- $ `yc-bench task dispatch --task-id Task-1` → { "task_id": "Task-1", "status": "active", "assignment_count": 4, "assigned_employees": [ "Emp_4", "Emp_8", "Emp_1", "Em…
- $ `yc-bench task inspect --task-id Task-1` → { "task_id": "Task-1", "title": "Task-1", "status": "active", "client_name": "Helix Systems", "required_prestige": 1, "r…

**Note**

> I started Helix Task-1 with the research team, so both teams are working again. Funds are $338,255.98 after Helix paid $21,579.79 for Task-133, which finished 66 hours early.
> 
> 1. **Task-1 (Helix, inference, $13,550.68, +0.255 prestige, due Feb 13):** after I accepted it, it shrank from 899 to 550 units, about 39% smaller. Emp_4, Emp_2, Emp_8 and Emp_1 do about 14.6 units/hr, so it needs roughly 38 work hours, which leaves lots of slack.
> 2. **Task-163 (Helix, inference team) is still running and due Feb 11.** It was on track last time I checked.
> 3. **Learned:** Helix trust is now 3.88, but each Helix task adds less trust (Task-133 added only +0.22). Cortex trust slipped from 2.93 to 2.82, so working mostly for Helix is costing us trust with the other clients.
> 4. **Next:** When Task-163 finishes, I'll give the inference team a Cortex inference task (Task-98) or a Stratos data_environment task (Task-174) to rebuild trust with those clients. I'm still avoiding Vanguard ML and Equinox Labs.

done, 4 steps, 5 model calls, $0.1833 (total $2.9654)

**Memory it saw:** 10 facts, 5 recalled episodes
- Helix Systems: Task-85, Task-25 and Task-199 finished 162, 168 and 163 hours ahead of their deadlines and were paid in full, with no failures on record.
- Completing a Helix Systems task ahead of its deadline raised Helix trust by about 0.4 early on, but later gains have fallen to about 0.29 per task.
- With 8 employees, two four-person teams fully occupy the staff, so a third concurrent task only splits time between teams.
- Helix Systems: Task-163 (inference, 1,294 to 816 units after acceptance) and Task-133 were both accepted and remained on track, with no failures on record.
- The research team is weaker at inference, at about 14.6 units per hour, so inference tasks given to it need extra time margin.
- Cortex Intelligence: task sizes have otherwise stayed the same after acceptance, with Task-110 and Task-128 the exceptions.
- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance and was cancelled; avoid new Vanguard ML tasks.
- Prism Analytics: Task-183 was completed 50 hours ahead of its deadline and paid in full; task sizes have not changed after acceptance.
- A four-person team at about 17 units per hour finished a 798-unit research task with about 47 work hours, ahead of its deadline.

**Events when time advanced**

- task_completed: {"task_id": "fec6f84b-2d51-445a-93fb-451919a800b5", "task_title": "Task-163", "client_name": "Helix Systems", "success": true, "funds_delta_usd": 15650.08, "listed_reward_usd": 15650.08, "trust_delta": 0.17213091745436104, "deadline_margin": "ahead by 146h", "employees_assigned": 4, "salary_bump_total_usd": 207.5, "bankrupt": false}

## Summary

- terminal reason: max_checkpoints
- checkpoints: 10, sim time 2025-02-05T12:42:24.902692
- final funds: $353,906.06
- cost: $2.9654 over 69 model calls

**Facts in memory at the end (28)**

- Deadlines appear only after a task is accepted and have typically been about 9 to 10 days out.
- The team works about 8 to 9 work hours per calendar day.
- A four-person team at about 17 units per hour finished a 798-unit research task with about 47 work hours, ahead of its deadline.
- With 8 employees, two four-person teams fully occupy the staff, so a third concurrent task only splits time between teams.
- The research team is weaker at inference, at about 14.6 units per hour, so inference tasks given to it need extra time margin.
- A four-person research team of Emp_4, Emp_8, Emp_2 and Emp_1 does about 21-25 units per hour on research work.
- Emp_4 is the strongest researcher on the team (research skill about 9.84).
- Emp_7 is strong at data_environment (skill about 7.08) and inference (skill about 6.85), and Emp_6 and Emp_7 are the best fit for data_environment work.
- Inference team Emp_7, Emp_6, Emp_3 and Emp_5 works at about 18 units per hour on inference work.
- Monthly payroll is deducted from funds every month, so both teams must stay on paid work to keep runway healthy.
- Cancelling a task above the prestige floor costs research prestige, e.g. 0.06 at 1.373.
- Higher trust with a trusted client unlocks larger, better-paid tasks.
- Prism Analytics: Task-183 was completed 50 hours ahead of its deadline and paid in full; task sizes have not changed after acceptance.
- Vanguard ML: Task-10 research requirement rose from 564 to 2,256 units after acceptance and was cancelled; Vanguard ML task sizes have grown after acceptance, so avoid new Vanguard ML tasks.
- Equinox Labs: Task-119 grew 4x after acceptance, from 860 to 3,440 units, and was cancelled; avoid Equinox Labs tasks.
- Trusted clients Helix Systems and Cortex Intelligence shrink accepted tasks by about 15-39% after acceptance, so repeat work for them may come in smaller.
- Cortex Intelligence: trust fell from 2.93 to 2.82 while the agent worked mostly for Helix Systems, so trust with other clients can erode when one client dominates the work.
- Cortex Intelligence: Task-110 shrank after acceptance from 851 to 643 units, Task-128 also changed after acceptance, and no failures are on record.
- Helix Systems: completing a task ahead of deadline raised trust by about 0.4 early on, but later gains have fallen to about 0.22-0.29 per task.
- Helix Systems: task sizes shrink after acceptance by about 15-39% (Task-163 about 37%, Task-1 about 39%), so re-check size right after accepting.
- Helix Systems: Task-85, Task-25, Task-199 and Task-133 finished 162, 168, 163 and 66 hours ahead of their deadlines, were paid in full, and have no failures on record.
- Helix Systems: Task-163 (inference, 1,294 to 816 units after acceptance) and Task-133 were both accepted and remained on track, with no failures on record.
- Re-check task size right after accepting a task, because requirements can change once accepted.
- Emp_6 and Emp_7 are the best fit for data_environment work.
- Cortex Intelligence: task sizes have otherwise stayed the same after acceptance, with Task-110 and Task-128 the exceptions.
- Vanguard ML task sizes have grown after acceptance, so new Vanguard tasks are risky to accept.
- Prism Analytics task sizes have not changed after acceptance.
- Cortex Intelligence: Task-110 shrank after acceptance, from 851 listed units to 643, when trust was about 2.44.
