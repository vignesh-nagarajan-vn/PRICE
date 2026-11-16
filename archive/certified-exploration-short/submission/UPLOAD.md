# Upload procedure: MATH-AI 2026

Venue group: `NeurIPS.cc/2026/Workshop/MATH-AI`
OpenReview: https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/MATH-AI
Deadline: **6 September 2026, AoE**. Notification 29 September 2026 (AoE).

## What goes where

| OpenReview field | File in this folder |
|---|---|
| PDF (the paper) | `main.pdf` |
| Supplementary Material | `supplementary.zip` |

Nothing else in this folder gets uploaded. There is nothing else in it.

## Field by field

1. **Title.** `A Proof Attempt Told the Search Where to Look: A Case Study in Machine-Assisted Mathematical Research`
2. **Authors.** Enter the real author list in the OpenReview author fields. The
   PDF itself stays anonymous and must not be replaced with a named build.
   Review is double-blind; OpenReview hides the author fields from reviewers.
3. **Abstract.** Paste the abstract from `main.pdf` (page 1) as plain text.
4. **PDF.** Upload `main.pdf`. It is the anonymous build: `dblblindworkshop`
   option, Anonymous Author(s) block, no author field in the PDF metadata, no
   identifying URLs. The only author names in the file are the third-person
   bibliography entry for the prior REFLEX paper this work builds on and the
   two in-text citations of it, in Appendix A and Appendix D, which is correct
   practice under double blind.
5. **Supplementary Material.** Upload `supplementary.zip`. It contains the
   anonymized derivation tree (`mlxor-derivations/`) and pipeline
   (`posk-pipeline/`), 54 files, no author names, no emails, no URLs beyond a
   matplotlib software tag inside the PNG figures, no git metadata, no
   `__pycache__/`, no `.pytest_cache/`.
6. **Reciprocal reviewing.** The CFP requires that at least one author of each
   submission agree to review, roughly three papers. Tick that box and name
   the author who will serve. The submission is not complete without it.
7. **Prior publication.** Answer that the work is unpublished. Previously
   published work, including at NeurIPS 2026, is not allowed. This submission
   is clean: the earlier ML x OR @ NeurIPS 2026 version was non-archival and
   was rejected, and non-archival workshop papers and arXiv preprints do not
   count as prior publication under this CFP.
8. **Archival status.** Accepted MATH-AI papers are non-archival. No action is
   needed at submission time.

## After acceptance

Camera-ready allows up to 5 pages of content. Add `,final` to the
`\usepackage[dblblindworkshop]{neurips_2026}` options line in
`../paper/main.tex` and rebuild.

## Regenerating this folder

Do not edit anything in this folder by hand. From the repository root:

```bash
python math-ai/build_submission.py
```

That copies `paper/main.pdf` here byte for byte and rebuilds
`supplementary.zip` from `math-ai/supporting/`.
