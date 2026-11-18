import CreditCert.Defs

/-!
# Take-up curves

The derivative of profit per applicant and the fact that a negative derivative makes slightly lower rates
strictly better (used by Proposition "a flatter believed slope prices too high"), and Proposition "reservation
spreads": if an applicant accepts exactly when the offered spread is below a reservation spread whose density is
nonincreasing, take-up is nonincreasing and convex.  The affine forms `C0 + λ S` allow a share of applicants who
accept at every admissible rate.
-/

namespace CreditCert

open Set

/-! ## Basic identities -/

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

/-! ## A negative profit slope means that a small rate cut earns more -/

/-- If profit has a negative derivative at `hs`, slightly lower rates earn strictly more. -/
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

/-! ## Proposition "reservation spreads" -/

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

/-- Take-up `C0 + λ S` is convex when `S` is and `λ ≥ 0`. -/
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

/-- Take-up `C0 + λ S` is nonincreasing when `S` is and `λ ≥ 0`. -/
theorem flow_antitoneOn {S : ℝ → ℝ} {D : Set ℝ} {C0 lam : ℝ} (hlam : 0 ≤ lam)
    (hS : AntitoneOn S D) : AntitoneOn (fun h => C0 + lam * S h) D := by
  intro x hx y hy hxy
  have h1 : S y ≤ S x := hS hx hy hxy
  have h2 : lam * S y ≤ lam * S x := mul_le_mul_of_nonneg_left h1 hlam
  show C0 + lam * S y ≤ C0 + lam * S x
  linarith

/-- Take-up `C0 + λ S` is nonnegative when all three parts are. -/
theorem flow_nonneg {S : ℝ → ℝ} {C0 lam h : ℝ} (hC0 : 0 ≤ C0) (hlam : 0 ≤ lam) (hS : 0 ≤ S h) :
    0 ≤ C0 + lam * S h := by
  exact add_nonneg hC0 (mul_nonneg hlam hS)


end CreditCert
