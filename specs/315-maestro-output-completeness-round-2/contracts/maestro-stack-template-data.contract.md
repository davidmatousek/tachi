# Contract: maestro-stack template_data payload (Story 1 / US-2 / #312)

**Type**: in-memory JSON spec-data contract (no HTTP API). Producer: `scripts/extract-infographic-data.py` (`--template maestro-stack`). Consumer: the infographic agent (`.claude/agents/tachi/threat-infographic.md`) rendering `templates/tachi/infographics/infographic-maestro-stack.md`.

## Required change (additive, backward-compatible)

The `template_data` object MUST gain three code-computed integer fields, in addition to the existing four:

```json
{
  "has_maestro_data": true,
  "maestro_layer_distribution": [ /* exactly 7 entries, canonical L1→L7, zeros backfilled */ ],
  "most_exposed_layer": { /* unchanged */ },
  "per_layer_summaries": [ /* covers all 7 */ ],

  "layers_with_findings": 3,
  "empty_layers": 4,
  "layer_count": 7
}
```

## Guarantees

1. **Completeness**: `maestro_layer_distribution` always has exactly 7 entries in canonical order (missing layers backfilled with `finding_count: 0`).
2. **Count correctness**: `layers_with_findings = |{L : finding_count > 0}|`; `empty_layers = 7 − layers_with_findings`; `layer_count = 7`. The identity `layers_with_findings + empty_layers == 7` always holds.
3. **Determinism (ADR-017)**: produced via `json.dumps(..., sort_keys=True, indent=2)`; identical input → byte-identical output across runs.
4. **Additivity**: existing four keys are unchanged; existing consumers are unaffected.
5. **Source of truth**: layer IDs/names come from `tachi_parsers.MAESTRO_LAYERS` (no per-renderer hard-coding).
6. **Empty state**: when `has_maestro_data == false` / zero findings, all 7 layers present with `layers_with_findings = 0`, `empty_layers = 7` (graceful, not an error).

## Verification

- Golden fixture `tests/scripts/fixtures/golden/maestro-stack.json` regenerated to include the three keys. Note its source `exec_arch/agentic_app` fixture is **table-less**, so the regenerated golden covers the **all-empty** case (`layers_with_findings=0, empty_layers=7`).
- **A NEW partial-MAESTRO fixture** (~3-of-7 layers) is required to test the **mixed** case (`layers_with_findings=3, empty_layers=4`) — the all-empty golden alone does not prove correct counting.
- `tests/scripts/test_extract_infographic_data.py` asserts on both: presence of the three keys; the `==7` identity; correct counts on the partial fixture; byte-identity across repeated runs.

## Non-goals

- No change to `maestro-heatmap` payload/template (FR-004) — the backfill is **local to the maestro-stack `template_data` block**, never the shared `extract_maestro_data` (which the heatmap also consumes).
- No change to `schemas/finding.yaml` or any SARIF output (FR-010).
