"""Baselines.  All of them receive the same information as C-TRR: the known
part K of profit, the markout cost psi, the noise scale, the search interval
[psi, h0] and (where they can use it) the flow level at the starting quote."""

from __future__ import annotations

import numpy as np

from .agent import tangent_response


class UCBGrid:
    """Lipschitz-propagated UCB over a quote grid.

    Each sampled arm gives a confidence interval for the flow; the interval is
    propagated to the other arms with the Lipschitz constant `lip`.

    conservative=a turns on the conservative-bandit rule of Wu et al. (2016):
    the optimistic arm is played only if the pessimistic cumulative profit
    stays above (1 - a) times the status-quo profit; otherwise the status-quo
    arm is played.
    """

    def __init__(self, mk, h_lo, h_hi, n_arms=25, lip=6.0, sigma=None, start=None,
                 conservative=None, phi0=None, tau_start=None):
        self.mk = mk
        self.grid = np.linspace(h_lo, h_hi, n_arms)
        self.gap = lip * np.abs(self.grid[:, None] - self.grid[None, :])
        self.Kg = mk.K(self.grid)
        self.marg = self.grid - mk.psi
        self.sigma = mk.sigma if sigma is None else sigma
        self.sum_y = np.zeros(n_arms)
        self.n = np.zeros(n_arms)
        self.t = 0
        self.i0 = n_arms // 2 if start is None else int(np.argmin(np.abs(self.grid - start)))
        self.conservative, self.phi0 = conservative, phi0
        self.cur = self.i0
        self.tau_start = tau_start          # known mean flow at the starting arm, if any
        if tau_start is not None:           # the starting arm must sit on the grid
            assert abs(self.grid[self.i0] - start) < 1e-9

    def _bounds(self):
        seen = self.n > 0
        mean = np.zeros(len(self.grid))
        width = np.zeros(len(self.grid))
        mean[seen] = self.sum_y[seen] / self.n[seen]
        width[seen] = self.sigma * np.sqrt(2 * np.log(max(self.t, 2) ** 2) / self.n[seen])
        if self.tau_start is not None:
            seen = seen.copy()
            seen[self.i0] = True
            mean[self.i0], width[self.i0] = self.tau_start, 0.0
        lo = np.max(mean[None, seen] - width[None, seen] - self.gap[:, seen], axis=1)
        hi = np.min(mean[None, seen] + width[None, seen] + self.gap[:, seen], axis=1)
        return np.maximum(lo, 0.0), np.maximum(hi, 0.0)

    def act(self):
        self.t += 1
        if not (self.n > 0).any() and self.tau_start is None:
            i = self.i0
        else:
            lo, hi = self._bounds()
            ucb = self.Kg + np.where(self.marg > 0, self.marg * hi, self.marg * lo)
            i = int(np.argmax(ucb))
            if self.conservative is not None and i != self.i0:
                lcb = self.Kg + np.where(self.marg > 0, self.marg * lo, self.marg * hi)
                other = np.ones(len(self.grid), dtype=bool)
                other[self.i0] = False
                credit = float(np.sum(self.n[other] * lcb[other])) + self.n[self.i0] * self.phi0 + lcb[i]
                if credit < (1 - self.conservative) * self.t * self.phi0:
                    i = self.i0
        self.cur = i
        return float(self.grid[i])

    def observe(self, h, y):
        self.sum_y[self.cur] += y
        self.n[self.cur] += 1


class StagePerfGD:
    """Performative gradient ascent with finite-difference flow slopes.

    At iterate h, deploy h + delta and h - delta alternately for n pairs,
    estimate tau(h) and tau'(h) from the stage, and step by
    eta * (K'(h) + tau_hat + (h - psi) slope_hat).  No certificate.
    """

    def __init__(self, mk, h0, delta=0.1, n_pairs=100, eta=0.5, lo=None, hi=None):
        self.mk, self.h = mk, float(h0)
        self.delta, self.n_pairs, self.eta = delta, n_pairs, eta
        self.lo = mk.psi if lo is None else lo
        self.hi = mk.h_hi if hi is None else hi
        self.phase, self.sp, self.sm, self.k = 0, 0.0, 0.0, 0

    def act(self):
        return float(np.clip(self.h + (self.delta if self.phase == 0 else -self.delta), self.lo, self.hi))

    def observe(self, h, y):
        if self.phase == 0:
            self.sp += y
            self.phase = 1
            return
        self.sm += y
        self.phase = 0
        self.k += 1
        if self.k >= self.n_pairs:
            yp, ym = self.sp / self.k, self.sm / self.k
            slope = min((yp - ym) / (2 * self.delta), 0.0)
            grad = self.mk.Kp(self.h) + 0.5 * (yp + ym) + (self.h - self.mk.psi) * slope
            self.h = float(np.clip(self.h + self.eta * grad, self.lo + self.delta, self.hi - self.delta))
            self.sp = self.sm = 0.0
            self.k = 0


class StageTangentResponse:
    """Uncertified tangent-response iteration with two-point slope estimates,
    on the schedule of Besbes and Zeevi (2015).

    Stage i deploys the iterate b and the perturbed quote b - delta_i for
    n_i periods each, with n_i = n0 * nu**i and delta_i = rho * n_i**(-1/4),
    fits the line through the two sample means, and moves to the maximizer of
    the resulting linear-flow profit model.
    """

    def __init__(self, mk, h0, n0=25, nu=2.0, rho=1.0, lo=None, hi=None):
        self.mk, self.b = mk, float(h0)
        self.n0, self.nu, self.rho = n0, nu, rho
        self.lo = mk.psi if lo is None else lo
        self.hi = mk.h_hi if hi is None else hi
        self.stage = 0
        self._start()

    def _start(self):
        self.n = int(round(self.n0 * self.nu ** self.stage))
        self.delta = self.rho * self.n ** -0.25
        self.side = -1.0 if self.b - self.delta >= self.lo else 1.0
        self.sb = self.sp = 0.0
        self.k = 0

    def act(self):
        if self.k < self.n:
            return self.b
        return float(np.clip(self.b + self.side * self.delta, self.lo, self.mk.h_hi))

    def observe(self, h, y):
        if self.k < self.n:
            self.sb += y
        else:
            self.sp += y
        self.k += 1
        if self.k >= 2 * self.n:
            tb, tp = self.sb / self.n, self.sp / self.n
            slope = min((tp - tb) / (self.side * self.delta), 0.0)
            self.b = tangent_response(self.mk, self.b, tb, slope, self.lo, self.hi)
            self.stage += 1
            self._start()


class BlindRetraining:
    """Repeated retraining on a rolling window: h <- argmax_h J(h; mean flow)."""

    def __init__(self, mk, h0, window=50):
        self.mk, self.h, self.window = mk, float(h0), window
        self.buf = []

    def act(self):
        return self.h

    def observe(self, h, y):
        self.buf.append(y)
        if len(self.buf) >= self.window:
            self.h = float(self.mk.best_response(float(np.mean(self.buf))))
            self.buf = []
