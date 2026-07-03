"""
ROS2 node that ports the thesis standard RRT* planner into a live planning node.

Subscribes:
    /map            (nav_msgs/OccupancyGrid) - the environment map
    /goal_pose_rrt  (geometry_msgs/PoseStamped) - target pose for RRT* planning

Uses TF2 to get the robot's current pose (map -> base_link).

Publishes:
    /planned_path_rrt (nav_msgs/Path) - the planned path, viewable in RViz

Uses a separate topic pair from the A* node (/goal_pose_rrt, /planned_path_rrt)
so both planners can run side by side for comparison, matching the thesis'
three-way comparison methodology.

Author: Md Asifuzzaman
Thesis: Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile
        Robots Using Sampling-Based and Graph-Based Algorithms
"""

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped
import tf2_ros
from tf2_ros import TransformException

from .rrt_star import RRTStar
from .utils import path_length


class RRTStarPlannerNode(Node):
    def __init__(self):
        super().__init__('rrt_star_planner_node')

        self.grid = None
        self.map_resolution = None
        self.map_origin_x = None
        self.map_origin_y = None

        self.planner = RRTStar()

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        map_qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)

        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, map_qos)

        self.goal_sub = self.create_subscription(
            PoseStamped, '/goal_pose_rrt', self.goal_callback, 10)

        self.path_pub = self.create_publisher(Path, '/planned_path_rrt', 10)

        self.get_logger().info(
            'RRT* planner node started, waiting for /map and /goal_pose_rrt...')

    def map_callback(self, msg: OccupancyGrid):
        width = msg.info.width
        height = msg.info.height
        data = np.array(msg.data, dtype=np.int16).reshape((height, width))

        grid = np.where(data <= 0, 0, 1).astype(np.uint8)
        grid[data == -1] = 1

        self.grid = grid
        self.map_resolution = msg.info.resolution
        self.map_origin_x = msg.info.origin.position.x
        self.map_origin_y = msg.info.origin.position.y

        self.get_logger().info(
            f'Map received: {width}x{height} cells, resolution={self.map_resolution:.3f} m/cell')

    def world_to_grid(self, wx, wy):
        gx = int((wx - self.map_origin_x) / self.map_resolution)
        gy = int((wy - self.map_origin_y) / self.map_resolution)
        return (gx, gy)

    def grid_to_world(self, gx, gy):
        wx = self.map_origin_x + (gx + 0.5) * self.map_resolution
        wy = self.map_origin_y + (gy + 0.5) * self.map_resolution
        return (wx, wy)

    def get_robot_pose(self):
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
        if self.grid is None:
            self.get_logger().warn('No map received yet, cannot plan.')
            return

        robot_pos = self.get_robot_pose()
        if robot_pos is None:
            self.get_logger().warn('No robot pose available, cannot plan.')
            return

        start_cell = self.world_to_grid(*robot_pos)
        goal_cell = self.world_to_grid(msg.pose.position.x, msg.pose.position.y)

        self.get_logger().info(
            f'RRT* planning from {start_cell} to {goal_cell} (grid cells)...')

        h, w = self.grid.shape
        if not (0 <= start_cell[0] < w and 0 <= start_cell[1] < h):
            self.get_logger().warn('Start cell is outside the map bounds.')
            return
        if not (0 <= goal_cell[0] < w and 0 <= goal_cell[1] < h):
            self.get_logger().warn('Goal cell is outside the map bounds.')
            return

        # RRT* is randomized and its thesis-measured success rate is only
        # 60% on a single attempt, so retry a few times before giving up.
        path_cells = None
        for attempt in range(5):
            path_cells = self.planner.plan(start_cell, goal_cell, self.grid)
            if path_cells is not None:
                break
            self.get_logger().info(f'RRT* attempt {attempt + 1} failed, retrying...')

        if path_cells is None:
            self.get_logger().warn('No path found after 5 RRT* attempts!')
            return

        self.get_logger().info(
            f'Path found: {len(path_cells)} waypoints, '
            f'length={path_length(path_cells):.2f} cells')

        self.publish_path(path_cells)

    def publish_path(self, path_cells):
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
        self.get_logger().info(
            f'Published path with {len(path_msg.poses)} poses to /planned_path_rrt')


def main(args=None):
    rclpy.init(args=args)
    node = RRTStarPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
