"""
Shared utilities for path planning algorithms.

Source: extracted and cleaned up from the original Colab research
notebook (A_vsRRT_vsHYBRID) used for the thesis:
"Obstacle Avoidance and Optimal Path Planning for Autonomous Mobile
Robots Using Sampling-Based and Graph-Based Algorithms"
Md Asifuzzaman, Lamar University, MES EEE, May 2026
"""

import math
import random
import heapq
import numpy as np


# -----------------------------
# Geometry / grid helpers
# -----------------------------
def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def path_length(path):
    if path is None or len(path) < 2:
        return float("inf")
    return sum(euclidean(path[i], path[i + 1]) for i in range(len(path) - 1))


def in_bounds(p, n):
    x, y = p
    return 0 <= x < n and 0 <= y < n


def make_grid(size=50, obstacle_prob=0.20, seed=0, border_free=True):
    """Generate a random occupancy grid (0 = free, 1 = obstacle)."""
    rng = np.random.default_rng(seed)
    grid = (rng.random((size, size)) < obstacle_prob).astype(np.uint8)
    if border_free:
        grid[0, :] = 0
        grid[-1, :] = 0
        grid[:, 0] = 0
        grid[:, -1] = 0
    return grid


def set_start_goal_free(grid, start, goal):
    grid[start[1], start[0]] = 0
    grid[goal[1], goal[0]] = 0


def line_collision_free(p1, p2, grid):
    """Check collision along a line segment using interpolation."""
    n = max(int(euclidean(p1, p2) * 3), 2)
    for t in np.linspace(0, 1, n):
        x = p1[0] + t * (p2[0] - p1[0])
        y = p1[1] + t * (p2[1] - p1[1])
        xi, yi = int(round(x)), int(round(y))
        if not in_bounds((xi, yi), grid.shape[0]):
            return False
        if grid[yi, xi] == 1:
            return False
    return True


def shortcut_path(path, grid, attempts=120):
    """Simple path smoothing / shortcutting."""
    if path is None or len(path) < 3:
        return path
    path = list(path)
    for _ in range(attempts):
        if len(path) < 3:
            break
        i = random.randint(0, len(path) - 3)
        j = random.randint(i + 2, len(path) - 1)
        if line_collision_free(path[i], path[j], grid):
            path = path[:i + 1] + path[j:]
    return path


# -----------------------------
# A* implementation
# -----------------------------
def astar(grid, start, goal):
    """A* on an 8-connected grid. start, goal are integer (x, y) tuples."""
    n = grid.shape[0]
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1),
             (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def heuristic(a, b):
        return euclidean(a, b)

    open_heap = [(0, start)]
    came_from = {}
    g_score = {start: 0.0}
    visited = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for dx, dy in moves:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            if not in_bounds(neighbor, n):
                continue
            if grid[ny, nx] == 1:
                continue

            step_cost = math.sqrt(2) if dx != 0 and dy != 0 else 1.0
            tentative_g = g_score[current] + step_cost

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_score, neighbor))

    return None


# -----------------------------
# Adaptive corridor (Hybrid method)
# -----------------------------
def local_obstacle_density(grid, x, y, radius=3):
    n = grid.shape[0]
    x0, x1 = max(0, x - radius), min(n, x + radius + 1)
    y0, y1 = max(0, y - radius), min(n, y + radius + 1)
    window = grid[y0:y1, x0:x1]
    return float(np.mean(window))


def build_adaptive_corridor(astar_path, grid, base_width=2.0, max_extra=4.0):
    """
    Assign a corridor width for each A* path point based on local
    obstacle density. Open region -> narrow corridor, dense region ->
    wider corridor. This is the core novelty of the Hybrid method.
    """
    corridor = []
    for (x, y) in astar_path:
        density = local_obstacle_density(grid, x, y, radius=3)
        width = base_width + max_extra * density
        corridor.append(((float(x), float(y)), float(width)))
    return corridor


def sample_from_corridor(grid, corridor, goal=None, goal_sample_rate=0.10):
    """Sample mainly near the A* path corridor; occasionally sample goal."""
    if goal is not None and random.random() < goal_sample_rate:
        return (float(goal[0]), float(goal[1]))

    for _ in range(100):
        center, radius = random.choice(corridor)
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        xi, yi = int(round(x)), int(round(y))
        if in_bounds((xi, yi), grid.shape[0]) and grid[yi, xi] == 0:
            return (x, y)

    return sample_uniform_free(grid, goal=goal, goal_sample_rate=0.0)


def sample_uniform_free(grid, goal=None, goal_sample_rate=0.08):
    """Sample uniformly across the whole free space (standard RRT*)."""
    if goal is not None and random.random() < goal_sample_rate:
        return (float(goal[0]), float(goal[1]))

    n = grid.shape[0]
    for _ in range(200):
        x = random.uniform(0, n - 1)
        y = random.uniform(0, n - 1)
        xi, yi = int(round(x)), int(round(y))
        if in_bounds((xi, yi), n) and grid[yi, xi] == 0:
            return (x, y)
    return (0.0, 0.0)


# -----------------------------
# RRT* core (shared by standard + corridor-guided variants)
# -----------------------------
class Node:
    def __init__(self, x, y, parent=None, cost=0.0):
        self.x = float(x)
        self.y = float(y)
        self.parent = parent
        self.cost = float(cost)

    def point(self):
        return (self.x, self.y)


def nearest_node(nodes, pt):
    dists = [(euclidean(node.point(), pt), i) for i, node in enumerate(nodes)]
    return min(dists, key=lambda x: x[0])[1]


def steer(from_pt, to_pt, step_size):
    d = euclidean(from_pt, to_pt)
    if d <= step_size:
        return to_pt
    theta = math.atan2(to_pt[1] - from_pt[1], to_pt[0] - from_pt[0])
    return (from_pt[0] + step_size * math.cos(theta),
            from_pt[1] + step_size * math.sin(theta))


def near_nodes(nodes, pt, radius):
    return [i for i, node in enumerate(nodes) if euclidean(node.point(), pt) <= radius]


def backtrack_path(nodes, goal_idx):
    path = []
    idx = goal_idx
    while idx is not None:
        path.append(nodes[idx].point())
        idx = nodes[idx].parent
    path.reverse()
    return path


def rrt_star_generic(grid, start, goal, sampler_fn, sampler_args=None,
                      max_iterations=1800, step_size=2.0, neighbor_radius=3.5,
                      goal_threshold=2.0, max_nodes=2500):
    """
    Generic RRT* engine. The `sampler_fn` determines the sampling
    strategy: uniform-free -> standard RRT*, corridor-guided -> Hybrid.
    """
    if sampler_args is None:
        sampler_args = {}

    nodes = [Node(start[0], start[1], parent=None, cost=0.0)]
    best_goal_idx = None
    best_goal_cost = float("inf")

    for _ in range(max_iterations):
        if len(nodes) >= max_nodes:
            break

        rnd = sampler_fn(**sampler_args)
        nearest_idx = nearest_node(nodes, rnd)
        nearest_pt = nodes[nearest_idx].point()
        new_pt = steer(nearest_pt, rnd, step_size)

        xi, yi = int(round(new_pt[0])), int(round(new_pt[1]))
        if not in_bounds((xi, yi), grid.shape[0]):
            continue
        if grid[yi, xi] == 1:
            continue
        if not line_collision_free(nearest_pt, new_pt, grid):
            continue

        near_idxs = near_nodes(nodes, new_pt, neighbor_radius)

        best_parent = nearest_idx
        best_cost = nodes[nearest_idx].cost + euclidean(nearest_pt, new_pt)
        for idx in near_idxs:
            cand_pt = nodes[idx].point()
            if line_collision_free(cand_pt, new_pt, grid):
                cand_cost = nodes[idx].cost + euclidean(cand_pt, new_pt)
                if cand_cost < best_cost:
                    best_cost, best_parent = cand_cost, idx

        new_node = Node(new_pt[0], new_pt[1], parent=best_parent, cost=best_cost)
        nodes.append(new_node)
        new_idx = len(nodes) - 1

        for idx in near_idxs:
            node_pt = nodes[idx].point()
            new_cost = new_node.cost + euclidean(new_pt, node_pt)
            if new_cost < nodes[idx].cost and line_collision_free(new_pt, node_pt, grid):
                nodes[idx].parent = new_idx
                nodes[idx].cost = new_cost

        if euclidean(new_pt, goal) <= goal_threshold and line_collision_free(new_pt, goal, grid):
            goal_cost = new_node.cost + euclidean(new_pt, goal)
            nodes.append(Node(goal[0], goal[1], parent=new_idx, cost=goal_cost))
            goal_idx = len(nodes) - 1
            if goal_cost < best_goal_cost:
                best_goal_cost, best_goal_idx = goal_cost, goal_idx

    if best_goal_idx is None:
        return None, nodes

    path = backtrack_path(nodes, best_goal_idx)
    path = shortcut_path(path, grid, attempts=150)
    return path, nodes
