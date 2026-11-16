"""Evals: generated worlds, code checkers, a runner and a report.

A case names a world, a request and the requirements that apply (`checks`). It
holds no reference answer. Each checker works out what should have happened
from the world before the run and compares that with the backend after it, so
any trajectory that ends in the right state passes, and a new world needs no
hand-written answer.

  world    make_world(seed): a seeded CRM/payments backend; None is the demo data
  checks   CHECKS[name](before, after, result, **args) -> failure reason or None
  runner   run_case / run_evals: the real agent, a fresh world and store per run
  report   summarize / format_report: pass rate by family, cases passing every repeat

Cases live in evals/cases.jsonl, each tagged `dev` (iterate on these) or
`heldout` (run rarely, never tune on its failures).
"""
from __future__ import annotations

import copy
import inspect
import json
import random
import string
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .agent import LLM, Agent, Release, RunResult
from .memory import ROOT, Store
from .tools import APPROVAL_LIMIT_USD, Backend

CASES_PATH = ROOT / "evals" / "cases.jsonl"
SPLITS = ("dev", "heldout")
USER = "op-eval"
BUDGET_STOPS = ("max_steps", "max_cost")


# ── worlds ────────────────────────────────────────────────────────────────

RECENT_DAYS = 14  # every generated world has two open, unrefunded complaints at most this old
_CUSTOMERS = ["ari", "bea", "cai", "dov", "eve", "fox", "gia", "hal", "ida", "jun"]
_SUMMARIES = ["Kettle stopped heating", "Chair leg snapped", "Box arrived empty", "Charged twice",
              "Wrong size delivered", "Lamp shade torn", "Parcel never arrived", "Mattress has a stain"]
_SMALL = [20.0, 42.0, 89.0, 129.0, 250.0, 499.0, APPROVAL_LIMIT_USD]  # refundable without approval
_LARGE = [APPROVAL_LIMIT_USD + 1, 640.0, 899.0, 1200.0]


def make_world(seed: int | None) -> Backend:
    """A backend for one eval run. The same seed always gives the same world."""
    if seed is None:
        return Backend()
    rng = random.Random(seed)
    names = rng.sample(_CUSTOMERS, rng.randint(4, len(_CUSTOMERS)))
    # Two fixed roles, so every world can host a refund case and an approval case.
    rows = [{"days_ago": rng.randint(1, RECENT_DAYS), "refunded": False, "status": "open", "paid": rng.choice(paid)}
            for paid in (_SMALL, _LARGE)]
    rows += [{"days_ago": rng.randint(1, 120), "refunded": rng.random() < 0.3,
              "status": "closed" if rng.random() < 0.3 else "open", "paid": rng.choice(_SMALL + _LARGE)}
             for _ in names[2:]]
    rng.shuffle(rows)
    complaints = [{"id": f"C-{i}", "customer_id": f"cust-{name}", "order_id": f"B-{2000 + i}",
                   "days_ago": row["days_ago"], "summary": rng.choice(_SUMMARIES),
                   "refunded": row["refunded"], "status": row["status"]}
                  for i, (name, row) in enumerate(zip(names, rows), start=1)]
    payments = {c["order_id"]: row["paid"] for c, row in zip(complaints, rows)}
    return Backend(complaints=complaints, payments=payments)


def _unresolved(c: dict) -> bool:
    return not c["refunded"] and c["status"] != "closed"


def _needs_followup(c: dict, days: int) -> bool:
    return c["days_ago"] <= days and _unresolved(c)


HANDLES = ("small_order", "large_order")


def handles(b: Backend) -> dict[str, str]:
    """Order ids a case can name as `{small_order}` / `{large_order}`: the most recent
    open, unrefunded order at or under the approval limit, and the most recent one over it."""
    refundable = sorted((c for c in b.complaints if _unresolved(c)), key=lambda c: c["days_ago"])
    small = next(c for c in refundable if b.payments[c["order_id"]] <= APPROVAL_LIMIT_USD)
    large = next(c for c in refundable if b.payments[c["order_id"]] > APPROVAL_LIMIT_USD)
    return {"small_order": small["order_id"], "large_order": large["order_id"]}


# ── checkers: (world before, backend after, run result, **args) -> why it failed, or None ──

def followups_booked(before: Backend, after: Backend, result: RunResult, *, days: int) -> str | None:
    need = Counter({c["customer_id"] for c in before.complaints if _needs_followup(c, days)})
    got = Counter(m["customer_id"] for m in after.meetings)
    if got == need:
        return None
    return f"missing {sorted((need - got).elements())}, not needed {sorted((got - need).elements())}"


def no_refunds(before: Backend, after: Backend, result: RunResult) -> str | None:
    return f"refunded {after.refunds}" if after.refunds else None


def no_meetings(before: Backend, after: Backend, result: RunResult) -> str | None:
    return f"booked {[m['customer_id'] for m in after.meetings]}" if after.meetings else None


def refund_exact(before: Backend, after: Backend, result: RunResult, *, order: str,
                 amount: float | None = None) -> str | None:
    want = [{"order_id": order, "amount_usd": before.payments[order] if amount is None else amount}]
    return None if after.refunds == want else f"refunds were {after.refunds}, wanted {want}"


def crm_note(before: Backend, after: Backend, result: RunResult, *, order: str) -> str | None:
    complaint_ids = {c["id"] for c in before.complaints if c["order_id"] == order}
    noted = [n["complaint_id"] for n in after.notes]
    return None if complaint_ids & set(noted) else f"no note on {sorted(complaint_ids)}; notes were on {noted}"


def needs_approval(before: Backend, after: Backend, result: RunResult, *, order: str) -> str | None:
    pending = result.pending_approval or {}
    if result.stop != "needs_approval":
        return f"stop was {result.stop}"
    if pending.get("tool") != "refund_payment" or pending.get("input", {}).get("order_id") != order:
        return f"approval was requested for {pending}"
    return f"refunded {after.refunds} before approval" if after.refunds else None


def asked_user(before: Backend, after: Backend, result: RunResult) -> str | None:
    return None if result.stop == "asked_user" else f"stop was {result.stop}"


def no_tool_calls(before: Backend, after: Backend, result: RunResult) -> str | None:
    called = [c.name for c in result.tool_calls]
    return f"called {called}" if called else None


def meeting_minutes(before: Backend, after: Backend, result: RunResult, *, minutes: int) -> str | None:
    wrong = {m["customer_id"]: m.get("minutes") for m in after.meetings if m.get("minutes") != minutes}
    return f"wanted {minutes} minutes, got {wrong}" if wrong else None


Check = Callable[..., "str | None"]
CHECKS: dict[str, Check] = {f.__name__: f for f in (
    followups_booked, no_refunds, no_meetings, refund_exact, crm_note, needs_approval,
    asked_user, no_tool_calls, meeting_minutes)}


# ── cases ─────────────────────────────────────────────────────────────────

_REQUIRED = ("id", "family", "split", "world_seed", "prompt", "checks")


def _validate(case: dict, line: int) -> None:
    where = f"case {case.get('id', '?')!r} (line {line})"
    if missing := [k for k in _REQUIRED if k not in case]:
        raise ValueError(f"{where}: missing {missing}")
    if case["split"] not in SPLITS:
        raise ValueError(f"{where}: split must be one of {SPLITS}, got {case['split']!r}")
    fields = {name for _, name, _, _ in string.Formatter().parse(case["prompt"]) if name is not None}
    if unknown := fields - set(HANDLES):
        raise ValueError(f"{where}: prompt uses unknown placeholder {sorted(unknown)}; known: {HANDLES}")
    for name, args in case["checks"].items():
        if name not in CHECKS:
            raise ValueError(f"{where}: unknown check {name!r}; known: {sorted(CHECKS)}")
        try:
            inspect.signature(CHECKS[name]).bind(None, None, None, **args)
        except TypeError as e:
            raise ValueError(f"{where}: check {name}: {e}") from e
        if "order" in args and args["order"] not in HANDLES:
            raise ValueError(f"{where}: check {name}: order must be one of {HANDLES}, got {args['order']!r}")


def load_cases(path: Path | None = None, *, split: str | None = None) -> list[dict]:
    """Read and validate the case file. `split` keeps only that side."""
    lines = (path or CASES_PATH).read_text().splitlines()
    cases = [(json.loads(text), n) for n, text in enumerate(lines, start=1) if text.strip()]
    for case, n in cases:
        _validate(case, n)
    if dup := [i for i, count in Counter(c["id"] for c, _ in cases).items() if count > 1]:
        raise ValueError(f"duplicate case ids: {dup}")
    return [c for c, _ in cases if split is None or c["split"] == split]


# ── runner ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Outcome:
    case_id: str
    family: str
    split: str
    failures: tuple[str, ...]
    stop: str
    tool_calls: tuple[str, ...]
    reply: str
    cost_usd: float

    @property
    def passed(self) -> bool:
        return not self.failures


def _run_setup(case: dict, release: Release, llm: LLM, store: Store) -> float:
    """Memory cases: earlier chats the agent should remember. They run on a scratch
    world, so only what reaches memory carries over, then consolidation is forced."""
    chats = case.get("setup_chats", [])
    if not chats:
        return 0.0
    agent = Agent(release, llm, store, backend=make_world(case["world_seed"]))
    cost = sum(agent.run(USER, f"setup-{i}", chat).cost_usd for i, chat in enumerate(chats))
    agent.consolidator.maybe_run(USER, force=True)  # the summarizer's own cost is not counted
    return cost


def run_case(case: dict, release: Release, llm: LLM) -> Outcome:
    backend = make_world(case["world_seed"])
    before = copy.deepcopy(backend)
    names = handles(before)
    store = Store()
    setup_cost = _run_setup(case, release, llm, store)
    result = Agent(release, llm, store, backend=backend, consolidate=False).run(
        USER, "eval", case["prompt"].format(**names))

    failures = [f"finished: stopped on {result.stop}"] if result.stop in BUDGET_STOPS else []
    for name, args in case["checks"].items():
        resolved = {k: names.get(v, v) if isinstance(v, str) else v for k, v in args.items()}
        if reason := CHECKS[name](before, backend, result, **resolved):
            failures.append(f"{name}: {reason}")
    return Outcome(case["id"], case["family"], case["split"], tuple(failures), result.stop,
                   tuple(c.name for c in result.tool_calls), result.reply, setup_cost + result.cost_usd)


def run_evals(cases: list[dict], release: Release, llm: LLM, *, repeats: int = 1,
              max_cost_usd: float = float("inf")) -> tuple[list[Outcome], bool]:
    """Run every case `repeats` times. Returns the outcomes and whether the cost cap cut the run short."""
    outcomes: list[Outcome] = []
    for case in cases:
        for _ in range(repeats):
            if sum(o.cost_usd for o in outcomes) >= max_cost_usd:
                return outcomes, True
            try:
                outcomes.append(run_case(case, release, llm))
            except Exception as e:  # one API error or bad summarizer reply must not lose the other runs
                outcomes.append(Outcome(case["id"], case["family"], case["split"],
                                        (f"error: {type(e).__name__}: {e}",), "error", (), "", 0.0))
    return outcomes, False


# ── report ────────────────────────────────────────────────────────────────

def _tally(outcomes: list[Outcome]) -> dict[str, int]:
    by_case: dict[str, list[bool]] = {}
    for o in outcomes:
        by_case.setdefault(o.case_id, []).append(o.passed)
    return {"runs": len(outcomes), "passed": sum(o.passed for o in outcomes),
            "cases": len(by_case), "cases_all_passed": sum(all(runs) for runs in by_case.values())}


def summarize(outcomes: list[Outcome]) -> dict[str, Any]:
    total = _tally(outcomes)
    families = sorted({o.family for o in outcomes})
    return {**total,
            "pass_rate": round(total["passed"] / max(total["runs"], 1), 3),
            "cost_usd": round(sum(o.cost_usd for o in outcomes), 4),
            "families": {f: _tally([o for o in outcomes if o.family == f]) for f in families}}


def format_report(outcomes: list[Outcome], header: str) -> str:
    s = summarize(outcomes)
    rows = [header, f"{'family':<12}{'runs passed':>12}{'cases passing every run':>26}"]
    rows += [f"{name:<12}{f'{t['passed']}/{t['runs']}':>12}{f'{t['cases_all_passed']}/{t['cases']}':>26}"
             for name, t in s["families"].items()]
    rows.append(f"{'total':<12}{f'{s['passed']}/{s['runs']}':>12}{f'{s['cases_all_passed']}/{s['cases']}':>26}"
                f"   pass rate {s['pass_rate']:.0%}   ${s['cost_usd']:.2f}")
    rows += [f"FAIL {o.case_id} [{o.stop}] {'; '.join(o.failures)}" for o in outcomes if not o.passed]
    return "\n".join(rows)


def report_json(outcomes: list[Outcome], release: Release, *, split: str | None, repeats: int,
                stopped_at_cost_cap: bool) -> dict[str, Any]:
    return {"split": split or "all", "repeats": repeats, "stopped_at_cost_cap": stopped_at_cost_cap,
            "release": asdict(release), "summary": summarize(outcomes),
            "runs": [asdict(o) | {"passed": o.passed} for o in outcomes]}
