import csv
import json

from benchmarks import analyze, runner

CFG = {
    "name": "t",
    "scenarios": [{"id": "r", "kind": "random", "size": 30, "params": {"density": 0.1}, "seeds": 4}],
    "planners": ["astar", "astar_smooth", "rrt_connect"],
}


def run(tmp_path, name):
    cfg_path = tmp_path / "c.json"
    cfg_path.write_text(json.dumps(CFG))
    out = tmp_path / name
    runner.main([str(cfg_path), "--out", str(out)])
    return out


def read(out):
    with open(out / "raw.csv", newline="") as f:
        return list(csv.DictReader(f))


def test_runner_is_reproducible(tmp_path):
    a, b = read(run(tmp_path, "a")), read(run(tmp_path, "b"))
    assert len(a) == 12
    key = lambda r: (r["scenario"], r["seed"], r["planner"])  # noqa: E731
    la = {key(r): (r["success"], r["length"]) for r in a}
    lb = {key(r): (r["success"], r["length"]) for r in b}
    assert la == lb


def test_runner_resumes_without_duplicates(tmp_path):
    out = run(tmp_path, "a")
    runner.main([str(tmp_path / "c.json"), "--out", str(out)])
    assert len(read(out)) == 12


def test_analyze_outputs_tables(tmp_path):
    out = run(tmp_path, "a")
    analyze.main([str(out), "--no-figures"])
    assert (out / "summary.csv").exists() and (out / "comparisons.csv").exists()
    text = (out / "summary.md").read_text()
    assert "astar_smooth" in text and "Paired comparison" in text


def test_stats_helpers():
    lo, hi = analyze.wilson(5, 10)
    assert 0.2 < lo < 0.5 < hi < 0.8
    assert analyze.holm([0.01, 0.04, 0.03]) == [0.03, 0.06, 0.06]
    m, a, b = analyze.boot_ci([1.0, 2.0, 3.0])
    assert a <= m <= b
