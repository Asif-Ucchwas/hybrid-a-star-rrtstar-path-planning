# ml/ — a learned corridor for the corridor RRT*

Can a small neural network draw a better sampling corridor than the A\* route the thesis planner uses?
This folder holds the whole experiment, from data to benchmark. Results and conclusions are in the
[top-level README](../README.md#-ml-extension-can-a-network-draw-a-better-corridor) and
[`results/summaries/ml_stage5_report.md`](../results/summaries/ml_stage5_report.md).

## Pipeline

| Stage | File | What it does | On the Legion |
|---|---|---|---|
| 1 | `make_dataset.py` | 99,269 seeded 50x50 maps (random and narrow, varied settings; half with random start/goal) labelled with the **exact** shortest path (`vis_graph`, exact collision rule, 0.05 margin). Seeds start at 100000, so no benchmark map is ever trained on. Mazes are left out on purpose. | 18 CPU workers, 2 h 54 min |
| 1 | `check_dataset.py` | Totals, sanity checks (no path cell on an obstacle, start/goal on the path, no seed overlap) and an example picture. | seconds |
| 3 | `train.py` | U-Net (1.93 M parameters, 3 input channels: obstacles, start, goal) predicts for every cell the chance that the shortest path passes through it. Loss: BCE + soft Dice. 90° rotations and mirrors as augmentation. Checkpoints every epoch, resumes after a stop. | RTX 5080, 40 epochs in 7 min |
| 4 | `learned_planner.py` | `learned_corridor` / `learned_tight`: the thesis RRT\* engine and budget, but samples come 10% from the goal, 20% from anywhere in free space and 70% from the heatmap. Same A\* fallback as `hybrid_fallback`. The network runs on one CPU thread and its time counts. | — |
| 5 | `run_stage5.sh`, `report_stage5.py` | 8,650 benchmark runs (see `configs/ml_*.json`) and one report with paired tests. | 1 worker, 1 h 16 min |
| — | `summarize.py` | Quick per-scenario table for any `raw.csv`. | — |
| — | `models/unet_v1.pt` | The trained model (+ training log and validation picture). | — |

## Reproduce

```bash
pip install -r requirements-ml.txt      # PyTorch etc.; see the file for the CUDA wheel index
python -m ml.make_dataset --n 100000 --out data/ml_corridor    # ~3 h on 18 workers
python -m ml.check_dataset data/ml_corridor
python -m ml.train --epochs 40 --name unet_v1                  # ~7 min on an RTX 5080
cp runs/unet_v1/best.pt ml/models/unet_v1.pt
./ml/run_stage5.sh                                             # ~1.3 h, 1 worker
python -m ml.report_stage5
```

The learned planners also work from the normal registry once PyTorch is installed:
`make_planner("learned_tight")`. Their tests (`tests/test_learned_planner.py`) are skipped when PyTorch or
the model file is missing, as in CI. If ROS 2 is sourced in the same shell, run the tests with
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` (ROS ships a pytest plugin that needs `yaml`).

## Validation (4,963 held-out maps)

| IoU | coverage | connected | corridor size |
|---:|---:|---:|---:|
| 0.760 | 0.960 | 0.927 | 9.4% of free cells |

*coverage*: share of true path cells inside the predicted corridor; *connected*: share of maps where the
corridor links start and goal through free cells; *corridor size*: how much of the free space it keeps.
