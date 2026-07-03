"""
ROS2 node that ports the thesis A* planner into a live planning node.

Subscribes:
    /map        (nav_msgs/OccupancyGrid) - the environment map
    /goal_pose  (geometry_msgs/PoseStamped) - target pose (e.g. from RViz "2D Nav Goal")

Uses TF2 to get the robot's current pose (map -> base_link).

Publishes:
    /planned_path (nav_msgs/Path) - the planned path, viewable in RViz

Author: Md Asifuzzaman
Thesis: Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile
        Robots Using Sampling-Based and Graph-Based Algorithms
"""

import numpy as np
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from geometry_msgs.msg import PoseStamped
import tf2_ros
from tf2_ros import TransformException

from .utils import astar, path_length


class AStarPlannerNode(Node):
    def __init__(self):
        super().__init__('a_star_planner_node')

        # latest map, stored as a 2D numpy grid (0 = free, 1 = occupied)
        self.grid = None
        self.map_resolution = None
        self.map_origin_x = None
        self.map_origin_y = None

        # TF2 buffer/listener to look up the robot's current pose
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        map_qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)

        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, map_qos)

        self.goal_sub = self.create_subscription(
            PoseStamped, '/goal_pose', self.goal_callback, 10)

        self.path_pub = self.create_publisher(Path, '/planned_path', 10)

        self.get_logger().info('A* planner node started, waiting for /map and /goal_pose...')

    def map_callback(self, msg: OccupancyGrid):
        """Convert the incoming OccupancyGrid into the 0/1 grid format astar() expects."""
        width = msg.info.width
        height = msg.info.height
        data = np.array(msg.data, dtype=np.int16).reshape((height, width))

        # OccupancyGrid values: 0 = free, 1-100 = probability occupied, -1 = unknown.
        # Treat anything not confidently free (including unknown) as an obstacle,
        # for safety.
        grid = np.where(data <= 0, 0, 1).astype(np.uint8)
        grid[data == -1] = 1

        self.grid = grid
        self.map_resolution = msg.info.resolution
        self.map_origin_x = msg.info.origin.position.x
        self.map_origin_y = msg.info.origin.position.y

        self.get_logger().info(
            f'Map received: {width}x{height} cells, resolution={self.map_resolution:.3f} m/cell')

    def world_to_grid(self, wx, wy):
        """Convert world coordinates (meters) to grid cell (col, row)."""
        gx = int((wx - self.map_origin_x) / self.map_resolution)
        gy = int((wy - self.map_origin_y) / self.map_resolution)
        return (gx, gy)

    def grid_to_world(self, gx, gy):
        """Convert a grid cell (col, row) back to world coordinates (meters), cell center."""
        wx = self.map_origin_x + (gx + 0.5) * self.map_resolution
        wy = self.map_origin_y + (gy + 0.5) * self.map_resolution
        return (wx, wy)

    def get_robot_pose(self):
        """Look up the robot's current position in the map frame via TF2."""
        try:
            transform = self.tf_buffer.lookup_transform(
                'map', 'base_link', rclpy.time.Time())
            x = transform.transform.translation.x
            y = transform.transform.translation.y
            return (x, y)
        except TransformException as e:
            self.get_logger().warn(f'Could not get robot pose from TF2: {e}')
            return None

    def goal_callback(self, msg: PoseStamped):
        """Triggered when a new goal is published (e.g. RViz '2D Nav Goal')."""
        if self.grid is None:
            self.get_logger().warn('No map received yet, cannot plan.')
            return

        robot_pos = self.get_robot_pose()
        if robot_pos is None:
            self.get_logger().warn('No robot pose available, cannot plan.')
            return

        start_world = robot_pos
        goal_world = (msg.pose.position.x, msg.pose.position.y)

        start_cell = self.world_to_grid(*start_world)
        goal_cell = self.world_to_grid(*goal_world)

        self.get_logger().info(
            f'Planning from {start_cell} to {goal_cell} (grid cells)...')

        # Guard against out-of-bounds or occupied start/goal cells
        h, w = self.grid.shape
        if not (0 <= start_cell[0] < w and 0 <= start_cell[1] < h):
            self.get_logger().warn('Start cell is outside the map bounds.')
            return
        if not (0 <= goal_cell[0] < w and 0 <= goal_cell[1] < h):
            self.get_logger().warn('Goal cell is outside the map bounds.')
            return

        path_cells = astar(self.grid, start_cell, goal_cell)

        if path_cells is None:
            self.get_logger().warn('No path found!')
            return

        self.get_logger().info(
            f'Path found: {len(path_cells)} waypoints, '
            f'length={path_length(path_cells):.2f} cells')

        self.publish_path(path_cells)

    def publish_path(self, path_cells):
        """Convert the grid-cell path into a nav_msgs/Path and publish it."""
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()

        for (gx, gy) in path_cells:
            wx, wy = self.grid_to_world(gx, gy)
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = path_msg.header.stamp
            pose.pose.position.x = wx
            pose.pose.position.y = wy
            pose.pose.orientation.w = 1.0
            path_msg.poses.append(pose)

        self.path_pub.publish(path_msg)
        self.get_logger().info(f'Published path with {len(path_msg.poses)} poses to /planned_path')


def main(args=None):
    rclpy.init(args=args)
    node = AStarPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
