"""The ROS2 package still carries its own copy of the core files.

Until the nodes import ``planner_core`` directly, this test makes sure the two
copies do not drift apart.
"""
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROS = os.path.join(ROOT, "ros2_integration", "planner_nodes", "planner_nodes")


@pytest.mark.parametrize("name", ["utils", "hybrid_astar", "rrt_star", "kalman_filter"])
def test_ros2_copy_matches_planner_core(name):
    with open(os.path.join(ROOT, "planner_core", f"{name}.py")) as a, \
            open(os.path.join(ROS, f"{name}.py")) as b:
        assert a.read() == b.read()
