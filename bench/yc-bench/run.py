"""Run the harness agent on YC-Bench (https://github.com/collinear-ai/yc-bench).

  uv run python bench/yc-bench/run.py --fake --max-checkpoints 3       offline, scripted model
  uv run python bench/yc-bench/run.py --seed 1 --max-checkpoints 10    real run (costs money)

Each checkpoint is one harness chat: the agent sees the company state, runs
`yc-bench` commands, and writes a short note. The runner then calls
`yc-bench sim resume` to advance time to the next event. Episodic and semantic
memory carry what the agent learned from one checkpoint to the next, in place
of YC-Bench's scratchpad.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
import os
import sys
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from harness.__main__ import load_env  # noqa: E402
from harness.agent import Agent, AnthropicLLM, Completion, Release  # noqa: E402
from harness.memory import ProceduralMemory, Store  # noqa: E402
from harness.tools import Tool, _obj  # noqa: E402

STDOUT_LIMIT = 12_000
REFUSED = {
    "sim resume": "the runner advances time after you reply; just finish your turn",
    "scratchpad": "your notes are kept by the harness memory; put them in your reply instead",
}


# ── model: a cost meter around every completion (agent and summarizer) ─────

class CostMeter:
    def __init__(self, llm: Any):
        self.llm, self.total, self.calls = llm, 0.0, 0

    def complete(self, **kwargs) -> Completion:
        c = self.llm.complete(**kwargs)
        self.total += c.cost_usd
        self.calls += 1
        return c


class FakeLLM:
    """Scripted model for --fake: browse, then accept/assign/dispatch, then a note."""

    def __init__(self):
        self.ids = itertools.count(1)

    def complete(self, *, model, messages, json_schema=None, **_) -> Completion:
        if json_schema:
            return self._text(model, json.dumps({"facts": ["BenchCo ran a scripted checkpoint."]}))
        step = 1 + sum(1 for m in messages if m["role"] == "assistant" and isinstance(m["content"], list))
        if step == 1:
            return self._tools(model, "yc-bench market browse --limit 5", "yc-bench employee list")
        if step == 2:
            browse, employees = (_parse(_parse(b["content"]).get("stdout") or "") for b in messages[-1]["content"])
            task = next((t for t in browse.get("tasks", []) if not t.get("required_trust")), None)
            if task is None:
                return self._text(model, "No task I can accept right now.")
            names = ",".join(e["name"] for e in employees.get("employees", [])[:3])
            tid = task["task_id"]
            return self._tools(model, f"yc-bench task accept --task-id {tid}",
                               f"yc-bench task assign --task-id {tid} --employees {names}",
                               f"yc-bench task dispatch --task-id {tid}")
        return self._text(model, "Accepted, assigned and dispatched one task.")

    def _tools(self, model: str, *commands: str) -> Completion:
        blocks = [{"type": "tool_use", "id": f"fake_{next(self.ids)}", "name": "run_command",
                   "input": {"command": c}} for c in commands]
        return Completion(blocks, "tool_use", model)

    @staticmethod
    def _text(model: str, text: str) -> Completion:
        return Completion([{"type": "text", "text": text}], "end_turn", model)


def _parse(text: str) -> dict:
    try:
        obj = json.loads(text)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


# ── the one tool ──────────────────────────────────────────────────────────

def run_command_tool(execute) -> Tool:
    def run(_backend, a: dict) -> dict:
        cmd = a["command"]
        for word, why in REFUSED.items():
            if word in cmd:
                raise ValueError(f"`{word}` is not available here: {why}.")
        r = execute(cmd)
        out = r.get("stdout") or ""
        if len(out) > STDOUT_LIMIT:
            out = out[:STDOUT_LIMIT] + "\n[truncated]"
        return {"ok": r.get("ok"), "exit_code": r.get("exit_code"), "stdout": out, "stderr": r.get("stderr") or ""}

    return Tool("run_command", "Run one `yc-bench` CLI command and get its JSON output.",
                _obj({"command": {"type": "string", "description": "e.g. yc-bench market browse --limit 10"}},
                     ["command"]), run)


# ── prompts and printing ──────────────────────────────────────────────────

def _usd(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def event_line(ev: dict) -> str:
    rest = {k: v for k, v in ev.items() if k != "type"}
    for k in [k for k in rest if k in ("funds_delta", "listed_reward") or k.endswith("_cents")]:  # cents read as dollars otherwise
        rest[k.removesuffix("_cents") + "_usd"] = rest.pop(k) / 100
    return f"- {ev.get('type', 'event')}: {json.dumps(rest, default=str)}"


def checkpoint_prompt(n: int, s: dict, wake_events: list[dict], resume_error: str | None) -> str:
    payroll = s["monthly_payroll_cents"]
    runway = f"~{s['funds_cents'] / payroll:.1f} months" if payroll else "unlimited (no payroll)"
    lines = [f"## Checkpoint {n}"]
    if n == 1:
        lines.append("This is the start of the simulation. No time has passed yet.")
    lines += [
        f"- sim time: {s['sim_time']}",
        f"- horizon end: {s['horizon_end']}",
        f"- funds: {_usd(s['funds_cents'])}",
        f"- monthly payroll: {_usd(payroll)}",
        f"- runway: {runway}",
        f"- employees: {s['employee_count']}",
        f"- active tasks: {s['active_tasks']}, planned tasks: {s['planned_tasks']}",
    ]
    if resume_error:
        lines.append(f"\nThe runner could not advance time: {resume_error}")
    if wake_events:
        lines.append("\n### Events since the last checkpoint")
        lines += [event_line(ev) for ev in wake_events]
    return "\n".join(lines)


# ── run.md: a readable log, appended per checkpoint so a crash still leaves one ──

def _text(v: Any) -> str:
    """Undo `readable`: a list of lines or a nested object back to text."""
    if isinstance(v, list) and all(isinstance(x, str) for x in v):
        return "\n".join(v)
    return v if isinstance(v, str) else json.dumps(v)


def _one_line(text: Any, limit: int = 140) -> str:
    text = " ".join(_text(text).split())
    return text if len(text) <= limit else text[:limit] + "…"


def header_md(seed: int, config: str, model: str, started_at: str, release: dict | None) -> str:
    settings = ", ".join(f"{k} {v}" for k, v in (release or {}).items()) or "not recorded"
    return (f"# YC-Bench run: seed {seed}, {model}\n\n"
            f"- started: {started_at}\n- config: {config}\n- release: {settings}\n")


def checkpoint_md(rec: dict) -> str:
    lines = [f"\n## Checkpoint {rec['checkpoint']} · {rec['sim_time_before']}\n",
             f"Funds {_usd(rec['funds_before'])} → {_usd(rec['funds_after'])}, "
             f"sim time → {rec['sim_time_after']}\n"]
    if rec.get("resume_error"):
        lines.append(f"Resume failed: {rec['resume_error']}\n")
    lines.append("**Commands**\n")
    for call in rec["tool_calls"]:
        res = call["result"]
        if isinstance(res, dict):
            failed = call["is_error"] or not res.get("ok")
            res = res.get("stdout") or res.get("stderr")
        else:
            failed = call["is_error"]
        lines.append(f"- {'✗' if failed else '$'} `{call['input'].get('command', '')}` → {_one_line(res, 120)}")
    lines.append("\n**Note**\n")
    lines += [f"> {line}" for line in _text(rec["reply"]).splitlines()]
    lines.append(f"\n{rec['stop']}, {rec['steps']} steps, {rec['model_calls']} model calls, "
                 f"${rec['cost_usd']:.4f} (total ${rec['total_cost_usd']:.4f})\n")
    episodes = rec["recalled_episodes"]  # a count in runs before checkpoints/ existed
    lines.append(f"**Memory it saw:** {len(rec['facts'])} facts, "
                 f"{episodes if isinstance(episodes, int) else len(episodes)} recalled episodes")
    lines += [f"- {f}" for f in rec["facts"]]
    if rec["wake_events"]:
        lines.append("\n**Events when time advanced**\n")
        lines += [event_line(ev) for ev in rec["wake_events"]]
    return "\n".join(lines) + "\n"


def summary_md(s: dict) -> str:
    lines = ["\n## Summary\n",
             f"- terminal reason: {s['terminal_reason']}",
             f"- checkpoints: {s['checkpoints']}, sim time {s['sim_time']}",
             f"- final funds: {_usd(s['final_funds_cents'])}",
             f"- cost: ${s['total_cost_usd']:.4f} over {s['model_calls']} model calls",
             f"\n**Facts in memory at the end ({len(s['facts'])})**\n"]
    lines += [f"- {f}" for f in s["facts"]]
    return "\n".join(lines) + "\n"


def readable(obj: Any) -> Any:
    """For the JSON files: embedded JSON becomes nested objects, multi-line text a list of lines."""
    if isinstance(obj, dict):
        return {k: readable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [readable(v) for v in obj]
    if isinstance(obj, str):
        if obj.lstrip()[:1] in ("{", "["):
            try:
                return readable(json.loads(obj))
            except ValueError:
                pass
        if "\n" in obj:
            return obj.splitlines()
    return obj


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(readable(obj), indent=2, ensure_ascii=False, default=str) + "\n")


def load_checkpoints(run_dir: Path) -> list[dict]:
    """checkpoints/cp-NNN.json; an older run's checkpoints.jsonl is converted to that layout first."""
    cp_dir, old = run_dir / "checkpoints", run_dir / "checkpoints.jsonl"
    if not cp_dir.is_dir() and old.exists():
        for line in old.read_text().splitlines():
            rec = json.loads(line)
            system = rec.pop("system")
            if rec["checkpoint"] == 1:  # no memory sections yet, so this is the bare system prompt
                (run_dir / "system_prompt.md").write_text(system)
            write_json(cp_dir / f"cp-{rec['checkpoint']:03d}.json", rec)
    return [json.loads(p.read_text()) for p in sorted(cp_dir.glob("cp-*.json"))]


def render(run_dir: Path) -> int:
    """Rebuild run.md from a run's checkpoints and summary.json."""
    rows = load_checkpoints(run_dir)
    summary = json.loads((run_dir / "summary.json").read_text())
    write_json(run_dir / "summary.json", summary)
    md = header_md(summary["seed"], summary["config"], summary["model"],
                   summary.get("started_at", "not recorded"), summary.get("release"))
    md += "".join(checkpoint_md(r) for r in rows) + summary_md(summary)
    (run_dir / "run.md").write_text(md)
    print(f"wrote {run_dir / 'run.md'}")
    return 0


# ── main ──────────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="run.py")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--config", default="default")
    p.add_argument("--model", help="overrides agent_model in bench/yc-bench/release.json")
    p.add_argument("--max-checkpoints", type=int)
    p.add_argument("--max-cost", type=float, default=30.0, help="total USD cap, summarizer included")
    p.add_argument("--out", type=Path)
    p.add_argument("--fake", action="store_true", help="offline scripted model, no API calls")
    p.add_argument("--render", type=Path, metavar="RUN_DIR", help="only rebuild RUN_DIR/run.md, then exit")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.render:
        return render(args.render)
    started_at = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
    out = (args.out or HERE / "runs" / f"{datetime.now():%Y%m%d-%H%M%S}-seed{args.seed}").resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Set before importing yc_bench: the CLI subprocesses read these too.
    os.environ["DATABASE_URL"] = f"sqlite:///{out / 'world.db'}"
    os.environ["YC_BENCH_EXPERIMENT"] = args.config
    load_env()

    from yc_bench.agent.commands.executor import run_command
    from yc_bench.agent.loop import _snapshot_state
    from yc_bench.config import load_config
    from yc_bench.db.session import build_engine, build_session_factory, init_db, session_scope
    from yc_bench.runner.extract import extract_time_series
    from yc_bench.runner.main import _init_simulation

    cfg = load_config(args.config)
    engine = build_engine()
    init_db(engine)
    factory = build_session_factory(engine)

    @contextmanager
    def db():
        with session_scope(factory) as session:
            yield session

    company_id = _init_simulation(db, SimpleNamespace(seed=args.seed, company_name="BenchCo", start_date="2025-01-01"),
                                  cfg, cfg.sim.horizon_years)

    release = Release.load(HERE / "release.json")
    if args.model:
        release = dataclasses.replace(release, agent_model=args.model)
    meter = CostMeter(FakeLLM() if args.fake else AnthropicLLM())
    agent = Agent(release, meter, Store(out / "memory.db"), tools=[run_command_tool(run_command)],
                  procedural=ProceduralMemory(skills_dir=out / "no-skills"))
    user_id = f"ycbench-seed{args.seed}"
    model = "fake" if args.fake else release.agent_model
    log = out / "run.md"
    log.write_text(header_md(args.seed, args.config, model, started_at, dataclasses.asdict(release)))
    (out / "system_prompt.md").write_text(release.system_prompt())
    print(f"YC-Bench seed {args.seed}, config {args.config}, model {model} → {out}")

    wake_events: list[dict] = []
    resume_error: str | None = None
    n, stop = 0, None
    try:
        while stop is None:
            if args.max_checkpoints is not None and n >= args.max_checkpoints:
                stop = "max_checkpoints"
                break
            if meter.total >= args.max_cost:
                stop = "max_cost"
                break
            n += 1
            with db() as s:
                before = _snapshot_state(s, company_id)
            prompt = checkpoint_prompt(n, before, wake_events, resume_error)
            spent, calls = meter.total, meter.calls
            res = agent.run(user_id, f"cp-{n:03d}", prompt)

            raw = run_command("yc-bench sim resume")
            payload = _parse(raw.get("stdout") or "")
            if payload.get("ok"):
                wake_events, resume_error = payload.get("wake_events") or [], None
                if payload.get("terminal_reason") in ("bankruptcy", "horizon_end"):
                    stop = payload["terminal_reason"]
            else:
                wake_events = []
                resume_error = payload.get("error") or raw.get("stderr") or "sim resume failed"
            with db() as s:
                after = _snapshot_state(s, company_id)

            wm = res.working_memory
            rec = {
                "checkpoint": n, "prompt": prompt,
                "tool_calls": [dataclasses.asdict(c) for c in res.tool_calls],
                "reply": res.reply, "stop": res.stop, "steps": res.steps,
                "model_calls": meter.calls - calls,
                "cost_usd": meter.total - spent, "total_cost_usd": meter.total,
                "sim_time_before": before["sim_time"], "sim_time_after": after["sim_time"],
                "funds_before": before["funds_cents"], "funds_after": after["funds_cents"],
                "wake_events": wake_events, "resume_error": resume_error,
                "facts": wm.facts, "recalled_episodes": wm.episodes,
            }
            block = checkpoint_md(rec)
            print(block)
            with open(log, "a") as f:
                f.write(block)
            write_json(out / "checkpoints" / f"cp-{n:03d}.json", rec)
    except Exception as e:  # keep the partial run: the summary still gets written
        traceback.print_exc()
        stop = f"error: {type(e).__name__}: {e}"

    with db() as s:
        final = _snapshot_state(s, company_id)
    summary = {
        "seed": args.seed, "config": args.config, "model": model, "started_at": started_at,
        "release": dataclasses.asdict(release),
        "checkpoints": n, "terminal_reason": stop, "sim_time": final["sim_time"],
        "final_funds_cents": final["funds_cents"], "total_cost_usd": round(meter.total, 4),
        "model_calls": meter.calls, "facts": [f.fact for f in agent.store.facts(user_id)],
        "time_series": extract_time_series(db, company_id),
    }
    write_json(out / "summary.json", summary)
    with open(log, "a") as f:
        f.write(summary_md(summary))
    print(summary_md(summary) + f"\n{out}")
    return 1 if stop.startswith("error") else 0


if __name__ == "__main__":
    sys.exit(main())
