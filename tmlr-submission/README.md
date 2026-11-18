# Certified rate changes for lenders that learn from their own loans

Paper, code, data processing and Lean proofs.

## Layout
- `paper/` LaTeX source (TMLR style). `generated/` and `figures/` are written by `code/experiments/report.py`.
- `lean/` Lean 4 development `CreditCert` (Mathlib, toolchain v4.36.0-rc2). Build: `lake build CreditCert`.
- `code/download_hmda.sh` downloads the six HMDA extracts (CFPB Data Browser) into `data/raw/`.
- `code/hmda_takeup.py` take-up of approved offers (writes `data/derived/takeup_*.json`, including the per-lender
  sums used to pool state-years with lenders as clusters).
- `code/cluster_inference.py` lender-clustered standard errors and wild cluster bootstrap intervals from those sums.
- `code/hmda_offers.py` competing offers, implied take-up curves, convexity, calibration (`data/derived/offers_*.json`).
- `code/lending/` markets, certificates and confidence intervals, the certified rate search, baselines (including
  the safe UCB ablation), metrics.
- `code/experiments/run_markets.py` main and robustness experiments (`results/*.json`).
- `code/experiments/adoption_times.py` quotes until the first adoption (re-runs the certified runs).
- `code/experiments/report.py` numbers, tables and figures for the paper.
- `code/verification/` numerical checks of every statement (`verify_math.py`), exact LP check of the certificates
  (`lp_check.py`), adversarial coverage test of the confidence events (`coverage.py`), checks of the baselines'
  numerical routines (`check_baselines.py`), and the Lean build with the axioms of every theorem
  (`lean_axioms.py`).
- `results/` logs and results.

## Reproduce
Python 3.13 with numpy 2.5 and matplotlib 3.11 (scipy only for `verification/lp_check.py`). Run scripts that read
the downloaded data with `python -I`.

    bash code/download_hmda.sh                       # about 0.8 GB
    python -I code/hmda_takeup.py data/raw/hmda_*_purchase.csv
    python -I code/hmda_offers.py data/raw/hmda_*_purchase.csv
    cd code
    python -I experiments/run_markets.py --seeds 50 --seeds-base 50 --out ../results/main.json
    python verification/verify_math.py > ../results/verify_math.log
    python verification/lp_check.py > ../results/lp_check.log
    python verification/coverage.py > ../results/coverage.log
    python -I verification/check_baselines.py > ../results/check_baselines.log
    python verification/lean_axioms.py               # builds the Lean development; writes results/lean_axioms.log
    python -I experiments/report.py
    cd ../paper && pdflatex main && bibtex main && pdflatex main && pdflatex main

## Where each result in the paper comes from
| Paper item | Script | Input |
|---|---|---|
| Table 1, Figure 1 (take-up of approved offers) | `code/hmda_takeup.py` | `data/raw/*.csv` -> `data/derived/takeup_*.json` |
| Table 2, slope table, Figure 2, calibration and convexity tables | `code/hmda_offers.py` | `data/raw/*.csv` -> `data/derived/offers_*.json` |
| Main table, tables by start and by K, difference tests, Figures 3 and 4 | `code/experiments/run_markets.py` | `results/main.json` |
| Robustness and design-parameter tables | `code/experiments/run_markets.py` with the options in `code/run_design.sh` and the README commands | `results/robust_*.json`, `results/design_*.json` |
| Determinism check | second pass of the certified runs | `results/determinism_check.json` |
| Quotes until the first adoption (Table in Appendix D) | `code/experiments/adoption_times.py` (re-runs the certified runs with their seeds; checks that all 16,200 reproduce `main.json`) | `results/adoption_times.json` |
| Numerical checks of every statement | `code/verification/verify_math.py` | `results/verify_math.log` |
| Exact linear-programming check of the certificates | `code/verification/lp_check.py` | `results/lp_check.log` |
| Adversarial coverage of the confidence events | `code/verification/coverage.py` | `results/coverage.log` |
| Checks of the baselines' numerical routines | `code/verification/check_baselines.py` | `results/check_baselines.log` |
| Lean build and axioms of every theorem | `code/verification/lean_axioms.py` (`lake build CreditCert`, `#print axioms`) | `results/lean_axioms.log` |

`code/experiments/report.py` turns these files into `paper/generated/numbers.tex`, the tables and the figures. It
stops with an error if a number quoted in the text is missing or if a fact stated in prose (for example, the count
of harmful adoptions) no longer matches the results.

## Robustness commands
    python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --ell-rel 0.05 --out ../results/robust_budget05.json
    python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --ell-rel 0.2 --out ../results/robust_budget20.json
    python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --extra '{"ci": "hoeffding"}' --out ../results/robust_hoeffding.json
    python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --n-hist 50000 --out ../results/robust_hist.json
    python -I experiments/run_markets.py --methods cert-eta --seeds 30 --extra '{"eta_mult": 0.5}' --out ../results/robust_etahalf.json
    python -I experiments/run_markets.py --methods ts-own --seeds-base 20 --extra '{"own_sd_mult": 10}' --out ../results/robust_tsown10.json
    python -I experiments/run_markets.py --methods ts-own --seeds-base 20 --extra '{"own_sd_mult": 100}' --out ../results/robust_tsown100.json
    python -I experiments/run_markets.py --methods ts-own --seeds-base 20 --extra '{"own_level": "matched"}' --out ../results/robust_tsownlevel.json
    python -I experiments/run_markets.py --methods klucb,ts --seeds-base 20 --extra '{"arms": "margin"}' --out ../results/robust_armsmargin.json
    python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.005}' --out ../results/safe_step0005.json
    python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.01}' --out ../results/safe_step001.json
    python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.02}' --out ../results/safe_step002.json
    python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.04}' --out ../results/safe_step004.json
    python -I experiments/run_markets.py --methods safe-M --seeds-base 20 --extra '{"safe_refresh": false}' --out ../results/safe_norefresh.json
    python -I experiments/run_markets.py --methods cert-M,cert-eta,cert-C --seeds 50 --out ../results/determinism_check.json
    PYTHON=python bash run_design.sh
    python -I experiments/adoption_times.py
