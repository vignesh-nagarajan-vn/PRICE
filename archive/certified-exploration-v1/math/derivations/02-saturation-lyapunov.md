# D1 - Information Saturation: the Exact Lyapunov Form

**Status: scalar case verified to 1e-16; d-dimensional identity verified
numerically (V1), including the non-normal amplification. Proofs complete.**

## 1. Scalar warm-up (the verified base case)

With no exploration (`u_t = 0`) and `m < 1`, `d_t = (-m)^t d_0`, so

```
   D_T = sum_{t=0}^{T} d_t^2 = d_0^2 (1 - m^{2(T+1)}) / (1 - m^2)  -->  d_0^2/(1 - m^2).
```

Fisher information for `eps` from OLS on the trajectory is `S_xx/sigma^2 <=
D_infty/sigma^2`: **bounded uniformly in the horizon**. Hence for any
unbiased estimator, at every horizon,

```
   Var(eps_hat)  >=  sigma^2 (1 - m^2) / d_0^2 .
```

**Corollary 1.1 (safety implies blindness).** The cap `d_0^2/(1-m^2)` is
strictly increasing in `m`: the fast-contracting (safe) loop reveals least;
identifiability is a near-instability phenomenon. (Immediate from the
formula; the *economic* content is stated in the paper body.)

**Corollary 1.2 (design degeneracy).** At `m = 1` the noiseless iterates form
the period-2 orbit `{+d_0, -d_0}`; for `m < 1` the support collapses
geometrically onto `{0}`. In either case the empirical design measure has at
most 2 effective support points - which by D5 (Chebyshev counting) cannot
identify a 3-parameter response family. Curvature is invisible to
trajectories at every `m`.

## 2. The d-dimensional identity via the discrete Lyapunov equation

Let the linearized joint loop be `d_{t+1} = M d_t`, `M in R^{dxd}`,
`rho(M) < 1` (for the multi-bond/multi-dealer instantiations `M` comes from
theory 1.5/1.3 and is generally **not symmetric**).

**Theorem (exact energy).** The total design energy is the quadratic form

```
   E(d_0) := sum_{t>=0} || M^t d_0 ||^2  =  d_0' P d_0 ,
```

where `P` is the unique PSD solution of the **discrete Lyapunov equation**

```
   P = I + M' P M .
```

**Proof.** `P := sum_{t>=0} (M')^t M^t` converges absolutely iff
`rho(M) < 1` (Gelfand). Then
`M' P M = sum_{t>=0} (M')^{t+1} M^{t+1} = P - I`. Uniqueness: the difference
`Q` of two solutions satisfies `Q = M' Q M = (M')^t Q M^t -> 0`. Finally
`d_0' P d_0 = sum ||M^t d_0||^2` by expanding the sum. []

Scalar check: `P = 1/(1 - m^2)` recovers section 1.

**Directional information.** For the response slope in direction `u`
(`tau_t = tau* - eps u' d_t + zeta_t` probing the component along `u`), the
relevant energy is `sum (u' M^t d_0)^2 = d_0' P_u d_0` with
`P_u = u u' + M' P_u M` - the same Lyapunov structure with rank-one right
side. Hence Fisher information is bounded in **every** direction, and the
information *operator* `I <= P_full/sigma^2` where `P_full` solves the
matrix-valued equation. Saturation is not a scalar accident.

## 3. Non-normality: transiently amplified information

If `M` is normal, `P` has eigenvalues `1/(1 - lambda_i^2)` and energy is
governed by the spectrum alone. If `M` is **non-normal** (heterogeneous
multi-dealer Jacobians are), transient growth inflates the energy beyond the
spectral prediction:

```
   E(d_0) <= kappa(V)^2 * ||d_0||^2 / (1 - rho(M)^2)          (V eigenbasis, kappa its condition number)
```

and the inequality is *achieved* in order: for the Jordan-type family
`M = [[m, a], [0, m]]` the energy along the first coordinate grows like
`a^2/(1-m^2)^3` for large `a` (verified numerically in V1 against the exact
Lyapunov solve). Reading: **badly-conditioned ecosystems leak extra
information about themselves during transients** - the free-information
remark of the paper, now with an exact constant (`P` itself). The paper
states the exact `P`-form and keeps the pseudospectral refinement for the
journal version.

## 4. What Theorem 1 does *not* say (scope, stated in the paper)

- With exploration on, saturation is *replaced* by the exchange rate (D2):
  the transient information `d_0' P d_0/sigma^2` is the free part;
  everything after is bought.
- The bound is for the linearized loop; the simulator's nonlinear regimes
  are handled empirically (the drift study, D2/V2 protocol).

## 5. Verified numerically (V1)

1. Scalar closed form vs direct sum (exact to floating point).
2. 2x2 and 5x5 random stable `M`: direct energy sum vs Lyapunov solve
   (`scipy`-free fixed-point iteration), agreement to 1e-12.
3. Non-normal amplification: energy for `[[m,a],[0,m]]` grows ~ `a^2`, far
   exceeding the normal-matrix bound `1/(1-m^2)`, and matches `d_0' P d_0`
   exactly.
4. Directional version: rank-one Lyapunov `P_u` vs direct directional sum.
