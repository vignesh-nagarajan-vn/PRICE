# PRICE: finalize report, 1 Sep 2026

Everything below was measured on the shipped tree, not remembered. The
repository working tree was not touched; all work happened on a copy of
origin/main (commit 3678fcf) and ships in this zip. CHANGES.diff records
every text change against origin/main.

## Task 1: README reconciled, stale numbers swept

`ml-or/README.md` no longer contradicts the paper. The three stale claims
(25 results, 34/34 checks, "best adversarial ratio 1.005x, structure-proof")
now read as the current state: 26 register results, 38/38 derivation checks,
and Theorem T9's two-sided result (proved within reach h >= h* - 2/c;
refuted below it by the frozen witness at ratio 0.8517, 50-digit verified;
the 1.005x verdict recorded as the search artifact behind pivot 11). A full
sweep found and fixed the same staleness wherever it appeared: E10 1.21 ->
1.20, gaps 2-4% -> 1.9-4.3%, "128-bond universe" -> 170 CUSIPs, and one
port-validation range (below).

## Task 2: blind status

The CFP (mlxor-2026.github.io) was re-checked from this environment on
1 Sep 2026 and could not be reached (network egress blocked, both direct
and via proxy). Per your rule, the build stays ANONYMOUS and this is that
explicit statement. The paper uses the official `neurips_2026.sty` with
`dblblindworkshop`: Anonymous Author(s) block, no identifying URLs, REFLEX
cited in third person, PDF metadata carries no author fields. The one-token
swap to `sglblindworkshop` (plus restoring the author block) is documented
in SUBMISSION-CHECKLIST.md item 1 if single-blind stands.

## Task 3: rebuild and verification, measured counts

PDF, rebuilt with pdflatex -> bibtex -> pdflatex x2 and then measured:

- Body content ends on page 4; References begin on page 5 (pdftotext).
- 0 overfull boxes, 0 underfull hboxes, 0 undefined references or
  citations. Three underfull-vbox page-fill notices remain (pages 2, 16,
  27); these are flushbottom page-break reports at figure boundaries, and
  page 2 was rendered and visually checked: no visible defect.
- 0 em dashes anywhere in the extracted PDF text.

Verification suites, all re-run on this tree today, observed counts:

| Suite | Observed | Expected | Match |
|---|---|---|---|
| verify_all.py | 38/38 checks passed | 38/38 | yes |
| check_docs.py | ALL DOCUMENT CHECKS PASSED (38 assertions) | pass | yes |
| pytest | 9 passed | 9/9 | yes |
| flake8 | clean | clean | yes |
| run_open1.py | exit 0 (floor + witness asserts hold) | exit 0 | yes |
| run_stability.py | exit 0, worst spread 0.0062 < 0.01 | pass | yes |
| run_all.py (full) | 36 rows, 0 FAIL | 36 rows, 0 FAIL | yes |
| THEOREMS.md register | 26 results | 26 | yes |

No discrepancies to flag. The regenerated RESULTS.md, OPEN1.md, and
STABILITY.md are byte-identical to the committed versions (determinism
confirmed).

## Task 4: claim trace and abstract

A full re-trace of every numeric claim in the body (abstract through
limitations plus Table 1) and both READMEs was run against the committed
artifacts.

- One number traced to a DIFFERENT value and was fixed by copying the
  artifact's value: the real-data port validation claimed agreement
  "within 0.5-5%". REALDATA.md's 30 published pairs give per-quantity
  maxima h* 0.23%, eps* 0.62%, m 0.76% (worst 0.76%, re-computed
  independently). The claim now reads "within 0.8%" in the paper, both
  READMEs, and the pipeline README's pivot log (4 files).
- Three values are correct but trace to committed artifacts outside the
  headline files: the E4 freeze fraction 0.33 / ~1,300 deployments and
  the E10 ratios 1.20/1.00 are in `results/full_run.log` (which the
  caption cites as "E4 log"); Table 1's d = 8 is set in
  `experiments/run_all.py`. Noted in the checklist; values verified.
- Everything else traces exactly; the full trace record is in the
  workflow log.
- Abstract: 207 words, under a 250-word cap if one applies.

## Task 5: review package disposition

Of the 11 ranked items in `mlxor-review/00-EXECUTIVE-SUMMARY.md`: items
1-9 are done and were re-verified in this build; the full item-by-item
evidence table is in DISPOSITION.md. Conscious declines, one line each:

- Item 10a (ship real-data validation inputs): the inputs are not in this
  repository and cannot be shipped from here; the paper states where they
  live and flags the leg as externally validated.
- Item 10b (verify-then-cite Zhang, Hou and Zhang): the paper was never
  read in full (arXiv unreachable from this environment); citing an
  unread paper violates the review's own verify-before-citing rule.
- Item 11 remainder (OPEN-1 sharp constant, P7.1 lift, multi-bond
  coupling, L3 under A3'): months-scale journal work, ranked
  post-deadline by the review itself. Its structure-proofness item is
  DONE: it became Theorem 3 (T9), and the review's guess that the
  infimum is exactly 1 was confirmed by the proof.

## Task 6: packaging and reproducibility

- Anonymity sweep of the final PDF: metadata clean (no Author field);
  the only author-name occurrence in the text is the REFLEX reference
  entry, which is correct third-person citation under double blind.
- The stale convenience copy `submission-materials/main.pdf` (origin
  still carried the V2 build) is synced to today's build.
- The zip was rebuilt from its own contents in a fresh temp directory as
  a reproducibility check: pdflatex compiles clean, References begin
  page 5, and verify_all + check_docs pass in the extracted tree (see
  the session record).
- Restored into the tree (dropped by the GitHub web upload, load-bearing
  because Appendix E claims CI exists): `mlxor-derivations/.github/
  workflows/verify.yml`, `posk-pipeline/.github/workflows/ci.yml`,
  `.gitignore`.

## Task 7: checklist walk

SUBMISSION-CHECKLIST.md is updated in place: every "verified in this
build" item now states what was actually measured on 1 Sep 2026 (page
gate, box counts, abstract word count, trace basis including
full_run.log, tail-average stability re-stated as "within 0.01, worst
0.0062" instead of the overclaimed "three decimals", CFP re-check
outcome). The four "before you submit" items remain: blind-option
confirmation at submission time, supplementary upload, journal pathway
indication (Stochastic Systems recommended), and a final Overleaf
compile check.

## Writing pass

A four-agent pass over the paper body, the appendix, and both READMEs
applied 45 edits (all length-neutral or shorter; page 4 still ends the
body): clipped colon-headers turned into sentences ("Around the identity
sit minimax floors...", "We deliberately report..."), empty intensifiers
cut ("quotable", "genuinely", "precisely" next to "exactly"), the last
spaced-dash em-dash stand-ins removed (proofs appendix and both READMEs),
two wrong statements fixed (a parenthetical misidentifying which pi is
Archimedes' constant; "none weakened a claim", which pivot 11 itself
contradicts), and one dangling promise removed (an L_theta constant "in
the proofs appendix" that the appendix does not state). Zero em dashes
remain in the shipped paper, appendix, and both READMEs; edits to
proofs_body.tex are mirrored in mlxor-derivations/latex/proofs.tex so the
single-source-of-truth check still passes.

## Not done, and why

- The repository itself is untouched: nothing committed, nothing pushed,
  per your instruction. CHANGES.diff (929 lines, 10 text files plus 3
  restored dot-entries) is the exact change set if you want it applied.
- literature/README.md still contains em dashes: it is an unchanged
  internal reading-notes file outside the submission package, and it is
  not in this zip.
- The three underfull-vbox page-fill notices are left: they are page-break
  reports, not typesetting defects, and the affected pages render clean.
