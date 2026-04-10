"""US-2 PDF page-positioning test for the Executive Threat Architecture page.

This module automates the T023 manual end-to-end verification (see
``specs/128-prd-128-executive/manual-verification.md``): it runs the full
extraction + Typst compile pipeline against ``examples/agentic-app/sample-report/``
with a placeholder ``threat-executive-architecture.jpg`` in place, then asserts
that the rendered PDF places the Executive Threat Architecture page *between*
Executive Summary and Attack Path Analysis.

Why relative ordering only
--------------------------
The absolute page numbers observed in T023 (10 / 11 / 12) are example-dependent:
the number of findings, attack trees, and optional infographic images can all
shift the three sections forward or backward across examples. This test asserts
*relative order* only — Executive Threat Architecture > Executive Summary AND
Executive Threat Architecture < Attack Path Analysis — so it survives any
legitimate content drift on the ``agentic-app`` example without needing to be
re-baselined.

Why the placeholder JPEG
------------------------
``examples/agentic-app/sample-report/`` does not yet contain a real
Gemini-generated ``threat-executive-architecture.jpg``; that image will land in
T033 (Phase 7 regeneration). Until then, the ``has-executive-architecture``
flag in ``extract-report-data.py`` only checks for *presence* and *non-zero
size* of the file, so we copy the existing ``threat-system-architecture.jpg``
under the new name to satisfy the detection logic. The placeholder is removed
in a ``try/finally`` block regardless of test outcome — leaving stale files in
the examples tree would pollute downstream tasks.

T029 placeholder
----------------
The skip-image branch (flag=false, page should NOT appear) is covered by T029
in Wave 5 (US-4) via a second test function
``test_executive_architecture_skip_image_pdf_omits_page`` that will be appended
to this same file. This file intentionally leaves room for that second test.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


# Repository root resolved from this file's location:
# tests/scripts/test_pdf_page_positioning.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
MAIN_TYP = TEMPLATE_DIR / "main.typ"
REPORT_DATA_TYP = TEMPLATE_DIR / "report-data.typ"
AGENTIC_APP_SAMPLE = REPO_ROOT / "examples" / "agentic-app" / "sample-report"
SOURCE_JPEG = AGENTIC_APP_SAMPLE / "threat-system-architecture.jpg"
PLACEHOLDER_JPEG = AGENTIC_APP_SAMPLE / "threat-executive-architecture.jpg"

# Deterministic timestamp for compile reproducibility (consistent with T024).
SOURCE_DATE_EPOCH = "1700000000"

# How many leading lines of each extracted page we scan for section headings.
# 25 is enough to cover the typical section-divider layout (header + title +
# leading content). TOC pages are excluded via the "Table of Contents" marker
# (see ``_find_first_page_with_heading``), so this window can safely be a bit
# generous without risk of capturing TOC entries.
PAGE_HEADING_SCAN_LINES = 25


def _find_first_page_with_heading(pages, heading):
    """Return 1-based page index of the first *section-divider* page for ``heading``.

    ``pages`` is the list produced by splitting the ``pdftotext -layout`` output
    on the form-feed character. The function scans the first
    ``PAGE_HEADING_SCAN_LINES`` lines of each page and applies two filters to
    avoid false positives from the Table of Contents:

    1. **Skip TOC pages**: any page whose scan window contains
       ``"Table of Contents"`` is skipped entirely. The TOC page on the
       agentic-app example lists every section with leader dots, so a naive
       substring match on ``"Executive Summary"`` would land on the TOC page
       (page 3) instead of the real section divider (page 10).

    2. **Reject dot-leader lines**: the TOC entries render as
       ``"Executive Summary . . . . . . . . . 10"`` in ``pdftotext -layout``
       output. Any line containing ``". . ."`` or ``"..."`` is assumed to be
       a TOC leader and skipped, even on pages that don't carry the literal
       ``"Table of Contents"`` marker (defensive — the main.typ layout puts
       the TOC on a dedicated page, but this guards against future layout
       churn that might leave a TOC fragment on a content page).

    Returns ``None`` if no page contains the heading after these filters.
    """
    for idx, page_text in enumerate(pages, start=1):
        lines = page_text.splitlines()[:PAGE_HEADING_SCAN_LINES]
        # Filter 1: skip TOC pages
        if any("Table of Contents" in line for line in lines):
            continue
        # Filter 2: look for the heading in a non-dot-leader line
        for line in lines:
            if heading not in line:
                continue
            if ". . ." in line or "..." in line:
                # TOC leader line — skip
                continue
            return idx
    return None


def test_executive_architecture_page_position(tmp_path):
    """Verify the Executive Threat Architecture page renders between Exec Summary
    and Attack Path Analysis when the placeholder image is present.

    Pipeline:
        1. Copy ``threat-system-architecture.jpg`` to
           ``threat-executive-architecture.jpg`` in the agentic-app sample
           folder (placeholder — T033 will replace with real Gemini output).
        2. Run ``scripts/extract-report-data.py`` to emit ``report-data.typ``
           with ``has-executive-architecture = true`` and the relative image
           path.
        3. Run ``typst compile`` against ``main.typ`` producing a PDF in
           ``tmp_path``.
        4. Extract per-page text with ``pdftotext -layout`` and split on the
           form-feed (``\\x0c``) separator.
        5. Locate the first page containing each of the three section
           headings in its first 25 lines.
        6. Assert relative ordering + small spread window.

    Cleanup runs in a ``finally`` block regardless of outcome: the placeholder
    JPEG and the intermediate ``report-data.typ`` are both deleted.
    """
    # Guard: skip if neither pdftotext nor pypdf is available. pdftotext is
    # installed on the dev machine and in CI; this is purely defensive.
    pdftotext_bin = shutil.which("pdftotext")
    pypdf_available = False
    if pdftotext_bin is None:
        try:
            import pypdf  # noqa: F401
            pypdf_available = True
        except ImportError:
            pass
    if pdftotext_bin is None and not pypdf_available:
        pytest.skip(
            "Neither 'pdftotext' (poppler) nor 'pypdf' is available — "
            "cannot extract per-page text from the generated PDF."
        )

    # Guard: the source JPEG we copy from must exist, otherwise the test
    # cannot produce a valid placeholder.
    assert SOURCE_JPEG.exists(), (
        f"Source JPEG for placeholder copy not found: {SOURCE_JPEG}. "
        "The agentic-app sample must contain threat-system-architecture.jpg."
    )

    # Paths for intermediate artifacts in the pytest-managed tmp dir
    tmp_pdf = tmp_path / "security-report.pdf"
    tmp_txt = tmp_path / "security-report.txt"

    placeholder_created = False
    report_data_created = False
    try:
        # Step 1: Stage the placeholder JPEG. Only create if not already
        # present — if a previous test left one behind (shouldn't happen, but
        # defensive), we don't clobber it.
        if not PLACEHOLDER_JPEG.exists():
            shutil.copyfile(SOURCE_JPEG, PLACEHOLDER_JPEG)
            placeholder_created = True
        assert PLACEHOLDER_JPEG.exists(), (
            f"Failed to stage placeholder JPEG at {PLACEHOLDER_JPEG}"
        )
        assert PLACEHOLDER_JPEG.stat().st_size > 0, (
            "Placeholder JPEG is zero-byte — has-executive-architecture "
            "detection requires non-zero size."
        )

        # Deterministic env for reproducible Typst output (parity with T024)
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH

        # Step 2: Run the extraction script against the agentic-app sample
        extract_cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--target-dir", str(AGENTIC_APP_SAMPLE),
            "--output", str(REPORT_DATA_TYP),
            "--template-dir", str(TEMPLATE_DIR),
        ]
        extract_result = subprocess.run(
            extract_cmd,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert extract_result.returncode == 0, (
            f"extract-report-data.py failed with exit {extract_result.returncode}.\n"
            f"stdout: {extract_result.stdout}\nstderr: {extract_result.stderr}"
        )
        assert REPORT_DATA_TYP.exists(), (
            f"Expected report-data.typ at {REPORT_DATA_TYP}, but file was not "
            "written by extract-report-data.py."
        )
        report_data_created = True

        # Sanity-check the flag — if this assertion fails, the compile step
        # would silently skip the page and the ordering assertion below would
        # produce a confusing error.
        report_data_content = REPORT_DATA_TYP.read_text(encoding="utf-8")
        assert "#let has-executive-architecture = true" in report_data_content, (
            "Expected '#let has-executive-architecture = true' in report-data.typ "
            "after staging the placeholder JPEG. Found:\n"
            f"{report_data_content[:500]}"
        )

        # Step 3: Typst compile. --root . ensures the template can resolve
        # the relative image path computed by extract-report-data.py (which
        # walks up from templates/tachi/security-report/ to examples/...).
        compile_cmd = [
            "typst",
            "compile",
            str(MAIN_TYP),
            str(tmp_pdf),
            "--root", str(REPO_ROOT),
        ]
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert compile_result.returncode == 0, (
            f"typst compile failed with exit {compile_result.returncode}.\n"
            f"stdout: {compile_result.stdout}\nstderr: {compile_result.stderr}"
        )
        assert tmp_pdf.exists() and tmp_pdf.stat().st_size > 0, (
            f"typst produced no output at {tmp_pdf} (or zero-byte file)."
        )

        # Step 4: Extract per-page text. Prefer pdftotext -layout (matches
        # T023 manual verification tooling); fall back to pypdf if unavailable.
        if pdftotext_bin is not None:
            pdftotext_cmd = [
                pdftotext_bin,
                "-layout",
                str(tmp_pdf),
                str(tmp_txt),
            ]
            pdftotext_result = subprocess.run(
                pdftotext_cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            assert pdftotext_result.returncode == 0, (
                f"pdftotext failed with exit {pdftotext_result.returncode}.\n"
                f"stderr: {pdftotext_result.stderr}"
            )
            full_text = tmp_txt.read_text(encoding="utf-8", errors="replace")
            # pdftotext -layout writes form feeds (\x0c) between pages
            pages = full_text.split("\x0c")
            # A trailing empty element is common after the final form feed;
            # strip it so page numbering matches the PDF.
            if pages and pages[-1].strip() == "":
                pages = pages[:-1]
        else:
            # pypdf fallback — one call per page
            import pypdf
            reader = pypdf.PdfReader(str(tmp_pdf))
            pages = [page.extract_text() or "" for page in reader.pages]

        assert len(pages) > 0, "Extracted zero pages from the generated PDF."

        # Step 5: Locate the three section heading pages
        exec_summary_page = _find_first_page_with_heading(
            pages, "Executive Summary"
        )
        exec_architecture_page = _find_first_page_with_heading(
            pages, "Executive Threat Architecture"
        )
        attack_path_page = _find_first_page_with_heading(
            pages, "Attack Path Analysis"
        )

        # Step 6: Assertions
        assert exec_summary_page is not None, (
            "Could not find 'Executive Summary' heading on any page "
            "(checked first %d lines of each page)." % PAGE_HEADING_SCAN_LINES
        )
        assert exec_architecture_page is not None, (
            "Could not find 'Executive Threat Architecture' heading on any "
            "page. Expected the page to be inserted when "
            "has-executive-architecture = true. Checked first %d lines of "
            "each page." % PAGE_HEADING_SCAN_LINES
        )
        assert attack_path_page is not None, (
            "Could not find 'Attack Path Analysis' heading on any page. "
            "agentic-app sample should contain attack trees. Checked first "
            "%d lines of each page." % PAGE_HEADING_SCAN_LINES
        )

        # Relative ordering — the core contract of T025
        assert exec_architecture_page > exec_summary_page, (
            f"Executive Threat Architecture (page {exec_architecture_page}) "
            f"must appear AFTER Executive Summary (page {exec_summary_page}). "
            "US-2 requires the new page to be inserted between Executive "
            "Summary and Attack Path Analysis."
        )
        assert exec_architecture_page < attack_path_page, (
            f"Executive Threat Architecture (page {exec_architecture_page}) "
            f"must appear BEFORE Attack Path Analysis (page {attack_path_page}). "
            "US-2 requires the new page to be inserted between Executive "
            "Summary and Attack Path Analysis."
        )

    finally:
        # Cleanup: always remove the placeholder JPEG and the intermediate
        # report-data.typ, even if the test failed. Leaving either behind
        # would pollute downstream tasks (T033 writes the real JPEG; other
        # tests expect report-data.typ to be generated fresh).
        if placeholder_created and PLACEHOLDER_JPEG.exists():
            try:
                PLACEHOLDER_JPEG.unlink()
            except OSError:
                pass
        if report_data_created and REPORT_DATA_TYP.exists():
            try:
                REPORT_DATA_TYP.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# T029 (Wave 5, US-4):
# test_executive_architecture_skip_image_pdf_omits_page
#
# Covers the absent-image branch — the end-to-end downstream effect of
# ``extract-infographic-data.py`` setting ``metadata.skip_image = true`` when
# no Critical/High findings exist. Under that condition the infographic agent
# does NOT invoke Gemini, so no ``threat-executive-architecture.jpg`` is
# created. This test verifies that when the JPEG is absent, the rendered PDF
# does NOT contain an Executive Threat Architecture page.
#
# This is the PDF-side test only. The extraction-side skip_image behavior is
# covered by Wave 3 T006's extraction bundle
# (``test_executive_architecture_no_critical_high_skip_image``).
# ---------------------------------------------------------------------------


def test_executive_architecture_skip_image_pdf_omits_page(tmp_path):
    """Verify the Executive Threat Architecture page is OMITTED from the PDF
    when ``threat-executive-architecture.jpg`` is absent (the skip_image=true
    downstream effect).

    Pipeline:
        1. Assert ``threat-executive-architecture.jpg`` does NOT exist in
           ``examples/agentic-app/sample-report/`` (skip test if it does, to
           avoid clobbering a real Gemini output from T033).
        2. Run ``scripts/extract-report-data.py`` against the agentic-app
           sample folder. Because the JPEG is absent, ``detect_images()``
           sets ``has-executive-architecture = false`` in the generated
           ``report-data.typ``.
        3. Run ``typst compile`` against ``main.typ`` producing a PDF in
           ``tmp_path``. The conditional block in ``main.typ`` should skip
           the Executive Threat Architecture page entirely.
        4. Extract per-page text with ``pdftotext -layout`` (with a ``pypdf``
           fallback, matching the present-branch test above).
        5. Assert NO page's first ``PAGE_HEADING_SCAN_LINES`` lines contain
           the literal "Executive Threat Architecture" string (modulo TOC
           leader filtering via ``_find_first_page_with_heading``).
        6. Sanity-assert that "Executive Summary" and "Attack Path Analysis"
           ARE present — these sections must still render so a missing
           heading on page 1 doesn't silently pass the omission check.
        7. Assert the report-data.typ flag is ``false`` before cleanup.

    Cleanup runs in a ``finally`` block: the intermediate ``report-data.typ``
    is deleted. This test does NOT create any placeholder JPEG, so nothing
    needs to be cleaned up in the examples tree.
    """
    # Guard: skip if neither pdftotext nor pypdf is available (same pattern
    # as the present-branch test).
    pdftotext_bin = shutil.which("pdftotext")
    pypdf_available = False
    if pdftotext_bin is None:
        try:
            import pypdf  # noqa: F401
            pypdf_available = True
        except ImportError:
            pass
    if pdftotext_bin is None and not pypdf_available:
        pytest.skip(
            "Neither 'pdftotext' (poppler) nor 'pypdf' is available — "
            "cannot extract per-page text from the generated PDF."
        )

    # Temporarily move the JPEG aside so the test exercises the
    # absent-image branch. After T033 landed, the real Gemini output lives at
    # PLACEHOLDER_JPEG, so simply skipping when it exists would leave the
    # absent-branch contract untested. Instead, stash the real file and
    # restore it in finally, guaranteeing the committed example stays intact
    # regardless of test outcome.
    jpeg_backup = None
    if PLACEHOLDER_JPEG.exists():
        jpeg_backup = tmp_path / "threat-executive-architecture.jpg.backup"
        shutil.move(str(PLACEHOLDER_JPEG), str(jpeg_backup))

    # Paths for intermediate artifacts in the pytest-managed tmp dir
    tmp_pdf = tmp_path / "security-report.pdf"
    tmp_txt = tmp_path / "security-report.txt"

    report_data_created = False
    try:
        # Deterministic env for reproducible Typst output (parity with T024)
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH

        # Step 2: Run the extraction script against the agentic-app sample.
        # With no JPEG in place, detect_images() must emit
        # has-executive-architecture = false.
        extract_cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--target-dir", str(AGENTIC_APP_SAMPLE),
            "--output", str(REPORT_DATA_TYP),
            "--template-dir", str(TEMPLATE_DIR),
        ]
        extract_result = subprocess.run(
            extract_cmd,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert extract_result.returncode == 0, (
            f"extract-report-data.py failed with exit {extract_result.returncode}.\n"
            f"stdout: {extract_result.stdout}\nstderr: {extract_result.stderr}"
        )
        assert REPORT_DATA_TYP.exists(), (
            f"Expected report-data.typ at {REPORT_DATA_TYP}, but file was not "
            "written by extract-report-data.py."
        )
        report_data_created = True

        # Verify the flag is false — if this assertion fails, the absent-JPEG
        # branch of detect_images() is broken and the page-omission assertion
        # below would produce a confusing error.
        report_data_content = REPORT_DATA_TYP.read_text(encoding="utf-8")
        assert "#let has-executive-architecture = false" in report_data_content, (
            "Expected '#let has-executive-architecture = false' in report-data.typ "
            "when the JPEG is absent. Found:\n"
            f"{report_data_content[:500]}"
        )

        # Step 3: Typst compile. --root . ensures the template can resolve
        # relative image paths for the OTHER infographic images (funnel,
        # baseball card, system architecture) which DO exist in the sample.
        compile_cmd = [
            "typst",
            "compile",
            str(MAIN_TYP),
            str(tmp_pdf),
            "--root", str(REPO_ROOT),
        ]
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert compile_result.returncode == 0, (
            f"typst compile failed with exit {compile_result.returncode}.\n"
            f"stdout: {compile_result.stdout}\nstderr: {compile_result.stderr}"
        )
        assert tmp_pdf.exists() and tmp_pdf.stat().st_size > 0, (
            f"typst produced no output at {tmp_pdf} (or zero-byte file)."
        )

        # Step 4: Extract per-page text. Prefer pdftotext -layout (matches
        # T023 manual verification tooling); fall back to pypdf if unavailable.
        if pdftotext_bin is not None:
            pdftotext_cmd = [
                pdftotext_bin,
                "-layout",
                str(tmp_pdf),
                str(tmp_txt),
            ]
            pdftotext_result = subprocess.run(
                pdftotext_cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            assert pdftotext_result.returncode == 0, (
                f"pdftotext failed with exit {pdftotext_result.returncode}.\n"
                f"stderr: {pdftotext_result.stderr}"
            )
            full_text = tmp_txt.read_text(encoding="utf-8", errors="replace")
            pages = full_text.split("\x0c")
            if pages and pages[-1].strip() == "":
                pages = pages[:-1]
        else:
            import pypdf
            reader = pypdf.PdfReader(str(tmp_pdf))
            pages = [page.extract_text() or "" for page in reader.pages]

        assert len(pages) > 0, "Extracted zero pages from the generated PDF."

        # Step 5: Assert NO page contains "Executive Threat Architecture" in
        # its first PAGE_HEADING_SCAN_LINES lines (after TOC filtering).
        # Reuse _find_first_page_with_heading so the test shares the exact
        # same TOC-filtering logic as the present-branch test — if either
        # test drifts in what counts as a "heading match", both drift
        # together.
        exec_architecture_page = _find_first_page_with_heading(
            pages, "Executive Threat Architecture"
        )
        assert exec_architecture_page is None, (
            f"Found 'Executive Threat Architecture' heading on page "
            f"{exec_architecture_page}, but the JPEG is absent and "
            "has-executive-architecture = false. The conditional block in "
            "main.typ must omit the page entirely when the flag is false. "
            "Check main.typ's Executive Threat Architecture conditional "
            "and extract-report-data.py's detect_images()."
        )

        # Step 6: Sanity-check that the pipeline DID produce the expected
        # surrounding sections. If Executive Summary or Attack Path Analysis
        # are also missing, the pipeline is broken and the page-omission
        # assertion above is a false positive (it would pass if the PDF were
        # entirely empty).
        exec_summary_page = _find_first_page_with_heading(
            pages, "Executive Summary"
        )
        attack_path_page = _find_first_page_with_heading(
            pages, "Attack Path Analysis"
        )
        assert exec_summary_page is not None, (
            "Could not find 'Executive Summary' heading on any page — the "
            "skip-image branch must NOT break the surrounding sections. "
            "The Executive Threat Architecture omission assertion above is "
            "meaningless if the pipeline produced an empty or broken PDF."
        )
        assert attack_path_page is not None, (
            "Could not find 'Attack Path Analysis' heading on any page — "
            "agentic-app sample has 8 attack trees and they must render in "
            "both the present and absent branches."
        )

        # With the page omitted, Attack Path Analysis should follow directly
        # after Executive Summary (no gap page for Executive Threat
        # Architecture in between). T023 observed page 10 → page 11 in the
        # absent branch. We don't assert the absolute values (content drift
        # can shift them) — we assert the gap is at most 1 page, matching the
        # omission of exactly one page.
        gap = attack_path_page - exec_summary_page
        assert gap == 1, (
            f"Expected Attack Path Analysis (page {attack_path_page}) to "
            f"appear exactly 1 page after Executive Summary (page "
            f"{exec_summary_page}) in the skip-image branch, got gap={gap}. "
            "A gap > 1 suggests the Executive Threat Architecture page is "
            "still being inserted (or some other unexpected page sits "
            "between them)."
        )

    finally:
        # Cleanup: always remove the intermediate report-data.typ, even if
        # the test failed. Restore the stashed real JPEG if we moved it aside
        # so the committed example is never left in a broken state.
        if report_data_created and REPORT_DATA_TYP.exists():
            try:
                REPORT_DATA_TYP.unlink()
            except OSError:
                pass
        if jpeg_backup is not None and jpeg_backup.exists():
            try:
                shutil.move(str(jpeg_backup), str(PLACEHOLDER_JPEG))
            except OSError:
                pass
