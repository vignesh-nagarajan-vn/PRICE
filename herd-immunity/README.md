# Herd Immunity and Learning Externalities in Markets of Shared Foundation Models

| | |
| --- | --- |
| **Venue** | [ABCSS 2026](https://css-japan.com/abcss2026/), a workshop at IEEE BigData 2026 (Dec 14 to 17, Phoenix) |
| **Status** | Accepted Nov 2, 2026, paper ID S07214. Camera-ready and author registration due Nov 26, presentation video due Dec 1 |
| **Submitted paper** | [`ieee-abcss/submission/abcss2026-herd-immunity.pdf`](ieee-abcss/submission/abcss2026-herd-immunity.pdf), 7 pages, IEEE two-column |
| **Camera-ready** | [`Herd Immunity - ABCSS 2026 revised paper.pdf`](<ieee-abcss/Herd Immunity Paper - ABCSS 2026 camera-ready/Herd Immunity - ABCSS 2026 revised paper.pdf>), 8 pages, PDF 1.4. Run it through IEEE PDF eXpress (conference ID 70701X) and upload the file that comes back |
| **Base paper** | REFLEX, [arXiv:2608.16155](https://arxiv.org/abs/2608.16155) |

## Thesis

A learning agent can pass every stability test run on it alone and still help destabilize its market, because each agent's retraining reshapes the data every other agent learns from next. The strength of that learning externality is set by effective crowding, which counts independent models and not firms. Three remedies follow in closed form: a retraining cadence window, a coverage threshold for feedback correction, and a Pigouvian fee.

## Results

| Result | Object |
| --- | --- |
| Effective crowding | `N_eff = 1 + kappa(lambda_max(R) - 1)`, and with a shared model fraction `s`, `N_eff = 1 + kappa*s*(N-1)` |
| Cadence window | `K_max = ln((m_N-1)/(m_N+1)) / ln c`, with critical crowding `(1+c)/(1-c)` |
| Herd immunity | Exact two-block root. In the fully shared corner it is the imperfect-vaccine coverage law `(1 - 1/m_N)/e` |
| Pigouvian wedge | Fee `t*` from stationary variance `1/(1-m_N^2)`, with over-adaptation for every `N >= 2` |

All four rest on one substitution, `m_N = N_eff * m_1`.

## Folder map

| Path | Holds |
| --- | --- |
| [`ieee-abcss/`](ieee-abcss/) | The paper: LaTeX source in `paper/`, the upload package in `submission/` and the build script |
| [`ieee-abcss/Herd Immunity Paper - ABCSS 2026 camera-ready/`](<ieee-abcss/Herd Immunity Paper - ABCSS 2026 camera-ready/>) | The camera-ready: source, the built PDF, the Overleaf zip, the compliance check and the three review reports |
| [`math/`](math/) | Notation, standing assumptions, one note per theorem and the complete proofs under `derivations/` |
| [`ml-contributions/`](ml-contributions/) | The theory module, the response environment, the experiment harness and the certificates |
| [`literature/`](literature/) | The literature review |

## Verify and rebuild

Run the certificates. All 542 assertions across eight files pass.

```bash
for f in herd-immunity/ml-contributions/certificates/verify_*.py; do python "$f" || break; done
```

Rebuild the paper and the upload package. The script stops on build errors, overfull boxes, undefined references, more than 10 pages or a font that is not embedded.

```bash
python herd-immunity/ieee-abcss/build_submission.py
```

## What is measured

One check is measured: it reruns the order-flow simulator from REFLEX and reproduces the published amplification of `1.74x` and `3.16x`. Every other check is a dry run that confirms a formula against the model it came from, and the paper labels each one that way. The key eigenvalue has not yet been measured on deployed models.

## Status flags

The notes in `math/` and `ml-contributions/` use four flags.

- `[VERIFIED]` follows from certified base results, or is already checked numerically
- `[DERIVED]` worked out for this paper, derivation recorded, low proof risk
- `[TO BUILD]` new experiment or configuration
- `[DEFERRED]` stated in the body, completed for the journal version

## Earlier version

The first full draft, its section drafts, claims ledger and status board, and the plan for the IEEE rewrite are in [`../archive/herd-immunity-v1/`](../archive/herd-immunity-v1/).
