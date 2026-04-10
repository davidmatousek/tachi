"""F-128 backward compatibility test — byte-identical PDF guarantee.

This module implements task T024 for feature 128-prd-128-executive (Wave 4,
US-2). It proves that the 5 unmodified example PDFs render byte-identical
before and after the F-128 changes, protecting against silent regressions in
the PDF security-report pipeline for examples that F-128 does not touch.

Why byte-identity?
------------------
Byte-identity is the strongest possible guarantee that the F-128 code changes
do not affect outputs for unmodified examples. It catches any regression the
moment it would change a single pixel of rendered content. See
``specs/128-prd-128-executive/decisions.md`` Decision 1 for the storage
rationale (committed ``.baseline`` files) and Decision 3 for the determinism
rationale (``SOURCE_DATE_EPOCH``).

Why SOURCE_DATE_EPOCH?
----------------------
Typst's default PDF output embeds wall-clock timestamps into the PDF Info
dictionary (``/ModDate``, ``/CreationDate``), the XMP metadata stream, and a
timestamp-derived ``xmpMM:InstanceID``. That means two consecutive Typst
invocations produce non-byte-identical PDFs even when every other byte is the
same. The reproducible-builds.org convention ``SOURCE_DATE_EPOCH`` is honored
natively by Typst and pins all timestamp-derived fields to a fixed value. The
baselines in ``examples/{name}/security-report.pdf.baseline`` were generated
with ``SOURCE_DATE_EPOCH=1700000000`` (see ``.aod/results/wave-2-baselines.md``
Resolution section), so this test MUST set the same value or the byte-cmp
will always fail inside the Typst metadata region.

Scope: 5 baseline examples only
-------------------------------
This test covers exactly the 5 examples F-128 does NOT modify:

* ``web-app``
* ``microservices``
* ``ascii-web-api``
* ``mermaid-agentic-app``
* ``free-text-microservice``

The ``agentic-app`` example is intentionally excluded — it is the F-128
regeneration target (T033) and is not expected to match any pre-F-128
baseline.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


# Repository root resolved from this file's location:
# tests/scripts/test_backward_compatibility.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
TEMPLATE_MAIN = TEMPLATE_DIR / "main.typ"
REPORT_DATA_TYP = TEMPLATE_DIR / "report-data.typ"

# Fixed epoch from decisions.md Decision 3. Do NOT change this value without
# regenerating all 5 .baseline files in the same commit — any other value will
# make Typst emit different metadata timestamps and the cmp will fail.
SOURCE_DATE_EPOCH = "1700000000"

# The 5 examples that must remain byte-identical across F-128.
BASELINE_EXAMPLES = [
    "web-app",
    "microservices",
    "ascii-web-api",
    "mermaid-agentic-app",
    "free-text-microservice",
]


def _hex_context(data: bytes, offset: int, window: int = 16) -> str:
    """Return a human-readable hex dump of ``data`` around ``offset``.

    Used in the failure message to show exactly where two PDFs diverge. The
    window is ``±window`` bytes around the divergence, clamped to the buffer
    bounds.
    """
    start = max(0, offset - window)
    end = min(len(data), offset + window + 1)
    chunk = data[start:end]
    hex_repr = " ".join(f"{b:02x}" for b in chunk)
    return f"bytes[{start}:{end}] = {hex_repr}"


def _find_first_divergence(a: bytes, b: bytes) -> int:
    """Return the byte offset of the first mismatch between ``a`` and ``b``.

    If the buffers are the same length and byte-identical, this is not called
    because the equality assertion passes first. If the buffers differ in
    length, the offset returned is the first differing position up to the
    shorter length, or the shorter length itself if one is a strict prefix of
    the other.
    """
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    return min_len


@pytest.mark.parametrize("example_name", BASELINE_EXAMPLES)
def test_unmodified_examples_byte_identical_pdfs(
    example_name: str, tmp_path: Path
) -> None:
    """Assert that running the F-128 pipeline produces a byte-identical PDF.

    For each example in ``BASELINE_EXAMPLES``:

    1. Locate the committed baseline at
       ``examples/{name}/security-report.pdf.baseline``.
    2. Run ``scripts/extract-report-data.py`` against
       ``examples/{name}/`` to regenerate ``report-data.typ``.
    3. Run ``typst compile`` on ``main.typ`` with
       ``SOURCE_DATE_EPOCH=1700000000`` set, writing the PDF to
       ``tmp_path/security-report.pdf``.
    4. Read both files as bytes and assert byte-identity.
    5. On failure, surface the first diverging byte offset with ±16 bytes of
       hex context for diagnosis.

    The intermediate ``report-data.typ`` is cleaned up in a ``finally`` block
    so a failed assertion does not leave stale state for the next test case.
    """
    target_dir = REPO_ROOT / "examples" / example_name
    baseline_pdf = target_dir / "security-report.pdf.baseline"
    generated_pdf = tmp_path / "security-report.pdf"

    # Pre-condition: baseline must exist. If it's missing, T003d didn't copy
    # the file into place — fail loud and direct the reader at the right task.
    assert baseline_pdf.exists(), (
        f"Baseline PDF missing for example '{example_name}': {baseline_pdf}. "
        "Expected file to be present from Wave 2 task T003d. See "
        ".aod/results/wave-2-baselines.md for generation procedure."
    )

    # Environment for both subprocess invocations: inherit current env and
    # pin SOURCE_DATE_EPOCH so Typst produces deterministic timestamps.
    pipeline_env = {**os.environ, "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH}

    try:
        # Step 1: Extract report data from the example's threats.md (and
        # friends) into templates/tachi/security-report/report-data.typ. The
        # script overwrites in place; cleanup happens in the finally block.
        extract_cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--target-dir",
            str(target_dir),
            "--output",
            str(REPORT_DATA_TYP),
            "--template-dir",
            str(TEMPLATE_DIR),
        ]
        subprocess.run(
            extract_cmd,
            cwd=REPO_ROOT,
            env=pipeline_env,
            check=True,
            capture_output=True,
        )

        # Step 2: Compile main.typ to PDF. --root . ties Typst's import
        # resolution to the repo root, matching how the baselines were
        # produced (see wave-2-baselines.md section T003b).
        compile_cmd = [
            "typst",
            "compile",
            str(TEMPLATE_MAIN),
            str(generated_pdf),
            "--root",
            str(REPO_ROOT),
        ]
        subprocess.run(
            compile_cmd,
            cwd=REPO_ROOT,
            env=pipeline_env,
            check=True,
            capture_output=True,
        )

        # Read both PDFs as raw bytes for the comparison.
        baseline_bytes = baseline_pdf.read_bytes()
        generated_bytes = generated_pdf.read_bytes()

        # Fast-path: equal bytes means the test passes.
        if baseline_bytes == generated_bytes:
            return

        # Failure path: surface the first divergence with hex context so a
        # human reviewer can tell at a glance whether the mismatch is in
        # content (unexpected F-128 regression) or metadata (unexpected
        # determinism issue — should not happen because SOURCE_DATE_EPOCH is
        # set, but worth distinguishing in the error).
        divergence = _find_first_divergence(baseline_bytes, generated_bytes)
        baseline_ctx = _hex_context(baseline_bytes, divergence)
        generated_ctx = _hex_context(generated_bytes, divergence)

        raise AssertionError(
            "PDF byte mismatch for example "
            f"'{example_name}'.\n"
            f"  Baseline size:  {len(baseline_bytes)} bytes ({baseline_pdf})\n"
            f"  Generated size: {len(generated_bytes)} bytes "
            f"({generated_pdf})\n"
            f"  First divergence at byte offset: {divergence}\n"
            f"  Baseline context:  {baseline_ctx}\n"
            f"  Generated context: {generated_ctx}\n"
            f"  SOURCE_DATE_EPOCH={SOURCE_DATE_EPOCH} (determinism pin).\n"
            "  If offset is inside the PDF Info dictionary or XMP stream, "
            "the env var is not being honored (determinism regression). "
            "Otherwise this is a real F-128 backward-compat break — "
            "investigate the script/template change that would alter "
            "unmodified examples."
        )

    except subprocess.CalledProcessError as exc:
        # Surface the subprocess stderr so pipeline errors don't masquerade as
        # a silent comparison failure. This also helps debug PATH or Typst
        # version drift in CI environments.
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace")
        stdout = (exc.stdout or b"").decode("utf-8", errors="replace")
        raise AssertionError(
            f"Pipeline subprocess failed for example '{example_name}' "
            f"(exit={exc.returncode}).\n"
            f"  Command: {' '.join(exc.cmd)}\n"
            f"  stdout: {stdout}\n"
            f"  stderr: {stderr}"
        ) from exc

    finally:
        # Always remove the generated report-data.typ so the next test case
        # (or any other test that runs after) starts from a clean template
        # directory. The template dir does not commit report-data.typ, so
        # leaving it behind would also pollute the working tree.
        if REPORT_DATA_TYP.exists():
            try:
                REPORT_DATA_TYP.unlink()
            except OSError:
                # Best-effort cleanup; do not mask the primary assertion
                # failure if unlink races with something.
                pass
