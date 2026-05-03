---
prd_reference: docs/product/02_PRD/005-stride-threat-agents-2026-03-21.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "All 7 PRD functional requirements (FR-1 through FR-7) fully traceable. All 4 PRD user stories mapped with 33 acceptance scenarios. 8 measurable success criteria. 2 low concerns (PRD table cross-references deferred to plan/tasks, priority labels aligned). 1 informational (deduplication deferred to F-004)."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: STRIDE Threat Agents

**Feature Branch**: `005-stride-threat-agents`
**Created**: 2026-03-21
**Status**: Draft
**Input**: PRD 005 - STRIDE Threat Agents

## User Scenarios & Testing

### User Story 1 - Spoofing and Tampering Agent Validation (Priority: P0)

A security analyst provides an architecture diagram to the orchestrator. The Spoofing agent examines authentication mechanisms, API keys, session management, and service-to-service identity. The Tampering agent examines input validation, data flow integrity, message signing, and database write controls. Both agents produce component-specific findings referencing named components from the input.

**Why this priority**: Spoofing and Tampering represent the most common attack vectors (identity compromise and data integrity violations). Together they cover authentication and integrity — the two most exploited security properties in agentic AI systems. Validating these agents first establishes the quality bar for all remaining agents.

**Independent Test**: Run the Spoofing agent against `examples/mermaid-agentic-app/input.md` and verify it produces findings with S-prefixed IDs referencing specific components (e.g., "User", "LLM Agent Orchestrator"). Run the Tampering agent against the same input and verify T-prefixed findings referencing applicable components.

**Acceptance Scenarios**:

1. **Given** an architecture with an LLM Agent Orchestrator (Process), **When** the Spoofing agent analyzes it, **Then** it produces at least one finding with an S-prefixed ID referencing "LLM Agent Orchestrator" by name
2. **Given** an architecture with a Knowledge Base (Data Store) and data flows between services, **When** the Tampering agent analyzes it, **Then** it produces findings with T-prefixed IDs referencing those specific components by name
3. **Given** a component classified as External Entity (e.g., "User"), **When** the Spoofing agent runs, **Then** it targets that component because External Entities are susceptible to Spoofing per the STRIDE-per-Element matrix
4. **Given** a component classified as External Entity (e.g., "User"), **When** the Tampering agent runs, **Then** it does NOT produce findings for that component because External Entities are not susceptible to Tampering per the STRIDE-per-Element matrix
5. **Given** a component classified as Data Flow, **When** the Spoofing agent runs, **Then** it does NOT produce findings for that component because Data Flows are not susceptible to Spoofing
6. **Given** a component classified as Data Flow, **When** the Tampering agent runs, **Then** it produces findings for that component because Data Flows are susceptible to Tampering
7. **Given** either agent produces a finding, **When** the finding is examined, **Then** the `component` field matches a named component from the orchestrator's Phase 1 (Scope) output — generic names like "the system" or "a service" are invalid
8. **Given** the Spoofing agent's findings, **When** examined for framework references, **Then** each finding includes at least one reference from OWASP, CWE, or MITRE ATT&CK (e.g., CWE-287, OWASP A07:2021, ATT&CK T1078)
9. **Given** the Tampering agent's findings, **When** examined for framework references, **Then** each finding includes at least one reference from OWASP, CWE, or MITRE ATT&CK (e.g., CWE-20, OWASP A03:2021)

---

### User Story 2 - Repudiation and Information Disclosure Agent Validation (Priority: P0)

A security analyst provides an architecture diagram. The Repudiation agent examines logging coverage, audit trail completeness, log integrity, and non-repudiation mechanisms. The Information Disclosure agent examines data classification, encryption (transit/rest), error messages, API response filtering, and storage access controls. Both produce component-specific findings with appropriate DFD element targeting.

**Why this priority**: Repudiation gaps (missing audit trails) and information disclosure (data exposure) are frequently missed in manual threat modeling. These agents cover confidentiality and non-repudiation — completing the security property coverage alongside US-1.

**Independent Test**: Run the Repudiation agent against `examples/mermaid-agentic-app/input.md` and verify it produces R-prefixed findings for applicable components (External Entities and Processes only). Run the Information Disclosure agent and verify I-prefixed findings for Processes, Data Stores, and Data Flows.

**Acceptance Scenarios**:

1. **Given** an architecture with backend services (Processes), **When** the Repudiation agent analyzes it, **Then** it produces findings about logging and audit gaps for those specific services with R-prefixed IDs
2. **Given** an architecture with a Knowledge Base (Data Store) and data flows, **When** the Information Disclosure agent analyzes it, **Then** it produces findings about data exposure risks for those specific components with I-prefixed IDs
3. **Given** a component classified as Data Flow, **When** the Repudiation agent runs, **Then** it does NOT produce findings for that component because Data Flows are not susceptible to Repudiation per the STRIDE-per-Element matrix
4. **Given** a component classified as Data Store, **When** the Information Disclosure agent runs, **Then** it targets that component because Data Stores are susceptible to Information Disclosure
5. **Given** either agent produces findings, **When** the findings are examined, **Then** each includes a concrete mitigation tied to the system's component (not generic advice like "implement proper logging")
6. **Given** the Information Disclosure agent's findings, **When** examined, **Then** each finding's `threat` field describes what specific data could be exposed and through what mechanism

---

### User Story 3 - Denial of Service and Elevation of Privilege Agent Validation (Priority: P0)

A security analyst provides an architecture diagram. The Denial of Service agent examines rate limiting, resource quotas, queue depths, circuit breakers, and failover mechanisms. The Elevation of Privilege agent examines RBAC/ABAC implementation, permission boundaries, default permissions, and lateral movement paths. Both produce component-specific findings following the STRIDE-per-Element targeting rules.

**Why this priority**: DoS and EoP complete the STRIDE hexad. DoS threats are critical for agentic systems where autonomous agents can consume unbounded resources. EoP threats address authorization — the most impactful vulnerability class (OWASP A01:2021 Broken Access Control).

**Independent Test**: Run the DoS agent against `examples/mermaid-agentic-app/input.md` and verify D-prefixed findings for Processes, Data Stores, and Data Flows (not External Entities). Run the EoP agent and verify E-prefixed findings for Processes only.

**Acceptance Scenarios**:

1. **Given** an architecture with API endpoints and services (Processes), **When** the DoS agent analyzes it, **Then** it produces findings about availability threats for those specific components with D-prefixed IDs
2. **Given** an architecture with services and user roles, **When** the Privilege Escalation agent analyzes it, **Then** it produces findings about authorization threats for those specific components with E-prefixed IDs
3. **Given** a component classified as External Entity, **When** the DoS agent runs, **Then** it does NOT produce findings for that component because External Entities are not susceptible to DoS per the STRIDE-per-Element matrix
4. **Given** a component classified as External Entity, **When** the Privilege Escalation agent runs, **Then** it does NOT produce findings for that component because External Entities are not susceptible to Elevation of Privilege
5. **Given** a component classified as Data Store, **When** the DoS agent runs, **Then** it targets that component because Data Stores are susceptible to DoS
6. **Given** a component classified as Data Store, **When** the Privilege Escalation agent runs, **Then** it does NOT produce findings for that component because Data Stores are not susceptible to Elevation of Privilege
7. **Given** each agent follows Microsoft STRIDE methodology, **When** producing findings, **Then** findings pattern-match against known threat categories defined in the agent's detection patterns — agents do not invent novel attack types

---

### User Story 4 - Consistent Output Format Across All Agents (Priority: P0)

All 6 STRIDE agents produce findings in a consistent format conforming to `schemas/finding.yaml`. The orchestrator can collect findings from any agent and assemble them into a unified threat model without format conversion or field mapping.

**Why this priority**: Consistent output is what enables the orchestrator to assemble findings from independent agents into a single, coherent threat model. Without format consistency, the end-to-end pipeline breaks.

**Independent Test**: Run all 6 agents against the same architecture input and verify every finding from every agent contains all required IR fields, uses correct ID prefixes, and has risk levels matching the OWASP 3x3 matrix computation.

**Acceptance Scenarios**:

1. **Given** any STRIDE agent produces a finding, **When** the finding is examined, **Then** it contains all 10 IR fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type
2. **Given** findings from all 6 agents, **When** IDs are examined, **Then** each follows the convention: S-N (Spoofing), T-N (Tampering), R-N (Repudiation), I-N (Information Disclosure), D-N (Denial of Service), E-N (Elevation of Privilege) — where N is sequential within each category
3. **Given** a finding with likelihood HIGH and impact HIGH, **When** the risk_level is computed, **Then** it equals Critical per the OWASP 3x3 matrix
4. **Given** a finding with likelihood LOW and impact LOW, **When** the risk_level is computed, **Then** it equals Note per the OWASP 3x3 matrix
5. **Given** a finding with likelihood MEDIUM and impact HIGH, **When** the risk_level is computed, **Then** it equals High per the OWASP 3x3 matrix
6. **Given** any finding, **When** the `references` field is examined, **Then** it contains at least one identifier from OWASP, CWE, or MITRE ATT&CK
7. **Given** any finding, **When** the `dfd_element_type` field is examined, **Then** it contains one of: External Entity, Process, Data Store, or Data Flow
8. **Given** findings that reference generic components (e.g., "the system", "the application", "a service"), **When** validated, **Then** they are flagged as invalid — the quality guardrail requires every finding to name a specific component from the input architecture

---

### User Story 5 - End-to-End Orchestrator Integration (Priority: P2)

The orchestrator dispatches to all 6 validated STRIDE agents and assembles their findings into a complete `threats.md` with all STRIDE table sections populated. The end-to-end flow from architecture input to assembled threat model works without manual intervention.

**Why this priority**: End-to-end integration validates that the agents work correctly within the orchestrator's dispatch protocol. Individual agent validation (US-1 through US-4) ensures quality; integration testing ensures the pipeline works as a whole.

**Independent Test**: Run the orchestrator against `examples/mermaid-agentic-app/input.md` and verify the output `threats.md` contains 6 STRIDE tables with findings, a coverage matrix showing all 5 components analyzed, and a risk summary with valid counts.

**Acceptance Scenarios**:

1. **Given** the mermaid-agentic-app example input, **When** the orchestrator dispatches to all 6 STRIDE agents and assembles findings, **Then** the resulting `threats.md` contains one table per STRIDE category with at least one finding each
2. **Given** the assembled `threats.md`, **When** the coverage matrix is examined, **Then** it shows finding counts for each component-category pair that matches the STRIDE-per-Element matrix (e.g., "User" has counts only in S and R columns)
3. **Given** the assembled `threats.md`, **When** the risk summary is examined, **Then** it contains accurate counts per risk level (Critical, High, Medium, Low, Note) matching the sum of all findings
4. **Given** the assembled `threats.md`, **When** every finding across all 6 tables is examined, **Then** 100% reference a named component from the input architecture (zero generic findings)

---

### Edge Cases

- What happens when a component has no applicable threats for a given agent? The agent produces zero findings for that component; the coverage matrix shows `-` (analyzed, no threats found) for that cell.
- What happens when an agent produces a finding with incorrect DFD element type for its scope? The finding is flagged as invalid by the quality guardrail (agent must not produce findings for element types outside its `dfd_targets`).
- How do agents handle components that could be classified as multiple DFD types? Agents use the DFD classification assigned by the orchestrator in Phase 1 — they do not reclassify components themselves.
- What happens when two agents identify overlapping threats (e.g., Spoofing and Elevation of Privilege both flag weak authentication)? Each agent produces its own finding with its category-specific lens. Deduplication is out of scope (future feature).
- How do agents handle architectures with only External Entities and no Processes? Only Spoofing and Repudiation agents produce findings (the only categories applicable to External Entities). Other agents produce empty results.

## Requirements

### Functional Requirements

- **FR-001**: Each of the 6 STRIDE agents MUST analyze architecture input through exactly one threat lens corresponding to its assigned STRIDE category (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, or Elevation of Privilege)
- **FR-002**: Each agent MUST target only the DFD element types assigned by the STRIDE-per-Element matrix — Processes (all 6), Data Flows (T, I, D), Data Stores (T, I, D), External Entities (S, R) — and MUST NOT produce findings for element types outside its scope
- **FR-003**: Every finding produced by any agent MUST reference a named component from the architecture input in the `component` field — findings with generic component names are invalid
- **FR-004**: All findings MUST conform to the `schemas/finding.yaml` intermediate representation with all 10 fields populated (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type)
- **FR-005**: Finding IDs MUST follow the sequential prefix convention: S-N, T-N, R-N, I-N, D-N, E-N (where N starts at 1 and increments per finding within each category)
- **FR-006**: Risk levels MUST be computed from the OWASP 3x3 matrix (likelihood x impact) as defined in the PRD's FR-5 table
- **FR-007**: Each finding MUST include at least one reference to an established security framework (OWASP Top 10, OWASP API Security Top 10, CWE, or MITRE ATT&CK)
- **FR-008**: Each agent MUST include detailed detection patterns organized by attack subcategory as defined in the PRD's FR-7
- **FR-009**: Each agent's frontmatter MUST include consistent metadata: agent_name, category, threat_class, dfd_targets, owasp_references, and output_schema reference
- **FR-010**: Each finding's `threat` field MUST describe both what the attacker does and what trust assumption is violated — vague descriptions like "could be tampered" are invalid
- **FR-011**: Each finding's `mitigation` field MUST provide an actionable countermeasure with specific technology or configuration — generic advice like "implement proper security" is invalid
- **FR-012**: All 6 agents MUST follow identical structural organization: frontmatter, purpose, detection scope, detection patterns, finding template, risk computation, references

### Key Entities

- **STRIDE Agent**: A markdown prompt file in `agents/stride/` that encodes detection patterns, finding templates, and framework references for exactly one STRIDE threat category
- **Finding (IR)**: A 10-field intermediate representation conforming to `schemas/finding.yaml` that captures a single identified threat with component reference, risk assessment, mitigation, and framework cross-references
- **DFD Element Type**: One of four data flow diagram classifications (External Entity, Process, Data Store, Data Flow) that determines which STRIDE categories apply to a component
- **STRIDE-per-Element Matrix**: The Microsoft-defined mapping of DFD element types to applicable STRIDE categories, serving as the targeting constraint for each agent
- **Detection Pattern**: A structured description within an agent prompt that defines what to look for (attack subcategory, indicators, vulnerable configurations) within a specific DFD element type

## Success Criteria

### Measurable Outcomes

- **SC-001**: Component Specificity Rate — 100% of findings across all 6 agents reference a named component from the input architecture (zero generic findings)
- **SC-002**: STRIDE Coverage — All 6 categories produce at least 1 finding when given an architecture with applicable component types (verified against `examples/mermaid-agentic-app/input.md`)
- **SC-003**: Schema Compliance — 100% of findings conform to all 10 fields defined in `schemas/finding.yaml` with correct data types and enum values
- **SC-004**: DFD Element Accuracy — Zero findings produced for DFD element types outside each agent's assigned scope (cross-referenced against the agent's `dfd_targets` frontmatter)
- **SC-005**: Risk Computation Correctness — 100% of risk_level values match the OWASP 3x3 matrix computation from the finding's likelihood and impact values
- **SC-006**: Framework Reference Coverage — 100% of findings include at least one OWASP, CWE, or MITRE ATT&CK reference in the `references` field
- **SC-007**: End-to-End Integration — The orchestrator successfully dispatches to all 6 agents and assembles findings into a valid `threats.md` with all 6 STRIDE tables populated
- **SC-008**: Structural Consistency — All 6 agent files follow identical section organization (frontmatter, purpose, detection scope, patterns, finding template, risk computation, references)

## Scope & Boundaries

### In Scope

**Must Have (P0)**:
- All 6 STRIDE agent prompt files validated for completeness and correctness
- Each agent targets correct DFD element types per STRIDE-per-Element matrix
- All findings reference specific components from input architecture
- Consistent finding format across all 6 agents conforming to `schemas/finding.yaml`
- End-to-end validation: orchestrator dispatches to agents and assembles valid `threats.md`

**Should Have (P1)**:
- OWASP API Security Top 10 2023 cross-references embedded in relevant agents
- OWASP Top 10 2021 cross-references for baseline context
- CWE and MITRE ATT&CK identifiers in detection patterns

### Out of Scope
- AI-specific threat agents (F-004 — separate feature, same agent pattern)
- Deduplication and risk rating refinement across agents (future feature)
- Platform-specific adapters for dispatching agents (F-009)
- Custom threat categories beyond STRIDE
- Agent prompt fine-tuning for specific LLM providers
- Runtime schema validation scripts or tooling
- Changes to `schemas/finding.yaml` or `docs/INTERFACE-CONTRACT.md`

### Assumptions
- The orchestrator (F-003) correctly parses architecture input and classifies components into DFD element types
- The `schemas/finding.yaml` schema is stable and will not change during this feature
- The sample architecture in `examples/mermaid-agentic-app/input.md` is representative enough for validation
- "Validation" means running agents against sample input and checking output against schema and quality criteria — not automated test scripts
- Agent prompt files already exist with substantial content; this feature validates and completes them, not builds from scratch

### Open Questions
- Should agents produce a minimum number of findings per component, or is quality-only (no minimum) acceptable? — product-manager — 2026-03-28
- Should cross-references between STRIDE categories be noted in findings (e.g., a Spoofing finding that also has Tampering implications)? — architect — 2026-03-28
