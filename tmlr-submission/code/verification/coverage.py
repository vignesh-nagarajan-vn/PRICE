"""Adversarial test of the confidence event (Lean: confidence_event_kl and confidence_event_bernoulli).

Claim: whatever adaptive rule decides which rate to sample next and when to open a new one, with probability
at least 1 - alpha every checkpoint of every rate satisfies
    relative-entropy rule:  N_i kl(phat, p_j) <= log(2 / delta_{j,i})
    Hoeffding rule:         |phat - p_j| <= (1/2) sqrt(2 log(2 / delta_{j,i}) / N_i)
with delta_{j,i} = alpha / ((j+1)(j+2)(i+1)(i+2)), the schedule used by lending/agent.py.  The script plays
three adaptive adversaries against these events with acceptance indicators whose rates p_j cycle through
P_CYCLE (from near 1/2, where Hoeffding is tight, to 1%, where it is loose), and reports the fraction of
replications with any violation, with an exact (Clopper-Pearson) 95% interval.  Every cell (rule x adversary)
uses its own random seeds, so the cells are independent.

Control: the same relative-entropy interval at level alpha at every look, that is without the error schedule
over rates and checkpoints.  Each such interval is valid for one look at one rate; the control shows what the
schedule is for.  It fails for two reasons that the adversaries combine: many rates and checkpoints are looked
at (many-anchors has no adaptivity at all and isolates this), and sampling continues or stops depending on the
data (the other two).

Adversaries (each has a budget of T samples per replication):
  chase-low      keep sampling the current rate while its running mean is below p; open a new rate as soon as
                 it is not (optional continuation on the sign of the error)
  many-anchors   sample each rate exactly to its first checkpoint, then open a new one
  chase-extreme  at each checkpoint continue only if the standardized error is at least 1, else open a new rate

It also checks the implementation: for every checkpoint where the relative-entropy event holds, the interval
returned by lending.bounds.kl_interval contains p_j.

Usage: python verification/coverage.py [--reps R] [--budget T] [--procs P]
"""
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lending.bounds import budget, kl_interval, klb  # noqa: E402

ALPHA, N0, RHO = 0.05, 64, 1.5
P_CYCLE = (0.5, 0.2, 0.05, 0.01)


def checkpoints(T):
    cps, n = [], N0
    while n <= T:
        cps.append(n)
        n = max(n + 1, int(math.ceil(n * RHO)))
    return cps


def violated(rule, j, i, n, k, p, impl_check):
    ph = k / n
    dl = budget(ALPHA, j, i)
    if rule == "kl":
        bad = n * klb(ph, p) > math.log(2 / dl)
        if impl_check and not bad:
            L, U = kl_interval(ph, n, dl)
            if not (L <= p <= U):
                raise AssertionError(f"kl_interval misses p: n={n} k={k} p={p} delta={dl} [{L}, {U}]")
        return bad
    if rule == "hoeffding":
        return abs(ph - p) > 0.5 * math.sqrt(2 * math.log(2 / dl) / n)
    return n * klb(ph, p) > math.log(2 / ALPHA)              # control: level alpha at every look, no schedule


def one_rep(args):
    cell, rep, T, adversary, rule, CP = args
    rng = np.random.default_rng([20261117, cell, rep])       # independent streams across cells and replications
    used, j = 0, -1
    impl = rule == "kl" and rep % 20 == 0
    while used < T:
        j += 1
        p = P_CYCLE[j % len(P_CYCLE)]
        left = T - used
        x = (rng.random(left) < p).astype(np.int64)
        S = np.cumsum(x)
        if adversary == "chase-low":
            ok = np.nonzero(S >= p * np.arange(1, left + 1))[0]
            stop = int(ok[0]) + 1 if len(ok) else left
        elif adversary == "many-anchors":
            stop = min(N0, left)
        else:
            stop = left
            for n in CP:
                if n > left:
                    break
                if abs(S[n - 1] - n * p) / math.sqrt(n * p * (1 - p)) < 1.0:
                    stop = n
                    break
        for i, n in enumerate(CP):
            if n > stop:
                break
            if violated(rule, j, i, n, int(S[n - 1]), p, impl):
                return 1
        used += stop
    return 0


def binom_cdf(k, n, p):
    """P(Bin(n, p) <= k), summed in logs."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    logs = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p)
            + (n - i) * math.log1p(-p) for i in range(k + 1)]
    m = max(logs)
    return min(1.0, math.exp(m) * sum(math.exp(v - m) for v in logs))


def clopper_pearson(k, n, level=0.95):
    """Exact two-sided interval for a binomial proportion (bisection on the binomial cdf)."""
    a = (1 - level) / 2
    lo, hi = 0.0, 1.0
    if k > 0:                                   # lower limit: P(X >= k | p) = a
        l, u = 0.0, k / n
        for _ in range(100):
            mid = 0.5 * (l + u)
            if 1 - binom_cdf(k - 1, n, mid) < a:
                l = mid
            else:
                u = mid
        lo = l
    if k < n:                                   # upper limit: P(X <= k | p) = a
        l, u = k / n, 1.0
        for _ in range(100):
            mid = 0.5 * (l + u)
            if binom_cdf(k, n, mid) > a:
                l = mid
            else:
                u = mid
        hi = u
    return lo, hi


def main():
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 4000
    T = int(sys.argv[sys.argv.index("--budget") + 1]) if "--budget" in sys.argv else 20000
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 6
    CP = checkpoints(T)
    print(f"alpha = {ALPHA}, n0 = {N0}, rho = {RHO}, rates cycle through {P_CYCLE}, budget T = {T} samples, "
          f"{reps} replications per cell", flush=True)
    ok = True
    cell = 0
    with Pool(procs) as pool:
        for rule in ("kl", "hoeffding", "nosched"):
            for adv in ("chase-low", "many-anchors", "chase-extreme"):
                cell += 1
                fails = sum(pool.map(one_rep, [(cell, s, T, adv, rule, CP) for s in range(reps)], chunksize=50))
                lo, hi = clopper_pearson(fails, reps)
                label = {"kl": "relative entropy (paper)", "hoeffding": "Hoeffding (paper)",
                         "nosched": "no schedule (control)"}[rule]
                verdict = ""
                if rule != "nosched":
                    passed = hi < ALPHA
                    ok &= passed
                    verdict = "PASS" if passed else "FAIL"
                print(f"{label:26s} {adv:14s} failure rate {fails / reps:.4f}  95% CI [{lo:.4f}, {hi:.4f}]  {verdict}",
                      flush=True)
    print("all certified cells below alpha with 95% confidence; kl_interval contained p whenever the event held"
          if ok else "SOME CELL NOT BELOW ALPHA")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
