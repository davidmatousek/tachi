---
prd_reference: docs/product/02_PRD/024-example-threat-models-2026-03-23.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 6 PRD functional requirements covered (expanded to 12 spec FRs), all 3 user stories covered with 2 additional, 8 measurable success criteria, both open questions resolved, no scope creep, clean WHAT/WHY separation"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Example Threat Models

**Feature Branch**: `024-example-threat-models`
**Created**: 2026-03-23
**Status**: Draft
**Input**: PRD 024 — Example Threat Models

## User Scenarios & Testing

### User Story 1 — Evaluating Developer Views Web App Example (Priority: P1)

A developer evaluating tachi for a traditional web application opens `examples/web-app/` and reads the architecture diagram and threat model output side by side. They see a familiar architecture (frontend, API, database, auth) analyzed with STRIDE, understand the output format, and confirm that AI threat sections correctly show "No AI components detected" rather than being omitted.

**Why this priority**: The web-app example is the simplest and most universally relatable architecture. It establishes the baseline output format and demonstrates that tachi works for non-AI systems — critical for broadening adoption beyond the AI-security niche.

**Independent Test**: Open `examples/web-app/architecture.md` in any Mermaid renderer, confirm it renders a valid diagram. Open `examples/web-app/threats.md`, confirm it has all required sections per schema v1.1 including Section 4a, STRIDE findings are populated, and AI sections show empty results.

**Acceptance Scenarios**:

1. **Given** `examples/web-app/architecture.md`, **When** a user reads it, **Then** it contains a valid Mermaid flowchart with at least 4 components (frontend, API gateway, auth service, database), trust boundary subgraphs, and labeled data flow arrows.
2. **Given** `examples/web-app/threats.md`, **When** a user reads it, **Then** it contains all 7+1 sections per schema v1.1, with all 6 STRIDE categories populated with findings.
3. **Given** the web app has no AI components, **When** a user examines the AI Threat Tables, **Then** both AG and LLM sections show "No AI components detected" with empty tables.
4. **Given** the web app threats, **When** a user checks the Correlated Findings section, **Then** it shows "No cross-agent correlations detected" (no AI findings to correlate).
5. **Given** the web app threats, **When** a user reads the OWASP appendix, **Then** findings are mapped to OWASP Top 10 Web 2025 categories (A01–A10) with category names.

---

### User Story 2 — AI Developer Views Agentic App Example (Priority: P1)

An AI developer evaluating tachi's unique value opens `examples/agentic-app/` and sees a multi-agent architecture with LLM, MCP servers, and tool access. The threat model shows both STRIDE findings and AI-specific findings (AG, LLM), with correlated findings demonstrating cross-agent analysis. OWASP Agentic Top 10 and MCP Top 10 cross-references prove framework coverage.

**Why this priority**: This example demonstrates tachi's core differentiator — AI-specific threat agents alongside traditional STRIDE. Without it, evaluators cannot see the unique value proposition.

**Independent Test**: Open `examples/agentic-app/architecture.md` in a Mermaid renderer, confirm dual-dispatch triggers are present. Open `threats.md`, confirm STRIDE + AI findings + correlated findings + OWASP cross-references are all present and internally consistent.

**Acceptance Scenarios**:

1. **Given** `examples/agentic-app/architecture.md`, **When** a user reads it, **Then** it contains a valid Mermaid flowchart with LLM, MCP server, tool access, and multi-agent orchestration components, with trust boundary subgraphs.
2. **Given** `examples/agentic-app/threats.md`, **When** a user reads it, **Then** it contains findings from all 6 STRIDE categories plus both AG and LLM threat agent categories.
3. **Given** the AI findings, **When** a user reads the OWASP appendix, **Then** AG findings map to OWASP Agentic Top 10 (ASI01–ASI10) categories and MCP-related findings map to OWASP MCP Top 10 (MCP01–MCP10) categories.
4. **Given** the agentic app has both STRIDE and AI findings, **When** a user reads Section 4a, **Then** correlated findings groups are present showing cross-agent threat correlations (e.g., Tampering + Data-Poisoning on the same component).
5. **Given** the coverage matrix, **When** a user examines it, **Then** it uses deduplicated counts with a footnote explaining correlation group merging.

---

### User Story 3 — Platform Engineer Views Microservices Example (Priority: P1)

A platform engineer evaluating tachi for complex architectures opens `examples/microservices/` and sees a multi-service system with API gateway, services, message queues, and databases. The threat model shows cross-service threat analysis covering trust boundaries between services, demonstrating that tachi scales to real-world topologies.

**Why this priority**: This example addresses the "does it scale?" question from platform engineers. Multi-service architectures are the most common real-world deployment pattern, and showing cross-boundary analysis at scale is essential for credibility.

**Independent Test**: Open `examples/microservices/architecture.md` in a Mermaid renderer, confirm it shows a realistic multi-service topology. Open `threats.md`, confirm cross-service findings and trust boundary analysis cover the full component set.

**Acceptance Scenarios**:

1. **Given** `examples/microservices/architecture.md`, **When** a user reads it, **Then** it contains a valid Mermaid flowchart with at least 6 components including API gateway, multiple services, a message queue, and databases, with trust boundary subgraphs.
2. **Given** `examples/microservices/threats.md`, **When** a user reads it, **Then** it contains cross-service threat findings covering service-to-service authentication, message queue security, and gateway-level protections.
3. **Given** the coverage matrix, **When** a user examines it, **Then** it shows meaningful coverage across many components and service boundaries, with appropriate `n/a` cells per STRIDE-per-Element rules.
4. **Given** the microservices have no AI components, **When** a user examines the AI Threat Tables, **Then** both AG and LLM sections show "No AI components detected."
5. **Given** the microservices threats, **When** a user reads the OWASP appendix, **Then** findings are mapped to OWASP Top 10 Web 2025 categories where applicable.

---

### User Story 4 — Examples README and Framework Hierarchy (Priority: P2)

A user navigating to `examples/README.md` sees an overview of all three examples, a framework relationship hierarchy diagram showing how STRIDE relates to OWASP Top 10, Agentic Top 10, and MCP Top 10, and a table mapping each example to the frameworks it exercises.

**Why this priority**: The README provides orientation and educational context. Without it, users must figure out the framework relationships on their own. However, individual examples are independently useful without it.

**Independent Test**: Open `examples/README.md`, confirm the framework hierarchy diagram renders in GitHub markdown, the example-to-framework mapping table is complete, and usage instructions are present.

**Acceptance Scenarios**:

1. **Given** `examples/README.md`, **When** a user reads it, **Then** it contains an overview describing the purpose of the three examples.
2. **Given** the README, **When** a user views the framework hierarchy, **Then** it shows a diagram or structured description of how STRIDE, OWASP Top 10 Web 2025, OWASP Agentic Top 10, and OWASP MCP Top 10 relate to each other.
3. **Given** the README, **When** a user reads the mapping table, **Then** each example row lists which threat frameworks that example exercises (web-app: STRIDE + OWASP Web; agentic-app: STRIDE + OWASP Web + Agentic + MCP; microservices: STRIDE + OWASP Web).
4. **Given** the README, **When** a user reads the usage instructions, **Then** they explain how to use examples as reference when running tachi on their own architecture.

---

### User Story 5 — Project README References Examples (Priority: P2)

The project README links to the examples directory so that new users discover them during initial evaluation.

**Why this priority**: Discoverability. If users cannot find the examples from the main README, the examples fail their primary purpose. However, this is a small documentation update, not core content.

**Independent Test**: Open `README.md` at the project root, confirm it links to `examples/` and briefly describes what users will find there.

**Acceptance Scenarios**:

1. **Given** the project `README.md`, **When** a user reads the examples section, **Then** it links to `examples/README.md` and describes the three example architectures available.

---

### Edge Cases

- What happens when a Mermaid renderer does not support subgraph notation? All diagrams use standard Mermaid `flowchart` syntax compatible with GitHub's built-in Mermaid renderer.
- What if an OWASP framework version is superseded? All OWASP references are pinned to specific versions (Top 10 Web 2025, Agentic Top 10 2026, MCP Top 10 2025) to avoid ambiguity.
- What if a user expects the examples to be runnable through tachi? The examples README clarifies that these are reference outputs, not generated on-the-fly. Users can run tachi on the `architecture.md` files to compare their results against the reference `threats.md`.

## Requirements

### Functional Requirements

- **FR-001**: Each example MUST live in a standardized directory (`examples/web-app/`, `examples/agentic-app/`, `examples/microservices/`) containing exactly two files: `architecture.md` (Mermaid diagram input) and `threats.md` (complete threat model output).

- **FR-002**: All `architecture.md` files MUST contain valid Mermaid `flowchart` syntax that renders correctly in GitHub's built-in Mermaid renderer, with clearly labeled components, trust boundary subgraphs, and labeled data flow arrows. Each diagram MUST have a minimum of 4 components.

- **FR-003**: All `threats.md` files MUST conform to output schema v1.1, including all 7 required sections plus Section 4a (Correlated Findings). YAML frontmatter MUST include `schema_version: "1.1"`.

- **FR-004**: The web-app `threats.md` MUST have all 6 STRIDE categories populated with findings. AI Threat Tables (AG and LLM) MUST show "No AI components detected" with empty tables — present but empty, not omitted.

- **FR-005**: The agentic-app `threats.md` MUST include findings from all 6 STRIDE categories plus both AG and LLM threat agent categories. Section 4a MUST contain at least one correlated findings group demonstrating cross-agent analysis.

- **FR-006**: The microservices `threats.md` MUST include cross-service threat findings covering trust boundaries between services. The coverage matrix MUST show analysis across at least 6 components.

- **FR-007**: Each `threats.md` MUST include an OWASP Framework Cross-Reference appendix as a mapping table. The web-app and microservices appendices map findings to OWASP Top 10 Web 2025 (A01–A10). The agentic-app appendix maps findings to OWASP Agentic Top 10 (ASI01–ASI10) and OWASP MCP Top 10 (MCP01–MCP10) in addition to OWASP Top 10 Web 2025.

- **FR-008**: `examples/README.md` MUST include: (a) an overview of the three examples and their purpose, (b) a framework relationship hierarchy showing how STRIDE, OWASP Top 10, Agentic Top 10, and MCP Top 10 relate, (c) a table mapping each example to the frameworks it exercises, and (d) usage instructions for running tachi against the example architectures.

- **FR-009**: The project `README.md` MUST reference the examples directory with a brief description of what users will find.

- **FR-010**: The three existing example directories (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) MUST be retained as format-specific test fixtures. They validate that tachi handles ASCII and free-text input formats correctly and are not replaced by the new standardized examples.

- **FR-011**: All finding risk levels MUST be computed using the OWASP 3x3 risk calibration matrix (Likelihood: LOW/MEDIUM/HIGH x Impact: LOW/MEDIUM/HIGH). Risk levels MUST be internally consistent — no finding may have a risk level that contradicts its likelihood and impact values.

- **FR-012**: Coverage matrices MUST use the three-state cell model: integer count (findings present), `---` (analyzed, clean), `n/a` (not applicable per STRIDE-per-Element rules). STRIDE-per-Element dispatch rules MUST be applied correctly (External Entity: S, R only; Process: all six; Data Store: T, I, D; Data Flow: T, I, D).

### Key Entities

- **Example**: A self-contained directory with an architecture diagram input and threat model output, targeting a specific architecture type.
- **Architecture Diagram**: A Mermaid flowchart describing system components, trust boundaries, and data flows — the input that tachi analyzes.
- **Threat Model Output**: A structured document conforming to schema v1.1 with STRIDE findings, AI findings, correlated findings, coverage matrix, risk summary, and recommended actions.
- **OWASP Cross-Reference Appendix**: A mapping table added to each `threats.md` linking finding IDs to OWASP framework categories — not a schema addition, but an example-specific supplement.
- **Framework Relationship Hierarchy**: A diagram or structured description showing how STRIDE (methodology) relates to OWASP classification frameworks (Top 10 Web, Agentic Top 10, MCP Top 10).

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 3 examples contain valid Mermaid architecture diagrams that render correctly in GitHub's Mermaid renderer and complete threat model outputs conforming to schema v1.1.
- **SC-002**: The web-app example maps at least 5 distinct OWASP Top 10 Web 2025 categories (A01–A10) in its cross-reference appendix.
- **SC-003**: The agentic-app example demonstrates at least 3 OWASP Agentic Top 10 categories (ASI01–ASI10) and at least 2 OWASP MCP Top 10 categories (MCP01–MCP10) in its cross-reference appendix.
- **SC-004**: The agentic-app example contains at least 1 correlated findings group in Section 4a, demonstrating cross-agent analysis.
- **SC-005**: The microservices example coverage matrix shows analysis across at least 6 components with meaningful cross-service findings.
- **SC-006**: `examples/README.md` documents the framework relationship hierarchy and maps all 3 examples to the frameworks they exercise.
- **SC-007**: The project `README.md` links to the examples directory.
- **SC-008**: All 3 existing example directories remain intact as format-specific test fixtures.

### Assumptions

- Mermaid syntax renders correctly in GitHub's built-in renderer (standard `flowchart` syntax used by the existing `mermaid-agentic-app` example).
- OWASP framework versions are stable: Top 10 Web 2025, Agentic Top 10 2026, MCP Top 10 2025.
- The output schema v1.1 and canonical template at `templates/threats.md` are the authoritative structural reference.
- Existing examples are retained rather than deleted — the new standardized examples complement them, not replace them.
- The OWASP cross-reference appendix format (finding ID to framework category mapping table) is sufficient to demonstrate coverage without requiring schema changes to `output.yaml`.
