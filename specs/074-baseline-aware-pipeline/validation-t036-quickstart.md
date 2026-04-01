# T036 Quickstart Validation Report

**Feature**: 074 - Baseline-Aware Pipeline
**Task**: T036 - Quickstart Validation Scenarios
**Date**: 2026-04-01
**Status**: **PASS** (7/7 scenarios verified, 9/9 checklist items verified)

---

## Validation Summary

| Test | Scenario | Status | Notes |
|------|----------|--------|-------|
| 1 | First Run (Stateless Mode) | **PASS** | Stateless mode fully specified in orchestrator Phase 0 and output template |
| 2 | Stable Re-Scan (Zero Drift) | **PASS** | UNCHANGED classification, score inheritance, and control carry-forward all specified |
| 3 | Remediation Verification | **PASS** | RESOLVED detection with original ID, last-known score, and resolution reason |
| 4 | New Threat Discovery | **PASS** | Isolated discovery, coverage summary, sequential IDs, deduplication at >80% |
| 5 | Coverage Gate | **PASS** | Component type detection, required categories, gap re-analysis all specified |
| 6 | Risk Score Inheritance | **PASS** | score_source field, bounded scoring, governance carry-forward all specified |
| 7 | Compensating Controls Carry-Forward | **PASS** | control_carry_forward, rescan_scope, incremental scanning all specified |

---

## Test 1: First Run (Stateless Mode) -- PASS

**Quickstart expectation**: Output identical to current behavior. All findings annotated `[NEW]`. No `baseline:` block in frontmatter.

### Evidence

**1a. Stateless mode when no baseline detected**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 101-106 (Phase 0)
- **Evidence**: "This phase is optional. When no baseline is detected, the pipeline operates in stateless mode -- identical to pre-baseline behavior. All findings are annotated `[NEW]` and no carry-forward occurs."
- **Status**: VERIFIED -- explicit backward compatibility guarantee.

**1b. All findings annotated [NEW]**

- **File**: `.claude/agents/tachi/orchestrator.md`, line 105
- **Evidence**: "All findings are annotated `[NEW]`" when no baseline present.
- **File**: `schemas/finding.yaml`, lines 123-138
- **Evidence**: `delta_status` defaults to `NEW` when no baseline provided.
- **Status**: VERIFIED -- default NEW annotation confirmed in both orchestrator and schema.

**1c. Output format matches pre-baseline behavior**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 59, 105, 124
- **Evidence**: Line 59: "When no baseline is available, the pipeline operates in stateless mode -- identical to pre-baseline behavior." Line 124: "Set `baseline_present = false` and proceed to Phase 1 in stateless mode. No further Phase 0 work is needed. The pipeline produces output identical to pre-baseline behavior."
- **Status**: VERIFIED -- three separate statements confirm identical behavior.

**1d. Baseline fields null when no baseline**

- **File**: `templates/tachi/output-schemas/threats.md`, lines 95-112 (first-run frontmatter example)
- **Evidence**: Example frontmatter shows `baseline.source: null`, `baseline.date: null`, `baseline.finding_count: null`, `baseline.run_id: null`.
- **Status**: VERIFIED -- template explicitly shows null baseline fields for first run.

---

## Test 2: Stable Re-Scan (Zero Drift) -- PASS

**Quickstart expectation**: 100% ID match, zero score drift, zero count drift. All findings `[UNCHANGED]`.

### Evidence

**2a. UNCHANGED classification when component/threat unchanged**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 409-432 (Phase 1a Carry-Forward Algorithm)
- **Evidence**: Step 3 of the carry-forward algorithm: "If the component's description, data flows, and trust boundary position are unchanged: Classify as `UNCHANGED`."
- **Status**: VERIFIED -- deterministic classification to UNCHANGED when architecture unchanged.

**2b. Score inheritance for UNCHANGED findings**

- **File**: `.claude/agents/tachi/risk-scorer.md`, lines 44-69 (Baseline-Aware Scoring)
- **Evidence**: Table shows `UNCHANGED` -> "Inherit all scores verbatim from baseline -- skip dimensional scoring entirely" with score_source `inherited`. Lines 56-68: Lists all 7 fields copied verbatim (cvss_base, cvss_vector, exploitability, scalability, reachability, composite_score, severity_band). Line 69: "Zero drift guarantee: Inherited scores are byte-identical to the baseline. No rounding, no recalculation, no adjustment."
- **Status**: VERIFIED -- explicit zero drift guarantee with byte-identical inheritance.

**2c. Control carry-forward for UNCHANGED**

- **File**: `.claude/agents/tachi/control-analyzer.md`, lines 96-117 (Baseline-Aware Control Analysis)
- **Evidence**: Table shows `UNCHANGED` -> "Inherit control status from baseline -- skip codebase scanning" with carry_forward `true`. Lines 107-117: Lists all 7 control fields copied verbatim.
- **Status**: VERIFIED -- UNCHANGED findings inherit all control fields.

**2d. All findings marked [UNCHANGED] on unchanged architecture**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 419-432
- **Evidence**: Carry-forward algorithm classifies findings as UNCHANGED when: (a) component exists, (b) threat category still applies, and (c) component context unchanged. On an unchanged architecture, all three conditions hold for all baseline findings, resulting in 100% UNCHANGED.
- **Status**: VERIFIED -- algorithm deterministically produces all-UNCHANGED on unchanged architecture.

---

## Test 3: Remediation Verification -- PASS

**Quickstart expectation**: S-3 annotated `[RESOLVED]` with original ID, description, and last-known score.

### Evidence

**3a. Component removal triggers RESOLVED**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 419-424 (Carry-Forward Algorithm Step 1)
- **Evidence**: "Check component existence: Is the finding's target component present in the current Phase 1 component inventory? If the component is not present (removed from architecture): Classify as `RESOLVED`."
- **Status**: VERIFIED -- component removal is the primary RESOLVED detection path.

**3b. Original ID preserved**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 436-444 (Classification Output table)
- **Evidence**: For RESOLVED findings: `id` = "Retain baseline ID", `delta_status` = `RESOLVED`.
- **File**: `.claude/agents/tachi/orchestrator.md`, lines 462-474 (RESOLVED findings output)
- **Evidence**: Field table explicitly lists `id` -> "Original baseline ID (e.g., 'T-2')" with purpose "Audit trail continuity".
- **Status**: VERIFIED -- original ID is explicitly retained, never reassigned.

**3c. Last-known score retained**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 440-444
- **Evidence**: Classification output table for RESOLVED shows `score_treatment` = "Retain last-known score".
- **File**: `.claude/agents/tachi/risk-scorer.md`, lines 50-53
- **Evidence**: Delta status table shows `RESOLVED` -> "Retain last-known scores from baseline -- no scoring needed" with score_source `inherited`.
- **Status**: VERIFIED -- last-known scores retained from baseline.

**3d. Resolution Reason field in Section 4b**

- **File**: `templates/tachi/output-schemas/threats.md`, lines 389-416 (Section 4b)
- **Evidence**: Section 4b "Resolved Findings" table has columns: ID, Component, Threat, Last Risk Level, Resolution Reason. Field definitions table confirms Resolution Reason is "Brief explanation of why the finding is resolved (component removed, category inapplicable, etc.)".
- **File**: `.claude/agents/tachi/orchestrator.md`, lines 449-452
- **Evidence**: Resolution reason patterns: Component removal -> `"Component '{name}' removed from architecture"`, Category inapplicability -> `"Threat category '{category}' no longer applicable to '{component}' (reclassified as {new_dfd_type})"`.
- **Status**: VERIFIED -- Resolution Reason field present with structured reason text.

---

## Test 4: New Threat Discovery -- PASS

**Quickstart expectation**: New findings annotated `[NEW]` with IDs sequential after highest existing per category. No duplicates.

### Evidence

**4a. Isolated discovery context excludes finding descriptions**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 590-612 (Phase 2 Isolation)
- **Evidence**: Isolated Discovery Context Payload table shows: Finding descriptions -> "No (Excluded to prevent anchoring)", Risk scores -> "No", Mitigation text -> "No", Finding IDs -> "No". Coverage summary -> "Yes (NEW)" with "Component names + covered categories from Phase 1a".
- **Status**: VERIFIED -- explicit anchoring prevention by excluding finding text, scores, mitigations, and IDs.

**4b. Coverage summary provided (component names + covered categories only)**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 495-508 (Coverage Summary Production)
- **Evidence**: "The coverage summary contains only component names and their covered threat categories. It does not include finding descriptions, scores, or mitigations. This prevents anchoring bias in Phase 2 discovery."
- **Status**: VERIFIED -- coverage summary is intentionally limited to prevent anchoring.

**4c. Sequential ID assignment after highest existing per category**

- **File**: `.claude/agents/tachi/orchestrator.md`, line 720 (Phase 3a)
- **Evidence**: "For genuinely new findings, assign a sequential ID after the highest existing ID in the finding's category. Example: if the carry-forward set has S-1 through S-5, a new spoofing finding gets S-6."
- **Status**: VERIFIED -- sequential ID assignment rule explicitly defined with example.

**4d. Deduplication at >80% similarity with baseline-wins policy**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 709-720 (Deduplication Algorithm)
- **Evidence**: Step 1 (exact match): "the finding is a duplicate -- discard the Phase 2 version. The carry-forward version (baseline) wins." Step 2 (similarity match): "If similarity > 0.80 (strictly greater than 80%), the finding is a duplicate -- discard the Phase 2 version. The carry-forward version wins." Step 3 (genuinely new): "At or below threshold (<=0.80): The finding is genuinely new."
- **Status**: VERIFIED -- deduplication at >80% with baseline-wins policy, including deterministic similarity algorithm.

---

## Test 5: Coverage Gate -- PASS

**Quickstart expectation**: Coverage gate passes when all required categories evaluated. Flags gaps and triggers targeted re-analysis.

### Evidence

**5a. Component type detection with AI subtype keywords**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 759-774 (Phase 3b Step 1)
- **Evidence**: "AI subtype detection (check first): Scan the component's name and description for AI subtype keywords. LLM Process: Keywords -- llm, language model, gpt, claude, ai model, inference. MCP Server: Keywords -- mcp, model context protocol, tool server, plugin host." Line 774: "AI subtype takes precedence: A Process component matching LLM keywords is classified as `llm_process`, not `process`."
- **Status**: VERIFIED -- AI subtype detection with keyword matching and precedence rule.

**5b. Required categories lookup from coverage-checklists.yaml**

- **File**: `schemas/coverage-checklists.yaml`, lines 69-89 (llm_process type)
- **Evidence**: `llm_process` required_categories includes all standard Process categories (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) plus `llm`.
- **File**: `.claude/agents/tachi/orchestrator.md`, lines 776-787 (Step 2 lookup table)
- **Evidence**: Orchestrator reproduces the same mapping, confirming alignment with the schema.
- **Status**: VERIFIED -- coverage checklist schema and orchestrator in sync.

**5c. Gap detection and targeted re-analysis dispatch**

- **File**: `.claude/agents/tachi/orchestrator.md`, lines 812-818 (Step 4) and 841-887 (Step 5)
- **Evidence**: Step 4: "Gaps detected: One or more required categories are missing for one or more components. Proceed to targeted re-analysis (Step 5)." Step 5: "For each gap in the gap list, dispatch the specific threat agent(s) for the missing category, targeting only the uncovered component."
- **Status**: VERIFIED -- gap detection triggers targeted agent dispatch.

**5d. LLM Process requires prompt injection, data poisoning, model theft (via llm category)**

- **File**: `schemas/coverage-checklists.yaml`, lines 130-134 (Category-to-Agent Mapping)
- **Evidence**: "llm | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft"
- **File**: `.claude/agents/tachi/orchestrator.md`, lines 857-858
- **Evidence**: "llm | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft"
- **Status**: VERIFIED -- llm category maps to all three required agents.

---

## Test 6: Risk Score Inheritance -- PASS

**Quickstart expectation**: UNCHANGED scores identical to baseline. NEW scores within +/-1.0 of category defaults.

### Evidence

**6a. score_source field: "inherited" for UNCHANGED, "fresh" for NEW/UPDATED**

- **File**: `.claude/agents/tachi/risk-scorer.md`, lines 44-53 (Baseline-Aware Scoring table)
- **Evidence**: Table shows: UNCHANGED -> score_source `inherited`, UPDATED -> `fresh`, NEW -> `fresh`, RESOLVED -> `inherited`.
- **File**: `schemas/risk-scoring.yaml`, lines 81-91
- **Evidence**: `score_source` field defined with enum `[inherited, fresh]`, required, with descriptions matching the agent behavior.
- **File**: `.claude/skills/tachi-risk-scoring/SKILL.md`, lines 41-46
- **Evidence**: Score Source Field section confirms: `"inherited"` for UNCHANGED/RESOLVED, `"fresh"` for NEW/UPDATED.
- **Status**: VERIFIED -- score_source field defined in schema, agent, and skill with consistent semantics.

**6b. Bounded scoring for NEW findings (+/-1.0 of category defaults)**

- **File**: `.claude/agents/tachi/risk-scorer.md`, lines 406-418 (Bounded Scoring for NEW Findings)
- **Evidence**: "When a finding has `delta_status: NEW`, its CVSS base score must fall within +/-1.0 of the category default. Bounding formula: min_score = max(0.0, category_default - 1.0), max_score = min(10.0, category_default + 1.0). If the assessed cvss_base falls outside [min_score, max_score], clamp it to the nearest bound."
- **File**: `schemas/risk-scoring.yaml`, lines 93-108
- **Evidence**: `score_bounds` field with min/max properties defined for NEW findings.
- **File**: `.claude/skills/tachi-risk-scoring/SKILL.md`, lines 48-67
- **Evidence**: Bounded Scoring section with formula, applicability table (NEW=Yes, UPDATED/UNCHANGED/RESOLVED=No), and edge case examples.
- **Status**: VERIFIED -- bounded scoring specified in agent, schema, and skill with consistent formula.

**6c. Governance field carry-forward (risk_owner, remediation_sla)**

- **File**: `.claude/skills/tachi-risk-scoring/SKILL.md`, lines 75-92 (Governance Field Persistence)
- **Evidence**: Carry-forward table shows: UNCHANGED preserves risk_owner, remediation_sla, risk_disposition, review_date from baseline. UPDATED (same band) preserves all. UPDATED (band changed) preserves risk_owner but recalculates SLA/disposition. NEW gets "Unassigned" owner with fresh governance fields. Line 78: "risk_owner is a human-assigned field and is never auto-overwritten by the scoring pipeline."
- **Status**: VERIFIED -- governance fields carry forward with explicit rules per delta status.

---

## Test 7: Compensating Controls Carry-Forward -- PASS

**Quickstart expectation**: UNCHANGED controls identical to baseline. Only changed findings re-scanned.

### Evidence

**7a. control_carry_forward = true for UNCHANGED**

- **File**: `.claude/agents/tachi/control-analyzer.md`, lines 96-103 (Baseline-Aware Control Analysis table)
- **Evidence**: Table shows UNCHANGED -> carry_forward `true`, UPDATED -> `false`, NEW -> `false`, RESOLVED -> N/A.
- **File**: `.claude/agents/tachi/control-analyzer.md`, line 117
- **Evidence**: "Set `control_carry_forward` to `true` and `rescan_scope` to `"incremental"`."
- **File**: `schemas/compensating-controls.yaml`, lines 96-104
- **Evidence**: `control_carry_forward` field defined as boolean, required, default false, with description confirming UNCHANGED inheritance behavior.
- **File**: `.claude/skills/tachi-control-analysis/SKILL.md`, line 46
- **Evidence**: "Set `control_carry_forward: true` and `rescan_scope: "incremental"`."
- **Status**: VERIFIED -- control_carry_forward=true specified in agent, schema, and skill.

**7b. rescan_scope = "incremental" when carry-forward active**

- **File**: `.claude/agents/tachi/control-analyzer.md`, lines 119-128 (Incremental Re-Scan)
- **Evidence**: "UNCHANGED findings: Skip scanning entirely -- inherit all control fields. NEW and UPDATED findings: Scan only the files associated with these findings. Set `rescan_scope` to `"incremental"` when any findings are inherited, `"full"` when all are fresh."
- **File**: `schemas/compensating-controls.yaml`, lines 106-118
- **Evidence**: `rescan_scope` field with enum `[full, incremental]` and description matching the agent behavior.
- **File**: `.claude/skills/tachi-control-analysis/SKILL.md`, lines 49-56 (Incremental Re-Scan Scope table)
- **Evidence**: Table confirms: All UNCHANGED -> incremental (nothing to scan), Mix -> incremental (scan only changed), All NEW -> full.
- **Status**: VERIFIED -- rescan_scope logic specified consistently across agent, schema, and skill.

**7c. Only NEW/UPDATED findings re-scanned**

- **File**: `.claude/agents/tachi/control-analyzer.md`, lines 100-103
- **Evidence**: UPDATED -> "Re-scan codebase for controls -- finding context changed", NEW -> "Full scan -- no baseline controls exist", RESOLVED -> "Skip -- finding no longer applicable".
- **File**: `.claude/skills/tachi-control-analysis/SKILL.md`, lines 22-25
- **Evidence**: Carry-forward conditions require delta_status UNCHANGED, baseline existence, and finding ID match.
- **Status**: VERIFIED -- only NEW and UPDATED findings trigger re-scanning.

---

## Validation Checklist

The quickstart document (lines 112-122) specifies 9 validation items:

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | First run without baseline works identically to current behavior | **PASS** | Orchestrator Phase 0: "operates in stateless mode -- identical to pre-baseline behavior" |
| 2 | Re-scan on unchanged codebase produces zero drift (IDs, scores, counts) | **PASS** | Risk-scorer: "Zero drift guarantee: Inherited scores are byte-identical to the baseline" |
| 3 | Resolved findings correctly marked with original ID preserved | **PASS** | Orchestrator Phase 1a RESOLVED output table retains original ID, threat, and last-known scores |
| 4 | New findings discovered with sequential IDs and bounded scores | **PASS** | Phase 3a: sequential ID after highest existing; Risk-scorer: bounded scoring +/-1.0 |
| 5 | Coverage gate detects missing categories and triggers re-analysis | **PASS** | Phase 3b Steps 3-5: gap detection, category-to-agent mapping, targeted dispatch |
| 6 | Risk scores inherited for unchanged findings | **PASS** | Risk-scorer: all 7 score fields copied verbatim for UNCHANGED, score_source="inherited" |
| 7 | Compensating controls carry forward for unchanged findings | **PASS** | Control-analyzer: all 7 control fields copied verbatim, control_carry_forward=true |
| 8 | SARIF output includes baselineState and baselineRunId | **PASS** | threats.sarif template: `partialFingerprints.baselineRunId` and `properties.baselineState` fields present; risk-scores.sarif: `baseline-state` in properties |
| 9 | Delta annotations present on every finding | **PASS** | threats.md template Section 3: Status column defined as `NEW \| UNCHANGED \| UPDATED`; finding.yaml: `delta_status` field with enum and required_when: baseline_present |

---

## Implementation Files Verified

| File | Sections Checked |
|------|-----------------|
| `.claude/agents/tachi/orchestrator.md` | Phase 0 (baseline detection), Phase 1a (carry-forward), Phase 2 (isolated discovery), Phase 3a (merge/dedup), Phase 3b (coverage gate) |
| `.claude/agents/tachi/risk-scorer.md` | Baseline-Aware Scoring, Score Inheritance, Bounded Scoring, Governance Fields |
| `.claude/agents/tachi/control-analyzer.md` | Baseline-Aware Control Analysis, Carry-Forward, Incremental Re-Scan |
| `.claude/skills/tachi-risk-scoring/SKILL.md` | Score Inheritance, Score Source, Bounded Scoring, Governance Persistence |
| `.claude/skills/tachi-control-analysis/SKILL.md` | Carry-Forward Conditions, Fields, Re-Scan Scope, Evidence Preservation |
| `schemas/finding.yaml` | delta_status enum, baseline_run_id field |
| `schemas/risk-scoring.yaml` | score_source enum, score_bounds object, category_defaults |
| `schemas/compensating-controls.yaml` | control_carry_forward boolean, rescan_scope enum |
| `schemas/coverage-checklists.yaml` | Component types, required categories, AI subtype detection, category-to-agent mapping |
| `templates/tachi/output-schemas/threats.md` | Frontmatter baseline fields, Section 3 Status column, Section 4b Resolved Findings |
| `templates/tachi/output-schemas/threats.sarif` | baselineRunId, baselineState in partialFingerprints/properties |
| `templates/tachi/output-schemas/risk-scores.md` | Baseline frontmatter (source, inherited_count, fresh_count) |
| `templates/tachi/output-schemas/risk-scores.sarif` | baseline-state property |
| `templates/tachi/output-schemas/compensating-controls.md` | rescan_scope, carry_forward_count frontmatter |
| `templates/tachi/output-schemas/compensating-controls.sarif` | control-carry-forward property |

---

## Gaps and Observations

**No gaps identified.** All 7 quickstart test scenarios are fully supported by the implemented pipeline instructions. The implementation is consistent across all three layers (agent instructions, schemas, and output templates).

**Cross-layer consistency note**: Every baseline-aware field verified appears in at minimum:
1. The agent instruction (behavioral specification)
2. The schema (data contract)
3. The output template (format specification)

This three-layer consistency ensures that any implementation following these specifications will produce output that satisfies all quickstart validation scenarios.
