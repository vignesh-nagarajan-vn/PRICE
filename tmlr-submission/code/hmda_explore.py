"""First look at take-up versus offered rate spread in public HMDA data (one state-year).
Usage: python -I code/hmda_explore.py data/raw/hmda_CA_2022_purchase.csv"""
import csv
import sys
from collections import Counter, defaultdict

import numpy as np

path = sys.argv[1]
n_all = 0
keep = []
reasons = Counter()
with open(path, newline="") as f:
    for r in csv.DictReader(f):
        n_all += 1
        cond = [("loan_type", r["loan_type"] == "1"), ("lien", r["lien_status"] == "1"),
                ("occupancy", r["occupancy_type"] == "1"), ("term360", r["loan_term"] == "360"),
                ("fixed", r["intro_rate_period"] in ("NA", "Exempt", "")), ("closed_end", r["open-end_line_of_credit"] == "2"),
                ("not_business", r["business_or_commercial_purpose"] == "2"), ("not_reverse", r["reverse_mortgage"] == "2"),
                ("conforming", r["conforming_loan_limit"] == "C")]
        bad = [k for k, ok in cond if not ok]
        if bad:
            reasons[bad[0]] += 1
            continue
        try:
            rs = float(r["rate_spread"]); ir = float(r["interest_rate"])
        except ValueError:
            reasons["no_rate"] += 1
            continue
        keep.append((r["action_taken"], rs, ir, r["lei"], r["loan_to_value_ratio"], r["debt_to_income_ratio"],
                     r["loan_amount"], r["income"], r["applicant_credit_score_type"]))
print(f"rows {n_all}; kept {len(keep)}; dropped by first failing filter: {dict(reasons.most_common())}")
acc = np.array([k[0] == "1" for k in keep], float)
rs = np.array([k[1] for k in keep])
print(f"take-up among approved: {acc.mean():.4f}; rate spread quantiles 1/10/50/90/99%: {np.round(np.percentile(rs, [1, 10, 50, 90, 99]), 3)}")
edges = np.percentile(rs, np.linspace(0, 100, 11))
print("raw take-up by rate-spread decile:")
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (rs >= lo) & (rs <= hi)
    print(f"   [{lo:6.3f}, {hi:6.3f}]  n={m.sum():6d}  take-up={acc[m].mean():.4f}")
lei = Counter(k[3] for k in keep)
print("lenders:", len(lei), "| top-10 share:", round(sum(c for _, c in lei.most_common(10)) / len(keep), 3))
