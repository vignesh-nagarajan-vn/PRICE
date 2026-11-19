"""Completeness check of the supplementary archive.

Checks that every file a table or figure of the paper is built from is present (the list in README.md) and that
each result file holds the runs it should.  Run it from anywhere inside the archive:

    python -I code/verification/check_supplement.py

Exit status 0 if everything is present and complete.
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TAGS = ["CA_2022", "CA_2023", "FL_2022", "FL_2023", "TX_2022", "TX_2023"]
CELLS = 18 * 6                                           # markets x starting rates

# result file -> (methods, seeds per cell); runs = cells x seeds x methods
RUNS = {
    "main.json": (12, 50),
    "determinism_check.json": (3, 50),
    "robust_budget05.json": (2, 30), "robust_budget20.json": (2, 30), "robust_hoeffding.json": (2, 30),
    "robust_hist.json": (2, 30), "robust_etahalf.json": (1, 30),
    "robust_tsown10.json": (1, 20), "robust_tsown100.json": (1, 20), "robust_tsownlevel.json": (1, 20),
    "robust_armsmargin.json": (2, 20),
    "safe_step0005.json": (2, 20), "safe_step001.json": (2, 20), "safe_step002.json": (2, 20),
    "safe_step004.json": (2, 20), "safe_norefresh.json": (1, 20),
}
for key in ("ncap50", "ncap200", "ratio125", "ratio200", "step0025", "step010", "n032", "n0128", "alpha01", "alpha10"):
    RUNS[f"design_{key}.json"] = (2, 30)

LOGS = {       # log -> a line it must contain
    "verify_math.log": r"(\d+) of \1 checks passed",
    "lp_check.log": r"LP optimum",
    "coverage.log": r"all certified cells below alpha",
    "check_baselines.log": r"(\d+) of \1 checks passed",
    "lean_axioms.log": r"theorems checked: (\d+)\ndeclared: \1",
    "hmda_takeup.log": r"wild cluster bootstrap",
    "hmda_offers.log": r".",
}
FILES = (
    [f"data/derived/takeup_{t}.json" for t in TAGS] + [f"data/derived/offers_{t}.json" for t in TAGS]
    + ["data/derived/raw_counts.json", "results/adoption_times.json", "README.md",
       "lean/lakefile.toml", "lean/lean-toolchain", "lean/lake-manifest.json", "lean/CreditCert.lean",
       "code/download_hmda.sh", "code/hmda_takeup.py", "code/hmda_offers.py", "code/cluster_inference.py",
       "code/run_design.sh", "code/experiments/run_markets.py", "code/experiments/report.py",
       "code/experiments/figures.py", "code/experiments/adoption_times.py", "code/experiments/robust_text.tex",
       "code/lending/market.py", "code/lending/bounds.py", "code/lending/agent.py", "code/lending/baselines.py",
       "code/lending/metrics.py", "code/verification/verify_math.py", "code/verification/lp_check.py",
       "code/verification/coverage.py", "code/verification/check_baselines.py",
       "code/verification/lean_axioms.py"]
    + [f"lean/CreditCert/{n}.lean" for n in ("Defs", "TakeUp", "Secant", "Certificate", "Adoption", "Confidence",
                                             "Indistinguishable", "Credit", "BernoulliKL", "Anytime")]
)


def main():
    bad = []
    for f in FILES:
        if not os.path.isfile(os.path.join(ROOT, f)):
            bad.append(f"missing file: {f}")
    for name, (methods, seeds) in sorted(RUNS.items()):
        path = os.path.join(ROOT, "results", name)
        if not os.path.isfile(path):
            bad.append(f"missing file: results/{name}")
            continue
        runs = json.load(open(path))["runs"]
        want = CELLS * seeds * methods
        per_method = Counter(r["method"] for r in runs)
        if len(runs) != want or len(per_method) != methods or len(set(per_method.values())) != 1:
            bad.append(f"results/{name}: {len(runs)} runs in {len(per_method)} methods, expected {want} in {methods}")
        else:
            print(f"ok  results/{name:28s} {len(runs):6d} runs, {methods} method(s), {seeds} seeds per cell")
    path = os.path.join(ROOT, "results", "adoption_times.json")
    if os.path.isfile(path):
        d = json.load(open(path))
        if not (d["n"] == d["same_as_main"] == CELLS * 50 * 3):
            bad.append("results/adoption_times.json: does not reproduce the certified runs of main.json")
        else:
            print(f"ok  results/adoption_times.json          {d['n']:6d} runs, all reproduce main.json")
    for name, pattern in sorted(LOGS.items()):
        path = os.path.join(ROOT, "results", name)
        if not os.path.isfile(path):
            bad.append(f"missing file: results/{name}")
        elif not re.search(pattern, open(path).read()):
            bad.append(f"results/{name}: expected line not found")
        else:
            print(f"ok  results/{name}")
    readme = open(os.path.join(ROOT, "README.md")).read() if os.path.isfile(os.path.join(ROOT, "README.md")) else ""
    for needle in ("results/main.json", "results/robust_*.json", "results/design_*.json", "results/safe_step*.json",
                   "results/adoption_times.json", "results/lean_axioms.log", "results/verify_math.log"):
        if needle not in readme:
            bad.append(f"README.md does not list {needle}")
    for b in bad:
        print("PROBLEM", b)
    print(f"{len(FILES) + len(RUNS) + len(LOGS)} items checked: " + ("complete" if not bad else f"{len(bad)} problem(s)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
