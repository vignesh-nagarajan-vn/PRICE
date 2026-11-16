# 3. Evidence, experiments and the results table

## 3.1 The evidence stack is the paper's strongest asset, and it holds

Both headline counts reproduce exactly on a clean re-run. `verify_all.py` gives
34/34 in 31 seconds. `run_all.py` gives 36 rows, 35 PASS, 1 DRIFT, 0 FAIL in
7 minutes 49 seconds, with the drift cell measuring 0.0062244 against a
predicted 0.0053539, which is the +16 percent the body quotes. The nine unit
tests pass. `run_open1.py` reproduces the 1.005 minimum and the monotone
tight-probe scan. Full log in `05`.

That is unusual for a workshop paper and the paper is right to lead with it.
Two of the three headline evidence numbers (34, 36) are exactly what the paper
says they are, which is not the norm.

The credibility apparatus around the numbers is the other asset. The DRIFT cell
measured rather than excused, the ten recorded pivots, the admission that
UCB-Grid wins raw regret, the real-data provenance warning: these are what make
the rest believable. **Nothing in this section proposes softening any of them.**
Every fix below either tightens a measurement or closes a gap between what the
harness measures and what the paper says it measures.

## 3.2 The last-iterate metric is the one real methodological defect

Three separate problems in the evidence stack have the same root cause: several
reported numbers are a *last-iterate* reading, `abs(agent.h - h_PO)`, taken from
trajectories that are still oscillating.

**(a) `e7_ablations.csv` does not reproduce.** Re-running `run_all.py` rewrote
two of eight cells by factors of 2 to 4 (0.2598 to 0.1092, and 0.0567 to
0.2264). This is not nondeterminism: three consecutive re-runs are bit
identical. Moving the horizon by one step is enough to move the number. The
anchor-off gated cell reads 0.27, 0.38, 0.11, 0.50, 0.13 at T = 4498 through
4502, while every anchored cell holds to four decimals. The gate-off cells
alternate with period two, which is a limit cycle being sampled at an arbitrary
phase. Full table in `05`.

**(b) E6's baseline table mixes metrics across arms.** In `run_all.py`'s
`e6_baselines`, SafeD-PerfGD, FD-PerfGD and ZO-PerfOpt are scored with
`abs(ag.h - hpo)`, BlindRRM with `abs(path[-1] - hpo)`, and UCB-Grid with
`abs(np.mean(ph[-100:]) - hpo)`. One arm of the comparison gets a
hundred-step tail average and the others get a single final value. The asymmetry
happens to run against SafeD, so it is conservative rather than
self-serving, but it is an inconsistency inside one table and it is exactly the
kind of thing a reviewer looking for a reason to discount the Pareto claim will
find.

**(c) Appendix E says "All results are deterministic from seeds."** For the
anchored cells that is true. For the anchor-off cells it is true only in the
narrow sense that the same code on the same machine gives the same bits; the
number carries no information about the agent's actual accuracy.

### The fix, verified rather than proposed

Replace the last iterate with a tail average over the deployed path, everywhere
in `run_all.py` that reports a final error. I tested a 300-step window on the
E7 grid across the same five horizons:

```
cell     tail-avg(path, 300), T = 4498 .. 4502
D1A1G1   0.0436 0.0436 0.0437 0.0437 0.0438
D0A1G1   0.0178 0.0170 0.0182 0.0212 0.0197
D1A0G1   0.1970 0.1969 0.1968 0.1967 0.1966
D0A0G1   0.2837 0.2849 0.2838 0.2804 0.2827
D1A0G0   0.1215 0.1215 0.1216 0.1216 0.1216
D0A0G0   0.0934 0.0928 0.0939 0.0965 0.0949
```

Every cell is now stable to three decimals. The T7 signature the ablation exists
to show gets *stronger*, not weaker: anchored cells sit at 0.018 to 0.044,
unanchored at 0.093 to 0.284, a clean separation instead of a noisy one. The
asserted row (`best_unanchored > best_anchored`) passes either way, so no
verification row is at risk.

`run_agent` already returns the path, so the change is one line per call site:
`abs(float(np.mean(path[-300:])) - hpo)` in place of `abs(ag.h - hpo)`. Roughly
half an hour of work plus one full re-run. Do it before the deadline: the
checklist tells reviewers to click the repository, and `e7_ablations.csv` is one
of three CSVs they will find there.

If there is no time for the re-run, the alternative is a one-clause honesty note
in Appendix E, which costs nothing and is still true:

> Appendix E, appended: The ablation grid's per-cell errors are single-seed
> last-iterate readings and move under horizon perturbation in the
> anchor-off cells; the grid's asserted comparison (anchored beats unanchored)
> is stable, the individual cell values are not.

That is the weaker option. Prefer the fix.

## 3.3 The Pareto claim rests on one seed

`e6_baselines` runs every arm exactly once, all at `seed=99`. There are no
repeats, no error bars, and no seed sweep. The resulting table:

| baseline | final error | cumulative regret |
|---|---|---|
| SafeD-PerfGD | 0.0274 | 799.34 |
| FD-PerfGD | 1.2464 | 9580.51 |
| ZO-PerfOpt | 0.1336 | 957.32 |
| UCB-Grid | 0.1290 | 342.19 |
| BlindRRM | 1.0743 | 2130.42 |

The frontier here is two points, SafeD and UCB-Grid. FD-PerfGD and BlindRRM are
dominated by SafeD; ZO-PerfOpt is dominated by UCB-Grid. So "no published
baseline Pareto-dominates SafeD-PerfGD" is carried entirely by the SafeD versus
UCB-Grid comparison, which is a 2.3x regret gap against a 4.7x error gap, from a
single draw each.

The claim is true on the evidence and it is stated carefully in the paper. It is
also the thinnest support for any of the four contribution bullets, and it is
the one a reviewer can attack cheaply ("would this survive a different seed?").

**Cost to close: about two hours plus one re-run.** Run each arm over 8 to 12
seeds, report the median with an interquartile range on both axes, and state
that the frontier is non-dominated across seeds (or, if it is not, say which
seeds flip, which would be a better paper). The figure `fig5_baselines.png`
already plots the frontier; adding error bars to it is the whole visual change.

The body sentence does not need to change if the result holds. If it does hold,
one clause makes it much harder to attack, and Figure 2's width (trim item 1)
pays for it:

> none Pareto-dominates SafeD-PerfGD on (final error, regret), across
> $12$ seeds

If there is no time, say what the evidence is. This is honest and costs four
words:

> none Pareto-dominates SafeD-PerfGD on (final error, regret) at a common seed

## 3.4 The published tolerances undercut the "0 failures" headline

`RESULTS.md` prints its own tolerance column, and it ranges from 8 percent to
50 percent:

| tolerance | rows |
|---|---|
| 0 percent (boolean assertions) | 15 |
| 8 percent | 2 |
| 10 percent | 3 |
| 12 percent | 6 |
| 15 percent | 5 |
| 30 percent | 3 |
| 50 percent | 1 |

The 50 percent row is E4's "design arm sd(c_hat) matches Fisher prediction",
measured 0.23364 against a Fisher prediction of 0.24784. The *actual* agreement
is 5.7 percent, which is a good result. The tolerance says 50 percent, which
reads as a check that could not fail. Same for the three 30 percent rows in E1:
actual agreement is 0.7, 0.2 and 6.4 percent.

The measurements are much better than the tolerances suggest, and the paper's
own body sentence is more accurate than its table ("the exchange rate within
1 to 6 percent", "the feedback floor within 1 to 7 percent"). A reviewer who
opens `RESULTS.md` sees the tolerance column first.

**Fix, one hour, no re-run required:** add a "rel. gap" column to `RESULTS.md`
carrying `abs(measured - predicted)/abs(predicted)` alongside the pre-registered
tolerance. The pre-registration is a real defence and should be kept visible;
what it needs beside it is the number showing how far inside the band the
measurement landed. This is a strict improvement in credibility for a table that
is already passing.

No body text changes. The body already quotes the actual gaps.

## 3.5 F = 1.63 is correct but has no artifact

The body's real-data sentence says "the shaping dispersion is $F = 1.63$
\emph{across} the portfolio against $1.002$ within one book". The 1.002 traces
to `REALDATA.md` section 3. The **1.63 does not appear in `REALDATA.md` at
all**; it appears only in `ml-or/README.md`, and no script computes it.

The number is right. I re-derived it from `REALDATA.md`'s own section 2: with
`Gamma` the diagonal of the ten published `gamma_PO` values,
`F = d tr(Gamma)/(tr Gamma^{1/2})^2 = 1.6252`, which is 1.63 to three figures.

The problem is the checklist's assertion that "Every numeric claim in the paper
traces to a row in RESULTS.md, OPEN1.md, or REALDATA.md". This one does not, and
it is one of two such numbers (the other is the known-`c` 0.05 in `01`).

**Fix: four lines in `run_realdata.py`,** at the end of section 3, computing the
dispersion over the ten cell `gamma_PO` values and writing it into
`REALDATA.md` next to the within-book 1.002. Fifteen minutes. Do this one: it is
the cheapest item in the package and it closes a traceability claim the
checklist makes explicitly.

## 3.6 The real-data leg is the one thing I could not verify

`run_realdata.py` prints "REFLEX tree not found - skipping real-data leg" and
exits 0. It needs `endo_market_v4/data/calibration/` and
`research/results/07-12-2026/calibrated/calibrated_boundaries.csv`, neither of
which is in this repository. So the 10/10 port validation, which the abstract
leads with, rests entirely on the committed `REALDATA.md`.

I am not disputing it. I am recording that it is the one claim in the evidence
stack that a reviewer with only the public repository also cannot check, and
that matters here in a way it does not for a normal paper, because the checklist
tells you single-blind reviewers will click the link.

**Two options, in order of preference:**

1. **Ship the ten-cell input CSV with the repository.** The port validation
   needs the published `calibrated_boundaries.csv` and the calibration inputs,
   which are ten rows of numbers. If they are publishable (the provenance note
   says the underlying series are public macro and bond-factor data), commit
   them under `posk-pipeline/data/` and let `run_realdata.py` default to them.
   Then the 10/10 claim is reproducible by anyone. Half a day, mostly checking
   what can be released.
2. **If they cannot be released, say so where the claim is made.** The
   provenance paragraph in `REALDATA.md` is binding and excellent, but it lives
   in the artifact, not the paper. One clause in the body, replacing "the port
   reproduces its published source \textbf{10/10} cells":

   > the port reproduces its published source \textbf{10/10} cells (validation
   > inputs are in the base project, not this repository)

   Six words, and it converts a claim a reviewer cannot check into a claim a
   reviewer knows they cannot check. That is a much better position.

Do not drop the provenance sentence from the body. It is on the never-trim list
and it is the reason the leg reads as honest rather than promotional.

## 3.7 Small evidence items

- **README and paper disagree on E10.** `ml-or/README.md` says the multi-bond
  risk ratio is 1.21; `RESULTS.md`, the paper's Table 1, and my re-run all say
  1.20. The paper is right. Fix the README.

**The OPEN-1 minimum is 1.00007, not 1.005, on a harder search.** My optimizer
(60000 random four-point designs plus four rounds of local refinement) drives
the family-knowing Cramer-Rao ratio to 1.00007, with the optimal support
collapsing to a cluster of spread 0.007 around the anchor. This does not
contradict `run_open1.py`; it just searches harder. The conclusion is
unchanged and slightly stronger: the infimum looks to be exactly 1, attained
at the symmetric local design, rather than 0.5 percent above it. If the body
sentence stays as "best family-knowing design: $1.005\times$ the floor", a
sharp reviewer may ask why it is not exactly 1, and the answer is "our search
stopped early", which is a worse answer than the truth. Consider:

  > \textbf{Adversarial numerics show the floor is \emph{structure-proof}} (no
  > family-knowing design beats it; best found $1.005\times$)

  which is what the evidence supports and does not invite the question.

**V3.4 is cited for something it does not measure.** Appendix A says the sharp
constant is one "against which no simulated adaptive policy fell in
verification", and Appendix B's T4 proof says "(V3.4: no simulated policy fell
below it)". V3.4 measures only the decay of the gain-to-cost ratio at the
minimax scale (0.1183 at T=250 to 0.0410 at T=2250, ratio 0.35 against a
predicted 1/3). It never computes `Var(eps_hat) x C_T` for any policy. The
actual support for the claim is `run_open1.py` section B, which tests three
amplitude schedules against the floor and reports ratios 1.018, 0.995 and
4.910. Note the 0.995: one of the three schedules lands marginally *below* the
floor, within Monte Carlo error. Replacement text for both places:

  > against which no simulated policy fell by more than Monte-Carlo error
  > (\texttt{run\_open1.py} §B)

  and in Appendix B, replacing "(V3.4: no simulated policy fell below it)":

  > (\texttt{run\_open1.py} §B: three adaptive amplitude schedules, ratios
  > $0.995$ to $1.018$)

**The drift cell is correctly reported and should stay exactly as it is.**
Measured 0.0062244 against 0.0053539, +16.3 percent, labelled DRIFT, outside
A1, not excused. My independent simulation reproduces the same effect in
miniature: the A1 remainder on the in-scope cells grows monotonically with
amplitude (+0.10, +0.35, +0.87, +3.25 percent), exactly as the local-quadratic
scope predicts. The drift cell is the honest end of that curve. Keep it, keep
the label, keep the limitations sentence that names it.

## 3.8 Two code fixes, written out

### (a) `check_docs.py` crashes, and there is no CI

`check_docs.py` exits 1 with an unhandled `FileNotFoundError`. `c4_workflow()`
opens `.github/workflows/verify.yml` outside a `try`, and no `.github/`
directory exists anywhere in the repository. Because `main()` calls
`c4_workflow()` before `c5_file_graph()`, the crash also skips C5, so the
**assumption-register completeness check never runs**, which is unfortunate
given that `02` finds two mislabelled assumptions in the body.

This matters beyond the crash. `mlxor-derivations/README.md` says both suites
are "in CI"; `posk-pipeline/README.md` lists `.github/workflows/ci.yml` in its
own layout diagram; and Appendix E of the paper says the repository contains
"continuous integration running the full verification on every push". None of
that is true of what is in the tree. A reviewer who clicks the link, as the
checklist says they will, finds no CI and a doc-checker that dies on startup.

Two changes, both small.

**Make C4 skip cleanly instead of crashing.** In `check_docs.py`, replace the
first two lines of `c4_workflow()`:

```python
def c4_workflow():
    print("== C4: workflow YAML ==")
    path = os.path.join(HERE, ".github", "workflows", "verify.yml")
    txt = open(path, encoding="utf-8").read()
```

with:

```python
def c4_workflow():
    print("== C4: workflow YAML ==")
    path = os.path.join(HERE, ".github", "workflows", "verify.yml")
    if not os.path.isfile(path):
        print("  [SKIP] no workflow file at %s" % path)
        return
    txt = open(path, encoding="utf-8").read()
```

That alone gets the suite to completion and lets C5 run. I confirmed the nine
checks before the crash all pass, so the suite should go green.

**Then add the workflow the docs already promise.** As
`mlxor-derivations/.github/workflows/verify.yml`:

```yaml
name: verify
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python verify/verify_all.py
      - run: python verify/check_docs.py
```

and the matching `posk-pipeline/.github/workflows/ci.yml`:

```yaml
name: ci
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/test_posk.py -q
      - run: python experiments/run_all.py --fast
      - run: python experiments/run_open1.py
```

`run_all.py --fast` rather than the full run: the full profile took 7m49s here
and `--fast` is what the README already advertises for CI-scale checking.
`run_realdata.py` stays out, since it skips without the REFLEX tree and a
skipping step in a badge is worse than no step.

If neither change is made before 31 Aug, the Appendix E sentence has to move.
Replacement text, which is true of the tree as it stands:

> ... the real-data leg with its 10/10 port validation, and a verification
> harness runnable end-to-end from a clean checkout.

Do not ship the CI sentence without the CI. It is the one claim in the paper
that a reviewer can falsify in ten seconds.

### (b) Make `F = 1.63` traceable

`run_realdata.py` already computes the *within-book* dispersion (1.0020) over
the 170-CUSIP universe. The cross-portfolio number the body quotes is a
different, simpler quantity over the ten cells, and it is not computed anywhere.
The section-2 loop already has every value it needs in `ext_rows`.

After the section-2 table loop, insert:

```python
    # C5.1 across the portfolio: the ten cells' own curvature dispersion
    gpo_cells = np.array([g for (_, _, _, g, _) in ext_rows])
    F_port = (len(gpo_cells) * gpo_cells.sum()
              / np.sqrt(gpo_cells).sum() ** 2)
    lines += ["", "**F = %.4f across the portfolio** of %d rating x regime "
              "cells (C5.1): isotropic exploration overpays the A-optimal "
              "shape by %.0f%% at the portfolio level."
              % (F_port, len(gpo_cells), 100 * (F_port - 1))]
```

I verified the value this produces: `F = 1.6252` from the ten published
`gamma_PO` values, which is the body's 1.63. Fifteen minutes, and it closes the
checklist's own traceability assertion.
