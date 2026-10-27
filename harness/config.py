"""Agent config: models, loop budgets and memory knobs, read from release.json."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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

    @classmethod
    def load(cls, path: Path | None = None) -> "Release":
        return cls(**json.loads((path or ROOT / "release.json").read_text()))

    def system_prompt(self) -> str:
        return (ROOT / "prompts" / f"system.{self.prompt_version}.md").read_text()
