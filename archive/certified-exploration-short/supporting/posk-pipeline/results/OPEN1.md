# OPEN-1 premise check: reach of the exchange-rate floor

Anchor h* = h_PO = 1.8461, gamma_PO(h*) = 0.4133, register market.

## A. Nonparametric estimators, local-quadratic cost

min ratio over 3-point designs: 1.000000; over 4-point: 1.000000.
The floor is TIGHT and un-beatable in its own scope (min = 1 at mean-centered designs). PASS

## A'. Nonparametric, TRUE incremental cost (finite amplitude)

min ratio: 0.9664 at support [2.643, 2.6, 1.824], weights [0.007, 0.022, 0.971].
Finite-amplitude wide-side probing rides the defensive-widening curvature collapse (Phi flattens above h*), so the TRUE cost undercuts the local-quadratic model - the known A1-scope drift (E2's drift cell), a polynomial effect that vanishes as amplitude -> 0. The floor's exact scope is local, as stated in T2/T4.

## B. Adaptive amplitude schedules (Monte Carlo, true cost)

| schedule | ratio |
|---|---|
| constant r = 0.10, centered at h* | 1.018 |
| decaying r_t = 0.25/sqrt(1+t/20), centered | 0.995 |
| constant r = 0.10, anchor misplaced +0.2 | 4.910 |

Amplitude adaptivity does not beat the floor (ratios ~ 1 up to MC error and small-amplitude drift); a misplaced anchor pays strictly more. PASS

## C. Structural family (C0, C1, c known): Cramer-Rao ratio

Baseline search (4000 random + 2500 refinements, the historical run): min ratio, local-quadratic cost: **1.0050** at support [1.988, 1.899, 1.965, 1.775], weights [0.014, 0.468, 0.051, 0.466].

min ratio, TRUE cost: **1.0051** at support [1.912, 1.926, 1.771, 1.977], weights [0.228, 0.235, 0.505, 0.032].

Mechanism scan (pair at h* +/- 0.1 plus one tight probe at t, weight grid 0.05-0.4):

| tight probe t | best ratio |
|---|---|
| 1.00 | 5.7177 |
| 0.80 | 8.8815 |
| 0.60 | 13.5204 |
| 0.40 | 20.3274 |
| 0.20 | 30.3623 |
| 0.05 | 40.9418 |

## C-deep. The two-sided picture: the reach h* - 2/c is exact (T9)

Hardened search RESTRICTED to the reach [h* - 2/c, h_hi] = [0.5128, 4.00] (3 x 30000 random + 10000 refinements): min ratio **1.00054** - the floor holds, as Theorem T9 proves it must.

Hardened GLOBAL search (support allowed down to h_lo = 0.05): min ratio **0.85164** at support [1.873, 0.05, 1.866, 1.307], weights [0.0033, 0.0003, 0.9557, 0.0407] - the floor BREAKS below the reach.

Canonical witness (frozen design; ratio verified independently at 50-digit precision = 0.85165047...): support [1.8726, 0.05, 1.8665, 1.3073], weights [0.003329, 0.000272, 0.955702, 0.040697], local-cost ratio **0.85165**, TRUE-cost ratio 1.0112 (> 1: the violation lives in the local-quadratic cost model, the floor's own scope). Every witness support point except h = 0.05 lies within the reach: the one below-reach probe, carrying weight 3e-4, is what breaks the floor.

**Verdict: structure-proofness is a REACH phenomenon, and the reach is exact.** Within h >= h* - 2/c (two curvature lengths below the anchor; every trust-region design the paper's agent can deploy, since r <= 0.8 < 2/c = 1.333) no family-knowing design beats the floor: that is now Theorem T9, proved by exhibiting the family element phi0(h) = 2/c - e^{-c(h-h*)}(2/c + h - h*) whose pointwise domination |phi0| <= |h - h*| holds exactly on [h* - 2/c, inf). Below the reach the domination fails, and a design exploiting that region (an asymmetric near-anchor cluster plus one vanishing-weight far probe) beats the floor by 15 percent. The earlier verdict of global structure-proofness (min 1.005, tight probes 'monotonically worse') was an artifact of two search gaps, recorded as the eleventh measurement-forced pivot: the weight grid never went below 0.05 (the violating probe carries 3e-4), and the random search never found the asymmetric cluster. Symmetric-pair-plus-far-probe families stay above the floor at every weight (they approach 1 from above as the weight vanishes); the violation requires the asymmetric structure.

## Register amendment (applied to OPEN-PROBLEMS.md and THEOREMS.md)

The structure-proofness conjecture is RESOLVED, in both directions: proved within the reach (T9), refuted beyond it (the witness). OPEN-1's structural-family clause is re-scoped to trust-region policies (assumption A4 with r <= 2/c), which T9 shows is not a technicality but exactly the condition that makes the floor structure-proof. Two scope caveats remain load-bearing: (i) at finite amplitude under the TRUE cost, wide-side flattening yields ratio 0.966 < 1 (A'), so the o(1)/local qualifier cannot be dropped; (ii) the exact characterization of which below-reach designs violate the floor (and by how much at most) is a new open problem, OPEN-5.
## D. The boundary: c known a priori

Same scan as C with the c coordinate dropped (theta = (C0, C1), sensitivity (1, e^{-ch})):

| tight probe t | best ratio (local cost) | best ratio (true cost) |
|---|---|---|
| 1.00 | 0.3002 | 0.3624 |
| 0.80 | 0.2028 | 0.2674 |
| 0.60 | 0.1358 | 0.1992 |
| 0.40 | 0.0895 | 0.1511 |
| 0.20 | 0.0586 | 0.1165 |
| 0.05 | 0.0425 | 0.0967 |

Unconstrained two-point designs (h*, t), best weight:

| probe t | best ratio (local cost) | best ratio (true cost) |
|---|---|---|
| 0.500 | 0.09652 | 0.15720 |
| 0.200 | 0.05267 | 0.10829 |
| 0.050 | 0.03854 | 0.09061 |
| 0.010 | 0.03542 | 0.08648 |
| 0.001 | 0.03475 | 0.08558 |

With c known the floor breaks outright, and the ratio falls monotonically as the probe moves away from the anchor, never settling at any particular value (0.0348 at t = 0.001 and still decreasing): there is no known-c floor at 0.05 or anywhere else the scan reaches. Remote sensitivity e^{-ch} no longer has to be pulled back through c-hat, so its cheapness is banked instead of discounted: the floor is an ignorance-of-curvature phenomenon, which is the boundary the paper's Section 3 states (its quoted ratios 0.30 at t=1.0 and 0.04 at t=0.05 are this table's local-cost column). PASS

