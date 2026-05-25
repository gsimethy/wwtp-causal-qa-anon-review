# Benchmarks

Five question sets and two precomputed CI files.

| File | n | Plant | Format |
|---|---:|---|---|
| `causal_qa_bench.jsonl` | 198 | Avedøre | 6 causal categories × 33 questions. The primary evaluation set. |
| `agtrup_bench.jsonl` | 40 | Agtrup | Cross-plant adaptation (BPR/BNR plant, disjoint state variables). |
| `asm1_textbook_bench.jsonl` | 40 | Generic | ASM1 textbook validation set (no plant-specific parameters). |
| `cf_bench.jsonl` | 60 | Avedøre | Single-turn counterfactual queries (§5.5). |
| `cfm_bench.jsonl` | 60 | Avedøre | Multi-turn counterfactual variant (Multi-CF DRR). |
| `bootstrap_ci.json` | — | — | 95% CIs (10,000 resamples) for each method × category cell. |
| `bootstrap_ci_strict.json` | — | — | CIs computed with the strict (exact-string-only) scorer. |

## Categories (Avedøre 198Q)

Each category has exactly 33 questions, balanced across regimes and state
variables:

| Category | What it tests |
|---|---|
| `causal_edge` | Direct numerical lookup: "What is the W_eff weight from X to Y in regime k?" |
| `regime` | Regime identification: "Which regime is dominant when X exceeds Y?" |
| `counterfactual` | Intervention reasoning: "If O2 setpoint dropped by 1 mg/L, what happens to N2O?" |
| `anomaly` | Spike/anomaly diagnosis: "Was the N2O excursion at step 412 internally or externally driven?" |
| `early_warning` | CII / lead-time reasoning: "How many steps in advance can CII flag this spike?" |
| `multi_hop` | Compound reasoning over multiple regimes or variables. |

## Schema

```json
{
  "id": "ce_001",
  "category": "causal_edge",
  "question": "In the CCSS-IX model at Avedøre WWTP, ...",
  "gold_answer": "The W_eff coupling weight from SS to NH4 in regime k=0 is 0.179.",
  "gold_keywords": ["0.179", "W_eff", "SS", "NH4"],
  "forbidden_keywords": ["not coupled", "no coupling"],
  "metadata": {"regime": 0, "horizon_min": 32}
}
```

`gold_keywords` drives the deterministic keyword scorer (paper §4).
`forbidden_keywords` catches hallucinated-overlap false positives.
A semantic-audit pass (local LLM judge) is applied only to near-misses;
the strict CI file captures the result of disabling that audit entirely.

## Scoring

A response passes a question if **all** gold keywords appear (case-
insensitive, whitespace-normalised) **and** **no** forbidden keyword
appears. The full scorer source will be released alongside the rest of
the training and evaluation code in a future update.
