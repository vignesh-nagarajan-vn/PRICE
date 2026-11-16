# Heterogeneous-response simulator port: the modeling decision

**Written 18 Aug 2026.** This is the design record for the port that panels 2,
2b, 4 and 5 need before any of them can reach `[MEASURED]`. It fixes the
mechanism and states what the mechanism does not cover. The skeleton that
implements it is
[`../experiments/hetero_simulator_port.py`](../experiments/hetero_simulator_port.py).

Nothing under the base project is modified. The port subclasses the base
simulator from inside this repository, the same arrangement
[`../experiments/reflex_anchor.py`](../experiments/reflex_anchor.py) already
uses.

---

## The problem, stated exactly

The base project's `env/multi_dealer.py` couples dealers through one line:

```python
own_resp  = [exp(-c_t * h_j) for j in dealers]      # per bond
sum_resp  = sum(own_resp)
spread_resp_i = own_resp[i] + kappa * (sum_resp - own_resp[i])
```

Collect that into a matrix acting on the vector of per-dealer responses:

```
spread_resp = [(1 - kappa) I + kappa * 1 1'] own_resp
```

Compare Theorem 1's joint Jacobian `J = -m_1[(1-kappa) I + kappa R]`. The base
market is the theorem at `R = 1 1'` and at nothing else. Every dealer
contributes to the informed pool identically and senses it identically, so
there is no object in the simulator that could carry a per-dealer response
direction. A knob does not exist to be turned; the channel has to be widened
first.

## The decision

**Give each dealer a bond-space exposure profile, and route both the
contribution to the informed pool and the sensing of that pool through it.**

Write `u_i in R^{n_bonds}` for dealer `i`'s exposure profile, normalized so that
its mean square across bonds is one. Replace the coupling line with

```
pool(b)          = sum_j  own_resp_j(b) * u_j(b)
spread_resp_i(b) = u_i(b) * [ (1 - kappa) * own_resp_i(b) * u_i(b)
                              + kappa * pool(b) ]
```

Read in words: the informed pool's attractiveness at bond `b` is the sum of
every dealer's spread response there, each weighted by how much of that dealer's
book sits in that bond, and dealer `i` feels that pool only to the extent that
its own book sits there too.

### Why this mechanism

Four reasons, in the order they mattered.

**It is the same construction the theory already uses, read in the simulator's
own coordinates.** In
[`hetero_response_env.py`](hetero_response_env.py) firm `i` senses the shared
pool projected on its own unit response direction, its own contribution at full
weight and every competitor's at weight `kappa`. That is line-for-line what the
expression above does, with the abstract response direction `E_i` replaced by
the concrete thing a bond dealer actually differs in, namely which bonds it
quotes seriously. The port therefore does not introduce a second, competing
notion of alignment that would then have to be reconciled with Theorem 1.

**It produces the alignment matrix rather than assuming one.** Differentiating
`spread_resp_i` in `h_j` at a common reference spread, then averaging over bonds
the way `_measure_toxic_levels` already does, gives a sensitivity matrix

```
M_ij  proportional to  mean_b[u_i(b) u_j(b)] * (kappa + (1 - kappa) delta_ij)
```

With the mean-square normalization the diagonal is one and the off-diagonal is
`kappa * R_ij` with `R_ij = mean_b[u_i(b) u_j(b)]`, a Gram matrix of unit-norm
vectors. So `M = (1 - kappa) I + kappa R`: the alignment matrix comes out of the
flow generation rather than being written into it. This is the same discipline
`hetero_response_env.py` enforces by separating `jacobian()` from
`predicted_jacobian()`, and the port keeps it by measuring `R` back off the
realized profiles instead of trusting the constructor.

**The bond dimension is already there and already correlated.** `bonds.py`
builds a sector-block plus global-factor structure over the universe, and that
structure is the environment's only existing account of why two instruments move
together. Specializing dealers by sector exposure therefore borrows an object
the ground truth already commits to, rather than bolting a new latent space onto
the simulator. It also gives the supply-chain parameter `s` an economic reading
that a referee can hold: `s` is overlap of coverage, and the global factor puts
a floor under how disjoint two dealers can be even when their sectors do not
intersect, which is the right qualitative statement about a market where
everything shares a rates factor.

**It leaves every other channel untouched.** Uninformed flow, spread capture,
inventory, price impact, the liquidity field and the draw order are all
unchanged. That matters for the reduction test below, and it means a
disagreement between the port and the closed form cannot be blamed on a
microstructure edit made at the same time.

### Rejected alternatives, briefly

*Separate informed-flow segments per dealer.* Cleanest economically, but it
requires inventing a segment-arrival process and a routing rule, and both of
those are new structural ground truth that nothing validates. It also does not
reduce to the base market at any parameter setting without a further argument.

*Different signal channels, that is per-dealer `info_signal_noise` or a
per-dealer signal draw.* This changes how well a dealer sees the mispricing, not
which direction its response points. It moves moduli, not alignment, so it
models correction (Theorem 3's `gamma_ratio`) and not crowding. Useful later,
wrong here.

*Per-dealer `kappa_ij` matrix.* Would give `R` directly and would be one line.
Rejected because it writes the answer in by hand: the alignment matrix would be
a free parameter of the environment rather than a consequence of what dealers
do, and the panel would then be checking the closed form against a restatement
of itself.

## The reduction to `R = 1 1'`, exactly

Set `u_i(b) = 1` for every dealer and every bond, which is the mean-square
normalization applied to a dealer that quotes the whole universe uniformly.
Then `pool(b) = sum_j own_resp_j(b) = sum_resp(b)` and

```
spread_resp_i = 1 * [ (1 - kappa) * own_resp_i * 1 + kappa * sum_resp ]
              = own_resp_i + kappa * (sum_resp - own_resp_i)
```

which is the base project's line character for character, and `R_ij =
mean_b[1 * 1] = 1` for every pair, so `R = 1 1'`.

The reduction is exact in floating point as well as on paper, not merely equal
in the limit. Multiplication by `1.0` is exact in IEEE arithmetic, and the port
forms `pool` with the same `torch.stack(...).sum(dim=0)` over the same list in
the same order as the base, so the summation rounds identically. The port then
writes the bracket in the base's own associativity, `own + kappa * (pool -
own)`, rather than an algebraically equal regrouping. That is why the acceptance
test can demand bit-for-bit reproduction of the published anchors instead of
agreement to some tolerance, and why a failure of that test is informative
rather than a tolerance argument.

The structural constructor is parametrized so the monoculture is a *value* of
the parameter, not a special case in the code: `sector_profiles(..., tilt=0)`
returns all-ones profiles. There is no separate monoculture code path to keep in
sync.

## Drift guard

The port reimplements the base `step` in order to change one expression inside
it, so the copy can go stale if the base project changes. The port therefore
inspects the base source at import and fails loudly if the coupling line it was
written against is no longer there. A silently stale copy that still reproduces
the old anchors is the failure mode worth spending ten lines to prevent.

## What this does not yet handle

Open, and left open.

1. **Only the informed-intensity channel carries the exposure profile.** The
   liquidity field is still driven by total gross flow and by the *tightest*
   dealer's spread across the whole universe, and price impact is still driven
   by total net flow. Both remain fully shared no matter what the profiles are.
   At `u = 1` that is exactly right, since everything is shared there anyway. Away
   from it there is a second coupling channel whose alignment is `1 1'` and not
   `R`, so the realized joint modulus should be expected to sit *above* the
   closed form's prediction by an amount that grows as the profiles separate.
   Whether that residual is small enough to leave the panels interpretable is an
   empirical question this session does not answer, and it is the first thing the
   heterogeneous sweep has to measure.

2. **The reachable set of `R` is constrained by the universe.** The default
   config has `n_bonds = 8` and `n_sectors = 2`. Sector-tilted profiles live in
   an 8-dimensional space, so at most 8 dealers can be placed independently, and
   with two sectors the sector-tilt constructor can only realize a two-block
   alignment. A genuine `(N, s)` sweep needs either a larger universe or the
   free-profile constructor. Enlarging the universe changes `BondUniverse` and
   therefore changes the market, so panel 1's anchor does not transfer to a
   config with different `n_bonds`. Any heterogeneous panel must either run at
   `n_bonds = 8` or re-anchor.

3. **The global factor puts a floor on separation, and it is not quantified.**
   Two dealers with disjoint sectors still overlap through `global_factor`, so
   `R_ij` cannot be driven to zero by sector choice alone. The exact floor as a
   function of `global_factor` and the sector partition is not worked out here.
   Orthogonal responses, claim 4.3, are therefore not reachable by the
   structural constructor, only by the free-profile one.

4. **Profiles are static and exogenous.** A dealer's coverage does not respond to
   crowding. Endogenous specialization is the interesting economics and is out of
   scope for the paper.

5. **Heterogeneous moduli and heterogeneous alignment are not yet combined in the
   simulator.** Theorem 3's mixed market needs per-dealer `gamma`, which is a
   different edit to a different part of the config. Claim 4.10's bounds are
   stated for heterogeneous moduli, and the port as written carries a single
   `toxicity_feedback` for all dealers.

6. **The reduction is proved at the coupling expression, not at the measured
   modulus, for `u != 1`.** At `u = 1` the acceptance test closes the loop
   end to end against a published measurement. Away from it, the argument that
   `M = (1 - kappa) I + kappa R` is a linearization of `_measure_toxic_levels`
   around a common reference spread, and the finite-difference probe at finite
   `delta` in a nonlinear saturating market will not match it exactly. Panel 1
   already measures that gap at `12.9%` and `5.2%` in the monoculture. The
   heterogeneous version of that gap is unmeasured.

## What is left on the port, in order

The next session's brief. Each item depends on the ones above it.

1. **Decide the universe.** Either accept `n_bonds = 8`, `n_sectors = 2` and
   sweep with free profiles rather than sector tilt, or enlarge the universe and
   re-measure the monoculture anchor at the new config, since panel 1's numbers
   do not transfer across a changed `BondUniverse`. This is a decision, not a
   build, and everything else waits on it.
2. **Build the free-profile constructor**, the analogue of
   `response_jacobians_for_R`: given a target alignment `R`, return profiles
   whose *measured* alignment is `R` to tolerance, subject to nonnegativity.
   Nonnegativity is the new constraint the linearized environment does not have,
   since a coverage weight cannot be negative, and it is what bounds the
   reachable set.
3. **Measure the residual from the shared channels.** Run the port at a sequence
   of separations from the monoculture and compare the measured joint modulus
   against `m_1 * N_eff` at the measured `R`. The liquidity and impact channels
   stay aligned at `1 1'` regardless of the profiles, so the measured modulus
   should exceed the prediction by a gap that grows with separation. Report the
   gap. If it is large the panels are not interpretable as stated and the design
   needs revisiting before any figure is drawn.
4. **Then, and only then, the panels.** Panel 5's substitution frontier first,
   since it is never cut, then panels 2, 2b and 4. Wire into `panels.py` only
   after step 3 has a number.
5. **Ledger.** No status moves before step 4 produces a run. A passing reduction
   test is not a measurement.

## Step 3, measured: the gate, and it does not open

**Run 18 Aug 2026**, `../experiments/hetero_channel_residual.py`, results in
`../experiments/results/hetero_channel_residual.json`. Step 1 was decided in
favour of keeping `n_bonds = 8` and `n_sectors = 2` and sweeping with free
profiles, since panel 1's anchor does not transfer across a changed
`BondUniverse` and panel 1 is never cut. Step 2 built two exact constructors:
`supply_chain_profiles`, which realizes `(1-s)I + s 1 1'` to machine precision
with nonnegative weights and reaches both the monoculture and the orthogonal
corner exactly, and `profiles_for_R`, the general projected-gradient version.

**The port itself is exact.** At flat profiles it reproduces the *unmodified*
base simulator's measured modulus at every `N` from 1 to 6, not only at the
published 1, 2 and 3. Nothing below is a port artifact.

The sweep, at `kappa = 1`, against the closed form `m_1 * N_eff` at the measured
alignment:

| `N` | `s` | predicted | measured | gap |
|---|---|---|---|---|
| 2 | `1.00` | `1.5712` | `1.3692` | `-12.86%` |
| 2 | `0.75` | `1.3748` | `1.2257` | `-10.85%` |
| 2 | `0.50` | `1.1784` | `1.0860` | `-7.84%` |
| 2 | `0.25` | `0.9820` | `0.9521` | `-3.05%` |
| 2 | `0.00` | `0.7856` | `0.8237` | `+4.85%` |
| 4 | `1.00` | `3.1424` | `6.1309` | `+95.10%` |
| 4 | `0.50` | `1.9640` | `2.8886` | `+47.08%` |
| 4 | `0.00` | `0.7856` | `1.0254` | `+30.52%` |

**Read the `s = 1` row first.** At `s = 1` the profiles are flat and the port is
the base market, so that row is not a channel residual at all: it is the base
market's own departure from the linearization. The residual the design predicted
is therefore the *change* in the gap along a row, not the gap itself.

**At `N = 2` the prediction holds and the residual is about 18 points.** The gap
moves monotonically from `-12.86%` at the monoculture to `+4.85%` at
orthogonality, a swing of `17.7` percentage points, and it crosses zero. The
sign is what the design argued: as the profiles separate, the closed form stops
seeing coupling that the liquidity and price-impact channels still carry, so the
measured modulus rises relative to the prediction until it sits above it. At
full orthogonality the closed form predicts no amplification whatsoever and the
market still delivers `+4.85%`. That is the shared-channel residual, isolated,
and it is not small.

**At `N = 4` the reference is broken before heterogeneity enters.** The
monoculture gap is `+95.10%`, measured against the base market itself. Beyond
`N = 4` the probe reports its best response pinned at a spread bound, so the
measured modulus is not a local slope at all. The market at `N = 4` has
`m_N = 6.13`, far outside the regime where a finite-difference probe at
`delta = 0.25 h_ref` measures a linearization of anything.

### What this means for the panels, stated plainly

**The panels are not interpretable in this simulator as planned, and no figure
should be drawn from it.** Panel 2 sweeps `(N, s)` over 48 cells, panel 4 runs at
`N = 20`, and panel 5's frontier is stated at `N = 20`. Every one of those sits
at an `N` where this configuration's probe is not measuring a slope. Even at
`N = 2`, where it is, the shared-channel residual reaches `17.7` points across
the separation range, which is larger than several of the effects the panels are
supposed to resolve.

Two possible repairs, neither attempted here and neither cheap:

1. **Route the liquidity and impact channels through the profiles too**, so the
   second coupling channel carries `R` rather than `1 1'`. This is a larger edit
   than the one the port makes and it changes the market at `u = 1` as well,
   which would cost the bit-for-bit anchor unless done with the same care.
2. **Find a configuration whose probe stays local at the `N` the panels need.**
   The `f_probe = 0.5` interior-probe gain keeps the best response interior at
   `N <= 4` but not the modulus small, and `N = 20` at any gain that keeps
   `m_N` near 1 is a different market from the one panel 1 anchors.

The gate exists so that this is a recorded negative result instead of a figure.
Panels 2, 2b, 4 and 5 stay `[DRY RUN]`, which is exactly the status they had
before the port ran, and the paper presents them as closed-form predictions with
reference-environment agreement stated as such.

## Status

**Workstream closed 19 Aug 2026.** Neither repair above is attempted for this
submission. Repair 1 is a larger edit than the port itself and would put panel
1's bit-for-bit anchor at risk, which is the paper's only measured result.
Repair 2 changes the market away from the one panel 1 anchors, so a probe that
stayed local at `N = 20` would be measuring a different object. Both cost days,
and the panels they would upgrade are allowed to ship at `[DRY RUN]`. The port
is left exactly as it stands, exact at the reduction and imported by nothing, so
a journal version resumes from this document rather than from scratch.

Nothing here upgrades any claim. Panels 2, 2b, 4 and 5 remain `[DRY RUN]` in
[`../../../archive/herd-immunity-v1/writing/CLAIMS-LEDGER.md`](../../../archive/herd-immunity-v1/writing/CLAIMS-LEDGER.md). This document
records a design and a skeleton that reproduces the known case; it records no
new measurement.
