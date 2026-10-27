"""CLI.

  python -m harness chat --user op-1             interactive chat (memory persists in harness.db)
  python -m harness consolidate --user op-1      force the summarizer to run now
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

from .config import ROOT, Release
from .llm import AnthropicLLM
from .loop import Agent
from .store import Store


def load_env(path: Path | None = None) -> None:
    """Load the repo `.env`. Variables already set in the environment win."""
    load_dotenv(path or ROOT / ".env")


def _lines():
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            return
        if line:
            yield line


def main(argv: list[str] | None = None) -> int:
    load_env()
    p = argparse.ArgumentParser(prog="harness")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("chat", "consolidate"):
        c = sub.add_parser(name)
        c.add_argument("--user", default="op-1")
        c.add_argument("--db", default=str(ROOT / "harness.db"))
    args = p.parse_args(argv)

    agent = Agent(Release.load(), AnthropicLLM(), Store(args.db))
    if args.cmd == "consolidate":
        print(json.dumps(agent.consolidator.run(args.user), indent=2))
        return 0

    chat_id = uuid.uuid4().hex[:8]
    print(f"chat {chat_id}. Ctrl-D to quit.")
    for line in _lines():
        res = agent.run(args.user, chat_id, line)
        print(res.reply)
        if res.pending_approval and input("approve? [y/N] ").strip().lower() == "y":
            res = agent.run(args.user, chat_id, f"Approved. Go ahead with: {line}",
                            approved={res.pending_approval["tool"]})
            print(res.reply)
        print(f"  [{res.stop}, {res.steps} steps, ${res.cost_usd:.4f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
