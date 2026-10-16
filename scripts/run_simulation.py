# Run Hybrid A*-RRT* Simulation
# Author: Md Asifuzzaman
# Thesis: Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile Robots
#         Using Sampling-Based and Graph-Based Algorithms
#
# Usage: python scripts/run_simulation.py

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.hybrid_astar import HybridAStar  # noqa: E402
from src.rrt_star import RRTStar  # noqa: E402
from src.kalman_filter import KalmanFilter  # noqa: E402

if __name__ == '__main__':
    print("Hybrid A*-RRT* Planner — Lamar University MES Thesis")
    print("ROS2/Gazebo integration coming soon")
