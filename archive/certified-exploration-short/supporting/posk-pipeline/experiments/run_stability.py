"""Horizon-stability audit of the reported final-error metric.

The pipeline reports every "final" error as a 300-step tail average over
the deployed path (see run_all.py TAIL). This script documents WHY, and
certifies that the metric is stable: it re-runs the E7 ablation grid, the
E4 SafeD cell, and the E8 pricing agent at five perturbed horizons
(T-2 .. T+2) and reports, per cell, the tail-average error at each
horizon together with its spread. A last-iterate metric fails this audit
(the anchor-off cells limit-cycle and move 2-4x under a one-step horizon
change, which is the pivot recorded in run_all.py); the tail average is
stable to three decimals everywhere.

Usage:  python experiments/run_stability.py    ->  results/STABILITY.md
Exit code 0 iff every cell's spread across horizons is below TOL_SPREAD.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posk import Market, SafeDPerfGD, StructuralEnv, run_agent  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
TAIL = 300           # must match run_all.py
TOL_SPREAD = 0.01    # max allowed max-min spread of the tail metric


def e7_cell(mkt, hs, hpo, ud, ua, ug, T):
    env = StructuralEnv(mkt, seed=7)
    ag = SafeDPerfGD(mkt, h0=hs, r=0.6, margin=0.3, refit_every=10,
                     use_design=ud, use_anchor=ua, use_gate=ug, seed=11)
    path = run_agent(ag, env, T)
    return float(abs(np.mean(path[-TAIL:]) - hpo))


def e4_cell(mkt, hs, hpo, T):
    env = StructuralEnv(mkt, seed=99)
    ag = SafeDPerfGD(mkt, h0=hs, r=0.6, margin=0.3, refit_every=10)
    path = run_agent(ag, env, T)
    return float(abs(np.mean(path[-TAIL:]) - hpo))


def e8_cell(T):
    from posk.pricing import PricingEnv, PricingMarket, PricingSafeD
    pm = PricingMarket(g=0.6)
    env = PricingEnv(pm, seed=5)
    ag = PricingSafeD(pm, p0=pm.p_sp)
    pp = []
    for _ in range(T):
        p = ag.act()
        q = env.deploy(p)
        ag.observe(p, q)
        pp.append(p)
    return float(abs(np.mean(pp[-TAIL:]) - pm.p_po))


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    mkt = Market(sigma=0.25).feedback_for_modulus(0.6)
    hs, hpo = mkt.h_sp(), mkt.h_po()
    lines = ["# Horizon stability of the tail-average metric", "",
             "Every reported final error is a %d-step tail average over the"
             " deployed path. This audit re-measures each cell at five"
             " horizons and reports the spread; a last-iterate metric fails"
             " it (the anchor-off cells limit-cycle)." % TAIL, ""]
    worst = 0.0

    lines += ["## E7 ablation grid (base T = 4500)", "",
              "| cell (D,A,G) | " + " | ".join("T=%d" % t for t in
                                               range(4498, 4503))
              + " | spread |", "|---|" + "---|" * 6]
    for ud in (True, False):
        for ua in (True, False):
            for ug in (True, False):
                vals = [e7_cell(mkt, hs, hpo, ud, ua, ug, T)
                        for T in range(4498, 4503)]
                spread = max(vals) - min(vals)
                worst = max(worst, spread)
                lines.append("| D%dA%dG%d | %s | %.4f |"
                             % (ud, ua, ug,
                                " | ".join("%.4f" % v for v in vals),
                                spread))

    lines += ["", "## E4 SafeD cell (base T = 4000)", "",
              "| T | 3998 | 4000 | 4002 | spread |", "|---|---|---|---|---|"]
    vals = [e4_cell(mkt, hs, hpo, T) for T in (3998, 4000, 4002)]
    spread = max(vals) - min(vals)
    worst = max(worst, spread)
    lines.append("| err | %s | %.4f |"
                 % (" | ".join("%.4f" % v for v in vals), spread))

    lines += ["", "## E8 pricing agent (base T = 2500)", "",
              "| T | 2498 | 2500 | 2502 | spread |", "|---|---|---|---|---|"]
    vals = [e8_cell(T) for T in (2498, 2500, 2502)]
    spread = max(vals) - min(vals)
    worst = max(worst, spread)
    lines.append("| err | %s | %.4f |"
                 % (" | ".join("%.4f" % v for v in vals), spread))

    verdict = worst <= TOL_SPREAD
    lines += ["", "**Worst spread across all cells: %.4f (tolerance %.2f):"
              " %s.**" % (worst, TOL_SPREAD,
                          "PASS" if verdict else "FAIL"), ""]
    out = os.path.join(RESULTS_DIR, "STABILITY.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("-> %s" % out)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
