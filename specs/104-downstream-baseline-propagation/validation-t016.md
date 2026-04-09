# T016 Primary Validation Results

**Feature**: 104 - Downstream Baseline Propagation
**Task**: T016 - Primary Validation
**Date**: 2026-04-08
**Validator**: BDD Testing Agent

---

## Summary

| Component | File | Result |
|-----------|------|--------|
| 1a. parse_baseline_frontmatter | scripts/tachi_parsers.py | PASS |
| 1b. parse_resolved_findings | scripts/tachi_parsers.py | PASS |
| 1c. parse_threats_findings (delta) | scripts/tachi_parsers.py | PASS |
| 2a. Infographic extraction | scripts/extract-infographic-data.py | PASS |
| 2b. Report extraction | scripts/extract-report-data.py | PASS |
| 3a. Threat report agent | agents/threat-report.md | PASS |
| 3b. Infographic agent | agents/threat-infographic.md | PASS |
| 3c. Report assembler agent | .claude/agents/tachi/report-assembler.md | PASS |
| 4a. Infographic command | .claude/commands/infographic.md | PASS |
| 4b. Security report command | .claude/commands/security-report.md | PASS |
| 5a. threats.md schema | templates/tachi/output-schemas/threats.md | PASS |
| 5b. threat-report.md schema | templates/tachi/output-schemas/threat-report.md | PASS |

**Overall Verdict**: PASS -- 0 issues found across 10 components (12 validation checks)

---

## 1. Python Scripts -- Execution Tests

### 1a. parse_baseline_frontmatter() -- PASS

Tested 4 scenarios via python3 -c execution:

| Scenario | Input | Expected | Actual | Result |
|----------|-------|----------|--------|--------|
| Baseline present | frontmatter with source/date/finding_count/run_id | All 4 fields populated | source="threats.md", date="2026-03-31", finding_count="20", run_id="2026-03-31T14-22-05" | PASS |
| No baseline (null) | baseline block with all null values | All 4 fields None | All None | PASS |
| No baseline block | frontmatter without baseline: block | All 4 fields None | All None | PASS |
| Code-fenced frontmatter | yaml fenced frontmatter with baseline | All 4 fields populated | source="old-threats.md", finding_count="15" | PASS |

**Function location**: scripts/tachi_parsers.py:248-279

### 1b. parse_resolved_findings() -- PASS

Tested 3 scenarios:

| Scenario | Input | Expected | Actual | Result |
|----------|-------|----------|--------|--------|
| Section 4b with 2 resolved findings | Table with T-2, LLM-3 | 2 findings with delta_status="RESOLVED" injected | Correct IDs, columns, delta_status | PASS |
| No Section 4b (first run) | Content without 4b header | Empty list | [] | PASS |
| Empty Section 4b table | Header present, no data rows | Empty list | [] | PASS |

**Columns verified**: ID, Component, Threat, Last Risk Level, Resolution Reason -- all 5 columns parsed correctly.
**delta_status injection verified**: Every returned dict has delta_status="RESOLVED" injected.
**Function location**: scripts/tachi_parsers.py:453-472

### 1c. parse_threats_findings() (delta_status) -- PASS

Tested 3 scenarios:

| Scenario | Input | Expected | Actual | Result |
|----------|-------|----------|--------|--------|
| Section 7 with Status column | 4 findings: UNCHANGED, NEW, UPDATED, UNCHANGED | delta_status present in each finding dict | Correct values per finding | PASS |
| Section 7 without Status column (pre-074) | 2 findings, no Status column | No delta_status key in dicts | Key absent (backward compatible) | PASS |
| Standard fields present | All tier-3 keys | id, component, threat, likelihood, impact, risk_level, mitigation | All 7 keys present | PASS |

**Backward compatibility verified**: When no Status column exists, delta_status key is completely absent (not set to empty string), preserving pre-074 behavior.
**Function location**: scripts/tachi_parsers.py:475-501

### Integration Test: RESOLVED Exclusion from Severity -- PASS

Verified end-to-end that RESOLVED findings (Section 4b) are never included in active severity counts:
- Active findings from Section 7: S-1, LLM-1, T-1 (3 findings)
- Resolved findings from Section 4b: T-2, LLM-3 (2 findings)
- Active and resolved sets are disjoint
- Severity from active only: critical=2, high=1, total=3 (excludes resolved High and Medium)
- Delta counts computed correctly: new=1, unchanged=1, updated=1, resolved=2

---

## 2. Extraction Scripts -- Code Review

### 2a. extract-infographic-data.py -- PASS

| Requirement | Line(s) | Status | Notes |
|-------------|---------|--------|-------|
| Imports parse_baseline_frontmatter | Line 35 | PASS | Imported from tachi_parsers |
| Imports parse_resolved_findings | Line 36 | PASS | Imported from tachi_parsers |
| Calls parse_baseline_frontmatter() | Line 1228 | PASS | Called on threats_content |
| Baseline detection gate | Line 1229 | PASS | `has_baseline = baseline["source"] is not None` |
| Excludes RESOLVED from severity | By design | PASS | Severity extracted from Section 7 findings (extract_severity -> parse_threats_findings), which never includes Section 4b findings. RESOLVED findings are structurally excluded. |
| Computes delta_counts | Lines 1331-1348 | PASS | Counts new/unchanged/updated from active findings + resolved from parse_resolved_findings() |
| Guards delta logic behind baseline check | Lines 1332-1349, 1360-1361 | PASS | `if has_baseline:` gate; delta_data only added to output when baseline present |
| delta_status in top findings | Lines 1248-1255 | PASS | When has_baseline, copies delta_status from source findings to top_findings |

### 2b. extract-report-data.py -- PASS

| Requirement | Line(s) | Status | Notes |
|-------------|---------|--------|-------|
| Imports parse_baseline_frontmatter | Line 29 | PASS | Imported from tachi_parsers |
| Imports parse_resolved_findings | Line 30 | PASS | Imported from tachi_parsers |
| Calls parse_baseline_frontmatter() | Line 884 | PASS | Called on threats_content |
| Writes baseline Typst variables | Lines 555-560 | PASS | has-baseline, baseline-source, baseline-date, baseline-finding-count, baseline-run-id |
| delta_status per finding in Typst | Lines 803-806 | PASS | In _format_finding(), delta_status appended to Typst dict when present (tier 3) |
| Writes resolved_findings list | Lines 567-579 | PASS | Full Typst array with id, component, threat, risk-level, resolution-reason per resolved finding |
| Computes delta counts | Lines 984-997 | PASS | Same pattern as infographic: counts from active + resolved |
| Writes delta count variables | Lines 562-565 | PASS | delta-new-count, delta-unchanged-count, delta-updated-count, delta-resolved-count |
| Guards delta logic | Lines 985-997 | PASS | `if has_baseline:` computes real counts; else zeros |

---

## 3. Agent Instructions -- Content Review

### 3a. threat-report.md -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| Input contract includes delta_status | Line 88 | PASS | Listed as optional enum field (NEW/UNCHANGED/UPDATED) |
| Input contract includes baseline_run_id | Line 89 | PASS | Listed as optional string field |
| Input contract includes Section 4b | Line 55 | PASS | Resolved Findings with columns: ID, Component, Threat, Last Risk Level, Resolution Reason |
| Input contract includes Section 8 | Line 59 | PASS | Delta Summary section documented |
| Frontmatter baseline fields | Lines 63-70 | PASS | baseline.source as primary gate, baseline.date, finding_count, run_id |
| Delta counts in executive summary | Lines 179 | PASS | "When delta data is present, include delta counts in the posture summary" with example |
| Lifecycle annotations in Threat Analysis | Line 252 | PASS | Delta status prefix format: [NEW], [UNCHANGED], [UPDATED] |
| Attack tree branching by delta_status | Lines 689-698 | PASS | NEW=fresh, UPDATED=fresh+note, UNCHANGED=carry-forward, RESOLVED=excluded, no-baseline=all fresh |
| Section 8 Delta Summary | Lines 835-881 | PASS | Complete structure: lifecycle breakdown, remediation progress, baseline reference |
| No-baseline guard | Lines 837, 841 | PASS | "only present when baseline data exists"; skip when null/~/absent |
| Quality checklist updated | Lines 119-120 | PASS | Section 8 presence check; frontmatter includes baseline_source, baseline_date, delta_counts |

### 3b. threat-infographic.md -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| delta_status in input contract | Line 72 | PASS | Listed as optional enum field with note about RESOLVED exclusion |
| Baseline and Delta Context section | Lines 76-87 | PASS | Describes delta.has_baseline, delta.delta_counts fields |
| RESOLVED exclusion note | Lines 72, 83-84 | PASS | "RESOLVED findings are excluded from severity distribution" explicitly stated |
| Delta emphasis directives | Lines 86 | PASS | "emphasize NEW findings in the Top Findings section" |

### 3c. report-assembler.md -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| Schema version v1.2 handling | Lines 208 | PASS | "v1.2: Full feature set plus delta/baseline data" |
| Delta / Baseline Awareness section | Lines 213-231 | PASS | Complete variable table and rendering rules |
| Active/resolved separation | Line 230 | PASS | "RESOLVED findings appear in separate section, not in active findings tables" |
| NEW badge annotation | Line 229 | PASS | "Annotate findings with delta_status: NEW using a visual indicator" |
| Resolved section rendering | Line 230 | PASS | "render a separate Resolved Findings section after the active findings table" |
| Delta counts in executive summary | Line 228 | PASS | "include delta counts in the risk posture summary" |
| No-baseline guard | Line 231 | PASS | "When has-baseline is false, render findings as before" |

---

## 4. Command Files -- Content Review

### 4a. infographic.md -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| Baseline detection | By design (extraction script) | PASS | Script handles detection; command invokes script |
| Delta context passing | Lines 168-171 | PASS | "If the JSON contains a delta object (has_baseline: true), include delta context" |
| Gemini prompt delta emphasis | Line 171 | PASS | "Pass delta emphasis directives to Gemini prompts" |
| RESOLVED exclusion note | Line 170 | PASS | "severity distribution reflects active findings only (RESOLVED excluded)" |

### 4b. security-report.md -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| Baseline detection in artifact summary | Line 113 | PASS | "if threats.md has baseline.source != null: Baseline: {source} ({date})" |
| Delta context to report-assembler | Lines 153-161 | PASS | "extraction script now detects baseline data... includes delta variables" |
| Delta counts noted in agent prompt | Lines 158-161 | PASS | "delta-aware variables (has-baseline, baseline-source, delta-*-count, resolved-findings)" |

---

## 5. Schema Templates -- Content Review

### 5a. threats.md (output schema) -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| Status column in Section 3 tables | Lines 244-245 | PASS | Status column in every STRIDE table template: "NEW | UNCHANGED | UPDATED" |
| Status column in Section 4 tables | Lines 340-342 | PASS | Status column in AG and LLM tables |
| Status column in Section 7 | Lines 554-558 | PASS | Status column with description of delta_status values |
| Section 4b Resolved Findings | Lines 389-417 | PASS | Complete section with table structure, field definitions, examples |
| Section 8 Delta Summary | Lines 575-619 | PASS | Finding Lifecycle table, Baseline Reference table, examples |
| Baseline fields in frontmatter | Lines 26-30, 46-49 | PASS | baseline.source, date, finding_count, run_id with nullable types |
| schema_version 1.2 | Line 22 | PASS | "schema_version: 1.2" in template |

### 5b. threat-report.md (output schema) -- PASS

| Requirement | Location | Status | Notes |
|-------------|----------|--------|-------|
| Baseline fields in frontmatter | Lines 31-38 | PASS | baseline_source, baseline_date, delta_counts with new/unchanged/updated/resolved |
| schema_version 1.1 | Line 21 | PASS | "schema_version: 1.1" |
| Section 8 Delta Summary | Lines 253-284 | PASS | Finding Lifecycle Breakdown, Remediation Progress, Baseline Reference |
| Attack tree baseline guidance | Lines 199-204 | PASS | NEW=fresh, UPDATED=fresh+note, UNCHANGED=carry-forward, RESOLVED=excluded, no-baseline=all fresh |
| delta_counts field descriptions | Lines 53-57 | PASS | All four count fields documented with nullable types |
| attack_tree_count adjusted for delta | Line 50 | PASS | "Counts Critical and High findings with delta_status NEW or UPDATED (fresh trees)" |

---

## Conclusion

All 10 modified files correctly handle the baseline-compared (delta-aware) scenario. The implementation demonstrates:

1. **Structural separation**: RESOLVED findings are structurally excluded from active severity by being in Section 4b (separate from Section 7), ensuring no downstream consumer accidentally inflates severity counts.

2. **Backward compatibility**: All delta logic is gated behind baseline presence checks (`has_baseline`, `baseline.source is not None`). When no baseline exists, behavior is identical to pre-Feature-104 output.

3. **Consistent delta counting**: Both extraction scripts use the same pattern: count NEW/UNCHANGED/UPDATED from active findings, count RESOLVED from `parse_resolved_findings()`.

4. **Complete contract propagation**: delta_status flows from parser -> extraction scripts -> Typst variables -> agent instructions -> command files -> schema templates with no gaps.

5. **No-baseline guard**: Every component that performs delta-aware behavior has an explicit guard condition that skips delta logic when no baseline is present.
