---
prd:
  number: "054"
  topic: security-assessment-pdf-booklet
  created: 2026-03-28
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "PRD authored by PM. Capstone of visualization arc — assembles all pipeline artifacts into single executive deliverable. All reviewer concerns addressed in PRD revision."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Typst is correct technology choice. 5 concerns (1 medium, 3 low, 1 info): 16:9 aspect ratio on landscape pages resolved with custom page dimensions; output filename specified as security-report.pdf; schema version handling clarified; template directory organization noted for spec. Recommend ADR for Typst adoption."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Timeline updated to 2-3 sessions (from 1-2). Typst POC validation required as Wave 1 gate. US Letter only for Phase 1, PDF/A deferred to P2. Parsing interface contract must be defined before Wave 2 parallelization. 70% confidence at 3 sessions."
source:
  idea_id: 54
  story_id: null
---

# Security Assessment PDF Booklet — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-28
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)
**Source**: GitHub Issue #54

---

## Executive Summary

### The One-Liner
A new `/security-report` command that assembles all generated threat model artifacts into a designed, multi-page PDF booklet suitable for board presentations, compliance audits, and stakeholder distribution.

### Problem Statement
After running tachi's full pipeline (`/threat-model` → `/risk-score` → `/compensating-controls` → `/infographic`), users have 8-12 separate files: markdown reports, SARIF files, infographic images, and attack trees. No single deliverable exists. To present findings to a board, CISO, or compliance auditor, users must manually copy-paste into PowerPoint or Google Slides. Every commercial threat modeling tool has the same gap — they produce CSV dumps, HTML pages, or flat tabular PDFs. No tool generates a designed, premium, multi-page PDF booklet combining infographic-quality visualizations with structured findings data.

### Proposed Solution
Add a `/security-report` command that auto-detects all available artifacts in a security output directory and assembles them into a cohesive, professionally designed PDF booklet using Typst (a modern typesetting engine). The booklet includes up to 9 page types — cover, executive summary, three full-bleed infographic pages, findings detail, control coverage, remediation roadmap, and optional progression pages. Pages are included only when their source artifact exists, enabling graceful degradation from a full-pipeline booklet down to a minimal threat-only report.

### Success Criteria
- `/security-report` produces a valid PDF from any combination of available artifacts (minimum: `threats.md` alone)
- Full-bleed infographic pages render at print quality (no borders, no scaling artifacts)
- PDF is boardroom-ready: professional typography, consistent color palette, proper pagination
- Generation completes in <30 seconds for a typical 34-finding threat model
- Command follows existing tachi patterns: auto-detect input directory, `--output-dir` flag

### Timeline
Single-phase implementation — estimated 2-3 sessions. Typst is a new technology dependency with no prior usage in the codebase; a Wave 1 proof-of-concept validates full-bleed rendering, mixed orientation, and conditional pages before full template authoring begins. Command scaffolding and artifact detection follow established patterns.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's mission is to be the default threat modeling toolkit for teams building agentic AI applications. The pipeline currently excels at analysis (threat identification, risk scoring, control detection, visual synthesis) but falls short at the final mile: distribution. Security findings that stay in a developer's terminal don't drive organizational change. A designed PDF booklet transforms tachi's output from developer artifacts into executive deliverables — the format that drives budget decisions, compliance approvals, and security program adoption.

### Roadmap Fit
Builds on the complete delivered artifact pipeline:
- **PRD-003** (Orchestrator Agent) — `threats.md`, `threat-report.md` generation
- **PRD-012** (SARIF Output) — machine-readable findings
- **PRD-015** (Threat Report & Attack Trees) — narrative report, remediation roadmap
- **PRD-035** (Quantitative Risk Scoring) — `risk-scores.md` with 4D scoring
- **PRD-036** (Compensating Controls) — `compensating-controls.md` with residual risk
- **PRD-039** (Standalone /infographic) — template system, Gemini image generation
- **PRD-048** (Tiered Detection & Residual Risk) — 3-tier auto-detection hierarchy
- **PRD-053** (Risk Reduction Funnel) — 4-tier funnel infographic template

This feature is the capstone of the visualization arc — assembling everything into one deliverable.

---

## Target Users & Personas

### Primary Persona: CISO / VP Security

**Demographics**:
- Role: Chief Information Security Officer or VP of Security
- Experience: Senior leadership, non-technical day-to-day, strategic decision-maker
- Goals: Communicate security posture to board, justify security investments, demonstrate compliance
- Pain Points: Receives fragmented technical artifacts that require manual assembly for presentation

**Why This Matters to Them**:
One command produces a boardroom-ready document they can attach to a board report, email to the audit committee, or present at a quarterly business review — no PowerPoint assembly required.

### Secondary Persona: Security Consultant

**Demographics**:
- Role: External security consultant or penetration tester
- Experience: Deep technical expertise, client-facing deliverable expectations
- Goals: Deliver professional, branded security assessment reports to clients
- Pain Points: Spends hours formatting findings into presentable documents; current tools produce ugly exports

**Why This Matters to Them**:
Transforms tachi output into a client-ready deliverable that looks like it came from a premium security consultancy, not a terminal window.

### Tertiary Persona: Compliance Officer

**Demographics**:
- Role: Compliance analyst or audit evidence manager
- Experience: Regulatory expertise, documentation-focused
- Goals: Include structured security assessments in audit evidence packages
- Pain Points: Needs complete, self-contained documents with cover page, executive summary, and detailed findings

**Why This Matters to Them**:
Produces a self-contained document that satisfies audit evidence requirements without additional formatting or assembly.

---

## User Stories

### US-1: Single-Command PDF Generation
**When**: I have completed a tachi threat model pipeline and have artifacts in a directory
**I want to**: Run a single command to generate a PDF booklet from all available artifacts
**So I can**: Distribute one professional document instead of managing multiple files

**Acceptance Criteria**:
- **Given** a directory with `threats.md`, **when** `/security-report` is run, **then** a PDF is generated with cover + executive summary + findings detail pages
- **Given** a directory with all artifacts (threats, risk-scores, compensating-controls, 3 infographic images), **when** `/security-report` is run, **then** all 8 page types are included
- **Given** a directory with no recognized artifacts, **when** `/security-report` is run, **then** a clear error message explains what's needed

**Priority**: P0
**Effort**: L

### US-2: Full-Bleed Infographic Pages
**When**: I have infographic JPEG images generated by `/infographic`
**I want to**: See them rendered as full-bleed pages in the PDF (edge-to-edge, no margins)
**So I can**: Present high-impact visuals to stakeholders without cropping or white borders

**Acceptance Criteria**:
- **Given** `threat-risk-funnel.jpg` exists, **when** PDF is generated, **then** page 3 renders the image full-bleed at 16:9 aspect ratio
- **Given** `threat-baseball-card.jpg` exists, **when** PDF is generated, **then** page 4 renders the image full-bleed
- **Given** `threat-system-architecture.jpg` exists, **when** PDF is generated, **then** page 5 renders the image full-bleed
- **Given** no infographic images exist, **when** PDF is generated, **then** those pages are omitted entirely (not blank pages)

**Priority**: P0
**Effort**: M

### US-3: Graceful Degradation
**When**: I have only partially completed the tachi pipeline (e.g., only `/threat-model` without `/risk-score`)
**I want to**: Still generate a valid PDF booklet with whatever artifacts exist
**So I can**: Get value from the report even without running the full pipeline

**Acceptance Criteria**:
- **Given** only `threats.md`, **when** PDF is generated, **then** booklet contains: cover, executive summary (from threats.md metadata), findings detail table
- **Given** `threats.md` + `risk-scores.md`, **when** PDF is generated, **then** booklet adds scored findings with severity distribution
- **Given** `threats.md` + `risk-scores.md` + `compensating-controls.md`, **when** PDF is generated, **then** booklet adds control coverage and remediation roadmap pages
- **Given** any artifact combination + infographic images, **when** PDF is generated, **then** corresponding full-bleed pages are included

**Priority**: P0
**Effort**: M

### US-4: Professional Design
**When**: I am presenting security findings to executives or external stakeholders
**I want to**: A PDF that looks professionally designed with consistent typography, colors, and layout
**So I can**: Build credibility for the security program and the assessment quality

**Acceptance Criteria**:
- **Given** a generated PDF, **when** opened, **then** cover page shows project name, assessment date, classification level, and tachi branding
- **Given** a generated PDF, **when** reviewed, **then** all text pages use consistent serif/sans-serif typography pairing
- **Given** a generated PDF, **when** reviewed, **then** findings tables use the tachi severity color palette (Critical=red, High=orange, Medium=yellow, Low=blue)
- **Given** a generated PDF, **when** reviewed, **then** pages have consistent headers, footers, and page numbers

**Priority**: P1
**Effort**: M

---

## Functional Requirements

### Core Capabilities

#### FR-1: Artifact Auto-Detection
**Description**: Scan a target directory and detect all available tachi artifacts.

**Detection Matrix** (ordered by pipeline stage):

| Artifact | File Pattern | Required | Page(s) Enabled |
|----------|-------------|----------|-----------------|
| `threats.md` | `threats.md` | Yes (minimum) | Cover, Executive Summary, Findings Detail |
| `threat-report.md` | `threat-report.md` | No | Executive Summary (enriched), Remediation Roadmap |
| `risk-scores.md` | `risk-scores.md` | No | Findings Detail (scored), Executive Summary (severity distribution) |
| `compensating-controls.md` | `compensating-controls.md` | No | Control Coverage, Remediation Roadmap (enriched) |
| Risk Funnel image | `threat-risk-funnel.jpg` | No | Risk Funnel (full bleed) |
| Baseball Card image | `threat-baseball-card.jpg` | No | Baseball Card (full bleed) |
| System Architecture image | `threat-system-architecture.jpg` | No | System Architecture (full bleed) |

**Business Rules**:
- `threats.md` is the minimum required artifact — abort with error if not found
- Follow the same directory detection pattern as existing commands (current directory, explicit path, or `--output-dir`)
- Report which artifacts were detected and which pages will be generated before PDF assembly

#### FR-2: Page Assembly Engine
**Description**: Assemble detected artifacts into a sequenced PDF booklet.

**Page Sequence** (pages included only if source artifact exists):

| Order | Page | Source Artifact | Layout |
|-------|------|----------------|--------|
| 1 | Cover | `threats.md` metadata (project name, date, classification) | Branded cover, centered text |
| 2 | Executive Summary | `threat-report.md` Section 1 OR `threats.md` risk summary | Two-column metrics + narrative |
| 3 | Risk Funnel | `threat-risk-funnel.jpg` | Full bleed, landscape |
| 4 | Baseball Card | `threat-baseball-card.jpg` | Full bleed, landscape |
| 5 | System Architecture | `threat-system-architecture.jpg` | Full bleed, landscape |
| 6 | Findings Detail | `compensating-controls.md` > `risk-scores.md` > `threats.md` (3-tier preference) | Severity-sorted table |
| 7 | Control Coverage | `compensating-controls.md` Section 2 | Coverage matrix + status table |
| 8 | Remediation Roadmap | `compensating-controls.md` Section 3 OR `threat-report.md` remediation section | Prioritized action table with SLAs |
| 9+ | Progression (optional) | Multiple timestamped run directories | Before/after comparison |

**Business Rules**:
- Pages maintain the sequence above; missing pages are skipped (no gaps or blank pages)
- Full-bleed infographic pages use custom page dimensions matching 16:9 aspect ratio (e.g., 11" x 6.1875") to avoid cropping or letterboxing; text pages use US Letter portrait with standard print margins
- Page numbering adjusts dynamically based on included pages
- Executive Summary adapts content richness based on available sources (richer with `threat-report.md`, minimal with `threats.md` alone)

#### FR-3: Typst-Based PDF Generation
**Description**: Use Typst as the PDF generation engine for reproducibility and portability.

**Inputs**: Typst template files (.typ) + extracted artifact data (parsed markdown → Typst variables)
**Processing**: Parse markdown artifacts → extract structured data → inject into Typst templates → compile to PDF
**Outputs**: `security-report.pdf` in the output directory

**Business Rules**:
- Typst must be invoked via CLI (`typst compile`) — no browser dependency
- Template files stored in `templates/security-report/` within tachi (separate from existing markdown reference templates, with README distinguishing rendering templates from reference templates)
- If Typst is not installed, provide clear error message with installation instructions for all platforms (`brew install typst`, `cargo install typst-cli`, `winget install typst`)
- Typst compilation must complete in <30 seconds for a typical report
- Pin to Typst version range 0.11.x-0.12.x (pre-1.0 API may have breaking changes between minors)

#### FR-4: Cover Page Generation
**Description**: Generate a professional cover page from artifact metadata.

**Data Sources**:
- Project name: from `threats.md` frontmatter `classification` field or directory name
- Assessment date: from `threats.md` frontmatter `date` field
- Classification: from `threats.md` frontmatter `classification` field (e.g., "CONFIDENTIAL")
- Risk posture: from `compensating-controls.md` executive summary (if available) or `threats.md` risk summary
- Finding counts: from highest-available artifact's finding counts

#### FR-5: Findings Detail Table
**Description**: Render a severity-sorted findings table using 3-tier data source preference.

**3-Tier Data Source Preference** (matches existing pattern):
1. `compensating-controls.md` — includes residual scores, control status, recommendations
2. `risk-scores.md` — includes 4D scores (CVSS, exploitability, scalability, reachability)
3. `threats.md` — qualitative findings (likelihood, impact, risk level)

**Table Columns by Tier**:
- **Tier 1** (compensating-controls): ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation
- **Tier 2** (risk-scores): ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability
- **Tier 3** (threats): ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation

### Data Requirements

**Data Model**: No persistent data model. All data is parsed at generation time from existing markdown artifacts.

**Parsing Requirements**:
- Parse YAML frontmatter from all markdown artifacts
- Parse markdown tables into structured data
- Parse section headers to locate specific content blocks (e.g., "Executive Summary", "Remediation Roadmap")
- Handle schema version differences gracefully: v1.0 `threats.md` lacks Section 4a (Correlated Findings) — omit correlated findings from executive summary but generate all other pages normally. SARIF files may serve as structured data fallback for the Findings Detail table but not for narrative pages.

### Integration Requirements

**External Dependencies**:
- **Typst CLI**: Required for PDF compilation. Version 0.11+ recommended.
- **Existing tachi artifacts**: All source data comes from previously generated tachi output files.

**Command Interface**:
```
/security-report [PATH] [--output-dir DIR] [--title "Custom Title"]
```

- `PATH`: Directory containing tachi artifacts (default: current directory)
- `--output-dir`: Output directory for the PDF (default: same as input)
- `--title`: Override the project name on the cover page

---

## Non-Functional Requirements

### Performance Requirements
- PDF generation: <30 seconds for a 34-finding report with 3 infographic images
- Markdown parsing: <2 seconds for all artifacts combined
- Typst compilation: <15 seconds for a 10-page booklet

### Reliability Requirements
- Graceful degradation when artifacts are missing (never crash, always produce a valid PDF)
- Clear error messages when Typst is not installed or compilation fails
- Idempotent: running twice on the same artifacts produces identical output

### Portability Requirements
- Typst runs on macOS, Linux, and Windows — no platform-specific dependencies
- No browser dependency (unlike Puppeteer/Playwright alternatives)
- PDF output is universally readable (PDF/A compliance deferred to Phase 2 — Typst may not support it natively)

### Security Requirements
- No data leaves the local machine — all processing is local
- Classification markings from artifact metadata are rendered on every page header/footer
- No external network calls during PDF generation

---

## Success Metrics

### Primary Metrics
- **Artifact Coverage**: % of available artifacts successfully included in PDF (target: 100%)
- **Generation Reliability**: % of runs that produce a valid PDF without errors (target: >99%)
- **Graceful Degradation**: Successful PDF generation from threats.md alone (binary: works or doesn't)

### User Satisfaction Metrics
- **Distribution Format Adoption**: Users generating PDFs vs. sharing raw markdown (target: >50% of pipeline completions trigger `/security-report`)
- **Design Quality**: PDF is used without additional PowerPoint formatting (qualitative)

---

## Scope & Boundaries

### In Scope (Phase 1)

**Must Have (P0)**:
- Artifact auto-detection with graceful degradation
- 8 page types: cover, executive summary, 3 full-bleed infographic pages, findings detail, control coverage, remediation roadmap
- Typst template system with professional design
- `/security-report` command following existing tachi patterns
- Clear error handling for missing Typst or missing minimum artifacts

**Should Have (P1)**:
- `--title` flag for custom cover page title
- Classification markings on page headers/footers
- Consistent severity color palette across all pages
- Dynamic page numbering

### Out of Scope (Future Phases)

**Could Have (P2)** - Not in Phase 1:
- Progression/trend pages comparing multiple assessment runs
- Custom branding/logo injection via configuration
- HTML report output as alternative to PDF
- Interactive PDF features (clickable table of contents, hyperlinks to findings)

**Won't Have** - Explicitly excluded:
- PowerPoint/PPTX export (different format, different tool)
- Real-time report generation (this is a batch/offline operation)
- Cloud-based report generation (local-first, per constitution Principle III)
- Custom page templates (fixed page structure in Phase 1)

### Assumptions
- Typst is available or installable on the user's machine
- Source artifacts follow tachi's documented schemas (v1.0/v1.1)
- Infographic images are JPEG format at 16:9 aspect ratio (as generated by `/infographic`)

### Constraints

**Technical Constraints**:
- Typst template language capabilities (no arbitrary code execution, declarative layout)
- Image embedding in Typst requires file path references (images must be accessible at compile time)
- PDF page size: US Letter (8.5" x 11") portrait for text pages; custom 16:9 page dimensions for full-bleed infographic pages. A4 support deferred to Phase 2.

**External Dependencies**:
- **Typst CLI**: User must install separately (`brew install typst`, `cargo install typst-cli`, or binary download)

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Typst image handling limitations
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Test full-bleed image rendering early in implementation. Typst supports image embedding and page geometry control natively.
- **Contingency**: If full-bleed proves impossible in Typst, use zero-margin pages with image scaling to fit.

**Risk 2**: Markdown parsing complexity
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Implement a focused markdown-to-Typst data extractor that targets known tachi artifact schemas rather than generic markdown parsing.
- **Contingency**: Use SARIF files as structured data source fallback (JSON is easier to parse than markdown).

**Risk 3**: Mixed page orientation (portrait text + landscape infographics)
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Typst supports per-page geometry changes. Test orientation switching early.
- **Contingency**: Render all pages in landscape if mixed orientation proves unreliable.

### Dependencies

**Internal Dependencies**:
- All artifact-producing commands (PRD-003 through PRD-053) — **Delivered**
- Schema definitions in `schemas/` — **Delivered**
- Infographic template system (PRD-039, PRD-048, PRD-053) — **Delivered**

**External Dependencies**:
- **Typst CLI** (v0.11+): User-installed prerequisite

---

## Open Questions

- [x] Typst vs Puppeteer? — Typst preferred (no browser dependency, reproducible, portable) — **Answered**
- [x] Should the command scaffold a Typst template that users can customize, or use a fixed internal template? — Phase 1 uses fixed template; P2 could add customization — **Answered**
- [x] PDF page size: US Letter only, or support A4 via flag? — US Letter only for Phase 1; A4 deferred to P2 — **Answered (Architect + Team-Lead review)**
- [x] PDF/A compliance? — Deferred to P2; Typst may not support it natively — **Answered (Team-Lead review)**
- [x] Should attack tree Mermaid diagrams be rendered as images and included as pages? — Deferred to P2 — **Answered**
- [ ] Should a schema file (`schemas/security-report.yaml`) be created defining input-to-output mapping and page inclusion rules? — architect — Recommend yes for consistency with existing commands — **Address in spec**

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)

### Technical Documentation
- Constitution: [constitution.md](../../../.aod/memory/constitution.md)
- Threat Model Schema: `schemas/output.yaml` (v1.1)
- Risk Scoring Schema: `schemas/risk-scoring.yaml` (v1.0)
- Compensating Controls Schema: `schemas/compensating-controls.yaml` (v1.0)
- Infographic Schema: `schemas/infographic.yaml` (v1.0)

### External Resources
- Typst Documentation: https://typst.app/docs
- Typst CLI: https://github.com/typst/typst

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | APPROVED | 2026-03-28 | PRD authored by PM. Capstone feature. All concerns addressed. |
| Architect | architect | APPROVED_WITH_CONCERNS | 2026-03-28 | Typst approved. 5 concerns addressable in spec phase. Recommend ADR for Typst adoption. |
| Engineering Lead | team-lead | APPROVED_WITH_CONCERNS | 2026-03-28 | Timeline 2-3 sessions. Typst POC gate required. 70% confidence. |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-28 | product-manager | Initial PRD |
