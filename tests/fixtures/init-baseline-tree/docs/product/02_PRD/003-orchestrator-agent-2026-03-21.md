---
prd:
  number: "003"
  topic: orchestrator-agent
  created: 2026-03-21
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-21, status: approved, notes: "PRD drafted by PM via ~aod-define skill with full F-001 deliverable context and consumer guide research"}
  architect_signoff: {agent: architect, date: 2026-03-21, status: approved_with_concerns, notes: "Technically feasible. 2 medium concerns (FR-5 agent communication mechanism, component name sanitization) addressable in spec phase. All F-001 artifact references verified on disk."}
  techlead_signoff: {agent: team-lead, date: 2026-03-21, status: approved_with_concerns, notes: "Feasible in 1 sprint. 4-6 hours realistic estimate. 3-wave execution (Draft, Domain Review, Quality Gate). 3 non-blocking concerns for spec phase."}
source:
  idea_id: 3
  story_id: null
---

# Orchestrator Agent - Product Requirements Document

**Status**: Draft
**Created**: 2026-03-21
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 1 (Foundation)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Build the central orchestrator agent prompt that parses architecture input, dispatches to threat agents, and assembles a structured threat model.

### Problem Statement
Developers building agentic AI applications need a single command that takes their system architecture and produces a complete, structured threat model. F-001 delivered the repository skeleton, interface contract, output template, and schemas -- but no agent can yet consume an architecture diagram and produce a threats.md. There is no orchestration logic that ties the 11 threat agent placeholders to the input specification, dispatch rules, and output template. Without the orchestrator, each agent is an isolated prompt with no workflow connecting input to output.

The orchestrator is the central workflow engine that makes tachi usable. It bridges the gap between "here is my architecture" and "here is your threat model."

### Proposed Solution
Author a comprehensive markdown prompt file (`agents/orchestrator.md`) that instructs any LLM to execute the OWASP four-step threat modeling process:

1. **Scope** -- Parse the architecture input (any of the 5 supported formats), classify components as DFD element types, identify trust boundaries, and produce a System Overview
2. **Determine Threats** -- Apply the STRIDE-per-Element normalization table to determine applicable threat categories per component, apply AI dispatch rules for keyword-matched elements, and dispatch to the appropriate threat agents
3. **Determine Countermeasures** -- Collect agent findings (conforming to the IR schema), validate risk levels against the OWASP 3x3 matrix, and assemble findings into the output template sections
4. **Assess** -- Generate the coverage matrix, risk summary, and recommended actions list; validate structural integrity against the output schema

The orchestrator is a **markdown prompt file**, not application code. It instructs the LLM to perform each step, referencing the interface contract, schemas, and templates delivered in F-001. Platform-specific dispatch mechanics (parallel invocation via Claude Code Task tool, Cursor agent calls, etc.) are an adapter concern handled by F-009.

### Success Criteria
- Orchestrator prompt correctly parses the `examples/mermaid-agentic-app/input.md` diagram and classifies all 5 components with correct DFD element types
- STRIDE-per-Element dispatch produces the correct applicable categories for each DFD element type (e.g., External Entity gets S, R only)
- AI dispatch rules trigger correctly: "LLM Agent Orchestrator" triggers both LLM and AG agents; "MCP Tool Server" triggers AG agents; "User", "Knowledge Base", and "External API" trigger no AI agents
- Assembled output conforms to `templates/threats.md` structure with all 7 required sections present
- Output frontmatter includes `schema_version: "1.0"` and correct `input_format` value

### Timeline
Target: 1 development sprint (estimated by Team-Lead during feasibility review)

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

This feature directly enables the core value proposition: "First toolkit to natively model AI-specific threat agents alongside traditional STRIDE." The orchestrator is the execution engine that makes this value proposition real. Without it, the interface contract and output template from F-001 are specifications without a workflow. With it, a developer can provide an architecture diagram and receive a structured threat model -- the fundamental user experience tachi promises.

### Roadmap Fit
**Phase**: Phase 1 (Foundation)
**Dependencies**: F-001 (delivered) -- repository structure, interface contract, output template, schemas
**Blocks**: F-003 (STRIDE Agents), F-004 (AI Agents), F-005 (Dedup & Risk Rating), F-009 (Platform Adapters)

The orchestrator must exist before any threat agent can be useful in context. F-003 and F-004 author the individual agent prompts, but without the orchestrator to dispatch them and assemble their output, those agents cannot produce a complete threat model. F-005 (deduplication and risk rating refinement) operates on findings the orchestrator assembles. F-009 (platform adapters) wraps the orchestrator's dispatch protocol for specific platforms.

---

## Target Users & Personas

### Primary Persona: AI Agent Developer
- **Role**: Software developer building agentic AI applications
- **Experience**: Proficient in code, new to threat modeling methodology
- **Goals**: Provide a system diagram and receive a structured threat model without learning STRIDE methodology, DFD classification, or AI threat taxonomies
- **Pain Points**: Does not know which threats apply to which components; does not know that an "LLM Agent Orchestrator" element needs different threat analysis than a "User Database" element

**Why This Matters**: The orchestrator encapsulates the OWASP threat modeling process and STRIDE-per-Element logic so this developer does not need to learn it. They provide input; the orchestrator handles classification, dispatch, and assembly.

### Secondary Persona: Security Integrator
- **Role**: Security engineer or DevSecOps engineer integrating threat modeling into CI/CD pipelines
- **Experience**: Deep security expertise, expects machine-readable outputs and predictable behavior
- **Goals**: Invoke tachi programmatically and receive consistent, schema-conforming output regardless of input format
- **Pain Points**: Needs the orchestrator to handle format detection and agent dispatch deterministically so automated pipelines produce reliable results

**Why This Matters**: The orchestrator's structured workflow (format detection, element classification, dispatch, assembly) gives this persona deterministic behavior. The same input always produces structurally identical output, enabling reliable pipeline integration.

---

## User Stories

### US-001: Parse Any Supported Architecture Format
**When** I provide my system architecture diagram in any supported format (ASCII, free-text, Mermaid, PlantUML, or C4),
**I want to** have the orchestrator parse it into a structured component inventory with DFD element types and trust boundaries,
**So I can** get a threat model without converting my diagram to a specific format.

**Acceptance Criteria**:
- **Given** an architecture input with `format: auto`, **when** the orchestrator processes the input, **then** it detects the correct format using the heuristic priority order defined in `docs/INTERFACE-CONTRACT.md` Section 1 (ASCII first, then free-text, Mermaid, PlantUML, C4)
- **Given** an architecture input with an explicit `format:` value, **when** the orchestrator processes the input, **then** it uses the specified format parser without heuristic detection
- **Given** a valid architecture input in any supported format, **when** parsing completes, **then** the orchestrator produces a component inventory listing: component name, DFD element type (External Entity, Process, Data Store, or Data Flow), and description for each identified component
- **Given** a parsed architecture, **when** the orchestrator identifies trust boundaries, **then** it documents trust zones and boundary crossings in the format defined by `templates/threats.md` Section 2
- **Given** a parsed architecture, **when** the orchestrator assembles the System Overview, **then** it includes Components, Data Flows, and Technologies tables matching the format defined by `templates/threats.md` Section 1
- **Given** an input containing fewer than 1 component or 0 data flows, **when** the orchestrator attempts parsing, **then** it returns the `NO_COMPONENTS` error defined in `docs/INTERFACE-CONTRACT.md` Section 7
- **Given** an input where `format: auto` fails to match any recognition pattern, **when** the orchestrator attempts parsing, **then** it returns the `UNSUPPORTED_FORMAT` error defined in `docs/INTERFACE-CONTRACT.md` Section 7

**Priority**: P1 | **Effort**: L

### US-002: Dispatch to Threat Agents Using STRIDE-per-Element and AI Dispatch Rules
**When** the orchestrator has parsed my architecture into a component inventory,
**I want to** have it dispatch each component to the correct threat agents based on its DFD element type and AI keyword matches,
**So I can** get comprehensive coverage without manually determining which threats apply to which components.

**Acceptance Criteria**:
- **Given** a component classified as an External Entity, **when** the orchestrator determines dispatch targets, **then** it dispatches to Spoofing (S) and Repudiation (R) agents only, per the STRIDE-per-Element normalization table in `docs/INTERFACE-CONTRACT.md` Section 2
- **Given** a component classified as a Process, **when** the orchestrator determines dispatch targets, **then** it dispatches to all 6 STRIDE agents (S, T, R, I, D, E)
- **Given** a component classified as a Data Store, **when** the orchestrator determines dispatch targets, **then** it dispatches to Tampering (T), Information Disclosure (I), and Denial of Service (D) agents only
- **Given** a component classified as a Data Flow, **when** the orchestrator determines dispatch targets, **then** it dispatches to Tampering (T), Information Disclosure (I), and Denial of Service (D) agents only
- **Given** a component whose name or description contains keywords "LLM", "model", "GPT", or "Claude" (case-insensitive), **when** the orchestrator determines dispatch targets, **then** it additionally dispatches to LLM threat agents (prompt-injection, data-poisoning, model-theft) per `docs/INTERFACE-CONTRACT.md` Section 3
- **Given** a component whose name or description contains keywords "agent", "autonomous", "orchestrator", "MCP server", "tool server", or "plugin" (case-insensitive), **when** the orchestrator determines dispatch targets, **then** it additionally dispatches to AG threat agents (agent-autonomy, tool-abuse) per `docs/INTERFACE-CONTRACT.md` Section 3
- **Given** a component matching keywords from both LLM and AG categories (e.g., "LLM Agent Orchestrator"), **when** the orchestrator determines dispatch targets, **then** it dispatches to both LLM and AG agent categories in addition to applicable STRIDE categories (dual-dispatch)
- **Given** all dispatch targets determined, **when** the orchestrator dispatches to agents, **then** it sends each agent the complete parsed architecture context (not just the individual component) so agents can assess cross-component threats
- **Given** the orchestrator dispatches to agents, **when** dispatch protocol is documented, **then** the prompt includes instructions for both parallel invocation (agent framework with concurrent execution) and sequential invocation (manual one-at-a-time execution), per the consumer guide

**Priority**: P1 | **Effort**: L

### US-003: Assemble Agent Findings into a Structured Threat Model
**When** all dispatched threat agents have returned their findings,
**I want to** have the orchestrator assemble them into a single `threats.md` document conforming to the output template,
**So I can** get a complete, actionable threat model in a consistent format.

**Acceptance Criteria**:
- **Given** findings collected from all dispatched agents, **when** the orchestrator assembles the output, **then** it produces a `threats.md` with YAML frontmatter containing `schema_version: "1.0"`, `date` (ISO 8601), `input_format` (detected or declared format), and `classification: "confidential"`
- **Given** collected findings, **when** the orchestrator assembles STRIDE tables, **then** it produces 6 tables (one per STRIDE category) with finding rows conforming to the field definitions in `templates/threats.md` Section 3 (ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation)
- **Given** collected findings, **when** the orchestrator assembles AI threat tables, **then** it groups findings from agent-autonomy and tool-abuse agents under the AG table, and findings from prompt-injection, data-poisoning, and model-theft agents under the LLM table, per the 5-agent-to-2-table mapping documented in `agents/ai/README.md`
- **Given** all findings assembled, **when** the orchestrator generates the coverage matrix, **then** it produces a cross-reference table with components as rows and threat categories (S, T, R, I, D, E, AG, LLM) as columns, with finding counts per cell matching the format in `templates/threats.md` Section 5
- **Given** all findings assembled, **when** the orchestrator generates the risk summary, **then** it counts findings per risk level (Critical, High, Medium, Low, Note) with percentages, matching the format in `templates/threats.md` Section 6
- **Given** all findings assembled, **when** the orchestrator generates the recommended actions list, **then** findings are sorted by risk level descending (Critical first, Note last), matching the format in `templates/threats.md` Section 7
- **Given** any finding returned by an agent, **when** the orchestrator validates the finding, **then** it verifies the risk_level matches the OWASP 3x3 matrix computation (likelihood x impact) defined in `schemas/finding.yaml`
- **Given** all 7 required output sections assembled, **when** the orchestrator finalizes the output, **then** the complete document conforms to the structure defined in `schemas/output.yaml`

**Priority**: P1 | **Effort**: L

---

## Functional Requirements

### FR-1: OWASP Four-Step Workflow Implementation

The orchestrator prompt MUST implement the OWASP threat modeling process as four sequential phases within a single prompt execution. The prompt instructs the LLM to perform each phase in order, producing intermediate results that feed into subsequent phases.

**Phase 1 -- Scope (Parse and Classify)**:
- Detect input format using the heuristic priority order from `docs/INTERFACE-CONTRACT.md` Section 1, or use the explicitly declared `format:` value
- Extract components from the architecture input and classify each as a DFD element type: External Entity, Process, Data Store, or Data Flow
- Identify trust boundaries (zones and crossings) using the format-specific trust boundary notation documented in the interface contract
- Produce a System Overview (components, data flows, technologies) conforming to `templates/threats.md` Section 1
- Produce a Trust Boundaries section conforming to `templates/threats.md` Section 2

**Phase 2 -- Determine Threats (Dispatch)**:
- For each classified component, apply the STRIDE-per-Element normalization table from `docs/INTERFACE-CONTRACT.md` Section 2 to determine applicable STRIDE categories
- Apply AI dispatch rules from `docs/INTERFACE-CONTRACT.md` Section 3 using case-insensitive keyword matching on component names and descriptions
- Dispatch each component to its applicable agents with the full parsed architecture context
- The orchestrator prompt MUST document both parallel and sequential dispatch protocols

**Phase 3 -- Determine Countermeasures (Collect and Assemble)**:
- Collect findings from all dispatched agents, each conforming to `schemas/finding.yaml`
- Validate each finding's `risk_level` matches the OWASP 3x3 matrix computation from its `likelihood` and `impact` values
- Assemble 6 STRIDE tables (one per category) per `templates/threats.md` Section 3
- Assemble 2 AI threat tables (AG, LLM) per `templates/threats.md` Section 4, applying the 5-agent-to-2-table mapping

**Phase 4 -- Assess (Summarize and Validate)**:
- Generate coverage matrix per `templates/threats.md` Section 5
- Generate risk summary per `templates/threats.md` Section 6
- Generate recommended actions list (sorted by risk level descending) per `templates/threats.md` Section 7
- Validate structural integrity: all 7 required sections present, finding IDs match the pattern `{CATEGORY_PREFIX}-{N}`, frontmatter contains all required fields

### FR-2: Input Format Detection and Parsing

The orchestrator prompt MUST include instructions for format detection and parsing that implement the interface contract specification.

**Format Detection Logic**:
- When `format: auto` (or `format` is absent), attempt heuristic detection in priority order:
  1. ASCII: Look for box-drawing characters (`+--+`, `|`, `[...]`), arrow indicators (`-->`, `<--`, `<-->`)
  2. Free-text: No diagram syntax detected; prose description of components and relationships
  3. Mermaid: Keywords `graph`, `flowchart`, `sequenceDiagram`; node definitions; edge definitions
  4. PlantUML: `@startuml`/`@enduml` delimiters; component declarations; relationship arrows
  5. C4: Keywords `Person`, `System`, `Container`, `Component`; C4 function syntax; `Rel(...)` declarations
- When `format` is explicitly set to a valid value, use that format's parsing rules directly
- When `format` is set to an invalid value, return the `INVALID_FORMAT_VALUE` error per `docs/INTERFACE-CONTRACT.md` Section 7

**Component Extraction**:
- Identify all components (services, databases, users, agents, APIs, etc.) from the input
- Classify each component as a DFD element type based on its role:
  - External Entity: Users, external services, third-party APIs (outside system boundary)
  - Process: Services, applications, agents, orchestrators, gateways (active processing)
  - Data Store: Databases, caches, file systems, knowledge bases (passive storage)
  - Data Flow: Named connections between components (data in transit)
- Extract component names, descriptions, and relationships

**Trust Boundary Identification**:
- Parse trust boundaries using format-specific notation (subgraph, boundary, dashed lines, etc.)
- Classify trust zones with trust level descriptions
- Identify boundary crossings where data flows between zones of different trust levels

### FR-3: STRIDE-per-Element Dispatch Logic

The orchestrator prompt MUST include the complete STRIDE-per-Element normalization table and dispatch logic.

**Normalization Table** (embedded in prompt):

| DFD Element Type | Applicable STRIDE Categories |
|------------------|------------------------------|
| External Entity  | S, R |
| Process          | S, T, R, I, D, E |
| Data Store       | T, I, D |
| Data Flow        | T, I, D |

**Dispatch Behavior**:
- For each component, look up its DFD element type in the normalization table
- Dispatch to the applicable STRIDE agent(s) for that element type
- Each agent receives the full architecture context, not just the individual component, to enable cross-component threat identification
- The prompt MUST NOT invent or extend the normalization table -- it is a fixed contract from F-001

### FR-4: AI Extension Dispatch Logic

The orchestrator prompt MUST include the AI dispatch rules from the interface contract.

**Keyword Matching**:
- LLM keywords: "LLM", "model", "GPT", "Claude" (case-insensitive)
- AG keywords: "agent", "autonomous", "orchestrator", "MCP server", "tool server", "plugin" (case-insensitive)
- Multi-word keywords (e.g., "MCP server", "tool server") match as phrases
- Matching is performed on component names, labels, and descriptions

**Dispatch Rules**:
- LLM keyword match: dispatch to prompt-injection, data-poisoning, model-theft agents
- AG keyword match: dispatch to agent-autonomy, tool-abuse agents
- Dual-dispatch: when a component matches both LLM and AG keywords, both agent categories are dispatched in addition to STRIDE categories
- AI dispatch is additive: STRIDE categories always apply based on DFD element type; AI dispatch adds to (never replaces) STRIDE dispatch

**Deduplication Note**:
- Duplicate findings from overlapping dispatches are resolved at coverage matrix assembly (Phase 4), not at dispatch time
- Each agent produces findings independently; the coverage matrix aggregates unique findings per component per category

### FR-5: Agent Communication Protocol

The orchestrator prompt MUST define how it communicates with threat agents.

**Agent Invocation Context**:
- Each agent receives: the full parsed architecture context (all components, data flows, trust boundaries), not just its target component
- Each agent is told which specific component(s) to analyze for its threat category
- Each agent is instructed to produce findings conforming to `schemas/finding.yaml`

**Dispatch Protocol Documentation**:
The orchestrator prompt MUST include instructions for two invocation modes:
1. **Parallel (agent framework)**: All applicable agents are invoked concurrently; the orchestrator collects all results before proceeding to assembly. This is the recommended mode when the host platform supports concurrent agent execution.
2. **Sequential (manual)**: Agents are invoked one at a time in category order (S, T, R, I, D, E, AG, LLM). This mode works with any LLM that cannot run multiple agents concurrently.

**Agent Output Collection**:
- The orchestrator waits for all dispatched agents to complete before proceeding to assembly
- If an agent produces findings that do not conform to `schemas/finding.yaml`, the orchestrator flags the non-conforming finding for review rather than silently dropping it
- If an agent produces zero findings for a component-category pair, the coverage matrix cell shows `-` (analyzed, no threats found)

### FR-6: Output Assembly and Validation

The orchestrator prompt MUST assemble collected findings into a complete `threats.md` conforming to the output template and schema.

**Frontmatter**:
```yaml
---
schema_version: "1.0"
date: "{ISO 8601 date}"
input_format: "{detected or declared format}"
classification: "confidential"
---
```

**Section Assembly Order** (per `templates/threats.md`):
1. System Overview -- from Phase 1 parsing output
2. Trust Boundaries -- from Phase 1 parsing output
3. STRIDE Tables (6) -- from Phase 3 agent findings, one table per category (S, T, R, I, D, E)
4. AI Threat Tables (2) -- from Phase 3 agent findings, AG table and LLM table
5. Coverage Matrix -- computed from all findings (components x categories)
6. Risk Summary -- computed from all findings (counts per risk level)
7. Recommended Actions -- all findings sorted by risk level descending

**Risk Level Validation**:
- Every finding's `risk_level` MUST match the OWASP 3x3 matrix computation from its `likelihood` and `impact` values
- If a finding's risk_level does not match the matrix, the orchestrator corrects it and notes the correction

**5-Agent-to-2-Table Mapping**:
- Findings from agent-autonomy.md and tool-abuse.md agents are grouped under the AG (Agentic Threats) table with ID prefix `AG-`
- Findings from prompt-injection.md, data-poisoning.md, and model-theft.md agents are grouped under the LLM table with ID prefix `LLM-`

**Output Naming**:
- Output follows the naming convention: `YYYY-MM-DD-{phase}/threats.md`
- Outputs are immutable once generated

### FR-7: Error Handling

The orchestrator prompt MUST handle error conditions defined in `docs/INTERFACE-CONTRACT.md` Section 7.

**Error Conditions**:
1. **UNSUPPORTED_FORMAT**: `format: auto` detection fails, or explicit `format` value is not in the supported enum. Response lists supported formats with guidance.
2. **NO_COMPONENTS**: Input is in a recognized format but contains no identifiable components or no data flows. Response states minimum requirements (1 component, 1 data flow).
3. **INVALID_FORMAT_VALUE**: The `format` field contains a value outside the allowed enum. Response lists allowed values.

**Graceful Degradation**:
- When a component cannot be confidently classified as a DFD element type, classify it as Process (the most broadly threatened type, receiving all 6 STRIDE categories) and flag the classification for human review
- When AI keyword matching is ambiguous (e.g., "model" could refer to a data model rather than an LLM), include the AI dispatch and note the ambiguity in the output

### FR-8: Input Sanitization Boundary

The orchestrator prompt MUST enforce the input sanitization principles from `docs/INTERFACE-CONTRACT.md` Section 6.

**Prompt Boundary Requirements**:
- The orchestrator prompt establishes its role and purpose before any user content is introduced
- Architecture input is injected into a clearly marked section (e.g., `<architecture-input>...</architecture-input>`) separated from orchestrator instructions
- The orchestrator constrains its output to the output template structure -- it does not produce content outside the defined sections
- The orchestrator treats architecture input as data to be parsed, not as instructions to be followed

### FR-9: Stub Agent Compatibility

The orchestrator prompt MUST work with the current agent files delivered in F-001.

**Stub Behavior**:
- The current agent files in `agents/stride/` and `agents/ai/` are placeholders (status: placeholder)
- The orchestrator must produce a valid threats.md even when agents are stubs that return minimal or no findings
- When an agent returns no findings, the corresponding output table section contains the table header with no data rows, and the coverage matrix shows `-` for all cells in that agent's category
- This enables validation of the orchestrator workflow end-to-end before F-003 and F-004 author the full agent prompts

---

## Non-Functional Requirements

### Performance Requirements
Not applicable for F-002. The orchestrator is a markdown prompt file processed by an LLM. Performance depends on the LLM provider and platform, not on orchestrator design. The orchestrator should minimize unnecessary verbosity in prompt instructions to reduce token consumption, but no specific latency or throughput targets apply to the prompt artifact itself.

### Reliability Requirements
- **Deterministic Classification**: The same architecture input MUST produce the same DFD element type classification and agent dispatch targets on every invocation. The STRIDE-per-Element table and AI keyword rules are deterministic; the orchestrator prompt must not introduce non-deterministic classification logic.
- **Structural Completeness**: Every output MUST contain all 7 required sections, even when some sections contain no findings. Empty sections include table headers to maintain structural integrity for downstream consumers (F-006 SARIF, F-007 narrative).
- **Schema Conformance**: Every output MUST include valid YAML frontmatter with all required fields (`schema_version`, `date`, `input_format`, `classification`).

### Security Requirements
- **Input-as-Data Boundary**: Architecture input is treated as data to be parsed. The orchestrator prompt MUST include explicit boundary markers separating orchestrator instructions from user-provided architecture content (per `docs/INTERFACE-CONTRACT.md` Section 6).
- **Output Classification**: All generated outputs include `classification: "confidential"` in frontmatter, as threat models contain security-sensitive architectural analysis.
- **Prompt Supply Chain**: The orchestrator prompt file (`agents/orchestrator.md`) is a security-sensitive artifact. Changes require feature branch and PR review per Constitution Principle IX.
- **No Credentials in Prompt**: Per knowledge-system security rules, the orchestrator prompt contains no API keys, tokens, passwords, or user-specific file paths.

### Technology Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Orchestrator format | Markdown prompt file | Platform-agnostic; works with any LLM backend (Claude, GPT, Gemini, local models); no runtime dependencies |
| Workflow structure | OWASP 4-step process | Industry-standard threat modeling methodology; provides clear phase separation for prompt organization |
| Dispatch logic | Embedded in prompt | Self-contained; no external configuration files needed at invocation time; all rules from interface contract are inlined |
| Platform dispatch | Deferred to F-009 | Platform-specific invocation (Task tool, agent calls, etc.) is an adapter concern; orchestrator defines the protocol, adapters implement it |

---

## Success Metrics

### Primary Metrics
- **Format Detection Accuracy**: Orchestrator correctly identifies the input format for all 3 example inputs (`examples/ascii-web-api/`, `examples/mermaid-agentic-app/`, `examples/free-text-microservice/`)
- **DFD Classification Accuracy**: All 5 components in the mermaid-agentic-app example are classified with correct DFD element types matching the expected dispatch behavior documented in `examples/mermaid-agentic-app/input.md`
- **AI Dispatch Correctness**: Dual-dispatch for "LLM Agent Orchestrator" (LLM + AG) and AG-only dispatch for "MCP Tool Server" match the expected behavior documented in the mermaid example
- **Output Structural Completeness**: Generated threats.md contains all 7 required sections with correct table structures, valid frontmatter, and conforming finding IDs
- **Stub Compatibility**: Orchestrator produces a valid, structurally complete threats.md when dispatching to F-001 stub agents (empty findings are acceptable; structural integrity is required)

### Downstream Enablement
- F-003 (STRIDE Agents) authors can read the orchestrator's dispatch protocol and agent communication format to understand exactly what context their agents receive and what output format they must produce
- F-004 (AI Agents) authors can verify their agent prompt files will be dispatched correctly based on AI keyword matching rules
- F-005 (Dedup & Risk Rating) can operate on the assembled findings in the coverage matrix
- F-009 (Platform Adapters) can implement the parallel and sequential dispatch protocols documented in the orchestrator

---

## Scope & Boundaries

### In Scope (P1 -- This Feature)
- Author `agents/orchestrator.md` replacing the current placeholder with a complete orchestrator prompt
- Implement OWASP four-step threat modeling process in the prompt
- Embed STRIDE-per-Element normalization table with dispatch logic
- Embed AI extension dispatch rules with keyword matching
- Define agent communication protocol (context sharing, finding collection)
- Document parallel and sequential dispatch modes
- Implement output assembly logic producing a complete threats.md
- Implement input format detection heuristics for all 5 supported formats
- Implement error handling for all 3 error conditions from the interface contract
- Enforce input sanitization boundary with prompt markers
- Validate against the 3 existing examples in `examples/`

### Out of Scope (Future Features)
- F-003: STRIDE agent prompt authoring (agents are stubs for F-002 validation)
- F-004: AI threat agent prompt authoring (agents are stubs for F-002 validation)
- F-005: Finding deduplication and risk rating refinement (orchestrator collects raw findings; F-005 refines)
- F-009: Platform-specific dispatch adapters (Claude Code Task tool, Cursor agent calls, etc.)
- Input format parsing implementation (F-002 defines parsing instructions in the prompt; F-005 handles edge cases)
- New input format support beyond the 5 formats specified in the interface contract
- Agent prompt content for VoiceProfile.md, StyleGuide.md, MasterContent/, or Narratives/
- Runtime implementation of output schema validation (structural integrity is checked by the orchestrator prompt, not by a validation script)

### Assumptions
- tachi is a knowledge system (markdown + YAML); the orchestrator is a prompt file, not compiled code
- Any LLM capable of following structured instructions can execute the orchestrator prompt
- The 11 threat agent files (6 STRIDE + 5 AI) exist as placeholders from F-001 and are available for dispatch reference
- The interface contract, schemas, and output template from F-001 are stable and will not change during F-002 implementation
- "Testing" means validation-by-example: the orchestrator is invoked with sample inputs and the output is checked against the expected structure and dispatch behavior
- The orchestrator must work with any agentic coding tool (Claude Code, Cursor, Copilot, Windsurf, custom pipelines) -- platform-specific dispatch is an adapter concern (F-009)

### Constraints
- **No Runtime Dependencies**: The orchestrator is a markdown file. No scripts, no compiled code, no package dependencies.
- **Interface Contract Compliance**: All dispatch logic MUST match the rules in `docs/INTERFACE-CONTRACT.md`. The orchestrator cannot extend or modify the normalization table, AI keywords, or format specifications.
- **Output Template Compliance**: All assembled output MUST conform to `templates/threats.md`. The orchestrator cannot add, remove, or reorder sections.
- **Schema Compliance**: All findings MUST conform to `schemas/finding.yaml`. All output MUST conform to `schemas/output.yaml`.
- **Platform Neutrality**: The orchestrator prompt MUST NOT contain platform-specific invocation syntax (e.g., Claude Code Task tool calls, Cursor agent references). Platform adaptation is F-009's responsibility.

---

## Risks & Dependencies

### Technical Risks

**Risk 1: DFD Element Type Classification Ambiguity** (HIGH)
- **Likelihood**: High (architecture diagrams vary widely in naming conventions; "Gateway" could be Process or Data Flow depending on context)
- **Impact**: Medium (incorrect classification dispatches wrong threat agents, producing incomplete coverage)
- **Mitigation**: Define clear classification heuristics in the prompt with examples for each DFD type; default ambiguous components to Process (broadest coverage); flag ambiguous classifications for human review in the output
- **Contingency**: F-005 can add a reclassification review step

**Risk 2: AI Keyword False Positives** (MEDIUM)
- **Likelihood**: Medium ("model" could refer to a data model, not an LLM; "agent" could refer to a human agent, not an AI agent)
- **Impact**: Low (extra AI dispatch adds findings that may not apply, but does not miss threats)
- **Mitigation**: Document known ambiguous keywords in the orchestrator prompt; dispatch broadly and rely on F-005 deduplication to filter irrelevant findings; note ambiguity in output
- **Contingency**: Add context-aware keyword disambiguation rules in a future iteration

**Risk 3: Prompt Token Limits** (MEDIUM)
- **Likelihood**: Medium (embedding the full STRIDE-per-Element table, AI dispatch rules, error handling, and assembly instructions in a single prompt creates a large prompt file)
- **Impact**: Medium (LLMs with smaller context windows may truncate the orchestrator instructions)
- **Mitigation**: Structure the prompt with clear section headers so it can be loaded incrementally if needed; keep instructions concise without sacrificing completeness; defer verbose examples to referenced files
- **Contingency**: Split the orchestrator into phased prompts (parse, dispatch, assemble) if token limits prove problematic

**Risk 4: Free-Text Parsing Unreliability** (MEDIUM)
- **Likelihood**: Medium (free-text has no syntactic markers; component extraction depends entirely on LLM comprehension)
- **Impact**: Medium (missed components mean incomplete threat coverage)
- **Mitigation**: Provide detailed parsing guidance with examples in the prompt; require the orchestrator to list all extracted components before proceeding to dispatch so the user can verify completeness
- **Contingency**: Recommend explicit format declaration for complex architectures; add structured free-text conventions in a future iteration

### Dependencies

**Internal Dependencies**:

| Dependency | Feature | Status | Impact if Unavailable |
|------------|---------|--------|----------------------|
| Repository structure | F-001 | Delivered | Cannot reference file paths |
| Interface contract | F-001 | Delivered | Cannot implement dispatch rules |
| Output template | F-001 | Delivered | Cannot assemble output |
| Schemas (finding, input, output) | F-001 | Delivered | Cannot validate findings or output |
| Example inputs | F-001 | Delivered | Cannot validate orchestrator behavior |
| Stub agent files | F-001 | Delivered | Cannot test dispatch protocol |

**External Dependencies**:
- OWASP Threat Modeling Process (stable, well-established four-step methodology)
- Microsoft STRIDE-per-Element (stable, MSDN 2006)
- OWASP LLM Top 10 v2025 (published, stable)
- OWASP Agentic Top 10 2026 (draft, may evolve -- affects AI keyword list)
- OWASP MCP Top 10 v0.1 Beta (early draft, may change -- affects AI keyword list)

**Dependency Graph**:
```
F-001 (Delivered)
  └─ F-002 (This Feature)
       ├─ Blocks: F-003 (STRIDE Agents)
       ├─ Blocks: F-004 (AI Agents)
       ├─ Blocks: F-005 (Dedup & Risk Rating)
       └─ Blocks: F-009 (Platform Adapters)
```

---

## Open Questions

- [ ] **Ambiguous component classification**: Should the orchestrator include a "classification confidence" field in the System Overview to flag uncertain DFD type assignments? -- Owner: Architect -- Due: Spec phase -- Status: Open
- [ ] **Agent finding count limits**: Should the orchestrator instruct agents to limit findings per component (e.g., top 3 per category) to prevent output bloat for complex architectures? -- Owner: PM -- Due: Spec phase -- Status: Open
- [ ] **Prompt modularity**: Should the orchestrator prompt be a single monolithic file or split into sections that can be loaded incrementally (e.g., parse-section.md, dispatch-section.md, assemble-section.md)? -- Owner: Architect -- Due: Spec phase -- Status: Open
- [ ] **Mermaid sequence diagrams**: The interface contract lists `sequenceDiagram` as a Mermaid recognition pattern, but sequence diagrams model interactions rather than components. Should the orchestrator treat sequence diagram participants as components? -- Owner: Architect -- Due: Spec phase -- Status: Open

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- Consumer Guide: [CONSUMER_GUIDE_TACHI.md](docs/guides/CONSUMER_GUIDE_TACHI.md) (F-002 section)
- Research Guide: [CONSUMER_GUIDE_TACHI_RESEARCH.md](docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md) (sections 1, 11, 12)
- F-001 PRD: [001-project-skeleton-interface-contract-2026-03-21.md](docs/product/02_PRD/001-project-skeleton-interface-contract-2026-03-21.md)

### Technical Documentation
- Interface Contract: [INTERFACE-CONTRACT.md](docs/INTERFACE-CONTRACT.md)
- Output Template: [threats.md](templates/threats.md)
- Finding IR Schema: [finding.yaml](schemas/finding.yaml)
- Input Schema: [input.yaml](schemas/input.yaml)
- Output Schema: [output.yaml](schemas/output.yaml)
- AI Agent Taxonomy: [agents/ai/README.md](agents/ai/README.md)
- Mermaid Example (validation input): [examples/mermaid-agentic-app/input.md](examples/mermaid-agentic-app/input.md)
- Constitution: [constitution.md](.aod/memory/constitution.md)

### External Resources
- OWASP Threat Modeling Process (four-step methodology: Scope, Determine Threats, Determine Countermeasures, Assess)
- Microsoft STRIDE: Kohnfelder & Garg (1999)
- STRIDE-per-Element: MSDN Magazine (November 2006)
- OWASP Risk Rating Methodology (3x3 matrix)
- OWASP LLM Top 10 v2025
- OWASP Agentic Top 10 (2026 draft)
- OWASP MCP Top 10 v0.1 Beta

---

## Definition of Done

Per Constitution Principle VII:
1. **Pushed to Production**: `agents/orchestrator.md` committed to feature branch and merged via PR, replacing the F-001 placeholder
2. **Tested**: Orchestrator successfully parses the `examples/mermaid-agentic-app/input.md` diagram, dispatches to stub agents with correct STRIDE-per-Element and AI dispatch targets, and assembles a valid threats.md matching the output template with all 7 required sections, valid frontmatter, and conforming finding IDs
3. **User Validated**: A developer can provide the mermaid example input and receive a structurally valid threats.md; the System Overview correctly lists all 5 components with accurate DFD types; the dispatch log shows correct agent targets per the expected dispatch behavior documented in the example

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-21 | product-manager | Initial PRD for F-002 Orchestrator Agent |
