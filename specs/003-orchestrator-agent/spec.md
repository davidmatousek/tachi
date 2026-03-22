---
prd_reference: docs/product/02_PRD/003-orchestrator-agent-2026-03-21.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED
    notes: "All 9 PRD functional requirements covered. 36 acceptance scenarios across 6 user stories. Both personas served. All 4 open questions resolved. 2 LOW non-blocking concerns (System Overview table format acceptance scenario, ASCII/free-text example coverage)."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Orchestrator Agent

**Feature Branch**: `003-orchestrator-agent`
**Created**: 2026-03-21
**Status**: Draft
**Input**: PRD 003 - Orchestrator Agent

## User Scenarios & Testing

### User Story 1 - Parse Architecture into Component Inventory (Priority: P1)

A developer provides their system architecture diagram in any supported format. The orchestrator parses the input, detects the format, classifies each component as a DFD element type, identifies trust boundaries, and produces a structured System Overview.

**Why this priority**: Parsing is the foundation — without accurate component classification, downstream dispatch and threat analysis are unreliable. This is the entry point of every user interaction with the orchestrator.

**Independent Test**: Provide the `examples/mermaid-agentic-app/input.md` diagram and verify the orchestrator produces a System Overview listing all 5 components with correct DFD element types and trust boundary identification.

**Acceptance Scenarios**:

1. **Given** an architecture input with `format: auto`, **When** the orchestrator processes the input, **Then** it detects the correct format using the heuristic priority order defined in `docs/INTERFACE-CONTRACT.md` Section 1 (ASCII first, then free-text, Mermaid, PlantUML, C4)
2. **Given** an architecture input with an explicit `format:` value, **When** the orchestrator processes the input, **Then** it uses the specified format parser without heuristic detection
3. **Given** a valid architecture input, **When** parsing completes, **Then** the orchestrator produces a component inventory listing component name, DFD element type (External Entity, Process, Data Store, or Data Flow), and description for each identified component
4. **Given** the mermaid-agentic-app example input, **When** the orchestrator classifies components, **Then** it assigns: User → External Entity, LLM Agent Orchestrator → Process, MCP Tool Server → Process, Knowledge Base → Data Store, External API → External Entity
5. **Given** a parsed architecture, **When** the orchestrator identifies trust boundaries, **Then** it documents trust zones and boundary crossings in the format defined by `templates/threats.md` Section 2
6. **Given** an input containing fewer than 1 component or 0 data flows, **When** the orchestrator attempts parsing, **Then** it returns the `NO_COMPONENTS` error defined in `docs/INTERFACE-CONTRACT.md` Section 7
7. **Given** an input where `format: auto` fails to match any recognition pattern, **When** the orchestrator attempts parsing, **Then** it returns the `UNSUPPORTED_FORMAT` error

---

### User Story 2 - Dispatch to Correct Threat Agents (Priority: P1)

After parsing the architecture, the orchestrator dispatches each component to the correct threat agents based on its DFD element type (STRIDE-per-Element) and AI keyword matches. Each agent receives the full architecture context for cross-component threat analysis.

**Why this priority**: Correct dispatch is the core differentiator — it encapsulates the STRIDE-per-Element methodology and AI-specific threat awareness so developers do not need to learn these frameworks themselves.

**Independent Test**: Parse the mermaid-agentic-app example input and verify that "LLM Agent Orchestrator" triggers dual-dispatch (all 6 STRIDE + LLM + AG agents), "MCP Tool Server" triggers STRIDE + AG agents, and "User" triggers only S and R agents.

**Acceptance Scenarios**:

1. **Given** a component classified as an External Entity, **When** the orchestrator determines dispatch targets, **Then** it dispatches to Spoofing (S) and Repudiation (R) agents only, per the STRIDE-per-Element normalization table
2. **Given** a component classified as a Process, **When** the orchestrator determines dispatch targets, **Then** it dispatches to all 6 STRIDE agents (S, T, R, I, D, E)
3. **Given** a component classified as a Data Store, **When** the orchestrator determines dispatch targets, **Then** it dispatches to Tampering (T), Information Disclosure (I), and Denial of Service (D) agents only
4. **Given** a component classified as a Data Flow, **When** the orchestrator determines dispatch targets, **Then** it dispatches to Tampering (T), Information Disclosure (I), and Denial of Service (D) agents only
5. **Given** a component whose name or description contains keywords "LLM", "model", "GPT", or "Claude" (case-insensitive), **When** the orchestrator determines dispatch targets, **Then** it additionally dispatches to LLM threat agents (prompt-injection, data-poisoning, model-theft)
6. **Given** a component whose name or description contains keywords "agent", "autonomous", "orchestrator", "MCP server", "tool server", or "plugin" (case-insensitive), **When** the orchestrator determines dispatch targets, **Then** it additionally dispatches to AG threat agents (agent-autonomy, tool-abuse)
7. **Given** a component matching both LLM and AG keywords (e.g., "LLM Agent Orchestrator"), **When** the orchestrator determines dispatch targets, **Then** it dispatches to both LLM and AG agent categories in addition to applicable STRIDE categories (dual-dispatch)
8. **Given** all dispatch targets determined, **When** the orchestrator dispatches to agents, **Then** it sends each agent the full parsed architecture context (all components, data flows, trust boundaries), not just the individual component

---

### User Story 3 - Assemble Findings into Structured Threat Model (Priority: P1)

After all dispatched agents return their findings, the orchestrator assembles them into a single `threats.md` document conforming to the output template with all 7 required sections, validated frontmatter, and correct risk level computations.

**Why this priority**: The assembled output is the deliverable the user receives. Structural completeness and schema conformance are what make the threat model actionable and consumable by downstream tools (SARIF export, narrative reports).

**Independent Test**: Collect findings from dispatched agents for the mermaid-agentic-app example and verify the assembled threats.md contains all 7 sections, valid frontmatter, correct STRIDE and AI table groupings, and a coverage matrix matching the expected dispatch targets.

**Acceptance Scenarios**:

1. **Given** findings from all dispatched agents, **When** the orchestrator assembles the output, **Then** it produces a `threats.md` with YAML frontmatter containing `schema_version: "1.0"`, `date` (ISO 8601), `input_format` (detected or declared format), and `classification: "confidential"`
2. **Given** collected findings, **When** the orchestrator assembles STRIDE tables, **Then** it produces 6 tables (one per STRIDE category) with finding rows conforming to the field definitions in `templates/threats.md` Section 3 (ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation)
3. **Given** collected findings, **When** the orchestrator assembles AI threat tables, **Then** it groups findings from agent-autonomy and tool-abuse under the AG table, and findings from prompt-injection, data-poisoning, and model-theft under the LLM table
4. **Given** all findings assembled, **When** the orchestrator generates the coverage matrix, **Then** it produces a cross-reference table with components as rows and threat categories (S, T, R, I, D, E, AG, LLM) as columns, with finding counts per cell
5. **Given** all findings assembled, **When** the orchestrator generates the risk summary, **Then** it counts findings per risk level (Critical, High, Medium, Low, Note) with percentages
6. **Given** all findings assembled, **When** the orchestrator generates the recommended actions list, **Then** findings are sorted by risk level descending (Critical first, Note last)
7. **Given** any finding returned by an agent, **When** the orchestrator validates the finding, **Then** it verifies the risk_level matches the OWASP 3x3 matrix computation (likelihood x impact) defined in `schemas/finding.yaml`
8. **Given** all 7 required output sections assembled, **When** the orchestrator finalizes the output, **Then** the complete document conforms to the structure defined in `schemas/output.yaml`

---

### User Story 4 - Handle Errors Gracefully (Priority: P2)

When the orchestrator encounters invalid input, ambiguous classifications, or non-conforming agent output, it handles errors predictably and provides actionable guidance to the user.

**Why this priority**: Error handling ensures reliability and determinism — critical for the Security Integrator persona who needs predictable behavior in automated pipelines.

**Independent Test**: Provide invalid inputs (empty content, unrecognized format, ambiguous components) and verify the orchestrator returns correct error codes with actionable messages.

**Acceptance Scenarios**:

1. **Given** an input with `format: auto` where detection fails, **When** the orchestrator processes it, **Then** it returns the `UNSUPPORTED_FORMAT` error listing supported formats with guidance
2. **Given** an input in a recognized format but with no identifiable components, **When** the orchestrator processes it, **Then** it returns the `NO_COMPONENTS` error stating minimum requirements (1 component, 1 data flow)
3. **Given** an input with `format` set to an invalid value, **When** the orchestrator processes it, **Then** it returns the `INVALID_FORMAT_VALUE` error listing allowed values
4. **Given** a component that cannot be confidently classified as a DFD element type, **When** the orchestrator classifies it, **Then** it defaults to Process (broadest coverage — all 6 STRIDE categories) and flags the classification for human review
5. **Given** ambiguous AI keyword matching (e.g., "model" referring to a data model), **When** the orchestrator determines dispatch, **Then** it includes the AI dispatch and notes the ambiguity in the output
6. **Given** an agent returns a finding that does not conform to `schemas/finding.yaml`, **When** the orchestrator collects it, **Then** it flags the non-conforming finding for review rather than silently dropping it
7. **Given** an agent returns zero findings for a component-category pair, **When** the orchestrator assembles the coverage matrix, **Then** the corresponding cell shows `-` (analyzed, no threats found)

---

### User Story 5 - Support Both Dispatch Modes (Priority: P2)

The orchestrator documents both parallel and sequential dispatch protocols so it can be used with any LLM platform, from concurrent agent frameworks to single-prompt manual execution.

**Why this priority**: Platform neutrality is a core constraint — the orchestrator must work with any agentic coding tool. Documenting both modes enables F-009 platform adapters to implement the correct invocation pattern.

**Independent Test**: Verify the orchestrator prompt includes clear instructions for both parallel (concurrent agent) and sequential (one-at-a-time) dispatch, and that the output is identical regardless of mode used.

**Acceptance Scenarios**:

1. **Given** a platform supporting concurrent agent execution, **When** the orchestrator dispatches, **Then** the prompt includes instructions for parallel invocation where all applicable agents run concurrently with results collected before assembly
2. **Given** a platform limited to sequential execution, **When** the orchestrator dispatches, **Then** the prompt includes instructions for sequential invocation in category order (S, T, R, I, D, E, AG, LLM)
3. **Given** either dispatch mode, **When** the orchestrator assembles findings, **Then** the assembled output is structurally identical regardless of dispatch mode used

---

### User Story 6 - Enforce Input Sanitization Boundary (Priority: P2)

The orchestrator treats architecture input as data to be parsed, not as instructions to be followed, maintaining a clear boundary between orchestrator instructions and user-provided content.

**Why this priority**: Threat models contain security-sensitive architectural analysis. The orchestrator must not be susceptible to prompt injection via crafted architecture inputs.

**Independent Test**: Provide an architecture input containing instruction-like content (e.g., "ignore previous instructions") and verify the orchestrator treats it as data and produces a valid threat model.

**Acceptance Scenarios**:

1. **Given** the orchestrator prompt, **When** architecture input is introduced, **Then** it is injected into a clearly marked section separated from orchestrator instructions
2. **Given** architecture input containing instruction-like text, **When** the orchestrator processes it, **Then** it treats the content as data to be parsed and constrains output to the output template structure
3. **Given** a completed threat model, **When** the output is assembled, **Then** all generated outputs include `classification: "confidential"` in frontmatter

---

### Edge Cases

- What happens when a component name matches both LLM and AG keywords AND is classified as an External Entity? STRIDE dispatch follows DFD type (S, R only) plus both LLM and AG dispatch. AI dispatch is additive to STRIDE.
- How does the orchestrator handle Mermaid `sequenceDiagram` input where participants represent interactions rather than components? Treat sequence diagram participants as components, classify based on role, flag for human review if ambiguous.
- What happens when a component name contains a keyword substring (e.g., "ModelValidator" contains "model")? Case-insensitive keyword matching applies — dispatch AI agents and note potential ambiguity.
- How does the orchestrator handle architectures with no trust boundaries defined? Trust Boundaries section contains headers with no data rows; coverage analysis proceeds without trust context.
- What happens when a finding's risk_level does not match the OWASP 3x3 matrix computation? Orchestrator corrects the risk_level to match the matrix and notes the correction.

## Requirements

### Functional Requirements

- **FR-001**: The orchestrator MUST implement the OWASP four-step threat modeling process (Scope, Determine Threats, Determine Countermeasures, Assess) as sequential phases within a single prompt execution
- **FR-002**: The orchestrator MUST detect input format using the heuristic priority order from `docs/INTERFACE-CONTRACT.md` Section 1 when `format: auto` is specified, or use the explicitly declared format value
- **FR-003**: The orchestrator MUST extract components from the architecture input and classify each as a DFD element type (External Entity, Process, Data Store, or Data Flow) based on its role in the system
- **FR-004**: The orchestrator MUST identify trust boundaries including trust zones and boundary crossings using format-specific notation
- **FR-005**: The orchestrator MUST apply the STRIDE-per-Element normalization table from `docs/INTERFACE-CONTRACT.md` Section 2 to determine applicable threat categories per component
- **FR-006**: The orchestrator MUST apply AI dispatch rules from `docs/INTERFACE-CONTRACT.md` Section 3 using case-insensitive keyword matching on component names and descriptions
- **FR-007**: The orchestrator MUST support dual-dispatch when a component matches both LLM and AG keyword categories
- **FR-008**: The orchestrator MUST send each dispatched agent the full parsed architecture context (all components, data flows, trust boundaries), not just the individual target component
- **FR-009**: The orchestrator MUST document both parallel and sequential dispatch protocols
- **FR-010**: The orchestrator MUST collect findings from all dispatched agents and validate each finding's risk_level against the OWASP 3x3 matrix
- **FR-011**: The orchestrator MUST assemble 6 STRIDE tables (one per category) and 2 AI threat tables (AG and LLM) using the 5-agent-to-2-table mapping
- **FR-012**: The orchestrator MUST generate a coverage matrix, risk summary, and recommended actions list from all assembled findings
- **FR-013**: The orchestrator MUST produce a complete `threats.md` with all 7 required sections conforming to `templates/threats.md` and `schemas/output.yaml`
- **FR-014**: The orchestrator MUST include valid YAML frontmatter with `schema_version: "1.0"`, `date`, `input_format`, and `classification: "confidential"`
- **FR-015**: The orchestrator MUST handle all 3 error conditions defined in `docs/INTERFACE-CONTRACT.md` Section 7 (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE)
- **FR-016**: The orchestrator MUST enforce input sanitization by treating architecture input as data with clear boundary markers separating orchestrator instructions from user content
- **FR-017**: The orchestrator MUST default ambiguous component classifications to Process (broadest STRIDE coverage) and flag the classification for human review
- **FR-018**: The orchestrator MUST produce a valid, structurally complete threats.md even when agents return zero findings (empty tables with headers preserved)

### Key Entities

- **Architecture Input**: The user-provided system diagram in any of 5 supported formats, containing components, data flows, and optionally trust boundaries
- **Component Inventory**: Parsed list of system elements, each classified with a DFD element type, name, and description
- **Dispatch Target Map**: The computed mapping of each component to its applicable threat agents (STRIDE + AI), determined by DFD type and keyword matching
- **Finding**: An individual threat identified by an agent, conforming to the 10-field IR schema (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type)
- **Threat Model Output**: The assembled `threats.md` document containing all 7 sections with validated structure and frontmatter

## Success Criteria

### Measurable Outcomes

- **SC-001**: The orchestrator correctly detects the input format for all 3 example inputs in `examples/` (ASCII, Mermaid, free-text)
- **SC-002**: All 5 components in the mermaid-agentic-app example are classified with correct DFD element types (User → External Entity, LLM Agent Orchestrator → Process, MCP Tool Server → Process, Knowledge Base → Data Store, External API → External Entity)
- **SC-003**: STRIDE-per-Element dispatch produces the correct applicable categories for each DFD element type per the normalization table (e.g., External Entity gets S, R only; Process gets all 6)
- **SC-004**: AI dispatch triggers correctly: "LLM Agent Orchestrator" triggers both LLM and AG agents (dual-dispatch); "MCP Tool Server" triggers AG agents; "User", "Knowledge Base", and "External API" trigger no AI agents
- **SC-005**: Assembled output conforms to `templates/threats.md` structure with all 7 required sections present and correctly ordered
- **SC-006**: Output frontmatter includes `schema_version: "1.0"` and correct `input_format` value matching the detected or declared format
- **SC-007**: Every finding's risk_level in the output matches the OWASP 3x3 matrix computation from its likelihood and impact values
- **SC-008**: The coverage matrix accurately reflects finding counts per component per threat category, with `-` for analyzed-but-empty cells
- **SC-009**: Error handling returns correct error codes and actionable messages for all 3 defined error conditions
- **SC-010**: The orchestrator prompt contains no platform-specific invocation syntax (Claude Code Task tool calls, Cursor agent references, etc.)

## Scope & Boundaries

### In Scope
- Author `agents/orchestrator.md` replacing the current placeholder with a complete orchestrator prompt
- Implement all four OWASP threat modeling phases in the prompt
- Embed STRIDE-per-Element normalization table with dispatch logic
- Embed AI extension dispatch rules with keyword matching
- Define agent communication protocol (context sharing, finding collection)
- Document parallel and sequential dispatch modes
- Implement output assembly logic producing a complete threats.md
- Implement input format detection heuristics for all 5 supported formats
- Implement error handling for all 3 error conditions
- Enforce input sanitization boundary

### Out of Scope
- STRIDE agent prompt authoring (existing agents from F-001)
- AI threat agent prompt authoring (existing agents from F-001)
- Finding deduplication and risk rating refinement (F-005)
- Platform-specific dispatch adapters (F-009)
- New input format support beyond the 5 specified formats
- Runtime schema validation scripts

### Assumptions
- The orchestrator is a markdown prompt file, not compiled code — no runtime dependencies
- All 11 threat agent files are available and implemented (verified in codebase research)
- The interface contract, schemas, and output template from F-001 are stable and will not change during implementation
- "Testing" means validation-by-example: invoke with sample inputs and check output against expected structure and dispatch behavior
- The orchestrator must work with any agentic coding tool — platform-specific dispatch is F-009 scope

### Open Questions Resolved
- **Classification confidence**: The orchestrator will flag ambiguous classifications for human review by noting them in the System Overview. A formal confidence field is deferred to F-005.
- **Finding count limits**: No per-component limits imposed at orchestrator level. Output volume is managed by individual agent prompts and by F-005 deduplication.
- **Prompt modularity**: The orchestrator will be a single file (`agents/orchestrator.md`) with clear section headers. Splitting into phased prompts is deferred unless token limits prove problematic.
- **Mermaid sequence diagrams**: Sequence diagram participants will be treated as components and classified based on their role. Ambiguous participants will be flagged for human review.
