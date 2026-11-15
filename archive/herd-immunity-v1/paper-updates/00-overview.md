# Frontier upgrade: overview

**What this package is.** A complete, section-by-section outline of the
changes that would move "Herd Immunity and Learning Externalities in
Markets of Adaptive Models" from a strong workshop paper to a frontier
paper in its domain. It is deliberately an outline: it specifies what each
section must contain, what evidence standard each claim must meet, and
what infrastructure must exist, but it does not write the content. Every
assumption the outline itself relies on was verified against the
literature, the Mathlib source of truth, or the venue, and the
verification is logged in `05-assumption-verification-log.md`; the two
things that could not be fully verified from this environment are flagged
there rather than assumed.

**What "frontier" means here, concretely.** The paper already has one
genuinely new object and four closed-form results. What separates it from
a frontier paper is the evidence stack. The upgrade adds three pillars,
each of which is rare alone at this venue and (to the verified extent of
my search) unprecedented in combination for this literature:

1. **Measured results with statistical significance.** Today the paper
   has one measured panel and five deterministic derivation checks, with
   no inferential statistics anywhere. The upgrade adds a measured panel
   on real deployed models with bootstrap confidence intervals,
   permutation nulls, and a random-matrix analytic null, plus confidence
   intervals on every random-ensemble fraction the paper quotes, and a
   seeded robustness ablation with uncertainty bands. Spec:
   `03-statistics-plan.md`.
2. **Machine-checked mathematics (Lean 4).** The core spectral results
   are formalizable with what Mathlib actually contains today (spectral
   theorem for Hermitian matrices, Rayleigh quotient theory: verified);
   Perron-Frobenius and Bernstein concentration are NOT in Mathlib
   (verified), so the plan routes the formalizable results around them
   and honestly tiers the rest. The paper then carries a three-layer
   verification stack no competitor in this niche has: machine-checked
   algebra, assertion-based numerical certificates, and
   realized-dynamics agreement. Spec: `02-lean4-plan.md`.
3. **Ecosystem-native framing aligned to both EconML tracks.** The venue
   organizes itself around two directions (wording verified from three
   independent sources; the site itself is egress-blocked here and that
   is flagged): "Economic Tools for Machine Learning" and "Machine
   Learning Ecosystems with Interacting Models". The paper is a bullseye
   for the second and currently leaves its legitimate claim on the first
   unstated. Spec: `04-track-alignment.md`.

**The honesty constraints the outline enforces everywhere.**

- Nothing may be claimed as machine-checked unless the Lean file
  compiles and `#print axioms` is clean; the paper's claim language is
  specified per tier in `02-lean4-plan.md` §6.
- Nothing may be claimed as statistically significant without the test,
  the null, the n, and the interval stated; deterministic grid checks
  keep their (stronger) worst-case-departure language and are never
  dressed up as statistics.
- The existing evidence-status discipline (MEASURED / DRY RUN, ledger,
  certificates) is retained and extended, not replaced.

**Feasibility, stated up front.** The full upgrade is not a
pre-deadline project. `06-sequencing-and-page-budget.md` splits it into
what strengthens the 29 Aug submission (statistics on existing ensembles,
the measured-alignment panel with its nulls, first Lean tier if it
compiles in time, track vocabulary), what belongs in the camera-ready
(remaining Lean tier 1-2, the ablation suite), and what is the journal
version (concentration formalization, perturbation theory, the
supervision estimator's inference theory).

**File map.**

| File | Contents |
|---|---|
| `01-section-outlines.md` | The core deliverable: per-section change outline for all nine sections, abstract, and appendices |
| `02-lean4-plan.md` | Theorem-by-theorem formalization roadmap with verified Mathlib dependencies and claim-language rules |
| `03-statistics-plan.md` | The statistical-significance layer: tests, nulls, intervals, reporting standard, per-panel |
| `04-track-alignment.md` | Verified track wording and the element-by-element alignment map |
| `05-assumption-verification-log.md` | Every assumption this outline makes, how it was verified, and the two flagged unknowns |
| `06-sequencing-and-page-budget.md` | Deadline / camera-ready / journal split and the nine-page ledger |
