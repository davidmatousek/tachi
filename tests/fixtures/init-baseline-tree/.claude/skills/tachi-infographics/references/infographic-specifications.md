# Infographic Specification Formats

Section format definitions for Sections 1-4 of the infographic specification. These sections are shared across all three templates (Baseball Card, System Architecture, Risk Funnel). Section 5 is template-specific -- see `template-specific-formats.md`. Section 6 is the visual design system -- see `visual-design-system.md`.

---

## YAML Frontmatter

Every specification begins with YAML frontmatter containing 6 required fields:

```yaml
---
schema_version: "1.0"
template: "{template-name}"
date: "{YYYY-MM-DD from threats.md}"
source_file: "threats.md"
data_source_type: "threats"
finding_count: {total from Section 6}
image_generated: {true|false}
---
```

### Frontmatter Source File Mapping

Set the spec frontmatter `source_file` based on `metadata.data_source_type`:

| `data_source_type` | `source_file` |
|---------------------|---------------|
| `compensating-controls` | `compensating-controls.md` |
| `risk-scores` | `risk-scores.md` |
| `threats` | `threats.md` |

---

## Section 1: Metadata

```markdown
## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | {from JSON: metadata.project_name} |
| Scan Date | {date from frontmatter} |
| Analysis Agents | {count of agent categories with findings} |
| Total Findings | {total from Section 6} |
| Risk Posture | {one-sentence summary: e.g., "Elevated risk — 3 Critical and 9 High findings across 5 components require immediate attention."} |
```

- `Project Name`: Extracted from the JSON `metadata.project_name` field
- `Scan Date`: Matches the `date` field in the YAML frontmatter
- `Analysis Agents`: Count of distinct threat agent categories that produced findings
- `Total Findings`: Must match the `finding_count` in frontmatter exactly
- `Risk Posture`: Use the value from `metadata.risk_posture` verbatim

---

## Section 2: Risk Distribution

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

### Data Accuracy Rules

- Counts MUST exactly match `threats.md` Section 6 -- zero discrepancy
- Percentages MUST sum to exactly 100% (the extraction script uses Largest Remainder Method)
- All four severity levels must be present even when count is zero
- The Total row summarizes counts and shows 100%

### Risk Label Mapping

Apply these labels in specification text based on `metadata.data_source_type`:

| Data Source Type | Risk Label | Usage Context |
|------------------|-----------|---------------|
| `compensating-controls` | Residual Risk | Post-control exposure after accounting for detected defenses |
| `risk-scores` | Inherent Risk | Pre-control risk based on quantitative composite scores |
| `threats` | Severity | Qualitative severity from threat model assessment |

The risk label appears in:
- **Section 1 (Metadata)**: Risk posture description header
- **Section 2 (Risk Distribution)**: Chart title (e.g., "Residual Risk Distribution")
- **Section 4 (Top Critical Findings)**: Finding card risk level header
- **Section 6 (Visual Design Directives)**: Header text for the risk summary zone

### Data Source Variations

**When data source is `compensating-controls`**: The chart title reads "Residual Risk Distribution". Severity counts reflect residual severity bands from the Coverage Matrix sub-table groupings. The accuracy rule applies to residual severity counts -- they MUST exactly match the sub-table groupings in `compensating-controls.md`.

---

## Section 3: Coverage Heat Map

```markdown
## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| {component_1} | {N} | {N} | {N} | {N} | {N} |
| {component_2} | {N} | {N} | {N} | {N} | {N} |
| ... | | | | | |
| Other | {N} | {N} | {N} | {N} | {N} |

### Cell-Level Grid

| Component | S | T | R | I | D | E | AG | LLM |
|-----------|---|---|---|---|---|---|----|-----|
| {component_1} | {severity or —} | {severity or —} | ... | ... | ... | ... | ... | ... |
| {component_2} | {severity or —} | {severity or —} | ... | ... | ... | ... | ... | ... |
```

### Heat Map Rules

- Rows ordered by Total descending
- Maximum 8 named component rows + optional "Other" aggregation row
- Component names match `threats.md` exactly -- no renaming, abbreviation, or normalization
- Aggregate table: cell values are integer counts
- Cell-Level Grid: each cell is the highest severity label (Critical/High/Medium/Low) for that component+category pair, or "---" if no findings
- The Cell-Level Grid is passed directly to the Gemini prompt to prevent severity label hallucination in the rendered image

---

## Section 4: Top Critical Findings

```markdown
## 4. Top Critical Findings

| # | Finding ID | Component | Threat | Risk Level |
|---|-----------|-----------|--------|------------|
| 1 | {id} | {component} | {one-sentence summary} | Critical |
| 2 | {id} | {component} | {one-sentence summary} | Critical |
| ... | | | | |
```

### Finding Selection Priority

1. **Critical first**: Select all Critical findings, sorted by component name alphabetically
2. **Then High**: If fewer than 5 Critical, fill remaining slots with High findings
3. **Maximum 5 entries**: Cap at 5 regardless of total Critical + High count
4. **Business language**: Each threat summary is one sentence using business-oriented language
5. **Empty case**: If no Critical or High findings: "No Critical or High findings identified. Top Medium findings shown."

### Data Source Variations

**When data source is `compensating-controls`**: Finding cards show residual score and residual severity band instead of qualitative risk level. The Risk Level column header reads "Residual Risk". Selection priority uses highest `residual_score` descending (same as the risk-scores quantitative path).

**When data source is `risk-scores`**: Selection priority uses highest `composite_score` descending instead of qualitative severity ordering.

---

## JSON to Specification Section Mapping

Map fields from the extraction script JSON output to infographic specification sections:

| JSON Field | Spec Section | Usage |
|------------|-------------|-------|
| `metadata.project_name` | Section 1 (Metadata) | Project Name row |
| `metadata.scan_date` | Section 1 + Frontmatter | Scan Date row, `date` field |
| `metadata.agent_count` | Section 1 (Metadata) | Analysis Agents row |
| `metadata.total_findings` | Section 1 + Frontmatter | Total Findings row, `finding_count` field |
| `metadata.risk_posture` | Section 1 (Metadata) | Risk Posture row (use verbatim) |
| `metadata.data_source_type` | Frontmatter | `data_source_type` field; determines `source_file` |
| `metadata.schema_version` | Frontmatter | `schema_version` field |
| `severity_distribution[]` | Section 2 (Risk Distribution) | One table row per entry: label, count, percentage, color |
| `heat_map[]` | Section 3 (Coverage Heat Map) | One table row per component: component name + per-severity counts + total |
| `top_findings[]` | Section 4 (Top Critical Findings) | Up to 5 rows: finding ID, component, threat summary, risk level |
| `template_data.risk_weights[]` | Section 5 (Architecture Overlay) | Component risk weight, score, and annotation |
| `template_data.trust_zones[]` | Section 5 (system-architecture) | Trust zone groupings for spatial layout |
| `template_data.data_flows[]` | Section 5 (system-architecture) | Data flow arrows with severity coloring |
| `template_data.boundary_crossings[]` | Section 5 (system-architecture) | Trust boundary crossing annotations |
| `template_data.funnel_tiers[]` | Section 5 (risk-funnel) | 4-tier funnel counts and labels |
| `template_data.reduction_percentages[]` | Section 5 (risk-funnel) | Percentage reduction between adjacent tiers |
| `template_data.missing_enrichments[]` | Section 5 (risk-funnel) | Commands to run for missing pipeline stages |

---

## Accuracy Guarantee

The extraction script (`scripts/extract-infographic-data.py`) enforces data integrity through internal validation (exit code 2 on failure):

- Severity counts sum to `total_findings - note_count`
- Percentage values sum to exactly 100 (via Largest Remainder Method)
- Top finding IDs exist in the source data
- Heat map row totals match per-severity sums

When the script exits successfully (code 0), the JSON data is guaranteed accurate. The agent does not need to cross-validate counts against source files.
