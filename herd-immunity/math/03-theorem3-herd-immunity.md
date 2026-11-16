# Theorem 3: herd immunity, and diversity as its substitute

The base project's corrected update (performative-gradient, structurally
anchored) stabilizes a *single* firm beyond its boundary, because the corrected
dynamics are governed by the objective curvature `gamma_PO` rather than by the
cobweb. It has never been asked what correction does in the *game*.

**Complete proof:** [`derivations/04-mixed-market-secular.md`](derivations/04-mixed-market-secular.md),
certified by
[`verify_theorem3_herd_immunity.py`](../ml-contributions/certificates/verify_theorem3_herd_immunity.py),
70 checks. **Where this note and the derivation disagree, the derivation is
right.** Three of this note's statements did not survive contact with the exact
root, and they are marked inline below.

## Setup

A mixed market: `N_b` blind firms with response slope `m_1`, and `N - N_b`
corrected firms whose response to competitors' deployments is damped by
`gamma/gamma_PO < 1`. Write the corrected fraction

```
   rho  =  1 - N_b/N .
```

## Statement

**Theorem 3.** The joint Jacobian of the mixed market has block structure whose
spectrum solves an explicit scalar secular equation, a quadratic in closed form
for two blocks. In the strong-correction limit (`gamma_PO -> infinity`) the
unstable feedback cycle runs through blind firms only, and the market is stable
iff the blind sub-ecosystem is:

```
   m_1 ( 1 + kappa * s * (N_b - 1) )  <  1 ,
```

that is, iff

```
   N_b  <  N_c(s)  =  1 + (1/m_1 - 1)/(kappa * s) ,
```

equivalently

```
   rho  >  rho*(s)  =  max( 0 ,  1 - N_c(s)/N ) .
```

[DERIVED]

## Derivation of the limit case

The blind block is itself a symmetric shared-pool market of size `N_b` with
effective spillover `kappa * s`, so the base theorem applies to it verbatim. In
the strong-correction limit the corrected firms transmit no feedback, so they
drop out of the cycle entirely and contribute only their own stable modes.

Rearranging the blind-block condition:

```
   1 + kappa*s*(N_b - 1)  <  1/m_1
   kappa*s*(N_b - 1)      <  1/m_1 - 1
   N_b                    <  1 + (1/m_1 - 1)/(kappa*s)  =  N_c(s)
```

and `rho = 1 - N_b/N > 1 - N_c(s)/N`. The `max(0, .)` handles the case where
`N_c(s) > N`, meaning the market is stable with no corrected firms at all.

**Verification status.** The closed form was checked against dense eigensolves
on 4000 random `(m_1, kappa, s, N_b)` draws with zero mismatches, before the
plan of record was written. [VERIFIED numerically]

## The herd-immunity collapse

At `kappa = s = 1`:

```
   N_c   =  1 + (1/m_1 - 1)/1  =  1/m_1
   m_N   =  m_1 (1 + 1*1*(N-1))  =  m_1 N
   rho*  =  1 - N_c/N  =  1 - 1/(m_1 N)  =  1 - 1/m_N .
```

**Exactly the epidemiological herd-immunity threshold `1 - 1/R_0`, with the
systemic modulus as the reproduction number.** A market of 10 firms at
`m_N = 2.5` needs 60% of them un-blinded. The un-blinded protect the blind,
because what they stop transmitting is destabilizing feedback. [DERIVED,
arithmetic checked]

The parallel is structural rather than decorative, and the paper should say why:
in network epidemiology the epidemic threshold is `1/lambda_max` of the contact
matrix, so `R_0` is itself the spectral radius of a next-generation operator.
`m_N` is the spectral radius of the joint retraining Jacobian. Both thresholds
are the same mathematical statement about a linearized operator, which is why
the vaccination law transfers without adjustment. See literature cluster E.

## The synthesis result: diversity and correction are substitutes

`rho*(s)` is increasing in `s`, so a market can reach stability along either
axis. Un-blind more agents, or share fewer models.

Worked at `N = 20`, `m_1 = 0.15`, `kappa = 0.8`, so
`(1/m_1 - 1) = 5.667`:

| `s` | `N_c(s)` | `rho*(s)` | reading |
|---|---|---|---|
| `1.0` | `8.08` | `0.596` | monoculture needs about 60% corrected |
| `0.5` | `15.17` | `0.242` | about a quarter suffices |
| `0.2` | `36.42` | `0` | stable with no corrected agents at all |

Recomputed by hand and matching the plan of record's "about 60%" and "at
`s = 0.2` the threshold is negative". [VERIFIED by recomputation]

The `(rho, s)` iso-stability frontier is the paper's headline figure and its
most policy-legible object: a regulator facing an unstable market of adaptive
models has two interchangeable instruments and can price them against each
other. Neither predecessor draft contained this, because each had only one of
the two axes.

## Economic reading

Correction is a **public good**. An un-blinded firm captures a private benefit,
since it quotes closer to its optimum, while the stability it contributes
accrues to everyone. Herd immunity below the threshold, free-riding above it,
which is exactly why the market will not reach `rho*` on its own and why
Theorem 4 exists.

Model diversity has the same structure, which is why the substitution is between
two goods that are **both under-supplied**, rather than between a good and a bad.
Say this explicitly; it is the difference between a substitution frontier a
regulator can move along and a menu of two policies that happen to be plotted on
the same axes.

## The exact finite-`gamma_PO` version

The strong-correction limit is clean; the exact version replaces it with the
root of the two-block secular equation. Both are reported. Structure:

```
   blocks:  blind (N_b),  corrected (N - N_b)
   coupling: kappa*s between blocks and within
   damping:  gamma/gamma_PO on the corrected block's response
```

Two blocks give a quadratic, so the root is closed form. Writing it out is on
the build list; it is fourth in the de-scope order, and if cut, the limit
theorem plus simulation ships in its place. [TO BUILD]

## The experiment, new in kind

The corrected loop has only ever been run single-dealer. Run it inside the
`N`-dealer shared-pool market at corrected fractions
`rho = 0, 1/N, ..., 1` in an `m_N > 1` regime, then sweep `s` to trace the
substitution frontier. Either outcome is a result; matching the predicted curve
is the headline. [TO BUILD]

Companion diagnostic: private P&L of corrected against blind firms, exhibiting
the public-good structure directly. Fifth in the de-scope order.

## Corrections this note needs

Recorded inline rather than by silent edit, so the disagreement is visible.

**1. The stability criterion above is not exact as written.** `rho > rho*(s)`
with `rho* = max(0, 1 - N_c/N)` mispredicts the all-blind market that is stable
because it needs no correction, since the clamp at zero combined with a strict
inequality excludes `N_b = N`. The primitive form `N_b < N_c(s)` is exact, on
4000 draws with zero mismatches. Use it as the theorem and keep `rho*` as the
policy object.

**2. The verification claim above is about the limit, not the market.** "Checked
against dense eigensolves on 4000 random draws with zero mismatches" holds for
the strong-correction limit's radius. It says nothing about the market at finite
`gamma_PO`, which is a different and larger number.

**3. The limit is optimistic, not conservative.** See below.

## Open items

1. ~~Write out the two-block quadratic.~~ **Done**, `derivations/04` Section 3,
   exact to `2.5e-14`. Empty blocks need the single-block form; the quadratic
   leaves a phantom root otherwise.
2. ~~Check whether `rho*` should be reported as a fraction or an integer count.~~
   **Done.** The count is `N - ceil(N_c) + 1`, not `ceil(rho* N)`. The two agree
   except at exact-integer `N_c`, where the latter is off by one.
3. ~~Confirm the strong-correction limit is approached from the stable side.~~
   **Done, and it is not.** See below.

**The limit is optimistic.** The radius is nondecreasing in `gamma/gamma_PO`, by
Perron-Frobenius on an entrywise-nonnegative matrix, so the limit under-states it.
On random draws it calls `11.8%` of configurations stable that are unstable at
finite correction. The paper must state the direction, and the exact root moves
out of the de-scope order.

**The repair is a better result than the thing it repairs.** At `kappa = s = 1`
the exact threshold is `(1 - 1/m_N)/(1 - theta)` with `theta = gamma/gamma_PO`,
the epidemiological **imperfect-vaccine** coverage law, and it carries a critical
efficacy `gamma_PO/gamma > m_N` past which no corrected fraction works. The
correspondence the paper claims now transfers a refinement and not just a
threshold, which is evidence the analogy is structural.
