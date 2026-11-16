# Notation and standing assumptions

ASCII math throughout, matching the plan of record. This table is the single
source of truth for symbols; every other note and every writing file uses these
and nothing else.

## Symbols

| Symbol | Meaning | Range | Origin |
|---|---|---|---|
| `N` | number of firms in the market | integer `>= 1` | |
| `d` | dimension of each firm's decision (in the market instantiation, bonds' half-spreads) | integer `>= 1` | |
| `h_i` | firm `i`'s deployed decision | `R^d` | |
| `eps` | performative response strength of the environment | `> 0` | REFLEX |
| `beta` | sensitivity of the objective to the induced shift | `> 0` | REFLEX |
| `gamma` | own-objective curvature (the stabilizing term) | `> 0` | REFLEX |
| `m_1` | single-firm performative retraining modulus, `= eps*beta/gamma` | `> 0`, stable iff `< 1` | REFLEX |
| `kappa` | spillover: how much one firm's deployment contaminates the flow its competitors face | `[0, 1]` | REFLEX |
| `E_i` | firm `i`'s response Jacobian: how its own deployment reshapes the flow it faces | `d x d` | **new here** |
| `r_ij` | pairwise alignment of feedback directions | `[-1, 1]` | **new here** |
| `R` | alignment matrix `(r_ij)`, a correlation matrix of feedback directions | `N x N`, PSD, unit diagonal | **new here** |
| `lambda_max(R)` | firms per independent model (effective crowding) | `[1, N]` | **new here** |
| `N_eff` | effective crowding, `= 1 + kappa(lambda_max(R) - 1)` | `[1, 1 + kappa(N-1)]` | **new here** |
| `m_N` | systemic modulus, `= N_eff * m_1`. The feedback reproduction number | `> 0`, stable iff `< 1` | **new here** |
| `s` | shared-model fraction: fraction of each firm's response attributable to a shared foundation model, vendor, or pretraining corpus | `[0, 1]` | **new here** |
| `Xi_i` | firm `i`'s idiosyncratic response component | `d x d` | **new here** |
| `K` | gradient steps taken per deployment (retraining cadence) | integer `>= 1` | REFLEX |
| `eta` | inner learning rate | `> 0` | REFLEX |
| `c` | inner per-step contraction, `= 1 - eta*gamma` | `(0, 1)` | REFLEX |
| `mu_N(K)` | outer-map slope of the joint common mode under `K`-step retraining | | **new here** |
| `K_max` | the cadence window: largest `K` keeping an `m_N > 1` market stable | | **new here** |
| `gamma_PO` | objective curvature governing the corrected dynamics | `> gamma` | REFLEX |
| `N_b` | number of blind (uncorrected) firms | `0..N` | **new here** |
| `rho` | corrected fraction, `= 1 - N_b/N` | `[0, 1]` | **new here** |
| `rho*` | herd-immunity threshold | `[0, 1)` | **new here** |
| `N_c(s)` | critical population of blind firms | | **new here** |
| `a_i` | firm `i`'s adaptation aggressiveness (cadence, learning rate, responsiveness) | `> 0` | **new here** |
| `t*` | the Pigouvian wedge | | **new here** |

Symbols marked **new here** are the paper's contribution surface. Everything
marked REFLEX is inherited and cited, never re-derived.

## Standing assumptions

**A1. Linearization.** All spectral statements are linearizations of the joint
retraining map around the joint equilibrium. The simulator is the nonlinear
check, and the scope boundary is reported rather than hidden.

**A2. Symmetric moduli.** Theorem 1's identity is exact for `m_i = m_1` for all
`i`. The heterogeneous case is a two-sided bound whose tightness is measured,
not asserted. See `01`, scope line.

**A3. Synchronous deployment.** All firms retrain on a common clock with a
common cadence `K`. Asynchronous clocks are named as an extension, not
attempted.

**A4. One shared environment.** Firms couple through a single pool with a
scalar spillover `kappa`. Heterogeneous pairwise spillover `kappa_ij` folds into
`R` only when it is separable, which is stated rather than assumed away.

**A5. The common mode binds.** Differential modes have `|slope| = m_1(1-kappa)`,
which is below one whenever `m_1 < 1`. So every stability statement in the paper
is a statement about the common mode. This is checked, not assumed, in each
note. It is **not universal**: it holds when `R` has nonnegative entries, where
Perron-Frobenius puts the leading eigenvector in the nonnegative orthant, and
fails under anti-alignment. Shared vendors and shared corpora produce positive
alignment, so the realistic regime satisfies it. Proof and the simplex
counterexample in [`derivations/01`](derivations/01-alignment-spectrum.md),
Section 4. Under lazy retraining (Theorem 2) the assumption is not needed at all,
because the binding mode is placed at `lambda_max` by monotonicity rather than by
sign pattern; see [`derivations/03`](derivations/03-cadence-composition.md),
Proposition 9.

**Two bounds worth stating once.** `lambda_max(R) >= 1` for any alignment matrix,
so `N_eff >= 1` and `rho(J) >= m_1`: interaction never stabilizes a market below
what its members achieve alone. And `lambda_max(R) >= 1 + (N-1) * mean`, so a
mean-similarity diversity index always under-states systemic risk, never
over-states it. Both proved in [`derivations/01`](derivations/01-alignment-spectrum.md).

## The one substitution

Everything in the paper reduces to

```
   m_N  =  N_eff * m_1 ,       N_eff  =  1 + kappa ( lambda_max(R) - 1 ) ,
```

with the supply-chain specialization `lambda_max(R) -> 1 + s(N-1)`, hence

```
   m_N  =  m_1 ( 1 + kappa * s * (N - 1) ) .
```

Results 2, 3 and 4 are stated in `m_N` and therefore inherit `s` for free. That
inheritance is the reason the two predecessor drafts were merged rather than
chosen between, and it is what every "what the merge adds" paragraph in the
paper is pointing at.

## Inherited base result

REFLEX derives, for `N` symmetric dealers sharing one pool of informed flow,

```
   J  =  -m_1 [ (1 - kappa) I  +  kappa 1 1' ] ,
```

with a common mode at `-m_1(1 + kappa(N-1))` and differential modes at
`-m_1(1 - kappa)`. Measured in a genuine shared-pool simulator: amplification
`1.74x` at `N = 2` and `3.16x` at `N = 3` against predicted `2` and `3`.
[VERIFIED, base result]

This paper's generalization replaces `1 1'` with `R`:

```
   J  =  -m_1 [ (1 - kappa) I  +  kappa R ] .
```

The base result is the `R = 1 1'` corner. Every claim in `01` through `04` is
built on this one replacement.
