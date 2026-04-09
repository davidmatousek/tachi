---
prd:
  number: 112
  topic: attack-path-pages-in-pdf
  created: 2026-04-09
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "PRD aligns with product vision — completes the findings-to-stories narrative arc. Attack path pages make the PDF a self-contained board-ready deliverable."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. Use PNG (not SVG) for Typst compatibility. Place mmdc invocation in extract-report-data.py. Page placement after Executive Summary may need adjustment during spec — consider grouping with infographics."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "1 sprint realistic but tight. Template and extraction are parallelizable. mmdc subprocess error handling and image sizing are hidden complexity areas to address in spec."
source:
  idea_id: 112
  story_id: null
---

# Attack Path Pages in Security Report PDF

**Status**: Draft
**Created**: 2026-04-09
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Add dedicated pages in the security report PDF that visualize each Critical and High attack path with a diagram, narrative explanation, and remediation plan.

### Problem Statement
The tachi security report PDF currently presents findings as tabular data — severity-sorted rows with mitigation text. While thorough, this format fails to communicate attack *stories*. CISOs and board-level stakeholders need to understand how an attacker chains vulnerabilities together, not just see a list of individual findings. The attack tree diagrams already exist as standalone Mermaid code blocks in `threat-report.md` and `attack-trees/` files, but they are invisible in the PDF booklet.

### Proposed Solution
Render each Critical and High attack tree as a dedicated portrait page in the PDF report. Each page is self-contained: a rendered Mermaid diagram (converted to image), a narrative explanation of the attack chain, and a prioritized remediation plan. Pages are conditionally included only when attack tree artifacts exist.

### Success Criteria
- Every Critical and High finding with an attack tree gets a dedicated page in the PDF
- Each page includes: rendered diagram image, narrative explanation, and remediation steps
- Pages are conditionally included (no blank pages when attack trees are absent)
- Existing reports without attack trees continue to generate without errors

### Timeline
Single implementation phase, estimated at 1 sprint.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)

This feature directly advances tachi's mission of making threat modeling accessible to teams building agentic AI applications. By turning abstract findings into visual attack stories, we lower the bar for security communication — developers and CISOs alike can understand threat chains without deep security expertise.

### Roadmap Fit
This feature builds on the existing PDF security report pipeline (PRDs 054, 060, 067, 071, 091) and the threat report agent (PRD 015). It completes the "findings to stories" narrative arc by bringing attack trees into the final deliverable.

---

## Target Users & Personas

### Primary Persona: CISO / Security Leadership

**Demographics**:
- Role: Chief Information Security Officer, VP of Security, Security Director
- Experience: Senior leadership, broad security knowledge, limited time for detail
- Goals: Communicate specific risks to the board with clear context and actionable next steps
- Pain Points: Tabular findings don't tell a story; board members need visual, self-contained threat narratives

**Why This Matters to Them**:
Each attack path page is a board-ready slide — visual diagram, plain-English explanation, and concrete remediation. No translation needed.

### Secondary Persona: Security Engineer / Penetration Tester

**Demographics**:
- Role: Application security engineer, penetration tester
- Experience: Deep technical expertise, produces security assessments
- Goals: Deliver professional assessment reports that clearly communicate risk
- Pain Points: Current reports require supplementary materials to explain attack chains

**Why This Matters to Them**:
Attack path pages add professional polish to their deliverables and reduce follow-up questions from stakeholders.

---

## User Stories

### US-1: View Attack Path in PDF Report
**When**: I'm reviewing a tachi security assessment PDF and encounter a Critical or High finding,
**I want to**: See a dedicated page with the attack tree diagram, narrative explanation, and remediation plan,
**So I can**: Understand the full attack chain and communicate it to my board with clear context.

**Acceptance Criteria**:
- **Given** a `threat-report.md` with attack trees for Critical/High findings, **when** the PDF is generated, **then** each attack tree appears as a dedicated portrait page after the Executive Summary section
- **Given** an attack path page, **when** I view it, **then** it contains: (1) the finding ID and title as heading, (2) a rendered diagram image, (3) a narrative explanation of the attack chain, (4) specific remediation steps
- **Given** a report with no attack tree artifacts, **when** the PDF is generated, **then** no attack path pages are included and no errors occur

**Priority**: P0
**Effort**: L

### US-2: Attack Path Page Ordering
**When**: I'm reading through multiple attack path pages in the PDF,
**I want to**: See them ordered by severity (Critical first, then High) and then by finding ID,
**So I can**: Focus on the most dangerous attack chains first.

**Acceptance Criteria**:
- **Given** multiple attack trees exist, **when** the PDF is generated, **then** pages are ordered: Critical findings first (by ID), then High findings (by ID)
- **Given** a single Critical finding with an attack tree, **when** the PDF is generated, **then** exactly one attack path page appears

**Priority**: P0
**Effort**: S

### US-3: Mermaid Diagram Rendering
**When**: The PDF generation pipeline encounters a Mermaid attack tree code block,
**I want to**: See the diagram rendered as a high-quality image (not raw code),
**So I can**: Understand the attack flow visually without needing a Mermaid renderer.

**Acceptance Criteria**:
- **Given** a Mermaid flowchart code block from an attack tree file, **when** the extraction script runs, **then** the Mermaid code is converted to a PNG/SVG image file
- **Given** a rendered diagram image, **when** it appears on the attack path page, **then** it is legible at A4/Letter page size with the standard color scheme (red goals, orange AND gates, teal OR gates, green leaves)
- **Given** a Mermaid code block that fails to render, **when** the pipeline runs, **then** the attack path page is still included with the raw Mermaid code as a fallback

**Priority**: P0
**Effort**: M

---

## Functional Requirements

### FR-1: Attack Tree Data Extraction

**Description**: Extend `scripts/extract-report-data.py` to detect and extract attack tree content from standalone files.

**Inputs**:
- `attack-trees/` directory containing `{finding-id}-attack-tree.md` files
- `threat-report.md` Section 5 (Attack Trees) as fallback source

**Processing**:
1. Scan for `attack-trees/*.md` files (primary source)
2. Fall back to inline attack trees in `threat-report.md` Section 5 if no standalone files exist
3. For each attack tree, extract: finding ID, title/component, severity, Mermaid code block, and correlated threat description
4. Cross-reference with findings data to get severity level for ordering

**Outputs**:
- Attack tree entries in `report-data.typ` with: finding ID, title, severity, Mermaid image path, narrative text, remediation steps
- Boolean flag `has-attack-trees` for conditional page inclusion

**Business Rules**:
- Only Critical and High severity findings are included (matching threat-report agent's filter)
- Order by severity (Critical first) then by finding ID
- Maximum page count: one page per qualifying finding (no multi-page trees)

### FR-2: Mermaid-to-Image Conversion

**Description**: Convert Mermaid code blocks into image files suitable for Typst embedding.

**Processing**:
1. Use `mmdc` (Mermaid CLI) or equivalent to render Mermaid code to PNG/SVG
2. Apply the standard tachi color scheme (already embedded in Mermaid style definitions)
3. Output images to a temporary directory for Typst consumption

**Business Rules**:
- If `mmdc` is unavailable, skip image rendering and include raw Mermaid code as preformatted text
- Images should target A4-width readability (~170mm effective width)
- Graceful degradation: failed renders produce a warning, not a pipeline abort

### FR-3: Attack Path Typst Page Template

**Description**: New `attack-path.typ` page template for the security report.

**Layout** (portrait, A4/Letter):
- **Header**: Finding ID badge (color-coded by severity) + Finding title
- **Diagram Section**: Rendered attack tree image, centered, scaled to fit (~60% of page height)
- **Narrative Section**: 2-4 sentence explanation of how the attack chain works
- **Remediation Section**: Bulleted list of specific, actionable remediation steps
- **Footer**: Standard page numbering

**Business Rules**:
- Each finding gets exactly one page (no overflow)
- If diagram is too large, scale down proportionally to fit the diagram section
- Narrative and remediation text derived from threat-report.md content and finding mitigation field

### FR-4: Report Page Sequencing

**Description**: Insert attack path pages into the existing PDF report sequence.

**Sequence**:
1. Cover → Disclaimer → TOC → Risk Methodology → Assessment Scope → Executive Summary
2. **Attack Path Pages** (NEW — conditionally included)
3. Findings Detail → Infographics → Control Coverage → Remediation Roadmap → MAESTRO Findings

**Business Rules**:
- Conditional: only included when `has-attack-trees` is true
- Section header page "Attack Path Analysis" before the first attack path page
- TOC updated to include attack path section when present

---

## Non-Functional Requirements

### Performance
- Mermaid rendering: <5s per diagram (most trees have <20 nodes)
- No measurable impact on PDF generation time when attack trees are absent
- Total PDF generation increase: <30s for a report with 5 attack path pages

### Compatibility
- Backward compatible: existing reports without attack trees generate identically
- Forward compatible: new attack tree format additions don't break the template
- Graceful degradation: missing `mmdc` tool produces text fallback, not failure

### Maintainability
- Follows existing conditional page pattern (`has-X` boolean flags in `report-data.typ`)
- Follows existing Typst template conventions (separate `.typ` file per page type)
- Reuses existing finding data structures — no new schemas required

---

## Success Metrics

### Primary Metrics

**Attack Path Page Coverage**:
- **Definition**: Percentage of Critical/High findings with attack trees that appear as PDF pages
- **Target**: 100% (every qualifying finding gets a page)

**Pipeline Reliability**:
- **Definition**: PDF generation success rate with attack path pages enabled
- **Target**: 100% (no regressions from this feature)

### User Satisfaction Metrics

**Report Completeness**:
- **Definition**: Users perceive the PDF as a complete, self-contained security assessment
- **Target**: No supplementary materials needed to explain attack chains

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Attack tree data extraction from standalone files and threat-report.md fallback
- Mermaid-to-image conversion with graceful fallback
- Portrait page template with diagram, narrative, and remediation sections
- Conditional page inclusion in report sequence
- Severity-ordered page sequencing (Critical first, then High)
- TOC integration

**Should Have (P1)**:
- Section header page ("Attack Path Analysis") before first attack path page
- Color-coded severity badges on page headers

### Out of Scope

**Won't Have**:
- Interactive/clickable diagrams in PDF (PDF is static)
- Medium/Low severity attack path pages (these don't get attack trees)
- Multi-page attack trees (one page per finding)
- Custom diagram styling per finding (uses standard tachi color scheme)
- Attack tree generation — trees must already exist from the threat-report agent

### Assumptions

- `mmdc` (Mermaid CLI) is available in the build environment, or users accept text fallback
- Attack tree files follow the existing naming convention: `{finding-id}-attack-tree.md`
- Mermaid code blocks in attack tree files are syntactically valid (validated by threat-report agent)
- Existing Typst compilation workflow supports additional portrait pages without configuration changes

### Constraints

**Technical Constraints**:
- Typst does not natively render Mermaid — requires pre-rendering to image format
- A4 page size limits diagram complexity (trees with >20 nodes may need scaling)
- Mermaid CLI requires Node.js runtime

**External Dependencies**:
- `mmdc` (Mermaid CLI) for diagram rendering — npm package `@mermaid-js/mermaid-cli`
- Existing `threat-report` agent must have generated attack trees

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Mermaid CLI unavailability in user environments
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Implement graceful fallback to raw Mermaid code as preformatted text block
- **Contingency**: Document mmdc installation in tachi setup guide

**Risk 2**: Large attack trees don't fit on a single page
- **Likelihood**: Low (threat-report agent caps at ~20 nodes)
- **Impact**: Low
- **Mitigation**: Scale diagram proportionally to fit; enforce max node count in threat-report agent
- **Contingency**: Truncate leaf nodes with "..." indicator

### Dependencies

**Internal Dependencies**:
- **Threat Report Agent** (PRD 015): Must generate attack trees in expected format
- **Report Assembler Agent**: Page sequencing logic must be updated
- **Extract Report Data Script** (PRD 067): Must be extended for attack tree extraction
- **Security Report Command**: Artifact detection must include attack tree files

**Dependency Graph**:
```
[Attack Path Pages]
  +-- Depends on: threat-report agent (attack tree generation)
  +-- Depends on: extract-report-data.py (data extraction)
  +-- Depends on: report-assembler agent (page sequencing)
  +-- Depends on: security-report command (artifact detection)
  +-- External: mmdc (Mermaid CLI) for image rendering
```

---

## Open Questions

- [x] Where should attack path pages appear in the report sequence? **Answer**: After Executive Summary, before Findings Detail — positions attack stories as the narrative bridge between summary and raw data
- [ ] Should the section header page include a mini-table listing all attack paths with page references? - product-manager - 2026-04-16 - Open
- [x] What image format (PNG vs SVG) works best with Typst for diagram rendering? **Answer**: PNG at 2x resolution (`mmdc -s 2`). Typst's SVG support is inconsistent with complex Mermaid styles; existing pipeline uses PNG/JPEG exclusively.

---

## References

### Related PRDs
- [PRD 015: Threat Report Agent & Attack Trees](015-threat-report-agent-attack-trees-2026-03-23.md) — attack tree generation
- [PRD 054: Security Assessment PDF Booklet](054-security-assessment-pdf-booklet-2026-03-28.md) — original PDF pipeline
- [PRD 060: Professional PDF Security Report Branding](060-professional-pdf-security-report-branding-2026-03-29.md) — branding and layout
- [PRD 067: Deterministic Report Data Extraction](067-deterministic-report-data-extraction-2026-03-30.md) — data extraction patterns
- [PRD 091: MAESTRO Infographic Templates and PDF Report Section](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md) — most recent PDF page addition

### Technical Documentation
- [Product Vision](../01_Product_Vision/product-vision.md)
- [Constitution](.aod/memory/constitution.md)

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-04-09 | Completes findings-to-stories narrative arc |
| Architect | architect | 🟡 Approved with Concerns | 2026-04-09 | Use PNG; mmdc in extract script; page placement TBD in spec |
| Team Lead | team-lead | 🟡 Approved with Concerns | 2026-04-09 | 1 sprint realistic; subprocess error handling needs spec detail |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-09 | product-manager | Initial PRD |
