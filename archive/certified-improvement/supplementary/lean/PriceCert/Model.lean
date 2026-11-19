import PriceCert.Defs

/-!
# The model: stable quotes, the shape class, and the exponential instance

Covers Lemma 1 (stable quotes are too wide), Proposition 1 (the reservation-value
microfoundation of the shape class) and the calculus of the instance used in the experiments.
-/

namespace PriceCert

open Set

/-! ## Basic identities -/

theorem Phi_eq_J (K τ : ℝ → ℝ) (ψ h : ℝ) : Phi K τ ψ h = J K ψ h (τ h) := by
  rfl

theorem hasDerivAt_Phi {K τ : ℝ → ℝ} {ψ h K' τ' : ℝ}
    (hK : HasDerivAt K K' h) (hτ : HasDerivAt τ τ' h) :
    HasDerivAt (Phi K τ ψ) (K' + τ h + (h - ψ) * τ') h := by
  have h1 : HasDerivAt (fun x : ℝ => x - ψ) 1 h := (hasDerivAt_id h).sub_const ψ
  have h2 : HasDerivAt (fun x : ℝ => K x + (x - ψ) * τ x) (K' + (1 * τ h + (h - ψ) * τ')) h :=
    hK.add (h1.mul hτ)
  have h3 : Phi K τ ψ = fun x : ℝ => K x + (x - ψ) * τ x := by
    funext x
    rfl
  rw [h3]
  convert h2 using 1
  ring

theorem hasDerivAt_J {K : ℝ → ℝ} {ψ h t K' : ℝ} (hK : HasDerivAt K K' h) :
    HasDerivAt (fun x => J K ψ x t) (K' + t) h := by
  have h1 : HasDerivAt (fun x : ℝ => x - ψ) 1 h := (hasDerivAt_id h).sub_const ψ
  have h2 : HasDerivAt (fun x : ℝ => K x + (x - ψ) * t) (K' + 1 * t) h :=
    hK.add (h1.mul_const t)
  have h3 : (fun x => J K ψ x t) = fun x : ℝ => K x + (x - ψ) * t := by
    funext x
    rfl
  rw [h3]
  convert h2 using 1
  ring

/-- Curvature of deployed profit: `Φ'' = K'' + 2 τ' + (h - ψ) τ''`. -/
theorem hasDerivAt_dPhi {K' τ τ' : ℝ → ℝ} {ψ h K'' τ'' : ℝ}
    (hK' : HasDerivAt K' K'' h) (hτ : HasDerivAt τ (τ' h) h) (hτ' : HasDerivAt τ' τ'' h) :
    HasDerivAt (fun x => K' x + τ x + (x - ψ) * τ' x) (K'' + 2 * τ' h + (h - ψ) * τ'') h := by
  have h1 : HasDerivAt (fun x : ℝ => x - ψ) 1 h := (hasDerivAt_id h).sub_const ψ
  have h2 : HasDerivAt (fun x : ℝ => K' x + τ x + (x - ψ) * τ' x)
      (K'' + τ' h + (1 * τ' h + (h - ψ) * τ'')) h :=
    (hK'.add hτ).add (h1.mul hτ')
  convert h2 using 1
  ring

/-! ## Lemma 1: stable quotes are too wide -/

/-- Lemma 1(a). At a stable quote the slope of deployed profit is `(h - ψ) τ'(h)`. -/
theorem hasDerivAt_Phi_of_stable {K τ : ℝ → ℝ} {ψ h K' τ' : ℝ}
    (hK : HasDerivAt K K' h) (hτ : HasDerivAt τ τ' h) (hstab : K' + τ h = 0) :
    HasDerivAt (Phi K τ ψ) ((h - ψ) * τ') h := by
  have h1 : HasDerivAt (Phi K τ ψ) (K' + τ h + (h - ψ) * τ') h := hasDerivAt_Phi hK hτ
  rw [hstab, zero_add] at h1
  exact h1

theorem slope_at_stable_nonpos {ψ h τ' : ℝ} (hψ : ψ ≤ h) (hτ' : τ' ≤ 0) : (h - ψ) * τ' ≤ 0 := by
  exact mul_nonpos_of_nonneg_of_nonpos (sub_nonneg.mpr hψ) hτ'

theorem slope_at_stable_neg {ψ h τ' : ℝ} (hψ : ψ < h) (hτ' : τ' < 0) : (h - ψ) * τ' < 0 := by
  exact mul_neg_of_pos_of_neg (sub_pos.mpr hψ) hτ'

/-- A negative slope means that slightly tighter quotes earn strictly more. -/
theorem eventually_lt_of_deriv_neg {Φ : ℝ → ℝ} {hs d : ℝ} (hd : HasDerivAt Φ d hs) (hneg : d < 0) :
    ∀ᶠ h in nhdsWithin hs (Set.Iio hs), Φ hs < Φ h := by
  have h1 : Filter.Tendsto (slope Φ hs) (nhdsWithin hs (Set.Iio hs)) (nhds d) :=
    (hasDerivAt_iff_tendsto_slope.mp hd).mono_left (nhdsLT_le_nhdsNE hs)
  have h2 : ∀ᶠ h in nhdsWithin hs (Set.Iio hs), slope Φ hs h < 0 :=
    h1.eventually (gt_mem_nhds hneg)
  filter_upwards [h2, self_mem_nhdsWithin] with h hslope hlt
  have hlt' : h - hs < 0 := sub_neg.mpr hlt
  rw [slope_def_field] at hslope
  by_contra hcon
  have hle : Φ h - Φ hs ≤ 0 := sub_nonpos.mpr (not_lt.mp hcon)
  have hge : 0 ≤ (Φ h - Φ hs) / (h - hs) := div_nonneg_of_nonpos hle hlt'.le
  exact absurd hslope (not_lt.mpr hge)

/-- A concave function whose derivative vanishes at a point of the set is maximal there. -/
theorem isMaxOn_of_concaveOn_of_hasDerivAt_zero {f : ℝ → ℝ} {I : Set ℝ} {b : ℝ}
    (hf : ConcaveOn ℝ I f) (hb : b ∈ I) (hd : HasDerivAt f 0 b) : IsMaxOn f I b := by
  intro x hx
  show f x ≤ f b
  rcases lt_trichotomy x b with hxb | hxb | hxb
  · have h1 : 0 ≤ slope f x b := hf.le_slope_of_hasDerivAt hx hb hxb hd
    rw [slope_def_field] at h1
    have h2 : 0 < b - x := sub_pos.mpr hxb
    have h3 : 0 ≤ f b - f x := by
      have := mul_nonneg h1 h2.le
      rwa [div_mul_cancel₀ _ h2.ne'] at this
    linarith
  · rw [hxb]
  · have h1 : slope f b x ≤ 0 := hf.slope_le_of_hasDerivAt hb hx hxb hd
    rw [slope_def_field] at h1
    have h2 : 0 < x - b := sub_pos.mpr hxb
    have h3 : f x - f b ≤ 0 := by
      have := mul_nonpos_of_nonpos_of_nonneg h1 h2.le
      rwa [div_mul_cancel₀ _ h2.ne'] at this
    linarith

/-- The first-order condition `K'(h) + t = 0` identifies the frozen best response. -/
theorem isMaxOn_J_of_foc {K : ℝ → ℝ} {I : Set ℝ} {ψ t hs K' : ℝ}
    (hK : ConcaveOn ℝ I K) (hs_mem : hs ∈ I) (hKd : HasDerivAt K K' hs) (hfoc : K' + t = 0) :
    IsMaxOn (fun x => J K ψ x t) I hs := by
  have hconc : ConcaveOn ℝ I (fun x => J K ψ x t) := by
    refine ⟨hK.1, ?_⟩
    intro x hx y hy a b ha hb hab
    have h1 : a • K x + b • K y ≤ K (a • x + b • y) := hK.2 hx hy ha hb hab
    simp only [smul_eq_mul] at h1 ⊢
    show a * (K x + (x - ψ) * t) + b * (K y + (y - ψ) * t)
      ≤ K (a * x + b * y) + (a * x + b * y - ψ) * t
    have h2 : a * ((x - ψ) * t) + b * ((y - ψ) * t) = (a * x + b * y - ψ) * t := by
      have hb' : b = 1 - a := by linarith
      subst hb'
      ring
    linarith
  have hderiv : HasDerivAt (fun x => J K ψ x t) 0 hs := by
    have h1 : HasDerivAt (fun x => J K ψ x t) (K' + t) hs := hasDerivAt_J hKd
    rwa [hfoc] at h1
  exact isMaxOn_of_concaveOn_of_hasDerivAt_zero hconc hs_mem hderiv

/-- Lemma 1(b). No quote wider than a stable quote earns more deployed profit.  Only
monotonicity of the flow is used. -/
theorem Phi_le_Phi_stable_of_ge {K τ : ℝ → ℝ} {I : Set ℝ} {ψ hs h : ℝ}
    (hanti : AntitoneOn τ I) (hs_mem : hs ∈ I) (h_mem : h ∈ I) (hψ : ψ ≤ h)
    (hmax : IsMaxOn (fun x => J K ψ x (τ hs)) I hs) (hge : hs ≤ h) :
    Phi K τ ψ h ≤ Phi K τ ψ hs := by
  have h1 : τ h ≤ τ hs := hanti hs_mem h_mem hge
  have h2 : J K ψ h (τ hs) ≤ J K ψ hs (τ hs) := hmax h_mem
  have h3 : (h - ψ) * τ h ≤ (h - ψ) * τ hs := mul_le_mul_of_nonneg_left h1 (sub_nonneg.mpr hψ)
  unfold J at h2
  unfold Phi
  linarith

/-- Lemma 1(c). The flow at a stable quote is known without data. -/
theorem tau_stable {K' τs : ℝ} (hstab : K' + τs = 0) : τs = -K' := by
  linarith

/-- Lemma 1(c). Deployed profit at a stable quote is known without data. -/
theorem Phi_stable {K τ : ℝ → ℝ} {ψ h K' : ℝ} (hstab : K' + τ h = 0) :
    Phi K τ ψ h = K h - (h - ψ) * K' := by
  have h1 : τ h = -K' := by linarith
  unfold Phi
  rw [h1]
  ring

/-! ## Proposition 1: a reservation-value model yields the shape class -/

/-- A survival function whose density is nonincreasing is convex. -/
theorem survival_convexOn {S f : ℝ → ℝ} {D : Set ℝ} (hD : Convex ℝ D) (hcont : ContinuousOn S D)
    (hderiv : ∀ x ∈ interior D, HasDerivAt S (-f x) x) (hf : AntitoneOn f (interior D)) :
    ConvexOn ℝ D S := by
  have hdiff : DifferentiableOn ℝ S (interior D) := fun x hx =>
    (hderiv x hx).differentiableAt.differentiableWithinAt
  have hmono : MonotoneOn (deriv S) (interior D) := by
    intro x hx y hy hxy
    rw [(hderiv x hx).deriv, (hderiv y hy).deriv]
    exact neg_le_neg (hf hx hy hxy)
  exact hmono.convexOn_of_deriv hD hcont hdiff

/-- A survival function with a nonnegative density is nonincreasing. -/
theorem survival_antitoneOn {S f : ℝ → ℝ} {D : Set ℝ} (hD : Convex ℝ D)
    (hcont : ContinuousOn S D) (hderiv : ∀ x ∈ interior D, HasDerivAt S (-f x) x)
    (hf0 : ∀ x ∈ interior D, 0 ≤ f x) : AntitoneOn S D := by
  have hdiff : DifferentiableOn ℝ S (interior D) := fun x hx =>
    (hderiv x hx).differentiableAt.differentiableWithinAt
  refine antitoneOn_of_deriv_nonpos hD hcont hdiff ?_
  intro x hx
  rw [(hderiv x hx).deriv]
  exact neg_nonpos.mpr (hf0 x hx)

theorem flow_convexOn {S : ℝ → ℝ} {D : Set ℝ} {C0 lam : ℝ} (hlam : 0 ≤ lam)
    (hS : ConvexOn ℝ D S) : ConvexOn ℝ D (fun h => C0 + lam * S h) := by
  refine ⟨hS.1, ?_⟩
  intro x hx y hy a b ha hb hab
  have h1 : S (a • x + b • y) ≤ a • S x + b • S y := hS.2 hx hy ha hb hab
  simp only [smul_eq_mul] at h1 ⊢
  have h2 : lam * S (a * x + b * y) ≤ lam * (a * S x + b * S y) :=
    mul_le_mul_of_nonneg_left h1 hlam
  have h3 : a * (C0 + lam * S x) + b * (C0 + lam * S y)
      = C0 + lam * (a * S x + b * S y) := by
    have hb' : b = 1 - a := by linarith
    subst hb'
    ring
  linarith

theorem flow_antitoneOn {S : ℝ → ℝ} {D : Set ℝ} {C0 lam : ℝ} (hlam : 0 ≤ lam)
    (hS : AntitoneOn S D) : AntitoneOn (fun h => C0 + lam * S h) D := by
  intro x hx y hy hxy
  have h1 : S y ≤ S x := hS hx hy hxy
  have h2 : lam * S y ≤ lam * S x := mul_le_mul_of_nonneg_left h1 hlam
  show C0 + lam * S y ≤ C0 + lam * S x
  linarith

theorem flow_nonneg {S : ℝ → ℝ} {C0 lam h : ℝ} (hC0 : 0 ≤ C0) (hlam : 0 ≤ lam) (hS : 0 ≤ S h) :
    0 ≤ C0 + lam * S h := by
  exact add_nonneg hC0 (mul_nonneg hlam hS)

/-! ## The exponential instance used in the experiments -/

theorem hasDerivAt_expFlow (C0 C1 c h : ℝ) :
    HasDerivAt (fun x => C0 + C1 * Real.exp (-c * x)) (-c * C1 * Real.exp (-c * h)) h := by
  have h1 : HasDerivAt (fun x : ℝ => -c * x) (-c * 1) h := (hasDerivAt_id h).const_mul (-c)
  have h2 : HasDerivAt (fun x : ℝ => Real.exp (-c * x)) (Real.exp (-c * h) * (-c * 1)) h := h1.exp
  have h3 : HasDerivAt (fun x : ℝ => C0 + C1 * Real.exp (-c * x))
      (C1 * (Real.exp (-c * h) * (-c * 1))) h := (h2.const_mul C1).const_add C0
  convert h3 using 1
  ring

theorem hasDerivAt_expFlow' (C1 c h : ℝ) :
    HasDerivAt (fun x => -c * C1 * Real.exp (-c * x)) (c ^ 2 * C1 * Real.exp (-c * h)) h := by
  have h1 : HasDerivAt (fun x : ℝ => -c * x) (-c * 1) h := (hasDerivAt_id h).const_mul (-c)
  have h2 : HasDerivAt (fun x : ℝ => Real.exp (-c * x)) (Real.exp (-c * h) * (-c * 1)) h := h1.exp
  have h3 : HasDerivAt (fun x : ℝ => -c * C1 * Real.exp (-c * x))
      (-c * C1 * (Real.exp (-c * h) * (-c * 1))) h := h2.const_mul (-c * C1)
  convert h3 using 1
  ring

theorem expFlow_convexOn {C0 C1 c : ℝ} (hC1 : 0 ≤ C1) :
    ConvexOn ℝ Set.univ (fun x => C0 + C1 * Real.exp (-c * x)) := by
  refine ⟨convex_univ, ?_⟩
  intro x _ y _ a b ha hb hab
  have h1 : Real.exp (a • (-c * x) + b • (-c * y))
      ≤ a • Real.exp (-c * x) + b • Real.exp (-c * y) :=
    convexOn_exp.2 (Set.mem_univ _) (Set.mem_univ _) ha hb hab
  simp only [smul_eq_mul] at h1 ⊢
  have h2 : -c * (a * x + b * y) = a * (-c * x) + b * (-c * y) := by ring
  rw [h2]
  have h3 : C1 * Real.exp (a * (-c * x) + b * (-c * y))
      ≤ C1 * (a * Real.exp (-c * x) + b * Real.exp (-c * y)) :=
    mul_le_mul_of_nonneg_left h1 hC1
  have h4 : a * (C0 + C1 * Real.exp (-c * x)) + b * (C0 + C1 * Real.exp (-c * y))
      = C0 + C1 * (a * Real.exp (-c * x) + b * Real.exp (-c * y)) := by
    have hb' : b = 1 - a := by linarith
    subst hb'
    ring
  linarith

theorem expFlow_antitone {C0 C1 c : ℝ} (hC1 : 0 ≤ C1) (hc : 0 ≤ c) :
    Antitone (fun x => C0 + C1 * Real.exp (-c * x)) := by
  intro x y hxy
  have h1 : -c * y ≤ -c * x := by
    have := mul_le_mul_of_nonneg_left hxy hc
    linarith
  have h2 : Real.exp (-c * y) ≤ Real.exp (-c * x) := Real.exp_le_exp.mpr h1
  have h3 : C1 * Real.exp (-c * y) ≤ C1 * Real.exp (-c * x) := mul_le_mul_of_nonneg_left h2 hC1
  show C0 + C1 * Real.exp (-c * y) ≤ C0 + C1 * Real.exp (-c * x)
  linarith

theorem expFlow_nonneg {C0 C1 c : ℝ} (hC0 : 0 ≤ C0) (hC1 : 0 ≤ C1) (x : ℝ) :
    0 ≤ C0 + C1 * Real.exp (-c * x) := by
  exact add_nonneg hC0 (mul_nonneg hC1 (Real.exp_pos _).le)

/-- First derivative of the known profit `K(h) = h A e^{-k h} - w (h - href)^2`. -/
theorem hasDerivAt_expK (A k w href h : ℝ) :
    HasDerivAt (fun x => x * (A * Real.exp (-k * x)) - w * (x - href) ^ 2)
      (A * Real.exp (-k * h) * (1 - k * h) - 2 * w * (h - href)) h := by
  have h1 : HasDerivAt (fun x : ℝ => -k * x) (-k * 1) h := (hasDerivAt_id h).const_mul (-k)
  have h2 : HasDerivAt (fun x : ℝ => Real.exp (-k * x)) (Real.exp (-k * h) * (-k * 1)) h := h1.exp
  have h3 : HasDerivAt (fun x : ℝ => A * Real.exp (-k * x))
      (A * (Real.exp (-k * h) * (-k * 1))) h := h2.const_mul A
  have h4 : HasDerivAt (fun x : ℝ => x * (A * Real.exp (-k * x)))
      (1 * (A * Real.exp (-k * h)) + h * (A * (Real.exp (-k * h) * (-k * 1)))) h :=
    (hasDerivAt_id h).mul h3
  have h5 : HasDerivAt (fun x : ℝ => x - href) 1 h := (hasDerivAt_id h).sub_const href
  have h6 : HasDerivAt (fun x : ℝ => (x - href) ^ 2) (2 * (h - href) ^ (2 - 1) * 1) h :=
    h5.pow 2
  have h7 : HasDerivAt (fun x : ℝ => x * (A * Real.exp (-k * x)) - w * (x - href) ^ 2)
      (1 * (A * Real.exp (-k * h)) + h * (A * (Real.exp (-k * h) * (-k * 1)))
        - w * (2 * (h - href) ^ (2 - 1) * 1)) h := h4.sub (h6.const_mul w)
  convert h7 using 1
  ring

/-- Second derivative of the known profit: `K'' = -(A k e^{-k h} (2 - k h) + 2 w)`. -/
theorem hasDerivAt_expK' (A k w href h : ℝ) :
    HasDerivAt (fun x => A * Real.exp (-k * x) * (1 - k * x) - 2 * w * (x - href))
      (-(A * k * Real.exp (-k * h) * (2 - k * h) + 2 * w)) h := by
  have h1 : HasDerivAt (fun x : ℝ => -k * x) (-k * 1) h := (hasDerivAt_id h).const_mul (-k)
  have h2 : HasDerivAt (fun x : ℝ => Real.exp (-k * x)) (Real.exp (-k * h) * (-k * 1)) h := h1.exp
  have h3 : HasDerivAt (fun x : ℝ => A * Real.exp (-k * x))
      (A * (Real.exp (-k * h) * (-k * 1))) h := h2.const_mul A
  have h4 : HasDerivAt (fun x : ℝ => 1 - k * x) (-(k * 1)) h :=
    ((hasDerivAt_id h).const_mul k).const_sub 1
  have h5 : HasDerivAt (fun x : ℝ => A * Real.exp (-k * x) * (1 - k * x))
      (A * (Real.exp (-k * h) * (-k * 1)) * (1 - k * h) + A * Real.exp (-k * h) * (-(k * 1))) h :=
    h3.mul h4
  have h6 : HasDerivAt (fun x : ℝ => x - href) 1 h := (hasDerivAt_id h).sub_const href
  have h7 : HasDerivAt (fun x : ℝ => A * Real.exp (-k * x) * (1 - k * x) - 2 * w * (x - href))
      (A * (Real.exp (-k * h) * (-k * 1)) * (1 - k * h) + A * Real.exp (-k * h) * (-(k * 1))
        - 2 * w * 1) h := h5.sub (h6.const_mul (2 * w))
  convert h7 using 1
  ring

theorem exp_mul_two_sub_ge (x : ℝ) : -Real.exp (-3) ≤ Real.exp (-x) * (2 - x) := by
  have h1 : x - 3 + 1 ≤ Real.exp (x - 3) := Real.add_one_le_exp (x - 3)
  have h2 : Real.exp (-x) * Real.exp (x - 3) = Real.exp (-3) := by
    rw [← Real.exp_add]
    congr 1
    ring
  have h3 : 0 ≤ Real.exp (-x) := (Real.exp_pos _).le
  have h4 : Real.exp (-x) * (x - 3 + 1) ≤ Real.exp (-x) * Real.exp (x - 3) :=
    mul_le_mul_of_nonneg_left h1 h3
  rw [h2] at h4
  have h5 : Real.exp (-x) * (2 - x) = -(Real.exp (-x) * (x - 3 + 1)) := by ring
  rw [h5]
  exact neg_le_neg h4

/-- The curvature `γ(h) = -K''(h)` is bounded below on the whole line. -/
theorem expK_curvature_lower {A k w : ℝ} (hA : 0 ≤ A) (hk : 0 ≤ k) (h : ℝ) :
    2 * w - A * k * Real.exp (-3) ≤ A * k * Real.exp (-k * h) * (2 - k * h) + 2 * w := by
  have h1 : -Real.exp (-3) ≤ Real.exp (-(k * h)) * (2 - k * h) := exp_mul_two_sub_ge (k * h)
  rw [← neg_mul] at h1
  have h2 : 0 ≤ A * k := mul_nonneg hA hk
  have h3 : A * k * -Real.exp (-3) ≤ A * k * (Real.exp (-k * h) * (2 - k * h)) :=
    mul_le_mul_of_nonneg_left h1 h2
  have h4 : A * k * Real.exp (-k * h) * (2 - k * h)
      = A * k * (Real.exp (-k * h) * (2 - k * h)) := by ring
  rw [h4]
  linarith

/-- The curvature `γ(h) = -K''(h)` is bounded above for nonnegative quotes. -/
theorem expK_curvature_upper {A k w h : ℝ} (hA : 0 ≤ A) (hk : 0 ≤ k) (hh : 0 ≤ h) :
    A * k * Real.exp (-k * h) * (2 - k * h) + 2 * w ≤ 2 * A * k + 2 * w := by
  have hkh : 0 ≤ k * h := mul_nonneg hk hh
  have hpos : 0 < Real.exp (-k * h) := Real.exp_pos _
  have hle1 : Real.exp (-k * h) ≤ 1 := by
    rw [← Real.exp_zero]
    apply Real.exp_le_exp.mpr
    rw [neg_mul]
    exact neg_nonpos.mpr hkh
  have hkey : Real.exp (-k * h) * (2 - k * h) ≤ 2 := by
    rcases le_total 0 (2 - k * h) with hsign | hsign
    · have h1 : Real.exp (-k * h) * (2 - k * h) ≤ 1 * (2 - k * h) :=
        mul_le_mul_of_nonneg_right hle1 hsign
      linarith
    · have h1 : Real.exp (-k * h) * (2 - k * h) ≤ 0 :=
        mul_nonpos_of_nonneg_of_nonpos hpos.le hsign
      linarith
  have h2 : 0 ≤ A * k := mul_nonneg hA hk
  have h3 : A * k * (Real.exp (-k * h) * (2 - k * h)) ≤ A * k * 2 :=
    mul_le_mul_of_nonneg_left hkey h2
  have h4 : A * k * Real.exp (-k * h) * (2 - k * h)
      = A * k * (Real.exp (-k * h) * (2 - k * h)) := by ring
  rw [h4]
  linarith

end PriceCert
