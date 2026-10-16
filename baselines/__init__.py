"""Baseline planners used in the paper comparison.

Every planner follows the same interface as ``planner_core.HybridAStar``:
``plan(start, goal, grid) -> list[(x, y)] | None`` with ``grid[y, x] == 1``
meaning obstacle.
"""
