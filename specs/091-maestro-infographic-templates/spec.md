---
prd_reference: docs/product/02_PRD/091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-08
    status: APPROVED_WITH_CONCERNS
    notes: "6 findings (1 MEDIUM priority drift — resolved by restoring PRD priorities, 2 LOW, 3 INFORMATIONAL). Spec is faithful translation of PRD with stronger edge cases and finer-grained FRs. All 7 PRD FRs covered, both personas served, scope aligned."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: MAESTRO Infographic Templates and PDF Report Section

**Feature Branch**: `091-maestro-infographic-templates`
**Created**: 2026-04-08
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Layer Risk Distribution (Priority: P0)

As a CISO reviewing a threat model, I want to see a vertical stack diagram showing finding counts and highest severities per MAESTRO layer (L1-L7), so I can quickly identify which architectural layers of our AI stack carry the most risk exposure and brief stakeholders accordingly.

**Why this priority**: This is the primary visualization that enables the core value proposition — answering "which layer is most exposed?" at a glance. Without it, security leaders must manually scan tabular findings to understand layer-level risk. This template directly serves the CISO/security management persona.

**Independent Test**: Can be fully tested by running the infographic command with `maestro-stack` template against any MAESTRO-tagged threats.md output, and verifying a spec and image are generated showing all seven layers with correct finding counts and severity indicators.

**Acceptance Scenarios**:

1. **Given** a threats.md with MAESTRO-tagged findings across multiple layers, **When** the infographic command runs with `maestro-stack` template, **Then** a spec file and image are generated showing L1-L7 layers as horizontal bands with finding counts and highest severity per layer
2. **Given** a threats.md without MAESTRO data (pre-Feature 084 output), **When** the infographic command runs with `maestro-stack` template, **Then** a graceful empty state is rendered indicating no MAESTRO data is available
3. **Given** the generated stack diagram, **When** a user views it, **Then** the most-exposed layer (highest finding count) is visually prominent
4. **Given** a threats.md where some layers have zero findings, **When** the stack renders, **Then** empty layers still appear in the diagram but are visually muted

---

### User Story 2 - View Component-Layer Heatmap (Priority: P0)

As a security engineer performing detailed threat analysis, I want to see a grid where rows are system components and columns are MAESTRO layers with severity coloring, so I can pinpoint exactly which component-layer intersections need remediation priority.

**Why this priority**: Tied with US-01 because it serves the second primary persona (security engineer) with a complementary visualization. While the stack diagram shows aggregate layer risk, the heatmap reveals specific component-layer hotspots that drive remediation decisions.

**Independent Test**: Can be fully tested by running the infographic command with `maestro-heatmap` template against any MAESTRO-tagged threats.md output, and verifying a grid image is generated with correct component-layer intersections colored by severity.

**Acceptance Scenarios**:

1. **Given** a threats.md with MAESTRO-tagged findings, **When** the infographic command runs with `maestro-heatmap` template, **Then** a spec file and image are generated showing a component-row by L1-L7-column grid with severity-colored cells
2. **Given** a component with no findings at a specific layer, **When** the heatmap renders, **Then** that cell appears empty or neutral-colored
3. **Given** multiple findings at the same component-layer intersection, **When** the heatmap renders, **Then** the cell shows the highest severity among those findings
4. **Given** an architecture with more than 10 components, **When** the heatmap renders, **Then** components are prioritized by finding count and capped at a reasonable maximum for readability

---

### User Story 3 - PDF Report MAESTRO Section (Priority: P0)

As a security professional generating a formal PDF assessment report, I want a dedicated MAESTRO Findings page that regroups threats by architectural layer, so I can include layer-level risk analysis in deliverables sent to clients and management.

**Why this priority**: The PDF report is the primary formal deliverable from tachi. Without a MAESTRO section, the layer classification added by Feature 084 is invisible in the most important output artifact. This directly completes the Feature 084 story.

**Independent Test**: Can be fully tested by running the security report command against a MAESTRO-tagged output directory and verifying the compiled PDF contains a MAESTRO Findings page with findings grouped by layer.

**Acceptance Scenarios**:

1. **Given** a threat model output with MAESTRO data, **When** the PDF report is generated, **Then** a MAESTRO Findings page appears showing findings grouped by L1-L7 layers with layer names, descriptions, and finding details
2. **Given** a threat model output without MAESTRO data, **When** the PDF report is generated, **Then** no MAESTRO page appears and existing pages are unaffected
3. **Given** the MAESTRO page renders, **When** viewed, **Then** each layer section shows the layer ID, full name, finding count, and individual findings with ID, component, severity, and threat summary

---

### User Story 4 - Generate Both MAESTRO Templates Together (Priority: P1)

As a user who wants both MAESTRO visualizations without running two separate commands, I want to use a `maestro` shorthand for the template flag, so I can generate both maestro-stack and maestro-heatmap in a single invocation.

**Why this priority**: Convenience feature that reduces friction for the common case of wanting both MAESTRO views. Lower priority because users can achieve the same result by running each template individually.

**Independent Test**: Can be fully tested by running the infographic command with `maestro` template shorthand and verifying both spec+image pairs are generated.

**Acceptance Scenarios**:

1. **Given** a valid threats.md with MAESTRO data, **When** the user specifies `maestro` as the template, **Then** both maestro-stack and maestro-heatmap spec and image files are generated
2. **Given** the `maestro` shorthand is used, **When** dispatching, **Then** it expands to generate both individual templates sequentially

---

### User Story 5 - MAESTRO Data Extraction (Priority: P0)

As the pipeline, when a threat model output contains MAESTRO layer data, I need the extraction script to automatically extract layer distribution, per-finding layer mappings, and the most-exposed layer, so that infographic templates and the PDF report receive accurate MAESTRO data.

**Why this priority**: This is the data foundation that enables all other user stories. Without MAESTRO extraction, neither the infographic templates nor the PDF page can render meaningful content.

**Independent Test**: Can be fully tested by running the extraction script against the agentic-app example output and verifying the output includes MAESTRO layer distribution, finding counts per layer, and most-exposed layer identification.

**Acceptance Scenarios**:

1. **Given** a threats.md with MAESTRO layer data in findings, **When** the extraction script runs, **Then** output includes layer distribution (layer ID, name, finding count, highest severity per layer), most-exposed layer, and per-finding layer assignments
2. **Given** a threats.md without MAESTRO data, **When** the extraction script runs, **Then** MAESTRO fields default to empty/null without errors
3. **Given** MAESTRO data is present, **When** extraction runs, **Then** the aggregate layer distribution matches the Section 6 "Risk by MAESTRO Layer" summary in threats.md

---

### Edge Cases

- What happens when all findings map to a single MAESTRO layer? The stack diagram should show one highlighted layer and six empty layers; the heatmap should have one populated column.
- What happens when findings have `maestro_layer: "Unclassified"`? Unclassified findings should be grouped in an "Unclassified" row/band separate from L1-L7.
- What happens when the extraction script encounters a threats.md with mixed schema versions (some findings with MAESTRO, some without)? Findings without MAESTRO layer should be treated as "Unclassified."
- What happens when MAESTRO infographic images are present but the PDF report data lacks MAESTRO variables? The images should still be includable as full-bleed infographic pages independent of the structured MAESTRO findings page.
- What happens when component names in the heatmap are very long? Component names should be truncated to maintain grid readability.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `maestro-stack` infographic template that renders a vertical seven-layer stack diagram showing finding counts and highest severity per MAESTRO layer
- **FR-002**: System MUST provide a `maestro-heatmap` infographic template that renders a component-by-layer grid with severity-colored cells at each intersection
- **FR-003**: System MUST provide a MAESTRO Findings page in the PDF report that groups findings by MAESTRO layer (L1-L7) with layer name, description, and finding details
- **FR-004**: System MUST extract MAESTRO layer distribution data from threat model output, including per-layer finding counts, highest severity per layer, and most-exposed layer
- **FR-005**: System MUST extract per-finding MAESTRO layer assignments for component-layer intersection data needed by the heatmap
- **FR-006**: System MUST support a `maestro` shorthand that generates both maestro-stack and maestro-heatmap templates in a single invocation
- **FR-007**: All MAESTRO sections (infographic templates, PDF page) MUST be gated by a data-presence flag so they render gracefully when MAESTRO data is absent
- **FR-008**: The heatmap MUST show the highest severity when multiple findings exist at the same component-layer intersection
- **FR-009**: The stack diagram MUST visually distinguish the most-exposed layer (highest finding count) from other layers
- **FR-010**: The PDF MAESTRO Findings page MUST appear conditionally — only when MAESTRO data exists in the threat model output
- **FR-011**: New infographic templates MUST follow the same structural pattern as existing templates (mandatory sections: layout, style, color palette, typography, zone specs, prompt template, API config, accessibility)
- **FR-012**: New extraction logic MUST parse aggregate layer data from the threats.md Section 6 "Risk by MAESTRO Layer" summary and per-finding layer data from Section 3 agent tables
- **FR-013**: The extraction script MUST be extended to accept `maestro-stack` and `maestro-heatmap` as valid template choices
- **FR-014**: Template documentation MUST be updated to include both new templates with their placeholders, output files, and usage instructions
- **FR-015**: New PDF report variables MUST include backward-compatible defaults so existing reports compile without modification

### Key Entities

- **MAESTRO Layer**: One of seven architectural layers (L1 Foundation Model through L7 User Interface) plus "Unclassified." Each layer has an ID, full name, and CSA-defined description. Findings are classified into layers based on their component's classification.
- **Layer Distribution**: Aggregate view of findings per layer — includes layer ID, layer name, finding count, and highest severity. Derived from threat model output Section 6.
- **Component-Layer Intersection**: A pairing of a system component and a MAESTRO layer. The heatmap renders severity at each intersection. Derived from per-finding data in threat model output Section 3.
- **Infographic Spec**: A structured markdown document (Sections 1-6) that describes the visual layout and data content for image generation. Each template produces its own spec format.
- **Report Data Variables**: The set of named variables that control PDF report content and page visibility. New MAESTRO variables extend this set with backward-compatible defaults.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both MAESTRO infographic templates generate valid spec files and images from the agentic-app example architecture (which contains MAESTRO data across 5+ layers)
- **SC-002**: The PDF report includes a MAESTRO Findings page when compiled from MAESTRO-tagged output, and omits it cleanly when compiled from pre-Feature 084 output
- **SC-003**: The `maestro` shorthand produces both template outputs in a single invocation without errors
- **SC-004**: Existing templates (baseball-card, system-architecture, risk-funnel) produce identical output before and after this feature is implemented — zero regression
- **SC-005**: Extraction script correctly identifies the most-exposed layer matching the Section 6 summary data in threats.md
- **SC-006**: All six example architectures in `examples/` compile successfully with the updated report pipeline — those with MAESTRO data show the new page, those without skip it gracefully
- **SC-007**: Template documentation accurately describes both new templates including all placeholders, output file names, and usage examples
- **SC-008**: The heatmap correctly maps component-layer intersections with highest-severity coloring verified against manual inspection of the agentic-app threats.md

## Assumptions

- Feature 084 (MAESTRO Layer Mapping) is delivered and stable; all MAESTRO data consumed by this feature originates from Feature 084's pipeline output
- The agentic-app example in `examples/` contains MAESTRO layer data across at least 5 layers, providing sufficient diversity for validation
- Gemini API can render the visual complexity of a 7-layer stack diagram and a component-layer heatmap grid at acceptable quality
- Existing report compilation toolchain supports adding a new page template without version upgrades
- The `maestro` shorthand at the skill dispatch level (not CLI parser) is the correct architectural location for template expansion, consistent with existing dispatch patterns

## Scope Boundaries

### In Scope
- Two new infographic templates (maestro-stack, maestro-heatmap)
- MAESTRO Findings page in PDF report
- MAESTRO data extraction from threats.md
- Report data variable contract extension
- Skill dispatch update for `maestro` shorthand
- Template and skill reference documentation updates

### Out of Scope
- Changes to agent detection logic or scoring formulas
- Modifications to existing infographic templates
- MAESTRO layer reclassification or keyword changes (Feature 084 scope)
- Interactive filtering in PDF output
- Coverage matrix for MAESTRO layers
- MAESTRO data in Tier 2 (risk-scores.md) or Tier 1 (compensating-controls.md) sources

## Dependencies

- **Feature 084** (MAESTRO Layer Mapping) — delivered 2026-04-08 — provides `maestro_layer` field in finding IR
- **Feature 071** (Deterministic Infographic Extraction) — delivered 2026-03-30 — provides extraction script being extended
- **Feature 067** (Deterministic Report Data Extraction) — delivered 2026-03-30 — provides report data pipeline
- **Feature 054** (Security Assessment PDF Booklet) — delivered 2026-03-28 — provides Typst template system
- **Feature 039** (Standalone /infographic Command) — delivered 2026-03-28 — provides infographic skill dispatch
- **Gemini API** — external dependency for image generation (same as existing templates)

## Risks

- **Gemini image quality for new visual formats**: Mitigated by reusing proven prompt engineering patterns from existing templates
- **Heatmap readability with many components**: Mitigated by capping components to top N by finding count, consistent with existing heat map strategy
- **Section 3 column variation**: STRIDE tables have 8 columns, AI agent tables have 9 — extraction must handle both column structures when parsing per-finding MAESTRO data
