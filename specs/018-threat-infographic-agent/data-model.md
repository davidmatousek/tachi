# Data Model: Threat Infographic Agent

## Input Schema: `threats.md` (read-only)

The infographic agent consumes `threats.md` as defined by `schemas/output.yaml` (v1.1). No modifications to this schema are needed.

**Key sections consumed**:

| Section | Data Extracted | Used In |
|---------|---------------|---------|
| YAML Frontmatter | `date`, `schema_version`, `classification` | Metadata |
| Section 1: Architecture | Component names, trust boundaries | Architecture Threat Overlay |
| Section 3: STRIDE Findings | Per-finding `component`, `risk_level` | Risk Distribution, Heat Map |
| Section 4: AI Findings | Per-finding `component`, `risk_level` | Risk Distribution, Heat Map |
| Section 4a: Correlated Findings | Correlation groups | Counted in totals |
| Section 5: Coverage Matrix | Component × category counts | Heat Map cross-validation |
| Section 6: Risk Summary | Aggregate severity counts | Risk Distribution (authoritative source) |
| Section 7: Recommended Actions | Top findings by severity | Top Critical Findings |

## Output Schema: `threat-infographic-spec.md`

Defined by `schemas/infographic.yaml` (v1.0). New schema created for this feature.

### Section Structure

```
threat-infographic-spec.md
├── YAML Frontmatter
│   ├── schema_version: "1.0"
│   ├── date: "YYYY-MM-DD"
│   ├── source_file: "threats.md"
│   ├── finding_count: N
│   └── image_generated: true|false
├── ## 1. Metadata
│   ├── project_name: string
│   ├── scan_date: date
│   ├── agent_count: integer
│   ├── finding_count: integer
│   └── risk_posture: string (one sentence)
├── ## 2. Risk Distribution
│   ├── severity_counts: {Critical: N, High: N, Medium: N, Low: N}
│   ├── percentages: {Critical: N%, High: N%, Medium: N%, Low: N%}
│   └── total: integer
├── ## 3. Coverage Heat Map
│   ├── rows[]: (max 8 + optional "Other")
│   │   ├── component: string (exact match to threats.md)
│   │   ├── critical: integer
│   │   ├── high: integer
│   │   ├── medium: integer
│   │   ├── low: integer
│   │   └── total: integer
│   └── ordering: by total descending
├── ## 4. Top Critical Findings
│   ├── entries[]: (max 5)
│   │   ├── finding_id: string (e.g., "AG-1")
│   │   ├── component: string
│   │   ├── threat_summary: string (one sentence)
│   │   └── risk_level: Critical|High
│   └── selection: Critical first, then High
├── ## 5. Architecture Threat Overlay
│   ├── component_annotations[]:
│   │   ├── component: string
│   │   ├── risk_weight: high|medium|low
│   │   └── annotation: string
│   └── visual_guidance: string
└── ## 6. Visual Design Directives
    ├── color_palette: {Critical: "#DC2626", High: "#F97316", Medium: "#EAB308", Low: "#4169E1", Info: "#6B7280"}
    ├── layout: three-zone (header, distribution, findings)
    ├── aspect_ratio: "16:9"
    ├── orientation: landscape
    ├── font_hierarchy: title > section > label > data
    └── background: dark navy (#1E293B) or white (#FFFFFF)
```

## Data Accuracy Constraints

| Constraint | Enforcement |
|-----------|-------------|
| Risk distribution counts = threats.md Section 6 | Agent validates before writing spec |
| Component names match threats.md exactly | Verbatim extraction, no renaming |
| Severity colors match CVSS hex codes | Hardcoded in schema, validated in checklist |
| Heat map row ordering | Sorted by total finding count descending |
| Top findings selection | Critical first, then High, max 5 |
