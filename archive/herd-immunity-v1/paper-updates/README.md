# EconML Paper Upgrade Ideas---Potential Improvements

The complete outline of changes that would make the EconML submission a
frontier paper: clear measured results with genuine statistical
significance, Lean 4 machine-checked mathematics, and explicit alignment
with both EconML @ NeurIPS 2026 directions. **Outlines and
specifications only, by design: nothing here is the finished content.**
Every assumption the outlines rest on was verified this session or is
explicitly flagged as a gate to check first; the log has the full trail.

Read in order:

| File | What it is |
|---|---|
| `00-overview.md` | The three pillars, the honesty constraints, feasibility up front |
| `01-section-outlines.md` | **The core deliverable**: per-section Keep / Change / Add / Cut / Track hook / Tier, for the abstract, all nine sections, appendices (including the new K: machine-checked results, and L: statistical protocols), and the checklist |
| `02-lean4-plan.md` | Theorem-by-theorem formalization roadmap (13 targets, S/M/L difficulty, phases), built on verified Mathlib facts: spectral theorem and Rayleigh available; Perron-Frobenius and Bernstein absent, with the two proof restructurings that route around them; strict claim-language rules |
| `03-statistics-plan.md` | The significance layer: three evidence regimes with separate reporting standards; the full pre-committed protocol for the measured-alignment panel (bootstrap CIs, permutation null, Marchenko-Pastur analytic null, provider permutation test); interval upgrades for every ensemble fraction; guardrails |
| `04-track-alignment.md` | The verified track wording and the element-by-element map onto Direction 2 (primary) and Direction 1 (secondary), the six concrete alignment edits, and the anti-goals |
| `05-assumption-verification-log.md` | All 15 assumptions with verification method and confidence; the two flagged gates (Panel 7 data source; Mathlib Phase 0 audit) |
| `06-sequencing-and-page-budget.md` | Deadline / camera-ready / journal split, the line-by-line nine-page ledger, and the upgrade's own risk register |

Baseline assumed: candidate-v6 from the adversarial-review package (all
mechanical fixes adopted). The two earlier zips (review package with
v5, adversarial package with v6) remain the record of what is already
done; this package is the record of what to build next and exactly
where it goes.
