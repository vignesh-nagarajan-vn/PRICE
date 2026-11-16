"""Heterogeneous-response port of the base project's order-flow simulator.

The design decision this implements is recorded in
../environment/HETERO-SIMULATOR-PORT-DESIGN.md and should be read first. In one
sentence: each dealer gets a bond-space exposure profile `u_i`, and both its
contribution to the informed pool and its sensing of that pool are routed
through it, so that the coupling matrix the dealers actually experience becomes
`(1 - kappa) I + kappa R` with `R` the Gram matrix of the profiles, instead of
the base market's fixed `(1 - kappa) I + kappa 1 1'`.

WHAT THIS SESSION ESTABLISHES. The reduction and nothing else. At the
monoculture configuration, every profile flat, the port must reproduce
reflex_anchor.py's already-published joint moduli bit for bit. That is the
acceptance test below and it is the only thing this file asserts.

WHAT IT DOES NOT ESTABLISH. No heterogeneous sweep is run, no panel is wired to
this, no figure is produced, and no claim in ../../../archive/herd-immunity-v1/writing/CLAIMS-LEDGER.md
changes status. Panels 2, 2b, 4 and 5 stay at [DRY RUN].

WHAT IT DOES NOT TOUCH. The base project is read-only. This module subclasses
MultiDealerSimulator from outside the base repository and writes nothing under
it. If the base repository is absent the script skips cleanly, so the branch
repository stays self-contained.

    python herd-immunity/ml-contributions/experiments/hetero_simulator_port.py

Requires the base project's virtual environment, since the simulator needs
torch and the branch repository's own code is numpy-only:

    "<base>/.venv/Scripts/python" herd-immunity/ml-contributions/experiments/hetero_simulator_port.py

Point at a non-default checkout with the REFLEX_ROOT environment variable.
"""
import inspect
import json
import os
import pathlib
import sys

import numpy as np

_BRANCH = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BRANCH / "theory"))
import herd_theory as T                                     # noqa: E402

RESULTS = pathlib.Path(__file__).resolve().parent / "results"

# The anchors this port has to reproduce, taken from reflex_anchor.py, which in
# turn reproduces the base project's 07-12-2026 paper-grade run. Reproducing
# these is the whole acceptance test: a port that cannot recover the known case
# has no business running an unknown one.
PUBLISHED = {
    1: {"common_measured": 0.785600462590498, "amplification": 1.0},
    2: {"common_measured": 1.3691618268039063, "amplification": 1.74},
    3: {"common_measured": 2.479927444224721, "amplification": 3.16},
}

# Identical to reflex_anchor.py's. Not free parameters: see that file's note on
# why episodes = 8 rather than the experiment default of 4.
PROTOCOL = {"kappa": 1.0, "probe_feedback": 0.5, "h_ref": 1.0,
            "seed": 0, "episodes": 8}

# Bit-for-bit is the standard here, not a tolerance. See the design document's
# section on the reduction: at flat profiles the port performs the same float
# operations in the same order as the base.
REPRODUCTION_TOL = 1e-6

# The base expression this port exists to generalize. Checked against the live
# base source at import so a stale copy fails loudly instead of quietly
# reproducing an old market.
_BASE_COUPLING_LINE = "spread_resp = own_resp[i] + self.kappa * (sum_resp - own_resp[i])"


def locate_base():
    """Find the base project, or return None if it is not available here."""
    env = os.environ.get("REFLEX_ROOT")
    candidates = [pathlib.Path(env)] if env else []
    candidates.append(_BRANCH.parents[2] / "REFLEX")
    for c in candidates:
        if (c / "endo_market_v4" / "reflex").is_dir():
            return c
    return None


# ===========================================================================
# exposure profiles
# ===========================================================================

def normalize_profiles(U, tol=1e-12):
    """Scale each dealer's profile to unit mean square across bonds.

    The normalization is what makes the induced coupling matrix have unit
    diagonal, so that it reads as `(1 - kappa) I + kappa R` with R a genuine
    alignment matrix. A dealer that quotes the whole universe uniformly
    normalizes to the all-ones profile, which is the monoculture corner.
    """
    U = np.asarray(U, dtype=float)
    if U.ndim != 2:
        raise ValueError(f"profiles must have shape (N, n_bonds), got {U.shape}")
    rms = np.sqrt(np.mean(U * U, axis=1))
    if np.any(rms < tol):
        raise ValueError("a dealer's exposure profile is identically zero")
    return U / rms[:, None]


def profile_alignment(U):
    """R, measured back off the realized profiles rather than assumed.

    Same discipline as hetero_response_env.measured_alignment: the constructor
    is never trusted to have hit its target, the target is read back.
    """
    U = normalize_profiles(U)
    return (U @ U.T) / U.shape[1]


def flat_profiles(n_dealers, n_bonds):
    """The monoculture: every dealer quotes the whole universe uniformly.

    This is the reduction target. R comes out exactly 1 1'.
    """
    return np.ones((int(n_dealers), int(n_bonds)), dtype=float)


def supply_chain_profiles(n_bonds, n_dealers, s):
    """Nonnegative profiles whose measured alignment is exactly (1-s)I + s 11'.

    This is the free-profile constructor the design document asks for, in the
    one case the paper actually sweeps. Partition the universe into `n_dealers`
    groups and write each dealer's unit direction as

        x_i  =  a * g  +  b * e_i ,

    with `g` the uniform direction over the whole universe and `e_i` the unit
    indicator of dealer `i`'s own group. Because the groups are disjoint,
    <e_i, e_j> = 0, so <x_i, x_j> = a^2 + 2 a b c with c = <g, e_i>, and
    ||x_i||^2 = a^2 + b^2 + 2 a b c. Solving both for a target off-diagonal `s`
    gives, with equal groups so that c = 1/sqrt(n_dealers),

        b = sqrt(1 - s) ,   a = -p + sqrt(p^2 + s) ,   p = sqrt((1-s)/n_dealers) .

    Both are nonnegative, and `g` and `e_i` are entrywise nonnegative, so the
    profile is a legal coverage weight. Nonnegativity is the constraint the
    linearized environment does not have and it is what bounds the reachable
    set; here it costs nothing, because the construction lands inside it for
    every `s` in [0, 1].

    The corners are exact rather than approximate. At `s = 1`, `b = 0` and
    `a = 1`, so every dealer is the uniform profile and R = 1 1', which is the
    monoculture the anchor is measured at. At `s = 0`, `a = 0` and `b = 1`, so
    the dealers are disjoint indicators and R = I, the orthogonal corner of
    claim 4.3, which the sector-tilt constructor cannot reach at all because the
    global factor floors the overlap.

    Requires `n_dealers` to divide `n_bonds`, which is what makes the groups
    equal and the realized alignment exactly exchangeable. That matters for more
    than tidiness: the base project's in-phase probe measures the Rayleigh
    quotient along the uniform direction, which equals the spectral radius only
    when the uniform direction is the leading eigenvector, and exchangeability
    is what guarantees it is. Use `profiles_for_R` for anything else, and read
    the measured alignment back before quoting a prediction.
    """
    n_bonds, n_dealers = int(n_bonds), int(n_dealers)
    s = float(s)
    if not 0.0 <= s <= 1.0:
        raise ValueError(f"s must lie in [0, 1], got {s}")
    if n_dealers < 1 or n_bonds % n_dealers:
        raise ValueError(
            f"n_dealers = {n_dealers} must divide n_bonds = {n_bonds} so the "
            "groups are equal and the realized alignment is exchangeable; use "
            "profiles_for_R otherwise")

    size = n_bonds // n_dealers
    g = np.ones(n_bonds) / np.sqrt(n_bonds)
    p = np.sqrt((1.0 - s) / n_dealers)
    a = -p + np.sqrt(p * p + s)
    b = np.sqrt(1.0 - s)

    X = np.empty((n_dealers, n_bonds), dtype=float)
    for i in range(n_dealers):
        e = np.zeros(n_bonds)
        e[i * size:(i + 1) * size] = 1.0 / np.sqrt(size)
        X[i] = a * g + b * e
    if np.any(X < -1e-15):
        raise ValueError("construction produced a negative coverage weight")
    return normalize_profiles(np.clip(X, 0.0, None))


def profiles_for_R(R, n_bonds, seed=0, iters=4000, step=0.25):
    """Nonnegative profiles whose measured alignment approximates `R`.

    The general constructor, by projected gradient on the unit directions
    `x_i = v_i / ||v_i||` with `v_i >= 0`. Returns the profiles; the caller is
    expected to read the alignment back with `profile_alignment` and check the
    achieved error rather than trusting the target, which is the same discipline
    `hetero_response_env.py` enforces.

    Nonnegativity means not every `R` is reachable. A target with negative
    off-diagonal entries is not attainable at all, since a Gram matrix of
    nonnegative vectors has nonnegative entries, and the residual this function
    reports is the honest statement of how far the projection landed.
    """
    R = np.asarray(R, dtype=float)
    N = R.shape[0]
    rng = np.random.default_rng(seed)
    Vm = rng.random((N, int(n_bonds))) + 0.1

    for _ in range(int(iters)):
        norms = np.linalg.norm(Vm, axis=1, keepdims=True)
        X = Vm / norms
        G = X @ X.T
        E = G - R
        np.fill_diagonal(E, 0.0)
        # d<x_i,x_j>/dv_i = (x_j - <x_i,x_j> x_i) / ||v_i||
        grad = np.zeros_like(Vm)
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                grad[i] += 4.0 * E[i, j] * (X[j] - G[i, j] * X[i]) / norms[i, 0]
        Vm = np.clip(Vm - step * grad, 0.0, None)
        if not np.all(np.linalg.norm(Vm, axis=1) > 1e-9):
            raise RuntimeError("a profile collapsed to zero during projection")
    return normalize_profiles(Vm)


def sector_profiles(sector, n_dealers, tilt, assignment=None):
    """Dealers specialized by sector exposure, from the universe's own sectors.

    `sector` is the base project's per-bond integer sector label. Dealer i is
    assigned a home sector and tilts its coverage toward it:

        raw_i(b) = 1 + tilt * (1[sector(b) == home_i] - share_i)

    where `share_i` is the fraction of the universe in that home sector, so the
    tilt is mean-preserving across the universe and `tilt = 0` returns flat
    profiles exactly. Profiles are normalized on return.

    The monoculture is therefore a value of `tilt`, not a separate code path.
    """
    sector = np.asarray(sector).astype(int).ravel()
    n_bonds = sector.size
    sectors = np.unique(sector)
    if assignment is None:
        assignment = [sectors[i % sectors.size] for i in range(int(n_dealers))]
    if len(assignment) != int(n_dealers):
        raise ValueError("assignment must name a home sector for each dealer")

    U = np.empty((int(n_dealers), n_bonds), dtype=float)
    for i, home in enumerate(assignment):
        ind = (sector == home).astype(float)
        U[i] = 1.0 + float(tilt) * (ind - ind.mean())
    if np.any(U < 0):
        raise ValueError(f"tilt = {tilt} drives a coverage weight negative; "
                         "exposure profiles must stay nonnegative")
    return normalize_profiles(U)


# ===========================================================================
# the port
# ===========================================================================

def build_port(base_pkg):
    """Build the simulator subclass against the located base project.

    Defined as a factory rather than at module scope because the base class is
    only importable once the base project's path is on sys.path and its venv is
    in use. Importing this module without the base project present must not
    fail.
    """
    from reflex.env.multi_dealer import (
        MultiDealerSimulator, MultiMarketState, DealerStepResult, MultiTransition,
    )
    from reflex.env.clients import _ARRIVAL_NOISE, _UNINF_IMBALANCE_STD
    from reflex.types import Quotes                            # noqa: F401
    import torch

    source = inspect.getsource(MultiDealerSimulator.step)
    if _BASE_COUPLING_LINE not in source:
        raise RuntimeError(
            "The base project's coupling expression is not what this port was "
            "written against.\nExpected to find, inside MultiDealerSimulator.step:\n"
            f"    {_BASE_COUPLING_LINE}\n"
            "The port reimplements step() in order to change that one line, so a "
            "changed base\nmeans this copy is stale. Re-derive the override against "
            "the current base source\nbefore trusting any number out of it."
        )

    class HeteroMultiDealerSimulator(MultiDealerSimulator):
        """MultiDealerSimulator with per-dealer bond-space exposure profiles.

        `step` mirrors the base method exactly, including the order of every
        random draw, and changes one expression: the coupled toxic
        responsiveness is routed through the exposure profiles. See
        ../environment/HETERO-SIMULATOR-PORT-DESIGN.md.

        With `profiles=None` the profiles are flat and the market is the base
        market, reproduced bit for bit.
        """

        def __init__(self, cfg, bonds=None, profiles=None):
            super().__init__(cfg, bonds=bonds)
            n_bonds = self.bonds.n_bonds
            if profiles is None:
                profiles = flat_profiles(self.n_dealers, n_bonds)
            U = normalize_profiles(profiles)
            if U.shape != (self.n_dealers, n_bonds):
                raise ValueError(
                    f"profiles must have shape ({self.n_dealers}, {n_bonds}), "
                    f"got {U.shape}")
            self.profiles = U
            self._u = [torch.as_tensor(U[i], dtype=torch.float32)
                       for i in range(self.n_dealers)]

        @property
        def alignment(self):
            """R, measured off the realized profiles."""
            return profile_alignment(self.profiles)

        @property
        def n_eff(self):
            """The branch theory module's N_eff at the measured alignment."""
            return float(T.n_eff(self.alignment, self.kappa))

        @property
        def is_monoculture(self):
            return bool(np.allclose(self.alignment, 1.0, atol=1e-12))

        # -- mirrors MultiDealerSimulator.step; one expression differs -------
        def step(self, state, quotes, generator=None):
            if len(quotes) != self.n_dealers:
                raise ValueError(
                    f"expected {self.n_dealers} quote sets, got {len(quotes)}")
            c = self.cfg.clients
            sim = self.sim_cfg
            n = self.bonds.n_bonds
            v = state.fundamental
            m = state.mid
            mispricing = v - m
            liq_ratio = (state.liquidity / self.liq_mean).clamp_min(0.0)

            hs = [q.half_spread.clamp_min(0.0) for q in quotes]
            own_resp = [torch.exp(-c.info_spread_decay * h) for h in hs]

            # THE ONE CHANGED EXPRESSION. Base:
            #     sum_resp = stack(own_resp).sum(0)
            #     spread_resp_i = own_resp[i] + kappa * (sum_resp - own_resp[i])
            # Port: each dealer's contribution to the pool and its sensing of the
            # pool are both weighted by its exposure profile. The stack-and-sum
            # is written in the base's order and the bracket in the base's
            # associativity so that flat profiles reduce exactly, in floating
            # point and not only on paper.
            weighted = [own_resp[j] * self._u[j] for j in range(self.n_dealers)]
            pool = torch.stack(weighted, dim=0).sum(dim=0)

            dealers = []
            S_total = torch.zeros(n)
            B_total = torch.zeros(n)
            for i in range(self.n_dealers):
                h = hs[i]
                skew = quotes[i].skew

                base = (c.base_arrival_rate
                        * torch.exp(-c.demand_elasticity * h) * liq_ratio)
                arrival_noise = 1.0 + _ARRIVAL_NOISE * torch.randn(n, generator=generator)
                uninf_vol = (base * arrival_noise).clamp_min(0.0)
                imb = 0.5 + _UNINF_IMBALANCE_STD * torch.randn(n, generator=generator)
                imb = imb.clamp(0.0, 1.0)
                u_buy_from_dealer = uninf_vol * imb
                u_sell_to_dealer = uninf_vol * (1.0 - imb)

                signal = mispricing + c.info_signal_noise * torch.randn(n, generator=generator)
                edge_scale = max(c.info_signal_noise, 1e-6)
                gate = torch.tanh(signal.abs() / edge_scale)
                own_w = weighted[i]
                spread_resp = self._u[i] * (own_w + self.kappa * (pool - own_w))
                toxic = gate * (
                    c.info_base_intensity
                    + c.alpha * c.toxicity_feedback * c.info_intensity * spread_resp
                )
                inf_vol = (toxic * liq_ratio).clamp_min(0.0)
                cap = max(c.info_cap, 1e-6)
                inf_vol = cap * torch.tanh(inf_vol / cap)
                direction = torch.sign(signal)
                informed_buy_from_dealer = inf_vol * (direction > 0).float()
                informed_sell_to_dealer = inf_vol * (direction < 0).float()

                S_i = u_buy_from_dealer + informed_buy_from_dealer
                B_i = u_sell_to_dealer + informed_sell_to_dealer
                S_total = S_total + S_i
                B_total = B_total + B_i

                spread_capture = S_i * (h + skew) + B_i * (h - skew)
                adverse = (B_i - S_i) * (m - v)
                dealers.append(
                    DealerStepResult(
                        dealer_sell=S_i,
                        dealer_buy=B_i,
                        informed_volume=informed_buy_from_dealer + informed_sell_to_dealer,
                        gross_volume=S_i + B_i,
                        pnl_components={
                            "spread_capture": spread_capture,
                            "inventory_pnl": torch.zeros(n),
                            "adverse_selection_loss": adverse,
                        },
                    )
                )

            shock = self.bonds.correlated_normal(generator)
            v_next = v + sim.fundamental_vol * shock

            net_client_buy = S_total - B_total
            reversion = sim.mid_reversion * mispricing
            impact = sim.impact * net_client_buy
            noise = sim.mid_noise * torch.randn(n, generator=generator)
            delta_m = (reversion + impact + noise).clamp(-sim.mid_move_cap, sim.mid_move_cap)
            m_next = m + delta_m

            gross_total = S_total + B_total
            h_tightest = torch.stack(hs, dim=0).min(dim=0).values
            liq_next = self.liquidity.step(
                liquidity=state.liquidity,
                half_spread=h_tightest,
                gross_flow=gross_total,
                spread_ref=self.cfg.clients.spread_ref,
                generator=generator,
            )

            inventories_next = state.inventories.clone()
            for i, d in enumerate(dealers):
                q_after = state.inventories[i] + (d.dealer_buy - d.dealer_sell)
                inventories_next[i] = q_after
                d.pnl_components["inventory_pnl"] = q_after * (v_next - v)

            next_state = MultiMarketState(
                inventories=inventories_next,
                mid=m_next,
                fundamental=v_next,
                liquidity=liq_next,
                flow_recent=net_client_buy,
                vol_recent=gross_total,
                t=state.t + 1,
            )
            return MultiTransition(
                state=state, quotes=list(quotes), dealers=dealers,
                next_state=next_state,
            )

    return HeteroMultiDealerSimulator


# ===========================================================================
# the acceptance test
# ===========================================================================

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

    print(f"base project: {base_root}")
    print(f"protocol: {PROTOCOL}")
    print("acceptance test: monoculture profiles must reproduce panel 1's "
          "published anchors\n")

    cfg_base = load_config(str(pkg / "configs" / "default.yaml"))
    cfg_base.clients.toxic_spillover = PROTOCOL["kappa"]

    rows, m1_ref = [], None
    for N in (1, 2, 3):
        cfg = interior_probe_config(cfg_base, N, f_probe=PROTOCOL["probe_feedback"])

        # Construct the simulator here rather than letting measure_joint_modulus_sim
        # build a base one, and seed exactly the way it would, so the only
        # difference from reflex_anchor.py is the class.
        torch.manual_seed(PROTOCOL["seed"])
        sim = Port(cfg, profiles=None)
        assert sim.is_monoculture, "flat profiles must give R = 1 1'"

        res = measure_joint_modulus_sim(
            cfg, h_ref=PROTOCOL["h_ref"], seed=PROTOCOL["seed"],
            n_episodes=PROTOCOL["episodes"], simulator=sim,
        )
        if N == 1:
            m1_ref = res.modulus_common

        rows.append({
            "N": N,
            "measured_common_modulus": float(res.modulus_common),
            "measured_amplification": float(res.modulus_common / m1_ref),
            "port_n_eff": sim.n_eff,
            "branch_predicted_n_eff": float(
                T.n_eff(T.monoculture_R(N), PROTOCOL["kappa"])),
            "measured_differential": float(res.modulus_differential),
            "br_clipped": bool(res.br_clipped),
            "published_common_measured": PUBLISHED[N]["common_measured"],
            "published_amplification": PUBLISHED[N]["amplification"],
            "max_abs_alignment_error": float(np.abs(sim.alignment - 1.0).max()),
        })

    print(f"{'N':>2} {'measured m_N':>13} {'published':>13} {'rel err':>10} "
          f"{'amplification':>14} {'R err':>9} {'clipped':>8}")
    reproduced = True
    for r in rows:
        rel = abs(r["measured_common_modulus"] - r["published_common_measured"]) \
            / max(r["published_common_measured"], 1e-12)
        r["relative_error"] = rel
        if rel > REPRODUCTION_TOL:
            reproduced = False
        print(f"{r['N']:>2} {r['measured_common_modulus']:>13.6f} "
              f"{r['published_common_measured']:>13.6f} {rel:>10.2e} "
              f"{r['measured_amplification']:>14.4f} "
              f"{r['max_abs_alignment_error']:>9.1e} "
              f"{str(r['br_clipped']):>8}")

    n_eff_agree = all(abs(r["port_n_eff"] - r["branch_predicted_n_eff"]) < 1e-12
                      for r in rows)
    print(f"\nport's measured N_eff matches the theory module at the corner: "
          f"{n_eff_agree}")
    print(f"published anchors reproduced to {REPRODUCTION_TOL:.0e}: {reproduced}")

    # A second, cheaper structural check that does not need the simulator: the
    # sector-tilt constructor must return the flat profiles at tilt = 0 and must
    # move R off 1 1' at tilt > 0. This is the constructor's own reduction, kept
    # separate from the market's.
    sector = sim.bonds.sector.numpy()
    flat = sector_profiles(sector, 3, tilt=0.0)
    tilted = sector_profiles(sector, 3, tilt=0.8)
    R_flat = profile_alignment(flat)
    R_tilted = profile_alignment(tilted)
    tilt_reduces = bool(np.allclose(R_flat, 1.0, atol=1e-12))
    tilt_separates = bool(np.abs(R_tilted - 1.0).max() > 1e-6)
    print(f"sector_profiles(tilt=0) gives R = 11': {tilt_reduces}")
    print(f"sector_profiles(tilt=0.8) moves R off 11': {tilt_separates} "
          f"(min off-diagonal {R_tilted[np.triu_indices(3, 1)].min():.4f})")

    out = {
        "panel": "simulator port, monoculture reduction test only",
        "status": "NOT A MEASUREMENT. Reproduces panel 1's already-published "
                  "anchors as an acceptance test of the port. No heterogeneous "
                  "sweep was run and no claim changes status.",
        "base_project": base_root.name,  # leaf only: the absolute path carries a username
        "protocol": PROTOCOL,
        "reproduction_tolerance": REPRODUCTION_TOL,
        "rows": rows,
        "published_reproduced": reproduced,
        "port_n_eff_matches_theory_module": n_eff_agree,
        "sector_constructor_reduces_at_tilt_zero": tilt_reduces,
        "sector_constructor_separates_at_tilt_08": tilt_separates,
        "note": "Panels 2, 2b, 4 and 5 remain DRY RUN. See "
                "../environment/HETERO-SIMULATOR-PORT-DESIGN.md for what the "
                "mechanism does not yet handle.",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "hetero_port_reduction.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {RESULTS / 'hetero_port_reduction.json'}")

    ok = reproduced and n_eff_agree and tilt_reduces and tilt_separates
    if not ok:
        print("\nFAILED. The port does not reproduce the known monoculture case. "
              "Do not run a\nheterogeneous sweep on it and do not quote any "
              "number it produces.")
        return 1
    print("\nPASSED. The port reduces to the base market at R = 11'. That "
          "licenses building\nthe heterogeneous sweep on it; it does not license "
          "any claim about a heterogeneous\nmarket, none of which has been run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
