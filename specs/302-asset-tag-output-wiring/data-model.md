# Data Model: Asset-Tag Output Wiring (F-260b)

**Feature**: 302 | **Date**: 2026-05-30 | **Plan**: [plan.md](plan.md)

This feature adds **one field** to the finding entity and serializes it across three formats. No new entities; no scoring-field changes.

## Entity: Finding (extended)

The finding gains exactly one new attribute. All existing attributes (`id`, `status`, `component`, `maestro_layer`, `agentic_pattern`, `cvss_base`, `composite`, `severity_band`, etc.) are **unchanged**.

| Attribute | Type | Required | Default | Source | Notes |
|---|---|---|---|---|---|
| `affected_assets` | `array<enum-string>` | optional, **always present** | `[]` | deterministic populator (AD-1) | NEW. Sorted, deduped. Elements ∈ the frozen 6-value enum. |

### `affected_assets` value rules

- **Enum domain (FROZEN)**: `pii | phi | auth | secrets | financial | safety`. No other value is valid. Adding a value is out of scope (FR-006).
- **Default**: `[]` (empty array) — present on **every** finding, never omitted (FR-005). Models the `agentic_pattern`/`maestro_layer` always-present-with-default precedent, **not** the `source_attribution` omit-when-empty precedent.
- **Population rule (Q4 PM-resolved)**: `affected_assets = component_asset_map.get(target_component, [])` — **all** tags on the finding's target component (asset exposure), not "tags that changed a CVSS bit". A `financial` tag on a finding already at `I:H` (no-op modifier) still appears.
- **Ordering**: sorted ascending (free — `parse_component_asset_map()` returns sorted, deduped, lowercase lists).
- **Join key**: the finding's `component`, matched to `component_asset_map` keys via the same case-insensitive/fuzzy cascade the risk-scorer §3.5 modifier pass uses. Unmatched → `[]`.
- **Provenance only**: recording `affected_assets` MUST NOT alter `cvss_base`, `composite`, `severity_band`, or any modifier behavior (NFR-2).

## Cross-Format Representation (the single shape, three surfaces)

The **same value** (a sorted array of enum strings) appears in three places, byte-equivalent per finding (NFR-3):

| Format | Location | Representation | Empty form |
|---|---|---|---|
| **IR / schema** | `schemas/finding.yaml` | `affected_assets: [pii, phi]` (enum-constrained array, default `[]`) | `affected_assets: []` |
| **threats.md** | appended always-present `affected_assets` block, keyed by finding ID (AD-1 §2; tables untouched) | `S-1: [phi, pii]` | `S-1: []` |
| **SARIF** (both surfaces) | `result.properties.affected_assets` (snake_case key, flat array — Q3) | `"affected_assets": ["phi","pii"]` | `"affected_assets": []` |

**Single value, copied into the SARIF surfaces**: the deterministic populator writes the `threats.md` block (the value authority — FR-2). The two **production** `.sarif` files are LLM-authored (orchestrator → `threats.sarif`, risk-scorer → `risk-scores.sarif`) and **copy that single block value verbatim** per their authoring contracts; the Python `generate-*-sarif.py` scripts + the shared `parse_affected_assets()` extractor are the **regeneration/verification tier** (not live). Cross-format consistency in **production** is therefore **baseline/test-checked** (SC-006 multi-finding equality + SC-002 byte-identity) — the `maestro_layer` precedent's guarantee — **NOT** structural-by-construction. (Structural identity holds only within the regeneration/script tier.)

## Schema Versioning

| Field | Old | New | Rule |
|---|---|---|---|
| `finding.yaml` `schema_version` | `1.8` | `1.9` | ADR-026 minor-bump: (a) additive ✓ (b) has default `[]` ✓ (c) shape/required-fields unchanged ✓ → minor |
| `risk-scoring.yaml` `schema_version` | `1.1` | `1.1` (UNCHANGED) | byte-frozen for SC-011; output-contract docs live in `asset-modifiers.md`, not here |

## State / Lifecycle

`affected_assets` is a **pure derived projection** of (architecture asset tags) × (finding→component join). It has no independent lifecycle, no mutation after population, and no effect on finding status (`NEW`/`UNCHANGED`/`UPDATED`/`RESOLVED`). For `UNCHANGED`/`RESOLVED` findings the field is still present (FR-005) and reflects the current architecture's tags for that component.

## Backward Compatibility

Additive + optional + empty-default ⟹ any consumer ignoring unknown fields is unaffected (NFR-1, R4). The only baseline change is the additive block (AD-2); regeneration under `SOURCE_DATE_EPOCH=1700000000` yields an additive-only diff (SC-002).
