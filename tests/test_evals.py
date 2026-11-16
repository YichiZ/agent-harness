"""Tests of the evaluator itself: answers whose verdict is known in advance."""
import dataclasses
import json

import pytest
from fakes import FakeLLM, Sequence, as_json, text, tool

from harness.agent import Release, RunResult, ToolCall
from harness.evals import CHECKS, Outcome, handles, load_cases, make_world, run_case, run_evals, summarize
from harness.tools import APPROVAL_LIMIT_USD, Backend


@pytest.fixture
def release():
    return dataclasses.replace(Release.load(), max_steps=6)


# ── checkers, on a hand-built world ───────────────────────────────────────

def complaint(i, customer, *, days=10, refunded=False, status="open"):
    return {"id": f"C-{i}", "customer_id": f"cust-{customer}", "order_id": f"A-{i}", "days_ago": days,
            "summary": "x", "refunded": refunded, "status": status}


def world(**changes) -> Backend:
    """ana and ben need a follow-up inside 60 days; cho, dee and eli do not."""
    base = Backend(
        complaints=[complaint(1, "ana", days=5), complaint(2, "ben", days=20),
                    complaint(3, "cho", days=20, refunded=True), complaint(4, "dee", days=20, status="closed"),
                    complaint(5, "eli", days=70)],
        payments={"A-1": 80.0, "A-2": 120.0, "A-3": 40.0, "A-4": 60.0, "A-5": 900.0})
    return dataclasses.replace(base, **changes)


def meetings(*customers, minutes=30):
    return [{"customer_id": f"cust-{c}", "minutes": minutes} for c in customers]


def ran(stop="done", calls=(), pending=None) -> RunResult:
    return RunResult("", stop, 1, 0.0, [ToolCall(n, {}, None) for n in calls], pending_approval=pending)


def verdict(name, after, result=None, **args):
    return CHECKS[name](world(), after, result or ran(), **args)


def test_followups_pass_when_exactly_the_needed_customers_have_a_meeting():
    assert verdict("followups_booked", world(meetings=meetings("ana", "ben")), days=60) is None


def test_followups_pass_in_any_booking_order():
    assert verdict("followups_booked", world(meetings=meetings("ben", "ana")), days=60) is None


def test_followups_fail_when_one_is_missing():
    assert "cust-ben" in verdict("followups_booked", world(meetings=meetings("ana")), days=60)


@pytest.mark.parametrize("extra", ["cho", "dee", "eli", "ana"])  # refunded, closed, too old, duplicate
def test_followups_fail_on_a_meeting_nobody_needed(extra):
    assert f"cust-{extra}" in verdict("followups_booked", world(meetings=meetings("ana", "ben", extra)), days=60)


def test_followups_window_changes_who_is_needed():
    assert verdict("followups_booked", world(meetings=meetings("ana")), days=10) is None
    assert verdict("followups_booked", world(meetings=meetings("ana", "ben", "eli")), days=90) is None


def test_followups_pass_with_no_meetings_when_nobody_needs_one():
    assert verdict("followups_booked", world(), days=2) is None


def test_no_refunds_and_no_meetings():
    assert verdict("no_refunds", world()) is None
    assert verdict("no_refunds", world(refunds=[{"order_id": "A-1", "amount_usd": 80.0}])) is not None
    assert verdict("no_meetings", world()) is None
    assert verdict("no_meetings", world(meetings=meetings("ana"))) is not None


def test_refund_exact_defaults_to_the_full_amount_paid():
    full = world(refunds=[{"order_id": "A-1", "amount_usd": 80.0}])
    assert verdict("refund_exact", full, order="A-1") is None
    assert verdict("refund_exact", full, order="A-1", amount=15) is not None
    assert verdict("refund_exact", world(refunds=[{"order_id": "A-1", "amount_usd": 15.0}]), order="A-1", amount=15) is None


@pytest.mark.parametrize("refunds", [
    [],                                                                               # nothing refunded
    [{"order_id": "A-2", "amount_usd": 120.0}],                                       # wrong order
    [{"order_id": "A-1", "amount_usd": 80.0}, {"order_id": "A-1", "amount_usd": 80.0}],  # refunded twice
    [{"order_id": "A-1", "amount_usd": 80.0}, {"order_id": "A-2", "amount_usd": 120.0}],  # and one nobody asked for
])
def test_refund_exact_fails_on_anything_but_the_one_refund(refunds):
    assert verdict("refund_exact", world(refunds=refunds), order="A-1") is not None


def test_crm_note_must_be_on_the_orders_complaint():
    assert verdict("crm_note", world(notes=[{"complaint_id": "C-1", "note": "refunded"}]), order="A-1") is None
    assert verdict("crm_note", world(notes=[{"complaint_id": "C-2", "note": "refunded"}]), order="A-1") is not None


def test_needs_approval_requires_the_pause_on_that_order_and_no_money_moved():
    pending = {"tool": "refund_payment", "input": {"order_id": "A-5", "amount_usd": 900.0}}
    assert verdict("needs_approval", world(), ran("needs_approval", pending=pending), order="A-5") is None
    assert verdict("needs_approval", world(), ran("asked_user"), order="A-5") is not None
    assert verdict("needs_approval", world(), ran("needs_approval", pending=pending), order="A-1") is not None
    moved = world(refunds=[{"order_id": "A-1", "amount_usd": 80.0}])
    assert verdict("needs_approval", moved, ran("needs_approval", pending=pending), order="A-5") is not None


def test_asked_user_and_no_tool_calls_read_the_run():
    assert verdict("asked_user", world(), ran("asked_user")) is None
    assert verdict("asked_user", world(), ran("done")) is not None
    assert verdict("no_tool_calls", world(), ran()) is None
    assert verdict("no_tool_calls", world(), ran(calls=["list_complaints"])) is not None


def test_meeting_minutes_applies_to_every_meeting():
    assert verdict("meeting_minutes", world(meetings=meetings("ana", "ben", minutes=45)), minutes=45) is None
    mixed = meetings("ana", minutes=45) + meetings("ben", minutes=30)
    assert "cust-ben" in verdict("meeting_minutes", world(meetings=mixed), minutes=45)


# ── generated worlds ──────────────────────────────────────────────────────

def test_make_world_is_deterministic_and_varies_by_seed():
    assert make_world(7) == make_world(7)
    assert make_world(7) != make_world(8)


def test_stock_world_is_the_demo_seed_data():
    assert make_world(None) == Backend()
    assert handles(make_world(None)) == {"small_order": "A-1001", "large_order": "A-1004"}


@pytest.mark.parametrize("seed", range(40))
def test_every_world_has_an_open_refundable_order_on_each_side_of_the_approval_limit(seed):
    b = make_world(seed)
    by_order = {c["order_id"]: c for c in b.complaints}
    h = handles(b)
    assert b.payments[h["small_order"]] <= APPROVAL_LIMIT_USD < b.payments[h["large_order"]]
    for order in h.values():
        c = by_order[order]
        assert not c["refunded"] and c["status"] == "open" and c["days_ago"] <= 14
    assert len({c["customer_id"] for c in b.complaints}) == len(b.complaints)
    assert set(by_order) == set(b.payments)


# ── runner, on the stock world (ana and ben need follow-up; A-1001 is $89, A-1004 is $640) ──

def case(**changes):
    return {"id": "t", "family": "followup", "split": "dev", "world_seed": None,
            "prompt": "Book follow-ups for open unrefunded complaints from the last 60 days.",
            "checks": {"followups_booked": {"days": 60}, "no_refunds": {}}} | changes


def test_run_case_passes_a_correct_trajectory(release):
    llm = FakeLLM(Sequence(tool(("list_complaints", {"days": 60})),
                           tool(("schedule_meeting", {"customer_id": "cust-ben"})),
                           tool(("schedule_meeting", {"customer_id": "cust-ana"})), text("Booked 2.")))
    out = run_case(case(), release, llm)
    assert out.passed and out.failures == ()
    assert out.tool_calls == ("list_complaints", "schedule_meeting", "schedule_meeting")
    assert out.cost_usd > 0


def test_run_case_reports_why_a_trajectory_failed(release):
    llm = FakeLLM(Sequence(tool(("schedule_meeting", {"customer_id": "cust-ana"})),
                           tool(("refund_payment", {"order_id": "A-1001", "amount_usd": 89.0})), text("Done.")))
    out = run_case(case(), release, llm)
    assert not out.passed
    assert [f.split(":")[0] for f in out.failures] == ["followups_booked", "no_refunds"]
    assert "cust-ben" in out.failures[0]


def test_run_case_fills_order_handles_into_the_prompt_and_the_checks(release):
    llm = FakeLLM(Sequence(tool(("get_payment", {"order_id": "A-1001"})),
                           tool(("refund_payment", {"order_id": "A-1001", "amount_usd": 89.0})),
                           tool(("add_crm_note", {"complaint_id": "C-1", "note": "Refund issued."})), text("Refunded.")))
    out = run_case(case(prompt="Refund order {small_order} in full.",
                        checks={"refund_exact": {"order": "small_order"}, "crm_note": {"order": "small_order"}}),
                   release, llm)
    assert out.passed
    assert llm.calls[0]["messages"][-1]["content"] == "Refund order A-1001 in full."


def test_run_case_sees_the_approval_pause(release):
    llm = FakeLLM(Sequence(tool(("refund_payment", {"order_id": "A-1004", "amount_usd": 640.0}))))
    out = run_case(case(prompt="Refund {large_order}.", checks={"needs_approval": {"order": "large_order"}}), release, llm)
    assert out.passed and out.stop == "needs_approval"


def test_run_case_fails_a_run_that_hit_a_budget(release):
    llm = FakeLLM(Sequence(*[tool(("list_complaints", {"days": 60}))] * 6))
    out = run_case(case(checks={}), release, llm)
    assert out.failures == ("finished: stopped on max_steps",)


def test_memory_case_carries_setup_chats_into_the_run_but_not_their_side_effects(release):
    llm = FakeLLM(Sequence(
        tool(("schedule_meeting", {"customer_id": "cust-dee"})), text("Noted."),  # setup chat books a stray meeting
        tool(("schedule_meeting", {"customer_id": "cust-ana", "minutes": 45}),
             ("schedule_meeting", {"customer_id": "cust-ben", "minutes": 45})), text("Booked 2."),
        side=lambda call: as_json({"facts": ["Operator wants follow-up meetings to be 45 minutes."]})))
    out = run_case(case(setup_chats=["Always make follow-ups 45 minutes."],
                        checks={"followups_booked": {"days": 60}, "meeting_minutes": {"minutes": 45}}), release, llm)
    assert out.passed
    assert "[chat setup-0] user: Always make follow-ups 45 minutes." in llm.calls[-1]["system"]
    assert sum(c.get("json_schema") is not None for c in llm.calls) == 1  # consolidated once, after setup


def test_run_evals_repeats_each_case(release):
    llm = FakeLLM(lambda call: text("I did nothing."))
    outcomes, stopped = run_evals([case(id="a"), case(id="b")], release, llm, repeats=3)
    assert [o.case_id for o in outcomes] == ["a"] * 3 + ["b"] * 3 and not stopped


def test_run_evals_stops_at_the_cost_cap(release):
    llm = FakeLLM(lambda call: text("x", cost_tokens=1_000_000))  # $24 a call on Opus 5.5
    outcomes, stopped = run_evals([case(id="a"), case(id="b")], release, llm, repeats=3, max_cost_usd=30.0)
    assert len(outcomes) == 2 and stopped


def test_run_evals_records_a_crashed_run_as_a_failure_and_keeps_going(release):
    def flaky(call):
        if len(llm.calls) == 1:
            raise TimeoutError("api timed out")
        return text("I did nothing.")

    llm = FakeLLM(flaky)
    outcomes, stopped = run_evals([case(id="a", checks={}), case(id="b", checks={})], release, llm)
    assert [(o.case_id, o.stop, o.failures) for o in outcomes] == [
        ("a", "error", ("error: TimeoutError: api timed out",)), ("b", "done", ())]
    assert not stopped


def test_summarize_counts_runs_and_cases_that_passed_every_repeat():
    def o(case_id, family, failures=()):
        return Outcome(case_id, family, "dev", tuple(failures), "done", (), "", 0.5)

    s = summarize([o("a", "followup"), o("a", "followup"), o("b", "followup"), o("b", "followup", ["no_refunds: x"]),
                   o("c", "refund", ["refund_exact: y"])])
    assert (s["runs"], s["passed"], s["cases"], s["cases_all_passed"]) == (5, 3, 3, 1)
    assert s["pass_rate"] == 0.6 and s["cost_usd"] == 2.5
    assert s["families"]["followup"] == {"runs": 4, "passed": 3, "cases": 2, "cases_all_passed": 1}
    assert s["families"]["refund"] == {"runs": 1, "passed": 0, "cases": 1, "cases_all_passed": 0}


# ── case file ─────────────────────────────────────────────────────────────

def write_cases(tmp_path, *cases):
    path = tmp_path / "cases.jsonl"
    path.write_text("\n".join(json.dumps(c) for c in cases))
    return path


def test_load_cases_filters_by_split(tmp_path):
    path = write_cases(tmp_path, case(id="a"), case(id="b", split="heldout"))
    assert [c["id"] for c in load_cases(path)] == ["a", "b"]
    assert [c["id"] for c in load_cases(path, split="heldout")] == ["b"]


@pytest.mark.parametrize("bad, message", [
    ({"checks": {"followups_bookd": {}}}, "unknown check"),
    ({"split": "test"}, "split"),
    ({"prompt": "Refund {tiny_order}."}, "tiny_order"),
    ({"checks": {"followups_booked": {}}}, "followups_booked"),  # missing its `days` argument
    ({"checks": {"refund_exact": {"order": "smal_order"}}}, "smal_order"),  # not a known order handle
])
def test_load_cases_rejects_a_malformed_case(tmp_path, bad, message):
    with pytest.raises(ValueError, match=message):
        load_cases(write_cases(tmp_path, case(**bad)))


def test_load_cases_rejects_duplicate_ids(tmp_path):
    with pytest.raises(ValueError, match="duplicate"):
        load_cases(write_cases(tmp_path, case(), case()))


def test_shipped_cases_keep_dev_and_heldout_apart():
    cases = load_cases()
    dev, held = ([c for c in cases if c["split"] == s] for s in ("dev", "heldout"))
    assert dev and held
    assert not {c["world_seed"] for c in dev} & {c["world_seed"] for c in held}
    assert not {c["prompt"] for c in dev} & {c["prompt"] for c in held}
    assert {c["family"] for c in dev} == {c["family"] for c in held}


# ── CLI ───────────────────────────────────────────────────────────────────

def test_eval_command_prints_a_report_writes_json_and_gates_on_min_pass(tmp_path, capsys):
    from harness.__main__ import main

    argv = ["eval", "--family", "no-tools", "--out", str(tmp_path)]
    assert main(argv, llm=FakeLLM(lambda call: text("It aims to rebuild trust."))) == 0
    printed = capsys.readouterr().out
    assert "no-tools" in printed and "2/2" in printed
    [report] = [json.loads(p.read_text()) for p in tmp_path.glob("*.json")]
    assert report["split"] == "dev" and report["summary"]["passed"] == 2
    assert [r["case_id"] for r in report["runs"]] == ["no-tools-meeting-purpose", "no-tools-approval-limit"]

    calls_a_tool = FakeLLM(Sequence(*[tool(("list_complaints", {"days": 60})), text("x")] * 2))
    assert main(argv + ["--min-pass", "1.0"], llm=calls_a_tool) == 1
    assert "FAIL no-tools-meeting-purpose" in capsys.readouterr().out


def test_eval_command_rejects_a_family_with_no_cases(tmp_path):
    from harness.__main__ import main

    with pytest.raises(SystemExit):
        main(["eval", "--family", "nope", "--out", str(tmp_path)], llm=FakeLLM(lambda call: text("x")))


def test_eval_command_fails_the_gate_when_the_cost_cap_cut_the_run_short(tmp_path, capsys):
    from harness.__main__ import main

    costly = FakeLLM(lambda call: text("It aims to rebuild trust.", cost_tokens=1_000_000))
    assert main(["eval", "--family", "no-tools", "--out", str(tmp_path), "--max-cost", "1"], llm=costly) == 1
    assert "Stopped early" in capsys.readouterr().out
