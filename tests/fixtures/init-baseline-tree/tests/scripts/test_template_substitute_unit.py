"""Unit-level tests for `aod_template_substitute_placeholders` (FR-001).

This module replaces 8 of the 12 substitution-semantics adversarial cases that
historically lived in the soon-to-be-deleted `ADVERSARIAL_CASES` block at the
top of the legacy adversarial test module. By exercising the helper directly
(sub-second `bash -c source` per case) instead of forking the project install
script end-to-end (~30s per case on macos-latest cold cache), this module
eliminates the 300s subprocess timeout class on the macos-latest CI leg
(FR-016 / SC-002).

R-4 — locale-pinning rationale (FR-008):
    Every `subprocess.run` invocation pins `LC_ALL=C` in a freshly constructed
    `env=` mapping. The parent shell's locale is NOT inherited — multibyte
    cases (Ⅷ-Ⅸ) under a UTF-8 parent locale would mask byte-boundary bugs that
    surface only under a C/POSIX locale. The 12 `AOD_PERSONALIZATION_*` env
    vars are also set here (per the helper's environment contract) and PATH is
    forwarded so `bash`, `cat`, `tail`, `od`, `mv`, etc. remain resolvable.

Load-bearing shim contract (FR-010 / SC-006):
    The substitution helper at `.aod/scripts/bash/template-substitute` (line 64
    of the helper file) calls `shopt -u patsub_replacement 2>/dev/null || true`.
    This shim disables the bash 5.2+ default that interprets `&` in
    `${var//pat/repl}` replacements as "match-text" backref — defeating the
    literal-substitution invariant (ADR-038 §D-1). On bash 3.2 (macOS) the
    shopt is unknown and silently no-ops via the redirect.

    Cases marked `# shim-sensitive: yes` (1 ampersand, 3 backref, 6 multibyte)
    MUST fail when the shim is removed on bash 5.x; cases marked
    `# shim-sensitive: no` (2, 4, 5, 7, 8) MUST pass under the same fault
    state. This split is the deliberate-fault matrix proven by T013.

    The test invocation below ALSO calls `shopt -u patsub_replacement` defensively,
    so the assertion holds under either bash 3.2 or bash 5.x without depending
    on shim state inherited from a parent shell.

Zero-import constraint (FR-003):
    This module deliberately imports zero integration helpers. The historical
    end-to-end fork pattern is replaced with a direct sourced-helper call.
    The whole point of the FR-001 extraction is to eliminate the integration
    layer for these 8 cases.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


# Each entry: SubstituteCase per data-model.md §Schema 1.
#   id            — kebab-case label, used as pytest -k filter and failure ID
#   project_name  — value substituted into AOD_PERSONALIZATION_PROJECT_NAME
#   src_content   — exact bytes written to tmp_path/src
#   expected_dest — exact bytes expected in tmp_path/dest after substitution
#   marker        — short rationale for failure messages and audit
SUBSTITUTE_CASES: list[dict] = [
    # shim-sensitive: yes (the F-248 closure — sed `&` corrupted AT&T to ATtachiT)
    {
        "id": "case_1_ampersand",
        "project_name": "AT&T",
        "src_content": "tachi\n",
        "expected_dest": "AT&T\n",
        "marker": "sed `&` backref expansion (the F-248 closure)",
    },
    # shim-sensitive: no (pipe is not a patsub_replacement metachar)
    {
        "id": "case_2_pipe",
        "project_name": "foo|bar",
        "src_content": "tachi\n",
        "expected_dest": "foo|bar\n",
        "marker": "sed `|` alternation in s///",
    },
    # shim-sensitive: yes (backref-style replacement under patsub_replacement)
    {
        "id": "case_3_backref",
        "project_name": "\\1\\2",
        "src_content": "tachi\n",
        "expected_dest": "\\1\\2\n",
        "marker": "sed `\\1\\2` capture-group backref",
    },
    # shim-sensitive: no (pure parameter expansion; quotes are literal in helper)
    {
        "id": "case_4_single_quoted",
        "project_name": "'inside'",
        "src_content": "tachi\n",
        "expected_dest": "'inside'\n",
        "marker": "shell quote-stripping pre-substitution",
    },
    # shim-sensitive: no (pure parameter expansion; quotes are literal in helper)
    {
        "id": "case_5_double_quoted",
        "project_name": '"inside"',
        "src_content": "tachi\n",
        "expected_dest": '"inside"\n',
        "marker": "shell expansion inside double-quotes",
    },
    # shim-sensitive: yes (bash 5.x patsub_replacement multibyte byte-boundary handling)
    {
        "id": "case_6_multibyte",
        "project_name": "Ⅷ-Ⅸ",
        "src_content": "tachi\n",
        "expected_dest": "Ⅷ-Ⅸ\n",
        "marker": "bash 5.x patsub_replacement multibyte handling — load-bearing for shim",
    },
    # shim-sensitive: no (embedded LF in value; helper preserves byte-for-byte)
    {
        "id": "case_7_newline_in_value",
        "project_name": "line1\nline2",
        "src_content": "tachi\n",
        "expected_dest": "line1\nline2\n",
        "marker": "embedded LF byte handling",
    },
    # shim-sensitive: no (empty value substitution edge — only template trailing LF remains)
    {
        "id": "case_8_empty_value",
        "project_name": "",
        "src_content": "tachi\n",
        "expected_dest": "\n",
        "marker": "empty-value substitution edge",
    },
]


@pytest.mark.parametrize("case", SUBSTITUTE_CASES, ids=lambda c: c["id"])
def test_template_substitute(case: dict, tmp_path: Path) -> None:
    """Per-case unit assertion against `aod_template_substitute_placeholders`.

    Each case writes `src_content` to `tmp_path/src`, invokes the helper via
    `bash -c "shopt -u patsub_replacement; source ...; aod_template_substitute_placeholders src dest"`
    with `LC_ALL=C` and the 12 `AOD_PERSONALIZATION_*` env vars set, and
    asserts the dest file matches `expected_dest` byte-literally.
    """
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.write_text(case["src_content"])

    env = {
        "LC_ALL": "C",
        "PATH": os.environ["PATH"],
        "AOD_PERSONALIZATION_PROJECT_NAME": case["project_name"],
        "AOD_PERSONALIZATION_PROJECT_DESCRIPTION": "stub-description",
        "AOD_PERSONALIZATION_GITHUB_USER": "stub-user",
        "AOD_PERSONALIZATION_GITHUB_REPO": "stub-repo",
        "AOD_PERSONALIZATION_AUTHOR_NAME": "stub-author",
        "AOD_PERSONALIZATION_AUTHOR_EMAIL": "stub@example.com",
        "AOD_PERSONALIZATION_LICENSE": "MIT",
        "AOD_PERSONALIZATION_RATIFICATION_DATE": "2026-05-04",
        "AOD_PERSONALIZATION_TIMESTAMP": "2026-05-04T00:00:00Z",
        "AOD_PERSONALIZATION_PROJECT_TYPE": "library",
        "AOD_PERSONALIZATION_VERSION": "0.0.0",
        "AOD_PERSONALIZATION_HOMEPAGE": "https://example.com",
    }

    bash_script = (
        "shopt -u patsub_replacement 2>/dev/null||true; "
        "source .aod/scripts/bash/template-substitute.sh; "
        f"aod_template_substitute_placeholders '{src}' '{dest}'"
    )

    result = subprocess.run(
        ["bash", "-c", bash_script],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, (
        f"helper exited {result.returncode} for {case['id']} "
        f"({case['marker']}). stderr: {result.stderr!r}"
    )
    assert dest.read_text() == case["expected_dest"], (
        f"substitution mismatch for {case['id']} ({case['marker']}). "
        f"expected: {case['expected_dest']!r}, got: {dest.read_text()!r}"
    )
