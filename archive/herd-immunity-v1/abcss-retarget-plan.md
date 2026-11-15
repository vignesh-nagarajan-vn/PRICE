# Plan: EconML paper at ABCSS 2026

Retarget of _Herd Immunity and Learning Externalities in Markets of Adaptive Models_ after the NeurIPS EconML workshop rejection. Written 18 Sep 2026.

## Status, 18 Sep 2026

A complete draft is in `paper/` and builds to 6 pages, inside the recommended 6 to 8. `submission/` holds the upload PDF, the form text and `UPLOAD.md`. It is ready to submit once the form opens on Oct 1.

Two things differ from the plan below. The measured-alignment panel is not in the draft; the Sep 22 go/no-go still decides whether it gets added. And the draft went in at 6 pages, not 8, because cadence and the wedge fit in one section without their figures. That leaves about two pages of room for the panel.

## The venue

**ABCSS 2026**, Application of Big Data for Computational Social Science, a workshop at IEEE BigData 2026 (Dec 14-17, Phoenix). Site: https://css-japan.com/abcss2026/

| Item | Value |
| --- | --- |
| Submission window | Oct 1 to **Oct 12, 2026** (extended from Oct 1) |
| Notification | Nov 1, 2026 |
| Camera-ready | Nov 14, 2026 |
| Length | 6-8 pages recommended, 10 max, references included |
| Format | IEEE conference template, 2-column, mandatory |
| Review | Single-blind |
| Proceedings | IEEE Xplore, indexed in Web of Science, Scopus, DBLP |
| Submission link | https://bit.ly/abcss2026submission |
| Organizers | Fujio Toriumi (Tokyo), Isamu Okada (Soka), Mitsuo Yoshida (Tsukuba), Yuya Shibuya (Tokyo) |

Listed topics include sociophysics and econophysics using big data, econometrics using big data, and business analytics. No past acceptance rate is published.

## What changes from the NeurIPS version

Three constraints drive almost every decision below.

**No free appendix.** The NeurIPS paper is 9 pages of body plus a 24-page appendix (33 pages total). Here everything, references included, fits in 10 two-column pages, and 8 is the target. The proofs cannot come along.

**Single-blind.** We can name ourselves, link the PRICE repo, and cite the REFLEX arXiv paper as our own. Full proofs and the 542 certificates move to the repo and get cited from the paper. That is how we survive the first constraint.

**The audience is computational social scientists, not ML theorists.** The workshop's word is "big data", and a paper that is all theorems and dry-run panels reads as out of scope. We need at least one result computed on real data. The epidemiology link should also lead, because sociophysics is on their topic list.

## The one piece of new work: the measured-alignment panel

Both the v1 external review and the 25 Aug internal review named this as the item that most strengthens the paper (see `../../archive/econml-neurips/STATUS.md`). For ABCSS it also buys the big-data fit.

The panel estimates the alignment matrix `R` and its leading eigenvalue `lambda_max(R)` from real per-item outputs of deployed models. It reports the effective crowding and the implied `N_eff` for a market built from those models.

For data, the first choice is the Kim et al. (ICML 2025) correlated-errors release, if it has per-item granularity and a usable licence. The fallback is HELM per-instance outputs, which are public.

The data check comes first and has a hard stop on **Sep 22**. If neither source works by then, we drop the panel. The paper then goes in on theory plus the one measured order-flow panel, and the framing changes below do the fit work alone.

The output is one figure (the eigenvalue spectrum, or `lambda_max` against the number of models from the same vendor), one new **measured** row in the panel table, and a short paragraph. Mean-similarity indices computed on the same data give a second, cheap result. The paper already claims those indices are wrong twice over, and this shows it on real models.

## Structure and page budget

A NeurIPS page holds roughly 0.75 of an IEEE two-column page, so the current 9-page body is about 7 IEEE pages before any cuts. The budget below is 8 pages of body plus about 1.5 of references.

| Section | Pages | Notes |
| --- | --- | --- |
| Abstract | 0.25 | Rewritten from scratch, about 150 words. |
| 1. Introduction | 1.0 | Open on a concrete market, not on the stability test. |
| 2. Related work | 0.5 | Add computational social science and econophysics work on herding, contagion and correlated behavior. Cut ML-only citations that don't earn a sentence. |
| 3. Setup | 0.75 | Dealers, one shared pool of order flow, the modulus `m`. Keep the plain-language reading of every symbol. |
| 4. Effective crowding (R1) | 1.0 | Theorem 1 plus the "fifty firms, one vendor" reading. Proof sketch only. |
| 5. Herd immunity (R3) | 1.25 | Promote to second position. This is the section ABCSS reviewers will remember: the imperfect-vaccine coverage law and the critical efficacy. Figure `fig_herd.pdf`. |
| 6. Cadence and the wedge (R2, R4) | 1.0 | Merge the two into one section of two short subsections. One figure between them, probably `fig_phase.pdf`. `fig_cadence.pdf` and `fig_wedge.pdf` move to the repo. |
| 7. Evidence | 1.5 | The measured order-flow panel (1.74x and 3.16x), the measured-alignment panel if it lands, and the dry-run table condensed. Status labels stay honest. |
| 8. Limitations and conclusion | 0.75 | Keep the supervision-from-public-prices result here, as the practical takeaway for a regulator. |
| References | 1.5 | IEEE numeric style. |

What gets cut from the body: all proofs (sketches stay), the mode-swap and strict-refinement witnesses, heterogeneous moduli, the concentration limit, the statistical protocols, and the checklist. Each goes to the repo with a pointer.

## Voice: make it read like the math-ai paper

The math-ai paper (`../../archive/math-ai/paper/main.tex`) reads like people wrote it. The current EconML draft reads like a compressed theorem register. The rules below come from what the math-ai paper actually does, so the rewrite has something concrete to check against.

**What the math-ai paper does**

**It tells you what happened, in order.** "A machine search believed a statement. A human proof attempt failed to reach the statement." Our version is the Theorem 3 story from `STATUS.md`. The strong-correction limit turned out optimistic and called about one configuration in eight stable when it wasn't. The exact fix turned out to be the imperfect-vaccine law with a critical efficacy. That story beats the result stated cold, and it belongs in the introduction.

**Every theorem gets a plain sentence right after it.** "Learning how your own deployment moves the world costs a fixed amount." Each of our four results needs one of these, written before the theorem is typeset.

**Sentence length varies.** Long sentences carry the argument, and a short one lands the point. The current EconML intro has several 60-word sentences in a row.

**It says what the paper is not.** The math-ai paper has a "What this paper is not" paragraph. Ours should say plainly that the heterogeneous panels are dry runs and why, near the front instead of only in the limitations.

**Examples come before notation.** "A dealer who quotes a wide spread sees different order flow than one who quotes a tight spread." Symbols get introduced only after the reader knows what they stand for.

**Numbers are exact and unadorned.** "ratio 0.8517, verified at 50-digit precision." No intensifiers next to them.

**What to remove from the current draft**

- Paragraphs that stack four defined terms before a full stop (the "Provenance and effective crowding" paragraph is the worst case).
- Italic run-in labels doing the work of a sentence (`\emph{Slow down:}`, `\emph{Correct:}`, `\emph{Diversify:}`). Write those as sentences.
- Parenthesized contribution lists crammed into one paragraph. Use the numbered `enumerate` the math-ai paper uses, three or four items, each one sentence.
- Internal vocabulary a reader never saw defined: "dry run", "port", "gate", "certificate" all need a one-line gloss the first time, or get replaced.
- AI-tell words and em dashes. Run the prose linter on the `.tex` source before every commit that touches prose.

**How to write it.** Rewrite each section from the outline and the math notes (`../math/`, `../../archive/econml-neurips/writing/`), not by editing the NeurIPS LaTeX line by line. Line editing keeps the old rhythm. Read each finished section aloud once. Any sentence you'd never say out loud gets rewritten.

## Folder layout

```
econml/ieee-abcss/
  PLAN.md            this file
  paper/
    main.tex         IEEEtran conference class
    references.bib
    figures/         only the figures that make the cut
  data-panel/        measured-alignment code and output, if the gate passes
  submission/        final PDF as uploaded
```

The NeurIPS files in `../../archive/econml-neurips/paper/` stay untouched as the record of that submission.

## Timeline

Today is Sep 18. 24 days to the Oct 12 deadline.

| Dates | Work |
| --- | --- |
| Sep 18-19 | Set up `paper/` with the IEEEtran template and a compiling skeleton. Paste in any NeurIPS reviewer comments we received, if any, as `reviews.md`. |
| Sep 19-22 | Data check for the measured-alignment panel. **Go or no-go on Sep 22.** |
| Sep 20-27 | Rewrite sections 1-5 in the new voice. Build the data panel in parallel if it's a go. |
| Sep 28-Oct 3 | Sections 6-8, abstract, related work. Merge the data panel into section 7. |
| Oct 4-5 | Split for peer review, same as for NeurIPS: each of us reads the other's sections cold. |
| Oct 6-9 | Revisions. Cut to page length. Check every number against its source (claim-trace). |
| Oct 10 | Final read aloud, prose linter clean, PDF passes IEEE PDF eXpress if the workshop requires it. |
| Oct 11 | Submit, one day early. |

## Open questions

- Does ABCSS require in-person presentation, and who registers? The site says the registration deadline is TBA.
- Is a paper already on arXiv fine for the workshop? The call is silent. Single-blind review suggests yes, but we should email abcss@css-japan.com before posting a new arXiv version.
- If the ML x OR paper also goes to an IEEE BigData workshop (BTSD, Oct 7), both would show up in the same proceedings. That's fine, but the two related-work sections should cite each other.
