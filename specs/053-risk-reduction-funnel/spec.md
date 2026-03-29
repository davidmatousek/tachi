---
prd_reference: docs/product/02_PRD/053-risk-reduction-funnel-2026-03-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All PRD requirements covered. User stories map 1:1 to PRD US-1 through US-4 plus template integration. No scope creep. Graceful degradation and data extraction paths well-specified."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Risk Reduction Funnel Infographic Template

**Feature Branch**: `053-risk-reduction-funnel`
**Created**: 2026-03-28
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/053-risk-reduction-funnel-2026-03-28.md`

## User Scenarios & Testing

### User Story 1 — Full Pipeline Funnel (Priority: P0)

As a security leader who has run the full tachi pipeline (threat-model, risk-score, compensating-controls), I want `/infographic --template risk-funnel` to render a 4-tier funnel showing threats identified, inherent risk scored, controls applied, and residual risk, so that I can present a single image to stakeholders showing the complete risk reduction journey.

**Why this priority**: This is the primary value proposition — the complete risk reduction narrative that no other tool provides. All data sources are available, enabling the richest visualization.

**Independent Test**: Run the full pipeline on any example architecture, then execute `/infographic --template risk-funnel`. The spec should contain 4 funnel tiers with progressively narrowing widths and a metrics sidebar with risk reduction statistics.

**Acceptance Scenarios**:

1. **Given** `compensating-controls.md`, `risk-scores.md`, and `threats.md` all exist in the output directory, **When** I run `/infographic --template risk-funnel`, **Then** the generated spec contains 4 funnel tiers with progressively narrowing widths representing risk reduction
2. **Given** the data source is `compensating-controls.md`, **When** the funnel spec is generated, **Then** Tier 1 shows total threat count and qualitative severity distribution, Tier 2 shows inherent composite score distribution, Tier 3 shows control coverage percentage and mitigation counts, and Tier 4 shows residual severity distribution
3. **Given** the funnel spec is generated, **When** I compare Tier 1 width to Tier 4 width, **Then** Tier 4 is visually narrower (minimum 10% narrower per tier to maintain the funnel metaphor even when actual risk reduction is minimal)
4. **Given** GEMINI_API_KEY is available, **When** the spec is generated, **Then** a photorealistic 3D funnel image is produced alongside the spec at `threat-risk-funnel.jpg`
5. **Given** GEMINI_API_KEY is not available, **When** the spec is generated, **Then** the specification is saved as standalone with `image_generated: false`, and no error is raised

---

### User Story 2 — Partial Pipeline Funnel (Priority: P0)

As a security analyst who has run `/threat-model` and `/risk-score` but not `/compensating-controls`, I want the risk funnel to show 3 populated tiers with the 4th tier indicated as "not yet available," so that I get a useful visualization and a clear signal to run `/compensating-controls` for the full picture.

**Why this priority**: Users commonly run partial pipelines. Graceful degradation ensures the template is useful at every stage, not just at full completion.

**Independent Test**: Run `/threat-model` and `/risk-score` on any architecture without running `/compensating-controls`. Execute `/infographic --template risk-funnel`. The spec should render 3 solid tiers and 1 ghost tier.

**Acceptance Scenarios**:

1. **Given** `risk-scores.md` and `threats.md` exist but `compensating-controls.md` does not, **When** I run `/infographic --template risk-funnel`, **Then** the spec renders 3 solid tiers (Threats Identified, Inherent Risk Scored, Unmitigated Risk summary) and 1 ghost tier (dashed outline) labeled "Run /compensating-controls to complete the funnel"
2. **Given** 3-tier mode, **When** the funnel is rendered, **Then** the bottom solid tier uses inherent risk data (same as Tier 2 severity distribution) since no control reduction has been applied
3. **Given** 3-tier mode, **When** the enhancement tip is displayed in the spec, **Then** it reads: "Run `/compensating-controls` to unlock the full 4-tier risk reduction funnel"

---

### User Story 3 — Minimal Pipeline Funnel (Priority: P0)

As a developer who has run only `/threat-model`, I want the risk funnel to show a single-tier summary with guidance toward the full funnel, so that I understand my starting point and the pipeline path ahead.

**Why this priority**: Even the most basic pipeline output should produce a useful funnel that communicates the starting threat volume and guides users toward enrichment.

**Independent Test**: Run `/threat-model` only on any architecture. Execute `/infographic --template risk-funnel`. The spec should render 1 solid tier and 3 ghost tiers.

**Acceptance Scenarios**:

1. **Given** only `threats.md` exists in the output directory, **When** I run `/infographic --template risk-funnel`, **Then** the spec renders 1 solid tier (Threats Identified) showing total threat count and qualitative severity distribution
2. **Given** 1-tier mode, **When** the funnel is rendered, **Then** below the solid tier are 3 ghost tiers (dashed outlines) labeled with the pipeline commands needed to unlock them
3. **Given** 1-tier mode, **When** the enhancement tip is displayed, **Then** it reads: "Run `/risk-score` to begin quantifying your risk reduction funnel"

---

### User Story 4 — Funnel Metrics Sidebar (Priority: P1)

As a security leader presenting to stakeholders, I want key metrics displayed alongside the funnel (total threats, risk reduction %, control coverage %), so that the numbers reinforce the visual narrative without requiring separate data lookup.

**Why this priority**: Sidebar metrics add quantitative reinforcement to the visual funnel. Not required for MVP but significantly enhances executive communication.

**Independent Test**: Generate a 4-tier funnel and verify the sidebar contains Total Findings, Risk Reduction %, Control Coverage %, and per-tier severity breakdown.

**Acceptance Scenarios**:

1. **Given** 4-tier mode (compensating-controls source), **When** the funnel spec is generated, **Then** a metrics sidebar shows: Total Findings, Risk Reduction %, Control Coverage %, and severity breakdown per tier
2. **Given** 3-tier mode, **When** the sidebar is generated, **Then** metrics show: Total Findings, severity distribution, and "Risk Reduction: N/A — run /compensating-controls"
3. **Given** 1-tier mode, **When** the sidebar is generated, **Then** metrics show: Total Findings and qualitative severity counts only

---

### User Story 5 — Template Integration (Priority: P0)

As a user running `/infographic --template all`, I want the risk-funnel template to be included alongside baseball-card and system-architecture, so that I can generate all three visualizations in a single command.

**Why this priority**: Template registration is required for the feature to be accessible through the existing command interface.

**Independent Test**: Run `/infographic --template all` with compensating-controls data. All three specs and images should be generated.

**Acceptance Scenarios**:

1. **Given** I run `/infographic --template risk-funnel`, **When** the command parses the template flag, **Then** `risk-funnel` is recognized as a valid template value
2. **Given** I run `/infographic --template all`, **When** templates are generated, **Then** three specs are produced: `threat-baseball-card-spec.md`, `threat-system-architecture-spec.md`, and `threat-risk-funnel-spec.md`
3. **Given** the infographic agent's template registry, **When** I check the registered templates, **Then** `risk-funnel` maps to `.claude/agents/tachi/templates/infographic-risk-funnel.md`

---

### Edge Cases

- **Empty threats.md**: If `threats.md` exists but contains zero findings, the funnel renders a single tier labeled "0 Threats Identified" with a message: "No threats found — threat model may need review"
- **All findings at same severity**: If all findings are the same severity level, the funnel still narrows (minimum 10% per tier) with uniform tier coloring; the severity color for the dominant level applies
- **Extremely large finding count (100+)**: Tier labels show aggregate counts; individual finding details are omitted from the funnel visual to prevent clutter (detail is in the spec sections)
- **Compensating-controls with zero risk reduction**: If all controls are "missing" (0% reduction), Tier 4 width equals Tier 2 width (no narrowing for those tiers), but Tier 1→Tier 2 still narrows to maintain funnel shape; a sidebar note states "0% risk reduction — no effective controls detected"
- **Missing co-located threats.md**: When primary source is `compensating-controls.md` or `risk-scores.md` but `threats.md` is not in the same directory, halt with error: "Co-located threats.md required for structural data"

## Requirements

### Functional Requirements

- **FR-001**: System MUST create a template file at `.claude/agents/tachi/templates/infographic-risk-funnel.md` following the established 9-section template pattern (frontmatter comment, ASCII layout, style table, color palette, typography, zone specifications, Gemini prompt template, Gemini API config, accessibility)
- **FR-002**: Template MUST define a 4-tier vertical funnel layout in 16:9 landscape orientation (minimum 1920x1080) with tiers labeled: Threats Identified (widest), Inherent Risk Scored, Controls Applied, and Residual Risk (narrowest)
- **FR-003**: System MUST implement graceful degradation based on data source: 4 solid tiers from `compensating-controls.md`, 3 solid + 1 ghost from `risk-scores.md`, 1 solid + 3 ghost from `threats.md`
- **FR-004**: Ghost tiers MUST render as dashed outlines with light opacity and display the pipeline command needed to unlock them as a call-to-action label
- **FR-005**: System MUST register `risk-funnel` in the infographic agent's template registry at `.claude/agents/tachi/threat-infographic.md`
- **FR-006**: System MUST register `risk-funnel` as a valid `--template` value in the infographic command at `.claude/commands/infographic.md`
- **FR-007**: Tier widths MUST be proportional to finding count or risk volume at each stage, with a minimum 10% visual narrowing per tier to maintain the funnel metaphor
- **FR-008**: Tier connectors MUST use gradient transitions between tiers (not hard edges) to convey the flowing pipeline narrative
- **FR-009**: The Gemini prompt MUST lead with aesthetic intent (photorealistic 3D funnel, premium glass-like material, executive boardroom quality) before specifying data content
- **FR-010**: Output files MUST follow the naming convention: `threat-risk-funnel-spec.md` for the specification and `threat-risk-funnel.jpg` for the image
- **FR-011**: The spec output MUST follow the `schemas/infographic.yaml` v1.0 format with all 6 required sections (Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, Visual Design Directives)
- **FR-012**: Risk distribution counts in the spec MUST match the source data exactly with zero discrepancy
- **FR-013**: The template MUST use the standard severity color palette: Critical=#DC2626, High=#EA580C, Medium=#CA8A04, Low=#2563EB, Note=#6B7280
- **FR-014**: The `--template all` flag MUST include `risk-funnel` alongside `baseball-card` and `system-architecture`

### P1 Requirements

- **FR-015**: Template SHOULD include a metrics sidebar (right-aligned, approximately 20% width) displaying Total Findings, Risk Reduction %, Control Coverage %, and severity breakdown per tier
- **FR-016**: Template SHOULD include percentage annotations between tiers showing the risk reduction at each stage transition

### Data Extraction Paths

- **FR-017**: Tier 1 (Threats Identified) MUST extract data from co-located `threats.md` Section 6 (Risk Summary): total finding count and qualitative severity distribution
- **FR-018**: Tier 2 (Inherent Risk Scored) MUST extract data from `risk-scores.md` Section 2 (Scored Threat Table): composite score distribution and severity band counts
- **FR-019**: Tier 3 (Controls Applied) MUST extract data from `compensating-controls.md` Section 1 (Executive Summary): control coverage percentage, findings with controls count, and mitigation statistics
- **FR-020**: Tier 4 (Residual Risk) MUST extract data from `compensating-controls.md` Section 2 (Coverage Matrix): residual severity distribution and residual score range

### Key Entities

- **Funnel Tier**: A visual trapezoid representing one stage of the risk reduction pipeline. Attributes: tier number (1-4), label, width percentage, data source section, content values, solid/ghost rendering state
- **Ghost Tier**: A funnel tier rendered as a dashed outline when its data source is unavailable. Attributes: tier number, label, CTA text (pipeline command to unlock), opacity (20%), border style (dashed)
- **Metrics Sidebar**: A right-aligned panel displaying aggregate statistics alongside the funnel. Attributes: total findings, risk reduction percentage, control coverage percentage, per-tier severity breakdown
- **Design Template**: The markdown file defining the complete visual specification for the funnel including layout, colors, typography, zone specs, and Gemini prompt. Located at `.claude/agents/tachi/templates/infographic-risk-funnel.md`

## Success Criteria

### Measurable Outcomes

- **SC-001**: Running `/infographic --template risk-funnel` with `compensating-controls.md` as the detected data source produces a spec containing all 4 funnel tiers with data-driven widths and all 6 required schema sections
- **SC-002**: Running `/infographic --template risk-funnel` with only `risk-scores.md` produces a 3-tier spec with 1 ghost tier and an enhancement tip directing to `/compensating-controls`
- **SC-003**: Running `/infographic --template risk-funnel` with only `threats.md` produces a 1-tier spec with 3 ghost tiers and an enhancement tip directing to `/risk-score`
- **SC-004**: The risk distribution counts in the generated spec match the source data with zero discrepancy across all three data source modes
- **SC-005**: Running `/infographic --template all` generates three separate specs (baseball-card, system-architecture, risk-funnel) without errors
- **SC-006**: When GEMINI_API_KEY is available, image generation produces a 16:9 JPEG alongside the spec; when unavailable, the spec is saved as standalone with no errors
- **SC-007**: The template file follows the exact 9-section structure used by existing templates (frontmatter, layout, style, palette, typography, zones, Gemini prompt, API config, accessibility)
- **SC-008**: All existing `/infographic` invocations (baseball-card, system-architecture, all, corporate-white alias) continue to work identically after adding risk-funnel

### Assumptions

- The existing 3-tier auto-detection hierarchy correctly identifies data source type without modification
- `compensating-controls.md` contains both composite scores (inherent) and residual scores per finding, enabling the delta calculation between Tiers 2 and 4
- Gemini image generation can render 3D funnel shapes at photorealistic quality at 16:9 resolution (acknowledged as best-effort per ADR-014)
- The infographic schema v1.0 (6 sections) is sufficient for the funnel template without schema modifications
- Section 5 (Architecture Threat Overlay) can accommodate a new "funnel-tier" format alongside the existing tabular (baseball-card) and spatial (system-architecture) formats
