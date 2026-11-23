"""Unit tests for the shared ``scripts/tachi_parsers.py`` helpers.

Exercises :func:`classify_maestro_coverage_state` and the
:data:`SEVERITY_ORDINAL` ordinal-0 invariant introduced by Feature 311
(MAESTRO Matrix Model B — clean vs. n/a), plus Feature 373's K9/K10/K12
shared-parser fixes (adopter install + output fidelity).

``classify_maestro_coverage_state`` is the single inheritance point both
extractors call to translate the Section-6 "Highest Severity" carried token
into the ``coverage_state`` enum. It is pure (reads only its two arguments),
does NOT read Section 1, and does NOT decide applicability — it classifies the
orchestrator's already-authored decision. See
``specs/311-maestro-matrix-model-b-clean-vs-na/contracts/coverage-state-classifier.contract.md``
and ADR-047 (D2/D3/D5).

Feature 373 additions (tasks.md T016; data-model.md §3/§6; contracts/
extraction-data-contract.md):
  - K9: ``normalize_header``/``HEADER_ALIASES``, the level-aware stop rule in
    ``parse_markdown_table``, ``is_placeholder_id``, ``parse_score``.
  - K10: ``match_heading``-based MAESTRO heading matching (level 3 or 4) in
    both extractors.
  - K12: ``normalize_delta_status``, ``delta_status_by_id``,
    ``compute_delta_counts`` (new signature, counts the normalized Section 7
    map), ``apply_delta_status``, ``warn_delta_scope``, and the
    4b|4c-accepting ``parse_resolved_findings``.

Fixtures live under ``tests/scripts/fixtures/fidelity_373/`` — see that
directory's README.md for hand-computed expected values and the buggy
reads the pre-Feature-373 parsers produced.

Stdlib-only per PAT-014 — no PyYAML, no Path operations beyond importlib.
"""

from __future__ import annotations

import ast
import json
import random
import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sarif_common  # noqa: E402  -- correlation_assignments re-applies D8's rules, and one test runs both
import tachi_parts  # noqa: E402  -- the escapers whose references the decoder reverses

from tachi_parsers import (  # noqa: E402  -- import after sys.path mutation
    SEVERITY_ORDINAL,
    HEADER_ALIASES,
    classify_maestro_coverage_state,
    normalize_header,
    is_placeholder_id,
    parse_score,
    match_heading,
    parse_markdown_table,
    parse_compensating_controls_md,
    parse_risk_scores_findings,
    composite_scores_by_id,
    parse_threats_findings,
    classify_control_status,
    normalize_delta_status,
    delta_status_by_id,
    compute_delta_counts,
    apply_delta_status,
    warn_delta_scope,
    parse_resolved_findings,
    compute_risk_posture,
    ReferenceSetError,
    parse_reference_set,
    decode_references,
    parse_attack_chains,
    parse_correlation_groups,
    parse_controls_assessment_inputs,
    parse_sarif_member_set,
    FORM_LACKS_CAUSE,
    FORM_LACKS_FLAG,
    strip_bold,
    _find_table_with_column,
)

FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373"


def _composites_from_fixture(subdir: str) -> dict:
    """Build a K11 ``composites_by_id`` map from a fixture's risk-scores.md."""
    return composite_scores_by_id(parse_risk_scores_findings(_read_fixture(subdir, "risk-scores.md")))


def _read_fixture(subdir: str, filename: str) -> str:
    return (FIXTURES_DIR / subdir / filename).read_text(encoding="utf-8")


# Canonical Section-6 zero-finding tokens (ADR-047 D1; data-model.md Entity 1).
# Authored with U+2014 (em-dash); no trailing period in the markdown cell.
_CLEAN_TOKEN = "Analyzed — no findings this scan"
_NA_TOKEN = "Not applicable — no components map to this layer"
# Same n/a phrase written with U+2013 (en-dash) — must still classify as n/a
# (INV-2 dash tolerance; the populator/extractor read-robustness parity).
_NA_TOKEN_ENDASH = "Not applicable – no components map to this layer"


# =============================================================================
# classify_maestro_coverage_state — mapping table (contract T-1..T-5)
# =============================================================================

# T-1: any positive finding count is "findings" regardless of severity.
def test_positive_finding_count_is_findings():
    assert classify_maestro_coverage_state(8, "Critical") == "findings"
    assert classify_maestro_coverage_state(2, "High") == "findings"


# T-2: zero findings + the clean token → "clean".
def test_zero_findings_clean_token_is_clean():
    assert classify_maestro_coverage_state(0, _CLEAN_TOKEN) == "clean"


# T-3: zero findings + the n/a token → "not_applicable".
def test_zero_findings_na_token_is_not_applicable():
    assert classify_maestro_coverage_state(0, _NA_TOKEN) == "not_applicable"


# T-4: zero findings + empty / unrecognized → "clean" (backfill default; INV-4).
def test_zero_findings_empty_is_clean_backfill_default():
    assert classify_maestro_coverage_state(0, "") == "clean"


def test_zero_findings_unrecognized_is_clean():
    assert classify_maestro_coverage_state(0, "n/a-ish unknown") == "clean"


# T-5: en-dash (U+2013) tolerance on the n/a phrase → "not_applicable".
def test_na_token_endash_tolerated_is_not_applicable():
    assert classify_maestro_coverage_state(0, _NA_TOKEN_ENDASH) == "not_applicable"


# =============================================================================
# INV-3 / D5: zero-finding tokens resolve to severity ordinal 0
# =============================================================================

# T-6: neither the n/a nor the clean token is in SEVERITY_ORDINAL, so both
# dict-miss to rank 0 — compute_most_exposed_layer never selects them.
def test_zero_finding_tokens_resolve_to_ordinal_zero():
    assert SEVERITY_ORDINAL.get(_NA_TOKEN, 0) == 0
    assert SEVERITY_ORDINAL.get(_CLEAN_TOKEN, 0) == 0


# =============================================================================
# Feature 373 K9: normalize_header / HEADER_ALIASES, is_placeholder_id,
# parse_score
# =============================================================================

def test_normalize_header_casefolds_strips_trailing_dot_collapses_whitespace():
    assert normalize_header("Residual  Sev.") == "residual sev"
    assert normalize_header("RESIDUAL SCORE") == "residual score"
    assert normalize_header("Inherent") == "inherent"


def test_header_aliases_resolve_all_four_canonical_fields():
    # FR-K9.1's alias table (data-model.md §3): both the long and short
    # spelling of every field resolve to the same canonical name. Inherent
    # Score/Control Status are consumed starting with K11 (T020); the table
    # itself is complete from K9 (T016) on.
    assert HEADER_ALIASES[normalize_header("Residual Score")] == "residual_score"
    assert HEADER_ALIASES[normalize_header("Residual")] == "residual_score"
    assert HEADER_ALIASES[normalize_header("Residual Severity")] == "residual_severity"
    assert HEADER_ALIASES[normalize_header("Residual Sev.")] == "residual_severity"
    assert HEADER_ALIASES[normalize_header("Inherent Score")] == "inherent_score"
    assert HEADER_ALIASES[normalize_header("Inherent")] == "inherent_score"
    assert HEADER_ALIASES[normalize_header("Control Status")] == "control_status"
    assert HEADER_ALIASES[normalize_header("Status")] == "control_status"


def test_is_placeholder_id():
    assert is_placeholder_id("") is True
    assert is_placeholder_id("   ") is True
    assert is_placeholder_id("-") is True
    assert is_placeholder_id("--") is True
    assert is_placeholder_id("–") is True  # en dash
    assert is_placeholder_id("—") is True  # em dash
    assert is_placeholder_id("T-1") is False
    assert is_placeholder_id("F-7") is False


def test_parse_score_valid():
    assert parse_score("8.0") == Decimal("8.0")
    assert parse_score(" 4.5 ") == Decimal("4.5")


def test_parse_score_unparseable_returns_none():
    # data-model.md §3: "", "—", "8.5 (High)" are all unparseable.
    assert parse_score("") is None
    assert parse_score("—") is None  # em dash
    assert parse_score("8.5 (High)") is None


def test_parse_score_rejects_non_finite():
    # Decimal("NaN") parses without raising; only the finiteness check
    # rejects it (K9's explicit NaN/Infinity rule; do not confuse with a
    # parse failure).
    assert parse_score("NaN") is None
    assert parse_score("Infinity") is None
    assert parse_score("-Infinity") is None


def test_parse_score_never_raises_on_non_string_input():
    # T036 L-5 (code-reviewer-373.md, extraction-data-contract.md's
    # parse_score row): the contract says parse_score returns None on
    # failure and never raises. `s.strip()` has no fallback on an object
    # with no `.strip()` method -- None.strip() (and int/float/list, none
    # of which define `.strip()`) raised an uncaught AttributeError before
    # this fix, rather than returning None like any other unparseable
    # value. Latent today because every current caller passes a string.
    assert parse_score(None) is None
    assert parse_score(5) is None
    assert parse_score(5.0) is None
    assert parse_score([1, 2]) is None
    assert parse_score({}) is None


# =============================================================================
# Feature 373 K9: the level-aware parse_markdown_table stop rule, and
# parse_compensating_controls_md's short-form/empty-band fidelity
# =============================================================================

def test_parse_markdown_table_empty_h3_band_yields_no_phantom_rows():
    # Direct regression for the stop-rule fix: querying an empty "### Critical
    # Residual Severity" section must not scan across "### High Residual
    # Severity" into its real row (the pre-fix "adopts the next band's table"
    # bug), nor across the empty "### Low..." into "### Summary Statistics"'s
    # unrelated table (the "phantom rows" bug — fixtures README).
    content = _read_fixture("controls_bands_shortform", "compensating-controls.md")
    assert parse_markdown_table(content, "### Critical Residual Severity") == []
    assert parse_markdown_table(content, "### Low Residual Severity") == []
    high_rows = parse_markdown_table(content, "### High Residual Severity")
    assert len(high_rows) == 1
    assert high_rows[0]["Threat ID"] == "T-1"


_RISK_SUMMARY_TITLE_SNIPPET = """\
# Threat Model Risk Summary

Some narrative text under the document title. No table here.

## 1. Components

| Component | Type |
|-----------|------|
| API | service |
"""


def test_pin_risk_summary_matching_document_title_stops_at_next_h2():
    # RC-3 (K9, P0 architect finding F-1): the bare-substring "Risk
    # Summary" fallback can match a document TITLE line ("# Threat Model
    # Risk Summary") when the title contains the search string and
    # precedes the real "## 6. Risk Summary" section. With the pre-fix
    # stop rule (`level <= matched_level`, matched_level=1), the scan
    # never stops at the next "##" and wrongly adopts this later
    # "## 1. Components" table. After the fix (`level <= max(matched_level,
    # 2)`), a level-1 match stops at the next "##"/"#" line exactly like a
    # level-2 match, so this returns [] (W0 behavior) — never a later
    # section's table.
    assert parse_markdown_table(_RISK_SUMMARY_TITLE_SNIPPET, "Risk Summary") == []


def test_shortform_headers_and_empty_bands_yield_exactly_two_findings():
    # US-3a #1/#2 (K9/FR-K9.1-K9.2): short-form Coverage Matrix headers
    # resolve via HEADER_ALIASES, and the empty Critical/Low bands yield no
    # rows — exactly 2 findings, not the pre-fix 7 (2 real + 5 phantom).
    content = _read_fixture("controls_bands_shortform", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    assert [f["id"] for f in data["findings"]] == ["T-1", "T-2"]
    t1, t2 = data["findings"]
    assert t1["residual_score"] == "8.0"
    assert t1["residual_severity"] == "High"
    assert t2["residual_score"] == "4.5"
    assert t2["residual_severity"] == "Medium"
    assert data["severity"] == {
        "critical": 0, "high": 1, "medium": 1, "low": 0, "note": 0, "total": 2,
    }


# =============================================================================
# Feature 373 K10: MAESTRO heading matched at level 3 or level 4
# =============================================================================

def test_infographic_maestro_h3_heading_parses(extract_infographic_data):
    # US-3a #4 (K10/FR-K10.1): a "###" MAESTRO heading (3 hashes) instead of
    # the canonical "####" must still be found.
    content = _read_fixture("maestro_heading_h3", "threats.md")
    layers = extract_infographic_data.parse_maestro_layer_distribution(content)
    assert len(layers) == 2
    assert layers[0]["layer_id"] == "L1"
    assert layers[0]["finding_count"] == 3
    assert layers[0]["highest_severity"] == "Critical"
    assert layers[1]["layer_id"] == "L4"
    assert layers[1]["finding_count"] == 2
    assert layers[1]["highest_severity"] == "High"


def test_report_maestro_h3_heading_parses(extract_report_data):
    content = _read_fixture("maestro_heading_h3", "threats.md")
    result = extract_report_data.parse_maestro_data(content)
    assert result["has_maestro_data"] is True
    assert [l["layer_id"] for l in result["maestro_layer_distribution"]] == ["L1", "L4"]
    # Critical (L1, 3 findings) outranks High (L4, 2 findings) on count alone.
    assert result["most_exposed_layer"] == "L1 — Foundation Model"


# =============================================================================
# Feature 373 K12: normalize_delta_status, delta_status_by_id,
# compute_delta_counts (new signature), apply_delta_status, warn_delta_scope,
# and the 4b|4c-accepting parse_resolved_findings
# =============================================================================

def test_normalize_delta_status_bracket_and_emphasis_variants():
    # N6 order (data-model.md §6): strip backtick/emphasis/whitespace run,
    # then one [...] pair, then the run again, then upper-case.
    assert normalize_delta_status("NEW") == "NEW"
    assert normalize_delta_status("[NEW]") == "NEW"
    assert normalize_delta_status("**[NEW]**") == "NEW"
    assert normalize_delta_status("`[NEW]`") == "NEW"
    assert normalize_delta_status(" new ") == "NEW"
    assert normalize_delta_status("UPDATED") == "UPDATED"
    assert normalize_delta_status("[UNCHANGED]") == "UNCHANGED"


def test_baseline_resolved_4c_exact_delta_counts():
    # US-3a #5: a `## 4c.` baseline with every bracketed Status spelling
    # (bare NEW, [NEW], **[NEW]**, `[NEW]`) plus UPDATED/UNCHANGED, and one
    # placeholder resolved row that must not be counted.
    content = _read_fixture("baseline_resolved_4c", "threats.md")
    status_by_id, has_status_column, row_count = delta_status_by_id(content)
    assert has_status_column is True
    assert row_count == 6
    assert status_by_id == {
        "F-1": "NEW", "F-2": "NEW", "F-3": "NEW", "F-4": "NEW",
        "F-5": "UPDATED", "F-6": "UNCHANGED",
    }
    resolved = parse_resolved_findings(content)
    assert [f["id"] for f in resolved] == ["F-7", "F-8"]  # placeholder row skipped
    counts = compute_delta_counts(status_by_id, resolved)
    assert counts == {"new": 4, "updated": 1, "unchanged": 1, "resolved": 2}


def test_tier3_parse_threats_findings_normalizes_bracket_and_emphasis_variants():
    # K12 (T016 gap): tier-3 parse_threats_findings must normalize Status at
    # parse, same as delta_status_by_id's Section 7 map, so tier-3 badges
    # and top_findings[].delta_status never show a raw "[NEW]"-style value.
    # Reuses baseline_resolved_4c's bracket/emphasis matrix (bare NEW,
    # [NEW], **[NEW]**, `[NEW]`, UPDATED, UNCHANGED) — the same fixture
    # test_baseline_resolved_4c_exact_delta_counts reads above.
    content = _read_fixture("baseline_resolved_4c", "threats.md")
    findings = parse_threats_findings(content)
    delta_status_by_finding_id = {f["id"]: f["delta_status"] for f in findings}
    assert delta_status_by_finding_id == {
        "F-1": "NEW", "F-2": "NEW", "F-3": "NEW", "F-4": "NEW",
        "F-5": "UPDATED", "F-6": "UNCHANGED",
    }


def test_baseline_resolved_4b_legacy_matches_4c_resolved_count():
    # US-3a #6: the legacy `## 4b. Resolved Findings` heading yields the
    # same resolved count (2) as its `## 4c.` twin, proving heading-spelling
    # parity (FR-K12.4).
    content = _read_fixture("baseline_resolved_4b_legacy", "threats.md")
    status_by_id, has_status_column, row_count = delta_status_by_id(content)
    assert has_status_column is True
    assert row_count == 3
    assert status_by_id == {"F-1": "NEW", "F-5": "UPDATED", "F-6": "UNCHANGED"}
    resolved = parse_resolved_findings(content)
    assert [f["id"] for f in resolved] == ["F-7", "F-8"]
    counts = compute_delta_counts(status_by_id, resolved)
    assert counts == {"new": 1, "updated": 1, "unchanged": 1, "resolved": 2}


def test_non_baseline_no_status_column_yields_empty_map_and_no_warning(capsys):
    # US-3a #7 (second half): a Status-less Section 7 on a non-baseline run
    # (the real maestro-reference/mobile-banking-app shape) must not warn,
    # and delta_counts comes back all zero.
    content = _read_fixture("non_baseline_no_status_column", "threats.md")
    status_by_id, has_status_column, row_count = delta_status_by_id(content)
    assert has_status_column is False
    assert row_count == 2
    assert status_by_id == {}
    counts = compute_delta_counts(status_by_id, [])
    assert counts == {"new": 0, "updated": 0, "unchanged": 0, "resolved": 0}
    warn_delta_scope(False, has_status_column, status_by_id, row_count, {"B-1", "B-2"})
    assert capsys.readouterr().err == ""


def test_baseline_status_id_mismatch_warns_but_counts_unrestricted(capsys):
    # US-3a #7 (first half); architect F1/NM-1: the map's ID set differs
    # from the tier's finding-ID set. delta_counts is computed over the
    # normalized map, unrestricted by the tier's IDs — the warning is
    # informational only.
    threats_content = _read_fixture("baseline_status_id_mismatch", "threats.md")
    controls_content = _read_fixture("baseline_status_id_mismatch", "compensating-controls.md")
    status_by_id, has_status_column, row_count = delta_status_by_id(threats_content)
    assert has_status_column is True
    assert status_by_id == {"A-1": "NEW", "A-2": "UNCHANGED", "A-3": "UPDATED"}

    tier1_data = parse_compensating_controls_md(controls_content)
    tier_ids = {f["id"] for f in tier1_data["findings"]}
    assert tier_ids == {"A-1", "A-2", "A-4"}

    counts = compute_delta_counts(status_by_id, [])
    assert counts == {"new": 1, "updated": 1, "unchanged": 1, "resolved": 0}

    warn_delta_scope(True, has_status_column, status_by_id, row_count, tier_ids)
    err = capsys.readouterr().err
    assert (
        "Section 7 status IDs differ from tier finding IDs "
        "(1 only-in-map, 1 only-in-tier)"
    ) in err


def test_warn_delta_scope_missing_status_column_on_baseline(capsys):
    warn_delta_scope(True, False, {}, 0, set())
    err = capsys.readouterr().err
    assert "baseline run but threats.md Section 7 has no Status column" in err


def test_warn_delta_scope_empty_map_with_rows(capsys):
    warn_delta_scope(True, True, {}, 3, {"X-1"})
    err = capsys.readouterr().err
    assert "Section 7 has 3 rows but no readable Finding ID/Status pairs" in err


def test_warn_delta_scope_unknown_status_after_normalization(capsys):
    warn_delta_scope(True, True, {"Z-9": "RESOLVED"}, 1, {"Z-9"})
    err = capsys.readouterr().err
    assert "1 Section 7 statuses are not NEW/UPDATED/UNCHANGED after normalization" in err
    assert "Z-9='RESOLVED'" in err


def test_warn_delta_scope_never_raises_and_is_silent_when_not_baseline(capsys):
    # Never raises, even on ragged input; silent unless has_baseline.
    warn_delta_scope(False, False, {}, 0, None)
    warn_delta_scope(False, True, {"A": "NEW"}, 1, None)
    assert capsys.readouterr().err == ""


def test_apply_delta_status_stamps_badges_only_not_counts():
    # AR-3/NM-1: apply_delta_status writes per-finding delta_status for
    # badge/top_findings display only; it must play no part in
    # compute_delta_counts, which reads the map directly.
    findings = [{"id": "F-1", "threat": "x"}, {"id": "F-9", "threat": "y"}]
    status_by_id = {"F-1": "NEW"}
    apply_delta_status(findings, status_by_id)
    assert findings[0]["delta_status"] == "NEW"
    assert "delta_status" not in findings[1]


def test_parse_resolved_findings_accepts_4b_and_4c_and_skips_placeholder():
    for subdir in ("baseline_resolved_4c", "baseline_resolved_4b_legacy"):
        content = _read_fixture(subdir, "threats.md")
        resolved = parse_resolved_findings(content)
        assert [f["id"] for f in resolved] == ["F-7", "F-8"]
        assert all(f["delta_status"] == "RESOLVED" for f in resolved)


def test_parse_resolved_findings_absent_returns_empty_list():
    assert parse_resolved_findings("# Threat Model\n\nno resolved section here\n") == []


# =============================================================================
# Pins (L4): parse_markdown_table's level-aware stop rule leaves every
# pre-existing caller unaffected. For a match on a non-heading line (the
# three bare-substring callers below), the rule is byte-for-byte the old
# one. For a match on a level-2 heading (the representative "##" caller
# and scripts/generate-risk-scores-sarif.py's two callers, named explicitly
# by FR-K9.2), "stop at the next heading of level <= max(matched_level, 2)"
# reduces to "stop at the next '##'/'#' line" — the old hardcoded rule —
# so these are unaffected by construction, proven here even across an
# intervening deeper heading. A level-1 match (a document title) is NOT
# the same reduction: RC-3 clamps it to level 2 as well, but for a
# different reason (architect finding F-1) — see
# test_pin_risk_summary_matching_document_title_stops_at_next_h2, beside
# the empty-H3-band test above.
# =============================================================================

_SEVERITY_DISTRIBUTION_SNIPPET = """\
## 1. Executive Summary

Some narrative text.

**Severity Distribution:**

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 2 |

### Column Definitions

Prose under a deeper heading that must not be mistaken for a stop boundary.

## 2. Scored Threat Table
"""


def test_pin_severity_distribution_bold_paragraph_caller_unaffected():
    # tachi_parsers.parse_risk_scores_severity's "Severity Distribution"
    # fallback (risk-scores.md:64 renders it as bold paragraph text, never
    # a heading).
    rows = parse_markdown_table(_SEVERITY_DISTRIBUTION_SNIPPET, "Severity Distribution")
    assert [r["Severity"] for r in rows] == ["Critical", "High"]


_COVERAGE_DISTRIBUTION_SNIPPET = """\
## 1. Executive Summary

**Coverage Distribution:**

| Status | Count |
|--------|-------|
| Found | 2 |
| Partial | 1 |

### Some Subheading

Prose under a deeper heading that must not be mistaken for a stop boundary.

## 2. Coverage Matrix
"""


def test_pin_coverage_distribution_bold_paragraph_caller_unaffected():
    # tachi_parsers.parse_compensating_controls_md's "Coverage Distribution"
    # fallback (compensating-controls.md:62 renders it as bold paragraph
    # text, never a heading).
    rows = parse_markdown_table(_COVERAGE_DISTRIBUTION_SNIPPET, "Coverage Distribution")
    assert [r["Status"] for r in rows] == ["Found", "Partial"]


_RISK_SUMMARY_BARE_SNIPPET = """\
## Risk Summary

### A Deeper Note Before The Table

Prose under a deeper heading that must not be mistaken for a stop boundary.

| Risk Level | Count |
|------------|-------|
| Critical | 0 |
| High | 1 |
| Medium | 0 |
| Low | 0 |

## 7. Recommended Actions
"""


def test_pin_risk_summary_bare_substring_caller_unaffected():
    # tachi_parsers.parse_threats_severity's last-resort "Risk Summary"
    # fallback (a bare substring, no "##"/"6." prefix) — for a non-numbered
    # heading spelling. It must still find the table beyond an intervening
    # "### A Deeper Note..." heading, exactly as before this fix (a
    # level-2 match reduces to the old hardcoded rule).
    rows = parse_markdown_table(_RISK_SUMMARY_BARE_SNIPPET, "Risk Summary")
    assert [r["Risk Level"] for r in rows] == ["Critical", "High", "Medium", "Low"]


_HASH2_CALLER_SNIPPET = """\
## 7. Recommended Actions

| Finding ID | Status |
|------------|--------|
| F-1 | NEW |
| F-2 | UPDATED |

### Some Deeper Note

Prose under a deeper heading that must not be mistaken for a stop boundary.

## 8. Delta Summary
"""


def test_pin_representative_hash2_caller_unaffected_by_intervening_h3():
    # A representative existing "##" caller — data-model.md's own "## 7.
    # Recommended Actions", used by parse_threats_findings and
    # delta_status_by_id.
    rows = parse_markdown_table(_HASH2_CALLER_SNIPPET, "## 7. Recommended Actions")
    assert [r["Finding ID"] for r in rows] == ["F-1", "F-2"]


_SARIF_RISK_SCORES_SNIPPET = """\
## 2. Scored Threat Table

Findings sorted by Composite score descending.

### A Deeper Note Before The Table

Prose a future template revision might insert here, between the section
heading and its table.

| ID | Composite |
|----|-----------|
| T-1 | 8.0 |
| T-2 | 6.0 |

## 3. Dimensional Breakdown

Per-finding detail.

## 4. Governance Fields

Remediation tracking metadata.

### A Deeper Note Before The Table

More such prose.

| ID | Owner |
|----|-------|
| F-1 | alice |

## 5. Scoring Methodology
"""


def test_pin_generate_risk_scores_sarif_scored_threat_table_unaffected():
    # scripts/generate-risk-scores-sarif.py:53 — the fourth consumer of
    # parse_markdown_table named explicitly by FR-K9.2. Not imported here
    # (a hyphenated filename, and it adds no logic of its own beyond this
    # call); the shared function this fix touches is exercised directly,
    # with the exact header string that call site uses.
    rows = parse_markdown_table(_SARIF_RISK_SCORES_SNIPPET, "## 2. Scored Threat Table")
    assert [r["ID"] for r in rows] == ["T-1", "T-2"]


def test_pin_generate_risk_scores_sarif_governance_fields_unaffected():
    # scripts/generate-risk-scores-sarif.py:139, same rationale.
    rows = parse_markdown_table(_SARIF_RISK_SCORES_SNIPPET, "## 4. Governance Fields")
    assert [r["ID"] for r in rows] == ["F-1"]


# =============================================================================
# Feature 373 K11: classify_control_status, the inherent read + join, the
# residual clamp, and band fallbacks (data-model.md §3; T020)
# =============================================================================

def test_classify_control_status_application_order():
    # Application order (data-model.md §3; spec ruling S-5): partial-prefix,
    # then the silent whole-string set, then found-with-no-negation, then
    # else-warns.
    assert classify_control_status("Partially Found") == ("partial", False)  # prefix wins
    assert classify_control_status("Partial Control") == ("partial", False)
    assert classify_control_status("No Control Found") == ("none", False)  # silent set
    assert classify_control_status("Missing") == ("none", False)
    assert classify_control_status("Not Found") == ("none", False)
    assert classify_control_status("None") == ("none", False)
    assert classify_control_status("Control Found") == ("found", False)
    assert classify_control_status("Control Found (implemented)") == ("found", False)
    assert classify_control_status("None found") == ("none", True)  # found + negation token
    assert classify_control_status("") == ("none", True)
    assert classify_control_status("Foobar") == ("none", True)  # no whole "found" token


def test_shortform_fixture_inherent_and_control_status_now_resolve():
    # Extends the K9 short-form fixture (T016) with K11's aliases: "Inherent"
    # and "Status" now resolve too, and classify_control_status replaces the
    # raw substring reads.
    content = _read_fixture("controls_bands_shortform", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    t1, t2 = data["findings"]
    assert t1["id"] == "T-1"
    assert t1["inherent"] == Decimal("8.0")
    assert t1["inherent_severity"] == "High"
    assert t1["status_class"] == "none"  # "No Control Found" -> silent
    assert t2["id"] == "T-2"
    assert t2["inherent"] == Decimal("6.5")
    assert t2["inherent_severity"] == "Medium"
    assert t2["status_class"] == "found"  # "Control Found"


def test_funnel_join_inherent_less_fills_inherent_by_id_join():
    # US-3b #6; architect finding F2: a Coverage Matrix with no Inherent
    # Score/Inherent column at all is filled by ID join to the sibling
    # risk-scores.md composites.
    content = _read_fixture("funnel_join_inherent_less", "compensating-controls.md")
    composites = _composites_from_fixture("funnel_join_inherent_less")
    assert composites == {"T-1": Decimal("8.0"), "T-2": Decimal("7.0")}

    data = parse_compensating_controls_md(content, composites_by_id=composites)
    t1, t2 = data["findings"]
    assert t1["id"] == "T-1"
    assert t1["status_class"] == "found"
    assert t1["inherent"] == Decimal("8.0")
    assert t1["residual_score"] == "7.5"
    assert t1["residual_severity"] == "High"
    assert t2["id"] == "T-2"
    assert t2["status_class"] == "partial"
    assert t2["inherent"] == Decimal("7.0")
    assert t2["residual_score"] == "6.6"
    assert t2["residual_severity"] == "Medium"


def test_funnel_join_inherent_less_without_composites_leaves_inherent_none():
    # Without a composites_by_id, the join simply can't happen — inherent
    # stays None (no crash), matching today's pre-K11 gap being closed.
    content = _read_fixture("funnel_join_inherent_less", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    assert all(f["inherent"] is None for f in data["findings"])


def test_funnel_step_bound_row_level_fields():
    # US-3b #1 fixture, at the row level (T021's funnel computation is
    # pinned in test_extract_infographic_data.py; this only proves T020's
    # parsed rows are what T021 needs).
    content = _read_fixture("funnel_step_bound", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    t1, t2 = data["findings"]
    assert t1["status_class"] == "found"
    assert t1["inherent"] == Decimal("8.0")
    assert t1["residual_score"] == "7.9"
    assert t2["status_class"] == "partial"
    assert t2["inherent"] == Decimal("8.0")
    assert t2["residual_score"] == "7.8"


def test_controls_warnings_kitchen_sink_status_classification_and_clamp(capsys):
    # The five T003 warning bullets combined (data-model.md §3, §4.5):
    # control-status variants, unparseable scores, residual above inherent,
    # and the join-miss path. Section 1 comparand / row-count-mismatch
    # warnings belong to T021 (the funnel), not this parser-level test.
    content = _read_fixture("controls_warnings_kitchen_sink", "compensating-controls.md")
    composites = _composites_from_fixture("controls_warnings_kitchen_sink")
    data = parse_compensating_controls_md(content, composites_by_id=composites)
    by_id = {f["id"]: f for f in data["findings"]}

    # by classify_control_status outcome (fixtures README's own table):
    assert by_id["W-1"]["status_class"] == "none"       # "Missing" (silent)
    assert by_id["W-2"]["status_class"] == "none"        # empty (warns)
    assert by_id["W-3"]["status_class"] == "none"        # "Foobar" (warns)
    assert by_id["W-4"]["status_class"] == "partial"      # "Partially Found"
    assert by_id["W-5"]["status_class"] == "none"        # "None found" (warns)
    assert by_id["W-6"]["status_class"] == "found"        # "Control Found"
    assert by_id["W-7"]["status_class"] == "none"        # "No Control Found" (silent)
    assert by_id["W-8"]["status_class"] == "partial"      # "Partial Control"
    assert by_id["W-9"]["status_class"] == "none"        # "No Control Found" (silent)
    assert by_id["W-10"]["status_class"] == "found"       # "Control Found"

    # W-6/W-7: unparseable residual (em dash / trailing text) defaults to
    # the (parseable) inherent score, no credit.
    assert by_id["W-6"]["inherent"] == Decimal("8.0")
    assert by_id["W-6"]["residual_score"] == "8.0"
    assert by_id["W-7"]["inherent"] == Decimal("7.2")
    assert by_id["W-7"]["residual_score"] == "7.2"

    # W-9: residual (9.5) clamped to inherent (8.0), band from the clamped
    # value.
    assert by_id["W-9"]["inherent"] == Decimal("8.0")
    assert by_id["W-9"]["residual_score"] == "8.0"
    assert by_id["W-9"]["residual_severity"] == "High"

    # W-8: unparseable inherent ("NaN") with no risk-scores.md entry to join
    # (row-count mismatch by design) — stays None, band falls back to the
    # (also blank) Inherent Severity column.
    assert by_id["W-8"]["inherent"] is None
    assert by_id["W-8"]["inherent_severity"] is None
    assert by_id["W-8"]["residual_score"] == "5.0"  # its own residual parses fine

    err = capsys.readouterr().err
    assert "3 controls rows have an unrecognized or empty status (first: W-2, W-3, W-5)" in err
    assert (
        "3 unparseable scores (first: W-6:Residual Score, W-7:Residual Score, "
        "W-8:Inherent Score)"
    ) in err
    assert "1 controls rows have a residual above the inherent score (first: W-9); clamped" in err
    assert (
        "2 controls rows have no residual score (first: W-6, W-7); "
        "defaulted to the inherent score (no credit)"
    ) in err
    assert (
        "1 controls rows have no inherent score (first: W-8); "
        "excluded from funnel volumes"
    ) in err


def test_posture_mmdc_free_residual_severity_counts():
    # K11's own row-level output on the fixture T025's stale-data gate also
    # uses (test_report_posture_contract.py); compute_risk_posture is
    # exercised on it below (T024).
    content = _read_fixture("posture_mmdc_free", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    assert data["severity"] == {
        "critical": 0, "high": 1, "medium": 1, "low": 1, "note": 0, "total": 3,
    }


# =============================================================================
# Feature 373 K13-posture: compute_risk_posture (data-model.md §5; T024)
# =============================================================================

def test_compute_risk_posture_zero_findings_is_low():
    # D-3: zero findings (an all-zero counts dict) gives low/LOW RISK.
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "note": 0, "total": 0}
    assert compute_risk_posture(counts) == ("low", "LOW RISK")


def test_compute_risk_posture_takes_the_highest_non_zero_band():
    assert compute_risk_posture({"critical": 1, "high": 5, "medium": 5}) == ("critical", "CRITICAL RISK")
    assert compute_risk_posture({"critical": 0, "high": 1, "medium": 5}) == ("high", "HIGH RISK")
    assert compute_risk_posture({"critical": 0, "high": 0, "medium": 1}) == ("medium", "MODERATE RISK")
    assert compute_risk_posture({"critical": 0, "high": 0, "medium": 0, "low": 9}) == ("low", "LOW RISK")


def test_compute_risk_posture_runs_on_post_clamp_counts_from_a_real_parse():
    # End-to-end: posture_mmdc_free's residual severity counts (post-clamp,
    # since K11 ships) give critical=0, high=1 -> the highest non-zero band
    # is High.
    content = _read_fixture("posture_mmdc_free", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    assert compute_risk_posture(data["severity"]) == ("high", "HIGH RISK")


# =============================================================================
# Feature 374 (W1, T018): the reference finding set (S-12, FR-E.16)
#
# parse_reference_set wraps parse_threats_findings. It reads Section 7's table form (T032 adds the
# drift forms), checks every ID against tachi_parts' allow-list, builds each finding once, and raises
# ReferenceSetError on anything it can't read, so a run ends before any agent is dispatched.
# =============================================================================

_REF_HEADER = (
    "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |\n"
    "|---|---|---|---|---|---|---|---|---|"
)


def _ref_row(finding_id, status="NEW", component="Gateway", threat="A threat", risk="High"):
    return "| %s | %s | Spoofing | \u2014 | %s | L4 | %s | %s | A fix |" % (finding_id, status, component, threat, risk)


def _ref_md(rows, resolved=(), header=_REF_HEADER, heading="## 7. Recommended Actions"):
    """A small threats.md: Section 4c (when ``resolved`` is given) and Section 7 over ``rows``."""
    parts = ["# Report\n\n## 1. Overview\n\nText.\n"]
    if resolved:
        parts.append("## 4c. Resolved Findings\n\n| ID | Component | Threat | Last Risk Level | Resolution Reason |\n"
                     "|----|-----------|--------|-----------------|-------------------|\n" + "\n".join(
                         "| %s | Old | An old threat | High | Removed |" % fid for fid in resolved) + "\n")
    if heading is not None:
        parts.append(heading + "\n\n" + (header + "\n" + "\n".join(rows) + "\n" if header else "Nothing is listed here.\n"))
    return "\n".join(parts)


def test_markdown_table_reports_the_rows_it_drops_only_when_asked(capsys):
    content = "## 7. Recommended Actions\n\n| A | B | C |\n|---|---|---|\n| 1 | 2 | 3 |\n| short |\n| 4 | 5 | 6 |\n| also | short |\n"
    skipped = []
    rows = parse_markdown_table(content, "## 7. Recommended Actions", skipped=skipped)
    assert [row["A"] for row in rows] == ["1", "4"]
    assert skipped == [6, 8], "1-based line numbers of the rows that were dropped"
    assert capsys.readouterr().err.count("skipping malformed row") == 2
    assert parse_markdown_table(content, "## 7. Recommended Actions") == rows, "the default is as it always was"


def test_reference_set_reads_section_7_and_section_4c_in_s2_order(capsys):
    """Open findings come in S-2 order, with each ID spelled as the file spells it. Section 4c's come as resolved."""
    content = _ref_md([_ref_row("T-10", "UNCHANGED"), _ref_row("S-2", "[UPDATED]"), _ref_row("AGP-01", "NEW", "Agent"),
                       _ref_row("T-9", "NEW"), _ref_row("LLM-3", "NEW")], resolved=["R-4", "E-1"])
    reference = parse_reference_set(content, source="run/threats.md")
    assert [finding["id"] for finding in reference["open"]] == ["S-2", "T-9", "T-10", "AGP-01", "LLM-3"]
    assert [finding["id"] for finding in reference["resolved"]] == ["R-4", "E-1"]
    assert reference["duplicates"] == []
    first = reference["open"][0]
    assert (first["component"], first["threat"], first["risk_level"], first["mitigation"]) == ("Gateway", "A threat", "High", "A fix")
    assert first["delta_status"] == "UPDATED", "the Status cell is normalized, as the other readers do"
    assert reference["open"][3]["agentic_pattern"] == "none" and reference["open"][3]["component"] == "Agent"
    assert capsys.readouterr().err == "", "a readable file prints nothing"


def test_reference_set_resolved_is_empty_without_section_4c_and_accepts_the_legacy_4b_heading():
    assert parse_reference_set(_ref_md([_ref_row("S-1")]))["resolved"] == []
    legacy = _ref_md([_ref_row("S-1")]).replace("## 1. Overview", "## 4b. Resolved Findings\n\n| ID | Component | Threat | Last Risk Level | Resolution Reason |\n"
                                                 "|----|---|---|---|---|\n| T-2 | Old | Old | Low | Gone |\n\n## 1. Overview")
    assert [finding["id"] for finding in parse_reference_set(legacy)["resolved"]] == ["T-2"]


def test_reference_set_reads_the_older_six_column_table_and_a_table_with_no_status_column():
    content = _ref_md(["| S-1 | Gateway | A threat | High | A fix |", "| T-1 | Gateway | Another | Low | Another fix |"],
                      header="| Finding ID | Component | Threat | Risk Level | Mitigation |\n|---|---|---|---|---|")
    reference = parse_reference_set(content)
    assert [finding["id"] for finding in reference["open"]] == ["S-1", "T-1"]
    assert all("delta_status" not in finding for finding in reference["open"]), "no Status column, no delta_status"


def test_reference_set_drops_placeholder_rows_and_keeps_the_rest():
    content = _ref_md([_ref_row("S-1"), _ref_row("\u2014"), _ref_row(""), _ref_row("T-1")])
    assert [finding["id"] for finding in parse_reference_set(content)["open"]] == ["S-1", "T-1"]


@pytest.mark.parametrize("problem,content", [
    ("is missing", _ref_md([], heading=None)),
    ("holds no table rows", _ref_md([], header=None)),
    ("holds no table rows", _ref_md([])),
    ("has no 'Finding ID' column", _ref_md(["| S-1 | NEW | x | y | z |"], header="| ID | Status | Component | Threat | Mitigation |\n|---|---|---|---|---|")),
    ("lists no findings", _ref_md([_ref_row("\u2014"), _ref_row("-")])),
    ("which is not a finding ID", _ref_md([_ref_row("S-1"), _ref_row("X-9")])),
    ("which is not a finding ID", _ref_md([_ref_row("S-1a")])),
    ("which is not a finding ID", _ref_md([_ref_row("S-\u0661")])),
    ("which is not a finding ID", _ref_md([_ref_row("S-1234567")])),
    ("has a malformed row", _ref_md([_ref_row("S-1"), "| T-1 | NEW | too few cells |"])),
], ids=["no-section", "no-table", "header-only", "no-id-column", "only-placeholders", "unknown-prefix",
        "trailing-letter", "unicode-digit", "seven-digits", "short-row"])
def test_reference_set_raises_on_anything_it_cannot_read(problem, content):
    """S-12(c): the run ends before dispatch. An empty extraction is an error, never a pass (KB 22)."""
    with pytest.raises(ReferenceSetError) as raised:
        parse_reference_set(content, source="run/threats.md")
    error = raised.value
    assert problem in error.reason
    assert error.reason.startswith("run/threats.md: Section 7 (Recommended Actions) ")
    assert "'Finding ID' column" in error.expected and error.remedy
    assert str(error) == "%s. Expected %s. Remedy: %s" % (error.reason, error.expected, error.remedy)


def test_reference_set_raises_on_a_resolved_id_that_is_not_a_finding_id():
    with pytest.raises(ReferenceSetError) as raised:
        parse_reference_set(_ref_md([_ref_row("S-1")], resolved=["T-2", "bogus"]))
    assert "Section 4c (Resolved Findings)" in raised.value.reason and "'bogus'" in raised.value.reason


def test_reference_set_error_never_echoes_a_long_id():
    with pytest.raises(ReferenceSetError) as raised:
        parse_reference_set(_ref_md([_ref_row("S-" + "9" * 500)]))
    assert len(raised.value.reason) < 300


def test_reference_set_holds_each_finding_once_the_first_row_wins_and_the_repeats_are_reported():
    """D-4. Two spellings of one canonical ID are one finding. An open finding beats a resolved one."""
    content = _ref_md([_ref_row("AGP-01", threat="first"), _ref_row("T-1"), _ref_row("AGP-1", threat="second"),
                       _ref_row("T-1", threat="third")], resolved=["T-1", "R-1", "R-01"])
    reference = parse_reference_set(content)
    assert [(finding["id"], finding["threat"]) for finding in reference["open"]] == [("T-1", "A threat"), ("AGP-01", "first")]
    assert [finding["id"] for finding in reference["resolved"]] == ["R-1"]
    assert reference["duplicates"] == ["T-1", "R-1", "AGP-1"], "each repeated canonical ID once, in S-2 order"


def test_reference_set_agrees_with_the_wrapped_parser_on_a_shipped_sample():
    content = (REPO_ROOT / "examples" / "agentic-app" / "sample-report" / "threats.md").read_text(encoding="utf-8")
    reference = parse_reference_set(content, source="sample")
    wrapped = [finding for finding in parse_threats_findings(content) if not is_placeholder_id(finding["id"])]
    assert len(reference["open"]) == len(wrapped) > 20
    assert {finding["id"] for finding in reference["open"]} == {finding["id"] for finding in wrapped}
    assert sorted(reference["open"], key=lambda finding: finding["id"]) == sorted(wrapped, key=lambda finding: finding["id"])
    assert reference["duplicates"] == []


def test_reference_set_uses_the_first_row_of_a_shipped_sample_that_lists_one_finding_twice():
    """``maestro-reference``'s Section 7 lists I-17 twice. A shipped example must keep working (NFR-1), so the wrapper
    reports the repeat instead of refusing the file."""
    content = (REPO_ROOT / "examples" / "maestro-reference" / "threats.md").read_text(encoding="utf-8")
    reference = parse_reference_set(content, source="maestro-reference")
    assert reference["duplicates"] == ["I-17"]
    ids = [finding["id"] for finding in reference["open"]]
    assert ids.count("I-17") == 1 and len(ids) == len(set(ids))
    kept = next(finding for finding in reference["open"] if finding["id"] == "I-17")
    assert "detailed error messages" in kept["threat"], "the first of the two rows"


def test_the_wrapped_parser_keeps_its_empty_list_and_warning_for_the_extractors(capsys):
    """S-12: ``parse_threats_findings`` is unchanged, because the extractors rely on ``[]`` with a warning."""
    assert parse_threats_findings("# no section seven here\n") == []
    assert "could not find Recommended Actions table" in capsys.readouterr().err


# =============================================================================
# Feature 374 (W2, T033): the shared reference decoder (ADR-050 D3)
#
# decode_references reverses exactly the references that tachi_parts escapes (ESCAPE_REFERENCES), in one pass. A
# reader runs it once on each value, after the row is split on raw "|": parse_markdown_table and every other
# reader of rendered text, the extractors' own table readers included. GFM's "\|" is not decoded, so today's
# examples parse as they always did (NFR-1).
# =============================================================================

# The closed set as D3 lists it, written out here so that a change to tachi_parts.ESCAPE_REFERENCES fails this file.
_CLOSED_REFERENCES = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">", "&#124;": "|", "&#96;": "`", "&#123;": "{", "&#10;": "\n", "&#35;": "#",
    "&#126;": "~"}
_ESCAPERS = {
    "cell": lambda text: tachi_parts.escape_cell(text),
    "cell-keeping-slots": lambda text: tachi_parts.escape_cell(text, keep_slots=True),
    "prose": lambda text: tachi_parts.escape_prose(text),
    "prose-keeping-slots": lambda text: tachi_parts.escape_prose(text, keep_slots=True),
}
_ROUND_TRIP_TEXTS = [
    "", "plain words", "a & b", "a | b || c", "if a < b && b > c", "`code` {{7*7}} {{{x}}", "two\nlines\n# not a heading",
    "# heading first\n  # indented\n\t# tabbed\n| row", "{{score:cvss_base}}", "{{{score:cvss_base}}", "{{score:", "}}{{",
    "a literal &lt; here", "tail &amp;lt; tail", "&#124; &#10; &#35; &#96; &#123; spelled out", "&amp;", "\n", "&", "<<>>",
    "```", "||", "{{", "{", "#", "x {{name:component}} y {{score:cvss_base}}",
    # P0-1: a prose line that starts with `~` is written `&#126;`; a `~` anywhere else, and a literal reference, are not
    "~~~", " ~~~", "\t~~~\nx", "first\n~~~\n  ~~~ tail", "~", "a ~ b", "x~~~", "~~~\n# h\n| row\n~~~",
    "&#126; and &amp;#126; spelled out",
]


def _generated_texts(count=400):
    """Texts built from the characters the escapers care about, with literal references among them. Seeded."""
    rng = random.Random(374)
    tokens = ["a", "b", "x", " ", "\t", "\n", "&", "<", ">", "|", "`", "{", "{{", "}", "}}", ":", "#", ";", "amp", "lt",
              "#124", "#10", "&amp;", "&lt;", "&#124;", "&#35;", "{{score:cvss_base}}", "{{name:component}}"]
    return ["".join(rng.choice(tokens) for _ in range(rng.randint(1, 12))) for _ in range(count)]


def test_the_decoder_reads_the_closed_set_that_tachi_parts_escapes():
    assert tachi_parts.ESCAPE_REFERENCES == _CLOSED_REFERENCES
    for reference, char in _CLOSED_REFERENCES.items():
        assert decode_references(reference) == char
        assert decode_references("a%sb%sc" % (reference, reference)) == "a%sb%sc" % (char, char)
    assert decode_references("&lt;b&gt;x&lt;/b&gt; &amp;&amp;") == "<b>x</b> &&"
    assert decode_references("") == ""


def test_the_decoder_reads_the_tilde_reference_through_the_same_closed_table():
    """P0-1: ``&#126;`` is the ninth reference. The decoder takes it from ``tachi_parts``, so it has no table of its own."""
    assert len(tachi_parts.ESCAPE_REFERENCES) == 9 and tachi_parts.ESCAPE_REFERENCES["&#126;"] == "~"
    assert decode_references("&#126;") == "~"
    assert decode_references("&#126;~~") == "~~~"
    assert decode_references("&#126;&#126;&#126;") == "~~~"
    assert decode_references("approx &#126;5 users, &#126; and &amp; &#124;") == "approx ~5 users, ~ and & |"
    assert decode_references("first\n  &#126;~~ fence\nlast") == "first\n  ~~~ fence\nlast"


def test_the_references_the_escapers_write_are_exactly_the_ones_the_decoder_reads():
    """No more and no fewer: between them, escape_cell and escape_prose write each reference of the set, and no other."""
    probe = "&<>|`{{\n# x\n~ y"
    written = set()
    for escape in (tachi_parts.escape_cell, tachi_parts.escape_prose):
        written.update(re.findall(r"&[#A-Za-z0-9]+;", escape(probe)))
    assert written == set(_CLOSED_REFERENCES)


@pytest.mark.parametrize("text,expected", [
    ("&amp;lt;", "&lt;"), ("&amp;amp;", "&amp;"), ("&amp;#124;", "&#124;"), ("&amp;#10;", "&#10;"),
    ("&amp;gt;&amp;lt;", "&gt;&lt;"), ("&#38;lt;", "&#38;lt;"), ("&&lt;", "&<"), ("&amp;&lt;", "&<"),
    ("&amp;#126;", "&#126;"), ("&amp;&#126;", "&~"), ("&#126;&amp;#126;", "~&#126;"),
])
def test_the_decoder_is_one_pass_and_never_scans_replaced_text(text, expected):
    assert decode_references(text) == expected


@pytest.mark.parametrize("text", [
    "&AMP;", "&Lt;", "&GT;", "&quot;", "&apos;", "&nbsp;", "&copy;", "&#x7c;", "&#X7C;", "&#0124;", "&#124", "&#12;", "&#1;",
    "&#38;", "&#60;", "&#62;", "&#x26;", "&#036;", "&#35", "&#x23;", "&#9;", "&amp", "&lt", "& amp;", "&;", "&#;", "&",
    ";", "#", "\\|", "a \\| b",
    "&#126", "&#x7e;", "&#X7E;", "&#0126;", "&#1260;", "&#127;", "&tilde;", "&Tilde;", "~", "~~~", "a ~ b",
])
def test_the_decoder_leaves_every_other_text_as_written(text):
    assert decode_references(text) == text


@pytest.mark.parametrize("name", sorted(_ESCAPERS))
def test_decoding_what_tachi_parts_escapes_gives_the_text_back(name):
    """The round trip: escape, then decode, is the identity. So escaping never compounds across two runs either."""
    escape = _ESCAPERS[name]
    for text in _ROUND_TRIP_TEXTS + _generated_texts():
        escaped = escape(text)
        assert decode_references(escaped) == text, repr(text)
        assert escape(decode_references(escaped)) == escaped, "a carried value is written the same bytes again: %r" % text
        for ampersand in re.finditer("&", escaped):
            assert escaped.startswith(tuple(_CLOSED_REFERENCES), ampersand.start()), \
                "every & the escapers write starts one reference of the set: %r" % text


def test_a_second_decode_corrupts_a_literal_reference():
    """ADR-050 D16: the round trip includes a literal ``&lt;`` in agent text, so a double decode fails it."""
    text = "compare a &lt; b before the &amp; step"
    escaped = tachi_parts.escape_cell(text)
    assert escaped == "compare a &amp;lt; b before the &amp;amp; step"
    once = decode_references(escaped)
    assert once == text
    assert decode_references(once) == "compare a < b before the & step" != text


def test_resolved_slot_values_decode_to_the_values():
    """``resolve_narrative`` escapes the value it fills in. Reading it back gives the value, and a slot-like value stays text."""
    values = {("name", "component"): "Gate & <Way> | “edge”", ("score", "cvss_base"): "9.1"}
    resolved = tachi_parts.resolve_narrative("Reaches {{name:component}} at {{score:cvss_base}} now", "risk-score",
                                             lambda kind, argument: values.get((kind, argument)))
    assert "&amp;" in resolved and "&lt;Way&gt;" in resolved and "&#124;" in resolved
    assert decode_references(resolved) == "Reaches Gate & <Way> | “edge” at 9.1 now"


# ---- the table readers ---------------------------------------------------------------------------------------

_TABLE_VALUES = [
    "plain words", "a | b || c", "if a < b && b > c", "two\nlines\nof text", "`code` and {{7*7}} and {{{x}}",
    "already &lt;escaped&gt; &amp; &#124; &#10; text", "tail &amp;lt; tail", "# looks like a heading", "&", "{{score:cvss_base}}",
    "&#35;", "~~~ in a cell", "&#126;",
]


def test_a_table_read_back_gives_each_cell_as_it_was_written():
    rows = [("S-%d" % (index + 1), value, "fix: " + value) for index, value in enumerate(_TABLE_VALUES)]
    content = "## 7. Recommended Actions\n\n| ID | Threat | Mitigation |\n|----|--------|------------|\n" + "\n".join(
        "| %s | %s | %s |" % (finding_id, tachi_parts.escape_cell(threat), tachi_parts.escape_cell(mitigation))
        for finding_id, threat, mitigation in rows) + "\n"
    parsed = parse_markdown_table(content, "## 7. Recommended Actions")
    assert [(row["ID"], row["Threat"], row["Mitigation"]) for row in parsed] == rows
    assert parse_markdown_table(content, "## 7. Recommended Actions") == parsed, "reading twice is reading once"


def test_a_reference_never_splits_a_row_and_decoding_never_changes_its_cell_count(capsys):
    content = "## 7. X\n\n| ID | Threat | Mitigation |\n|---|---|---|\n| S-1 | a &#124; b &#124;&#124; c | &#124; |\n"
    skipped = []
    rows = parse_markdown_table(content, "## 7. X", skipped=skipped)
    assert rows == [{"ID": "S-1", "Threat": "a | b || c", "Mitigation": "|"}]
    assert skipped == [] and capsys.readouterr().err == ""


def test_a_header_cell_is_a_cell_and_is_decoded_too():
    content = "## 7. X\n\n| ID | Threat &amp; Impact |\n|---|---|\n| S-1 | text |\n"
    assert parse_markdown_table(content, "## 7. X") == [{"ID": "S-1", "Threat & Impact": "text"}]


def test_gfm_escaped_pipe_is_not_decoded_the_row_splits_there_as_it_always_has():
    content = "## 7. X\n\n| ID | Threat | Mitigation |\n|---|---|---|\n| S-1 | not {{ a\\|safe }} | fix |\n"
    assert parse_markdown_table(content, "## 7. X") == [{"ID": "S-1", "Threat": "not {{ a\\", "Mitigation": "safe }}"}]


@pytest.mark.parametrize("relative", ["agentic-app/sample-report/threats.md", "agentic-app/threats.md"])
def test_the_shipped_rows_that_hold_a_gfm_pipe_parse_as_they_always_did(relative):
    """NFR-1, ADR-050 D3: LLM-5's Mitigation holds ``{{ value\\|safe }}`` (sample-report/threats.md:315, threats.md:230).

    The row has 12 raw cells for 11 columns. Its Mitigation ends at the backslash, the 12th cell is dropped, and no
    cell is changed by the decoder."""
    content = (REPO_ROOT / "examples" / relative).read_text(encoding="utf-8")
    lines = content.split("\n")
    at = [index for index, line in enumerate(lines) if "{{ value\\|safe }}" in line]
    assert len(at) == 1 and lines[at[0]].startswith("| LLM-5 |")
    heading = max(index for index in range(at[0]) if lines[index].startswith("#"))
    row = next(row for row in parse_markdown_table(content, start_line=heading) if row["ID"] == "LLM-5")
    raw = [strip_bold(cell.strip()) for cell in lines[at[0]].split("|")[1:-1]]
    assert len(raw) == 12 and raw[10].endswith("not `{{ value\\") and raw[11].startswith("safe }}`)")
    assert list(row.values()) == raw[:11]


def test_find_table_with_column_decodes_its_cells_and_skips_the_table_without_the_column():
    content = ("## 6. Risk Summary\n\n| Calibration | Note |\n|---|---|\n| a | b |\n\n"
               "| Risk Level | Count | Note |\n|---|---|---|\n| Critical | 2 | x &lt; y |\n| High | 1 | a &#124; b |\n")
    assert _find_table_with_column(content, "## 6. Risk Summary", "Risk Level") == [
        {"Risk Level": "Critical", "Count": "2", "Note": "x < y"}, {"Risk Level": "High", "Count": "1", "Note": "a | b"}]


# ---- the other readers of rendered text ----------------------------------------------------------------------

_CONTROLS_WITH_REFERENCES = """\
## 2. Coverage Matrix

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent | Inherent Severity | Status | Residual | Residual Sev. |
|-----------|-----|-----------|--------|----------|--------------------|--------|----------|---------------|
| T-1 | — | API &amp; Gateway | Input &lt;script&gt; reaches a &#96;sink&#96; &#124; unsanitized | 8.0 | High | No Control Found | 8.0 | High |

## 3. Control Details

### Input Validation

#### CTRL-1 — Allow-list validation

**Category**: Input Validation | **Status**: Found | **Effectiveness**: Medium

**Detected in**: `src/a&amp;b&#96;c.py:12`

**Threats Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| T-1 | Gate &amp; Way | A threat | 8.0 | 0.5 | 4.0 |
| T-9 | Other | Another threat | 6.0 | 0.5 | 3.0 |

---

## 4. Recommendations

#### 1. T-1 — API &amp; Gateway (Composite: 8.0, High)

**What to Implement**: Check against an &lt;allow-list&gt; and escape the &#124; character.
A second line keeps &amp;lt; as it was written.

**Where to Implement**: `src/a.py`
"""


def test_the_controls_reader_decodes_the_text_it_takes_from_every_section():
    data = parse_compensating_controls_md(_CONTROLS_WITH_REFERENCES)
    (finding,) = data["findings"]
    assert finding["component"] == "API & Gateway"
    assert finding["threat"] == "Input <script> reaches a `sink` | unsanitized"
    assert finding["recommendation"] == ("Check against an <allow-list> and escape the | character. "
                                         "A second line keeps &lt; as it was written.")
    assert data["controls"] == [{"component": "Gate & Way", "category": "Input Validation", "status": "Found",
                                 "evidence": "src/a&b`c.py:12", "effectiveness": "Medium"}]


_CHAINS_WITH_REFERENCES = """\
# Attack Chains

### CHAIN-001: Prompt &lt;injection&gt; to data theft

**Layers**: L2 → L3
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| S-1 | L2 | Entry | Web &amp; API | Spoofing | High |

#### Attack Progression

The attacker sends a &lt;payload&gt; and then &amp;lt; stays as written.
It continues &#124; here.

#### Chain-Breaking Controls

**Target**: S-1 (L2)
**Rationale**: Stops the &lt;entry&gt; step.
**Recommendation**: Add an allow-list &#124; filter.
"""


def test_the_chain_reader_decodes_its_prose_and_its_member_table():
    (chain,) = parse_attack_chains(_CHAINS_WITH_REFERENCES)
    assert chain["title"] == "Prompt <injection> to data theft"
    assert chain["findings"][0]["component"] == "Web & API"
    assert chain["narrative"] == "The attacker sends a <payload> and then &lt; stays as written. It continues | here."
    assert chain["chain_breaking_controls"] == [{
        "target_finding_id": "S-1", "target_layer": "L2", "rationale": "Stops the <entry> step.",
        "recommendation": "Add an allow-list | filter."}]


_AGENT_TABLE_WITH_REFERENCES = """\
### 3.1 Spoofing (S)

| ID | Status | Component | MAESTRO Layer | Risk Level | Threat |
|----|--------|-----------|---------------|------------|--------|
| S-1 | NEW | API &amp; Gateway | L2 — Data Operations | High | Token &lt;replay&gt; &#124; theft |
| S-2 | NEW | Web | L2 — Data Operations | Low | Not {{ a\\|safe }} |
"""


def test_the_report_extractors_maestro_reader_decodes_its_cells_and_keeps_a_gfm_pipe(extract_report_data):
    result = extract_report_data.parse_maestro_data(_AGENT_TABLE_WITH_REFERENCES)
    (layer,) = result["maestro_findings_by_layer"]
    assert layer["findings"] == [
        {"id": "S-1", "component": "API & Gateway", "severity": "High", "threat": "Token <replay> | theft"},
        {"id": "S-2", "component": "Web", "severity": "Low", "threat": "Not {{ a\\"}]


def test_the_infographic_extractors_readers_decode_their_cells(extract_infographic_data):
    findings = extract_infographic_data.parse_per_finding_maestro(_AGENT_TABLE_WITH_REFERENCES)
    assert [(f["id"], f["component"], f["threat"], f["risk_level"]) for f in findings] == [
        ("S-1", "API & Gateway", "Token <replay> | theft", "High"), ("S-2", "Web", "Not {{ a\\", "Low")]
    deduplicated = extract_infographic_data.deduplicate_findings(
        _AGENT_TABLE_WITH_REFERENCES + "\n## 4a. Correlation Groups\n\n| Group | Findings | Description |\n|---|---|---|\n"
        "| CG-1 | S-1, T-2 | An &amp; B |\n")
    assert deduplicated["unique_ids"] == {"S-1", "S-2", "T-2"} and deduplicated["has_correlations"] is True


def test_the_report_extractors_attack_tree_reader_decodes_the_metadata_table(extract_report_data, tmp_path):
    tree = tmp_path / "AG-1-tree.md"
    tree.write_text("# Attack Tree: AG-1 -- A title\n\n| Field | Value |\n|-------|-------|\n| Finding ID | AG-1 |\n"
                    "| Component | Web &amp; API |\n| Risk Level | High |\n| Threat | Prompt &lt;injection&gt; &#124; theft |\n\n"
                    "```mermaid\ngraph TD\n  A[\"Root\"]\n```\n", encoding="utf-8")
    entry = extract_report_data._parse_attack_tree_file(tree, {})
    assert (entry["id"], entry["component"], entry["title"], entry["severity"]) == (
        "AG-1", "Web & API", "Prompt <injection> | theft", "High")
    heading_only = tmp_path / "AG-2-tree.md"
    heading_only.write_text("# Attack Tree: AG-2 -- Prompt &lt;injection&gt;\n\n```mermaid\ngraph TD\n  A[\"Root\"]\n```\n",
                            encoding="utf-8")
    assert extract_report_data._parse_attack_tree_file(heading_only, {})["title"] == "Prompt <injection>"


def test_the_report_narrative_is_decoded_before_its_cut_so_the_cut_never_splits_a_reference(extract_report_data):
    short = "## 1. Executive Summary\n\nExposed to &lt;script&gt; &amp; more.\n\n### Remediation Timeline\n\n- **Now** (2 High findings)\n"
    result = extract_report_data.parse_threat_report_md(short)
    assert result["executive_narrative"] == "Exposed to <script> & more."
    assert result["remediation_timeline"] == [{"timeline": "Now", "count": 2, "severity": "High"}]
    long = "## 1. Executive Summary\n\n" + "x" * 1993 + "&amp;" * 4 + "\n"
    narrative = extract_report_data.parse_threat_report_md(long)["executive_narrative"]
    assert narrative == "x" * 1993 + "&" * 4, "2,013 characters written, 1,997 read: one decode, then the cut at 2,000"


# ---- every reader decodes -------------------------------------------------------------------------------------

_BINARY_EXAMPLE_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".baseline"}


def test_no_shipped_example_holds_a_reference_the_decoder_would_change():
    """ADR-050 D3: every shipped example parses as before, because none holds one of the references. Reads files only."""
    scanned, holding = [], []
    for path in sorted((REPO_ROOT / "examples").rglob("*")):
        if not path.is_file() or path.suffix.lower() in _BINARY_EXAMPLE_SUFFIXES:
            continue
        text = path.read_bytes().decode("utf-8")  # strict: a text example that isn't UTF-8 is a failure, not a skip
        scanned.append(path.relative_to(REPO_ROOT).as_posix())
        if decode_references(text) != text:
            for match in re.finditer("|".join(re.escape(reference) for reference in _CLOSED_REFERENCES), text):
                holding.append("%s:%d %s" % (scanned[-1], text.count("\n", 0, match.start()) + 1, match.group(0)))
    assert "examples/agentic-app/threats.md" in scanned and "examples/agentic-app/sample-report/threats.md" in scanned
    assert len(scanned) > 100, "the scan found the examples' text files"
    assert holding == []


def test_the_extractors_take_the_decoder_from_tachi_parsers_and_carry_no_copy(extract_report_data, extract_infographic_data):
    """One decoder. Not an identity check on the function: other modules load their own copy of ``tachi_parsers``
    under the same name, so in a mixed session the extractors can hold that copy's function."""
    for extractor in (extract_report_data, extract_infographic_data):
        assert extractor.decode_references.__module__ == "tachi_parsers"
        assert extractor.decode_references("&lt;&#124;&gt;") == "<|>"


def _is_a_split_on_a_raw_pipe(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "split"
            and len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and node.args[0].value == "|")


def _raw_pipe_splits(source):
    """``(splits, undecoded)``: the line of every ``.split("|")`` in ``source``, and those whose comprehension doesn't
    wrap its cells in ``decode_references``."""
    tree = ast.parse(source)
    decoded = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)) and any(
                isinstance(inner, ast.Call) and getattr(inner.func, "id", None) == "decode_references"
                for inner in ast.walk(node.elt)):
            decoded.update(id(inner) for generator in node.generators for inner in ast.walk(generator.iter))
    splits = [node for node in ast.walk(tree) if _is_a_split_on_a_raw_pipe(node)]
    return [node.lineno for node in splits], [node.lineno for node in splits if id(node) not in decoded]


@pytest.mark.parametrize("module,at_least", [("tachi_parsers.py", 5), ("extract-report-data.py", 3), ("extract-infographic-data.py", 4)])
def test_every_table_reader_decodes_its_cells_after_the_split_on_a_raw_pipe(module, at_least):
    """D3: the decoder runs in every reader of rendered text. A reader that splits a row on ``|`` must decode each cell."""
    splits, undecoded = _raw_pipe_splits((REPO_ROOT / "scripts" / module).read_text(encoding="utf-8"))
    assert len(splits) >= at_least, "the guard still sees this module's table readers"
    assert undecoded == [], "%s splits a row on a raw | without decode_references (lines %s)" % (module, undecoded)


def test_the_guard_flags_a_row_split_that_is_not_decoded():
    """The guard above is not vacuous: it passes a decoded comprehension and flags every other way to split a row."""
    assert _raw_pipe_splits('cells = [decode_references(c.strip()) for c in line.split("|")[1:-1]]') == ([1], [])
    assert _raw_pipe_splits('cells = [c.strip() for c in line.split("|")[1:-1]]') == ([1], [1])
    assert _raw_pipe_splits('cells = line.split("|")') == ([1], [1])
    assert _raw_pipe_splits('cells = [decode_references(c) for c in other]\nparts = line.split(",")') == ([], [])


# =============================================================================
# Feature 374 (W2, T048): the Section 4a reader, parse_correlation_groups (ADR-050 D8)
#
# One authority for D8's four rules: order, the claim, the primary and the two-member minimum. The scorer's routing
# and both renderers' SARIF correlation use its result, and sarif_common.correlation_assignments re-applies the same
# rules to the groups it is given, so one test runs the same edge cases through both.
# =============================================================================

_GROUP_HEADER = "| Group | Findings | Component | Threat Summary | Risk Level |\n|---|---|---|---|---|"


def _group_row(group, findings):
    return "| %s | %s | Gateway | Tampering: a summary | High |" % (group, findings)


def _section_4a(rows, heading="## 4a. Correlated Findings", prose="Correlation rules applied: CR-1.", header=_GROUP_HEADER):
    """A small threats.md around Section 4a. The tables before and after it must never be read as groups."""
    return "\n".join([
        "# Report", "", "## 3. Findings", "", "| Group | Findings |", "|---|---|", "| CG-90 | S-90, T-90 |", "",
        heading, "", prose, "", header] + list(rows) + [
        "", "## 5. Risk Summary", "", "| Group | Findings |", "|---|---|", "| CG-91 | S-91, T-91 |", ""])


def _group(group_id, members):
    return {"group_id": group_id, "primary": members[0], "members": members}


def test_groups_keep_section_4as_order_and_members_their_listed_order_with_the_primary_first():
    content = _section_4a([_group_row("CG-2", "T-2, LLM-4"), _group_row("CG-1", "E-2, R-3, AG-1"), _group_row("CG-3", "I-1, S-5")])
    assert parse_correlation_groups(content) == {
        "groups": [_group("CG-2", ["T-2", "LLM-4"]), _group("CG-1", ["E-2", "R-3", "AG-1"]), _group("CG-3", ["I-1", "S-5"])],
        "errors": []}, "file order, not number order; listed order, not S-2 order"


def test_members_are_canonical_and_the_group_id_is_kept_as_written():
    content = _section_4a([_group_row("CG-01", "AGP-01, T-2"), _group_row("CG-2", "**LLM-3**, I-04")])
    assert parse_correlation_groups(content)["groups"] == [_group("CG-01", ["AGP-1", "T-2"]), _group("CG-2", ["LLM-3", "I-4"])]


def test_members_are_filtered_to_the_member_set_and_the_first_one_left_is_the_primary():
    content = _section_4a([_group_row("CG-1", "S-1, T-2, I-3"), _group_row("CG-2", "E-4, D-5"), _group_row("CG-3", "R-6, AG-7, LLM-8")])
    groups = parse_correlation_groups(content, ["T-2", "I-3", "E-4", "R-6", "LLM-8", "S-99"])["groups"]
    assert groups == [_group("CG-1", ["T-2", "I-3"]), _group("CG-3", ["R-6", "LLM-8"])], \
        "S-1 is not a member, so T-2 is the primary; CG-2 keeps only E-4 and is omitted"
    assert parse_correlation_groups(content, [])["groups"] == [], "an empty member set leaves no group, unlike None"
    assert len(parse_correlation_groups(content, None)["groups"]) == 3 and len(parse_correlation_groups(content)["groups"]) == 3
    assert parse_correlation_groups(content, ["AGP-01"])["groups"] == [], "a member set takes any spelling of an ID"
    assert parse_correlation_groups(_section_4a([_group_row("CG-1", "AGP-1, S-1")]), ["AGP-01", "S-01"])["groups"] == [
        _group("CG-1", ["AGP-1", "S-1"])]
    with pytest.raises(ValueError):
        parse_correlation_groups(content, ["S-1", "not an ID"])


def test_a_group_of_fewer_than_two_emits_nothing_and_it_is_not_an_error():
    result = parse_correlation_groups(_section_4a([_group_row("CG-1", "S-1"), _group_row("CG-2", "T-2, T-2")]))
    assert result == {"groups": [], "errors": []}


def test_a_member_listed_in_two_groups_stays_in_the_first():
    """The shipped maestro-reference shape: AG-7 is in CG-1 and CG-2, so CG-2 is left with E-7 alone and falls away."""
    content = _section_4a([_group_row("CG-1", "T-7, AG-7"), _group_row("CG-2", "E-7, AG-7"), _group_row("CG-3", "I-7, LLM-1, AG-7")])
    assert parse_correlation_groups(content)["groups"] == [_group("CG-1", ["T-7", "AG-7"]), _group("CG-3", ["I-7", "LLM-1"])]


def test_a_first_group_that_falls_away_still_claims_its_ids():
    """D8's literal reading, ruled at W1: a later group never takes the ID over, and the ID stays uncorrelated."""
    alone = _section_4a([_group_row("CG-1", "S-1"), _group_row("CG-2", "S-1, T-2")])
    assert parse_correlation_groups(alone)["groups"] == [], "CG-1 has one member and omits itself, but S-1 is claimed"
    filtered = _section_4a([_group_row("CG-1", "S-1, T-2"), _group_row("CG-2", "S-1, I-3, E-4")])
    assert parse_correlation_groups(filtered, ["S-1", "I-3", "E-4"])["groups"] == [_group("CG-2", ["I-3", "E-4"])], \
        "T-2 is not a member, so CG-1 falls away; it still claims S-1"
    chain = _section_4a([_group_row("CG-1", "S-1, T-2"), _group_row("CG-2", "T-2, I-3"), _group_row("CG-3", "I-3, E-4, D-5")])
    assert parse_correlation_groups(chain)["groups"] == [_group("CG-1", ["S-1", "T-2"]), _group("CG-3", ["E-4", "D-5"])], \
        "CG-2 falls away, and still claims I-3"


def test_an_id_listed_twice_in_one_group_counts_once_even_under_two_spellings():
    content = _section_4a([_group_row("CG-1", "AGP-01, AGP-1, S-1, S-1")])
    assert parse_correlation_groups(content)["groups"] == [_group("CG-1", ["AGP-1", "S-1"])]


@pytest.mark.parametrize("row,reason", [
    (_group_row("CG-X", "S-1, T-2"), "names 'CG-X', which is not a correlation group ID"),
    (_group_row("CG-1234567", "S-1, T-2"), "names 'CG-1234567', which is not a correlation group ID"),
    (_group_row("cg-1", "S-1, T-2"), "names 'cg-1', which is not a correlation group ID"),
    (_group_row("_{CG-N}_", "_{comma-separated finding IDs}_"), "names '_{CG-N}_', which is not a correlation group ID"),
    (_group_row("", "S-1, T-2"), "names '', which is not a correlation group ID"),
    (_group_row("CG-1", "S-1, X-2"), "names 'X-2', which is not a finding ID"),
    (_group_row("CG-1", "S-1, T-2,"), "names '', which is not a finding ID"),
    (_group_row("CG-1", "S-1 T-2"), "names 'S-1 T-2', which is not a finding ID"),
    (_group_row("CG-1", "S-1, T-" + chr(0x661)), "names 'T-" + chr(0x661) + "', which is not a finding ID"),
    (_group_row("CG-1", "S-1, T-1234567"), "names 'T-1234567', which is not a finding ID"),
    (_group_row("CG-1", ""), "lists no findings"),
    (_group_row("CG-1", "—"), "lists no findings"),
    ("| CG-1 |", "has fewer cells than the table's header"),
], ids=["bad-group", "seven-digit-group", "lower-case-group", "template-placeholder", "empty-group", "bad-member", "trailing-comma",
        "no-separator", "unicode-digit", "seven-digit-member", "empty-findings", "dash-findings", "short-row"])
def test_a_malformed_row_is_skipped_and_listed_with_its_line_and_the_other_rows_still_parse(row, reason, capsys):
    content = _section_4a([_group_row("CG-5", "S-5, T-5"), row, _group_row("CG-6", "I-6, E-6")])
    lines = content.split("\n")
    at = lines.index(row) + 1
    result = parse_correlation_groups(content)
    assert result["groups"] == [_group("CG-5", ["S-5", "T-5"]), _group("CG-6", ["I-6", "E-6"])]
    assert result["errors"] == [{"line": at, "row": row, "reason": reason}]
    assert lines[at - 1] == row, "the line is 1-based"
    capsys.readouterr()


def test_a_skipped_row_claims_nothing_and_a_repeated_group_id_is_reported():
    content = _section_4a([_group_row("CG-1", "S-1, X-9"), _group_row("CG-2", "S-1, T-2"), _group_row("CG-2", "I-3, E-4"),
                           _group_row("CG-3", "I-3, E-4")])
    lines = content.split("\n")
    result = parse_correlation_groups(content)
    assert result["groups"] == [_group("CG-2", ["S-1", "T-2"]), _group("CG-3", ["I-3", "E-4"])], \
        "the bad row lost nothing to a claim, and the repeat of CG-2 is out, so I-3 and E-4 are CG-3's"
    assert [(e["line"], e["reason"]) for e in result["errors"]] == [
        (lines.index(_group_row("CG-1", "S-1, X-9")) + 1, "names 'X-9', which is not a finding ID"),
        (lines.index(_group_row("CG-2", "I-3, E-4")) + 1,
         "repeats group ID CG-2, first listed at line %d" % (lines.index(_group_row("CG-2", "S-1, T-2")) + 1))]


def test_a_placeholder_row_is_dropped_without_a_report_and_a_long_row_is_cut():
    content = _section_4a(["| — | — | — | — | — |", "|  |  | | | |", _group_row("CG-1", "S-1, T-2"),
                           _group_row("CG-2", "S-3, " + "T-" * 300)])
    result = parse_correlation_groups(content)
    assert result["groups"] == [_group("CG-1", ["S-1", "T-2"])]
    (error,) = result["errors"]
    assert len(error["row"]) == 200 and len(error["reason"]) < 80, "nothing long is echoed, in the row or in the reason"


@pytest.mark.parametrize("content", [
    "", "# Report\n\n## 7. Recommended Actions\n\n| ID | X |\n|---|---|\n| S-1 | y |\n",
    _section_4a([]), _section_4a([], prose="> No cross-agent correlations detected."),
    "## 4a. Correlated Findings\n\nNo table here at all.\n\n## 5. Next\n\n| Group | Findings |\n|---|---|\n| CG-1 | S-1, T-2 |\n",
    "## Section 4a: Correlated Findings\n\n**Cross-agent correlations detected**: NONE in this baseline.\n\n---\n\n## Section 5: Risk\n",
    "## 4a. Correlated Findings\n",
], ids=["empty", "no-section", "header-only-table", "zero-correlation-form", "prose-only-then-a-later-table", "section-form-prose-only", "heading-only"])
def test_a_missing_or_empty_section_4a_means_no_groups_and_no_errors(content):
    assert parse_correlation_groups(content) == {"groups": [], "errors": []}
    assert parse_correlation_groups(content, ["S-1", "T-2"]) == {"groups": [], "errors": []}


def test_section_4a_is_not_a_group_table_when_the_text_is_not_a_string():
    assert parse_correlation_groups(None) == {"groups": [], "errors": []}


@pytest.mark.parametrize("heading", ["## 4a. Correlated Findings", "### 4a. Correlated Findings", "## Section 4a: Correlated Findings",
                                     "## 4a. Correlation Groups", "### Section 4a. Correlated Findings"])
def test_the_three_heading_forms_that_the_shipped_samples_show_are_read(heading):
    content = _section_4a([_group_row("CG-1", "T-10, LLM-1, LLM-2")], heading=heading)
    assert parse_correlation_groups(content)["groups"] == [_group("CG-1", ["T-10", "LLM-1", "LLM-2"])]


@pytest.mark.parametrize("heading", ["#### 4a. Correlated Findings", "## 4b. Findings by Agentic Pattern", "## 4ab. Other", "## 4. Coverage",
                                     "## Correlated Findings"])
def test_a_heading_that_is_not_section_4a_is_not_read(heading):
    assert parse_correlation_groups(_section_4a([_group_row("CG-1", "S-1, T-2")], heading=heading)) == {"groups": [], "errors": []}


def test_only_the_first_table_of_the_section_is_read_and_a_level_three_section_stops_at_the_next_level_three_heading():
    two = _section_4a([_group_row("CG-1", "S-1, T-2"), "", "| Group | Findings |", "|---|---|", "| CG-2 | I-3, E-4 |"])
    assert [g["group_id"] for g in parse_correlation_groups(two)["groups"]] == ["CG-1"]
    stops = _section_4a([], heading="### 4a. Correlated Findings").replace("## 5. Risk Summary", "### 4b. Patterns")
    assert parse_correlation_groups(stops) == {"groups": [], "errors": []}, "the later table is another section's"


def test_a_section_4a_table_with_one_column_has_no_group_and_no_findings_cells_and_every_row_is_listed():
    content = _section_4a(["| CG-1 |", "| CG-2 |"], header="| Group |\n|---|")
    result = parse_correlation_groups(content)
    assert result["groups"] == [] and [e["reason"] for e in result["errors"]] == ["has no Group and Findings cells"] * 2
    assert [e["row"] for e in result["errors"]] == ["| CG-1 |", "| CG-2 |"]


def test_the_section_4a_cells_are_decoded_like_every_other_table():
    content = _section_4a(["| **CG-1** | S-1, T-2 | Gate &amp; Way | A &lt; B | High |"])
    assert parse_correlation_groups(content)["groups"] == [_group("CG-1", ["S-1", "T-2"])]


def test_parse_markdown_table_reports_the_line_of_each_row_it_returns(capsys):
    content = "## X\n\n| A | B |\n|---|---|\n| 1 | 2 |\n| short |\n| 3 | 4 |\n"
    at, skipped = [], []
    rows = parse_markdown_table(content, "## X", skipped=skipped, row_lines=at)
    assert [row["A"] for row in rows] == ["1", "3"] and at == [5, 7] and skipped == [6]
    assert parse_markdown_table(content, "## X") == rows, "the default is as it always was"
    capsys.readouterr()


# ---- the same edge cases through both implementations --------------------------------------------------------

_AGREEMENT_CASES = {
    "plain": ([("CG-1", ["S-1", "T-2"]), ("CG-2", ["I-3", "E-4", "AG-5"])], None),
    "a-member-in-two-groups": ([("CG-1", ["T-7", "AG-7"]), ("CG-2", ["E-7", "AG-7"]), ("CG-3", ["I-7", "LLM-1", "AG-7"])], None),
    "first-group-falls-away-on-the-member-set": ([("CG-1", ["S-1", "T-2"]), ("CG-2", ["S-1", "I-3", "E-4"])], ["S-1", "I-3", "E-4"]),
    "first-group-falls-away-alone": ([("CG-1", ["S-1"]), ("CG-2", ["S-1", "T-2"])], None),
    "an-id-outside-the-member-set-claims": ([("CG-1", ["D-9", "S-1"]), ("CG-2", ["S-1", "T-2", "I-3"])], ["S-1", "T-2", "I-3"]),
    "a-chain-of-falling-groups": ([("CG-1", ["S-1", "T-2"]), ("CG-2", ["T-2", "I-3"]), ("CG-3", ["I-3", "E-4", "D-5"])], None),
    "repeats-in-one-group": ([("CG-1", ["S-1", "S-1", "T-2"])], None),
    "two-spellings": ([("CG-1", ["AGP-01", "T-2"]), ("CG-2", ["AGP-1", "I-3"])], ["AGP-1", "T-2", "I-3"]),
    "the-primary-is-not-a-member": ([("CG-1", ["S-1", "T-2", "I-3"])], ["T-2", "I-3"]),
    "file-order-not-number-order": ([("CG-2", ["S-1", "T-2"]), ("CG-1", ["T-2", "I-3"])], None),
    "every-member-filtered": ([("CG-1", ["S-1", "T-2"])], []),
    "no-groups": ([], None),
}


def _as_assignments(groups):
    """What each group gives each member, the way correlation_assignments keys it."""
    out = {}
    for group in groups:
        peers = tuple(group["members"][1:])
        out[group["primary"]] = sarif_common.Correlation(group["group_id"], "primary", group["primary"], peers)
        for peer in peers:
            out[peer] = sarif_common.Correlation(group["group_id"], "peer", group["primary"], ())
    return out


@pytest.mark.parametrize("name", sorted(_AGREEMENT_CASES))
def test_the_section_4a_reader_and_the_sarif_emitters_assignments_agree(name):
    """The architect's W1 ruling: parse_correlation_groups is the one authority, and correlation_assignments, which
    only assigns roles, re-applies the same rules and must give the same answer on the same input."""
    raw_groups, member_ids = _AGREEMENT_CASES[name]
    content = _section_4a([_group_row(group_id, ", ".join(listed)) for group_id, listed in raw_groups])
    everyone = member_ids if member_ids is not None else sorted({tachi_parts.canonical_finding_id(i) for _, ids in raw_groups for i in ids})
    parsed = parse_correlation_groups(content, member_ids)
    assert parsed["errors"] == []
    from_the_file = _as_assignments(parsed["groups"])
    assert sarif_common.correlation_assignments(raw_groups, everyone) == from_the_file, "the same raw groups, in the emitter"
    assert sarif_common.correlation_assignments([(g["group_id"], g["members"]) for g in parsed["groups"]], everyone) == from_the_file, \
        "what the parser returns goes through the emitter unchanged"


def test_the_edge_cases_come_out_as_d8_reads_them():
    """Pins what the two implementations agree on, so a change to both together is still a decision."""
    by_name = {name: parse_correlation_groups(
        _section_4a([_group_row(group_id, ", ".join(listed)) for group_id, listed in raw]), member_ids)["groups"]
        for name, (raw, member_ids) in _AGREEMENT_CASES.items()}
    assert by_name["a-member-in-two-groups"] == [_group("CG-1", ["T-7", "AG-7"]), _group("CG-3", ["I-7", "LLM-1"])]
    assert by_name["first-group-falls-away-on-the-member-set"] == [_group("CG-2", ["I-3", "E-4"])]
    assert by_name["first-group-falls-away-alone"] == []
    assert by_name["an-id-outside-the-member-set-claims"] == [_group("CG-2", ["T-2", "I-3"])]
    assert by_name["a-chain-of-falling-groups"] == [_group("CG-1", ["S-1", "T-2"]), _group("CG-3", ["E-4", "D-5"])]
    assert by_name["two-spellings"] == [_group("CG-1", ["AGP-1", "T-2"])]
    assert by_name["the-primary-is-not-a-member"] == [_group("CG-1", ["T-2", "I-3"])]
    assert by_name["file-order-not-number-order"] == [_group("CG-2", ["S-1", "T-2"])]
    assert by_name["every-member-filtered"] == [] and by_name["no-groups"] == []


# ---- the shipped samples ---------------------------------------------------------------------------------------

def _example_threats(relative):
    return (REPO_ROOT / "examples" / relative / "threats.md").read_text(encoding="utf-8")


def test_every_shipped_section_4a_reads_without_an_error():
    paths = sorted((REPO_ROOT / "examples").rglob("threats.md"))
    assert len(paths) >= 10
    for path in paths:
        assert parse_correlation_groups(path.read_text(encoding="utf-8"))["errors"] == [], path.relative_to(REPO_ROOT).as_posix()


def test_the_shipped_samples_that_show_the_drift_forms_and_a_shared_member():
    maestro = parse_correlation_groups(_example_threats("maestro-reference"))["groups"]
    assert [g["group_id"] for g in maestro] == ["CG-1", "CG-3", "CG-4", "CG-5", "CG-6"], \
        "AG-7 is listed in CG-1 and CG-2, so CG-2 is left with E-7 and falls away"
    assert maestro[0] == _group("CG-1", ["T-7", "AG-7"])
    predictive = parse_correlation_groups(_example_threats("predictive-ml-app/sample-report"))["groups"]
    assert predictive[0] == _group("CG-1", ["T-10", "LLM-1", "LLM-2"]) and len(predictive) == 4, "a level-3 heading"
    assert parse_correlation_groups(_example_threats("consumer-agent-app/sample-report")) == {"groups": [], "errors": []}, \
        "`## Section 4a:` with prose and no table"
    agentic = parse_correlation_groups(_example_threats("agentic-app"))["groups"]
    assert agentic[2] == _group("CG-3", ["E-2", "R-3", "AG-1"]), "listed order, not S-2 order"
    for relative in ("web-app", "microservices", "ascii-web-api", "mermaid-agentic-app", "free-text-microservice"):
        assert parse_correlation_groups(_example_threats(relative)) == {"groups": [], "errors": []}, relative


# =============================================================================
# Feature 374 (W2, T142): the SARIF fallback reader, parse_sarif_member_set (ADR-050 D8, AR-T2)
#
# The member set, the groups and (for risk-scores.sarif) the scores of a SARIF file, for a stage whose markdown input
# is absent. It reads the new form (correlation properties), the form older samples show (a peer names its primary)
# and the legacy form (peer references in relatedLocations). A hash is never read, and an empty extraction raises.
# =============================================================================

def _result(finding_id, properties=None, related=None, fingerprints=None, **extra):
    result = {"ruleId": "tachi/stride/tampering", "message": {"text": "A finding."}, "level": "error",
              "partialFingerprints": {"primaryLocationLineHash": "0123456789abcdef:1", "findingId/v1": finding_id}}
    if fingerprints is not None:
        result["partialFingerprints"].update(fingerprints)
    if properties is not None:
        result["properties"] = properties
    if related is not None:
        result["relatedLocations"] = [{"id": index, "message": {"text": text}} for index, text in enumerate(related)]
    result.update(extra)
    return result


def _sarif(*results, **run):
    return json.dumps({"version": "2.1.0", "runs": [dict({"results": list(results)}, **run)]})


def _correlated(group, role, primary):
    return {"correlation-group": group, "correlation-role": role, "correlation-primary": primary}


def test_the_new_form_gives_members_in_result_order_and_its_groups_from_the_correlation_properties():
    text = _sarif(
        _result("S-1", _correlated("CG-1", "primary", "S-1")), _result("T-2"), _result("I-3", _correlated("CG-1", "peer", "S-1")),
        _result("AGP-01", _correlated("CG-2", "peer", "LLM-4")), _result("LLM-4", _correlated("CG-2", "primary", "LLM-4")))
    assert parse_sarif_member_set(text) == {
        "members": ["S-1", "T-2", "I-3", "AGP-1", "LLM-4"],
        "groups": [_group("CG-1", ["S-1", "I-3"]), _group("CG-2", ["LLM-4", "AGP-1"])],
        "scores": {}}


def test_the_legacy_form_groups_each_peer_reference_under_its_result():
    text = _sarif(
        _result("S-1", fingerprints={"correlationGroup": "CG-1"},
                related=["T-3: API Gateway session data may be tampered with", "I-2: may leak tokens", "Control evidence: auth in a.py"]),
        _result("E-5"))
    assert parse_sarif_member_set(text) == {
        "members": ["S-1", "T-3", "I-2", "E-5"], "groups": [_group("CG-1", ["S-1", "T-3", "I-2"])], "scores": {}}
    unnamed = parse_sarif_member_set(_sarif(_result("S-1", related=["T-3: a threat"])))
    assert unnamed["groups"] == [_group(None, ["S-1", "T-3"])], "`None` where the file names no group"


@pytest.mark.parametrize("text,is_a_reference", [
    ("T-3: a summary", True), ("AGP-12: a summary", True), ("AGP-012: a summary", True), ("LLM-1: x", True),
    ("T-3:no space", False), ("T-3 : space before", False), ("see T-3: later", False), (" T-3: leading space", False),
    ("t-3: lower case", False), ("X-3: unknown prefix", False), ("T-1234567: seven digits", False), ("T-: no number", False),
    ("T-" + chr(0x663) + ": unicode digit", False), ("Control evidence: authentication detected in a.py", False), ("", False),
])
def test_a_legacy_peer_reference_is_an_allow_listed_id_at_the_start_followed_by_a_colon_and_a_space(text, is_a_reference):
    members = parse_sarif_member_set(_sarif(_result("S-1", related=[text])))["members"]
    assert (len(members) == 2) is is_a_reference, members


def test_the_form_that_older_samples_show_has_a_peer_name_its_primary_with_no_group_id():
    text = _sarif(_result("E-2"), _result("AG-1", {"correlation-primary": "E-2"}), _result("R-3", {"correlation-primary": "E-2"}),
                  _result("D-1"))
    assert parse_sarif_member_set(text)["groups"] == [_group(None, ["E-2", "AG-1", "R-3"])]


def test_a_result_that_names_only_its_group_is_grouped_under_the_first_member_as_primary():
    text = _sarif(_result("T-2", {"correlation-group": "CG-4"}), _result("S-1", {"correlation-group": "CG-4"}), _result("E-3"))
    assert parse_sarif_member_set(text)["groups"] == [_group("CG-4", ["T-2", "S-1"])]


def test_a_bad_group_role_or_primary_is_ignored_not_an_error():
    text = _sarif(_result("S-1", _correlated("group-1", "boss", "S-1")), _result("T-2", _correlated("CG-1", "peer", "nope")),
                  _result("I-3", _correlated("CG-1", "peer", "T-2")))
    assert parse_sarif_member_set(text)["groups"] == [_group("CG-1", ["T-2", "I-3"])]


@pytest.mark.parametrize("marker", [
    {"properties": {"baselineState": "absent"}}, {"properties": {"baseline-state": "absent"}}, {"baselineState": "absent"},
    {"properties": {"baselineState": " Absent "}},
], ids=["property", "hyphenated-property", "result-key", "case-and-space"])
def test_an_absent_result_is_resolved_and_appears_nowhere(marker):
    gone = _result("S-1", dict(_correlated("CG-1", "primary", "S-1"), **marker.get("properties", {})))
    gone.update({key: value for key, value in marker.items() if key != "properties"})
    text = _sarif(gone, _result("T-2", _correlated("CG-1", "peer", "S-1")), _result("I-3", _correlated("CG-1", "peer", "S-1")),
                  _result("E-4", related=["S-1: a resolved finding", "D-5: still open"]),
                  _result("R-6", {"baselineState": "new"}), _result("AG-7", {"baselineState": "unchanged", "baseline-state": "updated"}))
    result = parse_sarif_member_set(text, with_scores=True)
    assert result["members"] == ["T-2", "I-3", "E-4", "D-5", "R-6", "AG-7"], "S-1 is neither a result nor a reference"
    assert result["groups"] == [_group("CG-1", ["T-2", "I-3"]), _group(None, ["E-4", "D-5"])], \
        "S-1 was the primary: T-2 is the first member left. E-4 keeps D-5 and loses the reference to S-1"
    assert "S-1" not in result["scores"] and set(result["scores"]) == {"T-2", "I-3", "E-4", "R-6", "AG-7"}
    assert "S-1" not in json.dumps(result)


def test_an_id_with_one_absent_result_and_one_that_is_not_stays():
    text = _sarif(_result("S-1", {"baselineState": "absent"}), _result("S-1", {"baselineState": "new"}), _result("T-2"))
    assert parse_sarif_member_set(text)["members"] == ["S-1", "T-2"]


@pytest.mark.parametrize("properties,composite,band", [
    ({"composite": 8.2, "security-severity": "8.2", "severity_band": "High"}, Decimal("8.2"), "High"),
    ({"security-severity": "7.8", "severity-band": "high"}, Decimal("7.8"), "High"),
    ({"composite": 8.4, "security-severity": "8.4", "severity": "Critical"}, Decimal("8.4"), "Critical"),
    ({"composite": "n/a", "security-severity": "6.1", "severity": "MEDIUM"}, Decimal("6.1"), "Medium"),
    ({"composite": 11, "security-severity": "3.4", "severity-band": "weird", "severity_band": "Low"}, Decimal("3.4"), "Low"),
    ({"composite": 9}, Decimal(9), None),
    ({"composite": 0}, Decimal(0), None),
    ({"composite": 10.0}, Decimal(10), None),
    ({"composite": True, "severity-band": True}, None, None),
    ({"security-severity": "NaN"}, None, None),
    ({"security-severity": "Infinity"}, None, None),
    ({"security-severity": "-0.1"}, None, None),
    ({"composite": 10.1}, None, None),
    ({"security-severity": "1e999"}, None, None),
    ({"composite": [8.2], "severity-band": "Note"}, None, None),
    ({"cvss-base-score": "9.8"}, None, None),
    ({}, None, None),
])
def test_scores_read_the_property_names_the_shipped_files_use(properties, composite, band):
    result = parse_sarif_member_set(_sarif(_result("S-1", properties)), with_scores=True)
    score = result["scores"]["S-1"]
    assert score == {"composite": composite, "band": band}
    assert composite is None or isinstance(score["composite"], Decimal)


def test_scores_are_only_for_the_results_that_exist_and_the_first_result_of_an_id_wins():
    text = _sarif(_result("S-1", {"security-severity": "8.2"}, related=["T-3: a peer with no result"]),
                  _result("S-1", {"security-severity": "1.0"}), _result("AGP-01", {"security-severity": "5.5"}))
    assert parse_sarif_member_set(text, with_scores=True)["scores"] == {
        "S-1": {"composite": Decimal("8.2"), "band": None}, "AGP-1": {"composite": Decimal("5.5"), "band": None}}
    assert parse_sarif_member_set(text)["scores"] == {}, "no scores unless asked"
    assert parse_sarif_member_set(text, with_scores=False)["scores"] == {}


def test_a_hash_is_never_read_and_a_result_has_an_id_only_from_its_fingerprint_or_its_id_property():
    kept = _result("S-1", fingerprints={"primaryLocationLineHash": "not even a hash"})
    only_a_hash = {"ruleId": "x", "message": {"text": "m"}, "partialFingerprints": {"primaryLocationLineHash": "0123456789abcdef:1"}}
    other_properties = {"ruleId": "x", "message": {"text": "m"}, "properties": {"findingId": "I-3", "finding_id": "E-4", "ID": "D-5"}}
    bad_ids = [_result(bad) for bad in (1, "", "S-1a", "S-" + chr(0x661), "S-1234567", "X-1", " S-1", "S-1\n", ["S-1"])]
    bad_ids.append(_result(None, {"id": "S-1a"}))
    result = parse_sarif_member_set(_sarif(kept, only_a_hash, other_properties, *bad_ids))
    assert result["members"] == ["S-1"], "no hash, and no property but `id`, names a finding"
    assert "0123456789abcdef" not in json.dumps(result)


def test_a_result_with_no_finding_id_fingerprint_takes_its_id_from_properties_id():
    """ADR-050 D8, option (b): tachi's older SARIF has no fingerprint and carries the ID as ``properties.id``."""
    older = {"ruleId": "tachi/risk/spoofing", "message": {"text": "m"}, "properties": {"id": "S-1"}}
    assert parse_sarif_member_set(_sarif(older))["members"] == ["S-1"]
    assert parse_sarif_member_set(_sarif({**older, "partialFingerprints": {}}))["members"] == ["S-1"]
    assert parse_sarif_member_set(_sarif({**older, "properties": {"id": "AGP-01"}}))["members"] == ["AGP-1"], "canonical"
    null_fingerprint = _result(None, {"id": "T-2"})
    assert parse_sarif_member_set(_sarif(null_fingerprint))["members"] == ["T-2"], "a null fingerprint is no fingerprint"
    both = _result("S-1", {"id": "T-2"})
    assert parse_sarif_member_set(_sarif(both))["members"] == ["S-1"], "findingId/v1 wins when both are present"
    mixed = parse_sarif_member_set(_sarif(older, _result("E-3"), {**older, "properties": {"id": "T-4"}}, both))
    assert mixed["members"] == ["S-1", "E-3", "T-4"]


@pytest.mark.parametrize("result", [
    _result("S-1a", {"id": "T-2"}), _result("", {"id": "T-2"}), _result(7, {"id": "T-2"}),
    {"message": {"text": "m"}, "properties": {"id": "X-9"}}, {"message": {"text": "m"}, "properties": {"id": "T-2\n"}},
    {"message": {"text": "m"}, "properties": {"id": "T-" + chr(0x661)}}, {"message": {"text": "m"}, "properties": {"id": 12}},
    {"message": {"text": "m"}, "properties": {"id": ["T-2"]}}, {"message": {"text": "m"}, "properties": {"Id": "T-2"}},
    {"message": {"text": "m"}, "properties": ["id", "T-2"]}, {"message": {"text": "m"}, "properties": {"baselineState": "absent", "id": "T-2"}},
], ids=["fingerprint-invalid-wins", "fingerprint-empty-wins", "fingerprint-number-wins", "unknown-prefix", "trailing-newline",
        "unicode-digit", "number", "list", "other-spelling", "properties-a-list", "absent"])
def test_a_result_that_names_no_allow_listed_id_is_ignored_and_an_extraction_of_only_those_is_empty(result):
    assert parse_sarif_member_set(_sarif(result, _result("S-1")))["members"] == ["S-1"]
    with pytest.raises(ValueError):
        parse_sarif_member_set(_sarif(result))


def test_the_properties_id_form_reads_its_scores_and_groups_like_the_other_forms():
    text = _sarif({"message": {"text": "m"}, "properties": {"id": "S-1", "composite": 8.4, "severity": "Critical", **_correlated("CG-1", "primary", "S-1")}},
                  {"message": {"text": "m"}, "properties": {"id": "T-2", "security-severity": "7.6", **_correlated("CG-1", "peer", "S-1")}})
    assert parse_sarif_member_set(text, with_scores=True) == {
        "members": ["S-1", "T-2"], "groups": [_group("CG-1", ["S-1", "T-2"])],
        "scores": {"S-1": {"composite": Decimal("8.4"), "band": "Critical"}, "T-2": {"composite": Decimal("7.6"), "band": None}}}


def test_an_id_is_one_member_under_any_spelling_and_only_the_first_run_counts():
    text = json.dumps({"runs": [{"results": [_result("AGP-01"), _result("AGP-1"), _result("T-2"), _result("T-2")]},
                                {"results": [_result("S-1")]}]})
    assert parse_sarif_member_set(text)["members"] == ["AGP-1", "T-2"]


def test_a_result_of_any_other_shape_is_skipped_and_never_raises():
    with_odd_locations = _result("T-2")
    with_odd_locations["relatedLocations"] = [None, 5, {"message": "T-3: x"}, {"message": {"text": 4}}, {"message": {"text": "I-4: ok"}}]
    odd = [None, 3, "S-1", [], {"partialFingerprints": "S-1"}, {"partialFingerprints": {"findingId/v1": "S-1"}, "properties": ["x"],
                                                                  "relatedLocations": {"a": 1}}, with_odd_locations]
    result = parse_sarif_member_set(json.dumps({"runs": [{"results": odd}]}), with_scores=True)
    assert result["members"] == ["S-1", "T-2", "I-4"]
    assert result["scores"]["S-1"] == {"composite": None, "band": None}


def test_named_groups_come_in_number_order_then_the_unnamed_in_first_appearance_order_and_a_group_id_names_one_group():
    text = _sarif(
        _result("T-2", _correlated("CG-2", "primary", "T-2")), _result("I-3", _correlated("CG-2", "peer", "T-2")),
        _result("D-8", {"correlation-primary": "R-9"}), _result("R-9"),
        _result("S-1", _correlated("CG-10", "primary", "S-1")), _result("E-4", _correlated("CG-10", "peer", "S-1")),
        _result("AG-5", _correlated("CG-1", "primary", "AG-5")), _result("LLM-6", _correlated("CG-1", "peer", "AG-5")),
        _result("OI-7", _correlated("CG-10", "primary", "OI-7")))
    assert parse_sarif_member_set(text)["groups"] == [
        _group("CG-1", ["AG-5", "LLM-6"]), _group("CG-2", ["T-2", "I-3"]), _group("CG-10", ["S-1", "E-4", "OI-7"]),
        _group(None, ["R-9", "D-8"])], "CG-10 has two primaries in the file, and is one group with the first"


def test_the_claim_rule_holds_in_the_fallback_with_the_groups_in_section_order():
    """Two legacy primaries both list AG-7. The lower group number claims it, as the Section 4a reader gives it."""
    text = _sarif(_result("E-7", fingerprints={"correlationGroup": "CG-2"}, related=["AG-7: x", "I-7: y"]),
                  _result("T-7", fingerprints={"correlationGroup": "CG-1"}, related=["AG-7: z"]))
    assert parse_sarif_member_set(text)["groups"] == [_group("CG-1", ["T-7", "AG-7"]), _group("CG-2", ["E-7", "I-7"])]
    only_one = _sarif(_result("E-7", fingerprints={"correlationGroup": "CG-2"}, related=["AG-7: x"]),
                      _result("T-7", fingerprints={"correlationGroup": "CG-1"}, related=["AG-7: z"]))
    assert parse_sarif_member_set(only_one)["groups"] == [_group("CG-1", ["T-7", "AG-7"])], "CG-2 is left with E-7 and falls away"


@pytest.mark.parametrize("text", [
    "", "   ", "not json", "{", '{"runs": [', "[1, 2", "{'runs': []}", '{"a": NaN}', '{"a": Infinity}', '{"a": -Infinity}',
    '{"a": ' + "9" * 25 + "}", "[" * 200000, '{"a":' * 5000 + "1" + "}" * 5000, '{"a": 1e999999999999999999999999}',
])
def test_text_that_is_not_json_raises_value_error_and_never_echoes_it(text):
    with pytest.raises(ValueError) as raised:
        parse_sarif_member_set(text)
    assert len(str(raised.value)) < 120


def test_the_error_for_bad_text_does_not_echo_it():
    with pytest.raises(ValueError) as raised:
        parse_sarif_member_set("SECRET-TOKEN {")
    assert "SECRET" not in str(raised.value)


def test_text_over_the_size_cap_raises_value_error(monkeypatch):
    text = _sarif(_result("S-1"))
    assert parse_sarif_member_set(text)["members"] == ["S-1"]
    monkeypatch.setattr(tachi_parts, "MAX_AGENT_INPUT_BYTES", len(text) - 1)
    with pytest.raises(ValueError) as raised:
        parse_sarif_member_set(text)
    assert "cap" in str(raised.value)


@pytest.mark.parametrize("value", [None, 5, b"{}", ["runs"], {"runs": []}])
def test_a_value_that_is_not_text_raises_value_error(value):
    with pytest.raises(ValueError):
        parse_sarif_member_set(value)


@pytest.mark.parametrize("document", [
    {}, [], "text", 5, None, {"runs": []}, {"runs": {}}, {"runs": [None]}, {"runs": [{}]}, {"runs": [{"results": []}]},
    {"runs": [{"results": {}}]}, {"runs": [{"results": [None, 3, "x"]}]},
    {"runs": [{"results": [{"partialFingerprints": {"primaryLocationLineHash": "0123456789abcdef:1"}}]}]},
    {"runs": [{"results": [_result("S-1", {"baselineState": "absent"}), _result("T-2", {"baseline-state": "absent"})]}]},
    {"runs": [{"results": []}, {"results": [_result("S-1")]}]},
], ids=["empty-object", "list", "string", "number", "null", "no-runs", "runs-object", "null-run", "run-without-results", "empty-results",
        "results-object", "results-of-junk", "hash-only", "all-absent", "results-only-in-run-two"])
def test_an_empty_extraction_raises_so_the_stage_stops_before_dispatch(document):
    with pytest.raises(ValueError) as raised:
        parse_sarif_member_set(json.dumps(document, default=str))
    message = str(raised.value)
    assert "no open finding" in message and "findingId/v1" in message and "properties.id" in message and len(message) < 250
    assert message.endswith("Remedy: regenerate the markdown input")


def test_the_reader_is_deterministic_and_returns_fresh_objects():
    text = _sarif(_result("S-1", {"security-severity": "8.2"}), _result("T-2", _correlated("CG-1", "peer", "S-1")))
    first, second = parse_sarif_member_set(text, with_scores=True), parse_sarif_member_set(text, with_scores=True)
    assert first == second and first is not second and first["members"] is not second["members"]


# ---- the shipped samples ---------------------------------------------------------------------------------------

def _shipped_sarif(relative):
    return (REPO_ROOT / "examples" / relative).read_text(encoding="utf-8")


@pytest.mark.parametrize("relative", [
    "agentic-app/sample-report/risk-scores.sarif", "agentic-app/sample-report/compensating-controls.sarif",
    "agentic-app/sample-report/threats.sarif", "consumer-agent-app/sample-report/risk-scores.sarif",
    "maestro-reference/risk-scores.sarif", "maestro-reference/compensating-controls.sarif", "maestro-reference/threats.sarif",
    "mobile-banking-app/sample-report/risk-scores.sarif", "mobile-banking-app/sample-report/compensating-controls.sarif",
    "agentic-app/test-output/2026-03-25T12-53-57/threats.sarif",
])
def test_a_shipped_sarif_that_carries_finding_ids_reads_as_the_distinct_ids_plus_its_legacy_references(relative):
    text = _shipped_sarif(relative)
    results = json.loads(text)["runs"][0]["results"]
    distinct = {tachi_parts.canonical_finding_id(r["partialFingerprints"]["findingId/v1"]) for r in results}
    references = set()
    for result in results:
        for location in result.get("relatedLocations", []):
            match = re.match(r"([A-Z]+-[0-9]+): ", location["message"]["text"])
            if match:
                references.add(tachi_parts.canonical_finding_id(match.group(1)))
    members = parse_sarif_member_set(text, with_scores=relative.endswith("risk-scores.sarif"))["members"]
    assert len(members) == len(set(members)) == len(distinct | references)
    assert set(members) == distinct | references


_PROPERTIES_ID_SAMPLES = [
    ("mobile-banking-app/sample-report/threats.sarif", 31, ["S-1", "S-2", "S-3", "S-4", "S-5", "T-1"]),
    ("predictive-ml-app/sample-report/threats.sarif", 49, ["S-1", "S-2", "S-3", "S-4", "S-5", "S-6"]),
    ("predictive-ml-app/sample-report/risk-scores.sarif", 12, ["S-1", "T-10", "LLM-1", "LLM-2", "LLM-3", "LLM-4", "D-8", "D-9", "D-10", "D-11", "S-5", "S-2"]),
    ("predictive-ml-app/sample-report/compensating-controls.sarif", 10, ["S-1", "T-10", "LLM-1", "LLM-2", "LLM-3", "LLM-4", "D-8", "D-9"]),
]


@pytest.mark.parametrize("relative,count,first", _PROPERTIES_ID_SAMPLES, ids=[sample[0].split("/")[0] + "-" + sample[0].rsplit("/", 1)[1]
                                                                            for sample in _PROPERTIES_ID_SAMPLES])
def test_a_shipped_sarif_that_carries_the_id_only_as_properties_id_yields_its_member_set(relative, count, first):
    """D8 option (b): `mobile-banking-app`'s `threats.sarif` and all three of `predictive-ml-app`'s files have no
    fingerprint and no correlation, and every result's `properties.id` is an allow-listed finding ID."""
    text = _shipped_sarif(relative)
    results = json.loads(text)["runs"][0]["results"]
    assert all("partialFingerprints" not in result for result in results)
    expected = [tachi_parts.canonical_finding_id(result["properties"]["id"]) for result in results]
    parsed = parse_sarif_member_set(text, with_scores=relative.endswith("risk-scores.sarif"))
    assert parsed["members"] == expected and len(expected) == len(set(expected)) == count
    assert parsed["members"][:len(first)] == first
    assert parsed["groups"] == []
    if relative.endswith("risk-scores.sarif"):
        assert set(parsed["scores"]) == set(expected) and all(s["composite"] is not None for s in parsed["scores"].values())


def test_the_older_sample_that_matches_its_markdown_reads_the_same_member_set():
    """`mobile-banking-app`'s `threats.sarif` has one result per Section 7 row, so the two readers agree. (The
    `predictive-ml-app` SARIF files are partial: 12 results for a 28-row `risk-scores.md`, and no N/N.)"""
    sarif = parse_sarif_member_set(_shipped_sarif("mobile-banking-app/sample-report/threats.sarif"))["members"]
    reference = parse_reference_set(_example_threats("mobile-banking-app/sample-report"))
    assert sorted(sarif, key=tachi_parts.finding_sort_key) == [finding["id"] for finding in reference["open"]]


def test_the_scores_of_a_shipped_risk_scores_sarif_read_for_every_result():
    for relative, count in (("agentic-app/sample-report/risk-scores.sarif", 86), ("consumer-agent-app/sample-report/risk-scores.sarif", 19),
                            ("maestro-reference/risk-scores.sarif", 35), ("mobile-banking-app/sample-report/risk-scores.sarif", 31)):
        scores = parse_sarif_member_set(_shipped_sarif(relative), with_scores=True)["scores"]
        assert len(scores) == count and all(s["composite"] is not None and s["band"] is not None for s in scores.values()), relative
    agentic = parse_sarif_member_set(_shipped_sarif("agentic-app/sample-report/risk-scores.sarif"), with_scores=True)["scores"]
    assert agentic["S-1"] == {"composite": Decimal("8.2"), "band": "High"}
    maestro = parse_sarif_member_set(_shipped_sarif("maestro-reference/risk-scores.sarif"), with_scores=True)["scores"]
    assert maestro["S-1"] == {"composite": Decimal("8.4"), "band": "High"}


@pytest.mark.parametrize("sample", ["agentic-app/sample-report", "maestro-reference"])
def test_the_fallback_reads_the_groups_that_section_4a_gives_on_a_shipped_sample(sample):
    """One authority: the SARIF reader and the Section 4a reader apply the same rules, so on a sample whose
    risk-scores.sarif was written from its threats.md they find the same groups (the SARIF may not name them)."""
    sarif = parse_sarif_member_set(_shipped_sarif(sample + "/risk-scores.sarif"))
    from_markdown = parse_correlation_groups(_example_threats(sample), sarif["members"])["groups"]
    assert from_markdown and len(from_markdown) == len(sarif["groups"])
    assert sorted((g["primary"], sorted(g["members"])) for g in sarif["groups"]) == \
        sorted((g["primary"], sorted(g["members"])) for g in from_markdown)


# =============================================================================
# Feature 374 (W2, T032): the drift forms of Section 7 (S-12, FR-E.16)
#
# The reference-set wrapper reads Section 7 under `## 7. Recommended Actions` or `## Section 7: Recommended Actions`, as a
# table or, when there is none, as the numbered list of bolded IDs that two shipped samples show. A value the form lacks is
# listed in `lacking`, so a stage can derive it from the baseline or score the finding fresh, flag it and list it (S-12(b)).
# Any other unreadable Section 7 raises, naming the file, the section, the expected forms and the remedy (S-12(c)).
# =============================================================================

_FINDING_TABLES = ("## 3. Findings\n\n| ID | Component | Threat |\n|----|-----------|--------|\n" + "\n".join(
    "| %s | Gateway | A threat |" % finding_id for finding_id in ("S-1", "T-1", "T-2", "T-3", "T-5", "E-1", "AGP-01", "LLM-1")) + "\n\n")


def _list_md(section_7, heading="## 7. Recommended Actions", tables=_FINDING_TABLES):
    """A small threats.md whose Section 7 is ``section_7``, after finding tables that a range is checked against."""
    return "# Report\n\n" + tables + heading + "\n\n" + section_7 + "\n\n## 9. Source Attribution\n\nNothing here.\n"


_LIST_SECTION = """\
### Critical Priority

1. **S-1**: Fix the first thing.
2. **T-1 + E-1**: Fix two things together.

### High Priority (within sprint)

3. **LLM-1 — A titled action**: Fix with a title.

### Medium / Low Priority

4. **T-2 through T-5**: Fix a span.
"""


def test_the_numbered_list_form_reads_ids_text_and_priority_in_s2_order():
    reference = parse_reference_set(_list_md(_LIST_SECTION), source="run/threats.md")
    assert reference["form"] == "list" and reference["resolved"] == [] and reference["duplicates"] == []
    rows = {finding["id"]: finding for finding in reference["open"]}
    assert [finding["id"] for finding in reference["open"]] == ["S-1", "T-1", "T-2", "T-3", "T-5", "E-1", "LLM-1"], \
        "S-2 order, and T-4 is not in the file's tables, so the range keeps T-2, T-3 and T-5"
    assert rows["S-1"] == {"id": "S-1", "component": "", "threat": "", "likelihood": "—", "impact": "—",
                           "risk_level": "Critical", "mitigation": "Fix the first thing.", "agentic_pattern": "none"}
    assert rows["T-1"]["mitigation"] == rows["E-1"]["mitigation"] == "Fix two things together." and rows["E-1"]["risk_level"] == "Critical"
    assert rows["LLM-1"]["risk_level"] == "High" and rows["LLM-1"]["mitigation"] == "Fix with a title.", "the bold title is dropped"
    assert rows["T-3"]["risk_level"] == "" and rows["T-3"]["mitigation"] == "Fix a span."
    assert all("delta_status" not in finding for finding in reference["open"]), "the form has no Status"


def test_what_the_list_form_lacks_is_listed_for_every_finding():
    reference = parse_reference_set(_list_md(_LIST_SECTION))
    everything = ["component", "threat", "delta_status"]
    assert reference["lacking"] == {"S-1": everything, "T-1": everything, "E-1": everything, "LLM-1": everything,
                                    "T-2": everything + ["risk_level"], "T-3": everything + ["risk_level"], "T-5": everything + ["risk_level"]}


def test_each_lacking_value_has_the_flag_that_the_closed_vocabulary_gives_it():
    """S-12(b): `input:<field>:not-in-form`, one for each value the form lacks, sorted, on each finding that lacks any."""
    reference = parse_reference_set(_list_md(_LIST_SECTION))
    assert (FORM_LACKS_CAUSE, FORM_LACKS_FLAG) == ("not-in-form", "input:%s:not-in-form")
    assert reference["flags"]["S-1"] == ["input:component:not-in-form", "input:delta_status:not-in-form", "input:threat:not-in-form"]
    assert reference["flags"]["T-3"] == ["input:component:not-in-form", "input:delta_status:not-in-form", "input:risk_level:not-in-form",
                                         "input:threat:not-in-form"]
    assert set(reference["flags"]) == set(reference["lacking"]), "the same findings"
    assert all(flags == sorted(FORM_LACKS_FLAG % name for name in reference["lacking"][finding_id]) for finding_id, flags in reference["flags"].items())
    no_status = parse_reference_set(_ref_md(["| S-1 | Gateway | A threat | High | A fix |"], header="| Finding ID | Component | Threat | Risk Level | Mitigation |\n|---|---|---|---|---|"))
    assert no_status["flags"] == {"S-1": ["input:delta_status:not-in-form"]}
    assert parse_reference_set(_ref_md([_ref_row("S-1", "NEW")]))["flags"] == {}, "a table with every column lacks nothing"


def test_the_flag_fits_the_scorers_closed_vocabulary_in_kind_field_and_cause():
    """`<kind>:<field>:<cause>`: the kind is one of the stage record's flag kinds, the field a finding-schema name (as
    `severity_band` and `remediation_sla` are), the cause kebab-case; and a finding has at most one flag for a kind and field."""
    finding_fields = {"component", "threat", "delta_status", "risk_level"}
    for sample in ("consumer-agent-app/sample-report", "predictive-ml-app/sample-report", "maestro-reference", "mobile-banking-app/sample-report"):
        for finding_id, flags in parse_reference_set(_example_threats(sample))["flags"].items():
            assert flags == sorted(flags) and len(flags) == len({flag.rsplit(":", 1)[0] for flag in flags}), finding_id
            for flag in flags:
                kind, field, cause = flag.split(":")
                assert kind in tachi_parts.COUNT_KEYS and field in finding_fields and re.fullmatch(r"[a-z]+(-[a-z0-9]+)*", cause), flag
                assert (kind, cause) == ("input", "not-in-form")


@pytest.mark.parametrize("heading", ["Critical Priority", "CRITICAL Priority (immediate action)", "### high priority", "MEDIUM Priority (next quarter)",
                                     "LOW Priority (backlog)"])
def test_a_subheading_that_names_one_band_gives_that_risk_level(heading):
    text = _list_md("### %s\n\n1. **S-1**: Fix.\n" % heading.lstrip("# "))
    assert parse_reference_set(text)["open"][0]["risk_level"] == heading.lstrip("# ").split()[0].capitalize()


@pytest.mark.parametrize("heading", ["Medium / Low Priority", "High-impact fixes (low effort)", "Notes", "Quick wins"])
def test_a_subheading_that_names_no_band_or_several_gives_no_risk_level(heading):
    reference = parse_reference_set(_list_md("### %s\n\n1. **S-1**: Fix.\n" % heading))
    assert reference["open"][0]["risk_level"] == "" and "risk_level" in reference["lacking"]["S-1"]


@pytest.mark.parametrize("heading", ["## 7. Recommended Actions", "## Section 7: Recommended Actions", "## 7. Recommended Actions (Prioritized)",
                                     "## Section 7: Recommended Actions (Prioritized)", "### 7. Recommended Actions", "## Section 7. Recommended Actions"])
def test_section_7_is_read_under_each_heading_for_a_list_and_for_a_table(heading):
    list_reference = parse_reference_set(_list_md("1. **S-1**: Fix.\n2. **T-1**: Fix.\n", heading=heading))
    assert (list_reference["form"], [f["id"] for f in list_reference["open"]]) == ("list", ["S-1", "T-1"])
    table_reference = parse_reference_set(_ref_md([_ref_row("S-1", "NEW"), _ref_row("T-1", "UPDATED")], heading=heading))
    assert (table_reference["form"], [f["id"] for f in table_reference["open"]]) == ("table", ["S-1", "T-1"])
    assert [f["delta_status"] for f in table_reference["open"]] == ["NEW", "UPDATED"] and table_reference["lacking"] == {}


@pytest.mark.parametrize("bold,ids", [
    ("S-1", ["S-1"]), ("S-1 + T-1", ["S-1", "T-1"]), ("S-1+T-1+E-1", ["S-1", "T-1", "E-1"]), ("T-2 through T-5", ["T-2", "T-3", "T-5"]),
    ("T-2 through T-2", ["T-2"]), ("S-1 — A title", ["S-1"]), ("S-1 – A title", ["S-1"]), ("S-1 - A title", ["S-1"]),
    ("S-1 + T-1 — A title", ["S-1", "T-1"]), ("T-2 through T-5 — A title", ["T-2", "T-3", "T-5"]), ("AGP-01", ["AGP-01"]),
])
def test_the_three_spellings_of_the_bold_text_and_an_optional_title(bold, ids):
    reference = parse_reference_set(_list_md("1. **%s**: Fix.\n" % bold))
    assert sorted(f["id"] for f in reference["open"]) == sorted(ids)
    assert all(f["mitigation"] == "Fix." for f in reference["open"])


def test_a_range_is_kept_to_the_ids_the_files_tables_list_and_never_to_a_resolved_one():
    tables = _FINDING_TABLES + "## 4c. Resolved Findings\n\n| ID | Component | Threat | Last Risk Level | Resolution Reason |\n|---|---|---|---|---|\n| T-3 | Old | Gone | High | Fixed |\n\n"
    reference = parse_reference_set(_list_md("1. **T-1 through T-5**: Fix.\n", tables=tables))
    assert [f["id"] for f in reference["open"]] == ["T-1", "T-2", "T-5"], "T-3 is resolved and T-4 is in no table"
    assert [f["id"] for f in reference["resolved"]] == ["T-3"]


def test_an_id_the_list_names_twice_is_one_finding_and_the_first_item_wins():
    reference = parse_reference_set(_list_md("1. **S-1**: First.\n2. **S-1 + T-1**: Second.\n3. **AGP-01**: Third.\n4. **AGP-1**: Fourth.\n"))
    assert [(f["id"], f["mitigation"]) for f in reference["open"]] == [("S-1", "First."), ("T-1", "Second."), ("AGP-01", "Third.")]
    assert reference["duplicates"] == ["S-1", "AGP-1"]
    assert sorted(reference["lacking"]) == ["AGP-1", "S-1", "T-1"], "the lacking map is keyed by canonical ID"


def test_only_a_numbered_item_counts_and_an_indented_line_is_a_continuation():
    section = ("Some prose before the list.\n\n1. **S-1**: Fix it\n   and then keep going.\n    1. a sub-item that is not bold\n\n"
               "- a bullet note\n\n2. **T-1**: Fix.\n\n---\n")
    assert [f["id"] for f in parse_reference_set(_list_md(section))["open"]] == ["S-1", "T-1"]


def test_a_table_wins_over_a_list_in_the_same_section_and_a_list_item_never_turns_into_a_row():
    mixed = _list_md("| Finding ID | Component | Threat | Risk Level | Mitigation |\n|---|---|---|---|---|\n| S-1 | G | T | High | Fix |\n\n1. **T-1**: List.\n")
    reference = parse_reference_set(mixed)
    assert (reference["form"], [f["id"] for f in reference["open"]]) == ("table", ["S-1"])


@pytest.mark.parametrize("section,problem", [
    ("1. S-1: not bold.\n", "has a numbered item that doesn't start with a bolded finding ID (line {0})"),
    ("1. **Note**: not an ID.\n", "names 'Note', which is not a finding ID (line {0})"),
    ("1. **S-1 + X-9**: unknown prefix.\n", "names 'X-9', which is not a finding ID (line {0})"),
    ("1. **S-1**: ok.\n2. **T-1:** colon inside the bold.\n", "names 'T-1:', which is not a finding ID (line {1})"),
    ("1. **S-1, T-1**: comma-joined.\n", "names 'S-1, T-1', which is not a finding ID (line {0})"),
    ("1. **T-2 through E-1**: two prefixes.\n", "has a range that can't be read (line {0})"),
    ("1. **T-5 through T-2**: descending.\n", "has a range that can't be read (line {0})"),
    ("1. **T-1 through T-9999**: too wide.\n", "has a range that can't be read (line {0})"),
    ("1. **T-1 through X-9**: unknown.\n", "names 'X-9', which is not a finding ID (line {0})"),
    ("1. **E-5 through E-9**: none listed.\n", "has a range that names no finding the file's tables list (line {0})"),
    ("- **S-1**: a bullet list.\n- **T-1**: another.\n", "holds no table rows and no numbered list of bolded finding IDs"),
    ("Fix everything soon.\n", "holds no table rows and no numbered list of bolded finding IDs"),
    ("", "holds no table rows and no numbered list of bolded finding IDs"),
    ("1. **\u2014**: a dash placeholder.\n", "names '\u2014', which is not a finding ID (line {0})"),
], ids=["not-bold", "bold-not-an-id", "unknown-prefix", "colon-in-bold", "comma-joined", "two-prefixes", "descending", "too-wide", "unknown-range-end",
        "range-confirms-nothing", "bullets", "prose", "empty", "dash-placeholder"])
def test_any_other_section_7_raises_naming_the_file_the_section_the_forms_and_the_remedy(section, problem):
    """S-12(c): the run ends before any agent is dispatched. A finding is never lost without a word."""
    content = _list_md(section)
    first = content.split("\n").index(section.split("\n")[0]) + 1 if section else 0
    with pytest.raises(ReferenceSetError) as raised:
        parse_reference_set(content, source="run/threats.md")
    error = raised.value
    assert error.reason == "run/threats.md: Section 7 (Recommended Actions) " + problem.format(first, first + 1)
    assert "'Finding ID' column" in error.expected and "numbered list" in error.expected and "bolded finding ID" in error.expected
    assert "table form" in error.remedy and "numbered-list form" in error.remedy and "/tachi.threat-model" in error.remedy
    assert str(error) == "%s. Expected %s. Remedy: %s" % (error.reason, error.expected, error.remedy)


def test_a_range_with_no_finding_tables_to_check_it_against_raises():
    with pytest.raises(ReferenceSetError) as raised:
        parse_reference_set(_list_md("1. **T-2 through T-3**: Fix.\n", tables=""))
    assert "has a range, and the file has no finding tables to check it against (line 5)" in raised.value.reason, raised.value.reason


def test_a_table_section_7_that_the_old_reader_read_is_read_the_same_and_nothing_it_lacks_is_a_surprise():
    full = parse_reference_set(_ref_md([_ref_row("S-1", "NEW"), _ref_row("T-1", "UNCHANGED")]))
    assert full["form"] == "table" and full["lacking"] == {}
    no_status = parse_reference_set(_ref_md(["| S-1 | Gateway | A threat | High | A fix |"], header="| Finding ID | Component | Threat | Risk Level | Mitigation |\n|---|---|---|---|---|"))
    assert no_status["lacking"] == {"S-1": ["delta_status"]}
    bare = parse_reference_set(_ref_md(["| S-1 | High | A fix |"], header="| Finding ID | Risk Level | Mitigation |\n|---|---|---|"))
    assert bare["lacking"] == {"S-1": ["component", "threat", "delta_status"]}


def test_the_unchanged_parsers_still_say_nothing_for_a_list_form_file(capsys):
    """FR-E.16: `parse_threats_findings` is unchanged for the extractors, which rely on `[]` and its warning."""
    content = _list_md(_LIST_SECTION)
    assert parse_threats_findings(content) == []
    assert "could not find Recommended Actions table" in capsys.readouterr().err
    assert delta_status_by_id(content) == ({}, False, 0)


# ---- the shipped drift-form samples, as read-only inputs --------------------------------------------------------------

_CONSUMER_IDS = ["S-1", "S-2", "T-1", "T-2", "T-3", "R-1", "R-2", "I-1", "I-2", "I-3", "D-1", "D-2", "D-3", "E-1", "TE-1", "TE-2", "TE-3", "TE-4", "TE-5"]


def test_the_consumer_agent_app_sample_reads_as_a_list_under_a_section_7_heading():
    """`## Section 7: Recommended Actions (Prioritized)`, items `N. **ID — Title**: text` under CRITICAL, HIGH, MEDIUM and LOW."""
    reference = parse_reference_set(_example_threats("consumer-agent-app/sample-report"), source="threats.md")
    assert reference["form"] == "list" and reference["resolved"] == [] and reference["duplicates"] == []
    assert [finding["id"] for finding in reference["open"]] == _CONSUMER_IDS
    levels = {finding["id"]: finding["risk_level"] for finding in reference["open"]}
    assert levels["TE-5"] == "Critical" and levels["TE-1"] == levels["S-1"] == "High" and levels["S-2"] == "Medium" and levels["R-2"] == "Low"
    assert reference["lacking"] == {finding_id: ["component", "threat", "delta_status"] for finding_id in _CONSUMER_IDS}
    assert reference["flags"] == {finding_id: ["input:component:not-in-form", "input:delta_status:not-in-form", "input:threat:not-in-form"]
                                  for finding_id in _CONSUMER_IDS}
    rows = {finding["id"]: finding for finding in reference["open"]}
    assert rows["TE-5"]["mitigation"].startswith("implement vulnerable-population safeguards layer")
    assert rows["S-1"]["mitigation"].startswith("deploy multi-factor authentication")
    members = parse_sarif_member_set(_shipped_sarif("consumer-agent-app/sample-report/threats.sarif"))["members"]
    assert sorted(members, key=tachi_parts.finding_sort_key) == _CONSUMER_IDS, "the same 19 findings as the sample's own SARIF"


def test_the_predictive_ml_app_sample_reads_as_a_list_with_ranges_and_joined_ids():
    """`## 7. Recommended Actions (Prioritized)`: `**T-10**`, `**LLM-3 + LLM-4**` and `**T-2 through T-9**` under Critical,
    High and `Medium / Low` subheadings. Section 7 lists 37 of the file's 49 findings, and that is the reference set."""
    reference = parse_reference_set(_example_threats("predictive-ml-app/sample-report"))
    ids = [finding["id"] for finding in reference["open"]]
    assert reference["form"] == "list" and len(ids) == len(set(ids)) == 37
    for span in (["T-2", "T-3", "T-4", "T-5", "T-6", "T-7", "T-8", "T-9"], ["E-1", "E-2", "E-3", "E-4", "E-5"],
                 ["R-1", "R-2", "R-3", "R-4", "R-5", "R-6", "R-7"], ["D-1", "D-2", "D-3", "D-4", "D-5", "D-6"]):
        assert set(span) <= set(ids), span
    rows = {finding["id"]: finding for finding in reference["open"]}
    assert rows["T-10"]["risk_level"] == "Critical" and rows["S-5"]["risk_level"] == rows["T-7"]["risk_level"] == "High"
    assert rows["LLM-3"]["mitigation"] == rows["LLM-4"]["mitigation"] and rows["D-10"]["mitigation"] == rows["D-11"]["mitigation"]
    assert rows["T-10"]["source_attribution"][0] == {"taxonomy": "owasp", "id": "ML01", "relationship": "primary"}
    unleveled = sorted(finding_id for finding_id, finding in rows.items() if not finding["risk_level"])
    assert unleveled == ["D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "R-1", "R-2", "R-3", "R-4", "R-5", "R-6", "R-7"], "`Medium / Low Priority`"
    assert all(names == ["component", "threat", "delta_status"] + (["risk_level"] if finding_id in unleveled else [])
               for finding_id, names in reference["lacking"].items()) and len(reference["lacking"]) == 37
    assert sum(len(flags) for flags in reference["flags"].values()) == 37 * 3 + 13, "four flags on the 13 with no risk level, three on the rest"
    absent = {"I-1", "I-2", "I-3", "I-4", "I-5", "I-6", "I-7", "S-1", "S-2", "S-3", "S-4", "T-1"}
    members = set(parse_sarif_member_set(_shipped_sarif("predictive-ml-app/sample-report/threats.sarif"))["members"])
    assert members == set(ids) | absent and not (absent & set(ids)), "the other 12 of the file's 49 findings are not in its Section 7"


def test_the_maestro_reference_sample_is_a_table_without_a_status_column_and_lists_one_finding_twice():
    reference = parse_reference_set(_example_threats("maestro-reference"))
    assert reference["form"] == "table" and reference["duplicates"] == ["I-17"] and len(reference["open"]) == 110
    assert set(tuple(names) for names in reference["lacking"].values()) == {("delta_status",)} and len(reference["lacking"]) == 110


def test_the_shipped_table_samples_with_every_column_lack_nothing():
    for relative in ("agentic-app", "web-app", "microservices"):
        reference = parse_reference_set(_example_threats(relative))
        assert reference["form"] == "table" and reference["lacking"] == {}, relative


# =============================================================================
# Feature 374 (W2, T057): the controls file in K8's corrected format and in the pre-fix format (FR-K8.1, FR-K8.2)
#
# Both parse to the same rows. K8's one Section 2 schema adds MAESTRO Layer and Control Category to the pre-fix columns
# (CF is in both), and the parser reads each by header name, per band table. A row only gains keys.
# =============================================================================

# id, CF, component, MAESTRO layer, control category, threat, inherent, inherent band, control status, residual, residual band
_CONTROL_ROWS = [
    ("T-1", "—", "API Gateway", "L4 — Deployment and Infrastructure", "Rate Limiting", "A denial of service threat", "7.5", "High",
     "No Control Found", "7.5", "High"),
    ("S-2", "CF", "Auth Service", "L3 — Agent Frameworks", "Authentication", "A spoofing threat", "9.1", "Critical",
     "Partial Control", "5.5", "Medium"),
    ("E-3", "—", "Admin UI", "L7 — Agent Ecosystem", "Access Control", "An elevation threat", "6.0", "Medium",
     "Control Found", "3.0", "Low"),
]
_PREFIX_HEADER = ["Threat ID", "CF", "Component", "Threat", "Inherent Score", "Inherent Severity", "Control Status", "Residual Score", "Residual Severity"]
_K8_HEADER = ["Threat ID", "CF", "Component", "MAESTRO Layer", "Threat", "Inherent Score", "Inherent Severity", "Control Status",
              "Control Category", "Residual Score", "Residual Severity"]
_ROW_FIELDS = ["Threat ID", "CF", "Component", "MAESTRO Layer", "Control Category", "Threat", "Inherent Score", "Inherent Severity",
               "Control Status", "Residual Score", "Residual Severity"]


def _control_table(header, rows):
    cells = lambda values: "| " + " | ".join(values) + " |"  # noqa: E731
    named = [dict(zip(_ROW_FIELDS, row)) for row in rows]
    return "\n".join([cells(header), cells(["---"] * len(header))] + [cells([row[name] for name in header]) for row in named])


def _controls_md(header, rows=_CONTROL_ROWS, omit_empty_bands=False, tail=""):
    """A compensating-controls.md with ``header`` for every band table. The pre-fix file lists all four bands."""
    by_band = {band: [row for row in rows if row[10] == band] for band in ("Critical", "High", "Medium", "Low")}
    sections = []
    for band, in_band in by_band.items():
        if not in_band and omit_empty_bands:
            continue
        sections.append("### %s Residual Severity\n\n%s\n" % (band, _control_table(header, in_band)))
    return ("---\nschema_version: \"1.0\"\n---\n\n# Compensating Controls Report\n\n## 1. Executive Summary\n\n"
            "**3** threats analyzed\n\n**Risk Reduction**: 22.6 inherent -> 16.0 residual (**29.2%** reduction)\n\n"
            "**Coverage Distribution:**\n\n| Status | Count | Percentage |\n|---|---|---|\n| Control Found | 1 | 33% |\n"
            "| Partial Control | 1 | 33% |\n| No Control Found | 1 | 33% |\n\n---\n\n## 2. Coverage Matrix\n\n" + "\n".join(sections) +
            "\n### Summary Statistics\n\n| Residual Severity | Count | Percentage |\n|---|---|---|\n| High | 1 | 33% |\n\n---\n\n"
            "## 3. Control Details\n\n### Authentication\n\n#### CTRL-1 — Token validation\n\n"
            "**Category**: Authentication | **Status**: Found | **Effectiveness**: Medium\n\n**Detected in**: `src/auth.py:12`\n\n"
            "**Threats Mitigated by This Control**:\n\n| Threat ID | Component | Threat | Inherent Score |\n|---|---|---|---|\n"
            "| S-2 | Auth Service | A spoofing threat | 9.1 |\n\n---\n\n## 4. Recommendations\n\nActionable recommendations.\n\n"
            "### Critical / High Risk Gaps\n\n#### 1. S-2 — Auth Service (Composite: 9.1, Critical)\n\n**Current Status**: Partial Control\n\n"
            "**What to Implement**: Harden the token check.\n\n**Where to Implement**: `src/auth.py`\n\n**Effort Estimate**: Medium\n\n"
            "#### 2. T-1 — API Gateway (Composite: 7.5, High)\n\n**Current Status**: No Control Found\n\n"
            "**What to Implement**: Add a rate limit.\n\n**Effort Estimate**: Low\n\n---\n\n## 5. Residual Risk Summary\n\nText.\n" + tail)


_K8_SECTION_7 = ("\n## 7. Analysis Integrity\n\n### Input Issues\n\nNone.\n\n### Assessment Inputs\n\n| ID | Field | Value |\n|---|---|---|\n"
                 "| S-2 | control_status | partial |\n")
_NEW_CONTROL_KEYS = ("maestro_layer", "control_category")


def _without_k8_cells(result):
    return dict(result, findings=[{key: value for key, value in finding.items() if key not in _NEW_CONTROL_KEYS} for finding in result["findings"]])


def test_a_controls_file_in_either_format_parses_to_the_same_rows():
    pre_fix = parse_compensating_controls_md(_controls_md(_PREFIX_HEADER))
    corrected = parse_compensating_controls_md(_controls_md(_K8_HEADER, omit_empty_bands=True, tail=_K8_SECTION_7))
    assert [f["id"] for f in pre_fix["findings"]] == ["T-1", "S-2", "E-3"], "by residual band: High, Medium, Low"
    assert _without_k8_cells(corrected) == _without_k8_cells(pre_fix), "the same findings, totals, matrix, controls and recommendations"
    by_id = {finding["id"]: finding for finding in corrected["findings"]}
    assert by_id["S-2"]["recommendation"] == "Harden the token check." and by_id["T-1"]["recommendation"] == "Add a rate limit."
    assert by_id["E-3"]["recommendation"] == "" and by_id["S-2"]["status_class"] == "partial"
    assert pre_fix["controls"] == corrected["controls"] and len(corrected["controls"]) == 1


def test_the_corrected_format_adds_maestro_layer_and_control_category_and_the_pre_fix_format_leaves_them_empty():
    corrected = {f["id"]: f for f in parse_compensating_controls_md(_controls_md(_K8_HEADER))["findings"]}
    pre_fix = {f["id"]: f for f in parse_compensating_controls_md(_controls_md(_PREFIX_HEADER))["findings"]}
    for row in _CONTROL_ROWS:
        assert corrected[row[0]]["maestro_layer"] == row[3] and corrected[row[0]]["control_category"] == row[4]
        assert pre_fix[row[0]]["maestro_layer"] == "" and pre_fix[row[0]]["control_category"] == ""


@pytest.mark.parametrize("order", [
    ["Threat ID", "CF", "Component", "MAESTRO Layer", "Threat", "Inherent Score", "Inherent Severity", "Control Status", "Control Category",
     "Residual Score", "Residual Severity"],
    ["Control Category", "MAESTRO Layer", "Threat ID", "Component", "Threat", "CF", "Inherent Score", "Inherent Severity", "Control Status",
     "Residual Score", "Residual Severity"],
], ids=["the-agent-spec-order", "another-order"])
def test_the_columns_are_read_by_header_name_wherever_they_sit(order):
    findings = {f["id"]: f for f in parse_compensating_controls_md(_controls_md(order))["findings"]}
    assert findings["S-2"]["maestro_layer"] == "L3 — Agent Frameworks" and findings["S-2"]["control_category"] == "Authentication"
    assert findings["S-2"]["carried_forward"] is True and findings["T-1"]["carried_forward"] is False
    assert findings["T-1"]["component"] == "API Gateway" and findings["T-1"]["residual_severity"] == "High"


@pytest.mark.parametrize("header", ["MAESTRO Layer.", "maestro layer", "MAESTRO  Layer", "**MAESTRO Layer**"])
def test_the_added_headers_are_matched_the_way_the_other_aliases_are(header):
    table = ("### High Residual Severity\n\n| Threat ID | %s | Control Category. | Threat | Inherent | Status | Residual |\n|---|---|---|---|---|---|---|\n"
             "| T-1 | L1 | Encryption | A threat | 7.5 | No Control Found | 7.5 |\n" % header)
    (finding,) = parse_compensating_controls_md("## 2. Coverage Matrix\n\n" + table)["findings"]
    assert (finding["maestro_layer"], finding["control_category"]) == ("L1", "Encryption")


@pytest.mark.parametrize("cell,carried", [("CF", True), ("cf", True), ("**CF**", True), (" CF ", True), ("—", False), ("-", False), ("", False),
                                          ("Y", False), ("carried", False), ("CF*", False)])
def test_the_cf_marker_is_a_carried_forward_row_only_when_the_cell_is_cf(cell, carried):
    table = ("### High Residual Severity\n\n| Threat ID | CF | Component | Threat | Inherent | Status | Residual |\n|---|---|---|---|---|---|---|\n"
             "| T-1 | %s | API | A threat | 7.5 | No Control Found | 7.5 |\n" % cell)
    (finding,) = parse_compensating_controls_md("## 2. Coverage Matrix\n\n" + table)["findings"]
    assert finding["carried_forward"] is carried


def test_a_table_with_no_cf_column_has_no_carried_rows():
    table = "### High Residual Severity\n\n| Threat ID | Component | Threat | Inherent | Status | Residual |\n|---|---|---|---|---|---|\n| T-1 | API | A threat | 7.5 | No Control Found | 7.5 |\n"
    (finding,) = parse_compensating_controls_md("## 2. Coverage Matrix\n\n" + table)["findings"]
    assert finding["carried_forward"] is False and finding["maestro_layer"] == ""


def test_a_drifted_file_that_mixes_the_two_schemas_between_bands_reads_each_table_by_its_own_header():
    """The drift K8 removes: before the fix, one file's band tables could carry different columns."""
    rows = _CONTROL_ROWS
    high_and_medium = _controls_md(_PREFIX_HEADER).replace(
        _control_table(_PREFIX_HEADER, [row for row in rows if row[10] == "Medium"]), _control_table(_K8_HEADER, [row for row in rows if row[10] == "Medium"]))
    findings = {f["id"]: f for f in parse_compensating_controls_md(high_and_medium)["findings"]}
    assert findings["S-2"]["control_category"] == "Authentication" and findings["T-1"]["control_category"] == ""
    assert _without_k8_cells(parse_compensating_controls_md(high_and_medium)) == _without_k8_cells(parse_compensating_controls_md(_controls_md(_PREFIX_HEADER)))


def test_an_empty_band_table_and_an_omitted_band_heading_read_the_same():
    kept = parse_compensating_controls_md(_controls_md(_K8_HEADER))
    omitted = parse_compensating_controls_md(_controls_md(_K8_HEADER, omit_empty_bands=True))
    assert kept == omitted and "### Critical Residual Severity" in _controls_md(_K8_HEADER) and "### Critical Residual Severity" not in _controls_md(_K8_HEADER, omit_empty_bands=True)


def test_the_corrected_formats_section_7_and_its_group_headings_change_nothing():
    plain = parse_compensating_controls_md(_controls_md(_K8_HEADER))
    with_integrity = parse_compensating_controls_md(_controls_md(_K8_HEADER, tail=_K8_SECTION_7))
    assert plain == with_integrity


def test_the_extractors_controls_readers_give_the_same_report_data_for_both_formats(extract_report_data):
    """Tier 1 reads the controls file through the parser, so the PDF's findings, recommendations and roadmap are the same."""
    outputs = []
    for header, md in ((_PREFIX_HEADER, _controls_md(_PREFIX_HEADER)), (_K8_HEADER, _controls_md(_K8_HEADER, omit_empty_bands=True, tail=_K8_SECTION_7))):
        data = parse_compensating_controls_md(md)
        findings = data["findings"]
        extract_report_data._apply_recommendation_fallback(findings, "")
        outputs.append({
            "section_4": extract_report_data._section4_has_content(md),
            "typst": [extract_report_data._format_finding(finding, 1) for finding in findings],
            "roadmap": extract_report_data.build_remediation_actions(findings, 1, cc_data=data),
            "controls": data["controls"], "matrix": data["coverage_matrix"], "summary": data["coverage_summary"], "severity": data["severity"]})
    assert outputs[0] == outputs[1]
    assert outputs[0]["section_4"] is True and len(outputs[0]["typst"]) == 3
    assert [action["recommendation"] for action in outputs[0]["roadmap"]] == [
        "Add a rate limit.", "Harden the token check.", extract_report_data.REC_PLACEHOLDER], "the §4 blocks joined their findings"


def test_every_shipped_controls_file_reads_as_the_pre_fix_format():
    paths = sorted((REPO_ROOT / "examples").rglob("compensating-controls.md"))
    assert len(paths) == 5
    for path in paths:
        findings = parse_compensating_controls_md(path.read_text(encoding="utf-8"))["findings"]
        assert findings and all(f["maestro_layer"] == f["control_category"] == "" and f["carried_forward"] is False for f in findings), path.parent.name


# =============================================================================
# Feature 374 (W2, T143): the controls file's persisted inputs, parse_controls_assessment_inputs (AR-T3)
#
# `### Assessment Inputs` holds each finding's whole controls result as `| ID | Field | Value |` rows (contracts/
# module-signatures.md): one row per value that exists, the field a dotted address (`evidence.0.summary`), each value
# escaped on write by D3's table-cell rule. The reader decodes it once, checks the closed values, and returns the
# items, so a carried result is escaped once per render and reads back byte for byte.
# =============================================================================

_RATINGS = {"coverage": "High", "configuration": "Medium", "currency": "Low", "completeness": "High"}

_PARTIAL_ITEM = {
    "control_status": "partial", "control_category": "input-validation", "confidence": "Medium", "carried_forward": False,
    "evidence": [
        {"file": "src/validate.py", "line": 42, "language": "python",
         "snippet": "if a < b && c > d:\n    run(\"x|y\")  # `tick` & {{7*7}}",
         "summary": "Checks a < b and a | b only",
         "assessment": {name: {"rating": rating, "rationale": "The %s check is {{count:evidence}} deep, &lt; kept" % name}
                        for name, rating in _RATINGS.items()}},
        {"file": "src/forms/parse.ts", "line": 7, "language": "typescript", "snippet": "const ok = a>b;", "summary": "A second place"},
    ],
    "matrix_row": "| S-2 | CF | Auth Service | L3 — Agent Frameworks | A <threat> | {{score:inherent}} | {{band:inherent}} | Partial Control | "
                  "input-validation | {{score:residual}} | {{band:residual}} |",
    "recommendation_body": "**What to Implement**: Validate `a` and `b`.\nAnd escape the | character, keeping &amp; as written.\n\n"
                           "**Effort Estimate**: Low",
}
_MISSING_ITEM = {
    "control_status": "missing", "control_category": "authentication", "confidence": None, "carried_forward": True, "evidence": [],
    "matrix_row": "| T-1 | — | API | L1 | A threat | {{score:inherent}} | {{band:inherent}} | No Control Found | authentication | "
                  "{{score:residual}} | {{band:residual}} |",
    "recommendation_body": "**What to Implement**: Add one.",
}
_FOUND_ITEM = {
    "control_status": "found", "control_category": "csp-security-headers", "confidence": "High", "carried_forward": False,
    "evidence": [{"file": "web/headers.py", "line": 3, "language": "python", "snippet": "set_csp()", "summary": "A CSP header"}],
    "matrix_row": "| E-3 | — | Web | L2 | A threat | {{score:inherent}} | {{band:inherent}} | Control Found | csp-security-headers | "
                  "{{score:residual}} | {{band:residual}} |",
    "recommendation_body": None,
}
_PERSISTED = {"S-2": _PARTIAL_ITEM, "T-1": _MISSING_ITEM, "E-3": _FOUND_ITEM}


def _addressed_values(item):
    """The (field address, text, kept slots?) of every value that exists, in the payload's key order."""
    out = []
    for name in ("control_status", "control_category", "confidence", "carried_forward"):
        value = item[name]
        if value is not None:
            out.append((name, ("true" if value else "false") if name == "carried_forward" else value, False))
    for index, entry in enumerate(item["evidence"]):
        for name in ("file", "line", "language", "snippet", "summary"):
            out.append(("evidence.%d.%s" % (index, name), str(entry[name]), False))
        for dimension in tachi_parts.ASSESSMENT_DIMENSIONS if "assessment" in entry else ():
            out.append(("evidence.%d.assessment.%s.rating" % (index, dimension), entry["assessment"][dimension]["rating"], False))
            out.append(("evidence.%d.assessment.%s.rationale" % (index, dimension), entry["assessment"][dimension]["rationale"], True))
    out.append(("matrix_row", item["matrix_row"], True))
    if item["recommendation_body"] is not None:
        out.append(("recommendation_body", item["recommendation_body"], False))
    return out


def _persisted_table(items, order=None, spelling=None):
    """What a renderer writes: rows in S-2 order of ID, then the payload's key order, each value escaped for a cell."""
    ids = order or sorted(items, key=tachi_parts.finding_sort_key)
    rows = ["| ID | Field | Value |", "|----|-------|-------|"]
    for finding_id in ids:
        for field, text, keep in _addressed_values(items[finding_id]):
            rows.append("| %s | %s | %s |" % ((spelling or {}).get(finding_id, finding_id), field, tachi_parts.escape_cell(text, keep_slots=keep)))
    return "\n".join(rows) + "\n"


def _controls_with_inputs(table, heading="### Assessment Inputs"):
    return "## 6. Methodology\n\nText.\n\n## 7. Analysis Integrity\n\n### Input Issues\n\nNone.\n\n" + heading + "\n\n" + table + "\n"


def test_the_persisted_inputs_read_back_each_controls_item_as_it_was_written():
    read = parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table(_PERSISTED)))
    assert read["errors"] == []
    assert list(read["inputs"]) == ["S-2", "T-1", "E-3"], "S-2 order: the S prefix, then T, then E"
    for finding_id, item in _PERSISTED.items():
        assert read["inputs"][finding_id] == item, finding_id
    assert list(read["inputs"]["S-2"]) == ["control_status", "control_category", "confidence", "carried_forward", "evidence", "matrix_row",
                                           "recommendation_body"], "the payload's key order, without finding_id"


def test_a_carried_value_is_written_the_same_bytes_again_so_escaping_never_compounds():
    """AR-T3, D16: an UNCHANGED result whose evidence holds `&lt;` and `|` is carried across two runs byte for byte."""
    first = _persisted_table(_PERSISTED)
    second = _persisted_table(parse_controls_assessment_inputs(_controls_with_inputs(first))["inputs"])
    assert second == first
    third = _persisted_table(parse_controls_assessment_inputs(_controls_with_inputs(second))["inputs"])
    assert third == first
    assert "&amp;lt;" in first and "&#124;" in first and "&#10;" in first, "the carried text holds references of its own"
    snippet = parse_controls_assessment_inputs(_controls_with_inputs(first))["inputs"]["S-2"]["evidence"][0]["snippet"]
    assert snippet == _PARTIAL_ITEM["evidence"][0]["snippet"] and "a < b && c > d" in snippet and "{{7*7}}" in snippet


def test_narrative_and_matrix_row_slots_survive_and_a_value_is_never_decoded_twice():
    item = parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table(_PERSISTED)))["inputs"]["S-2"]
    assert "{{score:inherent}}" in item["matrix_row"] and "{{band:residual}}" in item["matrix_row"]
    assert item["evidence"][0]["assessment"]["coverage"]["rationale"] == "The coverage check is {{count:evidence}} deep, &lt; kept"
    assert item["recommendation_body"].count("&amp;") == 1, "an `&amp;` the agent wrote stays one"


def test_a_value_may_hold_every_character_the_cell_escape_covers():
    nasty = "a & b < c > d | e ` f {{ g }} {{{score:x}}\nsecond & line # not a heading"
    item = dict(_FOUND_ITEM, evidence=[dict(_FOUND_ITEM["evidence"][0], summary=nasty, snippet=nasty)])
    read = parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table({"E-3": item})))
    assert read["errors"] == [] and read["inputs"]["E-3"] == item


def test_a_pre_1_1_file_has_no_persisted_inputs():
    for text in ("", "# Report\n\n## 2. Coverage Matrix\n\n| Threat ID | CF |\n|---|---|\n| T-1 | — |\n", _controls_md(_PREFIX_HEADER),
                 _controls_md(_K8_HEADER, tail=_K8_SECTION_7.replace("### Assessment Inputs", "### Something Else"))):
        assert parse_controls_assessment_inputs(text) == {"inputs": {}, "errors": []}
    assert parse_controls_assessment_inputs(None) == {"inputs": {}, "errors": []}
    for path in sorted((REPO_ROOT / "examples").rglob("compensating-controls.md")):
        assert parse_controls_assessment_inputs(path.read_text(encoding="utf-8")) == {"inputs": {}, "errors": []}, path.parent.name


def test_a_heading_with_no_row_gives_nothing_and_the_other_parsers_leave_the_section_alone():
    assert parse_controls_assessment_inputs(_controls_with_inputs("| ID | Field | Value |\n|---|---|---|\n")) == {"inputs": {}, "errors": []}
    assert parse_controls_assessment_inputs(_controls_with_inputs("Nothing was persisted.\n")) == {"inputs": {}, "errors": []}
    persisted = _controls_md(_K8_HEADER, tail="\n## 7. Analysis Integrity\n\n### Assessment Inputs\n\n" + _persisted_table(_PERSISTED))
    assert parse_compensating_controls_md(persisted) == parse_compensating_controls_md(_controls_md(_K8_HEADER))
    assert set(parse_controls_assessment_inputs(persisted)["inputs"]) == {"T-1", "S-2", "E-3"}


def test_the_id_cell_takes_any_spelling_and_the_item_is_keyed_by_the_canonical_id():
    item = dict(_FOUND_ITEM)
    read = parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table({"AGP-1": item}, spelling={"AGP-1": "AGP-01"})))
    assert list(read["inputs"]) == ["AGP-1"] and read["inputs"]["AGP-1"] == item


def test_findings_come_in_s2_order_whatever_order_the_rows_are_in():
    table = _persisted_table(_PERSISTED, order=["E-3", "T-1", "S-2"])
    assert list(parse_controls_assessment_inputs(_controls_with_inputs(table))["inputs"]) == ["S-2", "T-1", "E-3"]


@pytest.mark.parametrize("field,value,reason", [
    ("control_status", "sort-of", "control_status is not found, partial or missing"),
    ("control_category", "Authentication", "control_category is not one of the eight categories"),
    ("confidence", "Certain", "confidence is not High, Medium or Low"),
    ("carried_forward", "yes", "carried_forward is not true or false"),
    ("evidence.0.file", "/etc/passwd", "evidence.file breaks D7's relative path rule"),
    ("evidence.0.file", "a/../b.py", "evidence.file breaks D7's relative path rule"),
    ("evidence.0.file", "https://x.example/a.py", "evidence.file breaks D7's relative path rule"),
    ("evidence.0.file", "a" * 301, "evidence.file breaks D7's relative path rule"),
    ("evidence.0.line", "0", "evidence.line is not an integer of 1 or more"),
    ("evidence.0.line", "007", "evidence.line is not an integer of 1 or more"),
    ("evidence.0.line", "4.5", "evidence.line is not an integer of 1 or more"),
    ("evidence.0.line", "-3", "evidence.line is not an integer of 1 or more"),
    ("evidence.0.language", "Python 3", "evidence.language does not match the language pattern"),
    ("matrix", "x", "'matrix' is not a field of a controls item"),
    ("finding_id", "T-9", "'finding_id' is not a field of a controls item"),
    ("evidence.5.file", "a.py", "'evidence.5.file' is not a field of a controls item"),
    ("evidence.00.file", "a.py", "'evidence.00.file' is not a field of a controls item"),
    ("evidence.0.owner", "me", "'evidence.0.owner' is not a field of a controls item"),
    ("evidence.0.assessment.speed.rating", "High", "'evidence.0.assessment.speed.rating' is not a field of a controls item"),
    ("evidence.0.assessment.coverage.score", "High", "'evidence.0.assessment.coverage.score' is not a field of a controls item"),
    ("evidence.0.assessment.coverage.rating", "Great", "rating is not High, Medium or Low"),
    ("evidence..file", "a.py", "'evidence..file' is not a field of a controls item"),
    ("EVIDENCE.0.file", "a.py", "'EVIDENCE.0.file' is not a field of a controls item"),
])
def test_a_row_that_breaks_its_class_or_names_no_field_of_the_payload_is_an_error_and_its_item_is_left_out(field, value, reason, capsys):
    table = _persisted_table({"E-3": _FOUND_ITEM, "T-1": _MISSING_ITEM}).split("\n")
    at = next(index for index, row in enumerate(table) if row.startswith("| E-3 | evidence.0.summary |"))
    table[at] = "| E-3 | %s | %s |" % (field, value)
    text = _controls_with_inputs("\n".join(table))
    read = parse_controls_assessment_inputs(text)
    line = text.split("\n").index(table[at]) + 1
    assert [e["reason"] for e in read["errors"]] == [reason]
    assert read["errors"][0]["line"] == line and read["errors"][0]["row"] == table[at][:200], "the row is cut at 200 characters"
    assert list(read["inputs"]) == ["T-1"] and read["inputs"]["T-1"] == _MISSING_ITEM, "the other finding is unaffected"
    capsys.readouterr()


def test_a_row_with_a_bad_id_or_too_few_cells_is_an_error_and_a_repeated_value_spoils_its_item(capsys):
    table = _persisted_table({"E-3": _FOUND_ITEM, "T-1": _MISSING_ITEM}).rstrip("\n").split("\n") + [
        "| X-9 | control_status | found |", "| T-1 | control_status |", "| T-1 | control_status | partial |"]
    text = _controls_with_inputs("\n".join(table))
    read = parse_controls_assessment_inputs(text)
    lines = text.split("\n")
    assert [(e["row"], e["reason"]) for e in read["errors"]] == [
        ("| X-9 | control_status | found |", "names 'X-9', which is not a finding ID"),
        ("| T-1 | control_status |", "has fewer cells than the table's header"),
        ("| T-1 | control_status | partial |", "T-1 repeats the value control_status")]
    assert [e["line"] for e in read["errors"]] == [lines.index(e["row"]) + 1 for e in read["errors"]]
    assert list(read["inputs"]) == ["E-3"], "T-1 is left out"
    capsys.readouterr()


@pytest.mark.parametrize("drop,reason", [
    ("control_status", "it has no control_status row"), ("control_category", "it has no control_category row"),
    ("carried_forward", "it has no carried_forward row"), ("matrix_row", "it has no matrix_row row"),
    ("confidence", "confidence is written exactly when the status isn't missing"),
    ("recommendation_body", None),
    ("evidence.0.file", "evidence entry 0 has no file row"), ("evidence.0.summary", "evidence entry 0 has no summary row"),
])
def test_an_incomplete_item_is_left_out_with_one_error_at_its_first_row(drop, reason):
    """The part validator's rules, applied on read: a result that couldn't be a part's isn't carried. A found item has no
    recommendation_body, so dropping it changes nothing: that row doesn't exist."""
    rows = [row for row in _persisted_table({"E-3": _FOUND_ITEM}).split("\n") if not row.startswith("| E-3 | %s |" % drop)]
    read = parse_controls_assessment_inputs(_controls_with_inputs("\n".join(rows)))
    if reason is None:
        assert read["errors"] == [] and read["inputs"]["E-3"] == _FOUND_ITEM
        return
    assert list(read["inputs"]) == [] and len(read["errors"]) == 1
    assert read["errors"][0]["reason"] == "E-3: " + reason and read["errors"][0]["row"].startswith("| E-3 | ")


@pytest.mark.parametrize("items,target,extra_row,reason", [
    ({"E-3": _FOUND_ITEM}, "E-3", "| E-3 | recommendation_body | Do more. |", "recommendation_body is written exactly when the status isn't found"),
    ({"T-1": _MISSING_ITEM}, "T-1", "| T-1 | evidence.0.file | a.py |", "evidence has 1 to 5 entries for found or partial, and none for missing"),
    ({"T-1": _MISSING_ITEM}, "T-1", "| T-1 | confidence | High |", "confidence is written exactly when the status isn't missing"),
    ({"E-3": _FOUND_ITEM}, "E-3", "| E-3 | evidence.1.file | a.py |", "evidence entry 1 has no line row"),
], ids=["found-with-a-recommendation", "missing-with-evidence", "missing-with-a-confidence", "a-second-entry-with-only-a-file"])
def test_an_item_that_contradicts_its_own_status_is_left_out(items, target, extra_row, reason):
    rows = _persisted_table(items).rstrip("\n").split("\n") + [extra_row]
    read = parse_controls_assessment_inputs(_controls_with_inputs("\n".join(rows)))
    assert read["inputs"] == {} and [e["reason"] for e in read["errors"]] == ["%s: %s" % (target, reason)]
    assert read["errors"][0]["row"].startswith("| %s | " % target)


def test_a_partial_item_with_no_recommendation_is_left_out():
    rows = [row for row in _persisted_table({"S-2": _PARTIAL_ITEM}).split("\n") if "recommendation_body" not in row]
    read = parse_controls_assessment_inputs(_controls_with_inputs("\n".join(rows)))
    assert read["inputs"] == {} and [e["reason"] for e in read["errors"]] == ["S-2: recommendation_body is written exactly when the status isn't found"]


def test_evidence_entries_are_indexed_from_zero_without_a_gap_and_at_most_five():
    table = _persisted_table({"S-2": _PARTIAL_ITEM}).replace("evidence.1.", "evidence.2.")
    read = parse_controls_assessment_inputs(_controls_with_inputs(table))
    assert read["inputs"] == {} and read["errors"][0]["reason"] == "S-2: the evidence entries are not indexed from 0 without a gap"
    six = dict(_PARTIAL_ITEM, evidence=[_PARTIAL_ITEM["evidence"][1]] * 6)
    read = parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table({"S-2": six})))
    assert read["inputs"] == {} and read["errors"] and all("not a field of a controls item" in e["reason"] for e in read["errors"])
    five = dict(_PARTIAL_ITEM, evidence=[_PARTIAL_ITEM["evidence"][1]] * 5)
    assert parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table({"S-2": five})))["inputs"]["S-2"] == five


def test_an_assessment_is_all_four_dimensions_or_none():
    rows = [row for row in _persisted_table({"S-2": _PARTIAL_ITEM}).split("\n") if "assessment.currency" not in row]
    read = parse_controls_assessment_inputs(_controls_with_inputs("\n".join(rows)))
    assert read["inputs"] == {} and read["errors"][0]["reason"] == "S-2: evidence entry 0 has an incomplete assessment"
    only_rating = [row for row in _persisted_table({"S-2": _PARTIAL_ITEM}).split("\n") if "assessment.coverage.rationale" not in row]
    assert parse_controls_assessment_inputs(_controls_with_inputs("\n".join(only_rating)))["inputs"] == {}


@pytest.mark.parametrize("header", ["| Finding | Field | Value |\n|---|---|---|", "| ID | Name | Value |\n|---|---|---|", "| ID | Field |\n|---|---|"])
def test_a_table_without_the_three_columns_is_one_error_and_no_input(header, capsys):
    text = _controls_with_inputs(header + "\n| T-1 | control_status | missing |\n")
    read = parse_controls_assessment_inputs(text)
    assert read["inputs"] == {} and len(read["errors"]) == 1
    assert read["errors"][0]["reason"] in ("the table has no ID, Field and Value columns", "has fewer cells than the table's header")
    capsys.readouterr()


def test_the_heading_may_stand_anywhere_and_only_the_first_table_after_it_is_read():
    elsewhere = "## 5. Notes\n\n### Assessment Inputs\n\n" + _persisted_table({"E-3": _FOUND_ITEM}) + "\n### Other\n\n| ID | Field | Value |\n|---|---|---|\n| T-1 | control_status | missing |\n"
    assert list(parse_controls_assessment_inputs(elsewhere)["inputs"]) == ["E-3"]
    assert list(parse_controls_assessment_inputs(elsewhere.replace("### Assessment Inputs", "### Assessment Inputs  "))["inputs"]) == ["E-3"]
    assert parse_controls_assessment_inputs(elsewhere.replace("### Assessment Inputs", "## Assessment Inputs")) == {"inputs": {}, "errors": []}


def test_keep_bold_keeps_the_markers_a_persisted_value_holds_and_the_default_strips_them_as_it_always_did():
    """The persisted tables hold `**What to Implement**: ...` as written, so a reader of them asks for the markers kept."""
    content = "## X\n\n| ID | **Field** | Value |\n|---|---|---|\n| S-1 | note | **bold** and &lt;b&gt; text |\n"
    assert parse_markdown_table(content, "## X") == [{"ID": "S-1", "Field": "note", "Value": "bold and <b> text"}]
    assert parse_markdown_table(content, "## X", keep_bold=True) == [{"ID": "S-1", "Field": "note", "Value": "**bold** and <b> text"}]
    assert parse_markdown_table(content, "## X", keep_bold=False) == parse_markdown_table(content, "## X")


def test_a_recommendation_body_keeps_its_bold_labels_through_the_persisted_table():
    body = parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table(_PERSISTED)))["inputs"]["S-2"]["recommendation_body"]
    assert body == _PARTIAL_ITEM["recommendation_body"] and body.startswith("**What to Implement**:") and "**Effort Estimate**: Low" in body


def test_an_empty_value_cell_is_a_value_the_writer_wrote_and_the_reader_returns_it_as_it_is():
    item = dict(_FOUND_ITEM, evidence=[dict(_FOUND_ITEM["evidence"][0], summary="")])
    assert parse_controls_assessment_inputs(_controls_with_inputs(_persisted_table({"E-3": item})))["inputs"]["E-3"] == item
