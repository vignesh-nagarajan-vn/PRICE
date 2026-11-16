# Theory module spec

One module holding every closed form in the paper. Every experiment checks
itself against this module, so it is written first and certified before any
panel runs.

**Status: written.** [`theory/herd_theory.py`](theory/herd_theory.py), with
acceptance tests in
[`certificates/verify_theory_module.py`](certificates/verify_theory_module.py),
50 checks, all passing. This file remains the spec; where the implementation
departs from it, the departure is recorded at the bottom.

**Dependencies:** numpy and scipy only. CPU-only, deterministic, no state.
Every function is pure: same arguments give the same result, no globals, no
caching.

**Placement:** ships in the REFLEX repository alongside the existing theory
modules, following their naming and certificate conventions rather than
inventing new ones.

## Functions

### Alignment and the effective number of learners (Theorem 1)

```
alignment_matrix(E)                 -> R
    E: (N, d, d) array of response Jacobians
    R: (N, N) correlation matrix of vec(E_i), unit diagonal
    Asserts: symmetric, PSD to tolerance, diagonal == 1

n_eff(R, kappa)                     -> float
    = 1 + kappa * (lambda_max(R) - 1)

m_systemic(m_1, R, kappa)           -> float
    = m_1 * n_eff(R, kappa)

supply_chain_R(N, s)                -> R
    = (1-s) I + s 1 1'      the concentration limit of the decomposition

n_eff_supply_chain(N, s, kappa)     -> float
    = 1 + kappa * s * (N - 1)
    Must equal n_eff(supply_chain_R(N, s), kappa) to machine precision

response_jacobians(N, d, s, rng)    -> E
    Draws E_i = sqrt(s) E_shared + sqrt(1-s) Xi_i with Xi_i independent
    Used by the environment builder and by the concentration certificate

clustered_R(N, cluster_sizes)       -> R
    Block-diagonal all-ones blocks. The vendor-with-a-plurality topology

mean_alignment(R)                   -> float
    Off-diagonal mean. Exists only so the paper can show it is the wrong
    statistic. Never called by any stability function
```

`mean_alignment` carries a docstring saying it is a foil, not a tool. Anyone
reading the module should not be able to mistake it for a diversity index the
paper endorses.

### Cadence (Theorem 2)

```
mu_N(m_N, c, K)                     -> float
    = -m_N + c**K * (1 + m_N)

k_max(m_N, c)                       -> float
    = log((m_N - 1)/(m_N + 1)) / log(c)      for m_N > 1
    = +inf                                    for m_N <= 1

critical_crowding(c)                -> float
    = (1 + c)/(1 - c)       the m_N past which no cadence helps

is_stable_lazy(m_N, c, K)           -> bool
    = abs(mu_N(m_N, c, K)) < 1
    Must agree with K < k_max(m_N, c) on every integer K
```

### Herd immunity (Theorem 3)

```
n_c(m_1, kappa, s)                  -> float
    = 1 + (1/m_1 - 1)/(kappa * s)

rho_star(N, m_1, kappa, s)          -> float
    = max(0, 1 - n_c(m_1, kappa, s)/N)

mixed_market_jacobian(N, n_blind, m_1, kappa, s, gamma_ratio)  -> J
    Two-block joint Jacobian. gamma_ratio = gamma/gamma_PO in (0, 1]

mixed_market_radius(...)            -> float
    Exact spectral radius via the two-block secular root.
    Falls back to a dense eigensolve, which is also the certificate

substitution_frontier(N, m_1, kappa, s_grid) -> rho_star_curve
    The (rho, s) iso-stability curve. The headline figure's ground truth
```

### The wedge (Theorem 4)

```
stationary_variance(m_N, sigma)     -> float
    = sigma**2 / (1 - m_N**2)       for m_N < 1, else +inf

dV_dm(m_N, sigma)                   -> float
    = 2 * sigma**2 * m_N / (1 - m_N**2)**2

pigouvian_wedge(N, m_1, kappa, s, sigma, dm_da)  -> float
    Externalized marginal cost. Both channels, aggressiveness and provenance
```

## Acceptance tests

The module is not done until all of these pass.

1. **Reduction.** `n_eff(ones((N,N)), kappa)` equals the base law
   `1 + kappa*(N-1)` for `N` in `2..50`, every `kappa` on a grid.
2. **Two routes agree.** `n_eff_supply_chain(N, s, kappa)` equals
   `n_eff(supply_chain_R(N, s), kappa)` to machine precision.
3. **The simplex correction.** `n_eff` of the simplex `R` equals
   `1 + kappa/(N-1)`, and `m_1*(1-kappa)` appears in the Jacobian's spectrum but
   is not its radius. This test exists because the plan of record got it wrong;
   see `../math/01-theorem1-alignment.md`.
4. **Cadence agreement.** `is_stable_lazy` and `K < k_max` agree on every
   integer `K` in `1..200` across an `(m_N, c)` grid.
5. **Herd-immunity limit.** `mixed_market_radius` with `gamma_ratio -> 0`
   converges to the blind-block radius, and `rho_star` predicts the sign change
   with zero mismatches on 4000 random draws.
6. **Monotonicity.** `k_max` decreasing in `m_N`; `rho_star` increasing in `s`;
   `pigouvian_wedge` increasing in `N`, in `kappa`, and in `m_N`.

Tests 1 and 2 are the ones that catch a wrong sign convention. Test 3 is the
one that catches a regression back to the plan's version. Test 5 is the paper.

## Departures from this spec, as built

Recorded rather than silently absorbed.

**Added, because the derivations produced them after this spec was written.**
`simplex_R` and `monoculture_R` as named anchors; `joint_jacobian`;
`n_eff_mean_index`, the second foil; `hetero_modulus_bounds`, returning the
bracket and the exact value together; `is_stable_mixed`, `min_corrected`,
`rho_star_imperfect` and `critical_efficacy` from Theorem 3's exact treatment.

**Changed.** `mixed_market_radius` branches on empty blocks. The spec describes
it as the two-block secular root with a dense fallback; with `n_blind` equal to
`0` or `N` the quadratic leaves a phantom root behind, so those cases take the
single-block form. This is a correctness fix, not a shortcut.

**Not built.** `pigouvian_wedge`, because Theorem 4's welfare page is not
derived. An acceptance test asserts its absence so it cannot arrive by accident.

**Cautions attached to two functions.** `mean_alignment` and `n_eff_mean_index`
carry docstrings saying they are foils. `rho_star` carries one saying it is the
policy object and not the exact criterion, since `rho > rho_star` mispredicts the
all-blind stable market; `is_stable_mixed` is the verdict function. Acceptance
test A5 confirms those mispredictions are real, so the caution is load-bearing
rather than decorative.
