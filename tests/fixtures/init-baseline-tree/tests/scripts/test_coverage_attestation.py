"""Tests for the Feature 194 coverage-attestation report section (F-B).

Wave 2.1 TDD "Red" step — tests are authored BEFORE the Wave 2.2+ implementation
lands. Most tests SKIP gracefully on missing attributes (the aggregator
helpers do not yet exist) and will flip to PASS as Wave 2.2 implementation
tasks T011 / T024 / T025 / T026 / T035 land.

The three US3 gate tests (T008 / T009 / T010) reference the already-scaffolded
``compute_has_source_attribution`` stub from Wave 1.1 (T007). T008 passes
trivially because the stub returns ``False`` on every input (matching the
empty-fixture expectation). T009 FAILS at Wave 2.1 because the stub returns
``False`` where the one-primary fixture demands ``True`` — T011 implementation
flips it to Green. T010 validates the main.typ default-value guard contract
(T012) and depends on both T012 (guards) and T013 + T014 (import + conditional
block) being absent-resilient.

Fixture sources:
- tests/scripts/fixtures/coverage_attestation/empty_attribution.yaml
- tests/scripts/fixtures/coverage_attestation/one_primary_attribution.yaml
- tests/scripts/fixtures/coverage_attestation/multi_mixed_attribution.yaml
- tests/scripts/fixtures/coverage_attestation/zero_denominator_framework.yaml

Tasks referenced: T008-T010 (US3 gate), T017-T023 (US2 per-framework),
T031-T034 (US1 per-finding).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from .conftest import monkeypatch_framework_record_counts


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "coverage_attestation"
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
TEMPLATE_MAIN = TEMPLATE_DIR / "main.typ"


# ---------------------------------------------------------------------------
# Fixture loaders
# ---------------------------------------------------------------------------
#
# The coverage_attestation YAML fixtures store a list of finding dicts in the
# shape produced by ``scripts/tachi_parsers.py::parse_threats_findings``. For
# these tests we load the YAML directly (simpler than round-tripping through
# the parser) and hand the list straight to the aggregator helpers.


def _load_fixture(name: str) -> list[dict]:
    """Load a coverage_attestation fixture YAML as a list of finding dicts."""
    path = FIXTURES / name
    with path.open() as fh:
        data = yaml.safe_load(fh)
    return data if data is not None else []


@pytest.fixture
def empty_fixture() -> list[dict]:
    return _load_fixture("empty_attribution.yaml")


@pytest.fixture
def one_primary_fixture() -> list[dict]:
    return _load_fixture("one_primary_attribution.yaml")


@pytest.fixture
def multi_mixed_fixture() -> list[dict]:
    return _load_fixture("multi_mixed_attribution.yaml")


# ---------------------------------------------------------------------------
# Helper: locate an aggregator symbol on the extract_report_data module.
# ---------------------------------------------------------------------------
#
# The aggregator helpers (build_per_framework_aggregates, build_per_finding_rows,
# classify_framework_items, load_framework_yaml_record_counts) do not yet exist
# on the module at Wave 2.1 authoring time. Tests that exercise them use the
# _get_aggregator helper which returns ``None`` when the symbol is absent, and
# a ``pytest.skip`` message so tests collect cleanly and flip to Pass/Fail as
# Wave 2.2 implementation lands.


def _get_symbol(module, name: str):
    """Return the named attribute from ``module`` or ``None`` if absent."""
    return getattr(module, name, None)


def _skip_if_missing(module, name: str, task: str):
    """Skip the calling test if ``module`` does not yet export ``name``."""
    if _get_symbol(module, name) is None:
        pytest.skip(
            f"{name!r} not yet implemented on extract_report_data module — "
            f"will land in Wave 2.2 task {task}."
        )


# =============================================================================
# US3: Conditional-inclusion gate tests (T008-T010)
# =============================================================================


def test_has_source_attribution_false_on_empty_fixture(
    extract_report_data, empty_fixture
):
    """T008 — empty-attribution fixture: gate is False.

    The empty fixture carries 3 findings, NONE of which carries a
    ``source_attribution`` key. The gate predicate must evaluate to ``False``
    so ``main.typ`` omits the entire coverage-attestation section.

    Passes trivially in Wave 2.1 because the stub returns ``False``
    unconditionally. Remains green after T011 implementation because the
    fixture truly carries no attribution on any finding.
    """
    result = extract_report_data.compute_has_source_attribution(empty_fixture)
    assert result is False, (
        "compute_has_source_attribution must return False when no finding "
        f"carries a non-empty source_attribution array. Got: {result!r}"
    )


def test_has_source_attribution_true_on_one_primary_fixture(
    extract_report_data, one_primary_fixture
):
    """T009 — one-primary fixture: gate is True.

    The one-primary fixture carries exactly ONE finding (``LLM-1``) with a
    single primary OWASP citation. The gate predicate must evaluate to ``True``
    so ``main.typ`` renders the coverage-attestation section.

    FAILS in Wave 2.1 because the Wave 1.1 stub returns ``False``
    unconditionally. Flips to PASS when T011 lands the real predicate.
    """
    result = extract_report_data.compute_has_source_attribution(one_primary_fixture)
    assert result is True, (
        "compute_has_source_attribution must return True when ≥1 finding "
        f"carries a non-empty source_attribution array. Got: {result!r}"
    )


def test_default_value_guard_stale_report_data(tmp_path: Path):
    """T010 — stale report-data.typ compiles via the §2b default-value guard.

    Simulates the operational scenario where a user runs main.typ against a
    report-data.typ file generated by an older (pre-F-B) extract-report-data.py
    invocation. The 3 F-B declarations (``has-source-attribution``,
    ``per-finding-rows``, ``per-framework-aggregates``) are absent.

    Contract (FR-004 / SC-004a): the §2b defaults block in main.typ forces
    each absent variable to a safe default (``false`` / ``()``) so Typst does
    NOT raise an "unknown variable" compile error. The coverage-attestation
    section is omitted via the conditional block (T014).

    Initial-state expectation at Wave 2.1: test PASSES only because main.typ
    does not yet reference the F-B vars (T013 #import and T014 conditional
    block have not landed). Once T013 and T014 land without T012 default
    guards, this test goes RED with an "unknown variable" error — which is
    the intended TDD driver for T012.
    """
    if not shutil.which("typst"):
        pytest.skip("typst CLI not available in test environment")

    # Author a minimal stale report-data.typ. The pre-F-B baseline declares
    # every variable that main.typ consumes EXCEPT the 3 F-B additions.
    # The §2b defaults block in main.typ already guards the others, so this
    # subset is sufficient to isolate the F-B guard behavior.
    #
    # We derive the stale file from the current extract-report-data.py output
    # on a real example baseline — the web-app example is the smallest and
    # produces a report-data.typ with every non-F-B variable populated.
    #
    # CRITICAL: --template-dir MUST point at the real TEMPLATE_DIR so the
    # image paths in report-data.typ (logo, infographic paths) resolve
    # relative to where main.typ will actually live at compile time.
    script_path = REPO_ROOT / "scripts" / "extract-report-data.py"
    target_dir = REPO_ROOT / "examples" / "web-app"
    stale_path = tmp_path / "report-data.typ"

    env = {**os.environ, "SOURCE_DATE_EPOCH": "1700000000"}
    extract_cmd = [
        sys.executable,
        str(script_path),
        "--target-dir",
        str(target_dir),
        "--output",
        str(stale_path),
        "--template-dir",
        str(TEMPLATE_DIR),
    ]
    subprocess.run(
        extract_cmd, cwd=REPO_ROOT, env=env, check=True, capture_output=True
    )

    # Defense-in-depth: strip any F-B declarations that might already be
    # emitted by extract-report-data.py (if Wave 2.2 T011/T027/T036 land
    # before T010 is re-run). The stale scenario requires all 3 F-B vars
    # to be absent from the data file.
    content = stale_path.read_text()
    stripped = []
    for line in content.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("#let has-source-attribution"):
            continue
        if stripped_line.startswith("#let per-finding-rows"):
            continue
        if stripped_line.startswith("#let per-framework-aggregates"):
            continue
        stripped.append(line)
    stale_path.write_text("\n".join(stripped) + "\n")

    # Compile main.typ against the stale report-data.typ. We run with the
    # real template dir as cwd and a temp output path, but scope the
    # report-data.typ mutation to the sandbox by pointing main.typ directly
    # at the sandbox copy. --root is set to REPO_ROOT (production convention)
    # but the source file must also live under REPO_ROOT, so we swap the real
    # template_dir's report-data.typ with the stale sandbox version for the
    # duration of the compile and restore it after.
    real_report_data = TEMPLATE_DIR / "report-data.typ"
    preexisting = real_report_data.exists()
    preexisting_backup = None
    if preexisting:
        preexisting_backup = real_report_data.read_bytes()

    try:
        real_report_data.write_bytes(stale_path.read_bytes())

        compile_cmd = [
            "typst",
            "compile",
            str(TEMPLATE_MAIN),
            str(tmp_path / "out.pdf"),
            "--root",
            str(REPO_ROOT),
        ]
        result = subprocess.run(
            compile_cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True
        )
    finally:
        # Restore or remove the real report-data.typ so we do not leave test
        # artifacts in the template directory.
        if preexisting_backup is not None:
            real_report_data.write_bytes(preexisting_backup)
        elif real_report_data.exists():
            try:
                real_report_data.unlink()
            except OSError:
                pass

    assert result.returncode == 0, (
        f"main.typ compile against stale report-data.typ failed with exit "
        f"code {result.returncode}. The §2b defaults block (T012) MUST "
        f"guard the 3 F-B variables (has-source-attribution, "
        f"per-finding-rows, per-framework-aggregates) so stale data files "
        f"compile cleanly.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


# =============================================================================
# US2: Per-framework aggregate tests (T017-T023)
# =============================================================================


def test_per_framework_aggregates_emits_exactly_5_records(
    extract_report_data, multi_mixed_fixture
):
    """T017 — aggregator emits exactly 5 per-framework records.

    The closed external-framework enum (FR-001, ADR-028) is 5-valued:
    owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe. The aggregator MUST
    emit one record per framework, no more and no fewer, regardless of
    whether any finding cites a given framework.
    """
    _skip_if_missing(extract_report_data, "build_per_framework_aggregates", "T026/T027")

    aggregates = extract_report_data.build_per_framework_aggregates(multi_mixed_fixture)

    assert len(aggregates) == 5, (
        f"build_per_framework_aggregates MUST emit exactly 5 records "
        f"(one per external framework). Got: {len(aggregates)}"
    )

    emitted_frameworks = {a["framework"] for a in aggregates}
    expected_frameworks = {
        "owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe",
    }
    assert emitted_frameworks == expected_frameworks, (
        f"Per-framework aggregates must cover the closed 5-value enum. "
        f"Got: {emitted_frameworks}. Missing: "
        f"{expected_frameworks - emitted_frameworks}. Extra: "
        f"{emitted_frameworks - expected_frameworks}"
    )


@pytest.mark.parametrize(
    "fixture_name",
    ["empty_attribution.yaml", "one_primary_attribution.yaml",
     "multi_mixed_attribution.yaml"],
)
def test_partition_invariant(extract_report_data, fixture_name):
    """T018 — covered + partial + gap == in_scope_yaml_record_count per framework.

    The partition invariant (data-model.md §Per-Framework Aggregate Record)
    states that every IN-SCOPE framework item classifies as exactly one of
    Covered / Partial / Gap — no overlap, no omission. The aggregator
    post-condition is ``covered_count + partial_count + gap_count ==
    in_scope_yaml_record_count`` for every framework, across every fixture.

    Post-F-241 Stream 4 (T044/T045/T047): Out-of-Scope records are filtered
    out of the items list at ``build_per_framework_aggregates`` (line ~1241
    of ``extract-report-data.py``), so the partition holds against the
    in-scope denominator — NOT the raw ``yaml_record_count`` (which now
    differs from the in-scope count for ``mitre-attack`` post-T041 expansion:
    701 raw / 323 in-scope).
    """
    _skip_if_missing(extract_report_data, "build_per_framework_aggregates", "T026/T027")

    findings = _load_fixture(fixture_name)
    aggregates = extract_report_data.build_per_framework_aggregates(findings)

    for agg in aggregates:
        total = (
            agg["covered_count"] + agg["partial_count"] + agg["gap_count"]
        )
        assert total == agg["in_scope_yaml_record_count"], (
            f"Partition invariant violated for framework {agg['framework']!r} "
            f"on fixture {fixture_name!r}: covered({agg['covered_count']}) + "
            f"partial({agg['partial_count']}) + gap({agg['gap_count']}) = "
            f"{total} != in_scope_yaml_record_count("
            f"{agg['in_scope_yaml_record_count']})"
        )


def test_classification_rules_q1_a(extract_report_data):
    """T019 — FR-007 / Q1-A 3-value classification rules.

    - Covered → ≥1 finding cites the item with relationship: primary
    - Partial → zero primary AND ≥1 finding cites with related or derived
    - Gap → zero findings cite the item with any relationship

    Uses hand-constructed findings + hand-constructed framework_yaml_records
    so the assertion is independent of the live taxonomy YAML contents.
    """
    _skip_if_missing(extract_report_data, "classify_framework_items", "T025")

    findings = [
        {
            "id": "X-1",
            "source_attribution": [
                {"taxonomy": "owasp", "id": "LLM05", "relationship": "primary"},
            ],
        },
        {
            "id": "X-2",
            "source_attribution": [
                {"taxonomy": "owasp", "id": "LLM06", "relationship": "related"},
            ],
        },
        # Nothing cites LLM07 — it must classify Gap.
    ]
    framework_records = [
        {"id": "LLM05"},
        {"id": "LLM06"},
        {"id": "LLM07"},
    ]

    items = extract_report_data.classify_framework_items(
        findings, "owasp", framework_records
    )
    classification_by_id = {item["id"]: item["classification"] for item in items}

    assert classification_by_id["LLM05"] == "covered", (
        f"Item with ≥1 primary citation must classify Covered. "
        f"Got: {classification_by_id['LLM05']!r}"
    )
    assert classification_by_id["LLM06"] == "partial", (
        f"Item with ≥1 related-only citation (zero primary) must classify "
        f"Partial. Got: {classification_by_id['LLM06']!r}"
    )
    assert classification_by_id["LLM07"] == "gap", (
        f"Item with zero citations must classify Gap. "
        f"Got: {classification_by_id['LLM07']!r}"
    )


def test_coverage_percentage_arithmetic(
    extract_report_data, multi_mixed_fixture
):
    """T020 — coverage percentages match hand-computed values (post Stream 3/4).

    Hand-computed against ``multi_mixed_attribution.yaml`` and the live
    taxonomy YAML record counts post-F-241 Stream 3 expansion + Stream 4
    in-scope-only denominator filter:

    - OWASP: 2 primary citations (LLM05 in LLM-1, A03 in I-4) / 60 in-scope
      records → 3.33% (no OOS filtering — owasp.yaml has 0 OOS records)
    - CWE: 1 primary (CWE-200 in I-4) / 53 in-scope → 1.89% (no OOS records)
    - MITRE-ATTACK: 0 primary / 323 in-scope → 0.00%
        Rationale: the fixture's only `primary` ATT&CK citation, T1070.001
        (Clear Windows Event Logs), is now Out-of-Scope per T041 tactical
        grouping (TA0005 Defense Evasion runs at runtime/IR layer, outside
        tachi's design-time scope). The aggregator filters T1070.001 out of
        the in-scope record set, so it doesn't appear in the items list and
        cannot increment ``covered_count``. The fixture also cites T1078
        (Valid Accounts, in-scope, TA0006 Credential Access) but only as
        ``related`` — that classifies T1078 as ``partial`` (covered_count=0,
        partial_count=1, gap_count=322; 0+1+322 = 323 in-scope partition).
        Pre-Stream-3/4 expected was 2.63% (1/38, raw denominator); the
        Stream 4 in-scope filter + Stream 3 expansion (38 → 701 raw / 323
        in-scope) jointly produce the 0.00% post-fix expected. Per T046
        edge case, T1070.001 still renders on the per-finding attribution
        table for traceability — it's only excluded from the per-framework
        coverage-percentage denominator.
    - MITRE-ATLAS: 0 primary / 30 in-scope → 0.00% (Stream 3 expansion 12 →
      30; the fixture's mitre-atlas citations are all `related`/`derived`
      so this classifies them all as `partial`, 0% covered)
    - NIST-AI-RMF: 0 primary / 72 in-scope → 0.00% (no OOS records)
    """
    _skip_if_missing(extract_report_data, "build_per_framework_aggregates", "T026/T027")

    aggregates = extract_report_data.build_per_framework_aggregates(
        multi_mixed_fixture
    )
    pct_by_framework = {a["framework"]: a["coverage_percentage"] for a in aggregates}

    expected_pct = {
        "owasp": "3.33%",
        "cwe": "1.89%",
        "mitre-attack": "0.00%",
        "mitre-atlas": "0.00%",
        "nist-ai-rmf": "0.00%",
    }

    for framework, expected in expected_pct.items():
        actual = pct_by_framework.get(framework)
        assert actual == expected, (
            f"Coverage percentage mismatch for framework {framework!r}: "
            f"expected {expected!r}, got {actual!r}"
        )


def test_coverage_percentage_na_on_zero_denominator(
    extract_report_data, monkeypatch
):
    """T021 — zero-denominator framework renders coverage_percentage "N/A".

    When a framework YAML is accidentally empty (zero top-level records),
    the coverage fraction is mathematically undefined. Per FR-011(a), the
    aggregator MUST render ``coverage_percentage: "N/A"`` — not ``0/0`` and
    not a ``ZeroDivisionError``.

    Injects zero-item record counts for the owasp framework via
    monkeypatch on BOTH ``load_framework_yaml_record_counts`` (raw) and
    ``load_framework_yaml_in_scope_record_counts`` (in-scope-only, post
    F-241 Stream 4 / T044/T045) so the live YAML on disk is not modified
    (architect M-3). Post-F-241 the coverage-percentage denominator reads
    the in-scope helper, so monkeypatching only the raw helper would leave
    the in-scope path returning live disk values and the assertion would
    fall through.
    """
    _skip_if_missing(
        extract_report_data, "build_per_framework_aggregates", "T026/T027"
    )
    _skip_if_missing(
        extract_report_data, "load_framework_yaml_record_counts", "T024"
    )
    _skip_if_missing(
        extract_report_data,
        "load_framework_yaml_in_scope_record_counts",
        "T045",
    )

    # Stream 3 inventory counts: 701 raw / 323 in-scope for mitre-attack;
    # owasp zeroed to exercise the zero-denominator "N/A" branch.
    monkeypatch_framework_record_counts(
        monkeypatch,
        extract_report_data,
        raw={"owasp": 0, "mitre-attack": 701, "mitre-atlas": 30, "nist-ai-rmf": 72, "cwe": 53},
        in_scope={"owasp": 0, "mitre-attack": 323, "mitre-atlas": 30, "nist-ai-rmf": 72, "cwe": 53},
    )

    # Non-empty finding set so the gate predicate is True.
    findings = _load_fixture("multi_mixed_attribution.yaml")
    aggregates = extract_report_data.build_per_framework_aggregates(findings)

    owasp_agg = next(a for a in aggregates if a["framework"] == "owasp")
    assert owasp_agg["coverage_percentage"] == "N/A", (
        f"coverage_percentage for zero-denominator framework MUST be 'N/A' "
        f"per FR-011(a). Got: {owasp_agg['coverage_percentage']!r}"
    )


def test_coverage_percentage_0pct_on_zero_numerator(extract_report_data):
    """T022 — zero-numerator framework renders coverage_percentage "0.00%".

    Per FR-011(b), a framework with a non-zero denominator but zero primary
    attributions must render ``"0.00%"``. The multi_mixed fixture cites zero
    nist-ai-rmf and mitre-atlas primaries (mitre-atlas has 1 related + 1
    derived — zero primary); both frameworks must render 0.00% on that
    fixture.

    This scope is stricter than the empty-fixture case because it proves
    the aggregator handles "non-empty finding set + zero primaries for
    framework X" separately from the all-empty gate case.
    """
    _skip_if_missing(extract_report_data, "build_per_framework_aggregates", "T026/T027")

    findings = _load_fixture("multi_mixed_attribution.yaml")
    aggregates = extract_report_data.build_per_framework_aggregates(findings)
    pct_by_framework = {a["framework"]: a["coverage_percentage"] for a in aggregates}

    # nist-ai-rmf is NOT cited at all in multi_mixed (known limitation noted
    # in the fixture). mitre-atlas IS cited, but only with related + derived
    # (zero primary), which should also yield 0.00%.
    for framework in ("nist-ai-rmf", "mitre-atlas"):
        assert pct_by_framework[framework] == "0.00%", (
            f"Framework {framework!r} has zero primary citations on "
            f"multi_mixed fixture; coverage_percentage must be '0.00%' "
            f"per FR-011(b). Got: {pct_by_framework[framework]!r}"
        )


def test_aggregator_fails_loud_on_malformed_yaml(extract_report_data):
    """T023 — malformed framework YAML raises yaml.YAMLError.

    Per FR-011(c) / ADR-022 fail-loud pattern, the aggregator MUST NOT
    silently emit empty aggregates when a framework YAML fails safe_load.
    A yaml.YAMLError (or a wrapping exception that surfaces the offending
    framework name and the underlying error) MUST propagate.
    """
    _skip_if_missing(
        extract_report_data, "load_framework_yaml_record_counts", "T024"
    )

    def _raise_yaml_error(*args, **kwargs):
        raise yaml.YAMLError("malformed: simulated safe_load failure")

    # Patch yaml.safe_load on the yaml module directly. extract-report-data.py
    # imports yaml lazily inside _load_framework_yaml_records (stdlib-only
    # module-load invariant), so the patch target is the shared yaml module
    # rather than a module-level attribute of extract_report_data. The loader
    # is lru_cached for hot-path performance; clear the cache so this test
    # actually exercises yaml.safe_load rather than returning cached records
    # populated by a prior test in the same session.
    extract_report_data._load_framework_yaml_records.cache_clear()
    with patch.object(yaml, "safe_load", _raise_yaml_error):
        with pytest.raises((yaml.YAMLError, RuntimeError, OSError)) as exc_info:
            extract_report_data.load_framework_yaml_record_counts()

    # Best-effort assertion that the error surfaces something identifying the
    # context — either the original YAML message or a framework name. Does
    # not require an exact wrapper format (T024 implementation chooses).
    message = str(exc_info.value)
    assert message, (
        "Error raised by load_framework_yaml_record_counts must carry a "
        "non-empty message (ADR-022 fail-loud actionability)."
    )


# =============================================================================
# US1: Per-finding attribution row tests (T031-T034)
# =============================================================================


def test_per_finding_row_count_matches_finding_count(
    extract_report_data, multi_mixed_fixture
):
    """T031 — one row per finding, including findings without attribution.

    Per FR-006 / data-model.md: every finding in the input list produces
    exactly one Per-Finding Attribution Row, including findings with absent
    or empty ``source_attribution``. The row for such findings has all 4
    ``*_refs`` arrays as empty lists (not omitted keys).
    """
    _skip_if_missing(extract_report_data, "build_per_finding_rows", "T035")

    rows = extract_report_data.build_per_finding_rows(multi_mixed_fixture)

    assert len(rows) == len(multi_mixed_fixture), (
        f"One-row-per-finding invariant violated: input carries "
        f"{len(multi_mixed_fixture)} findings, aggregator emitted "
        f"{len(rows)} rows."
    )

    # Finding T-5 carries no source_attribution; its row must still appear
    # with all 4 ref arrays present as empty lists.
    finding_t5 = next(r for r in rows if r["id"] == "T-5")
    for ref_key in ("owasp_refs", "mitre_refs", "nist_refs", "cwe_refs"):
        assert ref_key in finding_t5, (
            f"Finding T-5 (no source_attribution) row must still carry "
            f"key {ref_key!r}. Keys present: {sorted(finding_t5.keys())}"
        )
        assert finding_t5[ref_key] == [], (
            f"Finding T-5 (no source_attribution) must emit empty list for "
            f"{ref_key!r}. Got: {finding_t5[ref_key]!r}"
        )


def test_per_finding_row_mitre_merge_with_prefix(extract_report_data):
    """T032 — MITRE column merges ATT&CK and ATLAS with a per-ref prefix.

    Per FR-005, the MITRE column groups ``mitre-attack`` and ``mitre-atlas``
    citations into a single ``mitre_refs`` list, with each entry's ``id``
    prefixed by its framework family: ``"ATT&CK:T1070.001"`` for mitre-attack
    and ``"ATLAS:AML.T0051"`` for mitre-atlas.
    """
    _skip_if_missing(extract_report_data, "build_per_finding_rows", "T035")

    finding = {
        "id": "X-1",
        "title": "Merge test",
        "severity": "high",
        "source_attribution": [
            {"taxonomy": "mitre-attack", "id": "T1070.001", "relationship": "primary"},
            {"taxonomy": "mitre-atlas", "id": "AML.T0051", "relationship": "primary"},
        ],
    }

    rows = extract_report_data.build_per_finding_rows([finding])
    assert len(rows) == 1

    mitre_refs = rows[0]["mitre_refs"]
    assert mitre_refs == [
        {"id": "ATT&CK:T1070.001", "relationship": "primary"},
        {"id": "ATLAS:AML.T0051", "relationship": "primary"},
    ], (
        f"MITRE ref merge + prefix failed. Expected ATT&CK: / ATLAS: "
        f"prefixes on merged mitre_refs. Got: {mitre_refs!r}"
    )


def test_per_finding_row_grouping_by_taxonomy(extract_report_data):
    """T033 — per-finding row partitions attribution records by taxonomy.

    A finding citing OWASP primary + CWE related must emit:
    - owasp_refs  = [{id: "LLM05", relationship: "primary"}]
    - cwe_refs    = [{id: "CWE-1333", relationship: "related"}]
    - mitre_refs  = []
    - nist_refs   = []

    Uses ``CWE-1333`` (present in the real cwe.yaml) rather than the
    hypothetical ``CWE-1426`` cited in the spec example, to keep the test
    aligned with the live F-A1 catalog.
    """
    _skip_if_missing(extract_report_data, "build_per_finding_rows", "T035")

    finding = {
        "id": "X-1",
        "title": "Grouping test",
        "severity": "high",
        "source_attribution": [
            {"taxonomy": "owasp", "id": "LLM05", "relationship": "primary"},
            {"taxonomy": "cwe", "id": "CWE-1333", "relationship": "related"},
        ],
    }

    rows = extract_report_data.build_per_finding_rows([finding])
    assert len(rows) == 1
    row = rows[0]

    assert row["owasp_refs"] == [
        {"id": "LLM05", "relationship": "primary"}
    ], f"owasp_refs mismatch: {row['owasp_refs']!r}"
    assert row["cwe_refs"] == [
        {"id": "CWE-1333", "relationship": "related"}
    ], f"cwe_refs mismatch: {row['cwe_refs']!r}"
    assert row["mitre_refs"] == [], (
        f"mitre_refs must be empty when no mitre-* taxonomy cited. "
        f"Got: {row['mitre_refs']!r}"
    )
    assert row["nist_refs"] == [], (
        f"nist_refs must be empty when no nist-ai-rmf taxonomy cited. "
        f"Got: {row['nist_refs']!r}"
    )


def test_per_finding_row_preserves_input_order(
    extract_report_data, multi_mixed_fixture
):
    """T034 — aggregator preserves input finding-list order (no re-sort).

    Per data-model.md Invariants §Per-Finding Attribution Row: emission
    order mirrors the input finding-list order. The aggregator MUST NOT
    re-sort by severity, finding-id, or any other field.

    The multi_mixed fixture lists findings in order: LLM-1, R-2, AG-3, I-4,
    T-5. The emitted rows must mirror that order exactly.
    """
    _skip_if_missing(extract_report_data, "build_per_finding_rows", "T035")

    rows = extract_report_data.build_per_finding_rows(multi_mixed_fixture)
    emitted_order = [r["id"] for r in rows]
    input_order = [f["id"] for f in multi_mixed_fixture]

    assert emitted_order == input_order, (
        f"Per-finding row order must mirror input finding-list order "
        f"(no re-sort). Expected: {input_order!r}, got: {emitted_order!r}"
    )
