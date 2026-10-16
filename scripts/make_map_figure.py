"""Draw one benchmark map with the paths of a few planners (used in the README).

Runs the planners exactly as ``benchmarks.runner`` does (exact collision rule, margin 0.05,
per-run seeds from ``derive_seed``), so a given ``--seed`` always gives the same picture.

    python scripts/make_map_figure.py --seed 3 --out assets/readme/example_map.png
    python scripts/make_map_figure.py --list      # one line per seed, to pick a good example
"""

import argparse
import os
import random
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.maps import make_map  # noqa: E402
from benchmarks.metrics import evaluate_path  # noqa: E402
from benchmarks.planners import make_planner  # noqa: E402
from benchmarks.runner import derive_seed  # noqa: E402
from planner_core.utils import set_collision_mode  # noqa: E402

SCENARIO = "random_d0.20"
DENSITY = 0.20
PLANNERS = [("astar_smooth", "A* + shortcut"), ("theta_star_tight", "Theta* + tighten"),
            ("hybrid_tight", "Hybrid + tighten")]
REFERENCE = "vis_graph"


def run(seed):
    set_collision_mode("exact", 0.05)
    grid, start, goal = make_map("random", 50, seed, {"density": DENSITY})
    out = {}
    for pid, _ in PLANNERS + [(REFERENCE, "Shortest path")]:
        planner = make_planner(pid)
        rseed = derive_seed(SCENARIO, seed, pid)
        random.seed(rseed)
        np.random.seed(rseed)
        t0 = time.perf_counter()
        path = planner.plan(start, goal, grid)
        dt = time.perf_counter() - t0
        info = getattr(planner, "last_info", None) or {}
        out[pid] = dict(path=path, time=dt, fallback=bool(info.get("fallback")))
        if path is not None:
            m = evaluate_path(path, grid)
            out[pid].update(length=m["length"], turn=m["turn_total_deg"])
    return grid, start, goal, out


def draw(seed, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    grid, start, goal, res = run(seed)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.6))
    colors = {"astar_smooth": "#d95f02", "theta_star_tight": "#1b6ca8", "hybrid_tight": "#1b9e77"}
    ys, xs = np.nonzero(grid)
    for ax, (pid, label) in zip(axes, PLANNERS):
        ax.set_facecolor("#f7f7f7")
        for x, y in zip(xs, ys):
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, color="#3a3f47", lw=0))
        ref = res[REFERENCE]["path"]
        if ref:
            ax.plot(*zip(*ref), color="black", lw=1.1, ls=(0, (4, 3)), label="exact shortest path", zorder=3)
        r = res[pid]
        if r["path"]:
            px, py = zip(*r["path"])
            ax.plot(px, py, color=colors[pid], lw=2.4, marker="o", ms=3.2, label=label, zorder=4)
        ax.scatter(*start, s=90, marker="s", color="#2ca02c", edgecolor="white", zorder=5)
        ax.scatter(*goal, s=130, marker="*", color="#d62728", edgecolor="white", zorder=5)
        ax.set_xlim(-0.5, 49.5)
        ax.set_ylim(-0.5, 49.5)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        note = "  (fell back to A*)" if r["fallback"] else ""
        ax.set_title(f"{label}{note}\nlength {r['length']:.1f} cells   turning {r['turn']:.0f}°", fontsize=10)
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color="black", lw=1.2, ls=(0, (4, 3)), label="exact shortest path"),
               Line2D([0], [0], marker="s", color="w", markerfacecolor="#2ca02c", ms=9, label="start"),
               Line2D([0], [0], marker="*", color="w", markerfacecolor="#d62728", ms=13, label="goal"),
               Line2D([0], [0], marker="s", color="w", markerfacecolor="#3a3f47", ms=9,
                      label="obstacle cell")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=9, frameon=False)
    fig.suptitle(f"One 50×50 map, obstacle density {DENSITY:.2f} (seed {seed}, exact collision rule)",
                 fontsize=11, y=0.985)
    fig.tight_layout(rect=[0, 0.05, 1, 0.94])
    fig.savefig(out_path, dpi=170)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="assets/readme/example_map.png")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        for s in range(30):
            _, _, _, res = run(s)
            row = []
            for pid, _ in PLANNERS + [(REFERENCE, "")]:
                r = res[pid]
                row.append(f"{pid}:{r.get('length', float('nan')):.1f}/{r.get('turn', float('nan')):.0f}"
                           f"{'F' if r['fallback'] else ''}")
            print(s, " ".join(row))
        return
    draw(args.seed, args.out)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
