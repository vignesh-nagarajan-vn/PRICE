# Disposition of the mlxor-review ranked action list (00-EXECUTIVE-SUMMARY.md)

Checked against the shipped tree on 1 Sep 2026. "Done" means verified in this
build, not remembered from an earlier one.

| # | Item | Status | Evidence in this build |
|---|------|--------|------------------------|
| 1 | Rescope Theorem 2(ii) to the Le Cam constant | Done | Theorem 2 states gamma_PO sigma^2/27; the sharp 1/2 is labelled numerically supported and open (OPEN-1) in the abstract, theorem, and limitations |
| 2 | Fix the three wrong body claims (known-c 0.05, "wider spread", van Trees prior term) | Done | known-c ratio 0.04 traces to run_open1.py section D; Section 2 says tighter spread; Theorem 2(i) carries the prior term sigma^2/(D + sigma^2 (pi/w)^2) |
| 3 | neurips_2026.sty with the workshop option | Done, with one caveat | Build uses neurips_2026 with dblblindworkshop (anonymous). The CFP said single-blind on 25 Aug; it was unreachable from this environment today, so the build stays anonymous and the one-token swap to sglblindworkshop is documented in the checklist |
| 4 | Close the citation gaps (Bracale et al.; market making) | Done | bracale2025reverse, gueant2013inventory, barzykin2026quoting all cited in main.tex with dispatch sentences |
| 5 | Tail-average metric replacing last-iterate | Done | TAIL=300 in run_all.py; STABILITY.md worst spread 0.0062 against tolerance 0.01; e7 cells stable |
| 6 | Assumption labels and an in-PDF register | Done | A1-A6 defined at the top of Appendix B; Section 2 labels corrected; Theorem 1 cites A1, A2-sym, A3, A6 |
| 7 | F = 1.63 traceable, check_docs crash, CI workflows | Done | F_port block in run_realdata.py (F = 1.6252); check_docs.py passes 38/38 with a C4 skip guard; verify.yml and ci.yml present in both trees |
| 8 | Seed-swept baselines with error bars | Done | E6 baseline table is a 12-seed median + IQR with per-seed Pareto reporting |
| 9 | Em dash pass, "converges when", double modulus, orphan proofs, T6 parenthetical | Done | 0 em dashes in main.tex and all body tex; "converges iff" absent; T6 proof carries the correct two-line argument |
| 10 | Camera-ready: ship real-data inputs; verify-then-cite Zhang, Hou and Zhang | Declined (both halves) | The validation inputs are not in this repository and cannot be shipped from here; the paper says where they live (the REFLEX repository) and flags the leg as externally validated. Zhang, Hou and Zhang was never read in full (arXiv unreachable from this environment), so under the review's own verify-before-citing rule it stays uncited |
| 11 | Journal track: OPEN-1 conditional van Trees, structure-proofness equivalence, P7.1 lift, multi-bond coupling, L3 under A3' | One item done, rest declined | The structure-proofness item became Theorem 3 (T9): proved on the exact reach h >= h* - 2/c with the infimum exactly 1, refuted beyond it (witness 0.8517 at 50-digit precision). The review's guess that the infimum is 1, not 1.005, was confirmed. The remaining four items are journal-version scope, not workshop-deadline scope |

Declines in one line each:

- Real-data inputs: not present in this repository; shipping them is not
  possible from here, and the paper already states their location honestly.
- Zhang, Hou and Zhang (arXiv:2602.03049): unread (network egress blocked);
  citing an unread paper violates the review's own rule.
- OPEN-1 sharp constant, P7.1 lift, multi-bond coupling, L3 under A3':
  months-scale journal work, explicitly ranked post-deadline by the review.
