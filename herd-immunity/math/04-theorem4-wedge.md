# Theorem 4: the Pigouvian wedge

The externality formalized rather than narrated. This is the section an economics
reviewer looks for after reading the framing, and its absence is what would make
the paper read as an ML paper wearing economics vocabulary.

**Status: complete.** Certified in
[`verify_theorem4_wedge.py`](../ml-contributions/certificates/verify_theorem4_wedge.py).
The welfare page below replaces the sketch this note carried until 18 Aug 2026.

---

## 1. The welfare object

Take the linearized joint map of [`00-notation.md`](00-notation.md) and drive it
with noise. Under (A1) and (A5) the binding mode is the common one, whose
deviation `z_t` from the joint equilibrium obeys

```
   z_{t+1}  =  - m_N z_t  +  xi_t ,        xi_t  iid,  mean 0,  variance sigma^2 .
```

This is an AR(1) with coefficient `-m_N`. Stationarity requires `|m_N| < 1`,
which is exactly the stability condition the rest of the paper works with, and
taking variances of both sides of a stationary solution gives
`V = m_N^2 V + sigma^2`, hence

```
   V(m_N)  =  sigma^2 / ( 1 - m_N^2 ) .
```

**On the sign convention.** The coefficient is `-m_N` and not `m_N`, because the
retraining Jacobian is `J = -m_1[(1-kappa)I + kappa R]` and the common mode
inherits its sign. The stationary variance is blind to that sign, since the
recursion enters squared, which is why the same `1/(1 - m_N^2)` serves both. The
sign is not lost information: it reappears in the lag-1 autocorrelation, which is
`-m_N` and therefore **negative**, so a crowded market shows oscillatory rather
than persistent common-mode error. That is the observable Section 8's estimator
reads, and it is the reason a positive-autocorrelation diagnostic would look for
the wrong thing. Both facts are certified rather than asserted, which closes open
item 2.

`V` is the paper's price of instability, and it is a modeling choice defended
rather than assumed: stationary variance is the smooth proxy for divergence
risk, it is finite everywhere strictly inside the stable region, and it diverges
exactly at the boundary the rest of the paper is about. Nothing below depends on
the particular functional form beyond `V` being positive, increasing and convex
in `m_N` on `[0, 1)`, all three of which the closed form satisfies.

## 2. Standing assumptions for this section

**(W1) Aggressiveness.** Each firm chooses `a_i > 0`, meaning cadence, learning
rate, or responsiveness: anything that scales its own performative modulus. Write
`m_i = mu(a_i)` with `mu` differentiable and strictly increasing, common across
firms. Aggressiveness moves a firm's *gain*, not its response *direction*, so `R`
and `kappa` are held fixed. This is the same reading of correction that
Hypothesis (M) in [`derivations/04`](derivations/04-mixed-market-secular.md)
uses, applied to a choice variable instead of to a technology.

**(W2) Benefit.** Aggressiveness buys tracking benefit `B(a_i)`, strictly
increasing and strictly concave. Only firm `i`'s own benefit depends on `a_i`, so
the entire interaction runs through `m_N`.

**(W3) Exchangeable alignment.** `R` is exchangeable, meaning invariant under a
common permutation of firms. The supply-chain alignment
`R = (1-s)I + s 1 1'` that the whole paper specializes to is exchangeable, as are
the monoculture and orthogonal corners. This buys the leading eigenvector
`v = 1/sqrt(N)` at the symmetric point, which is what makes the `(N-1)/N`
statement exact rather than approximate.

**(W4) Client exposure.** The planner's variance weight `W` strictly exceeds the
sum of the private weights: `W > sum_i w_i`, all weights positive.

On (W4), following the lean recorded in the previous version of this note: it is
**stated as an assumption, not microfounded**, and the justification is one
sentence. Every trade has a client on the other side who bears execution-quality
variance while no dealer's objective contains it, so the planner's weight on
common-mode variance strictly exceeds what the dealers together internalize.
The results below turn on the **sign** of `W - sum_i w_i` and never on its size,
so a microfoundation would fix a magnitude the theorem does not use. Open item 3
is closed this way, and the paper says so in one sentence rather than carrying a
welfare model it does not need.

## 3. The marginal crowding share

The one piece of real work. To write either first-order condition we need
`d m_N / d a_i`, and `m_N = m_1 N_eff` is stated for equal moduli, so a single
firm's deviation leaves the regime where that identity is available. The
heterogeneous-modulus machinery of
[`derivations/01`](derivations/01-alignment-spectrum.md) supplies the derivative
directly.

By Proposition 4 of `01`, for `M = diag(m_1, ..., m_N)` and
`B = (1-kappa)I + kappa R`, the radius of `J = -M B` is `lambda_max(A)` for the
symmetric congruence

```
   A(M)  =  M^{1/2} B M^{1/2} .
```

**Lemma 11 (marginal crowding share).** *Let `A(M)` have a simple leading
eigenvalue with unit eigenvector `v`. Then*

```
   d lambda_max / d m_i  =  ( B M^{1/2} v )_i * v_i / sqrt(m_i) .
```

*At the symmetric point `M = m_1 I` this is*

```
   d m_N / d m_i  =  N_eff * v_i^2 ,        sum_i  d m_N / d m_i  =  N_eff ,
```

*and under (W3), `v_i^2 = 1/N` so*

```
   d m_N / d m_i  =  N_eff / N  =  m_N / ( N m_1 ) .
```

*Proof.* `d M^{1/2} / d m_i = (1/(2 sqrt(m_i))) e_i e_i'`, so

```
   dA/dm_i  =  (1/(2 sqrt(m_i))) ( e_i e_i' B M^{1/2}  +  M^{1/2} B e_i e_i' ) .
```

For a simple eigenvalue, first-order perturbation gives
`d lambda_max/d m_i = v' (dA/dm_i) v`. The two terms are transposes of one
another and `A` is symmetric, so they contribute equally, giving

```
   d lambda_max/d m_i  =  (1/sqrt(m_i)) * v_i * ( e_i' B M^{1/2} v )
                       =  ( B M^{1/2} v )_i v_i / sqrt(m_i) .
```

At `M = m_1 I` we have `A = m_1 B`, so `v` is the leading eigenvector of `B` and
`B M^{1/2} v = sqrt(m_1) lambda_max(B) v = sqrt(m_1) N_eff v`. Substituting,
`d lambda_max/d m_i = N_eff v_i^2`. Summing over `i` gives `N_eff` because `v` is
a unit vector. Under (W3) the symmetric point's leading eigenvector is the
uniform one, since an exchangeable `B` commutes with every permutation matrix and
a simple leading eigenvector must therefore be permutation invariant. Hence
`v_i^2 = 1/N`. `[]`

Chaining (W1),

```
   d m_N / d a_i  =  ( N_eff / N ) * mu'(a_i)      at the symmetric profile.
```

Two things worth reading off. First, the **sum** of the marginal effects is
`N_eff`, not `1`: the market's total sensitivity to a uniform increase in
aggressiveness is amplified by exactly the effective learner count, which is the
same object Theorem 1 introduces. Second, an **individual** firm moves `m_N` by
`N_eff/N`, so as `N` grows each firm's own footprint shrinks while the total
grows, which is the arithmetic shape of every commons problem and is what the
next section prices.

## 4. The two problems

Firm `i` bears weight `w_i` on the common-mode variance. The planner bears `W`.

```
   private:  max_{a_i}   B(a_i)  -  w_i * V( m_N(a_1, ..., a_N) )
   social:   max_{a}     sum_j B(a_j)  -  W * V( m_N(a) )
```

Write `V'(m) = dV/dm = 2 sigma^2 m / (1 - m^2)^2 > 0` for `m` in `(0,1)`, and
evaluate at a symmetric profile `a_i = a` for all `i`, so that
`m_N = m_N(a) = mu(a) N_eff`.

**Private first-order condition.**

```
   B'(a)  =  w_i * V'( m_N ) * ( N_eff / N ) * mu'(a) .                    (P)
```

**Social first-order condition.** The planner differentiates in `a_i` too, but
carries the full weight:

```
   B'(a)  =  W * V'( m_N ) * ( N_eff / N ) * mu'(a) .                      (S)
```

The two conditions are the same equation with a different price on crowding.
Everything Theorem 4 says is the gap between the two coefficients.

## 5. The wedge

**Theorem 4.** *Under (W1) to (W4), at a symmetric profile the marginal variance
cost a firm ignores is*

```
   t*  =  ( W - w_i ) * V'( m_N ) * ( N_eff / N ) * mu'(a)
       =  ( W - w_i ) * ( 2 sigma^2 m_N / (1 - m_N^2)^2 ) * ( N_eff / N ) * mu'(a) ,
```

*and a per-unit fee `t*` on aggressiveness makes (P) coincide with (S), so the
taxed decentralized equilibrium implements the symmetric social optimum.*

*Proof.* Subtract (P) from (S). A firm facing the fee solves
`max B(a_i) - w_i V(m_N(a)) - t* a_i`, whose first-order condition is (P) with
`B'(a)` replaced by `B'(a) - t*`. Substituting the stated `t*` reproduces (S)
term for term. `[]`

**The `(N-1)/N` reading.** With symmetric weights `w_i = w` and
`W = chi * N * w` for some `chi > 1` given by (W4),

```
   t*  =  ( chi N - 1 ) * w * V'( m_N ) * ( N_eff / N ) * mu'(a) ,
```

whose total marginal cost counterpart is `chi N w V'(m_N)(N_eff/N) mu'(a)`. The
ignored fraction is `(chi N - 1)/(chi N)`. Setting `chi = 1`, that is: shutting
off client exposure entirely and leaving only the firm-to-firm channel, the
ignored fraction is exactly `(N - 1)/N`. That is the statement of ledger claim
7.2: the private condition ignores `(N-1)/N` of the marginal variance cost borne
by other firms, **plus** the entire client-side exposure, which is the part
`chi > 1` adds.

**Corollary 4.1 (comparative statics).** *`t*` is strictly increasing in `N`, in
`kappa`, and in `m_N`, and diverges as `m_N -> 1`.*

*Proof.* Take the supply-chain specialization `N_eff = 1 + kappa s (N-1)` and
symmetric weights, so
`t* = (chi - 1/N) * w * V'(m_N) * N_eff * mu'(a)`. The factor `chi - 1/N` is
strictly increasing in `N`. `N_eff` is strictly increasing in `N` whenever
`kappa s > 0`, and strictly increasing in `kappa` whenever `s > 0` and
`N >= 2`. `m_N = mu(a) N_eff` inherits both. Finally
`V'(m) = 2 sigma^2 m/(1-m^2)^2` is strictly increasing on `(0,1)` and diverges at
`1`, since both `m` and `(1-m^2)^{-2}` are. Every factor moves the same way, so
the product does. `[]`

The divergence is the economically loaded part. The fee that would correct a
market is not proportional to how crowded it is; it blows up like
`(1 - m_N)^{-2}` as the market approaches its stability boundary. A regulator
setting a fee from a comfortable-looking market and holding it fixed is setting
it far too low by the time the market is close to the edge.

## 6. Over-adaptation

**Corollary 4.2 (over-adaptation).** *Under (W1) to (W4), assume `V(m_N(a))` is
convex and increasing in `a` on the stable range and that an interior symmetric
solution exists for both problems. Then the symmetric decentralized equilibrium
`a_d` strictly exceeds the symmetric social optimum `a_s`, for every `N >= 2`,
and the gap is strict even when client exposure is switched off (`chi = 1`).*

*Proof.* Write `C(a) = V(m_N(a))`, and

```
   F_priv(a)  =  B'(a)  -  w  C'(a) ,        F_soc(a)  =  B'(a)  -  W  C'(a) .
```

Both are strictly decreasing, since `B'` is strictly decreasing by (W2) and `C'`
is nondecreasing by convexity, so each has at most one zero, and by the interior
assumption each has exactly one: `a_d` and `a_s` respectively. Because `C'(a) > 0`
on the stable range (`V' > 0`, `N_eff > 0`, `mu' > 0`) and `W > w` by (W4),

```
   F_soc(a)  =  F_priv(a)  -  (W - w) C'(a)  <  F_priv(a)     for every a.
```

Evaluate at `a_d`: `F_soc(a_d) < F_priv(a_d) = 0`. Since `F_soc` is strictly
decreasing and vanishes at `a_s`, this forces `a_s < a_d`. For the last clause,
set `chi = 1` so that `W = N w`; then `W - w = (N-1) w > 0` exactly when
`N >= 2`, so the strict inequality survives with no client-side channel at all.
At `N = 1` and `chi = 1` the wedge is zero and the two problems coincide, which
is the correct degenerate case: a single firm bearing its own variance in full
internalizes everything. `[]`

The distortion grows as the market crowds, in the sense of Corollary 4.1: the
coefficient gap `(W - w) C'(a)` is proportional to `V'(m_N) N_eff`, both of which
increase in `N` and `kappa`.

## 7. What the merge adds: the provenance channel

`d m_N / d a_i` is one of two channels, because `m_N = m_1 N_eff` and `N_eff`
depends on `s`:

```
   aggressiveness channel:   d m_N / d a_i  =  ( N_eff / N ) mu'(a_i)
   provenance channel:       d m_N / d s    =  m_1 * kappa * (N - 1)
```

**Proposition 12.** *Under the supply-chain specialization,
`d m_N/ds = m_1 kappa (N-1)` exactly, and the corresponding adoption wedge is*

```
   t*_s  =  ( W - w_i ) * V'( m_N ) * m_1 * kappa * ( N - 1 ) .
```

*Proof.* `m_N = m_1 (1 + kappa s (N-1))` is affine in `s`, so the derivative is
the coefficient. The wedge follows from Theorem 4's proof with `s` in place of
`a_i` as the choice variable. `[]`

The same wedge therefore prices **shared-model adoption** directly, which turns
the monoculture externality into a fee rather than a warning, and connects this
result to the adoption-incentive question the call for papers asks about.

Note the contrast with the aggressiveness channel. `d m_N/d a_i` carries a factor
`N_eff/N`, which is bounded above by `(1 + kappa(N-1))/N` and therefore tends to
`kappa` from above as `N` grows: a firm's marginal footprint through its own
cadence does not grow without bound. The provenance channel is **linear in `N`
and does not decay**. A firm's decision to adopt the market-leading vendor
imposes a marginal cost on the market that grows with market size, while its
private quality gain does not. That asymmetry is the reason unregulated adoption
dynamics run toward the unstable configuration rather than away from it, and it
is why the diversity floor of Theorem 3 is a different instrument from the
cadence cap of Theorem 2 rather than a restatement of it.

## 8. The policy triple

This is where the paper's three levers are named as what they are, which is the
standard instrument taxonomy. Say it in one sentence and an economics reader
knows exactly what they are looking at.

| Lever | Instrument type | Where |
|---|---|---|
| Cadence caps | Quantity regulation | Theorem 2 |
| Correction mandates | Technology mandate | Theorem 3 |
| Diversity floors | Structural remedy | Theorem 3 |
| The wedge | Price instrument | Theorem 4 |

The quantity-versus-price choice under uncertainty is Weitzman's question, and
the paper cites it for the framing rather than solving it. Worth one sentence,
because a reader from economics will otherwise supply the objection themselves.

## 9. Certificates

Implemented in
[`verify_theorem4_wedge.py`](../ml-contributions/certificates/verify_theorem4_wedge.py),
assertion-based.

| # | Statement |
|---|---|
| C19 | The AR(1) reduction: simulated stationary variance equals `sigma^2/(1-m_N^2)`, and the lag-1 autocorrelation equals `-m_N`, so the sign convention is checked rather than assumed |
| C20 | `t*` is strictly increasing in `N`, in `kappa`, and in `m_N`, and diverges at the boundary |
| C21 | Over-adaptation: the decentralized symmetric equilibrium exceeds the social optimum for every `N >= 2` on a grid, and the two coincide at `N = 1` with `chi = 1` |
| C34 | **Lemma 11**, by finite differences: `d m_N/d m_i = N_eff v_i^2` on random alignment matrices, summing to `N_eff`, and equal to `N_eff/N` on exchangeable `R` |

C34 is the load-bearing one. Everything else in the theorem is arithmetic on top
of the marginal crowding share, and until C34 that share was the step where a
plausible-looking `1/N` could have been wrong by a factor of `N_eff`.

## 10. Open items

1. ~~Write the welfare page.~~ **Closed**, Sections 1 to 6 above.
2. ~~Confirm the AR(1) reduction gives exactly `1/(1 - m_N^2)`, including the
   sign convention.~~ **Closed**, Section 1 and C19. The variance is sign-blind;
   the lag-1 autocorrelation is not, and is negative.
3. ~~Decide whether `W > sum_i w_i` needs a microfoundation.~~ **Closed as an
   assumption**, (W4), with one sentence of justification. The result uses the
   sign and never the size.
4. Experiment 6 is decentralized against socially optimal aggressiveness on a
   small grid, plus the wedge's comparative statics in `N`, `kappa` and `s`.
   Second in the de-scope order; if cut, Theorem 4 ships as theory. **Still
   open**, and `pigouvian_wedge` stays out of the theory module until the panel
   is built, so nothing can be measured ahead of its experiment.
5. Beyond the symmetric point, `d m_N/d m_i = N_eff v_i^2` says the marginal
   crowding share is the leading eigenvector's **participation ratio** at firm
   `i`, so a firm sitting on the crowded mode imposes more than its `1/N` share.
   Named, not developed. The asymmetric-wedge question it opens belongs with
   4.11 in the journal version.
