import dataclasses
import json
import os

import pytest
from fakes import FakeLLM, Sequence, as_json, text, tool

from harness.config import Release
from harness.evals import check, run_evals
from harness.loop import Agent
from harness.memory import ProceduralMemory
from harness.store import Store
from harness.tools import Backend


@pytest.fixture
def release():
    return dataclasses.replace(Release.load(), consolidate_every_n_chats=2, max_steps=4)


def agent_with(release, *steps, side=None, store=None, backend=None):
    llm = FakeLLM(Sequence(*steps, side=side))
    return Agent(release, llm, store or Store(), backend=backend or Backend()), llm


# ── loop ──────────────────────────────────────────────────────────────────

def test_tool_loop_books_meetings_and_saves_episodes(release):
    agent, llm = agent_with(
        release,
        tool(("list_complaints", {"days": 60})),
        tool(("schedule_meeting", {"customer_id": "cust-ana"}), ("schedule_meeting", {"customer_id": "cust-ben"})),
        text("Found 3 complaints; booked 2 follow-ups."),
    )
    res = agent.run("op-1", "chat-1", "Book follow-ups for unreimbursed complaints")
    assert res.stop == "done"
    assert [c.name for c in res.tool_calls] == ["list_complaints", "schedule_meeting", "schedule_meeting"]
    assert len(agent.backend.meetings) == 2
    # tool results go back in ONE user message, after the assistant turn, unchanged
    last_call = llm.calls[-1]["messages"]
    assert last_call[-2]["role"] == "assistant" and last_call[-2]["content"][0]["type"] == "tool_use"
    assert [b["type"] for b in last_call[-1]["content"]] == ["tool_result", "tool_result"]
    assert [e.role for e in agent.store.episodes("op-1")] == ["user", "assistant"]


def test_max_steps_guardrail_ends_the_loop(release):
    agent, _ = agent_with(release, *[tool(("list_complaints", {"days": 60}))] * 10)
    res = agent.run("op-1", "c", "loop forever")
    assert res.stop == "max_steps" and res.steps == release.max_steps
    assert "stopped after 4 steps" in res.reply


def test_max_cost_guardrail_ends_the_loop(release):
    cheap = dataclasses.replace(release, max_cost_usd=0.01)
    # 1M tokens each way on Opus 5.5 = $24 per step, so the first step blows the budget
    agent, llm = agent_with(cheap, tool(("list_complaints", {"days": 60}), cost_tokens=1_000_000), text("x"))
    res = agent.run("op-1", "c", "list complaints")
    assert res.stop == "max_cost" and len(llm.calls) == 1


def test_large_refund_needs_approval_and_does_not_run(release):
    agent, _ = agent_with(release, tool(("refund_payment", {"order_id": "A-1004", "amount_usd": 640.0})))
    res = agent.run("op-1", "c", "refund A-1004")
    assert res.stop == "needs_approval"
    assert res.pending_approval == {"tool": "refund_payment", "input": {"order_id": "A-1004", "amount_usd": 640.0}}
    assert agent.backend.refunds == []


def test_approved_refund_runs(release):
    agent, _ = agent_with(release, tool(("refund_payment", {"order_id": "A-1004", "amount_usd": 640.0})), text("Refunded."))
    res = agent.run("op-1", "c", "Approved: refund A-1004", approved={"refund_payment"})
    assert res.stop == "done" and agent.backend.refunds == [{"order_id": "A-1004", "amount_usd": 640.0}]


def test_ask_user_ends_turn_with_the_question(release):
    agent, _ = agent_with(release, tool(("ask_user", {"question": "Refund all 2, or just list them?"})))
    res = agent.run("op-1", "c", "deal with complaints")
    assert res.stop == "asked_user" and res.reply == "Refund all 2, or just list them?"


def test_tool_error_goes_back_to_the_model(release):
    agent, llm = agent_with(release, tool(("get_payment", {"order_id": "NOPE"})), text("That order doesn't exist."))
    res = agent.run("op-1", "c", "how much was NOPE?")
    assert res.tool_calls[0].is_error
    assert llm.calls[1]["messages"][-1]["content"][0]["is_error"] is True
    assert res.stop == "done"


# ── memory ────────────────────────────────────────────────────────────────

def test_procedural_memory_loads_only_matching_skills():
    pm = ProceduralMemory()
    assert [s.name for s in pm.select("Please refund order A-1")] == ["refunds"]
    assert {s.name for s in pm.select("follow up on unresolved complaints and refund them")} == {"complaint-followup", "refunds"}
    assert pm.select("what's the weather") == []


def test_working_memory_includes_skills_facts_and_past_chats(release):
    store = Store()
    agent, llm = agent_with(release, text("ok"), text("ok"), store=store)
    agent.consolidator = None
    vec = agent.embedder.embed(["Operator prefers follow-up meetings on Tuesdays"])[0]
    store.add_fact("op-1", "Operator prefers follow-up meetings on Tuesdays", vec, ["old"])
    agent.run("op-1", "chat-a", "Book follow-up meetings for the blender complaint")
    agent.run("op-1", "chat-b", "Schedule follow-up meetings for complaints")
    system = llm.calls[-1]["system"]
    assert "## complaint-followup" in system
    assert "prefers follow-up meetings on Tuesdays" in system
    assert "[chat chat-a] user: Book follow-up meetings for the blender complaint" in system


def test_chat_history_is_replayed_within_a_chat(release):
    agent, llm = agent_with(release, text("Hi Sam."), text("Your name is Sam."))
    agent.consolidator = None
    agent.run("op-1", "c", "I'm Sam")
    agent.run("op-1", "c", "What's my name?")
    assert [m["role"] for m in llm.calls[-1]["messages"]] == ["user", "assistant", "user"]


def test_consolidation_waits_for_n_chats_then_distills_and_replaces_facts(release):
    summaries = iter([
        as_json({"facts": ["Operator wants follow-up meetings booked for 45 minutes."]}),
        as_json({"facts": ["Operator wants follow-up meetings booked for 15 minutes."]}),
    ])
    store = Store()
    agent, llm = agent_with(release, *[text("ok")] * 4, side=lambda c: next(summaries), store=store)

    agent.run("op-1", "c1", "Always make follow-up meetings 45 minutes")
    assert store.facts("op-1") == []  # 1 chat < N=2, summarizer not called
    agent.run("op-1", "c2", "thanks")
    assert [f.fact for f in store.facts("op-1")] == ["Operator wants follow-up meetings booked for 45 minutes."]
    assert llm.calls[-1]["model"] == release.summarizer_model

    agent.run("op-1", "c3", "Actually make follow-up meetings 15 minutes from now on")
    agent.run("op-1", "c4", "ok")
    facts = store.facts("op-1")
    assert [f.fact for f in facts] == ["Operator wants follow-up meetings booked for 15 minutes."]  # replaced, not appended
    assert set(facts[0].source_chat_ids) == {"c1", "c2", "c3", "c4"}


# ── LLM Ops ───────────────────────────────────────────────────────────────

def test_release_tag_changes_with_config(release):
    assert release.tag == dataclasses.replace(release).tag
    assert release.tag != dataclasses.replace(release, semantic_top_k=9).tag


def test_checks_are_deterministic_on_backend_state(release):
    agent, _ = agent_with(release, tool(("refund_payment", {"order_id": "A-1001", "amount_usd": 89.0})), text("done"))
    res = agent.run("op-1", "c", "deal with it")
    failed = check({"tools_not_called": ["refund_payment"], "asks_user": True}, res, agent.backend)
    assert failed == ["tools_not_called:refund_payment", "asks_user"]


def test_eval_gate(release):
    dataset = [
        {"id": "good", "user_id": "u", "prompt": "list complaints", "expect": {"tools_called": ["list_complaints"]}},
        {"id": "bad", "user_id": "u", "prompt": "deal with it", "expect": {"asks_user": True}},
    ]
    agent_steps = Sequence(tool(("list_complaints", {"days": 60})), text("3 complaints."), text("Done!"))
    judge = FakeLLM(lambda c: as_json({"score": 5 if "3 complaints" in c["messages"][0]["content"] else 2, "reason": "r"}))
    report = run_evals(release, FakeLLM(agent_steps), dataset=dataset, judge_llm=judge)
    assert [c.passed for c in report.cases] == [True, False]
    assert report.mean_judge == 3.5 and report.pass_rate == 0.5
    assert report.gate_passed is False  # pass rate 50% < 80%
    assert json.loads(json.dumps(report.to_json()))["cases"][1]["failed_checks"] == ["asks_user"]


def test_memory_is_isolated_per_user(release):
    store = Store()
    agent, llm = agent_with(release, text("ok"), text("ok"), store=store)
    agent.consolidator = None
    vec = agent.embedder.embed(["Operator op-1 prefers Tuesday follow-up meetings"])[0]
    store.add_fact("op-1", "Operator op-1 prefers Tuesday follow-up meetings", vec, [])
    agent.run("op-1", "a", "Book follow-up meetings")
    agent.run("op-2", "b", "Book follow-up meetings")
    assert "Tuesday" not in llm.calls[-1]["system"]
    assert "[chat a]" not in llm.calls[-1]["system"]


def test_langfuse_tracer_records_a_run(release, monkeypatch):
    """Exercises the real Langfuse SDK calls; export goes nowhere (unreachable host)."""
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-test")
    monkeypatch.setenv("LANGFUSE_BASE_URL", "http://127.0.0.1:9")
    from harness.tracing import Tracer

    tracer = Tracer()
    assert tracer.enabled
    llm = FakeLLM(Sequence(tool(("list_complaints", {"days": 60})), text("3 complaints.")))
    agent = Agent(release, llm, Store(), tracer=tracer, consolidate=False)
    res = agent.run("op-1", "c", "list complaints")
    assert res.stop == "done" and len(res.trace_id) == 32 and not res.trace_id.startswith("local-")
    tracer.score(res.trace_id, "judge_quality", 5.0, "fine")


def test_anthropic_client_request_shape_and_parsing():
    """Checks the real SDK types round-trip; no network."""
    from anthropic.types.beta import BetaMessage

    from harness.llm import AnthropicLLM

    sent = {}

    class Messages:
        def create(self, **kwargs):
            sent.update(kwargs)
            return BetaMessage.model_validate({
                "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-opus-5-5",
                "stop_reason": "tool_use", "stop_sequence": None,
                "content": [{"type": "text", "text": "Checking."},
                            {"type": "tool_use", "id": "tu_1", "name": "list_complaints", "input": {"days": 60}}],
                "usage": {"input_tokens": 1000, "output_tokens": 200},
            })

    class Client:
        class beta:
            messages = Messages()

    c = AnthropicLLM(client=Client()).complete(
        model="claude-opus-5-5", system="s", messages=[{"role": "user", "content": "hi"}],
        tools=[{"name": "t", "description": "d", "input_schema": {"type": "object"}}], effort="medium")
    assert sent["fallbacks"] == "default" and sent["betas"] == ["server-side-fallback-2026-07-01"]
    assert sent["output_config"] == {"effort": "medium"}
    assert c.tool_uses == [{"type": "tool_use", "id": "tu_1", "name": "list_complaints", "input": {"days": 60}}]
    assert c.text == "Checking." and c.cost_usd == pytest.approx((1000 * 4 + 200 * 20) / 1e6)


def test_load_env_reads_dotenv_without_overriding(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("HARNESS_FROM_FILE=from-file\nHARNESS_ALREADY_SET=from-file\n")
    monkeypatch.setenv("HARNESS_FROM_FILE", "x")
    monkeypatch.delenv("HARNESS_FROM_FILE")
    monkeypatch.setenv("HARNESS_ALREADY_SET", "from-env")
    from harness.__main__ import load_env

    load_env(env)
    assert os.environ["HARNESS_FROM_FILE"] == "from-file"
    assert os.environ["HARNESS_ALREADY_SET"] == "from-env"
