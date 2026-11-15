# Experiment specs

Six panels. Each maps to exactly one result, and the mapping is stated in the
paper so a referee can check coverage at a glance.

All experiments run in the base project's genuine `N`-dealer simulator, which
reduces bit-for-bit to the single-dealer market at `N = 1`. CPU-only,
deterministic from `(config, seed)`, common random numbers on paired probes,
every closed form certified numerically.

---

## 1. Amplification replication

**Anchors:** Section 3, the base result.

Sweep `N` in the homogeneous shared-pool market and reproduce the published
`1.74x` at `N = 2` and `3.16x` at `N = 3` against predicted `2` and `3`.

This is **external validation against a prior published run**, not a
self-consistency check, and that distinction is the reason it comes first.
Ships as a table, not a figure, because the comparison to the published numbers
is easier to check in a table.

**Cut status:** never cut.

---

## 2. The `(N, s)` phase diagram

**Tests:** Theorem 1.

Measured `m_N` over a grid of firms by shared-model fraction, against the
predicted boundary `m_1(1 + kappa*s*(N-1)) = 1`. Figure 1.

Requires the **heterogeneous-response environment**, which is the one piece of
new infrastructure this paper needs. Per-firm response parameters drawn to hit a
target `R`, including clustered topologies. Its acceptance test is that it
reduces to the existing homogeneous environment at `R = 1 1'`, and that
reduction is checked before any measurement is taken from it.

**Status: built.** [`environment/hetero_response_env.py`](environment/hetero_response_env.py),
32 acceptance tests passing, the reduction among them. Firms are placed at any
valid target alignment exactly rather than in distribution, so an `s` sweep moves
along the exact curve. Sweep with `exact=True`; the drawn decomposition exists to
demonstrate the `O(1/d)` concentration, not to run panels on.

**Companion panel:** the clustered topology, three aligned firms among ten,
showing instability at mean-alignment values a naive diversity index calls safe.
The numbers are worked in `../math/01-theorem1-alignment.md`: `N_eff = 2.60`
true against `1.48` by the mean index, so a market at `m_1 = 0.5` is unstable
and the mean index calls it safe with margin.

**Cut status:** the companion panel is fifth in the de-scope order. The main
panel stays.

---

## 3. The crowding-cadence frontier

**Tests:** Theorem 2.

Joint `K`-step loop stability over the `(N_eff, K)` grid, converge or diverge
per cell on common-random-number seeds, against predicted `K_max`. Figure 2.

Overlay `s` contours. Include the **critical-crowding column** where the window
closes entirely, at `m_N > (1+c)/(1-c)`, which is `m_N > 9` at `c = 0.8`.

State `c` in the caption. The worked table in the math note assumes `c = 0.8`
and the figure is not reproducible without it.

**Cut status:** stays.

---

## 4. Herd immunity

**Tests:** Theorem 3.

Mixed markets at corrected fractions `rho = 0, 1/N, ..., 1` in an `m_N > 1`
regime, against the predicted `rho*`. Figure 3.

**New in kind:** the corrected loop (`perfgd_structural`) has only ever been run
single-dealer. This is the first time it runs inside the `N`-dealer game. Either
outcome is a result.

**Sweep at the realized `gamma_ratio`, never at the strong-correction limit.**
The limit under-states the spectral radius, so a panel run at the limit inherits
its optimism and will report stability the market does not have. Plot the exact
threshold at the simulated `gamma_PO` alongside the limit; the gap between them is
a result, not an error bar. See
[`../math/derivations/04-mixed-market-secular.md`](../math/derivations/04-mixed-market-secular.md),
Section 6.

**The threshold in whole firms is `N - ceil(N_c(s)) + 1`,** not `ceil(rho* N)`.
The two differ when `N_c` is an integer, and one firm is several percentage
points at the `N` this panel runs at.

**Companion diagnostic:** private P&L of corrected against blind firms,
exhibiting the public-good structure directly. Fourth in the de-scope order.

**Cut status:** never cut. The main panel is the paper's core claim.

---

## 5. The substitution frontier

**Tests:** Theorem 3, the synthesis result.

The `(rho, s)` iso-stability curve, measured against predicted. Figure 4.

**This is the headline figure and the one that goes on the poster.** It is the
paper's most policy-legible object: it says a regulator facing an unstable
market of adaptive models has two interchangeable instruments and can price them
against each other.

Protected time in the build plan. Nothing else is scheduled against it.

**Cut status:** never cut.

---

## 6. Over-adaptation

**Tests:** Theorem 4.

Decentralized against socially optimal aggressiveness on a small grid, plus the
wedge's comparative statics in `N`, `kappa` and `s`. Figure 5.

**Built 19 Aug 2026, at `[DRY RUN]`.** `panel6_over_adaptation` solves both
first-order conditions by bisection with `m_N` read from the reference
environment's realized dynamics rather than from the closed form, so the
over-adaptation verdict is a property of the simulated market. 12 configurations,
zero rows contradicting Corollary 4.2, the fee implementing the social optimum to
`1.7e-13`, and the degenerate `N = 1` row showing exactly zero gap.
`panel6b_comparative_statics` evaluates Corollary 4.1 and Proposition 12 in
closed form.

**It cannot reach `[MEASURED]`.** The order-flow simulator has no aggressiveness
choice variable and no welfare object, so the panel's welfare layer has no
counterpart there. This is a different situation from panels 2 to 5, whose
`[MEASURED]` route existed and was closed by the port gate.

**Cut status:** second in the de-scope order. If cut, Theorem 4 ships as theory
with no panel, which is acceptable because the theorem is the contribution and
the panel is the illustration.

---

## Appendix: the supervision panel

PC1 variance share and lag-1 autocorrelation of cross-sectional spread
co-movement on the 212-CUSIP panel, 1990 to 2026, overlaid on the model-implied
fragility index.

**With a placebo** on Treasury and macro series, where no dealer-model channel
exists. Run it and report it whatever it shows.

Framed as consistency evidence, never identification. Co-movement is
macro-contaminated and the data is public proxies, not trade-level TRACE.

**Cut status:** first in the de-scope order, along with the whole supervision
section.

---

## Protocol rules

Inherited from the base project and non-negotiable. Violating any of these
silently invalidates a panel.

- Sweep the feedback gain, never the confounded adversariality parameter.
- Probe at the operating spread, with common random numbers.
- Multi-dealer runs can saturate the informed-flow cap. Scale the liquidity
  boost down per the environment's guidance and never de-saturate silently.
- Beyond-boundary probe readings are diagnostics, not slopes.

## Coverage table

Reproduced in the paper so a referee can check it at a glance.

| Result | Panel |
|---|---|
| Base result (Section 3) | 1 |
| Theorem 1 | 2, plus the clustered companion |
| Theorem 2 | 3 |
| Theorem 3 | 4 and 5 |
| Theorem 4 | 6 |
| Supervision | appendix, with placebo |
