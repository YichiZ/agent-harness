"""One trace per run, in Langfuse (LLM Ops: Trace + Observe).

Each run is a tree: agent-run -> retrieval, llm call (generation), tool call,
guardrail. Tokens, cost and latency land on the generations; the release tag
lands on the trace so a regression can be pinned to the prompt/config that
caused it.

Optional: with no LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY the tracer is a
no-op and the harness runs the same.
"""
from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from typing import Any, Iterator


class _NullObs:
    def update(self, **_: Any) -> None: ...


class Tracer:
    def __init__(self) -> None:
        self.enabled = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
        self.lf = None
        if self.enabled:
            from langfuse import get_client

            self.lf = get_client()

    @contextmanager
    def run(self, *, user_id: str, chat_id: str, release_tag: str, prompt: str,
            tags: list[str] | None = None) -> Iterator[tuple[Any, str]]:
        """Yields (root observation, trace_id)."""
        if not self.lf:
            yield _NullObs(), f"local-{uuid.uuid4().hex[:12]}"
            return
        from langfuse import propagate_attributes

        with self.lf.start_as_current_observation(name="agent-run", as_type="agent", input=prompt) as root:
            with propagate_attributes(user_id=user_id, session_id=chat_id, version=release_tag,
                                      tags=[release_tag, *(tags or [])], trace_name="agent-run"):
                yield root, self.lf.get_current_trace_id()

    @contextmanager
    def span(self, name: str, as_type: str = "span", **kwargs: Any) -> Iterator[Any]:
        if not self.lf:
            yield _NullObs()
            return
        with self.lf.start_as_current_observation(name=name, as_type=as_type, **kwargs) as obs:
            yield obs

    def score(self, trace_id: str, name: str, value: float, comment: str | None = None) -> None:
        if self.lf and not trace_id.startswith("local-"):
            self.lf.create_score(trace_id=trace_id, name=name, value=value, comment=comment)

    def flush(self) -> None:
        if self.lf:
            self.lf.flush()
