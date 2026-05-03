# Data Model: Baseline-Aware Pipeline

## Schema Extensions

### Finding IR Extension (`schemas/finding.yaml`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `delta_status` | string enum | Yes (when baseline present) | `NEW`, `UNCHANGED`, `UPDATED`, `RESOLVED` |
| `baseline_run_id` | string, nullable | No | Run ID of the baseline that first discovered this finding. Null for first run |

**Validation Rules**:
- `delta_status` is required when a baseline is provided; defaults to `NEW` when no baseline
- `baseline_run_id` is set when a finding is carried forward from a previous run
- `delta_status` must be one of the 4 recognized values

### Scored Finding Extension (`schemas/risk-scoring.yaml`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `score_source` | string enum | Yes | `inherited` (carried from baseline) or `fresh` (scored this run) |
| `score_bounds` | object, nullable | No | `{min: number, max: number}` — bounds for new finding scores per category |

**Validation Rules**:
- `score_source` is `inherited` for `UNCHANGED` findings, `fresh` for `NEW` and `UPDATED`
- When `score_source` is `inherited`, all scoring fields (cvss_base, exploitability, scalability, reachability, composite_score) are copied verbatim from baseline
- When `score_source` is `fresh` and `delta_status` is `NEW`, cvss_base must fall within `score_bounds` (±1.0 of category default)

### Controlled Finding Extension (`schemas/compensating-controls.yaml`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `control_carry_forward` | boolean | Yes | True if control status was inherited from baseline |
| `rescan_scope` | string enum | Yes | `full` (first run or all findings changed) or `incremental` (only new/updated findings re-scanned) |

**Validation Rules**:
- `control_carry_forward` is true for `UNCHANGED` findings, false for `NEW`, `UPDATED`, `RESOLVED`
- When `control_carry_forward` is true, control_status, control_evidence, reduction_factor, and residual_score are copied from baseline

### Coverage Checklists Schema (`schemas/coverage-checklists.yaml`) — NEW

| Field | Type | Description |
|-------|------|-------------|
| `component_type` | string | DFD element type or AI subtype |
| `required_categories` | list[string] | Minimum threat categories that must be evaluated |

**Component Type Mappings**:

| Component Type | Required Threat Categories |
|---------------|--------------------------|
| External Entity | spoofing, repudiation |
| Process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation |
| Data Store | tampering, info-disclosure, denial-of-service |
| Data Flow | tampering, info-disclosure, denial-of-service |
| LLM Process | All Process categories + llm (prompt injection, data poisoning, model theft) |
| MCP Server | All Process categories + agentic (tool abuse, agent autonomy) |

## Baseline Frontmatter Schema

Added to output file YAML frontmatter:

```yaml
baseline:
  source: "threats.md"          # or null for first run
  date: "2026-03-25"            # ISO date of baseline run
  finding_count: 39             # baseline finding count
  run_id: "2026-03-25T12-53-57" # unique run identifier
coverage_gate:
  status: "pass"                # pass or warn
  gaps: []                      # list of {component, missing_category} if any
```

## SARIF Fingerprint Extensions

Added to `partialFingerprints` object per result:

| Field | Type | Description |
|-------|------|-------------|
| `findingId/v1` | string | Stable finding ID (e.g., "S-3") — PRIMARY correlation key |
| `primaryLocationLineHash` | string | SHA-256(ruleId\|component_name) truncated to 16 hex — SECONDARY signal |
| `baselineRunId` | string, nullable | Run ID of the originating baseline run |

Added to result `properties`:

| Field | Type | Description |
|-------|------|-------------|
| `baselineState` | string enum | `new`, `unchanged`, `updated`, `absent` (SARIF convention for resolved) |

## Entity Relationships

```
Finding (base)
  ├── delta_status: NEW | UNCHANGED | UPDATED | RESOLVED
  ├── baseline_run_id → Baseline.run_id
  │
  └── ScoredFinding (extends Finding)
        ├── score_source: inherited | fresh
        ├── score_bounds: {min, max}
        │
        └── ControlledFinding (extends ScoredFinding)
              ├── control_carry_forward: boolean
              └── rescan_scope: full | incremental

Baseline (metadata)
  ├── source: filename
  ├── date: ISO date
  ├── finding_count: integer
  └── run_id: unique identifier

CoverageChecklist (configuration)
  ├── component_type → DFD element type
  └── required_categories[] → threat category enum
```
