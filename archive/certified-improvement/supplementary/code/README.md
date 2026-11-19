# C-TRR: code for "Certified Safe Improvement of Self-Confirming Dealer Quotes"

This folder reproduces every experiment, table, figure and number in the paper.

## Layout

- `ctrr/model.py`: the dealer markets (known profit part K, responsive flow tau, noise) and the environment.
- `ctrr/agent.py`: the C-TRR agent (Algorithm 1), the lower envelope and the certified gain.
- `ctrr/baselines.py`: UCB, conservative UCB, PerfGD (two-point), two-point tangent response, blind retraining.
- `experiments/run_all.py`: runs the experiment suites and writes `results/*.json`.
- `experiments/report.py`: reads `results/*.json` and writes every table and the file `numbers.tex`
  that the paper reads all of its numbers from.
- `experiments/figures.py`: draws the seven figures.
- `experiments/coverage.py`: re-runs C-TRR, records every confidence interval and checks coverage.
- `verification/verify_math.py`: numerical and symbolic checks of every theorem on the instance
  (`verification/verify_math.log`: 50 of 50 checks passed).
- `results/`: stored results of all runs (30 seeds each, seeds 100 to 129).

## Requirements

Python 3 with numpy and matplotlib (tested with numpy 2.5.4 and matplotlib 3.11.2);
`verify_math.py` also uses sympy and mpmath. No other packages are needed.

## Commands

Run from this folder.

```bash
python -u experiments/run_all.py                      # all suites; or name some: main ablation robust horizon noisy poisson
python -u experiments/run_all.py main --seeds 30 --procs 8
python experiments/report.py --out generated          # tables and numbers.tex
python experiments/figures.py --out figures           # all figures; --only NAME for one
python -u experiments/coverage.py                     # interval coverage check
python -u verification/verify_math.py                 # theorem checks
```

The long-horizon suite is the slowest part. All runs are deterministic given the seed: re-running the
robustness, Poisson and long-horizon suites reproduced every stored configuration exactly, the coverage
script reproduces the stored results of all 1,200 runs it re-runs, `figures.py` re-runs seed 100 and checks
the stored regret, and `report.py` checks that the fixed baseline configurations are the ones selected by the
tuning rule of the paper.

## Labels in `verify_math.py`

The verification script uses short internal names. They correspond to the paper as follows.

| Script | Paper |
|---|---|
| Proposition 1 | Proposition 1 (reservation spreads) |
| Lemma 1 | Lemma 3 (self-confirming quotes are too wide) |
| Theorem 4 | Theorem 5 (no certificate without data at other quotes) |
| Lemma 2 | Lemma 6 (tangent minorant) |
| Theorem 1 | Theorem 7 (profit ascent) |
| Theorem 2 | Theorem 8 (fixed points and rate) |
| Theorem 3 | Theorem 10 (certified gain) |
| Proposition 3 | Proposition 11 (two-anchor tightness) |
| Proposition 2 | Proposition 12 (loss of a tighter quote) |
| Theorem 5 | Lemma 13 and Theorem 14 (confidence event, anytime guarantee) |
| Proposition 4 | Proposition 15 (when a certified move happens) |
