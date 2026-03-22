---
prd:
  number: "005"
  topic: stride-threat-agents
  created: 2026-03-21
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-21, status: approved, notes: "PRD drafted by PM via ~aod-define skill with GitHub Issue #5 user stories and consumer guide research as primary inputs"}
  architect_signoff: {agent: architect, date: 2026-03-21, status: approved_with_concerns, notes: "Technically feasible. STRIDE-per-Element matrix verified correct across all artifacts. 1 medium concern (dependency graph numbering collision -- corrected) and 2 low concerns (dispatch mechanism clarification, IR vs. rendered table -- both addressed)."}
  techlead_signoff: {agent: team-lead, date: 2026-03-21, status: approved_with_concerns, notes: "Feasible in 1 sprint. Agents are content-complete (100-116 lines each); work is validation/refinement. PRD effort estimates (M) slightly conservative but provide healthy buffer. 3-wave execution strategy (parallel validation, consistency check, end-to-end). No blockers."}
source:
  idea_id: 5
  story_id: null
---

# STRIDE Threat Agents - Product Requirements Document

**Status**: Draft
**Created**: 2026-03-21
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 1 (Foundation)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Build all 6 STRIDE threat agents so that each one analyzes an architecture through exactly one threat lens and produces component-specific findings grounded in the Microsoft STRIDE framework.

### Problem Statement
Developers building agentic AI applications need systematic threat identification across all six STRIDE categories. The orchestrator (F-003) can parse architecture input, dispatch to agents, and assemble output -- but the STRIDE agents it dispatches to must produce specific, component-referencing findings grounded in established security frameworks. Without fully validated STRIDE agents, the orchestrator dispatches to agents that may produce generic, untargeted threats rather than actionable, component-specific findings tied to the STRIDE-per-Element matrix.

The agent prompt files exist in `agents/stride/` with detailed detection patterns and finding templates (delivered as part of F-001 skeleton and refined in F-003). This feature validates, tests, and ensures end-to-end correctness of all 6 agents when invoked by the orchestrator against real architecture input.

### Proposed Solution
Validate and complete all 6 STRIDE agent prompt files (`agents/stride/*.md`) so each agent:

1. **Analyzes through exactly one threat lens** -- Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, or Elevation of Privilege
2. **Targets correct DFD element types** -- per the STRIDE-per-Element matrix from Microsoft's methodology
3. **Produces component-specific findings** -- every finding references a specific component from the input architecture; generic/untargeted threats are rejected
4. **Follows consistent output format** -- findings conform to `schemas/finding.yaml` with ID convention (S-N, T-N, R-N, I-N, D-N, E-N)
5. **Includes framework-grounded references** -- OWASP, CWE, MITRE ATT&CK identifiers supporting each finding

Each agent is a **markdown prompt file**, not application code. Agents are platform-neutral and work with any LLM capable of following structured markdown prompts.

**Dispatch model**: When the orchestrator "dispatches" to a STRIDE agent, it follows that agent's analysis methodology within its own execution context -- it does not invoke a separate process or API call. The orchestrator internalizes each agent's detection patterns and finding template to produce findings for that category. Platform-specific multi-call dispatch (e.g., parallel agent invocation) is an adapter concern addressed in F-009.

### Success Criteria
- All 6 STRIDE agents produce specific, component-referencing findings when given the sample architecture (`examples/mermaid-agentic-app/input.md`)
- No generic or untargeted threats appear in any agent's output -- every finding references a named component from the input
- Each agent's findings conform to `schemas/finding.yaml` with correct ID prefix (S-N, T-N, R-N, I-N, D-N, E-N)
- Each agent targets only its assigned DFD element types per the STRIDE-per-Element matrix
- Risk levels are computed correctly using the OWASP 3x3 matrix (likelihood x impact)
- Orchestrator can dispatch to all 6 agents and assemble their findings into a valid `threats.md`

### Timeline
Target: 1 development sprint (estimated during Team-Lead feasibility review)

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature directly delivers the core value proposition: "First toolkit to natively model AI-specific threat agents alongside traditional STRIDE." The STRIDE agents are the foundational threat analysis layer. Without them producing validated, component-specific findings, the toolkit cannot deliver structured threat models. The orchestrator (F-003) provides the workflow; the STRIDE agents provide the security analysis substance.

### Roadmap Fit
**Phase**: Phase 1 (Foundation)
**Dependencies**: F-001 (delivered) -- repository skeleton, interface contract, schemas; F-003 (delivered) -- orchestrator agent with dispatch logic
**Blocks**: F-004 (AI Agents -- same pattern, AI-specific threats), Dedup & Risk Rating (future -- operates on STRIDE+AI findings), F-009 (Platform Adapters -- wraps orchestrator+agents for specific platforms)

The STRIDE agents must produce validated output before AI agents (F-004) can be built using the same pattern. The deduplication feature operates on the combined findings from STRIDE and AI agents. This is the next critical path item after the orchestrator.

---

## Target Users & Personas

### Primary Persona: Security Analyst
- **Role**: Security professional performing threat modeling on agentic AI systems
- **Experience**: Familiar with STRIDE methodology and threat modeling processes
- **Goals**: Systematically identify threats across all 6 STRIDE categories for a given architecture
- **Pain Points**: Manual threat modeling is time-consuming, inconsistent, and prone to missing categories

**Why This Matters to Them**: Each STRIDE agent automates one category of threat identification with framework-grounded patterns, ensuring complete coverage and consistent quality across all 6 categories.

### Secondary Persona: AI Agent Developer
- **Role**: Software developer building agentic AI applications
- **Experience**: Proficient in code, new to threat modeling methodology
- **Goals**: Get a complete threat model for their architecture without deep security expertise
- **Pain Points**: Doesn't know what threats to look for, doesn't have time to learn all 6 STRIDE categories in depth

**Why This Matters to Them**: The STRIDE agents encode security expertise into reusable prompts, so developers get expert-level threat identification without needing to be security experts themselves.

---

## User Stories

### US-1: Spoofing and Tampering Agents
**When** a security analyst provides an architecture diagram to the orchestrator,
**I want** the Spoofing agent to examine authentication mechanisms, API keys, session management, and service-to-service identity, and the Tampering agent to examine input validation, data flow integrity, message signing, and database write controls,
**So I can** have identity/authentication and data integrity threats systematically identified.

**Acceptance Criteria**:
- **Given** an architecture with an OAuth Login Service, **when** the Spoofing agent analyzes it, **then** it produces findings referencing that specific component with S-prefixed IDs
- **Given** an architecture with a database and API data flows, **when** the Tampering agent analyzes it, **then** it produces findings referencing those specific components with T-prefixed IDs
- **Given** a component classified as External Entity, **when** the Spoofing agent runs, **then** it targets that component (External Entities are susceptible to Spoofing per STRIDE-per-Element)
- **Given** a component classified as External Entity, **when** the Tampering agent runs, **then** it does NOT target that component (External Entities are not susceptible to Tampering per STRIDE-per-Element)
- Every finding references a specific component from the input diagram -- generic threats are rejected

**Priority**: P0
**Effort**: M

### US-2: Repudiation and Information Disclosure Agents
**When** a security analyst provides an architecture diagram to the orchestrator,
**I want** the Repudiation agent to examine logging coverage, audit trail completeness, log integrity, and non-repudiation mechanisms, and the Information Disclosure agent to examine data classification, encryption (transit/rest), error messages, API response filtering, and storage access controls,
**So I can** have audit gaps and data exposure risks identified.

**Acceptance Criteria**:
- **Given** an architecture with backend services, **when** the Repudiation agent analyzes it, **then** it produces findings about logging and audit gaps for those specific services with R-prefixed IDs
- **Given** an architecture with data stores and data flows, **when** the Information Disclosure agent analyzes it, **then** it produces findings about data exposure risks for those specific components with I-prefixed IDs
- Findings include concrete mitigations tied to the system's technology stack
- **Given** a component classified as Data Flow, **when** the Repudiation agent runs, **then** it does NOT target that component (Data Flows are not susceptible to Repudiation per STRIDE-per-Element)

**Priority**: P0
**Effort**: M

### US-3: Denial of Service and Privilege Escalation Agents
**When** a security analyst provides an architecture diagram to the orchestrator,
**I want** the Denial of Service agent to examine rate limiting, resource quotas, queue depths, circuit breakers, and failover mechanisms, and the Privilege Escalation agent to examine RBAC/ABAC implementation, permission boundaries, default permissions, and lateral movement paths,
**So I can** have availability and authorization threats covered.

**Acceptance Criteria**:
- **Given** an architecture with API endpoints and services, **when** the DoS agent analyzes it, **then** it produces findings about availability threats for those specific components with D-prefixed IDs
- **Given** an architecture with services and user roles, **when** the Privilege Escalation agent analyzes it, **then** it produces findings about authorization threats for those specific components with E-prefixed IDs
- Each agent follows Microsoft STRIDE methodology -- pattern-matching against known threats, not open-ended invention
- **Given** a component classified as External Entity, **when** the DoS agent runs, **then** it does NOT target that component (External Entities are not susceptible to DoS per STRIDE-per-Element)

**Priority**: P0
**Effort**: M

### US-4: Consistent Table Format Output
**When** any STRIDE agent produces findings,
**I want** each finding to follow a consistent table format with ID, Component, Threat, Risk (likelihood + impact), and Mitigation,
**So that** the orchestrator can assemble them into a unified threat model.

**Acceptance Criteria**:
- Each agent outputs findings with fields: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation, References, DFD Element Type
- IDs follow the convention: S-N (Spoofing), T-N (Tampering), R-N (Repudiation), I-N (Information Disclosure), D-N (Denial of Service), E-N (Elevation of Privilege)
- All findings conform to `schemas/finding.yaml`
- Quality guardrail: findings that don't reference specific components from the input are flagged for revision
- Risk levels computed via OWASP 3x3 matrix (likelihood x impact) match expected values

**Priority**: P0
**Effort**: S

---

## Functional Requirements

### FR-1: One Agent Per STRIDE Category
Each of the 6 STRIDE agents analyzes architecture input through exactly one threat lens:

| Agent File | Threat Class | ID Prefix | Security Property Violated |
|-----------|-------------|-----------|---------------------------|
| `spoofing.md` | Spoofing | S-N | Authentication |
| `tampering.md` | Tampering | T-N | Integrity |
| `repudiation.md` | Repudiation | R-N | Non-repudiation |
| `info-disclosure.md` | Information Disclosure | I-N | Confidentiality |
| `denial-of-service.md` | Denial of Service | D-N | Availability |
| `privilege-escalation.md` | Elevation of Privilege | E-N | Authorization |

### FR-2: STRIDE-per-Element Targeting
Each agent targets only the DFD element types assigned by the Microsoft STRIDE-per-Element matrix:

| DFD Element | S | T | R | I | D | E |
|-------------|---|---|---|---|---|---|
| **Processes** | X | X | X | X | X | X |
| **Data Flows** | | X | | X | X | |
| **Data Stores** | | X | | X | X | |
| **External Entities** | X | | X | | | |

Agents MUST NOT produce findings for DFD element types outside their assigned scope.

### FR-3: Component-Specific Findings
Every finding MUST reference a named component from the architecture input. The finding's `component` field must match a component identified in the orchestrator's Phase 1 (Scope) output. Findings with generic component names (e.g., "the system", "the application", "a service") are invalid and must be rejected.

### FR-4: Finding Schema Compliance
All findings conform to the `schemas/finding.yaml` intermediate representation (IR). The IR contains all 10 fields; rendered output tables (e.g., STRIDE tables in `threats.md`) display a subset of 7 columns. The `references` and `dfd_element_type` fields are IR fields used for validation, cross-referencing, and coverage analysis -- they are not necessarily displayed in every output format.

IR fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Sequential with category prefix (S-1, T-1, etc.) |
| `category` | string | STRIDE category name (lowercase) |
| `component` | string | Named component from architecture input |
| `threat` | string | Specific threat description -- what the attacker does and what trust assumption they violate |
| `likelihood` | enum | LOW, MEDIUM, HIGH -- assessed using OWASP factors |
| `impact` | enum | LOW, MEDIUM, HIGH -- assessed using OWASP factors |
| `risk_level` | enum | Note, Low, Medium, High, Critical -- computed from OWASP 3x3 matrix |
| `mitigation` | string | Actionable countermeasure -- specific technology or configuration |
| `references` | array | OWASP, CWE, MITRE ATT&CK, or CVE identifiers |
| `dfd_element_type` | string | DFD classification of the target component |

### FR-5: Risk Level Computation
Risk levels computed from the OWASP 3x3 matrix:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

### FR-6: Framework-Grounded References
Each agent's findings must include references to established security frameworks:
- OWASP Top 10 (2021/2025) for web application context
- OWASP API Security Top 10 (2023) for API-specific patterns
- CWE identifiers for vulnerability classification
- MITRE ATT&CK technique IDs for attack pattern context

### FR-7: Detection Patterns Per Agent
Each agent must include detailed detection patterns organized by attack category:

- **Spoofing**: Authentication bypass, credential theft/replay, session hijacking, service impersonation, federated identity attacks
- **Tampering**: Input injection, data flow manipulation, storage corruption, code/config tampering, API parameter manipulation
- **Repudiation**: Missing audit logging, log integrity gaps, non-repudiation mechanism gaps, timestamp manipulation, accountability gaps
- **Information Disclosure**: Data leakage, excessive exposure, side-channel attacks, error message disclosure, storage access control gaps
- **Denial of Service**: Resource exhaustion, application-layer attacks, infrastructure-layer attacks, algorithmic complexity, cascading failures
- **Elevation of Privilege**: Vertical escalation, horizontal escalation, permission boundary violations, default permission abuse, lateral movement

---

## Non-Functional Requirements

### Prompt Quality
- Agent prompts must be clear enough for any LLM (Claude, GPT-4, Gemini) to follow without ambiguity
- Detection patterns must be specific enough to produce targeted findings, not vague enough to produce generic ones
- Finding templates must be unambiguous -- the output format is deterministic given a component and threat

### Platform Neutrality
- Agents are markdown prompt files, not application code
- No references to specific platforms, IDEs, or invocation frameworks
- Works with any LLM capable of following structured markdown prompts

### Consistency
- All 6 agents follow identical structure: frontmatter, purpose, detection scope, patterns, finding template, risk computation, references
- Frontmatter schema is consistent across all agents (agent_name, category, threat_class, dfd_targets, owasp_references, output_schema)

---

## Success Metrics

### Primary Metrics

**Component Specificity Rate**: 100% of findings reference a named component from input
- **Baseline**: Not yet validated
- **Target**: 100% (zero generic findings)
- **Measurement**: Run all 6 agents against sample input, count findings with/without specific component references

**STRIDE Coverage**: All 6 categories produce at least 1 finding for applicable components
- **Baseline**: Not yet validated
- **Target**: 6/6 categories produce findings
- **Measurement**: Run orchestrator end-to-end, verify each category section in output has findings

**Schema Compliance**: 100% of findings conform to `schemas/finding.yaml`
- **Baseline**: Not yet validated
- **Target**: 100%
- **Measurement**: Validate each finding's fields against schema definition

### Secondary Metrics

**DFD Element Accuracy**: 0 findings produced for DFD element types outside the agent's assigned scope
- **Target**: 0 out-of-scope findings
- **Measurement**: Cross-reference each finding's `dfd_element_type` against the agent's `dfd_targets` frontmatter

---

## Scope & Boundaries

### In Scope (This Feature)

**Must Have (P0)**:
- All 6 STRIDE agent prompt files validated and complete
- Each agent targets correct DFD element types per STRIDE-per-Element matrix
- All findings reference specific components from input architecture
- Consistent finding format across all 6 agents (conforming to `schemas/finding.yaml`)
- End-to-end validation: orchestrator dispatches to agents and assembles valid `threats.md`

**Should Have (P1)**:
- OWASP API Security Top 10 cross-references embedded in relevant agents (Spoofing -> API2, EoP -> API1/API3/API5, DoS -> API4)
- OWASP Top 10 Web cross-references for baseline context (Injection = Tampering, Broken Access Control = EoP)

### Out of Scope (Future Features)

- AI-specific threat agents (F-004 -- separate feature, same agent pattern)
- Deduplication and risk rating refinement across agents (F-005)
- Platform-specific adapters for dispatching agents (F-009)
- Custom threat categories beyond STRIDE
- Agent prompt fine-tuning for specific LLM providers

### Assumptions
- The orchestrator (F-003) correctly parses architecture input and classifies components into DFD element types
- The `schemas/finding.yaml` schema is stable and will not change during this feature
- The sample architecture in `examples/mermaid-agentic-app/input.md` is representative enough for validation

### Constraints

**Technical Constraints**:
- Agents are markdown prompt files only -- no application code, no runtime dependencies
- Output must conform to existing `schemas/finding.yaml` without schema modifications
- Agents must work within the orchestrator's existing dispatch protocol (F-003)

**External Dependencies**:
- F-001 (delivered): Repository skeleton, interface contract, schemas
- F-003 (delivered): Orchestrator with STRIDE agent dispatch logic

---

## Interface Contract

### Produces
- `agents/stride/spoofing.md` -- Spoofing threat agent (validated)
- `agents/stride/tampering.md` -- Tampering threat agent (validated)
- `agents/stride/repudiation.md` -- Repudiation threat agent (validated)
- `agents/stride/info-disclosure.md` -- Information Disclosure threat agent (validated)
- `agents/stride/denial-of-service.md` -- Denial of Service threat agent (validated)
- `agents/stride/privilege-escalation.md` -- Elevation of Privilege threat agent (validated)

### Consumes
- `schemas/finding.yaml` -- Finding output schema
- `schemas/input.yaml` -- Architecture input schema
- `docs/INTERFACE-CONTRACT.md` -- Interface contract specification
- `examples/mermaid-agentic-app/input.md` -- Sample architecture for validation

### Output Format
Each agent produces findings in the `threats.md` STRIDE format:

| ID | Component | Threat | Likelihood | Impact | Risk | Mitigation |
|----|-----------|--------|------------|--------|------|------------|
| S-1 | {Named Component} | {Specific threat description} | HIGH | HIGH | Critical | {Actionable countermeasure} |

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Agent prompts produce generic rather than component-specific findings
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Quality guardrail in each agent requiring component name from input; validation against sample architecture
- **Contingency**: Refine detection patterns with more specific component-targeting instructions

**Risk 2**: LLM variability produces inconsistent output across different models
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Deterministic finding template with strict field definitions; platform-neutral prompt design
- **Contingency**: Add LLM-specific prompt tuning notes (out of scope for this feature, addressed in F-009)

### Dependencies

**Internal Dependencies**:
- **F-001 (delivered)**: Repository skeleton, schemas, interface contract
- **F-003 (delivered)**: Orchestrator dispatch logic and STRIDE-per-Element normalization

**Dependency Graph**:
```
F-001 (Skeleton) ─── delivered
  └─ F-003 (Orchestrator) ─── delivered
       └─ F-005 (STRIDE Agents) ◄── THIS FEATURE
            ├─ F-004 (AI Agents) ─── blocked
            └─ Dedup & Risk Rating (future) ─── blocked
```

---

## Open Questions

- [x] Are the existing agent files (from F-001/F-003) complete or do they need additional content? -- **Answered**: Files have detailed content; this feature validates and ensures end-to-end correctness
- [ ] Should agents produce a minimum number of findings per component, or is quality-only (no minimum) acceptable? -- product-manager -- 2026-03-28
- [ ] Should cross-references between STRIDE categories be noted in findings (e.g., a Spoofing finding that also has Tampering implications)? -- architect -- 2026-03-28

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- Orchestrator PRD: [003-orchestrator-agent-2026-03-21.md](003-orchestrator-agent-2026-03-21.md)

### Technical Documentation
- Interface Contract: [INTERFACE-CONTRACT.md](../../INTERFACE-CONTRACT.md)
- Finding Schema: [schemas/finding.yaml](../../../schemas/finding.yaml)
- Input Schema: [schemas/input.yaml](../../../schemas/input.yaml)
- Output Schema: [schemas/output.yaml](../../../schemas/output.yaml)
- Output Template: [templates/threats.md](../../../templates/threats.md)

### Research & Analysis
- Consumer Guide Research: [CONSUMER_GUIDE_TACHI_RESEARCH.md](../../guides/CONSUMER_GUIDE_TACHI_RESEARCH.md)
  - Section 1: Microsoft STRIDE (original 1999 paper definitions, STRIDE-per-Element matrix)
  - Section 5: OWASP API Security Top 10 (API-specific STRIDE cross-references)
  - Section 9: OWASP Top 10 Web (baseline web risk cross-references)
  - Section 12: Input-to-STRIDE Crosswalk (which STRIDE threats apply per element type)
- Consumer Guide: [CONSUMER_GUIDE_TACHI.md](../../guides/CONSUMER_GUIDE_TACHI.md)

### External Resources
- Microsoft STRIDE: Kohnfelder & Garg, "The Threats to Our Products" (1999)
- Microsoft Threat Modeling Tool: STRIDE-per-Element methodology
- OWASP Threat Modeling Process: https://owasp.org/www-community/Threat_Modeling_Process
- OWASP Risk Rating Methodology (3x3 matrix)
