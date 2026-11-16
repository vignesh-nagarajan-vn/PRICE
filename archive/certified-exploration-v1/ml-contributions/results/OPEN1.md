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

min ratio, local-quadratic cost: **1.0050** at support [1.988, 1.899, 1.965, 1.775], weights [0.014, 0.468, 0.051, 0.466].

min ratio, TRUE cost: **1.0051** at support [1.912, 1.926, 1.771, 1.977], weights [0.228, 0.235, 0.505, 0.032].

Mechanism scan (pair at h* +/- 0.1 plus one tight probe at t, best weight):

| tight probe t | best ratio |
|---|---|
| 1.00 | 5.7177 |
| 0.80 | 8.8815 |
| 0.60 | 13.5204 |
| 0.40 | 20.3274 |
| 0.20 | 30.3623 |
| 0.05 | 40.9418 |

**Verdict: the floor is STRUCTURE-PROOF - the premise of OPEN-1's structural-family clause is numerically confirmed.**

The a-priori threat was that tight-side probes (sensitivity e^{-ch} grows exponentially as h falls) would let a policy that KNOWS the family buy eps(h*) below the floor. The search refutes the threat: the optimizer's best design collapses back to a near-symmetric cluster at h* (the two-point extremal configuration re-emerges as the PARAMETRIC optimum), and the tight-probe scan is monotonically WORSE. Mechanism: eps(h*) = eps(t) e^{-c (h* - t)}, so remote information must be pulled back through c, and the extrapolation variance in c-hat - amplified by the pull-back distance - dominates the sensitivity gain. Off-anchor information about a LOCAL slope is discounted at exactly the rate its cheapness accrues; parametric side information does not evade the exchange rate.

## Register amendment (applied to OPEN-PROBLEMS.md)

OPEN-1 keeps the structural-family clause; its risk entry is upgraded from unverified to NUMERICALLY SUPPORTED (min Cramer-Rao ratio 1.005 over 4-point exponential-family designs, both cost models; two-point symmetric configuration extremal - consistent with the least-favorable-two-point reduction the proof strategy needs). One scope caveat is load-bearing and stays in the statement: at finite amplitude under the TRUE cost, wide-side flattening yields ratio 0.966 < 1 (A'), so the o(1)/local qualifier cannot be dropped. The structure-proofness itself (parametric CR product minimized by the symmetric local design) is recorded as a new conjecture-with-evidence for the journal version.
