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

**Proved today.** The constant-factor version, over all non-anticipating
(adaptive, randomized) policies:
`inf sup Var x C_T >= gamma_PO sigma^2 / 27 (1 - O(T^{-1/2}))` by the Le
Cam two-point reduction at the minimax scale, with the exploited rebate
vanishing at rate `T^{-1/2}` (L2; `latex/proofs.tex` T4; verified
V3.3-V3.4). The sharp constant `1/2` is NOT proved at any prior class -
the D3 sec. 3 composition (`Var >= sigma^2/S_T` times
`C_T >= (1/2) gamma_PO S_T`) is heuristic, not a joint minimax over
(policy, estimator), which is exactly why `proofs.tex` replaced it with
the Le Cam route and lost the constant. It is numerically supported
(`run_open1.py` sec. B: three adaptive amplitude schedules, ratios 0.995
to 1.018). The deviation-budget version is fully general already (T3).

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

**Premise check, RESOLVED as Theorem T9 (2026-08, `posk` pipeline +
`latex/proofs.tex`).** The structure-proofness question is now closed in
both directions. (i) PROVED (T9): within the reach `h >= h* - 2/c` no
design that knows the family's functional form has Cramer-Rao product
below the floor - the family element
`phi0 = 2/c - e^{-c(h-h*)}(2/c + h - h*)` has unit slope at the anchor
and satisfies `|phi0| <= |h - h*|` pointwise exactly on the reach, and
the Rayleigh reduction converts that domination into `R(mu) >= 1`,
strict off the two equality points `{h*, h* - 2/c}`; the
infimum is 1, approached by collapsing symmetric designs (rate
`delta^2`, V9.2). Assumption A4's trust region (`r <= 2/c`) is therefore
not a technicality: it is exactly the condition that makes the floor
structure-proof. (ii) REFUTED beyond the reach: a frozen four-point
witness with a single below-reach probe of weight 3e-4 attains ratio
0.8517 (verified at 50-digit precision; `run_open1.py` C-deep), so the
structural-family clause of the OPEN-1 target is FALSE without the
trust-region restriction, and the register scopes it to A4 with
`r <= 2/c` accordingly. The earlier upgrade note (min ratio 1.005,
tight probes monotonically worse) was a search artifact - the violating
designs need probe weights below the old scan's grid and an asymmetric
near-anchor cluster; recorded as the eleventh measurement-forced pivot.
Two scope caveats remain load-bearing: at finite amplitude under the
TRUE cost, wide-side flattening yields ratio 0.966 < 1 (A'), so the
local/`o(1)` qualifier cannot be dropped; and the witness's violation
lives in the local-quadratic cost model (its TRUE-cost ratio is 1.011).

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

## OPEN-5. The below-reach violation set (new, opened by T9)

**Target.** Characterize the set of designs that beat the floor below
the reach `h* - 2/c`: the infimum of `R(mu)` over all designs on
`(0, h_hi]`, its attaining geometry (the witness suggests an asymmetric
near-anchor cluster plus one vanishing-weight far probe), and whether
the infimum is positive or 0 as `h_lo -> 0`. The scan evidence:
single-far-probe symmetric families never violate (they approach 1 from
above as the probe weight vanishes); the violation requires the
asymmetric structure, and the best known value is 0.8517.

**Status.** Newly opened by T9's sharpness half, and already sharpened
by the verification campaign: (a) `inf_w R(X, w) = m(X)^2` with `m(X)`
the maximal unit-normalized dominated slope on the support (easy
direction proved; equality LP-certified), reducing the problem to a
max-slope linear program per support; (b) the failure is generic below
the reach (for every `A > 2/c` some design supported in `[h* - A, inf)`
violates; certified 3-point example `R = 0.8537`); (c) `phi0` is the
unique single candidate with a left domination interval, of maximal
reach exactly `2/c`. What remains: the infimum of `R` over all designs
on `(0, h_hi]` and its attaining geometry.

## Non-problems (documented so they are not re-opened)

- The `h_PO`-anchored identity: **false**, not open - the `(1 + g^2/v)`
  inflation is verified and the incremental anchor is the definition.
- The mean-modulus eigenvalue formula (EconML companion): **false**, not
  open - orthogonal-response counterexample.
- Fixed-`delta` exploitation decay: does **not** vanish, and is not meant
  to - the CE anchor re-anchors learned structure (D3 honesty box (iii)).
