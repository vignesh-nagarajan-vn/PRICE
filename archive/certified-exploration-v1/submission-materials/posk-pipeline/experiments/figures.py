"""Paper figures. Each mirrors an experiment's exact measurement (same
code paths, smaller settings) - no figure shows anything the suite does
not verify. Writes PNGs to results/figures/.

Run `python experiments/run_all.py` first: fig5 (baselines) and fig4's
CSV fallback read the suite's artifacts when present.

Usage: python experiments/figures.py [--fast]
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from posk.agents import BlindRRM, SafeDPerfGD, run_agent  # noqa: E402
from posk.design import d_optimal_3pt  # noqa: E402
from posk.env import StructuralEnv  # noqa: E402
from posk.estimators import StructuralFit  # noqa: E402
from posk.theory import Market  # noqa: E402
from run_open1 import struct_ratio  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")

STYLE = dict(color="#1f77b4"), dict(color="#d62728"), dict(color="#2ca02c")


def _save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  wrote %s" % path)


# ------------------------------------------------------------ fig 1: T2
def fig_exchange_rate(fast):
    T = 1500 if fast else 3000
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    for tgt, col in ((0.3, "#1f77b4"), (0.6, "#d62728")):
        mkt = Market(sigma=0.25).feedback_for_modulus(tgt)
        hs = mkt.h_sp()
        pred = mkt.exchange_rate()
        s_grid = [0.03, 0.05, 0.08, 0.15, 0.25]
        prods = []
        for s_e in s_grid:
            rng = np.random.default_rng(7)
            env = StructuralEnv(mkt, seed=17)
            h, hh = hs, []
            for t in range(T):
                env.deploy(h)
                hh.append(h)
                y_retrain = mkt.tau(h) + mkt.sigma / 5.0 \
                    * rng.standard_normal()
                h = mkt.best_response(y_retrain) + s_e * rng.standard_normal()
            hh = np.asarray(hh[200:])
            hc = hh - hh.mean()
            var_eps = mkt.sigma ** 2 / float((hc ** 2).sum())
            cost = float(np.sum(mkt.Phi(hh.mean()) - mkt.Phi(hh)))
            prods.append(var_eps * cost)
        ax.plot(s_grid, prods, "o-", color=col,
                label="measured, m = %.1f" % tgt)
        ax.axhline(pred, color=col, ls="--", lw=1,
                   label=r"$\frac{1}{2}\gamma_{PO}\sigma^2$, m = %.1f" % tgt)
    ax.set_xlabel("exploration amplitude $s_e$")
    ax.set_ylabel(r"Var$(\hat\varepsilon) \times C_T$")
    ax.set_title("The exchange rate is invariant to how you explore (T2)")
    ax.legend(fontsize=7)
    _save(fig, "fig1_exchange_rate.png")


# ------------------------------------------------------------ fig 2: T1
def fig_saturation(fast):
    from dataclasses import replace
    d0 = 0.10
    ms = np.array([0.2, 0.35, 0.5, 0.65, 0.8, 0.9])
    meas = []
    for tgt in ms:
        mkt = Market(sigma=0.25).feedback_for_modulus(float(tgt))
        mkt0 = replace(mkt, sigma=0.0)
        hs = mkt.h_sp()
        env0 = StructuralEnv(mkt0, seed=1)
        path0 = run_agent(BlindRRM(mkt0, hs + d0), env0, 300)
        meas.append(float(((path0 - hs) ** 2).sum()))
    grid = np.linspace(0.05, 0.93, 200)
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    ax.plot(grid, d0 ** 2 / (1 - grid ** 2), "-", color="#1f77b4",
            label=r"cap $d_0^2/(1-m^2)$ (T1)")
    ax.plot(ms, meas, "o", color="#d62728", label="measured loop energy")
    ax.set_xlabel("modulus $m$")
    ax.set_ylabel("cumulative squared deviation")
    ax.set_title("Information saturation: free data is capped (T1)")
    ax.legend()
    _save(fig, "fig2_saturation.png")


# ---------------------------------------------------- fig 3: gate timeline
def fig_certification(fast):
    T = 2500 if fast else 4000
    mkt = Market(sigma=0.25).feedback_for_modulus(0.6)
    hs, hpo = mkt.h_sp(), mkt.h_po()
    env = StructuralEnv(mkt, seed=99)
    ag = SafeDPerfGD(mkt, h0=hs, r=0.6, margin=0.3, refit_every=10)
    centers, frozen = [], []
    fs = 0
    for _ in range(T):
        h = ag.act()
        y = env.deploy(h)
        ag.observe(h, y)
        centers.append(ag.h)
        frozen.append(ag.frozen_steps > fs)
        fs = ag.frozen_steps
    centers = np.asarray(centers)
    frozen = np.asarray(frozen)
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    t = np.arange(T)
    # shade frozen episodes
    in_f = False
    for i in range(T):
        if frozen[i] and not in_f:
            start, in_f = i, True
        if in_f and (not frozen[i] or i == T - 1):
            ax.axvspan(start, i, color="#f0c0c0", alpha=0.5, lw=0)
            in_f = False
    ax.plot(t, centers, color="#1f77b4", lw=1.2, label="operating point $h_t$")
    ax.axhline(hs, color="k", ls=":", lw=1, label="$h_{SP}$ (blind fix point)")
    ax.axhline(hpo, color="#2ca02c", ls="--", lw=1.2,
               label="$h_{PO}$ (performative optimum)")
    ax.set_xlabel("deployment $t$")
    ax.set_ylabel("spread $h$")
    ax.set_title("Certification before exploitation: the gate timeline "
                 "(shaded = frozen)")
    ax.legend(fontsize=8, loc="center right")
    _save(fig, "fig3_certification.png")


# ---------------------------------------------------- fig 4: T7 crossover
def fig_crossover(fast):
    mkt = Market(sigma=0.25).feedback_for_modulus(0.5)
    hs = mkt.h_sp()
    B, T = 0.6, 120
    mse_np_pred = mkt.mse_np(B, T)
    csv_path = os.path.join(RESULTS_DIR, "e5_anchor_mse.csv")
    if os.path.exists(csv_path):
        arr = np.loadtxt(csv_path, delimiter=",", skiprows=1)
        a_grid, mse_anchor = arr[:, 0], arr[:, 1]
    else:   # self-contained smaller recompute
        seeds = 150
        fit = StructuralFit()
        S = 2 * B / mkt.gamma_po(hs)
        w = float(np.sqrt(S / T))
        pts = d_optimal_3pt(hs, w * np.sqrt(3.0 / 2.0), mkt.C1, mkt.c)

        class MisEnv(StructuralEnv):
            def __init__(self, market, a, seed):
                super().__init__(market, seed)
                self.a = a

            def true_tau(self, h):
                return self.m.tau(h) - self.a * h

        a_grid = np.array([0.0, 0.05, 0.1, 0.2, 0.35])
        mse_anchor = []
        for a in a_grid:
            errs = np.empty(seeds)
            eps_true = mkt.eps(hs) + a
            for s in range(seeds):
                env = MisEnv(mkt, a, seed=40_000 + s)
                hh = np.tile(pts, T // 3 + 1)[:T]
                yy = np.array([env.deploy(h) for h in hh])
                errs[s] = StructuralFit.eps_hat(fit.fit(hh, yy), hs) - eps_true
            mse_anchor.append(float((errs ** 2).mean()))
        mse_anchor = np.asarray(mse_anchor)
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    ax.plot(a_grid, mse_anchor, "o-", color="#1f77b4",
            label="anchored (structural fit)")
    ax.axhline(mse_np_pred, color="#d62728", ls="--",
               label="nonparametric optimum (T7)")
    ax.set_xlabel("misspecification size $a$ (linear leak)")
    ax.set_ylabel(r"MSE of $\hat\varepsilon$")
    ax.set_title("Anchoring wins short-horizon, until the model is wrong (T7)")
    ax.legend()
    _save(fig, "fig4_crossover.png")


# ---------------------------------------------------- fig 5: baselines
def fig_baselines(fast):
    csv_path = os.path.join(RESULTS_DIR, "e6_baselines.csv")
    if not os.path.exists(csv_path):
        print("  fig5 skipped (run run_all.py first: needs e6_baselines.csv)")
        return
    with open(csv_path) as f:
        rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
    n_seeds = rows[0].get("n_seeds", "?") if rows else "?"
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    for r_ in rows:
        e, reg = float(r_["err_median"]), float(r_["regret_median"])
        e1, e3 = float(r_["err_q1"]), float(r_["err_q3"])
        r1, r3 = float(r_["regret_q1"]), float(r_["regret_q3"])
        is_safe = r_["baseline"] == "SafeD-PerfGD"
        col = "#d62728" if is_safe else "#1f77b4"
        e, reg = max(e, 1e-4), max(reg, 1e-1)
        ax.errorbar(e, reg,
                    xerr=[[max(e - e1, 0)], [max(e3 - e, 0)]],
                    yerr=[[max(reg - r1, 0)], [max(r3 - reg, 0)]],
                    fmt="o", ms=9 if is_safe else 6, color=col,
                    ecolor=col, elinewidth=1.2, capsize=3,
                    zorder=3 if is_safe else 2)
        ax.annotate(r_["baseline"], (e, reg),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"final error $|\bar h_{\rm tail} - h_{PO}|$ (median, IQR)")
    ax.set_ylabel("cumulative performative regret (median, IQR)")
    ax.set_title("Safety and identification are purchased (E6):\n"
                 "no baseline dominates SafeD-PerfGD (medians, %s seeds)"
                 % n_seeds, fontsize=10)
    _save(fig, "fig5_baselines.png")


# ---------------------------------------------------- fig 6: OPEN-1
def fig_open1(fast):
    m = Market()
    hstar = m.h_po()
    ts = np.linspace(0.05, hstar - 0.15, 25)
    best = []
    for t in ts:
        b = np.inf
        for wt in (0.05, 0.1, 0.2, 0.4):
            pts = np.array([hstar - 0.1, hstar + 0.1, t])
            wts = np.array([(1 - wt) / 2, (1 - wt) / 2, wt])
            b = min(b, struct_ratio(m, hstar, pts, wts, "true"))
        best.append(b)
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    ax.plot(ts, best, "-", color="#1f77b4",
            label="best Cramer-Rao ratio with a tight probe at $t$")
    ax.axhline(1.0, color="#d62728", ls="--",
               label=r"floor $\frac{1}{2}\gamma_{PO}\sigma^2$")
    ax.set_xlabel("tight-probe location $t$  (anchor $h^*$ = %.2f)" % hstar)
    ax.set_ylabel(r"(Var $\times$ cost) / floor")
    ax.set_yscale("log")
    ax.set_title("The floor is structure-proof: tight-side probing "
                 "only hurts (OPEN-1)")
    ax.legend(fontsize=8)
    _save(fig, "fig6_open1.png")


# ---------------------------------------------------- fig 7: real data
def fig_realdata(fast):
    try:
        import run_realdata as rd
    except Exception as e:  # pragma: no cover
        print("  fig7 skipped (%s)" % e)
        return
    root = "/home/user/REFLEX"
    if not os.path.isdir(os.path.join(root, "endo_market_v4")):
        print("  fig7 skipped (REFLEX tree not found)")
        return
    cells = rd.load_cells(root)
    names, gpos, gaps = [], [], []
    for c in cells:
        hs = c.h_sp()
        names.append("%s\n%s" % (c.rating, c.regime))
        gpos.append(c.gamma_po(hs))
        gaps.append(100 * (hs - c.h_po()) / c.h0)
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.bar(x - 0.2, gpos, 0.4, color="#1f77b4",
           label=r"$\gamma_{PO}$ (log scale)")
    ax.set_yscale("log")
    ax.set_ylabel(r"$\gamma_{PO}$ per 100 par")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, gaps, 0.4, color="#d62728",
            label="echo-chamber gap (% of anchor)")
    ax2.set_ylabel(r"$h_{SP} - h_{PO}$ (% of $h_0$)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7)
    ax.set_title("The paper's constants on the REFLEX calibration "
                 "(10 rating x regime cells)")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper right")
    _save(fig, "fig7_realdata.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    os.makedirs(FIG_DIR, exist_ok=True)
    for fn in (fig_exchange_rate, fig_saturation, fig_certification,
               fig_crossover, fig_baselines, fig_open1, fig_realdata):
        fn(args.fast)
    print("figures -> %s" % FIG_DIR)


if __name__ == "__main__":
    main()
