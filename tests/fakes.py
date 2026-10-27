"""A scripted stand-in for the model, so every harness path is tested offline."""
from __future__ import annotations

import copy
import itertools
import json
from typing import Any, Callable

from harness.agent import Completion

_ids = itertools.count(1)


def text(t: str, model: str = "claude-opus-5-5", cost_tokens: int = 100) -> Completion:
    return Completion([{"type": "text", "text": t}], "end_turn", model, cost_tokens, cost_tokens)


def tool(*calls: tuple[str, dict], model: str = "claude-opus-5-5", cost_tokens: int = 100) -> Completion:
    blocks = [{"type": "tool_use", "id": f"tu_{next(_ids)}", "name": n, "input": a} for n, a in calls]
    return Completion(blocks, "tool_use", model, cost_tokens, cost_tokens)


def as_json(obj: Any, model: str = "claude-haiku-5-5") -> Completion:
    return Completion([{"type": "text", "text": json.dumps(obj)}], "end_turn", model, 50, 50)


class FakeLLM:
    """Routes each call to `script(call)`; records every call for assertions."""

    def __init__(self, script: Callable[[dict], Completion]):
        self.script = script
        self.calls: list[dict] = []

    def complete(self, **kwargs) -> Completion:
        self.calls.append(copy.deepcopy(kwargs))  # the loop keeps appending to messages
        return self.script(kwargs)


class Sequence:
    """Returns agent completions in order, per run; summarizer calls go to `side`."""

    def __init__(self, *steps: Completion, side: Callable[[dict], Completion] | None = None):
        self.steps = list(steps)
        self.side = side

    def __call__(self, call: dict) -> Completion:
        if call.get("json_schema") is not None:
            assert self.side, "unexpected structured-output call"
            return self.side(call)
        return self.steps.pop(0)
