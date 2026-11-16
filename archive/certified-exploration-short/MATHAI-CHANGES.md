# From ML x OR to MATH-AI: what changed, and why

The ML x OR @ NeurIPS 2026 version of PRICE was rejected. This folder holds
the MATH-AI 2026 retarget. Sources were copied from
`ml-or/PRICE-final/ml-or/submission-materials/`, the corrected 1 September
2026 build, not from the stale `ml-or/submission-materials/` tree. Nothing in
either source tree was modified.

The mathematics did not change. No experiment was re-run, no proof was
touched, no number was recomputed. Every quantity in the new body is copied
from the same committed artifacts the old one used. What changed is which
results lead, how much space each gets, and how they are explained.

Anyone wanting to reconstruct the ML x OR version can start from
`ml-or/PRICE-final/ml-or/submission-materials/paper/main.tex`, which is intact,
and use the table below to see what this version did to it.

## The reframing

ML x OR bought the paper as operations research: an exchange rate between
estimator variance and performative regret, with a certified agent and a
real-data leg. MATH-AI does not buy that, because performative prediction is
not in its scope. What is in scope is how mathematics gets made with machine
help, so this version is a case study in machine-assisted mathematical
research, with the PRICE theory as the substrate rather than the subject.

The lead is now Theorem T9 and the eleventh measurement-forced pivot: a
numerical search believed the exchange-rate floor was structure-proof at
ratio 1.005, the proof attempt covered only the reach `h >= h* - 2/c`, and
searching exactly where the proof stopped produced a counterexample at ratio
0.8517. That arc, plus the ten other recorded pivots and the verification
infrastructure, is the paper's argument to this venue.

## What was cut from the body

| Cut | One-line reason |
|---|---|
| The REFLEX corporate-bond real-data leg (10/10 cells, `gamma_PO` spans 510.6 to 2.3, gaps 1.9 to 4.3 percent, `F = 1.63`) | Domain evidence for an OR committee; a MATH-AI reader does not need it. One table row and one appendix sentence remain. |
| The baselines table and discussion (FD-PerfGD, ZO-PerfOpt, UCB-Grid, BlindRRM, 12 seeds, Pareto claim) | Algorithmic competition is not the case study's subject and cost most of a page. |
| The LQ performative-pricing second domain as body text | Same. Survives as one table row. |
| SafeD-PerfGD's engineering detail (the four-step explore/fit/gate/freeze loop, Newton scaling, `L_fam`) | The agent is now one clause in Section 2; its design is not the argument. |
| The positioning paragraph (Jagadeesan, Bracale, Lin, Lai-Robbins, dual control, task-optimal design) | Written for an OR/ML audience arguing novelty against that literature. Cut from the body, then **restored** into Appendix A on 6 September 2026: see the note below. |
| The market microstructure setup (benign flow `Ae^{-kh}`, toxic flow `C_0 + C_1 e^{-ch}`, `psi`, `w`, echo-chamber gap, adverse selection citations) | Reduced to two sentences: a dealer whose quote reshapes the flow it prices. |
| Free-data saturation (T1) as a headline paragraph | Demoted to an appendix statement plus one pivot mention in Section 4. |
| The support-degeneracy (T6) and misspecification-crossover (T7) paragraphs | Stated in the appendix, referenced from Section 4's pivots and Table 1. |
| Figures `fig5_baselines.png` and `fig7_realdata.png` | Their content was cut from the body. |
| Figures `fig2_saturation.png`, `fig3_certification.png`, `fig4_crossover.png` | Kept in `paper/figures/` and in the supplementary, but no longer referenced. The appendix must not contain anything the body never refers to, so the additional-figures appendix went with them. |
| Appendix C, the complete derivation record D0 to D9 (`derivations_body.tex`, 1,664 lines) | Roughly 20 pages of an appendix now capped at 10. It ships in full in the supplementary repository. |
| Proofs of L1 through P9.3 other than L1, T2 and T9 (`proofs_body.tex`, 590 lines, 24 proofs) | The body no longer argues from them. Appendix D says so explicitly and points at `mlxor-derivations/latex/proofs.tex`. |
| Register statements for C1.2, R1, P2.1, P2.2, T5b, T5c, L3, R2, T8, P9.1, P9.2, P9.3 | Not referred to anywhere in the new body. |
| `derivations_body.tex`, `proofs_body.tex`, `theorems_body.tex` deleted from `math-ai/paper/` | No longer `\input` by anything, and 2,495 lines of dead source in a working directory invite mistakes. All three are intact in `ml-or/PRICE-final/ml-or/submission-materials/paper/` and in `math-ai/supporting/mlxor-derivations/latex/`. |

## What was kept, unchanged in substance

- All four headline results: the exchange-rate conservation law (T2), the
  minimax floors (T3, T4), the optimal design theory (T5a, C5.1), and
  certified correction (L4, P7.1). Plus T9, which now leads.
- The full T9 proof, both directions, including the frozen witness, copied
  verbatim from `proofs_body.tex` lines 458 to 575.
- The T2 proof and the L1 cost-equivalence proof it rests on, copied verbatim.
- The compact verification table (Table 1), with the drift row intact.
- Reproducibility: determinism, tail averages, the 0.0062 worst spread.
- Every honesty item the ML x OR review hardened, none re-loosened: the DRIFT
  cell reported and not excused; T4's sharp constant `1/2` labelled
  numerically supported, open, and unproved; the earlier 1.005 verdict named
  as a search artifact; the local scope of T2 with its load-bearing `o(1)`;
  T9(ii)'s true-cost ratio 1.0112 stated so the violation is not overread.
- Zero em dashes, `dblblindworkshop`, anonymous author block, no identifying
  URLs, REFLEX cited in third person.

## What was reframed rather than cut

| Old role | New role |
|---|---|
| T9 as contribution bullet 2's second half, half a paragraph | Section 3, the whole lead, with the search history, the failed proof step, the witness, and why the first search missed it |
| The eleven pivots as one sentence in the results section | Section 4, the generalization argument, with E1, E5 and E7 written out as the same pattern at smaller scale |
| The verification infrastructure as a reproducibility footnote | Section 4, presented as the transferable part: register with proof status, preregistered tolerances, CI, pivots recorded in code |
| The dealer market as the model | Two sentences establishing that the object of study is a decision-maker whose deployed action reshapes its own retraining data |
| Limitations as a paragraph of scope caveats | Same content, plus the explicit statement that eleven pivots from one project by one group is a sample and not a study |

## Writing changes

The ML x OR body was dense: colon-chained clauses, several claims per
sentence, and symbols (`gamma_PO`, `h_SP`, `h_PO`, `m`, the modulus) used in
the introduction without ever being defined in the body. This version defines
before use, opens every section with a plain-language paragraph, and keeps to
roughly one idea per sentence. The claim that earns the most space now reads
"Learning how your own deployment moves the world costs a fixed amount. You
can choose what to buy with it, but not how much to pay."

## Two things worth knowing

1. **One number was restated at the artifact's precision.** The ML x OR body
   quoted the known-`c` boundary ratios as `0.30` at `t = 1.0` and `0.04` at
   `t = 0.05`. `results/OPEN1.md` section D reports `0.3002` and `0.0425`, and
   `0.03475` at `t = 0.001`. This version quotes `0.3002`, `0.0425` and
   `0.0348`. No value changed, only the rounding, which now matches the
   artifact.
2. **The CI workflow files are not in this copy.** The 1 September report says
   `mlxor-derivations/.github/workflows/verify.yml` and
   `posk-pipeline/.github/workflows/ci.yml` were restored into the shipped
   zip, but neither exists anywhere in this repository, including in
   `ml-or/PRICE-final/`. The appendix therefore says CI runs in the project
   repository and that the two workflow files are not part of the anonymized
   copy, rather than claiming the supplementary contains them.

## Correction, 6 September 2026: the references

Cutting the positioning paragraph took its citations with it, which was a
mistake rather than a space decision. The build of 4 September printed 6
references from 31 bibliography entries. Twenty-five were orphaned, and
several results stood with no attribution at all: A-optimal design without
Kiefer and Wolfowitz or Pukelsheim, van Trees minimax floors without Gill and
Levit, an extended Chebyshev system asserted without a source, and the dual
control lineage absent. The venue allows an unlimited number of reference
pages, so nothing was bought by the omission.

Worse for this venue, the bibliography contained no machine-assisted
mathematics at all. A case study in how mathematics gets made with machine
help cited no work on computation guiding mathematical intuition, on search
refuting conjectures, or on automated proof.

What changed:

- Nine entries added for the machine-assisted mathematics literature, with
  metadata verified against Crossref or arXiv.
- A new Appendix A, `paper/appendix_related.tex`, which places the eleventh
  pivot against that literature and restores the substrate's positioning
  against performative prediction, learning while earning, dual control and
  experiment design.
- Representative citations threaded into the body where they fit inside four
  pages, and attribution attached to the individual statements in Appendix B.
- Nine entries removed again on a second pass, described below.
- All 31 entries are cited, and the body still ends on page 4.

### The second pass: trimming the inherited OR cluster

Restoring the ML x OR citations wholesale overshot. One paragraph in Appendix
A carried nine references, six of them inside a single bracket, for the
operations-research incomplete-learning literature. That bracket was doing
adversarial-novelty work for an OR committee, which is not this venue's
argument, and citing a survey together with six of the papers it surveys reads
as list-stuffing rather than scholarship.

Removed, with the point each was making now carried by an entry that stays:

| Removed | Point now carried by |
|---|---|
| `rothschild1974two`, `easley1988controlling`, `aghion1991optimal`, `harrison2012bayesian`, `broder2012dynamic` | `denboer2015dynamic`, the survey covering them, plus `keskin2014dynamic` as the dynamic-pricing exemplar |
| `grossman1980impossibility` | Nothing. It was thematically adjacent and never engaged. |
| `dean2020sample` | `simchowitz2020naive` and `wagenmaker2021task`, which carry the linear-systems comparison |
| `mendler2020stochastic` | The three other gap-closing algorithms already cited |
| `li2022state` | `brown2022performative`, the stateful case |

No result lost its attribution and no claim changed. The bibliography went
from 40 entries to 31, and the paper from 14 pages to 13.

The mathematics is still untouched. No experiment was re-run and no number was
recomputed for this change set.
