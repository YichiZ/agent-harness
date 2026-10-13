"""Model clients. The loop only sees `LLM.complete`, so tests swap in a fake."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

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
    raw_usage: dict[str, Any] = field(default_factory=dict)

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
            raw_usage={k: v for k, v in usage.items() if isinstance(v, int)},
        )
