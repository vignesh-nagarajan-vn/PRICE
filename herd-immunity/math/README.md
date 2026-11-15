# Math

Two layers. The numbered notes are per-theorem summaries: statement, anchors that
pin it, and the open issues. The `derivations/` folder holds the complete proofs
those notes summarize, each one paired with an assertion-based certificate under
`../ml-contributions/certificates/`. Settle the algebra here before any of it
reaches `../../archive/herd-immunity-v1/writing/`.

| File | Covers |
|---|---|
| [`00-notation.md`](00-notation.md) | Symbol table, standing assumptions, what is inherited from REFLEX |
| [`01-theorem1-alignment.md`](01-theorem1-alignment.md) | The alignment matrix `R`, `N_eff`, the supply-chain map, the heterogeneous-modulus scope line |
| [`02-theorem2-cadence.md`](02-theorem2-cadence.md) | `mu_N(K)`, the cadence window `K_max`, critical crowding |
| [`03-theorem3-herd-immunity.md`](03-theorem3-herd-immunity.md) | Mixed-market stability, `rho*(s)`, the substitution frontier |
| [`04-theorem4-wedge.md`](04-theorem4-wedge.md) | Stationary variance, the Pigouvian wedge, over-adaptation |
| [`05-supervision.md`](05-supervision.md) | Critical slowing down, the public-price estimator (deferred) |

## Derivations

| File | Proves | Certificate |
|---|---|---|
| [`derivations/01-alignment-spectrum.md`](derivations/01-alignment-spectrum.md) | The reduction lemma, `rho(J) = m_1 N_eff`, the anchors, the mean-index bound, heterogeneous moduli | `verify_theorem1_proof.py`, 123 checks |
| [`derivations/02-supply-chain-concentration.md`](derivations/02-supply-chain-concentration.md) | `r_ij -> s` as a probability bound rather than an expectation, and the spectral consequence | same file, block P7 |
| [`derivations/03-cadence-composition.md`](derivations/03-cadence-composition.md) | The inner-loop lemma, the joint `K`-step map, the frontier in both forms, critical crowding as a corollary | `verify_theorem2_cadence.py`, 59 checks |
| [`derivations/04-mixed-market-secular.md`](derivations/04-mixed-market-secular.md) | The exact two-block root, the limit's error direction, the imperfect-correction law and its critical efficacy | `verify_theorem3_herd_immunity.py`, 70 checks |

Theorem 4 has a note but no derivation. That is the next block of work, and it is
the only theorem still resting on a sketch.

## Standing rules

**All stability claims use the spectral form, never a mean.** Mean alignment
understates clustered alignment and, as `01` shows, does not even order
configurations correctly: the configuration minimizing mean alignment is not
the configuration minimizing `lambda_max(R)`. Two independent counterexamples
are recorded there.

**Anchors before proofs.** Every closed form is checked against at least two
independently derived limits before it is written into the paper. Where an
anchor in the plan of record fails, the note says so and the claims ledger
records the correction.

**Nothing is claimed beyond what is derived or measured at submission time.**
Status flags are `[VERIFIED]`, `[DERIVED]`, `[TO BUILD]`, `[DEFERRED]`, and
they mean what `../README.md` says they mean.

## Corrections to the plan of record

Recorded here so they are not lost between the plan and the paper.

| Where | Issue | Resolution |
|---|---|---|
| Plan Section 5, Theorem 1 anchors | "maximal diversity (simplex responses) gives `m_1(1-kappa)`" is not the spectral radius | The simplex configuration matches `m_1(1-kappa)` on one eigenvalue, not on `lambda_max`. Its spectral radius is `m_1(1 + kappa/(N-1))`. Verified numerically and **the plan of record has been corrected**. Detail in [`01`](01-theorem1-alignment.md), evidence in [`verify_theorem1_anchors.py`](../ml-contributions/certificates/verify_theorem1_anchors.py) |
| `00-notation.md`, symbol table | `N_eff` range given as `[1 - kappa, ...]` and `lambda_max(R)` as `[0, N]` | Both lower ends are unattainable. `tr R = N > 0` with nonnegative eigenvalues forces `lambda_max(R) >= 1`, hence `N_eff >= 1`. Table corrected. The economic content is worth keeping: interaction never stabilizes a market below what its members achieve alone. Proof in [`derivations/01`](derivations/01-alignment-spectrum.md), Corollaries 1.1 and 1.2 |
| `02-theorem2-cadence.md`, binding mode | The argument routes through the size of the differential modes, and inherits the Perron-Frobenius condition it does not need | Under lazy retraining `mu_i(K)` is strictly decreasing in `nu_i`, so the extreme sits at `lambda_max` for any sign pattern of `R`. Shorter and unconditional. [`derivations/03`](derivations/03-cadence-composition.md), Proposition 9 |
| Plan Section 7 and `03-theorem3-herd-immunity.md` | The strong-correction limit is assumed conservative, and the exact root sits third in the de-scope order | **The limit is optimistic.** The radius is nondecreasing in `gamma/gamma_PO`, so the limit under-states it and calls `11.8%` of random configurations stable that are not. The exact root has left the de-scope order and the plan of record is amended. [`derivations/04`](derivations/04-mixed-market-secular.md), Section 6 |
| `03-theorem3-herd-immunity.md`, criterion | `rho > rho*(s)` stated as the exact stability condition | Not exact: the clamp at zero with a strict inequality excludes the all-blind market that is stable without correction, on `134` of 4000 draws. `N_b < N_c(s)` is exact. [`derivations/04`](derivations/04-mixed-market-secular.md), Section 8 |
| `03-theorem3-herd-immunity.md`, integer threshold | Realized threshold given as `ceil(rho* N)` firms | `N - ceil(N_c) + 1`. The two differ by one when `N_c` is an integer. [`derivations/04`](derivations/04-mixed-market-secular.md), Section 9 |
