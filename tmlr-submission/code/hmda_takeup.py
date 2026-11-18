"""Take-up of approved mortgage offers versus the offered rate spread, raw and within comparable borrowers.

Sample: conventional, first-lien, owner-occupied, 30-year fixed, closed-end, conforming home-purchase
applications that were approved: originated (taken up) or approved but not accepted.  Price: rate spread
(APR minus APOR), trimmed to [-3, 5] percentage points.  Controls: lender x LTV bin x DTI bin x loan-amount
quintile x credit-score model (cells).  Within-cell demeaning gives the controlled relationship.  Standard
errors are reported both under independence and clustered by lender, and the slope also gets a wild cluster
bootstrap interval (cluster_inference.py), because a few lenders carry much of the variation.  The per-lender
sums needed to pool state-years with lenders as clusters across files are saved with the results.

Usage: python -I code/hmda_takeup.py data/raw/hmda_XX_YYYY_purchase.csv [...]   -> prints a summary and
writes data/derived/takeup_<state>_<year>.json
"""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cluster_inference import effective_clusters, wild_ci  # noqa: E402


def ltv_bin(x):
    try:
        v = float(x)
    except ValueError:
        return "na"
    return "<=60" if v <= 60 else "60-80" if v <= 80 else "80-90" if v <= 90 else "90-95" if v <= 95 else ">95"


def load(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if not (r["loan_type"] == "1" and r["lien_status"] == "1" and r["occupancy_type"] == "1"
                    and r["loan_term"] == "360" and r["intro_rate_period"] in ("NA", "Exempt", "")
                    and r["open-end_line_of_credit"] == "2" and r["business_or_commercial_purpose"] == "2"
                    and r["reverse_mortgage"] == "2" and r["conforming_loan_limit"] == "C"
                    and r["action_taken"] in ("1", "2")):
                continue
            try:
                rs = float(r["rate_spread"]); amt = float(r["loan_amount"])
            except ValueError:
                continue
            if not -3.0 <= rs <= 5.0:
                continue
            rows.append((1.0 if r["action_taken"] == "1" else 0.0, rs, r["lei"], ltv_bin(r["loan_to_value_ratio"]),
                         r["debt_to_income_ratio"], amt, r["applicant_credit_score_type"]))
    return rows


def analyze(path):
    rows = load(path)
    y = np.array([r[0] for r in rows]); s = np.array([r[1] for r in rows]); amt = np.array([r[5] for r in rows])
    q = np.searchsorted(np.percentile(amt, [20, 40, 60, 80]), amt)
    cell_keys = [f"{r[2]}|{r[3]}|{r[4]}|{qq}|{r[6]}" for r, qq in zip(rows, q)]
    uniq, inv = np.unique(np.array(cell_keys), return_inverse=True)
    cnt = np.bincount(inv); ys = np.bincount(inv, y); ss = np.bincount(inv, s); s2 = np.bincount(inv, s * s)
    var = s2 / cnt - (ss / cnt) ** 2
    ok = (cnt[inv] >= 2) & (var[inv] > 1e-10)
    yr = y - ys[inv] / cnt[inv]; sr = s - ss[inv] / cnt[inv]
    yr, sr, yo = yr[ok], sr[ok], y[ok]
    leis, gid = np.unique(np.array([r[2] for r in rows])[ok], return_inverse=True)   # lender clusters
    raw_slope = np.polyfit(s, y, 1)[0]
    ctl_slope = float(np.sum(yr * sr) / np.sum(sr * sr))
    se_slope = float(np.sqrt(np.sum((yr - ctl_slope * sr) ** 2) / (len(yr) - 1) / np.sum(sr * sr)))
    score = np.bincount(gid, sr * (yr - ctl_slope * sr))               # lender-clustered (sandwich) variance
    se_slope_cl = float(np.sqrt(np.sum(score ** 2)) / np.sum(sr * sr))
    sxx_l, sxy_l, n_l = np.bincount(gid, sr * sr), np.bincount(gid, sr * yr), np.bincount(gid)
    wlo, whi, wp0 = wild_ci(sxx_l, sxy_l)                              # wild cluster bootstrap, null imposed
    top_share, g_eff = effective_clusters(sxx_l)
    # quadratic shape test within cells: regress yr on sr and (sr^2 - cellmean(sr^2))
    sq = sr ** 2
    inv_ok = inv[ok]
    sq_mean = np.bincount(inv_ok, sq, minlength=len(cnt)) / np.maximum(np.bincount(inv_ok, minlength=len(cnt)), 1)
    sqr = sq - sq_mean[inv_ok]
    Xm = np.column_stack([sr, sqr]); beta, *_ = np.linalg.lstsq(Xm, yr, rcond=None)
    res = yr - Xm @ beta; sigma2 = np.sum(res ** 2) / (len(yr) - 2)
    XtXi = np.linalg.inv(Xm.T @ Xm)
    cov = sigma2 * XtXi
    sc = np.column_stack([np.bincount(gid, Xm[:, 0] * res), np.bincount(gid, Xm[:, 1] * res)])
    cov_cl = XtXi @ (sc.T @ sc) @ XtXi
    # controlled binned curve on the residual spread
    edges = np.percentile(sr, np.linspace(0, 100, 11))
    curve = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (sr >= lo) & (sr <= hi)
        dev = np.bincount(gid[m], yr[m] - yr[m].mean(), minlength=len(leis))   # lender sums of deviations
        curve.append(dict(lo=float(lo), hi=float(hi), mid=float(np.median(sr[m])), n=int(m.sum()),
                          takeup=float(yo.mean() + yr[m].mean()), se=float(yr[m].std() / np.sqrt(m.sum())),
                          se_cluster=float(np.sqrt(np.sum(dev ** 2)) / m.sum())))
    out = dict(file=os.path.basename(path), n=int(len(y)), n_within=int(ok.sum()), cells=int(len(uniq)),
               takeup=float(y.mean()), spread_q=[float(v) for v in np.percentile(s, [10, 50, 90])],
               within_sd=float(sr.std()), raw_slope=float(raw_slope), slope=ctl_slope, slope_se=se_slope,
               quad=float(beta[1]), quad_se=float(np.sqrt(cov[1, 1])), lin=float(beta[0]), curve=curve,
               slope_se_cluster=se_slope_cl, quad_se_cluster=float(np.sqrt(cov_cl[1, 1])),
               lenders=int(gid.max() + 1), slope_wild_ci=[wlo, whi], slope_wild_p0=wp0,
               top_lender_share=top_share, effective_lenders=g_eff,
               lender_sums={str(k): [float(a), float(b), int(c)] for k, a, b, c in zip(leis, sxx_l, sxy_l, n_l)})
    return out


if __name__ == "__main__":
    os.makedirs("data/derived", exist_ok=True)
    for path in sys.argv[1:]:
        o = analyze(path)
        tag = o["file"].replace("hmda_", "").replace("_purchase.csv", "")
        json.dump(o, open(f"data/derived/takeup_{tag}.json", "w"), indent=1)
        print(f"{tag}: n={o['n']} (within-cell {o['n_within']}, {o['cells']} cells); take-up {o['takeup']:.4f}; "
              f"spread p10/50/90 {np.round(o['spread_q'], 2)}; within-cell spread sd {o['within_sd']:.3f}")
        print(f"   slope per pp: raw {o['raw_slope']:+.4f}, controlled {o['slope']:+.4f} (se {o['slope_se']:.4f}, "
              f"lender-clustered {o['slope_se_cluster']:.4f}); quadratic term {o['quad']:+.4f} (se {o['quad_se']:.4f}, "
              f"clustered {o['quad_se_cluster']:.4f}); {o['lenders']} lenders")
        print(f"   wild cluster bootstrap 95% interval [{o['slope_wild_ci'][0]:+.4f}, {o['slope_wild_ci'][1]:+.4f}], "
              f"p(slope = 0) {o['slope_wild_p0']:.3f}; largest lender {100 * o['top_lender_share']:.1f}% of the "
              f"within-cell variation, effective number of lenders {o['effective_lenders']:.1f}")
        print("   controlled curve:", " ".join(f"{c['mid']:+.2f}:{c['takeup']:.3f}" for c in o["curve"]))
