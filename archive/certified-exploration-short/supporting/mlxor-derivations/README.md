# Mathematical Derivations - PRICE

Complete, from-scratch derivations of the mathematical foundations for the
ML x OR @ NeurIPS 2026 paper *"PRICE: Minimax
Estimation-Regret Tradeoffs and Certified Exploration in Performative
Prediction"* - the theory that a system whose deployment reshapes its own
training distribution must *purchase* knowledge of that feedback with the
objective itself, at an exact exchange rate, under a stability constraint.

Every checkable claim is verified numerically: **38/38 checks pass**
(`VERIFICATION.md`, `verify/last_run.log`). The verification process
falsified three claims as first drafted; each fix is recorded in place and
each produced a sharper result than the original.

## Layout

```
mlxor-derivations/
|- README.md                  <- this file
|- THEOREMS.md                <- the results-section skeleton: every result numbered, with
|                                assumptions, derivation source, verification IDs, status,
|                                the dependency spine, and the 4-page-cut mapping
|- VERIFICATION.md            <- the verification record: 38 checks, 3 falsifications, tolerances
|- NOVELTY-CROSSWALK.md       <- theorem -> nearest prior art -> paste-ready delta sentence
|                                (rows keyed to the literature review's gaps G1-G6)
|- OPEN-PROBLEMS.md           <- the labeled-open register (OPEN-1..5): precise targets, what
|                                is proved today, strategies, risk - the journal delta
|- SYMBOLS-TO-REFLEX.md       <- every constant mapped to where the reflex package computes it
|                                (EXISTS rows name-checked against the source by check_docs.py)
|- requirements.txt           <- numpy pin
|- .github/workflows/verify.yml  <- CI: runs both suites on every push (living certificate)
|- latex/
|  |- macros.sty              <- the shared macro single-source (theorems, proofs, and the
|  |                             NeurIPS main.tex all \usepackage it - notation cannot drift)
|  |- theorems.tex            <- LaTeX twins of all statements (compiles standalone; the
|  |                             marked body block drops into the NeurIPS build)
|  |- proofs.tex              <- THE APPENDIX: complete proofs of all 26 register entries,
|  |                             each tagged [ID] and cross-referenced to its verification
|  |                             checks; the T4 proof states exactly what is proved (the
|  |                             gamma_PO sigma^2/27 constant-factor version) with the sharp
|  |                             constant marked as OPEN-1; falsification remarks kept inline
|- derivations/
|  |- 00-notation-and-assumptions.md    canonical symbol table + assumption register A1-A6
|                                       + the two anchoring conventions (authoritative)
|  |- 01-model-and-cost-lemma.md        D0: the loop model, deviation vs value budgets,
|  |                                        the cost-equivalence lemma + exact variance
|  |                                        decomposition, the certainty-equivalent anchor
|  |- 02-saturation-lyapunov.md         D1: information saturation - exact d-dimensional
|  |                                        energy via the discrete Lyapunov equation,
|  |                                        "safety implies blindness", non-normal
|  |                                        transient information
|  |- 03-exchange-rate.md               D2: the pathwise exchange-rate identity
|  |                                        Var x Cost = (1/2) gamma_PO sigma^2, its
|  |                                        concentration, and the full Stambaugh feedback
|  |                                        bias with the m = 1/3 sign change
|  |- 04-minimax-lower-bounds.md        D3: van Trees over adaptive designs (exact,
|  |                                        deviation budget) + the exploitation-information
|  |                                        lemma (value budget, Pinsker/Le Cam), with the
|  |                                        1 - O(T^{-1/2}) minimax product bound
|  |- 05-design-geometry.md             D4/D5: the optimal-exploration trio
|  |                                        (A-opt ~ Gamma^{-1/2}, D-opt ~ Gamma^{-1},
|  |                                        c-opt along the correction direction), the
|  |                                        curvature-dispersion price of isotropic jitter,
|  |                                        the temporal-shaping lemma, and the Chebyshev
|  |                                        counting theorem (trajectories never identify
|  |                                        curvature)
|  |- 06-safe-certainty-equivalence.md  D6: where the stability constraint actually bites
|  |                                        (estimate feedback, not open-loop probing), the
|  |                                        perturbed-modulus lemma, the pessimism rule and
|  |                                        the safety proposition; O(sqrt(T)) design regret
|  |                                        stated as the labeled-open journal item
|  |- 07-anchoring-crossover.md         D7: the anchoring-vs-misspecification crossover,
|  |                                        horizon-dependent (anchor iff
|  |                                        delta < |tau'''| B / (3 gamma_PO T)), with the
|  |                                        exact secant-bias constant tau'''/6 w^2
|  |- 08-roi-and-instantiation.md       D8/D9: the ROI of self-knowledge
|  |                                        (v* = (sigma/kappa) sqrt(rho); break-even
|  |                                        patience rho* = (h_SP - h_PO)^4/(4 kappa^2
|  |                                        sigma^2) - gamma cancels), the two consistency
|  |                                        lemmas (Lai-Robbins on the frontier; the
|  |                                        isotropy contrast), and the multi-bond Gamma_PO
|- verify/
   |- verify_all.py           <- the numerical suite (numpy only, deterministic, ASCII output)
   |- check_docs.py           <- document-consistency suite: register IDs vs the log, symbol
   |                             map vs the reflex source, LaTeX structure, workflow YAML,
   |                             file graph + assumption completeness (stdlib only)
   |- last_run.log            <- the 38/38 numerical run the record refers to
```

## Result map (derivation -> paper)

| Paper object (as compiled) | Derivation | Status |
|---|---|---|
| Body Theorem 1 = T2 (exchange rate) | D0 + D2 | proved + verified |
| Body Theorem 2 = T3/T4 (minimax floors) | D3 sec. 2-3 | T3 proved + verified (tight); T4 constant-factor proved, sharp 1/2 = OPEN-1 |
| Body Theorem 3 = T9 (structure-proofness, exact reach) | D3 sec. 5 | proved + verified (V9.1-V9.4); witness frozen |
| In-text: saturation T1 + C1.1/C1.2, R1 | D1 | proved + verified |
| In-text: design trio T5 + C5.1, L3 | D4 | proved + verified |
| In-text: Chebyshev T6 | D5 | proved + verified |
| In-text: safe design L4, R2, P7.1 | D6 | structure + safety proved; regret bound = labeled open |
| In-text: anchoring crossover T7 | D7 | proved + verified |
| In-text: ROI T8, frontier P9.1, isotropy P9.2 | D8 | proved + verified |
| Feedback-bias scope condition P2.2 | D2 sec. 4 | proved + verified (incl. sign change) |
| REFLEX instantiation (`Gamma_PO`, constants) P9.3 | D8/D9 | separable case exact + verified; coupled case first-order |

## Reproduce

```
pip install -r requirements.txt
python verify/verify_all.py     # numerical suite: ~4 min CPU, deterministic, exit 0 iff 38/38
python verify/check_docs.py     # document consistency: register IDs, symbol map (pass
                                # --reflex-root <path-to-endo_market_v4> to name-check the
                                # EXISTS rows against the source), LaTeX, YAML, file graph
```

The CI workflow runs both suites on every push, so the 38/38 record and the
document cross-references are a living certificate, not a one-time log.

## Conventions

Mathematics in fenced ASCII blocks (repo convention; renders identically
everywhere); notation follows REFLEX theory 1.1-1.6 (`gamma`, `beta`,
`epsilon`, `psi`, `h_SP`, `h_PO`, `m = eps beta/gamma`); every falsified
draft claim is kept visible in its document with the correction - the
falsification record is part of the method, not an embarrassment. The two
labeled-open items (D3b full generality, D6 regret) are exactly the
workshop-to-journal delta the ML x OR pipeline expects.
