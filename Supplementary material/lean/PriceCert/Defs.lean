import Mathlib

/-!
# Definitions

A dealer quotes a half-spread `h`.

* `K h` is the part of expected profit the dealer can compute: benign flow and quadratic costs.
* `τ h` is the responsive flow at the quote `h`.  The dealer does not know this function.
* `ψ` is the cost the dealer bears per unit of responsive flow.

All statements in this development are about real functions of one real variable.
-/

namespace PriceCert

/-- Deployed profit `Φ(h) = K(h) + (h - ψ) τ(h)`. -/
def Phi (K τ : ℝ → ℝ) (ψ h : ℝ) : ℝ := K h + (h - ψ) * τ h

/-- Frozen profit `J(h; t) = K(h) + (h - ψ) t`: the profit a model predicts when it treats the
flow level `t` as fixed. -/
def J (K : ℝ → ℝ) (ψ h t : ℝ) : ℝ := K h + (h - ψ) * t

/-- Tangent surrogate at the base quote `b`, with flow level `τb` and flow slope `s` at the base:
`S_b(h) = K(h) + (h - ψ) (τb + s (h - b))`. -/
def tangentSurrogate (K : ℝ → ℝ) (ψ b τb s h : ℝ) : ℝ := K h + (h - ψ) * (τb + s * (h - b))

/-- The two-point extremal flow: the chord through `(x1, t1)` and `(x2, t2)` to the left of its
crossing with the level `t2`, and the constant `t2` to the right. -/
noncomputable def twoPoint (x1 x2 t1 t2 h : ℝ) : ℝ := max (t1 + (t2 - t1) / (x2 - x1) * (h - x1)) t2

/-- The chord through `(x1, t1)` and `(x2, t2)`, floored at zero. -/
noncomputable def chordFloor (x1 x2 t1 t2 h : ℝ) : ℝ := max (t1 + (t2 - t1) / (x2 - x1) * (h - x1)) 0

/-- Confidence radius after `n` samples at error level `δ` for noise of scale `σ`. -/
noncomputable def radius (σ : ℝ) (n : ℕ) (δ : ℝ) : ℝ := σ * Real.sqrt (2 * Real.log (2 / δ) / n)

/-- Error budget assigned to checkpoint `i` of anchor `j`, both counted from zero:
`α / ((j + 1) (j + 2) (i + 1) (i + 2))`. -/
noncomputable def budget (α : ℝ) (j i : ℕ) : ℝ :=
  α / (((j : ℝ) + 1) * ((j : ℝ) + 2) * (((i : ℝ) + 1) * ((i : ℝ) + 2)))

end PriceCert
