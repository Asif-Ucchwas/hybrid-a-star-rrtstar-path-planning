"""Seeded map generators. Every generator returns ``(grid, start, goal)``.

Convention (same as ``planner_core``): ``grid[y, x] == 1`` is an obstacle,
start and goal are integer ``(x, y)`` tuples, and the same ``(kind, size,
seed, params)`` always produces the same map.
"""

import numpy as np

from planner_core.utils import astar, make_grid, set_start_goal_free


def random_map(size=50, density=0.20, seed=0, margin=2):
    """Uniform random obstacles (the thesis setting). Corner to corner."""
    start, goal = (margin, margin), (size - 1 - margin, size - 1 - margin)
    grid = make_grid(size=size, obstacle_prob=density, seed=seed)
    set_start_goal_free(grid, start, goal)
    return grid, start, goal


def narrow_map(size=50, walls=4, gap=2, clutter=0.05, seed=0, margin=2):
    """Vertical walls, each with one narrow gap, plus light clutter.

    Start is on the left, goal on the right. The gap cells (and their
    horizontal neighbours) are always free, so a route exists unless the
    random clutter blocks it; in that case clutter is removed.
    """
    rng = np.random.default_rng(seed)
    grid = (rng.random((size, size)) < clutter).astype(np.uint8)
    xs = np.linspace(0, size - 1, walls + 2)[1:-1].astype(int)
    for x in xs:
        grid[:, x] = 1
        y0 = int(rng.integers(margin + 1, size - margin - gap - 1))
        grid[y0:y0 + gap, max(0, x - 1):x + 2] = 0
    start, goal = (margin, size // 2), (size - 1 - margin, size // 2)
    set_start_goal_free(grid, start, goal)
    if astar(grid, start, goal) is None:  # clutter blocked a gap: drop clutter
        grid2 = np.zeros_like(grid)
        for x in xs:
            grid2[:, x] = 1
        rng2 = np.random.default_rng(seed)
        for x in xs:
            y0 = int(rng2.integers(margin + 1, size - margin - gap - 1))
            grid2[y0:y0 + gap, max(0, x - 1):x + 2] = 0
        grid = grid2
        set_start_goal_free(grid, start, goal)
    return grid, start, goal


def maze_map(size=50, corridor=3, loops=0.10, seed=0):
    """Perfect maze (DFS) with ``corridor``-wide passages, plus some loops.

    The returned grid is ``n_cells * (corridor + 1) + 1`` cells wide (<= size).
    """
    rng = np.random.default_rng(seed)
    pitch = corridor + 1
    n = max(2, (size - 1) // pitch)
    side = n * pitch + 1
    grid = np.ones((side, side), dtype=np.uint8)

    def carve_cell(cx, cy):
        x0, y0 = 1 + cx * pitch, 1 + cy * pitch
        grid[y0:y0 + corridor, x0:x0 + corridor] = 0

    def carve_between(a, b):
        (ax, ay), (bx, by) = a, b
        x0 = 1 + min(ax, bx) * pitch
        y0 = 1 + min(ay, by) * pitch
        if ax != bx:   # horizontal neighbours: open the wall column between them
            grid[y0:y0 + corridor, x0 + corridor] = 0
        else:          # vertical neighbours
            grid[y0 + corridor, x0:x0 + corridor] = 0

    visited = np.zeros((n, n), dtype=bool)
    stack = [(0, 0)]
    visited[0, 0] = True
    carve_cell(0, 0)
    while stack:
        cx, cy = stack[-1]
        nbrs = [(cx + dx, cy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= cx + dx < n and 0 <= cy + dy < n and not visited[cy + dy, cx + dx]]
        if not nbrs:
            stack.pop()
            continue
        nx, ny = nbrs[int(rng.integers(len(nbrs)))]
        visited[ny, nx] = True
        carve_cell(nx, ny)
        carve_between((cx, cy), (nx, ny))
        stack.append((nx, ny))

    # knock out extra walls so the maze has alternative routes
    for cy in range(n):
        for cx in range(n):
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = cx + dx, cy + dy
                if nx < n and ny < n and rng.random() < loops:
                    carve_between((cx, cy), (nx, ny))

    mid = 1 + corridor // 2
    start = (mid, mid)
    goal = (1 + (n - 1) * pitch + corridor // 2, 1 + (n - 1) * pitch + corridor // 2)
    return grid, start, goal


def image_map(path, threshold=0.5, downsample=1, start=(2, 2), goal=None, invert=False):
    """Occupancy map from an image (e.g. a Nav2 map saved as PGM/PNG).

    White (free) / black (occupied) convention; set ``invert`` for the opposite.
    The image is cropped to a square. ``seed`` is ignored (the map is fixed).
    """
    import matplotlib.image as mpimg

    img = mpimg.imread(path)
    if img.ndim == 3:
        img = img[..., :3].mean(axis=2)
    occupied = (img < threshold) if not invert else (img >= threshold)
    grid = occupied.astype(np.uint8)[::downsample, ::downsample]
    side = min(grid.shape)
    grid = np.ascontiguousarray(grid[:side, :side])
    if goal is None:
        goal = (side - 3, side - 3)
    set_start_goal_free(grid, start, goal)
    return grid, tuple(start), tuple(goal)


GENERATORS = {
    "random": random_map,
    "narrow": narrow_map,
    "maze": maze_map,
    "image": image_map,
}


def make_map(kind, size, seed, params=None):
    """Build a map. ``params`` are passed to the generator as keyword arguments."""
    params = dict(params or {})
    if kind not in GENERATORS:
        raise ValueError(f"unknown map kind {kind!r}; choose from {sorted(GENERATORS)}")
    if kind == "image":
        return image_map(**params)
    return GENERATORS[kind](size=size, seed=seed, **params)
