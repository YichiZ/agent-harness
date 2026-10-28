"""Memory: storage, embeddings, the four memories, and consolidation.

Working memory (the context window for one run) =
    system prompt
  + procedural memory: skill .md files whose triggers match the request
  + semantic memory:   top-k durable facts about this user (vector search)
  + episodic memory:   recent chats (SQL) + relevant past messages (vector search)
  + current chat history
  + the user prompt

Episodes and facts live in SQLite (Postgres + pgvector in prod). The embedder is
a deterministic hashed bag-of-words so everything runs offline; swap in a real
model behind `Embedder.embed`. Every N chats the summarizer (cheaper model)
distills new episodes into facts; a near-duplicate fact is replaced, not appended.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .agent import LLM, Release

ROOT = Path(__file__).resolve().parent.parent


# ── embeddings ────────────────────────────────────────────────────────────

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it", "that", "this", "with", "be", "was", "are", "i", "you", "me", "my"}


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _TOKEN.findall(text.lower()):
            if tok in _STOP:
                continue
            tok = tok[:-1] if len(tok) > 3 and tok.endswith("s") else tok  # crude plural fold
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0 if (h >> 8) & 1 else -1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # inputs are unit-normalised


# ── storage ───────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  chat_id TEXT NOT NULL,
  ts REAL NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS episodes_user_ts ON episodes (user_id, ts);
CREATE TABLE IF NOT EXISTS facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  fact TEXT NOT NULL,
  embedding TEXT NOT NULL,
  source_chat_ids TEXT NOT NULL,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS facts_user ON facts (user_id);
CREATE TABLE IF NOT EXISTS consolidation_state (
  user_id TEXT PRIMARY KEY,
  last_episode_id INTEGER NOT NULL
);
"""


@dataclass
class Episode:
    id: int
    user_id: str
    chat_id: str
    ts: float
    role: str
    content: str
    embedding: list[float]


@dataclass
class Fact:
    id: int
    user_id: str
    fact: str
    embedding: list[float]
    source_chat_ids: list[str]
    updated_at: float


class Store:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(str(path))
        self.db.executescript(SCHEMA)

    # ── episodic ──────────────────────────────────────────────────────────
    def add_episode(self, user_id: str, chat_id: str, role: str, content: str,
                    embedding: list[float], ts: float | None = None) -> int:
        cur = self.db.execute(
            "INSERT INTO episodes (user_id, chat_id, ts, role, content, embedding) VALUES (?,?,?,?,?,?)",
            (user_id, chat_id, ts or time.time(), role, content, json.dumps(embedding)),
        )
        self.db.commit()
        return cur.lastrowid

    def episodes(self, user_id: str, *, after_id: int = 0, chat_id: str | None = None,
                 exclude_chat: str | None = None) -> list[Episode]:
        sql = "SELECT id, user_id, chat_id, ts, role, content, embedding FROM episodes WHERE user_id = ? AND id > ?"
        args: list = [user_id, after_id]
        if chat_id:
            sql += " AND chat_id = ?"
            args.append(chat_id)
        if exclude_chat:
            sql += " AND chat_id != ?"
            args.append(exclude_chat)
        rows = self.db.execute(sql + " ORDER BY id", args).fetchall()
        return [Episode(*r[:6], json.loads(r[6])) for r in rows]

    def recent_chat_ids(self, user_id: str, limit: int, exclude_chat: str | None = None) -> list[str]:
        rows = self.db.execute(
            "SELECT chat_id, MAX(id) AS last FROM episodes WHERE user_id = ? AND chat_id != ? "
            "GROUP BY chat_id ORDER BY last DESC LIMIT ?",
            (user_id, exclude_chat or "", limit),
        ).fetchall()
        return [r[0] for r in rows]

    # ── semantic ──────────────────────────────────────────────────────────
    def facts(self, user_id: str) -> list[Fact]:
        rows = self.db.execute(
            "SELECT id, user_id, fact, embedding, source_chat_ids, updated_at FROM facts WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
        return [Fact(r[0], r[1], r[2], json.loads(r[3]), json.loads(r[4]), r[5]) for r in rows]

    def add_fact(self, user_id: str, fact: str, embedding: list[float], source_chat_ids: list[str]) -> int:
        now = time.time()
        cur = self.db.execute(
            "INSERT INTO facts (user_id, fact, embedding, source_chat_ids, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (user_id, fact, json.dumps(embedding), json.dumps(source_chat_ids), now, now),
        )
        self.db.commit()
        return cur.lastrowid

    def replace_fact(self, fact_id: int, fact: str, embedding: list[float], source_chat_ids: list[str]) -> None:
        self.db.execute(
            "UPDATE facts SET fact = ?, embedding = ?, source_chat_ids = ?, updated_at = ? WHERE id = ?",
            (fact, json.dumps(embedding), json.dumps(source_chat_ids), time.time(), fact_id),
        )
        self.db.commit()

    # ── consolidation watermark ───────────────────────────────────────────
    def watermark(self, user_id: str) -> int:
        row = self.db.execute("SELECT last_episode_id FROM consolidation_state WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else 0

    def set_watermark(self, user_id: str, episode_id: int) -> None:
        self.db.execute(
            "INSERT INTO consolidation_state (user_id, last_episode_id) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_episode_id = excluded.last_episode_id",
            (user_id, episode_id),
        )
        self.db.commit()


# ── the four memories ─────────────────────────────────────────────────────

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

    h = release.headings()
    sections = [release.system_prompt().strip()]
    if skills:
        sections.append(f"# {h['skills']}\n\n" + "\n\n".join(f"## {s.name}\n{s.body}" for s in skills))
    if facts:
        sections.append(f"# {h['facts']}\n" + "\n".join(f"- {f}" for f in facts))
    if episodes:
        sections.append(f"# {h['episodes']}\n" + "\n".join(f"- {e}" for e in episodes))

    messages = episodic.history(user_id, chat_id, release.history_turns)
    messages.append({"role": "user", "content": prompt})
    return WorkingMemory("\n\n".join(sections), messages, [s.name for s in skills], facts, episodes)


# ── consolidation: episodic -> semantic, only after N new chats ───────────

REPLACE_SIMILARITY = 0.6

FACTS_SCHEMA = {
    "type": "object",
    "properties": {"facts": {"type": "array", "items": {"type": "string"}}},
    "required": ["facts"],
    "additionalProperties": False,
}


class Consolidator:
    def __init__(self, release: "Release", llm: "LLM", store: Store, embedder: Embedder):
        self.release, self.llm, self.store, self.embedder = release, llm, store, embedder

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
        h = self.release.headings()
        known = "\n".join(f"- {f.fact}" for f in existing) or h["no_facts"]
        prompt = f"{h['existing_facts']}:\n{known}\n\n{h['log']}:\n{log}"

        c = self.llm.complete(model=self.release.summarizer_model, system=self.release.summarizer_prompt(),
                              messages=[{"role": "user", "content": prompt}],
                              json_schema=FACTS_SCHEMA, max_tokens=4000)
        facts = [f.strip() for f in json.loads(c.text or '{"facts": []}').get("facts", []) if f.strip()]

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
