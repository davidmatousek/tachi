# Data Model: Compensating Controls Analysis

**Schema file**: `schemas/compensating-controls.yaml`
**Extends**: `schemas/risk-scoring.yaml` → `schemas/finding.yaml`

## Entity Hierarchy

```
finding.yaml (base)
  └── risk-scoring.yaml (scored_finding)
        └── compensating-controls.yaml (controlled_finding)
```

## Controlled Finding Schema

Extends `scored_finding` (all fields from finding.yaml + risk-scoring.yaml) with:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `control_status` | enum | found, partial, missing | Detection classification |
| `control_evidence` | list[object] | `[{file, line, snippet}]` | Evidence for detected controls |
| `control_category` | enum | authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control | Which of the 8 categories matched |
| `control_effectiveness` | enum | strong, moderate, weak, none | P1: effectiveness rating (P0: derived from status) |
| `reduction_factor` | number | 0.00 - 1.00 | Risk reduction multiplier |
| `residual_score` | number | 0.0 - 10.0 | `composite_score * (1 - reduction_factor)` |
| `residual_severity_band` | enum | Critical, High, Medium, Low | Mapped from residual_score |
| `recommendation` | string | — | Remediation guidance (null if control_status = found) |
| `effort_estimate` | enum | Low, Medium, High | Implementation effort (null if control_status = found) |

## Control Evidence Object

| Field | Type | Description |
|-------|------|-------------|
| `file` | string | Relative file path from target root |
| `line` | number | Line number where control is detected |
| `snippet` | string | Code snippet demonstrating the control (max 5 lines) |

## Reduction Factor Mapping

### P0 (Binary)

| control_status | reduction_factor |
|---------------|-----------------|
| found | 0.50 |
| partial | 0.25 |
| missing | 0.00 |

### P1 (Effectiveness-aware)

| control_status | control_effectiveness | reduction_factor |
|---------------|----------------------|-----------------|
| found | strong | 0.80 |
| found | moderate | 0.50 |
| found | weak | 0.20 |
| partial | strong | 0.50 |
| partial | moderate | 0.30 |
| partial | weak | 0.10 |
| missing | none | 0.00 |

## STRIDE-to-Control Category Mapping

| STRIDE Category | Primary Control Categories |
|----------------|--------------------------|
| spoofing | authentication, access-control |
| tampering | input-validation |
| repudiation | logging-audit |
| info-disclosure | encryption |
| denial-of-service | rate-limiting |
| privilege-escalation | access-control |
| agentic | all 8 (P0); ai-specific (P1) |
| llm | input-validation, logging-audit (P0); ai-specific (P1) |

## Validation Rules

1. `control_status` is required for every controlled_finding
2. `control_evidence` must have >= 1 entry when `control_status` is "found" or "partial"
3. `control_evidence` must be empty when `control_status` is "missing"
4. `recommendation` must be non-null when `control_status` is "partial" or "missing"
5. `effort_estimate` must be non-null when `recommendation` is non-null
6. `residual_score` = `composite_score * (1 - reduction_factor)`, clamped to [0.0, 10.0]
7. `residual_severity_band` follows same thresholds as `severity_band`
8. When multiple controls address the same threat, use the control with highest `reduction_factor`
