---
prd_reference: docs/product/02_PRD/029-agent-refactoring-right-size-2026-03-25.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-25
    status: APPROVED
    notes: "Faithful decomposition of PRD 029. All 4 user stories covered with traceable acceptance scenarios. All 3 PRD functional requirements decomposed into 15 granular spec requirements. Success criteria match 1:1 with PRD metrics. No scope creep. Non-blocking observation: spec re-prioritizes stories from uniform P0 to P1/P2 execution ordering — compatible with PRD 4-wave timeline."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Agent Refactoring — Right-Size Orchestrator, Report, and Infographic Agents

**Feature Branch**: `029-agent-refactoring-right`
**Created**: 2026-03-25
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/029-agent-refactoring-right-size-2026-03-25.md`
**Research**: `specs/029-agent-refactoring-right/research.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Orchestrator Right-Sizing (Priority: P1)

A threat model user runs `/threat-model` on an architecture description. The orchestrator agent processes the analysis with its always-loaded context reduced to ~1,100-1,200 lines (from 2,085), with consultation-only content — SARIF generation specification, validation checklist, and error templates — loaded on-demand from reference documents at the specific pipeline phases where they are needed.

**Why this priority**: The orchestrator is the largest agent at 2,085 lines (~28K tokens), 2x the Claude Code production benchmark. It has the highest risk of instruction-following degradation from the "lost in the middle" effect. Reducing its always-loaded context addresses the single biggest quality risk in the pipeline.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` before and after refactoring. Compare output structure: finding count, risk distribution, SARIF result count, section presence. Output must be structurally equivalent.

**Acceptance Scenarios**:

1. **Given** the orchestrator agent file, **When** its line count is measured, **Then** it contains ~1,100-1,200 lines (reduced from 2,085)
2. **Given** SARIF generation specification content (~490 lines), **When** Phase 4 of the pipeline completes, **Then** the orchestrator loads it from `adapters/claude-code/agents/references/sarif-generation.md` on-demand
3. **Given** the validation checklist (~80 lines), **When** the pipeline reaches its final validation step, **Then** the orchestrator loads it from `adapters/claude-code/agents/references/validation-checklist.md` on-demand
4. **Given** pure error template content (~100 lines), **When** an error occurs during pipeline execution, **Then** the orchestrator loads it from `adapters/claude-code/agents/references/error-templates.md` on-demand
5. **Given** defensive specification content (~128 lines: DFD classification rules, non-conforming finding handler, three-state cell model), **When** the orchestrator executes normal pipeline phases, **Then** this content remains in the core agent file (not extracted to the error-only reference)
6. **Given** verbose, redundant prose (~200 lines), **When** reviewed during refactoring, **Then** it has been condensed or removed without loss of specification content

---

### User Story 2 — Report Agent Right-Sizing (Priority: P2)

A threat model user generates a narrative threat report with attack trees. The report agent follows its instructions with high fidelity because its always-loaded context has been reduced to ~300-400 lines (from 801), with output templates, Mermaid attack tree examples, and verbose formatting instructions extracted to reference documents.

**Why this priority**: The report agent at 801 lines is 2.7x over the best-practices ceiling. While smaller than the orchestrator, it still carries significant consultation-only content that can be loaded on-demand during report generation.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` and verify the narrative report section has equivalent structure: executive summary present, attack trees rendered, finding details complete, remediation roadmap included.

**Acceptance Scenarios**:

1. **Given** the threat-report agent file, **When** its line count is measured, **Then** it contains ~300-400 lines (reduced from 801)
2. **Given** output format templates and verbose examples, **When** identified during capability inventory, **Then** they are extracted to `adapters/claude-code/agents/references/report-templates.md`
3. **Given** the report agent loading instructions, **When** report generation begins, **Then** the agent loads its reference documents on-demand at the appropriate generation phase

---

### User Story 3 — Infographic Agent Right-Sizing (Priority: P2)

A threat model user generates threat model infographics via the Gemini API. The infographic agent follows Gemini API integration instructions accurately because its always-loaded context has been reduced to ~300-400 lines (from 592), with Gemini API specification and error handling content extracted to reference documents.

**Why this priority**: The infographic agent at 592 lines is 2x over the ceiling. Its Gemini API specification and error handling patterns are consultation-only content loaded during specific generation phases. This agent can be refactored in parallel with the report agent (US-2) since they are independent.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` with `GEMINI_API_KEY` set and verify infographic specification is produced with correct structure. Verify graceful degradation when API key is absent.

**Acceptance Scenarios**:

1. **Given** the threat-infographic agent file, **When** its line count is measured, **Then** it contains ~300-400 lines (reduced from 592)
2. **Given** Gemini API specification content, **When** identified during capability inventory, **Then** it is extracted to `adapters/claude-code/agents/references/infographic-gemini-api.md`
3. **Given** infographic-specific error handling content, **When** identified during capability inventory, **Then** it is extracted to `adapters/claude-code/agents/references/infographic-error-handling.md`
4. **Given** the six graceful degradation failure conditions (missing key, rate limit, timeout, content policy, missing input, empty model), **When** the refactoring is complete, **Then** all six conditions are preserved and produce the local spec artifact

---

### User Story 4 — Zero Regression on Threat Agents (Priority: P0)

A tachi developer verifies that the refactoring introduced no changes to the 11 well-sized STRIDE and AI threat agents. These agents are already within the optimal 108-196 line range and must remain byte-identical.

**Why this priority**: P0 because regression in threat agents would undermine the entire threat modeling pipeline. This is a validation gate, not an implementation story — it verifies the refactoring's constraint boundary.

**Independent Test**: Run `git diff` on all 11 threat agent files after refactoring. All must show zero changes.

**Acceptance Scenarios**:

1. **Given** any of the 11 threat agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse), **When** compared before and after refactoring, **Then** the files are byte-identical
2. **Given** the two infographic design templates (`templates/infographic-baseball-card.md`, `templates/infographic-system-architecture.md`), **When** compared before and after refactoring, **Then** the files are byte-identical
3. **Given** all schemas in `schemas/`, **When** compared before and after refactoring, **Then** the files are unchanged

---

### Edge Cases

- What happens when a reference document is missing from the expected path? The agent must fail with a clear error message identifying the missing file, not silently produce incomplete output.
- What happens if a reference document contains corrupted or truncated content? The agent should validate that the loaded content meets minimum expected size or structure before proceeding.
- How does the system handle concurrent threat model runs that both load the same reference documents? No issue — reference documents are read-only files, loaded via the Read tool, with no write contention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each refactored agent MUST include loading instructions specifying which reference document to load, at what pipeline phase, and the file path
- **FR-002**: Reference documents MUST be stored in `adapters/claude-code/agents/references/` directory
- **FR-003**: Each reference document MUST be self-contained with no cross-references to other reference documents
- **FR-004**: Reference documents MUST include minimal frontmatter with `source-agent`, `loaded-at` (pipeline phase), and `extracted-from` (source description)
- **FR-005**: The orchestrator MUST load SARIF generation specification on-demand at Phase 4 completion (not pre-loaded)
- **FR-006**: The orchestrator MUST load validation checklist on-demand at pipeline end (not pre-loaded)
- **FR-007**: The orchestrator MUST load error templates on-demand when an error occurs (not pre-loaded)
- **FR-008**: The orchestrator MUST retain all defensive specification content (DFD classification, non-conforming finding handling, three-state cell model) in its core file
- **FR-009**: If a reference document is missing at load time, the agent MUST fail with a clear error message identifying the expected file path
- **FR-010**: All orchestration logic, phase sequencing, and dispatch rules MUST remain in the core agent files
- **FR-011**: The `/threat-model` command interface MUST remain unchanged — no changes to invocation, parameters, or output formats
- **FR-012**: A preservation-first capability inventory MUST be created and committed before any extraction begins
- **FR-013**: Report agent extraction targets MUST be determined by a detailed content inventory during the Plan phase, since the PRD research provides granular analysis only for the orchestrator
- **FR-014**: Infographic agent extraction targets MUST be determined by a detailed content inventory during the Plan phase
- **FR-015**: Verbose, redundant prose in the orchestrator MUST be condensed or removed — only narration is compressible, never specification content (tables, schemas, algorithms)

### Key Entities

- **Reference Document**: A standalone markdown file containing consultation-only content (specification, templates, checklists) extracted from an agent. Loaded on-demand via Read tool at specific pipeline phases. Located in `adapters/claude-code/agents/references/`.
- **Capability Inventory**: A comprehensive list of all capabilities, workflows, and integration points for each target agent, created before any modifications. Committed as `specs/029-agent-refactoring-right/capability-inventory.md`.
- **Core Agent**: The refactored agent file containing orchestration logic, phase sequencing, dispatch rules, and loading instructions for reference documents. Always loaded as part of the agent prompt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Orchestrator agent reduced to ~1,100-1,200 lines (from 2,085) — verified by `wc -l`
- **SC-002**: Report agent reduced to ~300-400 lines (from 801) — verified by `wc -l`
- **SC-003**: Infographic agent reduced to ~300-400 lines (from 592) — verified by `wc -l`
- **SC-004**: Zero changes to any of the 11 STRIDE/AI threat agents — verified by `git diff`
- **SC-005**: `/threat-model` on `examples/agentic-app/architecture.md` produces structurally equivalent output before and after refactoring (finding count, risk distribution, SARIF result count, section presence)
- **SC-006**: SARIF output validates against SARIF 2.1.0 schema
- **SC-007**: All reference documents are loadable via Read tool and contain the expected content
- **SC-008**: Capability inventory is committed documenting all pre-refactoring capabilities for each target agent

## Assumptions

- The reference-extraction pattern (load via Read tool on-demand) works within the Claude Code agent framework without latency issues
- Line count is a reasonable proxy for prompt token size (approximately 13-14 tokens per line for markdown content)
- The "lost in the middle" effect applies to the current model (Claude Opus 4.6) and reducing always-loaded context improves instruction-following fidelity
- Structural equivalence (finding count, risk distribution, section presence) is a sufficient regression test — exact text matching is not required since LLM output is non-deterministic
- The report and infographic agent content inventories will reveal sufficient extractable content to reach their target line counts during the Plan phase
