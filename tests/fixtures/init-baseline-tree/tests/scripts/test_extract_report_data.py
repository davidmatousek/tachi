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

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff\xe0\x00\x10JFIF"


def _write_minimal_png(path: Path) -> None:
    """Write a byte sequence that begins with the PNG magic header.

    Only the magic bytes matter to ``detect_images`` (it reads the first 8
    bytes). The trailing payload is arbitrary filler so ``st_size > 0``.
    """
    path.write_bytes(PNG_MAGIC + b"\x00" * 16)


def _write_minimal_jpeg(path: Path) -> None:
    path.write_bytes(JPEG_MAGIC + b"\x00" * 16)


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


# =============================================================================
# Byte-probe image detection (Issue #215 regression coverage)
# =============================================================================


def _build_byte_probe_fixture(tmp_path: Path) -> Path:
    """Set up a minimal target dir: copy threats.md from image_present fixture."""
    fixture = tmp_path / "target"
    fixture.mkdir()
    (fixture / "threats.md").write_bytes(
        (FIXTURES_DIR / "image_present" / "threats.md").read_bytes()
    )
    return fixture


def test_mislabeled_jpg_with_png_bytes_emits_png_path_and_writes_sibling(tmp_path):
    """A `.jpg` file whose bytes are PNG must produce a corrected `.png` sibling.

    Reproduces the production failure mode: assessment directories generated
    against the `gemini-2.5-flash-image` fallback model contain `.jpg` files
    with PNG bytes. Typst rejects mismatched bytes/extension. The extractor
    must (a) detect the mismatch via magic-byte probe, (b) write a correctly
    named sibling, (c) emit the corrected `.png` path in `report-data.typ`.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    mislabeled = fixture / "threat-executive-architecture.jpg"
    _write_minimal_png(mislabeled)

    returncode, _stdout, stderr, content = run_extract(fixture)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    sibling = fixture / "threat-executive-architecture.png"
    assert sibling.exists(), (
        "Expected a `.png` sibling to be written next to the mislabeled `.jpg`."
    )
    assert sibling.read_bytes().startswith(PNG_MAGIC), (
        "Sibling must contain the original PNG bytes (not be empty/corrupt)."
    )

    path_lines = [
        line for line in content.splitlines()
        if line.startswith("#let executive-architecture-image-path")
    ]
    assert len(path_lines) == 1, f"Expected one path line, got: {path_lines!r}"
    assert path_lines[0].rstrip().endswith('threat-executive-architecture.png"'), (
        f"Expected emitted path to be the `.png` sibling, got: {path_lines[0]!r}"
    )

    assert "Image format mismatch" in stderr, (
        "Expected a stderr note announcing the corrected sibling write."
    )
    assert "PNG bytes" in stderr, (
        "Expected the format-mismatch note to identify the actual format."
    )


def test_mixed_extensions_prefers_self_consistent_png_over_stale_jpg(tmp_path):
    """When both `.jpg` (PNG bytes, stale) and `.png` (PNG bytes, fresh) exist,
    pick the `.png` whose extension matches its bytes — never the stale `.jpg`.

    Models the cross-version re-run case: a previous fallback-model run
    produced the `.jpg`; a fresh run produced the `.png`. The `.jpg`-first
    preference of the old code would silently pick the stale file.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    stale = fixture / "threat-executive-architecture.jpg"
    fresh = fixture / "threat-executive-architecture.png"
    _write_minimal_png(stale)
    _write_minimal_png(fresh)

    returncode, _stdout, stderr, content = run_extract(fixture)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    path_lines = [
        line for line in content.splitlines()
        if line.startswith("#let executive-architecture-image-path")
    ]
    assert len(path_lines) == 1, f"Expected one path line, got: {path_lines!r}"
    assert path_lines[0].rstrip().endswith('threat-executive-architecture.png"'), (
        f"Expected the `.png` (self-consistent) to be selected, got: {path_lines[0]!r}"
    )

    assert "Image format mismatch" not in stderr, (
        "Best-match path must not trip the recovery branch — no warning expected."
    )


def test_clean_jpeg_emits_jpg_path_without_warning(tmp_path):
    """Backward compatibility: a true JPEG `.jpg` file must keep emitting the
    `.jpg` path with no recovery activity. Guards against false-positive
    warnings during normal operation.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    clean = fixture / "threat-executive-architecture.jpg"
    _write_minimal_jpeg(clean)

    returncode, _stdout, stderr, content = run_extract(fixture)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    path_lines = [
        line for line in content.splitlines()
        if line.startswith("#let executive-architecture-image-path")
    ]
    assert len(path_lines) == 1, f"Expected one path line, got: {path_lines!r}"
    assert path_lines[0].rstrip().endswith('threat-executive-architecture.jpg"'), (
        f"Expected `.jpg` to be preserved for clean JPEG input, got: {path_lines[0]!r}"
    )
    assert "Image format mismatch" not in stderr, (
        "Clean JPEG must not emit the format-mismatch warning."
    )
    assert not (fixture / "threat-executive-architecture.png").exists(), (
        "Clean JPEG must not trigger sibling creation."
    )
