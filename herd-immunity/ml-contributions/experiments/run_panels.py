"""Run every panel, write results and figures, and report disagreements.

    python herd-immunity/ml-contributions/experiments/run_panels.py

Deterministic from the seed in panels.py. Writes JSON to results/ and PNG to
results/figures/. Exits nonzero if any panel disagrees with its closed form,
so a broken derivation fails the run rather than producing a quiet figure.

These are dry runs in the linearized reference environment, not the paper's
panels. See panels.py for what that does and does not establish.
"""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                               # noqa: E402
import numpy as np                                            # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import panels                                                 # noqa: E402

RESULTS = pathlib.Path(__file__).resolve().parent / "results"
FIGURES = RESULTS / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

TOL = 5e-3
problems = []


def save(name, obj):
    (RESULTS / f"{name}.json").write_text(json.dumps(obj, indent=2), encoding="utf-8")


def note(msg):
    problems.append(msg)
    print(f"  DISAGREEMENT  {msg}")


# ------------------------------------------------------------------ panel 1

print("\npanel 1: amplification replication")
p1 = panels.panel1_amplification()
save("panel1_amplification", p1)
for r in p1["rows"]:
    print(f"  N={r['N']:>2}  predicted {r['predicted_radius']:.6f}  "
          f"measured {r['measured_radius']:.6f}  "
          f"amplification {r['measured_amplification']:.4f}")
if p1["max_rel_error"] > TOL:
    note(f"panel 1 relative error {p1['max_rel_error']:.2e}")
print(f"  max relative error {p1['max_rel_error']:.2e}")
print(f"  EXTERNAL ANCHOR STILL OUTSTANDING: {p1['external_anchor']['status']}")

fig, ax = plt.subplots(figsize=(5.5, 3.6))
Ns = [r["N"] for r in p1["rows"]]
ax.plot(Ns, [r["predicted_radius"] for r in p1["rows"]], "-", label="predicted")
ax.plot(Ns, [r["measured_radius"] for r in p1["rows"]], "o", ms=5,
        mfc="none", label="measured from dynamics")
ax.axhline(1.0, ls=":", lw=1, color="0.5")
ax.set_xlabel("N"); ax.set_ylabel("$m_N$")
ax.set_title("Panel 1: amplification (reference environment)", fontsize=10)
ax.legend(fontsize=8); fig.tight_layout()
fig.savefig(FIGURES / "panel1_amplification.png", dpi=150); plt.close(fig)


# ------------------------------------------------------------------ panel 2

print("\npanel 2: the (N, s) phase diagram")
p2 = panels.panel2_phase_diagram()
save("panel2_phase_diagram", p2)
print(f"  {len(p2['grid'])} cells, max absolute error {p2['max_abs_error']:.2e}")
if p2["max_abs_error"] > TOL:
    note(f"panel 2 absolute error {p2['max_abs_error']:.2e}")

p2b = panels.panel2_clustered_companion()
save("panel2b_clustered", p2b)
print(f"  clustered companion: measured m_N {p2b['measured_m_N']:.4f}, "
      f"mean index reports {p2b['mean_index_m_N']:.4f}")
if not (p2b["truly_unstable"] and p2b["mean_index_says_stable"]):
    note("panel 2b no longer exhibits the mean-index failure")
else:
    print(f"  the mean index calls an unstable market safe, understating "
          f"N_eff by {p2b['understatement_factor']:.3f}x")

Ns = sorted({c["N"] for c in p2["grid"]})
ss = sorted({c["s"] for c in p2["grid"]})
Z = np.array([[next(c["measured_m_N"] for c in p2["grid"]
                    if c["N"] == N and c["s"] == s) for s in ss] for N in Ns])
fig, ax = plt.subplots(figsize=(5.6, 3.8))
im = ax.pcolormesh(ss, Ns, Z, shading="nearest", cmap="RdYlBu_r",
                   norm=matplotlib.colors.TwoSlopeNorm(vcenter=1.0))
cs = ax.contour(ss, Ns, Z, levels=[1.0], colors="k", linewidths=2)
ax.clabel(cs, fmt={1.0: "stability boundary"}, fontsize=8)
fig.colorbar(im, ax=ax, label="measured $m_N$")
ax.set_xlabel("shared-model fraction $s$"); ax.set_ylabel("firms $N$")
ax.set_title("Panel 2: the $(N, s)$ phase diagram", fontsize=10)
fig.tight_layout(); fig.savefig(FIGURES / "panel2_phase_diagram.png", dpi=150)
plt.close(fig)


# ------------------------------------------------------------------ panel 3

print("\npanel 3: the crowding-cadence frontier")
p3 = panels.panel3_cadence()
save("panel3_cadence", p3)
print(f"  {len(p3['cells'])} cells, {p3['disagreements']} disagreements with "
      f"the predicted frontier")
if p3["disagreements"]:
    note(f"panel 3 has {p3['disagreements']} disagreements")

ss = sorted({c["s"] for c in p3["cells"]})
Ks = sorted({c["K"] for c in p3["cells"]})
S = np.array([[next(c["measured_stable"] for c in p3["cells"]
                    if c["s"] == s and c["K"] == K) for K in Ks] for s in ss])
fig, ax = plt.subplots(figsize=(6.0, 3.8))
ax.pcolormesh(Ks, ss, S.astype(float), shading="nearest", cmap="RdYlBu", vmin=0, vmax=1)
frontier = [next(c["k_max"] for c in p3["cells"] if c["s"] == s) for s in ss]
ok = [(k, s) for k, s in zip(frontier, ss) if k is not None]
if ok:
    ax.plot([k for k, _ in ok], [s for _, s in ok], "k-", lw=2,
            label="$K_{max}$ predicted")
ax.set_xlabel("cadence $K$"); ax.set_ylabel("shared-model fraction $s$")
ax.set_title(f"Panel 3: cadence window, $c$ = {p3['params']['c']}", fontsize=10)
ax.legend(fontsize=8, loc="upper right"); fig.tight_layout()
fig.savefig(FIGURES / "panel3_cadence.png", dpi=150); plt.close(fig)


# ------------------------------------------------------------------ panel 4

print("\npanel 4: herd immunity")
p4 = panels.panel4_herd_immunity()
save("panel4_herd_immunity", p4)
print(f"  m_N = {p4['m_N']:.4f}, limit threshold rho* = {p4['rho_star_limit']:.4f}")
print(f"  correction is a usable lever only above "
      f"gamma_PO/gamma = {p4['critical_efficacy_gamma_PO_over_gamma']:.2f}")
for s_ in p4["series"]:
    print(f"  efficacy={s_['efficacy']:.2f}  measured {s_['measured_threshold_firms']} "
          f"firms  |  limit says {s_['predicted_limit_threshold_firms']}  |  "
          f"imperfect law says {s_['imperfect_law_firms']}  "
          f"{'MATCH' if s_['imperfect_law_matches'] else 'differs'}")
limit_series = p4["series"][0]
if limit_series["measured_threshold_firms"] != \
        limit_series["predicted_limit_threshold_firms"]:
    note("panel 4 limit threshold does not match the closed form")
_law_hits = sum(1 for s_ in p4["series"] if s_["imperfect_law_matches"])
print(f"  the imperfect-correction law predicts {_law_hits}/{len(p4['series'])} "
      f"thresholds, at kappa = {p4['params']['kappa']} where it is not exact")

fig, ax = plt.subplots(figsize=(6.0, 3.8))
for s_ in p4["series"]:
    ax.plot([p["rho"] for p in s_["points"]],
            [p["measured_radius"] for p in s_["points"]],
            marker="o", ms=3, lw=1.2,
            label=f"efficacy {s_['efficacy']:.2f}")
ax.axhline(1.0, ls=":", color="0.4", lw=1)
ax.axvline(p4["rho_star_limit"], ls="--", color="k", lw=1,
           label=r"$\rho^*$ (perfect correction)")
ax.set_xlabel(r"corrected fraction $\rho$"); ax.set_ylabel("measured $m_N$")
ax.set_title("Panel 4: herd immunity, and the limit's optimism", fontsize=10)
ax.legend(fontsize=7); fig.tight_layout()
fig.savefig(FIGURES / "panel4_herd_immunity.png", dpi=150); plt.close(fig)


# ------------------------------------------------------------------ panel 5

print("\npanel 5: the substitution frontier")
p5 = panels.panel5_substitution()
save("panel5_substitution", p5)
print(f"  {p5['exact_matches']} of {p5['points']} points match the predicted "
      f"threshold exactly")
if p5["exact_matches"] != p5["points"]:
    note(f"panel 5 matched {p5['exact_matches']}/{p5['points']}")

fig, ax = plt.subplots(figsize=(6.0, 3.9))
xs = [p["s"] for p in p5["curve"]]
N5 = p5["params"]["N"]
ax.plot(xs, [p["predicted_rho_star"] for p in p5["curve"]], "-", lw=2,
        label=r"predicted $\rho^*(s)$, continuous")
ax.step(xs, [p["predicted_threshold_firms"] / N5 for p in p5["curve"]],
        where="mid", lw=1.2, color="tab:green",
        label=r"predicted, whole firms")
ax.plot(xs, [p["measured_rho"] for p in p5["curve"]], "o", ms=6, mfc="none",
        color="tab:orange", label="measured threshold")
ax.fill_between(xs, [p["predicted_rho_star"] for p in p5["curve"]], 1.0,
                alpha=0.12, color="tab:blue", label="stable")
ax.set_xlabel("shared-model fraction $s$")
ax.set_ylabel(r"corrected fraction $\rho$")
ax.set_title(f"Panel 5: the substitution frontier "
             f"({p5['exact_matches']}/{p5['points']} exact)", fontsize=10)
ax.legend(fontsize=7); ax.set_ylim(-0.02, 1.0); fig.tight_layout()
fig.savefig(FIGURES / "panel5_substitution.png", dpi=150); plt.close(fig)



# ------------------------------------------------------------------ panel 6

print("\npanel 6: over-adaptation and the Pigouvian wedge")
p6 = panels.panel6_over_adaptation()
save("panel6_over_adaptation", p6)
for r in p6["rows"]:
    print(f"  N={r['N']:>2} kappa={r['kappa']} s={r['s']} chi={r['chi']}  "
          f"a_d {r['a_decentralized']:.4f}  a_s {r['a_social']:.4f}  "
          f"over-adaptation {100 * r['relative_over_adaptation']:.1f}%")
if p6["over_adaptation_violations"]:
    note(f"panel 6 has {p6['over_adaptation_violations']} rows whose "
         f"over-adaptation verdict contradicts Corollary 4.2")
if p6["max_fee_implementation_error"] > 1e-6:
    note(f"panel 6 fee does not implement the optimum, error "
         f"{p6['max_fee_implementation_error']:.2e}")
if p6["max_m_N_measurement_error"] > TOL:
    note(f"panel 6 measured m_N departs from the closed form by "
         f"{p6['max_m_N_measurement_error']:.2e}")
print(f"  smallest relative gap {p6['smallest_relative_gap']:.4f} at N = 2; "
      f"zero at N = 1 with no client exposure, as Corollary 4.2 requires")
print(f"  the fee implements the social optimum to "
      f"{p6['max_fee_implementation_error']:.1e}")

p6b = panels.panel6_comparative_statics()
save("panel6b_comparative_statics", p6b)
for name, ser in p6b["series"].items():
    print(f"  t* strictly increasing in {name}: {ser['strictly_increasing']}")
    if not ser["strictly_increasing"]:
        note(f"panel 6b: t* is not strictly increasing in {name}")
print(f"  boundary divergence rate, log-log slope "
      f"{p6b['boundary_log_log_slope']:.4f} against a predicted -2")
if abs(p6b["boundary_log_log_slope"] + 2.0) > 1e-3:
    note(f"panel 6b divergence rate {p6b['boundary_log_log_slope']:.4f}, "
         f"predicted -2")

fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6))
ax = axes[0]
sym = [r for r in p6["rows"] if r["chi"] == 1.0 and r["s"] == 1.0
       and r["kappa"] == 0.8]
Ns6 = [r["N"] for r in sym]
ax.plot(Ns6, [r["a_decentralized"] for r in sym], "o-", ms=5,
        label="decentralized $a_d$")
ax.plot(Ns6, [r["a_social"] for r in sym], "s-", ms=5,
        label="socially optimal $a_s$")
ax.fill_between(Ns6, [r["a_social"] for r in sym],
                [r["a_decentralized"] for r in sym], alpha=0.15,
                color="tab:red", label="over-adaptation")
ax.set_xlabel("firms $N$"); ax.set_ylabel("aggressiveness $a$")
ax.set_title("Panel 6: over-adaptation ($\\chi$ = 1, $s$ = 1)", fontsize=10)
ax.legend(fontsize=8)

ax = axes[1]
ser = p6b["series"]["N"]
xs6 = [p["N"] for p in ser["points"] if p["t_star"] is not None]
ys6 = [p["t_star"] for p in ser["points"] if p["t_star"] is not None]
ax.semilogy(xs6, ys6, "-", lw=2, label="$t^*$ in $N$")
ax.set_xlabel("firms $N$"); ax.set_ylabel("$t^*$ (log scale)")
ax.set_title("The wedge's comparative statics", fontsize=10)
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(FIGURES / "panel6_over_adaptation.png", dpi=150)
plt.close(fig)


# ---------------------------------------------------------------- summary

print("\n" + "=" * 68)
if problems:
    print(f"{len(problems)} DISAGREEMENT(S) between the panels and the closed forms:")
    for p in problems:
        print(f"  - {p}")
    print("=" * 68)
    sys.exit(1)
print("All panels agree with their closed forms.")
print("These are reference-environment dry runs. The paper's panels run in the")
print("order-flow simulator, and every experimental claim stays at its")
print("derivation status until they do.")
print("=" * 68)
