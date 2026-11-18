"""The certified rate search.

The lender quotes rates on a lattice b0 + g * step.  It keeps one incumbent rate and at most one pilot rate;
while a pilot runs, quotes alternate between the two.  Each lattice point has an anytime-valid confidence
interval for its take-up (bounds.py; relative-entropy intervals by default, Hoeffding intervals as an option).

  * Adoption: a rate replaces the incumbent only when the direct comparison certifies a higher profit,
    (h - psi) L_h > (b - psi) U_b.  No shape assumption is used.
  * Rejection: a pilot stops when it is certified worse, (h - psi) U_h < (b - psi) L_b, or after n_cap of its
    own quotes without a decision ("unresolved").
  * Safety: a pilot rate is allowed only if its certified gain against the incumbent is at least -ell for every
    take-up curve of the declared shape class that fits the intervals.  Only this step uses the class.
  * Search: a line search.  It pilots the deepest safe cut (and moves a running pilot deeper once a rate at
    least `extend` times as far has become safe), keeps the direction after an adoption, halves the step after
    a rejected pilot, gives up a direction after an unresolved one, and turns to rate increases (when the class
    makes any safe) once cuts are done.  While no rate in the current direction is safe yet, it waits for more
    data; it gives up a direction in which no rate can ever be safe.  It stops when both directions are done,
    and starts again from any rate adopted later.
"""
import math

import numpy as np

from .bounds import budget, certified_gain, kl_interval, lattice_index, radius


class Anchor:
    __slots__ = ("g", "x", "j", "n", "s", "L", "U", "i", "next_cp", "state")

    def __init__(self, g, x, n0):
        self.g, self.x, self.j = g, float(x), lattice_index(g)
        self.n, self.s = 0, 0
        self.L, self.U = 0.0, 1.0              # take-up is a probability
        self.i, self.next_cp = 0, n0
        self.state = "open"                    # open | rejected | unresolved | beaten


class CertifiedRateSearch:
    def __init__(self, psi, b0, ell=None, step=0.005, ell_rel=None, shape="M", eta=None, alpha=0.05, n0=64, rho=1.5,
                 n_cap=100000, extend=1.5, ci="kl", lo=-np.inf, hi=np.inf, jmax=1200):
        if b0 <= psi:
            raise ValueError("the starting rate must exceed the break-even spread")
        if shape == "eta" and (eta is None or eta < 0):
            raise ValueError("shape 'eta' needs a slope bound eta >= 0")
        if (ell is None) == (ell_rel is None):
            raise ValueError("give exactly one of ell (fixed budget) and ell_rel (share of the incumbent's profit)")
        self.psi, self.b0, self.step = float(psi), float(b0), float(step)
        self.ell_fixed, self.ell_rel = (None if ell is None else float(ell)), ell_rel
        self.shape, self.eta, self.alpha = shape, eta, alpha
        self.n0, self.rho, self.n_cap, self.jmax, self.extend, self.ci = n0, rho, n_cap, jmax, extend, ci
        self.lo, self.hi = max(lo, psi), hi
        self.anchors = {}
        self.inc = self._anchor(0)
        self.ch = None
        self.dir, self.cap, self.exhausted, self.done = -1, {-1: None, 1: None}, {-1: False, 1: False}, False
        self.t, self._t0 = 0, 0
        self.moves = []      # (t, from rate, to rate)
        self.pilots = []     # (t start, incumbent rate, pilot rate, outcome, pilot quotes, budget at start)
        self._ell0 = None
        self.last_raw = (0.0, 1.0)

    # ------------------------------------------------------------ bookkeeping
    def _anchor(self, g):
        if g not in self.anchors:
            self.anchors[g] = Anchor(g, self.b0 + g * self.step, self.n0)
        return self.anchors[g]

    def update_ci(self, A):
        """Checkpoint i of anchor j: intersect the running interval with the new one."""
        dl = budget(self.alpha, A.j, A.i)
        m = A.s / A.n
        if self.ci == "kl":
            lo, up = kl_interval(m, A.n, dl)
        else:
            r = radius(A.n, dl)
            lo, up = m - r, m + r
        self.last_raw = (lo, up)
        L, U = max(A.L, lo), min(A.U, up)
        if L <= U:                             # an empty intersection is only possible off the confidence event
            A.L, A.U = L, U
        A.i += 1
        A.next_cp = max(A.n + 1, int(math.ceil(A.next_cp * self.rho)))

    def block(self, remaining):
        """Quotes to serve until the next checkpoint: [(anchor, n)], alternating while a pilot runs."""
        inc = self.inc
        if self.ch is None or remaining < 2:
            return [(inc, min(inc.next_cp - inc.n, remaining))]
        ch = self.ch
        k = min(inc.next_cp - inc.n, ch.next_cp - ch.n, self.n_cap - ch.n, remaining // 2)
        return [(inc, k), (ch, k)]

    def feed(self, served):
        """served: [(anchor, n quotes, acceptances)]."""
        for A, n, k in served:
            A.n += n
            A.s += k
            self.t += n
            if A.n == A.next_cp:
                self.update_ci(A)
        self.decide()

    # --------------------------------------------------------------- decisions
    def decide(self):
        psi, b = self.psi, self.inc
        best, gbest = None, 0.0                # 1. adoption by direct comparison
        for A in self.anchors.values():
            if A is b or A.n == 0:
                continue
            ga = (A.x - psi) * A.L - (b.x - psi) * b.U
            if ga > gbest:
                best, gbest = A, ga
        if best is not None:
            if self.ch is not None:
                self._log_pilot("adopted" if best is self.ch else "superseded")
                self.ch = None
            self.moves.append((self.t, b.x, best.x))
            b.state = "beaten"
            self.dir = -1 if best.x < b.x else 1
            self.inc, self.cap, self.exhausted = best, {-1: None, 1: None}, {-1: False, 1: False}
            self.done = False                  # a new incumbent reopens the search in both directions
            best.state = "open"
            b = best
        if self.ch is not None:                # 2. certified rejection, or the pilot cap
            c = self.ch
            if (c.x - psi) * c.U < (b.x - psi) * b.L:
                self._end_pilot("rejected")
            elif c.n >= self.n_cap:
                self._end_pilot("unresolved")
        if self.ch is not None and self.extend:  # 3. deepen a running pilot once a deeper rate has become safe
            c = self.ch
            d = 1 if c.g > b.g else -1
            k = abs(c.g - b.g)
            ks = self.safe_steps(d) if self.cap[d] is None else min(self.cap[d], self.safe_steps(d))
            A = self.anchors.get(b.g + d * ks)
            if ks >= self.extend * k and (A is None or A.state == "open"):
                self._log_pilot("extended")
                self.ch, self._t0, self._ell0 = self._anchor(b.g + d * ks), self.t, self.ell
        if self.ch is None and not self.done and b.n >= self.n0:
            self._propose()                    # 4. next pilot

    def _log_pilot(self, outcome):
        self.pilots.append((self._t0, self.inc.x, self.ch.x, outcome, self.ch.n, self._ell0))

    def _end_pilot(self, outcome):
        c = self.ch
        c.state = outcome
        self._log_pilot(outcome)
        self.ch = None
        d = 1 if c.g > self.inc.g else -1
        if outcome == "rejected":              # overshoot: the better rates, if any, are nearer
            self._shrink(d, abs(c.g - self.inc.g))
        else:                                  # undecided: the remaining gain in this direction is below resolution
            self.exhausted[d] = True
            self.done = self.exhausted[-1] and self.exhausted[1]

    def _shrink(self, d, k):
        self.cap[d] = k // 2
        if self.cap[d] == 0:
            self.exhausted[d] = True
            self.done = self.exhausted[-1] and self.exhausted[1]

    @property
    def ell(self):
        """Risk budget per pilot quote: fixed, or a share of the incumbent's certified profit (b - psi) L_b,
        which is at most its true profit on the confidence event."""
        if self.ell_fixed is not None:
            return self.ell_fixed
        return self.ell_rel * (self.inc.x - self.psi) * self.inc.L

    def safe_steps(self, d, collapse=None):
        """Largest k such that the k nearest lattice rates in direction d all have certified gain >= -ell.
        With collapse=c the incumbent's interval is replaced by [c, c] (and the budget by its value at c).  The
        intervals its future data can produce lie inside [L_b, U_b].  For the classes "M" and "eta" every rule
        is a maximum of functions affine in c, so the safety margin of a rate is convex in c: if no step is safe
        at c = L_b or at c = U_b, none will ever be while only the incumbent is quoted.  For "C" one chord term
        is concave in c, so there the two-ended test is a heuristic for when to stop; it does not affect safety."""
        A = sorted(self.anchors.values(), key=lambda a: a.x)
        xs = np.array([a.x for a in A])
        L = np.array([a.L for a in A])
        U = np.array([a.U for a in A])
        ib = A.index(self.inc)
        ell = self.ell
        if collapse is not None:
            L[ib] = U[ib] = collapse
            if self.ell_fixed is None:
                ell = self.ell_rel * (self.inc.x - self.psi) * collapse
        H = self.inc.x + d * self.step * np.arange(1, self.jmax + 1)
        ok = (H > self.psi + 1e-12) & (H >= self.lo - 1e-12) & (H <= self.hi + 1e-12)
        first_bad = np.nonzero(~ok)[0]
        H = H[: first_bad[0]] if len(first_bad) else H
        if len(H) == 0:
            return 0
        safe = certified_gain(H, xs, L, U, ib, self.psi, self.shape, self.eta) >= -ell
        bad = np.nonzero(~safe)[0]
        return int(bad[0]) if len(bad) else len(H)

    def _propose(self):
        """Pilot in the current direction if a new safe rate exists; a direction in which no rate can ever be
        safe is given up; while the current direction only needs more data, the other one may be used."""
        for d in (self.dir, -self.dir):
            while not self.exhausted[d]:
                ks = self.safe_steps(d)
                k = ks if self.cap[d] is None else min(self.cap[d], ks)
                if k <= 0:
                    if self.safe_steps(d, collapse=self.inc.L) == 0 and self.safe_steps(d, collapse=self.inc.U) == 0:
                        self.exhausted[d] = True
                        self.done = self.exhausted[-1] and self.exhausted[1]
                    break
                A = self.anchors.get(self.inc.g + d * k)
                if A is not None and A.state != "open":
                    self._shrink(d, k)         # tried before: halve the step
                    continue
                self.ch, self.dir, self._t0, self._ell0 = self._anchor(self.inc.g + d * k), d, self.t, self.ell
                return
            if not self.exhausted[d]:
                return                         # the current direction needs more data: wait


def run_certified(market, b0, T, rng, n_hist=0, **kw):
    """Simulate the certified rate search for T quotes.  n_hist quotes at b0 precede it (history, not counted).
    The simulator knows the true take-up, so it also records whether any interval ever missed it, that is,
    whether the confidence event failed in this run."""
    ag = CertifiedRateSearch(market.psi, b0, lo=market.lo, hi=market.hi, **kw)
    miss = []
    update = ag.update_ci

    def checked_update(A):
        update(A)
        lo, up = ag.last_raw                   # the interval of this checkpoint alone, before intersecting
        if not miss and not (lo <= float(market.a(A.x)) <= up):
            miss.append(ag.t)
    ag.update_ci = checked_update
    h = int(n_hist)
    while h > 0:
        A = ag.inc
        n = min(A.next_cp - A.n, h)
        k = market.draw(rng, A.x, n)
        A.n += n
        A.s += k
        h -= n
        if A.n == A.next_cp:
            ag.update_ci(A)
    ag.decide()
    served, t = [], 0
    while t < T:
        out = []
        for A, n in ag.block(T - t):
            k = market.draw(rng, A.x, n)
            out.append((A, n, k))
            served.append((A.x, n))
            t += n
        ag.feed(out)
    if ag.ch is not None:
        ag._log_pilot("running")
    return dict(served=served, final=ag.inc.x, moves=ag.moves, pilots=ag.pilots,
                ci_miss=bool(miss), ci_miss_t=(miss[0] if miss else None))
