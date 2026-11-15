# Claims ledger

Every numbered claim the paper makes, its status flag, and its evidence. **The
flag in the paper must match the flag here, which must match the certificate
table in `../ml-contributions/CERTIFICATES.md`.** Nothing ships at a status
stronger than its ledger entry.

Reviewed as a pass of its own before freeze, against the built PDF rather than
the source, because a status flag that drifted during writing is invisible in a
diff. Last reconciled against `paper/main.pdf` on 20 Aug 2026: one `[MEASURED]`
row and six `[DRY RUN]` rows in Table 2 of the body, matching E1 and E2 through
E6 here, and 542 certificate assertions passing.

**Proofs.** As of 20 Aug 2026 every numbered result in the body is proved in the
submission PDF's own appendix rather than promised to supplementary material, and
Appendix H carries the certificate inventory this file is the authority for.

**Numbering.** This file's section headings are the markdown drafts in this
folder. The built paper folds supervision into the closing section, so it runs
nine sections, and the four results are Theorem 2, 4, 5 and 8 there against
Theorem 1 to 4 here. Where this file says Section 9 or 10, the paper says
Section 8 or 9. Flags are unaffected.

## Status flags

- `[VERIFIED]` follows from certified base results, or checked numerically
- `[DERIVED]` worked out for this paper, derivation recorded, low proof risk
- `[TO BUILD]` new experiment or configuration, not yet run
- `[DEFERRED]` stated in the body, completed for the journal version
- `[DRY RUN]` run in the linearized reference environment, which has no
  microstructure. Establishes that the closed forms govern the realized
  dynamics. **Does not license the paper to imply measurement**
- `[MEASURED]` run in the order-flow simulator. This is the only status that
  lets the paper say a thing was measured in a market

---

## Section 3, background

| # | Claim | Status | Evidence |
|---|---|---|---|
| 3.1 | Symmetric multi-dealer law, common mode at `-m_1 N_eff` | `[VERIFIED]` | base result, REFLEX |
| 3.2 | Measured amplification `1.74x` at `N=2`, `3.16x` at `N=3` | `[VERIFIED]` | base result; replicated in panel 1 |
| 3.3 | The externality is technological, not pecuniary | argument | Buchanan and Stubblebine, 1962 |

## Section 4, Theorem 1

Proofs in [`../math/derivations/01-alignment-spectrum.md`](../math/derivations/01-alignment-spectrum.md)
and [`../math/derivations/02-supply-chain-concentration.md`](../math/derivations/02-supply-chain-concentration.md).

| # | Claim | Status | Evidence |
|---|---|---|---|
| 4.0 | **Reduction:** `J = -m_1[(1-kappa)I + kappa R]` follows from the response Jacobians under (H1) to (H4) | `[VERIFIED]` | `derivations/01` Lemma 1; C22, agreement `5.6e-17` |
| 4.1 | `m_N = m_1 (1 + kappa(lambda_max(R) - 1))` for equal moduli | `[VERIFIED]` | `derivations/01` Thm 1; C1, C2, C3, C23. 384 configurations |
| 4.2 | Monoculture corner recovers the base law | `[VERIFIED]` | C1 |
| 4.3 | Orthogonal responses give `m_N = m_1` | `[VERIFIED]` | C3 |
| 4.4 | Simplex spectrum contains `m_1(1-kappa)`; radius is `m_1(1+kappa/(N-1))` | `[VERIFIED]` | C4, run. **Plan of record corrected to match** |
| 4.5 | The binding mode is the common one iff `R` has nonnegative entries | `[DERIVED]` | Perron-Frobenius; `derivations/01` Prop 2; C22 |
| 4.6 | Supply chain: `N_eff = 1 + kappa*s*(N-1)` | `[VERIFIED]` | `derivations/02`; C2, C6 |
| 4.7 | `r_ij -> s` with `O(1/d)` fluctuation, **as a probability bound** | `[VERIFIED]` | `derivations/02` Lemma 5 and Prop 6; C6, fitted exponent `-1.018`. **Open item closed** |
| 4.8 | Clustered counterexample: `N_eff` 2.60 against 1.48 by the mean index | `[VERIFIED]` | C5, run. Factor 1.757 |
| 4.9 | Mean alignment does not order configurations correctly | `[VERIFIED]` | C4, run. Simplex against orthogonal at `N` in {5,10,30} |
| 4.10 | Heterogeneous moduli: `max_i m_i <= rho(J) <= max_i m_i * N_eff` | `[VERIFIED]` | `derivations/01` Prop 4; C7, 300 draws, exact in three limits |
| 4.11 | Share-weighted alignment, fully heterogeneous reduction | `[DEFERRED]` | named, not attempted |
| 4.12 | **`N_eff >= 1`, so `rho(J) >= m_1`:** interaction never stabilizes a market below what its members achieve alone | `[VERIFIED]` | `derivations/01` Cor 1.2; C23. Notation table corrected |
| 4.13 | **The mean index errs with a sign:** `N_eff >= 1 + kappa(N-1)*mean` for every `R`, so it under-states risk and never over-states it | `[VERIFIED]` | `derivations/01` Prop 3; C24, 360 draws, zero violations |
| 4.14 | The sharp operator-norm concentration rate `sqrt(N)/d` | `[DEFERRED]` | crude `N/d` bound proved; sharp rate measured, not proved |

## Section 5, Theorem 2

Proof in [`../math/derivations/03-cadence-composition.md`](../math/derivations/03-cadence-composition.md).

| # | Claim | Status | Evidence |
|---|---|---|---|
| 5.0 | **Inner loop:** `K` gradient steps contract to the frozen best response by `c^K`, `c = 1 - eta*gamma` | `[VERIFIED]` | `derivations/03` Lemma 7; measured from actual GD |
| 5.1 | `mu_N(K) = -m_N + c^K(1+m_N)`, from `M_K = c^K I + (1-c^K)J` | `[VERIFIED]` | `derivations/03` Thm 2; C12, C25 |
| 5.2 | `K_max = ln((m_N-1)/(m_N+1))/ln c`, decreasing in `m_N` and in `s` | `[VERIFIED]` | C8 (51600 cases), C9 |
| 5.3 | Critical crowding at `m_N = (1+c)/(1-c)`, factor 9 at `c = 0.8` | `[VERIFIED]` | `derivations/03` Cor 10.3; C10, sharp at five `c` |
| 5.4 | Worked window: `20.68 / 5.28 / 2.53` at `s = 0.25 / 0.5 / 1`, at `c = 0.8` | `[VERIFIED]` | C11 |
| 5.5 | `c` is invariant to `N` | `[VERIFIED]` | C12, spread `4.4e-16`. **The one place the composition could fail** |
| 5.6 | **The upper side of `\|mu_N\| < 1` never binds, and the lower binds at `lambda_max`,** by monotonicity rather than by sign pattern | `[VERIFIED]` | `derivations/03` Prop 9; C25 |
| 5.7 | Equivalent form: stable iff `m_N < (1+c^K)/(1-c^K)`, of which critical crowding is the `K = 1` case | `[VERIFIED]` | `derivations/03` Thm 10; C8 |
| 5.8 | Realized window is `floor(K_max)`, the plotted frontier continuous | `[VERIFIED]` | C8 |
| 5.9 | The simulated joint loop lands on the predicted side of the frontier | `[VERIFIED]` | C26, 59 decisive trials, zero disagreements |
| 5.10 | Heterogeneous `K_i` across firms | `[DEFERRED]` | breaks the eigenvector sharing the proof uses |

## Section 6, Theorem 3

Proof in [`../math/derivations/04-mixed-market-secular.md`](../math/derivations/04-mixed-market-secular.md),
which supersedes `../math/03` where they disagree.

| # | Claim | Status | Evidence |
|---|---|---|---|
| 6.0 | **Exact radius from the two-block quadratic**, with the single-block branch for empty blocks | `[VERIFIED]` | `derivations/04`; H1, `2.5e-14` on 6000 draws; H2 |
| 6.1 | Strong-correction limit: stability iff the blind block is stable | `[VERIFIED]` | now a corollary of 6.0; H3, C13 |
| 6.2 | Stability iff `N_b < N_c(s)` | `[VERIFIED]` | C14, 4000 draws, zero mismatches |
| 6.2a | The clamped `rho > rho*` is **not** an exact restatement of 6.2 | `[VERIFIED]` | C14, 134 mismatches, all the all-blind stable market. **Note corrected** |
| 6.3 | Collapse to `rho* = 1 - 1/m_N` at `kappa = s = 1` | `[VERIFIED]` | C15 |
| 6.4 | The `R_0` correspondence is structural, both being spectral radii | argument, now supported by 6.10 | Diekmann et al., 1990 |
| 6.5 | `rho*` increasing in `s`, so diversity and correction are substitutes | `[VERIFIED]` | C16, strict where `rho* > 0` |
| 6.6 | Worked thresholds: `0.596 / 0.242 / 0` at `s = 1 / 0.5 / 0.2` | `[VERIFIED]` | C17 |
| 6.7 | Exact two-block secular root | `[VERIFIED]` | 6.0. **Removed from the de-scope order, see 6.8** |
| 6.8 | **The limit is approached from the UNSTABLE side: it is optimistic, not conservative** | `[VERIFIED]` | C18, zero monotonicity violations on 3000 draws; `11.8%` of draws flip verdict, 2157 of 18313, exact 95% interval `[11.3, 12.3]%` with its sampling measure in `verify_ensemble_intervals.py` and Appendix K. **The plan's hoped-for direction is false** |
| 6.9 | Correction is a public good, under-supplied in equilibrium | argument | Bergstrom, Blume and Varian, 1986 |
| 6.10 | **Imperfect correction: `rho*(e) = (1 - 1/m_N)/e` at `kappa = s = 1`, with efficacy `e = 1 - gamma/gamma_PO`** | `[VERIFIED]` | `derivations/04` Thm 3'; H5, `1.8e-15`. The epidemiological imperfect-vaccine law |
| 6.11 | **Critical efficacy: no corrected fraction stabilizes unless `gamma_PO/gamma > m_N`** | `[VERIFIED]` | H6. Structural parallel of 5.3 |
| 6.12 | Realized threshold is `N - ceil(N_c) + 1` firms, not `ceil(rho* N)` | `[VERIFIED]` | H4, exact on 3000 draws; the two differ at exact-integer `N_c` |
| 6.13 | Correction never backfires: the radius is monotone in `gamma/gamma_PO` | `[VERIFIED]` | C18, Perron-Frobenius |
| 6.14 | Three or more correction levels; correction that moves `R` | `[DEFERRED]` | named, not attempted |

## Section 7, Theorem 4

Welfare page in [`../math/04-theorem4-wedge.md`](../math/04-theorem4-wedge.md),
complete as of 18 Aug 2026.

| # | Claim | Status | Evidence |
|---|---|---|---|
| 7.0 | **Marginal crowding share:** `d m_N/d m_i = N_eff * v_i^2`, hence `N_eff/N` on exchangeable `R`, and the shares sum to `N_eff` rather than to `1` | `[VERIFIED]` | `../math/04` Lemma 11; C34, finite differences to `1e-5` |
| 7.1 | Stationary variance is `sigma^2/(1-m_N^2)`, and the lag-1 autocorrelation is `-m_N`, so it is **negative** | `[VERIFIED]` | `../math/04` Section 1; C19, simulated to `2e-2` on 400k-step paths |
| 7.2 | Private FOC ignores `(N-1)/N` of marginal cost, plus client exposure | `[VERIFIED]` | `../math/04` Thm 4; C34 for the share, C19 and the fee identity for the rest |
| 7.3 | Wedge increasing in `N`, `kappa`, `s`, and proximity to boundary, diverging like `(1-m_N)^-2` | `[VERIFIED]` | `../math/04` Cor 4.1; C20, fitted exponent `-2.000000` |
| 7.4 | Over-adaptation for every `N >= 2`, strict even with no client exposure | `[VERIFIED]` | `../math/04` Cor 4.2; C21, 108 configurations, smallest relative gap `0.290` |
| 7.5 | Provenance channel `dm_N/ds = m_1 kappa (N-1)`, linear in `N` and non-decaying, unlike the aggressiveness channel which tends to `kappa` | `[VERIFIED]` | `../math/04` Prop 12; C34's companion checks |
| 7.6 | `W > sum_i w_i` (client exposure) | assumption, (W4) | Stated with one sentence of justification. The results use its **sign** and never its size |

## Section 8, supervision

| # | Claim | Status | Evidence |
|---|---|---|---|
| 8.1 | PC1 lag-1 autocorrelation tends to one as `m_N -> 1` | `[DEFERRED]` | estimator not yet formal |
| 8.2 | Variance share grows like `1/(1-m_N)` | `[DEFERRED]` | |
| 8.3 | Real-data panel is consistency evidence, not identification | stated as such | placebo required |

## Experiments

**A dry run is not a measurement.** Panels 1 to 5 have run in the linearized
reference environment, which has no informed flow, no spread and no inventory.
That establishes the closed forms govern the realized dynamics; it does not
establish anything about a market. `[DRY RUN]` is therefore its own status and
does **not** license the paper to imply measurement. Only `[MEASURED]`, which
requires the order-flow simulator, does that.

| # | Panel | Status |
|---|---|---|
| E1 | Amplification replication | **`[MEASURED]`**. Reproduced bit for bit in the order-flow simulator: `1.7428x` and `3.1567x`, relative error `0.00e+00` |
| E2 | `(N, s)` phase diagram | `[DRY RUN]`, 48 cells, max error `7.1e-15`. **Port gate failed, see below: stays `[DRY RUN]`** |
| E2b | Clustered companion | `[DRY RUN]`, measured `m_N` `1.30` against the mean index's `0.74` |
| E3 | Crowding-cadence frontier | `[DRY RUN]`, 175 cells, zero disagreements |
| E4 | Herd immunity | `[DRY RUN]`, thresholds `12 / 14 / 16 / 20` firms across efficacy |
| E5 | Substitution frontier | `[DRY RUN]`, 18 of 18 exact. **never cut** |
| E6 | Over-adaptation | `[DRY RUN]`, built 19 Aug 2026. 12 configurations, zero rows contradicting Corollary 4.2, smallest relative gap `0.290` at `N = 2` and exactly zero at `N = 1` with no client exposure |

| # | Claim | Status | Evidence |
|---|---|---|---|
| E1.1 | Measured amplification `1.74x` at `N=2` and `3.16x` at `N=3` | `[MEASURED]` | `reflex_anchor.py`, reproduced bit for bit from the base project's paper-grade run |
| E1.2 | The measured market departs from the linear prediction **with both signs**: `-12.9%` at `N=2` and `+5.2%` at `N=3` | `[MEASURED]` | `panel1_external_anchor.json`. **Corrected 18 Aug 2026:** the previous wording called both a shortfall, and the `N=3` figure is an overshoot. State this in the body; it is content, not error, and the two-signed departure is the point |
| E1.3 | The differential mode is dead at `kappa = 1`, measuring `3.4e-03` against a theoretical `0` | `[MEASURED]` | Instability is purely common-mode, which is what Theorem 1 generalizes |
| E4.1 | The imperfect-correction law predicts the threshold at `kappa = 0.8`, where it is not proved exact | `[DRY RUN]` | panel 4, 4 of 4 thresholds. **Evidence, not a proof** |
| E6.1 | The decentralized equilibrium over-adapts on every configuration with `N >= 2`, with the gap widening in `N`: `29.0%` at `N = 2` rising to `119.9%` at `N = 20` | `[DRY RUN]` | `panel6_over_adaptation.json`. `m_N` measured from the reference environment's dynamics, the welfare layer above it closed form |
| E6.2 | The fee `t*` implements the social optimum: a firm facing it chooses `a_s`, to relative error `1.7e-13` | `[DRY RUN]` | `panel6_over_adaptation.json` |
| E6.3 | `t*` is strictly increasing in `N`, `kappa` and `s`, and diverges at the boundary with fitted log-log slope `-2.0000` | `[DERIVED]` | `panel6b_comparative_statics.json`. Closed form throughout, no dynamics, so this evaluates Corollary 4.1 rather than measuring it |

---

## Open items blocking a status upgrade

1. ~~**4.7** is stated in expectation and needs a concentration bound.~~
   **Closed.** `../math/derivations/02` proves the entrywise bound and its
   spectral consequence with an explicit failure probability. The sharp
   operator-norm rate is now tracked separately as 4.14, `[DEFERRED]`.
2. ~~**6.7** and **6.8** are the two outstanding pieces of Theorem 3.~~
   **Closed, and 6.8 failed.** See the note below.
3. ~~**7.1** and the welfare page are the whole of Theorem 4's remaining work.~~
   **Closed, 18 Aug 2026**, and panel 6 followed on 19 Aug 2026 at `[DRY RUN]`. The welfare page is written, `verify_theorem4_wedge.py`
   passes with 125 assertions, and 7.0 through 7.5 are `[VERIFIED]`. What remains
   on Theorem 4 is panel 6 (E6) and the `pigouvian_wedge` entry in the theory
   module, which stays absent until the panel exists.
4. Every panel still short of `[MEASURED]`. Panels 2 to 5 sit at `[DRY RUN]`, and
   **after the port's step-3 gate ran on 18 Aug 2026 they are expected to stay
   there for this submission.** The gate measured the residual from the still-
   shared liquidity and price-impact channels and it is not small: `17.7`
   percentage points across the separation range at `N = 2`, and at `N >= 4` the
   simulator's finite-difference probe is no longer measuring a local slope at
   all (`+95%` against the closed form at `N = 4`, best response pinned at a
   bound from `N = 5`). Details in
   `../ml-contributions/environment/HETERO-SIMULATOR-PORT-DESIGN.md`, "Step 3,
   measured". No figure was drawn and no status moved, which is what the gate is
   for.

**Closed 19 Aug 2026.** The port workstream is shut, not paused. Neither repair
the design document names is attempted: routing liquidity and impact through the
profiles is a multi-day edit that risks panel 1's bit-for-bit anchor, and
re-tuning the probe to stay local at `N = 20` is a different market from the one
panel 1 anchors. Panels 2, 2b, 4 and 5 therefore ship at `[DRY RUN]`, which is
the status they held before the port ran and the fallback the plan named. No row
above changes. Section 10 states the gate outcome as a limitation.

On that last one: a passing dry run is progress on the derivations and no
progress at all on the empirics. Until a panel runs in the order-flow simulator
the claim it tests holds at its derivation status and the paper must not imply
measurement. The temptation to treat a passing dry run as a result is exactly why
`[DRY RUN]` was given its own flag rather than folded into `[VERIFIED]`.

## Note on 6.8, the one claim that failed

The strong-correction limit is optimistic rather than conservative. As the
previous version of this ledger anticipated, that changed what the paper claims
and not only what it proves: the exact root is now the theorem, the limit is a
corollary carrying a stated error direction, and two new results (6.10, 6.11)
replace the clean law with a strictly larger claim. The de-scope order is amended
in the plan of record, since shipping the limit alone would state an unsafe
criterion without flagging it.

Worth recording that the ledger did its job here. 6.8 was flagged in advance as
the claim whose failure would matter most, and it was checked before the section
was written rather than after.

## Note on the Section 4 and 5 upgrades

Sections 4 and 5 moved from `[DERIVED]` to `[VERIFIED]` on 18 Aug 2026, when the
proofs in `../math/derivations/` landed with assertion-based certificates rather
than report-printing scripts. The standing rule is satisfied: each upgraded claim
names a certificate that fails loudly, and every one of them has been run. Claims
still resting on argument rather than computation (4.5's Perron-Frobenius
condition) stay at `[DERIVED]`, and the two genuinely open pieces (4.14, 5.10) are
tracked as `[DEFERRED]` rather than quietly dropped.

## Note on the Section 7 upgrade

Section 7 moved from `[DERIVED]` to `[VERIFIED]` on 18 Aug 2026 when the welfare
page landed with `verify_theorem4_wedge.py`. The upgrade satisfies the standing
rule: each claim names a certificate that fails loudly and every one has been run.
Two things are deliberately not upgraded. 7.6 is an **assumption**, not a claim,
and is flagged as one. E6 is `[DRY RUN]` as of 19 Aug 2026 and goes no higher:
it runs in the reference environment, where `m_N` is measured from dynamics but
the welfare object above it is closed form. The order-flow simulator has no
aggressiveness choice variable and no welfare object, so there is no route to
`[MEASURED]` for this panel at any effort, and the theory being certified does
not make the panel a measurement.

The load-bearing step was Lemma 11. Before it, `d m_N/d a_i` was going to be
written down as `1/N` by analogy with the commons, which C34 shows is wrong by
the factor `N_eff`.

## Standing rule

**A closed form that reaches the paper without a passing certificate ships at
`[DERIVED]`, never at `[VERIFIED]`.** The temptation to round up appears during
the writing week, which is why the rule is written down now.
