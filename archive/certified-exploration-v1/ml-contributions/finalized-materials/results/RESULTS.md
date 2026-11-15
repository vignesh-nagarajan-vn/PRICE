# Pipeline results vs theory

| Exp | Claim | Measured | Predicted | Tol | Status |
|---|---|---|---|---|---|
| E1 | noiseless energy = saturation cap (m=0.30) | 0.010857 | 0.010989 | 10% | PASS |
| E1 | noisy energy growth rate = feedback floor (m=0.30) | 0.015088 | 0.014989 | 30% | PASS |
| E1 | noiseless energy = saturation cap (m=0.60) | 0.014994 | 0.015625 | 10% | PASS |
| E1 | noisy energy growth rate = feedback floor (m=0.60) | 0.020716 | 0.020675 | 30% | PASS |
| E1 | noiseless energy = saturation cap (m=0.85) | 0.033748 | 0.036036 | 10% | PASS |
| E1 | noisy energy growth rate = feedback floor (m=0.85) | 0.043269 | 0.046214 | 30% | PASS |
| E2 | Var x Cost (m=0.3, s_e=0.05) | 0.010621 | 0.010558 | 15% | PASS |
| E2 | Var x Cost (m=0.3, s_e=0.15) | 0.010696 | 0.010558 | 15% | PASS |
| E2 | Var x Cost (m=0.6, s_e=0.05) | 0.0054946 | 0.0053539 | 15% | PASS |
| E2 | Var x Cost (m=0.6, s_e=0.15) | 0.0056856 | 0.0053539 | 15% | PASS |
| E2 | drift cell: saturating env (out of A1 scope) | 0.0062244 | 0.0053539 | 0% | DRIFT |
| E3 | isotropic/A-optimal risk ratio = dispersion F | 1.529 | 1.5063 | 12% | PASS |
| E3 | A-opt risk matches sigma^2 (tr G^{1/2})^2 / (T B) | 0.0064248 | 0.0068504 | 12% | PASS |
| E4 | design arm sd(c_hat) matches Fisher prediction | 0.23364 | 0.24784 | 50% | PASS |
| E4 | jitter arm unidentified (sd ratio jitter/design >= 3: ratio=7.8) | 1 | 1 | 0% | PASS |
| E4 | SafeD-PerfGD settles at the performative optimum | 1.3237 | 1.2964 | 8% | PASS |
| E4 | trust region never violated (max step/cap=0.88 <= 1) | 1 | 1 | 0% | PASS |
| E5 | nonparametric MSE at (B,T) optimum | 0.013205 | 0.012318 | 15% | PASS |
| E5 | anchored beats nonparametric when well-specified (a=0) | 1 | 1 | 0% | PASS |
| E5 | anchored loses under gross misspecification (a=0.35) | 1 | 1 | 0% | PASS |
| E6 | SafeD final error within 1.5x of best baseline | 1 | 1 | 0% | PASS |
| E6 | no baseline Pareto-dominates SafeD on (error, regret) | 1 | 1 | 0% | PASS |
| E6 | unsafe baseline (FD-PerfGD) pays >5x SafeD regret | 1 | 1 | 0% | PASS |
| E7 | full architecture reaches h_PO (err < 0.1) | 1 | 1 | 0% | PASS |
| E7 | design-off still converges at matched transit energy (T6's cliff is support/amplitude - see E4, E8 - not shape) | 1 | 1 | 0% | PASS |
| E7 | matched-energy c-identification in the parity band (0.3 <= RMS ratio <= 3.5, no cliff either way) | 1 | 1 | 0% | PASS |
| E7 | anchor-off degrades final error (T7 prediction) | 1 | 1 | 0% | PASS |
| E7 | gate discipline: gated cells freeze, ungated never do | 1 | 1 | 0% | PASS |
| E8 | pricing exchange rate (g=0.4, s_e=0.2) | 0.384 | 0.384 | 12% | PASS |
| E8 | pricing exchange rate (g=0.4, s_e=0.5) | 0.384 | 0.384 | 12% | PASS |
| E8 | pricing exchange rate (g=0.7, s_e=0.2) | 0.192 | 0.192 | 12% | PASS |
| E8 | pricing exchange rate (g=0.7, s_e=0.5) | 0.192 | 0.192 | 12% | PASS |
| E8 | transplanted SafeD reaches the pricing optimum | 12.583 | 12.5 | 8% | PASS |
| E10 | dispersed universe: shaped beats isotropic at steady state (ratio > 1.15) | 1 | 1 | 0% | PASS |
| E10 | flat-control universe: shaping is null (|ratio-1| < 0.25) | 1 | 1 | 0% | PASS |
| E10 | agents reach the anchored-bond optima (shaped err < 0.2) | 1 | 1 | 0% | PASS |

36 rows, 0 FAIL
