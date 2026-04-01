---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Severity Bands and Composite Scoring Reference

Weighted composite formula, severity band thresholds, correlation group handling, governance field derivation rules, and computation sequence for the risk scoring pipeline.

---

## Weighted Composite Formula

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

Load weights from `schemas/risk-scoring.yaml` -> `weights` section:
- `cvss_base`: 0.35 -- Inherent vulnerability severity carries the most weight
- `exploitability`: 0.30 -- Practical attack feasibility is the second-strongest signal
- `scalability`: 0.15 -- Blast radius and automation potential
- `reachability`: 0.20 -- Architecture exposure and trust zone position

The composite score must be a value between 0.0 and 10.0, rounded to one decimal place.

---

## Reachability Scoring

Reachability scores are produced by the Section 6 pipeline (trust-zone-derived scoring):

1. **Zone baseline** (6a): Map the finding's component to a baseline score via `component_zone_map` trust levels (Untrusted 9.0, Semi-Trusted 5.5, Trusted 2.5)
2. **Per-finding refinement** (6b): Adjust the baseline using zone name keyword matching, clamped to the trust level's range
3. **Architecture adjustments** (6c): Reduce the score for authentication barriers (-1.5 each, max 3) and network segmentation boundaries (-1.0 each, max 3) parsed from `architecture.md`
4. **Final clamping** (6d): Clamp the adjusted score to [0.0, 10.0], rounded to one decimal place

**Fallback**: When `component_zone_map` is empty (Section 6e), default to 5.0 and emit: `"Reachability defaulted to 5.0 -- no trust zone data available for component '{component_name}'"`. Architecture adjustments still apply to the 5.0 default when `architecture.md` is present.

---

## Severity Band Mapping

Map the composite score to a severity band using ranges from `schemas/risk-scoring.yaml` -> `severity_bands`:

| Severity Band | Composite Score Range | Boundary Rule |
|---------------|-----------------------|---------------|
| Critical | 9.0 - 10.0 | Score >= 9.0 |
| High | 7.0 - 8.9 | Score >= 7.0 and < 9.0 |
| Medium | 4.0 - 6.9 | Score >= 4.0 and < 7.0 |
| Low | 0.0 - 3.9 | Score < 4.0 |

**Boundary precision**: When a composite score falls exactly on a boundary value, it maps to the **higher** band: 7.0 = High, 4.0 = Medium, 9.0 = Critical. The `min` values in the schema are inclusive.

**Note consolidation**: The existing `schemas/output.yaml` defines 5 bands (Critical/High/Medium/Low/Note). For composite scoring, Note is consolidated into Low (0.0-3.9) because composite scores always produce a meaningful numeric value -- there is no scenario where a scored finding should be classified as informational-only.

---

## OWASP 3x3 Risk Matrix

The OWASP risk rating methodology uses likelihood and impact to derive a qualitative risk level. This matrix is used during threat model generation (threats.md) and provides the initial risk_level that the quantitative scorer refines.

| | Low Impact | Medium Impact | High Impact |
|---|---|---|---|
| **High Likelihood** | Medium | High | Critical |
| **Medium Likelihood** | Low | Medium | High |
| **Low Likelihood** | Low | Low | Medium |

**Relationship to composite scoring**: The qualitative risk_level from threats.md is an input signal, not a binding constraint. The four-dimensional composite score may produce a different severity band than the OWASP matrix suggests. When they diverge, the composite score takes precedence — it incorporates more dimensions of analysis (exploitability, scalability, reachability) that the simple likelihood×impact matrix does not capture.

**Finding ID to OWASP mapping**: The initial risk_level field parsed from threats.md table rows uses this matrix. During scoring, the risk_level serves as a reasonableness check — if the composite score diverges by more than one severity band from the OWASP risk_level, the scorer should document the divergence rationale in the scoring notes.

---

## Correlation Group Handling

When Section 4a correlation groups exist in the parsed input:

1. **Identify primary finding**: The first finding ID listed in the correlation group is the primary
2. **Score the primary**: Apply full four-dimensional scoring (CVSS, exploitability, scalability, reachability) to the primary finding
3. **Peers inherit scores**: All correlated peer findings receive the same dimensional scores, composite score, severity band, and governance fields as the primary finding
4. **Rationale**: Correlated findings represent the same underlying issue from different perspectives. Independent scoring would create inconsistencies; inheritance ensures the group is treated as a coherent risk unit
5. **SC-001 exemption**: Correlated peer groups are excluded from the score differentiation metric (SC-001). Peers intentionally receive identical scores; this is correct behavior, not a differentiation failure

---

## Computation Sequence

For each finding (after parsing, in order):

1. Look up the finding's `category` to get the default CVSS vector
2. Refine the CVSS vector per-threat (Section 3) -> produces `cvss_base` and `cvss_vector`
3. Assess exploitability (Section 4) -> produces `exploitability`
4. Assess scalability (Section 5) -> produces `scalability`
5. Determine reachability via Section 6 pipeline (zone baseline -> per-finding refinement -> architecture adjustments -> clamping; falls back to 5.0 per Section 6e when no trust zone data is available) -> produces `reachability`
6. Calculate composite: `(0.35 x cvss_base) + (0.30 x exploitability) + (0.15 x scalability) + (0.20 x reachability)`
7. Map composite to severity band
8. If the finding is a correlation group primary: store scores for peer inheritance
9. If the finding is a correlation group peer: copy all scores from the primary instead of computing

### Output per Finding

After composite calculation, each finding has these scoring fields ready for output:

| Field | Type | Source |
|-------|------|--------|
| `cvss_base` | number (0.0-10.0) | Section 3 |
| `cvss_vector` | string | Section 3 |
| `exploitability` | number (0.0-10.0) | Section 4 |
| `scalability` | number (0.0-10.0) | Section 5 |
| `reachability` | number (0.0-10.0) | Section 6 or default 5.0 |
| `composite_score` | number (0.0-10.0) | This section (weighted formula) |
| `severity_band` | Critical/High/Medium/Low | This section (band mapping) |

---

## Governance Fields

Attach remediation tracking metadata to each scored finding based on its severity band. Governance fields provide organizational accountability -- who owns the risk, when it must be addressed, and what the initial disposition is. These fields are derived deterministically from the severity band assigned in Section 7, using the mappings defined in `schemas/risk-scoring.yaml` -> `severity_bands`.

### Field Generation Rules

For each scored finding, generate four governance fields by looking up the finding's `severity_band` in the severity bands table:

| Field | Type | Generation Rule |
|-------|------|-----------------|
| `risk_owner` | string | Default: `"Unassigned"`. This is a placeholder indicating the finding has not yet been triaged by a human reviewer. The scorer never assigns a specific owner -- ownership is a human decision made during remediation planning. |
| `remediation_sla` | string | Mapped from the `sla` property of the finding's severity band in `schemas/risk-scoring.yaml` -> `severity_bands`. Represents the maximum time allowed to address the finding after scoring. |
| `risk_disposition` | string | Mapped from the `disposition` property of the finding's severity band in `schemas/risk-scoring.yaml` -> `severity_bands`. Represents the initial recommended action for the finding. |
| `review_date` | string (YYYY-MM-DD) | Calculated as: scoring date + SLA duration. The scoring date is the date the risk scorer executes, not the date the threat model was generated. |

### Severity-to-Governance Mapping

Load these mappings from `schemas/risk-scoring.yaml` -> `severity_bands`:

| Severity Band | `remediation_sla` | `risk_disposition` | `review_date` Calculation |
|---------------|--------------------|---------------------|---------------------------|
| Critical | `24h` | `Mitigate` | scoring date + 1 day |
| High | `7d` | `Mitigate` | scoring date + 7 days |
| Medium | `30d` | `Review` | scoring date + 30 days |
| Low | `90d` | `Review` | scoring date + 90 days |

**SLA duration parsing**: Convert the `sla` string to a day count for review date calculation:
- `"24h"` -> 1 day
- `"7d"` -> 7 days
- `"30d"` -> 30 days
- `"90d"` -> 90 days

### Review Date Calculation

The `review_date` is the calendar date by which the finding must be reviewed or remediated:

```
review_date = scoring_date + sla_days
```

Where:
- `scoring_date` is the current date when the risk scorer runs (format: YYYY-MM-DD)
- `sla_days` is the day count derived from the severity band's `sla` property

**Example**: If the scorer runs on 2026-03-27 and a finding has severity band `High` (SLA = 7d):
- `review_date` = 2026-03-27 + 7 days = `2026-04-03`

**Month/year boundary handling**: Standard calendar arithmetic applies. If adding days crosses a month or year boundary, use the correct calendar date (e.g., 2026-01-29 + 30 days = 2026-02-28).

### Disposition Values

The `risk_disposition` field uses one of four values defined in `schemas/risk-scoring.yaml` -> `scored_finding.risk_disposition.enum`:

| Disposition | Meaning | Assigned By |
|-------------|---------|-------------|
| `Mitigate` | Active remediation required within the SLA period | Severity mapping (Critical, High) |
| `Review` | Finding requires evaluation to determine appropriate action | Severity mapping (Medium, Low) |
| `Accept` | Risk accepted with documented justification | Human override only |
| `Transfer` | Risk transferred to a third party (insurance, vendor responsibility) | Human override only |

The scorer assigns only `Mitigate` or `Review` based on severity mapping. `Accept` and `Transfer` are valid disposition values that humans may set during remediation planning, but the scorer never generates them automatically.

### Override Guidance

All governance fields are defaults intended to be refined during human triage. The scorer produces deterministic initial values; organizations customize them post-scoring:

- **`risk_owner`**: Replace `"Unassigned"` with the responsible team or individual during triage. Ownership assignment depends on organizational structure and is outside the scorer's scope.
- **`remediation_sla`**: Organizations may tighten SLAs (e.g., Critical from 24h to 12h for regulated systems) or relax them with documented justification. Custom SLAs should still use duration notation (e.g., `"12h"`, `"14d"`).
- **`risk_disposition`**: Change from the severity-mapped default when appropriate. For example, a Low-severity finding with `"Review"` may be changed to `"Accept"` if the risk is within tolerance, or a Medium finding may be escalated to `"Mitigate"` based on business context.
- **`review_date`**: Recalculate if the SLA is overridden. The review date should always reflect the actual SLA in effect, not the original severity-mapped default.

Overridden values must be preserved in both output formats (risk-scores.md and risk-scores.sarif). The scorer records the severity-mapped defaults; downstream tooling or manual edits apply overrides.

### Correlation Group Governance

Governance fields for correlation groups follow the same inheritance rule as scoring fields (Section 7):

1. The **primary finding** receives governance fields derived from its severity band
2. All **correlated peer findings** inherit the primary's governance fields identically
3. If a human overrides governance fields on the primary, peers should reflect the same override

This ensures a correlation group -- which represents a single underlying risk from multiple perspectives -- receives consistent remediation tracking.

### Governance Output per Finding

After governance field generation, each finding has these additional fields ready for output:

| Field | Type | Example Value |
|-------|------|---------------|
| `risk_owner` | string | `"Unassigned"` |
| `remediation_sla` | string | `"7d"` |
| `risk_disposition` | string | `"Mitigate"` |
| `review_date` | string (YYYY-MM-DD) | `"2026-04-03"` |

Combined with the scoring fields from Section 7, each finding now carries the complete set of fields needed for output generation (Sections 9 and 10).
