# Data Model: Coverage Attestation Report Section

**Feature**: 194
**Phase**: 1 — Design & Contracts
**Date**: 2026-04-18

## Scope

F-B introduces no persistent data-model changes. All new entities are **transient aggregator output** flowing from `extract-report-data.py` to the Typst renderer. The persistent contract (Finding → `source_attribution`) is unchanged and owned by F-A2.

---

## Read-Only Input Entities (Existing — F-A1 / F-A2)

### Finding (existing — F-A2)

**Source**: `schemas/finding.yaml` v1.5, parsed by `scripts/tachi_parsers.py::parse_threats_findings` (line 796 stores `source_attribution` on the finding dict when present).

**Relevant fields** (F-B-consumed subset):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | e.g., `S-001`, `T-002`, `AGP-003` |
| `title` | string | yes | Short human-readable title |
| `severity` | enum | yes | `critical` \| `high` \| `medium` \| `low` \| `info` |
| `source_attribution` | list[record] | **optional** (absent when finding cites nothing) | Per-finding citation array (F-A2) |

**Mutation policy**: F-B reads only; no write-back (preserves F-A2 single-source-of-truth).

### Source Attribution Record (existing — F-A2 / ADR-028)

**Source**: nested under `Finding.source_attribution`.

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `taxonomy` | enum (closed, 5-value) | yes | `owasp` \| `mitre-attack` \| `mitre-atlas` \| `nist-ai-rmf` \| `cwe` |
| `id` | string | yes | Framework-native identifier (e.g., `LLM05`, `T1070.001`, `AML.T0051`, `MAP 4.2`, `CWE-1426`) |
| `relationship` | enum (closed, 3-value) | optional (default `primary`) | `primary` \| `related` \| `derived` |

**Referential integrity**: guaranteed by F-A2's post-parse validator (ADR-028 Decision 5) — every `id` resolves to a top-level entry in `schemas/taxonomy/{taxonomy}.yaml`. F-B **trusts** this and does NOT re-validate.

### Framework Catalog Record (existing — F-A1 / ADR-027)

**Source**: top-level entry in `schemas/taxonomy/{framework}.yaml` (one file per external framework).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Framework-native identifier |
| `full_id` | string | yes | Disambiguated form (e.g., `OWASP-LLM05`) |
| `name` | string | yes | Human-readable name |
| `url` | string | yes | Canonical authoritative source URL |
| `cwe_refs` | list[string] | optional | CWE cross-references (OWASP-only population) |

**F-B reads**: only `id` (for classification) and the **count** of top-level records (for `yaml_record_count` denominator). `full_id`, `name`, `url`, `cwe_refs` are not consumed by the coverage-attestation section.

---

## New Transient Entities (F-B Aggregator Output)

### Per-Finding Attribution Row

**Purpose**: One record per finding, emitted by the aggregator and consumed by the Typst per-finding table.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Mirrors `Finding.id` |
| `title` | string | yes | Mirrors `Finding.title` |
| `severity` | string | yes | Mirrors `Finding.severity` (lower-case) |
| `owasp_refs` | list[RefEntry] | yes (may be empty) | 0..N entries with `taxonomy == owasp` |
| `mitre_refs` | list[RefEntry] | yes (may be empty) | 0..N entries with `taxonomy == mitre-attack \| mitre-atlas` (merged column) |
| `nist_refs` | list[RefEntry] | yes (may be empty) | 0..N entries with `taxonomy == nist-ai-rmf` |
| `cwe_refs` | list[RefEntry] | yes (may be empty) | 0..N entries with `taxonomy == cwe` |

**RefEntry** (nested record):

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | For MITRE refs, prefixed by family (e.g., `ATT&CK:T1070.001` vs `ATLAS:AML.T0051`); other taxonomies use raw framework-native ID |
| `relationship` | string | One of `primary` / `related` / `derived` — drives bold-vs-plain rendering |

**Invariants**:

- Every finding in the input list produces exactly one Per-Finding Attribution Row — including findings with absent or empty `source_attribution` (row renders with blank ref cells per FR-006).
- Per-finding row emission order matches the input finding-list order (typically severity-sorted upstream; F-B does not re-sort).
- `mitre_refs` merges both `mitre-attack` and `mitre-atlas` entries; the per-entry `id` prefix disambiguates.

### Per-Framework Aggregate Record

**Purpose**: One record per external framework, emitted by the aggregator and consumed by the Typst per-framework matrix page.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `framework` | enum (closed, 5-value) | yes | `owasp` \| `mitre-attack` \| `mitre-atlas` \| `nist-ai-rmf` \| `cwe` |
| `yaml_record_count` | int | yes | `len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))` — computed once per-run |
| `covered_count` | int | yes | # framework items with ≥1 `primary` attribution across the finding set |
| `partial_count` | int | yes | # framework items with zero `primary` AND ≥1 `related`/`derived` attribution |
| `gap_count` | int | yes | # framework items with zero attributions |
| `coverage_percentage` | string | yes | Format `"X.XX%"` \| `"N/A"` (N/A when `yaml_record_count == 0`) |
| `items` | list[FrameworkItemClassification] | yes | Per-item classification list (for detailed page rendering) |

**Invariants**:

- `covered_count + partial_count + gap_count == yaml_record_count` (partition invariant)
- Exactly 5 Per-Framework Aggregate Records emitted (never more, never fewer) when `has-source-attribution: true`
- `coverage_percentage` uses Covered count ONLY as numerator (FR-008 — primary-only)
- `items` is ordered by framework-native order (preserves YAML iteration order)

### Framework Item Classification

**Purpose**: One record per top-level entry in a framework YAML.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Framework-native ID (mirror of `Framework Catalog Record.id`) |
| `classification` | enum (closed, 3-value) | yes | `covered` \| `partial` \| `gap` |

Classification rule (FR-007):

```
relationship_set = { r.relationship for finding in findings
                                   for r in finding.source_attribution
                                   if r.taxonomy == THIS_FRAMEWORK
                                  and r.id == THIS_ID }

if "primary" in relationship_set:
    classification = "covered"
elif "related" in relationship_set or "derived" in relationship_set:
    classification = "partial"
else:
    classification = "gap"
```

### `has-source-attribution` Boolean

**Purpose**: Single-predicate gate for the entire coverage-attestation section.

**Shape**: Typst `bool` (emitted as `#let has-source-attribution = true` or `false`).

**Computation**:

```
has_source_attribution = any(
    finding.source_attribution is not None and len(finding.source_attribution) > 0
    for finding in findings
)
```

**Invariant**: The boolean is `true` iff ≥1 finding carries a non-empty `source_attribution` array. No implicit defaults that would silently invert the gate (SC-003).

---

## Data-Flow Sequence

```
(1) parse_threats_findings(threats.md) → finding list (F-A2 contract)
(2) has_source_attribution = scan_findings(finding_list) → bool
(3) if has_source_attribution:
      for framework in [owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe]:
        yaml_records = yaml.safe_load(schemas/taxonomy/{framework}.yaml)
        yaml_record_count = len(yaml_records)
        per_framework_aggregate = classify_records(yaml_records, finding_list, framework)
      per_finding_rows = build_per_finding_rows(finding_list)
(4) emit Typst data contract:
      #let has-source-attribution = {has_source_attribution}
      #let per-finding-rows = {per_finding_rows}
      #let per-framework-aggregates = {per_framework_aggregates}
(5) main.typ conditionally renders coverage-attestation-page(...)
```

---

## Edge Cases & Invariants

| Edge | Aggregator Behavior |
|------|---------------------|
| `has_source_attribution == false` | Emit `has-source-attribution: false`; omit per-finding rows and per-framework aggregates from Typst contract (or emit empty arrays — Typst gate + `.len() > 0` check both fire) |
| `yaml.safe_load` raises on a framework YAML | Aggregator fails loud with clear error (ADR-022); surfaces framework name + file path + underlying YAML error |
| Framework YAML with 0 top-level records | `yaml_record_count: 0`, `covered_count: 0`, `partial_count: 0`, `gap_count: 0`, `coverage_percentage: "N/A"` |
| Framework YAML with N records, 0 matching findings | `yaml_record_count: N`, `covered_count: 0`, `partial_count: 0`, `gap_count: N`, `coverage_percentage: "0.00%"` |
| Finding with `source_attribution` field present but empty array (`[]`) | Counts as "no attribution" — row renders with blank ref cells; does NOT flip `has_source_attribution` |
| Finding citing `id` that doesn't resolve in YAML | Treated as normal citation for classification purposes (F-A2 validator catches the validity upstream); F-B does NOT re-check |

---

## Validation Rules

1. **Closed-enum validation** — All `taxonomy` values in `source_attribution` MUST be in `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` (F-A2-enforced upstream; F-B does NOT re-check).
2. **Partition invariant** — `covered_count + partial_count + gap_count == yaml_record_count` for every Per-Framework Aggregate Record (aggregator post-condition, asserted in unit tests).
3. **Exactly-5 invariant** — Exactly 5 Per-Framework Aggregate Records emitted when `has-source-attribution: true` (framework-count invariant, asserted in unit tests).
4. **Order-preservation** — Per-Finding Attribution Row list preserves input finding order (no re-sort).
5. **Primary-only numerator** — `coverage_percentage` uses Covered count as numerator (FR-008 — Partial never blended in).

---

## Traceability to Spec FRs

| Entity / Field | Spec FR |
|----------------|---------|
| `has-source-attribution` boolean | FR-002, FR-003, FR-004, SC-003, SC-004 |
| Per-Finding Attribution Row | FR-005, FR-006 |
| RefEntry `relationship` (bold vs. plain) | FR-006 |
| MITRE column merge (ATT&CK + ATLAS with prefix) | FR-005 |
| Per-Framework Aggregate Record | FR-007, FR-008, FR-009 |
| `coverage_percentage` format `"N/A"` on zero-denominator | FR-011(a) |
| `coverage_percentage` format `"0.00%"` on zero-numerator | FR-011(b) |
| Aggregator fail-loud on malformed YAML | FR-011(c) |
| Framework Item Classification enum (3-value) | FR-007, FR-019 (no 4th value) |
| External-frameworks-only (no internal taxonomies rendered) | FR-018 |
