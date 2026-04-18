"""Tests for the source_attribution schema extension.

Covers round-trip paths (absent, single, multi, empty), closed-enum rejection
(taxonomy, relationship, id), and referential integrity against F-A1 catalogs.
"""
import sys
from pathlib import Path

import pytest

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
    """Three attribution records round-trip in input order."""
    content = (FIXTURES / "valid_multi_record.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 1
    finding = findings[0]
    assert finding["id"] == "LLM-5"
    assert "source_attribution" in finding

    records = finding["source_attribution"]
    assert len(records) == 3
    assert records[0] == {"taxonomy": "owasp", "id": "LLM05", "relationship": "primary"}
    assert records[1] == {"taxonomy": "cwe", "id": "CWE-116", "relationship": "primary"}
    assert records[2] == {"taxonomy": "mitre-atlas", "id": "AML.T0051", "relationship": "primary"}


def test_round_trip_single_record():
    """Single-record round-trip injects the default relationship 'primary'."""
    content = (FIXTURES / "valid_single_record.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 1
    finding = findings[0]
    assert finding["id"] == "S-1"
    # Input omitted relationship; parser injects the default.
    assert finding["source_attribution"] == [
        {"taxonomy": "owasp", "id": "A01", "relationship": "primary"}
    ]


def test_absent_omits_key():
    """Absent Section 9 => ``source_attribution`` key omitted from every finding.

    Distinct from the empty-array case below: absent means "no claim", while
    an explicit ``[]`` means "explicitly no attribution claimed".
    """
    content = (FIXTURES / "valid_absent.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 3
    for finding in findings:
        assert "source_attribution" not in finding, (
            f"finding {finding['id']!r} gained a source_attribution key "
            f"despite the fixture omitting Section 9"
        )


def test_empty_array_preserved():
    """Present-but-empty ``D-4: []`` round-trips with the key present and value []."""
    content = (FIXTURES / "valid_empty_array.md").read_text()
    findings = parse_threats_findings(content)

    assert len(findings) == 1
    finding = findings[0]
    assert finding["id"] == "D-4"
    assert finding["source_attribution"] == []


def test_invalid_taxonomy_rejected():
    """Bad taxonomy raises with a message naming the finding, the bad value, and the closed domain."""
    content = (FIXTURES / "invalid_taxonomy.md").read_text()
    with pytest.raises(ValueError) as excinfo:
        parse_threats_findings(content)
    message = str(excinfo.value)
    assert "T-9" in message
    assert "not-a-real-taxonomy" in message
    for allowed in ("owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"):
        assert allowed in message


def test_invalid_relationship_rejected():
    """Bad relationship raises with a message naming the finding, the bad value, and the closed domain."""
    content = (FIXTURES / "invalid_relationship.md").read_text()
    with pytest.raises(ValueError) as excinfo:
        parse_threats_findings(content)
    message = str(excinfo.value)
    assert "I-7" in message
    assert "fabricated_value" in message
    for allowed in ("primary", "related", "derived"):
        assert allowed in message


def test_relationship_defaults_to_primary():
    """Absent relationship defaults to 'primary' during parse."""
    content = (FIXTURES / "valid_single_record.md").read_text()
    findings = parse_threats_findings(content)
    assert findings[0]["source_attribution"][0]["relationship"] == "primary"


def test_invalid_id_detected():
    """Syntactically valid but unresolvable id surfaces only at the validator tier."""
    content = (FIXTURES / "invalid_id.md").read_text()
    findings = parse_threats_findings(content)
    assert findings[0]["source_attribution"] == [
        {"taxonomy": "owasp", "id": "NOT-A-REAL-OWASP-ID", "relationship": "primary"}
    ]

    errors = validate_source_attribution(findings, taxonomy_dir=TAXONOMY_DIR)
    assert len(errors) == 1
    err = errors[0]
    assert isinstance(err, ValidationError)
    assert err.finding_id == "E-2"
    assert err.record == {"taxonomy": "owasp", "id": "NOT-A-REAL-OWASP-ID", "relationship": "primary"}
    assert err.target_yaml_path.endswith("owasp.yaml")


def test_fixtures_self_consistent():
    """Every valid fixture's attribution records resolve against the live catalogs."""
    all_findings = []
    for name in (
        "valid_single_record.md",
        "valid_multi_record.md",
        "valid_absent.md",
        "valid_empty_array.md",
    ):
        content = (FIXTURES / name).read_text()
        all_findings.extend(parse_threats_findings(content))

    assert validate_source_attribution(all_findings, taxonomy_dir=TAXONOMY_DIR) == []
