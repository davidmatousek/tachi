"""Unit tests for the F-7 Mobile Top 10 Coverage Bundle enrichment (T068).

These tests enforce structural invariants on the **five** enriched STRIDE host
agent files and their companion pattern catalogs at the **four-or-five-agent
scope** (M8 dual-host carve-up per ADR-036 D-4 yields five host enrichment):

- ``.claude/agents/tachi/spoofing.md`` (STRIDE tier, <=120 line cap; M1, M3)
- ``.claude/agents/tachi/tampering.md`` (STRIDE tier, <=120 line cap; M2, M4, M7)
- ``.claude/agents/tachi/info-disclosure.md`` (STRIDE tier, <=120 line cap; M5,
  M6, M9, M10)
- ``.claude/agents/tachi/privilege-escalation.md`` (STRIDE tier, <=120 line cap;
  M8 privilege-gain variant per ADR-036 D-4)
- ``.claude/agents/tachi/repudiation.md`` (STRIDE tier, <=120 line cap; M8
  accountability-loss variant per ADR-036 D-4)
- Five companion ``detection-patterns.md`` files under
  ``.claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/``
  carrying the new Pattern Categories per ADR-036 D-3.

Per spec ``specs/237-mobile-top-10-coverage-bundle/spec.md``, this module covers
F-7 functional requirements FR-2/FR-4/FR-6/FR-8 (line caps), FR-3/FR-5/FR-7/FR-9
(new Pattern Categories), FR-13 (no schema bump — sweep-tested via MAESTRO grep
clean across all 10 enriched files), FR-17 (this test layer), and success
criteria SC-1/SC-4/SC-7/SC-10 (line caps), SC-3/SC-6/SC-9 (Pattern Categories),
SC-15 (schema invariant), SC-17 (references-array contract + ATT&CK Mobile
catalog-gap codification).

This module follows the F-6 enrichment-test precedent in
``tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py`` (three-agent
scope) at four-or-five-agent scope. **Section B (structural byte-identity)**
is intentionally a thin presence check — full byte-identity of pre-existing
content is delegated to ``tests/scripts/test_backward_compatibility.py``
against the 6 byte-identity baselines per FR-15 / SC-13 separation-of-duties.

Schema regex tests are NOT included — F-7 reuses the existing ``S``, ``T``,
``I``, ``E``, ``R`` STRIDE prefixes without a schema bump per ADR-036 D-6
(fourth no-bump enrichment after F-3 / F-5 / F-6; first at four-or-five-agent
scope). Section G enforces the prose-only invariant for ATT&CK Mobile T1474 /
T1626 / T1398 — 3-of-3 worst-case catalog-resolvability gap codified in
ADR-036 D-7.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT


# ---------------------------------------------------------------------------
# File path constants (5 host agents + 5 companions + 11 fixtures)
# ---------------------------------------------------------------------------


# Host agent files (STRIDE-tier enrichment surface)
SPOOFING_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "spoofing.md"
TAMPERING_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "tampering.md"
INFO_DISCLOSURE_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "info-disclosure.md"
PRIVILEGE_ESCALATION_AGENT = (
    REPO_ROOT / ".claude" / "agents" / "tachi" / "privilege-escalation.md"
)
REPUDIATION_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "repudiation.md"

# Companion detection-pattern catalogs (Wave 3 new pattern categories)
SPOOFING_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-spoofing"
    / "references"
    / "detection-patterns.md"
)
TAMPERING_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-tampering"
    / "references"
    / "detection-patterns.md"
)
INFO_DISCLOSURE_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-info-disclosure"
    / "references"
    / "detection-patterns.md"
)
PRIVILEGE_ESCALATION_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-privilege-escalation"
    / "references"
    / "detection-patterns.md"
)
REPUDIATION_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-repudiation"
    / "references"
    / "detection-patterns.md"
)

# Eleven fixtures under tests/scripts/fixtures/mobile_top_10_coverage_bundle/
# NB: 11 (not 10) because M8 dual-host carve per ADR-036 D-4 yields one
# fixture per host (privilege-escalation E-{N} + repudiation R-{N}).
FIXTURE_DIR = (
    REPO_ROOT / "tests" / "scripts" / "fixtures" / "mobile_top_10_coverage_bundle"
)
# spoofing host (M1 + M3)
S_M1_FIXTURE = FIXTURE_DIR / "valid_category_n_plus_1_spoofing_mobile_credential_finding.yaml"
S_M3_FIXTURE = (
    FIXTURE_DIR / "valid_category_n_plus_2_spoofing_mobile_authentication_finding.yaml"
)
# tampering host (M2 + M4 + M7)
T_M2_FIXTURE = FIXTURE_DIR / "valid_category_11_tampering_mobile_supply_chain_finding.yaml"
T_M4_FIXTURE = FIXTURE_DIR / "valid_category_12_tampering_mobile_ipc_finding.yaml"
T_M7_FIXTURE = (
    FIXTURE_DIR / "valid_category_13_tampering_mobile_binary_protections_finding.yaml"
)
# info-disclosure host (M5 + M6 + M9 + M10)
I_M5_FIXTURE = (
    FIXTURE_DIR / "valid_category_n_plus_1_info_disclosure_mobile_communication_finding.yaml"
)
I_M6_FIXTURE = (
    FIXTURE_DIR / "valid_category_n_plus_2_info_disclosure_mobile_privacy_finding.yaml"
)
I_M9_FIXTURE = (
    FIXTURE_DIR / "valid_category_n_plus_3_info_disclosure_mobile_data_storage_finding.yaml"
)
I_M10_FIXTURE = (
    FIXTURE_DIR / "valid_category_n_plus_4_info_disclosure_mobile_cryptography_finding.yaml"
)
# M8 dual-host: privilege-escalation (privilege-gain variant) + repudiation
# (accountability-loss variant) per ADR-036 D-4
E_M8_FIXTURE = (
    FIXTURE_DIR
    / "valid_category_11_privilege_escalation_mobile_misconfiguration_finding.yaml"
)
R_M8_FIXTURE = (
    FIXTURE_DIR / "valid_category_9_repudiation_mobile_misconfiguration_finding.yaml"
)

# All 5 host agents (sweep tuples)
ALL_F7_HOST_AGENTS = (
    SPOOFING_AGENT,
    TAMPERING_AGENT,
    INFO_DISCLOSURE_AGENT,
    PRIVILEGE_ESCALATION_AGENT,
    REPUDIATION_AGENT,
)

# All 5 companions (sweep tuples)
ALL_F7_COMPANIONS = (
    SPOOFING_COMPANION,
    TAMPERING_COMPANION,
    INFO_DISCLOSURE_COMPANION,
    PRIVILEGE_ESCALATION_COMPANION,
    REPUDIATION_COMPANION,
)

# All 10 enriched files (5 hosts + 5 companions) for the MAESTRO grep sweep
ALL_F7_ENRICHED_FILES = ALL_F7_HOST_AGENTS + ALL_F7_COMPANIONS

# All 11 fixtures for the catalog-gap sweep
ALL_F7_FIXTURES = (
    S_M1_FIXTURE,
    S_M3_FIXTURE,
    T_M2_FIXTURE,
    T_M4_FIXTURE,
    T_M7_FIXTURE,
    I_M5_FIXTURE,
    I_M6_FIXTURE,
    I_M9_FIXTURE,
    I_M10_FIXTURE,
    E_M8_FIXTURE,
    R_M8_FIXTURE,
)


# ---------------------------------------------------------------------------
# Helpers (mirror F-6 verbatim per T068 contract)
# ---------------------------------------------------------------------------


def _load_fixture(path: Path) -> dict:
    """Load a YAML fixture from disk."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _joined_refs(fixture_path: Path) -> str:
    """Return the references array of a fixture as a pipe-joined string."""
    finding = _load_fixture(fixture_path)
    refs = finding.get("references", [])
    assert isinstance(refs, list), (
        f"{fixture_path.name} references MUST be a list; got {type(refs)}"
    )
    return " | ".join(refs)


def _all_fixture_refs_joined() -> str:
    """Aggregate all 11 F-7 fixtures' references into a single pipe-joined string.

    Used for catalog-resolvability sweep tests (T1474 / T1626 / T1398 prose-only
    per ADR-036 D-7 — 3-of-3 worst-case at four-or-five-agent scope).
    """
    parts = [_joined_refs(fixture) for fixture in ALL_F7_FIXTURES]
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Section A — Line-count caps (FR-2 / FR-4 / FR-6 / FR-8 + SC-1 / SC-4 / SC-7 / SC-10)
# ---------------------------------------------------------------------------


class TestLineCountCaps:
    """STRIDE-tier line-count caps preserved across all 5 host agents.

    Per ADR-023 lean-agent line-count discipline, every STRIDE-tier host
    agent MUST remain <=120 lines post-enrichment. F-7 enriches 5 host
    agents at four-or-five-agent scope (M8 dual-host carve per ADR-036 D-4);
    each is independently capped.
    """

    def test_spoofing_md_line_cap(self) -> None:
        """SC-1 / FR-2: spoofing.md MUST be <=120 lines (STRIDE-tier cap per ADR-023)."""
        line_count = sum(1 for _ in SPOOFING_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 120, (
            f"spoofing.md line count {line_count} exceeds STRIDE-tier cap of 120 "
            f"(ADR-023 lean-agent discipline; FR-2 / SC-1)."
        )

    def test_tampering_md_line_cap(self) -> None:
        """SC-4 / FR-4: tampering.md MUST be <=120 lines (STRIDE-tier cap per ADR-023)."""
        line_count = sum(1 for _ in TAMPERING_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 120, (
            f"tampering.md line count {line_count} exceeds STRIDE-tier cap of 120 "
            f"(ADR-023 lean-agent discipline; FR-4 / SC-4)."
        )

    def test_info_disclosure_md_line_cap(self) -> None:
        """SC-7 / FR-6: info-disclosure.md MUST be <=120 lines (STRIDE-tier cap)."""
        line_count = sum(1 for _ in INFO_DISCLOSURE_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 120, (
            f"info-disclosure.md line count {line_count} exceeds STRIDE-tier cap of 120 "
            f"(ADR-023 lean-agent discipline; FR-6 / SC-7)."
        )

    def test_privilege_escalation_md_line_cap(self) -> None:
        """SC-10 / FR-8: privilege-escalation.md MUST be <=120 lines (M8 priv-gain host)."""
        line_count = sum(
            1 for _ in PRIVILEGE_ESCALATION_AGENT.open("r", encoding="utf-8")
        )
        assert line_count <= 120, (
            f"privilege-escalation.md line count {line_count} exceeds STRIDE-tier cap "
            f"of 120 (ADR-023 lean-agent discipline; M8 privilege-gain variant per "
            f"ADR-036 D-4; FR-8 / SC-10)."
        )

    def test_repudiation_md_line_cap(self) -> None:
        """SC-10 / FR-8: repudiation.md MUST be <=120 lines (M8 accountability-loss host)."""
        line_count = sum(1 for _ in REPUDIATION_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 120, (
            f"repudiation.md line count {line_count} exceeds STRIDE-tier cap of 120 "
            f"(ADR-023 lean-agent discipline; M8 accountability-loss variant per "
            f"ADR-036 D-4; FR-8 / SC-10)."
        )


# ---------------------------------------------------------------------------
# Section B — Structural byte-identity presence check (lightweight)
# ---------------------------------------------------------------------------


class TestStructuralByteIdentityPreExisting:
    """Lightweight presence check that pre-existing companion content survived
    F-7 enrichment unmodified.

    Full byte-identity of pre-existing categories is delegated to
    ``tests/scripts/test_backward_compatibility.py`` against the 6 byte-identity
    baselines (per FR-15 / SC-13 separation-of-duties — `tester` agent owns
    baseline regen verification). This section is therefore a thin sanity-check
    asserting that distinctive pre-existing strings remain present after F-7
    additive-only edits per ADR-036 D-2 / ADR-023 D3.

    For each companion, we anchor on a distinctive pre-existing section header
    that pre-dates F-7 and would be removed only if a regression overwrote
    pre-existing content rather than appending. If this test fails but
    ``test_backward_compatibility.py`` passes, the regression is surgical —
    investigate the companion delta.
    """

    @pytest.mark.parametrize(
        "path,anchor",
        [
            (SPOOFING_COMPANION, "## Authentication Bypass"),
            (TAMPERING_COMPANION, "## Input Injection"),
            (INFO_DISCLOSURE_COMPANION, "## Error Message Exposure"),
            (PRIVILEGE_ESCALATION_COMPANION, "## Pattern Category 1: Broken Access Control"),
            (REPUDIATION_COMPANION, "## Missing Audit Trails"),
        ],
        ids=lambda v: v if isinstance(v, str) else v.parent.parent.name,
    )
    def test_pre_existing_section_anchor_present(self, path: Path, anchor: str) -> None:
        """Each companion MUST retain its pre-existing distinctive section anchor.

        Anchors chosen as the **first** distinctive non-Overview / non-Targeted
        section header in each companion as of pre-F-7 baseline. Removal would
        indicate a non-additive edit regression in violation of ADR-036 D-2.
        """
        content = path.read_text(encoding="utf-8")
        assert anchor in content, (
            f"{path.parent.parent.name} companion MUST retain pre-existing anchor "
            f"{anchor!r} per ADR-036 D-2 additive-only edit discipline (cross-ref "
            f"ADR-023 D3). Full byte-identity check: see "
            f"tests/scripts/test_backward_compatibility.py against 6 baselines."
        )

    def test_all_5_companions_retain_pattern_category_header_form(self) -> None:
        """Each of the 5 F-7 companions MUST retain at least one ``## Pattern Category``
        header (either pre-existing or F-7-added).

        This sanity-check guards against a regression that removed every
        ``## Pattern Category N:`` / ``## Pattern Category N —`` header from a
        companion file (which would silently break detection-pattern dispatch
        on agent invocation).
        """
        for path in ALL_F7_COMPANIONS:
            content = path.read_text(encoding="utf-8")
            matches = re.findall(
                r"^## Pattern Category [0-9N]", content, re.MULTILINE
            )
            assert len(matches) >= 1, (
                f"{path.parent.parent.name} companion MUST retain at least one "
                f"'## Pattern Category' header (regression guard); found {len(matches)}."
            )


# ---------------------------------------------------------------------------
# Section C — MAESTRO grep clean (FR-13 / SC-15 invariant sweep)
# ---------------------------------------------------------------------------


class TestMaestroGrepClean:
    """FR-13 / SC-15 (sweep extension): zero MAESTRO references on all 10
    enriched files.

    Consistent with F-1 through F-6 governance constraint — F-7 host files
    MUST NOT introduce MAESTRO references (MAESTRO layer assignment is
    orchestrator-owned, not agent-authored). Sweep at four-or-five-agent
    scope: 10 files (5 hosts + 5 companions).
    """

    @pytest.mark.parametrize("path", ALL_F7_ENRICHED_FILES, ids=lambda p: p.name)
    def test_no_maestro_references_in_enriched_files(self, path: Path) -> None:
        """No 'maestro' substring (case-insensitive) in any of the 10 F-7 files."""
        content = path.read_text(encoding="utf-8").lower()
        assert "maestro" not in content, (
            f"{path.name} MUST contain zero MAESTRO references "
            f"(MAESTRO layer assignment is orchestrator-owned, not agent-authored; "
            f"FR-13 / SC-15 sweep at four-or-five-agent scope per ADR-036)."
        )


# ---------------------------------------------------------------------------
# Section D — Pattern Category Disambiguation header presence (FR-11 / ADR-036 D-9)
# ---------------------------------------------------------------------------


class TestPatternCategoryDisambiguation:
    """FR-11 / ADR-036 D-9: each F-7 companion has exactly 1 Disambiguation header.

    The Disambiguation subsection maps the new mobile categories' boundary
    against pre-existing categories in the same companion (Q1 SPLIT
    discipline). At four-or-five-agent dual-host path: 5 companions × 1
    Disambiguation each = 5 matches sweep total.

    Mirrors F-6 Section C precedent at four-or-five-agent scope (F-6 was
    three-agent: 3 companions × 1 Disambiguation each = 3 matches).
    """

    @pytest.mark.parametrize(
        "path", ALL_F7_COMPANIONS, ids=lambda p: p.parent.parent.name
    )
    def test_pattern_category_disambiguation_present_on_5_companions(
        self, path: Path
    ) -> None:
        """Each of the 5 F-7 companions MUST contain exactly 1 Disambiguation header."""
        content = path.read_text(encoding="utf-8")
        matches = re.findall(
            r"^## Pattern Category Disambiguation", content, re.MULTILINE
        )
        assert len(matches) == 1, (
            f"{path.parent.parent.name} companion MUST contain exactly 1 "
            f"'## Pattern Category Disambiguation' header per FR-11 / ADR-036 D-9; "
            f"found {len(matches)}."
        )


# ---------------------------------------------------------------------------
# Section E — New Pattern Categories present (FR-3 / FR-5 / FR-7 / FR-9)
# ---------------------------------------------------------------------------


class TestNewPatternCategoriesPresent:
    """New mobile-tier Pattern Category headers MUST be present in the
    corresponding F-7 companion. Eleven assertions, one per F-7 fixture's
    owning category. Headers verified against authored content as of T068.

    Header naming convention: F-7 uses long-dash (—) separator ('Pattern
    Category N+1 — Title') except where a category index slots into existing
    numeric sequence (Cat 11 / 12 / 13 in tampering; Cat 11 in
    privilege-escalation; Cat 9 in repudiation) which uses long-dash
    consistently. Numeric-vs-N+K choice tracks the post-F-6 baseline of each
    companion.
    """

    def test_spoofing_companion_has_cat_n_plus_1_M1(self) -> None:
        """spoofing detection-patterns.md MUST contain M1 (Improper Mobile Credential Usage)."""
        content = SPOOFING_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category N+1 — Improper Mobile Credential Usage (M1)"
            in content
        ), (
            "Pattern Category N+1 (Improper Mobile Credential Usage — M1) "
            "header MUST be present in spoofing detection-patterns.md per FR-3."
        )

    def test_spoofing_companion_has_cat_n_plus_2_M3(self) -> None:
        """spoofing detection-patterns.md MUST contain M3 (Insecure Mobile Auth/Authz)."""
        content = SPOOFING_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category N+2 — Insecure Mobile Authentication / Authorization (M3)"
            in content
        ), (
            "Pattern Category N+2 (Insecure Mobile Authentication / Authorization — M3) "
            "header MUST be present in spoofing detection-patterns.md per FR-3."
        )

    def test_tampering_companion_has_cat_11_M2(self) -> None:
        """tampering detection-patterns.md MUST contain Cat 11 (Mobile Supply Chain Integrity)."""
        content = TAMPERING_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category 11 — Mobile Supply Chain Integrity (M2)" in content
        ), (
            "Pattern Category 11 (Mobile Supply Chain Integrity — M2) "
            "header MUST be present in tampering detection-patterns.md per FR-5. "
            "Numeric Cat 11 (not N+1) because tampering already carries Cat 1-10 "
            "post-F-6 baseline (with F-6 Cat 10 Adversarial Input Manipulation)."
        )

    def test_tampering_companion_has_cat_12_M4(self) -> None:
        """tampering detection-patterns.md MUST contain Cat 12 (Mobile IPC Input Validation).

        ADR-036 D-5 cross-axis annotation: Cat 12 owns mobile-IPC-input-side
        validation; the F-1 ``output-integrity`` agent independently owns
        LLM-output-side sanitization on disjoint architectural surfaces.
        """
        content = TAMPERING_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 12 — Mobile IPC Input Validation (M4)" in content, (
            "Pattern Category 12 (Mobile IPC Input Validation — M4) header MUST be "
            "present in tampering detection-patterns.md per FR-5. ADR-036 D-5 "
            "cross-axis boundary: F-1 output-integrity owns disjoint LLM-output-side "
            "sanitization."
        )

    def test_tampering_companion_has_cat_13_M7(self) -> None:
        """tampering detection-patterns.md MUST contain Cat 13 (Insufficient Mobile Binary Protections)."""
        content = TAMPERING_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category 13 — Insufficient Mobile Binary Protections (M7)"
            in content
        ), (
            "Pattern Category 13 (Insufficient Mobile Binary Protections — M7) "
            "header MUST be present in tampering detection-patterns.md per FR-5."
        )

    def test_info_disclosure_companion_has_cat_n_plus_1_M5(self) -> None:
        """info-disclosure detection-patterns.md MUST contain M5 (Insecure Mobile Communication)."""
        content = INFO_DISCLOSURE_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category N+1 — Insecure Mobile Communication (M5)" in content
        ), (
            "Pattern Category N+1 (Insecure Mobile Communication — M5) "
            "header MUST be present in info-disclosure detection-patterns.md per FR-7."
        )

    def test_info_disclosure_companion_has_cat_n_plus_2_M6(self) -> None:
        """info-disclosure detection-patterns.md MUST contain M6 (Inadequate Mobile Privacy Controls)."""
        content = INFO_DISCLOSURE_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category N+2 — Inadequate Mobile Privacy Controls (M6)"
            in content
        ), (
            "Pattern Category N+2 (Inadequate Mobile Privacy Controls — M6) "
            "header MUST be present in info-disclosure detection-patterns.md per FR-7."
        )

    def test_info_disclosure_companion_has_cat_n_plus_3_M9(self) -> None:
        """info-disclosure detection-patterns.md MUST contain M9 (Insecure Mobile Data Storage)."""
        content = INFO_DISCLOSURE_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category N+3 — Insecure Mobile Data Storage (M9)" in content
        ), (
            "Pattern Category N+3 (Insecure Mobile Data Storage — M9) "
            "header MUST be present in info-disclosure detection-patterns.md per FR-7."
        )

    def test_info_disclosure_companion_has_cat_n_plus_4_M10(self) -> None:
        """info-disclosure detection-patterns.md MUST contain M10 (Insufficient Mobile Cryptography)."""
        content = INFO_DISCLOSURE_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category N+4 — Insufficient Mobile Cryptography (M10)"
            in content
        ), (
            "Pattern Category N+4 (Insufficient Mobile Cryptography — M10) "
            "header MUST be present in info-disclosure detection-patterns.md per FR-7."
        )

    def test_privilege_escalation_companion_has_M8_priv_gain(self) -> None:
        """privilege-escalation detection-patterns.md MUST contain Cat 11 (M8 Privilege-Gain Variant).

        ADR-036 D-4 dual-host carve: M8 privilege-gain variant lives on
        ``privilege-escalation`` host; the accountability-loss variant lives
        on ``repudiation`` host. Same architecture may surface BOTH without
        duplication; mitigation vocabularies differ.
        """
        content = PRIVILEGE_ESCALATION_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category 11: M8 Privilege-Gain Variant — Mobile Security Misconfiguration"
            in content
        ), (
            "Pattern Category 11 (M8 Privilege-Gain Variant — Mobile Security "
            "Misconfiguration) header MUST be present in privilege-escalation "
            "detection-patterns.md per FR-9 / ADR-036 D-4."
        )

    def test_repudiation_companion_has_M8_accountability_loss(self) -> None:
        """repudiation detection-patterns.md MUST contain Cat 9 (M8 Accountability-Loss Variant).

        ADR-036 D-4 dual-host carve: M8 accountability-loss variant lives on
        ``repudiation`` host; counterpart privilege-gain variant lives on
        ``privilege-escalation`` host. Disjoint architectural-tells; disjoint
        mitigation vocabularies (audit-trail completeness + crash-reporting
        configuration vs authorization-gating + attestation integration).
        """
        content = REPUDIATION_COMPANION.read_text(encoding="utf-8")
        assert (
            "## Pattern Category 9: M8 Accountability-Loss Variant — Mobile Security Misconfiguration"
            in content
        ), (
            "Pattern Category 9 (M8 Accountability-Loss Variant — Mobile Security "
            "Misconfiguration) header MUST be present in repudiation "
            "detection-patterns.md per FR-9 / ADR-036 D-4."
        )


# ---------------------------------------------------------------------------
# Section F — Per-fixture references-array contract (SC-17 / Finding IR Invariant 1)
# ---------------------------------------------------------------------------


class TestFixtureReferencesContract:
    """SC-17 / Finding IR Invariant 1: each fixture's references array contains
    its primary OWASP Mobile Top 10:2024 identifier (catalog-resolvable per
    ``schemas/taxonomy/owasp.yaml`` per Wave 1.0 T012 verification).

    M8 dual-host fixtures additionally cite catalog-resolvable CWE entries and
    section-level OWASP MASVS-PLATFORM / MASVS-CODE granularity citations per
    ADR-036 D-3 mapping table row + the M8 dual-host carve per ADR-036 D-4.
    """

    def test_s_M1_fixture_references_array(self) -> None:
        """S-M1 fixture references MUST contain 'OWASP M1:2024'."""
        joined = _joined_refs(S_M1_FIXTURE)
        assert "OWASP M1:2024" in joined, (
            f"S-M1 (spoofing Cat N+1) fixture references MUST include "
            f"'OWASP M1:2024' (Improper Credential Usage; Invariant 1); got: {joined!r}"
        )

    def test_s_M3_fixture_references_array(self) -> None:
        """S-M3 fixture references MUST contain 'OWASP M3:2024'."""
        joined = _joined_refs(S_M3_FIXTURE)
        assert "OWASP M3:2024" in joined, (
            f"S-M3 (spoofing Cat N+2) fixture references MUST include "
            f"'OWASP M3:2024' (Insecure Authentication/Authorization; Invariant 1); "
            f"got: {joined!r}"
        )

    def test_t_M2_fixture_references_array(self) -> None:
        """T-M2 fixture references MUST contain 'OWASP M2:2024'."""
        joined = _joined_refs(T_M2_FIXTURE)
        assert "OWASP M2:2024" in joined, (
            f"T-M2 (tampering Cat 11) fixture references MUST include "
            f"'OWASP M2:2024' (Inadequate Supply Chain Security; Invariant 1); "
            f"got: {joined!r}"
        )

    def test_t_M4_fixture_references_array(self) -> None:
        """T-M4 fixture references MUST contain 'OWASP M4:2024'.

        ADR-036 D-5 cross-axis annotation: M4 OWASP citation lives entirely on
        ``tampering`` host. The disjoint-tells boundary with F-1
        ``output-integrity`` is at the architectural-tell axis without catalog
        overlap (no shared OWASP identifier between Cat 12 mobile-IPC-input and
        F-1 LLM-output-sanitization).
        """
        joined = _joined_refs(T_M4_FIXTURE)
        assert "OWASP M4:2024" in joined, (
            f"T-M4 (tampering Cat 12) fixture references MUST include "
            f"'OWASP M4:2024' (Insufficient Input/Output Validation; Invariant 1); "
            f"got: {joined!r}"
        )

    def test_t_M7_fixture_references_array(self) -> None:
        """T-M7 fixture references MUST contain 'OWASP M7:2024'."""
        joined = _joined_refs(T_M7_FIXTURE)
        assert "OWASP M7:2024" in joined, (
            f"T-M7 (tampering Cat 13) fixture references MUST include "
            f"'OWASP M7:2024' (Insufficient Binary Protections; Invariant 1); "
            f"got: {joined!r}"
        )

    def test_i_M5_fixture_references_array(self) -> None:
        """I-M5 fixture references MUST contain 'OWASP M5:2024'."""
        joined = _joined_refs(I_M5_FIXTURE)
        assert "OWASP M5:2024" in joined, (
            f"I-M5 (info-disclosure Cat N+1) fixture references MUST include "
            f"'OWASP M5:2024' (Insecure Communication; Invariant 1); got: {joined!r}"
        )

    def test_i_M6_fixture_references_array(self) -> None:
        """I-M6 fixture references MUST contain 'OWASP M6:2024'."""
        joined = _joined_refs(I_M6_FIXTURE)
        assert "OWASP M6:2024" in joined, (
            f"I-M6 (info-disclosure Cat N+2) fixture references MUST include "
            f"'OWASP M6:2024' (Inadequate Privacy Controls; Invariant 1); "
            f"got: {joined!r}"
        )

    def test_i_M9_fixture_references_array(self) -> None:
        """I-M9 fixture references MUST contain 'OWASP M9:2024'."""
        joined = _joined_refs(I_M9_FIXTURE)
        assert "OWASP M9:2024" in joined, (
            f"I-M9 (info-disclosure Cat N+3) fixture references MUST include "
            f"'OWASP M9:2024' (Insecure Data Storage; Invariant 1); got: {joined!r}"
        )

    def test_i_M10_fixture_references_array(self) -> None:
        """I-M10 fixture references MUST contain 'OWASP M10:2024'."""
        joined = _joined_refs(I_M10_FIXTURE)
        assert "OWASP M10:2024" in joined, (
            f"I-M10 (info-disclosure Cat N+4) fixture references MUST include "
            f"'OWASP M10:2024' (Insufficient Cryptography; Invariant 1); "
            f"got: {joined!r}"
        )

    def test_e_M8_fixture_references_array(self) -> None:
        """E-M8 fixture references MUST contain M8 + CWE-732 + MASVS-PLATFORM.

        ADR-036 D-4 privilege-gain variant on ``privilege-escalation`` host;
        ADR-036 D-3 mapping table row populates references with section-level
        MASVS-PLATFORM granularity citation. CWE-732 (Incorrect Permission
        Assignment) is catalog-resolvable per pre-existing tachi-privilege-
        escalation companion Primary Sources list.
        """
        joined = _joined_refs(E_M8_FIXTURE)
        assert "OWASP M8:2024" in joined, (
            f"E-M8 (privilege-escalation Cat 11; M8 priv-gain variant) fixture "
            f"references MUST include 'OWASP M8:2024' (Security Misconfiguration; "
            f"Invariant 1); got: {joined!r}"
        )
        assert "CWE-732" in joined, (
            f"E-M8 fixture references MUST include 'CWE-732' (Incorrect Permission "
            f"Assignment; catalog-resolvable per ADR-036 D-3); got: {joined!r}"
        )
        assert "MASVS-PLATFORM" in joined, (
            f"E-M8 fixture references MUST include 'OWASP MASVS-PLATFORM' (section-level "
            f"granularity per ADR-036 D-3 mapping table); got: {joined!r}"
        )

    def test_r_M8_fixture_references_array(self) -> None:
        """R-M8 fixture references MUST contain M8 + CWE-778 + MASVS-CODE.

        ADR-036 D-4 accountability-loss variant on ``repudiation`` host; the
        privilege-gain counterpart is at E-10 on ``privilege-escalation``.
        Disjoint mitigation vocabularies preserved across the dual-host carve.
        CWE-778 (Insufficient Logging) catalog-resolvable per pre-existing
        tachi-repudiation companion Primary Sources list.
        """
        joined = _joined_refs(R_M8_FIXTURE)
        assert "OWASP M8:2024" in joined, (
            f"R-M8 (repudiation Cat 9; M8 accountability-loss variant) fixture "
            f"references MUST include 'OWASP M8:2024' (Security Misconfiguration; "
            f"Invariant 1); got: {joined!r}"
        )
        assert "CWE-778" in joined, (
            f"R-M8 fixture references MUST include 'CWE-778' (Insufficient Logging; "
            f"catalog-resolvable per ADR-036 D-3); got: {joined!r}"
        )
        assert "MASVS-CODE" in joined, (
            f"R-M8 fixture references MUST include 'OWASP MASVS-CODE' (section-level "
            f"granularity per ADR-036 D-3 mapping table); got: {joined!r}"
        )


# ---------------------------------------------------------------------------
# Section G — ATT&CK Mobile catalog-resolvability gap (Invariant 3 / ADR-036 D-7)
# ---------------------------------------------------------------------------


class TestAttackMobileCatalogResolvabilityGap:
    """SC-17 / Finding IR Contract Invariant 3: only catalog-resolvable
    identifiers appear in references arrays. Non-catalog ATT&CK Mobile
    entries appear ONLY as prose-only cross-references in mitigation
    narrative.

    Per ADR-036 D-7 (cross-ref Wave 1.0 T012 / T004 verification), the three
    cited ATT&CK Mobile techniques **T1474, T1626, T1398** are NOT
    catalog-resolvable in ``schemas/taxonomy/mitre-attack.yaml`` (verified
    0/0/0 absent at T004). They appear ONLY in prose mitigation narratives
    of the relevant Pattern Categories — NEVER in any fixture's references
    array.

    F-7's 3-of-3 prose-only worst-case at four-or-five-agent scope extends:
    - F-5 ADR-034 D-6 1-of-1 prose-only T1496 precedent
    - F-6 ADR-035 D-7 3-of-6 prose-only T0015/T0019/T0031 precedent
    """

    @pytest.mark.parametrize("attack_mobile_id", ["T1474", "T1626", "T1398"])
    def test_prose_only_attack_mobile_techniques_absent_from_references(
        self, attack_mobile_id: str
    ) -> None:
        """Non-catalog-resolvable ATT&CK Mobile techniques MUST NOT appear in
        any F-7 fixture references array per Invariant 3 / ADR-036 D-7.

        - T1474 (Supply Chain Compromise — Mobile sub-technique) is prose-only
          on tampering Cat 11 mitigation
        - T1626 (Abuse Elevation Control Mechanism — Mobile sub-technique) is
          prose-only on tampering Cat 13 + privilege-escalation Cat 11
          mitigations
        - T1398 (Boot or Logon Initialization Scripts — Mobile sub-technique)
          is prose-only on repudiation Cat 9 mitigation
        """
        joined = _all_fixture_refs_joined()
        assert attack_mobile_id not in joined, (
            f"ATT&CK Mobile {attack_mobile_id} MUST NOT appear in any F-7 fixture "
            f"references array per Invariant 3 / ADR-036 D-7 (catalog-absent in "
            f"schemas/taxonomy/mitre-attack.yaml; prose-only on owning Pattern "
            f"Category mitigation). 3-of-3 prose-only worst-case at four-or-five-"
            f"agent scope extends F-5 1-of-1 + F-6 3-of-6 catalog-gap precedent."
        )


# ---------------------------------------------------------------------------
# Section H — MANDATORY Read directive preservation (ADR-023 lean variant)
# ---------------------------------------------------------------------------


class TestMandatoryReadDirective:
    """ADR-023 lean variant: each F-7 host agent has a MANDATORY Read directive
    instructing it to load its companion detection-patterns.md before applying
    patterns to components.

    Mirrors the F-3 / F-5 / F-6 single-point-load pattern at four-or-five-agent
    scope; ensures F-7 enrichment did not regress the directive across any of
    the 5 host agents (additive-only edit discipline per ADR-036 D-2).
    """

    def test_spoofing_agent_mandatory_read_directive_present(self) -> None:
        """spoofing.md MUST contain the MANDATORY Read directive."""
        content = SPOOFING_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "spoofing.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant."
        )
        assert "tachi-spoofing/references/detection-patterns.md" in content, (
            "spoofing.md MANDATORY Read directive MUST reference "
            "'tachi-spoofing/references/detection-patterns.md' as its target."
        )

    def test_tampering_agent_mandatory_read_directive_present(self) -> None:
        """tampering.md MUST contain the MANDATORY Read directive."""
        content = TAMPERING_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "tampering.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant."
        )
        assert "tachi-tampering/references/detection-patterns.md" in content, (
            "tampering.md MANDATORY Read directive MUST reference "
            "'tachi-tampering/references/detection-patterns.md' as its target."
        )

    def test_info_disclosure_agent_mandatory_read_directive_present(self) -> None:
        """info-disclosure.md MUST contain the MANDATORY Read directive."""
        content = INFO_DISCLOSURE_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "info-disclosure.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant."
        )
        assert "tachi-info-disclosure/references/detection-patterns.md" in content, (
            "info-disclosure.md MANDATORY Read directive MUST reference "
            "'tachi-info-disclosure/references/detection-patterns.md' as its target."
        )

    def test_privilege_escalation_agent_mandatory_read_directive_present(self) -> None:
        """privilege-escalation.md MUST contain the MANDATORY Read directive."""
        content = PRIVILEGE_ESCALATION_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "privilege-escalation.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant. "
            "(M8 privilege-gain host per ADR-036 D-4.)"
        )
        assert (
            "tachi-privilege-escalation/references/detection-patterns.md" in content
        ), (
            "privilege-escalation.md MANDATORY Read directive MUST reference "
            "'tachi-privilege-escalation/references/detection-patterns.md' as its target."
        )

    def test_repudiation_agent_mandatory_read_directive_present(self) -> None:
        """repudiation.md MUST contain the MANDATORY Read directive."""
        content = REPUDIATION_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "repudiation.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant. "
            "(M8 accountability-loss host per ADR-036 D-4.)"
        )
        assert "tachi-repudiation/references/detection-patterns.md" in content, (
            "repudiation.md MANDATORY Read directive MUST reference "
            "'tachi-repudiation/references/detection-patterns.md' as its target."
        )
