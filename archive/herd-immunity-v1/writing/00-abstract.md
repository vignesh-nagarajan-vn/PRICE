# Abstract

**Status: rewritten 19 Aug 2026**, after Sections 6 and 7 landed and panel 6 ran.
Target 150 to 200 words.

---

## Draft

A learning agent can satisfy every single-agent stability criterion and still
help destabilize the market it operates in. When adaptive agents share an
environment that reacts to their decisions, each agent's retraining reshapes the
data every other agent learns from next, a **learning externality** that no agent
internalizes. We show its strength is governed not by the number of firms but by
the **effective number of independent learners**, the leading eigenvalue of the
correlation matrix of firms' response Jacobians, so foundation-model
concentration enters the stability condition as a term rather than as a concern:
fifty firms fine-tuning one vendor's model are dynamically close to one large
learner. Three closed-form levers follow. A crowding-cadence frontier bounds how
often a market can retrain, and closes past a critical crowding level. A
herd-immunity threshold makes the market stable once the corrected
fraction exceeds `(1 - 1/m_N)/e` at correction efficacy `e`, the imperfect-vaccine
coverage law with the systemic modulus as the reproduction number, exact in the
fully shared limit and accurate away from it, and correction
stops working entirely below a critical efficacy. A Pigouvian wedge prices the
externality and shows every market of two or more firms over-adapts. The last two
levers are substitutes, along a frontier we compute. In a shared-pool order-flow
market the mechanism reproduces a published `1.74x` and `3.16x` amplification at
two and three firms, at relative error `0.00e+00`.

---

## Notes

**Word count.** 221 as drafted, over the 200 ceiling by 21. The cut is the
critical-efficacy clause and the fifty-firms illustration, together 30 words,
both of which Section 4 or Section 6 states again within a page. Do not cut the
closing sentence.

**What changed from the previous draft.** Three things, all forced by results
that landed after it was written. The herd-immunity law is quoted in its
**imperfect-correction** form rather than as `1 - 1/m_N`, because the clean form
is the perfect-efficacy corner and the strong-correction limit errs optimistic;
an abstract quoting only the corner would state a criterion the paper spends a
section correcting. Over-adaptation is named, since Theorem 4 is now proved
rather than sketched. And the abstract now ends on a **measured** number as
planned, which is panel 1's external replication rather than experiment 5's
frontier: experiment 5 is a dry run and cannot carry the closing sentence.

**On the closing sentence, and it is the one to check at freeze.** It claims a
replication in an order-flow market, which is exactly what panel 1 is and exactly
what panels 2 to 6 are not. The wording says "the mechanism reproduces" and names
the amplification, so it claims no more than `[MEASURED]` licenses. Any rewrite
that widens it to the substitution frontier or the herd-immunity threshold is
overclaiming and must be rejected.

**Rejected openings.** Anything beginning with the field ("Machine learning
systems increasingly...") or with the venue's vocabulary ("Algorithmic
monoculture has emerged as..."). The first sentence is the paper's claim, and it
is the sentence a reviewer decides on.

**Title check.** "Herd Immunity and Learning Externalities in Markets of Shared
Foundation Models" (v6) pairs the memorable law with the economic mechanism that
produces it, and "externalities" is the word an EconML reviewer scans for. The
v6 title names the mechanism the paper is actually about, shared models rather
than firm count, and names it as the setting rather than as a scope restriction:
Theorem 1 holds for any alignment matrix `R`, and the supply chain is one of its
four anchors. "Markets" is kept because it is the venue's own word and the body's
(41 uses). Effective crowding is left to the abstract rather than carried in the
title, since it is the object that makes the law computable rather than the
reason a reviewer stops to read.
