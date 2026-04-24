"""Unit tests for executive-architecture image detection in extract-report-data.py.

Invokes ``scripts/extract-report-data.py`` as a subprocess and asserts against the
generated ``report-data.typ`` content. Subprocess invocation is used instead of
direct module access because the assertions target the emitted Typst text rather
than intermediate Python state.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "report_data"
GOLDEN_EXISTING_FLAGS = FIXTURES_DIR / "golden_existing_image_flags.txt"
AGENTIC_APP_SAMPLE = REPO_ROOT / "examples" / "agentic-app" / "sample-report"


def run_extract(target_dir, template_dir=None):
    """Run extract-report-data.py and return (returncode, stdout, stderr, typst_content)."""
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


def test_has_executive_architecture_true_when_image_present():
    """Emit ``#let has-executive-architecture = true`` when the image is present and non-zero."""
    returncode, _stdout, stderr, content = run_extract(FIXTURES_DIR / "image_present")
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"
    assert "#let has-executive-architecture = true" in content, (
        "Expected '#let has-executive-architecture = true' line in report-data.typ "
        "when threat-executive-architecture.jpg is present and non-zero."
    )


def test_has_executive_architecture_false_when_image_absent():
    """When the image is missing, the variable must still be declared ``= false`` (safe default)."""
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
    """A zero-byte image file is treated as absent (matching the ``st_size > 0`` convention)."""
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
    """The emitted ``executive-architecture-image-path`` must be relative, not absolute.

    Path is computed via ``os.path.relpath(target_dir, template_dir)`` matching the
    existing funnel/baseball/architecture convention. The fixture lives outside the
    template directory tree so the relative path must begin with ``..``.
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


@pytest.fixture(scope="module")
def agentic_app_report_typst():
    """Run extract-report-data.py once against the agentic-app sample and cache the output."""
    returncode, _stdout, stderr, content = run_extract(AGENTIC_APP_SAMPLE)
    assert returncode == 0, (
        f"Expected exit 0 for agentic-app sample-report, got {returncode}. "
        f"stderr: {stderr}"
    )
    assert content is not None, "Expected report-data.typ to be written"
    return content


@pytest.fixture(scope="module")
def golden_image_flag_lines():
    assert GOLDEN_EXISTING_FLAGS.exists(), (
        f"Missing golden fixture: {GOLDEN_EXISTING_FLAGS}"
    )
    lines = [
        line for line in GOLDEN_EXISTING_FLAGS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == 5, (
        f"Expected exactly 5 lines in {GOLDEN_EXISTING_FLAGS.name}, got {len(lines)}"
    )
    return lines


@pytest.mark.parametrize(
    "expected_line",
    [
        "#let has-funnel-image = true",
        "#let has-baseball-image = true",
        "#let has-architecture-image = true",
        "#let has-maestro-stack-image = true",
        "#let has-maestro-heatmap-image = true",
    ],
)
def test_existing_image_flags_unchanged(
    expected_line, agentic_app_report_typst, golden_image_flag_lines
):
    """Pre-existing image flag lines stay byte-identical to the frozen golden baseline."""
    assert expected_line in golden_image_flag_lines, (
        f"Test parameter {expected_line!r} is not in golden file. "
        f"Golden contents: {golden_image_flag_lines!r}"
    )

    output_lines = agentic_app_report_typst.splitlines()
    assert expected_line in output_lines, (
        f"Golden flag line drifted. Expected line {expected_line!r} "
        f"not found in generated report-data.typ. Backward compatibility regression."
    )
