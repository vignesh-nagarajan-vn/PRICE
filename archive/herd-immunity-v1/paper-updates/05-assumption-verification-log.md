# Assumption verification log

Every assumption this outline package rests on, how it was verified on
25 Aug 2026, and its confidence. Anything not verifiable from this
environment is flagged, not assumed.

| # | Assumption used in the outline | Verification | Confidence |
|---|---|---|---|
| V1 | The workshop's two directions and their wording, logistics (Atlanta Dec 12/13, 9-page long format, 29 Aug AoE deadline, Sept 29 decisions) | Three independent search reads of econml26-workshop.github.io content (the domain itself is egress-blocked here), cross-checked against the NeurIPS 2026 workshops announcement (blog.neurips.cc) and the OpenReview group NeurIPS.cc/2026/Workshop/EconML; all consistent; deadline reconciles with NeurIPS's suggested 29 Aug AoE and the site's 30 Aug 11:59 UTC (same instant) | High; residual: load the site directly once before submitting (flagged in 04 §1) |
| V2 | "Reviewers not required to read beyond the main text"; "no theory track"; long/short split | paper/README.md's venue-check notes (recorded against the call on 19 Aug) plus consistency with V1 sources | Medium-high; same residual check as V1 |
| V3 | Mathlib HAS: spectral theorem for Hermitian matrices, eigenvalue machinery, Rayleigh quotient theory | Mathlib4 docs pages surfaced by search: Mathlib.Analysis.Matrix.Spectrum (and the mathlib3 ancestor linear_algebra.matrix.spectrum), Rayleigh-quotient results referenced in the same docs family | High for existence; exact lemma names/current signatures NOT verified (no Lean toolchain in this environment): Phase 0 of 02-lean4-plan.md exists precisely to close this |
| V4 | Mathlib LACKS: Perron-Frobenius (positive leading eigenvector at the spectral radius for irreducible nonnegative matrices) | The statement appears as an open target on the official Lean formalization leaderboard (lean-lang.org/eval/problems/...spectralRadius); corroborated by a 2026 formalization paper listing P-F as missing from Mathlib and engineering around it | High as of the search date; re-check at Phase 0 (Mathlib moves fast, and if it has landed, T7's workaround becomes optional) |
| V5 | Mathlib lacks Bernstein/sub-exponential concentration at the strength Appendix C needs | Search found no such results; only partial sub-Gaussian and moment machinery surfaced | Medium-high; same Phase 0 re-check; the plan does not depend on it (concentration is tier J regardless) |
| V6 | Kim, Garg, Peng & Garg (ICML 2025), 350+ models, error correlation concentrated within providers, exists and is the right methodological anchor for Panel 7 | PMLR v267 (kim25e), ICML poster page, arXiv 2506.07962, all consistent | High for the paper's existence and findings; its DATA release, license, and per-item granularity were NOT verified from here -> flagged: check the paper's repository before committing Panel 7 to this source; HELM per-instance outputs are the named fallback |
| V7 | HELM publishes per-instance predictions suitable as the fallback | Prior knowledge only; NOT re-verified this session | Medium; verify before relying |
| V8 | Marchenko-Pastur / largest-eigenvalue null is the standard hygiene for lambda_max of empirical correlation matrices, and the paper already cites the founding applications | Laloux et al. 1999 and Plerou et al. 2002 are in the paper's bibliography (read there); Johnstone 2001 (Tracy-Widom for largest eigenvalues) is standard and should be added when Panel 7 lands | High |
| V9 | No existing paper in this niche ships machine-checked proofs; formalized-econ precedents exist elsewhere (auctions/game theory) | Session searches for the niche (multiplayer performative prediction, monoculture, systemic risk of learning agents) surfaced no formalization claims; formalized-econ precedent knowledge is prior knowledge | Medium: absence of evidence from searches, not a literature review; the paper should claim "we are not aware of," not "first," unless a fuller search is run |
| V10 | Loewner-order lemmas sufficient for the congruence step (Prop A.7's formal version) exist in Mathlib | NOT verified; flagged as a Phase 0 audit item in 02-lean4-plan.md | Unknown |
| V11 | The commuting-Jacobians (shared-eigenbasis) family yields the claimed channel decoupling (Section 4 add-item 2) | NOT proved anywhere yet; the outline marks it to-prove-before-drafting. Plausibility: simultaneous diagonalization is standard; the coupling structure must be checked against (H3)'s sensing rule | To prove, not to assume |
| V12 | The coverage-law optimistic-direction finding (16% mismatch, 0/492 conservative, rates by kappa*s) | Computed this session by dense eigensolve on 4000-draw grids, two runs (adversarial package, evidence/stress_vaccine_law.py); the paper-side Perron-style proof of the direction is conjectured, marked attempt-before-drafting | High for the numbers; open for the proof |
| V13 | Statistical machinery named (item bootstrap + BCa, permutation tests, Clopper-Pearson, exact one-sided binomial) is standard and appropriate for the stated uses | Standard methods; choices justified by use-case in 03-statistics-plan.md (deterministic vs ensemble vs field regimes kept separate) | High; add textbook citations (Efron-Tibshirani; Good) to Appendix L when drafted |
| V14 | Baseline facts about the current paper (page gate, certificates 525 passing, harness behavior, figure defects, checklist state) | Directly executed/inspected in this session and the prior two reviews (builds, reruns, renders, timing) | High |
| V15 | EU AI Act (Regulation 2024/1689) is the correct referent for "regulation setting thresholds on model scale" | Prior knowledge of the compute-threshold provision for general-purpose models; citation added in candidate-v6 | High for existence; verify article number if the paper cites one (it should not need to) |

## The two flagged unknowns that gate work

1. **Panel 7's data source** (V6/V7): confirm per-item availability and
   license for the Kim et al. release, else fall back to HELM, before
   any Panel 7 drafting. This is the only gate on the centerpiece.
2. **Mathlib current state** (V3-V5, V10): the half-day Phase 0 audit
   gates all Lean claims. Nothing in the paper text should mention Lean
   until Phase 1 compiles.
