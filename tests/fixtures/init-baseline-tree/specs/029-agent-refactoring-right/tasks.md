---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-25
    status: APPROVED
    notes: "All 4 user stories fully covered with traceable tasks. All 15 FRs have implementing tasks. All 8 success criteria verifiable. No scope creep. MVP-first strategy with regression checkpoint after US1 is valuable risk mitigation."
  architect_signoff:
    agent: architect
    date: 2026-03-25
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered. Line ranges verified accurate. Error handling split correct. 3 minor concerns addressed: (1) T002 updated to include schema checksums, (2) T014 [P] removed — depends on T013 same file, (3) T004/T005 append coordination noted."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-25
    status: APPROVED
    notes: "27 tasks across 4 waves is lean and proportionate. 10-15 hour estimate realistic. Critical path identified. Parallelization maximized in Wave 3. Task granularity appropriate for LLM agent execution. Agent assignments: 65% senior-backend-engineer, 20% tester, 15% code-reviewer."
---

# Tasks: Agent Refactoring — Right-Size Orchestrator, Report, and Infographic Agents

**Input**: Design documents from `specs/029-agent-refactoring-right/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not explicitly requested in spec. Regression verification is embedded in Wave 4 validation tasks.

**Organization**: Tasks grouped by user story mapped to the plan's 4-wave structure. US2 and US3 are parallelizable (Wave 3).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup — Baseline & Capability Inventory (Wave 1)

**Purpose**: Capture pre-refactoring state for preservation-first validation. All subsequent phases depend on this.

- [X] T001 Create `adapters/claude-code/agents/references/` directory
- [X] T002 Record baseline checksums of all 11 threat agents (spoofing.md, tampering.md, repudiation.md, info-disclosure.md, denial-of-service.md, privilege-escalation.md, prompt-injection.md, data-poisoning.md, model-theft.md, agent-autonomy.md, tool-abuse.md), 2 infographic templates (templates/infographic-baseball-card.md, templates/infographic-system-architecture.md), and all schema files in `schemas/` — save to `specs/029-agent-refactoring-right/baseline-checksums.txt`
- [X] T003 Create capability inventory for orchestrator.md: list all capabilities, workflows, integration points, section-by-section content map with line ranges — save to `specs/029-agent-refactoring-right/capability-inventory.md` (orchestrator section)
- [X] T004 [P] Create capability inventory for threat-report.md: list all capabilities, section content map with line ranges — append to `specs/029-agent-refactoring-right/capability-inventory.md` (report section). Note: T004 and T005 are parallel with T003 but must append sequentially to the same file — run after T003 creates the file
- [X] T005 [P] Create capability inventory for threat-infographic.md: list all capabilities, section content map with line ranges — append to `specs/029-agent-refactoring-right/capability-inventory.md` (infographic section). Note: run after T003 or T004 to avoid write conflicts

**Checkpoint**: Baseline captured and capability inventory committed. All extraction targets documented before any modifications begin.

---

## Phase 2: Foundational — Baseline Regression Capture (Wave 1 continued)

**Purpose**: Capture pre-refactoring output for regression comparison. BLOCKS all user story work.

**CRITICAL**: No agent modifications can begin until baseline output is captured.

- [X] T006 Run `/threat-model` on `examples/agentic-app/architecture.md` and save all output files (threats.md, threats.sarif, threat-report.md, attack-trees/, threat-baseball-card-spec.md, threat-system-architecture-spec.md) to `specs/029-agent-refactoring-right/baseline-output/` for regression comparison

**Checkpoint**: Foundation ready — extraction work can now begin.

---

## Phase 3: User Story 1 — Orchestrator Right-Sizing (Priority: P1) MVP

**Goal**: Reduce orchestrator from 2,085 to ~1,100-1,200 lines by extracting consultation-only content to reference documents and condensing verbose prose.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` and compare output structure against baseline. `wc -l adapters/claude-code/agents/orchestrator.md` must show ~1,100-1,200 lines.

### Extraction Tasks

- [X] T007 [US1] Extract SARIF generation section (lines 1224-1718) from `adapters/claude-code/agents/orchestrator.md` to `adapters/claude-code/agents/references/sarif-generation.md` — include frontmatter (source_agent: orchestrator.md, loaded_at: Phase 4 completion, extracted_from: SARIF Output Generation section lines 1224-1718, version: 1.0)
- [X] T008 [US1] Extract validation checklist (lines 1138-1223) from `adapters/claude-code/agents/orchestrator.md` to `adapters/claude-code/agents/references/validation-checklist.md` — include frontmatter (source_agent: orchestrator.md, loaded_at: pipeline end, extracted_from: Output Structural Validation Checklist lines 1138-1223, version: 1.0)
- [X] T009 [US1] Split error handling section in `adapters/claude-code/agents/orchestrator.md`: extract pure YAML error templates from UNSUPPORTED_FORMAT (lines 1863-1908), NO_COMPONENTS (lines 1908-1949), INVALID_FORMAT_VALUE (lines 1949-1990) to `adapters/claude-code/agents/references/error-templates.md` — retain 1-2 line trigger summaries in core agent pointing to reference; retain all defensive specification content (error evaluation order lines 1990-2001, ambiguous DFD classification lines 2002-2036, non-conforming finding handling lines 2037-2069, three-state cell model lines 2070-2085) in core agent

### Prose Condensation

- [X] T010 [US1] Condense verbose prose (~200 lines scattered) in `adapters/claude-code/agents/orchestrator.md` — only remove redundant narration, NEVER specification content (tables, schemas, algorithms, rules). Focus on Phase 1 format detection narrative, Phase 5/6 dispatch descriptions, and redundant explanations

### Loading Instructions

- [X] T011 [US1] Add Reference Documents section to `adapters/claude-code/agents/orchestrator.md` — table with Reference/Path/Load When columns for sarif-generation.md (Phase 4), validation-checklist.md (pipeline end), error-templates.md (error condition); include error-on-missing instruction per FR-009

### Verification

- [X] T012 [US1] Verify orchestrator line count: run `wc -l adapters/claude-code/agents/orchestrator.md` — target ~1,100-1,200 lines. If outside range, identify additional condensation opportunities or document justification

**Checkpoint**: Orchestrator refactored. Run `/threat-model` on `examples/agentic-app/architecture.md` and compare output structure against baseline to verify structural equivalence.

---

## Phase 4: User Story 2 — Report Agent Right-Sizing (Priority: P2)

**Goal**: Reduce threat-report agent from 801 to ~300-400 lines by extracting attack tree construction rules, Mermaid conventions, and example trees to a reference document.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` and verify narrative report has equivalent structure: executive summary present, attack trees rendered, finding details complete, remediation roadmap included.

### Extraction Tasks

- [X] T013 [P] [US2] Extract attack tree construction rules (lines 349-392), Mermaid conventions + validation checklist (lines 393-531), and example attack trees (lines 532-642) from `adapters/claude-code/agents/threat-report.md` to `adapters/claude-code/agents/references/report-templates.md` — include frontmatter (source_agent: threat-report.md, loaded_at: attack tree generation phase, extracted_from: Attack Tree Construction Rules + Mermaid Conventions + Example Trees lines 349-642, version: 1.0)

### Prose Condensation

- [X] T014 [US2] Condense prose in `adapters/claude-code/agents/threat-report.md` (depends on T013 completing — both modify the same file) — target dual output location section (~57 lines), remediation roadmap generation (~101 lines), executive summary methodology, architecture overview narrative, and per-finding narrative template. Target ~50-80 lines of condensation

### Loading Instructions

- [X] T015 [US2] Add Reference Documents section to `adapters/claude-code/agents/threat-report.md` — table with Reference/Path/Load When for report-templates.md (attack tree generation phase); include error-on-missing instruction

### Verification

- [X] T016 [US2] Verify report agent line count: run `wc -l adapters/claude-code/agents/threat-report.md` — target ~300-400 lines. If floor exceeds 400, document justification in capability inventory (remaining content is specification, not prose)

**Checkpoint**: Report agent refactored and independently testable.

---

## Phase 5: User Story 3 — Infographic Agent Right-Sizing (Priority: P2)

**Goal**: Reduce threat-infographic agent from 592 to ~300-400 lines by extracting Gemini API specification and error handling to reference documents.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` with `GEMINI_API_KEY` set and verify infographic specification is produced. Verify graceful degradation when key absent.

### Extraction Tasks

- [X] T017 [P] [US3] Extract Gemini API prompt construction (lines 389-445) and Gemini API integration (lines 446-532) from `adapters/claude-code/agents/threat-infographic.md` to `adapters/claude-code/agents/references/infographic-gemini-api.md` — include frontmatter (source_agent: threat-infographic.md, loaded_at: image generation phase, extracted_from: Gemini API Prompt Construction + Integration lines 389-532, version: 1.0)
- [X] T018 [P] [US3] Extract error handling & graceful degradation (lines 533-592) from `adapters/claude-code/agents/threat-infographic.md` to `adapters/claude-code/agents/references/infographic-error-handling.md` — include frontmatter (source_agent: threat-infographic.md, loaded_at: error condition during infographic generation, extracted_from: Error Handling & Graceful Degradation lines 533-592, version: 1.0). Ensure all 6 failure conditions preserved (missing key, rate limit, timeout, content policy, missing input, empty model)

### Loading Instructions

- [X] T019 [US3] Add Reference Documents section to `adapters/claude-code/agents/threat-infographic.md` — table with Reference/Path/Load When for infographic-gemini-api.md (image generation phase) and infographic-error-handling.md (error condition); include error-on-missing instruction

### Verification

- [X] T020 [US3] Verify infographic agent line count: run `wc -l adapters/claude-code/agents/threat-infographic.md` — target ~300-400 lines

**Checkpoint**: Infographic agent refactored and independently testable.

---

## Phase 6: User Story 4 — Zero Regression Validation (Priority: P0) & Polish

**Goal**: Verify all 11 threat agents are byte-identical, all templates and schemas unchanged, and end-to-end `/threat-model` produces structurally equivalent output.

**Independent Test**: `git diff` on all 11 threat agents shows zero changes. End-to-end regression test passes.

### Zero Regression Verification

- [X] T021 [US4] Verify all 11 threat agents are byte-identical: compare checksums against `specs/029-agent-refactoring-right/baseline-checksums.txt` for spoofing.md, tampering.md, repudiation.md, info-disclosure.md, denial-of-service.md, privilege-escalation.md, prompt-injection.md, data-poisoning.md, model-theft.md, agent-autonomy.md, tool-abuse.md in `adapters/claude-code/agents/`
- [X] T022 [P] [US4] Verify both infographic design templates unchanged: compare `templates/infographic-baseball-card.md` and `templates/infographic-system-architecture.md` against baseline checksums
- [X] T023 [P] [US4] Verify all schemas unchanged: compare all files in `schemas/` against baseline

### End-to-End Regression

- [X] T024 [US4] Run end-to-end `/threat-model` on `examples/agentic-app/architecture.md` — compare output against `specs/029-agent-refactoring-right/baseline-output/`: finding count, risk distribution, SARIF result count, section presence must be structurally equivalent
- [X] T025 [US4] Validate SARIF output structure against SARIF 2.1.0 schema: verify `$schema`, `version`, `runs[].tool`, `runs[].results[]` structure, `runs[].taxonomies[]` presence

### Reference Document Verification

- [X] T026 [P] [US4] Verify all 6 reference documents load correctly via Read tool: sarif-generation.md, validation-checklist.md, error-templates.md, report-templates.md, infographic-gemini-api.md, infographic-error-handling.md in `adapters/claude-code/agents/references/`

### Polish

- [X] T027 Update `specs/029-agent-refactoring-right/capability-inventory.md` with post-refactoring verification results: final line counts, extraction summary, any deviations from targets with justification

**Checkpoint**: All validation passed. Feature complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Baseline)**: Depends on Phase 1 (directory and checksums created)
- **Phase 3 (Orchestrator/US1)**: Depends on Phase 2 (baseline captured) — BLOCKS on baseline
- **Phase 4 (Report/US2)**: Depends on Phase 2 (baseline captured) — can run in parallel with Phase 5
- **Phase 5 (Infographic/US3)**: Depends on Phase 2 (baseline captured) — can run in parallel with Phase 4
- **Phase 6 (Validation/US4)**: Depends on Phases 3, 4, and 5 completion

### User Story Dependencies

- **US1 (Orchestrator, P1)**: Depends on Phase 2 — no dependencies on other user stories
- **US2 (Report, P2)**: Depends on Phase 2 — independent of US1 and US3, can start in parallel
- **US3 (Infographic, P2)**: Depends on Phase 2 — independent of US1 and US2, can start in parallel
- **US4 (Validation, P0)**: Depends on US1, US2, US3 completion — final validation gate

### Parallel Opportunities

- T003/T004/T005 can run in parallel (different agent inventories)
- T013/T014 (US2 report) can run in parallel with T017/T018 (US3 infographic) — Wave 3 parallel
- T021/T022/T023 can run in parallel (different verification targets)
- After Phase 2, US1/US2/US3 can all start in parallel if team capacity allows

---

## Parallel Example: Wave 3 (Report + Infographic)

```
# Launch report and infographic extraction in parallel:
Agent 1: "Extract attack tree rules, Mermaid conventions, examples from threat-report.md to references/report-templates.md" (T013)
Agent 2: "Extract Gemini API sections from threat-infographic.md to references/infographic-gemini-api.md" (T017)
Agent 3: "Extract error handling from threat-infographic.md to references/infographic-error-handling.md" (T018)
Agent 4: "Condense prose in threat-report.md dual output and remediation sections" (T014)
```

---

## Implementation Strategy

### MVP First (US1 Only — Orchestrator)

1. Complete Phase 1: Setup (baseline + inventory)
2. Complete Phase 2: Baseline regression capture
3. Complete Phase 3: Orchestrator refactoring (US1)
4. **STOP and VALIDATE**: Run regression test on orchestrator
5. Proceed to US2/US3 only if orchestrator regression passes

### Incremental Delivery

1. Phase 1 + 2 → Baseline ready
2. Phase 3 (US1) → Orchestrator right-sized → Regression verified
3. Phase 4 + 5 (US2 + US3 parallel) → Report + Infographic right-sized
4. Phase 6 (US4) → Full validation → Feature complete

### Total: 27 tasks across 6 phases

| Phase | Tasks | Parallel Tasks |
|-------|-------|---------------|
| Phase 1: Setup | 5 | 2 (T004, T005) |
| Phase 2: Baseline | 1 | 0 |
| Phase 3: US1 Orchestrator | 6 | 0 (sequential extraction) |
| Phase 4: US2 Report | 4 | 2 (T013, T014) |
| Phase 5: US3 Infographic | 4 | 2 (T017, T018) |
| Phase 6: US4 Validation | 7 | 3 (T022, T023, T026) |
| **Total** | **27** | **9** |

---

## Notes

- [P] tasks = different files, no dependencies on each other
- [Story] label maps task to spec user story for traceability
- Phase 4 and Phase 5 are fully parallelizable (Wave 3 in plan)
- All extraction tasks reference specific line ranges from the plan's content inventory
- Capability inventory (T003-T005) is a deliverable per SC-008
- Regression baseline (T006) is a one-time capture — do not re-run until all extraction is complete
