---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Severity Bands and Composite Scoring Reference

Weighted composite formula, severity band thresholds, correlation group handling, governance field derivation rules, and computation sequence for the risk scoring pipeline.

The shipped renderer (`scripts/render-risk-scores.py`, over `scripts/tachi_scoring.py` and `scripts/tachi_scoring_rules.py`) computes everything here. The risk-scorer agent writes only the judgment fields that feed it: the CVSS vector, the eight sub-scores and the reachability inputs. ADR-050 D2, D5 and D9 are the authority where this reference and the code differ.

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

The composite score must be a value between 0.0 and 10.0, rounded to one decimal place. The renderer takes the four stored one-decimal values, multiplies them by the weights in exact decimal arithmetic, and rounds the sum half up to one decimal (`tachi_scoring.q1`), so a composite of 4.55 is 4.6. It never uses Python's `round()` or a float.

---

## Reachability Scoring

The renderer produces reachability scores with the Section 6 pipeline (trust-zone-derived scoring), from the zone, trust level, authentication barrier count and network boundary count the agent wrote:

1. **Zone baseline** (6a): Map the finding's component to a baseline score via its trust level (Untrusted 9.0, Semi-Trusted 5.5, Trusted 2.5)
2. **Per-finding refinement** (6b): Adjust the baseline using zone name keyword matching, clamped to the trust level's range
3. **Architecture adjustments** (6c): Reduce the score for the agent's authentication barrier count (-1.5 each, max 3) and network segmentation boundary count (-1.0 each, max 3)
4. **Final clamping** (6d): Clamp the adjusted score to [0.0, 10.0], rounded to one decimal place

**Fallback**: When a component has no zone data (Section 6e), the renderer defaults to 5.0 and emits: `"Reachability defaulted to 5.0 -- no trust zone data available for component '{component_name}'"`. The agent's barrier and boundary counts still apply to the 5.0 default.

---

## Severity Band Mapping

Map the composite score to a severity band using ranges from `schemas/risk-scoring.yaml` -> `severity_bands`:

| Severity Band | Composite Score Range | Boundary Rule |
|---------------|-----------------------|---------------|
| Critical | 9.0 - 10.0 | Score >= 9.0 |
| High | 7.0 - 8.9 | Score >= 7.0 and < 9.0 |
| Medium | 4.0 - 6.9 | Score >= 4.0 and < 7.0 |
| Low | 0.0 - 3.9 | Score < 4.0 |

**Boundary precision**: When a composite score falls exactly on a boundary value, it maps to the **higher** band: 7.0 = High, 4.0 = Medium, 9.0 = Critical. The `min` values in the schema are inclusive. The renderer's `band()` takes only a value already rounded to one decimal, and refuses any other, so a composite is always rounded before it is banded.

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

**Finding ID to OWASP mapping**: The initial risk_level field parsed from threats.md table rows uses this matrix. During scoring, the risk_level serves as a reasonableness check on the agent's own assessment — if the composite score diverges by more than one severity band from the OWASP risk_level, the agent may say so in its rationale, citing the band only through the `{{band:severity}}` slot. The renderer doesn't compare the two.

---

## Correlation Group Handling

Groups come from Section 4a of the source `threats.md`, read through `tachi_parsers.parse_correlation_groups`. Groups keep Section 4a's order, the first member left after filtering to the open findings is the primary, a group of fewer than two members is dropped, and an ID listed in two groups stays in the first (ADR-050 D8).

1. **Identify primary finding**: The first finding ID listed in the correlation group is the primary
2. **Score the primary**: The agent assesses the primary with the full four-dimensional model, as it does any finding that needs judgment
3. **NEW and UPDATED peers inherit**: A NEW or UPDATED peer takes its primary's vector, `score_bounds`, dimensional scores and derived fields. An UPDATED peer keeps its own owner
4. **An UNCHANGED peer keeps its own score**: When its composite differs from its primary's, the renderer flags it `divergent:composite_score:primary=<ID>` and leaves the score alone
5. **A regroup changes no carried value**: A new primary, or a finding that moves to another group, never changes a carried score, band or SLA by itself
6. **Rationale**: Correlated findings represent the same underlying issue from different perspectives. One score for the group, set by its primary, keeps a NEW group a coherent risk unit, and the divergence flag keeps an old group's differences visible
7. **SC-001 exemption**: Correlated peer groups are excluded from the score differentiation metric (SC-001). Peers that inherit intentionally receive identical scores; this is correct behavior, not a differentiation failure

---

## Computation Sequence

The renderer takes each finding through these steps, in order (ADR-050 D2, D9, D10):

1. **Route** the finding. A NEW or UPDATED non-peer, or a finding with no usable baseline row, has its judgment fields from the agent's part. An UNCHANGED finding with a baseline row inherits its inputs from that row (the assessed vector, the sub-scores, the reachability inputs, the tags used and the scored-on date). A NEW or UPDATED peer copies its primary
2. Look up the finding's category from its ID prefix (`tachi_scoring.category_for_prefix`) to get the default CVSS vector and its bound
3. Compute the CVSS base score from the assessed vector (Section 3), clamp it to the category bound for a NEW finding in a baseline-aware run, then apply the asset-sensitivity pass (Section 3.5) -> produces `cvss_base`
4. Compute exploitability as the mean of the four sub-scores (Section 4), rounded half up -> produces `exploitability`
5. Compute scalability as the mean of the four sub-scores (Section 5), rounded half up -> produces `scalability`
6. Compute reachability from the zone, trust level and counts via the Section 6 pipeline (zone baseline -> keyword refinement -> architecture adjustments -> zone clamp; it falls back to 5.0 per Section 6e when a component has no zone data) -> produces `reachability`
7. Calculate composite: `(0.35 x cvss_base) + (0.30 x exploitability) + (0.15 x scalability) + (0.20 x reachability)`, rounded half up
8. Map composite to severity band
9. Compare each recomputed value of an inherited finding with the value the baseline stored. A rounding-only difference is normalized and counted. Any other difference is flagged, with its cause (Section 6 of `risk-scores.md`)
10. Derive the governance fields from the band (below)

### Output per Finding

After composite calculation, each finding has these scoring fields ready for output:

| Field | Type | Source |
|-------|------|--------|
| `cvss_base` | number (0.0-10.0) | Section 3 |
| `cvss_vector` | string | The agent's assessment (Section 3) |
| `exploitability` | number (0.0-10.0) | Section 4 |
| `scalability` | number (0.0-10.0) | Section 5 |
| `reachability` | number (0.0-10.0) | Section 6 or default 5.0 |
| `composite_score` | number (0.0-10.0) | This section (weighted formula) |
| `severity_band` | Critical/High/Medium/Low | This section (band mapping) |

---

## Governance Fields

The renderer attaches remediation tracking metadata to each scored finding based on its severity band. Governance fields provide organizational accountability -- who owns the risk, when it must be addressed, and what the initial disposition is. These fields are derived deterministically from the severity band assigned in Section 7, using the mappings defined in `schemas/risk-scoring.yaml` -> `severity_bands`. A human's choices are the exception, and they are carried forward (see Carry-Forward below).

### Field Generation Rules

For each scored finding, generate four governance fields by looking up the finding's `severity_band` in the severity bands table:

| Field | Type | Generation Rule |
|-------|------|-----------------|
| `risk_owner` | string | Default: `"Unassigned"`. This is a placeholder indicating the finding has not yet been triaged by a human reviewer. The renderer never assigns a specific owner -- ownership is a human decision made during remediation planning, and a baseline's owner is always carried forward, never flagged. |
| `remediation_sla` | string | Mapped from the `sla` property of the finding's severity band in `schemas/risk-scoring.yaml` -> `severity_bands`. Represents the maximum time allowed to address the finding after scoring. |
| `risk_disposition` | string | Mapped from the `disposition` property of the finding's severity band in `schemas/risk-scoring.yaml` -> `severity_bands`. Represents the initial recommended action for the finding. |
| `review_date` | string (YYYY-MM-DD) | Calculated as: scoring date + SLA duration. The scoring date is the `--date` the command passed to the planner, which the plan keeps, never the clock and not the date the threat model was generated. |

### Severity-to-Governance Mapping

Load these mappings from `schemas/risk-scoring.yaml` -> `severity_bands`:

| Severity Band | `remediation_sla` | `risk_disposition` | `review_date` Calculation |
|---------------|--------------------|---------------------|---------------------------|
| Critical | `24h` | `Mitigate` | scoring date + 1 day |
| High | `7d` | `Mitigate` | scoring date + 7 days |
| Medium | `30d` | `Review` | scoring date + 30 days |
| Low | `90d` | `Review` | scoring date + 90 days |

**SLA duration parsing**: Convert the `sla` string to a day count for review date calculation (`<n>h` is the next whole day up from n/24, `<n>d` is n, and any other form is unparseable):
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
- `scoring_date` is the date the command passed to the planner (format: YYYY-MM-DD)
- `sla_days` is the day count derived from the severity band's `sla` property

**Example**: If the run's scoring date is 2026-03-27 and a finding has severity band `High` (SLA = 7d):
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

The renderer assigns only `Mitigate` or `Review` based on severity mapping. `Accept` and `Transfer` are valid disposition values that humans may set during remediation planning, but the renderer never generates them. It carries them forward from the baseline as they are, and flags them `override`.

### Override Guidance

All governance fields are defaults intended to be refined during human triage. The scorer produces deterministic initial values; organizations customize them post-scoring:

- **`risk_owner`**: Replace `"Unassigned"` with the responsible team or individual during triage. Ownership assignment depends on organizational structure and is outside the scorer's scope.
- **`remediation_sla`**: Organizations may tighten SLAs (e.g., Critical from 24h to 12h for regulated systems) or relax them with documented justification. Custom SLAs should still use duration notation (e.g., `"12h"`, `"14d"`).
- **`risk_disposition`**: Change from the severity-mapped default when appropriate. For example, a Low-severity finding with `"Review"` may be changed to `"Accept"` if the risk is within tolerance, or a Medium finding may be escalated to `"Mitigate"` based on business context.
- **`review_date`**: Recalculate if the SLA is overridden. The review date should always reflect the actual SLA in effect, not the original severity-mapped default.

Overridden values must be preserved in both output formats (risk-scores.md and risk-scores.sarif). The renderer records the severity-mapped defaults, and carries an override forward verbatim when it finds one in the baseline. An Accept or Transfer disposition, and an SLA or disposition that differs from the **stored** band's default, count as overrides, are flagged `override:<field>:human`, and keep their review date.

### Correlation Group Governance

Governance fields for correlation groups follow the same rule as scoring fields (Correlation Group Handling above):

1. The **primary finding** receives governance fields derived from its severity band
2. **NEW and UPDATED peers** inherit the primary's derived governance fields, and an UPDATED peer keeps its own owner
3. An **UNCHANGED peer** keeps its own governance fields, which follow its own band
4. If a human overrides governance fields on the primary, a NEW or UPDATED peer reflects the same override

This ensures a correlation group -- which represents a single underlying risk from multiple perspectives -- receives consistent remediation tracking.

### Carry-Forward by Delta Status

A baseline's human-assigned governance data survives across runs. The renderer recalculates only what follows from a band that changed (ADR-050 D9, R-5 and R-31):

| Delta Status | Owner | SLA and disposition | Review date |
|--------------|-------|---------------------|-------------|
| `UNCHANGED` | Carried verbatim | Follow the recomputed band, except an override, which is carried verbatim | Kept while the band holds or the SLA is an override. A corrected band gives the original scoring date plus the new SLA |
| `UPDATED` | Carried verbatim, never overwritten | As for `UNCHANGED`. A band change restarts the clock | This run's scoring date plus the new SLA, when the band changed |
| `NEW` | `Unassigned` | Assigned fresh from the band | This run's scoring date plus the SLA |
| `RESOLVED` | Carried verbatim | Carried verbatim | Carried verbatim, outside the SLA clock (R-30) |

**The original scoring date** of a carried finding is the scored-on date its baseline stored, or the stored review date minus the stored SLA for a legacy baseline. Where either value is missing or unparseable, the renderer takes the baseline file's frontmatter `date` (flagged `corrected:review_date:baseline-date`). Without that, it keeps the stored review date (flagged `unchecked:review_date:scoring-date-unknown`), and without that, it uses this run's date plus the SLA (flagged `corrected:review_date:clock-restarted`). No step is silent.

**A band change that the asset tags alone explain** is not a correction, and is flagged `retagged`. When the band goes up, the review date becomes this run's scoring date plus the new SLA, unless the stored review date is earlier, in which case it is kept: tagging never makes a finding overdue on the day, and a higher band never gets more time. When the band goes down, the original scoring date is kept, so removing a tag never clears a deadline that was already missed under the lower band's SLA. An SLA override still keeps its review date. A legacy row records no tags, so there a band change that comes only from the elevation this run's tags apply follows the same rule.

### Governance Output per Finding

After governance field generation, each finding has these additional fields ready for output:

| Field | Type | Example Value |
|-------|------|---------------|
| `risk_owner` | string | `"Unassigned"` |
| `remediation_sla` | string | `"7d"` |
| `risk_disposition` | string | `"Mitigate"` |
| `review_date` | string (YYYY-MM-DD) | `"2026-04-03"` |

Combined with the scoring fields from Section 7, each finding now carries the complete set of fields the renderer needs to write its output files (Sections 9 and 10).
