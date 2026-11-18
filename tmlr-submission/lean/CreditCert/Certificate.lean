import CreditCert.Secant

/-!
# Profit certificates

Covers the gain rules of Theorem "certified gain": the direct comparison, the envelope rule, the rule for rate
cuts and the two joint rules.  They are stated for profit `K(s) + (s - ψ) a(s)`; the lending results use `K = 0`.
-/

namespace CreditCert

open Set

/-! ## Rule (D): direct comparison at an anchor.  No shape assumption. -/

theorem direct_gain {K τ : ℝ → ℝ} {ψ a b La Ub : ℝ} (ha : ψ ≤ a) (hb : ψ ≤ b)
    (hLa : La ≤ τ a) (hUb : τ b ≤ Ub) :
    K a + (a - ψ) * La - K b - (b - ψ) * Ub ≤ Phi K τ ψ a - Phi K τ ψ b := by
  have h1 : (a - ψ) * La ≤ (a - ψ) * τ a := mul_le_mul_of_nonneg_left hLa (sub_nonneg.mpr ha)
  have h2 : (b - ψ) * τ b ≤ (b - ψ) * Ub := mul_le_mul_of_nonneg_left hUb (sub_nonneg.mpr hb)
  unfold Phi
  linarith

theorem direct_gain_upper {K τ : ℝ → ℝ} {ψ a b Ua Lb : ℝ} (ha : ψ ≤ a) (hb : ψ ≤ b)
    (hUa : τ a ≤ Ua) (hLb : Lb ≤ τ b) :
    Phi K τ ψ a - Phi K τ ψ b ≤ K a + (a - ψ) * Ua - K b - (b - ψ) * Lb := by
  have h1 : (a - ψ) * τ a ≤ (a - ψ) * Ua := mul_le_mul_of_nonneg_left hUa (sub_nonneg.mpr ha)
  have h2 : (b - ψ) * Lb ≤ (b - ψ) * τ b := mul_le_mul_of_nonneg_left hLb (sub_nonneg.mpr hb)
  unfold Phi
  linarith

/-! ## The envelope rule: any lower bound on take-up at `h` gives a lower bound on the gain. -/

theorem envelope_gain {K τ : ℝ → ℝ} {ψ h b τlow Ub : ℝ} (hψ : ψ ≤ h) (hb : ψ ≤ b)
    (hlow : τlow ≤ τ h) (hUb : τ b ≤ Ub) :
    K h - K b + (h - ψ) * τlow - (b - ψ) * Ub ≤ Phi K τ ψ h - Phi K τ ψ b := by
  have h1 : (h - ψ) * τlow ≤ (h - ψ) * τ h := mul_le_mul_of_nonneg_left hlow (sub_nonneg.mpr hψ)
  have h2 : (b - ψ) * τ b ≤ (b - ψ) * Ub := mul_le_mul_of_nonneg_left hUb (sub_nonneg.mpr hb)
  unfold Phi
  linarith

/-! ## Rule (ML): rate cuts -/

/-- Rule (ML).  A rate below the incumbent loses at most the incumbent's take-up times the rate
difference. -/
theorem monotone_left_gain {K τ : ℝ → ℝ} {ψ h b Ub : ℝ} (hψ : ψ ≤ h) (hhb : h ≤ b)
    (hmono : τ b ≤ τ h) (hUb : τ b ≤ Ub) :
    K h - K b - (b - h) * Ub ≤ Phi K τ ψ h - Phi K τ ψ b := by
  have h1 : (h - ψ) * τ b ≤ (h - ψ) * τ h := mul_le_mul_of_nonneg_left hmono (sub_nonneg.mpr hψ)
  have h2 : (b - h) * τ b ≤ (b - h) * Ub := mul_le_mul_of_nonneg_left hUb (sub_nonneg.mpr hhb)
  unfold Phi
  linarith

/-! ## The joint rules: the incumbent's take-up enters both the bound at the new rate and the comparison -/

/-- Three-point form of convexity: for `x ≤ y ≤ z` with `x < z`, the value at `y` lies below the
chord through `x` and `z`, written without division. -/
private lemma certificate_three_point {τ : ℝ → ℝ} {S : Set ℝ} {x y z : ℝ} (hconv : ConvexOn ℝ S τ)
    (hx : x ∈ S) (hz : z ∈ S) (hxy : x ≤ y) (hyz : y ≤ z) (hxz : x < z) :
    τ y * (z - x) ≤ τ x * (z - y) + τ z * (y - x) := by
  have hpos : 0 < z - x := sub_pos.mpr hxz
  have h1 : 0 ≤ (z - y) / (z - x) := div_nonneg (sub_nonneg.mpr hyz) hpos.le
  have h2 : 0 ≤ (y - x) / (z - x) := div_nonneg (sub_nonneg.mpr hxy) hpos.le
  have h3 : (z - y) / (z - x) + (y - x) / (z - x) = 1 := by
    rw [← add_div, div_eq_one_iff_eq hpos.ne']
    ring
  have h4 := hconv.2 hx hz h1 h2 h3
  have h5 : ((z - y) / (z - x)) • x + ((y - x) / (z - x)) • z = y := by
    rw [smul_eq_mul, smul_eq_mul, div_mul_eq_mul_div, div_mul_eq_mul_div, ← add_div,
      div_eq_iff hpos.ne']
    ring
  rw [h5, smul_eq_mul, smul_eq_mul] at h4
  calc τ y * (z - x)
      ≤ ((z - y) / (z - x) * τ x + (y - x) / (z - x) * τ z) * (z - x) :=
        mul_le_mul_of_nonneg_right h4 hpos.le
    _ = τ x * ((z - y) / (z - x) * (z - x)) + τ z * ((y - x) / (z - x) * (z - x)) := by ring
    _ = τ x * (z - y) + τ z * (y - x) := by
        rw [div_mul_cancel₀ _ hpos.ne', div_mul_cancel₀ _ hpos.ne']

/-- Rule (J-left).  New rate `h ≤ b`, second anchor `a > b`. -/
theorem joint_left_gain {K τ : ℝ → ℝ} {S : Set ℝ} {ψ h b a Lb Ub Ua : ℝ}
    (hconv : ConvexOn ℝ S τ) (hh : h ∈ S) (ha : a ∈ S) (hψ : ψ ≤ h) (hhb : h ≤ b) (hba : b < a)
    (hLb : Lb ≤ τ b) (hUb : τ b ≤ Ub) (hUa : τ a ≤ Ua) :
    K h - K b
        + min (((h - ψ) * (a - h) / (a - b) - (b - ψ)) * Lb)
            (((h - ψ) * (a - h) / (a - b) - (b - ψ)) * Ub)
        + -((h - ψ) * (b - h) / (a - b)) * Ua
      ≤ Phi K τ ψ h - Phi K τ ψ b := by
  have hab : 0 < a - b := sub_pos.mpr hba
  have hψ' : 0 ≤ h - ψ := sub_nonneg.mpr hψ
  have hbh : 0 ≤ b - h := sub_nonneg.mpr hhb
  -- convexity at `h ≤ b < a`
  have h3 : τ b * (a - h) ≤ τ h * (a - b) + τ a * (b - h) :=
    certificate_three_point hconv hh ha hhb hba.le (lt_of_le_of_lt hhb hba)
  have hτh : (τ b * (a - h) - τ a * (b - h)) / (a - b) ≤ τ h := by
    rw [div_le_iff₀ hab]
    linarith
  have hca0 : -((h - ψ) * (b - h) / (a - b)) ≤ 0 :=
    neg_nonpos.mpr (div_nonneg (mul_nonneg hψ' hbh) hab.le)
  have hmin : min (((h - ψ) * (a - h) / (a - b) - (b - ψ)) * Lb)
      (((h - ψ) * (a - h) / (a - b) - (b - ψ)) * Ub)
      ≤ ((h - ψ) * (a - h) / (a - b) - (b - ψ)) * τ b := by
    rcases le_total 0 ((h - ψ) * (a - h) / (a - b) - (b - ψ)) with hc | hc
    · exact (min_le_left _ _).trans (mul_le_mul_of_nonneg_left hLb hc)
    · exact (min_le_right _ _).trans (mul_le_mul_of_nonpos_left hUb hc)
  have hUa' : -((h - ψ) * (b - h) / (a - b)) * Ua ≤ -((h - ψ) * (b - h) / (a - b)) * τ a :=
    mul_le_mul_of_nonpos_left hUa hca0
  have hmul : (h - ψ) * ((τ b * (a - h) - τ a * (b - h)) / (a - b)) ≤ (h - ψ) * τ h :=
    mul_le_mul_of_nonneg_left hτh hψ'
  have e : ((h - ψ) * (a - h) / (a - b) - (b - ψ)) * τ b
      + -((h - ψ) * (b - h) / (a - b)) * τ a + (b - ψ) * τ b
      = (h - ψ) * ((τ b * (a - h) - τ a * (b - h)) / (a - b)) := by
    ring
  unfold Phi
  linarith

/-- Rule (J-right).  New rate `h ≥ b`, second anchor `a < b`. -/
theorem joint_right_gain {K τ : ℝ → ℝ} {S : Set ℝ} {ψ h b a Lb Ub Ua : ℝ}
    (hconv : ConvexOn ℝ S τ) (ha : a ∈ S) (hh : h ∈ S) (hψ : ψ ≤ h) (hab : a < b) (hbh : b ≤ h)
    (hLb : Lb ≤ τ b) (hUb : τ b ≤ Ub) (hUa : τ a ≤ Ua) :
    K h - K b
        + min (((h - ψ) * (h - a) / (b - a) - (b - ψ)) * Lb)
            (((h - ψ) * (h - a) / (b - a) - (b - ψ)) * Ub)
        + -((h - ψ) * (h - b) / (b - a)) * Ua
      ≤ Phi K τ ψ h - Phi K τ ψ b := by
  have hba : 0 < b - a := sub_pos.mpr hab
  have hψ' : 0 ≤ h - ψ := sub_nonneg.mpr hψ
  have hhb : 0 ≤ h - b := sub_nonneg.mpr hbh
  -- convexity at `a < b ≤ h`
  have h3 : τ b * (h - a) ≤ τ a * (h - b) + τ h * (b - a) :=
    certificate_three_point hconv ha hh hab.le hbh (lt_of_lt_of_le hab hbh)
  have hτh : (τ b * (h - a) - τ a * (h - b)) / (b - a) ≤ τ h := by
    rw [div_le_iff₀ hba]
    linarith
  have hca0 : -((h - ψ) * (h - b) / (b - a)) ≤ 0 :=
    neg_nonpos.mpr (div_nonneg (mul_nonneg hψ' hhb) hba.le)
  have hmin : min (((h - ψ) * (h - a) / (b - a) - (b - ψ)) * Lb)
      (((h - ψ) * (h - a) / (b - a) - (b - ψ)) * Ub)
      ≤ ((h - ψ) * (h - a) / (b - a) - (b - ψ)) * τ b := by
    rcases le_total 0 ((h - ψ) * (h - a) / (b - a) - (b - ψ)) with hc | hc
    · exact (min_le_left _ _).trans (mul_le_mul_of_nonneg_left hLb hc)
    · exact (min_le_right _ _).trans (mul_le_mul_of_nonpos_left hUb hc)
  have hUa' : -((h - ψ) * (h - b) / (b - a)) * Ua ≤ -((h - ψ) * (h - b) / (b - a)) * τ a :=
    mul_le_mul_of_nonpos_left hUa hca0
  have hmul : (h - ψ) * ((τ b * (h - a) - τ a * (h - b)) / (b - a)) ≤ (h - ψ) * τ h :=
    mul_le_mul_of_nonneg_left hτh hψ'
  have e : ((h - ψ) * (h - a) / (b - a) - (b - ψ)) * τ b
      + -((h - ψ) * (h - b) / (b - a)) * τ a + (b - ψ) * τ b
      = (h - ψ) * ((τ b * (h - a) - τ a * (h - b)) / (b - a)) := by
    ring
  unfold Phi
  linarith

end CreditCert
