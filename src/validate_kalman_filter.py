"""
Kalman Filter Synthetic Validation Script
Author: Md Asifuzzaman

Purpose: Regenerate the KF position-error-reduction validation figure and
number, reproducibly, using the actual KalmanFilter implementation deployed
in the ROS2 node (ros2_integration/planner_nodes/planner_nodes/kalman_filter.py).

Ground-truth trajectory: circular path, matching the paper's live simulation
validation setup (~0.19 m/s tangential speed).

Filter parameters (fixed, matching the paper's stated values):
    dt = 0.05 s
    process_noise = 0.05
    measurement_noise = 0.1

Outputs:
    - Printed position-error-reduction percentage (raw vs. filtered RMSE)
    - fig_kf_validation.png (regenerated validation figure)
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "ros2_integration",
                  "planner_nodes", "planner_nodes")
)
from kalman_filter import KalmanFilter  # noqa: E402

SEED = 42
rng = np.random.default_rng(SEED)

DT = 0.05
PROCESS_NOISE = 0.05
MEASUREMENT_NOISE = 0.1

RADIUS = 2.0
SPEED = 0.19
OMEGA = SPEED / RADIUS
DURATION = 60.0
N_STEPS = int(DURATION / DT)

t = np.arange(N_STEPS) * DT
true_x = RADIUS * np.cos(OMEGA * t)
true_y = RADIUS * np.sin(OMEGA * t)
true_pos = np.stack([true_x, true_y], axis=1)

measurement_std = 0.15  # realistic injected sensor noise (filter's internal belief stays MEASUREMENT_NOISE=0.1)
noisy_pos = true_pos + rng.normal(0, measurement_std, size=true_pos.shape)

kf = KalmanFilter(dt=DT, process_noise=PROCESS_NOISE,
                   measurement_noise=MEASUREMENT_NOISE)

filtered_pos = np.zeros_like(true_pos)
for i in range(N_STEPS):
    kf.predict()
    est = kf.update(noisy_pos[i])
    filtered_pos[i] = est[:2]

raw_error = np.linalg.norm(noisy_pos - true_pos, axis=1)
filtered_error = np.linalg.norm(filtered_pos - true_pos, axis=1)

BURN_IN = 10
raw_rmse = np.sqrt(np.mean(raw_error[BURN_IN:] ** 2))
filtered_rmse = np.sqrt(np.mean(filtered_error[BURN_IN:] ** 2))

reduction_pct = (raw_rmse - filtered_rmse) / raw_rmse * 100

print(f"Raw (noisy) measurement RMSE:      {raw_rmse:.4f} m")
print(f"Kalman-filtered RMSE:               {filtered_rmse:.4f} m")
print(f"Position-error reduction:           {reduction_pct:.1f}%")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.plot(true_x, true_y, 'k-', linewidth=2, label='Ground truth')
ax.plot(noisy_pos[:, 0], noisy_pos[:, 1], '.', color='tab:red',
        markersize=2, alpha=0.4, label='Noisy measurement')
ax.plot(filtered_pos[:, 0], filtered_pos[:, 1], '-', color='tab:blue',
        linewidth=1.5, label='Kalman filter estimate')
ax.set_xlabel('x (m)')
ax.set_ylabel('y (m)')
ax.set_title('Trajectory Tracking: Ground Truth vs. Noisy vs. Filtered')
ax.legend(loc='upper right', fontsize=8)
ax.set_aspect('equal')
ax.grid(alpha=0.3)

ax2 = axes[1]
ax2.plot(t[BURN_IN:], raw_error[BURN_IN:], color='tab:red', alpha=0.6,
         linewidth=1, label=f'Raw error (RMSE={raw_rmse:.3f} m)')
ax2.plot(t[BURN_IN:], filtered_error[BURN_IN:], color='tab:blue',
         linewidth=1.2, label=f'Filtered error (RMSE={filtered_rmse:.3f} m)')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Position error (m)')
ax2.set_title(f'Position Error Over Time ({reduction_pct:.1f}% reduction)')
ax2.legend(loc='upper right', fontsize=8)
ax2.grid(alpha=0.3)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "figures", "fig_kf_validation.png")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, dpi=200)
print(f"\nFigure saved to: {out_path}")
