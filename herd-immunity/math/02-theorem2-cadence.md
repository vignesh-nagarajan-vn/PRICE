# Theorem 2: the crowding-cadence frontier

The base theory contains, separately, the `N_eff` amplification law and a
single-dealer lazy-deployment result. Nobody has composed them.

**Complete proof:** [`derivations/03-cadence-composition.md`](derivations/03-cadence-composition.md),
certified by
[`verify_theorem2_cadence.py`](../ml-contributions/certificates/verify_theorem2_cadence.py),
59 checks. This note stays the summary.

## Inherited pieces

**Lazy deployment, single dealer.** A dealer taking only `K` gradient steps per
deployment instead of retraining to convergence realizes outer-map slope

```
   mu(K)  =  -m  +  c^K (1 + m) ,        c  =  1 - eta*gamma  in (0,1) .
```

`c` is the inner per-step contraction and is own-objective curvature, so it does
not depend on `N`. [VERIFIED, base result]

## Statement

**Theorem 2.** In the `N`-firm market with synchronous `K`-step retraining, the
composition applies mode by mode and the common mode's outer slope is `-m_N`, so

```
   mu_N(K)  =  -m_N  +  c^K (1 + m_N) .
```

A market that is unstable under full retraining (`m_N > 1`) is stable under lazy
retraining iff `|mu_N(K)| < 1`, which reduces to

```
   K  <  K_max  =  ln( (m_N - 1)/(m_N + 1) ) / ln c ,
```

and `K_max` is decreasing in `m_N`. [DERIVED]

## Derivation

Both sides of `|mu_N(K)| < 1`, taken separately.

*Upper side.* `mu_N(K) < 1` requires `c^K (1 + m_N) < 1 + m_N`, which holds for
every `K >= 1` because `c < 1`. Never binds.

*Lower side.* `mu_N(K) > -1` requires

```
   c^K (1 + m_N)  >  m_N - 1
   c^K            >  (m_N - 1)/(m_N + 1)
   K ln c         >  ln( (m_N - 1)/(m_N + 1) )
```

and `ln c < 0` flips the inequality, giving `K < K_max` as stated. When
`m_N <= 1` the right-hand side is non-positive and the constraint is vacuous,
which is the correct behavior: a market stable under full retraining is stable
at every cadence.

*Why the common mode binds.* Differential modes have `|slope| = m_1(1-kappa)`,
which is below one whenever `m_1 < 1`. Subject to the Perron-Frobenius condition
recorded in `01`. [DERIVED]

## Critical crowding

`K_max > 1` is required for any cadence to be feasible, since `K` is a positive
integer. That gives

```
   c  >  (m_N - 1)/(m_N + 1)
   c(m_N + 1)  >  m_N - 1
   c + 1       >  m_N (1 - c)
   m_N         <  (1 + c)/(1 - c) .
```

Past that level of effective crowding, even the laziest retrainer is unstable
and the market is unstable at every retraining frequency. Equivalently,
**minimum-cadence operation multiplies the sustainable effective crowding by
exactly `(1+c)/(1-c)`**, a factor of `9` at `c = 0.8`. [DERIVED]

## The supply-chain reading

Substituting Result 1, `K_max` is a function of `s`, not just of `N`. Holding
the number of firms fixed and raising the shared-model fraction shrinks every
incumbent's retraining budget.

Worked at `m_1 = 0.15`, `kappa = 0.8`, `N = 30`, `c = 0.8`, so
`N_eff = 1 + 23.2 s`:

| `s` | `N_eff` | `m_N` | `K_max` |
|---|---|---|---|
| `0.25` | `6.80` | `1.020` | `20.68` |
| `0.50` | `12.60` | `1.890` | `5.28` |
| `1.00` | `24.20` | `3.630` | `2.53` |

All three recomputed by hand and matching the plan of record's `~20.7`, `~5.3`
and `~2.5`. The plan does not state `c`; these figures pin it at `c = 0.8`,
which is also the value the critical-crowding factor of `9` assumes. Record
`c = 0.8` as the paper's worked example and state it explicitly, because a
reader cannot reproduce the table without it. [VERIFIED by recomputation]

The externality in its sharpest operational form is therefore not merely that
**your competitor's entry consumes your retraining budget** but that **your
competitor's choice of vendor does too**, without their entering at all and
without either firm doing anything wrong. That sentence is the paper's best
one-line statement of the market failure, and it exists only because the two
predecessor drafts were merged.

## The tradeoff this lever buys with

Cadence buys stability with model staleness. Quantify it rather than presenting
it as free: at cadence `K` the deployed model lags the current best response by
a factor `c^K`, so the same `c^K` that delivers stability is the staleness. The
paper states this as the lever's price, in one sentence, in Section 5.

## Figure

The `(N_eff, K)` plane: measured joint-loop stability, converge or diverge per
cell on common-random-number seeds, against the predicted frontier, with `s`
contours overlaid and the critical-crowding column where the window closes. One
panel, fully falsifiable.

## What the proof added

**The binding-mode argument is simpler than this note's.** `mu_i(K)` is strictly
decreasing in `nu_i`, so the extreme mode sits at `lambda_max` for any sign pattern
of `R`, and the upper side of `|mu_N| < 1` never binds for any `K >= 1`. No claim
about the size of the differential modes is needed, and neither is the
Perron-Frobenius condition Theorem 1 carries. `derivations/03`, Proposition 9.

**Critical crowding is not a separate result.** The frontier in the form
`m_N < (1 + c^K)/(1 - c^K)` makes it the `K = 1` instance, since `K` is a positive
integer. One derivation instead of two.

**The boundary `m_N = 1`.** Lazy retraining strictly stabilizes the marginal market
at every finite `K`, with margin `2c^K`. Worth the one line it costs.

## Open items

1. ~~Confirm the lazy-deployment lemma's linearization at the frozen best response
   is unaffected by `N`.~~ **Done.** C12 measures the realized inner contraction
   inside the joint market across 45 configurations, spread `4.4e-16`. This was
   the one place the composition could fail.
2. `K` is an integer, so `K_max` is a real-valued frontier and the realized
   window is `floor(K_max)`. State that in the paper; the figure's cells are
   integer `K` and the frontier is drawn continuous. Verified in Q4.
3. Asynchronous cadences are out of scope under A3 and named as an extension.
   Heterogeneous `K_i` across firms breaks the eigenvector sharing the proof
   uses, so it is a genuine extension rather than bookkeeping. [DEFERRED]
