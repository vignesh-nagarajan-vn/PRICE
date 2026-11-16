# D4. Theorem 3: the mixed market, exactly

**Status: complete, and it changes what the paper claims.** Certified in
[`verify_theorem3_herd_immunity.py`](../../ml-contributions/certificates/verify_theorem3_herd_immunity.py),
70 checks, all passing. The note
[`../03-theorem3-herd-immunity.md`](../03-theorem3-herd-immunity.md) is the
summary and predates this file.

Read Section 6 first if you read nothing else. The strong-correction limit does
not err in the direction the plan of record hoped, and what replaces it is a
better result rather than a worse one.

---

## 1. The model

`N` firms share one pool. `N_b` are **blind**, running the ordinary retraining
loop. `N_corr = N - N_b` are **corrected**, running the feedback-aware update
whose dynamics are governed by the objective curvature `gamma_PO` rather than by
the cobweb. Write

```
   theta  =  gamma / gamma_PO  in  (0, 1] ,
```

so `theta = 1` is no correction and `theta -> 0` is the strong-correction limit.

**Hypothesis (M).** Correction scales a firm's modulus: a corrected firm carries
`theta * m_1` where a blind firm carries `m_1`. This is the faithful reading of
the single-firm result, where the corrected loop's modulus is `m_1 gamma/gamma_PO`
because the corrected dynamics are governed by `gamma_PO`. Correction changes a
firm's *gain*, not its response *direction*, so the alignment matrix is untouched.

Take the supply-chain alignment `R = (1-s)I + s 1 1'`. Then

```
   B  =  (1-kappa) I + kappa R  =  (1 - ks) I  +  ks * 1 1' ,      ks := kappa*s ,
```

and by Proposition 4 of [`01`](01-alignment-spectrum.md) the radius of
`J = -M B` is `lambda_max(A)` for the symmetric congruence
`A = M^{1/2} B M^{1/2}`, with `M = diag(m_i)`.

## 2. Diagonal plus rank one

Substituting `B`,

```
   A  =  (1 - ks) M  +  ks * w w' ,        w = M^{1/2} 1 ,   w_i = sqrt(m_i) .
```

`A` is a diagonal matrix plus a positive-weight rank-one term, so its eigenvalues
not equal to a diagonal entry solve the secular equation

```
   1  +  ks * sum_i  m_i / ( (1-ks) m_i  -  lambda )  =  0 .
```

With only two distinct moduli the sum collapses to two terms, and the secular
equation clears to a quadratic. This is why the mixed market has a closed form at
all, and why three or more correction levels would not.

## 3. The two-block quadratic

Write `a = (1-ks) m_1` and `b = (1-ks) theta m_1` for the two diagonal values.
Clearing denominators in the secular equation gives

```
   (a - lambda)(b - lambda)  +  ks N_b m_1 (b - lambda)
                             +  ks N_corr theta m_1 (a - lambda)  =  0 ,
```

that is `lambda^2 - P lambda + Q = 0` with

```
   P  =  a + b + ks * m_1 * ( N_b + theta * N_corr )
   Q  =  theta * m_1^2 * (1 - ks) * ( 1 + ks (N - 1) )
      =  theta * m_1^2 * (1 - ks) * N_eff .
```

**Theorem 3 (exact).** *For `1 <= N_b <= N-1`,*

```
   rho(J)  =  ( P + sqrt( P^2 - 4Q ) ) / 2 ,
```

*and the remaining spectrum is `a` with multiplicity `N_b - 1` and `b` with
multiplicity `N_corr - 1`.*

*Proof.* The two secular roots are the quadratic's roots; the eigenvectors
constant within each block and orthogonal to `w` supply the rest. Because the
rank-one weight `ks` is positive, the eigenvalues of `A` interlace those of
`(1-ks)M`, so the largest eigenvalue of `A` exceeds every diagonal entry and is
therefore the larger secular root rather than a degenerate one. []

The appearance of `N_eff` inside `Q` is not cosmetic: the mixed market inherits
Theorem 1's crowding through the product term, which is why every statement below
carries `s`.

[VERIFIED, H1: maximum error `2.5e-14` against dense eigensolves over 6000 random
draws]

## 4. The degenerate blocks, which are a real trap

When `N_b = 0` or `N_b = N` one block is empty, but the quadratic still carries
that block's factor and leaves a **phantom root** behind. At `N_b = 0` the naive
quadratic returns `(1-ks) m_1`, a value no firm's modulus supports, and at small
`theta` that phantom exceeds the true radius: `0.132` against a true `0.043` at
`N = 12`, `m_1 = 0.3`, `kappa = 0.8`, `s = 0.7`, `theta = 0.02`. The correct
values are the single-block ones,

```
   N_b = N     ->  rho = m_1 * N_eff ,
   N_b = 0     ->  rho = theta * m_1 * N_eff .
```

Any implementation must branch on this. [VERIFIED, H2]

## 5. The two limits, both now corollaries

**`theta = 1`, no correction.** `P = m_1[2(1-ks) + ks N]` and
`Q = m_1^2 (1-ks) N_eff`, whose roots are `m_1 N_eff` and `m_1(1-ks)`. Theorem 1
is recovered exactly. [VERIFIED, H3]

**`theta -> 0`, strong correction.** `Q -> 0`, so one root goes to zero and the
other to `P -> m_1[(1-ks) + ks N_b]`, that is

```
   rho(J)  ->  m_1 ( 1 + kappa*s*(N_b - 1) ) ,
```

**the blind-block condition.** The note derives this by arguing that corrected
firms transmit no feedback and drop out of the cycle. That argument is right, and
now it is also a corollary of the exact root rather than a separate claim.
[VERIFIED, H3, C13]

## 6. C18: the limit errs, and it errs optimistic

The plan of record asks for confirmation that the strong-correction limit is
approached from the stable side, so that the limit theorem is conservative. **It
is not.**

**Proposition 11 (monotonicity).** `rho(J)` is nondecreasing in `theta`.

*Proof.* `A_ij = sqrt(m_i m_j) B_ij` and `B` is entrywise nonnegative for
`ks in [0,1]`, so `A` is entrywise nonnegative. Every `m_i` is nondecreasing in
`theta`, constant for blind firms and `theta m_1` for corrected ones, so every
entry of `A` is nondecreasing in `theta`. `A` is symmetric and nonnegative, so by
Perron-Frobenius its Rayleigh maximizer may be taken in the nonnegative orthant;
for such an `x`, `x' A(theta) x` is nondecreasing in `theta`. Taking `x` to be
the maximizer at `theta_1 < theta_2`,

```
   lambda_max(A(theta_2))  >=  x' A(theta_2) x  >=  x' A(theta_1) x
                           =   lambda_max(A(theta_1)) .   []
```

[VERIFIED, C18: zero violations on 3000 random configurations, each swept over 50
values of `theta`]

**Two readings, and they point opposite ways.**

The good one. Correction never backfires. More correction is always weakly
stabilizing, so there is no perverse configuration in which un-blinding a firm
destabilizes the market. That is worth one sentence in the body, because a
reviewer will wonder.

The uncomfortable one. `rho(theta) >= rho(0)`, so the limit **under-states** the
radius. The limit theorem is **optimistic**: it can call a market stable that is
unstable at any finite correction strength. On uniform random draws with `theta`
in `[0.01, 1]`, the limit calls `11.8%` of configurations stable that are actually
unstable. Worked cases, all of which the limit reads as comfortably stable:

| Configuration | limit reads | truly unstable unless |
|---|---|---|
| `N = 10`, `N_b = 6`, `m_1 = 0.15`, `kappa = 0.8`, `s = 1` | `0.750` | `gamma_PO > 1.9 gamma` |
| `N = 30`, `N_b = 8`, `m_1 = 0.10`, `kappa = 0.9`, `s = 0.8` | `0.604` | `gamma_PO > 3.9 gamma` |
| `N = 20`, `N_b = 10`, `m_1 = 0.12`, `kappa = 0.8`, `s = 1` | `0.984` | `gamma_PO > 58.6 gamma` |

**Consequence for the build.** The exact two-block root is fourth in the de-scope
order. It must not be: shipping the limit alone would state a stability criterion
that errs in the unsafe direction without saying so. The plan of record is
corrected accordingly. [VERIFIED, C18]

## 7. What replaces the clean law, and it is better

The limit's optimism has an exact repair, and the repair deepens the
epidemiological correspondence instead of straining it.

**Theorem 3' (imperfect correction).** *At `kappa = s = 1` the quadratic
degenerates, since `(1-ks) = 0` kills `a`, `b` and `Q`, leaving
`rho = P = m_1 (N_b + theta N_corr)`. Solving `rho < 1` for the corrected
fraction gives*

```
   rho*(theta)  =  ( 1 - 1/m_N ) / ( 1 - theta ) .
```

[VERIFIED, H5: agreement to `1.8e-15` over 120 configurations, and the radius form
checked against dense eigensolves]

Write the **correction efficacy** `e = 1 - theta = 1 - gamma/gamma_PO`. Then

```
   required corrected fraction  =  ( 1 - 1/m_N ) / e ,
```

which is exactly the standard epidemiological coverage requirement for an
**imperfect vaccine**. The clean law `1 - 1/m_N` is its perfect-efficacy corner.
The correspondence the paper claims therefore survives the correction and gets
stronger: it now transfers not only the threshold but the standard refinement of
the threshold, which is the sort of thing a structural analogy predicts and a
decorative one does not.

**Corollary 11.1 (critical correction efficacy).** The required fraction exceeds
one, so no corrected fraction stabilizes the market, exactly when
`theta > 1/m_N`. Equivalently, correction is a usable lever only if

```
   gamma_PO / gamma  >  m_N .
```

At `m_N = 2.5` the corrected update must deliver at least a `2.5x` curvature
improvement or the market cannot be stabilized by un-blinding at all, whatever
fraction is treated. [VERIFIED, H6]

This is the exact structural parallel of Theorem 2's critical crowding level. Each
lever has a regime past which it stops working, and stating both is what makes the
substitution frontier of Section 7 an honest object rather than an extrapolation.

Away from `kappa = s = 1` the closed form is no longer exact, and the exact
threshold comes from setting the quadratic's larger root to one. The imperfect
correction law remains accurate to well under one firm's granularity at the
parameters the paper uses, which is stated rather than hidden.

**Measured evidence that it generalizes further than it is proved to.** Panel 4,
run at `N = 20`, `m_1 = 0.15`, `kappa = 0.8`, `s = 1`, where the law is *not*
exact, measured thresholds of `12`, `14`, `16` and `20` firms at efficacies
`1.00`, `0.90`, `0.75` and `0.60`. The law predicts `12`, `14`, `16` and `20`:
four out of four, at the integer granularity that is what a market actually
faces. This is measured in the linearized reference environment and is recorded
as evidence, not as a proof. The exact statement away from `kappa = s = 1`
remains the quadratic's root. [DRY RUN, panel 4]

The flag is `[DRY RUN]` and not `[MEASURED]` on purpose. Panel 4 runs in the
linearized reference environment, which has no informed flow, no spread and no
inventory, so it establishes that the closed form governs the realized dynamics
and nothing about a market. The claims ledger is the enforcement point and
carries E4 and E4.1 at `[DRY RUN]`; this note now matches it.

## 8. The threshold, and which form is exact

**Proposition 12.** The strong-correction limit is stable if and only if

```
   N_b  <  N_c(s)  =  1 + (1/m_1 - 1)/(kappa*s) .
```

*Proof.* Rearrange `m_1(1 + kappa s (N_b - 1)) < 1`. [] [VERIFIED, C14: zero
mismatches on 4000 draws]

**The clamped form is not an exact restatement, and the note states it as if it
were.** Writing `rho = 1 - N_b/N` and `rho* = max(0, 1 - N_c(s)/N)`, the criterion
`rho > rho*` fails on `134` of the same 4000 draws. Every failure is the same
corner: `N_b = N` with `N_c(s) >= N`, the all-blind market that is stable because
it needs no correction at all. The clamp at zero combined with a strict inequality
excludes it.

Fixes, in order of preference: state `N_b < N_c(s)` as the theorem, since it is
primitive and exact; or use the unclamped `rho > 1 - N_c(s)/N`, also exact; or keep
the clamped `rho*` as the *policy object*, read as "the fraction that must be
corrected", with the understanding that `rho* = 0` means no requirement rather
than a strict inequality to clear. The paper does the first and presents the third.
[VERIFIED, C14]

## 9. The realized threshold is a whole number of firms

`rho* N` is generally not an integer, and the experiment runs at `N` in the tens
where one firm is several percentage points. The largest stable blind count is
`ceil(N_c) - 1`, so

```
   minimum corrected firms  =  N - ceil( N_c(s) ) + 1 ,
```

clamped to `[0, N]`. [VERIFIED, H4: exact on 3000 draws]

The note suggests `ceil(rho* N)`. That agrees on every random draw, because random
draws never land on an exact integer `N_c`, but it is off by one exactly when
`N_c` is an integer: at `N = 20`, `m_1 = 0.15`, `kappa = 0.8` and the `s` giving
`N_c = 8`, the truth is `13` corrected firms and `ceil(rho* N)` says `12`. Use the
formula. [VERIFIED, H4]

Worked at `N = 20`, `m_1 = 0.15`, `kappa = 0.8`:

| `s` | `N_c(s)` | `rho*` | minimum corrected firms |
|---|---|---|---|
| `1.0` | `8.08` | `0.596` | `12` |
| `0.5` | `15.17` | `0.242` | `5` |
| `0.2` | `36.42` | `0` | `0` |

[VERIFIED, C17]

## 10. The collapse and the substitution result

At `kappa = s = 1`, `N_c = 1/m_1` and `N_eff = N`, so

```
   rho*  =  1 - N_c/N  =  1 - 1/(m_1 N)  =  1 - 1/m_N ,
```

the epidemiological herd-immunity threshold with the systemic modulus as the
reproduction number. A market of 10 firms at `m_N = 2.5` needs 60% un-blinded.
[VERIFIED, C15, on a grid of `N` and `m_1` including the vacuous branch]

`rho*` is increasing in `s`, strictly so wherever it is positive, which is what
makes model diversity and corrected learning substitutes and what the `(rho, s)`
frontier plots. [VERIFIED, C16]

## 11. Status

| Result | Statement | Certificate |
|---|---|---|
| Theorem 3 | exact radius from the two-block quadratic | H1, `2.5e-14` |
| Degenerate blocks | empty blocks need the single-block form | H2 |
| Limits | `theta = 1` gives Theorem 1; `theta -> 0` gives the blind block | H3, C13 |
| Prop 11 | `rho` nondecreasing in `theta`, so correction never backfires | C18 |
| **C18 finding** | **the limit is optimistic, not conservative** | C18, `11.8%` verdict flips |
| Theorem 3' | `rho*(theta) = (1 - 1/m_N)/(1 - theta)`, the imperfect-vaccine law | H5, `1.8e-15` |
| Cor 11.1 | critical efficacy: `gamma_PO/gamma > m_N` or no fraction works | H6 |
| Prop 12 | `N_b < N_c(s)` exact; the clamped `rho > rho*` is not | C14 |
| Integer form | `N - ceil(N_c) + 1` corrected firms | H4 |
| Collapse | `rho* = 1 - 1/m_N` at `kappa = s = 1` | C15 |
| Monotone in `s` | the substitution result | C16 |

## 12. Open items

1. The exact threshold away from `kappa = s = 1` has no clean closed form; it is
   the root of the quadratic set to one. The paper reports the imperfect-correction
   law as exact at `kappa = s = 1` and accurate elsewhere, with the deviation
   measured. [DERIVED]
2. Hypothesis (M) treats correction as a pure gain reduction. A corrected firm
   that also *changes its response direction* would move `R`, which this
   derivation does not model. Worth one sentence of scope in the body.
   [DEFERRED]
3. Three or more correction levels break the two-block collapse and return a
   genuine secular equation rather than a quadratic. Journal material.
   [DEFERRED]
