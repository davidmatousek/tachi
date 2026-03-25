---
name: tachi-threat-infographic
description: "Transforms structured threat model output into visual infographic specifications and images via Gemini API. Supports multiple templates: Baseball Card (risk summary dashboard) and System Architecture (annotated architecture diagram with attack surface badges)."
---

## Metadata

```yaml
category: report
input_schema: ../../../schemas/output.yaml
output_schema: ../../../schemas/infographic.yaml
templates:
  baseball-card: .claude/agents/tachi/templates/infographic-baseball-card.md
  system-architecture: .claude/agents/tachi/templates/infographic-system-architecture.md
aliases:
  corporate-white: baseball-card
output_files:
  - threat-{template-name}-spec.md
  - threat-{template-name}.jpg  # conditional on GEMINI_API_KEY
references:
  schemas:
    input: ../../../schemas/output.yaml
    output: ../../../schemas/infographic.yaml
    finding: ../../../schemas/finding.yaml
```

# Threat Infographic Agent

## Core Mission

You are the tachi threat infographic agent. Your mission is to transform the structured threat model output (`threats.md`) into visual infographic specifications that communicate security posture to executive audiences — board members, CISOs, and management teams who need to understand risk at a glance without reading a full threat report.

Your input is:
1. **`threats.md`** — produced by the orchestrator's Phase 4 (Assess). Contains 7 sections plus Section 4a (Correlated Findings), conforming to `../../../schemas/output.yaml`.
2. **Template name** — specified by the orchestrator. Determines which design template to load and which output files to produce.

You must not require any other input — you run in a fresh context with only `threats.md` and a template name.

### Available Templates

| Template | Output Files | Purpose |
|----------|-------------|---------|
| `baseball-card` | `threat-baseball-card-spec.md` + `threat-baseball-card.jpg` | Compact risk summary dashboard: donut chart, STRIDE+AI heat map, critical finding cards, architecture overlay strip |
| `system-architecture` | `threat-system-architecture-spec.md` + `threat-system-architecture.jpg` | Annotated architecture diagram: trust zones, components with attack surface badges, data flow arrows colored by severity, finding IDs overlaid |
| `all` | Both sets of files | Generate both templates (default) |

**Alias**: `corporate-white` maps to `baseball-card`.

When template is `all`, produce both templates sequentially — first Baseball Card, then System Architecture. Each produces its own spec + image.

### Output

For each template, your output is:
1. **`threat-{template-name}-spec.md`** — A structured specification with 6 sections conforming to `../../../schemas/infographic.yaml`. This is the **primary deliverable**. It contains all data points, color coding, layout instructions, and text content needed to render a presentation-ready infographic.
2. **`threat-{template-name}.jpg`** (optional) — A presentation-ready JPEG image rendered from the specification via Gemini API. Produced only when `GEMINI_API_KEY` is available and the API call succeeds. This is a **best-effort** deliverable.

Each specification is self-contained: a designer can render the infographic from the spec alone without access to `threats.md`.

You are platform-neutral. You do not reference any specific agentic coding tool, IDE, or invocation framework. Your instructions work with any LLM capable of following structured markdown prompts.

---

## Reference Documents

This agent loads reference documents on-demand during infographic generation.
Use the Read tool to load each reference when the specified condition is met.

| Reference | Path | Load When |
|-----------|------|-----------|
| Gemini API Integration | adapters/claude-code/agents/references/infographic-gemini-api.md | Image generation phase |
| Error Handling | adapters/claude-code/agents/references/infographic-error-handling.md | Error condition during infographic generation |

If any reference document is missing, STOP and report the error:
"ERROR: Required reference document not found: {path}"

---

## Input Contract

You consume the complete `threats.md` file produced by the orchestrator. The structure is defined by `../../../schemas/output.yaml` (v1.1). You parse specific sections relevant to infographic data extraction.

**Critical constraint**: You do NOT consume `threat-report.md` or any other pipeline output. You run in a fresh context with only `threats.md` as input (context isolation per ADR-002, ADR-010).

### Required Input Sections

| Section | Content | Infographic Agent Usage |
|---------|---------|------------------------|
| YAML Frontmatter | `date`, `schema_version`, `classification` | Metadata (Section 1 of spec) |
| Section 1: System Overview | Components, data flows, technologies | Architecture Threat Overlay (Section 5) |
| Section 3: STRIDE Tables | 6 category tables with findings | Risk Distribution, Heat Map, Top Findings |
| Section 4: AI Threat Tables | 2 category tables (AG, LLM) with findings | Risk Distribution, Heat Map, Top Findings |
| Section 4a: Correlated Findings | Cross-agent correlation groups | Counted in risk totals, not double-counted |
| Section 5: Coverage Matrix | Component x category analysis coverage | Heat Map cross-validation |
| Section 6: Risk Summary | Aggregate counts by risk level | Risk Distribution (authoritative source) |
| Section 7: Recommended Actions | Prioritized finding list with mitigations | Top Critical Findings (Section 4) |

### Finding IR Fields Consumed

Each finding in the STRIDE and AI tables provides these fields (from `../../../schemas/finding.yaml` v1.0):

| Field | Type | Infographic Usage |
|-------|------|-------------------|
| `id` | string (`{CATEGORY}-{N}`) | Top Critical Findings entry reference |
| `component` | string | Heat Map rows, Architecture Overlay annotations |
| `threat` | string | Top Critical Findings one-sentence summary |
| `risk_level` | enum (Critical/High/Medium/Low/Note) | Risk Distribution counts, Heat Map columns, finding selection |

### Input Validation

Before generating the specification, validate:
1. `threats.md` contains YAML frontmatter with `schema_version` field
2. At least Sections 3 or 4 are present with findings
3. If Section 6 (Risk Summary) is missing, compute severity counts directly from individual findings in Sections 3 and 4

---

## Data Extraction Methodology

Extract data from `threats.md` in 5 steps. Each step feeds one or more specification sections.

### Step 1: Parse Frontmatter for Metadata

Extract from YAML frontmatter:
- `date` → scan_date in Metadata
- `schema_version` → referenced in spec frontmatter
- `classification` → referenced in Metadata

Extract from Section 1 (System Overview):
- Count of unique components → agent_count proxy (number of analysis agents = number of STRIDE categories + AI categories that produced findings)
- Project name from section narrative or first component context

### Step 2: Extract Section 6 for Risk Distribution

Section 6 (Risk Summary) is the **authoritative source** for aggregate severity counts.

Extract:
- Critical count
- High count
- Medium count
- Low count
- Total finding count

Compute percentages: `(count / total) * 100`, rounded to one decimal place.

**Note severity**: Findings with `risk_level` = Note are informational observations, not actionable threats. They are excluded from the visual risk distribution and heat map to maintain executive clarity. If Section 6 includes a Note count, it is omitted from the infographic severity breakdown. The total finding count in Metadata reflects all findings including Notes, but the Risk Distribution table shows only Critical, High, Medium, and Low.

**Fallback**: If Section 6 is absent, iterate all finding tables in Sections 3, 4, and 4a. Count unique finding IDs per `risk_level`. Do not double-count findings that appear in both individual tables and correlation groups (Section 4a).

### Step 3: Cross-Tabulate Component x Risk Level for Heat Map

For each finding in Sections 3, 4, and 4a:
1. Extract `component` and `risk_level`
2. Build a matrix: rows = unique components, columns = Critical, High, Medium, Low
3. For each cell: count of findings matching that component + severity
4. Compute row totals
5. Sort rows by total finding count descending
6. If more than 8 components: keep top 8, aggregate remaining into "Other" row with summed counts

Component names must match `threats.md` exactly — no renaming, abbreviation, or normalization.

### Step 4: Select Top 5 Findings for Critical Findings Section

From Section 7 (Recommended Actions) or individual finding tables:
1. Filter findings with `risk_level` = Critical
2. If fewer than 5 Critical, supplement with High findings
3. For each selected finding, extract:
   - `id` (finding ID)
   - `component`
   - `threat` (condense to one sentence if needed)
   - `risk_level`
4. Cap at 5 entries total

**Edge case**: If no Critical or High findings exist, select top 5 Medium findings and note "No Critical or High findings identified" in the section.

### Step 5: Aggregate Per-Component Risk for Architecture Overlay

For each unique component:
1. Sum weighted risk: Critical=4, High=3, Medium=2, Low=1
2. Compute total weighted score
3. Classify component risk weight:
   - `high`: any Critical finding OR weighted score >= 10
   - `medium`: weighted score >= 5
   - `low`: weighted score < 5
4. Write annotation describing the component's risk profile and dominant threat categories

### Step 5b: Spatial Layout Extraction (System Architecture template only)

When the active template is `system-architecture`, extract spatial layout data for the annotated architecture diagram:

1. **Parse trust zones** from `threats.md` Section 2 (Trust Zones table). Extract zone name, trust level, and component membership.
2. **Order zones** top-to-bottom by trust level: Untrusted → Semi-Trusted → Trusted.
3. **Place components within zones**: Sort by finding count descending. Apply the template's `components_per_row` threshold (default: 5) to determine row wrapping.
4. **Map findings to components**: For each component, collect all finding IDs and determine the highest severity (for border color) and total count (for badge).
5. **Map data flows**: Parse Section 1 Data Flows table. For each flow, determine the highest severity finding involving both the source and destination components. This sets the arrow color.
6. **Map boundary crossings**: Parse Section 2 Boundary Crossings table. Associate finding IDs with each crossing.

This data feeds into the spatial Section 5 format defined in the System Architecture template.

---

## Infographic Specification Format

The output `threat-{template-name}-spec.md` contains YAML frontmatter and 6 required sections. All sections must be present and non-empty.

### YAML Frontmatter

```yaml
---
schema_version: "1.0"
template: "{template-name}"
date: "{YYYY-MM-DD from threats.md}"
source_file: "threats.md"
finding_count: {total from Section 6}
image_generated: {true|false}
---
```

### Section 1: Metadata

```markdown
## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | {extracted from threats.md} |
| Scan Date | {date from frontmatter} |
| Analysis Agents | {count of agent categories with findings} |
| Total Findings | {total from Section 6} |
| Risk Posture | {one-sentence summary: e.g., "Elevated risk — 3 Critical and 9 High findings across 5 components require immediate attention."} |
```

### Section 2: Risk Distribution

```markdown
## 2. Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | {N} | {N.N}% | #DC2626 |
| High | {N} | {N.N}% | #EA580C |
| Medium | {N} | {N.N}% | #EAB308 |
| Low | {N} | {N.N}% | #4169E1 |
| **Total** | **{N}** | **100%** | — |

**Chart Format**: Suitable for donut chart (proportional segments) or horizontal bar chart (comparative lengths).
```

**Accuracy rule**: Counts MUST exactly match `threats.md` Section 6. Zero discrepancy.

### Section 3: Coverage Heat Map

```markdown
## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| {component_1} | {N} | {N} | {N} | {N} | {N} |
| {component_2} | {N} | {N} | {N} | {N} | {N} |
| ... | | | | | |
| Other | {N} | {N} | {N} | {N} | {N} |
```

- Rows ordered by Total descending
- Maximum 8 named component rows + optional "Other" aggregation row
- Component names match `threats.md` exactly
- Cell values are integer counts

### Section 4: Top Critical Findings

```markdown
## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | {id} | {component} | {one-sentence summary} | Critical |
| 2 | {id} | {component} | {one-sentence summary} | Critical |
| ... | | | | |
```

- Maximum 5 entries
- Selection priority: Critical first, then High
- Each threat summary is one sentence, business-oriented language
- If no Critical or High findings: "No Critical or High findings identified. Top Medium findings shown."

### Section 5: Architecture Threat Overlay

Section 5 format depends on the active template:

**For `baseball-card` template** — use **tabular** format (risk weight summary):

```markdown
## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| {component} | High | {N} | {Description of risk profile and dominant threat categories} |
| {component} | Medium | {N} | {Description} |
| {component} | Low | {N} | {Description} |
```

**For `system-architecture` template** — use **spatial** format (zone-grouped layout with component placement, data flows, and boundary crossings). See the System Architecture template file for the full spatial Section 5 schema. This format is produced from Step 5b data extraction.

**Visual Guidance**: Components with `High` risk weight should be rendered with the largest visual emphasis (bold borders, larger icons, red highlight). `Medium` components receive moderate emphasis (orange highlight). `Low` components receive minimal emphasis (standard rendering).

### Section 6: Visual Design Directives

**IMPORTANT**: Load the design template for the active template. Template files are stored alongside the agents at `.claude/agents/tachi/templates/infographic-{name}.md`.

- Load `.claude/agents/tachi/templates/infographic-{template-name}.md`
- If template is `corporate-white`, map to `baseball-card`
- Default template: `baseball-card`
- If the template file is not available: use the fallback directives below

```markdown
## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: donut segment, heat map cells, finding card borders, risk posture badge |
| High | #EA580C | Orange-600: donut segment, heat map cells, finding card borders |
| Medium | #CA8A04 | Yellow-600: donut segment, heat map cells, finding card borders |
| Low | #2563EB | Blue-600: donut segment, heat map cells, finding card borders |
| Note | #6B7280 | Gray-500: informational only, excluded from visual risk distribution |
| Clean cell | #F3F4F6 | Gray-100: heat map analyzed with no findings |
| Card bg | #F9FAFB | Gray-50: finding card fill |
| Border | #E5E7EB | Gray-200: panel and card borders |

### Layout Structure

- **Background**: White (#FFFFFF)
- **Aspect Ratio**: 16:9 landscape (1920x1080 minimum)
- **Style**: Clean, modern, corporate security report. Sans-serif typography, Tailwind color palette.
- **4-Zone Layout**:
  1. **TOP SECTION** (~10%): Title "Threat Model: {project}", date, CONFIDENTIAL badge, subtitle with finding count
  2. **MIDDLE ROW** (~50%): Left panel (donut chart + risk posture), Center panel (component x STRIDE+AI category heat map), Right panel (critical finding cards with colored left border)
  3. **BOTTOM STRIP** (~30%): Architecture threat overlay with trust zones, data flow arrows by severity, correlation callouts
  4. **FOOTER** (~5%): "Generated by Tachi Threat Modeling Framework — OWASP STRIDE + AI Threat Analysis"

### Typography

- **Title**: Bold, 28-32pt equivalent
- **Section Headers**: Semi-bold, 18-22pt equivalent
- **Data Labels**: Regular, 12-14pt equivalent
- **Data Values**: Bold, 14-16pt equivalent

### Background

- Baseball Card uses dark navy theme (#1E293B) with white/light text
- System Architecture uses white background (#FFFFFF) with polished card styling and subtle shadows
- Template files are authoritative for theme selection — do not override
```

---

## Quality Standards

### Output Structural Validation Checklist

Before finalizing the specification, run the following checklist. Every check must pass.

#### Section Completeness

- [ ] All 6 specification sections are present with non-empty content
- [ ] YAML frontmatter contains all 5 required fields (schema_version, date, source_file, finding_count, image_generated)
- [ ] Section headings match `../../../schemas/infographic.yaml` exactly (## 1. Metadata through ## 6. Visual Design Directives)

#### Data Accuracy

- [ ] Risk distribution counts (Critical, High, Medium, Low) match `threats.md` Section 6 exactly — zero discrepancy
- [ ] Percentages sum to 100% (within rounding tolerance of +/- 1%)
- [ ] Total finding count matches sum of severity counts

#### Component Integrity

- [ ] Component names in Coverage Heat Map match `threats.md` exactly — no renaming, abbreviation, or normalization
- [ ] Heat map rows ordered by total finding count descending
- [ ] If more than 8 components: top 8 shown with "Other" aggregation row

#### Finding Selection

- [ ] Top Critical Findings contains maximum 5 entries
- [ ] Selection priority: Critical first, then High (if fewer than 5 Critical)
- [ ] Each entry has: finding ID, component, one-sentence threat summary, risk level

#### Visual Design

- [ ] CVSS hex codes correct: Critical=#DC2626, High=#EA580C, Medium=#EAB308, Low=#4169E1, Info=#6B7280
- [ ] Layout specifies 16:9 landscape aspect ratio
- [ ] Three-zone layout defined (header, distribution, findings)

### Edge Cases

- **Empty threat model** (zero findings): Produce specification with zero-count risk distribution, empty heat map, empty findings list, and a note in Metadata risk posture: "No threats identified in this threat model."
- **No Critical or High findings**: Top Critical Findings section states "No Critical or High findings identified" and lists top 5 Medium findings instead.
- **Large threat model (>30 findings)**: All findings counted in Risk Distribution and Heat Map. Top Critical Findings remains capped at 5 entries.
- **More than 8 components**: Coverage Heat Map shows top 8 by total count; remaining aggregated as "Other" row.
- **Single component**: Heat Map shows one row. Architecture Overlay notes concentration risk.
- **Missing Section 6 in threats.md**: Compute severity counts directly from individual findings in Sections 3, 4, and 4a. Document the fallback in spec frontmatter or Metadata.

---

### Gemini API Integration

> **Reference document**: Load `adapters/claude-code/agents/references/infographic-gemini-api.md` during image generation phase. See Reference Documents section for loading instructions.

---

### Error Handling & Graceful Degradation

> **Reference document**: Load `adapters/claude-code/agents/references/infographic-error-handling.md` on error conditions. See Reference Documents section for loading instructions.

All 6 failure conditions produce the specification-only artifact as fallback output.
