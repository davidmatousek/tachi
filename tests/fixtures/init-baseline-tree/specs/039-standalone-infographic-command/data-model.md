# Data Model: Standalone /infographic Command

## Entities

### Data Source (Input)

Two mutually exclusive input paths:

| Source Type | File | Content | Structural Data | Quantitative Scores |
|------------|------|---------|----------------|-------------------|
| threats.md | `threats.md` | Qualitative severity counts, components, trust zones, data flows | Yes (complete) | No |
| risk-scores.md | `risk-scores.md` + co-located `threats.md` | Quantitative composite scores + structural skeleton | Via co-located threats.md | Yes |

### Data Extraction Mapping

| Data Point | From threats.md | From risk-scores.md |
|-----------|-----------------|---------------------|
| Risk distribution | Section 6 severity counts (Critical/High/Medium/Low) | Section 1 composite score distribution bands |
| Component risk | Finding count per component (weighted: C=4, H=3, M=2, L=1) | Weighted composite score per component |
| Top findings | Highest severity findings (Critical first, then High) | Highest composite score findings |
| Architecture overlay | Component + severity mapping | Component + quantitative risk weight |
| Project metadata | Section 1 (System Overview) | **From co-located threats.md** Section 1 |
| Trust zones | Section 2 (Trust Boundaries) | **From co-located threats.md** Section 2 |
| Data flows | Section 2 (boundary crossings) | **From co-located threats.md** Section 2 |

### Template (Configuration)

| Template | Theme | Layout | Audience |
|----------|-------|--------|----------|
| baseball-card | Dark navy (#1E293B) | 4-zone 16:9 (donut, heat map, finding cards, architecture strip) | Executives |
| system-architecture | White (#FFFFFF) | Zone-stacked architecture, 16:9 (trust zones, components, data flows) | Engineers |
| corporate-white | Alias for baseball-card | — | — |

### Infographic Specification (Output)

YAML frontmatter + 6 required sections per `schemas/infographic.yaml`:

```yaml
# Frontmatter
schema_version: "1.0"
template: "{template-name}"
date: "YYYY-MM-DD"
source_file: "{path to primary input file}"
finding_count: {integer}
image_generated: {boolean}
```

| Section | Content |
|---------|---------|
| 1. Metadata | Project name, date, agent count, total findings, risk posture |
| 2. Risk Distribution | Severity counts + percentages + color codes |
| 3. Coverage Heat Map | Component x severity matrix (max 8 + "Other") |
| 4. Top Critical Findings | Max 5 entries: ID, component, threat, risk level |
| 5. Architecture Threat Overlay | Tabular (baseball-card) or spatial (system-architecture) |
| 6. Visual Design Directives | Color palette, layout, typography, background |

## State Transitions

No persistent state. The command is stateless and idempotent:
- Input: data source file(s) → Output: spec + optional image
- Re-running overwrites previous output in same directory
