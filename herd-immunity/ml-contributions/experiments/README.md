# Panels

```bash
python herd-immunity/ml-contributions/experiments/run_panels.py
```

Deterministic, CPU-only, about a minute. Writes JSON to `results/` and PNG to
`results/figures/`. Exits nonzero if any panel disagrees with its closed form, so
a broken derivation fails the run rather than producing a quiet figure.

## What these are, and what they are not

**These are dry runs in the linearized reference environment, not the paper's
panels.** The environment realizes the model's response geometry and nothing
else: no informed flow, no spread, no inventory. The paper's panels run in the
base project's order-flow simulator, and **every experimental claim stays at its
derivation status until they do.** Nothing here upgrades a claim to measured.

What they do establish, which is worth having ten days out:

The step from linearized spectrum to realized dynamics, which no amount of
algebra checking covers. Stability is not read off an eigensolve here; each panel
runs the actual retraining map and estimates the spectral radius from the
trajectory's asymptotic growth by power iteration.

The shape of every figure, so the simulator port has a target rather than a blank
page. A discrepancy between the simulator and these is then diagnostic: it is
microstructure, since the geometry is already known to agree.

## Results

| Panel | Tests | Outcome |
|---|---|---|
| 1, amplification | Section 3 | Reduction exact to `5.6e-16`. **External anchor closed**, see below |
| 2, `(N, s)` phase diagram | Theorem 1 | 48 cells, max error `7.1e-15` |
| 2b, clustered companion | Theorem 1 | Measured `m_N` `1.30`, mean index reports `0.74` |
| 3, cadence frontier | Theorem 2 | 175 cells, zero disagreements |
| 4, herd immunity | Theorem 3 | Thresholds `12 / 14 / 16 / 20` firms at efficacy `1.0 / 0.9 / 0.75 / 0.6` |
| 5, substitution frontier | Theorem 3 | 18 of 18 points exact |
| 6, over-adaptation | Theorem 4 | **Not written.** Theorem 4 is not derived |

## The external anchor, which is the one measured result here

```bash
"<base>/.venv/Scripts/python" herd-immunity/ml-contributions/experiments/reflex_anchor.py
```

[`reflex_anchor.py`](reflex_anchor.py) runs against the base project's **genuine
shared-pool market**: real order flow, real spreads, real inventory, CRN probes
through the full deploy-collect-fit-optimize pipeline. It is the only thing in
this folder that is `[MEASURED]` rather than `[DRY RUN]`, and it is the one panel
whose claim is the monoculture corner `R = 1 1'`, which the base project already
implements, so it could be closed without any of the heterogeneous-response work.

It reproduces the published run bit for bit, relative error `0.00e+00`:

| `N` | measured `m_N` | amplification | linear prediction | gap |
|---|---|---|---|---|
| 1 | `0.785600` | `1.0000` | `1` | |
| 2 | `1.369162` | `1.7428` | `2` | `12.9%` |
| 3 | `2.479927` | `3.1567` | `3` | `5.2%` |

The differential mode measures `3.4e-03` against a theoretical `0` at
`kappa = 1`, so the instability is purely common-mode, which is the mechanism
this paper's Theorem 1 generalizes.

**The gap is the paper's content, not its error.** The prediction is a
linearization and the market is nonlinear with saturating flow. The reference
environment reproduces the prediction exactly *because* it omits both, which is
precisely why the reference environment cannot substitute for this run.

**The probe episode count is part of the protocol, not a tuning knob.** The
paper-grade profile uses 8 episodes; the experiment's own default is 4. At 4 the
anchor lands at `1.80x` for `N = 2` rather than `1.74x`, which looks close enough
to pass unnoticed and would make the amplification law appear to fit worse than
it does. This is pinned in the script with a comment saying why.

The base project is read-only here: nothing under it is modified, and the script
skips cleanly when it is absent, so this repository stays self-contained for
anyone without a local checkout. Point at a non-default checkout with
`REFLEX_ROOT`.

**Panel 4 is where the C18 finding becomes visible.** At perfect correction the
market needs 12 of 20 firms un-blinded. At efficacy `0.90` it needs 14, at `0.75`
sixteen, and at `0.60` all twenty. The strong-correction limit says 12 in every
one of those cases, which is the optimism the derivation predicted, now drawn.

That panel also produced a finding the derivation did not claim: **the
imperfect-correction law predicted all four thresholds exactly at `kappa = 0.8`,
where it is only proved exact at `kappa = s = 1`.** Recorded in
[`../../math/derivations/04-mixed-market-secular.md`](../../math/derivations/04-mixed-market-secular.md)
as measured evidence, not upgraded to a proof.

## Reading the figures

Panel 5's markers sit on or above the continuous `rho*(s)` curve because a
threshold is a whole number of firms and the curve is continuous. The green step
line is the integer prediction, and the markers land on it at all 18 points. The
apparent offset from the smooth curve is granularity, not error.

Panel 3's frontier is drawn continuous while its cells are integer `K`, so the
realized window is `floor(K_max)`.
