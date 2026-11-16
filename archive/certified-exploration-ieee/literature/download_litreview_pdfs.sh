#!/usr/bin/env bash
# Fetch the openly-licensed PDFs for the M2 literature review.
# Run on an unrestricted machine (the build environment blocks arXiv/PMLR).
# Ten core PDFs already ship in ./pdfs/ (copied from the REFLEX repo).
set -u
cd "$(dirname "$0")/pdfs" || exit 1
get () {  # get <arxiv-id> <slug>
  f="${1//\//_}__$2.pdf"
  [ -s "$f" ] && { echo "have  $f"; return; }
  curl -sL --fail --max-time 120 -o "$f" "https://arxiv.org/pdf/$1" \
    && echo "ok    $f" || echo "FAIL  $1  ($2)"
  sleep 2
}

# --- Cluster A/B: performative prediction frontier -----------------------
get 2310.16608 "hardt-mendler-dunner-pp-past-and-future-survey"
get 2305.18728 "lin-zrnic-plugin-performative-optimization"
get 2201.03398 "narang-multiplayer-performative"
get 2405.15172 "reverse-causal-pp-distribution-map"
get 2408.05146 "pp-games-mechanism-design"
get 2503.07324 "decision-dependent-distribution-dynamics"
get 2509.17304 "sprint-stochastic-pp-variance-reduction"
get 2606.07890 "partially-performative-prediction"
get 2602.10176 "dissecting-pp-comprehensive-survey"
get 2607.15623 "retraining-seeks-stable-signals"

# --- Cluster D: learning-for-control canon (arXiv versions) --------------
get 2102.05214 "wagenmaker-task-optimal-exploration-linear-systems"
get 1710.01688 "dean-mania-matni-recht-tu-sample-complexity-lqr"
get 2001.09576 "simchowitz-foster-naive-exploration-online-lqr"

# --- Paywalled classics: DOI links (library access required) -------------
# Keskin & Zeevi 2014, Operations Research .... doi.org/10.1287/opre.2014.1294
# Harrison, Keskin, Zeevi 2012, Mgmt Science .. doi.org/10.1287/mnsc.1110.1426
# Broder & Rusmevichientong 2012, Oper. Res. .. doi.org/10.1287/opre.1120.1057
# den Boer 2015, Surveys in ORMS .............. doi.org/10.1016/j.sorms.2015.03.001
# Bombois et al. 2006, Automatica ............. doi.org/10.1016/j.automatica.2006.05.016
# Rothschild 1974, J. Economic Theory ......... doi.org/10.1016/0022-0531(74)90066-0
# Aghion, Bolton, Harris, Jullien 1991, REStud  doi.org/10.2307/2297825
# Easley & Kiefer 1988, Econometrica .......... doi.org/10.2307/1911358
# McLennan 1984, J. Econ. Dynamics & Control .. doi.org/10.1016/0165-1889(84)90022-6
# Keller & Rady 1999, REStud .................. doi.org/10.1111/1467-937X.00095
# Grossman & Stiglitz 1980, AER ............... jstor.org/stable/1805228
# Lai & Robbins 1979, Annals of Statistics .... doi.org/10.1214/aos/1176344840
# Kiefer & Wolfowitz 1960, Canad. J. Math ..... doi.org/10.4153/CJM-1960-030-4
# Gill & Levit 1995, Bernoulli ................ doi.org/10.2307/3318681
# Feldbaum 1960-61, Autom. Remote Control ..... (reprinted; see Wittenmark's dual-control survey)
echo "done"
