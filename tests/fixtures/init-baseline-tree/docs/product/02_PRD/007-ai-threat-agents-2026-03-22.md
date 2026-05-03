---
prd:
  number: "007"
  topic: ai-threat-agents
  created: 2026-03-22
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-22, status: approved, notes: "PRD drafted by PM via ~aod-define skill with GitHub Issue #7 user stories and consumer guide research as primary inputs"}
  architect_signoff: {agent: architect, date: 2026-03-22, status: approved_with_concerns, notes: "Technically feasible. 3 findings (1 medium, 2 low) — all addressed: FR-3 keyword model clarified to two-layer dispatch/detection, model-theft DFD targets corrected to [Data Store, Process], LLM04 reference corrected. No blocking issues."}
  techlead_signoff: {agent: team-lead, date: 2026-03-22, status: approved_with_concerns, notes: "Feasible in 1 sprint (90% confidence). Agents are content-complete (134-168 lines each). 3-wave execution strategy (parallel validation, consistency check, end-to-end). 3 low concerns addressed: model-theft DFD target, OWASP reference breadth, dual-dispatch testing. No blockers."}
source:
  idea_id: 7
  story_id: null
---

# AI Threat Agents - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-22
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 1 (Foundation)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Build and validate 5 AI-specific threat agents so that agentic and LLM threats are systematically identified against OWASP frameworks, producing component-specific findings alongside traditional STRIDE analysis.

### Problem Statement
Developers building agentic AI applications face a critical gap: traditional STRIDE threat modeling (delivered in F-005) covers classical security threats but misses AI-specific attack vectors. Prompt injection, tool abuse, data poisoning, model theft, and agent autonomy risks are fundamentally different from Spoofing, Tampering, or Denial of Service — they require dedicated detection patterns grounded in AI-specific OWASP frameworks.

The orchestrator (F-003) already supports AI agent dispatch via keyword-based detection (matching "LLM", "agent", "MCP server", etc. in architecture elements). The 5 AI agent prompt files exist in `agents/ai/` with detection patterns and finding templates. This feature validates, tests, and ensures end-to-end correctness of all 5 agents when invoked by the orchestrator against real architecture input containing AI/LLM/agentic components.

### Proposed Solution
Validate and complete all 5 AI agent prompt files (`agents/ai/*.md`) so each agent:

1. **Analyzes through its assigned threat lens** — prompt injection, data poisoning, model theft (LLM category) or agent autonomy, tool abuse (Agentic category)
2. **Targets correct DFD element types** — per the interface contract's AI extension dispatch rules
3. **Produces component-specific findings** — every finding references a specific component from the input architecture; generic/untargeted threats are rejected
4. **Follows consistent output format** — findings conform to `schemas/finding.yaml` with ID convention (LLM-N for LLM agents, AG-N for Agentic agents)
5. **Includes OWASP reference IDs** — each finding maps to established AI vulnerability catalogs (LLM0x:2025, ASIxx, MCPxx:2025)

Each agent is a **markdown prompt file**, not application code. Agents are platform-neutral and work with any LLM capable of following structured markdown prompts.

**Dispatch model**: When the orchestrator dispatches to an AI agent, it follows that agent's analysis methodology within its own execution context. The orchestrator internalizes each agent's detection patterns and finding template to produce findings for that category. Platform-specific multi-call dispatch is an adapter concern addressed in F-009.

### Success Criteria
- All 5 AI agents produce specific, component-referencing findings when given the sample architecture (`examples/mermaid-agentic-app/input.md`)
- No generic or untargeted threats appear in any agent's output — every finding references a named component from the input
- Each agent's findings conform to `schemas/finding.yaml` with correct ID prefix (LLM-N or AG-N)
- Each agent targets only its assigned DFD element types per the interface contract
- Risk levels are computed correctly using the OWASP 3x3 matrix (likelihood x impact)
- Each finding includes at least one OWASP reference ID (LLM0x:2025, ASIxx, or MCPxx:2025)
- Orchestrator can dispatch to all 5 AI agents and assemble their findings into valid AG and LLM tables in `threats.md`
- AI agents produce empty results for purely traditional architectures with no AI/LLM/agentic components

### Timeline
Target: 1 development sprint (estimated during Team-Lead feasibility review)

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature directly delivers the core value proposition: "First toolkit to natively model AI-specific threat agents alongside traditional STRIDE." The STRIDE agents (F-005) provide the traditional threat layer; the AI agents provide the AI-specific layer. Together they form the complete threat model. Without validated AI agents, the toolkit cannot differentiate from generic STRIDE tools — the AI threat agents are the product's unique selling point.

### Roadmap Fit
**Phase**: Phase 1 (Foundation)
**Dependencies**: F-001 (delivered) — repository skeleton, interface contract, schemas; F-003 (delivered) — orchestrator with AI dispatch logic; F-005 (delivered) — STRIDE agents validated (same pattern)
**Blocks**: Dedup & Risk Rating (future — operates on combined STRIDE+AI findings), F-009 (Platform Adapters — wraps orchestrator+agents for specific platforms)

The AI agents follow the same validated pattern as the STRIDE agents (F-005). This is the final critical path item to complete the core threat modeling capability. Once AI agents are validated, the toolkit can produce complete threat models covering both traditional and AI-specific threats.

---

## Target Users & Personas

### Primary Persona: Security Analyst
- **Role**: Security professional performing threat modeling on agentic AI systems
- **Experience**: Familiar with STRIDE methodology, learning AI-specific threat landscape
- **Goals**: Systematically identify AI-specific threats (prompt injection, tool abuse, agent autonomy) alongside traditional STRIDE threats
- **Pain Points**: No established framework maps AI threats to DFD elements; manual AI threat identification is ad hoc and inconsistent

**Why This Matters to Them**: Each AI agent encodes OWASP AI security expertise into reusable prompts with framework-grounded references (LLM Top 10, Agentic Top 10, MCP Top 10), ensuring complete coverage of AI-specific attack vectors.

### Secondary Persona: AI Agent Developer
- **Role**: Software developer building agentic AI applications
- **Experience**: Proficient in code and AI/ML, new to security threat modeling
- **Goals**: Get a complete threat model that covers both traditional and AI-specific threats without deep security expertise
- **Pain Points**: Knows OWASP Top 10 for web but not the LLM/Agentic/MCP-specific variants; doesn't know what AI-specific threats to look for

**Why This Matters to Them**: The AI agents automate AI-specific threat identification so developers get expert-level findings with OWASP reference IDs they can research and act on.

---

## User Stories

### US-1: Agentic AI Threat Agent
**When** a security analyst provides an architecture diagram containing autonomous AI components to the orchestrator,
**I want** the Agentic AI threat agents (agent-autonomy, tool-abuse) to examine excessive agency, tool/function abuse, insecure plugin execution, agent-to-agent trust boundaries, MCP-specific threats, and multi-agent coordination risks,
**So I can** have threats unique to systems with autonomous AI tool access identified against OWASP Agentic Top 10 (2026) and OWASP MCP Top 10 (2025).

**Acceptance Criteria**:
- **Given** an architecture with an AI orchestrator component, **when** the agent-autonomy agent analyzes it, **then** it produces findings referencing that specific component with AG-prefixed IDs covering excessive autonomy, goal misalignment, and missing human-in-the-loop
- **Given** an architecture with MCP tool servers, **when** the tool-abuse agent analyzes it, **then** it produces findings referencing those components with AG-prefixed IDs covering tool poisoning, unauthorized invocation, and rug pull attacks
- **Given** an architecture with multi-agent communication, **when** the agent-autonomy agent analyzes it, **then** it produces findings about cascading failures and autonomous resource consumption
- Each finding includes OWASP reference IDs (ASIxx for agentic threats, MCPxx:2025 for MCP-specific threats)
- AI agents produce empty results for architectures with no AI/agent/MCP components

**Priority**: P0
**Effort**: M

### US-2: LLM Threat Agent
**When** a security analyst provides an architecture diagram containing LLM integration to the orchestrator,
**I want** the LLM threat agents (prompt-injection, data-poisoning, model-theft) to examine prompt injection vectors, training data integrity, model supply chain, sensitive information disclosure via model output, and unbounded resource consumption,
**So I can** have threats specific to LLM integration identified against OWASP LLM Top 10 v2025.

**Acceptance Criteria**:
- **Given** an architecture with an LLM inference service, **when** the prompt-injection agent analyzes it, **then** it produces findings referencing that specific component with LLM-prefixed IDs covering direct injection, indirect injection, and system prompt leakage
- **Given** an architecture with RAG pipeline and vector databases, **when** the data-poisoning agent analyzes it, **then** it produces findings referencing those components with LLM-prefixed IDs covering training data manipulation, RAG index poisoning, and knowledge base corruption
- **Given** an architecture with model hosting, **when** the model-theft agent analyzes it, **then** it produces findings referencing that component with LLM-prefixed IDs covering model extraction, unbounded consumption, and supply chain risks
- Each finding includes OWASP reference IDs (LLM0x:2025)
- AI agents produce empty results for architectures with no LLM/model components

**Priority**: P0
**Effort**: M

### US-3: OWASP-Referenced Findings with Consistent Format
**When** any AI threat agent produces findings,
**I want** each finding to follow a consistent format with ID, Component, Threat, OWASP Reference, Risk (likelihood + impact), and Mitigation,
**So that** findings map directly to established vulnerability catalogs and the orchestrator can assemble them into unified AG and LLM threat tables.

**Acceptance Criteria**:
- Each agent outputs findings with fields: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation, References (OWASP IDs), DFD Element Type
- Agentic agent IDs follow convention AG-N; LLM agent IDs follow convention LLM-N
- All findings conform to `schemas/finding.yaml`
- Output includes OWASP Reference column in rendered tables (ASI-xx, MCP-xx, or LLM0x:2025)
- Risk levels computed via OWASP 3x3 matrix match expected values
- Quality guardrail: findings that don't reference specific components from the input are flagged for revision

**Priority**: P0
**Effort**: S

---

## Functional Requirements

### FR-1: Five Agents Across Two AI Threat Categories
Each AI agent analyzes architecture input through its assigned threat lens:

| Agent File | Category | Threat Class | ID Prefix | OWASP Framework |
|-----------|----------|-------------|-----------|-----------------|
| `prompt-injection.md` | LLM | Prompt Injection | LLM-N | LLM Top 10 v2025 (LLM01) |
| `data-poisoning.md` | LLM | Data & Model Poisoning | LLM-N | LLM Top 10 v2025 (LLM04) |
| `model-theft.md` | LLM | Model Theft & Abuse | LLM-N | LLM Top 10 v2025 (LLM03, LLM10) |
| `agent-autonomy.md` | Agentic | Agent Autonomy Risks | AG-N | Agentic Top 10 (ASI01, ASI06, ASI08, ASI09, ASI10) |
| `tool-abuse.md` | Agentic | Tool Misuse & Exploitation | AG-N | Agentic Top 10 (ASI02, ASI04), MCP Top 10 (MCP03) |

### FR-2: DFD Element Targeting
Each agent targets DFD element types per the interface contract:

| Agent | Primary DFD Targets | Rationale |
|-------|-------------------|-----------|
| `prompt-injection.md` | Process | LLM inference endpoints are processes receiving user input |
| `data-poisoning.md` | Data Store, Data Flow | Poisoning targets training data stores and data flows feeding models |
| `model-theft.md` | Data Store, Process | Model weights are stored in data stores; inference endpoints are processes exposing model behavior |
| `agent-autonomy.md` | Process | Autonomous agents are processes with decision-making capability |
| `tool-abuse.md` | Process | Tool servers and plugin hosts are processes executing actions |

Agents MUST NOT produce findings for DFD element types outside their assigned scope.

### FR-3: Two-Layer Keyword Dispatch
AI agent activation uses a two-layer keyword model:

**Layer 1 — Orchestrator Dispatch** (which category of agents to activate):
The orchestrator uses interface contract Section 3 keywords to determine which agent categories apply to each architecture element:

- **LLM dispatch keywords**: "LLM", "model", "GPT", "Claude", "language model", "completion", "chat", "inference", "prompt", "generative AI"
  - Activates: prompt-injection, data-poisoning, model-theft agents
- **Agentic dispatch keywords**: "agent", "autonomous", "orchestrator", "MCP server", "tool server", "plugin"
  - Activates: agent-autonomy, tool-abuse agents
- **Dual-dispatch**: Elements matching both LLM and agentic keywords trigger both agent categories

**Layer 2 — Agent Detection Scope** (which components within the category to analyze):
Each agent file defines its own trigger keywords that extend beyond the orchestrator dispatch keywords. These are per-agent refinements for targeted threat detection (e.g., data-poisoning adds "training", "RAG", "vector store"; tool-abuse adds "tool use", "function calling"). Agent-level keywords are documented in each agent's Detection Scope section and do not need to be duplicated in the interface contract.

### FR-4: Component-Specific Findings
Every finding MUST reference a named component from the architecture input. The finding's `component` field must match a component identified in the orchestrator's Phase 1 (Scope) output. Findings with generic component names (e.g., "the system", "the AI", "a model") are invalid and must be rejected.

### FR-5: Finding Schema Compliance
All findings conform to `schemas/finding.yaml` intermediate representation (IR):

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Sequential with category prefix (LLM-1, AG-1, etc.) |
| `category` | string | `llm` or `agentic` |
| `component` | string | Named component from architecture input |
| `threat` | string | Specific threat description — what the attacker does and what trust assumption they violate |
| `likelihood` | enum | LOW, MEDIUM, HIGH — assessed using OWASP factors |
| `impact` | enum | LOW, MEDIUM, HIGH — assessed using OWASP factors |
| `risk_level` | enum | Note, Low, Medium, High, Critical — computed from OWASP 3x3 matrix |
| `mitigation` | string | Actionable countermeasure — specific technology or configuration |
| `references` | array | OWASP LLM/Agentic/MCP IDs, CWE, MITRE ATLAS identifiers |
| `dfd_element_type` | string | DFD classification of the target component |

### FR-6: Risk Level Computation
Risk levels computed from the OWASP 3x3 matrix:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

### FR-7: OWASP Framework References
Each agent's findings must include references to established AI security frameworks:

- **LLM agents**: OWASP LLM Top 10 v2025 (LLM01:2025 through LLM10:2025)
- **Agentic agents**: OWASP Top 10 for Agentic Applications 2026 (ASI01 through ASI10)
- **MCP-related findings**: OWASP MCP Top 10 2025 (MCP01:2025 through MCP10:2025)
- **Cross-references**: CWE identifiers for vulnerability classification, MITRE ATLAS for AI attack taxonomy

### FR-8: Detection Patterns Per Agent
Each agent must include detailed detection patterns organized by attack category:

- **Prompt Injection**: Direct injection, indirect injection (via documents/URLs), jailbreaking, system prompt extraction, cross-plugin injection
- **Data Poisoning**: Training data manipulation, RAG index poisoning, knowledge base corruption, fine-tuning supply chain attacks, context window contamination
- **Model Theft**: Model extraction via API queries, model weight exfiltration, unbounded inference consumption, model supply chain compromise
- **Agent Autonomy**: Excessive autonomy, goal misalignment, unconstrained action scope, missing human-in-the-loop, cascading failures across agents, autonomous resource consumption
- **Tool Abuse**: Unauthorized tool invocation, capability escalation, parameter injection, tool chain manipulation, tool poisoning (direct, shadowing, rug pulls)

### FR-9: Empty Results for Non-AI Architectures
AI agents MUST produce empty results (no findings) when the input architecture contains no AI/LLM/agentic components. This ensures the toolkit doesn't generate false positives for purely traditional systems.

---

## Non-Functional Requirements

### Prompt Quality
- Agent prompts must be clear enough for any LLM (Claude, GPT-4, Gemini) to follow without ambiguity
- Detection patterns must be specific enough to produce targeted findings, not vague enough to produce generic ones
- Finding templates must be unambiguous — the output format is deterministic given a component and threat

### Platform Neutrality
- Agents are markdown prompt files, not application code
- No references to specific platforms, IDEs, or invocation frameworks
- Works with any LLM capable of following structured markdown prompts

### Consistency with STRIDE Agents
- All 5 AI agents follow identical structure to STRIDE agents: frontmatter, purpose, detection scope, patterns, finding template, risk computation, references
- Frontmatter schema is consistent across all agents (agent_name, category, threat_class, dfd_targets, owasp_references, output_schema)

### OWASP Accuracy
- All OWASP reference IDs must use official formats: LLM0x:2025, ASIxx, MCPxx:2025
- Category mappings must align with official OWASP documentation
- Detection patterns must reflect actual OWASP-documented attack vectors, not invented ones

---

## Success Metrics

### Primary Metrics

**Component Specificity Rate**: 100% of findings reference a named component from input
- **Baseline**: Not yet validated
- **Target**: 100% (zero generic findings)
- **Measurement**: Run all 5 agents against sample input, count findings with/without specific component references

**AI Category Coverage**: Both AI categories (AG, LLM) produce at least 1 finding for applicable components
- **Baseline**: Not yet validated
- **Target**: 2/2 categories produce findings for AI architectures; 0/2 for non-AI architectures
- **Measurement**: Run orchestrator end-to-end against agentic architecture, verify both AG and LLM tables have findings

**Schema Compliance**: 100% of findings conform to `schemas/finding.yaml`
- **Baseline**: Not yet validated
- **Target**: 100%
- **Measurement**: Validate each finding's fields against schema definition

### Secondary Metrics

**OWASP Reference Coverage**: Every finding includes at least one OWASP reference ID
- **Target**: 100% of findings include LLM0x:2025, ASIxx, or MCPxx:2025 references
- **Measurement**: Check `references` field in each finding for OWASP ID presence

**DFD Element Accuracy**: 0 findings produced for DFD element types outside the agent's assigned scope
- **Target**: 0 out-of-scope findings
- **Measurement**: Cross-reference each finding's `dfd_element_type` against the agent's `dfd_targets` frontmatter

---

## Scope & Boundaries

### In Scope (This Feature)

**Must Have (P0)**:
- All 5 AI agent prompt files validated and complete
- Each agent targets correct DFD element types per interface contract
- All findings reference specific components from input architecture
- Consistent finding format across all 5 agents (conforming to `schemas/finding.yaml`)
- OWASP reference IDs in every finding (LLM0x:2025, ASIxx, MCPxx:2025)
- End-to-end validation: orchestrator dispatches to AI agents and assembles valid AG and LLM tables in `threats.md`
- Empty results for non-AI architectures

**Should Have (P1)**:
- MITRE ATLAS cross-references for AI attack taxonomy
- CWE identifiers for vulnerability classification where applicable

### Out of Scope (Future Features)

- Deduplication and risk rating refinement across STRIDE + AI findings (future feature)
- Platform-specific adapters for dispatching agents (F-009)
- Custom AI threat categories beyond OWASP frameworks
- Agent prompt fine-tuning for specific LLM providers
- Additional AI agent categories (e.g., multimodal threats, embedding attacks)

### Assumptions
- The orchestrator (F-003) correctly parses architecture input and dispatches to AI agents based on keyword detection
- The `schemas/finding.yaml` schema supports AI categories (`llm`, `agentic`) and ID prefixes (`LLM-N`, `AG-N`)
- The sample architecture in `examples/mermaid-agentic-app/input.md` contains sufficient AI/LLM/agentic components for validation
- STRIDE agents (F-005) are delivered and stable — AI agents follow the same validated pattern

### Constraints

**Technical Constraints**:
- Agents are markdown prompt files only — no application code, no runtime dependencies
- Output must conform to existing `schemas/finding.yaml` without schema modifications
- Agents must work within the orchestrator's existing dispatch protocol (F-003)
- AI agents must coexist with STRIDE agents — no conflicts in finding ID namespaces

**External Dependencies**:
- F-001 (delivered): Repository skeleton, interface contract, schemas
- F-003 (delivered): Orchestrator with AI agent dispatch logic
- F-005 (delivered): STRIDE agents (same pattern, validated)

---

## Interface Contract

### Produces
- `agents/ai/prompt-injection.md` — Prompt Injection threat agent (validated)
- `agents/ai/data-poisoning.md` — Data & Model Poisoning threat agent (validated)
- `agents/ai/model-theft.md` — Model Theft & Abuse threat agent (validated)
- `agents/ai/agent-autonomy.md` — Agent Autonomy threat agent (validated)
- `agents/ai/tool-abuse.md` — Tool Misuse & Exploitation threat agent (validated)

### Consumes
- `schemas/finding.yaml` — Finding output schema
- `schemas/input.yaml` — Architecture input schema
- `docs/INTERFACE-CONTRACT.md` — Interface contract specification (Section 3: AI Extension Dispatch Rules)
- `examples/mermaid-agentic-app/input.md` — Sample architecture for validation

### Output Format
AI agents produce findings in two output tables:

**Agentic Threats (AG)**:

| ID | Component | Threat | OWASP Ref | Likelihood | Impact | Risk | Mitigation |
|----|-----------|--------|-----------|------------|--------|------|------------|
| AG-1 | {Named Component} | {Specific threat} | ASI-01 | HIGH | HIGH | Critical | {Actionable countermeasure} |

**LLM Threats (LLM)**:

| ID | Component | Threat | OWASP Ref | Likelihood | Impact | Risk | Mitigation |
|----|-----------|--------|-----------|------------|--------|------|------------|
| LLM-1 | {Named Component} | {Specific threat} | LLM01:2025 | HIGH | HIGH | Critical | {Actionable countermeasure} |

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Agent prompts produce generic rather than component-specific findings
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Quality guardrail in each agent requiring component name from input; validation against sample architecture; same guardrail pattern validated in F-005
- **Contingency**: Refine detection patterns with more specific component-targeting instructions

**Risk 2**: OWASP framework mappings become outdated
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Pin to specific versions (LLM Top 10 v2025, Agentic Top 10 2026, MCP Top 10 v0.1 Beta); document update process
- **Contingency**: Version lock references; update agents when new OWASP versions are published

**Risk 3**: Overlap between AI agents and STRIDE agents produces duplicate findings
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Clear scope boundaries per agent; deduplication is a future feature operating on combined output
- **Contingency**: Accept minor overlap in initial release; dedup feature will resolve

### Dependencies

**Internal Dependencies**:
- **F-001 (delivered)**: Repository skeleton, schemas, interface contract
- **F-003 (delivered)**: Orchestrator AI dispatch logic and keyword detection
- **F-005 (delivered)**: STRIDE agents — validates the agent pattern this feature follows

**Dependency Graph**:
```
F-001 (Skeleton) ─── delivered
  └─ F-003 (Orchestrator) ─── delivered
       ├─ F-005 (STRIDE Agents) ─── delivered
       └─ F-007 (AI Threat Agents) ◄── THIS FEATURE
            └─ Dedup & Risk Rating (future) ─── blocked
```

---

## Open Questions

- [ ] Should AI agents detect threats in non-AI components that interact with AI (e.g., a database storing model outputs)? — architect — 2026-03-29
- [ ] Should cross-references between AI and STRIDE categories be noted in findings (e.g., a prompt injection finding that also has Tampering implications)? — architect — 2026-03-29
- [ ] What is the minimum number of OWASP references per finding — 1 or should agents aim for comprehensive cross-referencing? — product-manager — 2026-03-29

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- STRIDE Agents PRD: [005-stride-threat-agents-2026-03-21.md](005-stride-threat-agents-2026-03-21.md)
- Orchestrator PRD: [003-orchestrator-agent-2026-03-21.md](003-orchestrator-agent-2026-03-21.md)

### Technical Documentation
- Interface Contract: [INTERFACE-CONTRACT.md](../../INTERFACE-CONTRACT.md) (Section 3: AI Extension Dispatch Rules)
- Finding Schema: [schemas/finding.yaml](../../../schemas/finding.yaml)
- Input Schema: [schemas/input.yaml](../../../schemas/input.yaml)
- Output Schema: [schemas/output.yaml](../../../schemas/output.yaml)
- Output Template: [templates/threats.md](../../../templates/threats.md)

### Research & Analysis
- Consumer Guide Research: [CONSUMER_GUIDE_TACHI_RESEARCH.md](../../guides/CONSUMER_GUIDE_TACHI_RESEARCH.md)
  - Section 2: OWASP Top 10 for LLM Applications v2025 (LLM01-LLM10)
  - Section 3: OWASP Top 10 for Agentic Applications 2026 (ASI01-ASI10)
  - Section 4: OWASP MCP Top 10 2025 (MCP01-MCP10)
  - Section 13: Consumer Guide Corrections (ID format, coverage gaps)
- Consumer Guide: [CONSUMER_GUIDE_TACHI.md](../../guides/CONSUMER_GUIDE_TACHI.md)

### External Resources
- OWASP Top 10 for LLM Applications v2025: https://genai.owasp.org/llm-top-10/
- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/agentic-top-10/
- OWASP MCP Top 10 2025: https://owasp.org/www-project-model-context-protocol-top-10/
- MITRE ATLAS (Adversarial Threat Landscape for AI Systems): https://atlas.mitre.org/
