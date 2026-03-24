---
prd:
  number: "024"
  topic: example-threat-models
  created: 2026-03-23
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-23, status: Approved, notes: "PRD authored and revised per Triad feedback"}
  architect_signoff: {agent: architect, date: 2026-03-23, status: Approved with Concerns, notes: "Schema v1.1 migration and OWASP cross-ref mechanism addressed in v1.1; defer to spec phase for details"}
  techlead_signoff: {agent: team-lead, date: 2026-03-23, status: Approved with Concerns, notes: "Wave strategy and effort variance incorporated in v1.1; 2.5-day realistic timeline at 75% confidence"}
source:
  idea_id: 24
  story_id: null
---

# Example Threat Models - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-23
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
End-to-end example threat models for three common architecture types, demonstrating tachi's value across AI and non-AI systems.

### Problem Statement
New users evaluating tachi have no way to see what the toolkit produces without running it themselves. There is no "before and after" demonstration showing an architecture input alongside the generated threat model output. This creates a high trial barrier — users must invest time setting up and running tachi before they can assess whether it meets their needs.

### Current State
Three example directories exist (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) but they were created as internal test fixtures during development. They lack:
- Standardized naming and structure for external consumption
- Cross-references to OWASP frameworks (Top 10 Web 2025, Agentic Top 10, MCP Top 10)
- A README explaining the framework relationship hierarchy and how examples demonstrate coverage
- Consistent Mermaid diagram format across all examples

### Proposed Solution
Create three polished, externally-facing example threat models with standardized structure:

1. **Web Application** — Traditional STRIDE-only architecture demonstrating full coverage on a non-AI system (AI agents produce empty results)
2. **Agentic Application** — LLM + MCP + multi-agent architecture demonstrating the unique value of AI-specific threat agents (OWASP Agentic Top 10, MCP Top 10)
3. **Microservices** — Multi-service architecture demonstrating cross-service threat analysis and trust boundary coverage at scale

Each example includes a Mermaid architecture diagram (input) and a complete generated threat model (output).

### Success Criteria
- All 3 examples contain valid Mermaid architecture diagrams and complete threat model outputs matching the output template
- Web app example cross-references OWASP Top 10 Web 2025 (A01–A10)
- Agentic app example demonstrates OWASP Agentic Top 10 (ASI01–ASI10) and MCP Top 10 (MCP01–MCP10) coverage
- Examples are referenced from the project README
- Examples README documents the framework relationship hierarchy (per research §13.6)

### Timeline
- **Single Sprint** (~2.5 days realistic): 4-wave build strategy accounting for within-example dependencies

| Wave | Tasks | Duration |
|------|-------|----------|
| 1 | Directory scaffold + Mermaid diagrams (all 3 parallel) | 0.5 days |
| 2 | Threat model enrichment: schema v1.1, OWASP cross-refs (all 3 parallel) | 1–1.5 days |
| 3 | Examples README + Project README update | 0.5 days |
| 4 | Quality validation | 0.5 days |

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Examples directly support the vision of becoming "the default threat modeling toolkit for any team building agentic AI applications." Users evaluating the toolkit need to see concrete output before committing. The agentic app example specifically demonstrates the core value proposition — AI-specific threat agents alongside traditional STRIDE — without requiring users to install or run anything.

### Roadmap Fit
**Phase**: Polish (per Consumer Guide sequencing)
**Dependencies**: All core features delivered (F-001 through F-021)

---

## Target Users & Personas

### Primary Persona: Evaluating Developer
- **Role**: Developer or architect evaluating tachi for their project
- **Experience**: Familiar with threat modeling concepts but new to tachi
- **Goals**: Quickly understand what tachi produces and whether it's worth adopting
- **Pain Points**: Must run the full toolkit to see output; no way to preview results

### Secondary Persona: New User Following Tutorial
- **Role**: Developer who has decided to use tachi and is learning how
- **Experience**: First-time tachi user
- **Goals**: See a complete input→output example to understand the expected workflow
- **Pain Points**: No reference implementation to compare their own results against

### Tertiary Persona: Platform Engineer
- **Role**: Engineer responsible for multi-service architectures
- **Experience**: Deep infrastructure knowledge, may be new to AI threat modeling
- **Goals**: See how tachi handles complex architectures with many trust boundaries
- **Pain Points**: Unclear whether tachi scales to real-world service topologies

---

## User Stories

### US-001: Web Application Example
**When** I'm evaluating tachi for a traditional web application,
**I want to** see a complete threat model for a typical web app architecture,
**So I can** understand what tachi produces for non-AI systems before running it on my own.

**Acceptance Criteria**:
- **Given** `examples/web-app/architecture.md`, **when** I read it, **then** it contains a valid Mermaid diagram of a typical web app (frontend, API, database, auth service)
- **Given** `examples/web-app/threats.md`, **when** I read it, **then** it contains a complete threat model with all 6 STRIDE categories populated
- **Given** the web app has no AI components, **when** I examine `threats.md`, **then** AI threat agent sections show "No AI components detected" (empty results, not omitted)
- **Given** the threats, **when** I cross-reference OWASP Top 10 Web 2025, **then** findings map to relevant A01–A10 categories

**Priority**: P0
**Effort**: M

### US-002: Agentic Application Example
**When** I'm an AI developer evaluating tachi's unique value,
**I want to** see a threat model that includes AI-specific findings,
**So I can** understand how tachi's +AI agents add value beyond standard STRIDE.

**Acceptance Criteria**:
- **Given** `examples/agentic-app/architecture.md`, **when** I read it, **then** it contains a valid Mermaid diagram of an agentic app (LLM, MCP servers, tool access, multi-agent orchestration)
- **Given** `examples/agentic-app/threats.md`, **when** I read it, **then** it contains findings from both STRIDE and AI threat agents
- **Given** the AI findings, **when** I cross-reference OWASP Agentic Top 10, **then** findings map to relevant ASI01–ASI10 categories
- **Given** the AI findings, **when** I cross-reference OWASP MCP Top 10, **then** findings map to relevant MCP01–MCP10 categories
- **Given** the example, **when** compared to the web-app example, **then** the additional AI-specific findings clearly demonstrate tachi's unique value

**Priority**: P0
**Effort**: M

### US-003: Microservices Example
**When** I'm a platform engineer evaluating tachi for complex architectures,
**I want to** see a threat model for a multi-service system with many trust boundaries,
**So I can** see how tachi handles cross-service threats and scales to real-world topologies.

**Acceptance Criteria**:
- **Given** `examples/microservices/architecture.md`, **when** I read it, **then** it contains a valid Mermaid diagram of a microservices system (API gateway, services, message queue, databases)
- **Given** `examples/microservices/threats.md`, **when** I read it, **then** it contains cross-service threat findings and trust boundary analysis
- **Given** the coverage matrix in `threats.md`, **when** I examine it, **then** it shows meaningful coverage across many components and service boundaries

**Priority**: P0
**Effort**: L (free-text-to-Mermaid conversion + more components = ~1.5x effort of US-001/US-002)

---

## Functional Requirements

### FR-001: Standardized Example Directory Structure
Each example lives in `examples/{example-name}/` with a consistent structure:

```
examples/
├── README.md                    # Overview, framework hierarchy, how to use examples
├── web-app/
│   ├── architecture.md          # Mermaid diagram input
│   └── threats.md               # Complete generated threat model output
├── agentic-app/
│   ├── architecture.md          # Mermaid diagram input
│   └── threats.md               # Complete generated threat model output
└── microservices/
    ├── architecture.md          # Mermaid diagram input
    └── threats.md               # Complete generated threat model output
```

### FR-002: Mermaid Architecture Diagrams
All three `architecture.md` files MUST contain:
- Valid Mermaid diagram syntax (flowchart or C4 notation)
- Clearly labeled components with roles (e.g., "API Gateway", "Auth Service", "LLM Agent")
- Trust boundary notation where applicable
- Data flow arrows showing communication patterns
- Enough complexity to trigger meaningful threat findings (minimum 4 components per diagram)

### FR-003: Complete Threat Model Outputs
All three `threats.md` files MUST contain:
- Output matching the tachi output template (per `schemas/output.yaml`) at **schema version 1.1** (including Section 4a: Correlated Findings)
- Coverage matrix showing which agents produced findings for which components
- Risk-rated findings with severity levels
- Mitigation recommendations for each finding
- Deduplication applied (no duplicate findings across agents)

**Note**: Existing examples use schema_version 1.0. Migration to v1.1 (adding Correlated Findings section) is a required subtask for all three examples.

### FR-004: OWASP Framework Cross-References
- **Web app**: Findings reference OWASP Top 10 Web 2025 categories (A01–A10) where applicable
- **Agentic app**: AI findings reference OWASP Agentic Top 10 (ASI01–ASI10) and OWASP MCP Top 10 (MCP01–MCP10)
- **Microservices**: Findings reference OWASP Top 10 Web 2025 where applicable

**Cross-reference mechanism**: OWASP mappings should be implemented as an appendix mapping table within each `threats.md` (not as schema field additions to `output.yaml`). This avoids impacting all tachi outputs globally while still demonstrating framework coverage in examples. Exact format to be defined in spec phase.

### FR-005: Examples README
`examples/README.md` MUST include:
- Overview of the three examples and their purpose
- Framework relationship hierarchy diagram (per research §13.6) showing how STRIDE, OWASP Top 10, Agentic Top 10, and MCP Top 10 relate
- Table mapping each example to the threat frameworks it exercises
- Instructions for using examples as reference when running tachi on your own architecture

### FR-006: Existing Example Migration
The three existing example directories (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) will be evaluated during spec phase:
- Determine whether existing content can be adapted or whether fresh examples are needed
- Existing examples may be retained as additional format-specific test fixtures or removed if superseded
- Migration strategy to be defined in spec.md

---

## Non-Functional Requirements

### Readability
- Architecture diagrams should be understandable by developers without security expertise
- Threat model outputs should be scannable — findings organized by severity, then by component
- Examples serve as documentation — prioritize clarity over comprehensiveness

### Accuracy
- All OWASP cross-references must cite correct category IDs (A01, ASI01, MCP01, etc.)
- AI threat agent sections in the web-app example must correctly show empty results (demonstrating that AI agents are selective, not omnipresent)
- Risk ratings must be consistent with the severity rubric used by tachi's agents

### Maintainability
- Examples use the same output template as actual tachi runs — when the template changes, examples should be regenerated
- Architecture diagrams use standard Mermaid syntax for broad rendering compatibility

---

## Success Metrics

### Primary Metrics
- **Completeness**: All 3 examples contain valid architecture diagrams and complete threat model outputs
- **OWASP coverage**: Web app maps to A01–A10; agentic app maps to ASI01–ASI10 and MCP01–MCP10
- **Framework hierarchy**: README documents the relationship between all referenced frameworks

### Adoption Metrics
- **README reference**: Project README links to examples directory
- **User comprehension**: Examples are self-explanatory without requiring additional documentation

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Three example directories with standardized structure (`web-app`, `agentic-app`, `microservices`)
- Mermaid architecture diagrams for all three examples
- Complete threat model outputs for all three examples
- OWASP framework cross-references in findings
- Updated examples README with framework relationship hierarchy
- Project README updated to reference examples

### Out of Scope
- Automated example generation or regeneration pipeline
- Examples for other input formats (ASCII, free-text, PlantUML, C4) — existing format-specific examples remain as-is
- Interactive examples or web-based viewers
- Video walkthroughs or tutorials
- Attack tree or threat report outputs for all examples (only the agentic-app example currently has these)

### Assumptions
- Tachi's output template and agent behavior are stable (all core features delivered)
- Mermaid syntax renders correctly in GitHub markdown preview
- OWASP framework categories (Top 10 2025, Agentic Top 10, MCP Top 10) are stable

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Existing examples may not map cleanly to the new structure
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Evaluate during spec phase; create fresh examples if adaptation is more work than starting from scratch

**Risk 2**: OWASP framework cross-references may become outdated
- **Likelihood**: Low (frameworks are versioned and stable)
- **Impact**: Medium
- **Mitigation**: Pin references to specific framework versions (e.g., "OWASP Top 10 Web 2025")

### Dependencies

**Internal Dependencies**:
- **F-001 (Project Skeleton)**: Output template, schemas — Delivered
- **F-003 (Orchestrator)**: Agent dispatch for generating outputs — Delivered
- **F-005 (STRIDE Agents)**: Core STRIDE threat analysis — Delivered
- **F-007 (AI Agents)**: AI-specific threat analysis — Delivered
- **F-010 (Deduplication)**: Deduplicated findings in output — Delivered

**Dependency Graph**:
```
[F-024 Example Threat Models]
  ├── Depends on: F-001 (Project Skeleton) ✅ Delivered
  ├── Depends on: F-003 (Orchestrator) ✅ Delivered
  ├── Depends on: F-005 (STRIDE Agents) ✅ Delivered
  ├── Depends on: F-007 (AI Agents) ✅ Delivered
  └── Depends on: F-010 (Deduplication) ✅ Delivered
```

---

## Open Questions

- [ ] Should existing examples (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) be retained alongside the new standardized examples or replaced? — architect — MEDIUM priority
- [ ] Should the agentic-app example include attack trees and threat report outputs (like the current `mermaid-agentic-app`) or keep to the minimal `architecture.md` + `threats.md` structure? — product-manager — LOW priority

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- Consumer Guide: [CONSUMER_GUIDE_TACHI.md](docs/guides/CONSUMER_GUIDE_TACHI.md)
- Research: [CONSUMER_GUIDE_TACHI_RESEARCH.md](docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md) (§3, §4, §9, §12, §13.6)

### Technical Documentation
- Interface Contract: [INTERFACE-CONTRACT.md](docs/INTERFACE-CONTRACT.md)
- Output Schema: [schemas/output.yaml](schemas/output.yaml)

### Source
- GitHub Issue: #24 (Example Threat Models)
- ICE Score: Impact 8, Confidence 7, Effort 7 = 22

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Comments |
|------|-------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-03-23 | PRD authored and revised per Triad feedback |
| Architect | architect | Approved w/ Concerns | 2026-03-23 | Schema v1.1 migration + OWASP cross-ref mechanism addressed in v1.1 |
| Team Lead | team-lead | Approved w/ Concerns | 2026-03-23 | Wave strategy and effort variance incorporated in v1.1 |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-23 | product-manager | Initial PRD |
| 1.1 | 2026-03-23 | product-manager | Address Architect + Team-Lead review: add schema v1.1 migration requirement (FR-003), OWASP cross-ref mechanism (FR-004), wave build strategy, adjust US-003 effort to L |
