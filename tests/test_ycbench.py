"""The YC-Bench runner: command policy, money conversion, and an end-to-end run with the scripted model."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bench" / "yc-bench" / "run.py"
_spec = importlib.util.spec_from_file_location("ycbench_runner", SCRIPT)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)


def release_version() -> str:
    return json.loads((SCRIPT.parent / "release.json").read_text())["prompt_version"]


@pytest.mark.parametrize("command", [
    "yc-bench sim resume",
    "yc-bench sim  resume",
    "yc-bench 'sim' resume",
    'yc-bench "sim" "resume"',
    "yc-bench run --model x",
    "yc-bench scratchpad write --content hi",
    "yc-bench start",
    "yc-bench",
    "ls -la",
    "yc-bench task list 'unclosed",
])
def test_runner_owned_and_malformed_commands_are_refused(command):
    assert runner.check_command(command)


@pytest.mark.parametrize("command", [
    "yc-bench market browse --limit 5",
    "yc-bench task cancel --task-id Task-1 --reason 'sim resume later'",  # the words only matter as the group
    "yc-bench client history",
])
def test_agent_commands_are_allowed(command):
    assert runner.check_command(command) is None


def test_event_money_is_shown_in_dollars():
    payroll = {"type": "monthly_payroll", "funds_after": 19615111, "amount_cents": 3836503}
    done = {"type": "task_completed", "funds_delta": -608312, "listed_reward": 1738037,
            "salary_bump_total_cents": 11741, "employees_assigned": 2}
    assert runner.dollars(payroll) == {"type": "monthly_payroll", "funds_after_usd": 196151.11, "amount_usd": 38365.03}
    line = runner.event_line(done)
    assert '"funds_delta_usd": -6083.12' in line and '"listed_reward_usd": 17380.37' in line
    assert '"salary_bump_total_usd": 117.41' in line and '"employees_assigned": 2' in line


@pytest.mark.parametrize("reason, code", [
    ("max_checkpoints", 0), ("max_cost", 0), ("horizon_end", 0), ("bankruptcy", 0),
    ("stalled", 1), ("interrupted", 1), ("error: RuntimeError: boom", 1),
])
def test_exit_code_fails_runs_that_did_not_end_on_their_own_terms(reason, code):
    assert runner.exit_code(reason) == code


def test_non_empty_out_folder_is_refused(tmp_path):
    (tmp_path / "old.txt").write_text("earlier run")
    with pytest.raises(SystemExit):
        runner.main(["--fake", "--max-checkpoints", "1", "--out", str(tmp_path)])


def test_fake_run_advances_the_simulation(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")  # restored after main() overwrites them
    monkeypatch.setenv("YC_BENCH_EXPERIMENT", "")

    assert runner.main(["--fake", "--max-checkpoints", "3", "--out", str(tmp_path)]) == 0

    rows = [json.loads(p.read_text()) for p in sorted((tmp_path / "checkpoints").glob("cp-*.json"))]
    assert [r["checkpoint"] for r in rows] == [1, 2, 3]
    assert rows[-1]["sim_time_after"] > rows[0]["sim_time_before"]
    assert all(r["resume"]["exit_code"] == 0 and r["system"] for r in rows)
    assert "Your note from the last checkpoint" in "\n".join(rows[1]["prompt"])
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["checkpoints"] == 3 and summary["total_cost_usd"] == 0
    assert summary["yc_bench_commit"] and {f"{k}.{release_version()}.md" for k in ("system", "summarizer", "checkpoint")} <= set(summary["prompt_sha256"])
    assert isinstance(summary["git_dirty"], bool)
    assert summary["runner_sha256"] == hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    assert "\\n" not in (tmp_path / "checkpoints" / "cp-001.json").read_text()  # multi-line text is a list of lines
    log = (tmp_path / "run.md").read_text()
    assert log.count("## Checkpoint") == 3 and "## Summary" in log

    (tmp_path / "run.md").unlink()
    assert runner.main(["--render", str(tmp_path)]) == 0
    assert (tmp_path / "run.md").read_text().count("## Checkpoint") == 3


LEAK_PATTERNS = [  # hidden mechanics stock YC-Bench agents aren't told, in any wording
    r"inflat", r"scope creep", r"adversar", r"after (you )?accept", r"\brat client",
    r"\b35 ?(%|percent)", r"thirty-five", r"/ ?150\b", r"\b150 units",
    r"strongest", r"\b(top|best) ?(4|four)\b", r"(4|four) (best|strongest)",
    r"per (business )?hour", r"units per hour", r"business hours? a day",
    r"\b0?9:00\b", r"\b9 ?am\b", r"\b6 ?pm\b", r"\b18:00\b", r"max\(7",
    r"only on success", r"no cash penalty",
]


def leaks_in(text: str) -> list[str]:
    from yc_bench.services.generate_clients import _CLIENT_NAME_POOL

    text = " ".join(text.lower().split())
    return ([n for n in _CLIENT_NAME_POOL if n.lower() in text]
            + [p for p in LEAK_PATTERNS if re.search(p, text)])


def test_leak_check_catches_rewordings():
    for leak in ("a 35 % penalty", "only the top 4 count", "rates are units per hour",
                 "work 9am to 6pm", "max(7, units/150)", "Vanguard ML failed"):
        assert leaks_in(leak), leak
    assert not leaks_in("Acme Widgets: Task-3 failed, late by 40 hours.")


def test_current_prompts_do_not_leak_simulator_secrets():
    """Fairness: stock YC-Bench agents get neither real client names nor hidden mechanics."""
    release = json.loads((SCRIPT.parent / "release.json").read_text())
    prompts_dir = SCRIPT.parent.parent.parent / release["prompts_dir"]
    files = [prompts_dir / f"{kind}.{release['prompt_version']}.md" for kind in ("system", "summarizer", "checkpoint")]
    for f in files + [SCRIPT]:
        assert f.exists(), f
        assert not leaks_in(f.read_text()), f"{f.name} leaks {leaks_in(f.read_text())}"
