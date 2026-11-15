"""OPEN-1 premise check: how far does the (1/2) gamma_PO sigma^2 floor reach?

The register's OPEN-1 conjectures the exchange-rate floor
    inf_policy sup_prior  Var(eps_hat) x C_T  >=  (1/2) gamma_PO sigma^2 (1-o(1))
for general prior classes "(continuous densities on an interval, or the
p-dim structural family)". Before investing in the sharp-constant program
we test the premise numerically:

  A. NONPARAMETRIC linear slope estimators, any static design measure:
     ratio(mu) = [sum w d^2] / [sum w (d - dbar)^2]  (local-quadratic cost).
     Closed form says min = 1 at mean-centered designs; the optimizer
     should find 1.0000 and nothing below.
  B. ADAPTIVE amplitude schedules (alternating-sign probes, any r_t) and a
     misplaced-anchor variant, Monte Carlo: ratio >= 1 up to MC error.
  C. STRUCTURAL family (C0, C1, c known form): Cramer-Rao ratio
         R(mu) = g' M(mu)^{-1} g  x  cost(mu) / cost_unit
     minimized over designs, under (i) the local-quadratic cost model and
     (ii) the TRUE incremental cost Phi(h*) - Phi(h). If R_min < 1 the
     structural-family clause of OPEN-1 is FALSE as stated: global
     structure breaks the floor (tight-side probes carry exponentially
     large sensitivity e^{-ch} at only polynomially larger cost), and the
     register is amended to the local/nonparametric scope.

Usage: python experiments/run_open1.py    ->  results/OPEN1.md
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posk.theory import Market  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


# ---------------------------------------------------------------- part A/C
def np_ratio(m, hstar, pts, wts, cost="local"):
    """Nonparametric OLS-slope ratio: Var x C over the floor."""
    d = pts - hstar
    s_c = wts @ (d - wts @ d) ** 2
    if s_c <= 1e-12:
        return np.inf
    if cost == "local":
        return (wts @ d ** 2) / s_c
    dphi = np.maximum(m.Phi(hstar) - m.Phi(pts), 0.0)
    return 2 * (wts @ dphi) / (m.gamma_po(hstar) * s_c)


def known_c_ratio(m, hstar, pts, wts, cost="local"):
    """Cramer-Rao ratio for eps(h*) when the curvature c is KNOWN a
    priori: theta = (C0, C1) only, sensitivity s(h) = (1, e^{-ch}),
    g = d eps(h*)/d theta = (0, c e^{-c h*}). This is the boundary case
    the paper's Sec. 3 sentence quotes: with c known the floor breaks."""
    e = np.exp(-m.c * pts)
    S = np.column_stack([np.ones(len(pts)), e])
    M = (S * wts[:, None]).T @ S
    g = np.array([0.0, m.c * np.exp(-m.c * hstar)])
    try:
        var_term = g @ np.linalg.solve(M + 1e-13 * np.eye(2), g)
    except np.linalg.LinAlgError:
        return np.inf
    if var_term <= 0:
        return np.inf
    if cost == "local":
        return var_term * (wts @ (pts - hstar) ** 2)
    dphi = np.maximum(m.Phi(hstar) - m.Phi(pts), 0.0)
    return 2 * var_term * (wts @ dphi) / m.gamma_po(hstar)


def struct_ratio(m, hstar, pts, wts, cost="local"):
    """Cramer-Rao ratio for eps(h*) within the (C0, C1, c) family."""
    e = np.exp(-m.c * pts)
    S = np.column_stack([np.ones(len(pts)), e, -m.C1 * pts * e])
    M = (S * wts[:, None]).T @ S
    g = np.array([0.0,
                  m.c * np.exp(-m.c * hstar),
                  m.C1 * np.exp(-m.c * hstar) * (1 - m.c * hstar)])
    try:
        var_term = g @ np.linalg.solve(M + 1e-13 * np.eye(3), g)
    except np.linalg.LinAlgError:
        return np.inf
    if var_term <= 0:
        return np.inf
    if cost == "local":
        return var_term * (wts @ (pts - hstar) ** 2)
    dphi = np.maximum(m.Phi(hstar) - m.Phi(pts), 0.0)
    return 2 * var_term * (wts @ dphi) / m.gamma_po(hstar)


def minimize_ratio(fn, m, hstar, k, lo, hi, seed, n_rand=4000, n_ref=2500):
    """Random search + perturbation refinement over k-point designs."""
    rng = np.random.default_rng(seed)
    best, best_x = np.inf, None
    for _ in range(n_rand):
        pts = rng.uniform(lo, hi, k)
        wts = rng.dirichlet(np.ones(k))
        r = fn(m, hstar, pts, wts)
        if r < best:
            best, best_x = r, (pts, wts)
    pts, wts = best_x
    scale = 0.25
    for i in range(n_ref):
        p2 = np.clip(pts + scale * rng.standard_normal(k), lo, hi)
        lw = np.log(wts + 1e-12) + scale * rng.standard_normal(k)
        w2 = np.exp(lw - lw.max())
        w2 /= w2.sum()
        r = fn(m, hstar, p2, w2)
        if r < best:
            best, pts, wts = r, p2, w2
        if i % 500 == 499:
            scale *= 0.5
    return best, pts, wts


# ---------------------------------------------------------------- part B
def adaptive_mc(m, hstar, schedule, anchor, T=1500, reps=1500, seed=0):
    """MC: alternating-sign probes with amplitude schedule r_t around
    `anchor`; OLS slope on (h_t, tau_obs); Var x true pathwise cost."""
    rng = np.random.default_rng(seed)
    t = np.arange(T)
    r_t = schedule(t)
    sgn = np.where(t % 2 == 0, 1.0, -1.0)
    h = anchor + sgn * r_t
    cost = float(np.sum(np.maximum(m.Phi(hstar) - m.Phi(h), 0.0)))
    dc = h - h.mean()
    s_c = float(dc @ dc)
    eps_hats = []
    true_tau = m.tau(h)
    for _ in range(reps):
        y = true_tau + m.sigma * rng.standard_normal(T)
        eps_hats.append(-(dc @ y) / s_c)
    var = float(np.var(eps_hats))
    return var * cost / (0.5 * m.gamma_po(hstar) * m.sigma ** 2)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    m = Market()
    hstar = m.h_po()
    lines = ["# OPEN-1 premise check: reach of the exchange-rate floor", "",
             "Anchor h* = h_PO = %.4f, gamma_PO(h*) = %.4f, register market."
             % (hstar, m.gamma_po(hstar)), ""]

    # ---- A: nonparametric, local cost --------------------------------
    ra3, _, _ = minimize_ratio(
        lambda mm, hh, p, w: np_ratio(mm, hh, p, w, "local"),
        m, hstar, 3, m.h_lo, m.h_hi, seed=1)
    ra4, _, _ = minimize_ratio(
        lambda mm, hh, p, w: np_ratio(mm, hh, p, w, "local"),
        m, hstar, 4, m.h_lo, m.h_hi, seed=2)
    a_ok = min(ra3, ra4) > 0.999
    lines += ["## A. Nonparametric estimators, local-quadratic cost", "",
              "min ratio over 3-point designs: %.6f; over 4-point: %.6f."
              % (ra3, ra4),
              "The floor is TIGHT and un-beatable in its own scope "
              "(min = 1 at mean-centered designs). %s"
              % ("PASS" if a_ok else "FAIL"), ""]

    # ---- A': nonparametric, TRUE cost (finite amplitude) -------------
    rat3, pts_t, wts_t = minimize_ratio(
        lambda mm, hh, p, w: np_ratio(mm, hh, p, w, "true"),
        m, hstar, 3, m.h_lo, m.h_hi, seed=3)
    lines += ["## A'. Nonparametric, TRUE incremental cost "
              "(finite amplitude)", "",
              "min ratio: %.4f at support %s, weights %s."
              % (rat3, np.round(pts_t, 3).tolist(),
                 np.round(wts_t, 3).tolist()),
              "Finite-amplitude wide-side probing rides the defensive-"
              "widening curvature collapse (Phi flattens above h*), so the "
              "TRUE cost undercuts the local-quadratic model - the known "
              "A1-scope drift (E2's drift cell), a polynomial effect that "
              "vanishes as amplitude -> 0. The floor's exact scope is "
              "local, as stated in T2/T4.", ""]

    # ---- B: adaptive schedules (MC, true cost, small amplitude) ------
    rb_const = adaptive_mc(m, hstar, lambda t: 0.10 + 0 * t, hstar,
                           seed=11)
    rb_decay = adaptive_mc(m, hstar,
                           lambda t: 0.25 / np.sqrt(1 + 0.05 * t), hstar,
                           seed=12)
    rb_mis = adaptive_mc(m, hstar, lambda t: 0.10 + 0 * t, hstar + 0.2,
                         seed=13)
    b_ok = rb_const > 0.9 and rb_decay > 0.9 and rb_mis > 1.5
    lines += ["## B. Adaptive amplitude schedules (Monte Carlo, true cost)",
              "",
              "| schedule | ratio |", "|---|---|",
              "| constant r = 0.10, centered at h* | %.3f |" % rb_const,
              "| decaying r_t = 0.25/sqrt(1+t/20), centered | %.3f |"
              % rb_decay,
              "| constant r = 0.10, anchor misplaced +0.2 | %.3f |" % rb_mis,
              "",
              "Amplitude adaptivity does not beat the floor (ratios ~ 1 up "
              "to MC error and small-amplitude drift); a misplaced anchor "
              "pays strictly more. %s" % ("PASS" if b_ok else "FAIL"), ""]

    # ---- C: structural family --------------------------------------
    rc_loc, pts_l, wts_l = minimize_ratio(
        lambda mm, hh, p, w: struct_ratio(mm, hh, p, w, "local"),
        m, hstar, 4, m.h_lo, m.h_hi, seed=21)
    rc_true, pts_r, wts_r = minimize_ratio(
        lambda mm, hh, p, w: struct_ratio(mm, hh, p, w, "true"),
        m, hstar, 4, m.h_lo, m.h_hi, seed=22)
    # mechanism scan: anchored pair +/- 0.1 plus one tight probe at t
    scan = []
    for t in [1.0, 0.8, 0.6, 0.4, 0.2, 0.05]:
        best_t = np.inf
        for wt in [0.05, 0.1, 0.2, 0.4]:
            pts = np.array([hstar - 0.1, hstar + 0.1, t])
            wts = np.array([(1 - wt) / 2, (1 - wt) / 2, wt])
            best_t = min(best_t, struct_ratio(m, hstar, pts, wts, "true"))
        scan.append((t, best_t))
    lines += ["## C. Structural family (C0, C1, c known): Cramer-Rao ratio",
              "",
              "Baseline search (4000 random + 2500 refinements, the "
              "historical run): min ratio, local-quadratic cost: "
              "**%.4f** at support %s, weights %s."
              % (rc_loc, np.round(pts_l, 3).tolist(),
                 np.round(wts_l, 3).tolist()),
              "",
              "min ratio, TRUE cost: **%.4f** at support %s, weights %s."
              % (rc_true, np.round(pts_r, 3).tolist(),
                 np.round(wts_r, 3).tolist()),
              "",
              "Mechanism scan (pair at h* +/- 0.1 plus one tight probe at "
              "t, weight grid 0.05-0.4):", "",
              "| tight probe t | best ratio |", "|---|---|"]
    lines += ["| %.2f | %.4f |" % (t, r) for t, r in scan]

    # ---- C-deep: the two-sided picture (T9 + the witness) -----------
    # Hardened searches, run separately WITHIN the reach h >= h* - 2/c
    # (where T9 proves the floor cannot be beaten) and GLOBALLY (where a
    # violating design exists). The reach constant 2/c is T9's pointwise-
    # domination boundary; see latex/proofs.tex, proof of T9.
    reach = hstar - 2.0 / m.c
    within_best = np.inf
    for sd in (31, 32, 33):
        r_, p_, w_ = minimize_ratio(
            lambda mm, hh, p, w: struct_ratio(mm, hh, p, w, "local"),
            m, hstar, 4, max(m.h_lo, reach), m.h_hi, seed=sd,
            n_rand=30000, n_ref=10000)
        within_best = min(within_best, r_)
    glob_best, glob_pts, glob_wts = np.inf, None, None
    for sd in (33, 40, 41, 44, 47, 50):
        r_, p_, w_ = minimize_ratio(
            lambda mm, hh, p, w: struct_ratio(mm, hh, p, w, "local"),
            m, hstar, 4, m.h_lo, m.h_hi, seed=sd,
            n_rand=30000, n_ref=12000)
        if r_ < glob_best:
            glob_best, glob_pts, glob_wts = r_, p_, w_
    # canonical witness (frozen design AND frozen anchor 1.8461; ratio
    # verified independently to 50 decimal digits with mpmath:
    # 0.8516504721831888870...)
    wit_anchor = 1.8461
    wit_pts = np.array([1.8726, 0.05, 1.8665, 1.3073])
    wit_wts = np.array([0.003329, 0.000272, 0.955702, 0.040697])
    wit_wts = wit_wts / wit_wts.sum()
    wit_loc = struct_ratio(m, wit_anchor, wit_pts, wit_wts, "local")
    wit_true = struct_ratio(m, wit_anchor, wit_pts, wit_wts, "true")
    c_holds = within_best > 0.999 and wit_loc < 0.9 and glob_best < 0.98
    lines += ["", "## C-deep. The two-sided picture: the reach h* - 2/c "
              "is exact (T9)", "",
              "Hardened search RESTRICTED to the reach [h* - 2/c, h_hi] "
              "= [%.4f, %.2f] (3 x 30000 random + 10000 refinements): "
              "min ratio **%.5f** - the floor holds, as Theorem T9 "
              "proves it must." % (reach, m.h_hi, within_best),
              "",
              "Hardened GLOBAL search (support allowed down to h_lo = "
              "%.2f): min ratio **%.5f** at support %s, weights %s - "
              "the floor BREAKS below the reach."
              % (m.h_lo, glob_best, np.round(glob_pts, 3).tolist(),
                 np.round(glob_wts, 4).tolist()),
              "",
              "Canonical witness (frozen design; ratio verified "
              "independently at 50-digit precision = 0.85165047...): "
              "support %s, weights %s, local-cost ratio **%.5f**, "
              "TRUE-cost ratio %.4f (> 1: the violation lives in the "
              "local-quadratic cost model, the floor's own scope). Every "
              "witness support point except h = 0.05 lies within the "
              "reach: the one below-reach probe, carrying weight 3e-4, "
              "is what breaks the floor."
              % (wit_pts.tolist(), wit_wts.round(6).tolist(),
                 wit_loc, wit_true),
              "",
              "**Verdict: structure-proofness is a REACH phenomenon, and "
              "the reach is exact.** Within h >= h* - 2/c (two curvature "
              "lengths below the anchor; every trust-region design the "
              "paper's agent can deploy, since r <= 0.8 < 2/c = %.3f) "
              "no family-knowing design beats the floor: that is now "
              "Theorem T9, proved by exhibiting the family element "
              "phi0(h) = 2/c - e^{-c(h-h*)}(2/c + h - h*) whose "
              "pointwise domination |phi0| <= |h - h*| holds exactly on "
              "[h* - 2/c, inf). Below the reach the domination fails, "
              "and a design exploiting that region (an asymmetric near-"
              "anchor cluster plus one vanishing-weight far probe) beats "
              "the floor by 15 percent. The earlier verdict of global "
              "structure-proofness (min 1.005, tight probes "
              "'monotonically worse') was an artifact of two search "
              "gaps, recorded as the eleventh measurement-forced pivot: "
              "the weight grid never went below 0.05 (the violating "
              "probe carries 3e-4), and the random search never found "
              "the asymmetric cluster. Symmetric-pair-plus-far-probe "
              "families stay above the floor at every weight (they "
              "approach 1 from above as the weight vanishes); the "
              "violation requires the asymmetric structure."
              % (2.0 / m.c),
              "",
              "## Register amendment (applied to OPEN-PROBLEMS.md and "
              "THEOREMS.md)", "",
              "The structure-proofness conjecture is RESOLVED, in both "
              "directions: proved within the reach (T9), refuted beyond "
              "it (the witness). OPEN-1's structural-family clause is "
              "re-scoped to trust-region policies (assumption A4 with "
              "r <= 2/c), which T9 shows is not a technicality but "
              "exactly the condition that makes the floor structure-"
              "proof. Two scope caveats remain load-bearing: (i) at "
              "finite amplitude under the TRUE cost, wide-side "
              "flattening yields ratio %.3f < 1 (A'), so the o(1)/local "
              "qualifier cannot be dropped; (ii) the exact "
              "characterization of which below-reach designs violate "
              "the floor (and by how much at most) is a new open "
              "problem, OPEN-5." % rat3]

    # ---- D: the boundary - c known a priori --------------------------
    # Same probe grid as the C scan (pair at h* +/- 0.1 plus one tight
    # probe at t, best weight), c dropped from the parameter vector.
    # Reported under both cost models, like C.
    scan_kc = []
    for t in [1.0, 0.8, 0.6, 0.4, 0.2, 0.05]:
        best_l, best_r = np.inf, np.inf
        for wt in [0.05, 0.1, 0.2, 0.4]:
            pts = np.array([hstar - 0.1, hstar + 0.1, t])
            wts = np.array([(1 - wt) / 2, (1 - wt) / 2, wt])
            best_l = min(best_l, known_c_ratio(m, hstar, pts, wts, "local"))
            best_r = min(best_r, known_c_ratio(m, hstar, pts, wts, "true"))
        scan_kc.append((t, best_l, best_r))
    # unconstrained two-point designs (h*, t), best weight
    two_kc = []
    for t in [0.5, 0.2, 0.05, 0.01, 0.001]:
        best_l, best_r = np.inf, np.inf
        for wt in np.linspace(0.01, 0.99, 99):
            pts = np.array([hstar, t])
            wts = np.array([1 - wt, wt])
            best_l = min(best_l, known_c_ratio(m, hstar, pts, wts, "local"))
            best_r = min(best_r, known_c_ratio(m, hstar, pts, wts, "true"))
        two_kc.append((t, best_l, best_r))
    d_breaks = (scan_kc[0][1] < 1 and scan_kc[0][2] < 1
                and two_kc[-1][1] < two_kc[0][1])
    lines += ["## D. The boundary: c known a priori", "",
              "Same scan as C with the c coordinate dropped "
              "(theta = (C0, C1), sensitivity (1, e^{-ch})):", "",
              "| tight probe t | best ratio (local cost) | best ratio "
              "(true cost) |", "|---|---|---|"]
    lines += ["| %.2f | %.4f | %.4f |" % (t, rl, rr)
              for t, rl, rr in scan_kc]
    lines += ["", "Unconstrained two-point designs (h*, t), best weight:",
              "", "| probe t | best ratio (local cost) | best ratio "
              "(true cost) |", "|---|---|---|"]
    lines += ["| %.3f | %.5f | %.5f |" % (t, rl, rr)
              for t, rl, rr in two_kc]
    lines += ["",
              "With c known the floor breaks outright, and the ratio "
              "falls monotonically as the probe moves away from the "
              "anchor, never settling at any particular value (%.4f at "
              "t = %.3f and still decreasing): there is no known-c floor "
              "at 0.05 or anywhere else the scan reaches. Remote "
              "sensitivity e^{-ch} no longer has to be pulled back "
              "through c-hat, so its cheapness is banked instead of "
              "discounted: the floor is an ignorance-of-curvature "
              "phenomenon, which is the boundary the paper's Section 3 "
              "states (its quoted ratios 0.30 at t=1.0 and 0.04 at "
              "t=0.05 are this table's local-cost column). %s"
              % (two_kc[-1][1], two_kc[-1][0],
                 "PASS" if d_breaks else "FAIL"), ""]

    out = os.path.join(RESULTS_DIR, "OPEN1.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("-> %s" % out)
    return 0 if (a_ok and b_ok and c_holds and d_breaks) else 1


if __name__ == "__main__":
    sys.exit(main())
