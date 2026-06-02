"""Unit tests for extract-report-data.py.

Most tests invoke ``scripts/extract-report-data.py`` as a subprocess and assert
against the generated ``report-data.typ`` content. Subprocess invocation is used
when the assertions target the emitted Typst text rather than intermediate Python
state. A handful of tests (the MAESTRO layer-grouping regression guard) import the
script as a module to exercise ``parse_maestro_data`` directly against a synthetic
threats.md, which is both cleaner and more deterministic than rendering Typst.
"""

import importlib.util
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


def _load_extract_module():
    """Import the hyphenated ``extract-report-data.py`` as a module.

    The script filename is not a valid Python identifier (it contains hyphens),
    so it cannot be imported by name. ``scripts`` is placed on ``sys.path`` first
    so the script's own ``from tachi_parsers import ...`` line resolves, matching
    how the script is invoked as ``__main__``.
    """
    scripts_dir = str(REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("extract_report_data", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


# =============================================================================
# MAESTRO zero-finding-layer retention (Feature 098, FR-009a / T009)
# =============================================================================
#
# T003 removed the zero-finding FILTER from the maestro layer-grouping path in
# extract-report-data.py: ``findings_by_layer`` is now built from EVERY layer
# seeded by the "Risk by MAESTRO Layer" distribution table, regardless of
# whether that layer has any findings. A layer with 0 findings must survive as
# a group with an empty ``findings`` list so the Typst template's ``else``
# branch can render its "no findings this scan" state. This test is a genuine
# regression guard: if a ``if group["findings"]`` filter were reintroduced, the
# zero-finding L4 group would be dropped and the length-7 assertion would fail.


# A synthetic threats.md whose Section 6 distribution table names all 7 canonical
# MAESTRO layers, with L4 carrying 0 findings. There are deliberately NO Section
# 3/4 per-finding rows: every layer is therefore zero-finding at the per-finding
# level, so an old-style ``if group["findings"]`` filter would drop ALL seven
# groups (length 0) rather than retain them (length 7) — the strongest possible
# form of the guard. The heading uses the ``####`` form that
# ``parse_markdown_table`` keys on; ``L4``'s "Highest Severity" cell carries a
# sentence (matching the production "Analyzed — no findings this scan" idiom) to
# confirm the parser tolerates non-severity prose in that column.
_SYNTHETIC_THREATS_ALL_SEVEN_LAYERS = """## 6. Risk Summary

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---|---|---|
| L1 — Foundation Model | 2 | High |
| L2 — Data Operations | 1 | Medium |
| L3 — Agent Frameworks | 1 | High |
| L4 — Deployment Infrastructure | 0 | Analyzed — no findings this scan |
| L5 — Evaluation and Observability | 1 | Medium |
| L6 — Security and Compliance | 1 | High |
| L7 — Agent Ecosystem | 1 | Low |
"""


def test_maestro_zero_finding_layer_is_retained_not_dropped():
    """All 7 canonical layers survive grouping; a zero-finding layer keeps an empty list.

    Regression guard for the T003 filter removal (Feature 098, FR-009a). Drives
    ``parse_maestro_data`` directly with a synthetic threats.md that names all
    seven L-IDs (L4 = 0 findings) so the grouping path is exercised end-to-end
    without rendering Typst.

    Asserts:
      (a) ``maestro_findings_by_layer`` has length exactly 7 — proving no
          zero-finding layer was filtered out, and
      (b) the L4 group carries an empty ``findings`` list — so the Typst
          ``else``-branch ("no findings this scan") fires for it.

    If the dropped ``if group["findings"]`` filter were reinstated, every group
    would be removed (no per-finding rows exist) and assertion (a) would fail.
    """
    extract = _load_extract_module()
    result = extract.parse_maestro_data(_SYNTHETIC_THREATS_ALL_SEVEN_LAYERS)

    groups = result["maestro_findings_by_layer"]
    layer_ids = [g["layer_id"] for g in groups]

    # (a) No zero-finding layer was dropped — all 7 canonical layers present.
    assert len(groups) == 7, (
        "Expected maestro_findings_by_layer to retain all 7 canonical layers "
        "(the T003 zero-finding filter was removed), got "
        f"{len(groups)}: {layer_ids!r}. A length < 7 here means a "
        "'if group[\"findings\"]' filter was reintroduced — regression."
    )
    assert layer_ids == extract.MAESTRO_LAYERS, (
        "Expected the 7 groups in canonical L1-L7 order matching "
        f"MAESTRO_LAYERS={extract.MAESTRO_LAYERS!r}, got {layer_ids!r}."
    )

    # (b) The zero-finding layer (L4) is present with an empty findings list.
    l4_groups = [g for g in groups if g["layer_id"] == "L4"]
    assert len(l4_groups) == 1, (
        f"Expected exactly one L4 group, got {len(l4_groups)}: {layer_ids!r}."
    )
    assert l4_groups[0]["findings"] == [], (
        "Expected the zero-finding L4 layer to carry an empty 'findings' list "
        "(so the Typst else-branch renders 'no findings this scan'), got "
        f"{l4_groups[0]['findings']!r}."
    )
