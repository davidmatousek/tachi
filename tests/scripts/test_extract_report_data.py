"""US-2 unit tests for the executive-architecture image detection in extract-report-data.py.

These tests exercise the Phase 4 (US-2) implementation of F-128. They invoke
`scripts/extract-report-data.py` as a subprocess via ``sys.executable`` and
assert against the generated ``report-data.typ`` content. Direct helper-function
access is exposed by the ``extract_report_data`` session-scoped fixture
declared in ``tests/conftest.py``; this file uses subprocess invocation because
the assertions target the final emitted Typst text rather than intermediate
Python state.

Note on the test-first gate (T017):
-----------------------------------
F-128 tasks T018/T019 add the `has-executive-architecture` and
`executive-architecture-image-path` Typst variables. At the time T016 authors
these tests, those lines do NOT yet exist in ``extract-report-data.py``. The
expected failure pattern is:

* ``test_has_executive_architecture_true_when_image_present``   — FAIL
* ``test_has_executive_architecture_false_when_image_absent``   — may pre-pass
  (the absence of any ``has-executive-architecture = false`` line is what the
  assertion actually checks for; see inline rationale below)
* ``test_has_executive_architecture_false_when_image_zero_size`` — FAIL
* ``test_executive_architecture_image_path_relative_to_template_dir`` — FAIL
* ``test_existing_image_flags_unchanged``                       — PASS
  (backward-compat baseline; must stay green before and after T018/T019)

The T017 gate runs ``make test`` (or ``pytest tests/scripts/test_extract_report_data.py -v``)
and records the expected-failure set. Once T018/T019 land, all 5 tests must
pass, including the parametrized ``test_existing_image_flags_unchanged``.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


# Repository root resolved from this file's location:
# tests/scripts/test_extract_report_data.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "report_data"
GOLDEN_EXISTING_FLAGS = FIXTURES_DIR / "golden_existing_image_flags.txt"
AGENTIC_APP_SAMPLE = REPO_ROOT / "examples" / "agentic-app" / "sample-report"


# -----------------------------------------------------------------------------
# Subprocess helper
# -----------------------------------------------------------------------------

def run_extract(target_dir, template_dir=None):
    """Run extract-report-data.py as a subprocess against a target folder.

    Args:
        target_dir: Path to the folder containing ``threats.md`` and optional
            image files. The script writes ``report-data.typ`` into a temp
            location; this helper returns the emitted content as a string.
        template_dir: Optional override for ``--template-dir``. Defaults to
            the real ``templates/tachi/security-report/`` directory so path
            resolution matches production behavior.

    Returns:
        Tuple ``(returncode, stdout, stderr, typst_content_or_None)``. The
        fourth element is ``None`` when the script fails to write output.
    """
    if template_dir is None:
        template_dir = TEMPLATE_DIR
    with tempfile.NamedTemporaryFile(suffix=".typ", delete=False) as f:
        output_path = f.name
    try:
        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--target-dir", str(target_dir),
            "--template-dir", str(template_dir),
            "--output", output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        content = None
        if result.returncode == 0 and os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except OSError:
                content = None
        return result.returncode, result.stdout, result.stderr, content
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass


# -----------------------------------------------------------------------------
# US-2 Tests
# -----------------------------------------------------------------------------

def test_has_executive_architecture_true_when_image_present():
    """Fixture folder with a non-zero threat-executive-architecture.jpg.

    Contract: ``report-data.typ`` must contain the exact line
    ``#let has-executive-architecture = true`` when the image file exists and
    has non-zero size. Pre-F-128 the line is absent entirely; this test
    therefore FAILS until T018/T019 ship.
    """
    returncode, _stdout, stderr, content = run_extract(FIXTURES_DIR / "image_present")
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"
    assert "#let has-executive-architecture = true" in content, (
        "Expected '#let has-executive-architecture = true' line in report-data.typ "
        "when threat-executive-architecture.jpg is present and non-zero."
    )


def test_has_executive_architecture_false_when_image_absent():
    """Fixture folder without the executive architecture image.

    Contract: when the image file is missing, the emitted Typst file must
    contain ``#let has-executive-architecture = false`` — i.e. the variable
    is still declared with a false value, not omitted. This asserts the
    variable is ALWAYS present (safe default), not that the absence of the
    image makes the line implicitly absent.

    This test will FAIL pre-F-128 because no ``has-executive-architecture``
    line exists at all — including the ``= false`` form required by the
    contract. It PASSES after T018/T019 ship the safe-default writer.
    """
    returncode, _stdout, stderr, content = run_extract(FIXTURES_DIR / "image_absent")
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"
    assert "#let has-executive-architecture = false" in content, (
        "Expected '#let has-executive-architecture = false' line (safe default) "
        "in report-data.typ when threat-executive-architecture.jpg is absent."
    )
    # Negative assertion: the true form must NOT appear
    assert "#let has-executive-architecture = true" not in content, (
        "Did not expect '#let has-executive-architecture = true' when image is absent."
    )


def test_has_executive_architecture_false_when_image_zero_size():
    """Fixture with an empty (zero-byte) threat-executive-architecture.jpg.

    Contract: a zero-byte file is treated as absent (matches the existing
    ``stat().st_size > 0`` convention in ``detect_images``). The emitted
    line must be ``#let has-executive-architecture = false``.
    """
    returncode, _stdout, stderr, content = run_extract(FIXTURES_DIR / "image_zero_size")
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"
    assert "#let has-executive-architecture = false" in content, (
        "Expected '#let has-executive-architecture = false' line when the "
        "image file exists but is zero bytes (treated as absent)."
    )
    assert "#let has-executive-architecture = true" not in content, (
        "Did not expect '#let has-executive-architecture = true' for a zero-byte image."
    )


def test_executive_architecture_image_path_relative_to_template_dir():
    """When the image is present, the emitted path must be relative (not absolute).

    Contract (``report-data-typst-contract.md``): the path is computed via
    ``os.path.relpath(target_dir, template_dir)``, following the same
    convention as the existing funnel/baseball/architecture paths. For the
    ``image_present`` fixture living under ``tests/scripts/fixtures/report_data/``,
    the relative path from ``templates/tachi/security-report/`` MUST begin
    with ``..`` (parent traversal) because the fixture directory is outside
    the template directory tree.

    Additional assertions:

    * The path must NOT start with ``/`` (no absolute paths).
    * The path must end with ``threat-executive-architecture.jpg``.
    * The line must be declared via ``#let executive-architecture-image-path =``.
    """
    returncode, _stdout, stderr, content = run_extract(FIXTURES_DIR / "image_present")
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    # Find the emitted executive-architecture-image-path line.
    path_lines = [
        line for line in content.splitlines()
        if line.startswith("#let executive-architecture-image-path")
    ]
    assert len(path_lines) == 1, (
        f"Expected exactly 1 '#let executive-architecture-image-path' line, "
        f"got {len(path_lines)}: {path_lines!r}"
    )
    path_line = path_lines[0]

    # Extract the quoted value.
    assert "\"" in path_line, f"Expected quoted path value in: {path_line!r}"
    first_quote = path_line.index("\"")
    last_quote = path_line.rindex("\"")
    assert last_quote > first_quote, f"Malformed quoted value: {path_line!r}"
    path_value = path_line[first_quote + 1:last_quote]

    assert path_value.endswith("threat-executive-architecture.jpg"), (
        f"Expected path to end with 'threat-executive-architecture.jpg', "
        f"got: {path_value!r}"
    )
    assert not path_value.startswith("/"), (
        f"Expected relative path, got absolute path: {path_value!r}"
    )
    assert ".." in path_value, (
        "Expected relative path to traverse up from template_dir (contain '..'), "
        f"got: {path_value!r}"
    )


@pytest.mark.parametrize(
    "expected_line",
    [
        "#let has-funnel-image = true",
        "#let has-baseball-image = true",
        "#let has-architecture-image = true",
        "#let has-maestro-stack-image = false",
        "#let has-maestro-heatmap-image = false",
    ],
)
def test_existing_image_flags_unchanged(expected_line):
    """Pre-existing image flag lines are byte-identical to the pre-F-128 golden.

    The golden file ``golden_existing_image_flags.txt`` was captured BEFORE
    the executive-architecture detection branch was added to
    ``extract-report-data.py`` by running the script against
    ``examples/agentic-app/sample-report/``. That folder has funnel, baseball,
    and architecture JPEGs present but no MAESTRO images, producing the 5
    canonical flag values used as the backward-compat baseline.

    This test re-runs the script against the same folder and asserts that
    each of the 5 ``#let has-*-image = ...`` lines appears byte-identically
    in the new output. A regression here indicates F-128 accidentally
    modified an existing image flag's emission format, variable name, or
    default value — all of which would break every downstream example.

    Unlike the other 4 tests, this one is expected to PASS at T017 (before
    T018/T019) and continue passing after T018/T019. It is a frozen
    backward-compatibility baseline.
    """
    # Load the golden file; it must exist with exactly 5 lines.
    assert GOLDEN_EXISTING_FLAGS.exists(), (
        f"Missing golden fixture: {GOLDEN_EXISTING_FLAGS}"
    )
    golden_lines = [
        line for line in GOLDEN_EXISTING_FLAGS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(golden_lines) == 5, (
        f"Expected exactly 5 lines in {GOLDEN_EXISTING_FLAGS.name}, "
        f"got {len(golden_lines)}"
    )
    # The parametrized expected_line must be in the golden file (sanity check
    # that the test and the golden agree).
    assert expected_line in golden_lines, (
        f"Test parameter {expected_line!r} is not in golden file. "
        f"Golden contents: {golden_lines!r}"
    )

    # Re-run the script against the canonical agentic-app sample-report folder.
    returncode, _stdout, stderr, content = run_extract(AGENTIC_APP_SAMPLE)
    assert returncode == 0, (
        f"Expected exit 0 for agentic-app sample-report, got {returncode}. "
        f"stderr: {stderr}"
    )
    assert content is not None, "Expected report-data.typ to be written"

    # Byte-identical line match.
    output_lines = content.splitlines()
    assert expected_line in output_lines, (
        f"Golden flag line drifted. Expected line {expected_line!r} "
        f"not found in generated report-data.typ. Backward compatibility regression."
    )
