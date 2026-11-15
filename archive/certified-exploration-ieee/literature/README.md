# Literature Review — "The Price of Self-Knowledge"

In-depth literature review for the certified-exploration paper: **identification cost,
exploration, and stability in performative systems**. The paper claims that
estimating a system's own performative response is a priced, designed,
stability-constrained activity — this review maps the six literatures that
claim touches, verifies every source, justifies each gap, and renders an
honest novelty verdict.

## Contents

| File | What it is |
|---|---|
| `LITERATURE-REVIEW-M2.md` | The full review: 6 clusters, ~35 sources, per-paper deltas, gap justifications (G1–G6), novelty verdict, source manifest |
| `pdfs/` | 10 core PDFs in hand (arXiv versions, from the REFLEX literature collection) |
| `download_litreview_pdfs.sh` | One-command fetch of the remaining open-access PDFs (arXiv IDs) + DOI links for the paywalled classics — run on an unrestricted machine; the build environment blocks arXiv/PMLR/publisher sites |

## Verification method

Every source is tagged with how it was verified:

- **V1** — PDF in hand and read (10 papers; the closest ML neighbor,
  Jagadeesan et al. ICML 2022, was read in full for this review)
- **V2** — bibliographic record (venue, volume, pages, year) confirmed
  against the publisher/aggregator via web search this week
- **V3** — canonical classical result, cross-checked against an independent
  index; flagged for a click-check at camera-ready

Credibility bar: every load-bearing source is a top peer-reviewed venue
(ICML, NeurIPS, AISTATS, COLT, Operations Research, Management Science,
Automatica, Annals of Statistics, JET, REStud, Econometrica, FoCM) or a
survey of record. arXiv-only items map the 2024–26 frontier and are never
load-bearing for a gap claim.

## The six clusters

| # | Cluster | Anchor sources | What it supplies / lacks |
|---|---|---|---|
| A | Performative prediction core | Perdomo et al. '20; Mendler-Dünner et al. '20; Izzo et al. '21; Miller et al. '21; Drusvyatskiy–Xiao (MOR '22); Hardt–MD survey '23 | The framework and the modulus; **no identification pricing anywhere** — confirmed by the field's own survey |
| B | Exploration inside performativity | **Jagadeesan et al. ICML '22**; **Lin–Zrnic ICML '24**; zeroth-order/noise-injection family | The nearest ML neighbors: regret of *search* and plug-in models — neither has a cost side, a loop, or a stability constraint |
| C | OR: pricing with demand learning | **Keskin–Zeevi (OR '14)**; Harrison–Keskin–Zeevi (MS '12); Broder–Rusmevichientong (OR '12); den Boer survey '15; **Lai–Robbins '79/'82** | Incomplete learning under converging policies — the static-environment ancestor of the saturation theorem; order-level bounds, no invariance identity, no performativity |
| D | Adaptive control & system ID | Feldbaum '60–61 (dual control); persistent excitation (Åström–Wittenmark, Ljung); **Bombois et al. (Automatica '06)**; Dean et al. (FoCM '20); Simchowitz–Foster (ICML '20); Wagenmaker et al. (ICML '21) | Least-costly ID and task-optimal design — for an *exogenous* plant; no retraining loop to starve or destabilize |
| E | Optimal experimental design | Kiefer–Wolfowitz '60; Fedorov '72; Pukelsheim; van Trees / Gill–Levit '95 | The D-/A-optimality toolbox and the Bayesian Cramér–Rao machinery; cost is always exogenous |
| F | Economics of experimentation | Rothschild (JET '74); McLennan '84; Easley–Kiefer (E'metrica '88); Aghion et al. (REStud '91); Keller–Rady (REStud '99); Grossman–Stiglitz (AER '80) | Rational incomplete learning and the patience mechanism — qualitative; the environment never reacts *to the agent* |

## The gaps (each justified against its nearest prior art)

- **G1** — Identification is never *priced* in performative prediction
  (exploration exists only as an algorithmic device; Jagadeesan prices the
  search, not the knowledge)
- **G2** — No saturation theorem for *retraining loops* (pricing/control have
  incomplete learning, but from optimizer convergence against a static
  environment — no modulus, no "safety implies blindness")
- **G3** — No exact exchange rate anywhere (every neighbor states rates or
  bounds, never an invariance identity; Lai–Robbins log-n schemes lie *on*
  the frontier — consistency check performed)
- **G4** — No stability-constrained experiment design (Bombois's constraint
  is plant limits, not the spectral contraction of a learning loop)
- **G5** — Anchoring vs. misspecification never budget-priced (Lin–Zrnic is
  closest of all ~35 sources; it has no cost side — must be cited as the
  launch point of Theorem 6)
- **G6** — The explore-or-stay-blind decision has no closed form (economics
  has the qualitative patience mechanism; the market model makes it
  computable)

## Novelty verdict (the honest one)

**New:** the framework — identification of one's own performative response as
a priced, designed, stability-constrained activity — and four objects within
it: the modulus-tied saturation cap, the exact invariance identity (+ minimax
and matrix versions), the spectral-safety design class, and the budget-priced
anchoring crossover.

**Not new, and the paper must say so:** the learning-vs-earning tension
(Feldbaum, Rothschild), incomplete learning under converging policies
(Lai–Robbins, Keskin–Zeevi), cost-constrained ID for a downstream task
(Bombois, Wagenmaker), the design toolbox. Correct self-description: *the
performative instance of dual control, where the plant is the learner's own
retraining loop — and there, order-level tradeoffs become exact identities
with computable constants.*

**Four citations without which the paper is rejected:** Jagadeesan et al.
(B1), Keskin–Zeevi (C3), Bombois et al. (D3), Lin–Zrnic (B2) — each gets a
named-delta sentence in related work. **Two quotable consistency checks:**
Lai–Robbins sits on the frontier; Simchowitz–Foster's "naive exploration is
optimal" flips performatively by the curvature-dispersion factor.

## Frontier de-risking

The 2024–26 arXiv sweep found no identification-cost work. The
scariest-sounding title, Hardt's "Retraining Seeks Stable Signals" (July
2026), was checked directly: it concerns *why RRM fixed points exist*
(stable-signal principle) — orthogonal to identification cost, and a useful
citation rather than a threat.

## Remaining work before submission (~1 day)

1. **Full-text reads of the 4 closest papers** (Lin–Zrnic, Keskin–Zeevi,
   Bombois, arXiv:2408.08499 "The Limitations of Model Retraining…") — run
   the download script locally; the build environment cannot fetch them
2. **Add the safe-exploration sub-cluster** (SafeOpt/Sui et al., Berkenkamp
   et al., Turchetta et al.) as the neighbor of Theorem 5's constraint class
3. Abstract-read the remaining 2025–26 frontier items
4. Compress into the paper's related-work section (the named-delta sentences
   are already formulated in the review)
