"""The four memories from the diagram, and the working memory built from them.

Working memory (the context window for one run) =
    system prompt
  + procedural memory: skill .md files whose triggers match the request
  + semantic memory:   top-k durable facts about this user (vector search)
  + episodic memory:   recent chats (SQL) + relevant past messages (vector search)
  + current chat history
  + the user prompt
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import ROOT, Release
from .embed import Embedder, cosine
from .store import Store

MIN_SIMILARITY = 0.15  # below this a memory is noise; leaving it out keeps the context lean


@dataclass
class Skill:
    name: str
    description: str
    triggers: list[str]
    body: str


class ProceduralMemory:
    """Skill files: how to act. Loaded only when the request matches a trigger."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills = [self._parse(p) for p in sorted((skills_dir or ROOT / "skills").glob("*.md"))]

    @staticmethod
    def _parse(path: Path) -> Skill:
        text = path.read_text()
        meta: dict[str, str] = {}
        body = text
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
            body = m.group(2)
        triggers = [t.strip().lower() for t in meta.get("triggers", "").split(",") if t.strip()]
        return Skill(meta.get("name", path.stem), meta.get("description", ""), triggers, body.strip())

    def select(self, prompt: str) -> list[Skill]:
        p = prompt.lower()
        return [s for s in self.skills if any(t in p for t in s.triggers)]


class SemanticMemory:
    def __init__(self, store: Store, embedder: Embedder):
        self.store, self.embedder = store, embedder

    def search(self, user_id: str, query: str, k: int) -> list[str]:
        facts = self.store.facts(user_id)
        if not facts:
            return []
        [q] = self.embedder.embed([query])
        scored = sorted(((cosine(q, f.embedding), f.fact) for f in facts), reverse=True)
        return [fact for score, fact in scored[:k] if score >= MIN_SIMILARITY]


class EpisodicMemory:
    def __init__(self, store: Store, embedder: Embedder):
        self.store, self.embedder = store, embedder

    def save(self, user_id: str, chat_id: str, role: str, content: str) -> None:
        [vec] = self.embedder.embed([content])
        self.store.add_episode(user_id, chat_id, role, content, vec)

    def history(self, user_id: str, chat_id: str, turns: int) -> list[dict]:
        eps = self.store.episodes(user_id, chat_id=chat_id)[-turns:]
        msgs = [{"role": e.role, "content": e.content} for e in eps]
        while msgs and msgs[0]["role"] != "user":  # the API needs a user turn first
            msgs.pop(0)
        return msgs

    def recall(self, user_id: str, chat_id: str, query: str, *, recent_k: int, top_k: int) -> list[str]:
        """SQL for recency + vectors for relevance, from chats other than this one."""
        past = self.store.episodes(user_id, exclude_chat=chat_id)
        if not past:
            return []
        recent_chats = set(self.store.recent_chat_ids(user_id, recent_k, exclude_chat=chat_id))
        picked = {e.id: e for e in past if e.chat_id in recent_chats and e.role == "user"}
        [q] = self.embedder.embed([query])
        for score, e in sorted(((cosine(q, e.embedding), e) for e in past), key=lambda x: -x[0])[:top_k]:
            if score >= MIN_SIMILARITY:
                picked[e.id] = e
        return [f"[chat {e.chat_id}] {e.role}: {e.content}" for e in sorted(picked.values(), key=lambda e: e.id)]


@dataclass
class WorkingMemory:
    system: str
    messages: list[dict]
    skills: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    episodes: list[str] = field(default_factory=list)


def build_working_memory(release: Release, procedural: ProceduralMemory, semantic: SemanticMemory,
                         episodic: EpisodicMemory, user_id: str, chat_id: str, prompt: str) -> WorkingMemory:
    skills = procedural.select(prompt)
    facts = semantic.search(user_id, prompt, release.semantic_top_k)
    episodes = episodic.recall(user_id, chat_id, prompt,
                               recent_k=release.episodic_recent_k, top_k=release.episodic_top_k)

    sections = [release.system_prompt().strip()]
    if skills:
        sections.append("# Skills for this request\n\n" + "\n\n".join(f"## {s.name}\n{s.body}" for s in skills))
    if facts:
        sections.append("# What you know about this operator\n" + "\n".join(f"- {f}" for f in facts))
    if episodes:
        sections.append("# Relevant past conversations\n" + "\n".join(f"- {e}" for e in episodes))

    messages = episodic.history(user_id, chat_id, release.history_turns)
    messages.append({"role": "user", "content": prompt})
    return WorkingMemory("\n\n".join(sections), messages, [s.name for s in skills], facts, episodes)
