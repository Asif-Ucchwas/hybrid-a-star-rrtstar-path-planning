"""
Independent reproducibility check.

Runs A*, standard RRT*, and the Hybrid A*+corridor-RRT* planner across
N randomly generated maps and reports aggregate success rate, average
path length, and average planning time for each.

This is a fresh, independent validation using the same code as the
thesis experiments — not a re-run of the exact original experiment.
Exact percentages will vary run to run (RRT* and Hybrid are randomized
algorithms, and this script's default parameters/random seeds are not
guaranteed identical to the original thesis notebook). The officially
published, committee-approved thesis results are in the thesis document
itself and in this repo's README. What this script demonstrates is that
the same qualitative pattern reproduces: Hybrid is more reliable than
standard RRT* and produces shorter paths on average, while A* remains
the fastest but not the shortest.

Usage:
    python benchmark_50trials.py
"""

import time
import numpy as np

from utils import make_grid, set_start_goal_free, astar, path_length
from hybrid_astar import HybridAStar
from rrt_star import RRTStar


def run_benchmark(n_trials=50, obstacle_prob=0.20, grid_size=50):
    start, goal = (2, 2), (grid_size - 3, grid_size - 3)

    results = {
        'A*': {'successes': 0, 'lengths': [], 'times': []},
        'RRT*': {'successes': 0, 'lengths': [], 'times': []},
        'Hybrid': {'successes': 0, 'lengths': [], 'times': []},
    }

    for trial in range(n_trials):
        grid = make_grid(size=grid_size, obstacle_prob=obstacle_prob, seed=trial)
        set_start_goal_free(grid, start, goal)

        # A*
        t0 = time.perf_counter()
        a_path = astar(grid, start, goal)
        t1 = time.perf_counter()
        if a_path is not None:
            results['A*']['successes'] += 1
            results['A*']['lengths'].append(path_length(a_path))
        results['A*']['times'].append(t1 - t0)

        # Standard RRT*
        rrt = RRTStar()
        t0 = time.perf_counter()
        rrt_path = rrt.plan(start, goal, grid)
        t1 = time.perf_counter()
        if rrt_path is not None:
            results['RRT*']['successes'] += 1
            results['RRT*']['lengths'].append(path_length(rrt_path))
        results['RRT*']['times'].append(t1 - t0)

        # Hybrid
        hybrid = HybridAStar()
        t0 = time.perf_counter()
        hybrid_path = hybrid.plan(start, goal, grid)
        t1 = time.perf_counter()
        if hybrid_path is not None:
            results['Hybrid']['successes'] += 1
            results['Hybrid']['lengths'].append(path_length(hybrid_path))
        results['Hybrid']['times'].append(t1 - t0)

        print(f'Trial {trial + 1}/{n_trials} done', end='\r')

    print()
    return results


def print_summary(results, n_trials):
    print(f'\n{"=" * 65}')
    print(f'INDEPENDENT REPRODUCIBILITY CHECK — {n_trials} trials, obstacle density 0.20')
    print(f'(see module docstring: not an exact re-run of the original thesis experiment)')
    print(f'{"=" * 65}')
    print(f'{"Algorithm":<10} {"Success":<10} {"Avg Length":<14} {"Avg Time (s)":<14}')
    print('-' * 65)

    rrt_avg_length = None
    for name in ['A*', 'RRT*', 'Hybrid']:
        r = results[name]
        success_rate = 100 * r['successes'] / n_trials
        avg_len = np.mean(r['lengths']) if r['lengths'] else float('nan')
        avg_time = np.mean(r['times'])
        print(f'{name:<10} {success_rate:>6.1f}%   {avg_len:>10.2f}    {avg_time:>10.4f}')
        if name == 'RRT*':
            rrt_avg_length = avg_len

    print('-' * 65)
    if rrt_avg_length and results['Hybrid']['lengths']:
        hybrid_avg = np.mean(results['Hybrid']['lengths'])
        improvement = 100 * (rrt_avg_length - hybrid_avg) / rrt_avg_length
        print(f'Hybrid vs RRT* path-length improvement (this run): {improvement:.2f}%')
    print(f'{"=" * 65}\n')


if __name__ == '__main__':
    results = run_benchmark(n_trials=50, obstacle_prob=0.20)
    print_summary(results, n_trials=50)
