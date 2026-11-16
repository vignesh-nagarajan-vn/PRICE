# 3. Model, and private versus systemic stability

**Status: drafted.** Target 1.25 pages. Sources:
[`../math/00-notation.md`](../math/00-notation.md) and
[`../math/01-theorem1-alignment.md`](../math/01-theorem1-alignment.md).

Double-blind compliance: REFLEX appears in the third person as an ordinary
reference. No sentence positions it as the authors' own work, and no sentence
says the paper previously showed anything.

Two jobs, and the order matters. The framing comes first because it is the
paper's reason to exist at this venue, and the setup follows because it is what
makes the framing precise. A reviewer who reads only this section should be able
to state the thesis and check the stability condition.

---

## 3.1 The base result

Consider `N` symmetric dealers quoting the same instruments and sharing one pool
of informed order flow, coupled by a spillover `kappa in [0,1]`: one dealer
tightening its quotes raises the toxic flow routed to every dealer, in proportion
`kappa`. Each dealer periodically retrains on the flow it has observed and
redeploys. Write `m_1 = eps*beta/gamma` for a single firm's performative
retraining modulus, the factor by which one round of retraining amplifies a
perturbation to its own deployment, so that a firm in isolation is stable exactly
when `m_1 < 1`.

The joint retraining map of that market has Jacobian

```
   J  =  -m_1 [ (1 - kappa) I  +  kappa 1 1' ] ,
```

with a common mode at `-m_1 * N_eff`, `N_eff = 1 + kappa(N-1)`, and `N-1`
differential modes at `-m_1(1 - kappa)`. The common mode dominates, so the market
crosses into instability a factor `N_eff` earlier than any individual dealer's
own loop would. Measured in a shared-pool simulator with real spreads, inventory
and liquidity feedback, the amplification is `1.74x` at `N = 2` and `3.16x` at
`N = 3` against a linear prediction of `2` and `3`; the shortfall is flow
saturation, not disagreement (REFLEX, arXiv:2608.16155). [VERIFIED, base result]

That is inherited scaffolding and the paper does not re-derive it. Everything
from Section 4 onward turns on replacing one object in it.

## 3.2 Private against systemic stability

There are two questions here and they are not the same question. Is each agent
stable considered alone, `m_1 < 1`? And is the collection stable when its members
interact, `m_N < 1`? A shared environment separates them. Dealer A retrains and
redeploys, the pool of flow changes, dealer B observes a changed environment and
retrains on it, which changes the pool again, which A then retrains on. The loop
closes through the environment, and nothing in A's validation set contains B.

The consequence is the paper's thesis in one line. **Agent count is not a
descriptive characteristic of a market; it enters the stability condition.**
Systemic instability here is an emergent property of the interaction structure,
not a property that any agent has and could be tested for. Every firm can pass a
correctly specified single-agent stability check and the market can still
diverge.

Read as economics rather than as dynamics, this is an externality: no participant
internalizes the effect of its own adaptive behavior on the environment that
other adaptive participants face. The cost is real, it falls on parties outside
the transaction that produced it, and no price carries it. That is what makes
"is this model stable when deployed?" the wrong certification question in a
shared endogenous environment, and "is the ecosystem of interacting models
stable?" the right one.

The externality is **technological, not pecuniary** (Buchanan and Stubblebine,
1962): the coupling runs through the data-generating process each learner faces,
not through the price at which the firms trade with one another. The distinction
is load-bearing rather than decorative. Firms that affect each other only through
prices impose no market failure, because the price movement is a transfer and the
allocation stays efficient; firms that reshape the distribution their competitors
learn from change the production technology of everyone's forecast, and that is a
genuine efficiency loss. Section 7 prices it.

The question itself is not new. Beale et al. (2011) asked exactly this of banks,
showing that portfolio choices each individually prudent can be collectively
destabilizing when institutions diversify into the same positions. What changes
when the institutions learn is that the shared exposure is no longer a static
portfolio choice but a fixed point of everyone's retraining, and the degree of
sharing is set by the model supply chain rather than by any firm's allocation
decision.

## 3.3 The feedback reproduction number

Name the quantity now, because the rest of the paper is about controlling it.
Call `m_N` the **feedback reproduction number** of the market: the factor by
which a common perturbation is amplified per retraining round. Below one,
perturbations die out; above one, they compound. The analogy is not decoration.
`m_N` is a spectral radius of a linearized round-to-round operator, which is what
`R_0` is in the epidemiological setting, and the results that follow inherit more
of the epidemiological structure than the name alone would license. Section 6
recovers a coverage threshold and, past it, the imperfect-vaccine refinement of
that threshold with its critical efficacy.

Sections 4 through 7 use the name without re-explaining it.

## 3.4 The general case, and what is assumed

Theorem 1 needs three objects. Firm `i` has a **response Jacobian** `E_i`, the
`d x d` matrix describing how its own deployment reshapes the flow it faces. The
**alignment matrix** `R = (r_ij)` collects the normalized inner products
`r_ij = <vec E_i, vec E_j> / (||E_i||_F ||E_j||_F)`, a correlation matrix of
feedback directions rather than of returns or predictions; it is positive
semidefinite with unit diagonal. And the generalization is the single
substitution of `R` for `1 1'` in the Jacobian above. The base result is the
`R = 1 1'` corner, where every firm's feedback points the same way. Section 4
does the work; this is the definition list.

Four standing assumptions, each restated in Section 10 with its consequence.
**(A1)** All spectral statements are linearizations of the joint retraining map
around the joint equilibrium, with the simulator as the nonlinear check and the
gap reported rather than hidden. **(A2)** The identity in Theorem 1 is exact for
equal moduli `m_i = m_1`; unequal moduli give a two-sided bound whose tightness
is measured. **(A3)** Firms retrain on a common clock at a common cadence `K`;
asynchronous clocks are named as an extension and not attempted. **(A4)** Firms
couple through one pool with a scalar spillover `kappa`, and pairwise `kappa_ij`
folds into `R` only when it is separable.

A fifth is stated separately because it is the one that can fail. **(A5) The
common mode binds.** Differential modes carry slope `m_1(1-kappa)`, below one
whenever `m_1 < 1`, so every stability statement in the paper is a statement
about the common mode. This holds when `R` has nonnegative entries, where
Perron-Frobenius places the leading eigenvector of `R` in the nonnegative
orthant, and it fails under anti-alignment: Section 4's simplex configuration is
an explicit case where the all-ones direction is the most stable one rather than
the binding one. Shared vendors and shared pretraining corpora produce positive
alignment, so the regime the paper is about satisfies the condition. It is
checked rather than assumed, and under lazy retraining (Section 5) it is not
needed at all, since monotonicity places the binding mode at `lambda_max`
regardless of sign pattern.

## Figure budget

None. Section 4 gets the first figure. A schematic of the externality loop would
go in the appendix if anywhere, because at nine pages a diagram that carries no
measurement is not worth a column inch.

## Checklist

- [x] Base result stated in half a page, cited, not re-derived
- [x] Private-versus-systemic paragraph written before any algebra
- [x] Technological-not-pecuniary sentence present, with the reason the
      distinction is load-bearing rather than only the label
- [x] The feedback reproduction number named before Theorem 1, and the
      `R_0` correspondence flagged as structural rather than nominal
- [x] Standing assumptions listed compactly, each with a Section 10 counterpart
- [x] The Perron-Frobenius condition on "the common mode binds" stated, per
      [`../math/01-theorem1-alignment.md`](../math/01-theorem1-alignment.md)
- [x] Beale et al. (2011) acknowledged here, where the reader thinks of it,
      with the named delta rather than a bare citation
