# EconML @ NeurIPS 2026 (P2)

## "Herd Immunity and Learning Externalities in Markets of Adaptive Models"

| | |
|---|---|
| **Venue** | EconML workshop @ NeurIPS 2026, Atlanta, Dec 12/13 |
| **Deadline** | **Aug 29, 2026** |
| **Format** | Long paper: 9 pages main body, unlimited references and appendix |
| **Review** | Double-blind. In-person presentation required |
| **Base paper** | REFLEX, arXiv:2608.16155 (public at submission; cited in third person) |
| **Plan of record** | [`../finalized-ideas/econml paper idea`](../finalized-ideas/econml%20paper%20idea) |

The finalized plan is the specification. This folder is the build against it.
Where a file here disagrees with the plan, the file states the disagreement
explicitly and the claims ledger records which one is right.

---

## Thesis in three sentences

An individual learning agent can pass every stability test we know how to run
and still help destabilize the market it operates in, because each agent's
retraining reshapes the data every other agent will learn from next. The
strength of that **learning externality** is set not by the number of firms but
by the firms' **effective crowding**, a spectral measure of how aligned their
feedback directions are, counting firms per independent model, so foundation-model concentration
enters the stability condition as a term rather than as a talking point. Three
closed-form levers follow, and the last two trade off against each other:
model diversity and corrected learning are substitutes, and the paper gives the
frontier along which a market can buy stability with either.

## The four results

| # | Result | Object | Status |
|---|---|---|---|
| 1 | Effective crowding (firms per independent model) | `N_eff = 1 + kappa(lambda_max(R) - 1)`; supply chain `N_eff = 1 + kappa*s*(N-1)` | anchors verified, identity derived |
| 2 | Crowding-cadence frontier | `K_max = ln((m_N-1)/(m_N+1)) / ln c`; critical crowding `(1+c)/(1-c)` | derived, arithmetic checked |
| 3 | Herd immunity and the substitution frontier | `rho*(s) = max(0, 1 - N_c(s)/N)`, collapsing to `1 - 1/m_N` | derived, limit case checked |
| 4 | Pigouvian wedge | `t*` from stationary variance `1/(1-m_N^2)`; over-adaptation corollary | proved and certified |

Everything reduces to one substitution: `m_N = N_eff * m_1`, with `N_eff` set by
model alignment rather than by headcount. Results 2 through 4 are all stated in
`m_N`, so each inherits the supply-chain parameter `s` for free.

## Directory map

| Path | Holds |
|---|---|
| [`STATUS.md`](STATUS.md) | **Where the build is: done, not done, risks, suggested order. Read this first** |
| [`literature/`](literature/) | The literature review, cluster by cluster, with gaps, novelty verdict and verification debt |
| [`math/`](math/) | Notation, standing assumptions, one note per theorem, and the complete proofs under `derivations/` |
| [`ml-contributions/`](ml-contributions/) | The theory module, the response environment, the panel harness, specs and certificates |
| [`writing/`](writing/) | Section-by-section paper content, page budget, claims ledger |
| [`paper/`](paper/) | **The submission.** `main.tex`, the NeurIPS checklist, the official style file, and the compiled `main.pdf` |
| [`paper/README.md`](paper/README.md) | **Read before touching the paper.** Build commands, compliance rules, the version history, and the two review items that must not be acted on |

## Status board

| Piece | State |
|---|---|
| Literature review | **complete** (`literature/LITERATURE-REVIEW-P2.md`) |
| Introduction | **complete** (`writing/01-introduction.md`) |
| Abstract | **rewritten** around the imperfect-correction law, closing on panel 1 |
| Theorem 1 | **proved and certified** (`math/derivations/01`, `02`); 123 checks |
| Theorem 2 | **proved and certified** (`math/derivations/03`); 59 checks |
| Theorem 3 | **proved and certified** (`math/derivations/04`); 70 checks. **C18 failed and changed the claim** |
| Theorem 4 | **proved and certified** (`math/04-theorem4-wedge.md`); 125 checks |
| Section 4, Result 1 | **drafted** (`writing/04`) |
| Section 5, Result 2 | **drafted** (`writing/05`) |
| Section 6, Result 3 | **drafted** around the exact root (`writing/06`) |
| Theory module | **written and certified** (`ml-contributions/theory/`); 56 checks |
| Heterogeneous-response environment | **built and certified** (`ml-contributions/environment/`); 32 checks |
| Panel harness | **built** (`ml-contributions/experiments/`); panels 1-6 run |
| Panel 1 anchor | **`[MEASURED]`** in the real order-flow market, reproducing `1.74x / 3.16x` bit for bit |
| Panels 2-5 | **dry runs pass**, all agreeing with their closed forms. Not measurements |
| Heterogeneous-response port | **exact at the reduction, step-3 gate failed, workstream closed.** Panels 2-5 stay `[DRY RUN]` |
| Panel 6 | **dry run passes**, 12 configurations, zero contradictions of the over-adaptation corollary |
| Sections 7 to 10 | **drafted** |
| Page budget | closed **in LaTeX**, at nine content pages. The markdown build folder still holds more than nine pages; `paper/README.md` records what was cut |
| Statistical layer | **added in v5**. The one random-ensemble fraction carries its sampling measure, its n, its exact count and a Clopper-Pearson interval (`verify_ensemble_intervals.py`, Appendix K); deterministic grid checks keep worst-case-departure language. Checklist Q7 flips to yes |
| Submission | **v5**, 27 Aug 2026. Citation gap closed, wedge scope corrected, notation unified, track vocabulary in, narrative repairs applied. See `paper/README.md` |
| Submission PDF | **compiles clean**, 9 content pages, references and checklist after |
| NeurIPS checklist | **all 16 answered**, instruction block stripped, heading kept |
| Review of v1 | **back, accept as poster.** Three items would move it: derive the reduction in the body, dispatch Narang et al., measure `s` on real models. See `paper/README.md` |
| Paper v2 | **built.** Reduction lemma and Narang containment are in the body, the smaller items landed, measuring `s` is out. Nine sections, nine content pages, clean three-pass build |
| Paper v3 | **built 20 Aug 2026.** Abstract qualifies the herd-immunity law to the fully shared limit; panel 1 is no longer called external validation in the caption, Appendix I or the checklist; Peng and Garg (2024) and Jagadeesan et al. (2023) added; `\workshoptitle` matches the call. The anchors table paid for the space. No status flag moved, zero overfull boxes |
| Paper v4 | **built 20 Aug 2026** against an external review of v3. Cadence terminology matches what the theorem proves; the Narang containment is Proposition 3 with an explicit witness pair; the wedge's exchangeable-symmetric scope is stated in the body; (H3) is motivated with a concrete market; the base paper is a preprint, not published. Two review items rejected on evidence. Nine content pages, page 9 full. v1 to v3 archived in `paper/archive/` |
| Appendix | **typeset, in the submission PDF.** Ten appendices: complete proofs of every numbered result, the certificate inventory, the experimental protocol and the deferred register. 31 pages total, content still ending on page 9 |

Theorems 1 through 4 have moved from `[DERIVED]` to `[VERIFIED]` in the claims
ledger, each against assertion-based certificates that fail loudly. 542 assertions
across eight files, all passing.

**One claim failed, and it was the one the ledger flagged in advance.** The
strong-correction limit in Theorem 3 is optimistic rather than conservative, so it
can call a market stable that is unstable at finite correction strength. The exact
two-block root is now the theorem, the limit is a corollary that states its own
error direction, and the exact root has left the de-scope order. What replaced the
clean law is larger than the clean law: the exact threshold is the epidemiological
imperfect-vaccine coverage requirement, and it carries a critical efficacy below
which correction stops working at all.

Three open items closed along the way: supply-chain concentration now carries a
probability bound rather than holding in expectation, the invariance of the inner
contraction `c` to firm count is measured rather than argued, and the realized
herd-immunity threshold in whole firms has a formula that is right at the corner
where the obvious one is off by one.

## Conventions

**Status flags**, used everywhere and meaning the same thing each time:

- `[VERIFIED]` follows from certified base results, or already checked numerically
- `[DERIVED]` worked out for this paper, derivation recorded, low proof risk
- `[TO BUILD]` new experiment or configuration
- `[DEFERRED]` stated in the body, completed for the journal version

**Double-blind rules.** No author block, no repository URL anywhere, scrubbed
PDF metadata and figure paths, simulator described generically with an
anonymized-artifact promise. REFLEX and PEBSA are both public at submission time
and are cited as ordinary third-party references. The only rule to enforce is
that no sentence positions either as the authors' own work: no "our earlier
framework", no "we previously showed", no "building on our REFLEX".

**Section and theorem numbering.** This folder, `STATUS.md` and the claims
ledger number the four results Theorem 1 to 4 and follow the eleven markdown
drafts in `writing/`. The built paper folds supervision into the closing section,
so it runs nine sections and numbers the same four results Theorem 2, 4, 5 and 8,
after Lemma 1 and Proposition 3. Status flags match across both; only the labels differ.

**Notation.** ASCII math in all markdown here, matching the plan of record.
LaTeX happens once, at the end, from these files. Nothing in this folder is
LaTeX.

**Prose.** No em dashes. House style is enforced by `prose-guard`.

## De-scope order

Fixed in advance so the decision is not made under deadline pressure. In order:
supervision from public prices (already scoped to one paragraph), then
experiment 6, then the free-riding diagnostic, then the clustered companion in
experiment 2.

**Never cut:** experiment 1's anchor, experiment 4, experiment 5, the exact
two-block root, or the private-versus-systemic framing, which is the paper's
reason to exist at this venue.

The exact two-block root was third in this order until 18 Aug 2026. It came out
once the strong-correction limit was shown to err in the unsafe direction: the
exact root is what makes the stability criterion honest, not a refinement of it.

The heterogeneous-response port is not in this order. It was infrastructure that
would have upgraded experiments 2, 2b, 4 and 5 to `[MEASURED]`; its step-3 gate
failed on 18 Aug 2026 and the workstream was closed on 19 Aug 2026 without
attempting either named repair. Those panels ship at the `[DRY RUN]` status they
already held, so nothing is cut and no claim is weakened.
