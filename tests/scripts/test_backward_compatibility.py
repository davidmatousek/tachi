"""Backward compatibility test — byte-identical PDF guarantee.

Proves that running the current pipeline against each unmodified example produces
a PDF byte-identical to the committed ``.baseline``. Byte-identity catches any
silent regression to the PDF security-report pipeline for examples that recent
changes do not intentionally touch.

Typst embeds wall-clock timestamps into the PDF Info dictionary, XMP metadata
stream, and ``xmpMM:InstanceID``, so two consecutive invocations normally
produce non-identical PDFs. The reproducible-builds.org ``SOURCE_DATE_EPOCH``
convention is honored natively by Typst and pins all timestamp-derived fields.
This test MUST set the same value used when the baselines were generated,
otherwise the byte comparison fails inside the metadata region.

The ``agentic-app`` example is excluded because it is the regeneration target
for the executive-architecture template and is not expected to match the
pre-existing baseline.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
TEMPLATE_MAIN = TEMPLATE_DIR / "main.typ"
REPORT_DATA_TYP = TEMPLATE_DIR / "report-data.typ"

# Do NOT change this without regenerating all .baseline files in the same commit —
# any other value will make Typst emit different metadata timestamps and cmp will fail.
SOURCE_DATE_EPOCH = "1700000000"

BASELINE_EXAMPLES = [
    "web-app",
    "microservices",
    "ascii-web-api",
    "mermaid-agentic-app",
    "free-text-microservice",
]


def _hex_context(data: bytes, offset: int, window: int = 16) -> str:
    start = max(0, offset - window)
    end = min(len(data), offset + window + 1)
    chunk = data[start:end]
    hex_repr = " ".join(f"{b:02x}" for b in chunk)
    return f"bytes[{start}:{end}] = {hex_repr}"


def _find_first_divergence(a: bytes, b: bytes) -> int:
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    return min_len


@pytest.mark.slow
@pytest.mark.parametrize("example_name", BASELINE_EXAMPLES)
def test_unmodified_examples_byte_identical_pdfs(
    example_name: str, tmp_path: Path
) -> None:
    """Regenerate report-data.typ, run typst compile, and assert bytes match the baseline."""
    target_dir = REPO_ROOT / "examples" / example_name
    baseline_pdf = target_dir / "security-report.pdf.baseline"
    generated_pdf = tmp_path / "security-report.pdf"

    assert baseline_pdf.exists(), (
        f"Baseline PDF missing for example '{example_name}': {baseline_pdf}"
    )

    pipeline_env = {**os.environ, "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH}

    try:
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

        baseline_bytes = baseline_pdf.read_bytes()
        generated_bytes = generated_pdf.read_bytes()

        if baseline_bytes == generated_bytes:
            return

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
            "  If the offset is inside the PDF Info dictionary or XMP stream, "
            "the env var is not being honored (determinism regression). "
            "Otherwise investigate any script or template change that would "
            "alter unmodified examples."
        )

    except subprocess.CalledProcessError as exc:
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
        # Remove the generated report-data.typ so the template dir stays clean
        # for any subsequent test. The template dir does not commit this file.
        if REPORT_DATA_TYP.exists():
            try:
                REPORT_DATA_TYP.unlink()
            except OSError:
                pass
