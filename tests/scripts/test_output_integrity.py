"""Unit tests for the ``output-integrity`` threat agent contracts.

Covers two surfaces: the ``schemas/finding.yaml`` ``id.pattern`` regex
(extended with the ``OI`` prefix) and F-A2 referential-integrity validation
on OI-{N} source_attribution citations.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "output_integrity"


class TestSchemaIdPatternRegex:

    def test_schema_version_is_1_8(self, schema: dict) -> None:
        schema_version = schema["schema_version"]
        assert schema_version == "1.8", (
            f"Schema version MUST be 1.8. Got: {schema_version!r}"
        )

    @pytest.mark.parametrize(
        "valid_id",
        [
            "S-1",
            "T-1",
            "R-1",
            "I-1",
            "D-1",
            "E-1",
            "AG-1",
            "LLM-1",
            "AGP-1",
        ],
    )
    def test_pre_1_6_ids_remain_valid(self, id_pattern: re.Pattern, valid_id: str) -> None:
        assert id_pattern.match(valid_id), (
            f"Pre-1.6 ID {valid_id!r} MUST remain valid in schema 1.6 regex."
        )

    @pytest.mark.parametrize(
        "oi_id",
        [
            "OI-1",
            "OI-10",
            "OI-99",
            "OI-100",
        ],
    )
    def test_oi_ids_now_valid(self, id_pattern: re.Pattern, oi_id: str) -> None:
        assert id_pattern.match(oi_id), (
            f"OI-{{N}} ID {oi_id!r} MUST match schema 1.6 regex."
        )

    @pytest.mark.parametrize(
        "invalid_id",
        [
            "OI1",
            "OIA-1",
            "oi-1",
            "",
            "OI-",
            "OI-abc",
            "XX-1",
            "OI-1 ",
            " OI-1",
        ],
    )
    def test_malformed_ids_rejected(self, id_pattern: re.Pattern, invalid_id: str) -> None:
        assert not id_pattern.match(invalid_id), (
            f"Malformed ID {invalid_id!r} MUST NOT match schema 1.6 regex."
        )


class TestOutputIntegritySourceAttribution:

    def test_valid_fixture_exists(self) -> None:
        fixture = FIXTURE_DIR / "valid_oi_finding.yaml"
        assert fixture.exists(), f"Valid OI fixture missing: {fixture}"

    def test_invalid_fixture_exists(self) -> None:
        fixture = FIXTURE_DIR / "invalid_attribution_finding.yaml"
        assert fixture.exists(), f"Invalid OI fixture missing: {fixture}"

    def test_valid_fixture_parses(self) -> None:
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
        primary_ids = {
            entry.get("id") for entry in source_attribution
            if entry.get("relationship") == "primary"
        }
        assert "LLM05" in primary_ids, (
            f"Valid fixture MUST cite OWASP LLM05 as primary. Got: {primary_ids!r}"
        )

    def test_invalid_fixture_cites_absent_cwe(self) -> None:
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
