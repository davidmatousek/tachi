# Final Architecture Review: Feature 104 — Downstream Baseline Propagation

**Reviewer**: Architect Agent
**Date**: 2026-04-08
**Status**: APPROVED_WITH_CONCERNS
**Scope**: 10 modified files across 4 layers (shared parser, extraction scripts, agent instructions, output schema templates)

---

## 1. Architecture Consistency

**Verdict: PASS**

All 10 components follow the same delta-driven branching pattern established in Feature 074:

- **Guard pattern**: Every component gates delta logic on `baseline.source` presence (frontmatter check) or `delta_status` field presence (per-finding check). This is consistent across:
  - `tachi_parsers.py`: `parse_baseline_frontmatter()` returns all-None dict when no baseline; `parse_threats_findings()` only includes `delta_status` key when Status column is non-empty
  - `extract-infographic-data.py`: `has_baseline = baseline["source"] is not None` (line 1229)
  - `extract-report-data.py`: `has_baseline = baseline["source"] is not None` (line 885)
  - `agents/threat-report.md`: "When `baseline.source` is null... skip Section 8 and all delta annotations"
  - `agents/threat-infographic.md`: "When delta data is present" gate throughout
  - `.claude/agents/tachi/report-assembler.md`: `has-baseline` boolean gate
  - Both commands: "When baseline data is present" conditional
  - Both schema templates: "Present only when a baseline was used" conditional

- **Branching pattern**: NEW/UNCHANGED/UPDATED/RESOLVED four-status model is consistent in all components. No component introduces additional statuses or deviates from the established vocabulary.

---

## 2. Data Flow Integrity

**Verdict: PASS WITH ONE CONCERN (see Finding 1)**

The data flow from threats.md through parsers to downstream consumers is architecturally sound:

```
threats.md (Section 7 Status column + Section 4b Resolved Findings + Section 8 Delta Summary)
    |
    +-- tachi_parsers.py::parse_threats_findings()     -> findings with delta_status
    +-- tachi_parsers.py::parse_resolved_findings()    -> resolved findings from Section 4b
    +-- tachi_parsers.py::parse_baseline_frontmatter() -> baseline metadata from frontmatter
    |
    +-- extract-report-data.py
    |     - Calls all 3 parser functions
    |     - Writes delta variables to report-data.typ (has-baseline, delta-*-count, resolved-findings)
    |     - Includes per-finding delta_status in Typst finding tuples (Tier 3 only, line 803-806)
    |     [COMPLETE DATA FLOW]
    |
    +-- extract-infographic-data.py
    |     - Calls all 3 parser functions
    |     - Computes delta_counts from findings + resolved
    |     - Stores in data["delta"] (line 1361)
    |     - **build_json_output() DOES NOT include data["delta"] in JSON** (see Finding 1)
    |     [INCOMPLETE DATA FLOW]
    |
    +-- threat-report agent (reads threats.md directly)
    |     - Parses baseline frontmatter for gate
    |     - Reads delta_status from STRIDE/AI tables (Section 3/4 Status column)
    |     - Reads Section 4b for resolved findings
    |     - Reads Section 8 for Delta Summary pass-through
    |     [COMPLETE DATA FLOW]
    |
    +-- infographic agent/command
    |     - Consumes JSON from extraction script
    |     - Expects "delta" object in JSON (per command Step 2 instructions)
    |     [BLOCKED by Finding 1]
    |
    +-- report-assembler agent/command
          - Consumes report-data.typ from extraction script
          [COMPLETE DATA FLOW]
```

---

## 3. Backward Compatibility

**Verdict: PASS**

All delta guards are consistent and follow the same defensive pattern:

1. **Parser layer**: `parse_threats_findings()` uses `row.get("Status", "").strip()` -- returns empty string when column absent, skips delta_status key entirely. `parse_resolved_findings()` returns empty list when Section 4b absent. `parse_baseline_frontmatter()` returns all-None dict when no baseline block.

2. **Extraction scripts**: Both scripts use `has_baseline = baseline["source"] is not None` as the primary gate. When false, delta logic is skipped entirely. `extract-report-data.py` defaults to zeroed delta counts when no baseline (line 997).

3. **Agent instructions**: All three agents specify "When no baseline, output is identical to current behavior" with explicit no-baseline behavior documented.

4. **Schema templates**: Both templates specify "Omit this entire section on first run (no baseline)" for Section 8.

5. **Edge case handling**: The spec's edge cases are covered -- findings without delta_status default to NEW behavior (parser skips field, agents treat missing as NEW), unrecognized values would pass through as-is (parser does not validate enum values, agents treat unrecognized as NEW per spec).

---

## 4. Schema Coherence

**Verdict: PASS**

### Section 7 Status Column (threats.md template)

The threats.md template (lines 553-558) correctly adds the Status column to Section 7 Recommended Actions table with clear documentation of values (NEW/UNCHANGED/UPDATED) and the note that RESOLVED findings do not appear in this table. The column position (after Finding ID, before Component) matches the parser expectation in `parse_threats_findings()` which uses `row.get("Status", "")`.

### Section 8 Delta Summary (threats.md template)

The threats.md template (lines 575-619) defines Section 8 with the exact structure specified in the plan: Finding Lifecycle table (Status/Count/Description) and Baseline Reference table (Field/Value). The structure matches what the threat-report agent expects to pass through with narrative enrichment.

### threat-report.md schema (v1.1)

The threat-report.md template correctly adds:
- `baseline_source` and `baseline_date` frontmatter fields (lines 37-38)
- `delta_counts` object with new/unchanged/updated/resolved sub-fields (lines 39-43)
- `attack_tree_count` description updated to account for UNCHANGED carry-forward exclusion (line 50)
- Section 8 Delta Summary structure with Finding Lifecycle Breakdown, Remediation Progress narrative, and Baseline Reference (lines 253-284)

The schema version bump from 1.0 to 1.1 is appropriate -- it signals additive changes without breaking existing consumers that do not check `schema_version`.

---

## 5. Production Readiness

**Verdict: APPROVED WITH CONCERNS (1 bug found)**

### Finding 1: Infographic JSON output drops delta data (MEDIUM severity)

**File**: `scripts/extract-infographic-data.py`
**Lines**: 1149-1170 (`build_json_output()`) and 1360-1361 (`data["delta"]` assignment)

**Issue**: The `build_json_output()` function constructs its output dict from specific keys (`metadata`, `severity_distribution`, `heat_map`, `top_findings`, `template_data`) but does NOT include `data.get("delta")`. The delta data is correctly computed (lines 1331-1348) and stored in `data["delta"]` (line 1361), but it is silently dropped during JSON serialization.

**Impact**: The infographic agent and command will never receive delta breakdown data (FR-007: delta_counts in infographic output). The infographic command's Step 2 instructions explicitly reference: "If the JSON contains a 'delta' object (has_baseline: true), include delta context..." -- this condition will never be true because the delta object is not in the JSON.

**Fix**: Add `data.get("delta")` to the `build_json_output()` function's output dict:

```python
output = {
    "metadata": data["metadata"],
    "severity_distribution": data["severity_distribution"],
    "heat_map": data["heat_map"],
    "top_findings": data["top_findings"],
    "template_data": data.get("template_data", {}),
}
# Include delta data when baseline present
if "delta" in data:
    output["delta"] = data["delta"]
```

**Classification**: This is a functional bug, not an architecture issue. The architecture and data flow design are correct -- the implementation simply missed propagating the computed data to the serialization layer. One-line fix.

### All other components: PASS

- `tachi_parsers.py`: Three new functions (`parse_baseline_frontmatter`, `parse_resolved_findings`, extended `parse_threats_findings`) are well-structured, follow existing parser patterns, and maintain backward compatibility.
- `extract-report-data.py`: Complete delta data flow from parser through Typst output. Correctly includes per-finding delta_status (Tier 3), resolved-findings list, and all delta count variables.
- `agents/threat-report.md`: Comprehensive delta branching for attack trees (NEW/UPDATED/UNCHANGED/RESOLVED), executive summary delta counts, and Section 8 Delta Summary. Input contract updated with Section 4b, Section 8, and baseline frontmatter fields.
- `agents/threat-infographic.md`: Delta emphasis directives and baseline context documented. RESOLVED exclusion from severity distribution clearly specified.
- `.claude/agents/tachi/report-assembler.md`: Schema version handling updated to v1.2 awareness. Delta/baseline variable table and rendering rules documented.
- `.claude/commands/infographic.md`: Delta context pass-through to agent documented in Step 2 prompt.
- `.claude/commands/security-report.md`: Baseline detection in artifact summary and delta context pass-through to report-assembler.
- `templates/tachi/output-schemas/threats.md`: Section 7 Status column and Section 8 Delta Summary structure correct.
- `templates/tachi/output-schemas/threat-report.md`: Schema v1.1 with delta frontmatter fields and Section 8 structure correct.

---

## Summary

| Review Dimension | Verdict |
|-----------------|---------|
| Architecture consistency | PASS |
| Data flow integrity | PASS with 1 concern |
| Backward compatibility | PASS |
| Schema coherence | PASS |
| Production readiness | 1 MEDIUM bug |

**Overall Status**: APPROVED_WITH_CONCERNS

The architecture is sound, consistent, and well-designed. All 10 components follow the same delta-driven branching pattern with consistent backward compatibility guards. The one functional bug (infographic JSON output dropping delta data) is a one-line fix in `build_json_output()` that should be addressed before merging.
