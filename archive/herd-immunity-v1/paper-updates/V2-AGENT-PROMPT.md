# Handoff prompt for the v2 implementation session

Paste everything below the line into a fresh session started in the repo root.

---

You are implementing **v2 of the EconML workshop paper** in `econml/paper/`.
Submission deadline is **29 Aug 2026**; today is 19 Aug 2026.

## Read first

1. `econml/paper/PAPER-V2-CHANGES.md` — the external review of v1, an assessment
   of each criticism against the code, and the space arithmetic. This is your
   specification. Read it completely before editing anything.
2. `econml/paper/README.md` — build commands, compliance rules, page-count
   verification.
3. `econml/paper/main.tex` — the paper itself, currently v1.

## Step 0, before any edit

Archive v1. Create `econml/paper/v1/` and copy `main.tex` and `main.pdf` into
it unchanged. Then edit `main.tex` in place as v2. v1 is frozen at commit
`486d213`.

## Scope decisions already made — do not relitigate these

- **R1 (measuring `s` on real models) is OUT.** The repo has no
  `transformers`/`peft`/LoRA infrastructure, the experimental stack is CPU-only
  and deterministic, and it would cost 0.30 pg the budget cannot fund. The
  abstract and Section 9 therefore keep their v1 framing. Do not add a panel,
  do not add a ledger row, do not change any status flag.
- **R4 is OUT and acting on it is harmful.** `main.tex` line 4 already reads
  `\usepackage[dblblindworkshop]{neurips_2026}`. The generic footer is what the
  style file prints in every track when `final` and `preprint` are unset.
  **Do not modify `neurips_2026.sty`** — it is grounds for desk rejection.
- **Do not cut any figures.** All five stay. All space comes from prose.
- **Do not compress Sections 4 to 6.**
- **Do not round any `[DRY RUN]` up to `[MEASURED]`.** The review singled out
  the paper's honesty about evidential status as rare. It is an asset.

## The work, in order

### 1. R2 — move the reduction derivation into Section 3 (~0.35 pg)

The crux of the paper is currently one asserted line in Section 3. The workshop
CFP requires the main text to be self-contained.

Source: `econml/math/derivations/01-alignment-spectrum.md` §1 "The reduction
lemma" — hypotheses (H1) through (H4), the statement of Lemma 1, and the proof.
Certified as C22 at agreement `5.6e-17`.

Render it as a numbered lemma in Section 3 with the four hypotheses stated
compactly, the `J = -m_1[(1-\kappa)I + \kappa R]` display, and a proof sketch of
about three lines. Note (H2) is standing assumption (A2) restated in the new
object's terms; say so rather than duplicating it.

### 2. R3 — the Narang containment statement (~0.35 pg)

The most likely fatal criticism, and the cheapest to defuse. Budget 0.35 pg, not
the 0.50 the review doc estimates — the trimmed version is a deliberate call.

Source: `econml/literature/LITERATURE-REVIEW-P2.md` entry **B7**. The material
is written; it has never been compressed into the containment statement a
reviewer wants. State (a) their condition, (b) ours, (c) the relation between
them. The load-bearing point already in B7: their coupling enters through scalar
sensitivity and Lipschitz constants, with no object representing *which
direction* each agent perturbs the environment, so two markets with identical
sensitivity constants and opposite alignment structure are indistinguishable in
their condition and have different stability in ours. Say plainly whether
Theorem 1 is implied by, strictly sharper than, or orthogonal to their result —
the reader should not have to take the paper's word for it.

Expand the existing Section 2 paragraph rather than adding a new section.

### 3. R5 and PEBSA — close to free

- **W4.** Section 9's dry-run defense currently claims a dry run establishes
  something "no algebra check covers". Too strong. Replace with what is true:
  the dry runs check that the closed forms were derived from the map we think
  they were. That is a check on the derivation, not evidence about dynamics. It
  has caught real errors; say that instead.
- **W7.** Section 7 currently ends with "The provenance channel". **Lead with
  it.** Verified: `N_eff` cancels completely from the wedge's ignored fraction —
  `t*/(t* + own marginal cost)` is exactly `(N-1)/N` at `chi = 1` regardless of
  `kappa` and `s`. So Corollary 7 is a generic commons result, while the
  provenance asymmetry (`dm_N/ds` linear in `N` and non-decaying, against a
  private adoption gain that does not grow with `N`) is the paper-specific
  result. Reorder to match. Pure reordering, no net space change.
- **PEBSA.** It gets one sentence in Section 2. Keep it to one sentence and add
  no second citation. Make the contrast do work: an exogenous-signal estimator's
  accuracy does not depend on the state of the system it measures, while the
  Section 8 estimator sharpens as the system approaches instability, so the two
  face opposite sample-complexity problems near the event of interest.

### 4. W8 — relocate (A5)

Verified: `R` is PSD with unit diagonal, so every eigenvalue is non-negative and
`1 + kappa(lambda_i - 1)` is increasing in `lambda_i`, putting the radius at
`lambda_max` whatever the sign pattern. Checked on 400 random alignment matrices
and the simplex at `N` in {3, 6, 12}, zero mismatches.

So (A5) is **not** needed for Theorem 1's radius. It is needed only for the
reading that the binding mode is the common one, which Lemma 5's share
interpretation leans on. Move it out of the standing assumption block and attach
it there. Section 5 already says it needs no analogue of (A5), which stays
consistent.

## Space budget — this is the hard constraint

v1 is exactly nine content pages with zero slack. Content ends on page 9;
references start on page 10. Every addition needs an equal subtraction, and
**figures are not available as a source of space**.

| Item | Direction | Estimate |
|---|---|---|
| R2 reduction derivation | needs | +0.35 |
| R3 Narang containment | needs | +0.35 |
| W5, Section 8 folded into the conclusion | frees | −0.15 |
| W11, meta-commentary trim | frees | −0.20 |
| W7 reorder, W4/W8 rewording | neutral | 0 |

That leaves roughly **0.35 pg short**. Take it from prose, in this order, and
stop as soon as the build fits:

1. Section 2's monoculture paragraph, compressed to three sentences (~0.10)
2. Section 9's per-panel prose, deferring to Table 2 (~0.15)
3. Section 3's "Two questions" paragraph, which largely restates the
   introduction (~0.08)
4. Section 7's defensive asides — "The choice is defended rather than assumed",
   "That is an assumption, stated as one, and the results turn on its sign and
   never its size" (~0.05)

W11's meta-commentary trim is the same register throughout: sentences that
comment on the paper's own rhetorical moves rather than making a claim. "which
is what the gate is for", "stated plainly", "we do not re-derive it". Cut the
commentary, keep the content.

## Build and verify

```bash
python econml/paper/make_figures.py
cd econml/paper && pdflatex main.tex && pdflatex main.tex
```

Two passes — cross-references to numbered theorems resolve on the second. No
bibtex; the bibliography is a `thebibliography` block inside `main.tex`.

**Verify the page count from a clean build, not an incremental one.** Delete
`main.aux` first. A stale `.aux` hid a three-line overflow during the v1 build.

```bash
pdftotext -f 10 -l 10 econml/paper/main.pdf - | head -2
```

That must print the References heading. If content has spilled onto page 10, the
paper is over the limit and is not done.

## Final pass

Reconcile the four status surfaces last, as its own pass, exactly as v1 did:
`main.tex`, `econml/writing/CLAIMS-LEDGER.md`, `econml/ml-contributions/CERTIFICATES.md`,
and `econml/STATUS.md`. Every status flag in the body must match the ledger.
Since R1 is out, no status should move — confirm that rather than assuming it.

Then update `PAPER-V2-CHANGES.md` to record what was implemented and what was
deliberately skipped, so the state of the folder is legible to the next session.

## If time runs short

**R3 before R2.** The review calls R3 the most likely fatal criticism and it is
the cheaper of the two.
