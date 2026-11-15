# D3 - Minimax Lower Bounds: van Trees over Adaptive Designs, and the Exploitation-Information Lemma

**Status: (a) derived in full, verified in V3a; (b) derived with the
exploitation lemma proved and its `O(T^{-1/2})` correction established;
verified in V3b. This is the paper's flagship theory section.**

## 1. Why a lower bound is the point

D2's identity says a *specific* scheme (stationary symmetric jitter + OLS)
achieves `Var x Cost = (1/2) gamma_PO sigma^2`. The claim that makes this an
*exchange rate* - a property of the problem, not of a scheme - is that no
adaptive exploration policy and no estimator does better. Two versions,
by budget type.

## 2. Theorem 3a - deviation-budget version (exact)

**Setting.** Any exploration policy (each `u_t` any measurable function of
the history) subject to the pathwise budget `sum_{t<=T} d_t^2 <= D`; any
estimator `eps_hat` of `eps` (biased allowed).

**Theorem.** For the minimax risk over an interval of `eps` values of width
`w`,

```
   inf_{policy, estimator}  sup_{eps}  E[ (eps_hat - eps)^2 ]
        >=  sigma^2 / ( D + sigma^2 * (pi/w)^2 )
        =   (sigma^2 / D) * (1 - o(1))     as  D * (w/sigma)^2 -> infinity .
```

Hence `sup Var x (1/2) gamma_PO D >= (1/2) gamma_PO sigma^2 (1 - o(1))`:
the exchange rate is a floor.

**Proof.** Van Trees (Bayesian Cramer-Rao; Gill-Levit 1995) with prior
density `pi` supported on the width-`w` interval:

```
   E_pi E [ (eps_hat - eps)^2 ]  >=  1 / ( E_pi[ I_T(eps) ] + I(pi) ) ,
```

where `I(pi) = int (pi')^2/pi` is the prior information (`= (pi/w)^2` for
the cosine-squared prior, the minimizer) and `I_T(eps)` is the Fisher
information of the *adaptively designed* experiment. The one nonstandard
step is that `I_T` for an adaptive design is still bounded by the design
energy: by the chain rule for Fisher information over the filtration,

```
   I_T(eps) = sum_t E[ I( tau_t | F_t ; eps ) ]  =  sum_t E[ d_t^2 ] / sigma^2 ,
```

because conditionally on `F_t` the observation `tau_t` is Gaussian with mean
linear in `eps` (slope `-d_t`, and `d_t` is `F_t`-measurable) - the policy
can *place* information but cannot manufacture it. The pathwise budget gives
`E[I_T] <= D/sigma^2`. Substitute and take the sup over the interval
(`sup >= E_pi`). []

**Remarks.** (i) Biased estimators are covered - van Trees needs no
unbiasedness. (ii) The bound is achieved (up to `o(1)`) by two-point
symmetric probing at the budget with OLS, tying back to D2. (iii) The
`o(1)` is explicit: `sigma^2 (pi/w)^2 / D`.

## 3. Theorem 3b - value-budget version, and the exploitation problem

Under the value budget the policy pays `Phi(h*_CE) - Phi(h_t)` (D0's
certainty-equivalent anchor). The residual linear coefficient at the anchor
is `phi'(eps_bar)(eps - eps_bar) = -beta (h*-psi)(eps - eps_bar)`: a policy
could try to *earn while exploring* by guessing the sign of
`eps - eps_bar` and drifting accordingly. The theorem says this
self-financing is bounded by the information already purchased - you cannot
exploit what you have not yet paid to know.

**Setting.** Two-point prior `eps in {eps_bar - delta, eps_bar + delta}`,
symmetric; write `s = sign(eps - eps_bar)`, `g1 := beta |h* - psi|`
(the known coefficient of the unknown part). Policy non-anticipating;
per-step trust region `|d_t| <= r`.

**Lemma (exploitation-information).** For any non-anticipating policy,

```
   E[ gain_T ]  :=  E[ sum_t g1 delta s d_t ]
               <=  g1 delta * sum_t E[ TV_t |d_t| ]
               <=  ( g1 delta^2 / sigma ) * sqrt(S_T) * sum_t E[ |d_t| ]
               <=  ( g1 delta^2 / sigma ) * S_T * sqrt(T) ,
```

where `TV_t <= delta sqrt(S_t)/sigma` is the total-variation distance
between the two hypotheses' laws after `t` observations
(`KL_t = 2 delta^2 S_t / sigma^2`, Pinsker), and the last step is
Cauchy-Schwarz (`sum |d_t| <= sqrt(T S_T)`).

**Proof of the TV step.** The policy's knowledge of `s` at time `t` is
`|E[s | F_t]| <= TV(P^+_t, P^-_t)` (posterior imbalance is bounded by the
distinguishability of the two environments; starting prior symmetric). The
two environments differ only in the observation means, by `2 delta d_i` at
step `i`, so `KL_t = sum_{i<=t} (2 delta d_i)^2 / (2 sigma^2)
= 2 delta^2 S_t / sigma^2`; Pinsker gives
`TV <= sqrt(KL/2) = delta sqrt(S_t)/sigma`. []

**Theorem.** At the minimax-relevant prior scale
`delta = c sigma / sqrt(S_T)` (the accuracy the budget can buy - any larger
`delta` is learned exactly and any smaller is unlearnable),

```
   E[ gain_T ] <= g1 c^2 sigma sqrt(T) ,       while    E[ C_T ] = (1/2) gamma_PO S_T ~ (1/2) gamma_PO T v ,
```

so the exploitable fraction of the budget is

```
   E[gain] / E[C_T]  <=  2 g1 c^2 sigma / ( gamma_PO v sqrt(T) )  =  O( T^{-1/2} ) ,
```

and the value-budget minimax product satisfies

```
   inf sup  Var(eps_hat) x C_T  >=  (1/2) gamma_PO sigma^2 * ( 1 - O(T^{-1/2}) ) .
```

**Interpretation (the self-referential structure).** The profitable
direction is `s` - the thing being estimated. Pinsker converts "how much the
policy knows about `s`" into "how much design energy it has already spent";
so any gain is a rebate proportional to information already paid for, and
the rebate's *rate* vanishes. Knowledge cannot be bootstrapped from its own
purchase. To our knowledge no analog of this lemma exists in the
performative, pricing, or design literatures (lit review G1-G3).

**Honesty box.** (i) The constant in `O(T^{-1/2})` is explicit
(`2 g1 c^2 sigma / (gamma_PO v)`), and blows up as `v -> 0`: a policy that
barely explores can have its tiny cost substantially rebated - consistent,
since then both sides of the product are dominated by the transient (D1).
The theorem is stated for stationary-scale exploration `S_T = Theta(T)`.
(ii) `g1 = beta|h*-psi|` is `O(1)` in general; in the weak-performativity
regime it is `O(eps)`, giving the sharper `(1 - O(eps T^{-1/2}))`.
(iii) **The fixed-`delta` regime is different, and the CE anchor is why.**
At *fixed* prior separation the policy eventually learns `s` outright and
can exploit it indefinitely - the exploitation fraction does not vanish
(observed directly in V3b's first, deliberately mis-scaled run). That
regime is not a counterexample: sustained exploitation of *learned*
structure is exactly what D0's certainty-equivalent anchor re-anchors away
- once `eps` is known, the CE-optimal deployment shifts and the "gain" is
no longer measured as a rebate against exploration. The theorem's content
is about the *unlearned* residual, whose hardest instances live at the
minimax scale `delta ~ sigma/sqrt(S_T)`, and there the rebate vanishes at
rate `T^{-1/2}` (verified). State this distinction in the paper - it is
the difference between the theorem being deep and being wrong.

## 4. Verified numerically (V3)

1. **(V3a)** Bayes-risk simulation: Gaussian-prior posterior-mean estimator
   under three designs (front-loaded, spread, adaptive-greedy) with capped
   `D`: measured risk respects `sigma^2/(D + sigma^2/sigma_pi^2)` in every
   arm, with the spread design near-tight.
2. **(V3b-i)** The Pinsker chain: measured posterior imbalance
   `|E[s|F_t]|` <= `delta sqrt(S_t)/sigma` pathwise along simulated runs.
3. **(V3b-ii)** An explicitly exploiting policy (drifts by the posterior
   mean of the unknown linear term) is simulated at several `T`: its
   realized `gain/C_T` decays consistently with `O(T^{-1/2})`, and its
   achieved `Var x Cost` never falls below
   `(1/2) gamma_PO sigma^2 (1 - measured rebate)`.

## 5. Structure-proofness within reach (T9)

The floors above are nonparametric. A separate threat is a policy that
KNOWS the response family's functional form `tau(h) = C0 + C1 e^{-ch}`
and shops for designs whose parametric Cramer-Rao product undercuts the
floor. Define, for a finitely supported design `mu`,

    R(mu) = (g' M(mu)^{-1} g) * int (h - h*)^2 dmu,
    M(mu) = int s s' dmu,
    s(h)  = (1, e^{-ch}, -C1 h e^{-ch})'   (the sensitivity),
    g     = grad_theta eps(h*) = -s'(h*),

normalized so `R(mu) >= 1` says the family-knowing product is at least
the exchange-rate floor `(1/2) gamma_PO sigma^2` under the
local-quadratic (A1) cost.

**One-dimensional reduction.** The generalized Rayleigh identity plus
the bijection `u <-> phi_u = u's` between `R^3` and
`V = span{1, e^{-ch}, h e^{-ch}}` (using `C1 != 0`) gives

    g' M(mu)^{-1} g = 1 / inf{ ||phi||^2_mu : phi in V, phi'(h*) = 1 },

because `u'g = -phi_u'(h*)` (the sign squares away). So the floor holds
at `mu` iff SOME unit-slope family element is mu-cheaper than the linear
function `d(h) = h - h*`.

**The candidate and its reach.** The unique element of V with 2-jet
`(0, 1, 0)` at the anchor is

    phi0(h) = 2/c - e^{-c(h-h*)} (2/c + (h - h*)),

with expansion `phi0(x) = x - (c^2/6) x^3 + ...` in `x = h - h*`. The
pointwise domination `|phi0(x)| <= |x|` holds EXACTLY on
`x in [-2/c, inf)` (equality only at `x = 0` and `x = -2/c`), fails
strictly and exponentially below `-2/c`: the three elementary
ingredients are `1 + t < e^t` (which makes `phi0(x) - x` strictly
decreasing), `phi0' = e^{-cx}(1 + cx) > 0` above `-1/c`, and the single
sign change of `e^{-cx}(1 + cx) + 1` on `(-2/c, 0)` (since
`e^{-cx}(1+cx)` is increasing there from `-e^2` to 1). The full proof
is `latex/proofs.tex`, T9; verified V9.1.

**Consequence (T9(i)).** For any design supported in `[h* - 2/c, inf)`:
`R(mu) > 1` whenever the estimand is estimable, and `inf R = 1`,
approached by symmetric three-point designs collapsing at the anchor
(rate `delta^2`, V9.2; the limit is exact because in 2-jet coordinates
the collapsing model is the quadratic family, where every symmetric
design has `R = 1` on the nose). The trust region A4 with `r <= 2/c` is
therefore exactly the condition under which the floor is structure-proof
- not a technicality.

**The reach is exact (T9(ii)).** Below `h* - 2/c` the domination fails,
and the failure is realized: the frozen witness (support
`{1.8726, 1.8665, 1.3073, 0.05}`, weights
`{0.003329, 0.955702, 0.040697, 0.000272}` normalized, frozen anchor
`h* = 1.8461`, register market `c = 1.5`) attains

    R = 0.8516504721831888870...   (50-digit precision; V9.2),

with every support point except the `0.05` probe inside the reach: one
vanishing-weight below-reach probe breaks the floor by 15 percent. Its
TRUE-cost ratio is 1.011 > 1, so the violation lives in the
local-quadratic cost model, which is the floor's own scope. Symmetric
pair-plus-far-probe families never violate (their ratio tends to 1 from
above as the probe weight vanishes; the old scan's verdict of global
structure-proofness was a weight-grid artifact, recorded as the
eleventh measurement-forced pivot). The characterization of the full
below-reach violation set is OPEN-5.

**Sharpness and duality (adversarial campaign, certified numerics).**
(i) For finite support `X` with `m(X) = max{phi'(h*) : phi in V,
|phi| <= |h - h*| on X}`, every weighting satisfies `R(X, w) >= m(X)^2`
(scale the maximizer to unit slope and feed it to the Rayleigh infimum);
`phi0` certifies `m >= 1` within reach, and numerically the duality is
tight (`inf_w R = m^2`, LP duality), so pointwise domination is exactly
the right proof device. (ii) `phi0` is the unique unit-slope element of
V whose domination set contains a left interval at the anchor, with
maximal reach exactly `2/c`; the 2-jet-(0,1,gamma) family trades the
boundary outward only by vacating a gap just below the anchor, where the
violating designs live. (iii) The below-reach failure is generic: for
every `A > 2/c` some nonsingular design supported in `[h* - A, inf)`
has `R < 1` (certified 3-point example: `R = 0.8537`). Full write-up:
OPEN-5, journal scope.
