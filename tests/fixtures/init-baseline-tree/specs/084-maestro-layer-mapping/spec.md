---
prd_reference: docs/product/02_PRD/084-maestro-layer-mapping-2026-04-07.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-07
    status: APPROVED
    notes: "All 4 PRD functional requirements covered. All 4 user stories mapped with matching acceptance criteria. All 3 non-functional requirements addressed. All 8 PRD open questions handled correctly. Zero scope creep. Ready for planning."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Layer Mapping

**Feature Branch**: `084-maestro-layer-mapping`
**Created**: 2026-04-07
**Status**: Draft
**Input**: PRD 084 — MAESTRO Layer Mapping: CSA Seven-Layer Taxonomy Overlay for Threat Findings

## User Scenarios & Testing

### User Story 1 - Layer-Tagged Threat Findings (Priority: P0)

A threat analyst reviews tachi threat model output after a pipeline run and needs to understand which architectural layers carry the most risk. Each finding in the STRIDE and AI threat tables includes a MAESTRO Layer column showing the CSA seven-layer classification (L1-L7) for the finding's target component. The analyst filters and groups threats by layer to identify risk concentrations without manually mapping each finding to infrastructure layers.

**Why this priority**: This is the core value proposition — without layer-tagged findings, no downstream features (layer summaries, SARIF tags) have data to work with. Every other user story depends on this classification being present.

**Independent Test**: Run a full pipeline on the agentic-app example architecture and verify that every finding row in threats.md includes a MAESTRO Layer value derived from the component's classification in Phase 1.

**Acceptance Scenarios**:

1. **Given** a completed pipeline run on an architecture with identifiable components, **When** viewing threats.md, **Then** each finding in STRIDE and AI threat tables includes a MAESTRO Layer column with a value from L1-L7 or "Unclassified"
2. **Given** a component classified as L3 (Agent Framework) in Phase 1, **When** a STRIDE finding targets that component, **Then** the finding's MAESTRO Layer column shows "L3 — Agent Framework"
3. **Given** a component with no keyword matches, **When** classification completes, **Then** the component and its findings are assigned "Unclassified" without error

---

### User Story 2 - Phase 1 Component Classification (Priority: P0)

During Phase 1 (Scope), the tachi orchestrator classifies each component by its MAESTRO layer using keyword matching against the component's name, description, and DFD type. The classification appears in both the component inventory and the dispatch table as a new MAESTRO Layer column. This ensures the layer tag is available before any threat agents run, enabling passive propagation through all downstream phases.

**Why this priority**: Classification is the upstream dependency for all layer tagging. If components are not classified in Phase 1, no downstream phase can assign layers to findings.

**Independent Test**: Run Phase 1 on the agentic-app example architecture and verify the component inventory and dispatch table both include a MAESTRO Layer column with values derived from keyword matching.

**Acceptance Scenarios**:

1. **Given** an architecture description with identifiable components, **When** Phase 1 completes, **Then** the component inventory includes a MAESTRO Layer column
2. **Given** the dispatch table produced after Phase 1, **When** displayed to the user, **Then** it includes a MAESTRO Layer column between DFD Type and STRIDE Categories
3. **Given** a component named "Knowledge Base" with description mentioning "vector store", **When** keyword matching runs, **Then** the component is classified as L2 (Data Operations)
4. **Given** a component with no matching keywords in name, description, or DFD type, **When** classification completes, **Then** it defaults to "Unclassified"

---

### User Story 3 - SARIF Layer Tags (Priority: P0)

A security auditor consuming tachi SARIF output in GitHub Code Scanning or similar security tooling needs MAESTRO layer tags on each result to filter alerts by architectural layer. Each SARIF result includes the layer as both a tag in the tags array and as a dedicated property.

**Why this priority**: SARIF is the primary machine-readable output. Without layer tags in SARIF, security tooling cannot programmatically filter or group by architectural layer.

**Independent Test**: Run a full pipeline, open the SARIF output file, and verify each result object includes `maestro-layer:{layer-name}` in `properties.tags` and a `maestro-layer` key in `properties`.

**Acceptance Scenarios**:

1. **Given** a SARIF output file from a pipeline run, **When** inspecting a result, **Then** `properties.tags` array includes `maestro-layer:{layer-name}` (e.g., "maestro-layer:L3")
2. **Given** a SARIF output file, **When** inspecting a result, **Then** `properties` includes `maestro-layer` key with the full layer name (e.g., "L3 — Agent Framework")
3. **Given** existing SARIF consumers processing tachi SARIF output, **When** the new fields are present, **Then** existing consumers continue to function without error (additive only)

---

### User Story 4 - Layer-Based Risk Summary (Priority: P1)

A CISO reviewing the threat report for executive communication needs risk summaries grouped by MAESTRO layer to prioritize remediation by architectural layer and communicate risk posture using industry-standard vocabulary. A "Risk by MAESTRO Layer" subsection appears in the risk summary section of threats.md showing finding counts and highest severity per layer.

**Why this priority**: Executive communication is high value but depends on layer-tagged findings (US-1) being implemented first. This is a reporting enhancement on top of the core classification.

**Independent Test**: Run a full pipeline on an architecture with findings across multiple layers, and verify the risk summary section includes a MAESTRO layer breakdown table.

**Acceptance Scenarios**:

1. **Given** a completed pipeline run, **When** viewing the threats.md risk summary, **Then** a "Risk by MAESTRO Layer" subsection is present
2. **Given** findings across multiple layers, **When** the layer summary renders, **Then** each layer with findings shows the finding count and highest severity level
3. **Given** layers with zero findings, **When** the summary renders, **Then** those layers are omitted from the table

---

### User Story 5 - Downstream Propagation (Priority: P1)

The MAESTRO layer tag assigned in Phase 1 propagates passively through risk-scores.md, compensating-controls.md, and the narrative threat report without modifying any scoring formulas, control detection logic, or report generation logic. Downstream consumers read the field if present and include it in their output; they do not compute or modify it.

**Why this priority**: Propagation ensures layer data is available across the full pipeline output suite. Without propagation, users would need to cross-reference threats.md manually for layer context when reviewing scores or controls.

**Independent Test**: Run a full pipeline including risk scoring and compensating controls analysis, and verify that the MAESTRO layer field appears in risk-scores.md and compensating-controls.md output.

**Acceptance Scenarios**:

1. **Given** findings with MAESTRO layer tags in threats.md, **When** risk scoring runs, **Then** risk-scores.md includes the layer tag for each scored finding without changes to scoring formulas
2. **Given** scored findings with MAESTRO layer tags, **When** compensating controls analysis runs, **Then** compensating-controls.md includes the layer tag for each finding without changes to control detection logic
3. **Given** a finding with no MAESTRO layer tag (absent field), **When** downstream consumers process it, **Then** the finding is treated as "Unclassified" without error

---

### Edge Cases

- What happens when a component matches keywords for multiple MAESTRO layers? First-match-wins: layers are evaluated in order L1-L7, and the first matching layer is assigned.
- What happens when the architecture has no identifiable components (e.g., empty or malformed input)? Phase 1 produces an empty component inventory with no MAESTRO classifications. No errors, no "Unclassified" entries for nonexistent components.
- What happens when a finding references a component not in the Phase 1 inventory? The finding defaults to "Unclassified" for its MAESTRO layer.
- What happens during a baseline-aware run? MAESTRO layer tags propagate through delta status correlation. The current run's layer assignment takes precedence over the baseline's layer assignment. Layer differences between baseline and current run do not affect delta status computation (delta status is determined by finding identity, not metadata).
- What happens when all components are classified as "Unclassified"? The "Risk by MAESTRO Layer" subsection shows a single row for "Unclassified". The pipeline completes without error.

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a shared reference file defining the CSA MAESTRO seven-layer taxonomy with keyword-to-layer mappings, following the established shared reference pattern (Feature 078)
- **FR-002**: System MUST classify each component by MAESTRO layer during Phase 1 (Scope) using case-insensitive keyword matching against component name, description, and DFD type
- **FR-003**: System MUST use first-match-wins ordering (layers evaluated L1 through L7) when a component matches keywords for multiple layers
- **FR-004**: System MUST assign "Unclassified" to components matching no layer keywords, without treating this as an error
- **FR-005**: System MUST display a MAESTRO Layer column in both the Phase 1 component inventory and the dispatch table intermediate artifacts
- **FR-006**: System MUST add an optional `maestro_layer` field to the finding intermediate representation (IR) schema with values L1-L7 or "Unclassified" and a default of "Unclassified"
- **FR-007**: System MUST add a MAESTRO Layer column to all STRIDE threat tables (6 tables) and AI threat tables (2 tables) in threats.md output
- **FR-008**: System MUST add a "Risk by MAESTRO Layer" subsection to the risk summary section of threats.md showing finding count and highest severity per layer, omitting layers with zero findings
- **FR-009**: System MUST add MAESTRO layer metadata to each SARIF result: a `maestro-layer:{layer-name}` entry in `properties.tags` and a `maestro-layer` key in `properties`
- **FR-010**: System MUST propagate the `maestro_layer` field passively through risk-scores.md and compensating-controls.md without modifying scoring formulas, control detection logic, or residual risk calculations
- **FR-011**: System MUST maintain full backward compatibility — existing pipeline output unchanged when no MAESTRO layer keywords match (all findings default to "Unclassified")
- **FR-012**: System MUST update all example architecture outputs (6 examples) with MAESTRO layer classifications

### Key Entities

- **MAESTRO Layer**: An architectural classification from the CSA seven-layer taxonomy (L1 Foundation Model through L7 User Interface, plus "Unclassified"). Assigned to components during Phase 1 and propagated through findings to all pipeline outputs.
- **Layer Keyword Mapping**: A reference table associating keywords with MAESTRO layers. Used for classification during Phase 1. Maintained in a shared reference file, human-editable without code changes.
- **Component Inventory**: The Phase 1 intermediate artifact listing all extracted components with their DFD type, description, and (new) MAESTRO layer assignment.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Greater than 90% of components in example architectures receive a non-"Unclassified" MAESTRO layer assignment, validating keyword coverage
- **SC-002**: 100% of findings across threats.md, risk-scores.md, compensating-controls.md, and SARIF output include the `maestro_layer` field (present or defaulted to "Unclassified")
- **SC-003**: Existing pipeline output is byte-identical (excluding new MAESTRO columns and subsections) when comparing pre-feature and post-feature runs on the same architecture input — zero regression
- **SC-004**: SARIF output with MAESTRO layer tags validates against the SARIF 2.1.0 JSON schema and is consumable by GitHub Code Scanning without error
- **SC-005**: The MAESTRO layer keyword table is maintained in a single shared reference file that can be updated without modifying any agent definitions, skill files, or output templates

## Assumptions

- The CSA MAESTRO seven-layer taxonomy is stable and will not undergo breaking changes in the near term. If CSA adds or renames layers, the shared reference file can be updated independently.
- Keyword matching against component name, description, and DFD type provides sufficient classification accuracy for the initial release. ML-based classification is not needed at this stage.
- "Unclassified" is an acceptable and non-erroneous default. Users understand that some components (particularly generic infrastructure like "Load Balancer") may not match any layer-specific keywords.
- The existing shared reference loading pattern (Feature 078) is adequate for MAESTRO layer definitions — no new loading mechanism is required.
- All 11 threat agents can propagate the `maestro_layer` field without modification to their detection logic — the field is read-only metadata from their perspective.
- SARIF consumers (GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps) tolerate unknown properties in `result.properties` per the SARIF 2.1.0 specification.
