<!-- prose-lint: off -->

# ABCSS 2026 review reports, paper S07214

Three reviewers. Notification Nov 2, 2026. Recorded verbatim from the acceptance
email so the camera-ready revision can be checked against them.

## Scores

| | R1 | R2 | R3 |
| --- | --- | --- | --- |
| Relevant to the workshop | Yes | Yes | Yes |
| Innovative (0-5) | 3, marginally | 3, marginally | 4, innovative |
| Technical quality (0-5) | 3, good | 2, needs improvement | 3, good |
| Presentation (0-5) | 2, below average | 4, good | 3, above average |
| Of interest to practitioners (0-3) | 2, maybe | 3, yes | 2, maybe |
| Reviewer confidence (0-2) | 0, low | 1, medium | 1, medium |
| Recommendation (0-5) | 3, weak accept | 2, weak reject | 3, weak accept |

## Reviewer 1

Studies the stability of a market in which multiple firms use the same foundation
model to make decisions. The mathematical analysis seems solid, and the connection
to herd immunity is particularly interesting. Two concerns.

1. The connection to foundation models is unclear. It is not clear how the results
   are specific to foundation models or generative AI. Similar effects could occur
   when multiple firms follow similar strategies recommended by the same consulting
   firm. The results seem to apply more generally to firms using similar
   decision-making strategies. Explain what makes foundation models different from
   other sources of shared strategy and why the distinction matters for stability.
2. The market model is not sufficiently explained. Section III introduces the
   Jacobian in Eq. (2) without explaining the underlying market dynamics, so it is
   hard to see how the Jacobian is derived or what the stability analysis represents.
   Rather than referring to previous work, explain the key parts of the model: what
   each firm optimizes, how its decisions affect the market environment, and how the
   resulting data influence later retraining.

## Reviewer 2

Appreciates that the two kinds of check, measured and dry run, are clearly
separated. The main concern is an assumption the central conclusion depends on.

**Main comment.** Under Section III-A, when one dealer tightens its quotes, more
toxic flow reaches every dealer in proportion to a spillover kappa, so the total
effect received grows as kappa(N-1), linearly in N. But in a market where firms
share a single pool of order flow, if orders displaced from one firm are
distributed among the others and total flow is conserved, each firm should receive
roughly kappa/(N-1) rather than kappa. Normalizing kappa = kappa_0/(N-1) caps N_eff
at 1 + kappa_0 even when all firms share one model, and the abstract's claim that
fifty firms on one vendor's model behave like one learner fifty times larger no
longer holds. State explicitly any market mechanism under which kappa does not
depend on N, and discuss how the main results including Theorem 1 change when kappa
is normalized by N.

**Suggestions.**

1. The introduction mentions lending and ranking, but the model and discussion stay
   inside a dealer market. The assumption in Lemma 1 that each firm reads the pool
   only along its own direction rests on a dealer seeing order flow only in the
   instruments it quotes. A short discussion of how far that carries over to lending
   or recommendation would help readers in computational social science.
2. The firms' objective function and the definitions of epsilon, beta and gamma are
   not given, and assumptions such as gamma-strong convexity in Lemma 1 are stated
   without supporting references. These are presumably defined in prior work for the
   scalar dealer-market setting, but this paper treats a more general setting with
   matrix responses E_i. Include the main definitions with their references and
   explain why the assumptions hold in the generalized setting.
3. Theorem 4 considers a decentralized equilibrium, but neither the equilibrium
   concept nor the firms' information structure is stated, and the private
   first-order condition is not shown. Since the ignored cost takes the form
   (W - w_i), firms appear to internalize their own share w_i of the effect on the
   common-mode variance V(m_N), which requires knowing m_N and N_eff. Is that
   consistent with the Conclusion saying every quantity is hidden from a supervisor?
   Specify the information structure assumed.

**Minor.**

1. Figures 1-3 report dry-run results, yet the axis and colorbar labels read
   "measured m_N". Correct the labels.
2. In Section I-D it is unclear what "This result corrects an earlier one" refers
   to. Cite it if published, rephrase if it was an earlier draft.

## Reviewer 3

The framing is original and the distinction between individual-model stability and
market-level stability is useful. The derivations are clear and the public release of
numerical certificates is commendable. The lack of validation on real data is the key
issue.

1. The conclusions are not tested against real data. Apart from the one check that
   reproduces an earlier simulator, all verification compares closed forms against
   the model they were derived from. The dry-run label is honest, but agreement at
   7.1e-15 confirms algebra, not that real markets behave this way. The measured
   check uses the authors' own prior simulator and covers only the monoculture case,
   so it tests none of the four new results. For a venue on big data for
   computational social science, at least one empirical estimate of the key quantity
   is expected. Even a pilot estimate of lambda_max(R) and the implied N_eff on a
   public benchmark would substantially strengthen the paper and would change the
   assessment of its fit to the workshop.
2. A realistic alignment matrix R is not estimated. The main message depends on R
   being close to a known structure. Error correlation is described as only a proxy,
   yet the policy conclusions are phrased as if the proxy were the quantity itself.
   Either show how conclusions change under realistic estimates of R, or explicitly
   restrict the policy claims to the theoretical model. A clearer statement of how
   sensitive the stability boundary is to errors in estimating lambda_max(R) is also
   recommended, since that is what a supervisor would need.

## Status against the revision

| Reviewer and comment | Where the revision answers it |
| --- | --- |
| R1, what makes foundation models different from any other shared strategy | "Why foundation models" paragraph, Section III-B, three reasons |
| R1, the market model behind the Jacobian is not explained | Section III expanded, each firm's problem stated before Eq. (2) |
| R2 main, spillover should be normalized by N when total flow is conserved | Remark 1 (Conserved flow), with `N_eff = 1 + d s + c s (N-1)` and the pure-diversion case |
| R2 minor 1, figures labelled "measured m_N" while reporting dry runs | Axis and colorbar labels now read "realized m_N" |
| R2 minor 2, unclear what "This result corrects an earlier one" refers to | Phrase removed |
| R3, no empirical estimate of the key quantity | Section VII-D, pilot on 79 deployed models, and Table II |

R1's two points, R2's main comment and both minor points, and R3's first point are
answered. R2's suggestions 2 and 3 are not closed, and R3's second point is answered
only in part, through the proxy caveats in Section VII-D and Section IX. Page 8 is
full, so anything added for the open items needs a matching cut.
