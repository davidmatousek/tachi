"""F-241 Stream 3 + Stream 4 in-scope-only coverage-percentage tests (T048).

Validates the post-T044/T045/T047 aggregator behavior:

1. ``_load_framework_yaml_records(in_scope_only=True)`` filters records
   carrying ``out_of_scope: true`` (T044) — records that omit the field
   are treated as in-scope per data-model.md §2 backward-compat.
2. ``load_framework_yaml_in_scope_record_counts()`` returns the filtered
   counts (T045 sibling helper of ``load_framework_yaml_record_counts``).
3. ``_build_per_framework_aggregate()`` emits BOTH ``yaml_record_count``
   (raw) AND ``in_scope_yaml_record_count`` (filtered) on the per-framework
   aggregate dict (T045/T047).
4. Coverage percentage uses ``in_scope_yaml_record_count`` as denominator
   per data-model.md §3 lines 156-161 + finding-contract.md §2.
5. The Typst data emission at line ~1899 of ``extract-report-data.py`` carries
   ``in-scope-record-count: <int>`` alongside the existing ``yaml-record-count``
   field (FR-024 / data-model.md §3).
6. Findings citing Out-of-Scope items (T046 edge case): the aggregator
   filters OOS records out of the items list, so they DO NOT appear as
   covered/partial/gap. The finding itself still emits on the per-finding
   attribution table (preserves F-A2 referential-integrity contract; that
   surface is exercised separately by ``test_per_finding_row_*`` tests).

Fixtures consumed:
- ``tests/scripts/fixtures/stream_3_taxonomy/`` — synthetic taxonomy YAML subsets
- ``tests/scripts/fixtures/stream_4_coverage_percentage/`` — finding fixture +
  expected aggregate-shape pairs (live taxonomy YAMLs)

Tasks referenced: T044 / T045 / T046 / T047 / T048.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
STREAM_3_FIXTURES = (
    Path(__file__).parent / "fixtures" / "stream_3_taxonomy"
)
STREAM_4_FIXTURES = (
    Path(__file__).parent / "fixtures" / "stream_4_coverage_percentage"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path):
    """Return the parsed YAML document at ``path`` (or empty list on None)."""
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if data is not None else []


def _stream_3_records(name: str) -> list:
    """Return the list of records in the named Stream 3 fixture."""
    return _load_yaml(STREAM_3_FIXTURES / f"{name}.yaml")


def _stream_4_findings(name: str) -> list:
    """Return the list of findings in the named Stream 4 fixture."""
    return _load_yaml(STREAM_4_FIXTURES / f"{name}.yaml")


def _stream_4_expected(name: str) -> dict:
    """Return the expected aggregate-shape dict for the named Stream 4 fixture."""
    return _load_yaml(STREAM_4_FIXTURES / f"{name}.expected.yaml")


# ===========================================================================
# Stream 3: Synthetic taxonomy YAML filter behavior (T044)
# ===========================================================================


class TestStream3FixtureShape:
    """Verify the Stream 3 fixtures themselves carry the documented shape.

    These tests exercise the FIXTURE FILES directly (not the aggregator) — they
    pin the fixture inventory invariant so silent fixture drift in subsequent
    waves surfaces as a test failure rather than a downstream aggregator
    miscompute.
    """

    def test_mixed_in_scope_and_oos_record_count(self):
        records = _stream_3_records("mixed_in_scope_and_oos")
        assert len(records) == 5, (
            f"mixed_in_scope_and_oos.yaml must carry 5 records "
            f"(3 in-scope + 2 OOS). Got: {len(records)}"
        )
        in_scope = [r for r in records if not r.get("out_of_scope", False)]
        oos = [r for r in records if r.get("out_of_scope", False)]
        assert len(in_scope) == 3, (
            f"mixed fixture must have 3 in-scope records. Got: {len(in_scope)}"
        )
        assert len(oos) == 2, (
            f"mixed fixture must have 2 OOS records. Got: {len(oos)}"
        )

    def test_omits_oos_field_records_treated_as_in_scope(self):
        """Pre-F-241 backward-compat — records that omit the field default to in-scope."""
        records = _stream_3_records("omits_oos_field")
        assert len(records) == 4, (
            f"omits_oos_field.yaml must carry 4 records. Got: {len(records)}"
        )
        # Every record must omit BOTH new fields (pure pre-F-241 shape).
        for record in records:
            assert "out_of_scope" not in record, (
                f"Record {record.get('id')!r} must NOT carry out_of_scope "
                f"(pre-F-241 backward-compat fixture)."
            )
            assert "out_of_scope_rationale" not in record, (
                f"Record {record.get('id')!r} must NOT carry "
                f"out_of_scope_rationale (pre-F-241 backward-compat fixture)."
            )

    def test_with_rationale_records_carry_non_empty_rationale(self):
        records = _stream_3_records("with_rationale")
        assert len(records) == 4, (
            f"with_rationale.yaml must carry 4 records. Got: {len(records)}"
        )
        for record in records:
            assert record.get("out_of_scope") is True, (
                f"Record {record.get('id')!r} in with_rationale.yaml must "
                f"carry out_of_scope: true."
            )
            rationale = record.get("out_of_scope_rationale", "")
            assert rationale, (
                f"Record {record.get('id')!r} in with_rationale.yaml must "
                f"carry a non-empty out_of_scope_rationale."
            )
            assert "outside tachi's design-time threat-modeling scope" in rationale, (
                f"Record {record.get('id')!r} rationale must echo the "
                f"verbatim/derived T040 narrative pattern. Got: {rationale!r}"
            )

    def test_empty_yaml_returns_empty_list(self):
        """The empty-YAML fixture must parse to an empty list (zero-denominator case)."""
        records = _stream_3_records("empty_yaml")
        assert records == [], (
            f"empty_yaml.yaml must parse as an empty list. Got: {records!r}"
        )

    def test_all_oos_fixture_is_entirely_out_of_scope(self):
        records = _stream_3_records("all_oos")
        assert len(records) == 3, (
            f"all_oos.yaml must carry 3 records. Got: {len(records)}"
        )
        for record in records:
            assert record.get("out_of_scope") is True, (
                f"Record {record.get('id')!r} in all_oos.yaml must "
                f"carry out_of_scope: true."
            )


# ===========================================================================
# Stream 3: Loader filter behavior (T044) — exercised against monkeypatched
# data via the public _load_framework_yaml_records(in_scope_only=...) helper.
# ===========================================================================


class TestStream3LoaderFilter:
    """Exercise ``_load_framework_yaml_records`` filter semantics.

    The loader signature gained an ``in_scope_only`` kwarg in T044. When True,
    records carrying ``out_of_scope: true`` are filtered. Records that omit
    the field are treated as in-scope (pre-F-241 backward-compat per
    data-model.md §2).

    These tests monkeypatch the on-disk path resolution via injection of a
    synthetic fixture into ``SCHEMAS_TAXONOMY_DIR`` lookup — the cleanest way
    to exercise the filter against synthetic content without touching the
    live ``schemas/taxonomy/*.yaml`` files (architect M-3 / FR-014).
    """

    def _stub_load(self, fixture_name: str, in_scope_only: bool, monkeypatch):
        """Run ``_load_framework_yaml_records`` against a Stream 3 fixture.

        Patches the module-level ``SCHEMAS_TAXONOMY_DIR`` to point at the
        Stream 3 fixtures directory so the loader resolves
        ``<framework>.yaml`` to our synthetic content. The framework name
        used in the call is the fixture filename minus the ``.yaml``
        extension.
        """
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "extract_report_data", REPO_ROOT / "scripts" / "extract-report-data.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        monkeypatch.setattr(
            module, "SCHEMAS_TAXONOMY_DIR", STREAM_3_FIXTURES
        )
        return module._load_framework_yaml_records(
            fixture_name, in_scope_only=in_scope_only
        )

    def test_raw_call_returns_all_records_including_oos(self, monkeypatch):
        records = self._stub_load(
            "mixed_in_scope_and_oos", in_scope_only=False, monkeypatch=monkeypatch
        )
        ids = [r["id"] for r in records]
        # All 5 IDs (in-scope + OOS) must appear in raw return.
        assert ids == ["T1190", "T1071", "T1078", "T1041", "T1195"], (
            f"raw _load_framework_yaml_records must return ALL records "
            f"(both in-scope and OOS). Got: {ids!r}"
        )

    def test_in_scope_only_filters_oos_records(self, monkeypatch):
        records = self._stub_load(
            "mixed_in_scope_and_oos", in_scope_only=True, monkeypatch=monkeypatch
        )
        ids = [r["id"] for r in records]
        # Exactly the 3 in-scope IDs (T1190, T1078, T1195) must remain.
        assert ids == ["T1190", "T1078", "T1195"], (
            f"in_scope_only=True must filter the 2 OOS records "
            f"(T1071, T1041). Got: {ids!r}"
        )

    def test_in_scope_only_treats_missing_field_as_in_scope(self, monkeypatch):
        """Pre-F-241 backward-compat: records without out_of_scope key are kept."""
        records = self._stub_load(
            "omits_oos_field", in_scope_only=True, monkeypatch=monkeypatch
        )
        # All 4 records lack the out_of_scope field; all 4 must be returned.
        assert len(records) == 4, (
            f"in_scope_only=True must keep all 4 records that omit "
            f"out_of_scope (treated as default-in-scope per data-model.md "
            f"§2). Got: {len(records)}"
        )

    def test_in_scope_only_on_empty_yaml_returns_empty(self, monkeypatch):
        records = self._stub_load(
            "empty_yaml", in_scope_only=True, monkeypatch=monkeypatch
        )
        assert records == [], (
            f"in_scope_only=True on empty YAML must return []. "
            f"Got: {records!r}"
        )

    def test_in_scope_only_on_all_oos_returns_empty(self, monkeypatch):
        records = self._stub_load(
            "all_oos", in_scope_only=True, monkeypatch=monkeypatch
        )
        assert records == [], (
            f"in_scope_only=True on all-OOS YAML must filter every record "
            f"and return []. Got: {records!r}"
        )

    def test_raw_call_on_all_oos_returns_full_inventory(self, monkeypatch):
        """All-OOS edge case: raw call returns 3 records (in_scope returns 0)."""
        records = self._stub_load(
            "all_oos", in_scope_only=False, monkeypatch=monkeypatch
        )
        assert len(records) == 3, (
            f"raw _load_framework_yaml_records on all-OOS must return all "
            f"3 records (filter only applies when in_scope_only=True). "
            f"Got: {len(records)}"
        )


# ===========================================================================
# Stream 4: in_scope_yaml_record_count emission on aggregate dict (T045/T047)
# ===========================================================================


class TestStream4AggregateShape:
    """Verify the aggregator dict carries BOTH yaml_record_count and
    in_scope_yaml_record_count keys (data-model.md §3 / FR-024 / Architect M-2).
    """

    def test_aggregate_emits_in_scope_yaml_record_count(self, extract_report_data):
        """Every per-framework aggregate dict must carry the new field."""
        findings = _stream_4_findings("findings_in_scope_only")
        aggregates = extract_report_data.build_per_framework_aggregates(findings)

        for agg in aggregates:
            assert "in_scope_yaml_record_count" in agg, (
                f"Per-framework aggregate for {agg.get('framework')!r} must "
                f"carry the in_scope_yaml_record_count field per F-241 "
                f"Stream 4 / T045 / data-model.md §3. Keys present: "
                f"{sorted(agg.keys())}"
            )
            assert "yaml_record_count" in agg, (
                f"Per-framework aggregate for {agg.get('framework')!r} must "
                f"preserve the raw yaml_record_count field for "
                f"external-auditor traceability. Keys present: "
                f"{sorted(agg.keys())}"
            )

    def test_in_scope_count_equals_raw_minus_oos_for_mitre_attack(
        self, extract_report_data
    ):
        """mitre-attack post-T041: 701 raw records, 378 OOS, 323 in-scope."""
        findings = _stream_4_findings("findings_in_scope_only")
        aggregates = extract_report_data.build_per_framework_aggregates(findings)
        attack = next(a for a in aggregates if a["framework"] == "mitre-attack")

        assert attack["yaml_record_count"] == 701, (
            f"mitre-attack raw record count must be 701 post-T041. "
            f"Got: {attack['yaml_record_count']}"
        )
        assert attack["in_scope_yaml_record_count"] == 323, (
            f"mitre-attack in-scope record count must be 323 (701 - 378 OOS). "
            f"Got: {attack['in_scope_yaml_record_count']}"
        )
        # The two counts MUST differ for mitre-attack post-Stream 3.
        assert attack["yaml_record_count"] != attack["in_scope_yaml_record_count"], (
            "mitre-attack raw and in-scope counts must differ post-T041 "
            "tactical-grouping (Stream 3 expansion authored 378 OOS records)."
        )

    def test_owasp_in_scope_equals_raw_no_oos_records(self, extract_report_data):
        """owasp.yaml has 0 OOS records — raw and in-scope counts must match."""
        findings = _stream_4_findings("findings_in_scope_only")
        aggregates = extract_report_data.build_per_framework_aggregates(findings)
        owasp = next(a for a in aggregates if a["framework"] == "owasp")

        assert owasp["yaml_record_count"] == 60
        assert owasp["in_scope_yaml_record_count"] == 60
        assert owasp["yaml_record_count"] == owasp["in_scope_yaml_record_count"], (
            "owasp.yaml has 0 OOS records (T037 — all 60 in-scope); raw and "
            "in-scope counts must be identical."
        )


# ===========================================================================
# Stream 4: Coverage-percentage arithmetic against expected fixtures
# ===========================================================================


class TestStream4CoveragePercentage:
    """Hand-computed expected fixtures + aggregator output equality."""

    def _assert_aggregate_matches_expected(
        self, aggregate: dict, expected: dict, framework_name: str
    ):
        """Assert each numeric/string key on the aggregate matches expected."""
        assert aggregate["yaml_record_count"] == expected["yaml_record_count"], (
            f"{framework_name}.yaml_record_count: expected "
            f"{expected['yaml_record_count']}, got "
            f"{aggregate['yaml_record_count']}"
        )
        assert (
            aggregate["in_scope_yaml_record_count"]
            == expected["in_scope_yaml_record_count"]
        ), (
            f"{framework_name}.in_scope_yaml_record_count: expected "
            f"{expected['in_scope_yaml_record_count']}, got "
            f"{aggregate['in_scope_yaml_record_count']}"
        )
        assert aggregate["covered_count"] == expected["covered_count"], (
            f"{framework_name}.covered_count: expected "
            f"{expected['covered_count']}, got {aggregate['covered_count']}"
        )
        assert aggregate["partial_count"] == expected["partial_count"], (
            f"{framework_name}.partial_count: expected "
            f"{expected['partial_count']}, got {aggregate['partial_count']}"
        )
        assert aggregate["gap_count"] == expected["gap_count"], (
            f"{framework_name}.gap_count: expected "
            f"{expected['gap_count']}, got {aggregate['gap_count']}"
        )
        assert (
            aggregate["coverage_percentage"] == expected["coverage_percentage"]
        ), (
            f"{framework_name}.coverage_percentage: expected "
            f"{expected['coverage_percentage']!r}, got "
            f"{aggregate['coverage_percentage']!r}"
        )

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "findings_in_scope_only",
            "findings_oos_only",
            "findings_mixed",
        ],
    )
    def test_aggregator_matches_expected_fixture(
        self, extract_report_data, fixture_name
    ):
        """Aggregate output equals hand-computed expected for each fixture pair."""
        findings = _stream_4_findings(fixture_name)
        expected = _stream_4_expected(fixture_name)
        aggregates = extract_report_data.build_per_framework_aggregates(findings)
        agg_by_framework = {a["framework"]: a for a in aggregates}

        for framework_name, expected_shape in expected.items():
            aggregate = agg_by_framework.get(framework_name)
            assert aggregate is not None, (
                f"Aggregator must emit a record for framework "
                f"{framework_name!r}. Frameworks emitted: "
                f"{sorted(agg_by_framework.keys())}"
            )
            self._assert_aggregate_matches_expected(
                aggregate, expected_shape, framework_name
            )

    def test_oos_only_findings_render_on_per_finding_table(
        self, extract_report_data
    ):
        """T046 contract: findings citing OOS items still appear on the
        per-finding attribution table (preserves F-A2 referential-integrity)
        even though the OOS items don't increment covered_count.
        """
        findings = _stream_4_findings("findings_oos_only")
        rows = extract_report_data.build_per_finding_rows(findings)

        # The fixture carries 1 finding (R-1) citing 3 OOS mitre-attack IDs.
        assert len(rows) == 1, (
            f"build_per_finding_rows must emit one row per finding "
            f"regardless of OOS-citation status. Got: {len(rows)}"
        )
        row = rows[0]
        assert row["id"] == "R-1"
        # mitre_refs must carry all 3 cited IDs with ATT&CK: prefix.
        # (The merge contract — T032 — prefixes mitre-attack ids with "ATT&CK:".)
        mitre_refs = row["mitre_refs"]
        assert len(mitre_refs) == 3, (
            f"R-1's mitre_refs must carry all 3 cited OOS IDs (T046: OOS "
            f"items still render on attribution table). Got: {mitre_refs!r}"
        )
        # All 3 IDs must be present even though they're OOS:
        cited_ids = {ref["id"] for ref in mitre_refs}
        assert cited_ids == {
            "ATT&CK:T1070.001",
            "ATT&CK:T1071",
            "ATT&CK:T1041",
        }, (
            f"All 3 cited OOS mitre-attack IDs must render on the per-finding "
            f"row even though they're filtered from the per-framework aggregate. "
            f"Got: {cited_ids!r}"
        )


# ===========================================================================
# Stream 4: Zero-denominator (entirely-Out-of-Scope framework) edge case
# ===========================================================================


class TestStream4ZeroInScopeDenominator:
    """The aggregator must emit ``coverage_percentage: "N/A"`` when
    ``in_scope_yaml_record_count == 0`` for a framework — even when the raw
    ``yaml_record_count`` is non-zero (entirely-Out-of-Scope framework).
    """

    def test_na_when_in_scope_count_is_zero(
        self, extract_report_data, monkeypatch
    ):
        """All-OOS framework: in_scope=0, raw>0, expected = "N/A"."""
        # Stub raw = 3, in_scope = 0 for owasp; preserve other frameworks.
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

        findings = _stream_4_findings("findings_zero_against_all_oos")
        aggregates = extract_report_data.build_per_framework_aggregates(findings)
        owasp = next(a for a in aggregates if a["framework"] == "owasp")

        assert owasp["yaml_record_count"] == 3, (
            f"yaml_record_count must reflect raw stub. "
            f"Got: {owasp['yaml_record_count']}"
        )
        assert owasp["in_scope_yaml_record_count"] == 0
        assert owasp["coverage_percentage"] == "N/A", (
            f"coverage_percentage must be 'N/A' when "
            f"in_scope_yaml_record_count == 0 (entirely-OOS framework) per "
            f"data-model.md §3 line 165. Got: "
            f"{owasp['coverage_percentage']!r}"
        )
        # Items list must be empty per build_per_framework_aggregates line 1247
        # (in_scope_count == 0 short-circuits to []).
        assert owasp["items"] == [], (
            f"items list must be empty when in_scope_count == 0. "
            f"Got: {owasp['items']!r}"
        )
