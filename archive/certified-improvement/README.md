# Certified Safe Improvement of Self-Confirming Dealer Quotes

| | |
| --- | --- |
| **Venue** | [TMLR](https://jmlr.org/tmlr/) |
| **Status** | Superseded before submission by the lending paper in [`../../tmlr-submission/`](../../tmlr-submission/), which went to TMLR on November 19, 2026. Kept as a record and not maintained |
| **Paper** | [`certified-safe-improvement.pdf`](certified-safe-improvement.pdf), the final manuscript in the TMLR template |
| **Base paper** | REFLEX, [arXiv:2608.16155](https://arxiv.org/abs/2608.16155) |

## Thesis

A dealer's pricing model that is retrained on the order flow its own quotes attract settles at a self-confirming quote: the flow the model expects is the flow it sees, so its data never contradict it. The paper asks when a dealer can leave such a quote with a guarantee.

## Results

| Result | What it says |
| --- | --- |
| Diagnosis | The self-confirming quote is too wide whenever responsive flow falls with the spread, and no wider quote is better (Lemma 3) |
| No free certificate | Data collected at the self-confirming quote cannot certify that any other quote is better (Theorem 5) |
| Certificates | If responsive flow is nonnegative, nonincreasing and convex in the spread, samples at a few other quotes give finite-sample lower bounds on the profit gain of every candidate quote (Theorem 10), tight with two anchors (Proposition 11) |
| C-TRR | An agent that adopts a quote only when a certificate shows it raises expected profit and trials only quotes within a preset loss budget, with both properties holding in every period at once with probability at least 1 - δ (Theorem 14) |
| Price of certification | Uncertified baselines tuned per market reach lower regret in three of four markets. Fixed-width intervals cut regret by 1.9x to 4.3x but cause harmful adoptions in 189 of 720 runs |

The lemmas behind these results are machine-checked in Lean 4 (107 theorems). Appendix B of the paper maps every result to its Lean theorems and lists the steps argued only on paper.

## Folder map

| Path | Holds |
| --- | --- |
| [`supplementary/code/`](supplementary/code/) | The C-TRR agent, the baselines, the experiment suites, stored results for 30 seeds and the theorem checks. See its [README](supplementary/code/README.md) |
| [`supplementary/lean/`](supplementary/lean/) | The Lean 4 formalization, `PriceCert`. See its [README](supplementary/lean/README.md) |

## Verify

Run the theorem checks from `supplementary/code/`. They need numpy, sympy and mpmath, and all 50 pass.

```bash
cd archive/certified-improvement/supplementary/code && python verification/verify_math.py
```

Build the Lean proofs from `supplementary/lean/`. This needs the Lean toolchain in `lean-toolchain` and downloads a compiled Mathlib.

```bash
cd archive/certified-improvement/supplementary/lean && lake exe cache get && lake build PriceCert
```

## Earlier versions

This paper grew out of the certified-exploration work: an IEEE draft (*A Certified Exploration Framework for Pricing Models That Shape Their Own Data*) with its derivations and experiment pipeline, an earlier first draft and a shorter reframing. All three are elsewhere in this [`archive/`](../).
