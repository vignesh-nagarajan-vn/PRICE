# Heterogeneous-response environment

[`hetero_response_env.py`](hetero_response_env.py) places firms at chosen
response directions and lets them retrain against a shared pool. Experiments 2,
4 and 5 run against it, including the substitution frontier, which is never cut.

Acceptance tests:
[`../certificates/verify_hetero_env.py`](../certificates/verify_hetero_env.py),
32 checks, all passing.

```bash
python herd-immunity/ml-contributions/certificates/verify_hetero_env.py
```

## What it is, and what it is not

It realizes the **response geometry** of the model: firms with chosen response
Jacobians, a shared pool carrying their combined distortion, and each firm
sensing that pool through its own channel. That is the mechanism derived in
[`../../math/derivations/01-alignment-spectrum.md`](../../math/derivations/01-alignment-spectrum.md),
Section 1.

It is **not** the base project's order-flow simulator. There is no informed
flow, no spread, no inventory, no microstructure of any kind. Panels that need
those run in the simulator. This is the reference the simulator's heterogeneous
extension is checked against, and it is where a closed form is falsified cheaply
before anyone spends a simulator run on it.

## The reduction test

The acceptance test the experiment spec names, and the one that runs first: at
`R = 1 1'` the environment must reproduce the base project's homogeneous
market. It does, on three counts. The measured alignment is exactly `1 1'`,
`n_eff` is exactly `1 + kappa(N-1)`, and the built Jacobian equals
`-m_1[(1-kappa)I + kappa 1 1']` to `1e-10`. The published amplification anchors
`N_eff = 2` and `3` at `N = 2, 3` come out, and the market reduces to a single
firm at `N = 1`.

## Why the Jacobian is built rather than evaluated

`jacobian()` differentiates the actual retraining map. `predicted_jacobian()`
evaluates the closed form. They are separate methods and the acceptance test
compares them, because a market that evaluates the formula it is supposed to
test proves nothing. Agreement is `1.3e-15` over 300 markets, and holds with
heterogeneous moduli.

## Placing firms exactly

`response_jacobians_for_R(R, d, rng)` returns Jacobians whose *measured*
alignment is the target to `1e-10`, for any valid alignment matrix. It factors
`R = L L'` by eigendecomposition rather than Cholesky, because the topologies
that matter most are singular: the monoculture `1 1'` has rank one.

The realized `d` must satisfy `d*d >= N`, since `N` directions cannot be placed
in fewer dimensions. The guard raises rather than silently degrading.

Two ways to build a supply-chain market, and the difference matters. `exact=True`
places firms at the limit alignment `(1-s)I + s 1 1'`, so a sweep over `s` moves
along the exact curve. `exact=False` draws
`E_i = sqrt(s) E_shared + sqrt(1-s) Xi_i` and lets the alignment concentrate,
which is what a real supply chain does and which converges at `O(1/d)`, measured
at a log-log slope of `-0.90`. Sweeps use the exact placement; the drawn version
exists to show the concentration is real.

## Mixed markets

`mixed_market(...)` builds the Theorem 3 configuration: `n_blind` blind firms
carrying modulus `m_1`, the rest corrected and carrying `gamma_ratio * m_1`.
Correction changes a firm's gain, not its response direction, so the alignment is
untouched.

The environment reproduces the C18 finding end to end. At `N = 10`, `N_b = 6`,
`m_1 = 0.15`, `kappa = s = 1`, the strong-correction limit is stable and the same
market at `gamma_ratio = 0.6` is not. Sweep at the realized `gamma_ratio`, never
at the limit, or the panel will inherit the limit's optimism.

## The simulator port

[`HETERO-SIMULATOR-PORT-DESIGN.md`](HETERO-SIMULATOR-PORT-DESIGN.md) records the
modeling decision that lets the base project's order-flow simulator carry a
per-dealer response direction, which it has no concept of today. The mechanism
is a bond-space exposure profile per dealer, routed through both the
contribution to the informed pool and the sensing of it, so the coupling matrix
becomes `(1-kappa)I + kappa R` with `R` the Gram matrix of the profiles.

The skeleton is
[`../experiments/hetero_simulator_port.py`](../experiments/hetero_simulator_port.py).
Its one acceptance test is the reduction: at flat profiles it reproduces panel
1's published anchors bit for bit, relative error `0.00e+00` at `N = 1, 2, 3`.

```bash
"<base>/.venv/Scripts/python" herd-immunity/ml-contributions/experiments/hetero_simulator_port.py
```

**No heterogeneous sweep has been run.** Panels 2, 2b, 4 and 5 remain
`[DRY RUN]`. The design document's closing section lists what the mechanism does
not yet handle, and the second entry there, that the liquidity and impact
channels stay fully shared regardless of the profiles, is the one the first
heterogeneous run has to measure.
