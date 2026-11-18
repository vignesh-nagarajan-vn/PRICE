"""Competing offers in HMDA and the take-up curves they imply.

Comparable borrowers form a cell: county x LTV bin x DTI bin x loan-amount quintile x credit-score model,
within one state-year.  A loan's relative spread is its rate spread minus the mean spread of the OTHER
lenders' loans in its cell (so the cell needs at least two lenders).  A lender's markup is the mean relative
spread of its loans; lenders with at least MIN_LOANS such loans are kept.  The volume-weighted distribution F
of markups, smoothed with a Gaussian kernel, is the distribution of competing quotes.

A borrower who holds K competing quotes takes ours at markup s only if s is below all of them, so take-up is
a_K(s) = (1 - F(s))^K.  a_K is convex exactly where (K - 1) f^2 >= (1 - F) f'.  For each state-year and K the
script reports the share of loan volume whose lender faces a convex take-up curve on [m - d, m + d] around
its own markup m (d = 0, 1/8 and 1/4 point), with percentile-bootstrap intervals over lenders (lenders are
resampled with replacement, with the bandwidth held at its full-sample value), under three
versions of F: the lender-level kernel estimate, the same with twice the bandwidth, and a loan-level version
(relative spreads of all loans, not lender means).  The loan-level version overstates quote dispersion
because it keeps unobserved risk differences; the lender-level version understates it because it drops
quote-level noise.

It also calibrates one market per state-year and K for the simulator: the break-even spread psi is set so the
volume-weighted median markup satisfies the first-order condition a + (s - psi) a' = 0.

Usage: python -I code/hmda_offers.py [--out DIR] data/raw/hmda_XX_YYYY_purchase.csv [...]
       -> data/derived/offers_<STATE>_<YEAR>.json
"""
import csv
import json
import math
import os
import sys

import numpy as np

MIN_LOANS = 30
KS = (1, 2, 3)
B_BOOT = 1000
DS = (0.0, 0.125, 0.25)
GRID = 2401
SEED = 20261116


def ltv_bin(x):
    try:
        v = float(x)
    except ValueError:
        return "na"
    return "<=60" if v <= 60 else "60-80" if v <= 80 else "80-90" if v <= 90 else "90-95" if v <= 95 else ">95"


def load(path):
    s, lei, cell, amt = [], [], [], []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if not (r["loan_type"] == "1" and r["lien_status"] == "1" and r["occupancy_type"] == "1"
                    and r["loan_term"] == "360" and r["intro_rate_period"] in ("NA", "Exempt", "")
                    and r["open-end_line_of_credit"] == "2" and r["business_or_commercial_purpose"] == "2"
                    and r["reverse_mortgage"] == "2" and r["conforming_loan_limit"] == "C"
                    and r["action_taken"] in ("1", "2")):
                continue
            try:
                rs = float(r["rate_spread"]); a = float(r["loan_amount"])
            except ValueError:
                continue
            if not -3.0 <= rs <= 5.0:
                continue
            s.append(rs); lei.append(r["lei"]); amt.append(a)
            cell.append(f"{r['county_code']}|{ltv_bin(r['loan_to_value_ratio'])}|{r['debt_to_income_ratio']}|"
                        f"{r['applicant_credit_score_type']}")
    s, amt = np.array(s), np.array(amt)
    q = np.searchsorted(np.percentile(amt, [20, 40, 60, 80]), amt)
    cell = np.char.add(np.array(cell), np.char.add("|", q.astype(str)))
    return s, np.array(lei), cell


def relative_spreads(s, lei, cell):
    """Spread minus the mean spread of the other lenders' loans in the same cell (NaN if there are none)."""
    _, ci = np.unique(cell, return_inverse=True)
    _, li = np.unique(lei, return_inverse=True)
    cl = ci.astype(np.int64) * (li.max() + 1) + li
    _, cli = np.unique(cl, return_inverse=True)
    c_n, c_s = np.bincount(ci), np.bincount(ci, s)
    cl_n, cl_s = np.bincount(cli), np.bincount(cli, s)
    other_n = c_n[ci] - cl_n[cli]
    with np.errstate(invalid="ignore", divide="ignore"):
        rel = np.where(other_n > 0, s - (c_s[ci] - cl_s[cli]) / np.maximum(other_n, 1), np.nan)
    return rel


class Smoothed:
    """Gaussian-kernel smoothing of a weighted sample: F, f and f' in closed form."""

    def __init__(self, x, w, bw=None):
        self.x, self.w = np.asarray(x, float), np.asarray(w, float) / np.sum(w)
        if bw is None:   # Silverman's rule with Kish's effective sample size
            n_eff = 1.0 / np.sum(self.w ** 2)
            mu = np.sum(self.w * self.x)
            sd = math.sqrt(np.sum(self.w * (self.x - mu) ** 2))
            iqr = wquantile(self.x, self.w, 0.75) - wquantile(self.x, self.w, 0.25)
            bw = 0.9 * min(sd, iqr / 1.349) * n_eff ** (-0.2)
        self.bw = float(bw)

    def _z(self, g):
        return (np.asarray(g, float)[:, None] - self.x[None, :]) / self.bw

    def F(self, g):
        z = self._z(g)
        return ncdf(z) @ self.w

    def f(self, g):
        z = self._z(g)
        return (np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi) / self.bw) @ self.w

    def fp(self, g):
        z = self._z(g)
        return (-z * np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi) / self.bw ** 2) @ self.w


_ZT = np.linspace(-9.0, 9.0, 36001)
_PT = np.array([0.5 * (1.0 + math.erf(z / math.sqrt(2.0))) for z in _ZT])


def ncdf(z):
    """Standard normal cdf by interpolation in a table with step 5e-4 (error below 1e-8)."""
    return np.interp(z, _ZT, _PT)


def wquantile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / np.sum(w)
    return float(np.interp(q, c, x[o]))


def convexity_indicator(sm, g, K):
    """Positive multiple of a_K'' at the points g (a_K = (1 - F)^K)."""
    F, f, fp = sm.F(g), sm.f(g), sm.fp(g)
    return (K - 1) * f * f - (1.0 - F) * fp


def sign_changes(ind, tol=1e-9):
    sg = np.sign(np.where(np.abs(ind) <= tol, 0.0, ind))
    sg = sg[sg != 0]
    return int(np.sum(sg[1:] != sg[:-1]))


def convex_shares(sm, grid, mk, wt, tol=1e-9):
    """For each K and d: share of volume whose lender's take-up curve is convex on [m - d, m + d] around its
    markup m.  F, f and f' are evaluated once on the grid; a lender's neighbourhood is checked at the grid
    points inside it (and at the nearest grid point when d = 0)."""
    F, f, fp = sm.F(grid), sm.f(grid), sm.fp(grid)
    out = {}
    for K in KS:
        ok_grid = ((K - 1) * f * f - (1.0 - F) * fp) >= -tol
        bad = np.concatenate([[0], np.cumsum(~ok_grid)])      # prefix counts of non-convex grid points
        for d in DS:
            lo = np.searchsorted(grid, mk - d, side="left")
            hi = np.searchsorted(grid, mk + d, side="right")
            if d == 0:
                lo = np.clip(np.searchsorted(grid, mk), 0, len(grid) - 1)
                hi = lo + 1
            ok = (bad[np.clip(hi, 0, len(grid))] - bad[np.clip(lo, 0, len(grid))]) == 0
            out[(K, d)] = float(np.sum(wt[ok]) / np.sum(wt))
    return out


def implied_slope(sm, K, m50):
    """Take-up of a borrower with K competing quotes and its slope at the markup m50:
    a_K = (1 - F)^K and a_K' = -K (1 - F)^(K - 1) f, in take-up per percentage point."""
    F, f = sm.F(np.array([m50]))[0], sm.f(np.array([m50]))[0]
    return float((1 - F) ** K), float(-K * (1 - F) ** (K - 1) * f)


def calibrate(sm, grid, K, m50):
    """psi from the first-order condition at the median markup; then the global optimum on the grid."""
    F, f = sm.F(np.array([m50]))[0], sm.f(np.array([m50]))[0]
    a, ap = (1 - F) ** K, -K * (1 - F) ** (K - 1) * f
    psi = m50 + a / ap
    G = grid[grid >= psi]
    phi = (G - psi) * (1 - sm.F(G)) ** K
    k = int(np.argmax(phi))
    return dict(psi=float(psi), s_star=float(G[k]), phi_star=float(phi[k]), a_star=float((1 - sm.F(G[k:k + 1])[0]) ** K),
                foc_at_median_is_global=bool(abs(G[k] - m50) <= 2 * (grid[1] - grid[0])))


def analyze(path):
    s, lei, cell = load(path)
    rel = relative_spreads(s, lei, cell)
    ok = np.isfinite(rel)
    rel_ok, lei_ok = rel[ok], lei[ok]
    lu, li = np.unique(lei_ok, return_inverse=True)
    lc = np.bincount(li)
    lm = np.bincount(li, rel_ok) / lc
    keep = lc >= MIN_LOANS
    mk, wt = lm[keep], lc[keep].astype(float)
    sm = Smoothed(mk, wt)
    lo, hi = wquantile(mk, wt, 0.005) - 4 * sm.bw, wquantile(mk, wt, 0.995) + 4 * sm.bw
    grid = np.linspace(lo, hi, GRID)
    w = wt / wt.sum()
    mu = float(np.sum(w * mk))
    out = dict(file=os.path.basename(path), n_loans=int(len(s)), n_rel=int(ok.sum()), lenders=int(keep.sum()),
               loans_in_kept_lenders=int(wt.sum()), bandwidth=sm.bw,
               markup_mean=mu, markup_sd=float(math.sqrt(np.sum(w * (mk - mu) ** 2))),
               markup_q={str(q): wquantile(mk, wt, q / 100) for q in (5, 10, 25, 50, 75, 90, 95)},
               loan_rel_sd=float(np.std(rel_ok)),
               markups=[float(v) for v in mk], weights=[float(v) for v in wt], grid=[lo, hi, GRID])
    m50 = out["markup_q"]["50"]
    # loan-level robustness: kernel on a fine histogram of relative spreads
    edges = np.linspace(np.percentile(rel_ok, 0.5), np.percentile(rel_ok, 99.5), 401)
    hist, _ = np.histogram(rel_ok, bins=edges)
    sm_loan = Smoothed(0.5 * (edges[1:] + edges[:-1]), hist.astype(float))
    rng = np.random.default_rng(SEED)
    lgrid = np.linspace(edges[0], edges[-1], GRID)
    versions = dict(lender=(sm, grid), lender_2bw=(Smoothed(mk, wt, bw=2 * sm.bw), grid), loan=(sm_loan, lgrid))
    est = {v: convex_shares(sv, g, mk, wt) for v, (sv, g) in versions.items()}
    boot = {v: [] for v in versions}
    boot_slope = {K: [] for K in KS}
    for _ in range(B_BOOT):
        idx = rng.integers(0, len(mk), len(mk))
        for v, (sv, g) in versions.items():
            smb = sv if v == "loan" else Smoothed(mk[idx], wt[idx], bw=sv.bw)   # loan-level F is held fixed
            boot[v].append(convex_shares(smb, g, mk[idx], wt[idx]))
            if v == "lender":       # slope of the implied take-up at the resample's own median markup
                m50b = wquantile(mk[idx], wt[idx], 0.5)
                for K in KS:
                    boot_slope[K].append(implied_slope(smb, K, m50b))
    res = {}
    for K in KS:
        r = dict(calibrate(sm, grid, K, m50))
        r["sign_changes"] = {v: sign_changes(convexity_indicator(sv, g, K)) for v, (sv, g) in versions.items()}
        r["convex_share"] = {f"{v}|{d}": [est[v][(K, d)], float(np.percentile([b[(K, d)] for b in boot[v]], 2.5)),
                                          float(np.percentile([b[(K, d)] for b in boot[v]], 97.5))]
                             for v in versions for d in DS}
        a50, s50 = implied_slope(sm, K, m50)
        bs = np.array(boot_slope[K])
        r["takeup_at_median"] = a50
        r["slope_at_median"] = [s50, float(np.percentile(bs[:, 1], 2.5)), float(np.percentile(bs[:, 1], 97.5))]
        semi = bs[:, 1] / bs[:, 0]
        r["semi_elasticity_at_median"] = [s50 / a50, float(np.percentile(semi, 2.5)), float(np.percentile(semi, 97.5))]
        res[str(K)] = r
    out["K"] = res
    out["loan_level_bandwidth"] = sm_loan.bw
    out["bootstrap_resamples"] = B_BOOT
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    out_dir = "data/derived"
    if "--out" in args:                     # optional output directory
        k = args.index("--out")
        out_dir = args[k + 1]
        del args[k:k + 2]
    os.makedirs(out_dir, exist_ok=True)
    for path in args:
        o = analyze(path)
        tag = o["file"].replace("hmda_", "").replace("_purchase.csv", "")
        json.dump(o, open(os.path.join(out_dir, f"offers_{tag}.json"), "w"))
        q = o["markup_q"]
        print(f"{tag}: {o['n_rel']} loans in cells with 2+ lenders; {o['lenders']} lenders with >= {MIN_LOANS} loans "
              f"({o['loans_in_kept_lenders']} loans); markup sd {o['markup_sd']:.3f} pp, p10/50/90 "
              f"{q['10']:+.3f}/{q['50']:+.3f}/{q['90']:+.3f}; bandwidth {o['bandwidth']:.3f}; loan-level sd {o['loan_rel_sd']:.3f}")
        for K, r in o["K"].items():
            cs = r["convex_share"]
            print(f"   K={K}: psi {r['psi']:+.3f}, s* {r['s_star']:+.3f} (median is global opt: {r['foc_at_median_is_global']}), "
                  f"a(s*) {r['a_star']:.3f}, Phi* {r['phi_star']:.4f}; sign changes {r['sign_changes']}; "
                  f"slope at median {r['slope_at_median'][0]:+.3f} ({r['slope_at_median'][1]:+.3f} to {r['slope_at_median'][2]:+.3f}) per pp")
            for v in ("lender", "lender_2bw", "loan"):
                print(f"      convex near own markup [{v}]: " + "; ".join(
                    f"d={d}: {cs[f'{v}|{d}'][0]:.2f} ({cs[f'{v}|{d}'][1]:.2f}-{cs[f'{v}|{d}'][2]:.2f})" for d in DS))
