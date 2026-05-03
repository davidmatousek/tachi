---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 5 user stories covered, all 12 FRs addressed, no scope creep, MVP scope viable, tasks organized by user story"
  architect_signoff:
    agent: architect
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "All 8 evaluation criteria pass. Non-blocking concern: spec FR-012 uses ASCII hyphens vs em dash — tasks.md correctly enforces U+2014"
  techlead_signoff:
    agent: team-lead
    date: 2026-03-23
    status: APPROVED
    notes: "50 tasks fit 2.5-day timeline at 75% confidence. 4-wave strategy optimal. Agent assignments feasible. No hidden dependencies"
---

# Tasks: Example Threat Models

**Input**: Design documents from `/specs/024-example-threat-models/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not requested in spec — test tasks omitted. Validation is covered in the Polish phase.

**Organization**: Tasks grouped by user story. US1–US3 (all P1) can execute in parallel after Setup. US4–US5 (P2) depend on US1–US3 completion.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Directory Scaffold)

**Purpose**: Create standardized directory structure for all three examples

- [X] T001 Create directory `examples/web-app/`
- [X] T002 [P] Create directory `examples/agentic-app/`
- [X] T003 [P] Create directory `examples/microservices/`

**Checkpoint**: All three example directories exist alongside the existing format-specific test fixtures.

---

## Phase 2: User Story 1 — Web App Example (Priority: P1)

**Goal**: A developer evaluating tachi for traditional web apps can see a complete STRIDE threat model with OWASP Web 2025 cross-references and correctly empty AI sections.

**Independent Test**: Open `examples/web-app/architecture.md` in GitHub, confirm Mermaid renders. Open `threats.md`, confirm all 8 schema v1.1 sections present, STRIDE populated, AI sections empty.

### Implementation for User Story 1

- [X] T004 [P] [US1] Create Mermaid architecture diagram with at least 4 components (Web Client, API Gateway, Auth Service, User Database), trust boundary subgraphs, and labeled data flow arrows in `examples/web-app/architecture.md`
- [X] T005 [US1] Author Section 1 (System Overview) with components table, data flows table, and technologies table in `examples/web-app/threats.md`
- [X] T006 [US1] Author Section 2 (Trust Boundaries) with trust zones and boundary crossings tables in `examples/web-app/threats.md`
- [X] T007 [US1] Author Section 3 (STRIDE Tables) — all 6 categories (S, T, R, I, D, E) populated with findings per STRIDE-per-Element rules in `examples/web-app/threats.md`
- [X] T008 [US1] Author Section 4 (AI Threat Tables) showing "No AI components detected" with empty AG and LLM tables in `examples/web-app/threats.md`
- [X] T009 [US1] Author Section 4a (Correlated Findings) showing "No cross-agent correlations detected" with empty table in `examples/web-app/threats.md`
- [X] T010 [US1] Author Section 5 (Coverage Matrix) using three-state model (count, `—` em dash, `n/a`) with correct STRIDE-per-Element rules and AG/LLM columns as `n/a` in `examples/web-app/threats.md`
- [X] T011 [US1] Author Section 6 (Risk Summary) with OWASP 3x3 calibration matrix and deduplicated counts in `examples/web-app/threats.md`
- [X] T012 [US1] Author Section 7 (Recommended Actions) sorted by risk level descending in `examples/web-app/threats.md`
- [X] T013 [US1] Author OWASP Framework Cross-Reference appendix mapping findings to OWASP Top 10 Web 2025 (A01–A10) with at least 5 distinct categories in `examples/web-app/threats.md`
- [X] T014 [US1] Add YAML frontmatter with `schema_version: "1.1"`, `date`, `input_format: "mermaid"`, `classification: "confidential"` to `examples/web-app/threats.md`

**Checkpoint**: Web-app example is complete and independently verifiable.

---

## Phase 3: User Story 2 — Agentic App Example (Priority: P1)

**Goal**: An AI developer evaluating tachi sees STRIDE + AI findings with correlated findings and OWASP Agentic/MCP cross-references demonstrating the unique value of AI-specific threat agents.

**Independent Test**: Open `examples/agentic-app/architecture.md` in GitHub, confirm Mermaid renders and dual-dispatch triggers present. Open `threats.md`, confirm STRIDE + AG + LLM findings, Section 4a correlated groups, and OWASP appendix with ASI and MCP categories.

### Implementation for User Story 2

- [X] T015 [P] [US2] Create Mermaid architecture diagram with at least 5 components (User, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, External API), trust boundary subgraphs, labeled data flows, and component names that trigger correct AI dispatch keywords in `examples/agentic-app/architecture.md`
- [X] T016 [US2] Author Section 1 (System Overview) with components table including DFD element types that trigger dual-dispatch, data flows, and technologies in `examples/agentic-app/threats.md`
- [X] T017 [US2] Author Section 2 (Trust Boundaries) with trust zones and boundary crossings in `examples/agentic-app/threats.md`
- [X] T018 [US2] Author Section 3 (STRIDE Tables) — all 6 categories populated. Ensure at least one STRIDE finding targets a component that also has AI findings to enable correlation in `examples/agentic-app/threats.md`
- [X] T019 [US2] Author Section 4 (AI Threat Tables) with populated AG findings (agent-autonomy, tool-abuse) referencing ASI categories and LLM findings (prompt-injection, data-poisoning) referencing LLM/MCP categories in `examples/agentic-app/threats.md`
- [X] T020 [US2] Author Section 4a (Correlated Findings) with at least 1 correlation group using rules CR-1 through CR-5 (e.g., Tampering + Data-Poisoning on same component) in `examples/agentic-app/threats.md`
- [X] T021 [US2] Author Section 5 (Coverage Matrix) with full 8-column layout (S/T/R/I/D/E/AG/LLM), deduplicated counts, and correlation footnote in `examples/agentic-app/threats.md`
- [X] T022 [US2] Author Section 6 (Risk Summary) with raw/deduplicated parenthetical notation and OWASP 3x3 matrix in `examples/agentic-app/threats.md`
- [X] T023 [US2] Author Section 7 (Recommended Actions) with all findings sorted by risk level descending in `examples/agentic-app/threats.md`
- [X] T024 [US2] Author OWASP Framework Cross-Reference appendix mapping: STRIDE findings to OWASP Top 10 Web 2025, AG findings to OWASP Agentic Top 10 (ASI01–ASI10, at least 3 categories), LLM/MCP findings to OWASP MCP Top 10 (MCP01–MCP10, at least 2 categories) in `examples/agentic-app/threats.md`
- [X] T025 [US2] Add YAML frontmatter with `schema_version: "1.1"`, `date`, `input_format: "mermaid"`, `classification: "confidential"` to `examples/agentic-app/threats.md`

**Checkpoint**: Agentic-app example is complete with AI-specific findings and cross-agent correlations.

---

## Phase 4: User Story 3 — Microservices Example (Priority: P1)

**Goal**: A platform engineer sees how tachi handles cross-service threat analysis with many trust boundaries, demonstrating scale to real-world topologies.

**Independent Test**: Open `examples/microservices/architecture.md` in GitHub, confirm Mermaid renders a multi-service topology. Open `threats.md`, confirm cross-service findings, trust boundary analysis across 6+ components, and OWASP Web appendix.

### Implementation for User Story 3

- [X] T026 [P] [US3] Create Mermaid architecture diagram with at least 7 components (API Gateway, Order Service, Payment Service, Notification Service, Inventory Database, Message Queue, External Payment Provider), trust boundary subgraphs, and labeled data flows in `examples/microservices/architecture.md`
- [X] T027 [US3] Author Section 1 (System Overview) with components table, data flows covering service-to-service communication, and technologies in `examples/microservices/threats.md`
- [X] T028 [US3] Author Section 2 (Trust Boundaries) with at least 4 trust zones (External, DMZ, Internal Services, External Services) and boundary crossings in `examples/microservices/threats.md`
- [X] T029 [US3] Author Section 3 (STRIDE Tables) — all 6 categories populated with emphasis on cross-service threats: service-to-service auth (S), message queue tampering (T), inter-service repudiation (R), data leakage between services (I), cascade DoS (D), service impersonation (E) in `examples/microservices/threats.md`
- [X] T030 [US3] Author Section 4 (AI Threat Tables) showing "No AI components detected" with empty AG and LLM tables in `examples/microservices/threats.md`
- [X] T031 [US3] Author Section 4a (Correlated Findings) showing "No cross-agent correlations detected" with empty table in `examples/microservices/threats.md`
- [X] T032 [US3] Author Section 5 (Coverage Matrix) with 7+ component rows, correct STRIDE-per-Element `n/a` cells, and AG/LLM as `n/a` throughout in `examples/microservices/threats.md`
- [X] T033 [US3] Author Section 6 (Risk Summary) with OWASP 3x3 calibration matrix and counts in `examples/microservices/threats.md`
- [X] T034 [US3] Author Section 7 (Recommended Actions) sorted by risk level descending in `examples/microservices/threats.md`
- [X] T035 [US3] Author OWASP Framework Cross-Reference appendix mapping findings to OWASP Top 10 Web 2025 (A01–A10) with at least 5 distinct categories in `examples/microservices/threats.md`
- [X] T036 [US3] Add YAML frontmatter with `schema_version: "1.1"`, `date`, `input_format: "mermaid"`, `classification: "confidential"` to `examples/microservices/threats.md`

**Checkpoint**: Microservices example is complete with cross-service threat analysis at scale.

---

## Phase 5: User Story 4 — Examples README (Priority: P2)

**Goal**: Users navigating to `examples/` see a comprehensive README with framework relationship hierarchy, example-to-framework mapping, and usage instructions.

**Independent Test**: Open `examples/README.md` in GitHub, confirm framework hierarchy Mermaid diagram renders, mapping table is complete, and usage instructions are present.

### Implementation for User Story 4

- [X] T037 [US4] Write overview section describing the purpose of the three standardized examples and the three retained format-specific test fixtures in `examples/README.md`
- [X] T038 [US4] Create framework relationship hierarchy as a Mermaid diagram showing STRIDE as base methodology with OWASP Top 10 Web 2025, Agentic Top 10, and MCP Top 10 as classification overlays in `examples/README.md`
- [X] T039 [US4] Create example-to-framework mapping table (web-app: STRIDE + OWASP Web; agentic-app: STRIDE + OWASP Web + Agentic + MCP; microservices: STRIDE + OWASP Web) in `examples/README.md`
- [X] T040 [US4] Write usage instructions explaining how to run tachi against example `architecture.md` files and compare results against reference `threats.md` in `examples/README.md`

**Checkpoint**: Examples README provides complete orientation for all example types.

---

## Phase 6: User Story 5 — Project README Update (Priority: P2)

**Goal**: New users discover examples from the main project README.

**Independent Test**: Open `README.md` at project root, confirm it links to examples with a description of the three architectures.

### Implementation for User Story 5

- [X] T041 [US5] Update the examples section in `README.md` to link to `examples/README.md` and describe the three standardized examples (web-app, agentic-app, microservices)

**Checkpoint**: Project README references examples for discoverability.

---

## Phase 7: Polish & Validation

**Purpose**: Cross-cutting validation ensuring all examples are schema-compliant, internally consistent, and render correctly.

- [X] T042 Validate all 3 `architecture.md` files render valid Mermaid diagrams in GitHub
- [X] T043 [P] Validate all 3 `threats.md` files have correct YAML frontmatter with `schema_version: "1.1"`
- [X] T044 [P] Validate all 3 `threats.md` files have all 8 sections in correct order per `schemas/output.yaml`
- [X] T045 Validate STRIDE-per-Element rules in all 3 coverage matrices (External Entity: S,R only; Process: all six; Data Store: T,I,D; Data Flow: T,I,D)
- [X] T046 Validate all finding risk levels match OWASP 3x3 matrix (no Likelihood/Impact/Risk inconsistencies)
- [X] T047 Validate agentic-app Section 4a has at least 1 correlated findings group
- [X] T048 Validate OWASP appendix accuracy: web-app maps 5+ A01–A10 categories, agentic-app maps 3+ ASI + 2+ MCP categories, microservices maps 5+ A01–A10 categories
- [X] T049 Verify all 3 existing example directories (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) remain intact and unmodified
- [X] T050 Run quickstart.md validation — confirm all file paths listed in quickstart.md exist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1, US2, US3 (Phases 2–4)**: Depend on Setup. All three can run **in parallel** (different directories, no cross-dependencies)
- **US4 (Phase 5)**: Depends on US1 + US2 + US3 completion (README references all three examples)
- **US5 (Phase 6)**: Depends on US4 completion (project README links to examples README)
- **Validation (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (Web App)**: Can start after Setup — independent of US2, US3
- **US2 (Agentic App)**: Can start after Setup — independent of US1, US3
- **US3 (Microservices)**: Can start after Setup — independent of US1, US2
- **US4 (Examples README)**: Depends on US1 + US2 + US3 (needs to reference all examples)
- **US5 (Project README)**: Depends on US4 (links to examples README)

### Within Each User Story (US1–US3)

1. Architecture diagram first (T004/T015/T026) — informs threat model
2. Threat model sections in order (System Overview → Trust Boundaries → STRIDE → AI → Correlated → Coverage → Risk → Actions)
3. OWASP appendix after STRIDE/AI sections (references finding IDs)
4. Frontmatter last (after all content finalized)

### Parallel Opportunities

- T001, T002, T003 (all Setup dirs) can run in parallel
- T004, T015, T026 (all architecture diagrams) can run in parallel after Setup
- US1, US2, US3 entire phases can run in parallel after Setup
- T042–T050 (validation tasks marked [P]) can run in parallel

---

## Parallel Example: Wave-Based Execution

```
Wave 1 — Setup + Architecture Diagrams (parallel):
  Agent A: T001, T004 (web-app dir + diagram)
  Agent B: T002, T015 (agentic-app dir + diagram)
  Agent C: T003, T026 (microservices dir + diagram)

Wave 2 — Threat Model Authoring (parallel):
  Agent A: T005–T014 (web-app threats.md)
  Agent B: T016–T025 (agentic-app threats.md)
  Agent C: T027–T036 (microservices threats.md)

Wave 3 — READMEs (sequential):
  Agent A: T037–T040 (examples README)
  Agent A: T041 (project README)

Wave 4 — Validation (parallel):
  Agent A: T042–T046 (schema + risk validation)
  Agent B: T047–T050 (OWASP + integrity checks)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (3 directories)
2. Complete Phase 2: US1 — Web App example
3. **STOP and VALIDATE**: Verify Mermaid renders, schema v1.1 compliance, OWASP appendix
4. A single working example already demonstrates tachi's value

### Incremental Delivery

1. Setup → Web App (MVP!)
2. Add Agentic App → adds AI-specific value demonstration
3. Add Microservices → adds scale demonstration
4. Add READMEs → adds orientation and discoverability
5. Validation → ensures cross-example consistency

### Wave Strategy (Recommended)

All three P1 examples in parallel (Wave 1+2), then READMEs (Wave 3), then validation (Wave 4). Total: ~2.5 days per PRD timeline.

---

## Notes

- All deliverables are Markdown files — no compiled code
- The `threats.md` files are hand-authored to match what tachi would produce, using `templates/threats.md` as the structural reference
- Coverage matrix "analyzed-but-clean" cells must use em dash `—` (U+2014), not ASCII hyphens `---`
- Existing examples (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) must not be modified or deleted
- OWASP cross-references are appendix mapping tables, not schema additions to `output.yaml`

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 50 |
| US1 (Web App) | 11 tasks |
| US2 (Agentic App) | 11 tasks |
| US3 (Microservices) | 11 tasks |
| US4 (Examples README) | 4 tasks |
| US5 (Project README) | 1 task |
| Setup | 3 tasks |
| Validation | 9 tasks |
| Parallel opportunities | Waves 1, 2, 4 fully parallelizable |
| MVP scope | US1 only (14 tasks: Setup + US1) |
