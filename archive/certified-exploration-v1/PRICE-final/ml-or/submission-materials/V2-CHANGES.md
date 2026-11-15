# V2: anonymous build with the REFLEX foundation, Theorem T9, and the full derivation appendix

This build starts from the reviewed-and-fixed V1 (see REVIEW-FIXES.md) and
adds five things.

## 1. REFLEX cited as the foundation paper

REFLEX (Nagarajan and Ashok, arXiv:2608.16155, 2026) is now cited in
third person as the structural market this paper builds on: in the
abstract, at the top of the Model section, and in the real-data leg
(which validates against REFLEX's published run and says its validation
inputs live in the REFLEX repository). The bib entry is `reflex2026`.

## 2. Fully anonymous build (NeurIPS template, dblblindworkshop)

- `\usepackage[dblblindworkshop]{neurips_2026}`: Anonymous Author(s)
  block, no names, no emails.
- The abstract's repository URL is replaced by "anonymized repository in
  the supplementary material".
- Prior work, REFLEX included, is cited in third person; the checklist no
  longer names authors.
- CAVEAT, stated in the preamble and the checklist: the CFP as verified
  on 25 Aug 2026 says the workshop is SINGLE-blind and non-anonymous
  (`sglblindworkshop`). If that stands, swap one option token and restore
  the author block. The anonymous build is what was requested here.

## 3. A new theorem (T9): structure-proofness of the floor, with an exact reach

The old claim "adversarial numerics show the floor is structure-proof
(best 1.005x)" is replaced by something sharper and two-sided:

- **Proved (T9(i))**: on every design supported within two curvature
  lengths of the anchor (h >= h* - 2/c), no design that knows the
  response family's functional form has Cramer-Rao product below the
  exchange-rate floor. The proof exhibits the family element
  phi0 = 2/c - e^{-c(h-h*)}(2/c + h - h*) and shows the pointwise
  domination |phi0| <= |h - h*| exactly on the reach; a Rayleigh
  reduction converts domination into the floor. The infimum is 1,
  approached at rate delta^2 by collapsing symmetric designs, not
  attained. Assumption A4's trust region (r <= 2/c) is therefore exactly
  what keeps the agent inside the floor's protection.
- **Refuted beyond (T9(ii))**: searching exactly where the proof stops
  found a genuine violation: a four-point design with one below-reach
  probe of weight 3e-4 attains ratio 0.8517, verified at 50-digit
  precision (mpmath) and frozen (design, anchor, and reference value)
  in `run_open1.py` section C-deep and check V9.2. The earlier 1.005x
  verdict was a search artifact (probe weights below the old scan's
  grid; an asymmetric near-anchor cluster the random search missed),
  recorded as the eleventh measurement-forced pivot.

Verification: four new checks V9.1-V9.4 (pointwise lemma at three
curvatures, the frozen witness + collapse rate, 20000 within-reach
random designs, the jet-Jacobian closed form): the numerical suite is
now 38/38. The theorem survived a three-skeptic adversarial review
(one real-analysis, one mathematical-statistics, one counterexample
hunter) plus an independent numerical validation agent (212,000
within-reach designs, min ratio 1.0021; pointwise lemma max violation
0.0 across four parameter sets; collapse rate slope 2.0008). Two gaps
the statistics skeptic found were fixed in the statement: the
unbiased/regular-estimator qualifier on the Cramer-Rao reading, and the
singular-design case (special two-point designs CAN estimate eps(h*);
their finite pseudo-inverse products obey the bound, e.g. R = 1.063 at
the pair {1.627, 2.127}, checked independently).

## 4. The complete derivation record is now in the paper (Appendix C)

All nine derivation documents (notation/assumption register, D0 model
and cost lemma, D1 saturation, D2 exchange rate, D3 minimax + the new
T9 reach section, D4/D5 design geometry, D6 safe certainty equivalence,
D7 crossover, D8/D9 ROI and instantiations) are rendered as a LaTeX
appendix, every formula cross-verified against the source documents by
a second agent pass, register numbering aligned (D0 = model doc, per
the register convention), no em dashes, house macros throughout.

## 5. Code quality and depth of results

- flake8-clean across `posk/`, `experiments/`, `tests/` (unused imports,
  ambiguous names, a broken line continuation in multibond.py); 9/9
  unit tests; behavior-preserving (full suite re-run: 36 rows, 0 FAIL).
- `run_open1.py`: hardened two-regime search (within reach vs global),
  the frozen witness with its 50-digit reference, and the corrected
  two-sided verdict; exit code now asserts the within-reach floor AND
  the witness's reproduction.
- New `experiments/run_stability.py` -> `results/STABILITY.md`: the
  horizon-stability audit of the tail-average metric (every cell at
  five perturbed horizons; worst spread 0.0062, tolerance 0.01, PASS).
- Registers updated: THEOREMS.md carries T9 (26 results),
  check accounting 38/38; VERIFICATION.md has V9.1-V9.4;
  OPEN-PROBLEMS.md's premise check is RESOLVED both directions and a
  new OPEN-5 (characterize the below-reach violation set) is opened;
  `derivations/04-minimax-lower-bounds.md` gained section 5 (T9).

## What was NOT changed

- The exchange-rate identity, minimax floors, design theory, agent, and
  all experimental headline numbers (36 rows, 0 FAIL; 12-seed baseline
  medians; tail-average metrics) are as in V1.
- The honesty apparatus: the DRIFT cell, the UCB lower-raw-regret
  admission, the one-seed Pareto flip, the real-data provenance
  caveats: all intact.
