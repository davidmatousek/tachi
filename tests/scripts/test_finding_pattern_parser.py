"""Unit tests for the Feature 142 finding-pattern parser extensions.

Exercises the three post-T005 parser behaviors in ``scripts/tachi_parsers.py``:

  1. :data:`VALID_AGENTIC_PATTERNS` module constant — the canonical 8-value enum
     used across the Phase 3.6 synthesis engine, the threats.md Pattern column,
     and the SARIF ``maestro-pattern:`` tag propagation path (FR-003).
  2. :func:`parse_finding_pattern` — a pure helper that normalizes a single
     cell value to a canonical lowercase enum string. Backward-compatibility
     per FR-017: null / missing / empty-string / whitespace-only / em-dash /
     ASCII-dash / unrecognized-string inputs all collapse to ``none``.
     Case-insensitive on input; canonical storage is always lowercase.
  3. :func:`parse_threats_findings` — extended to detect a ``Pattern`` or
     ``Agentic Pattern`` column (case-insensitive header match) in the
     Section 7 Recommended Actions table and populate
     ``finding["agentic_pattern"]`` on every returned finding. Pre-Feature-142
     threats.md (no column) default every finding to ``none`` per FR-017.

Five fixtures at ``tests/scripts/fixtures/finding_pattern_parser/``:

  * ``threats_with_patterns.md`` — post-Feature-142 shape, populated Pattern
    column with a spread of canonical values plus em-dash / none / multiple
    cases; the multi-row fixture exercises column detection + per-row
    canonicalization.
  * ``threats_pre_feature_142.md`` — pre-Feature-142 baseline, NO Pattern
    column anywhere; validates the FR-017 default-to-``none`` behavior.
  * ``threats_all_em_dash.md`` — post-Feature-142 shape but every row uses
    the FR-009 em-dash placeholder; validates em-dash → ``none`` handling.
  * ``threats_mixed_case_headers.md`` — post-Feature-142 shape with the
    ``Agentic Pattern`` spelling AND mixed-case values
    (``AGENT_COLLUSION``, ``Multiple``, ``Trust_Exploitation``); validates
    both case-insensitive header detection and case-insensitive value
    canonicalization.
  * ``threats_pattern_column_shifted.md`` — post-Feature-142 shape with the
    Pattern column placed LAST (after Mitigation) rather than the FR-009
    canonical position; validates header-name-based detection (positional
    extraction would return 'none' for every row here).

Mirrors :mod:`tests.scripts.test_attack_chains` style (Feature 141 precedent)
and :mod:`tests.scripts.test_project_name_parser` structure (field-parsing
helper test suite precedent). Zero new runtime dependencies per FR-020.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


# Make tachi_parsers importable the same way test_attack_chains.py does.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from tachi_parsers import (  # noqa: E402
    VALID_AGENTIC_PATTERNS,
    parse_finding_pattern,
    parse_threats_findings,
)


# =============================================================================
# Fixture paths
# =============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "finding_pattern_parser"

FIXTURE_WITH_PATTERNS = FIXTURES_DIR / "threats_with_patterns.md"
FIXTURE_PRE_F142 = FIXTURES_DIR / "threats_pre_feature_142.md"
FIXTURE_ALL_EM_DASH = FIXTURES_DIR / "threats_all_em_dash.md"
FIXTURE_MIXED_CASE_HEADERS = FIXTURES_DIR / "threats_mixed_case_headers.md"
FIXTURE_COLUMN_SHIFTED = FIXTURES_DIR / "threats_pattern_column_shifted.md"


# =============================================================================
# Shared test data
# =============================================================================

# The eight canonical enum values per data-model.md Entity 1 + FR-003.
# Keep this list explicit (not sourced from VALID_AGENTIC_PATTERNS) so a
# regression in the module constant is caught by test_constant_has_exact_values
# rather than silently passing the parametrize sweep below.
CANONICAL_PATTERN_VALUES = (
    "agent_collusion",
    "emergent_behavior",
    "temporal_attack",
    "trust_exploitation",
    "communication_vulnerability",
    "resource_competition",
    "none",
    "multiple",
)


# =============================================================================
# Test: VALID_AGENTIC_PATTERNS module constant
# =============================================================================

class TestValidAgenticPatternsConstant:
    """Tests for the VALID_AGENTIC_PATTERNS module-level constant.

    The constant is the single source of truth consumed by parse_finding_pattern
    and is exported for downstream consumers (Phase 3.6 synthesis engine, SARIF
    tag emitter). Any drift from the 8 canonical enum values per FR-003 is a
    regression caught here before it propagates to the synthesis or emission
    steps.
    """

    def test_constant_is_exported(self):
        """The module exports VALID_AGENTIC_PATTERNS at the top level."""
        import tachi_parsers

        assert hasattr(tachi_parsers, "VALID_AGENTIC_PATTERNS")

    def test_constant_has_eight_values(self):
        """The constant contains exactly 8 enum values per FR-003."""
        assert len(VALID_AGENTIC_PATTERNS) == 8

    def test_constant_has_exact_values(self):
        """The constant contains exactly the 8 canonical values (no drift)."""
        assert set(VALID_AGENTIC_PATTERNS) == set(CANONICAL_PATTERN_VALUES)

    def test_constant_values_are_all_lowercase(self):
        """All enum values are lowercase strings (canonical storage format)."""
        for value in VALID_AGENTIC_PATTERNS:
            assert isinstance(value, str)
            assert value == value.lower(), (
                f"VALID_AGENTIC_PATTERNS contains non-lowercase value: {value!r}"
            )

    def test_constant_has_none_sentinel(self):
        """The constant contains the `none` sentinel for non-pattern findings."""
        assert "none" in VALID_AGENTIC_PATTERNS

    def test_constant_has_multiple_sentinel(self):
        """The constant contains the `multiple` value for equal-rule matches."""
        assert "multiple" in VALID_AGENTIC_PATTERNS


# =============================================================================
# Test: parse_finding_pattern() — canonical enum values
# =============================================================================

class TestParseFindingPatternCanonicalValues:
    """Canonical enum values round-trip to themselves (identity on valid input)."""

    @pytest.mark.parametrize("canonical_value", CANONICAL_PATTERN_VALUES)
    def test_canonical_value_returns_itself(self, canonical_value):
        """Each of the 8 canonical values normalizes to itself (identity)."""
        assert parse_finding_pattern(canonical_value) == canonical_value


# =============================================================================
# Test: parse_finding_pattern() — case-insensitive input handling
# =============================================================================

class TestParseFindingPatternCaseInsensitive:
    """Case-insensitive input normalization to canonical lowercase values.

    Per the parse_finding_pattern docstring: "Case-insensitive on input:
    Agent_Collusion and AGENT_COLLUSION both normalize to agent_collusion.
    Canonical storage is always lowercase."
    """

    def test_uppercase_agent_collusion(self):
        assert parse_finding_pattern("AGENT_COLLUSION") == "agent_collusion"

    def test_mixed_case_multiple(self):
        assert parse_finding_pattern("Multiple") == "multiple"

    def test_title_case_trust_exploitation(self):
        assert parse_finding_pattern("Trust_Exploitation") == "trust_exploitation"

    def test_mixed_case_emergent_behavior(self):
        assert parse_finding_pattern("Emergent_Behavior") == "emergent_behavior"

    def test_uppercase_none(self):
        assert parse_finding_pattern("NONE") == "none"


# =============================================================================
# Test: parse_finding_pattern() — backward-compat sentinels (→ "none")
# =============================================================================

class TestParseFindingPatternBackwardCompat:
    """Backward-compat inputs per FR-017 all collapse to `none`.

    The complete list of inputs that MUST canonicalize to `none`:
        None (Python null) — pre-Feature-142 findings without the field
        ""  (empty string)
        "   " (whitespace-only)
        "\u2014" (em-dash U+2014 — FR-009 placeholder for `none` findings)
        "—"    (em-dash literal — same codepoint, direct string form)
        "-"    (ASCII hyphen — for robustness to editor de-curling)
        any unrecognized string — graceful degradation per FR-017
    """

    def test_none_input_returns_none_string(self):
        """Python None input returns the string 'none' (not None)."""
        assert parse_finding_pattern(None) == "none"

    def test_empty_string_returns_none(self):
        assert parse_finding_pattern("") == "none"

    def test_whitespace_only_returns_none(self):
        assert parse_finding_pattern("   ") == "none"

    def test_tabs_and_newlines_return_none(self):
        assert parse_finding_pattern("\t\n  \n") == "none"

    def test_em_dash_unicode_escape_returns_none(self):
        """U+2014 em-dash via unicode escape — canonical FR-009 placeholder."""
        assert parse_finding_pattern("\u2014") == "none"

    def test_em_dash_literal_returns_none(self):
        """U+2014 em-dash as a literal character in source returns 'none'."""
        assert parse_finding_pattern("—") == "none"

    def test_ascii_hyphen_returns_none(self):
        """ASCII hyphen-minus returns 'none' (editor-de-curling tolerance)."""
        assert parse_finding_pattern("-") == "none"

    def test_unrecognized_string_returns_none(self):
        """Unrecognized strings gracefully degrade to 'none' per FR-017."""
        assert parse_finding_pattern("xyz") == "none"

    def test_almost_canonical_typo_returns_none(self):
        """A near-miss typo is not silently corrected — returns 'none'."""
        assert parse_finding_pattern("agent_collusio") == "none"

    def test_non_string_integer_returns_none(self):
        """Non-string input (int) converts + fails validation → 'none'."""
        # `str(0).strip().lower()` is "0", which is not in VALID_AGENTIC_PATTERNS
        assert parse_finding_pattern(0) == "none"

    def test_em_dash_with_surrounding_whitespace_returns_none(self):
        """Em-dash with surrounding whitespace — strip before comparison."""
        assert parse_finding_pattern("  —  ") == "none"


# =============================================================================
# Test: parse_threats_findings() — Pattern column detection and extraction
# =============================================================================

class TestParseThreatsFindingsWithPatternColumn:
    """Post-Feature-142 threats.md with populated Pattern column."""

    @pytest.fixture(scope="class")
    def findings(self):
        content = FIXTURE_WITH_PATTERNS.read_text(encoding="utf-8")
        return parse_threats_findings(content)

    def test_all_findings_parsed(self, findings):
        """All 10 rows in the fixture table are parsed."""
        assert len(findings) == 10

    def test_every_finding_has_pattern_field(self, findings):
        """Every parsed finding has a populated ``agentic_pattern`` field."""
        for finding in findings:
            assert "agentic_pattern" in finding, (
                f"finding {finding.get('id')} missing agentic_pattern key"
            )
            assert finding["agentic_pattern"] is not None
            assert finding["agentic_pattern"] != ""

    def test_every_pattern_is_canonical(self, findings):
        """Every emitted agentic_pattern is one of the 8 canonical values."""
        for finding in findings:
            assert finding["agentic_pattern"] in VALID_AGENTIC_PATTERNS, (
                f"finding {finding['id']} has non-canonical pattern "
                f"{finding['agentic_pattern']!r}"
            )

    def test_trust_exploitation_mapped(self, findings):
        match = next(f for f in findings if f["id"] == "S-1")
        assert match["agentic_pattern"] == "trust_exploitation"

    def test_agent_collusion_mapped_twice(self, findings):
        """Two separate rows with agent_collusion both parse correctly."""
        collusion = [f for f in findings if f["agentic_pattern"] == "agent_collusion"]
        assert len(collusion) == 2
        ids = {f["id"] for f in collusion}
        assert ids == {"AG-2", "AGP-01"}

    def test_em_dash_row_parses_as_none(self, findings):
        """The T-3 row with Pattern = `—` parses as `agentic_pattern: 'none'`."""
        em_dash_finding = next(f for f in findings if f["id"] == "T-3")
        assert em_dash_finding["agentic_pattern"] == "none"

    def test_emergent_behavior_mapped(self, findings):
        match = next(f for f in findings if f["id"] == "AG-4")
        assert match["agentic_pattern"] == "emergent_behavior"

    def test_temporal_attack_mapped(self, findings):
        match = next(f for f in findings if f["id"] == "AG-5")
        assert match["agentic_pattern"] == "temporal_attack"

    def test_communication_vulnerability_mapped(self, findings):
        match = next(f for f in findings if f["id"] == "I-6")
        assert match["agentic_pattern"] == "communication_vulnerability"

    def test_resource_competition_mapped(self, findings):
        match = next(f for f in findings if f["id"] == "D-7")
        assert match["agentic_pattern"] == "resource_competition"

    def test_multiple_sentinel_mapped(self, findings):
        match = next(f for f in findings if f["id"] == "AG-8")
        assert match["agentic_pattern"] == "multiple"

    def test_explicit_none_value_mapped(self, findings):
        """A literal 'none' value in the table parses as 'none' (not '—')."""
        match = next(f for f in findings if f["id"] == "AG-9")
        assert match["agentic_pattern"] == "none"


# =============================================================================
# Test: Case-insensitive header detection + case-insensitive values
# =============================================================================

class TestParseThreatsFindingsCaseInsensitiveHeaders:
    """Parser detects the column by header name, case-insensitively.

    Both ``Pattern`` and ``Agentic Pattern`` are accepted as the column name.
    Header matching is case-insensitive per the parser's lower()-based check.
    """

    @pytest.fixture(scope="class")
    def findings(self):
        content = FIXTURE_MIXED_CASE_HEADERS.read_text(encoding="utf-8")
        return parse_threats_findings(content)

    def test_agentic_pattern_header_detected(self, findings):
        """The 'Agentic Pattern' spelling is detected (FR-009 canonical)."""
        # If header detection failed, every finding would default to 'none'.
        # We have 4 non-none rows in this fixture, so at least one must be
        # non-none for detection to have worked.
        non_none = [f for f in findings if f["agentic_pattern"] != "none"]
        assert len(non_none) >= 4

    def test_uppercase_value_canonicalized(self, findings):
        """AGENT_COLLUSION in a table cell normalizes to 'agent_collusion'."""
        match = next(f for f in findings if f["id"] == "AG-2")
        assert match["agentic_pattern"] == "agent_collusion"

    def test_title_case_value_canonicalized(self, findings):
        """Trust_Exploitation in a table cell normalizes to 'trust_exploitation'."""
        match = next(f for f in findings if f["id"] == "S-1")
        assert match["agentic_pattern"] == "trust_exploitation"

    def test_mixed_case_multiple_canonicalized(self, findings):
        """'Multiple' in a cell normalizes to 'multiple'."""
        match = next(f for f in findings if f["id"] == "AG-4")
        assert match["agentic_pattern"] == "multiple"

    def test_mixed_case_none_canonicalized(self, findings):
        """'None' in a cell normalizes to 'none'."""
        match = next(f for f in findings if f["id"] == "T-5")
        assert match["agentic_pattern"] == "none"


# =============================================================================
# Test: Column position doesn't matter — header-name-based detection
# =============================================================================

class TestParseThreatsFindingsColumnPositionIndependent:
    """Parser detects the Pattern column by header name, not by positional index.

    FR-009 documents the canonical layout as "between Category and Component",
    but the parser's responsibility is header-name-based detection, not
    positional. This class validates the fixture where the Pattern column is
    moved to the LAST position (after Mitigation) — a parser that relies on
    positional extraction would return 'none' for every row here.
    """

    @pytest.fixture(scope="class")
    def findings(self):
        content = FIXTURE_COLUMN_SHIFTED.read_text(encoding="utf-8")
        return parse_threats_findings(content)

    def test_all_findings_parsed(self, findings):
        assert len(findings) == 3

    def test_shifted_column_values_extracted(self, findings):
        """Pattern column values extract correctly even at the table end."""
        trust_exp = next(f for f in findings if f["id"] == "S-1")
        assert trust_exp["agentic_pattern"] == "trust_exploitation"

        collusion = next(f for f in findings if f["id"] == "AG-2")
        assert collusion["agentic_pattern"] == "agent_collusion"

        em_dash = next(f for f in findings if f["id"] == "T-3")
        assert em_dash["agentic_pattern"] == "none"


# =============================================================================
# Test: parse_threats_findings() — Section 7 with all em-dash rows
# =============================================================================

class TestParseThreatsFindingsAllEmDash:
    """Post-Feature-142 shape where every row uses the FR-009 em-dash placeholder.

    This shape is emitted by the orchestrator for architectures where the
    multi-agent gate predicate evaluates FALSE (single-agent / non-agentic).
    All findings receive ``agentic_pattern: none`` but the column still renders
    for consistent table shape (FR-009).
    """

    @pytest.fixture(scope="class")
    def findings(self):
        content = FIXTURE_ALL_EM_DASH.read_text(encoding="utf-8")
        return parse_threats_findings(content)

    def test_all_findings_parsed(self, findings):
        """Four rows in the fixture table are all parsed."""
        assert len(findings) == 4

    def test_every_finding_has_none_pattern(self, findings):
        """Every em-dash cell canonicalizes to 'none'."""
        for finding in findings:
            assert finding["agentic_pattern"] == "none", (
                f"finding {finding['id']} expected 'none' got "
                f"{finding['agentic_pattern']!r}"
            )


# =============================================================================
# Test: Backward compatibility — pre-Feature-142 threats.md (no Pattern column)
# =============================================================================

class TestParseThreatsFindingsPreFeature142Backward:
    """Pre-Feature-142 threats.md with NO Pattern column.

    Per FR-017: baseline findings lacking the field MUST parse successfully
    and default to ``agentic_pattern: 'none'`` on every returned finding.
    Zero parse errors, zero warnings.
    """

    @pytest.fixture(scope="class")
    def findings(self):
        content = FIXTURE_PRE_F142.read_text(encoding="utf-8")
        return parse_threats_findings(content)

    def test_all_findings_parsed(self, findings):
        """All 5 rows of the pre-Feature-142 fixture parse successfully."""
        assert len(findings) == 5

    def test_zero_parse_errors(self, findings):
        """Parsing produces findings (not an empty list on error)."""
        assert findings, "pre-Feature-142 fixture parsed to empty list"

    def test_every_finding_has_pattern_key(self, findings):
        """Per FR-017, every finding has an ``agentic_pattern`` key populated."""
        for finding in findings:
            assert "agentic_pattern" in finding

    def test_every_finding_defaults_to_none(self, findings):
        """Per FR-017, every finding defaults to 'none' (no Pattern column)."""
        for finding in findings:
            assert finding["agentic_pattern"] == "none", (
                f"finding {finding['id']} expected default 'none' got "
                f"{finding['agentic_pattern']!r}"
            )

    def test_non_pattern_fields_still_parsed(self, findings):
        """Existing (non-pattern) fields remain correctly parsed post-FR-017."""
        first = findings[0]
        assert first["id"] == "S-1"
        assert first["component"] == "Auth Service"
        assert first["risk_level"] == "High"
        # The mitigation field exercises the unchanged Section 7 extraction path
        assert "RS256" in first["mitigation"]

    def test_no_warnings_emitted(self, capsys, findings):
        """Parsing pre-Feature-142 content emits no warnings to stderr.

        Re-runs the parse inside the capsys context so captured stderr is
        attributable to this single parse (the class-scoped ``findings``
        fixture ran outside capsys scope).
        """
        content = FIXTURE_PRE_F142.read_text(encoding="utf-8")
        parse_threats_findings(content)
        captured = capsys.readouterr()
        assert "Warning" not in captured.err, (
            f"pre-Feature-142 fixture emitted unexpected warnings: {captured.err!r}"
        )


# =============================================================================
# Test: Determinism — same input produces identical output
# =============================================================================

class TestParseThreatsFindingsDeterminism:
    """Same input twice produces byte-identical output per ADR-021."""

    def test_deterministic_on_post_f142_fixture(self):
        content = FIXTURE_WITH_PATTERNS.read_text(encoding="utf-8")
        first = parse_threats_findings(content)
        second = parse_threats_findings(content)
        assert first == second

    def test_deterministic_on_pre_f142_fixture(self):
        content = FIXTURE_PRE_F142.read_text(encoding="utf-8")
        first = parse_threats_findings(content)
        second = parse_threats_findings(content)
        assert first == second
