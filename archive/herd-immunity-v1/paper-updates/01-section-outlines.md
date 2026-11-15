# Section-by-section change outline

Format per section: **Current** (one line), **Keep**, **Change**, **Add**
(as an outline of what the new material must contain, not the material
itself), **Cut** (what pays for it), **Track hook**, **Tier**
(D = by the 29 Aug deadline, C = camera-ready, J = journal version).
Baseline is candidate-v6 from the adversarial package (all mechanical
fixes assumed adopted); page arithmetic is in `06-sequencing...md`.

---

## Abstract

- **Current**: v6 abstract (levers fixed, coverage-law error direction
  stated, measured replication as the close).
- **Keep**: the opening thesis sentence; the coverage-law sentence with
  its efficacy; the fifty-firms/one-vendor image.
- **Change**: the final beat. Today it closes on replicating the prior
  paper's amplification; frontier version closes on this paper's own
  measured object. Outline of the replacement close (one sentence each):
  1. the measured effective-learner count on real deployed models, with
     its interval and its null exceedance;
  2. the machine-checked core (count of results formalized in Lean 4);
  3. the replication sentence, demoted to a clause.
- **Cut**: the two-sentence overlap between sentences 1 and 2 (merge).
- **Track hook**: insert the word "ecosystem" once, in the sentence that
  currently says "the market it runs in".
- **Tier**: D (the close depends on the panel landing; if it does not,
  keep v6's abstract).

## Section 1: Introduction

- **Keep**: the single-agent-test framing; the three-lever paragraph;
  the contributions list structure.
- **Change**:
  1. De-duplicate the abstract's first sentence (verbatim twin, flagged
     in the adversarial review).
  2. Contributions list: append one sentence per the narrative fix
     (which contributions carry measured vs derivational vs
     machine-checked evidence), so the evidence stack is announced as a
     method, not discovered in Section 8.
- **Add** (outline):
  1. One clause naming the evidence stack: proofs, machine-checked
     algebra (Lean 4), assertion certificates, realized dynamics,
     measured data. One clause, not a paragraph.
  2. One ML-native instantiation sentence beside the dealer one
     (recommender platforms fine-tuning one foundation model over one
     attention pool), so the ecosystem reading arrives on page 1.
- **Cut**: the second epigram of the monoculture paragraph (per the
  writing review) pays for the additions.
- **Track hook**: "ecosystem-level" vocabulary in the what-can-be-done
  paragraph; the paradigm-limitation sentence ("single-agent evaluation
  cannot certify a market of models") reworded once in Track-1 terms
  (a limitation of the prevailing evaluation paradigm).
- **Tier**: D.

## Section 2: Related work

- **Keep**: the three-dispatch structure and the v5 additions
  (Piliouras-Yu, Li-Yau-Wai, Kim et al.).
- **Change**: add the one-sentence cluster map as the section's opening
  (three bordering literatures: static monoculture, multiplayer
  performative dynamics, systemic risk outside learning), per the
  writing review.
- **Add** (outline):
  1. One sentence on the contemporaneous 2026 finance thread (the two
     arXiv preprints), added only after reading them in full; the
     dispatch axis is method (calibrated simulation / aggregate adoption
     model) vs this paper's closed-form spectral boundary with priced
     instruments. Flagged verify-before-citing in the log.
  2. If the Lean pillar ships: one sentence locating the formalization
     contribution relative to formalized-economics work (formalized
     game-theory/auction precedents exist; a formalized stability theory
     of interacting learners does not, to the extent searched). Cite the
     precedent landscape honestly rather than claiming a first without a
     search trail; the log records what was searched.
- **Cut**: nothing further; this section is already tight post-v5.
- **Tier**: D for the map sentence; C for the additions.

## Section 3: Setup

- **Keep**: everything through the reduction lemma; (H1)-(H4) statement;
  the own-channel-sensing motivation.
- **Change**:
  1. State (H2)/(H4) by pointer to the appendix, keeping (H1)/(H3) at
     full strength in the body (writing review; frees ~4 lines).
  2. The "two questions" paragraph absorbs the Track-1 sentence from the
     introduction if space forces a choice between them.
- **Add** (outline):
  1. A forward pointer, one clause, to the new shared-eigenbasis family
     (below, Section 4 add-item 2), so (H1)'s scope limitation arrives
     with its partial repair in the same breath.
- **Tier**: D (pointers), C (the family itself).

## Section 4: Result 1 (effective number of independent learners)

- **Keep**: theorem, anchors, containment proposition, supply-chain
  paragraph, mean-index paragraph.
- **Change**:
  1. The mean-index paragraph gains one sentence reporting the
     scalar-criterion failure *rate* on a random ensemble with its
     confidence interval (statistics plan §4), upgrading the witness
     from existence to magnitude.
- **Add** (outline):
  1. **The measured panel's headline lands here, one sentence + pointer
     to the Section 8 row and figure**: measured lambda_max on real
     models, its bootstrap interval, its permutation-null exceedance,
     and the within/between-provider split. The full treatment lives in
     Section 8; Result 1's text gets exactly one sentence so the
     theorem-to-measurement link is explicit where the object is defined.
  2. **Shared-eigenbasis reduction family** (new proposition, appendix
     proof): the reduction is exact not only under (H1) but for the
     family where all response Jacobians commute (shared encoder /
     shared representation case); outline: statement, one-line proof
     idea (simultaneous diagonalization decouples the d channels into d
     independent N-firm problems; the radius is the max over channels),
     and one sentence on what it covers (the representation-homogeneity
     story) and what it still excludes. This is the single cheapest
     substantive theory extension and directly answers the (H1)
     criticism. Verify the claim before drafting: the commuting case
     must actually yield the stated decoupling (the log flags this as a
     to-prove, not an assumption).
  3. If Lean tier L1 compiles: margin marker on the theorem (the
     appendix K table carries the mapping).
- **Cut**: the four-anchor prose compresses to three anchors plus
  pointer (the simplex anchor's derivation is appendix material
  already).
- **Track hook**: this section is the Track-2 core; the measured
  sentence is what makes "ecosystems with interacting models" literal.
- **Tier**: D (items 1, 3 conditional), C (item 2).

## Section 5: Result 2 (crowding-cadence frontier)

- **Keep**: theorem, critical crowding, supply-chain window table,
  staleness sentence (v5 form).
- **Change**: the operational reading gains its practitioner sentence
  (the one unilateral lever, stated as advice with the formula), per the
  narrative review.
- **Add** (outline):
  1. One sentence + appendix pointer for the **c-sensitivity ablation**
     (three contraction values; shows the frontier's shape is not an
     artifact of c = 0.8).
  2. If Lean L1 compiles: the cadence theorem is the easiest
     formalization target (scalar algebra); margin marker.
- **Cut**: nothing; this is the tightest section.
- **Tier**: D (sentence), C (ablation row).

## Section 6: Result 3 (herd immunity, substitution)

- **Keep**: exact-root theorem, optimistic-limit paragraph, imperfect
  vaccine law, critical efficacy, synthesis, public-good reading.
- **Change**:
  1. The v6 abstract's new claim (law optimistic-never-conservative away
     from the corner) gets its body sentence here with the grid numbers
     and their Clopper-Pearson interval, plus a new certificate ID.
     (The adversarial package's `stress_vaccine_law.py` is the
     prototype; the paper text states the finding, the appendix states
     the protocol.)
  2. If the one-line Perron argument for that direction goes through
     (technical review 3.1.6), the sentence upgrades from grid finding
     to corollary; attempt before drafting, do not assume.
- **Add** (outline):
  1. Free-riding paragraph gains the forward stitch to Section 7 (the
     wedge as the instrument that repairs exactly this under-supply).
- **Cut**: "un-blinded" terminology unified to "corrected" (writing
  review; frees nothing but removes friction).
- **Track hook**: the correction mandate doubles as a Track-1 statement
  (an economic mechanism that improves learning); one clause says so.
- **Tier**: D.

## Section 7: Result 4 (Pigouvian wedge)

- **Keep**: welfare object, share lemma (v5 scoped form), wedge theorem,
  over-adaptation, provenance channel.
- **Change**:
  1. Add the mode-truncation scope sentence near the welfare-object
     paragraph (both problems price only the binding mode; a shared
     truncation), per adversarial ledger C15.
  2. Panel 6's welfare-loss number (not just the aggressiveness gap)
     enters the results sentence; the bisection already computes it.
  3. Section ends on the provenance asymmetry; the Weitzman non-answer
     moves mid-paragraph (writing review).
- **Add**: nothing new; this section's frontier upgrades (asymmetric
  wedge, endogenous vendor choice) are journal-tier and stay in the
  deferred register with one clause sharpened to say the participation-
  ratio observation already does the technical work.
- **Tier**: D (1-3).

## Section 8: Experiments (the section that changes most)

- **Keep**: the status taxonomy, the panel table, the honest port-gate
  paragraph, the protocol pointer.
- **Change**:
  1. Opening sentence: verdict-first rewrite (writing review) plus the
     internal/external-validity reframe replacing "establishes nothing
     about a market" (narrative review).
  2. Table gains a **column for evidence class** with four values:
     measured (order-flow), measured (field data), realized (reference
     environment), certified (ensemble with CI). This resolves the
     precision-regime mixing flagged in the adversarial review and makes
     the statistics legible in one glance.
  3. Every ensemble-derived number in the table gains its n and 95% CI;
     every deterministic grid check keeps max-departure language.
- **Add** (outline of the two new panels; specs in `03-statistics-plan.md`):
  1. **Panel 7, measured alignment on deployed models** (the decisive
     one): data source and licensing check; error-indicator construction
     on common items; R-hat; lambda_max with item-bootstrap CI;
     permutation null and analytic (Marchenko-Pastur edge) null;
     within/between-provider decomposition with permutation p-value;
     fitted shared fraction s-hat; one figure (provider-ordered heatmap +
     null-vs-observed inset); honest proxy caveat in the row itself;
     status tag: measured (field data).
  2. **Panel 8, nonlinearity robustness**: saturating response sweep in
     the reference environment; seeds x configs; measured boundary vs
     Theorem 2 prediction with bootstrap band; one small figure or four
     inline numbers; status: realized, with uncertainty.
- **Cut**: the "why the rest are not measured" paragraph compresses by
  two lines (the port story is fully told in the appendix; the body
  keeps the residual number and the decision).
- **Track hook**: Panel 7 is the "ecosystems" evidence; say the word in
  its row caption.
- **Tier**: D (panel 7, opening rewrite, CI column), C (panel 8 if the
  deadline crowds it).

## Section 9: Limitations and conclusion

- **Keep**: the limitations inventory and its candor; the conclusion's
  thesis sentence.
- **Change**:
  1. Limitations gains one line each for: the proxy nature of the
     measured alignment (output-side error correlation, not response
     Jacobians); the same-platform scope of "deterministic"
     (adversarial C14); what is and is not machine-checked (pointer to
     Appendix K's table).
  2. Conclusion: the EU AI Act citation stays (v6); the final sentence
     upgrades to name the three evidence layers the paper now carries.
- **Tier**: D.

## Appendices

- **Keep**: A-J as structured, including the certificate inventory and
  deferred register.
- **Add** (outlines):
  1. **Appendix K: machine-checked results.** Table mapping paper result
     -> Lean theorem name -> Mathlib version pin -> axioms output
     (`#print axioms` clean). One paragraph on scope: what is
     formalized (the algebraic/spectral layer), what is not
     (concentration, perturbation, anything Perron-Frobenius-dependent
     beyond the elementary nonnegativity trick), and why (verified
     Mathlib gaps, cited to the plan in the artifact). Claim-language
     rules from `02-lean4-plan.md` §6 apply verbatim.
  2. **Appendix L: statistical protocols.** One subsection per
     inferential claim: estimator, resampling scheme, null construction,
     n, seed, interval method. The 11.8% and the vaccine-law 16% move
     their protocols here (from D) and gain intervals.
  3. **Appendix D addendum**: the vaccine-law error map (mismatch rate
     vs kappa*s table) and its certificate ID.
  4. **Appendix J updates**: shared-eigenbasis family moves from
     deferred to done when Section 4 add-item 2 lands; formalization of
     the concentration layer enters the register as a named journal
     item.
- **Tier**: K skeleton D (with whatever L1 has compiled), L at D for the
  ensembles + panel 7, rest C.

## Checklist (must be revisited; it is an evidence surface)

- Q3 (proofs): answer unchanged; justification gains the Appendix K
  clause if any Lean lands (checked, not overstated).
- Q7 (error bars): flips from No to **Yes** once panels 7-8 and the
  ensemble CIs exist; the justification outline: deterministic grid
  checks keep worst-case language; stochastic estimates carry stated
  intervals; both are defined in Appendix L. This flip removes the
  reviewer-visible "No" that currently sits mid-checklist.
- Q4/Q6: add the panel-7 data source, license, and access date.
- **Tier**: D.
