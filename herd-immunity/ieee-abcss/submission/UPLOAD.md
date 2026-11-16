# Upload procedure: ABCSS 2026

Workshop: Application of Big Data for Computational Social Science, at IEEE BigData 2026 (Dec 14-17, Phoenix).
Submission window: Oct 1 to **Oct 12, 2026**. Notification Nov 1. Camera-ready Nov 14.
Submission link: https://bit.ly/abcss2026submission, which redirects to the IEEE BigData 2026 CyberChair workshop form, subarea `S07`.

The form does not accept uploads before Oct 1. Submit on Oct 11 at the latest, one day early.

## What goes where

| Form field | Source |
| --- | --- |
| Title | `form-fields.txt`, TITLE |
| Authors | Vignesh Nagarajan (Texas A&M University, vigneshn26@tamu.edu) and Shriraghav Ashok (UC Berkeley, sashok24@berkeley.edu), in that order, matching the PDF |
| Abstract | `form-fields.txt`, ABSTRACT, already stripped of LaTeX |
| Keywords | `form-fields.txt`, KEYWORDS |
| Paper PDF | `abcss2026-herd-immunity.pdf` |

`source.zip` is not uploaded now. It is the LaTeX source for camera-ready, and it compiles on its own with two `pdflatex` runs.

## Before uploading

1. Rebuild from source, so the PDF matches the committed `.tex`:

   ```
   python herd-immunity/ieee-abcss/build_submission.py
   ```

   The script stops if the build has errors, overfull boxes, undefined references, more than 10 pages, or a font that is not embedded.
2. Open the PDF and check page 1: both names, both affiliations, both emails. Review is single-blind, so names belong in the PDF.
3. Confirm the repository link in the PRICE reference resolves: https://github.com/vignesh-nagarajan-vn/PRICE. The paper points readers there for the proofs and the 542 certificates, so the repo must stay public through review.

## Checks already passed

| Requirement | Status |
| --- | --- |
| IEEE conference template, two-column | `IEEEtran` `[conference]` |
| At most 10 pages including references | 7 pages (6 to 8 recommended) |
| Paper size | US letter |
| Fonts | All embedded, Type 1 and TrueType, no Type 3 |
| Build | No errors, no overfull boxes, no undefined references |
| Prose | Clean under the repo's prose linter |
| No appendix (main-conference rule) | None; proofs live in the repo |
| Single-blind: names on the paper | Both authors, affiliations and emails on page 1 |
| No page numbers or headers | None |
| Copyright notice | Centered in the page 1 footer, ISBN digits as `XXXX` placeholders |
| Abstract | 214 words, no math or citations (IEEE asks for 150 to 250) |
| Index Terms | Present, alphabetical |
| Tables and figures | Table caption above, figure captions below, "Fig." used throughout as the template asks |
| References | IEEE numeric style via `IEEEtran.bst`; the repo entry uses the online format with an access date |
| PDF metadata | Title and authors set |

Rules checked against the ABCSS page (IEEE conference proceedings format, templates at https://www.ieee.org/conferences/publishing/templates.html, 10 pages, single-blind) and the IEEE BigData 2026 call for papers (IEEE Computer Society proceedings guidelines, references count toward 10 pages, no appendix). Checked 19 Sep 2026.

## Prior publication

No earlier version of this paper has appeared in any proceedings, so this is not a duplicate submission. Confirm with the organizers (abcss@css-japan.com) before posting a new arXiv version.

## Open items before Oct 12

- **Registration.** The site says the author registration deadline is TBA. IEEE BigData workshops normally require one author to register and present in person for the paper to appear in IEEE Xplore. Decide who goes.
- **IEEE PDF eXpress.** Usually needed only at camera-ready. Check the acceptance email for a conference ID.
- **Copyright notice.** The copyright line sits at the bottom of page 1 with the ISBN digits as `XXXX` placeholders. The acceptance email gives the exact text. Replace the placeholder in the footer definition above `\maketitle` in `main.tex` at camera-ready.
- **Measured-alignment panel.** Not in this version. The plan's Sep 22 go/no-go still stands. If the panel lands before Oct 11, it goes into Section VII and the paper grows toward 7 pages.
