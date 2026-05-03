"""PDF page-positioning tests for the Executive Threat Architecture page.

Runs the extraction + Typst compile pipeline against
``examples/agentic-app/sample-report/`` with a placeholder
``threat-executive-architecture.jpg`` in place, then asserts that the rendered
PDF places the Executive Threat Architecture page *between* Executive Summary
and Attack Path Analysis.

Absolute page numbers are content-dependent (findings, attack trees, and optional
infographic images all shift sections forward and backward), so this test asserts
*relative order* only. That lets it survive legitimate content drift on the
``agentic-app`` example without a baseline rebuild.

The placeholder JPEG is a copy of the real ``threat-system-architecture.jpg``
under the executive-architecture filename, used because
``has-executive-architecture`` in ``extract-report-data.py`` only checks for
presence and non-zero size. The placeholder is removed in a ``try/finally``
block regardless of test outcome so it does not pollute the examples tree.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
MAIN_TYP = TEMPLATE_DIR / "main.typ"
REPORT_DATA_TYP = TEMPLATE_DIR / "report-data.typ"
AGENTIC_APP_SAMPLE = REPO_ROOT / "examples" / "agentic-app" / "sample-report"
SOURCE_JPEG = AGENTIC_APP_SAMPLE / "threat-system-architecture.jpg"
PLACEHOLDER_JPEG = AGENTIC_APP_SAMPLE / "threat-executive-architecture.jpg"

SOURCE_DATE_EPOCH = "1700000000"

# 25 covers the typical section-divider layout (header + title + leading content).
# TOC pages are filtered via the "Table of Contents" marker in
# _find_first_page_with_heading, so this window can be generous without risk.
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


@pytest.mark.slow
def test_executive_architecture_page_position(tmp_path):
    """Stage the placeholder JPEG, run the pipeline, and assert the Executive Threat
    Architecture page renders between Executive Summary and Attack Path Analysis."""
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
        # Stage the placeholder only if not already present — don't clobber a
        # previous test's leftover.
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

        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH

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

        # --root pins Typst to the repo root so it can resolve the relative
        # image path computed by extract-report-data.py (which walks up from
        # templates/tachi/security-report/ to examples/...).
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

        exec_summary_page = _find_first_page_with_heading(
            pages, "Executive Summary"
        )
        exec_architecture_page = _find_first_page_with_heading(
            pages, "Executive Threat Architecture"
        )
        attack_path_page = _find_first_page_with_heading(
            pages, "Attack Path Analysis"
        )

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


@pytest.mark.slow
def test_executive_architecture_skip_image_pdf_omits_page(tmp_path):
    """Run the pipeline without a ``threat-executive-architecture.jpg`` in place and
    assert the Executive Threat Architecture page is omitted from the rendered PDF."""
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

    # Stash any real Gemini output aside for the duration of the test so the
    # absent-branch contract stays covered even when the checked-in example
    # has a real ``threat-executive-architecture.jpg``. Restored in finally.
    jpeg_backup = None
    if PLACEHOLDER_JPEG.exists():
        jpeg_backup = tmp_path / "threat-executive-architecture.jpg.backup"
        shutil.move(str(PLACEHOLDER_JPEG), str(jpeg_backup))

    # Paths for intermediate artifacts in the pytest-managed tmp dir
    tmp_pdf = tmp_path / "security-report.pdf"
    tmp_txt = tmp_path / "security-report.txt"

    report_data_created = False
    try:
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH

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

        # --root pins Typst to the repo root so it can resolve the relative
        # image paths for the OTHER infographic images (funnel, baseball card,
        # system architecture) which DO exist in the sample.
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

        # Reuse _find_first_page_with_heading so the TOC-filtering logic stays
        # shared with the present-branch test; if either test drifts in what
        # counts as a heading match, both drift together.
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

        # Sanity-check the surrounding sections — if Executive Summary or
        # Attack Path Analysis are also missing, the page-omission assertion
        # above is a false positive (it would trivially pass on an empty PDF).
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
        # after Executive Summary with exactly a one-page gap. Absolute page
        # numbers can drift with content changes, so we assert the relative gap.
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
        # Restore the stashed real JPEG if we moved it aside so the committed
        # example is never left in a broken state.
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
