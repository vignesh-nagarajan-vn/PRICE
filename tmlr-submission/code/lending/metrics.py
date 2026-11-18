"""Outcome measures for one simulated run."""
import numpy as np


def window_means(x, n, v, W):
    """Quote-weighted mean of v over W equal windows of the horizon (blocks split across window edges)."""
    T = n.sum()
    edges = np.linspace(0, T, W + 1)
    ends = np.cumsum(n)
    starts = ends - n
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        w = np.clip(np.minimum(ends, hi) - np.maximum(starts, lo), 0, None)
        out.append(float(np.sum(w * v) / max(np.sum(w), 1)))
    return out


def summarize(market, b0, ell, res):
    x = np.array([r for r, n in res["served"]], float)
    n = np.array([n for r, n in res["served"]], float)
    T = n.sum()
    phi, phi0, phis = market.phi(x), float(market.phi(b0)), market.phi_star
    out = dict(
        final_rate=float(res["final"]),
        final_of_opt=float(market.phi(res["final"]) / phis),            # profit of the final rate / optimum
        start_of_opt=phi0 / phis,
        avg_of_opt=float(np.sum(n * phi) / T / phis),                    # average profit per quote / optimum
        net_gain=float(np.sum(n * (phi - phi0)) / (T * phi0)),           # vs never changing the rate
        over_budget=float(np.sum(n[phi < phi0 - ell - 1e-12]) / T),      # quotes losing more than ell vs b0
        worst_loss=float(max(0.0, (phi0 - phi.min()) / phi0)),
        above_start=float(np.sum(n[x > b0 + 1e-9]) / T),                # quotes above the starting rate
        final_worse=bool(market.phi(res["final"]) < phi0 - 1e-12),
        path=window_means(x, n, phi / phis, 10),                         # profit / optimum in 10 windows
    )
    if "moves" in res:
        mv = res["moves"]
        out["harmful_moves"] = int(sum(market.phi(b) < market.phi(a) for _, a, b in mv))
        out["n_moves"] = len(mv)
        pv = res["pilots"]
        out["n_pilots"] = len(pv)
        # the guarantee: a pilot loses at most the budget in force when it started, per pilot quote
        out["pilot_over_budget"] = int(sum(market.phi(inc) - market.phi(h) > l0 + 1e-12 for _, inc, h, _, _, l0 in pv))
        out["pilot_loss_max_rel"] = float(max([0.0] + [(market.phi(inc) - market.phi(h)) / market.phi(inc)
                                                        for _, inc, h, _, _, _ in pv]))
        out["ci_miss"] = bool(res.get("ci_miss", False))
    elif "ci_miss" in res:               # safe UCB: whether any of its intervals missed the true take-up
        out["ci_miss"] = bool(res["ci_miss"])
    if "ts_not_converged" in res:        # Thompson sampling: posterior-mode updates that did not converge
        out["ts_not_converged"] = int(res["ts_not_converged"])
    return out
