---
type: shared-reference
name: finding-format-shared
version: 1.0.0
source_schema: schemas/finding.yaml
consumers:
  - orchestrator
  - spoofing
  - tampering
  - repudiation
  - info-disclosure
  - denial-of-service
  - privilege-escalation
  - prompt-injection
  - data-poisoning
  - model-theft
  - agent-autonomy
  - tool-abuse
  - risk-scorer
---

# Finding Format — Shared Reference

Canonical finding intermediate representation (IR) specification used across the tachi pipeline. This is the single source of truth for finding structure, field definitions, ID conventions, and validation rules. All producing agents (threat agents) and consuming agents (orchestrator, risk-scorer) should Read this file rather than maintaining inline definitions.

The finding IR is the atomic unit of threat analysis output. Every threat agent (6 STRIDE + 5 AI) produces findings conforming to this format. Every downstream consumer (output assembly, risk scoring, control analysis, reporting) reads findings in this format.

---

## Required Fields

Every finding must include these fields. Missing required fields trigger the non-conforming finding handler in the orchestrator.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique finding identifier. Prefix indicates category, suffix is sequential number. | `S-1`, `AG-2`, `LLM-3` |
| `category` | string (enum) | Threat category. Maps 1:1 to the agent type that produced the finding. | `spoofing`, `tampering`, `agentic`, `llm` |
| `component` | string | Target component name from the architecture input. | `API Gateway`, `LLM Agent` |
| `threat` | string | Description of the identified threat -- what the attacker does and what trust assumption they violate. | `Attacker forges service identity tokens...` |
| `likelihood` | string (enum) | Assessed probability of exploitation. One of: `LOW`, `MEDIUM`, `HIGH`. | `HIGH` |
| `impact` | string (enum) | Assessed severity of exploitation. One of: `LOW`, `MEDIUM`, `HIGH`. | `HIGH` |
| `risk_level` | string (enum) | Computed from the OWASP 3x3 matrix. One of: `Critical`, `High`, `Medium`, `Low`, `Note`. | `Critical` |
| `mitigation` | string | Recommended countermeasure -- specific technology or configuration, not generic advice. | `Enforce mTLS with certificate pinning...` |

### Category Enum Values

```
spoofing | tampering | repudiation | info-disclosure |
denial-of-service | privilege-escalation | agentic | llm
```

---

## Optional Fields

These fields are present in specific pipeline contexts but not required for every finding.

| Field | Type | Present When | Description |
|-------|------|-------------|-------------|
| `references` | list[string] | AI categories (required), STRIDE (optional) | OWASP IDs, CVE IDs, or framework citations. Required for `agentic` and `llm` categories. |
| `dfd_element_type` | string (enum) | Threat agent output | DFD classification of the target component. One of: `External Entity`, `Process`, `Data Store`, `Data Flow`. |
| `delta_status` | string (enum) | Baseline-aware runs | Lifecycle status: `NEW`, `UNCHANGED`, `UPDATED`, `RESOLVED`. Defaults to `NEW` when no baseline is present. |
| `baseline_run_id` | string (nullable) | Baseline-aware runs | Run ID of the baseline that first discovered this finding. Null for first-run findings. |
| `maestro_layer` | string (enum) | Phase 1 classification | CSA MAESTRO architectural layer classification for the finding's target component. One of: `L1 — Foundation Model`, `L2 — Data Operations`, `L3 — Agent Framework`, `L4 — Deployment Infrastructure`, `L5 — Evaluation and Observability`, `L6 — Security and Compliance`, `L7 — Agent Ecosystem`, `Unclassified`. Defaults to `"Unclassified"` when not present or when the component matched no layer keywords. Assigned during Phase 1 and inherited by findings in Phase 3. |
| `correlation_group` | string | Correlated findings | Correlation group ID (e.g., `CG-1`). Present when the finding belongs to a cross-category correlation group. |
| `fingerprints` | object | SARIF output | Partial fingerprints for cross-run correlation: `findingId/v1` (primary key) and `primaryLocationLineHash` (validation signal). |

---

## ID Format Conventions

Finding IDs follow the pattern `{PREFIX}-{N}` where PREFIX indicates the threat category and N is a sequential integer starting at 1 within each category.

### ID Prefix Table

| Prefix | Category | Agent(s) |
|--------|----------|----------|
| S | Spoofing | tachi-spoofing |
| T | Tampering | tachi-tampering |
| R | Repudiation | tachi-repudiation |
| I | Information Disclosure | tachi-info-disclosure |
| D | Denial of Service | tachi-denial-of-service |
| E | Elevation of Privilege | tachi-privilege-escalation |
| AG | Agentic Threats | tachi-agent-autonomy, tachi-tool-abuse |
| LLM | LLM Threats | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft |

### ID Rules

1. IDs are sequentially numbered within each category starting at 1, with no gaps.
2. No duplicate IDs within any table or across tables of the same category.
3. The ID prefix must match the category: `S-*` -> spoofing, `T-*` -> tampering, `R-*` -> repudiation, `I-*` -> info-disclosure, `D-*` -> denial-of-service, `E-*` -> privilege-escalation, `AG-*` -> agentic, `LLM-*` -> llm.
4. ID pattern regex: `^(S|T|R|I|D|E|AG|LLM)-\d+$`

---

## STRIDE Table Format

Six tables, one per STRIDE category. Each row uses these columns:

| ID | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|--------|------------|--------|------------|------------|

When baseline-aware, an additional Status column is included after ID:

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|

Status values: `NEW`, `UNCHANGED`, `UPDATED`.

---

## AI Table Format

Two tables (AG and LLM). Each row includes an OWASP Reference field:

| ID | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|---------------|--------|------------------|------------|--------|------------|------------|

When baseline-aware, an additional Status column is included after ID:

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|

---

## Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

Every finding's `risk_level` must match the matrix computation for its `likelihood` and `impact` values. Mismatches are corrected by the orchestrator's Risk Level Validation step before output assembly.

---

## Validation Rules

### Field-Level Validation

1. `id` prefix must match `category` (see ID Prefix Table).
2. `risk_level` must match the OWASP 3x3 matrix computation for the given `likelihood` and `impact`.
3. `references` must contain at least one entry for AI categories (`agentic`, `llm`).
4. `likelihood` must be one of: `LOW`, `MEDIUM`, `HIGH`.
5. `impact` must be one of: `LOW`, `MEDIUM`, `HIGH`.
6. `risk_level` must be one of: `Critical`, `High`, `Medium`, `Low`, `Note`.

### Non-Conforming Finding Handling

When a finding does not conform to the schema, the orchestrator applies recovery rules rather than dropping the finding:

1. Missing or malformed `id`: Assign the next sequential ID in the appropriate category.
2. Non-enum `likelihood` or `impact`: Map to the closest valid value (e.g., "high" -> "HIGH", "moderate" -> "MEDIUM") or default to "MEDIUM". Recompute `risk_level`.
3. Missing `component`: Use the target component name from the dispatch record.
4. Missing `mitigation`: Enter `"[No mitigation provided by agent -- review required]"`.
5. Annotate the finding by appending a warning to the Mitigation field.
6. Include the annotated finding in all downstream computations.

---

## Category Display Name Mapping

Used in report output and human-readable tables:

| Internal Name | Display Name |
|---------------|-------------|
| `spoofing` | Spoofing |
| `tampering` | Tampering |
| `repudiation` | Repudiation |
| `info-disclosure` | Information Disclosure |
| `denial-of-service` | Denial of Service |
| `privilege-escalation` | Privilege Escalation |
| `agentic` | Agentic Threats |
| `llm` | LLM Threats |
