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

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 20 | - | - | 1.0000 | ns |
| astar_smooth | length | 20 | 5.9 | 5.709 | 0.0000 | *** |
| astar_smooth | time_s | 20 | -66.2 | -0.016 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 20 | 45.4 | 323.590 | 0.0000 | *** |
| astar_smooth | clearance_mean | 20 | 0.3 | 0.012 | 1.0000 | ns |
| hybrid_fallback | success | 20 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 20 | 3.4 | 0.773 | 0.0583 | ns |
| hybrid_fallback | time_s | 20 | 555.6 | 0.132 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 20 | 29.8 | 97.874 | 0.0000 | *** |
| hybrid_fallback | clearance_mean | 20 | 0.1 | -0.002 | 1.0000 | ns |
| hybrid_tight | success | 20 | - | - | 1.0000 | ns |
| hybrid_tight | length | 20 | -0.4 | -0.279 | 0.0315 | * |
| hybrid_tight | time_s | 20 | 584.6 | 0.148 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 20 | 0.7 | 6.146 | 0.7093 | ns |
| hybrid_tight | clearance_mean | 20 | -0.4 | -0.005 | 0.4095 | ns |
| hybrid_tight_x2 | success | 20 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 20 | -0.9 | -1.018 | 0.0029 | ** |
| hybrid_tight_x2 | time_s | 20 | 3215.3 | 0.976 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 20 | -0.1 | -4.234 | 0.7093 | ns |
| hybrid_tight_x2 | clearance_mean | 20 | -1.1 | -0.016 | 0.0171 | * |
| theta_star_cc | success | 20 | - | - | 1.0000 | ns |
| theta_star_cc | length | 20 | 3.8 | 4.250 | 0.0000 | *** |
| theta_star_cc | time_s | 20 | -21.1 | -0.004 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 20 | 13.8 | 109.305 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 20 | 3.9 | 0.053 | 0.0000 | *** |

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

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 20 | - | - | 1.0000 | ns |
| astar_smooth | length | 20 | 3.9 | 3.161 | 0.0000 | *** |
| astar_smooth | time_s | 20 | -67.6 | -0.028 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 20 | 53.2 | 144.234 | 0.0000 | *** |
| astar_smooth | clearance_mean | 20 | 0.2 | 0.012 | 1.0000 | ns |
| hybrid_fallback | success | 20 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 20 | 0.7 | 0.080 | 0.7285 | ns |
| hybrid_fallback | time_s | 20 | 601.1 | 0.211 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 20 | 19.5 | 38.303 | 0.0043 | ** |
| hybrid_fallback | clearance_mean | 20 | -0.5 | -0.008 | 1.0000 | ns |
| hybrid_tight | success | 20 | - | - | 1.0000 | ns |
| hybrid_tight | length | 20 | -0.7 | -0.323 | 0.0073 | ** |
| hybrid_tight | time_s | 20 | 627.1 | 0.234 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 20 | -0.4 | -2.961 | 0.8609 | ns |
| hybrid_tight | clearance_mean | 20 | -1.5 | -0.016 | 0.1087 | ns |
| hybrid_tight_x2 | success | 20 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 20 | -1.2 | -1.016 | 0.0001 | *** |
| hybrid_tight_x2 | time_s | 20 | 3453.2 | 1.319 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 20 | -1.1 | -5.900 | 0.8609 | ns |
| hybrid_tight_x2 | clearance_mean | 20 | -1.8 | -0.028 | 0.0859 | ns |
| theta_star_cc | success | 20 | - | - | 1.0000 | ns |
| theta_star_cc | length | 20 | 2.3 | 2.044 | 0.0004 | *** |
| theta_star_cc | time_s | 20 | -6.5 | -0.003 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 20 | 20.3 | 68.001 | 0.0007 | *** |
| theta_star_cc | clearance_mean | 20 | 1.6 | 0.030 | 0.0013 | ** |
| vis_graph | success | 20 | - | - | 1.0000 | ns |
| vis_graph | length | 20 | -2.3 | -1.929 | 0.0000 | *** |
| vis_graph | time_s | 20 | 8378.5 | 3.754 | 0.0000 | *** |
| vis_graph | turn_total_deg | 20 | -4.2 | -13.073 | 0.0041 | ** |
| vis_graph | clearance_mean | 20 | -2.5 | -0.033 | 0.0060 | ** |

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

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 30 | 1.3 | 0.719 | 0.0000 | *** |
| astar_smooth | time_s | 30 | -41.8 | -0.006 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 30 | 151.6 | 107.860 | 0.0000 | *** |
| astar_smooth | clearance_mean | 30 | 2.8 | 0.047 | 0.0062 | ** |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 30 | -0.4 | -0.252 | 0.0000 | *** |
| hybrid_fallback | time_s | 30 | 3424.4 | 0.472 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 30 | -2.1 | -0.714 | 0.7766 | ns |
| hybrid_fallback | clearance_mean | 30 | -0.8 | -0.013 | 0.3819 | ns |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 30 | -0.5 | -0.252 | 0.0000 | *** |
| hybrid_tight | time_s | 30 | 3273.1 | 0.476 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 30 | -24.8 | -17.302 | 0.0266 | * |
| hybrid_tight | clearance_mean | 30 | -1.0 | -0.015 | 0.3819 | ns |
| hybrid_tight_x2 | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 30 | -0.6 | -0.312 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 30 | 14600.3 | 1.976 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 30 | -18.4 | -17.876 | 0.0930 | ns |
| hybrid_tight_x2 | clearance_mean | 30 | -1.2 | -0.029 | 0.2758 | ns |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 30 | 1.3 | 0.805 | 0.0000 | *** |
| theta_star_cc | time_s | 30 | -15.0 | -0.002 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 30 | 139.9 | 97.029 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 30 | 1.2 | 0.021 | 0.0062 | ** |
| vis_graph | success | 30 | - | - | 1.0000 | ns |
| vis_graph | length | 30 | -1.0 | -0.587 | 0.0000 | *** |
| vis_graph | time_s | 30 | 251.8 | 0.026 | 0.0000 | *** |
| vis_graph | turn_total_deg | 30 | -18.2 | -9.262 | 0.1465 | ns |
| vis_graph | clearance_mean | 30 | -4.7 | -0.064 | 0.0062 | ** |

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

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 29 | 4.6 | 2.928 | 0.0000 | *** |
| astar_smooth | time_s | 29 | -49.5 | -0.009 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 29 | 196.5 | 477.961 | 0.0000 | *** |
| astar_smooth | clearance_mean | 29 | 1.8 | 0.037 | 0.0054 | ** |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 29 | 0.2 | -0.623 | 0.1433 | ns |
| hybrid_fallback | time_s | 29 | 1446.1 | 0.268 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 29 | 51.5 | 17.122 | 0.0730 | ns |
| hybrid_fallback | clearance_mean | 29 | -1.1 | 0.000 | 0.4294 | ns |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 29 | -1.2 | -0.838 | 0.0000 | *** |
| hybrid_tight | time_s | 29 | 1395.4 | 0.259 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 29 | -5.5 | -19.741 | 0.3952 | ns |
| hybrid_tight | clearance_mean | 29 | -2.3 | -0.018 | 0.0055 | ** |
| hybrid_tight_x2 | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 29 | -1.5 | -1.000 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 29 | 7109.0 | 1.397 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 29 | -2.6 | -14.697 | 0.3952 | ns |
| hybrid_tight_x2 | clearance_mean | 29 | -2.9 | -0.030 | 0.0001 | *** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 29 | 4.6 | 2.928 | 0.0000 | *** |
| theta_star_cc | time_s | 29 | -21.6 | -0.004 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 29 | 161.1 | 387.436 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 29 | 1.8 | 0.021 | 0.0001 | *** |
| vis_graph | success | 30 | - | - | 1.0000 | ns |
| vis_graph | length | 29 | -2.8 | -1.720 | 0.0000 | *** |
| vis_graph | time_s | 29 | 2328.9 | 0.330 | 0.0000 | *** |
| vis_graph | turn_total_deg | 29 | -15.8 | -33.253 | 0.0094 | ** |
| vis_graph | clearance_mean | 29 | -5.9 | -0.060 | 0.0000 | *** |

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

Paired comparison against `theta_star_tight` (same maps; Holm-adjusted p):

| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |
|---|---|---|---|---|---|---|
| astar_smooth | success | 30 | - | - | 1.0000 | ns |
| astar_smooth | length | 29 | 8.5 | 6.202 | 0.0000 | *** |
| astar_smooth | time_s | 29 | -56.6 | -0.013 | 0.0000 | *** |
| astar_smooth | turn_total_deg | 29 | 199.0 | 958.593 | 0.0000 | *** |
| astar_smooth | clearance_mean | 29 | 1.5 | 0.025 | 0.0340 | * |
| hybrid_fallback | success | 30 | - | - | 1.0000 | ns |
| hybrid_fallback | length | 29 | 3.4 | 0.695 | 0.0076 | ** |
| hybrid_fallback | time_s | 29 | 578.3 | 0.114 | 0.0000 | *** |
| hybrid_fallback | turn_total_deg | 29 | 90.0 | 299.409 | 0.0000 | *** |
| hybrid_fallback | clearance_mean | 29 | 0.1 | 0.009 | 0.7493 | ns |
| hybrid_tight | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight | length | 29 | -0.4 | -0.185 | 0.3357 | ns |
| hybrid_tight | time_s | 29 | 551.1 | 0.118 | 0.0000 | *** |
| hybrid_tight | turn_total_deg | 29 | 5.9 | 24.904 | 0.3026 | ns |
| hybrid_tight | clearance_mean | 29 | -0.6 | -0.002 | 0.3657 | ns |
| hybrid_tight_x2 | success | 30 | - | - | 1.0000 | ns |
| hybrid_tight_x2 | length | 29 | -1.9 | -1.087 | 0.0000 | *** |
| hybrid_tight_x2 | time_s | 29 | 3658.1 | 0.877 | 0.0000 | *** |
| hybrid_tight_x2 | turn_total_deg | 29 | -2.2 | -5.510 | 0.3927 | ns |
| hybrid_tight_x2 | clearance_mean | 29 | -1.7 | -0.019 | 0.0043 | ** |
| theta_star_cc | success | 30 | - | - | 1.0000 | ns |
| theta_star_cc | length | 29 | 7.3 | 5.256 | 0.0000 | *** |
| theta_star_cc | time_s | 29 | -31.6 | -0.007 | 0.0000 | *** |
| theta_star_cc | turn_total_deg | 29 | 137.3 | 618.150 | 0.0000 | *** |
| theta_star_cc | clearance_mean | 29 | 2.4 | 0.027 | 0.0000 | *** |
| vis_graph | success | 30 | - | - | 1.0000 | ns |
| vis_graph | length | 29 | -4.3 | -3.508 | 0.0000 | *** |
| vis_graph | time_s | 29 | 13646.0 | 3.202 | 0.0000 | *** |
| vis_graph | turn_total_deg | 29 | -5.8 | -48.155 | 0.3026 | ns |
| vis_graph | clearance_mean | 29 | -4.8 | -0.057 | 0.0000 | *** |
