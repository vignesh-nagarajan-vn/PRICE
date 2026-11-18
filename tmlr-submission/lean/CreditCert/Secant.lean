import CreditCert.Defs

/-!
# Secant bounds for a convex nonincreasing take-up curve

Covers the envelope rules of Theorem "certified gain" (monotone bound, chord extensions with exact values and
with confidence intervals) and Proposition "two-anchor tightness" (the bound from two anchors cannot be improved).
-/

namespace CreditCert

open Set

/-! ## Chord extensions with exact values -/

/-- Three-point form of convexity, cleared of denominators: for `x ≤ y ≤ z` with `x < z` and
`x, z` in the domain, `(z - x) τ(y) ≤ (z - y) τ(x) + (y - x) τ(z)`. -/
private theorem convexOn_three_point {τ : ℝ → ℝ} {S : Set ℝ} {x y z : ℝ} (hconv : ConvexOn ℝ S τ)
    (hx : x ∈ S) (hz : z ∈ S) (hxy : x ≤ y) (hyz : y ≤ z) (hxz : x < z) :
    (z - x) * τ y ≤ (z - y) * τ x + (y - x) * τ z := by
  have hpos : 0 < z - x := sub_pos.mpr hxz
  have ha : 0 ≤ (z - y) / (z - x) := div_nonneg (sub_nonneg.mpr hyz) hpos.le
  have hb : 0 ≤ (y - x) / (z - x) := div_nonneg (sub_nonneg.mpr hxy) hpos.le
  have hab : (z - y) / (z - x) + (y - x) / (z - x) = 1 := by
    field_simp
    ring
  have key := hconv.2 hx hz ha hb hab
  have hy : ((z - y) / (z - x)) • x + ((y - x) / (z - x)) • z = y := by
    simp only [smul_eq_mul]
    field_simp
    ring
  rw [hy] at key
  simp only [smul_eq_mul] at key
  calc (z - x) * τ y
      ≤ (z - x) * ((z - y) / (z - x) * τ x + (y - x) / (z - x) * τ z) :=
        mul_le_mul_of_nonneg_left key hpos.le
    _ = (z - y) * τ x + (y - x) * τ z := by
        field_simp

/-- The chord through two points of a convex function, extended to the left, lies below the
function. -/
theorem chord_ext_left {τ : ℝ → ℝ} {S : Set ℝ} {h x1 x2 : ℝ} (hconv : ConvexOn ℝ S τ)
    (hh : h ∈ S) (hx2 : x2 ∈ S) (h1 : h ≤ x1) (h12 : x1 < x2) :
    τ x1 + (τ x1 - τ x2) * (x1 - h) / (x2 - x1) ≤ τ h := by
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  have key := convexOn_three_point hconv hh hx2 h1 h12.le (lt_of_le_of_lt h1 h12)
  have heq : τ x1 + (τ x1 - τ x2) * (x1 - h) / (x2 - x1)
      = ((x2 - h) * τ x1 - (x1 - h) * τ x2) / (x2 - x1) := by
    field_simp
    ring
  rw [heq, div_le_iff₀ hd]
  linarith

/-- The chord through two points of a convex function, extended to the right, lies below the
function. -/
theorem chord_ext_right {τ : ℝ → ℝ} {S : Set ℝ} {h x1 x2 : ℝ} (hconv : ConvexOn ℝ S τ)
    (hx1 : x1 ∈ S) (hh : h ∈ S) (h12 : x1 < x2) (h2 : x2 ≤ h) :
    τ x2 + (τ x2 - τ x1) * (h - x2) / (x2 - x1) ≤ τ h := by
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  have key := convexOn_three_point hconv hx1 hh h12.le h2 (lt_of_lt_of_le h12 h2)
  have heq : τ x2 + (τ x2 - τ x1) * (h - x2) / (x2 - x1)
      = ((h - x1) * τ x2 - (h - x2) * τ x1) / (x2 - x1) := by
    field_simp
    ring
  rw [heq, div_le_iff₀ hd]
  linarith

/-- Between two points a convex function lies below its chord. -/
theorem chord_upper {τ : ℝ → ℝ} {S : Set ℝ} {h x1 x2 : ℝ} (hconv : ConvexOn ℝ S τ)
    (hx1 : x1 ∈ S) (hx2 : x2 ∈ S) (h1 : x1 ≤ h) (h2 : h ≤ x2) (h12 : x1 < x2) :
    τ h ≤ τ x1 + (τ x2 - τ x1) * (h - x1) / (x2 - x1) := by
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  have key := convexOn_three_point hconv hx1 hx2 h1 h2 h12
  have heq : τ x1 + (τ x2 - τ x1) * (h - x1) / (x2 - x1)
      = ((x2 - h) * τ x1 + (h - x1) * τ x2) / (x2 - x1) := by
    field_simp
    ring
  rw [heq, le_div_iff₀ hd]
  linarith

/-! ## The envelope rules with confidence intervals -/

/-- Rule (M). A lower confidence limit at an anchor to the right is a lower bound. -/
theorem mono_lower {τ : ℝ → ℝ} {S : Set ℝ} {h xa La : ℝ} (hanti : AntitoneOn τ S)
    (hh : h ∈ S) (hxa : xa ∈ S) (hle : h ≤ xa) (hLa : La ≤ τ xa) : La ≤ τ h :=
  hLa.trans (hanti hh hxa hle)

/-- Rule (CL). Chord extension to the left of two anchors with interval data. -/
theorem chord_ext_left_interval {τ : ℝ → ℝ} {S : Set ℝ} {h x1 x2 L1 U2 : ℝ}
    (hconv : ConvexOn ℝ S τ) (hanti : AntitoneOn τ S) (hh : h ∈ S) (hx1 : x1 ∈ S) (hx2 : x2 ∈ S)
    (h1 : h ≤ x1) (h12 : x1 < x2) (hL1 : L1 ≤ τ x1) (hU2 : τ x2 ≤ U2) :
    L1 + max (L1 - U2) 0 * (x1 - h) / (x2 - x1) ≤ τ h := by
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  have hc : 0 ≤ (x1 - h) / (x2 - x1) := div_nonneg (sub_nonneg.mpr h1) hd.le
  have hchord := chord_ext_left hconv hh hx2 h1 h12
  have hmono : τ x1 ≤ τ h := hanti hh hx1 h1
  rw [mul_div_assoc] at hchord ⊢
  rcases le_total (L1 - U2) 0 with hneg | hpos
  · rw [max_eq_right hneg, zero_mul, add_zero]
    exact hL1.trans hmono
  · rw [max_eq_left hpos]
    have hmul : (L1 - U2) * ((x1 - h) / (x2 - x1)) ≤ (τ x1 - τ x2) * ((x1 - h) / (x2 - x1)) :=
      mul_le_mul_of_nonneg_right (by linarith) hc
    linarith

/-- Rule (CR). Chord extension to the right of two anchors with interval data. -/
theorem chord_ext_right_interval {τ : ℝ → ℝ} {S : Set ℝ} {h x1 x2 U1 L2 : ℝ}
    (hconv : ConvexOn ℝ S τ) (hx1 : x1 ∈ S) (hh : h ∈ S) (h12 : x1 < x2) (h2 : x2 ≤ h)
    (hU1 : τ x1 ≤ U1) (hL2 : L2 ≤ τ x2) :
    L2 + min (L2 - U1) 0 * (h - x2) / (x2 - x1) ≤ τ h := by
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  have hc : 0 ≤ (h - x2) / (x2 - x1) := div_nonneg (sub_nonneg.mpr h2) hd.le
  have hchord := chord_ext_right hconv hx1 hh h12 h2
  rw [mul_div_assoc] at hchord ⊢
  have hmin : min (L2 - U1) 0 ≤ τ x2 - τ x1 := (min_le_left _ _).trans (by linarith)
  have hmul : min (L2 - U1) 0 * ((h - x2) / (x2 - x1)) ≤ (τ x2 - τ x1) * ((h - x2) / (x2 - x1)) :=
    mul_le_mul_of_nonneg_right hmin hc
  linarith

/-! ## Proposition "two-anchor tightness": the two-anchor envelope is attained -/

/-- An affine function of one real variable is convex on the whole line. -/
private theorem convexOn_affine_line (c m x0 : ℝ) :
    ConvexOn ℝ Set.univ (fun h : ℝ => c + m * (h - x0)) := by
  refine ⟨convex_univ, fun x _ y _ a b _ _ hab => le_of_eq ?_⟩
  simp only [smul_eq_mul]
  have hb : b = 1 - a := by linarith
  subst hb
  ring

/-- The maximum of an affine function and a constant is convex on the whole line. -/
private theorem convexOn_max_affine_const (c m x0 k : ℝ) :
    ConvexOn ℝ Set.univ (fun h : ℝ => max (c + m * (h - x0)) k) :=
  (convexOn_affine_line c m x0).sup (convexOn_const k convex_univ)

/-- The maximum of a nonincreasing affine function and a constant is nonincreasing. -/
private theorem antitone_max_affine_const {c m x0 k : ℝ} (hm : m ≤ 0) :
    Antitone (fun h : ℝ => max (c + m * (h - x0)) k) := by
  intro a b hab
  have hmul : m * (b - x0) ≤ m * (a - x0) :=
    mul_le_mul_of_nonpos_left (sub_le_sub_right hab x0) hm
  exact max_le_max (by linarith) le_rfl

theorem twoPoint_convexOn (x1 x2 t1 t2 : ℝ) : ConvexOn ℝ Set.univ (twoPoint x1 x2 t1 t2) :=
  convexOn_max_affine_const t1 ((t2 - t1) / (x2 - x1)) x1 t2

theorem twoPoint_antitone {x1 x2 t1 t2 : ℝ} (h12 : x1 < x2) (ht : t2 ≤ t1) :
    Antitone (twoPoint x1 x2 t1 t2) :=
  antitone_max_affine_const
    (div_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr ht) (sub_pos.mpr h12).le)

theorem twoPoint_nonneg {x1 x2 t1 t2 : ℝ} (ht2 : 0 ≤ t2) (h : ℝ) :
    0 ≤ twoPoint x1 x2 t1 t2 h := by
  unfold twoPoint
  exact le_max_of_le_right ht2

theorem twoPoint_left {x1 x2 t1 t2 : ℝ} (ht : t2 ≤ t1) : twoPoint x1 x2 t1 t2 x1 = t1 := by
  unfold twoPoint
  rw [sub_self, mul_zero, add_zero]
  exact max_eq_left ht

theorem twoPoint_right {x1 x2 t1 t2 : ℝ} (h12 : x1 < x2) : twoPoint x1 x2 t1 t2 x2 = t2 := by
  unfold twoPoint
  rw [div_mul_cancel₀ _ (sub_ne_zero.mpr h12.ne'), add_sub_cancel, max_self]

/-- To the left of both anchors the curve `twoPoint` equals the chord-extension bound. -/
theorem twoPoint_attains_left {x1 x2 t1 t2 h : ℝ} (h12 : x1 < x2) (ht : t2 ≤ t1) (hh : h ≤ x1) :
    twoPoint x1 x2 t1 t2 h = t1 + max (t1 - t2) 0 * (x1 - h) / (x2 - x1) := by
  unfold twoPoint
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  rw [max_eq_left (sub_nonneg.mpr ht)]
  have heq : t1 + (t2 - t1) / (x2 - x1) * (h - x1) = t1 + (t1 - t2) * (x1 - h) / (x2 - x1) := by
    field_simp
    ring
  rw [heq]
  apply max_eq_left
  have hnn : 0 ≤ (t1 - t2) * (x1 - h) / (x2 - x1) :=
    div_nonneg (mul_nonneg (sub_nonneg.mpr ht) (sub_nonneg.mpr hh)) hd.le
  linarith

/-- Between the anchors, the curve with its kink at `h` passes through both anchors and equals the
monotone bound `t2` at `h`. -/
theorem twoPoint_attains_between {x1 x2 t1 t2 h : ℝ} (h1 : x1 < h) (h2 : h ≤ x2) (ht : t2 ≤ t1) :
    twoPoint x1 h t1 t2 x1 = t1 ∧ twoPoint x1 h t1 t2 x2 = t2 ∧ twoPoint x1 h t1 t2 h = t2 := by
  refine ⟨twoPoint_left ht, ?_, twoPoint_right h1⟩
  unfold twoPoint
  apply max_eq_right
  have hd : 0 < h - x1 := sub_pos.mpr h1
  have hm : (t2 - t1) / (h - x1) ≤ 0 :=
    div_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr ht) hd.le
  have hmul : (t2 - t1) / (h - x1) * (x2 - x1) ≤ (t2 - t1) / (h - x1) * (h - x1) :=
    mul_le_mul_of_nonpos_left (sub_le_sub_right h2 x1) hm
  rw [div_mul_cancel₀ _ hd.ne'] at hmul
  linarith

theorem chordFloor_convexOn (x1 x2 t1 t2 : ℝ) : ConvexOn ℝ Set.univ (chordFloor x1 x2 t1 t2) :=
  convexOn_max_affine_const t1 ((t2 - t1) / (x2 - x1)) x1 0

theorem chordFloor_antitone {x1 x2 t1 t2 : ℝ} (h12 : x1 < x2) (ht : t2 ≤ t1) :
    Antitone (chordFloor x1 x2 t1 t2) :=
  antitone_max_affine_const
    (div_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr ht) (sub_pos.mpr h12).le)

theorem chordFloor_nonneg (x1 x2 t1 t2 h : ℝ) : 0 ≤ chordFloor x1 x2 t1 t2 h := by
  unfold chordFloor
  exact le_max_right _ _

theorem chordFloor_left {x1 x2 t1 t2 : ℝ} (ht1 : 0 ≤ t1) : chordFloor x1 x2 t1 t2 x1 = t1 := by
  unfold chordFloor
  rw [sub_self, mul_zero, add_zero]
  exact max_eq_left ht1

theorem chordFloor_right {x1 x2 t1 t2 : ℝ} (h12 : x1 < x2) (ht2 : 0 ≤ t2) :
    chordFloor x1 x2 t1 t2 x2 = t2 := by
  unfold chordFloor
  rw [div_mul_cancel₀ _ (sub_ne_zero.mpr h12.ne'), add_sub_cancel]
  exact max_eq_left ht2

/-- To the right of both anchors the curve `chordFloor` equals the larger of the chord-extension
bound and zero. -/
theorem chordFloor_attains_right {x1 x2 t1 t2 h : ℝ} (h12 : x1 < x2) (ht : t2 ≤ t1) :
    chordFloor x1 x2 t1 t2 h = max (t2 + min (t2 - t1) 0 * (h - x2) / (x2 - x1)) 0 := by
  unfold chordFloor
  have hd : 0 < x2 - x1 := sub_pos.mpr h12
  rw [min_eq_left (sub_nonpos.mpr ht)]
  have heq : t1 + (t2 - t1) / (x2 - x1) * (h - x1) = t2 + (t2 - t1) * (h - x2) / (x2 - x1) := by
    field_simp
    ring
  rw [heq]

end CreditCert
