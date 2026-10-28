"""The agent: config, model client, and the loop.

working memory -> LLM <-> tools loop -> end-loop guardrails -> reply.

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
from pathlib import Path
from typing import Any, Protocol

from .memory import (ROOT, Consolidator, Embedder, EpisodicMemory, HashingEmbedder, ProceduralMemory,
                     SemanticMemory, Store, WorkingMemory, build_working_memory)
from .tools import TOOLS, Backend, Tool


# ── config: models, loop budgets and memory knobs, read from release.json ──

@dataclass(frozen=True)
class Release:
    prompt_version: str
    agent_model: str
    agent_effort: str
    summarizer_model: str
    max_steps: int
    max_cost_usd: float
    history_turns: int
    semantic_top_k: int
    episodic_top_k: int
    episodic_recent_k: int
    consolidate_every_n_chats: int
    prompts_dir: str = "prompts"  # relative to the repo root

    @classmethod
    def load(cls, path: Path | None = None) -> "Release":
        return cls(**json.loads((path or ROOT / "release.json").read_text()))

    def system_prompt(self) -> str:
        return self._prompt("system")

    def summarizer_prompt(self) -> str:
        return self._prompt("summarizer")

    def headings(self) -> dict[str, str]:
        """Section headings and labels in working memory and the summarizer's input, one `key: text` per line."""
        return dict(line.split(": ", 1) for line in self._prompt("headings").splitlines() if line.strip())

    def _prompt(self, kind: str) -> str:
        return (ROOT / self.prompts_dir / f"{kind}.{self.prompt_version}.md").read_text()


# ── model client: the loop only sees `LLM.complete`, so tests swap in a fake ──

# $ per million tokens (input, output), Claude API list prices.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}


@dataclass
class Completion:
    content: list[dict[str, Any]]  # Anthropic content blocks, passed back unchanged
    stop_reason: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def text(self) -> str:
        return "".join(b.get("text", "") for b in self.content if b.get("type") == "text")

    @property
    def tool_uses(self) -> list[dict[str, Any]]:
        return [b for b in self.content if b.get("type") == "tool_use"]

    @property
    def cost_usd(self) -> float:
        inp, out = PRICES.get(self.model, (0.0, 0.0))
        return (self.input_tokens * inp + self.output_tokens * out) / 1_000_000


class LLM(Protocol):
    def complete(
        self,
        *,
        model: str,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        effort: str | None = None,
        json_schema: dict[str, Any] | None = None,
        max_tokens: int = 16000,
    ) -> Completion: ...


class AnthropicLLM:
    """Claude via the official SDK.

    Server-side refusal fallbacks are on (`fallbacks="default"`), so a request a
    safety classifier declines is re-run on Anthropic's recommended model inside
    the same call instead of ending the run.
    """

    def __init__(self, client: Any | None = None):
        import anthropic

        self.client = client or anthropic.Anthropic()

    def complete(self, *, model, system, messages, tools=None, effort=None,
                 json_schema=None, max_tokens=16000) -> Completion:
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
            "betas": ["server-side-fallback-2026-07-01"],
            "fallbacks": "default",
        }
        if tools:
            kwargs["tools"] = tools
        output_config: dict[str, Any] = {}
        if effort:
            output_config["effort"] = effort
        if json_schema:
            output_config["format"] = {"type": "json_schema", "schema": json_schema}
        if output_config:
            kwargs["output_config"] = output_config

        resp = self.client.beta.messages.create(**kwargs)
        usage = resp.usage.model_dump() if resp.usage else {}
        return Completion(
            content=[b.model_dump(exclude_none=True) for b in resp.content],
            stop_reason=resp.stop_reason or "",
            model=resp.model or model,
            input_tokens=usage.get("input_tokens") or 0,
            output_tokens=usage.get("output_tokens") or 0,
        )


# ── the loop ──────────────────────────────────────────────────────────────

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
    tool_calls: list[ToolCall] = field(default_factory=list)
    pending_approval: dict[str, Any] | None = None
    working_memory: WorkingMemory | None = None


class Agent:
    def __init__(self, release: Release, llm: LLM, store: Store, *, embedder: Embedder | None = None,
                 backend: Backend | None = None, tools: list[Tool] | None = None, consolidate: bool = True,
                 procedural: ProceduralMemory | None = None):
        self.release, self.llm, self.store = release, llm, store
        self.embedder = embedder or HashingEmbedder()
        self.backend = backend or Backend()
        self.tools = {t.name: t for t in (tools or TOOLS)}
        self.procedural = procedural or ProceduralMemory()
        self.semantic = SemanticMemory(store, self.embedder)
        self.episodic = EpisodicMemory(store, self.embedder)
        self.consolidator = Consolidator(release, llm, store, self.embedder) if consolidate else None

    def run(self, user_id: str, chat_id: str, prompt: str, *, approved: set[str] = frozenset()) -> RunResult:
        wm = build_working_memory(self.release, self.procedural, self.semantic, self.episodic, user_id, chat_id, prompt)
        result = self._loop(wm, approved)
        result.working_memory = wm

        self.episodic.save(user_id, chat_id, "user", prompt)
        self.episodic.save(user_id, chat_id, "assistant", result.reply)
        if self.consolidator:
            self.consolidator.maybe_run(user_id)
        return result

    def _loop(self, wm: WorkingMemory, approved: set[str]) -> RunResult:
        r = self.release
        messages = list(wm.messages)
        specs = [t.spec() for t in self.tools.values()]
        calls: list[ToolCall] = []
        cost = 0.0

        for step in range(1, r.max_steps + 1):
            if cost >= r.max_cost_usd:
                return RunResult(f"I stopped before finishing: this request hit the ${r.max_cost_usd:.2f} cost limit.",
                                 "max_cost", step - 1, cost, calls)

            c = self.llm.complete(model=r.agent_model, system=wm.system, messages=messages,
                                  tools=specs, effort=r.agent_effort)
            cost += c.cost_usd
            messages.append({"role": "assistant", "content": c.content})

            if c.stop_reason == "refusal":
                return RunResult("I can't help with that request.", "refusal", step, cost, calls)
            if not c.tool_uses:
                return RunResult(c.text.strip(), "done", step, cost, calls)

            results, stop = [], None
            for tu in c.tool_uses:
                call, block, stop_here = self._call_tool(tu, approved)
                calls.append(call)
                results.append(block)
                stop = stop or stop_here
            messages.append({"role": "user", "content": results})

            if stop:
                kind, reply, pending = stop
                return RunResult(reply, kind, step, cost, calls, pending_approval=pending)

        done = ", ".join(c.name for c in calls) or "nothing"
        return RunResult(f"I stopped after {r.max_steps} steps without finishing. Here is what I did: {done}.",
                         "max_steps", r.max_steps, cost, calls)

    def _call_tool(self, tu: dict, approved: set[str]):
        name, args = tu["name"], tu.get("input") or {}
        tool = self.tools.get(name)
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
        block = {"type": "tool_result", "tool_use_id": tu["id"],
                 "content": out if isinstance(out, str) else json.dumps(out), "is_error": err}
        return ToolCall(name, args, out, err), block, stop
