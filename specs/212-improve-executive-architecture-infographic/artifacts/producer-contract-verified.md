# Producer Contract Verification — Architect MEDIUM-2 Lock

**Task**: T004
**Date**: 2026-04-25
**Producer file**: `scripts/tachi_parsers.py`
**Function**: `parse_scope_data(content: str) -> dict` at line 904
**Verified by**: orchestrator (architect-tier verification)

---

## `data_flows[]` field contract (lines 925–933)

```python
df_rows = parse_markdown_table(content, "### Data Flows")
for row in df_rows:
    result["data_flows"].append({
        "source": row.get("Source", "").strip(),
        "destination": row.get("Destination", "").strip(),
        "data": row.get("Data", "").strip(),
        "protocol": row.get("Protocol", "").strip(),
    })
```

**Field names** (verbatim from producer):
- `source` — string, line 929
- `destination` — string, line 930 — **NOT `target`** (Architect MEDIUM-2 lock)
- `data` — string, line 931
- `protocol` — string, line 932

---

## `trust_boundaries[]` field contract (lines 935–942)

```python
tz_rows = parse_markdown_table(content, "### Trust Zones")
for row in tz_rows:
    result["trust_boundaries"].append({
        "zone": row.get("Zone", "").strip(),
        "trust-level": row.get("Trust Level", "").strip(),
        "components": row.get("Components", "").strip(),
    })
```

**Field names** (verbatim from producer):
- `zone` — string, line 939
- `trust-level` — string, line 940 — **hyphen, NOT underscore** (consumer must rename to `trust_level` per FR-212-15 / payload-schema.md §clusters[])
- `components` — string, line 941 — **NOT `members`** (consumer must rename to `members` per FR-212-15)

---

## Lock summary

| Producer field (this file) | F-212 consumer field | Rename rule |
|----------------------------|----------------------|-------------|
| `data_flows[].source` | `flow_edges[].source` | passthrough |
| `data_flows[].destination` | `flow_edges[].destination` | passthrough — NOT `target` |
| `data_flows[].data` | `flow_edges[].data` | passthrough |
| `data_flows[].protocol` | `flow_edges[].protocol` | passthrough |
| `trust_boundaries[].zone` | `clusters[].name` | rename `zone` → `name` |
| `trust_boundaries[].trust-level` | `clusters[].trust_level` | rename hyphen → underscore |
| `trust_boundaries[].components` | `clusters[].members` | rename `components` → `members` |

Drift-guard tests in `tests/scripts/test_executive_architecture_payload.py` (T022) MUST mechanically enforce these rename rules:

- `test_destination_field_name_lock` — asserts `payload["flow_edges"][0]` has `destination` key
- `test_clusters_trust_level_rename` — asserts `payload["clusters"][*].trust_level` is populated and no `trust-level` key remains
- `test_clusters_members_sorted` — implicitly asserts `members` field exists (sourced from producer's `components`)

---

## Verdict

**APPROVED** — producer field names confirmed at lines 929–932 (data_flows) and 939–941 (trust_boundaries). Architect MEDIUM-2 contract lock satisfied. T024 (`_build_flow_edges`) and T025 (`_build_clusters`) implementations may proceed in Phase 5 with these field-name contracts pinned.
