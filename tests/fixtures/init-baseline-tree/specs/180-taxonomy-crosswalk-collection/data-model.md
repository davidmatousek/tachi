# Data Model: F-A1 Taxonomy Crosswalk Collection

**Feature**: 180-taxonomy-crosswalk-collection
**Phase**: 1 — Design & Contracts
**Source**: [spec.md](./spec.md) FR-003 through FR-014

---

## 1. Entity: Catalog Record

Authoritative shape for records in 7 catalog YAMLs (5 external framework + 2 tachi pseudo-taxonomy).

### Fields

| Field | Type | Required | Constraints | Source |
|-------|------|----------|-------------|--------|
| `id` | string | Yes | Unique within file; short canonical form | FR-004 |
| `full_id` | string | Yes | Human-readable long form with framework prefix | FR-005 |
| `name` | string | Yes | Verbatim from authoritative source | FR-006 |
| `url` | string | Yes | URL-shaped OR existing repo file path | FR-007 |
| `cwe_refs` | list[string] | Conditional | **Required (with `[]` allowed) on all 6 non-cwe catalogs** (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, tachi-control-category, tachi-stride-ai-category); **OMITTED entirely** on cwe.yaml records. On owasp.yaml records the list SHOULD be populated where the OWASP source publishes CWE cross-references; on other non-cwe catalogs the list MAY be empty `[]` but the key MUST be present. | FR-003, FR-008 |

### Validation rules

- **Uniqueness**: `id` MUST be unique within each catalog YAML (enforced by `test_framework_yamls_load()`)
- **Shape**: every record MUST contain all required fields and MUST NOT contain fields outside the contract (strict schema)
- **URL**: `url` field MUST match URL-regex (`^https?://`) OR resolve to an existing path relative to repo root (pseudo-taxonomy convention)
- **cwe_refs**: when present, each entry MUST match regex `^CWE-\d+$`; entries do not need to resolve in `cwe.yaml` in F-A1 (forward-compat — future F-A1 extensions may add CWEs to cwe.yaml)

### Examples (annotated)

**OWASP LLM Top 10 item**:
```yaml
- id: LLM05
  full_id: OWASP-LLM-2025-05
  name: Improper Output Handling
  url: https://genai.owasp.org/llmrisk/llm05-improper-output-handling/
  cwe_refs: [CWE-79, CWE-89, CWE-116]
```

**CWE record** (no `cwe_refs` field):
```yaml
- id: CWE-89
  full_id: CWE-89
  name: "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')"
  url: https://cwe.mitre.org/data/definitions/89.html
```

**Pseudo-taxonomy record** (tachi-control-category):
```yaml
- id: authentication
  full_id: TACHI-CONTROL-authentication
  name: Authentication
  url: .claude/skills/tachi-control-analysis/references/control-categories.md
  cwe_refs: []
```

---

## 2. Entity: Crosswalk Edge

Authoritative shape for records in `crosswalk.yaml`.

### Fields

| Field | Type | Required | Constraints | Source |
|-------|------|----------|-------------|--------|
| `source.taxonomy` | string | Yes | Member of 7-value `taxonomy` enum | FR-010 |
| `source.id` | string | Yes | Resolves to a record in catalog YAML named by `source.taxonomy` | FR-011 |
| `target.taxonomy` | string | Yes | Member of 7-value `taxonomy` enum | FR-010 |
| `target.id` | string | Yes | Resolves to a record in catalog YAML named by `target.taxonomy` | FR-011 |
| `edge_type` | string | Yes | Member of 3-value `edge_type` enum | FR-012 |
| `confidence` | string | Yes | Member of 3-value `confidence` enum | FR-013 |
| `citation` | string | Yes | Non-empty; URL-shaped OR existing repo file path | FR-014 |

### Validation rules

- **Referential integrity**: `source.id` MUST resolve to an `id` in the catalog YAML whose filename stem matches `source.taxonomy`. Identical rule for `target.id` / `target.taxonomy`. (Enforced by `test_crosswalk_referential_integrity()`.)
- **Enum closure**: `source.taxonomy`, `target.taxonomy`, `edge_type`, `confidence` MUST each be in their respective closed enum.
- **Uniqueness**: no duplicate edges — the 3-tuple `{source, target, edge_type}` MUST be unique across the full crosswalk. (Enforced by `test_crosswalk_loads()`.)
- **Citation non-empty + resolvable**: `citation` MUST be a non-empty string that is either URL-regex-matched or file-path-resolvable. (Enforced by `test_citation_shape()`.)

### Example (annotated)

**NIST Surface B edge** (tachi-control-category → nist-ai-rmf):
```yaml
- source:
    taxonomy: tachi-control-category
    id: authentication
  target:
    taxonomy: nist-ai-rmf
    id: MEASURE-2.7
  edge_type: primary
  confidence: high
  citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md
```

**OWASP LLM → CWE edge** (with external URL citation):
```yaml
- source:
    taxonomy: owasp
    id: LLM05
  target:
    taxonomy: cwe
    id: CWE-79
  edge_type: primary
  confidence: high
  citation: https://genai.owasp.org/llmrisk/llm05-improper-output-handling/
```

**CWE superseded edge** (CWE→CWE shape example; ILLUSTRATIVE ONLY — `superseded` edges are **out of F-A1 scope** per spec FR-025 "F-A1 default scope is primary-only"; CWE→CWE shape is supported by FR-003 exclusion of `cwe_refs` on cwe.yaml, but no such edges ship in F-A1):
```yaml
- source:
    taxonomy: cwe
    id: CWE-76
  target:
    taxonomy: cwe
    id: CWE-79
  edge_type: superseded
  confidence: high
  citation: https://cwe.mitre.org/data/definitions/76.html
```

---

## 3. Enum Domains

### `taxonomy` (7 values)

The filename stem of each catalog YAML. Closed enum.

| Value | Catalog YAML | Seed Source |
|-------|--------------|-------------|
| `owasp` | `owasp.yaml` | External curation (6 OWASP lists) |
| `mitre-attack` | `mitre-attack.yaml` | 11 agent detection-patterns.md (38 unique) |
| `mitre-atlas` | `mitre-atlas.yaml` | 7 agent seed + 5 curated AML.T0058–T0062 |
| `nist-ai-rmf` | `nist-ai-rmf.yaml` | NIST AI 100-1 Tables 1–4 (68 Subcategories) |
| `cwe` | `cwe.yaml` | 41 agent seed + CWE Top 25 2025 |
| `tachi-control-category` | `tachi-control-category.yaml` | `.claude/skills/tachi-control-analysis/references/control-categories.md` |
| `tachi-stride-ai-category` | `tachi-stride-ai-category.yaml` | `.claude/skills/tachi-shared/references/stride-categories-shared.md` |

### `edge_type` (3 values)

| Value | Semantics | F-A1 Scope |
|-------|-----------|------------|
| `primary` | Canonical / most-direct mapping | In scope (≥500 edges at F-A1 merge) |
| `related` | Thematic or partial mapping | Out of F-A1 scope (follow-on Issue) |
| `superseded` | Historical mapping replaced by newer framework item | Out of F-A1 scope (follow-on Issue) |

### `confidence` (3 values)

| Value | Semantics | Example |
|-------|-----------|---------|
| `high` | Published cross-reference (explicit framework-to-framework citation) | OWASP LLM05 explicitly lists CWE-1426 in its published cross-references |
| `medium` | Inferred one-hop (semantic match without explicit listing) | LLM05 relates to CWE-79 via category-semantic match |
| `low` | Two-hop or thematic (curator judgment with citation) | ATT&CK T1190 relates to OWASP API7 via adversary-objective alignment |

**Anti-drift rule** (FR-013): "if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label."

---

## 4. Relationships

### 4.1 Catalog-to-catalog (via crosswalk)

Edges in `crosswalk.yaml` carry arbitrary directional (source, target) pairs across the 7 taxonomies. Same-taxonomy pairs are permitted (e.g., CWE→CWE supersession).

### 4.2 `cwe_refs` (per-record, unidirectional OWASP→CWE only)

Per FR-008, only `owasp.yaml` records carry meaningful `cwe_refs` content (since OWASP is the only external source publishing direct CWE cross-references as part of its Top 10 item definitions). Other catalogs MAY carry empty `[]` lists (except `cwe.yaml` which omits the field entirely per FR-003).

CWE→CWE relationships (e.g., superseded, related) live ONLY in `crosswalk.yaml`, NOT as `cwe_refs` on cwe.yaml records.

### 4.3 NIST Surface B / C verbatim transcription

Per FR-022:
- Every Surface B real-mapping row (27 rows) → 1 crosswalk edge with `source.taxonomy = tachi-control-category` + `target.taxonomy = nist-ai-rmf` + `edge_type = primary` + `confidence = high`
- Every Surface C Overlap row (14 rows) → 1 crosswalk edge with `source.taxonomy = tachi-stride-ai-category` + `target.taxonomy = nist-ai-rmf` + `edge_type = primary` + `confidence = high`
- Total: **41 NIST-derived edges** (spec-time re-count; PRD estimated ~54)

---

## 5. Test Coverage

Every data-model validation rule is covered by at least one pytest assertion in `tests/schemas/test_taxonomy_integrity.py`. Traceability:

| Validation Rule | Test Function | FR Reference |
|-----------------|---------------|--------------|
| 7 catalog YAMLs parse cleanly | `test_framework_yamls_load` | FR-028 |
| Per-record required fields (FR-003) | `test_framework_yamls_load` | FR-028 |
| `id` uniqueness within file | `test_framework_yamls_load` | FR-028 |
| `url` URL-regex OR file-path-resolvable | `test_framework_yamls_load` | FR-028 |
| `crosswalk.yaml` parses cleanly | `test_crosswalk_loads` | FR-029 |
| Per-edge required fields (FR-009) | `test_crosswalk_loads` | FR-029 |
| No duplicate `{source, target, edge_type}` triples | `test_crosswalk_loads` | FR-029 |
| Edge referential integrity (FR-011) | `test_crosswalk_referential_integrity` | FR-030 |
| Enum closure on `taxonomy` / `edge_type` / `confidence` | `test_crosswalk_referential_integrity` | FR-030 |
| Non-empty + resolvable citation | `test_citation_shape` | FR-031 |
| (Optional) record sort-order | `test_records_sorted` | FR-032 |
