---
prd:
  number: "091"
  topic: maestro-infographic-templates-and-pdf-report-section
  created: 2026-04-08
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-08, status: APPROVED, notes: "2 LOW findings (risk-funnel doc gap acknowledgment, qualitative AC in US-01), 1 INFORMATIONAL (PRD 084 open question #1 still open). Clean extension of Feature 084 with clear user value for two personas." }
  architect_signoff: { agent: architect, date: 2026-04-08, status: APPROVED_WITH_CONCERNS, notes: "4 findings (0 blocking, 1 medium, 3 low). Medium: extraction source gap (Section 7 lacks MAESTRO column) — addressed in PRD with Section 6 summary + Section 3 per-finding mapping approach. Low: Tier 2/1 MAESTRO absence, missing Typst per-finding variable (both addressed), Section 3 column variation risk (added)." }
  techlead_signoff: { agent: team-lead, date: 2026-04-08, status: APPROVED_WITH_CONCERNS, notes: "3-day estimate feasible (80% confidence). 2 medium findings (CLI choices hardcoded, contract reference ripple) — both addressed in PRD. 3-wave parallel execution strategy: Wave 1 templates+extraction, Wave 2 integration, Wave 3 docs+validation." }
source:
  idea_id: 91
  story_id: null
---

# MAESTRO Infographic Templates and PDF Report Section

**Status**: Approved
**Created**: 2026-04-08
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High Confidence, Moderate Impact)
**Evidence**: LinkedIn thread -- Marco M. (Founder, Threat Modeling Academy / Field CISO) asked about MAESTRO for agentic AI threat modeling. Design research on 2026-04-07 identified that Feature 084's pipeline-level MAESTRO support needs corresponding visualization in infographics and PDF reports.

---

## Executive Summary

### The One-Liner
Visualize MAESTRO layer risk distribution through two new infographic templates and a dedicated PDF report page so security teams can see at a glance which layers of their AI stack carry the most threat exposure.

### Problem Statement
Feature 084 added MAESTRO seven-layer classification to every finding in the tachi pipeline, but this data has no visual representation. Security teams reviewing infographics and PDF reports cannot answer "which architectural layer carries the most risk?" without manually scanning tabular findings. CISOs and management need a layer-stack overview; security engineers need a component-by-layer heatmap. Neither audience is served by the existing baseball-card and system-architecture templates, which organize findings by STRIDE category and trust boundary -- not by MAESTRO layer.

### Proposed Solution
Add two new infographic templates (maestro-stack and maestro-heatmap), a full-page Typst PDF section (`maestro-findings.typ`), and MAESTRO-aware data extraction to the existing Python script. A `--infographic-template maestro` shorthand generates both MAESTRO templates in one flag. All new sections are gated by a `has-maestro-data` flag for backward compatibility when MAESTRO data is absent.

### Success Criteria
- Both MAESTRO infographic templates generate correctly from example architectures with MAESTRO data
- PDF report includes MAESTRO findings page when `has-maestro-data` is true
- Empty state renders gracefully when no MAESTRO data is present
- Existing templates (baseball-card, system-architecture, risk-funnel) are unaffected
- `--infographic-template maestro` shorthand generates both MAESTRO templates
- INFOGRAPHIC_TEMPLATES.md documents new templates with placeholders and output files

### Timeline
Estimated 3 days -- two infographic templates, one Typst page, extraction script extension, skill dispatch update, and documentation.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

tachi's vision is "the default threat modeling toolkit for any team building agentic AI applications." Feature 084 added MAESTRO classification; this feature completes the story by making that data visible. Security teams that adopted MAESTRO as their architectural taxonomy (per CSA guidance) will see tachi natively render findings in their mental model -- strengthening tachi's position as the agentic AI threat modeling standard.

### Dependency on Feature 084
**Reference**: [PRD 084](docs/product/02_PRD/084-maestro-layer-mapping-2026-04-07.md)

This feature is a direct extension of Feature 084 (MAESTRO Layer Mapping), which added the `maestro_layer` field to the finding IR, keyword classification in the orchestrator, and downstream propagation. Feature 084 was delivered on 2026-04-08. All MAESTRO data consumed by this feature originates from Feature 084's pipeline output.

---

## Target Users & Personas

### Primary Persona: CISO / Security Management
- **Role**: Chief Information Security Officer, VP Security, Security Manager
- **Experience**: Strategic decision-maker, evaluates risk posture across organizational layers
- **Goals**: Understand which architectural layers carry the most risk exposure
- **Pain Points**: Tabular findings lack spatial/architectural context; cannot quickly brief executives on layer-level risk
- **Template**: maestro-stack (vertical layer diagram)

### Secondary Persona: Security Engineer
- **Role**: Application Security Engineer, Threat Modeling Practitioner
- **Experience**: Hands-on security assessment, component-level analysis
- **Goals**: Identify component/layer intersections with highest severity concentration
- **Pain Points**: Must manually cross-reference components against MAESTRO layers to find hotspots
- **Template**: maestro-heatmap (component x layer grid)

---

## User Stories

### US-01: View Layer Risk Distribution
**When**: I'm reviewing a threat model and want to understand architectural layer exposure,
**I want to**: see a vertical stack diagram showing finding counts and severities per MAESTRO layer,
**So I can**: quickly identify which layers of our AI stack carry the most risk and brief stakeholders.

**Acceptance Criteria**:
- **Given** a threats.md with MAESTRO-tagged findings, **when** `/infographic` runs with `maestro-stack` template, **then** a spec and image are generated showing L1-L7 layers with finding counts and highest severity per layer
- **Given** a threats.md without MAESTRO data, **when** `/infographic` runs with `maestro-stack` template, **then** the template renders a graceful empty state
- **Given** the generated image, **when** a CISO views it, **then** the most-exposed layer is visually prominent

**Priority**: P0
**Effort**: M

### US-02: View Component-Layer Heatmap
**When**: I'm performing detailed threat analysis and want to find component/layer hotspots,
**I want to**: see a grid where rows are components and columns are MAESTRO layers with severity coloring,
**So I can**: pinpoint exactly which component-layer intersections need remediation priority.

**Acceptance Criteria**:
- **Given** a threats.md with MAESTRO-tagged findings, **when** `/infographic` runs with `maestro-heatmap` template, **then** a spec and image are generated showing a component x L1-L7 grid with severity-colored cells
- **Given** a component with no findings at a layer, **when** the heatmap renders, **then** that cell is empty/neutral
- **Given** multiple findings at the same component-layer intersection, **when** the heatmap renders, **then** the cell shows the highest severity

**Priority**: P0
**Effort**: M

### US-03: Generate Both MAESTRO Templates Together
**When**: I want both MAESTRO visualizations without running two commands,
**I want to**: use `--infographic-template maestro` as a shorthand,
**So I can**: generate both maestro-stack and maestro-heatmap in a single invocation.

**Acceptance Criteria**:
- **Given** a valid threats.md, **when** user specifies `--infographic-template maestro`, **then** both maestro-stack and maestro-heatmap spec+image files are generated
- **Given** the `maestro` shorthand, **when** the infographic skill dispatches, **then** it expands to `["maestro-stack", "maestro-heatmap"]`

**Priority**: P1
**Effort**: S

### US-04: PDF Report MAESTRO Section
**When**: I'm generating a full PDF security assessment report,
**I want to**: see a dedicated MAESTRO Findings page that regroups threats by architectural layer,
**So I can**: include layer-level risk analysis in formal assessment deliverables.

**Acceptance Criteria**:
- **Given** `has-maestro-data` is true in report-data.typ, **when** the PDF compiles, **then** a MAESTRO Findings page appears after the existing infographic pages
- **Given** `has-maestro-data` is false, **when** the PDF compiles, **then** no MAESTRO page is rendered
- **Given** the MAESTRO page renders, **when** viewed, **then** findings are grouped by layer L1-L7 with layer name, description, and finding details

**Priority**: P0
**Effort**: M

### US-05: MAESTRO Data Extraction
**When**: the pipeline generates threat model output with MAESTRO layer data,
**I want to**: have MAESTRO layer distribution automatically extracted by the Python script,
**So I can**: feed accurate MAESTRO data to infographic templates and the PDF report.

**Acceptance Criteria**:
- **Given** a threats.md with `maestro_layer` in findings, **when** `extract-infographic-data.py` runs, **then** output includes `maestro_layer_distribution`, `maestro_layer_finding_counts`, and `most_exposed_layer`
- **Given** a threats.md without MAESTRO data, **when** extraction runs, **then** MAESTRO fields are empty/null without errors

**Priority**: P0
**Effort**: M

---

## Functional Requirements

### FR-01: Infographic Template -- maestro-stack
**Description**: Vertical layer stack diagram following existing template architecture.

**Layout**: Seven horizontal bands stacked vertically (L7 at top, L1 at bottom). Each band shows:
- Layer ID and name
- Finding count
- Highest severity (color-coded)
- Top finding summaries (up to 2)
- Sidebar: aggregate stats, most-exposed layer badge

**File**: `templates/tachi/infographics/infographic-maestro-stack.md`
**Spec output**: `threat-maestro-stack-spec.md`
**Image output**: `threat-maestro-stack.jpg`

### FR-02: Infographic Template -- maestro-heatmap
**Description**: Component x MAESTRO layer grid following existing template architecture.

**Layout**: Grid with:
- Rows: system components (from architecture input)
- Columns: L1 through L7
- Cells: highest severity finding at that intersection, color-coded
- Legend: severity color scale

**File**: `templates/tachi/infographics/infographic-maestro-heatmap.md`
**Spec output**: `threat-maestro-heatmap-spec.md`
**Image output**: `threat-maestro-heatmap.jpg`

### FR-03: Typst PDF Page -- maestro-findings.typ
**Description**: Full-page Typst template consistent with existing page template architecture.

**Content**: Findings regrouped by MAESTRO layer (L1-L7), each layer section showing:
- Layer name and CSA description
- Findings assigned to that layer with ID, severity, component, and threat summary
- Finding count per layer

**Conditional inclusion**: Gated by `has-maestro-data` boolean in report-data.typ.
**Placement**: After existing infographic pages, before "Detailed Findings" section divider.

### FR-04: report-data.typ Contract Extension
**New variables**:
- `has-maestro-data`: boolean -- true when findings contain `maestro_layer` data
- `maestro-layer-distribution`: array of (layer-id, layer-name, finding-count, highest-severity) tuples
- `most-exposed-layer`: string -- layer with highest finding count
- `maestro-findings-by-layer`: array of (layer-id, layer-name, findings-array) groups -- structured data for Typst page rendering, where each finding includes id, component, severity, and threat summary
- `has-maestro-stack-image`: boolean
- `maestro-stack-image-path`: string
- `has-maestro-heatmap-image`: boolean
- `maestro-heatmap-image-path`: string

**Backward compatibility**: `main.typ` Section 2b must include default values for all MAESTRO variables following the existing pattern (lines 62-87), defaulting booleans to `false` and arrays to empty `()`.

### FR-05: extract-infographic-data.py Extension

**Extraction sources** (addresses Section 7 column gap identified in Architect review):
- **Aggregate layer distribution**: Parse from Section 6 "Risk by MAESTRO Layer" summary table, which already contains `MAESTRO Layer | Finding Count | Highest Severity` columns. This maps directly to `maestro_layer_distribution`.
- **Per-finding layer mapping**: Build from Section 3 agent tables, which include a `MAESTRO Layer` column per finding row. Reuse the existing `deduplicate_findings()` iteration pattern that already handles Section 3's varying column structures (8 columns for STRIDE agents, 9 for AI agents).
- **Fallback**: When MAESTRO data is absent (pre-084 output), all MAESTRO fields default to empty/null without errors.

**Tier strategy**: MAESTRO extraction uses Tier 3 (threats.md) as the sole source. Tier 2 (risk-scores.md) and Tier 1 (compensating-controls.md) do not currently contain MAESTRO layer data. If a higher-tier source is present but lacks MAESTRO data, the extraction falls back to threats.md for MAESTRO fields only.

**CLI changes**: The `--template` argument parser `choices` list (line 933) must be extended with `"maestro-stack"` and `"maestro-heatmap"` values. The `maestro` shorthand expansion is handled at the skill dispatch level (FR-06), not in the CLI parser.

**New extraction logic**:
- Parse Section 6 for aggregate layer distribution
- Parse Section 3 for per-finding `maestro_layer` field (for heatmap component-layer intersection data)
- Compute most-exposed layer (highest finding count)
- Output MAESTRO-specific data for infographic spec generation and report-data.typ variables

### FR-06: Infographic Skill Dispatch
**Update**: `.claude/skills/tachi-infographics/` template dispatch to handle `maestro` shorthand.
- `maestro` expands to `["maestro-stack", "maestro-heatmap"]`
- Individual `maestro-stack` and `maestro-heatmap` values dispatch to respective templates

### FR-07: INFOGRAPHIC_TEMPLATES.md Update
**Update**: `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md` to include:
- New rows in Available Templates table
- New rows in Output Files table
- `maestro` shorthand in Using Templates section
- New MAESTRO-specific placeholders documented

---

## Non-Functional Requirements

### Backward Compatibility
- `has-maestro-data` flag guards all MAESTRO sections; graceful empty state when Feature 084 data is absent
- Existing templates (baseball-card, system-architecture, risk-funnel) are unchanged
- Existing Typst pages (findings-detail.typ, control-coverage.typ, etc.) are unchanged
- Existing report-data.typ variables are not modified

### Template Architecture Consistency
- New infographic templates follow identical structure to existing templates (Gemini Prompt Template, Color Palette, Layout, Gemini API Configuration)
- New Typst page follows identical pattern to existing pages (single export function, conditional inclusion in main.typ)
- New placeholders follow existing naming conventions

### Performance
- No impact on pipeline execution time (MAESTRO data already classified by Feature 084)
- Extraction script overhead: negligible (single pass over existing findings data)

---

## Scope & Boundaries

### In Scope (P0/P1)
- **P0**: maestro-stack infographic template
- **P0**: maestro-heatmap infographic template
- **P0**: maestro-findings.typ Typst page template
- **P0**: report-data.typ contract extension with MAESTRO variables
- **P0**: extract-infographic-data.py MAESTRO extraction logic
- **P1**: `maestro` shorthand for `--infographic-template` flag
- **P1**: INFOGRAPHIC_TEMPLATES.md documentation update
- **P1**: main.typ conditional MAESTRO page inclusion

### Out of Scope
- Agent detection logic changes (all 11 agents unchanged)
- Scoring formula changes (CVSS, exploitability, scalability, reachability unchanged)
- Dispatch rule changes (STRIDE-per-Element and AI keyword dispatch unchanged)
- Existing infographic template modifications
- MAESTRO layer reclassification or keyword changes (Feature 084 scope)
- Coverage matrix for MAESTRO (potential future feature)
- Interactive MAESTRO filtering in PDF output

### Assumptions
- Feature 084 is delivered and all example outputs include `maestro_layer` data
- Gemini API supports the visual complexity of a 7-layer stack and a component-layer grid
- Typst compilation supports the new page template without version upgrade

### Constraints
- **Template architecture**: Must follow existing patterns (no new template frameworks)
- **Data source**: All MAESTRO data comes from the finding IR `maestro_layer` field -- no new classification logic
- **Backward compatible**: `has-maestro-data` false must compile cleanly

---

## Risks & Dependencies

### Dependencies
**Internal -- Delivered**:
- **Feature 084** (MAESTRO Layer Mapping): `maestro_layer` field in finding IR, orchestrator classification, downstream propagation. **Status: Delivered 2026-04-08.**
- **Feature 071** (Deterministic Infographic Extraction): `extract-infographic-data.py` script. **Status: Delivered 2026-03-30.**
- **Feature 067** (Deterministic Report Data Extraction): Report data extraction pipeline. **Status: Delivered 2026-03-30.**
- **Feature 054** (Security Assessment PDF Booklet): Typst template system. **Status: Delivered 2026-03-28.**
- **Feature 039** (Standalone /infographic Command): Infographic skill dispatch. **Status: Delivered 2026-03-28.**

**External**:
- **Gemini API**: Image generation for new infographic templates (same dependency as existing templates)

### Technical Risks
**Risk 1**: Gemini image quality for 7-layer stack diagram
- **Likelihood**: Low (existing templates handle similar visual complexity)
- **Impact**: Medium (degraded visual quality)
- **Mitigation**: Use same Gemini prompt engineering patterns proven in baseball-card and system-architecture templates

**Risk 2**: Component-layer heatmap readability with many components
- **Likelihood**: Medium (some architectures have 10+ components)
- **Impact**: Low (heatmap truncates to most relevant components)
- **Mitigation**: Design prompt to prioritize top-N components by finding count; cap at max 10 components in spec

**Risk 3**: Section 3 column variation between STRIDE and AI agent tables
- **Likelihood**: Medium (STRIDE tables have 8 columns, AI tables have 9)
- **Impact**: Low (extraction fails gracefully with null MAESTRO data)
- **Mitigation**: Reuse existing `deduplicate_findings()` pattern that already handles column count variation; use Section 6 summary for aggregate data

---

## Open Questions

- [x] Should `maestro` shorthand be `all-maestro`, `maestro`, or `maestro-all`? -- **Resolved**: `maestro` (consistent with `all` shorthand pattern)
- [x] Where in the PDF page sequence should MAESTRO Findings appear? -- **Resolved**: After existing infographic pages, before "Detailed Findings" section divider

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- PRD 084 (MAESTRO Layer Mapping): [084-maestro-layer-mapping](docs/product/02_PRD/084-maestro-layer-mapping-2026-04-07.md)

### Technical Documentation
- Finding IR Schema: [finding.yaml](schemas/finding.yaml)
- MAESTRO Layers Reference: [maestro-layers-shared.md](.claude/skills/tachi-shared/references/maestro-layers-shared.md)
- Infographic Templates: [INFOGRAPHIC_TEMPLATES.md](templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md)
- Typst Template Contract: [typst-template-contract.md](.claude/skills/tachi-report-assembly/references/typst-template-contract.md)
- Main Typst Orchestrator: [main.typ](templates/tachi/security-report/main.typ)
- Extraction Script: [extract-infographic-data.py](scripts/extract-infographic-data.py)

### External Resources
- CSA MAESTRO Framework: Cloud Security Alliance -- Multi-Agent Environment Security Toolkit for Reasoning and Orchestration (February 2025)
- LinkedIn Evidence: Marco M. inquiry on MAESTRO for agentic AI threat modeling

---

## What Changes

| Area | Files | Change |
|------|-------|--------|
| Infographic templates | `templates/tachi/infographics/infographic-maestro-stack.md`, `infographic-maestro-heatmap.md` | 2 new template files |
| PDF report | `templates/tachi/security-report/maestro-findings.typ`, `main.typ` | 1 new page template + import/conditional inclusion |
| Extraction script | `scripts/extract-infographic-data.py` | MAESTRO extraction logic |
| Infographic skill | `.claude/skills/tachi-infographics/` | Template dispatch for `maestro` shorthand |
| Report assembly skill | `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` | New MAESTRO variables in contract |
| Infographic skill refs | `.claude/skills/tachi-infographics/references/template-specific-formats.md` | New MAESTRO template format sections |
| Documentation | `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md` | Index updates (also fix pre-existing risk-funnel gap) |

## What Does NOT Change

- Agent detection logic (all 11 agents unchanged)
- Scoring formulas (CVSS, exploitability, scalability, reachability unchanged)
- Dispatch rules (STRIDE-per-Element and AI keyword dispatch unchanged)
- Existing infographic templates (baseball-card, system-architecture, risk-funnel unchanged)
- Existing Typst page templates (findings-detail.typ, control-coverage.typ, etc. unchanged)
- Finding IR schema (no schema version bump -- consumes existing `maestro_layer` field)
