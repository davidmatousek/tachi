# Quickstart: /infographic Command

## Basic Usage

Generate infographics from the best available data source:

```bash
# Auto-detect data source in current directory
/infographic

# Auto-detect data source in a specific directory
/infographic path/to/output/

# Use a specific file
/infographic path/to/risk-scores.md
/infographic path/to/threats.md
```

## Template Selection

```bash
# Executive summary (dark theme, 4-zone layout)
/infographic --template baseball-card

# Technical architecture view (white theme, zone-stacked)
/infographic --template system-architecture

# Both templates (default)
/infographic --template all
```

## Typical Workflow

```bash
# 1. Run threat analysis
/threat-model docs/security/architecture.md

# 2. (Optional) Enrich with quantitative risk scoring
/risk-score

# 3. Generate infographics — automatically uses richest data
/infographic
```

## Output Files

| File | Description | Condition |
|------|-------------|-----------|
| `threat-baseball-card-spec.md` | Baseball card specification | When template = `baseball-card` or `all` |
| `threat-baseball-card.jpg` | Baseball card image | When GEMINI_API_KEY available |
| `threat-system-architecture-spec.md` | System architecture specification | When template = `system-architecture` or `all` |
| `threat-system-architecture.jpg` | System architecture image | When GEMINI_API_KEY available |

## Data Source Priority

The command automatically selects the richest available data:

1. `risk-scores.md` (quantitative composite scores) — preferred
2. `threats.md` (qualitative severity counts) — fallback

When `risk-scores.md` is used, co-located `threats.md` is also read for structural data (project metadata, trust zones, data flows).
