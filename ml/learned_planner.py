"""Stage 4: RRT* that samples where a trained U-Net expects the shortest path to run.

The thesis Hybrid planner samples inside a corridor drawn around an A* route.
This planner replaces that corridor with the network's heatmap:

* with probability ``goal_sample_rate`` it samples the goal (same as Hybrid),
* with probability ``uniform_mix`` it samples anywhere in free space, so a gap in
  the heatmap can never trap the search (the network leaves a gap on ~7% of maps),
* otherwise it picks a free cell with probability proportional to the heatmap
  and a random point inside that cell.

It uses the same RRT* engine and the same budget as ``hybrid`` (1800 iterations,
2500 nodes). If RRT* finds nothing, ``learned_corridor`` falls back to smoothed A*
exactly like ``hybrid_fallback``; ``learned_tight`` then tightens the path like
``hybrid_tight``. The network runs on the CPU with one thread by default, and its
time is inside the planner's time (``last_info['infer_s']`` reports it separately).

    from benchmarks.planners import make_planner
    p = make_planner("learned_tight")                 # ml/models/unet_v1.pt
    p = make_planner("learned_tight:uniform_mix=0.3,device='cuda'")
"""

import os
import random
import time

import numpy as np
import torch

from baselines.astar_family import AStarSmooth
from baselines.smoothing import tighten_path
from ml.train import UNet, make_input
from planner_core.utils import rrt_star_generic, sample_uniform_free

DEFAULT_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "unet_v1.pt")
_MODELS = {}


def load_model(path=DEFAULT_MODEL, device="cpu"):
    """Load a trained U-Net once per process and keep it."""
    key = (os.path.abspath(path), device)
    if key not in _MODELS:
        ck = torch.load(path, map_location=device)
        model = UNet(base=ck.get("base", 32)).to(device)
        model.load_state_dict(ck["model"])
        model.eval()
        _MODELS[key] = model
    return _MODELS[key]


@torch.no_grad()
def predict_heatmap(model, grid, start, goal, device="cpu"):
    """(H, W) array: chance that the shortest path passes through each cell."""
    g = torch.as_tensor(np.ascontiguousarray(grid), dtype=torch.uint8, device=device).unsqueeze(0)
    s = torch.as_tensor([start], dtype=torch.long, device=device)
    t = torch.as_tensor([goal], dtype=torch.long, device=device)
    logits = model(make_input(g, s, t))
    return torch.sigmoid(logits.float())[0, 0].cpu().numpy()


def sample_from_heatmap(grid, cdf, cells, goal=None, goal_sample_rate=0.10, uniform_mix=0.2):
    """Goal / uniform free space / heatmap-weighted cell, as described in the module docstring."""
    r = random.random()
    if goal is not None and r < goal_sample_rate:
        return (float(goal[0]), float(goal[1]))
    if r < goal_sample_rate + uniform_mix or cells is None:
        return sample_uniform_free(grid, goal=goal, goal_sample_rate=0.0)
    k = int(np.searchsorted(cdf, random.random() * cdf[-1], side="right"))
    y, x = cells[min(k, len(cells) - 1)]
    n = grid.shape[0]
    px = min(max(x + random.uniform(-0.5, 0.5), 0.0), n - 1.0)
    py = min(max(y + random.uniform(-0.5, 0.5), 0.0), n - 1.0)
    return (px, py)


class LearnedCorridor:
    """RRT* guided by the network heatmap, with the same A* fallback as ``hybrid_fallback``."""

    def __init__(self, model_path=DEFAULT_MODEL, device="cpu", threads=1, uniform_mix=0.2,
                 max_iterations=1800, step_size=2.0, neighbor_radius=3.5, goal_threshold=2.0,
                 max_nodes=2500, goal_sample_rate=0.10, fallback=True):
        self.model_path, self.device = model_path, device
        self.uniform_mix = float(uniform_mix)
        self.max_iterations, self.step_size = max_iterations, step_size
        self.neighbor_radius, self.goal_threshold = neighbor_radius, goal_threshold
        self.max_nodes, self.goal_sample_rate = max_nodes, goal_sample_rate
        self.fallback = fallback
        if device == "cpu" and threads:
            torch.set_num_threads(int(threads))
        self.model = load_model(model_path, device)
        self.last_info = {}
        self.heatmap = None

    def plan(self, start, goal, grid):
        start, goal = tuple(int(v) for v in start), tuple(int(v) for v in goal)
        t0 = time.perf_counter()
        heat = predict_heatmap(self.model, grid, start, goal, self.device)
        infer_s = time.perf_counter() - t0
        self.heatmap = heat

        w = np.where(grid == 0, heat, 0.0).ravel()
        keep = np.flatnonzero(w > 1e-6)
        cells = cdf = None
        if len(keep):
            cells = np.stack(np.unravel_index(keep, grid.shape), axis=1)   # rows are (y, x)
            cdf = np.cumsum(w[keep])

        path, nodes = rrt_star_generic(
            grid=grid, start=start, goal=goal, sampler_fn=sample_from_heatmap,
            sampler_args={"grid": grid, "cdf": cdf, "cells": cells, "goal": goal,
                          "goal_sample_rate": self.goal_sample_rate, "uniform_mix": self.uniform_mix},
            max_iterations=self.max_iterations, step_size=self.step_size,
            neighbor_radius=self.neighbor_radius, goal_threshold=self.goal_threshold,
            max_nodes=self.max_nodes)
        info = {"nodes": len(nodes), "infer_s": infer_s}
        if path is None and self.fallback:
            path = AStarSmooth().plan(start, goal, grid)   # None when there is no route at all
            info["fallback"] = path is not None
        self.last_info = info
        return path


class LearnedTight(LearnedCorridor):
    """``learned_corridor`` followed by the same tightening every ``*_tight`` planner gets."""

    def plan(self, start, goal, grid):
        path = super().plan(start, goal, grid)
        return tighten_path(path, grid) if path is not None else None


KINDS = {"learned_corridor": LearnedCorridor, "learned_tight": LearnedTight}


def make_learned(name, **kwargs):
    return KINDS[name](**kwargs)
