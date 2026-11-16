# 00 - Notation and Assumption Register (canonical)

Every symbol is defined **once**, here; every assumption is numbered here and
cited by number in the derivations and in `THEOREMS.md`. Where a derivation
document restates a condition, this register is authoritative.

## 1. Notation

| Symbol | Meaning | Defined in / source |
|---|---|---|
| `h`, `h_t` | deployed decision (half-spread); at step `t` | D0 |
| `h*` | performatively stable point (RRM fixed point) | REFLEX 1.1 sec. 4 |
| `h_SP`, `h_PO` | stable point (= `h*`), performative optimum | REFLEX 1.2 sec. 1 |
| `d_t` | deviation `h_t - h*` | D0 |
| `m` | retraining modulus `eps*beta/gamma in [0,1)` | REFLEX 1.1 |
| `gamma, beta, eps, psi` | curvature, smoothness, response slope, adverse severity | REFLEX 1.1 (closed forms) |
| `Phi` | true performative objective `J(h; tau(h))` | REFLEX 1.2 |
| `delta0` | `Phi'(h*) = -beta (h*-psi) eps(h*)` (nonzero) | D0 sec. 1 |
| `gamma_PO` | `-Phi''` at the operating point | REFLEX 1.2 sec. 4.1 |
| `sigma` | response-noise sd (`sigma_tau` in REFLEX) | D0 |
| `sigma_e`, `u_t` | exploration intensity / input | D0 |
| `xi_t, zeta_t` | deployment / response noise (iid, mean 0) | D0 |
| `v` | stationary deviation variance `sigma_e^2/(1-m^2)` | D2 |
| `v_phi` | ditto with feedback: `(sigma_e^2 + phi^2 sigma^2)/(1-m^2)` | D2 sec. 4 |
| `phi` | noise-feedback gain (observed flow into next deployment) | D2 sec. 4 |
| `S_xx` | centered design energy `sum (d_t - dbar)^2` | D2 |
| `D_T` | deviation budget `sum d_t^2` | D0 sec. 2 |
| `C_T` | value budget: expected incremental cost (Lemma 1) | D0 sec. 2-3 |
| `I_T` | Fisher information for `eps` | D1/D3 |
| `F_t` | history sigma-field `sigma(d_0, u_{<t}, tau_{<t})` | D0 |
| `M` | d-dim loop Jacobian (`rho(M) < 1`) | D1 sec. 2 |
| `P`, `P_u` | discrete-Lyapunov energy matrices | D1 sec. 2 |
| `Gamma_PO` | d-dim objective curvature matrix | D9 |
| `M` (design) | exploration second moment `E[d d']` - context disambiguates from the Jacobian; the design `M` appears only in D4 | D4 |
| `B` | value budget in the design problems | D4 |
| `F` | curvature dispersion `d tr(Gamma_PO)/(tr Gamma_PO^{1/2})^2` | D4 Cor. |
| `c` | correction-direction vector (c-optimality) | D4 sec. 3 |
| `s(h)` | structural-family sensitivity vector, `p = 3` | D5 |
| `w` | probe half-width (crossover analysis) | D7 |
| `delta_mis` | `C^1` misspecification of the structural family | D6/D7 |
| `kappa` | correction sensitivity `|d h_PO / d eps|` (**not** the multi-dealer spillover of the EconML companion - that symbol does not occur in this paper) | D8 |
| `rho_disc` | discount rate (ROI analysis) | D8 |
| `delta`, `s` | two-point prior half-width / its sign (minimax) | D3 |
| `g1` | `beta |h* - psi|`, coefficient of the unknown linear part | D3 |
| `TV, KL` | total variation / Kullback-Leibler | D3 |
| `r` | trust-region radius on `|d_t|` | A4 |

Conventions: ASCII math in fenced blocks; `'` denotes transpose on matrices
and derivative on scalar functions (context unambiguous); all logs natural.

## 2. Assumption register

- **A1 (local quadratic scope).** `Phi` is `C^3` and strongly concave on the
  operating interval; expansions are at `h*` with third-order remainder
  bounded by `L3 = sup |Phi'''|`. Identities are exact for the quadratic
  model and first-order accurate otherwise; the nonlinear deviation is
  *measured* (the drift study), never assumed away.
- **A2 (exploration classes).** All policies are non-anticipating
  (`u_t` is `F_t`-measurable). Two subclasses: **A2-sym** - conditionally
  symmetric (`E[u_t | F_t] = 0`), under which Lemma 1's linear term vanishes
  in expectation; **A2-adaptive** - unrestricted non-anticipating, under
  which costs are measured from the certainty-equivalent anchor (D0 sec. 4)
  and D3b's exploitation lemma applies.
- **A3 (noise exogeneity, with its named relaxation).** `zeta_t` iid, mean
  zero, variance `sigma^2`, independent of `F_t`. Relaxation A3': the
  feedback channel `phi zeta_t` into `d_{t+1}` - under A3' the exact
  `O(1/T)` bias of D2 sec. 4 applies (with the `(3m-1)` sign structure) and
  "exploration-dominant design" means `sigma_e^2 >> phi^2 sigma^2`.
- **A4 (trust region).** `|d_t| <= r` pathwise. Enters D3b's constants, the
  design problems' feasible set, and the D6 basin argument.
- **A5 (stationary-scale exploration; D3b only).** `S_T = Theta(T)`. The
  transient-dominated regime `S_T = o(T)` is governed by D1 instead.
- **A6 (stable base loop).** `m < 1` (scalar) / `rho(M) < 1` (d-dim) for all
  stationary-regime statements; boundary behaviour (`m = 1`) appears only in
  Corollary 1.2's degeneracy statement.

## 3. Anchoring conventions (the two audit-critical definitions)

1. **Incremental anchor (A2-sym results).** `C_T` is measured relative to
   the jitter-free loop at `h*`. Anchoring at `h_PO` adds the sunk
   echo-chamber term and provably destroys the D2 invariance (verified:
   the `(1 + g^2/v)` inflation).
2. **Certainty-equivalent anchor (A2-adaptive results).** `C_T` is measured
   relative to the deployment that is optimal under current posterior
   knowledge. Exploitation of *learned* structure is thereby re-anchored
   away; D3b prices only the *unlearned* residual. Both anchors coincide
   under A2-sym with an uninformative start.
