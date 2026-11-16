# 1. Novelty and the citation surface

## 1.1 What is genuinely new, graded

The paper's novelty claim is four objects, stated in `NOVELTY-CROSSWALK.md`'s
aggregate paragraph: the modulus-governed saturation cap, the pathwise
invariance identity with its two-sided minimax closure, the self-referential
exploitation bound, and the objective-priced stability-constrained design class.
Graded honestly, against a session of literature search rather than against the
crosswalk:

**T2, the exchange rate, is the paper's real contribution and it holds up.** An
exact, policy-independent product identity between estimator variance and
cumulative performative regret is not something I found anywhere. Searches over
adaptive control, dual control, least-costly identification and the
exploration-exploitation control literature returned order-level tradeoffs
(`O(log T)` cost with efficient estimation, `sqrt(T)` regret floors) and nothing
of the form "the product is pinned". The mechanism is elementary once seen, and
the paper says so, which is the right posture. State this as "we are not aware
of", not "first": one session of search is not a literature review.

**L2, the exploitation-information lemma, is the second-best moment.** Bounding
the self-financing of a probe by the information already purchased about one's
own feedback, under a certainty-equivalent anchor, is a genuinely
self-referential construction and the Pinsker step is the right tool. The
honesty box in `derivations/04` about the fixed-`delta` regime is the kind of
thing that makes a proof credible; keep it.

**T5a-c and C5.1 are standard machinery in a new place, correctly labelled.**
The A-, D- and c-optimality derivations are textbook KKT over the PSD cone. What
is new is that the budget is the decision-maker's own curvature, which makes the
optimal shapes functions of `Gamma_PO`. The Simchowitz-Foster inversion
("naive exploration is optimal for LQR" becomes "naive exploration overpays by
exactly `F`") is the paper's most quotable line and it is correct: `F = 1` iff
the curvature spectrum is flat, which is precisely the isotropic case where the
LQR result lives. I verified `F` and both optimality claims independently
(136 checks in `tools/indep_check.py`, including 4000 random feasible designs
per cell never beating the optimum).

**T1, T6, T7 and T8 are correct and useful, and none is deep.** T1 is a
geometric sum plus a Lyapunov identity. T6 is a rank count on a Chebyshev
system. T7 is a bias-variance tradeoff with a budget constraint. T8 is a concave
NPV with a first-order condition. Each does necessary work and the paper does
not oversell any of them. T8's "`gamma_PO` cancels" is a nice observation and it
verifies exactly.

**T3 and T4 are where the novelty claim is thinnest, and the paper's own
scoping is better than the body's phrasing.** See `02`: the body asserts more
than the appendix proves, and the fix is to say what is actually there, which is
still a good result.

## 1.2 The citation gap a reviewer will hit first

**Bracale, Maity, Sun and Banerjee, "Learning the Distribution Map in Reverse
Causal Performative Prediction", AISTATS 2025 (PMLR v258), arXiv:2405.15172.**

This paper does optimal design for estimating the distribution map in
performative prediction, and it does a regret analysis of the resulting
exploration. Section 4 is titled "Optimal design for deploying models"; Section
5 is "Regret analysis on performative risk"; Algorithm 3 is a sequential design
with a doubling trick that splits each episode into an exploration and an
exploitation phase, and Theorem 5.1 gives the total regret
`Reg(M) = O_P(M^{1/(1+eta)} log^eta)` at the optimal split
`alpha = 1/(1+eta)`. They compare their bound to Jagadeesan et al. (2022).

This is the nearest prior art to the paper's entire premise, it predates the
crosswalk by more than a year, and it is uncited. Two consequences:

1. **The G1 gap statement does not survive it.** `LITERATURE-REVIEW-M2.md`'s G1
   reads "Identification is never *priced* in performative prediction
   (exploration exists only as an algorithmic device; Jagadeesan prices the
   search, not the knowledge)". Bracale et al. price exactly the exploration
   needed to learn the map. G1 as written is false.
2. **The delta is still real, and it is sharper than G1.** They optimise an
   exogenous criterion (mean integrated squared error of the map) against an
   order-level regret bound with a tuned exploration fraction. The paper prices
   the design in the decision-maker's own curvature, gets an exact invariance
   rather than a rate, closes it from below with a minimax floor, and adds a
   stability constraint that has no counterpart there. Saying that is a stronger
   positioning sentence than the one currently in the paper.

Replacement text, for the Positioning paragraph in Section 1, to sit
immediately after the Jagadeesan sentence. This is 34 words; the trim order's
item 4 (the Rothschild/Easley/Aghion citation clause in Section 3) pays for it
and is already listed as expendable:

> \citet{bracale2025reverse} design deployments to learn the distribution map
> and bound the regret of doing so at an order level; we price the same activity
> exactly, in the objective's own curvature, and close it from below.

Bibliography entry:

```bibtex
@inproceedings{bracale2025reverse,
  author    = {Bracale, Daniele and Maity, Subha and Sun, Yuekai and Banerjee, Moulinath},
  title     = {Learning the Distribution Map in Reverse Causal Performative Prediction},
  booktitle = {Proceedings of the 28th International Conference on Artificial
               Intelligence and Statistics (AISTATS)},
  series    = {PMLR},
  volume    = {258},
  year      = {2025}
}
```

I read the extracted text of the abstract, Section 4, Section 5, Algorithm 3 and
Theorem 5.1. I did not read the whole paper. Give it a ten-minute skim before
the sentence goes in, but the dispatch above is written strictly from what those
sections say.

## 1.3 The citation gap an OR reviewer will hit

**The paper's model is a market maker and it cites no market-making
literature.**

Section 2 is a dealer quoting a half-spread against informed flow. That is the
adverse-selection market-making problem, and it has a large OR and
quantitative-finance literature. `references.bib` contains 26 entries and not
one of them is from it. This matters more at ML x OR than it would at a pure ML
workshop, because half the programme committee comes from the OR side.

The awkward part: three of those papers are already in the repository's own
`literature/pdfs/`, and `LITERATURE-REVIEW-M2.md`'s manifest tags all three
**V1, "PDF in hand and read"**. They appear in the source manifest labelled
"instantiation" and get no cluster, no delta row, and no bibliography entry. The
review read them and then dropped them.

The one that is not optional:

**Barzykin, Bergault, Gueant and Lemmel, "Optimal Quoting under Adverse
Selection and Price Reading", arXiv:2508.20225v5, revised 13 Jun 2026.** From
the abstract, read directly from the PDF in the repository: they "tackle two
critical dimensions: adverse selection, arising from the presence of informed
traders, and price reading, whereby the market maker's own quotes inadvertently
reveal the direction of their inventory". Price reading is a performative
feedback loop in market making, written by the market-making community, two
months old. A paper that models a dealer whose quotes summon informed flow and
does not cite it is exposed.

Replacement text for Section 2, appended to the sentence that introduces the
toxic channel. 26 words, and Figure 2's width (0.41 to 0.38, trim item 1) pays
for it:

> The quote-summons-toxicity channel is the market maker's adverse-selection
> problem \citep{gueant2013inventory}; that its own quotes feed the flow it
> then reads is \citet{barzykin2026quoting}'s price-reading effect.

```bibtex
@article{gueant2013inventory,
  author  = {Gu{\'e}ant, Olivier and Lehalle, Charles-Albert and Fernandez-Tapia, Joaquin},
  title   = {Dealing with the Inventory Risk: A Solution to the Market Making Problem},
  journal = {arXiv preprint arXiv:1105.3115},
  year    = {2013}
}

@article{barzykin2026quoting,
  author  = {Barzykin, Alexander and Bergault, Philippe and Gu{\'e}ant, Olivier and Lemmel, Malo},
  title   = {Optimal Quoting under Adverse Selection and Price Reading},
  journal = {arXiv preprint arXiv:2508.20225},
  year    = {2026}
}
```

Both entries are given as arXiv preprints because that is what I read. The
Gueant-Lehalle paper has a journal of record; I did not re-verify which, so
check it before the bibliography goes final rather than taking the entry above
as authoritative.

If only one of the two fits the page, take Barzykin et al. It is the
contemporaneous one and it is the one whose subject is the paper's own feedback
loop.

## 1.4 The stateful line, cheap to close

**Li and Wai, "State Dependent Performative Prediction with Stochastic
Approximation", AISTATS 2022, arXiv:2110.00800.** PDF in the repository; first
page read directly. Their setting is a learner whose samples are "adapted to the
learner's and agent's previous states", with an explicitly "unforgetful" data
process and a finite-time analysis at rate `O(1/k)`.

That is the paper's retraining cobweb: `d_{t+1} = -m d_t + u_t` carries state,
and the whole saturation story (T1) is about what that state does to
identifiability. The stateful line is the closest structural neighbour to the
paper's dynamics and it is uncited.

`brown2022performative` (Brown, Hod, Kalemaj, "Performative Prediction in a
Stateful World", AISTATS 2022) is already in `references.bib` and never cited,
which is the same gap half-closed.

Cheapest fix, zero page cost: add both to the existing Section 1 citation
bracket after `\citep{izzo2021learn,miller2021outside}`, which becomes

> \citep{izzo2021learn,miller2021outside,li2022state,brown2022performative}

```bibtex
@inproceedings{li2022state,
  author    = {Li, Qiang and Wai, Hoi-To},
  title     = {State Dependent Performative Prediction with Stochastic Approximation},
  booktitle = {Proceedings of the 25th International Conference on Artificial
               Intelligence and Statistics (AISTATS)},
  year      = {2022}
}
```

Three further entries already sit in `references.bib` uncited:
`mendler2020stochastic`, `drusvyatskiy2022stochastic`, `hardt2023performative`.
With `plainnat` they simply do not print, so there is no build consequence, but
the Drusvyatskiy-Xiao and Hardt-Mendler-Duenner entries are the two that a
performative-prediction reviewer expects to see acknowledged somewhere. One
`\citep` in the Section 1 opening bracket costs nothing.

## 1.5 Contemporaneous 2026 work, verify before citing

The crosswalk predates these. None is load-bearing against the paper's novelty;
all four are things a 2026 reviewer may know.

**Zhang, Hou and Zhang, "Unified Inference Framework for Single and
Multi-Player Performative Prediction: Method and Asymptotic Optimality",
arXiv:2602.03049, Feb 2026.** This is the one that touches T3/T4. They derive
a semiparametric efficiency bound for estimating the distributional parameter
under performativity and prove their estimators attain it. That is a variance
lower bound for learning the performative response, which is the same object
the paper's floor is about. **I read a structured report of this paper, not
the paper.** Verify before citing. If it says what the report says, the delta
is clean and worth one clause: their bound is on asymptotic variance at a
given sampling scheme with no cost side, while the floor here is on the
variance-times-cost product over designs. Camera-ready, not pre-deadline.

- **"Dissecting Performative Prediction: A Comprehensive Survey"**,
  arXiv:2602.10176 / ACM, Feb 2026. A newer survey of record than the
  `hardt2023performative` entry sitting uncited in the bibliography. Abstract
  only. Camera-ready.
- **"The Stability of Online Algorithms in Performative Prediction"**,
  arXiv:2602.24207, Feb 2026. Adjacent to the modulus and L4 story. Abstract
  only. Camera-ready.
- **"Partially Performative Prediction"**, arXiv:2606.07890, Jun 2026. Abstract
  only. Probably not needed.

Do not cite any of these four unread. The pre-deadline citation work is 1.2,
1.3 and 1.4, all of which rest on documents I read.

## 1.6 One number in this section that the paper cannot source

Section 3 says "The boundary is exact: with `c` known a priori the floor breaks
(ratio -> 0.05)". Nothing in the shipped repository computes a known-`c` ratio.
`run_open1.py` has no such branch, and the value does not appear in `OPEN1.md`,
`OPEN-PROBLEMS.md` or `RESULTS.md`. The only 0.05 nearby is the tight-probe
*location* `t = 0.05` in `OPEN1.md`'s scan table, whose ratio is 40.94.

This matters more than an ordinary loose number because the checklist asserts
"Every numeric claim in the paper traces to a row in RESULTS.md, OPEN1.md, or
REALDATA.md", and it puts this exact claim on the never-trim list.

The claim's *direction* is right, and I confirmed it independently. Dropping the
`c` coordinate leaves `theta = (C0, C1)` with sensitivity `s(h) = (1, e^{-ch})`;
the Cramer-Rao product for `eps(h*)` then falls monotonically as the probe moves
away from the anchor, because sensitivity to `C1` grows like `e^{-ch}` while
cost grows only quadratically. Over the paper's own probe grid it reaches 0.0425
at `t = 0.05`; over unconstrained two-point designs it reaches 0.0344 at
`t = 0.001` and is still falling. There is no limit at 0.05, so the arrow is
wrong even if a 0.05 was computed offline at some particular design.

Replacement sentence, same length as the original, no page cost:

> The boundary is exact: with $c$ known a priori the floor breaks outright, and
> the best design's Cram\'er--Rao product falls below it without bound as the
> probe widens (ratio $0.30$ at $t{=}1.0$, $0.04$ at $t{=}0.05$).

If the underlying scan is not going to be shipped by 31 Aug, cut the numbers and
keep the boundary:

> The boundary is exact: with $c$ known a priori the floor breaks outright.

Either version keeps the never-trim item intact. The first is better and costs
one afternoon: the computation is thirty lines in `run_open1.py`, reusing the
`cr_product` machinery already there with the `c` column dropped.
