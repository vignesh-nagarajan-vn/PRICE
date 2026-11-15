# Review package: the ML x OR paper, 25 Aug 2026

A peer review of `ml-or/submission-materials/` against five axes, written to be
the mirror of the EconML review in `econml/paper-updates/` and the earlier six-axis
package. Deadline 31 Aug AoE, six days out.

Read `00-EXECUTIVE-SUMMARY.md` first. It carries the verdict and the ranked
action list; everything else is the evidence behind a row in that list.

| File | Carries |
|---|---|
| `00-EXECUTIVE-SUMMARY.md` | Verdict, the ranked action list, and what was checked and found sound |
| `01-novelty-and-citations.md` | What is genuinely new, how defensible, the three citation gaps, contemporaneous 2026 work |
| `02-technical-rigor.md` | Proof audit, the assumption register against the body, four scope slips with replacement text |
| `03-evidence-and-experiments.md` | Suite re-runs, the results table, baselines, ablations, the real-data gate |
| `04-narrative-venue-and-style.md` | The 4-page spine, ML x OR fit, format compliance, journal designation, prose |
| `05-verification-log.md` | Every suite run with its counts and runtime, every claim's verification method, and what could not be checked |
| `tools/indep_check.py` | Independent re-derivation, 136 checks, no import from `posk/` |

## Method

Nothing is in this package that was not checked first.

1. **The repository's own suites were re-run** and their output recorded:
   `verify_all.py`, `check_docs.py`, `run_all.py`, `run_open1.py`,
   `run_realdata.py`, `tests/test_posk.py`. Counts and runtimes are in `05`.
   Where a claimed count did not match, or a suite did not complete, that is a
   finding and it is written as one.
2. **Every headline number was re-derived independently** in
   `tools/indep_check.py`, from the formulas printed in `main.tex`,
   `theorems_body.tex` and `proofs_body.tex`. The script imports nothing from
   `posk/` and reads no result file. 136 checks, 0 failures, 1 number the paper
   states that no shipped artifact produces.
3. **Every proof was read line by line** against `THEOREMS.md` and the
   assumption register, with attention to the `PV*` and `COND` status flags and
   to whether the 4-page body respects the scope they mark.
4. **The citation surface was checked against the literature**, not against
   `NOVELTY-CROSSWALK.md`. Nothing is recommended for citation that was not
   read; where only an abstract or a structured report was available, the
   recommendation says so and is marked verify-before-citing.
5. **The venue facts were re-verified** from the workshop site: deadline, page
   limit, format option, blind status, and the three journal pathways.
6. **The paper was rebuilt from source** (pdflatex, bibtex, pdflatex x3) and the
   page boundary re-checked with `pdftotext`.

## Constraints this package works under

The paper source belongs to Shriraghav. Nothing outside `ml-or/mlxor-review/`
was modified; the two result CSVs that `run_all.py` rewrote during the re-run
were restored to their committed state, and the diff is reported in `05` because
it is itself a finding.

Every proposed edit carries exact replacement text next to its reason, so it can
be pasted. There is no candidate build and no patch file: that is the deliberate
simplification against the six-axis package, and it is why the words are in the
review instead.

Every suggestion respects the 4-page body. Anything proposed for the body names
what pays for it or is scoped to the appendix, which is unlimited. Nothing on
the checklist's never-trim list is touched.
