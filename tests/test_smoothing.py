import random

import numpy as np

from baselines.smoothing import prune_visible, relax_vertices, tighten_path
from benchmarks.maps import make_map
from benchmarks.metrics import path_is_valid
from benchmarks.planners import make_planner
from planner_core.utils import astar, path_length


def _open_grid(n=30):
    return np.zeros((n, n), dtype=np.uint8)


def test_tighten_collapses_straight_line_to_two_points():
    grid = _open_grid()
    path = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
    assert tighten_path(path, grid) == [(1, 1), (5, 1)]


def test_tighten_leaves_short_paths_alone():
    grid = _open_grid()
    assert tighten_path(None, grid) is None
    assert tighten_path([(1, 1), (2, 2)], grid) == [(1, 1), (2, 2)]


def test_tighten_keeps_endpoints_validity_and_never_lengthens():
    for seed in range(8):
        grid, start, goal = make_map("random", 40, seed, {"density": 0.25})
        raw = astar(grid, start, goal)
        if raw is None:
            continue
        tight = tighten_path(raw, grid)
        assert tuple(tight[0]) == tuple(start) and tuple(tight[-1]) == tuple(goal)
        assert path_is_valid(tight, grid, start, goal)
        assert path_length(tight) <= path_length(raw) + 1e-9
        assert len(tight) <= len(raw)


def test_tighten_is_deterministic_and_does_not_touch_the_rng():
    grid, start, goal = make_map("random", 40, 3, {"density": 0.25})
    raw = astar(grid, start, goal)
    random.seed(123)
    state = random.getstate()
    a = tighten_path(raw, grid)
    assert random.getstate() == state
    b = tighten_path(raw, grid)
    assert a == b


def test_prune_and_relax_keep_validity():
    grid, start, goal = make_map("random", 40, 5, {"density": 0.30})
    raw = astar(grid, start, goal)
    pruned = prune_visible(list(raw), grid)
    assert path_is_valid(pruned, grid, start, goal)
    relaxed = relax_vertices(pruned, grid)
    assert path_is_valid(relaxed, grid, start, goal)
    assert path_length(relaxed) <= path_length(pruned) + 1e-9


def test_new_baselines_are_valid_and_tightening_does_not_lengthen():
    grid, start, goal = make_map("random", 40, 7, {"density": 0.20})
    random.seed(0)
    lengths = {}
    for name in ("astar_smooth", "theta_star_smooth", "astar_tight", "theta_star_tight"):
        path = make_planner(name).plan(start, goal, grid)
        assert path is not None and path_is_valid(path, grid, start, goal), name
        lengths[name] = path_length(path)
    assert lengths["astar_tight"] <= path_length(astar(grid, start, goal)) + 1e-9


def test_hybrid_tight_is_valid_and_no_longer_than_hybrid_fallback():
    grid, start, goal = make_map("random", 40, 4, {"density": 0.20})
    random.seed(0)
    base = make_planner("hybrid_fallback:max_iterations=1200").plan(start, goal, grid)
    random.seed(0)
    tight = make_planner("hybrid_tight:max_iterations=1200").plan(start, goal, grid)
    assert base is not None and tight is not None
    assert path_is_valid(tight, grid, start, goal)
    assert path_length(tight) <= path_length(base) + 1e-9
