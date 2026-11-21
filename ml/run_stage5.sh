#!/usr/bin/env bash
# Stage 5: the full benchmark of the learned planners. Safe to re-run: every part resumes
# where it stopped (finished runs are skipped).
#   A ml_main    50x50 test maps, all planners          1 worker (clean timing)
#   B ml_budget  success vs search budget, no fallback  1 worker (clean timing)
#   C ml_big     100x100 maps (never trained on)        1 worker (clean timing)
#   D ml_big_ref exact shortest paths for C             many workers (reference only)
# Then: statistics, tables and figures for each (benchmarks.analyze).
set -euo pipefail
cd "$(dirname "$0")/.."
stamp() { echo; echo "=== $(date '+%a %H:%M:%S')  $*"; }

stamp "A  ml_main (3550 runs)";    python -m benchmarks.runner configs/ml_main.json    --workers 1
stamp "B  ml_budget (4500 runs)";  python -m benchmarks.runner configs/ml_budget.json  --workers 1
stamp "C  ml_big (500 runs)";      python -m benchmarks.runner configs/ml_big.json     --workers 1
stamp "D  ml_big_ref (100 runs)";  python -m benchmarks.runner configs/ml_big_ref.json --workers "$(( $(nproc) - 2 ))"

stamp "Analysis"
python -m benchmarks.analyze results/ml_main   --ref hybrid_tight
python -m benchmarks.analyze results/ml_budget --ref hybrid@1800 --no-figures
python -m benchmarks.analyze results/ml_big    --ref hybrid_tight
python -m ml.summarize results/ml_main/raw.csv
python -m ml.summarize results/ml_big/raw.csv
stamp "STAGE 5 DONE"
