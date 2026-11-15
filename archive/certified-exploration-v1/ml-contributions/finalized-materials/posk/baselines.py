"""Published-literature baselines, implemented in this environment.

- FDPerfGD: Izzo et al. (ICML 2021)-style performative gradient descent -
  the distribution response is estimated by FINITE DIFFERENCES across
  paired perturbed deployments, then the corrected gradient is ascended.
  No design shaping, no anchoring, no safety gate.
- ZOPerfOpt: zeroth-order performative optimization - two-point profit
  (P&L) differences estimate the TOTAL performative gradient Phi' directly
  (no structural knowledge at all), with the standard 1/(2 delta) estimator.
- UCBGrid: a performative-confidence-bounds explorer in the spirit of
  Jagadeesan et al. (ICML 2022): a grid of candidate deployments; deploying
  an arm yields flow samples that estimate tau(arm); the performative risk
  of EVERY arm is then bounded using the known loss plus a Lipschitz bound
  on the unexplored response, and the optimistic arm is deployed.

All baselines see exactly the interface SafeD-PerfGD sees (deploy ->
observe flow; optionally observe noisy P&L). None receives oracle
quantities.
"""

from __future__ import annotations

import numpy as np

from .estimators import OLSSlope


class FDPerfGD:
    """Finite-difference PerfGD (Izzo-style): paired probes h +/- delta_fd."""

    def __init__(self, market, h0, delta_fd=0.15, eta=None, pair_every=2,
                 seed=0):
        self.market = market
        self.h = float(h0)
        self.delta_fd = delta_fd
        self.eta = eta
        self.phase = 0
        self.y_plus = None
        self.eps_hat = 0.0
        self.n_pairs = 0

    def act(self):
        return self.h + (self.delta_fd if self.phase == 0 else -self.delta_fd)

    def observe(self, h, tau_obs):
        if self.phase == 0:
            self.y_plus = tau_obs
            self.phase = 1
            return
        self.phase = 0
        slope = (self.y_plus - tau_obs) / (2 * self.delta_fd)
        self.n_pairs += 1
        w = 1.0 / self.n_pairs
        self.eps_hat = (1 - w) * self.eps_hat + w * max(-slope, 0.0)
        tau_mid = 0.5 * (self.y_plus + tau_obs)
        G = self.market.frozen_foc(self.h, tau_mid)
        delta_corr = -(self.h - self.market.psi) * self.eps_hat
        eta = self.eta or 1.0 / max(self.market.gamma(self.h), 0.5)
        self.h = float(np.clip(self.h + eta * (G + delta_corr),
                               self.market.h_lo, self.market.h_hi))


class ZOPerfOpt:
    """Zeroth-order performative optimization on noisy P&L observations."""

    def __init__(self, market, h0, delta_zo=0.2, eta=0.4, seed=0):
        self.market = market
        self.h = float(h0)
        self.delta_zo = delta_zo
        self.eta = eta
        self.phase = 0
        self.p_plus = None

    def act(self):
        return self.h + (self.delta_zo if self.phase == 0 else -self.delta_zo)

    def observe_pnl(self, h, pnl_obs):
        if self.phase == 0:
            self.p_plus = pnl_obs
            self.phase = 1
            return
        self.phase = 0
        grad = (self.p_plus - pnl_obs) / (2 * self.delta_zo)
        self.h = float(np.clip(self.h + self.eta * grad,
                               self.market.h_lo, self.market.h_hi))


class UCBGrid:
    """Performative-confidence-bounds explorer over a deployment grid."""

    def __init__(self, market, h_lo, h_hi, n_arms=25, lip=2.0, sigma=None,
                 seed=0):
        self.market = market
        self.grid = np.linspace(h_lo, h_hi, n_arms)
        self.lip = lip                      # Lipschitz bound on tau(.)
        self.sigma = sigma or market.sigma
        self.sum_y = np.zeros(n_arms)
        self.n = np.zeros(n_arms)
        self.t = 0
        self.h = float(self.grid[n_arms // 2])

    def _phi_ucb(self):
        """Optimistic performative value of every arm via propagated bounds."""
        ucb = np.empty(len(self.grid))
        for i, h in enumerate(self.grid):
            # tau upper/lower bound at arm i from ALL arms (Lipschitz +
            # sampling width) - performative feedback propagates knowledge
            lo, hi = -np.inf, np.inf
            for j in range(len(self.grid)):
                if self.n[j] == 0:
                    continue
                mean_j = self.sum_y[j] / self.n[j]
                width = self.sigma * np.sqrt(
                    2 * np.log(max(self.t, 2) ** 2) / self.n[j])
                gap = self.lip * abs(self.grid[j] - h)
                lo = max(lo, mean_j - width - gap)
                hi = min(hi, mean_j + width + gap)
            if not np.isfinite(hi):
                ucb[i] = np.inf
                continue
            # optimistic value: the loss is known given tau (performative
            # feedback); toxic flow earns h - psi per unit
            tau_opt = hi if h > self.market.psi else max(lo, 0.0)
            ucb[i] = self.market.J(h, max(tau_opt, 0.0))
        return ucb

    def act(self):
        self.t += 1
        i = int(np.argmax(self._phi_ucb()))
        self.h = float(self.grid[i])
        return self.h

    def observe(self, h, tau_obs):
        i = int(np.argmin(np.abs(self.grid - h)))
        self.sum_y[i] += tau_obs
        self.n[i] += 1
