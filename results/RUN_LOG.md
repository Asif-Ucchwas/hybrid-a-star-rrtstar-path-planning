# Run log

One row per benchmark run that produced numbers we use. **Add a row after every run.** The raw CSVs are not
committed (they are large); the summaries behind the README charts are in [`summaries/`](summaries/).
"Runs" means one planner on one map (`configs/*.json` expands to that many tasks).

## Runs behind the current README

| When | Config | Collision rule | Runs | Machine | Notes |
|---|---|---|---:|---|---|
| Oct 2026 | `decision.json` | exact, margin 0.05 | **890** | Legion tower, Core Ultra 7 265K, Python 3.12.3, 1 worker | 7 planners on 130 maps (random d0.10/0.20/0.30 x 30, narrow x 20, maze x 20). Main result. |
| Oct 2026 | `decision_control.json` | sampled (thesis rule) | **450** | same | 5 planners on the 90 random maps. Control: shows what the old rule did. |
| | **Total** | | **1,340** | | |

The commit recorded in `meta.json` for the first run (`a8224e8`) was rewritten when the branch authorship was
reset on 16 Oct 2026. The code is the same as commit `3e6e57f` ("Add an exact collision rule ...").

## Other configs (defined, run count not recorded here)

If you ran these, add a row above with the real count and date. Counts below are what each config expands to.

| Config | Tasks if run in full |
|---|---:|
| `smoke.json` | 135 |
| `pilot.json` | 810 |
| `ablation.json` | 4,200 |
| `sensitivity.json` | 4,600 |
| `ompl_check.json` | 2,530 |
| `paper_smoothing.json` | 9,100 |
| `paper_main.json` | 18,200 |

Not counted: the 50-trial thesis benchmark (`src/`, run on the Acer laptop). Its numbers are in the archived
[thesis README](../docs/THESIS_README.md). Do not mix Acer and Legion timings.
