import CreditCert.Confidence

/-!
# Relative-entropy confidence intervals for acceptance rates

Acceptances take the values `0` and `1`.  For such observations the Chernoff bound with the exact moment
generating function gives the tail bound `exp (-n kl(q, p))`, where `kl` is the relative entropy between
Bernoulli laws.  The confidence interval `{p' : n kl(p̂, p') ≤ log (2 / δ)}` therefore misses the true
acceptance rate with probability at most `δ`.  It lies inside the Hoeffding interval of
`confidence_event_bernoulli` (Pinsker's inequality) and is much shorter when take-up is far from `1/2`.

Main results: `mgf_zero_one`, `chernoff_kl_upper` (tail bound at a fixed level, including the level `1`),
`kl_deviation` (two-sided bound for the deviation `n kl(p̂, p)`), and `confidence_event_kl` (all anchors and
checkpoints at once, with the error schedule `budget`).
-/

namespace CreditCert

open MeasureTheory ProbabilityTheory Real Set Filter Topology
open scoped ENNReal NNReal

/-- Relative entropy between the Bernoulli laws with means `q` and `p`. -/
noncomputable def klb (q p : ℝ) : ℝ := q * log (q / p) + (1 - q) * log ((1 - q) / (1 - p))

private theorem mul_log_div_eq (x y : ℝ) (hy : y ≠ 0) : x * log (x / y) = x * log x - x * log y := by
  rcases eq_or_ne x 0 with h | h
  · simp [h]
  · rw [log_div h hy]
    ring

theorem klb_eq {q p : ℝ} (hp0 : p ≠ 0) (hp1 : 1 - p ≠ 0) :
    klb q p = (q * log q - q * log p) + ((1 - q) * log (1 - q) - (1 - q) * log (1 - p)) := by
  unfold klb
  rw [mul_log_div_eq q p hp0, mul_log_div_eq (1 - q) (1 - p) hp1]

theorem continuous_klb {p : ℝ} (hp0 : p ≠ 0) (hp1 : 1 - p ≠ 0) : Continuous fun q => klb q p := by
  have h : (fun q => klb q p) =
      fun q => (q * log q - q * log p) + ((1 - q) * log (1 - q) - (1 - q) * log (1 - p)) :=
    funext fun q => klb_eq hp0 hp1
  rw [h]
  have h1 : Continuous fun q : ℝ => q * log q := Real.continuous_mul_log
  have h2 : Continuous fun q : ℝ => (1 - q) * log (1 - q) :=
    Real.continuous_mul_log.comp (continuous_const.sub continuous_id)
  exact (h1.sub (continuous_id.mul continuous_const)).add
    (h2.sub ((continuous_const.sub continuous_id).mul continuous_const))

theorem klb_symm (q p : ℝ) : klb (1 - q) (1 - p) = klb q p := by
  unfold klb
  simp only [sub_sub_cancel]
  ring

theorem klb_one (p : ℝ) : klb 1 p = -log p := by
  unfold klb
  simp [one_div, Real.log_inv]

/-! ## The moment generating function of a `{0,1}`-valued variable -/

theorem mgf_zero_one {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : Ω → ℝ} (hm : Measurable X) (h01 : ∀ ω, X ω = 0 ∨ X ω = 1) (t : ℝ) :
    mgf X μ t = 1 + (exp t - 1) * μ[X] := by
  have hpt : (fun ω => exp (t * X ω)) = fun ω => 1 + (exp t - 1) * X ω := by
    funext ω
    rcases h01 ω with h | h <;> simp [h]
  have hint : Integrable X μ := by
    refine Integrable.of_bound hm.aestronglyMeasurable 1 (Eventually.of_forall fun ω => ?_)
    rcases h01 ω with h | h <;> simp [h]
  unfold mgf
  rw [hpt, integral_add (integrable_const _) (hint.const_mul _), integral_const, integral_const_mul]
  simp

private theorem sum_zero_one_bounds {Ω : Type*} {X : ℕ → Ω → ℝ} (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (n : ℕ) (ω : Ω) : 0 ≤ ∑ k ∈ Finset.range n, X k ω ∧ ∑ k ∈ Finset.range n, X k ω ≤ n := by
  constructor
  · exact Finset.sum_nonneg fun k _ => by rcases h01 k ω with h | h <;> simp [h]
  · calc ∑ k ∈ Finset.range n, X k ω ≤ ∑ _k ∈ Finset.range n, (1 : ℝ) :=
          Finset.sum_le_sum fun k _ => by rcases h01 k ω with h | h <;> simp [h]
      _ = n := by simp

/-! ## Chernoff bounds for a sum of independent acceptance indicators -/

/-- The Chernoff bound for a sum of `n` independent `{0,1}`-valued variables with mean `p`, at any `t ≥ 0`. -/
theorem chernoff_sum_upper {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → Ω → ℝ} (hm : ∀ k, Measurable (X k)) (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (hind : iIndepFun X μ) {p : ℝ} (hp : ∀ k, μ[X k] = p) (n : ℕ) {t : ℝ} (ht : 0 ≤ t) (ε : ℝ) :
    μ.real {ω | ε ≤ ∑ k ∈ Finset.range n, X k ω} ≤ exp (-t * ε) * (1 + (exp t - 1) * p) ^ n := by
  set S : Ω → ℝ := fun ω => ∑ k ∈ Finset.range n, X k ω with hSdef
  have hSm : Measurable S := Finset.measurable_sum _ fun k _ => hm k
  have hint : Integrable (fun ω => exp (t * S ω)) μ := by
    refine Integrable.of_bound ((hSm.const_mul t).exp.aestronglyMeasurable) (exp (t * n))
      (Eventually.of_forall fun ω => ?_)
    have hb := sum_zero_one_bounds h01 n ω
    rw [Real.norm_eq_abs, abs_of_pos (exp_pos _)]
    exact exp_le_exp.mpr (mul_le_mul_of_nonneg_left hb.2 ht)
  have h := measure_ge_le_exp_mul_mgf (X := S) ε ht hint
  have hS' : S = ∑ k ∈ Finset.range n, X k := by
    funext ω
    simp [hSdef, Finset.sum_apply]
  have hmgf : mgf S μ t = (1 + (exp t - 1) * p) ^ n := by
    rw [hS', hind.mgf_sum hm]
    rw [Finset.prod_congr rfl (fun k _ => by rw [mgf_zero_one (hm k) (h01 k) t, hp k])]
    rw [Finset.prod_const, Finset.card_range]
  rw [hmgf] at h
  exact h

/-- At the level `n`, the Chernoff bound gives `p ^ n`, the probability that every applicant accepts. -/
theorem chernoff_all_ones {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → Ω → ℝ} (hm : ∀ k, Measurable (X k)) (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (hind : iIndepFun X μ) {p : ℝ} (hp : ∀ k, μ[X k] = p) (n : ℕ) :
    μ.real {ω | (n : ℝ) ≤ ∑ k ∈ Finset.range n, X k ω} ≤ p ^ n := by
  have hf : ∀ t : ℝ, 0 ≤ t →
      μ.real {ω | (n : ℝ) ≤ ∑ k ∈ Finset.range n, X k ω} ≤ (exp (-t) * (1 - p) + p) ^ n := by
    intro t ht
    refine (chernoff_sum_upper hm h01 hind hp n ht n).trans (le_of_eq ?_)
    have hinv : exp (-t) * exp t = 1 := by rw [← exp_add]; simp
    rw [show -t * (n : ℝ) = n * (-t) by ring, Real.exp_nat_mul, ← mul_pow]
    congr 1
    linear_combination p * hinv
  have hlim : Tendsto (fun t : ℝ => (exp (-t) * (1 - p) + p) ^ n) atTop (𝓝 (p ^ n)) := by
    have h0 : Tendsto (fun t : ℝ => exp (-t) * (1 - p) + p) atTop (𝓝 (0 * (1 - p) + p)) :=
      (tendsto_exp_neg_atTop_nhds_zero.mul_const (1 - p)).add_const p
    rw [zero_mul, zero_add] at h0
    exact h0.pow n
  exact ge_of_tendsto hlim (eventually_atTop.mpr ⟨0, fun t ht => hf t ht⟩)

/-- **Chernoff bound in relative-entropy form.**  For `p ≤ q ≤ 1`, the probability that the mean of `n`
independent acceptance indicators with mean `p` is at least `q` is at most `exp (-n kl(q, p))`. -/
theorem chernoff_kl_upper {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → Ω → ℝ} (hm : ∀ k, Measurable (X k)) (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (hind : iIndepFun X μ) {p : ℝ} (hp : ∀ k, μ[X k] = p) (hp0 : 0 < p) (hp1 : p < 1) (n : ℕ)
    {q : ℝ} (hpq : p ≤ q) (hq1 : q ≤ 1) :
    μ.real {ω | n * q ≤ ∑ k ∈ Finset.range n, X k ω} ≤ exp (-(n * klb q p)) := by
  rcases hq1.lt_or_eq with hq1 | hq1
  · have hq0 : 0 < q := lt_of_lt_of_le hp0 hpq
    have h1p : 0 < 1 - p := by linarith
    have h1q : 0 < 1 - q := by linarith
    set r := q * (1 - p) / (p * (1 - q)) with hr
    have hr0 : 0 < r := by positivity
    have hr1 : 1 ≤ r := by
      rw [hr, le_div_iff₀ (by positivity)]
      nlinarith
    have h := chernoff_sum_upper hm h01 hind hp n (log_nonneg hr1) (n * q)
    have hbase : 1 + (exp (log r) - 1) * p = (1 - p) / (1 - q) := by
      rw [exp_log hr0, hr]
      field_simp
      ring
    rw [hbase] at h
    refine h.trans (le_of_eq ?_)
    rw [← exp_log (show 0 < ((1 - p) / (1 - q)) ^ n by positivity), ← exp_add, Real.log_pow]
    congr 1
    rw [klb_eq hp0.ne' h1p.ne', hr, log_div (by positivity) (by positivity),
      log_mul hq0.ne' h1p.ne', log_mul hp0.ne' h1q.ne', log_div h1p.ne' h1q.ne']
    ring
  · subst hq1
    have h := chernoff_all_ones hm h01 hind hp n
    rw [mul_one]
    refine h.trans (le_of_eq ?_)
    rw [klb_one p, mul_neg, neg_neg, Real.exp_nat_mul, exp_log hp0]

/-! ## The deviation `n kl(p̂, p)` -/

/-- Upper half: means at or above `p`. -/
theorem kl_upper_deviation {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → Ω → ℝ} (hm : ∀ k, Measurable (X k)) (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (hind : iIndepFun X μ) {p : ℝ} (hp : ∀ k, μ[X k] = p) (hp0 : 0 < p) (hp1 : p < 1)
    {n : ℕ} (hn : 0 < n) (c : ℝ) :
    μ.real {ω | p ≤ (∑ k ∈ Finset.range n, X k ω) / n ∧
      c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} ≤ exp (-c) := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hmean1 : ∀ ω, (∑ k ∈ Finset.range n, X k ω) / n ≤ 1 := fun ω => by
    rw [div_le_one hn']
    exact (sum_zero_one_bounds h01 n ω).2
  set A : Set ℝ := {q | p ≤ q ∧ q ≤ 1 ∧ c < n * klb q p} with hA
  have hmem : ∀ q, q ∈ A ↔ (p ≤ q ∧ q ≤ 1 ∧ c < n * klb q p) := fun q => by rw [hA]; rfl
  by_cases hne : A.Nonempty
  · have hbdd : BddBelow A := by
      refine ⟨p, fun q hq => ?_⟩
      exact ((hmem q).1 hq).1
    obtain ⟨q₁, hq₁⟩ := hne
    have hq₀p : p ≤ sInf A := le_csInf ⟨q₁, hq₁⟩ fun q hq => ((hmem q).1 hq).1
    have hq₀1 : sInf A ≤ 1 := (csInf_le hbdd hq₁).trans ((hmem q₁).1 hq₁).2.1
    have hc : c ≤ n * klb (sInf A) p := by
      have hcl : IsClosed {q : ℝ | c ≤ n * klb q p} :=
        isClosed_le continuous_const (continuous_const.mul (continuous_klb hp0.ne' (by linarith)))
      exact closure_minimal (fun q hq => le_of_lt ((hmem q).1 hq).2.2) hcl
        (csInf_mem_closure ⟨q₁, hq₁⟩ hbdd)
    have hsub : {ω | p ≤ (∑ k ∈ Finset.range n, X k ω) / n ∧
        c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} ⊆
        {ω | n * sInf A ≤ ∑ k ∈ Finset.range n, X k ω} := by
      intro ω hω
      have hle : sInf A ≤ (∑ k ∈ Finset.range n, X k ω) / n :=
        csInf_le hbdd ((hmem _).2 ⟨hω.1, hmean1 ω, hω.2⟩)
      have h2 := mul_le_mul_of_nonneg_left hle hn'.le
      rwa [mul_div_cancel₀ _ hn'.ne'] at h2
    calc _ ≤ μ.real {ω | n * sInf A ≤ ∑ k ∈ Finset.range n, X k ω} := measureReal_mono hsub
      _ ≤ exp (-(n * klb (sInf A) p)) := chernoff_kl_upper hm h01 hind hp hp0 hp1 n hq₀p hq₀1
      _ ≤ exp (-c) := exp_le_exp.mpr (by linarith)
  · have hempty : {ω | p ≤ (∑ k ∈ Finset.range n, X k ω) / n ∧
        c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} = ∅ := by
      ext ω
      simp only [mem_ofPred_eq, mem_empty_iff_false, iff_false, not_and, not_lt]
      intro h1
      by_contra h2
      exact hne ⟨_, (hmem _).2 ⟨h1, hmean1 ω, lt_of_not_ge h2⟩⟩
    rw [hempty, measureReal_empty]
    positivity

/-- Lower half: means below `p`, by applying the upper half to the refusals `1 - X k`. -/
theorem kl_lower_deviation {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → Ω → ℝ} (hm : ∀ k, Measurable (X k)) (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (hind : iIndepFun X μ) {p : ℝ} (hp : ∀ k, μ[X k] = p) (hp0 : 0 < p) (hp1 : p < 1)
    {n : ℕ} (hn : 0 < n) (c : ℝ) :
    μ.real {ω | (∑ k ∈ Finset.range n, X k ω) / n < p ∧
      c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} ≤ exp (-c) := by
  set Y : ℕ → Ω → ℝ := fun k ω => 1 - X k ω with hY
  have hYm : ∀ k, Measurable (Y k) := fun k => measurable_const.sub (hm k)
  have hY01 : ∀ k ω, Y k ω = 0 ∨ Y k ω = 1 := fun k ω => by
    rcases h01 k ω with h | h
    · right
      simp [hY, h]
    · left
      simp [hY, h]
  have hYind : iIndepFun Y μ :=
    hind.comp (fun _ x => 1 - x) (fun _ => measurable_const.sub measurable_id)
  have hYp : ∀ k, μ[Y k] = 1 - p := fun k => by
    have hint : Integrable (X k) μ := by
      refine Integrable.of_bound (hm k).aestronglyMeasurable 1 (Eventually.of_forall fun ω => ?_)
      rcases h01 k ω with h | h <;> simp [h]
    simp only [hY]
    rw [integral_sub (integrable_const 1) hint, integral_const, hp k]
    simp
  have h := kl_upper_deviation hYm hY01 hYind hYp (by linarith) (by linarith) hn c
  refine le_trans (measureReal_mono ?_) h
  intro ω hω
  have hn' : (n : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hn.ne'
  have hsum : (∑ k ∈ Finset.range n, Y k ω) / n = 1 - (∑ k ∈ Finset.range n, X k ω) / n := by
    simp only [hY, Finset.sum_sub_distrib, Finset.sum_const, Finset.card_range, nsmul_eq_mul, mul_one]
    field_simp
  refine ⟨?_, ?_⟩
  · rw [hsum]
    linarith [hω.1]
  · rw [hsum, klb_symm]
    exact hω.2

/-- **Two-sided deviation bound.**  The probability that `n kl(p̂, p) > c` is at most `2 exp (-c)`. -/
theorem kl_deviation {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → Ω → ℝ} (hm : ∀ k, Measurable (X k)) (h01 : ∀ k ω, X k ω = 0 ∨ X k ω = 1)
    (hind : iIndepFun X μ) {p : ℝ} (hp : ∀ k, μ[X k] = p) (hp0 : 0 < p) (hp1 : p < 1)
    {n : ℕ} (hn : 0 < n) (c : ℝ) :
    μ.real {ω | c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} ≤ 2 * exp (-c) := by
  have hsub : {ω | c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} ⊆
      {ω | p ≤ (∑ k ∈ Finset.range n, X k ω) / n ∧
        c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} ∪
      {ω | (∑ k ∈ Finset.range n, X k ω) / n < p ∧
        c < n * klb ((∑ k ∈ Finset.range n, X k ω) / n) p} := by
    intro ω hω
    by_cases h : p ≤ (∑ k ∈ Finset.range n, X k ω) / n
    · exact Or.inl ⟨h, hω⟩
    · exact Or.inr ⟨lt_of_not_ge h, hω⟩
  calc _ ≤ μ.real (_ ∪ _) := measureReal_mono hsub
    _ ≤ _ := measureReal_union_le _ _
    _ ≤ exp (-c) + exp (-c) := add_le_add (kl_upper_deviation hm h01 hind hp hp0 hp1 hn c)
        (kl_lower_deviation hm h01 hind hp hp0 hp1 hn c)
    _ = 2 * exp (-c) := by ring

/-! ## All anchors and checkpoints at once -/

/-- **Confidence event, relative-entropy form.**  Anchor `j` has acceptance indicators `X j k`, independent
in `k` with mean `p j ∈ (0, 1)`; checkpoint `i` uses the first `N i` of them.  With probability at least
`1 - α`, every checkpoint of every anchor satisfies `N i kl(p̂, p j) ≤ log (2 / δ_{j,i})`, so `p j` lies in
every relative-entropy interval the agent computes. -/
theorem confidence_event_kl {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, Measurable (X j k)) (h01 : ∀ j k ω, X j k ω = 0 ∨ X j k ω = 1)
    (hind : ∀ j, iIndepFun (X j) μ) {p : ℕ → ℝ} (hp : ∀ j k, μ[X j k] = p j)
    (hp0 : ∀ j, 0 < p j) (hp1 : ∀ j, p j < 1) {α : ℝ} (hα : 0 < α) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i) :
    μ {ω | ∃ j i, log (2 / budget α j i) <
      N i * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) (p j)} ≤ ENNReal.ofReal α := by
  have hset : {ω | ∃ j i, log (2 / budget α j i) <
      N i * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) (p j)} =
      ⋃ j, ⋃ i, {ω | log (2 / budget α j i) <
        N i * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) (p j)} := by
    ext ω
    simp only [mem_ofPred_eq, mem_iUnion]
  rw [hset]
  refine union_bound_schedule μ hα.le _ fun j i => ?_
  have hb := budget_pos hα j i
  have h := kl_deviation (hm j) (h01 j) (hind j) (hp j) (hp0 j) (hp1 j) (hN i) (log (2 / budget α j i))
  have he : 2 * exp (-log (2 / budget α j i)) = budget α j i := by
    rw [exp_neg, exp_log (by positivity)]
    field_simp
  rw [he] at h
  rw [← ofReal_measureReal]
  exact ENNReal.ofReal_le_ofReal h

/-! ## Pinsker's inequality for acceptance rates -/

theorem klb_self (q : ℝ) : klb q q = 0 := by
  unfold klb
  have h1 : q * log (q / q) = 0 := by
    rcases eq_or_ne q 0 with h | h
    · simp [h]
    · rw [div_self h, log_one, mul_zero]
  have h2 : (1 - q) * log ((1 - q) / (1 - q)) = 0 := by
    rcases eq_or_ne (1 - q) 0 with h | h
    · simp [h]
    · rw [div_self h, log_one, mul_zero]
  rw [h1, h2, add_zero]

/-- The derivative in `p` of `kl(q, p) - 2 (q - p)²`, with the relative entropy written with separate
logarithms: it is `(p - q) (1 - 2p)² / (p (1 - p))`, which has the sign of `p - q`. -/
private theorem hasDerivAt_pinskerGap (q : ℝ) {p : ℝ} (hp0 : 0 < p) (hp1 : p < 1) :
    HasDerivAt (fun x : ℝ => (q * log q - q * log x) + ((1 - q) * log (1 - q) - (1 - q) * log (1 - x))
      - 2 * (q - x) ^ 2) ((p - q) * (1 - 2 * p) ^ 2 / (p * (1 - p))) p := by
  have h1p : (1 - p) ≠ 0 := by linarith
  have d1 : HasDerivAt (fun x : ℝ => q * log x) (q * p⁻¹) p := (hasDerivAt_log hp0.ne').const_mul q
  have d2 : HasDerivAt (fun x : ℝ => (1 - q) * log (1 - x)) ((1 - q) * (-1 / (1 - p))) p :=
    (((hasDerivAt_id' p).const_sub 1).log h1p).const_mul (1 - q)
  have d3 : HasDerivAt (fun x : ℝ => 2 * (q - x) ^ 2) (2 * (2 * (q - p) * (-1))) p := by
    have h := (((hasDerivAt_id' p).const_sub q).pow 2).const_mul (2 : ℝ)
    convert h using 1
    norm_num
  have d := (((hasDerivAt_const p (q * log q)).sub d1).add
    ((hasDerivAt_const p ((1 - q) * log (1 - q))).sub d2)).sub d3
  convert d using 1
  field_simp
  ring

/-- Pinsker's inequality for Bernoulli laws, interior case. -/
private theorem pinsker_bernoulli_open {q p : ℝ} (hq0 : 0 < q) (hq1 : q < 1) (hp0 : 0 < p) (hp1 : p < 1) :
    2 * (q - p) ^ 2 ≤ klb q p := by
  set H : ℝ → ℝ := fun x => (q * log q - q * log x) + ((1 - q) * log (1 - q) - (1 - q) * log (1 - x))
    - 2 * (q - x) ^ 2 with hH
  have hHq : H q = 0 := by simp [hH]
  have hHp : H p = klb q p - 2 * (q - p) ^ 2 := by
    rw [klb_eq hp0.ne' (by linarith)]
  have hderiv : ∀ x, 0 < x → x < 1 →
      HasDerivAt H ((x - q) * (1 - 2 * x) ^ 2 / (x * (1 - x))) x :=
    fun x h0 h1 => hasDerivAt_pinskerGap q h0 h1
  suffices h : 0 ≤ H p by
    rw [hHp] at h
    linarith
  rcases le_total q p with hqp | hpq
  · have hmono : MonotoneOn H (Icc q p) := by
      refine monotoneOn_of_deriv_nonneg (convex_Icc q p) ?_ ?_ ?_
      · intro x hx
        exact (hderiv x (lt_of_lt_of_le hq0 hx.1) (lt_of_le_of_lt hx.2 hp1)).continuousAt.continuousWithinAt
      · intro x hx
        rw [interior_Icc] at hx
        exact (hderiv x (lt_trans hq0 hx.1) (lt_trans hx.2 hp1)).differentiableAt.differentiableWithinAt
      · intro x hx
        rw [interior_Icc] at hx
        have hx0 : 0 < x := lt_trans hq0 hx.1
        have hx1 : x < 1 := lt_trans hx.2 hp1
        rw [(hderiv x hx0 hx1).deriv]
        have hden : 0 < x * (1 - x) := mul_pos hx0 (by linarith)
        exact div_nonneg (mul_nonneg (by linarith [hx.1]) (sq_nonneg _)) hden.le
    have h := hmono (left_mem_Icc.mpr hqp) (right_mem_Icc.mpr hqp) hqp
    rwa [hHq] at h
  · have hanti : AntitoneOn H (Icc p q) := by
      refine antitoneOn_of_deriv_nonpos (convex_Icc p q) ?_ ?_ ?_
      · intro x hx
        exact (hderiv x (lt_of_lt_of_le hp0 hx.1) (lt_of_le_of_lt hx.2 hq1)).continuousAt.continuousWithinAt
      · intro x hx
        rw [interior_Icc] at hx
        exact (hderiv x (lt_trans hp0 hx.1) (lt_trans hx.2 hq1)).differentiableAt.differentiableWithinAt
      · intro x hx
        rw [interior_Icc] at hx
        have hx0 : 0 < x := lt_trans hp0 hx.1
        have hx1 : x < 1 := lt_trans hx.2 hq1
        rw [(hderiv x hx0 hx1).deriv]
        have hden : 0 < x * (1 - x) := mul_pos hx0 (by linarith)
        exact div_nonpos_of_nonpos_of_nonneg
          (mul_nonpos_of_nonpos_of_nonneg (by linarith [hx.2]) (sq_nonneg _)) hden.le
    have h := hanti (left_mem_Icc.mpr hpq) (right_mem_Icc.mpr hpq) hpq
    rwa [hHq] at h

/-- **Pinsker's inequality for Bernoulli laws.**  For `q ∈ [0, 1]` and `p ∈ (0, 1)`, `2 (q - p)² ≤ kl(q, p)`. -/
theorem pinsker_bernoulli {q p : ℝ} (hq0 : 0 ≤ q) (hq1 : q ≤ 1) (hp0 : 0 < p) (hp1 : p < 1) :
    2 * (q - p) ^ 2 ≤ klb q p := by
  have hcl : IsClosed {x : ℝ | 2 * (x - p) ^ 2 ≤ klb x p} :=
    isClosed_le (by fun_prop) (continuous_klb hp0.ne' (by linarith))
  have hsub : Ioo (0 : ℝ) 1 ⊆ {x : ℝ | 2 * (x - p) ^ 2 ≤ klb x p} :=
    fun x hx => pinsker_bernoulli_open hx.1 hx.2 hp0 hp1
  have hmem : q ∈ closure (Ioo (0 : ℝ) 1) := by
    rw [closure_Ioo (by norm_num)]
    exact ⟨hq0, hq1⟩
  exact closure_minimal hsub hcl hmem

/-- **The relative-entropy interval lies inside the Hoeffding interval.**  If `n kl(q, p) ≤ log (2 / δ)`, then
`|q - p|` is at most the Hoeffding radius with noise level `1/2`. -/
theorem kl_within_radius {q p δ : ℝ} {n : ℕ} (hn : 0 < n) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) (hp0 : 0 < p)
    (hp1 : p < 1) (hδ : 0 < δ) (hδ2 : δ ≤ 2) (h : n * klb q p ≤ log (2 / δ)) :
    |q - p| ≤ radius (1 / 2) n δ := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hlog : 0 ≤ log (2 / δ) := log_nonneg (by rw [le_div_iff₀ hδ]; linarith)
  have hr : 0 ≤ radius (1 / 2) n δ := radius_nonneg (by norm_num) n
  have hrsq : radius (1 / 2) n δ ^ 2 = log (2 / δ) / (2 * n) := by
    unfold radius
    rw [mul_pow, Real.sq_sqrt (by positivity)]
    field_simp
  have hpin := pinsker_bernoulli hq0 hq1 hp0 hp1
  have hsq : (q - p) ^ 2 ≤ radius (1 / 2) n δ ^ 2 := by
    rw [hrsq, le_div_iff₀ (by positivity)]
    nlinarith
  exact (Real.abs_le_sqrt hsq).trans_eq (Real.sqrt_sq hr)

/-- Any two points of a relative-entropy interval are within twice the Hoeffding radius of each other; in
particular every point of the interval is within `2 r` of the true acceptance rate on the confidence event. -/
theorem kl_interval_width {q p x δ : ℝ} {n : ℕ} (hn : 0 < n) (hq0 : 0 ≤ q) (hq1 : q ≤ 1)
    (hp0 : 0 < p) (hp1 : p < 1) (hx0 : 0 < x) (hx1 : x < 1) (hδ : 0 < δ) (hδ2 : δ ≤ 2)
    (hp : n * klb q p ≤ log (2 / δ)) (hx : n * klb q x ≤ log (2 / δ)) :
    |x - p| ≤ 2 * radius (1 / 2) n δ := by
  have h1 := kl_within_radius hn hq0 hq1 hp0 hp1 hδ hδ2 hp
  have h2 := kl_within_radius hn hq0 hq1 hx0 hx1 hδ hδ2 hx
  have h3 : |x - p| ≤ |q - x| + |q - p| := by
    have : x - p = -(q - x) + (q - p) := by ring
    rw [this]
    exact (abs_add_le _ _).trans (by rw [abs_neg])
  linarith

end CreditCert
