# 5. Verification log

Everything below was executed on 25 Aug 2026 on Windows 11, Python 3.12.10,
numpy 2.4.6, scipy 1.18.0, pytest 9.1.1, MiKTeX 25.12. Nothing in this package
is asserted from memory.

## 5.1 The repository's own suites

| Suite | Claimed | Actual | Runtime | Verdict |
|---|---|---|---|---|
| `mlxor-derivations/verify/verify_all.py` | 34 checks | **34 PASS, 0 FAIL** | 31s | matches |
| `mlxor-derivations/verify/check_docs.py` | document consistency, "in CI" | **crashes**, exit 1 | 0.3s | **fails to run** |
| `posk-pipeline/experiments/run_all.py` | 36 rows, 35 PASS + 1 DRIFT, 0 FAIL | **36 rows, 35 PASS, 1 DRIFT, 0 FAIL** | 7m49s | matches |
| `posk-pipeline/experiments/run_open1.py` | OPEN-1 premise check | completes, min CR ratio 1.0050 | 2.5s | matches |
| `posk-pipeline/experiments/run_realdata.py` | 10/10 cells | **skips**: REFLEX tree absent | 0.6s | **not verifiable here** |
| `posk-pipeline/tests/test_posk.py` | 9 tests | **9 passed** | 12s | matches |

The two headline counts the paper prints, 34 and 36, both reproduce exactly,
including the single DRIFT cell and its measured value
(0.0062244 vs predicted 0.0053539, the +16 percent the body quotes).

### check_docs.py crashes

```
== C4: workflow YAML ==
Traceback (most recent call last):
  File ".../verify/check_docs.py", line 211, in main
    c4_workflow()
  File ".../verify/check_docs.py", line 163, in c4_workflow
    txt = open(path, encoding="utf-8").read()
FileNotFoundError: ... mlxor-derivations\.github\workflows\verify.yml
```

`c4_workflow()` opens the workflow file outside a `try`. There is no
`.github/` directory anywhere in the repository (`find` over the whole tree
returns no `.yml` or `.yaml` file at all). Because `main()` calls `c4_workflow()`
before `c5_file_graph()`, the crash also skips C5, so the assumption-register
completeness check (A1 through A6 defined) and the derivation file graph never
execute. The nine checks that do run before the crash all pass.

### run_realdata.py skips

```
REFLEX tree not found - skipping real-data leg
```

The script needs `endo_market_v4/data/calibration/` and
`research/results/07-12-2026/calibrated/calibrated_boundaries.csv` from the
REFLEX tree, which is not in this repository. The committed `REALDATA.md` is
therefore the only evidence for the 10/10 claim, and it was not re-derived here.
This is the same class of gate as the REFLEX-anchor numbers flagged in the
EconML review's log. Confidence in the 10/10 claim: **unverified**, not
disputed.

### run_all.py rewrites two committed result files

The run left `results/e5_anchor_mse.csv` and `results/e7_ablations.csv`
modified. Both were restored with `git checkout` before any further work; the
diff is reported here because it is a finding, not an accident of the review.

`e5_anchor_mse.csv` moved in the ninth significant figure (1.070748630643e-02 to
1.070748629863e-02): ordinary floating-point drift, no consequence.

`e7_ablations.csv` moved materially in two of eight cells:

| cell (design, anchor, gate) | committed final_err | re-run final_err | committed c_err | re-run c_err |
|---|---|---|---|---|
| 1, 0, 1 | 0.2598 | **0.1092** | 0.1025 | 0.0454 |
| 0, 0, 1 | 0.0567 | **0.2264** | 0.2105 | 0.0153 |

This is not run-to-run nondeterminism. Three consecutive re-runs of
`e7_ablations` in a scratch copy produced bit-identical output. The cause is
that the reported quantity is a *last-iterate* error, `abs(ag.h - hpo)`, on
trajectories that are still oscillating. Perturbing only the horizon shows it:

```
cell    T=4498  T=4499  T=4500  T=4501  T=4502
D1A1G1  0.0115  0.0053  0.0058  0.0057  0.0057
D1A0G1  0.2667  0.3791  0.1092  0.4978  0.1302
D0A0G1  0.3346  0.4118  0.2264  0.5507  0.0921
D1A0G0  0.1950  0.0594  0.1940  0.0595  0.1942
D0A0G0  0.2044  0.0406  0.2051  0.0405  0.2053
```

Every anchored cell is stable to four decimals. Every anchor-off cell is not:
the gate-off cells alternate with period two (a limit cycle), and the gated ones
range over a factor of six. The fix was verified rather than guessed: replacing
the last iterate with a 300-step tail average over the deployed path pins every
cell to three decimals across the same five horizons, and separates anchored
from unanchored more cleanly than the last iterate does.

```
cell     tail-avg(path, 300) over T=4498..4502
D1A1G1   0.0436 0.0436 0.0437 0.0437 0.0438
D0A1G1   0.0178 0.0170 0.0182 0.0212 0.0197
D1A0G1   0.1970 0.1969 0.1968 0.1967 0.1966
D0A0G1   0.2837 0.2849 0.2838 0.2804 0.2827
D1A0G0   0.1215 0.1215 0.1216 0.1216 0.1216
D0A0G0   0.0934 0.0928 0.0939 0.0965 0.0949
```

The asserted row, `best_unanchored > best_anchored`, passes at every horizon
tested, so no verification row is at risk. What is at risk is the committed CSV
and the Appendix E sentence "All results are deterministic from seeds."

## 5.2 Independent re-derivation (`tools/indep_check.py`)

Written from the paper's formulas alone. No import from `posk/`, no result file
read; the market constants are transcribed and every quantity recomputed.
**136 checks, 0 failures, 1 untraceable number.** Runtime 2m21s.

Covered:

- The model's closed forms: `gamma`, `gamma_PO = gamma + eps(2 + c psi - c h)`
  and `eps = -tau'` against numerical derivatives of `J` and `Phi` at four
  operating points; `h_SP` as a fixed point of `BR(tau(.))`; `Phi'(h_PO) = 0`.
- T2 at both moduli: the predicted rate `(1/2) gamma_PO sigma^2` reproduces the
  table's 0.01056 and 0.00535 to four figures, and the realized modulus hits
  0.3 and 0.6 exactly. Four simulated (modulus, amplitude) cells on the loop
  `d_{t+1} = -m d_t + u_t` with cost taken from the *true* `Phi`, so the residual
  is exactly the A1 remainder: +0.10, +0.87, +0.35 and +3.25 percent, all
  inside the paper's 1 to 6 percent band and monotone in amplitude as A1
  predicts. The off-centre inflation factor `1 + T dbar^2/S_xx` verifies exactly.
- T1: the cap `d_0^2/(1-m^2)` to nine decimals at three moduli, and its
  monotonicity in `m` (C1.1). The excitation floor `(sigma/gamma)^2/(1-m^2)`
  simulated at three moduli, within 0.02 relative.
- T3/T4: the van Trees bound is strictly below `sigma^2/D` at every cell tried
  (4.8 and 0.4 percent lower), which is the arithmetic behind the scope slip in
  `02`. The Le Cam optimizer `c* = 2/3` and the constant `c*^2(1-c*)/4 = 1/27`
  reproduce, and `(1/2)/(1/27) = 13.5` matches the body's stated factor.
- T5a/T5b/T5c and C5.1 at d = 3, 5, 8: the A-optimal value
  `(tr Gamma^{1/2})^2/B`, the isotropic-to-A-optimal ratio equal to `F` to
  machine precision, `1 <= F <= d`, and 4000 random feasible designs per cell
  never beating the optimum. The D-optimal design maximizes log-det against the
  same random search; the c-optimal value is never beaten.
- The dispersion factor on the real-data cells: `F = 1.6252` over the ten
  published `gamma_PO` values, which is the paper's 1.63.
- T6: 4000 random three-point designs, worst determinant 3.3e-06 (never
  singular); 20000 random two-point designs, minimum `|n_3| = 0.439` on the null
  direction, so the c-sensitivity is never estimable from two points; the
  two-point Fisher matrix is singular and the three-point one is not.
- T7 at three (B, T) cells: the secant bias matches `tau'''/6 w^2` within 2
  percent, the two-term `MSE_np` closed form matches the direct
  variance-plus-bias computation, and the crossover threshold
  `|tau'''| B / (3 gamma_PO T)` equals the square root of the bias term exactly.
- T8: `v* = (sigma/kappa) sqrt(rho)` by grid maximization at three discount
  rates; the sign of NPV flips across `rho*` in both directions; `gamma_PO`
  cancels out of `rho*` to 1e-9.
- P9.1: three schedules (`t^{-1/2}`, constant, geometric) at two horizons, all
  landing on `(1/2) gamma_PO sigma^2` to machine precision.
- E8: every LQ constant re-derived from `Phi(p) = p(a + (g-b)p)` alone.
  `gamma_PO = 2(b-g)`, `p_PO = a/(2(b-g))`, `p_SP = a/(2b-g)`, and the exchange
  rate 0.384 at g = 0.4 and 0.192 at g = 0.7, both to three figures. The
  reported agent cell (`p_SP = 7.14`, `p_PO = 12.5`) reproduces at g = 0.6.
- L4: the bracket `||e|| + |h-psi| ||e'||` collapses to `L_fam ||e||` with
  `L_fam = 1 + c|h-psi|` at six (h, error) cells, which is the constant the
  agent uses.
- OPEN-1: the family-knowing Cramer-Rao product minimized over four-point
  designs by 60000 random draws plus four rounds of local refinement.

Two numbers came out differently from the paper, both reported in `01` and `03`:

**The OPEN-1 minimum is 1.00007, not 1.005.** My search drives the
family-knowing design closer to the floor than `run_open1.py` does, and the
optimizer's support collapses to a cluster of spread 0.007 around the anchor.
The paper's conclusion is unaffected and in fact strengthened: the infimum
looks to be exactly 1, attained at the symmetric local design.

**The tight-probe scan reproduces in direction but not in magnitude.** I get
4.83 at t = 1.00 rising to 17.99 at t = 0.05; `run_open1.py` reports 5.72
rising to 40.94. Both are monotone increasing, which is the claim the paper
makes. The magnitudes differ because my cost model is the local quadratic
throughout and `run_open1.py` mixes the local-quadratic and true incremental
costs across its sections. The paper's numbers trace to `OPEN1.md`, so they
are sourced; they are not independently confirmed here.

One number is untraceable:

**"with c known a priori the floor breaks (ratio -> 0.05)"** (main.tex
Sec. 3). No shipped artifact computes a known-`c` ratio. `run_open1.py` has no
known-`c` branch and `grep` finds no such number in `OPEN1.md`,
`OPEN-PROBLEMS.md`, or `RESULTS.md`. The nearest 0.05 in the vicinity is the
tight-probe *location* `t = 0.05` in `OPEN1.md`'s table, whose ratio is 40.94.
I re-derived the known-`c` computation from scratch (drop the `c` coordinate,
so `theta = (C0, C1)` and `s(h) = (1, e^{-ch})`). The direction of the paper's
claim is right and the boundary is real, but the number is not a limit:

  ```
  same probe grid as the paper's scan, c known:
    t=1.00 -> 0.3002   t=0.80 -> 0.2028   t=0.60 -> 0.1358
    t=0.40 -> 0.0895   t=0.20 -> 0.0586   t=0.05 -> 0.0425
  unconstrained 2-point designs (h*, t), c known:
    t=0.500 -> 0.09565   t=0.200 -> 0.05220   t=0.050 -> 0.03819
    t=0.010 -> 0.03510   t=0.001 -> 0.03444
  ```

  The ratio falls monotonically and does not settle at 0.05. See `01` for the
  replacement sentence.

## 5.3 Proof reading

Every proof in `mlxor-derivations/latex/proofs.tex` (identical to the paper's
`proofs_body.tex` below the BEGIN BODY marker) was read line by line against
`THEOREMS.md`, the assumption register, and the corresponding derivation
document: L1, T1, C1.1, C1.2, R1, T2, P2.1, P2.2, T3, L2, T4, T5a-c, C5.1, L3,
T6, L4, R2, P7.1, T7, T8, P9.1, P9.2, P9.3.

All are correct as stated. The algebra in T5a-c, C5.1, T7 and T8 was re-derived
by hand and again numerically. The one substantive proof issue found is in T6,
where the stated reason does not support the (true) conclusion; the two-line
argument that does is in `02` with replacement text.

The four scope slips found are between the *body* and the appendix, not inside
any proof. They are in `02`.

## 5.4 Build verification

Built from source in a scratch copy of `paper/` (the committed tree was not
touched): `pdflatex` then `bibtex` then `pdflatex` x3.

- Exit 0 on every pass. **Zero overfull boxes, zero underfull boxes**, no
  undefined citations, no undefined references.
- 14 pages. Content ends on page 4, References begin on page 5, Appendix A on
  page 6. The checklist's page-gate claim is confirmed by my own build.
- The two `LaTeX Warning: 'h' float specifier changed to 'ht'` lines are from
  the appendix table and figure; harmless.
- `paper/theorems_body.tex` and `paper/proofs_body.tex` are byte-identical to
  `mlxor-derivations/latex/theorems.tex` and `proofs.tex` between their
  BEGIN/END BODY markers. Single source of truth is intact. The one consequence
  of the marker placement is a finding: `proofs.tex`'s standing-assumptions
  paragraph sits *above* the marker and so never reaches the PDF (see `02`).
- Theorem numbering as compiled: body Theorem 1 = T2, body Theorem 2 = T3/T4;
  Appendix A restates them as Theorem 4 and Theorems 5 and 6.

## 5.5 Web verification (25 Aug 2026)

**Venue.** `mlxor-2026.github.io` loaded directly. Confirmed verbatim:
deadline 31 Aug 2026 AoE; "Maximum 4 pages for the main body, using the
NeurIPS conference format"; "Submissions are non-anonymous", single-blind;
notification 29 Sept 2026 AoE; 12 or 13 Dec 2026, Atlanta. The three journal
pathways (Stochastic Systems, Mathematics of OR, Operations Research) and
"Authors may indicate at most one journal" are confirmed. Every checklist
venue fact holds.

**One new venue fact the checklist does not have.** The CFP asks for the
`sglblindworkshop` option of the NeurIPS 2026 template. Confirmed that
`neurips_2026.sty` declares `sglblindworkshop` and `dblblindworkshop`, and
confirmed by reading the shipped `neurips_2025.sty` that it declares only
`final`, `nonatbib` and `preprint`. See `04`.

**Stochastic Systems scope** re-read from the INFORMS editorial statement:
flagship of the Applied Probability Society, OR content only, explicitly
welcomes "ties between applied probability and optimization, or with machine
learning" and work "at the interface of stochastics, modeling, statistics, and
data science". The checklist's recommendation still looks right; `04` says why
and names the one condition that would change it.

**Bracale, Maity, Sun and Banerjee**, "Learning the Distribution Map in
Reverse Causal Performative Prediction", AISTATS 2025, PMLR v258,
arXiv:2405.15172. Read the extracted paper text: abstract, Section 4 "Optimal
design for deploying models under binary actions", Section 5 "Regret analysis
on performative risk", Algorithm 3 and Theorem 5.1. Not read in full.

- **Li and Wai**, "State Dependent Performative Prediction with Stochastic
  Approximation", arXiv:2110.00800. PDF in the repository's own
  `literature/pdfs/`; first page read directly (title, authors, abstract,
  introduction).
- **Barzykin, Bergault, Gueant and Lemmel**, "Optimal Quoting under Adverse
  Selection and Price Reading", arXiv:2508.20225v5, dated 13 Jun 2026. PDF in
  `literature/pdfs/`; first page read directly.
- **Gueant, Lehalle and Fernandez-Tapia**, "Dealing with the Inventory Risk: A
  solution to the market making problem", arXiv:1105.3115v5. PDF in
  `literature/pdfs/`; first two pages read directly.
- **Zhang, Hou and Zhang**, "Unified Inference Framework for Single and
  Multi-Player Performative Prediction: Method and Asymptotic Optimality",
  arXiv:2602.03049, Feb 2026. **Only a structured report of the paper was read,
  not the paper.** Marked verify-before-citing.
- A search for prior art on a variance-times-regret invariance identity in
  adaptive control and dual control returned nothing of the kind. That is
  absence of evidence from one search session, not a literature review; `01`
  states the novelty claim in those terms.

## 5.6 The five open checklist items, re-checked

| # | Item | State |
|---|---|---|
| 1 | Author emails and affiliations | **Still open.** `main.tex:35` reads `vignesh.nagarajan@[institution].edu`. Note that neither author has an affiliation line at all, so this is an addition, not a substitution |
| 2 | Repository placeholder URL | **Still open.** `main.tex:43` reads `https://github.com/[repo]/price` |
| 3 | `neurips_2025.sty` stopgap | **Still open, and larger than the checklist thinks.** See `04` |
| 4 | Journal designation | **Still open.** Not a `.tex` field; it is an OpenReview submission field. Recommendation endorsed in `04` |
| 5 | Compile check | **Done here.** Content ends p.4, References start p.5, zero overfull boxes |

## 5.7 What was NOT verified, stated plainly

**The real-data leg's 10/10 port validation.** `run_realdata.py` skips without
the REFLEX tree, which is not in this repository. The `REALDATA.md` table was
read but not reproduced. This is the paper's only external-data claim and it
is the one thing in the evidence stack I could not touch.

- **`F = 1.63` across the portfolio** was re-derived here (1.6252 from the ten
  published `gamma_PO` cells), but the *provenance* of those ten cells rests on
  the same unverified leg.

**The exact behaviour of `sglblindworkshop`**: whether it prints a workshop
notice, and what it does to the author block. The official NeurIPS 2026 author
kit was not retrievable from this environment. The finding in `04` rests only
on the option's existence in `neurips_2026.sty` and its absence from
`neurips_2025.sty`, both of which are confirmed.

- **Zhang, Hou and Zhang (2026)**: structured report only. Do not cite unread.

**Publication venues of record** for the Gueant-Lehalle and Barzykin papers:
arXiv identifiers and author lists were read from the PDFs in hand; the
journal of record for each was not re-verified. Use the arXiv entry or check
before the bibliography goes final.

- **`run_all.py --fast`** was used for the horizon-sensitivity study in 5.1;
  the headline table came from the full run.
- The claim that the ten measurement-forced pivots are "recorded in code where
  they happened" was spot-checked in `run_all.py` (E1 and E7 both carry their
  pivot records as comments) but not audited for all ten.
