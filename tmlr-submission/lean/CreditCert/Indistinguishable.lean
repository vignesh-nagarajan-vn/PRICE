import CreditCert.Adoption
import CreditCert.Confidence

/-!
# No certificate from data at a single rate

Covers the statistical half of Theorem "no certificate from single-rate data".  The data collected at the rate
`b` are modelled abstractly: `law σ` is the law of the data set when the take-up curve is `σ`, and it depends on
the curve only through its value `σ b`, as the law of acceptance indicators at `b` does.  A rule maps data to
`none` ("keep `b`") or to `some h` ("`h` beats `b`").  `no_certificate_single_rate` in `Credit.lean` supplies
the matching curve (`linFlow`).
-/

namespace CreditCert

open MeasureTheory

/-- If the law of the data depends on the take-up curve only through its value at `b`, a rule whose improvement
claims are false with probability at most `α` under every curve of a class claims an improvement with probability
at most `α` under any curve `τ` for which the class contains a curve `τt` with `τt b = τ b` that makes every other
rate strictly worse than `b`. -/
theorem no_certificate_of_matching_curve {Ω : Type*} [MeasurableSpace Ω]
    (law : (ℝ → ℝ) → Measure Ω) {b : ℝ}
    (hlaw : ∀ σ σ' : ℝ → ℝ, σ b = σ' b → law σ = law σ')
    (rule : Ω → Option ℝ) {K : ℝ → ℝ} {ψ : ℝ} {I : Set ℝ} (cls : (ℝ → ℝ) → Prop) {α : ENNReal}
    (hvalid : ∀ σ, cls σ →
      law σ {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b ∧ Phi K σ ψ h ≤ Phi K σ ψ b} ≤ α)
    {τ τt : ℝ → ℝ} (hcls : cls τt) (hb : τt b = τ b)
    (hopt : ∀ h ∈ I, h ≠ b → Phi K τt ψ h < Phi K τt ψ b) :
    law τ {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b} ≤ α := by
  rw [hlaw τ τt hb.symm]
  refine le_trans (measure_mono ?_) (hvalid τt hcls)
  rintro ω ⟨h, hI, hr, hne⟩
  exact ⟨h, hI, hr, hne, le_of_lt (hopt h hI hne)⟩

end CreditCert
