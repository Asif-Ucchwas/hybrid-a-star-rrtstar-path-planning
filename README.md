# Hybrid A*–RRT* Path Planning for Autonomous Mobile Robots

## Overview

This project presents a hybrid motion planning framework combining A* and RRT* algorithms. A* is used to generate a global path, while RRT* refines the path within an adaptive corridor to improve efficiency and optimality.

## Features

* A* global path planning
* RRT* path refinement
* Adaptive corridor-guided sampling
* Occupancy grid-based environment
* Performance evaluation under different obstacle densities

## Tools & Technologies

* Python
* NumPy
* Matplotlib
* Google Colab

## Results

The hybrid method reduces unnecessary exploration and improves convergence compared to standalone A* and RRT* approaches in cluttered environments.

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## Repository Structure

* `src/` – algorithm implementations
* `maps/` – occupancy grid maps
* `results/` – performance plots
* `figures/` – visualization images
* `notebooks/` – Colab experiments
