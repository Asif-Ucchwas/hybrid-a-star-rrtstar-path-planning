# Run log

One row per benchmark run on this project. **Add a row after every run.** The raw CSVs and logs are not
committed (they are large); the summaries behind the README charts are in [`summaries/`](summaries/).
"Runs" means one planner on one map (`configs/*.json` expands to that many rows in `raw.csv`).
The exact timestamp of each run is in its `meta.json`.

**Machine for all rows: Legion tower** (Core Ultra 7 265K, Python 3.12.3). The thesis benchmark was run earlier
on the Acer laptop and is not counted here. Do not mix Acer and Legion timings.

## Total

| | Runs |
|---|---:|
| All runs below | **52,070** |
| Behind the numbers in the README (`decision*` rows + the 8,650 ML rows) | **12,630** |

## Runs behind the current README

| Folder | Config | Collision rule | Runs | Notes |
|---|---|---|---:|---|
| `results/decision/` | `decision.json` | exact, margin 0.05 | **890** | 7 planners on 130 maps (random d0.10/0.20/0.30 x 30, narrow x 20, maze x 20). Main result. 1 worker, clean timing. |
| `results/decision_control/` | `decision_control.json` | sampled (thesis rule) | **450** | 5 planners on the 90 random maps. Control: shows what the old rule did. |

The commit recorded in `meta.json` for `decision` (`a8224e8`) was rewritten on 16 Oct 2026 when the branch
authorship was reset. The code is the same as commit `3e6e57f` ("Add an exact collision rule ...").

## Runs added 21 Nov 2026 (ML extension, branch `ml-corridor`)

Learned corridor planners (`learned_corridor`, `learned_tight`, model `ml/models/unet_v1.pt`) against the thesis
planner, Theta\* + tighten and plain RRT\*. Exact rule, margin 0.05. Started 15:54, finished 17:10
(`ml/run_stage5.sh`). Tables: [`summaries/ml_stage5_report.md`](summaries/ml_stage5_report.md).

| Folder | Config | Collision rule | Runs | Notes |
|---|---|---|---:|---|
| `results/ml_main/` | `ml_main.json` | exact, margin 0.05 | **3,550** | 8 planners on 450 maps (random d0.10/0.20/0.30 x 100, narrow x 100, maze x 50; map seeds 0-99, 0-29 = `decision` maps). 1 worker, clean timing. |
| `results/ml_budget/` | `ml_budget.json` | exact, margin 0.05 | **4,500** | `rrt_star`, `hybrid`, `learned_corridor` (no fallback, no tightening) at 300/600/1200/1800/3600 iterations on 300 maps. 1 worker. |
| `results/ml_big/` | `ml_big.json` | exact, margin 0.05 | **500** | 5 planners on 100 maps of 100x100 (d0.20/0.30 x 50). 1 worker. |
| `results/ml_big_ref/` | `ml_big_ref.json` | exact, margin 0.05 | **100** | `vis_graph` on the same 100x100 maps, length reference only (18 workers, timing not used). |

Not counted as benchmark runs: the training data (99,269 `vis_graph` paths on seeds 100000+, `ml/make_dataset.py`).

## Runs added 16 Oct 2026 (RRT* and the other sampling planners)

Same 7-planner idea as `decision`, but the planner list is RRT*, Informed RRT*, RRT-Connect, BIT*, `hybrid`
(no fallback), `hybrid_fallback` and `theta_star_tight`. Same maps and map seeds as `decision` and
`decision_control`. `meta.json` records commit `02591d5` for the first two rows and `7ffdcd7` for the budget rows. 1 worker, clean timing.

| Folder | Config | Collision rule | Runs | Notes |
|---|---|---|---:|---|
| `results/decision_rrt/` | `decision_rrt.json` | exact, margin 0.05 | **910** | 7 planners on 130 maps. Re-tests the thesis RRT* comparison under the exact rule. |
| `results/decision_rrt_control/` | `decision_rrt_control.json` | sampled (thesis rule) | **630** | 7 planners on the 90 random maps. |
| `results/decision_rrt_budget/` | `decision_rrt_budget.json` | exact, margin 0.05 | **650** | Budget control: `rrt_star` and `hybrid` at the default budget (1800 iterations, 2500 nodes), `rrt_star_x2` and `hybrid_x2` at twice that, plus `theta_star_tight`, on 130 maps. |
| `results/decision_rrt_budget_control/` | `decision_rrt_budget_control.json` | sampled (thesis rule) | **450** | Same 5 planners on the 90 random maps. |

## Earlier runs (sampled collision rule, not used for the README numbers)

These ran before the exact collision rule existed, so they use the thesis sampled rule.

| Folder | Config | Runs |
|---|---|---:|
| `results/pilot_legion/` | `pilot.json` | 810 |
| `results/ablation/` | `ablation.json` | 4,200 |
| `results/sensitivity/` | `sensitivity.json` | 4,600 |
| `results/ompl_check/` | `ompl_check.json` | 2,530 |
| `results/paper_smoothing/` | `paper_smoothing.json` | 9,100 |
| `results/paper_main/` | `paper_main.json` | 18,200 |

`smoke.json` (135 runs) is the one-minute check from CI and is not counted.

Not counted: the 50-trial thesis benchmark (`src/`, Acer laptop). Its numbers are in the archived
[thesis README](../docs/THESIS_README.md).
