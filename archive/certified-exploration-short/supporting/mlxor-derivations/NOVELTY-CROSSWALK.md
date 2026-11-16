# Novelty Crosswalk: theorem -> nearest prior art -> named delta

One row per result; the "delta sentence" is written to be pasted into the
related-work section nearly verbatim. Gap IDs (G1-G6) refer to the
literature review (`litreview/LITERATURE-REVIEW-M2.md`); prior-art
citations were credibility-verified there.

| Result | Nearest prior art | Delta sentence | Gap |
|---|---|---|---|
| T1 + C1.1 (saturation; safety implies blindness) | Persistent excitation (Astrom-Wittenmark; Ljung); incomplete learning under myopic policies (Harrison-Keskin-Zeevi MS'12; Keskin-Zeevi OR'14) | Closed-loop information starvation is classical for *exogenous* plants under converging *optimization*; here the starving mechanism is the retraining cobweb's own contraction, the cap is exact (`d_0' P d_0`, Lyapunov) and is governed by the performative modulus - so identifiability couples to the stability boundary, an inversion with no analog in either literature. | G2 |
| T2 (exchange rate) | Lai-Robbins (AoS'79/'82): `O(log n)` observation cost with efficient estimation; sqrt(T) regret lower bounds in pricing (Broder-Rusmevichientong OR'12) | Where the ancestors prove order-level tradeoffs, T2 is an exact pathwise *invariance*: the product is pinned at `(1/2) gamma_PO sigma^2` for every scheme; the Lai-Robbins schedules sit exactly on this frontier (P9.1) - their result is a point on our curve. | G3 |
| P2.2 (feedback bias, `(3m-1)` sign change) | Stambaugh bias (predictive regressions); Kendall AR bias | Same Wick-expansion machinery, new object: the retraining loop's noise-feedback channel, with a sign change at `m = 1/3` that neither literature contains because neither has a modulus. | G1/G3 |
| T3 (deviation-budget minimax) | van Trees / Gill-Levit (Bernoulli'95); sequential CR bounds | Standard machinery, new setting: the budget is the deployment deviation of a performative loop and the bound is met with equality by the D2 scheme - jointly they close the frontier from both sides. | G1 |
| L2 + T4 (exploitation-information; value-budget minimax) | Le Cam two-point bounds; information-directed sampling (regret-information ratios) | IDS-type ratios bound *regret* by information for an exogenous environment; L2 bounds *self-financing of the probe itself* by the information already purchased about one's own feedback, under the CE anchor - to our knowledge the first self-referential information bound in a decision-dependent system. | G1, G3 |
| T5a/b (A-/D-optimal shapes) | Classical optimal design (Kiefer-Wolfowitz; Pukelsheim); task-optimal system-ID design (Wagenmaker et al. ICML'21) | Classical design has exogenous budgets; task-optimal ID has exogenous plants; here the budget *is* the decision objective, yielding design shapes that are functions of the objective's curvature (`Gamma_PO^{-1/2}`, `Gamma_PO^{-1}`) - a design class that did not exist. | G4 |
| T5c (c-optimal along the correction) | Elfving (1952) geometry; c-optimal design theory | The functional is the performative correction itself and the value `c'Gamma_PO c/B` prices "knowing your correction" in the objective's own norm - the operational statement that a desk need not identify its whole Jacobian. | G4 |
| C5.1 + P9.2 (isotropy contrast) | Simchowitz-Foster (ICML'20): naive exploration optimal for online LQR | The performative setting reverses the slogan: naive (isotropic) exploration overpays by exactly the curvature dispersion `F`, generically `> 1` on the calibrated universe - a quotable, computable contrast. | G4 |
| L3 (temporal shaping) | Standard OLS information algebra | Stated because its *failure* under A3' (OPEN-4) marks the honest scope boundary; the lemma collapses the design space to static measures, which is what makes T5 complete. | - |
| T6 (Chebyshev unidentifiability) | Chebyshev systems / de la Garza phenomenon (1950s design theory) | Classical counting applied to a new question - what a retraining trajectory can never identify about its own response family - upgrading REFLEX's empirical "wide spread range" rule and its anti-echo freeze into a theorem. | G2 |
| L4 + P7.1 (perturbed modulus; safe pessimism) | Least-costly ID for control (Bombois et al., Automatica'06); safe exploration (SafeOpt line) | Bombois prices experiments against *plant* constraints; safe-BO keeps an exogenous system in a safe set; here the hazard is the estimate feeding back into the learner's own closed loop, and safety is inherited from an anytime-valid CS through an explicit Lipschitz translation - a constraint class none of the three literatures contains. | G4 |
| T7 (horizon-dependent crossover) | Plug-in performative optimization (Lin-Zrnic ICML'24) | Lin-Zrnic show misspecified structural models can help, with no cost side; T7 prices anchoring against the exploration budget *and* the horizon, giving the decision rule `delta < |tau'''| B/(3 gamma_PO T)` - and predicting when their qualitative message reverses. | G5 |
| T8 (ROI; break-even patience) | Rothschild (JET'74), McLennan, Easley-Kiefer, Aghion et al. (REStud'91): rational incomplete learning; optimal experimentation and patience | The economics established the mechanism qualitatively; because the market model computes every constant, the break-even patience is a closed form - `rho* = (h_SP-h_PO)^4/(4 kappa^2 sigma^2)`, curvature cancelling - i.e. the classical mechanism made operational. | G6 |
| P9.3 (multi-bond `Gamma_PO`) | Bergault-Gueant factor reduction; REFLEX 1.5 | Pure instantiation: extends REFLEX's curvature machinery to the performative objective so every d-dimensional constant in T5/C5.1 is computable at `O(d k^2)`. | - |

**Aggregate statement (for the introduction).** The four objects with no
prior-art row that survives inspection - the modulus-governed saturation
cap, the pathwise invariance identity with its two-sided minimax closure,
the self-referential exploitation bound, and the objective-priced
stability-constrained design class - are the paper's novelty claim; every
other row is standard machinery deployed in a new setting and is cited as
such. The claim language is "we introduce the framework and establish its
exact laws," never "we develop new mathematics."
