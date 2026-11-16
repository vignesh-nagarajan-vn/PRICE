# 7. Result 4: the Pigouvian wedge

**Status: drafted.** Target 0.75 pages. Source:
[`../math/04-theorem4-wedge.md`](../math/04-theorem4-wedge.md).
Certificates in `../ml-contributions/certificates/verify_theorem4_wedge.py`.

---

The third lever is the price instrument, and it is the one that turns the
externality from a narrative into a number. Sections 5 and 6 say what a market
must do to stay stable. This section says what the market's own participants
would have to be charged to want to.

**The welfare object.** Inside the stable region the binding mode is an AR(1)
with coefficient `-m_N` driven by noise of variance `sigma^2`, so its stationary
variance is

```
   V(m_N)  =  sigma^2 / ( 1 - m_N^2 ) .
```

The choice is defended rather than assumed: stationary variance is the smooth
proxy for divergence risk, finite everywhere strictly inside the stable region
and divergent exactly at the boundary the rest of the paper is about. Nothing
below uses more than `V` being positive, increasing and convex. The coefficient
carries a sign that the variance does not see, and it is not lost information:
the lag-1 autocorrelation is `-m_N` and therefore **negative**, so a crowded
market's common mode oscillates rather than persists. That is the observable
Section 8 reads, and a diagnostic looking for persistence would look for the
wrong thing. [VERIFIED, simulated to `2e-2` on 400k-step paths]

**The choice variable.** Each firm picks an adaptation aggressiveness `a_i`,
meaning cadence, learning rate, or responsiveness: anything scaling its own
modulus through `m_i = mu(a_i)`. Aggressiveness buys concave tracking benefit
`B(a_i)`, and it moves a firm's gain rather than its response direction, so `R`
and `kappa` are held fixed. Firm `i` bears weight `w_i` on common-mode variance
and the planner bears `W`, with `W > sum_i w_i` because every trade has a client
on the other side who bears execution-quality variance while no dealer's
objective contains it. That is an assumption, stated as one, and the results
below turn on its **sign** and never on its size.

**The marginal crowding share, which is the load-bearing step.** Writing either
first-order condition needs `d m_N/d a_i`, which the modulus-weighted machinery
of Result 1 supplies directly.

<!-- APPENDIX, page-budget step 1, 19 Aug 2026: a single firm's deviation leaves
     the equal-moduli regime where m_N = m_1 N_eff is available, which is why
     Proposition 4 of the alignment derivation is the route. -->

**Lemma 11.** *At the symmetric point, `d m_N/d m_i = N_eff v_i^2`, where `v` is
the leading eigenvector of the coupling matrix. The shares therefore sum to
`N_eff` rather than to one, and on exchangeable `R` each equals `N_eff/N`.*
[VERIFIED, by finite differences to `1e-5`]

Both readings matter. The **sum** is `N_eff`, so the market's total sensitivity
to a uniform increase in aggressiveness is amplified by exactly the effective
learner count of Result 1. The **individual** share is `N_eff/N`, so as the
market grows each firm's own footprint shrinks while the total grows, which is
the arithmetic shape of every commons problem. The naive guess here is `1/N` by
analogy with the commons, and it is wrong by the factor `N_eff`, which at
`N = 20`, `kappa = 0.8`, `s = 1` is `16.2`.

**Theorem 4.** *Under the standing assumptions, at a symmetric profile the
private and social first-order conditions are the same equation with a different
price on crowding, and the marginal cost a firm ignores is*

```
   t*  =  ( W - w_i ) * V'( m_N ) * ( N_eff / N ) * mu'(a) ,
   V'(m_N)  =  2 sigma^2 m_N / ( 1 - m_N^2 )^2 .
```

*A per-unit fee `t*` on aggressiveness makes the private condition coincide with
the social one, so the taxed decentralized equilibrium implements the symmetric
social optimum.* [VERIFIED]

With symmetric weights the private condition ignores the fraction
`(N-1)/N` of the marginal variance cost borne by other firms, **plus** the entire
client-side exposure. Setting client exposure to zero leaves exactly `(N-1)/N`,
which is the clean statement of what one firm does not internalize. [VERIFIED]

**Comparative statics.** `t*` is strictly increasing in `N`, in `kappa`, in `s`
and in `m_N`, and it diverges at the boundary like `(1 - m_N)^-2`. [VERIFIED] The
rate is the economically loaded part: a regulator who sets a fee from a
comfortable-looking market and holds it fixed is setting it far too low by the
time the market is close to instability.

<!-- APPENDIX, page-budget step 3, 19 Aug 2026. The comparative statics move to
     the appendix with their conclusion kept above as one clause, per the
     compression order in README.md.

The exponent is measured at `-2.000000` rather than argued. The fee that would
correct a market is not proportional to how crowded the market is; it blows up
quadratically in the distance to the edge, so the correction a regulator owes a
market is a steeply nonlinear function of a quantity that regulator cannot
directly observe.
-->

**Corollary 4.2.** *The decentralized equilibrium over-adapts relative to the
social optimum for every `N >= 2`, strictly so even with client exposure switched
off, and the distortion grows as the market crowds.* [VERIFIED] At `N = 1` with
no client exposure the wedge is exactly zero, which is the correct degenerate
case: a single firm bearing its own variance in full internalizes everything.

**The provenance channel, which is what the merge buys.** `m_N` depends on `s`,
so the wedge has a second channel:

```
   aggressiveness:   d m_N / d a_i  =  ( N_eff / N ) mu'(a_i)
   provenance:       d m_N / d s    =  m_1 * kappa * ( N - 1 )
```

The same wedge therefore prices **shared-model adoption** directly, turning the
monoculture externality into a fee rather than a warning. [VERIFIED] The contrast
between the two channels explains the adoption dynamic in one line. The
aggressiveness channel's `N_eff/N` factor is bounded and tends to `kappa` from
above, so a firm's marginal footprint through its own cadence does not grow
without bound. The provenance channel is **linear in `N` and does not decay**,
while a firm's private quality gain from adopting the market-leading vendor does
not grow with market size at all. Unregulated adoption therefore runs toward the
unstable configuration rather than away from it, which is why the diversity floor
of Result 3 is a different instrument from the cadence cap of Result 2 rather
than a restatement of it.

**The policy triple, named.** Result 2 is quantity regulation, Result 3 is a
technology mandate or a structural remedy, and Result 4 is the price instrument.
The choice between quantity and price under uncertainty is Weitzman's question
(Weitzman, 1974), and this paper supplies the objects a regulator would need to
pose it rather than answering it.

---

## Figure 5

**Over-adaptation.** Decentralized against socially optimal aggressiveness across
`N`, with the gap shaded, beside the wedge's comparative statics in `N` on a log
scale. Caption states `mu`, `B`, the weights, the client-exposure multiplier and
the fitted boundary exponent, and states that the panel is a dry run.

The panel behind it is `[DRY RUN]`, not a measurement, and Section 9 says so in
its own row. Twelve configurations, zero rows contradicting Corollary 4.2, the
smallest relative gap `29.0%` at `N = 2` widening to `119.9%` at `N = 20`, the
fee implementing the social optimum to `1.7e-13`, and the degenerate `N = 1` row
at exactly zero.

**Second in the de-scope order.** If it goes, Theorem 4 ships as theory with no
figure, which is acceptable: the theorem is the contribution and the panel is the
illustration.

## Checklist

- [x] Variance-as-welfare-cost choice defended, not asserted
- [x] Both channels of `dm_N/da_i` shown, aggressiveness and provenance
- [x] The linear-in-`N` asymmetry stated, since it explains the adoption dynamic
- [x] Policy triple named explicitly, with Weitzman cited and not oversold
- [x] Client-side exposure assumption stated in one sentence, and flagged as an
      assumption whose sign is what the results use
- [x] Lemma 11 present with the `1/N` guess named as wrong by the factor `N_eff`
- [x] The panel's `[DRY RUN]` status stated here, not only in Section 9
- [ ] Confirm at assembly that Weitzman (1974) is the right attribution in the
      bibliography's spelling

## Notes for the writing pass

**Length.** Drafted at about 950 words of prose. Steps 1 and 3 of the page-budget
compression order have been applied, moving the derivation lead-in and the
comparative statics to the appendix, which brings the body to about 870 words.
That is still over the 0.75-page target. The provenance channel and Corollary
4.2 do not move, since they are what the section is for.

**What changed against the plan of record.** The plan states the wedge as
`(dm_N/da_i) * (marginal variance cost borne by others)` and leaves the
derivative unevaluated. Evaluating it by the obvious commons analogy gives `1/N`,
which is what the build was about to write down; Lemma 11 shows it is `N_eff/N`,
so the wedge is larger by the effective learner count. That is a gap the plan
left open rather than a claim it got wrong, and the section fills it. The plan
also leaves the welfare page as a sketch; it is complete and certified, so this
section states results rather than intentions.

**The one thing a referee will probe.** Whether stationary variance is the right
welfare object. The honest answer is that it is a modeling choice, that the
section says so in the same breath as the formula, and that nothing below the
choice depends on more than `V` being positive, increasing and convex. A referee
who wants a different cost function can substitute one and every statement here
survives.
