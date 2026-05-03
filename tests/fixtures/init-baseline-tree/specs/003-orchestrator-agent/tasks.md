---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED
    notes: "6/6 user stories covered, 18/18 FRs addressed, 0 scope creep. P1-before-P2 correct. 2 LOW observations (US5/US6 folding annotation, stub-agent validation implicit)."
  architect_signoff:
    agent: architect
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered. Parallel waves safe. 12 cross-references verified. 2 MEDIUM concerns (agent context payload format, component name output sanitization) addressable during implementation."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "35 tasks appropriate granularity. Critical path correct. 4-6 hour estimate realistic (75% confidence). 6-wave execution plan with senior-backend-engineer primary. 4 LOW, 2 INFORMATIONAL findings."
---

# Tasks: Orchestrator Agent

**Input**: Design documents from `specs/003-orchestrator-agent/`
**Prerequisites**: plan.md (approved), spec.md (approved), research.md

**Tests**: Not requested in specification. Validation-by-example tasks included in Polish phase.

**Organization**: Tasks grouped by user story. All tasks target a single file (`agents/orchestrator.md`) — parallelization is within sections that do not depend on each other.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different sections, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- All tasks target `agents/orchestrator.md` unless otherwise noted

---

## Phase 1: Setup

**Purpose**: Read F-001 reference artifacts and establish orchestrator prompt structure

- [X] T001 Read all F-001 reference artifacts: docs/INTERFACE-CONTRACT.md, templates/threats.md, schemas/finding.yaml, schemas/input.yaml, schemas/output.yaml, agents/ai/README.md, agents/stride/README.md, and all 11 agent files in agents/stride/ and agents/ai/
- [X] T002 Author orchestrator prompt frontmatter (agent_name, category, status, version, references) and Role & Purpose section establishing orchestrator identity and output constraints in agents/orchestrator.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prompt infrastructure sections that all OWASP phases reference

**CRITICAL**: These sections must be complete before any OWASP phase section can be authored

- [X] T003 Author Input Sanitization Boundary section with XML-style boundary markers (`<architecture-input>`) separating orchestrator instructions from user content in agents/orchestrator.md
- [X] T004 [P] Author Output Format Specification subsection defining frontmatter requirements (schema_version, date, input_format, classification) and the 7-section output structure per templates/threats.md in agents/orchestrator.md

**Checkpoint**: Prompt skeleton established — OWASP phase authoring can begin

---

## Phase 3: User Story 1 — Parse Architecture into Component Inventory (Priority: P1) MVP

**Goal**: Orchestrator parses any of 5 supported input formats, classifies components as DFD element types, identifies trust boundaries, and produces a System Overview

**Independent Test**: Provide `examples/mermaid-agentic-app/input.md` and verify 5 components classified with correct DFD types (User → External Entity, LLM Agent Orchestrator → Process, MCP Tool Server → Process, Knowledge Base → Data Store, External API → External Entity)

### Implementation for User Story 1

- [X] T005 [US1] Author Phase 1 Scope preamble with OWASP question ("What are we working on?") and phase objectives in agents/orchestrator.md
- [X] T006 [US1] Author format detection instructions with heuristic priority order (ASCII → free-text → Mermaid → PlantUML → C4) and explicit format override logic per docs/INTERFACE-CONTRACT.md Section 1 in agents/orchestrator.md
- [X] T007 [US1] Author component extraction instructions with DFD classification heuristics and concrete examples for each element type (External Entity, Process, Data Store, Data Flow) in agents/orchestrator.md
- [X] T008 [US1] Author trust boundary identification instructions with format-specific notation (subgraph for Mermaid, dashed lines for ASCII, boundary for PlantUML, System_Boundary for C4, section headers for free-text) in agents/orchestrator.md
- [X] T009 [US1] Author System Overview assembly instructions producing Components table, Data Flows table, and Technologies table per templates/threats.md Section 1 in agents/orchestrator.md
- [X] T010 [US1] Author intermediate output requirement: orchestrator must produce complete component inventory (name, DFD type, description) as a visible intermediate artifact before proceeding to Phase 2 in agents/orchestrator.md

**Checkpoint**: Phase 1 (Scope) section complete — orchestrator can parse any input format and classify components

---

## Phase 4: User Story 2 — Dispatch to Correct Threat Agents (Priority: P1)

**Goal**: Orchestrator dispatches each component to correct STRIDE and AI agents based on DFD type and keyword matching, with full architecture context

**Independent Test**: Parse mermaid-agentic-app and verify "LLM Agent Orchestrator" gets dual-dispatch (STRIDE + LLM + AG), "MCP Tool Server" gets STRIDE + AG, "User" gets S and R only

### Implementation for User Story 2

- [X] T011 [US2] Author Phase 2 Determine Threats preamble with OWASP question ("What can go wrong?") and phase objectives in agents/orchestrator.md
- [X] T012 [US2] Embed STRIDE-per-Element normalization table verbatim from docs/INTERFACE-CONTRACT.md Section 2 (External Entity → S,R | Process → S,T,R,I,D,E | Data Store → T,I,D | Data Flow → T,I,D) in agents/orchestrator.md
- [X] T013 [US2] Author AI keyword dispatch rules from docs/INTERFACE-CONTRACT.md Section 3: LLM keywords (LLM, model, GPT, Claude), AG keywords (agent, autonomous, orchestrator, MCP server, tool server, plugin), dual-dispatch logic, case-insensitive matching in agents/orchestrator.md
- [X] T014 [US2] Author agent invocation protocol specifying that each agent receives full parsed architecture context (all components, data flows, trust boundaries) and is told which specific component(s) to analyze in agents/orchestrator.md
- [X] T015 [US2] Author dispatch protocol documentation for both parallel mode (all agents concurrently, collect before assembly) and sequential mode (category order: S, T, R, I, D, E, AG, LLM) in agents/orchestrator.md
- [X] T016 [US2] Author intermediate output requirement: orchestrator must produce dispatch table (component → agent list) as a visible intermediate artifact before invoking agents in agents/orchestrator.md

**Checkpoint**: Phase 2 (Determine Threats) section complete — orchestrator can dispatch to all 11 agents with correct targeting

---

## Phase 5: User Story 3 — Assemble Findings into Structured Threat Model (Priority: P1)

**Goal**: Orchestrator collects agent findings, validates risk levels, assembles 8 tables (6 STRIDE + 2 AI), generates coverage matrix, risk summary, and recommended actions into a complete threats.md

**Independent Test**: Collect findings from mermaid-agentic-app dispatch and verify assembled threats.md has all 7 sections, valid frontmatter, correct 5-to-2 AI table mapping, and OWASP 3x3-compliant risk levels

### Implementation for User Story 3

- [X] T017 [US3] Author Phase 3 Determine Countermeasures preamble with OWASP question ("What are we going to do about it?") and finding collection instructions in agents/orchestrator.md
- [X] T018 [US3] Author risk_level validation logic embedding OWASP 3x3 matrix from schemas/finding.yaml (HIGH/HIGH → Critical, HIGH/MEDIUM → High, etc.) with correction instructions for mismatched values in agents/orchestrator.md
- [X] T019 [P] [US3] Author STRIDE table assembly instructions producing 6 tables (S, T, R, I, D, E) with finding rows conforming to templates/threats.md Section 3 field definitions (ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation) in agents/orchestrator.md
- [X] T020 [P] [US3] Author AI threat table assembly instructions with 5-agent-to-2-table mapping (agent-autonomy + tool-abuse → AG table; prompt-injection + data-poisoning + model-theft → LLM table) per agents/ai/README.md in agents/orchestrator.md
- [X] T021 [US3] Author Phase 4 Assess preamble with OWASP question ("Did we do a good enough job?") in agents/orchestrator.md
- [X] T022 [US3] Author coverage matrix generation instructions producing components-as-rows × categories-as-columns (S, T, R, I, D, E, AG, LLM) with finding counts per cell and `-` for analyzed-but-empty cells in agents/orchestrator.md
- [X] T023 [US3] Author risk summary computation (count and percentage per risk level: Critical, High, Medium, Low, Note) and recommended actions list generation (sorted by risk level descending) in agents/orchestrator.md
- [X] T024 [US3] Author output structural validation checklist: verify 7 sections present, frontmatter complete, finding IDs match pattern `{CATEGORY_PREFIX}-{N}`, all required fields populated in agents/orchestrator.md

**Checkpoint**: Phases 3-4 (Countermeasures + Assess) complete — orchestrator produces a valid threats.md

---

## Phase 6: User Story 4 — Handle Errors Gracefully (Priority: P2)

**Goal**: Orchestrator returns correct error codes with actionable messages for invalid inputs and handles ambiguous classifications predictably

**Independent Test**: Provide empty input (NO_COMPONENTS), invalid format value (INVALID_FORMAT_VALUE), and unrecognizable format (UNSUPPORTED_FORMAT) and verify correct error responses

### Implementation for User Story 4

- [X] T025 [P] [US4] Author UNSUPPORTED_FORMAT error response section listing supported formats with guidance per docs/INTERFACE-CONTRACT.md Section 7 in agents/orchestrator.md
- [X] T026 [P] [US4] Author NO_COMPONENTS error response section stating minimum requirements (1 component, 1 data flow) per docs/INTERFACE-CONTRACT.md Section 7 in agents/orchestrator.md
- [X] T027 [P] [US4] Author INVALID_FORMAT_VALUE error response section listing allowed enum values per docs/INTERFACE-CONTRACT.md Section 7 in agents/orchestrator.md
- [X] T028 [US4] Author ambiguous classification handling: default to Process for uncertain DFD types, flag for human review; include AI keyword ambiguity notes (e.g., "model" as data model vs LLM) in agents/orchestrator.md
- [X] T029 [US4] Author non-conforming finding handling: flag findings that do not conform to schemas/finding.yaml for review rather than dropping silently; show `-` in coverage matrix for zero-finding cells in agents/orchestrator.md

**Checkpoint**: Error handling complete — orchestrator degrades gracefully for all edge cases

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete orchestrator prompt against examples and schemas

- [X] T030 [P] Validate orchestrator prompt against examples/mermaid-agentic-app/input.md: verify format detection (mermaid), 5 correct DFD classifications, dual-dispatch for "LLM Agent Orchestrator", AG dispatch for "MCP Tool Server", output has all 7 sections
- [X] T031 [P] Validate orchestrator prompt against examples/ascii-web-api/input.md: verify format detection (ASCII), component extraction, trust boundary identification
- [X] T032 [P] Validate orchestrator prompt against examples/free-text-microservice/input.md: verify format detection (free-text), component extraction from prose
- [X] T033 Review complete prompt for platform-specific syntax (no Claude Code Task tool calls, no Cursor agent references, no platform-specific invocation) per SC-010
- [X] T034 Review complete prompt for interface contract compliance: verify STRIDE-per-Element table matches docs/INTERFACE-CONTRACT.md Section 2 verbatim, AI keywords match Section 3, error codes match Section 7
- [X] T035 Final review of prompt length and readability: verify clear section headers, concise instructions, no unnecessary verbosity, logical flow from Phase 1 through Phase 4

**Checkpoint**: Orchestrator prompt validated — ready for PR

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T002) — BLOCKS all user stories
- **US1 Parse (Phase 3)**: Depends on Foundational (T003-T004)
- **US2 Dispatch (Phase 4)**: Depends on US1 (T005-T010) — dispatch references parsed component inventory
- **US3 Assemble (Phase 5)**: Depends on US2 (T011-T016) — assembly references dispatch targets
- **US4 Error Handling (Phase 6)**: Depends on US1 (T005-T010) — errors reference parsing and classification
- **Polish (Phase 7)**: Depends on all user stories complete (T005-T029)

### User Story Dependencies

- **US1 (P1)**: Start after Foundational — no story dependencies
- **US2 (P1)**: Start after US1 — references component inventory from US1
- **US3 (P1)**: Start after US2 — references dispatch targets from US2
- **US4 (P2)**: Start after US1 — can run in parallel with US2/US3 (different sections)
- **US5 (P2)**: Covered within US2 tasks (T015 documents both dispatch modes)
- **US6 (P2)**: Covered within Foundational tasks (T003 establishes sanitization boundary)

### Within Each User Story

- Preamble before detailed instructions
- Reference data before logic that uses it
- Instructions before intermediate output requirements

### Parallel Opportunities

- T003 and T004 (Foundational) can run in parallel
- T019 and T020 (STRIDE tables and AI tables) can run in parallel
- T025, T026, T027 (error responses) can all run in parallel
- T030, T031, T032 (example validations) can all run in parallel
- US4 can run in parallel with US2/US3 (different prompt sections)

---

## Parallel Example: Foundational Phase

```
# Launch both foundational tasks together:
Task: "Author Input Sanitization Boundary section in agents/orchestrator.md"
Task: "Author Output Format Specification subsection in agents/orchestrator.md"
```

## Parallel Example: Error Handling Phase

```
# Launch all three error response tasks together:
Task: "Author UNSUPPORTED_FORMAT error response in agents/orchestrator.md"
Task: "Author NO_COMPONENTS error response in agents/orchestrator.md"
Task: "Author INVALID_FORMAT_VALUE error response in agents/orchestrator.md"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T004)
3. Complete Phase 3: US1 Parse (T005-T010)
4. **STOP and VALIDATE**: Test with mermaid example — verify component inventory and DFD classification
5. This delivers a working parser even before dispatch/assembly

### Incremental Delivery

1. Setup + Foundational → Prompt skeleton ready
2. Add US1 (Parse) → Test format detection and DFD classification (MVP!)
3. Add US2 (Dispatch) → Test agent targeting with mermaid example
4. Add US3 (Assemble) → Test complete end-to-end flow with output validation
5. Add US4 (Error Handling) → Test edge cases and error conditions
6. Polish → Validate all 3 examples, review for compliance
7. Each increment adds value without breaking previous sections

### Single-Agent Strategy

Since all tasks target one file, sequential execution by a single agent is most practical:
1. Agent reads all F-001 artifacts (T001)
2. Agent authors sections top-to-bottom (T002 → T029)
3. Agent validates with examples (T030-T035)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 35 |
| Setup tasks | 2 |
| Foundational tasks | 2 |
| US1 tasks | 6 |
| US2 tasks | 6 |
| US3 tasks | 8 |
| US4 tasks | 5 |
| Polish tasks | 6 |
| Parallel opportunities | 4 waves (Foundational, Tables, Errors, Validation) |
| MVP scope | Phase 1-3 (T001-T010): format detection + DFD classification |
| Estimated effort | 4-6 hours (per Team-Lead PRD estimate) |
