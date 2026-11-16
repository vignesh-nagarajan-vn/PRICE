"""Step 3 of the port: measure the residual from the still-shared channels.

This is the gate the design document puts in front of every heterogeneous panel,
and it is deliberately a separate script from the panels so that its number
exists before any figure does. See
../environment/HETERO-SIMULATOR-PORT-DESIGN.md, "What this does not yet handle",
item 1.

THE QUESTION. The exposure profiles route the informed-intensity channel, and
only that channel. The liquidity field is still driven by total gross flow and
by the tightest dealer's spread across the whole universe, and price impact is
still driven by total net flow. Both stay coupled at R = 1 1' no matter what the
profiles are. At the monoculture that is exactly right, since everything is
shared there anyway. Away from it there is a second coupling channel whose
alignment is 1 1' rather than R, so the measured joint modulus should be
expected to sit ABOVE m_1 * N_eff by a gap that grows with separation from the
monoculture.

WHAT THIS SCRIPT DOES. Sweeps the shared-model fraction s from the monoculture
down to orthogonality at fixed N, using the exact nonnegative constructor
`supply_chain_profiles`, and reports

    gap(s)  =  ( measured m_N  -  m_1 * N_eff(R_measured) ) / ( m_1 * N_eff ) .

s = 1 is the in-sweep control: it must reproduce panel 1's published anchor bit
for bit, because at s = 1 the profiles are flat and the port is the base market.

WHAT IT DOES NOT DO. It draws no figure, wires nothing into panels.py, and moves
no claim in ../../../archive/herd-immunity-v1/writing/CLAIMS-LEDGER.md. If the gap is large the panels are
not interpretable as planned and the design needs revisiting before any figure
is drawn, which is the whole reason this runs first.

    "<base>/.venv/Scripts/python" herd-immunity/ml-contributions/experiments/hetero_channel_residual.py
"""
import json
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "theory"))

import herd_theory as T                                      # noqa: E402
from hetero_simulator_port import (                            # noqa: E402
    PROTOCOL, PUBLISHED, build_port, locate_base, profile_alignment,
    supply_chain_profiles,
)

RESULTS = _HERE / "results"

# n_bonds = 8 and n_sectors = 2 are kept, which is step 1 of the port's brief
# decided in favour of not re-anchoring: panel 1's measured numbers do not
# transfer across a changed BondUniverse, and panel 1 is never cut. So the sweep
# uses free profiles at the existing universe rather than a larger one.
N_BONDS = 8
SWEEP_N = (2, 4)
SWEEP_S = (1.0, 0.9, 0.75, 0.5, 0.25, 0.0)


def main():
    base_root = locate_base()
    if base_root is None:
        print("Base project not found. Set REFLEX_ROOT to its checkout.")
        print("SKIPPED. This is not a failure: the branch repository does not "
              "vendor the simulator.")
        return 0

    pkg = base_root / "endo_market_v4"
    sys.path.insert(0, str(pkg))
    try:
        import torch
        from reflex.config import load_config
        from reflex.equilibrium import interior_probe_config, measure_joint_modulus_sim
    except ImportError as exc:
        print(f"Base project found at {base_root} but not importable: {exc}")
        print("The simulator needs torch. Run this with the base project's venv:")
        print(f'  "{base_root}/.venv/Scripts/python" '
              f'herd-immunity/ml-contributions/experiments/{pathlib.Path(__file__).name}')
        return 0

    Port = build_port(pkg)
    cfg_base = load_config(str(pkg / "configs" / "default.yaml"))
    cfg_base.clients.toxic_spillover = PROTOCOL["kappa"]
    kappa = PROTOCOL["kappa"]

    n_bonds_cfg = None
    m_1 = PUBLISHED[1]["common_measured"]

    print(f"base project: {base_root}")
    print(f"protocol: {PROTOCOL}")
    print(f"m_1 reference (measured, N = 1): {m_1:.6f}")
    print("\nthe question: how far above m_1 * N_eff does the measured modulus "
          "sit, and does\nthe gap grow with separation from the monoculture?\n")

    rows = []
    for N in SWEEP_N:
        cfg = interior_probe_config(cfg_base, N, f_probe=PROTOCOL["probe_feedback"])
        print(f"N = {N}")
        print(f"  {'s':>5} {'lam_max':>8} {'N_eff':>8} {'predicted':>10} "
              f"{'measured':>10} {'gap':>9} {'diff mode':>10} {'clip':>6}")
        for s in SWEEP_S:
            U = supply_chain_profiles(N_BONDS, N, s)
            torch.manual_seed(PROTOCOL["seed"])
            sim = Port(cfg, profiles=U)
            n_bonds_cfg = sim.bonds.n_bonds
            if n_bonds_cfg != N_BONDS:
                raise RuntimeError(
                    f"config has n_bonds = {n_bonds_cfg}, not the {N_BONDS} the "
                    "profiles were built for; the anchor does not transfer "
                    "across a changed BondUniverse")

            R = sim.alignment
            target = (1 - s) * np.eye(N) + s * np.ones((N, N))
            r_err = float(np.abs(R - target).max())
            lam = float(np.linalg.eigvalsh(R).max())
            n_eff = float(T.n_eff(R, kappa))
            predicted = m_1 * n_eff

            res = measure_joint_modulus_sim(
                cfg, h_ref=PROTOCOL["h_ref"], seed=PROTOCOL["seed"],
                n_episodes=PROTOCOL["episodes"], simulator=sim,
            )
            measured = float(res.modulus_common)
            gap = (measured - predicted) / predicted

            rows.append({
                "N": N, "s": s,
                "alignment_construction_error": r_err,
                "lambda_max": lam, "n_eff": n_eff,
                "m_1_reference": m_1,
                "predicted_m_N": predicted,
                "measured_m_N": measured,
                "relative_gap": gap,
                "measured_differential": float(res.modulus_differential),
                "br_clipped": bool(res.br_clipped),
            })
            print(f"  {s:>5.2f} {lam:>8.4f} {n_eff:>8.4f} {predicted:>10.6f} "
                  f"{measured:>10.6f} {gap:>+9.2%} "
                  f"{res.modulus_differential:>10.2e} "
                  f"{str(res.br_clipped):>6}")
        print()

    # The in-sweep control. At s = 1 the profiles are flat, so the port is the
    # base market and must reproduce the published anchor bit for bit. A sweep
    # whose own monoculture end has drifted says nothing about its other end.
    control_ok = True
    for N in SWEEP_N:
        if N not in PUBLISHED:
            continue
        row = next(r for r in rows if r["N"] == N and r["s"] == 1.0)
        rel = abs(row["measured_m_N"] - PUBLISHED[N]["common_measured"]) \
            / PUBLISHED[N]["common_measured"]
        ok = rel < 1e-6
        control_ok &= ok
        print(f"control: N = {N}, s = 1 reproduces the published anchor "
              f"{PUBLISHED[N]['common_measured']:.6f} to {rel:.2e}: {ok}")

    # Does the gap grow with separation, as the shared-channel argument predicts?
    summary = {}
    for N in SWEEP_N:
        g = [r["relative_gap"] for r in rows if r["N"] == N]
        s_vals = [r["s"] for r in rows if r["N"] == N]
        summary[N] = {
            "gap_at_monoculture": g[0],
            "gap_at_orthogonal": g[-1],
            "max_abs_gap": max(abs(x) for x in g),
            "monotone_in_separation": all(
                b >= a - 1e-9 for a, b in zip(g, g[1:])),
            "s_grid": s_vals,
            "gaps": g,
        }
        print(f"\nN = {N}: gap {g[0]:+.2%} at the monoculture, {g[-1]:+.2%} at "
              f"orthogonality, largest {max(abs(x) for x in g):.2%}")
        print(f"        grows monotonically with separation: "
              f"{summary[N]['monotone_in_separation']}")

    worst = max(s_["max_abs_gap"] for s_ in summary.values())
    print(f"\nlargest residual anywhere on the sweep: {worst:.2%}")

    out = {
        "panel": "port step 3: residual from the still-shared liquidity and "
                 "price-impact channels",
        "status": "NOT A PANEL AND NOT A CLAIM. This is the gate the port "
                  "design puts in front of every heterogeneous panel. No ledger "
                  "entry changes status on the strength of it.",
        "base_project": base_root.name,  # leaf only: the absolute path carries a username
        "protocol": PROTOCOL,
        "universe": {"n_bonds": n_bonds_cfg,
                     "decision": "kept at 8 rather than enlarged, so panel 1's "
                                 "anchor still transfers"},
        "m_1_reference": m_1,
        "rows": rows,
        "summary": {str(k): v for k, v in summary.items()},
        "monoculture_control_reproduces_anchor": bool(control_ok),
        "largest_residual": worst,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "hetero_channel_residual.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {RESULTS / 'hetero_channel_residual.json'}")

    if not control_ok:
        print("\nFAILED. The monoculture end of the sweep does not reproduce "
              "the published\nanchor, so nothing at the other end is "
              "interpretable. Do not draw a figure.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
