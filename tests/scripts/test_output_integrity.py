"""Unit tests for Feature 201 ``output-integrity`` threat agent contracts.

Exercises two post-T005 / post-T006 behaviors:

  1. Schema 1.6 regex extension — ``schemas/finding.yaml`` ``id.pattern``
     extended from ``^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$`` (pre-1.6) to
     ``^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$`` (1.6+) per ADR-030 D8
     (Complex-Shape Clarifier extension to regex-alternation prefixes).
     Backward-compatibility: pre-1.6 IDs remain valid. Forward-compatibility:
     OI-{N} IDs now match. Negative cases: malformed IDs still rejected.

  2. F-A2 referential-integrity validation on OI-{N} findings —
     ``validate_source_attribution`` rejects findings that cite framework IDs
     absent from the F-A1 catalog (e.g., CWE-73 is not in ``schemas/taxonomy/
     cwe.yaml`` at the time of F-1; FR-007 substitutes CWE-22 for path
     traversal and CWE-94 for template injection). The fixture-driven test
     validates both the positive (valid citation) and negative (absent CWE)
     paths.

Zero new runtime or developer dependencies per SC-008 (``pyyaml`` + ``pytest``
already declared in ``requirements-dev.txt`` per Feature 128).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "finding.yaml"
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "output_integrity"


def _load_schema() -> dict:
    """Parse ``schemas/finding.yaml`` into a dict."""
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# --- T005 Regex Tests --------------------------------------------------------

class TestSchemaIdPatternRegex:
    """Test the ``id.pattern`` regex extension for schema 1.6.

    Pre-1.6 pattern: ``^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$``
    1.6 pattern:     ``^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$``

    Backward-compatibility: all pre-1.6 IDs MUST continue to match.
    Forward-compatibility: OI-{N} IDs MUST now match.
    Negative: malformed ID shapes MUST NOT match.
    """

    @pytest.fixture
    def id_pattern(self) -> re.Pattern:
        schema = _load_schema()
        raw_pattern = schema["finding"]["id"]["pattern"]
        return re.compile(raw_pattern)

    @pytest.fixture
    def schema_version(self) -> str:
        schema = _load_schema()
        return schema["schema_version"]

    def test_schema_version_is_1_6(self, schema_version: str) -> None:
        """SC-012 — schema_version MUST be ``1.6`` at F-1 merge."""
        assert schema_version == "1.6", (
            f"Schema version MUST be 1.6 post-T006 bump. Got: {schema_version!r}"
        )

    @pytest.mark.parametrize(
        "valid_id",
        [
            "S-1",     # spoofing (STRIDE)
            "T-1",     # tampering (STRIDE)
            "R-1",     # repudiation (STRIDE)
            "I-1",     # info-disclosure (STRIDE)
            "D-1",     # denial-of-service (STRIDE)
            "E-1",     # elevation-of-privilege (STRIDE)
            "AG-1",    # agent-autonomy (AI)
            "LLM-1",   # prompt-injection / data-poisoning / etc. (AI)
            "AGP-1",   # synthesized agentic pattern (Feature 142)
        ],
    )
    def test_pre_1_6_ids_remain_valid(self, id_pattern: re.Pattern, valid_id: str) -> None:
        """Backward-compatibility — every pre-1.6 prefix remains valid in 1.6 regex."""
        assert id_pattern.match(valid_id), (
            f"Pre-1.6 ID {valid_id!r} MUST remain valid in schema 1.6 regex."
        )

    @pytest.mark.parametrize(
        "oi_id",
        [
            "OI-1",    # single digit
            "OI-10",   # double digit
            "OI-99",   # triple digit edge
            "OI-100",  # multi-digit
        ],
    )
    def test_oi_ids_now_valid(self, id_pattern: re.Pattern, oi_id: str) -> None:
        """Forward-compatibility — OI-{N} IDs now match 1.6 regex."""
        assert id_pattern.match(oi_id), (
            f"OI-{{N}} ID {oi_id!r} MUST match schema 1.6 regex per ADR-030 D8."
        )

    @pytest.mark.parametrize(
        "invalid_id",
        [
            "OI1",         # missing hyphen
            "OIA-1",       # unknown extended prefix
            "oi-1",        # lowercase
            "",            # empty
            "OI-",         # missing digits
            "OI-abc",      # non-digit suffix
            "XX-1",        # unknown prefix
            "OI-1 ",       # trailing whitespace
            " OI-1",       # leading whitespace
        ],
    )
    def test_malformed_ids_rejected(self, id_pattern: re.Pattern, invalid_id: str) -> None:
        """Negative cases — the 1.6 regex still rejects malformed shapes."""
        assert not id_pattern.match(invalid_id), (
            f"Malformed ID {invalid_id!r} MUST NOT match schema 1.6 regex."
        )


# --- T037 Source-Attribution Fixture Tests ----------------------------------

class TestOutputIntegritySourceAttribution:
    """Fixture-driven F-A2 referential integrity validation.

    The valid fixture cites OWASP LLM05 (primary) + CWE-79 (related) — both
    present in the F-A1 catalog (``schemas/taxonomy/owasp.yaml`` + ``cwe.yaml``).
    The invalid fixture cites CWE-73 — absent from the catalog — and MUST be
    rejected by ``validate_source_attribution`` per F-A2 V4 referential check.
    """

    def test_valid_fixture_exists(self) -> None:
        """T007 — valid OI fixture committed."""
        fixture = FIXTURE_DIR / "valid_oi_finding.yaml"
        assert fixture.exists(), f"Valid OI fixture missing: {fixture}"

    def test_invalid_fixture_exists(self) -> None:
        """T008 — invalid-attribution OI fixture committed."""
        fixture = FIXTURE_DIR / "invalid_attribution_finding.yaml"
        assert fixture.exists(), f"Invalid OI fixture missing: {fixture}"

    def test_valid_fixture_parses(self) -> None:
        """Valid fixture parses as a well-formed finding dict."""
        fixture = FIXTURE_DIR / "valid_oi_finding.yaml"
        with fixture.open("r", encoding="utf-8") as f:
            finding = yaml.safe_load(f)
        assert finding is not None
        assert finding.get("id", "").startswith("OI-"), (
            f"Valid fixture id MUST start with 'OI-'. Got: {finding.get('id')!r}"
        )
        assert finding.get("category") == "llm", (
            f"Valid fixture category MUST be 'llm'. Got: {finding.get('category')!r}"
        )
        source_attribution = finding.get("source_attribution") or []
        assert len(source_attribution) >= 1, (
            "Valid fixture MUST carry at least one source_attribution entry."
        )
        primary_entries = [
            entry for entry in source_attribution
            if entry.get("relationship") == "primary"
        ]
        assert len(primary_entries) >= 1, (
            "Valid fixture MUST carry at least one primary source_attribution entry."
        )
        primary_ids = {entry.get("id") for entry in primary_entries}
        assert "LLM05" in primary_ids, (
            f"Valid fixture MUST cite OWASP LLM05 as primary. Got: {primary_ids!r}"
        )

    def test_invalid_fixture_cites_absent_cwe(self) -> None:
        """Invalid fixture explicitly cites CWE-73 (absent from F-A1 catalog)."""
        fixture = FIXTURE_DIR / "invalid_attribution_finding.yaml"
        with fixture.open("r", encoding="utf-8") as f:
            finding = yaml.safe_load(f)
        assert finding is not None
        source_attribution = finding.get("source_attribution") or []
        cwe_ids = {
            entry.get("id") for entry in source_attribution
            if entry.get("taxonomy") == "cwe"
        }
        assert "CWE-73" in cwe_ids, (
            f"Invalid fixture MUST cite CWE-73 (absent from F-A1 catalog). "
            f"Got: {cwe_ids!r}"
        )
