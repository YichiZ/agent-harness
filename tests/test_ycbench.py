"""The YC-Bench runner: command policy, money conversion, and an end-to-end run with the scripted model."""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bench" / "yc-bench" / "run.py"
_spec = importlib.util.spec_from_file_location("ycbench_runner", SCRIPT)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)


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
    assert summary["yc_bench_commit"] and "system.v1.md" in summary["prompt_sha256"]
    assert "\\n" not in (tmp_path / "checkpoints" / "cp-001.json").read_text()  # multi-line text is a list of lines
    log = (tmp_path / "run.md").read_text()
    assert log.count("## Checkpoint") == 3 and "## Summary" in log

    (tmp_path / "run.md").unlink()
    assert runner.main(["--render", str(tmp_path)]) == 0
    assert (tmp_path / "run.md").read_text().count("## Checkpoint") == 3
