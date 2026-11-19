<div align="center">

# PRICE

**Performative Risk In Coupled Environments**

Two papers on what it costs when models retrain on data their own predictions shaped.

<p align="center"><sub><b>Languages & Tools:</b></sub></p>
<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
  <img src="https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white">
  <img src="https://img.shields.io/badge/latex-%23008080.svg?style=for-the-badge&logo=latex&logoColor=white">
  <img src="https://img.shields.io/badge/lean_4-0F3D5C?style=for-the-badge">
</p>

</div>

PRICE extends REFLEX ([GitHub](https://github.com/vignesh-nagarajan-vn/REFLEX), [arXiv:2608.16155](https://arxiv.org/abs/2608.16155)) from a single learner to dynamic, coupled settings. Both papers put a price on a feedback loop. One prices it privately, as the cost a single decision-maker pays to learn its own influence. The other prices it socially, as the cost each firm's retraining imposes on every other firm in the market.

Built by Shriraghav Ashok and Vignesh Nagarajan.

## Papers

| Paper | Prices the loop | Status | Read |
| --- | --- | --- | --- |
| **Herd Immunity and Learning Externalities in Markets of Shared Foundation Models** | Socially | Accepted at [ABCSS 2026](https://css-japan.com/abcss2026/), a workshop at IEEE BigData 2026 | [PDF](herd-immunity/ieee-abcss/submission/abcss2026-herd-immunity.pdf) · [folder](herd-immunity/) |
| **Certified Rate Changes for Lenders That Learn from Their Own Loans** | Privately | Submitted to [TMLR](https://jmlr.org/tmlr/) on November 19, 2026, under review ([OpenReview](https://openreview.net/forum?id=7KhnbCrUhb)) | [PDF](tmlr-submission/certified-rate-changes-tmlr.pdf) · [folder](tmlr-submission/) |

## Layout

| Path | Holds |
| --- | --- |
| [`herd-immunity/`](herd-immunity/) | The herd-immunity paper, its proofs, certificates and experiment harness |
| [`tmlr-submission/`](tmlr-submission/) | The lending paper as submitted to TMLR, its HMDA analyses, code, results and Lean 4 proofs, and the uploaded supplement |
| [`archive/`](archive/) | Earlier drafts of both papers, including the dealer-quotes paper the lending paper replaced, and the planning notes |

Each paper folder has its own README with the results, the folder map and what is and is not verified.

## Run the checks

Every result in both papers has a check that fails loudly on disagreement.

```bash
for f in herd-immunity/ml-contributions/certificates/verify_*.py; do python "$f" || break; done
```

```bash
cd tmlr-submission/code && python verification/verify_math.py
```

```bash
cd tmlr-submission/lean && lake exe cache get && lake build CreditCert
```

The first runs 542 assertions across eight certificate files and needs only NumPy. The second runs the 32 numerical checks of the lending paper. The third builds the 123 Lean 4 theorems behind that paper.

## Archive

Earlier drafts of both papers and the planning notes that led to them are kept under [`archive/`](archive/) with their own [README](archive/README.md). Nothing there is maintained.
