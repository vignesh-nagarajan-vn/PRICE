"""Second domain: performative dynamic pricing (linear-quadratic).

A seller posts price p; demand carries a performative reference effect - the
DEPLOYED price shifts willingness-to-pay (habituation/anchoring):

    demand:   q(p; p_dep) = a - b p + g p_dep + zeta,   zeta ~ N(0, sigma^2)
    profit:   J(p; theta) = p (theta - b p),    theta = a + g p_dep  (frozen intercept)
    performative objective:  Phi(p) = p (a + (g - b) p)

Every register object has an exact LQ instance (no local-quadratic caveat:
A1 holds globally), which is the point of the domain - the same laws, a
different economy, zero shared code with the market model:

    gamma   = 2b          beta = 1        eps = g         m = g / (2b)
    gamma_PO = 2 (b - g)                  p_SP = a / (2b - g)
    p_PO = a / (2 (b - g))                exchange rate = (1/2) gamma_PO sigma^2

The estimand is the reference gain g - the seller's own performativity.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PricingMarket:
    a: float = 10.0     # demand intercept
    b: float = 1.0      # own-price slope
    g: float = 0.6      # performative reference gain (the estimand)
    sigma: float = 0.8  # demand noise sd
    p_lo: float = 0.5
    p_hi: float = 16.0

    def demand(self, p, p_dep):
        return self.a - self.b * p + self.g * p_dep

    def Phi(self, p):
        return p * (self.a + (self.g - self.b) * p)

    @property
    def gamma(self):
        return 2 * self.b

    @property
    def gamma_po(self):
        return 2 * (self.b - self.g)

    @property
    def modulus(self):
        return self.g / (2 * self.b)

    @property
    def p_sp(self):
        return self.a / (2 * self.b - self.g)

    @property
    def p_po(self):
        return self.a / (2 * (self.b - self.g))

    def exchange_rate(self):
        return 0.5 * self.gamma_po * self.sigma ** 2

    def best_response(self, theta):
        """argmax_p p (theta - b p) = theta / (2b), clipped."""
        return float(np.clip(theta / (2 * self.b), self.p_lo, self.p_hi))


class PricingEnv:
    """Deploy a price, observe one noisy demand realization."""

    def __init__(self, market: PricingMarket, seed: int = 0):
        self.m = market
        self.rng = np.random.default_rng(seed)
        self.p_dep = market.p_sp   # environment reacts to the LAST deployment

    def deploy(self, p):
        p = float(np.clip(p, self.m.p_lo, self.m.p_hi))
        q = self.m.demand(p, self.p_dep) \
            + self.m.sigma * self.rng.standard_normal()
        self.p_dep = p
        return q


class PricingSafeD:
    """SafeD-PerfGD transplanted to the pricing domain.

    The response family here is linear (intercept theta responds to p_dep
    with slope g), so the anchored fit is OLS of demand on the DEPLOYED
    price lag - two parameters, identified by any two-point design. The
    gate, correction and Newton scaling carry over verbatim, which is
    itself the domain-transfer claim: nothing in the architecture is
    market-making-specific.
    """

    def __init__(self, market, p0, r=1.2, margin=0.25, alpha=0.05, seed=0):
        self.m = market
        self.p = float(p0)
        self.r = r
        self.margin = margin
        self.alpha = alpha
        self.prev_dep = None
        self.rows = []      # (p_dep_lag, p_now, q_obs)
        self.g_hat = 0.0
        self.ci = np.inf
        self.rng = np.random.default_rng(seed)
        self.frozen_steps = 0
        self.corrected_steps = 0

    def act(self):
        # RANDOM probe sign: a deterministic alternation makes p_now and the
        # lag column perfectly anti-correlated (p_now + p_lag = const), so
        # (b, g) are collinear and g is unidentifiable - a design-degeneracy
        # instance of T6, caught by the frozen gate in the first run and
        # fixed here (pivot recorded).
        sgn = 1.0 if self.rng.random() < 0.5 else -1.0
        return float(np.clip(self.p + sgn * self.r / np.sqrt(2),
                             self.m.p_lo, self.m.p_hi))

    def observe(self, p_now, q_obs):
        if self.prev_dep is not None:
            self.rows.append((self.prev_dep, p_now, q_obs))
        self.prev_dep = p_now
        if len(self.rows) < 8:
            return
        Z = np.asarray(self.rows[-2400:])
        X = np.column_stack([np.ones(len(Z)), -Z[:, 1], Z[:, 0]])
        coef, *_ = np.linalg.lstsq(X, Z[:, 2], rcond=None)
        a_hat, b_hat, g_hat = coef[0], coef[1], max(coef[2], 0.0)
        self.g_hat = g_hat
        # anytime CI for g via the design energy of the lag column
        lag = Z[:, 0]
        s = ((lag - lag.mean()) ** 2).sum()
        self.ci = self.m.sigma * np.sqrt(
            2 * np.log(np.sqrt(1 + s) / self.alpha) / max(s, 1e-9))
        gamma_po_hat = 2 * (b_hat - g_hat)
        eta = 1.0 / max(gamma_po_hat, 2 * b_hat * 0.25, 0.5)
        if eta * self.ci * 2.0 > self.margin:     # L4-style pessimism (L_fam=2)
            self.frozen_steps += 1
            self.p = self.m.best_response(a_hat + g_hat * self.p)  # blind, stable
            return
        self.corrected_steps += 1
        # exact PerfGD step for LQ: Phi'(p) = a_hat + 2 (g_hat - b_hat) p
        grad = a_hat + 2 * (g_hat - b_hat) * self.p
        self.p = float(np.clip(self.p + eta * grad, self.m.p_lo, self.m.p_hi))
