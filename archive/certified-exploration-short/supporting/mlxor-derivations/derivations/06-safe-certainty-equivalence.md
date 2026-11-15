# D6 - Safety Under Certainty Equivalence: the Perturbed-Modulus Lemma and the Pessimism Rule

**Status: the structural observation and the perturbed-modulus lemma derived
and verified (V6); the safety proposition proved conditional on a valid
confidence sequence; the O(sqrt(T)) design-regret bound stated with proof
strategy (journal-version item, labeled).**

## 1. Where the stability constraint actually bites (a structural fact)

A fact discovered in the derivation and promoted to the paper: **open-loop
exploration cannot destabilize the linearized loop.** With
`d_{t+1} = -m d_t + u_t` and `u_t` a planned (history-independent) sequence,
the homogeneous dynamics keep modulus `m < 1` regardless of `u` - bounded
inputs give bounded outputs. The stability risk of probing enters through
exactly two channels:

1. **Estimate feedback (the real one).** The corrected update deploys
   `h_{t+1} = h_t + eta * Phi_hat'(h_t)` where `Phi_hat' = G + Delta_hat`
   uses the *estimated* response `eps_hat(.)`. Estimation error changes the
   closed-loop map itself - this is where safety must be engineered.
2. **Basin exit (nonlinear).** Large probes can leave the contraction
   neighbourhood; handled by the trust region `|d_t| <= r`, a constraint the
   design problems of D4 already carry.

## 2. The perturbed-modulus lemma

Let the corrected map be `Psi(h) = h + eta [ G(h) - beta (h - psi)
eps_hat(h) ]` and let `rho_hat` be its slope at the fixed point; `rho` the
slope under the true `eps(.)` (`rho = 1 - eta gamma_PO`, 1.2 section 4).

**Lemma.** With `e(h) := eps_hat(h) - eps(h)`,

```
   | rho_hat - rho |  <=  eta * beta * ( ||e||_inf  +  |h* - psi| * ||e'||_inf )
                       =: eta * beta * L_corr * || e ||_C1 .
```

**Proof.** `Psi'(h) = 1 + eta Phi_hat''(h)`;
`Phi_hat'' - Phi'' = -beta d/dh [ (h-psi) e(h) ] = -beta [ e + (h-psi) e' ]`.
Take absolute values and the sup over the operating interval. []

For the structural family the `C^1` error is controlled by the parameter
error with explicit constants (`e = eps(.; theta_hat) - eps(.; theta)`;
`||e||_C1 <= L_theta ||theta_hat - theta||` with `L_theta` computable from
`(C1, c, r)` - stated with the constant in the appendix). So the
confidence region for `theta` translates directly into a modulus interval.

## 3. The pessimism rule and the safety proposition

Maintain any anytime-valid confidence sequence `Theta_t` for the response
parameters (from the CRN machinery of REFLEX 1.4, or a standard
self-normalized bound; width shrinks as information accumulates per D2).

**Rule.** At each step choose `(eta_t, design)` such that the **worst-case**
modulus over `Theta_t` respects the margin:

```
   sup_{theta in Theta_t}  | rho_hat(theta) |  <=  1 - c_margin ,
```

i.e. pessimistic on stability - while the design objective (D4) is evaluated
optimistically. When `Theta_t` is too wide to certify the margin, the rule
freezes correction and explores under the blind (provably stable, `m < 1`)
loop - exactly the anti-echo freeze of `structural_response.py`, now derived
rather than engineered.

**Proposition (safety).** If the confidence sequence is valid at level
`1 - delta` (uniformly over time), then with probability `>= 1 - delta` the
realized modulus satisfies `|rho_t| <= 1 - c_margin` for **all** `t`
simultaneously. *Proof: on the event that `theta in Theta_t` for all `t`
(probability `>= 1-delta` by anytime-validity), the rule's sup dominates the
realized modulus at every step.* []

The engineering reading: safety is inherited from the confidence sequence's
uniform validity - no union bound over steps, no per-step failure
accumulation.

## 4. Design regret (stated; journal deliverable)

**Claim (to prove in full).** The certainty-equivalent re-solving scheme
(D-opt objective from D4, pessimism rule above, trust region `r`) attains
identification regret `O(sqrt(T))` against the budget-matched oracle design,
with the elliptical-potential argument of linear-bandit design theory
supplying the rate and the freeze episodes contributing an additive
`O(log T)` term (each freeze ends when the confidence width halves, and
widths shrink geometrically in accumulated design energy). Labeled
**partial** for the workshop: algorithm + safety proved; the regret constant
and the freeze-episode accounting are the journal version's work.

## 5. Verified numerically (V6)

1. Open-loop neutrality: injected bounded schedules never change the
   measured homogeneous contraction rate (slope of the deviation envelope).
2. The perturbed-modulus lemma: corrected loops run with deliberately
   corrupted `eps_hat` (`C^1` error swept over a grid); the measured
   fixed-point slope deviates from `1 - eta gamma_PO` by less than the
   lemma's bound in every cell, and the bound is tight within a factor ~2 at
   small errors.
3. The pessimism rule: under a simulated valid confidence sequence, no
   trajectory in 400 seeded runs violates the margin; under a deliberately
   *invalid* (too-narrow) sequence, violations appear - the assumption is
   necessary.
