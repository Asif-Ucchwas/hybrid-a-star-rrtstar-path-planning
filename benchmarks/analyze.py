"""Turn ``raw.csv`` into tables, paired statistics and figures.

    python -m benchmarks.analyze results/paper_main
    python -m benchmarks.analyze results/sensitivity --sweep base_width

Outputs (in the same directory): summary.csv, comparisons.csv, summary.md and
figures/*.png.

Statistics:
* success rate with a 95% Wilson interval;
* mean metrics with 95% bootstrap intervals (successful runs only);
* paired comparisons against a reference planner on the same maps:
  exact McNemar test for success, Wilcoxon signed-rank for numeric metrics
  (maps where both planners succeeded), Holm-adjusted per scenario and metric.
"""

import argparse
import csv
import json
import math
import os
from collections import defaultdict

import numpy as np
from scipy import stats

NUMERIC = ["time_s", "cpu_s", "length", "astar_len", "turn_total_deg", "turn_mean_deg",
           "clearance_min", "clearance_mean", "strict_valid", "n_waypoints", "nodes"]
COMPARE_METRICS = ["length", "time_s", "turn_total_deg", "clearance_mean"]


def load_rows(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            for k in NUMERIC + ["x"]:
                try:
                    r[k] = float(r[k])
                except (TypeError, ValueError):
                    r[k] = float("nan")
            for k in ["success", "valid", "fallback", "seed"]:
                r[k] = int(float(r[k])) if r[k] != "" else 0
            rows.append(r)
    return rows


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def boot_ci(values, n_boot=2000, seed=0):
    v = np.asarray([x for x in values if not math.isnan(x)], dtype=float)
    if len(v) == 0:
        return float("nan"), float("nan"), float("nan")
    if len(v) == 1:
        return float(v[0]), float(v[0]), float(v[0])
    rng = np.random.default_rng(seed)
    means = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(axis=1)
    return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (same order as input)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def group(rows):
    g = defaultdict(list)
    for r in rows:
        g[(r["scenario"], r["planner"])].append(r)
    return g


def summarize(rows):
    out = []
    for (scenario, planner), rs in sorted(group(rows).items()):
        n = len(rs)
        ok = [r for r in rs if r["success"]]
        k = len(ok)
        lo, hi = wilson(k, n)
        row = {"scenario": scenario, "planner": planner, "family": rs[0]["family"],
               "x": rs[0]["x"], "n": n, "successes": k, "success_rate": k / n if n else float("nan"),
               "success_lo": lo, "success_hi": hi}
        errors = sum(1 for r in rs if r["error"])
        row["errors"] = errors
        for key in ["time_s", "cpu_s", "length", "turn_total_deg", "turn_mean_deg",
                    "clearance_min", "clearance_mean", "nodes"]:
            m, a, b = boot_ci([r[key] for r in ok])
            row[key] = m
            row[key + "_lo"] = a
            row[key + "_hi"] = b
        t = np.array([r["time_s"] for r in ok]) if ok else np.array([])
        row["time_median"] = float(np.median(t)) if len(t) else float("nan")
        row["time_p95"] = float(np.percentile(t, 95)) if len(t) else float("nan")
        ratios = [r["length"] / r["astar_len"] for r in ok
                  if r["astar_len"] and not math.isnan(r["astar_len"])]
        row["len_ratio_vs_astar"] = float(np.mean(ratios)) if ratios else float("nan")
        row["fallback_rate"] = float(np.mean([r["fallback"] for r in rs]))
        sv = [r["strict_valid"] for r in ok if not math.isnan(r["strict_valid"])]
        row["strict_valid_rate"] = float(np.mean(sv)) if sv else float("nan")
        out.append(row)
    return out


def compare(rows, ref_planner):
    by = defaultdict(dict)  # (scenario, planner) -> seed -> row
    for r in rows:
        by[(r["scenario"], r["planner"])][r["seed"]] = r
    scenarios = sorted({r["scenario"] for r in rows})
    planners = sorted({r["planner"] for r in rows})
    out = []
    for sc in scenarios:
        ref = by.get((sc, ref_planner))
        if not ref:
            continue
        per_metric = defaultdict(list)  # metric -> list of result dicts (for Holm)
        for p in planners:
            if p == ref_planner or (sc, p) not in by:
                continue
            cur = by[(sc, p)]
            seeds = sorted(set(ref) & set(cur))
            b = sum(1 for s in seeds if ref[s]["success"] and not cur[s]["success"])
            c = sum(1 for s in seeds if not ref[s]["success"] and cur[s]["success"])
            p_succ = stats.binomtest(min(b, c), b + c, 0.5).pvalue if b + c else 1.0
            out.append({"scenario": sc, "planner": p, "reference": ref_planner,
                        "metric": "success", "n_pairs": len(seeds),
                        "ref_only_success": b, "planner_only_success": c,
                        "median_diff": float("nan"), "mean_pct_diff": float("nan"),
                        "p": p_succ, "p_holm": float("nan")})
            for metric in COMPARE_METRICS:
                both = [s for s in seeds if ref[s]["success"] and cur[s]["success"]]
                d = np.array([cur[s][metric] - ref[s][metric] for s in both], dtype=float)
                rv = np.array([ref[s][metric] for s in both], dtype=float)
                if len(d) >= 1 and not np.all(d == 0):
                    try:
                        pv = float(stats.wilcoxon(d).pvalue)
                    except ValueError:
                        pv = 1.0
                else:
                    pv = 1.0
                res = {"scenario": sc, "planner": p, "reference": ref_planner, "metric": metric,
                       "n_pairs": len(both), "ref_only_success": "", "planner_only_success": "",
                       "median_diff": float(np.median(d)) if len(d) else float("nan"),
                       "mean_pct_diff": float(100 * d.mean() / rv.mean())
                       if len(d) and rv.mean() else float("nan"),
                       "p": pv, "p_holm": float("nan")}
                out.append(res)
                per_metric[metric].append(res)
            per_metric["success"].append(out[-len(COMPARE_METRICS) - 1])
        for metric, lst in per_metric.items():
            adj = holm([r["p"] for r in lst])
            for r, a in zip(lst, adj):
                r["p_holm"] = a
    return out


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def fmt(v, nd=2):
    return "-" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.{nd}f}"


def stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def markdown(summary, comps, meta, ref):
    lines = ["# Benchmark summary", ""]
    if meta:
        lines += [f"- config: `{meta.get('config_file')}`  commit: `{meta.get('git_commit')}`",
                  f"- machine: {meta.get('cpu')} ({meta.get('cpu_count')} cores), "
                  f"Python {meta.get('python')}, workers={meta.get('workers')}",
                  f"- clean timing: **{meta.get('clean_timing')}** "
                  "(timings are only publishable when workers=1 on an idle machine)", ""]
    for sc in sorted({s["scenario"] for s in summary}):
        lines += [f"## {sc}", "",
                  "| planner | n | success % (95% CI) | time ms mean / median / p95 | length | "
                  "length vs A* | turning deg | clearance | corner-clip free % |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for s in [s for s in summary if s["scenario"] == sc]:
            lines.append(
                f"| {s['planner']} | {s['n']} | {100 * s['success_rate']:.1f} "
                f"({100 * s['success_lo']:.0f}-{100 * s['success_hi']:.0f}) | "
                f"{fmt(1000 * s['time_s'], 1)} / {fmt(1000 * s['time_median'], 1)} / "
                f"{fmt(1000 * s['time_p95'], 1)} | {fmt(s['length'])} "
                f"[{fmt(s['length_lo'])}, {fmt(s['length_hi'])}] | {fmt(s['len_ratio_vs_astar'], 3)} | "
                f"{fmt(s['turn_total_deg'], 0)} | {fmt(s['clearance_mean'])} | "
                f"{fmt(100 * s['strict_valid_rate'], 0)} |")
        lines.append("")
        cs = [c for c in comps if c["scenario"] == sc]
        if cs:
            lines += [f"Paired comparison against `{ref}` (same maps; Holm-adjusted p):", "",
                      "| planner | metric | pairs | mean % diff | median diff | p (Holm) | sig |",
                      "|---|---|---|---|---|---|---|"]
            for c in cs:
                lines.append(f"| {c['planner']} | {c['metric']} | {c['n_pairs']} | "
                             f"{fmt(c['mean_pct_diff'], 1)} | {fmt(c['median_diff'], 3)} | "
                             f"{c['p_holm']:.4f} | {stars(c['p_holm'])} |")
            lines.append("")
    return "\n".join(lines)


def make_figures(summary, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(outdir, exist_ok=True)
    scenarios = sorted({s["scenario"] for s in summary})
    planners = sorted({s["planner"] for s in summary})
    idx = {(s["scenario"], s["planner"]): s for s in summary}
    width = 0.8 / max(len(planners), 1)
    cmap = plt.get_cmap("tab20")

    def grouped(metric, lo=None, hi=None, ylabel="", fname="", log=False, scale=1.0):
        fig, ax = plt.subplots(figsize=(max(7, 1.6 * len(scenarios) + 3), 4.2))
        for j, p in enumerate(planners):
            ys, err = [], [[], []]
            for sc in scenarios:
                s = idx.get((sc, p))
                y = s[metric] * scale if s else float("nan")
                ys.append(y)
                if s and lo and hi and not math.isnan(s[lo]):
                    err[0].append(max(y - s[lo] * scale, 0))
                    err[1].append(max(s[hi] * scale - y, 0))
                else:
                    err[0].append(0)
                    err[1].append(0)
            xs = np.arange(len(scenarios)) + j * width
            ax.bar(xs, ys, width, yerr=err, label=p, color=cmap(j % 20), capsize=1.5)
        ax.set_xticks(np.arange(len(scenarios)) + 0.4 - width / 2)
        ax.set_xticklabels(scenarios, rotation=20, ha="right")
        ax.set_ylabel(ylabel)
        if log:
            ax.set_yscale("log")
        ax.legend(fontsize=6, ncol=2)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, fname), dpi=200)
        plt.close(fig)

    grouped("success_rate", "success_lo", "success_hi", "success rate", "success.png")
    grouped("len_ratio_vs_astar", None, None, "path length / raw A* length", "length_ratio.png")
    grouped("time_s", "time_s_lo", "time_s_hi", "planning time (ms)", "time.png", True, 1000.0)
    grouped("turn_total_deg", "turn_total_deg_lo", "turn_total_deg_hi",
            "total turning (deg)", "turning.png")
    grouped("clearance_mean", "clearance_mean_lo", "clearance_mean_hi",
            "mean clearance (cells)", "clearance.png")

    # density-style line plots for families with several x values
    fams = defaultdict(lambda: defaultdict(list))
    for s in summary:
        if not math.isnan(s["x"]):
            fams[s["family"]][s["planner"]].append(s)
    for fam, per in fams.items():
        if max(len(v) for v in per.values()) < 2:
            continue
        for metric, lo, hi, label, scale, log, name in [
            ("success_rate", "success_lo", "success_hi", "success rate", 1.0, False, "success"),
            ("len_ratio_vs_astar", None, None, "length / raw A*", 1.0, False, "length_ratio"),
            ("time_s", "time_s_lo", "time_s_hi", "time (ms)", 1000.0, True, "time"),
        ]:
            fig, ax = plt.subplots(figsize=(6.5, 4))
            for j, (p, lst) in enumerate(sorted(per.items())):
                lst = sorted(lst, key=lambda s: s["x"])
                xs = [s["x"] for s in lst]
                ys = [s[metric] * scale for s in lst]
                if lo and hi:
                    yerr = [[max(y - s[lo] * scale, 0) for y, s in zip(ys, lst)],
                            [max(s[hi] * scale - y, 0) for y, s in zip(ys, lst)]]
                    ax.errorbar(xs, ys, yerr=yerr, marker="o", ms=3, capsize=2,
                                label=p, color=cmap(j % 20))
                else:
                    ax.plot(xs, ys, marker="o", ms=3, label=p, color=cmap(j % 20))
            ax.set_xlabel("obstacle density")
            ax.set_ylabel(label)
            if log:
                ax.set_yscale("log")
            ax.legend(fontsize=6)
            fig.tight_layout()
            fig.savefig(os.path.join(outdir, f"{fam}_{name}_vs_x.png"), dpi=200)
            plt.close(fig)


def sweep_plot(summary, meta, key, outdir):
    """Plot each metric against the value of a planner parameter (sensitivity)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from benchmarks.planners import parse_spec

    spec_of = {p["id"]: p["spec"] for p in meta["config"]["planners"]}
    for sc in meta["config"]["scenarios"]:
        for p in sc.get("planners", []):
            spec_of[p["id"]] = p["spec"]
    pts = defaultdict(list)
    for s in summary:
        spec = spec_of.get(s["planner"])
        if spec is None:
            continue
        _, kw = parse_spec(spec)
        if key in kw:
            pts[s["scenario"]].append((kw[key], s))
    if not pts:
        print(f"no planner spec uses parameter {key!r}")
        return
    os.makedirs(outdir, exist_ok=True)
    for metric, lo, hi, label, scale in [
        ("success_rate", "success_lo", "success_hi", "success rate", 1.0),
        ("length", "length_lo", "length_hi", "path length", 1.0),
        ("time_s", "time_s_lo", "time_s_hi", "time (ms)", 1000.0),
    ]:
        fig, ax = plt.subplots(figsize=(6, 4))
        for sc, lst in sorted(pts.items()):
            lst = sorted(lst, key=lambda t: t[0])
            xs = [t[0] for t in lst]
            ys = [t[1][metric] * scale for t in lst]
            yerr = [[max(y - t[1][lo] * scale, 0) for y, t in zip(ys, lst)],
                    [max(t[1][hi] * scale - y, 0) for y, t in zip(ys, lst)]]
            ax.errorbar(xs, ys, yerr=yerr, marker="o", capsize=2, label=sc)
        ax.set_xlabel(key)
        ax.set_ylabel(label)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, f"sweep_{key}_{metric}.png"), dpi=200)
        plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("results_dir")
    ap.add_argument("--ref", default=None, help="reference planner id (default astar_smooth, else first)")
    ap.add_argument("--sweep", default=None, help="planner parameter name for sensitivity plots")
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args(argv)

    d = args.results_dir
    rows = load_rows(os.path.join(d, "raw.csv"))
    meta = None
    if os.path.exists(os.path.join(d, "meta.json")):
        with open(os.path.join(d, "meta.json")) as f:
            meta = json.load(f)
    planners = sorted({r["planner"] for r in rows}, key=lambda p: [r["planner"] for r in rows].index(p))
    ref = args.ref or ("astar_smooth" if "astar_smooth" in planners else planners[0])

    summary = summarize(rows)
    comps = compare(rows, ref)
    write_csv(os.path.join(d, "summary.csv"), summary)
    write_csv(os.path.join(d, "comparisons.csv"), comps)
    with open(os.path.join(d, "summary.md"), "w") as f:
        f.write(markdown(summary, comps, meta, ref))
    if not args.no_figures:
        make_figures(summary, os.path.join(d, "figures"))
        if args.sweep and meta:
            sweep_plot(summary, meta, args.sweep, os.path.join(d, "figures"))
    errs = sum(1 for r in rows if r["error"])
    print(f"{len(rows)} runs, {errs} with errors. Wrote summary.csv, comparisons.csv, summary.md in {d}")


if __name__ == "__main__":
    main()
