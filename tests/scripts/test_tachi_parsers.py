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
directory's README.md for hand-computed expected values and today's
(pre-fix) buggy reads.

Stdlib-only per PAT-014 — no PyYAML, no Path operations beyond importlib.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

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
    classify_control_status,
    normalize_delta_status,
    delta_status_by_id,
    compute_delta_counts,
    apply_delta_status,
    warn_delta_scope,
    parse_resolved_findings,
)

FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373"


def _composites_from_fixture(subdir: str) -> dict:
    """Build a K11 ``composites_by_id`` map from a fixture's risk-scores.md."""
    rs_content = _read_fixture(subdir, "risk-scores.md")
    return {
        f["id"]: parse_score(f["composite_score"])
        for f in parse_risk_scores_findings(rs_content)
        if f.get("id")
    }


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


def test_warn_delta_scope_never_raises_and_is_silent_when_not_baseline():
    # Never raises, even on ragged input; silent unless has_baseline.
    warn_delta_scope(False, False, {}, 0, None)
    warn_delta_scope(False, True, {"A": "NEW"}, 1, None)


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
# one. For a match on a level-1-or-2 heading (the representative "##"
# caller and scripts/generate-risk-scores-sarif.py's two callers, named
# explicitly by FR-K9.2), "stop at the next heading of the same or higher
# level" reduces mathematically to "stop at the next '##'/'#' line" — the
# old hardcoded rule — so these are unaffected by construction, proven here
# even across an intervening deeper heading.
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
    # US-3b #1 fixture, at the row level (T021 computes the funnel itself in
    # W2; this only proves T020's parsed rows are what T021 needs).
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
    # T024 will consume these counts through compute_risk_posture; this pins
    # K11's own row-level output on the fixture T025's stale-data gate (W2)
    # will also use.
    content = _read_fixture("posture_mmdc_free", "compensating-controls.md")
    data = parse_compensating_controls_md(content)
    assert data["severity"] == {
        "critical": 0, "high": 1, "medium": 1, "low": 1, "note": 0, "total": 3,
    }
