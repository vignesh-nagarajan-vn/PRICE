# 9. Experiments

**Status: drafted.** Target 1.00 page. Source:
[`../ml-contributions/EXPERIMENT-SPECS.md`](../ml-contributions/EXPERIMENT-SPECS.md),
which holds the full specs, and the result files under
`../ml-contributions/experiments/results/`.

---

Six panels, one per result. The table states the mapping so a referee can check
coverage at a glance, and it states each panel's evidential status in the same
row, because the six are not all the same kind of evidence and a section that
blurred them would be claiming more than the build earns.

**Two statuses, and the difference is the whole of this section.** A panel marked
`[MEASURED]` ran in the order-flow simulator: a genuine `N`-dealer market with
informed flow, spread and inventory, reducing bit for bit to the single-dealer
market at `N = 1`. A panel marked `[DRY RUN]` ran in a linearized reference
environment that realizes the model's response geometry and nothing else. A dry
run establishes that the closed forms govern the realized dynamics, which no
amount of algebra checking covers, and it establishes nothing about a market.
Stability in every panel is estimated from the trajectory's asymptotic growth
rate under the actual retraining map rather than read off an eigensolve, so
"measured" always means measured from dynamics.

| # | Panel | Tests | Status | Figure |
|---|---|---|---|---|
| 1 | Amplification replication | base result | **`[MEASURED]`** | table |
| 2 | The `(N, s)` phase diagram | Theorem 1 | `[DRY RUN]` | Fig 1 |
| 2b | Clustered companion | Theorem 1 | `[DRY RUN]` | Fig 1 inset |
| 3 | The crowding-cadence frontier | Theorem 2 | `[DRY RUN]` | Fig 2 |
| 4 | Herd immunity | Theorem 3 | `[DRY RUN]` | Fig 3 |
| 5 | The substitution frontier | Theorem 3 | `[DRY RUN]` | **Fig 4** |
| 6 | Over-adaptation | Theorem 4 | `[DRY RUN]` | Fig 5 |

**Panel 1 is measured in the order-flow simulator rather than in the reference
environment, and it validates the inherited scaffolding rather than any of the
four results.** Its claim is the monoculture corner `R = 1 1'`, which the base
project already implements. It is not *external* validation: the prior published
run is this paper's own base work, cited in the third person because the review
is double-blind, and third-person citation cannot support a claim of
independence. It reproduces a
prior published run in that run's own simulator, measuring common-mode moduli of
`0.7856`, `1.3692` and `2.4799` at `N = 1, 2, 3`, hence amplification `1.7428x`
and `3.1567x` against a published `1.74x` and `3.16x`, at relative error
`0.00e+00`. [MEASURED] It ships as a table rather than a plot, because comparing
to published numbers is easier to check in a table.

**The gap to the linear prediction is content, not error.** The predictions are
`2` and `3`, so the market runs `-12.9%` at `N = 2` and `+5.2%` at `N = 3`. The
two gaps have **opposite signs**, which is what a nonlinear market with
saturating flow does around a linearization, and it is a better argument for the
reference environment than a one-signed shortfall would be: the reference
environment reproduces the prediction exactly because it omits precisely the
nonlinearity and the flow saturation that produce the two-signed departure.
[MEASURED] The differential mode measures `3.4e-03` against a theoretical zero at
`kappa = 1`, so the instability is purely common-mode, which is the mechanism
Result 1 generalizes. [MEASURED]

**Panels 2 to 6, and what they establish.** Panel 2 sweeps 48 cells of the
`(N, s)` plane and agrees with the predicted boundary to `7.1e-15`; its clustered
companion runs a market whose measured modulus is `1.30`, comfortably unstable,
while a mean-alignment diversity index reports `0.74` and calls it safe with
margin, understating the effective learner count by `1.757x`. Panel 3 covers 175
cells of the `(N_eff, K)` grid with zero disagreements against the predicted
`K_max`. Panel 4 finds the herd-immunity threshold at `12 / 14 / 16 / 20` firms
of twenty at efficacies `1.00 / 0.90 / 0.75 / 0.60`, all four matching the
imperfect-correction law at `kappa = 0.8`, where that law is not proved exact, so
those four are evidence rather than proof. Panel 5 matches the predicted
substitution frontier at 18 of 18 points. Panel 6 finds the decentralized
equilibrium over-adapting on every configuration with `N >= 2`, from `29.0%` at
`N = 2` to `119.9%` at `N = 20`, with the fee implementing the social optimum to
`1.7e-13` and the degenerate single-firm case at exactly zero. **All six of these
are `[DRY RUN]`.** Each agrees with the closed form it tests, and none of them is
a claim about a market.

**Why panels 2 to 5 are not measured, stated plainly rather than left to a
reader's inference.** A heterogeneous-response port of the order-flow simulator
was designed and built, and it is exact: at flat exposure profiles it reproduces
the unmodified base simulator at every `N` from 1 to 6. Its acceptance gate then
failed. The simulator's liquidity and price-impact channels stay shared whatever
the response profiles are, and isolating that residual shows it reaching `17.7`
percentage points across the separation range at `N = 2`, larger than several of
the effects these panels resolve; at `N >= 4` the finite-difference probe is no
longer measuring a local slope at all. The two available repairs were priced and
declined for this version. No figure was drawn from that port and no status
moved, which is what the gate is for, and Section 10 carries the consequence as a
limitation.

**Panel 6 is a different case and the paper does not conflate them.** It is
`[DRY RUN]` because the order-flow simulator has no aggressiveness choice
variable and no welfare object, so there is no `[MEASURED]` version of it to
build. Its crowding is measured from dynamics and the welfare layer above that is
closed form.

**Reporting rules,** inherited and stated once. Sweep the feedback gain, never
the confounded adversariality parameter. Probe at the operating spread, with
common random numbers on paired probes. Multi-dealer runs can saturate the
informed-flow cap, so the liquidity boost is scaled down per the environment's
guidance and never de-saturated silently. Beyond-boundary probe readings are
diagnostics, not slopes. Every panel is CPU-only and deterministic from
`(config, seed)`, every closed form carries a numerical certificate that fails
loudly, and the harness exits nonzero on any disagreement with a closed form
rather than producing a quiet figure. The reference environment's acceptance test
is that it reproduces the homogeneous market at `R = 1 1'`, and that reduction is
checked before any number is taken from it.

**Disagreement is reported where it occurs.** A measured frontier departing from
a predicted one is the scope boundary of a linearized theory and is a result. The
port gate above is the clearest instance in this build, and it is reported rather
than smoothed.

Under double-blind the simulator is described generically, with an
anonymized-artifact promise and no repository URL.

---

## Checklist

**Status honesty, all new since the port gate ran:**

- [x] Coverage table present, with status in the same row as the mapping
- [x] Panel 1 labeled measured rather than external, with what it validates named,
      and the two-signed departure stated as content rather than error
- [x] Every panel's status stated explicitly; no dry run described in language
      implying measurement
- [x] The port gate stated in the body, since a reader is owed the reason panels
      2 to 5 are not measured
- [x] Panel 6's different reason for being a dry run distinguished from panels 2
      to 5's

**Carried over from the original plan:**

- [x] Environment reduction test mentioned
- [x] Protocol rules stated once, compactly
- [x] Simulator described generically, no repository URL
- [ ] Every worked-example parameter stated in a caption, `c = 0.8` included.
      **Carried to the figure pass**, since captions are written with the figures

## Notes for the writing pass

**Length.** About 940 words of prose, excluding the table. That is at the
one-page target with the table costing roughly a fifth of a page, so this section
is slightly over and is the first place overflow shows. The cut, if one is
needed, is the panel-by-panel paragraph compressing to its numbers alone, since
the table already carries the mapping.

**What changed against the plan of record.** The plan's experiment list assumes
every panel reaches the simulator. Five of six did not, so this section carries a
status column the plan does not have and a paragraph explaining the port gate
that the plan did not anticipate needing. That is a disagreement with the plan
and it is stated as one here rather than absorbed silently.

**The one thing a referee will probe.** Whether the dry runs are being passed off
as measurements. The defense is structural rather than rhetorical: the status is
in the coverage table, in every claim's inline flag, and in the claims ledger, and
the reason for the gap is in the body rather than in a footnote.
