# D8/D9 - The ROI of Self-Knowledge, the Consistency Lemmas, and the REFLEX Instantiation

**Status: ROI closed forms derived and verified (V8); both consistency
lemmas proved (one-liners, verified); the multi-bond `Gamma_PO` derived
exactly in the separable case with the coupled extension stated.**

## 1. D8 - The ROI of self-knowledge

**Ingredients** (all from earlier derivations / REFLEX 1.2):

```
   A  =  (1/2) gamma_PO (h_SP - h_PO)^2          (echo-chamber value gap per step, 1.2 (6b))
   b  =  (1/2) gamma_PO sigma^2                   (the exchange rate, D2: cost of accuracy v is b/v)
   a  =  (1/2) gamma_PO kappa^2                   (residual gap per unit estimator variance:
                                                   an eps-error of variance v displaces the
                                                   corrected deployment by kappa^2 v in squared
                                                   spread units, kappa = |d h_PO / d eps| from the
                                                   1.2 fixed-point sensitivity - closed form)
```

**The decision problem.** Explore once to accuracy `v`, then run corrected
forever, discounting at rate `rho_disc`:

```
   NPV(v)  =  ( A - a v ) / rho_disc  -  b / v .
```

**Theorem (optimal accuracy and break-even patience).**

```
   v*        =  sqrt( b rho_disc / a )  =  ( sigma / kappa ) sqrt( rho_disc )     [note gamma_PO cancels]
   NPV(v*)   =  A / rho_disc  -  2 sqrt( a b / rho_disc )
   explore   iff  A > 2 sqrt( a b rho_disc )
             iff  rho_disc  <  rho*  :=  A^2 / (4 a b)  =  (h_SP - h_PO)^4 / ( 4 kappa^2 sigma^2 ) .
```

**Derivation.** `NPV'(v) = -a/rho + b/v^2 = 0` gives `v*`; concavity in `v`
on `(0, inf)` certifies the max; `NPV(v*) > 0` rearranges to the threshold;
substitute `A, a, b` and watch `gamma_PO` cancel completely. []

**Readings.** (i) The break-even patience `rho* = (h_SP-h_PO)^4 /
(4 kappa^2 sigma^2)` involves only the gap, the correction's sensitivity,
and the response noise - the curvature drops out, a genuinely clean and
slightly surprising closed form (it cancels between the gap's value and the
exploration price). (ii) Everything on the right is computable from REFLEX
primitives before exploring - the point of the corollary. (iii) `v*` is the
*right amount* of self-knowledge: more accuracy than `v*` is vanity, less is
blindness.

## 2. Consistency lemmas (the two lit-review checks, now formal)

**Lemma (Lai-Robbins schemes sit on the frontier).** Any deterministic
design `d_t` has pathwise product
`(sigma^2/S_T) * (1/2) gamma_PO S_T = (1/2) gamma_PO sigma^2` - in
particular the `d_t ~ c/sqrt(t)` schedules with `S_T = c^2 log T` (the
Lai-Robbins cost-`O(log T)` regime) satisfy the exchange rate exactly:
their celebrated cheapness buys proportionally little information, precisely
on the frontier. *Proof: the product's `S_T` cancels; nothing about the
schedule matters.* []

**Lemma (the isotropy contrast).** In the `d`-dimensional problem the
isotropic-vs-optimal risk ratio is the curvature dispersion
`F = d tr(Gamma_PO) / (tr Gamma_PO^{1/2})^2` (D4). `F = 1` iff `Gamma_PO`
is a multiple of `I` - the LQR-like isotropic case where naive exploration
is optimal (Simchowitz-Foster 2020); generically `F > 1` and grows with
curvature spread. *The performative setting is generically anisotropic
(bond-level `gamma_a` spans decades across the calibrated universe), so
naive exploration is generically suboptimal - the clean contrast sentence
for the paper.* []

## 3. D9 - The multi-bond `Gamma_PO` (instantiation)

**Separable case (exact).** With per-bond decisions `h_a` and separable
flows (diagonal response `E = diag(eps_a)`), the performative objective
separates, and by 1.2 section 4.1 applied per bond:

```
   ( Gamma_PO )_aa  =  gamma_a  +  beta eps_a ( 2 + c_t psi_a - c_t h_a ) ,     off-diagonal 0 .
```

All quantities are the calibrated per-bond constants of theory 1.5
(`per_bond_constants`); the curvature-dispersion factor `F` of section 2 is
then directly computable on the 128-bond calibrated universe - the number
quoted in the paper's experiments.

**Coupled case (construction, first order).** With factor-coupled responses
(`E` diagonal-plus-low-rank as in 1.5), the same differentiation gives

```
   Gamma_PO  =  Gamma  +  beta [ 2 E_sym + c_t ( diag(psi) E_sym - H E_sym ) ]  + O(||E_offdiag||^2),
   E_sym = (E + E')/2 ,   H = diag(h_a) ,
```

exact when `E` is symmetric and evaluated at the operating point; the
low-rank structure of `E` is inherited, so `Gamma_PO^{-1/2}` and
`tr Gamma_PO^{1/2}` remain `O(d k^2)` via the same Woodbury/eigen-split
machinery as 1.5 (no new computational burden). The paper states the
separable case as a theorem and the coupled case as a first-order
construction with its error term - matching the honesty conventions of the
REFLEX experiments (arXiv:2608.16155).

## 4. Verified numerically (V8)

1. `v* = sqrt(b rho/a)` and the `NPV(v*)` formula against a numerical scan
   over `v` (three parameter sets).
2. The break-even: root-finding `NPV(v*)(rho) = 0` in `rho` recovers
   `rho* = Delta_h^4/(4 kappa^2 sigma^2)` to 1e-10, confirming the
   `gamma_PO` cancellation.
3. The frontier lemma: `c/sqrt(t)` schedules measured on-frontier exactly.
4. The dispersion factor on a synthetic curvature spectrum spanning two
   decades: `F` matches the measured isotropic/optimal risk ratio (V4
   cross-check).
5. Separable `Gamma_PO`: finite-difference Hessian of the separable
   objective matches the per-bond formula entrywise.
