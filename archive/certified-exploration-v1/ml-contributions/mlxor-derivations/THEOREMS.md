# Theorem Register - statements, dependencies, verification, status

The results-section skeleton: every result with its final numbering,
statement (informal-precise; LaTeX twins in `latex/theorems.tex`),
assumptions cited from `derivations/00-notation-and-assumptions.md`,
derivation source, verification check IDs (per `VERIFICATION.md`), and
status. Status legend: **PV** = proved + numerically verified; **P** =
proved (no numerical content to check); **PV*** = proved for the stated
class, general case in `OPEN-PROBLEMS.md`; **COND** = proved conditional on
a stated hypothesis.

| # | Result | Statement (one line) | Assumptions | Derivation | Checks | Status |
|---|---|---|---|---|---|---|
| L1 | Cost-equivalence lemma | `C_T = (1/2) gamma_PO E[D_T] + O(E|d|^3)` under A2-sym; exact fluctuation decomposition `Var(C) = delta0^2 Var(sum d) + (gamma_PO^2/4) Var(sum d^2)`, zero cross term | A1, A2-sym, A3 | D0 sec. 3 | V0.1, V0.2, V0.3 | PV |
| T1 | Information saturation | Noiseless trajectory energy `= d_0' P d_0`, `P = I + M'PM`; Fisher info for the response bounded in every direction, uniformly in the horizon | A1, A6 | D1 sec. 1-2 | V1.1, V1.2, V1.4 | PV |
| C1.1 | Safety implies blindness | The scalar cap `d_0^2/(1-m^2)` is increasing in `m`: identifiability is a near-instability phenomenon | A1, A6 | D1 sec. 1 | V1.1 | P |
| C1.2 | Trajectory design degeneracy | Noiseless designs have <= 2 effective support points (geometric collapse; period-2 at `m = 1`) | A1 | D1 sec. 1 | (feeds T6) | P |
| R1 | Non-normal transient information | Energy exactly `d_0' P d_0` also for non-normal `M`; exceeds the spectral cap by up to `kappa(V)^2` | A6 | D1 sec. 3 | V1.3 | PV |
| T2 | The exchange rate (pathwise) | `Var(eps_hat|design) x (1/2) gamma_PO sum d^2 = (1/2) gamma_PO sigma^2 (1 + T dbar^2/S_xx)` pathwise; invariant to `sigma_e, m, T` up to `O_P(1/T)` | A1, A2-sym, A3, A6 | D2 sec. 1 | V2.1 | PV |
| P2.1 | Concentration | Measured product concentrates at rate `T^{-1/2}`; long-run `Var(sum d) = T v (1-m)/(1+m)` | A2-sym, A3, A6 | D2 sec. 2 | V2.2, V2.3 | PV |
| P2.2 | Feedback bias (full Stambaugh form) | Under A3': `bias = phi sigma^2 (3m-1)/((1-m^2) T v_phi)` - `O(1/T)`, sign change at `m = 1/3` | A3', A6 | D2 sec. 4 | V2.4, V2.5 | PV |
| T3 | Minimax lower bound, deviation budget | Over all adaptive policies (A2-adaptive) and all estimators with `D_T <= D`: risk `>= sigma^2/(D + sigma^2 (pi/w)^2)`; hence the exchange rate is a floor, met with equality | A1, A2, A3, A4 | D3 sec. 2 | V3.1, V3.2 | PV |
| L2 | Exploitation-information lemma | `E[gain] <= g1 delta^{3/2} T^{1/2} (E S_T)^{3/4} / sigma^{1/2}` via the exact identity `E|E[s|F_t]| = TV_t` + Pinsker `TV_t <= delta sqrt(E S_t)/sigma`; at the minimax scale this is an `O(T^{-1/2})` fraction of the cost - exploitation is bounded by information already purchased | A2-adaptive, A3, A4, CE anchor | D3 sec. 3 | V3.3 | PV |
| T4 | Minimax lower bound, value budget | At the minimax scale, `inf sup Var x C_T >= (1/2) gamma_PO sigma^2 (1 - O(T^{-1/2}))`, explicit constant | A1, A2-adaptive, A3, A4, A5 | D3 sec. 3 | V3.4 | PV* (two-point family; proofs.tex establishes the constant-factor version `>= gamma_PO sigma^2/27 (1 - O(T^{-1/2}))` rigorously; the sharp constant 1/2 -- numerically supported -- and general priors = OPEN-1) |
| T5a | A-optimal exploration | `min tr M^{-1}` s.t. `tr(Gamma M) <= B`: `M* ~ Gamma_PO^{-1/2}`, value `(tr Gamma_PO^{1/2})^2/B` | A1 | D4 sec. 1 | V4.1 | PV |
| T5b | D-optimal exploration | `M* = (B/d) Gamma_PO^{-1}` | A1 | D4 sec. 2 | V4.2 | PV |
| T5c | c-optimal exploration | `M* = B cc'/(c'Gamma_PO c)` - probe along the correction direction; value `c'Gamma_PO c / B` | A1 | D4 sec. 3 | V4.3 | PV |
| C5.1 | Price of isotropic jitter | Overpayment factor `F = d tr(Gamma_PO)/(tr Gamma_PO^{1/2})^2 >= 1`, `= 1` iff isotropic curvature | A1 | D4 sec. 1 | V4.4 | PV |
| L3 | Temporal-shaping lemma | Under A3, information depends on exploration only through its empirical second moment; shaping is irrelevant | A3 | D4 sec. 4 | V4.5 | PV |
| T6 | Chebyshev unidentifiability | The `p = 3` structural family needs >= 3 design support points; trajectories supply <= 2 (C1.2): curvature is invisible to retraining at every modulus | A1 | D5 | V5.1 | PV |
| L4 | Perturbed-modulus lemma | `|rho_hat - rho| <= eta beta (||e||_inf + |h*-psi| ||e'||_inf)` for `C^1` response error `e` | A1 | D6 sec. 2 | V6.1 | PV |
| R2 | Open-loop neutrality | History-independent exploration schedules cannot change the linearized contraction | A6 | D6 sec. 1 | V6.2 | PV |
| P7.1 | Safety under pessimism | With an anytime-valid confidence sequence at level `1-delta`, the pessimism rule keeps `|rho_t| <= 1 - c_margin` for all `t` w.p. `>= 1-delta` | A1, A4, valid CS | D6 sec. 3 | (conditional; CS validity is the hypothesis) | COND |
| T7 | Anchoring crossover (horizon-dependent) | `MSE_np = gamma_PO sigma^2/(2B) + (tau'''/6)^2 (2B/(gamma_PO T))^2`; anchor iff `delta_mis < ~ |tau'''| B/(3 gamma_PO T)` | A1, A3, A4 | D7 | V7.1-V7.6 | PV |
| T8 | ROI of self-knowledge | `v* = (sigma/kappa) sqrt(rho_disc)`; explore iff `rho_disc < rho* = (h_SP-h_PO)^4/(4 kappa^2 sigma^2)` - `gamma_PO` cancels | A1 | D8 sec. 1 | V8.1, V8.2 | PV |
| P9.1 | Frontier consistency (Lai-Robbins) | Any deterministic design sits exactly on the exchange-rate frontier; in particular the `O(log T)`-cost schedules | A1, A3 | D8 sec. 2 | V8.3 | PV |
| P9.2 | Isotropy contrast | Naive exploration (optimal in isotropic LQR-like settings) overpays by exactly `F` in the performative setting | A1 | D8 sec. 2 | V4.4 (cross-ref) | PV |
| P9.3 | Separable multi-bond `Gamma_PO` | `(Gamma_PO)_aa = gamma_a + beta eps_a (2 + c_t psi_a - c_t h_a)`, exact in the separable case; coupled case first-order with stated error | A1 | D8 sec. 3 (D9) | V8.4 | PV (separable); P (coupled, first-order) |

**Check accounting.** V0: 3, V1: 4, V2: 5, V3: 4, V4: 5, V5: 1, V6: 2,
V7: 6, V8: 4 - total **34**, matching `verify/last_run.log` (34/34 PASS).

**Dependency spine.** L1 -> T2 -> {T3, T4 (with L2), T8}; T1 -> {C1.1,
C1.2 -> T6}; T5a-c + L3 are independent given L1's budget form; L4 -> P7.1;
T7 stands on L1 + the D5 sensitivity family; P9.3 instantiates everything
d-dimensional. No circularities; every result's assumptions are a subset of
A1-A6 + the two anchoring conventions.

**Paper mapping (4-page cut).** Body: T1 + C1.1, T2, T3/T4 (statement + L2
mechanism), T5a/T5c + C5.1, one line each for T6-T8. Appendix: everything,
in this register's order. Journal delta: OPEN-1, OPEN-2 (see
`OPEN-PROBLEMS.md`).
