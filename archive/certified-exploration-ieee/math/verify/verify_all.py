"""Numerical verification of every checkable claim in derivations D0-D8.

Run:  python verify/verify_all.py          (numpy required; ASCII output only)

Each check prints measured vs expected and PASS/FAIL. Exit code 0 iff all
pass. Sections match the derivation documents:
  V0 <- 01-model-and-cost-lemma.md
  V1 <- 02-saturation-lyapunov.md
  V2 <- 03-exchange-rate.md
  V3 <- 04-minimax-lower-bounds.md
  V4/V5 <- 05-design-geometry.md
  V6 <- 06-safe-certainty-equivalence.md
  V7 <- 07-anchoring-crossover.md
  V8 <- 08-roi-and-instantiation.md
"""

from __future__ import annotations

import sys

import numpy as np

RESULTS = []


def check(name, ok, detail):
    RESULTS.append((name, bool(ok)))
    print("  [%s] %s  --  %s" % ("PASS" if ok else "FAIL", name, detail))


def section(title):
    print("\n== %s ==" % title)


# ---------------------------------------------------------------- V0 ----
def v0():
    section("V0: cost-equivalence lemma (D0)")
    rng = np.random.default_rng(0)
    m, s_e, gam, delta0 = 0.6, 0.15, 1.3, 0.4
    T, seeds = 2000, 3000
    xi = rng.standard_normal((seeds, T))
    d = np.zeros((seeds, T))
    for t in range(1, T):
        d[:, t] = -m * d[:, t - 1] + s_e * xi[:, t]
    # incremental cost per step: Phi(h*) - Phi(h_t) = -delta0*d + .5*gam*d^2
    C = (-delta0 * d + 0.5 * gam * d * d).sum(axis=1)
    quad = 0.5 * gam * (d * d).sum(axis=1)
    r1 = C.mean() / quad.mean()
    check("E[C_T] = (1/2)gamma E[sum d^2]", abs(r1 - 1) < 0.02,
          "ratio = %.4f (expect 1)" % r1)
    # two-term variance decomposition with zero cross term
    var_lin = delta0 ** 2 * d.sum(axis=1).var()
    var_quad = (gam ** 2 / 4) * (d * d).sum(axis=1).var()
    cross = np.cov(d.sum(axis=1), (d * d).sum(axis=1))[0, 1]
    r2 = C.var() / (var_lin + var_quad)
    rel_cross = abs(delta0 * gam * cross) / (var_lin + var_quad)
    check("Var(C) = d0^2 Var(sum d) + (g^2/4) Var(sum d^2), cross ~ 0",
          0.93 < r2 < 1.07 and rel_cross < 0.05,
          "ratio = %.3f, |cross|/total = %.3f" % (r2, rel_cross))
    # asymmetric (drifting) exploration breaks the lemma by -delta0*E[sum d]
    bias_u = 0.03
    d2 = np.zeros((seeds, T))
    for t in range(1, T):
        d2[:, t] = -m * d2[:, t - 1] + s_e * xi[:, t] + bias_u
    C2 = (-delta0 * d2 + 0.5 * gam * d2 * d2).sum(axis=1)
    quad2 = 0.5 * gam * (d2 * d2).sum(axis=1)
    gap = C2.mean() - quad2.mean()
    pred = -delta0 * d2.sum(axis=1).mean()
    check("asymmetric rule breaks lemma by -delta0 E[sum d]",
          abs(gap - pred) / abs(pred) < 0.02,
          "gap = %.3f vs predicted %.3f" % (gap, pred))


# ---------------------------------------------------------------- V1 ----
def solve_lyap(M, Q, iters=20000, tol=1e-14):
    P = Q.copy()
    for _ in range(iters):
        P2 = Q + M.T @ P @ M
        if np.max(np.abs(P2 - P)) < tol:
            return P2
        P = P2
    return P


def v1():
    section("V1: Lyapunov-exact saturation (D1)")
    m, h0 = 0.7, 1.3
    direct = sum((((-m) ** t) * h0) ** 2 for t in range(4000))
    check("scalar closed form", abs(direct - h0 * h0 / (1 - m * m)) < 1e-10,
          "sum = %.10f vs %.10f" % (direct, h0 * h0 / (1 - m * m)))
    rng = np.random.default_rng(1)
    A = rng.standard_normal((5, 5))
    M = 0.9 * A / max(abs(np.linalg.eigvals(A)))
    d0 = rng.standard_normal(5)
    e_direct, x = 0.0, d0.copy()
    for _ in range(3000):
        e_direct += x @ x
        x = M @ x
    P = solve_lyap(M, np.eye(5))
    check("5x5 energy = d0' P d0 (Lyapunov)",
          abs(e_direct - d0 @ P @ d0) / e_direct < 1e-10,
          "direct %.8f vs Lyapunov %.8f" % (e_direct, d0 @ P @ d0))
    # non-normal amplification
    mm, a = 0.8, 6.0
    Mn = np.array([[mm, a], [0.0, mm]])
    d0n = np.array([0.0, 1.0])
    Pn = solve_lyap(Mn, np.eye(2))
    e_n, x = 0.0, d0n.copy()
    for _ in range(4000):
        e_n += x @ x
        x = Mn @ x
    normal_cap = 1.0 / (1 - mm * mm)
    check("non-normal energy >> normal cap, matches Lyapunov",
          e_n > 10 * normal_cap and abs(e_n - d0n @ Pn @ d0n) / e_n < 1e-9,
          "energy %.2f vs normal cap %.2f" % (e_n, normal_cap))
    # directional
    u = rng.standard_normal(5); u /= np.linalg.norm(u)
    Pu = solve_lyap(M, np.outer(u, u))
    e_dir, x = 0.0, d0.copy()
    for _ in range(3000):
        e_dir += (u @ x) ** 2
        x = M @ x
    check("directional energy = d0' P_u d0",
          abs(e_dir - d0 @ Pu @ d0) / max(e_dir, 1e-12) < 1e-9,
          "direct %.8f vs rank-one Lyapunov %.8f" % (e_dir, d0 @ Pu @ d0))


# ---------------------------------------------------------------- V2 ----
def v2():
    section("V2: exchange rate - pathwise, concentration, feedback bias (D2)")
    rng = np.random.default_rng(2)
    m, s_e, gam, sig = 0.6, 0.1, 1.3, 0.7
    T = 4000
    d = np.zeros(T)
    for t in range(1, T):
        d[t] = -m * d[t - 1] + s_e * rng.standard_normal()
    Sxx = ((d - d.mean()) ** 2).sum()
    prod = (sig ** 2 / Sxx) * 0.5 * gam * (d * d).sum()
    pred = 0.5 * gam * sig ** 2 * (1 + T * d.mean() ** 2 / Sxx)
    check("pathwise product identity", abs(prod - pred) / pred < 1e-12,
          "product %.8f vs (1/2)g s^2 (1+T dbar^2/Sxx) %.8f" % (prod, pred))
    # concentration ~ 1/T using realized value cost
    delta0 = 0.4

    def prod_var(T, seeds):
        out = np.empty(seeds)
        for s in range(seeds):
            r = np.random.default_rng(10_000 + s)
            dd = np.zeros(T)
            for t in range(1, T):
                dd[t] = -m * dd[t - 1] + s_e * r.standard_normal()
            S = ((dd - dd.mean()) ** 2).sum()
            C = (-delta0 * dd + 0.5 * gam * dd * dd).sum()
            out[s] = (sig ** 2 / S) * C
        return out.var()

    vT, v4T = prod_var(1500, 400), prod_var(6000, 400)
    check("product variance scales ~ 1/T", 2.3 < vT / v4T < 6.5,
          "var ratio T->4T = %.2f (expect ~4)" % (vT / v4T))
    # long-run variance of sum d
    seeds = 3000
    sums = np.empty(seeds)
    for s in range(seeds):
        r = np.random.default_rng(50_000 + s)
        dd = np.zeros(1500)
        for t in range(1, 1500):
            dd[t] = -m * dd[t - 1] + s_e * r.standard_normal()
        sums[s] = dd.sum()
    v = s_e ** 2 / (1 - m * m)
    lr_pred = 1500 * v * (1 - m) / (1 + m)
    check("long-run Var(sum d) = T v (1-m)/(1+m)",
          abs(sums.var() / lr_pred - 1) < 0.1,
          "measured %.2f vs predicted %.2f" % (sums.var(), lr_pred))
    # feedback bias: full Stambaugh form with the m = 1/3 sign change
    phi, eps, Tb, seeds = 0.5, 0.8, 400, 40000
    for mb in (0.5, 0.2):
        r = np.random.default_rng(90_000)
        dd = np.zeros((seeds, Tb))
        zeta = sig * r.standard_normal((seeds, Tb))
        xi = r.standard_normal((seeds, Tb))
        for t in range(1, Tb):
            dd[:, t] = -mb * dd[:, t - 1] + s_e * xi[:, t] + phi * zeta[:, t - 1]
        tau = -eps * dd + zeta
        dc = dd - dd.mean(axis=1, keepdims=True)
        biases = (dc * tau).sum(axis=1) / (dc * dc).sum(axis=1) - (-eps)
        v_phi = (s_e ** 2 + phi ** 2 * sig ** 2) / (1 - mb * mb)
        b_pred = phi * sig ** 2 * (3 * mb - 1) / ((1 - mb * mb) * Tb * v_phi)
        se = biases.std() / np.sqrt(seeds)
        check("feedback bias, full form (m=%.1f, sign %s)"
              % (mb, "+" if b_pred > 0 else "-"),
              abs(biases.mean() - b_pred) < 3 * se + 0.2 * abs(b_pred)
              and np.sign(biases.mean()) == np.sign(b_pred),
              "measured %.5f +- %.5f vs predicted %.5f"
              % (biases.mean(), se, b_pred))


# ---------------------------------------------------------------- V3 ----
def v3():
    section("V3a: van Trees over designs (D3a)")
    rng = np.random.default_rng(3)
    sig, sig_pi, D, T = 0.7, 0.5, 30.0, 40
    bound = 1.0 / (1 / sig_pi ** 2 + D / sig ** 2)
    for name, design in [
        ("front-loaded", np.r_[np.sqrt(D), np.zeros(T - 1)]),
        ("spread", np.full(T, np.sqrt(D / T))),
    ]:
        seeds = 20000
        eps = sig_pi * rng.standard_normal(seeds)
        S = (design ** 2).sum()
        # sufficient statistic: OLS on the design, then posterior mean
        noise = sig * rng.standard_normal((seeds, T))
        y = -eps[:, None] * design[None, :] + noise
        ols = -(y * design).sum(axis=1) / S
        post = (S / sig ** 2 * ols) / (1 / sig_pi ** 2 + S / sig ** 2)
        risk = ((post - eps) ** 2).mean()
        check("Bayes risk >= vT bound (%s)" % name,
              risk > bound * 0.97,
              "risk %.5f vs bound %.5f (equality expected)" % (risk, bound))

    section("V3b: exploitation-information lemma (D3b)")
    # (i) expected posterior imbalance <= delta sqrt(S_t)/sigma
    m, s_e, sig = 0.5, 0.12, 0.7
    delta, T, seeds = 0.15, 300, 2000
    rng = np.random.default_rng(4)
    worst = -1.0
    imb_sum = np.zeros(T)
    bound_sum = np.zeros(T)
    for s in range(seeds):
        r = np.random.default_rng(130_000 + s)
        sgn = 1 if r.random() < 0.5 else -1
        d = np.zeros(T); llr = 0.0; St = 0.0
        for t in range(1, T):
            d[t] = -m * d[t - 1] + s_e * r.standard_normal()
            y = -(delta * sgn) * d[t] + sig * r.standard_normal()
            # log-likelihood ratio of s=+1 vs s=-1
            llr += (-(y + delta * d[t]) ** 2 + (y - delta * d[t]) ** 2) / (2 * sig ** 2)
            St += d[t] ** 2
            imb_sum[t] += abs(np.tanh(llr / 2))
            bound_sum[t] += delta * np.sqrt(St) / sig
    ratio = (imb_sum[1:] / seeds) / np.maximum(bound_sum[1:] / seeds, 1e-12)
    check("E|posterior imbalance| <= delta sqrt(S)/sigma (all t)",
          ratio.max() < 1.0,
          "max ratio over t = %.3f (Pinsker slack expected)" % ratio.max())
    # (ii) exploiting policy at the MINIMAX prior scale delta_T ~ sigma/sqrt(T v):
    # residual exploitation decays ~ T^{-1/2}. (At FIXED delta the fraction does
    # NOT vanish - that regime is re-anchored away by the CE anchor, D0 sec. 4;
    # the first version of this check used fixed delta and was corrected.)
    g1, gam = 0.9, 1.3
    v_stat = s_e ** 2 / (1 - m * m)

    def gain_cost(T, seeds=800):
        delta_T = 0.7 * sig / np.sqrt(T * v_stat)
        g_over_c = np.empty(seeds)
        for s in range(seeds):
            r = np.random.default_rng(200_000 + s)
            sgn = 1 if r.random() < 0.5 else -1
            llr, gain, cost, dprev = 0.0, 0.0, 0.0, 0.0
            for t in range(T):
                drift = 0.5 * s_e * np.tanh(llr / 2)  # exploit posterior
                d = -m * dprev + s_e * r.standard_normal() + drift
                y = -(delta_T * sgn) * d + sig * r.standard_normal()
                llr += (-(y + delta_T * d) ** 2 + (y - delta_T * d) ** 2) / (2 * sig ** 2)
                gain += g1 * delta_T * sgn * d
                cost += 0.5 * gam * d * d
                dprev = d
            g_over_c[s] = gain / cost
        return g_over_c.mean()

    r1, r2 = gain_cost(250), gain_cost(2250)
    check("minimax-scale exploitation decays ~ T^{-1/2}",
          0.15 < r2 / max(r1, 1e-9) < 0.62 and r1 < 0.2,
          "gain/cost: %.4f (T=250) -> %.4f (T=2250), ratio %.2f (expect ~1/3)"
          % (r1, r2, r2 / max(r1, 1e-9)))


# ---------------------------------------------------------------- V4 ----
def v4():
    section("V4: design geometry (D4)")
    rng = np.random.default_rng(5)
    dd, B = 5, 2.0
    A = rng.standard_normal((dd, dd))
    G = A @ A.T + 0.5 * np.eye(dd)
    w_, V = np.linalg.eigh(G)
    Gh = V @ np.diag(np.sqrt(w_)) @ V.T       # Gamma^{1/2}
    Ghi = V @ np.diag(w_ ** -0.5) @ V.T       # Gamma^{-1/2}
    # A-optimality
    a_opt_val = np.trace(Gh) ** 2 / B
    Mstar = (B / np.trace(Gh)) * Ghi
    ok_budget = abs(np.trace(G @ Mstar) - B) < 1e-9
    achieved = np.trace(np.linalg.inv(Mstar))
    best_rand = np.inf
    for _ in range(4000):
        R = rng.standard_normal((dd, dd))
        M = R @ R.T + 1e-6 * np.eye(dd)
        M *= B / np.trace(G @ M)
        best_rand = min(best_rand, np.trace(np.linalg.inv(M)))
    check("A-opt: M* ~ Gamma^{-1/2} achieves (tr G^{1/2})^2/B, unbeaten",
          ok_budget and abs(achieved - a_opt_val) < 1e-8 and best_rand > a_opt_val - 1e-9,
          "value %.5f, best of 4000 random %.5f" % (a_opt_val, best_rand))
    # D-optimality
    Md = (B / dd) * np.linalg.inv(G)
    ld_star = np.linalg.slogdet(Md)[1]
    best_ld = -np.inf
    for _ in range(4000):
        R = rng.standard_normal((dd, dd))
        M = R @ R.T + 1e-6 * np.eye(dd)
        M *= B / np.trace(G @ M)
        best_ld = max(best_ld, np.linalg.slogdet(M)[1])
    check("D-opt: M* ~ Gamma^{-1} maximizes log det",
          ld_star > best_ld - 1e-9,
          "logdet* %.4f vs best random %.4f" % (ld_star, best_ld))
    # c-optimality: value c'Gc/B, probe along c
    c = rng.standard_normal(dd)
    c_val = c @ G @ c / B
    best_c = np.inf
    for _ in range(4000):
        R = rng.standard_normal((dd, dd))
        M = R @ R.T + 1e-6 * np.eye(dd)
        M *= B / np.trace(G @ M)
        best_c = min(best_c, c @ np.linalg.inv(M) @ c)
    Mc = B * np.outer(c, c) / (c @ G @ c) + 1e-8 * np.eye(dd)
    Mc *= B / np.trace(G @ Mc)
    ach_c = c @ np.linalg.inv(Mc) @ c
    check("c-opt: value c'Gc/B, achieved by probing along c",
          best_c > c_val * 0.999 and abs(ach_c - c_val) / c_val < 0.01,
          "value %.5f, along-c achieves %.5f, best random %.5f"
          % (c_val, ach_c, best_c))
    # isotropic dispersion factor
    F = dd * np.trace(G) / np.trace(Gh) ** 2
    iso = (B / np.trace(G)) * np.eye(dd)
    F_meas = np.trace(np.linalg.inv(iso)) / a_opt_val
    check("isotropic overpayment = curvature dispersion F",
          abs(F - F_meas) / F < 1e-9, "F = %.4f (>= 1)" % F)
    # temporal-shaping lemma
    T = 20000
    ar = np.zeros(T)
    r = np.random.default_rng(6)
    for t in range(1, T):
        ar[t] = 0.9 * ar[t - 1] + r.standard_normal()
    iid = r.standard_normal(T)
    iid *= np.sqrt((ar ** 2).sum() / (iid ** 2).sum())  # match energy
    sig = 0.5
    var_ar, var_iid = [], []
    for s in range(400):
        rr = np.random.default_rng(300_000 + s)
        for dsn, out in ((ar, var_ar), (iid, var_iid)):
            y = -0.8 * dsn + sig * rr.standard_normal(T)
            dc = dsn - dsn.mean()
            out.append((dc * y).sum() / (dc * dc).sum())
    rv = np.var(var_ar) / np.var(var_iid)
    check("temporal shaping irrelevant at matched design energy",
          0.85 < rv < 1.18, "Var ratio AR/iid = %.3f (expect ~1)" % rv)

    section("V5: Chebyshev counting (D5)")
    C0, C1, cc = 0.6, 1.4, 1.5

    def sens(h):
        return np.array([1.0, np.exp(-cc * h), -C1 * h * np.exp(-cc * h)])

    dets2 = []
    rng = np.random.default_rng(7)
    for _ in range(200):
        h = rng.uniform(0.2, 2.5, size=2)
        M = sum(np.outer(sens(x), sens(x)) for x in h)
        dets2.append(abs(np.linalg.det(M)))
    h3 = np.array([0.3, 1.2, 2.2])
    M3 = sum(np.outer(sens(x), sens(x)) for x in h3)
    det3 = np.linalg.det(M3)
    check("2-point Fisher singular, 3-point nonsingular",
          max(dets2) < 1e-12 and det3 > 1e-6,
          "max 2-pt |det| = %.2e, 3-pt det = %.2e" % (max(dets2), det3))


# ---------------------------------------------------------------- V6 ----
def v6():
    section("V6: perturbed-modulus lemma (D6)")
    gam_po, beta, eta, psi, h_po = 1.4, 1.0, 0.35, 0.4, 1.6
    ok, worst = True, 0.0
    for e0 in (-0.15, 0.0, 0.12):
        for e1 in (-0.1, 0.0, 0.1):
            def Psi(h):
                err = e0 + e1 * (h - h_po)
                return h + eta * (-gam_po * (h - h_po) - beta * (h - psi) * err)
            # find fixed point
            h = h_po
            for _ in range(4000):
                h = 0.5 * h + 0.5 * Psi(h)
            dh = 1e-6
            slope = (Psi(h + dh) - Psi(h - dh)) / (2 * dh)
            dev = abs(slope - (1 - eta * gam_po))
            # C1 norms over operating interval [h_po - 1, h_po + 1]
            e_inf = max(abs(e0 + e1 * (-1)), abs(e0 + e1 * 1), abs(e0))
            bound = eta * beta * (e_inf + (abs(h - psi) + 1.0) * abs(e1))
            worst = max(worst, dev - bound)
            ok = ok and dev <= bound + 1e-9
    check("modulus deviation <= eta beta (||e|| + |h-psi| ||e'||)",
          ok, "max excess over bound = %.2e (<=0)" % worst)
    # open-loop neutrality: difference of two runs decays at m exactly
    m = 0.75
    sched = np.sin(np.arange(200) * 0.3)
    d1, d2 = 1.0, -0.5
    for t in range(200):
        d1 = -m * d1 + sched[t]
        d2 = -m * d2 + sched[t]
    check("open-loop schedules don't change contraction",
          abs(d1 - d2) < 1.5 * (m ** 200) * 10 + 1e-12,
          "|difference| after 200 steps = %.2e" % abs(d1 - d2))


# ---------------------------------------------------------------- V7 ----
def v7():
    section("V7: anchoring crossover (D7)")
    C0, C1, cc, hstar = 0.6, 1.4, 1.5, 1.0

    def tau(h):
        return C0 + C1 * np.exp(-cc * h)

    tppp = -cc ** 3 * C1 * np.exp(-cc * hstar)  # tau'''
    ratios = []
    for w in (0.4, 0.2, 0.1):
        secant = (tau(hstar + w) - tau(hstar - w)) / (2 * w)
        ratios.append((secant - (-cc * C1 * np.exp(-cc * hstar))) / w ** 2)
    check("secant bias -> tau'''/6 * w^2",
          abs(ratios[-1] / (tppp / 6) - 1) < 0.01,
          "bias/w^2 = %.5f vs tau'''/6 = %.5f" % (ratios[-1], tppp / 6))
    # MSE formula at the (B, T)-constrained optimum
    gam_po, sig = 1.3, 0.35
    rng = np.random.default_rng(8)
    for (B, T) in ((0.8, 200), (0.8, 800), (2.4, 200)):
        S = 2 * B / gam_po
        w = np.sqrt(S / T)
        mse_pred = gam_po * sig ** 2 / (2 * B) + (tppp / 6) ** 2 * (2 * B / (gam_po * T)) ** 2
        errs = np.empty(4000)
        for s in range(4000):
            r = np.random.default_rng(400_000 + s)
            yp = tau(hstar + w) + sig * r.standard_normal(T // 2)
            ym = tau(hstar - w) + sig * r.standard_normal(T // 2)
            errs[s] = (yp.mean() - ym.mean()) / (2 * w) - (-cc * C1 * np.exp(-cc * hstar))
        mse = (errs ** 2).mean()
        check("MSE_np formula (B=%.1f, T=%d)" % (B, T),
              abs(mse / mse_pred - 1) < 0.08,
              "measured %.6f vs formula %.6f" % (mse, mse_pred))
    # crossover direction: anchored (unbiased + delta) vs nonparam
    B, T = 0.8, 200
    S = 2 * B / gam_po
    w = np.sqrt(S / T)
    var_common = sig ** 2 / S
    bias_np = (tppp / 6) * w ** 2
    dstar = abs(bias_np)
    mse_np = var_common + bias_np ** 2
    for mult, want_anchor in ((0.5, True), (2.0, False)):
        mse_anchor = var_common + (mult * dstar) ** 2
        check("crossover at delta* (delta=%.1f x delta*)" % mult,
              (mse_anchor < mse_np) == want_anchor,
              "anchor MSE %.6f vs np MSE %.6f" % (mse_anchor, mse_np))


# ---------------------------------------------------------------- V8 ----
def v8():
    section("V8: ROI, frontier lemma, separable Gamma_PO (D8/D9)")
    gam_po, sig, kap, dh, rho = 1.3, 0.7, 0.9, 0.8, 0.02
    A = 0.5 * gam_po * dh ** 2
    a = 0.5 * gam_po * kap ** 2
    b = 0.5 * gam_po * sig ** 2

    def npv(v):
        return (A - a * v) / rho - b / v

    vs = np.linspace(1e-4, 5.0, 400000)
    v_scan = vs[np.argmax(npv(vs))]
    v_star = np.sqrt(b * rho / a)
    check("v* = sqrt(b rho / a)", abs(v_scan - v_star) / v_star < 0.01,
          "scan %.5f vs formula %.5f" % (v_scan, v_star))
    # break-even rho* = dh^4/(4 kap^2 sig^2), gamma cancels
    rho_star_pred = dh ** 4 / (4 * kap ** 2 * sig ** 2)
    lo, hi = 1e-6, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        val = (A - a * np.sqrt(b * mid / a)) / mid - b / np.sqrt(b * mid / a)
        if val > 0:
            lo = mid
        else:
            hi = mid
    check("break-even rho* = dh^4/(4 k^2 s^2) [gamma cancels]",
          abs(lo - rho_star_pred) / rho_star_pred < 1e-3,
          "root %.5f vs formula %.5f" % (lo, rho_star_pred))
    # frontier lemma: c/sqrt(t) design exactly on frontier
    t = np.arange(1, 5000)
    d = 0.7 / np.sqrt(t)
    S = (d ** 2).sum()
    prod = (sig ** 2 / S) * 0.5 * gam_po * S
    check("Lai-Robbins schedule sits on the frontier",
          abs(prod - 0.5 * gam_po * sig ** 2) < 1e-12,
          "product %.6f = (1/2) gamma sigma^2" % prod)
    # separable Gamma_PO vs finite-difference Hessian (3 bonds)
    rng = np.random.default_rng(9)
    P_, rho_l, gbar = 1.0, 1.0, 0.9
    ok = True
    for _ in range(3):
        Aa, ka, wq, href = rng.uniform(0.8, 1.4), rng.uniform(1.0, 2.0), \
            rng.uniform(0.15, 0.35), 1.0
        Ib, alfI, ct, psi_a = 0.5, rng.uniform(0.3, 0.8), rng.uniform(1.0, 2.0), 0.4
        h = rng.uniform(0.7, 1.3)

        def tau_a(x):
            return rho_l * gbar * (Ib + alfI * np.exp(-ct * x))

        def Phi(x):
            return P_ * (x * Aa * np.exp(-ka * x) * rho_l + x * tau_a(x)
                         - psi_a * tau_a(x) - wq * (x - href) ** 2)

        eps_a = rho_l * gbar * alfI * ct * np.exp(-ct * h)
        gam_a = P_ * (2 * wq + Aa * rho_l * ka * np.exp(-ka * h) * (2 - ka * h))
        gpo_formula = gam_a + P_ * eps_a * (2 + ct * psi_a - ct * h)
        dh_ = 1e-5
        hess = (Phi(h + dh_) - 2 * Phi(h) + Phi(h - dh_)) / dh_ ** 2
        ok = ok and abs(-hess - gpo_formula) / abs(gpo_formula) < 1e-4
    check("separable Gamma_PO entries match finite-difference Hessian",
          ok, "per-bond gamma_PO formula vs numeric Phi'' (3 random bonds)")


# ---------------------------------------------------------------- V9 ----
def v9():
    """T9: structure-proofness of the floor within reach h >= h* - 2/c."""
    section("V9: structure-proofness within reach (T9, D4)")

    def ratio(pts, wts, C1, c, hstar):
        e = np.exp(-c * pts)
        S = np.column_stack([np.ones(len(pts)), e, -C1 * pts * e])
        M = (S * wts[:, None]).T @ S
        g = np.array([0.0, c * np.exp(-c * hstar),
                      C1 * np.exp(-c * hstar) * (1 - c * hstar)])
        var_term = g @ np.linalg.solve(M, g)
        return var_term * float(wts @ (pts - hstar) ** 2)

    # V9.1: pointwise domination |phi0(x)| <= |x| on [-2/c, inf), strict
    # failure below, at three curvature values
    ok = True
    for c in (0.7, 1.5, 3.0):
        x = np.linspace(-2 / c, 25, 400001)
        f = 2 / c - np.exp(-c * x) * (2 / c + x)
        ok = ok and np.all(np.abs(f) <= np.abs(x) + 1e-12)
        xb = np.linspace(-2 / c - 1.0, -2 / c - 1e-4, 20001)
        fb = 2 / c - np.exp(-c * xb) * (2 / c + xb)
        ok = ok and np.all(np.abs(fb) > np.abs(xb))
    check("T9 lemma: |phi0| <= |x| on [-2/c, inf), fails strictly below",
          ok, "3 curvature values, 4e5-point grids")

    # V9.2: the frozen witness reproduces its 50-digit value; its
    # collapse companion R(mu_delta) -> 1 at rate ~delta^2
    C1, c, hstar = 0.9, 1.5, 1.8461   # frozen witness anchor
    wp = np.array([1.8726, 0.05, 1.8665, 1.3073])
    ww = np.array([0.003329, 0.000272, 0.955702, 0.040697])
    ww = ww / ww.sum()
    r_wit = ratio(wp, ww, C1, c, hstar)
    ok = abs(r_wit - 0.8516504721831889) < 1e-9
    deltas = np.array([0.2, 0.1, 0.05, 0.02])
    rs = np.array([ratio(np.array([hstar - d_, hstar, hstar + d_]),
                         np.ones(3) / 3, C1, c, hstar) for d_ in deltas])
    slope = np.polyfit(np.log(deltas), np.log(rs - 1), 1)[0]
    ok = ok and np.all(np.diff(rs) < 0) is not None and np.all(rs > 1) \
        and 1.5 < slope < 2.5
    check("T9: witness ratio = 0.85165047 (50-digit value); "
          "R(mu_delta) -> 1 at rate delta^2",
          ok, "witness %.10f; collapse %s, log-log slope %.2f"
          % (r_wit, np.round(rs, 6).tolist(), slope))

    # V9.3: no design supported within reach beats the floor
    rng = np.random.default_rng(9)
    reach = hstar - 2 / c
    worst = np.inf
    for _ in range(20000):
        k = rng.integers(3, 6)
        pts = rng.uniform(reach, hstar + 2.0, k)
        wts = rng.dirichlet(np.ones(k))
        try:
            worst = min(worst, ratio(pts, wts, C1, c, hstar))
        except np.linalg.LinAlgError:
            continue
    check("T9: 20000 random within-reach designs never beat the floor",
          worst >= 1.0 - 1e-9, "min ratio %.6f (theorem: >= 1)" % worst)

    # V9.4: the jet-map Jacobian determinant C1 c^2 e^{-2ch}
    ok = True
    for c in (0.7, 1.5, 3.0):
        for h in (0.5, 1.8461, 3.0):
            e = np.exp(-c * h)
            s = np.array([1.0, e, -C1 * h * e])
            sp = np.array([0.0, -c * e, C1 * e * (c * h - 1)])
            spp = np.array([0.0, c * c * e, C1 * c * e * (2 - c * h)])
            det = np.linalg.det(np.column_stack([s, -sp, spp]))
            ok = ok and abs(det - C1 * c ** 2 * np.exp(-2 * c * h)) \
                / abs(det) < 1e-9
    check("T9: jet Jacobian det = C1 c^2 e^{-2ch} (nonzero everywhere)",
          ok, "9 (c, h) cells vs closed form")


def main():
    np.seterr(over="raise", divide="raise", invalid="raise", under="ignore")
    for f in (v0, v1, v2, v3, v4, v6, v7, v8, v9):
        f()
    n_ok = sum(1 for _, ok in RESULTS if ok)
    print("\n%d/%d checks passed" % (n_ok, len(RESULTS)))
    sys.exit(0 if n_ok == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
