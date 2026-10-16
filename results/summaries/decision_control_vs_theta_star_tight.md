# Benchmark summary

- config: `decision_control.json`  commit: `a8224e80be13ac527288eb88c24d4bc4d313bd35`
- machine: Intel(R) Core(TM) Ultra 7 265K (20 cores), Python 3.12.3, workers=1
- collision rule: **sampled**
- clean timing: **True** (timings are only publishable when workers=1 on an idle machine)

## random_d0.10

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 30 | 100.0 (89-100) | 2.0 / 1.9 / 2.7 | 64.21 [64.09, 64.34] | 0.990 | 136 | 1.65 | 73 |
| hybrid_fallback | 30 | 100.0 (89-100) | 188.5 / 184.9 / 223.6 | 63.79 [63.76, 63.82] | 0.983 | 40 | 1.64 | 100 |
| hybrid_tight | 30 | 100.0 (89-100) | 187.5 / 192.4 / 218.1 | 63.75 [63.72, 63.77] | 0.983 | 24 | 1.62 | 100 |
| theta_star_cc | 30 | 100.0 (89-100) | 4.0 / 4.1 / 5.6 | 64.01 [63.94, 64.08] | 0.987 | 77 | 1.68 | 90 |
| theta_star_tight | 30 | 100.0 (89-100) | 4.4 / 4.3 / 6.2 | 63.93 [63.88, 63.98] | 0.986 | 59 | 1.67 | 97 |

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 30 | 0.4 | 0.193 | 0.0000 | *** |
| astar_smooth | time_s | 30 | -55.3 | -0.002 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 30 | 131.0 | 66.425 | 0.0000 | *** |
| astar_smooth | clearance_mean | 30 | -1.0 | -0.000 | 0.3389 | ns |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 30 | -0.2 | -0.132 | 0.0000 | *** |
| hybrid_fallback | time_s | 30 | 4179.2 | 0.182 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 30 | -32.3 | -10.912 | 0.0011 | ** |
| hybrid_fallback | clearance_mean | 30 | -2.0 | -0.011 | 0.0654 | ns |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 30 | -0.3 | -0.155 | 0.0000 | *** |
| hybrid_tight | time_s | 30 | 4156.5 | 0.187 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 30 | -59.9 | -31.050 | 0.0000 | *** |
| hybrid_tight | clearance_mean | 30 | -2.9 | -0.025 | 0.0038 | ** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 30 | 0.1 | 0.054 | 0.0000 | *** |
| theta_star_cc | time_s | 30 | -9.0 | -0.000 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 30 | 30.9 | 9.289 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 30 | 0.4 | 0.004 | 0.0134 | * |

## random_d0.20

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 30 | 100.0 (89-100) | 2.4 / 2.3 / 3.4 | 65.22 [65.01, 65.43] | 0.987 | 346 | 1.25 | 93 |
| hybrid_fallback | 30 | 100.0 (89-100) | 146.6 / 154.3 / 188.8 | 64.23 [64.09, 64.39] | 0.972 | 110 | 1.22 | 100 |
| hybrid_tight | 30 | 100.0 (89-100) | 150.3 / 155.3 / 188.0 | 64.13 [64.02, 64.25] | 0.971 | 72 | 1.21 | 100 |
| theta_star_cc | 30 | 100.0 (89-100) | 3.7 / 3.3 / 5.3 | 64.72 [64.56, 64.88] | 0.980 | 196 | 1.27 | 93 |
| theta_star_tight | 30 | 100.0 (89-100) | 4.3 / 4.1 / 6.2 | 64.44 [64.30, 64.58] | 0.976 | 127 | 1.25 | 100 |

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 30 | 1.2 | 0.737 | 0.0000 | *** |
| astar_smooth | time_s | 30 | -43.7 | -0.002 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 30 | 173.3 | 178.522 | 0.0000 | *** |
| astar_smooth | clearance_mean | 30 | 0.2 | 0.001 | 0.4522 | ns |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 30 | -0.3 | -0.192 | 0.0000 | *** |
| hybrid_fallback | time_s | 30 | 3303.5 | 0.150 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 30 | -13.2 | -13.484 | 0.0767 | ns |
| hybrid_fallback | clearance_mean | 30 | -2.7 | -0.027 | 0.0000 | *** |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 30 | -0.5 | -0.311 | 0.0000 | *** |
| hybrid_tight | time_s | 30 | 3389.5 | 0.150 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 30 | -43.2 | -46.622 | 0.0000 | *** |
| hybrid_tight | clearance_mean | 30 | -3.6 | -0.033 | 0.0000 | *** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 30 | 0.4 | 0.256 | 0.0000 | *** |
| theta_star_cc | time_s | 30 | -14.8 | -0.001 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 30 | 54.4 | 56.540 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 30 | 1.2 | 0.014 | 0.0000 | *** |

## random_d0.30

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 30 | 100.0 (89-100) | 3.3 / 3.3 / 4.3 | 67.53 [67.12, 67.99] | 0.989 | 752 | 1.11 | 100 |
| hybrid_fallback | 30 | 100.0 (89-100) | 101.1 / 102.5 / 162.3 | 65.92 [65.45, 66.41] | 0.965 | 393 | 1.06 | 100 |
| hybrid_tight | 30 | 100.0 (89-100) | 92.7 / 88.8 / 147.1 | 65.43 [65.07, 65.89] | 0.958 | 250 | 1.05 | 100 |
| theta_star_cc | 30 | 100.0 (89-100) | 4.5 / 4.1 / 6.4 | 66.55 [66.17, 66.98] | 0.975 | 455 | 1.11 | 100 |
| theta_star_tight | 30 | 100.0 (89-100) | 5.6 / 5.2 / 7.5 | 65.84 [65.49, 66.24] | 0.964 | 282 | 1.08 | 100 |

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 30 | 2.6 | 1.760 | 0.0000 | *** |
| astar_smooth | time_s | 30 | -40.8 | -0.002 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 30 | 167.0 | 473.118 | 0.0000 | *** |
| astar_smooth | clearance_mean | 30 | 2.0 | 0.024 | 0.0001 | *** |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 30 | 0.1 | -0.293 | 0.1642 | ns |
| hybrid_fallback | time_s | 30 | 1705.5 | 0.097 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 30 | 39.7 | 8.159 | 0.1607 | ns |
| hybrid_fallback | clearance_mean | 30 | -1.8 | -0.025 | 0.0020 | ** |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 30 | -0.6 | -0.404 | 0.0001 | *** |
| hybrid_tight | time_s | 30 | 1555.8 | 0.083 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 30 | -11.3 | -57.423 | 0.1607 | ns |
| hybrid_tight | clearance_mean | 30 | -2.9 | -0.029 | 0.0000 | *** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 30 | 1.1 | 0.722 | 0.0000 | *** |
| theta_star_cc | time_s | 30 | -18.9 | -0.001 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 30 | 61.4 | 168.264 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 30 | 2.5 | 0.032 | 0.0000 | *** |
