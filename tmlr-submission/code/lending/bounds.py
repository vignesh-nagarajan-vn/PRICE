"""Confidence intervals and profit certificates.

Error schedule (Lean: CreditCert.budget): delta_{j,i} = alpha / ((j + 1)(j + 2)(i + 1)(i + 2)), j, i >= 0.
Index j belongs to a lattice point (lattice_index), index i to a checkpoint of that point's sample count.
Two interval rules, both proved in Lean:
  "kl"         {p : n kl(phat, p) <= log(2 / delta)}, the relative-entropy interval (confidence_event_kl);
  "hoeffding"  phat +- sigma sqrt(2 log(2 / delta) / n) with sigma = 1/2 (confidence_event_bernoulli).
The first lies inside the second (Pinsker's inequality) and is much shorter when take-up is far from 1/2.

Lower bounds on take-up at rates H >= psi, valid for every curve in a shape class whose values at the
anchors xs lie in [L, U]:
  "M"    nonincreasing, values in [0, 1]                                         (no further assumption)
  "eta"  as M, and a(h) >= a(x) - eta (h - x) whenever x <= h                     (a slope bound)
  "C"    as M, and convex                                                         (a curvature assumption)
certified_gain gives a lower bound on Phi(h) - Phi(b) for the incumbent b = xs[ib]; the Lean theorem behind
each rule is named next to it.
"""
import math

import numpy as np


def radius(n, delta, sigma=0.5):
    return sigma * math.sqrt(2.0 * math.log(2.0 / delta) / n)


def klb(q, p):
    """Relative entropy between Bernoulli laws with means q and p (Lean: CreditCert.klb), 0 log 0 = 0."""
    out = 0.0
    if q > 0.0:
        out += q * math.log(q / p)
    if q < 1.0:
        out += (1.0 - q) * math.log((1.0 - q) / (1.0 - p))
    return out


def kl_interval(phat, n, delta, iters=80):
    """{p : n klb(phat, p) <= log(2 / delta)} (Lean: confidence_event_kl).  klb(phat, .) decreases on (0, phat]
    and increases on [phat, 1), so each end is found by bisection; the returned ends are on the outer side of
    the exact ends, so the returned interval contains the exact one."""
    t = math.log(2.0 / delta) / n
    if phat <= 0.0:
        L = 0.0
    elif phat >= 1.0:
        L = math.exp(-t)                          # klb(1, p) = -log p
        L = math.nextafter(L, 0.0)
    else:
        lo, hi = 0.0, phat                        # klb(phat, lo) > t (lo -> 0 gives +inf), klb(phat, hi) = 0
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            if mid > 0.0 and klb(phat, mid) <= t:
                hi = mid
            else:
                lo = mid
        L = lo
    if phat >= 1.0:
        U = 1.0
    elif phat <= 0.0:
        U = math.nextafter(-math.expm1(-t), 1.0)  # klb(0, p) = -log(1 - p)
    else:
        lo, hi = phat, 1.0
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            if mid < 1.0 and klb(phat, mid) <= t:
                lo = mid
            else:
                hi = mid
        U = hi
    return L, U


def budget(alpha, j, i):
    return alpha / ((j + 1) * (j + 2) * (i + 1) * (i + 2))


def lattice_index(g):
    """Error-schedule index of the lattice point b0 + g * step: g = 0, -1, +1, -2, +2, ... get j = 0, 1, 2, 3, 4, ..."""
    return 0 if g == 0 else 2 * abs(g) - (1 if g < 0 else 0)


def lower_takeup(H, xs, L, U, shape, eta=None):
    H = np.atleast_1d(np.asarray(H, float))
    tl = np.zeros(H.shape)
    for x, lo in zip(xs, L):                      # a(h) >= a(x) >= L for h <= x           (mono_lower)
        tl = np.where(H <= x, np.maximum(tl, lo), tl)
    if shape == "eta":
        for x, lo in zip(xs, L):                  # a(h) >= L - eta (h - x) for h >= x
            tl = np.where(H > x, np.maximum(tl, lo - eta * (H - x)), tl)
    elif shape == "C":
        m = len(xs)
        for p in range(m):
            for q in range(p + 1, m):
                D = xs[q] - xs[p]
                sl = max(L[p] - U[q], 0.0) / D    # chord extended left of xs[p]  (chord_ext_left_interval)
                if sl > 0:
                    tl = np.where(H <= xs[p], np.maximum(tl, L[p] + sl * (xs[p] - H)), tl)
                sr = min(L[q] - U[p], 0.0) / D    # chord extended right of xs[q] (chord_ext_right_interval)
                tl = np.where(H >= xs[q], np.maximum(tl, L[q] + sr * (H - xs[q])), tl)
    elif shape != "M":
        raise ValueError(shape)
    return np.maximum(tl, 0.0)


def certified_gain(H, xs, L, U, ib, psi, shape, eta=None):
    """Lower bound on Phi(h) - Phi(b), b = xs[ib], at rates H >= psi, for every take-up curve of the class
    with a(xs[p]) in [L[p], U[p]] for all p.  xs must be strictly increasing."""
    H = np.atleast_1d(np.asarray(H, float))
    xb, Lb, Ub = xs[ib], L[ib], U[ib]
    g = (H - psi) * lower_takeup(H, xs, L, U, shape, eta) - (xb - psi) * Ub                  # (envelope_gain)
    g = np.where(H <= xb, np.maximum(g, -(xb - H) * Ub), g)                                   # (rate_cut_loss)
    if shape == "eta":
        g = np.where(H >= xb, np.maximum(g, (H - xb) * Lb - eta * (H - xb) * (H - psi)), g)  # (increase_with_slope_bound)
    if shape == "C":
        for p in range(len(xs)):
            if p == ib:
                continue
            D = abs(xs[p] - xb)
            if xs[p] > xb:       # (joint_left_gain): convexity on [h, xs[p]] through b
                cb = (H - psi) * (xs[p] - H) / D - (xb - psi)
                ca = -(H - psi) * (xb - H) / D
                jb = np.where(cb >= 0, cb * Lb, cb * Ub) + ca * U[p]
                g = np.where(H <= xb, np.maximum(g, jb), g)
            else:                # (joint_right_gain): convexity on [xs[p], h] through b
                cb = (H - psi) * (H - xs[p]) / D - (xb - psi)
                ca = -(H - psi) * (H - xb) / D
                jb = np.where(cb >= 0, cb * Lb, cb * Ub) + ca * U[p]
                g = np.where(H >= xb, np.maximum(g, jb), g)
    return g
