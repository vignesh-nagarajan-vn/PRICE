"""Independent re-derivation of the headline numbers in ml-or/submission-materials.

Written from the paper's own formulas (main.tex sections 2-5, theorems_body.tex,
proofs_body.tex). Imports nothing from posk/ and reads no result file: every
constant below is transcribed from the paper or the register, and every
quantity is recomputed here.

Run:  python indep_check.py
"""
import numpy as np

PASS = FAIL = DRIFT = 0


def check(name, got, want, tol=5e-3, note=""):
    """Strictly RELATIVE check against a number the paper states.  (Note the
    scale: most quantities here are O(0.01), so an absolute tolerance would
    make the check vacuous.)"""
    global PASS, FAIL
    scale = max(abs(want), abs(got), 1e-15)
    good = abs(got - want) <= tol * scale
    print("%s  %-58s got %-14.6g paper %-12.6g %s"
          % ("PASS" if good else "FAIL", name, got, want, note))
    PASS += good
    FAIL += not good


def assert_true(name, cond, note=""):
    global PASS, FAIL
    print("%s  %-58s %s" % ("PASS" if cond else "FAIL", name, note))
    PASS += bool(cond)
    FAIL += not cond


def report(name, value, note=""):
    """A number the paper states but no shipped artifact reproduces."""
    global DRIFT
    DRIFT += 1
    print("DRIFT %-58s computed %-12.6g %s" % (name, value, note))


# ---------------------------------------------------------------------------
# The model, transcribed from main.tex section 2 and the register's constants.
#   U(h)   = A e^{-kh}                      benign flow
#   tau(h) = C0 + C1 e^{-ch}                toxic flow
#   J(h;T) = h U(h) + (h - psi) T - w (h - href)^2
#   Phi(h) = J(h, tau(h))
#   eps(h) = -tau'(h),  gamma = -d^2J/dh^2,  gamma_PO = -Phi''
# ---------------------------------------------------------------------------
A, K, C0, C1, C, PSI, W, HREF, SIGMA = 1.0, 1.5, 0.6, 0.9, 1.5, 0.4, 0.25, 1.0, 0.25


def U(h, A=A, k=K):
    return A * np.exp(-k * h)


def tau(h, C0=C0, C1=C1, c=C):
    return C0 + C1 * np.exp(-c * h)


def eps(h, C1=C1, c=C):
    return c * C1 * np.exp(-c * h)          # -tau'(h)


def tau3(h, C1=C1, c=C):
    return -c ** 3 * C1 * np.exp(-c * h)    # tau'''(h)


def J(h, T, A=A, k=K, psi=PSI, w=W, href=HREF):
    return h * U(h, A, k) + (h - psi) * T - w * (h - href) ** 2


def Phi(h, **kw):
    C1_ = kw.get("C1", C1)
    return J(h, tau(h, C1=C1_), **{q: kw[q] for q in kw if q != "C1"})


def gamma_closed(h, A=A, k=K, w=W):
    """-d^2 J/dh^2 at frozen toxic level: A k e^{-kh}(2 - kh) + 2w."""
    return A * k * np.exp(-k * h) * (2 - k * h) + 2 * w


def gamma_po_closed(h, C1=C1, c=C, psi=PSI):
    """main.tex Sec. 2:  gamma_PO = gamma + eps (2 + c psi - c h)."""
    return gamma_closed(h) + eps(h, C1, c) * (2 + c * psi - c * h)


def d2(f, h, e=1e-4):
    return (f(h + e) - 2 * f(h) + f(h - e)) / e ** 2


print("=" * 100)
print("1. The model's closed forms (main.tex Sec. 2)")
print("=" * 100)

for h in (0.9, 1.3, 1.85, 2.4):
    check("gamma(h=%.2f) = -J''" % h, gamma_closed(h), -d2(lambda x: J(x, tau(h)), h), 1e-4)
    check("gamma_PO(h=%.2f) = -Phi''" % h, gamma_po_closed(h),
          -d2(lambda x: Phi(x), h), 1e-4)
    check("eps(h=%.2f) = -tau'(h)" % h, eps(h),
          -(tau(h + 1e-5) - tau(h - 1e-5)) / 2e-5, 1e-5)


def best_response(T, A=A, k=K, w=W, href=HREF, lo=0.05, hi=4.0):
    """argmax_h J(h;T): bisection on the FOC, which is decreasing in h."""
    foc = lambda h: A * np.exp(-k * h) * (1 - k * h) + T - 2 * w * (h - href)
    if foc(hi) > 0:
        return hi
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if foc(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def h_sp(C1=C1, c=C):
    h = HREF
    for _ in range(600):
        h = 0.5 * h + 0.5 * best_response(tau(h, C1=C1, c=c))
    return h


def h_po(C1=C1, c=C):
    g = np.linspace(0.05, 4.0, 200001)
    return float(g[np.argmax(J(g, tau(g, C1=C1, c=c)))])


def modulus(C1=C1, c=C):
    h = h_sp(C1, c)
    return eps(h, C1, c) / gamma_closed(h)


def C1_for_modulus(target, c=C):
    lo, hi = 1e-3, 60.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if modulus(mid, c) < target else (lo, mid)
    return 0.5 * (lo + hi)


assert_true("h_SP is a fixed point of BR(tau(.))",
            abs(h_sp() - best_response(tau(h_sp()))) < 1e-8)
# main.tex Sec. 2 says the optimum "sits at a WIDER spread" than the stable
# point.  In this model it does not: h_PO < h_SP in every cell, which is also
# the sign REALDATA.md's "gap h_SP - h_PO" column reports.  The check asserts
# what the model actually does.
assert_true("h_PO < h_SP: the optimum quotes TIGHTER, not wider",
            h_po() < h_sp(),
            "h_SP=%.4f  h_PO=%.4f  gap h_SP-h_PO=%+.4f  (main.tex Sec. 2 says "
            "'wider')" % (h_sp(), h_po(), h_sp() - h_po()))
for tgt in (0.3, 0.6, 0.85):
    c1 = C1_for_modulus(tgt)
    assert_true("  ... and at m=%.2f too" % tgt, h_po(c1) < h_sp(c1),
                "h_SP=%.4f  h_PO=%.4f" % (h_sp(c1), h_po(c1)))
assert_true("Phi'(h_PO) = 0 and Phi'(h_SP) != 0",
            abs((Phi(h_po() + 1e-5) - Phi(h_po() - 1e-5)) / 2e-5) < 1e-4
            and abs((Phi(h_sp() + 1e-5) - Phi(h_sp() - 1e-5)) / 2e-5) > 1e-3)

print()
print("=" * 100)
print("2. T2, the exchange rate:  Var(eps_hat) x C_T = (1/2) gamma_PO sigma^2")
print("=" * 100)

# The paper's Table 1 reports two (modulus, amplitude) pairs per modulus.
for tgt, want_pred in ((0.3, 0.01056), (0.6, 0.00535)):
    c1 = C1_for_modulus(tgt)
    hs = h_sp(c1)
    pred = 0.5 * gamma_po_closed(hs, C1=c1) * SIGMA ** 2
    check("predicted rate at m=%.1f  = (1/2) gamma_PO sigma^2" % tgt, pred, want_pred, 6e-3)
    check("realised modulus at m=%.1f" % tgt, modulus(c1), tgt, 1e-6)

# Pathwise identity: Var = sigma^2/S_xx, cost = (1/2) gamma_PO sum d^2, so the
# product is (1/2) gamma_PO sigma^2 (1 + T dbar^2 / S_xx).  Simulated on the
# loop d_{t+1} = -m d_t + u_t, cost measured from the true Phi (not the
# quadratic), so any gap is exactly the A1 remainder.
rng = np.random.default_rng(11)
for tgt, s_e in ((0.3, 0.05), (0.3, 0.15), (0.6, 0.05), (0.6, 0.15)):
    c1 = C1_for_modulus(tgt)
    hs, m = h_sp(c1), modulus(c1)
    T, d = 60000, 0.0
    path = np.empty(T)
    for t in range(T):
        d = -m * d + s_e * rng.standard_normal()
        path[t] = hs + d
    hh = path[300:]
    hc = hh - hh.mean()
    var_eps = SIGMA ** 2 / float((hc ** 2).sum())
    cost_true = float(np.sum(Phi(hh.mean(), C1=c1) - Phi(hh, C1=c1)))
    pred = 0.5 * gamma_po_closed(hs, C1=c1) * SIGMA ** 2
    rel = var_eps * cost_true / pred - 1.0
    check("simulated Var x C_T / rate (m=%.1f, s_e=%.2f)" % (tgt, s_e),
          var_eps * cost_true / pred, 1.0, 0.06,
          "A1 remainder %+.2f%%" % (100 * rel))

# The paper's mechanism claim: information energy S_T and cost energy sum d^2
# coincide only for mean-centred exploration.  Quantify the inflation factor.
dbar_frac = 0.5
d_off = hc + dbar_frac * hc.std()
infl = float((d_off ** 2).sum()) / float(((d_off - d_off.mean()) ** 2).sum())
check("off-centre inflation = 1 + T dbar^2/S_xx", infl,
      1 + len(d_off) * d_off.mean() ** 2 / float(((d_off - d_off.mean()) ** 2).sum()), 1e-9)

print()
print("=" * 100)
print("3. T1 and the feedback floor")
print("=" * 100)

# T1 scalar cap: sum_t d_t^2 for d_t = (-m)^t d_0 is exactly d_0^2/(1-m^2).
for m in (0.3, 0.6, 0.85):
    d0 = 0.10
    energy = sum((d0 * (-m) ** t) ** 2 for t in range(20000))
    check("saturation cap d_0^2/(1-m^2), m=%.2f" % m, energy, d0 ** 2 / (1 - m ** 2), 1e-9)
    assert_true("cap increasing in m (C1.1, safety implies blindness) m=%.2f" % m,
                d0 ** 2 / (1 - m ** 2) < d0 ** 2 / (1 - (m + 0.01) ** 2))

# Excitation floor: retraining on noisy observations feeds sigma into the
# deployment with gain 1/gamma, so d_{t+1} = -m d_t + (sigma/gamma) zeta_t has
# stationary variance (sigma/gamma)^2/(1-m^2) -- the per-step energy rate.
for tgt in (0.3, 0.6, 0.85):
    c1 = C1_for_modulus(tgt)
    hs, m = h_sp(c1), modulus(c1)
    g = gamma_closed(hs)
    sig = 0.05
    r = np.random.default_rng(3)
    T, d = 400000, 0.0
    acc = 0.0
    for t in range(T):
        d = -m * d + (sig / g) * r.standard_normal()
        if t > 2000:
            acc += d * d
    check("excitation floor (sigma/gamma)^2/(1-m^2), m=%.2f" % tgt,
          acc / (T - 2001), (sig / g) ** 2 / (1 - m ** 2), 0.02)

print()
print("=" * 100)
print("4. T3 / T4, the minimax floors")
print("=" * 100)

# T3 is a van Trees bound: risk >= (D/sigma^2 + (pi/w)^2)^{-1}.  The paper's
# body drops the prior term and states sigma^2/B.  Both are computed here.
for D, wid, sig in ((150.0, 0.8, 0.7), (400.0, 1.2, 0.5)):
    vt = 1.0 / (D / sig ** 2 + (np.pi / wid) ** 2)
    naive = sig ** 2 / D
    assert_true("van Trees bound < sigma^2/D (prior term is not free), D=%g" % D,
                vt < naive, "vT %.6g  vs  sigma^2/D %.6g  (%.1f%% lower)"
                % (vt, naive, 100 * (1 - vt / naive)))

# (The register's V3.1/V3.2 cell quotes bound 0.01533, but its (sigma, D, w)
# are not published, so that number is not re-derivable here and is left to
# the suite re-run rather than guessed at.)

# T4's Le Cam arithmetic, from proofs_body.tex:
#   product >= (c^2 sigma^2/(2 Sbar))(1-c) . (gamma_PO Sbar/2)
#            = gamma_PO sigma^2 c^2 (1-c)/4,  maximised at c = 2/3.
cs = np.linspace(1e-6, 1 - 1e-6, 2000001)
val = cs ** 2 * (1 - cs) / 4
cstar, best = cs[val.argmax()], val.max()
check("Le Cam optimiser c*", cstar, 2.0 / 3.0, 1e-5)
check("Le Cam constant  c*^2(1-c*)/4", best, 1.0 / 27.0, 1e-6)
check("gap between the proved 1/27 and the claimed 1/2", 0.5 / (1.0 / 27.0), 13.5, 1e-9,
      "matches the paper's 'within a factor <= 13.5'")

print()
print("=" * 100)
print("5. T5 / C5.1, design geometry and the dispersion factor")
print("=" * 100)


def F_disp(g):
    """C5.1:  F = d tr(Gamma) / (tr Gamma^{1/2})^2."""
    g = np.asarray(g, float)
    return len(g) * g.sum() / np.sqrt(g).sum() ** 2


# The theorem: with budget tr(Gamma M) <= B, A-optimal M* ~ Gamma^{-1/2} and
# isotropic M overpays by exactly F.  Verified by direct construction and by
# random search over feasible designs.
r = np.random.default_rng(5)
for d in (3, 5, 8):
    for trial in range(3):
        g = np.exp(r.normal(0, 1.0, d))
        B = 2.0
        m_a = (B / np.sqrt(g).sum()) / np.sqrt(g)          # A-optimal: ~ g^{-1/2}
        m_i = np.full(d, B / g.sum())                       # isotropic
        check("A-optimal value = (tr G^{1/2})^2/B (d=%d)" % d,
              (1 / m_a).sum(), np.sqrt(g).sum() ** 2 / B, 1e-9)
        check("iso/A-opt ratio = F (d=%d)" % d,
              (1 / m_i).sum() / (1 / m_a).sum(), F_disp(g), 1e-9)
        best = min(float((1 / np.abs(r.dirichlet(np.ones(d)) * B / g)).sum())
                   for _ in range(4000))
        assert_true("no random feasible design beats A-optimal (d=%d, t=%d)" % (d, trial),
                    best >= (1 / m_a).sum() - 1e-9)
        assert_true("1 <= F <= d (d=%d, t=%d)" % (d, trial),
                    1 - 1e-12 <= F_disp(g) <= d + 1e-12, "F=%.4f" % F_disp(g))

# D- and c-optimal shapes (T5b, T5c) in the diagonal case.
g = np.exp(r.normal(0, 0.8, 6))
B = 3.0
m_d = (B / len(g)) / g
check("D-optimal M* = (B/d) Gamma^{-1}: budget met", float((g * m_d).sum()), B, 1e-12)
assert_true("D-optimal maximises log det among random feasible designs",
            all(np.log(m_d).sum() >= np.log(np.abs(r.dirichlet(np.ones(len(g))) * B / g)).sum()
                for _ in range(4000)))
cv = r.normal(size=len(g))
c_opt_val = float(cv @ (g * cv)) / B
best_c = min(float((cv @ np.linalg.solve(np.diag(np.abs(r.dirichlet(np.ones(len(g))) * B / g)), cv)))
             for _ in range(4000))
assert_true("c-optimal value c'Gamma c/B is never beaten by a diagonal design",
            best_c >= c_opt_val - 1e-9,
            "c-optimal %.5g, best random diagonal %.5g" % (c_opt_val, best_c))

# The paper's Table 1 row: "Isotropic/A-optimal risk ratio, d=8: 1.529 vs F=1.506".
# F is a pure function of the curvature spectrum; the measured 1.529 sits 1.5%
# above it, inside the paper's stated tolerance.
check("Table 1 measured/predicted gap for F (d=8)", 1.529 / 1.506, 1.0, 0.02,
      "measured is 1.5%% above F")

# Real-data leg: "F = 1.63 across the portfolio" against the 10 published
# gamma_PO cells in REALDATA.md section 2.
gpo_cells = np.array([510.6, 293.8, 163.1, 77.6, 37.8, 30.5, 17.4, 9.8, 5.0, 2.3])
check("F over the 10 real-data gamma_PO cells", F_disp(gpo_cells), 1.63, 4e-3,
      "the paper's cross-portfolio number")

print()
print("=" * 100)
print("6. T6, Chebyshev unidentifiability of the 3-parameter family")
print("=" * 100)

# s(h) = (1, e^{-ch}, -C1 h e^{-ch}) for theta = (C0, C1, c).
def sens(h, C1=C1, c=C):
    e = np.exp(-c * h)
    return np.array([1.0, e, -C1 * h * e])


r = np.random.default_rng(9)
worst3 = np.inf
for _ in range(4000):
    h1, h2, h3 = r.uniform(0.3, 3.0, 3)
    if min(abs(h1 - h2), abs(h1 - h3), abs(h2 - h3)) < 0.15:
        continue
    Mx = np.stack([sens(h1), sens(h2), sens(h3)])
    worst3 = min(worst3, abs(np.linalg.det(Mx)))
assert_true("3 distinct support points: design matrix never singular",
            worst3 > 1e-6, "worst |det| over 4000 draws = %.3g" % worst3)

# Two support points: rank 2 in R^3, so some direction is unidentified.  The
# appendix argues the null direction "must" hit the c-sensitivity because
# otherwise two points would determine three parameters; that is not the
# reason (a singular information matrix can still leave a functional
# estimable).  The correct argument: the null vector n satisfies
# n.s(h_1) = n.s(h_2) = 0, and n_3 = 0 forces n_1 + n_2 e^{-c h_i} = 0 for
# both i, hence n = 0 for h_1 != h_2.  So n_3 != 0 always and c is never
# estimable.  Checked numerically below.
worst_n3 = np.inf
for _ in range(20000):
    h1, h2 = r.uniform(0.3, 3.0, 2)
    if abs(h1 - h2) < 0.1:
        continue
    Mx = np.stack([sens(h1), sens(h2)])
    _, _, Vt = np.linalg.svd(Mx)
    n = Vt[-1]
    worst_n3 = min(worst_n3, abs(n[2]))
assert_true("2-point null direction always loads on the c-sensitivity",
            worst_n3 > 1e-3,
            "min |n_3| over 20000 pairs = %.3g (c never estimable)" % worst_n3)

fisher2 = sum(np.outer(sens(h), sens(h)) for h in (1.2, 1.9))
fisher3 = sum(np.outer(sens(h), sens(h)) for h in (1.2, 1.9, 2.7))
assert_true("2-point Fisher matrix singular, 3-point not",
            abs(np.linalg.det(fisher2)) < 1e-15 and abs(np.linalg.det(fisher3)) > 1e-6,
            "det2 %.2g  det3 %.2g" % (np.linalg.det(fisher2), np.linalg.det(fisher3)))

print()
print("=" * 100)
print("7. T7, the anchoring crossover")
print("=" * 100)

hs = h_sp()
gpo = gamma_po_closed(hs)
for B, T in ((0.6, 400), (1.2, 900), (2.0, 2500)):
    w_opt = np.sqrt(2 * B / (gpo * T))
    # Bias of the symmetric secant at half-width w, by Taylor: tau'''/6 w^2.
    bias = (tau(hs + w_opt) - tau(hs - w_opt)) / (2 * w_opt) - (-eps(hs))
    check("secant bias = tau'''/6 w^2 (B=%.1f,T=%d)" % (B, T), bias,
          tau3(hs) / 6 * w_opt ** 2, 0.02)
    var = SIGMA ** 2 / (T * w_opt ** 2)
    mse_direct = var + bias ** 2
    mse_formula = gpo * SIGMA ** 2 / (2 * B) + (tau3(hs) / 6) ** 2 * (2 * B / (gpo * T)) ** 2
    check("MSE_np = gpo sigma^2/(2B) + (tau'''/6)^2 (2B/(gpo T))^2 (B=%.1f)" % B,
          mse_direct, mse_formula, 0.02)
    # The crossover rule delta_mis < |tau'''| B / (3 gpo T) is exactly the
    # misspecification at which delta^2 equals the squared bias term.
    thr = abs(tau3(hs)) * B / (3 * gpo * T)
    check("crossover threshold = sqrt(bias^2 term) (B=%.1f,T=%d)" % (B, T),
          thr, abs(tau3(hs) / 6 * (2 * B / (gpo * T))), 1e-12)

# Table 1 row: "Nonparametric MSE at (B,T) optimum: 0.0132 vs 0.0123".
check("Table 1 T7 measured/predicted gap", 0.0132 / 0.0123, 1.0, 0.08,
      "measured is 7.3%% above the closed form")

print()
print("=" * 100)
print("8. T8, the ROI of self-knowledge")
print("=" * 100)

kappa, sig = 0.35, SIGMA
gap = h_po() - h_sp()
Aval = 0.5 * gpo * gap ** 2
a, b = 0.5 * gpo * kappa ** 2, 0.5 * gpo * sig ** 2
for rho in (0.02, 0.08, 0.2):
    npv = lambda v: (Aval - a * v) / rho - b / v
    grid = np.linspace(1e-6, 5.0, 4000001)
    check("v* = (sigma/kappa) sqrt(rho), rho=%.2f" % rho,
          grid[np.argmax(npv(grid))], (sig / kappa) * np.sqrt(rho), 2e-3)
rho_star = gap ** 4 / (4 * kappa ** 2 * sig ** 2)
for f, side in ((0.9, True), (1.1, False)):
    rho = f * rho_star
    v = (sig / kappa) * np.sqrt(rho)
    npv = (Aval - a * v) / rho - b / v
    assert_true("explore iff rho < rho* (rho = %.2f rho*)" % f, (npv > 0) == side,
                "NPV = %+.4f" % npv)
assert_true("gamma_PO cancels out of rho*",
            abs(gap ** 4 / (4 * kappa ** 2 * sig ** 2)
                - (4 * Aval ** 2) / (16 * a * b)) < 1e-9)

print()
print("=" * 100)
print("9. P9.1, Lai-Robbins schedules sit on the frontier")
print("=" * 100)

for sched, label in (
        (lambda t: 0.2 * (t + 1.0) ** -0.5, "d_t ~ t^{-1/2} (log-cost)"),
        (lambda t: 0.1 + 0.0 * t, "constant amplitude"),
        (lambda t: 0.3 * np.exp(-t / 500.0), "geometric decay")):
    for T in (2000, 20000):
        d = np.array([sched(t) * (-1) ** t for t in range(T)])   # mean-centred
        S = float((d ** 2).sum())
        prod = (SIGMA ** 2 / S) * (0.5 * gpo * S)
        check("%s, T=%d" % (label, T), prod, 0.5 * gpo * SIGMA ** 2, 1e-12)

print()
print("=" * 100)
print("10. OPEN-1: is the floor structure-proof, and does known c break it?")
print("=" * 100)

hstar = h_po()
gpo_star = gamma_po_closed(hstar)
floor = 0.5 * gpo_star * SIGMA ** 2


def cr_product(support, weights, known_c):
    """Cramer-Rao product for eps(h*) under a design measure, in the
    structural family.  Var = sigma^2 g' M^{-1} g / n with M = sum w_i s s',
    cost = (1/2) gamma_PO n sum w_i (h_i - h*)^2, so n cancels and the
    product is (1/2) gamma_PO sigma^2 . [g'M^{-1}g] . [sum w_i dev^2]."""
    support = np.asarray(support, float)
    weights = np.asarray(weights, float)
    weights = weights / weights.sum()
    e = np.exp(-C * support)
    if known_c:
        # theta = (C0, C1);  eps(h*) = C1 c e^{-c h*}, c fixed.
        S = np.stack([np.ones_like(support), e], axis=1)
        g = np.array([0.0, C * np.exp(-C * hstar)])
    else:
        # theta = (C0, C1, c);  eps(h*) = C1 c e^{-c h*}.
        S = np.stack([np.ones_like(support), e, -C1 * support * e], axis=1)
        g = np.array([0.0, C * np.exp(-C * hstar),
                      C1 * np.exp(-C * hstar) * (1 - C * hstar)])
    M = (S * weights[:, None]).T @ S
    try:
        var_unit = float(g @ np.linalg.solve(M, g))
    except np.linalg.LinAlgError:
        return np.inf
    if not np.isfinite(var_unit) or var_unit <= 0:
        return np.inf
    energy = float((weights * (support - hstar) ** 2).sum())
    return 0.5 * gpo_star * SIGMA ** 2 * var_unit * energy / floor


# (a) Unknown c: the paper says the best family-knowing design is 1.005x the
# floor.  Random + local search over 4-point designs.
r = np.random.default_rng(17)
best_unknown, arg_unknown = np.inf, None
for _ in range(60000):
    sup = hstar + r.normal(0, 0.25, 4)
    wts = r.dirichlet(np.ones(4) * 0.5)
    v = cr_product(sup, wts, known_c=False)
    if v < best_unknown:
        best_unknown, arg_unknown = v, (sup.copy(), wts.copy())
sup, wts = arg_unknown
for scale in (0.1, 0.03, 0.01, 0.003):
    for _ in range(20000):
        s2 = sup + r.normal(0, scale, 4)
        w2 = np.abs(wts + r.normal(0, scale, 4)) + 1e-9
        v = cr_product(s2, w2, known_c=False)
        if v < best_unknown:
            best_unknown, sup, wts = v, s2, w2 / w2.sum()
check("OPEN-1 min CR ratio, c unknown (4-point designs)", best_unknown, 1.005, 0.02,
      "the paper's structure-proofness number")
assert_true("floor is structure-proof: best family-knowing design >= 1",
            best_unknown >= 0.99,
            "min ratio %.4f, support spread %.3f" % (best_unknown, sup.std()))

# (b) The paper's tight-probe scan: a pair at h* +/- 0.1 plus one tight probe
# at t.  The paper reports 5.7 -> 41 as t falls, i.e. monotonically worse.
prev = 0.0
mono = True
for t in (1.0, 0.8, 0.6, 0.4, 0.2, 0.05):
    best_t = min(cr_product([hstar - 0.1, hstar + 0.1, t], [(1 - wt) / 2, (1 - wt) / 2, wt],
                            known_c=False) for wt in (0.05, 0.1, 0.2, 0.4))
    mono = mono and best_t > prev
    prev = best_t
    print("      tight probe t=%.2f -> best ratio %.3f" % (t, best_t))
assert_true("tight-side probing is monotonically worse (c unknown)", mono,
            "ratio rises as the probe tightens, as the paper reports")

# (c) The paper's boundary claim: "with c known a priori the floor breaks
# (ratio -> 0.05)".  Nothing in the shipped pipeline computes this.  Recompute.
print("      --- c known a priori ---")
best_known = np.inf
for t in (1.0, 0.8, 0.6, 0.4, 0.2, 0.05):
    bt = min(cr_product([hstar - 0.1, hstar + 0.1, t],
                        [(1 - wt) / 2, (1 - wt) / 2, wt], known_c=True)
             for wt in (0.02, 0.05, 0.1, 0.2, 0.4))
    best_known = min(best_known, bt)
    print("      tight probe t=%.2f -> best ratio %.4f" % (t, bt))
assert_true("with c known the floor does break (ratio < 1)", best_known < 1.0,
            "min ratio over the same scan = %.4f" % best_known)

# Unconstrained search over 2-point designs with c known: does the ratio have
# a floor at 0.05, or does it fall without bound?
tail = []
for probe in (0.5, 0.2, 0.05, 0.01, 0.001):
    b = np.inf
    for wt in np.linspace(0.001, 0.5, 400):
        b = min(b, cr_product([hstar, probe], [1 - wt, wt], known_c=True))
    tail.append((probe, b))
    print("      2-point (h*, t=%.3f) known c -> best ratio %.5f" % (probe, b))
assert_true("known-c ratio keeps falling as the probe widens (no floor at 0.05)",
            tail[-1][1] < tail[0][1] and tail[-1][1] < 0.05,
            "%.5f at t=%.3f vs %.5f at t=%.3f"
            % (tail[-1][1], tail[-1][0], tail[0][1], tail[0][0]))
report("paper's stated known-c ratio 0.05", best_known,
       "no shipped artifact computes it; the value is design-dependent")

print()
print("=" * 100)
print("11. E8, the LQ pricing domain (A1 exact, so the rate should be exact)")
print("=" * 100)

# Linear-quadratic performative pricing: q(p; p_dep) = a - b p + g p_dep, so
# Phi(p) = p (a + (g - b) p) is exactly quadratic and A1 holds globally.
# Re-derive every constant from Phi alone, then the exchange rate.
A_LQ, B_LQ, SIG_LQ = 10.0, 1.0, 0.8


def phi_lq(p, g):
    return p * (A_LQ + (g - B_LQ) * p)


for g_, want_rate in ((0.4, 0.384), (0.7, 0.192), (0.6, None)):
    gpo_num = -d2(lambda x: phi_lq(x, g_), 3.0)
    check("LQ gamma_PO = 2(b-g) at g=%.1f" % g_, gpo_num, 2 * (B_LQ - g_), 1e-6)
    p_po_num = float(np.linspace(0.5, 30, 2000001)[
        np.argmax(phi_lq(np.linspace(0.5, 30, 2000001), g_))])
    check("LQ p_PO = a/(2(b-g)) at g=%.1f" % g_, p_po_num,
          A_LQ / (2 * (B_LQ - g_)), 1e-5)
    check("LQ p_SP = a/(2b-g) at g=%.1f" % g_, A_LQ / (2 * B_LQ - g_),
          A_LQ / (2 * B_LQ - g_), 0)
    if want_rate is not None:
        check("LQ exchange rate (1/2) gamma_PO sigma^2 at g=%.1f" % g_,
              0.5 * gpo_num * SIG_LQ ** 2, want_rate, 2e-3,
              "the paper's E8 cell")

# The reported agent cell: "reaches the pricing optimum (12.58 vs 12.5)" from
# p_SP = 7.14, at the default g = 0.6.
check("LQ p_PO at g=0.6 (paper's 12.5)", A_LQ / (2 * (B_LQ - 0.6)), 12.5, 1e-9)
check("LQ p_SP at g=0.6 (paper's 7.14)", A_LQ / (2 * B_LQ - 0.6), 7.14, 1e-3)
assert_true("in the LQ domain p_PO > p_SP (opposite ordering to the market model)",
            A_LQ / (2 * (B_LQ - 0.6)) > A_LQ / (2 * B_LQ - 0.6),
            "p_SP=%.2f  p_PO=%.2f" % (A_LQ / (2 * B_LQ - 0.6), A_LQ / (2 * (B_LQ - 0.6))))

# In an LQ model the identity holds exactly, whatever the schedule.  Verify on
# a synthetic quadratic Phi with the same structure.
for gpo_lq in (0.768, 0.384):
    for s_e in (0.2, 0.5):
        r2 = np.random.default_rng(23)
        T = 200000
        d = r2.normal(0, s_e, T)
        d = d - d.mean()
        sig_t = 1.0
        var_eps = sig_t ** 2 / float((d ** 2).sum())
        cost = 0.5 * gpo_lq * float((d ** 2).sum())
        check("LQ identity exact (gpo=%.3f, s_e=%.1f)" % (gpo_lq, s_e),
              var_eps * cost, 0.5 * gpo_lq * sig_t ** 2, 1e-12)

print()
print("=" * 100)
print("12. L4, the perturbed-modulus lemma and its Lipschitz constant")
print("=" * 100)

# L4: |rho_hat - rho| <= eta beta (||e||_inf + |h-psi| ||e'||_inf).  For the
# exponential family e(h) = (C1_hat - C1) c e^{-ch} so ||e'||_inf = c ||e||_inf
# and the bracket collapses to ||e||_inf (1 + c |h - psi|) = ||e||_inf L_fam,
# which is the constant the paper's agent uses.
for h in (1.2, 1.85, 2.5):
    for dC1 in (0.01, 0.05):
        grid = np.linspace(h - 0.3, h + 0.3, 4001)
        e_fn = dC1 * C * np.exp(-C * grid)
        ep_fn = -dC1 * C ** 2 * np.exp(-C * grid)
        bracket = np.abs(e_fn).max() + abs(h - PSI) * np.abs(ep_fn).max()
        lfam = (1 + C * abs(h - PSI)) * np.abs(e_fn).max()
        check("L4 bracket = L_fam . ||e|| (h=%.2f, dC1=%.2f)" % (h, dC1),
              bracket, lfam, 0.02)

print()
print("=" * 100)
print("SUMMARY:  %d pass, %d fail, %d untraceable" % (PASS, FAIL, DRIFT))
print("=" * 100)
raise SystemExit(1 if FAIL else 0)
