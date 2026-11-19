#!/usr/bin/env python
"""Figures of the paper.

Every figure is drawn from results/*.json or from a re-run of one seed that
uses exactly the code path of experiments/run_all.py; each re-run is checked
against the stored regret before anything is drawn.

    python experiments/figures.py [--out DIR] [--only NAME ...]

Colours: three categorical hues (blue, orange, aqua) that pass the
colour-vision-deficiency and normal-vision separation checks for every pair on
a white surface, with line style as the second channel; ordered budget levels
take a one-hue blue ramp.  Text is never drawn in a series colour.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.lines import Line2D                  # noqa: E402
from matplotlib.patches import Patch                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ctrr.agent import certified_gain, lower_envelope, trr_step     # noqa: E402
from ctrr.model import Env                                          # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "experiments", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


run_all = _load("run_all")
report = _load("report")

# ------------------------------------------------------------------- style
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
BLUE_LIGHT, BLUE_DARK = "#86b6ef", "#1c5cab"
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
DASH = (0, (4, 2))
WIDTH = 6.5
MK = ["m=0.3", "m=0.6", "m=0.8", "m=1.09"]
HEAD = {"m=0.3": "$m=0.3$", "m=0.6": "$m=0.6$", "m=0.8": "$m=0.8$", "m=1.09": "$m=1.09$"}
POW = {1: "1", 10: "10", 100: "$10^2$", 1000: "$10^3$", 10000: "$10^4$", 100000: "$10^5$"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans",
    "font.size": 7.5, "axes.titlesize": 7.5, "axes.labelsize": 7.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "text.color": INK, "axes.titlecolor": INK, "axes.titlelocation": "left", "axes.titlepad": 4,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.labelcolor": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 0,
    "xtick.minor.size": 0, "ytick.minor.size": 0,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "legend.frameon": False, "legend.handlelength": 2.2,
    "lines.linewidth": 1.5, "pdf.fonttype": 42, "ps.fonttype": 42,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})
DOT = dict(marker="o", ms=5, mec="white", mew=1.1)


def save(fig, out, name):
    path = os.path.join(out, name)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03, dpi=300)
    plt.close(fig)
    print("wrote", path)


def log_ticks(ax, axis, ticks):
    getattr(ax, f"set_{axis}ticks")(ticks)
    getattr(ax, f"set_{axis}ticklabels")([POW[t] for t in ticks])
    getattr(ax, f"{axis}axis").set_minor_locator(matplotlib.ticker.NullLocator())


def simulate(market, cfg, seed, T, stored=None):
    """Re-run one seed as run_all.run_one does and return the agent and the
    deployed quotes.  `stored` is (suite, config name) for the regret check."""
    mk = run_all.get_market(market)
    h0 = mk.stable_point()
    phi0 = float(mk.Phi(h0))
    ag = run_all.make_agent(cfg, mk, h0, phi0)
    env = Env(mk, seed=seed)
    path = np.empty(T)
    for t in range(T):
        h = ag.act()
        ag.observe(h, env.deploy(h))
        path[t] = h
    if stored is not None:
        reg = float(np.sum(float(mk.Phi(mk.optimum())) - mk.Phi(path)))
        ref = report.runs(stored[0], stored[1], market)[seed - run_all.SEED0]["regret"]
        assert abs(reg - ref) <= 1e-8 * max(1.0, abs(ref)), (market, stored, seed, reg, ref)
    return mk, ag, path


# ---------------------------------------------------------------- figure 1
def fig_landscape(out):
    mk = run_all.get_market("m=0.6")
    hs, ho, psi = mk.stable_point(), mk.optimum(), mk.psi
    H = np.linspace(0.9, 3.0, 900)
    K = mk.K(H)

    def minorant(b):
        return K + (H - psi) * (float(mk.tau(b)) - float(mk.eps(b)) * (H - b))

    b1 = float(trr_step(mk, hs))
    b2 = float(trr_step(mk, b1))
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.45),
                               gridspec_kw=dict(width_ratios=[1.5, 1], wspace=0.27))
    a.plot(H, mk.J(H, float(mk.tau(hs))), color=ORANGE,
           label="profit with the flow frozen at $\\tau(h_{\\mathrm{s}})$")
    a.plot(H, minorant(hs), color=AQUA, lw=1.1, label="tangent minorant at $h_{\\mathrm{s}}$")
    a.plot(H, minorant(b1), color=AQUA, lw=1.1, ls=DASH, label="tangent minorant at $b_1$")
    a.plot(H, mk.Phi(H), color=BLUE, label="true profit $\\Phi$")
    for x, col in ((b1, AQUA), (b2, AQUA), (hs, INK), (ho, INK)):
        a.plot([x], [float(mk.Phi(x))], color=col, ls="none", zorder=5, **DOT)
    up = dict(textcoords="offset points", va="bottom", color=INK)
    a.annotate("$h_{\\mathrm{s}}$  stable quote", (hs, float(mk.Phi(hs))), xytext=(4, 5), ha="left", **up)
    a.annotate("$h^\\star$  optimum", (ho, float(mk.Phi(ho))), xytext=(0, 5), ha="center", **up)
    a.annotate("$b_1$", (b1, float(mk.Phi(b1))), xytext=(3, 4), ha="left", **up)
    a.annotate("$b_2$", (b2, float(mk.Phi(b2))), xytext=(3, 4), ha="left", **up)
    a.set_xlim(0.9, 3.0)
    a.set_ylim(0.55, 1.68)
    a.set_xlabel("half-spread $h$")
    a.set_ylabel("expected profit per period")
    a.set_title("(a) Profit as a function of the quote")
    handles, labels = a.get_legend_handles_labels()
    order = [3, 0, 1, 2]
    handles, labels = [handles[i] for i in order], [labels[i] for i in order]

    n, start = 12, 1.9
    r, t = [start], [start]
    for _ in range(n):
        r.append(float(mk.best_response(float(mk.tau(r[-1])))))
        t.append(float(trr_step(mk, t[-1])))
    k = np.arange(n + 1)
    for y, text in ((hs, "$h_{\\mathrm{s}}$"), (ho, "$h^\\star$")):
        b.axhline(y, color=MUTED, lw=0.6, zorder=1)
        b.annotate(text, (n + 0.4, y), xytext=(4, 0), textcoords="offset points", ha="left", va="center",
                   color=INK, annotation_clip=False)
    b.plot(k, r, color=ORANGE, lw=1.2, label="repeated retraining", zorder=3, **DOT)
    b.plot(k, t, color=AQUA, lw=1.2, label="tangent-response update", zorder=3, **DOT)
    b.set_xlim(-0.4, n + 0.4)
    b.set_ylim(1.1, 3.0)
    b.set_xticks(range(0, n + 1, 2))
    b.set_xlabel("update number")
    b.set_ylabel("half-spread $h$")
    b.set_title("(b) Two update rules from the same start")
    hb, lb = b.get_legend_handles_labels()
    fig.legend(handles + hb, labels + lb, loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3,
               labelcolor=INK2, columnspacing=1.8)
    save(fig, out, "fig_landscape.pdf")


# ---------------------------------------------------------------- figure 2
def fig_certificate(out, snap=1000, seed=100):
    mk, ag, _ = simulate("m=0.6", dict(kind="ctrr", bud=0.05), seed, snap)
    hs = mk.stable_point()
    idx = sorted((k for k, a in enumerate(ag.anchors) if a.ready), key=lambda k: ag.anchors[k].x)
    xs = np.array([ag.anchors[k].x for k in idx])
    L = np.array([ag.anchors[k].L for k in idx])
    U = np.array([ag.anchors[k].U for k in idx])
    M = np.array([ag.anchors[k].mean for k in idx])
    N = [ag.anchors[k].n for k in idx]
    ib = idx.index(ag.inc)
    xb = xs[ib]
    xc = ag.anchors[ag.ch].x if ag.ch is not None else None
    H = np.unique(np.concatenate([np.linspace(1.0, hs, 1400), xs, xs - 1e-9, xs + 1e-9]))
    H = H[(H >= 1.0) & (H <= hs)]
    low = lower_envelope(H, xs, L, U)
    g_low = certified_gain(mk, H, xs, L, U, ib)
    g_true = mk.Phi(H) - float(mk.Phi(xb))
    assert np.all(low <= mk.tau(H) + 1e-9), "envelope above the truth: confidence event failed in this run"
    assert np.all(g_low <= g_true + 1e-9)
    print("certificate snapshot: period", snap, "anchors", np.round(xs, 4), "samples", N,
          "incumbent", round(xb, 4), "challenger", None if xc is None else round(xc, 4),
          "ell", round(ag.ell, 5))

    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.4), gridspec_kw=dict(wspace=0.27))
    a.plot(H, mk.tau(H), color=BLUE, label="truth (unknown to the dealer)")
    a.plot(H, low, color=ORANGE, label="certified lower bound")
    a.errorbar(xs, M, yerr=[np.maximum(M - L, 0), np.maximum(U - M, 0)], fmt="o", color=INK, ms=3.2,
               elinewidth=0.9, capsize=2.6, capthick=0.9, zorder=5,
               label="trial quotes: sample mean and confidence interval")
    a.annotate("start $h_0$: flow\nknown exactly", (xs[-1], M[-1]), xytext=(0, 44), textcoords="offset points",
               ha="right", va="bottom", color=INK, linespacing=1.15,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkA=1.5, shrinkB=4.5,
                               relpos=(0.93, 0.0)))
    a.set_xlim(0.97, hs + 0.06)
    a.set_ylim(0.6, 2.1)
    a.set_xlabel("half-spread $h$")
    a.set_ylabel("responsive flow per period")
    a.set_title("(a) Responsive flow $\\tau$")
    handles, labels = a.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.955), ncol=3, labelcolor=INK2,
               columnspacing=1.6)

    ell = ag.ell
    safe = g_low >= -ell
    edges = np.flatnonzero(np.diff(np.concatenate([[0], safe.astype(int), [0]])))
    for s, e in zip(edges[::2], edges[1::2]):
        b.axvspan(H[s], H[e - 1], color=MUTED, alpha=0.13, lw=0, zorder=0)
    b.axhline(0.0, color=MUTED, lw=0.6, zorder=1)
    b.axhline(-ell, color=MUTED, lw=0.6, zorder=1)
    b.plot(H, g_true, color=BLUE)
    b.plot(H, g_low, color=ORANGE)
    b.plot([xb], [0.0], color=INK, ls="none", zorder=6, **DOT)
    b.annotate("incumbent", (xb, 0.0), xytext=(5, 5), textcoords="offset points", ha="left", va="bottom", color=INK)
    if xc is not None:
        gc = float(mk.Phi(xc) - mk.Phi(xb))
        b.plot([xc], [gc], color=INK, ls="none", zorder=6, **DOT)
        b.annotate("quote on trial", (xc, gc), xytext=(6, 3), textcoords="offset points",
                   ha="left", va="bottom", color=INK)
    right = dict(xytext=(3, 0), textcoords="offset points", ha="left", va="center", color=INK,
                 annotation_clip=False)
    b.annotate("$-\\ell$", (hs + 0.06, -ell), **right)
    b.annotate("0", (hs + 0.06, 0.0), **right)
    s0 = H[safe]
    b.text(0.5 * (s0.min() + s0.max()), -0.405, "safe\nto trial", ha="center", va="bottom", color=INK2,
           linespacing=1.15)
    b.set_xlim(0.97, hs + 0.06)
    b.set_ylim(-0.42, 0.2)
    b.set_xlabel("half-spread $h$")
    b.set_ylabel("profit relative to the incumbent")
    b.set_title("(b) Gain from moving the incumbent to $h$")
    save(fig, out, "fig_certificate.pdf")


# ---------------------------------------------------------------- figure 3
def fig_paths(out, market="m=0.6", seed=100, name="fig_paths.pdf"):
    T = run_all.T_MAIN
    F = report.FIXED
    specs = [("C-TRR, $\\ell=5\\%$", "C-TRR ell=5%", dict(kind="ctrr", bud=0.05), BLUE),
             ("UCB", F["ucb"], run_all.FIXED[F["ucb"]], ORANGE),
             ("PerfGD", F["gd"], run_all.FIXED[F["gd"]], AQUA),
             ("Two-point TR", F["bz"], run_all.FIXED[F["bz"]], AQUA)]
    fig, axes = plt.subplots(2, 4, figsize=(WIDTH, 3.5), sharex=True, sharey="row",
                             gridspec_kw=dict(wspace=0.09, hspace=0.16))
    tt = np.arange(1, T + 1)
    pct_best = None
    for c, (title, cname, cfg, col) in enumerate(specs):
        mk, ag, path = simulate(market, cfg, seed, T, stored=("main", cname))
        hs, ho = mk.stable_point(), mk.optimum()
        phi0 = float(mk.Phi(hs))
        pct = 100.0 * (mk.Phi(path) - phi0) / phi0
        pct_best = 100.0 * (float(mk.Phi(ho)) - phi0) / phi0
        top, bot = axes[0, c], axes[1, c]
        for y in (hs, ho):
            top.axhline(y, color=MUTED, lw=0.6, zorder=1)
        for y in (0.0, pct_best):
            bot.axhline(y, color=MUTED, lw=0.6, zorder=1)
        dots = dict(ls="none", marker="o", ms=1.5, mew=0, color=col, alpha=0.55, rasterized=True, zorder=2)
        top.plot(tt, path, **dots)
        bot.plot(tt, pct, **dots)
        if cfg["kind"] == "ctrr":
            inc = np.array(ag.inc_path)
            top.step(tt, inc, where="post", color=INK, lw=0.9, zorder=3)
            bot.step(tt, 100.0 * (mk.Phi(inc) - phi0) / phi0, where="post", color=INK, lw=0.9, zorder=3)
        top.set_title(title)
        top.set_xscale("log")
        bot.set_xlabel("period")
    axes[0, 0].set_xlim(1, T)
    log_ticks(axes[0, 0], "x", [1, 10, 100, 1000, 10000])
    axes[0, 0].set_ylabel("deployed half-spread")
    axes[1, 0].set_ylabel("profit over the stable quote (%)")
    mk = run_all.get_market(market)
    hs, ho = mk.stable_point(), mk.optimum()
    right = dict(xytext=(4, 0), textcoords="offset points", ha="left", va="center", color=INK,
                 annotation_clip=False)
    axes[0, 3].annotate("$h_{\\mathrm{s}}$", (T, hs), **right)
    axes[0, 3].annotate("$h^\\star$", (T, ho), **right)
    axes[1, 3].annotate("optimum", (T, pct_best), **right)
    axes[1, 3].annotate("stable", (T, 0.0), **right)
    handles = [Line2D([], [], ls="none", marker="o", ms=3, mew=0, color=MUTED, label="quote deployed in a period"),
               Line2D([], [], color=INK, lw=0.9, label="C-TRR incumbent")]
    fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.93), labelcolor=INK2,
               columnspacing=2.0)
    save(fig, out, name)


# ---------------------------------------------------------------- figure 4
SERIES = [("C-TRR ell=5%", "C-TRR, $\\ell=5\\%$", BLUE, "-"),
          ("C-TRR ell=10%", "C-TRR, $\\ell=10\\%$", BLUE, DASH),
          ("ucb", "UCB", ORANGE, "-"),
          ("gd", "PerfGD", AQUA, "-"),
          ("bz", "Two-point TR", AQUA, DASH)]


def _cfg(key):
    return report.FIXED.get(key, key)


def _series_legend(fig, extra=(), y=1.0, lw=1.5):
    handles = [Line2D([], [], color=col, ls=ls, lw=lw, label=lab) for _, lab, col, ls in SERIES] + list(extra)
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), bbox_to_anchor=(0.5, y),
               labelcolor=INK2, columnspacing=1.3, handletextpad=0.5)


def fig_regret(out):
    T = 96000
    cps = np.unique(np.round(np.geomspace(10, T, 48)).astype(int))
    fig, axes = plt.subplots(1, 4, figsize=(WIDTH, 2.15), sharex=True, sharey=True,
                             gridspec_kw=dict(wspace=0.09))
    for ax, m in zip(axes, MK):
        mk = run_all.get_market(m)
        gap = float(mk.Phi(mk.optimum()) - mk.Phi(mk.stable_point()))
        ax.plot(cps, gap * cps, color=MUTED, lw=0.8, zorder=1)
        for key, lab, col, ls in SERIES:
            C = np.array([r["curve"] for r in report.runs("horizon", _cfg(key), m)])
            assert C.shape == (30, len(cps)), C.shape
            q1, med, q3 = np.percentile(C, [25, 50, 75], axis=0)
            ax.fill_between(cps, q1, q3, color=col, alpha=0.10, lw=0, zorder=2)
            ax.plot(cps, med, color=col, ls=ls, lw=1.25, zorder=3)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(HEAD[m])
        ax.set_xlabel("period")
    axes[0].set_xlim(10, T)
    axes[0].set_ylim(1, 2e4)
    log_ticks(axes[0], "x", [10, 100, 1000, 10000])
    log_ticks(axes[0], "y", [1, 10, 100, 1000, 10000])
    axes[0].set_ylabel("cumulative regret")
    _series_legend(fig, extra=[Line2D([], [], color=MUTED, lw=0.8, label="stay at the stable quote")],
                   y=0.98, lw=1.25)
    save(fig, out, "fig_regret.pdf")


# ---------------------------------------------------------------- figure 5
def fig_price(out):
    fig = plt.figure(figsize=(WIDTH, 4.2))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.05], hspace=0.66, wspace=0.09)
    budgets = [("ell=1%", "1"), ("ell=2%", "2"), ("ell=5%", "5"), ("ell=10%", "10"), ("ell=20%", "20"),
               ("ell=inf d0=0.5", "none")]
    xpos = [0, 1, 2, 3, 4, 5.5]
    top = []
    for c, m in enumerate(MK):
        ax = fig.add_subplot(gs[0, c], sharey=top[0] if top else None)
        top.append(ax)
        R = [np.array([r["regret"] for r in report.runs("ablation", cfg, m)]) for cfg, _ in budgets]
        q1, med, q3 = (np.array([np.percentile(r, q) for r in R]) for q in (25, 50, 75))
        ax.plot(xpos[:5], med[:5], color=BLUE, lw=1.1, zorder=2)
        ax.errorbar(xpos, med, yerr=[med - q1, q3 - med], fmt="none", ecolor=BLUE, elinewidth=0.9,
                    capsize=0, zorder=3)
        ax.plot(xpos, med, color=BLUE, ls="none", zorder=4, marker="o", ms=4.2, mec="white", mew=0.9)
        ax.set_yscale("log")
        ax.set_xlim(-0.6, 6.1)
        ax.set_xticks(xpos)
        ax.set_xticklabels([lab for _, lab in budgets])
        ax.set_title(HEAD[m])
        ax.set_xlabel("loss budget $\\ell$ (%)")
        if c:
            plt.setp(ax.get_yticklabels(), visible=False)
    top[0].set_ylim(25, 3000)
    top[0].set_yticks([30, 100, 300, 1000, 3000])
    top[0].set_yticklabels(["30", "100", "300", "1,000", "3,000"])
    top[0].yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    top[0].set_ylabel("cumulative regret")
    x0 = top[0].get_position().x0
    fig.text(x0, 0.945, "(a) Regret of C-TRR against the loss budget (median and interquartile range)",
             ha="left", va="bottom", color=INK)

    kinds = [("", "anytime-\nvalid"), (" uncertified z=1.64", "fixed\n$z=1.64$"),
             (" uncertified z=1", "fixed\n$z=1$"), (" uncertified z=0.5", "fixed\n$z=0.5$")]
    harm, regs = {}, {}
    for tag in ("ell=5%", "ell=10%"):
        harm[tag], regs[tag] = [], []
        for suffix, _ in kinds:
            rs = [report.runs("ablation", tag + suffix, m) for m in MK]
            harm[tag].append(sum(sum(1 for r in cell if r["harmful"] > 0) for cell in rs))
            # sum of the per-market medians as printed in the table (rounded to integers)
            regs[tag].append(sum(int(report.fi(np.median([r["regret"] for r in cell]))) for cell in rs))
    print("price of certification: harmful runs", harm, "sum of median regrets", regs)
    x = np.arange(len(kinds))
    wbar, off = 0.3, 0.165
    panels = [(fig.add_subplot(gs[1, 0:2]), harm, "(b) Runs with a harmful adoption, of 120", "{:d}"),
              (fig.add_subplot(gs[1, 2:4]), regs, "(c) Sum of the median regrets in the four markets", "{:,d}")]
    for ax, data, title, fmt in panels:
        hi = max(max(v) for v in data.values())
        for tag, col, dx in (("ell=5%", BLUE_LIGHT, -off), ("ell=10%", BLUE_DARK, off)):
            ax.bar(x + dx, data[tag], width=wbar, color=col, lw=0, zorder=2)
            for xi, v in zip(x + dx, data[tag]):
                ax.text(xi, v + 0.015 * hi, fmt.format(v), ha="center", va="bottom", color=INK, fontsize=6.8)
        ax.set_xticks(x)
        ax.set_xticklabels([lab for _, lab in kinds])
        ax.set_xlim(-0.6, len(kinds) - 0.4)
        ax.set_ylim(0, 1.14 * hi)
        ax.set_title(title)
        ax.set_xlabel("confidence intervals behind the certificates")
    panels[0][0].legend(handles=[Patch(color=BLUE_LIGHT, lw=0, label="budget $\\ell=5\\%$"),
                                 Patch(color=BLUE_DARK, lw=0, label="budget $\\ell=10\\%$")],
                        loc="upper left", borderaxespad=0.2, labelcolor=INK2, handlelength=1.1)
    pos = panels[1][0].get_position()
    panels[1][0].set_position([pos.x0 + 0.03, pos.y0, pos.width - 0.03, pos.height])
    pos = panels[0][0].get_position()
    panels[0][0].set_position([pos.x0, pos.y0, pos.width - 0.03, pos.height])
    save(fig, out, "fig_price.pdf")


# ---------------------------------------------------------------- figure 6
def fig_noise(out):
    sig = [(0.25, "main", {}), (0.5, "noisy", {"sigma": 0.5}), (1.0, "noisy", {"sigma": 1.0})]
    fig, axes = plt.subplots(1, 4, figsize=(WIDTH, 2.05), sharex=True, sharey=True,
                             gridspec_kw=dict(wspace=0.09))
    x = np.arange(len(sig))
    for ax, m in zip(axes, MK):
        for key, lab, col, ls in SERIES:
            med = [float(np.median([r["regret"] for r in report.runs(suite, _cfg(key), m, **opts)]))
                   for _, suite, opts in sig]
            ax.plot(x, med, color=col, ls=ls, lw=1.25, zorder=3, **DOT)
        ax.set_yscale("log")
        ax.set_title(HEAD[m])
        ax.set_xlabel("noise level $\\sigma$")
    axes[0].set_ylim(30, 5000)
    axes[0].set_xlim(-0.25, len(sig) - 0.75)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"{s:g}" for s, _, _ in sig])
    axes[0].set_ylabel("median cumulative regret")
    axes[0].set_yticks([30, 100, 300, 1000, 3000])
    axes[0].set_yticklabels(["30", "100", "300", "1,000", "3,000"])
    axes[0].yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    _series_legend(fig, y=0.98, lw=1.25)
    save(fig, out, "fig_noise.pdf")


FIGURES = {"landscape": fig_landscape, "certificate": fig_certificate,
           "paths": fig_paths,
           "paths_weak": lambda out: fig_paths(out, market="m=0.3", name="fig_paths_weak.pdf"),
           "regret": fig_regret, "price": fig_price, "noise": fig_noise}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "figures"))
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for name, fn in FIGURES.items():
        if args.only is None or name in args.only:
            fn(args.out)


if __name__ == "__main__":
    main()
