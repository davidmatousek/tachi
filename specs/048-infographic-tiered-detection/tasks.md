---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 3 user stories covered. 16/16 FRs addressed. 6 edge cases traced to tasks. No scope creep. Task granularity appropriate for docs-only feature."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correct. Parallel opportunities accurate. Step references match. 3 findings: (M) T014 should clarify template column 'Residual Severity' vs schema field 'residual_severity_band'; (L) T014 Step 5 should enumerate finding ID prefixes for STRIDE derivation; (L) T009/T022 type_label consistency noted."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED
    notes: "27 tasks well-sized for 200-300 line change. Critical path: Setup → US-1 → Validation. Two-agent parallelism viable (~45 min). Estimate: 1 session. No missing tasks."
---

# Tasks: 048 — Infographic Tiered Pipeline Auto-Detection & Residual Risk

**Input**: Design documents from `specs/048-infographic-tiered-detection/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not required (documentation/prompt-engineering feature — validation is manual walkthrough).

**Organization**: Tasks grouped by user story. All tasks edit markdown prompt files — no application code changes.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Read Source Materials)

**Purpose**: Read all source files needed to make accurate edits

- [X] T001 Read existing infographic command at `.claude/commands/infographic.md` and note current auto-detection logic (Step 1.2), co-location check (Step 1.3), detection summary (Step 1.5), agent invocation (Step 2), and report/tips (Step 3)
- [X] T002 [P] Read existing infographic agent at `.claude/agents/tachi/threat-infographic.md` and note Metadata block, Data Source Detection section, Data Extraction Methodology sections (threats and risk-scores paths), and Specification Generation sections
- [X] T003 [P] Read compensating-controls output template at `templates/compensating-controls.md` and note Coverage Matrix structure (Section 2: 4 sub-tables grouped by residual severity band), Executive Summary format (Section 1: risk reduction percentage), and column headers (Threat ID, Component, Threat, Inherent Score, Inherent Severity, Control Status, Residual Score, Residual Severity)
- [X] T004 [P] Read compensating-controls schema at `schemas/compensating-controls.yaml` and note controlled_finding fields (residual_score, residual_severity_band, control_status, reduction_factor) and severity band thresholds
- [X] T005 [P] Read infographic schema at `schemas/infographic.yaml` to confirm 6-section output structure and frontmatter fields

**Checkpoint**: All source materials read. Accurate detection patterns and extraction formats available for editing.

---

## Phase 2: US-1 — Tiered Auto-Detection with Residual Risk (Priority: P0)

**Goal**: Extend `/infographic` to auto-detect `compensating-controls.md` as the richest data source and extract residual risk scores for infographic generation.

**Independent Test**: Run `/infographic` in a directory containing all three source files (`compensating-controls.md`, `risk-scores.md`, `threats.md`). Verify the command selects `compensating-controls.md` and the generated spec uses residual scores.

### Command Updates (`.claude/commands/infographic.md`)

- [X] T006 [US1] Update Step 1.2 explicit-path detection in `.claude/commands/infographic.md` to add a new detection rule BEFORE the existing two: file contains `## 2. Coverage Matrix` AND first table has `Residual Score` column → type is `compensating-controls`. Update the UNABLE TO DETECT error message to list all three expected formats (compensating-controls, risk-scores, threats)
- [X] T007 [US1] Update Step 1.2 auto-detect in `.claude/commands/infographic.md` to scan for `compensating-controls.md` FIRST (before `risk-scores.md`). If found: set primary_file = compensating-controls.md, type = compensating-controls. If not found: fall through to existing risk-scores.md scan. Update NO DATA SOURCE FILES FOUND error to list all three tiers with their producing commands (`/compensating-controls`, `/risk-score`, `/threat-model`)
- [X] T008 [US1] Extend Step 1.3 co-located threats.md check in `.claude/commands/infographic.md` to trigger when type is `compensating-controls` (not just `risk-scores`). Use identical logic: require `threats.md` in `data_source_dir` for structural data. Add note that `risk-scores.md` is NOT required when compensating-controls is primary
- [X] T009 [US1] Update Step 1.5 detection summary in `.claude/commands/infographic.md` to add type label for compensating-controls: `residual risk (compensating-controls.md)`
- [X] T010 [US1] Update Step 2 agent invocation in `.claude/commands/infographic.md` to include `compensating-controls` as a valid data source type in the prompt template passed to the agent. Follow the same `primary_file` + `secondary_file` pattern already used for risk-scores

### Agent Updates (`.claude/agents/tachi/threat-infographic.md`)

- [X] T011 [US1] Update Metadata block in `.claude/agents/tachi/threat-infographic.md` to add `compensating-controls` data source type with files `[compensating-controls.md, threats.md]` and description `"Residual risk extraction with control effectiveness (dual-file)"`. Add `compensating-controls: ../../../schemas/compensating-controls.yaml` to input_schemas
- [X] T012 [US1] Update Input Contract section in `.claude/agents/tachi/threat-infographic.md` to document the third data source type: `compensating-controls.md` with co-located `threats.md`. Add dual-file requirement description parallel to existing risk-scores documentation
- [X] T013 [US1] Add compensating-controls detection rule to Data Source Detection section in `.claude/agents/tachi/threat-infographic.md`. Insert BEFORE existing risk-scores detection: contains `## 2. Coverage Matrix` with `Residual Score` column → type is `compensating-controls`. Add co-located file requirement for `threats.md` (same pattern as risk-scores). Update the "Neither indicator found" error message to list all three formats
- [X] T014 [US1] Add new "Data Extraction Methodology: compensating-controls.md" section in `.claude/agents/tachi/threat-infographic.md` AFTER the existing risk-scores extraction section. Include 5 extraction steps: Step 1 (parse Section 1 Executive Summary for metadata: total threats, coverage distribution, risk reduction percentage, date); Step 2 (parse Section 2 Coverage Matrix — iterate all 4 sub-tables for per-finding data: id, component, threat, residual_score, residual_severity_band, control_status — with accuracy invariant); Step 3 (read co-located threats.md Section 1 for project metadata); Step 4 (read co-located threats.md Section 2 for spatial data); Step 5 (compute residual risk distribution, cross-tabulate component × category using finding ID prefix for STRIDE category, select top findings by residual_score descending)
- [X] T015 [US1] Add error handling rules to the new compensating-controls extraction section in `.claude/agents/tachi/threat-infographic.md`: detection-level failure (file lacks `## 2. Coverage Matrix` or `Residual Score` column) falls through to risk-scores detection; extraction-level failure (malformed/empty rows mid-extraction) halts with warning, does NOT fall through
- [X] T016 [US1] Add compensating-controls frontmatter specification to the Specification Generation section in `.claude/agents/tachi/threat-infographic.md`: `data_source_type: "compensating-controls"`, `source_file: "compensating-controls.md"` in output spec YAML frontmatter (parallel to existing frontmatter specs for threats and risk-scores types)

**Checkpoint**: Auto-detection and extraction working for all three tiers. Existing behavior preserved for risk-scores and threats paths.

---

## Phase 3: US-2 — Enhancement Tips at Each Tier (Priority: P0)

**Goal**: Display contextual tips after data source detection to guide users toward richer pipeline tiers.

**Independent Test**: Run `/infographic` at each tier and verify correct tip. Run with explicit path and verify no tip.

- [X] T017 [US2] Replace the existing single post-run tip in Step 3 of `.claude/commands/infographic.md` with tiered enhancement tips: when `threats` detected → `Tip: Run /risk-score to add quantitative risk scores to your infographic`; when `risk-scores` detected → `Tip: Run /compensating-controls to visualize residual risk (actual exposure after defenses)`; when `compensating-controls` detected → `Full pipeline — visualizing residual risk (richest data available)`. Include emoji prefixes per PRD FR-3
- [X] T018 [US2] Add tip suppression logic in `.claude/commands/infographic.md`: when explicit `data_source_path` was provided (from Step 0), skip enhancement tip display entirely. Document the rationale: explicit path = intentional choice, no second-guessing

**Checkpoint**: Enhancement tips display correctly at each tier and suppress on explicit path.

---

## Phase 4: US-3 — Risk Labels and Template Adaptations (Priority: P1)

**Goal**: Infographic outputs clearly indicate whether they show Residual Risk, Inherent Risk, or Severity based on data source.

**Independent Test**: Generate infographics from each source type and verify header labels and data values match the source type.

- [X] T019 [US3] Add risk label mapping to `.claude/agents/tachi/threat-infographic.md` after the Data Source Detection section: `compensating-controls` → "Residual Risk"; `risk-scores` → "Inherent Risk"; `threats` → "Severity". Document where the label appears: spec Section 1 metadata, Section 2 chart title, Section 4 finding card headers, Section 6 visual design directives header
- [X] T020 [US3] Update Baseball Card specification generation in `.claude/agents/tachi/threat-infographic.md` for compensating-controls source: donut chart uses residual severity distribution; finding cards show residual score and residual severity band; summary zone adds "Risk Reduction: {risk_reduction_pct}%" line from Executive Summary; header label uses risk label mapping ("Residual Risk")
- [X] T021 [US3] Update System Architecture specification generation in `.claude/agents/tachi/threat-infographic.md` for compensating-controls source: component box border color uses residual severity; badge shows residual finding count and severity; finding legend groups by residual severity band; header label uses risk label mapping ("Residual Risk")
- [X] T022 [US3] Update the command type label in Step 3 of `.claude/commands/infographic.md` to include compensating-controls: when type is `compensating-controls`, `type_label` is `residual risk (compensating-controls.md)`

**Checkpoint**: Risk labels and template adaptations complete. All three source types produce correctly labeled output.

---

## Phase 5: Validation

**Purpose**: Verify all changes work correctly and backward compatibility is preserved

- [X] T023 [P] Verify backward compatibility by reviewing that no existing Step 1.2 detection logic for `risk-scores` or `threats` types was altered (only new `compensating-controls` tier inserted before them) in `.claude/commands/infographic.md`
- [X] T024 [P] Verify backward compatibility by reviewing that no existing Data Extraction Methodology sections for `threats` or `risk-scores` paths were altered (only new `compensating-controls` section added) in `.claude/agents/tachi/threat-infographic.md`
- [X] T025 Verify that the infographic output spec structure (6 sections with YAML frontmatter per `schemas/infographic.yaml`) remains identical across all three data source types by reviewing the Specification Generation sections in `.claude/agents/tachi/threat-infographic.md`
- [X] T026 Verify that no template files were modified: confirm `.claude/agents/tachi/templates/infographic-baseball-card.md` and `.claude/agents/tachi/templates/infographic-system-architecture.md` are unchanged
- [X] T027 Verify that no schema files were modified: confirm `schemas/infographic.yaml` and `schemas/compensating-controls.yaml` are unchanged

**Checkpoint**: All changes validated. Feature ready for delivery.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US-1 (Phase 2)**: Depends on Setup (Phase 1) completion — BLOCKS US-2 and US-3
- **US-2 (Phase 3)**: Depends on US-1 command changes (T006-T010) — tips reference the detection tiers
- **US-3 (Phase 4)**: Depends on US-1 agent changes (T011-T016) — labels reference the extraction paths
- **Validation (Phase 5)**: Depends on all user story phases complete

### User Story Dependencies

- **US-1 (P0)**: Foundational — detection and extraction must exist before tips or labels
- **US-2 (P0)**: Depends on US-1 detection logic — tips reference detected tier
- **US-3 (P1)**: Depends on US-1 extraction path — labels reference source type

### Within Each Phase

- Command file tasks (T006-T010) are sequential (same file)
- Agent file tasks (T011-T016) are sequential (same file)
- Command tasks and agent tasks within the same phase CAN run in parallel (different files) but are labeled sequential for clarity since US-1 spans both files

### Parallel Opportunities

- Phase 1: T002-T005 can all run in parallel (reading different files)
- Phase 2: Command tasks and agent tasks target different files but share logical dependency (detection logic must be consistent)
- Phase 3 and Phase 4: Can run in parallel (US-2 edits command file, US-3 edits agent file — different files)
- Phase 5: T023-T024 and T026-T027 can run in parallel (read-only verification)

---

## Implementation Strategy

### MVP First (US-1 Only)

1. Complete Phase 1: Setup (read source files)
2. Complete Phase 2: US-1 (detection + extraction in both files)
3. **STOP and VALIDATE**: Run `/infographic` with all three source files present
4. Core value delivered: compensating-controls.md is auto-detected and residual risk is visualized

### Incremental Delivery

1. US-1 (Phase 2) → Detection + extraction working → MVP
2. US-2 (Phase 3) → Enhancement tips added → Pipeline discoverability
3. US-3 (Phase 4) → Risk labels + template adaptations → Full feature
4. Validation (Phase 5) → Backward compatibility confirmed → Ready for delivery

### Parallel Execution

With two agents:
1. Both read source files (Phase 1)
2. Agent A: Command file changes (US-1 command tasks + US-2 tips)
3. Agent B: Agent file changes (US-1 agent tasks + US-3 labels)
4. Both: Validation (Phase 5)
