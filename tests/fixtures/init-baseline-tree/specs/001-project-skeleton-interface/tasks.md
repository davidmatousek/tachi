---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 user stories covered. All 20 FRs addressed. No scope creep. MVP strategy correct. 5 non-blocking: T023/T024 large scope, field count discrepancy, prior concerns not tracked, implicit directory creation."
  architect_signoff:
    agent: architect
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "Dependency ordering sound. No false parallelism. Naming conventions compliant. Zero anti-patterns. 2 concerns: T004 should note IR field count resolution (10 not 11), agent frontmatter format should reference canonical template."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible. 33 tasks, 7 waves, 3-4 hours wall-clock. 3 agents: senior-backend-engineer (22), security-analyst (7), tester (2). 3 concerns: T029-T031 should be [P], IR field count follow spec (10), T023/T024 start first in Wave 3."
---

# Tasks: Project Skeleton & Interface Contract

**Input**: Design documents from `/specs/001-project-skeleton-interface/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not requested in specification. Validation is by cross-reference integrity and structural inspection.

**Organization**: Tasks grouped by user story for independent implementation. Setup and Foundational phases establish shared contracts that all user stories depend on.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- All file paths are relative to repository root

---

## Phase 1: Setup

**Purpose**: Create new directories and root files needed before any content can be written.

- [X] T001 Create schemas/ directory at repository root
- [X] T002 [P] Create LICENSE file with Apache 2.0 license text at LICENSE

---

## Phase 2: Foundational (Schemas + Configuration)

**Purpose**: Machine-readable contracts and configuration that ALL user stories depend on. Schemas define the IR contract between agents and templates. Configuration updates fix scaffold paths.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 [P] Create schemas/README.md explaining directory purpose, schema relationships (finding→agents, input→parser, output→template), versioning policy, and schema_version 1.0
- [X] T004 [P] Create schemas/finding.yaml with IR schema: 10 fields (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type) each with type, enum/pattern, and description per contracts/finding-ir.md
- [X] T005 [P] Create schemas/input.yaml with input validation schema: format field (enum: auto/ascii/free-text/mermaid/plantuml/c4, default: auto), content field (min_length: 10), context field (optional object), and recognition patterns for all 5 formats per contracts/input-format.md
- [X] T006 [P] Create schemas/output.yaml with output structure schema: frontmatter fields (schema_version, date, input_format, classification), 7 required sections (System Overview, Trust Boundaries, STRIDE Tables, AI Threat Tables, Coverage Matrix, Risk Summary, Recommended Actions) with field definitions per contracts/output-schema.md
- [X] T007 [P] Update adapters/ContextLoading.yaml — correct all scaffold paths: always_load (_Global/VoiceProfile.md → agents/VoiceProfile.md, _Global/StyleGuide.md → agents/StyleGuide.md), on_demand.analyze (_Global/MasterContent/ → agents/MasterContent/, _Config/Terms/ → adapters/Terms/), on_demand.draft (_Global/MasterContent/ → agents/MasterContent/, _Global/Narratives/ → agents/Narratives/, _Config/Presets/ → adapters/Presets/), on_demand.review (_Config/ScoringRubric.md → adapters/ScoringRubric.md), on_demand.export (_Templates/ → templates/)
- [X] T008 [P] Update adapters/ProjectMeta.yaml — populate: project_name: "tachi", description: "Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications", version: "0.1.0", status: "building", domain: "threat-modeling"
- [X] T009 [P] Update adapters/ScoringRubric.md — replace example dimensions with OWASP 3x3 risk scoring: 8 likelihood factors (skill level, motive, opportunity, size, ease of discovery, ease of exploit, awareness, intrusion detection) and 8 impact factors (loss of confidentiality, loss of integrity, loss of availability, loss of accountability, financial damage, reputation damage, non-compliance, privacy violation), set passing threshold to 3, floor to 2, add OWASP 3x3 matrix table mapping likelihood x impact to risk levels (Critical/High/Medium/Low/Note)

**Checkpoint**: Foundation ready — schemas and configuration provide stable contracts for all downstream tasks.

---

## Phase 3: User Story 1 — Navigable Repository Structure (Priority: P1) MVP

**Goal**: Every top-level directory has a README, agents/stride/ has 6 STRIDE agent files, agents/ai/ has 5 AI agent files with 5-to-2 table mapping documented.

**Independent Test**: Clone the repo, open any top-level directory, verify README exists. List agents/stride/ and find 6 agent files + README. List agents/ai/ and find 5 agent files + README with AG/LLM mapping.

### Implementation for User Story 1

- [X] T010 [P] [US1] Create agents/stride/spoofing.md — Spoofing threat agent prompt with frontmatter (agent_name: spoofing, category: stride, threat_class: S, dfd_targets: [External Entity, Process], owasp_references: [], output_schema: schemas/finding.yaml), Purpose, Detection Scope, Finding Template matching IR schema, References
- [X] T011 [P] [US1] Create agents/stride/tampering.md — Tampering threat agent prompt with frontmatter (category: stride, threat_class: T, dfd_targets: [Process, Data Store, Data Flow]), Purpose, Detection Scope, Finding Template, References
- [X] T012 [P] [US1] Create agents/stride/repudiation.md — Repudiation threat agent prompt with frontmatter (category: stride, threat_class: R, dfd_targets: [External Entity, Process]), Purpose, Detection Scope, Finding Template, References
- [X] T013 [P] [US1] Create agents/stride/info-disclosure.md — Information Disclosure threat agent prompt with frontmatter (category: stride, threat_class: I, dfd_targets: [Process, Data Store, Data Flow]), Purpose, Detection Scope, Finding Template, References
- [X] T014 [P] [US1] Create agents/stride/denial-of-service.md — Denial of Service threat agent prompt with frontmatter (category: stride, threat_class: D, dfd_targets: [Process, Data Store, Data Flow]), Purpose, Detection Scope, Finding Template, References
- [X] T015 [P] [US1] Create agents/stride/privilege-escalation.md — Elevation of Privilege threat agent prompt with frontmatter (category: stride, threat_class: E, dfd_targets: [Process]), Purpose, Detection Scope, Finding Template, References
- [X] T016 [P] [US1] Create agents/ai/prompt-injection.md — Prompt Injection threat agent prompt with frontmatter (category: llm, threat_class: LLM, dfd_targets: [Process], owasp_references: [OWASP LLM01:2025], output_schema: schemas/finding.yaml), Purpose, Detection Scope (keywords: LLM, model, GPT, Claude), Finding Template, References
- [X] T017 [P] [US1] Create agents/ai/tool-abuse.md — Tool Abuse threat agent prompt with frontmatter (category: agentic, threat_class: AG, dfd_targets: [Process], owasp_references: [MCP-03], output_schema: schemas/finding.yaml), Purpose, Detection Scope (keywords: agent, MCP server, tool server, plugin), Finding Template, References
- [X] T018 [P] [US1] Create agents/ai/data-poisoning.md — Data Poisoning threat agent prompt with frontmatter (category: llm, threat_class: LLM, dfd_targets: [Data Store, Data Flow], owasp_references: [OWASP LLM03:2025]), Purpose, Detection Scope, Finding Template, References
- [X] T019 [P] [US1] Create agents/ai/model-theft.md — Model Theft threat agent prompt with frontmatter (category: llm, threat_class: LLM, dfd_targets: [Data Store, Process], owasp_references: [OWASP LLM10:2025]), Purpose, Detection Scope, Finding Template, References
- [X] T020 [P] [US1] Create agents/ai/agent-autonomy.md — Agent Autonomy threat agent prompt with frontmatter (category: agentic, threat_class: AG, dfd_targets: [Process], owasp_references: [ASI-01], output_schema: schemas/finding.yaml), Purpose, Detection Scope (keywords: agent, autonomous, orchestrator), Finding Template, References
- [X] T021 [P] [US1] Update agents/ai/README.md — add 5-agent-to-2-table mapping section: AG (Agentic Threats) = agent-autonomy.md + tool-abuse.md (OWASP Agentic Top 10 / MCP Top 10 references), LLM (LLM Threats) = prompt-injection.md + data-poisoning.md + model-theft.md (OWASP LLM Top 10 v2025 references). Include mapping rationale and output table category explanation.
- [X] T022 [P] [US1] Create agents/orchestrator.md — placeholder with frontmatter (agent_name: orchestrator, category: orchestrator, status: placeholder), Purpose section stating "Implemented in F-002", and reference to interface contract for dispatch rules

**Checkpoint**: Repository structure complete — all agent directories populated, all READMEs in place. US1 independently verifiable.

---

## Phase 4: User Story 2 — Interface Contract for Integration (Priority: P1)

**Goal**: docs/INTERFACE-CONTRACT.md exists with all 7 sections answering: what formats, how to invoke, what output, what side effects.

**Independent Test**: Read docs/INTERFACE-CONTRACT.md and verify it answers all 4 integration questions without opening any other file.

### Implementation for User Story 2

- [X] T023 [US2] Create docs/INTERFACE-CONTRACT.md with all 7 sections: (1) Input Specification — 5 formats (ASCII priority 1, Free-text 2, Mermaid 3, PlantUML 4, C4 5) with recognition patterns per format and at least one example valid input each, format field (default: auto) with explicit declaration option; (2) STRIDE-per-Element Normalization Table — YAML mapping: External Entity→S,R / Process→S,T,R,I,D,E / Data Store→T,I,D / Data Flow→T,I,D; (3) AI Extension Dispatch Rules — keyword→category mapping: LLM keywords (LLM, model, GPT, Claude)→LLM agents, Agentic keywords (agent, autonomous, orchestrator, MCP server, tool server, plugin)→AG agents, dual-dispatch when both match with dedup at coverage matrix; (4) Output Specification — reference templates/threats.md and schemas/output.yaml, schema_version 1.0; (5) Invocation Protocol — input: architecture diagram + optional context, output: threats.md per template, side-effects: none beyond writing output files, naming: YYYY-MM-DD-{phase}/threats.md; (6) Input Sanitization Guidance — architecture input treated as data not instructions, agents must include system-level prompt boundaries, output template validates structural integrity; (7) Error Conditions — unsupported format returns error with supported list, no components returns error with minimum requirements (1 component + 1 data flow)

**Checkpoint**: Interface contract complete — integrators can read one document to understand how to use tachi. US2 independently verifiable.

---

## Phase 5: User Story 3 — Consistent Output Template (Priority: P1)

**Goal**: templates/threats.md defines the complete output structure with all 7 sections, field descriptions, and example values.

**Independent Test**: Read templates/threats.md and verify all 7 sections exist with field descriptions and at least one example value per section.

### Implementation for User Story 3

- [X] T024 [US3] Create templates/threats.md with YAML frontmatter (schema_version: "1.0", date: placeholder, input_format: placeholder, classification: confidential) and all 7 content sections: (1) System Overview — field descriptions for components, data flows, technologies with example values; (2) Trust Boundaries — field descriptions for zone names and boundary crossings with examples; (3) STRIDE Tables — 6 separate tables (S/T/R/I/D/E), each with columns: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation, with one example finding row per table; (4) AI Threat Tables — 2 tables (AG and LLM), each with columns: ID, Component, Threat, OWASP Reference, Likelihood, Impact, Risk Level, Mitigation, with one example finding row per table; (5) Coverage Matrix — components as rows, S/T/R/I/D/E/AG/LLM as columns, finding counts as cells, with example matrix; (6) Risk Summary — counts per risk level (Critical/High/Medium/Low/Note) using OWASP 3x3 matrix, with example counts; (7) Recommended Actions — findings sorted by risk level descending with columns: Finding ID, Component, Threat, Risk Level, Mitigation, with example rows

**Checkpoint**: Output template complete — developers can understand the expected output without running any agents. US3 independently verifiable.

---

## Phase 6: User Story 4 — Machine-Readable Schemas (Priority: P2)

**Goal**: schemas/finding.yaml, input.yaml, and output.yaml define complete field specifications for downstream features.

**Independent Test**: Read each schema file and verify field definitions include types, allowed values, and descriptions.

**Note**: Schema files were created in Phase 2 (Foundational). This phase verifies completeness and adds cross-references.

### Implementation for User Story 4

- [X] T025 [US4] Verify and finalize schemas/ completeness — confirm finding.yaml has all 10 fields with types and enums, input.yaml covers all 5 formats with recognition patterns, output.yaml matches templates/threats.md sections exactly, schemas/README.md cross-references agents/ (producers) and templates/ (consumers) correctly

**Checkpoint**: Schemas verified — downstream features (F-002 through F-010) can build against stable contracts. US4 independently verifiable.

---

## Phase 7: User Story 5 — Example Inputs for Validation (Priority: P2)

**Goal**: 3 self-contained examples (ASCII, Mermaid, free-text) each with input.md and threats.md demonstrating the interface contract and output template.

**Independent Test**: Open each example directory, verify input.md is valid in the stated format, and threats.md follows the template with all 7 sections populated.

### Implementation for User Story 5

- [X] T026 [P] [US5] Create examples/ascii-web-api/input.md — ASCII architecture diagram of a web API with: external user, API gateway (Process), user database (Data Store), authentication service (Process), data flows between components, trust boundary between external and internal zones using dashed-line notation
- [X] T027 [P] [US5] Create examples/mermaid-agentic-app/input.md — Mermaid flowchart diagram of an agentic AI application with: user (External Entity), LLM agent orchestrator (Process), tool server / MCP server (Process), knowledge base (Data Store), external API (External Entity), subgraph trust boundaries, demonstrating both LLM and AG dispatch triggers
- [X] T028 [P] [US5] Create examples/free-text-microservice/input.md — free-text prose description of a microservice architecture with: API gateway, order service, payment service, inventory database, message queue, external payment provider, trust boundaries described in narrative form
- [X] T029 [US5] Create examples/ascii-web-api/threats.md — expected output following templates/threats.md structure with all 7 sections populated using realistic example findings for the ASCII web API architecture (at least 1 finding per STRIDE category, at least 1 AG and 1 LLM finding if applicable, coverage matrix, risk summary, recommended actions)
- [X] T030 [US5] Create examples/mermaid-agentic-app/threats.md — expected output following templates/threats.md structure with all 7 sections populated using realistic findings for the agentic app (emphasis on AI threat tables — AG findings for agent-autonomy/tool-abuse, LLM findings for prompt-injection/data-poisoning/model-theft, plus STRIDE findings)
- [X] T031 [US5] Create examples/free-text-microservice/threats.md — expected output following templates/threats.md structure with all 7 sections populated using realistic findings for the microservice architecture (emphasis on traditional STRIDE findings for distributed systems)

**Checkpoint**: Examples complete — developers can validate the interface contract and output template against concrete scenarios. US5 independently verifiable.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Root file updates and cross-reference validation across all deliverables.

- [X] T032 Update root README.md — add quickstart section pointing to docs/INTERFACE-CONTRACT.md for integration, link to templates/threats.md for output format, link to schemas/ for machine-readable contracts, and link to examples/ for sample inputs
- [X] T033 Run cross-reference validation — verify: all 9 paths in adapters/ContextLoading.yaml resolve to existing files, all agent files reference schemas/finding.yaml in frontmatter, INTERFACE-CONTRACT.md references to templates/threats.md and schemas/output.yaml resolve, schemas/README.md references to agents/ and templates/ resolve, example threats.md files follow the template structure, every top-level directory (agents/, adapters/, templates/, schemas/, examples/) contains a README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (schemas/ directory must exist) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 (agent files reference schemas/finding.yaml)
- **US2 (Phase 4)**: Depends on Phase 2 (interface contract references schemas/)
- **US3 (Phase 5)**: Depends on Phase 2 (template references schemas/output.yaml)
- **US4 (Phase 6)**: Depends on Phase 2 + Phase 5 (verify schemas match template)
- **US5 (Phase 7)**: Depends on Phases 3, 4, 5 (examples reference agents, interface contract, and template)
- **Polish (Phase 8)**: Depends on all preceding phases

### User Story Dependencies

- **US1 (P1)**: Independent after Foundational — 13 parallel agent file tasks
- **US2 (P1)**: Independent after Foundational — 1 large task
- **US3 (P1)**: Independent after Foundational — 1 large task
- **US4 (P2)**: Depends on Foundational + US3 (verify schemas match template)
- **US5 (P2)**: Depends on US1 + US2 + US3 (examples must reference completed artifacts)

### Parallel Opportunities

**Wave 1** (Phase 1): T001, T002 in parallel
**Wave 2** (Phase 2): T003-T009 all in parallel (7 independent files)
**Wave 3** (Phases 3-5): US1 (T010-T022, 13 parallel tasks), US2 (T023), US3 (T024) — all three stories can run in parallel
**Wave 4** (Phase 6): T025 (schema verification)
**Wave 5** (Phase 7): T026-T028 input files in parallel, then T029-T031 output files
**Wave 6** (Phase 8): T032, T033 sequentially

---

## Parallel Example: Wave 3 (Maximum Parallelism)

```
# All 15 tasks can run simultaneously across 3 user stories:

# US1: 13 agent file tasks (all [P])
T010: agents/stride/spoofing.md
T011: agents/stride/tampering.md
T012: agents/stride/repudiation.md
T013: agents/stride/info-disclosure.md
T014: agents/stride/denial-of-service.md
T015: agents/stride/privilege-escalation.md
T016: agents/ai/prompt-injection.md
T017: agents/ai/tool-abuse.md
T018: agents/ai/data-poisoning.md
T019: agents/ai/model-theft.md
T020: agents/ai/agent-autonomy.md
T021: agents/ai/README.md update
T022: agents/orchestrator.md

# US2: 1 large task
T023: docs/INTERFACE-CONTRACT.md

# US3: 1 large task
T024: templates/threats.md
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1: Setup (2 tasks)
2. Complete Phase 2: Foundational (7 tasks, all parallel)
3. Complete Phases 3-5: US1 + US2 + US3 in parallel (15 tasks)
4. **STOP AND VALIDATE**: Repository navigable, interface contract readable, output template complete
5. This delivers the three P1 user stories — the minimum viable foundation

### Incremental Delivery

1. Setup + Foundational → Contracts established
2. US1 (agent files) + US2 (interface contract) + US3 (output template) → Core foundation complete (MVP)
3. US4 (schema verification) → Downstream confidence
4. US5 (examples) → Validation layer
5. Polish → Cross-reference integrity

### Task Summary

| Phase | Tasks | Parallel | User Story |
|-------|-------|----------|------------|
| Setup | 2 | 2 | — |
| Foundational | 7 | 7 | — |
| US1 | 13 | 13 | Navigable Repo (P1) |
| US2 | 1 | — | Interface Contract (P1) |
| US3 | 1 | — | Output Template (P1) |
| US4 | 1 | — | Schemas (P2) |
| US5 | 6 | 3 | Examples (P2) |
| Polish | 2 | — | — |
| **Total** | **33** | **25** | |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- All deliverables are markdown + YAML — no runtime code
- Agent prompt files follow standard frontmatter format from plan.md Component 1
- Knowledge system naming: PascalCase for directories/config, kebab-case for agent files
- Commit after each wave or logical group
- Stop at any checkpoint to validate story independently
