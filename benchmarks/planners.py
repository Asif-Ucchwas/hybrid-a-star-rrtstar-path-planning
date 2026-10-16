"""Planner registry: build any planner from a short text spec.

Spec format: ``name`` or ``name:key=value,key=value`` with Python-literal values,
for example ``hybrid:base_width=2,max_extra=0`` (a fixed 2-cell corridor).

Names: astar, astar_smooth, theta_star, rrt_star, informed_rrt_star,
rrt_connect, bit_star, hybrid, hybrid_fallback.
"""

import ast

from baselines.astar_family import AStarSmooth, ThetaStar
from baselines.sampling_family import BITStar, InformedRRTStar, RRTConnect
from planner_core import HybridAStar, RRTStar
from planner_core.utils import astar


class AStarRaw:
    """Plain 8-connected grid A* with no smoothing (the thesis baseline)."""

    last_info = {}

    def plan(self, start, goal, grid):
        return astar(grid, start, goal)


class HybridFallback:
    """Hybrid corridor planner that falls back to smoothed A* if RRT* fails.

    ``last_info['fallback']`` is True when the fallback produced the path.
    """

    def __init__(self, **kwargs):
        self.hybrid = HybridAStar(**kwargs)
        self.fallback = AStarSmooth()
        self.last_info = {}

    def plan(self, start, goal, grid):
        path = self.hybrid.plan(start, goal, grid)
        info = {"nodes": len(getattr(self.hybrid, "last_nodes", []) or [])}
        if path is None and getattr(self.hybrid, "astar_path", None) is not None:
            path = self.fallback.plan(start, goal, grid)
            info["fallback"] = True
        self.last_info = info
        return path


REGISTRY = {
    "astar": AStarRaw,
    "astar_smooth": AStarSmooth,
    "theta_star": ThetaStar,
    "rrt_star": RRTStar,
    "informed_rrt_star": InformedRRTStar,
    "rrt_connect": RRTConnect,
    "bit_star": BITStar,
    "hybrid": HybridAStar,
    "hybrid_fallback": HybridFallback,
}


def parse_spec(spec):
    """Split a spec string into ``(name, kwargs)``."""
    name, _, rest = spec.partition(":")
    name = name.strip()
    kwargs = {}
    if rest.strip():
        for item in rest.split(","):
            key, _, val = item.partition("=")
            kwargs[key.strip()] = ast.literal_eval(val.strip())
    return name, kwargs


def make_planner(spec):
    name, kwargs = parse_spec(spec)
    if name not in REGISTRY:
        raise ValueError(f"unknown planner {name!r}; choose from {sorted(REGISTRY)}")
    return REGISTRY[name](**kwargs)


def planner_nodes(planner):
    """Number of tree nodes the planner built, if it reports it."""
    info = getattr(planner, "last_info", None) or {}
    if "nodes" in info:
        return info["nodes"]
    return len(getattr(planner, "last_nodes", []) or [])
