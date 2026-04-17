"""Referential integrity tests for ``schemas/taxonomy/``."""

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"

CATALOG_FILENAMES = [
    "owasp.yaml",
    "mitre-attack.yaml",
    "mitre-atlas.yaml",
    "nist-ai-rmf.yaml",
    "cwe.yaml",
    "tachi-control-category.yaml",
    "tachi-stride-ai-category.yaml",
]

TAXONOMY_ENUM = {
    "owasp",
    "mitre-attack",
    "mitre-atlas",
    "nist-ai-rmf",
    "cwe",
    "tachi-control-category",
    "tachi-stride-ai-category",
}

EDGE_TYPE_ENUM = {"primary", "related", "superseded"}

CONFIDENCE_ENUM = {"high", "medium", "low"}

REQUIRED_RECORD_KEYS = {"id", "full_id", "name", "url"}

REQUIRED_EDGE_KEYS = {"source", "target", "edge_type", "confidence", "citation"}

REQUIRED_ENDPOINT_KEYS = {"taxonomy", "id"}

URL_REGEX = re.compile(r"^https?://")

CWE_REF_REGEX = re.compile(r"^CWE-\d+$")

PRIMARY_EDGE_FLOOR = 500


def _is_url_or_existing_file(value: str) -> bool:
    """Return True if *value* is URL-shaped OR resolves to a repo file.

    Performs NO HTTP fetch — URL validation is regex-only per ADR-021
    determinism constraint.
    """
    if not isinstance(value, str) or not value:
        return False
    if URL_REGEX.match(value):
        return True
    return (REPO_ROOT / value).is_file()


def _sort_key_nist(record_id: str):
    """Numeric-within-function sort key so ``MEASURE 2.2`` precedes ``MEASURE 2.10``.

    Parses ``MEASURE 2.10`` into ``('MEASURE', 2, 10)``. Pure lexicographic
    sort would emit ``MEASURE 2.10`` before ``MEASURE 2.2``, breaking the NIST
    publication ordering.
    """
    function_part, _, number_part = record_id.partition(" ")
    major_str, _, minor_str = number_part.partition(".")
    try:
        major = int(major_str)
        minor = int(minor_str) if minor_str else 0
    except ValueError:  # malformed — fall back to string sort for stability
        return (function_part, 0, 0, record_id)
    return (function_part, major, minor)


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
    """Build ``{taxonomy_stem: set(id)}`` for O(1) referential integrity checks."""
    index = {}
    for filename, records in catalogs.items():
        stem = Path(filename).stem
        index[stem] = {record["id"] for record in records}
    return index


def test_framework_yamls_load(catalogs):
    """Each catalog YAML parses; every record has required fields; ids unique; urls valid."""
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

            if filename == "cwe.yaml":
                assert "cwe_refs" not in record, (
                    f"{filename}: record {index} (id={record['id']!r}) MUST NOT "
                    f"carry cwe_refs (CWE->CWE relations belong in crosswalk.yaml)"
                )
            else:
                assert "cwe_refs" in record, (
                    f"{filename}: record {index} (id={record['id']!r}) missing "
                    f"required field 'cwe_refs' (only cwe.yaml omits it)"
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

            record_id = record["id"]
            assert record_id not in seen_ids, (
                f"{filename}: duplicate id {record_id!r} at record index {index}"
            )
            seen_ids.add(record_id)

            url = record["url"]
            assert _is_url_or_existing_file(url), (
                f"{filename}: record {record_id!r}: url {url!r} is neither "
                f"URL-shaped (^https?://) nor an existing repo file path"
            )


def test_crosswalk_loads(crosswalk):
    """crosswalk.yaml parses; edges have required fields; no duplicates; primary-edge floor met."""
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
            f"{sorted(extras)} (schema forbids extras)"
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

    primary_count = sum(1 for edge in crosswalk if edge["edge_type"] == "primary")
    assert primary_count >= PRIMARY_EDGE_FLOOR, (
        f"crosswalk.yaml: {primary_count} primary edges below floor "
        f"of {PRIMARY_EDGE_FLOOR}"
    )


def test_crosswalk_referential_integrity(crosswalk, catalog_id_index):
    """Every edge's source/target resolves in its catalog; every enum value is closed."""
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


def test_citation_shape(crosswalk):
    """Every citation is non-empty and is URL-shaped OR resolves to a repo file (no HTTP fetches)."""
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


def test_records_sorted(catalogs):
    """nist-ai-rmf uses numeric-within-function sort; others use lexicographic id sort."""
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
