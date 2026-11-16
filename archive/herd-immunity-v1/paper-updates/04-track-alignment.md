# EconML @ NeurIPS 2026 track alignment

## 1. The tracks, as verified

The workshop site (econml26-workshop.github.io) is egress-blocked from
this environment, so its wording was reconstructed from three
independent search reads of the site plus the NeurIPS 2026 workshop
announcement and the OpenReview group page; all three agree (log entries
V1-V3). Verified wording:

- The workshop "brings together researchers from machine learning,
  economics, game theory, and related fields to map the economic
  consequences of ML's growing success, anticipate emerging risks, and
  develop economic interventions that support long-term sustainability
  and benefit," and "bridges micro-scale mechanism design and
  market-level analysis."
- **Direction 1, Economic Tools for Machine Learning**: "how can
  economic ideas improve learning and alignment, reveal the limitations
  of existing algorithms and paradigms, and align incentives in local
  interactions around AI systems."
- **Direction 2, Machine Learning Ecosystems with Interacting Models**:
  "what economic phenomena emerge when many models interact in shared
  environments, and how interventions can improve ecosystem-level
  outcomes."
- Submissions welcomed include motivating "an emerging topic, problem
  or direction, with clearly articulated motivation and a rigorous
  formal model," and work on "solutions made possible by, or risks
  arising from, the unique properties of machine learning models and AI
  systems."
- Logistics: Atlanta, Dec 12 or 13; long (9 content pages) and short
  (4) formats; deadline 29 Aug AoE; decisions Sept 29; in-person.

Before submitting, load the site once from an unblocked machine and
diff against this section; that residual check is flagged in the log
(V1) and takes five minutes.

## 2. Element-by-element alignment map

| Paper element (post-upgrade) | Direction 2 (primary) | Direction 1 (secondary) |
|---|---|---|
| Learning externality + m_N | the emergent economic phenomenon, named | - |
| Effective number of independent learners; measured lambda_max on deployed models (Panel 7) | "many models interact in shared environments," made literal and measured | - |
| Cadence caps, correction mandates, diversity floors, the wedge | "interventions [to] improve ecosystem-level outcomes," one per instrument | wedge and mandate as incentive alignment |
| Herd immunity / imperfect-vaccine law | ecosystem-level intervention with a coverage threshold | correction as an economic mechanism that improves learning |
| "Single-agent evaluation cannot certify a market of models" | - | "reveal the limitations of existing algorithms and paradigms," near-verbatim; say it in these words once |
| Free-riding / public-good structure of correction and diversity | - | "align incentives in local interactions around AI systems" |
| Supply-chain term; provenance channel | risk arising from a unique property of ML (shared foundation models) | - |
| Reduction lemma + assumption discipline | the call's "rigorous formal model" ask | - |
| Lean 4 layer | - | strengthens the "rigorous formal model" credential; venue-neutral |
| Statistics layer (nulls, CIs) | makes the Direction-2 evidence inferential rather than illustrative | - |

## 3. The concrete alignment edits (all outlined in 01-section-outlines.md)

1. The word "ecosystem" enters the abstract (once), the introduction
   (once), Panel 7's row caption, and the conclusion (once). Currently
   it appears zero times; keyword triage is real at eighty-submission
   workshops.
2. The paradigm-limitation sentence is voiced once in Direction-1
   vocabulary (Section 1 or 3, not both).
3. The correction mandate gets its one-clause Direction-1 reading
   (Section 6).
4. The introduction's ML-native instantiation (recommender platforms on
   one foundation model) makes the "interacting models" reading
   available to a reader who never trades bonds.
5. The practitioner sentence in Section 5 gives the "local interactions"
   audience a takeaway that is theirs, not a regulator's.
6. Nothing is re-tracked: the paper remains a Direction-2 submission
   with legible Direction-1 hooks; do not split the difference harder
   than that, and do not relabel sections by track.

## 4. Anti-goals

- No chasing the mechanism-design half of the call: the paper has no
  auction or matching content and pretending otherwise would read as
  fit-stuffing.
- No "alignment" (AI-safety sense) claims; the workshop's word
  "alignment" in Direction 1 is about incentives and learning, and the
  correction mandate's clause should stay in that register.
- The two-format choice stays long-paper; the results density cannot
  survive 4 pages.
