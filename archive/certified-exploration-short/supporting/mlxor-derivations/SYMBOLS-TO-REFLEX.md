# Symbol -> `reflex` Package Map (the executable instantiation)

Where every constant in the derivations is *computed* in the REFLEX codebase
(`endo_market_v4/reflex/`), making D9's "computable from primitives" claim
executable. Status: **EXISTS** = present in the package today (name-checked
against the source by `verify/check_docs.py`); **CONFIG** = a configuration
field; **PLANNED** = to be added by the paper's build (module named in the
M2 implementation plan); **DERIVED** = computed from EXISTS quantities by a
stated formula, no new code needed.

| Symbol | Meaning | Where | Status |
|---|---|---|---|
| `gamma` | strong convexity | `reflex/theory/analytic_boundary.py :: gamma` | EXISTS |
| `beta` | joint smoothness (= `pnl_scale`) | `reflex/theory/analytic_boundary.py :: beta` | EXISTS |
| `eps(h)` | response slope | `reflex/theory/analytic_boundary.py :: epsilon` | EXISTS |
| `tau(h)` | toxic-flow curve | `reflex/theory/analytic_boundary.py :: tau` | EXISTS |
| `h*` (`h_SP`) | stable point | `reflex/theory/analytic_boundary.py :: solve_fixed_point` | EXISTS |
| `m` | modulus + boundary bundle | `reflex/theory/analytic_boundary.py :: analytic_boundary` | EXISTS |
| `psi, gbar` | adverse severity / gate means | `reflex/theory/analytic_boundary.py :: gate_means`, `reference_state` | EXISTS |
| `h_PO` | performative optimum | `reflex/theory/perfgd.py :: solve_performative_optimum` | EXISTS |
| `gamma_PO` | objective curvature at the optimum | `reflex/theory/perfgd.py :: gamma_po` | EXISTS |
| `h_SP - h_PO`, value gap | echo-chamber gap (feeds T8's `A`) | `reflex/theory/perfgd.py :: echo_chamber_gap` | EXISTS |
| `delta0 = Phi'(h*)` | anchor-point gradient | `reflex/theory/perfgd.py :: perfgd_correction` evaluated at `h*` | EXISTS |
| `sigma` (`sigma_tau`) | response-noise scale | `reflex/equilibrium/structural_response.py :: StructuralResponse.residual_rms` (realized); raw channel scale from `clients.info_signal_noise` | EXISTS |
| structural family `(C0, C1, c)` | the `p = 3` family of T6/T7 | `reflex/equilibrium/structural_response.py :: fit_structural_response` | EXISTS |
| `identified` flag | the anti-echo freeze T6 formalizes | `reflex/equilibrium/structural_response.py :: StructuralResponse` | EXISTS |
| `sigma_e` | exploration intensity | `config :: rrm.collection_jitter` | CONFIG |
| `r` | trust region | `config :: rrm.structural_max_rel_step` | CONFIG |
| feedback lever for `eps` sweeps | control variable (never `alpha`) | `config :: clients.toxicity_feedback` | CONFIG |
| `P = pnl_scale` | the `beta` identification | `config :: reward.pnl_scale` | CONFIG |
| per-bond `(A_a, k_a, sigma_a, ...)` | d-dim constants | `reflex/theory/factor_scaling.py :: per_bond_constants` | EXISTS |
| `Gamma` (blind, d-dim) | curvature matrix | `reflex/theory/factor_scaling.py :: curvature_matrix` | EXISTS |
| `M` (loop Jacobian, d-dim) | modulus matrix for D1's Lyapunov | `reflex/theory/factor_scaling.py :: modulus_matrix` | EXISTS |
| `rho(M)` at scale | spectral radius via Woodbury | `reflex/theory/factor_scaling.py :: spectral_radius_woodbury` | EXISTS |
| `Gamma_PO` (d-dim) | performative curvature matrix (P9.3) | separable: per-bond formula on top of `per_bond_constants` + `gamma_po`; coupled: first-order construction | DERIVED |
| `kappa = |d h_PO/d eps|` | correction sensitivity (T8) | implicit-function differentiation of `solve_performative_optimum` (finite difference in `eps` via `toxicity_feedback`) | DERIVED |
| CRN probe / measured modulus | the `m` measurement T2/T3 compare against | `reflex/estimators/br_slope.py` | EXISTS |
| `eps` triangulation | measured response for V-experiments | `reflex/estimators/triangulate.py` | EXISTS |
| saturation cap, exchange rate, feasibility, ROI | T1, T2, T3, T8 as package functions | `reflex/theory/identification.py` | PLANNED |
| design shapes + Frank-Wolfe scheduler | T5a-c + the D6 algorithm | `reflex/estimators/design.py` | PLANNED |
| certificates for all of the above | verification-layer entries | `reflex/verification/certificates.py` (+~10) | PLANNED |

**Unit discipline (inherited, binding).** On calibrated configs every width,
tolerance, probe and blur is *scale-relative* (real per-$100-par units);
`reflex/calibration/mapping.py` is the single unit-conversion point. The
design quantities (`sigma_e`, `r`, `w`) inherit this rule: the paper's
experiments express them as fractions of the configured spread scale, never
absolute numbers.
