"""Build every table and every quoted number of the paper from the stored results.

    python experiments/report.py [--out DIR]

Reads results/*.json and verification/verify_math.log.  Writes LaTeX tabulars (tab_*.tex) and
numbers.tex (one macro per quoted number, used in the text as \\num{key}) into DIR, which
defaults to ./generated.  Nothing in the paper's tables or quoted numbers is typed by hand.
"""
import importlib.util
import json
import math
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ctrr.agent import trr_rate, trr_step                      # noqa: E402
from ctrr.model import LogisticMarket, standard_markets        # noqa: E402

RES = os.path.join(ROOT, "results")
MK = ["m=0.3", "m=0.6", "m=0.8", "m=1.09"]
TAG = dict(zip(MK, "abcd"))
HEAD = {"m=0.3": "$m=0.3$", "m=0.6": "$m=0.6$", "m=0.8": "$m=0.8$", "m=1.09": "$m=1.09$"}
NUM = {}


def put(key, val):
    assert key not in NUM, key
    NUM[key] = str(val)


def fi(x):
    return f"{int(round(float(x)))}"


def fsep(x):
    return f"{int(round(float(x))):,}".replace(",", "{,}")


def load(name):
    with open(os.path.join(RES, f"{name}.json")) as f:
        d = json.load(f)
    idx = {}
    for c in d["cells"]:
        idx[(c["config"], c["market"], json.dumps(c["opts"], sort_keys=True))] = c["runs"]
    return d, idx


DATA = {s: load(s) for s in ("main", "noisy", "ablation", "robust", "horizon", "poisson")}


def runs(suite, cfg, mk, **opts):
    return DATA[suite][1][(cfg, mk, json.dumps(opts, sort_keys=True))]


class Stat:
    def __init__(self, rs, phi0):
        self.rs = rs
        self.n = len(rs)
        self.reg = np.array([r["regret"] for r in rs])
        self.below = np.array([r["below"] for r in rs])
        self.low = min(r["minphi"] for r in rs) / phi0
        self.tail = np.array([r["tail"] for r in rs])
        self.med = float(np.median(self.reg))
        self.q1, self.q3 = (float(v) for v in np.percentile(self.reg, [25, 75]))
        self.max = float(self.reg.max())
        self.bmed = float(np.median(self.below))
        self.bruns = int(np.sum(self.below > 0))
        self.ctrr = "moves" in rs[0]
        if self.ctrr:
            self.harm_runs = sum(1 for r in rs if r["harmful"] > 0)
            self.harm_moves = sum(r["harmful"] for r in rs)
            self.over = sum(r["over"] for r in rs)
            self.short = max((r["maxshort"] / r["ell"]) if r["ell"] else 0.0 for r in rs)
            self.worst_loss = max([-m[4] for r in rs for m in r["movelist"] if m[4] < 0] or [0.0])

    def miqr(self):
        return f"{fi(self.med)} [{fi(self.q1)}, {fi(self.q3)}]"


MARKETS = standard_markets()
LOGI = LogisticMarket(C1=1.2, c=3.0, hmid=1.6)
PHI0 = {m: float(MARKETS[m].Phi(MARKETS[m].stable_point())) for m in MK}
PHI0["logistic"] = float(LOGI.Phi(LOGI.stable_point()))


def st(suite, cfg, mk, **opts):
    phi0 = PHI0[mk]
    if "offset" in opts:
        mkt = MARKETS[mk]
        phi0 = float(mkt.Phi(mkt.stable_point() + opts["offset"]))
    return Stat(runs(suite, cfg, mk, **opts), phi0)


# ------------------------------------------------------------------ baseline families
FAM = {
    "ucb": ("UCB", [f"UCB arms={a} L={L}" for a in (13, 25, 41) for L in (2, 6, 12)]),
    "cucb": ("Conservative UCB", [f"CUCB arms={a} L={L}" for a in (13, 25) for L in (2, 6)]),
    "gd": ("PerfGD", [f"PerfGD delta={d} n={n} eta={e}"
                      for d in (0.1, 0.2) for n in (50, 100) for e in (0.25, 0.5, 1)]),
    "bz": ("Two-point TR", [f"BZ n0={n} rho={r}" for n in (25, 50) for r in (0.5, 1)]),
}


def params(cfg):
    """Human-readable parameters of a baseline configuration, in the paper's notation."""
    m = re.fullmatch(r"C?UCB arms=(\d+) L=(\S+?)( sigma=2.5x)?", cfg)
    if m:
        s = f"{m.group(1)} arms, $L={m.group(2)}$"
        return s + (", noise scale $2.5\\sigma$" if m.group(3) else "")
    m = re.fullmatch(r"PerfGD delta=(\S+) n=(\d+) eta=(\S+)", cfg)
    if m:
        return f"$u={m.group(1)}$, $n={m.group(2)}$, $\\eta={m.group(3)}$"
    m = re.fullmatch(r"BZ n0=(\d+) rho=(\S+)", cfg)
    if m:
        return f"$n_0={m.group(1)}$, $\\kappa={m.group(2)}$"
    raise ValueError(cfg)


def family_of(cfg):
    for k, (_, names) in FAM.items():
        if cfg in names:
            return k
    return None


def select_fixed(suite, **opts):
    return {k: min(names, key=lambda n: sum(st(suite, n, m, **opts).med for m in MK))
            for k, (_, names) in FAM.items()}


def select_oracle(suite, **opts):
    return {k: {m: min(names, key=lambda n: st(suite, n, m, **opts).med) for m in MK}
            for k, (_, names) in FAM.items()}


FIXED = select_fixed("main")
spec = importlib.util.spec_from_file_location("run_all", os.path.join(ROOT, "experiments", "run_all.py"))
run_all = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_all)
assert set(FIXED.values()) == set(run_all.FIXED), (FIXED, list(run_all.FIXED))

CTRR_LAB = {"C-TRR ell=5%": "C-TRR, $\\ell=5\\%$", "C-TRR ell=10%": "C-TRR, $\\ell=10\\%$",
            "C-TRR ell=20%": "C-TRR, $\\ell=20\\%$"}


def comparison_rows(suite, with20=False, **opts):
    """(slug, label, {market: config}) rows of a method comparison."""
    orc = select_oracle(suite, **opts)
    rows = [("ctrr5", CTRR_LAB["C-TRR ell=5%"], {m: "C-TRR ell=5%" for m in MK}),
            ("ctrr10", CTRR_LAB["C-TRR ell=10%"], {m: "C-TRR ell=10%" for m in MK})]
    if with20:
        rows.append(("ctrr20", CTRR_LAB["C-TRR ell=20%"], {m: "C-TRR ell=20%" for m in MK}))
    for k, (lab, _) in FAM.items():
        rows.append((k, f"{lab}, fixed", {m: FIXED[k] for m in MK}))
        rows.append((k + "O", f"{lab}, best per market", orc[k]))
    rows.append(("blind", "Blind retraining", {m: "Blind retraining" for m in MK}))
    rows.append(("ucbfull", "UCB on the full quote range", {m: "UCB uninformed arms=25 L=2" for m in MK}))
    return rows


def write(out, name, lines):
    with open(os.path.join(out, name), "w") as f:
        f.write("% generated by experiments/report.py; do not edit\n" + "\n".join(lines) + "\n")


def mc(n, text, align="c"):
    return f"\\multicolumn{{{n}}}{{{align}}}{{{text}}}"


HEAD8 = " & " + " & ".join(mc(2, HEAD[m]) for m in MK) + " \\\\"
RULES8 = "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\\cmidrule(l){8-9}"


# ------------------------------------------------------------------ tables
def table_landscape(out):
    L = ["\\begin{tabular}{@{}lrrrrrrrrrr@{}}", "\\toprule",
         "Market & $C_1$ & $m$ & $h_{\\mathrm{s}}$ & $h^\\star$ & $\\Phi(h_{\\mathrm{s}})$ & $\\Phi(h^\\star)$"
         " & gap & gap (\\%) & $\\Phi''(h_{\\mathrm{s}})$ & TR rate \\\\", "\\midrule"]
    items = [(HEAD[m], TAG[m], MARKETS[m]) for m in MK] + [("logistic", "l", LOGI)]
    for lab, tag, mk in items:
        hs, ho = mk.stable_point(), mk.optimum()
        ps, po = float(mk.Phi(hs)), float(mk.Phi(ho))
        mod = float(mk.modulus())
        rate = float(trr_rate(mk, ho))
        curv = -float(mk.gamma_po(hs))
        L.append(f"{lab} & {mk.C1:.4f} & {mod:.2f} & {hs:.4f} & {ho:.4f} & {ps:.4f} & {po:.4f} & "
                 f"{po - ps:.4f} & {100 * (po - ps) / ps:.1f} & ${curv:+.3f}$ & {rate:.3f} \\\\")
        for k, v in dict(hs=f"{hs:.3f}", ho=f"{ho:.3f}", phis=f"{ps:.3f}", phio=f"{po:.3f}",
                         gap=f"{po - ps:.3f}", gappct=f"{100 * (po - ps) / ps:.0f}",
                         gapT=fsep((po - ps) * 12000), mod=f"{mod:.2f}", rate=f"{rate:.2f}",
                         C1=f"{mk.C1:.4g}", taus=f"{float(mk.tau(hs)):.3f}",
                         dphis=f"{float(mk.dPhi(hs)):.3f}", curv=f"{curv:.3f}").items():
            put(f"mk:{tag}:{k}", v)
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_landscape.tex", L)
    # exact tangent-response iterates in the m = 0.6 market
    mk = MARKETS["m=0.6"]
    b, it = mk.stable_point(), []
    for _ in range(9):
        it.append(b)
        b = trr_step(mk, b, mk.psi, mk.h_hi)
    put("trr:b:iter", ", ".join(f"{v:.3f}" for v in it[:6]))
    put("trr:b:gain8", f"{100 * (float(mk.Phi(it[8])) - float(mk.Phi(it[0]))) / (float(mk.Phi(mk.optimum())) - float(mk.Phi(it[0]))):.1f}")


def table_main(out):
    rows = comparison_rows("main")
    L = ["\\begin{tabular}{@{}l*{4}{r@{\\quad}r}@{}}", "\\toprule", HEAD8, "\\midrule",
         mc(9, "\\emph{A. Cumulative regret, median [interquartile range]}", "@{}l") + " \\\\"]
    for slug, lab, cfgs in rows:
        cells = []
        for m in MK:
            s = st("main", cfgs[m], m)
            cells.append(mc(2, s.miqr()))
            for k, v in dict(reg=fsep(s.med), q1=fsep(s.q1), q3=fsep(s.q3), max=fsep(s.max),
                             below=fsep(s.bmed), belowruns=s.bruns, low=f"{s.low:.2f}").items():
                put(f"main:{slug}:{TAG[m]}:{k}", v)
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        if slug in ("ctrr10", "bzO"):
            L.append("\\addlinespace")
    L += ["\\midrule",
          mc(9, "\\emph{B. Safety: runs (of 30) with a period below the status quo; lowest profit of a "
                "deployed quote as a fraction of status-quo profit}", "@{}l") + " \\\\",
          " & " + " & ".join("runs & low" for _ in MK) + " \\\\", RULES8]
    for slug, lab, cfgs in rows:
        cells = []
        for m in MK:
            s = st("main", cfgs[m], m)
            cells += [str(s.bruns), f"{s.low:.2f}"]
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        if slug in ("ctrr10", "bzO"):
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_main.tex", L)
    # ratios of C-TRR to the best baseline of any family tuned per market
    orc = select_oracle("main")
    for m in MK:
        best = min(st("main", orc[k][m], m).med for k in FAM)
        bestfix = min(st("main", FIXED[k], m).med for k in FAM)
        for slug, cfg in (("ctrr5", "C-TRR ell=5%"), ("ctrr10", "C-TRR ell=10%")):
            put(f"main:{slug}:{TAG[m]}:ratio", f"{st('main', cfg, m).med / best:.1f}")
            put(f"main:{slug}:{TAG[m]}:ratiofix", f"{st('main', cfg, m).med / bestfix:.1f}")
        put(f"main:best:{TAG[m]}:reg", fsep(best))
    for k in FAM:
        put(f"fixed:{k}", params(FIXED[k]))


def table_diag(out):
    L = ["\\begin{tabular}{@{}llrrrrrrrrrr@{}}", "\\toprule",
         "$\\ell$ & Market & $d_0$ & moves & anchors & first move & final $b$ & $h^\\star$ & tail gap (\\%) & "
         "trial share & shortfall$/\\ell$ & over budget \\\\", "\\midrule"]
    for cfg, lab, slug in (("C-TRR ell=5%", "$5\\%$", "ctrr5"), ("C-TRR ell=10%", "$10\\%$", "ctrr10")):
        for m in MK:
            s = st("main", cfg, m)
            mk = MARKETS[m]
            gap = float(mk.Phi(mk.optimum())) - PHI0[m]
            rs = s.rs
            vals = dict(d0=f"{rs[0]['d0']:.3f}", moves=fi(np.median([r["moves"] for r in rs])),
                        anchors=fi(np.median([r["anchors"] for r in rs])),
                        first=fi(np.median([r["first"] for r in rs])),
                        inc=f"{np.median([r['inc'] for r in rs]):.3f}",
                        tailpct=f"{100 * np.median(s.tail) / gap:.1f}",
                        share=f"{np.median([r['trial_share'] for r in rs]):.2f}",
                        short=f"{s.short:.2f}", over=str(s.over), harmruns=str(s.harm_runs),
                        ell=f"{rs[0]['ell']:.4f}", maxmoves=str(max(r["moves"] for r in rs)),
                        nomove=str(sum(1 for r in rs if r["moves"] == 0)))
            for k, v in vals.items():
                put(f"diag:{slug}:{TAG[m]}:{k}", v)
            L.append(f"{lab} & {HEAD[m]} & {vals['d0']} & {vals['moves']} & {vals['anchors']} & {vals['first']} & "
                     f"{vals['inc']} & {mk.optimum():.3f} & {vals['tailpct']} & {vals['share']} & "
                     f"{vals['short']} & {vals['over']} \\\\")
        if slug == "ctrr5":
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_diag.tex", L)


def table_horizon(out):
    rows = [("ctrr5", CTRR_LAB["C-TRR ell=5%"], "C-TRR ell=5%"),
            ("ctrr10", CTRR_LAB["C-TRR ell=10%"], "C-TRR ell=10%")]
    for k, (lab, _) in FAM.items():
        rows.append((k, f"{lab}, fixed", FIXED[k]))
    for cfg in ("UCB arms=13 L=6", "UCB arms=25 L=6", "UCB arms=41 L=6", "PerfGD delta=0.1 n=100 eta=0.5",
                "BZ n0=50 rho=0.5"):
        k = family_of(cfg)
        rows.append((None, f"{FAM[k][0]}, {params(cfg)}", cfg))
    L = ["\\begin{tabular}{@{}l*{4}{r@{\\quad}r}@{}}", "\\toprule", HEAD8, "\\midrule",
         mc(9, "\\emph{A. Cumulative regret at $T=96{,}000$, median [interquartile range]}", "@{}l") + " \\\\"]
    for slug, lab, cfg in rows:
        cells = []
        for m in MK:
            s = st("horizon", cfg, m)
            cells.append(mc(2, s.miqr()))
            if slug:
                for k, v in dict(reg=fsep(s.med), max=fsep(s.max), belowruns=s.bruns,
                                 tail=f"{1000 * np.median(s.tail):.1f}",
                                 growth=f"{s.med / st('main', cfg, m).med:.1f}").items():
                    put(f"hor:{slug}:{TAG[m]}:{k}", v)
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        if slug in ("ctrr10", "bz"):
            L.append("\\addlinespace")
    L += ["\\midrule",
          mc(9, "\\emph{B. Growth of median regret from $T=12{,}000$ to $T=96{,}000$; median per-period gap "
                "over the last 1{,}000 periods ($\\times 10^{-3}$)}", "@{}l") + " \\\\",
          " & " + " & ".join("growth & gap" for _ in MK) + " \\\\", RULES8]
    for slug, lab, cfg in rows:
        cells = []
        for m in MK:
            s = st("horizon", cfg, m)
            cells += [f"{s.med / st('main', cfg, m).med:.1f}", f"{1000 * np.median(s.tail):.1f}"]
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        if slug in ("ctrr10", "bz"):
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_horizon.tex", L)
    for m in MK:
        best = min(st("horizon", r[2], m).med for r in rows if not r[0] or not r[0].startswith("ctrr"))
        for slug, cfg in (("ctrr5", "C-TRR ell=5%"), ("ctrr10", "C-TRR ell=10%")):
            put(f"hor:{slug}:{TAG[m]}:ratio", f"{st('horizon', cfg, m).med / best:.1f}")


def table_noise(out):
    L = ["\\begin{tabular}{@{}l*{4}{r@{\\quad}r}@{}}", "\\toprule", HEAD8,
         " & " + " & ".join("regret & runs" for _ in MK) + " \\\\", RULES8]
    for sig, tag in ((0.5, "s50"), (1.0, "s100")):
        rows = comparison_rows("noisy", with20=True, sigma=sig)
        L.append(mc(9, f"\\emph{{Flow noise $\\sigma={sig:g}$}}", "@{}l") + " \\\\")
        for slug, lab, cfgs in rows:
            if slug == "ucbfull":
                continue
            cells = []
            for m in MK:
                s = st("noisy", cfgs[m], m, sigma=sig)
                cells += [fi(s.med), str(s.bruns)]
                for k, v in dict(reg=fsep(s.med), max=fsep(s.max), below=fsep(s.bmed),
                                 belowruns=s.bruns, low=f"{s.low:.2f}").items():
                    put(f"{tag}:{slug}:{TAG[m]}:{k}", v)
                if s.ctrr:
                    put(f"{tag}:{slug}:{TAG[m]}:harmruns", s.harm_runs)
                    put(f"{tag}:{slug}:{TAG[m]}:over", s.over)
            L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
            if slug in ("ctrr20", "bzO"):
                L.append("\\addlinespace")
        orc = select_oracle("noisy", sigma=sig)
        for m in MK:
            best = min(st("noisy", orc[k][m], m, sigma=sig).med for k in FAM)
            for slug, cfg in (("ctrr5", "C-TRR ell=5%"), ("ctrr10", "C-TRR ell=10%"), ("ctrr20", "C-TRR ell=20%")):
                put(f"{tag}:{slug}:{TAG[m]}:ratio", f"{st('noisy', cfg, m, sigma=sig).med / best:.1f}")
        tot = [st("noisy", c, m, sigma=sig) for c in CTRR_LAB for m in MK]
        put(f"{tag}:ctrr:harmruns", sum(s.harm_runs for s in tot))
        put(f"{tag}:ctrr:over", sum(s.over for s in tot))
        put(f"{tag}:ctrr:belowruns", sum(s.bruns for s in tot))
        if sig == 0.5:
            L.append("\\midrule")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_noise.tex", L)


def table_budget(out):
    names = [("ell=1%", "$1\\%$"), ("ell=2%", "$2\\%$"), ("ell=5%", "$5\\%$"), ("ell=10%", "$10\\%$"),
             ("ell=20%", "$20\\%$"), ("ell=inf d0=0.5", "none ($d_0=0.5$)")]
    L = ["\\begin{tabular}{@{}lrrrrrrrr@{}}", "\\toprule",
         "Budget $\\ell/\\Phi(h_0)$ & " + " & ".join(HEAD[m] for m in MK) +
         " & $d_0$ ($m=0.6$) & shortfall$/\\ell$ & runs below & harmful \\\\", "\\midrule"]
    inf_short = {m: max(r["maxshort"] for r in runs("ablation", "ell=inf d0=0.5", m)) for m in MK}
    for m in MK:
        put(f"bud:inf:{TAG[m]}:short", f"{inf_short[m]:.2f}")
        put(f"bud:inf:{TAG[m]}:shortpct", f"{100 * inf_short[m] / PHI0[m]:.0f}")
    for cfg, lab in names:
        ss = [st("ablation", cfg, m) for m in MK]
        d0 = runs("ablation", cfg, "m=0.6")[0]["d0"]
        short = max(s.short for s in ss) if "inf" not in cfg else float("nan")
        L.append(f"{lab} & " + " & ".join(fi(s.med) for s in ss) + f" & {d0:.3f} & " +
                 ("--" if math.isnan(short) else f"{short:.2f}") +
                 f" & {sum(s.bruns for s in ss)} & {sum(s.harm_runs for s in ss)} \\\\")
        slug = cfg.replace("ell=", "").replace("%", "").replace(" d0=0.5", "")
        for m, s in zip(MK, ss):
            put(f"bud:{slug}:{TAG[m]}:reg", fsep(s.med))
            put(f"bud:{slug}:{TAG[m]}:d0", f"{runs('ablation', cfg, m)[0]['d0']:.3f}")
        put(f"bud:{slug}:belowruns", sum(s.bruns for s in ss))
        put(f"bud:{slug}:harmruns", sum(s.harm_runs for s in ss))
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_budget.tex", L)


def table_ablation(out):
    var = [("", "default"), (" cold start", "no warm start"), (" raw fit", "plug-in from raw means"),
           (" no expansion", "no safe expansion"), (" no optimistic step", "no optimistic refinement"),
           (" alpha=0.01", "$\\alpha=0.01$"), (" alpha=0.2", "$\\alpha=0.2$"),
           (" rho=1.25", "$\\rho=1.25$"), (" rho=2", "$\\rho=2$"), (" n0=8", "$n_0=8$"), (" n0=32", "$n_0=32$")]
    L = ["\\begin{tabular}{@{}l*{8}{r}@{}}", "\\toprule",
         " & " + mc(4, "$\\ell=5\\%$") + " & " + mc(4, "$\\ell=10\\%$") + " \\\\",
         "\\cmidrule(lr){2-5}\\cmidrule(l){6-9}",
         "Variant & " + " & ".join(HEAD[m] for m in MK) + " & " + " & ".join(HEAD[m] for m in MK) + " \\\\",
         "\\midrule"]
    for suf, lab in var:
        cells = []
        for tag in ("ell=5%", "ell=10%"):
            for m in MK:
                s = st("ablation", tag + suf, m)
                cells.append(fi(s.med) + ("$^{\\ast}$" if s.harm_runs else ""))
                key = (suf.strip().replace(" ", "").replace("=", "").replace(".", "") or "default")
                put(f"abl:{tag[4:-1]}:{key}:{TAG[m]}:reg", fsep(s.med))
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        if suf == "":
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_ablation.tex", L)


def table_uncert(out):
    var = [("", "anytime-valid, $\\alpha=0.05$"), (" uncertified z=1.64", "fixed $z=1.64$"),
           (" uncertified z=1", "fixed $z=1$"), (" uncertified z=0.5", "fixed $z=0.5$")]
    L = ["\\begin{tabular}{@{}ll*{4}{r@{\\quad}r}rr@{}}", "\\toprule",
         " & & " + " & ".join(mc(2, HEAD[m]) for m in MK) + " & over & worst \\\\",
         "$\\ell$ & Interval & " + " & ".join("regret & harm" for _ in MK) + " & budget & loss \\\\", "\\midrule"]
    sums = {}
    for tag, lab in (("ell=5%", "$5\\%$"), ("ell=10%", "$10\\%$")):
        for suf, vlab in var:
            ss = [st("ablation", tag + suf, m) for m in MK]
            cells = []
            for s in ss:
                cells += [fi(s.med), str(s.harm_runs)]
            over = sum(s.over for s in ss)
            worst = max(s.worst_loss for s in ss)
            L.append(f"{lab if suf == '' else ''} & {vlab} & " + " & ".join(cells) +
                     f" & {over} & {worst:.4f} \\\\")
            key = "cert" if suf == "" else "z" + suf.split("=")[1].replace(".", "")
            put(f"unc:{tag[4:-1]}:{key}:harmruns", sum(s.harm_runs for s in ss))
            put(f"unc:{tag[4:-1]}:{key}:over", over)
            put(f"unc:{tag[4:-1]}:{key}:worst", f"{worst:.3f}")
            put(f"unc:{tag[4:-1]}:{key}:belowruns", sum(s.bruns for s in ss))
            # sum over the four markets of the rounded median regrets (panel (c) of the price figure)
            sums[(tag, key)] = sum(int(round(float(s.med))) for s in ss)
            put(f"unc:{tag[4:-1]}:{key}:sum", fsep(sums[(tag, key)]))
            if key != "cert":
                put(f"unc:{tag[4:-1]}:{key}:cut", f"{sums[(tag, 'cert')] / sums[(tag, key)]:.1f}")
            for m, s in zip(MK, ss):
                put(f"unc:{tag[4:-1]}:{key}:{TAG[m]}:reg", fsep(s.med))
                put(f"unc:{tag[4:-1]}:{key}:{TAG[m]}:harmruns", s.harm_runs)
        if tag == "ell=5%":
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_uncert.tex", L)
    allz = [st("ablation", tag + suf, m) for tag in ("ell=5%", "ell=10%") for suf, _ in var[1:] for m in MK]
    put("unc:z:runs", len(allz) * 30)
    put("unc:z:harmruns", sum(s.harm_runs for s in allz))
    put("unc:z:worst", f"{max(s.worst_loss for s in allz):.3f}")


def table_robust(out):
    L = ["\\begin{tabular}{@{}ll*{4}{r@{\\;}r}rrr@{}}", "\\toprule",
         " & & " + " & ".join(mc(2, HEAD[m]) for m in MK) + " & harm & over & runs \\\\",
         "$\\ell$ & Condition & " + " & ".join("med. & (max)" for _ in MK) + " & runs & budget & below \\\\",
         "\\midrule"]
    for tag, lab, slug in (("C-TRR ell=5%", "$5\\%$", "5"), ("C-TRR ell=10%", "$10\\%$", "10")):
        conds = [("gauss", "Gaussian (reference)", "main", tag, {}),
                 ("laplace", "Laplace noise", "robust", tag, dict(noise="laplace")),
                 ("student", "Student-$t_5$ noise", "robust", tag, dict(noise="student5")),
                 ("uniform", "uniform noise", "robust", tag, dict(noise="uniform")),
                 ("sb15", "$\\bar\\sigma=1.5\\,\\sigma$", "robust", tag + " sigma_bar=1.5x", {}),
                 ("sb05", "$\\bar\\sigma=0.5\\,\\sigma$", "robust", tag + " sigma_bar=0.5x", {}),
                 ("coldm", "start $h_{\\mathrm{s}}-0.1$, no warm start", "robust", tag + " cold", dict(offset=-0.1)),
                 ("coldp", "start $h_{\\mathrm{s}}+0.1$, no warm start", "robust", tag + " cold", dict(offset=0.1))]
        for i, (key, clab, suite, cfg, opts) in enumerate(conds):
            ss = [st(suite, cfg, m, **opts) for m in MK]
            cells = []
            for s in ss:
                cells += [fi(s.med), f"({fi(s.max)})"]
            L.append(f"{lab if i == 0 else ''} & {clab} & " + " & ".join(cells) +
                     f" & {sum(s.harm_runs for s in ss)} & {sum(s.over for s in ss)} & {sum(s.bruns for s in ss)} \\\\")
            put(f"rob:{slug}:{key}:harmruns", sum(s.harm_runs for s in ss))
            put(f"rob:{slug}:{key}:over", sum(s.over for s in ss))
            put(f"rob:{slug}:{key}:belowruns", sum(s.bruns for s in ss))
            put(f"rob:{slug}:{key}:short", f"{max(s.short for s in ss):.2f}")
            for m, s in zip(MK, ss):
                put(f"rob:{slug}:{key}:{TAG[m]}:reg", fsep(s.med))
        if slug == "5":
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_robust.tex", L)


def table_logistic(out):
    rows = [("ctrr5", CTRR_LAB["C-TRR ell=5%"], "C-TRR ell=5%"), ("ctrr10", CTRR_LAB["C-TRR ell=10%"], "C-TRR ell=10%"),
            ("ctrrinf", "C-TRR, no budget ($d_0=0.5$)", "C-TRR ell=inf d0=0.5")]
    for k, (lab, _) in FAM.items():
        rows.append((k, f"{lab}, fixed", FIXED[k]))
    for cfg in ("UCB arms=13 L=2", "UCB arms=13 L=6", "UCB arms=25 L=2", "UCB arms=25 L=6",
                "PerfGD delta=0.1 n=100 eta=0.25", "PerfGD delta=0.1 n=100 eta=0.5",
                "BZ n0=50 rho=0.5", "BZ n0=50 rho=1"):
        rows.append((None, f"{FAM[family_of(cfg)][0]}, {params(cfg)}", cfg))
    L = ["\\begin{tabular}{@{}lrrrrr@{}}", "\\toprule",
         "Method & median regret [IQR] & max & runs below & low & harmful runs \\\\", "\\midrule"]
    for slug, lab, cfg in rows:
        s = st("robust", cfg, "logistic")
        L.append(f"{lab} & {s.miqr()} & {fi(s.max)} & {s.bruns} & {s.low:.2f} & "
                 f"{s.harm_runs if s.ctrr else '--'} \\\\")
        if slug:
            put(f"log:{slug}:reg", fsep(s.med))
            put(f"log:{slug}:belowruns", s.bruns)
            if s.ctrr:
                put(f"log:{slug}:short", f"{s.short:.2f}")
                put(f"log:{slug}:over", s.over)
                put(f"log:{slug}:harmruns", s.harm_runs)
        if slug in ("ctrrinf", "bz"):
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_logistic.tex", L)
    hs, ho = LOGI.stable_point(), LOGI.optimum()
    put("log:tau2", f"{float(LOGI.tau2(ho)):.2f}")


def table_poisson(out):
    P = dict(noise="poisson")
    rows = [("ctrr5v", "C-TRR, $\\ell=5\\%$, $\\bar\\sigma=2.5\\sigma$", "C-TRR ell=5% sigma_bar=2.5x"),
            ("ctrr10v", "C-TRR, $\\ell=10\\%$, $\\bar\\sigma=2.5\\sigma$", "C-TRR ell=10% sigma_bar=2.5x"),
            ("ctrr5m", "C-TRR, $\\ell=5\\%$, $\\bar\\sigma=\\sigma$ (too small)", "C-TRR ell=5% sigma_bar=1x"),
            ("ctrr10m", "C-TRR, $\\ell=10\\%$, $\\bar\\sigma=\\sigma$ (too small)", "C-TRR ell=10% sigma_bar=1x")]
    for k, (lab, _) in FAM.items():
        if (FIXED[k], "m=0.3", json.dumps(P, sort_keys=True)) in DATA["poisson"][1]:
            rows.append((k, f"{lab}, fixed", FIXED[k]))
    for cfg in ("UCB arms=13 L=6", "UCB arms=13 L=6 sigma=2.5x", "BZ n0=50 rho=0.5"):
        rows.append((None, f"{FAM[family_of(cfg.replace(' sigma=2.5x', ''))][0]}, {params(cfg)}", cfg))
    L = ["\\begin{tabular}{@{}l*{4}{r@{\\quad}r}rr@{}}", "\\toprule",
         " & " + " & ".join(mc(2, HEAD[m]) for m in MK) + " & harm & over \\\\",
         "Method & " + " & ".join("regret & runs" for _ in MK) + " & runs & budget \\\\", "\\midrule"]
    for slug, lab, cfg in rows:
        ss = [st("poisson", cfg, m, **P) for m in MK]
        cells = []
        for s in ss:
            cells += [fi(s.med), str(s.bruns)]
        extra = f"{sum(s.harm_runs for s in ss)} & {sum(s.over for s in ss)}" if ss[0].ctrr else "-- & --"
        L.append(f"{lab} & " + " & ".join(cells) + f" & {extra} \\\\")
        if slug:
            for m, s in zip(MK, ss):
                put(f"poi:{slug}:{TAG[m]}:reg", fsep(s.med))
            if ss[0].ctrr:
                put(f"poi:{slug}:harmruns", sum(s.harm_runs for s in ss))
                put(f"poi:{slug}:over", sum(s.over for s in ss))
                put(f"poi:{slug}:short", f"{max(s.short for s in ss):.2f}")
                put(f"poi:{slug}:belowruns", sum(s.bruns for s in ss))
        if slug in ("ctrr10m", "bz"):
            L.append("\\addlinespace")
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_poisson.tex", L)
    for m in MK:
        mk = MARKETS[m]
        put(f"poi:{TAG[m]}:sdratio", f"{math.sqrt(float(mk.tau(mk.optimum())) / float(mk.tau(mk.stable_point()))):.2f}")
        put(f"poi:{TAG[m]}:sdratiopsi", f"{math.sqrt(float(mk.tau(mk.psi)) / float(mk.tau(mk.stable_point()))):.2f}")
    # expected number of Poisson arrivals per period at the stable quote, tau(h_s)^2 / sigma^2, for sigma = 0.25
    arr = {m: float(MARKETS[m].tau(MARKETS[m].stable_point())) ** 2 / 0.25 ** 2 for m in MK}
    put("poi:arrivals", f"{arr['m=0.6']:.0f}")
    put("poi:arrivals:lo", f"{min(arr.values()):.0f}")
    put("poi:arrivals:hi", f"{max(arr.values()):.0f}")


def table_grid(out):
    for suite, opts, fname, tag in (("main", {}, "tab_grid_025.tex", "main"),
                                    ("noisy", dict(sigma=0.5), "tab_grid_050.tex", "s50"),
                                    ("noisy", dict(sigma=1.0), "tab_grid_100.tex", "s100")):
        orc = select_oracle(suite, **opts)
        names = [n for k in FAM for n in FAM[k][1]] + ["Blind retraining", "UCB uninformed arms=25 L=2"]
        L = ["\\begin{tabular}{@{}l*{4}{r@{\\quad}r}@{}}", "\\toprule", HEAD8,
             "Configuration & " + " & ".join("regret & below" for _ in MK) + " \\\\", RULES8]
        last = None
        for n in names:
            k = family_of(n)
            if k != last and last is not None:
                L.append("\\addlinespace")
            last = k
            lab = (f"{FAM[k][0]}, {params(n)}" if k else
                   ("Blind retraining" if n.startswith("Blind") else "UCB, full range, 25 arms, $L=2$"))
            if k and FIXED[k] == n:
                lab += "$^{\\dagger}$"
            cells = []
            for m in MK:
                s = st(suite, n, m, **opts)
                r = fi(s.med)
                if k and orc[k][m] == n:
                    r = f"\\textbf{{{r}}}"
                cells += [r, f"{fi(s.bmed)} ({s.bruns})"]
            L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        L += ["\\bottomrule", "\\end{tabular}"]
        write(out, fname, L)


def table_coverage(out):
    with open(os.path.join(RES, "coverage.json")) as f:
        cov = json.load(f)
    assert cov["mismatched"] == 0
    L = ["\\begin{tabular}{@{}lrrrrrr@{}}", "\\toprule",
         "Suite & runs & intervals & missed & seeds with a miss & harmful runs & of which after a miss \\\\",
         "\\midrule"]
    tot = dict(runs=0, iv=0, miss=0, harm=0, harm_after=0)
    seeds_all = set()
    for suite, lab in (("main", "main ($\\sigma=0.25$, $T=12{,}000$)"),
                       ("noisy", "noise ($\\sigma\\in\\{0.5,1\\}$, $T=12{,}000$)"),
                       ("horizon", "horizon ($\\sigma=0.25$, $T=96{,}000$)")):
        cells = [c for c in cov["cells"] if c["suite"] == suite]
        rs = [r for c in cells for r in c["runs"]]
        iv = sum(r["intervals"] for r in rs)
        miss = sum(len(r["misses"]) for r in rs)
        seeds = sorted({r["seed"] for r in rs if r["misses"]})
        seeds_all |= set(seeds)
        harm = [r for r in rs if r["harmful"] > 0]
        after = 0
        for r in harm:
            tmin = min(m[0] for m in r["movelist"] if m[4] < 0)
            after += any(ms[0] <= tmin for ms in r["misses"])
        L.append(f"{lab} & {len(rs)} & {iv} & {miss} & {len(seeds)} & {len(harm)} & {after} \\\\")
        tot["runs"] += len(rs)
        tot["iv"] += iv
        tot["miss"] += miss
        tot["harm"] += len(harm)
        tot["harm_after"] += after
        put(f"cov:{suite}:runs", fsep(len(rs)))
        put(f"cov:{suite}:intervals", fsep(iv))
        put(f"cov:{suite}:misses", miss)
    L += ["\\midrule", f"all & {tot['runs']} & {tot['iv']} & {tot['miss']} & {len(seeds_all)} & "
          f"{tot['harm']} & {tot['harm_after']} \\\\", "\\bottomrule", "\\end{tabular}"]
    write(out, "tab_coverage.tex", L)
    put("cov:runs", fsep(tot["runs"]))
    put("cov:intervals", fsep(tot["iv"]))
    put("cov:misses", tot["miss"])
    put("cov:seeds", len(seeds_all))
    put("cov:seedlist", ", ".join(str(s) for s in sorted(seeds_all)))
    put("cov:harm", tot["harm"])
    put("cov:harmafter", tot["harm_after"])
    put("cov:reproduced", fsep(cov["reproduced"]))
    # the single recorded miss (it recurs in every configuration of that seed)
    ms = [m for c in cov["cells"] if c["suite"] == "main" and c["budget"] == 0.05 and c["market"] == "m=0.3"
          for r in c["runs"] for m in r["misses"]]
    assert len(ms) == 1
    t, j, i, n, x, mean, truth, r = ms[0]
    z = (mean - truth) / (0.25 / math.sqrt(n))
    put("cov:miss:n", n)
    put("cov:miss:x", f"{x:.3f}")
    put("cov:miss:mean", f"{mean:.3f}")
    put("cov:miss:truth", f"{truth:.3f}")
    put("cov:miss:radius", f"{r:.3f}")
    put("cov:miss:z", f"{abs(z):.2f}")
    delta = 0.05 / (j * (j + 1) * i * (i + 1))
    put("cov:miss:crit", f"{math.sqrt(2 * math.log(2 / delta)):.2f}")
    put("cov:miss:pz", f"{math.erfc(abs(z) / math.sqrt(2)):.1e}".replace("e-0", "\\times 10^{-").replace("e-", "\\times 10^{-") + "}")
    put("cov:miss:pcrit", f"{math.erfc(math.sqrt(2 * math.log(2 / delta)) / math.sqrt(2)):.1e}".replace("e-0", "\\times 10^{-").replace("e-", "\\times 10^{-") + "}")


def table_harmful(out):
    """Every harmful adoption of a certified configuration, by cause."""
    rowsA, rowsB = [], []
    seen = set()

    def scan(suite, cfg, m, opts, lab, cause, shown=None):
        # `lab` identifies the configuration; `shown` is the printed label.  A long-horizon run repeats
        # the main-suite run of the same seed over its first 12,000 periods, so those moves are listed once.
        for i, r in enumerate(runs(suite, cfg, m, **opts)):
            for mv in r["movelist"]:
                if mv[4] < 0:
                    key = (lab, m, 100 + i, mv[0])
                    row = (shown or lab, HEAD[m], 100 + i, mv[0], mv[1], mv[2], mv[3], mv[4])
                    if key in seen:
                        continue
                    seen.add(key)
                    (rowsA if cause == "valid" else rowsB).append(row)

    for b in ("5", "10"):
        tag = f"C-TRR ell={b}%"
        lb = f"$\\ell={b}\\%$"
        for m in MK:
            scan("main", tag, m, {}, lb, "valid")
            scan("horizon", tag, m, {}, lb, "valid", shown=lb + ", $T=96{,}000$")
            for sig in (0.5, 1.0):
                scan("noisy", tag, m, dict(sigma=sig), f"{lb}, $\\sigma={sig:g}$", "valid")
            for suf, vl in ((" raw fit", "plug-in from raw means"), (" no expansion", "no safe expansion"),
                            (" no optimistic step", "no optimistic refinement"), (" cold start", "no warm start"),
                            (" alpha=0.01", "$\\alpha=0.01$"), (" alpha=0.2", "$\\alpha=0.2$"),
                            (" rho=1.25", "$\\rho=1.25$"), (" rho=2", "$\\rho=2$"),
                            (" n0=8", "$n_0=8$"), (" n0=32", "$n_0=32$")):
                scan("ablation", f"ell={b}%" + suf, m, {}, f"{lb}, {vl}", "valid")
            scan("robust", tag, m, dict(noise="uniform"), f"{lb}, uniform noise", "valid")
            scan("robust", tag + " sigma_bar=1.5x", m, {}, f"{lb}, $\\bar\\sigma=1.5\\sigma$", "valid")
            for off in (-0.1, 0.1):
                scan("robust", tag + " cold", m, dict(offset=off), f"{lb}, start offset ${off:+.1f}$", "valid")
            scan("poisson", tag + " sigma_bar=2.5x", m, dict(noise="poisson"),
                 f"{lb}, Poisson, $\\bar\\sigma=2.5\\sigma$", "outside")
            scan("robust", tag, m, dict(noise="laplace"), f"{lb}, Laplace noise", "outside")
            scan("robust", tag, m, dict(noise="student5"), f"{lb}, Student-$t_5$ noise", "outside")
            scan("robust", tag + " sigma_bar=0.5x", m, {}, f"{lb}, $\\bar\\sigma=0.5\\sigma$", "outside")
            scan("poisson", tag + " sigma_bar=1x", m, dict(noise="poisson"),
                 f"{lb}, Poisson, $\\bar\\sigma=\\sigma$", "outside")
    for m in MK:
        scan("ablation", "ell=1%", m, {}, "$\\ell=1\\%$", "valid")
        scan("ablation", "ell=2%", m, {}, "$\\ell=2\\%$", "valid")
        scan("ablation", "ell=20%", m, {}, "$\\ell=20\\%$", "valid")
        for sig in (0.5, 1.0):
            scan("noisy", "C-TRR ell=20%", m, dict(sigma=sig), f"$\\ell=20\\%$, $\\sigma={sig:g}$", "valid")
    L = ["\\begin{tabular}{@{}llrrrrrr@{}}", "\\toprule",
         "Configuration & Market & seed & period & from & to & certified gain & true gain \\\\", "\\midrule",
         mc(8, "\\emph{A. Noise bound valid (assumptions of Theorem~\\ref{thm:anytime} hold)}", "@{}l") + " \\\\"]
    for row in rowsA:
        L.append("{} & {} & {} & {} & {:.4f} & {:.4f} & {:.5f} & ${:.5f}$ \\\\".format(*row))
    L += ["\\addlinespace",
          mc(8, "\\emph{B. Noise bound too small, or noise not sub-Gaussian (outside the theorem)}", "@{}l") + " \\\\"]
    for row in rowsB:
        L.append("{} & {} & {} & {} & {:.4f} & {:.4f} & {:.5f} & ${:.5f}$ \\\\".format(*row))
    L += ["\\bottomrule", "\\end{tabular}"]
    write(out, "tab_harmful.tex", L)
    put("harm:valid:moves", len(rowsA))
    put("harm:valid:seeds", ", ".join(str(s) for s in sorted({r[2] for r in rowsA})))
    put("harm:valid:markets", ", ".join(sorted({r[1] for r in rowsA})))
    put("harm:valid:worst", f"{max(-r[7] for r in rowsA):.4f}")
    put("harm:valid:least", f"{min(-r[7] for r in rowsA):.4f}")
    put("harm:outside:moves", len(rowsB))
    put("harm:outside:worst", f"{max(-r[7] for r in rowsB):.4f}")
    return rowsA, rowsB


def misc_numbers():
    put("seeds", 30)
    log = open(os.path.join(ROOT, "verification", "verify_math.log")).read()
    m = re.search(r"(\d+) of (\d+) checks passed", log)
    assert m and m.group(1) == m.group(2), "verification log does not show all checks passing"
    put("ver:checks", m.group(2))
    m = re.search(r"Gaussian noise\s+\(failure frequency ([\d.]+) over (\d+) replications", log)
    put("ver:mcfail", f"{100 * float(m.group(1)):.2f}")
    put("ver:mcreps", fsep(int(m.group(2))))
    p = float(m.group(1))
    put("ver:anyof30", f"{100 * (1 - (1 - p) ** 30):.0f}")
    m = re.search(r"uniform noise\s+\(failure frequency ([\d.]+) over", log)
    put("ver:mcfailunif", f"{100 * float(m.group(1)):.2f}")
    mk = MARKETS["m=0.6"]
    put("gamma:min", f"{2 * mk.w - mk.A * mk.k * math.exp(-3):.3f}")
    put("gamma:max", f"{2 * mk.A * mk.k + 2 * mk.w:.1f}")


def main():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(ROOT, "generated")
    os.makedirs(out, exist_ok=True)
    table_landscape(out)
    table_main(out)
    table_diag(out)
    table_horizon(out)
    table_noise(out)
    table_budget(out)
    table_ablation(out)
    table_uncert(out)
    table_robust(out)
    table_logistic(out)
    table_poisson(out)
    table_grid(out)
    table_coverage(out)
    rowsA, rowsB = table_harmful(out)
    misc_numbers()
    lines = ["\\makeatletter",
             "\\newcommand{\\num}[1]{\\ifcsname num@#1\\endcsname\\csname num@#1\\endcsname"
             "\\else\\errmessage{Undefined number #1}\\fi}"]
    for k in sorted(NUM):
        lines.append(f"\\expandafter\\def\\csname num@{k}\\endcsname{{{NUM[k]}}}")
    lines.append("\\makeatother")
    write(out, "numbers.tex", lines)
    print(f"wrote {len(NUM)} numbers and the tables to {out}")
    print("fixed configurations:", FIXED)
    print("harmful adoptions, noise bound valid:")
    for r in rowsA:
        print("   ", r)
    print("harmful adoptions, outside the assumptions:")
    for r in rowsB:
        print("   ", r)


if __name__ == "__main__":
    main()
