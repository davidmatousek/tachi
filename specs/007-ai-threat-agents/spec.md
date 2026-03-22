---
prd_reference: docs/product/02_PRD/007-ai-threat-agents-2026-03-22.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "All 9 PRD functional requirements, all 3 user stories, and all 5 success metrics fully traceable. Spec adds 5 FRs and 2 user stories as legitimate refinements. 3 low concerns: PRD NFRs not restated, dispatch validation promoted to P0, FR-010 trust assumption phrasing."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: AI Threat Agents

**Feature Branch**: `007-ai-threat-agents`
**Created**: 2026-03-22
**Status**: Draft
**Input**: PRD 007 - AI Threat Agents

## User Scenarios & Testing

### User Story 1 - Agentic Threat Agent Validation (Priority: P0)

A security analyst provides an architecture diagram containing autonomous AI components to the orchestrator. The Agent Autonomy agent examines excessive agency, goal misalignment, missing human-in-the-loop controls, cascading failures, and autonomous resource consumption. The Tool Abuse agent examines unauthorized tool invocation, capability escalation, parameter injection, tool chain manipulation, and tool poisoning (direct, shadowing, rug pulls). Both agents produce component-specific findings referencing named components from the input with AG-prefixed IDs.

**Why this priority**: Agentic threats represent the most novel and least understood attack surface in AI systems. Autonomous agents executing tool calls without adequate controls are uniquely dangerous because they can take real-world actions. Validating these agents first establishes the agentic security coverage.

**Independent Test**: Run the Agent Autonomy agent against `examples/mermaid-agentic-app/input.md` and verify it produces findings with AG-prefixed IDs referencing specific components (e.g., "LLM Agent Orchestrator"). Run the Tool Abuse agent against the same input and verify AG-prefixed findings referencing tool-executing components (e.g., "MCP Tool Server").

**Acceptance Scenarios**:

1. **Given** an architecture with an LLM Agent Orchestrator (Process), **When** the Agent Autonomy agent analyzes it, **Then** it produces at least one finding with an AG-prefixed ID referencing "LLM Agent Orchestrator" by name covering excessive autonomy or goal misalignment
2. **Given** an architecture with an MCP Tool Server (Process), **When** the Tool Abuse agent analyzes it, **Then** it produces at least one finding with an AG-prefixed ID referencing "MCP Tool Server" by name covering tool poisoning or unauthorized invocation
3. **Given** an architecture with multi-agent communication (e.g., Orchestrator dispatching to Tool Server), **When** the Agent Autonomy agent analyzes it, **Then** it produces findings about cascading failures and autonomous resource consumption referencing the specific agent components involved
4. **Given** a component classified as Process that matches agentic dispatch keywords, **When** the Agent Autonomy agent runs, **Then** it targets that component because Processes are in its `dfd_targets` scope
5. **Given** a component classified as Data Store (e.g., "Knowledge Base"), **When** the Agent Autonomy agent runs, **Then** it does NOT produce findings for that component because Data Stores are outside its `dfd_targets` scope
6. **Given** a component classified as Data Store, **When** the Tool Abuse agent runs, **Then** it does NOT produce findings for that component because Data Stores are outside its `dfd_targets` scope
7. **Given** either agentic agent produces a finding, **When** the finding is examined, **Then** the `component` field matches a named component from the orchestrator's Phase 1 (Scope) output — generic names like "the AI agent" or "the system" are invalid
8. **Given** the Agent Autonomy agent's findings, **When** examined for framework references, **Then** each finding includes at least one reference from OWASP Agentic Top 10 (ASI-xx format)
9. **Given** the Tool Abuse agent's findings, **When** examined for framework references, **Then** each finding includes at least one reference from OWASP Agentic Top 10 (ASI-xx) or OWASP MCP Top 10 (MCP-xx:2025)
10. **Given** a purely traditional architecture with no AI/agent/MCP components, **When** the agentic agents run, **Then** they produce zero findings (empty results)

---

### User Story 2 - LLM Threat Agent Validation (Priority: P0)

A security analyst provides an architecture diagram containing LLM integration to the orchestrator. The Prompt Injection agent examines direct injection, indirect injection via documents/URLs, jailbreaking, system prompt extraction, and cross-plugin injection. The Data Poisoning agent examines training data manipulation, RAG index poisoning, knowledge base corruption, fine-tuning supply chain attacks, and context window contamination. The Model Theft agent examines model extraction via API queries, model weight exfiltration, unbounded inference consumption, and model supply chain compromise. All three agents produce component-specific findings with LLM-prefixed IDs.

**Why this priority**: LLM threats target the foundational model layer that underpins all agentic capabilities. Prompt injection (LLM01:2025) is the #1 ranked OWASP LLM threat. Data poisoning and model theft complete coverage of the model lifecycle (input integrity, stored model, output extraction).

**Independent Test**: Run the Prompt Injection agent against `examples/mermaid-agentic-app/input.md` and verify LLM-prefixed findings for LLM-related Processes. Run Data Poisoning against the same input and verify LLM-prefixed findings for Data Stores and Data Flows feeding models. Run Model Theft and verify LLM-prefixed findings for model-hosting components.

**Acceptance Scenarios**:

1. **Given** an architecture with an LLM inference service (Process), **When** the Prompt Injection agent analyzes it, **Then** it produces findings with LLM-prefixed IDs referencing that specific component covering direct injection, indirect injection, and system prompt leakage
2. **Given** an architecture with a Knowledge Base (Data Store) feeding an LLM via RAG, **When** the Data Poisoning agent analyzes it, **Then** it produces findings with LLM-prefixed IDs referencing the Knowledge Base and the data flow between it and the LLM covering RAG index poisoning and knowledge base corruption
3. **Given** an architecture with an LLM inference endpoint (Process), **When** the Model Theft agent analyzes it, **Then** it produces findings with LLM-prefixed IDs referencing that component covering model extraction and unbounded consumption
4. **Given** a component classified as Process that matches LLM dispatch keywords, **When** the Prompt Injection agent runs, **Then** it targets that component because Processes are in its `dfd_targets` scope
5. **Given** a component classified as External Entity, **When** the Prompt Injection agent runs, **Then** it does NOT produce findings for that component because External Entities are outside its `dfd_targets` scope
6. **Given** a component classified as Data Store, **When** the Data Poisoning agent runs, **Then** it targets that component because Data Stores are in its `dfd_targets` scope
7. **Given** a component classified as Data Flow feeding an LLM, **When** the Data Poisoning agent runs, **Then** it targets that data flow because Data Flows are in its `dfd_targets` scope
8. **Given** a component classified as Data Store containing model weights, **When** the Model Theft agent runs, **Then** it targets that component because Data Stores are in its `dfd_targets` scope
9. **Given** any LLM agent produces a finding, **When** examined for framework references, **Then** each finding includes at least one OWASP LLM Top 10 reference (LLM0x:2025 format)
10. **Given** a purely traditional architecture with no LLM/model components, **When** the LLM agents run, **Then** they produce zero findings (empty results)

---

### User Story 3 - Consistent Output Format Across All AI Agents (Priority: P0)

All 5 AI agents produce findings in a consistent format conforming to `schemas/finding.yaml`. The orchestrator can collect findings from any AI agent and assemble them into AG and LLM threat tables without format conversion or field mapping.

**Why this priority**: Consistent output enables the orchestrator to assemble findings from independent AI agents into unified AG and LLM tables alongside STRIDE tables. Without format consistency, the end-to-end pipeline breaks.

**Independent Test**: Run all 5 AI agents against the same architecture input and verify every finding contains all required IR fields, uses correct ID prefixes (AG-N or LLM-N), and has risk levels matching the OWASP 3x3 matrix computation.

**Acceptance Scenarios**:

1. **Given** any AI agent produces a finding, **When** the finding is examined, **Then** it contains all 10 IR fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type
2. **Given** findings from all 5 AI agents, **When** IDs are examined, **Then** agentic agent findings use AG-N prefix and LLM agent findings use LLM-N prefix — where N is sequential within each category
3. **Given** a finding with likelihood HIGH and impact HIGH, **When** the risk_level is computed, **Then** it equals Critical per the OWASP 3x3 matrix
4. **Given** a finding with likelihood LOW and impact LOW, **When** the risk_level is computed, **Then** it equals Note per the OWASP 3x3 matrix
5. **Given** a finding with likelihood MEDIUM and impact HIGH, **When** the risk_level is computed, **Then** it equals High per the OWASP 3x3 matrix
6. **Given** any AI finding, **When** the `references` field is examined, **Then** it contains at least one OWASP AI framework identifier (LLM0x:2025, ASI-xx, or MCP-xx:2025)
7. **Given** any AI finding, **When** the `dfd_element_type` field is examined, **Then** it contains one of: External Entity, Process, Data Store, or Data Flow
8. **Given** findings that reference generic components (e.g., "the model", "an agent", "the AI system"), **When** validated, **Then** they are flagged as invalid — the quality guardrail requires every finding to name a specific component from the input architecture
9. **Given** findings from agentic agents, **When** the `category` field is examined, **Then** it equals `agentic`
10. **Given** findings from LLM agents, **When** the `category` field is examined, **Then** it equals `llm`

---

### User Story 4 - Two-Layer Keyword Dispatch Validation (Priority: P0)

The orchestrator correctly dispatches to AI agents using the two-layer keyword model. Layer 1 (orchestrator dispatch) activates agent categories based on component names and descriptions matching LLM or agentic keywords. Layer 2 (agent detection scope) refines targeting using per-agent keywords for more precise threat detection.

**Why this priority**: Correct dispatch is the prerequisite for all other validation. If the orchestrator doesn't activate the right agents for the right components, all downstream findings are invalid or missing.

**Independent Test**: Run the orchestrator against `examples/mermaid-agentic-app/input.md` and verify the dispatch table shows correct agent activation per component based on keyword matching.

**Acceptance Scenarios**:

1. **Given** a component named "LLM Agent Orchestrator" containing both LLM and agentic keywords, **When** the orchestrator dispatches, **Then** it activates all 5 AI agents (dual-dispatch) plus applicable STRIDE agents for that component
2. **Given** a component named "MCP Tool Server" containing agentic keywords but no LLM keywords, **When** the orchestrator dispatches, **Then** it activates only the 2 agentic agents (agent-autonomy, tool-abuse) plus applicable STRIDE agents
3. **Given** a component named "Knowledge Base" containing no AI/LLM/agentic keywords, **When** the orchestrator dispatches, **Then** it activates only STRIDE agents — no AI agents are dispatched
4. **Given** a component whose description (not just name) contains LLM keywords (e.g., "Manages LLM inference requests"), **When** the orchestrator dispatches, **Then** it activates LLM agents based on description keyword matching
5. **Given** a component matching LLM dispatch keywords, **When** LLM agents run, **Then** each agent further refines its scope using Layer 2 detection keywords specific to its threat class (e.g., Data Poisoning looks for "training", "RAG", "vector store")
6. **Given** a purely traditional architecture with no AI/LLM/agentic keywords in any component, **When** the orchestrator dispatches, **Then** zero AI agents are activated — only STRIDE agents run

---

### User Story 5 - End-to-End Orchestrator Integration (Priority: P1)

The orchestrator dispatches to all 5 validated AI agents and assembles their findings into AG and LLM threat tables in `threats.md`. The end-to-end flow from architecture input to assembled threat model includes both STRIDE and AI tables without manual intervention.

**Why this priority**: End-to-end integration validates that AI agents work correctly within the orchestrator's dispatch protocol alongside STRIDE agents. Individual agent validation (US-1 through US-4) ensures quality; integration testing ensures the complete pipeline works.

**Independent Test**: Run the orchestrator against `examples/mermaid-agentic-app/input.md` and verify the output `threats.md` contains AG and LLM threat tables with findings, correct component references, and valid risk computations.

**Acceptance Scenarios**:

1. **Given** the mermaid-agentic-app example input, **When** the orchestrator dispatches to all 5 AI agents and assembles findings, **Then** the resulting `threats.md` contains one AG threat table and one LLM threat table with at least one finding each
2. **Given** the assembled `threats.md`, **When** the AG table is examined, **Then** it contains findings from both agent-autonomy and tool-abuse agents with AG-prefixed IDs, each referencing named components
3. **Given** the assembled `threats.md`, **When** the LLM table is examined, **Then** it contains findings from prompt-injection, data-poisoning, and model-theft agents with LLM-prefixed IDs, each referencing named components
4. **Given** the assembled `threats.md`, **When** the coverage matrix is examined, **Then** it shows AI agent dispatch for components matching AI/LLM/agentic keywords and no AI dispatch for traditional components
5. **Given** the assembled `threats.md`, **When** every finding across AG and LLM tables is examined, **Then** 100% reference a named component from the input architecture (zero generic findings)
6. **Given** the assembled `threats.md`, **When** both STRIDE and AI tables are present, **Then** finding ID namespaces do not conflict (S/T/R/I/D/E prefixes are separate from AG/LLM prefixes)

---

### Edge Cases

- What happens when a component matches both LLM and agentic dispatch keywords? The orchestrator activates all 5 AI agents for that component (dual-dispatch). Each agent independently evaluates the component through its own threat lens.
- What happens when an AI agent targets a DFD element type outside its assigned scope? The finding is flagged as invalid by the quality guardrail (agent must not produce findings for element types outside its `dfd_targets`).
- What happens when the architecture contains no AI/LLM/agentic components? All AI agents produce zero findings (empty results). Only STRIDE agents produce output. The `threats.md` contains STRIDE tables but empty or absent AG and LLM tables.
- What happens when two AI agents identify overlapping threats (e.g., prompt injection and tool abuse both flag an MCP server)? Each agent produces its own finding with its category-specific lens and ID prefix. Deduplication is out of scope (future feature).
- What happens when the orchestrator's Layer 1 keyword matching produces a false positive (e.g., a "data model" component triggering LLM dispatch)? The AI agent's Layer 2 detection patterns provide secondary filtering — if no AI-relevant characteristics are detected, the agent produces zero findings for that component despite being dispatched.

## Requirements

### Functional Requirements

- **FR-001**: Each of the 5 AI agents MUST analyze architecture input through exactly one threat lens corresponding to its assigned AI threat class (Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, or Tool Abuse)
- **FR-002**: Each agent MUST target only the DFD element types defined in its `dfd_targets` frontmatter — Prompt Injection (Process), Data Poisoning (Data Store, Data Flow), Model Theft (Data Store, Process), Agent Autonomy (Process), Tool Abuse (Process) — and MUST NOT produce findings for element types outside its scope
- **FR-003**: Every finding produced by any AI agent MUST reference a named component from the architecture input in the `component` field — findings with generic component names (e.g., "the AI", "a model", "the system") are invalid
- **FR-004**: All findings MUST conform to `schemas/finding.yaml` intermediate representation with all 10 fields populated (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type)
- **FR-005**: Finding IDs MUST follow the sequential prefix convention: LLM-N for LLM agents, AG-N for agentic agents (where N starts at 1 and increments per finding within each category)
- **FR-006**: Risk levels MUST be computed from the OWASP 3x3 matrix (likelihood x impact) — HIGH/HIGH=Critical, HIGH/MEDIUM=High, MEDIUM/MEDIUM=Medium, LOW/LOW=Note, etc.
- **FR-007**: Each finding MUST include at least one reference to an established AI security framework (OWASP LLM Top 10 v2025 using LLM0x:2025 format, OWASP Agentic Top 10 using ASI-xx format, or OWASP MCP Top 10 using MCP-xx:2025 format)
- **FR-008**: Each agent MUST include detailed detection patterns organized by attack subcategory as defined in the PRD's FR-8 (prompt injection: direct/indirect/jailbreaking/system prompt extraction/cross-plugin; data poisoning: training data/RAG index/knowledge base/fine-tuning/context window; model theft: API extraction/weight exfiltration/unbounded consumption/supply chain; agent autonomy: excessive autonomy/goal misalignment/unconstrained scope/missing HITL/cascading failures/resource consumption; tool abuse: unauthorized invocation/capability escalation/parameter injection/tool chain manipulation/tool poisoning)
- **FR-009**: Each agent's frontmatter MUST include consistent metadata: agent_name, category, threat_class, dfd_targets, owasp_references, and output_schema reference — matching the structure used by validated STRIDE agents
- **FR-010**: Each finding's `threat` field MUST describe both what the attacker does and what trust assumption is violated — vague descriptions like "could be poisoned" or "may be compromised" are invalid
- **FR-011**: Each finding's `mitigation` field MUST provide an actionable countermeasure with specific technology or configuration — generic advice like "implement AI safety" is invalid
- **FR-012**: All 5 agents MUST follow identical structural organization: frontmatter, purpose, detection scope, detection patterns, finding template, risk computation, references
- **FR-013**: AI agents MUST produce empty results (zero findings) when the input architecture contains no AI/LLM/agentic components, preventing false positives for purely traditional systems
- **FR-014**: The orchestrator MUST use the two-layer keyword dispatch model: Layer 1 (orchestrator dispatch keywords) activates agent categories, Layer 2 (per-agent detection scope) refines targeting within activated categories

### Key Entities

- **AI Threat Agent**: A markdown prompt file in `agents/ai/` that encodes detection patterns, finding templates, and framework references for exactly one AI threat class (Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, or Tool Abuse)
- **Finding (IR)**: A 10-field intermediate representation conforming to `schemas/finding.yaml` that captures a single identified AI-specific threat with component reference, risk assessment, mitigation, and OWASP AI framework cross-references
- **AI Threat Category**: One of two top-level categories — `llm` (for Prompt Injection, Data Poisoning, Model Theft agents) or `agentic` (for Agent Autonomy, Tool Abuse agents) — determining the finding ID prefix and output table placement
- **Detection Pattern**: A structured description within an agent prompt that defines what AI-specific indicators to look for (attack subcategory, trigger conditions, vulnerable configurations) within applicable DFD element types
- **Two-Layer Keyword Dispatch**: The mechanism by which the orchestrator activates AI agents — Layer 1 matches component names/descriptions against category-level keywords, Layer 2 applies per-agent detection scope keywords for refined targeting
- **OWASP AI Framework Reference**: Official vulnerability identifiers from three complementary frameworks — LLM Top 10 v2025 (LLM0x:2025), Agentic Top 10 2026 (ASI-xx), MCP Top 10 2025 (MCP-xx:2025) — required in every AI finding

## Success Criteria

### Measurable Outcomes

- **SC-001**: Component Specificity Rate — 100% of findings across all 5 AI agents reference a named component from the input architecture (zero generic findings)
- **SC-002**: AI Category Coverage — Both AI categories (AG, LLM) produce at least 1 finding when given an architecture with applicable component types (verified against `examples/mermaid-agentic-app/input.md`)
- **SC-003**: Schema Compliance — 100% of findings conform to all 10 fields defined in `schemas/finding.yaml` with correct data types, enum values, and AI-specific category values (`llm`, `agentic`)
- **SC-004**: DFD Element Accuracy — Zero findings produced for DFD element types outside each agent's assigned scope (cross-referenced against the agent's `dfd_targets` frontmatter)
- **SC-005**: Risk Computation Correctness — 100% of risk_level values match the OWASP 3x3 matrix computation from the finding's likelihood and impact values
- **SC-006**: OWASP AI Reference Coverage — 100% of findings include at least one AI-specific OWASP reference ID (LLM0x:2025, ASI-xx, or MCP-xx:2025) in the `references` field
- **SC-007**: End-to-End Integration — The orchestrator successfully dispatches to all 5 AI agents and assembles findings into valid AG and LLM threat tables in `threats.md`
- **SC-008**: Structural Consistency — All 5 agent files follow identical section organization matching the validated STRIDE agent pattern (frontmatter, purpose, detection scope, patterns, finding template, risk computation, references)
- **SC-009**: Empty Results for Non-AI Architectures — All 5 AI agents produce zero findings when given a purely traditional architecture with no AI/LLM/agentic components
- **SC-010**: Dispatch Accuracy — The orchestrator's two-layer keyword dispatch correctly activates AI agents only for components matching AI/LLM/agentic keywords and produces no false activations for traditional components

## Scope & Boundaries

### In Scope

**Must Have (P0)**:
- All 5 AI agent prompt files validated for completeness and correctness
- Each agent targets correct DFD element types per interface contract AI extension rules
- All findings reference specific components from input architecture
- Consistent finding format across all 5 agents conforming to `schemas/finding.yaml`
- OWASP AI framework reference IDs in every finding (LLM0x:2025, ASI-xx, MCP-xx:2025)
- End-to-end validation: orchestrator dispatches to AI agents and assembles valid AG and LLM tables
- Empty results for non-AI architectures
- Two-layer keyword dispatch validation

**Should Have (P1)**:
- MITRE ATLAS cross-references for AI attack taxonomy
- CWE identifiers for vulnerability classification where applicable

### Out of Scope
- Deduplication and risk rating refinement across STRIDE + AI findings (future feature)
- Platform-specific adapters for dispatching agents (F-009)
- Custom AI threat categories beyond OWASP frameworks
- Agent prompt fine-tuning for specific LLM providers
- Additional AI agent categories (e.g., multimodal threats, embedding attacks)
- Changes to `schemas/finding.yaml` or `docs/INTERFACE-CONTRACT.md`
- Runtime schema validation scripts or tooling

### Assumptions
- The orchestrator (F-003) correctly parses architecture input and dispatches to AI agents based on keyword detection
- The `schemas/finding.yaml` schema supports AI categories (`llm`, `agentic`) and ID prefixes (`LLM-N`, `AG-N`) without modification
- The sample architecture in `examples/mermaid-agentic-app/input.md` contains sufficient AI/LLM/agentic components for validation
- STRIDE agents (F-005) are delivered and stable — AI agents follow the same validated pattern
- All 5 AI agent prompt files already exist with substantial content; this feature validates and completes them, not builds from scratch
- "Validation" means running agents against sample input and checking output against schema and quality criteria

### Open Questions
- Should AI agents detect threats in non-AI components that interact with AI (e.g., a database storing model outputs)? — architect — 2026-03-29
- Should cross-references between AI and STRIDE categories be noted in findings (e.g., a prompt injection finding that also has Tampering implications)? — architect — 2026-03-29
- What is the minimum number of OWASP references per finding — 1 or should agents aim for comprehensive cross-referencing? — product-manager — 2026-03-29
