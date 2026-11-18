"""Numbers, tables and figures of the paper, computed from the saved results.

    python experiments/report.py [--main results/main.json] [--paper ../paper]

Writes paper/generated/numbers.tex (one macro per quoted number, used in the text as \\num{key}),
paper/generated/tab_*.tex and paper/figures/*.pdf.  Every number in the paper comes from here.
"""
import argparse
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = os.path.dirname(ROOT)
DER = os.path.join(PROJ, "data", "derived")
RES = os.path.join(PROJ, "results")
TAGS = ["CA_2022", "CA_2023", "FL_2022", "FL_2023", "TX_2022", "TX_2023"]
TAGNAME = {t: t.replace("_", " ") for t in TAGS}
METHODS = ["cert-M", "cert-eta", "cert-C", "safe-M", "safe-eta", "stay", "etc", "ucb", "klucb", "cucb", "ts", "ts-own"]
LEARNERS = ("etc", "ucb", "klucb", "cucb", "ts", "ts-own")      # baselines that change the rate
MNAME = {"cert-M": r"Certified, $\Mc$", "cert-eta": r"Certified, $\Meta$", "cert-C": r"Certified, $\Cc$",
         "safe-M": r"Safe UCB, $\Mc$", "safe-eta": r"Safe UCB, $\Meta$",
         "stay": "Keep $b_0$", "etc": "Explore then commit", "ucb": "UCB (Hoeffding)", "klucb": "KL-UCB",
         "cucb": "Conservative UCB",
         "ts": "Thompson, vague prior", "ts-own": "Thompson, own-data prior"}
NUM = {}
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cluster_inference  # noqa: E402


def put(key, val):
    NUM[key] = val


def fmt_int(n):
    return f"{int(round(n)):,}".replace(",", "{,}")


def pct(x, d=1):
    return f"{100 * x:.{d}f}"


def load_runs(path):
    if path.endswith(".jsonl"):
        return [json.loads(l) for l in open(path)]
    return json.load(open(path))["runs"]


# ------------------------------------------------------------------ HMDA: take-up of approved offers
def takeup_section(out):
    """Take-up of approved offers.  Intervals for the within-cell slope are wild cluster bootstrap intervals
    (clusters: lenders), because a few lenders carry much of the within-cell variation; the pooled slope stacks
    the six state-years and clusters by lender across them, since most lenders appear in several."""
    rows, n_tot, tus, bound = [], 0, [], 0.0
    est = [json.load(open(os.path.join(DER, f"takeup_{t}.json"))) for t in TAGS]
    assert all("slope_wild_ci" in d for d in est), "rerun code/hmda_takeup.py (wild cluster bootstrap missing)"
    for t, d in zip(TAGS, est):
        n_tot += d["n"]
        tus.append(d["takeup"])
        lo, hi = d["slope_wild_ci"]
        bound = max(bound, abs(lo), abs(hi))
        put(f"hmda:n:{t}", fmt_int(d["n"]))
        rows.append(f"{TAGNAME[t]} & {fmt_int(d['n'])} & {fmt_int(d['lenders'])} & {pct(d['takeup'])} & "
                    f"{100 * d['raw_slope']:+.2f} & {100 * d['slope']:+.2f} ({100 * d['slope_se_cluster']:.2f}) & "
                    f"{100 * d['quad']:+.2f} ({100 * d['quad_se_cluster']:.2f}) & {d['within_sd']:.2f} \\\\")
    put("hmda:topshare:lo", pct(min(d["top_lender_share"] for d in est), 0) + r"\%")
    put("hmda:topshare:hi", pct(max(d["top_lender_share"] for d in est), 0) + r"\%")
    put("hmda:geff:lo", f"{min(d['effective_lenders'] for d in est):.0f}")
    put("hmda:geff:hi", f"{max(d['effective_lenders'] for d in est):.0f}")
    put("hmda:lenders:lo", fmt_int(min(d["lenders"] for d in est)))
    put("hmda:lenders:hi", fmt_int(max(d["lenders"] for d in est)))
    # pooled slope: one within-cell regression on the stacked sample, lenders as clusters across state-years
    pool = {}
    for d in est:
        for lei, (sxx, sxy, n) in d["lender_sums"].items():
            a = pool.setdefault(lei, [0.0, 0.0, 0])
            a[0] += sxx
            a[1] += sxy
            a[2] += 1
    sxx = np.array([v[0] for v in pool.values()])
    sxy = np.array([v[1] for v in pool.values()])
    pooled, pse = cluster_inference.slope(sxx, sxy)
    plo, phi, pp0 = cluster_inference.wild_ci(sxx, sxy)
    put("hmda:pooled", f"{100 * pooled:+.2f}")
    put("hmda:pooled:se", f"{100 * pse:.2f}")
    put("hmda:pooled:lo", f"{100 * plo:+.2f}")
    put("hmda:pooled:hi", f"{100 * phi:+.2f}")
    put("hmda:pooled:p", f"{pp0:.2f}")
    put("hmda:pooled:lenders", fmt_int(len(pool)))
    put("hmda:pooled:shared", fmt_int(sum(v[2] >= 2 for v in pool.values())))
    put("hmda:pooled:absmax", f"{100 * max(abs(plo), abs(phi)):.1f}")
    assert pp0 >= 0.05 and plo < 0 < phi + 1e-4, "text says the pooled slope is not distinguishable from zero at 5%"
    assert pooled < 0, "text says the pooled slope is negative"
    srows, ratio, ratio_all = [], [], []
    for t, d in zip(TAGS, est):
        of = json.load(open(os.path.join(DER, f"offers_{t}.json")))
        if "slope_at_median" not in of["K"]["1"]:
            srows = None
            break
        lo, hi = d["slope_wild_ci"]
        cells = [f"{100 * d['slope']:+.2f} [{100 * lo:+.2f}, {100 * hi:+.2f}]"]
        for K in ("1", "2", "3"):
            v = of["K"][K]["slope_at_median"]
            cells.append(f"{100 * v[0]:+.0f} [{100 * v[1]:+.0f}, {100 * v[2]:+.0f}]")
        steepest = min(lo, -1e-12)                                              # steepest slope the own-file interval allows
        ratio.append(of["K"]["1"]["slope_at_median"][2] / steepest)
        ratio_all.append(max(of["K"][K]["slope_at_median"][2] for K in ("1", "2", "3")) / steepest)   # end nearest zero
        srows.append(f"{TAGNAME[t]} & " + " & ".join(cells) + r" \\")
    if srows:
        srows.append(r"\midrule")
        srows.append(f"All six, stacked & {100 * pooled:+.2f} [{100 * plo:+.2f}, {100 * phi:+.2f}] & -- & -- & -- " + r"\\")
        tab = [r"\begin{tabular}{lllll}", r"\toprule",
               r" & Approved offers & \multicolumn{3}{c}{Implied by competing offers, at the median lender} \\",
               r"\cmidrule(lr){3-5}",
               r"State-year & (within cell) & $K=1$ & $K=2$ & $K=3$ \\", r"\midrule"] + srows + [r"\bottomrule", r"\end{tabular}"]
        open(os.path.join(out, "tab_slopes.tex"), "w").write("\n".join(tab) + "\n")
        k1 = [json.load(open(os.path.join(DER, f"offers_{t}.json")))["K"]["1"]["slope_at_median"] for t in TAGS]
        put("off:slope:K1:lo", f"{-100 * max(v[0] for v in k1):.0f}")      # smallest and largest magnitude of the estimates
        put("off:slope:K1:hi", f"{-100 * min(v[0] for v in k1):.0f}")
        put("off:slope:K1:cimin", f"{-100 * max(v[2] for v in k1):.0f}")   # smallest magnitude among the CI ends
        put("off:slope:ratio", f"{math.floor(min(ratio) / 10) * 10:.0f}")  # rounded down to a multiple of ten: "about"
        put("off:slope:ratio:all", f"{math.floor(min(ratio_all) / 10) * 10:.0f}")
        assert min(ratio_all) >= 50, "text says the implied slopes are at least fifty times steeper"
    put("hmda:n", fmt_int(n_tot))
    put("hmda:takeup:lo", pct(min(tus)))
    put("hmda:takeup:hi", pct(max(tus)))
    put("hmda:slope:bound", f"{100 * bound:.1f}")
    tab = [r"\begin{tabular}{lrrrrrrr}", r"\toprule",
           r"State-year & Applications & Lenders & Take-up (\%) & Raw slope & Within-cell slope & Quadratic & Spread s.d. \\",
           r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_takeup.tex"), "w").write("\n".join(tab) + "\n")


# ------------------------------------------------------------------ HMDA: competing offers
def offers_section(out):
    rows, sds = [], []
    share = defaultdict(list)
    for t in TAGS:
        d = json.load(open(os.path.join(DER, f"offers_{t}.json")))
        sds.append(d["markup_sd"])
        q = d["markup_q"]
        cells = []
        for K in ("1", "2", "3"):
            cs = d["K"][K]["convex_share"]
            v = cs["lender|0.125"]
            share[(K, "lender", "0.125")].append(v[0])
            share[(K, "loan", "0.125")].append(cs["loan|0.125"][0])
            share[(K, "lender", "0.0")].append(cs["lender|0.0"][0])
            share[(K, "lender", "0.25")].append(cs["lender|0.25"][0])
            cells.append(f"{pct(v[0], 0)} [{pct(v[1], 0)}, {pct(v[2], 0)}] / {pct(cs['loan|0.125'][0], 0)}")
        rows.append(f"{TAGNAME[t]} & {fmt_int(d['lenders'])} & {d['markup_sd']:.2f} & {q['10']:+.2f} & {q['50']:+.2f} & "
                    f"{q['90']:+.2f} & " + " & ".join(cells) + r" \\")
    put("off:sd:lo", f"{min(sds):.2f}")
    put("off:sd:hi", f"{max(sds):.2f}")
    put("off:K1:lender:0125:cimax", pct(max(json.load(open(os.path.join(DER, f"offers_{t}.json")))["K"]["1"]
                                           ["convex_share"]["lender|0.125"][2] for t in TAGS), 0))
    # how concentrated the lender weights are (the bootstrap over lenders is rough when a few dominate)
    conc = [json.load(open(os.path.join(DER, f"offers_{t}.json"))) for t in TAGS]
    if all("weights" in d for d in conc):
        tops = [max(d["weights"]) / sum(d["weights"]) for d in conc]
        neff = [sum(d["weights"]) ** 2 / sum(w * w for w in d["weights"]) for d in conc]
        put("off:topshare:lo", pct(min(tops), 0) + r"\%")
        put("off:topshare:hi", pct(max(tops), 0) + r"\%")
        put("off:neff:lo", f"{min(neff):.0f}")
        put("off:neff:hi", f"{max(neff):.0f}")
        put("off:toploans:lo", fmt_int(min(max(d["weights"]) for d in conc)))
        put("off:toploans:hi", fmt_int(max(max(d["weights"]) for d in conc)))
    # facts stated in prose about the convexity shares and the calibration: fail loudly if the data change them
    for t in TAGS:
        d = json.load(open(os.path.join(DER, f"offers_{t}.json")))
        assert d.get("bootstrap_resamples") == 1000, f"{t}: text says 1,000 bootstrap resamples"
        # every version of the K = 1 estimate leaves most of the volume outside the convex region (text)
        for ver in ("lender|0.125", "loan|0.125", "lender_2bw|0.125"):
            if ver in d["K"]["1"]["convex_share"]:
                assert d["K"]["1"]["convex_share"][ver][0] < 0.5, f"{t}: K=1 convex share ({ver}) is not a minority"
        assert d["K"]["2"]["convex_share"]["loan|0.125"][0] > 0.5 and d["K"]["3"]["convex_share"]["loan|0.125"][0] > 0.5, \
            f"{t}: loan-level K>=2 shares are not a majority"
        assert 0.60 <= 1 - d["K"]["1"]["convex_share"]["loan|0.125"][0] <= 0.75, f"{t}: loan-level K=1 share outside 'about two thirds'"
        assert all(d["K"][K]["foc_at_median_is_global"] for K in ("1", "2", "3")), f"{t}: median is not the global optimum"
    gaps = [json.load(open(os.path.join(DER, f"offers_{t}.json")))["markup_q"] for t in TAGS]
    gaps = [g["90"] - g["10"] for g in gaps]
    put("off:p1090:lo", f"{min(gaps):.2f}")
    put("off:p1090:hi", f"{max(gaps):.2f}")
    for (K, v, dd), xs in share.items():
        key = f"off:K{K}:{v}:{dd.replace('.', '')}"
        put(key + ":lo", pct(min(xs), 0))
        put(key + ":hi", pct(max(xs), 0))
    tab = [r"\begin{tabular}{lrrrrrlll}", r"\toprule",
           r" & & Markup & \multicolumn{3}{c}{Markup quantiles} & \multicolumn{3}{c}{Volume convex within $\pm\frac18$ point (\%)} \\",
           r"\cmidrule(lr){4-6}\cmidrule(lr){7-9}",
           r"State-year & Lenders & s.d. & 10\% & 50\% & 90\% & $K=1$ & $K=2$ & $K=3$ \\", r"\midrule"] + rows + [
           r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_offers.tex"), "w").write("\n".join(tab) + "\n")
    # calibration
    margins = []
    crow = []
    for t in TAGS:
        d = json.load(open(os.path.join(DER, f"offers_{t}.json")))
        parts = []
        for K in ("1", "2", "3"):
            r = d["K"][K]
            m = r["s_star"] - r["psi"]
            margins.append(m)
            parts.append(f"{r['psi']:+.2f} & {m:.2f} & {pct(r['a_star'], 0)}")
        crow.append(f"{TAGNAME[t]} & " + " & ".join(parts) + r" \\")
    put("cal:margin:lo", f"{min(margins):.2f}")
    put("cal:margin:hi", f"{max(margins):.2f}")
    a3 = [json.load(open(os.path.join(DER, f"offers_{t}.json")))["K"]["3"]["a_star"] for t in TAGS]
    put("cal:K3:takeup:lo", pct(min(a3), 0) + r"\%")
    put("cal:K3:takeup:hi", pct(max(a3), 0) + r"\%")
    tab = [r"\begin{tabular}{lccccccccc}", r"\toprule",
           r" & \multicolumn{3}{c}{$K=1$} & \multicolumn{3}{c}{$K=2$} & \multicolumn{3}{c}{$K=3$} \\",
           r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}",
           r"State-year & $\zeta$ & $m^\star$ & $a(s^\star)$ & $\zeta$ & $m^\star$ & $a(s^\star)$ & $\zeta$ & $m^\star$ & $a(s^\star)$ \\",
           r"\midrule"] + crow + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_calibration.tex"), "w").write("\n".join(tab) + "\n")


def sample_section(out):
    rows = []
    for t in TAGS:
        tk = json.load(open(os.path.join(DER, f"takeup_{t}.json")))
        of = json.load(open(os.path.join(DER, f"offers_{t}.json")))
        raw = os.path.join(PROJ, "data", "raw", f"hmda_{t}_purchase.csv")
        n_raw = None
        if os.path.exists(raw):
            with open(raw, "rb") as fh:
                n_raw = sum(chunk.count(b"\n") for chunk in iter(lambda: fh.read(1 << 24), b"")) - 1
        rows.append(f"{TAGNAME[t]} & {fmt_int(n_raw) if n_raw is not None else '--'} & {fmt_int(tk['n'])} & "
                    f"{fmt_int(tk['n_within'])} & {fmt_int(tk['cells'])} & {fmt_int(of['n_rel'])} & {fmt_int(of['lenders'])} & "
                    f"{fmt_int(of['loans_in_kept_lenders'])} & {of['bandwidth']:.3f} \\\\")
    tab = [r"\begin{tabular}{lrrrrrrrr}", r"\toprule",
           r" & Downloaded & \multicolumn{3}{c}{Take-up analysis} & \multicolumn{4}{c}{Competing-offers analysis} \\",
           r"\cmidrule(lr){3-5}\cmidrule(lr){6-9}",
           r"State-year & records & Sample & In cells & Cells & In multi-lender cells & Lenders & Their loans & Bandwidth \\",
           r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_sample.tex"), "w").write("\n".join(tab) + "\n")
    rows = []
    for K in ("1", "2", "3"):
        for t in TAGS:
            cs = json.load(open(os.path.join(DER, f"offers_{t}.json")))["K"][K]["convex_share"]
            cells = []
            for v in ("lender", "lender_2bw", "loan"):
                for dd in ("0.0", "0.125", "0.25"):
                    cells.append(pct(cs[f"{v}|{dd}"][0], 0))
            rows.append(f"{K} & {TAGNAME[t]} & " + " & ".join(cells) + r" \\")
        rows.append(r"\midrule" if K != "3" else "")
    tab = [r"\begin{tabular}{llrrrrrrrrr}", r"\toprule",
           r" & & \multicolumn{3}{c}{Lender level} & \multicolumn{3}{c}{Twice the bandwidth} & \multicolumn{3}{c}{Loan level} \\",
           r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}\cmidrule(lr){9-11}",
           r"$K$ & State-year & $0$ & $\pm\frac18$ & $\pm\frac14$ & $0$ & $\pm\frac18$ & $\pm\frac14$ & $0$ & $\pm\frac18$ & $\pm\frac14$ \\",
           r"\midrule"] + [r for r in rows if r] + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_offers_robust.tex"), "w").write("\n".join(tab) + "\n")


# ------------------------------------------------------------------ main experiments
def cp_interval(k, n, level=0.95):
    """Exact (Clopper-Pearson) two-sided interval for a binomial proportion k / n, by bisection on the binomial
    distribution function (no normal approximation, so it is valid for k = 0 and other rare counts)."""
    a = (1 - level) / 2

    def cdf(j, pr):                                   # P(X <= j) for X ~ Binomial(n, pr)
        if j < 0:
            return 0.0
        if pr <= 0:
            return 1.0
        if pr >= 1:
            return 1.0 if j >= n else 0.0
        lp, lq = math.log(pr), math.log1p(-pr)
        t = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq
             for i in range(j + 1)]
        m = max(t)
        return min(1.0, math.exp(m) * sum(math.exp(v - m) for v in t))

    lo, hi = 0.0, 1.0
    if k > 0:
        u, v = 0.0, k / n
        for _ in range(80):
            mid = (u + v) / 2
            if 1 - cdf(k - 1, mid) < a:
                u = mid
            else:
                v = mid
        lo = u
    if k < n:
        u, v = k / n, 1.0
        for _ in range(80):
            mid = (u + v) / 2
            if cdf(k, mid) > a:
                u = mid
            else:
                v = mid
        hi = v
    return lo, hi


def strat(rs, field):
    """Mean over runs and its standard error, stratified by cell (market x starting rate): the mean of cell
    means, with variance sum_c s_c^2 / n_c divided by the squared number of cells."""
    cells = defaultdict(list)
    for r in rs:
        cells[(r["tag"], r["K"], r["r"])].append(float(r[field]))
    means = [np.mean(v) for v in cells.values()]
    var = [np.var(v, ddof=1) / len(v) if len(v) > 1 else 0.0 for v in cells.values()]
    return float(np.mean(means)), float(math.sqrt(np.sum(var)) / len(cells))


def holm(pvals):
    """Holm step-down adjusted p-values."""
    order = np.argsort(pvals)
    m, adj, run = len(pvals), [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * pvals[i]))
        adj[i] = run
    return adj


def fmt_p(p):
    return "$<0.001$" if p < 0.001 else f"{p:.3f}"


def mean_ci(x):
    x = np.asarray(x, float)
    return x.mean(), 1.96 * x.std(ddof=1) / math.sqrt(len(x)) if len(x) > 1 else 0.0


def main_section(out, runs):
    by = defaultdict(list)
    for r in runs:
        by[r["method"]].append(r)
    put("main:runs", fmt_int(len(runs)))
    cert = [r for m in ("cert-M", "cert-eta", "cert-C") for r in by[m]]
    put("main:cert:runs", fmt_int(len(cert)))
    for m in METHODS:
        rs = by[m]
        if not rs:
            continue
        k = m.replace("-", "")
        put(f"main:{k}:final", pct(np.mean([r["final_of_opt"] for r in rs]), 0) + r"\%")
        put(f"main:{k}:finalone", pct(np.mean([r["final_of_opt"] for r in rs]), 1) + r"\%")
        put(f"main:{k}:avg", pct(np.mean([r["avg_of_opt"] for r in rs]), 0) + r"\%")
        put(f"main:{k}:over", pct(np.mean([r["over_budget"] for r in rs]), 1) + r"\%")
        put(f"main:{k}:above", pct(np.mean([r["above_start"] for r in rs]), 0) + r"\%")
        if m.startswith("cert"):
            put(f"main:{k}:harm", fmt_int(sum(r["harmful_moves"] for r in rs)))
            put(f"main:{k}:pilotover", fmt_int(sum(r["pilot_over_budget"] for r in rs)))
            put(f"main:{k}:pilots", fmt_int(sum(r["n_pilots"] for r in rs)))
            put(f"main:{k}:moves", fmt_int(sum(r["n_moves"] for r in rs)))
    tsr = [r for m in ("ts", "ts-own") for r in by[m]]
    if tsr:      # Thompson sampling: the posterior-mode solver must have converged at every update of every run
        assert all("ts_not_converged" in r for r in tsr), "Thompson runs predate the damped solver; rerun them"
        assert sum(r["ts_not_converged"] for r in tsr) == 0, "a Thompson posterior-mode update did not converge"
        put("ts:runs", fmt_int(len(tsr)))
    put("main:cert:harm", fmt_int(sum(r["harmful_moves"] for r in cert)))
    put("main:cert:harmruns", fmt_int(sum(r["harmful_moves"] > 0 for r in cert)))
    put("main:certMeta:pilotover", fmt_int(sum(r["pilot_over_budget"] for m in ("cert-M", "cert-eta") for r in by[m])))
    put("main:certMeta:runs", fmt_int(len(by["cert-M"]) + len(by["cert-eta"])))
    put("main:certC:runsover", pct(np.mean([r["pilot_over_budget"] > 0 for r in by["cert-C"]]), 1) + r"\%")
    # facts stated in prose: fail loudly if a rerun changes them
    assert sum(r["harmful_moves"] for r in cert) == 1, "text says exactly one harmful adoption"
    assert sum(r["pilot_over_budget"] for m in ("cert-M", "cert-eta") for r in by[m]) == 0, "text says no pilot over budget"
    assert sum(r["over_budget"] > 0 for m in ("cert-M", "cert-eta") for r in by[m]) == 0, "text says no quote below the floor"
    assert sum(r["pilot_over_budget"] for r in by["cert-C"]) > 0, "text says convex-class pilots exceeded the budget"
    if all("ci_miss" in r for r in cert):
        put("main:cert:cimiss", pct(np.mean([r["ci_miss"] for r in cert]), 2) + r"\%")
        put("main:cert:cimissruns", fmt_int(sum(r["ci_miss"] for r in cert)))
        harm = [r for r in cert if r["harmful_moves"] > 0]
        put("main:cert:harmmiss", "all" if all(r["ci_miss"] for r in harm) else "not all")
        assert all(r["ci_miss"] for r in harm), "text says the harmful adoption followed an interval miss"
    # exact binomial intervals for the rare-event counts quoted in the text.  Runs of different classes with the
    # same seed share their random draws, so the independent unit is the seed (market x start x seed index):
    # an event is counted once per seed if it occurs in any of the classes named.
    def put_cp(key, k, n, d=3):
        lo, hi = cp_interval(k, n)
        put(key + ":lo", pct(lo, d) + r"\%")
        put(key + ":hi", pct(hi, d) + r"\%")

    def seeds_with(methods, pred):
        hit, allseeds = set(), set()
        for m in methods:
            for r in by[m]:
                u = (r["tag"], r["K"], r["r"], r["seed"])
                allseeds.add(u)
                if pred(r):
                    hit.add(u)
        return len(hit), len(allseeds)

    put("main:certC:pilotlossmax", pct(max(r["pilot_loss_max_rel"] for r in by["cert-C"]), 0) + r"\%")
    if by["safe-M"] and by["safe-eta"]:        # the safe UCB baseline: its floor is the quantity "over_budget"
        safe = by["safe-M"] + by["safe-eta"]
        put("main:safe:runs", fmt_int(len(safe)))
        nover = sum(r["over_budget"] > 0 for r in safe)
        put("main:safe:overruns", fmt_int(nover))
        ks, ns = seeds_with(("safe-M", "safe-eta"), lambda r: r["over_budget"] > 0)
        put_cp("main:safe:over:cp", ks, ns)
        put("main:safe:overseeds", str(ks))
        assert all("ci_miss" in r for r in safe), "safe UCB runs predate the interval-miss diagnostic; rerun them"
        # the floor can only be broken off the confidence event: every such run must have an interval miss
        assert all(r["ci_miss"] for r in safe if r["over_budget"] > 0), "safe UCB below the floor without an interval miss"
        km, _ = seeds_with(("safe-M", "safe-eta"), lambda r: r["ci_miss"])
        put("main:safe:cimissseeds", str(km))
        if nover == 0:           # the sentence in the text depends on whether any run broke the floor
            put("main:safe:floor", "in " + fmt_int(len(safe)) + r" runs it made no quote that earned less than "
                r"$(1-\lrel)\Phi(b_0)$ (exact 95\% upper limit " + NUM["main:safe:over:cp:hi"] + " per seed)")
            put("main:safe:floorshort", "kept the same per-quote floor in every run")
        else:
            put("main:safe:floor", "it made a quote that earned less than $(1-\\lrel)\\Phi(b_0)$ in " + fmt_int(nover)
                + " of " + fmt_int(len(safe)) + " runs, which belong to " + str(ks) + (" seed" if ks == 1 else " seeds")
                + r" in which a confidence interval had missed, an event the guarantee allows (exact 95\% interval "
                + "for the probability per seed: " + NUM["main:safe:over:cp:lo"] + " to " + NUM["main:safe:over:cp:hi"] + ")")
            put("main:safe:floorshort", "kept the same per-quote floor except after a confidence interval missed")
    rcode = {-0.5: "m50", -0.25: "m25", 0.0: "0", 0.25: "p25", 0.5: "p50", 1.0: "p100"}
    for m in ("cert-M", "cert-eta", "safe-M", "safe-eta"):       # final and average profit by starting rate
        for r0, code in rcode.items():
            rs0 = [r for r in by[m] if r["r"] == r0]
            if rs0:
                put(f"main:{m.replace('-', '')}:final:{code}", pct(np.mean([r["final_of_opt"] for r in rs0]), 0) + r"\%")
                put(f"main:{m.replace('-', '')}:avg:{code}", pct(np.mean([r["avg_of_opt"] for r in rs0]), 0) + r"\%")
    k, n = seeds_with(("cert-M", "cert-eta"), lambda r: r["pilot_over_budget"] > 0)
    put("main:seeds", fmt_int(n))
    put_cp("main:certMeta:pilotover:cp", k, n)
    k, n = seeds_with(("cert-M", "cert-eta", "cert-C"), lambda r: r["harmful_moves"] > 0)
    put("main:cert:harmseeds", str(k))
    put_cp("main:cert:harm:cp", k, n)
    k, n = seeds_with(("cert-C",), lambda r: r["pilot_over_budget"] > 0)
    put_cp("main:certC:runsover:cp", k, n, 1)
    if all("ci_miss" in r for r in cert):
        k, n = seeds_with(("cert-M", "cert-eta", "cert-C"), lambda r: r["ci_miss"])
        put("main:cert:cimissseeds", fmt_int(k))
        put("main:cert:cimissshare", pct(k / n, 2) + r"\%")
        put_cp("main:cert:cimiss:cp", k, n, 2)
        assert cp_interval(k, n)[1] < 0.05, "interval misses not below alpha"
    # pairwise comparisons of the certified search with each baseline (stratified z-tests, Holm-adjusted)
    tests, rows_d = [], []
    for c in ("cert-M", "cert-eta"):
        for b in (c.replace("cert", "safe"),) + LEARNERS:      # the safe UCB of the same class, then the learners
            if not by[b]:
                continue
            for field in ("avg_of_opt", "final_of_opt"):
                mc, sc = strat(by[c], field)
                mb, sb = strat(by[b], field)
                d, se = mc - mb, sc + sb      # valid under any dependence between the two methods' runs
                pv = math.erfc(abs(d) / se / math.sqrt(2)) if se > 0 else 0.0
                tests.append((c, b, field, d, se, pv))
    adj = holm([t[5] for t in tests])
    for i in range(0, len(tests), 2):
        (c, b, _, d1, se1, _), (_, _, _, d2, se2, _) = tests[i], tests[i + 1]
        rows_d.append(f"{MNAME[c]} & {MNAME[b]} & {100 * d1:+.2f} [{100 * (d1 - 1.96 * se1):+.2f}, {100 * (d1 + 1.96 * se1):+.2f}] & "
                      f"{fmt_p(adj[i])} & {100 * d2:+.2f} [{100 * (d2 - 1.96 * se2):+.2f}, {100 * (d2 + 1.96 * se2):+.2f}] & "
                      f"{fmt_p(adj[i + 1])} \\\\")
        k = f"diff:{c.replace('-', '')}:{b.replace('-', '')}"
        put(k + ":avg", f"{100 * d1:+.1f}")
        put(k + ":final", f"{100 * d2:+.1f}")
    put("diff:tests", str(len(tests)))
    # the same comparison market by market: in how many of the 18 markets (state-year x K) is the certified
    # search's average profit per quote above the baseline's?
    cell = defaultdict(list)
    for r in runs:
        cell[(r["method"], r["tag"], r["K"])].append(r["avg_of_opt"])
    markets = sorted({(t, K) for (_, t, K) in cell})
    put("mk:n", str(len(markets)))
    for c in ("cert-M", "cert-eta"):
        for b in (c.replace("cert", "safe"),) + LEARNERS:
            if not by[b]:
                continue
            won = [(t, K) for (t, K) in markets if np.mean(cell[(c, t, K)]) > np.mean(cell[(b, t, K)])]
            k = f"mk:{c.replace('-', '')}:{b.replace('-', '')}"
            put(k, str(len(won)))
            for K in (1, 2, 3):
                put(f"{k}:K{K}", str(sum(1 for w in won if w[1] == K)))
    # facts stated in prose about the ranking of average profit: fail loudly if a rerun changes them
    if "main:klucb:final" in NUM and "main:ts:final" in NUM:
        assert NUM["main:klucb:final"] == NUM["main:ts:final"], "abstract gives one figure for KL-UCB and Thompson (vague)"
    for c in ("certM", "certeta"):
        for b in ("klucb", "ts"):
            if f"mk:{c}:{b}" in NUM:
                assert NUM[f"mk:{c}:{b}"] == "0", f"text says {b} out-earns the certified search in every market"
        if f"mk:{c}:etc" in NUM:
            assert NUM[f"mk:{c}:etc"] == str(len(markets)), "text says the certified search out-earns explore-then-commit everywhere"
    if "mk:certM:ucb" in NUM:
        assert NUM["mk:certM:ucb"] == NUM["mk:certM:ucb:K3"] == "6", "text says UCB (Hoeffding) loses only with three quotes"
    if by["safe-M"] and by["safe-eta"]:      # text: the safe UCB earns more than the certified search of its class
        for c, sm in (("cert-M", "safe-M"), ("cert-eta", "safe-eta")):
            assert strat(by[sm], "avg_of_opt")[0] > strat(by[c], "avg_of_opt")[0], f"text: {sm} has the higher average profit"
            assert strat(by[sm], "final_of_opt")[0] > strat(by[c], "final_of_opt")[0] - 0.005, f"text: {sm} ends at least as well"
        f = lambda m, r0, fld: np.mean([r[fld] for r in by[m] if r["r"] == r0])
        assert f("safe-M", 1.0, "final_of_opt") > f("cert-M", 1.0, "final_of_opt"), "text: safe UCB ends better from twice the margin"
    # range of the final-rate profit over the learners other than the own-data sampler, and the smallest share
    # of their runs with a quote over budget (quoted in the abstract and introduction)
    gen = [b for b in LEARNERS if b != "ts-own" and by[b]]
    fin = [np.mean([r["final_of_opt"] for r in by[b]]) for b in gen]
    put("learn:final:lo", pct(min(fin), 1) + r"\%")
    put("learn:final:hi", pct(max(fin), 1) + r"\%")
    anyover = [np.mean([r["over_budget"] > 0 for r in by[b]]) for b in gen]
    put("learn:anyover:lo", pct(min(anyover), 0) + r"\%")
    worst = [np.mean([r["worst_loss"] for r in by[b]]) for b in gen]
    put("learn:worst:lo", pct(min(worst), 0) + r"\%")
    put("learn:worst:hi", pct(max(worst), 0) + r"\%")
    quotes_over = [np.mean([r["over_budget"] for r in by[b]]) for b in gen]
    put("learn:over:lo", pct(min(quotes_over), 1) + r"\%")
    put("learn:over:hi", pct(max(quotes_over), 1) + r"\%")
    put("diff:maxp", fmt_p(max(adj)) if tests else "--")
    put("diff:nsig", str(sum(a < 0.05 for a in adj)))
    tab = [r"\begin{tabular}{llrlrl}", r"\toprule",
           r" & & \multicolumn{2}{c}{Average profit} & \multicolumn{2}{c}{Profit of final rate} \\",
           r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}",
           r"Certified search & Baseline & Difference [95\% CI] & $p$ & Difference [95\% CI] & $p$ \\", r"\midrule"] + rows_d + [
           r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_diff.tex"), "w").write("\n".join(tab) + "\n")
    rows = []
    for m in METHODS:
        rs = by[m]
        if not rs:
            continue
        f, fe = strat(rs, "final_of_opt")
        a, ae = strat(rs, "avg_of_opt")
        fe, ae = 1.96 * fe, 1.96 * ae
        o = np.mean([r["over_budget"] for r in rs])
        anyover = np.mean([r["over_budget"] > 0 for r in rs])
        w = np.mean([r["worst_loss"] for r in rs])
        ab = np.mean([r["above_start"] for r in rs])
        harm = f"{sum(r['harmful_moves'] for r in rs)}" if m.startswith("cert") else "--"
        pov = fmt_int(sum(r['pilot_over_budget'] for r in rs)) if m.startswith("cert") else "--"
        rows.append(f"{MNAME[m]} & {pct(f)} $\\pm$ {pct(fe, 2)} & {pct(a)} $\\pm$ {pct(ae, 2)} & {pct(o, 2)} & {pct(anyover, 2 if 0 < anyover < 0.001 else 1 if 0 < anyover < 0.01 else 0)} & "
                    f"{pct(w, 0)} & {pct(ab, 0)} & {harm} & {pov} \\\\")
    tab = [r"\begin{tabular}{lrrrrrrrr}", r"\toprule",
           r" & Final rate & Average & Quotes over & Runs with & Worst & Quotes & Harmful & Pilots over \\",
           r"Method & (\% of opt.) & (\% of opt.) & budget (\%) & any (\%) & loss (\%) & above $b_0$ (\%) & adoptions & budget \\",
           r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_main.tex"), "w").write("\n".join(tab) + "\n")
    # final profit by start, averaged over markets
    starts = sorted(set(r["r"] for r in runs))
    rows = []
    for m in METHODS:
        rs = by[m]
        if not rs:
            continue
        cells = []
        for s in starts:
            v = [r["final_of_opt"] for r in rs if r["r"] == s]
            cells.append(pct(np.mean(v), 0) if v else "--")
        rows.append(f"{MNAME[m]} & " + " & ".join(cells) + r" \\")
    st = [r for r in by["stay"]]
    cells = [pct(np.mean([r["start_of_opt"] for r in st if r["r"] == s]), 0) for s in starts]
    head = " & ".join(f"$r={s:+.2f}$".replace("+0.00", "0") for s in starts)
    tab = [r"\begin{tabular}{l" + "r" * len(starts) + "}", r"\toprule", "Method & " + head + r" \\", r"\midrule",
           r"Starting rate & " + " & ".join(cells) + r" \\", r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_bystart.tex"), "w").write("\n".join(tab) + "\n")
    # by K
    rows = []
    for m in METHODS:
        rs = by[m]
        if not rs:
            continue
        cells = []
        for K in (1, 2, 3):
            v = [r for r in rs if r["K"] == K]
            cells.append(f"{pct(np.mean([r['final_of_opt'] for r in v]), 0)} & {pct(np.mean([r['avg_of_opt'] for r in v]), 0)}")
        rows.append(f"{MNAME[m]} & " + " & ".join(cells) + r" \\")
    tab = [r"\begin{tabular}{lrrrrrr}", r"\toprule",
           r" & \multicolumn{2}{c}{$K=1$} & \multicolumn{2}{c}{$K=2$} & \multicolumn{2}{c}{$K=3$} \\",
           r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}",
           r"Method & Final & Average & Final & Average & Final & Average \\", r"\midrule"] + rows + [
           r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_byK.tex"), "w").write("\n".join(tab) + "\n")


ROBUST = [
    ("budget05", "Budget share $\\lrel=0.05$", ["cert-M", "cert-eta"]),
    ("budget20", "Budget share $\\lrel=0.2$", ["cert-M", "cert-eta"]),
    ("hoeffding", "Hoeffding intervals", ["cert-M", "cert-eta"]),
    ("hist", "50{,}000 quotes of history at $b_0$", ["cert-M", "cert-eta"]),
    ("etahalf", "Slope bound too small ($\\eta=0.5\\max|a'|$)", ["cert-eta"]),
    ("tsown10", "Own-data prior, standard deviations $\\times10$", ["ts-own"]),
    ("tsown100", "Own-data prior, standard deviations $\\times100$", ["ts-own"]),
    ("tsownlevel", "Own-data prior, level matched to take-up at $b_0$", ["ts-own"]),
    ("armsmargin", "Arms scaled to the optimal margin", ["klucb", "ts"]),
]


def robust_section(out, main_runs):
    rows, text = [], []
    base = defaultdict(list)
    for r in main_runs:
        base[r["method"]].append(r)
    def row(label, m, rs):
        f = np.mean([r["final_of_opt"] for r in rs])
        a = np.mean([r["avg_of_opt"] for r in rs])
        o = np.mean([r["over_budget"] for r in rs])
        pov = fmt_int(sum(r["pilot_over_budget"] for r in rs)) if m.startswith("cert") else "--"
        harm = str(sum(r["harmful_moves"] for r in rs)) if m.startswith("cert") else "--"
        return f"{label} & {MNAME[m]} & {fmt_int(len(rs))} & {pct(f)} & {pct(a)} & {pct(o, 2)} & {harm} & {pov} \\\\"
    for m in ("cert-M", "cert-eta", "ts-own", "klucb", "ts"):
        if base[m]:
            rows.append(row("Main setting", m, base[m]))
    rows.append(r"\midrule")
    found = 0
    for key, label, methods in ROBUST:
        path = os.path.join(RES, f"robust_{key}.json")
        if not os.path.exists(path):
            path += ".part.jsonl"
            if not os.path.exists(path):
                continue
        runs = load_runs(path)
        found += 1
        for m in methods:
            rs = [r for r in runs if r["method"] == m]
            if not rs:
                continue
            rows.append(row(label, m, rs))
            if m.startswith("ts"):
                assert all(r.get("ts_not_converged", 1) == 0 for r in rs), f"{key}: a Thompson update did not converge"
            k = f"rob:{key}:{m.replace('-', '')}"
            put(k + ":final", pct(np.mean([r["final_of_opt"] for r in rs]), 0) + r"\%")
            put(k + ":avg", pct(np.mean([r["avg_of_opt"] for r in rs]), 0) + r"\%")
            put(k + ":avgone", pct(np.mean([r["avg_of_opt"] for r in rs]), 1) + r"\%")
            put(k + ":over", pct(np.mean([r["over_budget"] for r in rs]), 1) + r"\%")
            put(k + ":anyover", pct(np.mean([r["over_budget"] > 0 for r in rs]), 0) + r"\%")
            if m.startswith("cert"):
                put(k + ":pilotover", fmt_int(sum(r["pilot_over_budget"] for r in rs)))
                put(k + ":pilots", fmt_int(sum(r["n_pilots"] for r in rs)))
                put(k + ":harm", fmt_int(sum(r["harmful_moves"] for r in rs)))
                put(k + ":runsover", pct(np.mean([r["pilot_over_budget"] > 0 for r in rs]), 0) + r"\%")
                put(k + ":cimiss", fmt_int(sum(r["ci_miss"] for r in rs)))
                put(k + ":pilotlossmax", pct(max(r["pilot_loss_max_rel"] for r in rs), 0) + r"\%")
                harm = [r for r in rs if r["harmful_moves"] > 0]
                assert all(r["ci_miss"] for r in harm), f"{key} {m}: a harmful adoption without an interval miss"
        if any(r["method"].startswith("cert") for r in runs):
            put(f"rob:{key}:harmall", fmt_int(sum(r.get("harmful_moves", 0) for r in runs)))
    # facts stated in the robustness prose about the own-data prior
    if "rob:tsown10:tsown:final" in NUM:
        g = lambda key: float(NUM[key].replace("\\%", ""))
        assert g("rob:tsown10:tsown:final") > 90 and g("rob:tsown100:tsown:final") > 90, "text: a wider prior recovers"
        if "rob:tsownlevel:tsown:final" in NUM:
            assert g("rob:tsownlevel:tsown:final") < 50, "text: a matched level does not rescue the tight prior"
    tab = [r"\begin{tabular}{llrrrrrr}", r"\toprule",
           r"Variant & Method & Runs & Final (\%) & Average (\%) & Quotes over budget (\%) & Harmful adoptions & Pilots over budget \\",
           r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_robust.tex"), "w").write("\n".join(tab) + "\n")
    open(os.path.join(out, "robust.tex"), "w").write(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "robust_text.tex")).read()
                                                   if found else "Robustness runs are pending.\n")


DESIGN = [
    ("ncap50", r"Pilot cap $n_{\max}=50{,}000$"), ("ncap200", r"Pilot cap $n_{\max}=200{,}000$"),
    ("ratio125", r"Checkpoint ratio $1.25$"), ("ratio200", r"Checkpoint ratio $2$"),
    ("step0025", r"Increment $\Delta=0.0025$"), ("step010", r"Increment $\Delta=0.01$"),
    ("n032", r"First checkpoint $n_0=32$"), ("n0128", r"First checkpoint $n_0=128$"),
    ("alpha01", r"Error level $\alpha=0.01$"), ("alpha10", r"Error level $\alpha=0.1$"),
]


def design_section(out, main_runs):
    """Sensitivity of the certified search to its own design parameters (same 30 seeds as the main setting)."""
    def row(label, m, rs):
        f, fe = strat(rs, "final_of_opt")
        a, ae = strat(rs, "avg_of_opt")
        return (f"{label} & {MNAME[m]} & {fmt_int(len(rs))} & {pct(f)} $\\pm$ {pct(1.96 * fe, 2)} & {pct(a)} $\\pm$ {pct(1.96 * ae, 2)} & "
                f"{sum(r['harmful_moves'] for r in rs)} & {sum(r['pilot_over_budget'] for r in rs)} & "
                f"{sum(r['ci_miss'] for r in rs)} \\\\")
    rows, finals, tot = [], {"cert-M": [], "cert-eta": []}, dict(runs=0, over=0, harm=0, miss=0)
    for m in ("cert-M", "cert-eta"):
        rs = [r for r in main_runs if r["method"] == m and r["seed"] % 100 < 30]
        rows.append(row("Main setting", m, rs))
    rows.append(r"\midrule")
    found = 0
    for key, label in DESIGN:
        path = os.path.join(RES, f"design_{key}.json")
        if not os.path.exists(path):
            continue
        found += 1
        runs = load_runs(path)
        for m in ("cert-M", "cert-eta"):
            rs = [r for r in runs if r["method"] == m]
            rows.append(row(label, m, rs))
            finals[m].append(strat(rs, "final_of_opt")[0])
            tot["runs"] += len(rs)
            tot["over"] += sum(r["pilot_over_budget"] for r in rs)
            tot["harm"] += sum(r["harmful_moves"] for r in rs)
            tot["miss"] += sum(r["ci_miss"] for r in rs)
            assert all(r["ci_miss"] for r in rs if r["harmful_moves"] > 0), f"design {key}: harmful adoption without a miss"
    if found:
        put("rob:design:variants", str(found))
        put("rob:design:runs", fmt_int(tot["runs"]))
        put("rob:design:pilotover", fmt_int(tot["over"]))
        put("rob:design:harm", fmt_int(tot["harm"]))
        put("rob:design:cimiss", fmt_int(tot["miss"]))
        for m in finals:
            k = m.replace("-", "")
            put(f"rob:design:{k}:lo", pct(min(finals[m]), 0) + r"\%")
            put(f"rob:design:{k}:hi", pct(max(finals[m]), 0) + r"\%")
        hit, allseeds = set(), set()
        for key, _ in DESIGN:
            path = os.path.join(RES, f"design_{key}.json")
            if os.path.exists(path):
                for r in load_runs(path):
                    u = (r["tag"], r["K"], r["r"], r["seed"])
                    allseeds.add(u)
                    if r["pilot_over_budget"] > 0:
                        hit.add(u)
        lo, hi = cp_interval(len(hit), len(allseeds))
        put("rob:design:seeds", fmt_int(len(allseeds)))
        put("rob:design:pilotover:cp:hi", pct(hi, 3) + r"\%")
    tab = [r"\begin{tabular}{llrrrrrr}", r"\toprule",
           r"Variant & Method & Runs & Final (\%) & Average (\%) & Harmful adoptions & Pilots over budget & Runs with a missed interval \\",
           r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_design.tex"), "w").write("\n".join(tab) + "\n")


# ------------------------------------------------------------------ verification logs and Lean
def safestep_section(out):
    """Lattice step of the safe UCB: four values, 20 seeds each; the main runs use the step with the highest
    average profit summed over the two classes.  Also the version without the rule that re-quotes b0."""
    steps = [("0005", 0.5), ("001", 1.0), ("002", 2.0), ("004", 4.0)]
    rows, avg, data = [], {}, {}
    for key, bp in steps:
        path = os.path.join(RES, f"safe_step{key}.json")
        if not os.path.exists(path):
            return
        runs = load_runs(path)
        data[bp] = runs
        # a quote below the floor is only possible off the confidence event
        assert all(r.get("ci_miss") for r in runs if r["over_budget"] > 0), f"safe_step{key}: floor broken without an interval miss"
        for m in ("safe-M", "safe-eta"):
            rs = [r for r in runs if r["method"] == m]
            f, fe = strat(rs, "final_of_opt")
            a, ae = strat(rs, "avg_of_opt")
            avg[(m, bp)] = a
            rows.append(f"{bp:g} & {MNAME[m]} & {fmt_int(len(rs))} & {pct(f)} $\\pm$ {pct(1.96 * fe, 2)} & "
                        f"{pct(a)} $\\pm$ {pct(1.96 * ae, 2)} & {sum(r['over_budget'] > 0 for r in rs)} \\\\")
        rows.append(r"\midrule")
    rows = rows[:-1]
    best = max((bp for _, bp in steps), key=lambda bp: avg[("safe-M", bp)] + avg[("safe-eta", bp)])
    src = open(os.path.join(ROOT, "experiments", "run_markets.py")).read()
    used = 100 * float(re.search(r"^SAFE_STEP = ([0-9.]+)", src, flags=re.M).group(1))      # basis points
    assert abs(best - used) < 1e-9, f"main runs use a safe UCB step of {used:g} bp, but {best:g} bp has the highest average"
    put("safe:step", "one basis point" if abs(used - 1) < 1e-9 else f"{used:g} basis points")
    tab = [r"\begin{tabular}{llrrrr}", r"\toprule",
           r"Step (basis points) & Method & Runs & Final (\%) & Average (\%) & Runs with a quote over budget \\",
           r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_safestep.tex"), "w").write("\n".join(tab) + "\n")
    path = os.path.join(RES, "safe_norefresh.json")
    if os.path.exists(path):
        f = lambda runs: np.mean([r["final_of_opt"] for r in runs if r["method"] == "safe-M" and r["r"] == 1.0])
        no, yes = f(load_runs(path)), f(data[used])
        put("safe:norefresh:final:p100", pct(no, 0) + r"\%")
        put("safe:refresh:final:p100", pct(yes, 0) + r"\%")
        assert yes > no + 0.1, "text says the admissible set stops growing without the refresh rule"


def adoption_section(out):
    """Quotes until the first certified adoption (experiments/adoption_times.py re-runs the certified runs of
    the main design with the same seeds and records when each adoption happened)."""
    path = os.path.join(RES, "adoption_times.json")
    if not os.path.exists(path):
        return
    d = json.load(open(path))
    assert d["same_as_main"] == d["n"], "the adoption-time rerun must reproduce main.json"
    put("adopt:runs", fmt_int(d["n"]))
    put("adopt:same", fmt_int(d["same_as_main"]))
    by = defaultdict(list)
    for r in d["runs"]:
        by[(r["method"], r["r"], r["K"])].append(r)

    def cell(keys):
        rs = [r for k in keys for r in by[k]]
        first = [r["times"][0] for r in rs if r["times"]]
        return len(first) / len(rs), (float(np.median(first)) if first else None), len(rs)

    rows = []
    for m, starts in (("cert-M", (0.25, 0.5, 1.0)), ("cert-eta", (-0.5, -0.25))):
        for r0 in starts:
            cells = []
            for K in (1, 2, 3):
                sh, med, _ = cell([(m, r0, K)])
                cells.append(f"{pct(sh, 0)} & " + (f"{med / 1000:.0f}" if med is not None else "--"))
            rows.append(f"{MNAME[m]} & ${r0:+.2f}$ & " + " & ".join(cells) + r" \\")
    tab = [r"\begin{tabular}{llrrrrrr}", r"\toprule",
           r" & & \multicolumn{2}{c}{$K=1$} & \multicolumn{2}{c}{$K=2$} & \multicolumn{2}{c}{$K=3$} \\",
           r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}",
           r"Method & Start $r$ & Adopt (\%) & Quotes & Adopt (\%) & Quotes & Adopt (\%) & Quotes \\", r"\midrule"]
    tab += rows + [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_adopt.tex"), "w").write("\n".join(tab) + "\n")
    # prose: overpriced starts (r = 0.5 or 1) with the monotone class, by the number of competing quotes
    for K in (1, 2, 3):
        sh, med, n = cell([("cert-M", 0.5, K), ("cert-M", 1.0, K)])
        put(f"adopt:M:K{K}:share", pct(sh, 0) + r"\%")
        put(f"adopt:M:K{K}:median", f"{med / 1000:.0f}")
        put(f"adopt:M:K{K}:runs", fmt_int(n))
    sh1, _, _ = cell([("cert-M", 0.5, 1), ("cert-M", 1.0, 1)])
    sh2, _, _ = cell([("cert-M", 0.5, 2), ("cert-M", 1.0, 2)])
    assert sh1 == 1.0 and sh2 == 1.0, "text says every such run adopted a lower rate for K = 1 and 2"
    sh3, _, _ = cell([("cert-M", 0.5, 3), ("cert-M", 1.0, 3)])
    assert sh3 < 0.5, "text says fewer than half of such runs adopted a rate for K = 3"


def verification_section():
    def grab(path):
        return open(path).read() if os.path.exists(path) else ""
    vm = grab(os.path.join(RES, "verify_math.log"))
    m = re.search(r"(\d+) of (\d+) checks passed", vm)
    if m:
        put("ver:math:pass", m.group(1))
        put("ver:math:total", m.group(2))
    lp = grab(os.path.join(RES, "lp_check.log"))
    for cls in ("M", "eta", "C"):
        mm = re.search(rf"class {cls}\s*: (\d+) \(instance, rate\) pairs.*?equals the LP optimum in ([\d.]+)%", lp)
        if mm:
            put(f"ver:lp:{cls}:pairs", fmt_int(int(mm.group(1))))
            put(f"ver:lp:{cls}:tight", mm.group(2))
    bl = grab(os.path.join(RES, "check_baselines.log"))
    mm = re.search(r"(\d+) of (\d+) checks passed", bl)
    if mm:
        put("ver:base:pass", mm.group(1))
        put("ver:base:total", mm.group(2))
        assert mm.group(1) == mm.group(2), "a baseline solver check fails"
    mm = re.search(r"undamped Newton steps fail on (\d+) of (\d+)", bl)
    if mm:
        put("ver:base:undamped", fmt_int(int(mm.group(1))))
        put("ver:base:problems", fmt_int(int(mm.group(2))))
    cv = grab(os.path.join(RES, "coverage.log"))
    rates = [float(x) for x in re.findall(r"\(paper\)\s+\S+\s+failure rate ([\d.]+)", cv)]
    if rates:
        put("ver:cov:max", f"{max(rates):.4f}")
    ups = [float(x) for x in re.findall(r"\(paper\)\s+\S+\s+failure rate [\d.]+\s+95% CI \[[\d.]+, ([\d.]+)\]", cv)]
    if ups:
        put("ver:cov:maxupper", f"{max(ups):.4f}")
    ctl = [float(x) for x in re.findall(r"\(control\)\s+\S+\s+failure rate ([\d.]+)", cv)]
    if ctl:
        put("ver:cov:ctl:lo", pct(min(ctl), 0) + r"\%")
        put("ver:cov:ctl:hi", pct(max(ctl), 0) + r"\%")
    mm = re.search(r"\(control\)\s+many-anchors\s+failure rate ([\d.]+)", cv)
    if mm:
        put("ver:cov:ctl:many", pct(float(mm.group(1)), 0) + r"\%")
    mm = re.search(r"(\d+) replications per cell", cv)
    if mm:
        put("ver:cov:reps", fmt_int(int(mm.group(1))))
    second = os.path.join(RES, "determinism_check.json")
    if os.path.exists(second) and os.path.exists(os.path.join(RES, "main.json")):
        old = {(r["tag"], r["K"], r["r"], r["method"], r["seed"]): r for r in json.load(open(second))["runs"]}
        new = {(r["tag"], r["K"], r["r"], r["method"], r["seed"]): r
               for r in json.load(open(os.path.join(RES, "main.json")))["runs"] if r["method"].startswith("cert")}
        skip = {"secs"}
        same = sum(all(old[k][f] == v[f] for f in v if f not in skip and f in old[k]) for k, v in new.items() if k in old)
        put("ver:det:same", fmt_int(same))
        put("ver:det:total", fmt_int(len(new)))
        assert same == len(new) == len(old), f"rerun differs: {same} of {len(new)} identical"
    ax = grab(os.path.join(RES, "lean_axioms.log"))
    mm = re.search(r"theorems checked: (\d+)", ax)
    if mm:
        put("lean:count", mm.group(1))


LEAN_MAP = [
    ("Proposition~\\ref{prop:shape}", ["survival_antitoneOn", "survival_convexOn", "shopping_takeup_convexOn",
                                      "shopping_takeup_antitoneOn", "flow_convexOn", "flow_antitoneOn", "flow_nonneg"]),
    ("Proposition~\\ref{prop:flatter}", ["flatter_slope_prices_too_high", "hasDerivAt_Phi", "eventually_lt_of_deriv_neg"]),
    ("Lemma~\\ref{lem:linear}", ["linFlow_convexOn", "linFlow_antitone", "linFlow_nonneg", "linFlow_at",
                                  "linFlow_profit_gap", "linFlow_strict_max"]),
    ("Theorem~\\ref{thm:nocert}", ["no_certificate_monotone", "stepTakeUp_antitone", "stepTakeUp_mem",
                                  "stepTakeUp_at", "stepTakeUp_strict_max", "no_certificate_convex_capped",
                                  "linFlow_le_two_mul", "no_certificate_single_rate",
                                  "no_certificate_of_matching_curve"]),
    ("Proposition~\\ref{prop:convexcap}", ["convex_cap_increase_gain"]),
    ("Proposition~\\ref{prop:cuts}", ["rate_cut_loss", "cut_pilot_within_budget", "cut_pilot_safe", "cut_fraction_loss"]),
    ("Proposition~\\ref{prop:increases}", ["increase_worst_case_monotone", "increase_worst_case",
                                          "increase_with_slope_bound"]),
    ("Proposition~\\ref{prop:adverse}", ["adverse_selection_cut", "adverse_selection_increase", "gain_antitone_in_psi"]),
    ("Theorem~\\ref{thm:cert}", ["direct_gain", "direct_gain_upper", "envelope_gain", "monotone_left_gain",
                                  "rate_cut_loss", "increase_with_slope_bound_lower", "slope_lower",
                                  "joint_left_gain", "joint_right_gain", "mono_lower", "chord_ext_left_interval",
                                  "chord_ext_right_interval", "chord_ext_left", "chord_ext_right",
                                  "pilotTestM_sound", "pilotTestEta_sound", "pilotTestC_sound"]),
    ("Proposition~\\ref{prop:tight}", ["twoPoint_convexOn", "twoPoint_antitone", "twoPoint_nonneg", "twoPoint_left",
                                      "twoPoint_right", "twoPoint_attains_left", "twoPoint_attains_between",
                                      "chordFloor_convexOn", "chordFloor_antitone", "chordFloor_nonneg",
                                      "chordFloor_left", "chordFloor_right", "chordFloor_attains_right"]),
    ("Lemma~\\ref{lem:conf}, relative entropy", ["klb_eq", "continuous_klb", "klb_symm", "klb_one", "mgf_zero_one",
                                                "chernoff_sum_upper", "chernoff_all_ones", "chernoff_kl_upper",
                                                "kl_upper_deviation", "kl_lower_deviation", "kl_deviation",
                                                "confidence_event_kl", "klb_self", "pinsker_bernoulli",
                                                "kl_within_radius", "kl_interval_width"]),
    ("Lemma~\\ref{lem:conf}, Hoeffding", ["bernoulli_subgaussian", "confidence_event_bernoulli", "confidence_event",
                                         "confidence_event_martingale", "radius_identity", "union_bound_schedule",
                                         "sum_budget_le", "budget_pos", "budget_le"]),
    ("Theorem~\\ref{thm:anytime}", ["adoption_sound", "rejection_sound", "incumbent_monotone", "deployed_ge_start_sub",
                                     "cumulative_profit_lower", "running_interval_contains", "budget_rel_le",
                                     "quoted_ge_start_rel", "anytime_trace", "anytime_trace_cumulative",
                                     "anytime_of_safe", "adoption_strict", "rejection_valid", "anytime_monotone",
                                     "anytime_slope", "anytime_convex", "confidence_limits_valid",
                                     "anytime_prob_of_sound", "anytime_monotone_prob", "anytime_slope_prob",
                                     "anytime_convex_prob"]),
    ("Proposition~\\ref{prop:detect}", ["certified_gain_lower", "certified_gain_upper", "detection_sample_size",
                                       "detection_bernoulli", "kl_within_radius", "kl_interval_width"]),
]


def lean_section(out):
    lean_dir = os.path.join(PROJ, "lean", "CreditCert")
    where, public = {}, []
    for f in sorted(glob.glob(os.path.join(lean_dir, "*.lean"))):
        for line in open(f):
            mm = re.match(r"^(theorem|lemma) (\S+)", line)
            if mm:
                where[mm.group(2)] = os.path.basename(f)
                public.append(mm.group(2))
    put("lean:public", str(len(public)))
    rows = []
    for res, names in LEAN_MAP:
        missing = [n for n in names if n not in where]
        if missing:
            raise SystemExit(f"Lean names not found for {res}: {missing}")
        files = sorted(set(where[n] for n in names))
        rows.append(f"{res} & " + ", ".join(f"\\lean{{{n}}}" for n in names) + " & " + ", ".join(files) + r" \\")
    tab = [r"\begin{longtable}{p{0.2\linewidth}p{0.55\linewidth}p{0.17\linewidth}}",
           r"\caption{Results of the paper and the Lean theorems that prove them.}\label{tab:lean}\\",
           r"\toprule", r"Result & Lean theorems & Files \\", r"\midrule", r"\endfirsthead",
           r"\toprule", r"Result & Lean theorems & Files \\", r"\midrule", r"\endhead"] + rows + [
           r"\bottomrule", r"\end{longtable}"]
    open(os.path.join(out, "tab_lean.tex"), "w").write("\n".join(tab) + "\n")


def write_numbers(out):
    lines = ["% generated by experiments/report.py; do not edit", r"\makeatletter",
             r"\newcommand{\num}[1]{\ifcsname num@#1\endcsname\csname num@#1\endcsname\else\errmessage{Undefined number #1}\fi}"]
    for k in sorted(NUM):
        lines.append(rf"\expandafter\def\csname num@{k}\endcsname{{{NUM[k]}}}")
    if "lean:count" in NUM:
        lines.append(rf"\newcommand{{\leancount}}{{{NUM['lean:count']}}}")
    else:
        print("WARNING: results/lean_axioms.log missing; \\leancount set to ??")
        lines.append(r"\newcommand{\leancount}{??}")
    lines.append(r"\makeatother")
    open(os.path.join(out, "numbers.tex"), "w").write("\n".join(lines) + "\n")


def check_keys(paper):
    used = set()
    for f in glob.glob(os.path.join(paper, "*.tex")):
        with open(f) as fh:
            used |= set(re.findall(r"\\num\{([^}]+)\}", fh.read()))
    missing = sorted(used - set(NUM))
    if missing:
        print("MISSING NUMBERS:", ", ".join(missing))
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default=os.path.join(RES, "main.json"))
    ap.add_argument("--paper", default=os.path.join(PROJ, "paper"))
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args()
    out = os.path.join(a.paper, "generated")
    os.makedirs(out, exist_ok=True)
    takeup_section(out)
    offers_section(out)
    sample_section(out)
    path = a.main if os.path.exists(a.main) else a.main + ".part.jsonl"
    runs = load_runs(path)
    main_section(out, runs)
    robust_section(out, runs)
    design_section(out, runs)
    adoption_section(out)
    safestep_section(out)
    verification_section()
    lean_section(out)
    if not a.no_figures:
        import figures
        figures.make_all(a.paper, runs, NUM)
    write_numbers(out)
    missing = check_keys(a.paper)
    print(f"{len(NUM)} numbers written; {len(runs)} runs from {os.path.basename(path)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
