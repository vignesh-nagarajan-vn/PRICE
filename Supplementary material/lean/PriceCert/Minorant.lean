import PriceCert.Model

/-!
# The tangent-response update as minorize-maximize ascent

Covers Lemma 2 (the tangent surrogate is a minorant of deployed profit) and Theorem 1
(ascent, quadratic ascent, summable squared steps, limit points are fixed points).
-/

namespace PriceCert

open Set

/-! ## Lemma 2 -/

/-- A convex function lies above each of its tangent lines. -/
theorem tangent_le_of_convexOn {τ : ℝ → ℝ} {S : Set ℝ} {b h τ' : ℝ}
    (hconv : ConvexOn ℝ S τ) (hb : b ∈ S) (hh : h ∈ S) (hd : HasDerivAt τ τ' b) :
    τ b + τ' * (h - b) ≤ τ h := by
  rcases lt_trichotomy h b with hlt | heq | hgt
  · -- `h < b`: the secant slope from `h` to `b` is at most the derivative at `b`
    have h1 : slope τ h b ≤ τ' := hconv.slope_le_of_hasDerivAt hh hb hlt hd
    rw [slope_def_field, div_le_iff₀ (sub_pos.mpr hlt)] at h1
    linarith
  · subst heq
    simp
  · -- `b < h`: the derivative at `b` is at most the secant slope from `b` to `h`
    have h1 : τ' ≤ slope τ b h := hconv.le_slope_of_hasDerivAt hb hh hgt hd
    rw [slope_def_field, le_div_iff₀ (sub_pos.mpr hgt)] at h1
    linarith

/-- Lemma 2. For quotes at or above the cost `ψ`, the tangent surrogate lies below deployed
profit. -/
theorem surrogate_le_Phi {K τ : ℝ → ℝ} {S : Set ℝ} {ψ b h τ' : ℝ}
    (hconv : ConvexOn ℝ S τ) (hb : b ∈ S) (hh : h ∈ S) (hd : HasDerivAt τ τ' b) (hψ : ψ ≤ h) :
    tangentSurrogate K ψ b (τ b) τ' h ≤ Phi K τ ψ h := by
  have h1 : τ b + τ' * (h - b) ≤ τ h := tangent_le_of_convexOn hconv hb hh hd
  have h2 : (h - ψ) * (τ b + τ' * (h - b)) ≤ (h - ψ) * τ h :=
    mul_le_mul_of_nonneg_left h1 (sub_nonneg.mpr hψ)
  unfold tangentSurrogate Phi
  linarith

/-- Lemma 2. The surrogate touches deployed profit at the base quote. -/
theorem surrogate_self (K τ : ℝ → ℝ) (ψ b s : ℝ) :
    tangentSurrogate K ψ b (τ b) s b = Phi K τ ψ b := by
  simp [tangentSurrogate, Phi]

/-! ## Theorem 1 -/

/-- Ascent. A quote that does not lower the surrogate does not lower deployed profit. -/
theorem Phi_ascent {K τ : ℝ → ℝ} {S : Set ℝ} {ψ b bp τ' : ℝ}
    (hconv : ConvexOn ℝ S τ) (hb : b ∈ S) (hbp : bp ∈ S) (hd : HasDerivAt τ τ' b) (hψ : ψ ≤ bp)
    (hmax : tangentSurrogate K ψ b (τ b) τ' b ≤ tangentSurrogate K ψ b (τ b) τ' bp) :
    Phi K τ ψ b ≤ Phi K τ ψ bp := by
  calc Phi K τ ψ b = tangentSurrogate K ψ b (τ b) τ' b := (surrogate_self K τ ψ b τ').symm
    _ ≤ tangentSurrogate K ψ b (τ b) τ' bp := hmax
    _ ≤ Phi K τ ψ bp := surrogate_le_Phi hconv hb hbp hd hψ

/-- A maximizer of a strongly concave function beats every other point by a quadratic margin. -/
theorem quadratic_growth_of_strongConcaveOn {g : ℝ → ℝ} {I : Set ℝ} {m x xs : ℝ}
    (hg : StrongConcaveOn I m g) (hxs : xs ∈ I) (hx : x ∈ I) (hmax : IsMaxOn g I xs) :
    m / 2 * (xs - x) ^ 2 ≤ g xs - g x := by
  obtain ⟨hconv, hineq⟩ := hg
  have hD : 0 ≤ g xs - g x := sub_nonneg.mpr (hmax hx)
  -- the defining inequality at the point `(1 - t) xs + t x`, combined with maximality of `xs`
  have key : ∀ t : ℝ, 0 < t → t < 1 → (1 - t) * (m / 2 * (xs - x) ^ 2) ≤ g xs - g x := by
    intro t ht0 ht1
    have hsum : (1 - t) + t = 1 := by ring
    have h1 := hineq hxs hx (sub_nonneg.mpr ht1.le) ht0.le hsum
    have hmem : (1 - t) • xs + t • x ∈ I := hconv hxs hx (sub_nonneg.mpr ht1.le) ht0.le hsum
    have h2 : g ((1 - t) • xs + t • x) ≤ g xs := hmax hmem
    simp only [smul_eq_mul, Real.norm_eq_abs, sq_abs] at h1 h2
    have h3 : t * ((1 - t) * (m / 2 * (xs - x) ^ 2)) ≤ t * (g xs - g x) := by
      have e1 : t * ((1 - t) * (m / 2 * (xs - x) ^ 2))
          = (1 - t) * t * (m / 2 * (xs - x) ^ 2) := by ring
      have e2 : t * (g xs - g x) = g xs - ((1 - t) * g xs + t * g x) := by ring
      rw [e1, e2]
      linarith
    exact le_of_mul_le_mul_left h3 ht0
  -- let `t → 0`
  have aux : ∀ Q D : ℝ, 0 ≤ D → (∀ t : ℝ, 0 < t → t < 1 → (1 - t) * Q ≤ D) → Q ≤ D := by
    intro Q D hD0 hkey
    by_contra hcon
    rw [not_le] at hcon
    have hQ : 0 < Q := lt_of_le_of_lt hD0 hcon
    have ht0 : 0 < (Q - D) / (2 * Q) := div_pos (sub_pos.mpr hcon) (by positivity)
    have ht1 : (Q - D) / (2 * Q) < 1 := by
      rw [div_lt_one (by positivity)]
      linarith
    have h4 := hkey _ ht0 ht1
    have h5 : (Q - D) / (2 * Q) * Q = (Q - D) / 2 := by
      rw [div_mul_eq_mul_div, mul_div_mul_right _ _ hQ.ne']
    rw [sub_mul, one_mul, h5] at h4
    linarith
  exact aux _ _ hD key

/-- The one-sided Lipschitz bound on `K'` follows from a bound on the second derivative. -/
theorem deriv_gap_of_second_deriv_le {K' K'' : ℝ → ℝ} {I : Set ℝ} {γ : ℝ} (hI : Convex ℝ I)
    (hK' : ∀ x ∈ I, HasDerivAt K' (K'' x) x) (hK'' : ∀ x ∈ I, K'' x ≤ -γ)
    {x y : ℝ} (hx : x ∈ I) (hy : y ∈ I) (hxy : x ≤ y) : K' y - K' x ≤ -γ * (y - x) := by
  refine hI.image_sub_le_mul_sub_of_deriv_le ?_ ?_ ?_ x hx y hy hxy
  · exact fun z hz => (hK' z hz).continuousAt.continuousWithinAt
  · exact fun z hz => (hK' z (interior_subset hz)).differentiableAt.differentiableWithinAt
  · intro z hz
    rw [(hK' z (interior_subset hz)).deriv]
    exact hK'' z (interior_subset hz)

/-- Strong concavity from a one-sided Lipschitz bound on the derivative. -/
theorem strongConcaveOn_of_deriv {K K' : ℝ → ℝ} {I : Set ℝ} {γ : ℝ} (hI : Convex ℝ I)
    (hK : ∀ x ∈ I, HasDerivAt K (K' x) x)
    (hK' : ∀ x ∈ I, ∀ y ∈ I, x ≤ y → K' y - K' x ≤ -γ * (y - x)) :
    StrongConcaveOn I γ K := by
  rw [strongConcaveOn_iff_convex]
  have hfun : (fun x : ℝ => K x + γ / 2 * ‖x‖ ^ 2) = fun x => K x + γ / 2 * x ^ 2 := by
    funext x
    rw [Real.norm_eq_abs, sq_abs]
  rw [hfun]
  have hderiv : ∀ x ∈ I, HasDerivAt (fun x : ℝ => K x + γ / 2 * x ^ 2) (K' x + γ * x) x := by
    intro x hx
    have h1 : HasDerivAt (fun x : ℝ => γ / 2 * x ^ 2) (γ * x) x := by
      have h0 := ((hasDerivAt_id' x).pow 2).const_mul (γ / 2)
      convert h0 using 1
      ring
    exact (hK x hx).add h1
  refine AntitoneOn.concaveOn_of_deriv hI ?_ ?_ ?_
  · exact fun x hx => (hderiv x hx).continuousAt.continuousWithinAt
  · exact fun x hx => (hderiv x (interior_subset hx)).differentiableAt.differentiableWithinAt
  · intro x hx y hy hxy
    rw [(hderiv x (interior_subset hx)).deriv, (hderiv y (interior_subset hy)).deriv]
    have h2 := hK' x (interior_subset hx) y (interior_subset hy) hxy
    linarith

/-- With a nonpositive flow slope the tangent surrogate is as strongly concave as the known
profit. -/
theorem surrogate_strongConcaveOn {K : ℝ → ℝ} {I : Set ℝ} {γ ψ b τb s : ℝ}
    (hK : StrongConcaveOn I γ K) (hs : s ≤ 0) :
    StrongConcaveOn I γ (tangentSurrogate K ψ b τb s) := by
  refine ⟨hK.1, fun x hx y hy a c ha hc hac => ?_⟩
  have h1 := hK.2 hx hy ha hc hac
  have hc' : c = 1 - a := by linarith
  subst hc'
  -- the quadratic `h ↦ (h - ψ) (τb + s (h - b))` is concave because `s ≤ 0`
  have h2 : 0 ≤ -s * (a * (1 - a) * (x - y) ^ 2) :=
    mul_nonneg (neg_nonneg.mpr hs) (mul_nonneg (mul_nonneg ha hc) (sq_nonneg (x - y)))
  have h3 : (a * x + (1 - a) * y - ψ) * (τb + s * (a * x + (1 - a) * y - b))
      - (a * ((x - ψ) * (τb + s * (x - b))) + (1 - a) * ((y - ψ) * (τb + s * (y - b))))
      = -s * (a * (1 - a) * (x - y) ^ 2) := by ring
  simp only [smul_eq_mul, tangentSurrogate] at h1 ⊢
  linarith

/-- Theorem 1, quantitative ascent.  If `bp` maximizes the tangent surrogate at `b` over the
feasible set, deployed profit rises by at least `(γ / 2) (bp - b)^2`. -/
theorem Phi_ascent_quadratic {K τ : ℝ → ℝ} {I : Set ℝ} {ψ γ b bp τ' : ℝ}
    (hK : StrongConcaveOn I γ K) (hconv : ConvexOn ℝ I τ)
    (hb : b ∈ I) (hbp : bp ∈ I) (hψ : ψ ≤ bp)
    (hd : HasDerivAt τ τ' b) (hτ' : τ' ≤ 0)
    (hmax : IsMaxOn (tangentSurrogate K ψ b (τ b) τ') I bp) :
    γ / 2 * (bp - b) ^ 2 ≤ Phi K τ ψ bp - Phi K τ ψ b := by
  have hS : StrongConcaveOn I γ (tangentSurrogate K ψ b (τ b) τ') :=
    surrogate_strongConcaveOn hK hτ'
  have h1 : γ / 2 * (bp - b) ^ 2
      ≤ tangentSurrogate K ψ b (τ b) τ' bp - tangentSurrogate K ψ b (τ b) τ' b :=
    quadratic_growth_of_strongConcaveOn hS hbp hb hmax
  have h2 : tangentSurrogate K ψ b (τ b) τ' bp ≤ Phi K τ ψ bp :=
    surrogate_le_Phi hconv hb hbp hd hψ
  have h3 : tangentSurrogate K ψ b (τ b) τ' b = Phi K τ ψ b := surrogate_self K τ ψ b τ'
  linarith

/-- Deployed profit is nondecreasing along the iteration. -/
theorem Phi_monotone_along {Φ : ℝ → ℝ} {b : ℕ → ℝ} {γ : ℝ} (hγ : 0 ≤ γ)
    (hstep : ∀ k, γ / 2 * (b (k + 1) - b k) ^ 2 ≤ Φ (b (k + 1)) - Φ (b k)) :
    Monotone (fun k => Φ (b k)) := by
  refine monotone_nat_of_le_succ fun k => ?_
  have h1 := hstep k
  have h2 : 0 ≤ γ / 2 * (b (k + 1) - b k) ^ 2 := by positivity
  show Φ (b k) ≤ Φ (b (k + 1))
  linarith

/-- The squared steps have a bounded sum. -/
theorem sum_sq_steps_le {Φ : ℝ → ℝ} {b : ℕ → ℝ} {γ M : ℝ} (hγ : 0 < γ)
    (hstep : ∀ k, γ / 2 * (b (k + 1) - b k) ^ 2 ≤ Φ (b (k + 1)) - Φ (b k))
    (hM : ∀ k, Φ (b k) ≤ M) (n : ℕ) :
    ∑ k ∈ Finset.range n, (b (k + 1) - b k) ^ 2 ≤ 2 * (M - Φ (b 0)) / γ := by
  have h1 : ∑ k ∈ Finset.range n, γ / 2 * (b (k + 1) - b k) ^ 2
      ≤ ∑ k ∈ Finset.range n, (Φ (b (k + 1)) - Φ (b k)) :=
    Finset.sum_le_sum fun k _ => hstep k
  have h2 : ∑ k ∈ Finset.range n, (Φ (b (k + 1)) - Φ (b k)) = Φ (b n) - Φ (b 0) :=
    Finset.sum_range_sub (fun k => Φ (b k)) n
  rw [h2, ← Finset.mul_sum] at h1
  have h3 := hM n
  rw [le_div_iff₀ hγ]
  linarith

/-- Hence the steps vanish. -/
theorem steps_tendsto_zero {Φ : ℝ → ℝ} {b : ℕ → ℝ} {γ M : ℝ} (hγ : 0 < γ)
    (hstep : ∀ k, γ / 2 * (b (k + 1) - b k) ^ 2 ≤ Φ (b (k + 1)) - Φ (b k))
    (hM : ∀ k, Φ (b k) ≤ M) :
    Filter.Tendsto (fun k => b (k + 1) - b k) Filter.atTop (nhds 0) := by
  have hsum : Summable (fun k => (b (k + 1) - b k) ^ 2) :=
    summable_of_sum_range_le (fun k => sq_nonneg _) (fun n => sum_sq_steps_le hγ hstep hM n)
  have h0 : Filter.Tendsto (fun k => (b (k + 1) - b k) ^ 2) Filter.atTop (nhds 0) :=
    hsum.tendsto_atTop_zero
  have h1 : Filter.Tendsto (fun k => Real.sqrt ((b (k + 1) - b k) ^ 2)) Filter.atTop
      (nhds (Real.sqrt 0)) :=
    (Real.continuous_sqrt.tendsto 0).comp h0
  rw [Real.sqrt_zero] at h1
  have h2 : (fun k => Real.sqrt ((b (k + 1) - b k) ^ 2)) = fun k => |b (k + 1) - b k| := by
    funext k
    rw [Real.sqrt_sq_eq_abs]
  rw [h2] at h1
  exact (tendsto_zero_iff_abs_tendsto_zero _).mpr h1

/-- A limit point of the iteration is a fixed point of the update map wherever the map is
continuous. -/
theorem limit_point_fixed {T : ℝ → ℝ} {b : ℕ → ℝ} {x : ℝ} {φ : ℕ → ℕ}
    (hb : ∀ k, b (k + 1) = T (b k))
    (hstep : Filter.Tendsto (fun k => b (k + 1) - b k) Filter.atTop (nhds 0))
    (hφ : StrictMono φ) (hlim : Filter.Tendsto (fun k => b (φ k)) Filter.atTop (nhds x))
    (hT : ContinuousAt T x) : T x = x := by
  have h1 : Filter.Tendsto (fun k => T (b (φ k))) Filter.atTop (nhds (T x)) :=
    hT.tendsto.comp hlim
  have h2 : Filter.Tendsto (fun k => b (φ k + 1) - b (φ k)) Filter.atTop (nhds 0) :=
    hstep.comp hφ.tendsto_atTop
  have h3 : Filter.Tendsto (fun k => b (φ k) + (b (φ k + 1) - b (φ k))) Filter.atTop
      (nhds (x + 0)) := hlim.add h2
  have h4 : (fun k => b (φ k) + (b (φ k + 1) - b (φ k))) = fun k => T (b (φ k)) := by
    funext k
    rw [hb (φ k)]
    ring
  rw [h4, add_zero] at h3
  exact tendsto_nhds_unique h1 h3

/-- Stability of the maximizer of a strongly concave function when the function is perturbed.
This is the inequality behind the continuity of the update map. -/
theorem argmax_stability {f g : ℝ → ℝ} {I : Set ℝ} {γ L x y : ℝ} (hγ : 0 < γ) (hL : 0 ≤ L)
    (hf : StrongConcaveOn I γ f) (hg : StrongConcaveOn I γ g)
    (hx : x ∈ I) (hy : y ∈ I) (hxmax : IsMaxOn f I x) (hymax : IsMaxOn g I y)
    (hLip : |(f x - g x) - (f y - g y)| ≤ L * |x - y|) : |x - y| ≤ L / γ := by
  have h1 : γ / 2 * (x - y) ^ 2 ≤ f x - f y :=
    quadratic_growth_of_strongConcaveOn hf hx hy hxmax
  have h2 : γ / 2 * (y - x) ^ 2 ≤ g y - g x :=
    quadratic_growth_of_strongConcaveOn hg hy hx hymax
  have h3 : (f x - g x) - (f y - g y) ≤ L * |x - y| := (le_abs_self _).trans hLip
  have h4 : (y - x) ^ 2 = |x - y| * |x - y| := by
    rw [abs_mul_abs_self]
    ring
  have h5 : (x - y) ^ 2 = |x - y| * |x - y| := by
    rw [abs_mul_abs_self]
    ring
  rw [h4] at h2
  rw [h5] at h1
  rw [le_div_iff₀ hγ]
  rcases (abs_nonneg (x - y)).eq_or_lt with h0 | hpos
  · rw [← h0, zero_mul]
    exact hL
  · have h6 : |x - y| * (|x - y| * γ) ≤ |x - y| * L := by linarith
    exact le_of_mul_le_mul_left h6 hpos

end PriceCert
