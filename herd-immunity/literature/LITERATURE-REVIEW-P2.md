# Literature Review: "Herd Immunity and Learning Externalities in Markets of Adaptive Models"

## Monoculture, multi-agent learning dynamics, and the economics of systemic instability: the seven literatures the paper touches, the gaps between them, and the novelty verdict

**Prepared 2026-08-17 for the herd-immunity paper (P2).**

**Verification statement, stated honestly.** This review was assembled from
record rather than from click-through, and its tags say so:

- **[V1]** the PDF is in hand and was read. Ten papers, shipped in
  `pdfs/`, fetched from arXiv by this folder's script.
  Six are load-bearing here; three instantiate the market model; one delimits
  scope.
- **[B]** bibliographic details stated from record and internally consistent,
  **pending click-through verification**. Every [B] entry is listed in the
  verification-debt table at the end of this document.

Do not treat a [B] tag as equivalent to the [V2] tag used in the companion ML x
OR review, which meant "confirmed this week against the publisher page". Nothing
here was confirmed against a publisher page. The debt table is the work item,
and the six load-bearing entries clear before the submission draft is written,
not before camera-ready.

**Credibility bar.** Every load-bearing source is a top peer-reviewed venue in
its field (PNAS, Nature, AER, JPE, QJE, REStud, Econometrica, ICML, NeurIPS,
JMLR, AISTATS, EC, FAccT, Journal of Finance, RFS, Mathematics of OR, PRL) or a
monograph of record. Working papers and policy reports appear only in Cluster G,
are marked as such, and are never load-bearing for a gap claim.

---

## 0. The paper being positioned, in three sentences

P2 claims: (i) agents that each pass an individual stability test can jointly
destabilize a shared environment, because each agent's retraining reshapes the
data every other agent learns from next, and the strength of that **learning
externality** is set by the **effective number of independent learners**
`lambda_max(R)`, a spectral statistic of the firms' response Jacobians, not by
headcount; (ii) three closed-form levers follow, all expressed in the systemic
modulus `m_N = N_eff * m_1`, namely a crowding-cadence frontier, a
herd-immunity threshold `rho* = 1 - 1/m_N` that is exactly the epidemiological
`1 - 1/R_0`, and a Pigouvian wedge; (iii) the last two are **substitutes**, so a
market can buy stability with model diversity or with corrected learning, along
a frontier the paper computes. The question this review answers: which parts of
that already exist, where, and in what form.

---

## Cluster A. Algorithmic monoculture and model multiplicity: the venue's home literature

This is where an economics-and-ML reviewer looks first, and the cluster-level finding is
simple: **the phenomenon is well established and entirely static.**

**A1. Kleinberg, Raghavan. "Algorithmic Monoculture and Social Welfare." PNAS
118(22):e2018340118, 2021.** [B]
The foundational result: when many firms adopt the same algorithm, welfare can
fall *even when the shared algorithm is the better one*, because correlated
selection destroys the option value of independent evaluation. A hiring/matching
model with a fixed applicant pool. **The delta, stated precisely:** the harm is
allocative and cross-sectional, measured at one point in time on one cohort;
there is no dynamics, no retraining, no environment that reacts, and therefore
no stability question. P2's harm is a different harm with a different remedy: a
market can be statically fine and dynamically fragile at the same shared-model
fraction. This is the nearest prior art on the headline object and it gets a
named-delta sentence, not a mention.

**A2. Bommasani, Creel, Bansal, Card, Liang. "Picking on the Same Person: Does
Algorithmic Monoculture harm Users?" NeurIPS 2022.** [B]
Formalizes outcome homogenization: shared components cause the *same*
individuals to be rejected everywhere, a harm distinct from average accuracy
loss. Again cross-sectional, again on outcomes rather than dynamics.

**A3. Bommasani et al. "On the Opportunities and Risks of Foundation Models."
arXiv:2108.07258, 2021.** [B]
The homogenization argument at ecosystem scale, and the origin of the
"defects propagate downstream" framing that P2's supply-chain decomposition
makes quantitative. A report, not a peer-reviewed result. Cited for the framing
and the vocabulary, never for a gap claim.

**A4. Toups, Bommasani, Creel, Bana, Jurafsky, Liang. "Ecosystem-level Analysis
of Deployed Machine Learning Reveals Homogeneous Outcomes." NeurIPS 2023.** [B]
Measures homogenization empirically across deployed systems. Establishes that
the shared-component fraction P2 calls `s` is a real, measurable quantity in
deployed ecosystems, which matters because a reviewer will ask whether `s` is a
modeling convenience. It is not, and this is the citation that says so.

**A5. Marx, Calmon, Ustun. "Predictive Multiplicity in Classification." ICML
2020; Black, Raghavan, Barocas. "Model Multiplicity: Opportunities, Concerns,
and Solutions." FAccT 2022.** [B]
Model multiplicity: many models fit the data equally well and disagree on
individuals. The **conceptual inverse** of P2's object and worth stating as
such. Multiplicity asks how much models *could* differ; P2's `lambda_max(R)`
measures how much their *feedback directions actually* differ, and shows that
the second quantity, not the first, is what a market's stability depends on. A
market of maximally multiplicitous models with aligned response Jacobians is
still a monoculture in P2's sense.

**A6. Creel, Hellman. "The Algorithmic Leviathan: Arbitrariness, Fairness, and
Opportunity in Algorithmic Decision-Making Systems." Canadian Journal of
Philosophy 52(1):26-43, 2022.** [B]
The normative case against ecosystem-wide algorithmic uniformity. Cited for the
framing sentence that monoculture harm is a systemic property rather than a
per-decision one, which is the philosophical version of P2's private-versus-
systemic distinction.

**A7. Peng, Garg. "Monoculture in matching markets." NeurIPS 2024.** [B, low
confidence, verify before citing]
Extends A1 to two-sided matching. If it exists as recorded it is the closest
recent extension and belongs in the paragraph; if the citation does not verify,
drop it. Nothing in P2 depends on it.

**A8. The cybersecurity precedent. Geer et al. "CyberInsecurity: The Cost of
Monopoly." Computer and Communications Industry Association, 2003; Birman,
Schneider. "The Monoculture Risk Put into Context." IEEE Security & Privacy
7(1):14-17, 2009.** [B]
Twenty years before the ML version, the same argument in software: a homogeneous
installed base is vulnerable to a single exploit, and the epidemiological
analogy was explicit. Birman and Schneider is the *skeptical* entry and is more
useful for it, since it argues the biological analogy is often invoked loosely.
P2 must therefore earn the analogy rather than assert it, and it does: the
epidemic threshold and the retraining threshold are both spectral radii of a
linearized operator, which is a structural identity and not a metaphor. Citing
the skeptic and then meeting the objection is stronger than citing only the
enthusiasts.

**Cluster A verdict.** The literature owns the word "monoculture" and owns the
static harm. Not one entry contains a dynamical system, a retraining loop, or a
stability boundary. The dynamical harm is unclaimed.

## Cluster B. Multiplayer and multi-agent performative prediction: where the dynamics live

The strongest technical prior-art threat, so the deltas are stated at the level
of the mathematical object rather than at the level of topic.

**B1. Perdomo, Zrnic, Mendler-Dunner, Hardt. "Performative Prediction." ICML
2020.** [V1]
The framework and the modulus `m = eps*beta/gamma` that P2's systemic version
generalizes. Single learner throughout.

**B2. Mendler-Dunner, Perdomo, Zrnic, Hardt. "Stochastic Optimization for
Performative Prediction." NeurIPS 2020.** [V1]
Greedy against lazy deployment. **Load-bearing for Theorem 2**, because the
single-learner lazy-deployment slope `mu(K) = -m + c^K(1+m)` is the piece P2
composes with the multi-agent amplification law. That composition has not been
done, and this is the paper whose result gets composed.

**B3. Izzo, Ying, Zou. "How to Learn when Data Reacts to Your Model:
Performative Gradient Descent." ICML 2021.** [V1]
The corrected update. **Load-bearing for Theorem 3**, because the corrected loop
is the "vaccine" whose population-level effect P2 computes. Studied here as one
learner's algorithm, and the question "what happens when a *fraction* of a
market runs it" is not posed.

**B4. Miller, Perdomo, Zrnic. "Outside the Echo Chamber: Optimizing the
Performative Risk." ICML 2021.** [V1]
Conditions for tractable performative-risk optimization; names the echo-chamber
phenomenon. The private benefit side of P2's public-good argument, since it is
what an un-blinded firm captures for itself.

**B5. Drusvyatskiy, Xiao. "Stochastic Optimization with Decision-Dependent
Distributions." Mathematics of OR 47(2):954-998, 2022.** [V1]
The optimization-theoretic consolidation. Cited for the general
decision-dependent framing.

**B6. Li, Wai. "State-Dependent Performative Prediction with Stochastic
Approximation." AISTATS 2022.** [V1]
Stateful and Markovian environments, which is the setting the simulator actually
lives in. No multi-agent alignment structure.

**B7. Narang, Faulkner, Drusvyatskiy, Fazel, Ratliff. "Multiplayer Performative
Prediction: Learning in Decision-Dependent Games." JMLR 24, 2023
(arXiv:2201.03398).** [B]
**The nearest dynamics in the literature, and the citation P2 cannot omit.**
Multiple learners in a shared decision-dependent environment, with equilibrium
concepts (performatively stable equilibrium) and convergence conditions for
repeated retraining. **The delta, stated at the object level:** their coupling
enters through *scalar* sensitivity and Lipschitz constants on the joint
distribution map. There is no object in their framework representing *which
direction* each agent perturbs the environment, so two markets with identical
sensitivity constants but opposite alignment structure are indistinguishable in
their condition and have completely different stability in P2's. That is exactly
what `R` supplies. Consequently their framework cannot express monoculture,
cannot express model provenance, and has no supply chain. It also has no policy
analysis: no externality is priced, no mixed population is studied, and
retraining frequency is not a variable.

**B8. Piliouras, Yu. "Multi-agent Performative Prediction: From Global Stability
and Optimality to Chaos." EC 2023.** [B]
The dynamical-systems reading: multi-agent performative dynamics can be stable,
optimal, or chaotic depending on parameters. Establishes that the multi-agent
stability question is taken seriously at an economics venue, which is
supportive rather than threatening. Same delta as B7 on the alignment object,
plus no policy instruments.

**B9. Brown, Hod, Kalemaj. "Performative Prediction in a Stateful World."
AISTATS 2022.** [B] Stateful extension; cited to delimit scope.

**B10. Jagadeesan, Zrnic, Mendler-Dunner. "Regret Minimization with Performative
Feedback." ICML 2022.** [V1]
Cited here only to delimit scope: it is the companion pricing paper's nearest
neighbor, not P2's. Single learner, and the question is the cost of *search*.

**B11. Hardt, Mendler-Dunner. "Performative Prediction: Past and Future."
arXiv:2310.16608, 2023 (survey).** [B]
The field's own map of itself. **Its open-problems discussion contains no entry
corresponding to alignment-dependent multi-agent stability, retraining cadence
as a systemic lever, mixed populations of corrected and uncorrected learners, or
policy instruments for performative externalities.** The cleanest available
evidence that the gaps are real, from the field's founders.

**B12. Strategic classification. Hardt, Megiddo, Papadimitriou, Wootters.
"Strategic Classification." ITCS 2016; Dong, Roth, Schutzman, Waggoner, Wu.
"Strategic Classification from Revealed Preferences." EC 2018.** [B]
The adversarial cousin, where the environment reacts because agents
strategically manipulate. Cited in one sentence to place P2's setting: the
response here is aggregate and non-strategic, so the externality is a
coordination failure rather than a game against the classifier.

**B13. Nagarajan, Ashok. "REFLEX: Reflexive Equilibrium Fixed-point Learning
for Endogenous eXchanges." arXiv:2608.16155, 2026.** [V1]
**The direct base, and the largest overlap surface in this review.** It
instantiates B1's framework in a structural OTC market-making model where every
constant is computed from microstructure primitives rather than fitted, and
supplies three inputs this paper composes: the symmetric multi-dealer law
`J = -m_1[(1-kappa)I + kappa 1 1']` with its measured `1.74x / 3.16x`
amplification, the single-dealer lazy-deployment lemma
`mu(K) = -m + c^K(1+m)`, and the structurally anchored corrected update.

**The non-overlap statement, claim by claim, because this is the first question
a reviewer asks.** REFLEX's multi-dealer result is the monoculture corner
`R = 1 1'` of Theorem 1 and carries no alignment object, no model provenance and
no supply chain. Its lazy-deployment lemma is single-learner and has never been
composed with the multi-agent law, which is Theorem 2 and its critical-crowding
level. Its corrected update has only ever been run single-dealer, so the
mixed-population question that produces Theorem 3 is unposed there. It contains
no welfare statement, no policy instrument, and no substitution frontier.
Everything in this paper sits strictly above it.

Cited in the third person as an ordinary public reference. Under double-blind
that is a requirement, and it also raises the stakes on the paragraph above: a
reviewer reads REFLEX as a third-party paper this submission leans on heavily,
so the delta has to be stated rather than assumed.

**Cluster B verdict.** The dynamics exist and the multi-agent case has been
posed. What does not exist anywhere in it: a directional alignment object, model
provenance, retraining frequency as a lever, mixed populations, or any welfare
or policy statement.

## Cluster C. Externalities, public goods, and corrective taxation: the apparatus

Nothing in this cluster is new, and the paper says so. It is cited so that an
economics reviewer sees the standard apparatus used correctly rather than
reinvented with different names.

**C1. Pigou. "The Economics of Welfare." Macmillan, 1920.** [B]
The corrective tax equal to marginal external damage. Theorem 4 is a Pigouvian
wedge and is called one.

**C2. Meade. "External Economies and Diseconomies in a Competitive Situation."
Economic Journal 62(245):54-67, 1952; Buchanan, Stubblebine. "Externality."
Economica 29(116):371-384, 1962.** [B]
The formal anatomy of an externality, and the distinction between technological
and pecuniary externalities. **This distinction matters for P2 and a good
reviewer will raise it:** competitors' actions affecting each other through
prices is pecuniary and not a market failure. P2's externality is technological,
because the coupling runs through the *data-generating process* each firm's
learner faces, not through the price at which they trade. Say it explicitly,
in one sentence, citing Buchanan and Stubblebine.

**C3. Baumol. "On Taxation and the Control of Externalities." AER
62(3):307-322, 1972; Sandmo. "Optimal Taxation in the Presence of Externalities."
Swedish Journal of Economics 77(1):86-98, 1975.** [B]
The modern theory of the corrective tax, including what happens when the tax is
set without knowing the damage function exactly. Relevant because `R` and `s`
are unobservable to the regulator, which is why the supervision section exists.

**C4. Samuelson. "The Pure Theory of Public Expenditure." Review of Economics
and Statistics 36(4):387-389, 1954; Olson. "The Logic of Collective Action."
Harvard, 1965; Bergstrom, Blume, Varian. "On the Private Provision of Public
Goods." Journal of Public Economics 29(1):25-49, 1986.** [B]
Public goods and free-riding in private provision. **Load-bearing for Theorem
3's economic reading:** correction is a public good, an un-blinded firm captures
a private benefit while the stability it contributes accrues to everyone, and
Bergstrom-Blume-Varian is the citation for why the market lands below `rho*` on
its own.

**C5. Weitzman. "Prices vs. Quantities." Review of Economic Studies
41(4):477-491, 1974.** [B]
**The instrument-choice question, and a citation P2 cannot skip.** The paper
offers a quantity instrument (cadence caps), a technology mandate and structural
remedy (correction, diversity floors), and a price instrument (the wedge).
Weitzman is the classical answer to which one to prefer under uncertainty. P2
cites it for the framing and does not solve it, and says so in one sentence.
Omitting it invites the objection from any economics reviewer; including it
converts the objection into acknowledged future work.

**Cluster C verdict.** Entirely classical, entirely conceded, cited for correct
use. The contribution is that these instruments have never been applied to
adaptation aggressiveness or model provenance, because the object they would
price did not exist.

## Cluster D. Systemic risk, crowding, and the regulator's dilemma: where private-versus-systemic was posed before

The finance and complex-systems literature posed P2's framing decades ago, for
agents that do not learn. This is the cluster where P2's honesty is tested, and
both halves have to be said.

**D1. Beale, Rand, Battey, Croxson, May, Nowak. "Individual versus systemic risk
and the Regulator's Dilemma." PNAS 108(31):12647-12652, 2011.** [B]
**The direct framing ancestor and the third of the six load-bearing citations.**
Banks each diversifying optimally choose *similar* portfolios, which maximizes
the probability of simultaneous failure. Individually rational, systemically
disastrous, and the paper's title is literally P2's Section 4. **The delta:**
their agents solve a static portfolio problem and do not learn, so there is no
retraining loop, no modulus, no cadence, and no stability boundary. The
homogeneity is a portfolio overlap, not an alignment of feedback directions.
Most importantly there is no second instrument: they have diversity, and nothing
to trade it against, so no substitution frontier can arise. P2's contribution
against D1 is precisely that the agents learn, which supplies both a mechanism
(aligned feedback resonates through retraining) and a second lever (correct the
learning instead of diversifying the models).

**D2. Wagner. "Diversification at Financial Institutions and Systemic Crises."
Journal of Financial Intermediation 19(3):373-386, 2010.** [B]
The same tension formalized: full diversification at the level of each
institution is not socially optimal because it homogenizes the system. The
cleanest statement anywhere that *individually optimal diversity choices produce
systemically dangerous uniformity*, which is the economic logic driving markets
to high `s` in P2.

**D3. Haldane, May. "Systemic Risk in Banking Ecosystems." Nature 469:351-355,
2011.** [B]
Ecological and epidemiological framings for financial stability, from a central
banker and a theoretical ecologist. Establishes the legitimacy of the analogy
P2 uses, at the highest possible venue, and predates the current AI discussion
by fifteen years.

**D4. Khandani, Lo. "What Happened to the Quants in August 2007?" Journal of
Investment Management 5(4):29-78, 2007.** [B]
The empirical event: many funds running similar strategies on similar signals
unwound simultaneously, and the crowding was invisible from any single fund's
risk report. **The best real-world instance of P2's mechanism that predates
machine learning entirely**, and the answer to a reviewer asking whether the
paper's scenario is hypothetical. Cited once, in the introduction, as motivation
rather than as evidence.

**D5. Acemoglu, Ozdaglar, Tahbaz-Salehi. "Systemic Risk and Stability in
Financial Networks." AER 105(2):564-608, 2015; Elliott, Golub, Jackson.
"Financial Networks and Contagion." AER 104(10):3115-3153, 2014; Allen, Gale.
"Financial Contagion." JPE 108(1):1-33, 2000.** [B]
The network-contagion canon: how the topology of exposures determines whether a
shock is absorbed or amplified, with phase transitions in connectivity.
Structurally the closest *mathematics* in economics to P2's spectral condition.
**The delta:** their network is a network of *balance-sheet exposures* and the
propagating object is a *default*. P2's coupling is through a shared
data-generating process and the propagating object is a *retraining update*.
Neither has a learner anywhere in it.

**D6. Brunnermeier, Pedersen. "Market Liquidity and Funding Liquidity." Review
of Financial Studies 22(6):2201-2238, 2009; Danielsson, Shin, Zigrand.
"Endogenous and Systemic Risk." In Quantifying Systemic Risk, University of
Chicago Press, 2012.** [B]
Endogenous risk: risk generated by participants' responses to risk itself,
including the destabilizing feedback of risk-sensitive constraints. The nearest
thing in finance to a performative loop, and the honest ancestor of the phrase
"the environment reacts to the decision". **The delta:** the feedback runs
through constraints and prices under fixed decision rules, not through a
learner's retraining on self-induced data, so there is no analog of `m_1` and
nothing corresponding to correcting the learning.

**D7. Kirilenko, Kyle, Samadi, Tuzun. "The Flash Crash: High-Frequency Trading
in an Electronic Market." Journal of Finance 72(3):967-998, 2017.** [B]
Automated participants interacting to produce an outcome no participant chose.
One sentence in the introduction, alongside D4.

**D8. Herding. Banerjee. "A Simple Model of Herd Behavior." QJE
107(3):797-817, 1992; Bikhchandani, Hirshleifer, Welch. "A Theory of Fads,
Fashion, Custom, and Cultural Change as Informational Cascades." JPE
100(5):992-1026, 1992; Scharfstein, Stein. "Herd Behavior and Investment." AER
80(3):465-479, 1990.** [B]
Why rational agents end up doing the same thing: informational cascades and
reputational incentives. **Distinguish clearly.** Herding is about *beliefs and
choices* converging through observational learning. P2's alignment is about
*feedback directions* being mechanically identical because the models share
weights, and it obtains even when firms never observe each other. Same
destination, different mechanism, and conflating them would be a real error. One
sentence, drawing the distinction.

**D9. Nagarajan, Mittal. "PEBSA: Predicting Economic Behavior via Sentiment
Analysis." International Journal of Engineering and Computer Science
13(12):26656-26676, 2024.** [V1]
Cited once, in Section 8, and for the contrast rather than for a shared method.
It belongs to the same broad question that section asks, which is what can be
inferred about the state of an economy from aggregate public signals no single
participant controls. **The delta is the measurement channel.** PEBSA's is
*exogenous*: sentiment is a signal about an economy the observer stands outside
of, and the accuracy of the inference does not depend on the economy's own
dynamics. Section 8's observable is *endogenous*: the public prices a supervisor
reads are generated by the very adaptive agents being monitored, so the
measurement channel is part of the system and the signal strengthens as the
system nears instability. Do not oversell the link. If Section 8 is cut, which
it is first in the de-scope order, this citation goes with it or drops to one
line in related work.

**Cluster D verdict.** The framing, the tension, and the mathematics all have
respected ancestors here. What no entry has: a learner. Adding one is what
produces a modulus, a cadence, a correction that can be mandated, and a second
axis to trade diversity against.

## Cluster E. Epidemic thresholds and herd immunity: the law Result 3 lands on

P2 invokes a famous law and must earn it rather than gesture at it.

**E1. Kermack, McKendrick. "A Contribution to the Mathematical Theory of
Epidemics." Proceedings of the Royal Society A 115(772):700-721, 1927.** [B]
The threshold theorem and the origin of `R_0`.

**E2. Anderson, May. "Infectious Diseases of Humans: Dynamics and Control."
Oxford University Press, 1991; Fine, Eames, Heymann. "Herd Immunity: A Rough
Guide." Clinical Infectious Diseases 52(7):911-916, 2011.** [B]
The critical vaccination fraction `1 - 1/R_0`, the exact form P2's `rho*`
collapses to at `kappa = s = 1`, plus Fine et al.'s careful account of the
assumptions the simple formula needs (homogeneous mixing above all). **Load-
bearing, and the assumptions matter:** P2's collapse also requires the
homogeneous corner, and the paper says so in the same breath as the formula.

**E3. Diekmann, Heesterbeek, Metz. "On the definition and the computation of the
basic reproduction ratio R0 in models for infectious diseases in heterogeneous
populations." Journal of Mathematical Biology 28(4):365-382, 1990.** [B]
**The citation that turns the analogy into a structural identity, and the reason
the parallel is not decoration.** `R_0` in a heterogeneous population is defined
as the *spectral radius of the next-generation operator*. `m_N` is the spectral
radius of the joint retraining Jacobian. The two thresholds are the same
mathematical statement about a linearized operator, which is why the vaccination
law transfers without adjustment and why the heterogeneous version transfers
too. This is the strongest single citation in the review and the paper should
lean on it hard.

**E4. Pastor-Satorras, Vespignani. "Epidemic Spreading in Scale-Free Networks."
Physical Review Letters 86(14):3200-3203, 2001; Wang, Chakrabarti, Wang,
Faloutsos. "Epidemic Spreading in Real Networks: An Eigenvalue Viewpoint." SRDS
2003; Van Mieghem, Omic, Kooij. "Virus Spread in Networks." IEEE/ACM
Transactions on Networking 17(1):1-14, 2009.** [B]
The network version: the epidemic threshold is `1/lambda_max` of the adjacency
matrix. **Structurally identical to P2's `lambda_max(R)` condition**, and this
is what licenses reading the alignment matrix as a contact structure between
learners. Wang et al. is the cleanest statement and is the one to cite in the
body; the other two go in the footnote.

**Cluster E verdict.** The law is classical and is conceded as classical. The
contribution is that `R_0` here is a *learning* modulus derived from
microstructure primitives rather than fitted, the contact structure is *model
alignment* rather than physical mixing, and the vaccine is an *algorithm* that a
regulator can mandate. The paper's honest self-description is that it identifies
a system in which the epidemiological threshold applies exactly, and computes
its `R_0` from primitives.

## Cluster F. Effective counts and spectra of correlation matrices: the defensive footnote

`lambda_max(R)` is not a new statistic. Concede it immediately, in a footnote,
and the cheapest available referee objection ("you renamed effective rank")
disappears.

**F1. Laloux, Cizeau, Bouchaud, Potters. "Noise Dressing of Financial
Correlation Matrices." Physical Review Letters 83(7):1467-1470, 1999; Plerou,
Gopikrishnan, Rosenow, Amaral, Guhr, Stanley. "Random matrix approach to cross
correlations in financial data." Physical Review E 65(6):066126, 2002.** [B]
`lambda_max` of a return correlation matrix as the strength of the common market
mode, with the random-matrix null for what counts as signal. **The closest
existing use of the exact same statistic**, and the reason P2 must be explicit
that the novelty is the matrix it is computed from, not the eigenvalue.

**F2. Roy, Vetterli. "The effective rank: A measure of effective dimensionality."
EUSIPCO 2007.** [B] Effective rank in signal processing.

**F3. Hill. "Diversity and Evenness: A Unifying Notation and Its Consequences."
Ecology 54(2):427-432, 1973; Simpson. "Measurement of Diversity." Nature
163:688, 1949.** [B]
Hill numbers, the "effective number of species". The oldest and clearest
precedent for the phrase "effective number of X", and worth citing because it
shows the naming convention is standard rather than invented.

**F4. Participation ratio and inverse participation ratio. Bell, Dean. "Atomic
vibrations in vitreous silica." Discussions of the Faraday Society 50:55-61,
1970; Thouless. "Electrons in disordered systems and the theory of
localization." Physics Reports 13(3):93-142, 1974.** [B, verify]
The physics lineage of spectral effective counts.

**F5. Hirschman. "The Paternity of an Index." AER 54(5):761-762, 1964.** [B]
The Herfindahl-Hirschman index, the concentration measure a competition
regulator actually uses. **This citation earns its place by being the natural
comparison a policy reader will reach for, and by failing.** HHI is a function
of market *shares*; `lambda_max(R)` is a function of *feedback alignment*. A
market of fifty equal-share firms has a minimal HHI and looks perfectly
competitive, and if all fifty fine-tune one vendor's model it has
`N_eff = 1 + 49 kappa`. Concentration in the product market and concentration in
the model supply chain are different quantities, and only the second one enters
the stability condition. That sentence is worth a paragraph of the paper.

**Cluster F verdict.** The statistic is old, the naming convention is old, and
both are conceded. New: it is computed on **response Jacobians** rather than on
returns or shares, and it enters a **stability condition** rather than
describing a cross-section. Also new, and worth more than it looks: the
demonstration that the mean-based index a policymaker would reach for is the
wrong one, with two counterexamples of different character recorded in
`../math/01-theorem1-alignment.md`.

## Cluster G. AI supply chains and market concentration: the policy conversation

Working papers and policy documents. **Non-load-bearing by construction**, cited
to establish that the question is live and that the paper answers a question
practitioners are actually asking.

**G1. Vipra, Korinek. "Market Concentration Implications of Foundation Models."
Brookings Center on Regulation and Markets working paper, 2023.** [B]
The economics of foundation-model concentration: scale economies at the model
layer, competitive dynamics downstream. Qualitative throughout. **P2's
contribution against this cluster in one line: it turns "concentration risk"
from a rhetorical concern into a term in a stability condition, with a
computable threshold and a price.**

**G2. Widder, West, Whittaker. "Open (For Business): Big Tech, Concentrated
Power, and the Political Economy of Open AI." SSRN, 2023.** [B]
Argues that openness at the model layer does not resolve concentration at the
compute and data layers. Relevant because it undercuts the obvious objection
that open-weight models make `s` small: shared weights are shared weights, and
open ones are shared more widely, not less.

**G3. Narechania, Sitaraman. "An Antimonopoly Approach to Governing Artificial
Intelligence."** [B, verify venue and year]
The structural-remedy argument in law. Cited if it verifies, as the legal
counterpart to the diversity-floor lever. Nothing depends on it.

**G4. Regulation (EU) 2024/1689 (the AI Act), provisions on general-purpose AI
models with systemic risk.** [B, verify article numbers before citing]
**The single most useful policy hook available**, because it establishes that a
regulator has already written "systemic risk" into law for shared general-purpose
models, with obligations triggered by a threshold. P2 supplies exactly what such
a threshold currently lacks, which is a mechanism connecting model sharing to a
measurable systemic quantity. One sentence in the introduction or the
conclusion, with the article numbers verified or the citation dropped.

**Cluster G verdict.** The policy conversation is entirely qualitative. It
supplies P2's motivation and its audience, and none of it constrains the paper's
novelty.

---

## The gaps, with justifications

**G1. Monoculture has no dynamics.** Every entry in Cluster A measures a
cross-sectional harm: correlated outcomes, homogenized rejections, allocative
welfare loss. Not one contains a retraining loop, a stability boundary, or a
time index that matters. The dynamical harm, that aligned feedback directions
resonate through retraining so the market destabilizes at a feedback gain each
firm individually survives, is a different harm with a different remedy.
*Justification:* verified by reading A1 and A2's problem statements; the harm in
both is defined on a single allocation round.

**G2. Multi-agent performative prediction is blind to alignment direction.**
B7 and B8 have genuine dynamics and genuine equilibrium analysis. Their coupling
is a scalar sensitivity, so two markets with identical constants and opposite
alignment structure are indistinguishable in their conditions. There is no
object representing which direction an agent perturbs the environment, hence no
monoculture, no provenance, no supply chain. *Justification:* the coupling
enters through Lipschitz and sensitivity constants on the joint distribution
map; a directional object cannot be recovered from them.

**G3. Retraining frequency is not a lever anywhere.** Lazy deployment (B2) is
single-learner. The multi-agent strand (B7, B8) does not model cadence at all,
treating each round as a full retraining. So the composition, `K`-step
retraining inside the `N`-agent game, is unposed, and with it the frontier
`K_max` and the critical crowding level `(1+c)/(1-c)` past which no cadence
helps. *Justification:* B2's result is stated for one learner and B7's rounds
are atomic.

**G4. No mixed population has been studied.** The corrected update (B3) is
studied as one learner's algorithm. Nobody has asked what happens when a
*fraction* of a market runs it, which is the only question whose answer is a
herd-immunity threshold. The threshold law itself is classical (E1, E2) and its
spectral form on networks is classical (E3, E4), and neither has ever been
applied to a population of learners. *Justification:* the mixed-population
question requires both a multi-agent stability condition and an algorithmic
intervention, and the two literatures that have these do not intersect.

**G5. Diversity and correction as substitutes: no frontier exists.** D1 and D2
have the diversity-versus-systemic-risk tension in its sharpest form, and D1 even
has P2's exact framing in its title. What they lack is a second instrument.
Their agents hold portfolios rather than learn, so the only lever is
heterogeneity itself, and a substitution frontier has nothing to trade against.
The `(rho, s)` iso-stability curve requires an algorithmic intervention that
exists only because the agents learn. *Justification:* D1's model has one degree
of freedom, the overlap of portfolio choices.

**G6. Performative externalities are not priced.** The Pigouvian apparatus (C1,
C3) and the instrument-choice question (C5) are classical, and the AI-policy
conversation (Cluster G) is qualitative. No one has priced adaptation
aggressiveness or model provenance, because the object that would be priced,
a stability cost that is a function of alignment, did not exist.
*Justification:* Cluster G contains no formal welfare model; Cluster C contains
no learning agents.

**G7. `lambda_max` as an effective count is old; on response Jacobians it is
new.** Fully conceded, in a footnote, with F1 through F4. The delta is the
matrix it is computed from and the condition it enters. The genuinely new
observation in this neighborhood is negative and useful: mean-based diversity
indices, including the HHI a competition regulator would reach for (F5), do not
merely understate clustered alignment, they do not order configurations
correctly. Two counterexamples of different character, recorded in the math
notes.

## Novelty verdict, the honest one

**What is genuinely new.** The framing, private against systemic stability for
markets of *adaptive* models, and four objects within it: the effective number
of independent learners entering a stability condition (G2, G7), the
crowding-cadence frontier with its critical-crowding level (G3), the
herd-immunity theorem for a mixed population of learners (G4), and the
substitution frontier between model diversity and corrected learning (G5),
which exists only once the first and third are stated in the same quantity. The
Pigouvian wedge (G6) is a standard instrument applied to a new object, and is
presented that way rather than as a new result.

**What is emphatically not new, and the paper must say so.** Monoculture and its
static harms (A1, A2). The private-versus-systemic tension (D1, D2), which
predates this paper by fifteen years and whose title P2's Section 4 reuses. The
herd-immunity law (E1, E2) and its spectral form on networks (E3, E4). Spectral
effective counts (F1 through F4). The entire policy apparatus (Cluster C).
Endogenous risk as a phenomenon (D6) and crowding as an empirical event (D4).

**P2's correct self-description:** *the learning instance of the regulator's
dilemma, in which the agents' homogeneity is an alignment of feedback
directions rather than of portfolios. In that instance the systemic threshold is
computable from microstructure primitives, the epidemiological vaccination law
applies exactly, and a second policy instrument appears that has no analog when
the agents do not learn.*

"A new theory of systemic risk" is not defensible. "The first stability theory
for markets of retraining agents in which model provenance is a term" is.
Writing it the first way would get the paper killed by any reviewer from
Cluster D, and there will be one.

**The six citations without which the paper is rejected**, each getting a
named-delta sentence rather than a mention: **Kleinberg-Raghavan** (A1, nearest
monoculture), **Narang et al.** (B7, nearest dynamics), **Beale et al.** (D1,
nearest framing), **Anderson-May with Wang et al.** (E2, E4, the law being
invoked), **Weitzman** (C5, the instrument-choice framing), and
**Laloux/Plerou with Roy-Vetterli** (F1, F2, the effective-count concession).

**Two consistency checks worth reporting in the paper.** Diekmann et al. (E3)
define `R_0` as a spectral radius of a next-generation operator, so P2's
threshold and the epidemiological one are the same statement about a linearized
operator rather than an analogy. And Khandani-Lo (D4) is a documented instance
of P2's mechanism occurring in a market with no machine learning in it at all,
which shows the mechanism is about shared response directions rather than about
anything specific to neural networks.

**Why this positioning is a strength.** The paper covers algorithmic
monoculture and model multiplicity, feedback loops and performative prediction
effects, market concentration among AI service providers, AI supply chains and
their dynamics, multi-agent learning dynamics in economic environments, and
ecosystem-level incentive design with one model. This review's cluster structure
maps onto those topics directly: A and F are monoculture, B is feedback, G is
concentration and supply chains, C and D are incentive design.

---

## Verification debt

Everything tagged [B] needs click-through verification. Priority order, because
the list will not clear in one sitting.

**Tier 1, before the submission draft is written.** The six load-bearing
citations, since a wrong year or venue on one of these is the kind of error a
reviewer treats as evidence of carelessness about everything else.

| Entry | Check |
|---|---|
| A1 Kleinberg-Raghavan | PNAS volume, article number, year |
| B7 Narang et al. | JMLR volume and issue; confirm 2023 |
| D1 Beale et al. | PNAS pages, year |
| E2 Anderson-May | edition and publisher; Fine et al. CID pages |
| E4 Wang et al. | SRDS 2003 proceedings details |
| C5 Weitzman | REStud volume, pages |
| F1 Laloux et al. | PRL volume, pages; Plerou PRE article number |

**Tier 2, before camera-ready.** Everything else tagged [B], all of Clusters C
and D's classical entries in particular, where volume and page numbers are
stated from record.

**Tier 3, verify or drop.** Entries flagged low-confidence in the text, where
nothing in the paper depends on the citation and the correct action on a failed
check is deletion rather than repair: A7 (Peng-Garg), F4 (Bell-Dean, Thouless),
G3 (Narechania-Sitaraman), G4 (AI Act article numbers).

**Tier 4, frontier sweep not yet done.** This review has no equivalent of the
companion review's 2024-26 arXiv sweep for the monoculture-dynamics
intersection. Run it before the submission draft, searching on the intersection
terms rather than on either literature alone: monoculture with dynamics or
stability, performative prediction with alignment or heterogeneity or
provenance, model homogenization with feedback. **The gap claims in G1 through
G5 are stated against the literature as reviewed here, and a frontier sweep is
the one thing that could overturn one of them.** Treat that sweep as a
prerequisite for the novelty section, not as a nice-to-have.

---

## Source manifest

**In hand, read, shipped in `pdfs/`:**

| File | Entry | Role in P2 |
|---|---|---|
| `2002.06673__perdomo-performative-prediction.pdf` | B1 | the modulus |
| `2006.06887__mendler-dunner-stochastic-pp.pdf` | B2 | load-bearing, Theorem 2 |
| `2102.07698__izzo-performative-gradient-descent.pdf` | B3 | load-bearing, Theorem 3 |
| `2102.08570__miller-outside-echo-chamber.pdf` | B4 | the private benefit |
| `2011.11173__drusvyatskiy-xiao-decision-dependent.pdf` | B5 | general framing |
| `2110.00800__li-wai-state-dependent-pp.pdf` | B6 | the simulator's setting |
| `2202.00628__jagadeesan-performative-feedback.pdf` | B10 | scope delimitation |
| `1105.3115__gueant-lehalle-inventory-risk.pdf` | market model | instantiation |
| `1907.01225__bergault-gueant-size-matters-otc.pdf` | market model | instantiation |
| `2508.20225__barzykin-adverse-selection-price-reading.pdf` | market model | instantiation |

**The two base papers, tagged [V1] but not in `pdfs/`:** REFLEX (B13,
arXiv:2608.16155) and PEBSA (D9, IJECS 13(12):26656-26676, 2024). Both are held directly
rather than fetched, both are public at submission time, and both are cited as
ordinary third-party references under double-blind.

**Fetchable by script.** `download_litreview_pdfs.sh` in this folder gets the
openly-licensed arXiv versions: Narang et al. (2201.03398), Hardt and
Mendler-Dunner (2310.16608), Bommasani et al. foundation models (2108.07258),
Kleinberg-Raghavan (2101.05853), Toups et al. (2307.05862), Marx et al.
(1909.06677), plus the Cluster B extensions.

**Paywalled or offline.** Cluster C's classical economics, Cluster D's finance
journals, Cluster E's epidemiology monographs, Cluster F's physics letters. DOI
links are in the script's comments where known and flagged where not. All are
standard library holdings.
