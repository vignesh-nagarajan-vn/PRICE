"""Performative market environments.

StructuralEnv realizes the theory's world exactly (the exponential response
family with Gaussian observation noise). SaturatingEnv adds the REFLEX-style
tanh cap on toxic flow - the nonlinearity the theory's local scope excludes,
used to *measure* the exchange-rate drift rather than assume it away.

The environment exposes only what a real desk would see: deploy a spread,
observe one noisy flow realization and one noisy profit realization. Oracle
quantities (true Phi, true tau, h*, m) are available through `.oracle` for
measurement and verification, never for the agents.
"""

from __future__ import annotations

import numpy as np

from .theory import Market


class StructuralEnv:
    def __init__(self, market: Market, seed: int = 0):
        self.m = market
        self.rng = np.random.default_rng(seed)
        self.t = 0
        self.history = []  # (h, tau_obs)

    # -- what the theory calls the environment's true map (oracle) ----
    @property
    def oracle(self) -> Market:
        return self.m

    def true_tau(self, h):
        return self.m.tau(h)

    def deploy(self, h):
        """Deploy a spread; return one noisy observation of the induced flow."""
        h = float(np.clip(h, self.m.h_lo, self.m.h_hi))
        tau_obs = self.true_tau(h) + self.m.sigma * self.rng.standard_normal()
        self.t += 1
        self.history.append((h, tau_obs))
        return tau_obs

    def deploy_pnl(self, h, pnl_noise=0.3):
        """Deploy and observe a noisy profit realization (for zeroth-order
        baselines): Phi(h) + noise. Counts as a deployment."""
        h = float(np.clip(h, self.m.h_lo, self.m.h_hi))
        self.t += 1
        return self.m.Phi(h) + pnl_noise * self.rng.standard_normal()

    def incremental_cost(self, h, anchor):
        """Oracle measurement of Phi(anchor) - Phi(h) (verification only)."""
        return self.m.Phi(anchor) - self.m.Phi(float(h))


class SaturatingEnv(StructuralEnv):
    """Toxic flow saturates: tau_cap = cap * tanh(tau / cap).

    Engages at tight spreads; outside the local-quadratic scope of the
    theory (Assumption A1), so measured deviations here are the *drift
    study*, not falsifications.
    """

    def __init__(self, market: Market, cap: float = 1.2, seed: int = 0):
        super().__init__(market, seed)
        self.cap = cap

    def true_tau(self, h):
        raw = self.m.tau(h)
        return self.cap * np.tanh(raw / self.cap)
