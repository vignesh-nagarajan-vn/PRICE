# math-ai

The MATH-AI 2026 version of the PRICE paper.

**Venue.** The 6th Workshop on Mathematical Reasoning and AI (MATH-AI),
NeurIPS 2026, Atlanta. Double-blind, non-archival, 4-page body, deadline
6 September 2026 AoE, OpenReview group `NeurIPS.cc/2026/Workshop/MATH-AI`.

**Where it came from.** The ML x OR @ NeurIPS 2026 submission, rejected. The
LaTeX sources, figures, pipeline and derivation trees were copied from
`ml-or/PRICE-final/ml-or/submission-materials/`, the corrected 1 September
2026 build. Those source trees were not modified and
`ml-or/PRICE-final/CHANGES.diff` was left unapplied.

**What changed.** The mathematics did not. No experiment was re-run, no proof
was touched, no number was recomputed. The paper is now a case study in
machine-assisted mathematical research, led by Theorem T9 and the eleventh
measurement-forced pivot, with the PRICE theory as the substrate.
`MATHAI-CHANGES.md` lists every cut with its reason, in enough detail to
reconstruct the ML x OR version.

## Layout

```
paper/        working LaTeX and build output
supporting/   the code and derivation trees the paper points to
submission/   exactly what gets uploaded to OpenReview, and nothing else
```

`submission/` is generated. Never hand-edit a file inside it.

## Rebuild

```bash
cd math-ai/paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex && cd .. && python build_submission.py
```

`build_submission.py` copies `paper/main.pdf` into `submission/` and rebuilds
`submission/supplementary.zip` from `supporting/`, printing the SHA-256 of
each so the PDF copy can be confirmed byte-identical.

`paper/check.py` re-runs the page-gate, box-count, em-dash and anonymity
checks against the built PDF and log.

## Status

Measured on 4 September 2026: body ends page 4, references begin page 5,
10 pages total, 0 overfull boxes, 0 undefined references or citations, 0 em
dashes, no author field in the PDF metadata, and no author name, email or
repository URL in `supplementary.zip`. `SUBMISSION-CHECKLIST.md` has the
numbers and the one known gap.
