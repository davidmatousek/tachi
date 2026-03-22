---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "All 5 user stories covered with 48 tasks across 8 phases. All 14 FRs addressed including FR-010. All 10 success criteria achievable. No scope creep detected."
  architect_signoff:
    agent: architect
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "Technically correct across all 5 evaluation criteria. 1 moderate concern: T010/T029 section structure naming may not match actual agent structure (sections vs subsections). 2 minor: T001 missing [P] marker, ASI format inconsistency. No blocking issues."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-22
    status: APPROVED
    notes: "48 tasks, 5 waves, 4 agents. Feasible in 1 sprint (3.3 hours wall-clock, 90% confidence). Dependency chains correct. Parallelism maximized across Phase 3+4+6. 2 informational observations, no blockers."
---

# Tasks: AI Threat Agents

**Input**: Design documents from `/specs/007-ai-threat-agents/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent validation of each story. No test tasks — validation is performed inline via manual review and orchestrator integration runs.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Load reference materials and verify stable dependencies

- [X] T001 Verify `schemas/finding.yaml` supports AI categories (`agentic`, `llm`) and ID prefixes (`AG-*`, `LLM-*`) — read-only check, no modifications
- [X] T002 [P] Verify `docs/INTERFACE-CONTRACT.md` Section 3 defines AI dispatch keywords matching plan's DFD Targeting Matrix
- [X] T003 [P] Verify `examples/mermaid-agentic-app/input.md` contains AI/LLM/agentic components suitable for validation (at minimum: LLM Agent Orchestrator, MCP Tool Server)
- [X] T004 [P] Verify all 5 AI agent files exist in `agents/ai/` (prompt-injection.md, data-poisoning.md, model-theft.md, agent-autonomy.md, tool-abuse.md)

---

## Phase 2: Foundational — Structural Audit (Wave 1)

**Purpose**: Verify all 5 agents have correct structure and frontmatter before content validation

**CRITICAL**: No content validation can begin until structural compliance is confirmed

- [X] T005 [P] Audit frontmatter of `agents/ai/agent-autonomy.md` — verify 6 fields (agent_name, category: agentic, threat_class: AG, dfd_targets: [Process], owasp_references, output_schema: schemas/finding.yaml) and fix any gaps
- [X] T006 [P] Audit frontmatter of `agents/ai/tool-abuse.md` — verify 6 fields (agent_name, category: agentic, threat_class: AG, dfd_targets: [Process], owasp_references, output_schema: schemas/finding.yaml) and fix any gaps
- [X] T007 [P] Audit frontmatter of `agents/ai/prompt-injection.md` — verify 6 fields (agent_name, category: llm, threat_class: LLM, dfd_targets: [Process], owasp_references, output_schema: schemas/finding.yaml) and fix any gaps
- [X] T008 [P] Audit frontmatter of `agents/ai/data-poisoning.md` — verify 6 fields (agent_name, category: llm, threat_class: LLM, dfd_targets: [Data Store, Data Flow], owasp_references, output_schema: schemas/finding.yaml) and fix any gaps
- [X] T009 [P] Audit frontmatter of `agents/ai/model-theft.md` — verify 6 fields (agent_name, category: llm, threat_class: LLM, dfd_targets: [Data Store, Process], owasp_references, output_schema: schemas/finding.yaml) and fix any gaps
- [X] T010 [P] Audit section structure of all 5 agents in `agents/ai/` — verify each has canonical sections in order: Purpose, Detection Scope, Patterns/Indicators, Finding Template, Risk Level Computation, References. Flag missing or misordered sections

**Checkpoint**: All 5 agents pass structural audit — content validation can begin

---

## Phase 3: User Story 1 — Agentic Threat Agent Validation (Priority: P0)

**Goal**: Validate agent-autonomy and tool-abuse agents produce correct, component-specific findings with OWASP Agentic/MCP references

**Independent Test**: Run each agentic agent against `examples/mermaid-agentic-app/input.md` and verify AG-prefixed findings reference named components (e.g., "LLM Agent Orchestrator", "MCP Tool Server")

### Implementation for User Story 1

- [X] T011 [P] [US1] Validate detection patterns in `agents/ai/agent-autonomy.md` cover all PRD FR-8 subcategories: excessive autonomy, goal misalignment, unconstrained action scope, missing human-in-the-loop, cascading failures across agents, autonomous resource consumption. Add any missing subcategories
- [X] T012 [P] [US1] Validate detection patterns in `agents/ai/tool-abuse.md` cover all PRD FR-8 subcategories: unauthorized tool invocation, capability escalation, parameter injection, tool chain manipulation, tool poisoning (direct, shadowing, rug pulls). Add any missing subcategories
- [X] T013 [US1] Verify finding template in `agents/ai/agent-autonomy.md` demonstrates component-specific threats — example must reference a named component (not generic "the agent"), describe attacker action + trust assumption violated (FR-010), and include actionable mitigation (FR-011)
- [X] T014 [US1] Verify finding template in `agents/ai/tool-abuse.md` demonstrates component-specific threats — example must reference a named component, describe attacker action + trust assumption violated, and include actionable mitigation
- [X] T015 [US1] Verify OWASP references in `agents/ai/agent-autonomy.md` — must include ASI01, ASI06, ASI08, ASI09, ASI10 in references section with correct format
- [X] T016 [US1] Verify OWASP references in `agents/ai/tool-abuse.md` — must include ASI02, ASI04, MCP03:2025, MCP05:2025 in references section with correct format
- [X] T017 [US1] Verify `agents/ai/agent-autonomy.md` produces empty results guidance — agent must include instructions to produce zero findings when no AI/agent components are present in architecture input
- [X] T018 [US1] Verify `agents/ai/tool-abuse.md` produces empty results guidance — agent must include instructions to produce zero findings when no tool server/MCP/plugin components are present

**Checkpoint**: Both agentic agents validated — AG-prefixed findings are component-specific, schema-compliant, and OWASP-grounded

---

## Phase 4: User Story 2 — LLM Threat Agent Validation (Priority: P0)

**Goal**: Validate prompt-injection, data-poisoning, and model-theft agents produce correct, component-specific findings with OWASP LLM references

**Independent Test**: Run each LLM agent against `examples/mermaid-agentic-app/input.md` and verify LLM-prefixed findings reference named components

### Implementation for User Story 2

- [X] T019 [P] [US2] Validate detection patterns in `agents/ai/prompt-injection.md` cover all PRD FR-8 subcategories: direct injection, indirect injection (via documents/URLs), jailbreaking, system prompt extraction, cross-plugin injection. Add any missing subcategories
- [X] T020 [P] [US2] Validate detection patterns in `agents/ai/data-poisoning.md` cover all PRD FR-8 subcategories: training data manipulation, RAG index poisoning, knowledge base corruption, fine-tuning supply chain attacks, context window contamination. Add any missing subcategories
- [X] T021 [P] [US2] Validate detection patterns in `agents/ai/model-theft.md` cover all PRD FR-8 subcategories: model extraction via API queries, model weight exfiltration, unbounded inference consumption, model supply chain compromise. Add any missing subcategories
- [X] T022 [US2] Verify finding template in `agents/ai/prompt-injection.md` demonstrates component-specific threats — must reference a named LLM component, describe attacker action + trust assumption violated, include actionable mitigation
- [X] T023 [US2] Verify finding template in `agents/ai/data-poisoning.md` demonstrates component-specific threats — must reference named data stores or data flows, not generic "the database"
- [X] T024 [US2] Verify finding template in `agents/ai/model-theft.md` demonstrates component-specific threats — must reference named model hosting component, not generic "the model"
- [X] T025 [P] [US2] Verify OWASP references in `agents/ai/prompt-injection.md` — must include LLM01:2025, LLM07:2025 with correct format
- [X] T026 [P] [US2] Verify OWASP references in `agents/ai/data-poisoning.md` — must include LLM03:2025, LLM04:2025, LLM08:2025 with correct format
- [X] T027 [P] [US2] Verify OWASP references in `agents/ai/model-theft.md` — must include LLM03:2025, LLM10:2025 with correct format
- [X] T028 [US2] Verify all 3 LLM agents include empty results guidance — each must instruct to produce zero findings when no LLM/model components are present

**Checkpoint**: All 3 LLM agents validated — LLM-prefixed findings are component-specific, schema-compliant, and OWASP-grounded

---

## Phase 5: User Story 3 — Consistent Output Format (Priority: P0)

**Goal**: Verify all 5 agents produce findings in identical format conforming to `schemas/finding.yaml` with correct category values and ID prefixes

**Independent Test**: Compare finding template sections across all 5 agents — all must define the same 10 IR fields with consistent formatting

### Implementation for User Story 3

- [X] T029 [US3] Cross-check all 5 agents in `agents/ai/` for identical section organization — verify each follows: Purpose, Detection Scope, Patterns/Indicators, Finding Template, Risk Level Computation, References (FR-012)
- [X] T030 [US3] Cross-check finding templates across all 5 agents — verify all define 10 IR fields (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type) with consistent field names
- [X] T031 [US3] Verify ID prefix conventions — agentic agents use AG-N, LLM agents use LLM-N, N starts at 1 and increments sequentially
- [X] T032 [US3] Verify category field values — agentic agents use `agentic`, LLM agents use `llm` (matching `schemas/finding.yaml` enum)
- [X] T033 [US3] Verify risk computation sections in all 5 agents use identical OWASP 3x3 matrix (HIGH/HIGH=Critical, HIGH/MEDIUM=High, MEDIUM/MEDIUM=Medium, LOW/LOW=Note)
- [X] T034 [US3] Verify all 5 agents reference `schemas/finding.yaml` as output_schema in frontmatter

**Checkpoint**: All 5 agents produce format-consistent findings — orchestrator can assemble without conversion

---

## Phase 6: User Story 4 — Two-Layer Keyword Dispatch Validation (Priority: P0)

**Goal**: Verify orchestrator correctly dispatches to AI agents using two-layer keyword model

**Independent Test**: Trace dispatch logic through `agents/orchestrator.md` and `docs/INTERFACE-CONTRACT.md` Section 3 against the expected dispatch matrix from plan.md

### Implementation for User Story 4

- [X] T035 [US4] Verify Layer 1 dispatch keywords in `docs/INTERFACE-CONTRACT.md` Section 3 match orchestrator implementation in `agents/orchestrator.md` — LLM keywords activate 3 LLM agents, agentic keywords activate 2 agentic agents
- [X] T036 [US4] Verify Layer 2 detection scope keywords in each of the 5 agents in `agents/ai/` extend (not conflict with) Layer 1 keywords — document per-agent keyword additions
- [X] T037 [US4] Verify dual-dispatch behavior — confirm `agents/orchestrator.md` activates both LLM and agentic agents when a component matches keywords from both categories (e.g., "LLM Agent Orchestrator")
- [X] T038 [US4] Verify dispatch matrix against `examples/mermaid-agentic-app/input.md` — trace each component through Layer 1 keywords and confirm expected AI agent activation matches plan's Two-Layer Keyword Dispatch Validation Matrix

**Checkpoint**: Two-layer dispatch verified — correct agents activate for correct components

---

## Phase 7: User Story 5 — End-to-End Orchestrator Integration (Priority: P1)

**Goal**: Run orchestrator against sample architecture and verify complete threat model output with both STRIDE and AI tables

**Independent Test**: Execute orchestrator against `examples/mermaid-agentic-app/input.md` and verify `threats.md` contains AG and LLM tables with component-specific findings

### Implementation for User Story 5

- [X] T039 [US5] Run orchestrator against `examples/mermaid-agentic-app/input.md` and verify output `threats.md` contains AG threat table with AG-prefixed findings from agent-autonomy and tool-abuse agents
- [X] T040 [US5] Verify output `threats.md` contains LLM threat table with LLM-prefixed findings from prompt-injection, data-poisoning, and model-theft agents
- [X] T041 [US5] Verify 100% component specificity — every finding across AG and LLM tables references a named component from the input (zero generic findings)
- [X] T042 [US5] Verify risk_level values in all AI findings match OWASP 3x3 matrix computation from their likelihood and impact values
- [X] T043 [US5] Verify coverage matrix in output shows AI agent dispatch for "LLM Agent Orchestrator" (dual-dispatch) and "MCP Tool Server" (agentic only), and no AI dispatch for "Knowledge Base", "User", "External API"
- [X] T044 [US5] Verify finding ID namespaces don't conflict — AG/LLM prefixes are separate from S/T/R/I/D/E prefixes in the same `threats.md`
- [X] T045 [US5] Verify empty results — confirm non-AI components (User, Knowledge Base, External API) have no entries in AG or LLM tables

**Checkpoint**: End-to-end integration validated — complete threat model with 8 tables (6 STRIDE + 2 AI) works correctly

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: P1 improvements and documentation

- [X] T046 [P] Add MITRE ATLAS cross-references to all 5 agents in `agents/ai/` where applicable (P1 deliverable)
- [X] T047 [P] Add CWE identifiers to agents in `agents/ai/` where applicable — prompt-injection (CWE-77), data-poisoning (CWE-1321), model-theft (CWE-200)
- [X] T048 Verify `agents/ai/README.md` accurately documents the 5-agent-to-2-table mapping (AG table: agent-autonomy + tool-abuse; LLM table: prompt-injection + data-poisoning + model-theft)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 Agentic (Phase 3)**: Depends on Foundational — can run in parallel with US2
- **US2 LLM (Phase 4)**: Depends on Foundational — can run in parallel with US1
- **US3 Format (Phase 5)**: Depends on US1 + US2 (requires individual agents validated)
- **US4 Dispatch (Phase 6)**: Depends on Foundational — can run in parallel with US1/US2
- **US5 E2E (Phase 7)**: Depends on US1 + US2 + US3 + US4 (all agents validated and dispatch verified)
- **Polish (Phase 8)**: Depends on US5 (core validation complete)

### User Story Dependencies

- **US1 (P0)**: Can start after Foundational — No dependencies on other stories
- **US2 (P0)**: Can start after Foundational — No dependencies on other stories
- **US3 (P0)**: Depends on US1 + US2 completion (needs all agents individually validated)
- **US4 (P0)**: Can start after Foundational — reads orchestrator and interface contract, independent of agent content
- **US5 (P1)**: Depends on all P0 stories (US1-US4) — full integration test

### Parallel Opportunities

- **Phase 1**: T002, T003, T004 can run in parallel
- **Phase 2**: T005-T010 can all run in parallel (different files)
- **Phase 3 + Phase 4**: US1 and US2 can run entirely in parallel (agentic vs LLM tracks)
- **Phase 3**: T011, T012 can run in parallel (different agents)
- **Phase 4**: T019, T020, T021 can run in parallel; T025, T026, T027 can run in parallel
- **Phase 6**: Can run in parallel with Phases 3-4 (reads different files)
- **Phase 8**: T046, T047 can run in parallel

---

## Parallel Example: User Story 1 + User Story 2 (Wave 2)

```
# Track A (Agentic) — can run simultaneously with Track B:
Task: T011 "Validate detection patterns in agents/ai/agent-autonomy.md"
Task: T012 "Validate detection patterns in agents/ai/tool-abuse.md"

# Track B (LLM) — can run simultaneously with Track A:
Task: T019 "Validate detection patterns in agents/ai/prompt-injection.md"
Task: T020 "Validate detection patterns in agents/ai/data-poisoning.md"
Task: T021 "Validate detection patterns in agents/ai/model-theft.md"
```

---

## Implementation Strategy

### MVP First (US1 + US2 — Core Agent Validation)

1. Complete Phase 1: Setup (verify dependencies)
2. Complete Phase 2: Structural Audit (all 5 agents)
3. Complete Phase 3: US1 Agentic agents + Phase 4: US2 LLM agents (in parallel)
4. **STOP and VALIDATE**: Each agent produces component-specific, schema-compliant findings
5. Core value delivered — all 5 AI agents validated

### Incremental Delivery

1. Setup + Structural Audit -> Foundation ready
2. US1 + US2 (parallel) -> Individual agents validated -> Core MVP
3. US3 -> Cross-agent consistency confirmed
4. US4 -> Dispatch correctness confirmed
5. US5 -> End-to-end integration validated -> Feature complete
6. Polish -> P1 cross-references added

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No test tasks — validation is inline (prompt files, not code)
- Each phase checkpoint is independently verifiable
- Total: 48 tasks across 8 phases
