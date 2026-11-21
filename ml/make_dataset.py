"""Stage 1: build a training set of maps labelled with their exact shortest path.

Each sample is one 50x50 map (random or narrow, varied settings), a start and a
goal, and the exact shortest path from ``vis_graph`` under the same collision
rule as ``configs/decision.json`` (exact, 0.05-cell margin). The path is also
drawn into a 0/1 mask of the cells it passes through: that mask is what the
network will learn to predict.

Training seeds start at 100000, far away from the benchmark seeds (0-29), so
no test map ever appears in training. Half the samples use the benchmark's own
start/goal layout, half use random start/goal pairs, so the network has to look
at the map instead of memorising one route. Mazes are left out on purpose: they
stay as an unseen map family for testing.

Output: ``<out>/shard_00000.npz`` ... (1000 samples each) plus ``<out>/meta.json``.
Re-running the same command resumes: finished shards are skipped.

    python -m ml.make_dataset --n 500 --out data/ml_test          # timing test
    python -m ml.make_dataset --n 50000 --out data/ml_corridor     # full run
"""

import argparse
import json
import math
import multiprocessing as mp
import os
import signal
import time

import numpy as np

from baselines.visgraph import VisGraphShortest
from benchmarks.maps import narrow_map, random_map
from benchmarks.metrics import path_is_valid
from planner_core.utils import astar, path_length, set_collision_mode, set_start_goal_free

SIZE = 50
SEED_BASE = 100_000
SHARD = 1000
MAX_WAYPOINTS = 64          # paths are padded to this many points in the files
COLLISION, MARGIN = "exact", 0.05


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def _init_worker():
    set_collision_mode(COLLISION, MARGIN)
    signal.signal(signal.SIGALRM, _alarm)


def random_endpoints(grid, rng, min_dist):
    """A free start and goal at least ``min_dist`` apart, or None."""
    free = np.argwhere(grid == 0)          # rows are (y, x)
    for _ in range(50):
        a, b = free[rng.integers(len(free), size=2)]
        start, goal = (int(a[1]), int(a[0])), (int(b[1]), int(b[0]))
        if math.dist(start, goal) >= min_dist:
            return start, goal
    return None


def path_mask(path, size):
    """Cells (y, x) that the polyline passes through. Cell (x, y) is the unit square centred on (x, y)."""
    mask = np.zeros((size, size), dtype=np.uint8)
    for (x0, y0), (x1, y1) in zip(path[:-1], path[1:]):
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 0.1) + 1)
        xs = np.clip(np.rint(np.linspace(x0, x1, steps)).astype(int), 0, size - 1)
        ys = np.clip(np.rint(np.linspace(y0, y1, steps)).astype(int), 0, size - 1)
        mask[ys, xs] = 1
    return mask


def make_sample(i, timeout_s):
    """Build sample number ``i``. Returns a dict, or None if it was skipped."""
    seed = SEED_BASE + i
    rng = np.random.default_rng(seed)
    if rng.random() < 0.75:
        kind = "random"
        params = {"density": float(rng.uniform(0.05, 0.35))}
        grid, start, goal = random_map(size=SIZE, seed=seed, **params)
    else:
        kind = "narrow"
        params = {"walls": int(rng.integers(2, 7)), "gap": int(rng.integers(2, 4)),
                  "clutter": float(rng.uniform(0.0, 0.15))}
        grid, start, goal = narrow_map(size=SIZE, seed=seed, **params)

    endpoints = "benchmark"
    if rng.random() < 0.5:
        pair = random_endpoints(grid, rng, min_dist=SIZE / 3)
        if pair is not None:
            start, goal = pair
            set_start_goal_free(grid, start, goal)
            endpoints = "random"

    if astar(grid, start, goal) is None:
        return None                         # no route: skip this map

    t0 = time.perf_counter()
    signal.alarm(timeout_s)
    try:
        path = VisGraphShortest().plan(start, goal, grid)
    except Timeout:
        return None
    finally:
        signal.alarm(0)
    t = time.perf_counter() - t0

    if path is None or len(path) > MAX_WAYPOINTS or not path_is_valid(path, grid, start, goal):
        return None
    padded = np.full((MAX_WAYPOINTS, 2), np.nan, dtype=np.float32)
    padded[:len(path)] = np.asarray(path, dtype=np.float32)
    return {
        "index": i, "seed": seed, "kind": kind, "params": json.dumps(params),
        "endpoints": endpoints, "grid": grid.astype(np.uint8),
        "start": np.array(start, dtype=np.int16), "goal": np.array(goal, dtype=np.int16),
        "mask": path_mask(path, SIZE), "path": padded, "n_waypoints": len(path),
        "length": path_length(path), "time_s": t,
    }


def _work(args):
    return make_sample(*args)


def write_shard(path, samples):
    keys = ["index", "seed", "kind", "params", "endpoints", "start", "goal",
            "grid", "mask", "path", "n_waypoints", "length", "time_s"]
    arrays = {k: np.stack([s[k] for s in samples]) if isinstance(samples[0][k], np.ndarray)
              else np.array([s[k] for s in samples]) for k in keys}
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)                   # a shard is either complete or absent


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=500, help="number of samples to try")
    ap.add_argument("--out", default="data/ml_corridor")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--timeout", type=int, default=60, help="seconds per map before skipping it")
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    meta = {"size": SIZE, "seed_base": SEED_BASE, "shard": SHARD, "collision": COLLISION,
            "margin": MARGIN, "n": args.n, "max_waypoints": MAX_WAYPOINTS}
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    n_shards = math.ceil(args.n / SHARD)
    t_start = time.time()
    kept = skipped = 0
    with mp.Pool(args.workers, initializer=_init_worker) as pool:
        for s in range(n_shards):
            out = os.path.join(args.out, f"shard_{s:05d}.npz")
            if os.path.exists(out):
                print(f"shard {s:05d}: already done, skipping", flush=True)
                continue
            lo, hi = s * SHARD, min((s + 1) * SHARD, args.n)
            samples = []
            for r in pool.imap_unordered(_work, [(i, args.timeout) for i in range(lo, hi)], chunksize=4):
                if r is None:
                    skipped += 1
                else:
                    samples.append(r)
            samples.sort(key=lambda r: r["index"])
            kept += len(samples)
            if samples:
                write_shard(out, samples)
            el = time.time() - t_start
            print(f"shard {s:05d}: {len(samples)} kept | total {kept} kept, {skipped} skipped | "
                  f"{el / 60:.1f} min so far", flush=True)

    el = time.time() - t_start
    print(f"\nDONE: {kept} samples kept, {skipped} skipped, {el / 60:.1f} min, "
          f"{args.workers} workers -> {args.out}")
    if kept:
        per_1000 = el / max(1, kept + skipped) * 1000 / 60
        print(f"Speed: about {per_1000:.1f} min per 1000 maps with {args.workers} workers")


if __name__ == "__main__":
    main()
