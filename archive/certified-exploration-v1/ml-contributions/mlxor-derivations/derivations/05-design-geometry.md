# D4/D5 - The Geometry of Optimal Exploration, and What Trajectories Can Never Identify

**Status: all three design optima derived with proofs; the temporal-shaping
lemma proved; the Chebyshev counting result proved; all verified in V4/V5.**

Setting: `d`-dimensional decision, response Jacobian estimand, exploration
with stationary second moment `M := E[d d'] (PSD)`, response noise variance
`sigma^2` per coordinate, value budget `B = (T/2) tr(Gamma_PO M)` per Lemma
1's `d`-dimensional form `cost rate = (1/2) E[d' Gamma_PO d] =
(1/2) tr(Gamma_PO M)`. Per-unit-time information matrix `M/sigma^2`.
Absorb `T` and `sigma^2` into units; the three problems and their exact
solutions:

## 1. A-optimality: what to do if you must know everything equally

```
   minimize   tr( M^{-1} )     subject to   tr( Gamma M ) <= B,   M > 0
   solution:  M* = ( B / tr Gamma^{1/2} ) * Gamma^{-1/2}
   value:     tr( M*^{-1} ) = ( tr Gamma^{1/2} )^2 / B .
```

**Proof.** The objective is strictly convex on the PSD cone, the constraint
linear, so KKT is sufficient: `-M^{-2} + lam Gamma = 0` gives
`M = lam^{-1/2} Gamma^{-1/2}`; the budget pins `lam^{-1/2} =
B/tr(Gamma^{1/2})`; substitute. (Diagonal-case Cauchy-Schwarz check:
`(sum 1/m_i)(sum g_i m_i) >= (sum sqrt(g_i))^2`, equality at
`m_i ~ g_i^{-1/2}`.) []

**Reading: explore where the objective is flat.** The optimal exploration
covariance is `Gamma_PO^{-1/2}` - inverse *square root*, not inverse: flat
directions are cheap per unit information but not infinitely favoured;
curved directions are expensive but cannot be abandoned when every
coordinate of the Jacobian is needed.

**Corollary (the price of isotropic jitter).** Isotropic exploration at the
same budget (`M = (B/tr Gamma) I`) has risk `d * tr Gamma / B`; the ratio to
optimal is

```
   F  =  d * tr(Gamma) / ( tr Gamma^{1/2} )^2   >=  1 ,
```

with equality iff all curvatures are equal (Cauchy-Schwarz). `F` is the
**curvature dispersion** of the objective - the exact factor by which
"naive exploration" (optimal in LQR, Simchowitz-Foster 2020) overpays in
the performative setting. Computable on the calibrated multi-bond
`Gamma_PO`.

## 2. D-optimality: what the confidence-volume objective wants

```
   maximize   log det M       subject to   tr( Gamma M ) <= B
   solution:  M* = ( B / d ) * Gamma^{-1}      (value: log det = d log(B/d) - log det Gamma).
```

**Proof.** `grad log det M = M^{-1} = lam Gamma` at stationarity;
concave objective, linear constraint. []

Note the shape difference: A-opt gives `Gamma^{-1/2}`, D-opt gives
`Gamma^{-1}`. The paper must never conflate them; the algorithm (D6) uses
D-opt internally (Frank-Wolfe on `log det`), while the headline risk theorem
is A-opt. Both are stated; the discrepancy factor between them is itself
computable and small when dispersion is moderate.

## 3. c-optimality: what the PerfGD correction actually needs (the new one)

The corrected update consumes the response only through one functional -
the correction direction `c` (in the scalar family, `Delta` needs
`eps(h*)`; in `d` dimensions, `c = grad_E Delta`, a fixed vector once the
operating point is known). Estimating `c' theta` alone:

```
   minimize   c' M^{-1} c     subject to   tr( Gamma M ) <= B
   design:    M*  =  B * c c' / ( c' Gamma c )        (rank-one: probe ALONG c itself)
   value:     c' M*^{+} c  =  c' Gamma c / B .
```

**Proof.** Substitute `N = Gamma^{1/2} M Gamma^{1/2}` (`tr N = tr(Gamma M)
<= B`), `w = Gamma^{1/2} c`; the objective is `w' N^{-1} w`. Cauchy-Schwarz:
`(w'w)^2 = (w' N^{-1/2} N^{1/2} w)^2 <= (w'N^{-1}w)(w'Nw)` and
`w'Nw <= ||w||^2 tr N <= ||w||^2 B`, so `w'N^{-1}w >= ||w||^2/B`, attained
at `N* = B ww'/||w||^2`. Back-substituting: `M* = Gamma^{-1/2} N*
Gamma^{-1/2} = B (Gamma^{-1/2} w)(Gamma^{-1/2} w)'/||w||^2` and
`Gamma^{-1/2} w = c`, giving `M* = B cc'/(c'Gamma c)`. []

**The corrected trio, worth a display in the paper.** A-optimality shapes
exploration as `Gamma_PO^{-1/2}`, D-optimality as `Gamma_PO^{-1}`, and
c-optimality probes **along the correction direction itself** - the
curvature does not tilt the direction at all, it only *prices* it: the
value `c' Gamma_PO c / B` says the cost of knowing your correction is the
`Gamma_PO`-norm of what the correction asks for. (An earlier draft of this
derivation mis-stated the c-optimal direction as `Gamma^{-1} c`; the
substitution above corrects it - recorded per the project's falsification
convention, and locked by the V4 numerical check.)

The savings over A-opt is the operational argument for correction-targeted
probing: a desk does not need the whole Jacobian, and the geometry says
exactly what it may skip. (Rank-one designs are singular - in practice
regularized by the trust region; the paper states the limit and the
regularized form.)

## 4. The temporal-shaping lemma (design space collapse)

**Lemma.** With response noise iid and independent of the deployment path,
the information about the response parameters depends on the exploration
process only through its empirical second moment `sum d_t d_t'`. Hence
temporally-correlated exploration (AR-shaped, cyclic, burst) buys nothing
beyond its stationary design measure, and the design problem is exactly the
static problems of sections 1-3.

**Proof.** The conditional log-likelihood is
`sum_t -(tau_t - a - theta' d_t)^2/(2 sigma^2)`; its Hessian in `theta` is
`-sum d_t d_t'/sigma^2` regardless of the temporal order or dependence of
`{d_t}`. []

(The lemma fails when noise is serially correlated or feedback-coupled -
the D2 section 4 regime - where shaping *does* matter; stated as the scope
boundary and left to the journal version.)

## 5. D5 - Chebyshev counting: why curvature is invisible to trajectories

Structural family (REFLEX 1.1/`structural_response.py`):

```
   tau(h) = C0 + C1 exp(-c h) ,     parameters (C0, C1, c),  p = 3 .
   sensitivity: s(h) = ( 1, exp(-c h), -C1 h exp(-c h) ) .
```

**Proposition.** (i) `{1, e^{-ch}, h e^{-ch}}` is an extended Chebyshev
system on any interval (nonzero Wronskian-type determinants; standard).
(ii) Therefore the Fisher matrix `M(xi) = sum_i w_i s(h_i) s(h_i)'` of any
design `xi` with fewer than 3 distinct support points is **singular**, and
the decay rate `c` is unidentified. (iii) Any noiseless RRM trajectory has
effective support <= 2 (D1 Corollary 1.2: geometric collapse or period-2),
hence **no retraining trajectory, at any modulus, identifies the curvature
of its own response family**. (iv) D-optimal designs for this family on a
trust-region interval `[h*-r, h*+r]` are supported on exactly 3 points
including both endpoints (de la Garza-type; the interior point computed
numerically in the experiments).

**Proof of (ii).** `rank(M(xi)) <= #support(xi)`; a 2-point design gives
rank <= 2 < 3, so `det M = 0` and the c-direction lies in (or meets) the
null space. Exact-arithmetic check in V5: `det M = 0` to machine precision
for *every* random 2-point design, `det M > 0` for generic 3-point designs.
[]

This is the sharp form of the repo's empirical rule "exponential response
fits need a wide spread range", and the formal reason the anti-echo freeze
(`structural_response.py`, `identified` flag) exists.

## 6. Verified numerically (V4/V5)

1. A-opt: random-search over PSD `M` at fixed budget never beats
   `(tr Gamma^{1/2})^2/B`; the formula's `M*` achieves it (5x5, random SPD
   `Gamma`).
2. D-opt: `M* = (B/d) Gamma^{-1}` beats random feasible designs in
   `log det`.
3. c-opt: random-search never beats `c'Gamma c/B`; the rank-one construction
   approaches it.
4. Isotropic factor `F = d tr Gamma/(tr Gamma^{1/2})^2` matches the measured
   ratio.
5. Temporal lemma: AR-shaped and iid exploration with matched empirical
   second moment give identical OLS covariance.
6. Chebyshev: `det M = 0` (2-point) vs `> 0` (3-point), and the c-direction
   variance is infinite/huge under 2-point designs.
