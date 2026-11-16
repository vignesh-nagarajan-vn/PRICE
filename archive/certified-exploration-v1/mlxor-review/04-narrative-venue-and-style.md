# 4. The four-page spine, venue fit, and style

## 4.1 The spine works

Four pages is a brutal budget and this paper spends it well. The compiled
structure:

| page | carries |
|---|---|
| 1 | title, abstract, the retraining-as-fixed-point setup, contributions 1 and 2 |
| 2 | contributions 3 and 4, Positioning, the whole Model section, the saturation paragraph |
| 3 | Figure 1, Theorem 1 and its mechanism, Theorem 2 and the structure-proofness paragraph |
| 4 | Figure 2, the agent, Verified results, Baselines, Second economy, Real data, Limitations |

The spine is: *the perturbations are not free, here is exactly what they cost,
here is the floor, here is how to spend optimally, here is an agent that does
it, here is the whole thing measured.* That is one argument, it is stated in the
first paragraph, and every section advances it. The abstract's opening sentence
("must pay, in its own objective, to learn how it moves the world") and the
Section 1 question ("What does it cost to learn your own influence?") are the
same sentence twice, which is the right kind of repetition at this length.

Two structural choices are worth naming as good, because they are the ones a
shorter paper usually gets wrong:

**The Positioning paragraph is doing the work of a related-work section in
one dense block, and it dispatches by naming the delta rather than the
topic.** "Lai and Robbins's adaptive designs are *points on* our frontier" is
the best sentence in the paper. Keep the structure; `01` adds two dispatches
to it.

**The Limitations paragraph is in the body, not the appendix, and it names
four real limits including the one that undercuts the headline** (the `o(1)`
amplitude qualifier is "load-bearing"). At four pages most authors would move
this to the appendix. Not moving it is why the rest reads as credible.

## 4.2 Where the spine strains

**Section 4 is the compressed one.** Three theorems (T5 shape, T6 support, T7
anchor) share a single paragraph with bolded run-in heads, and each gets two to
three sentences. T6 in particular arrives as "The exponential family is
Chebyshev-degenerate on thin designs" with no explanation of why a reader should
care until the callback in Section 5 ("a cliff we later hit twice in the wild").

This is a real cost but it is the right trade at four pages, and the callback
does rescue it. The one cheap improvement, if a line becomes free: move the
"cliff we later hit twice" clause forward so it lands with the theorem instead
of after it. Zero net cost, it is a clause relocation:

> \textbf{Support (T6).} The exponential family is Chebyshev-degenerate on thin
> designs: fewer than three support points (or vanishing spread, or collinear
> probe schedules) cannot identify $(C_0, C_1, c)$, a cliff we hit twice in the
> wild (\S\ref{sec:experiments}).

then delete " --- a cliff we later hit twice in the wild (\S\ref{sec:experiments})"
from where it currently sits.

**Page 4 is doing too much.** Figure 2, the agent's four-step description, all
of Section 5 (headline rows, baselines, second economy, real data), and
Limitations. The agent paragraph alone is 150 words of dense mechanism. If the
style-file swap in 4.4 costs any lines, this is where the pressure lands, and
the checklist's trim order handles it correctly (Figure 2's width first).

**The abstract is one 250-word paragraph.** It is well built and every clause
earns its place, but it is a wall. No fix proposed: at this length a structured
abstract would cost more than it returns, and the workshop's own template does
not encourage one.

## 4.3 ML x OR fit: this is a bullseye, and the paper undersells it

The workshop's title is "Mathematical Foundations and Operational Integration of
Machine Learning for Uncertainty-Aware Decision-Making". This paper is
mathematical foundations (an invariance identity, minimax floors, an optimal
design theory) plus operational integration (a deployable agent, a second
economy, a real-data calibration) for a decision-maker under uncertainty about
its own influence. It is hard to construct a better fit.

The OR half of the audience is served well in places and left out in others:

**Served:** the incomplete-learning line (Rothschild, Harrison-Keskin-Zeevi,
Keskin-Zeevi, Broder-Rusmevichientong, den Boer) is cited and dispatched, and
Lai-Robbins is positioned as a point on the frontier. The dual-control and
least-costly-identification inheritance (Feldbaum, Bombois) is named. The
classical design canon (Kiefer-Wolfowitz, Pukelsheim) is there.

- **Not served:** the model is a market maker and there is no market-making
  citation anywhere. See `01` section 1.3. This is the single largest
  audience-calibration gap and it is cheap to close.

One framing suggestion, no page cost. The abstract's parenthetical currently
reads "(a market maker whose quoted spread summons adverse flow)". For an OR
audience the operational hook is stronger if it names the decision problem
rather than the setting:

> (a dealer whose quoted spread summons the adverse flow it must then price)

## 4.4 Format compliance: the style file is a real problem, and the fix is in this repo

**The call for papers asks for the `sglblindworkshop` option.** Verified by
loading `mlxor-2026.github.io` directly: "Please use the NeurIPS 2026 paper
format" with "the 'sglblindworkshop' option".

The paper uses `\usepackage[final]{neurips_2025}` plus a manual
`\renewcommand{\@noticestring}` hack to override the hardcoded main-conference
footer. I read the shipped `neurips_2025.sty`: it declares exactly three
options, `final`, `nonatbib` and `preprint`. **The required option does not
exist in the file the paper is built against.** The checklist treats this as a
cosmetic stopgap ("when the official `neurips_2026.sty` drops, swap the file").
It is not cosmetic; the submission is currently in the wrong format, and the
`\@noticestring` hack exists precisely because the right option is missing.

**The file is already in this repository.** `econml/paper/neurips_2026.sty` is
the official 2026 style, and it declares `sglblindworkshop`, `dblblindworkshop`,
`nonanonymous` and the track options alongside `final`. The EconML paper is
built against it (`\usepackage[dblblindworkshop]{neurips_2026}`).

**I tested the swap rather than recommending it blind.** Copied
`econml/paper/neurips_2026.sty` into a scratch copy of `paper/`, rewrote the
preamble, deleted the `\@noticestring` hack, and rebuilt twice:

| build | pages | overfull | content ends | References | footer |
|---|---|---|---|---|---|
| `[sglblindworkshop]` | 14 | 0 | p. 4 | p. 5 | "Submitted to 40th ... Do not distribute", line numbers on |
| `[sglblindworkshop,final]` | 14 | 0 | p. 4 | p. 5 | "40th Conference ... Workshop: Second Workshop on ML x OR." |

Author names and emails are visible in both, which is what single-blind wants.
**The page budget survives the swap in both variants**, which was the checklist's
stated worry.

### Exact changes

Copy `econml/paper/neurips_2026.sty` to `ml-or/submission-materials/paper/`,
then in `main.tex` replace lines 3 to 6:

```
% ML x OR @ NeurIPS 2026: 4-page main body, NeurIPS conference format,
% non-anonymous ([final]), unlimited references + appendix.
% Swap neurips_2025.sty for the official neurips_2026.sty when released.
\usepackage[final]{neurips_2025}
```

with:

```
% ML x OR @ NeurIPS 2026: 4-page main body, NeurIPS conference format,
% single-blind workshop track (author block visible), unlimited refs + appendix.
\usepackage[sglblindworkshop]{neurips_2026}
\workshoptitle{Second Workshop on ML$\times$OR}
```

and delete lines 22 to 26 entirely, the `% Workshop footer` block with its
`\makeatletter ... \makeatother` hack. `\workshoptitle` now feeds the sty's own
`\@trackname` and the hack would fight it.

**Which variant to submit.** Take `[sglblindworkshop]` alone, which is what the
CFP asks for literally; it turns on line numbers, which reviewers want, at the
cost of a generic footer that does not name the workshop. Add `,final` at
camera-ready, which removes the line numbers and prints the workshop track name
in the footer, which is what the manual hack was trying to achieve all along.
Both compile clean and both hold page 4.

Delete `neurips_2025.sty` from the folder afterwards so nothing builds against
it by accident.

## 4.5 Journal designation: Stochastic Systems is still right

Verified from the CFP: three pathways (Stochastic Systems, Mathematics of OR,
Operations Research), "Authors may indicate at most one journal". It is free
optionality with no downside, so indicate one.

I re-read the Stochastic Systems editorial statement. It is the INFORMS Applied
Probability Society's flagship, publishes only OR content, wants applied
probability in "a significant, and not just supporting, role", and explicitly
welcomes "papers that explore the ties between applied probability and
optimization, or with machine learning" and work "at the interface of
stochastics, modeling, statistics, and data science". That is this paper.

**Endorse the checklist's recommendation.** Two reasons beyond fit:

1. **The stability-of-a-stochastic-feedback-loop content is the applied
   probability**, and it is central rather than decorative: the modulus governs
   the saturation cap, the excitation floor, the confidence-sequence gate and
   the L4 certificate. A journal that wants applied probability in a leading
   role gets exactly that.
2. **OPEN-1 is still open.** Mathematics of OR would reasonably want the sharp
   constant proved rather than conjectured, and the paper would be arriving with
   its headline constant at 1/27 instead of 1/2 (see `02`). Stochastic Systems
   is the better-calibrated bet for the paper as it actually stands.

**The one condition that would change this.** If OPEN-1 closes before the
journal submission, the paper becomes a sharp minimax theorem with an exact
invariance identity and a complete design theory, and Mathematics of OR is the
right home for that. Do not indicate MOR now on the hope; the designation is
made at workshop submission and the proof is not in hand.

Operations Research is the wrong one of the three. The paper's contribution is
theory, not an application or a methodology for a class of operational problems,
and the real-data leg validates machinery rather than delivering an operational
result. The paper says so itself in the limitations.

## 4.6 Style

The voice is good and it should not be sanded. Short claim-first sentences,
bolded run-in heads doing real navigational work, and a refusal to hedge that
is earned by the evidence behind it. "The stabler the loop, the less it reveals:
safety implies blindness" is the paper in seven words. Keep all of it.

Four things to fix.

**(a) 34 em dashes in a four-page body.** The repository's convention is no em
dashes; the EconML paper has zero across `main.tex`, `appendix.tex` and both
checklist files. This paper has 34 `---` in `main.tex` alone. Beyond the house
rule, at this density they stop working as punctuation: the Positioning
paragraph has four in six sentences, and the Section 3 structure-proofness
paragraph has three in one sentence. Most convert to a comma or a colon with no
loss; a few want a full stop. Worked examples:

> the invariant prices \emph{exploration}, not \emph{suboptimality}

(from "--- the invariant prices..."; a full stop before it, and the sentence
stands on its own)

> a quotable inversion of ``naive exploration is optimal'' for LQR
> \citep{simchowitz2020naive}: a support-degeneracy theorem and a
> misspecification crossover complete the design picture

(colon for the dash)

> \emph{The floor is an ignorance-of-curvature phenomenon}: the correct scope
> for the general theorem

This is a mechanical pass over 34 sites, roughly an hour, and it slightly
*reduces* line count because `---` sets wider than a comma. It pays for one of
the additions in `01`.

**(b) "converges iff" in Section 1** attributes an iff to Perdomo et al. Their
theorem is a sufficient condition. Replace with "converges when". One word.

**(c) The modulus is defined twice with different formulas**, `\eps\beta/\gamma`
in Section 1 and `\eps/\gamma` in Section 2. Both correct because `\beta = 1` in
this model, which the paper never says. Fix in Section 2:

> a contraction iff the modulus $m = \eps\beta/\gamma = \eps/\gamma$ ($\beta=1$
> here) is below one \citep{perdomo2020performative}

**(d) Two overloaded sentences.** The agent paragraph's step (iii) runs 62 words
through a gate condition, a Lipschitz constant, a lemma reference and a
mechanism. The Section 5 real-data sentence runs 70 words through three
different quantities with three different units. Neither is wrong; both are read
twice. If a line frees up, split step (iii) after "margin":

> \emph{gate}: apply the performative correction $-(h-\psi)\hat\eps$ with Newton
> scaling $\eta = 1/\hat\gamma_{\mathrm{PO}}$ only if
> $\eta \cdot \mathrm{ci}_t \cdot L_{\mathrm{fam}} \le \text{margin}$. The
> perturbed-modulus lemma (L4), with the family's own Lipschitz constant
> $L_{\mathrm{fam}} = 1 + \hat c\,|h - \psi|$, converts estimation error into a
> certified bound on the closed-loop modulus.

Low priority. It is a readability item, not a defect.

## 4.7 The three duplicate trees

`ml-or/` carries the same content three times: `math/` plus
`ml-contributions/`, then `ml-contributions/finalized-materials/`, then
`submission-materials/`. Only the last has `paper/`, `references.bib` and
`SUBMISSION-CHECKLIST.md`; the other two are earlier snapshots, and
`ml-contributions/posk/` is missing `baselines.py`, `pricing.py` and
`multibond.py` entirely, so it predates three of the paper's experiments.
Compiled `__pycache__` directories are committed in two of them.

This does not affect the submission. It affects what happens when the repository
is pushed public, which the checklist's item 2 requires before the deadline
because reviewers will click the abstract's link. A reviewer landing on a tree
with three copies of the derivations, two of them stale, forms a worse
impression than the work deserves, and may read the wrong `THEOREMS.md`.

**Fix at push time, not now:** push only `submission-materials/posk-pipeline/`
and `submission-materials/mlxor-derivations/` as the public repository, exactly
as the checklist already says. Add `__pycache__/` to `.gitignore` there. Leave
this working tree alone; the snapshots are history and history is fine to keep
privately.
