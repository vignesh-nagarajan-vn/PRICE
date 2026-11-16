# Numerical certificates

Every closed form in the paper ships a numerical certificate in the base
project's verification layer, which currently holds 66. This paper adds the
following. The count is deliberately small: one certificate per closed form,
plus one per anchor that could regress.

A certificate is a deterministic check with a stated tolerance that fails loudly.
It is not a unit test of the implementation; it is evidence that the closed form
is the thing the simulator does.

## Theorem 1

Proofs in [`../math/derivations/01-alignment-spectrum.md`](../math/derivations/01-alignment-spectrum.md)
and [`../math/derivations/02-supply-chain-concentration.md`](../math/derivations/02-supply-chain-concentration.md).

| # | Checks | Tolerance | State |
|---|---|---|---|
| C1 | `n_eff(1 1', kappa)` equals the base law `1 + kappa(N-1)`, `N` in `2..50` | machine | **run** |
| C2 | `n_eff_supply_chain` equals `n_eff(supply_chain_R(...))`, two routes to one number | machine | **run** |
| C3 | `n_eff(I, kappa) == 1`, so orthogonal responses are dynamically one firm | machine | **run** |
| C4 | **Simplex spectrum.** `lambda_max(R_simplex) == N/(N-1)`, and `m_1(1-kappa)` is in the Jacobian's spectrum but is not its radius. Also the ordering failure: simplex has lower mean alignment and higher `lambda_max` than orthogonality | machine | **run** |
| C5 | **Clustered counterexample.** `N_eff` from `lambda_max` exceeds `N_eff` from the mean-alignment index by 1.757 at `kappa = 0.8` | `1e-12` | **run** |
| C6 | **Concentration.** `r_ij -> s` as `d` grows, with the residual scaling as `O(1/d)` | fitted exponent within `0.15` of `-1` | **run**, measured `-1.018` |
| C7 | Heterogeneous-modulus bounds hold: `max_i m_i <= rho(J) <= max_i m_i * N_eff`, on random draws, exact in the three stated limits | machine at limits | **run**, 300 draws |
| C22 | **Reduction lemma.** The retraining map built from actual response Jacobians, without constructing `R`, has Jacobian `-m_1[(1-kappa)I + kappa R]` | `1e-12` | **run**, `5.6e-17` |
| C23 | **Spectral range.** `1 <= lambda_max(R) <= N` on random alignment matrices, so `N_eff >= 1` and `rho(J) >= m_1` | `1e-10` | **run** |
| C24 | **The mean is a lower bound.** `N_eff >= 1 + kappa(N-1)*mean` on random `R`, with equality exactly on constant-row-sum `R` | `1e-10` | **run**, 360 draws, zero violations |

C22 is the load-bearing one for Theorem 1. Everything else in the theorem follows
from the Jacobian, and until C22 the Jacobian was asserted rather than derived.

C4 exists because the plan of record stated that anchor incorrectly; the plan has
since been corrected, so C4 is now a regression guard against reverting to the
wrong version rather than a live disagreement.

C1 to C5 are implemented in
[`certificates/verify_theorem1_anchors.py`](certificates/verify_theorem1_anchors.py).
C1 to C7 and C22 to C24 are implemented in
[`certificates/verify_theorem1_proof.py`](certificates/verify_theorem1_proof.py),
123 checks, assertion-based, all passing. The simplex is checked two independent
ways, analytically from `R_simplex` and constructively from actual unit response
vectors summing to zero; the constructive path is the load-bearing one, since it
rules out the result being an artifact of how the matrix was written down.

`verify_theorem1_anchors.py` was converted from a report-printing script to an
assertion-based certificate on 18 Aug 2026, against `verify_theorem1_proof.py`
as the template. It keeps its printed tables, since the section (D) and (F)
numbers are quoted in the math notes and a reader checking a quote wants to see
them, and it now carries 60 assertions on the checks it was already computing.
The load-bearing additions are in section (C): `m_1(1-kappa)` is asserted to be
in the spectrum and asserted **not** to be the radius, so the plan of record's
original error cannot silently return.

**Outstanding:** folding the certificates into the base project's verification
layer. [TO BUILD]

## Theorem 2

Proof in [`../math/derivations/03-cadence-composition.md`](../math/derivations/03-cadence-composition.md).

| # | Checks | Tolerance | State |
|---|---|---|---|
| C8 | `is_stable_lazy(m_N, c, K)` agrees with `K < k_max(m_N, c)` on every integer `K` in `1..200` across an `(m_N, c)` grid | exact, boolean | **run**, 51600 cases |
| C9 | `k_max` is decreasing in `m_N`, and in `s` through `m_N` | exact, monotone | **run** |
| C10 | No integer `K >= 1` is stable once `m_N > (1+c)/(1-c)`, and `K = 1` is stable just below it | exact, boolean | **run**, sharp at five `c` |
| C11 | The worked table reproduces: `K_max` of `20.68 / 5.28 / 2.53` at `s = 0.25 / 0.5 / 1` with `m_1 = 0.15`, `kappa = 0.8`, `N = 30`, `c = 0.8` | `1e-2` | **run** |
| C12 | `c` is invariant to `N`, so the inner contraction is genuinely own-objective curvature | `1e-10` | **run**, spread `4.4e-16` |
| C25 | **The joint map, measured.** Running actual inner gradient descent on each basis vector reproduces `c^K I + (1-c^K) J`, and `mu_N(K)` is its extreme eigenvalue | `1e-12` | **run** |
| C26 | **Dynamic frontier.** Iterating the real joint map to convergence or divergence agrees with the predicted side of the frontier | exact, boolean | **run**, 59 decisive trials, zero disagreements |

C12 is the one that catches a broken composition, and it is the certificate the
open item in the math note asked for. It is measured from gradient descent inside
the joint market rather than asserted from the formula.

C26 is the one that would catch a frontier that is algebraically right and
dynamically wrong, which no amount of algebra checking can rule out.

All seven are implemented in
[`certificates/verify_theorem2_cadence.py`](certificates/verify_theorem2_cadence.py),
59 checks, assertion-based, all passing.

**Recorded from C8.** At `m_N = 1` exactly the stability margin is `2c^K`, positive
for every finite `K` but below double precision past `K = 171` at `c = 0.8`. That
is a floating-point limit, not a statement about the market, and the certificate
says so where a later reader would otherwise misread it.

## Theorem 3

Proof in [`../math/derivations/04-mixed-market-secular.md`](../math/derivations/04-mixed-market-secular.md).

| # | Checks | Tolerance | State |
|---|---|---|---|
| C13 | Limit case: `mixed_market_radius` with `gamma_ratio -> 0` converges to the blind-block radius | `1e-8` | **run** |
| C14 | The stability criterion predicts the sign change on 4000 random draws against dense eigensolves | exact, boolean | **run**, see below |
| C15 | Herd-immunity collapse: at `kappa = s = 1`, `rho_star == 1 - 1/m_N` | machine | **run** |
| C16 | `rho_star` is increasing in `s`, which is what makes diversity and correction substitutes | exact, monotone | **run**, strict where positive |
| C17 | The worked thresholds reproduce: `0.596 / 0.242 / 0` at `s = 1 / 0.5 / 0.2` with `N = 20`, `m_1 = 0.15`, `kappa = 0.8` | `1e-3` | **run** |
| C18 | The strong-correction limit is approached from the stable side, so the limit theorem is conservative | sign check | **run, and it FAILED** |
| C27 | **Exact two-block root** against dense eigensolves, all block splits | `1e-10` | **run**, `2.5e-14` on 6000 draws |
| C28 | **Degenerate blocks.** An empty block needs the single-block form; the quadratic otherwise leaves a phantom root that exceeds the true radius | `1e-12` | **run** |
| C29 | **Integer threshold.** Minimum corrected firms is `N - ceil(N_c) + 1`, and `ceil(rho* N)` is off by one at exact-integer `N_c` | exact | **run**, 3000 draws |
| C30 | **Imperfect correction.** At `kappa = s = 1` the exact threshold is `(1 - 1/m_N)/(1 - gamma_ratio)` | `1e-14` | **run**, `1.8e-15` |
| C31 | **Critical efficacy.** The threshold passes 1 exactly at `gamma_ratio = 1/m_N`, and all-corrected is unstable above it | `1e-12` | **run** |

**C18 failed, and the failure is the most consequential result of the build.**
The radius is nondecreasing in `gamma_ratio`, by Perron-Frobenius on an
entrywise-nonnegative matrix, so the limit under-states it. The limit theorem is
**optimistic**, not conservative: on the ensemble of `verify_ensemble_intervals.py`
it calls `11.8%` (2157 of 18313 draws, exact 95% interval `[11.3, 12.3]%`) of
configurations stable that are unstable at finite correction. The plan of record
anticipated this possibility and required the error direction be stated, which the
paper now does. The exact two-block root has left the de-scope order as a result.

**C14 needed restating.** The note claims `rho*` predicts the sign change with
zero mismatches on 4000 draws. The primitive condition `N_b < N_c(s)` does, and
the clamped comparison `rho > rho*` does not: it mispredicts the all-blind market
that is stable without any correction, on `134` of the same draws. The certificate
now checks all three candidate forms and records which are exact.

C30 and C31 are the results that replaced the clean law. They are stronger than
what they replaced, since the imperfect-vaccine correspondence means the
epidemiological analogy transfers a refinement of the law and not merely the law.

All eleven are implemented in
[`certificates/verify_theorem3_herd_immunity.py`](certificates/verify_theorem3_herd_immunity.py),
70 checks, assertion-based, all passing.

## Theorem 4

Welfare page in [`../math/04-theorem4-wedge.md`](../math/04-theorem4-wedge.md).

| # | Checks | Tolerance | State |
|---|---|---|---|
| C19 | **The AR(1) reduction, simulated.** `z_{t+1} = -m_N z_t + xi_t` run to stationarity has variance `sigma^2/(1 - m_N^2)`, and lag-1 autocorrelation `-m_N`, so the sign convention is measured rather than asserted | `2e-2` on 400k-step paths, `1e-9` on the algebra | **run** |
| C20 | `t*` is strictly increasing in `N`, in `kappa`, in `s` and in `m_N`, and the divergence rate at the boundary is `(1 - m_N)^-2` | exact monotone; fitted exponent within `1e-3` of `-2` | **run**, measured `-2.000000` |
| C21 | **Over-adaptation.** The decentralized symmetric equilibrium exceeds the social optimum on every configuration of a grid in `N`, `kappa`, `s` and client exposure, the gap widens with `N`, and the wedge is exactly zero at `N = 1` with no client exposure | exact, sign | **run**, 108 configurations, smallest relative gap `0.290` |
| C34 | **Lemma 11, the marginal crowding share.** `d m_N/d m_i = N_eff * v_i^2` by finite differences on random alignment matrices, summing to `N_eff`; equal to `N_eff/N` on exchangeable `R` | `1e-5` | **run** |

C34 is the load-bearing one, and it is the reason Theorem 4 is a derivation
rather than an assertion. Everything else in the theorem is arithmetic on top of
the marginal crowding share, and a plausible-looking `1/N` there would have been
wrong by the factor `N_eff`, which at `N = 20`, `kappa = 0.8`, `s = 1` is
`16.2`. The certificate checks the naive guess is wrong by exactly that factor.

C19 is simulated rather than algebraic on purpose. The algebra
`V = m_N^2 V + sigma^2` is one line and could not fail; what could fail is the
sign convention, and the lag-1 autocorrelation is where a sign error would show.
It is negative, so a crowded market's common mode oscillates rather than
persists, which is what Section 8's estimator has to look for.

All four are implemented in
[`certificates/verify_theorem4_wedge.py`](certificates/verify_theorem4_wedge.py),
125 checks, assertion-based, all passing.

**`pigouvian_wedge` joined the module on 19 Aug 2026**, when panel 6 was built.
It was held out while the panel did not exist, since the module is the surface a
panel imports from and the standing rule is that nothing reaches the paper ahead
of its derivation. `verify_theory_module.py` no longer asserts its absence; the
assertion is replaced by section A9, which re-derives the wedge longhand on 72
configurations, checks the `(N-1)/N` reading and its vanishing at `N = 1`,
checks Lemma 11's shares sum to `N_eff` rather than to one, and checks the
provenance channel outgrows the aggressiveness channel. That file now carries 56
checks rather than 50.

**Panel 6 carries no separate certificate, by decision.** Its closed forms are
already certified by C19 to C21 and C34, and its own agreement gate lives in
`run_panels.py`, which exits nonzero if any row contradicts Corollary 4.2, if
the fee fails to implement the social optimum, or if the measured `m_N` departs
from the closed form. A certificate here would restate C21 against the same
algebra.

## Infrastructure certificates

Not closed forms, but the same rule applies: the code every panel depends on is
certified before a panel runs.

| # | Checks | State |
|---|---|---|
| C32 | **Theory module acceptance.** The six tests the spec names, plus guards and the A9 wedge tests, each re-deriving its expectation against a dense eigensolve or brute force rather than importing the module's own answer | **run**, 56 checks |
| C33 | **Environment reduction.** At `R = 1 1'` the heterogeneous-response environment reproduces the base project's homogeneous market in alignment, `N_eff` and Jacobian, and the built Jacobian equals the closed form on arbitrary topologies | **run**, 32 checks |

C33 is the acceptance test the experiment specs name, and it runs before any
measurement is taken from the environment.

**The simulator port carries no certificate, by decision.** Its one acceptance
test, bit-for-bit reproduction of the unmodified base at flat profiles, passes at
relative error `0.00e+00` for `N` in `1..6` and is recorded in
[`environment/HETERO-SIMULATOR-PORT-DESIGN.md`](environment/HETERO-SIMULATOR-PORT-DESIGN.md).
Its step-3 gate failed and the workstream was closed on 19 Aug 2026 without
either named repair, so no panel imports the port and no claim rests on it. A
certificate here would guard code that nothing in the paper depends on.

## Running total

34 new certificates against the base project's 66, for 100. Every one of them is
deterministic, CPU-only, numpy-only apart from `scipy.stats` in
`verify_ensemble_intervals.py`, and runs from `(config, seed)`.

All 34 are written and passing, spread across **542 individual assertions in
eight files**. Theorem 4's four (C19 to C21 and C34) joined on 18 Aug 2026 when
the welfare page landed, and the ensemble-interval file on 27 Aug 2026.

```bash
for f in herd-immunity/ml-contributions/certificates/verify_*.py; do python "$f" || break; done
```

| File | Assertions |
|---|---|
| `verify_theorem1_proof.py` | 123 |
| `verify_theorem2_cadence.py` | 59 |
| `verify_theorem3_herd_immunity.py` | 70 |
| `verify_theory_module.py` | 56 |
| `verify_hetero_env.py` | 32 |
| `verify_theorem1_anchors.py` | 60 |
| `verify_theorem4_wedge.py` | 125 |
| `verify_ensemble_intervals.py` | 17 |

542 assertions across eight files, all passing. The anchors file joined the count
on 18 Aug 2026 when it was converted to assert rather than print, and the
Theorem 4 file the same day when the welfare page landed. The theory module
gained six on 19 Aug 2026 when the wedge replaced the absence assertion.

**Re-run 27 Aug 2026 as the pre-freeze check.** All eight files exit zero, the
per-file counts above are reproduced exactly, and the total is 542.

`verify_ensemble_intervals.py` is the newest and the only one that is
inferential rather than deterministic. It exists because the paper quotes one
fraction estimated on a random ensemble, and a fraction without its sampling
measure, its n and an interval is not a certified number. It records the
protocol, computes the exact Clopper-Pearson interval on the count C18 first
measured, and reproduces the estimate on five independent ensembles. The
direction of the error stays a theorem and is not restated as a statistic.

## Rule

A closed form that reaches the paper without a passing certificate is stated at
`[DERIVED]`, never at `[VERIFIED]`. The claims ledger in `../../archive/herd-immunity-v1/writing/` is the
enforcement point, and the status flag in the paper must match the ledger entry,
which must match this table.
