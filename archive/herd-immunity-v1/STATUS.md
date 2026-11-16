# Status: EconML @ NeurIPS 2026

**As of 27 Aug 2026. Submission 29 Aug 2026, two days out.**

> **v5 landed 27 Aug 2026.** The body of this file still describes the state at
> 20 Aug and is accurate about the theory, the panels and the port. What changed
> since is the paper, in five passes recorded in
> [`paper/README.md`](paper/README.md): the citation gap closed, the wedge's
> orthogonal-corner scope slip corrected and the notation unified to `rho_c`, an
> exact interval put on the one random-ensemble number with a new certificate
> and a new Appendix K, the workshop's two directions spoken once each with the
> wedge figure moved beside Result 4, and the dry-run framing reworded from
> "establishes nothing about a market" to internal against external validity.
> Certificates went from 525 to 542, all passing. Checklist Q7 flipped from no
> to yes. No status flag moved and no claim was cut.
>
> **What remains, and it is not editorial.** The measured-alignment panel, which
> would put `lambda_max` on real deployed models, is not built. Both the v1
> external review and the 25 Aug internal review named it as the single item
> that moves this from poster to oral, and it is gated on a data check nobody
> has run: whether the Kim et al. (ICML 2025) release has per-item granularity
> and a usable licence, with HELM per-instance outputs as the named fallback.
> The Lean 4 layer is also not attempted and no paper text mentions it. Both
> were scoped for a four-day window in `paper-updates/` and this pass had
> two days; if the panel does not land by 28 Aug it moves to camera-ready with
> its protocol already written.

Paper: "Herd Immunity and Learning Externalities in Markets of Adaptive Models".
9 pages main body, unlimited appendix, double-blind, in-person.

---

## One-paragraph summary

The theory is done and certified: all four results have complete proofs,
Theorem 4's welfare page having landed on 18 Aug 2026. The infrastructure is
done: the closed-form module and the heterogeneous-response environment both
exist and pass acceptance tests. Five of six panels have run as dry runs against
the reference environment and agree with the closed forms, and **panel 1's anchor
is measured in the real order-flow market, reproducing the published run bit for
bit**. **The heterogeneous-response port is closed as a realized fallback**: it
is exact at the reduction, its step-3 gate failed, neither named repair is
attempted, and panels 2, 2b, 4 and 5 ship at `[DRY RUN]`. What remains is
editorial plus one panel: four sections to draft, the abstract to rewrite, and
panel 6 to build.

## Where the time went, and what it bought

The build found one result that changed the paper. Theorem 3's strong-correction
limit is **optimistic, not conservative**: it under-states the spectral radius and
calls roughly one configuration in eight stable when it is not. That was caught
because the claims ledger flagged it in advance as the claim whose failure would
matter most, and it was checked before the section was written rather than after.

The repair is larger than the damage. The exact threshold is the epidemiological
**imperfect-vaccine coverage law**, and it carries a **critical efficacy** below
which correction stops working at any coverage. So the `R_0` correspondence now
transfers a refinement of the law rather than just the law, which is much stronger
evidence it is structural. The exact two-block root left the de-scope order as a
consequence.

---

## Done

### Theory, all proved and certified

| Theorem | Proof | Certificate |
|---|---|---|
| 1, effective crowding, firms per independent model | `math/derivations/01`, `02` | 123 checks |
| 2, crowding-cadence frontier | `math/derivations/03` | 59 checks |
| 3, mixed market and herd immunity | `math/derivations/04` | 70 checks |
| 4, Pigouvian wedge | `math/04-theorem4-wedge.md` | 125 checks |

542 assertions across eight assertion-based files, all passing:

```bash
for f in econml/ml-contributions/certificates/verify_*.py; do python "$f" || break; done
```

### Results the build added beyond the plan of record

The reduction lemma, deriving the joint Jacobian from response Jacobians instead
of asserting the substitution. `N_eff >= 1`, so interaction never stabilizes a
market below what its members achieve alone. The mean-alignment index proved to
be a lower bound with a signed error, so it under-states risk and never
over-states it, which replaces two counterexamples with one theorem. The exact
two-block root. The imperfect-correction law and its critical efficacy. A
supply-chain concentration bound that holds with probability rather than in
expectation.

### Infrastructure

| Piece | State |
|---|---|
| Theory module, `ml-contributions/theory/` | All four theorems complete, 56 acceptance checks. `pigouvian_wedge` joined on 19 Aug 2026 with panel 6 |
| Heterogeneous-response environment, `ml-contributions/environment/` | 32 acceptance checks, reduction verified |
| Panel harness, `ml-contributions/experiments/` | panels 1 to 6, exits nonzero on disagreement |
| Simulator port, `experiments/hetero_simulator_port.py` | **exact at the reduction; step-3 gate failed and the workstream is closed.** No panel imports it |

### Panels, as dry runs only

| Panel | Outcome |
|---|---|
| 1, amplification | reduction exact to `5.6e-16`; **external anchor closed, `[MEASURED]`** |
| 2, `(N, s)` phase diagram | 48 cells, max error `7.1e-15` |
| 2b, clustered companion | measured `m_N` `1.30`, mean index reports `0.74` |
| 3, cadence frontier | 175 cells, zero disagreements |
| 4, herd immunity | `12 / 14 / 16 / 20` firms at efficacy `1.00 / 0.90 / 0.75 / 0.60` |
| 5, substitution frontier | 18 of 18 points exact |
| 6, over-adaptation | 12 configurations, zero contradictions of Corollary 4.2, smallest gap `0.290` |

**Panels 2 to 6 are not measurements.** They run in the linearized reference
environment, which has no informed flow, no spread and no inventory. They
establish that the closed forms govern realized dynamics and they fix every
figure's shape. They establish nothing about a market. The ledger tracks them at
`[DRY RUN]`, a status that deliberately does not license the paper to imply
measurement.

### Panel 1's external anchor, the one measured result

`ml-contributions/experiments/reflex_anchor.py` runs the base project's genuine
shared-pool market and **reproduces the published run bit for bit**, relative
error `0.00e+00`:

| `N` | measured `m_N` | amplification | linear prediction | gap |
|---|---|---|---|---|
| 1 | `0.785600` | `1.0000` | `1` | |
| 2 | `1.369162` | `1.7428` | `2` | `-12.9%` |
| 3 | `2.479927` | `3.1567` | `3` | `+5.2%` |

Differential mode `3.4e-03` against a theoretical `0`, so instability is purely
common-mode, which is the mechanism Theorem 1 generalizes.

This one panel could be closed today because its claim is the monoculture corner
`R = 1 1'`, which the base project already implements. The base project is
read-only throughout and the script skips cleanly when it is absent.

**The gap to the linear prediction is content, not error**, and the body should
say so: the prediction is a linearization and the market is nonlinear with
saturating flow. Note the two gaps have **opposite signs**, `-12.9%` at `N = 2`
and `+5.2%` at `N = 3`. An earlier version of the ledger called both a
shortfall; corrected 18 Aug 2026. A two-signed departure is what a nonlinear
market does around a linearization, and it is a better argument for the
reference environment than a one-signed one would be. The reference environment reproduces the prediction exactly
because it omits both, which is the clearest available argument for why the
remaining panels need the simulator.

### Writing

**All eleven sections are drafted as of 19 Aug 2026.** Word counts are body
prose, excluding display math, tables and the per-file notes. These are the
markdown working drafts; v2 of the paper folds section 8 into section 10, so the
built PDF carries nine sections and this table's numbering is the drafts', not
the submission's.

| Section | State | Body words | Measured pages |
|---|---|---|---|
| 0, abstract | **rewritten** around the imperfect-correction law, closing on panel 1 | 223 | 0.21 |
| 1, introduction | complete | 1195 | 1.17 |
| 2, related work | drafted, plus PEBSA's contrast sentence moved in from Section 8 | 1271 | 1.21 |
| 3, model and framing | drafted | 1242 | 1.21 |
| 4, Result 1 | drafted, proof moved to the appendix | 849 | 1.19 |
| 5, Result 2 | drafted, proof moved to the appendix | 488 | 0.82 |
| 6, Result 3 | drafted around the exact root | 1037 | 1.60 |
| 7, Result 4 | **drafted**, compression steps 1 and 3 applied | 888 | 1.14 |
| 8, supervision | **drafted**, collapsed to two sentences under step 2 | 113 | 0.11 |
| 9, experiments | **drafted**, with a per-panel status column | 951 | 1.07 |
| 10, limitations and conclusion | **drafted** | 725 | 0.69 |
| | | | **10.41** |

**The page budget closed in LaTeX rather than in markdown.** The compression
order recovered only `0.27` of a page against a `1.41` overage, so the fit was
made during the LaTeX pass instead: proof bodies to the appendix, the worked
tables in Sections 5 and 6 reduced to inline numbers, and the clustered
companion folded into a table row. The markdown files above are the working
drafts and still exceed nine pages; `paper/main.tex` is the submission and does
not. `paper/README.md` records every cut and why.

---

## Not done

### Blocking, in priority order

**1. ~~The simulator port.~~ Closed 19 Aug 2026, as a realized fallback.** Panel
1 is measured because its claim is the monoculture corner the base project
already implements. Panels 2, 2b, 4 and 5 are not, and the reason is structural:
the base project's `env/multi_dealer.py` has **no concept of a per-dealer
response direction**. Every dealer shares one scalar toxic channel
`exp(-c_t*h_i)` coupled by a single scalar `kappa`, which *is* `R = 1 1'` and
nothing else.

The modeling decision was made and recorded in
`ml-contributions/environment/HETERO-SIMULATOR-PORT-DESIGN.md`: each dealer
carries a bond-space exposure profile, and both its contribution to the informed
pool and its sensing of that pool are routed through it, so the coupling matrix
becomes `(1-kappa)I + kappa R` with `R` the Gram matrix of the profiles. The
port implements it and **is exact**: at flat profiles it reproduces the
unmodified base simulator at every `N` from 1 to 6, relative error `0.00e+00`.

**The step-3 gate then ran, and it did not open.** The still-shared liquidity
and price-impact channels leave a `17.7` point residual across the separation
range at `N = 2`, and at `N >= 4` the finite-difference probe is not measuring a
local slope at all. The design document names two repairs, routing liquidity and
impact through the profiles as well, or finding a configuration whose probe
stays local at the `N` the panels need. **Neither is attempted and neither will
be for this submission.** Both are multi-day edits, the first of them risking
the bit-for-bit anchor that panel 1 rests on, and the panels they would upgrade
are allowed to ship at `[DRY RUN]`. The trade is not worth ten days out.

**Consequence, and it is the planned fallback rather than a surprise.** Panels
2, 2b, 4 and 5 ship at `[DRY RUN]`: closed-form predictions with
reference-environment agreement, stated as such, with no sentence implying
measurement. Panel 1 remains the paper's one measured result. Section 10 states
the gate outcome as a limitation. The port code is left as it stands, exact at
the reduction and unused by any panel, so a journal version can resume from the
design document rather than from scratch.

**2. ~~Theorem 4's welfare page, then panel 6.~~ Both done, 18 and 19 Aug 2026.** The welfare page is
written in `math/04-theorem4-wedge.md`: the AR(1) welfare object with its sign
convention certified, Lemma 11 giving the marginal crowding share
`d m_N/d m_i = N_eff v_i^2`, both first-order conditions, the wedge, its
comparative statics, and over-adaptation for every `N >= 2`. Ledger claims 7.0 to
7.5 are `[VERIFIED]`; `verify_theorem4_wedge.py` passes with 125 assertions.

Panel 6 followed on 19 Aug 2026 and ships at `[DRY RUN]`: 12 configurations,
zero rows contradicting Corollary 4.2, the fee implementing the social optimum
to `1.7e-13`, and the boundary divergence rate fitted at `-2.0000`. It goes no
higher than `[DRY RUN]` and there is no route by which it could: the order-flow
simulator carries no aggressiveness choice variable and no welfare object, so a
`[MEASURED]` version of this panel does not exist to be built. `pigouvian_wedge`
joined the theory module with the panel, and the test that asserted its absence
is replaced by acceptance tests on the function.

**3. ~~Four unwritten sections.~~ Closed 19 Aug 2026.** All eleven sections are
drafted and the abstract is rewritten. What replaced this item is the page
budget: at `10.41` measured pages the body is `1.41` over, the compression order
is exhausted, and the remaining cut is a scope decision rather than an editing
one. It is the only item this session leaves open.

### Known open items, none blocking

The sharp operator-norm concentration rate, deferred to the journal version with
the crude bound proved and the sharp rate measured. Share-weighted alignment and
the fully heterogeneous block-secular reduction, both named and not attempted.
Heterogeneous cadences across firms, which breaks the eigenvector sharing
Theorem 2 uses. Three or more correction levels, which breaks Theorem 3's
two-block collapse.

---

## The submission itself

Built 19 Aug 2026 in [`paper/`](paper/), against the official NeurIPS 2026 style
files and the mandatory paper checklist. The appendix landed 20 Aug 2026, with
v3 and v4 the same day.

**Where the proofs live, and why.** In the submission PDF. The workshop call
defers to the NeurIPS 2026 main track handbook for format, and the handbook puts
paper content, references, appendices and checklist in one PDF while reserving
the separate ZIP for data and code. Appendices do not count against the nine
content pages, and the workshop's own call repeats that. Until 20 Aug 2026 the
appendix was a single paragraph promising proofs as supplementary material,
which left checklist question 3 answering yes to a complete proof on the strength
of material not in the file and depended on an upload slot this venue's call
never mentions.

| Item | State |
|---|---|
| Appendix | **typeset 20 Aug 2026** in `paper/appendix.tex`. Appendices A to F carry complete proofs of Lemma 1 and Theorems 2, 3, 4 and 7 with their corollaries, plus the results stated only there; G is the deferred supervision material, H the certificate inventory, I the experimental protocol, J the deferred register. 31 pages total |
| Format | `dblblindworkshop` track, style file unmodified, `final` and `preprint` both omitted so the build anonymizes itself and carries line numbers |
| Page count | **nine content pages, and page 9 is full.** References, appendix pointer and checklist start on page 10 and do not count |
| Checklist | **all 16 questions answered** with justifications. Two deliberate `no` answers: code access, withheld to preserve the blind, and error bars, since the panels are deterministic and worst-case grid departure is reported instead |
| Double-blind | no author block, no repository URL, empty PDF metadata, figures generated from result JSONs with no local paths. The two base papers are cited in full **with authors**, which is third-person self-citation as the plan of record requires, not a leak |
| Figures | five, vector, regenerated by `paper/make_figures.py` from the committed result files so they cannot drift from the runs |

**The artifact URL is deliberately absent.** `github.com/vignesh-nagarajan-vn/PRICE`
names an author, so putting it in a double-blind submission would break
anonymity. The line sits commented in `main.tex` for the camera-ready, the live
sentence promises anonymized supplementary material to reviewers, and the
checklist's question 5 states the same arrangement.

**v1 was reviewed externally on 19 Aug 2026 and the version history is in
[`paper/README.md`](paper/README.md).** The verdict is accept
as poster, around 70% as submitted, high 80s if three things land: derive the
joint Jacobian in the body rather than the appendix, state the containment
relation against Narang et al. (2023), and measure the shared-model fraction `s`
once on real models. **v2 is built**: the reduction lemma and the Narang
containment are in the body, the smaller items landed, and measuring `s` was
ruled out for lack of infrastructure and page budget. **v3 followed on 20 Aug
2026**: the abstract's herd-immunity law now carries its fully-shared-limit
qualifier, panel 1 is no longer described as external validation anywhere, two
references from this workshop's own community were added, and `\workshoptitle`
matches the call exactly. The anchors table paid for the space. No status flag
moved. **v4 followed the same day**, against an external review of v3: the
cadence terminology now matches what Theorem 4 proves, the containment against
Narang et al. is a numbered proposition with an explicit witness pair, the
wedge's exchangeable-symmetric scope is stated in the body, hypothesis (H3) is
motivated with a concrete market, and the base paper is called a preprint rather
than published. Two of that review's items were rejected on evidence, both
recorded in `paper/README.md`. v1, v2 and v3 are frozen side by side
in `paper/archive/`, v1 at commit `486d213`. The paper is **nine sections**, since
supervision folded into the closing section, and the body's four results are
numbered Theorem 2, 4, 5 and 8 there against Theorem 1 to 4 in this file and the
ledger, Proposition 3 having entered the sequence in v4.
Two of the review's criticisms were checked against the code and hold (`N_eff`
cancels in the wedge's ignored fraction, and (A5) is not needed for Theorem 1's
radius); one is a misreading and **must not be acted on**, since the submission
footer is already correct and changing it means editing the style file.

**Venue checked against the call for papers, 19 Aug 2026.** `\workshoptitle`
reads "Economics for Machine Learning (EconML)", the workshop's registered name;
an earlier draft had it backwards. The call also confirms the nine-page content
limit with figures and tables included, the `dblblindworkshop` option, the
29 Aug deadline anywhere on earth, and Atlanta on 12 or 13 Dec 2026.

## Risk register

| Risk | Severity | State |
|---|---|---|
| ~~Heterogeneous-response port does not land in time~~ | **closed, realized, fallback accepted** | Steps 1 to 3 ran 18 Aug 2026. The port is exact, reproducing the unmodified base at every `N` from 1 to 6, and both profile constructors hit their targets to machine precision. **The gate failed:** a `17.7` point residual at `N = 2` from the still-shared liquidity and impact channels, and no local slope at `N >= 4`. Neither named repair is attempted, by decision on 19 Aug 2026. Panels 2, 2b, 4 and 5 ship `[DRY RUN]`, which is the fallback the plan named. Nothing further is owed here |
| ~~Theorem 4 stays a sketch~~ | **closed** | Welfare page landed 18 Aug 2026 with 125 passing assertions. Theorem 4 ships as theory even if panel 6 is cut |
| ~~Section 6 drafting slips~~ | **closed** | Drafted 18 Aug 2026 around the exact two-block root |
| Panel 6 does not land | medium | Second in the de-scope order. If it is cut, Theorem 4 ships as theory with no figure |
| ~~Page budget stays over 9~~ | **closed** | Measured at `10.41` pages on 19 Aug 2026 with all eleven sections drafted. The compression order ran in full and recovered only `0.27`. Closed 19 Aug 2026 in the LaTeX pass: `paper/main.pdf` is nine content pages with references and the checklist after, which is the compliant form. The cuts are recorded in `paper/README.md`. No section was dropped |
| A referee asks for fully heterogeneous agents | low | Answered as future work with the machinery stated to extend |
| A referee probes finite `gamma_PO` | **now low** | Was the paper's weakest point. The imperfect-correction law answers it directly |
| A referee reads a dry run as a measurement | low | `[DRY RUN]` is its own flag, Section 9 states each panel's status in its own row, and the gate outcome is a stated limitation in Section 10 |

## De-scope order, current

Supervision from public prices, then panel 6, then the free-riding diagnostic,
then the clustered companion in panel 2.

**Never cut:** panel 1's anchor, panel 4, panel 5, the exact two-block root, and
the private-versus-systemic framing.

The exact two-block root was third in this order until the limit was shown to err
unsafe. It is what makes Section 6's criterion honest rather than a refinement of
it.

**The port is not in this order and never was.** It was infrastructure that would
have upgraded panels 2, 2b, 4 and 5 from `[DRY RUN]` to `[MEASURED]`. The gate
closed that route for this submission, so those panels ship at the status they
already held. No panel is lost and no claim is weakened below what the ledger
already recorded; what is lost is an upgrade that was never assumed.

## Suggested order for the remaining days

The port workstream is closed and the theory is complete, so what remains is
writing and one panel. Draft Sections 7 and 8, build panel 6 and wire
`pigouvian_wedge` into the theory module, then write Section 9 with each panel's
actual status in it, then Section 10, then rewrite the abstract around a measured
number. Reconcile the four status surfaces last, as its own pass, against the
built PDF rather than the source.

The paper is submittable as it stands: the theory is complete and certified,
panel 1 is measured in a real market, and panels 2 to 5 are presented honestly as
closed-form predictions with reference-environment agreement stated as such. That
is a weaker empirical section than the plan wanted, and it is not a failed
submission.

---

## Conventions that are load-bearing

Status flags mean what `writing/CLAIMS-LEDGER.md` says they mean, and the flag in
the paper must match the ledger, which must match `ml-contributions/CERTIFICATES.md`.
A closed form reaching the paper without a passing certificate ships at
`[DERIVED]`, never `[VERIFIED]`. A dry run is not a measurement. All stability
claims use the spectral form, never a mean. Prose carries no em dashes and is
checked with `prose-guard`. Nothing in the double-blind build positions REFLEX or
PEBSA as the authors' own work.
