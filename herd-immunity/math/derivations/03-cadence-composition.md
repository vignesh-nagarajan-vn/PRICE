# D3. Theorem 2: the cadence composition

**Status: complete.** Every statement below is proved here and certified in
[`verify_theorem2_cadence.py`](../../ml-contributions/certificates/verify_theorem2_cadence.py),
59 checks, all passing. The note
[`../02-theorem2-cadence.md`](../02-theorem2-cadence.md) is the summary; this file
is the proof.

What this file adds over the note: the lazy-deployment slope is derived from
gradient descent rather than inherited as a formula (Section 1), the composition
is carried out mode by mode with its one hypothesis isolated and certified
(Sections 3 and 4), and the argument for which mode binds is replaced by a
monotonicity argument that is both shorter and unconditional (Section 5). Critical
crowding turns out not to be a separate result but the `K = 1` instance of the
frontier (Section 7).

---

## 1. The inner loop

**Lemma 7 (inner contraction).** Let firm `i` retrain by gradient descent on a
`gamma`-strongly-convex quadratic own objective whose minimizer is the frozen best
response `b`, with step size `eta`. Then `K` steps from `z_0` land at

```
   z_K  =  b  +  c^K ( z_0 - b ) ,        c  =  1 - eta*gamma .
```

*Proof.* The gradient is `gamma (z - b)`, so the update is
`z <- z - eta*gamma*(z - b) = b + (1 - eta*gamma)(z - b)`. Induct on `K`. []

`c in (0,1)` requires `0 < eta < 2/gamma`, and `eta <= 1/gamma` gives `c in [0,1)`.
[VERIFIED, Q1, exact to `1e-12` at three `(eta, gamma)` pairs and `K` in
{1, 3, 7, 20}]

The certificate runs actual gradient descent and measures the realized gap ratio.
`c` is never written into the loop; it is whatever the loop does.

## 2. The single-firm slope

**Lemma 8 (lazy deployment).** For a single firm whose full-retraining best
response has slope `-m`, the `K`-step outer map has slope

```
   mu(K)  =  -m  +  c^K (1 + m) .
```

*Proof.* The frozen best response at the current deployment `h_t` is `b = -m h_t`.
By Lemma 7,

```
   h_{t+1}  =  b + c^K (h_t - b)
            =  -m h_t + c^K ( h_t + m h_t )
            =  h_t [ -m + c^K (1 + m) ] .   []
```

Sanity at the ends: `K -> infinity` gives `-m`, the full-retraining slope, and
`K = 0` gives `1`, the identity map, since a firm that takes no gradient steps does
not move. This recovers the inherited single-dealer lemma, so the base result is
reproduced rather than assumed.

## 3. The composition, and its one hypothesis

**Hypothesis (C). `c` is the same scalar in the joint market as in the single-firm
market.** It is built from own-objective curvature `gamma` and the inner step size
`eta`, neither of which involves `N`, `kappa`, or `R`. Competitors change *where*
firm `i` is heading, through the frozen best response, and not *how fast* it gets
there.

This is the only place the composition can fail, so it is certified rather than
argued. C12 measures the realized one-step contraction inside the joint market
across 45 configurations spanning `N` in {1, 2, 5, 12, 30}, `kappa` in {0, 0.5, 1}
and `m_1` in {0.05, 0.15, 0.6}, with random `R` at each. Spread across all of them:
`4.4e-16`. [VERIFIED, C12]

**Theorem 2 (joint lazy map).** Under (C) and synchronous `K`-step retraining
(standing assumption A3), the joint deployment map is linear with matrix

```
   M_K  =  c^K I  +  ( 1 - c^K ) J ,
```

whose eigenvalues, sharing eigenvectors with `J`, are

```
   mu_i(K)  =  c^K  -  ( 1 - c^K ) m_1 nu_i ,      nu_i = (1-kappa) + kappa lambda_i(R) .
```

On the mode carrying `lambda_max(R)`, where `m_1 nu_max = m_N`,

```
   mu_N(K)  =  c^K - (1 - c^K) m_N  =  -m_N  +  c^K ( 1 + m_N ) .
```

*Proof.* All firms compute their frozen best responses from the common current
state `x`, giving `b = J x`, then each takes `K` inner steps. By Lemma 7 applied
coordinatewise, and using (C) so that the same `c` applies in every coordinate,

```
   x_{t+1}  =  J x_t  +  c^K ( x_t - J x_t )  =  [ c^K I + (1-c^K) J ] x_t .
```

`M_K` is an affine function of `J`, so it has the same eigenvectors, with
eigenvalues `c^K + (1-c^K) * (-m_1 nu_i)`. Substituting
`m_1 nu_max = m_1 N_eff = m_N` from Theorem 1 gives the last line, and rearranging
recovers the form the plan of record states. [] [VERIFIED, Q2 and Q3]

Q2 builds the joint map by running the actual inner gradient descent on each basis
vector and comparing to `c^K I + (1-c^K)J`, at 32 combinations of
`(N, kappa, m_1, K)`, agreeing below `1e-12`.

## 4. Why this is a composition and not a new mechanism

Both ingredients are published. The amplification law supplies `J`, and the
lazy-deployment slope supplies the inner contraction. Nobody has composed them,
because the single-learner literature does not carry `N` and the multiplayer
literature does not model retraining frequency at all. The algebra is an
afternoon's work and the paper should say so plainly rather than dressing it up.
The content is the frontier in Section 6 and the critical crowding level in
Section 7, neither of which exists anywhere.

## 5. Which mode binds

The note argues that the common mode binds because differential modes have
`|slope| = m_1(1-kappa) < 1`. That argument is correct but unnecessary, and it
carries a condition it does not need.

**Proposition 9 (the extreme mode is automatic).** `mu_i(K)` is strictly
decreasing in `nu_i`, since `(1 - c^K) m_1 > 0` for every `K >= 1`. Therefore:

1. **The upper side never binds.** Every `nu_i >= 0` by Lemma 2.1 and
   `kappa <= 1`, so `mu_i(K) <= c^K < 1` for all `i` and all `K >= 1`, whatever
   `R` is.
2. **The lower side binds at `lambda_max`.** `min_i mu_i(K)` is attained at
   `nu_max`, so the stability constraint is exactly `mu_N(K) > -1`.

*Proof.* Immediate from monotonicity in `nu_i` and `nu_i >= 0`. []
[VERIFIED, Q3, at 54 combinations across `N` in {4, 10, 25}]

This is better than the note's route in two ways. It does not need a separate claim
about the size of the differential modes, and it does not need the
Perron-Frobenius condition from D1, because monotonicity places the extreme at
`lambda_max` regardless of the sign pattern of `R`. Under lazy retraining the
binding mode is the `lambda_max` mode, full stop.

## 6. The frontier, in two equivalent forms

**Theorem 10 (cadence window).** Under Theorem 2, the market is stable iff

```
   m_N  <  g(K) := ( 1 + c^K ) / ( 1 - c^K ) ,
```

equivalently iff

```
   K  <  K_max  =  ln( (m_N - 1)/(m_N + 1) ) / ln c        for m_N > 1 ,
```

with `K_max = +infinity` when `m_N <= 1`.

*Proof.* By Proposition 9 the only constraint is `mu_N(K) > -1`:

```
   c^K - (1 - c^K) m_N  >  -1
   (1 - c^K) m_N        <  1 + c^K
   m_N                  <  (1 + c^K)/(1 - c^K) ,
```

which is the first form. Rearranging the same inequality the other way,

```
   c^K   >  (m_N - 1)/(m_N + 1)
   K ln c  >  ln( (m_N - 1)/(m_N + 1) ) ,
```

and `ln c < 0` flips the inequality on division, giving `K < K_max`. When
`m_N <= 1` the right-hand side of the `c^K` inequality is non-positive while
`c^K > 0`, so the constraint is vacuous and every cadence is stable. [] [VERIFIED,
C8: 51600 integer cases, zero mismatches; Q4: both forms agree]

**Which form to lead with.** The plan of record uses `K_max`, and the paper keeps
it, because "how many gradient steps may I take" is the operator's question. The
`g(K)` form is worth one line in the body because it makes Section 7 a corollary
instead of a second derivation.

**Corollary 10.1 (monotone in crowding).** `K_max` is strictly decreasing in
`m_N`: with `f(m) = ln((m-1)/(m+1))`,

```
   f'(m)  =  1/(m-1) - 1/(m+1)  =  2/(m^2 - 1)  >  0   for m > 1 ,
```

and dividing by `ln c < 0` flips the sign. [VERIFIED, C9, on 400-point grids at
`c` in {0.5, 0.8, 0.95}]

**Corollary 10.2 (integer windows).** `K` is a positive integer, so the realized
window is `floor(K_max)` while the plotted frontier is continuous. The figure
caption says so. [VERIFIED, Q4: `floor(K_max)` is the largest stable integer and
`floor(K_max) + 1` is unstable, at five `(c, m_N)` pairs]

## 7. Critical crowding is the `K = 1` case

**Corollary 10.3.** A feasible cadence exists iff `K_max > 1`, which by Theorem 10
is exactly `m_N < g(1) = (1 + c)/(1 - c)`. Past that level of effective crowding
the market is unstable at every retraining frequency, and minimum-cadence
operation multiplies the sustainable effective crowding by exactly `(1+c)/(1-c)`,
a factor of `9` at `c = 0.8`.

The note derives this separately. It is not separate: it is `g` evaluated at the
smallest admissible `K`. Presenting it as a corollary saves a derivation in the
body and makes the structure clearer, since `g` decreasing in `K` is what says the
laziest retrainer is the hardest to destabilize. [VERIFIED, C10: sharp at five values of `c`,
with no stable `K` up to 500 past the threshold and `K = 1` stable just below it]

## 8. The supply-chain reading

Substituting Theorem 1, `m_N = m_1(1 + kappa*s*(N-1))` and `K_max` becomes a
function of `s` at fixed firm count. Since `m_N` is increasing in `s` and `K_max`
is decreasing in `m_N`, the window shrinks as vendor concentration rises with no
entry at all. [VERIFIED, C9, monotone in `s` on a 100-point grid]

Worked at `m_1 = 0.15`, `kappa = 0.8`, `N = 30`, `c = 0.8`, so `N_eff = 1 + 23.2 s`:

| `s` | `N_eff` | `m_N` | `K_max` |
|---|---|---|---|
| `0.25` | `6.80` | `1.020` | `20.68` |
| `0.50` | `12.60` | `1.890` | `5.28` |
| `1.00` | `24.20` | `3.630` | `2.53` |

All three reproduce the plan of record's `~20.7`, `~5.3` and `~2.5`. The plan does
not state `c`; these figures pin it at `c = 0.8`, which is also the value the
factor of 9 assumes. **State `c = 0.8` wherever the table appears**, because a
reader cannot reproduce it otherwise. All three `m_N` values sit below the critical
crowding level of 9, so a window exists in every column, which is why the table is
a table of finite numbers. [VERIFIED, C11]

The operational statement the section exists for: the externality is not merely
that **your competitor's entry consumes your retraining budget** but that **your
competitor's choice of vendor does too**, without their entering at all and
without either firm doing anything wrong.

## 9. What the lever costs

By Lemma 7 the deployed model's gap to the frozen best response after a round is
exactly `c^K` times the gap before it. So `c^K` is simultaneously the quantity that
buys stability, through `g(K)` increasing in `c^K`, and the staleness of the
deployed model. The lever is not free and the paper quantifies its price in the
same parameter that delivers its benefit, in one sentence, rather than leaving a
reviewer to notice.

## 10. The boundary `m_N = 1`

Worth one line because the certificate found it. At `m_N = 1` exactly,
`mu_N(K) = -1 + 2c^K`, which lies strictly inside `(-1, 1)` for every finite `K`,
so lazy retraining strictly stabilizes the marginally-unstable market. The margin
`2c^K` decays geometrically, falling below double precision past `K = 171` at
`c = 0.8`, at which point the check goes numerically marginal. That is a
floating-point limit and not a statement about the market, and it is recorded in
the certificate so nobody later reads it as one. [VERIFIED, C8]

## 11. Status

| Result | Statement | Certificate |
|---|---|---|
| Lemma 7 | inner loop contracts by `c^K`, `c = 1 - eta*gamma` | Q1 |
| Lemma 8 | single-firm slope `mu(K) = -m + c^K(1+m)` | Q1, Q2 |
| Hyp (C) | `c` invariant to `N`, `kappa`, `R` | **C12** |
| Theorem 2 | `M_K = c^K I + (1-c^K)J`, `mu_N(K) = -m_N + c^K(1+m_N)` | Q2, Q3 |
| Prop 9 | upper side never binds; lower binds at `lambda_max` | Q3 |
| Theorem 10 | `m_N < (1+c^K)/(1-c^K)`, equivalently `K < K_max` | C8, Q4 |
| Cor 10.1 | `K_max` decreasing in `m_N` and in `s` | C9 |
| Cor 10.2 | realized window is `floor(K_max)` | Q4 |
| Cor 10.3 | critical crowding `(1+c)/(1-c)`, the `K = 1` case | C10 |
| Table | `20.68 / 5.28 / 2.53` at `s = 0.25 / 0.5 / 1` | C11 |
| Dynamics | iterating the real joint map matches the frontier | Q5 |

Q5 is the check that would catch a frontier that is algebraically right and
dynamically wrong: 59 decisive trials at random `(N, kappa, s, m_1, K)`, iterating
the actual joint map to convergence or divergence, zero disagreements with the
predicted side of the frontier.

## 12. Open items

1. Asynchronous cadences, where firms retrain on different clocks, are out of
   scope under A3 and named as an extension. The composition in Section 3 uses
   synchrony when it computes every firm's frozen best response from the same
   state. [DEFERRED]
2. Heterogeneous `K_i` across firms. The joint map stops being an affine function
   of `J` and the eigenvector sharing in Theorem 2 fails, so this is a genuine
   extension rather than bookkeeping. [DEFERRED]
3. The inner loop is linearized at the frozen best response. The simulator is the
   nonlinear check, and the scope boundary is reported rather than hidden, per
   standing assumption A1.
