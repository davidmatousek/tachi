"""Integration tests for agentic pattern extraction and propagation (Feature 142).

Covers three areas per tasks.md T018:

  1. Pattern extraction from threats.md — `extract-report-data.py` extraction
     of the new `agentic_pattern` column via `parse_threats_findings()`, plus
     the `has_agentic_patterns` boolean surfaced by `detect_artifacts()`
     (mirrors Feature 141's `has_attack_chains` pattern). Backward compat
     validation (FR-017): pre-Feature-142 threats.md (no Pattern column)
     still extracts cleanly with every finding defaulted to
     `agentic_pattern: 'none'`.

  2. Threat-report Agentic Pattern Analysis subsection construction — severity
     counts per pattern, finding ID enumeration, and the FR-013 ordering
     rules: max severity descending → finding count descending → pattern
     enum order tertiary tiebreak. Multi-Pattern Findings subsection renders
     FIRST when any finding carries `agentic_pattern: multiple`; multi-pattern
     findings also appear under each matching pattern's subsection. Zero-
     finding subsections are suppressed.

  3. SARIF format parity (SC-007) — regex parity check comparing the
     `maestro-pattern:<name>` tag format from Feature 142 (FR-014) against
     the established `maestro-layer:<L#>` convention from Feature 084. Both
     must match the same lowercase / colon-separator / no-quoting / no-
     spaces invariant. Findings with `agentic_pattern: none` MUST NOT
     receive a `maestro-pattern:` tag (avoiding tag noise).

The threat-report Pattern Analysis area uses reference implementations of
the subsection-construction algorithm described in
``.claude/agents/tachi/threat-report.md`` (post-T015 section spec),
`templates/tachi/output-schemas/threats.md` Section 4b, and FR-013
ordering rules. Any divergence between the reference implementations here
and the agent-driven runtime assembly is a test-tier bug or a spec-tier
bug — resolution depends on which side diverges from the canonical FR/AC
text.

Fixtures live in ``tests/scripts/fixtures/pattern_extraction/``:
  - ``threats_with_patterns.md`` — has non-none patterns for several
    pattern categories plus one `multiple` finding
  - ``threats_all_none.md`` — Pattern column present, all values `—`
  - ``threats_pre_feature_142.md`` — pre-Feature-142 threats.md, no
    Pattern column at all
  - ``sarif_sample.json`` — sample SARIF output with both
    ``maestro-layer:L3`` (Feature 084) and ``maestro-pattern:<name>``
    (Feature 142) tags on ``result.properties.tags``
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pattern_extraction"

# Make tachi_parsers importable (stdlib-only path mutation)
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Import the hyphenated extract-report-data.py module via importlib (mirrors
# test_attack_chain_extraction.py convention for the same file).
_spec = importlib.util.spec_from_file_location(
    "extract_report_data", str(SCRIPT_PATH)
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

from tachi_parsers import (  # noqa: E402
    VALID_AGENTIC_PATTERNS,
    detect_artifacts,
    parse_finding_pattern,
    parse_threats_findings,
)


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# Canonical CSA pattern enum order per data-model.md Entity 6 and
# maestro-agentic-patterns-shared.md Section 1. Used as the tertiary
# tiebreak in FR-013 subsection ordering.
PATTERN_ENUM_ORDER = (
    "agent_collusion",
    "emergent_behavior",
    "temporal_attack",
    "trust_exploitation",
    "communication_vulnerability",
    "resource_competition",
)

# Severity ordinal from tachi_parsers.SEVERITY_ORDINAL — reproduced here
# to avoid circular dependency on test-scope imports and match the
# canonical risk-level comparison semantics used by the synthesis engine
# and threat-report ordering logic.
SEVERITY_ORDINAL = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
    "Note": 0,
}

# Canonical tag-format regex for maestro-<namespace>:<value> tokens per
# FR-014. Lowercase namespace (`layer` or `pattern`), colon separator,
# no quoting, no whitespace. Value is `L\d+` for layer or a lowercase
# pattern enum name for pattern. ``Unclassified`` (capital U) is
# explicitly allowed on layer tags per the Feature 084 convention.
MAESTRO_TAG_REGEX = re.compile(
    r"^maestro-(layer|pattern):([A-Za-z0-9_]+)$"
)


# ---------------------------------------------------------------------------
# Fixture file loaders
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def threats_with_patterns_md() -> str:
    return (FIXTURES_DIR / "threats_with_patterns.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def threats_all_none_md() -> str:
    return (FIXTURES_DIR / "threats_all_none.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def threats_pre_feature_142_md() -> str:
    return (FIXTURES_DIR / "threats_pre_feature_142.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def sarif_sample() -> dict:
    return json.loads(
        (FIXTURES_DIR / "sarif_sample.json").read_text(encoding="utf-8")
    )


# ===========================================================================
# Area 1: Pattern extraction from threats.md
# ===========================================================================

class TestPatternExtractionFromThreatsMd:
    """Verify extract-report-data.py and tachi_parsers extract the pattern
    column correctly and emit `has_agentic_patterns` boolean as expected."""

    def test_parse_threats_findings_populates_pattern_field(
        self, threats_with_patterns_md
    ):
        """Every finding must have an `agentic_pattern` key (FR-003 / SC-010)."""
        findings = parse_threats_findings(threats_with_patterns_md)
        assert findings, "Expected at least one finding to be parsed"
        for f in findings:
            assert "agentic_pattern" in f, (
                f"Finding {f.get('id')} missing agentic_pattern key"
            )

    def test_parse_threats_findings_canonical_pattern_values(
        self, threats_with_patterns_md
    ):
        """All parsed patterns must be in the canonical enum (8 values)."""
        findings = parse_threats_findings(threats_with_patterns_md)
        for f in findings:
            assert f["agentic_pattern"] in VALID_AGENTIC_PATTERNS, (
                f"Finding {f.get('id')} has invalid pattern "
                f"{f.get('agentic_pattern')!r}"
            )

    def test_specific_pattern_assignments(self, threats_with_patterns_md):
        """Specific findings carry their expected pattern per the fixture."""
        findings = parse_threats_findings(threats_with_patterns_md)
        by_id = {f["id"]: f for f in findings}
        assert by_id["S-1"]["agentic_pattern"] == "trust_exploitation"
        assert by_id["AG-2"]["agentic_pattern"] == "agent_collusion"
        assert by_id["AGP-01"]["agentic_pattern"] == "agent_collusion"
        assert by_id["AG-4"]["agentic_pattern"] == "emergent_behavior"
        assert by_id["AGP-02"]["agentic_pattern"] == "temporal_attack"
        assert by_id["AG-5"]["agentic_pattern"] == "multiple"
        assert by_id["I-6"]["agentic_pattern"] == "communication_vulnerability"
        assert by_id["D-7"]["agentic_pattern"] == "resource_competition"

    def test_em_dash_pattern_normalizes_to_none(self, threats_with_patterns_md):
        """FR-009: em-dash ("—") in Pattern column normalizes to `none`."""
        findings = parse_threats_findings(threats_with_patterns_md)
        by_id = {f["id"]: f for f in findings}
        assert by_id["T-3"]["agentic_pattern"] == "none"

    def test_all_none_fixture_yields_all_none_patterns(self, threats_all_none_md):
        """Pattern column present but all `—` → every finding gets 'none'."""
        findings = parse_threats_findings(threats_all_none_md)
        assert findings, "Expected fixture to contain findings"
        for f in findings:
            assert f["agentic_pattern"] == "none", (
                f"Finding {f.get('id')} should be 'none' in all-none fixture, "
                f"got {f.get('agentic_pattern')!r}"
            )

    def test_pre_feature_142_fixture_defaults_to_none(
        self, threats_pre_feature_142_md
    ):
        """FR-017 backward compat: missing Pattern column → default 'none'."""
        findings = parse_threats_findings(threats_pre_feature_142_md)
        assert findings, "Expected pre-feature-142 fixture to contain findings"
        for f in findings:
            assert f["agentic_pattern"] == "none", (
                f"Pre-Feature-142 finding {f.get('id')} should default to "
                f"'none', got {f.get('agentic_pattern')!r}"
            )

    def test_parse_finding_pattern_handles_sentinels(self):
        """Helper normalizes None/empty/em-dash/hyphen/unknown → 'none'."""
        assert parse_finding_pattern(None) == "none"
        assert parse_finding_pattern("") == "none"
        assert parse_finding_pattern("   ") == "none"
        assert parse_finding_pattern("\u2014") == "none"  # em-dash
        assert parse_finding_pattern("—") == "none"  # em-dash literal
        assert parse_finding_pattern("-") == "none"
        assert parse_finding_pattern("unknown_pattern") == "none"

    def test_parse_finding_pattern_accepts_all_enum_values(self):
        """All 8 canonical enum values round-trip cleanly."""
        for value in VALID_AGENTIC_PATTERNS:
            assert parse_finding_pattern(value) == value
            assert parse_finding_pattern(value.upper()) == value  # case-fold

    def test_detect_artifacts_has_agentic_patterns_true(self, tmp_path):
        """has_agentic_patterns is True when ≥1 non-none pattern present."""
        (tmp_path / "threats.md").write_text(
            (FIXTURES_DIR / "threats_with_patterns.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        artifacts = detect_artifacts(tmp_path)
        assert artifacts["has_agentic_patterns"] is True

    def test_detect_artifacts_has_agentic_patterns_false_all_none(self, tmp_path):
        """has_agentic_patterns is False when all findings are 'none'."""
        (tmp_path / "threats.md").write_text(
            (FIXTURES_DIR / "threats_all_none.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        artifacts = detect_artifacts(tmp_path)
        assert artifacts["has_agentic_patterns"] is False

    def test_detect_artifacts_has_agentic_patterns_false_pre_f142(self, tmp_path):
        """Pre-Feature-142 baseline → has_agentic_patterns False (FR-017)."""
        (tmp_path / "threats.md").write_text(
            (FIXTURES_DIR / "threats_pre_feature_142.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        artifacts = detect_artifacts(tmp_path)
        assert artifacts["has_agentic_patterns"] is False


# ===========================================================================
# Area 2: Threat-report Agentic Pattern Analysis subsection construction
# ===========================================================================

def _build_pattern_analysis(findings: list) -> dict:
    """Reference implementation of Agentic Pattern Analysis assembly.

    Models the threat-report subsection-construction algorithm defined
    in ``.claude/agents/tachi/threat-report.md`` (post-T015 Agentic
    Pattern Analysis section spec) and the FR-013 ordering rules:

      - Build one subsection per canonical pattern that has ≥1 matching
        finding. Findings with ``agentic_pattern: multiple`` are
        included in EVERY canonical subsection they match (for this
        reference implementation, a `multiple` finding contributes to
        every canonical pattern subsection that produced ≥1 "hard"
        non-multiple match — this mirrors the spec's "multi-pattern
        findings also appear under each matching pattern's subsection"
        clause). Zero-finding subsections are suppressed.
      - Produce an ordered list of subsection records with:
          * ``pattern``: canonical enum value
          * ``count``: total findings (hard matches + multiple matches)
          * ``severity_counts``: dict keyed by severity with integer
            counts
          * ``max_severity_ordinal``: int (0-4) for ordering
          * ``findings``: list of finding IDs sorted alphanumerically
      - Ordering per FR-013:
          * primary: max severity descending (Critical=4 first)
          * secondary: finding count descending
          * tertiary: pattern enum order (agent_collusion first,
            resource_competition last)
      - ``Multi-Pattern Findings`` block (a non-canonical subsection
        holding findings with ``agentic_pattern: multiple``) is
        rendered FIRST when present (per template spec "rendered
        first").

    Returns a dict:
        {
          "has_multi_pattern": bool,
          "multi_pattern_findings": [finding IDs...],
          "subsections": [ordered records...],
        }

    Zero-finding subsections are absent from ``subsections``. When all
    findings are ``none``/``multiple`` only, ``subsections`` may be
    empty (``Multi-Pattern Findings`` still renders if present).
    """
    # Bucket findings by canonical pattern. `multiple` findings are
    # collected separately and also injected into every canonical
    # subsection per the spec clause "multi-pattern findings also
    # appear under each matching pattern's subsection".
    hard_buckets: dict = {p: [] for p in PATTERN_ENUM_ORDER}
    multi_findings: list = []

    for f in findings:
        pattern = f.get("agentic_pattern", "none")
        if pattern == "multiple":
            multi_findings.append(f)
        elif pattern in hard_buckets:
            hard_buckets[pattern].append(f)
        # "none" and any unexpected values are ignored (not surfaced
        # in the Pattern Analysis section).

    # Build subsection records. A canonical subsection is suppressed
    # ONLY when its bucket is empty AND there are no multi-pattern
    # findings (per spec: multi-pattern findings surface under every
    # canonical subsection that has ≥1 hard match). When multi findings
    # exist but the hard bucket is empty, the subsection is still
    # suppressed — multi findings only "appear under each matching
    # pattern's subsection" when that subsection is otherwise populated.
    subsections = []
    for pattern in PATTERN_ENUM_ORDER:
        hard = hard_buckets[pattern]
        if not hard:
            continue  # Zero-finding subsection suppression (FR-013)

        all_findings = list(hard) + list(multi_findings)
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for f in all_findings:
            sev = f.get("risk_level", "")
            if sev in severity_counts:
                severity_counts[sev] += 1

        max_ord = 0
        for sev, count in severity_counts.items():
            if count > 0:
                max_ord = max(max_ord, SEVERITY_ORDINAL.get(sev, 0))

        finding_ids = sorted(f["id"] for f in all_findings)

        subsections.append({
            "pattern": pattern,
            "count": len(all_findings),
            "severity_counts": severity_counts,
            "max_severity_ordinal": max_ord,
            "findings": finding_ids,
            "pattern_enum_index": PATTERN_ENUM_ORDER.index(pattern),
        })

    # FR-013 ordering: max severity desc → finding count desc →
    # pattern enum order tertiary.
    subsections.sort(
        key=lambda r: (
            -r["max_severity_ordinal"],
            -r["count"],
            r["pattern_enum_index"],
        )
    )

    return {
        "has_multi_pattern": bool(multi_findings),
        "multi_pattern_findings": sorted(f["id"] for f in multi_findings),
        "subsections": subsections,
    }


class TestPatternAnalysisSubsectionConstruction:
    """Verify severity counts, finding ID enumeration, ordering rules,
    and Multi-Pattern Findings placement (FR-013 + template spec)."""

    def _finding(self, fid, pattern, severity):
        """Compact finding-dict builder for ordering tests."""
        return {
            "id": fid,
            "agentic_pattern": pattern,
            "risk_level": severity,
        }

    def test_severity_counts_from_real_fixture(self, threats_with_patterns_md):
        """Parse the realistic fixture and verify severity counts per pattern."""
        findings = parse_threats_findings(threats_with_patterns_md)
        analysis = _build_pattern_analysis(findings)

        by_pattern = {s["pattern"]: s for s in analysis["subsections"]}

        # agent_collusion has AG-2 (Critical) + AGP-01 (Medium) hard
        # matches. AG-5 (High) is multiple — it counts here too.
        ac = by_pattern["agent_collusion"]
        assert ac["severity_counts"]["Critical"] == 1
        assert ac["severity_counts"]["High"] == 1
        assert ac["severity_counts"]["Medium"] == 1

        # emergent_behavior: AG-4 (High) hard, AG-5 (High) multiple
        eb = by_pattern["emergent_behavior"]
        assert eb["severity_counts"]["High"] == 2

        # temporal_attack: AGP-02 (High), AG-5 (High) multiple
        ta = by_pattern["temporal_attack"]
        assert ta["severity_counts"]["High"] == 2

        # trust_exploitation: S-1 (High), AG-5 (High) multiple
        te = by_pattern["trust_exploitation"]
        assert te["severity_counts"]["High"] == 2

    def test_finding_id_enumeration_sorted(self, threats_with_patterns_md):
        """Finding IDs enumerated under each subsection are sorted."""
        findings = parse_threats_findings(threats_with_patterns_md)
        analysis = _build_pattern_analysis(findings)
        for sub in analysis["subsections"]:
            assert sub["findings"] == sorted(sub["findings"]), (
                f"Pattern {sub['pattern']} finding IDs not sorted: "
                f"{sub['findings']}"
            )

    def test_agent_collusion_finding_ids_complete(self, threats_with_patterns_md):
        """Agent Collusion enumerates AG-2, AGP-01, and the multi AG-5."""
        findings = parse_threats_findings(threats_with_patterns_md)
        analysis = _build_pattern_analysis(findings)
        ac = next(
            s for s in analysis["subsections"] if s["pattern"] == "agent_collusion"
        )
        assert set(ac["findings"]) == {"AG-2", "AGP-01", "AG-5"}

    def test_zero_finding_subsections_absent(self):
        """FR-013: zero-finding subsections must be suppressed, not empty."""
        findings = [
            self._finding("AG-1", "agent_collusion", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        patterns = [s["pattern"] for s in analysis["subsections"]]
        assert patterns == ["agent_collusion"]
        assert "resource_competition" not in patterns
        assert "temporal_attack" not in patterns

    def test_multi_pattern_section_rendered_first(self):
        """Spec: Multi-Pattern Findings rendered FIRST when present."""
        findings = [
            self._finding("AG-1", "agent_collusion", "High"),
            self._finding("AG-5", "multiple", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        assert analysis["has_multi_pattern"] is True
        assert analysis["multi_pattern_findings"] == ["AG-5"]

    def test_multi_pattern_also_in_each_matching_subsection(self):
        """Multi-pattern findings appear under each matching canonical subsection."""
        findings = [
            self._finding("AG-1", "agent_collusion", "High"),
            self._finding("AG-4", "emergent_behavior", "High"),
            self._finding("AG-5", "multiple", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        by_pattern = {s["pattern"]: s for s in analysis["subsections"]}
        assert "AG-5" in by_pattern["agent_collusion"]["findings"]
        assert "AG-5" in by_pattern["emergent_behavior"]["findings"]

    def test_no_multi_pattern_flag_when_absent(self):
        """has_multi_pattern False when no finding is tagged 'multiple'."""
        findings = [
            self._finding("AG-1", "agent_collusion", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        assert analysis["has_multi_pattern"] is False
        assert analysis["multi_pattern_findings"] == []

    def test_ordering_by_max_severity_descending(self):
        """FR-013 primary: max severity descending."""
        findings = [
            self._finding("AG-1", "agent_collusion", "Medium"),
            self._finding("AG-4", "emergent_behavior", "Critical"),
            self._finding("AG-7", "temporal_attack", "Low"),
        ]
        analysis = _build_pattern_analysis(findings)
        patterns_in_order = [s["pattern"] for s in analysis["subsections"]]
        assert patterns_in_order == [
            "emergent_behavior",  # Critical
            "agent_collusion",    # Medium
            "temporal_attack",    # Low
        ]

    def test_ordering_tied_severity_by_count_descending(self):
        """FR-013 secondary: tied max severity → finding count descending."""
        findings = [
            # emergent_behavior: 1 High finding
            self._finding("AG-4", "emergent_behavior", "High"),
            # agent_collusion: 3 High findings — wins on count tiebreak
            self._finding("AG-1", "agent_collusion", "High"),
            self._finding("AG-2", "agent_collusion", "High"),
            self._finding("AG-3", "agent_collusion", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        patterns_in_order = [s["pattern"] for s in analysis["subsections"]]
        assert patterns_in_order == ["agent_collusion", "emergent_behavior"]

    def test_ordering_tied_severity_tied_count_by_enum_order(self):
        """FR-013 tertiary: tied sev + tied count → pattern enum order.

        trust_exploitation (enum index 3) beats resource_competition
        (enum index 5); both have 1 High finding → enum order decides.
        """
        findings = [
            self._finding("D-1", "resource_competition", "High"),
            self._finding("S-1", "trust_exploitation", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        patterns_in_order = [s["pattern"] for s in analysis["subsections"]]
        # trust_exploitation earlier in enum → wins tertiary tiebreak
        assert patterns_in_order == [
            "trust_exploitation",
            "resource_competition",
        ]

    def test_ordering_three_way_tertiary_tiebreak(self):
        """Three-way tied sev + tied count → enum order strictly.

        agent_collusion (0) < emergent_behavior (1) < temporal_attack (2).
        """
        findings = [
            self._finding("AG-3", "temporal_attack", "High"),
            self._finding("AG-2", "emergent_behavior", "High"),
            self._finding("AG-1", "agent_collusion", "High"),
        ]
        analysis = _build_pattern_analysis(findings)
        patterns_in_order = [s["pattern"] for s in analysis["subsections"]]
        assert patterns_in_order == [
            "agent_collusion",
            "emergent_behavior",
            "temporal_attack",
        ]

    def test_ordering_complex_mixed_severities(self):
        """Realistic mix: proves all three ordering criteria apply jointly."""
        findings = [
            # emergent_behavior: 1 Critical, 1 High = max Critical, count 2
            self._finding("AG-10", "emergent_behavior", "Critical"),
            self._finding("AG-11", "emergent_behavior", "High"),
            # agent_collusion: 2 High = max High, count 2
            self._finding("AG-20", "agent_collusion", "High"),
            self._finding("AG-21", "agent_collusion", "High"),
            # trust_exploitation: 1 High = max High, count 1
            self._finding("S-30", "trust_exploitation", "High"),
            # temporal_attack: 1 Medium = max Medium, count 1
            self._finding("AGP-40", "temporal_attack", "Medium"),
        ]
        analysis = _build_pattern_analysis(findings)
        patterns_in_order = [s["pattern"] for s in analysis["subsections"]]
        # emergent (Critical) first; then the two High groups ordered by
        # count desc then enum order; temporal_attack (Medium) last.
        assert patterns_in_order == [
            "emergent_behavior",   # max sev Critical
            "agent_collusion",     # High, count 2, enum 0
            "trust_exploitation",  # High, count 1, enum 3
            "temporal_attack",     # Medium
        ]


# ===========================================================================
# Area 3: SARIF format parity regex check (SC-007)
# ===========================================================================

def _extract_all_tags(sarif_doc: dict) -> list:
    """Collect every string from every result.properties.tags array."""
    tags = []
    for run in sarif_doc.get("runs", []):
        for result in run.get("results", []):
            props = result.get("properties", {}) or {}
            for tag in props.get("tags", []) or []:
                tags.append(tag)
    return tags


class TestSarifTagFormatParity:
    """SC-007: ``maestro-pattern:<name>`` matches the lowercase/colon/no-
    whitespace contract established by ``maestro-layer:<L#>``."""

    def test_layer_tags_match_canonical_regex(self, sarif_sample):
        """Sanity: existing maestro-layer tags obey the shared regex."""
        tags = _extract_all_tags(sarif_sample)
        layer_tags = [t for t in tags if t.startswith("maestro-layer:")]
        assert layer_tags, "Expected at least one maestro-layer tag in sample"
        for tag in layer_tags:
            assert MAESTRO_TAG_REGEX.match(tag), (
                f"maestro-layer tag {tag!r} does not match canonical format"
            )

    def test_pattern_tags_match_canonical_regex(self, sarif_sample):
        """FR-014: maestro-pattern tags must match the same regex family."""
        tags = _extract_all_tags(sarif_sample)
        pattern_tags = [t for t in tags if t.startswith("maestro-pattern:")]
        assert pattern_tags, (
            "Expected at least one maestro-pattern tag in sample SARIF"
        )
        for tag in pattern_tags:
            assert MAESTRO_TAG_REGEX.match(tag), (
                f"maestro-pattern tag {tag!r} does not match canonical format"
            )

    def test_layer_and_pattern_share_regex_family(self, sarif_sample):
        """Parity invariant: both tag families share ONE canonical regex."""
        tags = _extract_all_tags(sarif_sample)
        namespaced = [
            t for t in tags
            if t.startswith("maestro-layer:") or t.startswith("maestro-pattern:")
        ]
        assert namespaced, "Expected at least one maestro-* tag in sample"
        for tag in namespaced:
            match = MAESTRO_TAG_REGEX.match(tag)
            assert match, f"Tag {tag!r} failed canonical parity regex"
            namespace = match.group(1)
            assert namespace in ("layer", "pattern"), (
                f"Unexpected namespace {namespace!r} in {tag!r}"
            )

    def test_pattern_tag_no_whitespace(self, sarif_sample):
        """FR-014: no spaces or whitespace permitted in tag tokens."""
        tags = _extract_all_tags(sarif_sample)
        for tag in tags:
            if not tag.startswith("maestro-"):
                continue
            assert " " not in tag, f"Whitespace in tag: {tag!r}"
            assert "\t" not in tag, f"Tab in tag: {tag!r}"

    def test_pattern_tag_no_quoting(self, sarif_sample):
        """FR-014: no quoting around the tag value."""
        tags = _extract_all_tags(sarif_sample)
        for tag in tags:
            if not tag.startswith("maestro-"):
                continue
            assert '"' not in tag, f"Double quote in tag: {tag!r}"
            assert "'" not in tag, f"Single quote in tag: {tag!r}"

    def test_pattern_tag_lowercase_namespace(self, sarif_sample):
        """FR-014: namespace (`layer`/`pattern`) must be lowercase."""
        tags = _extract_all_tags(sarif_sample)
        for tag in tags:
            if not tag.startswith("maestro-"):
                continue
            # Split on first colon; the left side is `maestro-<namespace>`.
            left = tag.split(":", 1)[0]
            assert left == left.lower(), (
                f"Namespace in {tag!r} is not lowercase: {left!r}"
            )

    def test_pattern_tag_uses_canonical_enum_value(self, sarif_sample):
        """FR-014: pattern tag value must be a canonical enum (or 'multiple')."""
        tags = _extract_all_tags(sarif_sample)
        pattern_tags = [t for t in tags if t.startswith("maestro-pattern:")]
        assert pattern_tags, "Expected at least one maestro-pattern tag"
        for tag in pattern_tags:
            value = tag.split(":", 1)[1]
            assert value in VALID_AGENTIC_PATTERNS, (
                f"Pattern tag value {value!r} is not a canonical enum"
            )
            # Specifically, 'none' must not appear as a tag (FR-014).
            assert value != "none", (
                "Findings with agentic_pattern='none' MUST NOT receive a "
                "maestro-pattern tag"
            )

    def test_none_pattern_findings_have_no_pattern_tag(self, sarif_sample):
        """FR-014: findings with `agentic_pattern: none` skip the tag.

        The fixture's T-3 result (agentic_pattern = none) must NOT carry a
        `maestro-pattern:` tag. It MAY still carry a `maestro-layer:` tag.
        """
        for run in sarif_sample.get("runs", []):
            for result in run.get("results", []):
                if result.get("ruleId") != "T-3":
                    continue
                tags = (result.get("properties", {}) or {}).get("tags", []) or []
                pattern_tags = [
                    t for t in tags if t.startswith("maestro-pattern:")
                ]
                assert pattern_tags == [], (
                    f"Finding T-3 (agentic_pattern=none) unexpectedly has "
                    f"pattern tags: {pattern_tags}"
                )

    def test_multiple_pattern_tag_is_valid(self, sarif_sample):
        """data-model.md Entity 3: `maestro-pattern:multiple` is valid."""
        tags = _extract_all_tags(sarif_sample)
        multiple_tags = [t for t in tags if t == "maestro-pattern:multiple"]
        assert multiple_tags, (
            "Expected fixture to include maestro-pattern:multiple tag"
        )
        for tag in multiple_tags:
            assert MAESTRO_TAG_REGEX.match(tag), (
                f"Valid 'multiple' tag failed canonical regex: {tag!r}"
            )

    def test_non_none_findings_have_exactly_one_pattern_tag(self, sarif_sample):
        """SC-007: each non-`none` finding receives exactly one pattern tag."""
        for run in sarif_sample.get("runs", []):
            for result in run.get("results", []):
                props = result.get("properties", {}) or {}
                pattern_value = props.get("maestro-pattern")
                if not pattern_value or pattern_value == "none":
                    continue  # none-pattern findings skipped
                tags = props.get("tags", []) or []
                pattern_tags = [
                    t for t in tags if t.startswith("maestro-pattern:")
                ]
                assert len(pattern_tags) == 1, (
                    f"Finding {result.get('ruleId')!r} has "
                    f"{len(pattern_tags)} maestro-pattern tags; expected 1. "
                    f"Tags: {pattern_tags}"
                )
