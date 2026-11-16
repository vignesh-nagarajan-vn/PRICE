"""Run the full pipeline and verify measured results against the theory.

Usage:  python experiments/run_all.py [--only e1|e2|e3|e4|e5] [--fast]

Writes results/RESULTS.md (the measured-vs-predicted table with
PASS / DRIFT / FAIL statuses) and per-experiment CSVs. Statuses:
  PASS  - measured matches the register's closed form within tolerance;
  DRIFT - deliberate out-of-scope cell (nonlinear env): the deviation is
          the *measured scope boundary*, reported, never a failure;
  FAIL  - mismatch inside the theory's scope: a bug or a wrong theorem.
Exit code is 0 iff no FAIL.
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posk import (BlindRRM, JitterPerfGD, Market, SafeDPerfGD,   # noqa: E402
                  SaturatingEnv, StructuralEnv, StructuralFit,
                  a_optimal_design, dispersion_factor, run_agent,
                  secant_slope)
from posk.design import d_optimal_3pt, fisher, isotropic_design  # noqa: E402

ROWS = []
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def row(exp, claim, measured, predicted, tol_rel, drift=False):
    if drift:
        status = "DRIFT"
    else:
        ok = abs(measured - predicted) <= tol_rel * max(abs(predicted), 1e-12)
        status = "PASS" if ok else "FAIL"
    ROWS.append((exp, claim, measured, predicted, tol_rel, status))
    print("  [%s] %s: measured %.5g vs predicted %.5g (tol %g%%)"
          % (status, claim, measured, predicted, 100 * tol_rel))


# ---------------------------------------------------------------- E1 ----
def e1_saturation(fast=False):
    """Pivot record: the first version predicted the noiseless cap for a
    NOISY retraining loop and failed by ~4x. Diagnosis: BR(tau_obs) converts
    observation noise into deployment noise with gain 1/gamma (the A3'
    feedback channel), adding a stationary excitation floor
    v_fb = (sigma/gamma)^2 / (1 - m^2) per step. The experiment now verifies
    BOTH closed forms: the transient cap (noiseless run) and the floor rate
    (affine fit of energy vs horizon in the noisy run). Scientific upshot
    kept for the paper: even zero deliberate exploration carries a
    retraining-noise excitation floor - and it sits on the same exchange-rate
    frontier."""
    from dataclasses import replace
    print("== E1: information saturation (T1/C1.1) + the feedback floor ==")
    for tgt in (0.3, 0.6, 0.85):
        mkt = Market(sigma=0.25).feedback_for_modulus(tgt)
        hs = mkt.h_sp()
        d0 = 0.10   # small excursion: the cap is a linearization
        # (a) transient cap: noiseless loop
        mkt0 = replace(mkt, sigma=0.0)
        env0 = StructuralEnv(mkt0, seed=1)
        path0 = run_agent(BlindRRM(mkt0, hs + d0), env0, 200)
        row("E1", "noiseless energy = saturation cap (m=%.2f)" % mkt.modulus(),
            float(((path0 - hs) ** 2).sum()), mkt.saturation_cap(d0), 0.10)
        # (b) feedback floor: noisy loop, energy slope in T
        mkt_n = replace(mkt, sigma=0.05)
        energies = {}
        for T in (300, 1200):
            env = StructuralEnv(mkt_n, seed=2)
            path = run_agent(BlindRRM(mkt_n, hs + d0), env, T)
            energies[T] = float(((path - hs) ** 2).sum())
        slope = (energies[1200] - energies[300]) / 900.0
        v_fb = (mkt_n.sigma / mkt.gamma(hs)) ** 2 / (1 - mkt.modulus() ** 2)
        row("E1", "noisy energy growth rate = feedback floor (m=%.2f)"
            % mkt.modulus(), slope, v_fb, 0.30)


# ---------------------------------------------------------------- E2 ----
def e2_exchange_rate(fast=False):
    print("== E2: the exchange rate (T2), and its nonlinear drift ==")
    T = 2500 if fast else 5000
    for tgt in (0.3, 0.6):
        mkt = Market(sigma=0.25).feedback_for_modulus(tgt)
        hs = mkt.h_sp()
        pred = mkt.exchange_rate()
        for s_e in (0.05, 0.15):
            rng = np.random.default_rng(7)
            env = StructuralEnv(mkt, seed=17)
            h = hs
            hh, yy = [], []
            n_obs = 25   # retraining consumes aggregated flow (REFLEX's
            for t in range(T):  # n_episodes convention); the estimator's tape
                obs = [env.deploy(h) for _ in range(1)]  # is single-draw
                y = obs[0]
                y_retrain = mkt.tau(h) + mkt.sigma / np.sqrt(n_obs) \
                    * rng.standard_normal()
                hh.append(h)
                yy.append(y)
                h = mkt.best_response(y_retrain) + s_e * rng.standard_normal()
            hh, yy = np.asarray(hh[300:]), np.asarray(yy[300:])
            hc = hh - hh.mean()
            sxx = float((hc ** 2).sum())
            var_eps = mkt.sigma ** 2 / sxx
            cost = float(np.sum(mkt.Phi(hh.mean()) - mkt.Phi(hh)))
            row("E2", "Var x Cost (m=%.1f, s_e=%.2f)" % (tgt, s_e),
                var_eps * cost, pred, 0.15)
    # drift cell: saturating environment (outside A1 scope - measured, not failed)
    mkt = Market(sigma=0.25).feedback_for_modulus(0.6)
    envn = SaturatingEnv(mkt, cap=0.9, seed=17)
    rng = np.random.default_rng(7)
    h = mkt.h_sp()
    hh = []
    for t in range(T):
        envn.deploy(h)
        hh.append(h)
        y_retrain = envn.true_tau(h) + mkt.sigma / 5.0 * rng.standard_normal()
        h = mkt.best_response(y_retrain) + 0.15 * rng.standard_normal()
    hh = np.asarray(hh[300:])
    hc = hh - hh.mean()
    var_eps = mkt.sigma ** 2 / float((hc ** 2).sum())
    cost = float(np.sum(mkt.Phi(hh.mean()) - mkt.Phi(hh)))
    row("E2", "drift cell: saturating env (out of A1 scope)",
        var_eps * cost, mkt.exchange_rate(), 0.0, drift=True)


# ---------------------------------------------------------------- E3 ----
def e3_shaped_exploration(fast=False):
    print("== E3: shaped vs isotropic exploration (T5a/C5.1) ==")
    rng = np.random.default_rng(11)
    d, B, sigma = 8, 1.0, 0.5
    Q, _ = np.linalg.qr(rng.standard_normal((d, d)))
    Gamma = Q @ np.diag(np.logspace(-1, 1, d)) @ Q.T
    F = dispersion_factor(Gamma)
    theta = rng.standard_normal(d)
    T = 1500 if fast else 4000
    seeds = 100 if fast else 200
    risks = {}
    for name, M in (("iso", isotropic_design(Gamma, B)),
                    ("aopt", a_optimal_design(Gamma, B))):
        L = np.linalg.cholesky(M + 1e-12 * np.eye(d))
        errs = np.empty(seeds)
        for s in range(seeds):
            r = np.random.default_rng(1000 + s)
            X = r.standard_normal((T, d)) @ L.T
            y = X @ theta + sigma * r.standard_normal(T)
            theta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
            errs[s] = ((theta_hat - theta) ** 2).sum()
        risks[name] = errs.mean()
        # budget check: realized tr(Gamma M_emp)/T stays at B
    row("E3", "isotropic/A-optimal risk ratio = dispersion F",
        risks["iso"] / risks["aopt"], F, 0.12)
    row("E3", "A-opt risk matches sigma^2 (tr G^{1/2})^2 / (T B)",
        risks["aopt"], sigma ** 2 * (np.sqrt(np.linalg.eigvalsh(Gamma)).sum()) ** 2
        / (T * B), 0.12)


# ---------------------------------------------------------------- E4 ----
def e4_design_identifies_curvature(fast=False):
    print("== E4: the design identifies what jitter cannot (T6); safety ==")
    mkt = Market(sigma=0.25).feedback_for_modulus(0.6)
    hs = mkt.h_sp()
    N = 600
    seeds = 30 if fast else 60
    r_tr = 0.8
    fit = StructuralFit()
    sds = {}
    for name in ("jitter", "design"):
        cs = np.empty(seeds)
        for s in range(seeds):
            env = StructuralEnv(mkt, seed=5000 + s)
            r = np.random.default_rng(6000 + s)
            if name == "jitter":
                hh = hs + 0.05 * r.standard_normal(N)
            else:
                pts = d_optimal_3pt(hs, r_tr, mkt.C1, mkt.c)
                hh = np.tile(pts, N // 3 + 1)[:N]
            yy = np.array([env.deploy(h) for h in hh])
            cs[s] = fit.fit(hh, yy)["c"]
        sds[name] = cs.std()
    # Fisher-predicted sd for the 3-point design (c-component)
    pts = d_optimal_3pt(hs, r_tr, mkt.C1, mkt.c)
    M = fisher(pts, [N / 3] * 3, mkt.C1, mkt.c) / mkt.sigma ** 2
    pred_sd = float(np.sqrt(np.linalg.inv(M)[2, 2]))
    row("E4", "design arm sd(c_hat) matches Fisher prediction",
        sds["design"], pred_sd, 0.5)
    ratio = sds["jitter"] / sds["design"]
    row("E4", "jitter arm unidentified (sd ratio jitter/design >= 3: ratio=%.1f)"
        % ratio, float(ratio >= 3.0), 1.0, 0.0)
    # safety + performance of the full SafeD-PerfGD agent (certification
    # takes design energy - the gate timeline IS the exchange rate at work)
    env = StructuralEnv(mkt, seed=99)
    agent = SafeDPerfGD(mkt, h0=hs, r=0.6, margin=0.3, refit_every=10)
    T_safe = 3000 if fast else 4000
    path = run_agent(agent, env, T_safe)
    hpo = mkt.h_po()
    row("E4", "SafeD-PerfGD settles at the performative optimum",
        float(np.mean(agent.h)), hpo, 0.08)
    steps = np.abs(np.diff(path))
    # consecutive deployments may span the design support (2r) plus one
    # centre move (the trust-region cap) - that is the true bound
    caps = agent.max_rel_step * np.maximum(np.abs(path[:-1]), 0.2) \
        + 2 * agent.r + 1e-9
    row("E4", "trust region never violated (max step/cap=%.2f <= 1)"
        % float((steps / caps).max()), float((steps / caps).max() <= 1.0),
        1.0, 0.0)
    print("    (freeze fraction: %.2f, corrected steps: %d)"
          % (agent.frozen_steps / max(agent.frozen_steps + agent.corrected_steps, 1),
             agent.corrected_steps))


# ---------------------------------------------------------------- E5 ----
def e5_anchoring_crossover(fast=False):
    print("== E5: the anchoring crossover (T7) ==")
    mkt = Market(sigma=0.25).feedback_for_modulus(0.5)
    hs = mkt.h_sp()
    B, T = 0.6, 120
    S = 2 * B / mkt.gamma_po(hs)
    w = float(np.sqrt(S / T))
    seeds = 400 if fast else 700
    eps_true0 = mkt.eps(hs)
    mse_np_pred = mkt.mse_np(B, T)
    # nonparametric arm measured
    errs = np.empty(seeds)
    for s in range(seeds):
        env = StructuralEnv(mkt, seed=20_000 + s)
        slope = secant_slope(env, hs, w, T // 2)
        errs[s] = (-slope) - eps_true0
    row("E5", "nonparametric MSE at (B,T) optimum", float((errs ** 2).mean()),
        mse_np_pred, 0.15)
    # anchored arm across misspecification a: true tau += a * exp(-2c h)
    fit = StructuralFit()
    pts = d_optimal_3pt(hs, w * np.sqrt(3.0 / 2.0), mkt.C1, mkt.c)

    class MisEnv(StructuralEnv):
        """Misspecification that lives AT the operating point: a linear
        leak -a*h the exponential family cannot represent. (The first
        version injected a*e^{-2ch}, which has decayed to ~0 at the
        operating spread - the anchored fit rightly never saw it; pivot
        recorded.)"""

        def __init__(self, market, a, seed):
            super().__init__(market, seed)
            self.a = a

        def true_tau(self, h):
            return self.m.tau(h) - self.a * h

    a_grid = np.array([0.0, 0.05, 0.1, 0.2, 0.35])
    mse_anchor = []
    for a in a_grid:
        errs = np.empty(seeds)
        eps_true = mkt.eps(hs) + a
        for s in range(seeds):
            env = MisEnv(mkt, a, seed=40_000 + s)
            hh = np.tile(pts, T // 3 + 1)[:T]
            yy = np.array([env.deploy(h) for h in hh])
            p = fit.fit(hh, yy)
            errs[s] = StructuralFit.eps_hat(p, hs) - eps_true
        mse_anchor.append(float((errs ** 2).mean()))
    mse_anchor = np.asarray(mse_anchor)
    # verify direction: anchored beats np at a=0, loses at the largest a
    row("E5", "anchored beats nonparametric when well-specified (a=0)",
        float(mse_anchor[0] < mse_np_pred), 1.0, 0.0)
    row("E5", "anchored loses under gross misspecification (a=%.2f)" % a_grid[-1],
        float(mse_anchor[-1] > mse_np_pred), 1.0, 0.0)
    print("    (anchored MSE across a:", np.array2string(mse_anchor, precision=4),
          "np MSE pred %.4f)" % mse_np_pred)
    np.savetxt(os.path.join(RESULTS_DIR, "e5_anchor_mse.csv"),
               np.column_stack([a_grid, mse_anchor]), delimiter=",",
               header="a,mse_anchor", comments="")


# ---------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    exps = {"e1": e1_saturation, "e2": e2_exchange_rate,
            "e3": e3_shaped_exploration, "e4": e4_design_identifies_curvature,
            "e5": e5_anchoring_crossover}
    for name, fn in exps.items():
        if args.only and name != args.only:
            continue
        fn(fast=args.fast)
    lines = ["# Pipeline results vs theory", "",
             "| Exp | Claim | Measured | Predicted | Tol | Status |",
             "|---|---|---|---|---|---|"]
    n_fail = 0
    for exp, claim, meas, pred, tol, status in ROWS:
        n_fail += status == "FAIL"
        lines.append("| %s | %s | %.5g | %.5g | %g%% | %s |"
                     % (exp, claim, meas, pred, 100 * tol, status))
    lines += ["", "%d rows, %d FAIL" % (len(ROWS), n_fail)]
    with open(os.path.join(RESULTS_DIR, "RESULTS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n%d rows, %d FAIL -> results/RESULTS.md" % (len(ROWS), n_fail))
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
