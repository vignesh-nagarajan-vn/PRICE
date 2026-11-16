"""Unit tests for the posk package (fast; the experiment suite is the
full verification layer - see experiments/run_all.py and results/)."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posk import (BlindRRM, Market, SafeDPerfGD, StructuralEnv,  # noqa: E402
                  StructuralFit, run_agent)
from posk.design import d_optimal_3pt, fisher  # noqa: E402
from posk.theory import a_optimal_design, dispersion_factor  # noqa: E402


def test_fixed_point_consistency():
    mkt = Market()
    hs = mkt.h_sp()
    assert abs(mkt.best_response(mkt.tau(hs)) - hs) < 1e-6
    assert abs(mkt.frozen_foc(hs, mkt.tau(hs))) < 1e-6


def test_modulus_matches_numeric_slope():
    mkt = Market().feedback_for_modulus(0.5)
    hs, d = mkt.h_sp(), 1e-4
    slope = (mkt.best_response(mkt.tau(hs + d))
             - mkt.best_response(mkt.tau(hs - d))) / (2 * d)
    assert abs(-slope - mkt.modulus()) < 1e-3


def test_gamma_po_matches_numeric_hessian():
    mkt = Market()
    h, d = 1.3, 1e-5
    hess = (mkt.Phi(h + d) - 2 * mkt.Phi(h) + mkt.Phi(h - d)) / d ** 2
    assert abs(-hess - mkt.gamma_po(h)) < 1e-4


def test_feedback_for_modulus_hits_target():
    for tgt in (0.3, 0.7):
        assert abs(Market().feedback_for_modulus(tgt).modulus() - tgt) < 1e-3


def test_blind_agent_converges_to_stable_point():
    mkt = Market(sigma=0.0).feedback_for_modulus(0.5)
    env = StructuralEnv(mkt, seed=0)
    path = run_agent(BlindRRM(mkt, mkt.h_sp() + 0.3), env, 60)
    assert abs(path[-1] - mkt.h_sp()) < 1e-4


def test_structural_fit_recovers_truth():
    mkt = Market(sigma=0.02)
    rng = np.random.default_rng(0)
    h = np.tile(np.array([0.4, 1.2, 2.4]), 200)
    y = mkt.tau(h) + 0.02 * rng.standard_normal(len(h))
    p = StructuralFit().fit(h, y)
    assert p["identified"]
    assert abs(p["c"] - mkt.c) < 0.1
    assert abs(p["C1"] - mkt.C1) < 0.1


def test_two_point_design_singular_three_point_not():
    mkt = Market()
    M2 = fisher([1.0, 2.0], [0.5, 0.5], mkt.C1, mkt.c)
    M3 = fisher(d_optimal_3pt(1.5, 0.8, mkt.C1, mkt.c), [1 / 3] * 3,
                mkt.C1, mkt.c)
    assert abs(np.linalg.det(M2)) < 1e-12
    assert np.linalg.det(M3) > 1e-8


def test_a_optimal_beats_isotropic():
    rng = np.random.default_rng(1)
    A = rng.standard_normal((6, 6))
    G = A @ A.T + 0.2 * np.eye(6)
    B = 1.0
    Mopt = a_optimal_design(G, B)
    iso = (B / np.trace(G)) * np.eye(6)
    assert np.trace(np.linalg.inv(Mopt)) < np.trace(np.linalg.inv(iso))
    F = dispersion_factor(G)
    assert abs(np.trace(np.linalg.inv(iso)) / np.trace(np.linalg.inv(Mopt))
               - F) < 1e-8


def test_safed_trust_region_and_progress():
    mkt = Market(sigma=0.25).feedback_for_modulus(0.5)
    env = StructuralEnv(mkt, seed=3)
    agent = SafeDPerfGD(mkt, h0=mkt.h_sp(), r=0.5, margin=0.3)
    path = run_agent(agent, env, 300)
    # centre moves are trust-region capped; probes span at most 2r extra
    steps = np.abs(np.diff(path))
    caps = agent.max_rel_step * np.maximum(np.abs(path[:-1]), 0.2) \
        + 2 * agent.r + 1e-9
    assert (steps <= caps).all()
    assert np.isfinite(path).all()


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print("%d tests passed" % len(fns))
