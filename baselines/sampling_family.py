"""Sampling-based baselines: Informed RRT*, RRT-Connect, BIT* (compact).

All planners share the same grid convention as ``planner_core``:
``grid[y, x] == 1`` is an obstacle, points are ``(x, y)``. All use the
global ``random`` module for sampling, so seeding ``random`` before ``plan``
makes a run reproducible. Sampling-based outputs get the same random-shortcut
smoothing that ``rrt_star_generic`` applies to RRT* and Hybrid, so path length
comparisons are like for like.
"""

import heapq
import itertools
import math
import random

from planner_core.utils import (
    Node,
    backtrack_path,
    euclidean,
    in_bounds,
    line_collision_free,
    nearest_node,
    near_nodes,
    sample_uniform_free,
    shortcut_path,
    steer,
)


def _is_free(grid, pt):
    xi, yi = int(round(pt[0])), int(round(pt[1]))
    return in_bounds((xi, yi), grid.shape[0]) and grid[yi, xi] == 0


def informed_sample(grid, start, goal, c_best, goal_sample_rate=0.0):
    """Uniform sample inside the prolate ellipse of cost ``c_best`` (2D).

    Falls back to uniform free-space sampling when ``c_best`` is infinite or
    when no free ellipse sample is found in 100 tries.
    """
    if goal_sample_rate > 0 and random.random() < goal_sample_rate:
        return (float(goal[0]), float(goal[1]))
    c_min = euclidean(start, goal)
    if math.isinf(c_best) or c_best <= c_min + 1e-9:
        return sample_uniform_free(grid, goal=None, goal_sample_rate=0.0)

    a = c_best / 2.0
    b = math.sqrt(max(c_best ** 2 - c_min ** 2, 0.0)) / 2.0
    cx, cy = (start[0] + goal[0]) / 2.0, (start[1] + goal[1]) / 2.0
    theta = math.atan2(goal[1] - start[1], goal[0] - start[0])
    ct, st = math.cos(theta), math.sin(theta)
    for _ in range(100):
        r = math.sqrt(random.random())
        phi = random.uniform(0, 2 * math.pi)
        ux, uy = r * math.cos(phi) * a, r * math.sin(phi) * b
        x = cx + ct * ux - st * uy
        y = cy + st * ux + ct * uy
        if _is_free(grid, (x, y)):
            return (x, y)
    return sample_uniform_free(grid, goal=None, goal_sample_rate=0.0)


class InformedRRTStar:
    """Informed RRT* (Gammell, Srinivasa, Barfoot, 2014).

    Same parameters and iteration budget as ``planner_core.RRTStar``; after a
    first solution is found, sampling is restricted to the informed ellipse.
    """

    def __init__(self, max_iterations=1800, step_size=2.0, neighbor_radius=3.5,
                 goal_threshold=2.0, max_nodes=2500, goal_sample_rate=0.10,
                 smoothing_attempts=150):
        self.max_iterations = max_iterations
        self.step_size = step_size
        self.neighbor_radius = neighbor_radius
        self.goal_threshold = goal_threshold
        self.max_nodes = max_nodes
        self.goal_sample_rate = goal_sample_rate
        self.smoothing_attempts = smoothing_attempts
        self.last_info = {}

    def plan(self, start, goal, grid):
        nodes = [Node(start[0], start[1], parent=None, cost=0.0)]
        best_goal_idx = None
        best_cost = float("inf")

        for _ in range(self.max_iterations):
            if len(nodes) >= self.max_nodes:
                break
            rnd = informed_sample(grid, start, goal, best_cost,
                                  goal_sample_rate=self.goal_sample_rate)
            nearest_idx = nearest_node(nodes, rnd)
            nearest_pt = nodes[nearest_idx].point()
            new_pt = steer(nearest_pt, rnd, self.step_size)
            if not _is_free(grid, new_pt):
                continue
            if not line_collision_free(nearest_pt, new_pt, grid):
                continue

            near_idxs = near_nodes(nodes, new_pt, self.neighbor_radius)
            best_parent = nearest_idx
            best_c = nodes[nearest_idx].cost + euclidean(nearest_pt, new_pt)
            for idx in near_idxs:
                cand_pt = nodes[idx].point()
                if line_collision_free(cand_pt, new_pt, grid):
                    cand_c = nodes[idx].cost + euclidean(cand_pt, new_pt)
                    if cand_c < best_c:
                        best_c, best_parent = cand_c, idx

            new_node = Node(new_pt[0], new_pt[1], parent=best_parent, cost=best_c)
            nodes.append(new_node)
            new_idx = len(nodes) - 1

            for idx in near_idxs:
                node_pt = nodes[idx].point()
                new_cost = new_node.cost + euclidean(new_pt, node_pt)
                if new_cost < nodes[idx].cost and line_collision_free(new_pt, node_pt, grid):
                    nodes[idx].parent = new_idx
                    nodes[idx].cost = new_cost

            if (euclidean(new_pt, goal) <= self.goal_threshold
                    and line_collision_free(new_pt, goal, grid)):
                goal_cost = new_node.cost + euclidean(new_pt, goal)
                nodes.append(Node(goal[0], goal[1], parent=new_idx, cost=goal_cost))
                if goal_cost < best_cost:
                    best_cost = goal_cost
                    best_goal_idx = len(nodes) - 1

        self.last_info = {"nodes": len(nodes)}
        if best_goal_idx is None:
            return None
        path = backtrack_path(nodes, best_goal_idx)
        return shortcut_path(path, grid, attempts=self.smoothing_attempts)


class RRTConnect:
    """RRT-Connect (Kuffner and LaValle, 2000): two trees, greedy connect. Not optimal."""

    def __init__(self, max_iterations=1800, step_size=2.0, max_nodes=2500,
                 smoothing_attempts=150):
        self.max_iterations = max_iterations
        self.step_size = step_size
        self.max_nodes = max_nodes
        self.smoothing_attempts = smoothing_attempts
        self.last_info = {}

    def _extend(self, tree, target, grid):
        idx = nearest_node(tree, target)
        near_pt = tree[idx].point()
        new_pt = steer(near_pt, target, self.step_size)
        if not _is_free(grid, new_pt) or not line_collision_free(near_pt, new_pt, grid):
            return "trapped", None
        tree.append(Node(new_pt[0], new_pt[1], parent=idx,
                         cost=tree[idx].cost + euclidean(near_pt, new_pt)))
        reached = euclidean(new_pt, target) < 1e-9
        return ("reached" if reached else "advanced"), len(tree) - 1

    def _connect(self, tree, target, grid):
        status, idx = "advanced", None
        while status == "advanced":
            status, new_idx = self._extend(tree, target, grid)
            if new_idx is not None:
                idx = new_idx
        return status, idx

    def plan(self, start, goal, grid):
        tree_a = [Node(start[0], start[1])]
        tree_b = [Node(goal[0], goal[1])]
        a_is_start = True

        for _ in range(self.max_iterations):
            if len(tree_a) + len(tree_b) >= self.max_nodes:
                break
            q = sample_uniform_free(grid, goal=None, goal_sample_rate=0.0)
            status, idx_a = self._extend(tree_a, q, grid)
            if status != "trapped":
                status_b, idx_b = self._connect(tree_b, tree_a[idx_a].point(), grid)
                if status_b == "reached":
                    half_a = backtrack_path(tree_a, idx_a)
                    half_b = backtrack_path(tree_b, idx_b)
                    half_b.reverse()
                    # half_a runs root_a -> meeting point, half_b meeting point -> root_b
                    path = half_a + half_b[1:]
                    if not a_is_start:
                        path.reverse()
                    path[0] = (float(start[0]), float(start[1]))
                    path[-1] = (float(goal[0]), float(goal[1]))
                    self.last_info = {"nodes": len(tree_a) + len(tree_b)}
                    return shortcut_path(path, grid, attempts=self.smoothing_attempts)
            tree_a, tree_b = tree_b, tree_a
            a_is_start = not a_is_start

        self.last_info = {"nodes": len(tree_a) + len(tree_b)}
        return None


class BITStar:
    """Compact BIT* (Gammell, Srinivasa, Barfoot, 2015) for 2D grid maps.

    Batches of ``batch_size`` informed samples, a vertex queue and an edge queue
    ordered by estimated solution cost, and a random-geometric-graph radius.
    Simplification versus the paper: only samples are pruned after a solution
    is found (the tree vertices are kept). Budget: ``max_batches`` batches.
    """

    def __init__(self, batch_size=40, max_batches=12, eta=1.1,
                 smoothing_attempts=150, max_edge_pops=60000):
        self.batch_size = batch_size
        self.max_batches = max_batches
        self.eta = eta
        self.smoothing_attempts = smoothing_attempts
        self.max_edge_pops = max_edge_pops
        self.last_info = {}

    def _radius(self, q, free_area):
        d = 2.0
        q = max(q, 2)
        return self.eta * 2.0 * ((1.0 + 1.0 / d) * free_area / math.pi) ** (1.0 / d) \
            * (math.log(q) / q) ** (1.0 / d)

    def plan(self, start, goal, grid):
        start = (float(start[0]), float(start[1]))
        goal = (float(goal[0]), float(goal[1]))
        n = grid.shape[0]
        free_area = float(n * n - grid.sum())
        counter = itertools.count()

        g = {start: 0.0}                 # cost-to-come of tree vertices
        parent = {start: None}
        vertices = {start}
        samples = {goal}
        v_old = set()
        c_best = float("inf")

        def h_hat(p):
            return euclidean(p, goal)

        def g_hat(p):
            return euclidean(start, p)

        q_v = []   # (g_T(v)+h_hat(v), counter, v)
        q_e = []   # (g_T(v)+c_hat(v,x)+h_hat(x), counter, v, x)
        batches = 0
        pops = 0
        r = float("inf")

        def expand_vertex(v):
            near_x = [x for x in samples if euclidean(v, x) <= r]
            for x in near_x:
                if g_hat(v) + euclidean(v, x) + h_hat(x) < c_best:
                    key = g[v] + euclidean(v, x) + h_hat(x)
                    heapq.heappush(q_e, (key, next(counter), v, x))
            if v not in v_old:
                for w in vertices:
                    if w == v:
                        continue
                    if euclidean(v, w) <= r and parent.get(w) != v and parent.get(v) != w:
                        if (g_hat(v) + euclidean(v, w) + h_hat(w) < c_best
                                and g[v] + euclidean(v, w) < g[w]):
                            key = g[v] + euclidean(v, w) + h_hat(w)
                            heapq.heappush(q_e, (key, next(counter), v, w))

        while batches <= self.max_batches and pops < self.max_edge_pops:
            if not q_e and not q_v:
                if batches == self.max_batches:
                    break
                batches += 1
                # prune samples that cannot improve the current solution
                if not math.isinf(c_best):
                    samples = {x for x in samples
                               if g_hat(x) + h_hat(x) < c_best or x == goal}
                for _ in range(self.batch_size):
                    s = informed_sample(grid, start, goal, c_best)
                    samples.add((float(s[0]), float(s[1])))
                v_old = set(vertices)
                for v in vertices:
                    heapq.heappush(q_v, (g[v] + h_hat(v), next(counter), v))
                r = self._radius(len(vertices) + len(samples), free_area)

            # expand vertices until the best vertex is worse than the best edge
            while q_v and (not q_e or q_v[0][0] <= q_e[0][0]):
                _, _, v = heapq.heappop(q_v)
                if v in vertices:
                    expand_vertex(v)

            if not q_e:
                continue
            _, _, v, x = heapq.heappop(q_e)
            pops += 1
            if v not in vertices:
                continue
            c_hat = euclidean(v, x)
            if g[v] + c_hat + h_hat(x) >= c_best or g[v] + c_hat >= g.get(x, float("inf")):
                continue
            if not line_collision_free(v, x, grid):
                continue
            c_new = g[v] + c_hat
            if x in vertices:
                parent[x] = v
                g[x] = c_new
            else:
                samples.discard(x)
                vertices.add(x)
                parent[x] = v
                g[x] = c_new
                heapq.heappush(q_v, (g[x] + h_hat(x), next(counter), x))
            if goal in g:
                c_best = g[goal]

        self.last_info = {"nodes": len(vertices), "batches": batches}
        if goal not in g:
            return None
        path = [goal]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        path.reverse()
        return shortcut_path(path, grid, attempts=self.smoothing_attempts)
