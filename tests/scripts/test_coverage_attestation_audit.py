"""F-241 Coverage Attestation Audit Test (T035 / Wave 3.1 / SC-005 BLOCKER).

Walks ``schemas/taxonomy/owasp.yaml`` (60 records) and resolves each Covered
citation to >=1 agent file + >=1 detection-pattern category per BLP-01 Section 8
Quality Bar.

TDD-Red status:

- ``TestOwaspYamlRecordShape``: +2-field tests SKIP until Stream 3 task T037
  lands the ``out_of_scope`` / ``out_of_scope_rationale`` record-shape
  extension; 60-record count + 5-field shape PASS now.
- ``TestCitationCompleteness``: walk tests SKIP until T037 lands the
  partition field; static partial-item-deferral check PASSes now.
- ``TestKnownPartialItemClosure``: PASSes now on Wave 3.1 via static grep
  verification of the 6 closures (T025/T026/T028/T029/T030/T031).

Reference precedent: ``tests/scripts/test_coverage_attestation.py`` — uses
``pytest.skip()`` (not ``xfail``) for not-yet-implemented fields so failure
vs skip semantics stay clean across Wave transitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
OWASP_YAML = REPO_ROOT / "schemas" / "taxonomy" / "owasp.yaml"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents" / "tachi"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_owasp() -> list[dict[str, Any]]:
    """Load owasp.yaml and return the list of 60 OWASP records."""
    with OWASP_YAML.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if data is not None else []


def _grep_pattern_file(skill_name: str, needle: str) -> bool:
    """True iff ``needle`` appears in the named skill's detection-patterns.md."""
    path = SKILLS_DIR / skill_name / "references" / "detection-patterns.md"
    if not path.exists():
        return False
    return needle in path.read_text(encoding="utf-8")


def _agent_cites_owasp(needle: str) -> bool:
    """True iff ANY ``.claude/agents/tachi/*.md`` file references ``needle``."""
    if not AGENTS_DIR.exists():
        return False
    for agent_path in AGENTS_DIR.glob("*.md"):
        try:
            if needle in agent_path.read_text(encoding="utf-8"):
                return True
        except OSError:
            continue
    return False


def _pattern_catalog_cites_owasp(needle: str) -> bool:
    """True iff ANY ``tachi-*/references/detection-patterns.md`` cites ``needle``."""
    if not SKILLS_DIR.exists():
        return False
    for path in SKILLS_DIR.glob("tachi-*/references/detection-patterns.md"):
        try:
            if needle in path.read_text(encoding="utf-8"):
                return True
        except OSError:
            continue
    return False


# ===========================================================================
# Class 1: TestOwaspYamlRecordShape
# ===========================================================================


class TestOwaspYamlRecordShape:
    """Schema-shape tests on schemas/taxonomy/owasp.yaml.

    The 60-record-count and 5-field-shape tests PASS now (Wave 3.1).
    The +2-field tests SKIP until Stream 3 T037 extends the record shape.
    """

    def test_owasp_yaml_loads_60_records(self):
        """FR-020: owasp.yaml carries exactly 60 records (PASS now)."""
        records = _load_owasp()
        assert len(records) == 60, (
            f"FR-020 invariant violated: owasp.yaml must carry exactly 60 "
            f"records (Top 10:2021 + API:2023 + ASI:2026 + LLM:2025 + "
            f"Mobile:2024 + ML:2023 = 60). Got: {len(records)}"
        )

    def test_owasp_yaml_records_have_id_full_id_name_url_cwe_refs(self):
        """FR-003: every record carries id/full_id/name/url/cwe_refs (PASS now)."""
        records = _load_owasp()
        required = {"id", "full_id", "name", "url", "cwe_refs"}
        for idx, rec in enumerate(records):
            missing = required - set(rec.keys())
            assert not missing, (
                f"OWASP record idx={idx} (id={rec.get('id')!r}) missing "
                f"required field(s) {sorted(missing)}. Per FR-003, every "
                f"record must carry id/full_id/name/url/cwe_refs."
            )

    def test_owasp_yaml_records_have_out_of_scope_field(self):
        """T037 / ADR-027 D1: every record carries ``out_of_scope`` (default False).

        SKIPs now (T037 not landed). Flips to PASS once T037 extends the
        record shape with ``out_of_scope: false`` defaults across all 60.
        """
        records = _load_owasp()
        if records and "out_of_scope" not in records[0]:
            pytest.skip(
                "out_of_scope field not yet present on owasp.yaml records — "
                "Stream 3 task T037 (ADR-027 D1 record-shape extension) "
                "has not landed. Test flips to PASS once T037 lands."
            )
        for idx, rec in enumerate(records):
            assert "out_of_scope" in rec, (
                f"OWASP record idx={idx} (id={rec.get('id')!r}) missing "
                f"``out_of_scope``. Per T037 / ADR-027 D1, all 60 records "
                f"must carry the field with default False."
            )
            assert isinstance(rec["out_of_scope"], bool), (
                f"OWASP id={rec.get('id')!r} ``out_of_scope`` must be bool. "
                f"Got type {type(rec['out_of_scope']).__name__}."
            )

    def test_owasp_yaml_records_have_out_of_scope_rationale_field(self):
        """T037 / ADR-027 D1: every record carries ``out_of_scope_rationale``.

        SKIPs now (T037 not landed). Flips to PASS once T037 extends shape.
        """
        records = _load_owasp()
        if records and "out_of_scope_rationale" not in records[0]:
            pytest.skip(
                "out_of_scope_rationale field not yet present on owasp.yaml "
                "records — Stream 3 task T037 has not landed. Test flips "
                "to PASS once T037 lands."
            )
        for idx, rec in enumerate(records):
            assert "out_of_scope_rationale" in rec, (
                f"OWASP record idx={idx} (id={rec.get('id')!r}) missing "
                f"``out_of_scope_rationale``. Per T037 / ADR-027 D1, all "
                f"60 records must carry the field with default empty str."
            )
            assert isinstance(rec["out_of_scope_rationale"], str), (
                f"OWASP id={rec.get('id')!r} ``out_of_scope_rationale`` "
                f"must be str. Got type "
                f"{type(rec['out_of_scope_rationale']).__name__}."
            )


# ===========================================================================
# Class 2: TestCitationCompleteness (BLP-01 Section 8 Quality Bar)
# ===========================================================================


class TestCitationCompleteness:
    """For each OWASP record where ``out_of_scope == false``, assert >=1
    agent file + >=1 detection-pattern category cites the OWASP id.

    Walk tests SKIP until T037 lands the partition field; flip to PASS
    post-T037 + Stream 4 audit closure.
    """

    def test_every_covered_owasp_has_agent_citation(self):
        """BLP-01 Section 8: each Covered (in-scope) record cited by >=1 agent.

        SKIPs now (depends on T037 partition field). Flips to PASS post-T037
        + Stream 4 audit closure.
        """
        records = _load_owasp()
        if records and "out_of_scope" not in records[0]:
            pytest.skip(
                "Cannot enumerate Covered records until ``out_of_scope`` "
                "field exists on owasp.yaml — Stream 3 task T037 has not "
                "landed. Flips to PASS post-T037 + Stream 4 audit closure."
            )
        for rec in records:
            if rec.get("out_of_scope", False):
                continue
            owasp_id = rec["id"]
            assert _agent_cites_owasp(owasp_id), (
                f"BLP-01 Section 8 Quality Bar violation: Covered OWASP "
                f"record id={owasp_id!r} (name={rec.get('name')!r}) is "
                f"NOT cited by any ``.claude/agents/tachi/*.md`` file. "
                f"Either add an ``owasp_references`` entry on the owning "
                f"agent or set ``out_of_scope: true`` with a rationale."
            )

    def test_every_covered_owasp_has_pattern_category_citation(self):
        """BLP-01 Section 8: each Covered record cited by >=1 Pattern Category.

        SKIPs now (depends on T037 partition field). Flips to PASS post-T037
        + Stream 4 audit closure.
        """
        records = _load_owasp()
        if records and "out_of_scope" not in records[0]:
            pytest.skip(
                "Cannot enumerate Covered records until ``out_of_scope`` "
                "field exists on owasp.yaml — Stream 3 task T037 has not "
                "landed. Flips to PASS post-T037 + Stream 4 audit closure."
            )
        for rec in records:
            if rec.get("out_of_scope", False):
                continue
            owasp_id = rec["id"]
            assert _pattern_catalog_cites_owasp(owasp_id), (
                f"BLP-01 Section 8 Quality Bar violation: Covered OWASP "
                f"record id={owasp_id!r} (name={rec.get('name')!r}) is "
                f"NOT cited by any ``.claude/skills/tachi-*/references/"
                f"detection-patterns.md`` Pattern Category. Either add a "
                f"Pattern Category citation on the owning skill catalog "
                f"or set ``out_of_scope: true`` with a rationale."
            )

    def test_partial_owasp_items_either_covered_or_explicitly_deferred(self):
        """FR-005: each PRD-listed Partial item must be Covered or Deferred.

        Static check — does NOT depend on T037. PASSes now on Wave 3.1
        because the 6 closures landed in Stream 2 (T025/T026/T028/T029/
        T030/T031).
        """
        partial_items = ("A05:2021", "A06:2021", "API6:2023", "API8:2023",
                         "API9:2023", "API10:2023")
        for owasp_id in partial_items:
            assert _pattern_catalog_cites_owasp(owasp_id), (
                f"FR-005 violation: Partial item {owasp_id!r} is NEITHER "
                f"closed via Pattern Category citation NOR explicitly "
                f"deferred. Either land the closure in the appropriate "
                f"detection-patterns.md or document the Deferral in "
                f"ADR-037 (T080) and annotate Section 6 Coverage Matrix."
            )


# ===========================================================================
# Class 3: TestKnownPartialItemClosure (Stream 2 spec FR-005)
# ===========================================================================


class TestKnownPartialItemClosure:
    """Direct grep-based verification — no SKIP — that all 6 Partial items
    closed in F-241 Stream 2 are cited in the expected detection-pattern
    catalog. PASSes now on Wave 3.1 close-out.

    These tests do NOT depend on Stream 3 (T037) — they verify the landed
    Stream 2 closures via static grep on detection-patterns.md.
    """

    def test_a05_cited_on_privilege_escalation(self):
        """T025: A05:2021 closed on tachi-privilege-escalation Pattern Cat 11."""
        assert _grep_pattern_file("tachi-privilege-escalation", "A05:2021"), (
            "T025 closure missing: ``A05:2021`` not found in "
            "``.claude/skills/tachi-privilege-escalation/references/"
            "detection-patterns.md``."
        )

    def test_a06_cited_on_tampering(self):
        """T026: A06:2021 closed on tachi-tampering Pattern Category 8."""
        assert _grep_pattern_file("tachi-tampering", "A06:2021"), (
            "T026 closure missing: ``A06:2021`` not found in "
            "``.claude/skills/tachi-tampering/references/"
            "detection-patterns.md``."
        )

    def test_api6_cited_on_tool_abuse(self):
        """T028: API6:2023 closed on tachi-tool-abuse (NEW Pattern Category)."""
        assert _grep_pattern_file("tachi-tool-abuse", "API6:2023"), (
            "T028 closure missing: ``API6:2023`` not found in "
            "``.claude/skills/tachi-tool-abuse/references/"
            "detection-patterns.md``."
        )

    def test_api8_cited_on_privilege_escalation(self):
        """T029: API8:2023 closed on tachi-privilege-escalation Pat Cat 11."""
        assert _grep_pattern_file("tachi-privilege-escalation", "API8:2023"), (
            "T029 closure missing: ``API8:2023`` not found in "
            "``.claude/skills/tachi-privilege-escalation/references/"
            "detection-patterns.md``."
        )

    def test_api9_cited_on_info_disclosure(self):
        """T030: API9:2023 closed on tachi-info-disclosure (NEW Pat Cat)."""
        assert _grep_pattern_file("tachi-info-disclosure", "API9:2023"), (
            "T030 closure missing: ``API9:2023`` not found in "
            "``.claude/skills/tachi-info-disclosure/references/"
            "detection-patterns.md``."
        )

    def test_api10_cited_on_tampering(self):
        """T031: API10:2023 closed on tachi-tampering Pattern Category 9."""
        assert _grep_pattern_file("tachi-tampering", "API10:2023"), (
            "T031 closure missing: ``API10:2023`` not found in "
            "``.claude/skills/tachi-tampering/references/"
            "detection-patterns.md``."
        )

    def test_all_six_partial_items_closed(self):
        """Aggregate: all 6 Partial items cited in expected detection-pattern host.

        Provides single failure-summary view listing exactly which closures
        have NOT landed when any individual test fails.
        """
        expected = [
            ("tachi-privilege-escalation", "A05:2021", "T025"),
            ("tachi-tampering", "A06:2021", "T026"),
            ("tachi-tool-abuse", "API6:2023", "T028"),
            ("tachi-privilege-escalation", "API8:2023", "T029"),
            ("tachi-info-disclosure", "API9:2023", "T030"),
            ("tachi-tampering", "API10:2023", "T031"),
        ]
        missing = [
            f"{task}: {needle} on {skill}"
            for skill, needle, task in expected
            if not _grep_pattern_file(skill, needle)
        ]
        assert not missing, (
            f"FR-005 closure-bundle violation: {len(missing)}/6 Stream 2 "
            f"closures missing on Wave 3.1. Missing: {missing}"
        )
