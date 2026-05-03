# Data Model: Security Assessment PDF Booklet

## Entities

### Artifact

Represents a file produced by a tachi pipeline command that can serve as input to the PDF assembler.

| Field | Description |
|-------|-------------|
| file_pattern | Expected filename (e.g., `threats.md`, `threat-risk-funnel.jpg`) |
| file_type | `markdown` or `image` |
| required | Whether the artifact must be present (`threats.md` is the only required artifact) |
| detected | Whether the artifact was found in the target directory |
| enables | List of page types this artifact enables |
| data_tier | For markdown artifacts used by Findings Detail: tier 1, 2, or 3 (null for non-tiered) |

### Page

Represents a page (or page group) in the output PDF.

| Field | Description |
|-------|-------------|
| type | Page type identifier (cover, executive-summary, risk-funnel, baseball-card, system-architecture, findings-detail, control-coverage, remediation-roadmap) |
| sequence | Position in page ordering (1-8) |
| layout | `portrait` or `landscape` |
| page_size | `us-letter` (8.5" x 11") or `custom-16x9` (11" x 6.1875") |
| source_artifact | Which artifact provides data for this page |
| included | Whether this page is included in the current generation (based on artifact availability) |

### ExtractedData

Represents structured data parsed from markdown artifacts for Typst template injection.

| Field | Description |
|-------|-------------|
| project_name | From `threats.md` frontmatter or `--title` override |
| assessment_date | From `threats.md` frontmatter `date` field |
| classification | From `threats.md` frontmatter `classification` field (may be null) |
| schema_version | From `threats.md` frontmatter `schema_version` field |
| severity_counts | Critical, High, Medium, Low counts from Risk Summary |
| total_findings | Total finding count |
| findings_rows | Array of finding row objects (columns vary by tier) |
| executive_narrative | From `threat-report.md` Section 1 or `threats.md` risk summary |
| control_coverage_rows | From `compensating-controls.md` Section 2 (may be empty) |
| remediation_rows | From `compensating-controls.md` Section 3 or `threat-report.md` (may be empty) |
| infographic_paths | Map of image type to file path (may be empty) |
| data_source_tier | Which tier is active for Findings Detail (1, 2, or 3) |

### DataSourceTier

Represents the column configuration for the Findings Detail page based on available data.

| Tier | Source | Columns | Risk Label |
|------|--------|---------|------------|
| 1 | `compensating-controls.md` | ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation | Residual Risk |
| 2 | `risk-scores.md` | ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability | Inherent Risk |
| 3 | `threats.md` | ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation | Severity |

## Relationships

```
Artifact (7 types) --enables--> Page (8 types)
Page --uses--> ExtractedData
Findings Detail Page --selects--> DataSourceTier (1 of 3)
```

## State Transitions

No persistent state. All data is parsed at generation time from existing files and discarded after PDF compilation.
