# Archive

Earlier drafts of the two PRICE papers and the planning notes behind them. Kept as a record and not maintained. The current papers live in [`../herd-immunity/`](../herd-immunity/) and [`../tmlr-submission/`](../tmlr-submission/).

Files here were moved from their original locations and keep their original contents, so relative links and paths inside them may no longer resolve.

## History

| Date (2026) | Event |
| --- | --- |
| Aug 14 to 16 | Ideation for two papers extending REFLEX, finalized into two plans of record |
| Aug 29 to Sep 1 | First full drafts of both papers |
| Sep 4 | Shorter four-page reframing of the certified-exploration paper. Later dropped |
| Sep 18 onward | Both papers rewritten in IEEE format |
| Oct 11 | Herd-immunity paper submitted to ABCSS 2026 at IEEE BigData 2026, later accepted |
| Nov 14 | Pricing paper rewritten as *Certified Safe Improvement of Self-Confirming Dealer Quotes* for TMLR, superseding the certified-exploration IEEE draft |
| Nov 17 to 18 | Pricing paper rewritten for consumer lending on HMDA mortgage data as *Certified Rate Changes for Lenders That Learn from Their Own Loans*, replacing the dealer-quotes paper before it was submitted |
| Nov 19 | Lending paper submitted to TMLR ([OpenReview](https://openreview.net/forum?id=7KhnbCrUhb)) |

## What is here

| Path | Holds |
| --- | --- |
| [`ideation/`](ideation/) | Each author's early idea notes |
| [`finalized-ideas/`](finalized-ideas/) | The two plans of record the first drafts were built against |
| [`herd-immunity-v1/`](herd-immunity-v1/) | First draft of the herd-immunity paper: LaTeX paper with versions v1 to v5 and an arXiv build, section drafts and claims ledger, review responses, status board, the original folder README, and the plan for the IEEE rewrite (`abcss-retarget-plan.md`) |
| [`certified-exploration-v1/`](certified-exploration-v1/) | First draft of the certified-exploration paper: the submitted package, the corrected `PRICE-final` paper and reports, the internal review, earlier copies of the derivations and pipeline, and the original folder README |
| [`certified-exploration-short/`](certified-exploration-short/) | The dropped four-page reframing of the certified-exploration paper, with its paper, supporting trees and submission package |
| [`certified-exploration-ieee/`](certified-exploration-ieee/) | The IEEE draft *A Certified Exploration Framework for Pricing Models That Shape Their Own Data* (`price-ieee.pdf`), its derivations with 38 numerical checks (`math/`), the SafeD-PerfGD experiment pipeline (`posk-pipeline/`), its literature review and its README |
| [`certified-improvement/`](certified-improvement/) | The dealer-quotes paper (`certified-safe-improvement.pdf`) with its C-TRR code, results and the `PriceCert` Lean 4 proofs. Prepared for TMLR, never submitted |

The derivation and pipeline trees under `certified-exploration-v1/` are earlier copies of the ones in `certified-exploration-ieee/`. The dealer-quotes paper in [`certified-improvement/`](certified-improvement/) replaced all three certified-exploration versions, and the lending paper in [`../tmlr-submission/`](../tmlr-submission/) replaced it. Each has its own code and proofs.
