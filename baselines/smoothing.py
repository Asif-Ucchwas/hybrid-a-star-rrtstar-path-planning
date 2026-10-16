"""Deterministic path tightening, used as a stronger smoothing baseline.

The repo's standard smoother (``planner_core.utils.shortcut_path``) makes a fixed
number of random shortcut attempts. ``tighten_path`` is the strong version of the
same idea: it needs no random numbers and keeps going until nothing improves.

1. *Prune*: from each waypoint jump to the farthest waypoint it can see.
2. *Relax*: slide every interior waypoint toward the straight line between its
   two neighbours, keeping both new segments collision-free. Each accepted move
   shortens the path, so the loop converges to a locally taut path.
3. Repeat 1-2 until the waypoint count stops changing.

It uses the same collision check as every other planner
(``planner_core.utils.line_collision_free``), so the result is valid under the
benchmark's own rules. Like any taut path it hugs obstacle corners, so expect
lower clearance than the input path.
"""

import math

from planner_core.utils import line_collision_free


def prune_visible(path, grid):
    """Keep only waypoints needed so each hop is the farthest one in line of sight."""
    n = len(path)
    out = [path[0]]
    i = 0
    while i < n - 1:
        j = n - 1
        while j > i + 1 and not line_collision_free(path[i], path[j], grid):
            j -= 1
        out.append(path[j])
        i = j
    return out


def _closest_on_segment(p, a, b):
    abx, aby = b[0] - a[0], b[1] - a[1]
    denom = abx * abx + aby * aby
    if denom < 1e-18:
        return a
    t = ((p[0] - a[0]) * abx + (p[1] - a[1]) * aby) / denom
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return (a[0] + t * abx, a[1] + t * aby)


def relax_vertices(path, grid, sweeps=60, tol=1e-3):
    """Slide interior waypoints toward their neighbours' chord while staying collision-free."""
    pts = [(float(x), float(y)) for x, y in path]
    for _ in range(sweeps):
        moved = 0.0
        for k in range(1, len(pts) - 1):
            a, v, b = pts[k - 1], pts[k], pts[k + 1]
            tgt = _closest_on_segment(v, a, b)
            for frac in (1.0, 0.5, 0.25, 0.125):
                c = (v[0] + frac * (tgt[0] - v[0]), v[1] + frac * (tgt[1] - v[1]))
                if line_collision_free(a, c, grid) and line_collision_free(c, b, grid):
                    moved += math.hypot(c[0] - v[0], c[1] - v[1])
                    pts[k] = c
                    break
        if moved < tol:
            break
    return pts


def tighten_path(path, grid, rounds=6):
    """Prune and relax until the waypoint count stops changing. Endpoints are kept exactly."""
    if path is None or len(path) < 3:
        return path
    pts = prune_visible(list(path), grid)
    for _ in range(rounds):
        before = len(pts)
        if before < 3:
            break
        pts = prune_visible(relax_vertices(pts, grid), grid)
        if len(pts) == before:
            pts = relax_vertices(pts, grid)
            break
    pts[0] = tuple(path[0])
    pts[-1] = tuple(path[-1])
    return pts
