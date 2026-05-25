"""
params_agtrup.py — Ground-truth parameter store for CCSS-IX Agtrup WWTP model.

Agtrup is a biological nutrient removal (BNR) plant with both nitrification and
biological phosphorus removal (BPR). This contrasts with Avedøre (N2O/nitrogen focus).

Key differences from Avedøre:
  - State space: 2 observable (T1_NH4, T1_PO4) + 3 latent process states
  - Latent states: compressed representations of unmeasured biological processes
    (lat_0 = dominant biological activity proxy, drives both NH4 and PO4 removal)
  - Primary control: T1_O2 (dissolved oxygen setpoint)
  - Secondary control: METAL_Q (metal salt dosing for chemical P removal backup)
  - Main disturbances: TEMPERATURE, MAX_CF (carbon feed), IN_Q (inflow rate)

All values extracted from the trained CCSS-IX Agtrup model checkpoint
(ckpt_ccss_ix_agtrup_paper_open_loop.pt) via the analysis pipeline.

Source files:
  W_k:       outputs/analysis/ix_struct_v3/W_k.npy
  tau:       outputs/analysis/ix_struct_v3/obs_timescales_min.npy
  occupancy: outputs/analysis/ix_struct_v3/regime_usage.npy
"""

from __future__ import annotations

import numpy as np

# ── Variable metadata ─────────────────────────────────────────────────────────

# Observable state variables (directly measured)
OBS_NAMES = ["T1_NH4", "T1_PO4"]
OBS_IDX   = {"T1_NH4": 0, "T1_PO4": 1}
OBS_FULL  = {
    "T1_NH4": "ammonium (tank 1)",
    "T1_PO4": "phosphate (tank 1)",
}
OBS_UNITS = {
    "T1_NH4": "mg-N/L",
    "T1_PO4": "mg-P/L",
}

# Latent state variables (learned compressed representations)
LATENT_NAMES = ["lat_0", "lat_1", "lat_2"]
LATENT_DESC  = {
    "lat_0": "dominant biological activity proxy (drives PAO phosphorus uptake and AOB nitrification)",
    "lat_1": "secondary process dynamic (modulates response rate)",
    "lat_2": "tertiary transient dynamic",
}

# All states (observable + latent)
ALL_STATE_NAMES = OBS_NAMES + LATENT_NAMES
ALL_STATE_IDX   = {n: i for i, n in enumerate(ALL_STATE_NAMES)}

# Control and disturbance variables
CONTROL_NAMES = ["T1_O2", "METAL_Q", "IN_METAL_Q"]
CONTROL_DESC  = {
    "T1_O2":      "dissolved oxygen setpoint (tank 1), mg-O2/L — primary nitrification control",
    "METAL_Q":    "metal salt dosing rate (FeCl3/AlSO4) — chemical phosphorus backup",
    "IN_METAL_Q": "influent metal pre-dosing rate",
}
DISTURBANCE_NAMES = ["TEMPERATURE", "MAX_CF", "IN_Q"]
DISTURBANCE_DESC  = {
    "TEMPERATURE": "wastewater temperature — affects reaction rates",
    "MAX_CF":      "carbon feed rate (VFA/acetate) — essential for biological P removal (PAO)",
    "IN_Q":        "influent flow rate — hydraulic loading",
}

REGIME_NAMES = ["aerobic-fast", "standard", "slow-anoxic"]
REGIME_IDX   = {n: i for i, n in enumerate(REGIME_NAMES)}
REGIME_DESC  = {
    0: "aerobic-fast (k=0): high O2, rapid nitrification and P-release/uptake cycle active",
    1: "standard (k=1): balanced aerobic-anoxic, typical BNR operating state",
    2: "slow-anoxic (k=2): low O2, suppressed nitrification, elevated P-release risk",
}

# ── Regime occupancy ──────────────────────────────────────────────────────────
# From regime_usage.npy (Agtrup Aug 2023 dataset)
OCCUPANCY = {
    "aerobic-fast": 0.2287,   # k=0: 22.87%
    "standard":     0.5373,   # k=1: 53.73%
    "slow-anoxic":  0.2340,   # k=2: 23.40%
}

# ── Timescales (τ, minutes) ───────────────────────────────────────────────────
# From obs_timescales_min.npy  shape [3, 5] — [regime, state]
# Observable states only (idx 0=T1_NH4, 1=T1_PO4)
# Latent timescales included for completeness (idx 2–4)
TIMESCALES_MIN = {
    #              k=0 (aerobic)   k=1 (standard)  k=2 (slow-anoxic)
    "T1_NH4":  [13.16,           18.50,           96.90],
    "T1_PO4":  [11.94,           88.97,           84.82],
    "lat_0":   [ 3.85,           20.27,           15.59],
    "lat_1":   [ 3.57,           15.80,           16.49],
    "lat_2":   [ 3.71,            5.93,           21.27],
}

def get_timescale(variable: str, regime: int) -> float:
    """Return timescale τ (minutes) for variable in given regime."""
    if variable not in TIMESCALES_MIN:
        raise ValueError(f"Unknown variable: {variable}. Choose from {list(TIMESCALES_MIN.keys())}")
    if regime not in (0, 1, 2):
        raise ValueError(f"Regime must be 0, 1, or 2.")
    return TIMESCALES_MIN[variable][regime]

# ── Coupling weights W_eff ────────────────────────────────────────────────────
# From W_k.npy  shape [3, 5, 5] — [regime, target_idx, source_idx]
# Convention: W_k[regime, target, source] = causal influence of source on target
#
# Observable-to-observable couplings (T1_NH4 ↔ T1_PO4):
#   All regimes: weak positive coupling (~0.11–0.19), both directions
#
# Latent-to-observable (dominant signal):
#   lat_0 → T1_PO4: 2.37–3.50 (very strong — biological activity drives P removal)
#   lat_0 → T1_NH4: 1.19–1.32 (strong — same biological activity drives nitrification)
#   lat_1 → T1_PO4: 0.48–0.65 (moderate)
#   lat_1 → T1_NH4: 0.24–0.35 (moderate)

_W_K = np.array([
    # k=0 (aerobic-fast)
    [[0.0000, 0.1146, 1.2614, 0.3459, 0.1221],   # target=T1_NH4
     [0.1876, 0.0000, 3.3574, 0.6535, 0.3244],   # target=T1_PO4
     [0.0000, 0.0000, 0.0000, 0.0849, 0.0000],   # target=lat_0
     [0.0000, 0.0000, 0.4639, 0.0000, 0.0000],   # target=lat_1
     [0.0000, 0.0000, 0.8086, 0.1909, 0.0000]],  # target=lat_2
    # k=1 (standard)
    [[0.0000, 0.0915, 1.1921, 0.2375, 0.1067],
     [0.1457, 0.0000, 2.3746, 0.4826, 0.2998],
     [0.0000, 0.0000, 0.0000, 0.0600, 0.0548],
     [0.0000, 0.0000, 0.4536, 0.0000, 0.0000],
     [0.0000, 0.0000, 0.6933, 0.1233, 0.0000]],
    # k=2 (slow-anoxic)
    [[0.0000, 0.1112, 1.3241, 0.2857, 0.1112],
     [0.1910, 0.0000, 3.5029, 0.6250, 0.3000],
     [0.0000, 0.0000, 0.0000, 0.0814, 0.0000],
     [0.0000, 0.0000, 0.5173, 0.0000, 0.0000],
     [0.0000, 0.0000, 0.8656, 0.1649, 0.0000]],
])  # shape [3, 5, 5]

def load_W_k() -> np.ndarray:
    """Return W_eff matrices [3, 5, 5] for all regimes."""
    return _W_K.copy()

def get_coupling(source: str, target: str, regime: int) -> float:
    """Return W_eff coupling from source to target in given regime."""
    src_i = ALL_STATE_IDX.get(source)
    tgt_i = ALL_STATE_IDX.get(target)
    if src_i is None:
        raise ValueError(f"Unknown source: {source}")
    if tgt_i is None:
        raise ValueError(f"Unknown target: {target}")
    if regime not in (0, 1, 2):
        raise ValueError(f"Regime must be 0, 1, or 2.")
    return float(_W_K[regime, tgt_i, src_i])

def get_all_couplings(regime: int) -> dict[tuple[str, str], float]:
    """Return all non-zero W_eff couplings for a regime as {(source, target): W_eff}."""
    W = _W_K[regime]
    out = {}
    for tgt_i, tgt in enumerate(ALL_STATE_NAMES):
        for src_i, src in enumerate(ALL_STATE_NAMES):
            if src_i != tgt_i and W[tgt_i, src_i] > 0.01:
                out[(src, tgt)] = round(float(W[tgt_i, src_i]), 4)
    return out

def get_top_couplings(regime: int, top_k: int = 6) -> list[dict]:
    """Return top-k W_eff couplings by strength for a regime."""
    pairs = [
        {"source": src, "target": tgt, "W_eff": w}
        for (src, tgt), w in get_all_couplings(regime).items()
    ]
    return sorted(pairs, key=lambda x: x["W_eff"], reverse=True)[:top_k]

# ── Control effect strengths (from ix_effects analysis) ──────────────────────
# Causal effect strength of each control variable on the observable states
# Higher = stronger causal influence on system dynamics
CONTROL_EFFECT_STRENGTH = {
    "T1_O2":    {"k0": 2.1537, "k1": 1.2936, "k2": 1.5748},  # dominant control
    "METAL_Q":  {"k0": 2.0259, "k1": 1.1784, "k2": 1.3926},
    "IN_METAL_Q": {"k0": 1.8807, "k1": 1.0805, "k2": 1.4364},
}
DISTURBANCE_EFFECT_STRENGTH = {
    "TEMPERATURE": {"k0": 2.2122, "k1": 1.9827, "k2": 2.3450},  # largest disturbance
    "MAX_CF":      {"k0": 2.1839, "k1": 1.6124, "k2": 1.8770},  # VFA/carbon feed
    "IN_Q":        {"k0": 1.9714, "k1": 1.6865, "k2": 2.2466},
}

# ── Counterfactual simulation constants ───────────────────────────────────────
# From eval_counterfactual.py analysis on Agtrup dataset
CF_HORIZON_MIN       = 400    # integration horizon (200 steps × 2 min/step)
CF_O2_INTERVENTION   = "T1_O2"   # primary intervention variable
CF_PRIMARY_TARGETS   = ["T1_NH4", "T1_PO4"]  # key outcome variables

# Key counterfactual result: O2 setpoint effect on NH4 (from eval_counterfactual.py)
# High-O2 windows: CF (O2=median) → NH4 increases vs factual (O2 high)
# Low-O2 windows:  CF (O2=median) → NH4 decreases vs factual (O2 low)
# Sign accuracy: ~85% (model correctly predicts direction of O2 interventions)
