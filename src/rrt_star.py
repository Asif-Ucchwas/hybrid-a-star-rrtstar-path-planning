# RRT* Path Planning Algorithm (standard, uniform sampling)
# Author: Md Asifuzzaman
# Thesis: Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile Robots
#         Using Sampling-Based and Graph-Based Algorithms
# Lamar University, MES EEE, May 2026
#
# Used as baseline comparison in thesis experiments

try:
    from .utils import rrt_star_generic, sample_uniform_free, path_length
except ImportError:
    from utils import rrt_star_generic, sample_uniform_free, path_length


class RRTStar:
    def __init__(self, max_iterations=1800, step_size=2.0, neighbor_radius=3.5,
                 goal_threshold=2.0, max_nodes=2500, goal_sample_rate=0.10):
        self.max_iterations = max_iterations
        self.step_size = step_size
        self.neighbor_radius = neighbor_radius
        self.goal_threshold = goal_threshold
        self.max_nodes = max_nodes
        self.goal_sample_rate = goal_sample_rate

    def plan(self, start, goal, obstacle_map):
        """
        Plan a path using standard RRT* (uniform sampling across free space).
        obstacle_map: 2D numpy array, 0 = free, 1 = obstacle.
        Returns: list of (x, y) waypoints, or None if no path found.
        """
        path, nodes = rrt_star_generic(
            grid=obstacle_map,
            start=start,
            goal=goal,
            sampler_fn=sample_uniform_free,
            sampler_args={
                "grid": obstacle_map,
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
