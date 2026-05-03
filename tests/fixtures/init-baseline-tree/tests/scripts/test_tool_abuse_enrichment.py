"""Unit tests for the F-3 ASI07 tool-abuse enrichment (T033).

These tests enforce structural invariants on the host agent file
(``.claude/agents/tachi/tool-abuse.md``) and the companion pattern catalog
(``.claude/skills/tachi-tool-abuse/references/detection-patterns.md``):

- Line-count cap on ``tool-abuse.md`` per SC-002 (≤150 lines; target 100-106)
- Single ``**MANDATORY**: Read`` directive preserved per ADR-023 lean variant
- Zero MAESTRO references in both files per SC-016 / ADR-023 Decision 2
- Pattern Categories 9 + 10 + Disambiguation present per SC-005
- Primary Sources extended with ASI07 + AML.T0060 per SC-007
- Categories 1-8 + Overview + DFD targets + Trigger Keywords byte-identical
  pre/post edit per SC-006 BLOCKER (additive-only invariant per ADR-023 D3)
- F-A2 referential-integrity validation on Cat-9/10 fixtures per SC-015 BLOCKER
  (valid_category_9_a2a_finding + valid_category_10_mcp_to_mcp_finding pass;
  invalid_attribution_finding rejected — CWE-99999 absent from catalog)

TDD expectation: Cases against tool-abuse.md fail on the pre-Wave-1.1 baseline
(98 lines, no ASI-07 in owasp_references) and pass post-Wave-1.1. Cases against
detection-patterns.md fail on the pre-Wave-2 baseline (8 categories, no
ASI07 Primary Source) and pass post-Wave-2.

Schema regex tests are NOT included — F-3 reuses the existing ``AG`` prefix
without a schema bump per ADR-032 Decision 3 (asymmetry with ADR-031 Decision 8).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_ABUSE_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "tool-abuse.md"
DETECTION_PATTERNS = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-tool-abuse"
    / "references"
    / "detection-patterns.md"
)
FIXTURE_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "tool_abuse_enrichment"
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"

# Make scripts/ importable so we can use the canonical F-A2 validator instead
# of a test-local re-implementation. Importing the canonical
# `validate_source_attribution` ensures these tests would catch schema drift
# (e.g. acceptance of a non-canonical "atlas" taxonomy alias) rather than
# masking it behind a divergent test helper.
sys.path.insert(0, str(REPO_ROOT))

from scripts.tachi_parsers import (  # noqa: E402
    ValidationError,
    validate_source_attribution,
)


# ---------------------------------------------------------------------------
# Section A — Agent file structural invariants (SC-002 / SC-016 / SC-001)
# ---------------------------------------------------------------------------


def test_tool_abuse_line_count_within_cap() -> None:
    """SC-002 BLOCKER: tool-abuse.md MUST be ≤150 lines (AI tier cap per ADR-023)."""
    line_count = sum(1 for _ in TOOL_ABUSE_AGENT.open("r", encoding="utf-8"))
    assert line_count <= 150, (
        f"tool-abuse.md line count {line_count} exceeds AI-tier cap of 150 "
        f"(target 100-106 post-edit; PRD-time baseline 98)."
    )


def test_tool_abuse_single_mandatory_read() -> None:
    """ADR-023 lean variant: exactly one **MANDATORY**: Read directive."""
    content = TOOL_ABUSE_AGENT.read_text(encoding="utf-8")
    count = content.count("**MANDATORY**: Read")
    assert count == 1, (
        f"tool-abuse.md MUST contain exactly 1 **MANDATORY**: Read directive "
        f"(found {count}). The ADR-023 lean variant requires single-point load."
    )


def test_tool_abuse_zero_maestro_references() -> None:
    """SC-016 BLOCKER: tool-abuse.md MUST contain zero MAESTRO references."""
    content = TOOL_ABUSE_AGENT.read_text(encoding="utf-8").lower()
    assert "maestro" not in content, (
        "tool-abuse.md MUST contain zero MAESTRO references per ADR-023 Decision 2 "
        "(MAESTRO layer assignment is orchestrator-owned, not agent-authored)."
    )


def test_tool_abuse_metadata_includes_asi07() -> None:
    """SC-001: owasp_references list MUST include ASI-07 post-edit."""
    content = TOOL_ABUSE_AGENT.read_text(encoding="utf-8")
    match = re.search(r"^owasp_references: \[(.+)\]$", content, re.MULTILINE)
    assert match is not None, "owasp_references metadata key not found"
    refs = [r.strip() for r in match.group(1).split(",")]
    assert "ASI-07" in refs, (
        f"owasp_references MUST include 'ASI-07' post-Wave-1.1 (found: {refs})"
    )
    # Pre-existing entries preserved byte-identically
    for required in ("ASI-02", "ASI-04", "MCP-03", "MCP-05", "LLM06:2025"):
        assert required in refs, (
            f"Pre-existing entry {required!r} MUST be preserved byte-identically "
            f"(SC-001 byte-identity invariant; found: {refs})"
        )


def test_tool_abuse_workflow_step5_extended() -> None:
    """SC-004: Detection Workflow Step 5 references include ASI-07, AML.T0060, CWE-287, CWE-345."""
    content = TOOL_ABUSE_AGENT.read_text(encoding="utf-8")
    for required in ("ASI-07", "AML.T0060", "CWE-287", "CWE-345"):
        assert required in content, (
            f"tool-abuse.md Detection Workflow Step 5 MUST include {required!r} "
            f"per FR-003 / SC-004."
        )


# ---------------------------------------------------------------------------
# Section B — Pattern catalog structural invariants (SC-005 / SC-007 / SC-016)
# ---------------------------------------------------------------------------


def test_detection_patterns_categories_9_and_10_present() -> None:
    """SC-005: Pattern Category 9 + 10 + Disambiguation MUST be present post-Wave-2."""
    content = DETECTION_PATTERNS.read_text(encoding="utf-8")
    assert "## Pattern Category 9: Insecure Inter-Agent Communication" in content, (
        "Pattern Category 9 (A2A) header missing"
    )
    assert "## Pattern Category 10: MCP-to-MCP Trust Propagation" in content, (
        "Pattern Category 10 (MCP-to-MCP) header missing"
    )
    assert "## Pattern Category Disambiguation" in content, (
        "Pattern Category Disambiguation subsection missing per FR-2 / ADR-032 D7"
    )


def test_detection_patterns_categories_have_required_subsections() -> None:
    """SC-005: each new category MUST carry indicators + worked example + mitigations + anti-indicators."""
    content = DETECTION_PATTERNS.read_text(encoding="utf-8")
    cat9_start = content.find("## Pattern Category 9: Insecure Inter-Agent Communication")
    cat10_start = content.find("## Pattern Category 10: MCP-to-MCP Trust Propagation")
    cat9_section = content[cat9_start:cat10_start]
    disambiguation_start = content.find("## Pattern Category Disambiguation")
    cat10_section = content[cat10_start:disambiguation_start]

    for section_name, section_content in [("Category 9", cat9_section), ("Category 10", cat10_section)]:
        assert "**Indicators**" in section_content, f"{section_name} missing Indicators subsection"
        assert "**Anti-Indicators**" in section_content, (
            f"{section_name} missing Anti-Indicators subsection per Q4 default YES"
        )
        assert "**Worked Example**" in section_content, f"{section_name} missing Worked Example"
        assert "**Primary source**" in section_content, f"{section_name} missing Primary source"
        assert "**Related sources**" in section_content, f"{section_name} missing Related sources"
        assert "**Mitigations**" in section_content, f"{section_name} missing Mitigations"


def test_detection_patterns_primary_sources_extended() -> None:
    """SC-007: Primary Sources MUST include OWASP ASI07:2026 + MITRE ATLAS AML.T0060."""
    content = DETECTION_PATTERNS.read_text(encoding="utf-8")
    primary_sources_start = content.find("## Primary Sources")
    assert primary_sources_start != -1, "## Primary Sources header missing"
    primary_sources = content[primary_sources_start:]
    assert "OWASP ASI07:2026" in primary_sources, (
        "Primary Sources MUST include 'OWASP ASI07:2026 — Insecure Inter-Agent Communication'"
    )
    assert "AML.T0060" in primary_sources, (
        "Primary Sources MUST include 'MITRE ATLAS AML.T0060 — Agent-in-the-Middle'"
    )


def test_detection_patterns_zero_maestro_references() -> None:
    """SC-016 BLOCKER: detection-patterns.md MUST contain zero MAESTRO references."""
    content = DETECTION_PATTERNS.read_text(encoding="utf-8").lower()
    assert "maestro" not in content, (
        "detection-patterns.md MUST contain zero MAESTRO references per ADR-023 Decision 2"
    )


# ---------------------------------------------------------------------------
# Section C — Categories 1-8 byte-identity preservation (SC-006 BLOCKER)
# ---------------------------------------------------------------------------


def test_categories_1_8_byte_identity_against_main() -> None:
    """SC-006 BLOCKER: Categories 1-8 + Overview + DFD targets + Triggers byte-identical vs. main.

    Uses git to extract the pre-edit content from main and compares the
    region from start-of-file through end of Category 8 (which terminates
    where ``## Pattern Category 9`` begins post-edit, or ``## Primary Sources``
    pre-edit). The unchanged region MUST be byte-identical.
    """
    rel_path = DETECTION_PATTERNS.relative_to(REPO_ROOT)
    proc = subprocess.run(
        ["git", "show", f"main:{rel_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    pre_content = proc.stdout
    post_content = DETECTION_PATTERNS.read_text(encoding="utf-8")

    pre_terminator = pre_content.find("\n## Primary Sources\n")
    assert pre_terminator != -1, (
        "Pre-edit baseline missing '## Primary Sources' header — git main may have drifted"
    )
    pre_unchanged_region = pre_content[:pre_terminator]

    post_terminator = post_content.find("\n## Pattern Category 9: Insecure Inter-Agent Communication")
    assert post_terminator != -1, (
        "Post-edit content missing '## Pattern Category 9' — Wave 2 not applied"
    )
    post_unchanged_region = post_content[:post_terminator]

    assert pre_unchanged_region == post_unchanged_region, (
        "SC-006 BLOCKER: Categories 1-8 + Overview + DFD targets + Trigger Keywords "
        "regions are NOT byte-identical pre/post edit. ADR-023 Decision 3 additive-only "
        "invariant violated. Hard revert required before merge."
    )


# ---------------------------------------------------------------------------
# Section D — F-A2 referential-integrity validation on Cat-9/10 fixtures (SC-015)
# ---------------------------------------------------------------------------


def test_valid_cat_9_fixture_passes_referential_integrity() -> None:
    """SC-015 BLOCKER: valid_category_9_a2a_finding.yaml MUST pass F-A2 validation.

    Uses the canonical ``scripts.tachi_parsers.validate_source_attribution``
    instead of a test-local re-implementation. The canonical validator reads
    catalogs internally with its own per-call cache, so no fixture pre-load
    is required.
    """
    fixture_path = FIXTURE_DIR / "valid_category_9_a2a_finding.yaml"
    with fixture_path.open("r", encoding="utf-8") as f:
        finding = yaml.safe_load(f)
    errors = validate_source_attribution([finding], taxonomy_dir=TAXONOMY_DIR)
    assert errors == [], (
        f"Cat-9 valid fixture failed F-A2 validation: {errors}. "
        f"Catalog citations must resolve in schemas/taxonomy/{{owasp,cwe,mitre-atlas}}.yaml."
    )


def test_valid_cat_10_fixture_passes_referential_integrity() -> None:
    """SC-015 BLOCKER: valid_category_10_mcp_to_mcp_finding.yaml MUST pass F-A2 validation.

    Uses the canonical ``scripts.tachi_parsers.validate_source_attribution``
    instead of a test-local re-implementation.
    """
    fixture_path = FIXTURE_DIR / "valid_category_10_mcp_to_mcp_finding.yaml"
    with fixture_path.open("r", encoding="utf-8") as f:
        finding = yaml.safe_load(f)
    errors = validate_source_attribution([finding], taxonomy_dir=TAXONOMY_DIR)
    assert errors == [], (
        f"Cat-10 valid fixture failed F-A2 validation: {errors}. "
        f"Catalog citations must resolve in schemas/taxonomy/{{owasp,cwe,mitre-atlas}}.yaml."
    )


def test_invalid_attribution_fixture_rejected() -> None:
    """SC-015 BLOCKER: invalid_attribution_finding.yaml MUST be rejected (CWE-99999 absent).

    Uses the canonical ``scripts.tachi_parsers.validate_source_attribution``;
    asserts that the returned list of ``ValidationError`` includes a record
    whose reason mentions ``CWE-99999``.
    """
    fixture_path = FIXTURE_DIR / "invalid_attribution_finding.yaml"
    with fixture_path.open("r", encoding="utf-8") as f:
        finding = yaml.safe_load(f)
    errors = validate_source_attribution([finding], taxonomy_dir=TAXONOMY_DIR)
    assert errors, (
        "Negative fixture MUST be rejected; canonical validator returned no errors. "
        "F-A2 referential-integrity validation is broken."
    )
    assert all(isinstance(e, ValidationError) for e in errors), (
        f"Canonical validator must return ValidationError instances; got: {errors}"
    )
    assert any("CWE-99999" in e.reason for e in errors), (
        f"Negative fixture MUST be rejected for CWE-99999 absence; got errors: {errors}. "
        f"F-A2 referential-integrity validation is broken."
    )


def test_cat_9_fixture_has_required_source_attribution_shape() -> None:
    """SC-015: Cat-9 fixture MUST cite ASI07 (primary) + CWE-287 (related)."""
    fixture_path = FIXTURE_DIR / "valid_category_9_a2a_finding.yaml"
    with fixture_path.open("r", encoding="utf-8") as f:
        finding = yaml.safe_load(f)
    sa = finding.get("source_attribution", [])
    assert any(
        e.get("taxonomy") == "owasp" and e.get("id") == "ASI07" and e.get("relationship") == "primary"
        for e in sa
    ), "Cat-9 fixture MUST cite {taxonomy: owasp, id: ASI07, relationship: primary}"
    assert any(
        e.get("taxonomy") == "cwe" and e.get("id") == "CWE-287" and e.get("relationship") == "related"
        for e in sa
    ), "Cat-9 fixture MUST cite {taxonomy: cwe, id: CWE-287, relationship: related}"


def test_cat_10_fixture_has_required_source_attribution_shape() -> None:
    """SC-015: Cat-10 fixture MUST cite ASI07 (primary) + CWE-345 (related)."""
    fixture_path = FIXTURE_DIR / "valid_category_10_mcp_to_mcp_finding.yaml"
    with fixture_path.open("r", encoding="utf-8") as f:
        finding = yaml.safe_load(f)
    sa = finding.get("source_attribution", [])
    assert any(
        e.get("taxonomy") == "owasp" and e.get("id") == "ASI07" and e.get("relationship") == "primary"
        for e in sa
    ), "Cat-10 fixture MUST cite {taxonomy: owasp, id: ASI07, relationship: primary}"
    assert any(
        e.get("taxonomy") == "cwe" and e.get("id") == "CWE-345" and e.get("relationship") == "related"
        for e in sa
    ), "Cat-10 fixture MUST cite {taxonomy: cwe, id: CWE-345, relationship: related}"


def test_fixture_ids_match_ag_prefix() -> None:
    """SC per data-model invariant 6: fixture IDs MUST match ^AG-\\d+$ (existing schema 1.7)."""
    ag_pattern = re.compile(r"^AG-\d+$")
    for fixture_name in (
        "valid_category_9_a2a_finding.yaml",
        "valid_category_10_mcp_to_mcp_finding.yaml",
    ):
        fixture_path = FIXTURE_DIR / fixture_name
        with fixture_path.open("r", encoding="utf-8") as f:
            finding = yaml.safe_load(f)
        finding_id = finding.get("id", "")
        assert ag_pattern.match(finding_id), (
            f"Fixture {fixture_name} id {finding_id!r} MUST match ^AG-\\d+$ "
            f"(F-3 reuses existing AG prefix; no schema bump per ADR-032 Decision 3)."
        )


# ---------------------------------------------------------------------------
# Section E: Live regen validation (T039 — extends fixture-driven F-A2 tests)
# ---------------------------------------------------------------------------

def test_validate_source_attribution_on_regen() -> None:
    """SC-009 / SC-015 / FR-A2: Regenerated agentic-app/threats.md MUST contain
    at least 1 NEW AG-{N} finding from Pattern Category 9 (A2A Inter-Agent
    Communication Channel security) with primary OWASP ASI-07 citation + related
    CWE-287 citation + optional MITRE ATLAS AML.T0060 citation.

    Read `examples/agentic-app/sample-report/threats.md` (canonical post-Wave-3 promote)
    and verify:
    - At least 1 AG-{N} finding marked [NEW]
    - That finding cites ASI-07 (or ASI07) in its OWASP/STRIDE column or description
    - Description references "Inter-Agent Communication" or "A2A" (Pattern Category 9)
    - Mitigations reference at least 2 of: mTLS, message signing (HMAC/Ed25519),
      nonce-based replay prevention, taint propagation
    """
    threats_md = REPO_ROOT / "examples" / "agentic-app" / "sample-report" / "threats.md"
    assert threats_md.exists(), f"Regenerated threats.md not found at {threats_md}"
    content = threats_md.read_text(encoding="utf-8")

    # NEW AG finding present
    new_ag_matches = re.findall(r"\| (AG-\d+) \| \[NEW\]", content)
    assert new_ag_matches, "Expected at least 1 AG-{N} finding marked [NEW] in regen threats.md"

    # ASI-07 cited
    assert re.search(r"ASI-?07", content), "Expected ASI-07 citation in regen threats.md"

    # Pattern Category 9 indicators
    assert re.search(r"Inter-Agent Communication|A2A", content, re.IGNORECASE), \
        "Expected Pattern Category 9 (A2A / Inter-Agent Communication) reference"

    # Mitigation indicators (at least 2 of the named mechanisms)
    mitigation_count = sum(1 for pattern in [
        r"mTLS",
        r"HMAC|Ed25519|message sign",
        r"nonce|replay",
        r"taint",
    ] if re.search(pattern, content, re.IGNORECASE))
    assert mitigation_count >= 2, \
        f"Expected >=2 of {{mTLS, message signing, nonce/replay, taint}} mitigations; found {mitigation_count}"
