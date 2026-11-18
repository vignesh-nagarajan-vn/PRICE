"""Main experiments: HMDA-calibrated lending markets, certified rate search versus baselines.

Markets: one per state-year (CA, FL, TX x 2022, 2023) and number K of competing quotes (1, 2, 3), with the
break-even spread set by the first-order condition at the median lender markup (code/hmda_offers.py).
Starting rates: psi + m* (1 + r) for r in STARTS, where m* = s* - psi is the optimal margin, so r = -0.5 is a
lender charging half the optimal margin and r = 1 one charging twice it.
Methods: the certified rate search with three shape classes (M: monotone only; eta: monotone with a valid slope
bound, 1.5 x the curve's largest slope; C: monotone and convex) and the baselines of lending/baselines.py.

    python experiments/run_markets.py [--seeds S] [--seeds-base S] [--T T] [--procs P] [--out results/main.json]
           [--ell-rel 0.1] [--n-hist 0] [--starts -0.5,-0.25,0,0.25,0.5,1] [--methods ...]
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.path.dirname(ROOT), "data", "derived")
sys.path.insert(0, ROOT)

from lending.agent import run_certified                                    # noqa: E402
from lending.baselines import (arms_around, run_cucb, run_etc, run_klucb, run_safe_ucb, run_stay, run_ts,  # noqa: E402
                               run_ucb)
from lending.market import ShoppingMarket                                  # noqa: E402
from lending.metrics import summarize                                     # noqa: E402

TAGS = ["CA_2022", "CA_2023", "FL_2022", "FL_2023", "TX_2022", "TX_2023"]
KS = [1, 2, 3]
METHODS = ["cert-M", "cert-eta", "cert-C", "safe-M", "safe-eta", "stay", "etc", "ucb", "klucb", "cucb", "ts", "ts-own"]
SAFE_STEP = 0.01    # lattice step of the safe UCB baseline: the best of 0.005, 0.01, 0.02, 0.04 (results/safe_step*.json)
OWN_PRIOR_MEAN, OWN_PRIOR_SD = (3.4, -0.2), (0.1, 0.05)   # set from results/hmda_takeup.json (see report)
B = 200
_CACHE = {}


def market(tag, K):
    if (tag, K) not in _CACHE:
        _CACHE[(tag, K)] = ShoppingMarket.from_hmda(os.path.join(DATA, f"offers_{tag}.json"), K)
    return _CACHE[(tag, K)]


def run_one(job):
    tag, K, r, method, seed, T, ell_rel, n_hist, extra = job
    mk = market(tag, K)
    m_star = mk.s_star - mk.psi
    b0 = mk.psi + m_star * (1.0 + r)
    phi0 = float(mk.phi(b0))
    rng = np.random.default_rng(seed)
    t0 = time.time()
    if method.startswith("cert-"):
        shape = method.split("-")[1]
        kw = dict(extra)
        for key in ("own_sd_mult", "own_level", "arms", "safe_step", "safe_refresh"):
            kw.pop(key, None)
        if shape == "eta":
            kw["eta"] = kw.pop("eta_mult", 1.5) * mk.max_slope
        else:
            kw.pop("eta_mult", None)
        res = run_certified(mk, b0, T, rng, n_hist=n_hist, ell_rel=ell_rel, shape=shape, **kw)
    elif method.startswith("safe-"):
        shape = method.split("-")[1]
        res = run_safe_ucb(mk, b0, T, rng, rho=ell_rel, shape=shape, eta=1.5 * mk.max_slope,
                           step=dict(extra).get("safe_step", SAFE_STEP),
                           refresh=dict(extra).get("safe_refresh", True))
    else:
        arms = arms_around(b0, mk.psi, mk.lo, mk.hi)
        if dict(extra).get("arms") == "margin":
            # robustness: a grid scaled to the market, at multiples of one eighth of the optimal margin from
            # 1/8 to 3 times the margin (it contains every starting rate and the optimal rate)
            arms = mk.psi + m_star * np.arange(1, 25) / 8.0
            arms = arms[(arms >= mk.lo - 1e-9) & (arms <= mk.hi + 1e-9)]
        if method == "stay":
            res = run_stay(mk, b0, T, rng)
        elif method == "etc":
            res = run_etc(mk, b0, T, rng, arms)
        elif method == "ucb":
            res = run_ucb(mk, b0, T, rng, arms, B)
        elif method == "klucb":
            res = run_klucb(mk, b0, T, rng, arms, B)
        elif method == "cucb":
            res = run_cucb(mk, b0, T, rng, arms, B, beta=ell_rel)
        elif method == "ts":
            res = run_ts(mk, b0, T, rng, arms, B)
        elif method == "ts-own":
            # prior from a take-up model fitted to approved applications (HMDA: take-up near 0.97, slope near
            # zero), stated as logit level and logit slope per point; own_sd_mult weakens it (robustness)
            mult = dict(extra).get("own_sd_mult", 1.0)
            pm = OWN_PRIOR_MEAN
            if dict(extra).get("own_level") == "matched":
                # robustness: the prior level is the logit of the true take-up at the starting rate, so only
                # the flat slope of the own-data model is wrong
                a0 = min(max(float(mk.a(np.array([b0]))[0]), 1e-6), 1 - 1e-6)
                pm = (math.log(a0 / (1 - a0)), OWN_PRIOR_MEAN[1])
            res = run_ts(mk, b0, T, rng, arms, B, prior_mean=pm,
                         prior_sd=tuple(mult * v for v in OWN_PRIOR_SD))
        else:
            raise ValueError(method)
    out = summarize(mk, b0, ell_rel * phi0, res)
    out.update(tag=tag, K=K, r=r, method=method, seed=seed, b0=b0, psi=mk.psi, s_star=mk.s_star,
               secs=time.time() - t0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=50, help="seeds per cell for the certified search")
    ap.add_argument("--seeds-base", type=int, default=20, help="seeds per cell for the baselines")
    ap.add_argument("--T", type=int, default=500000)
    ap.add_argument("--procs", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(ROOT), "results", "main.json"))
    ap.add_argument("--ell-rel", type=float, default=0.10)
    ap.add_argument("--n-hist", type=int, default=0)
    ap.add_argument("--starts", default="-0.5,-0.25,0,0.25,0.5,1")
    ap.add_argument("--methods", default=",".join(METHODS))
    ap.add_argument("--tags", default=",".join(TAGS))
    ap.add_argument("--Ks", default=",".join(map(str, KS)))
    ap.add_argument("--extra", default="{}", help="JSON dict of extra keyword arguments for the certified agent")
    a = ap.parse_args()
    starts = [float(x) for x in a.starts.split(",")]
    methods = a.methods.split(",")
    tags, ks = a.tags.split(","), [int(k) for k in a.Ks.split(",")]
    extra = json.loads(a.extra)
    jobs = []
    for ti, tag in enumerate(tags):
        for K in ks:
            for ri, r in enumerate(starts):
                for s in range(max(a.seeds, a.seeds_base)):
                    seed = 1_000_000 + 10_000 * ti + 1_000 * K + 100 * ri + s
                    for m in methods:
                        if s < (a.seeds if m.startswith("cert") else a.seeds_base):
                            jobs.append((tag, K, r, m, seed, a.T, a.ell_rel, a.n_hist, tuple(sorted(extra.items()))))
    # certified runs first (they are fast), then the baselines; within each, one market at a time
    jobs.sort(key=lambda j: (not j[3].startswith("cert"), j[0], j[1]))
    t0 = time.time()
    print(f"{len(jobs)} runs on {a.procs} processes", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    part = a.out + ".part.jsonl"                    # incremental output, so an interrupted run keeps its results
    done = set()
    if os.path.exists(part):
        for line in open(part):
            r = json.loads(line)
            done.add((r["tag"], r["K"], r["r"], r["method"], r["seed"]))
    todo = [j for j in jobs if (j[0], j[1], j[2], j[3], j[4]) not in done]
    print(f"{len(done)} already done, {len(todo)} to run", flush=True)
    with Pool(a.procs, maxtasksperchild=500) as pool, open(part, "a") as fh:
        for k, r in enumerate(pool.imap_unordered(run_one, todo, chunksize=8), 1):
            fh.write(json.dumps(r) + "\n")
            if k % 2000 == 0:
                fh.flush()
                print(f"  {k}/{len(todo)} runs, {(time.time() - t0) / 60:.1f} min", flush=True)
    want = {(j[0], j[1], j[2], j[3], j[4]) for j in jobs}
    out = [r for r in (json.loads(line) for line in open(part))
           if (r["tag"], r["K"], r["r"], r["method"], r["seed"]) in want]
    meta = dict(args=vars(a), n=len(out), minutes=(time.time() - t0) / 60)
    json.dump(dict(meta=meta, runs=out), open(a.out, "w"))
    print(f"wrote {a.out} ({len(out)} runs, {meta['minutes']:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
