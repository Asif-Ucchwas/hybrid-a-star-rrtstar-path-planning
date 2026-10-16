"""Exact shortest path through obstacle corners (a visibility graph), as a reference.

Why this exists: Theta*, tightened A*/Theta* and the hybrid planner all produce
paths that are *close to* the shortest path. To say how close, we need the
shortest path itself. In free space with polygonal obstacles the shortest path
is a polyline whose bends sit on obstacle corners, so it is the shortest path in
the visibility graph of those corners.

Obstacle cell (x, y) is the unit square centred on (x, y). Each convex corner is
pushed ``eps`` (default 0.001 cell) outward along the diagonal, so the vertex lies
inside the neighbouring free cell. Edges use the same collision test as every
other planner (``planner_core.utils.line_collision_free``). Consequences:

* Use it with ``set_collision_mode("exact")`` (config key ``"collision": "exact"``).
  Then it is the shortest path that keeps at least ``eps`` away from every obstacle
  corner, and no other valid path is shorter by more than about ``eps`` per bend.
* Under the default ``"sampled"`` rule other planners can clip corners between
  collision samples and come out up to ~1.5% shorter than this path, so it is
  not a lower bound there.
* Shortest is not the same as smoothest. This planner is a reference for length
  (and a fair look at how much turning an exactly shortest path has).

The search is A* with lazy edge checks, restricted to vertices inside the
ellipse whose total length is at most an upper bound taken from a tightened
Theta* path (and rerun without the bound if that finds nothing). It is meant for
maps up to about 100x100; on 200x200 maps with many obstacles it is slow.
"""

import heapq
import math

import numpy as np

from baselines.astar_family import ThetaStar
from baselines.smoothing import tighten_path
from planner_core.utils import get_collision_margin, line_collision_free, path_length


def corner_points(grid, eps=0.001):
    """Vertices of the visibility graph: pushed-out convex obstacle corners in free cells,
    plus the squeeze points between diagonally touching obstacles, as an (n, 2) array."""
    n = grid.shape[0]
    ys, xs = np.nonzero(grid)
    off = 0.5 + eps
    pts = set()
    for sx in (-1, 1):
        for sy in (-1, 1):
            ix, iy = xs + sx, ys + sy                 # diagonal neighbour cell
            ok = (ix >= 0) & (iy >= 0) & (ix < n) & (iy < n)
            ix, iy, x0, y0 = ix[ok], iy[ok], xs[ok], ys[ok]
            ok = grid[iy, ix] == 0                    # the pushed point lands in a free cell
            ix, iy, x0, y0 = ix[ok], iy[ok], x0[ok], y0[ok]
            # skip concave pockets: both orthogonal neighbours are obstacles
            ok = ~((grid[y0, ix] == 1) & (grid[iy, x0] == 1))
            for x, y in zip(x0[ok].tolist(), y0[ok].tolist()):
                px, py = x + sx * off, y + sy * off
                if 0.0 <= px <= n - 1 and 0.0 <= py <= n - 1:
                    pts.add((round(px, 6), round(py, 6)))
    # Squeeze points: two obstacle cells touching only at a corner leave a zero-width
    # gap. A* and the exact collision rule both allow passing through it, so the
    # touching point itself is a vertex (exactly, no push-out).
    if get_collision_margin() > 0.0:      # with a margin the gap is closed: no squeeze points
        return np.array(sorted(pts), dtype=float).reshape(-1, 2)
    a, b = grid[:-1, :-1], grid[:-1, 1:]
    c, d = grid[1:, :-1], grid[1:, 1:]
    diag = ((a == 1) & (d == 1) & (b == 0) & (c == 0)) | ((b == 1) & (c == 1) & (a == 0) & (d == 0))
    for y, x in zip(*np.nonzero(diag)):
        pts.add((float(x) + 0.5, float(y) + 0.5))
    return np.array(sorted(pts), dtype=float).reshape(-1, 2)


class VisGraphShortest:
    """Shortest path in the visibility graph of obstacle corners (see module docstring)."""

    def __init__(self, eps=None, bound_slack=0.01):
        # default: just outside the margin-inflated corner
        self.eps = None if eps is None else float(eps)
        self.bound_slack = float(bound_slack)
        self.last_info = {}

    def plan(self, start, goal, grid):
        start, goal = tuple(start), tuple(goal)
        self.last_info = {}
        if line_collision_free(start, goal, grid):
            return [start, goal]
        seed = ThetaStar(corner_guard=0).plan(start, goal, grid)
        if seed is None:
            return None
        ub = path_length(tighten_path(seed, grid)) * (1.0 + self.bound_slack) + 0.5
        eps = self.eps if self.eps is not None else get_collision_margin() + 0.001
        corners = corner_points(grid, eps)
        path = self._search(start, goal, grid, corners, ub)
        if path is None:                      # bound was too tight: search without it
            path = self._search(start, goal, grid, corners, float("inf"))
            self.last_info["unbounded"] = True
        return path

    @staticmethod
    def _search(start, goal, grid, corners, ub):
        pts = np.vstack([np.array([start, goal], dtype=float), corners])
        d_start = np.hypot(pts[:, 0] - start[0], pts[:, 1] - start[1])
        d_goal = np.hypot(pts[:, 0] - goal[0], pts[:, 1] - goal[1])
        keep = np.flatnonzero(d_start + d_goal <= ub)
        keep = np.union1d(keep, [0, 1])
        P = pts[keep]
        h = d_goal[keep]
        m = len(P)
        s_idx, g_idx = 0, 1                    # start and goal sort first in `keep`
        closed = np.zeros(m, dtype=bool)
        parent = [-1] * m
        g_val = [math.inf] * m
        heap = [(h[s_idx], 0.0, s_idx, -1)]
        while heap:
            _, g, v, u = heapq.heappop(heap)
            if closed[v]:
                continue
            if u >= 0 and not line_collision_free(tuple(P[u]), tuple(P[v]), grid):
                continue                       # lazy edge check failed
            closed[v] = True
            parent[v] = u
            g_val[v] = g
            if v == g_idx:
                out = []
                while v != -1:
                    out.append(tuple(P[v]))
                    v = parent[v]
                out.reverse()
                out[0], out[-1] = start, goal
                return out
            dist = np.hypot(P[:, 0] - P[v, 0], P[:, 1] - P[v, 1])
            f = g + dist + h
            cand = np.flatnonzero(~closed & (f <= ub))
            for w in cand.tolist():
                heapq.heappush(heap, (float(f[w]), g + float(dist[w]), w, v))
        return None
