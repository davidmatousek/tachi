---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-07
    status: APPROVED
    notes: "All 5 user stories covered. All 12 FRs addressed with full traceability. Zero scope creep. MVP scope correctly identified (T001-T009). Success criteria have validation tasks."
  architect_signoff:
    agent: architect
    date: 2026-04-07
    status: APPROVED_WITH_CONCERNS
    notes: "5 findings (1 medium, 2 low, 2 info). Medium: templates/tachi/output-schemas/threats.md hardcoded table headers need MAESTRO column update — recommend adding Phase 2 task. Low: parallel vs sequential inconsistency for T010/T011; schema version comment in finding.yaml. Info: T014 resolves plan concern; T005 schema_version confirmed."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-07
    status: APPROVED
    notes: "22 tasks achievable in 3 days (2 optimistic, 4 pessimistic). 80% confidence. 5 execution waves with parallel factors 2/4/1/3/6. All tasks assigned to senior-backend-engineer. 3 non-blocking recommendations: batch orchestrator.md edits, checkpoint after Phase 3 MVP, pre-capture baseline outputs."
---

# Tasks: MAESTRO Layer Mapping

**Input**: Design documents from `/specs/084-maestro-layer-mapping/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Tests**: Not explicitly requested in spec — test tasks omitted. Validation is via example architecture regeneration and diff-based regression (SC-001, SC-003).

**Organization**: Tasks grouped by user story to enable independent implementation and testing. All modifications are to markdown and YAML files (knowledge system project — no application code).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create foundational reference file and schema extension that all user stories depend on

- [X] T001 Create MAESTRO shared reference file at `.claude/skills/tachi-shared/references/maestro-layers-shared.md` — include YAML frontmatter (type: shared-reference, version: 1.0.0, consumers list), seven-layer taxonomy table (L1-L7 with name, description, example components), keyword-to-layer mapping table per plan Component 1, and classification algorithm documentation (first-match-wins, "Unclassified" default, ordering rationale per TD-5)
- [X] T002 [P] Extend finding IR schema at `schemas/finding.yaml` — add optional `maestro_layer` field (string enum: L1-L7 values + "Unclassified", default "Unclassified") after `dfd_element_type` field, bump `schema_version` from `"1.1"` to `"1.2"` per TD-3
- [X] T003 [P] Update shared references skill metadata at `.claude/skills/tachi-shared/SKILL.md` — add MAESTRO reference file entry to Domain Coverage section (4th reference), add entry to Loading Table with consumers (orchestrator, risk-scorer, control-analyzer) and load condition

**Checkpoint**: Foundation ready — MAESTRO layer definitions and schema available for pipeline reference updates

---

## Phase 2: Foundational (Pipeline Reference Updates)

**Purpose**: Update all pipeline reference files that define table formats, validation rules, and output schemas. MUST complete before orchestrator agent modifications.

**CRITICAL**: No user story work can begin until this phase is complete — orchestrator relies on these reference definitions.

- [X] T004 [P] Update dispatch table format at `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — add MAESTRO Layer column between DFD Type and STRIDE Categories in table format definition, update example rows with layer values, update self-check to validate MAESTRO layer assignments for every component
- [X] T005 [P] Update output schemas at `.claude/skills/tachi-orchestration/references/output-schemas.md` — add MAESTRO Layer column to Section 3 STRIDE table format (after Component, or after Status when baseline-aware), add MAESTRO Layer column to Section 4 AI table format (same position), add "Risk by MAESTRO Layer" subsection specification within Section 6 per TD-1, update Section 6 validation checklist to include MAESTRO Layer checks, update `schema_version` validation to `"1.2"` per TD-3
- [X] T006 [P] Update finding format shared reference at `.claude/skills/tachi-shared/references/finding-format-shared.md` — add `maestro_layer` to optional fields documentation, update STRIDE table format to include MAESTRO Layer column, update AI table format to include MAESTRO Layer column, document field as optional with "Unclassified" default
- [X] T007 [P] Update SARIF specification at `.claude/skills/tachi-orchestration/references/sarif-specification.md` — add MAESTRO layer SARIF extension rules: `result.properties.tags[]` gains `"maestro-layer:{layer-name}"` entry, `result.properties.maestro-layer` gains full layer name string, document additive merge behavior with baseline properties per TD-4 (no conflict — distinct property keys)

**Checkpoint**: All pipeline reference files updated — orchestrator can now be modified to implement classification and output changes

---

## Phase 3: US2 — Phase 1 Component Classification (Priority: P0) MVP

**Goal**: Orchestrator classifies each component by MAESTRO layer during Phase 1 using keyword matching. Classification appears in component inventory and dispatch table.

**Independent Test**: Run Phase 1 on the agentic-app example architecture and verify component inventory and dispatch table include MAESTRO Layer column with values derived from keyword matching.

- [X] T008 [US2] Update orchestrator agent at `.claude/agents/tachi/orchestrator.md` Phase 1 section — add MAESTRO shared reference to reference loading table (load: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`, when: Phase 1 after DFD classification), add MAESTRO layer classification step after DFD classification (keyword matching against component name, description, and DFD type per shared reference algorithm), add MAESTRO Layer column to Component Inventory intermediate output table, add MAESTRO Layer column to Dispatch Table intermediate output table (between DFD Type and STRIDE Categories)

**Checkpoint**: Phase 1 classification operational — components now have MAESTRO layer assignments

---

## Phase 4: US1 — Layer-Tagged Threat Findings (Priority: P0)

**Goal**: Every finding in STRIDE and AI threat tables includes a MAESTRO Layer column. Findings inherit their layer from the target component's Phase 1 classification.

**Independent Test**: Run full pipeline on agentic-app example and verify every finding row in threats.md STRIDE and AI tables includes a MAESTRO Layer value.

- [X] T009 [US1] Update orchestrator agent at `.claude/agents/tachi/orchestrator.md` Phase 3 and Phase 4 sections — add finding-to-component MAESTRO layer inheritance logic in Phase 3 (each finding inherits `maestro_layer` from its target component's Phase 1 classification; if component not found, default to "Unclassified"), add MAESTRO Layer column to STRIDE table output format in Phase 4 (6 tables, column after Component or after Status when baseline-aware), add MAESTRO Layer column to AI table output format in Phase 4 (2 tables, same column position)

**Checkpoint**: Threat findings now carry MAESTRO layer tags in all 8 output tables

---

## Phase 5: US3 — SARIF Layer Tags (Priority: P0)

**Goal**: Each SARIF result includes MAESTRO layer as both a tag and a dedicated property for machine-readable filtering.

**Independent Test**: Run full pipeline, open SARIF output, verify each result has `maestro-layer:{layer}` in tags and `maestro-layer` property.

- [X] T010 [US3] Update orchestrator agent at `.claude/agents/tachi/orchestrator.md` Phase 4 SARIF generation section — add `"maestro-layer:{layer-name}"` entry to `result.properties.tags[]` array for each result, add `"maestro-layer": "{full-layer-name}"` key-value to `result.properties` for each result, ensure additive merge with existing baseline properties (delta_status, baselineRunId in partialFingerprints occupy distinct keys — no conflict per TD-4)

**Checkpoint**: SARIF output includes MAESTRO layer metadata — security tooling can filter by layer

---

## Phase 6: US4 — Layer-Based Risk Summary (Priority: P1)

**Goal**: Risk summary section in threats.md includes a "Risk by MAESTRO Layer" subsection showing finding counts and highest severity per layer.

**Independent Test**: Run full pipeline on architecture with findings across multiple layers, verify risk summary includes layer breakdown table.

- [X] T011 [US4] Update orchestrator agent at `.claude/agents/tachi/orchestrator.md` Phase 4 Section 6 output — add "Risk by MAESTRO Layer" subsection within Section 6 (Risk Summary) after the existing Risk Calibration Matrix per TD-1, format as table with columns: MAESTRO Layer, Finding Count, Highest Severity, omit layers with zero findings, order rows by highest severity descending then finding count descending, use deduplicated finding counts (correlation groups count as 1)

**Checkpoint**: Executive risk summary now includes architectural layer dimension

---

## Phase 7: US5 — Downstream Propagation (Priority: P1)

**Goal**: MAESTRO layer tag propagates passively through risk-scores.md, compensating-controls.md, and threat-report.md without modifying scoring, control detection, or report generation logic.

**Independent Test**: Run full pipeline with risk scoring and controls analysis, verify MAESTRO layer field appears in downstream outputs.

- [X] T012 [P] [US5] Update risk-scorer agent at `.claude/agents/tachi/risk-scorer.md` — add passive `maestro_layer` field propagation: read field from input findings if present, include in risk-scores.md output tables and risk-scores.sarif output, default to "Unclassified" if field absent, no changes to CVSS scoring formulas, exploitability/scalability/reachability assessments, or composite score calculations
- [X] T013 [P] [US5] Update control-analyzer agent at `.claude/agents/tachi/control-analyzer.md` — add passive `maestro_layer` field propagation: read field from scored findings if present, include in compensating-controls.md output tables and compensating-controls.sarif output, default to "Unclassified" if field absent, no changes to control detection logic, effectiveness classification, or residual risk calculations
- [X] T014 [P] [US5] Update threat-report agent at `.claude/agents/tachi/threat-report.md` — add MAESTRO Layer column awareness for STRIDE/AI table references in narrative report, propagate layer tag in finding references without modifying narrative generation or attack tree construction logic

**Checkpoint**: Full pipeline propagation complete — MAESTRO layer available in all output artifacts

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Regenerate all example architecture outputs and validate success criteria

- [X] T015 [P] Regenerate `examples/agentic-app/threats.md` with MAESTRO layer classifications by running full pipeline on `examples/agentic-app/architecture.md`
- [X] T016 [P] Regenerate `examples/web-app/threats.md` with MAESTRO layer classifications by running full pipeline on `examples/web-app/architecture.md`
- [X] T017 [P] Regenerate `examples/microservices/threats.md` with MAESTRO layer classifications by running full pipeline on `examples/microservices/architecture.md`
- [X] T018 [P] Regenerate `examples/ascii-web-api/threats.md` with MAESTRO layer classifications by running full pipeline on `examples/ascii-web-api/architecture.md`
- [X] T019 [P] Regenerate `examples/free-text-microservice/threats.md` with MAESTRO layer classifications by running full pipeline on `examples/free-text-microservice/architecture.md`
- [X] T020 [P] Regenerate `examples/mermaid-agentic-app/threats.md` with MAESTRO layer classifications by running full pipeline on `examples/mermaid-agentic-app/architecture.md`
- [X] T021 Validate SC-001: verify >90% of components across all 6 example architectures receive a non-"Unclassified" MAESTRO layer assignment — count total components vs. classified components, report classification rate
- [X] T022 Validate SC-003: verify backward compatibility via diff-based regression — compare pre-change baseline outputs against post-change outputs excluding MAESTRO-specific additions (MAESTRO Layer columns, Risk by MAESTRO Layer subsection, SARIF maestro-layer properties), confirm zero differences in non-MAESTRO content

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (shared reference file) — BLOCKS all user stories
- **US2 (Phase 3)**: Depends on Phase 2 completion — BLOCKS US1, US3, US4 (classification is upstream)
- **US1 (Phase 4)**: Depends on T008 (Phase 1 classification must exist for finding inheritance)
- **US3 (Phase 5)**: Depends on T009 (findings must have layer for SARIF tags)
- **US5 (Phase 7)**: Depends on T009 (findings must have layer for propagation) — can parallel with US3, US4
- **US4 (Phase 6)**: Depends on T009 (findings must have layer for risk summary)
- **Polish (Phase 8)**: Depends on ALL user stories — example regeneration validates complete pipeline

### User Story Dependencies

- **US2 (P0)**: Can start after Foundational (Phase 2) — No dependencies on other stories. **Upstream dependency for US1, US3, US4, US5.**
- **US1 (P0)**: Depends on US2 (needs Phase 1 classification). Once US2 complete, US1 is the next priority.
- **US3 (P0)**: Depends on US1 (needs layer-tagged findings). Sequential after US1.
- **US4 (P1)**: Depends on US1 (needs layer-tagged findings). Can parallel with US3 since they modify different orchestrator sections.
- **US5 (P1)**: Depends on US1 (needs layer-tagged findings). Can parallel with US3/US4 since it modifies different agent files.

### Within Each User Story

- Each task modifies specific sections of specific files — no intra-story parallelism needed (single-task stories)
- US5 has 3 parallel tasks (T012, T013, T014) — different agent files

### Parallel Opportunities

- **Phase 1**: T002 and T003 can parallel after T001
- **Phase 2**: All 4 tasks (T004-T007) can run in parallel (different files)
- **Phase 3-6**: Sequential (same file: orchestrator.md, different sections)
- **Phase 7**: All 3 tasks (T012-T014) can parallel (different agent files). Can also parallel with Phase 5-6.
- **Phase 8**: All 6 regeneration tasks (T015-T020) can parallel (different example directories)

---

## Parallel Example: Phase 2

```bash
# Launch all foundational reference updates together (different files):
Task: "Update dispatch-rules.md — MAESTRO Layer column in dispatch table"
Task: "Update output-schemas.md — table formats + risk summary + validation"
Task: "Update finding-format-shared.md — table format documentation"
Task: "Update sarif-specification.md — MAESTRO extension rules"
```

## Parallel Example: Phase 7

```bash
# Launch all downstream agent updates together (different files):
Task: "Update risk-scorer.md — passive maestro_layer propagation"
Task: "Update control-analyzer.md — passive maestro_layer propagation"
Task: "Update threat-report.md — MAESTRO Layer column awareness"
```

## Parallel Example: Phase 8

```bash
# Launch all example regenerations together (different directories):
Task: "Regenerate examples/agentic-app/threats.md"
Task: "Regenerate examples/web-app/threats.md"
Task: "Regenerate examples/microservices/threats.md"
Task: "Regenerate examples/ascii-web-api/threats.md"
Task: "Regenerate examples/free-text-microservice/threats.md"
Task: "Regenerate examples/mermaid-agentic-app/threats.md"
```

---

## Implementation Strategy

### MVP First (US2 + US1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007)
3. Complete Phase 3: US2 — Component Classification (T008)
4. Complete Phase 4: US1 — Layer-Tagged Findings (T009)
5. **STOP and VALIDATE**: Run pipeline on agentic-app, verify MAESTRO columns in tables
6. This delivers the core value: layer-tagged findings

### Incremental Delivery

1. Setup + Foundational -> Reference files ready
2. US2 -> Components classified -> Validate classification
3. US1 -> Findings tagged -> Validate tables (MVP!)
4. US3 -> SARIF tagged -> Validate SARIF
5. US4 -> Risk summary -> Validate executive view
6. US5 -> Full propagation -> Validate downstream outputs
7. Polish -> Examples regenerated -> Full validation

### Critical Path

T001 → T004-T007 (parallel) → T008 → T009 → T010 → T011

Minimum serial tasks on critical path: 7 (T001, one of T004-T007, T008, T009, T010, T011, T021/T022)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 22 |
| Phase 1 (Setup) | 3 tasks |
| Phase 2 (Foundational) | 4 tasks |
| Phase 3-7 (User Stories) | 7 tasks |
| Phase 8 (Polish) | 8 tasks |
| Parallel opportunities | 4 waves (Phase 1: 2P, Phase 2: 4P, Phase 7: 3P, Phase 8: 6P) |
| MVP scope | T001-T009 (9 tasks, delivers core layer tagging) |
| Files created | 1 (maestro-layers-shared.md) |
| Files modified | 10 (schemas, agents, skills, orchestration references) |
| Examples regenerated | 6 |

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All tasks modify markdown or YAML files — no compilation, no builds
- US2 is the upstream bottleneck — all other stories depend on Phase 1 classification
- US1 through US4 are sequential because they modify different sections of the same file (orchestrator.md)
- US5 is fully parallel with US3/US4 since it touches different agent files
- Example regeneration (Phase 8) is the schedule bottleneck per PRD team-lead review
- Commit after each phase completion for clean git history
