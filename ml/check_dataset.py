"""Check a dataset made by ``ml.make_dataset``: totals, sanity checks and a picture.

    python -m ml.check_dataset data/ml_corridor

Prints counts and checks, and saves ``<dir>/examples.png`` with 8 random maps
(black = obstacle, red = labelled path cells, blue line = exact path,
green = start, orange = goal).
"""

import argparse
import glob
import os

import numpy as np


def load(dirname):
    files = sorted(glob.glob(os.path.join(dirname, "shard_*.npz")))
    if not files:
        raise SystemExit(f"no shard_*.npz files in {dirname}")
    parts = {}
    for f in files:
        with np.load(f) as d:
            for k in d.files:
                parts.setdefault(k, []).append(d[k])
    return {k: np.concatenate(v) for k, v in parts.items()}, files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir", nargs="?", default="data/ml_corridor")
    ap.add_argument("--seed", type=int, default=0, help="which random examples to draw")
    args = ap.parse_args(argv)

    d, files = load(args.dir)
    n = len(d["index"])
    size_mb = sum(os.path.getsize(f) for f in files) / 1e6
    grid, mask = d["grid"], d["mask"]

    print(f"Samples: {n}  |  shards: {len(files)}  |  on disk: {size_mb:.0f} MB")
    for key in ("kind", "endpoints"):
        vals, counts = np.unique(d[key], return_counts=True)
        print(f"{key:>10}: " + ", ".join(f"{v} {c} ({100 * c / n:.0f}%)" for v, c in zip(vals, counts)))
    dens = grid.reshape(n, -1).mean(1)
    print(f"   density: min {dens.min():.2f}, mean {dens.mean():.2f}, max {dens.max():.2f}")
    print(f"path cells: mean {mask.reshape(n, -1).sum(1).mean():.0f} of {grid.shape[1] * grid.shape[2]} "
          f"({100 * mask.mean():.1f}% of the map) -> the network must find a thin line")
    print(f"path len  : mean {d['length'].mean():.1f}, waypoints mean {d['n_waypoints'].mean():.1f}, "
          f"max {d['n_waypoints'].max()}")
    t = d["time_s"]
    print(f"exact time: median {np.median(t):.2f} s, 95% {np.percentile(t, 95):.2f} s, max {t.max():.1f} s")

    print("\nChecks:")
    on_obst = int((mask & grid).sum())
    s, g = d["start"].astype(int), d["goal"].astype(int)
    idx = np.arange(n)
    ends_ok = bool(mask[idx, s[:, 1], s[:, 0]].all() and mask[idx, g[:, 1], g[:, 0]].all())
    ends_free = bool((grid[idx, s[:, 1], s[:, 0]] == 0).all() and (grid[idx, g[:, 1], g[:, 0]] == 0).all())
    seeds_ok = bool(d["seed"].min() >= 100_000)
    dup = n - len(np.unique(d["seed"]))
    for ok, text in [(on_obst == 0, f"path cells on obstacles: {on_obst}"),
                     (ends_ok, "start and goal are on the path"),
                     (ends_free, "start and goal are free cells"),
                     (seeds_ok, f"all seeds >= 100000 (no overlap with test seeds); lowest {d['seed'].min()}"),
                     (dup == 0, f"duplicate seeds: {dup}")]:
        print(f"  [{'OK' if ok else 'FAIL'}] {text}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(args.seed)
    pick = rng.choice(n, size=min(8, n), replace=False)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8.4))
    for ax, i in zip(axes.flat, pick):
        img = np.ones((*grid[i].shape, 3))
        img[grid[i] == 1] = 0.0
        img[(mask[i] == 1) & (grid[i] == 0)] = (1.0, 0.75, 0.75)
        ax.imshow(img, origin="lower", interpolation="nearest")
        p = d["path"][i]
        p = p[~np.isnan(p[:, 0])]
        ax.plot(p[:, 0], p[:, 1], "-", color="tab:blue", lw=1.6)
        ax.plot(*s[i], "o", color="tab:green", ms=7)
        ax.plot(*g[i], "o", color="tab:orange", ms=7)
        ax.set_title(f"{d['kind'][i]} | {d['endpoints'][i]} | seed {d['seed'][i]}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    out = os.path.join(args.dir, "examples.png")
    fig.savefig(out, dpi=110)
    print(f"\nPicture saved: {out}")


if __name__ == "__main__":
    main()
