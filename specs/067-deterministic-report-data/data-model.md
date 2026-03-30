# Data Model: Deterministic Report Data Extraction

## Entities

### ReportData (output: report-data.typ)

The central entity representing all extracted data as Typst `#let` variable bindings.

**Metadata Fields**:
- `project-name`: string — extracted from `# Threat Model: {name}` or `--title` override
- `assessment-date`: string (YYYY-MM-DD) — from threats.md frontmatter `date`
- `classification`: string or none — from threats.md frontmatter `classification`

**Severity Counts**:
- `critical-count`: integer — count of Critical severity findings
- `high-count`: integer — count of High severity findings
- `medium-count`: integer — count of Medium severity findings
- `low-count`: integer — count of Low severity findings
- `note-count`: integer — count of Note severity findings (excluded from 4-level sum)
- `total-findings`: integer — total individual findings (raw count if deduplicated)

**Page Inclusion Flags**:
- `has-threat-report`: boolean — threat-report.md exists and is non-empty
- `has-risk-scores`: boolean — risk-scores.md exists and is non-empty
- `has-compensating-controls`: boolean — compensating-controls.md exists and is non-empty
- `has-funnel-image`: boolean — threat-risk-funnel.jpg exists and is non-zero
- `has-baseball-image`: boolean — threat-baseball-card.jpg exists and is non-zero
- `has-architecture-image`: boolean — threat-system-architecture.jpg exists and is non-zero

**Data Source**:
- `data-source-tier`: integer (1, 2, or 3)

**Image Paths** (relative from templates/tachi/security-report/):
- `funnel-image-path`: string or ""
- `baseball-image-path`: string or ""
- `architecture-image-path`: string or ""

**Brand Assets**:
- `has-logo-primary`: boolean
- `has-logo-horizontal`: boolean
- `logo-primary-path`: string or none
- `logo-primary-dark-path`: string or none
- `logo-horizontal-path`: string or none

**Content**:
- `executive-narrative`: string or none — from threat-report.md Section 1 (max 2000 chars)
- `component-distribution`: array of (name, count) tuples or none
- `findings`: array of tier-specific finding dicts
- `coverage-matrix`: array of (category, found, partial, missing) dicts or empty
- `controls`: array of (component, category, status, evidence, effectiveness) dicts or empty
- `coverage-summary`: dict with total-found, total-partial, total-missing
- `remediation-actions`: array of remediation dicts or none

**Scope Data**:
- `scope-components`: array of (name, type, description) dicts
- `scope-data-flows`: array of (source, destination, data, protocol) dicts
- `scope-trust-boundaries`: array of (zone, trust-level, components) dicts
- `scope-boundary-crossings`: array of (crossing, from-zone, to-zone, components, controls) dicts
- `scope-component-count`: integer
- `scope-data-flow-count`: integer
- `scope-trust-boundary-count`: integer

**Page Visibility**:
- `show-disclaimer`: boolean (default true)
- `show-methodology`: boolean (default true)

### Finding (tier-variant)

**Tier 1** (from compensating-controls.md):
- id, component, threat, residual_score, residual_severity, control_status, recommendation

**Tier 2** (from risk-scores.md):
- id, component, threat, composite_score, severity, cvss, exploitability

**Tier 3** (from threats.md Section 7):
- id, component, threat, likelihood ("—"), impact ("—"), risk_level, mitigation

### ScopeComponent
- name: string
- type: string (External Entity, Process, Data Store)
- description: string

### ScopeDataFlow
- source: string
- destination: string
- data: string
- protocol: string

### TrustBoundary
- zone: string
- trust-level: string
- components: string

### BoundaryCrossing
- crossing: string
- from-zone: string
- to-zone: string
- components: string
- controls: string

### CoverageEntry
- category: string (STRIDE category name)
- found: integer
- partial: integer
- missing: integer

### ControlEntry
- component: string
- category: string
- status: string (Found, Partial, Missing)
- evidence: string
- effectiveness: string (Strong, Moderate, Weak, None)

### RemediationAction
- severity: string
- finding-id: string
- finding-name: string
- recommendation: string
- sla: string
- status: string

## Validation Rules

1. `critical-count + high-count + medium-count + low-count == total-findings - note-count`
2. `len(scope-components) == scope-component-count`
3. `len(scope-data-flows) == scope-data-flow-count`
4. `len(scope-trust-boundaries) == scope-trust-boundary-count`
5. All finding IDs in findings array are unique
6. All string values in Typst output are properly escaped (`"` → `\"`, `\` → `\\`)

## Tier Selection Logic

```
if compensating-controls.md exists and non-empty:
    tier = 1
    severity_source = count residual_severity from Section 2 findings
elif risk-scores.md exists and non-empty:
    tier = 2
    severity_source = risk-scores.md Section 1 distribution table
else:
    tier = 3
    severity_source = threats.md Section 6 Risk Summary table
```
