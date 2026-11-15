"""posk - The Price of Self-Knowledge: pipeline for the ML x OR paper.

Modules: theory (closed forms), env (performative environments), estimators
(OLS / anchored structural / secant + confidence sequence), design (optimal
exploration shapes), agents (BlindRRM, JitterPerfGD, SafeD-PerfGD), metrics.
"""

from .theory import Market, a_optimal_design, dispersion_factor
from .env import SaturatingEnv, StructuralEnv
from .estimators import OLSSlope, StructuralFit, secant_slope
from .agents import BlindRRM, JitterPerfGD, SafeDPerfGD, run_agent

__all__ = [
    "Market", "a_optimal_design", "dispersion_factor",
    "StructuralEnv", "SaturatingEnv",
    "OLSSlope", "StructuralFit", "secant_slope",
    "BlindRRM", "JitterPerfGD", "SafeDPerfGD", "run_agent",
]
