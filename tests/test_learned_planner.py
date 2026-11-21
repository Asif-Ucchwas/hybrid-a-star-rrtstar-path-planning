"""Tests for the learned planners (skipped when PyTorch or the model file is missing, e.g. in CI)."""

import os
import random

import numpy as np
import pytest

torch = pytest.importorskip("torch", reason="optional: needs PyTorch (see ml/)")

from benchmarks.maps import make_map  # noqa: E402
from benchmarks.metrics import path_is_valid  # noqa: E402
from benchmarks.planners import make_planner  # noqa: E402
from ml.learned_planner import DEFAULT_MODEL, sample_from_heatmap  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(DEFAULT_MODEL), reason="no trained model file")


@pytest.mark.parametrize("name", ["learned_corridor", "learned_tight"])
def test_learned_planner_returns_valid_path(name):
    grid, start, goal = make_map("random", 50, 3, {"density": 0.20})
    random.seed(0)
    planner = make_planner(name)
    path = planner.plan(start, goal, grid)
    assert path is not None
    assert path_is_valid(path, grid, start, goal)
    assert planner.heatmap.shape == grid.shape
    assert planner.last_info["infer_s"] >= 0.0


@pytest.mark.parametrize("name", ["learned_corridor", "learned_tight"])
def test_learned_planner_returns_none_when_no_route(name):
    grid, start, goal = make_map("random", 30, 2, {"density": 0.0})
    grid[:, 15] = 1
    random.seed(0)
    assert make_planner(f"{name}:max_iterations=100").plan(start, goal, grid) is None


def test_learned_planner_reports_fallback():
    grid, start, goal = make_map("random", 30, 2, {"density": 0.0})
    planner = make_planner("learned_corridor:max_iterations=1")
    random.seed(0)
    path = planner.plan(start, goal, grid)
    assert path is not None and path_is_valid(path, grid, start, goal)
    assert planner.last_info.get("fallback") is True


def test_model_runs_on_a_bigger_map_than_it_was_trained_on():
    grid, start, goal = make_map("random", 100, 1, {"density": 0.15})
    random.seed(0)
    planner = make_planner("learned_tight")
    path = planner.plan(start, goal, grid)
    assert planner.heatmap.shape == (100, 100)
    assert path is not None and path_is_valid(path, grid, start, goal)


def test_heatmap_sampler_only_returns_points_in_the_map():
    grid = np.zeros((10, 10), dtype=np.uint8)
    cells = np.array([[0, 0], [9, 9], [4, 5]])
    cdf = np.cumsum([1.0, 1.0, 2.0])
    random.seed(1)
    for _ in range(500):
        x, y = sample_from_heatmap(grid, cdf, cells, goal=(9, 9), uniform_mix=0.2)
        assert 0.0 <= x <= 9.0 and 0.0 <= y <= 9.0
