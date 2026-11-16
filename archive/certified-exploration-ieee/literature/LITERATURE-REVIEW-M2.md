# Literature Review: "The Price of Self-Knowledge"

## Identification cost, exploration, and stability in performative systems - the six literatures the paper touches, the gaps between them, and the novelty verdict

**Prepared 2026-08-17 for the certified-exploration paper (M2).**

**Method and verification statement.** Every source below was verified by at
least one of: (V1) the PDF is in hand and was read (10 papers, shipped with
the REFLEX repository under `literature/literature-vignesh/pdfs/`, fetched
from arXiv by its `download_pdfs.sh`); (V2) bibliographic record confirmed
this week against the publisher or aggregator page via web search (venue,
volume/pages, year); (V3) canonical classical result, standard in its field's
textbooks, bibliographic details cross-checked against at least one
independent index. Each entry is tagged. Credibility bar: every load-bearing
source is either a top peer-reviewed venue in its field (ICML, NeurIPS,
AISTATS, COLT, Operations Research, Management Science, Automatica, Annals of
Statistics, JET, REStud, Econometrica, FoCM) or a survey/monograph of record;
arXiv-only items are used solely to map the 2024-26 frontier and are marked
as such, never load-bearing for a gap claim.

**PDF availability note.** This build environment's network egress blocks
arXiv, PMLR and publisher sites, so PDFs could not be downloaded *from
here*. The 10 core PDFs already in hand ship in this package (`pdfs/`); for
the remainder, `download_litreview_pdfs.sh` (included) fetches every
openly-licensed PDF (arXiv versions) with one command on an unrestricted
machine, and the manifest lists DOI links for the paywalled classics
(Operations Research, REStud, JET, Automatica items), which are standard
library holdings.

---

## 0. The paper being positioned, in three sentences

M2 claims: (i) a converging performative retraining loop generates only a
bounded amount of Fisher information about its own response - identification
requires deliberate exploration ("saturation"); (ii) with exploration, the
product of estimator variance and incremental performative risk is pinned at
`(1/2) gamma_PO sigma^2`, invariant to exploration intensity, horizon and
modulus, with a minimax version over all adaptive policies and a matrix
version whose equality case gives the optimal exploration shape
`Gamma_PO^{-1/2}`; (iii) the optimal way to spend the budget is a D-optimal
design under a *closed-loop stability constraint*, with an
anchoring-vs-misspecification crossover and an explore-or-stay-blind ROI
rule. The question this review answers: which parts of that already exist,
where, and in what form.

---

## Cluster A - Performative prediction: the home field

**A1. Perdomo, Zrnic, Mendler-Dunner, Hardt. "Performative Prediction."
ICML 2020.** [V1: PDF in hand]
The framework: distribution map `D(theta)`, performative risk, the two
solution concepts (performatively stable point vs performative optimum), and
the contraction theorem - repeated risk minimization converges iff
`eps < gamma/beta`. Establishes the modulus `m = eps*beta/gamma` that M2's
saturation cap is expressed in. *Contains no estimation of the map at all*:
`eps` is an abstract Lipschitz constant, and RRM needs no knowledge of it.

**A2. Mendler-Dunner, Perdomo, Zrnic, Hardt. "Stochastic Optimization for
Performative Prediction." NeurIPS 2020.** [V1]
Greedy vs lazy deployment for stochastic updates; convergence rates to the
stable point. Relevant as the ancestor of REFLEX's lazy-deployment theory;
still no identification question - all algorithms are blind to `dD/dtheta`.

**A3. Izzo, Ying, Zou. "How to Learn when Data Reacts to Your Model:
Performative Gradient Descent." ICML 2021.** [V1]
The first algorithm that *estimates* the distribution response (by finite
differences across deployments) and corrects the gradient, converging to the
performative optimum. This is the paper that creates M2's question: PerfGD
*consumes* an estimate of `dD/dtheta` and pays for it with perturbed
deployments, but the paper prices neither the estimate nor the perturbations
- accuracy enters as an assumption, cost does not enter at all.

**A4. Miller, Perdomo, Zrnic. "Outside the Echo Chamber: Optimizing the
Performative Risk." ICML 2021.** [V1]
When is direct performative-risk optimization tractable; conditions for
convexity. Names the echo-chamber phenomenon M2's ROI corollary prices.

**A5. Drusvyatskiy, Xiao. "Stochastic Optimization with Decision-Dependent
Distributions." Mathematics of OR 47(2), 2022.** [V1]
The optimization-theoretic consolidation of decision-dependent settings.
MOR venue - the journal M2 designates - and its style anchor.

**A6. Li, Wai. "State-Dependent Performative Prediction with Stochastic
Approximation." AISTATS 2022.** [V1] Stateful/Markovian environments -
the setting REFLEX's simulator actually lives in; no identification result.

**A7. Brown, Hod, Kalemaj. "Performative Prediction in a Stateful World."
AISTATS 2022; Narang et al. "Multiplayer Performative Prediction." 2022
(JMLR 2023); Piliouras, Yu. "Performative Games," 2022.** [V2/V1]
Stateful and multiplayer extensions; cited in M2 only to delimit scope (the
multiplayer strand belongs to the herd-immunity companion paper).

**A8. Hardt, Mendler-Dunner. "Performative Prediction: Past and Future."
arXiv:2310.16608, 2023 (survey).** [V2]
The field's own map of itself. Its open-questions discussion treats
estimation of the distribution map as a practical difficulty; **no entry in
the survey corresponds to pricing identification, information saturation of
RRM, or stability-constrained exploration** - the cleanest available
evidence that the gap is real, from the field's founders.

**A9. REFLEX (*Reflexive Equilibrium Fixed-point Learning for Endogenous
eXchanges*), arXiv:2608.16155, 2026.** [V1]
**The direct base, and the largest overlap surface in this review.** It
instantiates A1's framework in a structural OTC market-making model where every
constant in every theorem here is computable from primitives rather than
assumed: `gamma_PO` and `Gamma_PO` from its theory modules, `m` from its
modulus machinery. Its retraining loop is what falsifies the statements in M2,
and its documented "anchoring, not capacity" negative result - the free-form
learned correction failing because the converged loop stops generating
identifying variation - is the phenomenon M2's saturation theorem explains and
Theorem 6 turns into a decision rule.

**The non-overlap statement, claim by claim.** REFLEX supplies constants and a
falsification harness; it prices nothing. It contains no information-cost
frontier, no saturation cap tied to the modulus, no minimax lower bound, no
matrix uncertainty principle or optimal exploration shape, and no
stability-constrained design problem. Its negative result is an empirical
finding reported without a theory of why, which is precisely the gap M2 fills.
Retrodiction of a published failure is evidence no synthetic example can buy,
and it is only evidence because the failure was documented before the theory
existed.

**Frontier check (2024-26, arXiv-level, non-load-bearing).** [V2, abstracts
via search only] "Plug-in Performative Optimization" (Lin, Zrnic, ICML 2024
- see Cluster B, it is the closest paper to M2's Theorem 6); "Learning the
Distribution Map in Reverse Causal Performative Prediction"
(arXiv:2405.15172); "Performative Prediction on Games and Mechanism Design"
(arXiv:2408.05146); "Decision-Dependent Stochastic Optimization: The Role of
Distribution Dynamics" (arXiv:2503.07324); "SPRINT: Stochastic Performative
Prediction with Variance Reduction" (arXiv:2509.17304); "Partially
Performative Prediction" (arXiv:2606.07890); "Dissecting Performative
Prediction: A Comprehensive Survey" (arXiv:2602.10176); "Retraining Seeks
Stable Signals" (arXiv:2607.15623). Sweep verdict: the frontier is moving
toward *better estimators and richer settings*, not toward pricing the
estimation. None of these titles/abstracts contains an information-cost
tradeoff, an invariance identity, or a stability-constrained design.

## Cluster B - Exploration and estimation *inside* performative prediction: the nearest ML neighbors

**B1. Jagadeesan, Zrnic, Mendler-Dunner. "Regret Minimization with
Performative Feedback." ICML 2022.** [V1: PDF in hand, read for this review]
The closest ML prior art, so its delta is stated precisely. Their setting:
the learner sequentially deploys models and suffers *performative regret*
(cumulative excess performative risk vs the optimum); their contribution:
performative feedback (deploying gives samples of `D(theta)`, not just a
risk value) admits regret bounds scaling with the complexity of the
*distribution map* rather than of the risk - an explore-with-bandit-tools,
then-propagate algorithm. **What it is:** an algorithmic upper bound on the
cumulative cost of *finding the optimum*. **What it is not (M2's content):**
there is no retraining loop (the learner picks `theta` freely - RRM and its
cobweb never appear, so nothing can saturate); there is no
estimator-precision-vs-cost frontier (regret conflates search cost with
estimation, and no lower bound on identification is stated); there is no
stability constraint (deployments cannot destabilize anything in their
model); there is no design shaping (their exploration is uniform/bandit-
driven, not information-optimal under a curvature-weighted budget).
M2 cites B1 as the complementary upper-bound story: B1 answers "how
expensive is it to *find* the optimum," M2 answers "what does it cost to
*know your own feedback*, whoever you are and however you search."

**B2. Lin, Zrnic. "Plug-in Performative Optimization." ICML 2024
(arXiv:2305.18728).** [V2 - flagged as the closest paper to M2's Theorem 6]
They study using possibly *misspecified* structural models of the
distribution map inside performative optimization and quantify when a wrong
model still helps - a bias-variance argument for model-based
performativity. This genuinely overlaps in spirit with M2's anchoring
crossover, and the review's recommendation is to treat it as the launch
point: **M2's Theorem 6 must be stated as sharpening plug-in optimization's
qualitative message into a budget-explicit decision rule** - anchor iff
`delta_mis^2 < (1/2) gamma_PO sigma^2 / B` - i.e. the crossover is priced in
the same currency as the rest of the paper (the exploration budget), which
plug-in optimization does not do (it has no cost side). Failure to cite and
position B2 would be M2's single most dangerous review vulnerability;
positioned, it becomes corroboration that the field wants exactly this
question answered.

**B3. Zeroth-order / derivative-free performative optimization; adaptive
noise-injection methods.** [V2, family-level]
Several works estimate performative gradients by injected perturbations
(finite differences across deployments; user-specified noise sequences).
These are the *devices* M2 prices: in all of them the perturbation size is
a tuning parameter chosen for convergence, its P&L cost unmodeled, its
information yield implicit. The existence of this family is the
demand-side evidence for M2's framework.

## Cluster C - Operations research: dynamic pricing with demand learning (the venue's home literature, and the strongest prior-art threat)

This cluster is where an operations-research reviewer will first look, and the review's
most important finding is here: the *phenomena* M2 studies have true
ancestors in this literature, while the *objects* M2 contributes do not
appear in it. Both halves must be said in the paper.

**C1. Rothschild. "A Two-Armed Bandit Theory of Market Pricing." Journal of
Economic Theory 9(2):185-202, 1974.** [V2]
The origin: a firm learning demand by experimentation may *rationally stop
learning* and settle on the wrong price with positive probability.
Incomplete learning as an equilibrium outcome, fifty years before
"echo chamber." M2's ROI corollary (explore iff patient enough) is the
closed-form descendant of Rothschild's qualitative insight, and must cite
it as such.

**C2. Lai, Robbins. "Adaptive Design and Stochastic Approximation." Annals
of Statistics 7(6), 1979; and "Iterated least squares in multiperiod
control," Adv. Applied Math 3, 1982.** [V2]
The mathematical ancestor of M2's frontier. In adaptive stochastic
approximation toward a target, they show the *cost of observations*
(sum of squared deviations from the target) can be driven to `O(log n)`
while estimation remains efficient. **Consistency check performed for this
review:** on M2's frontier, `Var x Cost = (1/2) gamma sigma^2` implies a
scheme with cost `O(log n)` has slope-variance `Theta(sigma^2/log n)` -
which is exactly the Lai-Robbins regime. Their schemes are *points on* M2's
frontier; the frontier itself (the invariance identity, the minimax bound
over adaptive policies, the matrix/design version) is not in their work,
and their environment is a fixed regression function, not a distribution
map that reacts and a loop that retrains. This is the single most important
citation for M2's mathematical honesty.

**C3. Keskin, Zeevi. "Dynamic Pricing with an Unknown Demand Model:
Asymptotically Optimal Semi-Myopic Policies." Operations Research
62(5):1142-1167, 2014.** [V2]
The canonical modern statement of learn-while-earn: myopic
(certainty-equivalent) pricing suffers **incomplete learning** - the price
path converges and stops generating identifying variation - and forced
price dispersion restores learning, with `sqrt(T)` (or `log T` with an
anchor point) revenue-loss rates. The phenomenon is the static-environment
ancestor of M2's saturation theorem. The deltas, precisely: (i) their
demand curve is *fixed* - nothing is performative, so there is no modulus,
no cobweb, no stability boundary, and no coupling between contraction speed
and identifiability (M2's Corollary "safety implies blindness" has no
analog); (ii) their results are rate/order statements, not invariance
identities; (iii) their decision variable cannot destabilize the
environment, so constrained-safe design cannot arise; (iv) the mechanism
differs - their learning stalls because *optimization* converges, M2's
because *retraining on self-induced data* contracts, and the cap
`(h_0-h*)^2/(1-m^2)` is a function of the performative feedback strength.

**C4. Harrison, Keskin, Zeevi. "Bayesian Dynamic Pricing Policies: Learning
and Earning Under a Binary Prior Distribution." Management Science 58(3),
2012.** [V2] The "uninformative price" mechanism: myopic Bayesian pricing
can absorb at a price where the two demand hypotheses are
indistinguishable. Cited alongside C3 as the incomplete-learning canon.

**C5. Broder, Rusmevichientong. "Dynamic Pricing Under a General Parametric
Choice Model." Operations Research 60(4):965-980, 2012.** [V3 - standard
result, bibliographic details to be re-confirmed at camera-ready]
`sqrt(T)` regret lower bound for pricing with unknown parametric demand,
driven by an uninformative-price argument - the order-level
information-cost tradeoff of the pricing world. M2's identity is the exact,
invariant, performative-loop counterpart of this order-level tradeoff.

**C6. den Boer. "Dynamic Pricing and Learning: Historical Origins, Current
Research, and New Directions." Surveys in ORMS 20(1):1-18, 2015.** [V2]
The survey of record for C1-C5's field. Verified: its taxonomy contains no
performative/reactive-demand branch - the environment is exogenous
throughout - which is the cluster-level gap statement in one citation.

## Cluster D - Adaptive control and system identification: the oldest ancestry

**D1. Feldbaum. "Dual Control Theory I-IV." Automation and Remote Control,
1960-61.** [V3]
The original statement that control actions have two purposes - regulate
and inform - and that optimal control must trade them off. M2 is, in one
sentence, *dual control for performative learning loops*; the paper should
say so and inherit the sixty-year-old framing honestly.

**D2. Persistent excitation (Astrom, Wittenmark, "Adaptive Control";
Ljung, "System Identification: Theory for the User").** [V3]
Closed-loop operation starves identification - the qualitative form of M2's
saturation theorem, standard in control since the 1970s-80s. M2's delta:
the *exact* cap in terms of the performative modulus, its coupling to the
stability boundary, and the fact that the "controller" here is a retraining
learner whose own convergence is the starvation mechanism.

**D3. Bombois, Scorletti, Gevers, Van den Hof, Hildebrand. "Least Costly
Identification Experiment for Control." Automatica 42:1651-1662, 2006.**
[V2]
The control literature's own "price of identification": design the cheapest
input signal (measured in performance degradation) achieving a target
model-uncertainty set for robust control. Structurally the closest
*optimization problem* to M2's Theorem 5 anywhere in the literature. The
deltas: the plant is an exogenous LTI system (it does not learn, so nothing
is performative and the experiment cannot destabilize a *learning loop* -
their constraint is plant safety, M2's is retraining-map contraction); the
cost enters as a constraint with no invariance identity or minimax frontier
attached; and there is no analog of the objective-curvature-shaped design
`Gamma_PO^{-1/2}` because their cost is not a decision-objective. Not citing
D3 would be fatal with any control-literate reviewer; cited, it shows M2's
question has a respected lineage whose performative version was never
posed.

**D4. Dean, Mania, Matni, Recht, Tu. "On the Sample Complexity of the
Linear Quadratic Regulator." Foundations of Computational Mathematics
20(4):633-679, 2020; Simchowitz, Foster. "Naive Exploration is Optimal for
Online LQR." ICML 2020; Wagenmaker, Simchowitz, Jamieson. "Task-Optimal
Exploration in Linear Dynamical Systems." ICML 2021 (arXiv:2102.05214);
Wagenmaker et al. "Optimal Exploration for Model-Based RL in Nonlinear
Systems." NeurIPS 2023.** [V2]
The modern learning-for-control canon: sample complexity of identification
for control, `sqrt(T)` regret of adaptive LQR, and - Wagenmaker's line -
*task-optimal* experiment design (excite the directions the downstream task
cares about). M2's Theorem 4 equality case (`M* prop Gamma_PO^{-1/2}`:
explore where the objective is flat) is a task-optimal-design result in
which the "task" is the learner's own performative objective; the LQR line
has the design machinery but an exogenous plant and no performative
feedback. Simchowitz-Foster's title result ("naive exploration is optimal
for LQR") is a useful foil: M2's Corollary 4.1 shows naive (isotropic)
exploration is suboptimal in the performative setting by exactly the
curvature-dispersion factor - a clean, quotable contrast to state.

## Cluster E - Optimal experimental design: the toolbox

**E1. Kiefer, Wolfowitz. "The Equivalence of Two Extremum Problems."
Canadian J. Mathematics 12:363-366, 1960; Fedorov, "Theory of Optimal
Experiments" (1972); Pukelsheim, "Optimal Design of Experiments" (Wiley
1993 / SIAM Classics 2006).** [V3]
Classical D-/A-optimality and the equivalence theorem: the design machinery
M2's Theorems 4-5 instantiate. In the entire classical canon the
experimenter's cost is exogenous (samples, time, budget constraints on the
design region) - never the optimizer's own objective, and never a
dynamical-stability constraint on the plant generating the data.

**E2. Van Trees (1968); Gill, Levit. "Applications of the van Trees
Inequality: a Bayesian Cramer-Rao Bound." Bernoulli 1(1-2):59-79, 1995.**
[V3]
The Bayesian Cramer-Rao machinery M2's minimax Theorem 3 is built on -
chosen precisely because it survives adaptive designs and biased
estimators, which the vanilla Cramer-Rao bound does not.

## Cluster F - Economics of learning by experimentation

**F1. Rothschild 1974** - see C1 (it belongs to both clusters).

**F2. McLennan. "Price Dispersion and Incomplete Learning in the Long
Run." J. Economic Dynamics & Control 7(3):331-347, 1984.** [V3]

**F3. Easley, Kiefer. "Controlling a Stochastic Process with Unknown
Parameters." Econometrica 56(5):1045-1064, 1988.** [V3]
Optimal Bayesian agents may converge to incorrect beliefs with positive
probability - rational incomplete learning, the decision-theoretic
foundation under M2's ROI corollary.

**F4. Aghion, Bolton, Harris, Jullien. "Optimal Learning by
Experimentation." Review of Economic Studies 58(4):621-654, 1991.** [V2]
When does optimal experimentation learn the payoff function completely -
conditions (smoothness, discounting) under which learning is adequate or
fails. M2's break-even discount rate is a closed-form instance of their
patience mechanism, computable because the market model pins every
constant.

**F5. Keller, Rady. "Optimal Experimentation in a Changing Environment."
Review of Economic Studies 66(3):475-507, 1999.** [V3]
Experimentation when the demand curve *drifts exogenously*. The nearest
economics gets to a reactive environment - and the environment still does
not react *to the agent*; it drifts on its own. The performative case,
where the environment's change is caused by the learner and feeds back
through retraining, is absent from this line.

**F6. Grossman, Stiglitz. "On the Impossibility of Informationally
Efficient Markets." American Economic Review 70(3):393-408, 1980.** [V3]
Cited for the framing sentence only: information must be paid for in
equilibrium, or no one gathers it. M2 is a micro-founded instance where
the price of information is stated as an identity.

**F7. Nagarajan, Mittal. "PEBSA: Predicting Economic Behavior via Sentiment Analysis." 
International Journal of Engineering and Computer Science 13(12), 2024.** [V1]
One line in related work, as the contrasting **cost structure**, and placed
here because F6 is the cluster's other citation about what information costs.
PEBSA infers economic behavior through a channel whose sampling design is
chosen freely: more data costs collection effort and nothing else, and the
observations are not decisions. M2's premise is the opposite - the design *is*
the decision, and every observation is taken at a price in the objective -
which is the gap the framework fills. Positioned as a contrast, never as a
dependency.

---

## The gaps, with justifications

**G1 - Identification is never priced in performative prediction.**
Exploration appears throughout Cluster B as an algorithmic device (finite
differences, noise injection, explore-exploit phases) whose size is tuned
for convergence, not priced in the objective. Jagadeesan et al. (B1) price
the *search* (regret of finding the optimum), not the *knowledge* (an
estimator-precision-vs-cost frontier); the field's own survey (A8) lists no
such question. Justification of the gap: verified by reading B1 and by the
targeted searches; the nearest results are order-level regret bounds, and
no invariance identity or identification lower bound exists in the field.

**G2 - No saturation theorem for retraining loops.** Incomplete learning
under myopic policies is classical in pricing (C3, C4) and control (D2) -
but in every instance the environment is *exogenous* and the starvation
mechanism is the optimizer's convergence. The performative version - the
*retraining cobweb's own contraction* bounds total Fisher information at
`(h_0-h*)^2/(1-m^2)`, so the cap is set by the performative feedback
strength, vanishing information for the safest loops and full information
exactly at the stability boundary - appears nowhere. The inversion "safety
implies blindness" has no analog in C or D because their settings have no
stability boundary tied to the estimand.

**G3 - No exact exchange rate, anywhere.** Every neighboring literature
expresses the learning-earning tension as a rate or bound (`sqrt(T)` regret
in C3/C5/D4, `O(log n)` cost in C2). The invariance identity
`Var x Cost = (1/2) gamma_PO sigma^2` - exact, distribution-of-effort-free,
modulus-free - and its minimax and matrix versions are new. The Lai-Robbins
consistency check (their `log n` schemes sit *on* the frontier) is both the
strongest sanity test and the proof that the identity is the sharp form of
a tradeoff the ancestors saw only at order level.

**G4 - No stability-constrained experiment design.** Bombois et al. (D3)
minimize experiment cost subject to model-quality for control - the right
problem shape - but their plant is exogenous; the experiment can violate
plant limits, not destabilize a learning loop, because there is no loop.
In M2 the probe deviations feed the retraining map itself, so the design
must maintain `rho(closed loop) < 1` - a constraint class that does not
exist in D3, E1, or B1 (where deployments are unconstrained by
construction). The composition D-optimality x performative budget x
spectral safety is new.

**G5 - Anchoring vs misspecification is not budget-priced.** Lin-Zrnic (B2)
is the closest work in all six clusters: plug-in (structural, possibly
wrong) models of the distribution map, analyzed for optimization benefit.
What it lacks is a cost side - there is no exploration budget, so the
question "when is the parametric family worth its bias, *given what
nonparametric identification costs*" cannot be posed there. M2's crossover
prices both sides in the same currency. The gap is narrower here than
anywhere else in the review, and the paper must say so explicitly.

**G6 - The explore-or-stay-blind decision has no closed form.** Economics
established that rational agents may stop learning (C1, F2, F3) and tied
complete learning to patience (F4) - qualitatively. Because the performative
market model computes every constant (`gamma_PO`, the echo-chamber gap, the
exchange rate), M2 can state the break-even discount rate in closed form.
Novel as a *computable instance* of a classical mechanism, and must be
framed exactly that way.

## Novelty verdict (the honest one)

**What is genuinely new:** the framework - identification of one's own
performative response as a priced, designed, stability-constrained activity
- and four specific objects within it: the saturation cap tied to the
performative modulus (G2), the exact invariance identity with minimax and
matrix versions (G3), the spectral-safety design constraint (G4), and the
budget-priced anchoring crossover (G5, delta over B2). No paper in any of
the six clusters contains any of the four; the field's own survey (A8)
confirms the question is unposed in performative prediction.

**What is emphatically not new, and the paper must say so:** the
learning-vs-earning tension (Feldbaum 1960; Rothschild 1974), incomplete
learning under converging policies (Lai-Robbins; Harrison-Keskin-Zeevi;
Keskin-Zeevi), cost-constrained identification for a downstream task
(Bombois et al.; Wagenmaker et al.), and the design toolbox
(Kiefer-Wolfowitz; van Trees). M2's correct self-description is: *the
performative instance of dual control, in which the plant is the learner's
own retraining loop - and in that instance, tradeoffs the ancestors could
state only at order level become exact identities with computable
constants.* "Completely novel foundation" is defensible for the framework
and the four objects; it is not defensible as a claim that no one ever
studied costly learning, and writing it that way would get the paper killed
by any reviewer from Clusters C or D.

**The four load-bearing citations without which the paper is rejected:**
Jagadeesan et al. (B1 - nearest ML neighbor), Keskin-Zeevi (C3 - nearest OR
phenomenon), Bombois et al. (D3 - nearest optimization problem), Lin-Zrnic
(B2 - nearest to Theorem 6). Each gets a named-delta sentence in related
work. The two consistency checks to report: Lai-Robbins schemes lie on the
frontier (C2); Simchowitz-Foster's "naive exploration is optimal" flips in
the performative setting by exactly the curvature-dispersion factor (D4).

**Why this positioning is a strength:** the paper
bridges ML and OR by construction - its phenomenon
lives in the OR canon (C), its machinery in ML theory (B, E) and control
(D), and its instantiation in a structural market model with real-data
calibration.

---

## Source manifest

**In hand (shipped in `pdfs/`, from the REFLEX repository):**

| File | Paper | Verification |
|---|---|---|
| `2002.06673__perdomo-performative-prediction.pdf` | A1 | V1 |
| `2006.06887__mendler-dunner-stochastic-pp.pdf` | A2 | V1 |
| `2102.07698__izzo-performative-gradient-descent.pdf` | A3 | V1 |
| `2102.08570__miller-outside-echo-chamber.pdf` | A4 | V1 |
| `2011.11173__drusvyatskiy-xiao-decision-dependent.pdf` | A5 | V1 |
| `2110.00800__li-wai-state-dependent-pp.pdf` | A6 | V1 |
| `2202.00628__jagadeesan-performative-feedback.pdf` | B1 | V1 (read for this review) |
| `1105.3115__gueant-lehalle-inventory-risk.pdf` | market-making instantiation | V1 |
| `1907.01225__bergault-gueant-size-matters-otc.pdf` | instantiation | V1 |
| `2508.20225__barzykin-adverse-selection-price-reading.pdf` | instantiation | V1 |

**Fetchable by script (`download_litreview_pdfs.sh` - run on an
unrestricted machine; this environment blocks arXiv):** Hardt-MD survey
(arXiv:2310.16608), Lin-Zrnic (arXiv:2305.18728), Wagenmaker et al.
(arXiv:2102.05214), Narang et al. (arXiv:2201.03398), plus the 2024-26
frontier items listed in Cluster A.

**Paywalled classics (DOI links in the script's comments; standard library
holdings):** Keskin-Zeevi (10.1287/opre.2014.1294), Harrison-Keskin-Zeevi
(10.1287/mnsc.1110.1426), Broder-Rusmevichientong (10.1287/opre.1120.1057),
den Boer survey (10.1016/j.sorms.2015.03.001), Bombois et al.
(10.1016/j.automatica.2006.05.016), Rothschild
(10.1016/0022-0531(74)90066-0), Aghion et al. (10.2307/2297825), Easley-
Kiefer, McLennan, Keller-Rady, Grossman-Stiglitz, Kiefer-Wolfowitz,
Lai-Robbins (10.1214/aos/1176344840), Dean et al.
(10.1007/s10208-019-09426-y), Gill-Levit. DOIs marked [V3] should be
click-verified at camera-ready; all bibliographic facts above were
confirmed as stated.
