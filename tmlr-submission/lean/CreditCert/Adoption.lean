import CreditCert.Certificate

/-!
# The certified rate search: what holds on the confidence event

Covers the deterministic half of Theorem "anytime guarantee" (adoption and rejection are sound, incumbents
improve, every quoted rate is within the risk budget of the incumbent, cumulative profit) and Proposition
"detection time" (the sample cost of a certificate).
-/

namespace CreditCert

open Set

/-! ## Intervals -/

/-- A sample mean within the radius of the truth gives a two-sided interval. -/
theorem interval_of_abs_lt {ybar τx r : ℝ} (h : |ybar - τx| < r) :
    ybar - r ≤ τx ∧ τx ≤ ybar + r := by
  obtain ⟨h1, h2⟩ := abs_lt.mp h
  constructor <;> linarith

/-- If every raw interval contains the truth, so does their running intersection.  In
particular the intersection is never empty. -/
theorem running_interval_contains {L U : ℕ → ℝ} {x : ℝ} (h : ∀ i, L i ≤ x ∧ x ≤ U i) (n : ℕ) :
    (Finset.range (n + 1)).sup' Finset.nonempty_range_add_one L ≤ x ∧
      x ≤ (Finset.range (n + 1)).inf' Finset.nonempty_range_add_one U := by
  exact ⟨Finset.sup'_le _ _ (fun i _ => (h i).1), Finset.le_inf' _ _ (fun i _ => (h i).2)⟩

/-! ## Theorem "anytime guarantee", part (ii): adoption and rejection -/

/-- A positive direct certificate implies a strict improvement.  No shape assumption. -/
theorem adoption_sound {K τ : ℝ → ℝ} {ψ c b Lc Ub : ℝ} (hc : ψ ≤ c) (hb : ψ ≤ b)
    (hLc : Lc ≤ τ c) (hUb : τ b ≤ Ub) (hpos : 0 < K c + (c - ψ) * Lc - K b - (b - ψ) * Ub) :
    Phi K τ ψ b < Phi K τ ψ c := by
  have h : K c + (c - ψ) * Lc - K b - (b - ψ) * Ub ≤ Phi K τ ψ c - Phi K τ ψ b :=
    direct_gain hc hb hLc hUb
  linarith

/-- A nonpositive upper certificate implies the challenger is no better. -/
theorem rejection_sound {K τ : ℝ → ℝ} {ψ c b Uc Lb : ℝ} (hc : ψ ≤ c) (hb : ψ ≤ b)
    (hUc : τ c ≤ Uc) (hLb : Lb ≤ τ b) (hneg : K c + (c - ψ) * Uc - K b - (b - ψ) * Lb ≤ 0) :
    Phi K τ ψ c ≤ Phi K τ ψ b := by
  have h : Phi K τ ψ c - Phi K τ ψ b ≤ K c + (c - ψ) * Uc - K b - (b - ψ) * Lb :=
    direct_gain_upper hc hb hUc hLb
  linarith

theorem incumbent_monotone {Φ : ℝ → ℝ} {inc : ℕ → ℝ}
    (hadopt : ∀ t, Φ (inc t) ≤ Φ (inc (t + 1))) : Monotone (fun t => Φ (inc t)) := by
  exact monotone_nat_of_le_succ hadopt

/-! ## Theorem "anytime guarantee", part (iii): every quoted rate is within the risk budget -/

theorem deployed_ge_start_sub {Φ : ℝ → ℝ} {inc q : ℕ → ℝ} {ℓ : ℝ}
    (hadopt : ∀ t, Φ (inc t) ≤ Φ (inc (t + 1))) (htrial : ∀ t, Φ (inc t) - ℓ ≤ Φ (q t)) (t : ℕ) :
    Φ (inc 0) - ℓ ≤ Φ (q t) := by
  have h1 : Φ (inc 0) ≤ Φ (inc t) := incumbent_monotone hadopt (Nat.zero_le t)
  have h2 : Φ (inc t) - ℓ ≤ Φ (q t) := htrial t
  linarith

/-- Cumulative deployed profit is at least the status-quo profit minus the risk budget times the
number of quotes at a rate other than the incumbent. -/
theorem cumulative_profit_lower {Φ : ℝ → ℝ} {inc q : ℕ → ℝ} {ℓ : ℝ} (hℓ : 0 ≤ ℓ)
    (hadopt : ∀ t, Φ (inc t) ≤ Φ (inc (t + 1))) (htrial : ∀ t, Φ (inc t) - ℓ ≤ Φ (q t)) (T : ℕ) :
    (T : ℝ) * Φ (inc 0) - ℓ * (((Finset.range T).filter (fun t => q t ≠ inc t)).card : ℝ)
      ≤ ∑ t ∈ Finset.range T, Φ (q t) := by
  -- The bound does not need `0 ≤ ℓ`; the hypothesis is part of the fixed statement.
  have _ := hℓ
  -- each period earns at least the starting profit, minus the budget when a trial is deployed
  have hterm : ∀ t ∈ Finset.range T,
      Φ (inc 0) - ℓ * (if q t ≠ inc t then (1 : ℝ) else 0) ≤ Φ (q t) := by
    intro t _
    have h1 : Φ (inc 0) ≤ Φ (inc t) := incumbent_monotone hadopt (Nat.zero_le t)
    by_cases hq : q t = inc t
    · rw [ite_eq_right (not_not.mpr hq), mul_zero, sub_zero, hq]
      exact h1
    · rw [ite_eq_left hq, mul_one]
      have h2 : Φ (inc t) - ℓ ≤ Φ (q t) := htrial t
      linarith
  calc (T : ℝ) * Φ (inc 0) - ℓ * (((Finset.range T).filter (fun t => q t ≠ inc t)).card : ℝ)
      = ∑ t ∈ Finset.range T, (Φ (inc 0) - ℓ * (if q t ≠ inc t then (1 : ℝ) else 0)) := by
        rw [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_range, nsmul_eq_mul,
          ← Finset.mul_sum, Finset.sum_boole]
    _ ≤ ∑ t ∈ Finset.range T, Φ (q t) := Finset.sum_le_sum hterm


/-! ## Proposition "detection time": the sample cost of a certificate -/

theorem certified_gain_lower {K τ : ℝ → ℝ} {ψ c b rc rb Lc Ub : ℝ} (hc : ψ ≤ c) (hb : ψ ≤ b)
    (hLc : τ c - 2 * rc ≤ Lc) (hUb : Ub ≤ τ b + 2 * rb) :
    (Phi K τ ψ c - Phi K τ ψ b) - 2 * (c - ψ) * rc - 2 * (b - ψ) * rb
      ≤ K c + (c - ψ) * Lc - K b - (b - ψ) * Ub := by
  have h1 : (c - ψ) * (τ c - 2 * rc) ≤ (c - ψ) * Lc :=
    mul_le_mul_of_nonneg_left hLc (sub_nonneg.mpr hc)
  have h2 : (b - ψ) * Ub ≤ (b - ψ) * (τ b + 2 * rb) :=
    mul_le_mul_of_nonneg_left hUb (sub_nonneg.mpr hb)
  unfold Phi
  linarith

theorem certified_gain_upper {K τ : ℝ → ℝ} {ψ c b rc rb Uc Lb : ℝ} (hc : ψ ≤ c) (hb : ψ ≤ b)
    (hUc : Uc ≤ τ c + 2 * rc) (hLb : τ b - 2 * rb ≤ Lb) :
    K c + (c - ψ) * Uc - K b - (b - ψ) * Lb
      ≤ (Phi K τ ψ c - Phi K τ ψ b) + 2 * (c - ψ) * rc + 2 * (b - ψ) * rb := by
  have h1 : (c - ψ) * Uc ≤ (c - ψ) * (τ c + 2 * rc) :=
    mul_le_mul_of_nonneg_left hUc (sub_nonneg.mpr hc)
  have h2 : (b - ψ) * (τ b - 2 * rb) ≤ (b - ψ) * Lb :=
    mul_le_mul_of_nonneg_left hLb (sub_nonneg.mpr hb)
  unfold Phi
  linarith

/-- Once the sample count exceeds `8 σ² log(2/δ) m² / Δ²`, twice the weighted radius is below
the true gain `Δ`. -/
theorem detection_sample_size {σ δ Δ m n : ℝ} (hσ : 0 < σ) (hδ : 0 < δ) (hδ2 : δ < 2)
    (hΔ : 0 < Δ) (hm : 0 ≤ m) (hn : 8 * σ ^ 2 * Real.log (2 / δ) * m ^ 2 / Δ ^ 2 < n) :
    2 * m * (σ * Real.sqrt (2 * Real.log (2 / δ) / n)) < Δ := by
  have hlog : 0 < Real.log (2 / δ) := by
    apply Real.log_pos
    rw [lt_div_iff₀ hδ]
    linarith
  have hΔ2 : 0 < Δ ^ 2 := by positivity
  have hn0 : 0 < n := by
    have h0 : 0 ≤ 8 * σ ^ 2 * Real.log (2 / δ) * m ^ 2 / Δ ^ 2 := by positivity
    linarith
  have hn' : 8 * σ ^ 2 * Real.log (2 / δ) * m ^ 2 < n * Δ ^ 2 := by
    rwa [div_lt_iff₀ hΔ2] at hn
  have hs0 : 0 ≤ 2 * Real.log (2 / δ) / n := by positivity
  have hsq : (Real.sqrt (2 * Real.log (2 / δ) / n)) ^ 2 = 2 * Real.log (2 / δ) / n :=
    Real.sq_sqrt hs0
  have hlhs : 0 ≤ 2 * m * (σ * Real.sqrt (2 * Real.log (2 / δ) / n)) :=
    mul_nonneg (mul_nonneg zero_le_two hm) (mul_nonneg hσ.le (Real.sqrt_nonneg _))
  -- both sides are nonnegative, so it suffices to compare squares
  refine (sq_lt_sq₀ hlhs hΔ.le).mp ?_
  calc (2 * m * (σ * Real.sqrt (2 * Real.log (2 / δ) / n))) ^ 2
      = 4 * m ^ 2 * σ ^ 2 * (Real.sqrt (2 * Real.log (2 / δ) / n)) ^ 2 := by ring
    _ = 4 * m ^ 2 * σ ^ 2 * (2 * Real.log (2 / δ) / n) := by rw [hsq]
    _ = (8 * σ ^ 2 * Real.log (2 / δ) * m ^ 2) / n := by ring
    _ < Δ ^ 2 := by
        rw [div_lt_iff₀ hn0]
        linarith

end CreditCert
