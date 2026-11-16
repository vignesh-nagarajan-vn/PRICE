# D7 - The Anchoring Crossover: Horizon-Dependent, Not Budget-Only

**Status: derived in full, including the subtlety that changes the theorem
(the nonparametric bias floor is horizon-dependent); the exact secant-bias
constant and both MSE formulas verified in V7.**

## 1. The question

REFLEX's headline empirical finding is that anchoring the response estimate
to the structural family ("structure") beats a free-form estimator
("capacity") - the v3/v4 negative-then-positive result. When is that the
right choice *in general*? The naive answer prices misspecification against
the exchange rate (`anchor iff delta_mis^2 < (1/2) gamma_PO sigma^2 / B`).
Working the derivation shows the naive answer is incomplete: the
nonparametric alternative's bias is **horizon-dependent**, and the honest
crossover involves `(delta_mis, B, T)` jointly.

## 2. The nonparametric side: local (secant) slope estimation

Estimate `eps = -tau'(h*)` from symmetric probes at `h* +/- w`, `n` probe
pairs, under the value budget and horizon:

```
   budget:   (1/2) gamma_PO * S  <=  B ,    S = 2 n w^2      (design energy)
   horizon:  2n <= T   =>   w^2 >= S / T  >=  2B / (gamma_PO T)   [budget binding]
```

**Secant bias (exact leading constant).** For the symmetric difference
quotient,

```
   ( tau(h*+w) - tau(h*-w) ) / (2w)  =  tau'(h*)  +  (tau'''(h*)/6) w^2  +  O(w^4) :
```

the even-order terms cancel by symmetry; the *second* derivative does not
enter (a point worth one sentence in the paper - symmetric probing is
already bias-optimal at its order). For the structural family
`tau = C0 + C1 e^{-ch}`: `tau''' = -c^3 C1 e^{-ch}`, so

```
   bias(w) = -( c^3 C1 e^{-c h*} / 6 ) w^2  =  ( c^2 / 6 ) * eps(h*) * w^2 * (sign) .
```

**MSE at the budget- and horizon-constrained optimum.** Variance is
`sigma^2 / S = gamma_PO sigma^2 / (2B)` (independent of how `S` splits into
`n` and `w`!), while bias requires small `w`, and the horizon caps how small:
`w^2 >= 2B/(gamma_PO T)`. Hence

```
   MSE_np  =  gamma_PO sigma^2 / (2B)   +   ( tau'''(h*)/6 )^2 * ( 2B / (gamma_PO T) )^2 .
```

**The discovered subtlety.** The bias term *falls* as `T` grows at fixed
budget: with more (cheaper, smaller) probes the nonparametric estimator
approaches the parametric rate. Nonparametric identification is not
uniformly worse - it is worse at *short horizons and fat probes*.

## 3. The parametric (anchored) side

Correctly specified family: MSE_p = `kappa_p * gamma_PO sigma^2/(2B)`, with
`kappa_p >= 1` the design efficiency for extracting `tau'(h*)` through the
family (c-optimal probing per D4 section 3 makes `kappa_p ~ 1`; the constant
is computable). Misspecified by `delta_mis` (the `C^1` distance from the
true response to the family, as in D6): an irreducible squared bias
`delta_mis^2` is added.

```
   MSE_anchor  =  kappa_p * gamma_PO sigma^2 / (2B)  +  delta_mis^2 .
```

## 4. The crossover theorem

Anchor iff `MSE_anchor < MSE_np`, i.e.

```
   delta_mis^2   <   ( tau'''(h*) / 6 )^2 * ( 2B / (gamma_PO T) )^2
                   + ( 1 - kappa_p ) * gamma_PO sigma^2 / (2B) ,
```

whose dominant first term gives the memorable form

```
   anchor   iff   delta_mis  <  | tau'''(h*) | * B / ( 3 gamma_PO T )   (approximately).
```

**Readings.** (i) Anchoring wins at short horizons, tight budgets, and
strongly curved responses; the free-form route wins asymptotically in `T`
at fixed budget. (ii) This retrodicts the v3 negative result *quantitatively*:
the free-form loop failed at modest `T` with the trust region forcing fat
effective probes - the regime the formula assigns to anchoring. (iii) It
also predicts when the finding would reverse (long horizons, generous probe
counts), which no experiment in the base project tests - a falsifiable
novel prediction. (iv) Delta over Lin-Zrnic (lit review G5): their plug-in
analysis has neither the budget nor the horizon; this formula prices both
in the paper's single currency.

## 5. Verified numerically (V7)

1. The secant-bias constant: measured `(secant - tau')/w^2 ->
   tau'''(h*)/6` for the exponential family (deterministic check, exact
   function evaluations, three `w` values extrapolated).
2. `MSE_np` formula: Monte-Carlo secant estimation at the constrained
   optimum matches the two-term formula across a `(B, T)` grid.
3. The crossover: simulated anchored fits (correct family + injected
   misspecification) vs the secant estimator; the empirical crossover
   `delta_mis*` tracks the formula within Monte-Carlo tolerance, including
   its `B/T` scaling (halving `T` doubles the crossover threshold).
