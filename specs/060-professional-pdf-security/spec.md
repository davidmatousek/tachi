---
prd_reference: docs/product/02_PRD/060-professional-pdf-security-report-branding-2026-03-29.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-29
    status: APPROVED_WITH_CONCERNS
    notes: "Comprehensive spec covering all 8 PRD user stories and 7 FRs. 3 concerns addressed: added FR-016 for schema version bump, corrected brand asset format assumption, added show-disclaimer test scenario. Approved for progression."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Professional PDF Security Assessment Report with tachi Branding

**Feature Branch**: `060-professional-pdf-security`
**Created**: 2026-03-29
**Status**: Draft
**Input**: PRD 060 — Professional PDF Security Assessment Report with tachi Branding

## User Scenarios & Testing

### User Story 1 — Branded Cover Page and Running Headers (Priority: P0)

A security consultant generating a client-facing assessment report sees the tachi logo on the cover page and consistent branded headers on every text page. The document immediately conveys professional quality without any post-generation reformatting.

**Why this priority**: The cover page is the first impression. Brand identity on cover and headers is the minimum viable branding that transforms "developer tool output" into "consultancy deliverable."

**Independent Test**: Generate a PDF from a minimal `threats.md` file and verify the cover displays the tachi primary logo centered in the upper portion, uses Tachi Indigo for the project title, and Vermillion for the classification banner. Verify text pages show the horizontal logo in the header.

**Acceptance Scenarios**:

1. **Given** brand assets exist at `brand/final/`, **When** a PDF is generated, **Then** the cover page displays the tachi primary logo (`tachi-logo-primary.png`) centered in the upper portion of the page, the project title uses Tachi Indigo (`#1B2A4A`), and the classification banner uses Vermillion (`#C93A40`).
2. **Given** brand assets exist, **When** a text page (Executive Summary, Findings Detail, etc.) is rendered, **Then** the header includes the tachi horizontal logo (`tachi-logo-horizontal.png`) left-aligned.
3. **Given** a full-bleed infographic page is rendered, **When** viewed, **Then** no header or footer is displayed (preserving edge-to-edge image rendering).
4. **Given** brand assets are missing from the expected path, **When** PDF is generated, **Then** the report renders with text-only branding ("tachi" in styled text) as a graceful fallback — no compilation error occurs.

---

### User Story 2 — Disclaimer and Table of Contents (Priority: P0)

A compliance officer receiving a tachi-generated assessment opens the document and finds a legal disclaimer on page 2 setting expectations about automated assessment methodology, followed by a table of contents enabling quick navigation to any section.

**Why this priority**: Disclaimer and TOC are table-stakes for any professional assessment report. Without them, the document cannot be used as audit evidence or navigated efficiently in board presentations.

**Independent Test**: Generate a PDF and verify page 2 is a disclaimer with four standard notice paragraphs. Verify page 3 is a TOC listing all included sections with correct page numbers. Omit optional artifacts and verify omitted sections do not appear in TOC.

**Acceptance Scenarios**:

1. **Given** a generated PDF, **When** page 2 is opened, **Then** a disclaimer page is displayed containing: assessment scope caveat, automated methodology notice, liability limitation, confidentiality notice, and recommendation for human expert review.
2. **Given** the disclaimer page, **When** reviewed, **Then** it uses branded design elements (Vermillion accent line, Tachi Indigo heading).
3. **Given** a generated PDF with all optional artifacts present, **When** the TOC is viewed, **Then** it lists every included section with accurate page numbers.
4. **Given** optional pages are omitted (e.g., no infographic images, no compensating controls), **When** the TOC is generated, **Then** omitted sections do not appear in the TOC and page numbers for remaining sections are correct.
5. **Given** existing templates, **When** the TOC is implemented, **Then** all section titles across all page templates are Typst `heading` elements (not `text()` calls) so that the native `outline()` function can discover them.

---

### User Story 3 — Risk Methodology and Assessment Scope Pages (Priority: P0)

A CISO presenting to the board includes the tachi assessment report. The methodology page explains how threats were identified and scored using STRIDE and AI-specific categories. The scope page shows exactly which components, data flows, and trust boundaries were assessed — answering "what was analyzed" without needing supplemental documentation.

**Why this priority**: Methodology and scope are required for audit evidence packages and build credibility with non-technical stakeholders. They answer "how did you find this?" and "what did you look at?" — the two most common questions from leadership.

**Independent Test**: Generate a PDF from `threats.md` alone and verify methodology shows qualitative assessment explanation. Generate with `risk-scores.md` added and verify 4D scoring explanation appears. Verify scope page extracts component list and data flow summary from threats.md Sections 1-2.

**Acceptance Scenarios**:

1. **Given** only `threats.md` exists, **When** the methodology page is rendered, **Then** it explains STRIDE threat categories and AI-specific threat categories (Prompt Injection, Tool Abuse, Agent Autonomy, Data Poisoning, Model Theft) and shows a qualitative probability x impact risk matrix.
2. **Given** `risk-scores.md` also exists, **When** the methodology page is rendered, **Then** it additionally explains the 4D quantitative scoring methodology (CVSS 3.1, Exploitability, Scalability, Reachability) and the composite score formula.
3. **Given** `compensating-controls.md` also exists, **When** the methodology page is rendered, **Then** it additionally explains compensating control detection and residual risk calculation.
4. **Given** `threats.md` contains Section 1 (Architecture Description) with a component table and Section 2 (Trust Boundaries) with trust zone and boundary crossing tables, **When** the scope page is rendered, **Then** it displays: components analyzed (name, type), data flows identified (source, destination, data), and trust boundaries mapped (zone, trust level).
5. **Given** `threats.md` lacks detailed Sections 1-2 but has frontmatter metadata, **When** the scope page is rendered, **Then** available metadata is displayed with a "Limited scope documentation" notice.
6. **Given** the methodology page, **When** reviewed, **Then** it includes a visual probability x impact matrix (2D grid with severity color coding) rather than text-only explanation.

---

### User Story 4 — Modular Theme Architecture (Priority: P1)

A developer extending tachi wants to customize the report's visual identity for their organization. They open a single `theme.typ` file, change the primary color and logo path, run `typst compile`, and the change propagates to every page automatically.

**Why this priority**: Theme centralization is the architectural foundation that prevents color/branding drift across templates. Without it, customization requires hunting through multiple files.

**Independent Test**: Modify a brand color in `theme.typ`, compile the report, and verify the change appears on all pages that use that color. Verify no hardcoded color values exist in any page template file.

**Acceptance Scenarios**:

1. **Given** the template directory, **When** reviewed, **Then** a `theme.typ` file exists containing all brand color definitions (7 brand tokens), logo path references (2 paths), and font declarations (3 font stacks).
2. **Given** `theme.typ` is modified (e.g., `brand-primary` changed to a different color), **When** `typst compile` is run, **Then** all pages referencing that token reflect the new color.
3. **Given** any page template file (.typ), **When** searched for hardcoded hex color values, **Then** no structural colors are hardcoded — all reference `theme.typ` tokens. Severity colors remain as functional constants.
4. **Given** the existing `shared.typ`, **When** reviewed after refactoring, **Then** it imports brand tokens from `theme.typ` and retains its existing layout functions (`report-header()`, `report-footer()`, `apply-typography()`, `apply-page-setup()`).

---

### User Story 5 — Report Configuration (Priority: P1)

A security team wants to customize the disclaimer text for their organization's legal requirements and hide the methodology page for internal-only reports. They create a `report-config.typ` file with overrides and the report adapts without modifying any template files.

**Why this priority**: Configuration enables organizational customization without forking templates — important for adoption but not blocking for initial release.

**Independent Test**: Generate a PDF without `report-config.typ` and verify defaults work. Create `report-config.typ` with custom disclaimer text and `show-methodology: false`, regenerate, and verify customizations applied.

**Acceptance Scenarios**:

1. **Given** no `report-config.typ` exists, **When** a PDF is generated, **Then** sensible defaults are used for all configurable values (default disclaimer text, methodology shown, disclaimer shown, default footer text).
2. **Given** `report-config.typ` contains `custom-disclaimer-text`, **When** PDF is generated, **Then** the disclaimer page uses the custom text instead of defaults.
3. **Given** `report-config.typ` contains `show-methodology: false`, **When** PDF is generated, **Then** the methodology page is omitted and does not appear in the TOC.
4. **Given** `report-config.typ` contains `show-disclaimer: false`, **When** PDF is generated, **Then** the disclaimer page is omitted and does not appear in the TOC.
5. **Given** the report assembler generates `report-config.typ`, **When** reviewed, **Then** it follows the same generation pattern as existing `report-data.typ` (generated alongside, consumed by main.typ).

---

### User Story 6 — Card-Based Findings Layout (Priority: P1, Cuttable)

A security consultant reviewing the findings section sees each finding as a styled card with a severity badge, threat ID, affected component, description, and recommendation — rather than dense table rows.

**Why this priority**: Visual improvement over flat tables, but the existing table layout is functional. This is cuttable if schedule pressure requires it — the enhanced table with branded colors serves as fallback.

**Independent Test**: Generate a PDF with 5+ findings and verify each displays as a card. Generate with 15+ findings and verify cards flow across multiple pages. If cut, verify the existing table renders with branded severity colors.

**Acceptance Scenarios**:

1. **Given** the findings detail page with card layout enabled, **When** rendered, **Then** each finding displays as a card with: severity badge (colored), threat ID, affected component, threat description, and recommendation.
2. **Given** findings with Tier 1 data (compensating-controls), **When** cards are rendered, **Then** each card includes residual risk score and control status.
3. **Given** more than 15 findings, **When** cards are rendered, **Then** cards flow across multiple pages with consistent layout and no orphaned cards (minimum 2 cards per page).
4. **Given** card layout is cut from scope, **When** the fallback table renders, **Then** severity cells use branded severity colors and table headers use Tachi Indigo background.

---

### Edge Cases

- What happens when brand assets exist but are corrupted (0 bytes or wrong format)? The system must detect non-PNG files and fall back to text-only branding with a warning, not a compilation error.
- What happens when `threats.md` uses schema v1.0 (no Section 1/2 in expected format)? The scope page displays available frontmatter metadata with "Limited scope documentation" notice.
- What happens when all optional artifacts are absent (only `threats.md`)? The PDF generates with cover, disclaimer, TOC, methodology (qualitative only), scope, executive summary (minimal), and findings detail — minimum 7 pages.
- What happens when existing `report-data.typ` files from PRD-054 (without new variables) are used? The report must compile successfully — new pages may render empty or with defaults, but no compilation error.
- What happens when the TOC lists an infographic page that spans custom page dimensions? The TOC entry references the page by section name with the correct page number.

## Requirements

### Functional Requirements

- **FR-001**: System MUST embed the tachi primary logo on the cover page and the horizontal logo in text page headers, with text-only fallback when logo files are absent.
- **FR-002**: System MUST apply the tachi brand color palette to all structural elements — Tachi Indigo (`#1B2A4A`) for headings and primary surfaces, Vermillion (`#C93A40`) for classification banners and accent elements, Steel Blue (`#2D4A6F`) for secondary elements.
- **FR-003**: System MUST centralize all brand tokens (7 colors, 2 logo paths, 3 font stacks) in a single `theme.typ` file, with no hardcoded structural color values in any page template.
- **FR-004**: System MUST generate a disclaimer page (always included) with four standard notice sections: assessment scope caveat, automated methodology notice, liability limitation, and confidentiality notice.
- **FR-005**: System MUST generate a table of contents using Typst's native `outline()` function that lists all included sections with accurate page numbers and excludes omitted conditional sections.
- **FR-006**: System MUST migrate all section titles across all page templates from `text()` calls to `heading` elements so that the `outline()` function can discover them for TOC generation.
- **FR-007**: System MUST generate a risk methodology page explaining STRIDE categories, AI-specific threat categories, and a visual probability x impact matrix, with conditional sections for 4D scoring (when `risk-scores.md` exists) and control analysis (when `compensating-controls.md` exists).
- **FR-008**: System MUST generate a scope page extracting component inventory, data flows, and trust boundaries from `threats.md` Sections 1-2, with graceful degradation when detailed sections are unavailable.
- **FR-009**: System MUST extract scope data from `threats.md` by parsing Section 1 (components table: Component, Type, Description) and Section 2 (trust zones table: Zone, Trust Level, Components; boundary crossings table: Crossing, From Zone, To Zone, Components, Controls).
- **FR-010**: System MUST inject logo file paths into `report-data.typ` using the same relative path pattern as infographic images (`../../{target_dir}/filename.png`), with the report assembler copying brand assets into the compilation directory.
- **FR-011**: System MUST support an optional `report-config.typ` file with four configurable values: `custom-disclaimer-text`, `custom-footer-text`, `show-methodology` (boolean), `show-disclaimer` (boolean), with sensible defaults when the file is absent.
- **FR-012**: System MUST preserve severity colors as functional constants — these are NOT overridden by brand colors.
- **FR-013**: System MUST maintain backward compatibility with existing `report-data.typ` files from PRD-054 — new pages may render empty but the report must compile without error.
- **FR-014**: System MUST include infographic pages in the TOC by rendering phantom `heading` elements on full-bleed pages that are invisible in the page content but discoverable by `outline()`.
- **FR-015**: System MUST render improved findings as styled cards with severity badge, threat ID, component, description, and recommendation (P1, cuttable — enhanced branded table serves as fallback).
- **FR-016**: System MUST update the report schema (`schemas/security-report.yaml`) from v1.0 to v1.1 to reflect the new page types, updated page sequence, theme token contract, and scope data variables added in this feature.

### Page Sequence

The complete page sequence for a fully-populated report:

1. Cover (always)
2. Disclaimer (always, unless `show-disclaimer: false`)
3. Table of Contents (always)
4. Risk Methodology (always, unless `show-methodology: false`)
5. Assessment Scope (always)
6. Executive Summary (always)
7. Risk Funnel infographic (conditional: `has-funnel-image`)
8. Baseball Card infographic (conditional: `has-baseball-image`)
9. System Architecture infographic (conditional: `has-architecture-image`)
10. Findings Detail (always)
11. Control Coverage (conditional: `has-compensating-controls`)
12. Remediation Roadmap (conditional: `has-compensating-controls` OR `has-threat-report` with remediation actions)

### Key Entities

- **Theme Tokens**: Brand identity configuration — 7 color values, 2 logo paths, 3 font stacks. Centralized in `theme.typ`, consumed by all templates via `shared.typ`.
- **Report Configuration**: Optional user overrides — disclaimer text, footer text, page visibility toggles. Generated as `report-config.typ` alongside `report-data.typ`.
- **Scope Data**: Assessment boundary information — component inventory (name, type, description), data flows (source, destination, data, protocol), trust boundaries (zone, trust level, components, crossings). Extracted from `threats.md` Sections 1-2.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of structural color values in page templates reference `theme.typ` tokens — zero hardcoded hex values outside of `theme.typ` and severity color constants.
- **SC-002**: All 4 new page types (Disclaimer, TOC, Methodology, Scope) render correctly from `threats.md` alone with graceful degradation for missing optional artifacts.
- **SC-003**: TOC page numbers are accurate for all included sections, including conditional pages — verified by generating PDFs with varying artifact combinations (threats-only, threats+scores, threats+scores+controls, all artifacts).
- **SC-004**: Existing `report-data.typ` files from PRD-054 (without new variables) compile successfully without error.
- **SC-005**: Modifying a single brand color in `theme.typ` propagates to all pages on recompilation — verified by changing `brand-primary` and confirming all headings update.
- **SC-006**: PDF generation completes in under 30 seconds for a full report with 3 infographic images and all new pages.
- **SC-007**: Side-by-side comparison of PRD-054 output and PRD-060 output demonstrates clear professional improvement in branding, layout, and completeness.

### Assumptions

- Brand assets in `brand/final/` have `.png` file extensions but may contain JPEG-encoded data internally. The system must handle both PNG and JPEG image data regardless of file extension (Typst `image()` detects format from file headers, not extensions).
- Typst `image()` function handles PNG embedding without quality loss (validated in PRD-054 with JPEG infographics).
- `threats.md` Sections 1 and 2 follow the documented schema (`schemas/output.yaml` v1.1) with component, data flow, and trust boundary tables.
- The report assembler can copy/symlink brand assets into the Typst compilation directory alongside the existing image path resolution pattern.
- Typst `outline()` function correctly handles conditional page inclusion when headings are inside `#if` blocks — headings that are never rendered do not appear in the outline.
- Font stacks remain unchanged (Helvetica Neue / New Computer Modern / Menlo) per brand typography guidelines.
