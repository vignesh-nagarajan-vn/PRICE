# D0 - The Model, the Two Budgets, and the Cost-Equivalence Lemma

**Status: derived in full; verified numerically (verify_all.py section V0).**
Everything downstream (D1-D8) consumes the definitions and Lemma 1 proved
here. Notation follows REFLEX theory 1.1/1.2 (`gamma`, `beta`, `epsilon`,
`psi`, `h_SP`, `h_PO`); mathematics in fenced ASCII blocks per repo
convention.

---

## 1. The local model

Work in a neighbourhood of the performatively stable point `h*` (the RRM
fixed point, 1.1 section 4). Write deviations `d_t := h_t - h*`.

```
   deployment:   d_{t+1} = -m d_t + u_t                    (retraining cobweb + exploration)
   response:     tau_t   = tau(h*) - eps d_t + zeta_t      (observed flow)
```

- `m = eps*beta/gamma in [0, 1)` is the retraining modulus (1.1, closed form).
- `u_t` is the exploration input chosen by the operator; it may be iid noise
  (`u_t = sigma_e xi_t`), a deterministic schedule, or adaptive
  (`F_t`-measurable, `F_t = sigma(d_0, u_0..u_{t-1}, tau_0..tau_{t-1})`).
- `zeta_t` iid, mean zero, variance `sigma^2`, independent of `F_t` (the
  feedback-violation of this assumption is quantified in D2 section 4).
- Estimand: the response slope `eps` (scalar here; the d-dimensional and
  structural-family versions in D4/D5).

The true performative objective `Phi(h) = J(h; tau(h))` (1.2) is smooth and
strongly concave on the operating interval with

```
   Phi'(h*)  = Delta(h*) = -beta (h* - psi) eps(h*)  =: delta0   (nonzero: h* != h_PO)
   Phi''(h*) = -gamma_PO                                          (1.2 section 4.1)
```

## 2. The two budgets

```
   deviation budget:   D_T := sum_{t<=T} d_t^2                       (realized design energy)
   value budget:       C_T := E[ sum_{t<=T} ( Phi(h*) - Phi(h_t) ) ] (expected incremental cost)
```

`D_T` is the tracking-error form (a desk's deviation limit): observable,
policy-independent in meaning, and the correct constraint for the exact
minimax theorem (D3a). `C_T` is the realized-P&L form. Lemma 1 relates them.

## 3. Lemma 1 (cost equivalence)

**Claim.** For any exploration rule that is *non-anticipating and
conditionally symmetric* (`E[u_t | F_t] = 0`; e.g. iid or scheduled
sign-symmetric jitter), in the regime where third-order terms are negligible,

```
   C_T = (1/2) gamma_PO * E[ D_T ]  +  R_T ,      |R_T| <= (L3/6) * E[ sum |d_t|^3 ] ,
```

with `L3 = sup |Phi'''|` on the operating interval. The linear term
contributes exactly zero to the expectation and contributes fluctuation of
standard deviation `|delta0| * sqrt(Var(sum d_t))` to the *realized* cost.

**Proof.** Taylor-expand at `h*`:

```
   Phi(h*) - Phi(h_t) = -delta0 d_t + (1/2) gamma_PO d_t^2 + r_t,   |r_t| <= (L3/6)|d_t|^3 .
```

Sum and take expectations. For the linear term: `d_t` is built from
`{u_s}_{s<t}` via the linear recursion, so `E[d_t]` obeys
`E[d_{t+1}] = -m E[d_t] + E[u_t]`; conditional symmetry gives
`E[u_t] = E[E[u_t|F_t]] = 0`, hence `E[d_t] = (-m)^t E[d_0]`. Starting at the
operating point (`d_0 = 0`) or in the stationary regime, `E[d_t] = 0` for all
`t`, so `E[sum delta0 d_t] = 0`. The quadratic term gives
`(1/2) gamma_PO E[D_T]`. []

**Fluctuation decomposition (exact, and a corrected earlier claim).** The
realized cost's variance splits into two terms with **zero cross term**
(the cross moment `E[d_t * d_s^2]`-sums vanish by the sign symmetry of the
stationary law):

```
   Var( C_T^realized )  =  delta0^2 Var( sum d_t )  +  (gamma_PO^2/4) Var( sum d_t^2 ) ,
   Var( sum d_t )   ~  T v (1-m)/(1+m)          (long-run variance, negative autocorrelation helps)
   Var( sum d_t^2 ) ~  T * 2 v^2 (1+m^2)/(1-m^2)   (Gaussian stationary AR(1))
```

An earlier draft asserted the linear term always dominates; the first
verification run falsified that at moderate `delta0` (measured
sd-ratio 1.62, exactly reproduced by the two-term formula), and the claim is
now stated as the full decomposition - which term dominates depends on
`delta0^2 (1-m)/(1+m)` vs `(gamma_PO^2 v/2)(1+m^2)/(1-m^2)`, both
computable. Recorded per the falsification convention; V0 now verifies the
decomposition itself.

**Why the anchoring is load-bearing (recorded from the audit).** Anchoring
the cost at the performative optimum `h_PO` instead adds
`T * (h* - h_PO)^2`-type terms that are paid *whether or not the operator
explores* - the sunk echo-chamber cost of blindness (1.2, 6b). Numerically
(verify_m2_identity.py, Claim 3): the mis-anchored product equals
`(1/2) gamma_PO sigma^2 (1 + g^2/v)`, destroying the D2 invariance. The
incremental anchor at `h*` is the definition under which every later theorem
is true.

## 4. The certainty-equivalent anchor (needed for adaptive minimax, D3b)

For *adaptive* policies the symmetric-exploration condition can be violated
deliberately: since `delta0 != 0`, drifting toward `h_PO` earns first-order
value. Two observations discipline this:

1. Decompose `Phi'(h*)` as a function of the estimand:
   `phi(eps) := Phi'(h*; eps) = -beta (h* - psi) eps` - *linear in `eps`*.
   Under a prior centred at `eps_bar`, split
   `phi(eps) = phi(eps_bar) + phi'(eps_bar)(eps - eps_bar)`.
2. The first (known) part is exploitable *without any learning*: it is a pure
   consequence of already-known information, i.e. of choosing the anchor
   wrongly. Define therefore the **certainty-equivalent anchor** `h*_CE`: the
   deployment that is optimal under current knowledge (the posterior mean),
   and measure exploration cost relative to the trajectory that sits at
   `h*_CE`. Relative to that anchor the residual linear coefficient is
   `phi'(eps_bar)(eps - eps_bar) = -beta(h*-psi)(eps - eps_bar)`, which has
   **zero prior mean** - only genuinely *unknown* structure can be exploited,
   and D3b bounds that exploitation by the information already purchased.

This definition also matches practice: a desk's exploration cost is measured
against its own current best policy, not against an oracle's.

## 5. What is verified numerically (V0)

1. `E[C_T] = (1/2) gamma_PO E[D_T]` within Monte-Carlo error, for a
   quadratic-plus-linear objective with `delta0 != 0`, under iid exploration.
2. The realized-cost fluctuation scale matches `|delta0| sd(sum d_t)`
   (the linear term is a variance contribution, not a bias).
3. A deliberately asymmetric (drifting) exploration rule breaks the lemma in
   the predicted direction and by the predicted first-order amount
   `-delta0 * E[sum d_t]` - the lemma's condition is necessary, not
   decorative.
