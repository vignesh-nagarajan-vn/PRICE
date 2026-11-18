"""Cluster-robust inference for a one-regressor slope from per-cluster sums.

The within-cell regression of take-up on the rate spread has a single regressor after demeaning, so the slope
and its cluster-robust variance depend on the data only through two sums per cluster (lender):
    sxx_l = sum of x^2,   sxy_l = sum of x y      (x, y demeaned within cells; cells are nested in lenders).
The same sums give the wild cluster bootstrap (Cameron, Gelbach and Miller, 2008) exactly: with the null
hypothesis slope = b0 imposed and Rademacher weights w_l by lender, the bootstrap slope is
    b* = b0 + sum_l w_l u_l / Sxx,   u_l = sxy_l - b0 sxx_l,
and its cluster scores are w_l u_l - (b* - b0) sxx_l.  A confidence interval is the set of b0 that the
bootstrap t-test does not reject.  This matters here because a few lenders carry much of the variation, so the
usual normal approximation with one cluster per lender can be too narrow.
"""
import numpy as np


def slope(sxx, sxy):
    """Slope and its lender-clustered (sandwich) standard error."""
    Sxx = float(np.sum(sxx))
    b = float(np.sum(sxy)) / Sxx
    u = sxy - b * sxx
    return b, float(np.sqrt(np.sum(u * u))) / Sxx


def effective_clusters(sxx):
    """Share of the regressor's variation in the largest cluster, and the effective number of clusters
    (sum sxx)^2 / sum sxx^2."""
    Sxx = float(np.sum(sxx))
    return float(np.max(sxx)) / Sxx, Sxx * Sxx / float(np.sum(sxx * sxx))


def wild_pvalue(sxx, sxy, b0, W):
    """Two-sided wild cluster bootstrap p-value of slope = b0 (null imposed), for a matrix W of +-1 weights."""
    Sxx = float(np.sum(sxx))
    b, se = slope(sxx, sxy)
    t = (b - b0) / se
    u0 = sxy - b0 * sxx
    d = (W @ u0) / Sxx
    us = W * u0[None, :] - d[:, None] * sxx[None, :]
    ts = d / (np.sqrt(np.sum(us * us, axis=1)) / Sxx)
    return float(np.mean(np.abs(ts) >= abs(t) - 1e-12))


def wild_ci(sxx, sxy, level=0.95, B=9999, seed=20261117):
    """Confidence interval by inverting the wild cluster bootstrap t-test, with common weights for every b0."""
    sxx, sxy = np.asarray(sxx, float), np.asarray(sxy, float)
    W = np.random.default_rng(seed).choice([-1.0, 1.0], size=(B, len(sxx)))
    b, se = slope(sxx, sxy)
    alpha = 1.0 - level

    def bound(sign):
        lo, hi = 0.0, 4.0                       # distance from the estimate, in standard errors
        while wild_pvalue(sxx, sxy, b + sign * hi * se, W) >= alpha and hi < 200:
            lo, hi = hi, 2 * hi
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if wild_pvalue(sxx, sxy, b + sign * mid * se, W) >= alpha:
                lo = mid
            else:
                hi = mid
        return b + sign * hi * se               # the outer end, so the interval is not too short

    return bound(-1.0), bound(+1.0), wild_pvalue(sxx, sxy, 0.0, W)
