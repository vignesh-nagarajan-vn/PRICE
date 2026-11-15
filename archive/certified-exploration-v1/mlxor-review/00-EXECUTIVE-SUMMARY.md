# Review: making this the strongest paper at ML x OR @ NeurIPS 2026

**Reviewed 25 Aug 2026 against `ml-or/submission-materials/`. Deadline 31 Aug
AoE, six days out.**

Every claim in this package was checked before it was written down. All six of
the repository's suites were re-run and their output recorded; every headline
number was re-derived from scratch in a script that imports nothing from `posk/`
(`tools/indep_check.py`, 136 of 136 checks pass); every proof was read line by
line against the register; the paper was rebuilt from source and the page gate
re-checked; the venue call was re-verified by loading the site. Two things could
not be checked from here and both are flagged rather than assumed.

## Verdict in one paragraph

This is a very good workshop paper and the evidence stack behind it is better
than most conference papers carry. The exchange rate is a real result: an exact,
policy-independent identity between estimator variance and cumulative
performative regret, which I could not find an analogue of anywhere, and which
reproduces to four figures under independent re-derivation. The design theory is
correct, the agent is derived rather than tuned, and the honesty discipline (the
DRIFT cell measured not excused, the ten pivots, the admission that UCB-Grid
wins raw regret) is the reason the whole thing reads as credible. What stands
between it and the top of the stack is one self-contradiction, one unsourced
number, and one wrong word, all in the four-page body and none of them in the
mathematics. Theorem 2(ii) states as proved what the paper's own Appendix B
twice calls conjectured, so a reviewer who reads both finds the paper
contradicting itself. Section 3's "with `c` known a priori the floor breaks
(ratio -> 0.05)" traces to nothing in the repository, and the checklist puts it
on the never-trim list while also asserting that every number traces. Section 2
says the performative optimum "sits at a wider spread" when in this model it
sits at a tighter one, in every cell, as the paper's own real-data table
already reports. All three are fixable in an afternoon, and the first is the
difference between a good score and an argument with a reviewer you lose.

## The ranked action list

Ranked by expected review impact per day of work. Items 1 to 6 are pre-deadline.

| # | Action | Impact | Cost | Where |
|---|---|---|---|---|
| 1 | **Rescope Theorem 2(ii) to what Appendix B proves.** The body, abstract, contribution bullet 2 and the limitations paragraph all say the sharp constant `1/2 gamma_PO sigma^2` holds over two-point symmetric priors. Appendix A says it is "conjectured", Appendix B says it "is part of OPEN-1", and `THEOREMS.md` agrees. The Le Cam proof gives `gamma_PO sigma^2/27`. Four replacement passages, all the same length or shorter | **This is the one.** It removes the only thing in the paper a reviewer can be flatly right about, and the theorem that remains is still strong. Leaving it is a self-contradiction inside one PDF | 1 hour | `02` §2.2 |
| 2 | **Fix the three unsourced or wrong body claims.** (a) the known-`c` ratio 0.05, which no artifact computes and which is not a limit (I re-derived it: 0.042 on the paper's own grid, 0.034 and still falling on wider designs); (b) "sits at a wider spread", which is backwards in every cell; (c) Theorem 2(i)'s `sigma^2/B`, which drops the van Trees prior term and so states something false for the biased estimators the theorem covers | Three things a careful reviewer catches and is right about, for three sentence swaps | 2 hours | `01` §1.6, `02` §2.3-2.4 |
| 3 | **Swap in `neurips_2026.sty` with `sglblindworkshop`.** The CFP requires that option; the shipped `neurips_2025.sty` does not declare it, which is why the paper carries a manual `\@noticestring` hack. **The correct style file is already in this repository** at `econml/paper/neurips_2026.sty`. I tested the swap in both variants: content still ends p.4, References still start p.5, zero overfull boxes | Format compliance. A desk-reject risk for a 20-minute fix, and it retires checklist item 3 | 20 min | `04` §4.4 |
| 4 | **Close the two citation gaps a reviewer will hit.** Bracale, Maity, Sun and Banerjee (AISTATS 2025) do optimal design plus regret analysis for learning the distribution map: this is the nearest prior art to the paper's whole premise and it is uncited, and gap G1 as written does not survive it. Separately, the model is a market maker and the bibliography has no market-making citation, while three such PDFs sit in `literature/pdfs/` tagged read-in-full. Dispatch sentences and bib entries are written out | Removes the most likely "missed related work" strike from both halves of an ML x OR committee | 3 hours | `01` §1.2-1.4 |
| 5 | **Replace the last-iterate metric with a tail average.** `e7_ablations.csv` does not reproduce: re-running moved two of eight cells by 2 to 4x, because the reported number is a last-iterate reading of a limit-cycling trajectory. E6's baseline table scores one arm with a tail average and the rest with last iterates. Appendix E claims determinism. I verified the fix rather than proposing it: a 300-step tail average pins every cell to three decimals and *strengthens* the T7 signature | The checklist tells reviewers to click the repo. This is what they find there | half day incl. re-run | `03` §3.2 |
| 6 | **Fix the assumption labels and give the PDF an assumption register.** Section 2 labels the noise model (A2) when it is A3, and glosses A3 as "stationary exploration scale" when that is A5. Theorem 1 says "Under A1--A3" where the register requires A1, A2-**sym**, A3, A6. And A1 through A6 are cited 18 times in the compiled PDF and defined nowhere, because `proofs.tex`'s standing-assumptions paragraph sits above the `BEGIN BODY` marker and never reaches the paper. Appendix is unlimited, so the register costs zero body lines | Cheapest credibility-per-minute item in the package | 1 hour | `02` §2.5 |
| 7 | Make `F = 1.63` traceable (four lines in `run_realdata.py`; I verified the value is 1.6252 from the ten published cells), fix `check_docs.py`'s crash, and add the CI the docs promise. Or, if not, remove the CI sentence from Appendix E | Retires two false claims about the artifact for an hour's work | 1 hour | `03` §3.8 |
| 8 | Run the baseline comparison over 8 to 12 seeds with error bars. The Pareto claim currently rests on one draw each, and its whole weight is the SafeD-versus-UCB-Grid pair | Hardens the weakest-supported contribution bullet | 2 hours + re-run | `03` §3.3 |
| 9 | The em dash pass (34 in a four-page body; the EconML paper has zero), "converges iff" to "converges when", the double modulus definition, the four orphan proofs in Appendix B, and T6's wrong-reason parenthetical | Readability and precision at review speed; the em dash pass slightly *reduces* line count | 2 hours | `02` §2.6-2.8, `04` §4.6 |
| 10 | **Camera-ready:** ship the real-data validation inputs so the 10/10 claim is reproducible, or say in the body that they live in the base project. Verify-then-cite Zhang, Hou and Zhang (Feb 2026), whose semiparametric efficiency bound is the closest thing to T3/T4 in the 2026 literature | Converts the one unverifiable claim into a checkable or an honestly-flagged one | half day | `03` §3.6, `01` §1.5 |
| 11 | **Journal track:** close OPEN-1 by the conditional van Trees route; prove structure-proofness as an equivalence theorem (my search suggests the infimum is exactly 1, not 1.005); lift P7.1 from COND to P; the coupled multi-bond case; what replaces L3 under A3' | The journal version's spine, and OPEN-1 is what would move the designation from Stochastic Systems to Mathematics of OR | months | `02` §2.9 |

**Indicate Stochastic Systems** as the journal pathway, as the checklist
already recommends. I re-read the editorial statement and the fit holds: INFORMS
Applied Probability Society flagship, OR content only, explicitly welcomes ties
between applied probability and machine learning. `04` §4.5 gives the reasoning
and names the one condition (OPEN-1 closing) that would argue for Mathematics of
OR instead.

## What was checked and found sound: do not spend deadline time here

**Every proof.** L1, T1, C1.1, C1.2, R1, T2, P2.1, P2.2, T3, L2, T4, T5a-c,
C5.1, L3, T6, L4, R2, P7.1, T7, T8, P9.1, P9.2, P9.3, read line by line against
the register and the derivations. No proof is wrong. The KKT arguments for the
three design shapes, C5.1's Cauchy-Schwarz, L2's three ingredients, T7's
constrained optimum and T8's concave NPV were each re-derived by hand and again
numerically. The one substantive proof note is T6's parenthetical, where the
stated reason does not support a conclusion that is nonetheless true; the
two-line argument that does support it is in `02`.

**Every closed form I could re-derive.** 136 checks in `tools/indep_check.py`,
0 failures, written from the paper's formulas with no import from `posk/`.
`gamma`, `gamma_PO` and `eps` against numerical derivatives. The T2 rate at both
moduli to four figures, with the simulated A1 remainder growing monotonically in
amplitude exactly as scope predicts (+0.10, +0.35, +0.87, +3.25 percent). The T1
cap and the excitation floor. The Le Cam arithmetic including the factor 13.5.
T5a/b/c and C5.1 at three dimensions, with 4000 random feasible designs per cell
never beating the optimum. T6's rank counting. T7's bias, variance and threshold
at three cells. T8's `v*` and `rho*` with `gamma_PO` cancelling. P9.1 on three
schedules. Every LQ constant in E8 re-derived from `Phi` alone. L4's Lipschitz
collapse.

**Both headline counts.** `verify_all.py` gives 34/34 in 31s. `run_all.py` gives
36 rows, 35 PASS, 1 DRIFT, 0 FAIL in 7m49s, with the drift cell at the +16
percent the body quotes. Nine unit tests pass. The counts in the paper are the
counts in the tree.

**The build.** Compiles clean from source, zero overfull and zero underfull
boxes, no undefined citations or references, content ends page 4, References
begin page 5. The checklist's page-gate claim is confirmed by my own build, and
it survives the style-file swap in item 3.

**Single source of truth.** `paper/theorems_body.tex` and
`paper/proofs_body.tex` are byte-identical to the derivation folder's
`theorems.tex` and `proofs.tex` between their BEGIN/END BODY markers. The one
consequence of the marker placement is the missing assumption register in
item 6.

**The venue facts.** Deadline 31 Aug AoE, 4-page main body in NeurIPS conference
format, non-anonymous and single-blind, notification 29 Sept, Atlanta 12 or 13
Dec, and the three journal pathways with at most one indicated. Every checklist
venue fact holds. The one new fact is the `sglblindworkshop` requirement in
item 3. The five open checklist items are all still open and none has drifted;
item 5, the compile check, is now done. `05` has the state of each.

**The honesty discipline.** The DRIFT cell, the ten recorded pivots, the
UCB-Grid admission, the real-data provenance sentence, the load-bearing `o(1)`
qualifier in the limitations. Nothing in this package proposes softening any of
them, and the never-trim list is untouched throughout.

## What could not be verified

**The real-data leg's 10/10 port validation.** `run_realdata.py` skips without
the REFLEX tree, which is not in this repository. `REALDATA.md` was read but not
reproduced. This is the paper's only external-data claim and the only part of
the evidence stack I could not touch. Not disputed, unverified.

**The exact behaviour of `sglblindworkshop`** beyond what I built and read. I
confirmed the option exists, compiled both variants, and read the resulting
footers and author blocks. The official NeurIPS 2026 author kit was not
retrievable from this environment.

**Zhang, Hou and Zhang (arXiv:2602.03049).** I read a structured report of the
paper, not the paper. Marked verify-before-citing throughout.

**Publication venues of record** for the Gueant-Lehalle and Barzykin papers.
Titles, authors and arXiv identifiers were read from the PDFs in hand; the
journal of record for each was not re-verified.

`05-verification-log.md` has the full trail: what was run, what it printed, how
long it took, and every place where my number and the paper's number differ.
