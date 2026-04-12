# Data Model: MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis

## Entities

### Attack Chain

The primary entity representing a cross-layer attack progression.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chain_id | string | Yes | Unique identifier (CHAIN-NNN format) |
| title | string | Yes | Human-readable chain title describing the attack progression |
| layers | array[string] | Yes | Ordered MAESTRO layer progression (e.g., ["L2", "L3", "L7"]) |
| max_severity | string | Yes | Highest severity among member findings (Critical, High, Medium, Low) |
| findings | array[ChainMemberFinding] | Yes | Ordered list of member findings with roles and causal relationships |
| narrative | string | Yes | Full chain narrative (150-300 words) covering initial exploit, cascades, business impact |
| chain_breaking_controls | array[ChainBreakingControl] | Yes | Heuristic recommendations for disrupting the chain |
| surfaced | boolean | Yes | Whether this chain meets the Critical/High threshold for report/PDF inclusion |

### Chain Member Finding

A reference to an existing finding participating in a chain.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| finding_id | string | Yes | Reference to finding ID from threats.md |
| maestro_layer | string | Yes | MAESTRO layer assignment (L1-L7) |
| role_in_chain | string | Yes | One of: "initial_exploit", "intermediate_cascade", "terminal_impact" |
| component | string | Yes | Target component name from architecture description |
| stride_category | string | Yes | STRIDE category of the finding |
| severity | string | Yes | Finding severity (Critical, High, Medium, Low) |
| causal_relationship | string | No | Description of how this finding enables the next finding in the chain (null for terminal findings) |

### Chain-Breaking Control

A heuristic recommendation for disrupting an attack chain.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| target_finding_id | string | Yes | The finding whose remediation would break the chain |
| target_layer | string | Yes | MAESTRO layer of the target finding |
| structural_rationale | string | Yes | Why this finding is the chain-breaking point (centrality explanation) |
| control_recommendation | string | Yes | Specific control action to implement |
| is_heuristic | boolean | Yes | Always true — disclaimer that this is structurally derived, not verified |

### Correlation Signal

The evidence connecting two adjacent findings in a chain.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_finding_id | string | Yes | Finding ID of the upstream finding |
| target_finding_id | string | Yes | Finding ID of the downstream finding |
| signal_type | string | Yes | One of: "component_lineage", "data_flow_dependency", "layer_adjacency_structural" |
| evidence | string | Yes | Specific evidence supporting the correlation (e.g., "Component A sends data to Component B via Data Flow DF-3") |

## Relationships

```
Attack Chain 1──* Chain Member Finding (ordered, via findings array)
Chain Member Finding *──1 Finding (reference to threats.md finding by ID)
Attack Chain 1──* Chain-Breaking Control (via chain_breaking_controls array)
Chain Member Finding 1──0..1 Correlation Signal (causal link to next finding)
Finding *──* Attack Chain (many-to-many: a finding can belong to multiple chains)
```

## Validation Rules

1. **Chain minimum length**: `len(layers) >= 2` — chains must span at least 2 distinct MAESTRO layers
2. **Chain maximum length**: `len(layers) <= 7` — at most one finding per MAESTRO layer
3. **Layer uniqueness within chain**: Each MAESTRO layer appears at most once per chain
4. **Finding existence**: All `finding_id` references must exist in the current threats.md output
5. **Layer consistency**: Each member finding's `maestro_layer` must match the corresponding entry in the chain's `layers` array
6. **Role ordering**: Exactly one `initial_exploit` (first), zero or more `intermediate_cascade` (middle), exactly one `terminal_impact` (last)
7. **Surfacing threshold**: `surfaced = true` only when `max_severity in ["Critical", "High"]`
8. **Correlation signal required**: Adjacent findings in a chain must have at least one correlation signal with `signal_type` of `component_lineage` or `data_flow_dependency` (layer adjacency alone is insufficient)
9. **Determinism**: Chain IDs are assigned sequentially (CHAIN-001, CHAIN-002, ...) in the deterministic ranking order (severity desc, length desc, ID alpha asc)

## Schema File: `schemas/attack-chain.yaml`

```yaml
schema_version: "1.0"
# Producers: orchestrator (Phase 3.5 cross-layer correlation)
# Consumers: threat-report agent (Section 6), extract-report-data.py, tachi_parsers.py

chain:
  chain_id:
    type: string
    pattern: "^CHAIN-\\d{3}$"
    description: "Unique chain identifier"
  title:
    type: string
    description: "Human-readable chain title"
  layers:
    type: array
    items: string
    enum_values: ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
    min_items: 2
    max_items: 7
    description: "Ordered MAESTRO layer progression"
  max_severity:
    type: string
    enum: ["Critical", "High", "Medium", "Low"]
    description: "Highest severity among member findings"
  findings:
    type: array
    items: chain_member_finding
    min_items: 2
    max_items: 7
    description: "Ordered list of member findings"
  narrative:
    type: string
    min_length: 150
    max_length: 2000
    description: "Full chain narrative"
  chain_breaking_controls:
    type: array
    items: chain_breaking_control
    min_items: 1
    description: "Heuristic chain-breaking recommendations"
  surfaced:
    type: boolean
    description: "Whether chain meets Critical/High threshold for report inclusion"
```
