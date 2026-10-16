"""Path quality metrics: length, smoothness (turning), clearance, validity."""

import math

import numpy as np
from scipy.ndimage import distance_transform_edt

from planner_core.utils import line_collision_free, path_length


def path_is_valid(path, grid, start, goal, tol=1e-6):
    """True if the path starts at start, ends at goal and never touches an obstacle."""
    if path is None or len(path) < 2:
        return False
    if math.hypot(path[0][0] - start[0], path[0][1] - start[1]) > tol:
        return False
    if math.hypot(path[-1][0] - goal[0], path[-1][1] - goal[1]) > tol:
        return False
    return all(line_collision_free(path[i], path[i + 1], grid)
               for i in range(len(path) - 1))


def turning_angles(path):
    """Absolute heading change (radians) at each interior waypoint."""
    angles = []
    for i in range(1, len(path) - 1):
        ax, ay = path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]
        bx, by = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        if math.hypot(ax, ay) < 1e-12 or math.hypot(bx, by) < 1e-12:
            continue
        cross = ax * by - ay * bx
        dot = ax * bx + ay * by
        angles.append(abs(math.atan2(cross, dot)))
    return angles


def clearance_map(grid):
    """Distance (in cells) from every cell to the nearest obstacle cell."""
    return distance_transform_edt(grid == 0)


def path_clearance(path, cmap, step=0.1):
    """(min, mean) obstacle distance sampled every ``step`` cells along the path.

    A minimum of 0 means a sample point lies inside an obstacle cell, i.e. the
    path clips a corner that the planner's coarser collision check (one sample
    every 1/3 cell) did not see.
    """
    n = cmap.shape[0]
    vals = []
    for i in range(len(path) - 1):
        p, q = path[i], path[i + 1]
        steps = max(int(math.hypot(q[0] - p[0], q[1] - p[1]) / step), 1)
        for t in np.linspace(0.0, 1.0, steps + 1):
            x = p[0] + t * (q[0] - p[0])
            y = p[1] + t * (q[1] - p[1])
            xi = min(max(int(round(x)), 0), n - 1)
            yi = min(max(int(round(y)), 0), n - 1)
            vals.append(cmap[yi, xi])
    if not vals:
        return float("nan"), float("nan")
    return float(np.min(vals)), float(np.mean(vals))


def evaluate_path(path, grid, cmap=None):
    """All quality metrics for a (valid) path."""
    if cmap is None:
        cmap = clearance_map(grid)
    ang = turning_angles(path)
    cmin, cmean = path_clearance(path, cmap)
    return {
        "length": path_length(path),
        "turn_total_deg": math.degrees(sum(ang)),
        "turn_mean_deg": math.degrees(sum(ang) / len(ang)) if ang else 0.0,
        "clearance_min": cmin,
        "clearance_mean": cmean,
        "strict_valid": int(cmin > 0),
        "n_waypoints": len(path),
    }
