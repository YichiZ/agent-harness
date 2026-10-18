"""CLI.

  python -m harness chat --user op-1             interactive chat (memory persists in harness.db)
  python -m harness eval                         run the eval set; exit 1 if the gate fails
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
    c = sub.add_parser("chat")
    c.add_argument("--user", default="op-1")
    c.add_argument("--db", default=str(ROOT / "harness.db"))
    e = sub.add_parser("eval")
    e.add_argument("--out", default=None)
    t = sub.add_parser("tau2", help="run on τ²-bench; exit 1 if pass^1 is under the gate")
    t.add_argument("--domain", default="airline")
    t.add_argument("--tasks", default=None, help="comma-separated task ids (default: all)")
    t.add_argument("--num-tasks", type=int, default=None)
    t.add_argument("--trials", type=int, default=1, help="attempts per task, for pass^k")
    t.add_argument("--user-llm", default=None, help="litellm model id for the simulated user")
    t.add_argument("--human", action="store_true", help="you type the customer's side; result is not saved")
    k = sub.add_parser("consolidate")
    k.add_argument("--user", default="op-1")
    k.add_argument("--db", default=str(ROOT / "harness.db"))
    args = p.parse_args(argv)

    release = Release.load()
    llm = AnthropicLLM()

    if args.cmd == "eval":
        from .evals import run_evals

        report = run_evals(release, llm)
        out = Path(args.out or ROOT / "evals" / "results" / f"{release.tag}.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report.to_json(), indent=2))
        for case in report.cases:
            mark = "PASS" if case.passed else "FAIL"
            print(f"{mark} {case.id:20} judge={case.judge_score} stop={case.stop} {', '.join(case.failed_checks)}")
        print(f"\nrelease {release.tag}: pass rate {report.pass_rate:.0%}, mean judge {report.mean_judge:.2f}"
              f" -> gate {'PASSED' if report.gate_passed else 'FAILED'}  ({out})")
        return 0 if report.gate_passed else 1

    if args.cmd == "tau2":
        from .bench.tau2 import human_user, run_tau2, save

        report = run_tau2(release, llm, domain=args.domain, num_tasks=args.num_tasks, trials=args.trials,
                          task_ids=args.tasks.split(",") if args.tasks else None, user_llm=args.user_llm,
                          user_factory=human_user if args.human else None)
        if args.human:
            for a in report.attempts:
                print(f"\ntask {a.task_id}: reward {a.reward} (db match {a.db_match}), "
                      f"agent cost ${a.cost_usd:.2f}, trace {a.trace_id}")
            return 0
        out = save(report)
        summary = report.to_json()
        print(f"{args.domain} release {release.tag}: "
              + ", ".join(f"{k} {v:.0%}" for k, v in summary.items() if k.startswith("pass^"))
              + f", cost ${summary['total_cost_usd']:.2f} -> gate {'PASSED' if report.gate_passed else 'FAILED'}  ({out})")
        return 0 if report.gate_passed else 1

    store = Store(args.db)
    agent = Agent(release, llm, store)
    if args.cmd == "consolidate":
        print(json.dumps(agent.consolidator.run(args.user), indent=2))
        return 0

    chat_id = uuid.uuid4().hex[:8]
    print(f"release {release.tag}, chat {chat_id}. Ctrl-D to quit.")
    for line in _lines():
        res = agent.run(args.user, chat_id, line)
        print(res.reply)
        if res.pending_approval and input("approve? [y/N] ").strip().lower() == "y":
            res = agent.run(args.user, chat_id, f"Approved. Go ahead with: {line}",
                            approved={res.pending_approval["tool"]})
            print(res.reply)
        print(f"  [{res.stop}, {res.steps} steps, ${res.cost_usd:.4f}, trace {res.trace_id}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
