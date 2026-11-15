# ML x OR - Mathematical Derivations”

This repo contains the derivations of the mathematical foundations for the
ML x OR @ NeurIPS 2026 paper *"The Price of Self-Knowledge: Minimax
Information-Cost Tradeoffs and Optimal Exploration in Performative
Systems"* - the theory that a system whose deployment reshapes its own
training distribution must *purchase* knowledge of that feedback with the
objective itself, at an exact exchange rate, under a stability constraint.

Every checkable claim is verified numerically: **34/34 checks pass**
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
|- VERIFICATION.md            <- the verification record: 34 checks, 3 falsifications, tolerances
|- NOVELTY-CROSSWALK.md       <- theorem -> nearest prior art -> paste-ready delta sentence
|                                (rows keyed to the literature review's gaps G1-G6)
|- OPEN-PROBLEMS.md           <- the labeled-open register (OPEN-1..4): precise targets, what
|                                is proved today, strategies, risk - the journal delta
|- SYMBOLS-TO-REFLEX.md       <- every constant mapped to where the reflex package computes it
|                                (EXISTS rows name-checked against the source by check_docs.py)
|- requirements.txt           <- numpy pin
|- .github/workflows/verify.yml  <- CI: runs both suites on every push (living certificate)
|- latex/
|  |- theorems.tex            <- LaTeX twins of all statements (compiles standalone; the
|                                marked body block drops into the NeurIPS build; macros fixed)
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
   |- last_run.log            <- the 34/34 numerical run the record refers to
```

## Result map (derivation -> paper)

| Paper object | Derivation | Status |
|---|---|---|
| Theorem 1 (saturation) + Cor. 1.1/1.2 | D1 | proved + verified |
| Theorem 2 (exchange rate, pathwise) | D0 + D2 | proved + verified |
| Theorem 3a (minimax, deviation budget) | D3 sec. 2 | proved + verified (tightness shown) |
| Theorem 3b (minimax, value budget) | D3 sec. 3 | proved for the two-point family; full generality = journal item |
| Theorem 4 (design trio + dispersion factor) | D4 | proved + verified |
| Theorem 5 (safe design) | D6 | structure + safety proved; regret bound = labeled open |
| Theorem 6 (anchoring crossover) | D7 | proved + verified |
| Corollary (ROI) | D8 | proved + verified |
| Chebyshev unidentifiability | D5 | proved + verified |
| Feedback-bias scope condition | D2 sec. 4 | proved + verified (incl. sign change) |
| REFLEX instantiation (`Gamma_PO`, constants) | D8/D9 | separable case exact + verified; coupled case first-order |

## Reproduce

```
pip install -r requirements.txt
python verify/verify_all.py     # numerical suite: ~4 min CPU, deterministic, exit 0 iff 34/34
python verify/check_docs.py     # document consistency: register IDs, symbol map (pass
                                # --reflex-root <path-to-endo_market_v4> to name-check the
                                # EXISTS rows against the source), LaTeX, YAML, file graph
```

The CI workflow runs both suites on every push, so the 34/34 record and the
document cross-references are a living certificate, not a one-time log.

## Conventions

Mathematics in fenced ASCII blocks (repo convention; renders identically
everywhere); notation follows REFLEX theory 1.1-1.6 (`gamma`, `beta`,
`epsilon`, `psi`, `h_SP`, `h_PO`, `m = eps beta/gamma`); every falsified
draft claim is kept visible in its document with the correction - the
falsification record is part of the method, not an embarrassment. The two
labeled-open items (D3b full generality, D6 regret) are exactly the
workshop-to-journal delta the ML x OR pipeline expects.
