# Data Model — F-A2 Source Attribution Schema Extension

**Feature**: 189 | **Branch**: `189-source-attribution-schema-extension` | **Date**: 2026-04-17

## Entities

### Finding (extended — schema version 1.5)

The existing top-level entity in `schemas/finding.yaml`. F-A2 adds one optional field; no existing field is removed, renamed, or re-typed.

| Field | Type | Required | Default | Provenance | F-A2 Changes |
|-------|------|----------|---------|------------|--------------|
| id | string (regex `^(S\|T\|R\|I\|D\|E\|AG\|LLM\|AGP)-\d+$`) | yes | — | schema 1.0 | unchanged |
| category | string (8-value enum) | yes | — | schema 1.0 | unchanged |
| component | string | yes | — | schema 1.0 | unchanged |
| threat | string | yes | — | schema 1.0 | unchanged |
| likelihood | string (LOW/MEDIUM/HIGH) | yes | — | schema 1.0 | unchanged |
| impact | string (LOW/MEDIUM/HIGH) | yes | — | schema 1.0 | unchanged |
| risk_level | string (Critical/High/Medium/Low/Note) | yes | — | schema 1.0 | unchanged |
| mitigation | string | yes | — | schema 1.0 | unchanged |
| references | list[string] | yes | — | schema 1.0 | unchanged |
| dfd_element_type | string (4-value enum) | yes | — | schema 1.0 | unchanged |
| maestro_layer | string (8-value enum) | no | "Unclassified" | schema 1.2 (Feature 084) | unchanged |
| agentic_pattern | string (8-value enum) | no (see ADR-026) | "none" | schema 1.4 (Feature 142) | unchanged |
| delta_status | string (4-value enum) | conditional (baseline_present) | "NEW" | schema 1.1 (Feature 104) | unchanged |
| baseline_run_id | string (nullable) | no | null | schema 1.1 (Feature 104) | unchanged |
| **source_attribution** | **list[SourceAttributionRecord]** | **no** | **absent (field omitted)** | **schema 1.5 (this feature)** | **NEW** |

**Invariants**:
- `schema_version` at the top of the document equals `"1.5"` (up from `"1.4"`).
- All 14 pre-existing fields retain their type signatures exactly.
- `source_attribution` is truly optional: it is absent — not `[]` — when a finding cites no framework items.

### SourceAttributionRecord (new — F-A2)

The nested record shape carried in `source_attribution` arrays. Each record is a dict with exactly 2 or 3 string fields.

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| taxonomy | string | yes | — | Closed 5-value enum: `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` |
| id | string | yes | — | Non-empty; MUST resolve as a top-level `id:` key in `schemas/taxonomy/{taxonomy}.yaml` |
| relationship | string | no | `"primary"` (injected by parser when absent) | Closed 3-value enum: `{primary, related, derived}` |

**Invariants**:
- Record has exactly 2 keys (`{taxonomy, id}` — parser injects `relationship: "primary"` on emission) or exactly 3 keys (`{taxonomy, id, relationship}`). Any extra key is a validation error.
- Duplicate records within a single finding's `source_attribution` array are NOT silently deduplicated at the parser tier — they round-trip verbatim. (Deduplication policy, if any, is a downstream F-A3 populator concern.)

## Relationships

```
Finding (1) ────── has ──── (0..N) SourceAttributionRecord
                                        │
                                        │ references (read-only)
                                        ▼
                            schemas/taxonomy/{taxonomy}.yaml (F-A1)
                                 ├── owasp.yaml         (5 external frameworks total)
                                 ├── mitre-attack.yaml
                                 ├── mitre-atlas.yaml
                                 ├── nist-ai-rmf.yaml
                                 └── cwe.yaml
```

**Cardinality notes**:
- A Finding has **0 to N** SourceAttributionRecord entries. N=0 is expressed by OMITTING the field entirely (no `source_attribution: []` injected by default).
- A SourceAttributionRecord is a **value-typed** entity (not a pointer): it fully defines its citation via `taxonomy + id + relationship`. No primary-key constraint beyond the closed enums and referential integrity.
- Records reference `schemas/taxonomy/*.yaml` read-only. F-A2 does not modify any file under `schemas/taxonomy/`.

## Validation Rules

### V1 — Parser-tier `taxonomy` enum membership

On every record read, assert `record.taxonomy ∈ {owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}`. Invalid values raise `ValueError(f"Finding {finding_id}: invalid taxonomy '{value}'. Allowed: {{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}}")`.

### V2 — Parser-tier `relationship` enum membership

On every record read, assert `record.relationship ∈ {primary, related, derived}` (after default-injection). Invalid values raise `ValueError(f"Finding {finding_id}: invalid relationship '{value}'. Allowed: {{primary, related, derived}}")`.

### V3 — Parser-tier `id` non-empty

Assert `record.id != "" and record.id is not None`. Invalid values raise `ValueError(f"Finding {finding_id}: empty or null id in source_attribution record")`.

### V4 — Validator-tier referential integrity

For every finding with `source_attribution`, for every record, load `schemas/taxonomy/{record.taxonomy}.yaml` (cached per-invocation) and assert `record.id` matches a top-level `id:` key in the catalog. Unresolved IDs yield structured `ValidationError(finding_id, record, target_yaml_path, reason)` entries.

### V5 — Parser-tier record shape

Assert record has exactly the key set `{taxonomy, id}` or `{taxonomy, id, relationship}`. Extra keys raise `ValueError(f"Finding {finding_id}: unexpected key(s) in source_attribution record: {extra_keys}")`.

### V6 — Parser-tier absent-vs-empty distinction

Parser-level invariant enforced by `_extract_source_attribution` helper:
- Input has no `source_attribution` data for finding → helper returns `None` → finding dict has NO `source_attribution` key.
- Input has `source_attribution: []` for finding → helper returns `[]` → finding dict has `source_attribution` key with empty list value.

## State Transitions

N/A. F-A2 is a pure data-contract feature. `source_attribution` has no lifecycle semantics; it is a static field on each finding populated at detection time (F-A3) or absent otherwise.

## Test Coverage Traceability

| FR | Validation Rule | Test Fixture | Test Function |
|----|-----------------|--------------|---------------|
| FR-002 | schema shape | `valid_single_record.md` | `test_round_trip_single_record` |
| FR-003 | V1 (taxonomy enum) | `invalid_taxonomy.md` | `test_invalid_taxonomy_rejected` |
| FR-004 | V2 (relationship enum) | `invalid_relationship.md` | `test_invalid_relationship_rejected` |
| FR-004 | V2 default | `valid_single_record.md` (relationship omitted) | `test_relationship_defaults_to_primary` |
| FR-005 | V3 (id non-empty) | synthetic fixture | `test_empty_id_rejected` |
| FR-006 | V6 (absent-key semantic) | `valid_absent.md` | `test_absent_omits_key` |
| FR-006 | V6 (present-but-empty) | `valid_empty_array.md` | `test_empty_array_preserved` |
| FR-007 | round-trip | `valid_multi_record.md` | `test_round_trip_multi_record` |
| FR-008 | V4 (referential integrity) | `invalid_id.md` | `test_invalid_id_detected` |
| FR-013 | fixture validity | all 7 fixtures | `test_fixtures_self_consistent` |
