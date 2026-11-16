"""Certificates for the Theorem 1 proof.

Source of the statements: ../../math/derivations/01-alignment-spectrum.md and
../../math/derivations/02-supply-chain-concentration.md.

Assertion-based: every check raises on failure and the script exits nonzero.
That is the form CERTIFICATES.md requires and the earlier
verify_theorem1_anchors.py does not have, so this file is also the template for
converting that one.

Checks, in the order the derivation makes them:

  P1  reduction lemma       J = -m_1[(1-kappa)I + kappa R] from actual E_i
  P2  spectral range        1 <= lambda_max(R) <= N, both equality cases
  P3  N_eff identity        rho(J) = m_1 * N_eff exactly, no absolute-value slack
  P4  anchors               monoculture, orthogonal, simplex
  P5  mean is a lower bound N_eff >= 1 + kappa(N-1)*mean, equality iff R1 is 1
  P6  clustered gap         the 1.757 factor the math note quotes
  P7  concentration         max|r_ij - s| = O(1/d), lambda_max -> 1 + s(N-1)
  P8  heterogeneous moduli  max_i m_i <= rho(J) <= max_i m_i * N_eff
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

def joint_jacobian(R, m1, kappa):
    """The generalized joint retraining Jacobian J = -m1[(1-kappa)I + kappa R]."""
    N = R.shape[0]
    return -m1 * ((1 - kappa) * np.eye(N) + kappa * R)


def n_eff(R, kappa):
    return 1 + kappa * (np.linalg.eigvalsh(R).max() - 1)


def radius(M):
    return np.abs(np.linalg.eigvals(M)).max()


def mean_alignment(R):
    """Off-diagonal mean. A foil, never a stability statistic. See P5."""
    N = R.shape[0]
    return (R.sum() - np.trace(R)) / (N * (N - 1))


def alignment_matrix(E):
    """R from response Jacobians E of shape (N, d, d), by vec inner products."""
    V = E.reshape(E.shape[0], -1)
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    return V @ V.T


def simplex_R(N):
    return (N / (N - 1)) * np.eye(N) - (1.0 / (N - 1)) * np.ones((N, N))


def random_R(N, D, rng):
    """A valid alignment matrix: Gram of N unit vectors in R^D."""
    X = rng.standard_normal((N, D))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X @ X.T


# --------------------------------------------------- P1  the reduction lemma

print("\nP1  reduction lemma: J = -m_1[(1-kappa)I + kappa R] from actual E_i")

def felt_jacobian(E, beta, gamma, kappa):
    """Jacobian of the felt-distortion retraining map, built without using R.

    Firm i's deviation is x_i along its own response direction. The pool
    carries Z = sum_j x_j E_j. Firm i feels its own contribution in full and
    its competitors' with weight kappa, projected on its own unit response
    direction, and retrains to x_i^+ = -(beta/gamma) * felt_i.
    """
    N = E.shape[0]
    V = E.reshape(N, -1)
    U = V / np.linalg.norm(V, axis=1, keepdims=True)   # unit response directions

    def step(x):
        out = np.empty(N)
        for i in range(N):
            own = x[i] * V[i]
            cross = kappa * sum(x[j] * V[j] for j in range(N) if j != i)
            out[i] = -(beta / gamma) * U[i] @ (own + cross)
        return out

    # numerical Jacobian of a linear map: columns are images of basis vectors
    return np.column_stack([step(e) for e in np.eye(N)])


rng = np.random.default_rng(20260818)
for N, d, kappa in ((3, 4, 0.8), (5, 6, 0.35), (8, 5, 1.0), (6, 7, 0.0)):
    eps, beta, gamma = 0.37, 1.4, 2.9
    E = rng.standard_normal((N, d, d))
    E *= eps / np.linalg.norm(E.reshape(N, -1), axis=1)[:, None, None]  # equal moduli
    m1 = eps * beta / gamma
    J_measured = felt_jacobian(E, beta, gamma, kappa)
    J_closed = joint_jacobian(alignment_matrix(E), m1, kappa)
    err = np.abs(J_measured - J_closed).max()
    check(f"P1 N={N} d={d} kappa={kappa}", err < 1e-12, f"max|J_meas - J_closed| = {err:.2e}")

# the monoculture corner must reproduce the inherited base law exactly
for N, kappa in ((2, 0.8), (3, 0.8), (10, 0.55)):
    E = np.repeat(rng.standard_normal((1, 4, 4)), N, axis=0)   # identical responses
    R = alignment_matrix(E)
    check(f"P1 monoculture R=11' N={N}", np.abs(R - 1).max() < 1e-12)
    check(f"P1 base law N={N} kappa={kappa}",
          abs(n_eff(R, kappa) - (1 + kappa * (N - 1))) < TOL,
          f"N_eff = {n_eff(R, kappa):.6f}")


# ----------------------------------------------------- P2  spectral range

print("\nP2  spectral range: 1 <= lambda_max(R) <= N")

for N in (3, 5, 10, 30):
    for trial in range(20):
        R = random_R(N, 64, rng)
        lam = np.linalg.eigvalsh(R).max()
        check_ok = 1 - 1e-10 <= lam <= N + 1e-10
        if not check_ok:
            raise AssertionError(f"P2 range violated: N={N} lam={lam}")
    check(f"P2 range holds on 20 random R, N={N}", True)

check("P2 lower equality at R = I", abs(np.linalg.eigvalsh(np.eye(9)).max() - 1) < TOL)
check("P2 upper equality at R = 11'",
      abs(np.linalg.eigvalsh(np.ones((9, 9))).max() - 9) < 1e-10)

# trace argument: sum of eigenvalues is N, so the mean eigenvalue is exactly 1
for N in (4, 11, 25):
    R = random_R(N, 40, rng)
    check(f"P2 trace = N at N={N}", abs(np.trace(R) - N) < 1e-10)


# --------------------------------------------------- P3  the N_eff identity

print("\nP3  rho(J) = m_1 * N_eff, with no absolute-value slack")

m1_grid = (0.05, 0.15, 0.5, 0.9)
kappa_grid = (0.0, 0.25, 0.8, 1.0)
worst = 0.0
for N in (3, 6, 12):
    for m1 in m1_grid:
        for kappa in kappa_grid:
            for trial in range(8):
                R = random_R(N, 50, rng)
                J = joint_jacobian(R, m1, kappa)
                worst = max(worst, abs(radius(J) - m1 * n_eff(R, kappa)))
check("P3 identity on 384 random configurations", worst < 1e-10,
      f"max deviation {worst:.2e}")

# The identity drops the absolute value because R is PSD and kappa <= 1, so
# every bracket (1-kappa) + kappa*lambda_i is nonnegative. Check that directly:
# it is the one step where the proof could silently pick the wrong extreme.
worst_bracket = np.inf
for N in (3, 6, 12, 30):
    for kappa in kappa_grid:
        for trial in range(15):
            lam = np.linalg.eigvalsh(random_R(N, 50, rng))
            worst_bracket = min(worst_bracket, ((1 - kappa) + kappa * lam).min())
check("P3 every bracket is nonnegative, so the radius sits at lambda_max",
      worst_bracket >= -1e-12, f"min bracket over all draws {worst_bracket:.2e}")

# Cauchy-Schwarz is what rules out the failure mode: a symmetric unit-diagonal
# matrix with entries outside [-1,1] can put the radius on lambda_min instead.
R_impossible = 4 * np.eye(3) - 3 * np.ones((3, 3))     # off-diagonal -3
lam_imp = np.linalg.eigvalsh(R_impossible)
check("P3 the failure mode needs |r_ij| > 1, which Cauchy-Schwarz forbids",
      abs(lam_imp.min()) > lam_imp.max() and abs(R_impossible[0, 1]) > 1,
      f"lambda_min = {lam_imp.min():.1f} dominates lambda_max = {lam_imp.max():.1f} "
      f"at r_ij = {R_impossible[0, 1]:.0f}")


# ------------------------------------------------------------- P4  anchors

print("\nP4  anchors")

m1, kappa = 0.15, 0.8
for N in (3, 5, 10, 30, 50):
    R = simplex_R(N)
    check(f"P4 simplex unit diagonal N={N}", abs(R[0, 0] - 1) < TOL)
    check(f"P4 simplex off-diagonal = -1/(N-1) N={N}",
          abs(R[0, 1] + 1 / (N - 1)) < TOL)

    lam = np.sort(np.linalg.eigvalsh(R))
    check(f"P4 simplex lambda_min = 0 on the all-ones direction N={N}",
          abs(lam[0]) < 1e-10)
    check(f"P4 simplex lambda_max = N/(N-1) N={N}",
          abs(lam[-1] - N / (N - 1)) < 1e-10)

    J = joint_jacobian(R, m1, kappa)
    spec = np.linalg.eigvals(J)
    claimed = m1 * (1 - kappa)                     # what the plan of record said
    truth = m1 * (1 + kappa / (N - 1))             # the actual radius
    check(f"P4 m_1(1-kappa) IS in the spectrum N={N}",
          np.abs(np.abs(spec) - claimed).min() < 1e-10)
    check(f"P4 m_1(1-kappa) is NOT the radius N={N}",
          abs(radius(J) - claimed) > 1e-6)
    check(f"P4 radius = m_1(1 + kappa/(N-1)) N={N}",
          abs(radius(J) - truth) < 1e-10, f"radius = {radius(J):.6f}")

check("P4 orthogonal: N_eff = 1", abs(n_eff(np.eye(20), kappa) - 1) < TOL)
check("P4 orthogonal: m_N = m_1",
      abs(radius(joint_jacobian(np.eye(20), m1, kappa)) - m1) < 1e-12)

# Perron-Frobenius: nonnegative R puts the leading eigenvector in the
# nonnegative orthant, and the simplex (which has negative entries) does not.
for N in (5, 12):
    R = np.abs(random_R(N, 30, rng))
    v = np.linalg.eigh(R)[1][:, -1]
    v = v * np.sign(v[np.argmax(np.abs(v))])
    check(f"P4 PF: nonneg R has a nonnegative leading eigenvector N={N}",
          (v > -1e-10).all())

# The mode swap: under the simplex the all-ones direction carries eigenvalue 0,
# the SMALLEST, so the leading eigenvector is orthogonal to it. PF does not
# apply, because the simplex has negative entries.
for N in (6, 15):
    Rs = simplex_R(N)
    ones = np.ones(N) / np.sqrt(N)
    check(f"P4 mode swap: all-ones carries lambda = 0 under the simplex N={N}",
          abs(Rs @ ones).max() < 1e-10)
    v_lead = np.linalg.eigh(Rs)[1][:, -1]
    check(f"P4 mode swap: leading eigenvector is orthogonal to all-ones N={N}",
          abs(v_lead @ ones) < 1e-8, f"|<v, 1>| = {abs(v_lead @ ones):.2e}")
    check(f"P4 simplex has negative entries, so PF does not apply N={N}",
          Rs[0, 1] < 0)


# ------------------------------------------ P5  the mean is a LOWER bound

print("\nP5  N_eff >= 1 + kappa(N-1)*mean, with equality iff R1 is parallel to 1")

def n_eff_mean_index(R, kappa):
    """What a mean-similarity diversity index would report."""
    N = R.shape[0]
    return 1 + kappa * (N - 1) * mean_alignment(R)


violations = 0
gaps = []
for N in (4, 8, 15, 30):
    for kappa in (0.3, 0.8, 1.0):
        for trial in range(30):
            R = random_R(N, 48, rng)
            true_ne, mean_ne = n_eff(R, kappa), n_eff_mean_index(R, kappa)
            if true_ne < mean_ne - 1e-10:
                violations += 1
            gaps.append(true_ne - mean_ne)
check("P5 no violation of the lower bound on 360 random R", violations == 0,
      f"min gap {min(gaps):.2e}, median gap {np.median(gaps):.4f}")

# equality case: uniform R has constant row sums, so 1 is its leading eigenvector
for N in (6, 20):
    for mbar in (0.0, 0.25, 0.7):
        R = (1 - mbar) * np.eye(N) + mbar * np.ones((N, N))
        check(f"P5 equality for uniform R, N={N} mean={mbar}",
              abs(n_eff(R, 0.8) - n_eff_mean_index(R, 0.8)) < 1e-10)

# ordering failure: the simplex minimizes the mean and beats orthogonality on lambda_max
for N in (5, 10, 30):
    Rs, Ri = simplex_R(N), np.eye(N)
    check(f"P5 ordering failure at N={N}",
          mean_alignment(Rs) < mean_alignment(Ri)
          and np.linalg.eigvalsh(Rs).max() > np.linalg.eigvalsh(Ri).max(),
          f"simplex mean {mean_alignment(Rs):+.4f} < 0, "
          f"lambda_max {N/(N-1):.4f} > 1")

# the mean floor -1/(N-1) is attained by the simplex, from 1'R1 >= 0
for N in (5, 10, 30):
    check(f"P5 mean floor -1/(N-1) attained at N={N}",
          abs(mean_alignment(simplex_R(N)) + 1 / (N - 1)) < TOL)


# ------------------------------------------------- P6  clustered gap

print("\nP6  clustered counterexample, the 1.757 factor")

N, kappa = 10, 0.8
R_clust = np.zeros((N, N))
R_clust[:3, :3] = 1.0
R_clust[3:, 3:] = np.eye(7)
lam_c = np.linalg.eigvalsh(R_clust).max()
mbar = mean_alignment(R_clust)
R_unif = (1 - mbar) * np.eye(N) + mbar * np.ones((N, N))

ne_c, ne_u = n_eff(R_clust, kappa), n_eff(R_unif, kappa)
check("P6 clustered lambda_max = 3", abs(lam_c - 3) < 1e-10)
check("P6 mean off-diagonal = 3/45", abs(mbar - 3 / 45) < TOL, f"{mbar:.6f}")
check("P6 clustered N_eff = 2.60", abs(ne_c - 2.60) < 5e-3, f"{ne_c:.4f}")
check("P6 uniform N_eff = 1.48", abs(ne_u - 1.48) < 5e-3, f"{ne_u:.4f}")
check("P6 understatement factor = 1.757", abs(ne_c / ne_u - 1.757) < 1e-3,
      f"{ne_c / ne_u:.4f}")
check("P6 at m_1 = 0.5 the true market is unstable", 0.5 * ne_c > 1,
      f"m_N = {0.5 * ne_c:.4f}")
check("P6 at m_1 = 0.5 the mean index calls it safe", 0.5 * ne_u < 1,
      f"mean index reports {0.5 * ne_u:.4f}")


# --------------------------------------------- P7  supply-chain concentration

print("\nP7  concentration: max|r_ij - s| = O(1/d) and lambda_max -> 1 + s(N-1)")

def supply_chain_E(N, d, s, rng):
    """E_i = sqrt(s) E_shared + sqrt(1-s) Xi_i, all entries iid Gaussian."""
    shared = rng.standard_normal((d, d))
    xi = rng.standard_normal((N, d, d))
    return np.sqrt(s) * shared[None, :, :] + np.sqrt(1 - s) * xi


N, s = 8, 0.6
ds = np.array([8, 16, 32, 64, 128])
errs = []
for d in ds:
    trials = [np.abs(alignment_matrix(supply_chain_E(N, d, s, rng))
                     - s)[~np.eye(N, dtype=bool)].max() for _ in range(40)]
    errs.append(np.median(trials))
errs = np.array(errs)
slope = np.polyfit(np.log(ds), np.log(errs), 1)[0]
check("P7 off-diagonal error decays as 1/d", abs(slope + 1.0) < 0.15,
      f"log-log slope {slope:.3f}, target -1")

# the limit matrix itself, and the two routes to N_eff agreeing exactly
for N in (5, 20, 50):
    for s in (0.0, 0.25, 0.6, 1.0):
        R_inf = (1 - s) * np.eye(N) + s * np.ones((N, N))
        check(f"P7 limit lambda_max = 1 + s(N-1), N={N} s={s}",
              abs(np.linalg.eigvalsh(R_inf).max() - (1 + s * (N - 1))) < 1e-9)
        check(f"P7 two routes to N_eff agree, N={N} s={s}",
              abs(n_eff(R_inf, 0.8) - (1 + 0.8 * s * (N - 1))) < 1e-9)

# lambda_max convergence at the rate the Weyl step predicts: N * max|Delta_ij|
N, s = 8, 0.6
for d in (16, 64, 256):
    R = alignment_matrix(supply_chain_E(N, d, s, rng))
    R_inf = (1 - s) * np.eye(N) + s * np.ones((N, N))
    lam_err = abs(np.linalg.eigvalsh(R).max() - (1 + s * (N - 1)))
    weyl = np.linalg.norm(R - R_inf, 2)
    check(f"P7 Weyl bound holds at d={d}", lam_err <= weyl + 1e-12,
          f"|d lambda| = {lam_err:.4f} <= ||Delta||_2 = {weyl:.4f}")


# ---------------------------------------- P8  heterogeneous-modulus bounds

print("\nP8  max_i m_i <= rho(J) <= max_i m_i * N_eff")

def hetero_radius(R, m, kappa):
    """rho of J = -M[(1-kappa)I + kappa R] via the symmetric congruence A."""
    Mh = np.diag(np.sqrt(m))
    A = (1 - kappa) * np.diag(m) + kappa * Mh @ R @ Mh
    return np.linalg.eigvalsh(A).max()


slack = []
for N in (3, 7, 15):
    for kappa in (0.0, 0.4, 0.8, 1.0):
        for trial in range(25):
            R = random_R(N, 40, rng)
            m = rng.uniform(0.05, 0.9, size=N)
            rho = hetero_radius(R, m, kappa)
            lo, hi = m.max(), m.max() * n_eff(R, kappa)
            check_ok = lo - 1e-10 <= rho <= hi + 1e-10
            if not check_ok:
                raise AssertionError(f"P8 bound violated: rho={rho} lo={lo} hi={hi}")
            slack.append((rho - lo, hi - rho))
check("P8 two-sided bound holds on 300 random draws", True,
      f"median slack low {np.median([a for a, _ in slack]):.4f}, "
      f"high {np.median([b for _, b in slack]):.4f}")

# the three limits where the bound is exact
for N in (5, 12):
    R = random_R(N, 40, rng)
    m = rng.uniform(0.05, 0.9, size=N)
    check(f"P8 exact at kappa = 0, N={N}",
          abs(hetero_radius(R, m, 0.0) - m.max()) < 1e-10)
    check(f"P8 exact at R = I, N={N}",
          abs(hetero_radius(np.eye(N), m, 0.7) - m.max()) < 1e-10)
    m_eq = np.full(N, 0.15)
    check(f"P8 upper exact at equal moduli, N={N}",
          abs(hetero_radius(R, m_eq, 0.8) - 0.15 * n_eff(R, 0.8)) < 1e-10)

# the tempting mean-modulus formula is provably false
R = np.eye(6)
m = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.9])
check("P8 mean-modulus formula is false at R = I",
      abs(hetero_radius(R, m, 0.7) - m.max()) < 1e-10
      and abs(hetero_radius(R, m, 0.7) - m.mean()) > 0.1,
      f"rho = {hetero_radius(R, m, 0.7):.4f}, max = {m.max():.4f}, "
      f"mean = {m.mean():.4f}")


print(f"\n{len(PASSED)} checks passed.")
