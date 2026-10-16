"""Where does the planning time go?

    python -m benchmarks.profile_planner hybrid --seed 0
    python -m benchmarks.profile_planner rrt_star --iterations 600 1200 1800 3600

Prints a cProfile summary for one run, then planning time against the RRT*
iteration budget (the time grows roughly quadratically because every iteration
scans all existing nodes). Run on an idle machine for numbers you plan to quote.
"""

import argparse
import cProfile
import io
import pstats
import random
import time

import numpy as np

from benchmarks.maps import make_map
from benchmarks.planners import make_planner


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("planner", help="planner spec, e.g. hybrid or rrt_star:max_iterations=900")
    ap.add_argument("--kind", default="random")
    ap.add_argument("--density", type=float, default=0.20)
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--iterations", type=int, nargs="*", default=[600, 1200, 1800, 3600],
                    help="iteration budgets for the scaling table (empty to skip)")
    args = ap.parse_args(argv)

    params = {"density": args.density} if args.kind == "random" else {}
    grid, start, goal = make_map(args.kind, args.size, args.seed, params)

    planner = make_planner(args.planner)
    random.seed(args.seed)
    np.random.seed(args.seed)
    prof = cProfile.Profile()
    t0 = time.perf_counter()
    prof.enable()
    path = planner.plan(start, goal, grid)
    prof.disable()
    dt = time.perf_counter() - t0
    print(f"{args.planner}: {'found' if path else 'no'} path in {dt:.2f}s (profiling overhead included)\n")
    buf = io.StringIO()
    pstats.Stats(prof, stream=buf).sort_stats("tottime").print_stats(args.top)
    print(buf.getvalue())

    name = args.planner.partition(":")[0]
    if args.iterations and name in ("rrt_star", "hybrid", "informed_rrt_star", "hybrid_fallback"):
        print("iteration budget -> planning time (no profiler)")
        for it in args.iterations:
            p = make_planner(f"{name}:max_iterations={it},max_nodes={max(2500, it + 700)}")
            random.seed(args.seed)
            np.random.seed(args.seed)
            t0 = time.perf_counter()
            p.plan(start, goal, grid)
            print(f"  {it:5d} iterations: {time.perf_counter() - t0:7.2f} s")


if __name__ == "__main__":
    main()
