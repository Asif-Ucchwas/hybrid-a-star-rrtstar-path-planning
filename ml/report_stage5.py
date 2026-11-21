"""Stage 5 report: one compact view of all four benchmark parts.

    python -m ml.report_stage5            # prints tables, writes results/stage5_report.md
                                          # and results/stage5_budget.png

A  ml_main   : per scenario, every planner: success, fallback rate, length, how far above the
               exact shortest path (paired with vis_graph on the same map), turning, median time;
               then paired tests of learned_tight against hybrid_tight and theta_star_tight
               (Wilcoxon signed-rank on maps where both succeed; McNemar for success).
B  ml_budget : raw search success (no fallback) and median time against the iteration budget.
C  ml_big    : the same as A on 100x100 maps, with lengths compared to ml_big_ref (vis_graph).
"""

import csv
import math
import os
import statistics as st
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

R = "results"
OUT = []


def say(line=""):
    print(line)
    OUT.append(line)


def load(name):
    path = os.path.join(R, name, "raw.csv")
    if not os.path.exists(path):
        return None
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        r["ok"] = r["success"] == "1"
        r["fb"] = r["fallback"] == "1"
        for k in ("length", "turn_total_deg", "time_s"):
            r[k] = float(r[k]) if r[k] not in ("", "nan") else math.nan
    return rows


def index(rows):
    by = defaultdict(dict)
    for r in rows:
        by[(r["scenario"], r["planner"])][r["seed"]] = r
    return by


def fmt(v, nd=1, pct=False):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{v:+.{nd}f}%" if pct else f"{v:.{nd}f}"


def planner_table(rows, ref_rows=None, ref_name="vis_graph"):
    by = index(rows)
    if ref_rows is not None:
        by.update({k: v for k, v in index(ref_rows).items()})
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    planners = list(dict.fromkeys(r["planner"] for r in rows if r["planner"] != ref_name))
    for sc in scenarios:
        ref = by.get((sc, ref_name), {})
        say(f"\n### {sc}")
        say("| planner | success | fallback | length | above best | turning | median time |")
        say("|---|---:|---:|---:|---:|---:|---:|")
        for p in planners:
            rs = by.get((sc, p))
            if not rs:
                continue
            vals = list(rs.values())
            ok = [r for r in vals if r["ok"]]
            gaps = [100 * (r["length"] / ref[s]["length"] - 1) for s, r in rs.items()
                    if r["ok"] and s in ref and ref[s]["ok"]]
            say(f"| {p} | {len(ok)}/{len(vals)} | {100 * sum(r['fb'] for r in vals) / len(vals):.0f}% | "
                f"{fmt(st.mean(r['length'] for r in ok)) if ok else '-'} | "
                f"{fmt(st.mean(gaps), 2, pct=True) if gaps else '-'} | "
                f"{fmt(st.mean(r['turn_total_deg'] for r in ok), 0) if ok else '-'}° | "
                f"{1000 * st.median(r['time_s'] for r in ok):.0f} ms |" if ok else
                f"| {p} | 0/{len(vals)} | - | - | - | - | - |")


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, run = [1.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        out[i] = run
    return out


def stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def paired_tests(rows, a, refs):
    by = index(rows)
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    for ref in refs:
        say(f"\n**{a} vs {ref}** (negative % = {a} is lower; Holm-adjusted over scenarios)")
        say("| scenario | success (only ref / only learned) | length | turning | time |")
        say("|---|---|---:|---:|---:|")
        results = []
        for sc in scenarios:
            x, y = by.get((sc, a)), by.get((sc, ref))
            if not x or not y:
                continue
            seeds = sorted(set(x) & set(y))
            b = sum(1 for s in seeds if y[s]["ok"] and not x[s]["ok"])
            c = sum(1 for s in seeds if x[s]["ok"] and not y[s]["ok"])
            p_s = stats.binomtest(min(b, c), b + c, 0.5).pvalue if b + c else 1.0
            both = [s for s in seeds if x[s]["ok"] and y[s]["ok"]]
            res = {"sc": sc, "succ": (b, c, p_s)}
            for m in ("length", "turn_total_deg", "time_s"):
                d = np.array([x[s][m] - y[s][m] for s in both])
                base = np.mean([y[s][m] for s in both]) if both else math.nan
                try:
                    p = float(stats.wilcoxon(d).pvalue) if len(d) and np.any(d != 0) else 1.0
                except ValueError:
                    p = 1.0
                res[m] = (100 * d.mean() / base if len(d) and base else math.nan, p)
            results.append(res)
        for key in ("succ", "length", "turn_total_deg", "time_s"):
            idx = 2 if key == "succ" else 1
            adj = holm([r[key][idx] for r in results])
            for r, q in zip(results, adj):
                r[key] = r[key][:idx] + (q,)
        for r in results:
            b, c, q = r["succ"]
            cells = [f"{fmt(r[m][0], 1, pct=True)} {stars(r[m][1])}" for m in ("length", "turn_total_deg", "time_s")]
            say(f"| {r['sc']} | {b} / {c} {stars(q)} | " + " | ".join(cells) + " |")


def budget_section(rows):
    by = index(rows)
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    fams = list(dict.fromkeys(r["planner"].split("@")[0] for r in rows))
    budgets = sorted({int(r["planner"].split("@")[1]) for r in rows})
    curves = {}
    for sc in scenarios:
        say(f"\n### {sc}: raw success (no fallback) / median time")
        say("| planner | " + " | ".join(str(b) for b in budgets) + " |")
        say("|---|" + "---:|" * len(budgets))
        for f in fams:
            cells, succ, tim = [], [], []
            for b in budgets:
                rs = list(by.get((sc, f"{f}@{b}"), {}).values())
                if not rs:
                    cells.append("-")
                    succ.append(math.nan)
                    tim.append(math.nan)
                    continue
                rate = 100 * sum(r["ok"] for r in rs) / len(rs)
                t = 1000 * st.median(r["time_s"] for r in rs)
                cells.append(f"{rate:.0f}% / {t:.0f} ms")
                succ.append(rate)
                tim.append(t)
            curves[(sc, f)] = (succ, tim)
            say(f"| {f} | " + " | ".join(cells) + " |")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, len(scenarios), figsize=(4.6 * len(scenarios), 7), squeeze=False)
        for j, sc in enumerate(scenarios):
            for f in fams:
                succ, tim = curves[(sc, f)]
                axes[0, j].plot(budgets, succ, "o-", label=f)
                axes[1, j].plot(budgets, tim, "o-", label=f)
            axes[0, j].set_title(sc)
            axes[0, j].set_ylabel("raw success (%)")
            axes[1, j].set_ylabel("median time (ms)")
            for ax in axes[:, j]:
                ax.set_xscale("log")
                ax.minorticks_off()
                ax.set_xticks(budgets)
                ax.set_xticklabels([str(b) for b in budgets])
                ax.set_xlabel("RRT* iteration budget")
                ax.grid(alpha=0.3)
            axes[0, j].legend(fontsize=8)
        fig.suptitle("Stage 5B: success and time against search budget (no fallback, no tightening)")
        fig.tight_layout()
        fig.savefig(os.path.join(R, "stage5_budget.png"), dpi=130)
        say(f"\nFigure: {R}/stage5_budget.png")
    except Exception as exc:  # the tables matter more than the picture
        say(f"\n(figure skipped: {exc})")


def main():
    main_rows, budget_rows = load("ml_main"), load("ml_budget")
    big_rows, big_ref = load("ml_big"), load("ml_big_ref")
    if main_rows:
        say("## A. 50x50 test maps (ml_main)")
        planner_table(main_rows)
        say("\n## A. Paired tests")
        paired_tests(main_rows, "learned_tight", ["hybrid_tight", "theta_star_tight"])
    if budget_rows:
        say("\n## B. Search budget (ml_budget)")
        budget_section(budget_rows)
    if big_rows:
        say("\n## C. 100x100 maps, never trained on (ml_big)")
        planner_table(big_rows, big_ref)
        say("\n## C. Paired tests")
        paired_tests(big_rows, "learned_tight_x4", ["hybrid_tight_x4"])
        paired_tests(big_rows, "learned_tight", ["hybrid_tight", "theta_star_tight"])
    with open(os.path.join(R, "stage5_report.md"), "w") as f:
        f.write("# Stage 5 report\n" + "\n".join(OUT) + "\n")
    print(f"\nSaved: {R}/stage5_report.md")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        R = sys.argv[1]
    main()
