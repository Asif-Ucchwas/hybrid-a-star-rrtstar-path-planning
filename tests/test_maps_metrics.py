import numpy as np
import pytest

from benchmarks.maps import make_map
from benchmarks.metrics import clearance_map, evaluate_path, path_is_valid, turning_angles
from planner_core.utils import astar


@pytest.mark.parametrize("kind,params", [("random", {"density": 0.3}), ("narrow", {}), ("maze", {})])
def test_maps_are_deterministic_and_solvable(kind, params):
    for seed in range(10):
        g1, s, t = make_map(kind, 50, seed, params)
        g2, _, _ = make_map(kind, 50, seed, params)
        assert np.array_equal(g1, g2)
        assert g1[s[1], s[0]] == 0 and g1[t[1], t[0]] == 0
        assert astar(g1, s, t) is not None


def test_different_seeds_give_different_maps():
    a, _, _ = make_map("random", 50, 0, {"density": 0.2})
    b, _, _ = make_map("random", 50, 1, {"density": 0.2})
    assert not np.array_equal(a, b)


def test_turning_angles_straight_and_right_angle():
    assert turning_angles([(0, 0), (1, 0), (2, 0)]) == [0.0]
    ang = turning_angles([(0, 0), (1, 0), (1, 1)])
    assert abs(ang[0] - np.pi / 2) < 1e-9


def test_path_validity_checks_endpoints_and_collisions():
    grid = np.zeros((20, 20), dtype=np.uint8)
    grid[5, 10] = 1
    assert path_is_valid([(1, 1), (18, 1)], grid, (1, 1), (18, 1))
    assert not path_is_valid([(1, 5), (18, 5)], grid, (1, 5), (18, 5))   # crosses obstacle
    assert not path_is_valid([(2, 1), (18, 1)], grid, (1, 1), (18, 1))   # wrong start
    assert not path_is_valid(None, grid, (1, 1), (18, 1))


def test_clearance_and_length_metrics():
    grid = np.zeros((20, 20), dtype=np.uint8)
    grid[10, :] = 1
    m = evaluate_path([(1, 8), (18, 8)], grid, clearance_map(grid))
    assert abs(m["length"] - 17) < 1e-9
    assert abs(m["clearance_min"] - 2) < 1e-9
    assert m["strict_valid"] == 1
