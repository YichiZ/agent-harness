"""Release config: everything the LLM Ops "release" step is allowed to change.

A fix ships as a new prompt file and/or new values here, never as a code edit,
so every trace can be tied to exactly one release.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Release:
    prompt_version: str
    agent_model: str
    agent_effort: str
    summarizer_model: str
    judge_model: str
    max_steps: int
    max_cost_usd: float
    history_turns: int
    semantic_top_k: int
    episodic_top_k: int
    episodic_recent_k: int
    consolidate_every_n_chats: int
    gate_min_score: float
    gate_min_pass_rate: float
    tau2_user_model: str
    tau2_gate_min_pass: float

    @classmethod
    def load(cls, path: Path | None = None) -> "Release":
        return cls(**json.loads((path or ROOT / "release.json").read_text()))

    def system_prompt(self) -> str:
        return (ROOT / "prompts" / f"system.{self.prompt_version}.md").read_text()

    @property
    def tag(self) -> str:
        """Short id for this exact prompt + config, attached to every trace."""
        blob = self.system_prompt() + json.dumps(asdict(self), sort_keys=True)
        return f"{self.prompt_version}-{hashlib.sha256(blob.encode()).hexdigest()[:8]}"
