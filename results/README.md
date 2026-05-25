# Per-method evaluation results

Every `.jsonl` here is the raw evaluator output for one (method, dataset)
pair. One line per question. Files are named so the directory listing alone
tells you the headline number.

## File map

### `oracle/` — Method 1, simulator-tool-use

| File | n_pass / n_total | Description |
|---|---:|---|
| `avedore_oracle_197of198.jsonl` | 197 / 198 | The headline Oracle result. LLM has bounded tool access to the CCSS-IX simulator; the response is generated after a verified tool call. |

### `structured_injection/` — Method 2

| File | n_pass / n_total | Description |
|---|---:|---|
| `avedore_base_struct_156of198.jsonl` | 156 / 198 | Frozen base LLM + plant parameters injected into the prompt as structured context. |
| `avedore_dense_rag_baseline.jsonl` | — | Dense-RAG control: the same parameters retrieved by an off-the-shelf dense retriever instead of being injected directly. Reported in the paper as a control condition. |

### `drr/` — Method 3, DRR retriever

| File | n_pass / n_total | Description |
|---|---:|---|
| `avedore_drr_trained_149of198.jsonl` | 149 / 198 | Trained DRR retriever, hybrid scorer, k=25. |
| `avedore_drr_heldout_150of198.jsonl` | 150 / 198 (75.8%) | **Held-out retriever**: trained on the train split only; this is the methodologically clean number reported in the abstract. |
| `avedore_drr_learned_only_143of198.jsonl` | 143 / 198 | Ablation: learned-component-only retriever (no hybrid token-overlap fallback). |
| `*_summary.json` | — | Per-category breakdown + average parameter-budget statistics. |

### `agtrup/` — Cross-plant transfer

| File | n_pass / n_total | Description |
|---|---:|---|
| `agtrup_drr_trained_35of40.jsonl` | 35 / 40 (88%) | **DRR cross-plant headline.** Retriever trained on Agtrup data, evaluated on Agtrup bench. |
| `agtrup_drr_untrained_20of40.jsonl` | 20 / 40 (50%) | DRR with no Agtrup-specific training (transfer only). |
| `agtrup_mcg_struct.jsonl` | — | M2 with MCG corpus + structured injection on Agtrup. |
| `agtrup_sft_struct.jsonl` | — | M2 with SFT (non-MCG) corpus + structured injection on Agtrup. |
| `agtrup_mcg_only.jsonl` | — | MCG-trained model without parameter injection. |
| `agtrup_sft_only.jsonl` | — | SFT-trained model without parameter injection. |

### `baselines/` — Ungrounded controls

All on the 198Q Avedøre benchmark.

| File | Description |
|---|---|
| `avedore_naive_baseline.jsonl` | Pure zero-shot, no grounding. The 21% number in the paper. |
| `avedore_grounded_baseline.jsonl` | Grounded baseline: minimal plant context. |
| `avedore_grounded_rag_baseline.jsonl` | Grounded + dense RAG. |
| `avedore_base_rag_baseline.jsonl` | Base LLM + dense RAG. |

### `asm1/` — ASM1 textbook validation

| File | Description |
|---|---|
| `asm1_eval_results.jsonl` | Per-question responses on the ASM1 textbook benchmark. |
| `asm1_eval_summary.json` | Aggregate scores per model variant. |

### `arc_drr/` — Cross-domain robustness

ARC Challenge subset: confirms DRR does not hurt out-of-domain accuracy.

| File | Description |
|---|---|
| `arc_base.jsonl` | Base LLM, no injection. |
| `arc_selective.jsonl` | DRR selective injection. |
| `arc_full_injection.jsonl` | Full-parameter injection control. |

### `cf_bench/` — Counterfactual

| File | Description |
|---|---|
| `cfm_drr_results.jsonl` | Multi-turn counterfactual DRR results (CF-Bench, §5.5). |

---

## Re-scoring

Every result file contains the raw `response` text alongside the score that
the paper used. To re-score with a different scorer:

1. Load the matching benchmark from `benchmarks/` using the `id` field as the
   join key.
2. Replace the contents of `score.passed` (or `passed`) with your own judgment.
3. The original keyword scorer source will be released alongside the rest of
   the training and evaluation code in a future update.
