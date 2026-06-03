# Data Model: F-315 MAESTRO Output Completeness (Round 2)

This feature changes no persistent schema (`schemas/finding.yaml` stays 1.9) and no SARIF. The only data-shape change is **additive** fields on the in-memory `maestro-stack` infographic spec-data payload. Entities below describe the data the implementation operates on.

## Entity: MAESTRO Layer Distribution (always 7)

The per-layer finding tally that drives both the infographic stack and the coverage invariant.

| Field | Type | Rule |
|-------|------|------|
| `layer_id` | string | One of the canonical seven from `tachi_parsers.MAESTRO_LAYERS` (`L1`…`L7`); never hard-coded per-renderer (ADR-019). |
| `layer_name` | string | Canonical name (L1 Foundation Model … L7 Agent Ecosystem) per ADR-020. |
| `finding_count` | int ≥ 0 | Number of findings mapped to the layer this scan. `0` = empty (muted). |
| `highest_severity` | string \| annotation | Severity, or the F-098 clean annotation `Analyzed — no findings this scan` when `finding_count == 0` (unchanged by this feature). |

**Invariants**:
- The distribution presented to the `maestro-stack` payload MUST contain **exactly seven** entries in canonical L1→L7 order. When the parsed `threats.md` table has fewer than seven rows (table-less / pre-F-098 input), missing layers are **backfilled** with `finding_count = 0` (FR-003).
- Ordering is canonical (L1→L7), independent of finding count.
- **Locality (FR-004 protection)**: the backfill is applied **only in the `maestro-stack` `template_data` assembly**, NOT in the shared `extract_maestro_data` function. The `maestro-heatmap` payload also carries `maestro_layer_distribution` (currently `[]`) and MUST remain unchanged.

## Entity: `maestro-stack` template_data (infographic spec-data payload)

The deterministic JSON object emitted by `scripts/extract-infographic-data.py --template maestro-stack`, consumed by the infographic agent.

| Field | Type | Status | Rule |
|-------|------|--------|------|
| `maestro_layer_distribution` | list | existing | The 7-entry distribution above. |
| `most_exposed_layer` | object/string | existing | Layer with the highest finding count. |
| `per_layer_summaries` | list | existing | Per-layer summary lines; covers all 7. |
| `has_maestro_data` | bool | existing | False → graceful empty state. |
| `layers_with_findings` | int | **NEW (FR-002)** | `count(finding_count > 0)`; range 0–7. |
| `empty_layers` | int | **NEW (FR-002)** | `7 − layers_with_findings`; range 0–7. |
| `layer_count` | int | **NEW (FR-002)** | Always `7`. |

**Invariants**:
- `layers_with_findings + empty_layers == layer_count == 7`.
- All three new fields are **code-computed** (deterministic), never agent-counted.
- Determinism: serialized via `json.dumps(..., sort_keys=True, indent=2)` (ADR-017); identical input → byte-identical output. The new keys are additive — existing consumers are unaffected (backward compatible).

## Entity: Coverage Invariant

The durability rule Story 2 gates in CI.

- **Rule**: every `examples/**/threats.md` that contains a "Risk by MAESTRO Layer" table MUST list all seven canonical layer IDs (L1–L7).
- **Discovery**: heading-level-agnostic; excludes `test-output/`; table-less files are skipped (not failed).
- **Failure mode**: the invariant test names the missing layer ID(s) on violation.

## Entity: Example Report Artifact

| Attribute | Values |
|-----------|--------|
| `threats.md` | the MAESTRO table source (subject to the invariant) |
| `security-report.pdf` (+ `.baseline`) | generated PDF |
| gating | **byte-gated** (6 baselines in `BASELINE_EXAMPLES` — must stay byte-identical, not expanded) or **non-gated** (refresh targets; manual diff verification) |
