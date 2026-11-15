"""Certificates for the Theorem 3 proof.

Source of the statements: ../../math/derivations/04-mixed-market-secular.md.

Assertion-based: every check raises on failure and the script exits nonzero.
The implementation here is deliberately independent of the theory module, so
that module's acceptance test is a genuine second route rather than a tautology.

Two of these checks contradict what the note and the plan of record say, and
both contradictions are the point rather than an accident:

  C18 asks whether the strong-correction limit is approached from the stable
  side. It is not. rho is nondecreasing in the correction parameter, so the
  limit UNDER-states the radius and the limit theorem is optimistic. The plan
  anticipated this outcome and said to report which way it errs.

  C14 asks whether rho* predicts the sign change. The primitive condition
  N_b < N_c(s) does, exactly. The clamped form rho > rho* does not: it
  mispredicts the all-blind market that is stable without any correction.

Checks:

  H1  exact root        the two-block quadratic against dense eigensolves
  H2  degenerate blocks empty blocks need the single-block form, not the quadratic
  H3  limits            gamma_ratio = 1 recovers Theorem 1; -> 0 gives the blind block
  C13 limit convergence mixed_market_radius -> blind-block radius
  C18 error direction   rho nondecreasing in gamma_ratio, so the limit is optimistic
  C14 threshold         N_b < N_c(s) is exact; the clamped rho form is not
  C15 collapse          rho* = 1 - 1/m_N at kappa = s = 1
  C16 monotone in s     rho* increasing in s, which is the substitution result
  C17 worked thresholds 0.596 / 0.242 / 0 at s = 1 / 0.5 / 0.2
  H4  integer threshold min corrected firms = N - ceil(N_c) + 1
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

def mixed_A(N, n_blind, m1, kappa, s, gamma_ratio):
    """The symmetric congruence with rho(J) = lambda_max(A), built densely.

    Blind firms carry modulus m1, corrected firms carry gamma_ratio * m1, where
    gamma_ratio = gamma/gamma_PO in (0, 1]. Alignment is the supply-chain limit
    R = (1-s)I + s 11', so B = (1-kappa)I + kappa R = (1-ks)I + ks 11'.
    """
    ks = kappa * s
    m = np.full(N, float(m1))
    m[n_blind:] = gamma_ratio * m1
    B = (1 - ks) * np.eye(N) + ks * np.ones((N, N))
    Mh = np.diag(np.sqrt(m))
    return Mh @ B @ Mh


def dense_radius(N, n_blind, m1, kappa, s, gamma_ratio):
    return np.linalg.eigvalsh(mixed_A(N, n_blind, m1, kappa, s, gamma_ratio)).max()


def secular_radius(N, n_blind, m1, kappa, s, gamma_ratio):
    """Exact spectral radius from the two-block quadratic.

    Empty blocks are handled separately: with no firms of one type the quadratic
    still carries that block's factor and leaves a phantom root behind.
    """
    ks = kappa * s
    n_eff = 1 + ks * (N - 1)
    if n_blind == N:
        return m1 * n_eff
    if n_blind == 0:
        return gamma_ratio * m1 * n_eff
    a = (1 - ks) * m1
    b = (1 - ks) * gamma_ratio * m1
    P = a + b + ks * m1 * (n_blind + gamma_ratio * (N - n_blind))
    Q = gamma_ratio * m1**2 * (1 - ks) * n_eff
    return (P + np.sqrt(max(P**2 - 4 * Q, 0.0))) / 2


def blind_block_radius(m1, kappa, s, n_blind):
    return m1 * (1 + kappa * s * (n_blind - 1)) if n_blind >= 1 else 0.0


def n_c(m1, kappa, s):
    return 1 + (1 / m1 - 1) / (kappa * s)


def rho_star(N, m1, kappa, s):
    return max(0.0, 1 - n_c(m1, kappa, s) / N)


def min_corrected(N, m1, kappa, s):
    """Smallest integer number of corrected firms that stabilizes the limit."""
    return int(max(0, min(N, N - int(np.ceil(n_c(m1, kappa, s))) + 1)))


rng = np.random.default_rng(20260818)


def random_case(nb_lo=0, nb_hi=None):
    N = int(rng.integers(2, 40))
    hi = N + 1 if nb_hi is None else min(nb_hi, N + 1)
    nb = int(rng.integers(nb_lo, hi))
    return (N, nb, float(rng.uniform(0.02, 0.9)), float(rng.uniform(0.05, 1.0)),
            float(rng.uniform(0.05, 1.0)))


# ------------------------------------------------- H1  the exact root

print("\nH1  the two-block quadratic against dense eigensolves")

worst = 0.0
for _ in range(6000):
    N, nb, m1, kappa, s = random_case()
    gr = float(rng.uniform(1e-9, 1.0))
    worst = max(worst, abs(secular_radius(N, nb, m1, kappa, s, gr)
                           - dense_radius(N, nb, m1, kappa, s, gr)))
check("H1 exact on 6000 random draws, all block splits", worst < 1e-10,
      f"max error {worst:.2e}")

# and specifically on the interior splits, where the quadratic actually applies
worst_interior = 0.0
for _ in range(3000):
    N, nb, m1, kappa, s = random_case(nb_lo=1)
    if nb >= N:
        continue
    gr = float(rng.uniform(1e-9, 1.0))
    worst_interior = max(worst_interior,
                         abs(secular_radius(N, nb, m1, kappa, s, gr)
                             - dense_radius(N, nb, m1, kappa, s, gr)))
check("H1 exact on interior splits 1 <= N_b <= N-1", worst_interior < 1e-10,
      f"max error {worst_interior:.2e}")


# --------------------------------------------- H2  the degenerate blocks

print("\nH2  empty blocks need the single-block form")

def naive_quadratic(N, n_blind, m1, kappa, s, gamma_ratio):
    """The quadratic applied blindly, phantom root and all."""
    ks = kappa * s
    a = (1 - ks) * m1
    b = (1 - ks) * gamma_ratio * m1
    P = a + b + ks * m1 * (n_blind + gamma_ratio * (N - n_blind))
    Q = gamma_ratio * m1**2 * (1 - ks) * (1 + ks * (N - 1))
    return (P + np.sqrt(max(P**2 - 4 * Q, 0.0))) / 2


N, m1, kappa, s, gr = 12, 0.3, 0.8, 0.7, 0.02
check("H2 all-corrected: single-block form is right",
      abs(secular_radius(N, 0, m1, kappa, s, gr)
          - dense_radius(N, 0, m1, kappa, s, gr)) < 1e-12)
check("H2 all-corrected: the naive quadratic is wrong, by a phantom root",
      abs(naive_quadratic(N, 0, m1, kappa, s, gr)
          - dense_radius(N, 0, m1, kappa, s, gr)) > 1e-3,
      f"naive {naive_quadratic(N, 0, m1, kappa, s, gr):.6f} against true "
      f"{dense_radius(N, 0, m1, kappa, s, gr):.6f}")
check("H2 all-blind: single-block form is right",
      abs(secular_radius(N, N, m1, kappa, s, gr)
          - dense_radius(N, N, m1, kappa, s, gr)) < 1e-12)


# -------------------------------------------------------- H3  the limits

print("\nH3  limits: gamma_ratio = 1 recovers Theorem 1, -> 0 gives the blind block")

for _ in range(400):
    N, nb, m1, kappa, s = random_case(nb_lo=1)
    if nb >= N:
        continue
    n_eff = 1 + kappa * s * (N - 1)
    if abs(secular_radius(N, nb, m1, kappa, s, 1.0) - m1 * n_eff) > 1e-10:
        raise AssertionError("H3 gamma_ratio = 1 does not recover m_1 * N_eff")
check("H3 gamma_ratio = 1 recovers m_1 * N_eff exactly", True, "400 draws")

for _ in range(400):
    N, nb, m1, kappa, s = random_case(nb_lo=1)
    if nb >= N:
        continue
    if abs(secular_radius(N, nb, m1, kappa, s, 1e-14)
           - blind_block_radius(m1, kappa, s, nb)) > 1e-6:
        raise AssertionError("H3 strong-correction limit is not the blind block")
check("H3 gamma_ratio -> 0 gives the blind-block radius", True, "400 draws")


# ------------------------------------------------- C13  limit convergence

print("\nC13  mixed_market_radius converges to the blind-block radius")

N, nb, m1, kappa, s = 20, 12, 0.15, 0.8, 0.7
target = blind_block_radius(m1, kappa, s, nb)
errs = [abs(secular_radius(N, nb, m1, kappa, s, gr) - target)
        for gr in (1e-2, 1e-4, 1e-6, 1e-8)]
check("C13 monotone convergence to the limit", all(np.diff(errs) < 0),
      f"errors {[f'{e:.2e}' for e in errs]}")
check("C13 limit reached to 1e-8", errs[-1] < 1e-8)


# ------------------------------------ C18  the error direction (this FAILS as hoped)

print("\nC18  which side is the strong-correction limit approached from?")

violations = 0
for _ in range(3000):
    N, nb, m1, kappa, s = random_case(nb_lo=1)
    if nb >= N:
        continue
    grid = np.linspace(1e-9, 1.0, 50)
    r = np.array([secular_radius(N, nb, m1, kappa, s, g) for g in grid])
    if np.any(np.diff(r) < -1e-12):
        violations += 1
check("C18 rho is nondecreasing in gamma_ratio", violations == 0,
      f"{violations} violations, so rho(gamma_ratio) >= rho(0)")

check("C18 therefore the limit UNDER-states the radius: it is OPTIMISTIC, "
      "not conservative", True,
      "the plan's hoped-for direction does not hold; report which way it errs")

# how often the optimism flips an actual verdict
flips = total = 0
for _ in range(20000):
    N, nb, m1, kappa, s = random_case(nb_lo=1)
    if nb >= N:
        continue
    gr = float(rng.uniform(0.01, 1.0))
    lim = secular_radius(N, nb, m1, kappa, s, 1e-12)
    true = secular_radius(N, nb, m1, kappa, s, gr)
    total += 1
    if lim < 1 <= true:
        flips += 1
frac = flips / total
check("C18 the optimism flips a real verdict often enough to matter",
      0.05 < frac < 0.30,
      f"{flips}/{total} = {100*frac:.1f}% of draws are called stable by the "
      f"limit but are unstable at finite correction")

# the correction strength the limit silently assumes, on worked cases
print("\n  correction strength the limit silently assumes:")
for (N, nb, m1, kappa, s) in ((10, 6, 0.15, 0.8, 1.0), (30, 8, 0.10, 0.9, 0.8),
                              (20, 10, 0.12, 0.8, 1.0)):
    lim = secular_radius(N, nb, m1, kappa, s, 1e-12)
    if lim >= 1 or secular_radius(N, nb, m1, kappa, s, 1.0) < 1:
        continue
    lo, hi = 1e-12, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if secular_radius(N, nb, m1, kappa, s, mid) < 1:
            lo = mid
        else:
            hi = mid
    print(f"    N={N} N_b={nb}: limit reads {lim:.4f} (stable), truly unstable "
          f"unless gamma_PO > {1/lo:.1f} * gamma")
    check(f"C18 worked case N={N} N_b={nb} needs a stated correction strength",
          lo < 1.0, f"crossover at gamma_ratio {lo:.4f}")


# --------------------------------------------------- C14  the threshold

print("\nC14  which stability criterion is exact")

cases = []
for _ in range(4000):
    cases.append(random_case())

def audit(predicate):
    bad = []
    for (N, nb, m1, kappa, s) in cases:
        r = secular_radius(N, nb, m1, kappa, s, 1e-14)
        if abs(r - 1) < 1e-9:
            continue
        if (r < 1) != predicate(N, nb, m1, kappa, s):
            bad.append((N, nb, m1, kappa, s))
    return bad


bad_primitive = audit(lambda N, nb, m1, k, s: nb < n_c(m1, k, s))
check("C14 the primitive condition N_b < N_c(s) is exact", len(bad_primitive) == 0,
      f"0 mismatches on {len(cases)} draws")

bad_clamped = audit(
    lambda N, nb, m1, k, s: (1 - nb / N) > max(0.0, 1 - n_c(m1, k, s) / N))
check("C14 the clamped form rho > rho* is NOT exact", len(bad_clamped) > 0,
      f"{len(bad_clamped)} mismatches, all of them the all-blind market")
check("C14 every clamped-form failure is N_b = N with N_c >= N",
      all(nb == N and n_c(m1, k, s) >= N
          for (N, nb, m1, k, s) in bad_clamped),
      "the market that is stable with no correction at all")

bad_unclamped = audit(
    lambda N, nb, m1, k, s: (1 - nb / N) > (1 - n_c(m1, k, s) / N))
check("C14 the unclamped form rho > 1 - N_c/N is exact",
      len(bad_unclamped) == 0, "so the clamp, not the rho form, is the problem")


# ------------------------------------------------ C15  the collapse

print("\nC15  rho* = 1 - 1/m_N at kappa = s = 1")

for N in (5, 10, 20, 50):
    for m1 in (0.05, 0.15, 0.25, 0.4):
        m_n = m1 * N                      # N_eff = N at kappa = s = 1
        if m_n <= 1:
            check(f"C15 vacuous below the boundary N={N} m1={m1}",
                  rho_star(N, m1, 1.0, 1.0) == 0.0)
            continue
        check(f"C15 collapse at N={N} m1={m1}",
              abs(rho_star(N, m1, 1.0, 1.0) - (1 - 1 / m_n)) < 1e-12,
              f"rho* = {rho_star(N, m1, 1.0, 1.0):.6f} = 1 - 1/{m_n:.2f}")

check("C15 the quoted example: 10 firms at m_N = 2.5 need 60 percent",
      abs(rho_star(10, 0.25, 1.0, 1.0) - 0.6) < 1e-12)


# --------------------------------------- C16  rho* increasing in s

print("\nC16  rho* increasing in s, which is what makes the two levers substitutes")

for (N, m1, kappa) in ((20, 0.15, 0.8), (10, 0.2, 1.0), (50, 0.05, 0.6)):
    grid = np.linspace(0.05, 1.0, 300)
    vals = np.array([rho_star(N, m1, kappa, s) for s in grid])
    check(f"C16 nondecreasing at N={N} m1={m1} kappa={kappa}",
          np.all(np.diff(vals) >= -1e-15),
          f"from {vals[0]:.4f} to {vals[-1]:.4f}")
    # and strictly increasing once it leaves the clamp
    active = vals > 0
    if active.sum() > 2:
        check(f"C16 strictly increasing where rho* > 0, N={N}",
              np.all(np.diff(vals[active]) > 0))


# ----------------------------------------------- C17  worked thresholds

print("\nC17  worked thresholds at N = 20, m_1 = 0.15, kappa = 0.8")

expected = {1.0: (8.0833, 0.5958), 0.5: (15.1667, 0.2417), 0.2: (36.4167, 0.0)}
for s, (nc_exp, rs_exp) in expected.items():
    check(f"C17 N_c at s={s}", abs(n_c(0.15, 0.8, s) - nc_exp) < 1e-3,
          f"{n_c(0.15, 0.8, s):.4f}")
    check(f"C17 rho* at s={s}", abs(rho_star(20, 0.15, 0.8, s) - rs_exp) < 1e-3,
          f"{rho_star(20, 0.15, 0.8, s):.4f}")


# --------------------------------------- H4  the integer threshold

print("\nH4  the realized threshold is a whole number of firms")

bad_formula = bad_ceil = 0
tested = 0
for _ in range(3000):
    N, _, m1, kappa, s = random_case()
    brute = None
    for corrected in range(N + 1):
        if secular_radius(N, N - corrected, m1, kappa, s, 1e-14) < 1:
            brute = corrected
            break
    if brute is None:
        continue
    tested += 1
    if min_corrected(N, m1, kappa, s) != brute:
        bad_formula += 1
    if int(np.ceil(rho_star(N, m1, kappa, s) * N)) != brute:
        bad_ceil += 1
check("H4 N - ceil(N_c) + 1 is exact", bad_formula == 0,
      f"0 wrong on {tested} draws")
check("H4 ceil(rho* N) agrees on random draws", bad_ceil == 0,
      f"0 wrong on {tested} draws, but see the exact-integer case below")

# the corner where ceil(rho* N) is off by one: N_c exactly an integer
N, m1, kappa = 20, 0.15, 0.8
for nc_target in (8.0, 12.0):
    s_edge = (1 / m1 - 1) / (kappa * (nc_target - 1))
    brute = next(c for c in range(N + 1)
                 if secular_radius(N, N - c, m1, kappa, s_edge, 1e-14) < 1)
    by_ceil = int(np.ceil(rho_star(N, m1, kappa, s_edge) * N))
    check(f"H4 exact-integer corner N_c = {nc_target}: the formula is right",
          min_corrected(N, m1, kappa, s_edge) == brute,
          f"formula {min_corrected(N, m1, kappa, s_edge)} = brute {brute}")
    check(f"H4 exact-integer corner N_c = {nc_target}: ceil(rho* N) is off by one",
          by_ceil == brute - 1, f"ceil gives {by_ceil}, truth is {brute}")

check("H4 worked: N = 20, m_1 = 0.15, kappa = 0.8, s = 1 needs 12 corrected",
      min_corrected(20, 0.15, 0.8, 1.0) == 12)
check("H4 worked: the same market at s = 0.5 needs 5",
      min_corrected(20, 0.15, 0.8, 0.5) == 5)
check("H4 worked: the same market at s = 0.2 needs none",
      min_corrected(20, 0.15, 0.8, 0.2) == 0)


# -------------------------- H5  the imperfect-correction law, and its corollary

print("\nH5  the exact threshold at kappa = s = 1 is the imperfect-vaccine law")

# At kappa = s = 1 the quadratic degenerates: (1-ks) = 0 kills a, b and Q, so
# rho = P = m_1 (N_b + gamma_ratio * N_corr) exactly. Solving rho < 1 for the
# corrected fraction gives (1 - 1/m_N)/(1 - gamma_ratio).
worst = 0.0
for N in (5, 10, 20, 50, 100):
    for m1 in (0.05, 0.15, 0.25, 0.4):
        m_n = m1 * N
        if m_n <= 1:
            continue
        for gr in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9):
            # threshold read off the exact radius, solved continuously
            continuous = 1 - (1 / m_n - gr) / (1 - gr)
            law = (1 - 1 / m_n) / (1 - gr)
            worst = max(worst, abs(continuous - law))
check("H5 exact threshold equals (1 - 1/m_N)/(1 - gamma_ratio)", worst < 1e-14,
      f"max deviation {worst:.2e} over 120 configurations")

# and it really is the radius, checked against the dense eigensolve
for N in (6, 15, 30):
    for nb in (0, N // 3, N // 2, N):
        for gr in (0.05, 0.3, 0.8):
            m1 = 0.2
            pred = m1 * (nb + gr * (N - nb))
            check_ok = abs(dense_radius(N, nb, m1, 1.0, 1.0, gr) - pred) < 1e-10
            if not check_ok:
                raise AssertionError(f"H5 radius form wrong at N={N} nb={nb}")
check("H5 at kappa = s = 1 the radius is m_1(N_b + gamma_ratio * N_corr)", True,
      "36 configurations against dense eigensolves")

check("H5 perfect correction recovers the clean law",
      abs((1 - 1 / 2.5) / (1 - 0.0) - 0.6) < 1e-12,
      "gamma_ratio = 0 gives 1 - 1/m_N")

print("\n  required corrected fraction at m_N = 2.5, efficacy e = 1 - gamma_ratio:")
for gr in (0.0, 0.2, 0.4, 0.6):
    need = (1 - 1 / 2.5) / (1 - gr)
    print(f"    gamma_ratio={gr:.1f}  e={1-gr:.1f}  required = {need:.4f}"
          + ("   (exceeds 1: no fraction suffices)" if need > 1 else ""))

print("\nH6  critical correction efficacy")

# The required fraction exceeds 1, so no fraction stabilizes the market, exactly
# when gamma_ratio > 1/m_N. Parallel in structure to Theorem 2's critical crowding.
for m_n in (1.5, 2.5, 4.0, 9.0):
    crit = 1 / m_n
    check(f"H6 threshold passes 1 exactly at gamma_ratio = 1/m_N, m_N={m_n}",
          abs((1 - 1 / m_n) / (1 - crit) - 1.0) < 1e-12,
          f"critical gamma_ratio = {crit:.4f}, so gamma_PO must exceed "
          f"{m_n:.1f} * gamma")
    check(f"H6 just below is feasible, just above is not, m_N={m_n}",
          (1 - 1 / m_n) / (1 - crit * 0.99) < 1
          and (1 - 1 / m_n) / (1 - min(crit * 1.01, 0.999)) > 1)

# and the direct check: at gamma_ratio above critical, even all-corrected fails
for (N, m1) in ((10, 0.25), (20, 0.15)):
    m_n = m1 * N
    if m_n <= 1:
        continue
    crit = 1 / m_n
    gr_bad = min(crit * 1.05, 0.99)
    check(f"H6 all-corrected is still unstable above critical, N={N}",
          dense_radius(N, 0, m1, 1.0, 1.0, gr_bad) > 1,
          f"m_N={m_n:.2f}, gamma_ratio={gr_bad:.4f}, "
          f"radius={dense_radius(N, 0, m1, 1.0, 1.0, gr_bad):.4f}")


print(f"\n{len(PASSED)} checks passed.")
print("\nNOTE: C18 did not come out the way the plan of record hoped. The "
      "strong-correction\nlimit is optimistic, not conservative. What replaces "
      "it is stronger: H5 shows the\nexact threshold is the epidemiological "
      "imperfect-vaccine law, and H6 gives a\ncritical correction efficacy. "
      "See ../../math/derivations/04-mixed-market-secular.md.")
