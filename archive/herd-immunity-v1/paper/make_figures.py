"""Render the paper's figures from the panel result JSONs.

Publication versions of the harness plots: no embedded titles, since the LaTeX
caption is the label, and larger type so the axes stay readable at column width.
Reads only the committed result files, so the figures cannot drift from the runs
that produced them.

    python econml/paper/make_figures.py
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches
import matplotlib.pyplot as plt                               # noqa: E402
import numpy as np                                            # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "ml-contributions" / "experiments" / "results"
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "legend.fontsize": 7.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})


def load(name):
    return json.loads((RESULTS / f"{name}.json").read_text(encoding="utf-8"))


# ----------------------------------------------------------------- figure 1a
p2 = load("panel2_phase_diagram")
Ns = sorted({c["N"] for c in p2["grid"]})
ss = sorted({c["s"] for c in p2["grid"]})
Z = np.array([[next(c["measured_m_N"] for c in p2["grid"]
                    if c["N"] == N and c["s"] == s) for s in ss] for N in Ns])
fig, ax = plt.subplots(figsize=(3.3, 2.5))
im = ax.pcolormesh(ss, Ns, Z, shading="nearest", cmap="RdYlBu_r",
                   norm=matplotlib.colors.TwoSlopeNorm(vcenter=1.0))
cs = ax.contour(ss, Ns, Z, levels=[1.0], colors="k", linewidths=1.8)
ax.clabel(cs, fmt={1.0: "stability boundary"}, fontsize=7)
fig.colorbar(im, ax=ax, label=r"measured $m_N$")
ax.set_xlabel(r"shared-model fraction $s$")
ax.set_ylabel(r"firms $N$")
fig.savefig(OUT / "fig_phase.pdf")
plt.close(fig)

# ----------------------------------------------------------------- figure 1b
p3 = load("panel3_cadence")
ss3 = sorted({c["s"] for c in p3["cells"]})
Ks = sorted({c["K"] for c in p3["cells"]})
S = np.array([[next(c["measured_stable"] for c in p3["cells"]
                    if c["s"] == s and c["K"] == K) for K in Ks] for s in ss3])
fig, ax = plt.subplots(figsize=(3.3, 2.5))
ax.pcolormesh(Ks, ss3, S.astype(float), shading="nearest", cmap="RdYlBu",
              vmin=0, vmax=1)
frontier = [next(c["k_max"] for c in p3["cells"] if c["s"] == s) for s in ss3]
ok = [(k, s) for k, s in zip(frontier, ss3) if k is not None]
if ok:
    ax.plot([k for k, _ in ok], [s for _, s in ok], "k-", lw=1.8,
            label=r"predicted $K_{\max}$")
ax.set_xlabel(r"cadence $K$")
ax.set_ylabel(r"shared-model fraction $s$")
# name the two colours, which otherwise carry the panel's whole verdict unlabelled
cmap = matplotlib.colormaps["RdYlBu"]
handles = [matplotlib.patches.Patch(facecolor=cmap(1.0), edgecolor="0.4",
                                    label="measured stable"),
           matplotlib.patches.Patch(facecolor=cmap(0.0), edgecolor="0.4",
                                    label="measured unstable")]
ax.legend(handles=handles + ax.get_legend_handles_labels()[0],
          loc="upper right", framealpha=0.92)
fig.savefig(OUT / "fig_cadence.pdf")
plt.close(fig)

# ----------------------------------------------------------------- figure 2a
p4 = load("panel4_herd_immunity")
fig, ax = plt.subplots(figsize=(3.3, 2.5))
for s_ in p4["series"]:
    ax.plot([p["rho"] for p in s_["points"]],
            [p["measured_radius"] for p in s_["points"]],
            marker="o", ms=2.5, lw=1.1,
            label=f"efficacy {s_['efficacy']:.2f}")
ax.axhline(1.0, ls=":", color="0.35", lw=1)
ax.axvline(p4["rho_star_limit"], ls="--", color="k", lw=1,
           label=r"$\rho_c^*$, perfect correction")
ax.set_xlabel(r"corrected fraction $\rho_c$")
ax.set_ylabel(r"measured $m_N$")
ax.legend(loc="upper right", framealpha=0.9)
fig.savefig(OUT / "fig_herd.pdf")
plt.close(fig)

# ----------------------------------------------------------------- figure 2b
p5 = load("panel5_substitution")
N5 = p5["params"]["N"]
xs = [p["s"] for p in p5["curve"]]
fig, ax = plt.subplots(figsize=(3.3, 2.5))
ax.fill_between(xs, [p["predicted_rho_star"] for p in p5["curve"]], 1.0,
                alpha=0.14, color="tab:blue", label="stable")
ax.plot(xs, [p["predicted_rho_star"] for p in p5["curve"]], "-", lw=1.8,
        label=r"predicted $\rho_c^*(s)$")
ax.step(xs, [p["predicted_threshold_firms"] / N5 for p in p5["curve"]],
        where="mid", lw=1.0, color="tab:green", label="predicted, whole firms")
ax.plot(xs, [p["measured_rho"] for p in p5["curve"]], "o", ms=4.5, mfc="none",
        color="tab:orange", label="measured threshold")
ax.set_xlabel(r"shared-model fraction $s$")
ax.set_ylabel(r"corrected fraction $\rho_c$")
ax.set_ylim(-0.03, 1.0)
ax.legend(loc="upper left", framealpha=0.9)
fig.savefig(OUT / "fig_substitution.pdf")
plt.close(fig)

# ------------------------------------------------------------------ figure 3
p6 = load("panel6_over_adaptation")
p6b = load("panel6b_comparative_statics")
fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.4))
ax = axes[0]
sym = sorted((r for r in p6["rows"]
              if r["chi"] == 1.0 and r["s"] == 1.0 and r["kappa"] == 0.8),
             key=lambda r: r["N"])  # the JSON stores N=1 last; unsorted x draws chords
Ns6 = [r["N"] for r in sym]
ax.plot(Ns6, [r["a_decentralized"] for r in sym], "o-", ms=4,
        label=r"decentralized $a_d$")
ax.plot(Ns6, [r["a_social"] for r in sym], "s-", ms=4,
        label=r"socially optimal $a_s$")
ax.fill_between(Ns6, [r["a_social"] for r in sym],
                [r["a_decentralized"] for r in sym], alpha=0.16,
                color="tab:red", label="over-adaptation")
ax.set_xlabel(r"firms $N$")
ax.set_ylabel(r"aggressiveness $a$")
ax.legend(framealpha=0.9)

ax = axes[1]
ser = p6b["series"]["N"]
xs6 = [p["N"] for p in ser["points"] if p["t_star"] is not None]
ys6 = [p["t_star"] for p in ser["points"] if p["t_star"] is not None]
ax.semilogy(xs6, ys6, "-", lw=1.8, color="tab:purple")
ax.set_xlabel(r"firms $N$")
ax.set_ylabel(r"wedge $t^*$ (log scale)")
fig.tight_layout()
fig.savefig(OUT / "fig_wedge.pdf")
plt.close(fig)

print("wrote 5 figures to", OUT)
