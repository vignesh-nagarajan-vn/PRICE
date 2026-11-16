"""Certificates for Theorem 4, the Pigouvian wedge.

Source of the statements: ../../math/04-theorem4-wedge.md.

Assertion-based: every check raises on failure and the script exits nonzero,
following verify_theorem1_proof.py as the template.

Checks, in the order the derivation makes them:

  W1  AR(1) reduction        simulated stationary variance is sigma^2/(1-m_N^2),
                             and the lag-1 autocorrelation is -m_N            [C19]
  W2  marginal crowding      d m_N/d m_i = N_eff * v_i^2 by finite differences,
                             summing to N_eff, equal to N_eff/N on exchangeable
                             R                                                [C34]
  W3  the wedge              t* closes the gap between the private and social
                             first-order conditions exactly
  W4  comparative statics    t* strictly increasing in N, kappa and m_N, and
                             divergent at the boundary                        [C20]
  W5  over-adaptation        a_d > a_s for every N >= 2, and they coincide at
                             N = 1 with chi = 1                               [C21]
  W6  provenance channel     d m_N/ds = m_1 kappa (N-1) exactly
"""
import numpy as np

TOL = 1e-12
PASSED = []


def check(name, condition, detail=""):
    """Record a check and fail loudly if it did not hold."""
    if not condition:
        raise AssertionError(f"FAILED {name}: {detail}")
    PASSED.append(name)
    print(f"  pass  {name}" + (f"   [{detail}]" if detail else ""))


# ---------------------------------------------------------------- primitives

def n_eff(R, kappa):
    return 1 + kappa * (np.linalg.eigvalsh(R).max() - 1)


def coupling_B(R, kappa):
    """B = (1-kappa)I + kappa R, the Jacobian's bracket without the moduli."""
    return (1 - kappa) * np.eye(R.shape[0]) + kappa * R


def hetero_radius(R, m, kappa):
    """rho(J) for J = -diag(m) B, via the symmetric congruence of Prop 4 of D1."""
    root_m = np.sqrt(m)
    A = root_m[:, None] * coupling_B(R, kappa) * root_m[None, :]
    return float(np.linalg.eigvalsh(A).max())


def supply_chain_R(N, s):
    return (1 - s) * np.eye(N) + s * np.ones((N, N))


def random_R(N, D, rng):
    """A valid alignment matrix: Gram of N unit vectors in R^D."""
    X = rng.standard_normal((N, D))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X @ X.T


def V(m_N, sigma=1.0):
    return sigma ** 2 / (1 - m_N ** 2)


def dV(m_N, sigma=1.0):
    return 2 * sigma ** 2 * m_N / (1 - m_N ** 2) ** 2


rng = np.random.default_rng(20260818)


# ------------------------------------------- W1  the AR(1) reduction   [C19]

print("\nW1  AR(1) reduction: V = sigma^2/(1 - m_N^2), lag-1 autocorr = -m_N")

def simulate_common_mode(m_N, sigma, n_steps, seed):
    """z_{t+1} = -m_N z_t + xi_t, run past burn-in from the stationary law."""
    g = np.random.default_rng(seed)
    z = 0.0
    burn = 5000
    out = np.empty(n_steps)
    for t in range(burn + n_steps):
        z = -m_N * z + sigma * g.standard_normal()
        if t >= burn:
            out[t - burn] = z
    return out

for m_N, sigma in ((0.30, 1.0), (0.60, 0.5), (0.85, 2.0), (0.95, 1.0)):
    z = simulate_common_mode(m_N, sigma, 400_000, seed=int(m_N * 1000) + 7)
    var_meas = float(z.var())
    var_closed = V(m_N, sigma)
    rel = abs(var_meas - var_closed) / var_closed
    check(f"W1 variance m_N={m_N} sigma={sigma}", rel < 2e-2,
          f"measured {var_meas:.5f} against {var_closed:.5f}, rel {rel:.2e}")
    ac1 = float(np.corrcoef(z[:-1], z[1:])[0, 1])
    check(f"W1 lag-1 autocorr m_N={m_N}", abs(ac1 - (-m_N)) < 2e-2,
          f"measured {ac1:+.5f} against {-m_N:+.5f}")
    check(f"W1 autocorr is negative m_N={m_N}", ac1 < 0,
          "a crowded market oscillates, it does not persist")

# the variance is blind to the sign, the autocorrelation is not
for m_N in (0.4, 0.8):
    check(f"W1 variance is sign-blind m_N={m_N}",
          abs(V(m_N) - V(-m_N)) < TOL,
          "same 1/(1 - m_N^2) for +m_N and -m_N")

# the analytic recursion V = m^2 V + sigma^2 solves to the closed form
for m_N, sigma in ((0.2, 1.0), (0.7, 3.0), (0.99, 1.0)):
    v = V(m_N, sigma)
    check(f"W1 fixed point m_N={m_N}", abs(v - (m_N ** 2 * v + sigma ** 2)) < 1e-9)

check("W1 V diverges at the boundary", V(0.999999) > 1e5,
      f"V(1-1e-6) = {V(0.999999):.3e}, growing like 1/(2(1-m_N))")

# dV/dm is the stated derivative
for m_N in (0.1, 0.5, 0.9):
    h = 1e-6
    fd = (V(m_N + h) - V(m_N - h)) / (2 * h)
    check(f"W1 dV/dm at m_N={m_N}", abs(fd - dV(m_N)) / dV(m_N) < 1e-6,
          f"fd {fd:.6f} against {dV(m_N):.6f}")


# ----------------------------------- W2  the marginal crowding share   [C34]

print("\nW2  Lemma 11: d m_N/d m_i = N_eff * v_i^2, and N_eff/N when R is exchangeable")

def marginal_shares_fd(R, m1, kappa, h=1e-7):
    """Finite-difference d rho / d m_i at the symmetric point m = m1 * 1."""
    N = R.shape[0]
    out = np.empty(N)
    for i in range(N):
        mp = np.full(N, m1); mp[i] += h
        mm = np.full(N, m1); mm[i] -= h
        out[i] = (hetero_radius(R, mp, kappa) - hetero_radius(R, mm, kappa)) / (2 * h)
    return out

for N, D, kappa in ((4, 9, 0.8), (6, 12, 0.55), (9, 20, 1.0), (5, 7, 0.3)):
    R = random_R(N, D, rng)
    m1 = 0.15
    ne = n_eff(R, kappa)
    B = coupling_B(R, kappa)
    w, Vec = np.linalg.eigh(B)
    v = Vec[:, -1]
    gap = w[-1] - w[-2]
    if gap < 1e-6:
        continue                      # Lemma 11 assumes a simple leading eigenvalue
    predicted = ne * v ** 2
    measured = marginal_shares_fd(R, m1, kappa)
    err = np.abs(measured - predicted).max()
    check(f"W2 shares N={N} kappa={kappa}", err < 1e-5,
          f"max|fd - N_eff v_i^2| = {err:.2e}")
    check(f"W2 shares sum to N_eff, N={N} kappa={kappa}",
          abs(measured.sum() - ne) < 1e-5,
          f"sum {measured.sum():.9f} against N_eff {ne:.9f}")

# exchangeable R: the share is exactly N_eff / N, which is the (N-1)/N statement
for N in (2, 3, 5, 10, 25):
    for kappa in (0.0, 0.4, 0.8, 1.0):
        for s in (0.2, 0.5, 1.0):
            R = supply_chain_R(N, s)
            m1 = 0.12
            ne = n_eff(R, kappa)
            measured = marginal_shares_fd(R, m1, kappa)
            spread = measured.max() - measured.min()
            if abs(ne - 1.0) < 1e-12:
                continue              # kappa*s = 0 leaves the leading eigenvalue degenerate
            check(f"W2 exchangeable N={N} kappa={kappa} s={s}",
                  abs(measured[0] - ne / N) < 1e-5 and spread < 1e-6,
                  f"share {measured[0]:.9f} against N_eff/N {ne / N:.9f}")

# monoculture corner, where m_N = m_1 N_eff has the base law's N_eff
for N in (3, 8, 20):
    R = np.ones((N, N))
    kappa = 0.8
    ne = n_eff(R, kappa)
    check(f"W2 monoculture N_eff N={N}", abs(ne - (1 + kappa * (N - 1))) < 1e-10)
    measured = marginal_shares_fd(R, 0.1, kappa)
    check(f"W2 monoculture share N={N}", abs(measured[0] - ne / N) < 1e-5,
          f"{measured[0]:.9f} against {ne / N:.9f}")

# the naive 1/N guess is wrong by exactly the factor N_eff, which is the point of C34
N, kappa, s = 20, 0.8, 1.0
ne = n_eff(supply_chain_R(N, s), kappa)
check("W2 the naive 1/N is wrong by the factor N_eff",
      abs((ne / N) / (1.0 / N) - ne) < 1e-10 and ne > 15,
      f"N_eff = {ne:.4f}, so the share is {ne:.4f} times the naive guess")


# ------------------------------------------------------ W3  the wedge

print("\nW3  the wedge closes the gap between the private and social conditions")

def m_N_of(a, N, kappa, s, mu):
    return mu(a) * n_eff(supply_chain_R(N, s), kappa)


def dmN_da(a, N, kappa, s, mu, dmu):
    """(N_eff/N) mu'(a), the aggressiveness channel of Lemma 11."""
    return n_eff(supply_chain_R(N, s), kappa) / N * dmu(a)


def t_star(a, N, kappa, s, mu, dmu, w, chi, sigma=1.0):
    W_planner = chi * N * w
    return (W_planner - w) * dV(m_N_of(a, N, kappa, s, mu), sigma) * dmN_da(a, N, kappa, s, mu, dmu)


# a concrete parameterisation satisfying (W1) and (W2)
MU0 = 0.02
def mu(a):        return MU0 * a
def dmu(a):       return MU0 + 0.0 * a
def Bben(a):      return 0.30 * np.log(a)
def dBben(a):     return 0.30 / a


def private_foc(a, N, kappa, s, w, chi, sigma=1.0, fee=0.0):
    return dBben(a) - fee - w * dV(m_N_of(a, N, kappa, s, mu), sigma) * dmN_da(a, N, kappa, s, mu, dmu)


def social_foc(a, N, kappa, s, w, chi, sigma=1.0):
    W_planner = chi * N * w
    return dBben(a) - W_planner * dV(m_N_of(a, N, kappa, s, mu), sigma) * dmN_da(a, N, kappa, s, mu, dmu)


def solve(f, N, kappa, s, w, chi, **kw):
    """Root of a strictly decreasing FOC on the stable range."""
    ne = n_eff(supply_chain_R(N, s), kappa)
    hi = (1.0 / (MU0 * ne)) * 0.999999          # m_N = 1 boundary in a
    lo = hi * 1e-6
    flo, fhi = f(lo, N, kappa, s, w, chi, **kw), f(hi, N, kappa, s, w, chi, **kw)
    if not (flo > 0 > fhi):
        return None
    for _ in range(300):                        # bisection, numpy-only by design
        mid = 0.5 * (lo + hi)
        if f(mid, N, kappa, s, w, chi, **kw) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


GRID = [(N, kappa, s, w, chi)
        for N in (2, 3, 5, 8, 12, 20)
        for kappa in (0.4, 0.8, 1.0)
        for s in (0.3, 0.6, 1.0)
        for w in (1.0,)
        for chi in (1.0, 1.5)]

n_cases = 0
for N, kappa, s, w, chi in GRID:
    a_d = solve(private_foc, N, kappa, s, w, chi)
    a_s = solve(social_foc, N, kappa, s, w, chi)
    if a_d is None or a_s is None:
        continue
    n_cases += 1
    # the fee at the social optimum makes the private condition hold there
    fee = t_star(a_s, N, kappa, s, mu, dmu, w, chi)
    resid = private_foc(a_s, N, kappa, s, w, chi, fee=fee)
    if abs(resid) > 1e-9:
        raise AssertionError(
            f"W3 fee does not implement the optimum at N={N} kappa={kappa} "
            f"s={s} chi={chi}: residual {resid:.3e}")
check(f"W3 t* implements the social optimum on {n_cases} configurations", n_cases > 0,
      f"max residual below 1e-9 across N in 2..20, kappa in 0.4..1, s in 0.3..1")

# the (N-1)/N reading: with chi = 1 the ignored fraction is exactly (N-1)/N
for N in (2, 3, 7, 15, 40):
    w, chi = 1.0, 1.0
    ignored = (chi * N * w - w) / (chi * N * w)
    check(f"W3 ignored fraction at chi=1, N={N}", abs(ignored - (N - 1) / N) < TOL,
          f"{ignored:.9f}")
    check(f"W3 ignored fraction strictly larger at chi>1, N={N}",
          (1.5 * N - 1) / (1.5 * N) > ignored,
          "client exposure adds to the (N-1)/N firm channel")


# ----------------------------------------- W4  comparative statics    [C20]

print("\nW4  t* is strictly increasing in N, in kappa and in m_N, and diverges")

# a0 is chosen so that m_N stays strictly inside the stable range over the whole
# sweep. Outside it V is not the stationary variance of anything and the
# comparative statics are vacuous, so the range is asserted rather than assumed.
a0, w, chi, s0, kappa0 = 1.0, 1.0, 1.5, 0.8, 0.8

worst = max(m_N_of(a0, N, 1.0, 1.0, mu) for N in range(2, 41))
check("W4 the sweep stays inside the stable range", worst < 1.0,
      f"largest m_N on the grid is {worst:.4f}")

vals = [t_star(a0, N, kappa0, s0, mu, dmu, w, chi) for N in range(2, 41)]
check("W4 strictly increasing in N", all(b > a for a, b in zip(vals, vals[1:])),
      f"t*(N=2) = {vals[0]:.4f} up to t*(N=40) = {vals[-1]:.4f}")

for N in (3, 10, 25):
    ks = np.linspace(0.05, 1.0, 40)
    vals = [t_star(a0, N, k, s0, mu, dmu, w, chi) for k in ks]
    check(f"W4 strictly increasing in kappa, N={N}",
          all(b > a for a, b in zip(vals, vals[1:])),
          f"{vals[0]:.4f} to {vals[-1]:.4f}")

# in m_N directly, holding the channel fixed
ms = np.linspace(0.05, 0.99, 60)
vals = [dV(m) for m in ms]
check("W4 dV/dm strictly increasing in m_N",
      all(b > a for a, b in zip(vals, vals[1:])),
      f"{vals[0]:.4f} to {vals[-1]:.4f}")

near = [dV(m) for m in (0.9, 0.99, 0.999, 0.9999)]
check("W4 divergence at the boundary", near[-1] / near[0] > 1e6,
      f"dV grows {near[-1] / near[0]:.3e} fold from m_N = 0.9 to 0.9999")

# the (1 - m_N)^-2 rate, fitted
xs = np.array([0.99, 0.999, 0.9999, 0.99999])
slope = np.polyfit(np.log(1 - xs), np.log([dV(x) for x in xs]), 1)[0]
check("W4 the divergence rate is (1 - m_N)^-2", abs(slope + 2) < 1e-3,
      f"fitted exponent {slope:.6f}")

# in s, through N_eff
for N in (5, 20):
    ss = np.linspace(0.05, 1.0, 30)
    vals = [t_star(a0, N, kappa0, sv, mu, dmu, w, chi) for sv in ss]
    check(f"W4 strictly increasing in s, N={N}",
          all(b > a for a, b in zip(vals, vals[1:])))


# --------------------------------------------- W5  over-adaptation    [C21]

print("\nW5  over-adaptation: a_d > a_s for every N >= 2")

n_pairs, min_gap = 0, np.inf
for N, kappa, s, w, chi in GRID:
    a_d = solve(private_foc, N, kappa, s, w, chi)
    a_s = solve(social_foc, N, kappa, s, w, chi)
    if a_d is None or a_s is None:
        continue
    n_pairs += 1
    if not a_d > a_s:
        raise AssertionError(
            f"W5 no over-adaptation at N={N} kappa={kappa} s={s} chi={chi}: "
            f"a_d={a_d:.6f} a_s={a_s:.6f}")
    min_gap = min(min_gap, (a_d - a_s) / a_s)
check(f"W5 a_d > a_s on {n_pairs} configurations", n_pairs >= 60,
      f"smallest relative gap {min_gap:.4f}")

# the resulting systemic modulus is higher under decentralisation
for N, kappa, s in ((5, 0.8, 1.0), (20, 0.8, 0.6), (3, 1.0, 1.0)):
    w, chi = 1.0, 1.5
    a_d = solve(private_foc, N, kappa, s, w, chi)
    a_s = solve(social_foc, N, kappa, s, w, chi)
    md, ms_ = m_N_of(a_d, N, kappa, s, mu), m_N_of(a_s, N, kappa, s, mu)
    check(f"W5 m_N is higher when decentralised, N={N} kappa={kappa} s={s}",
          md > ms_, f"m_N {md:.4f} against {ms_:.4f}")

# the gap widens with N, which is "the distortion grows as the market crowds"
gaps = []
for N in (2, 3, 5, 8, 12, 20):
    w, chi = 1.0, 1.5
    a_d = solve(private_foc, N, 0.8, 1.0, w, chi)
    a_s = solve(social_foc, N, 0.8, 1.0, w, chi)
    gaps.append((a_d - a_s) / a_s)
check("W5 the relative gap widens with N",
      all(b > a for a, b in zip(gaps, gaps[1:])),
      f"{gaps[0]:.4f} at N=2 up to {gaps[-1]:.4f} at N=20")

# the degenerate case: N = 1 with chi = 1 has a zero wedge and no distortion
w, chi, N = 1.0, 1.0, 1
check("W5 zero wedge at N=1 with chi=1",
      abs(t_star(a0, N, 0.8, 1.0, mu, dmu, w, chi)) < TOL,
      "a single firm bearing its own variance internalises everything")
for N in (2, 3, 10):
    check(f"W5 strictly positive wedge at chi=1, N={N}",
          t_star(a0, N, 0.8, 1.0, mu, dmu, 1.0, 1.0) > 0,
          "the firm-to-firm channel alone is strict for N >= 2")


# ------------------------------------------- W6  the provenance channel

print("\nW6  provenance channel: d m_N/ds = m_1 kappa (N-1)")

for N in (2, 5, 13, 30):
    for kappa in (0.2, 0.6, 1.0):
        m1 = 0.11
        h = 1e-7
        fd = (m1 * n_eff(supply_chain_R(N, 0.5 + h), kappa)
              - m1 * n_eff(supply_chain_R(N, 0.5 - h), kappa)) / (2 * h)
        closed = m1 * kappa * (N - 1)
        check(f"W6 dm_N/ds N={N} kappa={kappa}", abs(fd - closed) < 1e-6,
              f"fd {fd:.9f} against {closed:.9f}")

# linear in N and does not decay, unlike the aggressiveness channel's N_eff/N
kappa, m1 = 0.8, 0.11
prov = [m1 * kappa * (N - 1) for N in (10, 100, 1000)]
aggr = [n_eff(supply_chain_R(N, 1.0), kappa) / N for N in (10, 100, 1000)]
check("W6 the provenance channel grows without bound",
      prov[-1] / prov[0] > 90, f"{prov[0]:.4f} to {prov[-1]:.4f} from N=10 to 1000")
check("W6 the aggressiveness channel tends to kappa from above",
      all(x > kappa for x in aggr) and abs(aggr[-1] - kappa) < 1e-3,
      f"{aggr[0]:.5f}, {aggr[1]:.5f}, {aggr[2]:.5f} against kappa = {kappa}")


print(f"\n{len(PASSED)} checks passed.")
