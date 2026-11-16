# Open Problems Register (the workshop-to-journal delta)

The results the workshop paper states as *labeled partial* and the journal
version (Mathematics of OR designation) owes in full. Each entry: precise
statement, what is proved today, the strategy, and the risk assessment.
Nothing here is claimed in the paper beyond its proved portion.

## OPEN-1. The value-budget minimax bound beyond the two-point family (T4)

**Target statement.** For a general prior class `Pi` on the response
(continuous densities on an interval, or the `p`-dim structural family),
over all non-anticipating policies under the certainty-equivalent anchor
and stationary-scale exploration:
`inf sup Var x C_T >= (1/2) gamma_PO sigma^2 (1 - o(1))`.

**Proved today.** The two-point symmetric family, with explicit correction
constant `2 g1 c^2 sigma / (gamma_PO v)` and rate `T^{-1/2}` (D3 sec. 3;
verified V3.3-V3.4). The deviation-budget version is fully general already
(T3).

**Strategy.** Replace the sign-posterior/Pinsker step by a
mutual-information argument: the exploitable component of the linear term
is `phi'(eps_bar)(eps - E[eps | F_t])`, whose conditional mean-square is
controlled by the residual posterior variance; van Trees applied
*conditionally at each t* bounds that variance below by
`sigma^2/(S_t + const)`, and summing the exploitation gives the same
`S_T sqrt(T)` envelope. The two-point case is the extremal configuration by
a standard reduction (least-favorable two-point sub-prior); making that
reduction rigorous for the CE-anchored cost is the actual work.

**Risk.** Moderate. The conditional-van-Trees composition is delicate
(the anchor moves with the posterior); if the general reduction resists,
the journal fallback is the family of all symmetric priors, which the
two-point argument extends to by mixture.

## OPEN-2. Design regret of the safe scheduler (D6 sec. 4)

**Target statement.** The certainty-equivalent re-solving scheme (D-opt
objective, pessimism rule, trust region) attains identification regret
`O(sqrt(T))` against the budget-matched oracle design, with the safety
guarantee of P7.1 holding throughout, and freeze episodes contributing
`O(log T)` additive regret.

**Proved today.** The safety half (P7.1, conditional on a valid confidence
sequence); the algorithm; open-loop neutrality (R2); the perturbed-modulus
translation (L4).

**Strategy.** Elliptical-potential argument on the design information
matrix (the standard linear-bandit design analysis transfers because L3
reduces the problem to static design measures); freeze-episode accounting
via the geometric shrinkage of confidence widths in accumulated design
energy (each freeze ends after the width halves; widths halve at most
`O(log T)` times).

**Risk.** Low-moderate; mostly bookkeeping on known machinery. The one
subtle point is that the pessimism rule couples the design to the
confidence sequence - handled by conditioning on the CS-validity event.

## OPEN-3. Pseudospectral refinement of saturation (D1 sec. 3)

**Target.** Replace the condition-number bound
`E <= kappa(V)^2 ||d_0||^2/(1 - rho^2)` by a Kreiss-constant
characterization of the transient information of non-normal retraining
Jacobians, and characterize which ecosystem structures (heterogeneous
multi-dealer Jacobians) maximize transient information leakage.

**Status.** The exact Lyapunov identity already computes any given case
(verified V1.3); this item is about *structure*, not computation. Purely
journal-scope; connects to the EconML companion's heterogeneous-ecosystem
spectra.

## OPEN-4. Design under serially correlated / feedback-coupled noise

**Target.** L3 (temporal shaping irrelevant) fails when response noise is
serially correlated or feedback-coupled (the A3' regime): characterize the
optimal *temporal* shaping of exploration and the corrected exchange rate.
The `(3m-1)` bias formula (P2.2) is the first-order shadow of this regime.

**Status.** Untouched beyond P2.2. Genuinely open; flagged in D4 sec. 4 as
the scope boundary.

## Non-problems (documented so they are not re-opened)

- The `h_PO`-anchored identity: **false**, not open - the `(1 + g^2/v)`
  inflation is verified and the incremental anchor is the definition.
- The mean-modulus eigenvalue formula (EconML companion): **false**, not
  open - orthogonal-response counterexample.
- Fixed-`delta` exploitation decay: does **not** vanish, and is not meant
  to - the CE anchor re-anchors learned structure (D3 honesty box (iii)).
