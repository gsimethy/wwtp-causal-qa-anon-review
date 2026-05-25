# Prompts

Canonical system prompts used by the paper's three methods.

| File | Used by | Lines |
|---|---|---|
| `oracle_system_prompt.md` | Method 1 (Live Simulator Oracle) | 57 numbered rules + biochemistry framing |

The prompt is the verbatim text passed to the base LLM (Qwen2.5-32B-Instruct)
as the `system` message in every Oracle evaluation run. Numerical constants
that appear in the rules (CII threshold = 2.0, the empirical coupling rate
~96%, several regime-level τ values, and a small number of named W_eff
entries) are CCSS-IX outputs cached as constants for verbatim repetition;
all other quantitative information is obtained via live tool calls
(`run_what_if`, `get_timescale`, `get_coupling_weight`,
`get_coupling_matrix`, `get_regime_info`).

The headline-ablation breakdown of the prompt's contribution to Method 1's
overall accuracy is reported in the paper's experiments section
(`tools + 9-rule prompt` baseline at 145/198; +22.3 pp from the extended
rules 10–57 → 189/198 without self-correction; +4.0 pp from the
self-correction turn → 197/198 headline).
