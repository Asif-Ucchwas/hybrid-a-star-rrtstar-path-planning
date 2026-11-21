"""Print a quick per-scenario table from a benchmark raw.csv (success, fallbacks, length, turning, time).

    python -m ml.summarize results/ml_smoke/raw.csv
"""

import csv
import math
import statistics as st
import sys


def main(path):
    rows = list(csv.DictReader(open(path)))
    planners = list(dict.fromkeys(r["planner"] for r in sorted(rows, key=lambda r: r["planner"])))
    for sc in dict.fromkeys(r["scenario"] for r in rows):
        print(f"\n{sc}")
        print(f"{'planner':<20}{'success':>9}{'fallback':>10}{'length':>9}{'turning':>9}{'time':>9}")
        for p in planners:
            rs = [r for r in rows if r["scenario"] == sc and r["planner"] == p]
            if not rs:
                continue
            ok = [r for r in rs if r["success"] == "1"]

            def mean(k):
                return st.mean(float(r[k]) for r in ok) if ok else math.nan

            fb = sum(r["fallback"] == "1" for r in rs)
            print(f"{p:<20}{len(ok):>5}/{len(rs):<4}{fb:>7}   {mean('length'):>7.1f}"
                  f"{mean('turn_total_deg'):>8.0f}°{mean('time_s'):>8.2f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/ml_smoke/raw.csv")
