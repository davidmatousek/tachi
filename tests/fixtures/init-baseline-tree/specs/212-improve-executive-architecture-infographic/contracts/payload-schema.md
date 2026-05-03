# Contract — Executive-Architecture Payload Schema

**Feature**: 212
**Status**: Draft (Architect review pending)
**Contract type**: Producer → Consumer field contract for the `executive-architecture` infographic payload.

## Parties

| Role | Component | File |
|------|-----------|------|
| **Producer** (fixed) | `parse_scope_data()` | `scripts/tachi_parsers.py:904` |
| **Intermediate consumer / secondary producer** | `_build_executive_architecture_payload()` | `scripts/extract-infographic-data.py:911` |
| **Consumer A** | Gemini prompt (executive-architecture template) | `.claude/skills/tachi-infographics/references/executive-architecture.md` |
| **Consumer B** | Typst PDF assembler | `.typst/` templates (existing bindings) |
| **Drift guard** | Test module | `tests/scripts/test_executive_architecture_payload.py` (new) |

## Contract surface (F-212 additions only)

### A. Producer contract (unchanged — F-212 does NOT modify)

`parse_scope_data()` produces a dictionary including these two keys that F-212 consumes:

```python
{
    "data_flows": [
        {
            "source": str,                    # component name
            "destination": str,               # component name — NOT "target"
            "data": str,                      # may be empty
            "protocol": str                   # may be empty
        },
        ...
    ],
    "trust_boundaries": [
        {
            "zone": str,                      # zone name
            "trust-level": str,               # producer key uses hyphen
            "components": list[str]           # member component names
        },
        ...
    ]
}
```

**Producer guarantees**:
- When `### Data Flows` section is present in `threats.md`, `data_flows` is a non-empty list; when absent, the key is still present but the list is empty.
- When `### Trust Boundaries` section is present in `threats.md`, `trust_boundaries` is a non-empty list; when absent, the key is still present but the list is empty.
- Field names within list entries are stable across producer versions (governed by `tachi_parsers.py` changes via normal Triad flow).

**F-212 does not extend this contract — it only consumes it.**

### B. Payload consumer contract (NEW — F-212 extends)

`_build_executive_architecture_payload()` emits a dictionary containing two NEW top-level keys in addition to existing keys (`metadata`, `layers`, `callouts`, `severity_distribution`):

```python
{
    ...existing F-128 keys unchanged...,
    "flow_edges": [
        {
            "source": str,                    # from producer.data_flows[i].source
            "destination": str,               # from producer.data_flows[i].destination
            "data": str,                      # from producer.data_flows[i].data, default ""
            "protocol": str                   # from producer.data_flows[i].protocol, default ""
        },
        ...
    ],
    "clusters": [
        {
            "name": str,                      # from producer.trust_boundaries[i].zone
            "members": list[str],             # from producer.trust_boundaries[i].components
            "trust_level": str                # from producer.trust_boundaries[i]["trust-level"]
                                              # key renaming: hyphen → underscore
        },
        ...
    ]
}
```

**Consumer guarantees (FR-212-13 through FR-212-17)**:
- `flow_edges` and `clusters` are ALWAYS present. Empty list `[]` when producer data is absent or empty. Never `null`, never missing.
- `flow_edges[*].destination` matches producer field name (not `target`). Architect MEDIUM-2 lock.
- `clusters[*].members` is populated from producer's `components` field. `clusters[*].trust_level` is derived from producer's `trust-level` via hyphen→underscore rename to match payload-wide naming convention.
- Sort stability:
  - `flow_edges[]` sorted ascending by `(source.casefold(), destination.casefold())`.
  - `clusters[]` sorted ascending by `(_TRUST_LEVEL_ORDER[trust_level] default 99, name.casefold())` — mirrors `_compute_trust_zones:784` pattern.
  - `clusters[*].members` sorted ascending case-insensitive within each cluster.
- Truncation: `flow_edges[]` truncated to 50 entries (first 50 after sort) + warning log when producer emits more. `clusters[]` not truncated.

### C. Gemini prompt contract (Consumer A, FR-212-18)

The VERBATIM-locked prompt text in `.claude/skills/tachi-infographics/references/executive-architecture.md` MUST contain literal string references to `flow_edges` and `clusters` by name. This is enforced by a test assertion in `test_executive_architecture_payload.py` — the test opens the skill reference file and asserts `"flow_edges"` and `"clusters"` are present in the prompt block.

Rationale: prevents "orphaned payload field" regression — a schema change without a prompt change would mean Gemini continues inferring arrows/clusters from component names instead of using structured data, defeating the purpose of L3.

### D. Typst PDF assembler contract (Consumer B, FR-212-20)

**No change.** Typst consumes only:
- `has-executive-architecture` (boolean binding) — set by existing logic, unchanged.
- `executive-architecture-image-path` (string binding) — set by existing logic, unchanged.

The Typst layer is agnostic to `flow_edges` and `clusters` — they exist only in the payload JSON that feeds the Gemini image generation. Typst only ever sees the rendered `.jpg` + the binding booleans.

## Drift-guard test plan (`test_executive_architecture_payload.py`)

New test file. Covers:

| Test | Scenario | Assertion |
|------|----------|-----------|
| `test_flow_edges_absent` | threats.md has no `### Data Flows` section | `payload["flow_edges"]` exists and `== []` |
| `test_flow_edges_empty` | threats.md has `### Data Flows` but empty body | `payload["flow_edges"]` exists and `== []` |
| `test_flow_edges_single` | 1 data flow entry | 1 record with `source`, `destination`, `data`, `protocol` fields present; field names match producer |
| `test_flow_edges_multi_sorted` | 5 data flow entries with mixed case | sorted by `(source.casefold(), destination.casefold())` ascending |
| `test_flow_edges_truncation` | 55 data flow entries | truncated to 50 after sort; warning logged |
| `test_clusters_absent` | threats.md has no `### Trust Boundaries` section | `payload["clusters"]` exists and `== []` |
| `test_clusters_multi_sorted` | 3 trust boundaries with mixed trust levels | sorted by `(trust_level_order, name.casefold())` |
| `test_clusters_members_sorted` | cluster with 4 members in random case | `members` sorted case-insensitive within the cluster |
| `test_clusters_trust_level_rename` | producer emits `trust-level`; consumer emits `trust_level` | payload `clusters[*].trust_level` populated; no `trust-level` key present in payload records |
| `test_destination_field_name_lock` | 1 data flow | payload `flow_edges[0]` has key `destination` (not `target`) — Architect MEDIUM-2 guard |
| `test_determinism` | Run extractor twice on same input | `json.dumps(payload1)` == `json.dumps(payload2)` — byte-identical |
| `test_prompt_co_landing` | Read skill reference file | Prompt text contains literal `"flow_edges"` AND `"clusters"` — FR-212-18 guard |

## Out-of-contract items

Explicitly NOT part of this contract:
- The shape of `boundary_crossings[]` output from `parse_scope_data` (F-212 does not consume this key).
- The internal structure of `_compute_data_flows()` and `_compute_boundary_crossings()` helpers (used elsewhere in the extractor for other templates).
- The existing `callouts[]` / `layers[]` / `metadata` / `severity_distribution` fields — unchanged by this contract.
- The Gemini model version, API version, or inference parameters — ADR-014 governance applies; not in F-212 scope.

## Breakage playbook

| If... | Then... |
|-------|---------|
| Producer renames `destination` → `target` | Drift guard `test_destination_field_name_lock` fails; update consumer to match; file follow-up PRD if rename is intentional |
| Producer renames `trust-level` | Update hyphen→underscore rename in `_build_clusters`; update drift-guard test |
| Consumer reorders sort key | `test_flow_edges_multi_sorted` or `test_clusters_multi_sorted` fails; revert unless the ADR-017 invariant is intentionally updated |
| Prompt removes `"flow_edges"` or `"clusters"` reference | `test_prompt_co_landing` fails; re-add per FR-212-18 |
| New key added to payload (e.g., future F-NNN) | Not a breakage; existing tests continue to pass. Add new test for the new key per F-189 precedent. |
