---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "All 3 user stories covered. All 11 FRs traced to tasks. No scope creep. Priority alignment correct. MVP scope (T001-T009) delivers core correlation value."
  architect_signoff:
    agent: architect
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "6 findings (0 critical, 0 high, 2 medium, 4 low). M-02: schema_version 1.1 propagation incomplete — distribute to T015/T016/T021 during implementation. M-01: T003/T004 parallel on same YAML block — low risk. All 3 plan-review concerns resolved."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "3 findings (2 medium, 1 low). F-1: T003/T004 false parallel — merge or serialize. F-2: T018 wave conflict with T013-T014 — sequence after T014. Feasible ~1.75h (85% confidence). Agent assignments: senior-backend-engineer (22), tester (2)."
---

# Tasks: Deduplication & Risk Rating

**Input**: Design documents from `specs/010-prd-010-deduplication/`
**Prerequisites**: plan.md (approved), spec.md (approved), research.md

**Tests**: Not explicitly requested. Integration validation included in Polish phase via orchestrator runs against example architectures.

**Organization**: Tasks grouped by user story. All changes are prompt-only (markdown + YAML files).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Schema version bump and foundational schema changes that all subsequent work depends on.

- [X] T001 Bump `schema_version` from "1.0" to "1.1" in `schemas/output.yaml` frontmatter and update the `output.frontmatter.fields.schema_version.value` to "1.1"
- [X] T002 Add Correlated Findings section entry to `schemas/output.yaml` between the "AI Threat Tables" and "Coverage Matrix" sections with fields: group_id, findings, component, threat_summary, risk_level; set `required: true`
- [X] T003 [P] Add `dedup_note` field to the Coverage Matrix section in `schemas/output.yaml` to describe the deduplication footnote behavior
- [X] T004 [P] Update the Coverage Matrix `structure` field in `schemas/output.yaml` to document the three-state cell model: deduplicated count, "—" (analyzed-but-clean), "n/a" (not-applicable)

**Checkpoint**: Schema updated to v1.1 with Correlated Findings section. All downstream template and orchestrator work can reference the new schema.

---

## Phase 2: User Story 1 — Cross-Agent Finding Correlation (Priority: P0) MVP

**Goal**: When multiple agents flag the same component for related threats, correlated findings appear in a dedicated section with all contributing agent perspectives.

**Independent Test**: Run orchestrator against `examples/mermaid-agentic-app/input.md`. At least one correlation group should appear in Section 4a linking findings from different agent categories on the same component.

### Orchestrator: Correlation Detection

- [X] T005 [US1] Add Correlation Rule Table section to `agents/orchestrator.md` after AI Threat Table Assembly (Phase 3), defining the 5 correlation rules (CR-1 through CR-5) as a markdown table mapping STRIDE-to-AI category pairs with correlation basis
- [X] T006 [US1] Add Correlation Detection Algorithm section to `agents/orchestrator.md` with step-by-step instructions: (1) group findings by component, (2) within each group check cross-category pairs against 5 rules, (3) create CG-N groups, (4) merge multi-rule matches on same component into single group, (5) enforce one-group-per-finding constraint
- [X] T007 [US1] Add Correlation Group Assembly section to `agents/orchestrator.md` with instructions for: sequential CG-N ID assignment, risk level = highest among members, threat summary = each perspective prefixed by category name, store groups for Phase 4 consumption
- [X] T008 [US1] Add Correlation Self-Check section to `agents/orchestrator.md` verifying: no finding in >1 group, all member IDs exist in STRIDE/AI tables, group risk level matches highest member

### Template: Correlated Findings Section

- [X] T009 [US1] Add Section 4a "Correlated Findings" to `templates/threats.md` between Section 4 (AI Threat Tables) and Section 5 (Coverage Matrix) with table format: Group | Findings | Component | Threat Summary | Risk Level, plus example row and zero-correlation fallback text "No cross-agent correlations detected"

**Checkpoint**: Correlation detection logic complete. Original findings preserved in Sections 3-4. New Section 4a shows correlated groups. US-1 independently testable.

---

## Phase 3: User Story 2 — Deduplicated Risk Summary and Coverage Matrix (Priority: P0)

**Goal**: Coverage matrix and risk summary reflect unique threats (deduplicated counts) rather than inflated raw counts.

**Independent Test**: Run orchestrator against an architecture with STRIDE+AI overlap. Risk summary total should be less than raw finding count. Coverage matrix should show deduplicated counts with footnote.

### Orchestrator: Enhanced Phase 4

- [X] T010 [US2] Update Coverage Matrix Generation section in `agents/orchestrator.md` Phase 4 to compute deduplicated cell counts: when findings in a cell belong to a correlation group, the group contributes 1 to the count collectively
- [X] T011 [US2] Update Coverage Matrix Generation in `agents/orchestrator.md` to apply three-state cell model: deduplicated count (integer), "—" for analyzed-but-clean (dispatched, zero findings), "n/a" for not-applicable (category not dispatched)
- [X] T012 [US2] Add Coverage Matrix Footnote generation logic to `agents/orchestrator.md`: when correlation groups > 0, append "Counts reflect deduplicated findings. N correlation groups merged M individual findings."
- [X] T013 [US2] Update Risk Summary computation in `agents/orchestrator.md` Phase 4 to count deduplicated findings (correlation group = 1), showing parenthetical raw count when different from dedup count (e.g., "5 (7 raw)")
- [X] T014 [US2] Update Risk Summary percentage computation in `agents/orchestrator.md` to use deduplicated total as denominator

### Template: Enhanced Coverage Matrix and Risk Summary

- [X] T015 [P] [US2] Update Coverage Matrix section in `templates/threats.md` Section 5 to show three-state cells ("—" for zero-coverage, "n/a" for not-applicable), deduplicated counts, and footnote example
- [X] T016 [P] [US2] Update Risk Summary table in `templates/threats.md` Section 6 to show deduplicated count column with parenthetical raw count example and percentages based on deduplicated total

**Checkpoint**: Coverage matrix and risk summary reflect deduplicated counts. US-2 independently testable.

---

## Phase 4: User Story 3 — Risk Calibration Documentation (Priority: P1)

**Goal**: The OWASP 3×3 risk matrix is documented prominently in the output for reader verification of risk ratings.

**Independent Test**: Run orchestrator against any architecture. Risk Summary section should include a Risk Calibration Matrix subsection with the full 3×3 matrix.

- [X] T017 [US3] Add Risk Calibration Matrix subsection to `templates/threats.md` Section 6 before the risk summary table, showing the OWASP 3×3 matrix (Likelihood rows × Impact columns → Risk Level cells) with all 9 combinations and the note "Risk summary counts below reflect deduplicated findings."
- [X] T018 [US3] Update orchestrator Phase 4 Risk Summary section in `agents/orchestrator.md` to reference the Risk Calibration Matrix subsection and instruct inclusion of the 3×3 matrix before the summary table in every output

**Checkpoint**: Risk calibration matrix documented in output. All three user stories complete.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Interface contract formalization, structural validation updates, and integration testing.

### Interface Contract

- [X] T019 [P] Update `docs/INTERFACE-CONTRACT.md` Section 3 (AI Extension Dispatch Rules) to replace the forward-reference sentence about coverage matrix dedup with a concrete description of the 5 correlation rules and detection algorithm
- [X] T020 [P] Update `docs/INTERFACE-CONTRACT.md` Section 4 (Output Specification) to add Section 4a (Correlated Findings) to the Required Sections table, describe the three-state coverage matrix cell model, and update schema_version reference to "1.1"

### Structural Validation

- [X] T021 Update Output Structural Validation Checklist in `agents/orchestrator.md` Phase 4 to add checks: (1) Section 4a present with correct table format, (2) coverage matrix counts match deduplicated totals, (3) risk summary counts match deduplicated totals, (4) all CG-N member IDs exist in Sections 3-4

### Orchestrator Frontmatter

- [X] T022 Update `agents/orchestrator.md` YAML frontmatter to reflect new capabilities: add correlation detection and deduplication to the agent description, bump version if present

### Integration Validation

- [X] T023 Run orchestrator against `examples/mermaid-agentic-app/input.md` and verify: (1) at least one CG-N group in Section 4a, (2) original findings preserved in Sections 3-4, (3) deduplicated coverage matrix counts, (4) risk summary with dedup counts, (5) Risk Calibration Matrix present
- [X] T024 Run orchestrator against `examples/ascii-web-api/input.md` (non-AI architecture) and verify: (1) Section 4a shows "No cross-agent correlations detected", (2) AI columns show "n/a", (3) risk summary counts equal raw counts (no dedup needed), (4) Risk Calibration Matrix present

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US-1 (Phase 2)**: Depends on Phase 1 (schema must be updated first)
- **US-2 (Phase 3)**: Depends on Phase 2 (correlation groups must exist for dedup logic)
- **US-3 (Phase 4)**: Depends on Phase 1 only (independent of correlation — can parallelize with US-1/US-2 if desired)
- **Polish (Phase 5)**: Depends on all user stories complete

### User Story Dependencies

- **US-1** (Correlation): Depends on Phase 1 schema updates. No dependency on other stories.
- **US-2** (Dedup Counts): Depends on US-1 completion (needs correlation groups to deduplicate).
- **US-3** (Risk Calibration): Independent of US-1 and US-2. Can start after Phase 1.

### Within Each Phase

- Tasks without [P] must execute sequentially in listed order
- Tasks with [P] can execute in parallel within their phase
- T005 → T006 → T007 → T008 (sequential: each builds on prior)
- T010 → T011 → T012 (sequential: cell model → footnote)
- T013 → T014 (sequential: dedup count → percentage)
- T015, T016 [P] (parallel: different template sections)
- T019, T020 [P] (parallel: different interface contract sections)

### Parallel Opportunities

```
Wave 1: T001, T002 (sequential schema core)
Wave 2: T003, T004 (parallel schema refinements)
Wave 3: T005-T008 (sequential orchestrator correlation), T009 (template 4a)
         T017 (US3 template — can parallelize with US1 work)
Wave 4: T010-T014 (sequential orchestrator dedup), T015-T016 (parallel template updates)
         T018 (US3 orchestrator)
Wave 5: T019-T022 (polish — mostly parallel)
Wave 6: T023-T024 (sequential integration validation)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Schema updates (T001-T004)
2. Complete Phase 2: Correlation detection (T005-T009)
3. **STOP and VALIDATE**: Run orchestrator against agentic example — verify correlations appear
4. Delivers core deduplication value even without dedup counts

### Incremental Delivery

1. Phase 1 → Schema ready
2. Phase 2 (US-1) → Correlation groups visible → Validate
3. Phase 3 (US-2) → Dedup counts in coverage matrix + risk summary → Validate
4. Phase 4 (US-3) → Risk calibration matrix documented → Validate
5. Phase 5 → Interface contract + validation complete → Final integration test

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 24 |
| Phase 1 (Setup) | 4 tasks |
| Phase 2 (US-1) | 5 tasks |
| Phase 3 (US-2) | 7 tasks |
| Phase 4 (US-3) | 2 tasks |
| Phase 5 (Polish) | 6 tasks |
| Parallel opportunities | 8 tasks marked [P] |
| Files modified | 4 (orchestrator.md, threats.md, output.yaml, INTERFACE-CONTRACT.md) |
| Files created | 0 |
| MVP scope | T001-T009 (9 tasks) |
