# Hybrid A* Path Planning Algorithm
# Author: Md Asifuzzaman
# Thesis: Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile Robots
#         Using Sampling-Based and Graph-Based Algorithms
# Lamar University, MES EEE, May 2026
#
# Results: 5.87% path-length improvement over RRT*
#          98% success rate vs 60% for RRT* across 50 trials
#          Tested at obstacle densities: 0.10, 0.20, 0.30
#
# Method: run A* to get a global reference path, build an adaptive-width
# corridor around it (width driven by local obstacle density), then run
# RRT* with sampling restricted to that corridor. This focuses RRT*'s
# search effort where it matters instead of the whole free space.

try:
    from .utils import (
        astar,
        build_adaptive_corridor,
        sample_from_corridor,
        rrt_star_generic,
        path_length,
    )
except ImportError:
    # allows running as a standalone script (e.g. demo.py) as well as
    # as part of a package (e.g. a ROS2 node)
    from utils import (
        astar,
        build_adaptive_corridor,
        sample_from_corridor,
        rrt_star_generic,
        path_length,
    )


class HybridAStar:
    def __init__(self, base_width=2.0, max_extra=4.0, max_iterations=1800,
                 step_size=2.0, neighbor_radius=3.5, goal_threshold=2.0,
                 max_nodes=2500, goal_sample_rate=0.10):
        self.base_width = base_width
        self.max_extra = max_extra
        self.max_iterations = max_iterations
        self.step_size = step_size
        self.neighbor_radius = neighbor_radius
        self.goal_threshold = goal_threshold
        self.max_nodes = max_nodes
        self.goal_sample_rate = goal_sample_rate

    def plan(self, start, goal, obstacle_map):
        """
        Plan a path from start to goal avoiding obstacles, using the
        A*-guided adaptive corridor RRT* hybrid method.
        obstacle_map: 2D numpy array, 0 = free, 1 = obstacle.
        Returns: list of (x, y) waypoints, or None if no path found.
        """
        # Step 1: global reference path via A*
        a_path = astar(obstacle_map, start, goal)
        self.astar_path = a_path
        if a_path is None:
            return None

        # Step 2: adaptive corridor around the A* path
        corridor = build_adaptive_corridor(
            a_path, obstacle_map, base_width=self.base_width, max_extra=self.max_extra
        )
        self.corridor = corridor

        # Step 3: RRT* restricted to sampling from the corridor
        path, nodes = rrt_star_generic(
            grid=obstacle_map,
            start=start,
            goal=goal,
            sampler_fn=sample_from_corridor,
            sampler_args={
                "grid": obstacle_map,
                "corridor": corridor,
                "goal": goal,
                "goal_sample_rate": self.goal_sample_rate,
            },
            max_iterations=self.max_iterations,
            step_size=self.step_size,
            neighbor_radius=self.neighbor_radius,
            goal_threshold=self.goal_threshold,
            max_nodes=self.max_nodes,
        )
        self.last_nodes = nodes
        self.last_length = path_length(path) if path is not None else float("inf")
        return path
