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

This repository implements a hybrid motion planning algorithm that combines **A\*** (graph-based) and **RRT\*** (sampling-based) path planners with **Kalman filter state estimation** for autonomous mobile robots navigating in obstacle-dense environments.

The hybrid approach achieves a **5.87% path-length improvement** over RRT\* while maintaining a **98% success rate** across 50 simulation trials at three obstacle densities.

---

## Key Results

| Algorithm | Success Rate | Avg Path Length | Improvement |
|-----------|-------------|-----------------|-------------|
| A\*       | 85%         | baseline        | —           |
| RRT\*     | 60%         | +8.2%           | —           |
| **Hybrid A\*-RRT\*** | **98%** | **best** | **−5.87% vs RRT\*** |

> Tested across 50 simulation trials at obstacle densities: 0.10, 0.20, 0.30

---

## Multi-Objective Optimization

The planner minimizes a combined cost index:
