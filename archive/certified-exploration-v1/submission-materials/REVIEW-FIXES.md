# Review fixes applied — 26 Aug 2026

Every item in `ml-or/mlxor-review/` (files 00–05) has been applied to this
copy of `submission-materials/`. Nothing in the original repository was
modified. Every fix was re-verified before shipping: all suites were
re-run here (verify_all 34/34; check_docs ALL PASSED; run_all 36 rows,
0 FAIL; run_open1 exit 0; 9/9 unit tests), the paper was rebuilt from
source (0 overfull boxes, content ends p. 4, References begin p. 5), and
every changed mathematical claim was re-derived in an independent script
(19/19 checks, including the echo-chamber sign at four moduli, the van
Trees prior term, the Le Cam 1/27 and 13.5 constants, the T6 null-vector
argument, F = 1.6252, and the known-c scan reproducing the reviewer's
numbers exactly).

## Ranked action list → what was done

1. **Theorem 2(ii) rescoped to what Appendix B proves.** Abstract,
   contribution bullet 2, Theorem 2(ii), and the limitations paragraph now
   all state the constant-factor floor (`γ_PO σ²/27`, Le Cam) with the
   sharp constant ½ "numerically supported and open (OPEN-1)". The
   `OPEN-PROBLEMS.md` "Proved today" entry was reconciled to the same
   conservative reading (it had contradicted `proofs.tex`/`THEOREMS.md`).
2. **The three unsourced/wrong body claims fixed.**
   (a) Known-c "ratio → 0.05" replaced by the traceable "falls
   monotonically (0.30 at t=1.0, 0.04 at t=0.05)", now computed by a new
   §D in `run_open1.py` → `results/OPEN1.md` (both cost models; the
   local-cost column reproduces the reviewer's independent numbers to 4
   decimals).
   (b) "sits at a wider spread" → "sits at a *tighter* spread here, since
   toxic flow is profitable net of ψ" (verified h_PO < h_SP at every
   modulus, two independent implementations).
   (c) Theorem 2(i) now carries the pathwise budget and the van Trees
   prior term `σ²/(D + σ²(π/w)²)`; "holds exactly" removed.
3. **Style file swapped.** `neurips_2026.sty` (from `econml/paper/`) with
   `[sglblindworkshop]` + `\workshoptitle{...}`; the `\@noticestring`
   hack deleted; `neurips_2025.sty` removed. Rebuilt: content still ends
   p. 4, References p. 5, 0 overfull. Add `,final` at camera-ready.
4. **Citation gaps closed.** Bracale–Maity–Sun–Banerjee (AISTATS 2025)
   dispatched in Positioning; Guéant–Lehalle–Fernandez-Tapia and
   Barzykin–Bergault–Guéant–Lemmel (price reading) dispatched in the
   Model section; Li–Wai (2022) and Brown–Hod–Kalemaj (2022) added to the
   stateful bracket; Mendler-Dünner et al., Drusvyatskiy–Xiao and
   Hardt–Mendler-Dünner now cited in §1. Four new bib entries (the two
   market-making entries are arXiv versions — check the journal of record
   before camera-ready, per the review's caveat).
5. **Last-iterate metric replaced by a 300-step tail average** everywhere
   `run_all.py` reports a final error (E4, E6, E7, E8), one metric for
   every arm. Verified stable to three decimals under horizon
   perturbation (matches the review's own verification table). CSVs and
   `RESULTS.md` regenerated; Appendix E documents the metric.
6. **Assumption labels fixed and the register now reaches the PDF.**
   §2: noise is (A3), stationary scale is (A5); Theorem 1 reads "Under
   A1, A2-sym, A3 and A6". The `BEGIN BODY` marker in `proofs.tex` was
   moved above the standing-assumptions paragraph and the full A1–A6
   register written out there, so Appendix B now defines every assumption
   it cites (single source of truth preserved; `_body` files regenerated
   from the markers).
7. **F = 1.63 traceable + check_docs fixed + CI added.**
   `run_realdata.py` now computes the portfolio dispersion (F = 1.6252
   verified from the ten published cells) and `REALDATA.md` carries it;
   `check_docs.py` C4 skips cleanly instead of crashing (C5 now runs);
   `.github/workflows/verify.yml` and `ci.yml` added as the docs promise
   (pytest added to `posk-pipeline/requirements.txt`).
8. **Baselines over 12 seeds with error bars.** E6 runs every arm over 12
   seeds, reports median + IQR (CSV + `fig5_baselines.png` error bars).
   Honest result, stated in the paper: no baseline Pareto-dominates
   SafeD on medians; **UCB-Grid edges it in one of the twelve seeds**
   (seed 106), reported in the body, the CSV, and the console.
9. **Style pass.** Em dashes in the body: 34 → 0 (the one remaining `---`
   is a table placeholder); "converges iff" → "converges when"; the
   modulus defined once (`m = εβ/γ = ε/γ`, β = 1 here); T6's cliff clause
   moved onto the theorem; the four orphan proofs (P2.1, R1, R2, P9.2)
   now have statements in Appendix A; T6's wrong parenthetical replaced
   by the two-line null-vector argument; the T7 `\cdot\ldots` display
   fixed; V3.4 no longer cited for something it does not measure (both
   places now cite `run_open1.py` §B, ratios 0.995–1.018).
10. **Real-data leg honestly scoped.** Body now says "validation inputs
    are in the base project, not this repository". The abstract's dealer
    parenthetical uses the decision-problem phrasing. README E10 ratio
    corrected to 1.20.

## Page budget

The additions (≈110 words) were paid for by the checklist's trim order
plus: the §5 headline-rows enumeration (numbers live in App. C), merging
the certification figure into Figure 1 as a third panel, and small
tightenings in Positioning/§3. Content ends page 4; References begin
page 5; zero overfull boxes.

## Numbers that changed with the tail-average metric (all re-verified)

- E4 SafeD settle: 1.324 → **1.258** (vs h_PO = 1.296; Table 1 updated)
- E8 pricing agent: 12.58 → **12.65** (vs p_PO = 12.5; body + Table 1)
- E7 grid: anchored cells 0.018–0.044, unanchored 0.094–0.283 — the T7
  signature is *sharper* than under the last-iterate reading
- E6 medians (12 seeds): SafeD err 0.0599 / regret 1008; FD-PerfGD
  9587 regret (>5× SafeD); UCB-Grid 316 regret (lower raw regret,
  admitted in the body)

## Still open (cannot be done from this repository)

- Author affiliations/email placeholders and the repo URL in `main.tex`.
- The journal-pathway indication (OpenReview field): Stochastic Systems.
- The real-data 10/10 leg still requires the REFLEX tree to re-run;
  `REALDATA.md` is the committed evidence and the body now says so.
- `ml-or/README.md` (outside `submission-materials/`, not in this zip)
  still says the E10 ratio is 1.21; the correct value is 1.20.
- Verify-before-citing items for camera-ready: Zhang–Hou–Zhang
  (arXiv:2602.03049), the 2026 survey, and the journals of record for
  the two market-making arXiv entries.
