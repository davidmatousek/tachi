---
prd:
  number: 128
  topic: executive-threat-architecture
  created: 2026-04-09
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-09, status: APPROVED, notes: "Strong user value — moves critical visuals to where CISOs actually read"}
  architect_signoff: {agent: architect, date: 2026-04-09, status: APPROVED_WITH_CONCERNS, notes: "4 concerns (1M, 3L): infographic-page() already portrait — evaluate reuse; early-page insertion acceptable but document section grouping; clarify architectural layers vs MAESTRO layers; callout narrative rewriting belongs in agent spec phase not extraction. All resolvable in plan.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-09, status: APPROVED_WITH_CONCERNS, notes: "3 concerns: resolve callout text open question before spec; define architectural layer = trust zone; portrait risk is misframed — Typst pages already portrait, real risk is Gemini prompt engineering. Scope realistic (210-250 lines, 8 files, 1-2 sessions)."}
source:
  idea_id: 128
  story_id: null
---

# Executive Threat Architecture Infographic — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-09
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Move a high-impact architecture threat infographic to pages 2–3 of the PDF security report so CISOs see it before they stop reading.

### Problem Statement
CISOs and executive decision-makers rarely read past the first 3 pages of a security assessment report. Tachi's existing infographic templates (baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap) are placed after Attack Path Analysis — typically page 10+ — where executive audiences never reach them. The most valuable visual communication happens too late in the document to influence executive decisions.

### Proposed Solution
Add a 6th infographic template ("Executive Threat Architecture") that produces a layered architecture diagram with narrative threat callout boxes showing only Critical/High findings in plain English. Position it immediately after the Executive Summary (pages 2–3) in the PDF report via a new Typst page template with early-page sequencing. Gate inclusion with a `has-executive-architecture` boolean for backward compatibility.

### Success Criteria
- PDF reports that include the executive architecture infographic place it on pages 2–3 (immediately after Executive Summary)
- The infographic is understood in ≤30 seconds by a non-technical executive
- All existing reports without the template continue to render identically (backward compatibility)
- Pipeline follows established patterns: deterministic extraction → spec → Gemini → PDF assembly

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's mission is making threat modeling accessible to teams without deep security expertise. This feature extends that mission to the executive audience — CISOs who consume the PDF report output. By presenting threat findings in a visual, narrative format on the earliest pages, we bridge the gap between technical threat analysis and executive decision-making.

### Roadmap Fit
This is the natural evolution of the infographic pipeline (F-018 → F-039 → F-048 → F-053 → F-071 → F-091 → **F-128**). Each iteration has expanded template coverage and report integration. F-128 is the first to address page positioning for audience-specific impact.

---

## Target Users & Personas

### Primary Persona: Security Consultant
- **Role**: Delivers security assessments to client organizations
- **Experience**: Deep security expertise, uses tachi for threat modeling
- **Goal**: Produce reports that drive executive action on security findings
- **Pain Point**: CISOs skim pages 1–3 and delegate the rest; critical visual findings are buried on page 10+

### Secondary Persona: CISO / Security Executive
- **Role**: Receives and acts on security assessment reports
- **Experience**: Business-oriented, limited time, low tolerance for dense technical content
- **Goal**: Quickly understand "where does our system break?" and allocate remediation budget
- **Pain Point**: Current reports require reading 10+ pages to reach visual threat summaries

---

## User Stories

### US-128-1: Early-Page Architecture Infographic in PDF
**When** I generate a PDF security report for a client presentation,
**I want to** include a layered architecture infographic with threat callouts on pages 2–3,
**So I can** ensure the CISO encounters the most critical threat visualization within the pages they actually read.

**Acceptance Criteria**:
- **Given** a threat model output with an executive-threat-architecture JPEG, **when** the PDF is compiled, **then** the infographic page appears immediately after the Executive Summary (before Attack Path Analysis and existing infographic pages)
- **Given** a threat model output without an executive-threat-architecture JPEG, **when** the PDF is compiled, **then** the report renders identically to current behavior (no empty page, no errors)
- **Given** findings of mixed severity, **when** the infographic is generated, **then** only Critical and High severity findings are included (max one per architectural layer)

### US-128-2: Executive Threat Architecture Template
**When** I run `/tachi.infographic` with the `executive-architecture` template,
**I want to** generate a portrait-layout infographic with layered architecture and narrative threat callouts,
**So I can** produce a CISO-ready visual that tells the story "here is the system, here is where it breaks."

**Acceptance Criteria**:
- **Given** a valid threat model output, **when** I run `/tachi.infographic --template executive-architecture`, **then** a spec file (`threat-executive-architecture-spec.md`) and JPEG (`threat-executive-architecture.jpg`) are generated
- **Given** the infographic spec, **then** it contains: layered architecture diagram, threat callout boxes (Critical/High only), plain English descriptions, pastel layer fills, red dashed-border callouts with warning icons
- **Given** 0 Critical/High findings, **when** the template is selected, **then** the extraction script reports "no qualifying findings" and the template is skipped gracefully

### US-128-3: Template Dispatch Integration
**When** I run `/tachi.infographic --template all`,
**I want to** the executive-architecture template to be included in the `all` expansion,
**So I can** generate all infographic templates in a single command invocation.

**Acceptance Criteria**:
- **Given** the `all` shorthand, **when** expanded, **then** it includes `executive-architecture` alongside the existing 5 templates
- **Given** the `executive-architecture` shorthand, **when** dispatched, **then** it maps to a single template (not a compound like `maestro`)

---

## Functional Requirements

### FR-1: Deterministic Data Extraction
**Description**: Extend `extract-infographic-data.py` with extraction logic for the `executive-architecture` template.

**Inputs**: `threats.md` (required), `risk-scores.md` or `compensating-controls.md` (optional enrichment via existing tier detection)
**Processing**:
- Parse architectural layers/components from DFD scope data (Section 1 of `threats.md`)
- Filter findings to Critical and High severity only
- Select top finding per architectural layer (by composite score or severity ordinal)
- Generate plain-English narrative callout text for each selected finding
**Outputs**: JSON payload with `layers[]`, `callouts[]`, `severity_distribution`, `top_findings[]`

**Business Rules**:
- Maximum one callout per architectural layer
- Callout text must be ≤25 words in plain English (no technical jargon)
- If no Critical/High findings exist, return empty payload with `skip: true`
- Follow existing tier detection order: compensating-controls.md > risk-scores.md > threats.md

### FR-2: Infographic Spec Generation
**Description**: Extend the `tachi-threat-infographic` agent to support the `executive-architecture` template.

**Spec Structure** (6 sections, matching existing templates):
1. Metadata (template name, tier, source file, timestamp)
2. Architecture Layers (ordered list with layer names and component counts)
3. Threat Callouts (per-layer Critical/High finding with narrative text)
4. Severity Distribution (filtered to Critical/High only)
5. Visual Layout Directives (portrait, pastel fills, red dashed callouts, warning icons)
6. Gemini Prompt Construction Notes

### FR-3: Gemini Image Generation
**Description**: Generate the infographic image via the existing Gemini API integration.

**Visual Requirements**:
- **Layout**: Portrait orientation (unlike existing landscape templates)
- **Architecture layers**: Horizontal bands with pastel fills, labeled with layer names
- **Threat callouts**: Red dashed-border boxes with warning icons, connected to relevant layers
- **Typography**: Large, readable text suitable for projection/printing
- **Style**: Inspired by architecture flow diagrams with attack surface annotations

### FR-4: PDF Report Integration — Early-Page Sequencing
**Description**: Add a new Typst page template positioned after the Executive Summary.

**Page Sequence Change**:
```
Current:  ... → Executive Summary → [Attack Paths] → [Infographics] → ...
Proposed: ... → Executive Summary → [Executive Architecture] → [Attack Paths] → [Infographics] → ...
```

**Implementation**:
- New Typst template file: `templates/tachi/security-report/executive-architecture.typ`
- New boolean flag: `has-executive-architecture` (set by `extract-report-data.py`)
- Image detection: `threat-executive-architecture.jpg` found and non-zero size
- Portrait layout (not landscape like existing infographic pages)

### FR-5: Report Assembler Updates
**Description**: Update artifact detection in `extract-report-data.py` and report assembler agent.

- Detect `threat-executive-architecture.jpg` in the output folder
- Set `has-executive-architecture: true` in `report-data.typ`
- Update artifact detection table in report assembler agent documentation

---

## Non-Functional Requirements

### Backward Compatibility
- All existing reports without `threat-executive-architecture.jpg` must render identically
- No changes to existing template extraction logic, spec format, or image generation
- Boolean gating (`has-executive-architecture`) follows established pattern
- No new required dependencies

### Performance
- Extraction for the new template adds ≤2 seconds to `extract-infographic-data.py` runtime
- No impact on extraction performance for other templates (independent code paths)

### Reliability
- Extraction script exit codes follow existing convention (0=success, 1=missing threats.md, 2=validation failure)
- Graceful skip when no Critical/High findings exist (empty payload, no error)
- Image generation failure does not block spec file creation (existing pattern)

---

## Success Metrics

### Primary Metrics
- **Template Generation Success Rate**: Executive-architecture spec + JPEG generated without errors on existing example threat models
- **PDF Page Position Accuracy**: Infographic appears on the page immediately after Executive Summary in all test PDFs
- **Backward Compatibility**: All 6 existing examples compile to identical PDFs when the new template is absent

### Adoption Metric
- **Template Usage**: `executive-architecture` included in `all` shorthand expansion, available as standalone template selection

---

## Scope & Boundaries

### In Scope (P0 — Must Have)
- New extraction logic in `extract-infographic-data.py` for `executive-architecture` template
- New infographic spec template in `tachi-threat-infographic` agent
- New Typst page template for early-page PDF positioning (portrait layout)
- `has-executive-architecture` boolean flag in `report-data.typ`
- Update `main.typ` page sequencing to insert after Executive Summary
- Update `extract-report-data.py` for image detection
- Update report assembler agent artifact detection table
- Update infographic agent/command/schema with new template
- Add `executive-architecture` to `all` shorthand expansion
- Regenerate example outputs for `agentic-app` with new template

### In Scope (P1 — Should Have)
- Update infographic skill references with new template documentation
- Add `exec` shorthand alias for `executive-architecture`

### Out of Scope
- Interactive/animated infographic variants (future consideration)
- Custom layer ordering configuration (use DFD order from threats.md)
- Multi-page executive architecture (constrained to single page)
- Changes to existing 5 infographic templates or their positioning

### Assumptions
- Architectural layers can be reliably parsed from DFD scope data in threats.md Section 1
- Portrait orientation works within the existing Typst `infographic-page()` function or a minor variant
- Gemini API can produce the described visual style with adequate prompt engineering
- One finding per layer provides sufficient executive-level detail

### Constraints
- Must follow the deterministic extraction pattern (no LLM in extraction pipeline)
- Must use existing Gemini API integration for image generation (no new API dependencies)
- Must be backward compatible with all 6 existing example outputs
- Conditional inclusion gated by boolean flag (established pattern)

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Portrait layout vs. existing landscape `infographic-page()` function
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: The Typst template can use a custom page layout distinct from `infographic-page()` — the executive architecture page is a report page, not a full-bleed landscape infographic
- **Contingency**: Fall back to landscape layout if portrait introduces page-break issues

**Risk 2**: Layer extraction from DFD scope data quality
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: DFD scope data is already parsed by the system-architecture template; reuse parsing logic
- **Contingency**: Fall back to component-level grouping if layer data is insufficient

### Dependencies

**Internal Dependencies**:
- **Feature 071** (Deterministic Extraction): Delivered — provides the extraction script framework
- **Feature 091** (MAESTRO Templates): Delivered — provides the most recent template addition pattern
- **Feature 112** (Attack Path Pages): Delivered — provides the most recent PDF page sequencing pattern
- **Feature 054** (PDF Booklet): Delivered — provides the Typst compilation framework

All dependencies are satisfied (delivered features).

---

## Open Questions

- [x] Should the executive architecture page use portrait or landscape? → **Portrait** (per Issue #128 spec, distinct from existing landscape infographics)
- [x] Should the template be included in `all` shorthand? → **Yes** (consistent with other core templates)
- [ ] Should the callout text be auto-generated from finding descriptions or require a narrative rewrite? — architect — TBD
- [ ] Should the page include a mini severity legend/key? — product-manager — TBD

---

## References

### Related PRDs
- [F-018: Threat Infographic Agent](018-threat-infographic-agent-2026-03-23.md)
- [F-039: Standalone /tachi.infographic Command](039-standalone-infographic-command-2026-03-28.md)
- [F-048: Infographic Tiered Detection & Residual Risk](048-infographic-tiered-detection-residual-risk-2026-03-28.md)
- [F-053: Risk Reduction Funnel](053-risk-reduction-funnel-2026-03-28.md)
- [F-071: Deterministic Infographic Extraction](071-deterministic-infographic-extraction-2026-03-30.md)
- [F-091: MAESTRO Infographic Templates and PDF Report Section](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md)
- [F-112: Attack Path Pages in Security Report PDF](112-attack-path-pages-in-pdf-2026-04-09.md)

### Technical Documentation
- [Architecture README](docs/architecture/README.md)
- [Constitution](.aod/memory/constitution.md)

### Pipeline Files
- Extraction script: `scripts/extract-infographic-data.py`
- Report extraction: `scripts/extract-report-data.py`
- Infographic agent: `.claude/agents/tachi/threat-infographic.md`
- Infographic command: `.claude/commands/tachi.infographic.md`
- Infographic schema: `schemas/infographic.yaml`
- Report main template: `templates/tachi/security-report/main.typ`
- Full-bleed page: `templates/tachi/security-report/full-bleed.typ`

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-09 | product-manager | Initial PRD |
