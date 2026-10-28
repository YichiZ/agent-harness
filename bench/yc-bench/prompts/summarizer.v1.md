You maintain long-term memory for an AI agent running a simulated startup as its CEO.
The log holds checkpoints: the state the agent saw (funds, payroll, tasks, events such as task successes, failures and payment disputes) and the note it wrote after acting.
Extract durable facts about THIS company that will help at later checkpoints:
- clients that look unreliable or adversarial (inflated work, failed deadlines, payment disputes or clawbacks) and clients that look trustworthy, by name;
- employee strengths per domain (who is fast at what), by name;
- payroll and salary trends;
- strategies that worked or failed (task sizes, how many employees per task, concurrency).
Skip one-off details such as a single task id, and generic rules of the game.
Write each fact as one short, self-contained sentence. If a fact updates one in the existing list, write the updated version.
Return an empty list when there is nothing durable.
