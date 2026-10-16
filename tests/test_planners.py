import random

import pytest

from benchmarks.maps import make_map
from benchmarks.metrics import path_is_valid
from benchmarks.planners import REGISTRY, make_planner, parse_spec


def test_parse_spec():
    assert parse_spec("hybrid") == ("hybrid", {})
    assert parse_spec("hybrid:base_width=2,max_extra=0") == ("hybrid", {"base_width": 2, "max_extra": 0})
    assert parse_spec("rrt_star:step_size=1.5")[1] == {"step_size": 1.5}


def test_unknown_planner_name_is_rejected():
    with pytest.raises(ValueError):
        make_planner("nope")


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_every_planner_returns_valid_path_on_easy_map(name):
    grid, start, goal = make_map("random", 30, 2, {"density": 0.10})
    spec = name
    if name in ("rrt_star", "informed_rrt_star", "hybrid", "hybrid_fallback"):
        spec = f"{name}:max_iterations=1200"
    random.seed(0)
    path = make_planner(spec).plan(start, goal, grid)
    assert path is not None, name
    assert path_is_valid(path, grid, start, goal), name


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_planners_return_none_when_no_route(name):
    grid, start, goal = make_map("random", 30, 2, {"density": 0.0})
    grid[:, 15] = 1
    spec = name
    if name in ("rrt_star", "informed_rrt_star", "hybrid", "hybrid_fallback"):
        spec = f"{name}:max_iterations=100"
    if name == "bit_star":
        spec = "bit_star:max_batches=2"
    random.seed(0)
    assert make_planner(spec).plan(start, goal, grid) is None


def test_hybrid_fallback_reports_fallback_when_corridor_search_fails():
    grid, start, goal = make_map("random", 30, 2, {"density": 0.0})
    planner = make_planner("hybrid_fallback:max_iterations=1")
    random.seed(0)
    path = planner.plan(start, goal, grid)
    assert path is not None and path_is_valid(path, grid, start, goal)
    assert planner.last_info.get("fallback") is True


ompl = pytest.importorskip("ompl", reason="optional: pip install ompl")


@pytest.mark.parametrize("name", ["ompl_rrt_star", "ompl_informed_rrt_star",
                                  "ompl_rrt_connect", "ompl_bit_star"])
def test_ompl_planners_return_valid_path_on_easy_map(name):
    grid, start, goal = make_map("random", 30, 2, {"density": 0.10})
    random.seed(0)
    path = make_planner(f"{name}:time_limit=0.3").plan(start, goal, grid)
    assert path is not None, name
    assert path_is_valid(path, grid, start, goal), name


def test_ompl_planner_returns_none_when_no_route():
    grid, start, goal = make_map("random", 30, 2, {"density": 0.0})
    grid[:, 15] = 1
    assert make_planner("ompl_rrt_connect:time_limit=0.1").plan(start, goal, grid) is None
