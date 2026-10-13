"""Summarizer agent: episodic -> semantic memory, only after N new chats.

Consolidation reads every message since the user's watermark, so it is the most
token-heavy job in the harness. It runs on the cheaper summarizer model and
only once N new chats have piled up. A new fact that is close to an existing one
replaces it (the user changed their mind), so stale facts don't accumulate.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .embed import Embedder, cosine
from .store import Store

if TYPE_CHECKING:
    from .config import Release
    from .llm import LLM
    from .tracing import Tracer

REPLACE_SIMILARITY = 0.6

SUMMARIZER_SYSTEM = """You maintain long-term memory for an AI agent that works for one operator.
From the conversation log, extract durable facts worth remembering in future conversations:
the operator's preferences, standing instructions, recurring entities, and decisions.
Skip one-off task details, anything already true of every operator, and anything the agent said that the operator did not confirm.
Write each fact as one short, self-contained sentence. If a fact updates one in the existing list, write the updated version.
Return an empty list when there is nothing durable."""

FACTS_SCHEMA = {
    "type": "object",
    "properties": {"facts": {"type": "array", "items": {"type": "string"}}},
    "required": ["facts"],
    "additionalProperties": False,
}


class Consolidator:
    def __init__(self, release: "Release", llm: "LLM", store: Store, embedder: Embedder, tracer: "Tracer"):
        self.release, self.llm, self.store, self.embedder, self.tracer = release, llm, store, embedder, tracer

    def pending_chats(self, user_id: str) -> int:
        return len({e.chat_id for e in self.store.episodes(user_id, after_id=self.store.watermark(user_id))})

    def maybe_run(self, user_id: str, *, force: bool = False) -> list[str]:
        if not force and self.pending_chats(user_id) < self.release.consolidate_every_n_chats:
            return []
        return self.run(user_id)

    def run(self, user_id: str) -> list[str]:
        new = self.store.episodes(user_id, after_id=self.store.watermark(user_id))
        if not new:
            return []
        existing = self.store.facts(user_id)
        log = "\n".join(f"[chat {e.chat_id}] {e.role}: {e.content}" for e in new)
        known = "\n".join(f"- {f.fact}" for f in existing) or "(none)"
        prompt = f"Existing facts:\n{known}\n\nConversation log:\n{log}"

        with self.tracer.span("consolidate", as_type="generation", model=self.release.summarizer_model,
                              input=prompt, metadata={"user_id": user_id, "episodes": len(new)}) as gen:
            c = self.llm.complete(model=self.release.summarizer_model, system=SUMMARIZER_SYSTEM,
                                  messages=[{"role": "user", "content": prompt}],
                                  json_schema=FACTS_SCHEMA, max_tokens=4000)
            facts = [f.strip() for f in json.loads(c.text or '{"facts": []}').get("facts", []) if f.strip()]
            gen.update(output=facts, usage_details={"input": c.input_tokens, "output": c.output_tokens},
                       cost_details={"total": c.cost_usd})

        chat_ids = sorted({e.chat_id for e in new})
        vectors = self.embedder.embed(facts) if facts else []
        for fact, vec in zip(facts, vectors):
            best = max(existing, key=lambda f: cosine(vec, f.embedding), default=None)
            if best and cosine(vec, best.embedding) >= REPLACE_SIMILARITY:
                self.store.replace_fact(best.id, fact, vec, sorted(set(best.source_chat_ids) | set(chat_ids)))
            else:
                self.store.add_fact(user_id, fact, vec, chat_ids)
        self.store.set_watermark(user_id, new[-1].id)
        return facts
