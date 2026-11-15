# PriceCert: Lean 4 formalization

Machine-checked mathematics for "Certified Safe Improvement of Self-Confirming Dealer Quotes".
Appendix B of the paper maps every result to the theorems below and lists the steps that are argued only
on paper.

## Files

| File | Theorems | Content |
|---|---|---|
| `PriceCert/Defs.lean` | 0 (7 definitions) | profit, frozen profit, tangent surrogate, extremal two-point flows, radius, confidence levels |
| `PriceCert/Model.lean` | 28 | self-confirming quotes are too wide, reservation-spread microfoundation, the exponential instance |
| `PriceCert/Minorant.lean` | 14 | tangent minorant, profit ascent, quadratic growth, argmax stability |
| `PriceCert/FixedPoint.lean` | 14 | fixed points, local rate, retraining slope, local contraction and repulsion |
| `PriceCert/Secant.lean` | 19 | chord bounds and two-anchor tightness |
| `PriceCert/Certificate.lean` | 9 | certified gain bounds and safe pilots |
| `PriceCert/Adoption.lean` | 12 | soundness of adoption and rejection, impossibility, detection time |
| `PriceCert/Confidence.lean` | 11 | confidence levels, union bound, sub-Gaussian concentration, confidence event |

Total: 107 theorems.

## Build

Toolchain `leanprover/lean4:v4.36.0-rc2` (see `lean-toolchain`) with Mathlib at tag `v4.36.0-rc2`
(see `lakefile.toml` and `lake-manifest.json`).

```bash
lake exe cache get     # download compiled Mathlib
lake build PriceCert
```

The build completes without errors. No file contains `sorry`, `admit`, an `axiom` declaration,
`native_decide` or `unsafe` code, and `#print axioms` reports only `propext`, `Classical.choice` and
`Quot.sound` for every theorem.
