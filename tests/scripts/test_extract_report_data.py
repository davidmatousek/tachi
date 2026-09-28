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
import re
import shutil
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

# Feature 373 US-3a (K9/K10/K12/K13.1) extractor-level regression fixtures.
# See that directory's README.md for hand-computed expected values; the
# pure tachi_parsers.py-level pins for these same fixtures live in
# test_tachi_parsers.py (tasks.md T016) -- the tests below instead exercise
# extract-report-data.py's own wiring (parse_maestro_data, the CLI's
# delta_counts/report-data.typ call sites, and the K13.1 recommendation
# resolution across its three consumers: the finding card, the remediation
# roadmap, and the attack-path remediation).
FIDELITY_FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373"

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


def run_extract(target_dir, template_dir=None, extra_args=None):
    """Run extract-report-data.py and return (returncode, stdout, stderr, typst_content).

    ``extra_args`` is an optional list of additional CLI arguments appended to
    argv (e.g. ``["--cleanup-mislabeled-images"]``); existing call sites are
    unaffected since the parameter defaults to ``None`` (contracts/cli-contract.md §4).
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
        if extra_args:
            cmd.extend(extra_args)
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
def agentic_app_report_typst(tmp_path_factory):
    """Run extract-report-data.py once against a copy of the agentic-app sample and cache the output.

    Skipped when mmdc is absent (PD-8): the agentic-app sample-report carries
    attack trees and attack chains, so extract-report-data.py invokes mmdc to
    render them to PNG. Runs against a ``tmp_path_factory`` copy of the whole
    sample-report directory, never the tracked example itself, so a local
    run never re-renders the tracked attack-tree/attack-chain PNGs (#365).
    """
    if shutil.which("mmdc") is None:
        pytest.skip(
            "mmdc (@mermaid-js/mermaid-cli) not on PATH; required to render "
            "agentic-app sample-report's attack trees/chains"
        )
    target_dir = tmp_path_factory.mktemp("agentic_app_sample_report")
    shutil.copytree(AGENTIC_APP_SAMPLE, target_dir, dirs_exist_ok=True)
    returncode, _stdout, stderr, content = run_extract(target_dir)
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
# Opt-in mislabeled-image cleanup (Issue #217 / Feature 217)
# =============================================================================
#
# Nine cases exercise the --cleanup-mislabeled-images double gate (flag AND a
# byte-identical, correctly-labeled counterpart) across both wiring moments —
# Moment A (pre-existing pairs) and Moment B (recovery write). Seven run
# through the CLI subprocess path via run_extract(extra_args=[...]); the two
# fault-injection cases (AC-1f, FR-005) run in-process via _load_extract_module()
# because run_extract crosses a subprocess boundary that monkeypatch cannot.

CLEANUP_FLAG = ["--cleanup-mislabeled-images"]


def _stderr_deletion_lines(stderr: str) -> list:
    """Return stderr lines that report a completed deletion (contain "delet")."""
    return [line for line in stderr.splitlines() if "delet" in line.lower()]


def test_cleanup_flag_deletes_mislabeled_jpg_with_byte_identical_png(tmp_path):
    """AC-1a: flagged run deletes the mislabeled .jpg once a byte-identical,
    correctly-labeled .png counterpart exists; exactly one deletion record.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    mislabeled = fixture / "threat-executive-architecture.jpg"
    counterpart = fixture / "threat-executive-architecture.png"
    _write_minimal_png(mislabeled)
    _write_minimal_png(counterpart)  # identical fixed payload -> byte-identical

    returncode, _stdout, stderr, content = run_extract(fixture, extra_args=CLEANUP_FLAG)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert not mislabeled.exists(), "Mislabeled .jpg must be deleted under the double gate."
    assert counterpart.exists(), "Byte-identical .png counterpart must survive."

    path_lines = [
        line for line in content.splitlines()
        if line.startswith("#let executive-architecture-image-path")
    ]
    assert len(path_lines) == 1, f"Expected one path line, got: {path_lines!r}"
    assert path_lines[0].rstrip().endswith('threat-executive-architecture.png"'), (
        f"Expected emitted path to be the .png survivor, got: {path_lines[0]!r}"
    )

    deletion_lines = _stderr_deletion_lines(stderr)
    assert len(deletion_lines) == 1, (
        f"Expected exactly one deletion record, got {len(deletion_lines)}: {deletion_lines!r}"
    )
    assert mislabeled.name in deletion_lines[0], (
        f"Deletion record must name the removed path: {deletion_lines[0]!r}"
    )
    assert counterpart.name in deletion_lines[0], (
        f"Deletion record must name the retained survivor path: {deletion_lines[0]!r}"
    )


def test_no_flag_run_stays_byte_identical(tmp_path):
    """AC-1b (regression pin): without the flag, a mislabeled/counterpart pair
    is left untouched and no cleanup output is emitted. Exercises only
    pre-existing (#215) behavior, so this case passes pre-implementation.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    mislabeled = fixture / "threat-executive-architecture.jpg"
    counterpart = fixture / "threat-executive-architecture.png"
    _write_minimal_png(mislabeled)
    _write_minimal_png(counterpart)

    returncode, _stdout, stderr, content = run_extract(fixture)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert mislabeled.exists(), "No-flag run must never delete the mislabeled .jpg."
    assert counterpart.exists(), "No-flag run must never delete the .png counterpart."
    assert not _stderr_deletion_lines(stderr), (
        f"No-flag run must emit zero cleanup lines, got stderr: {stderr!r}"
    )

    path_lines = [
        line for line in content.splitlines()
        if line.startswith("#let executive-architecture-image-path")
    ]
    assert len(path_lines) == 1
    assert path_lines[0].rstrip().endswith('threat-executive-architecture.png"'), (
        "Selection behavior (self-consistent .png over stale-labeled .jpg) must be "
        f"unaffected by the flag's absence, got: {path_lines[0]!r}"
    )


def test_cleanup_flag_recovery_write_then_verify_then_delete(tmp_path):
    """AC-1c: no sibling exists yet — the corrected sibling is written first,
    verified byte-identical, and only then is the mislabeled original deleted.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    mislabeled = fixture / "threat-executive-architecture.jpg"
    sibling = fixture / "threat-executive-architecture.png"
    _write_minimal_png(mislabeled)
    assert not sibling.exists(), "Precondition: no sibling yet."

    returncode, _stdout, stderr, content = run_extract(fixture, extra_args=CLEANUP_FLAG)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert sibling.exists(), "Corrected sibling must be written."
    assert sibling.read_bytes().startswith(PNG_MAGIC), "Sibling must carry the PNG bytes."
    assert not mislabeled.exists(), "Original .jpg must be deleted after verified write."

    # Order provable via record content: the recovery-write note precedes the
    # deletion record in stderr (write -> verify -> delete).
    recovery_idx = stderr.find("Image format mismatch")
    deletion_lines = _stderr_deletion_lines(stderr)
    assert recovery_idx != -1, "Expected the recovery-write note in stderr."
    assert len(deletion_lines) == 1, (
        f"Expected exactly one deletion record, got {len(deletion_lines)}: {deletion_lines!r}"
    )
    deletion_idx = stderr.find(deletion_lines[0])
    assert recovery_idx < deletion_idx, (
        "Recovery write must be logged before the deletion record (write-verify-delete order)."
    )


def test_cleanup_flag_non_identical_pair_untouched(tmp_path):
    """AC-1d: a mislabeled .jpg and a self-consistent .png that are NOT
    byte-identical must never be deleted — never guess which is authoritative.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    mislabeled = fixture / "threat-executive-architecture.jpg"
    counterpart = fixture / "threat-executive-architecture.png"
    _write_minimal_png(mislabeled)
    counterpart.write_bytes(PNG_MAGIC + b"\x01" * 16)  # valid PNG, different bytes

    returncode, _stdout, stderr, content = run_extract(fixture, extra_args=CLEANUP_FLAG)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert mislabeled.exists(), "Non-identical mislabeled .jpg must be preserved."
    assert counterpart.exists(), "Non-identical .png counterpart must be preserved."
    assert not _stderr_deletion_lines(stderr), (
        f"No deletion record expected for a non-identical pair, got stderr: {stderr!r}"
    )


def test_cleanup_flag_all_correct_directory_is_a_no_op(tmp_path):
    """AC-1e: a directory with only a correctly-labeled image is a no-op —
    zero deletions, zero cleanup stderr.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    clean = fixture / "threat-executive-architecture.jpg"
    _write_minimal_jpeg(clean)

    returncode, _stdout, stderr, content = run_extract(fixture, extra_args=CLEANUP_FLAG)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert clean.exists(), "Correctly-labeled image must be untouched."
    assert not _stderr_deletion_lines(stderr), (
        f"All-correct directory must emit zero cleanup lines, got stderr: {stderr!r}"
    )
    assert "Image format mismatch" not in stderr, (
        "All-correct directory must not trigger the recovery branch."
    )


def test_cleanup_flag_truncated_recovery_copy_skips_delete(tmp_path, monkeypatch, capsys):
    """AC-1f: a truncated/failed sibling copy in the recovery path must NOT
    delete the mislabeled original, and the run must still complete (the
    exit-0 equivalent for an in-process call — no exception raised). Byte-
    identity verification doubles as copy-success verification. Runs
    in-process: run_extract crosses a subprocess boundary that a monkeypatched
    shutil.copyfile cannot.
    """
    extract = _load_extract_module()

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    mislabeled = target_dir / "threat-executive-architecture.jpg"
    _write_minimal_png(mislabeled)

    def _truncated_copyfile(src, dst):
        Path(dst).write_bytes(Path(src).read_bytes()[:4])  # short write, not byte-identical

    monkeypatch.setattr(extract.shutil, "copyfile", _truncated_copyfile)

    images = extract.detect_images(target_dir, template_dir, cleanup=True)  # must not raise

    assert mislabeled.exists(), "Mislabeled original must be preserved when the copy is truncated."
    assert images["executive_architecture_image_path"], (
        "detect_images must still complete and report a chosen path (exit-0 equivalent)."
    )

    stderr = capsys.readouterr().err
    assert "Image format mismatch" in stderr, (
        "Expected the pre-existing recovery-write note in stderr."
    )
    assert not _stderr_deletion_lines(stderr), (
        f"Truncated copy must never emit a deletion record, got stderr: {stderr!r}"
    )


def test_cleanup_flag_cross_swapped_pair_untouched(tmp_path):
    """AC-1g: a cross-swapped pair (.jpg holds PNG bytes AND .png holds JPEG
    bytes) must never be deleted — recovery-path deletion fires only when the
    corrected sibling did NOT pre-exist the copy.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    jpg_path = fixture / "threat-executive-architecture.jpg"
    png_path = fixture / "threat-executive-architecture.png"
    _write_minimal_png(jpg_path)    # .jpg holds PNG bytes
    _write_minimal_jpeg(png_path)   # .png holds JPEG bytes

    returncode, _stdout, stderr, content = run_extract(fixture, extra_args=CLEANUP_FLAG)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert jpg_path.exists(), "Cross-swapped .jpg must be preserved (no deletion)."
    assert png_path.exists(), "Cross-swapped .png must be preserved (no deletion)."
    assert not _stderr_deletion_lines(stderr), (
        f"Cross-swap must never emit a deletion record, got stderr: {stderr!r}"
    )


def test_cleanup_flag_legitimate_mixed_pair_untouched(tmp_path):
    """AC-1h: a self-consistent .jpg and .png of different legitimate images
    must never be touched — the predicate keys on mislabeled-ness, not
    sibling-existence.
    """
    fixture = _build_byte_probe_fixture(tmp_path)
    jpg_path = fixture / "threat-executive-architecture.jpg"
    png_path = fixture / "threat-executive-architecture.png"
    _write_minimal_jpeg(jpg_path)   # self-consistent
    _write_minimal_png(png_path)    # self-consistent, different legitimate image

    returncode, _stdout, stderr, content = run_extract(fixture, extra_args=CLEANUP_FLAG)
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert content is not None, "Expected report-data.typ to be written"

    assert jpg_path.exists(), "Legitimate self-consistent .jpg must be preserved."
    assert png_path.exists(), "Legitimate self-consistent .png must be preserved."
    assert not _stderr_deletion_lines(stderr), (
        f"Legitimate mixed pair must never emit a deletion record, got stderr: {stderr!r}"
    )
    assert "Image format mismatch" not in stderr, (
        "Legitimate mixed pair must not trip the recovery branch."
    )


def test_cleanup_deletion_failure_is_best_effort(tmp_path, monkeypatch, capsys):
    """FR-005/INV-3 (Architect MED-2): a per-file deletion failure (OSError
    from Path.unlink) is logged to stderr and MUST NOT fail extraction — the
    file persists, exactly one failure line is emitted, and detect_images
    still returns normally with unchanged output. Runs in-process: run_extract
    crosses a subprocess boundary that a monkeypatched Path.unlink cannot.
    """
    extract = _load_extract_module()

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    mislabeled = target_dir / "threat-executive-architecture.jpg"
    counterpart = target_dir / "threat-executive-architecture.png"
    _write_minimal_png(mislabeled)
    _write_minimal_png(counterpart)  # byte-identical: gate 2 would otherwise pass

    def _raise_permission_error(self, *args, **kwargs):
        raise OSError("Permission denied (simulated)")

    monkeypatch.setattr(Path, "unlink", _raise_permission_error)

    images = extract.detect_images(target_dir, template_dir, cleanup=True)  # must not raise

    assert mislabeled.exists(), "File must persist when deletion raises OSError (best-effort)."
    assert counterpart.exists(), "Survivor counterpart must remain untouched."
    assert images["executive_architecture_image_path"].endswith(
        "threat-executive-architecture.png"
    ), "Emitted output must be unchanged by the deletion failure."

    stderr = capsys.readouterr().err
    failure_lines = [
        line for line in stderr.splitlines()
        if mislabeled.name in line and "Permission denied (simulated)" in line
    ]
    assert len(failure_lines) == 1, (
        f"Expected exactly one failure line naming the path and OS error, "
        f"got {len(failure_lines)}: {failure_lines!r}. Full stderr: {stderr!r}"
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


# --- Feature 311: coverage_state threading (T009/T010, ADR-047 HIGH-A) ----------
#
# Synthetic threats.md mirroring the ``examples/microservices`` Section-6 state
# map AFTER the Phase-D populator regen (data-model.md fixture table): the four
# unmapped zero-finding layers (L1/L3/L5/L6) carry the NEW n/a token, the mapped
# zero-finding layer (L7) carries the UNCHANGED clean token, and the two
# finding-bearing layers (L2/L4) carry a severity label. The two tokens are
# byte-identical to the Phase-A contract (U+2014 em-dash, no trailing period).
# Driving ``parse_maestro_data`` against this string proves T009's wiring emits
# the right ``coverage_state`` enum on the GROUP records (the only structure
# main.typ passes to the MAESTRO page) without invoking the populator or
# rendering Typst — same harness style as the zero-finding-retention guard above.
_SYNTHETIC_THREATS_MICROSERVICES_STATE_MAP = """## 6. Risk Summary

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---|---|---|
| L1 — Foundation Model | 0 | Not applicable — no components map to this layer |
| L2 — Data Operations | 8 | Critical |
| L3 — Agent Framework | 0 | Not applicable — no components map to this layer |
| L4 — Deployment Infrastructure | 14 | Critical |
| L5 — Evaluation and Observability | 0 | Not applicable — no components map to this layer |
| L6 — Security and Compliance | 0 | Not applicable — no components map to this layer |
| L7 — Agent Ecosystem | 0 | Analyzed — no findings this scan |
"""

_MICROSERVICES_THREATS = REPO_ROOT / "examples" / "microservices" / "threats.md"

# Expected per-layer coverage_state for the microservices state map (the CI fixture
# anchor). Matches data-model.md "Fixture state map" and the cross-surface contract.
_MICROSERVICES_EXPECTED_STATE = {
    "L1": "not_applicable",
    "L2": "findings",
    "L3": "not_applicable",
    "L4": "findings",
    "L5": "not_applicable",
    "L6": "not_applicable",
    "L7": "clean",
}


def _group_state(groups, layer_id):
    """Return the coverage_state of the single group record with ``layer_id``."""
    matches = [g for g in groups if g["layer_id"] == layer_id]
    assert len(matches) == 1, (
        f"Expected exactly one {layer_id} group, got {len(matches)}: "
        f"{[g['layer_id'] for g in groups]!r}."
    )
    return matches[0].get("coverage_state")


def test_maestro_coverage_state_on_group_records_microservices_state_map():
    """coverage_state rides the maestro_findings_by_layer GROUP records (HIGH-A).

    The MAESTRO PDF page reads ONLY ``maestro_findings_by_layer`` (the grouped
    structure main.typ passes), so the clean-vs-n/a-vs-findings enum MUST live on
    each group record. Drives ``parse_maestro_data`` against the microservices
    state map (post-regen tokens) and asserts the group record for every canonical
    layer carries the expected ``coverage_state``: ``clean`` for L7,
    ``not_applicable`` for L1/L3/L5/L6, ``findings`` for L2/L4 (data-model.md
    fixture table + cross-surface-consistency contract).
    """
    extract = _load_extract_module()
    result = extract.parse_maestro_data(_SYNTHETIC_THREATS_MICROSERVICES_STATE_MAP)

    groups = result["maestro_findings_by_layer"]
    actual = {lid: _group_state(groups, lid) for lid in _MICROSERVICES_EXPECTED_STATE}

    assert actual == _MICROSERVICES_EXPECTED_STATE, (
        "coverage_state on the maestro_findings_by_layer GROUP records did not "
        "match the microservices state map.\n"
        f"  expected: {_MICROSERVICES_EXPECTED_STATE!r}\n"
        f"  actual:   {actual!r}\n"
        "The PDF MAESTRO page reads only the grouped structure (HIGH-A), so the "
        "enum must be set on the group record at the pre-build site, sourced from "
        "the matching parsed_layers row's classify_maestro_coverage_state token."
    )

    # The same enum must also ride maestro_layer_distribution (so the distribution
    # block in report-data.typ carries it too).
    dist = {l["layer_id"]: l.get("coverage_state") for l in result["maestro_layer_distribution"]}
    assert dist == _MICROSERVICES_EXPECTED_STATE, (
        "coverage_state on maestro_layer_distribution did not match the state map: "
        f"{dist!r}"
    )


def test_maestro_most_exposed_layer_never_a_zero_finding_layer():
    """compute_most_exposed_layer never selects a clean/n/a (zero-finding) layer (FR-012).

    With the microservices state map (only L2/L4 finding-bearing), the most-exposed
    layer MUST resolve to L2 or L4 and never to a zero-finding layer — guaranteed by
    the ordinal-0 tie-break left intact in parse_maestro_data (the clean and n/a
    tokens both miss _SEVERITY_ORDINAL → 0; no token was added to the ordinal map).
    """
    extract = _load_extract_module()
    result = extract.parse_maestro_data(_SYNTHETIC_THREATS_MICROSERVICES_STATE_MAP)

    most_exposed = result["most_exposed_layer"]
    assert most_exposed.startswith(("L2", "L4")), (
        "Expected the most-exposed layer to be a finding-bearing layer (L2 or L4), "
        f"got {most_exposed!r}. A zero-finding (clean/n/a) layer must never win the "
        "tie-break (FR-012 ordinal-0)."
    )
    # Belt-and-suspenders: both zero-finding tokens resolve to ordinal 0.
    assert extract._SEVERITY_ORDINAL.get("Not applicable — no components map to this layer", 0) == 0
    assert extract._SEVERITY_ORDINAL.get("Analyzed — no findings this scan", 0) == 0


def test_maestro_coverage_state_live_on_committed_microservices_example():
    """The committed examples/microservices threats.md drives coverage_state end-to-end.

    Proves the T009 wiring is live against the real CI fixture (not just a synthetic
    string): every group record carries a ``coverage_state`` field, the finding-bearing
    layers classify to ``findings``, the mapped zero-finding layer (L7) to ``clean``,
    and the most-exposed layer is never a zero-finding layer.

    NOTE ON SEQUENCING: the committed source still carries the *clean* token for the
    unmapped zero-finding layers (L1/L3/L5/L6) — the Phase-D populator regen (T018)
    flips those to the n/a token, after which they classify to ``not_applicable``.
    Until then they correctly classify to ``clean`` (the classifier reads only the
    carried token). This test therefore asserts the live wiring + the stable L7/L2/L4
    states and the ordinal-0 invariant; the L1/L3/L5/L6 → not_applicable transition is
    covered against the post-regen state map by
    ``test_maestro_coverage_state_on_group_records_microservices_state_map``.
    """
    extract = _load_extract_module()
    content = _MICROSERVICES_THREATS.read_text(encoding="utf-8")
    result = extract.parse_maestro_data(content)

    groups = result["maestro_findings_by_layer"]
    canonical = [g for g in groups if g["layer_id"] in extract.MAESTRO_LAYERS]

    # Every canonical group record carries the coverage_state field (HIGH-A wiring live).
    for g in canonical:
        assert "coverage_state" in g, (
            f"Group record for {g['layer_id']!r} is missing coverage_state — the "
            "HIGH-A wiring did not reach the grouped structure main.typ passes."
        )
        assert g["coverage_state"] in ("findings", "clean", "not_applicable"), (
            f"Unexpected coverage_state {g['coverage_state']!r} on {g['layer_id']!r}."
        )

    # Stable states on the committed source: L2/L4 finding-bearing, L7 clean.
    assert _group_state(groups, "L2") == "findings"
    assert _group_state(groups, "L4") == "findings"
    assert _group_state(groups, "L7") == "clean"

    # FR-012: most-exposed is a finding-bearing layer, never a zero-finding one.
    assert result["most_exposed_layer"].startswith(("L2", "L4")), (
        "Most-exposed layer on the committed microservices example must be a "
        f"finding-bearing layer, got {result['most_exposed_layer']!r}."
    )


# =============================================================================
# Feature 373 US-3a: K9, K10 extractor-level wiring (tasks.md T019).
# Fixtures: tests/scripts/fixtures/fidelity_373/ (see its README.md).
# =============================================================================


def _read_fidelity_fixture(subdir: str, filename: str) -> str:
    return (FIDELITY_FIXTURES_DIR / subdir / filename).read_text(encoding="utf-8")


def test_k9_shortform_bands_wire_through_parse_compensating_controls_md():
    # US-3a #1-#2 (K9/FR-K9.1-K9.2): confirms extract-report-data.py's own
    # module-level import binding of parse_compensating_controls_md (not
    # just tachi_parsers's own namespace, already pinned in
    # test_tachi_parsers.py) resolves the short-form headers plus an empty
    # Critical band and an empty last band before Summary Statistics.
    extract = _load_extract_module()
    cc_content = _read_fidelity_fixture("controls_bands_shortform", "compensating-controls.md")
    data = extract.parse_compensating_controls_md(cc_content)
    assert data["severity"] == {
        "critical": 0, "high": 1, "medium": 1, "low": 0, "note": 0, "total": 2,
    }
    assert [f["id"] for f in data["findings"]] == ["T-1", "T-2"]


def test_k10_h3_heading_equals_h4_form():
    # US-3a #4 (K10/FR-K10.1): a "###" heading and its "####" twin must
    # produce byte-for-byte identical parse_maestro_data results -- not
    # merely "parses without error" (already pinned per-fixture in
    # test_tachi_parsers.py).
    extract = _load_extract_module()
    h3_content = _read_fidelity_fixture("maestro_heading_h3", "threats.md")
    assert "### Risk by MAESTRO Layer" in h3_content
    h4_content = h3_content.replace("### Risk by MAESTRO Layer", "#### Risk by MAESTRO Layer", 1)
    result_h3 = extract.parse_maestro_data(h3_content)
    result_h4 = extract.parse_maestro_data(h4_content)
    assert result_h3 == result_h4
    assert result_h3["has_maestro_data"] is True
    assert result_h3["most_exposed_layer"] == "L1 — Foundation Model"


# =============================================================================
# Feature 373 US-3a: K12 extractor-level wiring (tasks.md T019).
# =============================================================================

_DELTA_COUNT_RE = re.compile(r"#let delta-(new|unchanged|updated|resolved)-count = (\d+)")


def _delta_counts_from_typ(content: str) -> dict:
    return {name: int(n) for name, n in _DELTA_COUNT_RE.findall(content)}


def test_k12_baseline_4c_exact_delta_counts_via_cli():
    # US-3a #5 (K12/FR-K12.1-K12.2): the 4c baseline's bracketed-status
    # variety (bare NEW, [NEW], **[NEW]**, `[NEW]`) plus one placeholder
    # resolved row, wired through the CLI end to end into report-data.typ.
    returncode, _stdout, stderr, content = run_extract(FIDELITY_FIXTURES_DIR / "baseline_resolved_4c")
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert _delta_counts_from_typ(content) == {
        "new": 4, "unchanged": 1, "updated": 1, "resolved": 2,
    }


def test_k12_baseline_4b_legacy_matches_4c_resolved_count_via_cli():
    # US-3a #6: the legacy "## 4b." heading yields the same resolved count
    # as its "## 4c." twin, end to end.
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "baseline_resolved_4b_legacy"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert _delta_counts_from_typ(content)["resolved"] == 2


def test_k12_non_baseline_no_status_column_no_warning_via_cli():
    # US-3a #7 (second half): a non-baseline run whose Section 7 has no
    # Status column must not warn, and every count stays 0.
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "non_baseline_no_status_column"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert _delta_counts_from_typ(content) == {
        "new": 0, "unchanged": 0, "updated": 0, "resolved": 0,
    }
    assert "Section 7" not in stderr


def test_k12_id_mismatch_absolute_tallies_and_one_warning_via_cli():
    # US-3a #7 (first half); architect F1/NM-1: both surfaces must report
    # the Section 7 tallies as absolute values (the normalized map's own
    # counts, not restricted to the tier's finding-ID set) and emit
    # exactly one ID-set warning. EXPECTED RED until Lane B2b's T017 wires
    # warn_delta_scope with this tier's finding IDs at this call site --
    # at T019 time nothing in extract-report-data.py calls warn_delta_scope
    # yet (the parser-level function is already fully pinned in
    # test_tachi_parsers.py; this is the wiring gap).
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "baseline_status_id_mismatch"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert _delta_counts_from_typ(content) == {
        "new": 1, "unchanged": 1, "updated": 1, "resolved": 0,
    }
    assert stderr.count("Section 7 status IDs differ from tier finding IDs") == 1
    assert "(1 only-in-map, 1 only-in-tier)" in stderr


# =============================================================================
# Feature 373 US-3a: K13.1 recommendation placeholder/fallback (tasks.md
# T019), per data-model.md §7's per-tier table. Fixtures:
# recommendations_partial_join/ and recommendations_drifted/ (tier 1 only;
# both are threats.md + compensating-controls.md runs).
# =============================================================================


def _typst_records(content: str, let_name: str) -> list:
    """Return each one-line record body from ``#let <let_name> = (...)``."""
    start = content.index(f"#let {let_name} = (")
    end = content.index("\n)", start)
    return re.findall(r'^\s*\((.*)\),?\s*$', content[start:end], re.MULTILINE)


def _typst_field(record: str, key: str) -> "str | None":
    m = re.search(rf'{re.escape(key)}: "([^"]*)"', record)
    return m.group(1) if m else None


def _findings_by_id(content: str, field: str = "recommendation") -> dict:
    return {
        _typst_field(r, "id"): _typst_field(r, field)
        for r in _typst_records(content, "findings")
    }


def _remediation_actions_by_id(content: str) -> dict:
    return {
        _typst_field(r, "finding-id"): _typst_field(r, "recommendation")
        for r in _typst_records(content, "remediation-actions")
    }


_T1_ANALYZER_TEXT = (
    "Implement per-tenant rate limiting and a Web Application Firewall rule "
    "set at the API Gateway ingress to absorb volumetric requests before "
    "they reach backend services."
)
_T2_PREFIXED_FALLBACK = "Threat-model mitigation: Apply rate limiting at the ingress"
_REC_PLACEHOLDER = "No recommendation available"


def test_k131_tier1_partial_join_recommendation_precedence_via_cli():
    # US-3a #8 (K13.1/FR-K13.1); data-model.md §7 tier-1 precedence: the
    # analyzer recommendation (T-1, covered by Section 4) wins over the
    # prefixed Section 7 mitigation fallback (T-2, not covered but has
    # mitigation text), which wins over the placeholder (T-3, neither
    # source has text). No Section 4 drift warning (at least one join
    # succeeded).
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "recommendations_partial_join"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    recs = _findings_by_id(content)
    assert recs["T-1"] == _T1_ANALYZER_TEXT
    assert recs["T-2"] == _T2_PREFIXED_FALLBACK
    assert recs["T-3"] == _REC_PLACEHOLDER
    assert "no recommendations matched" not in stderr


def test_k131_tier1_drifted_section4_warns_and_falls_back_via_cli():
    # US-3a #9: Section 4 has content but for an ID (Z-9) absent from the
    # tier-1 rows, so zero joins succeed -- the extractor warns, and every
    # finding falls back to its prefixed Section 7 mitigation or the
    # placeholder.
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "recommendations_drifted"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    recs = _findings_by_id(content)
    assert recs["T-1"] == "Threat-model mitigation: Restrict admin endpoints to VPN access"
    assert recs["T-2"] == _REC_PLACEHOLDER
    assert "controls Section 4 has content but no recommendations matched" in stderr


def test_k131_roadmap_matches_card_recommendation_tier1_via_cli():
    # data-model.md §7: on tier 1, the roadmap action text and the finding
    # card read the same `recommendation` field, so they always agree.
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "recommendations_partial_join"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    card = _findings_by_id(content)
    roadmap = _remediation_actions_by_id(content)
    assert roadmap == card, f"roadmap {roadmap} must equal card {card} on tier 1"


def test_k131_roadmap_tier2_empty_threat_falls_back_to_placeholder():
    # data-model.md §7 tier 2 row: today's threat text; REC_PLACEHOLDER
    # only when that resolves empty. EXPECTED RED until Lane B2b's T017
    # adds this guard -- today build_remediation_actions emits "" verbatim
    # for an empty threat (scripts/extract-report-data.py:211-213).
    extract = _load_extract_module()
    findings = [{"id": "T-2", "threat": "", "severity": "Medium"}]
    actions = extract.build_remediation_actions(
        findings, tier=2, tr_data={"remediation_timeline": [{"anything": True}]}
    )
    assert actions[0]["recommendation"] == _REC_PLACEHOLDER


def test_k131_tier3_empty_mitigation_resolves_once_for_all_three_consumers_via_cli():
    # data-model.md §7 tier 3 row: "mitigation, or the placeholder when
    # empty" is resolved ONCE, upstream in main() -- the card, the roadmap
    # and the attack path then all read that same already-resolved
    # `mitigation` field (the contract's "so the placeholder when empty"
    # phrasing for the roadmap/attack-path columns describes a
    # CONSEQUENCE of reading the shared field, not an independent guard
    # inside build_remediation_actions or _get_finding_mitigation). No
    # fixture existed for this tier-3 case; added
    # recommendations_tier3_empty_mitigation/ (documented in the fixture
    # README) since T003's list only covered tier-1 K13.1 scenarios.
    #
    # A prior draft of this test called build_remediation_actions directly
    # with a hand-built {"mitigation": ""} finding and expected it to
    # apply the placeholder itself. That stayed red against the merged
    # probe's B2b implementation (373-w2-B2b), which resolves the
    # placeholder upstream in main() instead and has build_remediation_actions
    # / _get_finding_mitigation read the already-resolved field verbatim --
    # matching the contract's literal wording more closely than the
    # original test did. Rewritten as this end-to-end check rather than
    # left pinned to the wrong call contract.
    returncode, _stdout, stderr, content = run_extract(
        FIDELITY_FIXTURES_DIR / "recommendations_tier3_empty_mitigation"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"

    card = _findings_by_id(content, field="mitigation")
    assert card["T-1"] == "Apply per-IP rate limiting at the gateway"
    assert card["T-2"] == _REC_PLACEHOLDER

    extract = _load_extract_module()
    roadmap = extract.build_remediation_actions(
        [{"id": fid, "mitigation": text} for fid, text in card.items()],
        tier=3,
        tr_data={"remediation_timeline": [{"anything": True}]},
    )
    roadmap_by_id = {a["finding-id"]: a["recommendation"] for a in roadmap}
    assert roadmap_by_id == card

    for fid, resolved_text in card.items():
        mitigation = extract._get_finding_mitigation({"id": fid, "mitigation": resolved_text})
        assert mitigation == resolved_text
    assert extract._build_remediation(card["T-2"]) == [_REC_PLACEHOLDER]


def test_k131_attack_path_tier2_stays_generic_not_placeholder():
    # data-model.md §7 tier 2 row, attack-path column: UNCHANGED --
    # _get_finding_mitigation returns "" (a tier-2 finding has neither a
    # recommendation nor a mitigation field) and _build_remediation renders
    # its generic step, never the roadmap's REC_PLACEHOLDER text. This is
    # the one tier-2 divergence data-model.md §7 calls out between the
    # roadmap and the attack path; it already holds today (an
    # anchor/regression guard T017 must not disturb).
    extract = _load_extract_module()
    mitigation = extract._get_finding_mitigation({"id": "T-2", "severity": "Medium"})
    assert mitigation == ""
    steps = extract._build_remediation(mitigation)
    assert steps == ["Review and implement appropriate security controls."]
    assert _REC_PLACEHOLDER not in steps[0]
