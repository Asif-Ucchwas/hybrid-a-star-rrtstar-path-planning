"""Reference-library baselines: RRT*, Informed RRT*, RRT-Connect and BIT* from OMPL.

Purpose: show that our own compact sampling baselines behave like the
reference implementations a reviewer would expect. OMPL is optional
(``pip install ompl``); nothing else in the repo imports this module.

Fair-comparison rules
- Same grid convention: ``grid[y, x] == 1`` is an obstacle, points are ``(x, y)``.
- Same collision rule as ``planner_core`` (a point is free if its rounded cell is
  free), made slightly conservative: a state is valid only if the point and its
  four neighbours 0.15 cell away are free, and motions are checked every 0.1
  cell. The benchmark's own validity check samples segments at other points, so
  without this margin OMPL would lose runs to a checker mismatch, not to the
  algorithm.
- Optimising planners (RRT*, Informed RRT*, BIT*) run for ``time_limit``
  seconds; RRT-Connect stops at its first solution.
- The result gets the same random-shortcut smoothing (150 attempts) as every
  other sampling planner in the benchmark.

Known limit: OMPL seeds one global random generator per process and refuses a
second seed, so OMPL runs are not reproducible run by run. Maps and all other
planners stay seeded; use enough trials that this does not matter.
"""

import math

from planner_core.utils import shortcut_path

KINDS = {
    "ompl_rrt_star": "RRTstar",
    "ompl_informed_rrt_star": "InformedRRTstar",
    "ompl_rrt_connect": "RRTConnect",
    "ompl_bit_star": "BITstar",
}


def ompl_available():
    try:
        import ompl  # noqa: F401
        return True
    except ImportError:
        return False


class OMPLPlanner:
    """One OMPL planner behind the repo's ``plan(start, goal, grid)`` interface."""

    def __init__(self, kind="RRTstar", time_limit=1.0, range_cells=2.0, smooth_attempts=150,
                 check_step=0.1, margin=0.15):
        self.kind = kind
        self.time_limit = time_limit
        self.range_cells = range_cells
        self.smooth_attempts = smooth_attempts
        self.margin = margin  # state must stay this far (cells) from obstacle cell borders
        self.check_step = check_step  # cells between collision checks (finer than the 1/3 used elsewhere)
        self.last_info = {}

    def plan(self, start, goal, grid):
        from ompl import base as ob
        from ompl import geometric as og
        from ompl import util as ou

        ou.setLogLevel(ou.LOG_ERROR)
        size = grid.shape[0]
        hi = size - 1

        space = ob.RealVectorStateSpace(2)
        bounds = ob.RealVectorBounds(2)
        bounds.setLow(0.0)
        bounds.setHigh(float(hi))
        space.setBounds(bounds)

        ss = og.SimpleSetup(space)

        margin = self.margin

        def free(x, y):
            xi, yi = int(round(x)), int(round(y))
            return 0 <= xi < size and 0 <= yi < size and grid[yi, xi] == 0

        def valid(state):
            x, y = state[0], state[1]
            return bool(free(x, y) and free(x - margin, y - margin) and free(x + margin, y - margin)
                        and free(x - margin, y + margin) and free(x + margin, y + margin))

        ss.setStateValidityChecker(valid)
        si = ss.getSpaceInformation()
        si.setStateValidityCheckingResolution(self.check_step / (math.sqrt(2.0) * hi))

        s = space.allocState()
        s[0], s[1] = float(start[0]), float(start[1])
        g = space.allocState()
        g[0], g[1] = float(goal[0]), float(goal[1])
        ss.setStartAndGoalStates(s, g, 0.01)

        objective = ob.PathLengthOptimizationObjective(si)
        ss.setOptimizationObjective(objective)

        planner = getattr(og, self.kind)(si)
        if hasattr(planner, "setRange"):
            planner.setRange(self.range_cells)
        ss.setPlanner(planner)

        solved = ss.solve(float(self.time_limit))
        has_exact = bool(solved) and solved.asString() == "Exact solution"
        nodes = 0
        try:
            pd = ob.PlannerData(si)
            ss.getPlannerData(pd)
            nodes = pd.numVertices()
        except Exception:
            pass
        self.last_info = {"nodes": nodes}
        if not has_exact:
            return None

        states = ss.getSolutionPath().getStates()
        path = [(float(p[0]), float(p[1])) for p in states]
        path[0] = (float(start[0]), float(start[1]))
        path[-1] = (float(goal[0]), float(goal[1]))
        return shortcut_path(path, grid, attempts=self.smooth_attempts)


def make_ompl(name, **kwargs):
    if name not in KINDS:
        raise ValueError(f"unknown OMPL planner {name!r}; choose from {sorted(KINDS)}")
    if not ompl_available():
        raise ImportError("OMPL planners need the optional package: pip install ompl")
    kwargs.setdefault("time_limit", 1.0)
    return OMPLPlanner(kind=KINDS[name], **kwargs)
