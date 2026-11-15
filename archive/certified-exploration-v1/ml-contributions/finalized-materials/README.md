# posk - The Price of Self-Knowledge

The ML architecture and full pipeline for the ML x OR @ NeurIPS 2026 paper
*"The Price of Self-Knowledge: Minimax Information-Cost Tradeoffs and
Optimal Exploration in Performative Systems"* - the companion
implementation of the `mlxor-derivations` math folder (theorem register
THEOREMS.md there; results here verify it end-to-end in a live pipeline).

## The architecture: SafeD-PerfGD

A learning agent for decision-dependent environments whose exploration is
**priced** (in its own objective), **shaped** (by the theory's optimal
designs), and **safety-gated** (by a pessimistic certificate on its own
closed-loop modulus). Per deployment round:

```
                 +--------------------------------------------------+
                 |                 SafeD-PerfGD                     |
                 |                                                  |
   deploy h_t    |  1. EXPLORE   D-optimal 3-point support of the   |
  ------------>  |     (design.py) structural family, re-centred    |
                 |     at the operating point, trust-region clipped |
   observe       |  2. FIT       anchored family (C0, C1, c) by     |
   tau_obs_t     |     (estimators) profile least squares +         |
  ------------>  |     anytime self-normalized confidence sequence  |
                 |  3. GATE      perturbed-modulus lemma (L4) with  |
                 |     (agents)  the family's own Lipschitz const:  |
                 |     certify eta*ci*L_fam <= margin, else FREEZE  |
                 |     the correction (blind step keeps running -   |
                 |     the anti-echo freeze, derived not tuned)     |
                 |  4. STEP      h <- h + eta (G_hat + Delta_hat),  |
                 |     Newton-scaled by gamma_PO_hat, clipped       |
                 +--------------------------------------------------+
```

Baselines: `BlindRRM` (the retraining cobweb, blind to dD/dphi) and
`JitterPerfGD` (isotropic exploration + OLS slope - the naive agent every
theorem prices), plus three published-literature baselines implemented on
the identical interface (`baselines.py`): `FDPerfGD` (Izzo-style
finite-difference PerfGD), `ZOPerfOpt` (two-point zeroth-order on noisy
P&L), and `UCBGrid` (performative-confidence-bounds explorer in the
Jagadeesan spirit).

## Layout

```
posk/
|- posk/
|  |- theory.py       closed forms (Market): gamma, eps, gamma_PO, h_SP,
|  |                  h_PO, modulus, exchange rate, saturation cap,
|  |                  crossover threshold, A-optimal design, dispersion F
|  |- env.py          StructuralEnv (the theory's world, exactly) and
|  |                  SaturatingEnv (REFLEX-style tanh cap: the measured
|  |                  out-of-scope drift cell)
|  |- estimators.py   OLS slope + anytime CS; anchored StructuralFit
|  |                  (profile LS, identified-flag); secant estimator
|  |- design.py       D-optimal 3-point support; scalar scheduler;
|  |                  isotropic baseline; Fisher matrices
|  |- agents.py       BlindRRM, JitterPerfGD, SafeD-PerfGD (with the
|  |                  design/anchor/gate ablation switches)
|  |- baselines.py    FD-PerfGD, ZO-PerfOpt, UCB-Grid (literature)
|  |- pricing.py      second domain: LQ performative pricing (exact A1)
|  |- multibond.py    d-dimensional market + VectorSafeD (shaped vs
|  |                  isotropic exploration at matched budget)
|- experiments/
|  |- run_all.py      E1-E8, E10: the measured-vs-predicted harness
|  |- run_open1.py    OPEN-1 premise check (floor vs structural family)
|  |- run_realdata.py the REFLEX-calibration leg (10 rating x regime
|  |                  cells validated against the published run)
|  |- figures.py      the 7 paper figures (results/figures/)
|- results/           RESULTS.md, OPEN1.md, REALDATA.md, CSVs, figures
|- tests/test_posk.py 9 fast unit tests
|- .github/workflows/ci.yml
```

## The verification loop (measured vs derived, with the pivots recorded)

Every experiment row compares a pipeline measurement against a closed form
from the derivations folder and stamps PASS / DRIFT / FAIL (DRIFT =
deliberately out-of-scope cell; exit code fails on FAIL only). The loop was
run repeatedly during development; **ten pivots were forced by
measurement, each recorded in the code where it happened**:

1. **E1, the feedback floor.** The noiseless saturation cap failed 4x
   against the noisy pipeline: retraining on noisy observations converts
   observation noise into deployment noise with gain 1/gamma (the A3'
   channel), adding a stationary excitation floor
   `v_fb = (sigma/gamma)^2/(1-m^2)` per step. Both closed forms now
   verified (cap within 3-8%, floor within 1-7%). Kept for the paper: even
   zero deliberate exploration carries a retraining-noise excitation floor
   - and it sits on the same exchange-rate frontier.
2. **E4, the gate is honest and therefore slow.** The pessimism gate never
   certified in 500 steps - because anytime confidence is expensive at a
   flat operating point (`gamma_PO(h_SP) = 0.17` here vs `1.42` at the
   optimum). Fixes faithful to the theory: freeze the *correction* only
   (the blind step keeps running - REFLEX's anti-echo convention, now
   derived), the family-specific L4 constant, and enough design horizon.
   Certification time is the exchange rate at work, and certification gets
   *easier* at the optimum (curvature rises) - both now measured.
3. **E4, trust accounting.** The checker's cap formula forgot that
   consecutive probes legitimately span the design support (2r); the agent
   never violated its clip.
4. **E5, misspecification must live at the operating point.** The injected
   `a e^{-2ch}` had decayed to ~1e-3 at the operating spread - the anchored
   fit rightly never saw it. Replaced by a linear leak `-a h`, which the
   family cannot represent: the anchored-MSE curve then crosses the
   nonparametric level exactly as T7 predicts.
5. **E6, raw regret is the wrong criterion.** UCB-Grid beats SafeD on
   cumulative regret - because SafeD's certification phase is a real cost,
   which is the paper's thesis (safety and identification are purchased).
   The recorded criterion is Pareto: no baseline dominates SafeD on
   (final error, regret) jointly, and the unsafe gradient baseline
   (FD-PerfGD) pays >5x SafeD's regret.
6. **E8, deterministic probes are a T6 instance.** The transplanted pricing
   agent froze forever: alternating +/-r probes make the deployed price and
   its lag perfectly anti-correlated (`p_now + p_lag = const`), so the
   own-price and reference-gain columns are collinear - design degeneracy
   exactly as T6 describes, in the wild. Randomized probe signs restore
   identification and the agent reaches `p_PO` (12.58 vs 12.5).
7. **E10, single-window risk is one chi-squared draw.** The shaped-vs-
   isotropic comparison was invisible under transit bias and window noise;
   the steady-state protocol (hold the operating point, average 10
   independent windows) recovers the T5a allocation effect: iso/shaped
   risk ratio 1.21 on a dispersed universe (static F = 1.45), null (1.00)
   on the flat control, exactly as the theory says it should be.
8. **Real data, the 75.8x config trap.** The first port of the REFLEX
   calibration used the package's dataclass defaults for the toxic channel
   (`alpha = 0.15`, `feedback = 0.22`) and missed the published run's
   YAML overrides (`0.5`, `5.0`) - moduli off by 75.8x, 0/10 cells
   matching. With the published constants the port reproduces **10/10**
   cells of `calibrated_boundaries.csv` (h*, eps* = gamma, m within
   0.5-5%). The validation harness is what caught it - the point of
   having one.
9. **E7, single-draw proxies invert - and the fair rerun moved the
   claim.** The design-off c-identification check compared one draw of
   `|c_hat - c|` and inverted between profiles (one lucky seed). The
   multi-seed fix then exposed a second bug: the "matched energy" iid arm
   had HALF the design's realized energy (`r^2/3` vs `2r^2/3` per step) -
   and once fairly funded, the apparent 3x shape effect collapsed to
   parity (RMS ratio 0.7-1.5 across seed sets). The corrected, sharper
   statement now asserted: **T6's identification cliff is a
   support/amplitude phenomenon, not a shape phenomenon** - it bites
   narrow priced jitter (E4: 7.8x at operating amplitude) and degenerate
   collinear designs (E8), while full-support jitter at transit energy
   identifies fine. The ablation rows assert that measured boundary.
10. **OPEN-1, the floor is structure-proof (premise check).** The a-priori
   threat that knowing the response family lets tight-side probes
   (sensitivity `e^{-ch}`) buy the slope below the exchange-rate floor is
   *refuted numerically*: minimizing the Cramer-Rao product over
   structure-exploiting designs gives ratio 1.005 to the floor, the
   optimum collapses back to the symmetric two-point configuration, and
   tight probes are monotonically worse (extrapolation variance in c
   dominates the sensitivity gain). See `results/OPEN1.md`; the register's
   OPEN-1 risk entry is upgraded accordingly.

Headline verified numbers (fast profile; the full profile re-runs in CI):

| Result (register) | Measured | Predicted |
|---|---|---|
| Exchange rate, 4 cells (T2) | 0.0106-0.0057, flat in sigma_e and m | 0.0106 / 0.0054 |
| Saturating-env drift (scope) | +16% above the rate | (DRIFT cell) |
| Saturation cap, 3 moduli (T1) | within 3-8% | d0^2/(1-m^2) |
| Feedback floor, 3 moduli (new) | within 1-7% | (sigma/gamma)^2/(1-m^2) |
| Dispersion ratio, d=8 (C5.1) | 1.501 | F = 1.506 |
| A-opt risk (T5a) | 0.0189 | 0.0183 |
| sd(c_hat), design arm (T6) | 0.222 | Fisher 0.248 |
| jitter/design sd ratio (T6) | 8.2x | unidentified vs identified |
| SafeD-PerfGD final h (goal) | 1.312 | h_PO = 1.296 |
| Nonparametric MSE (T7) | 0.0136 | 0.0123 |
| Anchoring crossover (T7) | crosses between a=0.2 and 0.35 | monotone crossing |
| Baseline Pareto (E6) | SafeD undominated; FD regret >5x | safety is purchased |
| Ablations (E7) | anchor/gate earn their keep; design's cliff mapped to its regime | T7/L4; T6 boundary |
| Pricing exchange rate (E8) | 4 cells exact (0.384/0.192) | LQ: A1 global, no drift |
| Multi-bond shaping (E10) | iso/shaped risk 1.21; flat control 1.00 | T5a allocation |
| Real-data port (realdata) | 10/10 cells reproduce the published run | REFLEX 07-12-2026 |
| Floor vs structure (OPEN-1) | CR ratio min 1.005; tight probes worse | structure-proof |

## Reproduce

```
pip install -r requirements.txt
python tests/test_posk.py                 # 9 unit tests, ~1 min
python experiments/run_all.py --fast      # the verification table, ~10 min
python experiments/run_all.py             # full profile, ~25 min
python experiments/run_open1.py           # OPEN-1 premise check, ~1 min
python experiments/run_realdata.py        # REFLEX-calibration leg (needs
                                          #   the REFLEX tree; else skips)
python experiments/figures.py             # the 7 figures (after run_all)
```

Deterministic from seeds; numpy only; CPU only; ASCII output.

## Relation to the paper and to REFLEX

The math lives in the companion `mlxor-derivations` folder (derivations,
theorem register, proofs, 34-check numerical suite); this repo is the
*pipeline* leg: the same closed forms verified inside a live
deploy-observe-fit-correct loop with an agent a desk could actually run.
The environment is a self-contained simplification of the REFLEX structural
market (`endo_market_v4`); the full-market instantiation (calibrated
configs, multi-bond Gamma_PO) runs through the REFLEX package per the
derivations folder's SYMBOLS-TO-REFLEX.md map.
