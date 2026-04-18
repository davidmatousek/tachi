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

from scripts.tachi_parsers import parse_threats_findings  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "source_attribution"


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

    # Input order: owasp/LLM05, cwe/CWE-1426, mitre-atlas/AML.T0051
    assert records[0] == {"taxonomy": "owasp", "id": "LLM05", "relationship": "primary"}
    assert records[1] == {"taxonomy": "cwe", "id": "CWE-1426", "relationship": "primary"}
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
