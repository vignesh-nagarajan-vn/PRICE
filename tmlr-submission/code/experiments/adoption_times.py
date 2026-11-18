"""When does the certified search adopt?  Re-runs the certified runs of the main design with the same seeds and
records the quote count at each adoption.  The runs are deterministic given their seeds, so the final rates must
equal those in results/main.json; the script checks this for every run.

    python experiments/adoption_times.py [--procs P] [--out results/adoption_times.json]
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lending.agent import run_certified          # noqa: E402
from run_markets import KS, TAGS, market         # noqa: E402

STARTS = [-0.5, -0.25, 0.0, 0.25, 0.5, 1.0]
T, ELL_REL = 500000, 0.10


def run_one(job):
    tag, K, r, method, seed = job
    mk = market(tag, K)
    b0 = mk.psi + (mk.s_star - mk.psi) * (1.0 + r)
    shape = method.split("-")[1]
    kw = dict(eta=1.5 * mk.max_slope) if shape == "eta" else {}
    res = run_certified(mk, b0, T, np.random.default_rng(seed), n_hist=0, ell_rel=ELL_REL, shape=shape, **kw)
    times = [int(t) for t, _, _ in res["moves"]]
    return dict(tag=tag, K=K, r=r, method=method, seed=seed, final_rate=float(res["final"]), times=times)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=7)
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(ROOT), "results", "adoption_times.json"))
    ap.add_argument("--main", default=os.path.join(os.path.dirname(ROOT), "results", "main.json"))
    a = ap.parse_args()
    jobs = [(tag, K, r, m, 1_000_000 + 10_000 * ti + 1_000 * K + 100 * ri + s)
            for ti, tag in enumerate(TAGS) for K in KS for ri, r in enumerate(STARTS)
            for s in range(a.seeds) for m in ("cert-M", "cert-eta", "cert-C")]
    with Pool(a.procs, maxtasksperchild=500) as pool:
        out = list(pool.imap_unordered(run_one, jobs, chunksize=8))
    ref = {(r["tag"], r["K"], r["r"], r["method"], r["seed"]): r
           for r in json.load(open(a.main))["runs"] if r["method"].startswith("cert")}
    same = sum(ref[(r["tag"], r["K"], r["r"], r["method"], r["seed"])]["final_rate"] == r["final_rate"]
               and ref[(r["tag"], r["K"], r["r"], r["method"], r["seed"])]["n_moves"] == len(r["times"]) for r in out)
    json.dump(dict(n=len(out), same_as_main=same, T=T, runs=out), open(a.out, "w"))
    print(f"wrote {a.out}: {len(out)} runs, {same} identical to main.json in final rate and number of adoptions")


if __name__ == "__main__":
    main()
