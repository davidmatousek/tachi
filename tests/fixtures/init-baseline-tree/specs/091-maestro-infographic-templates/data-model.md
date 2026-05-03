# Data Model: MAESTRO Infographic Templates and PDF Report Section

## MAESTRO Layer Entity

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| layer_id | string | threats.md Section 1/6 | "L1" through "L7" or "Unclassified" |
| layer_name | string | threats.md Section 1/6 | Full name (e.g., "Foundation Model") |
| finding_count | integer | Computed from Section 6 | Number of findings classified to this layer |
| highest_severity | string | Computed from Section 6 | Highest severity among findings in this layer |

## Layer Distribution (Aggregate)

Parsed from threats.md Section 6 "Risk by MAESTRO Layer" table:

```
#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L1 — Foundation Model | 8 | Critical |
```

**JSON output format** (in `infographic-data.json`):

```json
{
  "maestro_layer_distribution": [
    {"layer_id": "L1", "layer_name": "Foundation Model", "finding_count": 8, "highest_severity": "Critical"},
    {"layer_id": "L3", "layer_name": "Agent Framework", "finding_count": 5, "highest_severity": "High"}
  ],
  "most_exposed_layer": "L1 — Foundation Model"
}
```

## Component-Layer Intersection (Heatmap)

Derived from per-finding MAESTRO layer data in Section 3 agent tables, cross-referenced with component names:

```json
{
  "maestro_heatmap": [
    {
      "component": "LLM Agent Orchestrator",
      "layers": {
        "L1": "Critical",
        "L3": "High",
        "L5": null
      }
    }
  ]
}
```

Each cell value is the highest severity at that (component, layer) intersection, or null if no findings.

## Typst Variable Mappings

### report-data.typ new variables

| Typst Variable | Type | Source | Default |
|----------------|------|--------|---------|
| `has-maestro-data` | boolean | Presence of MAESTRO data in findings | `false` |
| `maestro-layer-distribution` | array of dicts | Section 6 parse | `()` |
| `most-exposed-layer` | string | Computed (highest count) | `""` |
| `maestro-findings-by-layer` | array of layer groups | Section 3 parse + grouping | `()` |
| `has-maestro-stack-image` | boolean | Image file detection | `false` |
| `maestro-stack-image-path` | string | File path | `""` |
| `has-maestro-heatmap-image` | boolean | Image file detection | `false` |
| `maestro-heatmap-image-path` | string | File path | `""` |

### maestro-findings-by-layer structure

```typst
#let maestro-findings-by-layer = (
  (
    layer-id: "L1",
    layer-name: "Foundation Model",
    findings: (
      (id: "S-1", component: "LLM Engine", severity: "Critical", threat: "Attacker impersonates..."),
      (id: "LLM-3", component: "LLM Engine", severity: "High", threat: "Adversarial prompt..."),
    ),
  ),
  (
    layer-id: "L3",
    layer-name: "Agent Framework",
    findings: (
      (id: "AG-1", component: "Orchestrator", severity: "High", threat: "Unauthorized tool..."),
    ),
  ),
)
```

## Extraction Source Strategy

| Data Need | Primary Source | Fallback |
|-----------|--------------|----------|
| Layer distribution (aggregate) | threats.md Section 6 "Risk by MAESTRO Layer" | Compute from Section 3 findings |
| Per-finding MAESTRO layer | threats.md Section 3 agent tables (`MAESTRO Layer` column) | Component lookup from Section 1 |
| Component-to-layer mapping | threats.md Section 1 Components table | N/A |
| MAESTRO data presence | Any of above returns data | All empty → `has-maestro-data = false` |
