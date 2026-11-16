#!/usr/bin/env bash
# Fetch the openly-licensed PDFs for the herd-immunity literature review.
# Writes into ./pdfs/. Ten PDFs already live there; six are load-bearing here.
set -u
cd "$(dirname "$0")/pdfs" || exit 1
get () {  # get <arxiv-id> <slug>
  f="${1//\//_}__$2.pdf"
  [ -s "$f" ] && { echo "have  $f"; return; }
  curl -sL --fail --max-time 120 -o "$f" "https://arxiv.org/pdf/$1" \
    && echo "ok    $f" || echo "FAIL  $1  ($2)"
  sleep 2
}

# --- Cluster A: monoculture and model multiplicity ------------------------
get 2101.05853 "kleinberg-raghavan-algorithmic-monoculture"
get 2108.07258 "bommasani-foundation-models-opportunities-risks"
get 2211.13972 "bommasani-picking-on-the-same-person"
get 2307.05862 "toups-ecosystem-level-homogeneous-outcomes"
get 1909.06677 "marx-calmon-ustun-predictive-multiplicity"
get 2203.07487 "black-raghavan-barocas-model-multiplicity"

# --- Cluster B: multiplayer performative prediction -----------------------
get 2201.03398 "narang-multiplayer-performative-prediction"
get 2310.16608 "hardt-mendler-dunner-pp-past-and-future-survey"
get 2201.04853 "brown-hod-kalemaj-pp-stateful-world"
get 1506.06980 "hardt-strategic-classification"

# --- Cluster E: epidemic thresholds on networks ---------------------------
get cond-mat/0010317 "pastor-satorras-vespignani-epidemic-scale-free"

# --- Paywalled / offline: DOI links where known --------------------------
# Cluster A
# Kleinberg & Raghavan 2021, PNAS ............. doi.org/10.1073/pnas.2018340118
# Creel & Hellman 2022, Can. J. Philosophy ..... doi.org/10.1017/can.2022.3
# Birman & Schneider 2009, IEEE S&P ........... doi.org/10.1109/MSP.2009.24
# Cluster C: the policy apparatus
# Weitzman 1974, REStud ....................... doi.org/10.2307/2296698
# Baumol 1972, AER ............................ jstor.org/stable/1803378
# Sandmo 1975, Swedish J. Economics ........... doi.org/10.2307/3439329
# Samuelson 1954, REStat ...................... doi.org/10.2307/1925895
# Buchanan & Stubblebine 1962, Economica ...... doi.org/10.2307/2551386
# Meade 1952, Economic Journal ................ doi.org/10.2307/2227173
# Bergstrom, Blume, Varian 1986, J. Pub. Econ.  doi.org/10.1016/0047-2727(86)90024-1
# Cluster D: systemic risk
# Beale et al. 2011, PNAS ..................... doi.org/10.1073/pnas.1105882108
# Wagner 2010, J. Fin. Intermediation ......... doi.org/10.1016/j.jfi.2009.07.002
# Haldane & May 2011, Nature .................. doi.org/10.1038/nature09659
# Acemoglu et al. 2015, AER ................... doi.org/10.1257/aer.20130456
# Elliott, Golub, Jackson 2014, AER ........... doi.org/10.1257/aer.104.10.3115
# Allen & Gale 2000, JPE ...................... doi.org/10.1086/262109
# Brunnermeier & Pedersen 2009, RFS ........... doi.org/10.1093/rfs/hhn098
# Kirilenko et al. 2017, J. Finance ........... doi.org/10.1111/jofi.12498
# Banerjee 1992, QJE .......................... doi.org/10.2307/2118364
# Bikhchandani, Hirshleifer, Welch 1992, JPE .. doi.org/10.1086/261849
# Scharfstein & Stein 1990, AER ............... jstor.org/stable/2006678
# Khandani & Lo 2007, J. Investment Mgmt ...... ssrn.com/abstract=1015987
# Cluster E: epidemiology
# Kermack & McKendrick 1927, Proc. Roy. Soc. A  doi.org/10.1098/rspa.1927.0118
# Diekmann, Heesterbeek, Metz 1990, J. Math Bio doi.org/10.1007/BF00178324
# Fine, Eames, Heymann 2011, Clin. Infect. Dis. doi.org/10.1093/cid/cir007
# Van Mieghem, Omic, Kooij 2009, IEEE/ACM ToN . doi.org/10.1109/TNET.2008.925623
# Wang et al. 2003, SRDS ...................... doi.org/10.1109/RELDIS.2003.1238052
# Anderson & May 1991 ......................... Oxford Univ. Press monograph
# Cluster F: effective counts
# Laloux et al. 1999, PRL ..................... doi.org/10.1103/PhysRevLett.83.1467
# Plerou et al. 2002, Phys Rev E .............. doi.org/10.1103/PhysRevE.65.066126
# Hill 1973, Ecology .......................... doi.org/10.2307/1934352
# Simpson 1949, Nature ........................ doi.org/10.1038/163688a0
# Hirschman 1964, AER ......................... jstor.org/stable/1818582
# Thouless 1974, Physics Reports .............. doi.org/10.1016/0370-1573(74)90029-5
# Roy & Vetterli 2007, EUSIPCO ................ ieeexplore.ieee.org (proceedings)
# Cluster G: policy (working papers, non-load-bearing)
# Vipra & Korinek 2023 ........................ brookings.edu working paper
# Widder, West, Whittaker 2023 ................ ssrn.com/abstract=4543807
# EU AI Act, Regulation (EU) 2024/1689 ........ eur-lex.europa.eu
echo "done"
