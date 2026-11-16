"""Exploration design: the theory's optimal shapes made operational.

Scalar market: the D-optimal design for the p = 3 structural family on the
trust-region interval [h0 - r, h0 + r] (T6: three support points including
both endpoints; interior point found numerically). d-dimensional linear
problem: the A-optimal shape Gamma^{-1/2} (T5a) and the isotropic baseline
(C5.1's contrast).
"""

from __future__ import annotations

import numpy as np

from .theory import a_optimal_design  # noqa: F401  (re-export)


def sensitivity(h, C1, c):
    """s(h) for tau = C0 + C1 e^{-ch}: (1, e^{-ch}, -C1 h e^{-ch})."""
    e = np.exp(-c * h)
    return np.array([1.0, e, -C1 * h * e])


def fisher(design_pts, weights, C1, c):
    M = np.zeros((3, 3))
    for h, wgt in zip(design_pts, weights):
        s = sensitivity(h, C1, c)
        M += wgt * np.outer(s, s)
    return M


def d_optimal_3pt(h0, r, C1, c):
    """D-optimal 3-point design on [h0-r, h0+r]: endpoints + best interior."""
    lo, hi = h0 - r, h0 + r
    best, best_mid = -np.inf, h0
    for mid in np.linspace(lo + 0.05 * r, hi - 0.05 * r, 61):
        M = fisher([lo, mid, hi], [1 / 3] * 3, C1, c)
        val = np.linalg.slogdet(M)[1]
        if val > best:
            best, best_mid = val, mid
    return np.array([lo, best_mid, hi])


class ScalarScheduler:
    """Deployment scheduler for the SafeD-PerfGD agent.

    Cycles through the 3-point D-optimal support, re-centred on the current
    operating point, sized to the per-step budget share, clipped to the
    trust region. Under L3, only the visiting frequencies matter, so a
    deterministic cycle is as good as randomization and is CRN-friendly.
    """

    def __init__(self, r, budget_frac=1.0):
        self.r = r
        self.budget_frac = budget_frac
        self._i = 0

    def next_probe(self, h_center, C1_hat, c_hat):
        pts = d_optimal_3pt(h_center, self.r * self.budget_frac,
                            max(C1_hat, 1e-3), np.clip(c_hat, 0.2, 4.0))
        h = pts[self._i % 3]
        self._i += 1
        return float(h)


def isotropic_design(Gamma, B):
    """C5.1's baseline: M = (B / tr Gamma) I at matched budget."""
    d = Gamma.shape[0]
    return (B / np.trace(Gamma)) * np.eye(d)
