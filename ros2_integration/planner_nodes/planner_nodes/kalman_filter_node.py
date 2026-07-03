"""
ROS2 node that runs the Kalman filter on live odometry data.

Subscribes:
    /odom            (nav_msgs/Odometry) - raw wheel odometry from Gazebo

Publishes:
    /odom_filtered   (nav_msgs/Odometry) - Kalman-filtered position + velocity estimate

This is new work extending the thesis into real-time state estimation
for the ROS2 deployment (the original thesis never implemented a
Kalman filter). Fuses position measurements with a constant-velocity
motion model to produce a smoother pose estimate than raw odometry
alone, which is useful because wheel odometry drifts and is noisy due
to wheel slip and encoder resolution limits.

Author: Md Asifuzzaman
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

from .kalman_filter import KalmanFilter


class KalmanFilterNode(Node):
    def __init__(self):
        super().__init__('kalman_filter_node')

        # dt matches the timer period below (20 Hz)
        self.kf = KalmanFilter(dt=0.05, process_noise=0.05, measurement_noise=0.1)

        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)

        self.filtered_pub = self.create_publisher(Odometry, '/odom_filtered', 10)

        # Run predict() on a fixed timer, independent of odom message rate,
        # so the filter has a consistent motion model regardless of how
        # often odometry actually arrives.
        self.predict_timer = self.create_timer(0.05, self.predict_step)

        self.latest_odom_msg = None
        self.measurement_count = 0

        self.get_logger().info(
            'Kalman filter node started, waiting for /odom...')

    def predict_step(self):
        """Runs on a fixed timer: propagate the state forward."""
        self.kf.predict()
        if self.latest_odom_msg is not None:
            self.publish_filtered()

    def odom_callback(self, msg: Odometry):
        """Runs whenever a new odometry measurement arrives: update the filter."""
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        self.kf.update([x, y])
        self.latest_odom_msg = msg
        self.measurement_count += 1

        if self.measurement_count == 1:
            self.get_logger().info('First odometry measurement received, filter initialized.')
        elif self.measurement_count % 100 == 0:
            state = self.kf.get_state()
            self.get_logger().info(
                f'Filtered estimate: x={state[0]:.3f}, y={state[1]:.3f}, '
                f'vx={state[2]:.3f}, vy={state[3]:.3f} '
                f'({self.measurement_count} measurements processed)')

    def publish_filtered(self):
        """Publish the current filtered estimate as an Odometry message."""
        state = self.kf.get_state()

        filtered_msg = Odometry()
        filtered_msg.header.frame_id = 'odom'
        filtered_msg.header.stamp = self.get_clock().now().to_msg()
        filtered_msg.child_frame_id = self.latest_odom_msg.child_frame_id

        filtered_msg.pose.pose.position.x = float(state[0])
        filtered_msg.pose.pose.position.y = float(state[1])
        filtered_msg.pose.pose.position.z = self.latest_odom_msg.pose.pose.position.z
        # Orientation isn't part of this filter's state, so pass it through
        # from the raw odometry unchanged.
        filtered_msg.pose.pose.orientation = self.latest_odom_msg.pose.pose.orientation

        filtered_msg.twist.twist.linear.x = float(state[2])
        filtered_msg.twist.twist.linear.y = float(state[3])

        self.filtered_pub.publish(filtered_msg)


def main(args=None):
    rclpy.init(args=args)
    node = KalmanFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
