# D1. Theorem 1: the alignment spectrum

**Status: complete.** Every statement below is proved here and certified in
[`verify_theorem1_proof.py`](../../ml-contributions/certificates/verify_theorem1_proof.py),
123 checks, all passing. The note
[`../01-theorem1-alignment.md`](../01-theorem1-alignment.md) is the summary; this
file is the proof it summarizes.

What this file adds over the note: the note *asserts* the generalized Jacobian
`J = -m_1[(1-kappa)I + kappa R]` by replacing `1 1'` with `R`. Section 1 derives
it from the response Jacobians instead, and states the hypotheses the derivation
needs. Section 6 upgrades the note's two counterexamples against mean-based
diversity indices into a one-line theorem with a signed error direction.

---

## 1. The reduction lemma

The substitution `1 1' -> R` is the whole paper, so it is derived rather than
posited.

**Setup.** Firm `i` deploys `h_i in R^d`. Its deployment reshapes the flow it
faces through its response Jacobian `E_i` in `R^{d x d}`. Write `vec E_i` for its
`d^2`-vector form, `||.||_F` for the Frobenius norm, and

```
   E_hat_i  =  E_i / ||E_i||_F
```

for firm `i`'s unit response direction.

**Hypotheses.**

- **(H1) Rank-one deviation.** Firm `i`'s deviation from the joint equilibrium is
  a scalar `x_i` along its own response direction. The market state is the vector
  `x in R^N`, not the full `R^{Nd}`.
- **(H2) Equal response magnitude.** `||E_i||_F = eps` for every `i`. This is
  standing assumption A2, restated in terms of the new object: the response
  strength `eps` inherited from the base model *is* the Frobenius norm of the
  response Jacobian.
- **(H3) Own-channel sensing.** Firm `i` retrains against the component of the
  pool distortion lying along its own response direction, feeling its own
  contribution in full and each competitor's with spillover weight `kappa`.
- **(H4) Quadratic retraining.** Firm `i` minimizes a `gamma`-strongly-convex
  own objective whose sensitivity to the felt distortion is `beta`, giving
  `x_i^+ = -(beta/gamma) * felt_i`.

**Lemma 1 (reduction).** Under (H1) to (H4) the joint retraining map is linear
with Jacobian

```
   J  =  -m_1 [ (1 - kappa) I  +  kappa R ] ,      m_1 = eps * beta / gamma ,
```

where `R = (r_ij)` and `r_ij = <vec E_i, vec E_j> / (||E_i||_F ||E_j||_F)`.

*Proof.* The pool carries the aggregate distortion `Z = sum_j x_j E_j`. By (H3)
the distortion firm `i` feels is

```
   felt_i  =  <E_hat_i, x_i E_i>  +  kappa * sum_{j != i} <E_hat_i, x_j E_j>
           =  eps [ x_i  +  kappa * sum_{j != i} r_ij x_j ] ,
```

using `<E_hat_i, E_j> = eps * r_ij` from (H2). Since `r_ii = 1`, the own term can
be folded into the sum:

```
   felt_i  =  eps [ (1 - kappa) x_i  +  kappa * sum_j r_ij x_j ] .
```

By (H4), `x^+ = -(beta/gamma) * eps [ (1-kappa) I + kappa R ] x`, and
`m_1 = eps*beta/gamma` is exactly the base model's single-firm modulus. []

**Why `r_ij` and not something else.** The alignment enters because firm `i`
senses the pool through its own response channel. Two firms whose deployments
perturb the environment in orthogonal directions do not read each other's
perturbations at all, however large those perturbations are. This is the
mechanism the paper is about, and it is (H3) that carries it.

**The monoculture corner.** If all `E_i` are equal then `r_ij = 1` for all `i, j`,
so `R = 1 1'` and Lemma 1 returns the inherited base result exactly. The base
model is therefore not generalized away; it is the corner of the new law where
every firm's feedback points the same way. [VERIFIED, P1]

**Certificate.** P1 builds random `E_i`, forms the retraining map from the felt
distortion without ever constructing `R`, differentiates it numerically, and
compares against `-m_1[(1-kappa)I + kappa R]`. Agreement to `5.6e-17` at
`(N, d, kappa)` of `(3,4,0.8)`, `(5,6,0.35)`, `(8,5,1.0)` and `(6,7,0.0)`, so
both spillover endpoints are covered. The monoculture corner is checked
separately against `1 + kappa(N-1)` at `N` of 2, 3 and 10.

**Scope, stated honestly.** (H1) is the substantive hypothesis. Without it the
state is `(h_1, ..., h_N) in R^{Nd}` and the Jacobian carries a Kronecker
structure, block `(i,j)` equal to `-(beta/gamma) c_ij E_j` with
`c_ij = 1` for `i = j` and `kappa` otherwise, whose spectral radius is not in
general `m_1 * N_eff`. Reducing that object is the fully heterogeneous
block-secular problem already named as deferred in the note, and this file does
not attempt it. [DEFERRED]

## 2. What `R` is

**Lemma 2 (properties of the alignment matrix).** Let `V` be the `N x d^2` matrix
whose rows are the unit vectors `vec E_hat_i`. Then `R = V V'` and:

1. `R` is positive semidefinite, so every `lambda_i(R) >= 0`.
2. `r_ii = 1`, hence `tr R = N`, hence `sum_i lambda_i(R) = N`.
3. `|r_ij| <= 1`, by Cauchy-Schwarz.
4. `1 <= lambda_max(R) <= N`.
5. `lambda_max(R) = 1` iff `R = I`.
6. `lambda_max(R) = N` iff `R = D 1 1' D` for a sign matrix `D = diag(+-1)`, that
   is, iff every response is parallel or antiparallel to one common direction.

*Proof.* (1) and (2) are immediate from `R = V V'` and unit rows. (3) is
Cauchy-Schwarz. For (4), the eigenvalues are nonnegative and sum to `N`, so the
largest is at least the mean `N/N = 1` and at most the total `N`. For (5),
`lambda_max = 1` with nonnegative eigenvalues summing to `N` forces all `N`
eigenvalues to equal 1, so `R = I`. For (6), `lambda_max = N` forces every other
eigenvalue to 0, so `R` has rank one, `R = v v'`; unit diagonal gives
`v_i^2 = 1`, so `v_i = +-1`. [] [VERIFIED, P2]

Item 4 is the one the paper leans on: **`lambda_max(R)` is a genuine effective
count**, bounded below by one firm and above by `N`, with both ends attained.

## 3. Theorem 1

**Theorem 1.** Under Lemma 1, with `kappa in [0,1]`,

```
   spectrum(J)  =  { -m_1 [ (1-kappa) + kappa * lambda_i(R) ] } ,
   rho(J)       =  m_1 * N_eff ,       N_eff = 1 + kappa ( lambda_max(R) - 1 ) ,
```

and the market is stable iff `m_N := m_1 * N_eff < 1`, equivalently iff
`eps < (gamma/beta) / N_eff`.

*Proof.* Write `J = -m_1 B` with `B = (1-kappa)I + kappa R`. `B` is symmetric and
shares its eigenvectors with `R`, with eigenvalues

```
   nu_i  =  (1 - kappa)  +  kappa * lambda_i(R) .
```

So `rho(J) = m_1 * max_i |nu_i|`. Here is the step that needs care. By Lemma 2.1
every `lambda_i(R) >= 0`, and `kappa <= 1` gives `1 - kappa >= 0`, so every
`nu_i >= 1 - kappa >= 0`. The absolute value is therefore inert and the maximum
sits at `lambda_max`, not at `lambda_min`:

```
   rho(J)  =  m_1 [ (1-kappa) + kappa * lambda_max(R) ]
           =  m_1 [ 1 + kappa ( lambda_max(R) - 1 ) ]  =  m_1 * N_eff .
```

Stability of the linearized joint map is `rho(J) < 1`. Substituting
`m_1 = eps*beta/gamma` and solving for `eps` gives the stated form. []
[VERIFIED, P3: 384 random configurations, maximum deviation `4.7e-15`]

**The step that could have gone wrong.** Dropping the absolute value is legitimate
only because `R` is a Gram matrix. A symmetric unit-diagonal matrix with entries
outside `[-1,1]` can put the radius on `lambda_min` instead: at `N = 3` with every
off-diagonal equal to `-3`, the spectrum is `{-5, 4, 4}` and the negative mode
dominates. Cauchy-Schwarz (Lemma 2.3) is what rules this out for a real alignment
matrix. Certified both ways in P3.

**Corollary 1.1 (range).** `N_eff in [1, 1 + kappa(N-1)]`, attained at `R = I` and
`R = 1 1'` respectively.

**Correction to the notation table.** `../00-notation.md` gives the range of
`N_eff` as `[1 - kappa, 1 + kappa(N-1)]`. The lower end is unattainable: it would
need `lambda_max(R) = 0`, impossible for a matrix with `tr R = N > 0`. The correct
lower end is `1`. Recorded here and fixed in the table.

**Corollary 1.2 (interaction never stabilizes).** `rho(J) >= m_1`, with equality
iff `R = I`. A market of adaptive models sharing an environment is never more
stable than one of its members in isolation, and exact neutrality requires fully
orthogonal responses.

This is worth a sentence in the body. It says the externality has a sign: the
coupling can only amplify feedback, never damp it, so there is no configuration in
which crowding does a market a favor. Individual modes can be more damped than
`m_1`, and the differential mode at `m_1(1-kappa)` is one, but the radius is what
governs and the radius cannot fall below `m_1`.

## 4. Which mode binds

Standing assumption A5 says the common mode binds. That is a claim, not a
convention, and Section 5 shows it is false in general.

**Proposition 2 (Perron-Frobenius condition).** If `R` is entrywise nonnegative
and irreducible, then `B = (1-kappa)I + kappa R` is entrywise nonnegative and
irreducible, so by Perron-Frobenius its leading eigenvector is strictly positive
and simple. The binding mode is then a genuine common mode, in which every firm
deviates in the same direction.

Entrywise nonnegativity of `R` is exactly the condition **no firm's feedback
anti-aligns with another's**. Shared vendors and shared pretraining corpora
produce positive alignment, so the realistic regime satisfies it. The paper states
the condition rather than assuming it silently. [VERIFIED, P4]

## 5. The three anchors

**Anchor 1, monoculture.** `R = 1 1'` has rank one with eigenvalue `N` on the
all-ones direction and `0` elsewhere, so `lambda_max = N` and
`N_eff = 1 + kappa(N-1)`. This is the inherited law, whose predicted `2x` and `3x`
at `N = 2, 3` were measured at `1.74x` and `3.16x`. [VERIFIED]

**Anchor 2, orthogonal.** `R = I` gives `lambda_max = 1`, `N_eff = 1`, `m_N = m_1`.
A hundred firms perturbing the environment in a hundred orthogonal directions are
dynamically one firm. [VERIFIED]

**Anchor 3, simplex.** With `r_ij = -1/(N-1)` for `i != j`,

```
   R_simplex  =  (N/(N-1)) I  -  (1/(N-1)) 1 1' .
```

Unit diagonal: `N/(N-1) - 1/(N-1) = 1`. Its spectrum follows from `1 1'` having
eigenvalue `N` on the all-ones direction and `0` on the complement:

```
   on 1:          N/(N-1) - N/(N-1)  =  0
   on 1-perp:     N/(N-1) ,  multiplicity N-1
```

So `lambda_max = N/(N-1)`, `N_eff = 1 + kappa/(N-1)`, and

```
   rho(J)|_simplex  =  m_1 ( 1 + kappa/(N-1) )   ->   m_1   as N grows.
```

The value `m_1(1-kappa)` sits in the spectrum, carried by the all-ones direction
at `lambda = 0`, and it does match the base theory's differential-mode eigenvalue
derived by a different route, so the consistency check the plan of record wanted
is real. It is not the spectral radius. The plan has been corrected and this is
the proof. [VERIFIED, P4, at `N` in {3, 5, 10, 30, 50}]

**The mode swap.** Under the simplex the all-ones direction carries the *smallest*
eigenvalue, so the leading eigenvector is orthogonal to it and A5 fails. This is
consistent with Proposition 2: the simplex has negative entries, so
Perron-Frobenius does not apply. P4 checks all three parts, that the all-ones
direction is annihilated, that the leading eigenvector is orthogonal to it, and
that the entries are negative.

## 6. The mean-alignment index errs, and always in the same direction

The note records two counterexamples. They are instances of a general fact, and
stating the general fact is both shorter and stronger.

**Proposition 3 (the mean is a lower bound).** Let `mbar` be the off-diagonal mean
of `R`. Then

```
   lambda_max(R)  >=  1 + (N-1) * mbar ,
```

hence `N_eff >= N_eff_mean := 1 + kappa (N-1) mbar`, with equality iff `1` is a
leading eigenvector of `R`, that is, iff `R` has constant row sums.

*Proof.* `1' R 1 = N + N(N-1) mbar`, since the diagonal contributes `N`. The
Rayleigh quotient at the all-ones vector gives

```
   lambda_max(R)  >=  (1' R 1)/(1' 1)  =  1 + (N-1) mbar ,
```

with equality iff `1` attains the Rayleigh maximum, that is iff `R 1` is parallel
to `1`. Multiplying by `kappa` and adding `1 - kappa` preserves the inequality. []
[VERIFIED, P5: 360 random `R`, zero violations; equality confirmed on uniform `R`]

**Corollary 3.1 (the error has a sign).** A mean-similarity diversity index never
over-states systemic risk. It under-states it, or is exact. Every error it makes
is in the unsafe direction.

That sentence is the policy-legible form and it is what the body should say. A
regulator using mean similarity is not merely imprecise; it is imprecise in the
direction that lets unstable markets pass.

**Corollary 3.2 (the mean floor).** `1' R 1 = || sum_i vec E_hat_i ||^2 >= 0`
forces `mbar >= -1/(N-1)`, attained iff the unit responses sum to zero, which is
the simplex. [VERIFIED, P5]

**How large the gap gets, with the realistic topology.** The vendor with a
plurality, not the monopoly, is the case to worry about. Take `N = 10` with three
firms fully aligned and every other pair orthogonal, so
`R = blockdiag(1 1' of size 3, I_7)` and `lambda_max = 3`. Three of the
forty-five pairs are aligned, so `mbar = 3/45 = 0.0667` and the mean index reports
`lambda_max = 1.6`. At `kappa = 0.8`:

| | `lambda_max(R)` | `N_eff` | destabilizes at |
|---|---|---|---|
| Clustered, true | `3.00` | `2.60` | `m_1 = 0.385` |
| Uniform, same mean | `1.60` | `1.48` | `m_1 = 0.676` |

A market at `m_1 = 0.5` runs `m_N = 1.30` and is unstable, while the mean index
reports `0.74` and calls it safe with margin. The understatement in `N_eff` is a
factor of `1.757`. [VERIFIED, P6]

**The ordering failure.** Proposition 3 says the mean under-states the level. The
simplex says something worse: it *minimizes* `mbar` at `-1/(N-1)` while carrying
`lambda_max = N/(N-1) > 1`, so it is spectrally worse than orthogonality, which
has the larger mean. The mean does not order configurations correctly, so it fails
as a ranking and not only as a level. Checked at `N` in {5, 10, 30}. [VERIFIED, P5]

**Rule, enforced everywhere in this paper: all stability claims use the spectral
form, never a mean.**

## 7. Heterogeneous moduli

**Proposition 4 (two-sided bound).** With `M = diag(m_i)`, `m_i > 0`, and
`J = -M[(1-kappa)I + kappa R]`,

```
   max_i m_i   <=   rho(J)   <=   ( max_i m_i ) * N_eff .
```

*Proof.* `J` is not symmetric, but the congruence `S = M^{1/2}` gives
`M^{1/2} (M B) M^{-1/2} = M^{1/2} B M^{1/2}`, so `rho(J) = lambda_max(A)` with

```
   A  =  (1 - kappa) M  +  kappa M^{1/2} R M^{1/2} ,
```

symmetric and positive semidefinite.

*Lower.* `e_i' A e_i = (1-kappa) m_i + kappa m_i r_ii = m_i`, since `r_ii = 1`. The
Rayleigh quotient at each `e_i` gives `lambda_max(A) >= m_i` for every `i`.

*Upper.* `R <= lambda_max(R) I` in the Loewner order, and congruence by `M^{1/2}`
preserves it, so `M^{1/2} R M^{1/2} <= lambda_max(R) M`. Hence

```
   A  <=  [ (1-kappa) + kappa lambda_max(R) ] M  =  N_eff * M ,
```

and `lambda_max(A) <= N_eff * lambda_max(M) = N_eff * max_i m_i`. []
[VERIFIED, P8: 300 random draws, no violation]

**Exact in three limits**, each checked:

| Limit | Lower | Upper | Truth |
|---|---|---|---|
| `kappa = 0` | `m_max` | `m_max` | exact, `A = M` |
| `R = I` | `m_max` | `m_max` | exact, `A = M` |
| Equal moduli | `m_1` | `m_1 N_eff` | upper exact |

**The mean-modulus formula is provably false.** At `R = I` the firms decouple and
`rho(J) = max_i m_i`, not the mean. Certified with `m` ranging over
`{0.1, ..., 0.9}`: `rho = 0.900` against a mean of `0.400`. [VERIFIED, P8]

Stated in the paper as a remark with the bound. Tightness is measured in
simulation, not asserted.

## 8. Status

| Result | Statement | Certificate |
|---|---|---|
| Lemma 1 | the reduction `J = -m_1[(1-kappa)I + kappa R]` | P1 |
| Lemma 2 | `R` PSD, unit diagonal, `1 <= lambda_max <= N` | P2 |
| Theorem 1 | `rho(J) = m_1 N_eff`, no absolute-value slack | P3 |
| Cor 1.1 | `N_eff in [1, 1+kappa(N-1)]`, notation table corrected | P2, P3 |
| Cor 1.2 | `rho(J) >= m_1`, interaction never stabilizes | P2 |
| Prop 2 | Perron-Frobenius condition for the common mode | P4 |
| Anchors | monoculture, orthogonal, simplex, and the mode swap | P4 |
| Prop 3 | the mean index is a lower bound, error signed | P5 |
| Cor 3.2 | mean floor `-1/(N-1)`, attained by the simplex | P5 |
| Prop 4 | heterogeneous-modulus two-sided bound | P8 |

Concentration of `R` to the supply-chain limit is a separate argument and lives in
[`02-supply-chain-concentration.md`](02-supply-chain-concentration.md).

## 9. Open items

1. The fully heterogeneous case without (H1), which is the Kronecker object in
   Section 1's scope line. [DEFERRED, journal]
2. Share-weighted alignment for unequal-sized firms. Needs a majorization
   condition on the share vector, since the naive claim that any reweighting
   raises `lambda_max` is false. [DEFERRED, journal]
3. Non-separable spillover `kappa_ij`, which folds into `R` only when it factors.
   [DEFERRED, journal]
