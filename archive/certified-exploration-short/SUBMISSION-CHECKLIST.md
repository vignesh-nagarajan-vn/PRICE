# MATH-AI 2026 submission checklist

Replaces the ML x OR checklist at
`ml-or/PRICE-final/ml-or/submission-materials/SUBMISSION-CHECKLIST.md`, which
does not apply to this venue. Every item below states what was measured on
6 September 2026 on this build, not what is expected.

## Venue facts (read from the CFP at mathai-2026.github.io/cfp/, 4 Sep 2026)

| Fact | Value |
|---|---|
| Workshop | The 6th Workshop on Mathematical Reasoning and AI (MATH-AI), NeurIPS 2026, Atlanta |
| Body limit | 4 pages of content, unlimited references and supplementary |
| Camera-ready limit | 5 pages of content |
| Format | NeurIPS 2026 workshop template, `\usepackage[dblblindworkshop]{neurips_2026}` |
| Review | Double-blind; submissions must be anonymized |
| Archival | Non-archival; accepted papers listed on the workshop Papers page |
| OpenReview | `NeurIPS.cc/2026/Workshop/MATH-AI` |
| Deadline | 6 September 2026, AoE |
| Notification | 29 September 2026, AoE |
| Reciprocal reviewing | Required: at least one author per submission agrees to review, about three papers |
| Prior publication | Previously published work, including NeurIPS 2026, is not allowed; arXiv preprints and prior non-archival workshop papers are fine |

## Measured on this build

1. **Body ends page 4, references begin page 5.** Measured with `pdftotext`,
   not by eye. Page 4's last body line is the closing sentence of the
   Limitations paragraph; page 5 opens with the `References` heading.
2. **Total 13 pages.** Body 4 (pages 1 to 4), references 2 (pages 5 to 6),
   appendix 7 (pages 7 to 13). The CFP allows an unlimited number of pages for
   references and supplementary material, and the 9 pages following page 4
   also satisfy the stricter reading of a 10-page cap.
3. **Style option is `dblblindworkshop`**, in `paper/main.tex` line 8, with
   the official `neurips_2026.sty`. The Anonymous Author(s) block is intact.
4. **0 overfull boxes, 0 undefined references, 0 undefined citations, 0 LaTeX
   warnings.** Measured from `paper/main.log` after `pdflatex` then `bibtex`
   then `pdflatex` twice. Table 1 gained a `Verdict` header for its fourth
   column, which pushed it 1.8pt past the text block, so `\tabcolsep` is now
   4pt. One underfull vbox page-fill notice remains; it is a page-break report
   and the page renders without visible defect.
5. **Every section heading has content under it.** Checked by extracting the
   heading sequence from the PDF text and measuring the characters between
   consecutive appendix headings. The five appendices now run A Related work,
   B Assumptions and statements, C Proofs, D Verification rows, E
   Reproducibility, carrying 6690, 9749, 9817, 1794 and 2225 characters. Table
   1 stays pinned with `[H]` from the `float` package, under its own heading,
   preceded by a `\clearpage`, after an earlier build in which it floated past
   its section and left the section empty.
6. **0 em dashes in the extracted PDF text**, and 0 occurrences of `---`.
   Measured on the full `pdftotext` output, body and appendix.
7. **PDF metadata carries no Author field.** `pdfinfo` reports Title, Subject,
   Keywords and Author all empty; Creator is `LaTeX with hyperref`.
8. **Author names in the PDF text: 3 occurrences, all correct.** One is the
   bibliography entry for the prior REFLEX paper; the others are third-person
   in-text citations of that entry, in Appendix A and Appendix D. All are
   proper citation of prior work under double blind. No email address, no
   institutional affiliation, no repository URL appears anywhere in the text.
9. **`submission/main.pdf` is byte-identical to `paper/main.pdf`.** Confirmed
   by SHA-256, printed by `build_submission.py` on every run.
10. **`submission/supplementary.zip` is anonymous.** Extracted to a temporary
   directory (54 files) and grepped. `Vignesh`, `Nagarajan`, `Shriraghav`,
   `Ashok`, `nrvignesh`, `@gmail`, `github.com`: zero matches, case
   insensitive, across the whole extracted tree. No `__pycache__/`, no
   `.pytest_cache/`, no `.git` anything, no `.pyc`. The only URL in any file
   is the `https://matplotlib.org/` software tag that matplotlib writes into
   PNG metadata, in the seven figure files.
11. **`prose_lint.py` from `anthropic-skills:prose-guard` is clean** on all
    four sources, `main.tex`, `appendix_related.tex`,
    `appendix_statements.tex` and `appendix_proofs.tex`, at
    `--fail-on medium`.
12. **The bibliography is complete and every entry is cited.** 31 entries in
    `references.bib`, 31 `\bibitem` lines in `main.bbl`, 0 unused keys, 0
    undefined citations in `main.log`. The 4 September build printed 6
    references from 31 entries, leaving 25 orphaned, because the ML x OR
    retarget had cut the positioning prose and taken its citations with it.
    Nine machine-assisted-mathematics entries were added, with metadata
    verified against Crossref or arXiv rather than written from memory, and
    nine over-cited entries were then removed: see the note below.
13. **The headline numerical claim was recomputed independently.** The T9
    witness was rebuilt from the reported support and weights and evaluated at
    60 decimal digits outside the pipeline: `R = 0.851650472183`, matching the
    body. The reach boundary is `h* - 2/c = 0.51277`, so the `0.05` probe is
    below reach and the other three support points are inside it. An
    independent 200,000-design random search reproduced both directions, and
    the appendix's `R = 1.063` at the pair `{1.627, 2.127}` reproduces exactly.
14. **Every number in the body traces to a committed artifact.** Traced by
    hand against `posk-pipeline/results/RESULTS.md`, `OPEN1.md`,
    `REALDATA.md`, `STABILITY.md`, `full_run.log`, and
    `mlxor-derivations/THEOREMS.md` and `VERIFICATION.md`. One value was
    restated at the artifact's own precision rather than the ML x OR body's
    rounding: the known-`c` boundary ratios are now `0.3002`, `0.0425` and
    `0.0348`, as `OPEN1.md` section D reports them. No value was changed.
15. **The pipeline and derivation suites were not re-run.** They were executed
    and recorded on 1 September 2026 (38/38 derivation checks, 36 rows with
    0 FAIL, 9 unit tests, `run_open1.py` exit 0), and nothing in this retarget
    touches their inputs. This build re-narrates those runs; it does not claim
    to have reproduced them.

## Fixed in this build

`build_submission.py` excluded the `.log` suffix to strip LaTeX droppings, and
`supporting/` holds no LaTeX build, so the only two files it caught were run
records: `posk-pipeline/results/full_run.log`, which Appendix D names by path
as a provenance artifact, and `mlxor-derivations/verify/last_run.log`. The
shipped appendix therefore pointed at a file that was not in the archive. The
suffix is gone, a name-based guard replaces it, and the archive is now 54
files.

Theorem 2(i) said the within-reach bound is strict "except on one two-point
configuration", which reads as claiming equality is attained there. That
configuration does not identify the estimand, so the bound is infinite on it
and the inequality is strict without exception among estimable designs. The
body and the Appendix A statement now say so.

## Known gap, stated rather than papered over

The 1 September report records that
`mlxor-derivations/.github/workflows/verify.yml` and
`posk-pipeline/.github/workflows/ci.yml` were restored into the shipped
package. Neither file exists anywhere in this repository, so neither is in
`supporting/` or in `supplementary.zip`. Appendix D says CI runs in the
project repository and that the workflow files are not part of the anonymized
copy. If the files can be recovered before upload, drop them into
`math-ai/supporting/` and re-run `build_submission.py`.

## Before you submit

- [ ] Upload `submission/main.pdf` to the PDF field and
      `submission/supplementary.zip` to Supplementary Material. See
      `submission/UPLOAD.md`.
- [ ] Enter the real author list in the OpenReview author fields. Do not
      replace the PDF with a named build.
- [ ] Accept the reciprocal-reviewing commitment and name the reviewing
      author.
- [ ] Answer the prior-publication question as unpublished. The ML x OR
      version was non-archival and rejected, which the CFP explicitly permits.
- [ ] Submit before 6 September 2026 AoE.
