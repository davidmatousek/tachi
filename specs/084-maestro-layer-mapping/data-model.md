# Data Model: MAESTRO Layer Mapping

## Entity: MAESTRO Layer

An architectural classification from the CSA seven-layer taxonomy for agentic AI systems.

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| id | string | L1-L7 | Layer identifier |
| name | string | Foundation Model, Data Operations, Agent Framework, Deployment Infrastructure, Security, Agent Ecosystem, User Interface | Layer display name |
| full_label | string | "L1 — Foundation Model" ... "L7 — User Interface" | Combined label used in output tables |
| keywords | list[string] | Per-layer keyword set | Case-insensitive keywords for classification |

**Immutable**: Layer definitions are fixed by the CSA MAESTRO standard. Changes require shared reference file update.

## Entity: Finding IR Extension

Extension to the existing finding intermediate representation (`schemas/finding.yaml`).

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| maestro_layer | string | No | "Unclassified" | MAESTRO layer assigned to the finding's target component |

**Valid values**: "L1 — Foundation Model", "L2 — Data Operations", "L3 — Agent Framework", "L4 — Deployment Infrastructure", "L5 — Security", "L6 — Agent Ecosystem", "L7 — User Interface", "Unclassified"

**Lifecycle**: Assigned during Phase 1 (component classification) → inherited by findings in Phase 3 → propagated unchanged through risk scoring, control analysis, SARIF export, and narrative reporting.

## Entity: Component Inventory Extension

Extension to the Phase 1 component inventory intermediate artifact.

| Existing Field | Type | Description |
|----------------|------|-------------|
| name | string | Component name from architecture input |
| dfd_type | string | DFD element classification (External Entity, Process, Data Store, Data Flow) |
| description | string | Component description |

| New Field | Type | Default | Description |
|-----------|------|---------|-------------|
| maestro_layer | string | "Unclassified" | MAESTRO layer from keyword matching |

## Entity: SARIF Extension

Extension to SARIF `result` objects for MAESTRO metadata.

| Location | Field | Type | Example |
|----------|-------|------|---------|
| `result.properties.tags[]` | — | string (array entry) | `"maestro-layer:L3"` |
| `result.properties` | `maestro-layer` | string | `"L3 — Agent Framework"` |

**Additive only**: No existing SARIF fields modified or removed.

## Relationships

```
MAESTRO Layer (shared reference)
    │
    ├── 1:N → Component (classified during Phase 1)
    │              │
    │              └── 1:N → Finding (inherits layer from component)
    │                           │
    │                           ├── → threats.md table row (MAESTRO Layer column)
    │                           ├── → SARIF result (properties + tags)
    │                           ├── → risk-scores.md row (passive propagation)
    │                           └── → compensating-controls.md row (passive propagation)
    │
    └── N:1 → Risk by MAESTRO Layer summary (aggregated counts)
```
