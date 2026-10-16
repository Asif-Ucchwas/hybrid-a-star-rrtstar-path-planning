# Kalman Filter State Estimation
# Author: Md Asifuzzaman
# Thesis extension: built fresh for the ROS2/Gazebo deployment and the
# planned IEEE Access journal submission. This did NOT exist in the
# original thesis (confirmed: only a stub existed there) — it is new
# work extending the thesis into real-time state estimation.
#
# Model: constant-velocity motion model in 2D.
# State vector: [x, y, vx, vy]
# Measurement: [x, y] (e.g. from wheel odometry, which is noisy due to
# wheel slip, encoder resolution, etc.)
#
# predict(): propagates the state forward using the motion model,
#            uncertainty (P) grows.
# update():  incorporates a new position measurement, blends it with
#            the prediction weighted by the Kalman gain, uncertainty
#            shrinks.

import numpy as np


class KalmanFilter:
    def __init__(self, dt=0.1, process_noise=0.05, measurement_noise=0.1):
        """
        dt: time step between predict() calls, in seconds
        process_noise: how much we trust the motion model (lower = more trust)
        measurement_noise: how much we trust incoming measurements (lower = more trust)
        """
        self.dt = dt

        # State: [x, y, vx, vy]
        self.x = np.zeros((4, 1))

        # State covariance (uncertainty) - start fairly uncertain
        self.P = np.eye(4) * 1.0

        # State transition matrix: constant velocity model
        # x' = x + vx*dt, y' = y + vy*dt, vx' = vx, vy' = vy
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

        # Measurement matrix: we only measure position, not velocity
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ])

        # Process noise covariance (uncertainty added each predict step)
        self.Q = np.eye(4) * process_noise

        # Measurement noise covariance (how noisy we assume the sensor is)
        self.R = np.eye(2) * measurement_noise

        self.initialized = False

    def predict(self, state=None, control=None):
        """
        Prediction step: propagate the state forward using the motion
        model. Uncertainty grows. `state`/`control` are accepted for
        interface compatibility but this filter is self-contained and
        uses its own internal state.
        """
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x.flatten()

    def update(self, measurement):
        """
        Update step: incorporate a new [x, y] position measurement.
        Blends the prediction with the measurement, weighted by the
        Kalman gain. Uncertainty shrinks.
        """
        z = np.array(measurement, dtype=float).reshape(2, 1)

        if not self.initialized:
            # First measurement: just snap to it directly
            self.x[0, 0] = z[0, 0]
            self.x[1, 0] = z[1, 0]
            self.initialized = True
            return self.x.flatten()

        # Innovation: difference between measurement and prediction
        y = z - self.H @ self.x

        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R

        # Kalman gain: how much to trust the measurement vs the prediction
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update state and covariance
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

        return self.x.flatten()

    def get_state(self):
        """Returns current [x, y, vx, vy] estimate."""
        return self.x.flatten()

    def get_position(self):
        """Returns current [x, y] estimate only."""
        return self.x.flatten()[:2]
