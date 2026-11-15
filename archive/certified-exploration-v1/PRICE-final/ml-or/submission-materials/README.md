# PRICE (the price of self-knowledge): complete paper repository

| Folder | What it is | Verification |
|---|---|---|
| `mlxor-derivations/` | The mathematical foundation: 9 derivation documents, the theorem register (26 results), full LaTeX appendix proofs, notation/assumption register, open-problems register (OPEN-1 now carrying a numerical premise check), novelty crosswalk, symbol->REFLEX map | 38/38 numerical checks + document-consistency suite, both in CI |
| `posk-pipeline/` | The ML architecture and pipeline: the SafeD-PerfGD agent (shaped, budgeted, safety-gated exploration + anchored structural estimation + pessimistically gated performative correction), environments, literature baselines (FD-PerfGD, ZO-PerfOpt, UCB-Grid), the 2^3 ablation grid, a second domain (LQ performative pricing), the d-dimensional multi-bond agent, the REFLEX real-data leg, and the paper figures | 36 verification rows (35 PASS + 1 deliberate out-of-scope DRIFT cell, 0 FAIL), 9 unit tests, OPEN-1 premise check, 10/10 real-data cells reproducing REFLEX's published run - all in CI |

The pipeline verifies the derivations end-to-end in a live
deploy-observe-fit-correct loop. **Eleven measurement-forced pivots are
recorded in place** (see `posk-pipeline/README.md`): the feedback floor,
the honest-gate timeline, the trust accounting, the operating-point
misspecification, the Pareto criterion for baselines, the
collinearity-as-T6 instance in the pricing domain, the steady-state
multi-bond protocol, the 75.8x real-data config trap, the fair-funding
ablation fix, the structure-proof-looking floor (OPEN-1), and the exact reach
(T9) whose proof exposed the earlier verdict as a search artifact. Each
sharpened the theory rather than patching it.

Headline additions beyond the original five experiments:

- **Baselines (E6).** No published baseline Pareto-dominates SafeD-PerfGD
  on median (final error, cumulative regret) over 12 seeds, one metric
  for every arm (300-step tail averages over the deployed path); the
  unsafe finite-difference gradient baseline pays >5x SafeD's median
  regret. Raw regret alone is won by UCB-Grid; deliberately reported,
  because certification time is a real cost and that purchase is the
  paper's thesis. The seed-by-seed Pareto count is reported in
  `results/e6_baselines.csv`.
- **Ablations (E7).** Anchor and gate earn their keep with
  theorem-predicted signatures (T7 short-horizon accuracy, L4 freeze
  discipline); for the design component the fairly-funded ablation mapped
  the boundary of the effect instead: T6's identification cliff is a
  support/amplitude phenomenon (it bites narrow priced jitter, E4, and
  collinear designs, E8, not full-support jitter at transit energy).
- **Second domain (E8).** LQ performative pricing: the exchange rate is
  exact in all four cells (A1 is global in an LQ model: zero drift), and
  the transplanted agent reaches the pricing performative optimum.
- **d dimensions (E10).** Gamma_PO^{-1/2}-shaped exploration beats
  isotropic at matched budget inside a running corrected loop on a
  curvature-dispersed universe (risk ratio 1.20, static F = 1.45), and is
  null on a flat control: the T5a allocation effect, isolated.
- **Real data.** The REFLEX calibration ported and validated cell-by-cell:
  10/10 (rating x regime) cells reproduce the published
  `calibrated_boundaries.csv` (h*, eps* = gamma, m), then extended with
  the paper's objects (gamma_PO, exchange rate, echo-chamber gap).
- **T9 and the exact reach.** The exchange-rate floor is structure-proof
  exactly within two curvature lengths of the anchor (proved: no design
  supported in [h* - 2/c, inf) beats it even knowing the family's form),
  and the reach is exact: a frozen witness with one below-reach probe of
  weight 3e-4 attains ratio 0.8517, verified at 50-digit precision. The
  earlier 1.005 structure-proof verdict was a search artifact (pivot 11).
- **Figures.** Seven paper figures, each mirroring an experiment's exact
  measurement (`posk-pipeline/results/figures/`).
