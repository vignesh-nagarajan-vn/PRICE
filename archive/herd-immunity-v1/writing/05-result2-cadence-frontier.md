# 5. Result 2: the crowding-cadence frontier

**Status: drafted.** Target 1.00 page. Source:
[`../math/derivations/03-cadence-composition.md`](../math/derivations/03-cadence-composition.md).
Certificates in `../ml-contributions/certificates/verify_theorem2_cadence.py`.

---

The first lever is quantity regulation, and it is the one a firm can pull by
itself: move less per round. How much less is a closed form, and it depends on the
market's effective crowding rather than on the firm's own modulus.

**The inherited piece.** A learner that takes only `K` gradient steps per
deployment, rather than retraining to convergence, realizes outer-map slope
`mu(K) = -m + c^K(1+m)`, where `c = 1 - eta*gamma` is the inner per-step
contraction (Mendler-Duenner et al., 2020; REFLEX for the structural version).
`c` is built from the learner's own objective curvature and its step size, so it
does not depend on how many competitors it has. That independence is the entire
reason the composition below works, and it is the one claim in this section
verified by simulation rather than by algebra. [VERIFIED]

**Theorem 2.** *In the `N`-firm market with synchronous `K`-step retraining, the
joint deployment map is `c^K I + (1-c^K) J`, so the binding mode has slope*

```
   mu_N(K)  =  -m_N  +  c^K ( 1 + m_N ) ,
```

*and the market is stable if and only if*

```
   K  <  K_max  =  ln( (m_N - 1)/(m_N + 1) ) / ln c ,
```

*with `K_max` infinite when `m_N <= 1` and strictly decreasing in `m_N`.*
[VERIFIED]

The binding mode sits at `lambda_max` whatever the sign pattern of `R`, so this
section needs no analogue of Section 4's Perron-Frobenius condition.

<!-- APPENDIX, page-budget step 1, 19 Aug 2026. The three-line proof below moves
     out of the body. The body keeps the no-Perron-Frobenius sentence above,
     which is what a reader needs to know here.

The proof is three lines. All firms compute their frozen best responses from the
same state and then take `K` inner steps, so the joint map is an affine function
of `J` and shares its eigenvectors, with slopes `c^K - (1-c^K) m_1 nu_i` on the
mode carrying `lambda_i(R)`. That expression is strictly decreasing in `nu_i`,
which does two things at once: it puts every slope at or below `c^K < 1`, so the
upper side of the stability constraint never binds at any cadence, and it places
the binding mode at `lambda_max`. Rearranging `mu_N(K) > -1` gives the window.
-->

**Critical crowding.** The same inequality reads `m_N < (1 + c^K)/(1 - c^K)`, and
since `K` is a positive integer the most permissive case is `K = 1`. So a
stabilizing cadence exists at all if and only if

```
   m_N  <  (1 + c)/(1 - c) ,
```

a factor of `9` at `c = 0.8`. Minimum-cadence operation multiplies the sustainable
effective crowding by exactly that factor, and past it the market is unstable at
every cadence, however small the step budget. This is not a second result but the frontier
evaluated at its smallest admissible cadence, which is also why the laziest
retrainer is the hardest to destabilize. [VERIFIED]

**What the supply chain does to the window.** Because Theorem 2 is stated in
`m_N`, substituting Result 1 makes `K_max` a function of the shared-model fraction
at a fixed number of firms. At `m_1 = 0.15`, `kappa = 0.8`, `N = 30` and
`c = 0.8`:

| `s` | `N_eff` | `m_N` | `K_max` |
|---|---|---|---|
| `0.25` | `6.80` | `1.020` | `20.68` |
| `0.50` | `12.60` | `1.890` | `5.28` |
| `1.00` | `24.20` | `3.630` | `2.53` |

Holding the number of competitors fixed and raising vendor concentration cuts
every incumbent's step budget by a factor of eight. The externality in its
sharpest operational form is therefore not merely that **your competitor's entry
consumes your step budget** but that **your competitor's choice of vendor
does too**, without their entering at all and without either firm doing anything
wrong. [VERIFIED]

**What the lever costs.** Cadence buys stability with model staleness, and the
exchange rate is the same quantity on both sides: after a retraining round the
deployed model's gap to its own best response is exactly `c^K` times what it was,
so the `c^K` that widens the stability margin is the staleness. The lever is
cheap near the boundary and expensive far from it, and we quantify it rather than
presenting it as free.

---

## Figure 2

The `(N_eff, K)` plane. Measured joint-loop stability, converge or diverge per
cell on common-random-number seeds, against the predicted frontier, with `s`
contours overlaid and the critical-crowding column where the window closes. One
panel, fully falsifiable.

Caption must state `c = 0.8` and note that `K` is an integer, so the realized
window is `floor(K_max)` while the plotted frontier is continuous.

## Checklist

- [x] `c = 0.8` stated wherever the worked numbers appear
- [x] The composition credited as a composition, not presented as difficult
- [x] Critical crowding given in both forms, the `m_N` bound and the
      `(1+c)/(1-c)` multiplier
- [x] The staleness tradeoff stated, not omitted
- [x] Integer-`K` caveat carried into the figure caption
- [ ] Confirm at assembly that the Mendler-Duenner citation is the right
      attribution for the lazy-deployment slope in the bibliography's spelling

## Notes for the writing pass

**Length.** About 580 words of prose, excluding the table and display math,
comfortably inside one page, which leaves room for
Figure 2 at full width. This section is the one with slack, so it absorbs
overflow from Section 4 if needed.

**What changed against the plan of record.** The plan derives critical crowding
separately from the cadence window. Writing the frontier as
`m_N < (1+c^K)/(1-c^K)` makes it the `K = 1` instance, which saves a derivation
and explains the direction of the effect in the same breath. The plan also omits
`c` from its worked table; `c = 0.8` is pinned here and stated in the caption,
since the table is not reproducible without it.

**The one thing a referee will probe.** Whether `c` really is invariant to `N`.
The honest answer is that it follows from `c` being own-objective curvature, and
that the claim is checked by measuring the realized contraction inside the joint
market across configurations spanning `N`, `kappa`, `m_1` and random `R`. One
sentence in the body, the measurement in the appendix. A reviewer who suspects
the composition will look for exactly this and should find it without asking.
