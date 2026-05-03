# Architect P0 Review: MAESTRO Data Extraction (Wave 2)

**Feature**: 091 - MAESTRO Infographic Templates
**Reviewer**: Architect
**Date**: 2026-04-08
**Scope**: `scripts/extract-infographic-data.py` lines 890-1342 (MAESTRO extraction + CLI/main integration)

---

## 1. Architecture Consistency

**Verdict**: SOUND

The MAESTRO extraction follows the established pattern in the file:

| Pattern | Existing Code | MAESTRO Code | Consistent? |
|---------|--------------|--------------|-------------|
| Shared parser reuse | `parse_threats_findings()` via `tachi_parsers.parse_markdown_table()` | `parse_maestro_layer_distribution()` via `tachi_parsers.parse_markdown_table()` | YES |
| Coordinator function | `extract_severity()` orchestrates tier-based extraction | `extract_maestro_data()` orchestrates all MAESTRO sub-parsers | YES |
| Constants at module top | `SEVERITY_COLORS`, `_SEVERITY_ORDINAL` | `_MAESTRO_LAYERS` at line 895 | YES |
| Section comment blocks | `# T009`, `# T010`, etc. | `# T003-T011` | YES |
| Fallback on missing data | `_empty_severity()` returns zero-filled dict | Empty list/dict/string returns | YES |
| Deterministic sort keys | Multi-key sort with tie-breakers everywhere | Same pattern in `compute_most_exposed_layer()` and `compute_maestro_heatmap()` | YES |
| Template branch in `main()` | `if args.template == "baseball-card"` etc. | `elif args.template == "maestro-stack"` / `"maestro-heatmap"` | YES |

The MAESTRO code was placed in a clearly delimited section (lines 890-1135) between the existing risk-funnel code and the JSON output builder. This is the correct insertion point.

---

## 2. Parsing Approach: Dynamic Column Detection

**Verdict**: CORRECT DESIGN DECISION

`parse_per_finding_maestro()` (line 955) uses dynamic column detection by scanning the header row for column names rather than hardcoding indices. This is the architecturally correct approach because:

1. **Section 3 STRIDE tables have 8 columns**: ID, Component, MAESTRO Layer, Threat, Likelihood, Impact, Risk Level, Mitigation
2. **Section 4 AI agent tables have 9 columns**: Same + OWASP Reference (inserted after Threat)
3. The MAESTRO Layer column is always present but its positional index varies relative to other columns like Threat/Risk Level when the OWASP Reference column is inserted.

Dynamic detection on lines 997-1003 correctly handles this:

```python
for idx, col in enumerate(header_cols):
    if col == "MAESTRO Layer":
        maestro_idx = idx
        break
```

The same dynamic approach is used for Component, Threat, and Risk Level columns (lines 1010-1020), ensuring the parser works regardless of column count.

**Contrast with `deduplicate_findings()`** (line 391): The older function uses positional `cells[0]` for threat ID extraction, which works because ID is always the first column. The MAESTRO parser cannot use positional access for the same reason -- column positions shift between table types. The architectural choice to use dynamic detection is sound.

---

## 3. Data Flow Soundness

**Verdict**: SOUND

The data flow is clean and follows the single-pass principle:

```
threats_content (read once in main, line 1208)
    |
    +-> extract_maestro_data() [line 1249 in main]
         |
         +-> parse_maestro_layer_distribution()   -- Section 6 aggregate
         +-> parse_component_layer_mapping()       -- Section 1 components
         +-> parse_per_finding_maestro()            -- Section 3/4 per-finding
         |       |
         |       +-> compute_maestro_heatmap()     -- intersection matrix
         +-> compute_most_exposed_layer()           -- from layer_dist
```

Key observations:

- **No duplicate file reads**: `threats_content` is passed by reference to all sub-parsers. Only `parse_markdown_table()` in the shared module re-scans the string for section headers, which is the established pattern.
- **No circular dependencies**: Each sub-parser reads from the source content independently; `compute_maestro_heatmap()` consumes the output of `parse_per_finding_maestro()` and `parse_component_layer_mapping()`.
- **Main pipeline integration** (line 1249): `extract_maestro_data()` runs unconditionally for all templates, which is correct -- the data is lightweight to extract and the `has_maestro_data` flag gates downstream usage.

---

## 4. Edge Case Handling

**Verdict**: ADEQUATE with one LOW-severity observation

### Covered edge cases:

| Edge Case | Handling | Lines |
|-----------|----------|-------|
| Pre-084 output (no MAESTRO) | `parse_markdown_table()` returns `[]` when section header absent; `has_maestro_data` set to `False` | 903-905, 1126 |
| Section 6 table absent | Returns empty list | 904-905 |
| Missing MAESTRO Layer column | `maestro_idx` stays `None`, `maestro_layer` defaults to `""` | 998-1007 |
| Layer string without em dash | Falls back to raw string as layer_id, empty layer_name | 918-920 |
| Non-canonical layer IDs | `if layer_id not in _MAESTRO_LAYERS: continue` in heatmap | 1058-1059 |
| Component cap | Top 10 by finding count | 1072 |
| Empty per_finding data | `compute_maestro_heatmap()` returns empty list | 1048-1049 |
| Tie-breaking in most-exposed | Three-key sort: -count, -severity_ordinal, layer_id ascending | 1098-1102 |

### L-1 [LOW] Em dash vs en dash normalization

`compute_maestro_heatmap()` at line 1057 splits on both em dash and en dash:

```python
layer_id = layer_raw.split("\u2014")[0].strip().split("\u2013")[0].strip()
```

However, `parse_maestro_layer_distribution()` at line 914 only splits on em dash:

```python
parts = layer_raw.split("\u2014", 1)
```

And `compute_most_exposed_layer()` at line 1106 reconstructs with em dash:

```python
return f"{top['layer_id']} \u2014 {top['layer_name']}"
```

The inconsistency is low risk because the orchestrator output uses em dash consistently, but the heatmap parser's defensive split is actually the better pattern. The layer distribution parser should ideally match. Not blocking -- the current code works correctly with all six example outputs.

### L-2 [INFORMATIONAL] "Unclassified" layer handling

The spec mentions "Unclassified" findings as an edge case (spec.md line 107), and the data model references `layer_id: "Unclassified"`. The current extraction does not explicitly handle an "Unclassified" row in the MAESTRO Layer table. If an "Unclassified" row appears in Section 6, it would be parsed correctly (the split logic would assign "Unclassified" as `layer_id` with empty `layer_name`). In the heatmap, findings with "Unclassified" as their layer would be filtered out by the `if layer_id not in _MAESTRO_LAYERS` guard (line 1058). This is acceptable for P0 since the orchestrator currently does not produce "Unclassified" rows, but should be addressed when the feature moves to template rendering (Waves 3-4).

---

## 5. Production Readiness for Downstream Templates

**Verdict**: READY

The extraction output matches the data-model.md contract:

| Contract Field | Extraction Output | Match |
|----------------|------------------|-------|
| `maestro_layer_distribution` | List of `{layer_id, layer_name, finding_count, highest_severity}` | EXACT |
| `most_exposed_layer` | String `"L1 -- Foundation Model"` | EXACT |
| `component_layer_map` | Dict `{component_name: layer_string}` | EXACT |
| `per_finding_maestro` | List of `{id, component, maestro_layer, risk_level, threat}` | EXACT |
| `maestro_heatmap` | List of `{component, layers: {L1: severity\|null, ...}}` | EXACT |
| `has_maestro_data` | Boolean | EXACT |

Template-specific data assembly in `main()`:

- **maestro-stack** (lines 1272-1300): Enriches with `per_layer_summaries` containing top 2 findings per layer, threat text truncated to 120 chars. Clean addition over the raw extraction.
- **maestro-heatmap** (lines 1301-1306): Passes through extraction data directly. Clean.

Both template branches include `has_maestro_data` for graceful degradation.

---

## 6. Additional Observations

### I-1 [INFORMATIONAL] Extraction runs for all templates

`extract_maestro_data()` is called at line 1249 unconditionally, even for `baseball-card`, `system-architecture`, and `risk-funnel` templates that do not use MAESTRO data. The cost is negligible (three `parse_markdown_table()` calls that return empty on pre-084 output) and avoids branching complexity. Acceptable.

### I-2 [INFORMATIONAL] Threat text truncation

The maestro-stack template data truncates threat descriptions to 120 characters (line 1292: `f["threat"][:120]`). This is a reasonable bound for infographic space constraints and follows the pattern of `select_top_findings()` which passes full text but lets the template handle display. The difference is acceptable since the stack diagram has tighter visual space.

---

## Summary

| Category | Finding Count | Severity |
|----------|--------------|----------|
| Architecture consistency | 0 issues | -- |
| Parsing correctness | 0 issues | -- |
| Data flow | 0 issues | -- |
| Edge cases | 1 LOW, 1 INFORMATIONAL | L-1 dash normalization inconsistency |
| Production readiness | 0 issues | -- |
| General observations | 2 INFORMATIONAL | I-1, I-2 |

**Total**: 4 findings (0 blocking, 1 LOW, 3 INFORMATIONAL)
