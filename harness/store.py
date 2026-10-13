"""Durable storage for the two long-term memories (SQLite; Postgres + pgvector in prod).

- episodes: append-only, timestamped log of every message (episodic memory).
  SQL answers recency ("last 3 chats"), the embedding column answers relevance.
- facts: distilled, durable facts per user (semantic memory).
- consolidation_state: watermark so the summarizer only reads new episodes.
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

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
