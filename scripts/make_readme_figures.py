"""Build the charts shown in the README from the committed benchmark summaries.

Inputs (all in ``results/summaries/``, written by ``python -m benchmarks.analyze``):
    decision_vs_theta_star_tight.md          exact rule, paired against Theta* + tighten
    decision_vs_vis_graph.md                 exact rule, paired against the exact shortest path
    decision_control_vs_theta_star_tight.md  sampled rule (thesis rule), same random maps
    decision_summary.csv                     exact rule, one row per scenario and planner

    python scripts/make_readme_figures.py            # writes assets/readme/*.png

Every number in the charts comes from those files; nothing is typed in by hand.
The collision-rule picture is an illustration, not data.
"""

import csv
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUM = os.path.join(ROOT, "results", "summaries")
OUT = os.path.join(ROOT, "assets", "readme")

NAME = {"astar_smooth": "A* + shortcut", "theta_star_cc": "Theta*", "theta_star_tight": "Theta* + tighten",
        "hybrid_fallback": "Hybrid", "hybrid_tight": "Hybrid + tighten",
        "hybrid_tight_x2": "Hybrid + tighten (2x budget)", "vis_graph": "Exact shortest path"}
COL = {"astar_smooth": "#d95f02", "theta_star_cc": "#a9b4c0", "theta_star_tight": "#1b6ca8",
       "hybrid_fallback": "#9bd8aa", "hybrid_tight": "#1b9e77", "hybrid_tight_x2": "#0b5d46",
       "vis_graph": "#222222"}
DENS = ["random_d0.10", "random_d0.20", "random_d0.30"]
DLAB = {"random_d0.10": "0.10", "random_d0.20": "0.20", "random_d0.30": "0.30"}


def num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def parse_md(path):
    """Return (main, paired): main[scenario][planner] -> dict, paired[scenario][planner][metric] -> dict."""
    main, paired, scen, kind = {}, {}, None, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            scen = line[3:].strip()
            continue
        if not line.startswith("|") or scen is None:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "planner":
            kind = "main" if cells[1] == "n" else "paired"
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if kind == "main":
            ci = re.findall(r"-?\d+\.\d+", cells[4])
            main.setdefault(scen, {})[cells[0]] = dict(
                n=int(cells[1]), time_ms=num(cells[3].split("/")[0]), length=float(ci[0]),
                turn=num(cells[6]), graze=num(cells[8]))
        elif kind == "paired":
            paired.setdefault(scen, {}).setdefault(cells[0], {})[cells[1]] = dict(
                pct=None if cells[3] == "-" else float(cells[3]), sig=cells[6])
    return main, paired


def style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25,
                         "axes.axisbelow": True})


def fig_gap(vis_paired):
    """Length above the exact shortest path, per planner and map set."""
    planners = ["astar_smooth", "theta_star_cc", "theta_star_tight", "hybrid_fallback", "hybrid_tight",
                "hybrid_tight_x2"]
    groups = DENS + ["narrow"]
    labels = [f"random\ndensity {DLAB[g]}" if g in DLAB else "narrow\npassages" for g in groups]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    w = 0.13
    for i, p in enumerate(planners):
        vals = [vis_paired[g][p]["length"]["pct"] for g in groups]
        xs = np.arange(len(groups)) + (i - (len(planners) - 1) / 2) * w
        bars = ax.bar(xs, vals, w * 0.92, color=COL[p], label=NAME[p])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{v:.1f}", ha="center", va="bottom",
                    fontsize=7.5)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Longer than the best possible path (%)")
    ax.set_title("How close does each planner get to the exact shortest path?  (lower is better)", loc="left")
    ax.legend(ncol=3, fontsize=8.5, frameon=False, loc="upper left")
    ax.set_ylim(0, 16)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "gap_to_shortest.png"), dpi=160)
    plt.close(fig)


def fig_speed(vis_main, vis_paired):
    """Planning time (log) against path quality, one panel per obstacle density."""
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6), sharey=True)
    for ax, g in zip(axes, DENS):
        for p in COL:
            t = vis_main[g][p]["time_ms"]
            gap = 0.0 if p == "vis_graph" else vis_paired[g][p]["length"]["pct"]
            ax.scatter(t, gap, s=170 if p == "vis_graph" else 100, color=COL[p], edgecolor="white",
                       linewidth=0.8, zorder=3, marker="*" if p == "vis_graph" else "o", label=NAME[p])
        ax.set_xscale("log")
        ax.set_xlim(4, 15000)
        ax.set_ylim(-0.8, 14.5)
        ax.set_title(f"obstacle density {DLAB[g]}", fontsize=10.5)
        ax.set_xlabel("planning time (ms, log scale)")
    axes[0].set_ylabel("Longer than best possible path (%)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=9, frameon=False)
    fig.suptitle("Speed vs quality: the best planners sit in the bottom-left corner", x=0.01, ha="left",
                 fontsize=11.5)
    fig.tight_layout(rect=[0, 0.1, 1, 0.95])
    fig.savefig(os.path.join(OUT, "speed_vs_quality.png"), dpi=160)
    plt.close(fig)


def fig_rule(sampled_paired, exact_paired):
    """Turning of Hybrid vs Theta* + tighten under the two collision rules."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    w = 0.36
    for ax, p, title in zip(axes, ["hybrid_tight", "hybrid_fallback"],
                            ["Hybrid + tighten", "Hybrid (no tightening)"]):
        s_rec = [sampled_paired[g][p]["turn_total_deg"] for g in DENS]
        e_rec = [exact_paired[g][p]["turn_total_deg"] for g in DENS]
        x = np.arange(3)
        b1 = ax.bar(x - w / 2, [r["pct"] for r in s_rec], w, color="#7a8794",
                    label="old sampled rule (thesis)")
        b2 = ax.bar(x + w / 2, [r["pct"] for r in e_rec], w, color="#1b9e77",
                    label="exact rule (margin 0.05)")
        for bars, recs in ((b1, s_rec), (b2, e_rec)):
            for b, r in zip(bars, recs):
                h = b.get_height()
                tag = "ns" if r["sig"] == "ns" else r["sig"]
                ax.text(b.get_x() + b.get_width() / 2, h + (3 if h >= 0 else -3), f"{h:+.0f}%\n{tag}",
                        ha="center", va="bottom" if h >= 0 else "top", fontsize=7.5)
        ax.axhline(0, color="black", lw=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels([f"density {DLAB[g]}" for g in DENS])
        ax.set_title(title, loc="left", fontsize=10.5)
        ax.set_ylim(-90, 140)
    axes[0].set_ylabel("Turning vs Theta* + tighten (%)\nnegative = Hybrid is smoother")
    axes[0].legend(fontsize=8.5, frameon=False, loc="upper left")
    fig.suptitle("The collision rule changes who looks smoother  (ns = not significant)", x=0.01, ha="left",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(OUT, "rule_flips_the_result.png"), dpi=160)
    plt.close(fig)


def fig_fallback(csv_path):
    """How often the corridor RRT* failed and the planner fell back to A*."""
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    fb = {(r["scenario"], r["planner"]): 100 * float(r["fallback_rate"]) for r in rows}
    scen = ["random_d0.10", "random_d0.20", "random_d0.30", "narrow", "maze"]
    labels = ["random 0.10", "random 0.20", "random 0.30", "narrow", "maze"]
    planners = ["hybrid_fallback", "hybrid_tight", "hybrid_tight_x2"]
    fig, ax = plt.subplots(figsize=(9, 4))
    w = 0.26
    for i, p in enumerate(planners):
        vals = [fb[(s, p)] for s in scen]
        xs = np.arange(len(scen)) + (i - 1) * w
        bars = ax.bar(xs, vals, w * 0.92, color=COL[p], label=NAME[p])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(scen)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Runs that fell back to A* (%)")
    ax.set_ylim(0, 72)
    ax.set_title("At the default budget, Hybrid often gives up and uses A*", loc="left")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fallback_rate.png"), dpi=160)
    plt.close(fig)


def sampled_hits_obstacle(p, q, obstacle_cell, per_cell=3):
    """The thesis-style test: 3 samples per cell of length, each rounded to a cell."""
    length = float(np.hypot(q[0] - p[0], q[1] - p[1]))
    n = max(2, int(np.ceil(length * per_cell)) + 1)
    ts = np.linspace(0.0, 1.0, n)
    pts = np.array([[p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])] for t in ts])
    hit = any((round(x), round(y)) == obstacle_cell for x, y in pts)
    return pts, hit


def fig_leak():
    """Illustration: a segment that clips an obstacle corner between two samples."""
    cell = (4, 5)                          # obstacle cell, the unit square [3.5, 4.5] x [4.5, 5.5]
    best = None
    for shift in np.linspace(0.0, 0.5, 51):   # slide the segment so no sample lands in the corner
        p, q = (2.0 + shift, 2.15 + shift), (7.0 + shift, 7.15 + shift)   # line x - y = -0.15
        pts, hit = sampled_hits_obstacle(p, q, cell)
        if not hit:
            best = (p, q, pts)
            break
    assert best is not None, "could not build the illustration"
    p, q, pts = best
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    titles = ["Sampled rule (the thesis code):  accepted", "Exact rule:  rejected"]
    for ax, title in zip(axes, titles):
        for x in range(1, 9):
            for y in range(1, 9):
                ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, fill=False, ec="#d5d9de", lw=0.8))
        ax.add_patch(Rectangle((cell[0] - 0.5, cell[1] - 0.5), 1, 1, color="#3a3f47"))
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#1b6ca8", lw=2.2, zorder=3)
        ax.set_xlim(1.5, 7.5)
        ax.set_ylim(1.5, 7.5)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=11, loc="left")
        ax.grid(False)
    axes[0].scatter(pts[:, 0], pts[:, 1], s=26, color="#2ca02c", zorder=4,
                    label="sample points (all in free cells)")
    axes[0].legend(loc="upper left", fontsize=8.5, framealpha=0.95)
    # the clipped corner, in red on both sides
    for ax in axes:
        ax.add_patch(Polygon([[4.5, 4.5], [4.5, 4.65], [4.35, 4.5]], closed=True, color="#d62728", zorder=5))
    axes[0].annotate("the line clips this corner,\nbut no sample point lands in it\n\u2192 'free'",
                     xy=(4.45, 4.55), xytext=(5.0, 2.2), fontsize=9.5, color="#d62728",
                     arrowprops=dict(arrowstyle="->", color="#d62728"))
    axes[1].annotate("exact geometry: the path enters\nthe obstacle cell \u2192 collision", xy=(4.45, 4.55),
                     xytext=(5.0, 2.2), fontsize=9.5, color="#d62728",
                     arrowprops=dict(arrowstyle="->", color="#d62728"))
    fig.suptitle("Illustration: why the old collision check flattered corner-cutting planners",
                 x=0.01, ha="left", fontsize=11.5)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(OUT, "collision_rule_illustration.png"), dpi=160)
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    style()
    _, theta_paired = parse_md(os.path.join(SUM, "decision_vs_theta_star_tight.md"))
    vis_main, vis_paired = parse_md(os.path.join(SUM, "decision_vs_vis_graph.md"))
    _, samp_paired = parse_md(os.path.join(SUM, "decision_control_vs_theta_star_tight.md"))
    fig_gap(vis_paired)
    fig_speed(vis_main, vis_paired)
    fig_rule(samp_paired, theta_paired)
    fig_fallback(os.path.join(SUM, "decision_summary.csv"))
    fig_leak()
    print("wrote figures to", OUT)


if __name__ == "__main__":
    main()
