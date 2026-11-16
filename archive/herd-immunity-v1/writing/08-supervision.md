# 8. Supervision from public prices

**Status: drafted, and first in the de-scope order.** Target 0.20 pages, which is
one paragraph. Source: [`../math/05-supervision.md`](../math/05-supervision.md).

Drafted at one paragraph rather than written long and trimmed, then collapsed
further to the two-sentence form on 19 Aug 2026 when step one of the compression
order did not close the page budget. A section that is first to go should not be
carrying material anyone would have to rescue out of it.

---

Every quantity in Sections 4 through 7 is hidden from the regulator those
sections address, and near the boundary the system tells on itself: as `m_N`
approaches one the leading principal component of public quotes has lag-1
autocorrelation approaching one in magnitude, with the sign negative because
Result 4's common mode oscillates rather than persists, and variance share
growing like `1/(1 - m_N)`, so a supervisor can estimate distance to instability
from public prices alone with no access to any firm's model, data, or code. The
estimator sharpens exactly as the market approaches the boundary it watches for,
and its consistency proof, central limit theorem and detection sample complexity
are journal deliverables. [DEFERRED]

<!-- APPENDIX or cut, page-budget step 2, 19 Aug 2026. The paragraph above is
     already the two-sentence form the compression order calls for. What it
     replaced ran to about 200 words and read as follows, and it is the version
     to restore if the budget stops binding.

Every quantity in Sections 4 through 7 is hidden from the regulator those
sections address: no outsider observes a firm's response Jacobian, and `R` and
`s` are not filings. Near the boundary the system tells on itself. As `m_N`
approaches one the aligned combination of firms' decisions exhibits critical
slowing down, so the leading principal component of public quotes has lag-1
autocorrelation approaching one in magnitude and variance share growing like
`1/(1 - m_N)`, which lets a supervisor estimate distance to instability from
public prices alone, with no access to any firm's model, data, or code, and with
an estimator that sharpens exactly as the market approaches the boundary it is
watching for. The sign is the part a practitioner has to get right: Result 4's
common mode has autocorrelation `-m_N`, so the diagnostic is oscillatory
co-movement rather than persistent co-movement, and a monitor watching for
persistence would look for exactly the wrong thing.
-->

---

## Appendix panel

PC1 variance share and lag-1 autocorrelation of cross-sectional spread
co-movement on the 212-CUSIP panel, 1990 to 2026, overlaid on the model-implied
fragility index, **with a placebo** on Treasury and macro series where no
dealer-model channel exists.

**Framed as consistency evidence, never identification.** Co-movement is
macro-contaminated and the data is public proxies, not trade-level TRACE. The
claim is only that the observable the theory says should move, moves. Any
stronger phrasing is indefensible and an empirical-finance reviewer will say so.

## PEBSA

Cited once, for the contrast, in Section 2 rather than here so that cutting this
section does not orphan the reference. PEBSA's measurement channel is exogenous:
sentiment is a signal about an economy the observer stands outside of, and the
accuracy of the inference does not depend on the economy's own dynamics. The
observable here is endogenous, since the prices a supervisor reads are generated
by the very agents being monitored, so the measurement channel is part of the
system and the signal strengthens as the system nears instability. The value is
the contrast, not a shared method, and one sentence is the whole of it.

## Cut protocol

If this section goes, the paragraph above goes whole and nothing else moves. The
PEBSA sentence already lives in Section 2, the appendix panel stays in the
appendix, and no result in Sections 4 through 7 refers back to this one. That
independence is the reason it is placed last among the results and is what makes
it genuinely cuttable rather than nominally so.

## Checklist

- [x] One paragraph, not two
- [x] Written at cut length rather than trimmed to it
- [x] Consistency claim stated, proof deferred explicitly, flagged `[DEFERRED]`
- [x] The negative-autocorrelation sign carried over from Result 4, since it is
      what a practitioner would otherwise get backwards
- [x] PEBSA moved to Section 2 so the cut leaves nothing orphaned
- [ ] Placebo run and reported whatever it shows
- [ ] "Consistency evidence, not identification" in the appendix text

## Notes for the writing pass

**Length.** Drafted at about 200 words, then collapsed to two sentences on
19 Aug 2026 under step two of the compression order, since step one did not close
the budget. The body paragraph is now about 110 words. The longer version is
preserved in a comment in this file rather than deleted, so restoring it is a
revert rather than a rewrite.

**What changed against the plan of record.** The plan puts the PEBSA sentence
here or in related work and leaves the choice open. It is settled here in favour
of Section 2, because leaving it open means deciding it during the writing week,
which the plan itself warns against.
