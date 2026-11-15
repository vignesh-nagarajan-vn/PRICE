"""Heterogeneous-response market environment.

The one piece of new infrastructure the paper needs. Experiments 2, 4 and 5 all
run against it, including the substitution frontier, which is never cut.

WHAT THIS IS. A linearized reference environment. Firms are placed at chosen
response *directions*, the pool distortion they share is formed from their
actual response Jacobians, and each firm's retraining is derived from what it
senses through its own channel. The joint Jacobian is therefore *constructed*
rather than asserted, which is what makes it a test of the closed form instead
of a restatement of it.

WHAT THIS IS NOT. The base project's order-flow simulator. There is no informed
flow, no spread, no inventory. This environment realizes the response geometry
of the model and nothing else. Panels that need microstructure run in the
simulator; this is what the simulator's heterogeneous extension is checked
against, and it is what the acceptance test in
../certificates/verify_hetero_env.py exercises.

The mechanism is derived in ../../math/derivations/01-alignment-spectrum.md,
Section 1: firm i feels its own contribution to the pool in full and each
competitor's with weight kappa, projected on its own unit response direction.
"""
import numpy as np


# ===========================================================================
# placing firms at a target alignment
# ===========================================================================

def response_jacobians_for_R(R, d, rng, eps=1.0, tol=1e-9):
    """Response Jacobians whose measured alignment matrix is exactly R.

    R must be a valid alignment matrix: symmetric, positive semidefinite, unit
    diagonal. Returns E of shape (N, d, d) with ||E_i||_F = eps.

    Method. Factor R = L L' by eigendecomposition, which works for the singular
    cases the paper cares about (the monoculture R = 11' has rank one, so
    Cholesky is not available). Rows of L are unit vectors in R^N with the right
    Gram matrix. Embed them in R^(d*d) through a random orthonormal map, which
    preserves every inner product, then reshape.
    """
    R = np.asarray(R, dtype=float)
    N = R.shape[0]
    if R.shape != (N, N):
        raise ValueError(f"R must be square, got {R.shape}")
    if not np.allclose(R, R.T, atol=tol):
        raise ValueError("R must be symmetric")
    if not np.allclose(np.diag(R), 1.0, atol=tol):
        raise ValueError("R must have unit diagonal")
    lam, Q = np.linalg.eigh(R)
    if lam.min() < -tol:
        raise ValueError(f"R must be positive semidefinite, "
                         f"smallest eigenvalue {lam.min():.3e}")
    if d * d < N:
        raise ValueError(f"need d*d >= N to realize {N} directions in R^{d*d}; "
                         f"d = {d} gives only {d*d}")

    L = Q @ np.diag(np.sqrt(np.clip(lam, 0.0, None)))        # (N, N), Gram = R
    basis = np.linalg.qr(rng.standard_normal((d * d, N)))[0]  # (d*d, N)
    V = L @ basis.T                                           # (N, d*d)
    return eps * V.reshape(N, d, d)


def measured_alignment(E):
    """The alignment matrix read back off the realized Jacobians."""
    V = np.asarray(E, dtype=float).reshape(np.shape(E)[0], -1)
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    return V @ V.T


# ===========================================================================
# the market
# ===========================================================================

class HeterogeneousMarket:
    """N firms with chosen response directions sharing one pool.

    Parameters
    ----------
    E : (N, d, d) array
        Response Jacobians. Build them with `response_jacobians_for_R`.
    kappa : float in [0, 1]
        Spillover: how much of a competitor's pool distortion a firm feels.
    m_1 : float
        Single-firm modulus. Firms are homogeneous in modulus unless `moduli`
        is given.
    moduli : (N,) array, optional
        Per-firm moduli, for mixed markets. A corrected firm carries
        gamma_ratio * m_1. Overrides `m_1` when present.
    """

    def __init__(self, E, kappa, m_1, moduli=None):
        self.E = np.asarray(E, dtype=float)
        if self.E.ndim != 3:
            raise ValueError(f"E must have shape (N, d, d), got {self.E.shape}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must lie in [0, 1], got {kappa}")
        self.N, self.d = self.E.shape[0], self.E.shape[1]
        self.kappa = float(kappa)
        self.moduli = (np.full(self.N, float(m_1)) if moduli is None
                       else np.asarray(moduli, dtype=float))
        if self.moduli.shape != (self.N,):
            raise ValueError("moduli must have one entry per firm")
        if np.any(self.moduli < 0):
            raise ValueError("moduli must be nonnegative")

        V = self.E.reshape(self.N, -1)
        self._norms = np.linalg.norm(V, axis=1)
        if np.any(self._norms == 0):
            raise ValueError("a response Jacobian has zero norm")
        self._V = V
        self._U = V / self._norms[:, None]        # unit response directions

    # ---------------------------------------------------------------- geometry

    @property
    def alignment(self):
        """R, measured from the realized Jacobians rather than assumed."""
        return self._U @ self._U.T

    @property
    def n_eff(self):
        return 1.0 + self.kappa * (np.linalg.eigvalsh(self.alignment).max() - 1.0)

    @property
    def m_systemic(self):
        """m_N. Defined for homogeneous moduli; use `radius` when they differ."""
        return float(self.moduli[0] * self.n_eff)

    # ---------------------------------------------------------------- dynamics

    def felt_distortion(self, x):
        """What each firm senses: the pool distortion along its own channel.

        The pool carries Z = sum_j x_j E_j. Firm i feels its own contribution in
        full and each competitor's with weight kappa, projected on E_i / ||E_i||.
        """
        x = np.asarray(x, dtype=float)
        pool = self._V.T @ x                                   # sum_j x_j vec E_j
        own = self._V * x[:, None]                             # firm i's own term
        felt_all = self._U @ pool                              # full-weight sense
        felt_own = np.einsum("ij,ij->i", self._U, own)
        return self.kappa * felt_all + (1 - self.kappa) * felt_own

    def jacobian(self):
        """The joint retraining Jacobian, built from the response geometry.

        Constructed by differentiating the retraining map, not by evaluating the
        closed form. `predicted_jacobian` is the closed form, and the acceptance
        test compares the two.
        """
        return np.column_stack([self._retrain(e) for e in np.eye(self.N)])

    def predicted_jacobian(self):
        """The closed form -M[(1-kappa) I + kappa R] from Theorem 1."""
        R = self.alignment
        B = (1 - self.kappa) * np.eye(self.N) + self.kappa * R
        return -np.diag(self.moduli) @ B

    def _retrain(self, x):
        """Full retraining: each firm jumps to its frozen best response."""
        scale = self.moduli / self._norms
        return -scale * self.felt_distortion(x)

    def step(self, x, K=None, c=None):
        """One synchronous deployment round.

        With `K` and `c` given, every firm takes K inner gradient steps toward
        its frozen best response, contracting the gap by c per step. With
        neither, firms retrain to convergence.
        """
        x = np.asarray(x, dtype=float)
        target = self._retrain(x)
        if K is None:
            return target
        if c is None:
            raise ValueError("pass the inner contraction c along with K")
        if K < 1:
            raise ValueError("cadence K must be a positive integer")
        if not (0.0 < c < 1.0):
            raise ValueError(f"c must lie in (0, 1), got {c}")
        return target + c ** K * (x - target)

    def simulate(self, x0, steps=400, K=None, c=None, blow_up=1e12):
        """Iterate the joint map. Returns the trajectory of norms."""
        x = np.asarray(x0, dtype=float).copy()
        norms = [float(np.linalg.norm(x))]
        for _ in range(steps):
            x = self.step(x, K=K, c=c)
            n = float(np.linalg.norm(x))
            norms.append(n)
            if n > blow_up or n == 0.0:
                break
        return np.array(norms)

    def is_stable(self, K=None, c=None):
        """Stability verdict from the spectral radius of the realized map."""
        if K is None:
            return bool(np.abs(np.linalg.eigvals(self.jacobian())).max() < 1)
        J = self.jacobian()
        M = c ** K * np.eye(self.N) + (1 - c ** K) * J
        return bool(np.abs(np.linalg.eigvals(M)).max() < 1)


# ===========================================================================
# builders for the topologies the experiments sweep
# ===========================================================================

def homogeneous_market(N, d, kappa, m_1, rng):
    """The monoculture, R = 11'. Every firm perturbs the pool identically.

    This is the reduction target: the environment must agree with the base
    project's homogeneous multi-dealer market here, and the acceptance test
    checks exactly that.
    """
    E = response_jacobians_for_R(np.ones((N, N)), d, rng)
    return HeterogeneousMarket(E, kappa, m_1)


def supply_chain_market(N, d, kappa, m_1, s, rng, exact=True):
    """Shared-model fraction s.

    With `exact`, firms are placed at the limit alignment (1-s)I + s 11'. With
    `exact=False`, Jacobians are drawn from the decomposition
    E_i = sqrt(s) E_shared + sqrt(1-s) Xi_i, so the realized alignment
    concentrates at s with O(1/d) fluctuation instead of hitting it.
    """
    if exact:
        R = (1 - s) * np.eye(N) + s * np.ones((N, N))
        E = response_jacobians_for_R(R, d, rng)
    else:
        shared = rng.standard_normal((d, d))
        xi = rng.standard_normal((N, d, d))
        E = np.sqrt(s) * shared[None, :, :] + np.sqrt(1 - s) * xi
    return HeterogeneousMarket(E, kappa, m_1)


def clustered_market(N, d, kappa, m_1, cluster_sizes, rng):
    """The vendor-with-a-plurality topology: aligned blocks, orthogonal rest."""
    R = np.eye(N)
    start = 0
    for size in cluster_sizes:
        R[start:start + size, start:start + size] = 1.0
        start += size
    return HeterogeneousMarket(response_jacobians_for_R(R, d, rng), kappa, m_1)


def mixed_market(N, d, kappa, m_1, s, n_blind, gamma_ratio, rng):
    """A mixed market for Theorem 3: blind firms first, then corrected ones.

    Corrected firms carry modulus gamma_ratio * m_1. Correction changes a firm's
    gain, not its response direction, so the alignment is untouched.
    """
    if not (0 <= n_blind <= N):
        raise ValueError(f"n_blind must lie in [0, {N}], got {n_blind}")
    R = (1 - s) * np.eye(N) + s * np.ones((N, N))
    E = response_jacobians_for_R(R, d, rng)
    moduli = np.full(N, float(m_1))
    moduli[n_blind:] = gamma_ratio * m_1
    return HeterogeneousMarket(E, kappa, m_1, moduli=moduli)
