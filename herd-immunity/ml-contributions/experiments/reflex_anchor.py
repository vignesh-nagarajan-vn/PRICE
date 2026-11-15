"""Panel 1's external anchor, measured in the base project's real simulator.

This is the one panel that does NOT need the heterogeneous-response extension.
Its claim is the monoculture corner `R = 1 1'`, which the base project already
implements and has already validated, so the anchor can be closed today while
the rest of the simulator port is still design work.

WHAT MAKES THIS DIFFERENT FROM THE OTHER PANELS. Everything in `panels.py` runs
in the linearized reference environment and is flagged `[DRY RUN]`. This script
runs the genuine shared-pool market: real order flow, real spreads, real
inventory, real liquidity feedback, CRN probes through the full
deploy-collect-fit-optimize pipeline. A number that comes out of here is
`[MEASURED]`.

WHAT IT DOES NOT TOUCH. The base project is read-only here. Nothing is imported
that this script writes to, no file under the base repository is modified, and
the base project's own guidance is that derived papers build on it rather than
live inside it. If the base repository is absent this script skips cleanly, so
the branch repository stays self-contained for anyone without a local checkout.

    python herd-immunity/ml-contributions/experiments/reflex_anchor.py

Requires the base project's virtual environment, since the simulator needs
torch and the branch repository's own code is numpy-only:

    "<base>/.venv/Scripts/python" herd-immunity/ml-contributions/experiments/reflex_anchor.py

Point at a non-default checkout with the REFLEX_ROOT environment variable.
"""
import json
import os
import pathlib
import sys

_BRANCH = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BRANCH / "theory"))
import herd_theory as T                                     # noqa: E402

RESULTS = pathlib.Path(__file__).resolve().parent / "results"

# The published values this anchor exists to reproduce, from the base project's
# 07-12-2026 paper-grade run. Amplification is the ratio of measured
# common-mode moduli against the single-dealer measurement.
PUBLISHED = {
    1: {"common_measured": 0.785600462590498, "amplification": 1.0},
    2: {"common_measured": 1.3691618268039063, "amplification": 1.74},
    3: {"common_measured": 2.479927444224721, "amplification": 3.16},
}

# The protocol the published run used. These are not free parameters: the
# default config's feedback gain rails the best response at the spread cap for
# N >= 2, and multi-dealer runs must scale the liquidity boost down per the
# environment's documented guidance. Both are handled by interior_probe_config.
#
# episodes = 8 is the paper-grade profile, NOT the experiment's own default of
# 4. Running at 4 lands within a few percent and looks right, which is exactly
# why it is worth pinning: it reproduces 1.80x at N = 2 against the published
# 1.74x, and a reader comparing those would conclude the law fits worse than it
# does. The number of probe episodes is part of the protocol.
PROTOCOL = {"kappa": 1.0, "probe_feedback": 0.5, "h_ref": 1.0,
            "seed": 0, "episodes": 8}


def locate_base():
    """Find the base project, or return None if it is not available here."""
    env = os.environ.get("REFLEX_ROOT")
    candidates = [pathlib.Path(env)] if env else []
    candidates.append(_BRANCH.parents[2] / "REFLEX")
    for c in candidates:
        if (c / "endo_market_v4" / "reflex").is_dir():
            return c
    return None


def main():
    base_root = locate_base()
    if base_root is None:
        print("Base project not found. Set REFLEX_ROOT to its checkout, or run "
              "this from a machine that has one.")
        print("SKIPPED. This is not a failure: the branch repository does not "
              "vendor the simulator.")
        return 0

    pkg = base_root / "endo_market_v4"
    sys.path.insert(0, str(pkg))
    try:
        from reflex.config import load_config
        from reflex.equilibrium import interior_probe_config, measure_joint_modulus_sim
        from reflex.theory.multi_dealer import n_eff as base_n_eff
    except ImportError as exc:
        print(f"Base project found at {base_root} but not importable: {exc}")
        print("The simulator needs torch. Run this with the base project's venv:")
        print(f'  "{base_root}/.venv/Scripts/python" {pathlib.Path(__file__).name}')
        return 0

    print(f"base project: {base_root}")
    print(f"protocol: {PROTOCOL}\n")

    cfg_base = load_config(str(pkg / "configs" / "default.yaml"))
    cfg_base.clients.toxic_spillover = PROTOCOL["kappa"]

    rows, m1_ref = [], None
    for N in (1, 2, 3):
        cfg = interior_probe_config(cfg_base, N, f_probe=PROTOCOL["probe_feedback"])
        res = measure_joint_modulus_sim(
            cfg, h_ref=PROTOCOL["h_ref"], seed=PROTOCOL["seed"],
            n_episodes=PROTOCOL["episodes"],
        )
        if N == 1:
            m1_ref = res.modulus_common

        # The branch paper's prediction, computed from ITS OWN theory module at
        # the monoculture corner, not from the base project's n_eff. The two
        # agreeing is the point: two independently written implementations of
        # the same law.
        branch_n_eff = T.n_eff(T.monoculture_R(N), PROTOCOL["kappa"])
        base_ne = base_n_eff(N, PROTOCOL["kappa"])

        rows.append({
            "N": N,
            "measured_common_modulus": float(res.modulus_common),
            "measured_amplification": float(res.modulus_common / m1_ref),
            "branch_predicted_n_eff": float(branch_n_eff),
            "base_predicted_n_eff": float(base_ne),
            "predicted_common_modulus": float(branch_n_eff * m1_ref),
            "measured_differential": float(res.modulus_differential),
            "br_clipped": bool(res.br_clipped),
            "published_common_measured": PUBLISHED[N]["common_measured"],
            "published_amplification": PUBLISHED[N]["amplification"],
        })

    print(f"{'N':>2} {'measured m_N':>13} {'predicted':>10} {'amplification':>14} "
          f"{'published':>10} {'rel err':>9} {'clipped':>8}")
    reproduced = True
    for r in rows:
        rel = abs(r["measured_common_modulus"] - r["published_common_measured"]) \
            / max(r["published_common_measured"], 1e-12)
        if rel > 1e-6:
            reproduced = False
        print(f"{r['N']:>2} {r['measured_common_modulus']:>13.6f} "
              f"{r['predicted_common_modulus']:>10.4f} "
              f"{r['measured_amplification']:>14.4f} "
              f"{r['published_amplification']:>10.2f} {rel:>9.2e} "
              f"{str(r['br_clipped']):>8}")

    n_eff_agree = all(abs(r["branch_predicted_n_eff"] - r["base_predicted_n_eff"]) < 1e-12
                      for r in rows)
    print(f"\nbranch theory module and base project agree on N_eff: {n_eff_agree}")
    print(f"published values reproduced bit for bit: {reproduced}")
    # N = 1 has no differential mode, so its entry is nan by construction.
    diffs = [abs(r["measured_differential"]) for r in rows
             if r["N"] > 1 and r["measured_differential"] == r["measured_differential"]]
    print(f"differential mode at kappa = 1 (theory says 0): "
          f"{max(diffs):.2e}" if diffs else "differential mode: not measured")

    gaps = {r["N"]: abs(r["measured_amplification"] - r["branch_predicted_n_eff"])
            / r["branch_predicted_n_eff"] for r in rows if r["N"] > 1}
    print("\ngap between the measured market and the linear prediction:")
    for N, g in gaps.items():
        print(f"  N={N}: {100*g:.1f}%  "
              f"(measured {rows[N-1]['measured_amplification']:.3f} against "
              f"predicted {rows[N-1]['branch_predicted_n_eff']:.1f})")
    print("\nThat gap is the paper's honest content, not an error. The "
          "prediction is a\nlinearization; the market is nonlinear and its flow "
          "saturates. The reference\nenvironment reproduces the prediction "
          "exactly BECAUSE it omits both.")

    out = {
        "panel": "1. amplification replication, external anchor",
        "status": "MEASURED, in the base project's genuine shared-pool market",
        "base_project": base_root.name,  # leaf only: the absolute path carries a username
        "protocol": PROTOCOL,
        "rows": rows,
        "published_reproduced_exactly": reproduced,
        "branch_and_base_n_eff_agree": n_eff_agree,
        "max_relative_gap_to_linear_prediction": max(gaps.values()) if gaps else None,
        "note": "The gap to the linear prediction is nonlinearity and flow "
                "saturation, which the linearized reference environment does "
                "not model. Panels 2 to 5 remain DRY RUN.",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "panel1_external_anchor.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {RESULTS / 'panel1_external_anchor.json'}")

    if not reproduced:
        print("\nWARNING: the published values did not reproduce. Investigate "
              "before quoting either set.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
