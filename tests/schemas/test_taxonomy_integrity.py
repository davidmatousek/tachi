"""Referential integrity tests for ``schemas/taxonomy/`` (Feature 180 F-A1).

Authors the 4 mandatory + 1 optional pytest test functions specified in
``specs/180-taxonomy-crosswalk-collection/contracts/integrity-test-contract.md``
and enumerated in ``spec.md`` FR-027 through FR-032.

Offline-deterministic per ADR-021: no HTTP fetches, no external subprocesses.
All assertions operate on committed ``schemas/taxonomy/*.yaml`` files via
``yaml.safe_load``; citation shape is validated with a URL regex and
filesystem ``Path.is_file()`` checks only.

Stdlib + pyyaml only. Both are declared in ``requirements-dev.txt`` per
FR-037 / Feature 128 pytest bootstrap.
"""

import re
from pathlib import Path

import pytest
import yaml


# tests/schemas/test_taxonomy_integrity.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"

# The 7 per-framework catalog YAMLs (FR-001 enumerates 9 files; crosswalk.yaml
# is tested separately in FR-029; README.md is not a YAML).
CATALOG_FILENAMES = [
    "owasp.yaml",
    "mitre-attack.yaml",
    "mitre-atlas.yaml",
    "nist-ai-rmf.yaml",
    "cwe.yaml",
    "tachi-control-category.yaml",
    "tachi-stride-ai-category.yaml",
]

# FR-010 closed 7-value taxonomy enum (matches the filename stems above).
TAXONOMY_ENUM = {
    "owasp",
    "mitre-attack",
    "mitre-atlas",
    "nist-ai-rmf",
    "cwe",
    "tachi-control-category",
    "tachi-stride-ai-category",
}

# FR-012 closed 3-value edge_type enum.
EDGE_TYPE_ENUM = {"primary", "related", "superseded"}

# FR-013 closed 3-value confidence enum.
CONFIDENCE_ENUM = {"high", "medium", "low"}

# FR-003 required keys on every catalog record.
REQUIRED_RECORD_KEYS = {"id", "full_id", "name", "url"}

# FR-009 top-level required keys on every crosswalk edge.
REQUIRED_EDGE_KEYS = {"source", "target", "edge_type", "confidence", "citation"}

# FR-009 required sub-keys on source / target dicts.
REQUIRED_ENDPOINT_KEYS = {"taxonomy", "id"}

# URL regex per contract (URL-shaped OR file-path-resolvable).
URL_REGEX = re.compile(r"^https?://")

# FR-003 `cwe_refs` item format.
CWE_REF_REGEX = re.compile(r"^CWE-\d+$")

# FR-025 primary-edge floor.
PRIMARY_EDGE_FLOOR = 500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_url_or_existing_file(value: str) -> bool:
    """Return True if *value* is URL-shaped OR resolves to a repo file.

    Performs NO HTTP fetch — URL validation is regex-only per FR-031 / ADR-021
    determinism constraint.
    """
    if not isinstance(value, str) or not value:
        return False
    if URL_REGEX.match(value):
        return True
    return (REPO_ROOT / value).is_file()


def _sort_key_nist(record_id: str):
    """Sort key for ``nist-ai-rmf.yaml`` per FR-032 numeric-within-function.

    Parses an ID like ``MEASURE 2.10`` into ``('MEASURE', 2, 10)`` so that
    ``MEASURE 2.2`` precedes ``MEASURE 2.10`` (numeric ordering matches NIST
    publication convention). First tuple element is the function name
    ('GOVERN', 'MAP', 'MEASURE', 'MANAGE') in alphabetical order; the next
    two are the parsed X and Y numeric components.

    Architect decision at T027: numeric-within-function is canonical for NIST
    per ``.aod/results/architect.md`` §5.3 — pure lexicographic sort would
    emit ``MEASURE 2.10`` before ``MEASURE 2.2`` which breaks the publication
    ordering convention and the human-readable navigation expectation.
    """
    function_part, _, number_part = record_id.partition(" ")
    major_str, _, minor_str = number_part.partition(".")
    try:
        major = int(major_str)
        minor = int(minor_str) if minor_str else 0
    except ValueError:  # malformed — fall back to string sort for stability
        return (function_part, 0, 0, record_id)
    return (function_part, major, minor)


# ---------------------------------------------------------------------------
# Module-scoped loaders — parse each YAML exactly once per test session
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def catalogs():
    """Load all 7 catalog YAMLs once. Returns ``{filename: parsed_list}``."""
    loaded = {}
    for name in CATALOG_FILENAMES:
        path = TAXONOMY_DIR / name
        assert path.exists(), f"Missing catalog YAML: {path}"
        with open(path, encoding="utf-8") as handle:
            loaded[name] = yaml.safe_load(handle)
    return loaded


@pytest.fixture(scope="module")
def crosswalk():
    """Load ``crosswalk.yaml`` once per session."""
    path = TAXONOMY_DIR / "crosswalk.yaml"
    assert path.exists(), f"Missing crosswalk.yaml: {path}"
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@pytest.fixture(scope="module")
def catalog_id_index(catalogs):
    """Build ``{taxonomy_stem: set(id)}`` for O(1) referential integrity checks.

    Taxonomy stems are derived from the catalog filename (e.g. ``owasp.yaml``
    -> ``owasp``). Matches the FR-010 7-value taxonomy enum values.
    """
    index = {}
    for filename, records in catalogs.items():
        stem = filename[: -len(".yaml")]
        index[stem] = {record["id"] for record in records}
    return index


# ---------------------------------------------------------------------------
# FR-028 — test_framework_yamls_load
# ---------------------------------------------------------------------------


def test_framework_yamls_load(catalogs):
    """Each of the 7 catalog YAMLs parses; every record has FR-003 required fields.

    Per spec FR-028 and integrity-test-contract §1:
      1. Each YAML parses via ``yaml.safe_load`` without exception (handled by
         the ``catalogs`` fixture — any parse failure fails this test).
      2. Each parsed structure is a non-empty list.
      3. Each record is a dict with required keys ``{id, full_id, name, url}``.
      4. All catalogs EXCEPT ``cwe.yaml`` carry ``cwe_refs`` on every record;
         ``cwe_refs`` values are lists of strings matching ``^CWE-\\d+$``.
      5. ``cwe.yaml`` records MUST NOT carry ``cwe_refs`` (FR-003 explicit
         omission — CWE->CWE relations live in ``crosswalk.yaml``).
      6. ``id`` is unique within each catalog file.
      7. ``url`` is URL-shaped OR resolves to a repo-root file.
    """
    for filename, records in catalogs.items():
        assert isinstance(records, list), (
            f"{filename}: expected list, got {type(records).__name__}"
        )
        assert records, f"{filename}: parsed structure is empty"

        seen_ids = set()
        for index, record in enumerate(records):
            assert isinstance(record, dict), (
                f"{filename}: record {index} is {type(record).__name__}, expected dict"
            )

            missing = REQUIRED_RECORD_KEYS - set(record.keys())
            assert not missing, (
                f"{filename}: record {index} (id={record.get('id', '<none>')!r}) "
                f"missing required fields {sorted(missing)}"
            )

            # cwe_refs presence rules (FR-003).
            if filename == "cwe.yaml":
                assert "cwe_refs" not in record, (
                    f"{filename}: record {index} (id={record['id']!r}) MUST NOT "
                    f"carry cwe_refs per FR-003 (CWE->CWE relations belong in crosswalk.yaml)"
                )
            else:
                assert "cwe_refs" in record, (
                    f"{filename}: record {index} (id={record['id']!r}) missing "
                    f"required field 'cwe_refs' (per FR-003; only cwe.yaml omits it)"
                )
                cwe_refs = record["cwe_refs"]
                assert isinstance(cwe_refs, list), (
                    f"{filename}: record {record['id']!r}: cwe_refs is "
                    f"{type(cwe_refs).__name__}, expected list"
                )
                for ref in cwe_refs:
                    assert isinstance(ref, str) and CWE_REF_REGEX.match(ref), (
                        f"{filename}: record {record['id']!r}: cwe_refs entry "
                        f"{ref!r} does not match ^CWE-\\d+$"
                    )

            # FR-004 id uniqueness within each catalog file.
            record_id = record["id"]
            assert record_id not in seen_ids, (
                f"{filename}: duplicate id {record_id!r} at record index {index}"
            )
            seen_ids.add(record_id)

            # FR-007 url shape: URL-regex OR existing repo file.
            url = record["url"]
            assert _is_url_or_existing_file(url), (
                f"{filename}: record {record_id!r}: url {url!r} is neither "
                f"URL-shaped (^https?://) nor an existing repo file path"
            )


# ---------------------------------------------------------------------------
# FR-029 — test_crosswalk_loads
# ---------------------------------------------------------------------------


def test_crosswalk_loads(crosswalk):
    """crosswalk.yaml parses; every edge has FR-009 required fields; no duplicates.

    Per spec FR-029 and integrity-test-contract §2:
      1. ``crosswalk.yaml`` parses via ``yaml.safe_load`` without exception
         (handled by the ``crosswalk`` fixture).
      2. Parsed structure is a list of dicts.
      3. Each dict has exactly the top-level keys
         ``{source, target, edge_type, confidence, citation}`` (no extras).
      4. ``source`` and ``target`` are dicts with exactly ``{taxonomy, id}``.
      5. No two edges share the same
         ``(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)``
         5-tuple — duplicate edges fail the test.
      6. FR-025 primary-edge floor: ``len(edge_type=='primary') >= 500``.
    """
    assert isinstance(crosswalk, list), (
        f"crosswalk.yaml: expected list, got {type(crosswalk).__name__}"
    )
    assert crosswalk, "crosswalk.yaml: parsed structure is empty"

    seen_edge_keys = {}
    for index, edge in enumerate(crosswalk):
        assert isinstance(edge, dict), (
            f"crosswalk.yaml: edge {index} is {type(edge).__name__}, expected dict"
        )

        actual_keys = set(edge.keys())
        missing = REQUIRED_EDGE_KEYS - actual_keys
        extras = actual_keys - REQUIRED_EDGE_KEYS
        assert not missing, (
            f"crosswalk.yaml: edge {index} missing required fields {sorted(missing)}"
        )
        assert not extras, (
            f"crosswalk.yaml: edge {index} has unexpected extra fields "
            f"{sorted(extras)} (FR-009 forbids extras)"
        )

        for endpoint_name in ("source", "target"):
            endpoint = edge[endpoint_name]
            assert isinstance(endpoint, dict), (
                f"crosswalk.yaml: edge {index}: {endpoint_name} is "
                f"{type(endpoint).__name__}, expected dict"
            )
            endpoint_keys = set(endpoint.keys())
            missing_ep = REQUIRED_ENDPOINT_KEYS - endpoint_keys
            extras_ep = endpoint_keys - REQUIRED_ENDPOINT_KEYS
            assert not missing_ep, (
                f"crosswalk.yaml: edge {index}: {endpoint_name} missing "
                f"required fields {sorted(missing_ep)}"
            )
            assert not extras_ep, (
                f"crosswalk.yaml: edge {index}: {endpoint_name} has unexpected "
                f"extra fields {sorted(extras_ep)}"
            )

        dedupe_key = (
            edge["source"]["taxonomy"],
            edge["source"]["id"],
            edge["target"]["taxonomy"],
            edge["target"]["id"],
            edge["edge_type"],
        )
        if dedupe_key in seen_edge_keys:
            prior = seen_edge_keys[dedupe_key]
            raise AssertionError(
                f"crosswalk.yaml: duplicate edge at indices {prior},{index} — "
                f"{dedupe_key}"
            )
        seen_edge_keys[dedupe_key] = index

    # FR-025 primary-edge floor.
    primary_count = sum(1 for edge in crosswalk if edge["edge_type"] == "primary")
    assert primary_count >= PRIMARY_EDGE_FLOOR, (
        f"crosswalk.yaml: {primary_count} primary edges below FR-025 floor "
        f"of {PRIMARY_EDGE_FLOOR}"
    )


# ---------------------------------------------------------------------------
# FR-030 — test_crosswalk_referential_integrity
# ---------------------------------------------------------------------------


def test_crosswalk_referential_integrity(crosswalk, catalog_id_index):
    """Every edge's source/target resolves; every enum value is in its closed domain.

    Per spec FR-030 and integrity-test-contract §3:
      1. ``source.taxonomy`` ∈ 7-value enum.
      2. ``target.taxonomy`` ∈ 7-value enum.
      3. ``source.id`` resolves in the catalog named by ``source.taxonomy``.
      4. ``target.id`` resolves in the catalog named by ``target.taxonomy``.
      5. ``edge_type`` ∈ ``{primary, related, superseded}``.
      6. ``confidence`` ∈ ``{high, medium, low}``.

    Note (2026-04-17 T028): this test is EXPECTED TO FAIL at T028 commit time
    because 38 pre-existing drifted edges (22 Surface B dash-format + 16
    Surface C semantically incorrect targets) reference IDs absent from the
    canonical catalog records. T029 resolves the drift by removing those
    edges per architect's Option (c) decision at `.aod/results/architect.md`.
    The test is CORRECT; the data has drift the test is designed to catch.
    """
    for index, edge in enumerate(crosswalk):
        source_tax = edge["source"]["taxonomy"]
        target_tax = edge["target"]["taxonomy"]
        source_id = edge["source"]["id"]
        target_id = edge["target"]["id"]
        edge_type = edge["edge_type"]
        confidence = edge["confidence"]

        assert source_tax in TAXONOMY_ENUM, (
            f"crosswalk.yaml: edge {index}: source.taxonomy={source_tax!r} "
            f"not in 7-value enum {sorted(TAXONOMY_ENUM)}"
        )
        assert target_tax in TAXONOMY_ENUM, (
            f"crosswalk.yaml: edge {index}: target.taxonomy={target_tax!r} "
            f"not in 7-value enum {sorted(TAXONOMY_ENUM)}"
        )
        assert edge_type in EDGE_TYPE_ENUM, (
            f"crosswalk.yaml: edge {index}: edge_type={edge_type!r} "
            f"not in {sorted(EDGE_TYPE_ENUM)}"
        )
        assert confidence in CONFIDENCE_ENUM, (
            f"crosswalk.yaml: edge {index}: confidence={confidence!r} "
            f"not in {sorted(CONFIDENCE_ENUM)}"
        )

        # Referential integrity: source.id must exist in catalog_id_index[source_tax].
        assert source_id in catalog_id_index[source_tax], (
            f"crosswalk.yaml: edge {index}: source.id={source_id!r} not found "
            f"in {source_tax}.yaml "
            f"(source={edge['source']}, target={edge['target']}, edge_type={edge_type})"
        )
        assert target_id in catalog_id_index[target_tax], (
            f"crosswalk.yaml: edge {index}: target.id={target_id!r} not found "
            f"in {target_tax}.yaml "
            f"(source={edge['source']}, target={edge['target']}, edge_type={edge_type})"
        )


# ---------------------------------------------------------------------------
# FR-031 — test_citation_shape
# ---------------------------------------------------------------------------


def test_citation_shape(crosswalk):
    """Every citation is non-empty AND (URL-regex OR existing repo file).

    Per spec FR-031 and integrity-test-contract §4:
      1. ``citation`` is a non-empty string for every edge.
      2. Each citation matches ``^https?://`` OR resolves to an existing repo
         file path.
      3. NO HTTP fetches are performed at test time (ADR-021 determinism).
    """
    for index, edge in enumerate(crosswalk):
        citation = edge["citation"]
        assert isinstance(citation, str) and citation, (
            f"crosswalk.yaml: edge {index}: citation is empty or non-string "
            f"(value={citation!r})"
        )

        if URL_REGEX.match(citation):
            continue

        candidate_path = REPO_ROOT / citation
        assert candidate_path.is_file(), (
            f"crosswalk.yaml: edge {index}: citation={citation!r} is neither "
            f"URL-shaped (^https?://) nor an existing repo file at "
            f"{candidate_path}"
        )


# ---------------------------------------------------------------------------
# FR-032 — test_records_sorted (optional per architect directive)
# ---------------------------------------------------------------------------


def test_records_sorted(catalogs):
    """Each catalog is sorted per FR-032 conventions.

    Per spec FR-032 amendment (2026-04-17, architect T027):
      - ``nist-ai-rmf.yaml``: sort key is ``(function, X_int, Y_int)`` where
        function ∈ {GOVERN, MAP, MEASURE, MANAGE} (alphabetical) and ``X.Y``
        is the dotted numeric component parsed as a 2-tuple of ints. This
        matches the NIST publication convention where ``MEASURE 2.2``
        precedes ``MEASURE 2.10`` (numeric-within-function).
      - Other 6 catalogs: lexicographic sort on the ``id`` field.

    Fails with the first divergence point (name of file + index + id).
    """
    for filename, records in catalogs.items():
        ids = [record["id"] for record in records]

        if filename == "nist-ai-rmf.yaml":
            expected = sorted(ids, key=_sort_key_nist)
        else:
            expected = sorted(ids)

        for index, (actual_id, expected_id) in enumerate(zip(ids, expected)):
            assert actual_id == expected_id, (
                f"{filename}: record at index {index} has id {actual_id!r} "
                f"which is out of sort order (expected {expected_id!r}). "
                f"Full actual prefix: {ids[:index + 1]!r}; "
                f"expected prefix: {expected[:index + 1]!r}"
            )
