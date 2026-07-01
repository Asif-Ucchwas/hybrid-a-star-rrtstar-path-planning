# Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile Robots
### Using Sampling-Based and Graph-Based Algorithms

![Python](https://img.shields.io/badge/Python-3.10-blue)
![ROS2](https://img.shields.io/badge/ROS2-Jazzy-brightgreen)
![Gazebo](https://img.shields.io/badge/Gazebo-8.11-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Author:** Md Asifuzzaman
**Degree:** Master of Engineering Science (MES) — Electrical & Electronics Engineering
**University:** Lamar University, Beaumont, TX
**Year:** May 2026
**Thesis:** [View on ProQuest](https://www.proquest.com/dissertations-theses/obstacle-avoidance-optimal-path-planning/docview/32699575)

---

## Overview

This repository implements a hybrid motion planning algorithm that combines **A*** (graph-based) and **RRT*** (sampling-based) path planners with **Kalman filter state estimation** for autonomous mobile robots navigating in obstacle-dense environments.

The hybrid approach achieves a **5.87% path-length improvement** over RRT* while maintaining a **98% success rate** across 50 simulation trials at three obstacle densities.

---

## Key Results

| Algorithm | Success Rate | Avg Path Length | Improvement |
|-----------|-------------|-----------------|-------------|
| A* | 85% | baseline | — |
| RRT* | 60% | +8.2% | — |
| Hybrid A*-RRT* | 98% | best | -5.87% vs RRT* |

Tested across 50 simulation trials at obstacle densities: 0.10, 0.20, 0.30

---

## Multi-Objective Optimization

The planner minimizes a combined cost index:

J = aL + bT + g(1 - S)

Where:
- L = path length
- T = computation time
- S = success rate
- a, b, g = weighting coefficients

---

## Repository Structure

- src/hybrid_astar.py — Hybrid A*-RRT* planner
- src/rrt_star.py — RRT* baseline algorithm
- src/kalman_filter.py — Kalman filter state estimation
- scripts/run_simulation.py — Run simulation demo
- results/trajectory_plots/ — Path visualization outputs
- results/benchmark_data/ — 50-trial benchmark results
- docs/architecture.md — System architecture details

---

## Installation

Clone the repository:
git clone https://github.com/Asif-Ucchwas/hybrid-a-star-rrtstar-path-planning.git
cd hybrid-a-star-rrtstar-path-planning

Install dependencies:
pip install -r requirements.txt

Run simulation:
python scripts/run_simulation.py

---

## ROS2 Integration

Full ROS2/Gazebo integration with TurtleBot3 and Nav2 is in progress.
The hybrid planner will be implemented as a custom Nav2 planner plugin.

Environment: ROS2 Jazzy + Gazebo 8 + Ubuntu 24.04

---

## Related Work

- IoT-Based Fault Detection System — Co-authored paper, IJSRP, July 2023
- Smartphone-Controlled Mobile Robot — 3rd place, national robotics competition

---

## Contact

- LinkedIn: https://linkedin.com/in/masifuzzaman
- GitHub: https://github.com/Asif-Ucchwas
- Email: asifuzzamanucchwas@gmail.com
