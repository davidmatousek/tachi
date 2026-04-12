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

---

## For Threat Agents (Producers)

This section gives producer-oriented guidance for threat agents constructing findings. Consumers (orchestrator, risk-scorer) rely on the sections above; producers use this section in combination with them.

### Producer ID Prefix Assignment

Each threat agent owns a single prefix from the ID Prefix Table. Producers assign sequential numbers within their own prefix starting at 1 per invocation. `agentic` and `llm` prefixes are shared across multiple producers — the orchestrator renumbers if duplicates occur during Phase 3 aggregation.

| Producer Agent | Category | ID Prefix |
|----------------|----------|-----------|
| tachi-spoofing | spoofing | S |
| tachi-tampering | tampering | T |
| tachi-repudiation | repudiation | R |
| tachi-info-disclosure | info-disclosure | I |
| tachi-denial-of-service | denial-of-service | D |
| tachi-privilege-escalation | privilege-escalation | E |
| tachi-prompt-injection | llm | LLM |
| tachi-data-poisoning | llm | LLM |
| tachi-model-theft | llm | LLM |
| tachi-tool-abuse | agentic | AG |
| tachi-agent-autonomy | agentic | AG |

### Field Construction Guidance

When constructing a finding, populate each field as follows:

- **`id`**: Assign sequentially within your prefix (e.g., `S-1` for the first spoofing finding this run).
- **`category`**: Use the canonical enum value from the Category Enum Values section — not a display name.
- **`component`**: Use the exact component name from the orchestrator dispatch record. Do not paraphrase or abbreviate.
- **`threat`**: 1–3 sentences describing what the attacker does AND which trust assumption they violate. Be concrete about the attack path on this specific component — avoid generic CVE-style descriptions.
- **`likelihood`** / **`impact`**: Assess using OWASP factors (attacker skill, opportunity, detection difficulty for likelihood; loss of confidentiality/integrity/availability + accountability for impact). Pick `LOW`, `MEDIUM`, or `HIGH`.
- **`risk_level`**: Compute via the OWASP 3x3 matrix in the Risk Level Computation section — do not assign independently. Mismatches are corrected by the orchestrator.
- **`mitigation`**: Actionable, technology-specific guidance. Name the mechanism (mTLS with certificate pinning, Argon2id password hashing, step-up auth for admin operations). Do not emit generic advice ("use strong auth").
- **`references`**: Required for `agentic` and `llm` categories, optional for STRIDE. Cite from your agent's Primary Sources list in `detection-patterns.md` to maintain traceability.
- **`dfd_element_type`**: Use the DFD classification provided by the orchestrator dispatch record (`External Entity`, `Process`, `Data Store`, `Data Flow`).

### Risk Level Computation Example

An agent observes that an API Gateway exposes internal account management without authentication. Attacker skill and opportunity are trivial (likelihood `HIGH`); successful exploitation loses confidentiality + integrity on a high-value asset (impact `HIGH`). Applying the OWASP 3x3 matrix: `HIGH × HIGH → Critical`. The finding is emitted with `likelihood: HIGH`, `impact: HIGH`, `risk_level: Critical`. If the producer emits a different `risk_level`, the orchestrator's Risk Level Validation step corrects it and flags the finding for review.

### Reference Linking Conventions

Each entry in the `references` field should be a self-contained identifier resolvable without additional context:

- **OWASP Top 10**: `A01:2021`, `LLM06:2025`
- **OWASP API Security**: `API1:2023`, `API2:2023`
- **CWE**: `CWE-287`, `CWE-918`
- **MITRE ATT&CK**: `T1190`, `T1548.003`
- **MITRE ATLAS**: `AML.T0051`, `AML.T0058`
- **NIST**: `NIST SP 800-63B §5.1.1`, `NIST AI 600-1 §2.1`

CSA MAESTRO is NOT emitted as a reference — the MAESTRO layer is a separate `maestro_layer` field populated during orchestrator Phase 1, not by the producer.
