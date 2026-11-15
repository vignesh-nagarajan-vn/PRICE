"""Dealer quoting model with a spread-dependent responsive flow.

A dealer quotes a half-spread h.  Profit per period is

    Phi(h) = K(h) + (h - psi) * tau(h),

where K is the part of profit the desk already models (benign flow revenue
minus a convex penalty for leaving a reference spread), tau(h) is the mean
flow of the price-responsive client segment, and psi is the average
post-trade markout cost of that segment.  The dealer knows K and psi and
observes tau(h) + noise at the quote it deploys.  It does not know tau.

The numerical instance uses  U(h) = A exp(-k h)  and
tau(h) = C0 + C1 exp(-c h).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class Market:
    # known to the dealer
    A: float = 1.0       # benign arrival scale
    k: float = 1.5       # benign flow decay
    w: float = 0.25      # weight of the reference-spread penalty
    href: float = 1.0    # reference spread
    psi: float = 0.4     # markout cost per unit of responsive flow
    # not known to the dealer
    C0: float = 0.6      # insensitive part of the responsive flow
    C1: float = 0.9      # scale of the spread-sensitive part (feedback strength)
    c: float = 1.5       # decay of the spread-sensitive part
    sigma: float = 0.25  # sd of the flow observation noise
    h_hi: float = 4.0    # widest admissible quote

    # ---- known part -------------------------------------------------
    def U(self, h):
        return self.A * np.exp(-self.k * h)

    def K(self, h):
        return h * self.U(h) - self.w * (h - self.href) ** 2

    def Kp(self, h):
        return self.A * np.exp(-self.k * h) * (1 - self.k * h) - 2 * self.w * (h - self.href)

    def gamma(self, h):
        """-K''(h)."""
        return self.A * self.k * np.exp(-self.k * h) * (2 - self.k * h) + 2 * self.w

    # ---- responsive flow --------------------------------------------
    def tau(self, h):
        return self.C0 + self.C1 * np.exp(-self.c * h)

    def eps(self, h):
        """-tau'(h)."""
        return self.c * self.C1 * np.exp(-self.c * h)

    def tau2(self, h):
        """tau''(h)."""
        return self.c ** 2 * self.C1 * np.exp(-self.c * h)

    def tau3(self, h):
        """tau'''(h)."""
        return -self.c ** 3 * self.C1 * np.exp(-self.c * h)

    # ---- profit ------------------------------------------------------
    def J(self, h, t):
        """Profit at quote h if the responsive flow were frozen at t."""
        return self.K(h) + (h - self.psi) * t

    def Phi(self, h):
        return self.K(h) + (h - self.psi) * self.tau(h)

    def dPhi(self, h):
        return self.Kp(h) + self.tau(h) - (h - self.psi) * self.eps(h)

    def gamma_po(self, h):
        """-Phi''(h) = gamma + 2 eps - (h - psi) tau''."""
        return self.gamma(h) + 2 * self.eps(h) - (h - self.psi) * self.tau2(h)

    # ---- retraining ---------------------------------------------------
    def best_response(self, t, lo=None, hi=None):
        """argmax_h J(h; t) on [lo, hi]; J is strictly concave in h."""
        lo = self.psi if lo is None else lo
        hi = self.h_hi if hi is None else hi
        if self.Kp(lo) + t <= 0:
            return lo
        if self.Kp(hi) + t >= 0:
            return hi
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if self.Kp(mid) + t > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def stable_point(self):
        """The performatively stable quote: the root of K'(h) + tau(h)."""
        lo, hi = self.psi, self.h_hi
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if self.Kp(mid) + self.tau(mid) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def optimum(self):
        """argmax of Phi on [psi, h_hi] (grid search, then golden section)."""
        hs = np.linspace(self.psi, self.h_hi, 20001)
        j = int(np.argmax(self.Phi(hs)))
        lo, hi = hs[max(j - 1, 0)], hs[min(j + 1, len(hs) - 1)]
        r = 0.5 * (np.sqrt(5.0) - 1)
        for _ in range(120):
            a, b = hi - r * (hi - lo), lo + r * (hi - lo)
            if self.Phi(a) < self.Phi(b):
                lo = a
            else:
                hi = b
        return 0.5 * (lo + hi)

    def modulus(self, h=None):
        """|slope of the retraining map| at h: eps / gamma."""
        h = self.stable_point() if h is None else h
        return self.eps(h) / self.gamma(h)

    def with_modulus(self, target):
        """A copy with C1 chosen so that the modulus at the stable quote is `target`."""
        lo, hi = 1e-3, 60.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if replace(self, C1=mid).modulus() < target:
                lo = mid
            else:
                hi = mid
        return replace(self, C1=0.5 * (lo + hi))


@dataclass(frozen=True)
class LogisticMarket(Market):
    """Responsive flow tau(h) = C0 + C1 / (1 + exp(c (h - hmid))).

    The curve is concave for h < hmid, so the convexity assumption of the
    certificates fails there.  Used only for the misspecification study.
    """
    hmid: float = 1.6

    def _s(self, h):
        return 1.0 / (1.0 + np.exp(self.c * (h - self.hmid)))

    def tau(self, h):
        return self.C0 + self.C1 * self._s(h)

    def eps(self, h):
        s = self._s(h)
        return self.c * self.C1 * s * (1 - s)

    def tau2(self, h):
        s = self._s(h)
        return self.c ** 2 * self.C1 * s * (1 - s) * (1 - 2 * s)

    def tau3(self, h):
        s = self._s(h)
        return -self.c ** 3 * self.C1 * s * (1 - s) * (1 - 6 * s + 6 * s * s)


class Env:
    """Deploy a quote, observe one noisy realization of the responsive flow."""

    def __init__(self, market, seed=0, noise="gauss"):
        self.m = market
        self.rng = np.random.default_rng(seed)
        self.noise = noise
        # Poisson counts: flow = count / scale, with the scale chosen so that the
        # standard deviation at the stable quote equals market.sigma.
        self.scale = float(market.tau(market.stable_point())) / market.sigma ** 2

    def _z(self):
        if self.noise == "gauss":
            return self.rng.standard_normal()
        if self.noise == "laplace":          # unit variance
            return self.rng.laplace(0.0, 1.0 / np.sqrt(2.0))
        if self.noise == "student5":         # unit variance
            return self.rng.standard_t(5) / np.sqrt(5.0 / 3.0)
        if self.noise == "uniform":          # unit variance, bounded
            return self.rng.uniform(-np.sqrt(3.0), np.sqrt(3.0))
        raise ValueError(self.noise)

    def deploy(self, h):
        if self.noise == "poisson":          # variance grows with the flow level
            return float(self.rng.poisson(self.scale * float(self.m.tau(h)))) / self.scale
        return float(self.m.tau(h)) + self.m.sigma * self._z()


def standard_markets(sigma=0.25):
    """The four markets used in the experiments."""
    base = Market(sigma=sigma)
    out = {f"m={m}": base.with_modulus(m) for m in (0.3, 0.6, 0.8)}
    out["m=1.09"] = replace(base, C1=20.0)
    return out
