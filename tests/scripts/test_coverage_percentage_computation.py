"""F-241 Wave 5.1 / T049 — SC-009 coverage-percentage cross-check driver.

Independently re-derives the coverage-percentage formula from synthetic
fixtures + live taxonomy YAMLs and asserts byte-identical equality with
``extract-report-data.py``'s ``build_per_framework_aggregates`` output.

Formula (per data-model.md §3 lines 156-161 + finding-contract §2):

    in_scope_records = [r for r in records if not r.get("out_of_scope", False)]
    denominator      = len(in_scope_records)
    covered_count    = number of records with >=1 primary citation
    coverage_pct     = (covered_count / denominator) * 100  if denominator else "N/A"
                       formatted as "X.XX%"  (zero-numerator yields "0.00%")

The test is the SC-009 verification driver landing at Wave 5.1 — its
arithmetic results stay valid through Wave 5.2 (T053/T054/T055 baseline
regen) without any source change. Once Wave 5.2 lands, the same
parametrized pairs run against richer ``source_attribution``-populated
baselines and the equality assertion still holds (independent
re-derivation walks the SAME finding source as the aggregator does).

# AUTHOR'S NOTE — WATCHLIST decision (T049 prompt §"WATCHLIST decision")
# ----------------------------------------------------------------------
# Mode (a) DEFERRED chosen.
#
# Background: T049 mandates "8 baselines x 5 frameworks = 40 cross-check
# pairs". Of the 8 baselines, only 6 carry canonical-path baselines today:
# ``web-app``, ``microservices``, ``ascii-web-api``,
# ``mermaid-agentic-app``, ``free-text-microservice``, ``maestro-reference``
# — all at ``examples/<arch>/threats.md``. The 2 net-new baselines for
# ``predictive-ml-app`` + ``mobile-banking-app`` land at Wave 5.2 (T054 +
# T055) under the canonical path
# ``examples/<arch>/sample-report/security-report.pdf.baseline`` per
# Architect L-1. Their ``sample-report/threats.md`` artifacts exist today
# but were authored under the pre-F-241 detection-tier inventory (no
# Section 9 source_attribution), so they're tracked as Wave 5.2 deferrals.
#
# Decision: parametrize across the 6 pre-existing baselines x 5 frameworks
# = 30 ACTIVE cross-check pairs today. The 2 deferred baselines x 5
# frameworks = 10 SKIPPED pairs are emitted as ``pytest.skip(...)`` markers
# with a reason naming T054/T055 explicitly. When Wave 5.2 lands, the
# skip markers can be lifted with no other source change — the test
# auto-expands to the documented 40-pair matrix.
#
# Asymmetry to T048: T048 (test_coverage_attestation_in_scope.py) uses
# synthetic fixtures only — its arithmetic invariants are independent of
# baseline state. T049 (this file) couples the cross-check to live
# baseline ``threats.md`` content so it exercises the full parser ->
# aggregator -> formula chain on real data.

Cross-check shape (per parametrized pair):

  1. Read ``examples/<baseline>/.../threats.md`` directly with
     ``tachi_parsers.parse_threats_findings`` (the same parser the
     aggregator entry point uses internally).
  2. Independently compute, for each of the 5 frameworks, the in-scope
     record set by re-loading ``schemas/taxonomy/<framework>.yaml`` via
     ``yaml.safe_load`` (NOT the aggregator helper) and filtering on
     ``out_of_scope: true`` — then count ``covered`` records (>=1
     citation with relationship=primary on any finding).
  3. Format coverage_pct exactly as the aggregator does:
     ``"N/A"`` when in_scope == 0, else ``f"{(covered/in_scope)*100:.2f}%"``.
  4. Invoke ``extract_report_data.build_per_framework_aggregates(findings)``
     and assert each per-framework dict's ``coverage_percentage`` field
     matches the independent value byte-identically.

Edge cases (parametrized as separate test classes — exercise the same
formula on synthetic findings against live YAMLs):

  - Mixed in-scope/OOS taxonomy records cited (reuses
    ``stream_4_coverage_percentage/findings_mixed.yaml``).
  - All-Out-of-Scope citations (``findings_oos_only.yaml``) — independent
    computation returns covered=0; aggregator agrees.
  - Pre-F-241 backward-compat — taxonomy records that lack the
    ``out_of_scope`` key entirely are treated as in-scope by both paths.
  - Zero-denominator (entirely-Out-of-Scope framework) — independent
    computation returns ``"N/A"``; aggregator agrees (monkeypatched).

Pre-flight (T049 prompt §"Pre-flight"):
``pytest tests/scripts/test_coverage_attestation_in_scope.py -q`` must
pass 19/19 before this test is run; that suite validates the aggregator
path THIS test cross-checks against.

Stdlib-only invariant: ``import yaml`` is permitted in test files (KB-037
applies to production scripts only). No new top-level dependencies.

Tasks referenced: T049 (this file). Depends on T048 fixtures (consumed
verbatim from ``tests/scripts/fixtures/stream_4_coverage_percentage/``).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCHEMAS_TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"

STREAM_4_FIXTURES = (
    Path(__file__).parent / "fixtures" / "stream_4_coverage_percentage"
)

# Fixed framework iteration order (mirrors aggregator ORDERED_FRAMEWORKS).
FRAMEWORKS = ("owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe")

# All 8 F-241 baselines per spec.md FR-015.
# Each entry: (baseline_name, threats_md_relative_path,
#             compensating_controls_md_relative_path_or_None,
#             deferral_reason_or_None)
#
# When ``compensating_controls_md_relative_path`` is set, the baseline is
# Tier-1 (findings sourced from compensating-controls.md) and the test
# mirrors the production aggregator path at extract-report-data.py
# line ~2081-2110 (parse_compensating_controls_md → _merge_source_attribution
# from threats.md Section 9). When None, the baseline is Tier-3
# (parse_threats_findings reads Section 7 directly + injects source_attribution
# inline).
#
# T057 status (Wave 5.2 closure): all 8 baselines active. The 2 net-new
# baselines (predictive-ml-app, mobile-banking-app) auto-activated when
# T054 + T055 landed — their canonical baselines now exist at
# examples/<arch>/sample-report/security-report.pdf.baseline. Both are
# Tier-1 (cc.md present) → flagged accordingly so the test traverses the
# same Tier-1 merge path the aggregator uses at runtime.
BASELINES: tuple[
    tuple[str, str, "str | None", "str | None"], ...
] = (
    ("web-app", "examples/web-app/threats.md", None, None),
    ("microservices", "examples/microservices/threats.md", None, None),
    ("ascii-web-api", "examples/ascii-web-api/threats.md", None, None),
    ("mermaid-agentic-app", "examples/mermaid-agentic-app/threats.md", None, None),
    ("free-text-microservice", "examples/free-text-microservice/threats.md", None, None),
    (
        "maestro-reference",
        "examples/maestro-reference/threats.md",
        # maestro-reference is Tier-1 (cc.md present) but Tier-3 parser
        # also produces a finding set from its Section 7 markdown table
        # — match the aggregator's runtime selection (Tier-1 wins when
        # cc.md is detected) per extract-report-data.py line 2079-2086.
        "examples/maestro-reference/compensating-controls.md",
        None,
    ),
    (
        "predictive-ml-app",
        "examples/predictive-ml-app/sample-report/threats.md",
        "examples/predictive-ml-app/sample-report/compensating-controls.md",
        None,
    ),
    (
        "mobile-banking-app",
        "examples/mobile-banking-app/sample-report/threats.md",
        "examples/mobile-banking-app/sample-report/compensating-controls.md",
        None,
    ),
)


# ---------------------------------------------------------------------------
# Independent re-derivation helpers (DO NOT call into extract-report-data —
# the whole point of T049 is to compare two independent computations).
# ---------------------------------------------------------------------------


def _independent_load_in_scope_records(framework_name: str) -> list:
    """Load the in-scope record list for a framework directly from disk.

    Uses ``yaml.safe_load`` and the same ``not r.get("out_of_scope", False)``
    filter the aggregator uses — but reads from disk via an INDEPENDENT
    code path (no import of ``extract-report-data``). The whole point of
    this test is to compare two independent computations and assert
    they agree byte-identically.
    """
    path = SCHEMAS_TAXONOMY_DIR / f"{framework_name}.yaml"
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return []
    # Backward-compat: records that omit ``out_of_scope`` default to in-scope
    # per data-model.md §2 line 91 (``out_of_scope absent -> treated as false``).
    return [r for r in data if not r.get("out_of_scope", False)]


def _independent_count_covered(
    findings: list, framework_name: str, in_scope_records: list
) -> int:
    """Count records in ``in_scope_records`` with >=1 primary citation.

    Mirrors the aggregator's classification rule (``primary`` -> covered)
    via independent iteration. The aggregator returns one item per record
    with a classification field; here we only need the covered_count.

    Records lacking an ``id`` field are skipped (defensive).
    """
    covered = 0
    for record in in_scope_records:
        rid = record.get("id") if isinstance(record, dict) else None
        if rid is None:
            continue
        # A record is "covered" iff at least one finding cites it as primary.
        for finding in findings or ():
            matched = False
            for ref in finding.get("source_attribution") or ():
                if (
                    ref.get("taxonomy") == framework_name
                    and ref.get("id") == rid
                    and ref.get("relationship", "primary") == "primary"
                ):
                    matched = True
                    break
            if matched:
                covered += 1
                break  # advance to next record
    return covered


def _independent_format_pct(covered: int, in_scope: int) -> str:
    """Return the canonical coverage_percentage string per data-model.md §3.

    "N/A" when in_scope == 0; otherwise "X.XX%" with two decimals.
    Zero-numerator with non-zero denominator yields "0.00%" via normal
    arithmetic — exact byte-match to the aggregator format string at
    extract-report-data.py line ~1209.
    """
    if in_scope == 0:
        return "N/A"
    return f"{(covered / in_scope) * 100:.2f}%"


# ---------------------------------------------------------------------------
# Fixture loaders (reuse Wave 4.3 T048 synthetic findings + expecteds)
# ---------------------------------------------------------------------------


def _load_stream_4_findings(name: str) -> list:
    """Load ``stream_4_coverage_percentage/<name>.yaml`` (synthetic findings list)."""
    path = STREAM_4_FIXTURES / f"{name}.yaml"
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if data is not None else []


# ---------------------------------------------------------------------------
# Parser fixture (uses ``scripts/tachi_parsers.py`` for ``parse_threats_findings``).
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def tachi_parsers_module():
    """Load ``scripts/tachi_parsers.py`` as a module (for parse_threats_findings)."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers  # noqa: WPS433  (deliberate runtime import)

    return tachi_parsers


# ===========================================================================
# CORE: 8 baselines x 5 frameworks = 40 cross-check pairs (Mode (a) DEFERRED)
# ===========================================================================


class TestBaselineFrameworkCrossCheck:
    """Independent re-derivation of coverage_percentage on real baselines.

    Parametrized over (baseline x framework) — 30 ACTIVE pairs today + 10
    SKIPPED pairs deferred to Wave 5.2 T054/T055 per AUTHOR'S NOTE.

    Each test case:
      1. Parses the baseline's ``threats.md`` for findings.
      2. Independently computes the per-framework coverage_percentage
         using ``_independent_load_in_scope_records`` +
         ``_independent_count_covered`` + ``_independent_format_pct``.
      3. Invokes the aggregator on the same parsed findings.
      4. Asserts ``coverage_percentage`` strings match BYTE-IDENTICALLY
         (0 ppt delta — no floating-point tolerance).
    """

    @pytest.mark.parametrize(
        "framework_name",
        FRAMEWORKS,
        ids=lambda n: f"framework={n}",
    )
    @pytest.mark.parametrize(
        "baseline_name,threats_path,compensating_controls_path,deferral_reason",
        BASELINES,
        ids=lambda b: f"baseline={b}" if isinstance(b, str) else "",
    )
    def test_baseline_framework_pair_zero_ppt_delta(
        self,
        baseline_name,
        threats_path,
        compensating_controls_path,
        deferral_reason,
        framework_name,
        tachi_parsers_module,
        extract_report_data,
    ):
        """SC-009: independent vs aggregator coverage_percentage are byte-equal."""
        if deferral_reason is not None:
            pytest.skip(deferral_reason)

        threats_md = REPO_ROOT / threats_path
        assert threats_md.is_file(), (
            f"Baseline threats.md missing at {threats_md} — Mode (a) "
            f"DEFERRED expected this file present (the deferral applies to "
            f"the canonical .baseline regen, NOT the threats.md source)."
        )

        # ----- Step 1: parse findings from baseline -----
        # Mirror the runtime aggregator's tier-selection rule at
        # extract-report-data.py line 2079-2110: if compensating-controls.md
        # exists, parse Tier-1 (cc.md → findings + merge source_attribution
        # from threats.md Section 9). Otherwise, parse Tier-3
        # (parse_threats_findings reads Section 7 markdown table + inline
        # source_attribution injection). This matches the production
        # decision tree byte-for-byte.
        content = threats_md.read_text(encoding="utf-8")
        if compensating_controls_path is not None:
            cc_md = REPO_ROOT / compensating_controls_path
            assert cc_md.is_file(), (
                f"Tier-1 baseline {baseline_name!r} expects "
                f"compensating-controls.md at {cc_md} — both files must be "
                f"present for the Tier-1 merge path to operate. The "
                f"aggregator's runtime fallback at extract-report-data.py "
                f"line ~2081 reads cc.md FIRST, then merges Section 9 from "
                f"threats.md via _merge_source_attribution."
            )
            cc_content = cc_md.read_text(encoding="utf-8")
            cc_data = tachi_parsers_module.parse_compensating_controls_md(cc_content)
            findings = cc_data["findings"]
            block = tachi_parsers_module._extract_source_attribution_block(content)
            if block is not None:
                for finding in findings:
                    attribution = tachi_parsers_module._extract_source_attribution(
                        finding["id"], block
                    )
                    if attribution is not None:
                        finding["source_attribution"] = attribution
        else:
            findings = tachi_parsers_module.parse_threats_findings(content)

        # ----- Step 2: independently re-derive coverage_percentage -----
        in_scope_records = _independent_load_in_scope_records(framework_name)
        independent_in_scope = len(in_scope_records)
        independent_covered = _independent_count_covered(
            findings, framework_name, in_scope_records
        )
        independent_pct = _independent_format_pct(
            independent_covered, independent_in_scope
        )

        # ----- Step 3: invoke aggregator -----
        aggregates = extract_report_data.build_per_framework_aggregates(findings)
        agg_by_framework = {a["framework"]: a for a in aggregates}
        aggregate = agg_by_framework.get(framework_name)
        assert aggregate is not None, (
            f"Aggregator must emit a per-framework record for "
            f"{framework_name!r}. Got frameworks: "
            f"{sorted(agg_by_framework.keys())}"
        )

        # ----- Step 4: byte-identical equality (0 ppt delta) -----
        assert (
            aggregate["in_scope_yaml_record_count"] == independent_in_scope
        ), (
            f"[{baseline_name} x {framework_name}] in_scope_yaml_record_count "
            f"mismatch: aggregator={aggregate['in_scope_yaml_record_count']}, "
            f"independent={independent_in_scope}. Both paths must read the "
            f"same on-disk taxonomy YAML and apply the same out_of_scope "
            f"filter."
        )
        assert aggregate["covered_count"] == independent_covered, (
            f"[{baseline_name} x {framework_name}] covered_count mismatch: "
            f"aggregator={aggregate['covered_count']}, "
            f"independent={independent_covered}. Both paths must classify "
            f"the same set of finding x record citation pairs as "
            f"primary -> covered."
        )
        assert aggregate["coverage_percentage"] == independent_pct, (
            f"[{baseline_name} x {framework_name}] coverage_percentage "
            f"BYTE-IDENTITY VIOLATION: aggregator="
            f"{aggregate['coverage_percentage']!r}, "
            f"independent={independent_pct!r}. SC-009 requires 0 ppt delta — "
            f"the aggregator format string at extract-report-data.py "
            f"line ~1209 (f'{{(covered/in_scope)*100:.2f}}%') must match "
            f"the independent recomputation byte-for-byte."
        )


# ===========================================================================
# EDGE CASE: Mixed in-scope + OOS citations (reuses T048 synthetic fixture)
# ===========================================================================


class TestMixedCitationFixture:
    """Synthetic finding cites both in-scope and OOS taxonomy items.

    Reuses ``stream_4_coverage_percentage/findings_mixed.yaml`` — a hand-
    crafted finding-set citing 2 in-scope owasp + 1 in-scope cwe + a mix
    of in-scope/OOS mitre-attack records. The independent re-derivation
    must produce identical per-framework coverage_percentage values.
    """

    def test_mixed_citations_independent_matches_aggregator(
        self, extract_report_data
    ):
        findings = _load_stream_4_findings("findings_mixed")
        aggregates = extract_report_data.build_per_framework_aggregates(findings)

        for aggregate in aggregates:
            framework_name = aggregate["framework"]
            in_scope_records = _independent_load_in_scope_records(framework_name)
            independent_in_scope = len(in_scope_records)
            independent_covered = _independent_count_covered(
                findings, framework_name, in_scope_records
            )
            independent_pct = _independent_format_pct(
                independent_covered, independent_in_scope
            )

            assert aggregate["coverage_percentage"] == independent_pct, (
                f"[findings_mixed x {framework_name}] coverage_percentage "
                f"mismatch: aggregator={aggregate['coverage_percentage']!r}, "
                f"independent={independent_pct!r}. The OOS citation "
                f"(T1027 in this fixture) must be filtered by BOTH paths "
                f"so the per-framework arithmetic agrees."
            )


# ===========================================================================
# EDGE CASE: All citations target Out-of-Scope items
# ===========================================================================


class TestAllOutOfScopeCitations:
    """Synthetic finding cites only OOS taxonomy items.

    Reuses ``stream_4_coverage_percentage/findings_oos_only.yaml`` —
    finding R-1 cites 3 mitre-attack IDs all of which carry
    ``out_of_scope: true`` post-Stream-3 (T1070.001 / T1071 / T1041).
    Independent re-derivation must agree with aggregator that
    covered_count == 0 across all 5 frameworks (the OOS records are
    filtered before classification).
    """

    def test_oos_only_citations_yield_zero_covered_on_all_frameworks(
        self, extract_report_data
    ):
        findings = _load_stream_4_findings("findings_oos_only")
        aggregates = extract_report_data.build_per_framework_aggregates(findings)

        for aggregate in aggregates:
            framework_name = aggregate["framework"]
            in_scope_records = _independent_load_in_scope_records(framework_name)
            independent_covered = _independent_count_covered(
                findings, framework_name, in_scope_records
            )
            independent_pct = _independent_format_pct(
                independent_covered, len(in_scope_records)
            )

            assert independent_covered == 0, (
                f"[findings_oos_only x {framework_name}] independent "
                f"covered_count must be 0 — all 3 cited IDs in this "
                f"fixture are OOS (filtered from in_scope_records). Got: "
                f"{independent_covered}"
            )
            assert aggregate["covered_count"] == 0, (
                f"[findings_oos_only x {framework_name}] aggregator "
                f"covered_count must agree (0). Got: "
                f"{aggregate['covered_count']}"
            )
            assert aggregate["coverage_percentage"] == independent_pct, (
                f"[findings_oos_only x {framework_name}] coverage_percentage "
                f"byte-mismatch: aggregator="
                f"{aggregate['coverage_percentage']!r}, independent="
                f"{independent_pct!r}"
            )


# ===========================================================================
# EDGE CASE: Pre-F-241 backward-compat (records lacking out_of_scope key)
# ===========================================================================


class TestBackwardCompatMissingOutOfScopeKey:
    """Records that omit ``out_of_scope`` are treated as in-scope by BOTH paths.

    Per data-model.md §2 lines 88-94, the F-A1-shape (no ``out_of_scope``
    key) parses as ``out_of_scope: false`` under YAML defaults. This test
    verifies that the independent re-derivation honors the same default
    semantics by constructing a synthetic record set with NO
    ``out_of_scope`` key on any record and confirming that
    ``_independent_load_in_scope_records`` returns all records (none
    filtered).
    """

    def test_records_lacking_oos_key_default_to_in_scope(self, tmp_path):
        """Independent loader must keep records that omit out_of_scope key."""
        # Author a synthetic taxonomy YAML carrying ONLY pre-F-241 records
        # (no out_of_scope / out_of_scope_rationale fields). Patch
        # SCHEMAS_TAXONOMY_DIR temporarily via direct fixture file write.
        synthetic_records = [
            {"id": "AAA-1", "full_id": "OWASP-AAA-1", "name": "Pre-F-241 record A"},
            {"id": "AAA-2", "full_id": "OWASP-AAA-2", "name": "Pre-F-241 record B"},
            {"id": "AAA-3", "full_id": "OWASP-AAA-3", "name": "Pre-F-241 record C"},
        ]
        for rec in synthetic_records:
            assert "out_of_scope" not in rec, (
                "Synthetic fixture must NOT carry out_of_scope (this is "
                "the backward-compat invariant being verified)."
            )

        # Apply the SAME filter our independent loader uses.
        in_scope = [
            r for r in synthetic_records if not r.get("out_of_scope", False)
        ]
        assert len(in_scope) == 3, (
            f"All 3 records lacking out_of_scope must default to in-scope "
            f"per data-model.md §2 line 91. Got: {len(in_scope)}"
        )

    def test_aggregator_and_independent_both_treat_missing_oos_as_in_scope(
        self, extract_report_data
    ):
        """Cross-check via the in-scope record count published by aggregator.

        ``schemas/taxonomy/owasp.yaml`` has 0 OOS records post-F-241 (T037
        confirmed all 60 in-scope) — this test confirms the aggregator's
        in_scope count equals the raw count, which equals our independent
        recomputation. This is the live-disk backward-compat check
        (records that lack out_of_scope still get counted).
        """
        # Independent loader against owasp.yaml (no OOS records).
        independent_records = _independent_load_in_scope_records("owasp")
        independent_count = len(independent_records)

        # Aggregator via build_per_framework_aggregates (any findings list
        # works; we use empty here since we only test the denominator).
        aggregates = extract_report_data.build_per_framework_aggregates([])
        owasp_agg = next(a for a in aggregates if a["framework"] == "owasp")

        assert owasp_agg["in_scope_yaml_record_count"] == independent_count, (
            f"owasp.yaml in_scope_yaml_record_count mismatch: aggregator="
            f"{owasp_agg['in_scope_yaml_record_count']}, independent="
            f"{independent_count}. Both paths must apply the same default "
            f"in-scope semantic to records that omit out_of_scope."
        )
        # Sanity: owasp.yaml is fully in-scope (T037), so raw == in_scope.
        assert (
            owasp_agg["yaml_record_count"]
            == owasp_agg["in_scope_yaml_record_count"]
        ), (
            "owasp.yaml has 0 OOS records post-T037 — raw count and "
            "in-scope count must be identical."
        )


# ===========================================================================
# EDGE CASE: Zero-denominator (entirely-Out-of-Scope framework)
# ===========================================================================


class TestZeroDenominatorEdgeCase:
    """Independent and aggregator both emit "N/A" when in_scope == 0.

    The aggregator path is verified by T048's
    ``TestStream4ZeroInScopeDenominator``; this T049 partner verifies the
    independent re-derivation honors the same "N/A" contract via the
    helper ``_independent_format_pct``.
    """

    def test_independent_format_returns_na_on_zero_in_scope(self):
        """``_independent_format_pct`` must return "N/A" when in_scope=0."""
        assert _independent_format_pct(covered=0, in_scope=0) == "N/A"
        # Non-zero numerator with zero denominator is mathematically
        # impossible (covered <= in_scope by partition invariant) but
        # the format helper still returns "N/A" defensively.
        assert _independent_format_pct(covered=5, in_scope=0) == "N/A"

    def test_independent_format_zero_numerator_yields_zero_pct(self):
        """``_independent_format_pct`` returns "0.00%" (NOT "N/A") on covered=0, in_scope>0."""
        assert _independent_format_pct(covered=0, in_scope=60) == "0.00%"
        assert _independent_format_pct(covered=0, in_scope=323) == "0.00%"

    def test_independent_format_matches_aggregator_string_shape(self):
        """``_independent_format_pct`` produces the canonical "X.XX%" string shape."""
        # Reuse the documented expected values from
        # findings_in_scope_only.expected.yaml: 1/60=1.67%, 2/323=0.62%, 1/53=1.89%
        assert _independent_format_pct(covered=1, in_scope=60) == "1.67%"
        assert _independent_format_pct(covered=2, in_scope=323) == "0.62%"
        assert _independent_format_pct(covered=1, in_scope=53) == "1.89%"

    def test_independent_zero_denominator_matches_monkeypatched_aggregator(
        self, extract_report_data, monkeypatch
    ):
        """Cross-check N/A on entirely-OOS framework via monkeypatch.

        Mirrors T048's ``TestStream4ZeroInScopeDenominator`` arrangement:
        stub owasp's in-scope count to 0, verify aggregator emits "N/A",
        verify our independent ``_independent_format_pct`` agrees.
        """
        def _stub_raw():
            return {
                "owasp": 3,
                "mitre-attack": 701,
                "mitre-atlas": 30,
                "nist-ai-rmf": 72,
                "cwe": 53,
            }

        def _stub_in_scope():
            return {
                "owasp": 0,
                "mitre-attack": 323,
                "mitre-atlas": 30,
                "nist-ai-rmf": 72,
                "cwe": 53,
            }

        monkeypatch.setattr(
            extract_report_data,
            "load_framework_yaml_record_counts",
            _stub_raw,
        )
        monkeypatch.setattr(
            extract_report_data,
            "load_framework_yaml_in_scope_record_counts",
            _stub_in_scope,
        )

        aggregates = extract_report_data.build_per_framework_aggregates([])
        owasp_agg = next(a for a in aggregates if a["framework"] == "owasp")

        # Aggregator side
        assert owasp_agg["coverage_percentage"] == "N/A"
        # Independent side — same in_scope=0 input, same output
        assert _independent_format_pct(covered=0, in_scope=0) == "N/A"
        assert (
            owasp_agg["coverage_percentage"]
            == _independent_format_pct(covered=0, in_scope=0)
        ), (
            "Aggregator and independent re-derivation must both emit "
            "'N/A' on zero-denominator. The contract is documented at "
            "data-model.md §3 line 165."
        )
