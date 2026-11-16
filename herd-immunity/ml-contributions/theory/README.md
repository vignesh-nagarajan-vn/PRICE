# Theory module

[`herd_theory.py`](herd_theory.py) holds every closed form the paper states.
Each experiment checks itself against this module rather than against its own
copy of the algebra, which is the whole reason it exists.

Acceptance tests:
[`../certificates/verify_theory_module.py`](../certificates/verify_theory_module.py),
50 checks, all passing.

```bash
python herd-immunity/ml-contributions/certificates/verify_theory_module.py
```

## What is here, and what is not

| Theorem | State |
|---|---|
| 1, alignment and `N_eff` | complete |
| 2, the cadence frontier | complete |
| 3, the mixed market | complete, including the exact two-block root |
| 4, the Pigouvian wedge | **only `stationary_variance` and `dV_dm`** |

`pigouvian_wedge` is deliberately absent. Theorem 4's welfare page is not
derived, and the standing rule is that nothing reaches the paper ahead of its
derivation. An acceptance test asserts its absence, so it cannot be added by
accident before `../../math/04-theorem4-wedge.md` is written.

## Placement

This is the reference implementation. It ships in the REFLEX repository
alongside the existing theory modules, following their naming and certificate
conventions rather than inventing new ones, and this copy is what that port is
checked against.

## Three functions that need their docstrings read

**`mean_alignment` and `n_eff_mean_index` are foils.** They exist so the paper
can show they are the wrong statistic. No stability function in the module calls
either one. The mean is a lower bound on `lambda_max`, never an approximation to
it, so every error it makes lets an unstable market pass.

**`rho_star` is the policy object, not the stability criterion.** The comparison
`rho > rho_star` mispredicts the all-blind market that is stable without any
correction, because the clamp at zero combined with a strict inequality excludes
`N_b = N`. Use `is_stable_mixed` for a verdict. An acceptance test confirms the
mispredictions are real rather than hypothetical, so the caution cannot be
mistaken for defensiveness.

**`is_stable_mixed` defaults to the strong-correction limit, which is
optimistic.** The limit under-states the radius, so pass the realized
`gamma_ratio` when the answer matters. See
[`../../math/derivations/04-mixed-market-secular.md`](../../math/derivations/04-mixed-market-secular.md),
Section 6.

## Conventions

numpy only, CPU only, deterministic. Every function is pure: same arguments give
the same result, no globals, no caching. Arguments outside their stated ranges
raise rather than returning a plausible number, because a silently wrong `kappa`
is the failure mode that survives to a figure.
