"""Tests for F-A2 source_attribution schema extension (Feature 189, schema 1.5).

Covers the three round-trip paths (absent, single-record, multi-record) and
the three validation paths (bad taxonomy, bad relationship, bad id) plus
edge cases per spec FR-011 / FR-012 / FR-013.

User Story coverage:
- US-189-1 (Multi-Framework Citation): test_round_trip_multi_record
- US-189-2 (Parser Round-Trip / backward compat): test_absent_omits_key,
  test_empty_array_preserved
- US-189-3 (Closed-Enum + Referential Integrity): test_invalid_taxonomy_rejected,
  test_invalid_relationship_rejected, test_relationship_defaults_to_primary,
  test_invalid_id_detected, test_fixtures_self_consistent
"""
from pathlib import Path

import sys

# Make scripts/ importable from tests/
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.tachi_parsers import (  # noqa: E402
    ValidationError,
    parse_threats_findings,
    validate_source_attribution,
)

FIXTURES = Path(__file__).parent / "fixtures" / "source_attribution"
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"


def test_round_trip_multi_record():
    """US-189-1 AC-3 / FR-007: three attribution records round-trip in input order."""
    content = (FIXTURES / "valid_multi_record.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 1, "fixture defines exactly one finding (LLM-5)"
    finding = findings[0]
    assert finding["id"] == "LLM-5"
    assert "source_attribution" in finding, \
        "US-189-1 AC-3: source_attribution key MUST be present when Section 9 keys this finding"

    records = finding["source_attribution"]
    assert len(records) == 3, "three attribution records preserved"

    # Input order: owasp/LLM05, cwe/CWE-116, mitre-atlas/AML.T0051
    assert records[0] == {"taxonomy": "owasp", "id": "LLM05", "relationship": "primary"}
    assert records[1] == {"taxonomy": "cwe", "id": "CWE-116", "relationship": "primary"}
    assert records[2] == {"taxonomy": "mitre-atlas", "id": "AML.T0051", "relationship": "primary"}


def test_round_trip_single_record():
    """US-189-3 AC-1 / FR-004: single-record round-trip with default relationship injection."""
    content = (FIXTURES / "valid_single_record.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 1, "fixture defines exactly one finding (S-1)"
    finding = findings[0]
    assert finding["id"] == "S-1"
    assert "source_attribution" in finding

    records = finding["source_attribution"]
    assert len(records) == 1
    # Input omitted relationship; parser MUST inject the default "primary"
    assert records[0] == {"taxonomy": "owasp", "id": "A01", "relationship": "primary"}


def test_absent_omits_key():
    """US-189-2 AC-1 / V6: absent Section 9 => ``source_attribution`` key omitted.

    Fixture has 3 findings, no Section 9 block. Parser MUST NOT inject the
    ``source_attribution`` key on ANY returned finding dict — this is the
    conditional-key precedent from Feature 104 delta_status (ADR-028 Decision 2).
    """
    content = (FIXTURES / "valid_absent.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 3, "fixture defines exactly three findings (S-1, T-2, I-3)"
    for finding in findings:
        assert "source_attribution" not in finding, (
            f"V6 violation: finding {finding['id']!r} gained a source_attribution "
            f"key despite the fixture omitting Section 9. "
            f"Got: {finding.get('source_attribution')!r}"
        )


def test_empty_array_preserved():
    """US-189-2 AC-2 / V6: present-but-empty ``source_attribution: []`` preserved.

    Fixture declares ``D-4: []`` inline under Section 9. Parser MUST emit the
    ``source_attribution`` key with value ``[]`` — semantically distinct from
    the absent-key case (no-claim vs explicit-no-attribution-claimed).
    """
    content = (FIXTURES / "valid_empty_array.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 1
    finding = findings[0]
    assert finding["id"] == "D-4"
    assert "source_attribution" in finding, (
        "V6 violation: explicitly empty D-4 list MUST round-trip as "
        "source_attribution: [] (present key, empty value)"
    )
    assert finding["source_attribution"] == [], (
        f"Empty-array round-trip failed. Got: {finding['source_attribution']!r}"
    )


# =============================================================================
# US-189-3 — Closed-enum + referential-integrity tests
# =============================================================================

def test_invalid_taxonomy_rejected():
    """US-189-3 AC-1 / V1: bad taxonomy raises at parser tier with structured message."""
    import pytest  # local import keeps module import cheap for fast paths
    content = (FIXTURES / "invalid_taxonomy.md").read_text()
    with pytest.raises(ValueError) as excinfo:
        parse_threats_findings(content)
    message = str(excinfo.value)
    assert "T-9" in message, f"Message must name the finding id. Got: {message!r}"
    assert "not-a-real-taxonomy" in message, (
        f"Message must name the bad value. Got: {message!r}"
    )
    # Closed-domain must appear in the error (any-order tolerant)
    for allowed in ("owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"):
        assert allowed in message, (
            f"Message must include closed-domain value {allowed!r}. Got: {message!r}"
        )


def test_invalid_relationship_rejected():
    """US-189-3 AC-2 / V2: bad relationship raises at parser tier with structured message."""
    import pytest
    content = (FIXTURES / "invalid_relationship.md").read_text()
    with pytest.raises(ValueError) as excinfo:
        parse_threats_findings(content)
    message = str(excinfo.value)
    assert "I-7" in message, f"Message must name the finding id. Got: {message!r}"
    assert "fabricated_value" in message, (
        f"Message must name the bad value. Got: {message!r}"
    )
    for allowed in ("primary", "related", "derived"):
        assert allowed in message, (
            f"Message must include closed-domain value {allowed!r}. Got: {message!r}"
        )


def test_relationship_defaults_to_primary():
    """US-189-3 AC-3 / V2 default-injection: absent relationship => 'primary'.

    Re-exercises valid_single_record.md (from T007) at the US-189-3 boundary
    to prove the default-injection contract is uniformly enforced.
    """
    content = (FIXTURES / "valid_single_record.md").read_text()
    findings = parse_threats_findings(content)
    assert len(findings) == 1
    record = findings[0]["source_attribution"][0]
    assert record["relationship"] == "primary", (
        f"Default-injection must supply 'primary' when relationship is absent on input. "
        f"Got: {record['relationship']!r}"
    )


def test_invalid_id_detected():
    """US-189-3 AC-4 / V4: unresolved id surfaces as a ValidationError from the validator.

    Parser-tier enum checks (V1/V2/V3/V5) pass — the record is syntactically
    valid. Only the validator-tier referential-integrity check (V4) detects
    the non-existent catalog id per ADR-028 Decision 5.
    """
    content = (FIXTURES / "invalid_id.md").read_text()
    findings = parse_threats_findings(content)
    assert len(findings) == 1, "parser MUST succeed (V1/V2/V3/V5 all pass)"
    assert findings[0]["source_attribution"] == [
        {"taxonomy": "owasp", "id": "NOT-A-REAL-OWASP-ID", "relationship": "primary"}
    ]

    errors = validate_source_attribution(findings, taxonomy_dir=TAXONOMY_DIR)
    assert len(errors) == 1, f"Expected exactly one ValidationError. Got: {errors!r}"
    err = errors[0]
    assert isinstance(err, ValidationError)
    assert err.finding_id == "E-2"
    assert err.record["id"] == "NOT-A-REAL-OWASP-ID"
    assert err.record["taxonomy"] == "owasp"
    assert err.target_yaml_path.endswith("owasp.yaml"), (
        f"target_yaml_path must point at the owasp catalog. Got: {err.target_yaml_path!r}"
    )


def test_fixtures_self_consistent():
    """FR-013: every valid fixture's attribution records resolve referentially.

    Aggregates all valid fixtures (single, multi, absent, empty-array) and
    asserts the validator returns zero errors — proving that fixture
    authoring did not drift from the live F-A1 catalogs under
    ``schemas/taxonomy/``.
    """
    all_findings = []
    for name in (
        "valid_single_record.md",
        "valid_multi_record.md",
        "valid_absent.md",
        "valid_empty_array.md",
    ):
        content = (FIXTURES / name).read_text()
        all_findings.extend(parse_threats_findings(content))

    errors = validate_source_attribution(all_findings, taxonomy_dir=TAXONOMY_DIR)
    assert errors == [], (
        f"Valid fixtures must not produce validation errors. Got: {errors!r}"
    )
