# arXiv preprint build

`main.pdf` here is the de-anonymized preprint. The anonymous double-blind
submission build is the parent directory's `main.tex` / `main.pdf`, and it is
untouched. Both are built from the same body: `appendix.tex` and `checklist.tex`
are copies with the one checklist answer below flipped, and every source needed
to compile lives in this folder, so the directory builds standalone.

## What differs from the submission build

| | Submission | Preprint |
| --- | --- | --- |
| Style option | `[dblblindworkshop]` with `\workshoptitle` | `[preprint]`, notice line reads "Preprint." |
| Author block | `Anonymous Author(s)` | both authors, affiliations, emails, equal-contribution footnote |
| Hyperlinks | inert (`\hypersetup{draft=true}`) | live, `hidelinks` with `breaklinks` |
| PDF metadata | none | title, author, subject, keywords |
| Section 8 | code offered "as anonymized supplementary material" | repository URL in the sentence |
| Checklist Q5 | `[No]`, repository withheld to preserve the blind | `[Yes]`, repository named |
| Figure fonts | Type 3 (matplotlib default) | TrueType, `pdf.fonttype=42` |
| Engine | either | `\pdfoutput=1`, pdfLaTeX forced |

The workshop track is not claimed. `[preprint]` prints "Preprint." rather than a
venue line, which is the correct thing to post before a decision. On acceptance,
swap to `[sglblindworkshop,final]` (or `[dblblindworkshop,final]`) and restore
`\workshoptitle{Economics for Machine Learning}` for the camera-ready.

## Figures

The five figures are regenerated from the same result JSONs by the parent
directory's `make_figures.py`, with `matplotlib.rcParams["pdf.fonttype"] = 42`
set before the script runs. The data and the drawing code are identical; only
the font embedding changes. Matplotlib's default is Type 3, which arXiv accepts
but flags as low quality and which some viewers render poorly, so the preprint
carries TrueType subsets instead. The submission build keeps its original
figures, since that PDF is frozen.

## Links

The parent build makes hyperref inert to dodge a pdfTeX `\pdfendlink` abort on a
cross-reference straddling its page 2/3 break. The author block and the notice
line shift this build's layout enough that the straddle does not occur, so links
are live here. If a later edit brings the abort back, add
`\hypersetup{draft=true}` next to the other `\hypersetup` block; the printed
page is unchanged either way.

## Layout invariant

The README one directory up requires that the body end on page 9 and page 10
open with the references. This build holds it: 32 pages, body through page 9,
references from page 10.

## Build

```bash
latexmk -pdf main.tex
```

No undefined references, no overfull boxes, no Type 3 fonts, all fonts embedded.
One underfull `\vbox` from page breaking, which is cosmetic and which the
submission build has twice.

## Uploading to arXiv

`arxiv-submission.zip` in this directory is the upload, ready as it stands.
Rebuild it after any edit to the sources with:

```bash
python econml/paper/arxiv/package.py
```

It holds `main.tex`, `appendix.tex`, `checklist.tex`, `neurips_2026.sty` and the
five figures, stored at the archive root, which is the layout arXiv expects.
`main.pdf` is excluded because arXiv rejects a package carrying both TeX source
and a compiled PDF; this README and the packaging script are excluded as
repository documentation.

Everything arXiv's TeX Live does not already provide is inside the zip. The only
non-standard file is `neurips_2026.sty`, and the packages it pulls in
(`environ`, `natbib`, `geometry`, `lineno`) ship with TeX Live, as do the ones
`main.tex` requests directly (`inputenc`, `fontenc`, `hyperref`, `url`,
`booktabs`, `amsfonts`, `amsmath`, `amssymb`, `amsthm`, `nicefrac`, `microtype`,
`xcolor`, `graphicx`, `subcaption`).

No BibTeX pass is needed: the bibliography is a `thebibliography` environment
inside `main.tex`. The zip was verified by extracting it into an empty directory
and running three bare `pdflatex` passes, which is what arXiv's AutoTeX does; it
produced the same 32-page PDF with no undefined references.

Primary category `cs.LG`, cross-listed to `cs.GT` for the equilibrium and
welfare results and `cs.CY` for the governance ones. `econ.TH` is the natural
home for the Pigouvian material, and arXiv allows cross-lists to be added after
announcement, so it can go on once endorsement for the econ archive is in hand.

License: the arXiv.org perpetual non-exclusive license, matching REFLEX. It is
the reversible choice, since a later version can relax to CC BY but no version
can take a CC BY grant back.
