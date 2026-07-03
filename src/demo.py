"""
Demo / validation script.

Runs A*, standard RRT*, and the Hybrid A*+corridor-RRT* planner on the
same random map, and saves comparison figures. Use this to sanity-check
the ported algorithms and to generate images for the README / LinkedIn.

Usage:
    python demo.py
"""

import os
import matplotlib
matplotlib.use("Agg")  # headless-safe backend, works over SSH/WSL2 too
import matplotlib.pyplot as plt

from utils import make_grid, set_start_goal_free, astar, path_length
from hybrid_astar import HybridAStar
from rrt_star import RRTStar


def plot_grid(ax, grid, title=""):
    ax.imshow(grid, cmap="gray_r", origin="lower")
    ax.set_title(title)
    ax.set_xlim(-0.5, grid.shape[0] - 0.5)
    ax.set_ylim(-0.5, grid.shape[0] - 0.5)
    ax.set_aspect("equal")


def plot_path(ax, path, color="blue", lw=2, label=None):
    if path is None or len(path) < 2:
        return
    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    ax.plot(xs, ys, color=color, linewidth=lw, label=label)


def main():
    out_dir = "figures"
    os.makedirs(out_dir, exist_ok=True)

    grid = make_grid(size=50, obstacle_prob=0.20, seed=1)
    start, goal = (2, 2), (47, 47)
    set_start_goal_free(grid, start, goal)

    print("Running A*...")
    a_path = astar(grid, start, goal)
    print(f"  A* length: {path_length(a_path):.2f}")

    print("Running standard RRT*...")
    rrt = RRTStar()
    rrt_path = rrt.plan(start, goal, grid)
    print(f"  RRT* length: {path_length(rrt_path):.2f}" if rrt_path else "  RRT* FAILED")

    print("Running Hybrid A* + corridor RRT*...")
    hybrid = HybridAStar()
    hybrid_path = hybrid.plan(start, goal, grid)
    print(f"  Hybrid length: {path_length(hybrid_path):.2f}" if hybrid_path else "  Hybrid FAILED")

    fig, ax = plt.subplots(figsize=(8, 8))
    plot_grid(ax, grid, title="A* vs RRT* vs Hybrid A*+Corridor RRT*")
    plot_path(ax, a_path, color="blue", lw=2, label="A*")
    plot_path(ax, rrt_path, color="green", lw=2, label="RRT* (standard)")
    plot_path(ax, hybrid_path, color="red", lw=2, label="Hybrid (ours)")
    ax.scatter([start[0], goal[0]], [start[1], goal[1]], s=80, marker="o", color="black", zorder=5)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "comparison.png"), dpi=150)
    print(f"\nSaved figures/comparison.png")

    plt.close("all")


if __name__ == "__main__":
    main()
