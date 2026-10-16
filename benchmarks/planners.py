"""Planner registry: build any planner from a short text spec.

Spec format: ``name`` or ``name:key=value,key=value`` with Python-literal values,
for example ``hybrid:base_width=2,max_extra=0`` (a fixed 2-cell corridor).

Names: astar, astar_smooth, theta_star, theta_star_smooth, astar_tight,
theta_star_tight, rrt_star, informed_rrt_star, rrt_connect, bit_star, hybrid,
hybrid_fallback, hybrid_tight.
Optional (pip install ompl): ompl_rrt_star, ompl_informed_rrt_star, ompl_rrt_connect,
ompl_bit_star. ``ompl_*:time_limit=2.0`` sets the planning budget in seconds.
"""

import ast

from baselines.astar_family import AStarSmooth, AStarTight, ThetaStar, ThetaStarSmooth, ThetaStarTight
from baselines.smoothing import tighten_path
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


class HybridTight(HybridFallback):
    """``hybrid_fallback`` followed by the same deterministic tightening the A*/Theta* baselines get."""

    def plan(self, start, goal, grid):
        path = super().plan(start, goal, grid)
        return tighten_path(path, grid) if path is not None else None


REGISTRY = {
    "astar": AStarRaw,
    "astar_smooth": AStarSmooth,
    "theta_star": ThetaStar,
    "theta_star_smooth": ThetaStarSmooth,
    "astar_tight": AStarTight,
    "theta_star_tight": ThetaStarTight,
    "hybrid_tight": HybridTight,
    "rrt_star": RRTStar,
    "informed_rrt_star": InformedRRTStar,
    "rrt_connect": RRTConnect,
    "bit_star": BITStar,
    "hybrid": HybridAStar,
    "hybrid_fallback": HybridFallback,
}


# Optional reference-library planners (need ``pip install ompl``); see baselines/ompl_adapters.py
OMPL_KINDS = ("ompl_rrt_star", "ompl_informed_rrt_star", "ompl_rrt_connect", "ompl_bit_star")


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
    if name in OMPL_KINDS:
        from baselines.ompl_adapters import make_ompl
        return make_ompl(name, **kwargs)
    if name not in REGISTRY:
        raise ValueError(f"unknown planner {name!r}; choose from "
                         f"{sorted(REGISTRY) + sorted(OMPL_KINDS)}")
    return REGISTRY[name](**kwargs)


def planner_nodes(planner):
    """Number of tree nodes the planner built, if it reports it."""
    info = getattr(planner, "last_info", None) or {}
    if "nodes" in info:
        return info["nodes"]
    return len(getattr(planner, "last_nodes", []) or [])
