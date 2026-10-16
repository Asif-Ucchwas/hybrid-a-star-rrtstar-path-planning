import heapq
import math
import random

import numpy as np
import pytest

from planner_core.utils import get_collision_margin, set_collision_mode

from baselines.visgraph import VisGraphShortest, corner_points
from benchmarks.maps import make_map
from benchmarks.metrics import path_is_valid
from benchmarks.planners import make_planner
from planner_core.utils import line_collision_free, path_length


@pytest.fixture(autouse=True)
def exact_rule():
    set_collision_mode("exact", margin=0.05)
    yield
    set_collision_mode("sampled")


def _brute_force_length(start, goal, grid):
    """Dijkstra over the full visibility graph (no pruning, no bound)."""
    eps = get_collision_margin() + 0.001
    pts = [tuple(map(float, start)), tuple(map(float, goal))] + [tuple(p) for p in corner_points(grid, eps)]
    n = len(pts)
    dist = [math.inf] * n
    dist[0] = 0.0
    heap = [(0.0, 0)]
    done = [False] * n
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        if u == 1:
            return d
        for v in range(n):
            if done[v]:
                continue
            nd = d + math.hypot(pts[u][0] - pts[v][0], pts[u][1] - pts[v][1])
            if nd < dist[v] and line_collision_free(pts[u], pts[v], grid):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return math.inf


def test_corner_points_are_in_free_cells_and_in_bounds():
    grid, _, _ = make_map("random", 30, 1, {"density": 0.25})
    pts = corner_points(grid, 0.05 + 0.001)
    assert len(pts) > 0
    n = grid.shape[0]
    for x, y in pts:
        assert 0 <= x <= n - 1 and 0 <= y <= n - 1
        if x % 1 == 0.5 and y % 1 == 0.5:      # squeeze point between diagonal obstacles
            continue
        assert grid[int(round(y)), int(round(x))] == 0


def test_open_grid_gives_a_straight_segment():
    grid = np.zeros((20, 20), dtype=np.uint8)
    assert make_planner("vis_graph").plan((2, 2), (17, 17), grid) == [(2, 2), (17, 17)]


@pytest.mark.parametrize("seed", range(6))
def test_matches_brute_force_visibility_graph(seed):
    grid, start, goal = make_map("random", 25, seed, {"density": 0.25})
    path = make_planner("vis_graph").plan(start, goal, grid)
    assert path is not None and path_is_valid(path, grid, start, goal)
    assert path_length(path) == pytest.approx(_brute_force_length(start, goal, grid), abs=1e-6)


def test_not_longer_than_tightened_theta_star_under_exact_rule():
    for seed in range(6):
        grid, start, goal = make_map("random", 40, seed, {"density": 0.25})
        ref = path_length(make_planner("vis_graph").plan(start, goal, grid))
        other = path_length(make_planner("theta_star_tight").plan(start, goal, grid))
        assert ref <= other + 0.01


def test_returns_none_when_no_route():
    grid, start, goal = make_map("random", 30, 2, {"density": 0.0})
    grid[:, 15] = 1
    assert make_planner("vis_graph").plan(start, goal, grid) is None


def test_deterministic_and_does_not_touch_rng():
    grid, start, goal = make_map("random", 30, 3, {"density": 0.25})
    random.seed(7)
    state = random.getstate()
    a = VisGraphShortest().plan(start, goal, grid)
    assert random.getstate() == state
    assert a == VisGraphShortest().plan(start, goal, grid)


def test_zero_margin_graph_includes_squeeze_points_and_still_matches_brute_force():
    set_collision_mode("exact", margin=0.0)
    g = np.zeros((8, 8), dtype=np.uint8)
    g[3, 3] = g[4, 4] = 1
    pts = {tuple(p) for p in corner_points(g)}
    assert (3.5, 3.5) in pts
    for seed in range(4):
        grid, start, goal = make_map("random", 25, seed, {"density": 0.25})
        path = make_planner("vis_graph").plan(start, goal, grid)
        assert path_length(path) == pytest.approx(_brute_force_length(start, goal, grid), abs=1e-6)
