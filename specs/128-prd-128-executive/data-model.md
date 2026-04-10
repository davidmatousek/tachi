# Data Model: Executive Threat Architecture Infographic (F-128)

**Created**: 2026-04-09
**Plan**: [plan.md](plan.md)

This document defines the data structures used by the F-128 extraction script and the JSON contract between extraction, the agent, and the PDF assembly pipeline.

---

## Entity: ArchitecturalLayer

A grouping of system components representing one tier of the system architecture for executive presentation. Distinct from MAESTRO layers (CSA seven-layer agentic AI taxonomy from F-084).

### Fields

| Field | Type | Required | Source | Description |
|-------|------|----------|--------|-------------|
| `name` | string | yes | `parse_scope_data().trust_boundaries[].zone` (primary) OR DFD type fallback | Human-readable layer name (e.g., "Untrusted Edge", "Application Tier", "Data Store"). Truncated to 50 chars with ellipsis if longer. |
| `position` | integer | yes | derived | Ordinal position in the trust hierarchy (0 = top of hierarchy / least trusted, increasing toward most trusted). Used for layer ordering. |
| `components` | string[] | yes | `parse_scope_data().trust_boundaries[].components` (split by comma, trimmed) | List of component names contained in this layer. |
| `component_count` | integer | yes | `len(components)` | Cached count for spec rendering. |
| `source_kind` | string | yes | `"trust_zone"` or `"dfd_type"` | Indicates whether the layer was derived from trust zones (preferred) or fallback to DFD component type grouping. |

### Layer Ordering Rules

1. When source is `trust_zone`: order by trust level ascending (`untrusted < semi-trusted < trusted`), so the most exposed layers appear at the top of the diagram (matches "where attackers enter the system" mental model).
2. When source is `dfd_type`: group by DFD type name alphabetically. This is a fallback for threat models without trust boundary data.
3. Tie-break: alphabetical by `name` ascending.

### Validation

- `name` MUST be non-empty after trimming.
- `components` MUST be non-empty (a layer with no components is dropped from the output before serialization).
- `position` MUST be unique within the `layers[]` array.
- `source_kind` MUST be one of `"trust_zone"` or `"dfd_type"`.

---

## Entity: ThreatCallout

A narrative annotation attached to one architectural layer, representing the highest-severity Critical/High finding affecting that layer.

### Fields

| Field | Type | Required | Source | Description |
|-------|------|----------|--------|-------------|
| `layer_name` | string | yes | derived from layer association | The `ArchitecturalLayer.name` this callout is attached to. Foreign key to `layers[]`. |
| `finding_id` | string | yes | `parse_threats_findings()[].id` | Stable identifier of the finding (e.g., `STRIDE-T-003`, `AI-PI-001`). |
| `severity` | string | yes | `parse_threats_findings()[].severity` | One of `"Critical"` or `"High"` (other severities are filtered out before callout selection). |
| `raw_description` | string | yes | `parse_threats_findings()[].description` (or `title` if description absent) | Unmodified finding description from the source markdown. The agent's Gemini prompt is responsible for rewriting this to ≤25 words plain English. |
| `composite_score` | float \| null | no | `parse_threats_findings()[].composite_score` (when source tier is risk-scores or compensating-controls); null otherwise | Numeric score used as the secondary tie-breaker when selecting the top finding per layer. |
| `affected_component` | string \| null | no | `parse_threats_findings()[].component` | Optional: the specific component within the layer that the finding affects. Used by the Gemini prompt to anchor the callout's visual position. |

### Callout Selection Rules

For each `ArchitecturalLayer`:

1. Filter findings to those whose `affected_component` is in `layer.components`.
2. Filter further to `severity in {"Critical", "High"}`.
3. If the filtered set is empty: no callout for this layer.
4. Sort the filtered set by:
   1. `severity` descending (Critical before High)
   2. `composite_score` descending (null treated as 0)
   3. `finding_id` ascending (lexicographic, deterministic tie-break)
5. Select the first element after sort.

### Validation

- `layer_name` MUST match a `name` in the `layers[]` array of the parent payload.
- `severity` MUST be exactly `"Critical"` or `"High"` (case-sensitive).
- `finding_id` MUST be unique across all callouts in the payload (one finding cannot be a callout for two layers).
- `raw_description` MUST be non-empty after trimming.

---

## Entity: SeverityDistribution (filtered)

A count of Critical and High findings only, distinct from the full severity distribution used by other infographic templates.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `critical_count` | integer | yes | Number of Critical-severity findings in the source threat model |
| `high_count` | integer | yes | Number of High-severity findings in the source threat model |
| `total_qualifying` | integer | yes | `critical_count + high_count` (cached) |
| `total_after_layer_dedup` | integer | yes | Number of callouts actually shown (one per layer that has a qualifying finding); ≤ `total_qualifying` |

### Validation

- All counts MUST be non-negative integers.
- `total_qualifying` MUST equal `critical_count + high_count`.
- `total_after_layer_dedup` MUST be ≤ `total_qualifying`.

---

## Entity: PayloadMetadata

Metadata header attached to the JSON payload for traceability and downstream behavior.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_name` | string | yes | Always `"executive-architecture"` |
| `tier_source` | string | yes | One of `"compensating-controls"`, `"risk-scores"`, `"threats"` — indicates which source file was used (matches existing tier detection convention from F-048) |
| `source_file` | string | yes | Absolute or repo-relative path to the source markdown file used for extraction |
| `generation_timestamp` | string | yes | ISO 8601 UTC timestamp of extraction (`YYYY-MM-DDTHH:MM:SSZ`) |
| `qualifying_layer_count` | integer | yes | Number of layers in the `layers[]` array (after dropping empty layers) |
| `total_filtered_count` | integer | yes | Total Critical/High findings before per-layer dedup |
| `skip_image` | boolean | yes | `true` when 0 Critical/High findings exist, signaling the agent to skip Gemini invocation; `false` otherwise |
| `fallback_used` | boolean | yes | `true` when the layer source was `dfd_type` (fallback) instead of `trust_zone`; `false` otherwise |

### Validation

- `template_name` MUST be exactly `"executive-architecture"`.
- `tier_source` MUST be one of the three allowed values.
- `generation_timestamp` MUST be a valid ISO 8601 UTC timestamp.
- `skip_image == true` IFF `total_filtered_count == 0`.

---

## Aggregate: ExecutiveArchitecturePayload

The top-level JSON object emitted by `extract-infographic-data.py --template executive-architecture`. Consumed by the `tachi-threat-infographic` agent.

### Schema

```json
{
  "metadata": {
    "template_name": "executive-architecture",
    "tier_source": "compensating-controls",
    "source_file": "examples/agentic-app/sample-report/threats.md",
    "generation_timestamp": "2026-04-09T15:30:00Z",
    "qualifying_layer_count": 4,
    "total_filtered_count": 11,
    "skip_image": false,
    "fallback_used": false
  },
  "layers": [
    {
      "name": "Untrusted Edge",
      "position": 0,
      "components": ["API Gateway", "Public Web UI"],
      "component_count": 2,
      "source_kind": "trust_zone"
    },
    {
      "name": "Application Tier",
      "position": 1,
      "components": ["Order Service", "Auth Service", "Inventory Service"],
      "component_count": 3,
      "source_kind": "trust_zone"
    },
    {
      "name": "Data Store",
      "position": 2,
      "components": ["Postgres", "Redis Cache"],
      "component_count": 2,
      "source_kind": "trust_zone"
    },
    {
      "name": "Foundation Model",
      "position": 3,
      "components": ["LLM Provider"],
      "component_count": 1,
      "source_kind": "trust_zone"
    }
  ],
  "callouts": [
    {
      "layer_name": "Untrusted Edge",
      "finding_id": "STRIDE-T-001",
      "severity": "Critical",
      "raw_description": "Lack of input validation on the order intake endpoint enables SQL injection in downstream queries to the orders table.",
      "composite_score": 9.2,
      "affected_component": "API Gateway"
    },
    {
      "layer_name": "Application Tier",
      "finding_id": "STRIDE-E-004",
      "severity": "High",
      "raw_description": "Auth service issues JWT tokens without verifying audience claim, allowing token replay across services.",
      "composite_score": 7.8,
      "affected_component": "Auth Service"
    },
    {
      "layer_name": "Data Store",
      "finding_id": "STRIDE-I-002",
      "severity": "High",
      "raw_description": "Postgres backups are stored in S3 without encryption at rest, exposing PII if the bucket is misconfigured.",
      "composite_score": 7.5,
      "affected_component": "Postgres"
    },
    {
      "layer_name": "Foundation Model",
      "finding_id": "AI-PI-001",
      "severity": "Critical",
      "raw_description": "Prompt injection via untrusted user message bypasses system prompt boundaries and allows tool invocation.",
      "composite_score": 9.0,
      "affected_component": "LLM Provider"
    }
  ],
  "severity_distribution": {
    "critical_count": 4,
    "high_count": 7,
    "total_qualifying": 11,
    "total_after_layer_dedup": 4
  }
}
```

### Top-Level Validation

- `metadata`, `layers`, `callouts`, `severity_distribution` are all required keys.
- `layers[]` MAY be empty if neither trust zones nor DFD types yield any layers (this triggers exit code 2 in extraction with an error message).
- `callouts[]` MAY be empty if `total_filtered_count == 0` (this sets `metadata.skip_image == true`).
- For each callout, `callout.layer_name` MUST exist as a `layer.name` in `layers[]`.
- `severity_distribution.total_after_layer_dedup` MUST equal `len(callouts)`.

---

## Skipped-Image Edge Case

When the input threat model has zero Critical and zero High severity findings:

```json
{
  "metadata": {
    "template_name": "executive-architecture",
    "tier_source": "threats",
    "source_file": "examples/synthetic/no-critical/threats.md",
    "generation_timestamp": "2026-04-09T15:30:00Z",
    "qualifying_layer_count": 4,
    "total_filtered_count": 0,
    "skip_image": true,
    "fallback_used": false
  },
  "layers": [ /* full layer list still emitted */ ],
  "callouts": [],
  "severity_distribution": {
    "critical_count": 0,
    "high_count": 0,
    "total_qualifying": 0,
    "total_after_layer_dedup": 0
  }
}
```

The agent reads `metadata.skip_image == true` and produces a markdown spec with an explanatory note in the Threat Callouts section. The agent does NOT invoke Gemini. Downstream PDF compilation does not include the executive architecture page (because the JPEG file does not exist).

---

## Mapping to Existing Parser Functions

| Entity / Field | Source Function | File:Line |
|----------------|-----------------|-----------|
| `ArchitecturalLayer.name`, `components` (trust_zone source) | `_compute_trust_zones()` | `scripts/extract-infographic-data.py:620-655` |
| `ArchitecturalLayer.name`, `components` (dfd_type source) | NEW helper function (to be added) | `scripts/extract-infographic-data.py` (new) |
| `ThreatCallout.finding_id`, `severity`, `raw_description`, `composite_score`, `affected_component` | `parse_threats_findings()` (existing) or tier-specific parsers (`parse_risk_scores()`, `parse_compensating_controls()`) | `scripts/tachi_parsers.py` |
| `SeverityDistribution.critical_count`, `high_count` | `compute_severity_percentages()` (existing, but filtered) | `scripts/extract-infographic-data.py:158-189` |
| `PayloadMetadata.tier_source` | Existing tier detection logic | `scripts/extract-infographic-data.py` (existing tier detection) |

**Reuse principle**: All parsing logic comes from existing functions in `tachi_parsers.py` and `extract-infographic-data.py`. The only new code is the dispatch branch that combines existing helpers into the new payload shape, plus a new fallback function for DFD-type-based layer grouping when trust zones are absent.
