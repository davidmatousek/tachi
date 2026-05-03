# Data Model: Risk Reduction Funnel

## Entities

### Funnel Tier

Represents one stage of the risk reduction pipeline visualization.

| Attribute | Type | Description |
|-----------|------|-------------|
| tier_number | integer (1-4) | Position in funnel (1=top/widest, 4=bottom/narrowest) |
| label | string | Stage name: "Threats Identified", "Inherent Risk Scored", "Controls Applied", "Residual Risk" |
| width_pct | integer (10-100) | Visual width as percentage of max, proportional to data volume |
| data_source | string | Source file + section for this tier's data |
| render_state | enum | `solid` (data available) or `ghost` (data unavailable) |
| severity_counts | map | Critical/High/Medium/Low counts for this tier |
| total_count | integer | Aggregate count at this tier |
| color | hex | Dominant severity color for tier fill |
| cta_text | string (nullable) | Call-to-action for ghost tiers (e.g., "Run /risk-score") |

### Ghost Tier

Specialization of Funnel Tier when data source is unavailable.

| Attribute | Type | Description |
|-----------|------|-------------|
| opacity | float | Visual opacity (20% / 0.2) |
| border_style | string | "dashed" |
| border_color | hex | #475569 (Slate-600) |
| cta_command | string | Pipeline command to unlock this tier |

### Metrics Sidebar

Aggregate statistics panel displayed alongside the funnel.

| Attribute | Type | Description |
|-----------|------|-------------|
| total_findings | integer | Total findings across all tiers |
| risk_reduction_pct | float (nullable) | Overall risk reduction percentage (null in 1/3-tier mode) |
| control_coverage_pct | float (nullable) | Percentage of findings with controls (null in 1/3-tier mode) |
| per_tier_breakdown | list | Severity distribution per tier |

## Data Source Mapping

| Tier | compensating-controls.md | risk-scores.md | threats.md |
|------|-------------------------|----------------|------------|
| 1 — Threats Identified | Co-located threats.md §6 | Co-located threats.md §6 | §6 Risk Summary |
| 2 — Inherent Risk Scored | Co-located risk-scores.md §2 (or recalculate) | §2 Scored Threat Table | ghost |
| 3 — Controls Applied | §1 Executive Summary + §2 Coverage Matrix | ghost | ghost |
| 4 — Residual Risk | §2 Residual severity bands | ghost | ghost |

## Graceful Degradation States

| Data Source | Solid Tiers | Ghost Tiers | Enhancement Tip |
|-------------|-------------|-------------|-----------------|
| compensating-controls.md | 1, 2, 3, 4 | none | (full pipeline) |
| risk-scores.md | 1, 2, 3* | 4 | "Run /compensating-controls to unlock full funnel" |
| threats.md | 1 | 2, 3, 4 | "Run /risk-score to begin quantifying" |

*Tier 3 in risk-scores mode shows "Unmitigated Risk" using Tier 2 severity data (no control reduction applied).

## Width Calculation

```
For each tier:
  actual_width = (tier_volume / tier_1_volume) * 100

  # Enforce minimum 10% narrowing per tier
  min_width = previous_tier_width - 10
  tier_width = max(actual_width, min_width)
  tier_width = max(tier_width, 10)  # absolute floor
```
