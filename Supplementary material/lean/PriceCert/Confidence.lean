import PriceCert.Defs

/-!
# The confidence event

Covers the probabilistic half of Theorem 5: the error schedule sums to at most `α`, the radius
matches the two-sided sub-Gaussian tail bound, the fixed-sample bound for independent noise and
for conditionally sub-Gaussian noise, and the simultaneous event over all anchors and
checkpoints.
-/

namespace PriceCert

open MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal

/-! ## The error schedule -/

theorem sum_inv_mul_succ (n : ℕ) :
    ∑ i ∈ Finset.range n, 1 / (((i : ℝ) + 1) * ((i : ℝ) + 2)) = 1 - 1 / ((n : ℝ) + 1) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ih]
    push_cast
    have h1 : ((n : ℝ) + 1) ≠ 0 := by positivity
    have h2 : ((n : ℝ) + 2) ≠ 0 := by positivity
    have h3 : ((n : ℝ) + 1 + 1) ≠ 0 := by positivity
    field_simp
    ring

theorem budget_pos {α : ℝ} (hα : 0 < α) (j i : ℕ) : 0 < budget α j i := by
  unfold budget
  positivity

/-- The budgets are nonnegative as soon as `α` is. -/
private theorem budget_nonneg {α : ℝ} (hα : 0 ≤ α) (j i : ℕ) : 0 ≤ budget α j i := by
  unfold budget
  positivity

theorem budget_le {α : ℝ} (hα : 0 ≤ α) (j i : ℕ) : budget α j i ≤ α / 4 := by
  unfold budget
  have hj : (0 : ℝ) ≤ j := Nat.cast_nonneg j
  have hi : (0 : ℝ) ≤ i := Nat.cast_nonneg i
  have hJ : (2 : ℝ) ≤ ((j : ℝ) + 1) * ((j : ℝ) + 2) := by nlinarith
  have hI : (2 : ℝ) ≤ ((i : ℝ) + 1) * ((i : ℝ) + 2) := by nlinarith
  have hden : (4 : ℝ) ≤ ((j : ℝ) + 1) * ((j : ℝ) + 2) * (((i : ℝ) + 1) * ((i : ℝ) + 2)) := by
    nlinarith
  exact div_le_div_of_nonneg_left hα (by norm_num) hden

/-- The budgets of any finite block of anchors and checkpoints sum to at most `α`. -/
theorem sum_budget_le {α : ℝ} (hα : 0 ≤ α) (m n : ℕ) :
    ∑ j ∈ Finset.range m, ∑ i ∈ Finset.range n, budget α j i ≤ α := by
  have key : ∑ j ∈ Finset.range m, ∑ i ∈ Finset.range n, budget α j i
      = α * ((1 - 1 / ((m : ℝ) + 1)) * (1 - 1 / ((n : ℝ) + 1))) := by
    rw [← sum_inv_mul_succ m, ← sum_inv_mul_succ n, Finset.sum_mul_sum, Finset.mul_sum]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    unfold budget
    have h1 : ((j : ℝ) + 1) ≠ 0 := by positivity
    have h2 : ((j : ℝ) + 2) ≠ 0 := by positivity
    have h3 : ((i : ℝ) + 1) ≠ 0 := by positivity
    have h4 : ((i : ℝ) + 2) ≠ 0 := by positivity
    field_simp
  have hm0 : 0 ≤ 1 - 1 / ((m : ℝ) + 1) := by
    have : 1 / ((m : ℝ) + 1) ≤ 1 := by
      rw [div_le_one (by positivity)]
      linarith [(Nat.cast_nonneg m : (0 : ℝ) ≤ m)]
    linarith
  have hm1 : 1 - 1 / ((m : ℝ) + 1) ≤ 1 := by
    have : 0 ≤ 1 / ((m : ℝ) + 1) := by positivity
    linarith
  have hn0 : 0 ≤ 1 - 1 / ((n : ℝ) + 1) := by
    have : 1 / ((n : ℝ) + 1) ≤ 1 := by
      rw [div_le_one (by positivity)]
      linarith [(Nat.cast_nonneg n : (0 : ℝ) ≤ n)]
    linarith
  have hn1 : 1 - 1 / ((n : ℝ) + 1) ≤ 1 := by
    have : 0 ≤ 1 / ((n : ℝ) + 1) := by positivity
    linarith
  rw [key]
  have hprod : (1 - 1 / ((m : ℝ) + 1)) * (1 - 1 / ((n : ℝ) + 1)) ≤ 1 := by
    calc (1 - 1 / ((m : ℝ) + 1)) * (1 - 1 / ((n : ℝ) + 1)) ≤ 1 * 1 :=
          mul_le_mul hm1 hn1 hn0 zero_le_one
      _ = 1 := one_mul 1
  calc α * ((1 - 1 / ((m : ℝ) + 1)) * (1 - 1 / ((n : ℝ) + 1))) ≤ α * 1 :=
        mul_le_mul_of_nonneg_left hprod hα
    _ = α := mul_one α

/-! ## The radius -/

/-- The radius is chosen so that the two-sided tail bound equals the error level. -/
theorem radius_identity {σ δ : ℝ} {n : ℕ} (hσ : 0 < σ) (hn : 0 < n) (hδ : 0 < δ) (hδ2 : δ ≤ 2) :
    2 * Real.exp (-(n : ℝ) * radius σ n δ ^ 2 / (2 * σ ^ 2)) = δ := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have h2δ : 1 ≤ 2 / δ := by
    rw [le_div_iff₀ hδ]
    linarith
  have hlog : 0 ≤ Real.log (2 / δ) := Real.log_nonneg h2δ
  have hsq : radius σ n δ ^ 2 = σ ^ 2 * (2 * Real.log (2 / δ) / n) := by
    unfold radius
    rw [mul_pow, Real.sq_sqrt (by positivity)]
  have hexp : -(n : ℝ) * radius σ n δ ^ 2 / (2 * σ ^ 2) = -Real.log (2 / δ) := by
    rw [hsq]
    field_simp
  rw [hexp, Real.exp_neg, Real.exp_log (by positivity)]
  field_simp

theorem radius_nonneg {σ δ : ℝ} (hσ : 0 ≤ σ) (n : ℕ) : 0 ≤ radius σ n δ := by
  unfold radius
  exact mul_nonneg hσ (Real.sqrt_nonneg _)

/-! ## Union bound over anchors and checkpoints -/

theorem union_bound_schedule {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) {α : ℝ}
    (hα : 0 ≤ α) (E : ℕ → ℕ → Set Ω) (hE : ∀ j i, μ (E j i) ≤ ENNReal.ofReal (budget α j i)) :
    μ (⋃ j, ⋃ i, E j i) ≤ ENNReal.ofReal α := by
  calc μ (⋃ j, ⋃ i, E j i) ≤ ∑' j, μ (⋃ i, E j i) := measure_iUnion_le _
    _ ≤ ∑' j, ∑' i, μ (E j i) := tsum_le_tsum fun j => measure_iUnion_le _
    _ ≤ ∑' j, ∑' i, ENNReal.ofReal (budget α j i) :=
        tsum_le_tsum fun j => tsum_le_tsum fun i => hE j i
    _ ≤ ENNReal.ofReal α := by
      refine ENNReal.tsum_le_of_sum_range_le fun m => ?_
      rw [← Summable.tsum_finsetSum (fun j _ => CompleteLattice.summable)]
      refine ENNReal.tsum_le_of_sum_range_le fun n => ?_
      rw [Finset.sum_comm]
      have hsum : ∑ j ∈ Finset.range m, ∑ i ∈ Finset.range n, ENNReal.ofReal (budget α j i)
          = ENNReal.ofReal (∑ j ∈ Finset.range m, ∑ i ∈ Finset.range n, budget α j i) := by
        rw [ENNReal.ofReal_sum_of_nonneg
          (fun j _ => Finset.sum_nonneg fun i _ => budget_nonneg hα j i)]
        refine Finset.sum_congr rfl fun j _ => ?_
        rw [ENNReal.ofReal_sum_of_nonneg (fun i _ => budget_nonneg hα j i)]
      rw [hsum]
      exact ENNReal.ofReal_le_ofReal (sum_budget_le hα m n)

/-! ## Fixed-sample two-sided bounds -/

/-- The exponent of the tail bound for a sum at level `n * r`, rewritten for the mean. -/
private theorem exponent_identity (n r c : ℝ) (hn : 0 < n) :
    -(n * r) ^ 2 / (2 * (n * c)) = -n * r ^ 2 / (2 * c) := by
  rcases eq_or_ne c 0 with hc | hc
  · simp [hc]
  · have hn' : n ≠ 0 := hn.ne'
    field_simp

/-- A two-sided bound on the mean follows from the two one-sided bounds on the sum. -/
private theorem mean_abs_ge_le_of_sum_bounds {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
    [IsFiniteMeasure μ] {S : Ω → ℝ} {n : ℕ} (hn : 0 < n) {r B : ℝ}
    (h_up : μ.real {ω | (n : ℝ) * r ≤ S ω} ≤ B)
    (h_lo : μ.real {ω | (n : ℝ) * r ≤ -S ω} ≤ B) :
    μ.real {ω | r ≤ |S ω / (n : ℝ)|} ≤ 2 * B := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hsub : {ω | r ≤ |S ω / (n : ℝ)|}
      ⊆ {ω | (n : ℝ) * r ≤ S ω} ∪ {ω | (n : ℝ) * r ≤ -S ω} := by
    intro ω hω
    simp only [Set.mem_ofPred_eq, Set.mem_union] at hω ⊢
    rcases le_abs.mp hω with h | h
    · left
      rw [le_div_iff₀ hn'] at h
      linarith
    · right
      rw [← neg_div, le_div_iff₀ hn'] at h
      linarith
  calc μ.real {ω | r ≤ |S ω / (n : ℝ)|}
      ≤ μ.real ({ω | (n : ℝ) * r ≤ S ω} ∪ {ω | (n : ℝ) * r ≤ -S ω}) := measureReal_mono hsub
    _ ≤ μ.real {ω | (n : ℝ) * r ≤ S ω} + μ.real {ω | (n : ℝ) * r ≤ -S ω} :=
        measureReal_union_le _ _
    _ ≤ 2 * B := by linarith

/-- Hoeffding's inequality for the mean of independent sub-Gaussian variables, two-sided. -/
theorem mean_abs_ge_le_of_iIndepFun {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
    [IsProbabilityMeasure μ] {X : ℕ → Ω → ℝ} (h_indep : iIndepFun X μ) {c : ℝ≥0} {n : ℕ}
    (hn : 0 < n) (h_subG : ∀ i < n, HasSubgaussianMGF (X i) c μ) {r : ℝ} (hr : 0 ≤ r) :
    μ.real {ω | r ≤ |(∑ i ∈ Finset.range n, X i ω) / (n : ℝ)|}
      ≤ 2 * Real.exp (-(n : ℝ) * r ^ 2 / (2 * c)) := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hε : 0 ≤ (n : ℝ) * r := mul_nonneg hn'.le hr
  have hexp : -((n : ℝ) * r) ^ 2 / (2 * n * c) = -(n : ℝ) * r ^ 2 / (2 * c) := by
    rw [mul_assoc]
    exact exponent_identity n r c hn'
  have h_up : μ.real {ω | (n : ℝ) * r ≤ ∑ i ∈ Finset.range n, X i ω}
      ≤ Real.exp (-(n : ℝ) * r ^ 2 / (2 * c)) := by
    have h := HasSubgaussianMGF.measure_sum_range_ge_le_of_iIndepFun h_indep h_subG hε
    rwa [hexp] at h
  have h_indep_neg : iIndepFun (fun i ω => -X i ω) μ :=
    h_indep.comp (fun _ x => -x) (fun _ => measurable_neg)
  have h_subG_neg : ∀ i < n, HasSubgaussianMGF (fun ω => -X i ω) c μ :=
    fun i hi => (h_subG i hi).neg
  have h_lo : μ.real {ω | (n : ℝ) * r ≤ -∑ i ∈ Finset.range n, X i ω}
      ≤ Real.exp (-(n : ℝ) * r ^ 2 / (2 * c)) := by
    have h := HasSubgaussianMGF.measure_sum_range_ge_le_of_iIndepFun h_indep_neg h_subG_neg hε
    rw [hexp] at h
    simpa only [Finset.sum_neg_distrib] using h
  exact mean_abs_ge_le_of_sum_bounds hn h_up h_lo

/-- The Azuma-Hoeffding inequality for the mean of an adapted sequence of conditionally
sub-Gaussian variables, two-sided. -/
theorem mean_abs_ge_le_of_hasCondSubgaussianMGF {Ω : Type*} {mΩ : MeasurableSpace Ω}
    [StandardBorelSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ] {ℱ : Filtration ℕ mΩ}
    {Y : ℕ → Ω → ℝ} {c : ℝ≥0} (h_adapted : StronglyAdapted ℱ Y)
    (h0 : HasSubgaussianMGF (Y 0) c μ) {n : ℕ} (hn : 0 < n)
    (h_subG : ∀ i < n - 1, HasCondSubgaussianMGF (ℱ i) (ℱ.le i) (Y (i + 1)) c μ)
    {r : ℝ} (hr : 0 ≤ r) :
    μ.real {ω | r ≤ |(∑ i ∈ Finset.range n, Y i ω) / (n : ℝ)|}
      ≤ 2 * Real.exp (-(n : ℝ) * r ^ 2 / (2 * c)) := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hε : 0 ≤ (n : ℝ) * r := mul_nonneg hn'.le hr
  have hexp : -((n : ℝ) * r) ^ 2 / (2 * ((∑ _i ∈ Finset.range n, c : ℝ≥0) : ℝ))
      = -(n : ℝ) * r ^ 2 / (2 * c) := by
    rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul, NNReal.coe_mul, NNReal.coe_natCast]
    exact exponent_identity n r c hn'
  have h_up : μ.real {ω | (n : ℝ) * r ≤ ∑ i ∈ Finset.range n, Y i ω}
      ≤ Real.exp (-(n : ℝ) * r ^ 2 / (2 * c)) := by
    have h := measure_sum_ge_le_of_hasCondSubgaussianMGF (cY := fun _ => c) h_adapted h0 n
      h_subG hε
    rwa [hexp] at h
  have h_adapted_neg : StronglyAdapted ℱ (fun i ω => -Y i ω) := fun i => (h_adapted i).neg
  have h0_neg : HasSubgaussianMGF (fun ω => -Y 0 ω) c μ := h0.neg
  have h_subG_neg : ∀ i < n - 1,
      HasCondSubgaussianMGF (ℱ i) (ℱ.le i) (fun ω => -Y (i + 1) ω) c μ :=
    fun i hi => Kernel.HasSubgaussianMGF.neg (h_subG i hi)
  have h_lo : μ.real {ω | (n : ℝ) * r ≤ -∑ i ∈ Finset.range n, Y i ω}
      ≤ Real.exp (-(n : ℝ) * r ^ 2 / (2 * c)) := by
    have h := measure_sum_ge_le_of_hasCondSubgaussianMGF (cY := fun _ => c)
      (Y := fun i ω => -Y i ω) h_adapted_neg h0_neg n h_subG_neg hε
    rw [hexp] at h
    simpa only [Finset.sum_neg_distrib] using h
  exact mean_abs_ge_le_of_sum_bounds hn h_up h_lo

/-! ## The simultaneous confidence event -/

/-- Theorem 5, confidence event, for independent noise.  `ζ j k` is the noise in the `k`-th
observation at anchor `j` and `N i` is the sample count at checkpoint `i`.  With probability at
least `1 - α`, at every checkpoint of every anchor the mean noise is inside the radius. -/
theorem confidence_event {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {ζ : ℕ → ℕ → Ω → ℝ} {σ : ℝ≥0} (hσ : 0 < σ) (h_indep : ∀ j, iIndepFun (ζ j) μ)
    (h_subG : ∀ j k, HasSubgaussianMGF (ζ j k) (σ ^ 2) μ) {α : ℝ} (hα0 : 0 < α) (hα1 : α ≤ 1)
    (N : ℕ → ℕ) (hN : ∀ i, 0 < N i) :
    μ {ω | ∃ j i, radius σ (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), ζ j k ω) / (N i : ℝ)|} ≤ ENNReal.ofReal α := by
  have hσ' : (0 : ℝ) < σ := NNReal.coe_pos.mpr hσ
  have hset : {ω | ∃ j i, radius σ (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), ζ j k ω) / (N i : ℝ)|}
      = ⋃ j, ⋃ i, {ω | radius σ (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), ζ j k ω) / (N i : ℝ)|} := by
    ext ω
    simp only [Set.mem_ofPred_eq, Set.mem_iUnion]
  rw [hset]
  refine union_bound_schedule μ hα0.le _ fun j i => ?_
  have hb : 0 < budget α j i := budget_pos hα0 j i
  have hb2 : budget α j i ≤ 2 := (budget_le hα0.le j i).trans (by linarith)
  have h := mean_abs_ge_le_of_iIndepFun (h_indep j) (hN i) (fun k _ => h_subG j k)
    (radius_nonneg hσ'.le (N i) (δ := budget α j i))
  rw [NNReal.coe_pow, radius_identity hσ' (hN i) hb hb2] at h
  rw [← ofReal_measureReal]
  exact ENNReal.ofReal_le_ofReal h

/-- The same event for conditionally sub-Gaussian noise: `ζ j` is adapted to a filtration `ℱ j`
and each term is conditionally sub-Gaussian given the previous ones. -/
theorem confidence_event_martingale {Ω : Type*} {mΩ : MeasurableSpace Ω} [StandardBorelSpace Ω]
    {μ : Measure Ω} [IsProbabilityMeasure μ] {ℱ : ℕ → Filtration ℕ mΩ}
    {ζ : ℕ → ℕ → Ω → ℝ} {σ : ℝ≥0} (hσ : 0 < σ) (h_adapted : ∀ j, StronglyAdapted (ℱ j) (ζ j))
    (h0 : ∀ j, HasSubgaussianMGF (ζ j 0) (σ ^ 2) μ)
    (h_subG : ∀ j k, HasCondSubgaussianMGF (ℱ j k) ((ℱ j).le k) (ζ j (k + 1)) (σ ^ 2) μ)
    {α : ℝ} (hα0 : 0 < α) (hα1 : α ≤ 1) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i) :
    μ {ω | ∃ j i, radius σ (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), ζ j k ω) / (N i : ℝ)|} ≤ ENNReal.ofReal α := by
  have hσ' : (0 : ℝ) < σ := NNReal.coe_pos.mpr hσ
  have hset : {ω | ∃ j i, radius σ (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), ζ j k ω) / (N i : ℝ)|}
      = ⋃ j, ⋃ i, {ω | radius σ (N i) (budget α j i)
        ≤ |(∑ k ∈ Finset.range (N i), ζ j k ω) / (N i : ℝ)|} := by
    ext ω
    simp only [Set.mem_ofPred_eq, Set.mem_iUnion]
  rw [hset]
  refine union_bound_schedule μ hα0.le _ fun j i => ?_
  have hb : 0 < budget α j i := budget_pos hα0 j i
  have hb2 : budget α j i ≤ 2 := (budget_le hα0.le j i).trans (by linarith)
  have h := mean_abs_ge_le_of_hasCondSubgaussianMGF (h_adapted j) (h0 j) (hN i)
    (fun k _ => h_subG j k) (radius_nonneg hσ'.le (N i) (δ := budget α j i))
  rw [NNReal.coe_pow, radius_identity hσ' (hN i) hb hb2] at h
  rw [← ofReal_measureReal]
  exact ENNReal.ofReal_le_ofReal h

end PriceCert
