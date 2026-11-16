"""Certificates for the Theorem 1 anchors, especially the simplex case.

Source of the statements: ../../math/derivations/01-alignment-spectrum.md and
the claims ledger's 4.2, 4.3, 4.4, 4.8 and 4.9.

Assertion-based, following verify_theorem1_proof.py. Every check raises on
failure and the script exits nonzero. The printed tables are kept, because the
numbers in sections (D) and (F) are quoted in the math notes and a reader
checking a quote wants to see them, but they are no longer the point: the point
is that a broken derivation now fails the run instead of producing a report
nobody reads to the end.

The claim under test in section (C) is the one the plan of record got wrong. The
plan said maximal diversity gives spectral radius `m_1(1-kappa)`. That value is
in the spectrum, but it is not the radius: the radius is `m_1(1 + kappa/(N-1))`,
which is what ledger claim 4.4 now states. Section (C) asserts both halves, the
true one and the false one, so the correction cannot silently regress.

Checks, by section:

  A  analytic simplex     diagonal, off-diagonal, rank deficiency, lambda_max
  B  constructive simplex Gram of actual unit vectors equals the analytic R
  C  the corrected claim  m_1(1-kappa) is in the spectrum and is NOT the radius
  D  the three anchors    monoculture, orthogonal, simplex, radius = m_1 N_eff
  E  ordering failure     lower mean alignment, higher lambda_max
  F  clustered gap        the 1.757 understatement factor and the split verdict
"""
import numpy as np

np.set_printoptions(precision=6, suppress=True)

TOL = 1e-12
PASSED = []


def check(name, condition, detail=""):
    """Record a check and fail loudly if it did not hold."""
    if not condition:
        raise AssertionError(f"FAILED {name}: {detail}")
    PASSED.append(name)
    print(f"  pass  {name}" + (f"   [{detail}]" if detail else ""))


def J_of(R, m1, kappa):
    """Joint retraining Jacobian under the generalized law J = -m1[(1-k)I + kR]."""
    N = R.shape[0]
    return -m1 * ((1 - kappa) * np.eye(N) + kappa * R)


def radius(M):
    return max(abs(np.linalg.eigvals(M)))


def simplex_R(N):
    """N unit vectors with pairwise alignment -1/(N-1): the mean-minimizing set."""
    return (N / (N - 1)) * np.eye(N) - (1.0 / (N - 1)) * np.ones((N, N))


def simplex_vectors(N, d, seed=0):
    """Construct N actual unit vectors in R^d summing to zero (a regular simplex).

    Take the N-1 dim orthogonal complement of the all-ones vector in R^N,
    embed it in R^d via a random orthonormal map. Gram matrix is then exactly
    the simplex R, measured rather than assumed.
    """
    rng = np.random.default_rng(seed)
    # Columns of Q span 1-perp in R^N
    A = np.eye(N) - np.ones((N, N)) / N
    Q, _ = np.linalg.qr(A[:, : N - 1])          # d0 = N-1 orthonormal cols
    # rows of Q are the N points, already summing to zero
    V = Q                                       # (N, N-1)
    # embed into R^d with a random orthonormal basis
    G = rng.standard_normal((d, N - 1))
    B, _ = np.linalg.qr(G)                      # (d, N-1) orthonormal cols
    X = V @ B.T                                 # (N, d)
    X = X / np.linalg.norm(X, axis=1, keepdims=True)
    return X


def gram(X):
    Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
    return Xn @ Xn.T


print("=" * 72)
print("(A) ANALYTIC: simplex R built by hand")
print("=" * 72)
for N in (3, 5, 10, 50):
    R = simplex_R(N)
    ev = np.sort(np.linalg.eigvalsh(R))
    print(f"N={N:>3}  diag={R[0,0]:.6f}  offdiag={R[0,1]:+.6f}  "
          f"lam_min={ev[0]:+.6e}  lam_max={ev[-1]:.6f}  N/(N-1)={N/(N-1):.6f}")
    check(f"A simplex has unit diagonal at N={N}", abs(R[0, 0] - 1.0) < TOL,
          "N/(N-1) - 1/(N-1) = 1, so it is a genuine alignment matrix")
    check(f"A simplex off-diagonal is -1/(N-1) at N={N}",
          abs(R[0, 1] + 1.0 / (N - 1)) < TOL)
    check(f"A simplex is rank deficient at N={N}", abs(ev[0]) < 1e-10,
          f"lam_min = {ev[0]:.2e}, the all-ones direction")
    check(f"A simplex lambda_max is N/(N-1) at N={N}",
          abs(ev[-1] - N / (N - 1)) < 1e-10)
    check(f"A simplex is positive semidefinite at N={N}", ev[0] > -1e-10)

print()
print("=" * 72)
print("(B) CONSTRUCTIVE: alignment matrix measured from actual vec(E_i)")
print("=" * 72)
for N, d in ((3, 16), (5, 25), (10, 64)):
    X = simplex_vectors(N, d)
    R = gram(X)
    R_hand = simplex_R(N)
    ev = np.sort(np.linalg.eigvalsh(R))
    err = np.abs(R - R_hand).max()
    zero_sum = np.linalg.norm(X.sum(axis=0))
    print(f"N={N:>3} d={d:>3}  max|R_measured - R_analytic| = "
          f"{err:.3e}   lam_max={ev[-1]:.6f}  "
          f"sum of vectors = {zero_sum:.3e}")
    check(f"B measured Gram equals the analytic simplex at N={N}, d={d}",
          err < 1e-10, f"max error {err:.2e}")
    check(f"B simplex vectors sum to zero at N={N}, d={d}",
          zero_sum < 1e-10, f"norm {zero_sum:.2e}")
    check(f"B measured lambda_max is N/(N-1) at N={N}",
          abs(ev[-1] - N / (N - 1)) < 1e-10)

print()
print("=" * 72)
print("(C) THE CLAIM UNDER TEST: is the spectral radius m1*(1-kappa)?")
print("=" * 72)
m1, kappa = 0.15, 0.8
print(f"m1={m1}  kappa={kappa}   plan claims radius = m1(1-kappa) = "
      f"{m1*(1-kappa):.6f}\n")
print(f"{'N':>4} {'radius(J)':>12} {'m1(1+k/(N-1))':>15} {'m1(1-k)':>10} "
      f"{'in spectrum?':>13} {'is radius?':>11}")
c_rows = []
for N in (3, 5, 10, 30, 50):
    R = simplex_R(N)
    J = J_of(R, m1, kappa)
    spec = np.linalg.eigvals(J)
    rad = max(abs(spec))
    pred_radius = m1 * (1 + kappa / (N - 1))
    claimed = m1 * (1 - kappa)
    in_spec = np.min(np.abs(np.abs(spec) - claimed)) < 1e-12
    is_rad = abs(rad - claimed) < 1e-12
    c_rows.append((N, rad, pred_radius, in_spec, is_rad))
    print(f"{N:>4} {rad:>12.6f} {pred_radius:>15.6f} {claimed:>10.6f} "
          f"{str(in_spec):>13} {str(is_rad):>11}")
print()
for N, rad, pred_radius, in_spec, is_rad in c_rows:
    check(f"C m1(1-kappa) lies in the spectrum at N={N}", in_spec)
    check(f"C m1(1-kappa) is NOT the radius at N={N}", not is_rad,
          "the plan of record's claim, corrected in ledger 4.4")
    check(f"C radius is m1(1 + kappa/(N-1)) at N={N}",
          abs(rad - pred_radius) < 1e-12, f"radius {rad:.6f}")
check("C the radius decreases toward m1 as N grows",
      all(c_rows[i][1] > c_rows[i + 1][1] for i in range(len(c_rows) - 1))
      and c_rows[-1][1] > m1,
      f"{c_rows[0][1]:.6f} down to {c_rows[-1][1]:.6f}, floor m1 = {m1}")

print()
print("=" * 72)
print("(D) ALL THREE ANCHORS, N_eff = 1 + kappa(lam_max(R) - 1)")
print("=" * 72)
N = 10
anchors = {
    "monoculture  R=11'": np.ones((N, N)),
    "orthogonal   R=I  ": np.eye(N),
    "simplex           ": simplex_R(N),
}
d_rows = {}
for name, R in anchors.items():
    lam = max(np.linalg.eigvalsh(R))
    n_eff = 1 + kappa * (lam - 1)
    rad = radius(J_of(R, m1, kappa))
    match = abs(rad - m1 * n_eff) < 1e-12
    d_rows[name.strip()] = (lam, n_eff, rad, match)
    print(f"{name}  lam_max={lam:>8.6f}  N_eff={n_eff:>8.6f}  "
          f"m_N={m1*n_eff:>8.6f}  radius(J)={rad:>8.6f}  "
          f"match={match}")
print(f"\nbase-law check: monoculture N_eff should be 1+kappa(N-1) = "
      f"{1 + kappa*(N-1):.6f}\n")
for name, (lam, n_eff, rad, match) in d_rows.items():
    check(f"D radius equals m1 * N_eff for the {name.split()[0]} anchor", match,
          f"radius {rad:.6f}")
check("D monoculture recovers the base law N_eff = 1 + kappa(N-1)",
      abs(d_rows["monoculture  R=11'"][1] - (1 + kappa * (N - 1))) < TOL,
      "ledger 4.2")
check("D orthogonal responses give N_eff = 1",
      abs(d_rows["orthogonal   R=I"][1] - 1.0) < TOL, "ledger 4.3")
check("D N_eff >= 1 at every anchor",
      all(v[1] >= 1.0 - TOL for v in d_rows.values()), "ledger 4.12")

print()
print("=" * 72)
print("(E) ORDERING FAILURE: does minimizing MEAN alignment minimize lam_max?")
print("=" * 72)


def meanoff(R):
    n = R.shape[0]
    return (R.sum() - np.trace(R)) / (n * (n - 1))


for N in (5, 10, 30):
    Rs, Ri = simplex_R(N), np.eye(N)
    ls, li = max(np.linalg.eigvalsh(Rs)), max(np.linalg.eigvalsh(Ri))
    inverted = meanoff(Rs) < meanoff(Ri) and ls > li
    print(f"N={N:>3}  simplex: mean={meanoff(Rs):+.6f} lam_max={ls:.6f}   "
          f"orthogonal: mean={meanoff(Ri):+.6f} lam_max={li:.6f}   "
          f"-> lower mean, higher lam_max: {inverted}")
    check(f"E mean alignment orders the wrong way at N={N}", inverted,
          f"ledger 4.9; mean {meanoff(Rs):+.4f} < {meanoff(Ri):+.4f} but "
          f"lam_max {ls:.4f} > {li:.4f}")

print()
print("=" * 72)
print("(F) CLUSTERED COUNTEREXAMPLE numbers quoted in the math note")
print("=" * 72)
N = 10
R_clust = np.zeros((N, N))
R_clust[:3, :3] = 1.0
R_clust[3:, 3:] = np.eye(7)
lam_c = max(np.linalg.eigvalsh(R_clust))
mean_c = (R_clust.sum() - np.trace(R_clust)) / (N * (N - 1))
R_unif = (1 - mean_c) * np.eye(N) + mean_c * np.ones((N, N))
lam_u = max(np.linalg.eigvalsh(R_unif))
neff_c, neff_u = 1 + kappa * (lam_c - 1), 1 + kappa * (lam_u - 1)
factor = neff_c / neff_u
print(f"clustered:  lam_max={lam_c:.6f}  mean_offdiag={mean_c:.6f}  "
      f"N_eff={neff_c:.4f}  destabilizes at m1={1/neff_c:.4f}")
print(f"uniform:    lam_max={lam_u:.6f}  mean_offdiag={mean_c:.6f}  "
      f"N_eff={neff_u:.4f}  destabilizes at m1={1/neff_u:.4f}")
print(f"understatement factor in N_eff: {factor:.4f}")
print(f"at m1=0.5:  clustered m_N={0.5*neff_c:.4f} (unstable={0.5*neff_c>1}), "
      f"uniform m_N={0.5*neff_u:.4f} (unstable={0.5*neff_u>1})\n")
check("F the two configurations share an off-diagonal mean",
      abs(meanoff(R_clust) - meanoff(R_unif)) < 1e-12,
      f"mean {mean_c:.6f}; this is what makes the mean index blind here")
check("F clustered N_eff is 2.60 as the math note quotes",
      abs(neff_c - 2.60) < 5e-3, f"{neff_c:.4f}")
check("F uniform N_eff is 1.48 as the math note quotes",
      abs(neff_u - 1.48) < 5e-3, f"{neff_u:.4f}")
check("F the understatement factor is 1.757", abs(factor - 1.757) < 1e-3,
      f"{factor:.4f}, ledger 4.8")
check("F the mean index under-states and never over-states", factor >= 1.0 - TOL,
      "ledger 4.13, the signed error")
check("F the verdicts split at m1 = 0.5",
      0.5 * neff_c > 1.0 and 0.5 * neff_u < 1.0,
      f"clustered m_N {0.5*neff_c:.4f} unstable, uniform {0.5*neff_u:.4f} stable")

print(f"\n{len(PASSED)} checks passed.")
