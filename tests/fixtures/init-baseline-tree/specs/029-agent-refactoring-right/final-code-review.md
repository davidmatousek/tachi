# Code Review: Feature 029 — Agent Refactoring — Right-Size Orchestrator, Report, and Infographic Agents

**Reviewer**: code-reviewer
**Date**: 2026-03-25
**Branch**: `029-agent-refactoring-right`
**Verdict**: APPROVED_WITH_CONCERNS

---

## Review Scope

Reviewed all deliverables from Feature 029: 3 refactored core agent files and 6 new reference documents.

| File | Lines | Status |
|------|-------|--------|
| `adapters/claude-code/agents/orchestrator.md` | 1,273 | Refactored |
| `adapters/claude-code/agents/threat-report.md` | 472 | Refactored |
| `adapters/claude-code/agents/threat-infographic.md` | 414 | Refactored |
| `adapters/claude-code/agents/references/sarif-generation.md` | 499 | New |
| `adapters/claude-code/agents/references/validation-checklist.md` | 90 | New |
| `adapters/claude-code/agents/references/error-templates.md` | 131 | New |
| `adapters/claude-code/agents/references/report-templates.md` | 298 | New |
| `adapters/claude-code/agents/references/infographic-gemini-api.md` | 148 | New |
| `adapters/claude-code/agents/references/infographic-error-handling.md` | 67 | New |

---

## Findings

### WARNING Findings

#### W-1: Orchestrator line count exceeds spec target

- **File**: `adapters/claude-code/agents/orchestrator.md`
- **Issue**: Orchestrator is 1,273 lines. Spec SC-001 targets ~1,100-1,200 lines. The actual count is 73 lines (6%) over the upper bound of the target range.
- **Impact**: Minor deviation from spec metric. The plan (Section "Accepted residual") explicitly acknowledges the orchestrator at ~1,200 lines as an accepted position since ~1,400 lines are irreducible specification content. The architect approved with this understanding.
- **Fix**: Additional prose condensation could bring this into the 1,200-line range. The overshoot is marginal and was anticipated by the plan's "accepted residual" clause. If addressed, focus on Phase 1 and Phase 2 sections where verbose prose descriptions remain.

#### W-2: Report agent line count exceeds spec target

- **File**: `adapters/claude-code/agents/threat-report.md`
- **Issue**: Report agent is 472 lines. Spec SC-002 targets ~300-400 lines. The actual count is 72 lines (18%) over the upper bound.
- **Impact**: The plan acknowledged this risk explicitly: "The report agent's realistic floor is ~400-450 lines post-extraction" and noted the PM raised this as a non-blocking observation during plan review. The overshoot is higher than the plan's revised estimate of ~448 lines.
- **Fix**: Review the Remediation Roadmap Generation section (lines 391-473), which contains detailed effort estimation heuristics and correlation consolidation rules. Some of this content may be condensable, or a portion could be extracted to the existing `report-templates.md` reference document if it qualifies as consultation-only content.

#### W-3: Infographic agent line count exceeds spec target

- **File**: `adapters/claude-code/agents/threat-infographic.md`
- **Issue**: Infographic agent is 414 lines. Spec SC-003 targets ~300-400 lines. The actual count is 14 lines (3.5%) over the upper bound.
- **Impact**: Marginal overshoot. The remaining content appears to be specification content (input contract, data extraction methodology, infographic specification format) that cannot be further compressed without losing specification fidelity.
- **Fix**: Minor prose condensation in the Data Extraction Methodology section or Visual Design Directives section could bring this within range. Low priority given the small overshoot.

---

### SUGGESTION Findings

#### S-1: Frontmatter field naming inconsistency between spec and implementation

- **Files**: All 6 reference documents in `adapters/claude-code/agents/references/`
- **Issue**: FR-004 in `specs/029-agent-refactoring-right/spec.md` specifies `source-agent`, `loaded-at`, and `extracted-from` (kebab-case). The plan's "Frontmatter Standard" section defines `source_agent`, `loaded_at`, `extracted_from` (snake_case). The implementation follows the plan. This is a spec-to-plan naming discrepancy that was not caught during plan review.
- **Impact**: No functional impact. The plan was approved by PM and Architect with snake_case field names, and the implementation is internally consistent. YAML frontmatter commonly uses snake_case.
- **Fix**: Either update FR-004 in the spec to match the plan's snake_case convention, or note the deviation in the capability inventory. The implementation is correct per the approved plan.

#### S-2: Frontmatter includes `version` field not specified in FR-004

- **Files**: All 6 reference documents in `adapters/claude-code/agents/references/`
- **Issue**: All reference documents include a `version: "1.0"` frontmatter field. FR-004 in the spec lists only 3 required fields: `source-agent`, `loaded-at`, and `extracted-from`. The `version` field was added by the plan's "Frontmatter Standard" section.
- **Impact**: No negative impact. The `version` field is additive and useful for tracking reference document evolution. This is a scope expansion from spec to plan that benefits the deliverable.
- **Fix**: None required. The plan expanded the frontmatter standard appropriately, and this was approved by reviewers.

---

## Passed Checks

### Architecture Alignment

- [x] **Command-per-workflow**: Each agent maps to one workflow. No monolithic commands introduced.
- [x] **Content-as-data compliance**: Reference documents are read-only files loaded via Read tool. No agent modifies reference documents per-output.
- [x] **Loading instructions pattern**: All 3 refactored agents include a "Reference Documents" section with a loading table (Reference, Path, Load When) and missing-file error handling instructions.
- [x] **On-demand loading**: SARIF generation loaded at Phase 4 completion. Validation checklist loaded at pipeline end. Error templates loaded on error condition. Report templates loaded at attack tree generation phase. Gemini API loaded at image generation phase. Infographic error handling loaded on error condition.

### Naming Conventions

- [x] **Reference directory**: `adapters/claude-code/agents/references/` -- kebab-case directory name, consistent with agent file naming.
- [x] **Reference file names**: All 6 files use kebab-case: `sarif-generation.md`, `validation-checklist.md`, `error-templates.md`, `report-templates.md`, `infographic-gemini-api.md`, `infographic-error-handling.md`.
- [x] **Agent file names**: Unchanged kebab-case: `orchestrator.md`, `threat-report.md`, `threat-infographic.md`.

### Frontmatter Compliance

- [x] **Required fields present**: All 6 reference documents include `source_agent`, `loaded_at`, `extracted_from`, and `version` in frontmatter.
- [x] **source_agent values correct**: Orchestrator references point to `orchestrator.md`. Report reference points to `threat-report.md`. Infographic references point to `threat-infographic.md`.
- [x] **loaded_at values match loading tables**: Every `loaded_at` value in frontmatter matches the "Load When" column in the corresponding agent's Reference Documents table.

### Path Consistency (No Orphaned References)

- [x] **Orchestrator**: 3 paths referenced in loading table, 8 total path references in file body. All 3 reference documents exist at the specified paths.
- [x] **Report agent**: 1 path referenced in loading table, 2 total path references in file body. Reference document exists at the specified path.
- [x] **Infographic agent**: 2 paths referenced in loading table, 4 total path references in file body. Both reference documents exist at the specified paths.
- [x] **No orphaned files**: All 6 reference documents in `references/` are referenced by at least one agent.

### Self-Containment (FR-003)

- [x] **No cross-references**: Grep for reference document paths within the `references/` directory returned zero matches. No reference document links to another reference document.
- [x] **Each document standalone**: All 6 reference documents contain complete content that can be used independently without loading other reference documents.

### Zero-Regression (US-4 / SC-004)

- [x] **11 STRIDE/AI threat agents**: `git diff main` shows zero changes to all 11 threat agent files (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse).
- [x] **Infographic templates**: `git diff main` shows zero changes to `templates/infographic-baseball-card.md` and `templates/infographic-system-architecture.md`.
- [x] **Schemas**: `git diff main` shows zero changes to all files in `schemas/`.

### Specification Content Preservation (FR-008, FR-010)

- [x] **Defensive specification retained**: Error Evaluation Order (lines 1183-1191), Ambiguous DFD Classification (lines 1195-1227), Non-Conforming Finding Handling (lines 1230-1259), Three-State Cell Model (lines 1263-1273) -- all present in the orchestrator core file.
- [x] **Orchestration logic retained**: All phase sequencing (Phase 1-6), dispatch rules, correlation detection algorithm, risk level validation, STRIDE-per-Element normalization, AI keyword dispatch, coverage matrix generation, and risk summary computation remain in the orchestrator core file.
- [x] **Error handling structure retained**: Error evaluation order and trigger summaries remain in the orchestrator. Full error templates (YAML response bodies) correctly extracted to reference document.
- [x] **Report agent core retained**: Input contract, quality standards, report generation methodology, correlation group handling, finding reference appendix generation, dual output location, remediation roadmap generation -- all present in the report agent core file.
- [x] **Infographic agent core retained**: Input contract, data extraction methodology (Steps 1-5b), infographic specification format (Sections 1-6), quality standards -- all present in the infographic agent core file.

### Missing-File Error Handling (FR-009)

- [x] All 3 agents include the error message pattern: `"ERROR: Required reference document not found: {path}"`

---

## Line Count Summary

| Agent | Before | After | Target | Delta | Status |
|-------|--------|-------|--------|-------|--------|
| Orchestrator | 2,085 | 1,273 | ~1,100-1,200 | +73 over upper bound (6%) | WARNING (W-1) |
| Report | 801 | 472 | ~300-400 | +72 over upper bound (18%) | WARNING (W-2) |
| Infographic | 592 | 414 | ~300-400 | +14 over upper bound (3.5%) | WARNING (W-3) |

| Reference Document | Lines | Source Agent |
|-------------------|-------|-------------|
| sarif-generation.md | 499 | orchestrator |
| report-templates.md | 298 | threat-report |
| infographic-gemini-api.md | 148 | threat-infographic |
| error-templates.md | 131 | orchestrator |
| validation-checklist.md | 90 | orchestrator |
| infographic-error-handling.md | 67 | threat-infographic |

**Total extracted**: 1,233 lines across 6 reference documents.

---

## Verdict

**APPROVED_WITH_CONCERNS**

The refactoring is structurally sound. All 6 reference documents are self-contained, correctly frontmatted, and properly referenced from their source agents. Loading instructions follow the on-demand pattern consistently. Zero regression confirmed on all 11 threat agents, templates, and schemas. Defensive specification content and all orchestration logic correctly retained in core agent files. Naming conventions followed throughout.

The 3 WARNING findings relate to line count overshoots against spec targets. The orchestrator and infographic overshoots are marginal (6% and 3.5% respectively) and were anticipated in the plan. The report agent overshoot (18%) is larger and warrants attention, though the plan acknowledged a realistic floor of ~400-450 lines.

**Recommendation**: Accept as-is for merge. The line count overshoots are within the tolerance acknowledged by the plan's approved "target adjustment" and "accepted residual" clauses. If further reduction is desired, it can be pursued in a follow-up refinement pass targeting the report agent's remediation roadmap section.

**Critical findings**: 0
**Warning findings**: 3
**Suggestion findings**: 2
