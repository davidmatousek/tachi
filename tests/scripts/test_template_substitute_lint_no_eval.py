"""Lint test: no `eval` in template-substitute.sh (FR-007 + ADR-040 Decision Item 7).

This module is Test-5 of the F-2 BLP-02 Wave 2 (Source-Pattern Hardening) test
surface. It enforces the architectural rule that template-substitute.sh
contains ZERO eval invocations after the F-2 refactor.

Background
----------
Pre-F-2, `template-substitute.sh` had FOUR eval invocations:
  - line :217  → `eval "val=\\"\\${$key:-}\\""`           (read-side w/ default)
  - line :249  → `eval "AOD_PERSONALIZATION_${key}=\\"\\$val\\""` (write-side dynamic assign)
  - line :536  → `eval "val=\\"\\${$key:-}\\""`           (read-side w/ default)
  - line :558  → `eval "val=\\"\\${$key}\\""`             (read-side strict)

F-2 replaces all four with bash 3.2-compatible alternatives:
  - read-side: `local var_name=$key; local val=${!var_name:-}` (or `${!var_name}` strict)
  - write-side: `printf -v "AOD_PERSONALIZATION_${key}" '%s' "$val"`

The library `template-config-load.sh` retains ONE internal eval as the audit-
clarity carve-out per ADR-040 Decision Item 7 (bash 3.2 indirect array access).
This carve-out is explicitly scoped to the library and is NOT applied to
template-substitute.sh.

Future-PR-blocker semantics
---------------------------
This test is a forward-looking lint: if a future PR introduces a new `eval`
to template-substitute.sh, the test fails immediately, blocking review at
the canonical-pattern rule. Code-reviewers should treat any test failure
here as a refactor signal, not a test bug — the canonical pattern is
`printf -v` for assignment and `${!var}` for indirect read.

Closes TACHI-VULN-9a7512071b4a (MEDIUM).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_SUBSTITUTE_PATH = REPO_ROOT / ".aod" / "scripts" / "bash" / "template-substitute.sh"


def test_no_eval_in_template_substitute() -> None:
    """Assert `template-substitute.sh` contains zero `\\beval\\b` matches.

    Uses GNU/BSD-portable `grep -c '\\beval\\b'` to count whole-word eval
    occurrences. The `\\b` word-boundary anchor avoids false positives on
    substrings like "evaluate" or "preval".

    Acceptance criteria (FR-007):
      Pre-F-2: 4 matches expected.
      Post-F-2: 0 matches required (this test asserts).
      Future PR introducing a new `eval` to this file: this test fails,
        blocking the PR at the canonical-pattern rule.
    """
    assert TEMPLATE_SUBSTITUTE_PATH.is_file(), (
        f"template-substitute.sh not found at expected path: "
        f"{TEMPLATE_SUBSTITUTE_PATH}"
    )

    # Per FR-007 lint contract: `grep -c '\\beval\\b'` MUST return 0. The
    # post-F-2 file contains zero matches (executable AND comment) — all
    # commit comments referencing the pre-F-2 patterns have been rephrased
    # to reference "ADR-040 Decision Item 7" rather than the bare token,
    # so a future PR adding a new eval (executable OR comment) is detected
    # immediately at this lint.
    result = subprocess.run(
        ["grep", "-c", r"\beval\b", str(TEMPLATE_SUBSTITUTE_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )

    # `grep -c` exits 1 if no matches found AND prints "0\n". Both rc 0
    # (matches found) and rc 1 (no matches) are valid; rc >1 indicates an
    # I/O error.
    assert result.returncode in (0, 1), (
        f"grep failed with rc {result.returncode}; stderr: {result.stderr!r}"
    )

    count = int(result.stdout.strip())
    assert count == 0, (
        f"FR-007 violation: found {count} `eval` token(s) in "
        f"{TEMPLATE_SUBSTITUTE_PATH}. Per ADR-040 Decision Item 7, this file "
        f"MUST contain zero eval — the canonical pattern is `printf -v` for "
        f"assignment and `${{!var}}` for indirect read. If a refactor "
        f"genuinely requires eval (e.g., bash 3.2 indirect array access), "
        f"that case belongs in template-config-load.sh, NOT here."
    )
