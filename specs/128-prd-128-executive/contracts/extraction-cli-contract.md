# CLI Contract: extract-infographic-data.py — executive-architecture

**Script**: `scripts/extract-infographic-data.py`
**Template**: `executive-architecture`

## CLI Argument Additions

The script's argparse `--template` choices list MUST add `executive-architecture` to its enumeration. No other CLI argument changes.

### Invocation

```bash
python scripts/extract-infographic-data.py \
  --template executive-architecture \
  --target-dir /path/to/output/folder
```

### Inputs (read from `--target-dir`)

| File | Required | Purpose |
|------|----------|---------|
| `threats.md` | yes | Source of scope data and findings |
| `risk-scores.md` | optional | Tier upgrade — if present, sources composite scores |
| `compensating-controls.md` | optional | Tier upgrade — if present, takes precedence over risk-scores |

### Tier Detection

Existing convention from F-048:
1. If `compensating-controls.md` exists → tier `compensating-controls`
2. Else if `risk-scores.md` exists → tier `risk-scores`
3. Else → tier `threats`

The tier determines which finding source provides composite scores for callout selection tie-breaking.

### Output

JSON written to **stdout** (existing convention). The agent reads stdout directly.

The JSON object conforms to the `ExecutiveArchitecturePayload` schema defined in [data-model.md](../data-model.md).

### Exit Codes

| Code | Meaning | Conditions |
|------|---------|------------|
| 0 | Success | Payload written to stdout, regardless of `skip_image` value |
| 1 | Missing required input | `threats.md` not found in `--target-dir` |
| 2 | Validation failure | `threats.md` exists but no scope data parseable (no trust zones AND no DFD-type-grouped components), OR file permissions prevent reading |

### Error Output

All errors write to **stderr** with the prefix `[extract-infographic-data]` and a clear, actionable message:

```
[extract-infographic-data] ERROR: threats.md missing in /path/to/output/folder
[extract-infographic-data] ERROR: threats.md present but no parseable scope data (Section 1 components and Section 2 trust boundaries both empty)
```

### Performance Constraint

The executive-architecture branch MUST complete in ≤ 2 seconds for typical threat models (≤ 100 findings, ≤ 20 components). Measured against agentic-app and microservices examples.

### Determinism Constraint

Per ADR-017: byte-identical input MUST produce byte-identical JSON output. The only varying field is `metadata.generation_timestamp`. To support deterministic testing, the script SHALL accept an existing `--frozen-time` flag (already used by other templates) that pins the timestamp.

### Backward Compatibility

The executive-architecture branch MUST NOT modify the dispatch logic for any other template. Adding the new argparse choice and the new dispatch branch SHALL NOT change the behavior of:

- `--template baseball-card`
- `--template system-architecture`
- `--template risk-funnel`
- `--template maestro-stack`
- `--template maestro-heatmap`

Existing unit tests for these templates MUST continue to pass without modification.

## JSON Payload Shape Reference

See [data-model.md](../data-model.md) for the full schema. Summary:

```json
{
  "metadata": { /* PayloadMetadata */ },
  "layers": [ /* ArchitecturalLayer[] */ ],
  "callouts": [ /* ThreatCallout[] */ ],
  "severity_distribution": { /* SeverityDistribution */ }
}
```

## Test Plan (Contract Tests)

The new CLI contract is verified by these test cases (added to `tests/scripts/test_extract_infographic_data.py`):

| Test | Input Fixture | Expected |
|------|---------------|----------|
| `test_executive_architecture_happy_path` | agentic-app threats.md | Exit 0; payload has ≥1 layer, ≥1 callout, skip_image=false |
| `test_executive_architecture_with_risk_scores_tier` | agentic-app + risk-scores.md | Exit 0; metadata.tier_source=="risk-scores"; callouts have non-null composite_score |
| `test_executive_architecture_with_compensating_controls_tier` | agentic-app + compensating-controls.md | Exit 0; metadata.tier_source=="compensating-controls" |
| `test_executive_architecture_no_critical_high` | synthetic threats.md with only Medium/Low/Note | Exit 0; skip_image=true; callouts=[] |
| `test_executive_architecture_no_threats_md` | empty folder | Exit 1; stderr contains "threats.md missing" |
| `test_executive_architecture_no_scope_data` | threats.md with empty Section 1 and 2 | Exit 2; stderr contains "no parseable scope data" |
| `test_executive_architecture_trust_zone_fallback_to_dfd` | threats.md with Section 1 components but no Section 2 trust boundaries | Exit 0; metadata.fallback_used=true; layers source_kind=="dfd_type" |
| `test_executive_architecture_one_callout_per_layer` | threats.md where one layer has 5 Critical findings | Exit 0; that layer has exactly 1 callout (highest severity, lowest finding ID) |
| `test_executive_architecture_deterministic_output` | same input run twice | identical JSON output (with --frozen-time) |
| `test_existing_templates_unchanged` | run all 5 existing templates against agentic-app | identical JSON output to pre-F-128 baseline |
