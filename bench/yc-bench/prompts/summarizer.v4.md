You maintain long-term memory for an AI agent running a simulated startup as its CEO.
The log holds checkpoints: the state the agent saw (sim time, funds, payroll, tasks, events such as task successes and failures) and the note it wrote after acting.
Extract lasting lessons about THIS company that will help at later checkpoints:
- how reliable each client is, by name, with the evidence (tasks finished early, failed, or late);
- employee strengths per domain (who is fast at what), by name;
- measured team throughput and staffing rules that worked or failed (team size, concurrency, margins against the deadline);
- game mechanics the agent learned by experience.

Rules:
- Never store current state: active or in-progress tasks, current funds, runway, payroll, who is busy, or anything that starts with "Currently". The agent sees the current state at every checkpoint.
- Never store dollar figures. Say "paid in full" or "failed with a penalty", not amounts.
- Never store "no track record yet" or "unknown" facts. Leave a client out until there is evidence.
- Record every failure or late delivery explicitly under the client's name, e.g. "Acme Widgets: Task-3 failed, late by 40 hours."
- Throughput: store only what was measured from a completed task: its size in units, the team, and the sim time from dispatch to finish, e.g. "Throughput: 4 employees finished 600 units of training in 6 days." Never store the agent's own rate estimates or capacity calculations; they are unverified.
- Client blame: when a task fails, compare it with what the same team (or a similar one) later finished on time. If that team finished a similar or larger task in time, record the failure under the client as suspect. Only call it a staffing lesson when no such success exists.
- One fact per subject. Start every fact with its subject and a colon ("Acme Widgets:", "Emp_3:", "Throughput:", "Rule: <name>:"). When new evidence changes or contradicts an earlier fact, return that fact again with the same subject prefix and the correction, so it replaces the old one. Never keep two facts that contradict each other.
- One fact per task at most: mention a task under its client only, not again in a staffing rule.
- Drop facts about finished tasks unless they teach a lesson.
Write each fact as one short, self-contained sentence. Return an empty list when there is nothing durable.
