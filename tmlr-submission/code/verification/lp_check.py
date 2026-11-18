"""Exact check of the certified gain (Theorem "certified gain") for the three shape classes.

For an incumbent b and a candidate h >= psi, the tightest valid lower bound on Phi(h) - Phi(b) over every take-up
curve of a class that lies in the anchors' intervals is the value of a linear program in the curve's values at
the anchors, at b, at h and at the ends of the domain [lo, hi]:
  M    values in [0, 1], nonincreasing
  eta  as M, and v_{k+1} >= v_k - eta (x_{k+1} - x_k) for consecutive points
  C    as M, and slopes between consecutive points nondecreasing (convexity)
Every feasible vector of values extends to a curve of the class on [lo, hi] by linear interpolation, so the LP
value is the exact worst case.  The closed form in lending/bounds.py is valid exactly when it never exceeds the LP
value.  The script checks this on random instances and reports how often the closed form equals the LP value.

Requires scipy.  Usage: python verification/lp_check.py [--instances N]
"""
import os
import sys

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lending.bounds import certified_gain  # noqa: E402

LO, HI, TOL = -1.0, 2.0, 1e-7


def lp_min(xs, L, U, ib, h, psi, shape, eta):
    pts = np.unique(np.concatenate([xs, [h, LO, HI]]))
    P = len(pts)
    idx = {float(x): k for k, x in enumerate(pts)}
    c = np.zeros(P)
    c[idx[float(h)]] += h - psi
    c[idx[float(xs[ib])]] -= xs[ib] - psi
    bounds = [(0.0, 1.0)] * P
    for x, lo, up in zip(xs, L, U):
        bounds[idx[float(x)]] = (max(lo, 0.0), min(up, 1.0))
    rows, rhs = [], []
    d = np.diff(pts)
    for k in range(P - 1):                         # nonincreasing: v_{k+1} - v_k <= 0
        r = np.zeros(P); r[k + 1], r[k] = 1.0, -1.0
        rows.append(r); rhs.append(0.0)
        if shape == "eta":                         # v_k - v_{k+1} <= eta d_k
            r = np.zeros(P); r[k], r[k + 1] = 1.0, -1.0
            rows.append(r); rhs.append(eta * d[k])
    if shape == "C":
        for k in range(P - 2):                     # (v_{k+1} - v_k)/d_k <= (v_{k+2} - v_{k+1})/d_{k+1}
            r = np.zeros(P)
            r[k + 1] += 1.0 / d[k] + 1.0 / d[k + 1]
            r[k] -= 1.0 / d[k]
            r[k + 2] -= 1.0 / d[k + 1]
            rows.append(r); rhs.append(0.0)
    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=bounds, method="highs")
    if res.status == 2:
        return None                                # intervals inconsistent with the class: no curve fits
    assert res.status == 0, res.message
    return res.fun


def random_instance(rng, shape):
    m = int(rng.integers(1, 6))
    while True:
        xs = np.sort(rng.uniform(LO + 0.1, HI - 0.1, m))
        if m == 1 or np.min(np.diff(xs)) > 0.02:
            break
    # intervals around a curve of the class, so that the instance is feasible
    if shape == "C":
        kinks, slopes = rng.uniform(LO, HI, 3), rng.uniform(0, 0.3, 3)
        base = rng.uniform(0, 0.2)
        raw = lambda s: base + sum(sl * np.maximum(k - s, 0) for k, sl in zip(kinks, slopes))
        scale = max(1.0, float(raw(LO)) / 0.999)            # keep values below 1 without breaking convexity
        f = lambda s: raw(s) / scale
    else:
        mu, sc, c = rng.uniform(LO, HI), rng.uniform(0.05, 0.8), rng.uniform(0.2, 1)
        f = lambda s: c / (1 + np.exp((s - mu) / sc))
    v = f(xs)
    L = np.maximum(v - rng.uniform(0, 0.15, m), 0.0)
    U = np.minimum(v + rng.uniform(0, 0.15, m), 1.0)
    g = np.linspace(LO, HI, 3001)
    eta = float(np.max(np.abs(np.diff(f(g)) / np.diff(g)))) * rng.uniform(1.0, 2.0)
    return xs, L, U, eta


def main():
    n_inst = int(sys.argv[sys.argv.index("--instances") + 1]) if "--instances" in sys.argv else 600
    rng = np.random.default_rng(2026)
    ok = True
    for shape in ("M", "eta", "C"):
        worst, gaps, n_pairs, n_tight, n_infeasible = -np.inf, [], 0, 0, 0
        for _ in range(n_inst):
            xs, L, U, eta = random_instance(rng, shape)
            ib = int(rng.integers(0, len(xs)))
            psi = rng.uniform(LO - 1.0, LO)
            H = np.linspace(max(psi, LO), HI, 25)
            cf = certified_gain(H, xs, L, U, ib, psi, shape, eta if shape == "eta" else None)
            for h, g in zip(H, cf):
                v = lp_min(xs, L, U, ib, h, psi, shape, eta)
                if v is None:
                    n_infeasible += 1
                    continue
                n_pairs += 1
                worst = max(worst, g - v)
                gaps.append(v - g)
                n_tight += abs(v - g) <= 1e-6
        gaps = np.array(gaps)
        passed = worst <= TOL
        ok &= passed
        print(f"class {shape:3s}: {n_pairs} (instance, rate) pairs from {n_inst} instances "
              f"({n_infeasible} infeasible skipped); largest excess of the closed form over the LP optimum "
              f"{worst:.2e} -> {'PASS' if passed else 'FAIL'}; closed form equals the LP optimum in "
              f"{100 * n_tight / n_pairs:.1f}% of pairs; gap median {np.median(gaps):.4f}, "
              f"90th percentile {np.percentile(gaps, 90):.4f}", flush=True)
    print("closed-form certificates valid in every pair" if ok else "SOME CERTIFICATE EXCEEDS THE LP OPTIMUM")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
