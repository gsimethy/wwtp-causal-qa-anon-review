# Plant schemas

Structural metadata for the two CCSS-IX plant models used in the paper.

| File | What it contains |
|---|---|
| `avedore.yaml` | Avedøre WWTP: 5 state variables (NH4/NO3/N2O/O2/SS), 3 regimes, occupancy, timescales, CII early-warning constants. |
| `agtrup.yaml` | Agtrup WWTP: 2 observable + 3 latent states, 3 controls, 3 disturbances, 3 regimes, occupancy, per-state timescales. |
| `avedore_W_eff.npy`, `agtrup_W_eff.npy` | Effective coupling tensor, shape `(K=3 regimes, N=5 states, N=5 states)`. `W[k,i,j]` = coupling from state j to state i in regime k. |
| `avedore_tau.npy` | Avedøre timescales, shape `(3 regimes, 5 states)`, units = minutes. |
| `avedore_params.py`, `agtrup_params.py` | Original Python sources from the code repo, included verbatim. The Python files lazy-load the W_eff `.npy` from a path that does not exist in this repo; load the local `.npy` directly instead. |

## Why two formats

The YAML files are for human readers and lightweight tooling: variable
names, units, regime descriptions, and the shape/units of the tensor data.
The `.npy` files are the raw matrices the paper's methods consume. The
`.py` files are kept so the schema's canonical definition (as used by the
training pipeline) is here in full.

## Loading W_eff

```python
import numpy as np

W = np.load("plant_schemas/avedore_W_eff.npy")   # shape (3, 5, 5)
# Coupling weight from SS (idx=4) to NH4 (idx=0) in regime k=0:
print(W[0, 0, 4])   # → 0.179
```

State indices: `NH4=0, NO3=1, N2O=2, O2=3, SS=4`.
Regime indices: `aerobic-fast=0, standard=1, slow-anoxic=2`.
