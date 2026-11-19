# Certified Rate Changes for Lenders That Learn from Their Own Loans

| | |
| --- | --- |
| **Authors** | Shriraghav Ashok, Vignesh Nagarajan |
| **Venue** | [TMLR](https://jmlr.org/tmlr/), regular submission (submission 14693) |
| **Status** | Submitted November 19, 2026. Under double-blind review |
| **OpenReview** | [7KhnbCrUhb](https://openreview.net/forum?id=7KhnbCrUhb) |
| **Paper** | [`certified-rate-changes-tmlr.pdf`](certified-rate-changes-tmlr.pdf), the submitted anonymized PDF |
| **Supplement** | [`supplementary-material.zip`](supplementary-material.zip), the exact archive uploaded to OpenReview |
| **Base paper** | REFLEX, [arXiv:2608.16155](https://arxiv.org/abs/2608.16155) |

## Thesis

A lender that fits a take-up model to its own loan files learns only from applicants who already chose it. Most of the response to price happens earlier, when borrowers compare quotes and decide where to apply, so those files can show almost no response to the rate even when the rate is driving borrowers away. The paper asks how a lender can change its rate with a guarantee.

## Results

| Result | What it says |
| --- | --- |
| Data | In HMDA data for California, Florida and Texas in 2022 and 2023 (899,294 approved applications), take-up of approved offers is 96.3% to 97.1% and barely moves with the offered rate within a lender, while rates offered to comparable borrowers differ across lenders by several tenths of a point |
| No free certificate | If the lender assumes only that take-up falls as the rate rises, data collected at a single rate cannot certify any change |
| Cuts and increases | A rate cut giving up a fraction f of the margin risks at most a fraction f of profit for any nonincreasing take-up curve. A rate increase can lose all profit unless take-up is known to fall at a bounded rate |
| Certified rate search | Pilots small rate changes within a per-quote risk budget, uses relative-entropy confidence intervals that hold at every checkpoint, and adopts a new rate only when a direct comparison certifies higher profit |
| Simulations | In 18 markets calibrated to the HMDA dispersion, the search never exceeded its budget under a valid shape class and adopted a worse rate once in 16,200 runs. Its final rate earned 91.2% to 95.5% of optimal profit, against 99.5% for KL-UCB and 99.4% for Thompson sampling, which broke the budget in nearly every run |
| Convexity | The implied take-up curve is not convex near the rates of a large share of lenders, so the assumption that would make rate increases safe to test cannot be taken for granted |

The results, including the confidence events and the main guarantee, are proved in Lean 4: 123 theorems using only Lean's standard axioms. The code is tested against them, not verified.

## Layout

| Path | Holds |
| --- | --- |
| [`code/`](code/) | HMDA analyses (`hmda_takeup.py`, `hmda_offers.py`, `cluster_inference.py`), the lending markets, certificates and baselines (`lending/`), the experiments and report generator (`experiments/`), and the checks (`verification/`) |
| [`lean/`](lean/) | The Lean 4 development `CreditCert` (Mathlib, toolchain v4.36.0-rc2) |
| [`data/derived/`](data/derived/) | Outputs of the HMDA analyses. No loan-level records |
| [`results/`](results/) | Check logs and a subset of the simulation results |

This folder mirrors the submitted supplement except for the large simulation results. `results/main.json` (64,800 runs, 46 MB) and most of the `robust_*`, `design_*` and `safe_*` files are only in [`supplementary-material.zip`](supplementary-material.zip). Unzip it to run `check_supplement.py` or rebuild every table. The LaTeX source of the paper is not in the repo.

## Verify

```bash
cd tmlr-submission/code && python verification/verify_math.py
```

```bash
cd tmlr-submission/lean && lake exe cache get && lake build CreditCert
```

The first runs the 32 numerical checks of the paper's statements (numpy). The second builds the 123 Lean theorems; `code/verification/lean_axioms.py` does the same and prints the axioms of every theorem to `results/lean_axioms.log`.

## Rebuild tables and figures from the supplement

Python 3.13 with numpy 2.5 and matplotlib 3.11. Run from the unzipped supplement; no raw data is needed.

```bash
cd code
python -I verification/check_supplement.py     # every result file is present and complete
python -I experiments/report.py                # writes ../paper/generated/ and ../paper/figures/
```

`report.py` writes every table, every number quoted in the text (one macro per number) and the four figures. It stops with an error if a result file is missing or if a fact stated in the paper, such as the count of harmful adoptions, no longer matches the results.

## Where each table and figure comes from

| Paper item | Files | Produced by |
| --- | --- | --- |
| Table 1, Figure 1 (take-up of approved offers) | `data/derived/takeup_*.json` | `code/hmda_takeup.py` on the raw files |
| Table 2 (slopes side by side) | `data/derived/takeup_*.json`, `data/derived/offers_*.json` | `code/hmda_takeup.py`, `code/hmda_offers.py` |
| Tables 3, 8, 9 and Figure 2 (competing offers, calibration, convexity) | `data/derived/offers_*.json` | `code/hmda_offers.py` on the raw files |
| Table 7 (sample sizes) | `data/derived/*.json`, `data/derived/raw_counts.json` | the two HMDA scripts and `report.py` |
| Tables 4, 5, 11, 13 and Figure 4 (main comparison) | `results/main.json` | `code/experiments/run_markets.py` |
| Figure 3 (one run of the certified search) | `data/derived/offers_CA_2022.json` | `code/experiments/figures.py` replays the run from its seed |
| Table 12 (quotes until the first adoption) | `results/adoption_times.json` | `code/experiments/adoption_times.py` |
| Table 14 (robustness) | `results/main.json`, `results/robust_*.json` | `run_markets.py` with the options below |
| Table 15 (design parameters) | `results/main.json`, `results/design_*.json` | `code/run_design.sh` |
| Table 10 (safe UCB lattice step) | `results/safe_step*.json`, `results/safe_norefresh.json` | `run_markets.py` with the options below |
| Table 6 (results and Lean theorems) | `lean/CreditCert/*.lean`, `results/lean_axioms.log` | `code/verification/lean_axioms.py` |
| Section 4.5 (verification) | `results/verify_math.log`, `lp_check.log`, `coverage.log`, `check_baselines.log`, `determinism_check.json`, `lean_axioms.log` | the scripts in `code/verification/` |

## Rerun everything from scratch

Run scripts that read the downloaded data with `python -I`.

```bash
bash code/download_hmda.sh                       # about 0.8 GB from the CFPB Data Browser
python -I code/hmda_takeup.py data/raw/hmda_*_purchase.csv > results/hmda_takeup.log
python -I code/hmda_offers.py data/raw/hmda_*_purchase.csv > results/hmda_offers.log
cd code
python -I experiments/run_markets.py --seeds 50 --seeds-base 50 --out ../results/main.json
python -I experiments/run_markets.py --methods cert-M,cert-eta,cert-C --seeds 50 --out ../results/determinism_check.json
python -I experiments/adoption_times.py
python verification/verify_math.py > ../results/verify_math.log
python verification/lp_check.py > ../results/lp_check.log          # needs scipy
python verification/coverage.py > ../results/coverage.log
python -I verification/check_baselines.py > ../results/check_baselines.log
python verification/lean_axioms.py               # builds the Lean development; writes results/lean_axioms.log
```

Robustness variants (Table 14), 30 seeds for the certified search and 20 for the baselines:

```bash
python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --ell-rel 0.05 --out ../results/robust_budget05.json
python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --ell-rel 0.2 --out ../results/robust_budget20.json
python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --extra '{"ci": "hoeffding"}' --out ../results/robust_hoeffding.json
python -I experiments/run_markets.py --methods cert-M,cert-eta --seeds 30 --n-hist 50000 --out ../results/robust_hist.json
python -I experiments/run_markets.py --methods cert-eta --seeds 30 --extra '{"eta_mult": 0.5}' --out ../results/robust_etahalf.json
python -I experiments/run_markets.py --methods ts-own --seeds-base 20 --extra '{"own_sd_mult": 10}' --out ../results/robust_tsown10.json
python -I experiments/run_markets.py --methods ts-own --seeds-base 20 --extra '{"own_sd_mult": 100}' --out ../results/robust_tsown100.json
python -I experiments/run_markets.py --methods ts-own --seeds-base 20 --extra '{"own_level": "matched"}' --out ../results/robust_tsownlevel.json
python -I experiments/run_markets.py --methods klucb,ts --seeds-base 20 --extra '{"arms": "margin"}' --out ../results/robust_armsmargin.json
```

Design parameters (Table 15) and the safe UCB lattice step (Table 10):

```bash
PYTHON=python bash run_design.sh
python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.005}' --out ../results/safe_step0005.json
python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.01}' --out ../results/safe_step001.json
python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.02}' --out ../results/safe_step002.json
python -I experiments/run_markets.py --methods safe-M,safe-eta --seeds-base 20 --extra '{"safe_step": 0.04}' --out ../results/safe_step004.json
python -I experiments/run_markets.py --methods safe-M --seeds-base 20 --extra '{"safe_refresh": false}' --out ../results/safe_norefresh.json
```

The simulations are deterministic given their seeds, so these commands reproduce the result files exactly. In the code the break-even spread is called `psi`; the paper writes it as zeta.

## Earlier versions

This paper replaces *Certified Safe Improvement of Self-Confirming Dealer Quotes*, which was prepared for TMLR but not submitted, and the certified-exploration drafts before it. All of them are in [`../archive/`](../archive/).
