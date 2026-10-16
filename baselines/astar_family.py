"""Graph-search baselines: A* with smoothing, Theta*, and tightened variants."""

import heapq

from baselines.smoothing import tighten_path
from planner_core.utils import (
    astar,
    euclidean,
    get_collision_margin,
    in_bounds,
    line_collision_free,
    shortcut_path,
)


class AStarSmooth:
    """A* followed by the same random-shortcut smoothing RRT* paths get.

    This is the fair comparison against RRT*-based planners, whose paths are
    always shortcut-smoothed inside ``rrt_star_generic``.
    """

    def __init__(self, smoothing_attempts=150):
        self.smoothing_attempts = smoothing_attempts

    def plan(self, start, goal, grid):
        path = astar(grid, start, goal)
        if path is None:
            return None
        return shortcut_path(path, grid, attempts=self.smoothing_attempts)


class ThetaStar:
    """Basic Theta* (Daniel et al., 2010): any-angle A* with line-of-sight parents.

    ``corner_guard=1`` (default) refuses a diagonal step between two diagonal
    obstacle cells. The repo's A* does not refuse it, so for a like-for-like
    comparison with A* use ``theta_star:corner_guard=0``.
    """

    def __init__(self, corner_guard=1):
        self.corner_guard = bool(int(corner_guard))

    def plan(self, start, goal, grid):
        n = grid.shape[0]
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1),
                 (-1, -1), (-1, 1), (1, -1), (1, 1)]
        start = tuple(start)
        goal = tuple(goal)

        strict = get_collision_margin() > 0.0   # with a margin, a diagonal needs both side cells free
        g = {start: 0.0}
        parent = {start: start}
        open_heap = [(euclidean(start, goal), start)]
        closed = set()

        while open_heap:
            _, s = heapq.heappop(open_heap)
            if s in closed:
                continue
            if s == goal:
                path = [s]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                path.reverse()
                return path
            closed.add(s)

            for dx, dy in moves:
                nb = (s[0] + dx, s[1] + dy)
                if not in_bounds(nb, n) or grid[nb[1], nb[0]] == 1 or nb in closed:
                    continue
                # Prevent cutting corners between two diagonal obstacles.
                if dx != 0 and dy != 0:
                    side_x, side_y = grid[s[1], s[0] + dx] == 1, grid[s[1] + dy, s[0]] == 1
                    if (strict and (side_x or side_y)) or (self.corner_guard and side_x and side_y):
                        continue
                p = parent[s]
                if line_collision_free(p, nb, grid):
                    cand_parent = p
                    cand_g = g[p] + euclidean(p, nb)
                else:
                    cand_parent = s
                    cand_g = g[s] + euclidean(s, nb)
                if cand_g < g.get(nb, float("inf")):
                    g[nb] = cand_g
                    parent[nb] = cand_parent
                    heapq.heappush(open_heap, (cand_g + euclidean(nb, goal), nb))
        return None


class ThetaStarSmooth:
    """Theta* followed by the same random shortcut smoothing RRT* paths get.

    Uses the A*-equivalent movement rules (``corner_guard=0``) so it is the
    like-for-like partner of ``astar_smooth``.
    """

    def __init__(self, corner_guard=0, smoothing_attempts=150):
        self.theta = ThetaStar(corner_guard=corner_guard)
        self.smoothing_attempts = smoothing_attempts

    def plan(self, start, goal, grid):
        path = self.theta.plan(start, goal, grid)
        if path is None:
            return None
        return shortcut_path(path, grid, attempts=self.smoothing_attempts)


class AStarTight:
    """A* followed by deterministic path tightening (prune + relax until taut)."""

    def plan(self, start, goal, grid):
        path = astar(grid, start, goal)
        if path is None:
            return None
        return tighten_path(path, grid)


class ThetaStarTight:
    """Theta* (A*-equivalent movement rules) followed by deterministic tightening."""

    def __init__(self, corner_guard=0):
        self.theta = ThetaStar(corner_guard=corner_guard)

    def plan(self, start, goal, grid):
        path = self.theta.plan(start, goal, grid)
        if path is None:
            return None
        return tighten_path(path, grid)
