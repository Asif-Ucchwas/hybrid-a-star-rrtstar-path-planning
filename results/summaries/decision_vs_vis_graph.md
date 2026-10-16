# Benchmark summary

- config: `decision.json`  commit: `a8224e80be13ac527288eb88c24d4bc4d313bd35`
- machine: Intel(R) Core(TM) Ultra 7 265K (20 cores), Python 3.12.3, workers=1
- collision rule: **exact**, margin 0.05
- clean timing: **True** (timings are only publishable when workers=1 on an idle machine)

## maze

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 20 | 100.0 (84-100) | 8.9 / 8.8 / 13.3 | 114.48 [98.91, 134.21] | 0.981 | 1136 | 1.37 | 0 |
| hybrid_fallback | 20 | 100.0 (84-100) | 173.3 / 155.9 / 299.4 | 111.77 [95.41, 132.17] | 0.951 | 1014 | 1.37 | 0 |
| hybrid_tight | 20 | 100.0 (84-100) | 180.9 / 174.7 / 296.7 | 107.64 [93.17, 126.05] | 0.924 | 787 | 1.36 | 0 |
| hybrid_tight_x2 | 20 | 100.0 (84-100) | 876.2 / 1001.1 / 1342.3 | 107.14 [92.51, 125.78] | 0.918 | 781 | 1.35 | 0 |
| theta_star_cc | 20 | 100.0 (84-100) | 20.8 / 19.9 / 32.9 | 112.19 [97.21, 131.26] | 0.963 | 889 | 1.42 | 0 |
| theta_star_tight | 20 | 100.0 (84-100) | 26.4 / 24.0 / 44.2 | 108.09 [93.68, 126.39] | 0.929 | 781 | 1.37 | 0 |

## narrow

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 20 | 100.0 (84-100) | 12.9 / 13.7 / 16.9 | 85.78 [78.30, 93.62] | 0.958 | 560 | 1.91 | 0 |
| hybrid_fallback | 20 | 100.0 (84-100) | 279.1 / 253.0 / 500.3 | 83.16 [75.61, 91.05] | 0.927 | 437 | 1.90 | 0 |
| hybrid_tight | 20 | 100.0 (84-100) | 289.5 / 277.4 / 517.4 | 82.00 [75.01, 89.24] | 0.916 | 364 | 1.88 | 0 |
| hybrid_tight_x2 | 20 | 100.0 (84-100) | 1414.5 / 1366.7 / 2169.0 | 81.57 [74.64, 88.71] | 0.912 | 361 | 1.87 | 0 |
| theta_star_cc | 20 | 100.0 (84-100) | 37.2 / 39.9 / 50.1 | 84.48 [77.34, 91.92] | 0.944 | 440 | 1.94 | 0 |
| theta_star_tight | 20 | 100.0 (84-100) | 39.8 / 42.4 / 54.1 | 82.56 [75.70, 89.72] | 0.923 | 366 | 1.91 | 0 |
| vis_graph | 20 | 100.0 (84-100) | 3375.2 / 3802.9 / 5872.0 | 80.65 [73.97, 87.61] | 0.902 | 350 | 1.86 | 0 |

Paired comparison against `vis_graph` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 20 | - | - | 1.0000 | ns |
| astar_smooth | length | 20 | 6.4 | 4.329 | 0.0000 | *** |
| astar_smooth | time_s | 20 | -99.6 | -3.787 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 20 | 60.0 | 168.750 | 0.0000 | *** |
| astar_smooth | clearance_mean | 20 | 2.8 | 0.054 | 0.0577 | ns |
| hybrid_fallback | success | 20 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 20 | 3.1 | 1.373 | 0.0000 | *** |
| hybrid_fallback | time_s | 20 | -91.7 | -3.563 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 20 | 24.8 | 51.540 | 0.0000 | *** |
| hybrid_fallback | clearance_mean | 20 | 2.1 | 0.035 | 0.0332 | * |
| hybrid_tight | success | 20 | - | - | 1.0000 | ns |
| hybrid_tight | length | 20 | 1.7 | 1.173 | 0.0000 | *** |
| hybrid_tight | time_s | 20 | -91.4 | -3.617 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 20 | 4.0 | 12.689 | 0.0010 | *** |
| hybrid_tight | clearance_mean | 20 | 1.0 | 0.022 | 0.0592 | ns |
| hybrid_tight_x2 | success | 20 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 20 | 1.1 | 0.796 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 20 | -58.1 | -2.349 | 0.0009 | *** |
| hybrid_tight_x2 | turn_total_deg | 20 | 3.2 | 7.754 | 0.0001 | *** |
| hybrid_tight_x2 | clearance_mean | 20 | 0.8 | 0.021 | 0.0592 | ns |
| theta_star_cc | success | 20 | - | - | 1.0000 | ns |
| theta_star_cc | length | 20 | 4.8 | 3.809 | 0.0000 | *** |
| theta_star_cc | time_s | 20 | -98.9 | -3.757 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 20 | 25.6 | 75.563 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 20 | 4.3 | 0.073 | 0.0001 | *** |
| theta_star_tight | success | 20 | - | - | 1.0000 | ns |
| theta_star_tight | length | 20 | 2.4 | 1.929 | 0.0000 | *** |
| theta_star_tight | time_s | 20 | -98.8 | -3.754 | 0.0000 | *** |
| theta_star_tight | turn_total_deg | 20 | 4.4 | 13.073 | 0.0010 | ** |
| theta_star_tight | clearance_mean | 20 | 2.6 | 0.033 | 0.0060 | ** |

## random_d0.10

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 30 | 100.0 (89-100) | 7.9 / 8.0 / 10.0 | 65.47 [65.18, 65.76] | 0.958 | 204 | 1.79 | 0 |
| hybrid_fallback | 30 | 100.0 (89-100) | 478.2 / 482.6 / 553.5 | 64.34 [64.18, 64.53] | 0.941 | 79 | 1.73 | 0 |
| hybrid_tight | 30 | 100.0 (89-100) | 457.7 / 489.1 / 541.5 | 64.30 [64.13, 64.50] | 0.941 | 61 | 1.73 | 0 |
| hybrid_tight_x2 | 30 | 100.0 (89-100) | 1994.6 / 1988.9 / 2126.3 | 64.25 [64.10, 64.44] | 0.940 | 66 | 1.72 | 0 |
| theta_star_cc | 30 | 100.0 (89-100) | 11.5 / 11.6 / 14.7 | 65.46 [65.24, 65.68] | 0.958 | 194 | 1.77 | 0 |
| theta_star_tight | 30 | 100.0 (89-100) | 13.6 / 13.5 / 18.1 | 64.61 [64.44, 64.79] | 0.945 | 81 | 1.75 | 0 |
| vis_graph | 30 | 100.0 (89-100) | 47.7 / 39.9 / 105.8 | 63.97 [63.91, 64.03] | 0.936 | 66 | 1.66 | 0 |

Paired comparison against `vis_graph` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 30 | 2.4 | 1.434 | 0.0000 | *** |
| astar_smooth | time_s | 30 | -83.5 | -0.032 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 30 | 207.7 | 141.588 | 0.0000 | *** |
| astar_smooth | clearance_mean | 30 | 7.8 | 0.120 | 0.0000 | *** |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 30 | 0.6 | 0.295 | 0.0000 | *** |
| hybrid_fallback | time_s | 30 | 901.8 | 0.434 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 30 | 19.7 | 6.534 | 0.2667 | ns |
| hybrid_fallback | clearance_mean | 30 | 4.1 | 0.052 | 0.0077 | ** |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 30 | 0.5 | 0.180 | 0.0000 | *** |
| hybrid_tight | time_s | 30 | 858.8 | 0.441 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 30 | -8.1 | 1.485 | 1.0000 | ns |
| hybrid_tight | clearance_mean | 30 | 3.9 | 0.033 | 0.0093 | ** |
| hybrid_tight_x2 | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 30 | 0.4 | 0.147 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 30 | 4078.7 | 1.941 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 30 | -0.2 | 7.903 | 1.0000 | ns |
| hybrid_tight_x2 | clearance_mean | 30 | 3.6 | 0.023 | 0.0093 | ** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 30 | 2.3 | 1.377 | 0.0000 | *** |
| theta_star_cc | time_s | 30 | -75.8 | -0.028 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 30 | 193.3 | 108.602 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 30 | 6.2 | 0.079 | 0.0008 | *** |
| theta_star_tight | success | 30 | - | - | 1.0000 | ns |
| theta_star_tight | length | 30 | 1.0 | 0.587 | 0.0000 | *** |
| theta_star_tight | time_s | 30 | -71.6 | -0.026 | 0.0000 | *** |
| theta_star_tight | turn_total_deg | 30 | 22.3 | 9.262 | 0.2667 | ns |
| theta_star_tight | clearance_mean | 30 | 4.9 | 0.064 | 0.0058 | ** |

## random_d0.20

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 30 | 96.7 (83-99) | 9.5 / 9.4 / 12.2 | 70.42 [69.54, 71.31] | 0.954 | 743 | 1.37 | 0 |
| hybrid_fallback | 30 | 96.7 (83-99) | 291.9 / 285.6 / 416.9 | 67.42 [66.35, 68.56] | 0.913 | 380 | 1.33 | 0 |
| hybrid_tight | 30 | 96.7 (83-99) | 282.3 / 274.2 / 403.6 | 66.53 [65.93, 67.21] | 0.901 | 237 | 1.32 | 0 |
| hybrid_tight_x2 | 30 | 96.7 (83-99) | 1360.9 / 1410.6 / 1721.6 | 66.31 [65.75, 66.92] | 0.898 | 244 | 1.31 | 0 |
| theta_star_cc | 30 | 96.7 (83-99) | 14.8 / 13.7 / 20.7 | 70.41 [69.61, 71.25] | 0.954 | 654 | 1.37 | 0 |
| theta_star_tight | 30 | 96.7 (83-99) | 18.9 / 17.8 / 25.8 | 67.31 [66.61, 68.04] | 0.912 | 251 | 1.35 | 0 |
| vis_graph | 30 | 96.7 (83-99) | 458.5 / 348.2 / 948.3 | 65.45 [65.05, 65.90] | 0.887 | 211 | 1.27 | 0 |

Paired comparison against `vis_graph` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 29 | 7.6 | 5.094 | 0.0000 | *** |
| astar_smooth | time_s | 29 | -97.9 | -0.339 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 29 | 252.2 | 535.455 | 0.0000 | *** |
| astar_smooth | clearance_mean | 29 | 8.2 | 0.096 | 0.0000 | *** |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 29 | 3.0 | 1.071 | 0.0000 | *** |
| hybrid_fallback | time_s | 29 | -36.3 | -0.070 | 0.1125 | ns |
| hybrid_fallback | turn_total_deg | 29 | 80.0 | 89.611 | 0.0000 | *** |
| hybrid_fallback | clearance_mean | 29 | 5.2 | 0.056 | 0.0000 | *** |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 29 | 1.7 | 0.897 | 0.0000 | *** |
| hybrid_tight | time_s | 29 | -38.4 | -0.072 | 0.1125 | ns |
| hybrid_tight | turn_total_deg | 29 | 12.3 | 35.954 | 0.0070 | ** |
| hybrid_tight | clearance_mean | 29 | 3.8 | 0.030 | 0.0000 | *** |
| hybrid_tight_x2 | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 29 | 1.3 | 0.607 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 29 | 196.8 | 0.912 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 29 | 15.7 | 32.053 | 0.0070 | ** |
| hybrid_tight_x2 | clearance_mean | 29 | 3.2 | 0.031 | 0.0000 | *** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 29 | 7.6 | 5.060 | 0.0000 | *** |
| theta_star_cc | time_s | 29 | -96.8 | -0.335 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 29 | 210.2 | 413.133 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 29 | 8.2 | 0.090 | 0.0000 | *** |
| theta_star_tight | success | 30 | - | - | 1.0000 | ns |
| theta_star_tight | length | 29 | 2.9 | 1.720 | 0.0000 | *** |
| theta_star_tight | time_s | 29 | -95.9 | -0.330 | 0.0000 | *** |
| theta_star_tight | turn_total_deg | 29 | 18.8 | 33.253 | 0.0070 | ** |
| theta_star_tight | clearance_mean | 29 | 6.3 | 0.060 | 0.0000 | *** |

## random_d0.30

| planner | n | success % (95% CI) | time ms mean / median / p95 | length | length vs A* | turning deg | clearance | grazes obstacle cell % |
|---|---|---|---|---|---|---|---|---|
| astar_smooth | 30 | 96.7 (83-99) | 10.3 / 10.3 / 12.2 | 80.69 [79.29, 82.13] | 0.971 | 1424 | 1.22 | 0 |
| hybrid_fallback | 30 | 96.7 (83-99) | 160.5 / 138.3 / 261.9 | 76.92 [75.18, 78.81] | 0.926 | 905 | 1.20 | 0 |
| hybrid_tight | 30 | 96.7 (83-99) | 154.0 / 147.7 / 238.8 | 74.10 [72.75, 75.53] | 0.892 | 505 | 1.19 | 0 |
| hybrid_tight_x2 | 30 | 96.7 (83-99) | 889.1 / 898.5 / 1347.0 | 72.97 [71.62, 74.40] | 0.879 | 466 | 1.18 | 0 |
| theta_star_cc | 30 | 96.7 (83-99) | 16.2 / 16.3 / 21.1 | 79.87 [78.55, 81.29] | 0.962 | 1130 | 1.23 | 0 |
| theta_star_tight | 30 | 96.7 (83-99) | 23.7 / 23.5 / 30.1 | 74.40 [72.95, 75.88] | 0.896 | 476 | 1.20 | 0 |
| vis_graph | 30 | 96.7 (83-99) | 3252.1 / 3224.2 / 5927.0 | 71.20 [70.04, 72.47] | 0.857 | 449 | 1.14 | 0 |

Paired comparison against `vis_graph` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 29 | 13.3 | 9.670 | 0.0000 | *** |
| astar_smooth | time_s | 29 | -99.7 | -3.215 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 29 | 217.3 | 966.357 | 0.0000 | *** |
| astar_smooth | clearance_mean | 29 | 6.6 | 0.066 | 0.0000 | *** |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 29 | 8.0 | 4.156 | 0.0000 | *** |
| hybrid_fallback | time_s | 29 | -95.1 | -3.058 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 29 | 101.6 | 299.551 | 0.0000 | *** |
| hybrid_fallback | clearance_mean | 29 | 5.2 | 0.046 | 0.0000 | *** |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 29 | 4.1 | 2.740 | 0.0000 | *** |
| hybrid_tight | time_s | 29 | -95.3 | -3.066 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 29 | 12.4 | 91.146 | 0.0363 | * |
| hybrid_tight | clearance_mean | 29 | 4.4 | 0.040 | 0.0000 | *** |
| hybrid_tight_x2 | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 29 | 2.5 | 1.471 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 29 | -72.7 | -2.360 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 29 | 3.8 | 54.641 | 0.2017 | ns |
| hybrid_tight_x2 | clearance_mean | 29 | 3.2 | 0.022 | 0.0000 | *** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 29 | 12.2 | 8.989 | 0.0000 | *** |
| theta_star_cc | time_s | 29 | -99.5 | -3.210 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 29 | 151.8 | 630.588 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 29 | 7.5 | 0.080 | 0.0000 | *** |
| theta_star_tight | success | 30 | - | - | 1.0000 | ns |
| theta_star_tight | length | 29 | 4.5 | 3.508 | 0.0000 | *** |
| theta_star_tight | time_s | 29 | -99.3 | -3.202 | 0.0000 | *** |
| theta_star_tight | turn_total_deg | 29 | 6.1 | 48.155 | 0.2017 | ns |
| theta_star_tight | clearance_mean | 29 | 5.1 | 0.057 | 0.0000 | *** |
