# Baseline-Aware Pipeline Structural Validation Report

**Feature**: 074 -- Baseline-Aware Pipeline
**Date**: 2026-04-01
**Validator**: BDD Testing Specialist (structural consistency check)
**Scope**: Read-only validation of pipeline instructions, schemas, and templates

**Substitution Note**: The task originally referenced `examples/second-brain-mcp/` for STRIDE validation. That directory does not exist. Available example directories (`examples/web-app/`, `examples/microservices/`) could serve as substitutes for standard STRIDE validation, but this validation task focuses on structural consistency across pipeline definition files, not on running the pipeline against an example architecture. No example substitution was required.

---

## Overall Status: PASS (with 1 inconsistency found)

**Summary**: 7 validation areas checked. 6 areas PASS with no issues. 1 area (Output Template Alignment) has a minor but actionable inconsistency in the `threats.md` template where 5 of 6 STRIDE table template rows are missing the `Status` column while all 6 example rows include it correctly.

---

## 1. Carry-Forward Algorithm Consistency

**File**: `.claude/agents/tachi/orchestrator.md` (Phase 0 + Phase 1a)

| Check | Status | Details |
|-------|--------|---------|
| Phase 0 feeds Phase 1a | PASS | Phase 0 produces `baseline.present`, `baseline.source`, `baseline.date`, `baseline.finding_count`, `baseline.run_id`, and `registry[]`. Phase 1a consumes these directly. The handoff at line 405 is explicit: "proceed to Phase 1a (if baseline is present) or Phase 2 (if no baseline)." |
| Phase 1a skip condition | PASS | Line 411: "Skip this phase entirely when `baseline.present` is false." Proceeds directly to Phase 2. |
| Classification covers all cases | PASS | Three-step algorithm (lines 419-431) covers: (1) component absent = RESOLVED, (2) category inapplicable = RESOLVED, (3a) context unchanged = UNCHANGED, (3b) context changed = UPDATED. All four delta_status values (UNCHANGED, UPDATED, RESOLVED, NEW) are produced -- NEW is assigned in Phase 3a for genuinely new discoveries. |
| RESOLVED: component removal | PASS | Lines 450-451: "Component '{name}' removed from architecture" resolution reason documented. |
| RESOLVED: threat category inapplicability | PASS | Lines 452: "Threat category '{category}' no longer applicable to '{component}' (reclassified as {new_dfd_type})" resolution reason documented. |
| Component rename/refactor detection | PASS | Lines 456-460: Uses `primaryLocationLineHash` matching AND same DFD element type to detect renames. Classifies as UPDATED (not RESOLVED + NEW). Finding retains baseline ID. |
| Partial fix = UPDATED, not RESOLVED | PASS | Lines 454: Explicit rule that partial fixes are UPDATED, not RESOLVED. |

**Verdict**: PASS -- The carry-forward algorithm is internally consistent. Phase 0 output feeds Phase 1a correctly. All classification cases are covered with no gaps.

---

## 2. Score Inheritance Consistency

**File**: `.claude/agents/tachi/risk-scorer.md` (Baseline-Aware Scoring section)

| Check | Status | Details |
|-------|--------|---------|
| UNCHANGED: all fields copied verbatim | PASS | Lines 56-68: Seven fields explicitly listed (cvss_base, cvss_vector, exploitability, scalability, reachability, composite_score, severity_band). `score_source = "inherited"`. "Zero drift guarantee" stated: "Inherited scores are byte-identical to the baseline." |
| UPDATED: re-scored fresh | PASS | Lines 48-52: Table shows UPDATED -> "Re-score fresh using full 4-dimensional model", `score_source = "fresh"`. |
| NEW: bounded scoring | PASS | Lines 406-434: Bounded scoring within +/-1.0 of category defaults. Category default table with 8 categories and computed ranges provided. Bounding formula explicit: `min_score = max(0.0, category_default - 1.0)`, `max_score = min(10.0, category_default + 1.0)`. Edge cases at extremes documented. |
| NEW: bounding only for NEW | PASS | Lines 430-431: "Only to NEW findings from Phase 2 isolated discovery. UPDATED findings are re-scored fresh without bounding. UNCHANGED and RESOLVED findings inherit scores verbatim." |
| RESOLVED: retain last-known scores | PASS | Line 53: Table shows RESOLVED -> "Retain last-known scores from baseline", `score_source = "inherited"`. |
| Governance field preservation | PASS | Lines 502-529: Detailed carry-forward rules by delta status. UNCHANGED: all four governance fields carry forward verbatim. UPDATED: `risk_owner` always carried forward (never auto-overwritten); SLA/disposition/review_date carry forward unless severity band changed. NEW: assigned fresh. RESOLVED: retained from baseline. |
| score_source field in schema | PASS | `schemas/risk-scoring.yaml` lines 81-91: `score_source` field with enum `[inherited, fresh]`, default `"fresh"`, description matches agent behavior. |
| score_bounds field in schema | PASS | `schemas/risk-scoring.yaml` lines 93-108: `score_bounds` object with `min`/`max` properties, nullable, description matches agent bounding behavior. |

**Verdict**: PASS -- Score inheritance rules are consistent between the risk-scorer agent and the risk-scoring schema. All four delta_status treatments are documented and aligned.

---

## 3. Control Carry-Forward Consistency

**File**: `.claude/agents/tachi/control-analyzer.md` (Baseline-Aware Control Analysis section)

| Check | Status | Details |
|-------|--------|---------|
| UNCHANGED: control fields copied | PASS | Lines 107-116: Seven fields listed (control_status, control_evidence, control_category, control_effectiveness, reduction_factor, residual_score, residual_severity_band). All copied verbatim from baseline. |
| control_carry_forward = true for UNCHANGED | PASS | Line 117: "Set `control_carry_forward` to `true` and `rescan_scope` to `\"incremental\"`." |
| control_carry_forward = false for NEW/UPDATED/RESOLVED | PASS | Lines 98-103: Table shows NEW/UPDATED -> `false`, RESOLVED -> `N/A` (skipped). Schema (compensating-controls.yaml) line 104: "False for NEW, UPDATED, and RESOLVED findings." |
| rescan_scope = incremental when carry-forward active | PASS | Lines 123-124: "Set `rescan_scope` to `\"incremental\"` when any findings are inherited, `\"full\"` when all are fresh." |
| Schema alignment: control_carry_forward | PASS | `schemas/compensating-controls.yaml` lines 96-104: Boolean, required, default false, description matches agent. |
| Schema alignment: rescan_scope | PASS | `schemas/compensating-controls.yaml` lines 106-117: Enum `[full, incremental]`, required, default "full", description matches agent. |
| Template alignment: rescan_scope frontmatter | PASS | `templates/tachi/output-schemas/compensating-controls.md` line 26: `rescan_scope` field present with description matching schema. |
| Template alignment: carry_forward_count frontmatter | PASS | `templates/tachi/output-schemas/compensating-controls.md` line 27: `carry_forward_count` field present. |

**Verdict**: PASS -- Control carry-forward logic is consistent across the control-analyzer agent, compensating-controls schema, and compensating-controls.md template.

---

## 4. Output Template Alignment

**File**: `templates/tachi/output-schemas/threats.md`

| Check | Status | Details |
|-------|--------|---------|
| Baseline frontmatter fields | PASS | Lines 27-31: `baseline.source`, `baseline.date`, `baseline.finding_count`, `baseline.run_id` all present. Nullable. Matches orchestrator Phase 0 output. |
| Coverage gate frontmatter fields | PASS | Lines 32-33: `coverage_gate.status` and `coverage_gate.gaps` present. Values match orchestrator Phase 3b output. |
| Delta status column in Section 3.1 (Spoofing) template row | PASS | Line 243-245: Template row includes `Status` column with `_{NEW \| UNCHANGED \| UPDATED}_`. |
| Delta status column in Section 3.2 (Tampering) template row | **FAIL** | Line 257: Template row is `\| ID \| Component \| Threat \| ...` -- **missing** `Status` column. The example row on line 263 correctly includes Status. |
| Delta status column in Section 3.3 (Repudiation) template row | **FAIL** | Line 271: Template row missing `Status` column. Example row on line 277 correctly includes it. |
| Delta status column in Section 3.4 (Info Disclosure) template row | **FAIL** | Line 285: Template row missing `Status` column. Example row on line 291 correctly includes it. |
| Delta status column in Section 3.5 (Denial of Service) template row | **FAIL** | Line 299: Template row missing `Status` column. Example row on line 305 correctly includes it. |
| Delta status column in Section 3.6 (Elevation of Privilege) template row | **FAIL** | Line 313: Template row missing `Status` column. Example row on line 317 (when checked) correctly includes it. |
| Delta status column in AI tables (4.1 Agentic) | PASS | Line 342-343: Both template and example rows include `Status` column. |
| Delta status column in AI tables (4.2 LLM) | PASS | Line 356-357: Both template and example rows include `Status` column. |
| Section 4b (Resolved Findings) structure | PASS | Lines 389-417: Table has `ID \| Component \| Threat \| Last Risk Level \| Resolution Reason` columns. Matches orchestrator `resolved_findings` output fields (id, component, threat, risk_level, resolution_reason). "When no baseline is present" and "when baseline present but no resolved" behaviors both documented. |
| Section 5a (Coverage Gate Results) | PASS | Lines 446-490: Coverage Requirements Matrix and Gap Resolution Details tables present. Component type column matches coverage-checklists.yaml types. Resolution values match orchestrator Phase 3b Step 5 outputs. |
| Status column description text | PASS | Lines 228-229: Status column semantics correctly documented: "NEW (discovered this run), UNCHANGED (identical to baseline), UPDATED (component context changed). RESOLVED findings appear in Section 4b, not in these tables." |

**Verdict**: FAIL (minor) -- The `Status` column is present in the Section 3.1 Spoofing template row and in all example rows across all STRIDE tables, but **missing from the template (placeholder) rows** in Sections 3.2 through 3.6. The template rows for Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege lack the `Status` column. This is an inconsistency within the template file itself -- the examples are correct, but the template schemas do not match. An agent following the template row structure literally would omit the Status column for 5 of 6 STRIDE categories.

---

## 5. Schema Consistency

**Files**: `schemas/finding.yaml`, `schemas/risk-scoring.yaml`, `schemas/compensating-controls.yaml`, `schemas/coverage-checklists.yaml`

| Check | Status | Details |
|-------|--------|---------|
| finding.yaml: delta_status field | PASS | Lines 123-138: Enum `[NEW, UNCHANGED, UPDATED, RESOLVED]`, `required_when: baseline_present`, `default: NEW`. All four values documented with descriptions. |
| finding.yaml: baseline_run_id field | PASS | Lines 140-149: String, nullable, format described. Examples include both a run_id and null. |
| finding.yaml: schema_version = 1.1 | PASS | Line 13: `schema_version: "1.1"` (updated from pre-baseline 1.0). |
| risk-scoring.yaml: score_source field | PASS | Lines 81-91: Enum `[inherited, fresh]`, required, default "fresh". Description covers UNCHANGED (inherited) and NEW/UPDATED (fresh). |
| risk-scoring.yaml: score_bounds field | PASS | Lines 93-108: Object with min/max properties, nullable, range [0.0, 10.0]. Description covers bounded scoring for NEW findings. |
| risk-scoring.yaml: schema_version = 1.1 | PASS | Line 13: `schema_version: "1.1"`. |
| compensating-controls.yaml: control_carry_forward field | PASS | Lines 96-104: Boolean, required, default false. Description covers true (UNCHANGED) and false (NEW, UPDATED, RESOLVED). |
| compensating-controls.yaml: rescan_scope field | PASS | Lines 106-117: Enum `[full, incremental]`, required, default "full". Description covers both values. |
| compensating-controls.yaml: schema_version = 1.1 | PASS | Line 13: `schema_version: "1.1"`. |
| coverage-checklists.yaml: component types | PASS | Lines 38-108: Six types defined: external_entity, process, data_store, data_flow, llm_process, mcp_server. These match the orchestrator Phase 3b Step 1 (Component Type Determination) and Step 2 (Required Category Lookup). |
| coverage-checklists.yaml: llm_process detection keywords | PASS | Lines 73-79: Keywords match orchestrator Phase 3b text (llm, language model, gpt, claude, ai model, inference). |
| coverage-checklists.yaml: mcp_server detection keywords | PASS | Lines 93-98: Keywords match orchestrator Phase 3b text (mcp, model context protocol, tool server, plugin host). |
| coverage-checklists.yaml: required categories alignment | PASS | All required categories per type match the orchestrator Phase 3b Step 2 table exactly. |

**Verdict**: PASS -- All baseline-aware fields are documented in their respective schemas with correct types, enums, and descriptions. Coverage checklist component types and detection keywords are consistent with orchestrator expectations.

---

## 6. SARIF Template Alignment

**File**: `templates/tachi/output-schemas/threats.sarif`

| Check | Status | Details |
|-------|--------|---------|
| baselineState property in result properties | PASS | Lines 109, 144: `"baselineState": "<new\|unchanged\|updated\|absent>"` present in both example results. |
| baselineRunId in partialFingerprints | PASS | Lines 106, 141: `"baselineRunId": "<baseline-run-id-or-empty-for-first-run>"` present in both example results. |
| Value mapping: new -> NEW | PASS | SARIF uses lowercase `new` which maps to pipeline `NEW`. Standard SARIF 2.1.0 convention. |
| Value mapping: unchanged -> UNCHANGED | PASS | Lowercase `unchanged` maps to `UNCHANGED`. |
| Value mapping: updated -> UPDATED | PASS | Lowercase `updated` maps to `UPDATED`. |
| Value mapping: absent -> RESOLVED | PASS | SARIF 2.1.0 uses `absent` for findings no longer present; this correctly maps to the pipeline's `RESOLVED` status. The SARIF specification defines `absent` as "the result was detected in the baseline but not in the current run." |
| risk-scores.sarif: score-source property | PASS | Lines 309, 356: `"score-source": "<inherited\|fresh>"` present. |
| risk-scores.sarif: baseline-state property | PASS | Lines 310, 357: `"baseline-state": "<new\|unchanged\|updated\|absent>"` present. |
| compensating-controls.sarif: control-carry-forward | PASS | Lines 347, 411, 453, 517, 597: `"control-carry-forward": "<true\|false>"` present in all example results. |

**Verdict**: PASS -- SARIF templates correctly include all baseline-aware properties. The `absent` -> `RESOLVED` mapping follows SARIF 2.1.0 conventions.

---

## 7. Cross-File References

**Files checked**: orchestrator.md, risk-scorer.md, control-analyzer.md

| Reference | Declared In | Target File | Exists |
|-----------|-------------|-------------|--------|
| `schemas/finding.yaml` | orchestrator.md metadata | `schemas/finding.yaml` | YES |
| `schemas/input.yaml` | orchestrator.md metadata | `schemas/input.yaml` | YES |
| `schemas/output.yaml` | orchestrator.md metadata | `schemas/output.yaml` | YES |
| `schemas/report.yaml` | orchestrator.md metadata | `schemas/report.yaml` | YES |
| `schemas/risk-scoring.yaml` | risk-scorer.md (referenced) | `schemas/risk-scoring.yaml` | YES |
| `schemas/compensating-controls.yaml` | control-analyzer.md metadata | `schemas/compensating-controls.yaml` | YES |
| `schemas/coverage-checklists.yaml` | orchestrator.md Phase 3b | `schemas/coverage-checklists.yaml` | YES |
| `templates/tachi/output-schemas/threats.md` | orchestrator.md metadata | `templates/tachi/output-schemas/threats.md` | YES |
| `templates/tachi/output-schemas/threats.sarif` | orchestrator.md metadata | `templates/tachi/output-schemas/threats.sarif` | YES |
| `templates/tachi/output-schemas/threat-report.md` | orchestrator.md metadata | `templates/tachi/output-schemas/threat-report.md` | YES |
| `templates/tachi/output-schemas/risk-scores.md` | risk-scorer.md (referenced) | `templates/tachi/output-schemas/risk-scores.md` | YES |
| `templates/tachi/output-schemas/risk-scores.sarif` | risk-scorer.md (referenced) | `templates/tachi/output-schemas/risk-scores.sarif` | YES |
| `templates/tachi/output-schemas/compensating-controls.md` | control-analyzer.md metadata | `templates/tachi/output-schemas/compensating-controls.md` | YES |
| `templates/tachi/output-schemas/compensating-controls.sarif` | control-analyzer.md metadata | `templates/tachi/output-schemas/compensating-controls.sarif` | YES |
| `docs/INTERFACE-CONTRACT.md` | orchestrator.md metadata | `docs/INTERFACE-CONTRACT.md` | YES |
| `.claude/skills/tachi-orchestration/references/sarif-specification.md` | orchestrator.md Skill References | `.claude/skills/tachi-orchestration/references/sarif-specification.md` | YES |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | orchestrator.md Skill References | `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | YES |
| `.claude/skills/tachi-orchestration/references/output-schemas.md` | orchestrator.md Skill References | `.claude/skills/tachi-orchestration/references/output-schemas.md` | YES |
| `.claude/skills/tachi-orchestration/references/baseline-correlation.md` | orchestrator.md Phase 1a | `.claude/skills/tachi-orchestration/references/baseline-correlation.md` | YES |
| `.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md` | risk-scorer.md Skill References | `.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md` | YES |
| `.claude/skills/tachi-risk-scoring/references/cvss-vectors.md` | risk-scorer.md Skill References | `.claude/skills/tachi-risk-scoring/references/cvss-vectors.md` | YES |
| `.claude/skills/tachi-risk-scoring/references/severity-bands.md` | risk-scorer.md Skill References | `.claude/skills/tachi-risk-scoring/references/severity-bands.md` | YES |
| `.claude/skills/tachi-control-analysis/references/control-categories.md` | control-analyzer.md Skill References | `.claude/skills/tachi-control-analysis/references/control-categories.md` | YES |
| `.claude/skills/tachi-control-analysis/references/evidence-criteria.md` | control-analyzer.md Skill References | `.claude/skills/tachi-control-analysis/references/evidence-criteria.md` | YES |
| `.claude/skills/tachi-control-analysis/references/residual-risk.md` | control-analyzer.md Skill References | `.claude/skills/tachi-control-analysis/references/residual-risk.md` | YES |
| `adapters/claude-code/agents/references/sarif-generation.md` | control-analyzer.md metadata | `adapters/claude-code/agents/references/sarif-generation.md` | YES |

**Verdict**: PASS -- All 26 cross-file references resolve to existing files. No broken references found.

---

## Findings Summary

| # | Area | Status | Issues |
|---|------|--------|--------|
| 1 | Carry-Forward Algorithm Consistency | PASS | None |
| 2 | Score Inheritance Consistency | PASS | None |
| 3 | Control Carry-Forward Consistency | PASS | None |
| 4 | Output Template Alignment | **FAIL** (minor) | 5 of 6 STRIDE template rows in threats.md missing Status column |
| 5 | Schema Consistency | PASS | None |
| 6 | SARIF Template Alignment | PASS | None |
| 7 | Cross-File References | PASS | None |

---

## Actionable Issue

**Issue ID**: VAL-074-001
**Severity**: Minor (template inconsistency, not logic error)
**File**: `templates/tachi/output-schemas/threats.md`
**Location**: Sections 3.2 through 3.6 template (placeholder) rows

**Description**: The template row (the row showing placeholder values like `_{T-N}_`) in STRIDE Sections 3.2 (Tampering), 3.3 (Repudiation), 3.4 (Information Disclosure), 3.5 (Denial of Service), and 3.6 (Elevation of Privilege) is missing the `Status` column. Section 3.1 (Spoofing) correctly includes it. All example rows across all six sections correctly include the `Status` column.

**Impact**: An LLM agent using the template row (not the example) as a structural guide for Sections 3.2-3.6 could omit the delta status annotation from those tables. The risk is low because (a) the introductory description at line 228-229 explicitly documents the Status column requirement, (b) all example rows are correct, and (c) the AI threat tables (4.1, 4.2) are correct in both template and example rows.

**Recommended Fix**: Add `| Status |` column and corresponding `| _{NEW \| UNCHANGED \| UPDATED}_ |` placeholder to the template rows in Sections 3.2 through 3.6, matching the existing Section 3.1 pattern.
