# 2. Technical rigor, proofs and the assumption register

## 2.1 The proofs are sound. Do not spend deadline time re-reading them.

Every proof in `proofs_body.tex` was read line by line against `THEOREMS.md`,
the assumption register, and the corresponding derivation document: L1, T1,
C1.1, C1.2, R1, T2, P2.1, P2.2, T3, L2, T4, T5a-c, C5.1, L3, T6, L4, R2, P7.1,
T7, T8, P9.1, P9.2, P9.3. The algebra in T5a-c, C5.1, T7 and T8 was re-derived
by hand and again numerically.

**No proof is wrong.** The KKT arguments for the three optimality shapes are
correct and their global-optimality certification is legitimate (convex
objective, one linear constraint, PSD cone). C5.1's Cauchy-Schwarz gives
`F >= 1` with the stated equality condition, and `F <= d` with equality iff one
nonzero eigenvalue, matching the register's `[1, d]`. L2's three ingredients
(imbalance equals total variation, the KL chain rule cancelling the policy
factors, Cauchy-Schwarz twice) are each right, and the remark that the rigorous
chain changes the exponent bookkeeping but not T4's conclusion is honest and
accurate. T7's constrained optimum is correct: the budget fixes `S = 2B/gamma_PO`,
the horizon caps observations, bias increases in `w`, so `w^2 = 2B/(gamma_PO T)`.
T8's NPV is strictly concave and `gamma_PO` genuinely cancels between `a` and
`b`; I checked the break-even sign flip in both directions.

The defects below are all between the **body** and the appendix. Four of them
are scope slips where the 4-page body asserts more than Appendix B proves. The
paper's own registers are more careful than its body text, which is the good
news: the fix is to say what is already known internally.

## 2.2 The one that matters: Theorem 2(ii) claims what Appendix B calls conjectured

The body says (Section 3, Theorem 2):

> (ii)~Under a budget on realized performative cost with certainty-equivalent
> anchoring, the floor $\tfrac{1}{2}\gpo\sigma^2(1-o(1))$ holds with sharp
> constant over two-point symmetric priors (correction rate $T^{-1/2}$), and
> within constant factor ($\ge \gpo\sigma^2/27$, Le~Cam) over general priors.

Appendix B of the same PDF says, at the end of the T4 proof:

> The sharp constant $\tfrac{1}{2}\gpo\sigma^2$ -- numerically supported (V3.4:
> no simulated policy fell below it) -- requires the van Trees route with cost
> control in place of the two-point reduction and is part of OPEN-1.

Appendix A says it too: "The sharp constant $\tfrac{1}{2}$ ... is conjectured
and is part of OPEN-1." `THEOREMS.md` gives T4 status `PV*` with the note that
`proofs.tex` establishes the constant-factor version rigorously and "the sharp
constant 1/2 -- numerically supported -- and general priors = OPEN-1".

So the body states as a numbered theorem what the appendix, in the same
document, twice labels a conjecture. A reviewer who reads both finds the paper
contradicting itself, and they will be right.

The proof does not support the body. Read it: T4 *chooses* a two-point prior at
separation `delta = c sigma/sqrt(S_bar)`, applies Le Cam, and lands on
`gamma_PO sigma^2/27`. There is no argument anywhere in `proofs_body.tex` that
gets 1/2 on the two-point family. The 1/2 comes from `derivations/04` section 3,
which multiplies a `Var >= sigma^2/S_T` bound by a `C_T >= (1/2) gamma_PO S_T`
bound. That composition is heuristic: it is not a joint minimax over
(policy, estimator), which is exactly why `proofs.tex` replaced it with the Le
Cam route and lost the constant.

Note also that the paper's own documents disagree with each other on this point.
`OPEN-PROBLEMS.md`'s OPEN-1 entry says "**Proved today.** The two-point
symmetric family, with explicit correction constant ... and rate `T^{-1/2}`".
`proofs.tex` and `THEOREMS.md` say the opposite. The body followed
`OPEN-PROBLEMS.md`. Reconcile the three documents to the conservative reading,
because that is the one the LaTeX proof supports and the LaTeX proof is what
ships in the PDF.

The claim appears in four places and all four are wrong in the same direction:
the abstract, contribution bullet 2, Theorem 2(ii), and the limitations
paragraph. The limitations sentence is the most damaging, because it explicitly
frames the gap as being *beyond* two-point priors and so reinforces the false
half.

### Replacement text

**Abstract**, replacing "sharp-constant for value budgets over two-point priors":

> constant-factor for value budgets, with the sharp constant numerically
> supported

**Contribution bullet 2**, replacing "with sharp constant over two-point priors,
and within a factor $\le 13.5$ in general, under value budgets":

> within a factor $\le 13.5$ under value budgets, with the sharp constant
> numerically supported but open

**Theorem 2(ii)**, replacing the whole clause:

> (ii)~Under a budget on realized performative cost with certainty-equivalent
> anchoring, the floor holds within a constant factor over adaptive policies:
> $\sup \Var(\hat\eps)\times C_T \ge \gpo\sigma^2/27\,(1-O(T^{-1/2}))$ by a Le
> Cam two-point reduction, the exploited rebate vanishing at rate $T^{-1/2}$
> (Lemma~\ref{lem:exploit}). The sharp constant $\tfrac{1}{2}$ is numerically
> supported and open (OPEN-1).

**Limitations paragraph**, replacing "The value-budget sharp constant beyond
two-point priors is numerically supported, not proved":

> The value-budget floor is proved to within a factor $13.5$; the sharp constant
> $\tfrac{1}{2}$ is numerically supported, not proved, at any prior class.

This costs nothing on the page (the replacements are the same length or
shorter), it removes the only thing in the paper a reviewer can be flatly right
about, and the result that remains is still good: a constant-factor minimax
floor over adaptive policies for a product of variance and regret, with the
sharp constant conjectured and evidenced. That is a normal, strong theorem
statement.

## 2.3 Theorem 2(i) overstates T3 in three ways

Body:

> (i) Over all non-anticipating (possibly randomized, adaptive) policies with
> expected design energy $\E S_T \le B$: $\inf \sup \Var(\hat\eps) \ge
> \sigma^2/B$, hence the product floor holds exactly.

Appendix A, Theorem T3:

> Over all non-anticipating exploration policies with $\sum_{t\le T} \dev_t^2
> \le D$ almost surely and all estimators (biased included), the minimax risk
> over an interval of width $w$ satisfies $\inf\sup \E[(\hat\eps-\eps)^2] \ge
> \sigma^2/(D + \sigma^2(\pi/w)^2)$.

Three slips:

1. **Expected budget versus almost-sure budget.** The proof says "under the
   pathwise budget" explicitly. Policies satisfying `E S_T <= B` form a strictly
   larger class than those satisfying the constraint almost surely, and the
   bound is not proved over the larger one.
2. **The dropped prior term.** `sigma^2/B` is strictly larger than
   `sigma^2/(D + sigma^2(pi/w)^2)`, so the body claims a *stronger* bound than
   the proof gives. This is not a rounding matter. T3 covers biased estimators,
   and for biased estimators `sigma^2/D` is false: an estimator that shrinks
   toward the prior mean beats it. The `(pi/w)^2` term is what makes the van
   Trees statement true, and deleting it turns a correct theorem into an
   incorrect one. I computed the gap at two cells: 4.8 percent at
   (D=150, w=0.8, sigma=0.7) and 0.4 percent at (D=400, w=1.2, sigma=0.5). Small
   numerically, fatal logically.
3. **`S_T` versus `D_T`.** The body writes the constraint on `S_T`, which
   Section 3 defines as the *centered* energy `sum (d_t - dbar)^2`. T3
   constrains the *uncentered* `sum d_t^2`, which the register calls `D_T`.
   These differ by `T dbar^2`. The body's own mechanism paragraph notes the two
   coincide "for mean-centered exploration", which is precisely the condition
   not imposed here.

### Replacement text

Theorem 2(i), same length:

> (i) Over all non-anticipating (possibly randomized, adaptive) policies with
> pathwise deviation budget $\sum_{t\le T}\dev_t^2 \le D$, all estimators
> included, and any prior of width $w$:
> $\inf\sup\Var(\hat\eps) \ge \sigma^2/(D + \sigma^2(\pi/w)^2)$, so the product
> floor is attained up to the prior term, with equality by symmetric probing.

If the display is too long for the body at 4 pages, this shorter form is also
correct and costs less:

> (i) Over all non-anticipating policies with pathwise budget
> $\sum_t \dev_t^2 \le D$ and all estimators: $\inf\sup\Var(\hat\eps) \ge
> \sigma^2/D\,(1-o(1))$ by van Trees, attained by symmetric probing.

Then delete "hence the product floor holds exactly" and let the following
paragraph carry the frontier claim, which it already does.

## 2.4 The echo-chamber gap points the wrong way

Section 2 says:

> it converges to the stable point $\hsp$, while the optimum
> $\hpo = \arg\max\Phi$ sits at a wider spread --- the echo-chamber gap

In this model the optimum sits at a **tighter** spread. Verified two ways, from
my own re-implementation of Section 2's formulas and from the pipeline's own
`Market`, which agree to four decimals:

| market | `h_SP` | `h_PO` | `h_SP - h_PO` |
|---|---|---|---|
| register default | 2.0926 | 1.8461 | +0.2465 |
| m = 0.30 | 2.2019 | 1.6080 | +0.5939 |
| m = 0.60 | 2.4065 | 1.2964 | +1.1101 |
| m = 0.85 | 2.5808 | 1.1902 | +1.3906 |

Three of the paper's own artifacts already say so. `REALDATA.md` reports the gap
as a positive "gap `h_SP - h_PO`" column in all ten cells. Table 1's row "SafeD
reaches $\hpo$ ... $1.324$" is at `m = 0.6`, where `h_SP = 2.41`: the agent steps
down, not up. And `OPEN1.md` anchors at `h* = h_PO = 1.8461`, below the stable
point.

The economics is straightforward once the sign is right. With `psi = 0.4` and
`h` near 2, the term `(h - psi) tau(h)` is positive: toxic flow is profitable
net of adverse severity in this parameterisation, so internalising the response
makes the dealer quote *tighter* to summon more of it. Blind retraining, which
treats the toxic level as frozen, quotes too wide.

Worth noting for the author's own reassurance: the sign is genuinely
model-specific, not universal. In the LQ pricing domain of E8 the ordering
reverses (`p_SP = 7.14`, `p_PO = 12.5`), which I also verified independently.
That is a nice fact and it is currently invisible.

### Replacement text

Section 2, replacing "sits at a wider spread":

> sits at a \emph{tighter} spread here, since toxic flow is profitable net of
> $\psi$

Optional, if the transplant paragraph in Section 5 has a spare clause, appended
to the second-economy sentence at zero net cost by trimming "once its
deterministic probe schedule was randomized" to "once its probes were
randomized":

> the gap's sign flips with the sign of the response's profit contribution

## 2.5 The body's assumption labels are wrong, and the PDF never defines them

Section 2 contains the paper's only assumption glosses, and two of the three are
mislabelled against the register in `derivations/00-notation-and-assumptions.md`:

| Body text | Body's label | Register's actual content |
|---|---|---|
| "Deployments return noisy flow $y_t = \tau(h_t) + \sigma\xi_t$ **(A2)**" | A2 | A2 is the *exploration class* (non-anticipating; sym vs adaptive). Noise exogeneity is **A3** |
| "(A1: local quadratic scope; **A3**: stationary exploration scale)" | A3 | A3 is noise exogeneity. `S_T = Theta(T)` is **A5** |

Theorem 1 in the body is stated "Under A1--A3". The register gives T2's
assumptions as A1, **A2-sym**, A3, A6. The `-sym` qualifier is not cosmetic: it
is exactly the condition under which Lemma L1's linear term vanishes in
expectation, which is the whole reason the identity is an identity. A6 (`m < 1`)
is load-bearing too, since the stationary deviation variance
`v = sigma_e^2/(1-m^2)` does not exist without it.

Compounding all of this: **A1 through A6 are cited eighteen times in the
compiled PDF and defined nowhere in it.** `mlxor-derivations/latex/proofs.tex`
opens with a standing-assumptions paragraph ("Throughout, the local model of
Assumptions A1--A6: $\dev_{t+1} = -m\dev_t + u_t$ ... $\Phi$ three times
differentiable and strongly concave ... with $\Phi'(\hstar) = \delta_0 \neq 0$")
but that paragraph sits *above* the `% BEGIN BODY` marker, so `proofs_body.tex`
starts below it and it never reaches the paper. The appendix inherits the
citations without the definitions.

This is the cheapest high-value fix in the package. The appendix is unlimited,
so it costs zero body lines.

### Replacement text

**Section 2**, two label corrections:

> Deployments return noisy flow $y_t = \tau(h_t) + \sigma\xi_t$ (A3).

> anchored at the certainty-equivalent operating point $\hstar$ (A1: local
> quadratic scope; A5: stationary exploration scale).

**Theorem 1's hypothesis**, replacing "Under A1--A3":

> Under A1, A2-sym, A3 and A6

**New first paragraph of Appendix B**, to be inserted at the top of
`proofs_body.tex`. This is the paragraph that already exists in `proofs.tex`
above the marker, plus the register list. Zero body cost:

> Throughout, the local model of Assumptions A1--A6.
> \textbf{A1} (local quadratic scope): $\Phi$ is $C^3$ and strongly concave on
> the operating interval, expansions taken at $\hstar$ with third-order
> remainder bounded by $L_3 = \sup|\Phi'''|$.
> \textbf{A2} (exploration class): all policies are non-anticipating; A2-sym
> additionally requires $\E[u_t\mid\mathcal{F}_t]=0$, A2-adaptive is
> unrestricted and costs are measured from the certainty-equivalent anchor.
> \textbf{A3} (noise exogeneity): $\zeta_t$ i.i.d., mean zero, variance
> $\sigma^2$, independent of $\mathcal{F}_t$.
> \textbf{A4} (trust region): $|\dev_t| \le r$ pathwise.
> \textbf{A5} (stationary scale): $S_T = \Theta(T)$.
> \textbf{A6} (stable base loop): $m<1$, equivalently $\rho(M)<1$.
> The local dynamics are $\dev_{t+1} = -m\,\dev_t + u_t$ with
> $\dev_t = h_t - \hstar$ and $\tau_t = \tau(\hstar) - \eps\,\dev_t + \zeta_t$,
> with $\Phi'(\hstar) = \delta_0 \neq 0$ and $-\Phi'' = \gpo$ at the operating
> point.

The simplest way to make this permanent is to move `proofs.tex`'s
`% ================= BEGIN BODY =================` marker up so it sits above
that paragraph, and add the A1-A6 list there. Then the single source of truth
carries it and nothing can drift.

While in that file: the T7 variance derivation contains a literal
`\cdot\ldots` inside a display,

> $(2\sigma^2/n)/(4w^2) = \sigma^2/(n\,w^2\,2)\cdot\ldots = \sigma^2/S$

which compiles to a stray ellipsis in the submitted appendix. The arithmetic is
right (`2 sigma^2/(4 n w^2) = sigma^2/(2 n w^2)` and `S = 2nw^2`). Replace with:

> $\dfrac{2\sigma^2/n}{4w^2} = \dfrac{\sigma^2}{2nw^2} = \dfrac{\sigma^2}{S}$

## 2.6 T6's proof gives the wrong reason for a true result

The proof of T6 says a two-point design's Fisher matrix is singular "and its
null space necessarily has a component along the $c$-sensitivity (otherwise the
two-point system would determine all three parameters, contradicting the
Chebyshev property)".

The parenthetical does not support the claim. A singular information matrix can
still leave a particular linear functional estimable; singularity alone says
some direction is lost, not that the `c` direction is. The result is true and
there is a two-line argument for it.

Write `n` for the null vector of the 2-by-3 design matrix, so
`n . s(h_1) = n . s(h_2) = 0` with `s(h) = (1, e^{-ch}, -C_1 h e^{-ch})`. The
`c` component is estimable only if `n_3 = 0`. But `n_3 = 0` forces
`n_1 + n_2 e^{-c h_i} = 0` for `i = 1, 2`, and for `h_1 != h_2` the two
exponentials differ, so `n_1 = n_2 = 0` and `n = 0`, a contradiction. Hence
`n_3 != 0` for every pair of distinct support points and `c` is never estimable.

Checked numerically: over 20000 random distinct pairs on `[0.3, 3.0]` the
smallest `|n_3|` is 0.439, comfortably bounded away from zero.

### Replacement text

Replacing the parenthetical:

> and that null space always loads on the $c$-sensitivity: writing $n$ for the
> null vector, $n_3 = 0$ would force $n_1 + n_2 e^{-ch_i} = 0$ at both support
> points, hence $n = 0$ for $h_1 \neq h_2$.

The Chebyshev/Karlin-Studden material stays: it is what gives the
existence of exactly-three-point D-optimal designs, which is the constructive
half of the theorem.

## 2.7 Four proofs in Appendix B have no statement anywhere in the paper

Appendix A states 19 of the register's 25 results. Appendix B proves 23. The
four proved-but-never-stated results are **P2.1** (concentration), **P9.2**
(isotropy contrast), **R1** (non-normal transient information) and **R2**
(open-loop neutrality). The compiled PDF therefore contains "Proof of Remark R2
(open-loop neutrality)" with no Remark R2 anywhere above it.

`check_docs.py`'s C6 check only tests the other direction (every register ID has
a proof), so it cannot catch this, and in any case C6 never runs to completion
because the suite crashes first (see `05`).

Cheapest fix, zero body cost, appendix is unlimited: add four one-line
statements to `theorems_body.tex` in register order. Suggested text:

> \begin{proposition}[Concentration; P2.1]
> The measured product concentrates at rate $T^{-1/2}$, with long-run
> $\Var(\sum_t \dev_t) = T v (1-m)/(1+m)$.
> \end{proposition}
>
> \begin{remark}[Non-normal transient information; R1]
> The energy identity $\dev_0^\top P \dev_0$ holds for non-normal $M$ as well,
> where it can exceed the spectral cap by up to $\kappa(V)^2$.
> \end{remark}
>
> \begin{remark}[Open-loop neutrality; R2]
> History-independent exploration schedules cannot change the linearized
> contraction rate.
> \end{remark}
>
> \begin{proposition}[Isotropy contrast; P9.2]
> Naive isotropic exploration, optimal in isotropic LQR-like settings, overpays
> by exactly $F$ in the performative setting, with $F = 1$ iff the curvature
> spectrum is flat.
> \end{proposition}

The alternative, deleting the four proofs, is worse: R2 is cited implicitly by
the agent's design and P9.2 is the formal version of the paper's most quotable
sentence.

## 2.8 Small precision items

**The modulus is defined twice, differently.** Section 1 writes
`$m = \eps\beta/\gamma < 1$`; Section 2 writes "a contraction iff the modulus
$m = \eps/\gamma < 1$". Both are right, because `beta = 1` at the stable point
in this model (the code says so in a docstring), but the paper never says so.
Fix in Section 2, three words: "the modulus $m = \eps\beta/\gamma = \eps/\gamma$
($\beta = 1$ here)".

- **"converges iff"** in Section 1 attributes an iff to
  `\citet{perdomo2020performative}`. Their theorem gives contraction under
  `eps beta/gamma < 1`; the converse is a counterexample, not a theorem. Replace
  "converges iff" with "converges when".

**Cross-referencing friction between body and appendix.** As compiled, T2 is
Theorem 1 in the body and Theorem 4 in Appendix A; T3/T4 are body Theorem 2
and appendix Theorems 5 and 6. Appendix B refers only to register IDs
("Proof of Theorem T3"). The register tag in each statement title is the only
bridge, and it works, but one sentence at the end of Section 2 removes all
doubt at a cost of eleven words: "Results carry their register identifiers
(T1, T2, ...) in both appendices."

**`\hstar` is a third object in the paper and the same as `h_SP` in the
register.** The register's notation table says `h*` is the performatively
stable point and `h_SP = h*`. The paper uses `\hstar` for the
certainty-equivalent anchor while also using `\hsp` and `\hpo`. Since Appendix
B's dynamics are written in `\hstar`, a reader who takes the register's
meaning gets a different theorem. The new Appendix B preamble in 2.5 fixes
this by defining `\hstar` as the operating point in the paper's own terms; the
register should be updated to match rather than the other way round, since the
paper's usage is the more general one.

## 2.9 Journal-strength upgrades, correctly deferred

In priority order for the journal version, all of which the paper already knows
about and correctly defers:

1. **OPEN-1: the sharp constant by the conditional van Trees route.** The
   strategy in `OPEN-PROBLEMS.md` is the right one and the obstruction is
   correctly identified (the anchor moves with the posterior). This is the
   single result that would convert Theorem 2 from constant-factor to sharp and
   it is the journal version's headline.
2. **Structure-proofness as a theorem.** The numerical finding that the
   parametric Cramer-Rao product is minimized by the symmetric local design is,
   on my search, exact rather than approximate: my optimizer reaches 1.00007
   with the support collapsing to a cluster of spread 0.007 around the anchor.
   An equivalence-theorem argument in the Kiefer-Wolfowitz style may well prove
   `inf = 1` outright. That is a contained, provable lemma and it is more
   interesting than the 1.005 the paper currently quotes.
3. **P7.1 from COND to P.** The confidence sequence's validity is the standing
   hypothesis; constructing it from the D2 information accounting is described
   as routine and probably is. Doing it removes the paper's only conditional
   result.
4. **OPEN-2 and the coupled multi-bond case.** P9.3 is exact only in the
   separable case; the coupled case is first-order with a stated error. The
   d-dimensional story is currently the thinnest leg of the theory.
5. **L3's failure under A3'.** The temporal-shaping lemma is what collapses the
   design space to static measures and so makes T5 complete. `OPEN-4` correctly
   flags that it fails under the noise-feedback relaxation. Stating what
   replaces it under A3' would generalise the whole design section.
