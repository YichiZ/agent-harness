"""Run the harness on τ²-bench (airline by default) and score it in Langfuse.

τ²-bench supplies the tools, the domain policy, a simulated user and the grader
(final database state, required actions, required information). This adapter
plugs the harness in as the agent:

  - working memory  = harness system prompt (prompts/tau2.<version>.md) + domain policy
  - LLM             = the release's agent model, with the same guardrails as the
                      harness loop: a step budget per user turn and a cost budget
  - trace           = one Langfuse trace per task attempt, scored with the τ² reward

The τ² orchestrator, not the harness, executes tool calls, so that the grader
can replay them. That is why this is a separate agent class rather than
`Agent.run`, which executes tools itself.

Requires TAU2_DATA_DIR pointing at a tau2-bench checkout's data/ folder; the
package itself is a main dependency (Python 3.13).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from tau2.agent.base_agent import HalfDuplexAgent
from tau2.data_model.message import AssistantMessage, MultiToolMessage, ToolCall, ToolMessage, UserMessage
from tau2.environment.tool import Tool as Tau2Tool
from tau2.evaluator.evaluator import EvaluationType
from tau2.orchestrator.orchestrator import Orchestrator
from tau2.runner import build_environment, build_user, get_tasks, run_simulation
from tau2.user.user_simulator import UserSimulator

from ..config import ROOT, Release
from ..llm import LLM
from ..tracing import Tracer

GIVE_UP = ("I'm sorry, I wasn't able to finish this request. "
           "I'm transferring you to a human agent who can help.")


def to_anthropic_tool(tool: Tau2Tool) -> dict[str, Any]:
    fn = tool.openai_schema["function"]
    return {"name": fn["name"], "description": fn["description"], "input_schema": fn["parameters"]}


@dataclass
class Tau2State:
    messages: list[dict[str, Any]] = field(default_factory=list)  # Anthropic format, append-only
    steps_this_turn: int = 0
    cost_usd: float = 0.0
    llm_calls: int = 0


class HarnessTau2Agent(HalfDuplexAgent[Tau2State]):
    def __init__(self, tools: list[Tau2Tool], domain_policy: str, *, release: Release, llm: LLM,
                 tracer: Tracer | None = None):
        super().__init__(tools=tools, domain_policy=domain_policy)
        self.release, self.llm, self.tracer = release, llm, tracer or Tracer()
        self.tool_specs = [to_anthropic_tool(t) for t in tools]
        prompt = (ROOT / "prompts" / f"tau2.{release.prompt_version}.md").read_text().strip()
        self.system = f"{prompt}\n\n# Domain policy\n\n{domain_policy}"

    def get_init_state(self, message_history: Optional[list] = None) -> Tau2State:
        state = Tau2State()
        for m in message_history or []:
            if isinstance(m, (UserMessage, ToolMessage, MultiToolMessage)):
                self._append_incoming(state, m)
            elif isinstance(m, AssistantMessage):
                state.messages.append({"role": "assistant", "content": self._assistant_blocks(m)})
        return state

    def generate_next_message(self, message, state: Tau2State) -> tuple[AssistantMessage, Tau2State]:
        r = self.release
        if isinstance(message, UserMessage):
            state.steps_this_turn = 0
        self._append_incoming(state, message)

        # End-loop guardrails, same budgets as the harness loop.
        if state.steps_this_turn >= r.max_steps or state.cost_usd >= r.max_cost_usd:
            kind = "max_steps" if state.steps_this_turn >= r.max_steps else "max_cost"
            with self.tracer.span(f"guardrail:{kind}", as_type="guardrail") as obs:
                obs.update(output=GIVE_UP, level="WARNING")
            state.messages.append({"role": "assistant", "content": [{"type": "text", "text": GIVE_UP}]})
            return AssistantMessage(role="assistant", content=GIVE_UP), state

        state.steps_this_turn += 1
        state.llm_calls += 1
        with self.tracer.span(f"llm-{state.llm_calls}", as_type="generation", model=r.agent_model,
                              input=state.messages[-1]["content"]) as gen:
            c = self.llm.complete(model=r.agent_model, system=self.system, messages=state.messages,
                                  tools=self.tool_specs, effort=r.agent_effort)
            gen.update(output=c.content, usage_details={"input": c.input_tokens, "output": c.output_tokens},
                       cost_details={"total": c.cost_usd}, metadata={"stop_reason": c.stop_reason})
        state.cost_usd += c.cost_usd
        state.messages.append({"role": "assistant", "content": c.content})

        if c.stop_reason == "refusal":
            return AssistantMessage(role="assistant", content="I can't help with that request."), state
        if c.tool_uses:
            # τ² rejects a message with both text and tool calls; the text stays in our own history.
            calls = [ToolCall(id=tu["id"], name=tu["name"], arguments=tu.get("input") or {}) for tu in c.tool_uses]
            return AssistantMessage(role="assistant", tool_calls=calls, cost=c.cost_usd), state
        return AssistantMessage(role="assistant", content=c.text.strip() or "(no reply)", cost=c.cost_usd), state

    @staticmethod
    def _append_incoming(state: Tau2State, m) -> None:
        if isinstance(m, UserMessage):
            state.messages.append({"role": "user", "content": m.content or ""})
            return
        tool_msgs = m.tool_messages if isinstance(m, MultiToolMessage) else [m]
        blocks = [{"type": "tool_result", "tool_use_id": t.id, "content": t.content or "", "is_error": t.error}
                  for t in tool_msgs]
        state.messages.append({"role": "user", "content": blocks})

    @staticmethod
    def _assistant_blocks(m: AssistantMessage) -> list[dict]:
        if m.tool_calls:
            return [{"type": "tool_use", "id": t.id, "name": t.name, "input": t.arguments} for t in m.tool_calls]
        return [{"type": "text", "text": m.content or ""}]


class HumanUser(UserSimulator):
    """You play the customer in the terminal. An empty line or Ctrl-D ends the conversation."""
    def __init__(self):
        super().__init__(llm="human")

    def _generate_next_message(self, message, state):
        if isinstance(message, AssistantMessage) and message.content:
            print(f"\nagent: {message.content}")
        try:
            line = input("\nyou> ").strip()
        except EOFError:
            line = ""
        return UserMessage(role="user", content=line or "###STOP###")


def human_user(env, task) -> HumanUser:
    print(f"τ² task {task.id}. Your role as the customer:\n{task.user_scenario}\n"
          "(empty line to finish; the run is then graded)")
    return HumanUser()


@dataclass
class TaskAttempt:
    task_id: str
    trial: int
    reward: float
    trace_id: str
    cost_usd: float
    termination: str
    db_match: Optional[bool]


@dataclass
class Tau2Report:
    domain: str
    release_tag: str
    attempts: list[TaskAttempt]
    gate_passed: bool = False

    def pass_hat_k(self, k: int) -> float:
        """τ-bench pass^k: share of tasks whose first k attempts all succeed."""
        by_task: dict[str, list[float]] = {}
        for a in self.attempts:
            by_task.setdefault(a.task_id, []).append(a.reward)
        ok = [all(r >= 1.0 for r in rs[:k]) for rs in by_task.values() if len(rs) >= k]
        return sum(ok) / len(ok) if ok else 0.0

    def to_json(self) -> dict[str, Any]:
        trials = max((a.trial for a in self.attempts), default=0) + 1
        return {"domain": self.domain, "release_tag": self.release_tag, "gate_passed": self.gate_passed,
                **{f"pass^{k}": round(self.pass_hat_k(k), 3) for k in range(1, trials + 1)},
                "total_cost_usd": round(sum(a.cost_usd for a in self.attempts), 4),
                "attempts": [asdict(a) for a in self.attempts]}


def run_tau2(release: Release, llm: LLM, *, domain: str = "airline", task_ids: list[str] | None = None,
             num_tasks: int | None = None, trials: int = 1, user_llm: str | None = None,
             tracer: Tracer | None = None, user_factory=None,
             evaluation_type: EvaluationType = EvaluationType.ALL) -> Tau2Report:
    tracer = tracer or Tracer()
    tasks = get_tasks(domain, task_ids=task_ids, num_tasks=num_tasks)
    report = Tau2Report(domain, release.tag, [])
    for task in tasks:
        for trial in range(trials):
            env = build_environment(domain)
            agent = HarnessTau2Agent(env.get_tools(), env.get_policy(), release=release, llm=llm, tracer=tracer)
            user = (user_factory(env, task) if user_factory
                    else build_user("user_simulator", env, task, llm=user_llm or release.tau2_user_model))
            orch = Orchestrator(domain=domain, agent=agent, user=user, environment=env, task=task,
                                max_steps=100, max_errors=10, seed=trial)
            with tracer.run(user_id=f"tau2-{domain}", chat_id=f"{domain}-{task.id}-t{trial}",
                            release_tag=release.tag, prompt=f"τ² {domain} task {task.id}",
                            tags=["tau2", domain]) as (root, trace_id):
                sim = run_simulation(orch, evaluation_type=evaluation_type)
                reward = float(sim.reward_info.reward) if sim.reward_info else 0.0
                db = sim.reward_info.db_check if sim.reward_info else None
                root.update(output=sim.messages[-1].content if sim.messages else None,
                            metadata={"reward": reward, "termination": str(sim.termination_reason)})
            tracer.score(trace_id, "tau2_reward", reward)
            report.attempts.append(TaskAttempt(task.id, trial, reward, trace_id, agent_cost(sim),
                                               str(sim.termination_reason), db.db_match if db else None))
    report.gate_passed = report.pass_hat_k(1) >= release.tau2_gate_min_pass
    tracer.flush()
    return report


def agent_cost(sim) -> float:
    return round(sum((m.cost or 0.0) for m in sim.messages if isinstance(m, AssistantMessage)), 6)


def save(report: Tau2Report, out: Path | None = None) -> Path:
    out = out or ROOT / "evals" / "results" / f"tau2-{report.domain}-{report.release_tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_json(), indent=2))
    return out
