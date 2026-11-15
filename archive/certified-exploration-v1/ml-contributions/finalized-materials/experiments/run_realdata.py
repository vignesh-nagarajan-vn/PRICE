"""Real-data leg: the paper's constants computed on the REFLEX calibration.

Ports the REFLEX unit mapping (endo_market_v4/reflex/calibration/mapping.py)
and the 1.1/1.2 closed forms (numpy only, no torch), then:

  1. VALIDATES the port cell-by-cell against REFLEX's published paper-grade
     run (research/results/07-12-2026/calibrated/calibrated_boundaries.csv):
     h_star, eps_star (= gamma at h_star) and m_pred must reproduce.
  2. EXTENDS each (rating x regime) cell with the paper's new objects:
     gamma_PO, the exchange rate per unit response variance (1/2) gamma_PO,
     the echo-chamber gap h_SP - h_PO, and the ROI break-even ingredients.
  3. Computes the curvature-dispersion factor F across the 212-CUSIP
     universe (per-bond vol from the monthly returns panel).

Usage:  python experiments/run_realdata.py [--reflex-root PATH]
Writes results/REALDATA.md. Skips gracefully when the REFLEX tree is absent.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

import numpy as np

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

# ---- ported unit mapping (mapping.py, verbatim constants) -----------------
PAR, SPY = 100.0, 252.0
TOXIC_INTENSITY_RATIO, TOXIC_BASE_RATIO = 1.4, 0.6
CT_TIMES_H, SIGNAL_NOISE_STEPS, MISPRICING_RATIO = 1.2, 2.4, 2.0
INV_RISK_RATIO, ANCHOR_STIFFNESS = 0.0625, 5.0
ALPHA, FEEDBACK = 0.5, 5.0  # configs/default.yaml values (the published run;
#   the DATACLASS defaults 0.15/0.22 differ - a 75.8x trap the validation caught)

_GH_X, _GH_W = np.polynomial.hermite.hermgauss(80)


def _egauss(fn):
    return float((_GH_W * fn(np.sqrt(2.0) * _GH_X)).sum() / np.sqrt(np.pi))


def gate_means(u):
    gbar = _egauss(lambda e: np.tanh(np.abs(u + e)))
    a = _egauss(lambda e: np.tanh(u + e))
    return max(gbar, 1e-9), a


class Cell:
    """One (rating, regime) calibrated market in per-100-par units."""

    def __init__(self, rating, regime, h_dec, A, k_raw, sigma_ann):
        self.rating, self.regime = rating, regime
        self.h0 = h_dec * PAR
        self.A = A
        self.k = k_raw / PAR
        self.vol = sigma_ann / np.sqrt(SPY) * PAR
        self.w = ANCHOR_STIFFNESS * A / max(self.h0, 1e-9)
        self.lam_q = INV_RISK_RATIO * self.h0 / max(A, 1e-9)
        self.I = TOXIC_INTENSITY_RATIO * A
        self.I_b = TOXIC_BASE_RATIO * A
        self.c_t = CT_TIMES_H / max(self.h0, 1e-9)
        self.sigma_s = SIGNAL_NOISE_STEPS * self.vol
        g = MISPRICING_RATIO * self.vol
        self.u = g / self.sigma_s
        self.gbar, self.a_signed = gate_means(self.u)
        self.psi = self.sigma_s * self.u * self.a_signed / self.gbar

    def tau(self, h):
        return self.gbar * (self.I_b + ALPHA * FEEDBACK * self.I
                            * np.exp(-self.c_t * h))

    def eps(self, h):
        return self.gbar * ALPHA * FEEDBACK * self.I * self.c_t \
            * np.exp(-self.c_t * h)

    def gamma(self, h):
        return 2 * self.w + self.A * self.k * np.exp(-self.k * h) \
            * (2 - self.k * h) + self.lam_q

    def gamma_po(self, h):
        return self.gamma(h) + self.eps(h) * (2 + self.c_t * self.psi
                                              - self.c_t * h)

    def foc(self, h):
        return self.A * np.exp(-self.k * h) * (1 - self.k * h) \
            + self.tau(h) - 2 * self.w * (h - self.h0)

    def h_sp(self):
        lo, hi = 1e-3, 8 * self.h0
        if self.foc(hi) > 0:
            return hi
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if self.foc(mid) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def phi(self, h):
        return h * self.A * np.exp(-self.k * h) + (h - self.psi) \
            * self.tau(h) - self.w * (h - self.h0) ** 2

    def h_po(self):
        hs = np.linspace(1e-3, 8 * self.h0, 6001)
        return float(hs[np.argmax([self.phi(x) for x in hs])])


def load_cells(reflex_root):
    path = os.path.join(reflex_root, "endo_market_v4", "data", "calibration",
                        "03_fitted_intensity_params.csv")
    cells = []
    with open(path) as f:
        for r_ in csv.DictReader(f):
            cells.append(Cell(r_["rating_bucket"], r_["regime"],
                              float(r_["h_mean_decimal"]), float(r_["sim_A"]),
                              float(r_["sim_k"]), float(r_["sim_sigma"])))
    return cells


def load_truth(reflex_root):
    path = os.path.join(reflex_root, "research", "results", "07-12-2026",
                        "calibrated", "calibrated_boundaries.csv")
    truth = {}
    with open(path) as f:
        for r_ in csv.DictReader(f):
            truth[(r_["rating"], r_["regime"])] = r_
    return truth


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reflex-root", default="/home/user/REFLEX")
    args = ap.parse_args()
    if not os.path.isdir(os.path.join(args.reflex_root, "endo_market_v4")):
        print("REFLEX tree not found - skipping real-data leg")
        return 0
    os.makedirs(RESULTS_DIR, exist_ok=True)
    cells = load_cells(args.reflex_root)
    truth = load_truth(args.reflex_root)

    lines = ["# Real-data leg: constants on the REFLEX calibration", "",
             "## 1. Port validation vs the published run (07-12-2026)", "",
             "| cell | h* (port/pub) | eps* = gamma (port/pub) | m (port/pub) |",
             "|---|---|---|---|"]
    n_ok, n_cells = 0, 0
    ext_rows = []
    for c in cells:
        t = truth.get((c.rating, c.regime))
        if t is None:
            continue
        n_cells += 1
        hs = c.h_sp()
        g = c.gamma(hs)
        m = c.eps(hs) / g
        hs_pub = float(t["h_star"])
        g_pub = float(t["eps_star"])
        m_pub = float(t["m_pred"]) if t["m_pred"] else None
        ok = (abs(hs - hs_pub) / hs_pub < 0.02
              and abs(g - g_pub) / g_pub < 0.02
              and (m_pub is None or abs(m - m_pub) / m_pub < 0.05))
        n_ok += ok
        lines.append("| %s-%s | %.3f / %.3f | %.1f / %.1f | %s / %s |%s"
                     % (c.rating, c.regime, hs, hs_pub, g, g_pub,
                        "%.4f" % m, "%.4f" % m_pub if m_pub else "-",
                        "" if ok else "  <-- MISMATCH"))
        # extension: the paper's new objects on this cell
        hpo = c.h_po()
        gpo = c.gamma_po(hs)
        ext_rows.append((c, hs, hpo, gpo, m))
    lines += ["", "**%d/%d cells reproduce the published run.**" % (n_ok, n_cells),
              "", "## 2. Extension: the paper's objects per cell", "",
              "| cell | gamma_PO | exch. rate (1/2)gamma_PO | gap h_SP-h_PO "
              "(% of h0) | m |", "|---|---|---|---|---|"]
    for c, hs, hpo, gpo, m in ext_rows:
        gap = hs - hpo
        lines.append("| %s-%s | %.1f | %.1f | %.4f (%.1f%%) | %.4f |"
                     % (c.rating, c.regime, gpo, 0.5 * gpo, gap,
                        100 * gap / c.h0, m))

    # dispersion factor across the 212-CUSIP universe (IG-normal base cell)
    ret_path = os.path.join(args.reflex_root, "endo_market_v4", "data",
                            "calibration", "reflex_G_bond_returns_monthly.csv")
    by_cusip = {}
    with open(ret_path) as f:
        for r_ in csv.DictReader(f):
            by_cusip.setdefault(r_["cusip"], []).append(
                float(r_["log_ret_monthly"]))
    vols = np.array([np.std(v) * np.sqrt(12) for v in by_cusip.values()
                     if len(v) >= 12])
    vols = vols[vols > 1e-6]     # constant-return CUSIPs carry no vol signal
    base = next(c for c in cells if c.rating == "IG" and c.regime == "normal")
    hs = base.h_sp()
    gpo_bonds = []
    for va in vols:
        cb = Cell(base.rating, base.regime, base.h0 / PAR, base.A,
                  base.k * PAR, va)
        gpo_bonds.append(cb.gamma_po(hs))
    gpo_bonds = np.array([g for g in gpo_bonds if g > 0])
    F = len(gpo_bonds) * gpo_bonds.sum() / (np.sqrt(gpo_bonds).sum()) ** 2
    lines += ["", "## 3. Curvature dispersion across the bond universe", "",
              "%d CUSIPs with >= 12 months of returns; per-bond annualized "
              "vol %.3f-%.3f (p5-p95)." % (len(gpo_bonds),
                                           np.percentile(vols, 5),
                                           np.percentile(vols, 95)),
              "",
              "**F = %.4f** on the IG-normal cell: isotropic exploration "
              "overpays the A-optimal shape by %.1f%% on this universe "
              "(C5.1). The modest value is itself a finding: at these "
              "anchor-dominated curvatures the real-data dispersion is "
              "small - the shaping gain concentrates in the toxic-channel "
              "term, which is structurally scaled (see the mapping's "
              "provenance caveat)." % (F, 100 * (F - 1)),
              "", "## Provenance (inherited, binding)",
              "", "Only (A, k, sigma, h) are data-identified; the toxic "
              "channel is structurally scaled (documented ratios in "
              "mapping.py). Not trade-level TRACE. The port validation in "
              "section 1 is against REFLEX's own published run, not against "
              "market ground truth."]
    out = os.path.join(RESULTS_DIR, "REALDATA.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:20]))
    print("... -> %s" % out)
    return 0 if n_ok == n_cells else 1


if __name__ == "__main__":
    sys.exit(main())
