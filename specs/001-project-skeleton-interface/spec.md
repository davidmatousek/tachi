---
prd_reference: docs/product/02_PRD/001-project-skeleton-interface-contract-2026-03-21.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "All 6 PRD FRs covered by 20 spec requirements. All 3 user stories have complete acceptance criteria. 3 non-blocking concerns: (1) pin OWASP dependency versions, (2) promote dual-dispatch edge case to FR text, (3) constitution-product alignment is governance hygiene."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Project Skeleton & Interface Contract

**Feature Branch**: `001-project-skeleton-interface`
**Created**: 2026-03-21
**Status**: Draft
**Input**: PRD 001 — Establish foundational repository structure, interface contract, and output template for tachi threat modeling toolkit

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Navigable Repository Structure (Priority: P1)

A developer clones the tachi repository for the first time and wants to understand how the toolkit is organized. They open the top-level directory and find clearly labeled directories — `agents/`, `adapters/`, `templates/`, `schemas/`, `examples/`, `docs/` — each containing a README that explains the directory's purpose, contents, and conventions. Without reading any source code or prompt files, the developer can locate any agent definition, configuration file, or output template within 30 seconds.

**Why this priority**: This is the foundational navigability contract. Every downstream feature (F-002 through F-010) depends on developers being able to find and understand artifacts. Without a navigable structure, no integration or contribution is possible.

**Independent Test**: Clone the repository, open any top-level directory, and verify a README exists that explains purpose and conventions. Navigate from root to any specific agent file in under 30 seconds.

**Acceptance Scenarios**:

1. **Given** a freshly cloned repository, **When** a developer opens any top-level directory (`agents/`, `adapters/`, `templates/`, `schemas/`, `examples/`), **Then** a README.md exists explaining the directory's purpose, contents, and conventions
2. **Given** the `agents/stride/` directory, **When** a developer lists its contents, **Then** they find 6 STRIDE agent prompt files (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) plus a README
3. **Given** the `agents/ai/` directory, **When** a developer lists its contents, **Then** they find 5 AI-specific threat agent prompt files (prompt-injection, tool-abuse, data-poisoning, model-theft, agent-autonomy) plus a README that documents the 5-agent-to-2-table mapping (AG and LLM)
4. **Given** the `schemas/` directory, **When** a developer lists its contents, **Then** they find `finding.yaml`, `input.yaml`, `output.yaml`, and a README explaining how schemas relate to agents and templates
5. **Given** a LICENSE file at the repository root, **When** a developer reads it, **Then** it contains either an Apache 2.0 or MIT license

---

### User Story 2 — Interface Contract for Integration (Priority: P1)

A developer wants to invoke tachi from their own orchestration framework (Claude Code, Cursor, Windsurf, or a custom pipeline). They open `docs/INTERFACE-CONTRACT.md` and find a single document specifying: what input formats are supported (ASCII, free-text, Mermaid, PlantUML, C4), how to invoke threat analysis (input + optional context → structured output), what the output looks like (reference to template and schema), and what side effects to expect (none beyond writing output files). The developer can integrate tachi without reading any agent prompt files or internal implementation details.

**Why this priority**: Tied with P1 — the interface contract is what makes tachi usable as a tool rather than just a collection of files. Integrators need a stable contract to build automation against.

**Independent Test**: Read `docs/INTERFACE-CONTRACT.md` and verify it answers: what formats are accepted, how to invoke, what output is produced, and what side effects occur. Validate that sample inputs for at least 3 formats are provided.

**Acceptance Scenarios**:

1. **Given** `docs/INTERFACE-CONTRACT.md` exists, **When** a developer reads the input specification section, **Then** they find 5 supported formats (ASCII, free-text, Mermaid, PlantUML, C4) with recognition patterns and at least one example valid input per format
2. **Given** the interface contract, **When** a developer reads the invocation protocol, **Then** they find: input = architecture diagram + optional context; output = structured `threats.md`; side-effect guarantee = no side effects beyond writing output files
3. **Given** the interface contract, **When** a developer reads the output schema section, **Then** they find a reference to `templates/threats.md` for structure and `schemas/output.yaml` for machine-readable validation, with `schema_version: "1.0"` documented
4. **Given** the interface contract, **When** a developer looks for the STRIDE-per-Element normalization table, **Then** they find a machine-readable mapping of DFD element types (External Entity, Process, Data Store, Data Flow) to applicable STRIDE categories
5. **Given** the interface contract, **When** a developer looks for AI extension dispatch rules, **Then** they find rules mapping element keywords ("LLM", "agent", "MCP server", etc.) to the appropriate AI threat agent category (AG or LLM)
6. **Given** the interface contract, **When** a developer reads the input format field specification, **Then** they find a `format:` field that defaults to `auto` with explicit format declaration as an option
7. **Given** the interface contract, **When** a developer reads the input sanitization section, **Then** they find guidance that architecture input is treated as data (not instructions) with prompt-level boundary requirements for agents

---

### User Story 3 — Consistent Output Template (Priority: P1)

A developer or security integrator wants all threat agents to produce findings in a consistent, predictable format. They open `templates/threats.md` and find a canonical template defining every section of a threat model: system overview, trust boundaries, STRIDE tables, AI threat tables, coverage matrix, risk summary, and recommended actions. Each section includes field descriptions and example values so the developer knows exactly what to expect in any generated output.

**Why this priority**: Tied with P1 — without a consistent output template, each agent would invent its own format, making outputs incomparable and unparseable by downstream features (SARIF export, narrative reports, infographics).

**Independent Test**: Read `templates/threats.md` and verify all 7 required sections exist with field descriptions and at least one example value per section.

**Acceptance Scenarios**:

1. **Given** `templates/threats.md` exists, **When** a developer reads it, **Then** they find all 7 required sections: System Overview, Trust Boundaries, STRIDE Tables (S/T/R/I/D/E), AI Threat Tables (AG/LLM), Coverage Matrix, Risk Summary, Recommended Actions
2. **Given** the output template, **When** a developer checks for schema versioning, **Then** they find `schema_version: "1.0"` in YAML frontmatter
3. **Given** the STRIDE tables, **When** a developer examines a finding row, **Then** they find fields: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation
4. **Given** the AI Threat tables, **When** a developer examines a finding row, **Then** they find fields: ID, Component, Threat, OWASP Reference (ASI-xx, MCP-xx, or LLM0x:2025), Likelihood, Impact, Risk Level, Mitigation
5. **Given** the Coverage Matrix, **When** a developer reads it, **Then** rows are components and columns are threat categories (S/T/R/I/D/E/AG/LLM) with finding counts per cell
6. **Given** the Risk Summary, **When** a developer reads it, **Then** they find counts per risk level: Critical, High, Medium, Low, Note (using OWASP 3x3 matrix)
7. **Given** the template, **When** a developer looks for field descriptions, **Then** each section includes field descriptions and at least one example value

---

### User Story 4 — Machine-Readable Schemas for Downstream Features (Priority: P2)

A developer building a downstream feature (orchestrator, SARIF export, narrative report) needs to know the exact data contract between agents and templates. They open `schemas/finding.yaml` and find the Intermediate Representation (IR) schema that all agents must produce. They can also reference `schemas/input.yaml` for input validation rules and `schemas/output.yaml` for output structure validation. These schemas enable downstream features to build against stable contracts without reading agent implementations.

**Why this priority**: P2 because schemas serve downstream features (F-002+), not direct end-user value. However, they are critical for preventing integration failures as the toolkit grows.

**Independent Test**: Read each schema file (`finding.yaml`, `input.yaml`, `output.yaml`) and verify they define complete field specifications with types, allowed values, and descriptions.

**Acceptance Scenarios**:

1. **Given** `schemas/finding.yaml` exists, **When** a developer reads it, **Then** they find a complete IR schema with fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type — each with type and allowed values
2. **Given** `schemas/input.yaml` exists, **When** a developer reads it, **Then** they find input validation rules for all 5 supported formats with recognition patterns
3. **Given** `schemas/output.yaml` exists, **When** a developer reads it, **Then** they find the complete output structure definition matching `templates/threats.md` sections

---

### User Story 5 — Example Inputs for Validation (Priority: P2)

A developer wants to verify that the interface contract and output template work as documented. They open the `examples/` directory and find at least 3 self-contained examples (ASCII diagram, Mermaid diagram, free-text description), each with an `input.md` file showing the architecture description and a `threats.md` file showing the expected output structure.

**Why this priority**: P2 because examples validate the contracts but are not the contracts themselves. They serve as both documentation and future test fixtures.

**Independent Test**: Open each example directory, verify `input.md` contains a valid architecture description in the stated format, and `threats.md` follows the output template structure.

**Acceptance Scenarios**:

1. **Given** `examples/ascii-web-api/` exists, **When** a developer reads `input.md`, **Then** they find a valid ASCII architecture diagram with trust boundaries
2. **Given** `examples/mermaid-agentic-app/` exists, **When** a developer reads `input.md`, **Then** they find a valid Mermaid architecture diagram featuring AI/agent components
3. **Given** `examples/free-text-microservice/` exists, **When** a developer reads `input.md`, **Then** they find a free-text architecture description with component and data flow details
4. **Given** any example directory, **When** a developer reads `threats.md`, **Then** the output follows the `templates/threats.md` structure with all 7 sections populated with example findings

---

### Edge Cases

- What happens when an integrator provides input in an unsupported format? The interface contract must document that unsupported formats return a clear error indicating supported options.
- What happens when an architecture diagram contains no identifiable components? The interface contract must specify minimum input requirements (at least one component and one data flow).
- What happens when an element matches both AG and LLM dispatch rules (e.g., "LLM agent orchestrator")? The AI extension dispatch rules must specify that both agent categories are dispatched, with deduplication handled at the coverage matrix level.
- What happens when a STRIDE-per-Element mapping produces zero applicable categories for an element type? This cannot occur — every DFD element type maps to at least 2 STRIDE categories per the normalization table.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST follow the canonical directory layout with 6 top-level directories (`agents/`, `adapters/`, `templates/`, `schemas/`, `examples/`, `docs/`), each containing a README.md explaining purpose, contents, and conventions
- **FR-002**: `agents/stride/` MUST contain 6 STRIDE agent prompt files (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) plus a README documenting the agent taxonomy
- **FR-003**: `agents/ai/` MUST contain 5 AI-specific threat agent prompt files (prompt-injection, tool-abuse, data-poisoning, model-theft, agent-autonomy) plus a README documenting the 5-agent-to-2-table mapping: AG (agent-autonomy, tool-abuse) and LLM (prompt-injection, data-poisoning, model-theft)
- **FR-004**: `docs/INTERFACE-CONTRACT.md` MUST specify 5 supported input formats (ASCII, free-text, Mermaid, PlantUML, C4) with recognition patterns, a `format:` field defaulting to `auto`, and at least one example valid input per format
- **FR-005**: The interface contract MUST include a machine-readable STRIDE-per-Element normalization table mapping DFD element types (External Entity, Process, Data Store, Data Flow) to applicable STRIDE categories
- **FR-006**: The interface contract MUST include AI extension dispatch rules mapping element keywords to threat agent categories (LLM keywords: "LLM", "model", "GPT", "Claude"; Agentic keywords: "agent", "autonomous", "orchestrator", "MCP server", "tool server", "plugin")
- **FR-007**: The interface contract MUST specify the invocation protocol: input = architecture diagram + optional context metadata; output = structured `threats.md`; side-effect guarantee = no side effects beyond writing output files
- **FR-008**: The interface contract MUST include input sanitization guidance stating that architecture input is treated as data (not instructions) with prompt-level boundary requirements for agents
- **FR-009**: `templates/threats.md` MUST include all 7 required sections (System Overview, Trust Boundaries, STRIDE Tables, AI Threat Tables, Coverage Matrix, Risk Summary, Recommended Actions) with field descriptions and at least one example value per section
- **FR-010**: The output template MUST include `schema_version: "1.0"` in YAML frontmatter and a `classification: confidential` header
- **FR-011**: `schemas/finding.yaml` MUST define the Intermediate Representation schema with fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type — each with type and allowed values
- **FR-012**: `schemas/input.yaml` MUST define input validation rules for all 5 supported formats with recognition patterns
- **FR-013**: `schemas/output.yaml` MUST define the complete output structure matching `templates/threats.md` sections
- **FR-014**: All findings MUST use the OWASP 3x3 risk matrix: Likelihood (LOW/MEDIUM/HIGH) x Impact (LOW/MEDIUM/HIGH) producing risk levels Critical, High, Medium, Low, Note
- **FR-015**: `adapters/ContextLoading.yaml` MUST reference correct post-scaffold paths (`agents/VoiceProfile.md`, `agents/StyleGuide.md`, `agents/MasterContent/`, `adapters/Terms/`, `adapters/Presets/`, `adapters/ScoringRubric.md`)
- **FR-016**: `adapters/ScoringRubric.md` MUST be populated with OWASP 3x3 risk scoring dimensions for likelihood (8 factors) and impact (8 factors)
- **FR-017**: `adapters/ProjectMeta.yaml` MUST be populated with tachi project metadata (name, description, version, domain, status)
- **FR-018**: `examples/` MUST contain at least 3 self-contained examples (ASCII, Mermaid, free-text), each with `input.md` and `threats.md` files
- **FR-019**: A LICENSE file MUST exist at the repository root containing either Apache 2.0 or MIT license text
- **FR-020**: Agent prompt files in `agents/stride/` and `agents/ai/` are immutable reference data — they MUST NOT be modified per-output

### Key Entities

- **Finding**: The atomic unit of threat analysis output. Defined by the IR schema (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type). Produced by agents, consumed by templates.
- **DFD Element**: A component in the architecture diagram classified as External Entity, Process, Data Store, or Data Flow. Each type maps to specific STRIDE categories via the normalization table.
- **Threat Agent**: A prompt definition file that analyzes one specific threat category. 6 STRIDE agents + 5 AI agents, producing findings conforming to the IR schema.
- **Output Template**: A format definition that transforms IR findings into a structured document. `threats.md` is the canonical template; future templates (SARIF, narrative) apply different formatting to the same findings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new developer can navigate from repository root to any specific agent, adapter, template, or schema file within 30 seconds using only directory READMEs for guidance
- **SC-002**: The interface contract answers all 4 integration questions (what formats, how to invoke, what output, what side effects) in a single document without requiring the reader to open any other file
- **SC-003**: All 7 output template sections include field descriptions and at least one example value, enabling a developer to understand the expected output without running any agents
- **SC-004**: All 3 schema files (finding.yaml, input.yaml, output.yaml) define complete field specifications that downstream features (F-002 through F-010) can build against without ambiguity
- **SC-005**: All cross-references between files (ContextLoading.yaml paths, schema references, template references) resolve to existing files with zero broken references
- **SC-006**: Sample inputs for at least 3 formats (ASCII, Mermaid, free-text) exist in `examples/` with corresponding expected output files following the template structure

### Assumptions

- tachi is a knowledge system (markdown + YAML) with no runtime dependencies or compiled code
- All "testing" is validation-by-example: sample inputs produce expected output structure, not unit tests against a runtime
- Developers adopt tachi by cloning the repository and invoking agents through their preferred orchestration framework
- The 5-agent AI taxonomy (prompt-injection, tool-abuse, data-poisoning, model-theft, agent-autonomy) is stable for Phase 1
- The OWASP 3x3 risk matrix is the standard for all risk rating (not CVSS or custom scales)
- Agent prompt content authoring (VoiceProfile text, StyleGuide rules, MasterContent entries, Narrative fragments) is out of scope — only scaffold structure and README documentation are delivered

### Constraints

- **No Runtime Dependencies**: All deliverables are markdown and YAML files
- **Knowledge System Pattern**: Must follow hub-and-spoke content model (agents/ as hub, adapters/ as configuration)
- **Naming Conventions**: PascalCase for content directories and config files, kebab-case for agent/command/narrative files
- **Immutability Principle**: Master content in agents/ is never modified per-output
- **No Credentials in Content**: Per security rules, no API keys, tokens, or hardcoded paths in any content file

### Dependencies

- **Blocks**: F-002 (Orchestrator), F-003 (STRIDE Agents), F-004 (AI Agents), F-005 (Input Parsing), F-006 (SARIF Export), F-007 (Narrative Report), F-008 (Infographic), F-009 (Platform Adapters), F-010 (E2E Validation)
- **Blocked by**: Nothing — this is the foundational feature
- **External**: OWASP LLM Top 10 v2025 (stable), OWASP Agentic Top 10 2026 draft (may evolve), OWASP MCP Top 10 v0.1 Beta (early draft)

### Open Questions

- **License choice**: Apache 2.0 or MIT? Decision needed before implementation. Assumption: Apache 2.0 (broader patent protection for a security tool)
- **Classification default**: Should `classification: confidential` be the default or configurable per invocation? Assumption: Default to `confidential` since outputs contain security-sensitive architectural details; can be overridden in future features
