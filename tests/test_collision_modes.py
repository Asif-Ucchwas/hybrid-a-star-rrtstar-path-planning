import random

import numpy as np
import pytest

from benchmarks.maps import make_map
from benchmarks.metrics import path_is_valid
from benchmarks.planners import make_planner
from planner_core import utils
from planner_core.utils import (astar, get_collision_margin, get_collision_mode,
                                line_collision_free, set_collision_mode)


@pytest.fixture(autouse=True)
def restore_mode():
    yield
    set_collision_mode("sampled")


def _grid_with(*cells, n=10):
    g = np.zeros((n, n), dtype=np.uint8)
    for x, y in cells:
        g[y, x] = 1
    return g


def test_default_mode_is_sampled_and_bad_mode_is_rejected():
    assert get_collision_mode() == "sampled"
    with pytest.raises(ValueError):
        set_collision_mode("fuzzy")


def test_exact_blocks_a_segment_through_an_obstacle_and_allows_a_free_one():
    set_collision_mode("exact")
    g = _grid_with((5, 5))
    assert not line_collision_free((2, 5), (8, 5), g)
    assert line_collision_free((2, 2), (8, 2), g)


def test_exact_allows_touching_an_edge_or_a_corner():
    set_collision_mode("exact")
    g = _grid_with((5, 5))
    assert line_collision_free((2, 4.5), (8, 4.5), g)          # runs along the bottom edge
    assert line_collision_free((4.5, 2), (4.5, 8), g)          # runs along the left edge
    assert line_collision_free((4, 4), (6, 4), g)              # row below, away from it


def test_exact_catches_a_corner_cut_that_sampling_misses():
    g = _grid_with((5, 5))
    p1, p2 = (3.71, 7.95), (7.34, 2.98)   # clips the obstacle square's corner between two samples
    set_collision_mode("sampled")
    assert line_collision_free(p1, p2, g)      # the leak this mode exists to remove
    set_collision_mode("exact")
    assert not line_collision_free(p1, p2, g)


def test_exact_rejects_points_outside_the_grid():
    set_collision_mode("exact")
    g = np.zeros((10, 10), dtype=np.uint8)
    assert not line_collision_free((-1, 2), (4, 2), g)
    assert not line_collision_free((2, 2), (4, 11), g)
    assert line_collision_free((0, 0), (9, 9), g)


def test_exact_and_sampled_agree_on_clear_and_blocked_grid_aligned_moves():
    g = _grid_with((3, 3), (6, 7))
    rng = random.Random(1)
    for _ in range(300):
        a = (rng.randint(0, 9), rng.randint(0, 9))
        b = (a[0] + rng.choice([-1, 0, 1]), a[1] + rng.choice([-1, 0, 1]))
        if not (0 <= b[0] < 10 and 0 <= b[1] < 10):
            continue
        set_collision_mode("sampled")
        s = line_collision_free(a, b, g)
        set_collision_mode("exact")
        e = line_collision_free(a, b, g)
        if g[a[1], a[0]] == 0 and g[b[1], b[0]] == 0:
            assert s == e


@pytest.mark.parametrize("name", ["astar_smooth", "theta_star_tight", "hybrid_fallback", "hybrid_tight"])
def test_planners_return_exactly_valid_paths_under_exact_mode(name):
    set_collision_mode("exact")
    grid, start, goal = make_map("random", 30, 2, {"density": 0.20})
    spec = f"{name}:max_iterations=1200" if name.startswith("hybrid") else name
    random.seed(0)
    path = make_planner(spec).plan(start, goal, grid)
    assert path is not None and path_is_valid(path, grid, start, goal)
    for a, b in zip(path[:-1], path[1:]):
        assert utils._segment_free_exact(a, b, grid)


def test_runner_config_key_sets_the_mode():
    from benchmarks.runner import _init_worker
    _init_worker({"collision": "exact", "scenarios": [], "planners": []})
    assert get_collision_mode() == "exact"
    _init_worker({"scenarios": [], "planners": []})
    assert get_collision_mode() == "sampled"


def test_margin_validation():
    with pytest.raises(ValueError):
        set_collision_mode("exact", margin=0.5)
    with pytest.raises(ValueError):
        set_collision_mode("exact", margin=-0.1)
    with pytest.raises(ValueError):
        set_collision_mode("sampled", margin=0.05)
    set_collision_mode("exact", margin=0.05)
    assert get_collision_margin() == 0.05
    set_collision_mode("sampled")
    assert get_collision_margin() == 0.0


def test_margin_makes_touching_a_collision_but_clear_passes_stay_free():
    g = _grid_with((5, 5))
    set_collision_mode("exact", margin=0.0)
    assert line_collision_free((2, 4.5), (8, 4.5), g)          # along the edge: touching is allowed
    set_collision_mode("exact", margin=0.05)
    assert not line_collision_free((2, 4.5), (8, 4.5), g)      # touching now collides
    assert not line_collision_free((2, 4.47), (8, 4.47), g)    # 0.03 from the edge, inside the margin
    assert line_collision_free((2, 4.4), (8, 4.4), g)          # 0.1 from the edge, clear
    assert line_collision_free((2, 2), (8, 2), g)


def test_margin_closes_a_zero_width_diagonal_squeeze():
    g = _grid_with((4, 4), (5, 5))                             # touch only at the point (4.5, 4.5)
    set_collision_mode("exact", margin=0.0)
    assert line_collision_free((4, 5), (5, 4), g)              # squeezes through the touching point
    set_collision_mode("exact", margin=0.05)
    assert not line_collision_free((4, 5), (5, 4), g)


def test_margin_keeps_the_path_off_the_map_border():
    set_collision_mode("exact", margin=0.05)
    g = np.zeros((10, 10), dtype=np.uint8)
    assert line_collision_free((0, 0), (9, 0), g)              # cell centres are 0.5 from the border
    assert not line_collision_free((-0.48, 2), (4, 2), g)


def test_astar_avoids_squeezes_only_when_a_margin_is_set():
    # 2x2 pocket with obstacles on the anti-diagonal: the only way (0,0)->(1,1) is the diagonal squeeze.
    h = np.zeros((2, 2), dtype=np.uint8)
    h[0, 1] = h[1, 0] = 1
    set_collision_mode("exact", margin=0.0)
    assert astar(h, (0, 0), (1, 1)) is not None
    set_collision_mode("exact", margin=0.05)
    assert astar(h, (0, 0), (1, 1)) is None


@pytest.mark.parametrize("name", ["astar_smooth", "theta_star_cc", "theta_star_tight", "hybrid_fallback",
                                  "hybrid_tight", "vis_graph"])
def test_planners_return_valid_paths_with_a_margin(name):
    set_collision_mode("exact", margin=0.05)
    grid, start, goal = make_map("random", 30, 2, {"density": 0.20})
    spec = {"theta_star_cc": "theta_star:corner_guard=0"}.get(name, name)
    if name.startswith("hybrid"):
        spec = f"{name}:max_iterations=1500"
    random.seed(0)
    path = make_planner(spec).plan(start, goal, grid)
    assert path is not None and path_is_valid(path, grid, start, goal)
