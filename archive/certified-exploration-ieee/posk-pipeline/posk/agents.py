"""The agents: blind retraining, jittered PerfGD, and SafeD-PerfGD.

SafeD-PerfGD is the paper's architecture. Per deployment round it:
  1. EXPLORES on the D-optimal 3-point support of the structural family,
     re-centred at the operating point, inside the trust region (design.py);
  2. FITS the anchored family (C0, C1, c) to the window of (h, tau_obs)
     pairs (estimators.StructuralFit), with the identified-flag freeze;
  3. GATES the performative correction pessimistically: correct only when
     the anytime confidence width translates, through the perturbed-modulus
     lemma (L4), into a certified closed-loop margin - otherwise freeze the
     correction and keep exploring (the anti-echo freeze, derived);
  4. STEPS h <- h + eta * (G_hat + Delta_hat), trust-region clipped, with
     eta = 1 / gamma_PO_hat (certainty-equivalent Newton scaling).

The blind agent is the RRM cobweb (retrain-on-observed-flow best response);
the jitter agent is PerfGD with isotropic exploration and OLS slope - the
naive baseline every theorem prices.
"""

from __future__ import annotations

import numpy as np

from .design import ScalarScheduler
from .estimators import OLSSlope, StructuralFit


class BlindRRM:
    """h_{t+1} = BR(tau_obs(h_t)): the cobweb, blind to dD/dphi."""

    def __init__(self, market, h0):
        self.market = market
        self.h = float(h0)

    def act(self):
        return self.h

    def observe(self, h, tau_obs):
        self.h = self.market.best_response(tau_obs)


class JitterPerfGD:
    """PerfGD with isotropic jitter exploration and OLS slope estimation."""

    def __init__(self, market, h0, sigma_e=0.05, eta=None, window=200,
                 seed=0):
        self.market = market
        self.h = float(h0)
        self.sigma_e = sigma_e
        self.eta = eta
        self.ols = OLSSlope()
        self.window = window
        self.rng = np.random.default_rng(seed)

    def _correction(self, h, eps_hat):
        return -(h - self.market.psi) * eps_hat

    def act(self):
        return self.h + self.sigma_e * self.rng.standard_normal()

    def observe(self, h, tau_obs):
        self.ols.update(h, tau_obs)
        if self.ols.n < 8:
            return
        eps_hat = max(self.ols.eps_hat(), 0.0)
        G = self.market.frozen_foc(self.h, tau_obs)
        step = G + self._correction(self.h, eps_hat)
        eta = self.eta or 1.0 / max(self.market.gamma(self.h), 0.2)
        self.h = float(np.clip(self.h + eta * step,
                               self.market.h_lo, self.market.h_hi))


class SafeDPerfGD:
    """The architecture: shaped exploration + anchored fit + pessimism gate."""

    def __init__(self, market, h0, r=0.5, window=600, margin=0.2,
                 alpha=0.05, max_rel_step=0.35, refit_every=5, seed=0,
                 use_design=True, use_anchor=True, use_gate=True):
        self.market = market       # the dealer's OWN objective bookkeeping
        self.h = float(h0)         # operating point
        self.r = r                 # trust region
        self.window = window
        self.margin = margin
        self.alpha = alpha
        self.max_rel_step = max_rel_step
        self.refit_every = refit_every
        self.use_design = use_design    # ablation: 3-pt design vs iid jitter
        self.use_anchor = use_anchor    # ablation: structural fit vs OLS slope
        self.use_gate = use_gate        # ablation: pessimism gate vs always-on
        self.rng = np.random.default_rng(seed)
        self._since_fit = 0
        self.sched = ScalarScheduler(r)
        self.fitter = StructuralFit()
        self.ols = OLSSlope()
        self.buf = []              # (h, tau_obs) window
        self.params = None
        self.frozen_steps = 0
        self.corrected_steps = 0

    # -- components ---------------------------------------------------
    def _eps_ci(self):
        return self.ols.ci_width(self.market.sigma, self.alpha)

    def _modulus_certified(self, ci, c_hat):
        """L4 pessimism with the structural family's own Lipschitz constant:
        ||e|| + |h-psi| ||e'|| <= ci * (1 + c_hat (|h-psi| + r)) =: ci L_fam,
        and the Newton-scaled step makes the nominal slope ~0, so the
        certified condition is eta * ci * L_fam <= margin."""
        eta = 1.0 / max(self.market.gamma_po(self.h),
                        self.market.gamma(self.h), 0.5)
        # family-specific L4: the exponential family's pointwise error field
        # satisfies |e'(h)| <= c_hat |e(h)|, so the C^1 combination at the
        # operating point is bounded by ci (1 + c_hat |h - psi|).
        L_fam = 1.0 + c_hat * abs(self.h - self.market.psi)
        return eta * ci * L_fam <= self.margin

    def _correction(self, h, eps_hat):
        return -(h - self.market.psi) * eps_hat

    # -- interface ----------------------------------------------------
    def act(self):
        if not self.use_design:
            # matched design energy: the 3-point support realizes
            # E[u^2] = 2r^2/3 per step (measured 0.208 vs 0.207 predicted),
            # so the iid arm needs sd r sqrt(2/3) - the first version used
            # r/sqrt(3) and under-funded the ablation by 2x (pivot recorded)
            probe = self.h + self.r * np.sqrt(2.0 / 3.0) \
                * self.rng.standard_normal()
        else:
            C1 = self.params["C1"] if self.params else self.market.C1
            c = self.params["c"] if self.params else self.market.c
            probe = self.sched.next_probe(self.h, C1, c)
        lo = self.h - self.max_rel_step * max(self.h, 0.2)
        hi = self.h + self.max_rel_step * max(self.h, 0.2)
        return float(np.clip(probe, max(lo, self.market.h_lo),
                             min(hi, self.market.h_hi)))

    def observe(self, h, tau_obs):
        self.buf.append((h, tau_obs))
        self.buf = self.buf[-self.window:]
        self.ols.update(h, tau_obs)
        if len(self.buf) < 9:
            return
        self._since_fit += 1
        if self.params is None or self._since_fit >= self.refit_every:
            hs, ys = map(np.asarray, zip(*self.buf))
            self.params = self.fitter.fit(hs, ys)
            self._since_fit = 0
        if self.use_anchor:
            eps_hat = max(StructuralFit.eps_hat(self.params, self.h), 0.0)
        else:
            eps_hat = max(self.ols.eps_hat(), 0.0)
        ci = self._eps_ci()
        gate_ok = (self.params["identified"]
                   and self._modulus_certified(ci, self.params["c"]))
        if self.use_gate and not gate_ok:
            # the anti-echo freeze, derived: no CORRECTION, but the blind
            # step (provably stable at m < 1) keeps running under the fit
            self.frozen_steps += 1
            tau_here = self.params["C0"] + self.params["C1"] \
                * np.exp(-self.params["c"] * self.h)
            h_blind = self.market.best_response(tau_here)
            cap = self.max_rel_step * max(self.h, 0.2)
            self.h = float(np.clip(h_blind, self.h - cap, self.h + cap))
            return
        self.corrected_steps += 1
        tau_here = self.params["C0"] + self.params["C1"] \
            * np.exp(-self.params["c"] * self.h)
        G = self.market.frozen_foc(self.h, tau_here)
        step = G + self._correction(self.h, eps_hat)
        eta = 1.0 / max(self.market.gamma_po(self.h),
                        self.market.gamma(self.h), 0.5)
        h_new = self.h + eta * step
        cap = self.max_rel_step * max(self.h, 0.2)
        self.h = float(np.clip(h_new, self.h - cap, self.h + cap))
        self.h = float(np.clip(self.h, self.market.h_lo, self.market.h_hi))


def run_agent(agent, env, T):
    """The pipeline loop: deploy -> observe -> update. Returns the h path."""
    path = []
    for _ in range(T):
        h = agent.act()
        tau_obs = env.deploy(h)
        agent.observe(h, tau_obs)
        path.append(h)
    return np.asarray(path)
