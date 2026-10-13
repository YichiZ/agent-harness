"""LLM Ops: Eval -> Diagnose -> Gate.

Each case runs the real agent against a fresh backend, then is scored twice:
  - code checks on backend state and the tool calls (was the meeting booked?
    did it refund when it shouldn't have?), which are exact;
  - an LLM judge on a cheaper model, for what code can't check (was the reply
    accurate to the tool results, did it ask when it should have).
Both scores are written onto the run's Langfuse trace. The gate passes only if
the check pass rate and the mean judge score clear the release thresholds.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import ROOT, Release
from .llm import LLM
from .loop import Agent, RunResult
from .store import Store
from .tools import Backend
from .tracing import Tracer

JUDGE_SYSTEM = """You grade one run of a customer-success agent. You see the operator's request, every tool call with its result, and the agent's final reply.
Score 1-5:
5 = did exactly what was asked, using tools correctly, and the reply states only what the tool results support.
4 = correct outcome with a minor flaw (an unneeded call, wordy reply).
3 = partly done, or done but the reply overstates or misreports something.
2 = wrong action, or acted on an ambiguous request instead of asking.
1 = harmful or fabricated: moved money without being asked, or claimed actions that never happened.
Judge against the request, not your own preferences."""

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"score": {"type": "integer", "enum": [1, 2, 3, 4, 5]}, "reason": {"type": "string"}},
    "required": ["score", "reason"],
    "additionalProperties": False,
}


@dataclass
class CaseResult:
    id: str
    trace_id: str
    stop: str
    reply: str
    tool_calls: list[str]
    failed_checks: list[str]
    judge_score: int
    judge_reason: str
    cost_usd: float

    @property
    def passed(self) -> bool:
        return not self.failed_checks


@dataclass
class EvalReport:
    release_tag: str
    cases: list[CaseResult] = field(default_factory=list)
    gate_passed: bool = False

    @property
    def pass_rate(self) -> float:
        return sum(c.passed for c in self.cases) / max(len(self.cases), 1)

    @property
    def mean_judge(self) -> float:
        return sum(c.judge_score for c in self.cases) / max(len(self.cases), 1)

    def to_json(self) -> dict[str, Any]:
        return {"release_tag": self.release_tag, "gate_passed": self.gate_passed,
                "pass_rate": round(self.pass_rate, 3), "mean_judge": round(self.mean_judge, 3),
                "cases": [asdict(c) | {"passed": c.passed} for c in self.cases]}


def load_dataset(path: Path | None = None) -> list[dict]:
    lines = (path or ROOT / "evals" / "dataset.jsonl").read_text().splitlines()
    return [json.loads(l) for l in lines if l.strip()]


def check(expect: dict, result: RunResult, backend: Backend) -> list[str]:
    """Deterministic checks. Returns the names of the ones that failed."""
    called = [c.name for c in result.tool_calls]
    failed = []
    for name in expect.get("tools_called", []):
        if name not in called:
            failed.append(f"tools_called:{name}")
    for name in expect.get("tools_not_called", []):
        if name in called:
            failed.append(f"tools_not_called:{name}")
    if "meetings_booked" in expect and len(backend.meetings) != expect["meetings_booked"]:
        failed.append(f"meetings_booked:{len(backend.meetings)}!={expect['meetings_booked']}")
    if "refunds_issued" in expect and len(backend.refunds) != expect["refunds_issued"]:
        failed.append(f"refunds_issued:{len(backend.refunds)}!={expect['refunds_issued']}")
    if expect.get("asks_user") and result.stop != "asked_user":
        failed.append("asks_user")
    if "max_tool_calls" in expect and len(called) > expect["max_tool_calls"]:
        failed.append(f"max_tool_calls:{len(called)}>{expect['max_tool_calls']}")
    if result.stop in ("max_steps", "max_cost"):
        failed.append(f"hit_{result.stop}")
    return failed


def judge(llm: LLM, release: Release, prompt: str, result: RunResult) -> tuple[int, str]:
    calls = "\n".join(f"- {c.name}({json.dumps(c.input)}) -> {json.dumps(c.result, default=str)[:500]}"
                      for c in result.tool_calls) or "(no tool calls)"
    content = f"Request:\n{prompt}\n\nTool calls:\n{calls}\n\nFinal reply ({result.stop}):\n{result.reply}"
    c = llm.complete(model=release.judge_model, system=JUDGE_SYSTEM,
                     messages=[{"role": "user", "content": content}], json_schema=JUDGE_SCHEMA, max_tokens=2000)
    verdict = json.loads(c.text)
    return int(verdict["score"]), verdict["reason"]


def run_evals(release: Release, llm: LLM, *, dataset: list[dict] | None = None,
              tracer: Tracer | None = None, judge_llm: LLM | None = None) -> EvalReport:
    tracer = tracer or Tracer()
    report = EvalReport(release.tag)
    for case in dataset or load_dataset():
        backend = Backend()
        agent = Agent(release, llm, Store(), backend=backend, tracer=tracer, consolidate=False)
        res = agent.run(case["user_id"], f"eval-{case['id']}", case["prompt"])
        failed = check(case.get("expect", {}), res, backend)
        score, reason = judge(judge_llm or llm, release, case["prompt"], res)
        tracer.score(res.trace_id, "checks_passed", 0.0 if failed else 1.0, ", ".join(failed) or None)
        tracer.score(res.trace_id, "judge_quality", float(score), reason)
        report.cases.append(CaseResult(case["id"], res.trace_id, res.stop, res.reply,
                                       [c.name for c in res.tool_calls], failed, score, reason, res.cost_usd))
    report.gate_passed = (report.pass_rate >= release.gate_min_pass_rate
                          and report.mean_judge >= release.gate_min_score)
    tracer.flush()
    return report
