"""End-to-end: the YC-Bench runner on a real simulated world, with the scripted model."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bench" / "yc-bench" / "run.py"


def test_fake_run_advances_the_simulation(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")  # restored after main() overwrites them
    monkeypatch.setenv("YC_BENCH_EXPERIMENT", "")
    spec = importlib.util.spec_from_file_location("ycbench_runner", SCRIPT)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    assert runner.main(["--fake", "--max-checkpoints", "3", "--out", str(tmp_path)]) == 0

    rows = [json.loads(p.read_text()) for p in sorted((tmp_path / "checkpoints").glob("cp-*.json"))]
    assert [r["checkpoint"] for r in rows] == [1, 2, 3]
    assert rows[-1]["sim_time_after"] > rows[0]["sim_time_before"]
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["checkpoints"] == 3
    assert "\\n" not in (tmp_path / "checkpoints" / "cp-001.json").read_text()  # multi-line text is a list of lines
    assert summary["total_cost_usd"] == 0
    log = (tmp_path / "run.md").read_text()
    assert log.count("## Checkpoint") == 3 and "## Summary" in log

    (tmp_path / "run.md").unlink()
    assert runner.main(["--render", str(tmp_path)]) == 0
    assert (tmp_path / "run.md").read_text().count("## Checkpoint") == 3
