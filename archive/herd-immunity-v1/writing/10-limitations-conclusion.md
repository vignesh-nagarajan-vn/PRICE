# 10. Limitations and conclusion

**Status: drafted.** Target 0.60 pages.

---

## Limitations

Stated in the paper's own voice, before a reviewer states them. Each is a
standing assumption with its consequence made explicit rather than a hedge.

**The analysis is linearized** around the joint equilibrium, and the simulator is
the nonlinear check on it. Result 1's amplification anchor shows what that costs:
the measured market departs from the linear prediction by `-12.9%` at `N = 2` and
`+5.2%` at `N = 3`, with opposite signs, which is the shape of the approximation
error rather than a failure of it. [MEASURED]

**The heterogeneous sweep is closed-form agreement, not measurement.** This is
the build's largest gap and it is stated first among the empirical limitations.
A heterogeneous-response port of the order-flow simulator was designed, built and
shown exact at flat exposure profiles, reproducing the unmodified market at every
`N` from 1 to 6. Its gate then failed: the simulator's liquidity and price-impact
channels remain shared whatever the response profiles are, leaving a `17.7` point
residual across the separation range at `N = 2`, and at `N >= 4` the
finite-difference probe stops measuring a local slope. Panels 2 to 5 therefore
establish that the closed forms govern realized dynamics in a reference
environment that has no informed flow, no spread and no inventory, and they
establish nothing about a real market. [DRY RUN] Only Result 1's amplification
anchor is measured in one. Routing the liquidity and impact channels through the
response profiles is the identified repair and it is future work. Result 4's
panel is a dry run for a separate reason: the order-flow simulator carries no
aggressiveness choice variable and no welfare object, so no measured counterpart
of it exists to be built. [DRY RUN]

**Theorem 1 is exact for equal moduli.** The heterogeneous-modulus case is a
two-sided bound whose tightness is measured rather than asserted. [VERIFIED]
Share-weighted alignment for unequal-sized firms and the fully heterogeneous
block-secular reduction are named extensions, not results. [DEFERRED] The sharp
operator-norm concentration rate is measured and not proved; the crude bound is
what the paper uses. [DEFERRED]

**The herd-immunity collapse assumes the monoculture corner.** The `1 - 1/R_0`
form holds at `kappa = s = 1`, which is the homogeneous-mixing assumption its
epidemiological counterpart also makes, and away from that corner the criterion
is the exact two-block root. The strong-correction limit errs **optimistic**, and
the paper reports the direction alongside the limit rather than in a caveat.
[VERIFIED] Three or more correction levels, and correction that moves a firm's
response direction rather than only its gain, are named and not attempted.
[DEFERRED]

**Deployment is synchronous with a common cadence.** Heterogeneous retraining
clocks across firms break the eigenvector sharing Theorem 2's composition uses,
and are named as an extension rather than absorbed. [DEFERRED]

**Theorem 4 prices instability through stationary variance**, a modeling choice
defended in Section 7 as the smooth proxy for divergence risk. Nothing in the
result uses more than that the cost is positive, increasing and convex.

**The cadence lever buys stability with model staleness**, and the exchange rate
is quantified in Section 5 rather than presented as free.

**Neither `R` nor `s` is observable to an outsider.** Section 8 is the designed
answer, and its real-data leg is consistency evidence with a placebo, never
identification of monoculture: co-movement is macro-contaminated and the data is
public proxies, not trade-level records. [DEFERRED]

## Conclusion

**Individual model evaluation cannot certify a market of models.** The quantity
that separates the two questions is the effective number of independent learners,
a spectral property of how firms' response directions align, and no evaluation of
a single model can see it. A firm can pass every stability test available to it
and still be one of the reasons its market fails, without doing anything wrong
and without observing the firms it is coupled to.

What follows for policy is concrete rather than hortatory. A regulator already
drafting systemic-risk obligations for shared general-purpose models has a
threshold on model scale but no mechanism connecting model sharing to a
measurable systemic quantity. This paper supplies one, and with it two
substitutable instruments and a price: move less per round, share fewer models or
correct more of them, or pay for the crowding. The substitution frontier is the
object a regulator would act on, because it says the instruments are
interchangeable at a computable rate rather than merely available.

---

## Anonymization checklist

Run before freeze, as a separate pass, against the built PDF rather than the
source.

**Identity in the artifact:**

- [ ] No author block
- [ ] No repository URL anywhere, including figure paths and captions
- [ ] PDF metadata scrubbed (author, title, producer, creation host)
- [ ] Figure files carry no local paths in their embedded metadata
- [ ] **Result files carry absolute local paths.** `panel1_external_anchor.json`
      records a checkout path containing a username. Scrub at release rather
      than in place, since the file is a run record. Found 19 Aug 2026

**Identity in the prose:**

- [ ] Simulator described generically with an anonymized-artifact promise
- [x] REFLEX and PEBSA cited as ordinary third-party references, authors
      included. Verified against Crossref and the arXiv API, 19 Aug 2026. The
      shared author name is deliberate: an author-less entry is the more
      revealing artifact
- [ ] **No sentence positions either as the authors' own work.** No "our earlier
      framework", no "we previously showed", no "building on our REFLEX".
      Grep the source for "our" and check each hit
- [ ] Acknowledgments section absent or anonymized

## Checklist

- [x] Every limitation carries its consequence, not just its name
- [x] The port gate stated as the first empirical limitation, since it is the
      largest gap and a reader should not have to infer it
- [x] Deferred items named where the reader meets them, and listed here with
      their flags: 4.11, 4.14, 5.10, 6.14
- [x] No future-work list beyond the deferrals, and no summary paragraph
- [x] The certification claim restated once, as the thing to take away
- [ ] Confirm at assembly whether the EU AI Act's general-purpose-model article
      numbers verify. **Dropped from the draft above** rather than cited
      unverified; restore only if the numbers check

## Notes for the writing pass

**Length.** About 640 words, at the 0.60-page target. This section does not
absorb overflow from elsewhere, since every paragraph is a limitation a reviewer
would otherwise raise.

**What changed against the plan of record.** The plan lists limitations that
assume the empirical program landed in full. It did not, so the heterogeneous
sweep's status is a limitation here that the plan does not contain, and it is
placed first among the empirical ones. The plan also proposes citing the EU AI
Act by article number; the numbers are not verified in this build, so the
conclusion makes the same point without them and the citation is a checklist item
rather than a claim.

**The one thing a referee will probe.** Whether the empirical section supports
the paper's ambitions. The honest answer is that one panel is measured and five
are dry runs, that the paper says so in the coverage table, in every inline flag
and here, and that the theory is certified independently of all six. A reviewer
who discounts the dry runs entirely still has four proved results and one
external replication.
