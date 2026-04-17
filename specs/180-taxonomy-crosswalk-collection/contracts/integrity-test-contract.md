# Contract: Integrity Test Functions (tests/schemas/test_taxonomy_integrity.py)

**Feature**: 180-taxonomy-crosswalk-collection
**Phase**: 1 — Design & Contracts
**Source**: [spec.md](../spec.md) FR-027 through FR-032 and [data-model.md](../data-model.md) §5

This contract specifies the **4 mandatory + 1 optional** pytest test function signatures. Implementation authors compile to these contracts.

---

## Mandatory test 1: `test_framework_yamls_load()`

**Source**: spec.md FR-028
**Purpose**: Assert that each catalog YAML parses cleanly, every record has required fields, and every `url` field is URL-shaped or file-path-resolvable.

**Signature**:
```python
def test_framework_yamls_load():
    """Each of the 7 catalog YAMLs parses; every record has FR-003 required fields."""
```

**Assertions**:
1. Each of the 7 catalog YAMLs (`owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`, `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`) parses via `yaml.safe_load` WITHOUT exception.
2. Each parsed structure is a list.
3. Each record is a dict with required keys `{id, full_id, name, url}`.
4. For all 7 catalogs EXCEPT `cwe.yaml`: each record has `cwe_refs` key; its value is a list of strings matching `^CWE-\d+$`.
5. For `cwe.yaml`: each record MUST NOT have a `cwe_refs` key (FR-003).
6. For each catalog: the `id` field is unique across all records within that file.
7. For each record: `url` MUST EITHER match URL-regex `^https?://` OR resolve to an existing file path relative to repo root.

**Failure message template**:
```
AssertionError: {filename}: record {id_or_index} missing required field {field} (or duplicate id / invalid url)
```

---

## Mandatory test 2: `test_crosswalk_loads()`

**Source**: spec.md FR-029
**Purpose**: Assert `crosswalk.yaml` parses cleanly, every edge has required fields, no duplicate edges.

**Signature**:
```python
def test_crosswalk_loads():
    """crosswalk.yaml parses; every edge has FR-009 required fields; no duplicate edges."""
```

**Assertions**:
1. `schemas/taxonomy/crosswalk.yaml` parses via `yaml.safe_load` WITHOUT exception.
2. Parsed structure is a list of dicts.
3. Each dict has top-level keys `{source, target, edge_type, confidence, citation}` (exactly; no extras).
4. Each `source` and `target` is a dict with keys `{taxonomy, id}` (exactly; no extras).
5. No two edges share the same `{source, target, edge_type}` 3-tuple (where `source` and `target` are dict-equality compared on their `{taxonomy, id}` keys — equivalent to a 5-tuple `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` comparison). Uniqueness constraint — duplicate edges fail the test.

**Failure message template**:
```
AssertionError: crosswalk.yaml: edge {index} missing required field {field} (or duplicate edge at index {a},{b})
```

---

## Mandatory test 3: `test_crosswalk_referential_integrity()`

**Source**: spec.md FR-030
**Purpose**: Assert every edge's source / target resolves to a record in the named catalog YAML; all enum values are in closed domains.

**Signature**:
```python
def test_crosswalk_referential_integrity():
    """Every edge's source.id and target.id resolve; every enum value is in its closed domain."""
```

**Assertions**:
1. `source.taxonomy` ∈ `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category}` (7-value closed enum).
2. `target.taxonomy` ∈ the same 7-value enum.
3. `source.id` is an `id` present in the catalog YAML whose filename stem matches `source.taxonomy`.
4. `target.id` is an `id` present in the catalog YAML whose filename stem matches `target.taxonomy`.
5. `edge_type` ∈ `{primary, related, superseded}` (3-value closed enum).
6. `confidence` ∈ `{high, medium, low}` (3-value closed enum).

**Implementation note**: load all 7 catalog YAMLs once at test-setup time; build an `{taxonomy: set(ids)}` mapping; check each edge against this mapping.

**Failure message template**:
```
AssertionError: crosswalk.yaml: edge {index}: {field}='{value}' — {reason, e.g., "not in taxonomy enum" / "id 'X' not found in {catalog}.yaml" / "not in edge_type enum"}
```

---

## Mandatory test 4: `test_citation_shape()`

**Source**: spec.md FR-031
**Purpose**: Assert every `citation` is non-empty and is either URL-shaped or an existing repo file path.

**Signature**:
```python
def test_citation_shape():
    """Every citation is non-empty; URL-regex OR existing-file-path."""
```

**Assertions**:
1. `citation` is a non-empty string for every edge.
2. Each `citation` matches URL-regex `^https?://` OR resolves to an existing file path relative to repo root.
3. NO HTTP fetches are performed at test time (preserves ADR-021 determinism — test is offline-deterministic).

**Implementation note**: use `re.match` for URL check + `pathlib.Path(repo_root / citation).is_file()` for file-path check. Do NOT use `urllib.request` or similar.

**Failure message template**:
```
AssertionError: crosswalk.yaml: edge {index}: citation='{value}' — empty / not URL-shaped / file not found at {repo_root / value}
```

---

## Optional test 5: `test_records_sorted()`

**Source**: spec.md FR-032
**Purpose**: Assert stable record ordering (alphabetical by `id` within catalog YAMLs; lexicographic on 4-tuple for crosswalk edges).

**Signature**:
```python
def test_records_sorted():
    """Records are sorted by id; crosswalk edges sorted by (source.taxonomy, source.id, target.taxonomy, target.id)."""
```

**Assertions**:
1. For each of the 7 catalog YAMLs: records appear in ascending order of `id` (using Python `sorted()` ordering).
2. For `crosswalk.yaml`: edges appear in ascending lexicographic order of `(source.taxonomy, source.id, target.taxonomy, target.id)`.

**Status**: Optional per Architect NFR-3 recommendation. A failing sort assertion fails the full suite. Test authors MAY add if time permits; SHOULD NOT skip if the optional test is feasible within Phase 4 budget.

**Failure message template**:
```
AssertionError: {filename}: record at index {i} has id '{id}' which is out of sort order (expected >= '{prev_id}')
```

---

## Test fixture strategy

- **YAML loading**: use module-scoped pytest fixtures to load each YAML once per test run (avoid repeated parse).
- **Repo-root resolution**: use a session-scoped fixture that computes `pathlib.Path(__file__).parent.parent.parent` to locate repo root (same pattern as `tests/scripts/conftest.py` per Feature 128 bootstrap).
- **No external fixtures**: all tests operate on committed `schemas/taxonomy/*.yaml` files; no test-specific fixture YAMLs.

## Failure-mode edge case (from spec.md US-180-4 scenario 6)

A deliberately-corrupted fixture is NOT included in F-A1; the acceptance scenario is satisfied by the inherent failure behavior of the mandatory tests — e.g., commit an edge with `edge_type: invalid` and the suite fails `test_crosswalk_referential_integrity` with a clear assertion message. No dedicated corruption fixture is needed.
