"""Closed forms for the herd-immunity paper.

One module holding every closed form the paper states, so that each experiment
checks itself against a single source rather than against a reimplementation.

Scope. Theorems 1, 2 and 3 are complete and proved in ../../math/derivations/,
and Theorem 4's welfare page in ../../math/04-theorem4-wedge.md. All four are
certified, so every closed form the paper states appears here.

Conventions.
  - numpy only, CPU only, deterministic. Every function is pure.
  - `kappa` is the spillover in [0, 1], `s` the shared-model fraction in [0, 1].
  - `gamma_ratio` is gamma/gamma_PO in (0, 1]: 1 is no correction, 0 the
    strong-correction limit.
  - Alignment matrices are Gram matrices of vectorized response Jacobians:
    symmetric, positive semidefinite, unit diagonal.

Reading order, if this is the first file you open: `n_eff` is the paper's central
quantity and everything else is stated in terms of `m_systemic`.
"""
import numpy as np

__all__ = [
    "alignment_matrix", "n_eff", "m_systemic", "supply_chain_R",
    "n_eff_supply_chain", "response_jacobians", "clustered_R", "simplex_R",
    "monoculture_R", "mean_alignment", "n_eff_mean_index",
    "joint_jacobian", "hetero_modulus_bounds",
    "mu_N", "k_max", "critical_crowding", "is_stable_lazy",
    "n_c", "rho_star", "mixed_market_jacobian", "mixed_market_radius",
    "is_stable_mixed", "min_corrected", "rho_star_imperfect",
    "critical_efficacy", "substitution_frontier",
    "stationary_variance", "dV_dm", "marginal_crowding_share",
    "pigouvian_wedge", "provenance_wedge",
]

_PSD_TOL = 1e-9


# ===========================================================================
# Theorem 1: alignment and the effective number of independent learners
# ===========================================================================

def alignment_matrix(E, check=True):
    """R from response Jacobians E of shape (N, d, d), by vec inner products.

    R[i, j] = <vec E_i, vec E_j> / (||E_i||_F ||E_j||_F).
    """
    E = np.asarray(E, dtype=float)
    if E.ndim != 3:
        raise ValueError(f"E must have shape (N, d, d), got {E.shape}")
    V = E.reshape(E.shape[0], -1)
    norms = np.linalg.norm(V, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("a response Jacobian has zero norm, so its direction "
                         "is undefined")
    R = (V / norms) @ (V / norms).T
    R = (R + R.T) / 2                      # kill asymmetry from rounding
    if check:
        if not np.allclose(np.diag(R), 1.0, atol=_PSD_TOL):
            raise ValueError("alignment matrix does not have unit diagonal")
        if np.linalg.eigvalsh(R).min() < -_PSD_TOL:
            raise ValueError("alignment matrix is not positive semidefinite")
    return R


def n_eff(R, kappa):
    """Effective crowding, 1 + kappa (lambda_max(R) - 1).

    Bounded below by 1 for any genuine alignment matrix, so interaction never
    stabilizes a market below what its members achieve alone. See
    ../../math/derivations/01-alignment-spectrum.md, Corollary 1.2.
    """
    _check_unit(kappa, "kappa")
    return 1.0 + kappa * (float(np.linalg.eigvalsh(np.asarray(R)).max()) - 1.0)


def m_systemic(m_1, R, kappa):
    """The systemic modulus m_N = N_eff * m_1, the feedback reproduction number."""
    return float(m_1) * n_eff(R, kappa)


def joint_jacobian(R, m_1, kappa):
    """J = -m_1 [(1-kappa) I + kappa R], the joint retraining Jacobian."""
    R = np.asarray(R, dtype=float)
    N = R.shape[0]
    return -float(m_1) * ((1 - kappa) * np.eye(N) + kappa * R)


def supply_chain_R(N, s):
    """(1-s) I + s 11', the concentration limit of the response decomposition."""
    _check_unit(s, "s")
    return (1 - s) * np.eye(N) + s * np.ones((N, N))


def n_eff_supply_chain(N, s, kappa):
    """1 + kappa s (N-1). Must equal n_eff(supply_chain_R(N, s), kappa)."""
    _check_unit(s, "s")
    _check_unit(kappa, "kappa")
    return 1.0 + kappa * s * (N - 1)


def monoculture_R(N):
    """All firms perturbing the environment identically. lambda_max = N."""
    return np.ones((N, N))


def simplex_R(N):
    """The mean-minimizing configuration, r_ij = -1/(N-1). lambda_max = N/(N-1).

    Kept because it is the sharper counterexample to mean-based diversity
    indices: it minimizes mean alignment yet is spectrally worse than
    orthogonality, so the mean does not order configurations correctly.
    """
    if N < 2:
        raise ValueError("the simplex configuration needs N >= 2")
    return (N / (N - 1)) * np.eye(N) - (1.0 / (N - 1)) * np.ones((N, N))


def clustered_R(N, cluster_sizes):
    """Block-diagonal all-ones blocks: the vendor-with-a-plurality topology.

    Firms not named in `cluster_sizes` are mutually orthogonal.
    """
    if sum(cluster_sizes) > N:
        raise ValueError("cluster sizes exceed the number of firms")
    R = np.eye(N)
    start = 0
    for size in cluster_sizes:
        R[start:start + size, start:start + size] = 1.0
        start += size
    return R


def response_jacobians(N, d, s, rng):
    """Draw E_i = sqrt(s) E_shared + sqrt(1-s) Xi_i with Xi_i independent.

    The realized alignment concentrates at s with fluctuation O(1/d). For an
    alignment matrix hit exactly rather than in distribution, use the
    environment builder in ../environment/.
    """
    _check_unit(s, "s")
    shared = rng.standard_normal((d, d))
    xi = rng.standard_normal((N, d, d))
    return np.sqrt(s) * shared[None, :, :] + np.sqrt(1 - s) * xi


def mean_alignment(R):
    """Off-diagonal mean of R.

    THIS IS A FOIL, NOT A DIVERSITY INDEX. It exists so the paper can show it is
    the wrong statistic, and no stability function in this module calls it. It is
    a lower bound on lambda_max, never an approximation to it, so every error it
    makes is in the direction that lets an unstable market pass. See
    ../../math/derivations/01-alignment-spectrum.md, Proposition 3.
    """
    R = np.asarray(R, dtype=float)
    N = R.shape[0]
    if N < 2:
        return 0.0
    return float((R.sum() - np.trace(R)) / (N * (N - 1)))


def n_eff_mean_index(R, kappa):
    """What a mean-similarity diversity index would report. Also a foil.

    Always less than or equal to n_eff(R, kappa), with equality only when R has
    constant row sums.
    """
    N = np.asarray(R).shape[0]
    return 1.0 + kappa * (N - 1) * mean_alignment(R)


def hetero_modulus_bounds(R, m, kappa):
    """Two-sided bound on rho(J) with heterogeneous moduli, and the exact value.

    Returns (lower, exact, upper) with lower = max_i m_i and
    upper = max_i m_i * n_eff. The tempting mean-modulus formula is false: at
    R = I the firms decouple and rho = max_i m_i, not the mean.
    """
    R = np.asarray(R, dtype=float)
    m = np.asarray(m, dtype=float)
    if np.any(m <= 0):
        raise ValueError("moduli must be positive for the congruence to exist")
    Mh = np.diag(np.sqrt(m))
    A = (1 - kappa) * np.diag(m) + kappa * Mh @ R @ Mh
    exact = float(np.linalg.eigvalsh(A).max())
    return float(m.max()), exact, float(m.max()) * n_eff(R, kappa)


# ===========================================================================
# Theorem 2: the crowding-cadence frontier
# ===========================================================================

def mu_N(m_N, c, K):
    """Outer-map slope of the binding mode under K-step retraining."""
    _check_contraction(c)
    return -m_N + c ** K * (1 + m_N)


def k_max(m_N, c):
    """Largest real cadence keeping an m_N > 1 market stable. Infinite if m_N <= 1."""
    _check_contraction(c)
    if m_N <= 1:
        return np.inf
    return np.log((m_N - 1) / (m_N + 1)) / np.log(c)


def critical_crowding(c):
    """(1+c)/(1-c): the m_N past which no cadence helps.

    This is the frontier evaluated at K = 1, not a separate result, since K is a
    positive integer and the constraint m_N < (1+c^K)/(1-c^K) loosens as K falls.
    """
    _check_contraction(c)
    return (1 + c) / (1 - c)


def is_stable_lazy(m_N, c, K):
    """Stability of the joint loop at integer cadence K.

    Agrees with K < k_max(m_N, c) on every integer K. The upper side of
    |mu_N| < 1 never binds, because every mode's slope is at most c^K < 1.
    """
    if K < 1:
        raise ValueError("cadence K must be a positive integer")
    return bool(abs(mu_N(m_N, c, K)) < 1)


# ===========================================================================
# Theorem 3: the mixed market and herd immunity
# ===========================================================================

def n_c(m_1, kappa, s):
    """Critical count of blind firms. The market's limit is stable iff N_b < n_c."""
    if kappa * s == 0:
        return np.inf
    return 1.0 + (1.0 / m_1 - 1.0) / (kappa * s)


def rho_star(N, m_1, kappa, s):
    """Herd-immunity threshold as a corrected fraction, clamped at zero.

    CAUTION. This is the policy object, not the exact criterion. `rho > rho_star`
    mispredicts the all-blind market that is stable without any correction,
    because the clamp combined with a strict inequality excludes N_b = N. Use
    `is_stable_mixed` for a verdict. See
    ../../math/derivations/04-mixed-market-secular.md, Proposition 12.
    """
    return float(max(0.0, 1.0 - n_c(m_1, kappa, s) / N))


def mixed_market_jacobian(N, n_blind, m_1, kappa, s, gamma_ratio):
    """Two-block joint Jacobian. Blind firms first, then corrected ones."""
    _check_blocks(N, n_blind)
    _check_unit(gamma_ratio, "gamma_ratio")
    m = np.full(N, float(m_1))
    m[n_blind:] = gamma_ratio * m_1
    R = supply_chain_R(N, s)
    return -np.diag(m) @ ((1 - kappa) * np.eye(N) + kappa * R)


def mixed_market_radius(N, n_blind, m_1, kappa, s, gamma_ratio):
    """Exact spectral radius, from the two-block secular quadratic.

    An empty block needs the single-block form: the quadratic still carries that
    block's factor and otherwise leaves a phantom root behind, which at small
    gamma_ratio exceeds the true radius.
    """
    _check_blocks(N, n_blind)
    _check_unit(gamma_ratio, "gamma_ratio")
    ks = kappa * s
    ne = n_eff_supply_chain(N, s, kappa)
    if n_blind == N:
        return float(m_1 * ne)
    if n_blind == 0:
        return float(gamma_ratio * m_1 * ne)
    a = (1 - ks) * m_1
    b = (1 - ks) * gamma_ratio * m_1
    P = a + b + ks * m_1 * (n_blind + gamma_ratio * (N - n_blind))
    Q = gamma_ratio * m_1 ** 2 * (1 - ks) * ne
    return float((P + np.sqrt(max(P ** 2 - 4 * Q, 0.0))) / 2)


def is_stable_mixed(N, n_blind, m_1, kappa, s, gamma_ratio=0.0):
    """Exact stability verdict for the mixed market.

    Defaults to the strong-correction limit, which is OPTIMISTIC: it under-states
    the radius, so pass the realized gamma_ratio for a verdict that can be
    trusted.
    """
    if gamma_ratio == 0.0:
        return bool(n_blind < n_c(m_1, kappa, s))
    return bool(mixed_market_radius(N, n_blind, m_1, kappa, s, gamma_ratio) < 1)


def min_corrected(N, m_1, kappa, s):
    """Smallest whole number of corrected firms that stabilizes the limit.

    N - ceil(n_c) + 1, clamped to [0, N]. Not ceil(rho_star * N), which is off by
    one when n_c is exactly an integer.
    """
    nc = n_c(m_1, kappa, s)
    if not np.isfinite(nc):
        return 0
    return int(min(N, max(0, N - int(np.ceil(nc)) + 1)))


def rho_star_imperfect(m_N, gamma_ratio):
    """(1 - 1/m_N) / (1 - gamma_ratio): the imperfect-correction threshold.

    Exact at kappa = s = 1, where it is the epidemiological coverage requirement
    for an imperfect vaccine with efficacy e = 1 - gamma_ratio. Returns a value
    above 1 when no corrected fraction suffices; see `critical_efficacy`.
    """
    _check_unit(gamma_ratio, "gamma_ratio")
    if m_N <= 1:
        return 0.0
    if gamma_ratio >= 1:
        return np.inf
    return float((1 - 1 / m_N) / (1 - gamma_ratio))


def critical_efficacy(m_N):
    """Smallest gamma_PO/gamma at which correction is a usable lever at all.

    Below this ratio no corrected fraction stabilizes the market. The structural
    parallel of `critical_crowding` for the correction lever.
    """
    return float(m_N) if m_N > 1 else 1.0


def substitution_frontier(N, m_1, kappa, s_grid):
    """The (rho, s) iso-stability curve. Ground truth for the headline figure."""
    return np.array([rho_star(N, m_1, kappa, float(s)) for s in np.asarray(s_grid)])


# ===========================================================================
# Theorem 4: the welfare object, the marginal crowding share, and the wedge
# ===========================================================================
# The welfare page in ../../math/04-theorem4-wedge.md landed on 18 Aug 2026 and
# panel 6 landed on 19 Aug 2026, so `pigouvian_wedge` joins the module here. It
# was held out until both existed, under the standing rule that nothing reaches
# the paper ahead of its derivation.

def stationary_variance(m_N, sigma):
    """sigma^2 / (1 - m_N^2), the common mode's stationary variance."""
    if m_N >= 1:
        return np.inf
    return float(sigma ** 2 / (1 - m_N ** 2))


def dV_dm(m_N, sigma):
    """Derivative of the stationary variance in m_N."""
    if m_N >= 1:
        return np.inf
    return float(2 * sigma ** 2 * m_N / (1 - m_N ** 2) ** 2)


def marginal_crowding_share(R, kappa):
    """Lemma 11: d m_N/d m_i = N_eff * v_i^2 at the symmetric point.

    Returns the vector of shares, which sums to `N_eff` rather than to 1. That
    is the whole content of the lemma: the market's total sensitivity to a
    uniform increase in aggressiveness is amplified by the effective learner
    count, and the naive `1/N` guess is wrong by exactly that factor.
    """
    R = np.asarray(R, dtype=float)
    N = R.shape[0]
    B = (1 - kappa) * np.eye(N) + kappa * R
    w, V = np.linalg.eigh(B)
    v = V[:, int(np.argmax(w))]
    return float(np.max(w)) * (v ** 2)


def pigouvian_wedge(m_N, N_eff, N, mu_prime, w, chi, sigma=1.0):
    """Theorem 4: t* = (W - w) V'(m_N) (N_eff/N) mu'(a), with W = chi*N*w.

    The per-unit fee on aggressiveness that makes the private first-order
    condition coincide with the social one. `chi > 1` is the client-exposure
    multiplier of (W4); `chi = 1` switches client exposure off and leaves the
    firm-to-firm channel alone, where the ignored fraction is (N-1)/N.

    Infinite at or beyond the stability boundary, since V' is.
    """
    if not (chi >= 1.0):
        raise ValueError(f"chi must be at least 1 under (W4), got {chi}")
    if m_N >= 1:
        return np.inf
    W_planner = chi * N * w
    return float((W_planner - w) * dV_dm(m_N, sigma) * (N_eff / N) * mu_prime)


def provenance_wedge(m_N, m_1, N, kappa, w, chi, sigma=1.0):
    """Proposition 12: the same wedge with s as the choice variable.

    t*_s = (W - w) V'(m_N) * m_1 * kappa * (N - 1). The provenance channel is
    linear in N and does not decay, unlike the aggressiveness channel whose
    N_eff/N factor tends to kappa from above.
    """
    if not (chi >= 1.0):
        raise ValueError(f"chi must be at least 1 under (W4), got {chi}")
    if m_N >= 1:
        return np.inf
    W_planner = chi * N * w
    return float((W_planner - w) * dV_dm(m_N, sigma) * m_1 * kappa * (N - 1))


# ===========================================================================
# guards
# ===========================================================================

def _check_unit(x, name):
    if not (0.0 <= x <= 1.0):
        raise ValueError(f"{name} must lie in [0, 1], got {x}")


def _check_contraction(c):
    if not (0.0 < c < 1.0):
        raise ValueError(f"inner contraction c must lie in (0, 1), got {c}")


def _check_blocks(N, n_blind):
    if not (0 <= n_blind <= N):
        raise ValueError(f"n_blind must lie in [0, {N}], got {n_blind}")
