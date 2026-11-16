# 2. Related work

**Status: drafted.** Target 0.75 pages. Source:
[`../literature/LITERATURE-REVIEW-P2.md`](../literature/LITERATURE-REVIEW-P2.md).

The rule this section is written to: **prove the deltas, do not assert them.**
Six citations get a named-delta sentence each and everything else is grouped and
cited in bulk. A related-work section that lists topics tells a reviewer the
authors read; one that states deltas tells them the authors understood.

Double-blind compliance: REFLEX and PEBSA appear in the third person as ordinary
references. No sentence positions either as the authors' own work, and no
sentence claims prior results for this paper.

---

**Algorithmic monoculture, and why it is static.** Kleinberg and Raghavan (2021)
show that when many firms adopt the same algorithm welfare can fall even when the
shared algorithm is the better one, because correlated selection destroys the
option value of independent evaluation; Bommasani et al. (2022) formalize the
resulting outcome homogenization, and Toups et al. (2023) measure it across
deployed systems, which is what establishes that a shared-component fraction is a
real quantity rather than a modeling convenience. The delta is a difference of
harm, not of degree: every one of these measures a cross-sectional loss on a
single allocation round, with no retraining loop and therefore no stability
boundary, so a market can be statically fine and dynamically fragile at the same
shared-model fraction. The model-multiplicity literature (Marx et al., 2020;
Black et al., 2022) is the conceptual inverse and worth stating as such:
multiplicity asks how much models *could* differ, while the object here measures
how much their feedback directions *do*. A market of maximally multiplicitous
models with aligned response Jacobians is a monoculture in this paper's sense.
The cybersecurity precedent made the same argument twenty years earlier, and its
skeptical entry (Birman and Schneider, 2009) is the one worth taking seriously,
because it warns that the biological analogy is usually invoked loosely. The
fourth paragraph below is the answer to it.

**Multi-agent performative prediction, and its blindness to direction.** Narang
et al. (2023) and Piliouras and Yu (2023) supply genuine multi-agent
decision-dependent dynamics with equilibrium concepts and convergence conditions,
and they are the nearest dynamics in the literature. Stated at the object level
rather than the topic level, the delta is that their coupling enters through
scalar sensitivity and Lipschitz constants on the joint distribution map, so
there is no object in either framework representing which direction an agent
perturbs the environment, and two markets with identical constants but opposite
alignment structure are indistinguishable in their conditions while having
entirely different stability here. That absence is why the strand can express
neither monoculture nor model provenance nor a supply chain, and why it contains
no priced externality and no mixed population. Retraining frequency is not a
variable anywhere in it, which is what leaves the cadence question unposed.
Strategic classification is the adversarial cousin and is placed rather than
surveyed: the response modeled here is aggregate and non-strategic, so the
failure is one of coordination rather than a game against a classifier. REFLEX
(arXiv:2608.16155) is the closest single antecedent and the largest overlap
surface, supplying the symmetric multi-dealer law, the single-learner
lazy-deployment lemma and a structurally anchored corrected update; its delta is
that its multi-dealer law is the `R = 1 1'` corner of Theorem 1 and carries no
alignment object, its lazy-deployment lemma is single-learner and has not been
composed with a multi-agent amplification law, its corrected update has only been
run at one firm so no mixed population arises, and it contains no welfare
statement and no policy instrument.

**The framing has an ancestor, and its agents do not learn.** Beale et al. (2011)
named the regulator's dilemma, showing that banks each diversifying optimally
choose similar portfolios and so maximize the probability of simultaneous
failure, and Wagner (2010) formalized why individually optimal diversification
homogenizes a system. The private-versus-systemic tension is theirs and this
paper concedes it in full. The delta is that their agents hold portfolios rather
than learn, so homogeneity is portfolio overlap rather than alignment of feedback
directions, there is no modulus, no cadence and no stability boundary, and above
all there is only one instrument: diversity, with nothing to trade it against.
The second instrument, and therefore the substitution frontier of Section 6,
exists only because the agents learn. Khandani and Lo (2007) is the empirical
instance, where many funds running similar strategies unwound at once and the
crowding was invisible from any single fund's risk report. Herding is a different
mechanism reaching the same destination and the two should not be conflated
(Banerjee, 1992; Bikhchandani et al., 1992): herding converges beliefs and
choices through observational learning, whereas alignment here is mechanical,
arising because models share weights, and it obtains even when firms never
observe each other. The corrective apparatus is classical and is used rather than
reinvented: Pigou (1920) for the wedge, Bergstrom, Blume and Varian (1986) for
why a public good is under-supplied in private provision, and Buchanan and
Stubblebine (1962) for the distinction that keeps this externality technological
rather than pecuniary, since the coupling runs through the data-generating
process each learner faces and not through the price at which the firms trade.
Weitzman (1974) is the instrument-choice question, and this paper offers a
quantity instrument, a technology mandate and a price instrument without
resolving which a regulator should prefer under uncertainty; that is
acknowledged, not solved.

**The law and the statistic are both borrowed, and both are conceded.** The
herd-immunity threshold is Kermack and McKendrick (1927) and Anderson and May
(1991), with Fine et al. (2011) on the assumptions the simple `1 - 1/R_0` form
needs, homogeneous mixing above all; its spectral form on a contact network is
Wang et al. (2003), where the epidemic threshold is the reciprocal of the largest
adjacency eigenvalue. Diekmann et al. (1990) is what converts the parallel from
analogy into identity, and it is the delta worth stating most carefully: `R_0` in
a heterogeneous population is *defined* as the spectral radius of a
next-generation operator, and the systemic modulus here is the spectral radius of
a linearized joint retraining operator, so the two thresholds are the same
mathematical statement and the vaccination law transfers without adjustment,
including its imperfect-vaccine refinement. On the statistic, the largest
eigenvalue of a correlation matrix as an effective count is standard in
random-matrix finance (Laloux et al., 1999; Plerou et al., 2002), in signal
processing (Roy and Vetterli, 2007) and in ecology (Hill, 1973); the delta is
that it is computed here on response Jacobians rather than on returns, shares or
predictions, and that it enters a stability condition rather than describing a
cross-section. The comparison a policy reader reaches for first is the
Herfindahl-Hirschman index (Hirschman, 1964), and it earns its place by failing:
fifty equal-share firms have minimal HHI and look perfectly competitive, and if
all fifty fine-tune one vendor's model the effective count is `1 + 49*kappa`.
Concentration in the product market and concentration in the model supply chain
are different quantities, and only the second enters the stability condition.

**Inference from public aggregates, and the contrast that matters.** The
question Section 8 asks, what can be inferred about the state of an economy from
aggregate public signals no single participant controls, is asked in a different
measurement regime by work reading macroeconomic conditions off public sentiment
(PEBSA, 2024): there the channel is **exogenous**, a signal about an economy the
observer stands outside of, and the accuracy of the inference does not depend on
the economy's own dynamics. The observable in Section 8 is **endogenous**, since
the prices a supervisor reads are generated by the very adaptive agents being
monitored, so the measurement channel is part of the system and the signal
strengthens as the system nears instability. The contrast is the point and there
is no shared method to claim.

**Footnote,** attached to the first use of "effective number of independent
learners" in Section 4: the phrase follows a long naming convention, from Hill
numbers in ecology (Hill, 1973) through effective rank in signal processing (Roy
and Vetterli, 2007) and participation ratios in physics. Nothing about the
eigenvalue is new. What is new is the matrix it is computed from and the
condition it enters.

---

## Held back from the introduction on purpose

The monoculture citations do not appear in Section 1. Their value is the delta,
the delta needs a sentence, and a passing mention in the introduction would spend
the position without buying the argument.

## Deliberately absent

No survey of performative prediction: Section 3 gives the modulus and that is all
the setup a reader needs. Strategic classification gets one clause, since the
setting is placed rather than engaged. The AI-policy literature is motivation and
belongs in Section 1 or the conclusion; it is not prior art for any claim here.

## Checklist

- [x] Six named-delta sentences present, one per load-bearing citation:
      Kleinberg and Raghavan, Narang et al., REFLEX, Beale et al., Diekmann et
      al., and the random-matrix effective-count line
- [x] Buchanan-Stubblebine sentence present: the externality is technological,
      not pecuniary, because the coupling runs through the data-generating
      process rather than through prices
- [x] Weitzman cited for instrument choice, with the acknowledgment that the
      paper does not solve it
- [x] Herding distinguished from alignment in one sentence: alignment obtains
      even when firms never observe each other
- [x] No sentence positions REFLEX or PEBSA as the authors' own work
- [x] Birman and Schneider's skepticism cited and then answered, rather than
      only the enthusiasts cited
- [x] PEBSA's one sentence lives here rather than in Section 8, so that cutting
      Section 8 leaves no orphaned reference

## Verification debt carried into this draft

Every citation above except the ten marked `[V1]` in the literature review is
bibliographic from record and has not been checked against a publisher page. The
six load-bearing entries clear before the submission draft freezes, per that
review's debt table. Peng and Garg (2024), Narechania and Sitaraman, and the AI
Act article numbers are flagged there as verify-or-drop and none of them is used
above.
