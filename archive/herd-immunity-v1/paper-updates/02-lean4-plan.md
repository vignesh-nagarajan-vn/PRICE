# Lean 4 formalization plan

## 1. Why this is the right frontier move, and its honest limits

No paper in this niche (multiplayer performative prediction, algorithmic
monoculture, systemic risk of learning agents) ships machine-checked
proofs; formalized economics exists (auction/game formalizations) but not
a formalized stability theory of interacting learners, to the extent
searched (log entry V9). The paper's mathematics is unusually well suited:
finite-dimensional, real-symmetric, explicit. The limit is Mathlib's
actual contents, verified this session:

- **Available** (verified): the spectral theorem for Hermitian matrices
  and eigenvalue machinery (`Mathlib.Analysis.Matrix.Spectrum`,
  descended from mathlib3 `linear_algebra.matrix.spectrum`); Rayleigh
  quotient theory (`Mathlib.Analysis.InnerProductSpace.Rayleigh`);
  positive-semidefinite matrices, Gram matrices, congruence machinery.
- **Absent** (verified): Perron-Frobenius for nonnegative matrices (it
  is an open target on the Lean formalization leaderboard); Bernstein /
  sub-exponential concentration at the strength Appendix C needs.
- **Uncertain, verify locally before relying on it** (log entries
  V10-V11): the exact current lemma names above; Loewner-order lemmas
  strong enough for the congruence step of the heterogeneous-moduli
  bound; matrix polynomial/charpoly tooling convenient enough for the
  secular quadratic. First action of the workstream is a half-day
  `exact?`/Loogle audit against a pinned Mathlib.

Design rule that follows: **formalize nothing that needs
Perron-Frobenius or concentration; restructure two proofs to elementary
arguments that Mathlib can carry** (T7, T8 below).

## 2. Repository and infrastructure (outline)

- `formal/` Lake project; Mathlib pinned by commit; one module per paper
  result, names mirroring the paper (`Reduction.lean`, `Alignment.lean`,
  `Cadence.lean`, `MixedMarket.lean`, `Wedge.lean`, `Anchors.lean`).
- CI: GitHub Action running `lake build` plus a script that greps
  `#print axioms` output for each exported theorem and fails on anything
  beyond the standard three (propext, Classical.choice, Quot.sound);
  no `sorry` reaches main.
- A generated `MANIFEST.md`: paper label -> Lean name -> file -> axioms.
  This file is the source for Appendix K's table; it is generated, so
  the paper cannot drift from the code.
- Blind note: the formal repo is part of the artifact; before
  de-anonymization it ships in the anonymized supplementary zip like the
  certificates.

## 3. Target-by-target roadmap

Ordered by (value x tractability). Each entry: the statement to
formalize (paper label), the route, the Mathlib load-bearing pieces, and
the difficulty (S/M/L in experienced-formalizer days; multiply by ~3
without Lean experience).

| # | Target (paper label) | Route | Difficulty |
|---|---|---|---|
| T1 | Lemma 1 (reduction): the felt-distortion computation yields J = -m1[(1-k)I + kR] | Direct finite computation over `Fin N`; inner products of vec'd matrices as `Matrix.trace (Aᵀ*B)` or plain `EuclideanSpace` vectors (model E_i abstractly as unit vectors in R^D from the start; nothing downstream needs matrix structure) | S |
| T2 | Lemma A.1 (R = VVᵀ properties: PSD, unit diagonal, |r_ij| <= 1, 1 <= lmax <= N, both attainment ends) | Gram-matrix PSD is stock; trace = N; eigenvalue bounds from trace + nonnegativity via `IsHermitian.eigenvalues`; attainment by the explicit R = I and R = 11ᵀ instances | S-M |
| T3 | Theorem 2 core: rho(J) = m1 * (1 + k(lmax(R) - 1)) for k in [0,1], R PSD unit-diagonal | J = -m1 B, B symmetric; eigenvalues of B are affine in eigenvalues of R (B = (1-k)I + kR shares eigenvectors: spectral theorem); nonnegativity of nu_i kills the absolute value (the Gram step); max via Rayleigh sup characterization | M |
| T4 | Anchors: monoculture (lmax = N), orthogonal (lmax = 1), simplex (spectrum {0, N/(N-1)}) | Explicit eigenvector verification (Av = lam*v is `decide`-adjacent computation); no spectral abstraction needed | S |
| T5 | Prop 3 (containment witness) | Pure arithmetic on T3's two instances; interval nonemptiness | S |
| T6 | Prop A.5 (mean bound lmax >= 1 + (N-1)*rbar, with equality iff constant row sums) | Rayleigh quotient at the all-ones vector; equality case needs the Rayleigh-maximizer characterization (available; the iff may cost the most of this entry) | M |
| T7 | Prop A.9 (rho nondecreasing in theta) WITHOUT Perron-Frobenius | Restructure to the elementary route: for entrywise-nonnegative symmetric A, xᵀAx <= |x|ᵀA|x|, so the Rayleigh sup is attained on the nonnegative orthant; then entrywise monotonicity of A(theta) gives monotone sup. Both steps are elementary inequalities Mathlib can express; this REPLACES the paper's P-F citation in the formal layer (paper prose can keep P-F; the Lean proof is the absolute-value trick) | M |
| T8 | Theorem 5 (two-block quadratic) | Avoid secular-equation manipulation: exhibit the 2-dim invariant subspace (block-constant vectors), verify A maps it to itself with the stated 2x2 matrix whose char poly is lam^2 - P*lam + Q; verify the orthogonal complement is spanned by explicit eigenvectors at the two diagonal values; conclude the spectrum by exhaustion; larger root is the max by comparison with T7's nonnegative-orthant Rayleigh argument. Also formalize the degenerate-block branch (the phantom-root warning becomes a machine-checked caveat, which is a lovely thing to be able to say) | M-L |
| T9 | Cadence: Lemmas C.1-C.2 (inner contraction, K-step slope) and Theorem 4 (window; K_max formula; K_max infinite iff m_N <= 1; strict monotonicity in m_N) | Scalar induction + log/exp monotonicity: `Mathlib.Analysis.SpecialFunctions.Log` covers it; the joint-map step reuses T3's shared-eigenvector fact | S-M |
| T10 | Imperfect-vaccine law + Cor. 6 (critical efficacy) at the k*s = 1 corner | Scalar algebra from T8's degenerate case | S |
| T11 | Wedge layer: V'(m) formula, FOC gap, Cor. 8 (over-adaptation via strict monotone F's), t* comparative statics | One-variable calculus (`deriv`, strict mono); the share lemma itself is NOT here (see T13) | M |
| T12 | NEW result from the adversarial review: coverage law optimistic away from the corner (law's rho* <= exact threshold) | Only if the paper-side Perron argument goes through on paper first; the Lean version would ride T7's machinery. Attempt after T7 | M, conditional |
| T13 | NOT formalizable now, stated so in Appendix K: Lemma 6 (eigenvalue perturbation / marginal shares), Appendix C concentration (needs Bernstein), anything needing full P-F (simplicity + positivity of the leading eigenvector) | Journal tier; contributing P-F to Mathlib is itself a freestanding contribution worth considering, but it is not this paper | L+ |

## 4. Sequencing

- Phase 0 (half day): Mathlib audit (the uncertain-names check), project
  scaffold, CI.
- Phase 1 = T1, T4, T5, T9-scalar, T10: the guaranteed-compilable set.
  If only Phase 1 lands by the deadline, Appendix K ships with exactly
  those rows and the paper's claim is scoped to them.
- Phase 2 = T2, T3, T6, T7: the spectral core. This is the set that
  makes the claim "the paper's central theorem is machine-checked."
- Phase 3 = T8, T11, T12: the full algebraic layer.
- Every phase gate: `lake build` green + axioms clean + MANIFEST
  regenerated.

## 5. What this buys in the paper (outline of the claims)

- Section 1: one clause in the evidence-stack sentence.
- Section 8: nothing (Lean checks algebra, not dynamics; keep the layers
  distinct or reviewers will conflate them).
- Appendix K: the table + scope paragraph (per `01-section-outlines.md`).
- Artifact release: the `formal/` tree with CI badge.

## 6. Claim-language rules (non-negotiable)

1. "Machine-checked" attaches to individual results listed in Appendix
   K, never to "the paper" or "the theory".
2. A result is listed only if it compiles against the pinned Mathlib
   with clean axioms on CI, on the day of submission.
3. Where the formal statement is a restructured route (T7's
   absolute-value argument standing in for Perron-Frobenius), Appendix K
   says so: the formalized statement is equivalent in conclusion, not a
   transcription of the prose proof.
4. Where the formal statement is narrower than the paper's (e.g., T3
   proved for the exact hypothesis set of Assumption 1), the table
   states the formal hypotheses.
5. Absences are listed with reasons (verified Mathlib gaps), which turns
   the limitation into a roadmap sentence rather than an omission.
