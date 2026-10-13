"""τ²-bench adapter, run offline: scripted model + scripted user, real τ² env and grader."""
import dataclasses

import pytest

pytest.importorskip("tau2")

from tau2.utils.utils import DATA_DIR  # noqa: E402

if not DATA_DIR.exists():
    pytest.skip(f"τ² data not found at {DATA_DIR}; set TAU2_DATA_DIR", allow_module_level=True)

from fakes import FakeLLM, Sequence, text, tool  # noqa: E402
from tau2.user.user_simulator import UserSimulator  # noqa: E402
from tau2.data_model.message import UserMessage  # noqa: E402
from tau2.evaluator.evaluator import EvaluationType  # noqa: E402

from harness.bench.tau2 import HarnessTau2Agent, run_tau2, to_anthropic_tool  # noqa: E402
from harness.config import Release  # noqa: E402


class ScriptedUser(UserSimulator):
    def __init__(self, lines):
        super().__init__(llm="scripted")
        self.lines = list(lines)

    def _generate_next_message(self, message, state):
        return UserMessage(role="user", content=self.lines.pop(0))


# Task 0: Emma Kim asks to cancel EHGLP3, which the policy doesn't allow; the agent must refuse.
OPENING = "Hi, I'm Emma Kim, user id emma_kim_9957. Please cancel reservation EHGLP3."


@pytest.fixture
def release():
    return dataclasses.replace(Release.load(), max_steps=3)


def run(release, *agent_steps, lines=("###STOP###",)):
    llm = FakeLLM(Sequence(*agent_steps))
    report = run_tau2(release, llm, task_ids=["0"],
                      user_factory=lambda env, task: ScriptedUser([OPENING, *lines]),
                      evaluation_type=EvaluationType.ENV)
    return report, llm


def test_refusing_a_disallowed_cancellation_scores_1(release):
    report, llm = run(
        release,
        tool(("get_reservation_details", {"reservation_id": "EHGLP3"})),
        text("This booking isn't eligible for cancellation with a refund under our policy, so I can't cancel it."),
    )
    [a] = report.attempts
    assert a.reward == 1.0 and a.db_match is True
    assert report.pass_hat_k(1) == 1.0 and report.gate_passed
    # the τ² tool result came back to the model as an Anthropic tool_result
    tool_result = llm.calls[1]["messages"][-1]["content"][0]
    assert tool_result["type"] == "tool_result" and "EHGLP3" in tool_result["content"]
    assert "# Domain policy" in llm.calls[0]["system"]


def test_cancelling_anyway_fails_the_db_check(release):
    report, _ = run(
        release,
        tool(("cancel_reservation", {"reservation_id": "EHGLP3"})),
        text("Done, it's cancelled."),
    )
    [a] = report.attempts
    assert a.reward == 0.0 and a.db_match is False
    assert not report.gate_passed


def test_step_budget_hands_off_instead_of_looping(release):
    looping = [tool(("get_user_details", {"user_id": "emma_kim_9957"}))] * 3
    report, llm = run(release, *looping)
    assert len(llm.calls) == release.max_steps  # the 4th step never reached the model
    assert report.attempts[0].reward == 1.0     # nothing was written, so the DB still matches


def test_tool_schemas_convert_to_anthropic_format():
    from tau2.runner import build_environment

    specs = [to_anthropic_tool(t) for t in build_environment("airline").get_tools()]
    cancel = next(s for s in specs if s["name"] == "cancel_reservation")
    assert cancel["input_schema"]["required"] == ["reservation_id"]
    assert set(cancel) == {"name", "description", "input_schema"}
