"""Baselines.  All price on the same arms (a lattice around the starting rate) and decide in batches of B quotes.

  stay       keep the starting rate b0
  etc        explore all arms round-robin for a fraction of the horizon, then commit to the best estimate
  ucb        UCB on profit per quote with a Hoeffding bound on take-up at exploration level log t (index
             margin * min(1, mean + sqrt(log t / (2 n))); half the exploration term of UCB1)
  klucb      KL-UCB (Garivier and Cappe, 2011): the same index with the upper confidence bound on take-up taken
             from the Bernoulli relative entropy at exploration level log t, the kind of interval the certified
             search uses
  cucb       conservative UCB (Wu, Shariff, Lattimore and Szepesvari, 2016) with the known profit of b0 as the
             baseline: an arm other than b0 is played only if a lower bound on cumulative profit stays above
             (1 - beta) times the profit of always quoting b0
  ts         Thompson sampling with a logistic take-up model and a Laplace posterior (a parametric model,
             misspecified for the HMDA-calibrated curves); a vague prior by default, or a prior centred on a
             fitted model (ts-own: the lender's own-data model of approved applications)
  safe-M,    stage-wise safe UCB: the pilot test of the certified search with the incumbent frozen at the
  safe-eta   starting rate (so every quoted rate is certified to earn at least the share 1 - rho of the starting
             profit), optimism inside that safe set, and no adoption test.  It uses the intervals and the error
             schedule of the certified search.  It keeps the per-quote floor and drops the certificate of
             improvement.
Each returns the served (rate, quotes) blocks and the final rate.
"""
import math

import numpy as np

from .bounds import budget, kl_interval, lattice_index


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60.0, 60.0)))


def arms_around(b0, psi, lo, hi, width=0.75, spacing=0.05):
    g = np.arange(-int(round(width / spacing)), int(round(width / spacing)) + 1)
    a = b0 + spacing * g
    return a[(a > psi + 1e-9) & (a >= lo - 1e-9) & (a <= hi + 1e-9)]


def run_stay(market, b0, T, rng):
    return dict(served=[(b0, T)], final=b0)


def run_etc(market, b0, T, rng, arms, frac=0.2):
    per = max(1, int(frac * T) // len(arms))
    served, means = [], []
    for x in arms:
        means.append(market.draw(rng, x, per) / per)
        served.append((x, per))
    best = float(arms[int(np.argmax((arms - market.psi) * np.array(means)))])
    served.append((best, T - per * len(arms)))
    return dict(served=served, final=best)


def run_ucb(market, b0, T, rng, arms, B):
    psi, K = market.psi, len(arms)
    n, s = np.zeros(K), np.zeros(K)
    served, t = [], 0
    while t < T:
        if (n == 0).any():
            k = int(np.argmax(n == 0))
        else:
            k = int(np.argmax((arms - psi) * np.minimum(1.0, s / n + np.sqrt(math.log(t) / (2 * n)))))
        m = min(B, T - t)
        s[k] += market.draw(rng, arms[k], m)
        n[k] += m
        served.append((float(arms[k]), m))
        t += m
    return dict(served=served, final=float(arms[int(np.argmax(n))]))


def kl_upper(phat, n, level, iters=40):
    """Largest q in [phat, 1] with n * kl(phat, q) <= level, for arrays phat and n (bisection)."""
    lo, hi = phat.astype(float).copy(), np.ones_like(phat, dtype=float)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        mc = np.clip(mid, 1e-15, 1 - 1e-15)
        kl = (np.where(phat > 0, phat * np.log(np.maximum(phat, 1e-300) / mc), 0.0)
              + np.where(phat < 1, (1 - phat) * np.log(np.maximum(1 - phat, 1e-300) / (1 - mc)), 0.0))
        ok = n * kl <= level
        lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
    return hi


def run_klucb(market, b0, T, rng, arms, B):
    psi, K = market.psi, len(arms)
    n, s = np.zeros(K), np.zeros(K)
    served, t = [], 0
    while t < T:
        if (n == 0).any():
            k = int(np.argmax(n == 0))
        else:
            k = int(np.argmax((arms - psi) * kl_upper(s / n, n, math.log(t))))
        m = min(B, T - t)
        s[k] += market.draw(rng, arms[k], m)
        n[k] += m
        served.append((float(arms[k]), m))
        t += m
    return dict(served=served, final=float(arms[int(np.argmax(n))]))


def run_cucb(market, b0, T, rng, arms, B, beta, delta=0.05):
    psi, K = market.psi, len(arms)
    phi0 = float(market.phi(b0))                   # known profit of the baseline rate
    n, s = np.zeros(K), np.zeros(K)
    n_base, served, t = 0, [], 0
    while t < T:
        m = min(B, T - t)
        nn = np.maximum(n, 1)
        rad = np.sqrt(np.log(4 * K * nn ** 2 / delta) / (2 * nn))
        mean = np.where(n > 0, s / nn, 0.0)
        ucb = (arms - psi) * np.where(n > 0, np.minimum(1.0, mean + rad), 1.0)
        lcb = (arms - psi) * np.where(n > 0, np.maximum(0.0, mean - rad), 0.0)
        J = int(np.argmax(ucb))
        if np.sum(n * lcb) + m * lcb[J] + n_base * phi0 >= (1 - beta) * (t + m) * phi0:
            s[J] += market.draw(rng, arms[J], m)
            n[J] += m
            served.append((float(arms[J]), m))
        else:
            n_base += m
            served.append((b0, m))
        t += m
    mean = np.where(n > 0, s / np.maximum(n, 1), 0.0)
    played = n >= max(B, 1)
    final = float(arms[int(np.argmax(np.where(played, (arms - psi) * mean, -np.inf)))]) if played.any() else b0
    if played.any() and (final - psi) * mean[int(np.argmin(np.abs(arms - final)))] < phi0:
        final = b0
    return dict(served=served, final=final)


def safe_gain(X, anchored, L, U, i0, psi, shape, eta=None):
    """Lower bound on Phi(h) - Phi(b0) at every lattice rate h in X (increasing), for every take-up curve of
    the class whose values at the anchored rates lie in [L, U]; b0 = X[i0] is anchored.  The same rules as
    bounds.certified_gain for classes "M" and "eta" (envelope, cut and slope rules), computed in one pass."""
    lo = np.where(anchored, L, 0.0)
    tl = np.maximum.accumulate(lo[::-1])[::-1]                   # a(h) >= L_x for an anchor x >= h
    if shape == "eta":
        v = np.where(anchored, L + eta * X, -np.inf)             # a(h) >= L_x - eta (h - x) for an anchor x <= h
        tl = np.maximum(tl, np.maximum.accumulate(v) - eta * X)
    elif shape != "M":
        raise ValueError(shape)
    tl = np.maximum(tl, 0.0)
    xb, Lb, Ub = X[i0], L[i0], U[i0]
    g = (X - psi) * tl - (xb - psi) * Ub
    g = np.where(X <= xb, np.maximum(g, -(xb - X) * Ub), g)
    if shape == "eta":
        g = np.where(X >= xb, np.maximum(g, (X - xb) * Lb - eta * (X - xb) * (X - psi)), g)
    return g


def run_safe_ucb(market, b0, T, rng, rho=0.1, shape="M", eta=None, step=0.005, alpha=0.05, n0=64, ratio=1.5,
                 gmax=600, refresh=True):
    """Stage-wise safe UCB on the lattice b0 + g * step.  A rate may be quoted only if its certified gain against
    the starting rate is at least -rho (b0 - psi) L_b0 (the pilot test of the certified search with incumbent
    b0); among such rates the one with the largest optimistic profit (h - psi) * min{U_x : x <= h anchored} is
    quoted until its next checkpoint, except that b0 is quoted instead while the optimistic rate sits at the edge
    of the admissible set and has the narrower interval (refresh).  Intervals: relative entropy, at the
    checkpoints and with the error schedule of the certified search, intersected over checkpoints."""
    psi = market.psi
    lo, hi = max(market.lo, psi), market.hi
    G = np.arange(-min(gmax, int(math.floor((b0 - lo) / step + 1e-9))),
                  min(gmax, int(math.floor((hi - b0) / step + 1e-9))) + 1)
    X = b0 + G * step
    keep = X > psi + 1e-9
    G, X = G[keep], X[keep]
    i0 = int(np.nonzero(G == 0)[0][0])
    J = [lattice_index(int(g)) for g in G]
    m = len(X)
    n, k = np.zeros(m, dtype=np.int64), np.zeros(m, dtype=np.int64)
    L, U = np.zeros(m), np.ones(m)
    ci, next_cp = np.zeros(m, dtype=np.int64), np.full(m, n0, dtype=np.int64)
    a_true = market.a(X)                                         # only to record interval misses (a diagnostic)
    served, t, miss = [], 0, False
    while t < T:
        if ci[i0] == 0:
            idx = i0                                             # the starting rate until its first checkpoint
        else:
            anchored = ci > 0
            safe = safe_gain(X, anchored, L, U, i0, psi, shape, eta) >= -rho * (b0 - psi) * L[i0]
            safe[i0] = True
            ub = np.minimum.accumulate(np.where(anchored, U, 1.0))   # monotone: a(h) <= U_x for an anchor x <= h
            idx = int(np.argmax(np.where(safe, (X - psi) * ub, -np.inf)))
            if refresh and idx != i0 and anchored[idx]:
                # Every certificate compares a candidate with b0, so the interval of b0 limits how far the
                # admissible set can grow, and optimism alone stops quoting b0 once it looks worse.  While
                # the optimistic rate is at the edge of the admissible set, quote b0 whenever its interval is
                # the wider of the two.
                adm = np.nonzero(safe)[0]
                if (idx == adm[0] or idx == adm[-1]) and U[i0] - L[i0] > U[idx] - L[idx]:
                    idx = i0
        q = int(min(next_cp[idx] - n[idx], T - t))
        k[idx] += market.draw(rng, X[idx], q)
        n[idx] += q
        t += q
        served.append((float(X[idx]), q))
        if n[idx] == next_cp[idx]:
            lo_, up_ = kl_interval(k[idx] / n[idx], int(n[idx]), budget(alpha, J[idx], int(ci[idx])))
            miss = miss or not (lo_ <= a_true[idx] <= up_)       # the confidence event failed at this checkpoint
            Lc, Uc = max(L[idx], lo_), min(U[idx], up_)
            if Lc <= Uc:                                         # an empty intersection is only possible off the event
                L[idx], U[idx] = Lc, Uc
            ci[idx] += 1
            next_cp[idx] = max(n[idx] + 1, int(math.ceil(next_cp[idx] * ratio)))
    return dict(served=served, final=float(X[int(np.argmax(n))]), ci_miss=bool(miss))


def posterior_mode(X, n, k, pm, pv, th, iters=200, tol=1e-12):
    """Mode of the logistic posterior with a Gaussian prior, by Newton's method with step halving.

    The log posterior is strictly concave, so the damped iteration converges from any start; undamped Newton
    steps can diverge when the prior is weak and an arm has no acceptances.  Progress is measured by the Newton
    decrement d = g' H^{-1} g, the squared length of the Newton step in units of the posterior standard deviation
    of the Laplace approximation.  While d >= 1e-6 a step is halved until the log posterior rises (Armijo rule);
    below that the iteration is in its quadratic phase and takes full steps; it stops when d < tol, that is when
    the mode is located to within 1e-6 posterior standard deviations.  Returns the mode, the negative Hessian
    there, and whether the stopping rule was met."""
    def logpost(v):
        eta = X @ v
        return float(k @ eta - n @ np.logaddexp(0.0, eta) - 0.5 * np.sum((v - pm) ** 2 / pv))

    def newton(v):
        p = sigmoid(X @ v)
        grad = X.T @ (k - n * p) - (v - pm) / pv
        H = (X.T * (n * p * (1 - p))) @ X + np.diag(1.0 / pv)        # negative Hessian, positive definite
        step = np.linalg.solve(H, grad)
        return H, step, float(grad @ step)

    f = logpost(th)
    ok = False
    for _ in range(iters):
        H, step, dec = newton(th)
        if dec < tol:
            ok = True
            break
        if dec < 1e-6:
            th = th + step
            f = logpost(th)
            continue
        lam = 1.0
        while True:
            new = th + lam * step
            fn = logpost(new)
            if fn >= f + 1e-4 * lam * dec or lam < 1e-10:
                break
            lam *= 0.5
        th, f = new, fn
    if not ok:
        H = newton(th)[0]
    return th, H, ok


def run_ts(market, b0, T, rng, arms, B, prior_sd=(3.0, 10.0), prior_mean=(0.0, 0.0)):
    psi, K = market.psi, len(arms)
    z = arms - b0
    n, k = np.zeros(K), np.zeros(K)
    pv = np.array(prior_sd, float) ** 2
    pm = np.array(prior_mean, float)
    th = pm.copy()
    served, t = [], 0
    X = np.column_stack([np.ones(K), z])
    not_converged = 0
    while t < T:
        th, H, ok = posterior_mode(X, n, k, pm, pv, th)
        not_converged += not ok
        cov = np.linalg.inv(H)
        draw = rng.multivariate_normal(th, (cov + cov.T) / 2)
        j = int(np.argmax((arms - psi) * sigmoid(X @ draw)))
        m = min(B, T - t)
        k[j] += market.draw(rng, arms[j], m)
        n[j] += m
        served.append((float(arms[j]), m))
        t += m
    th, H, ok = posterior_mode(X, n, k, pm, pv, th)
    not_converged += not ok
    final = float(arms[int(np.argmax((arms - psi) * sigmoid(X @ th)))])
    return dict(served=served, final=final, ts_not_converged=int(not_converged))
