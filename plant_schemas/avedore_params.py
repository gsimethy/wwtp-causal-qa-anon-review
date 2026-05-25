"""
params.py — Ground-truth parameter store for CCSS-IX Avedøre WWTP model.

All values are read from the trained CCSS-IX model outputs, not from LLM weights.
This is the core principle: the simulator is the causal oracle, not the language model.
"""

from __future__ import annotations
import numpy as np
from pathlib import Path

# ── Variable and regime metadata ──────────────────────────────────────────────

STATE_NAMES = ["NH4", "NO3", "N2O", "O2", "SS"]
STATE_FULL = {
    "NH4": "ammonium",
    "NO3": "nitrate",
    "N2O": "nitrous oxide",
    "O2":  "dissolved oxygen",
    "SS":  "suspended solids",
}
STATE_IDX = {n: i for i, n in enumerate(STATE_NAMES)}
STATE_UNITS = {
    "NH4": "mg-N/L",
    "NO3": "mg-N/L",
    "N2O": "mg-N/L",
    "O2":  "mg-O2/L",
    "SS":  "mg/L",
}

REGIME_NAMES = ["aerobic-fast", "standard", "slow-anoxic"]
REGIME_IDX   = {n: i for i, n in enumerate(REGIME_NAMES)}
REGIME_SHORT = {0: "k=0", 1: "k=1", 2: "k=2"}
REGIME_DESC = {
    0: "aerobic-fast (k=0): high dissolved oxygen, rapid nitrification, AOB fully active",
    1: "standard (k=1): mixed aerobic-anoxic, most common operating state",
    2: "slow-anoxic (k=2): low oxygen, AOB suppressed, elevated N2O emission risk",
}

# Regime occupancy from CCSS-IX analysis on Avedøre dataset (empirical, 2022-2024)
# These are the values used to generate the evaluation benchmark
OCCUPANCY = {
    "aerobic-fast": 0.260,   # k=0: 26.0%
    "standard":     0.573,   # k=1: 57.3%
    "slow-anoxic":  0.167,   # k=2: 16.7%
}

# CII (Causal Isolation Index) constants — from CCSS-IX epistemic analysis
CII_THRESHOLD = 2.0          # z-score threshold for early warning alert (operator decision boundary)
CII_COUPLING_RATE = 0.96     # fraction of all N2O spikes that are externally coupled
CII_N_TOTAL_SPIKES = 1857    # total N2O spike events in Avedøre 2022-2024 dataset
CII_N_COUPLED = 1784         # spikes classified as coupled by CII (~96% of 1857; 0.96×1857=1783.7)
CII_N_ISOLATED = 73          # spikes with no CII early warning (~4% of 1857, internal/spontaneous)
# Lead time distribution (from 1000-window corpus; NOTE: benchmark labels steps as "min")
CII_LEAD_TIME_MEDIAN = 32    # median CII lead time (steps ≈ 32 "min" in benchmark units)
CII_LEAD_TIME_P15 = 10       # 15th percentile lead time
CII_LEAD_TIME_P85 = 48       # 85th percentile lead time

# Timescales (τ, minutes) — hardcoded from CCSS-IX obs_timescales_min.npy
# Rows: regime [k=0, k=1, k=2]; Cols: variable [NH4, NO3, N2O, O2, SS]
TIMESCALES_MIN = np.array([
    [12.7, 10.7,  3.5,  3.8,  4.5],  # k=0 aerobic-fast
    [12.7, 50.7, 14.7, 22.2,  6.1],  # k=1 standard
    [84.0, 74.3, 11.9, 13.3, 22.1],  # k=2 slow-anoxic
])

# W_k path — loaded lazily from CCSS-IX model output
_W_K_PATH = Path(__file__).parents[2] / "ccss-ix" / "outputs" / "analysis" / "ix_struct_v2" / "W_k.npy"
_W_K: np.ndarray | None = None


def load_W_k() -> np.ndarray:
    """Load W_k[K, D, D] coupling matrix from CCSS-IX model outputs.
    W_k[regime, target_idx, source_idx] = effective coupling weight.
    """
    global _W_K
    if _W_K is None:
        if not _W_K_PATH.exists():
            raise FileNotFoundError(f"W_k.npy not found at {_W_K_PATH}")
        _W_K = np.load(_W_K_PATH)
    return _W_K


def get_coupling(source: str, target: str, regime: int | str) -> float:
    """Return W_eff coupling weight from source → target in the given regime.

    Args:
        source: Source variable name, e.g. "N2O"
        target: Target variable name, e.g. "NH4"
        regime: Integer (0/1/2) or string ("aerobic-fast"/"standard"/"slow-anoxic")

    Returns:
        Effective coupling weight W_eff (float)
    """
    if isinstance(regime, str):
        regime = REGIME_IDX[regime]
    W_k = load_W_k()
    src_i = STATE_IDX[source]
    tgt_j = STATE_IDX[target]
    return round(float(W_k[regime, tgt_j, src_i]), 3)


def get_timescale(variable: str, regime: int | str) -> float:
    """Return characteristic timescale τ (minutes) for variable in regime."""
    if isinstance(regime, str):
        regime = REGIME_IDX[regime]
    var_i = STATE_IDX[variable]
    return float(TIMESCALES_MIN[regime, var_i])


def get_all_couplings(regime: int | str) -> dict[str, dict[str, float]]:
    """Return full W_k coupling matrix for a regime as {source: {target: weight}}."""
    if isinstance(regime, str):
        regime = REGIME_IDX[regime]
    W_k = load_W_k()
    result: dict[str, dict[str, float]] = {}
    for src_i, src in enumerate(STATE_NAMES):
        result[src] = {}
        for tgt_j, tgt in enumerate(STATE_NAMES):
            result[src][tgt] = round(float(W_k[regime, tgt_j, src_i]), 3)
    return result


def get_top_couplings(regime: int | str, top_k: int = 5) -> list[dict]:
    """Return top-k strongest coupling edges for a regime, sorted by W_eff descending."""
    if isinstance(regime, str):
        regime = REGIME_IDX[regime]
    W_k = load_W_k()
    edges = []
    for src_i, src in enumerate(STATE_NAMES):
        for tgt_j, tgt in enumerate(STATE_NAMES):
            if src_i != tgt_j:  # skip self-loops
                edges.append({
                    "source": src,
                    "target": tgt,
                    "W_eff": round(float(W_k[regime, tgt_j, src_i]), 3),
                })
    edges.sort(key=lambda x: x["W_eff"], reverse=True)
    return edges[:top_k]
