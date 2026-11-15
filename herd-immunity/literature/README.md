# Literature

| File | Covers |
|---|---|
| [`LITERATURE-REVIEW-P2.md`](LITERATURE-REVIEW-P2.md) | The full review: seven clusters, the gaps, the novelty verdict, the verification debt |
| [`download_litreview_pdfs.sh`](download_litreview_pdfs.sh) | Fetches every openly-licensed PDF for this review, one command |

The PDFs live in [`pdfs/`](pdfs/). Six of the ten there are load-bearing for
this paper: Perdomo et al., Mendler-Dunner et al., Izzo et al., Miller et al.,
Drusvyatskiy and Xiao, and Li and Wai. The download script writes into that
same folder.

## The seven clusters

| | Cluster | Why it is here |
|---|---|---|
| A | Algorithmic monoculture and model multiplicity | The venue's home literature and the nearest prior art on the paper's headline object |
| B | Multiplayer and multi-agent performative prediction | Where the dynamics live, and the strongest technical prior-art threat. **Holds REFLEX (B13), the base paper, with the claim-by-claim non-overlap statement** |
| C | Externalities, public goods, and corrective taxation | The economics apparatus Sections 7 and 8 use |
| D | Systemic risk, crowding, and the regulator's dilemma | Where private-versus-systemic stability was posed before, without learners. Also holds PEBSA (D9), the exogenous-signal contrast |
| E | Epidemic thresholds and herd immunity | The law Result 3 lands on, and its spectral form on networks |
| F | Effective counts and spectra of correlation matrices | The ancestry of `lambda_max(R)` as an effective count, conceded up front |
| G | AI supply chains and market concentration | The policy conversation the paper turns into a term in a condition |

## The six citations without which the paper is rejected

Each gets a named-delta sentence in related work, not a mention.

1. **Kleinberg and Raghavan** (PNAS 2021), nearest monoculture result. Delta:
   static allocation welfare against dynamical stability.
2. **Narang et al.** (JMLR 2023), nearest dynamics. Delta: their coupling is a
   scalar sensitivity, blind to which direction each agent perturbs the
   environment, so monoculture cannot be expressed in their condition.
3. **Beale et al.** (PNAS 2011), nearest private-versus-systemic framing. Delta:
   their agents hold portfolios, they do not learn, and there is no second
   instrument to trade diversity against.
4. **Anderson and May** (1991) with **Wang et al.** (2003), the threshold law
   being invoked. Delta: `R_0` here is a learning modulus derived from
   microstructure primitives, and the vaccine is an algorithm.
5. **Weitzman** (REStud 1974), the instrument-choice framing for the policy
   triple.
6. **Laloux et al.** / **Plerou et al.** with **Roy and Vetterli**, the
   effective-count concession. Delta: computed on response Jacobians rather
   than returns, and entering a stability condition rather than describing a
   cross-section.

## Verification status

This review was assembled from record rather than from click-through. Tags are
`[V1]` PDF in hand and read, and `[B]` bibliographic details stated from record,
internally consistent, **pending click-through verification**. The review's
closing section lists the verification debt as a checklist. Clear it before
camera-ready, and clear the six load-bearing entries before the submission
draft is written.
