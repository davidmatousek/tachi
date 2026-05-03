---
type: shared-reference
name: severity-bands-shared
version: 1.0.0
source_schema: schemas/risk-scoring.yaml
consumers:
  - orchestrator
  - risk-scorer
  - control-analyzer
  - threat-report
  - threat-infographic
  - report-assembler
---

# Severity Bands — Shared Reference

Canonical severity band definitions used across the tachi pipeline. This is the single source of truth for severity thresholds, color codes, SLA mappings, and governance field derivation. All consuming agents should Read this file rather than maintaining inline definitions.

---

## Severity Band Thresholds

Map composite scores to severity bands using these boundaries. Boundary values are inclusive to the higher band (e.g., 9.0 maps to Critical, 7.0 maps to High).

| Severity Band | Composite Score Range | Boundary Rule | Color Code |
|---------------|-----------------------|---------------|------------|
| Critical | 9.0 -- 10.0 | Score >= 9.0 | Red (#DC2626) |
| High | 7.0 -- 8.9 | Score >= 7.0 and < 9.0 | Orange (#EA580C) |
| Medium | 4.0 -- 6.9 | Score >= 4.0 and < 7.0 | Yellow (#CA8A04) |
| Low | 0.0 -- 3.9 | Score < 4.0 | Blue (#2563EB) |

**Boundary precision**: When a composite score falls exactly on a boundary value, it maps to the higher band: 7.0 = High, 4.0 = Medium, 9.0 = Critical. The `min` values in `schemas/risk-scoring.yaml` are inclusive.

**Note consolidation**: The qualitative output (`schemas/output.yaml`) defines 5 bands (Critical/High/Medium/Low/Note). For quantitative composite scoring, Note is consolidated into Low (0.0--3.9) because composite scores always produce a meaningful numeric value -- there is no scenario where a scored finding should be classified as informational-only.

---

## SLA Mappings

Each severity band maps to a remediation SLA, default disposition, and review date offset. These drive governance field generation for scored findings.

| Severity Band | Remediation SLA | Disposition | Review Date Offset | SLA Days |
|---------------|-----------------|-------------|--------------------|---------:|
| Critical | 24h | Mitigate | +1 day | 1 |
| High | 7d | Mitigate | +7 days | 7 |
| Medium | 30d | Review | +30 days | 30 |
| Low | 90d | Review | +90 days | 90 |

**SLA duration parsing**: Convert the `sla` string to a day count for review date calculation:
- `"24h"` -> 1 day
- `"7d"` -> 7 days
- `"30d"` -> 30 days
- `"90d"` -> 90 days

**Review date formula**: `review_date = scoring_date + sla_days`, where `scoring_date` is the current date when the pipeline runs (format: YYYY-MM-DD). Standard calendar arithmetic applies for month/year boundaries.

---

## Disposition Values

The `risk_disposition` field uses one of four values. The scorer assigns only `Mitigate` or `Review` based on severity mapping. `Accept` and `Transfer` are valid values that humans may set during remediation planning.

| Disposition | Meaning | Assigned By |
|-------------|---------|-------------|
| Mitigate | Active remediation required within the SLA period | Severity mapping (Critical, High) |
| Review | Finding requires evaluation to determine appropriate action | Severity mapping (Medium, Low) |
| Accept | Risk accepted with documented justification | Human override only |
| Transfer | Risk transferred to a third party (insurance, vendor responsibility) | Human override only |

---

## OWASP 3×3 Risk Matrix

The qualitative risk matrix used during threat model generation (`threats.md`) to derive the initial `risk_level` from likelihood and impact. This matrix is the input signal that the quantitative scorer refines.

| | Low Impact | Medium Impact | High Impact |
|---|---|---|---|
| **High Likelihood** | Medium | High | Critical |
| **Medium Likelihood** | Low | Medium | High |
| **Low Likelihood** | Note | Low | Medium |

**Relationship to composite scoring**: The qualitative `risk_level` from `threats.md` is an input signal, not a binding constraint. The four-dimensional composite score may produce a different severity band. When they diverge, the composite score takes precedence -- it incorporates exploitability, scalability, and reachability dimensions that the simple likelihood x impact matrix does not capture.

---

## Color Codes for Visual Output

Color values used by infographic and report agents for severity-based visual formatting.

| Severity Band | Hex | Usage |
|---------------|-----|-------|
| Critical | #DC2626 | Backgrounds, badges, donut chart segments, table row highlights |
| High | #EA580C | Backgrounds, badges, donut chart segments, table row highlights |
| Medium | #CA8A04 | Backgrounds, badges, donut chart segments, table row highlights |
| Low | #2563EB | Backgrounds, badges, donut chart segments, table row highlights |
| Note | #6B7280 | Informational items in qualitative output only |

---

## SARIF Level Mapping

Severity bands map to SARIF `level` values for machine-readable output.

| Severity Band | SARIF Level |
|---------------|-------------|
| Critical | error |
| High | error |
| Medium | warning |
| Low | note |
| Note | note |
