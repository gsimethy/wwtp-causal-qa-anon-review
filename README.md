# WWTP Causal Q&A: Benchmark and Evaluation Artifacts

> **Anonymous review copy.** This repository is the anonymised version of a
> public companion dataset whose source paper is currently under double-blind
> review. Author and institutional metadata have been removed; the full
> repository (with attribution) will be made available on acceptance.

Companion dataset for the paper *Simulator-Grounded LLMs for Industrial Causal
Reasoning: Tool-Use, Structured Injection, and Plant-Portable Retrieval for
Wastewater Treatment Process Control* (manuscript under review).

This repository contains everything needed to **inspect, re-score, and audit**
the paper's results: the question benchmarks, the per-method model outputs,
the plant-parameter schemas, and representative samples of the MCG training
corpus and CCSS-IX simulator signal windows.

The full training and evaluation code is not included here. It will be
released in a future update.

---

## What's in this repository

| Directory | Contents |
|---|---|
| [`benchmarks/`](benchmarks/) | The four question sets used in the paper, plus precomputed bootstrap CIs. |
| [`results/`](results/) | Per-method model responses and scores for every headline number in the paper. |
| [`plant_schemas/`](plant_schemas/) | Variable, regime, timescale, and W_eff metadata for both plants. |
| [`prompts/`](prompts/) | The 57-rule oracle system prompt used by Method 1 (Live Simulator Oracle). |
| [`samples/`](samples/) | A representative excerpt of the MCG training corpus and five CCSS-IX signal windows. |

Total repository size: **~4 MB** (everything in-tree, no Git LFS required).

---

## Benchmarks

The four benchmarks are released here in full, not as a subset.

| File | n | Description |
|---|---:|---|
| [`benchmarks/causal_qa_bench.jsonl`](benchmarks/causal_qa_bench.jsonl) | 198 | The Avedøre 198-question Causal Q&A Benchmark — the paper's primary evaluation set, covering six causal categories (causal_edge, regime, counterfactual, anomaly, early_warning, multi_hop), 33 per category. |
| [`benchmarks/agtrup_bench.jsonl`](benchmarks/agtrup_bench.jsonl) | 40 | Agtrup cross-plant benchmark: the same six categories adapted to a biological nutrient removal (BPR/BNR) plant with disjoint state variables (T1_NH4, T1_PO4) and a different sensor topology. |
| [`benchmarks/asm1_textbook_bench.jsonl`](benchmarks/asm1_textbook_bench.jsonl) | 12 | ASM1 textbook validation set, used to check that grounding methods do not regress on canonical biological wastewater dynamics. |
| [`benchmarks/cf_bench.jsonl`](benchmarks/cf_bench.jsonl) | 60 | Counterfactual Q&A benchmark used in §5.5 (single-turn counterfactual queries). |
| [`benchmarks/cfm_bench.jsonl`](benchmarks/cfm_bench.jsonl) | 8 | Multi-turn counterfactual variant (representative subset; full set forthcoming). |
| [`benchmarks/bootstrap_ci.json`](benchmarks/bootstrap_ci.json) | — | Precomputed bootstrap 95% CIs (10,000 resamples) for each method × category cell reported in the paper. |
| [`benchmarks/bootstrap_ci_strict.json`](benchmarks/bootstrap_ci_strict.json) | — | The same, computed with the strict (exact-string-only) scorer, to bound the semantic-audit contribution. |

### Record schema

Each `*_bench.jsonl` line has the format:

```json
{
  "id": "ce_001",
  "category": "causal_edge",
  "question": "In the CCSS-IX model at Avedøre WWTP, ...",
  "gold_answer": "...",
  "gold_keywords": ["W_eff", "0.179", "..."],
  "forbidden_keywords": ["..."],
  "metadata": {"regime": 0, "horizon_min": 32, ...}
}
```

`gold_keywords` drives the deterministic keyword scorer. `forbidden_keywords`
flags hallucinated-overlap false positives. The semantic-audit layer
(local LLM judge) is invoked only on near-misses.

---

## Results (model outputs)

Every JSONL in [`results/`](results/) is the **raw evaluator output** — one model
response per question, plus the score that was computed for the paper. This
lets you re-score with a different scorer, inspect failure modes, or audit
the semantic-judge overrides.

### Headline numbers mapped to files

| Paper claim | File | n_pass / n_total |
|---|---|---|
| **M1 Oracle (Avedøre)** | [`results/oracle/avedore_oracle_197of198.jsonl`](results/oracle/avedore_oracle_197of198.jsonl) | 197 / 198 |
| **M2 Structured Injection (Avedøre)** | [`results/structured_injection/avedore_base_struct_156of198.jsonl`](results/structured_injection/avedore_base_struct_156of198.jsonl) | 156 / 198 |
| **M3 DRR trained retriever (Avedøre)** | [`results/drr/avedore_drr_trained_149of198.jsonl`](results/drr/avedore_drr_trained_149of198.jsonl) | 149 / 198 |
| **M3 DRR held-out retriever (Avedøre)** | [`results/drr/avedore_drr_heldout_150of198.jsonl`](results/drr/avedore_drr_heldout_150of198.jsonl) | 150 / 198 (75.8%) |
| **M3 DRR cross-plant (Agtrup)** | [`results/agtrup/agtrup_drr_trained_35of40.jsonl`](results/agtrup/agtrup_drr_trained_35of40.jsonl) | 35 / 40 (88%) |

Per-category breakdowns are in the accompanying `*_summary.json` files.

See [`results/README.md`](results/README.md) for the full file map (oracle,
structured, DRR variants, baselines, ASM1, ARC cross-domain, counterfactual).

### Record schema

```json
{
  "id": "ce2_001",
  "category": "causal_edge",
  "question": "...",
  "response": "The W_eff coupling weight from SS to NH4 in regime 0 is 0.179.",
  "score": {"passed": true, "partial_score": 1.0, "hits": [true], "forbidden_hit": false},
  "model_tag": "drr",
  "param_keys": ["OCC(0)", "T(NH4,0)", "T(SS,0)", "W(NH4,SS,0)", "W(SS,NH4,0)"],
  "n_params": 5
}
```

`response` is the raw text the LLM produced. `score.passed` is the
keyword-scorer verdict used in the paper. `param_keys` (DRR only) shows
which CCSS-IX parameters the retriever selected for this question.

---

## Plant schemas

[`plant_schemas/`](plant_schemas/) contains the structural metadata for both
CCSS-IX plant models — variable names, units, regime descriptions, empirical
occupancy, timescales, and the effective coupling tensor W_eff used by Methods
1 and 2.

| File | Description |
|---|---|
| `avedore.yaml`, `agtrup.yaml` | Human-readable plant schemas. |
| `avedore_W_eff.npy`, `agtrup_W_eff.npy` | Effective coupling tensor: shape `(K=3 regimes, N=5 states, N=5 states)`. `W[k,i,j]` is the regime-conditional effective coupling from state j to state i. |
| `avedore_tau.npy` | Avedøre timescales (3 regimes × 5 states), units = minutes. |
| `avedore_params.py`, `agtrup_params.py` | The original Python source files from the code repo, included verbatim as the canonical definition. |

The high-resolution **operational sensor data** that CCSS-IX was trained on
cannot be redistributed (data-sharing agreement with the operator), but the
**pre-computed simulator outputs** in [`samples/signal_windows/`](samples/signal_windows/)
are sufficient to reproduce all benchmark targets.

---

## MCG corpus and signal samples

The MCG training corpus and the CCSS-IX signal-window archive are too large
to ship in this repository, so [`samples/`](samples/) ships representative
subsets only:

| File | Included | Full archive |
|---|---:|---|
| `mcg_corpus_train_excerpt.jsonl` | first 200 records | ~990k records / 1.3 GB |
| `mcg_corpus_val_excerpt.jsonl`   | first 50 records  | ~52k records / 69 MB |
| `signal_windows/window_*.npz`    | 5 representative windows (ids 0, 200, 500, 700, 999) | 1,000 windows / 87 MB |

The samples are sufficient to inspect the record schema and the `.npz` layout
(regime gates, predicted vs. observed state, the W_k tensor at each timestep,
the CII (Coupled-Influence Index) trace, and any N2O spike events in the
window). The full archives will be released in a future update.

See [`samples/README.md`](samples/README.md) for the full record and `.npz`
schemas.

---

## How to cite

If you use this benchmark, please cite both the paper and this repository.
See [`CITATION.cff`](CITATION.cff) for the machine-readable form.

---

## License

- **Data and benchmarks** (everything under `benchmarks/`, `results/`,
  `plant_schemas/`, `samples/`): CC BY 4.0 — see [`LICENSE`](LICENSE).
- **Python source files** (`plant_schemas/*_params.py`): MIT.
