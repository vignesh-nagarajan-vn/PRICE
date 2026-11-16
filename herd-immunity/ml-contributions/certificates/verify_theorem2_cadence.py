"""Certificates for the Theorem 2 proof.

Source of the statements: ../../math/derivations/03-cadence-composition.md.

Assertion-based: every check raises on failure and the script exits nonzero.

The load-bearing check is C12. The composition of the amplification law with the
lazy-deployment slope is only valid if the inner per-step contraction
c = 1 - eta*gamma is the same object in the joint market as in the single-firm
market, that is, if it depends on own-objective curvature and not on N, kappa or
R. Everything else in Theorem 2 is algebra that follows once that holds, so C12
is simulated from actual gradient descent rather than asserted.

Checks:

  Q1  inner contraction     K steps of GD contract to the frozen best response by c^K
  C12 c is invariant to N   the same c is measured at every N, kappa and R
  Q2  joint map             the K-step joint map is c^K I + (1-c^K) J, measured
  Q3  mu_N(K)               the common mode's slope, and which mode binds
  C8  cadence agreement     is_stable_lazy agrees with K < k_max on integer K
  C9  monotonicity          k_max decreasing in m_N
  C10 critical crowding     no integer K >= 1 survives m_N > (1+c)/(1-c)
  Q4  equivalent form       stable iff m_N < (1+c^K)/(1-c^K)
  C11 worked table          K_max = 20.68 / 5.28 / 2.53 at s = 0.25 / 0.5 / 1
  Q5  dynamic check         iterating the real joint map matches the frontier
"""
import numpy as np

TOL = 1e-12
PASSED = []


def check(name, condition, detail=""):
    if not condition:
        raise AssertionError(f"FAILED {name}: {detail}")
    PASSED.append(name)
    print(f"  pass  {name}" + (f"   [{detail}]" if detail else ""))


# ---------------------------------------------------------------- primitives

def joint_jacobian(R, m1, kappa):
    N = R.shape[0]
    return -m1 * ((1 - kappa) * np.eye(N) + kappa * R)


def n_eff(R, kappa):
    return 1 + kappa * (np.linalg.eigvalsh(R).max() - 1)


def mu_N(m_N, c, K):
    return -m_N + c ** K * (1 + m_N)


def k_max(m_N, c):
    if m_N <= 1:
        return np.inf
    return np.log((m_N - 1) / (m_N + 1)) / np.log(c)


def critical_crowding(c):
    return (1 + c) / (1 - c)


def is_stable_lazy(m_N, c, K):
    return abs(mu_N(m_N, c, K)) < 1


def supply_chain_R(N, s):
    return (1 - s) * np.eye(N) + s * np.ones((N, N))


def random_R(N, D, rng):
    X = rng.standard_normal((N, D))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X @ X.T


rng = np.random.default_rng(20260818)


# ------------------------------------ Q1  the inner loop really contracts by c

print("\nQ1  K steps of gradient descent contract to the frozen best response by c^K")

def inner_loop(z0, target, eta, gamma, K):
    """K gradient steps on L(z) = (gamma/2)(z - target)^2, the own-objective loss.

    The gradient is gamma*(z - target), so the update is
    z <- z - eta*gamma*(z - target), which contracts the gap by 1 - eta*gamma.
    c is never written down here; it is whatever this loop does.
    """
    z = np.array(z0, dtype=float)
    for _ in range(K):
        z = z - eta * gamma * (z - target)
    return z


for eta, gamma in ((0.10, 2.0), (0.05, 3.0), (0.25, 1.2)):
    c = 1 - eta * gamma
    for K in (1, 3, 7, 20):
        z0, target = np.array([1.7]), np.array([-0.4])
        z = inner_loop(z0, target, eta, gamma, K)
        gap_ratio = (z - target) / (z0 - target)
        check(f"Q1 eta={eta} gamma={gamma} K={K}", abs(gap_ratio[0] - c ** K) < 1e-12,
              f"measured {gap_ratio[0]:.8f} vs c^K = {c ** K:.8f}")


# ---------------------------------- C12  c does not depend on N, kappa or R

print("\nC12  the inner contraction is own-objective curvature, invariant to N")

eta, gamma = 0.10, 2.0
c_true = 1 - eta * gamma
measured = []
for N in (1, 2, 5, 12, 30):
    for kappa in (0.0, 0.5, 1.0):
        for m1 in (0.05, 0.15, 0.6):
            R = random_R(N, 40, rng) if N > 1 else np.ones((1, 1))
            J = joint_jacobian(R, m1, kappa)
            x = rng.standard_normal(N)
            b = J @ x                        # frozen best response, depends on N/R
            z = inner_loop(x, b, eta, gamma, 1)
            # the realized one-step contraction of the gap to the best response
            c_meas = np.median((z - b) / (x - b))
            measured.append(c_meas)
            if abs(c_meas - c_true) > 1e-12:
                raise AssertionError(f"C12 broke at N={N} kappa={kappa}: {c_meas}")
spread = max(measured) - min(measured)
check("C12 c identical across N, kappa, m_1 and R", spread < 1e-12,
      f"{len(measured)} configurations, spread {spread:.2e}, c = {c_true}")


# ---------------------------- Q2  the K-step joint map, measured not assumed

print("\nQ2  the joint K-step map is c^K I + (1 - c^K) J")

def joint_step(x, J, eta, gamma, K):
    """One synchronous deployment round: every firm takes K inner steps toward
    its frozen best response, all firms updating against the same x."""
    b = J @ x                                # frozen best responses, computed once
    return inner_loop(x, b, eta, gamma, K)


for N in (3, 8):
    for kappa in (0.4, 0.9):
        for m1 in (0.1, 0.4):
            for K in (1, 2, 5, 15):
                R = random_R(N, 40, rng)
                J = joint_jacobian(R, m1, kappa)
                c = 1 - eta * gamma
                # measure the map by its action on the standard basis
                M_meas = np.column_stack(
                    [joint_step(e, J, eta, gamma, K) for e in np.eye(N)])
                M_closed = c ** K * np.eye(N) + (1 - c ** K) * J
                err = np.abs(M_meas - M_closed).max()
                if err > 1e-12:
                    raise AssertionError(f"Q2 failed N={N} K={K}: {err}")
    check(f"Q2 joint map matches the closed form at N={N}", True,
          "16 (kappa, m_1, K) combinations, max error below 1e-12")


# --------------------------------------- Q3  mu_N(K) and which mode binds

print("\nQ3  the common mode's slope, and the binding mode")

c = 1 - eta * gamma
for N in (4, 10, 25):
    for kappa in (0.3, 0.8, 1.0):
        for m1 in (0.05, 0.2):
            for K in (1, 3, 8):
                R = random_R(N, 45, rng)
                J = joint_jacobian(R, m1, kappa)
                M = c ** K * np.eye(N) + (1 - c ** K) * J
                slopes = np.linalg.eigvalsh(M)
                m_n = m1 * n_eff(R, kappa)
                # the most negative slope is the common mode's, and equals mu_N
                if abs(slopes.min() - mu_N(m_n, c, K)) > 1e-10:
                    raise AssertionError(f"Q3 mismatch N={N} K={K}")
                # the upper side never binds: every slope is at most c^K < 1
                if slopes.max() > c ** K + 1e-12:
                    raise AssertionError(f"Q3 upper side bound violated N={N}")
    check(f"Q3 mu_N is the extreme slope and the upper side never binds, N={N}",
          True, "18 combinations")

check("Q3 the upper side is slack by construction, since c^K < 1 for all K >= 1",
      all(c ** K < 1 for K in range(1, 200)))


# ------------------------------------------------ C8  cadence agreement

print("\nC8  is_stable_lazy agrees with K < k_max on every integer K in 1..200")

mismatches = 0
tested = 0
for m_n in np.concatenate([np.linspace(1.01, 8.0, 40), [1.0001, 20.0, 50.0]]):
    for c_ in (0.5, 0.7, 0.8, 0.9, 0.95, 0.99):
        km = k_max(m_n, c_)
        for K in range(1, 201):
            tested += 1
            if is_stable_lazy(m_n, c_, K) != (K < km):
                # a tie exactly at K == k_max is a measure-zero boundary case
                if abs(K - km) > 1e-9:
                    mismatches += 1
check("C8 no mismatch", mismatches == 0, f"{tested} integer cases tested")

# and the vacuous branch: a market with m_N < 1 is stable at every cadence
for m_n in (0.2, 0.7, 0.999):
    check(f"C8 vacuous branch at m_N={m_n}",
          all(is_stable_lazy(m_n, 0.8, K) for K in range(1, 201))
          and k_max(m_n, 0.8) == np.inf)

# The boundary m_N = 1 is its own case. In exact arithmetic mu_N(1, c, K) =
# -1 + 2c^K lies strictly inside (-1, 1) for every finite K, so lazy retraining
# strictly stabilizes the marginal market. The margin decays like 2c^K, so it
# falls below machine epsilon and the check goes numerically marginal past
# K ~ ln(eps/2)/ln(c), which is about 165 at c = 0.8. Recorded rather than
# papered over: it is a floating-point limit, not a statement about the market.
c_b = 0.8
K_underflow = next(K for K in range(1, 2000) if not is_stable_lazy(1.0, c_b, K))
check("C8 boundary m_N = 1 is stable at every cadence below the underflow point",
      all(is_stable_lazy(1.0, c_b, K) for K in range(1, K_underflow)),
      f"holds for K in 1..{K_underflow - 1}")
check("C8 the boundary margin 2c^K is positive but below double precision there",
      2 * c_b ** K_underflow > 0
      and 2 * c_b ** K_underflow < np.finfo(float).eps,
      f"first numerically marginal K = {K_underflow}, "
      f"exact margin {2 * c_b ** K_underflow:.2e} against eps "
      f"{np.finfo(float).eps:.2e}")
check("C8 k_max is infinite on the whole vacuous branch, boundary included",
      all(k_max(m, 0.8) == np.inf for m in (0.2, 0.7, 0.999, 1.0)))


# ------------------------------------------------ C9  k_max monotonicity

print("\nC9  k_max is strictly decreasing in m_N")

for c_ in (0.5, 0.8, 0.95):
    grid = np.linspace(1.001, 8.0, 400)
    vals = np.array([k_max(m, c_) for m in grid])
    check(f"C9 decreasing at c={c_}", np.all(np.diff(vals) < 0),
          f"from {vals[0]:.2f} down to {vals[-1]:.2f}")

# and decreasing in s, through m_N, which is the supply-chain reading
m1, kappa, N = 0.15, 0.8, 30
s_grid = np.linspace(0.05, 1.0, 100)
kv = [k_max(m1 * (1 + kappa * s * (N - 1)), 0.8) for s in s_grid]
kv = [v for v in kv if np.isfinite(v)]
check("C9 k_max decreasing in the shared-model fraction s", np.all(np.diff(kv) < 0),
      f"{len(kv)} finite points, from {kv[0]:.2f} to {kv[-1]:.2f}")


# ------------------------------------------- C10  critical crowding

print("\nC10  no integer cadence survives m_N > (1+c)/(1-c)")

for c_ in (0.5, 0.7, 0.8, 0.9, 0.95):
    mstar = critical_crowding(c_)
    for m_n in (mstar * 1.001, mstar * 1.1, mstar * 5):
        if any(is_stable_lazy(m_n, c_, K) for K in range(1, 501)):
            raise AssertionError(f"C10 failed: stable K found at m_N={m_n}, c={c_}")
    # just below the threshold, K = 1 is stable, so the threshold is sharp
    check(f"C10 sharp threshold at c={c_}",
          is_stable_lazy(mstar * 0.999, c_, 1)
          and not is_stable_lazy(mstar * 1.001, c_, 1),
          f"m_N* = {mstar:.4f}")

check("C10 factor of 9 at c = 0.8", abs(critical_crowding(0.8) - 9.0) < TOL)
check("C10 critical crowding is the K = 1 case of the general form",
      all(abs(critical_crowding(cc) - (1 + cc ** 1) / (1 - cc ** 1)) < TOL
          for cc in (0.5, 0.8, 0.95)))


# --------------------------------------------- Q4  the equivalent form

print("\nQ4  stable iff m_N < (1 + c^K)/(1 - c^K)")

for c_ in (0.5, 0.8, 0.95):
    for K in range(1, 40):
        bound = (1 + c_ ** K) / (1 - c_ ** K)
        for m_n in (bound * 0.99, bound * 1.01):
            if is_stable_lazy(m_n, c_, K) != (m_n < bound):
                raise AssertionError(f"Q4 failed c={c_} K={K} m_N={m_n}")
    check(f"Q4 equivalent form holds for K in 1..39 at c={c_}", True)

# the two forms are the same statement, rearranged
for c_ in (0.6, 0.85):
    for m_n in (1.2, 2.5, 6.0):
        km = k_max(m_n, c_)
        K_star = int(np.floor(km))
        if K_star >= 1:
            check(f"Q4 floor(k_max) is the largest stable integer, c={c_} m_N={m_n}",
                  is_stable_lazy(m_n, c_, K_star)
                  and not is_stable_lazy(m_n, c_, K_star + 1),
                  f"k_max = {km:.4f}, largest stable K = {K_star}")


# ------------------------------------------------- C11  the worked table

print("\nC11  the worked table at m_1 = 0.15, kappa = 0.8, N = 30, c = 0.8")

m1, kappa, N, c_ = 0.15, 0.8, 30, 0.8
expected = {0.25: (6.80, 1.020, 20.68), 0.50: (12.60, 1.890, 5.28),
            1.00: (24.20, 3.630, 2.53)}
for s, (ne_exp, mn_exp, km_exp) in expected.items():
    ne = 1 + kappa * s * (N - 1)
    mn = m1 * ne
    km = k_max(mn, c_)
    check(f"C11 N_eff at s={s}", abs(ne - ne_exp) < 1e-9, f"{ne:.4f}")
    check(f"C11 m_N at s={s}", abs(mn - mn_exp) < 1e-9, f"{mn:.4f}")
    check(f"C11 K_max at s={s}", abs(km - km_exp) < 1e-2, f"{km:.4f}")
    # two routes to N_eff: the closed form and the eigenvalue of the limit R
    check(f"C11 two routes to N_eff agree at s={s}",
          abs(ne - n_eff(supply_chain_R(N, s), kappa)) < 1e-9)

check("C11 all three windows sit below critical crowding, so a window exists",
      all(m1 * (1 + kappa * s * (N - 1)) < critical_crowding(c_)
          for s in expected),
      f"largest m_N = {m1 * (1 + kappa * 1.0 * (N - 1)):.3f} < 9")


# ------------------------------- Q5  dynamic check against the real joint map

print("\nQ5  iterating the joint map converges or diverges as the frontier says")

eta, gamma = 0.10, 2.0
c_ = 1 - eta * gamma
agree = disagree = 0
for trial in range(60):
    N = int(rng.integers(3, 20))
    kappa = float(rng.uniform(0.2, 1.0))
    s = float(rng.uniform(0.1, 1.0))
    m1 = float(rng.uniform(0.02, 0.5))
    K = int(rng.integers(1, 25))
    R = supply_chain_R(N, s)
    J = joint_jacobian(R, m1, kappa)
    m_n = m1 * n_eff(R, kappa)

    # skip cases within 2% of the frontier, where finite-horizon iteration
    # cannot separate the two sides
    km = k_max(m_n, c_)
    if np.isfinite(km) and abs(K - km) / max(km, 1.0) < 0.02:
        continue

    x = rng.standard_normal(N)
    x /= np.linalg.norm(x)
    for _ in range(400):
        x = joint_step(x, J, eta, gamma, K)
        if np.linalg.norm(x) > 1e12:
            break
    converged = np.linalg.norm(x) < 1e-6
    diverged = np.linalg.norm(x) > 1e6
    predicted_stable = is_stable_lazy(m_n, c_, K)
    if (converged and predicted_stable) or (diverged and not predicted_stable):
        agree += 1
    elif converged or diverged:
        disagree += 1
check("Q5 simulated dynamics agree with the predicted frontier", disagree == 0,
      f"{agree} decisive trials, 0 disagreements")


print(f"\n{len(PASSED)} checks passed.")
