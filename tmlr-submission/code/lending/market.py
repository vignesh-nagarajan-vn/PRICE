"""Lending markets: take-up curves, profit per quote, and acceptance draws.

A market fixes the break-even spread psi, a take-up curve a(s) (the probability that a quoted applicant takes
the offer at rate s), and the admissible range [lo, hi] of rates.  Rates are markups in percentage points
relative to the competing-offer benchmark of the borrower's segment.  Expected profit per quote is
Phi(s) = (s - psi) a(s), in percentage points of balance per year.
"""
import json
import math

import numpy as np

_ZT = np.linspace(-9.0, 9.0, 36001)
_PT = np.array([0.5 * (1.0 + math.erf(z / math.sqrt(2.0))) for z in _ZT])


def ncdf(z):
    """Standard normal cdf by table interpolation (error below 1e-8)."""
    return np.interp(z, _ZT, _PT)


class Market:
    def __init__(self, a, psi, lo, hi, name=""):
        self._a, self.psi, self.lo, self.hi, self.name = a, float(psi), float(lo), float(hi), name
        g = np.linspace(max(self.lo, self.psi), self.hi, 40001)
        av = np.concatenate([self.a(c) for c in np.array_split(g, 40)])   # in chunks, to bound memory
        p = (g - self.psi) * av
        k = int(np.argmax(p))
        self.s_star, self.phi_star = float(g[k]), float(p[k])
        self.max_slope = float(np.max(np.abs(np.diff(av) / np.diff(g))))   # sup |a'| on the range, numerically

    def a(self, s):
        return np.clip(self._a(np.asarray(s, float)), 0.0, 1.0)

    def phi(self, s):
        s = np.asarray(s, float)
        return (s - self.psi) * self.a(s)

    def draw(self, rng, s, n):
        """Number of acceptances among n quotes at rate s."""
        return int(rng.binomial(int(n), float(self.a(s))))


class ShoppingMarket(Market):
    """Take-up of a borrower who holds K competing quotes: a(s) = (1 - F(s))^K, with F the volume-weighted,
    kernel-smoothed distribution of lender markups estimated from HMDA (code/hmda_offers.py)."""

    def __init__(self, markups, weights, bw, K, psi, lo, hi, name=""):
        self.m = np.asarray(markups, float)
        self.w = np.asarray(weights, float) / np.sum(weights)
        self.bw, self.K = float(bw), int(K)
        super().__init__(self._take_up, psi, lo, hi, name)

    def F(self, s):
        s = np.atleast_1d(np.asarray(s, float))
        return ncdf((s[:, None] - self.m[None, :]) / self.bw) @ self.w

    def _take_up(self, s):
        shape = np.shape(s)
        return ((1.0 - self.F(s)) ** self.K).reshape(shape)

    def quantile(self, q):
        """Volume-weighted quantile of lender markups (the starting rates of the experiments)."""
        o = np.argsort(self.m)
        c = np.cumsum(self.w[o])
        return float(np.interp(q, c, self.m[o]))

    @classmethod
    def from_hmda(cls, path, K):
        d = json.load(open(path))
        r = d["K"][str(K)]
        lo, hi, _ = d["grid"]
        tag = d["file"].replace("hmda_", "").replace("_purchase.csv", "")
        return cls(d["markups"], d["weights"], d["bandwidth"], K, r["psi"], lo, hi, name=f"{tag}/K={K}")


class LogisticMarket(Market):
    """a(s) = c / (1 + exp((s - mu) / scale)): a synthetic market for tests."""

    def __init__(self, c=0.9, mu=0.3, scale=0.15, psi=-0.2, lo=-0.6, hi=1.5):
        super().__init__(lambda s: c / (1.0 + np.exp((s - mu) / scale)), psi, lo, hi, name="logistic")
