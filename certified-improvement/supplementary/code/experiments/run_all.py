"""Run every experiment of the paper and write JSON files to results/.

    python -u experiments/run_all.py [suite ...] [--seeds N] [--procs P]

Suites: main, ablation, robust, horizon, noisy, poisson.  With no suite named, all are run.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ctrr.agent import CTRR                                             # noqa: E402
from ctrr.baselines import (BlindRetraining, StagePerfGD,               # noqa: E402
                            StageTangentResponse, UCBGrid)
from ctrr.model import Env, LogisticMarket, Market, standard_markets    # noqa: E402

T_MAIN = 12000
SEED0 = 100


def get_market(name):
    if name.startswith("m="):
        return standard_markets()[name]
    if name == "logistic":
        return LogisticMarket(C1=1.2, c=3.0, hmid=1.6)
    raise ValueError(name)


def make_agent(cfg, mk, h0, phi0):
    cfg = dict(cfg)
    kind = cfg.pop("kind")
    if kind == "ctrr":
        bud = cfg.pop("bud", None)
        sb = cfg.pop("sigma_mult", None)
        if sb is not None:
            cfg["sigma_bar"] = sb * mk.sigma
        return CTRR(mk, h0, budget=None if bud is None else bud * phi0, **cfg)
    if kind == "ucb":
        sm = cfg.pop("sigma_mult", None)
        if sm is not None:
            cfg["sigma"] = sm * mk.sigma
        dom = cfg.pop("dom", "informed")
        known = cfg.pop("known", True)
        cons = cfg.pop("cons", None)
        if dom == "full":
            return UCBGrid(mk, mk.psi, 3.6, start=None, phi0=phi0, conservative=cons, **cfg)
        return UCBGrid(mk, mk.psi, h0, start=h0, phi0=phi0, conservative=cons,
                       tau_start=-float(mk.Kp(h0)) if known else None, **cfg)
    if kind == "gd":
        return StagePerfGD(mk, h0, hi=h0, **cfg)
    if kind == "bz":
        return StageTangentResponse(mk, h0, hi=h0, **cfg)
    if kind == "blind":
        return BlindRetraining(mk, h0, **cfg)
    raise ValueError(kind)


def run_one(job):
    market, cfg, seed, T, opts = job
    mk = get_market(market)
    if "sigma" in opts:
        mk = replace(mk, sigma=opts["sigma"])
    hstar = mk.stable_point()
    h0 = hstar + opts.get("offset", 0.0)
    phi0 = float(mk.Phi(h0))
    hpo = mk.optimum()
    best = float(mk.Phi(hpo))
    ag = make_agent(cfg, mk, h0, phi0)
    env = Env(mk, seed=seed, noise=opts.get("noise", "gauss"))
    path = np.empty(T)
    for t in range(T):
        h = ag.act()
        ag.observe(h, env.deploy(h))
        path[t] = h
    phi = mk.Phi(path)
    reg = np.cumsum(best - phi)
    cps = np.unique(np.round(np.geomspace(10, T, 48)).astype(int))
    out = dict(regret=float(reg[-1]), below=int(np.sum(phi < phi0 - 1e-12)),
               minphi=float(phi.min()), tail=float(np.mean(best - phi[-1000:])),
               hfinal=float(np.mean(path[-1000:])), curve=[float(reg[c - 1]) for c in cps])
    if cfg["kind"] == "ctrr":
        incp = np.array(ag.inc_path)
        short = mk.Phi(incp) - phi
        true_gain = [float(mk.Phi(b) - mk.Phi(a)) for (_, a, b, _) in ag.moves]
        out.update(inc=ag.anchors[ag.inc].x, moves=len(ag.moves), anchors=len(ag.anchors),
                   harmful=sum(1 for g in true_gain if g < 0),
                   harm=float(-sum(g for g in true_gain if g < 0)),
                   movelist=[[int(t), float(a), float(b), float(c), g]
                             for (t, a, b, c), g in zip(ag.moves, true_gain)],
                   first=ag.moves[0][0] if ag.moves else -1,
                   maxshort=float(short.max()), ell=None if ag.ell is None else float(ag.ell),
                   over=int(np.sum(short > ag.ell + 1e-12)) if ag.ell is not None else 0,
                   d0=float(ag.d0), kinds="".join(p[3][0] for p in ag.proposals),
                   rejects=len(ag.rejects), trial_share=float(np.mean(ag.kinds)))
    return out


# ------------------------------------------------------------------ suites
MARKETS = ["m=0.3", "m=0.6", "m=0.8", "m=1.09"]

# The configuration of each baseline family with the smallest sum of median regrets over the four
# markets of the main suite (experiments/report.py recomputes this selection and stops if it
# differs).  These four configurations are also run in the horizon, Poisson and logistic experiments.
FIXED = {
    "UCB arms=13 L=12": dict(kind="ucb", n_arms=13, lip=12.0),
    "CUCB arms=13 L=6": dict(kind="ucb", n_arms=13, lip=6.0, cons=0.05),
    "PerfGD delta=0.1 n=50 eta=0.25": dict(kind="gd", delta=0.1, n_pairs=50, eta=0.25),
    "BZ n0=25 rho=0.5": dict(kind="bz", n0=25, rho=0.5),
}


def suite_main():
    cfgs = {}
    for b in (0.05, 0.10):
        cfgs[f"C-TRR ell={int(b * 100)}%"] = dict(kind="ctrr", bud=b)
    for n in (13, 25, 41):
        for L in (2.0, 6.0, 12.0):
            cfgs[f"UCB arms={n} L={L:g}"] = dict(kind="ucb", n_arms=n, lip=L)
    for n in (13, 25):
        for L in (2.0, 6.0):
            cfgs[f"CUCB arms={n} L={L:g}"] = dict(kind="ucb", n_arms=n, lip=L, cons=0.05)
    for d in (0.1, 0.2):
        for n in (50, 100):
            for e in (0.25, 0.5, 1.0):
                cfgs[f"PerfGD delta={d:g} n={n} eta={e:g}"] = dict(kind="gd", delta=d, n_pairs=n, eta=e)
    for n0 in (25, 50):
        for r in (0.5, 1.0):
            cfgs[f"BZ n0={n0} rho={r:g}"] = dict(kind="bz", n0=n0, rho=r)
    cfgs["Blind retraining"] = dict(kind="blind", window=50)
    cfgs["UCB uninformed arms=25 L=2"] = dict(kind="ucb", dom="full", n_arms=25, lip=2.0)
    return [(c, mk, {}, T_MAIN) for c in cfgs for mk in MARKETS], cfgs


def suite_ablation():
    cfgs = {}
    for b in (0.01, 0.02, 0.05, 0.10, 0.20):
        cfgs[f"ell={b * 100:g}%"] = dict(kind="ctrr", bud=b)
    cfgs["ell=inf d0=0.5"] = dict(kind="ctrr", d0=0.5)
    for b in (0.05, 0.10):
        tag = f"ell={int(b * 100)}%"
        cfgs[f"{tag} cold start"] = dict(kind="ctrr", bud=b, warm=False)
        cfgs[f"{tag} raw fit"] = dict(kind="ctrr", bud=b, fit="raw")
        cfgs[f"{tag} no expansion"] = dict(kind="ctrr", bud=b, expand=False)
        cfgs[f"{tag} no optimistic step"] = dict(kind="ctrr", bud=b, optimistic=False)
        for z in (0.5, 1.0, 1.64):
            cfgs[f"{tag} uncertified z={z:g}"] = dict(kind="ctrr", bud=b, zfix=z)
        for a in (0.01, 0.2):
            cfgs[f"{tag} alpha={a:g}"] = dict(kind="ctrr", bud=b, alpha=a)
        for r in (1.25, 2.0):
            cfgs[f"{tag} rho={r:g}"] = dict(kind="ctrr", bud=b, rho=r)
        for n0 in (8, 32):
            cfgs[f"{tag} n0={n0}"] = dict(kind="ctrr", bud=b, n0=n0)
    return [(c, mk, {}, T_MAIN) for c in cfgs for mk in MARKETS], cfgs


def suite_robust():
    cfgs, jobs = {}, []
    for b in (0.05, 0.10):
        tag = f"C-TRR ell={int(b * 100)}%"
        cfgs[tag] = dict(kind="ctrr", bud=b)
        cfgs[f"{tag} sigma_bar=1.5x"] = dict(kind="ctrr", bud=b, sigma_mult=1.5)
        cfgs[f"{tag} sigma_bar=0.5x"] = dict(kind="ctrr", bud=b, sigma_mult=0.5)
        cfgs[f"{tag} cold"] = dict(kind="ctrr", bud=b, warm=False)
        for noise in ("laplace", "student5", "uniform"):
            jobs += [(tag, mk, dict(noise=noise), T_MAIN) for mk in MARKETS]
        jobs += [(f"{tag} sigma_bar=1.5x", mk, {}, T_MAIN) for mk in MARKETS]
        jobs += [(f"{tag} sigma_bar=0.5x", mk, {}, T_MAIN) for mk in MARKETS]
        for off in (-0.1, 0.1):
            jobs += [(f"{tag} cold", mk, dict(offset=off), T_MAIN) for mk in MARKETS]
        jobs += [(tag, "logistic", {}, T_MAIN)]
    cfgs["C-TRR ell=inf d0=0.5"] = dict(kind="ctrr", d0=0.5)
    jobs += [("C-TRR ell=inf d0=0.5", "logistic", {}, T_MAIN)]
    for n in (13, 25):
        for L in (2.0, 6.0):
            cfgs[f"UCB arms={n} L={L:g}"] = dict(kind="ucb", n_arms=n, lip=L)
            jobs += [(f"UCB arms={n} L={L:g}", "logistic", {}, T_MAIN)]
    for e in (0.25, 0.5):
        cfgs[f"PerfGD delta=0.1 n=100 eta={e:g}"] = dict(kind="gd", delta=0.1, n_pairs=100, eta=e)
        jobs += [(f"PerfGD delta=0.1 n=100 eta={e:g}", "logistic", {}, T_MAIN)]
    for r in (0.5, 1.0):
        cfgs[f"BZ n0=50 rho={r:g}"] = dict(kind="bz", n0=50, rho=r)
        jobs += [(f"BZ n0=50 rho={r:g}", "logistic", {}, T_MAIN)]
    for name, c in FIXED.items():
        if name not in cfgs:
            cfgs[name] = c
            jobs += [(name, "logistic", {}, T_MAIN)]
    return jobs, cfgs


def suite_horizon():
    T = 96000
    cfgs = {
        "C-TRR ell=5%": dict(kind="ctrr", bud=0.05),
        "C-TRR ell=10%": dict(kind="ctrr", bud=0.10),
        "UCB arms=13 L=6": dict(kind="ucb", n_arms=13, lip=6.0),
        "UCB arms=25 L=6": dict(kind="ucb", n_arms=25, lip=6.0),
        "UCB arms=41 L=6": dict(kind="ucb", n_arms=41, lip=6.0),
        "PerfGD delta=0.1 n=100 eta=0.5": dict(kind="gd", delta=0.1, n_pairs=100, eta=0.5),
        "BZ n0=50 rho=0.5": dict(kind="bz", n0=50, rho=0.5),
    }
    for name, c in FIXED.items():
        cfgs.setdefault(name, c)
    return [(c, mk, {}, T) for c in cfgs for mk in MARKETS], cfgs


def suite_noisy():
    """The main comparison with two and four times the flow noise."""
    _, cfgs = suite_main()
    cfgs = dict(cfgs)
    cfgs["C-TRR ell=20%"] = dict(kind="ctrr", bud=0.20)
    jobs = [(c, mk, dict(sigma=s), T_MAIN) for s in (0.5, 1.0) for c in cfgs for mk in MARKETS]
    return jobs, cfgs


def suite_poisson():
    """Poisson arrival counts: noise that is neither Gaussian nor homoscedastic."""
    cfgs = {}
    for b in (0.05, 0.10):
        tag = f"C-TRR ell={int(b * 100)}%"
        cfgs[f"{tag} sigma_bar=1x"] = dict(kind="ctrr", bud=b)
        cfgs[f"{tag} sigma_bar=2.5x"] = dict(kind="ctrr", bud=b, sigma_mult=2.5)
    cfgs["UCB arms=13 L=6"] = dict(kind="ucb", n_arms=13, lip=6.0)
    cfgs["UCB arms=13 L=6 sigma=2.5x"] = dict(kind="ucb", n_arms=13, lip=6.0, sigma_mult=2.5)
    cfgs["PerfGD delta=0.1 n=50 eta=0.25"] = dict(kind="gd", delta=0.1, n_pairs=50, eta=0.25)
    cfgs["BZ n0=50 rho=0.5"] = dict(kind="bz", n0=50, rho=0.5)
    for name, c in FIXED.items():
        cfgs.setdefault(name, c)
    return [(c, mk, dict(noise="poisson"), T_MAIN) for c in cfgs for mk in MARKETS], cfgs


SUITES = dict(main=suite_main, ablation=suite_ablation, robust=suite_robust, horizon=suite_horizon,
              noisy=suite_noisy, poisson=suite_poisson)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nseeds = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 30
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 8
    args = [a for a in args if a in SUITES]
    names = args or list(SUITES)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    for name in names:
        t0 = time.time()
        cells, cfgs = SUITES[name]()
        jobs, keys = [], []
        for (cname, market, opts, T) in cells:
            for s in range(SEED0, SEED0 + nseeds):
                jobs.append((market, cfgs[cname], s, T, opts))
                keys.append((cname, market, json.dumps(opts, sort_keys=True), T))
        with Pool(procs) as pool:
            res = pool.map(run_one, jobs, chunksize=4)
        cells_out = {}
        for k, r in zip(keys, res):
            cells_out.setdefault(k, []).append(r)
        out = dict(suite=name, seeds=list(range(SEED0, SEED0 + nseeds)), configs=cfgs,
                   cells=[dict(config=k[0], market=k[1], opts=json.loads(k[2]), T=k[3], runs=v)
                          for k, v in cells_out.items()])
        path = os.path.join(ROOT, "results", f"{name}.json")
        with open(path, "w") as f:
            json.dump(out, f)
        print(f"{name}: {len(jobs)} runs in {time.time() - t0:.0f}s -> {path}", flush=True)


if __name__ == "__main__":
    main()
