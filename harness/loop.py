"""The agent run: working memory -> LLM <-> tools loop -> end-loop guardrails -> reply.

Guardrails that end the loop (each sets `RunResult.stop`):
  done            the model answered without calling a tool
  asked_user      the model called ask_user: the question is the reply
  needs_approval  a tool call needs a human (e.g. a large refund); nothing ran
  max_steps       step budget spent (release.max_steps)
  max_cost        cost budget spent (release.max_cost_usd)
  refusal         the model declined
After the reply, both messages go to episodic memory, and every N chats the
summarizer distills them into semantic facts.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .config import Release
from .consolidate import Consolidator
from .embed import Embedder, HashingEmbedder
from .llm import LLM
from .memory import EpisodicMemory, ProceduralMemory, SemanticMemory, WorkingMemory, build_working_memory
from .store import Store
from .tools import TOOLS, Backend, Tool
from .tracing import Tracer


@dataclass
class ToolCall:
    name: str
    input: dict[str, Any]
    result: Any
    is_error: bool = False


@dataclass
class RunResult:
    reply: str
    stop: str
    steps: int
    cost_usd: float
    trace_id: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    pending_approval: dict[str, Any] | None = None
    working_memory: WorkingMemory | None = None


class Agent:
    def __init__(self, release: Release, llm: LLM, store: Store, *, embedder: Embedder | None = None,
                 backend: Backend | None = None, tracer: Tracer | None = None,
                 tools: list[Tool] | None = None, consolidate: bool = True):
        self.release, self.llm, self.store = release, llm, store
        self.embedder = embedder or HashingEmbedder()
        self.backend = backend or Backend()
        self.tracer = tracer or Tracer()
        self.tools = {t.name: t for t in (tools or TOOLS)}
        self.procedural = ProceduralMemory()
        self.semantic = SemanticMemory(store, self.embedder)
        self.episodic = EpisodicMemory(store, self.embedder)
        self.consolidator = Consolidator(release, llm, store, self.embedder, self.tracer) if consolidate else None

    def run(self, user_id: str, chat_id: str, prompt: str, *, approved: set[str] = frozenset()) -> RunResult:
        r = self.release
        with self.tracer.run(user_id=user_id, chat_id=chat_id, release_tag=r.tag, prompt=prompt) as (root, trace_id):
            with self.tracer.span("working-memory", as_type="retriever", input=prompt) as obs:
                wm = build_working_memory(r, self.procedural, self.semantic, self.episodic, user_id, chat_id, prompt)
                obs.update(output={"skills": wm.skills, "facts": wm.facts, "episodes": wm.episodes},
                           metadata={"system_chars": len(wm.system), "history_messages": len(wm.messages) - 1})

            result = self._loop(wm, trace_id, approved)
            result.working_memory = wm
            root.update(output=result.reply, metadata={
                "stop": result.stop, "steps": result.steps, "cost_usd": round(result.cost_usd, 6),
                "tool_calls": [c.name for c in result.tool_calls], "skills": wm.skills})

        self.episodic.save(user_id, chat_id, "user", prompt)
        self.episodic.save(user_id, chat_id, "assistant", result.reply)
        if self.consolidator:
            self.consolidator.maybe_run(user_id)
        self.tracer.flush()
        return result

    def _loop(self, wm: WorkingMemory, trace_id: str, approved: set[str]) -> RunResult:
        r = self.release
        messages = list(wm.messages)
        specs = [t.spec() for t in self.tools.values()]
        calls: list[ToolCall] = []
        cost = 0.0

        for step in range(1, r.max_steps + 1):
            if cost >= r.max_cost_usd:
                return self._guardrail(trace_id, "max_cost", step - 1, cost, calls,
                                       f"I stopped before finishing: this request hit the ${r.max_cost_usd:.2f} cost limit.")

            with self.tracer.span(f"llm-{step}", as_type="generation", model=r.agent_model,
                                  input=messages[-1]["content"]) as gen:
                c = self.llm.complete(model=r.agent_model, system=wm.system, messages=messages,
                                      tools=specs, effort=r.agent_effort)
                gen.update(output=c.content, usage_details={"input": c.input_tokens, "output": c.output_tokens},
                           cost_details={"total": c.cost_usd}, metadata={"stop_reason": c.stop_reason})
            cost += c.cost_usd
            messages.append({"role": "assistant", "content": c.content})

            if c.stop_reason == "refusal":
                return self._guardrail(trace_id, "refusal", step, cost, calls, "I can't help with that request.")
            if not c.tool_uses:
                return RunResult(c.text.strip(), "done", step, cost, trace_id, calls)

            results, stop = [], None
            for tu in c.tool_uses:
                call, block, stop_here = self._call_tool(tu, approved)
                calls.append(call)
                results.append(block)
                stop = stop or stop_here
            messages.append({"role": "user", "content": results})

            if stop:
                kind, reply, pending = stop
                res = self._guardrail(trace_id, kind, step, cost, calls, reply)
                res.pending_approval = pending
                return res

        return self._guardrail(trace_id, "max_steps", r.max_steps, cost, calls,
                               f"I stopped after {r.max_steps} steps without finishing. Here is what I did: "
                               + (", ".join(c.name for c in calls) or "nothing") + ".")

    def _call_tool(self, tu: dict, approved: set[str]):
        name, args = tu["name"], tu.get("input") or {}
        tool = self.tools.get(name)
        with self.tracer.span(f"tool:{name}", as_type="tool", input=args) as obs:
            stop = None
            if tool is None:
                out, err = f"unknown tool {name}", True
            elif tool.ends_turn:
                out, err = tool.run(self.backend, args), False
                stop = ("asked_user", args.get("question", ""), None)
            elif (reason := tool.needs_approval(self.backend, args)) and name not in approved:
                out, err = f"Not run: needs operator approval ({reason}).", True
                stop = ("needs_approval", f"I need your approval first: {reason}.", {"tool": name, "input": args})
            else:
                try:
                    out, err = tool.run(self.backend, args), False
                except Exception as e:  # tool errors go back to the model, not up the stack
                    out, err = f"{type(e).__name__}: {e}", True
            obs.update(output=out, level="ERROR" if err and not stop else "DEFAULT")
        block = {"type": "tool_result", "tool_use_id": tu["id"],
                 "content": out if isinstance(out, str) else json.dumps(out), "is_error": err}
        return ToolCall(name, args, out, err), block, stop

    def _guardrail(self, trace_id, kind, steps, cost, calls, reply) -> RunResult:
        with self.tracer.span(f"guardrail:{kind}", as_type="guardrail") as obs:
            obs.update(output=reply, level="WARNING" if kind in ("max_steps", "max_cost", "refusal") else "DEFAULT")
        return RunResult(reply, kind, steps, cost, trace_id, calls)
