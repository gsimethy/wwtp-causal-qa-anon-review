# Samples

Representative subsets of the MCG training corpus and the CCSS-IX signal-window
archive. The full archives are too large to ship in-tree and will be released
in a future update.

| File | Included | Full archive |
|---|---:|---|
| `mcg_corpus_train_excerpt.jsonl` | first 200 records | ~990k records / 1.3 GB |
| `mcg_corpus_val_excerpt.jsonl`   | first 50 records  | ~52k records / 69 MB  |
| `signal_windows/window_*.npz`    | 5 windows (ids 0, 200, 500, 700, 999) | 1,000 windows / 87 MB |

## MCG corpus excerpt

`mcg_corpus_train_excerpt.jsonl` (200 records) and `mcg_corpus_val_excerpt.jsonl`
(50 records) are the first records of each split, included to show the
training distribution.

### Record schema

```json
{
  "messages": [
    {"role": "system",    "content": "You are a mechanistic WWTP dynamics expert ..."},
    {"role": "user",      "content": "At window step 0, what causal regime is active ..."},
    {"role": "assistant", "content": "At window step 0, the dominant regime is aerobic-fast ..."}
  ],
  "type": "regime_narrative",
  "metadata": {"window_id": 0, "regime": 0, "p_gate": 1.0, ...},
  "source_model": "ccss-ix-avedore-v2"
}
```

`type` is one of: `regime_narrative`, `hourly_summary`, `event_narrative`,
`counterfactual`, `timestep_narrative`.

## Signal windows

Five `.npz` files spanning the available range (window 0, 200, 500, 700, 999)
of the Avedøre CCSS-IX inference outputs. Each window covers 1,000 timesteps
(≈ 33 hours at the model's effective sampling rate).

### `.npz` keys

| Key | Shape | Type | Description |
|---|---|---|---|
| `window_id` | scalar | int64 | Index of the window in the source archive. |
| `start_s` | scalar | int64 | Start time in seconds of the source dataset. |
| `H` | scalar | int64 | Horizon (number of timesteps) — 1000. |
| `y_pred` | (1000, 5) | float32 | CCSS-IX state predictions for [NH4, NO3, N2O, O2, SS]. |
| `y_true` | (5,) | float32 | Observed terminal state (only end-of-window values are public). |
| `y_mask` | (5,) | float32 | Which terminal states are observed (1) vs. censored (0). |
| `p_gate` | (1000, 3) | float32 | Regime posterior at each timestep over [aerobic-fast, standard, slow-anoxic]. |
| `regime_label` | (1000,) | int64 | Hard regime label = argmax(p_gate). |
| `W_k` | (3, 5, 5) | float64 | Regime-conditional coupling tensor at this window's timestep. |
| `cii_z` | (1000,) | float64 | Coupled-Influence-Index z-score trace. |
| `cii_raw` | (1000,) | float64 | Raw CII trace. |
| `W_eff_n2o` | (1000, 5) | float64 | Effective coupling INTO N2O at each timestep (per source state). |
| `u_vals` | (1000, 2) | float32 | Control input trace (plant-specific actuator values). |
| `w_vals` | (1000, 4) | float32 | Disturbance input trace. |
| `spike_events_json` | scalar | str | JSON-encoded list of N2O spike events detected in this window. |

### Quick start

```python
import numpy as np, json
d = np.load("samples/signal_windows/window_00000.npz")
print("window_id:", int(d["window_id"]))
print("dominant regime trace:", d["regime_label"][:10])
print("CII peaks:", np.where(d["cii_z"] > 2.0)[0][:10])
print("spike events:", json.loads(str(d["spike_events_json"])))
```
