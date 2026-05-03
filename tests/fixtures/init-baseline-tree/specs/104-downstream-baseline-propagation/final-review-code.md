# Feature 104 Final Code Review

**Reviewer**: code-reviewer
**Date**: 2026-04-08
**Branch**: 104-downstream-baseline-propagation
**Verdict**: APPROVED_WITH_CONCERNS

---

## Summary

Feature 104 adds delta_status awareness (NEW, UNCHANGED, UPDATED, RESOLVED) to downstream pipeline consumers. The implementation spans 3 Python files and 7 markdown instruction/template files. The core parser additions are well-structured, follow existing patterns, and handle edge cases correctly. Two concerns warrant attention before or shortly after merge.

---

## Python File Review

### scripts/tachi_parsers.py

#### parse_baseline_frontmatter() (lines 248-279)

**Quality**: GOOD. The function follows the same defensive pattern as `parse_frontmatter()`: dual regex for standard and code-fenced frontmatter, line-by-line parsing, null-coalescing for missing values.

**Edge cases handled**:
- Returns all-None dict when no frontmatter exists (line 261)
- Returns all-None dict when frontmatter exists but has no `baseline:` block
- Correctly exits the baseline block when a non-indented line is encountered (line 271)
- Treats YAML null representations (`null`, `~`, empty string) uniformly as None (line 275)
- Only populates keys that exist in the result dict, ignoring unexpected nested keys (line 278)

**Style**: Follows existing `parse_frontmatter()` patterns. Variable naming (`fm`, `kv`, `in_baseline`) is consistent with nearby code.

No issues found.

#### parse_resolved_findings() (lines 453-472)

**Quality**: GOOD. Returns empty list when Section 4b is absent -- correct first-run behavior. Injects `delta_status: "RESOLVED"` as a hard-coded constant, which is the right approach since resolved findings always have this status by definition.

**Edge case handled**: Empty table / missing section returns `[]` (line 460).

**Column mapping**: Uses `"ID"`, `"Component"`, `"Threat"`, `"Last Risk Level"`, `"Resolution Reason"` -- these must match the Section 4b table headers in the orchestrator output.

No issues found.

#### parse_threats_findings() (lines 475-501)

**Quality**: GOOD. The refactoring from `dict-literal-append` to `finding = {...}; conditionally-add; append` is clean. The `delta_status` field is included only when the "Status" column is present and non-empty (lines 497-499), maintaining backward compatibility with pre-delta threats.md files.

No issues found.

---

### scripts/extract-infographic-data.py

#### CRITICAL CONCERN: build_json_output() does not include delta data (line 1149-1170)

**File**: `/Users/david/Projects/tachi/scripts/extract-infographic-data.py`, lines 1149-1170
**Issue**: The `build_json_output()` function explicitly constructs the output dict from five named keys (`metadata`, `severity_distribution`, `heat_map`, `top_findings`, `template_data`). It does NOT include the `delta` key that was added to `data` at line 1361. This means delta data is computed and validated internally but is silently dropped from the JSON output file.

**Impact**: The infographic agent documentation (agents/threat-infographic.md, lines 76-84) states that `delta.has_baseline`, `delta.delta_counts.new`, and `delta.delta_counts.resolved` are available in `infographic-data.json`. With the current code, these fields will never appear in the output JSON, so the infographic agent will never see delta context.

**Severity**: WARNING (not CRITICAL, because the infographic agent treats delta as optional -- it gates on `delta.has_baseline` and degrades gracefully to non-delta rendering. No crash or incorrect data will result, but delta-aware infographics will never trigger.)

**Fix**: Add the delta key to `build_json_output()`:
```python
# In build_json_output(), after the output dict construction:
if "delta" in data:
    output["delta"] = data["delta"]
```

#### delta_status propagation into top_findings (lines 1248-1255)

**Quality**: GOOD. The lookup-by-id pattern (`findings_by_id`) is correct. Only injects `delta_status` when both baseline is present AND the source finding has the field. No mutation of the original findings list.

#### Delta counts computation (lines 1331-1349)

**Quality**: GOOD. Mirrors the logic in extract-report-data.py. Counts RESOLVED from `parse_resolved_findings()` and active statuses from the findings list. The `.upper()` call on delta_status ensures case-insensitive matching.

**Note**: Findings without a `delta_status` key (e.g., Tier 1 and Tier 2 findings) will silently contribute 0 to all counters -- correct behavior since delta is currently a Tier 3 concern only.

---

### scripts/extract-report-data.py

#### Imports (lines 28-31)

**Quality**: CLEAN. `parse_baseline_frontmatter` and `parse_resolved_findings` are the only new imports. No unused imports introduced.

#### Baseline/delta parsing in main() (lines 883-888)

**Quality**: GOOD. Parsing happens once, early, and results are stored in local variables (`baseline`, `has_baseline`, `resolved_findings`). The `has_baseline` gate is `baseline["source"] is not None` -- consistent with the parser's null-coalescing behavior.

#### generate_report_data_typ() -- Section 3c2 Baseline/Delta (lines 554-580)

**Quality**: GOOD. All delta variables use `data.get()` with defaults, so the function works even if delta keys are missing from the data dict. The `resolved-findings` Typst array generation correctly escapes all string fields.

**Naming consistency check**: Typst variables use kebab-case (`has-baseline`, `delta-new-count`, `resolved-findings`) which matches the existing Typst variable naming convention in the file. Finding dict keys inside resolved findings use snake_case (`risk_level`, `resolution_reason`) which matches the Python-side convention. The Typst output uses kebab-case for the struct keys (`risk-level`, `resolution-reason`). This is correct -- Typst and Python conventions are appropriately bridged.

#### _format_finding() -- Tier 3 delta_status (lines 792-807)

**Quality**: GOOD. The delta_status field is appended conditionally only for Tier 3 findings, which is correct because only `parse_threats_findings()` produces findings with this field. Tier 1 and Tier 2 parsers do not extract delta_status from their respective source tables.

**NOTE**: If delta_status is later added to Tier 1 or Tier 2 findings (future feature), `_format_finding()` for Tiers 1 and 2 would need the same conditional append. This is acceptable as-is since the feature scope is Tier 3 only.

#### Delta counts in main() (lines 984-997)

**Quality**: GOOD. Identical logic to the infographic extraction script. Defaults to all-zero counts when no baseline, ensuring the Typst variables always have valid integer values.

---

## Markdown File Review

### agents/threat-report.md

**Clarity**: GOOD. The new Section 4b row in the input contract table clearly specifies columns and conditions. The new frontmatter baseline fields table (lines 146-153) defines the primary gate (`baseline.source` non-null) explicitly.

**Delta annotations in Section 3** (lines 249-253): The `[NEW]`, `[UNCHANGED]`, `[UPDATED]` prefix format is unambiguous. The instruction to "omit the delta prefix entirely" when no baseline is clear.

**Delta-aware attack trees** (lines 686-223): The four-branch specification (NEW, UPDATED, UNCHANGED, RESOLVED) is exhaustive and each branch has a clear action. The carry-forward note for UNCHANGED includes the baseline date variable.

**Section 8 Delta Summary** (lines 829-882): Well-structured with three sub-sections (lifecycle breakdown, remediation progress, baseline reference). Quality rules at the end enforce count consistency.

No issues found.

### agents/threat-infographic.md

**Clarity**: GOOD. The delta_status field description (line 72) correctly notes that RESOLVED findings are excluded from severity distribution and appear only in Section 4b. The "Baseline and Delta Context" subsection (lines 74-87) properly identifies the JSON path (`delta.has_baseline`) and describes the gating behavior.

No issues found.

### .claude/agents/tachi/report-assembler.md

**Clarity**: GOOD. The v1.2 schema version entry (line 208) properly lists Section 4b and Section 8. The delta variable table (lines 216-224) matches what `generate_report_data_typ()` actually produces. The four rendering rules (lines 226-231) are specific and actionable.

No issues found.

### .claude/commands/infographic.md

**Clarity**: GOOD. The delta instruction added to Step 2 (lines 168-172) is concise and correctly references the JSON `delta` object structure.

No issues found.

### .claude/commands/security-report.md

**Clarity**: GOOD. The baseline detection line in the Step 2 detection output (line 57) uses conditional format correctly. The Step 4 note (lines 153-156) about automatic delta variable inclusion is informative.

No issues found.

### templates/tachi/output-schemas/threats.md

**Completeness**: GOOD. Section 7 table now includes the Status column with the three active statuses documented. Section 8 (Delta Summary) template includes both the schema definition and a worked example with realistic data.

**Consistency check**: The Section 7 example (lines 415-422) shows a mix of NEW, UNCHANGED, and UPDATED statuses across findings, which matches the expected output format.

No issues found.

### templates/tachi/output-schemas/threat-report.md

**Completeness**: GOOD. Schema version bumped to 1.1. Frontmatter template includes all new fields (baseline_source, baseline_date, delta_counts). Section 5 attack tree delta handling rules are documented in the blockquote. Section 8 template is fully specified with lifecycle table, remediation narrative, and baseline reference.

**Consistency check**: The `attack_tree_count` description (line 329) correctly notes that UNCHANGED trees (carried forward) are excluded from the count. This matches the agent instructions.

No issues found.

---

## Cross-Cutting Checks

### Import hygiene
All new imports are used. No unnecessary imports added. The existing pattern of importing `_empty_severity` (a conventionally private function) was already established before this feature.

### Naming consistency
- Parser functions: `parse_baseline_frontmatter`, `parse_resolved_findings` -- follow `parse_*` pattern.
- Dict keys: `delta_status`, `delta_counts`, `has_baseline`, `baseline_source` -- follow existing snake_case pattern.
- Typst variables: `has-baseline`, `delta-new-count`, `resolved-findings` -- follow existing kebab-case pattern.
- All consistent.

### Error handling
- `parse_baseline_frontmatter()`: Returns all-None on missing/malformed frontmatter.
- `parse_resolved_findings()`: Returns `[]` on missing Section 4b.
- `parse_threats_findings()`: Omits `delta_status` key when Status column is absent.
- Both extraction scripts handle missing baseline gracefully with defaults.
- All extraction scripts handle empty findings lists without error.

### Backward compatibility
- `parse_threats_findings()` only adds `delta_status` when the Status column exists, preserving backward compatibility with pre-delta threats.md files.
- `generate_report_data_typ()` uses `data.get()` with defaults for all delta fields.
- `_format_finding()` conditionally appends delta_status only when present.
- Infographic JSON output gates delta on `has_baseline`.
- All backward compatible.

---

## Findings Summary

| # | Severity | File | Line(s) | Issue |
|---|----------|------|---------|-------|
| 1 | WARNING | `scripts/extract-infographic-data.py` | 1149-1170 | `build_json_output()` does not include `data["delta"]` in output JSON -- delta data computed but silently dropped from serialized output |

---

## Verdict: APPROVED_WITH_CONCERNS

1 WARNING finding. The delta data loss in the infographic JSON output (#1) does not cause crashes or incorrect data (the infographic agent gates on `delta.has_baseline` and falls back gracefully), but it means delta-aware infographic rendering will never activate. This should be fixed before the infographic delta feature is expected to work end-to-end.

The remaining code is clean, well-structured, follows existing patterns, handles edge cases defensively, and maintains full backward compatibility. The markdown instructions are clear, unambiguous, and consistent with what the parsers actually produce.
