import random

import numpy as np

from planner_core import HybridAStar, KalmanFilter, RRTStar
from planner_core.utils import astar, line_collision_free, make_grid, path_length, set_start_goal_free


def empty_grid(n=30):
    return np.zeros((n, n), dtype=np.uint8)


def test_astar_straight_line_on_empty_grid():
    path = astar(empty_grid(), (1, 1), (20, 1))
    assert path[0] == (1, 1) and path[-1] == (20, 1)
    assert abs(path_length(path) - 19) < 1e-9


def test_astar_returns_none_when_blocked():
    grid = empty_grid()
    grid[:, 10] = 1
    assert astar(grid, (1, 1), (20, 1)) is None


def test_rrt_star_and_hybrid_find_collision_free_paths():
    grid = make_grid(30, 0.15, seed=3)
    start, goal = (2, 2), (27, 27)
    set_start_goal_free(grid, start, goal)
    for planner in (RRTStar(max_iterations=900), HybridAStar(max_iterations=900)):
        random.seed(1)
        path = planner.plan(start, goal, grid)
        assert path is not None
        assert path[0] == start and path[-1] == goal
        assert all(line_collision_free(path[i], path[i + 1], grid) for i in range(len(path) - 1))


def test_hybrid_is_deterministic_under_a_seed():
    grid = make_grid(30, 0.15, seed=5)
    start, goal = (2, 2), (27, 27)
    set_start_goal_free(grid, start, goal)
    runs = []
    for _ in range(2):
        random.seed(7)
        runs.append(HybridAStar(max_iterations=600).plan(start, goal, grid))
    assert runs[0] == runs[1]


def test_hybrid_returns_none_if_no_route():
    grid = empty_grid()
    grid[:, 10] = 1
    assert HybridAStar(max_iterations=50).plan((1, 1), (20, 1), grid) is None


def test_kalman_filter_reduces_noise_on_constant_velocity_track():
    rng = np.random.default_rng(0)
    kf = KalmanFilter(dt=0.1, process_noise=0.01, measurement_noise=0.25)
    raw_err, kf_err = [], []
    for k in range(200):
        truth = np.array([0.5 * 0.1 * k, 0.2 * 0.1 * k])
        meas = truth + rng.normal(0, 0.5, 2)
        kf.predict()
        est = kf.update(meas)[:2]
        if k > 20:
            raw_err.append(np.linalg.norm(meas - truth))
            kf_err.append(np.linalg.norm(est - truth))
    assert np.sqrt(np.mean(np.square(kf_err))) < np.sqrt(np.mean(np.square(raw_err)))
