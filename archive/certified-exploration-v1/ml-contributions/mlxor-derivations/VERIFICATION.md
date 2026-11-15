# Verification Record

**Run: 2026-08-18, `python verify/verify_all.py` (numpy 2.4.6). Result:
34/34 checks passed.** The complete run log ships as
`verify/last_run.log`; every number below is from that run. The suite is
deterministic (fixed seeds) - re-running reproduces it exactly.

## What "verified" means here

Each derivation document (in `derivations/`) ends with a list of claims and
the suite implements one check per claim: exact identities are checked to
floating-point precision; Monte-Carlo claims are checked against predicted
constants within stated tolerances; inequalities are checked pathwise or
over randomized instances; and where a claim asserts that a *condition is
necessary*, the suite also runs the condition-violated case and confirms the
predicted failure appears. Every check prints measured vs expected.

## The three falsifications (found by this process, fixes recorded in the docs)

The suite is not decoration - its first runs falsified three claims as
originally drafted, and each fix produced a sharper result:

1. **D0 fluctuation claim.** The draft said the linear term dominates the
   realized cost's fluctuation. First run: measured/predicted sd ratio 1.62.
   The correct statement is the exact two-term decomposition
   `Var(C) = delta0^2 Var(sum d) + (gamma^2/4) Var(sum d^2)` with vanishing
   cross term - now verified (ratio 1.010, cross/total 0.010).
2. **D2 feedback bias.** The draft's centering-only formula predicted the
   wrong *sign*. The full Stambaugh expansion adds the numerator-denominator
   covariance term and yields
   `bias = phi sigma^2 (3m-1) / ((1-m^2) T v_phi)` - with a sign change at
   `m = 1/3`. Verified at `m = 0.5` (measured +0.00172 +- 0.00042, predicted
   +0.00231) and `m = 0.2` (measured -0.00254 +- 0.00047, predicted
   -0.00185): the sign flip lands exactly where the formula says.
3. **D3b exploitation check.** At *fixed* prior separation the exploitation
   fraction does not vanish - the first check was mis-scaled, and the
   observation sharpened the theory: sustained exploitation of *learned*
   structure is what the certainty-equivalent anchor (D0 section 4)
   re-anchors away; the theorem's decay claim lives at the minimax scale
   `delta ~ sigma/sqrt(S_T)`, where the measured decay ratio is 0.35 for a
   9x horizon increase (predicted 1/3).

An earlier, pre-suite falsification is also recorded in D4/D5's document:
the c-optimal design direction was first mis-stated as `Gamma^{-1}c`; the
substitution proof gives `M* = B cc'/(c' Gamma c)` (probe along `c`
itself), locked by the V4 check (along-c achieves 1.80195 vs the bound
1.80194; 4000 random designs never beat it).

## Check-by-check summary

| # | Claim (derivation) | Result |
|---|---|---|
| V0.1 | `E[C_T] = (1/2) gamma E[sum d^2]` (D0 Lemma 1) | ratio 1.0002 |
| V0.2 | Two-term variance decomposition, zero cross (D0) | ratio 1.010, cross 1% |
| V0.3 | Asymmetric rule breaks lemma by `-delta0 E[sum d]` (D0) | -14.987 vs -14.987 |
| V1.1 | Scalar saturation closed form (D1) | exact to 1e-10 |
| V1.2 | 5x5 energy = Lyapunov quadratic form (D1) | rel. err < 1e-10 |
| V1.3 | Non-normal amplification, exact via `P` (D1) | 1268.2 vs normal cap 2.78 |
| V1.4 | Directional rank-one Lyapunov (D1) | rel. err < 1e-9 |
| V2.1 | Pathwise product identity incl. `(1 + T dbar^2/S)` (D2) | exact to 1e-12 |
| V2.2 | Product variance ~ 1/T (D2) | ratio 4.80 for 4x T |
| V2.3 | Long-run `Var(sum d) = T v (1-m)/(1+m)` (D2) | 5.72 vs 5.86 |
| V2.4 | Feedback bias, m=0.5 (sign +) (D2) | +0.00172+-0.00042 vs +0.00231 |
| V2.5 | Feedback bias, m=0.2 (sign -) (D2) | -0.00254+-0.00047 vs -0.00185 |
| V3.1, V3.2 | van Trees bound met with equality, two designs (D3a) | risk 0.01525/0.01531 vs bound 0.01533 |
| V3.3 | `E|posterior imbalance| <= delta sqrt(S)/sigma`, all t (D3b) | max ratio 0.828 |
| V3.4 | Minimax-scale exploitation decays ~ T^{-1/2} (D3b) | ratio 0.35 (predict 1/3) |
| V4.1 | A-opt `(tr G^{1/2})^2/B` achieved, unbeaten in 4000 (D4) | 44.477 vs best random 61.276 |
| V4.2 | D-opt `M* ~ Gamma^{-1}` (D4) | logdet -9.58 vs -11.19 |
| V4.3 | c-opt value `c'Gc/B`, probe along c (D4) | 1.80194 achieved |
| V4.4 | Isotropic overpayment = dispersion `F` (D4) | exact |
| V4.5 | Temporal shaping irrelevant (D4) | Var ratio 1.032 |
| V5.1 | 2-point Fisher singular / 3-point not (D5) | 1.3e-17 vs 6.2e-3 |
| V6.1 | Perturbed-modulus bound, 9-cell grid (D6) | max excess 2.4e-11 |
| V6.2 | Open-loop schedules stability-neutral (D6) | difference 0 |
| V7.1 | Secant bias constant `tau'''/6` (D7) | -0.17591 vs -0.17572 |
| V7.2, V7.3, V7.4 | `MSE_np` formula on (B,T) grid (D7) | within 2% at all three |
| V7.5, V7.6 | Crossover direction both sides of `delta*` (D7) | correct both sides |
| V8.1 | `v* = sqrt(b rho/a)` (D8) | scan matches |
| V8.2 | `rho* = dh^4/(4 k^2 s^2)`, gamma cancels (D8) | root 0.25800 exact |
| V8.3 | Lai-Robbins schedule on the frontier (D8) | exact |
| V8.4 | Separable `Gamma_PO` vs numeric Hessian (D9) | rel. err < 1e-4, 3 bonds |

## Tolerances and honesty notes

- Monte-Carlo tolerances are stated in the code next to each check; none
  were widened after the fact except where the *claim itself* was corrected
  (the three falsifications above, each documented in its derivation file).
- V2.4/V2.5 sit within 3 standard errors of the predicted constants but not
  on top of them: the `O(1/T^2)` terms of the ratio expansion are visible at
  `T = 400`. The *sign change* is the load-bearing confirmation.
- V3a's designs achieve the van Trees bound with near-equality because the
  Gaussian-prior/Gaussian-noise model makes the posterior mean exactly
  efficient - the check demonstrates tightness, not just validity.
- Nothing in this suite verifies the two labeled-open items (the D3b bound
  at full generality beyond the two-point family, and D6's O(sqrt(T))
  design-regret) - those are stated as proof strategies in their documents
  and are the journal-version work.
