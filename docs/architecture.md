# System Architecture

## Overview
This repository implements a hybrid motion planning algorithm combining A* and RRT*
with Kalman filter state estimation for autonomous mobile robots.

## Thesis
Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile Robots
Using Sampling-Based and Graph-Based Algorithms
Md Asifuzzaman — Lamar University, MES EEE, May 2026

## Components
- **Hybrid A***: Global path planner combining A* graph search with RRT* sampling
- **RRT***: Baseline comparison algorithm
- **Kalman Filter**: State estimation for robot pose tracking

## Results
| Algorithm | Success Rate | Path Length vs RRT* |
|-----------|-------------|----------------------|
| A*        | 85%         | baseline             |
| RRT*      | 60%         | baseline             |
| Hybrid A*-RRT* | 98%   | -5.87% improvement   |

## Optimization Index
J = αL + βT + γ(1−S)
where L = path length, T = computation time, S = success rate

## ROS2 Integration
Coming soon: Nav2 custom planner plugin on TurtleBot3/Gazebo
