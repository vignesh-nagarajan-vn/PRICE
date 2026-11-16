"""d-dimensional (multi-bond) market and the vector SafeD agent.

Separable structural market: d bonds, each with its own (A_a, k_a, C1_a)
spanning a curvature decade, so Gamma_PO is diagonal with genuine
dispersion (P9.3). The item-8 claim tested here: the Gamma_PO^{-1/2}
exploration SHAPE (T5a) helps a *running agent*, not just the static
design testbed - shaped vs isotropic exploration at matched realized
budget, measured on the A-risk of the response estimate and the distance
to the vector performative optimum.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .theory import Market


@dataclass(frozen=True)
class MultiBondMarket:
    markets: tuple    # per-bond scalar Markets (separable)

    @staticmethod
    def make(d=4, seed=0, sigma=0.25, kind="dispersed"):
        """kind="dispersed": genuine curvature decade (F ~ 1.45), interior
        optima; kind="flat": near-isotropic control (F ~ 1.1) where shaping
        should be null."""
        if kind == "dispersed":
            specs = [dict(A=1.0, k=1.6, C1=0.35, c=1.3, w=1.6),
                     dict(A=1.0, k=1.4, C1=0.6, c=1.5, w=0.45),
                     dict(A=1.0, k=1.3, C1=0.9, c=1.6, w=0.14),
                     dict(A=1.0, k=1.2, C1=1.3, c=1.8, w=0.05)][:d]
        else:
            specs = [dict(A=1.0, k=1.3 + 0.1 * a, C1=0.8, c=1.5,
                          w=0.25) for a in range(d)]
        return MultiBondMarket(markets=tuple(
            Market(sigma=sigma, h_hi=8.0, **sp) for sp in specs))

    @property
    def d(self):
        return len(self.markets)

    def h_sp(self):
        return np.array([m.h_sp() for m in self.markets])

    def h_po(self):
        return np.array([m.h_po() for m in self.markets])

    def gamma_po_diag(self, h):
        return np.array([m.gamma_po(h[a]) for a, m in enumerate(self.markets)])

    def eps_vec(self, h):
        return np.array([m.eps(h[a]) for a, m in enumerate(self.markets)])

    def Phi(self, h):
        return sum(m.Phi(h[a]) for a, m in enumerate(self.markets))


class MultiBondEnv:
    def __init__(self, mb: MultiBondMarket, seed=0):
        self.mb = mb
        self.rng = np.random.default_rng(seed)

    def deploy(self, h):
        return np.array([
            m.tau(h[a]) + m.sigma * self.rng.standard_normal()
            for a, m in enumerate(self.mb.markets)])


class VectorSafeD:
    """Vector SafeD: per-bond OLS response slopes + corrections, with the
    exploration covariance either SHAPED (proportional to Gamma_PO^{-1/2})
    or isotropic, both scaled to the same Gamma_PO-budget rate.

    Honesty note: the SHAPE and the Newton step scale use the model's
    curvature bookkeeping (the dealer's own objective per D0's convention;
    gamma_PO's eps-ingredient makes this partially oracle) - deliberately,
    to isolate the effect under test: does the T5a shape help a *running*
    agent at matched budget? Estimating the shape online is a small further
    delta and adds only noise to both arms symmetrically."""

    def __init__(self, mb, h0, budget_rate=0.08, shaped=True, seed=0,
                 warmup=300, window=600, ridge=2.0):
        self.mb = mb
        self.h = np.asarray(h0, float)
        self.budget_rate = budget_rate   # (1/2) E[u' Gamma_PO u] per step
        self.shaped = shaped
        self.rng = np.random.default_rng(seed)
        self.warmup = warmup             # pure exploration before correcting
        self.window = window             # windowed OLS (drift containment)
        self.ridge = ridge               # eps_hat shrinkage toward 0
        self.buf = []                    # (h_vec, y_vec) window
        self.n = 0

    def _explore_cov_diag(self, gpo_diag):
        if self.shaped:
            raw = gpo_diag ** -0.5                     # T5a shape
        else:
            raw = np.ones(self.mb.d)                   # isotropic
        scale = 2 * self.budget_rate / float(gpo_diag @ raw)
        return scale * raw                             # diag of M

    def act(self):
        gpo = np.maximum(self.mb.gamma_po_diag(self.h), 0.2)
        var = self._explore_cov_diag(gpo)
        u = np.sqrt(var) * self.rng.standard_normal(self.mb.d)
        self._last_u = u
        return self.h + u

    def _fit(self):
        """Windowed per-bond OLS with ridge shrinkage of the slope."""
        H = np.asarray([b[0] for b in self.buf[-self.window:]])
        Y = np.asarray([b[1] for b in self.buf[-self.window:]])
        hbar, ybar = H.mean(axis=0), Y.mean(axis=0)
        dc = H - hbar
        sxx = (dc ** 2).sum(axis=0)
        sxy = (dc * (Y - ybar)).sum(axis=0)
        eps_hat = np.maximum(-sxy / (sxx + self.ridge), 0.0)
        return eps_hat, hbar, ybar

    def observe(self, h_dep, tau_obs):
        self.n += 1
        self.buf.append((np.asarray(h_dep, float).copy(),
                         np.asarray(tau_obs, float).copy()))
        if self.n < self.warmup:
            return
        eps_hat, hbar, ybar = self._fit()
        for a, m in enumerate(self.mb.markets):
            # smoothed frozen level from the window fit at the current h
            tau_here = ybar[a] - eps_hat[a] * (self.h[a] - hbar[a])
            G = m.frozen_foc(self.h[a], tau_here)
            step = G - (self.h[a] - m.psi) * eps_hat[a]
            eta = 1.0 / max(m.gamma_po(self.h[a]), m.gamma(self.h[a]), 1.0)
            cap = 0.10 * max(self.h[a], 0.2)
            self.h[a] = float(np.clip(self.h[a] + np.clip(eta * step, -cap, cap),
                                      m.h_lo, m.h_hi))

    def eps_risk(self, true_eps):
        eps_hat, _, _ = self._fit()
        return float(((eps_hat - true_eps) ** 2).sum())

    def clean_risk(self, env, T2=1200, n_rep=10):
        """Steady-state estimation risk: hold the operating point fixed and
        probe under the agent's own shape - the drift-free measurement of
        the design-allocation effect (the transit phase is bias-dominated,
        which is reported separately). Averaged over n_rep independent
        windows (a single window is one chi^2 draw dominated by one bond -
        pure measurement noise, diagnosed in the first run)."""
        gpo = np.maximum(self.mb.gamma_po_diag(self.h), 0.2)
        var = self._explore_cov_diag(gpo)
        true_eps = self.mb.eps_vec(self.h)
        risks = []
        for _ in range(n_rep):
            H = self.h + np.sqrt(var) * self.rng.standard_normal(
                (T2, self.mb.d))
            Y = np.stack([m.tau(H[:, a]) for a, m in
                          enumerate(self.mb.markets)], axis=1)                 + np.array([m.sigma for m in self.mb.markets])                 * self.rng.standard_normal((T2, self.mb.d))
            hbar, ybar = H.mean(axis=0), Y.mean(axis=0)
            dc = H - hbar
            sxx = (dc ** 2).sum(axis=0)
            sxy = (dc * (Y - ybar)).sum(axis=0)
            eps_hat = np.maximum(-sxy / np.maximum(sxx, 1e-9), 0.0)
            risks.append(((eps_hat - true_eps) ** 2).sum())
        return float(np.mean(risks))
