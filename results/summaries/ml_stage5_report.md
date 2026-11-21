# Stage 5 report
## A. 50x50 test maps (ml_main)

### random_d0.10
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 100/100 | 0% | 64.8 | +1.10% | 95° | 12 ms |
| hybrid_fallback | 100/100 | 0% | 64.4 | +0.55% | 85° | 478 ms |
| hybrid_tight | 100/100 | 0% | 64.4 | +0.48% | 73° | 494 ms |
| hybrid_tight_x2 | 100/100 | 0% | 64.3 | +0.39% | 74° | 2017 ms |
| learned_corridor | 100/100 | 0% | 64.2 | +0.24% | 101° | 572 ms |
| learned_tight | 100/100 | 0% | 64.2 | +0.16% | 87° | 575 ms |
| learned_tight_x2 | 100/100 | 0% | 64.1 | +0.11% | 81° | 2284 ms |

### random_d0.20
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 99/100 | 0% | 67.4 | +2.72% | 261° | 15 ms |
| hybrid_fallback | 99/100 | 8% | 67.3 | +2.49% | 345° | 280 ms |
| hybrid_tight | 99/100 | 4% | 66.7 | +1.66% | 242° | 294 ms |
| hybrid_tight_x2 | 99/100 | 1% | 66.4 | +1.27% | 243° | 1497 ms |
| learned_corridor | 99/100 | 9% | 66.8 | +1.84% | 370° | 366 ms |
| learned_tight | 99/100 | 3% | 66.2 | +0.92% | 278° | 368 ms |
| learned_tight_x2 | 99/100 | 0% | 65.9 | +0.50% | 258° | 1761 ms |

### random_d0.30
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 98/100 | 0% | 73.6 | +3.97% | 493° | 18 ms |
| hybrid_fallback | 98/100 | 47% | 76.8 | +8.45% | 1040° | 133 ms |
| hybrid_tight | 98/100 | 51% | 73.2 | +3.41% | 507° | 145 ms |
| hybrid_tight_x2 | 98/100 | 0% | 72.2 | +1.99% | 469° | 929 ms |
| learned_corridor | 98/100 | 51% | 76.9 | +8.62% | 1110° | 175 ms |
| learned_tight | 98/100 | 56% | 73.1 | +3.21% | 526° | 197 ms |
| learned_tight_x2 | 98/100 | 10% | 72.4 | +2.24% | 512° | 1074 ms |

### narrow
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 100/100 | 0% | 83.2 | +2.19% | 377° | 36 ms |
| hybrid_fallback | 100/100 | 15% | 83.7 | +2.55% | 452° | 248 ms |
| hybrid_tight | 100/100 | 14% | 82.8 | +1.64% | 386° | 259 ms |
| hybrid_tight_x2 | 100/100 | 1% | 82.3 | +1.00% | 374° | 1370 ms |
| learned_corridor | 100/100 | 24% | 84.0 | +2.70% | 472° | 284 ms |
| learned_tight | 100/100 | 22% | 82.6 | +1.38% | 383° | 288 ms |
| learned_tight_x2 | 100/100 | 2% | 82.0 | +0.75% | 374° | 1505 ms |

### maze
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 50/50 | 0% | 106.0 | - | 735° | 20 ms |
| hybrid_fallback | 50/50 | 40% | 109.3 | - | 951° | 132 ms |
| hybrid_tight | 50/50 | 44% | 105.5 | - | 737° | 158 ms |
| hybrid_tight_x2 | 50/50 | 16% | 104.8 | - | 731° | 918 ms |
| learned_corridor | 50/50 | 84% | 111.5 | - | 1034° | 96 ms |
| learned_tight | 50/50 | 84% | 106.2 | - | 749° | 107 ms |
| learned_tight_x2 | 50/50 | 56% | 106.6 | - | 749° | 447 ms |

## A. Paired tests

**learned_tight vs hybrid_tight** (negative % = learned_tight is lower; Holm-adjusted over scenarios)
| scenario | success (only ref / only learned) | length | turning | time |
|---|---|---:|---:|---:|
| random_d0.10 | 0 / 0 ns | -0.3% *** | +18.3% * | +19.2% *** |
| random_d0.20 | 0 / 0 ns | -0.7% *** | +14.6% *** | +24.6% *** |
| random_d0.30 | 0 / 0 ns | -0.2% ns | +3.7% ns | +35.6% *** |
| narrow | 0 / 0 ns | -0.2% ** | -0.8% ns | +22.0% *** |
| maze | 0 / 0 ns | +0.6% *** | +1.6% ns | -30.2% *** |

**learned_tight vs theta_star_tight** (negative % = learned_tight is lower; Holm-adjusted over scenarios)
| scenario | success (only ref / only learned) | length | turning | time |
|---|---|---:|---:|---:|
| random_d0.10 | 0 / 0 ns | -0.9% *** | -8.8% ns | +4287.3% *** |
| random_d0.20 | 0 / 0 ns | -1.8% *** | +6.2% ns | +2272.9% *** |
| random_d0.30 | 0 / 0 ns | -0.7% *** | +6.8% * | +1036.7% *** |
| narrow | 0 / 0 ns | -0.6% *** | +1.5% ns | +847.4% *** |
| maze | 0 / 0 ns | +0.2% ns | +2.0% ns | +434.5% *** |

## B. Search budget (ml_budget)

### random_d0.20: raw success (no fallback) / median time
| planner | 300 | 600 | 1200 | 1800 | 3600 |
|---|---:|---:|---:|---:|---:|
| rrt_star | 0% / 2 ms | 8% / 6 ms | 28% / 23 ms | 56% / 53 ms | 78% / 282 ms |
| hybrid | 2% / 7 ms | 20% / 19 ms | 80% / 108 ms | 96% / 284 ms | 99% / 1471 ms |
| learned | 2% / 15 ms | 17% / 33 ms | 80% / 153 ms | 96% / 372 ms | 99% / 1754 ms |

### random_d0.30: raw success (no fallback) / median time
| planner | 300 | 600 | 1200 | 1800 | 3600 |
|---|---:|---:|---:|---:|---:|
| rrt_star | 0% / 1 ms | 0% / 3 ms | 0% / 6 ms | 1% / 11 ms | 9% / 52 ms |
| hybrid | 0% / 5 ms | 0% / 11 ms | 20% / 51 ms | 57% / 151 ms | 96% / 853 ms |
| learned | 0% / 12 ms | 1% / 19 ms | 15% / 70 ms | 43% / 170 ms | 91% / 974 ms |

### narrow: raw success (no fallback) / median time
| planner | 300 | 600 | 1200 | 1800 | 3600 |
|---|---:|---:|---:|---:|---:|
| rrt_star | 2% / 2 ms | 3% / 6 ms | 10% / 18 ms | 24% / 38 ms | 65% / 204 ms |
| hybrid | 2% / 8 ms | 21% / 20 ms | 67% / 88 ms | 83% / 251 ms | 100% / 1299 ms |
| learned | 4% / 15 ms | 16% / 28 ms | 60% / 111 ms | 83% / 304 ms | 96% / 1522 ms |

Figure: results/stage5_budget.png

## C. 100x100 maps, never trained on (ml_big)

### big_d0.20
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 50/50 | 0% | 140.8 | +2.56% | 475° | 60 ms |
| hybrid_tight | 50/50 | 94% | 140.6 | +2.40% | 503° | 100 ms |
| hybrid_tight_x4 | 50/50 | 0% | 139.0 | +1.27% | 405° | 2426 ms |
| learned_tight | 50/50 | 92% | 141.6 | +3.17% | 524° | 153 ms |
| learned_tight_x4 | 50/50 | 22% | 153.8 | +12.03% | 660° | 1932 ms |

### big_d0.30
| planner | success | fallback | length | above best | turning | median time |
|---|---:|---:|---:|---:|---:|---:|
| theta_star_tight | 49/50 | 0% | 150.7 | +3.59% | 900° | 73 ms |
| hybrid_tight | 49/50 | 98% | 151.1 | +3.87% | 936° | 83 ms |
| hybrid_tight_x4 | 49/50 | 36% | 149.6 | +2.81% | 873° | 1097 ms |
| learned_tight | 49/50 | 98% | 151.2 | +3.94% | 941° | 127 ms |
| learned_tight_x4 | 49/50 | 92% | 151.1 | +3.88% | 944° | 1089 ms |

## C. Paired tests

**learned_tight_x4 vs hybrid_tight_x4** (negative % = learned_tight_x4 is lower; Holm-adjusted over scenarios)
| scenario | success (only ref / only learned) | length | turning | time |
|---|---|---:|---:|---:|
| big_d0.20 | 0 / 0 ns | +10.6% *** | +63.1% *** | -17.5% ** |
| big_d0.30 | 0 / 0 ns | +1.0% *** | +8.1% *** | -5.8% ns |

**learned_tight vs hybrid_tight** (negative % = learned_tight is lower; Holm-adjusted over scenarios)
| scenario | success (only ref / only learned) | length | turning | time |
|---|---|---:|---:|---:|
| big_d0.20 | 0 / 0 ns | +0.7% ns | +4.3% ns | +49.7% *** |
| big_d0.30 | 0 / 0 ns | +0.1% ns | +0.5% ns | +54.2% *** |

**learned_tight vs theta_star_tight** (negative % = learned_tight is lower; Holm-adjusted over scenarios)
| scenario | success (only ref / only learned) | length | turning | time |
|---|---|---:|---:|---:|
| big_d0.20 | 0 / 0 ns | +0.6% ns | +10.5% *** | +156.5% *** |
| big_d0.30 | 0 / 0 ns | +0.3% ** | +4.6% *** | +82.5% *** |
