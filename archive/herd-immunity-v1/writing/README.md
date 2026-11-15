# Writing

Paper content in markdown, one file per section. LaTeX happens once at the end,
from these files. Nothing here is LaTeX.

## Page budget (9 pages main body)

**Measured 19 Aug 2026 from the drafted files**, not projected. Calibration:
1050 words of body prose per page, plus `0.03` page per display-math block,
`0.012` per table row, and `0.20` per figure. That words-per-page figure is
back-derived from the original projection in this table, so it is soft; the
overage below is large enough that no plausible calibration closes it.

| File | Section | Target | Measured | State |
|---|---|---|---|---|
| [`00-abstract.md`](00-abstract.md) | Abstract | 0.15 | 0.21 | rewritten |
| [`01-introduction.md`](01-introduction.md) | Introduction | 1.25 | 1.17 | **complete** |
| [`02-related-work.md`](02-related-work.md) | Related work | 0.75 | 1.21 | **drafted, 0.46 over its line** |
| [`03-model-and-framing.md`](03-model-and-framing.md) | Setup, private vs systemic | 1.25 | 1.21 | **drafted** |
| [`04-result1-effective-learners.md`](04-result1-effective-learners.md) | Theorem 1, the supply chain | 1.25 | 1.19 | **drafted**, proof moved out |
| [`05-result2-cadence-frontier.md`](05-result2-cadence-frontier.md) | Theorem 2 | 1.00 | 0.82 | **drafted**, proof moved out |
| [`06-result3-herd-immunity.md`](06-result3-herd-immunity.md) | Theorem 3, the substitution frontier | 1.25 | 1.60 | **drafted**, not compressible |
| [`07-result4-pigouvian-wedge.md`](07-result4-pigouvian-wedge.md) | Theorem 4 | 0.75 | 1.14 | **drafted**, steps 1 and 3 applied |
| [`08-supervision.md`](08-supervision.md) | Supervision from public prices | 0.20 | 0.11 | **drafted**, collapsed under step 2 |
| [`09-experiments.md`](09-experiments.md) | Six panels | 1.00 | 1.07 | **drafted** |
| [`10-limitations-conclusion.md`](10-limitations-conclusion.md) | Limitations, conclusion | 0.60 | 0.69 | **drafted** |
| | **Total** | **9.45** | **10.41** | working drafts; the submission is nine pages |

## Compression, and where the budget actually closed

Overflow is absorbed in a fixed order, decided in advance so it is not
renegotiated under deadline pressure:

1. Proofs and derivation sketches move to the appendix.
2. Section 8 collapses to two sentences.
3. Section 7's comparative statics move to the appendix.

**All three ran on 19 Aug 2026 and the budget still does not close.** They
recovered `0.27` of a page, from `10.68` to `10.41`: `0.067` from Section 4,
`0.088` from Section 5, `0.056` from Section 7 and `0.059` from Section 8. The
order was designed when the sections were unwritten, and what it reaches turns
out to be a small share of what they became. Moved text is marked
with an `APPENDIX` HTML comment in place rather than deleted, so every move is a
revert rather than a rewrite. Result sections 4 through 6 are not compressed and
were not.

**Closed 19 Aug 2026, in the LaTeX pass rather than here.** The files in this
folder are the working drafts and they still exceed nine pages. The submission
is [`../paper/main.tex`](../paper/main.tex), and it is nine content pages, which
is the only page count that has to be true.

The fit was made by cutting on the way into LaTeX, not by tightening these
files: proof bodies moved to the appendix, the worked tables in Sections 5 and 6
became inline numbers, the clustered companion became a row of the panel table,
and the appendix-bound material stayed in the appendix. No section was dropped
and no claim was weakened. [`../paper/README.md`](../paper/README.md) records
every cut and the reason for it.

These files stay long on purpose. They are the source the journal version and
the appendix are written from, and shortening them to fit a workshop limit would
throw away the material the appendix needs.

## Figures

Five figures in the body, one per result plus the headline. Figure budget is
tight at 9 pages, so each figure earns its place by being the falsifiable test
of exactly one closed form.

| Fig | Content | Section |
|---|---|---|
| 1 | The `(N, s)` phase diagram, measured `m_N` against the predicted boundary | 4 |
| 2 | The `(N_eff, K)` stability grid against predicted `K_max`, `s` contours overlaid | 5 |
| 3 | Herd immunity: measured stability against corrected fraction `rho`, predicted `rho*` marked | 6 |
| 4 | **The substitution frontier**, `(rho, s)` iso-stability curve. The poster figure | 6 |
| 5 | Over-adaptation: decentralized against socially optimal aggressiveness | 7 |

The amplification replication (experiment 1) is a table, not a figure. It is an
external validation checkpoint against a prior published run, and a table makes
the comparison to the published `1.74x / 3.16x` easier to check than a plot.

## Claims

Every numbered claim in the paper is tracked in
[`CLAIMS-LEDGER.md`](CLAIMS-LEDGER.md) with its status flag and its evidence.
Nothing ships at a status stronger than its ledger entry.

## Rules for this folder

- ASCII math, matching the plan of record and `../math/00-notation.md`.
- No em dashes. Run `prose-guard` before any commit that touches prose.
- Double-blind: no first-person reference to REFLEX or PEBSA, ever. Both are
  cited as ordinary third-party references.
- Every claim carries a status flag inline the first time it is stated.
