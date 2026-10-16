# Dev log

Newest first. Plain notes on what changed and what we learned. Numbers come from [`results/RUN_LOG.md`](../results/RUN_LOG.md).

## 2026-10-16: the collision rule decides the ranking

- Added an **exact** collision rule (obstacle cell inflated by a 0.05 margin; touching counts as a collision)
  next to the thesis **sampled** rule.
- Added `vis_graph`, the exact shortest path, as a length reference.
- Final run: 890 runs (exact rule) + 450 runs (sampled control).
- **Finding:** Hybrid beats A\* + shortcut, but not Theta\* + tighten. All tightened planners are within 4.5%
  of the shortest path. Hybrid costs 6.5-34x the time and falls back to A\* in 40-60% of runs on dense maps at
  default settings. Under the old sampled rule Hybrid looked 43-60% smoother than Theta\* + tighten on the
  sparser maps; under the exact rule that shrinks to 25% at density 0.10 and is not significant elsewhere.
- Consequence: no algorithm-novelty claim. The work becomes a short benchmark / collision-rule report, and the
  rover / ROS2 work becomes the main line.
- README rewritten with charts and an example map. Thesis README archived to `docs/THESIS_README.md`.

## 2026-10-16: stronger baselines

- Added a like-for-like Theta\* (`theta_star_cc`) and stronger smoothing baselines (deterministic tightening).
- Added `paper_smoothing` config.

## 2026-10-15: reproducible benchmark repo

- New `planner_core` package; `src/` became thin wrappers.
- Added `baselines/`, `benchmarks/` (map generators, runner, metrics, paired statistics), tests, CI, LICENSE,
  `CITATION.cff`.
- Optional OMPL reference baselines and `ompl_check` config.
- Speed-up of the planner core with identical results; renamed the fine-sampling metric.
- Runs are seeded per (scenario, map, planner), so reruns reproduce exactly.

## May 2026: thesis

- M.E.S. thesis, Lamar University: A\*-seeded adaptive-corridor RRT\* and standalone ROS2 nodes.
- Benchmarked on a small laptop with the sampled collision rule and weaker baselines. See
  [`THESIS_README.md`](THESIS_README.md). Tag: `v1.0-thesis`.
