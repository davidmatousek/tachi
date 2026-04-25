# Data Model — Feature 212

**Feature**: 212 — Improve Executive-Architecture Infographic
**Scope**: Payload dict emitted by `scripts/extract-infographic-data.py::_build_executive_architecture_payload()`

## Overview

Feature 212 extends the executive-architecture payload with two new top-level keys (`flow_edges`, `clusters`) and modifies the semantics of one existing key (`callouts`) + an optional field on an existing key (`layers[].layer_overflow`). This file is the authoritative data-model reference. Field names match `parse_scope_data` producer output byte-for-byte (Architect MEDIUM-2 resolution).

All schema changes are **additive** per ADR-028. Pre-F-212 consumers that read `metadata`, `layers`, `callouts`, `severity_distribution` continue to work unchanged.

## Full payload schema (post-F-212)

```python
{
    "metadata": {
        "template_name": str,            # unchanged
        "tier_source": str,              # unchanged
        "source_file": str,              # unchanged
        "generation_timestamp": str,     # unchanged (ISO8601 or frozen when SOURCE_DATE_EPOCH set)
        "qualifying_layer_count": int,   # unchanged
        "total_filtered_count": int,     # unchanged
        "skip_image": bool,              # unchanged
        "fallback_used": bool            # unchanged
    },
    "layers": [                           # see below — L2 adds optional layer_overflow
        {
            "name": str,
            "trust_level": str,           # "trusted" | "semi-trusted" | "untrusted"
            "components": list[str],
            "layer_overflow": str | None  # L2 NEW — optional; populated when callouts>4 for layer
        },
        ...
    ],
    "callouts": [                         # L2 SEMANTICS CHANGED — shape unchanged, count 6-8 weighted
        {
            "layer_name": str,
            "finding_id": str,
            "severity": str,              # "Critical" | "High"
            "raw_description": str,
            "composite_score": float | None,
            "affected_component": str | None
        },
        ...  # 0..8 entries (was: ≤qualifying_layer_count)
    ],
    "severity_distribution": {             # unchanged
        "Critical": int,
        "High": int,
        "Medium": int,
        "Low": int,
        "Informational": int
    },
    "flow_edges": [                        # L3 NEW — always present, empty [] when source absent
        {
            "source": str,                 # component name — matches producer
            "destination": str,            # component name — MATCHES PRODUCER (not "target")
            "data": str,                   # optional content from producer; "" when absent
            "protocol": str                # optional content from producer; "" when absent
        },
        ...
    ],
    "clusters": [                          # L3 NEW — always present, empty [] when source absent
        {
            "name": str,                   # zone name from trust_boundaries[].zone
            "members": list[str],          # components of the zone
            "trust_level": str             # "trusted" | "semi-trusted" | "untrusted"
        },
        ...
    ]
}
```

## `layers[]` — L2 extension (layer_overflow)

Existing key, existing fields preserved. One new optional field:

- **`layer_overflow`** (`str | None`, optional)
  - Populated only when the layer has more qualifying Critical/High findings than callouts allocated to it (layer cap = 4).
  - Value: `"+ N more in this layer"` where N = total qualifying findings for this layer minus callouts shown.
  - Default: `None` (not populated) when layer count ≤ 4 callouts.
  - Rendered by Gemini prompt as a compact annotation on the layer.

## `callouts[]` — L2 semantics change (same shape)

Field structure is **unchanged** from F-128. Only the selection algorithm and count differ:

| Aspect | Pre-F-212 | Post-F-212 (L2) |
|--------|-----------|-----------------|
| Count | 0 or 1 per layer (up to qualifying_layer_count) | 0–8 total, weighted by per-layer qualifying count |
| Algorithm | Per-layer dedup: top 1 per layer | Largest Remainder Method per-layer allocation with floor + ceiling |
| Per-layer floor | N/A | ≥1 per qualifying layer when total ≤ 8 (mechanically enforceable invariant) |
| Per-layer ceiling | N/A (1 each) | 4 callouts max per layer |
| Tie-break within layer | Severity ↓ → composite ↓ → id ↑ | Severity ↓ → composite ↓ → id ↑ (unchanged) |
| Layer ordering | Existing layer order | Existing layer order (unchanged) |

## `flow_edges[]` — L3 new key

**Source**: `parse_scope_data.data_flows[]` in `scripts/tachi_parsers.py`.

**Producer reference** (verbatim from `tachi_parsers.py:928-933`):
```python
{
    "source": <component name>,
    "destination": <component name>,       # Field name is "destination", NOT "target"
    "data": <optional data description>,
    "protocol": <optional protocol>
}
```

**F-212 payload record**:

| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| `source` | `str` | yes | `data_flows[i].source` | Component name; should appear in `layers[].components` or on a `clusters[].members` entry; unmatched names emit an edge anyway + warning log (Edge Case 3) |
| `destination` | `str` | yes | `data_flows[i].destination` | **Field is `destination`, not `target`** — matches producer |
| `data` | `str` | yes (may be empty) | `data_flows[i].data` or `""` | Always string; `""` when producer omits |
| `protocol` | `str` | yes (may be empty) | `data_flows[i].protocol` or `""` | Always string; `""` when producer omits |

**Sort order**: ascending by `(source.casefold(), destination.casefold())`. Case-folded comparison is case-insensitive but deterministic across platforms.

**Empty semantics**: Always present as a list. Empty list `[]` when `data_flows` absent or empty from `threats.md`. Never `null`, never missing from the payload.

**Truncation (FR-212-17)**: After sort, if length > 50, truncate to first 50 entries and log `warning: flow_edges truncated to 50 entries (N emitted by producer)`. Implementation at `_build_flow_edges()` before return.

## `clusters[]` — L3 new key

**Source**: `parse_scope_data.trust_boundaries[]` in `scripts/tachi_parsers.py` (NOT `boundary_crossings[]` — PRD's original reference was imprecise; clusters represent zone membership, boundary crossings represent edges between zones).

**Producer reference** (verbatim from `tachi_parsers.py:938-942`):
```python
{
    "zone": <zone name>,
    "trust-level": <"trusted" | "semi-trusted" | "untrusted">,
    "components": <list of component names>
}
```

**F-212 payload record**:

| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| `name` | `str` | yes | `trust_boundaries[i].zone` | Zone name |
| `members` | `list[str]` | yes (may be empty) | `trust_boundaries[i].components` | Component list; sorted ascending case-insensitive within each cluster |
| `trust_level` | `str` | yes | `trust_boundaries[i]["trust-level"]` | One of `trusted`, `semi-trusted`, `untrusted`; produces key renaming from `trust-level` (producer uses hyphen) to `trust_level` (consumer uses underscore — matches rest of payload schema) |

**Sort order**: ascending by `(_TRUST_LEVEL_ORDER.get(trust_level, 99), name.casefold())` mirroring the existing `_compute_trust_zones` sort at `scripts/extract-infographic-data.py:784`. Constant imported or re-declared:

```python
_TRUST_LEVEL_ORDER = {"trusted": 0, "semi-trusted": 1, "untrusted": 2}
```

**Empty semantics**: Always present as a list. Empty list `[]` when `trust_boundaries` absent or empty. Never `null`, never missing.

**No truncation** — trust boundaries per architecture rarely exceed 10 in practice.

## Validation rules

1. **Key presence invariant**: `flow_edges` and `clusters` MUST be present on every payload emission. Never missing, never `null`. Empty arrays are valid. Enforced by `test_executive_architecture_payload.py` across absent / empty / single / multi fixtures.
2. **Field-name invariant**: `flow_edges[*].destination` (not `target`); `clusters[*].members` (populated from producer's `components`). Enforced by assertion in drift-guard tests.
3. **Sort-stability invariant**: Two consecutive runs on identical input produce byte-identical `flow_edges[]` and `clusters[]`. Enforced by determinism test.
4. **Trust-level enum invariant**: `clusters[*].trust_level ∈ {trusted, semi-trusted, untrusted}`. Unknown values fall to sort-order 99 but are still emitted (no filtering).
5. **Schema additivity invariant**: Removing, renaming, or retyping `metadata`, `layers`, `callouts`, `severity_distribution` is OUT OF SCOPE for F-212. Only additions are permitted. Enforced by test assertions on existing keys.

## State transitions

No stateful entities. Payload is an immutable snapshot per extractor invocation.
