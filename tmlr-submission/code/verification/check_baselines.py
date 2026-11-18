"""Checks of the baseline learners' numerical routines (the certified search has its own checks in verify_math.py).

1. KL-UCB: the upper confidence bound on take-up equals the upper end of the relative-entropy interval used by
   the certified search at the same level.
2. Thompson sampling: the posterior-mode solver (Newton's method with step halving) converges on hard problems
   (weak priors, arms with no acceptances, large samples): one more Newton step from the returned point is
   shorter than 1e-5 posterior standard deviations (checked independently of the solver's own stopping rule);
   since the log posterior is strictly concave, a stationary point is the global maximum.
3. The same problems with undamped Newton steps, to document why step halving is needed.

Usage: python verification/check_baselines.py [--n N]
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lending.baselines import kl_upper, posterior_mode, sigmoid  # noqa: E402
from lending.bounds import kl_interval                            # noqa: E402

RNG = np.random.default_rng(20261117)
N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 2000
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name:72s} {detail}", flush=True)


def problem(rng):
    """Sufficient statistics of a pricing problem with 31 arms: quotes n, acceptances k, and a Gaussian prior."""
    K = 31
    z = np.linspace(-0.75, 0.75, K)
    X = np.column_stack([np.ones(K), z])
    played = rng.random(K) < rng.uniform(0.03, 1.0)
    n = np.where(played, rng.integers(1, 500000, K), 0).astype(float)
    ptrue = sigmoid(rng.normal(0, 4) + rng.normal(0, 10) * z)
    k = rng.binomial(n.astype(int), ptrue).astype(float)
    pm = np.array([rng.normal(0, 3), rng.normal(0, 1)])
    pv = np.array([rng.choice([0.01, 1.0, 9.0, 100.0]), rng.choice([0.0025, 0.25, 25.0, 100.0])])
    return X, n, k, pm, pv


def undamped(X, n, k, pm, pv, th, iters=25):
    for _ in range(iters):
        p = sigmoid(X @ th)
        grad = X.T @ (k - n * p) - (th - pm) / pv
        H = (X.T * (n * p * (1 - p))) @ X + np.diag(1.0 / pv)
        step = np.linalg.solve(H, grad)
        th = th + step
        if np.max(np.abs(step)) < 1e-10:
            return th, True
    return th, False


def main():
    worst = 0.0
    for _ in range(N):
        n = int(RNG.integers(1, 200000))
        ph = int(RNG.integers(0, n + 1)) / n
        lev = float(RNG.uniform(0.05, 20))
        u = float(kl_upper(np.array([ph]), np.array([float(n)]), lev)[0])
        worst = max(worst, abs(u - kl_interval(ph, n, 2 * math.exp(-lev))[1]))
    check("KL-UCB bound equals the upper end of the certified search's interval", worst < 1e-9,
          f"(max difference {worst:.1e}, {N} cases)")

    conv, gap, und_fail = 0, 0.0, 0
    for _ in range(N):
        X, n, k, pm, pv = problem(RNG)
        th, H, ok = posterior_mode(X, n, k, pm, pv, pm.copy())
        p = sigmoid(X @ th)
        g = X.T @ (k - n * p) - (th - pm) / pv
        conv += ok
        gap = max(gap, math.sqrt(max(float(g @ np.linalg.solve(H, g)), 0.0)))   # next Newton step, posterior sd
        th_u, ok_u = undamped(X, n, k, pm, pv, pm.copy())
        und_fail += (not ok_u) or (not np.allclose(th_u, th, atol=1e-6, rtol=1e-6))
    check("Thompson sampling: damped Newton converges on every problem", conv == N, f"({conv} of {N})")
    check("Thompson sampling: returned point is the mode (next step < 1e-5 posterior sd)", gap < 1e-5,
          f"(largest {gap:.1e})")
    print(f"INFO  undamped Newton steps fail on {und_fail} of {N} of the same problems")
    print(f"{sum(RESULTS)} of {len(RESULTS)} checks passed")
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
