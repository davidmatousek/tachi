# T024: Regression Test — Existing Templates

**Status**: PASS
**Date**: 2026-04-08
**Target**: `examples/agentic-app/sample-report/`
**Data Tier**: 1 (compensating-controls)

## Summary

All three pre-existing infographic templates produce valid, consistent output with zero regression after Feature 091 changes to `extract-infographic-data.py`.

## Test Execution

| Template | Exit Code | Finding Count | Tier | JSON Valid |
|----------|-----------|---------------|------|------------|
| baseball-card | 0 | 34 | 1 | Yes |
| system-architecture | 0 | 34 | 1 | Yes |
| risk-funnel | 0 | 34 | 1 | Yes |

## Validation Checks

### Common Fields (all three templates)

| Check | Result |
|-------|--------|
| `project_name` populated | PASS ("Agentic AI Application") |
| `total_findings` > 0 | PASS (34) |
| `severity_distribution` present | PASS (4 entries) |
| `top_findings` present | PASS (5 entries) |
| Severity count sum matches total | PASS (34 = 34 - 0 notes) |
| Percentage sums to 100 | PASS (0 + 21 + 50 + 29 = 100) |
| Heat map row consistency | PASS (7 rows, each critical+high+medium+low = total) |
| Heat map total findings | PASS (11 + 8 + 6 + 3 + 3 + 2 + 1 = 34) |
| No MAESTRO field leakage | PASS (zero MAESTRO keys in top-level or template_data) |

### Severity Distribution (identical across all three)

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 7 | 21% | #EA580C |
| Medium | 17 | 50% | #CA8A04 |
| Low | 10 | 29% | #2563EB |

### Template-Specific Data

**baseball-card**: `risk_weights` (7 components, scores 1.3-2.2, weights low/medium)

**system-architecture**: `trust_zones` (3 zones), `data_flows` (13 flows), `boundary_crossings` (3 crossings), `risk_weights` (7 components)

**risk-funnel**: `funnel_tiers` (4 tiers, all count=34), `reduction_percentages` (3 transitions, all 0%), `missing_enrichments` (empty), `risk_weights` (7 components)

### MAESTRO Leakage Check

Scanned all three output files for the following MAESTRO-specific keys at top-level, metadata, and template_data: `maestro_layer_distribution`, `most_exposed_layer`, `component_layer_map`, `per_finding_maestro`, `maestro_heatmap`, `has_maestro_data`, `per_layer_summaries`.

**Result**: Zero MAESTRO keys found in any non-MAESTRO template output.

## Warnings (Expected)

All three runs produced 14 severity-section mismatch warnings (score-derived band corrections). These are pre-existing and expected behavior from the compensating-controls parser when section headers disagree with computed residual scores.

## Output Files

- `/tmp/regression-baseball-card.json`
- `/tmp/regression-system-architecture.json`
- `/tmp/regression-risk-funnel.json`
