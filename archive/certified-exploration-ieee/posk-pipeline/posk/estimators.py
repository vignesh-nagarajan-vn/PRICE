"""Response estimators and the anytime confidence sequence.

Three estimators, matching the theory's three regimes:
  - OLSSlope: the scalar response slope eps (T2/T3's estimand);
  - StructuralFit: the anchored p = 3 family (C0, C1, c) - grid-plus-refine
    nonlinear least squares, numpy only (T6/T7's anchored arm);
  - secant_slope: the nonparametric symmetric-difference estimator (T7's
    free-form arm).

The confidence sequence is a stitched self-normalized bound: anytime-valid
width  sigma * sqrt(2 log(2 t^2 / alpha) / S_t)  (conservative; validity is
what P7.1 consumes, tightness is not needed).
"""

from __future__ import annotations

import numpy as np


class OLSSlope:
    """Recursive least squares of tau_obs on h; slope estimate -eps_hat."""

    def __init__(self):
        self.h, self.y = [], []

    def update(self, h, y):
        self.h.append(float(h))
        self.y.append(float(y))

    @property
    def n(self):
        return len(self.h)

    def sxx(self):
        h = np.asarray(self.h)
        return float(((h - h.mean()) ** 2).sum()) if len(h) > 1 else 0.0

    def slope(self):
        h, y = np.asarray(self.h), np.asarray(self.y)
        hc = h - h.mean()
        s = (hc ** 2).sum()
        if s <= 0:
            return 0.0
        return float((hc * (y - y.mean())).sum() / s)

    def eps_hat(self):
        return -self.slope()

    def ci_width(self, sigma, alpha=0.05):
        """Anytime-valid half-width (self-normalized mixture bound)."""
        s = self.sxx()
        if s <= 0:
            return np.inf
        return sigma * np.sqrt(2 * np.log(np.sqrt(1 + s) / alpha) / s)


class StructuralFit:
    """Anchored fit of tau(h) = C0 + C1 exp(-c h) by profile least squares.

    For each candidate decay c, (C0, C1) solve a linear LS; c is chosen on a
    grid then refined by golden search. `identified` mirrors REFLEX's
    anti-echo convention: the fit is only trusted when the design has
    genuine spread (T6: >= 3 support points, enforced as a range floor).
    """

    def __init__(self, c_lo=0.2, c_hi=4.0, min_rel_range=0.05):
        self.c_lo, self.c_hi = c_lo, c_hi
        self.min_rel_range = min_rel_range

    def _profile_sse(self, c, h, y):
        X = np.column_stack([np.ones_like(h), np.exp(-c * h)])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ coef
        return float(r @ r), coef

    def fit(self, h, y):
        h, y = np.asarray(h, float), np.asarray(y, float)
        rng_ok = (h.max() - h.min()) >= self.min_rel_range * max(h.mean(), 1e-9)
        n_support = len(np.unique(np.round(h, 6)))
        cs = np.linspace(self.c_lo, self.c_hi, 60)
        sses = [self._profile_sse(c, h, y)[0] for c in cs]
        c0 = cs[int(np.argmin(sses))]
        lo, hi = max(self.c_lo, c0 - 0.15), min(self.c_hi, c0 + 0.15)
        for _ in range(50):
            m1, m2 = lo + 0.382 * (hi - lo), lo + 0.618 * (hi - lo)
            if self._profile_sse(m1, h, y)[0] > self._profile_sse(m2, h, y)[0]:
                lo = m1
            else:
                hi = m2
        c = 0.5 * (lo + hi)
        sse, coef = self._profile_sse(c, h, y)
        return {
            "C0": float(coef[0]), "C1": float(coef[1]), "c": float(c),
            "identified": bool(rng_ok and n_support >= 3 and coef[1] > 0),
            "resid_rms": float(np.sqrt(sse / max(len(h) - 3, 1))),
        }

    @staticmethod
    def eps_hat(params, h):
        return params["c"] * params["C1"] * np.exp(-params["c"] * h)


def secant_slope(env, h_center, w, n_pairs, rng=None):
    """T7's nonparametric arm: symmetric probes at h_center +/- w."""
    yp = np.array([env.deploy(h_center + w) for _ in range(n_pairs)])
    ym = np.array([env.deploy(h_center - w) for _ in range(n_pairs)])
    return (yp.mean() - ym.mean()) / (2 * w)
