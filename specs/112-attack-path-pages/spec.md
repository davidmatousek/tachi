---
prd_reference: docs/product/02_PRD/112-attack-path-pages-in-pdf-2026-04-09.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All 4 PRD functional requirements covered (decomposed into 15 spec FRs). All 3 PRD user stories mapped plus US-4 section header/TOC. All architect and team lead PRD concerns resolved. 6 measurable success criteria, zero scope creep, 5 edge cases addressed."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Attack Path Pages in Security Report PDF

**Feature Branch**: `112-attack-path-pages`
**Created**: 2026-04-09
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/112-attack-path-pages-in-pdf-2026-04-09.md`
**Input**: User description: "PRD: 112 - Attack Path Pages in Security Report PDF"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Attack Path Page in PDF Report (Priority: P1)

A CISO reviewing a tachi security assessment PDF encounters a Critical or High finding and wants to understand the full attack chain. They navigate to the Attack Path Analysis section and find a dedicated page for each qualifying finding. Each page shows a rendered diagram of the attack tree, a plain-English narrative explaining how the attack chain works, and specific remediation steps. The CISO can use this page directly in a board presentation without additional preparation.

**Why this priority**: This is the core value proposition — transforming abstract tabular findings into visual, self-contained attack stories. Without this, the feature delivers no user value.

**Independent Test**: Generate a PDF from a threat model that has attack trees for Critical/High findings. Verify each qualifying finding has a dedicated page with diagram, narrative, and remediation sections.

**Acceptance Scenarios**:

1. **Given** a threat model with attack tree files for 2 Critical and 1 High finding, **When** the PDF is generated, **Then** the report contains 3 attack path pages in the Attack Path Analysis section
2. **Given** an attack path page, **When** a reader views it, **Then** it shows: (1) a severity-colored header with finding ID and title, (2) a rendered diagram image of the attack tree, (3) a 2-4 sentence narrative explanation of the attack chain, (4) a bulleted list of remediation steps
3. **Given** a threat model with no attack tree files, **When** the PDF is generated, **Then** no attack path pages appear and no errors occur — the report generates identically to before this feature

---

### User Story 2 - Attack Path Page Ordering (Priority: P1)

A security engineer reviewing a report with multiple attack path pages sees them ordered by severity (Critical findings first, then High) and within the same severity by finding ID. This allows them to focus on the most dangerous attack chains first.

**Why this priority**: Ordering is essential for usability — without it, the attack path section is disorganized and harder to navigate. This is tightly coupled with US-1 and must ship together.

**Independent Test**: Generate a PDF from a threat model with mixed Critical and High findings. Verify pages appear in correct order.

**Acceptance Scenarios**:

1. **Given** attack trees for findings T-1 (High), E-3 (Critical), AG-1 (Critical), **When** the PDF is generated, **Then** pages appear in order: AG-1, E-3, T-1 (Critical alphabetically first, then High)
2. **Given** a single Critical finding with an attack tree, **When** the PDF is generated, **Then** exactly one attack path page appears

---

### User Story 3 - Mermaid Diagram Rendering (Priority: P1)

When the PDF generation pipeline encounters a Mermaid attack tree, it renders the diagram as a high-quality image rather than showing raw code. The diagram uses the standard tachi color scheme (red goals, orange AND gates, teal OR gates, green leaves) and is legible at page size.

**Why this priority**: Visual diagrams are the key differentiator from existing tabular data. Raw Mermaid code would not deliver the intended user value.

**Independent Test**: Run the extraction pipeline on a sample attack tree file. Verify a PNG image is produced with correct colors and readable text.

**Acceptance Scenarios**:

1. **Given** a Mermaid flowchart code block from an attack tree file, **When** the extraction pipeline runs with the rendering tool available, **Then** a PNG image file is produced at 2x resolution
2. **Given** a rendered diagram image on the attack path page, **When** viewed at page size, **Then** node labels and edge connections are legible
3. **Given** the rendering tool is not available on the system, **When** the extraction pipeline runs, **Then** the attack path page is still included with the raw Mermaid code displayed as preformatted text — no pipeline failure occurs

---

### User Story 4 - Section Header and TOC Integration (Priority: P2)

The attack path pages are introduced by a section header page titled "Attack Path Analysis" and the section appears in the table of contents. This provides clear navigation within the report.

**Why this priority**: Navigation and structure are important for a professional report but are not the core value — the content pages (US-1) can function without a section header.

**Independent Test**: Generate a PDF with attack path pages. Verify the section divider page appears before the first attack path page and the TOC includes the section.

**Acceptance Scenarios**:

1. **Given** attack path pages exist in the report, **When** the PDF is generated, **Then** a section divider page titled "Attack Path Analysis" appears before the first attack path page
2. **Given** no attack tree artifacts exist, **When** the PDF is generated, **Then** no section divider page for Attack Path Analysis appears

---

### Edge Cases

- What happens when an attack tree file contains invalid Mermaid syntax? The page is included with raw Mermaid code as preformatted text fallback, and a warning is logged.
- What happens when an attack tree has more than 20 nodes and the diagram is very large? The diagram image is scaled down proportionally to fit the allocated page area (~60% of page height).
- What happens when a finding has both a standalone attack tree file and an inline tree in threat-report.md? The standalone file takes precedence (primary source).
- What happens when attack tree files exist but none match Critical or High severity? No attack path pages are generated (only Critical and High qualify).
- What happens when a finding's severity was changed between threat-report.md and the standalone file metadata? The finding severity from the cross-referenced findings data is authoritative for ordering and filtering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The extraction pipeline MUST detect attack tree files in the `attack-trees/` directory of the target report directory
- **FR-002**: The extraction pipeline MUST fall back to extracting inline attack trees from threat-report.md Section 5 when no standalone attack tree files exist
- **FR-003**: The extraction pipeline MUST extract from each attack tree: finding ID, component name, severity level, Mermaid code block, and correlated threat description
- **FR-004**: The extraction pipeline MUST cross-reference attack tree finding IDs with findings data to determine authoritative severity level for ordering
- **FR-005**: The extraction pipeline MUST convert Mermaid code blocks to PNG images at 2x resolution when the rendering tool is available
- **FR-006**: The extraction pipeline MUST gracefully fall back to including raw Mermaid code as text when the rendering tool is unavailable or rendering fails
- **FR-007**: The extraction pipeline MUST output a boolean flag indicating whether attack tree data exists for conditional page inclusion
- **FR-008**: The extraction pipeline MUST output an ordered array of attack tree entries (Critical first by ID, then High by ID)
- **FR-009**: Each attack path page MUST display: a severity-colored finding ID badge, the finding title, a rendered diagram image (or text fallback), a narrative explanation (2-4 sentences), and remediation steps (bulleted list)
- **FR-010**: Attack path pages MUST appear in the report sequence after the Executive Summary section and before the Detailed Findings section
- **FR-011**: A section divider page titled "Attack Path Analysis" MUST precede the first attack path page
- **FR-012**: Attack path pages MUST be conditionally included — omitted entirely when no qualifying attack trees exist
- **FR-013**: Each finding MUST occupy exactly one page — diagram scaling MUST ensure no overflow
- **FR-014**: The table of contents MUST include the Attack Path Analysis section when present
- **FR-015**: Existing reports without attack tree artifacts MUST generate identically to before this feature (backward compatibility)

### Key Entities

- **Attack Tree Entry**: Represents a single attack path visualization. Attributes: finding ID, component name, severity level, diagram image path (or raw Mermaid text), narrative description, remediation steps, rendering status (image or fallback)
- **Attack Path Section**: A conditional report section containing zero or more attack tree entries, preceded by a section divider. Present only when qualifying entries exist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Critical and High findings with attack tree artifacts appear as dedicated pages in the PDF — no qualifying finding is omitted
- **SC-002**: PDF generation succeeds with 100% reliability when attack tree artifacts are present — no regressions from this feature
- **SC-003**: PDF generation succeeds with 100% reliability when attack tree artifacts are absent — identical output to pre-feature behavior
<!-- Inverted by Feature 130 (2026-04-11): text fallback is no longer a supported shipping mode -->
- **SC-004**: Rendering tool (`mmdc`) availability is verified at preflight when `attack-trees/` contains Critical/High findings; 100% of attack path pages render as PNG diagrams OR the pipeline aborts loudly at preflight with a non-zero exit code and the canonical install message — no silent fallback, no raw Mermaid source ever ships in a PDF. See [ADR-022](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md).
- **SC-005**: Total PDF generation time increases by less than 30 seconds for a report with 5 attack path pages
- **SC-006**: All 6 example outputs in `examples/` continue to generate without errors after this feature is implemented

## Assumptions

- Attack tree files follow the existing naming convention `{finding-id}-attack-tree.md` with metadata table and Mermaid code block as documented in the threat-report agent
- The Mermaid code blocks in attack tree files are syntactically valid (validated by the threat-report agent at generation time)
- The narrative and remediation content for each attack path page can be derived from the attack tree file metadata and the corresponding finding's mitigation field in the findings data
- The existing Typst compilation workflow supports additional portrait pages without configuration changes
- The rendering tool (`mmdc` from `@mermaid-js/mermaid-cli`) IS a hard dependency as of Feature 130 when `attack-trees/` contains Critical/High findings; text fallback has been removed and the pipeline aborts at preflight if `mmdc` is missing — see [ADR-022](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md)
