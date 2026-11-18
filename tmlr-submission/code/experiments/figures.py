"""Figures of the paper, drawn from the saved results (called by report.py).

Colours: the first five slots of the validated categorical palette (blue, orange, aqua, yellow, magenta) in a
fixed order per method, with line style as a second channel and a legend on every multi-series panel; one hue
for single-series small multiples.  Grids and axes are light; text is never drawn in a series colour.
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DER = os.path.join(PROJ, "data", "derived")
TAGS = ["CA_2022", "CA_2023", "FL_2022", "FL_2023", "TX_2022", "TX_2023"]
SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
# one colour and line style per role; the class of the certified search and of the safe UCB is set per panel
STYLE = {"cert": (SLOT[0], "-"), "safe": (SLOT[2], "--"), "ts": (SLOT[1], "-"), "klucb": (SLOT[3], ":"),
         "ts-own": (SLOT[4], "-.")}
LABEL = {"cert": "Certified search", "safe": "Safe UCB", "ts": "Thompson, vague prior",
         "klucb": "KL-UCB", "ts-own": "Thompson, own-data prior"}

plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.linewidth": 0.6, "legend.frameon": False, "font.family": "serif",
                     "pdf.fonttype": 42})


def _ax(ax):
    ax.grid(True, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_takeup(paper):
    fig, axes = plt.subplots(2, 3, figsize=(6.6, 3.4), sharex=True, sharey=True)
    for ax, t in zip(axes.ravel(), TAGS):
        d = json.load(open(os.path.join(DER, f"takeup_{t}.json")))
        x = np.array([c["mid"] for c in d["curve"]])
        y = 100 * np.array([c["takeup"] for c in d["curve"]])
        e = 196 * np.array([c["se_cluster"] for c in d["curve"]])         # lender-clustered standard errors
        ax.fill_between(x, y - e, y + e, color=SLOT[0], alpha=0.18, linewidth=0)
        ax.plot(x, y, color=SLOT[0], linewidth=1.3, marker="o", markersize=2.5)
        ax.set_title(t.replace("_", " "), fontsize=8, color=INK)
        ax.set_ylim(90, 100)
        _ax(ax)
    fig.supxlabel("offered rate spread minus the mean of its cell (percentage points)", fontsize=8, color=INK)
    fig.supylabel("take-up of approved offers (%)", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(paper, "figures", "fig_takeup.pdf"))
    plt.close(fig)


def fig_offers(paper, tag="CA_2022"):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lending.market import ShoppingMarket
    d = json.load(open(os.path.join(DER, f"offers_{tag}.json")))
    fig, axes = plt.subplots(1, 4, figsize=(6.8, 2.1), gridspec_kw=dict(width_ratios=[1.3, 1, 1, 1]))
    g = np.linspace(-1.2, 1.2, 600)
    m1 = ShoppingMarket.from_hmda(os.path.join(DER, f"offers_{tag}.json"), 1)
    h = 1e-3
    dens = (m1.F(g + h) - m1.F(g - h)) / (2 * h)
    a0 = axes[0]
    a0.plot(g, dens, color=SLOT[0], linewidth=1.3)
    med = d["markup_q"]["50"]
    a0.axvline(med, color=INK2, linewidth=0.8, linestyle=":")
    a0.annotate("median", xy=(med, dens.max() * 0.55), xytext=(med + 0.35, dens.max() * 0.75), fontsize=6.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, linewidth=0.5))
    a0.set_xlabel("lender markup (pp)")
    a0.set_ylabel("density")
    a0.set_title(f"Competing offers, {tag.replace('_', ' ')}", fontsize=7.5, color=INK)
    _ax(a0)
    rug = np.array(d["markups"])
    for K, ax in zip((1, 2, 3), axes[1:]):
        m = ShoppingMarket.from_hmda(os.path.join(DER, f"offers_{tag}.json"), K)
        a = m.a(g)
        d2 = np.gradient(np.gradient(a, g), g)
        ax.fill_between(g, 0, 1, where=d2 >= 0, color=INK2, alpha=0.12, linewidth=0, step="mid")
        ax.plot(g, a, color=SLOT[0], linewidth=1.3)
        r_in = rug[(rug >= g[0]) & (rug <= g[-1])]
        ax.plot(r_in, np.full_like(r_in, 0.015), "|", color=INK2, markersize=3, markeredgewidth=0.4)
        ax.set_ylim(0, 1)
        ax.set_xlim(g[0], g[-1])
        ax.set_title(f"take-up, K = {K}", fontsize=7.5, color=INK)
        ax.set_xlabel("our markup (pp)")
        _ax(ax)
        if K > 1:
            ax.set_yticklabels([])
    axes[1].set_ylabel("a(s)")
    fig.tight_layout()
    fig.savefig(os.path.join(paper, "figures", "fig_offers.pdf"))
    plt.close(fig)


def fig_paths(paper, runs):
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=True)
    groups = (("Overpriced start ($r = 0.5$ or $1$), monotone class", (0.5, 1.0), "M"),
              ("Underpriced start ($r = -0.5$ or $-0.25$), slope bound", (-0.5, -0.25), "eta"))
    for ax, (title, rs, cls) in zip(axes, groups):
        for role, m in (("cert", f"cert-{cls}"), ("safe", f"safe-{cls}"), ("ts", "ts"), ("klucb", "klucb"),
                        ("ts-own", "ts-own")):
            P = np.array([r["path"] for r in runs if r["method"] == m and r["r"] in rs])
            if len(P) == 0:
                continue
            x = (np.arange(P.shape[1]) + 0.5) / P.shape[1] * 500
            c, ls = STYLE[role]
            ax.plot(x, 100 * P.mean(axis=0), color=c, linestyle=ls, linewidth=1.4, label=LABEL[role])
        ax.set_title(title, fontsize=8, color=INK)
        ax.set_xlabel("quotes (thousands)")
        _ax(ax)
    axes[0].set_ylabel("profit per quote (% of optimum)")
    hd, lb = axes[0].get_legend_handles_labels()
    fig.legend(hd, lb, loc="lower center", ncol=3, fontsize=6.5, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.savefig(os.path.join(paper, "figures", "fig_paths.pdf"))
    plt.close(fig)


def fig_trace(paper, tag="CA_2022", K=1, r=1.0, seed=1_000_000 + 1_000 + 500):
    """One run of the certified search (monotone class): incumbent rate and pilot rates over time."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lending.market import ShoppingMarket
    from lending.agent import run_certified
    mk = ShoppingMarket.from_hmda(os.path.join(DER, f"offers_{tag}.json"), K)
    b0 = mk.psi + (mk.s_star - mk.psi) * (1 + r)
    res = run_certified(mk, b0, 500_000, np.random.default_rng(seed), ell_rel=0.1, shape="M")
    fig, ax = plt.subplots(figsize=(6.6, 2.3))
    t, x = [0], [b0]
    for tm, a, b in res["moves"]:
        t += [tm, tm]
        x += [a, b]
    t.append(500_000)
    x.append(x[-1])
    ax.plot(np.array(t) / 1000, x, color=SLOT[0], linewidth=1.5, label="incumbent rate")
    first = True
    for t0, inc, h, outcome, n, _ in res["pilots"]:
        style = dict(color=SLOT[1], linewidth=2.2, alpha=0.9, solid_capstyle="butt")
        ax.plot([t0 / 1000, (t0 + 2 * n) / 1000], [h, h], label="pilot rate" if first else None, **style)
        first = False
    ax.axhline(mk.s_star, color=INK2, linewidth=0.8, linestyle=":")
    ax.text(503, mk.s_star + 0.012, "optimal rate", color=INK2, fontsize=6.5, va="bottom")
    ax.set_xlim(0, 570)
    ax.set_xlabel("quotes (thousands)")
    ax.set_ylabel("rate (pp over benchmark)")
    ax.legend(loc="upper right", fontsize=6.5)
    _ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(paper, "figures", "fig_trace.pdf"))
    plt.close(fig)
    return len(res["moves"]), len(res["pilots"])


def make_all(paper, runs, num):
    os.makedirs(os.path.join(paper, "figures"), exist_ok=True)
    fig_takeup(paper)
    fig_offers(paper)
    fig_paths(paper, runs)
    nm, npil = fig_trace(paper)
    num["trace:moves"] = str(nm)
    num["trace:pilots"] = str(npil)
