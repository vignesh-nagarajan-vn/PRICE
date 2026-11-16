"""Independent numerical and symbolic checks of every formal statement in the paper.

    python -u verification/verify_math.py

The checks are organised by the numbering used in the paper.  Each check
prints one line; the script exits with status 1 if any check fails.

Three kinds of evidence are produced.

  symbolic   identities verified with sympy for generic functions
  random     inequalities tested on randomly drawn members of the model
             class (several families for the known profit part K and for
             the flow curve tau, including curves that are not smooth)
  end-to-end runs of the actual agent in which the truth of the confidence
             event is recorded, so that the guarantees can be checked on the
             runs where the event holds

Nothing here replaces the proofs.  The Lean development checks the same
statements formally; this script guards against a mismatch between the
statements, the formulas typeset in the paper and the code.
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import sympy as sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ctrr.agent import CTRR, certified_gain, lower_envelope, tangent_response, trr_rate, trr_step  # noqa: E402
from ctrr.model import Env, standard_markets                                                       # noqa: E402

RNG = np.random.default_rng(20261113)
TOL = 1e-9
RESULTS = []


def report(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""), flush=True)


# ---------------------------------------------------------------- random model class
class KFam:
    """Known profit part with K'' <= -gmin < 0 and -K'' <= gbar on [psi, hbar]."""

    def __init__(self, kind, hbar):
        self.kind, self.hbar = kind, hbar
        r = RNG.uniform
        if kind == "inst":      # h A exp(-k h) - w (h - href)^2
            self.A, self.k, self.w, self.href = r(0.5, 2), r(0.5, 2.5), r(0.3, 1.0), r(0.5, 2.0)
            self.gmin = 2 * self.w - self.A * self.k * math.exp(-3)
            self.gbar = 2 * self.A * self.k + 2 * self.w
        elif kind == "quad":    # a h - g h^2 / 2
            self.a, self.g = r(0.5, 3), r(0.3, 2)
            self.gmin = self.gbar = self.g
        else:                   # a log(1 + h) - w (h - href)^2
            self.a, self.w, self.href = r(0.5, 3), r(0.2, 1.0), r(0.5, 2.0)
            self.gmin = 2 * self.w + self.a / (1 + hbar) ** 2
            self.gbar = 2 * self.w + self.a

    def K(self, h):
        h = np.asarray(h, float)
        if self.kind == "inst":
            return h * self.A * np.exp(-self.k * h) - self.w * (h - self.href) ** 2
        if self.kind == "quad":
            return self.a * h - 0.5 * self.g * h ** 2
        return self.a * np.log1p(h) - self.w * (h - self.href) ** 2

    def Kp(self, h):
        h = np.asarray(h, float)
        if self.kind == "inst":
            return self.A * np.exp(-self.k * h) * (1 - self.k * h) - 2 * self.w * (h - self.href)
        if self.kind == "quad":
            return self.a - self.g * h
        return self.a / (1 + h) - 2 * self.w * (h - self.href)

    def Kpp(self, h):
        h = np.asarray(h, float)
        if self.kind == "inst":
            return -(self.A * self.k * np.exp(-self.k * h) * (2 - self.k * h) + 2 * self.w)
        if self.kind == "quad":
            return -self.g * np.ones_like(h)
        return -self.a / (1 + h) ** 2 - 2 * self.w


class TauFam:
    """Flow curves that are nonnegative, nonincreasing and convex."""

    def __init__(self, kind):
        self.kind = kind
        r = RNG.uniform
        self.C0 = r(0.0, 1.0)
        if kind == "exp":
            self.C1, self.c = r(0.2, 12), r(0.5, 2.5)
        elif kind == "power":
            self.C1, self.p = r(0.2, 12), r(0.5, 3.0)
        elif kind == "exp2":
            self.C1, self.c, self.C2, self.c2 = r(0.2, 8), r(0.5, 2.5), r(0.2, 8), r(0.2, 4.0)
        elif kind == "cubic":   # C0 + C1 max(1 - h/a, 0)^3, twice continuously differentiable
            self.C1, self.a = r(0.2, 12), r(1.0, 5.0)
        else:                   # "pl": max of decreasing lines and a floor, not differentiable
            n = RNG.integers(2, 6)
            self.s = np.sort(r(0.05, 4.0, n))[::-1]
            self.x0 = np.sort(r(0.3, 4.5, n))
            self.lines = []
            v = self.C0
            for i in range(n - 1, -1, -1):      # build from the right so the max is convex
                self.lines.append((v + self.s[i] * self.x0[i], self.s[i]))
                v = v + self.s[i] * 0.1

    smooth = property(lambda self: self.kind != "pl")

    def tau(self, h):
        h = np.asarray(h, float)
        if self.kind == "exp":
            return self.C0 + self.C1 * np.exp(-self.c * h)
        if self.kind == "power":
            return self.C0 + self.C1 * (1 + h) ** (-self.p)
        if self.kind == "exp2":
            return self.C0 + self.C1 * np.exp(-self.c * h) + self.C2 * np.exp(-self.c2 * h)
        if self.kind == "cubic":
            return self.C0 + self.C1 * np.maximum(1 - h / self.a, 0.0) ** 3
        out = np.full(h.shape, self.C0)
        for a, s in self.lines:
            out = np.maximum(out, a - s * h)
        return out

    def d1(self, h):
        h = np.asarray(h, float)
        if self.kind == "exp":
            return -self.c * self.C1 * np.exp(-self.c * h)
        if self.kind == "power":
            return -self.p * self.C1 * (1 + h) ** (-self.p - 1)
        if self.kind == "exp2":
            return -self.c * self.C1 * np.exp(-self.c * h) - self.c2 * self.C2 * np.exp(-self.c2 * h)
        if self.kind == "cubic":
            return -3 * self.C1 / self.a * np.maximum(1 - h / self.a, 0.0) ** 2
        raise ValueError

    def d2(self, h):
        h = np.asarray(h, float)
        if self.kind == "exp":
            return self.c ** 2 * self.C1 * np.exp(-self.c * h)
        if self.kind == "power":
            return self.p * (self.p + 1) * self.C1 * (1 + h) ** (-self.p - 2)
        if self.kind == "exp2":
            return (self.c ** 2 * self.C1 * np.exp(-self.c * h)
                    + self.c2 ** 2 * self.C2 * np.exp(-self.c2 * h))
        if self.kind == "cubic":
            return 6 * self.C1 / self.a ** 2 * np.maximum(1 - h / self.a, 0.0)
        raise ValueError


class Inst:
    """One random instance of the model class."""

    def __init__(self, smooth=True):
        self.psi = RNG.uniform(0.1, 0.6)
        self.hbar = RNG.uniform(4.0, 6.0)
        self.Kf = KFam(RNG.choice(["inst", "quad", "log"]), self.hbar)
        kinds = ["exp", "power", "exp2", "cubic"] + ([] if smooth else ["pl", "pl"])
        self.Tf = TauFam(RNG.choice(kinds))
        self.K, self.Kp, self.Kpp = self.Kf.K, self.Kf.Kp, self.Kf.Kpp
        self.tau = self.Tf.tau
        self.gmin, self.gbar = self.Kf.gmin, self.Kf.gbar

    def Phi(self, h):
        return self.K(h) + (np.asarray(h, float) - self.psi) * self.tau(h)

    def dPhi(self, h):
        return self.Kp(h) + self.tau(h) + (np.asarray(h, float) - self.psi) * self.Tf.d1(h)

    def J(self, h, t):
        return self.K(h) + (np.asarray(h, float) - self.psi) * t

    def stable(self):
        """Interior root of K' + tau, or None.  K' + tau is strictly decreasing."""
        f = lambda h: float(self.Kp(h) + self.tau(h))
        lo, hi = self.psi, self.hbar
        if f(lo) <= 0 or f(hi) >= 0:
            return None
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return 0.5 * (lo + hi)

    def bisect_dec(self, d):
        """Maximizer on [psi, hbar] of a concave function with decreasing derivative d."""
        lo, hi = self.psi, self.hbar
        if d(lo) <= 0:
            return lo
        if d(hi) >= 0:
            return hi
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if d(mid) > 0 else (lo, mid)
        return 0.5 * (lo + hi)

    def T(self, b):
        """Tangent-response map."""
        tb, sb = float(self.tau(b)), float(self.Tf.d1(b))
        return self.bisect_dec(lambda h: float(self.Kp(h)) + tb + sb * (h - b) + (h - self.psi) * sb)

    def S(self, b, h):
        return self.K(h) + (np.asarray(h, float) - self.psi) * (self.tau(b) + self.Tf.d1(b) * (h - b))

    def BR(self, t):
        return self.bisect_dec(lambda h: float(self.Kp(h)) + t)


def instances(n, smooth=True, need_stable=False):
    out = []
    while len(out) < n:
        I = Inst(smooth)
        if need_stable:
            hs = I.stable()
            if hs is None or hs - I.psi < 0.3 or I.hbar - hs < 0.3:
                continue
            I.hs = hs
        out.append(I)
    return out


# ------------------------------------------------------------------ symbolic checks
def symbolic():
    h, b, psi, x = sp.symbols("h b psi x", real=True)
    K, tau, T = sp.Function("K"), sp.Function("tau"), sp.Function("T")
    Phi = K(h) + (h - psi) * tau(h)
    ok = sp.simplify(sp.diff(Phi, h) - (sp.diff(K(h), h) + tau(h) + (h - psi) * sp.diff(tau(h), h))) == 0
    report("S1  Phi' = K' + tau + (h - psi) tau'", ok)

    # Lemma 1(a): at a stable quote the slope of Phi is (h - psi) tau'
    Kp_s, tau_s, taup_s = sp.symbols("Kp_s tau_s taup_s", real=True)
    slope = (Kp_s + tau_s + (h - psi) * taup_s).subs(Kp_s, -tau_s)
    report("S2  Lemma 1(a): slope at a stable quote is (h - psi) tau'", sp.simplify(slope - (h - psi) * taup_s) == 0)
    report("S3  Lemma 1(c): Phi(h_s) = K(h_s) - (h_s - psi) K'(h_s)",
           sp.simplify((sp.Symbol("K_s") + (h - psi) * tau_s).subs(tau_s, -Kp_s)
                       - (sp.Symbol("K_s") - (h - psi) * Kp_s)) == 0)

    # Lemma 2 / Theorem 2(a): surrogate touches Phi at b with the same slope
    tb, sb = sp.symbols("tau_b s_b", real=True)
    S = K(h) + (h - psi) * (tb + sb * (h - b))
    ok1 = sp.simplify(S.subs(h, b) - (K(b) + (b - psi) * tb)) == 0
    dS = sp.diff(S, h).subs(h, b)
    ok2 = sp.simplify(dS - (sp.diff(K(h), h).subs(h, b) + tb + (b - psi) * sb)) == 0
    report("S4  Theorem 2(a): S_b(b) = Phi(b) and S_b'(b) = Phi'(b)", ok1 and ok2)

    # Theorem 2(b): implicit differentiation of the first-order condition of the surrogate.
    # G(x, y) = K'(y) + tau(x) + tau'(x)(y - x) + (y - psi) tau'(x) vanishes at y = T(x).
    # The chain rule gives G_x + G_y T'(x) = 0; at a fixed point y = x the two partial
    # derivatives are (x - psi) tau''(x) and K''(x) + 2 tau'(x).
    y = sp.Symbol("y", real=True)
    Kp = sp.Function("Kp")
    taup = sp.diff(tau(x), x)
    G = Kp(y) + tau(x) + taup * (y - x) + (y - psi) * taup
    Gx = sp.diff(G, x).subs(y, x)
    Gy = sp.diff(G, y).subs(y, x)
    ok = sp.simplify(Gx - (x - psi) * sp.diff(tau(x), x, 2)) == 0 and \
        sp.simplify(Gy - (sp.diff(Kp(x), x) + 2 * taup)) == 0
    report("S5  Theorem 2(b): T'(K'' + 2 tau') + (b - psi) tau'' = 0", ok)
    T1, t2 = sp.symbols("T1 t2", real=True)
    g, e = sp.symbols("gamma epsilon", positive=True)
    rate = sp.solve(sp.Eq(T1 * (-g - 2 * e) + (b - psi) * t2, 0), T1)[0]
    ok = sp.simplify(rate - (b - psi) * t2 / (g + 2 * e)) == 0 and \
        sp.simplify(rate - (1 - (g + 2 * e - (b - psi) * t2) / (g + 2 * e))) == 0
    report("S6  Theorem 2(b): T' = (b - psi) tau''/(gamma + 2 eps) = 1 - gamma_PO/(gamma + 2 eps)", ok)
    R1 = sp.Symbol("R1", real=True)
    ok = sp.simplify(sp.solve(sp.Eq(R1 * (-g) + (-e), 0), R1)[0] + e / g) == 0
    report("S7  Theorem 2(c): slope of the retraining map is -eps/gamma", ok)

    # quadratic K: the tangent-response step in closed form
    Kq, gq, tq, eq = sp.symbols("Kp_b gamma tau_b eps", real=True)
    foc = (Kq - gq * (h - b)) + (tq - eq * (h - b)) + (h - psi) * (-eq)
    sol = sp.solve(sp.Eq(foc, 0), h)[0]
    report("S8  quadratic K: step = b + Phi'(b)/(gamma + 2 eps)",
           sp.simplify(sol - (b + (Kq + tq - (b - psi) * eq) / (gq + 2 * eq))) == 0)

    # joint rules: exact algebra behind the coefficients c_b and c_a
    a, tb_, ta_ = sp.symbols("a tau_b tau_a", real=True)
    low_left = (tb_ * (a - h) - ta_ * (b - h)) / (a - b)        # chord (b, a) extended to h <= b
    cb = (h - psi) * (a - h) / (a - b) - (b - psi)
    ca = -(h - psi) * (b - h) / (a - b)
    ok1 = sp.simplify((h - psi) * low_left - (b - psi) * tb_ - (cb * tb_ + ca * ta_)) == 0
    low_right = (tb_ * (h - a) - ta_ * (h - b)) / (b - a)       # chord (a, b) extended to h >= b
    cb = (h - psi) * (h - a) / (b - a) - (b - psi)
    ca = -(h - psi) * (h - b) / (b - a)
    ok2 = sp.simplify((h - psi) * low_right - (b - psi) * tb_ - (cb * tb_ + ca * ta_)) == 0
    report("S9  Theorem 3: coefficients of the joint rules (left and right)", ok1 and ok2)

    # the numerical instance
    A, k, w, href = sp.symbols("A k w h_ref", positive=True)
    Ki = h * A * sp.exp(-k * h) - w * (h - href) ** 2
    ok1 = sp.simplify(sp.diff(Ki, h) - (A * sp.exp(-k * h) * (1 - k * h) - 2 * w * (h - href))) == 0
    ok2 = sp.simplify(sp.diff(Ki, h, 2) + (A * k * sp.exp(-k * h) * (2 - k * h) + 2 * w)) == 0
    report("S10 instance: K' and K'' formulas", ok1 and ok2)
    f = sp.exp(-x) * (2 - x)
    crit = sp.solve(sp.diff(f, x), x)
    ok = crit == [3] and sp.simplify(f.subs(x, 3) + sp.exp(-3)) == 0 and sp.diff(f, x, 2).subs(x, 3) > 0
    report("S11 instance: min of exp(-x)(2 - x) is -exp(-3), so gamma >= 2w - A k exp(-3)", ok)
    C0, C1, c = sp.symbols("C0 C1 c", positive=True)
    ti = C0 + C1 * sp.exp(-c * h)
    Phii = Ki + (h - psi) * ti
    gpo = (A * k * sp.exp(-k * h) * (2 - k * h) + 2 * w) + 2 * c * C1 * sp.exp(-c * h) \
        - (h - psi) * c ** 2 * C1 * sp.exp(-c * h)
    report("S12 instance: -Phi'' = gamma + 2 eps - (h - psi) tau''", sp.simplify(sp.diff(Phii, h, 2) + gpo) == 0)

    # confidence radius and schedule
    sig, dl, n = sp.symbols("sigma delta n", positive=True)
    r = sig * sp.sqrt(2 * sp.log(2 / dl) / n)
    report("S13 Theorem 5: 2 exp(-n r^2 / (2 sigma^2)) = delta", sp.simplify(2 * sp.exp(-n * r ** 2 / (2 * sig ** 2)) - dl) == 0)
    i, j, m_, n_ = sp.symbols("i j m n", integer=True, positive=True)
    s1 = sp.summation(1 / (i * (i + 1)), (i, 1, n_))
    report("S14 Theorem 5: sum_{i<=n} 1/(i(i+1)) = 1 - 1/(n+1)", sp.simplify(s1 - (1 - 1 / (n_ + 1))) == 0)
    Dl, mm = sp.symbols("Delta m", positive=True)
    nstar = 8 * sig ** 2 * sp.log(2 / dl) * mm ** 2 / Dl ** 2
    report("S15 Proposition 4: at n = 8 sigma^2 log(2/delta) m^2 / Delta^2 the margin 2 m r equals Delta",
           sp.simplify((2 * mm * r.subs(n, nstar)) ** 2 - Dl ** 2) == 0)


# -------------------------------------------------------------------- random checks
def lemma1():
    bad_a = bad_b = bad_c = 0
    worst = 0.0
    for I in instances(400, need_stable=True):
        hs = I.hs
        # (a) slope of Phi at the stable quote, against a central difference
        e = 1e-5
        num = float(I.Phi(hs + e) - I.Phi(hs - e)) / (2 * e)
        slope = (hs - I.psi) * float(I.Tf.d1(hs))
        bad_a += not (abs(num - slope) < 1e-5 * (1 + abs(slope)) and slope <= 0)
        # (b) wider quotes are no better, through the frozen profit
        H = np.linspace(hs, I.hbar, 400)
        ts = float(I.tau(hs))
        mid = I.J(H, ts)
        bad_b += not (np.all(I.Phi(H) <= mid + TOL) and np.all(mid <= float(I.Phi(hs)) + 1e-7))
        worst = max(worst, float(np.max(I.Phi(H) - I.Phi(hs))))
        # (c) flow and profit at the stable quote from K alone
        bad_c += not (abs(ts + float(I.Kp(hs))) < 1e-9
                      and abs(float(I.Phi(hs)) - (float(I.K(hs)) - (hs - I.psi) * float(I.Kp(hs)))) < 1e-9)
    report("L1a Lemma 1(a): Phi'(h_s) = (h_s - psi) tau'(h_s) <= 0", bad_a == 0, "400 instances")
    report("L1b Lemma 1(b): Phi(h) <= J(h; tau(h_s)) <= Phi(h_s) for h >= h_s", bad_b == 0,
           f"400 instances, max Phi(h) - Phi(h_s) = {worst:.2e}")
    report("L1c Lemma 1(c): tau(h_s) = -K'(h_s), Phi(h_s) = K(h_s) - (h_s - psi) K'(h_s)", bad_c == 0)


def prop1():
    """Survival functions of nonincreasing densities are convex and nonincreasing."""
    bad = 0
    x = np.linspace(0, 8, 4001)
    for _ in range(300):
        kind = RNG.integers(0, 4)
        if kind == 0:       # mixture of uniforms on [0, a_i]: every nonincreasing density has this form
            a = RNG.uniform(0.3, 8, 5)
            p = RNG.dirichlet(np.ones(5))
            S = sum(pi * np.maximum(1 - x / ai, 0.0) for pi, ai in zip(p, a))
        elif kind == 1:     # exponential
            S = np.exp(-RNG.uniform(0.3, 3) * x)
        elif kind == 2:     # Lomax (Pareto type II)
            S = (1 + x / RNG.uniform(0.5, 3)) ** (-RNG.uniform(0.5, 4))
        else:               # half-normal
            s = RNG.uniform(0.5, 3)
            S = np.array([math.erfc(v / (s * math.sqrt(2))) for v in x])
        d2 = S[2:] - 2 * S[1:-1] + S[:-2]
        bad += not (np.all(np.diff(S) <= 1e-12) and np.all(d2 >= -1e-12) and np.all(S >= -1e-12))
    report("P1  Proposition 1: survival function of a nonincreasing density is in the shape class", bad == 0,
           "300 distributions")
    # a density that increases somewhere gives a survival function that is not convex
    S = np.array([0.5 * math.erfc((v - 2.0) / math.sqrt(2)) for v in x])
    report("P1' Proposition 1 is not vacuous: a unimodal density with interior mode fails convexity",
           np.any(S[2:] - 2 * S[1:-1] + S[:-2] < -1e-9))


def lemma2_theorem1():
    bad_min = bad_eq = bad_asc = bad_sum = bad_mono = bad_stat = 0
    n_int = 0
    worst_ratio = np.inf
    for I in instances(300):
        H = np.linspace(I.psi, I.hbar, 600)
        phimax = float(np.max(I.Phi(np.linspace(I.psi, I.hbar, 20001))))
        for b in RNG.uniform(I.psi, I.hbar, 3):
            Sb = I.S(b, H)
            bad_min += not np.all(Sb <= I.Phi(H) + TOL)
            bad_eq += not abs(float(I.S(b, b)) - float(I.Phi(b))) < 1e-10
            bp = I.T(b)
            gain = float(I.Phi(bp) - I.Phi(b))
            need = 0.5 * I.gmin * (bp - b) ** 2
            bad_asc += not gain >= need - 1e-9
            if need > 1e-6:
                worst_ratio = min(worst_ratio, gain / need)
        # iterate
        b = float(RNG.uniform(I.psi, I.hbar))
        b0, ssq, prev = b, 0.0, float(I.Phi(b))
        for _ in range(4000):
            bn = I.T(b)
            ssq += (bn - b) ** 2
            cur = float(I.Phi(bn))
            bad_mono += not cur >= prev - 1e-10
            prev, step, b = cur, abs(bn - b), bn
            if step < 1e-11:
                break
        bad_sum += not ssq <= 2 * (phimax - float(I.Phi(b0))) / I.gmin + 1e-8
        interior = I.psi + 1e-6 < b < I.hbar - 1e-6
        if interior:
            n_int += 1
            bad_stat += not abs(float(I.dPhi(b))) < 1e-5
        else:   # at a boundary the one-sided slope must point outward
            bad_stat += not ((b <= I.psi + 1e-6 and float(I.dPhi(b)) <= 1e-6)
                             or (b >= I.hbar - 1e-6 and float(I.dPhi(b)) >= -1e-6))
    report("L2  Lemma 2: S_b <= Phi on [psi, hbar], with equality at b", bad_min == 0 and bad_eq == 0, "900 pairs")
    report("T1a Theorem 1: Phi(b+) - Phi(b) >= (gamma_min/2)(b+ - b)^2", bad_asc == 0,
           f"900 steps, smallest gain/bound ratio {worst_ratio:.3f}")
    report("T1b Theorem 1: profit nondecreasing and sum of squared steps bounded", bad_mono == 0 and bad_sum == 0,
           "300 trajectories")
    report("T1c Theorem 1: the limit is stationary (or a boundary point with outward slope)", bad_stat == 0,
           f"{n_int} interior limits of 300")


def theorem2():
    bad_fix = bad_rate = bad_rng = bad_R = bad_stab = 0
    n_rate = n_stab = n_unst = 0
    for I in instances(300, need_stable=True):
        # (a) fixed points and stationary points coincide in the interior
        b = I.hs
        for _ in range(6000):
            bn = I.T(b)
            if abs(bn - b) < 1e-12:
                break
            b = bn
        if I.psi + 1e-4 < b < I.hbar - 1e-4:
            bad_fix += not (abs(I.T(b) - b) < 1e-9 and abs(float(I.dPhi(b))) < 1e-6)
            g, ep, t2 = -float(I.Kpp(b)), -float(I.Tf.d1(b)), float(I.Tf.d2(b))
            gpo = g + 2 * ep - (b - I.psi) * t2
            if gpo > 1e-3 and not (I.Tf.kind == "cubic" and abs(b - I.Tf.a) < 1e-2):
                e = 1e-5
                num = (I.T(b + e) - I.T(b - e)) / (2 * e)
                rate = (b - I.psi) * t2 / (g + 2 * ep)
                n_rate += 1
                bad_rate += not abs(num - rate) < 2e-4
                bad_rng += not (0 <= rate < 1 and abs(rate - (1 - gpo / (g + 2 * ep))) < 1e-12)
        # (c) retraining map at the stable quote
        hs = I.hs
        e = 1e-5
        numR = (I.BR(float(I.tau(hs + e))) - I.BR(float(I.tau(hs - e)))) / (2 * e)
        m = -float(I.Tf.d1(hs)) / -float(I.Kpp(hs))
        bad_R += not abs(numR + m) < 2e-4 * (1 + m)
        x = hs + 1e-3
        if m < 0.9:
            n_stab += 1
            for _ in range(400):
                x = I.BR(float(I.tau(x)))
            bad_stab += not abs(x - hs) < 1e-8
        elif m > 1.1:
            n_unst += 1
            bad_stab += not abs(I.BR(float(I.tau(x))) - hs) > abs(x - hs)
    report("T2a Theorem 2(a): the limit of the iteration is a fixed point with Phi' = 0", bad_fix == 0)
    report("T2b Theorem 2(b): T'(b) matches (b - psi) tau''/(gamma + 2 eps), in [0, 1) when gamma_PO > 0",
           bad_rate == 0 and bad_rng == 0, f"{n_rate} fixed points")
    report("T2c Theorem 2(c): R'(h_s) = -eps/gamma; contraction if m < 1, repulsion if m > 1",
           bad_R == 0 and bad_stab == 0, f"{n_stab} stable and {n_unst} unstable cases")


def prop2():
    bad1 = bad2 = 0
    for I in instances(300, smooth=False):
        b = float(RNG.uniform(I.psi + 0.2, I.hbar))
        H = np.linspace(I.psi, b, 300)
        lhs = I.Phi(H) - float(I.Phi(b))
        tb = float(I.tau(b))
        bad1 += not np.all(lhs >= I.K(H) - float(I.K(b)) - (b - H) * tb - TOL)
        bad1 += not np.all(lhs >= I.K(H) - float(I.K(b)) - (b - H) * (tb + 0.3) - TOL)
    for I in instances(300, need_stable=True):
        b = I.hs
        H = np.linspace(I.psi, b, 300)
        bad2 += not np.all(I.Phi(H) - float(I.Phi(b)) >= -0.5 * I.gbar * (b - H) ** 2 - TOL)
        ell = float(RNG.uniform(0.001, 0.2))
        d = math.sqrt(2 * ell / I.gbar)
        if b - d >= I.psi:
            bad2 += not float(I.Phi(b - d) - I.Phi(b)) >= -ell - TOL
    report("P2a Proposition 2: Phi(h) - Phi(b) >= K(h) - K(b) - (b - h) U_b for psi <= h <= b", bad1 == 0)
    report("P2b Proposition 2: at a stable b the loss is at most (gamma_bar/2)(b - h)^2; d = sqrt(2 ell/gamma_bar) is safe",
           bad2 == 0)


def theorem3():
    bad_env = bad_gain = bad_rule = bad_self = 0
    n = 0
    slack = []
    for I in instances(1500, smooth=False):
        m = int(RNG.integers(1, 7))
        xs = np.sort(RNG.uniform(I.psi, I.hbar, m))
        if m > 1 and np.min(np.diff(xs)) < 1e-3:
            continue
        tv = I.tau(xs)
        wl = RNG.uniform(0, 0.6, m) * (RNG.random(m) < 0.8)
        wu = RNG.uniform(0, 0.6, m) * (RNG.random(m) < 0.8)
        L, U = tv - wl, tv + wu
        ib = int(RNG.integers(0, m))
        H = np.linspace(I.psi, I.hbar, 500)
        truth = I.tau(H)
        env = lower_envelope(H, xs, L, U)
        bad_env += not np.all(env <= truth + TOL)

        class MK:           # the certificate code reads only K and psi
            psi = I.psi
            K = staticmethod(I.K)
        g = certified_gain(MK, H, xs, L, U, ib)
        true_gain = I.Phi(H) - float(I.Phi(xs[ib]))
        bad_gain += not np.all(g <= true_gain + TOL)
        slack.append(float(np.min(true_gain - g)))
        # with exact intervals the certificate is exact at the incumbent itself
        g0 = certified_gain(MK, np.array([xs[ib]]), xs, tv, tv, ib)[0]
        bad_self += not abs(g0) < 1e-9
        # each rule separately, written out independently of the code
        b, Lb, Ub = xs[ib], L[ib], U[ib]
        Kb = float(I.K(b))
        for hq in RNG.uniform(I.psi, I.hbar, 6):
            th = float(I.tau(hq))
            tg = float(I.Phi(hq) - I.Phi(b))
            lows = [0.0]
            for p in range(m):
                if hq <= xs[p]:
                    lows.append(L[p])                                           # (M)
                for q in range(p + 1, m):
                    D = xs[q] - xs[p]
                    if hq <= xs[p]:
                        lows.append(L[p] + max(L[p] - U[q], 0.0) * (xs[p] - hq) / D)   # (CL)
                    if hq >= xs[q]:
                        lows.append(L[q] + min(L[q] - U[p], 0.0) * (hq - xs[q]) / D)   # (CR)
            bad_rule += not max(lows) <= th + TOL
            bounds = [float(I.K(hq)) - Kb + (hq - I.psi) * max(lows) - (b - I.psi) * Ub]
            if hq <= b:
                bounds.append(float(I.K(hq)) - Kb - (b - hq) * Ub)              # (ML)
            for p in range(m):
                a, Ua = xs[p], U[p]
                if a > b and hq <= b:                                           # (J-left)
                    cb = (hq - I.psi) * (a - hq) / (a - b) - (b - I.psi)
                    ca = -(hq - I.psi) * (b - hq) / (a - b)
                    bounds.append(float(I.K(hq)) - Kb + min(cb * Lb, cb * Ub) + ca * Ua)
                if a < b and hq >= b:                                           # (J-right)
                    cb = (hq - I.psi) * (hq - a) / (b - a) - (b - I.psi)
                    ca = -(hq - I.psi) * (hq - b) / (b - a)
                    bounds.append(float(I.K(hq)) - Kb + min(cb * Lb, cb * Ub) + ca * Ua)
            bad_rule += not max(bounds) <= tg + TOL
            # the code and the independent formulas agree
            gc = certified_gain(MK, np.array([hq]), xs, L, U, ib)[0]
            bad_rule += not abs(gc - max(bounds)) < 1e-9
        n += 1
    report("T3a Theorem 3: envelope (M), (Z), (CL), (CR) is a lower bound on tau", bad_env == 0, f"{n} instances x 500 quotes")
    report("T3b Theorem 3: certified gain <= true gain for every quote (code path used by the agent)", bad_gain == 0,
           f"min slack {min(slack):.2e}")
    report("T3c Theorem 3: each rule checked separately and against the code", bad_rule == 0 and bad_self == 0)
    # (D) direct comparison needs no shape assumption: use arbitrary (even increasing, oscillating) flows
    bad = 0
    for _ in range(2000):
        psi = RNG.uniform(0.1, 0.6)
        a, b = RNG.uniform(psi, 5, 2)
        ta, tb = RNG.uniform(-1, 5, 2)
        La, Ub = ta - RNG.uniform(0, 1), tb + RNG.uniform(0, 1)
        Ka, Kb = RNG.uniform(-2, 2, 2)
        bad += not Ka + (a - psi) * La - Kb - (b - psi) * Ub <= (Ka + (a - psi) * ta) - (Kb + (b - psi) * tb) + TOL
    report("T3d Theorem 3 (D): direct comparison is valid for arbitrary flow values", bad == 0, "2000 draws")
    # the shape assumptions are needed: a concave decreasing flow violates the chord rule
    xs = np.array([1.0, 2.0])
    f = lambda h: 4.0 - 0.5 * np.asarray(h, float) ** 2
    env = lower_envelope(np.array([0.5]), xs, f(xs), f(xs))[0]
    report("T3e Theorem 3 is not vacuous: the chord rule fails for a concave flow", env > float(f(0.5)) + 1e-6)


def prop3():
    def two_point(x1, x2, t1, t2, h):
        return np.maximum(t1 + (t2 - t1) / (x2 - x1) * (np.asarray(h, float) - x1), t2)

    def chord_floor(x1, x2, t1, t2, h):
        return np.maximum(t1 + (t2 - t1) / (x2 - x1) * (np.asarray(h, float) - x1), 0.0)

    def in_class(f, grid):
        v = f(grid)
        return np.all(v >= -1e-12) and np.all(np.diff(v) <= 1e-12) and np.all(v[2:] - 2 * v[1:-1] + v[:-2] >= -1e-10)

    bad = 0
    grid = np.linspace(0, 8, 3201)
    for _ in range(1500):
        x1 = RNG.uniform(0.5, 3.0)
        x2 = x1 + RNG.uniform(0.05, 3.0)
        t2 = RNG.uniform(0, 3) * (RNG.random() < 0.9)
        t1 = t2 + RNG.uniform(0, 3) * (RNG.random() < 0.9)
        xs, tv = np.array([x1, x2]), np.array([t1, t2])
        # region h <= x1
        h = RNG.uniform(0, x1)
        f = lambda z: two_point(x1, x2, t1, t2, z)
        env = lower_envelope(np.array([h]), xs, tv, tv)[0]
        bad += not (in_class(f, grid) and abs(f(x1) - t1) < 1e-12 and abs(f(x2) - t2) < 1e-12
                    and abs(f(h) - env) < 1e-10)
        # region x1 < h <= x2: kink at h
        h = RNG.uniform(x1 + 1e-3, x2)
        f = lambda z: two_point(x1, h, t1, t2, z)
        env = lower_envelope(np.array([h]), xs, tv, tv)[0]
        bad += not (in_class(f, grid) and abs(f(x1) - t1) < 1e-12 and abs(f(x2) - t2) < 1e-12
                    and abs(f(h) - t2) < 1e-12 and abs(env - t2) < 1e-10)
        # region h >= x2
        h = RNG.uniform(x2, 8)
        f = lambda z: chord_floor(x1, x2, t1, t2, z)
        env = lower_envelope(np.array([h]), xs, tv, tv)[0]
        bad += not (in_class(f, grid) and abs(f(x1) - t1) < 1e-12 and abs(f(x2) - t2) < 1e-12
                    and abs(f(h) - env) < 1e-10)
    report("P3  Proposition 3: with two exact anchors the envelope is attained by a member of the class in all three regions",
           bad == 0, "1500 draws x 3 regions")


def theorem4():
    bad = 0
    for I in instances(400, need_stable=True):
        b = I.hs
        tb = float(I.tau(b))
        H = np.linspace(I.psi, I.hbar, 2000)
        H = H[np.abs(H - b) > 1e-6]
        gap = float(I.J(b, tb)) - I.J(H, tb)
        bad += not (np.all(gap > 0) and np.all(gap >= 0.5 * I.gmin * (H - b) ** 2 - 1e-9))
        # the constant flow reproduces the mean observation at b and lies in the shape class trivially
        bad += not abs(float(I.J(b, tb)) - float(I.Phi(b))) < 1e-12
    report("T4  Theorem 4: under the constant flow tau(b) every other quote is strictly worse than a stable b", bad == 0,
           "400 instances")


def theorem5_probability():
    alpha, sig, n0, rho = 0.05, 1.0, 16, 1.5
    # schedule: closed form and bound
    bad = 0
    for M, N in [(1, 1), (3, 7), (40, 40), (500, 500)]:
        s = sum(alpha / (j * (j + 1) * i * (i + 1)) for j in range(1, M + 1) for i in range(1, N + 1))
        bad += not (abs(s - alpha * (1 - 1 / (M + 1)) * (1 - 1 / (N + 1))) < 1e-12 and s <= alpha)
    report("T5a Theorem 5(i): the error budget alpha/(j(j+1)i(i+1)) sums to at most alpha", bad == 0)
    # checkpoints of the code are deterministic sample counts
    cps, nxt = [], n0
    while nxt < 20000:
        cps.append(nxt)
        nxt = max(nxt + 1, int(math.ceil(nxt * rho)))
    report("T5b checkpoint sample counts are deterministic: " + ", ".join(map(str, cps[:8])) + ", ...", cps[:4] == [16, 24, 36, 54])
    # Monte Carlo: simultaneous coverage over anchors and checkpoints, Gaussian and uniform noise
    for name, draw in [("Gaussian", lambda size: RNG.standard_normal(size)),
                       ("uniform", lambda size: RNG.uniform(-math.sqrt(3), math.sqrt(3), size))]:
        reps, J, I_ = 4000, 6, 12
        Nmax = cps[I_ - 1]
        fails = 0
        for _ in range(reps):
            z = draw((J, Nmax))
            cs = np.cumsum(z, axis=1)
            miss = False
            for j in range(1, J + 1):
                for i in range(1, I_ + 1):
                    nn = cps[i - 1]
                    dl = alpha / (j * (j + 1) * i * (i + 1))
                    r = sig * math.sqrt(2 * math.log(2 / dl) / nn)
                    if abs(cs[j - 1, nn - 1] / nn) >= r:
                        miss = True
            fails += miss
        freq = fails / reps
        report(f"T5c Theorem 5(i): simultaneous coverage, {name} noise", freq <= alpha,
               f"failure frequency {freq:.4f} over {reps} replications, allowed {alpha}")
    # sub-Gaussian moment generating functions used to place the noise models inside the theory
    t = np.linspace(-12, 12, 4801)
    t = t[np.abs(t) > 1e-9]
    a = math.sqrt(3.0)                                # uniform on [-a, a] has unit variance
    ok = np.all(np.sinh(a * t) / (a * t) <= np.exp(t ** 2 / 2) * (1 + 1e-12))
    ok &= all(math.factorial(2 * k + 1) >= 6 ** k * math.factorial(k) for k in range(0, 80))
    report("T5d uniform noise is sub-Gaussian with variance proxy equal to its variance", ok)


class Instrumented(CTRR):
    """C-TRR with a record of whether each new raw interval contains the truth."""

    def __init__(self, *a, **k):
        self.miss_times = []
        super().__init__(*a, **k)

    def observe(self, h, y):
        a = self.anchors[self.cur]
        i_before = a.i
        super().observe(h, y)
        if a.i > i_before:                      # a checkpoint was processed with index a.i
            dl = self.alpha / (a.j * (a.j + 1) * a.i * (a.i + 1))
            r = self.sig * math.sqrt(2 * math.log(2 / dl) / a.n)
            if not abs(a.s / a.n - float(self.mk.tau(a.x))) < r:
                self.miss_times.append(self.t)


def theorem5_end_to_end(seeds=range(100, 112), T=6000):
    """On runs where the confidence event holds: every adoption improves true profit, and
    every trial quote is within the budget of the incumbent's true profit."""
    mks = standard_markets()
    runs = held = viol_adopt = viol_trial = viol_cum = 0
    failed = []
    jobs = [(name, bud, s) for name in mks for bud in (0.05, 0.10) for s in seeds] + [("m=0.3", 0.05, 125)]
    for name, bud, s in jobs:
        mk = mks[name]
        h0 = mk.stable_point()
        phi0 = float(mk.Phi(h0))
        TT = 12000 if s == 125 else T
        ag = Instrumented(mk, h0, budget=bud * phi0)
        env = Env(mk, seed=s)
        phis, incs = np.empty(TT), np.empty(TT)
        for t in range(TT):
            h = ag.act()
            incs[t] = ag.anchors[ag.inc].x
            ag.observe(h, env.deploy(h))
            phis[t] = float(mk.Phi(h))
        runs += 1
        t_fail = ag.miss_times[0] if ag.miss_times else TT + 1
        if not ag.miss_times:
            held += 1
        else:
            failed.append((name, bud, s, t_fail))
        # check the guarantees on the periods before the first coverage failure
        for (tm, a, b, cert) in ag.moves:
            if tm < t_fail:
                viol_adopt += not float(mk.Phi(b) - mk.Phi(a)) > 0
        ok_t = np.arange(1, TT + 1) < t_fail
        short = mk.Phi(incs) - phis
        viol_trial += int(np.sum(short[ok_t] > ag.ell + 1e-12))
        viol_trial += int(np.sum(phis[ok_t] < phi0 - ag.ell - 1e-12))
        if not ag.miss_times:
            ntrial = int(np.sum(np.abs(phis - mk.Phi(incs)) > 0))
            viol_cum += not phis.sum() >= TT * phi0 - ag.ell * ntrial - 1e-9
    report("T5e Theorem 5(ii): on the confidence event every adoption strictly improves true profit", viol_adopt == 0,
           f"{runs} runs, event held throughout in {held}")
    report("T5f Theorem 5(ii): on the confidence event every deployed quote is within the budget of the incumbent and of the start",
           viol_trial == 0 and viol_cum == 0)
    s125 = [f for f in failed if f[2] == 125]
    report("T5g the one harmful adoption of the main experiment (seed 125) follows a recorded coverage failure",
           len(s125) == 1, f"coverage failures: {failed}")


def prop4():
    bad = 0
    for _ in range(4000):
        sig, dl = RNG.uniform(0.05, 2), RNG.uniform(1e-6, 1.9)
        Dl, m = RNG.uniform(1e-3, 2), RNG.uniform(0, 4)
        nstar = 8 * sig ** 2 * math.log(2 / dl) * m ** 2 / Dl ** 2
        n = nstar * (1 + RNG.uniform(1e-6, 2)) + 1e-12
        bad += not 2 * m * sig * math.sqrt(2 * math.log(2 / dl) / n) < Dl
        # certified gain against the true gain when the bounds are within two radii of the truth
        psi = RNG.uniform(0.1, 0.6)
        c, b = RNG.uniform(psi, 5, 2)
        tc, tb = RNG.uniform(0, 5, 2)
        rc, rb = RNG.uniform(0, 0.5, 2)
        Lc, Ub = tc - RNG.uniform(0, 2) * rc, tb + RNG.uniform(0, 2) * rb
        Kc, Kb = RNG.uniform(-2, 2, 2)
        true = (Kc + (c - psi) * tc) - (Kb + (b - psi) * tb)
        cert = Kc + (c - psi) * Lc - Kb - (b - psi) * Ub
        bad += not cert >= true - 2 * (c - psi) * rc - 2 * (b - psi) * rb - TOL
    report("P4  Proposition 4: certified gain >= true gain - 2(c - psi) r_c - 2(b - psi) r_b; sample-size threshold", bad == 0,
           "4000 draws")


def instance_facts():
    import mpmath as mpm
    mks = standard_markets()
    ref = {"m=0.3": (2.2019, 1.6080, 0.07332), "m=0.6": (2.4065, 1.2964, 0.40191),
           "m=0.8": (2.5456, 1.2054, 0.83206), "m=1.09": (2.7476, 1.1407, 1.87085)}
    bad = 0
    for name, mk in mks.items():
        A, k, w, href, psi, C0, C1, c = (mpm.mpf(v) for v in (mk.A, mk.k, mk.w, mk.href, mk.psi, mk.C0, mk.C1, mk.c))
        Kp = lambda h: A * mpm.e ** (-k * h) * (1 - k * h) - 2 * w * (h - href)
        tau = lambda h: C0 + C1 * mpm.e ** (-c * h)
        dPhi = lambda h: Kp(h) + tau(h) - (h - psi) * c * C1 * mpm.e ** (-c * h)
        hs = mpm.findroot(lambda h: Kp(h) + tau(h), mk.stable_point())
        hpo = mpm.findroot(dPhi, mk.optimum())
        gap = float(mk.Phi(float(hpo)) - mk.Phi(float(hs)))
        bad += not (abs(float(hs) - mk.stable_point()) < 1e-9 and abs(float(hpo) - mk.optimum()) < 1e-6
                    and abs(float(hs) - ref[name][0]) < 5e-5 and abs(float(hpo) - ref[name][1]) < 5e-5
                    and abs(gap - ref[name][2]) < 5e-6)
        # the instance satisfies the standing assumptions on [psi, h0]
        H = np.linspace(mk.psi, mk.h_hi, 4001)
        gmin = 2 * mk.w - mk.A * mk.k * math.exp(-3)
        bad += not (np.all(mk.gamma(H) >= gmin - 1e-12) and np.all(mk.gamma(H) <= 2 * mk.A * mk.k + 2 * mk.w)
                    and np.all(mk.eps(H) >= 0) and np.all(mk.tau2(H) >= 0) and np.all(mk.tau(H) >= 0))
        # exact tangent-response iteration from the stable quote converges to the optimum, monotonically in profit
        b, prev = mk.stable_point(), -np.inf
        for _ in range(400):
            cur = float(mk.Phi(b))
            bad += not cur >= prev - 1e-12
            prev, b = cur, trr_step(mk, b)
        bad += not (abs(b - float(hpo)) < 1e-6 and 0 <= trr_rate(mk, float(hpo)) < 1)
    report("I1  instance: stable quotes, optima and gaps match the values printed in the paper; assumptions hold", bad == 0)
    mk = mks["m=0.6"]
    seq, b = [], mk.stable_point()
    for _ in range(5):
        seq.append(round(b, 4))
        b = trr_step(mk, b)
    report("I2  instance: tangent-response iterates at m = 0.6", seq == [2.4065, 1.8554, 1.6045, 1.4694, 1.3941], str(seq))
    report("I3  instance: local rate of the tangent-response map at the optimum, m = 0.6",
           abs(trr_rate(mk, mk.optimum()) - 0.567) < 5e-4, f"{trr_rate(mk, mk.optimum()):.4f}")
    # blind retraining: stable for m < 1, period-two instability for the strong-feedback market
    out = {}
    for name, mk in mks.items():
        x = mk.stable_point() - 0.05
        for _ in range(200):
            x = mk.best_response(float(mk.tau(x)))
        out[name] = abs(x - mk.stable_point())
    ok = all(out[n] < 1e-6 for n in ("m=0.3", "m=0.6", "m=0.8")) and out["m=1.09"] > 0.05
    report("I4  instance: blind retraining returns to the stable quote iff the modulus is below one", ok,
           ", ".join(f"{k}: {v:.1e}" for k, v in out.items()))
    # tangent_response solves the surrogate problem
    bad = 0
    for name, mk in mks.items():
        for b in np.linspace(mk.psi + 0.05, mk.h_hi - 0.05, 25):
            tb, sl = float(mk.tau(b)), -float(mk.eps(b))
            x = tangent_response(mk, b, tb, sl)
            H = np.linspace(mk.psi, mk.h_hi, 40001)
            S = mk.K(H) + (H - mk.psi) * (tb + sl * (H - b))
            bad += not abs(H[int(np.argmax(S))] - x) < 2e-4
    report("I5  code: tangent_response returns the maximizer of the surrogate", bad == 0)


def main():
    symbolic()
    lemma1()
    prop1()
    lemma2_theorem1()
    theorem2()
    prop2()
    theorem3()
    prop3()
    theorem4()
    theorem5_probability()
    theorem5_end_to_end()
    prop4()
    instance_facts()
    nfail = sum(1 for _, ok in RESULTS if not ok)
    print(f"\n{len(RESULTS) - nfail} of {len(RESULTS)} checks passed")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
