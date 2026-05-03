---
prd_reference: docs/product/02_PRD/054-security-assessment-pdf-booklet-2026-03-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 5 PRD functional requirements covered by 23 spec FRs. All 4 PRD user stories mapped. Two additional stories (US-5, US-6) trace to explicit PRD content. No scope creep. 2 minor non-blocking observations."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Security Assessment PDF Booklet

**Feature Branch**: `054-security-assessment-pdf`
**Created**: 2026-03-28
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/054-security-assessment-pdf-booklet-2026-03-28.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single-Command PDF Generation (Priority: P0)

A user has completed a tachi threat model pipeline and has artifacts scattered across a directory -- threats.md, risk-scores.md, compensating-controls.md, infographic images, and narrative reports. They want to run a single command to assemble everything into one professional PDF booklet they can distribute to stakeholders. The command auto-detects all available artifacts, determines which pages to include, and produces a complete PDF without requiring the user to specify each input file.

**Why this priority**: This is the core value proposition. Without single-command generation, the feature has no reason to exist. Every other story builds on this foundation.

**Independent Test**: Run `/security-report` on a directory containing all tachi artifacts and verify a multi-page PDF is produced with the correct page sequence.

**Acceptance Scenarios**:

1. **Given** a directory containing only `threats.md`, **When** `/security-report` is run, **Then** a PDF is generated with cover page, executive summary, and findings detail pages
2. **Given** a directory with all artifacts (`threats.md`, `threat-report.md`, `risk-scores.md`, `compensating-controls.md`, 3 infographic JPEG images), **When** `/security-report` is run, **Then** all 8 page types are included in the correct sequence
3. **Given** a directory with no recognized tachi artifacts, **When** `/security-report` is run, **Then** a clear error message explains that `threats.md` is the minimum required artifact
4. **Given** a directory with artifacts and the `--output-dir /path/to/output` flag, **When** `/security-report` is run, **Then** the PDF is written to the specified output directory
5. **Given** a directory with artifacts and the `--title "Custom Project Name"` flag, **When** `/security-report` is run, **Then** the cover page displays the custom title instead of the auto-detected project name

---

### User Story 2 - Full-Bleed Infographic Pages (Priority: P0)

A user has generated infographic JPEG images using `/infographic` (risk funnel, baseball card, system architecture). When the PDF booklet is generated, these images must render as full-bleed pages -- edge-to-edge with no margins, white borders, or letterboxing. The infographic pages use landscape-oriented custom page dimensions to match the 16:9 aspect ratio of the source images, while text pages remain portrait US Letter.

**Why this priority**: Full-bleed infographic rendering is the primary visual differentiator. Without it, the PDF is just a text report with awkwardly embedded images -- indistinguishable from a markdown-to-PDF conversion.

**Independent Test**: Generate a PDF from a directory containing `threats.md` and one or more infographic JPEG images. Open the PDF and verify the infographic pages render edge-to-edge without margins or scaling artifacts.

**Acceptance Scenarios**:

1. **Given** `threat-risk-funnel.jpg` exists in the input directory, **When** PDF is generated, **Then** page 3 renders the image full-bleed using custom page dimensions matching 16:9 aspect ratio
2. **Given** `threat-baseball-card.jpg` exists, **When** PDF is generated, **Then** the baseball card page renders the image full-bleed
3. **Given** `threat-system-architecture.jpg` exists, **When** PDF is generated, **Then** the system architecture page renders the image full-bleed
4. **Given** no infographic images exist in the input directory, **When** PDF is generated, **Then** infographic pages are omitted entirely (no blank pages, no placeholders)
5. **Given** only one of three infographic images exists, **When** PDF is generated, **Then** only that one infographic page is included and page numbering adjusts dynamically

---

### User Story 3 - Graceful Degradation (Priority: P0)

A user has only partially completed the tachi pipeline -- perhaps they ran `/threat-model` but not `/risk-score` or `/compensating-controls`. The PDF command must still produce a valid, professional-looking booklet using whatever artifacts are available. Pages corresponding to missing artifacts are omitted entirely, and the remaining pages adapt their content richness based on what data sources exist.

**Why this priority**: Users at any pipeline stage should get value from the report. Requiring the full pipeline to run before PDF generation creates an adoption barrier and prevents incremental value delivery.

**Independent Test**: Generate PDFs from three different artifact combinations (threats-only, threats + risk-scores, full pipeline) and verify each produces a valid booklet with appropriate pages.

**Acceptance Scenarios**:

1. **Given** only `threats.md`, **When** PDF is generated, **Then** booklet contains: cover, executive summary (from threats.md metadata), and findings detail table (qualitative: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation)
2. **Given** `threats.md` + `risk-scores.md`, **When** PDF is generated, **Then** booklet adds scored findings with severity distribution and the findings detail table uses quantitative columns (ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability)
3. **Given** `threats.md` + `risk-scores.md` + `compensating-controls.md`, **When** PDF is generated, **Then** booklet adds control coverage and remediation roadmap pages, and findings detail table uses residual risk columns (ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation)
4. **Given** any artifact combination plus infographic images, **When** PDF is generated, **Then** corresponding full-bleed pages are included in the correct sequence positions
5. **Given** `threats.md` with schema version 1.0 (no Section 4a Correlated Findings), **When** PDF is generated, **Then** correlated findings are omitted from the executive summary but all other pages generate normally

---

### User Story 4 - Professional Design Quality (Priority: P1)

A CISO or security consultant needs to present the PDF to a board of directors, audit committee, or client. The document must look professionally designed with consistent typography, a severity color palette, branded cover page, and proper pagination. The design quality must be sufficient that the recipient does not feel the need to reformat the document before presenting it.

**Why this priority**: Design quality determines whether the PDF replaces manual PowerPoint assembly or becomes just another intermediate artifact. This story has lower priority than functional correctness but is essential for user adoption.

**Independent Test**: Generate a full-pipeline PDF and evaluate against design criteria: consistent fonts, severity colors, page numbers, headers/footers with classification markings, and branded cover page.

**Acceptance Scenarios**:

1. **Given** a generated PDF, **When** opened, **Then** the cover page displays project name, assessment date, classification level (from `threats.md` frontmatter), and tachi branding
2. **Given** a generated PDF, **When** reviewed, **Then** all text pages use a consistent serif/sans-serif typography pairing
3. **Given** a generated PDF, **When** reviewed, **Then** findings tables use the tachi severity color palette (Critical = red #DC2626, High = orange #F97316, Medium = yellow #EAB308, Low = blue #4169E1)
4. **Given** a generated PDF, **When** reviewed, **Then** every page has consistent headers, footers, and dynamic page numbers
5. **Given** a `threats.md` with `classification: confidential`, **When** PDF is generated, **Then** "CONFIDENTIAL" appears in the header or footer of every page

---

### User Story 5 - Typst Prerequisite Handling (Priority: P1)

A user attempts to run `/security-report` but does not have Typst installed on their system. The command must detect the missing dependency, provide a clear error message explaining what Typst is and why it is needed, and display platform-specific installation instructions so the user can resolve the issue without searching external documentation.

**Why this priority**: External dependency management directly affects first-run experience. A confusing error message when Typst is missing will cause users to abandon the feature.

**Independent Test**: Run `/security-report` on a system without Typst installed and verify the error message includes platform-specific installation instructions.

**Acceptance Scenarios**:

1. **Given** Typst is not installed, **When** `/security-report` is run, **Then** the command displays a clear error message naming "Typst" as the missing dependency
2. **Given** Typst is not installed, **When** the error message is displayed, **Then** it includes installation instructions for macOS (`brew install typst`), Linux (`cargo install typst-cli`), and Windows (`winget install typst`)
3. **Given** Typst is installed, **When** `/security-report` is run, **Then** no Typst-related warnings or messages are displayed (silent success)

---

### User Story 6 - Schema-Driven Page Assembly (Priority: P1)

The page assembly logic (which pages to include, in what order, using which data source) must be defined in a declarative schema file rather than hardcoded in the command or agent. This enables future extensions (new page types, custom page ordering) without modifying command logic, and maintains consistency with existing tachi schema conventions.

**Why this priority**: Architectural consistency with existing schemas (`output.yaml`, `risk-scoring.yaml`, etc.) and future extensibility. Lower priority than functional stories but important for maintainability.

**Independent Test**: Verify that a schema file defines the page sequence, data source mappings, and inclusion rules, and that the assembly logic references this schema.

**Acceptance Scenarios**:

1. **Given** the feature is implemented, **When** inspecting the schema directory, **Then** a `schemas/security-report.yaml` file exists defining page types, their sequence, source artifact requirements, and layout type (portrait/landscape)
2. **Given** the schema file, **When** reviewed, **Then** it declares which artifact must be present for each page to be included
3. **Given** the schema file, **When** reviewed, **Then** it defines the 3-tier data source preference for the Findings Detail page (compensating-controls > risk-scores > threats) with tier-specific column definitions

---

### Edge Cases

- **Corrupted artifact**: If a markdown artifact exists but cannot be parsed (malformed YAML frontmatter, missing expected sections), the system reports a parsing warning for that artifact but continues generating the PDF with remaining valid artifacts. The minimum viable artifact (`threats.md`) must parse successfully; corruption in `threats.md` aborts with a specific error message identifying the parsing failure.
- **Oversized findings table**: If the findings table exceeds one page, it must flow to subsequent pages with repeated column headers on each continuation page.
- **Missing classification field**: If `threats.md` frontmatter lacks a `classification` field, the cover page omits the classification marking and page headers/footers display no classification label (rather than "undefined" or a placeholder).
- **Empty infographic images**: If an infographic JPEG file exists but is 0 bytes or corrupted, that infographic page is skipped with a warning message.
- **Concurrent artifact access**: If artifacts are being regenerated while `/security-report` runs, the command reads files at invocation time and does not re-read mid-generation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST auto-detect all available tachi artifacts in the target directory by scanning for known file patterns (`threats.md`, `threat-report.md`, `risk-scores.md`, `compensating-controls.md`, `threat-risk-funnel.jpg`, `threat-baseball-card.jpg`, `threat-system-architecture.jpg`)
- **FR-002**: System MUST require `threats.md` as the minimum artifact; if absent, abort with a clear error identifying the missing file
- **FR-003**: System MUST report which artifacts were detected and which pages will be generated before beginning PDF assembly
- **FR-004**: System MUST assemble detected artifacts into a sequenced PDF following the page order: Cover, Executive Summary, Risk Funnel (full-bleed), Baseball Card (full-bleed), System Architecture (full-bleed), Findings Detail, Control Coverage, Remediation Roadmap
- **FR-005**: System MUST omit pages whose source artifacts are missing (no blank pages, no gaps in page numbering)
- **FR-006**: System MUST render infographic JPEG images as full-bleed pages using custom page dimensions matching 16:9 aspect ratio, without margins, cropping, or letterboxing
- **FR-007**: System MUST render text pages in US Letter portrait (8.5" x 11") with standard print margins
- **FR-008**: System MUST use the 3-tier data source preference for the Findings Detail page: compensating-controls.md (tier 1, residual risk columns) > risk-scores.md (tier 2, quantitative columns) > threats.md (tier 3, qualitative columns)
- **FR-009**: System MUST parse YAML frontmatter from markdown artifacts to extract metadata (project name, date, classification, schema version)
- **FR-010**: System MUST parse markdown tables from artifacts to extract structured finding data for the Findings Detail, Control Coverage, and Remediation Roadmap pages
- **FR-011**: System MUST generate a branded cover page displaying project name, assessment date, classification level, and finding count summary
- **FR-012**: System MUST generate an Executive Summary page that adapts content richness based on available sources (`threat-report.md` Section 1 for rich narrative, `threats.md` risk summary as fallback)
- **FR-013**: System MUST apply the tachi severity color palette to all severity indicators across all pages (Critical = red, High = orange, Medium = yellow, Low = blue)
- **FR-014**: System MUST render consistent headers, footers, and dynamic page numbers on all pages, with classification markings from artifact metadata on every page
- **FR-015**: System MUST support the `--output-dir` flag to specify the output directory for the generated PDF (default: same directory as input artifacts)
- **FR-016**: System MUST support the `--title` flag to override the project name displayed on the cover page
- **FR-017**: System MUST check for the Typst prerequisite before attempting PDF generation, and display platform-specific installation instructions if Typst is not installed
- **FR-018**: System MUST complete PDF generation in under 30 seconds for a typical report (34 findings, 3 infographic images, 8 pages)
- **FR-019**: System MUST produce identical output when run twice on the same input artifacts (idempotent generation)
- **FR-020**: System MUST handle schema version differences gracefully: v1.0 artifacts (lacking Section 4a Correlated Findings) generate all pages normally with correlated findings omitted from the executive summary
- **FR-021**: System MUST define page assembly rules in a declarative schema file (`schemas/security-report.yaml`) specifying page types, sequence, source requirements, layout type, and data source tiers
- **FR-022**: System MUST store rendering templates in `templates/security-report/` with a README distinguishing rendering templates (Typst `.typ` files) from existing reference templates (markdown examples)
- **FR-023**: System MUST perform all processing locally with no external network calls during PDF generation

### Key Entities

- **Artifact**: A file produced by a tachi pipeline command (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic JPEGs). Has a file pattern, optional/required status, and the set of pages it enables.
- **Page**: A single page (or page group) in the output PDF. Has a type (cover, executive-summary, full-bleed-infographic, findings-detail, control-coverage, remediation-roadmap), a layout (portrait or landscape), a source artifact dependency, and a sequence position.
- **Data Source Tier**: The priority level of an artifact for a specific page. The Findings Detail page uses a 3-tier preference where richer data sources (compensating-controls) take priority over leaner sources (threats).
- **Schema**: A declarative YAML file defining the rules for page assembly, including artifact-to-page mappings, data source tiers, column definitions per tier, and layout specifications.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `/security-report` produces a valid, openable PDF from `threats.md` alone (minimum viable input) in under 30 seconds
- **SC-002**: A full-pipeline PDF (all artifacts + 3 infographic images) includes all 8 page types in the correct sequence with no blank or missing pages
- **SC-003**: Full-bleed infographic pages render at 16:9 aspect ratio without visible margins, letterboxing, or scaling artifacts when viewed at 100% zoom
- **SC-004**: The Findings Detail table displays tier-appropriate columns based on which data source is available (3 distinct column sets verified)
- **SC-005**: Running `/security-report` twice on identical input produces byte-identical PDF output (idempotent)
- **SC-006**: PDF generation completes in under 30 seconds for a 34-finding report with 3 infographic images on a standard development machine
- **SC-007**: All text pages display consistent typography, severity color palette, page numbers, and classification markings
- **SC-008**: When Typst is not installed, the error message includes platform-specific installation instructions for macOS, Linux, and Windows
- **SC-009**: The `schemas/security-report.yaml` file defines all page types, their source artifact requirements, and the 3-tier data source preference

## Assumptions

- Typst CLI (v0.11+) is available or installable on the user's machine
- Source artifacts follow tachi's documented schemas (v1.0 or v1.1)
- Infographic images are JPEG format at 16:9 aspect ratio as generated by `/infographic`
- The `templates/` directory can be extended with a `security-report/` subdirectory for Typst files without conflicting with existing reference templates
- Users are comfortable installing a CLI tool (Typst) as a prerequisite, similar to how they install tachi itself
- US Letter (8.5" x 11") is the only required page size for Phase 1; A4 support is deferred

## Scope Boundaries

### In Scope (Phase 1)
- Artifact auto-detection with graceful degradation
- 8 page types: cover, executive summary, 3 full-bleed infographic pages, findings detail, control coverage, remediation roadmap
- Typst template system with professional design
- `/security-report` command following existing tachi patterns
- Schema file defining page assembly rules
- `--output-dir` and `--title` flags
- Classification markings on all pages
- Severity color palette
- Dynamic page numbering

### Out of Scope
- Progression/trend pages comparing multiple assessment runs (Phase 2)
- Custom branding/logo injection (Phase 2)
- A4 page size support (Phase 2)
- PDF/A compliance (Phase 2)
- HTML report output alternative
- PowerPoint/PPTX export
- Interactive PDF features (clickable TOC, hyperlinks)
- Custom page templates or user-editable page ordering
- Attack tree Mermaid diagram rendering as images (Phase 2)

## Dependencies

- All artifact-producing pipeline commands (delivered: `/threat-model`, `/risk-score`, `/compensating-controls`, `/infographic`)
- Existing schema definitions in `schemas/` directory
- Typst CLI (external, user-installed)
