import PriceCert.Minorant

/-!
# Fixed points and local rates

Covers Theorem 2: fixed points of the tangent-response update are the stationary points of
deployed profit, the local rate of the update, and the local behaviour of blind retraining.
-/

namespace PriceCert

open Set

/-! ## Theorem 2(a): fixed points are stationary points -/

theorem hasDerivAt_tangentSurrogate {K : ℝ → ℝ} {ψ b τb s h K' : ℝ} (hK : HasDerivAt K K' h) :
    HasDerivAt (tangentSurrogate K ψ b τb s) (K' + (τb + s * (h - b)) + (h - ψ) * s) h := by
  have h1 : HasDerivAt (fun x : ℝ => x - ψ) 1 h := (hasDerivAt_id' h).sub_const ψ
  have h2 : HasDerivAt (fun x : ℝ => τb + s * (x - b)) (s * 1) h :=
    (((hasDerivAt_id' h).sub_const b).const_mul s).const_add τb
  have h3 : HasDerivAt (fun x : ℝ => K x + (x - ψ) * (τb + s * (x - b)))
      (K' + (1 * (τb + s * (h - b)) + (h - ψ) * (s * 1))) h := hK.fun_add (h1.fun_mul h2)
  have heq : tangentSurrogate K ψ b τb s = fun x : ℝ => K x + (x - ψ) * (τb + s * (x - b)) := by
    funext x
    rfl
  rw [heq]
  exact h3.congr_deriv (by ring)

/-- The surrogate and deployed profit have the same slope at the base quote. -/
theorem surrogate_slope_at_base {K τ : ℝ → ℝ} {ψ b K' τ' : ℝ}
    (hK : HasDerivAt K K' b) (hτ : HasDerivAt τ τ' b) :
    HasDerivAt (tangentSurrogate K ψ b (τ b) τ') (K' + τ b + (b - ψ) * τ') b ∧
      HasDerivAt (Phi K τ ψ) (K' + τ b + (b - ψ) * τ') b := by
  refine ⟨?_, hasDerivAt_Phi hK hτ⟩
  have h := hasDerivAt_tangentSurrogate (ψ := ψ) (b := b) (τb := τ b) (s := τ') hK
  exact h.congr_deriv (by ring)

/-- An interior fixed point of the update is a stationary point of deployed profit. -/
theorem fixedPoint_stationary {K τ : ℝ → ℝ} {I : Set ℝ} {ψ b K' τ' : ℝ}
    (hK : HasDerivAt K K' b) (hτ : HasDerivAt τ τ' b) (hint : b ∈ interior I)
    (hfix : IsMaxOn (tangentSurrogate K ψ b (τ b) τ') I b) :
    HasDerivAt (Phi K τ ψ) 0 b := by
  obtain ⟨hS, hΦ⟩ := surrogate_slope_at_base (ψ := ψ) hK hτ
  have hloc : IsLocalMax (tangentSurrogate K ψ b (τ b) τ') b :=
    hfix.isLocalMax (mem_interior_iff_mem_nhds.mp hint)
  have hzero : K' + τ b + (b - ψ) * τ' = 0 := hloc.hasDerivAt_eq_zero hS
  exact hΦ.congr_deriv hzero

/-- Conversely, a stationary point of deployed profit is a fixed point of the update. -/
theorem stationary_isFixedPoint {K τ : ℝ → ℝ} {I : Set ℝ} {ψ b K' τ' : ℝ}
    (hKc : ConcaveOn ℝ I K) (hb : b ∈ I) (hK : HasDerivAt K K' b) (hτ' : τ' ≤ 0)
    (hstat : K' + τ b + (b - ψ) * τ' = 0) :
    IsMaxOn (tangentSurrogate K ψ b (τ b) τ') I b := by
  have hconc : ConcaveOn ℝ I (tangentSurrogate K ψ b (τ b) τ') := by
    refine ⟨hKc.1, fun x hx y hy a c ha hc hac => ?_⟩
    have hK2 := hKc.2 hx hy ha hc hac
    obtain rfl : c = 1 - a := by linarith
    simp only [smul_eq_mul, tangentSurrogate] at hK2 ⊢
    nlinarith [mul_nonneg (neg_nonneg.mpr hτ') (mul_nonneg (mul_nonneg ha hc) (sq_nonneg (x - y)))]
  have hd : HasDerivAt (tangentSurrogate K ψ b (τ b) τ') 0 b :=
    (hasDerivAt_tangentSurrogate (ψ := ψ) (b := b) (τb := τ b) (s := τ') hK).congr_deriv
      (by linear_combination hstat)
  exact isMaxOn_of_concaveOn_of_hasDerivAt_zero hconc hb hd

/-- For a quadratic known profit the update is a gradient step with a curvature-chosen step
size: `h = b + Φ'(b) / (γ + 2 ε)`, with `ε = -τ'`. -/
theorem quadratic_step {K' τb τ' γ ψ b h : ℝ} (hne : γ + 2 * -τ' ≠ 0)
    (hfoc : (K' - γ * (h - b)) + (τb + τ' * (h - b)) + (h - ψ) * τ' = 0) :
    h = b + (K' + τb + (b - ψ) * τ') / (γ + 2 * -τ') := by
  have h1 : (h - b) * (γ + 2 * -τ') = K' + τb + (b - ψ) * τ' := by
    linear_combination -hfoc
  have h2 : h - b = (K' + τb + (b - ψ) * τ') / (γ + 2 * -τ') := by
    rw [eq_div_iff hne]
    exact h1
  linarith

/-! ## Theorem 2(b): the local rate of the update -/

/-- Differentiating the first-order condition of the update at a fixed point. -/
theorem rate_identity {K' τ τ' T : ℝ → ℝ} {ψ b K'' τ'' T' : ℝ}
    (hTb : T b = b) (hT : HasDerivAt T T' b)
    (hK' : HasDerivAt K' K'' b) (hτ : HasDerivAt τ (τ' b) b) (hτ' : HasDerivAt τ' τ'' b)
    (hfoc : ∀ᶠ x in nhds b, K' (T x) + τ x + τ' x * (T x - x) + (T x - ψ) * τ' x = 0) :
    T' * (K'' + 2 * τ' b) + (b - ψ) * τ'' = 0 := by
  have h1 : HasDerivAt (fun x => K' (T x)) (K'' * T') b := hK'.comp_of_eq b hT hTb.symm
  have h3 : HasDerivAt (fun x => τ' x * (T x - x)) (τ'' * (T b - b) + τ' b * (T' - 1)) b :=
    hτ'.fun_mul (hT.fun_sub (hasDerivAt_id' b))
  have h4 : HasDerivAt (fun x => (T x - ψ) * τ' x) (T' * τ' b + (T b - ψ) * τ'') b :=
    (hT.sub_const ψ).fun_mul hτ'
  have hG : HasDerivAt (fun x => K' (T x) + τ x + τ' x * (T x - x) + (T x - ψ) * τ' x)
      (K'' * T' + τ' b + (τ'' * (T b - b) + τ' b * (T' - 1)) + (T' * τ' b + (T b - ψ) * τ'')) b :=
    ((h1.fun_add hτ).fun_add h3).fun_add h4
  have hev : (fun x => K' (T x) + τ x + τ' x * (T x - x) + (T x - ψ) * τ' x) =ᶠ[nhds b]
      fun _ => (0 : ℝ) := hfoc
  have hG0 : HasDerivAt (fun x => K' (T x) + τ x + τ' x * (T x - x) + (T x - ψ) * τ' x) 0 b :=
    (hasDerivAt_const b (0 : ℝ)).congr_of_eventuallyEq hev
  have hzero := hG.unique hG0
  rw [hTb] at hzero
  linear_combination hzero

/-- The rate in terms of `γ = -K''` and `ε = -τ'`. -/
theorem rate_formula {ψ b γ ε τ'' T' : ℝ} (hid : T' * (-γ + 2 * -ε) + (b - ψ) * τ'' = 0)
    (hne : γ + 2 * ε ≠ 0) : T' = (b - ψ) * τ'' / (γ + 2 * ε) := by
  rw [eq_div_iff hne]
  linear_combination -hid

/-- The rate equals one minus the ratio of the curvature of deployed profit to the curvature of
the surrogate. -/
theorem rate_eq_one_sub {ψ b γ ε τ'' : ℝ} (hne : γ + 2 * ε ≠ 0) :
    (b - ψ) * τ'' / (γ + 2 * ε) = 1 - (γ + 2 * ε - (b - ψ) * τ'') / (γ + 2 * ε) := by
  rw [sub_div, div_self hne]
  ring

/-- At a strict local maximum of deployed profit the rate lies in `[0, 1)`. -/
theorem rate_mem_Ico {ψ b γ ε τ'' : ℝ} (hγ : 0 < γ) (hε : 0 ≤ ε) (hτ'' : 0 ≤ τ'') (hb : ψ ≤ b)
    (hPO : 0 < γ + 2 * ε - (b - ψ) * τ'') :
    0 ≤ (b - ψ) * τ'' / (γ + 2 * ε) ∧ (b - ψ) * τ'' / (γ + 2 * ε) < 1 := by
  have hpos : 0 < γ + 2 * ε := by linarith
  refine ⟨div_nonneg (mul_nonneg (sub_nonneg.mpr hb) hτ'') hpos.le, ?_⟩
  rw [div_lt_one hpos]
  linarith

/-! ## Theorem 2(c): blind retraining -/

/-- Differentiating the first-order condition of blind retraining at a stable quote. -/
theorem retraining_slope_identity {K' τ R : ℝ → ℝ} {b K'' τ1 R' : ℝ}
    (hRb : R b = b) (hR : HasDerivAt R R' b) (hK' : HasDerivAt K' K'' b)
    (hτ : HasDerivAt τ τ1 b) (hfoc : ∀ᶠ x in nhds b, K' (R x) + τ x = 0) :
    R' * K'' + τ1 = 0 := by
  have h1 : HasDerivAt (fun x => K' (R x)) (K'' * R') b := hK'.comp_of_eq b hR hRb.symm
  have hG : HasDerivAt (fun x => K' (R x) + τ x) (K'' * R' + τ1) b := h1.fun_add hτ
  have hev : (fun x => K' (R x) + τ x) =ᶠ[nhds b] fun _ => (0 : ℝ) := hfoc
  have hG0 : HasDerivAt (fun x => K' (R x) + τ x) 0 b :=
    (hasDerivAt_const b (0 : ℝ)).congr_of_eventuallyEq hev
  have hzero := hG.unique hG0
  linear_combination hzero

/-- The slope of blind retraining is `-ε / γ`. -/
theorem retraining_slope_formula {γ ε R' : ℝ} (hid : R' * -γ + -ε = 0) (hγ : γ ≠ 0) :
    R' = -(ε / γ) := by
  rw [← neg_div, eq_div_iff hγ]
  linear_combination -hid

/-! ## Local dynamics of a one-dimensional map near a fixed point -/

/-- The first-order estimate behind the local dynamics: for every `c > 0`, near `b` the
increment `R x - R b` differs from `(x - b) * R'` by at most `c * |x - b|`. -/
private theorem abs_sub_linear_le_of_hasDerivAt {R : ℝ → ℝ} {b R' c : ℝ} (hR : HasDerivAt R R' b)
    (hc : 0 < c) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ x, |x - b| < δ → |R x - R b - (x - b) * R'| ≤ c * |x - b| := by
  have h1 : ∀ᶠ x in nhds b, ‖R x - R b - (x - b) • R'‖ ≤ c * ‖x - b‖ := hR.isLittleO.def hc
  rw [Metric.eventually_nhds_iff] at h1
  obtain ⟨δ, hδ, h2⟩ := h1
  refine ⟨δ, hδ, fun x hx => ?_⟩
  have h3 := @h2 x (by rw [Real.dist_eq]; exact hx)
  simpa only [Real.norm_eq_abs, smul_eq_mul] using h3

theorem local_contraction_of_abs_deriv_lt_one {R : ℝ → ℝ} {b R' : ℝ} (hRb : R b = b)
    (hR : HasDerivAt R R' b) (hlt : |R'| < 1) :
    ∃ q δ : ℝ, 0 ≤ q ∧ q < 1 ∧ 0 < δ ∧ ∀ x, |x - b| < δ → |R x - b| ≤ q * |x - b| := by
  have hc : 0 < (1 - |R'|) / 2 := by linarith
  obtain ⟨δ, hδ, h⟩ := abs_sub_linear_le_of_hasDerivAt hR hc
  have hR'0 : 0 ≤ |R'| := abs_nonneg R'
  refine ⟨(1 + |R'|) / 2, δ, by linarith, by linarith, hδ, fun x hx => ?_⟩
  have h1 : |R x - b - (x - b) * R'| ≤ (1 - |R'|) / 2 * |x - b| := by
    have := h x hx
    rwa [hRb] at this
  have h2 : |R x - b| ≤ |R x - b - (x - b) * R'| + |x - b| * |R'| := by
    calc |R x - b| = |(R x - b - (x - b) * R') + (x - b) * R'| := by rw [sub_add_cancel]
      _ ≤ |R x - b - (x - b) * R'| + |(x - b) * R'| := abs_add_le _ _
      _ = |R x - b - (x - b) * R'| + |x - b| * |R'| := by rw [abs_mul]
  nlinarith [h1, h2]

theorem iterate_le_of_local_contraction {R : ℝ → ℝ} {b q δ : ℝ} (hq0 : 0 ≤ q) (hq1 : q < 1)
    (hδ : 0 < δ) (hc : ∀ x, |x - b| < δ → |R x - b| ≤ q * |x - b|) {x : ℝ}
    (hx : |x - b| < δ) (n : ℕ) : |R^[n] x - b| ≤ q ^ n * |x - b| := by
  -- `hδ` is not needed for the argument: `hx` already forces `0 < δ`.
  have _ := hδ
  induction n with
  | zero => simp
  | succ n ih =>
    have hqn : q ^ n ≤ 1 := pow_le_one₀ hq0 hq1.le
    have hlt : |R^[n] x - b| < δ := by
      calc |R^[n] x - b| ≤ q ^ n * |x - b| := ih
        _ ≤ 1 * |x - b| := mul_le_mul_of_nonneg_right hqn (abs_nonneg _)
        _ = |x - b| := one_mul _
        _ < δ := hx
    rw [Function.iterate_succ_apply']
    calc |R (R^[n] x) - b| ≤ q * |R^[n] x - b| := hc _ hlt
      _ ≤ q * (q ^ n * |x - b|) := mul_le_mul_of_nonneg_left ih hq0
      _ = q ^ (n + 1) * |x - b| := by ring

theorem local_repulsion_of_one_lt_abs_deriv {R : ℝ → ℝ} {b R' : ℝ} (hRb : R b = b)
    (hR : HasDerivAt R R' b) (hgt : 1 < |R'|) :
    ∃ δ : ℝ, 0 < δ ∧ ∀ x, x ≠ b → |x - b| < δ → |x - b| < |R x - b| := by
  have hc : 0 < (|R'| - 1) / 2 := by linarith
  obtain ⟨δ, hδ, h⟩ := abs_sub_linear_le_of_hasDerivAt hR hc
  refine ⟨δ, hδ, fun x hxb hx => ?_⟩
  have h1 : |R x - b - (x - b) * R'| ≤ (|R'| - 1) / 2 * |x - b| := by
    have := h x hx
    rwa [hRb] at this
  have hpos : 0 < |x - b| := abs_pos.mpr (sub_ne_zero.mpr hxb)
  have h2 : |x - b| * |R'| ≤ |R x - b| + |R x - b - (x - b) * R'| := by
    calc |x - b| * |R'| = |(x - b) * R'| := (abs_mul _ _).symm
      _ = |(R x - b) - (R x - b - (x - b) * R')| := by rw [sub_sub_cancel]
      _ ≤ |R x - b| + |R x - b - (x - b) * R'| := abs_sub _ _
  nlinarith [h1, h2, mul_pos hpos (sub_pos.mpr hgt)]

end PriceCert
