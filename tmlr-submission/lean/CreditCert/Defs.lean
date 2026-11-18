import Mathlib

/-!
# Definitions

A lender offers a rate spread `s` to approved applicants.

* `a s` is the take-up curve: the probability that an approved applicant accepts an offer at spread `s`.
  The lender does not know this function.
* `ψ` is the break-even spread: funding, servicing and expected credit loss per unit of balance.
* `K s` is any part of profit the lender can compute exactly; the paper uses `K = 0`, so that profit
  per applicant is `(s - ψ) a(s)`.

All statements in this development are about real functions of one real variable.
-/

namespace CreditCert

/-- Profit per applicant, `Φ(s) = K(s) + (s - ψ) a(s)`. -/
def Phi (K a : ℝ → ℝ) (ψ s : ℝ) : ℝ := K s + (s - ψ) * a s

/-- The two-point extremal curve: the chord through `(x1, t1)` and `(x2, t2)` to the left of its
crossing with the level `t2`, and the constant `t2` to the right. -/
noncomputable def twoPoint (x1 x2 t1 t2 h : ℝ) : ℝ := max (t1 + (t2 - t1) / (x2 - x1) * (h - x1)) t2

/-- The chord through `(x1, t1)` and `(x2, t2)`, floored at zero. -/
noncomputable def chordFloor (x1 x2 t1 t2 h : ℝ) : ℝ := max (t1 + (t2 - t1) / (x2 - x1) * (h - x1)) 0

/-- The take-up curve that is linear through `(b, ab)` with slope `-ab / (b - ψ)`, floored at zero.
Under it the rate `b` is the unique profit-maximizing rate. -/
noncomputable def linFlow (ψ b ab s : ℝ) : ℝ := chordFloor b (2 * b - ψ) ab 0 s

/-- Confidence radius after `n` samples at error level `δ` for noise of scale `σ`. -/
noncomputable def radius (σ : ℝ) (n : ℕ) (δ : ℝ) : ℝ := σ * Real.sqrt (2 * Real.log (2 / δ) / n)

/-- Error budget assigned to checkpoint `i` of anchor `j`, both counted from zero:
`α / ((j + 1) (j + 2) (i + 1) (i + 2))`. -/
noncomputable def budget (α : ℝ) (j i : ℕ) : ℝ :=
  α / (((j : ℝ) + 1) * ((j : ℝ) + 2) * (((i : ℝ) + 1) * ((i : ℝ) + 2)))

end CreditCert
