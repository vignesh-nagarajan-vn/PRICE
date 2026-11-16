# 6. Result 3: herd immunity, and diversity as its substitute

**Status: drafted.** Target 1.25 pages. Source:
[`../math/derivations/04-mixed-market-secular.md`](../math/derivations/04-mixed-market-secular.md),
which supersedes `../math/03-theorem3-herd-immunity.md` where they disagree.
Certificates in `../ml-contributions/certificates/verify_theorem3_herd_immunity.py`.

**This is the paper.** If the build slips, everything else gives way before this
section does.

---

The second lever is a technology mandate, and unlike cadence it is not something
a firm can pull alone to any effect. A **corrected** firm runs the feedback-aware
update rather than the naive one, so its retraining is governed by the objective
curvature `gamma_PO` in place of the cobweb, and its modulus is scaled by
`theta = gamma/gamma_PO < 1`. The update itself is published machinery
(Izzo et al., 2021; Miller et al., 2021, with the structurally anchored variant
in REFLEX). What is new here is running it inside the game: a mixed market of
`N_b` blind firms and `N - N_b` corrected ones, with corrected fraction
`rho = 1 - N_b/N`. Correction changes a firm's gain and not its response
direction, so the alignment matrix `R` is untouched.

**Theorem 3.** *With supply-chain alignment and two correction levels, the joint
Jacobian's symmetric congruence is a diagonal matrix plus a positive rank-one
term, so its spectrum solves a secular equation. Two distinct moduli collapse
that equation to a quadratic, and for `1 <= N_b <= N-1` the radius is its larger
root,*

```
   rho(J)  =  ( P + sqrt(P^2 - 4Q) ) / 2 ,       ks := kappa*s ,
   P  =  (1-ks) m_1 (1 + theta)  +  ks m_1 ( N_b + theta N_corr ) ,
   Q  =  theta m_1^2 (1 - ks) N_eff ,
```

*with the remaining spectrum flat within each block. An empty block needs the
single-block form `m_1 N_eff` or `theta m_1 N_eff` instead; the quadratic
otherwise leaves a phantom root that can exceed the true radius.* [VERIFIED,
exact to `2.5e-14` against dense eigensolves on 6000 draws]

`N_eff` appearing inside `Q` is the reason every statement below carries `s`: the
mixed market inherits Result 1's crowding through the product term rather than by
stipulation.

**The strong-correction limit, and it errs in the unsafe direction.** As
`gamma_PO -> infinity` the quadratic's constant term vanishes and the unstable
cycle runs through blind firms only, giving `m_1(1 + kappa s (N_b - 1)) < 1`,
that is

```
   N_b  <  N_c(s)  =  1  +  (1/m_1 - 1)/(kappa*s) .
```

This is the memorable criterion, and taken alone it is **optimistic rather than
conservative**. The radius is nondecreasing in `theta` by Perron-Frobenius on an
entrywise-nonnegative matrix, so the limit under-states it: on random draws with
`theta` in `[0.01, 1]` the limit calls `11.8%` of configurations stable that are
unstable at every finite correction strength. A market of 20 firms with 10
corrected, at `m_1 = 0.12`, `kappa = 0.8`, `s = 1`, reads as comfortably stable in
the limit and is in fact unstable unless `gamma_PO` exceeds `58.6 gamma`. The
exact root is therefore the criterion and the limit is its corollary, quoted with
its error direction rather than on its own. The same monotonicity carries the
reassuring half: **correction never backfires**, so no configuration exists in
which un-blinding a firm destabilizes the market. [VERIFIED]

**The collapse, and its honest generalization.** At `kappa = s = 1` we have
`N_c = 1/m_1` and `N_eff = N`, so the limit reads

```
   rho*  =  1 - 1/m_N ,
```

**exactly the epidemiological herd-immunity threshold `1 - 1/R_0`** with the
systemic modulus as the reproduction number. A market of 10 firms at `m_N = 2.5`
needs 60% of them un-blinded, *if correction is perfect*. It is not, and at that
same corner the quadratic degenerates to `rho(J) = m_1(N_b + theta N_corr)`, whose
stability condition solves exactly for

```
   rho*(e)  =  ( 1 - 1/m_N ) / e ,        e  =  1 - gamma/gamma_PO ,
```

with `e` the **correction efficacy**. That is the standard coverage requirement
for an **imperfect vaccine**, of which the clean law is the perfect-efficacy
corner. The correspondence therefore does not merely survive the refinement, it
predicts it: a structural analogy transfers the refinements of the law it
borrows, and a decorative one does not. [VERIFIED, exact to `1.8e-15`]

**Critical efficacy.** `rho*(e)` exceeds one, so no corrected fraction works at
all, exactly when `theta > 1/m_N`. Correction is a usable lever only if

```
   gamma_PO / gamma  >  m_N .
```

At `m_N = 2.5` the corrected update must deliver a `2.5x` curvature improvement or
un-blinding cannot stabilize the market whatever fraction is treated. This is the
exact structural parallel of Section 5's critical crowding: each lever has a
regime past which it stops working, and knowing both is what makes trading them
off below an honest exercise rather than an extrapolation. [VERIFIED]

**Why the analogy is structural.** In heterogeneous populations `R_0` is *defined*
as the spectral radius of a next-generation operator (Diekmann et al., 1990), and
`m_N` is the spectral radius of the joint retraining Jacobian. The two thresholds
are the same statement about a linearized operator and not a resemblance between
two curves. The clean `1 - 1/R_0` form assumes homogeneous mixing (Fine et al.,
2011), and the collapse here assumes the `kappa = s = 1` corner for precisely that
reason; away from it the exact threshold is the quadratic's root set to one.
Stating the assumption in the same breath as the formula is what separates this
from a slogan.

**The synthesis.** `rho*` is increasing in `s`, strictly wherever it is positive,
so a market reaches stability along either axis. At `N = 20`, `m_1 = 0.15`,
`kappa = 0.8`:

| `s` | `N_c(s)` | `rho*` | minimum corrected firms |
|---|---|---|---|
| `1.0` | `8.08` | `0.596` | `12` |
| `0.5` | `15.17` | `0.242` | `5` |
| `0.2` | `36.42` | `0` | `0` |

A monoculture needs about 60% of its agents corrected; at half the response
shared, a quarter suffices; at a fifth, the market is stable with no corrected
agents at all. The last column is the one a regulator acts on, and it is
`N - ceil(N_c(s)) + 1` rather than `ceil(rho* N)`. The two agree on almost every
configuration and differ by one firm exactly when `N_c` is an integer, which at
`N` in the tens is several percentage points of coverage. [VERIFIED]

**The economic reading.** Correction is a public good. An un-blinded firm captures
a private benefit while the stability it contributes accrues to everyone, so the
market free-rides below the threshold and does not reach `rho*` unaided
(Bergstrom, Blume and Varian, 1986). Model diversity has the same structure: a
firm choosing an idiosyncratic vendor pays for it privately and supplies systemic
stability for free. **The substitution is therefore between two goods that are
both under-supplied**, not between a good and a bad. That is what makes the
frontier something a regulator can move along rather than a menu of two policies
plotted on shared axes, and it is what Result 4 prices.

**Scope.** Hypothesis (M) treats correction as a pure gain reduction. A corrected
firm that also changed its response direction would move `R`, which this
derivation does not model. Three or more correction levels return a genuine
secular equation rather than a quadratic. Both are named in Section 10.

---

## Figures 3 and 4

**Figure 3, herd immunity.** Stability against corrected fraction in an `m_N > 1`
regime, with the predicted `rho*` marked. Plot the exact threshold at the
simulated `gamma_PO` alongside the perfect-correction limit: the gap between them
is a result, not an error bar, and it is the visual form of the `11.8%` sentence
above. Caption states `N`, `m_1`, `kappa`, `s` and the efficacy grid, and notes
that the realized threshold is a whole number of firms.

**Figure 4, the substitution frontier.** The `(rho, s)` iso-stability curve,
measured against predicted. **The headline figure and the one that goes on the
poster.**

**The free-riding diagnostic** (private objective of corrected against blind
firms) sits in the appendix or as Figure 3's second panel, and is third in the
de-scope order.

## Checklist

**Structure and honesty, all new since the exact root landed:**

- [x] The exact two-block root is the theorem; the limit is its corollary
- [x] The limit's optimism stated with a number, in the same paragraph as the
      limit itself, never in a later caveat
- [x] The imperfect-correction law present, framed as the analogy predicting its
      own refinement
- [x] Critical efficacy stated, and tied to Section 5's critical crowding

**Carried over from the original plan:**

- [x] The threshold and the frontier presented together, threshold first
- [x] Diekmann et al. cited where the analogy is claimed, not elsewhere
- [x] The homogeneous-mixing assumption stated alongside the clean formula
- [x] Both-goods-under-supplied sentence present
- [x] Integer threshold uses `N - ceil(N_c) + 1`, not `ceil(rho* N)`
- [ ] The experiment is new in kind: the corrected loop has never run inside a
      multi-agent game. **Carried to Section 9**, where the panel's status is
      stated; this section makes no claim about what has been measured
- [ ] Confirm at assembly that Izzo et al. and Miller et al. are the right
      attributions for the corrected update in the bibliography's spelling

## Notes for the writing pass

**Length.** About 1150 words of prose, excluding the display math and the table.
That is over the 1.25-page target if both figures run at full width. The first
cut is the scope paragraph, which moves wholesale to Section 10, and the second
is the worked table's middle row. Neither cut touches the exact root, the
imperfect-correction law or the critical efficacy.

**What changed against the plan of record.** The plan presented the strong-
correction limit as the theorem. It is a corollary here, and its error direction
is stated in the same paragraph, because C18 showed it errs optimistic. The
imperfect-correction law and the critical efficacy are new content that did not
exist when the section was planned.

**The one thing a referee will probe.** What happens at finite `gamma_PO`. The
section answers it in closed form before the question is asked, which was the
whole point of the repair. The second probe is whether `rho*(e)` is exact away
from `kappa = s = 1`; it is not, the body says so, and the deviation is measured
rather than hidden.
