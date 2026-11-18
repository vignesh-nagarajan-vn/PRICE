"""Numerical checks of every mathematical statement of the paper on random instances.

Each check names the Lean theorem it mirrors.  The Lean proofs are the real verification; these checks guard
against a mismatch between the statements as proved and the formulas used in the code and the paper (signs,
constants, the direction of an inequality).  Exit status 0 if every check passes.

Usage: python verification/verify_math.py [--n N]
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lending.bounds import budget, certified_gain, kl_interval, klb, radius  # noqa: E402

RNG = np.random.default_rng(20261116)
N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 20000
TOL = 1e-9
RESULTS = []


def check(name, lean, ok, detail=""):
    RESULTS.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name:58s} [{lean}] {detail}", flush=True)


def phi(a, psi, s):
    return (s - psi) * a(s)


def random_decreasing(rng):
    """A random nonincreasing take-up curve with values in (0, 1): a mixture of logistic and exponential."""
    c = rng.uniform(0.2, 1.0)
    mu, sc = rng.uniform(-1, 1), rng.uniform(0.05, 0.6)
    lam, w = rng.uniform(0.2, 4), rng.uniform(0, 1)
    return lambda s: c * (w / (1 + np.exp((np.asarray(s, float) - mu) / sc)) + (1 - w) * np.exp(-lam * np.maximum(np.asarray(s, float) + 2, 0)))


def random_convex_decreasing(rng):
    k = rng.integers(1, 4)
    kinks = rng.uniform(-1.5, 1.5, k)
    slopes = rng.uniform(0.05, 0.6, k)
    base = rng.uniform(0.0, 0.3)
    lam = rng.uniform(0.1, 2.0)
    def a(s):
        s = np.asarray(s, float)
        v = base + 0.3 * np.exp(-lam * (s + 2))
        for x, m in zip(kinks, slopes):
            v = v + m * np.maximum(x - s, 0.0)
        return v
    return a


# ---------------------------------------------------------------- results on take-up and profit
def check_flatter_slope():
    bad = 0
    tested = 0
    for _ in range(N // 10):
        a = random_decreasing(RNG)
        psi = RNG.uniform(-1.5, -0.5)
        b = RNG.uniform(psi + 0.05, 1.0)
        e = 1e-6
        ab = float(a(b))
        ap = float((a(b + e) - a(b - e)) / (2 * e))
        mp = -ab / (b - psi)                      # the model's slope that makes b optimal for the model
        if not ap < mp - 1e-6:
            continue                               # hypothesis: the true slope is steeper than the model's
        tested += 1
        h = b - 1e-4
        bad += not phi(a, psi, h) > phi(a, psi, b)
    check("a flatter believed slope prices too high", "flatter_slope_prices_too_high", bad == 0, f"({tested} cases)")


def lin_flow(psi, b, ab):
    return lambda s: np.maximum(ab * ((2 * b - psi) - np.asarray(s, float)) / (b - psi), 0.0)


def check_linflow():
    bad = [0] * 5
    for _ in range(N // 10):
        psi = RNG.uniform(-1, 0)
        b = RNG.uniform(psi + 0.01, 1.5)
        ab = RNG.uniform(0.01, 1)
        f = lin_flow(psi, b, ab)
        s = np.sort(RNG.uniform(psi - 1, 2 * b - psi + 1, 50))
        v = f(s)
        d2 = v[2:] * (s[1:-1] - s[:-2]) - v[1:-1] * (s[2:] - s[:-2]) + v[:-2] * (s[2:] - s[1:-1])
        bad[0] += (d2 < -1e-9).any()                                 # convexity (three-point form)
        bad[1] += (np.diff(v) > 1e-12).any() or (v < 0).any()       # nonincreasing, nonnegative
        bad[2] += abs(float(f(b)) - ab) > 1e-12                      # matches the data at b
        h = RNG.uniform(psi - 1, 2 * b - psi)
        gap = (b - psi) * ab - (h - psi) * float(f(h))
        bad[3] += abs(gap - ab * (h - b) ** 2 / (b - psi)) > 1e-9    # profit gap
        h2 = RNG.uniform(psi - 2, 3 * b)
        bad[4] += (abs(h2 - b) > 1e-6) and not (phi(f, psi, h2) < phi(f, psi, b))   # unique optimum
    check("linear take-up: convex", "linFlow_convexOn", bad[0] == 0)
    check("linear take-up: nonincreasing and nonnegative", "linFlow_antitone, linFlow_nonneg", bad[1] == 0)
    check("linear take-up: agrees with the data at b", "linFlow_at", bad[2] == 0)
    check("linear take-up: profit gap a_b (h - b)^2 / (b - psi)", "linFlow_profit_gap", bad[3] == 0)
    check("linear take-up: b is the unique optimum", "linFlow_strict_max", bad[4] == 0)


def check_capped_classes():
    """Theorem "no certificate" (i) and (ii) and Proposition "convexity with a bound at one is a slope bound"."""
    bad = [0] * 4
    for _ in range(N // 10):
        psi = RNG.uniform(-1, 0)
        b = RNG.uniform(psi + 0.01, 1.5)
        ab = RNG.uniform(0.01, 1.0)
        step = lambda s: np.where(np.asarray(s, float) <= b, ab, 0.0)
        s = np.sort(RNG.uniform(psi - 1, b + 2, 60))
        v = step(s)
        bad[0] += (np.diff(v) > 0).any() or (v < 0).any() or (v > 1).any() or abs(float(step(b)) - ab) > 0
        h = RNG.uniform(psi - 1, b + 2)
        bad[0] += abs(h - b) > 1e-9 and not phi(step, psi, h) < phi(step, psi, b)          # stepTakeUp_strict_max
        abh = RNG.uniform(0.01, 0.5)                                                     # linear curve, a_b <= 1/2
        f = lin_flow(psi, b, abh)
        g = np.linspace(psi, b + 3, 200)
        bad[1] += (f(g) > 2 * abh + 1e-12).any() or (f(g) > 1 + 1e-12).any()           # linFlow_le_two_mul
        # convexity with a cap: random convex curves on [psi, h] with a(psi) <= 1
        k = RNG.integers(1, 4)
        kinks, slopes = RNG.uniform(psi, b + 1, k), RNG.uniform(0, 0.8, k)
        base = RNG.uniform(0, 0.5)
        raw = lambda x, kinks=kinks, slopes=slopes, base=base: base + sum(
            sl * np.maximum(kk - np.asarray(x, float), 0) for kk, sl in zip(kinks, slopes))
        sc = max(1.0, float(raw(psi)))
        a = lambda x, raw=raw, sc=sc: raw(x) / sc
        hh = RNG.uniform(b, b + 1.5)
        lb = (hh - b) * (2 * float(a(b)) - 1) - (1 - float(a(b))) * (hh - b) ** 2 / (b - psi)
        bad[2] += phi(a, psi, hh) - phi(a, psi, b) < lb - 1e-9                          # convex_cap_increase_gain
        # rule (c) with a lower confidence limit, and the slope term of the envelope
        eta = RNG.uniform(0, 3)
        Lb = float(a(b)) - RNG.uniform(0, 0.2)
        if float(a(hh)) >= float(a(b)) - eta * (hh - b):
            bad[3] += phi(a, psi, hh) - phi(a, psi, b) < (hh - b) * Lb - eta * (hh - b) * (hh - psi) - 1e-9
    check("step curve: in the monotone class, b the unique optimum", "no_certificate_monotone", bad[0] == 0)
    check("linear curve at most 2 a_b on [psi, inf), so capped when a_b <= 1/2", "no_certificate_convex_capped",
          bad[1] == 0)
    check("convexity with a(psi) <= 1 bounds the loss of an increase", "convex_cap_increase_gain", bad[2] == 0)
    check("slope rule with a lower confidence limit", "increase_with_slope_bound_lower", bad[3] == 0)


def check_cuts_and_increases():
    bad = [0] * 6
    for _ in range(N):
        a = random_decreasing(RNG)
        psi = RNG.uniform(-1, 0)
        b = RNG.uniform(psi, 1.5)
        h = RNG.uniform(psi, b)
        Ub = float(a(b)) + RNG.uniform(0, 0.3)
        gain = phi(a, psi, h) - phi(a, psi, b)
        bad[0] += gain < -(b - h) * Ub - TOL                                        # rate_cut_loss
        ell = RNG.uniform(0, 0.2)
        hh = b - RNG.uniform(0, ell / Ub)
        if hh >= psi:
            bad[1] += phi(a, psi, hh) - phi(a, psi, b) < -ell - TOL                  # cut_pilot_safe
        f = RNG.uniform(0, 1)
        hf = b - f * (b - psi)
        bad[2] += phi(a, psi, hf) - phi(a, psi, b) < -f * (b - psi) * Ub - TOL      # cut_fraction_loss
        # slope bound: a(h) >= a(b) - eta (h - b) with eta >= sup |a'|
        h2 = RNG.uniform(b, b + 1)
        sgrid = np.linspace(b, h2, 400)
        eta = float(np.max(np.abs(np.diff(a(sgrid)) / np.diff(sgrid)))) * (1 + 1e-6) + 1e-12
        if h2 >= psi and float(a(h2)) >= float(a(b)) - eta * (h2 - b) - 1e-12:
            lb = (h2 - b) * float(a(b)) - eta * (h2 - b) * (h2 - psi)
            bad[3] += phi(a, psi, h2) - phi(a, psi, b) < lb - 1e-9                   # increase_with_slope_bound
        # worst case of an increase: the chord through (b, a_b) and (h, 0), floored at 0
        ab = float(a(b))
        if h2 > b:
            w = lambda s: np.maximum(ab + (0 - ab) / (h2 - b) * (np.asarray(s, float) - b), 0.0)
            ok = abs(float(w(b)) - ab) < 1e-12 and abs(float(w(h2))) < 1e-12
            ok &= abs((phi(w, psi, h2) - phi(w, psi, b)) + (b - psi) * ab) < 1e-9
            bad[4] += not ok                                                          # increase_worst_case
    # adverse selection
    for _ in range(N):
        a = random_decreasing(RNG)
        b = RNG.uniform(-0.5, 1.5)
        h = RNG.uniform(-0.5, 1.5)
        k = RNG.uniform(0, 0.5)
        pb = RNG.uniform(-1, 0)
        ph = pb + k * (h - b) * RNG.uniform(0, 1) if h >= b else pb - RNG.uniform(0, 0.3)
        true_gain = (h - ph) * float(a(h)) - (b - pb) * float(a(b))
        computed = (h - pb) * float(a(h)) - (b - pb) * float(a(b))
        if h <= b:   # psi(h) <= psi(b): the computed gain is a lower bound            adverse_selection_cut
            bad[5] += computed > true_gain + TOL
        else:        # psi(h) <= psi(b) + k (h - b): overstates by at most k (h - b) U_h  adverse_selection_increase
            Uh = float(a(h)) + RNG.uniform(0, 0.2)
            bad[5] += computed - k * (h - b) * Uh > true_gain + TOL
    check("cuts lose at most (b - h) U_b", "rate_cut_loss", bad[0] == 0)
    check("cut pilots within ell / U_b stay within the budget", "cut_pilot_safe", bad[1] == 0)
    check("cutting a fraction f of the margin risks at most f", "cut_fraction_loss", bad[2] == 0)
    check("increase bound under a slope bound", "increase_with_slope_bound", bad[3] == 0)
    check("an increase can lose all profit without a slope bound", "increase_worst_case", bad[4] == 0)
    check("adverse selection: cuts conservative, increases bounded", "adverse_selection_cut/_increase", bad[5] == 0)


def check_psi_monotone():
    bad = 0
    for _ in range(N):
        a = random_decreasing(RNG)
        b = RNG.uniform(-0.5, 1.5)
        h = RNG.uniform(-0.5, b)
        p1 = RNG.uniform(-1.5, 0)
        p2 = p1 + RNG.uniform(0, 1)
        g = lambda p: (h - p) * float(a(h)) - (b - p) * float(a(b))
        bad += g(p2) > g(p1) + TOL
    check("for a cut, the gain is antitone in the break-even spread", "gain_antitone_in_psi", bad == 0)


def check_shopping():
    bad = 0
    for _ in range(N // 20):
        lam = RNG.uniform(0.2, 5)
        c = RNG.uniform(0.1, 1)
        S = lambda s: c * np.exp(-lam * (np.asarray(s, float) + 1))   # convex, nonincreasing, nonnegative
        s = np.linspace(-1, 2, 301)
        for K in range(1, 6):
            v = S(s) ** K
            bad += (np.diff(v, 2) < -1e-12).any() or (np.diff(v) > 1e-15).any()
    check("K competing quotes: S^K convex and nonincreasing", "shopping_takeup_convexOn/_antitoneOn", bad == 0)


def check_concave_interp():
    bad = 0
    for _ in range(N):
        c0, c1, c2 = RNG.uniform(0.5, 1), RNG.uniform(0, 0.5), RNG.uniform(0, 0.5)
        a = lambda s: c0 - c1 * s - c2 * s * s
        x1, x2 = np.sort(RNG.uniform(-1, 1, 2))
        if x2 - x1 < 1e-6:
            continue
        h = RNG.uniform(x1, x2)
        L1, L2 = a(x1) - RNG.uniform(0, 0.1), a(x2) - RNG.uniform(0, 0.1)
        lb = ((x2 - h) * L1 + (h - x1) * L2) / (x2 - x1)
        bad += lb > a(h) + TOL
    check("concave stretch: take-up above the chord of lower bounds", "concave_interp_lower", bad == 0)


# ---------------------------------------------------------------- certificates (closed form vs truth)
def check_certificates():
    bad = {"M": 0, "eta": 0, "C": 0}
    for _ in range(N // 4):
        shape = ["M", "eta", "C"][RNG.integers(0, 3)]
        a = random_convex_decreasing(RNG) if shape == "C" else random_decreasing(RNG)
        psi = RNG.uniform(-2, -1)
        m = int(RNG.integers(1, 6))
        xs = np.sort(RNG.uniform(-1, 1.5, m))
        if m > 1 and np.min(np.diff(xs)) < 1e-3:
            continue
        av = a(xs)
        L = np.maximum(av - RNG.uniform(0, 0.1, m), 0.0)
        U = av + RNG.uniform(0, 0.1, m)
        ib = int(RNG.integers(0, m))
        H = np.linspace(psi, 2.0, 61)
        eta = None
        if shape == "eta":
            g = np.linspace(-3, 3, 6001)
            eta = float(np.max(np.abs(np.diff(a(g)) / np.diff(g)))) * 1.0001
        lb = certified_gain(H, xs, L, U, ib, psi, shape, eta)
        true = phi(a, psi, H) - phi(a, psi, xs[ib])
        bad[shape] += (lb > true + 1e-9).any()
    for k in bad:
        check(f"certified gain is a valid lower bound, class {k}",
              {"M": "direct/envelope_gain, rate_cut_loss", "eta": "increase_with_slope_bound",
               "C": "joint_left_gain, joint_right_gain"}[k], bad[k] == 0)


# ---------------------------------------------------------------- probability
def check_monotone_in_limits():
    """A pilot is tested when it starts.  It keeps passing while it runs because the certified gain plus the
    budget rho (b - psi) L_b never falls when the limits tighten (running intersections only tighten)."""
    bad = {"M": 0, "eta": 0, "C": 0}
    for _ in range(max(200, N // 10)):
        m = int(RNG.integers(2, 7))
        xs = np.sort(RNG.uniform(0.3, 1.5, m))
        if np.min(np.diff(xs)) < 1e-3:
            continue
        psi, ib = float(RNG.uniform(0.0, 0.29)), int(RNG.integers(0, m))
        a = np.sort(RNG.uniform(0.02, 0.98, m))[::-1]
        L, U = np.clip(a - RNG.uniform(0, 0.3, m), 0, 1), np.clip(a + RNG.uniform(0, 0.3, m), 0, 1)
        L2, U2 = L + RNG.uniform(0, 1, m) * (a - L), U - RNG.uniform(0, 1, m) * (U - a)     # tighter, still valid
        H = np.linspace(psi + 1e-3, 1.8, 40)
        eta, rho = float(RNG.uniform(0.1, 4)), float(RNG.uniform(0.01, 0.5))
        for k in bad:
            g1 = certified_gain(H, xs, L, U, ib, psi, k, eta) + rho * (xs[ib] - psi) * L[ib]
            g2 = certified_gain(H, xs, L2, U2, ib, psi, k, eta) + rho * (xs[ib] - psi) * L2[ib]
            bad[k] += int(np.sum(g2 < g1 - TOL))
    check("a pilot that passed its test keeps passing as limits tighten", "paper: text after the anytime theorem",
          sum(bad.values()) == 0)


def log_binom_pmf(n, k, p):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p)


def check_bernoulli():
    bad_mgf = 0
    for _ in range(2000):
        p, t = RNG.uniform(0, 1), RNG.uniform(-5, 5)
        exact = (1 - p) * 1.0 + p * math.exp(t)
        bad_mgf += abs(exact - (1 + (math.exp(t) - 1) * p)) > 1e-9 * max(1, exact)
    check("mgf of a {0,1} variable is 1 + (e^t - 1) p", "mgf_zero_one", bad_mgf == 0)
    bad_pin = 0
    for q in np.linspace(0.0, 1.0, 401):
        for p in np.linspace(0.001, 0.999, 401):
            bad_pin += 2 * (q - p) ** 2 > klb(float(q), float(p)) + 1e-12
    check("Pinsker: 2 (q - p)^2 <= kl(q, p) on a grid of [0,1] x (0,1)", "pinsker_bernoulli", bad_pin == 0)
    bad_sg = 0
    for p in np.linspace(0.001, 0.999, 60):
        for lam in np.linspace(-20, 20, 81):
            lhs = (1 - p) * math.exp(-lam * p) + p * math.exp(lam * (1 - p))
            bad_sg += lhs > math.exp(lam * lam / 8) * (1 + 1e-12)
    check("acceptance indicators are 1/2-sub-Gaussian (Hoeffding's lemma)", "bernoulli_subgaussian", bad_sg == 0)
    bad_up, bad_dev, cases = 0, 0, 0
    for _ in range(600):
        n = int(RNG.integers(1, 400))
        p = float(RNG.uniform(0.005, 0.995))
        pmf = np.array([math.exp(log_binom_pmf(n, k, p)) for k in range(n + 1)])
        ks = np.arange(n + 1)
        for q in np.linspace(p, 1, 7):                              # upper tail at level q in [p, 1]
            tail = pmf[ks >= n * q - 1e-12].sum()
            bad_up += tail > math.exp(-n * klb(q, p)) * (1 + 1e-9) + 1e-15
        for c in (0.5, 1.0, 2.0, 3.0, 5.0, 8.0):                    # two-sided deviation
            prob = pmf[np.array([n * klb(k / n, p) > c for k in ks])].sum()
            bad_dev += prob > 2 * math.exp(-c) * (1 + 1e-9)
            cases += 1
    check("Chernoff tail exp(-n kl(q, p)) for q in [p, 1] (exact binomial)", "chernoff_kl_upper", bad_up == 0)
    check("P(n kl(phat, p) > c) <= 2 exp(-c) (exact binomial)", "kl_deviation", bad_dev == 0, f"({cases} cases)")


def check_schedule_and_radius():
    ok = True
    for alpha in (0.01, 0.05, 0.2, 1.0):
        tot = sum(budget(alpha, j, i) for j in range(400) for i in range(400))
        ok &= tot <= alpha
    check("error budgets sum to at most alpha", "sum_budget_le", ok)
    ok = True
    for _ in range(2000):
        n, d = int(RNG.integers(1, 10**6)), float(10 ** RNG.uniform(-12, math.log10(2)))
        r = radius(n, d)
        ok &= abs(2 * math.exp(-n * r * r / (2 * 0.25)) - d) <= 1e-9 * d
    check("Hoeffding radius gives tail exactly delta", "radius_identity", ok)
    ok = True
    for _ in range(N):
        d = float(10 ** RNG.uniform(-8, -0.5))
        m, D = RNG.uniform(0.01, 3), RNG.uniform(1e-4, 1)
        n = math.floor(2 * math.log(2 / d) * m * m / (D * D)) + 1
        ok &= 2 * m * 0.5 * math.sqrt(2 * math.log(2 / d) / n) < D
    check("detection sample size for Bernoulli outcomes", "detection_bernoulli", ok)
    ok = True
    for _ in range(3000):
        n = int(RNG.integers(1, 20000)); k = int(RNG.integers(0, n + 1)); d = float(10 ** RNG.uniform(-10, -0.5))
        L, U = kl_interval(k / n, n, d)
        g = np.linspace(1e-9, 1 - 1e-9, 4001)
        inside = g[np.array([n * klb(k / n, x) <= math.log(2 / d) for x in g])]
        r = radius(n, d)
        if len(inside):
            ok &= inside.min() >= L - 1e-12 and inside.max() <= U + 1e-12
        ok &= L >= k / n - r - 1e-12 and U <= k / n + r + 1e-12
    check("code's KL interval contains the exact set, inside Hoeffding", "confidence_event_kl (implementation)", ok)


if __name__ == "__main__":
    check_flatter_slope()
    check_linflow()
    check_capped_classes()
    check_cuts_and_increases()
    check_psi_monotone()
    check_shopping()
    check_concave_interp()
    check_certificates()
    check_monotone_in_limits()
    check_bernoulli()
    check_schedule_and_radius()
    print(f"{sum(RESULTS)} of {len(RESULTS)} checks passed")
    sys.exit(0 if all(RESULTS) else 1)
