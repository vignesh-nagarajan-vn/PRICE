import CreditCert.TakeUp
import CreditCert.Secant
import CreditCert.Certificate
import CreditCert.Adoption
import CreditCert.Confidence
import CreditCert.Indistinguishable

/-!
# Rate setting in lending

The lending results of the paper, for profit per applicant `Φ(s) = (s - ψ) a(s)` (that is, `K = 0`):
a flatter believed slope prices too high; a linear take-up curve fits any data collected at a single rate,
so such data cannot certify a change; rate cuts are safely testable and rate increases are not; certificates
for rate cuts survive adverse selection and those for increases need a bound on how fast the break-even
spread rises; take-up of borrowers who compare several quotes inherits the shape of one comparison; concave
stretches give interpolation bounds; and acceptance indicators are sub-Gaussian with constant `1/4`, which gives
the confidence event with no assumed noise bound (`BernoulliKL.lean` gives the sharper relative-entropy form).
-/

namespace CreditCert

open MeasureTheory ProbabilityTheory Set
open scoped ENNReal NNReal

/-- Profit per applicant when no part of profit is known exactly. -/
theorem Phi_zero (a : ℝ → ℝ) (ψ s : ℝ) : Phi (fun _ => 0) a ψ s = (s - ψ) * a s := by
  simp [Phi]

/-! ## A flatter believed slope prices too high -/

/-- If the lender's model agrees with the true take-up at `b`, makes `b` its profit-maximizing rate, and has a
flatter slope at `b` than the true curve, then a slightly lower rate earns strictly more. -/
theorem flatter_slope_prices_too_high {a : ℝ → ℝ} {ψ b a' am am' : ℝ}
    (ha : HasDerivAt a a' b) (hlevel : am = a b) (hfoc : am + (b - ψ) * am' = 0)
    (hslope : a' < am') (hψ : ψ < b) :
    ∀ᶠ h in nhdsWithin b (Set.Iio b), Phi (fun _ => 0) a ψ b < Phi (fun _ => 0) a ψ h := by
  have hd : HasDerivAt (Phi (fun _ => 0) a ψ) (0 + a b + (b - ψ) * a') b :=
    hasDerivAt_Phi (hasDerivAt_const b (0 : ℝ)) ha
  have hneg : 0 + a b + (b - ψ) * a' < 0 := by
    have h1 : (b - ψ) * a' < (b - ψ) * am' := mul_lt_mul_of_pos_left hslope (sub_pos.mpr hψ)
    linarith
  exact eventually_lt_of_deriv_neg hd hneg

/-! ## A linear take-up curve fits any single-rate data -/

theorem linFlow_convexOn (ψ b ab : ℝ) : ConvexOn ℝ Set.univ (linFlow ψ b ab) :=
  chordFloor_convexOn b (2 * b - ψ) ab 0

theorem linFlow_antitone {ψ b ab : ℝ} (hψ : ψ < b) (hab : 0 ≤ ab) : Antitone (linFlow ψ b ab) :=
  chordFloor_antitone (by linarith) hab

theorem linFlow_nonneg (ψ b ab s : ℝ) : 0 ≤ linFlow ψ b ab s :=
  chordFloor_nonneg b (2 * b - ψ) ab 0 s

theorem linFlow_at {ψ b ab : ℝ} (hab : 0 ≤ ab) : linFlow ψ b ab b = ab :=
  chordFloor_left hab

private theorem linFlow_eq {ψ b ab s : ℝ} (hψ : ψ < b) :
    linFlow ψ b ab s = max (ab * ((2 * b - ψ) - s) / (b - ψ)) 0 := by
  have hc : b - ψ ≠ 0 := (sub_pos.mpr hψ).ne'
  unfold linFlow chordFloor
  congr 1
  rw [show (2 * b - ψ) - b = b - ψ by ring]
  field_simp
  ring

/-- Under the linear curve, profit falls quadratically away from `b` on the linear part. -/
theorem linFlow_profit_gap {ψ b ab h : ℝ} (hψ : ψ < b) (hab : 0 ≤ ab) (hh2 : h ≤ 2 * b - ψ) :
    (b - ψ) * ab - (h - ψ) * linFlow ψ b ab h = ab * (h - b) ^ 2 / (b - ψ) := by
  have hpos : 0 < b - ψ := sub_pos.mpr hψ
  rw [linFlow_eq hψ, max_eq_left (div_nonneg (mul_nonneg hab (by linarith)) hpos.le)]
  field_simp
  ring

/-- Under the linear curve, `b` is the unique profit-maximizing rate. -/
theorem linFlow_strict_max {ψ b ab h : ℝ} (hψ : ψ < b) (hab : 0 < ab) (hne : h ≠ b) :
    Phi (fun _ => 0) (linFlow ψ b ab) ψ h < Phi (fun _ => 0) (linFlow ψ b ab) ψ b := by
  rw [Phi_zero, Phi_zero, linFlow_at hab.le]
  have hpos : 0 < b - ψ := sub_pos.mpr hψ
  by_cases h2 : h ≤ 2 * b - ψ
  · have hgap := linFlow_profit_gap hψ hab.le h2
    have hsq : 0 < (h - b) ^ 2 := lt_of_le_of_ne (sq_nonneg _) (Ne.symm (pow_ne_zero 2 (sub_ne_zero.mpr hne)))
    have hq : 0 < ab * (h - b) ^ 2 / (b - ψ) := div_pos (mul_pos hab hsq) hpos
    linarith
  · have hnum : ab * ((2 * b - ψ) - h) ≤ 0 := by nlinarith
    have hz : linFlow ψ b ab h = 0 := by
      rw [linFlow_eq hψ]
      exact max_eq_right (div_nonpos_iff.mpr (Or.inr ⟨hnum, hpos.le⟩))
    rw [hz, mul_zero]
    exact mul_pos hpos hab

/-- **No certificate from single-rate data.**  If the data collected at the rate `b` depend on the take-up
curve only through its value at `b`, every rule whose improvement claims are false with probability at most `α`
under every nonnegative, nonincreasing, convex curve claims an improvement with probability at most `α` under
the true curve, whatever the data set and in particular whatever the sample size. -/
theorem no_certificate_single_rate {Ω : Type*} [MeasurableSpace Ω]
    (law : (ℝ → ℝ) → Measure Ω) {b ψ : ℝ}
    (hlaw : ∀ σ σ' : ℝ → ℝ, σ b = σ' b → law σ = law σ')
    (rule : Ω → Option ℝ) {I : Set ℝ} (cls : (ℝ → ℝ) → Prop) {α : ℝ≥0∞}
    (hvalid : ∀ σ, cls σ → law σ {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b ∧
        Phi (fun _ => 0) σ ψ h ≤ Phi (fun _ => 0) σ ψ b} ≤ α)
    (hcls : ∀ σ : ℝ → ℝ, ConvexOn ℝ Set.univ σ → Antitone σ → (∀ x, 0 ≤ σ x) → cls σ)
    {a : ℝ → ℝ} (hψ : ψ < b) (hab : 0 < a b) :
    law a {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b} ≤ α :=
  no_certificate_of_matching_curve law hlaw rule cls hvalid
    (hcls _ (linFlow_convexOn ψ b (a b)) (linFlow_antitone hψ hab.le) (linFlow_nonneg ψ b (a b)))
    (linFlow_at hab.le) (fun _ _ hne => linFlow_strict_max hψ hab hne)

/-! ## Take-up curves with values in `[0, 1]`: the monotone class -/

/-- The step curve: take-up `ab` at rates up to `b` and zero above. -/
noncomputable def stepTakeUp (b ab s : ℝ) : ℝ := if s ≤ b then ab else 0

theorem stepTakeUp_antitone {b ab : ℝ} (hab : 0 ≤ ab) : Antitone (stepTakeUp b ab) := by
  intro x y hxy
  unfold stepTakeUp
  by_cases hy : y ≤ b
  · have hx : x ≤ b := le_trans hxy hy
    simp [hx, hy]
  · by_cases hx : x ≤ b
    · simp [hx, hy, hab]
    · simp [hx, hy]

theorem stepTakeUp_mem {b ab : ℝ} (h0 : 0 ≤ ab) (h1 : ab ≤ 1) (s : ℝ) :
    0 ≤ stepTakeUp b ab s ∧ stepTakeUp b ab s ≤ 1 := by
  unfold stepTakeUp
  split_ifs <;> constructor <;> linarith

theorem stepTakeUp_at (b ab : ℝ) : stepTakeUp b ab b = ab := by
  simp [stepTakeUp]

/-- Under the step curve, `b` is the unique profit-maximizing rate. -/
theorem stepTakeUp_strict_max {ψ b ab h : ℝ} (hψ : ψ < b) (hab : 0 < ab) (hne : h ≠ b) :
    Phi (fun _ => 0) (stepTakeUp b ab) ψ h < Phi (fun _ => 0) (stepTakeUp b ab) ψ b := by
  rw [Phi_zero, Phi_zero, stepTakeUp_at]
  unfold stepTakeUp
  split_ifs with hh
  · have hlt : h - ψ < b - ψ := by
      have : h < b := lt_of_le_of_ne hh hne
      linarith
    exact mul_lt_mul_of_pos_right hlt hab
  · rw [mul_zero]
    exact mul_pos (sub_pos.mpr hψ) hab

/-- **No certificate from single-rate data, monotone class.**  If the data collected at `b` depend on the
take-up curve only through its value there, every rule whose improvement claims are false with probability at
most `α` under every nonincreasing take-up curve with values in `[0, 1]` claims an improvement with probability at
most `α` under the true curve, whatever the amount of data. -/
theorem no_certificate_monotone {Ω : Type*} [MeasurableSpace Ω]
    (law : (ℝ → ℝ) → Measure Ω) {b ψ : ℝ}
    (hlaw : ∀ σ σ' : ℝ → ℝ, σ b = σ' b → law σ = law σ')
    (rule : Ω → Option ℝ) {I : Set ℝ} (cls : (ℝ → ℝ) → Prop) {α : ℝ≥0∞}
    (hvalid : ∀ σ, cls σ → law σ {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b ∧
        Phi (fun _ => 0) σ ψ h ≤ Phi (fun _ => 0) σ ψ b} ≤ α)
    (hcls : ∀ σ : ℝ → ℝ, Antitone σ → (∀ x, 0 ≤ σ x ∧ σ x ≤ 1) → cls σ)
    {a : ℝ → ℝ} (hψ : ψ < b) (hab : 0 < a b) (hab1 : a b ≤ 1) :
    law a {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b} ≤ α :=
  no_certificate_of_matching_curve law hlaw rule cls hvalid
    (hcls _ (stepTakeUp_antitone hab.le) (stepTakeUp_mem hab.le hab1))
    (stepTakeUp_at b (a b)) (fun _ _ hne => stepTakeUp_strict_max hψ hab hne)

/-- Without a slope bound, a rate increase can lose all profit even among `[0, 1]`-valued nonincreasing curves. -/
theorem increase_worst_case_monotone {ψ b h ab : ℝ} (hbh : b < h) (h0 : 0 ≤ ab) (h1 : ab ≤ 1) :
    ∃ σ : ℝ → ℝ, Antitone σ ∧ (∀ x, 0 ≤ σ x ∧ σ x ≤ 1) ∧ σ b = ab ∧ σ h = 0 ∧
      Phi (fun _ => 0) σ ψ h - Phi (fun _ => 0) σ ψ b = -((b - ψ) * ab) := by
  have hnot : ¬ h ≤ b := not_le.mpr hbh
  refine ⟨stepTakeUp b ab, stepTakeUp_antitone h0, stepTakeUp_mem h0 h1, stepTakeUp_at b ab, ?_, ?_⟩
  · simp [stepTakeUp, hnot]
  · rw [Phi_zero, Phi_zero, stepTakeUp_at]
    simp [stepTakeUp, hnot]

/-! ## The convex class with values in `[0, 1]` -/

/-- On the admissible range the linear curve is at most twice its value at `b`. -/
theorem linFlow_le_two_mul {ψ b ab s : ℝ} (hψ : ψ < b) (hab : 0 ≤ ab) (hs : ψ ≤ s) :
    linFlow ψ b ab s ≤ 2 * ab := by
  rw [linFlow_eq hψ]
  apply max_le
  · rw [div_le_iff₀ (sub_pos.mpr hψ)]
    nlinarith
  · linarith

/-- **No certificate from single-rate data, convex class with values in `[0, 1]`.**  When take-up at `b` is at
most one half, the linear curve stays in `[0, 1]` on `[ψ, ∞)`, so the conclusion holds for every class that
contains the curves that are convex, nonincreasing and `[0, 1]`-valued on the admissible range. -/
theorem no_certificate_convex_capped {Ω : Type*} [MeasurableSpace Ω]
    (law : (ℝ → ℝ) → Measure Ω) {b ψ : ℝ}
    (hlaw : ∀ σ σ' : ℝ → ℝ, σ b = σ' b → law σ = law σ')
    (rule : Ω → Option ℝ) {I : Set ℝ} (cls : (ℝ → ℝ) → Prop) {α : ℝ≥0∞}
    (hvalid : ∀ σ, cls σ → law σ {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b ∧
        Phi (fun _ => 0) σ ψ h ≤ Phi (fun _ => 0) σ ψ b} ≤ α)
    (hcls : ∀ σ : ℝ → ℝ, ConvexOn ℝ (Set.Ici ψ) σ → AntitoneOn σ (Set.Ici ψ) →
      (∀ x ∈ Set.Ici ψ, 0 ≤ σ x ∧ σ x ≤ 1) → cls σ)
    {a : ℝ → ℝ} (hψ : ψ < b) (hab : 0 < a b) (hhalf : a b ≤ 1 / 2) :
    law a {ω | ∃ h ∈ I, rule ω = some h ∧ h ≠ b} ≤ α :=
  no_certificate_of_matching_curve law hlaw rule cls hvalid
    (hcls _ ((linFlow_convexOn ψ b (a b)).subset (Set.subset_univ _) (convex_Ici ψ))
      ((linFlow_antitone hψ hab.le).antitoneOn _)
      (fun x hx => ⟨linFlow_nonneg ψ b (a b) x,
        by linarith [linFlow_le_two_mul hψ hab.le (Set.mem_Ici.mp hx)]⟩))
    (linFlow_at hab.le) (fun _ _ hne => linFlow_strict_max hψ hab hne)

/-- **Convexity with a cap is a slope bound.**  If take-up is convex on `[ψ, h]` with `a(ψ) ≤ 1` and
`ψ < b ≤ h`, then `Φ(h) - Φ(b) ≥ (h - b)(2 a(b) - 1) - (1 - a(b)) (h - b)² / (b - ψ)`.  When `a(b) > 1/2` the bound
is positive for small increases, so data at `b` alone certify them. -/
theorem convex_cap_increase_gain {a : ℝ → ℝ} {ψ b h : ℝ} (hconv : ConvexOn ℝ (Set.Icc ψ h) a)
    (hψb : ψ < b) (hbh : b ≤ h) (hcap : a ψ ≤ 1) :
    (h - b) * (2 * a b - 1) - (1 - a b) * (h - b) ^ 2 / (b - ψ) ≤
      Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  have hψh : ψ < h := lt_of_lt_of_le hψb hbh
  have hD : 0 < h - ψ := sub_pos.mpr hψh
  have hc : 0 < b - ψ := sub_pos.mpr hψb
  have hu : 0 ≤ h - b := sub_nonneg.mpr hbh
  have hψ_mem : ψ ∈ Set.Icc ψ h := ⟨le_rfl, hψh.le⟩
  have hh_mem : h ∈ Set.Icc ψ h := ⟨hψh.le, le_rfl⟩
  have hθ0 : 0 ≤ (h - b) / (h - ψ) := div_nonneg hu hD.le
  have hθ1 : 0 ≤ (b - ψ) / (h - ψ) := div_nonneg hc.le hD.le
  have hsum : (h - b) / (h - ψ) + (b - ψ) / (h - ψ) = 1 := by
    field_simp
    ring
  have key := hconv.2 hψ_mem hh_mem hθ0 hθ1 hsum
  have hpt : ((h - b) / (h - ψ)) • ψ + ((b - ψ) / (h - ψ)) • h = b := by
    simp only [smul_eq_mul]
    field_simp
    ring
  rw [hpt] at key
  simp only [smul_eq_mul] at key
  have key2 : a b * (h - ψ) ≤ (h - b) * a ψ + (b - ψ) * a h := by
    have h0 := mul_le_mul_of_nonneg_right key hD.le
    have e : ((h - b) / (h - ψ) * a ψ + (b - ψ) / (h - ψ) * a h) * (h - ψ)
        = (h - b) * a ψ + (b - ψ) * a h := by
      field_simp
    linarith
  have h1 : (h - b) * a ψ ≤ (h - b) * 1 := mul_le_mul_of_nonneg_left hcap hu
  have h2 : a b * (h - ψ) - (h - b) ≤ (b - ψ) * a h := by linarith
  have h3 : (h - ψ) * (a b * (h - ψ) - (h - b)) ≤ (h - ψ) * ((b - ψ) * a h) :=
    mul_le_mul_of_nonneg_left h2 hD.le
  rw [Phi_zero, Phi_zero]
  have e2 : (h - b) * (2 * a b - 1) - (1 - a b) * (h - b) ^ 2 / (b - ψ)
      = ((h - b) * (2 * a b - 1) * (b - ψ) - (1 - a b) * (h - b) ^ 2) / (b - ψ) := by
    field_simp
  rw [e2, div_le_iff₀ hc]
  nlinarith [h3]

/-! ## Rate cuts are safely testable; rate increases are not -/

/-- A rate cut from `b` to `h` loses at most `(b - h) U_b` per applicant, for any nonincreasing curve. -/
theorem rate_cut_loss {a : ℝ → ℝ} {ψ h b Ub : ℝ} (hψ : ψ ≤ h) (hhb : h ≤ b) (hmono : a b ≤ a h)
    (hUb : a b ≤ Ub) : -((b - h) * Ub) ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  have h0 := monotone_left_gain (K := fun _ => (0 : ℝ)) (ψ := ψ) hψ hhb hmono hUb
  simp only [sub_self, zero_sub] at h0
  linarith

/-- A cut of size at most `ℓ / U_b` stays within the budget `ℓ`. -/
theorem cut_pilot_within_budget {ℓ d Ub : ℝ} (hU : 0 < Ub) (hd : d ≤ ℓ / Ub) : d * Ub ≤ ℓ :=
  (le_div_iff₀ hU).mp hd

/-- **Cut pilots stay within the budget.**  A cut of at most `ℓ / U_b` below the incumbent rate loses at most `ℓ`
per applicant, for every nonincreasing take-up curve with `a(b) ≤ U_b`. -/
theorem cut_pilot_safe {a : ℝ → ℝ} {ψ h b Ub ℓ : ℝ} (hU : 0 < Ub) (hψ : ψ ≤ h) (hhb : h ≤ b)
    (hd : b - h ≤ ℓ / Ub) (hmono : a b ≤ a h) (hUb : a b ≤ Ub) :
    -ℓ ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  have h1 := rate_cut_loss hψ hhb hmono hUb
  have h2 := cut_pilot_within_budget hU hd
  linarith

/-- Cutting the margin `b - ψ` by a fraction `f` loses at most the fraction `f` of `(b - ψ) U_b`, an upper
bound on the incumbent's profit per applicant. -/
theorem cut_fraction_loss {a : ℝ → ℝ} {ψ b Ub f : ℝ} (hf0 : 0 ≤ f) (hf1 : f ≤ 1) (hψb : ψ ≤ b)
    (hmono : a b ≤ a (b - f * (b - ψ))) (hUb : a b ≤ Ub) :
    -(f * ((b - ψ) * Ub)) ≤
      Phi (fun _ => 0) a ψ (b - f * (b - ψ)) - Phi (fun _ => 0) a ψ b := by
  have hm : 0 ≤ b - ψ := sub_nonneg.mpr hψb
  have hψh : ψ ≤ b - f * (b - ψ) := by nlinarith
  have hhb : b - f * (b - ψ) ≤ b := by nlinarith
  have h1 := rate_cut_loss hψh hhb hmono hUb
  have e : (b - (b - f * (b - ψ))) * Ub = f * ((b - ψ) * Ub) := by ring
  rw [e] at h1
  exact h1

/-- Without a bound on the slope, a rate increase can lose all profit: some nonnegative, nonincreasing, convex
curve agrees with the data at `b` and is zero at the higher rate. -/
theorem increase_worst_case {ψ b h ab : ℝ} (hbh : b < h) (hab : 0 ≤ ab) :
    ∃ σ : ℝ → ℝ, ConvexOn ℝ Set.univ σ ∧ Antitone σ ∧ (∀ x, 0 ≤ σ x) ∧ σ b = ab ∧ σ h = 0 ∧
      Phi (fun _ => 0) σ ψ h - Phi (fun _ => 0) σ ψ b = -((b - ψ) * ab) := by
  refine ⟨chordFloor b h ab 0, chordFloor_convexOn b h ab 0, chordFloor_antitone hbh hab,
    chordFloor_nonneg b h ab 0, chordFloor_left hab, chordFloor_right hbh le_rfl, ?_⟩
  rw [Phi_zero, Phi_zero, chordFloor_right hbh le_rfl, chordFloor_left hab]
  ring

/-- With a known bound `η` on how fast take-up can fall, the loss of a rate increase is bounded. -/
theorem increase_with_slope_bound {a : ℝ → ℝ} {ψ b h η : ℝ} (hψ : ψ ≤ h)
    (hslope : a b - η * (h - b) ≤ a h) :
    (h - b) * a b - η * (h - b) * (h - ψ) ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  rw [Phi_zero, Phi_zero]
  have h1 := mul_le_mul_of_nonneg_left hslope (sub_nonneg.mpr hψ)
  nlinarith [h1]

/-! ## Two rules of Theorem "certified gain" with confidence limits -/

/-- A slope bound turns a lower confidence limit at `x ≤ h` into a lower bound at `h`. -/
theorem slope_lower {a : ℝ → ℝ} {x h η Lx : ℝ} (hslope : a x - η * (h - x) ≤ a h) (hL : Lx ≤ a x) :
    Lx - η * (h - x) ≤ a h := by
  linarith

/-- Rule (c): the slope bound for an increase, with a lower confidence limit at the incumbent. -/
theorem increase_with_slope_bound_lower {a : ℝ → ℝ} {ψ b h η Lb : ℝ} (hψ : ψ ≤ h) (hbh : b ≤ h)
    (hslope : a b - η * (h - b) ≤ a h) (hLb : Lb ≤ a b) :
    (h - b) * Lb - η * (h - b) * (h - ψ) ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  have h1 := increase_with_slope_bound hψ hslope
  have h2 : (h - b) * Lb ≤ (h - b) * a b := mul_le_mul_of_nonneg_left hLb (sub_nonneg.mpr hbh)
  linarith

/-! ## A risk budget set as a share of the incumbent's profit -/

/-- The budget `ρ (b - ψ) L_b`, computed from a lower confidence limit `L_b ≤ a(b)`, is at most the share `ρ` of
the incumbent's true profit per quote. -/
theorem budget_rel_le {a : ℝ → ℝ} {ψ b L ρ : ℝ} (hb : ψ ≤ b) (hρ : 0 ≤ ρ) (hL : L ≤ a b) :
    ρ * ((b - ψ) * L) ≤ ρ * Phi (fun _ => 0) a ψ b := by
  rw [Phi_zero]
  exact mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hL (sub_nonneg.mpr hb)) hρ

/-- If incumbents never get worse and every quoted rate earns at least the share `1 - ρ` of the current
incumbent's profit, every quoted rate earns at least the share `1 - ρ` of the starting profit. -/
theorem quoted_ge_start_rel {Φ : ℝ → ℝ} {inc q : ℕ → ℝ} {ρ : ℝ} (hρ : ρ ≤ 1)
    (hadopt : ∀ t, Φ (inc t) ≤ Φ (inc (t + 1))) (htrial : ∀ t, (1 - ρ) * Φ (inc t) ≤ Φ (q t)) (t : ℕ) :
    (1 - ρ) * Φ (inc 0) ≤ Φ (q t) := by
  have h1 : Φ (inc 0) ≤ Φ (inc t) := incumbent_monotone hadopt (Nat.zero_le t)
  exact (mul_le_mul_of_nonneg_left h1 (by linarith)).trans (htrial t)

/-! ## The anytime guarantee, assembled -/

/-- **Anytime guarantee, deterministic part.**  `inc t` is the incumbent rate and `q t` the quoted rate at quote
`t`.  Suppose that all intervals contain the true take-up (`L t x ≤ a x ≤ U t x`, the confidence event), that the
incumbent changes only when the direct test `(c - ψ) L_c - (b - ψ) U_b > 0` passes, and that every quoted rate
has a true gain of at least minus the budget `ρ (b - ψ) L_b` (which a valid certificate `G ≥ -ℓ` ensures).
Then the incumbent's profit never falls, and every quote earns at least the share `1 - ρ` of the starting
profit. -/
theorem anytime_trace {a : ℝ → ℝ} {ψ ρ : ℝ} {inc q : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (hψ : ∀ t, ψ ≤ inc t)
    (hint : ∀ t x, L t x ≤ a x ∧ a x ≤ U t x)
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (hpilot : ∀ t, -(ρ * ((inc t - ψ) * L t (inc t))) ≤
      Phi (fun _ => 0) a ψ (q t) - Phi (fun _ => 0) a ψ (inc t)) :
    (∀ t, Phi (fun _ => 0) a ψ (inc t) ≤ Phi (fun _ => 0) a ψ (inc (t + 1))) ∧
      (∀ t, (1 - ρ) * Phi (fun _ => 0) a ψ (inc 0) ≤ Phi (fun _ => 0) a ψ (q t)) := by
  have hstep : ∀ t, Phi (fun _ => 0) a ψ (inc t) ≤ Phi (fun _ => 0) a ψ (inc (t + 1)) := by
    intro t
    rcases hadopt t with h | h
    · rw [h]
    · have hpos : 0 < (fun _ : ℝ => (0 : ℝ)) (inc (t + 1)) + (inc (t + 1) - ψ) * L t (inc (t + 1))
          - (fun _ : ℝ => (0 : ℝ)) (inc t) - (inc t - ψ) * U t (inc t) := by
        simpa using h
      exact (adoption_sound (hψ (t + 1)) (hψ t) (hint t (inc (t + 1))).1 (hint t (inc t)).2 hpos).le
  have htrial : ∀ t, (1 - ρ) * Phi (fun _ => 0) a ψ (inc t) ≤ Phi (fun _ => 0) a ψ (q t) := by
    intro t
    have h1 := hpilot t
    have h2 := budget_rel_le (a := a) (hψ t) hρ0 (hint t (inc t)).1
    linarith
  exact ⟨hstep, quoted_ge_start_rel hρ1 hstep htrial⟩

/-- **Anytime guarantee, cumulative profit.**  Under the hypotheses of `anytime_trace`, if every budget used
is at most `ℓbar`, profit over the first `T` quotes is at least `T Φ(b₀)` minus `ℓbar` times the number of
quotes at a rate other than the incumbent. -/
theorem anytime_trace_cumulative {a : ℝ → ℝ} {ψ ρ ℓbar : ℝ} {inc q : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (hψ : ∀ t, ψ ≤ inc t)
    (hint : ∀ t x, L t x ≤ a x ∧ a x ≤ U t x)
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (hpilot : ∀ t, -(ρ * ((inc t - ψ) * L t (inc t))) ≤
      Phi (fun _ => 0) a ψ (q t) - Phi (fun _ => 0) a ψ (inc t))
    (hbar : ∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) (hℓ : 0 ≤ ℓbar) (T : ℕ) :
    (T : ℝ) * Phi (fun _ => 0) a ψ (inc 0)
        - ℓbar * (((Finset.range T).filter (fun t => q t ≠ inc t)).card : ℝ)
      ≤ ∑ t ∈ Finset.range T, Phi (fun _ => 0) a ψ (q t) := by
  have hstep := (anytime_trace hρ0 hρ1 hψ hint hadopt hpilot).1
  refine cumulative_profit_lower hℓ hstep (fun t => ?_) T
  have h1 := hpilot t
  have h2 := hbar t
  linarith

/-! ## Adverse selection -/

/-- If the break-even spread does not fall as the rate rises, a rate cut gains at least as much as the gain
computed with the break-even spread of the incumbent rate. -/
theorem adverse_selection_cut {a ψf : ℝ → ℝ} {h b : ℝ} (hψ : ψf h ≤ ψf b) (ha : 0 ≤ a h) :
    Phi (fun _ => 0) a (ψf b) h - Phi (fun _ => 0) a (ψf b) b ≤ (h - ψf h) * a h - (b - ψf b) * a b := by
  rw [Phi_zero, Phi_zero]
  nlinarith [mul_le_mul_of_nonneg_right hψ ha]

/-- **Adverse selection, rate increases.**  If the break-even spread rises by at most `κ` per point of rate
(`ψ(h) ≤ ψ(b) + κ (h - b)`), the gain of an increase computed with the incumbent's break-even spread overstates
the true gain by at most `κ (h - b) U_h`. -/
theorem adverse_selection_increase {a ψf : ℝ → ℝ} {h b κ Uh : ℝ} (hbh : b ≤ h) (hκ : 0 ≤ κ)
    (hψ : ψf h ≤ ψf b + κ * (h - b)) (ha0 : 0 ≤ a h) (hUh : a h ≤ Uh) :
    Phi (fun _ => 0) a (ψf b) h - Phi (fun _ => 0) a (ψf b) b - κ * (h - b) * Uh ≤
      (h - ψf h) * a h - (b - ψf b) * a b := by
  rw [Phi_zero, Phi_zero]
  have h1 : (ψf h - ψf b) * a h ≤ κ * (h - b) * a h :=
    mul_le_mul_of_nonneg_right (by linarith) ha0
  have h2 : κ * (h - b) * a h ≤ κ * (h - b) * Uh :=
    mul_le_mul_of_nonneg_left hUh (mul_nonneg hκ (sub_nonneg.mpr hbh))
  nlinarith

/-- For a rate cut, the gain computed with a larger break-even spread is smaller, so any upper bound on the
break-even spread gives a valid certificate. -/
theorem gain_antitone_in_psi {a : ℝ → ℝ} {ψ1 ψ2 h b : ℝ} (hψ : ψ1 ≤ ψ2) (hmono : a b ≤ a h) :
    Phi (fun _ => 0) a ψ2 h - Phi (fun _ => 0) a ψ2 b ≤ Phi (fun _ => 0) a ψ1 h - Phi (fun _ => 0) a ψ1 b := by
  rw [Phi_zero, Phi_zero, Phi_zero, Phi_zero]
  nlinarith [mul_le_mul_of_nonneg_left hmono (sub_nonneg.mpr hψ)]

/-! ## Borrowers who compare several quotes -/

/-- If the survival function `S` of competing quotes is convex and nonnegative on `D`, then so is the take-up
`S^K` of a borrower who holds `K` independent competing quotes and accepts ours only if it is the lowest. -/
theorem shopping_takeup_convexOn {S : ℝ → ℝ} {D : Set ℝ} (hS : ConvexOn ℝ D S)
    (h0 : ∀ x ∈ D, 0 ≤ S x) (K : ℕ) : ConvexOn ℝ D (fun s => S s ^ K) :=
  hS.pow (fun x hx => h0 x hx) K

/-- If `S` is nonincreasing and nonnegative on `D`, so is `S^K`. -/
theorem shopping_takeup_antitoneOn {S : ℝ → ℝ} {D : Set ℝ} (hS : AntitoneOn S D)
    (h0 : ∀ x ∈ D, 0 ≤ S x) (K : ℕ) : AntitoneOn (fun s => S s ^ K) D :=
  fun _ hx _ hy hxy => pow_le_pow_left₀ (h0 _ hy) (hS hx hy hxy) K

/-! ## Concave stretches -/

/-- On a stretch where take-up is concave, it lies above the chord of lower bounds at two anchors. -/
theorem concave_interp_lower {a : ℝ → ℝ} {S : Set ℝ} {x1 x2 h L1 L2 : ℝ} (hconc : ConcaveOn ℝ S a)
    (hx1 : x1 ∈ S) (hx2 : x2 ∈ S) (h1 : x1 ≤ h) (h2 : h ≤ x2) (h12 : x1 < x2)
    (hL1 : L1 ≤ a x1) (hL2 : L2 ≤ a x2) :
    ((x2 - h) * L1 + (h - x1) * L2) / (x2 - x1) ≤ a h := by
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  have key := chord_upper hconc.neg hx1 hx2 h1 h2 h12
  simp only [Pi.neg_apply] at key
  have key2 : -a h * (x2 - x1) ≤ -a x1 * (x2 - x1) + (-a x2 - -a x1) * (h - x1) := by
    have h3 := mul_le_mul_of_nonneg_right key hd.le
    rwa [add_mul, div_mul_cancel₀ _ hd.ne'] at h3
  rw [div_le_iff₀ hd]
  nlinarith [mul_le_mul_of_nonneg_left hL1 (sub_nonneg.mpr h2),
    mul_le_mul_of_nonneg_left hL2 (sub_nonneg.mpr h1)]

/-! ## Acceptance indicators -/

/-- **Hoeffding's lemma for acceptance indicators.** A random variable with values in `[0, 1]` is
sub-Gaussian about its mean with variance proxy `1/4`. -/
theorem bernoulli_subgaussian {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : Ω → ℝ} (hm : AEMeasurable X μ) (hb : ∀ᵐ ω ∂μ, X ω ∈ Set.Icc (0 : ℝ) 1) :
    HasSubgaussianMGF (fun ω => X ω - μ[X]) ((1 / 2 : ℝ≥0) ^ 2) μ := by
  have h := hasSubgaussianMGF_of_mem_Icc hm hb
  have hc : (‖(1 : ℝ) - 0‖₊ / 2 : ℝ≥0) = 1 / 2 := by simp
  rwa [hc] at h

/-- **Confidence event for acceptance indicators.** For independent acceptance indicators at each anchor, the
anytime intervals of radius `radius (1/2) N δ` hold simultaneously with probability at least `1 - α`. -/
theorem confidence_event_bernoulli {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, AEMeasurable (X j k) μ)
    (hb : ∀ j k, ∀ᵐ ω ∂μ, X j k ω ∈ Set.Icc (0 : ℝ) 1)
    (h_indep : ∀ j, iIndepFun (fun k ω => X j k ω - μ[X j k]) μ)
    {α : ℝ} (hα0 : 0 < α) (hα1 : α ≤ 1) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i) :
    μ {ω | ∃ j i, radius ((1 / 2 : ℝ≥0) : ℝ) (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), (X j k ω - μ[X j k])) / (N i : ℝ)|} ≤ ENNReal.ofReal α :=
  confidence_event (ζ := fun j k ω => X j k ω - μ[X j k]) (σ := 1 / 2) (by norm_num) h_indep
    (fun j k => bernoulli_subgaussian (hm j k) (hb j k)) hα0 hα1 N hN

/-- **Detection time for acceptance indicators.** With radius `(1/2) sqrt(2 log(2/δ) / n)` at both rates, a
sample size `n > 2 log(2/δ) m^2 / Δ^2` makes the total width `2 m r` smaller than the true gain `Δ`; together
with `certified_gain_lower` this makes the direct comparison positive. -/
theorem detection_bernoulli {δ Δ m n : ℝ} (hδ : 0 < δ) (hδ2 : δ < 2) (hΔ : 0 < Δ) (hm : 0 ≤ m)
    (hn : 2 * Real.log (2 / δ) * m ^ 2 / Δ ^ 2 < n) :
    2 * m * ((1 / 2) * Real.sqrt (2 * Real.log (2 / δ) / n)) < Δ := by
  apply detection_sample_size (by norm_num : (0 : ℝ) < 1 / 2) hδ hδ2 hΔ hm
  have h8 : 8 * (1 / 2 : ℝ) ^ 2 * Real.log (2 / δ) * m ^ 2 / Δ ^ 2
      = 2 * Real.log (2 / δ) * m ^ 2 / Δ ^ 2 := by ring
  rw [h8]
  exact hn

end CreditCert
