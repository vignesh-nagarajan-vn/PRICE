# Paper build

The submission itself: `main.tex` compiled against the official NeurIPS 2026
style files, plus the mandatory paper checklist.

`main.tex` is **v6**. v1 to v5 are archived unmodified side by side in
[`archive/`](archive/), v1 frozen at commit `486d213` and each later one at the
state it held before the pass that followed it. The version history below records
what each pass changed and, more importantly, the two review items that keep
recurring and must not be acted on.

```bash
python econml/paper/make_figures.py     # figures, from the committed result JSONs
cd econml/paper && pdflatex main.tex && pdflatex main.tex && pdflatex main.tex
```

**The appendix carries the proofs, and it is in this PDF.** The NeurIPS 2026
main track handbook, which the workshop's call defers to for format, puts paper
content, references, appendices and the checklist in a single PDF and reserves
the separate ZIP for data and source code. Appendices do not count against the
nine content pages. So every numbered result in the body is proved in
`appendix.tex`, not promised to a supplementary bundle that may have no upload
slot at this venue. Appendices A to F are the mathematics, G is the deferred
supervision material, H is the certificate inventory, I is the experimental
protocol, J is the register of what is not proved and K is the statistical
protocol behind the paper's one inferential number.

**Three passes.** v1 needed two; v2 needs a third because Lemma 1 shifts the
theorem numbering that the cross-references resolve against. No bibtex run: the
bibliography is a `thebibliography` block inside `main.tex`, since 27 entries do
not justify a `.bib` and a manual list cannot go stale against one.

**`\hypersetup{draft=true}` is deliberate.** A cross-reference link straddling
the page 2/3 break aborts pdfTeX with "\pdfendlink ended up in different nesting
level than \pdfstartlink". Neither `breaklinks` nor a larger `pdf_mem_size`
avoids it, and the layout that triggers it is the layout that fits nine pages.
Making hyperref inert leaves the printed page identical and costs only
clickability, which a double-blind submission does not need. **Remove the line
for the camera-ready**, where the layout differs anyway.

## Files

| File | What it is |
|---|---|
| `main.tex` | The paper |
| `appendix.tex` | The technical appendices: complete proofs, certificates, experimental specifications |
| `checklist.tex` | The NeurIPS checklist, all 16 questions answered |
| `neurips_2026.sty` | Official style file, **unmodified** |
| `checklist_template.tex` | The blank checklist as shipped, kept for diffing |
| `make_figures.py` | Renders the five figures from `../ml-contributions/experiments/results/` |
| `figures/*.pdf` | Generated, vector |
| `main.pdf` | The compiled submission |
| `archive/v1/` to `archive/v5/` | Frozen earlier versions, kept for diffing. Not part of the build |

## Compliance

**Format.** `\usepackage[dblblindworkshop]{neurips_2026}` with `\workshoptitle`,
which is the double-blind workshop track. The style file is used as shipped;
tweaking it is grounds for desk rejection. Options `final` and `preprint` are
both omitted, so the build anonymizes itself and adds line numbers for review.

**Page count.** Nine content pages, ending with the conclusion. References, the
appendix and the checklist do not count against the limit. As of v5 the
conclusion ends part-way down page 9 and the References heading follows it on
the same page, which is the compliant form with a little slack; through v4 the
body filled page 9 exactly and References began on page 10. Verify after any
edit:

```bash
pdftotext -f 10 -l 10 econml/paper/main.pdf - | head -2
```

That should print references, never body prose. If a section heading, a
paragraph of the conclusion or a figure appears on page 10, the paper is over.

**Checklist.** All 16 questions answered with a justification each, the
instruction block deleted and the section heading kept, as the template
requires. Answers: yes to 1, 2, 3, 4, 6, 7, 8, 9, 10, 12; no to 5; not
applicable to 11, 13, 14, 15, 16. The one `no` is deliberate and justified in
place: question 5 is `no` because the repository names an author and is
withheld until the paper is de-anonymized. **Question 7 flipped to `yes` in
v5.** The panels are still deterministic and still report worst-case departure
rather than error bars, which is the stronger statement and stays; what changed
is that the paper's one random-ensemble fraction now carries its sampling
measure, its n, its exact count and a Clopper-Pearson interval, so the honest
answer to the question as asked is yes with both standards stated in
Appendix K.

**Double-blind.** No author block, no repository URL, no acknowledgments. PDF
metadata carries no title, author, subject or keywords. Figure files are
generated from result JSONs and carry no local paths. No sentence positions
REFLEX as the authors' own work. PEBSA was dropped in v4 and restored in v5,
so two entries again share an author with the submission; both are cited in the
third person, which is what the rule asks.

**On the base paper carrying author names.** REFLEX is cited in full, with
authors, which puts a name shared with this submission's author list into the
bibliography. That is the plan of record's instruction and it is the right call:
the rule under double-blind is that self-citation happens in the third person,
not that it is scrubbed. A reference stripped of its authors is the more
revealing artifact, because it is visibly anomalous next to the ordinary
entries and reads as a paper hiding its own lineage. The submission cites it the
way any third party would and lets the third-person prose carry the blind.

**v4 dropped the second one, and v5 brought it back.** PEBSA supported a single
contrast in the systemic-risk paragraph that nothing else depended on, so v4
removed it at the cost of one sentence. v5 restored the contrast, so PEBSA and
REFLEX both share an author with the submission. This stays policy-compliant for
the same reason REFLEX does: third-person citation, no URL, no claim of
authorship.

**No entry carries a URL**, REFLEX included. It briefly did, and a DOI trailing
the one reference sharing an author with the submission is a worse tell than the
name itself. The bibliography is uniform, `Authors. Title. Venue,
vol(issue):pages, year.`, and anything reintroducing a link to one entry has to
add it to all twenty-three.

## The artifact URL

The public repository is `github.com/vignesh-nagarajan-vn/PRICE`. **It is not in
the submission**, and the line that would add it sits commented out in
`main.tex` next to the sentence it belongs to. The URL contains an author name,
so including it under double-blind review would break anonymity and invite desk
rejection. Uncomment it for the camera-ready version, when the paper is
de-anonymized anyway.

The live sentence promises code, derivations and certificates to reviewers as
anonymized supplementary material, which is what a double-blind submission may
say, and the checklist's question 5 states the same arrangement.

## What did not make the paper

The build folder holds more than nine pages of drafted content. What was cut
from `../writing/` on the way into LaTeX, and why:

- **Proof bodies.** Sketches stay inline and complete proofs sit in the
  appendix, where they cost no content pages. A workshop reviewer wants the
  mechanism and the assumptions in the body, not the algebra.
- **The worked tables in Sections 5 and 6.** Reduced to inline numbers, which
  cost a fifth of the space and carry the same three values.
- **The clustered-companion figure**, folded into a row of the panel table.
- **The supervision material's longer form**, collapsed to two sentences before
  the LaTeX pass and, in v2, folded out of its own section into the opening
  paragraph of the closing one.
- **The free-riding diagnostic and the supervision panel**, both appendix
  material, and both fourth and first in the de-scope order respectively.
- **The provenance paragraph and panel 6's method**, compressed in v4 against
  Appendices F and I, which carried both close to verbatim.
- **The anchors table**, cut in v3. Appendix B derives all three corner anchors
  and Appendix C the supply-chain row, both in more detail than the table gave,
  so the body states the four values inline and points there. This is what paid
  for v3's related-work additions, and it removed the build's only overfull box.

Nothing cut carries a claim the paper still makes. The claims ledger in
`../writing/CLAIMS-LEDGER.md` remains the authority on status, and every flag
in the body matches it.

## Venue, checked against the call for papers

`\workshoptitle` reads "Economics for Machine Learning", the string the call
instructs submissions to use. An earlier draft had it backwards as "Machine
Learning and Economics", corrected 19 Aug 2026, and it carried a trailing
"(EconML)" until v3 dropped it on 20 Aug 2026 to match the call exactly. The
string prints only at camera-ready, so the submission build is unchanged either
way.

The same source confirms the rest of the build. Long papers are capped at nine
content pages with figures and tables included, which is what this compiles to.
Review is double-blind and the call names `dblblindworkshop` as the required
option, which is the one in use. The deadline is 29 Aug 2026 anywhere on earth,
and the workshop runs 12 or 13 Dec 2026 in Atlanta.

The title reaches the page only in the camera-ready footer, since the submission
build prints the generic notice instead. Getting it right now means the
camera-ready needs no edit beyond adding the `final` option.

## Version history

`main.tex` is v6. Earlier versions are frozen in `archive/`.

| Version | What it changed |
|---|---|
| v1 | First full build, nine content pages, reviewed externally on 19 Aug 2026. Verdict: accept as poster |
| v2 | Acted on that review. The reduction lemma moved into the body, the containment against Narang et al. was stated, and measuring the shared-model fraction `s` on real models was ruled out for lack of infrastructure and page budget. Supervision folded into the closing section, leaving nine sections |
| v3 | Appendix typeset into the same PDF. The abstract's herd-immunity law gained its fully-shared-limit qualifier, panel 1 stopped being called external validation, Peng and Garg (2024) and Jagadeesan et al. (2023) were added, and `\workshoptitle` was matched to the call. The anchors table paid for the space |
| v4 | Cadence terminology matched to what the theorem proves, the containment turned into Proposition 3 with a witness pair, the wedge's exchangeable-symmetric scope stated in the body, (H3) motivated with a concrete market, and the base paper called a preprint rather than published. Paid for by a prose pass against appendix duplication |
| v5 | The 27 Aug 2026 pass, in five parts: the citation gap closed (Piliouras and Yu, Li/Yau/Wai, Kim et al.), the wedge's orthogonal-corner scope slip corrected and the notation unified to `rho_c`, an exact interval put on the one random-ensemble number with a new certificate and a new Appendix K (checklist Q7 flips to yes), the workshop's two directions spoken once each and the wedge figure moved beside Result 4, and the dry-run framing reworded to internal against external validity with the emphasis budget cut from 23 bolds to 7. Paid for throughout by compressing against the appendices, never by dropping a claim. Then the submission audit's F1--F10 and C5: `lambda_max` renamed from the inverted "effective number of independent learners" to **effective crowding**, firms per independent model; the abstract's substitutes repaired to correction and diversity; figure 3's chord artifact fixed; the machine path scrubbed from three result JSONs |
| v6 | Retitled to name the shared-model mechanism as the setting rather than a scope restriction, keeping "Markets". The abstract rewritten on Shriraghav's upgrade draft (`../writing/11-abstract-updates.md`): domain-grounded opening, `m_N` named as the feedback reproduction number, and the emphasis rebalanced so all four results appear, with the preprint attribution and "bit for bit" kept on the one measured number. 247 words, under the 250 limit |

### Two review items that must not be acted on

Both have now been raised by more than one external review. Neither is a bug.

**The page footer.** It reads "Submitted to 40th Conference on Neural
Information Processing Systems (NeurIPS 2026). Do not distribute.", and reviews
read that as proof the workshop option is missing. It is not. The call instructs,
verbatim, `\usepackage[dblblindworkshop]{neurips_2026}` and
`\workshoptitle{Economics for Machine Learning}`, which is what lines 4 and 5
carry. In `neurips_2026.sty` the string holding the workshop title is used only
inside `\if@neuripsfinal`, so with `final` and `preprint` unset the style file
prints the generic notice in every track. The workshop title appears at
camera-ready. **Do not modify the style file**; that is grounds for desk
rejection, which is the outcome the "fix" claims to prevent. The only other
workshop option, `sglblindworkshop`, sets `\@anonymousfalse` and would break the
blind.

**Cutting the experiments section because "theory papers owe no experiments".**
There is no theory track. The call splits submissions by length only, long at
nine content pages and short at four. It also lists empirical evaluation of
theoretical models among the directions it encourages, and states that reviewers
are not required to read beyond the main text, so moving Section 8 into the
appendix would work against both.

### What v4 rewrote, and why the page count did not move

The body was already full at nine pages, so Proposition 3, the (H3) paragraph
and the wedge's scope sentence had to be paid for. They were paid for by removing
material the appendices already carried rather than by cutting claims: the
provenance paragraph, panel 6's bisection method, the clustered-alignment
working, and the simplex argument were each stated twice. Two sentences in the
monoculture paragraph said the same thing. Dropping PEBSA removed a third.

Content now ends at the bottom of page 9 rather than four-fifths down it. No
figure was touched and no status flag moved.
