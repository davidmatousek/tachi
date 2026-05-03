"""Pagination smoke test for the Feature 194 coverage-attestation section.

Wave 3.2 / T038: exercises the per-finding attribution table and per-framework
matrix pages at 100-finding scale to verify:

1. The pagination smoke fixture generator produces a valid YAML fixture.
2. The aggregator (``build_per_finding_rows`` + ``build_per_framework_aggregates``)
   accepts 100-finding input without error.
3. The Typst compile of ``main.typ`` against a synthesized ``report-data.typ``
   including the aggregated output completes with exit code 0.
4. The resulting PDF has at least 5 per-framework pages + at least 1
   per-finding table page (typically 2-3 pages at 100-finding scale).

This is a **smoke test** — not a pixel-perfect visual regression. Its
purpose is to prove the template does not crash or silently truncate at
realistic-scale input, and that Typst's native row-break on the
``table.header(repeat: true)`` per-finding table paginates correctly.

Per T038 contingency note: if portrait US Letter shows overflow (cell text
truncation, illegible fonts), the test surfaces the issue but does NOT
activate landscape fallback. Per FR-012, landscape-orientation fallback is
a contingency carved out for a follow-up if MVP portrait is inadequate.

Tasks referenced: T038 (Pagination Smoke Fixture + Smoke Test).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
TESTS_SCRIPTS_DIR = REPO_ROOT / "tests" / "scripts"
FIXTURES_DIR = TESTS_SCRIPTS_DIR / "fixtures" / "coverage_attestation" / "pagination_smoke"
FIXTURE_YAML = FIXTURES_DIR / "findings.yaml"
GENERATOR_SCRIPT = TESTS_SCRIPTS_DIR / "generate_pagination_fixture.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
TEMPLATE_MAIN = TEMPLATE_DIR / "main.typ"


# ---------------------------------------------------------------------------
# Helper: bring the extract_report_data module onto sys.path.
# ---------------------------------------------------------------------------
# extract-report-data.py uses a hyphenated filename so we load it via a
# pytest fixture that importlib-loads the source path.

@pytest.fixture(scope="module")
def extract_report_data():
    """Load scripts/extract-report-data.py as a Python module."""
    import importlib.util

    module_path = SCRIPTS_DIR / "extract-report-data.py"
    spec = importlib.util.spec_from_file_location("extract_report_data", module_path)
    module = importlib.util.module_from_spec(spec)
    # Add scripts/ to sys.path so the module can locate tachi_parsers.
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pagination_fixture():
    """Regenerate the pagination fixture (deterministic — seed=194).

    Re-runs the generator each module session so the fixture YAML on disk
    tracks the generator script verbatim. Any drift between the generator
    and the committed YAML would be surfaced by CI diffing the working
    tree after the test session.
    """
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(GENERATOR_SCRIPT),
        "--output",
        str(FIXTURE_YAML),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"generate_pagination_fixture.py failed with exit {result.returncode}.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    return FIXTURE_YAML


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_fixture(path: Path) -> list[dict]:
    """Load the pagination fixture YAML as a list of finding dicts."""
    import yaml
    with path.open() as fh:
        data = yaml.safe_load(fh)
    return data if data is not None else []


def _typst_escape(value: str) -> str:
    """Minimal escape of " and \\ for Typst string literals."""
    if value is None:
        return ""
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _synthesize_report_data_typ(
    per_finding_rows: list[dict],
    per_framework_aggregates: list[dict],
) -> str:
    """Synthesize a minimal ``report-data.typ`` fragment carrying the
    coverage-attestation data plus every other variable ``main.typ`` expects.

    The approach: run extract-report-data.py against an existing baseline
    (web-app) to get a full report-data.typ, then overwrite only the
    coverage-attestation declarations with the synthesized aggregator
    output. This keeps the test scope narrow to coverage-attestation
    pagination.
    """
    # Step 1: derive a baseline report-data.typ from web-app.
    target_dir = REPO_ROOT / "examples" / "web-app"
    import tempfile
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".typ", delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)

    env = {**os.environ, "SOURCE_DATE_EPOCH": "1700000000"}
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "extract-report-data.py"),
        "--target-dir",
        str(target_dir),
        "--output",
        str(tmp_path),
        "--template-dir",
        str(TEMPLATE_DIR),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert result.returncode == 0, (
        f"extract-report-data.py failed on web-app baseline: {result.stderr}"
    )

    content = tmp_path.read_text()
    tmp_path.unlink()

    # Step 2: rebuild the 3 coverage-attestation declarations with the
    # synthesized aggregator output.
    rows_lines = ["#let per-finding-rows = ("]
    for row in per_finding_rows:
        row_id = _typst_escape(row.get("id", ""))
        title = _typst_escape(row.get("title", ""))
        severity = _typst_escape(row.get("severity", ""))
        ref_parts = []
        for ref_key, hyphen_key in (
            ("owasp_refs", "owasp-refs"),
            ("mitre_refs", "mitre-refs"),
            ("nist_refs", "nist-refs"),
            ("cwe_refs", "cwe-refs"),
        ):
            refs = row.get(ref_key, []) or ()
            if refs:
                inner = ", ".join(
                    f'(id: "{_typst_escape(r["id"])}", '
                    f'relationship: "{_typst_escape(r["relationship"])}")'
                    for r in refs
                )
                ref_parts.append(f"{hyphen_key}: ({inner},)")
            else:
                ref_parts.append(f"{hyphen_key}: ()")
        rows_lines.append(
            f'  (id: "{row_id}", title: "{title}", severity: "{severity}", '
            f'{", ".join(ref_parts)}),'
        )
    rows_lines.append(")")
    rows_emission = "\n".join(rows_lines)

    agg_lines = ["#let per-framework-aggregates = ("]
    for agg in per_framework_aggregates:
        framework = _typst_escape(agg.get("framework", ""))
        # ``yaml_record_count`` (raw) is read here for layout fidelity with
        # production: pagination smoke layout depends on the rendered
        # "Covered: X / Y = Z%" line which uses the raw denominator (the
        # Typst template at coverage-attestation.typ:164 reads
        # ``yaml-record-count``). Production also emits
        # ``in-scope-record-count`` (per F-241 Stream 4 / T045 / data-model.md
        # §3) so we mirror that here for synthesizer fidelity even though the
        # current Typst template binding doesn't read it yet.
        yaml_count = int(agg.get("yaml_record_count", 0))
        in_scope_count = int(
            agg.get("in_scope_yaml_record_count", yaml_count)
        )
        covered = int(agg.get("covered_count", 0))
        partial = int(agg.get("partial_count", 0))
        gap = int(agg.get("gap_count", 0))
        pct = _typst_escape(agg.get("coverage_percentage", "N/A"))
        items = agg.get("items", []) or ()
        if items:
            items_inner = ", ".join(
                f'(id: "{_typst_escape(it["id"])}", '
                f'classification: "{_typst_escape(it["classification"])}")'
                for it in items
            )
            items_typst = f"({items_inner},)"
        else:
            items_typst = "()"
        agg_lines.append(
            f'  (framework: "{framework}", yaml-record-count: {yaml_count}, '
            f'in-scope-record-count: {in_scope_count}, '
            f'covered-count: {covered}, partial-count: {partial}, '
            f'gap-count: {gap}, coverage-percentage: "{pct}", '
            f'items: {items_typst}),'
        )
    agg_lines.append(")")
    agg_emission = "\n".join(agg_lines)

    # Replace the baseline's 3 F-B declarations with the synthesized versions.
    # The baseline emits:
    #   #let has-source-attribution = false
    #   #let per-finding-rows = ()
    #   #let per-framework-aggregates = ()
    # We swap each to the populated form.
    patched = content
    patched = re.sub(
        r"^#let has-source-attribution = false$",
        "#let has-source-attribution = true",
        patched,
        flags=re.MULTILINE,
    )
    patched = re.sub(
        r"^#let per-finding-rows = \(\)$",
        rows_emission,
        patched,
        flags=re.MULTILINE,
    )
    patched = re.sub(
        r"^#let per-framework-aggregates = \(\)$",
        agg_emission,
        patched,
        flags=re.MULTILINE,
    )
    return patched


def _count_pdf_pages(pdf_path: Path) -> int:
    """Count pages in a PDF by grepping /Type /Page markers.

    Prefers pdfinfo when available (more accurate); falls back to the
    regex heuristic otherwise. The heuristic undercounts in some edge
    cases but is a safe lower bound.
    """
    if shutil.which("pdfinfo"):
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())

    # Fallback: regex search on the raw PDF bytes.
    data = pdf_path.read_bytes()
    matches = re.findall(rb"/Type\s*/Page[^s]", data)
    return len(matches)


# ---------------------------------------------------------------------------
# T038: Pagination smoke test
# ---------------------------------------------------------------------------


def test_pagination_fixture_generator_is_deterministic(pagination_fixture):
    """Generator must produce byte-identical output across two invocations.

    Determinism is a prerequisite for the smoke test: without it, CI could
    see spurious diffs on repeated runs.
    """
    # Re-run and compare.
    import tempfile
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)

    cmd = [
        sys.executable,
        str(GENERATOR_SCRIPT),
        "--output",
        str(tmp_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        assert result.returncode == 0

        fixture_bytes = pagination_fixture.read_bytes()
        second_bytes = tmp_path.read_bytes()
        assert fixture_bytes == second_bytes, (
            "Pagination fixture generator is not deterministic — two "
            "invocations produced different output."
        )
    finally:
        tmp_path.unlink()


def test_pagination_fixture_has_100_findings(pagination_fixture):
    """Fixture must carry exactly 100 findings."""
    findings = _load_fixture(pagination_fixture)
    assert len(findings) == 100, (
        f"Pagination smoke fixture must carry exactly 100 findings. "
        f"Got: {len(findings)}"
    )


def test_pagination_fixture_covers_all_5_frameworks(pagination_fixture):
    """Every framework must appear in at least one finding's citations."""
    findings = _load_fixture(pagination_fixture)
    taxonomies = set()
    for finding in findings:
        for cit in finding.get("source_attribution") or ():
            taxonomies.add(cit.get("taxonomy"))

    expected = {"owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"}
    assert taxonomies == expected, (
        f"Pagination fixture must cite every external framework. "
        f"Got: {taxonomies}. Missing: {expected - taxonomies}. "
        f"Extra: {taxonomies - expected}"
    )


def test_aggregator_accepts_100_finding_input(
    extract_report_data, pagination_fixture
):
    """Both aggregator entry points accept 100-finding input without error."""
    findings = _load_fixture(pagination_fixture)

    rows = extract_report_data.build_per_finding_rows(findings)
    assert len(rows) == 100, (
        f"build_per_finding_rows must emit one row per finding. "
        f"Got: {len(rows)}"
    )

    aggregates = extract_report_data.build_per_framework_aggregates(findings)
    assert len(aggregates) == 5, (
        f"build_per_framework_aggregates must emit exactly 5 records. "
        f"Got: {len(aggregates)}"
    )


def test_pagination_smoke(tmp_path: Path, extract_report_data, pagination_fixture):
    """End-to-end smoke: compile main.typ against 100-finding fixture data.

    Writes a synthesized report-data.typ carrying:
      - per-finding-rows: 100 rows from ``build_per_finding_rows``
      - per-framework-aggregates: 5 aggregates from
        ``build_per_framework_aggregates``
      - has-source-attribution: true

    Swaps the live template-dir ``report-data.typ`` with the synthesized
    one for the duration of the compile, restores it after. Compiles
    ``main.typ`` to a PDF and asserts:

      1. Exit code 0 (no compile errors on 100-finding scale).
      2. PDF has at least ``baseline_pages + 6`` pages — 5 framework pages
         + at least 1 per-finding table page. (The per-finding table at
         100 rows typically spans 2-3 pages; the "at least 1" threshold
         is deliberately loose so the test remains stable under minor
         pagination drift.)

    Per FR-012 contingency: if portrait US Letter shows overflow (cell
    truncation), the assertion messages highlight the mismatch but do NOT
    activate landscape fallback. Landscape fallback is a carved-out
    follow-up.
    """
    if not shutil.which("typst"):
        pytest.skip("typst CLI not available in test environment")

    findings = _load_fixture(pagination_fixture)
    per_finding_rows = extract_report_data.build_per_finding_rows(findings)
    per_framework_aggregates = extract_report_data.build_per_framework_aggregates(findings)

    # Synthesize the report-data.typ with populated coverage attestation.
    synthesized = _synthesize_report_data_typ(
        per_finding_rows, per_framework_aggregates
    )

    # Also compute the baseline (gate=false) PDF page count for comparison.
    baseline_typ = _synthesize_report_data_typ([], [])
    # Baseline path: strip the gate re-write so it reads has-source-attribution=false.
    baseline_typ = baseline_typ.replace(
        "#let has-source-attribution = true",
        "#let has-source-attribution = false",
        1,
    )

    real_report_data = TEMPLATE_DIR / "report-data.typ"
    preexisting_backup = None
    if real_report_data.exists():
        preexisting_backup = real_report_data.read_bytes()

    env = {**os.environ, "SOURCE_DATE_EPOCH": "1700000000"}

    try:
        # --- Baseline compile (gate=false) -----------------------------
        real_report_data.write_text(baseline_typ)
        baseline_pdf = tmp_path / "baseline.pdf"
        result_baseline = subprocess.run(
            [
                "typst",
                "compile",
                str(TEMPLATE_MAIN),
                str(baseline_pdf),
                "--root",
                str(REPO_ROOT),
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result_baseline.returncode == 0, (
            f"Baseline compile (gate=false) failed with exit "
            f"{result_baseline.returncode}:\n"
            f"stdout: {result_baseline.stdout}\n"
            f"stderr: {result_baseline.stderr}"
        )
        baseline_pages = _count_pdf_pages(baseline_pdf)

        # --- Populated compile (gate=true, 100 findings) ---------------
        real_report_data.write_text(synthesized)
        populated_pdf = tmp_path / "populated.pdf"
        result_populated = subprocess.run(
            [
                "typst",
                "compile",
                str(TEMPLATE_MAIN),
                str(populated_pdf),
                "--root",
                str(REPO_ROOT),
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result_populated.returncode == 0, (
            f"Populated compile (100 findings, gate=true) failed with "
            f"exit {result_populated.returncode}. Typst errors indicate "
            f"coverage-attestation template authoring bugs:\n"
            f"stdout: {result_populated.stdout}\n"
            f"stderr: {result_populated.stderr}"
        )
        populated_pages = _count_pdf_pages(populated_pdf)

    finally:
        # Restore or remove the real report-data.typ.
        if preexisting_backup is not None:
            real_report_data.write_bytes(preexisting_backup)
        elif real_report_data.exists():
            try:
                real_report_data.unlink()
            except OSError:
                pass

    # --- Assert pagination delta -------------------------------------
    # Expected: at least 5 framework pages + at least 1 per-finding table
    # page = 6 additional pages over baseline. At 100 findings the
    # per-finding table typically wraps across 2-3 pages, so >=7 is the
    # realistic expectation. Use >=6 as the stable lower bound.
    expected_min_delta = 6
    actual_delta = populated_pages - baseline_pages
    assert actual_delta >= expected_min_delta, (
        f"Coverage attestation section should add at least "
        f"{expected_min_delta} pages over baseline (5 per-framework + "
        f"≥1 per-finding table). Got: baseline={baseline_pages} pages, "
        f"populated={populated_pages} pages, delta={actual_delta}. "
        f"Indicates pagination regression or broken template rendering."
    )

    # Sanity: the PDF must exist and be non-trivial.
    assert populated_pdf.exists(), "Populated PDF must exist after compile"
    assert populated_pdf.stat().st_size > 100_000, (
        f"Populated PDF is suspiciously small "
        f"({populated_pdf.stat().st_size} bytes) — possible content "
        f"truncation."
    )
