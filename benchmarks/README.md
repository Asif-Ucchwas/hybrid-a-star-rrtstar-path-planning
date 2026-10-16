# Benchmarks

One command runs every planner on the same seeded maps and writes a CSV; a second
command turns the CSV into tables, statistics and figures.

## Quick start

```bash
pip install -r requirements-dev.txt        # numpy, scipy, matplotlib, pytest, flake8
python -m pytest -q                        # unit tests (~30 s)

# 1. tiny smoke run (about a minute)
python -m benchmarks.runner configs/smoke.json --out results/smoke --workers 2
python -m benchmarks.analyze results/smoke

# 2. the paper experiments (long: run on the lab server)
python -m benchmarks.runner configs/paper_main.json --workers 1      # clean timing
python -m benchmarks.runner configs/ablation.json --workers 1
python -m benchmarks.runner configs/sensitivity.json --workers 1
python -m benchmarks.analyze results/paper_main
python -m benchmarks.analyze results/ablation --ref hybrid
python -m benchmarks.analyze results/sensitivity --sweep base_width
```

Runs are resumable: if a job is interrupted, run the same command again and it
continues from the last finished run.

## What is compared

| id | planner |
|---|---|
| `astar` | plain 8-connected A* (the thesis baseline) |
| `astar_smooth` | A* + the same random-shortcut smoothing RRT* paths get |
| `theta_star` | Theta* (any-angle A*) |
| `rrt_star` | RRT* (the thesis baseline, `planner_core.RRTStar`) |
| `informed_rrt_star` | Informed RRT* |
| `rrt_connect` | RRT-Connect (not optimal) |
| `bit_star` | BIT*, compact re-implementation (see the docstring for the simplification) |
| `hybrid` | the A*-seeded adaptive-corridor RRT* (`planner_core.HybridAStar`) |
| `hybrid_fallback` | `hybrid`, falling back to smoothed A* when RRT* fails |

Planner specs in a config can set parameters: `"hybrid:base_width=2,max_extra=0"`
is a *fixed* 2-cell corridor (the ablation), `"hybrid:max_iterations=600"` changes
the budget. Use `{"id": "name", "spec": "..."}` to give a spec a short name.

Map kinds: `random` (density), `narrow` (walls with narrow gaps), `maze`, and
`image` (any PGM/PNG occupancy map, e.g. a Nav2 or TurtleBot3 map).

## What is measured (per run)

success (valid path only), planning time (wall and CPU), path length and length
relative to raw A*, total and mean turning angle (smoothness), mean and minimum
clearance, number of tree nodes, and whether the A* fallback was used.
`strict_valid` is 0 when the path clips an obstacle corner that the planners' own
collision check (one sample per 1/3 cell) did not catch.

## Statistics

Success rate has a 95% Wilson interval. Means have 95% bootstrap intervals
(successful runs only). Planners are compared with a reference on the *same maps*:
exact McNemar test for success, Wilcoxon signed-rank for length, time, turning and
clearance (maps where both succeeded), Holm-adjusted per scenario and metric.

## Reproducibility and timing

* Every map comes from `(kind, size, seed, params)`. Every planner run is seeded
  from `(scenario, map seed, planner id)`, so results repeat exactly.
* `meta.json` records the config, git commit, CPU, Python and NumPy versions.
* **Timing is only publishable with `--workers 1` on an idle machine.** With more
  workers the planners compete for CPU and cache. `cpu_s` is steadier than `time_s`.
* Report timings from native Linux (the lab server or the Acer), not WSL2.

## Latency profile

```bash
python -m benchmarks.profile_planner hybrid --seed 0
```

## Reference-library check (OMPL)

`configs/ompl_check.json` runs our compact sampling baselines next to the same
algorithms from OMPL (`ompl_rrt_star`, `ompl_informed_rrt_star`, `ompl_rrt_connect`,
`ompl_bit_star`). Install the optional package first: `pip install -r requirements-ompl.txt`.

```
python3 -m benchmarks.runner configs/ompl_check.json --workers 1 --out results/ompl_check
python3 -m benchmarks.analyze results/ompl_check
```

Rules (details in `baselines/ompl_adapters.py`):
- OMPL optimising planners run for a fixed time budget (default 1 s, `ompl_rrt_star:time_limit=2.0`
  to change it). RRT-Connect stops at its first solution. Our own planners run a fixed number of
  iterations, so compare quality at a similar time, not iteration counts.
- OMPL's collision check is slightly conservative (0.15 cell margin, 0.1 cell motion step) so it
  never accepts a segment the benchmark's validity check rejects.
- OMPL keeps one global random generator per process and cannot be re-seeded per run, so OMPL
  results are not reproducible run by run. Maps and all other planners are.
