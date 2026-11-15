"""Tangent-response updates and the certified agent (C-TRR).

The exact tangent-response step from an incumbent quote b maximizes the
surrogate

    S_b(h) = K(h) + (h - psi) * [tau(b) + tau'(b) (h - b)]

over h >= psi.  It is repeated retraining in which the responsive flow is
frozen along its tangent line instead of at its level.

C-TRR is the data-driven, certified form.  It keeps one incumbent and at
most one challenger, estimates the flow only at quotes it has deployed, and

  * adopts a challenger only when an anytime-valid direct comparison shows
    that its profit is higher (no shape assumption is used for adoption);
  * trials a quote only if every flow curve that is nonnegative,
    nonincreasing, convex and consistent with the confidence intervals gives
    a profit shortfall of at most the risk budget against the incumbent.
"""

from __future__ import annotations

import math

import numpy as np


# ------------------------------------------------------ exact (oracle) updates
def tangent_response(mk, b, tau_b, slope, lo=None, hi=None):
    """argmax_h K(h) + (h - psi)(tau_b + slope (h - b)) on [lo, hi].

    `slope` is the nonpositive slope of the linear flow model through
    (b, tau_b).  The surrogate has second derivative K''(h) + 2 slope < 0,
    so its derivative changes sign once.
    """
    lo = mk.psi if lo is None else lo
    hi = mk.h_hi if hi is None else hi

    def d(h):
        return mk.Kp(h) + tau_b + slope * (h - b) + (h - mk.psi) * slope

    if d(lo) <= 0:
        return lo
    if d(hi) >= 0:
        return hi
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if d(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def trr_step(mk, b, lo=None, hi=None):
    """Exact tangent-response step from quote b (true level and slope)."""
    return tangent_response(mk, b, float(mk.tau(b)), -float(mk.eps(b)), lo, hi)


def trr_rate(mk, h):
    """Derivative of the tangent-response map at a stationary quote h."""
    return 1.0 - mk.gamma_po(h) / (mk.gamma(h) + 2 * mk.eps(h))


# ---------------------------------------------------- shape-constrained fit
def nnls(Amat, b, tol=1e-11, maxit=None):
    """Lawson-Hanson nonnegative least squares (small dense problems)."""
    m, n = Amat.shape
    maxit = 6 * n if maxit is None else maxit
    x = np.zeros(n)
    P = np.zeros(n, dtype=bool)
    w = Amat.T @ (b - Amat @ x)
    it = 0
    while (~P).any() and np.max(np.where(~P, w, -np.inf)) > tol and it < maxit:
        it += 1
        j = int(np.argmax(np.where(~P, w, -np.inf)))
        P[j] = True
        for _ in range(3 * n + 3):
            s = np.zeros(n)
            s[P] = np.linalg.lstsq(Amat[:, P], b, rcond=None)[0]
            if not P.any() or s[P].min() > 0:
                break
            mask = P & (s <= 0)
            alpha = np.min(x[mask] / np.maximum(x[mask] - s[mask], 1e-300))
            x = x + alpha * (s - x)
            P &= x > tol
            x[~P] = 0.0
        x = s
        x[~P] = 0.0
        w = Amat.T @ (b - Amat @ x)
    return x


def convex_decreasing_fit(xs, ys, ws):
    """Weighted least-squares projection of (xs, ys) onto nonnegative,
    nonincreasing, convex sequences.  xs must be strictly increasing.

    Uses f(x) = a + sum_j beta_j (x_{j+1} - x)_+ with a, beta >= 0, which
    spans exactly the nonnegative nonincreasing convex piecewise-linear
    functions with knots at the data.
    """
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    ws = np.asarray(ws, float)
    m = len(xs)
    if m == 1:
        return np.maximum(ys, 0.0)
    B = np.ones((m, m))
    for j in range(1, m):
        B[:, j] = np.maximum(xs[j] - xs, 0.0)
    sw = np.sqrt(ws)
    coef = nnls(B * sw[:, None], ys * sw)
    return B @ coef


# ------------------------------------------------------------- certificates
def lower_envelope(H, xs, L, U):
    """Pointwise lower bound on tau at the points H, valid for every
    nonnegative, nonincreasing, convex tau with tau(xs[p]) in [L[p], U[p]].
    xs must be strictly increasing."""
    tl = np.zeros(H.shape)
    m = len(xs)
    for p in range(m):                      # monotonicity
        tl = np.where(H <= xs[p], np.maximum(tl, L[p]), tl)
    for p in range(m):                      # chords extended beyond their endpoints
        for q in range(p + 1, m):
            D = xs[q] - xs[p]
            sl = max(L[p] - U[q], 0.0) / D
            if sl > 0:
                tl = np.where(H <= xs[p], np.maximum(tl, L[p] + sl * (xs[p] - H)), tl)
            sr = min(L[q] - U[p], 0.0) / D
            tl = np.where(H >= xs[q], np.maximum(tl, L[q] + sr * (H - xs[q])), tl)
    return tl


def certified_gain(mk, H, xs, L, U, ib):
    """Lower bound on Phi(h) - Phi(b), b = xs[ib], at the points H (all >= psi),
    valid for every flow curve in the shape class with tau(xs[p]) in
    [L[p], U[p]] for all p."""
    H = np.atleast_1d(np.asarray(H, float))
    KH = mk.K(H)
    psi = mk.psi
    xb, Lb, Ub = xs[ib], L[ib], U[ib]
    Kb = float(mk.K(xb))
    tl = lower_envelope(H, xs, L, U)
    g = KH - Kb + (H - psi) * tl - (xb - psi) * Ub
    # tighter quotes: tau(h) >= tau(b), so only the margin difference b - h is exposed
    g = np.where(H <= xb, np.maximum(g, KH - Kb - (xb - H) * Ub), g)
    for p in range(len(xs)):
        if p == ib:
            continue
        D = abs(xs[p] - xb)
        if xs[p] > xb:      # chord (b, a) extended to the left, bounded jointly in tau(b)
            cb = (H - psi) * (xs[p] - H) / D - (xb - psi)
            ca = -(H - psi) * (xb - H) / D
            jb = KH - Kb + np.where(cb >= 0, cb * Lb, cb * Ub) + ca * U[p]
            g = np.where(H <= xb, np.maximum(g, jb), g)
        else:               # chord (a, b) extended to the right, bounded jointly in tau(b)
            cb = (H - psi) * (H - xs[p]) / D - (xb - psi)
            ca = -(H - psi) * (H - xb) / D
            jb = KH - Kb + np.where(cb >= 0, cb * Lb, cb * Ub) + ca * U[p]
            g = np.where(H >= xb, np.maximum(g, jb), g)
    return g


class Anchor:
    """A deployed quote: location, running sums, and an anytime confidence
    interval [L, U] for the mean responsive flow there."""

    __slots__ = ("x", "n", "s", "L", "U", "j", "i", "next_cp", "Kx", "n_prior", "m_prior")

    def __init__(self, x, j, n0, Kx):
        self.x, self.j, self.Kx = float(x), j, float(Kx)
        self.n, self.s = 0, 0.0
        self.L, self.U = -np.inf, np.inf
        self.i, self.next_cp = 0, n0
        self.n_prior, self.m_prior = 0.0, 0.0

    @property
    def cnt(self):
        return self.n + self.n_prior

    @property
    def mean(self):
        c = self.cnt
        return (self.s + self.n_prior * self.m_prior) / c if c else np.nan

    @property
    def ready(self):
        return np.isfinite(self.L) and np.isfinite(self.U)


# -------------------------------------------------------------------- C-TRR
class CTRR:
    """Certified tangent-response retraining.

    Parameters
    ----------
    mk        : market; the agent reads only K, K' and psi (and sigma as a
                noise bound unless sigma_bar is given)
    h0        : starting quote, assumed performatively stable
    budget    : per-period risk budget ell in profit units, or None (no trial
                filter; exploratory steps then have length d0)
    d0        : cap on the length of an exploratory step; None uses the largest
                step the budget allows at the stable start (0.5 with no budget)
    warm      : use tau(h0) = -K'(h0), which holds at a stable quote
    tol0      : half-width of the prior interval for tau(h0) when warm
    alpha     : total error probability of all confidence intervals
    zfix      : if set, fixed-z intervals with no union bound (uncertified ablation)
    fit       : "shape" (convex nonincreasing least squares) or "raw" anchor means
    """

    def __init__(self, mk, h0, budget=None, d0=None, warm=True, tol0=0.0, alpha=0.05,
                 rho=1.5, n0=16, dmin=0.02, sigma_bar=None, grid=801, jmax=40,
                 zfix=None, fit="shape", repropose=1.5, signif=1.0,
                 optimistic=True, expand=True):
        self.mk, self.alpha, self.rho, self.n0 = mk, alpha, rho, n0
        self.dmin, self.jmax, self.zfix, self.fit = dmin, jmax, zfix, fit
        self.repropose, self.signif = repropose, signif
        self.optimistic, self.expand = optimistic, expand
        self.sig = mk.sigma if sigma_bar is None else sigma_bar
        self.psi = mk.psi
        self.lo, self.hi = mk.psi, float(h0)     # wider than a stable quote is never better
        self.H = np.linspace(self.lo, self.hi, grid)
        self.KH = mk.K(self.H)
        self.ell = budget
        # a priori facts at a stable quote: tau(h0) = -K'(h0)
        self.tau0 = -float(mk.Kp(h0))
        self.phi0 = float(mk.K(h0)) + (h0 - mk.psi) * self.tau0
        # worst-case loss of a tighter pilot: K(h0) - K(h) + (h0 - h) tau(h0)  (zero at h0)
        loss = float(mk.K(h0)) - self.KH + (h0 - self.H) * self.tau0
        if budget is not None:
            # loss is convex in h and minimal at h0, so the safe quotes form an interval ending at h0
            dmax = h0 - float(self.H[loss <= budget].min())
            d0 = dmax if d0 is None else min(d0, dmax)
        elif d0 is None:
            d0 = 0.5
        self.d0 = d0
        a0 = Anchor(h0, 1, n0, mk.K(h0))
        if warm:
            a0.L, a0.U = self.tau0 - tol0, self.tau0 + tol0
            a0.m_prior = self.tau0
            a0.n_prior = 1e9 if tol0 == 0 else (self.sig / tol0) ** 2
        self.anchors = [a0]
        self.inc, self.ch = 0, None
        self.dominated = set()
        self.moves, self.rejects, self.proposals = [], [], []
        self.t, self.cur = 0, None
        self.kinds, self.inc_path = [], []
        self._add_challenger(h0 - d0, "pilot")

    # ------------------------------------------------------------ bookkeeping
    def _add_challenger(self, x, kind):
        x = float(np.clip(x, self.lo, self.hi))
        self.anchors.append(Anchor(x, len(self.anchors) + 1, self.n0, self.mk.K(x)))
        self.ch = len(self.anchors) - 1
        self.proposals.append((self.t, self.anchors[self.inc].x, x, kind))

    def act(self):
        self.t += 1
        if self.ch is not None and self.anchors[self.ch].cnt <= self.anchors[self.inc].cnt:
            self.cur = self.ch
            self.kinds.append(1)
        else:
            self.cur = self.inc
            self.kinds.append(0)
        self.inc_path.append(self.anchors[self.inc].x)
        return self.anchors[self.cur].x

    def observe(self, h, y):
        a = self.anchors[self.cur]
        a.n += 1
        a.s += y
        if a.n >= a.next_cp:
            a.i += 1
            if self.zfix is None:
                dl = self.alpha / (a.j * (a.j + 1) * a.i * (a.i + 1))
                r = self.sig * math.sqrt(2 * math.log(2 / dl) / a.n)
            else:
                r = self.zfix * self.sig / math.sqrt(a.n)
            m = a.s / a.n
            L, U = max(a.L, m - r), min(a.U, m + r)
            if L <= U:              # an empty intersection can only occur off the confidence event
                a.L, a.U = L, U
            a.next_cp = max(a.n + 1, int(math.ceil(a.next_cp * self.rho)))
            self._evaluate()

    def _gain(self, xs, L, U, ib, H=None):
        return certified_gain(self.mk, self.H if H is None else H, xs, L, U, ib)

    # --------------------------------------------------------------- decisions
    def _evaluate(self):
        psi = self.psi
        b = self.anchors[self.inc]
        # 1. adoption by direct comparison (valid without any shape assumption)
        if b.ready:
            best, gbest = None, 0.0
            for k, a in enumerate(self.anchors):
                if k == self.inc or not a.ready or k in self.dominated:
                    continue
                ga = a.Kx + (a.x - psi) * a.L - b.Kx - (b.x - psi) * b.U
                if ga > gbest:
                    best, gbest = k, ga
            if best is not None:
                self.moves.append((self.t, b.x, self.anchors[best].x, gbest))
                self.dominated.add(self.inc)
                self.inc, self.ch = best, None
                b = self.anchors[self.inc]
        # 2. certified rejection of the challenger
        if self.ch is not None:
            c = self.anchors[self.ch]
            if c.ready and b.ready and c.Kx + (c.x - psi) * c.U < b.Kx + (b.x - psi) * b.L:
                self.rejects.append((self.t, b.x, c.x))
                self.dominated.add(self.ch)
                self.ch = None
        if not b.ready or len(self.anchors) >= self.jmax:
            return
        idx = [k for k, a in enumerate(self.anchors) if a.ready]
        idx.sort(key=lambda k: self.anchors[k].x)
        if len(idx) < 2:
            return
        xs = np.array([self.anchors[k].x for k in idx])
        if np.min(np.diff(xs)) < 1e-9:
            return
        ib = idx.index(self.inc)
        L = np.array([self.anchors[k].L for k in idx])
        U = np.array([self.anchors[k].U for k in idx])
        # 3. safe trial set
        if self.ell is None:
            safe = np.ones(self.H.shape, dtype=bool)
        else:
            safe = self._gain(xs, L, U, ib) >= -self.ell
        allx = np.array([a.x for a in self.anchors])
        far = np.min(np.abs(self.H[:, None] - allx[None, :]), axis=1) >= self.dmin
        cand = safe & far
        # 4. plug-in flow values at the anchors
        ys = np.array([self.anchors[k].mean for k in idx])
        ns = np.array([self.anchors[k].cnt for k in idx], float)
        f = convex_decreasing_fit(xs, ys, ns) if self.fit == "shape" else np.maximum(ys, 0.0)
        se = (b.x - psi) * self.sig / math.sqrt(b.cnt)
        # 4a. maximin proposal: the quote with the best guaranteed gain under the fitted flows
        if cand.any():
            glow = self._gain(xs, f, f, ib)
            k = int(np.argmax(np.where(cand, glow, -np.inf)))
            if glow[k] > 0:
                p = float(self.H[k])
                if self.ch is None:
                    self._add_challenger(p, "maximin")
                else:
                    c = self.anchors[self.ch]
                    if (p - b.x) * (c.x - b.x) > 0 and abs(p - b.x) >= self.repropose * abs(c.x - b.x):
                        self._add_challenger(p, "maximin")
                return
        if self.ch is not None:
            return
        # 4b. an existing anchor that the fit prefers to the incumbent
        fb = b.Kx + (b.x - psi) * f[ib]
        best, gbest = None, self.signif * se
        for q, k in enumerate(idx):
            if k == self.inc or k in self.dominated:
                continue
            a = self.anchors[k]
            ga = a.Kx + (a.x - psi) * f[q] - fb
            if ga > gbest and (self.ell is None
                               or self._gain(xs, L, U, ib, H=a.x)[0] >= -self.ell):
                best, gbest = k, ga
        if best is not None:
            self.ch = best
            self.proposals.append((self.t, b.x, self.anchors[best].x, "retrial"))
            return
        # 4c. optimistic refinement between anchors, where the chord is an upper bound on the flow
        if self.optimistic and cand.any():
            m = cand & (self.H >= xs[0]) & (self.H <= xs[-1])
            if m.any():
                gup = self.KH + (self.H - psi) * np.interp(self.H, xs, f) - fb
                k = int(np.argmax(np.where(m, gup, -np.inf)))
                if gup[k] > self.signif * se:
                    self._add_challenger(float(self.H[k]), "optimistic")
                    return
        # 4d. safe expansion: left of the tightest anchor the flow has no upper bound,
        #     so trial the tightest safe quote within one step
        if self.expand and ib == 0 and cand.any():
            m = cand & (self.H < b.x) & (self.H >= b.x - self.d0 - 1e-12)
            if m.any():
                self._add_challenger(float(self.H[int(np.argmax(m))]), "expand")
