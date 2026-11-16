# 4. Result 1: the effective number of independent learners

**Status: drafted.** Target 1.25 pages. Source:
[`../math/derivations/01-alignment-spectrum.md`](../math/derivations/01-alignment-spectrum.md)
and [`../math/derivations/02-supply-chain-concentration.md`](../math/derivations/02-supply-chain-concentration.md),
which hold the complete proofs. Certificates in
`../ml-contributions/certificates/verify_theorem1_proof.py`.

Double-blind compliance: REFLEX appears in the third person as an ordinary
reference. No sentence positions it as the authors' own work.

---

The multi-agent stability condition counts firms. Counting firms is wrong, and
correcting it is what brings algorithmic monoculture and the AI supply chain
inside the model rather than alongside it.

**The alignment object.** Let firm `i` have response Jacobian `E_i`, the `d x d`
matrix describing how its own deployment reshapes the flow it faces, and define

```
   r_ij  =  <vec E_i, vec E_j> / ( ||E_i||_F ||E_j||_F ) ,       R  =  (r_ij) .
```

`R` is a correlation matrix of models' *feedback directions*, not of their
returns or their predictions. It is positive semidefinite with unit diagonal, so
its eigenvalues sum to `N` and `lambda_max(R)` runs from `1`, every firm
perturbing the environment its own way, to `N`, every firm perturbing it
identically.

**Theorem 1.** *With equal moduli `m_i = m_1` and heterogeneous response
directions, the joint retraining Jacobian is `J = -m_1[(1-kappa)I + kappa R]`,
whose spectral radius is*

```
   m_N  =  N_eff * m_1 ,        N_eff  =  1 + kappa ( lambda_max(R) - 1 ) ,
```

*and the market is stable if and only if `m_N < 1`.* [VERIFIED]

Setting `R = 1 1'` recovers the symmetric multi-dealer law of REFLEX
(arXiv:2608.16155) exactly, so the published result is not generalized away but
located: it is the monoculture corner, where every firm's feedback points the
same way.

<!-- APPENDIX, page-budget step 1, 19 Aug 2026. The two-step proof below moves
     out of the body and into the appendix. The body keeps the located-corner
     sentence above, which is the reading, not the derivation.

The proof is two steps. Firm `i` senses the shared pool through its own response
channel, feeling its own contribution in full and each competitor's with weight
`kappa`, which makes the coupling coefficient between `i` and `j` exactly `r_ij`
and produces the Jacobian above. Its eigenvalues are
`-m_1[(1-kappa) + kappa*lambda_i(R)]`, and because `R` is a Gram matrix every
bracket is nonnegative, so the radius sits at `lambda_max` with no absolute-value
slack.
-->

| Configuration | `lambda_max(R)` | `N_eff` | reading |
|---|---|---|---|
| Monoculture, `R = 1 1'` | `N` | `1 + kappa(N-1)` | the inherited law, measured at `1.74x` and `3.16x` for `N = 2, 3` |
| Orthogonal, `R = I` | `1` | `1` | a hundred firms are dynamically one firm |
| Simplex, `r_ij = -1/(N-1)` | `N/(N-1)` | `1 + kappa/(N-1)` | maximal spread, and still worse than orthogonality |

The simplex anchor is worth one clause of care because it carries two
consequences. Its Jacobian spectrum contains `m_1(1-kappa)`, which independently
matches the differential-mode eigenvalue the base theory derives by a completely
different route, but that value sits on the all-ones direction and is the *most*
stable mode rather than the radius. So the common mode binds only when no firm's
feedback anti-aligns with another's, that is, when `R` has nonnegative entries and
Perron-Frobenius places the leading eigenvector in the nonnegative orthant. Shared
vendors and shared corpora produce positive alignment, so the realistic regime
satisfies the condition, and we state it rather than assume it. [DERIVED]

**Interaction never stabilizes.** Since the eigenvalues of `R` sum to `N`, the
largest is at least their mean, so `lambda_max(R) >= 1` and therefore
`N_eff >= 1` with equality only at `R = I`. A market of adaptive models sharing an
environment is never more stable than one of its members in isolation, and exact
neutrality demands fully orthogonal responses. The externality has a sign: the
coupling can only amplify feedback, never damp it. [VERIFIED]

**The supply chain.** Decompose each firm's response into shared and idiosyncratic
parts, `E_i = sqrt(s) E_shared + sqrt(1-s) Xi_i`, where `s` is the fraction
attributable to a shared foundation model, vendor, or pretraining corpus. The
alignments concentrate at `r_ij -> s` with fluctuation `O(1/d)`, holding with high
probability rather than merely in expectation, so

```
   N_eff  =  1 + kappa * s * (N - 1) ,        m_N  =  m_1 ( 1 + kappa*s*(N-1) ) .
```

**The effective number of learners is the number of independent models, not the
number of firms.** Fifty dealers fine-tuning one vendor's model are dynamically
about `1 + 49*kappa` learners at `s` near one and barely more than one at `s` near
zero. The critical population generalizes from a single number to a surface in
`(N, s)`, which is Figure 1. [VERIFIED]

**Why the natural index fails, and in which direction.** A policymaker reaching
for a diversity statistic would reach for mean pairwise alignment. Evaluating the
Rayleigh quotient of `R` at the all-ones vector gives

```
   lambda_max(R)  >=  1 + (N-1) * mean(R) ,
```

with equality only when `R` has constant row sums. So mean similarity is a *lower
bound* on effective crowding, not an approximation to it, and **every error it
makes is in the direction that lets an unstable market pass**. [VERIFIED]

The gap is large at the realistic topology, which is a vendor with a plurality
rather than a monopoly. Three tightly aligned firms among ten otherwise-orthogonal
ones give `N_eff = 2.60` at `kappa = 0.8`, against `1.48` for the uniform
configuration with the identical mean, an understatement of `1.76x`. A market at
`m_1 = 0.5` then runs `m_N = 1.30` and is unstable while the mean index reports
`0.74` and calls it safe with margin. The simplex makes the sharper point in fewer
words: it *minimizes* mean alignment yet carries `lambda_max = N/(N-1) > 1`, so
the mean does not merely understate the level, it does not order configurations
correctly. **All stability claims in this paper use the spectral form, never a
mean.** [VERIFIED]

**Concentration in the product market is the wrong measurement.** Fifty
equal-share firms have a minimal Herfindahl index and look perfectly competitive.
If all fifty license one vendor's model they are dynamically a monoculture, with
`N_eff = 1 + 49*kappa`. The quantity that enters the stability condition is
concentration in the model supply chain, and the two can point in opposite
directions.

**Scope.** Theorem 1 is exact for equal moduli. The tempting mean-modulus
generalization is provably false, since orthogonal responses decouple the firms
entirely and give `max_i m_i` rather than the mean. The correct object is
`M^{1/2} R M^{1/2}`, which yields `max_i m_i <= rho(J) <= max_i m_i * N_eff`,
exact at `kappa = 0`, at `R = I`, and in the equal-moduli limit, with tightness
measured rather than asserted. [VERIFIED] Share-weighted alignment for
unequal-sized firms needs a majorization condition on the share vector, since the
naive claim that any reweighting raises `lambda_max` is false, and the exact
block-secular reduction for fully heterogeneous ecosystems is journal material.
Both are named and not attempted. [DEFERRED]

---

## Figure 1

The `(N, s)` phase diagram: measured `m_N` over firms by shared-model fraction,
against the predicted boundary. The clustered companion panel sits beside it if
space allows and is fifth in the de-scope order.

## Checklist

- [x] Simplex anchor stated correctly, not as the plan of record had it
- [x] Perron-Frobenius condition on the binding mode stated in the body
- [x] Both counterexamples to mean-based indices present, clustered and simplex
- [x] Heterogeneous-modulus bound stated as a remark with its three exact limits
- [x] Deferred extensions named, not attempted
- [ ] The naming footnote lives in Section 2, not repeated here. Check at
      assembly that the effective-rank concession appears exactly once
- [ ] Length check against 1.25 pages once Section 3 is drafted

## Notes for the writing pass

**Length.** About 920 words of prose, excluding the table and display math.
Compression targets in order: the Herfindahl
paragraph merges into the supply-chain paragraph, the scope paragraph loses its
list of three exact limits to a footnote, and the simplex clause drops to one
sentence with the detail moving to the appendix.

**What changed against the plan of record.** Two things the plan does not contain.
The `N_eff >= 1` corollary is new and cheap, and it gives the section a clean
one-line economic reading. The mean-index result is stated as a bound with a
signed error rather than as two counterexamples, which is shorter and stronger;
the counterexamples stay as the quantification of how large the gap gets.

**Deliberate omission.** No worked derivation of the reduction from response
Jacobians to the coupling matrix. It is four lines in the appendix and a reviewer
who wants it will look there. The body states the mechanism in one sentence,
which is that a firm senses the pool through its own response channel, because
that sentence is the economics and the algebra is not.
