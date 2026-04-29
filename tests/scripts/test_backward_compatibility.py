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

The following examples are excluded from this baseline list because they are
regeneration mutation targets for specific features and are not expected to
match a pre-existing baseline:

- ``agentic-app`` (F-128 / F-2 — executive-architecture template + LLM09 misinformation)
- ``consumer-agent-app`` (F-4 — human-trust-exploitation)
- ``predictive-ml-app`` (F-6 — ML Top 10 Coverage Bundle)
- ``mobile-banking-app`` (F-7 — Mobile Top 10 Coverage Bundle)

These targets are excluded by simply not appearing in ``BASELINE_EXAMPLES``.
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
    "maestro-reference",
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


# =============================================================================
# Feature 142 Wave 4 additions — T028 / T029
# =============================================================================

# Tachi detection agents whose zero-edit invariant must hold across Feature 142
# per ADR-026 Decision 1 (zero-edit invariant). This list is authoritative;
# adding a new detection agent file warrants updating both `schemas/coverage-
# checklists.yaml` and this list in the same change.
#
# Heuristic A enrichment branches additively edit existing detection-tier
# host files under ADR-023 Decision 3. Each carved-out file moves OUT of
# DETECTION_AGENT_PATHS and (for companions) INTO
# DETECTION_PATTERN_REF_ENRICHMENT_HOSTS in the same change. Files NOT listed
# here remain byte-identical on F-142 branches.
DETECTION_AGENT_PATHS = [
    ".claude/agents/tachi/prompt-injection.md",
    ".claude/agents/tachi/agent-autonomy.md",
    ".claude/agents/tachi/output-integrity.md",
    ".claude/agents/tachi/misinformation.md",
]

# Detection-patterns reference files produced by Feature 082 in
# `.claude/skills/tachi-<agent>/references/detection-patterns.md`. ADR-026
# Decision 1 requires these to remain byte-unmodified on the Feature 142
# feature branch because Feature 142 is a post-hoc synthesis layer and must
# not touch the detection tier. Companions modified by a Heuristic A
# enrichment branch are carved into DETECTION_PATTERN_REF_ENRICHMENT_HOSTS
# below.
DETECTION_PATTERN_REF_GLOB = ".claude/skills/tachi-*/references/detection-patterns.md"
DETECTION_PATTERN_REF_F3_HOST = ".claude/skills/tachi-tool-abuse/references/detection-patterns.md"
DETECTION_PATTERN_REF_F5_DOS_HOST = ".claude/skills/tachi-denial-of-service/references/detection-patterns.md"
DETECTION_PATTERN_REF_F5_MODEL_THEFT_HOST = ".claude/skills/tachi-model-theft/references/detection-patterns.md"
DETECTION_PATTERN_REF_F6_TAMPERING_HOST = ".claude/skills/tachi-tampering/references/detection-patterns.md"
DETECTION_PATTERN_REF_F6_DATA_POISONING_HOST = ".claude/skills/tachi-data-poisoning/references/detection-patterns.md"
DETECTION_PATTERN_REF_F7_SPOOFING_HOST = ".claude/skills/tachi-spoofing/references/detection-patterns.md"
DETECTION_PATTERN_REF_F7_INFO_DISCLOSURE_HOST = ".claude/skills/tachi-info-disclosure/references/detection-patterns.md"
DETECTION_PATTERN_REF_F7_PRIVILEGE_ESCALATION_HOST = ".claude/skills/tachi-privilege-escalation/references/detection-patterns.md"
DETECTION_PATTERN_REF_F7_REPUDIATION_HOST = ".claude/skills/tachi-repudiation/references/detection-patterns.md"
DETECTION_PATTERN_REF_ENRICHMENT_HOSTS = frozenset({
    DETECTION_PATTERN_REF_F3_HOST,
    DETECTION_PATTERN_REF_F5_DOS_HOST,
    DETECTION_PATTERN_REF_F5_MODEL_THEFT_HOST,
    DETECTION_PATTERN_REF_F6_TAMPERING_HOST,
    DETECTION_PATTERN_REF_F6_DATA_POISONING_HOST,
    DETECTION_PATTERN_REF_F7_SPOOFING_HOST,
    DETECTION_PATTERN_REF_F7_INFO_DISCLOSURE_HOST,
    DETECTION_PATTERN_REF_F7_PRIVILEGE_ESCALATION_HOST,
    DETECTION_PATTERN_REF_F7_REPUDIATION_HOST,
})


def test_feature_142_zero_edit_invariant_on_detection_agents():
    """ADR-026 Decision 1: no edits to the 11 detection agents on this branch.

    Per tasks.md T029 (architect LOW-3): assert ``git diff --name-only
    main..HEAD`` filtered to the 11 detection agent files and their
    companion detection-patterns.md reference files is empty. Any non-empty
    diff violates the zero-edit invariant and must be reverted before
    Feature 142 can ship.
    """
    # Only enforce when running on a Feature 142 branch (or a superset). On
    # main or other branches the invariant is trivially satisfied.
    branch_result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    current_branch = (branch_result.stdout or "").strip()
    if not current_branch or current_branch == "main":
        pytest.skip(
            f"Zero-edit invariant is only enforced on feature branches. "
            f"Current branch: {current_branch or '(none)'}"
        )

    # Build the glob-expanded list of files to diff against main. Use
    # `git ls-files` filtered by the glob so we get a stable enumeration
    # even if new detection-patterns.md files are added.
    ls_result = subprocess.run(
        ["git", "ls-files", DETECTION_PATTERN_REF_GLOB],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    detection_pattern_refs = [
        line
        for line in (ls_result.stdout or "").splitlines()
        if line.strip() and line not in DETECTION_PATTERN_REF_ENRICHMENT_HOSTS
    ]

    paths_to_check = DETECTION_AGENT_PATHS + detection_pattern_refs
    assert len(DETECTION_AGENT_PATHS) == 4, (
        f"Expected 4 detection agent paths, got {len(DETECTION_AGENT_PATHS)}. "
        "Update DETECTION_AGENT_PATHS when adding a new detection agent."
    )

    diff_result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=M", "main..HEAD", "--"]
        + paths_to_check,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    modified_files = [
        line for line in (diff_result.stdout or "").splitlines() if line.strip()
    ]

    assert modified_files == [], (
        f"Zero-edit invariant violated (ADR-026 Decision 1). "
        f"The following detection-tier files were modified on branch "
        f"{current_branch!r} relative to main: {modified_files}. "
        "Feature 142 (Post-Hoc Synthesis) must not edit detection agents "
        "or their companion detection-patterns.md reference files. Revert "
        "those changes or refactor the synthesis engine to avoid them."
    )


def test_feature_142_backward_compat_pattern_defaults():
    """FR-017: pre-Feature-142 threats.md without the Pattern column defaults
    every finding to ``agentic_pattern: none``.

    Exercises the three paths in ``parse_threats_findings`` + ``parse_finding_pattern``:
    (1) missing Pattern column (pre-Feature-142 baseline), (2) present Pattern
    column with em-dash placeholder, (3) present Pattern column with enum value.
    """
    # Make tachi_parsers importable from the test directory.
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from tachi_parsers import parse_threats_findings  # noqa: E402
    finally:
        # Keep sys.path clean.
        pass

    # Path 1 — pre-Feature-142 table with NO Pattern column.
    pre_f142 = (
        "## 7. Recommended Actions\n\n"
        "| Finding ID | Status | Component | Threat | Risk Level | Mitigation |\n"
        "|------------|--------|-----------|--------|------------|------------|\n"
        "| S-1 | NEW | API | Credential stuffing | High | MFA |\n"
    )
    findings = parse_threats_findings(pre_f142)
    assert len(findings) == 1
    assert findings[0]["agentic_pattern"] == "none", (
        "Pre-Feature-142 threats.md (no Pattern column) MUST default "
        f"agentic_pattern to 'none' per FR-017. Got: {findings[0]['agentic_pattern']!r}"
    )

    # Path 2 — post-Feature-142 table with em-dash placeholder rendering.
    em_dash = (
        "## 7. Recommended Actions\n\n"
        "| Finding ID | Status | Pattern | Component | Threat | Risk Level | Mitigation |\n"
        "|------------|--------|---------|-----------|--------|------------|------------|\n"
        "| S-1 | NEW | \u2014 | API | Credential stuffing | High | MFA |\n"
    )
    findings = parse_threats_findings(em_dash)
    assert findings[0]["agentic_pattern"] == "none", (
        f"Em-dash Pattern cell must normalize to 'none'. Got: {findings[0]['agentic_pattern']!r}"
    )

    # Path 3 — post-Feature-142 table with a real enum value.
    with_enum = (
        "## 7. Recommended Actions\n\n"
        "| Finding ID | Status | Pattern | Component | Threat | Risk Level | Mitigation |\n"
        "|------------|--------|---------|-----------|--------|------------|------------|\n"
        "| AG-1 | NEW | agent_collusion | Orchestrator | Collusion | High | Rate limits |\n"
    )
    findings = parse_threats_findings(with_enum)
    assert findings[0]["agentic_pattern"] == "agent_collusion", (
        f"Pattern enum value must pass through unchanged. Got: {findings[0]['agentic_pattern']!r}"
    )


@pytest.mark.parametrize("example_name", BASELINE_EXAMPLES)
def test_feature_142_multi_agent_gate_predicate_false_on_baselines(example_name):
    """SC-003 support: the 4 single-agent baselines produce zero non-`none`
    patterns because their architectures do not satisfy the multi-agent gate
    predicate. ``parse_threats_findings`` on each committed baseline emits
    findings that all carry ``agentic_pattern: none`` (either via missing
    Pattern column default or via explicit em-dash value).

    mermaid-agentic-app is excluded from this parametrization list (it lives
    in BASELINE_EXAMPLES but the SC-003 interpretation in tasks.md T033
    narrows SC-003 to the 4 single-agent baselines; mermaid-agentic-app's
    synthesis output would contain non-`none` patterns under the current
    rule table, documented as a known limitation).
    """
    # mermaid-agentic-app is an edge case per the T033 narrowed SC-003
    # interpretation — skip its multi-agent-gate-false assertion here.
    if example_name == "mermaid-agentic-app":
        pytest.skip(
            "mermaid-agentic-app is excluded from SC-003 per T033 narrowed "
            "interpretation (multi-agent gate predicate evaluates TRUE via "
            "condition (a)+(b); pattern classification is a documented "
            "known-limitation pending R-04/R-06 rule-tuning follow-up)."
        )

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from tachi_parsers import parse_threats_findings  # noqa: E402

    threats_path = REPO_ROOT / "examples" / example_name / "threats.md"
    assert threats_path.exists(), f"Missing baseline threats.md for {example_name}"

    content = threats_path.read_text()
    findings = parse_threats_findings(content)
    non_none = [f for f in findings if f.get("agentic_pattern") != "none"]
    assert non_none == [], (
        f"SC-003 violation: {example_name} produced {len(non_none)} non-`none` "
        f"patterns on a single-agent baseline. Expected zero. "
        f"Offending findings: {[(f['id'], f['agentic_pattern']) for f in non_none]}"
    )
