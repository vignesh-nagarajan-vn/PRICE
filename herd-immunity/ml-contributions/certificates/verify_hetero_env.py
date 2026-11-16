"""Acceptance tests for the heterogeneous-response environment.

The test the experiment spec names is E1: the environment must reduce to the
base project's homogeneous market at R = 11', and that reduction is checked
before any measurement is taken from it.

The rest establish that the environment realizes the geometry it claims to, and
that the theory module predicts what the environment does. The environment
builds its Jacobian by differentiating an actual retraining map, so agreement
with the closed form is a genuine test rather than a restatement.

  E1  reduction        R = 11' recovers the homogeneous market and the base law
  E2  exact placement  measured alignment equals the target, for every topology
  E3  constructed = closed form   the built Jacobian equals -M[(1-k)I + kR]
  E4  theory agreement n_eff, m_N and the frontier match the theory module
  E5  dynamics         simulated trajectories match the predicted verdict
  E6  cadence          K-step runs match Theorem 2's frontier
  E7  mixed market     realized radius matches the two-block root
  E8  concentration    the drawn decomposition converges to the exact placement
  E9  guards           invalid targets and parameters are rejected
"""
import pathlib
import sys

import numpy as np

_HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_HERE / "theory"))
sys.path.insert(0, str(_HERE / "environment"))
import herd_theory as T                                     # noqa: E402
import hetero_response_env as env                             # noqa: E402

PASSED = []


def check(name, condition, detail=""):
    if not condition:
        raise AssertionError(f"FAILED {name}: {detail}")
    PASSED.append(name)
    print(f"  pass  {name}" + (f"   [{detail}]" if detail else ""))


rng = np.random.default_rng(20260818)


# ------------------------------------------------------- E1  the reduction

print("\nE1  reduction to the homogeneous market at R = 11'")

for N in (2, 3, 5, 12, 30):
    for kappa in (0.0, 0.5, 0.8, 1.0):
        mkt = env.homogeneous_market(N, d=8, kappa=kappa, m_1=0.15, rng=rng)
        R = mkt.alignment
        check_ok = np.abs(R - 1.0).max() < 1e-10
        if not check_ok:
            raise AssertionError(f"E1 alignment is not 11' at N={N}")
        if abs(mkt.n_eff - (1 + kappa * (N - 1))) > 1e-10:
            raise AssertionError(f"E1 n_eff is not the base law at N={N}")
check("E1 R = 11' and n_eff = 1 + kappa(N-1)", True,
      "N in {2,3,5,12,30}, four values of kappa")

# the Jacobian itself must equal the base project's homogeneous form
for N in (3, 10):
    m_1, kappa = 0.15, 0.8
    mkt = env.homogeneous_market(N, d=8, kappa=kappa, m_1=m_1, rng=rng)
    base = -m_1 * ((1 - kappa) * np.eye(N) + kappa * np.ones((N, N)))
    check(f"E1 Jacobian equals the base homogeneous form at N={N}",
          np.abs(mkt.jacobian() - base).max() < 1e-10,
          f"max deviation {np.abs(mkt.jacobian() - base).max():.2e}")

# the published amplification anchors
for N, want in ((2, 2.0), (3, 3.0)):
    mkt = env.homogeneous_market(N, d=6, kappa=1.0, m_1=0.15, rng=rng)
    check(f"E1 amplification anchor at N={N}", abs(mkt.n_eff - want) < 1e-10,
          f"n_eff = {mkt.n_eff:.4f}, against which 1.74x and 3.16x were measured")

# and the single-firm reduction
solo = env.homogeneous_market(1, d=4, kappa=0.8, m_1=0.15, rng=rng)
check("E1 reduces to the single firm at N = 1",
      abs(solo.n_eff - 1.0) < 1e-12 and abs(solo.jacobian()[0, 0] + 0.15) < 1e-12)


# ---------------------------------------------------- E2  exact placement

print("\nE2  measured alignment equals the target")

worst = 0.0
targets = []
for N in (3, 6, 15):
    targets += [("monoculture", T.monoculture_R(N)), ("orthogonal", np.eye(N)),
                ("simplex", T.simplex_R(N)),
                ("clustered", T.clustered_R(N, [min(3, N)])),
                ("supply chain", T.supply_chain_R(N, 0.6))]
for name, R in targets:
    E = env.response_jacobians_for_R(R, d=8, rng=rng)
    err = np.abs(env.measured_alignment(E) - R).max()
    worst = max(worst, err)
    if err > 1e-10:
        raise AssertionError(f"E2 {name} not placed exactly: {err:.2e}")
check("E2 every topology placed exactly", worst < 1e-10,
      f"15 targets, max deviation {worst:.2e}")

# random valid alignment matrices too
for _ in range(200):
    N = int(rng.integers(2, 12))
    X = rng.standard_normal((N, 30))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    R = X @ X.T
    E = env.response_jacobians_for_R(R, d=6, rng=rng)
    if np.abs(env.measured_alignment(E) - R).max() > 1e-9:
        raise AssertionError("E2 random target not placed exactly")
check("E2 exact on 200 random alignment matrices", True)

# Frobenius norms come out as asked
E = env.response_jacobians_for_R(T.supply_chain_R(7, 0.4), d=5, rng=rng, eps=0.37)
norms = np.linalg.norm(E.reshape(7, -1), axis=1)
check("E2 response magnitudes equal eps", np.abs(norms - 0.37).max() < 1e-12,
      "eps is the Frobenius norm of the response Jacobian")


# -------------------------------------- E3  constructed equals closed form

print("\nE3  the constructed Jacobian equals the closed form")

worst = 0.0
for _ in range(300):
    N = int(rng.integers(2, 12))
    s = float(rng.uniform(0, 1))
    kappa = float(rng.uniform(0, 1))
    m_1 = float(rng.uniform(0.02, 0.9))
    mkt = env.supply_chain_market(N, d=6, kappa=kappa, m_1=m_1, s=s, rng=rng)
    worst = max(worst, np.abs(mkt.jacobian() - mkt.predicted_jacobian()).max())
check("E3 built by differentiation, matches -M[(1-kappa)I + kappa R]",
      worst < 1e-10, f"300 markets, max deviation {worst:.2e}")

# including mixed markets, where the moduli differ across firms
worst = 0.0
for _ in range(200):
    N = int(rng.integers(2, 15))
    nb = int(rng.integers(0, N + 1))
    mkt = env.mixed_market(N, d=6, kappa=float(rng.uniform(0, 1)), m_1=0.15,
                           s=float(rng.uniform(0.05, 1)), n_blind=nb,
                           gamma_ratio=float(rng.uniform(0.01, 1)), rng=rng)
    worst = max(worst, np.abs(mkt.jacobian() - mkt.predicted_jacobian()).max())
check("E3 holds with heterogeneous moduli", worst < 1e-10,
      f"200 mixed markets, max deviation {worst:.2e}")


# -------------------------------------------------- E4  theory agreement

print("\nE4  the theory module predicts what the environment does")

worst_neff = worst_rad = 0.0
for _ in range(300):
    N = int(rng.integers(2, 20))
    s = float(rng.uniform(0, 1))
    kappa = float(rng.uniform(0, 1))
    m_1 = float(rng.uniform(0.02, 0.6))
    mkt = env.supply_chain_market(N, d=7, kappa=kappa, m_1=m_1, s=s, rng=rng)
    worst_neff = max(worst_neff,
                     abs(mkt.n_eff - T.n_eff_supply_chain(N, s, kappa)))
    radius = np.abs(np.linalg.eigvals(mkt.jacobian())).max()
    worst_rad = max(worst_rad, abs(radius - m_1 * T.n_eff_supply_chain(N, s, kappa)))
check("E4 n_eff matches the closed form", worst_neff < 1e-9,
      f"max deviation {worst_neff:.2e}")
check("E4 realized radius equals m_1 * N_eff", worst_rad < 1e-9,
      f"max deviation {worst_rad:.2e}")

# the clustered counterexample, end to end through the environment
mkt = env.clustered_market(10, d=8, kappa=0.8, m_1=0.5, cluster_sizes=[3], rng=rng)
check("E4 clustered market reproduces N_eff = 2.60", abs(mkt.n_eff - 2.60) < 1e-6,
      f"{mkt.n_eff:.4f}")
check("E4 clustered market is genuinely unstable at m_1 = 0.5",
      not mkt.is_stable() and mkt.m_systemic > 1,
      f"m_N = {mkt.m_systemic:.4f}, which the mean index reports as "
      f"{T.n_eff_mean_index(mkt.alignment, 0.8) * 0.5:.4f}")
check("E4 and the mean index would call it safe",
      T.n_eff_mean_index(mkt.alignment, 0.8) * 0.5 < 1)


# ------------------------------------------------------- E5  the dynamics

print("\nE5  simulated trajectories match the predicted verdict")

agree = disagree = 0
for _ in range(200):
    N = int(rng.integers(2, 15))
    s = float(rng.uniform(0.1, 1))
    kappa = float(rng.uniform(0.2, 1))
    m_1 = float(rng.uniform(0.05, 0.4))
    mkt = env.supply_chain_market(N, d=6, kappa=kappa, m_1=m_1, s=s, rng=rng)
    m_n = mkt.m_systemic
    if abs(m_n - 1) < 0.02:                 # too close to call at finite horizon
        continue
    x0 = rng.standard_normal(N)
    x0 /= np.linalg.norm(x0)
    norms = mkt.simulate(x0, steps=300)
    converged, diverged = norms[-1] < 1e-6, norms[-1] > 1e6
    if (converged and m_n < 1) or (diverged and m_n > 1):
        agree += 1
    elif converged or diverged:
        disagree += 1
check("E5 no disagreement between simulation and prediction", disagree == 0,
      f"{agree} decisive trials")


# --------------------------------------------------------- E6  cadence

print("\nE6  K-step runs match Theorem 2's frontier")

c = 0.8
agree = disagree = 0
for _ in range(200):
    N = int(rng.integers(3, 18))
    s = float(rng.uniform(0.2, 1))
    kappa = float(rng.uniform(0.3, 1))
    m_1 = float(rng.uniform(0.05, 0.4))
    K = int(rng.integers(1, 25))
    mkt = env.supply_chain_market(N, d=6, kappa=kappa, m_1=m_1, s=s, rng=rng)
    m_n = mkt.m_systemic
    km = T.k_max(m_n, c)
    if np.isfinite(km) and abs(K - km) / max(km, 1.0) < 0.02:
        continue
    predicted = T.is_stable_lazy(m_n, c, K)
    if mkt.is_stable(K=K, c=c) == predicted:
        agree += 1
    else:
        disagree += 1
check("E6 realized cadence stability matches k_max", disagree == 0,
      f"{agree} trials at c = {c}")

# and the dynamics, not just the spectrum
mkt = env.supply_chain_market(30, d=6, kappa=0.8, m_1=0.15, s=1.0, rng=rng)
check("E6 worked case: m_N = 3.63 at N = 30, s = 1",
      abs(mkt.m_systemic - 3.63) < 1e-6, f"{mkt.m_systemic:.4f}")
K_star = int(np.floor(T.k_max(mkt.m_systemic, c)))
x0 = rng.standard_normal(30); x0 /= np.linalg.norm(x0)
check("E6 the worked window: floor(K_max) converges, one more diverges",
      mkt.simulate(x0, 400, K=K_star, c=c)[-1] < 1e-6
      and mkt.simulate(x0, 400, K=K_star + 1, c=c)[-1] > 1e6,
      f"K_max = {T.k_max(mkt.m_systemic, c):.4f}, so K = {K_star} is the window")


# ---------------------------------------------------- E7  the mixed market

print("\nE7  mixed markets match the two-block root")

worst = 0.0
for _ in range(400):
    N = int(rng.integers(2, 25))
    nb = int(rng.integers(0, N + 1))
    kappa = float(rng.uniform(0.05, 1))
    s = float(rng.uniform(0.05, 1))
    m_1 = float(rng.uniform(0.02, 0.6))
    gr = float(rng.uniform(1e-6, 1.0))
    mkt = env.mixed_market(N, d=6, kappa=kappa, m_1=m_1, s=s, n_blind=nb,
                           gamma_ratio=gr, rng=rng)
    realized = np.abs(np.linalg.eigvals(mkt.jacobian())).max()
    worst = max(worst, abs(realized - T.mixed_market_radius(
        N, nb, m_1, kappa, s, gr)))
check("E7 realized radius equals mixed_market_radius", worst < 1e-9,
      f"400 markets, max deviation {worst:.2e}")

# the herd-immunity threshold, realized rather than predicted
N, m_1, kappa, s = 20, 0.15, 0.8, 1.0
need = T.min_corrected(N, m_1, kappa, s)
mkt_below = env.mixed_market(N, 6, kappa, m_1, s, N - (need - 1), 1e-9, rng)
mkt_at = env.mixed_market(N, 6, kappa, m_1, s, N - need, 1e-9, rng)
check("E7 the realized threshold is where the theory says",
      not mkt_below.is_stable() and mkt_at.is_stable(),
      f"{need} corrected firms stabilize, {need - 1} do not")

# and the optimism of the limit, seen in the environment
mkt_finite = env.mixed_market(10, 6, 0.8, 0.15, 1.0, 6, 0.6, rng)
mkt_limit = env.mixed_market(10, 6, 0.8, 0.15, 1.0, 6, 1e-9, rng)
check("E7 the limit reads stable where finite correction is not",
      mkt_limit.is_stable() and not mkt_finite.is_stable(),
      "the C18 finding, reproduced end to end in the environment")


# ------------------------------------------------- E8  the drawn decomposition

print("\nE8  the drawn decomposition converges to the exact placement")

s = 0.6
errs = []
for d in (4, 8, 16, 32):
    trials = [np.abs(env.supply_chain_market(8, d, 0.8, 0.15, s, rng,
                                             exact=False).alignment
                     - T.supply_chain_R(8, s))[~np.eye(8, dtype=bool)].max()
              for _ in range(30)]
    errs.append(float(np.median(trials)))
slope = np.polyfit(np.log([4, 8, 16, 32]), np.log(errs), 1)[0]
check("E8 drawn alignment approaches the limit as 1/d", abs(slope + 1) < 0.2,
      f"log-log slope {slope:.3f}, target -1")
check("E8 exact placement has no such error",
      np.abs(env.supply_chain_market(8, 4, 0.8, 0.15, s, rng, exact=True).alignment
             - T.supply_chain_R(8, s)).max() < 1e-10,
      "which is why experiments sweep with exact=True")


# ------------------------------------------------------------- E9  guards

print("\nE9  guards")

def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


check("E9 non-PSD target rejected",
      raises(env.response_jacobians_for_R,
             np.array([[1.0, 2.0], [2.0, 1.0]]), 4, rng))
check("E9 non-unit diagonal rejected",
      raises(env.response_jacobians_for_R,
             np.array([[2.0, 0.0], [0.0, 2.0]]), 4, rng))
check("E9 asymmetric target rejected",
      raises(env.response_jacobians_for_R,
             np.array([[1.0, 0.3], [0.1, 1.0]]), 4, rng))
check("E9 too few dimensions to realize N directions rejected",
      raises(env.response_jacobians_for_R, np.eye(20), 3, rng),
      "d*d must be at least N")
check("E9 kappa outside [0,1] rejected",
      raises(env.HeterogeneousMarket, rng.standard_normal((3, 4, 4)), 1.4, 0.15))
check("E9 cadence without a contraction rejected",
      raises(env.homogeneous_market(4, 4, 0.8, 0.15, rng).step,
             np.ones(4), K=3))
check("E9 n_blind out of range rejected",
      raises(env.mixed_market, 10, 6, 0.8, 0.15, 1.0, 11, 0.5, rng))


print(f"\n{len(PASSED)} checks passed.")
