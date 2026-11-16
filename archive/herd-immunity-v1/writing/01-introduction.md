# 1. Introduction

**Status: complete.** Target 1.25 pages. Citations in author-year form; the
bibliography is assembled at LaTeX time from `../literature/`.

Double-blind compliance: REFLEX and PEBSA appear in the third person as ordinary
references. No sentence in this section positions either as the authors' own
work.

---

A learning agent can pass every stability test we know how to run and still help
destabilize the market it operates in.

The test we know how to run is a single-agent test. A model is evaluated,
stress-tested, and certified alone, against a distribution that is treated as
given. When the deployed model reshapes that distribution, the performative
prediction literature supplies the correction: repeated retraining converges if
and only if a modulus `m = eps*beta/gamma` stays below one, where `eps` measures
how strongly the environment responds and `gamma` is the learner's own objective
curvature (Perdomo et al., 2020). Certify `m < 1` and the loop is safe.

It is not, once the agent has company. Consider dealers whose quotes reshape a
common pool of informed flow, recommenders competing for one attention pool, or
lenders pricing against one population of borrowers. Each agent's retraining
changes the data every *other* agent will learn from next. No agent internalizes
that effect. We call it a **learning externality**, and it has the property that
makes externalities worth studying: every participant behaves rationally,
every participant passes its own test, and the interaction amplifies a loop that
none of them chose. Individual model evaluation cannot certify a market of
models, and the gap between the two questions is precisely the externality.

The externality is not new as an intuition. Banks that each diversify optimally
end up holding similar portfolios and failing together, a tension named the
regulator's dilemma two decades ago (Beale et al., 2011; Wagner, 2010). Funds
running similar strategies on similar signals unwound simultaneously in August
2007, and the crowding was invisible from any single fund's risk report
(Khandani and Lo, 2007). What is new is that the agents now *learn*, and that
changes both what determines the danger and what can be done about it.

**What determines it is not how many firms there are.** The natural reading of
the multi-agent stability condition counts participants: more firms, more
coupling, more amplification. That reading is wrong in a way that matters for
policy. What couples the firms is not their number but the *alignment of their
feedback directions*. Let firm `i` have a response Jacobian `E_i` describing how
its own deployment reshapes the flow it faces, and let `R` be the correlation
matrix of the vectorized `E_i`. We show that the market's stability is governed
by

```
   m_N  =  N_eff * m_1 ,        N_eff  =  1 + kappa ( lambda_max(R) - 1 ) ,
```

where `kappa` is the spillover between firms and `lambda_max(R)` is what we call
the **effective number of independent learners**. A hundred firms perturbing the
environment in a hundred orthogonal directions are dynamically one firm. Fifty
dealers fine-tuning one vendor's foundation model are dynamically close to one
very large learner, and the market they share inherits that learner's
instability.

That reading gives foundation-model concentration a home in a stability
condition rather than in a warning. Decomposing each firm's response into a
shared component and an idiosyncratic one, with `s` the fraction attributable to
a common model, vendor, or pretraining corpus, gives
`m_N = m_1 (1 + kappa * s * (N-1))`. **The effective number of learners is the
number of independent models, not the number of firms.** The quantity a
competition regulator measures, market share concentration, is the wrong one:
fifty equal-share firms have a minimal Herfindahl index and look perfectly
competitive, and if all fifty share one vendor they are dynamically a
monoculture.

The spectral form is not a convenience. Mean pairwise alignment, the index a
policymaker would naturally reach for, understates clustered alignment badly:
three tightly aligned firms among ten otherwise-orthogonal ones destabilize a
subspace the average barely registers, and a market that is unstable can look
safe with margin. Worse, the mean does not order configurations correctly, so it
fails as a ranking and not only as a level.

**What can be done about it takes three forms, and two of them are substitutes.**
Because every result is stated in `m_N`, each inherits the supply chain for free.

*Slow down.* Firms that take `K` gradient steps per deployment rather than
retraining to convergence face a stability window `K < K_max(m_N)` that narrows
as effective crowding rises, and closes entirely past a critical crowding level
beyond which no cadence is safe. The operational statement of the
externality is sharper than competition usually allows: your competitor's entry
consumes your step budget, and so does your competitor's *choice of
vendor*, without their entering at all and without either firm doing anything
wrong.

*Correct.* Feedback-aware updates that estimate the response and correct for it
(Izzo et al., 2021) stabilize a single learner beyond its boundary. Run inside
the market, they produce a threshold: the market is stable if and only if the
corrected fraction exceeds `rho* = 1 - 1/m_N`, **exactly the epidemiological
herd-immunity law `1 - 1/R_0`**, with the systemic modulus as the reproduction
number. The correspondence is structural rather than decorative. In
heterogeneous populations `R_0` is defined as the spectral radius of a
next-generation operator (Diekmann et al., 1990), and `m_N` is the spectral
radius of the joint retraining Jacobian, so the two thresholds are the same
statement about a linearized operator. Correction is a public good: an
un-blinded firm captures a private benefit while the stability it contributes
accrues to everyone, which is why a market does not reach `rho*` unaided.

*Diversify.* Since `rho*` is increasing in `s`, a market can reach stability
along either axis. Un-blind more agents, or share fewer models. The `(rho, s)`
iso-stability frontier is this paper's most directly usable object: a regulator
facing an unstable market of adaptive models holds two interchangeable
instruments and can price them against each other. Both are under-supplied for
the same reason, so the substitution is between two goods rather than between a
good and a bad.

Pricing the externality directly completes the standard policy triple. In the
stable regime the market's common mode fluctuates with variance proportional to
`1/(1 - m_N^2)`, diverging at the boundary, and the private first-order
condition ignores the share of that cost borne by others. The resulting
Pigouvian wedge prices adaptation aggressiveness and shared-model adoption in
one expression, and the decentralized equilibrium over-adapts for every `N >= 2`.

**Contributions.**

1. The **effective number of independent learners** as the reproduction number
   of a market of adaptive models, turning foundation-model concentration into a
   term in a stability condition, with the exact equal-moduli identity and two
   counterexamples invalidating mean-similarity diversity indices.
2. The **crowding-cadence frontier** and its critical crowding level, composing
   lazy deployment with multi-agent amplification for the first time, and its
   supply-chain reading.
3. The **herd-immunity theorem** `rho* = 1 - 1/m_N` for a mixed population of
   corrected and blind learners, together with the first experiment running a
   corrected retraining loop inside a multi-agent game.
4. The **substitution frontier** between model diversity and corrected learning,
   which exists only once the first and third are expressed in the same
   quantity.
5. The **Pigouvian wedge** and the over-adaptation corollary, unifying the
   levers as quantity, technology or structure, and price instruments.

All closed forms are checked numerically against a market simulator in which
every constant is computed from microstructure primitives rather than fitted
(REFLEX, arXiv:2608.16155), whose symmetric multi-dealer result is the
monoculture corner `R = 1 1'` of the condition above.

---

## Notes for the writing pass

**Length check.** About 1050 words as drafted. At NeurIPS single-column density
this runs slightly over 1.25 pages. First compression targets, in order: the
Khandani-Lo and Beale sentences merge into one, the mean-alignment paragraph
drops to two sentences since Section 4 repeats it, and the wedge paragraph loses
its middle clause.

**Deliberate omissions.** No roadmap paragraph. At nine pages with numbered
result sections the table of contents is visible from the section headings, and
a roadmap costs fifteen lines that Section 4 needs more.

**Citations placed here.** Perdomo et al. 2020; Beale et al. 2011; Wagner 2010;
Khandani and Lo 2007; Izzo et al. 2021; Diekmann et al. 1990; REFLEX. The
monoculture citations (Kleinberg and Raghavan; Bommasani et al.) are deliberately
held for Section 2, where the delta against them is the point and a passing
mention here would waste the position.

**Open decision.** The Herfindahl sentence is the most quotable line in the
section for a policy reader and the least load-bearing for a theory reviewer. It
stays unless the section runs long, in which case it moves to Section 4 next to
the phase diagram, where the figure carries it.
