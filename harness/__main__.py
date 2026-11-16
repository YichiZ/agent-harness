"""CLI.

  python -m harness chat --user op-1             interactive chat (memory persists in harness.db)
  python -m harness consolidate --user op-1      force the summarizer to run now
  python -m harness eval --split dev --repeats 3 run the eval cases against the real model
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv

from .agent import LLM, AnthropicLLM, Agent, Release
from .evals import SPLITS, format_report, load_cases, report_json, run_evals
from .memory import ROOT, Store


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


def _eval(p: argparse.ArgumentParser, args: argparse.Namespace, llm: LLM) -> int:
    """Run the eval cases, print the report, save it as JSON. Exit 1 below --min-pass."""
    cases = [c for c in load_cases(split=args.split) if args.family in (None, c["family"])]
    if not cases:
        p.error(f"no {args.split} cases in family {args.family!r}")
    if args.repeats < 1:
        p.error("--repeats must be at least 1")
    release = Release.load()
    outcomes, stopped = run_evals(cases, release, llm, repeats=args.repeats, max_cost_usd=args.max_cost)

    tag = f"{args.split}-{release.prompt_version}-{release.agent_model}"
    print(format_report(outcomes, f"{tag} · {len(cases)} cases × {args.repeats}"))
    if stopped:
        print(f"Stopped early: the ${args.max_cost:.2f} cost cap was reached.")
    out = Path(args.out) / f"{time.strftime('%Y-%m-%d-%H%M%S')}-{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    report = report_json(outcomes, release, split=args.split, repeats=args.repeats, stopped_at_cost_cap=stopped)
    out.write_text(json.dumps(report, indent=2))
    print(f"Report: {out}")
    # A run the cost cap cut short never passes the gate: the cases it skipped were not tested.
    return 0 if not stopped and report["summary"]["pass_rate"] >= args.min_pass else 1


def main(argv: list[str] | None = None, *, llm: LLM | None = None) -> int:
    load_env()
    p = argparse.ArgumentParser(prog="harness")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("chat", "consolidate"):
        c = sub.add_parser(name)
        c.add_argument("--user", default="op-1")
        c.add_argument("--db", default=str(ROOT / "harness.db"))
    e = sub.add_parser("eval")
    e.add_argument("--split", choices=SPLITS, default="dev")
    e.add_argument("--family", help="only cases in this family, e.g. refund")
    e.add_argument("--repeats", type=int, default=1, help="runs per case")
    e.add_argument("--max-cost", type=float, default=5.0, help="stop once the run has spent this many dollars")
    e.add_argument("--min-pass", type=float, default=0.0, help="exit 1 when the pass rate is below this (0 to 1)")
    e.add_argument("--out", default=str(ROOT / "evals" / "runs"), help="directory for the JSON report")
    args = p.parse_args(argv)

    llm = llm or AnthropicLLM()
    if args.cmd == "eval":
        return _eval(p, args, llm)

    agent = Agent(Release.load(), llm, Store(args.db))
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
