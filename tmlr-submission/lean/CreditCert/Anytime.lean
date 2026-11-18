import CreditCert.Credit
import CreditCert.BernoulliKL

/-!
# The anytime guarantee, assembled from the tests the search runs

`anytime_trace` (in `Credit.lean`) assumes that every quoted rate has a true gain of at least minus the budget.
This file removes that assumption.

* The pilot tests of the certified rate search are stated as predicates on the confidence limits
  (`PilotTestM`, `PilotTestEta`, `PilotTestC`: the rules of Theorem "certified gain" for each shape class).
* Each test is shown to bound the true gain when the take-up curve is in the class and the limits are valid
  (`pilotTestM_sound`, `pilotTestEta_sound`, `pilotTestC_sound`).
* The guarantee is concluded from the adoption test and the pilot test alone, for each class
  (`anytime_monotone`, `anytime_slope`, `anytime_convex`).
* The last section composes this with the confidence event `confidence_event_kl`: with probability at least
  `1 - α`, every sequence of incumbents and quotes that passes the tests, with limits that contain the
  relative-entropy confidence sets, satisfies the guarantee, every change of incumbent strictly raises profit,
  and every rate excluded by the rejection test earns no more than the incumbent (`anytime_monotone_prob`,
  `anytime_slope_prob`, `anytime_convex_prob`).

Throughout, `S` is the admissible range on which the shape of the take-up curve is assumed, and `V ⊆ S` is the
set of rates at which confidence limits are available.
-/

namespace CreditCert

open MeasureTheory ProbabilityTheory Real Set
open scoped ENNReal

/-! ## The conclusion -/

/-- The conclusion of the anytime guarantee for incumbents `inc t` and quoted rates `q t`: the incumbent's profit
never falls; every quoted rate earns at least the share `1 - ρ` of the starting profit; and the profit of the
first `T` quoted rates is at least `T Φ(b₀)` minus `ℓbar` for each quote at a rate other than the incumbent. -/
def Guarantee (a : ℝ → ℝ) (ψ ρ ℓbar : ℝ) (inc q : ℕ → ℝ) : Prop :=
  (∀ t, Phi (fun _ => 0) a ψ (inc t) ≤ Phi (fun _ => 0) a ψ (inc (t + 1))) ∧
    (∀ t, (1 - ρ) * Phi (fun _ => 0) a ψ (inc 0) ≤ Phi (fun _ => 0) a ψ (q t)) ∧
    ∀ T : ℕ, (T : ℝ) * Phi (fun _ => 0) a ψ (inc 0)
        - ℓbar * (((Finset.range T).filter (fun t => q t ≠ inc t)).card : ℝ)
      ≤ ∑ t ∈ Finset.range T, Phi (fun _ => 0) a ψ (q t)

/-- The guarantee from the adoption test and a bound on the true gain of every quoted rate, with confidence
limits that are valid on the set `V` of rates used. -/
theorem anytime_of_safe {a : ℝ → ℝ} {V : Set ℝ} {ψ ρ ℓbar : ℝ} {inc q : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (hψ : ∀ t, ψ ≤ inc t) (hincV : ∀ t, inc t ∈ V)
    (hint : ∀ t, ∀ x ∈ V, L t x ≤ a x ∧ a x ≤ U t x)
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (hsafe : ∀ t, -(ρ * ((inc t - ψ) * L t (inc t))) ≤
      Phi (fun _ => 0) a ψ (q t) - Phi (fun _ => 0) a ψ (inc t))
    (hbar : ∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) (hℓ : 0 ≤ ℓbar) :
    Guarantee a ψ ρ ℓbar inc q := by
  have hstep : ∀ t, Phi (fun _ => 0) a ψ (inc t) ≤ Phi (fun _ => 0) a ψ (inc (t + 1)) := by
    intro t
    rcases hadopt t with h | h
    · rw [h]
    · have hpos : 0 < (fun _ : ℝ => (0 : ℝ)) (inc (t + 1)) + (inc (t + 1) - ψ) * L t (inc (t + 1))
          - (fun _ : ℝ => (0 : ℝ)) (inc t) - (inc t - ψ) * U t (inc t) := by
        simpa using h
      exact (adoption_sound (hψ (t + 1)) (hψ t) (hint t _ (hincV (t + 1))).1
        (hint t _ (hincV t)).2 hpos).le
  have htrial : ∀ t, (1 - ρ) * Phi (fun _ => 0) a ψ (inc t) ≤ Phi (fun _ => 0) a ψ (q t) := by
    intro t
    have h1 := hsafe t
    have h2 := budget_rel_le (a := a) (hψ t) hρ0 (hint t _ (hincV t)).1
    linarith
  unfold Guarantee
  refine ⟨hstep, quoted_ge_start_rel hρ1 hstep htrial, fun T => ?_⟩
  refine cumulative_profit_lower hℓ hstep (fun t => ?_) T
  have h1 := hsafe t
  have h2 := hbar t
  linarith

/-! ## Adoptions and rejections -/

/-- **Part (i).**  If the incumbent changes at quote `t`, the direct test passed, so profit strictly rises.  No
shape assumption. -/
theorem adoption_strict {a : ℝ → ℝ} {V : Set ℝ} {ψ : ℝ} {inc : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hψ : ∀ t, ψ ≤ inc t) (hincV : ∀ t, inc t ∈ V)
    (hint : ∀ t, ∀ x ∈ V, L t x ≤ a x ∧ a x ≤ U t x)
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (t : ℕ) (hne : inc (t + 1) ≠ inc t) :
    Phi (fun _ => 0) a ψ (inc t) < Phi (fun _ => 0) a ψ (inc (t + 1)) := by
  rcases hadopt t with h | h
  · exact absurd h hne
  · rw [Phi_zero, Phi_zero]
    have h1 : (inc (t + 1) - ψ) * L t (inc (t + 1)) ≤ (inc (t + 1) - ψ) * a (inc (t + 1)) :=
      mul_le_mul_of_nonneg_left (hint t _ (hincV (t + 1))).1 (sub_nonneg.mpr (hψ (t + 1)))
    have h2 : (inc t - ψ) * a (inc t) ≤ (inc t - ψ) * U t (inc t) :=
      mul_le_mul_of_nonneg_left (hint t _ (hincV t)).2 (sub_nonneg.mpr (hψ t))
    linarith

/-- **Part (ii).**  If the upper limit on the profit of `h` is below the lower limit on the profit of `b` (the
rejection test), then `h` earns no more than `b`.  No shape assumption. -/
theorem rejection_valid {a : ℝ → ℝ} {V : Set ℝ} {ψ b h : ℝ} {L U : ℝ → ℝ}
    (hint : ∀ x ∈ V, L x ≤ a x ∧ a x ≤ U x) (hb : b ∈ V) (hh : h ∈ V) (hψb : ψ ≤ b) (hψh : ψ ≤ h)
    (hrej : (h - ψ) * U h < (b - ψ) * L b) :
    Phi (fun _ => 0) a ψ h ≤ Phi (fun _ => 0) a ψ b := by
  rw [Phi_zero, Phi_zero]
  have h1 : (h - ψ) * a h ≤ (h - ψ) * U h := mul_le_mul_of_nonneg_left (hint h hh).2 (sub_nonneg.mpr hψh)
  have h2 : (b - ψ) * L b ≤ (b - ψ) * a b := mul_le_mul_of_nonneg_left (hint b hb).1 (sub_nonneg.mpr hψb)
  linarith

/-- Parts (i) and (ii) of the guarantee for incumbents `inc` and limits `L t`, `U t` at the rates in `V`: every
change of incumbent strictly raises profit, and every rate in `V` that the rejection test excludes earns no more
than the incumbent. -/
def TestsSound (a : ℝ → ℝ) (V : Set ℝ) (ψ : ℝ) (inc : ℕ → ℝ) (L U : ℕ → ℝ → ℝ) : Prop :=
  (∀ t, inc (t + 1) ≠ inc t → Phi (fun _ => 0) a ψ (inc t) < Phi (fun _ => 0) a ψ (inc (t + 1))) ∧
    ∀ t, ∀ h ∈ V, ψ ≤ h → (h - ψ) * U t h < (inc t - ψ) * L t (inc t) →
      Phi (fun _ => 0) a ψ h ≤ Phi (fun _ => 0) a ψ (inc t)

/-! ## The pilot tests and their soundness -/

/-- The envelope rule with profit `(s - ψ) a(s)`: a lower bound on take-up at `h` and an upper limit at `b`. -/
private theorem envelope_gain_zero {a : ℝ → ℝ} {ψ h b low Ub : ℝ} (hψ : ψ ≤ h) (hb : ψ ≤ b)
    (hlow : low ≤ a h) (hUb : a b ≤ Ub) :
    (h - ψ) * low - (b - ψ) * Ub ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  rw [Phi_zero, Phi_zero]
  have h1 : (h - ψ) * low ≤ (h - ψ) * a h := mul_le_mul_of_nonneg_left hlow (sub_nonneg.mpr hψ)
  have h2 : (b - ψ) * a b ≤ (b - ψ) * Ub := mul_le_mul_of_nonneg_left hUb (sub_nonneg.mpr hb)
  linarith

/-- **Pilot test, monotone class.**  Incumbent `b`, candidate `h`, budget `ℓ`, limits `L`, `U` at the rates in
`V`.  The candidate passes if it is the incumbent; or it is a cut whose worst-case loss `(b - h) U_b` is within
the budget (rule (b)); or the envelope rule (a) holds with the lower limit of a rate at or above `h`; or the
budget covers the whole profit bound of the incumbent (the envelope rule with the lower bound zero). -/
def PilotTestM (V : Set ℝ) (ψ ℓ b h : ℝ) (L U : ℝ → ℝ) : Prop :=
  h = b ∨ (h ≤ b ∧ (b - h) * U b ≤ ℓ) ∨
    (∃ x ∈ V, h ≤ x ∧ -ℓ ≤ (h - ψ) * L x - (b - ψ) * U b) ∨ (b - ψ) * U b ≤ ℓ

/-- A candidate that passes the monotone test loses at most the budget, for every nonincreasing, nonnegative
take-up curve whose values lie inside the limits. -/
theorem pilotTestM_sound {a : ℝ → ℝ} {S V : Set ℝ} {ψ ℓ b h : ℝ} {L U : ℝ → ℝ}
    (hanti : AntitoneOn a S) (hnn : ∀ x ∈ S, 0 ≤ a x) (hVS : V ⊆ S)
    (hint : ∀ x ∈ V, L x ≤ a x ∧ a x ≤ U x) (hb : b ∈ V) (hh : h ∈ S) (hψh : ψ ≤ h) (hψb : ψ ≤ b)
    (hℓ : 0 ≤ ℓ) (htest : PilotTestM V ψ ℓ b h L U) :
    -ℓ ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  unfold PilotTestM at htest
  rcases htest with heq | ⟨hhb, hcut⟩ | ⟨x, hx, hhx, henv⟩ | hzero
  · rw [heq, sub_self]
    linarith
  · have h0 := rate_cut_loss (a := a) hψh hhb (hanti hh (hVS hb) hhb) (hint b hb).2
    linarith
  · have hlow : L x ≤ a h := (hint x hx).1.trans (hanti hh (hVS hx) hhx)
    have h0 := envelope_gain_zero hψh hψb hlow (hint b hb).2
    linarith
  · have h0 := envelope_gain_zero hψh hψb (hnn h hh) (hint b hb).2
    linarith

/-- **Pilot test, slope-bound class.**  A candidate passes if it passes the monotone test; or it is an increase
that passes the slope rule (c); or the envelope rule (a) holds with the lower limit of a rate at or below `h`,
reduced by `η` per unit of distance. -/
def PilotTestEta (V : Set ℝ) (ψ ℓ η b h : ℝ) (L U : ℝ → ℝ) : Prop :=
  PilotTestM V ψ ℓ b h L U ∨ (b ≤ h ∧ -ℓ ≤ (h - b) * L b - η * (h - b) * (h - ψ)) ∨
    ∃ x ∈ V, x ≤ h ∧ -ℓ ≤ (h - ψ) * (L x - η * (h - x)) - (b - ψ) * U b

/-- A candidate that passes the slope-bound test loses at most the budget, for every nonincreasing, nonnegative
take-up curve that falls by at most `η` per unit of rate and whose values lie inside the limits. -/
theorem pilotTestEta_sound {a : ℝ → ℝ} {S V : Set ℝ} {ψ ℓ η b h : ℝ} {L U : ℝ → ℝ}
    (hanti : AntitoneOn a S) (hnn : ∀ x ∈ S, 0 ≤ a x)
    (hslope : ∀ x ∈ S, ∀ y ∈ S, x ≤ y → a x - η * (y - x) ≤ a y) (hVS : V ⊆ S)
    (hint : ∀ x ∈ V, L x ≤ a x ∧ a x ≤ U x) (hb : b ∈ V) (hh : h ∈ S) (hψh : ψ ≤ h) (hψb : ψ ≤ b)
    (hℓ : 0 ≤ ℓ) (htest : PilotTestEta V ψ ℓ η b h L U) :
    -ℓ ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  unfold PilotTestEta at htest
  rcases htest with hM | ⟨hbh, hc⟩ | ⟨x, hx, hxh, henv⟩
  · exact pilotTestM_sound hanti hnn hVS hint hb hh hψh hψb hℓ hM
  · have h0 := increase_with_slope_bound_lower (a := a) hψh hbh (hslope b (hVS hb) h hh hbh) (hint b hb).1
    linarith
  · have hlow : L x - η * (h - x) ≤ a h := slope_lower (hslope x (hVS hx) h hh hxh) (hint x hx).1
    have h0 := envelope_gain_zero hψh hψb hlow (hint b hb).2
    linarith

/-- **Pilot test, convex class.**  A candidate passes if it passes the monotone test; or the envelope rule (a)
holds with the chord through two rates, extended to the left or to the right of them and bounded with the
limits; or one of the joint rules (d) holds with a second rate on the other side of the incumbent. -/
def PilotTestC (V : Set ℝ) (ψ ℓ b h : ℝ) (L U : ℝ → ℝ) : Prop :=
  PilotTestM V ψ ℓ b h L U ∨
    (∃ x ∈ V, ∃ y ∈ V, h ≤ x ∧ x < y ∧
      -ℓ ≤ (h - ψ) * (L x + max (L x - U y) 0 * (x - h) / (y - x)) - (b - ψ) * U b) ∨
    (∃ x ∈ V, ∃ y ∈ V, x < y ∧ y ≤ h ∧
      -ℓ ≤ (h - ψ) * (L y + min (L y - U x) 0 * (h - y) / (y - x)) - (b - ψ) * U b) ∨
    (∃ y ∈ V, h ≤ b ∧ b < y ∧
      -ℓ ≤ min (((h - ψ) * (y - h) / (y - b) - (b - ψ)) * L b)
            (((h - ψ) * (y - h) / (y - b) - (b - ψ)) * U b)
          + -((h - ψ) * (b - h) / (y - b)) * U y) ∨
    (∃ y ∈ V, y < b ∧ b ≤ h ∧
      -ℓ ≤ min (((h - ψ) * (h - y) / (b - y) - (b - ψ)) * L b)
            (((h - ψ) * (h - y) / (b - y) - (b - ψ)) * U b)
          + -((h - ψ) * (h - b) / (b - y)) * U y)

/-- A candidate that passes the convex test loses at most the budget, for every nonincreasing, nonnegative,
convex take-up curve whose values lie inside the limits. -/
theorem pilotTestC_sound {a : ℝ → ℝ} {S V : Set ℝ} {ψ ℓ b h : ℝ} {L U : ℝ → ℝ}
    (hconv : ConvexOn ℝ S a) (hanti : AntitoneOn a S) (hnn : ∀ x ∈ S, 0 ≤ a x) (hVS : V ⊆ S)
    (hint : ∀ x ∈ V, L x ≤ a x ∧ a x ≤ U x) (hb : b ∈ V) (hh : h ∈ S) (hψh : ψ ≤ h) (hψb : ψ ≤ b)
    (hℓ : 0 ≤ ℓ) (htest : PilotTestC V ψ ℓ b h L U) :
    -ℓ ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b := by
  unfold PilotTestC at htest
  rcases htest with hM | ⟨x, hx, y, hy, hhx, hxy, henv⟩ | ⟨x, hx, y, hy, hxy, hyh, henv⟩ |
    ⟨y, hy, hhb, hby, hj⟩ | ⟨y, hy, hyb, hbh, hj⟩
  · exact pilotTestM_sound hanti hnn hVS hint hb hh hψh hψb hℓ hM
  · have hlow := chord_ext_left_interval hconv hanti hh (hVS hx) (hVS hy) hhx hxy (hint x hx).1
      (hint y hy).2
    have h0 := envelope_gain_zero hψh hψb hlow (hint b hb).2
    linarith
  · have hlow := chord_ext_right_interval hconv (hVS hx) hh hxy hyh (hint x hx).2 (hint y hy).1
    have h0 := envelope_gain_zero hψh hψb hlow (hint b hb).2
    linarith
  · have h0 := joint_left_gain (K := fun _ => (0 : ℝ)) hconv hh (hVS hy) hψh hhb hby (hint b hb).1
      (hint b hb).2 (hint y hy).2
    simp only [sub_self, zero_add] at h0
    linarith
  · have h0 := joint_right_gain (K := fun _ => (0 : ℝ)) hconv (hVS hy) hh hψh hyb hbh (hint b hb).1
      (hint b hb).2 (hint y hy).2
    simp only [sub_self, zero_add] at h0
    linarith

/-! ## The guarantee from the two tests, for each class -/

/-- **Anytime guarantee, monotone class.**  If the take-up curve is nonincreasing and nonnegative on the
admissible range, all limits contain the true take-up, the incumbent changes only when the direct test passes,
and every quoted rate passes the monotone pilot test with the budget `ρ (b - ψ) L_b`, then the guarantee
holds. -/
theorem anytime_monotone {a : ℝ → ℝ} {S V : Set ℝ} {ψ ρ ℓbar : ℝ} {inc q : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hanti : AntitoneOn a S) (hnn : ∀ x ∈ S, 0 ≤ a x) (hVS : V ⊆ S)
    (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (hψ : ∀ t, ψ ≤ inc t) (hincV : ∀ t, inc t ∈ V)
    (hψq : ∀ t, ψ ≤ q t) (hqS : ∀ t, q t ∈ S)
    (hint : ∀ t, ∀ x ∈ V, L t x ≤ a x ∧ a x ≤ U t x) (hL0 : ∀ t, 0 ≤ L t (inc t))
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (hpilot : ∀ t, PilotTestM V ψ (ρ * ((inc t - ψ) * L t (inc t))) (inc t) (q t) (L t) (U t))
    (hbar : ∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) (hℓ : 0 ≤ ℓbar) :
    Guarantee a ψ ρ ℓbar inc q :=
  anytime_of_safe hρ0 hρ1 hψ hincV hint hadopt
    (fun t => pilotTestM_sound hanti hnn hVS (hint t) (hincV t) (hqS t) (hψq t) (hψ t)
      (mul_nonneg hρ0 (mul_nonneg (sub_nonneg.mpr (hψ t)) (hL0 t))) (hpilot t))
    hbar hℓ

/-- **Anytime guarantee, slope-bound class.** -/
theorem anytime_slope {a : ℝ → ℝ} {S V : Set ℝ} {ψ ρ η ℓbar : ℝ} {inc q : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hanti : AntitoneOn a S) (hnn : ∀ x ∈ S, 0 ≤ a x)
    (hslope : ∀ x ∈ S, ∀ y ∈ S, x ≤ y → a x - η * (y - x) ≤ a y) (hVS : V ⊆ S)
    (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (hψ : ∀ t, ψ ≤ inc t) (hincV : ∀ t, inc t ∈ V)
    (hψq : ∀ t, ψ ≤ q t) (hqS : ∀ t, q t ∈ S)
    (hint : ∀ t, ∀ x ∈ V, L t x ≤ a x ∧ a x ≤ U t x) (hL0 : ∀ t, 0 ≤ L t (inc t))
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (hpilot : ∀ t, PilotTestEta V ψ (ρ * ((inc t - ψ) * L t (inc t))) η (inc t) (q t) (L t) (U t))
    (hbar : ∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) (hℓ : 0 ≤ ℓbar) :
    Guarantee a ψ ρ ℓbar inc q :=
  anytime_of_safe hρ0 hρ1 hψ hincV hint hadopt
    (fun t => pilotTestEta_sound hanti hnn hslope hVS (hint t) (hincV t) (hqS t) (hψq t) (hψ t)
      (mul_nonneg hρ0 (mul_nonneg (sub_nonneg.mpr (hψ t)) (hL0 t))) (hpilot t))
    hbar hℓ

/-- **Anytime guarantee, convex class.** -/
theorem anytime_convex {a : ℝ → ℝ} {S V : Set ℝ} {ψ ρ ℓbar : ℝ} {inc q : ℕ → ℝ} {L U : ℕ → ℝ → ℝ}
    (hconv : ConvexOn ℝ S a) (hanti : AntitoneOn a S) (hnn : ∀ x ∈ S, 0 ≤ a x) (hVS : V ⊆ S)
    (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) (hψ : ∀ t, ψ ≤ inc t) (hincV : ∀ t, inc t ∈ V)
    (hψq : ∀ t, ψ ≤ q t) (hqS : ∀ t, q t ∈ S)
    (hint : ∀ t, ∀ x ∈ V, L t x ≤ a x ∧ a x ≤ U t x) (hL0 : ∀ t, 0 ≤ L t (inc t))
    (hadopt : ∀ t, inc (t + 1) = inc t ∨
      0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t))
    (hpilot : ∀ t, PilotTestC V ψ (ρ * ((inc t - ψ) * L t (inc t))) (inc t) (q t) (L t) (U t))
    (hbar : ∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) (hℓ : 0 ≤ ℓbar) :
    Guarantee a ψ ρ ℓbar inc q :=
  anytime_of_safe hρ0 hρ1 hψ hincV hint hadopt
    (fun t => pilotTestC_sound hconv hanti hnn hVS (hint t) (hincV t) (hqS t) (hψq t) (hψ t)
      (mul_nonneg hρ0 (mul_nonneg (sub_nonneg.mpr (hψ t)) (hL0 t))) (hpilot t))
    hbar hℓ

/-! ## Composition with the confidence event -/

/-- In a probability space, the complement of a set of measure at most `c` has measure at least `1 - c`.
No measurability is needed. -/
private theorem one_sub_le_measure_compl {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
    [IsProbabilityMeasure μ] {s : Set Ω} {c : ℝ≥0∞} (hs : μ s ≤ c) : 1 - c ≤ μ sᶜ := by
  have h1 : (1 : ℝ≥0∞) ≤ μ s + μ sᶜ := by
    have h := measure_union_le (μ := μ) s sᶜ
    rwa [Set.union_compl_self, measure_univ] at h
  calc 1 - c ≤ 1 - μ s := tsub_le_tsub_left hs 1
    _ ≤ μ sᶜ := tsub_le_iff_left.mpr h1

/-- **Valid limits with high probability.**  Rate `j` has independent acceptance indicators `X j k` with mean
`p j`.  With probability at least `1 - α`, simultaneously for every rate `j`: any pair of limits `(l, u)` that
brackets every value in `[0, 1]` consistent with the relative-entropy constraints of all checkpoints of rate `j`
also brackets the true take-up `p j`.  Limits computed from the checkpoints reached so far have this property,
because they bracket a larger set. -/
theorem confidence_limits_valid {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, Measurable (X j k)) (h01 : ∀ j k ω, X j k ω = 0 ∨ X j k ω = 1)
    (hind : ∀ j, iIndepFun (X j) μ) {p : ℕ → ℝ} (hp : ∀ j k, μ[X j k] = p j)
    (hp0 : ∀ j, 0 < p j) (hp1 : ∀ j, p j < 1) {α : ℝ} (hα : 0 < α) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i) :
    1 - ENNReal.ofReal α ≤ μ {ω | ∀ (j : ℕ) (l u : ℝ),
      (∀ p' : ℝ, 0 ≤ p' → p' ≤ 1 →
        (∀ i, (N i : ℝ) * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) p' ≤ log (2 / budget α j i)) →
        l ≤ p' ∧ p' ≤ u) →
      l ≤ p j ∧ p j ≤ u} := by
  refine (one_sub_le_measure_compl (confidence_event_kl hm h01 hind hp hp0 hp1 hα N hN)).trans
    (measure_mono ?_)
  intro ω hω
  have hgood : ∀ j i, (N i : ℝ) * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) (p j)
      ≤ log (2 / budget α j i) := by
    simpa only [Set.mem_compl_iff, Set.mem_ofPred_eq, not_exists, not_lt] using hω
  intro j l u hlu
  exact hlu (p j) (hp0 j).le (hp1 j).le (hgood j)

/-- **Anytime guarantee with probability `1 - α`, for any sound pilot test.**  The lattice rate `x j` has take-up
`a (x j) = p j` and acceptance indicators `X j k`.  `Test ℓ b h L U` is any pilot test that bounds the true loss
by the budget whenever the limits are valid at the lattice rates.  Then, with probability at least `1 - α`, the
guarantee holds for every sequence of incumbents `inc` (lattice rates at or above `ψ`) and quoted rates `q`, and
every family of limits `L t`, `U t` that bracket the relative-entropy confidence sets, such that the incumbent
changes only when the direct test passes and every quoted rate passes the pilot test; in addition every change
of incumbent strictly raises profit and every rejection is valid (`TestsSound`). -/
theorem anytime_prob_of_sound {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, Measurable (X j k)) (h01 : ∀ j k ω, X j k ω = 0 ∨ X j k ω = 1)
    (hind : ∀ j, iIndepFun (X j) μ) {p : ℕ → ℝ} (hp : ∀ j k, μ[X j k] = p j)
    (hp0 : ∀ j, 0 < p j) (hp1 : ∀ j, p j < 1) {α : ℝ} (hα : 0 < α) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i)
    {a : ℝ → ℝ} {x : ℕ → ℝ} (hax : ∀ j, a (x j) = p j) {ψ ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1)
    (Test : ℝ → ℝ → ℝ → (ℝ → ℝ) → (ℝ → ℝ) → Prop)
    (hsound : ∀ (ℓ b h : ℝ) (L U : ℝ → ℝ), (∀ s ∈ Set.range x, L s ≤ a s ∧ a s ≤ U s) →
      b ∈ Set.range x → ψ ≤ b → 0 ≤ ℓ → Test ℓ b h L U →
      -ℓ ≤ Phi (fun _ => 0) a ψ h - Phi (fun _ => 0) a ψ b) :
    1 - ENNReal.ofReal α ≤ μ {ω | ∀ (inc q : ℕ → ℝ) (L U : ℕ → ℝ → ℝ) (ℓbar : ℝ),
      (∀ (t j : ℕ) (p' : ℝ), 0 ≤ p' → p' ≤ 1 →
        (∀ i, (N i : ℝ) * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) p' ≤ log (2 / budget α j i)) →
        L t (x j) ≤ p' ∧ p' ≤ U t (x j)) →
      (∀ t, ψ ≤ inc t) → (∀ t, inc t ∈ Set.range x) → (∀ t, 0 ≤ L t (inc t)) →
      (∀ t, inc (t + 1) = inc t ∨
        0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t)) →
      (∀ t, Test (ρ * ((inc t - ψ) * L t (inc t))) (inc t) (q t) (L t) (U t)) →
      (∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) → 0 ≤ ℓbar →
      Guarantee a ψ ρ ℓbar inc q ∧ TestsSound a (Set.range x) ψ inc L U} := by
  refine (confidence_limits_valid hm h01 hind hp hp0 hp1 hα N hN).trans (measure_mono ?_)
  intro ω hω inc q L U ℓbar hLU hψ hinc hL0 hadopt hpilot hbar hℓ
  have hint : ∀ t, ∀ s ∈ Set.range x, L t s ≤ a s ∧ a s ≤ U t s := by
    rintro t _ ⟨j, rfl⟩
    rw [hax j]
    exact hω j (L t (x j)) (U t (x j)) (hLU t j)
  refine ⟨anytime_of_safe hρ0 hρ1 hψ hinc hint hadopt
    (fun t => hsound _ _ _ _ _ (hint t) (hinc t) (hψ t)
      (mul_nonneg hρ0 (mul_nonneg (sub_nonneg.mpr (hψ t)) (hL0 t))) (hpilot t))
    hbar hℓ, ?_⟩
  unfold TestsSound
  exact ⟨fun t hne => adoption_strict hψ hinc hint hadopt t hne,
    fun t h hh hψh hrej => rejection_valid (hint t) (hinc t) hh (hψ t) hψh hrej⟩

/-- **Theorem "anytime guarantee", monotone class, with probability `1 - α`.**  The pilot test is the monotone
test at an admissible candidate (`ψ ≤ h`, `h ∈ S`). -/
theorem anytime_monotone_prob {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, Measurable (X j k)) (h01 : ∀ j k ω, X j k ω = 0 ∨ X j k ω = 1)
    (hind : ∀ j, iIndepFun (X j) μ) {p : ℕ → ℝ} (hp : ∀ j k, μ[X j k] = p j)
    (hp0 : ∀ j, 0 < p j) (hp1 : ∀ j, p j < 1) {α : ℝ} (hα : 0 < α) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i)
    {a : ℝ → ℝ} {x : ℕ → ℝ} (hax : ∀ j, a (x j) = p j) {S : Set ℝ} (hxS : ∀ j, x j ∈ S)
    (hanti : AntitoneOn a S) (hnn : ∀ s ∈ S, 0 ≤ a s) {ψ ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) :
    1 - ENNReal.ofReal α ≤ μ {ω | ∀ (inc q : ℕ → ℝ) (L U : ℕ → ℝ → ℝ) (ℓbar : ℝ),
      (∀ (t j : ℕ) (p' : ℝ), 0 ≤ p' → p' ≤ 1 →
        (∀ i, (N i : ℝ) * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) p' ≤ log (2 / budget α j i)) →
        L t (x j) ≤ p' ∧ p' ≤ U t (x j)) →
      (∀ t, ψ ≤ inc t) → (∀ t, inc t ∈ Set.range x) → (∀ t, 0 ≤ L t (inc t)) →
      (∀ t, inc (t + 1) = inc t ∨
        0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t)) →
      (∀ t, ψ ≤ q t ∧ q t ∈ S ∧
        PilotTestM (Set.range x) ψ (ρ * ((inc t - ψ) * L t (inc t))) (inc t) (q t) (L t) (U t)) →
      (∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) → 0 ≤ ℓbar →
      Guarantee a ψ ρ ℓbar inc q ∧ TestsSound a (Set.range x) ψ inc L U} :=
  anytime_prob_of_sound hm h01 hind hp hp0 hp1 hα N hN hax hρ0 hρ1
    (fun ℓ b h L U => ψ ≤ h ∧ h ∈ S ∧ PilotTestM (Set.range x) ψ ℓ b h L U)
    (fun _ _ _ _ _ hint hb hψb hℓ htest =>
      pilotTestM_sound hanti hnn (Set.range_subset_iff.mpr hxS) hint hb htest.2.1 htest.1 hψb hℓ
        htest.2.2)

/-- **Theorem "anytime guarantee", slope-bound class, with probability `1 - α`.** -/
theorem anytime_slope_prob {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, Measurable (X j k)) (h01 : ∀ j k ω, X j k ω = 0 ∨ X j k ω = 1)
    (hind : ∀ j, iIndepFun (X j) μ) {p : ℕ → ℝ} (hp : ∀ j k, μ[X j k] = p j)
    (hp0 : ∀ j, 0 < p j) (hp1 : ∀ j, p j < 1) {α : ℝ} (hα : 0 < α) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i)
    {a : ℝ → ℝ} {x : ℕ → ℝ} (hax : ∀ j, a (x j) = p j) {S : Set ℝ} (hxS : ∀ j, x j ∈ S)
    (hanti : AntitoneOn a S) (hnn : ∀ s ∈ S, 0 ≤ a s) {η : ℝ}
    (hslope : ∀ s ∈ S, ∀ y ∈ S, s ≤ y → a s - η * (y - s) ≤ a y)
    {ψ ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) :
    1 - ENNReal.ofReal α ≤ μ {ω | ∀ (inc q : ℕ → ℝ) (L U : ℕ → ℝ → ℝ) (ℓbar : ℝ),
      (∀ (t j : ℕ) (p' : ℝ), 0 ≤ p' → p' ≤ 1 →
        (∀ i, (N i : ℝ) * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) p' ≤ log (2 / budget α j i)) →
        L t (x j) ≤ p' ∧ p' ≤ U t (x j)) →
      (∀ t, ψ ≤ inc t) → (∀ t, inc t ∈ Set.range x) → (∀ t, 0 ≤ L t (inc t)) →
      (∀ t, inc (t + 1) = inc t ∨
        0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t)) →
      (∀ t, ψ ≤ q t ∧ q t ∈ S ∧
        PilotTestEta (Set.range x) ψ (ρ * ((inc t - ψ) * L t (inc t))) η (inc t) (q t) (L t) (U t)) →
      (∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) → 0 ≤ ℓbar →
      Guarantee a ψ ρ ℓbar inc q ∧ TestsSound a (Set.range x) ψ inc L U} :=
  anytime_prob_of_sound hm h01 hind hp hp0 hp1 hα N hN hax hρ0 hρ1
    (fun ℓ b h L U => ψ ≤ h ∧ h ∈ S ∧ PilotTestEta (Set.range x) ψ ℓ η b h L U)
    (fun _ _ _ _ _ hint hb hψb hℓ htest =>
      pilotTestEta_sound hanti hnn hslope (Set.range_subset_iff.mpr hxS) hint hb htest.2.1 htest.1 hψb hℓ
        htest.2.2)

/-- **Theorem "anytime guarantee", convex class, with probability `1 - α`.** -/
theorem anytime_convex_prob {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {X : ℕ → ℕ → Ω → ℝ} (hm : ∀ j k, Measurable (X j k)) (h01 : ∀ j k ω, X j k ω = 0 ∨ X j k ω = 1)
    (hind : ∀ j, iIndepFun (X j) μ) {p : ℕ → ℝ} (hp : ∀ j k, μ[X j k] = p j)
    (hp0 : ∀ j, 0 < p j) (hp1 : ∀ j, p j < 1) {α : ℝ} (hα : 0 < α) (N : ℕ → ℕ) (hN : ∀ i, 0 < N i)
    {a : ℝ → ℝ} {x : ℕ → ℝ} (hax : ∀ j, a (x j) = p j) {S : Set ℝ} (hxS : ∀ j, x j ∈ S)
    (hconv : ConvexOn ℝ S a) (hanti : AntitoneOn a S) (hnn : ∀ s ∈ S, 0 ≤ a s)
    {ψ ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ ≤ 1) :
    1 - ENNReal.ofReal α ≤ μ {ω | ∀ (inc q : ℕ → ℝ) (L U : ℕ → ℝ → ℝ) (ℓbar : ℝ),
      (∀ (t j : ℕ) (p' : ℝ), 0 ≤ p' → p' ≤ 1 →
        (∀ i, (N i : ℝ) * klb ((∑ k ∈ Finset.range (N i), X j k ω) / N i) p' ≤ log (2 / budget α j i)) →
        L t (x j) ≤ p' ∧ p' ≤ U t (x j)) →
      (∀ t, ψ ≤ inc t) → (∀ t, inc t ∈ Set.range x) → (∀ t, 0 ≤ L t (inc t)) →
      (∀ t, inc (t + 1) = inc t ∨
        0 < (inc (t + 1) - ψ) * L t (inc (t + 1)) - (inc t - ψ) * U t (inc t)) →
      (∀ t, ψ ≤ q t ∧ q t ∈ S ∧
        PilotTestC (Set.range x) ψ (ρ * ((inc t - ψ) * L t (inc t))) (inc t) (q t) (L t) (U t)) →
      (∀ t, ρ * ((inc t - ψ) * L t (inc t)) ≤ ℓbar) → 0 ≤ ℓbar →
      Guarantee a ψ ρ ℓbar inc q ∧ TestsSound a (Set.range x) ψ inc L U} :=
  anytime_prob_of_sound hm h01 hind hp hp0 hp1 hα N hN hax hρ0 hρ1
    (fun ℓ b h L U => ψ ≤ h ∧ h ∈ S ∧ PilotTestC (Set.range x) ψ ℓ b h L U)
    (fun _ _ _ _ _ hint hb hψb hℓ htest =>
      pilotTestC_sound hconv hanti hnn (Set.range_subset_iff.mpr hxS) hint hb htest.2.1 htest.1 hψb hℓ
        htest.2.2)

end CreditCert
