"""Benchmark runner.

Runs every planner in a config on every (scenario, seed) map and appends one
CSV row per run to ``<out>/raw.csv``. Re-running the same command resumes: runs
already in the CSV are skipped.

    python -m benchmarks.runner configs/smoke.json --out results/smoke
    python -m benchmarks.runner configs/paper_main.json --workers 8

Timing note: with ``--workers > 1`` several planners compete for CPU and cache,
so wall-clock numbers are noisy. Use ``--workers 1`` on an otherwise idle
machine for any latency number you intend to publish (``cpu_s`` is steadier).
"""

import argparse
import csv
import json
import multiprocessing as mp
import os
import platform
import random
import subprocess
import sys
import time
import zlib
from datetime import datetime, timezone

import numpy as np

from benchmarks.maps import make_map
from benchmarks.metrics import clearance_map, evaluate_path, path_is_valid
from benchmarks.planners import make_planner, planner_nodes
from planner_core.utils import astar, path_length

FIELDS = [
    "scenario", "family", "x", "seed", "planner", "success", "valid", "time_s", "cpu_s",
    "length", "astar_len", "turn_total_deg", "turn_mean_deg", "clearance_min",
    "clearance_mean", "strict_valid", "n_waypoints", "nodes", "fallback", "error",
]


def load_config(path):
    with open(path) as f:
        cfg = json.load(f)
    planners = []
    for p in cfg["planners"]:
        planners.append({"id": p, "spec": p} if isinstance(p, str) else p)
    cfg["planners"] = planners
    for sc in cfg["scenarios"]:
        sc.setdefault("family", sc["id"])
        sc.setdefault("x", None)
        sc.setdefault("size", 50)
        sc.setdefault("params", {})
        sc.setdefault("seed_offset", 0)
        if "planners" in sc:
            sc["planners"] = [{"id": p, "spec": p} if isinstance(p, str) else p
                              for p in sc["planners"]]
    return cfg


def derive_seed(scenario_id, seed, planner_id):
    """Stable 31-bit seed for one (scenario, map seed, planner) run."""
    return zlib.crc32(f"{scenario_id}|{seed}|{planner_id}".encode()) & 0x7FFFFFFF


def build_tasks(cfg):
    tasks = []
    for si, sc in enumerate(cfg["scenarios"]):
        plist = sc.get("planners", cfg["planners"])
        for k in range(sc["seeds"]):
            seed = sc["seed_offset"] + k
            for p in plist:
                tasks.append((si, seed, p["id"], p["spec"]))
    return tasks


_CFG = None


def _init_worker(cfg):
    global _CFG
    _CFG = cfg


def run_task(task):
    si, seed, planner_id, spec = task
    sc = _CFG["scenarios"][si]
    row = {k: "" for k in FIELDS}
    row.update(scenario=sc["id"], family=sc["family"], x=sc["x"] if sc["x"] is not None else "",
               seed=seed, planner=planner_id, success=0, valid=0, fallback=0)
    try:
        grid, start, goal = make_map(sc["kind"], sc["size"], seed, sc["params"])
        ref = astar(grid, start, goal)
        row["astar_len"] = path_length(ref) if ref is not None else ""
        planner = make_planner(spec)
        rseed = derive_seed(sc["id"], seed, planner_id)
        random.seed(rseed)
        np.random.seed(rseed)
        t0, c0 = time.perf_counter(), time.process_time()
        path = planner.plan(start, goal, grid)
        row["time_s"] = time.perf_counter() - t0
        row["cpu_s"] = time.process_time() - c0
        row["nodes"] = planner_nodes(planner)
        row["fallback"] = int(bool((getattr(planner, "last_info", None) or {}).get("fallback")))
        if path is not None:
            valid = path_is_valid(path, grid, start, goal)
            row["valid"] = int(valid)
            row["success"] = int(valid)
            if valid:
                row.update(evaluate_path(path, grid, clearance_map(grid)))
    except Exception as exc:  # keep the run going, record the failure
        row["error"] = f"{type(exc).__name__}: {exc}"[:200]
    return row


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
                                       text=True, cwd=os.path.dirname(os.path.dirname(
                                           os.path.abspath(__file__)))).strip()
    except Exception:
        return None


def cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def load_done(raw_path):
    done = set()
    if os.path.exists(raw_path):
        with open(raw_path, newline="") as f:
            for r in csv.DictReader(f):
                done.add((r["scenario"], int(r["seed"]), r["planner"]))
    return done


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--out", default=None, help="output directory (default results/<config name>)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None, help="run at most N new tasks (debugging)")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    out = args.out or os.path.join("results", cfg.get("name", os.path.splitext(
        os.path.basename(args.config))[0]))
    os.makedirs(out, exist_ok=True)
    raw_path = os.path.join(out, "raw.csv")

    tasks = build_tasks(cfg)
    done = load_done(raw_path)
    todo = [t for t in tasks if (cfg["scenarios"][t[0]]["id"], t[1], t[2]) not in done]
    if args.limit:
        todo = todo[:args.limit]

    meta = {
        "config_file": os.path.basename(args.config),
        "config": cfg,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "cpu": cpu_model(),
        "cpu_count": os.cpu_count(),
        "workers": args.workers,
        "git_commit": git_commit(),
        "clean_timing": args.workers == 1,
    }
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"{len(tasks)} runs in config, {len(done)} already done, {len(todo)} to run "
          f"({args.workers} worker{'s' if args.workers != 1 else ''}) -> {raw_path}")
    if args.workers > 1:
        print("note: wall-clock timings are noisy with more than one worker.")

    new_file = not os.path.exists(raw_path)
    t_start = time.time()
    with open(raw_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        if args.workers == 1:
            _init_worker(cfg)
            results = map(run_task, todo)
            pool = None
        else:
            pool = mp.Pool(args.workers, initializer=_init_worker, initargs=(cfg,))
            results = pool.imap_unordered(run_task, todo, chunksize=4)
        try:
            for i, row in enumerate(results, 1):
                writer.writerow(row)
                if i % 50 == 0 or i == len(todo):
                    f.flush()
                    el = time.time() - t_start
                    print(f"  {i}/{len(todo)} runs  ({el:.0f}s elapsed)", end="\r", flush=True)
        finally:
            if pool is not None:
                pool.close()
                pool.join()
    print(f"\ndone: {raw_path}")


if __name__ == "__main__":
    main()
