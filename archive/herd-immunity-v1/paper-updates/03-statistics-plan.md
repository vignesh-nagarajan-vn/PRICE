# Statistical-significance plan

Principle first, because it protects the paper's existing strength: the
paper currently has two kinds of empirical statements and the upgrade
adds a third. Each gets its own reporting standard, stated once in the
new Appendix L and used everywhere:

1. **Deterministic grid checks** (panels 2-6 vs closed forms): keep the
   worst-case-departure language (max error over the grid). Do NOT dress
   these in intervals; the checklist's existing defense of this is
   correct and stays.
2. **Random-ensemble fractions** (the 11.8% verdict-flip rate; the new
   coverage-law mismatch rates): each gets sampling measure, n, exact
   count, and a 95% Clopper-Pearson interval; one-sided exact binomial
   statements where a direction is claimed (e.g., zero conservative
   errors in 492 mismatches).
3. **Measured field estimates** (new panels): full inferential
   treatment below.

## Panel 7: measured alignment on deployed models (the centerpiece)

Outline of the required protocol, in the order it must be pre-committed
(write the protocol into Appendix L BEFORE looking at results; state
that ordering in the paper, it is cheap credibility):

1. **Data**: public per-item evaluation outputs across N models
   (candidate sources and their access/licensing checks are log entries
   V6-V7; first choice the Kim et al. ICML 2025 released data, fallback
   HELM per-instance outputs). Common-item intersection; minimum-item
   threshold per model pair stated in advance.
2. **Estimator**: per-model error-indicator vectors on common items;
   R-hat = pairwise error correlation (phi coefficient); report
   lambda_max(R-hat) and N_eff-hat = 1 + kappa(lambda_max - 1) left in
   its kappa-free form (report lambda_max itself; do not invent a kappa
   for field data; state this scoping).
3. **Uncertainty**: nonparametric bootstrap over items (models fixed),
   B >= 2000, BCa 95% interval on lambda_max and on the
   within-minus-between-provider mean-correlation gap.
4. **Null 1, permutation**: independently permute each model's error
   vector across items (preserves marginal error rates, destroys
   cross-model dependence); null distribution of lambda_max; report
   exceedance p as (count+1)/(B+1).
5. **Null 2, analytic**: the Marchenko-Pastur bulk edge / largest-
   eigenvalue benchmark for an N x n correlation matrix as the
   finite-sample floor, exactly the random-matrix hygiene the paper
   already cites (Laloux et al. 1999; Plerou et al. 2002); add the
   standard largest-eigenvalue reference (Johnstone 2001, Tracy-Widom
   edge) to the bibliography when this lands. The paper's own related-
   work paragraph anticipated this null; use it.
6. **Provider effect**: permutation of provider labels across models
   (preserves R-hat, tests the block structure); p-value for the
   within/between gap; this is the field analogue of the clustered-
   companion topology and should be said in exactly that sentence shape.
7. **Effect sizes over p-values in the prose**: the headline is
   lambda_max against N (e.g., "N models behave like ~L independent
   ones, CI [a,b], permutation null < c"), not a significance star.
8. **Honest-proxy caveat**, in the panel row and the limitations line:
   output-side error correlation, not response Jacobians; what it
   measures is alignment of failure directions.
9. **Robustness cells** (appendix): task-subset split-half agreement of
   lambda_max; threshold sensitivity (error definition); leaderboard 2
   replication if using Kim et al.'s two.

## Panel 8: nonlinearity robustness (realized, with uncertainty)

1. Saturating response (tanh scale lambda) in the reference environment;
   grid over lambda x {two topologies}; seeds per cell (>= 20).
2. Report measured-boundary error vs Theorem 2 as median and max with
   bootstrap band per lambda; the claim shape is monotone graceful
   degradation, stated as an interval statement, not a point.
3. Seed policy and cell counts in Appendix L; figure or four inline
   numbers in Section 8.

## Upgrades to existing ensemble statements

- 11.8% verdict-flip rate: n = 18313, count = 2157 -> report with 95%
  CP interval (~[11.3%, 12.3%]; recompute at build time, do not copy
  this outline's arithmetic); protocol already stated post-v5.
- Coverage-law mismatch (the new Section 6 sentence): rate with CP
  interval by kappa*s bucket (table in Appendix D addendum), plus the
  one-sided exact statement for the zero-conservative-errors direction
  (0 of 492: report the exact one-sided 95% bound on the conservative
  rate, i.e. <= ~0.6%; again recompute).
- Scalar-criterion failure rate (Section 4 add): define the ensemble,
  report rate + CP interval; certificate asserts the bound.
- Certificates: each new statistical claim gets an assertion-based
  certificate like the existing 525 (assert count, interval bounds, and
  seed), so the statistics inherit the same falsification discipline.

## What NOT to do (guardrails)

- No p-values on machine-precision agreement rows.
- No claiming the permutation p as evidence about response Jacobians
  (it is evidence about error-direction alignment; the caveat sentence
  owns this).
- No post-hoc threshold shopping on panel 7: the pre-committed protocol
  paragraph is part of the contribution.
- Do not let the statistics displace the worst-case certificates; the
  paper's differentiator is carrying BOTH regimes with a stated boundary
  between them.
