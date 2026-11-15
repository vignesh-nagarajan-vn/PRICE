# D2 - The Exchange Rate: Pathwise Identity, Concentration, and the Feedback Bias

**Status: identity verified to 0 relative error (pre-existing check);
pathwise refinement, concentration rate, and the feedback-bias constant
derived here and verified in V2.**

## 1. The identity, upgraded from expectation to pathwise

Stationary jittered loop: `d_{t+1} = -m d_t + sigma_e xi_t`, stationary
variance `v = sigma_e^2/(1 - m^2)`. OLS of `tau_t` on `h_t` has
conditional-on-design variance `Var(eps_hat | design) = sigma^2 / S_xx`,
`S_xx = sum (d_t - dbar)^2`. The Lemma-1 cost is
`(1/2) gamma_PO sum d_t^2`.

**Proposition (pathwise identity).** On every realization,

```
   Var(eps_hat | design) * (1/2) gamma_PO sum_t d_t^2
        =  (1/2) gamma_PO sigma^2 * ( sum d_t^2 / S_xx )
        =  (1/2) gamma_PO sigma^2 * ( 1 + T dbar^2 / S_xx ) .
```

Since `dbar -> 0` a.s. at rate `T^{-1/2}` in the stationary regime, the
product equals `(1/2) gamma_PO sigma^2 * (1 + O_P(1/T))` **pathwise** - a
strictly stronger statement than the in-expectation identity, and the form
the experiments actually measure. The correction term `T dbar^2/S_xx` is
nonnegative: the realized product can only sit *above* the constant, by a
vanishing amount.

**Invariance.** Neither `sigma_e`, nor `m`, nor `T` appears: more jitter
buys information and burns value at the same rate; a larger modulus
amplifies the jitter into more excitation and more cost at the same rate.
The constant `(1/2) gamma_PO sigma^2` is the exchange rate between
self-knowledge and value.

## 2. Concentration (the identity is observable)

The realized *value* cost (Lemma 1) carries the linear-term fluctuation
`-delta0 sum d_t`. In the stationary regime `sum d_t` is a mean-zero
weakly-dependent sum, so

```
   sd( realized C_T ) / E[C_T]  =  O( 1/sqrt(T) ) ,
```

with the explicit leading constant: `Var(sum d_t) = T v (1-m)^{-2}(1+o(1))`
(the AR(1) long-run variance: `v * (1+rho)/(1-rho)` with `rho = -m`, i.e.
`v (1-m)/(1+m)` - note the *negative* autocorrelation of the cobweb
*shrinks* the fluctuation below iid, a small bonus worth one sentence in the
paper). Hence the measured product concentrates at rate `T^{-1/2}`.
Verified in V2 by doubling `T` and checking the variance quarter... halves
as `1/T`.

## 3. Detail: `S_xx` vs `sum d_t^2`

The estimator uses centered `S_xx`; the cost uses raw `sum d_t^2`. Their
ratio is `1 + T dbar^2/S_xx = 1 + O_P(1/T)` as above. All statements in the
paper use whichever is natural and record the `O(1/T)` equivalence once, in
this section's form.

## 4. The feedback (predetermined-regressor) bias, with its constant

In the real loop the *observed* response feeds the next deployment: model
this as

```
   d_{t+1} = -m d_t + sigma_e xi_t + phi zeta_t ,
```

with `phi` the noise-feedback gain (retraining on the realized flow moves
the next quote by `phi zeta_t`). Now `d_t` is correlated with past `zeta`,
so the regressor is predetermined but not strictly exogenous.

**Proposition (Stambaugh-type bias, full form - corrected by
verification).** The OLS slope satisfies

```
   E[ eps_hat - (-eps) ]  =  phi sigma^2 (3m - 1) / ( (1 - m^2) * T * v_phi )  * (1 + o(1)) ,
```

where `v_phi = (sigma_e^2 + phi^2 sigma^2)/(1 - m^2)` is the stationary
variance of the feedback loop. The bias is `O(1/T)`, proportional to the
feedback gain - **and changes sign at `m = 1/3`**: slow-contracting loops
bias the slope estimate upward, fast-contracting ones downward, and at
`m = 1/3` exactly the feedback bias vanishes at first order.

**Derivation (both terms; the first draft kept only the first and was
falsified by V2 - recorded per the falsification convention).** Write
`b_hat - b = N/S`, `N = sum (d_t - dbar) zeta_t`, `S = S_xx`, and expand
`E[N/S] = E[N]/E[S] - Cov(N, S)/E[S]^2 + O(T^{-2})`.

*Centering term.* `E[d_t zeta_t] = 0` (zeta_t independent of the past-built
`d_t`), so `E[N] = -E[dbar sum zeta_t]`; with
`E[d_s zeta_t] = phi sigma^2 (-m)^{s-t-1}` for `s > t`,

```
   E[N] = -(1/T) sum_{s>t} phi sigma^2 (-m)^{s-t-1} = - phi sigma^2/(1+m) + O(1/T) .
```

*Covariance term (the one the first draft missed).* By the Gaussian
fourth-moment (Wick) expansion, `Cov(N, S) = 2 sum_{t,s} E[d~_t d~_s]
E[d~_s zeta_t]` with `d~ = d - dbar`; substituting
`E[d~_t d~_s] ~ v_phi (-m)^{|s-t|}` and the cross-covariance above,

```
   Cov(N, S) = 2 v_phi phi sigma^2 sum_{k>=1} (-m)^k (-m)^{k-1} * T
             = - 2 v_phi phi sigma^2 T m / (1 - m^2) .
```

*Combine.* With `E[S] ~ T v_phi`:

```
   bias = [ -1/(1+m) + 2m/(1-m^2) ] * phi sigma^2 / (T v_phi)
        = (3m - 1)/(1 - m^2) * phi sigma^2 / (T v_phi) .    []
```

Verified in V2 at two moduli straddling the sign change (`m = 0.5`:
positive; `m = 0.2`: negative), each within Monte-Carlo tolerance of the
constant - the sign change is the sharpest possible falsification test of
the two-term structure, and it passes.

**Paper usage.** State the identity under exploration-dominant design; report
the bias formula as the *known, computable* deviation - a checkable condition
(`phi` is estimable from the loop's own update rule), not an assumption.

## 5. Verified numerically (V2)

1. Pathwise product = `(1/2) gamma_PO sigma^2 (1 + T dbar^2/S_xx)` exactly.
2. Product concentration: seed-variance of the measured product scales as
   `1/T` (factor-4 drop when `T` quadruples, within MC tolerance).
3. Long-run variance of `sum d_t` matches `T v (1-m)/(1+m)`.
4. Feedback bias: sign, magnitude and `1/T` scaling of
   `-phi/((1+m) T v_phi)`.
