# Data Model: Infographic Extraction JSON Output

## Overview

The infographic extraction script outputs a single JSON file that serves as the data contract between the deterministic extraction script and the infographic agent. The agent reads this JSON to populate Sections 1-5 of the spec markdown.

## JSON Schema

### Top-Level Structure

```json
{
  "metadata": { ... },
  "severity_distribution": [ ... ],
  "heat_map": [ ... ],
  "top_findings": [ ... ],
  "template_data": { ... }
}
```

### metadata

```json
{
  "project_name": "string",
  "scan_date": "string (YYYY-MM-DD)",
  "tier": "integer (1, 2, or 3)",
  "template": "string (baseball-card | system-architecture | risk-funnel)",
  "data_source_type": "string (threats | risk-scores | compensating-controls)",
  "total_findings": "integer (deduplicated count, includes Note)",
  "note_count": "integer",
  "agent_count": "integer (number of STRIDE+AI agents that produced findings)",
  "risk_posture": "string (one-sentence summary)",
  "schema_version": "string (from threats.md frontmatter)"
}
```

### severity_distribution

Array of severity entries, ordered by `SEVERITY_ORDER` (Critical, High, Medium, Low). Note severity excluded.

```json
[
  {
    "label": "Critical",
    "count": 5,
    "percentage": 12,
    "color": "#DC2626"
  },
  {
    "label": "High",
    "count": 14,
    "percentage": 33,
    "color": "#EA580C"
  },
  {
    "label": "Medium",
    "count": 18,
    "percentage": 43,
    "color": "#CA8A04"
  },
  {
    "label": "Low",
    "count": 5,
    "percentage": 12,
    "color": "#2563EB"
  }
]
```

**Invariants**:
- Sum of `percentage` values == 100 (or 0 when all counts are 0)
- Sum of `count` values == `metadata.total_findings` - `metadata.note_count`
- Percentages computed using Largest Remainder Method
- Color codes follow tachi severity palette

### heat_map

Array of component rows, ordered by total descending then name ascending. Max 8 rows (top 7 + "Other").

```json
[
  {
    "component": "API Gateway",
    "critical": 2,
    "high": 5,
    "medium": 3,
    "low": 1,
    "total": 11
  },
  {
    "component": "Other",
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 0,
    "total": 3
  }
]
```

**Invariants**:
- `critical + high + medium + low == total` for each row
- All components from scope data appear (zero-filled if no findings)
- "Other" row present only when input components > 8

### top_findings

Array of up to 5 findings, deterministically sorted.

```json
[
  {
    "id": "S-001",
    "component": "API Gateway",
    "threat": "Authentication bypass via token replay",
    "risk_level": "Critical",
    "score": 9.2
  }
]
```

**Sort order**: `score` descending, then `id` ascending (lexicographic) for ties.

**Score source by tier**:
- Tier 1: residual score from compensating-controls.md
- Tier 2: composite score from risk-scores.md
- Tier 3: severity ordinal (Critical=4, High=3, Medium=2, Low=1)

### template_data

Template-specific data. Structure depends on `metadata.template`.

#### baseball-card

```json
{
  "risk_weights": [
    {
      "component": "API Gateway",
      "weight": "high",
      "score": 3.2,
      "annotation": "5 High + 2 Critical findings"
    }
  ]
}
```

**Weight classification**: score >= 3.0 = "high", score >= 2.0 = "medium", score < 2.0 = "low"
**Score formula**: `(critical*4 + high*3 + medium*2 + low*1) / total_findings_for_component`

#### system-architecture

```json
{
  "risk_weights": [ ... ],
  "trust_zones": [
    {
      "name": "External Network",
      "trust_level": "untrusted",
      "components": ["User Browser", "External API"]
    }
  ],
  "data_flows": [
    {
      "source": "User Browser",
      "destination": "API Gateway",
      "severity_color": "#DC2626",
      "label": "HTTPS requests"
    }
  ],
  "boundary_crossings": [
    {
      "from_zone": "External Network",
      "to_zone": "DMZ",
      "crossing_point": "Load Balancer",
      "finding_count": 3
    }
  ]
}
```

**trust_zones**: `null` when scope data has no trust zones (flat component layout).
**severity_color**: Determined by highest-severity finding targeting the flow's destination component.

#### risk-funnel

```json
{
  "risk_weights": [ ... ],
  "funnel_tiers": [
    {
      "tier": 0,
      "label": "Threats Identified",
      "count": 42,
      "source": "threats.md Section 6"
    },
    {
      "tier": 1,
      "label": "Inherent Risk Scored",
      "count": 34,
      "source": "risk-scores.md"
    },
    {
      "tier": 2,
      "label": "Controls Applied",
      "count": 34,
      "source": "compensating-controls.md"
    },
    {
      "tier": 3,
      "label": "Residual Risk",
      "count": 12,
      "source": "compensating-controls.md residual"
    }
  ],
  "reduction_percentages": [
    {
      "from_tier": 0,
      "to_tier": 1,
      "percentage": 19
    },
    {
      "from_tier": 1,
      "to_tier": 2,
      "percentage": 0
    },
    {
      "from_tier": 2,
      "to_tier": 3,
      "percentage": 65
    }
  ],
  "missing_enrichments": []
}
```

**funnel_tiers[n]**: `null` when the corresponding artifact is absent.
**missing_enrichments**: Array of command strings (e.g., `["/risk-score", "/compensating-controls"]`) when intermediate artifacts are missing.
**reduction_percentages**: Only computed between adjacent non-null tiers. Uses Largest Remainder Method when presented as a set.

## Shared Module Entities (`tachi_parsers.py`)

### Constants
- `SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Note"]`
- `STRIDE_PREFIXES` — maps threat ID prefix to STRIDE/AI category name
- `EXIT_SUCCESS = 0`, `EXIT_MISSING_ARTIFACT = 1`, `EXIT_VALIDATION_FAILURE = 2`

### Color Palette
- Critical: `#DC2626`
- High: `#EA580C`
- Medium: `#CA8A04`
- Low: `#2563EB`
- Note: `#6B7280`
