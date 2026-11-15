"""Closed-form theory for the structural performative market (numpy only).

Mirrors the derivation folder's register (THEOREMS.md): every function here
is a closed form that the pipeline's *measured* results are verified
against. Market model (the simplified structural family; REFLEX 1.1 with
P = rho = gbar = 1 folded into the constants):

    benign flow:   U(h)   = A exp(-k h)
    toxic flow:    tau(h) = C0 + C1 exp(-c h)
    objective:     J(h;T) = h U(h) + h T - psi T - w (h - href)^2
    performative:  Phi(h) = J(h; tau(h))
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class Market:
    A: float = 1.0      # benign arrival scale
    k: float = 1.5      # benign demand elasticity
    C0: float = 0.6     # toxic base level
    C1: float = 0.9     # toxic slope scale  (the feedback lever)
    c: float = 1.5      # toxic spread decay (the curvature parameter of T6)
    psi: float = 0.4    # adverse severity per unit toxic flow
    w: float = 0.25     # quoting-cost convexity
    href: float = 1.0   # quoting-cost anchor
    sigma: float = 0.25  # response-noise sd (sigma_tau)
    h_lo: float = 0.05
    h_hi: float = 4.0

    # ---- primitives -------------------------------------------------
    def U(self, h):
        return self.A * np.exp(-self.k * h)

    def tau(self, h):
        return self.C0 + self.C1 * np.exp(-self.c * h)

    def eps(self, h):
        """Response slope |d tau/dh| = c C1 e^{-ch}."""
        return self.c * self.C1 * np.exp(-self.c * h)

    def tau3(self, h):
        """tau'''(h) = -c^3 C1 e^{-ch} (T7's bias constant)."""
        return -self.c ** 3 * self.C1 * np.exp(-self.c * h)

    def J(self, h, T):
        return h * self.U(h) + h * T - self.psi * T - self.w * (h - self.href) ** 2

    def Phi(self, h):
        return self.J(h, self.tau(h))

    # ---- REFLEX-1.1/1.2 closed forms --------------------------------
    def gamma(self, h):
        """Strong concavity of J in h at frozen T: A k e^{-kh}(2-kh) + 2w."""
        return self.A * self.k * np.exp(-self.k * h) * (2 - self.k * h) + 2 * self.w

    def gamma_po(self, h):
        """-Phi''(h) = gamma + eps (2 + c psi - c h)."""
        return self.gamma(h) + self.eps(h) * (2 + self.c * self.psi - self.c * h)

    def frozen_foc(self, h, T):
        """d J/d h at frozen toxic level T."""
        return self.A * np.exp(-self.k * h) * (1 - self.k * h) + T \
            - 2 * self.w * (h - self.href)

    def best_response(self, T):
        """argmax_h J(h; T) by bisection on the FOC (decreasing in h)."""
        lo, hi = self.h_lo, self.h_hi
        if self.frozen_foc(hi, T) > 0:
            return hi
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if self.frozen_foc(mid, T) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def h_sp(self):
        """Stable point: h = BR(tau(h)) by damped fixed-point iteration."""
        h = self.href
        for _ in range(400):
            h = 0.5 * h + 0.5 * self.best_response(self.tau(h))
        return h

    def h_po(self):
        """Performative optimum: argmax Phi on the grid + golden refine."""
        hs = np.linspace(self.h_lo, self.h_hi, 4001)
        h0 = hs[np.argmax(self.Phi(hs))]
        lo, hi = max(self.h_lo, h0 - 2e-3), min(self.h_hi, h0 + 2e-3)
        for _ in range(80):
            m1, m2 = lo + 0.382 * (hi - lo), lo + 0.618 * (hi - lo)
            if self.Phi(m1) < self.Phi(m2):
                lo = m1
            else:
                hi = m2
        return 0.5 * (lo + hi)

    def modulus(self, h=None):
        """m = eps * beta / gamma with beta = 1 at the stable point."""
        h = self.h_sp() if h is None else h
        return self.eps(h) / self.gamma(h)

    # ---- register closed forms consumed by the experiments ----------
    def exchange_rate(self, h=None):
        """T2: (1/2) gamma_PO sigma^2 at the operating point."""
        h = self.h_sp() if h is None else h
        return 0.5 * self.gamma_po(h) * self.sigma ** 2

    def saturation_cap(self, d0, h=None):
        """T1 scalar: d0^2 / (1 - m^2)."""
        m = self.modulus(h)
        return d0 ** 2 / (1 - m ** 2)

    def crossover_threshold(self, B, T, h=None):
        """T7 leading order: |tau'''| B / (3 gamma_PO T)."""
        h = self.h_sp() if h is None else h
        return abs(self.tau3(h)) * B / (3 * self.gamma_po(h) * T)

    def mse_np(self, B, T, h=None):
        """T7 full two-term nonparametric MSE at the constrained optimum."""
        h = self.h_sp() if h is None else h
        g = self.gamma_po(h)
        return g * self.sigma ** 2 / (2 * B) \
            + (self.tau3(h) / 6) ** 2 * (2 * B / (g * T)) ** 2

    def feedback_for_modulus(self, target_m):
        """Return a Market with C1 scaled so the stable-point modulus = target."""
        lo, hi = 1e-3, 60.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            mkt = replace(self, C1=mid)
            if mkt.modulus() < target_m:
                lo = mid
            else:
                hi = mid
        return replace(self, C1=0.5 * (lo + hi))


def dispersion_factor(Gamma):
    """C5.1: F = d tr(Gamma) / (tr Gamma^{1/2})^2 for SPD Gamma."""
    w = np.linalg.eigvalsh(Gamma)
    return len(w) * w.sum() / (np.sqrt(w).sum()) ** 2


def a_optimal_design(Gamma, B):
    """T5a: M* = (B / tr Gamma^{1/2}) Gamma^{-1/2}."""
    w, V = np.linalg.eigh(Gamma)
    Ghalf_inv = V @ np.diag(w ** -0.5) @ V.T
    return (B / np.sqrt(w).sum()) * Ghalf_inv
