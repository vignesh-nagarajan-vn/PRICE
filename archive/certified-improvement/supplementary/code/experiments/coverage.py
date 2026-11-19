"""Record, run by run, whether the confidence event of the anytime guarantee held.

    python -u experiments/coverage.py [--seeds N] [--procs P]

Re-runs every C-TRR configuration of the main, noisy and horizon suites with an agent
that also records, each time a confidence interval is computed, whether the raw interval
contains the true mean flow at that quote.  The agent's decisions are not changed: the
script checks that every run reproduces the regret stored by run_all.py.  The output,
results/coverage.json, lists every interval that missed the truth and every adoption.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ctrr.agent import CTRR                      # noqa: E402
from ctrr.model import Env, standard_markets     # noqa: E402

SEED0 = 100
MARKETS = ["m=0.3", "m=0.6", "m=0.8", "m=1.09"]


class Instrumented(CTRR):
    """C-TRR with a record of whether each new raw interval contains the truth."""

    def __init__(self, *a, **k):
        self.misses, self.n_intervals = [], 0
        super().__init__(*a, **k)

    def observe(self, h, y):
        a = self.anchors[self.cur]
        i_before = a.i
        super().observe(h, y)
        if a.i > i_before:                       # a checkpoint was processed, with index a.i
            self.n_intervals += 1
            dl = self.alpha / (a.j * (a.j + 1) * a.i * (a.i + 1))
            r = self.sig * math.sqrt(2 * math.log(2 / dl) / a.n)
            mean, truth = a.s / a.n, float(self.mk.tau(a.x))
            if not abs(mean - truth) <= r:
                self.misses.append([int(self.t), int(a.j), int(a.i), int(a.n), float(a.x),
                                    float(mean), truth, float(r)])


def run_one(job):
    market, bud, sigma, seed, T = job
    mk = replace(standard_markets()[market], sigma=sigma)
    h0 = mk.stable_point()
    phi0 = float(mk.Phi(h0))
    best = float(mk.Phi(mk.optimum()))
    ag = Instrumented(mk, h0, budget=bud * phi0)
    env = Env(mk, seed=seed)
    path = np.empty(T)
    for t in range(T):
        h = ag.act()
        ag.observe(h, env.deploy(h))
        path[t] = h
    phi = mk.Phi(path)
    short = mk.Phi(np.array(ag.inc_path)) - phi
    moves = [[int(t), float(a), float(b), float(c), float(mk.Phi(b) - mk.Phi(a))]
             for (t, a, b, c) in ag.moves]
    return dict(seed=seed, regret=float(np.sum(best - phi)), intervals=ag.n_intervals,
                misses=ag.misses, movelist=moves,
                harmful=sum(1 for m in moves if m[4] < 0),
                over=int(np.sum(short > ag.ell + 1e-12)),
                below=int(np.sum(phi < phi0 - 1e-12)))


def stored_regrets():
    """Regret of every C-TRR run stored by run_all.py, for the reproduction check."""
    out = {}
    for suite in ("main", "noisy", "horizon"):
        path = os.path.join(ROOT, "results", f"{suite}.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            d = json.load(f)
        for c in d["cells"]:
            if not c["config"].startswith("C-TRR ell="):
                continue
            bud = float(c["config"].split("=")[1].rstrip("%")) / 100
            sigma = c["opts"].get("sigma", 0.25)
            for s, r in zip(d["seeds"], c["runs"]):
                out[(c["market"], bud, sigma, s, c["T"])] = r["regret"]
    return out


def main():
    nseeds = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 30
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 8
    cells = [("main", b, 0.25, 12000) for b in (0.05, 0.10)]
    cells += [("noisy", b, s, 12000) for s in (0.5, 1.0) for b in (0.05, 0.10, 0.20)]
    cells += [("horizon", b, 0.25, 96000) for b in (0.05, 0.10)]
    jobs, keys = [], []
    for (suite, bud, sigma, T) in cells:
        for mk in MARKETS:
            for s in range(SEED0, SEED0 + nseeds):
                jobs.append((mk, bud, sigma, s, T))
                keys.append((suite, bud, sigma, T, mk))
    t0 = time.time()
    with Pool(procs) as pool:
        res = pool.map(run_one, jobs, chunksize=2)
    stored = stored_regrets()
    checked = mismatched = 0
    for job, r in zip(jobs, res):
        if job in stored:
            checked += 1
            if abs(stored[job] - r["regret"]) > 1e-6 * max(1.0, abs(stored[job])):
                mismatched += 1
    cells_out = {}
    for k, r in zip(keys, res):
        cells_out.setdefault(k, []).append(r)
    out = dict(seeds=list(range(SEED0, SEED0 + nseeds)), reproduced=checked, mismatched=mismatched,
               cells=[dict(suite=k[0], budget=k[1], sigma=k[2], T=k[3], market=k[4], runs=v)
                      for k, v in cells_out.items()])
    path = os.path.join(ROOT, "results", "coverage.json")
    with open(path, "w") as f:
        json.dump(out, f)
    print(f"coverage: {len(jobs)} runs in {time.time() - t0:.0f}s -> {path}", flush=True)
    print(f"reproduction check: {checked} runs compared with stored results, {mismatched} mismatched")
    for suite in ("main", "noisy", "horizon"):
        runs = [r for c in out["cells"] if c["suite"] == suite for r in c["runs"]]
        bad = [r for r in runs if r["misses"]]
        print(f"{suite}: {len(runs)} runs, {sum(r['intervals'] for r in runs)} intervals, "
              f"{sum(len(r['misses']) for r in runs)} missed the truth, in {len(bad)} runs; "
              f"runs with a harmful adoption: {sum(1 for r in runs if r['harmful'])}, "
              f"of which with a miss before it: "
              f"{sum(1 for r in runs if r['harmful'] and r['misses'])}")
    for c in out["cells"]:
        for r in c["runs"]:
            if r["misses"] or r["harmful"]:
                print(f"  {c['suite']} ell={c['budget']:g} sigma={c['sigma']:g} {c['market']} "
                      f"seed {r['seed']}: misses (t, anchor, checkpoint, n) "
                      f"{[m[:4] for m in r['misses']]}; harmful moves "
                      f"{[[m[0], round(m[1], 4), round(m[2], 4), round(m[4], 5)] for m in r['movelist'] if m[4] < 0]}")


if __name__ == "__main__":
    main()
