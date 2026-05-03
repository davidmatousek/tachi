---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED
    notes: "All 5 user stories covered (34 acceptance scenarios mapped). All 12 FRs addressed. All 8 success criteria achievable. No scope creep. P0/P2 priority ordering correct."
  architect_signoff:
    agent: architect
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "All 8 evaluation dimensions pass. Dependency ordering correct. Parallel opportunities accurately identified. STRIDE-per-Element dfd_targets verified. OWASP API Security mappings correct. 2 low concerns (detection pattern label naming, API9 to Repudiation mapping weakness)."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-21
    status: APPROVED
    notes: "Feasible with high confidence. 41 tasks, 3-agent parallel strategy for US1/US2/US3 is optimal. Critical path correctly identified. Task granularity appropriate. 5-wave execution plan with valid agent assignments."
---

# Tasks: STRIDE Threat Agents

**Input**: Design documents from `specs/005-stride-threat-agents/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Organization**: Tasks are grouped by user story. US1-US3 each validate and complete 2 agents (parallelizable). US4 validates cross-agent consistency. US5 validates end-to-end integration.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

**Purpose**: Establish validation criteria and reference materials

- [X] T001 Read STRIDE-per-Element matrix from `docs/INTERFACE-CONTRACT.md` Section 2 and verify it matches the validation matrix in `specs/005-stride-threat-agents/data-model.md`
- [X] T002 Read `schemas/finding.yaml` and extract the 10 IR fields, validation rules, and enum values for use as validation criteria
- [X] T003 [P] Read sample architecture `examples/mermaid-agentic-app/input.md` and identify all 5 components with their expected DFD element types

**Checkpoint**: Validation criteria established — agent work can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No blocking infrastructure needed — all 6 agent files exist with substantial content. This phase is intentionally empty.

**Checkpoint**: Foundation ready — all agents exist, user story implementation can begin in parallel

---

## Phase 3: User Story 1 - Spoofing and Tampering Agent Validation (Priority: P0) MVP

**Goal**: Validate and complete spoofing.md and tampering.md so both produce component-specific, schema-compliant findings with correct DFD targeting.

**Independent Test**: Run each agent against `examples/mermaid-agentic-app/input.md` and verify S-prefixed / T-prefixed findings reference specific components, target correct DFD element types, and include framework references.

### Implementation for User Story 1

- [X] T004 [P] [US1] Audit structural compliance of `agents/stride/spoofing.md` — verify frontmatter fields (agent_name, category, threat_class, dfd_targets, owasp_references, output_schema), section order (purpose, detection scope, patterns, finding template, risk computation, references), and `dfd_targets: [External Entity, Process]`
- [X] T005 [P] [US1] Audit structural compliance of `agents/stride/tampering.md` — verify frontmatter fields, section order, and `dfd_targets: [Process, Data Store, Data Flow]`
- [X] T006 [P] [US1] Verify detection patterns in `agents/stride/spoofing.md` cover all PRD FR-7 subcategories: authentication bypass, credential theft/replay, session hijacking, service impersonation, federated identity attacks
- [X] T007 [P] [US1] Verify detection patterns in `agents/stride/tampering.md` cover all PRD FR-7 subcategories: input injection, data flow manipulation, storage corruption, code/config tampering, API parameter manipulation
- [X] T008 [P] [US1] Add OWASP API Security Top 10 2023 cross-reference to `agents/stride/spoofing.md` — add `"OWASP API Security 2023 API2 — Broken Authentication"` to frontmatter `owasp_references` and References section
- [X] T009 [P] [US1] Add OWASP API Security Top 10 2023 cross-reference to `agents/stride/tampering.md` — add `"OWASP API Security 2023 API3 — Broken Object Property Level Authorization"` to frontmatter `owasp_references` and References section
- [X] T010 [US1] Verify finding template in `agents/stride/spoofing.md` demonstrates component-specific threats (not generic), actionable mitigations, and framework references (CWE-287, OWASP A07:2021, ATT&CK T1078)
- [X] T011 [US1] Verify finding template in `agents/stride/tampering.md` demonstrates component-specific threats (not generic), actionable mitigations, and framework references (CWE-20, OWASP A03:2021, ATT&CK T1565)

**Checkpoint**: Spoofing and Tampering agents validated and complete — can independently produce schema-compliant findings

---

## Phase 4: User Story 2 - Repudiation and Information Disclosure Agent Validation (Priority: P0)

**Goal**: Validate and complete repudiation.md and info-disclosure.md so both produce component-specific findings with correct DFD targeting (External Entity + Process for R; Process + Data Store + Data Flow for I).

**Independent Test**: Run each agent against `examples/mermaid-agentic-app/input.md` and verify R-prefixed / I-prefixed findings with correct DFD targeting and framework references.

### Implementation for User Story 2

- [X] T012 [P] [US2] Audit structural compliance of `agents/stride/repudiation.md` — verify frontmatter fields, section order, and `dfd_targets: [External Entity, Process]`
- [X] T013 [P] [US2] Audit structural compliance of `agents/stride/info-disclosure.md` — verify frontmatter fields, section order, and `dfd_targets: [Process, Data Store, Data Flow]`
- [X] T014 [P] [US2] Verify detection patterns in `agents/stride/repudiation.md` cover all PRD FR-7 subcategories: missing audit logging, log integrity gaps, non-repudiation mechanism gaps, timestamp manipulation, accountability gaps
- [X] T015 [P] [US2] Verify detection patterns in `agents/stride/info-disclosure.md` cover all PRD FR-7 subcategories: data leakage, excessive exposure, side-channel attacks, error message disclosure, storage access control gaps
- [X] T016 [P] [US2] Add OWASP API Security Top 10 2023 cross-reference to `agents/stride/repudiation.md` — add `"OWASP API Security 2023 API9 — Improper Inventory Management"` to frontmatter `owasp_references` and References section
- [X] T017 [P] [US2] Add OWASP API Security Top 10 2023 cross-reference to `agents/stride/info-disclosure.md` — add `"OWASP API Security 2023 API3 — Broken Object Property Level Authorization"` to frontmatter `owasp_references` and References section
- [X] T018 [US2] Verify finding template in `agents/stride/repudiation.md` demonstrates component-specific audit gap findings with concrete mitigations and references (CWE-778, OWASP A09:2021, ATT&CK T1070)
- [X] T019 [US2] Verify finding template in `agents/stride/info-disclosure.md` demonstrates data exposure findings specifying what data is exposed and through what mechanism, with references (CWE-200, OWASP A02:2021, ATT&CK T1005)

**Checkpoint**: Repudiation and Information Disclosure agents validated and complete

---

## Phase 5: User Story 3 - Denial of Service and Elevation of Privilege Agent Validation (Priority: P0)

**Goal**: Validate and complete denial-of-service.md and privilege-escalation.md so both produce component-specific findings with correct DFD targeting (Process + Data Store + Data Flow for D; Process only for E).

**Independent Test**: Run each agent against `examples/mermaid-agentic-app/input.md` and verify D-prefixed / E-prefixed findings with correct DFD targeting and framework references.

### Implementation for User Story 3

- [X] T020 [P] [US3] Audit structural compliance of `agents/stride/denial-of-service.md` — verify frontmatter fields, section order, and `dfd_targets: [Process, Data Store, Data Flow]`
- [X] T021 [P] [US3] Audit structural compliance of `agents/stride/privilege-escalation.md` — verify frontmatter fields, section order, and `dfd_targets: [Process]`
- [X] T022 [P] [US3] Verify detection patterns in `agents/stride/denial-of-service.md` cover all PRD FR-7 subcategories: resource exhaustion, application-layer attacks, infrastructure-layer attacks, algorithmic complexity, cascading failures
- [X] T023 [P] [US3] Verify detection patterns in `agents/stride/privilege-escalation.md` cover all PRD FR-7 subcategories: vertical escalation, horizontal escalation, permission boundary violations, default permission abuse, lateral movement
- [X] T024 [P] [US3] Add OWASP API Security Top 10 2023 cross-reference to `agents/stride/denial-of-service.md` — add `"OWASP API Security 2023 API4 — Unrestricted Resource Consumption"` to frontmatter `owasp_references` and References section
- [X] T025 [P] [US3] Add OWASP API Security Top 10 2023 cross-references to `agents/stride/privilege-escalation.md` — add `"OWASP API Security 2023 API1 — Broken Object Level Authorization"` and `"OWASP API Security 2023 API5 — Broken Function Level Authorization"` to frontmatter `owasp_references` and References section
- [X] T026 [US3] Verify finding template in `agents/stride/denial-of-service.md` demonstrates availability threat findings with actionable mitigations and references (CWE-400, ATT&CK T1499)
- [X] T027 [US3] Verify finding template in `agents/stride/privilege-escalation.md` demonstrates authorization threat findings with actionable mitigations and references (CWE-269, OWASP A01:2021, ATT&CK T1548)

**Checkpoint**: Denial of Service and Elevation of Privilege agents validated and complete

---

## Phase 6: User Story 4 - Consistent Output Format Validation (Priority: P0)

**Goal**: Verify all 6 agents produce findings in identical format conforming to `schemas/finding.yaml` with correct ID prefixes, risk level computation, and framework references.

**Independent Test**: Compare finding template sections across all 6 agents and verify structural consistency, ID prefix conventions, and OWASP 3x3 matrix presence.

### Implementation for User Story 4

- [X] T028 [US4] Cross-compare finding templates across all 6 agents in `agents/stride/` — verify all use identical 10-field IR table structure with consistent column names and descriptions
- [X] T029 [US4] Verify ID prefix conventions across all 6 agents: S-N (spoofing), T-N (tampering), R-N (repudiation), I-N (info-disclosure), D-N (denial-of-service), E-N (privilege-escalation)
- [X] T030 [US4] Verify OWASP 3x3 risk computation matrix is present and identical in all 6 agents (HIGH/HIGH=Critical, LOW/LOW=Note, MEDIUM/HIGH=High)
- [X] T031 [US4] Verify all 6 agents include `output_schema: schemas/finding.yaml` in frontmatter and reference the same schema version

**Checkpoint**: All 6 agents produce consistent, schema-compliant output format

---

## Phase 7: User Story 5 - End-to-End Orchestrator Integration (Priority: P2)

**Goal**: Validate that the orchestrator dispatches to all 6 STRIDE agents and assembles their findings into a complete `threats.md` with correct STRIDE tables, coverage matrix, and risk summary.

**Independent Test**: Run orchestrator against `examples/mermaid-agentic-app/input.md` and verify assembled output has 6 populated STRIDE tables, valid coverage matrix, and accurate risk summary.

### Implementation for User Story 5

- [X] T032 [US5] Run orchestrator against `examples/mermaid-agentic-app/input.md` and verify all 6 STRIDE agents are dispatched per STRIDE-per-Element matrix
- [X] T033 [US5] Verify assembled `threats.md` contains 6 STRIDE tables (one per category) with at least one finding each
- [X] T034 [US5] Verify coverage matrix in assembled output shows correct component-category targeting (e.g., "User" has counts only in S and R columns, "Knowledge Base" has counts in T, I, D columns)
- [X] T035 [US5] Verify 100% component specificity — every finding across all 6 tables references a named component from the input (zero generic findings)
- [X] T036 [US5] Verify risk summary has accurate counts per risk level (Critical, High, Medium, Low, Note) matching the sum across all findings
- [X] T037 [US5] Run orchestrator against `examples/ascii-web-api/input.md` as secondary validation — verify STRIDE tables are populated for a different input format
- [X] T038 [US5] Run orchestrator against `examples/free-text-microservice/input.md` as tertiary validation — verify STRIDE tables are populated for prose-format input

**Checkpoint**: End-to-end integration validated across 3 input formats

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final quality checks and documentation

- [X] T039 [P] Verify all 6 agents have consistent References sections with OWASP Top 10 2021 + OWASP API Security 2023 + CWE + MITRE ATT&CK cross-references
- [X] T040 Review and confirm no schema modifications were made to `schemas/finding.yaml` (read-only constraint)
- [X] T041 Update expected output files in `examples/mermaid-agentic-app/threats.md` if integration validation produced updated findings

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Empty — no blocking prerequisites
- **US1-US3 (Phases 3-5)**: Depend on Setup; can run **in parallel** with each other (each modifies different agent files)
- **US4 (Phase 6)**: Depends on US1-US3 completion (cross-agent consistency check)
- **US5 (Phase 7)**: Depends on US4 completion (integration requires all agents validated)
- **Polish (Phase 8)**: Depends on US5 completion

### User Story Dependencies

- **User Story 1 (P0)**: Can start after Setup — modifies only `spoofing.md` and `tampering.md`
- **User Story 2 (P0)**: Can start after Setup — modifies only `repudiation.md` and `info-disclosure.md`
- **User Story 3 (P0)**: Can start after Setup — modifies only `denial-of-service.md` and `privilege-escalation.md`
- **User Story 4 (P0)**: Depends on US1+US2+US3 — reads all 6 agent files for consistency check
- **User Story 5 (P2)**: Depends on US4 — end-to-end integration requires consistent agents

### Parallel Opportunities

- **US1, US2, US3 are fully parallel** — each touches different agent files with zero overlap
- Within each user story, structural audit tasks ([P] marked) can run in parallel
- OWASP API Security addition tasks ([P] marked) can run in parallel within each user story
- Integration validation (US5) runs sequentially against 3 inputs

---

## Parallel Example: Wave 1 (US1 + US2 + US3 in parallel)

```
Agent A: US1 — spoofing.md + tampering.md (T004-T011)
Agent B: US2 — repudiation.md + info-disclosure.md (T012-T019)
Agent C: US3 — denial-of-service.md + privilege-escalation.md (T020-T027)

All three run simultaneously — zero file conflicts.
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 3: US1 — Spoofing + Tampering (T004-T011)
3. **STOP and VALIDATE**: Run Spoofing and Tampering agents against sample input
4. Confirm component-specific, schema-compliant findings

### Incremental Delivery

1. Setup → US1 validated → US2 validated → US3 validated (parallel or sequential)
2. US4 cross-agent consistency check
3. US5 end-to-end integration with orchestrator
4. Polish — each step adds confidence without breaking previous validations

### Parallel Team Strategy

With 3 agents available:

1. All complete Setup together (T001-T003)
2. Once Setup done:
   - Agent A: US1 (spoofing + tampering)
   - Agent B: US2 (repudiation + info-disclosure)
   - Agent C: US3 (denial-of-service + privilege-escalation)
3. US4 consistency check (any single agent)
4. US5 integration validation (any single agent)
5. Polish (single agent)

---

## Notes

- [P] tasks = different files, no dependencies
- All agents are markdown files — "implementation" means content validation and completion, not code
- Validation-by-example: run against sample architectures, check output against schema and quality criteria
- schemas/finding.yaml is **read-only** — no modifications permitted
- Total: 41 tasks across 8 phases
