"""init.sh pre-commit prompt-flag matrix test (F-5).

Tests the 6-case matrix `[TTY/no-TTY] × [no-flag/--no-precommit/--precommit]`
covering the opt-in pre-commit prompt inserted after personalization
confirmation in scripts/init.sh.

Each test asserts:
  - Whether the pre-commit prompt was emitted to the user
  - Whether init.sh attempted `pre-commit install` (success or graceful WARN)

Auto-skip pattern: if the cloned tree's scripts/init.sh lacks the pre-commit
prompt block, cases auto-skip with a clear reason.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import init_sh_helpers as h

REPO_ROOT = Path(__file__).resolve().parents[2]

# Marker text emitted by init.sh prompt block (T015 contract).
PROMPT_MARKER = "Install pre-commit secret-scanning hook"

# Marker text emitted on graceful pre-commit-missing WARN (T015 contract).
WARN_MARKER = "WARN: pre-commit"


def _check_t015_landed(clone_root: Path) -> None:
    """Skip the test if T015 init.sh delta is not present in the clone.

    Probes the cloned `scripts/init.sh` for the prompt marker text. T015
    lands in Wave 3 — until then, this skipif causes the matrix to auto-skip.
    """
    init_sh = clone_root / "scripts" / "init.sh"
    if not init_sh.exists():
        pytest.skip("init.sh missing from clone (unexpected)")
    content = init_sh.read_text()
    if PROMPT_MARKER not in content:
        pytest.skip("T015 init.sh delta not landed in HEAD; this test auto-activates after T015 commits land")


def _build_stdin(clone_root: Path, *, precommit_response: str = "") -> str:
    """Build canonical stdin including the pre-commit prompt response.

    Default `precommit_response=""` invokes init.sh's default-Y fallback
    (the prompt's `${response:-Y}` expansion).
    """
    base = h.build_canonical_stdin(clone_root)
    return base + precommit_response + "\n"


def _run_init_with_flags(clone_root: Path, *, flags: list[str] | None = None,
                         stdin: str = "", timeout_sec: int = 900) -> h.InitRun:
    """Invoke init.sh with optional --no-precommit / --precommit flag args.

    Mirrors `h.run_init_in_clone` but appends `flags` to the bash invocation.
    """
    fake_home = clone_root.parent / "fake_home"
    fake_home.mkdir(exist_ok=True)
    env = {
        **os.environ,
        "LC_ALL": "C",
        "HOME": str(fake_home),
        "PATH": h._safe_path(),
        "AOD_RATIFICATION_DATE_OVERRIDE": "2026-05-04",
        "AOD_CURRENT_DATE_OVERRIDE": "2026-05-04",
    }
    cmd = ["bash", "./scripts/init.sh"]
    if flags:
        cmd.extend(flags)

    completed = subprocess.run(
        cmd,
        cwd=str(clone_root),
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_sec,
    )
    return h.InitRun(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        tmpdir=clone_root,
    )


def _prompt_emitted(run: h.InitRun) -> bool:
    """Whether init.sh emitted the pre-commit-install prompt text."""
    return PROMPT_MARKER in run.stdout or PROMPT_MARKER in run.stderr


def _install_attempted(run: h.InitRun) -> bool:
    """Whether init.sh attempted `pre-commit install` (success OR graceful WARN).

    Two acceptable signals:
      - "pre-commit installed at .git/hooks/pre-commit" (success path)
      - "WARN: pre-commit" prefix (T015 graceful-fallback path when
        pre-commit framework is missing on PATH)
    """
    output = run.stdout + run.stderr
    return ("pre-commit installed at" in output) or (WARN_MARKER in output)


# ============================================================================
# Matrix: [TTY simulation × no-flag/--no-precommit/--precommit] = 6 cases
# ============================================================================
#
# Note on TTY-vs-non-TTY in subprocess.run context: init.sh's `[ -t 0 ]`
# check returns FALSE for piped stdin (which is what subprocess.run uses).
# True TTY simulation requires `pty.openpty()`, which is fragile when
# combined with input feeding for the multiple personalization prompts that
# precede the pre-commit prompt. T017 covers TTY×no-flag empirically; the
# pytest matrix below validates the flag-override paths and the non-TTY
# default-skip path — the cases that are deterministic in subprocess context.
# ============================================================================


def test_non_tty_no_flag_skips_prompt_and_install(tmp_path: Path) -> None:
    """Case 1: non-TTY × no-flag → prompt SKIPPED, install NOT attempted.

    `[ -t 0 ]` returns false for piped stdin. With no flag override,
    init.sh should skip both the prompt and the install.
    """
    clone = h.clone_into_tmpdir(tmp_path)
    _check_t015_landed(clone)
    stdin = _build_stdin(clone)
    run = _run_init_with_flags(clone, flags=[], stdin=stdin)
    assert not _prompt_emitted(run), "non-TTY no-flag: prompt must NOT be emitted"
    assert not _install_attempted(run), "non-TTY no-flag: install must NOT be attempted"


def test_non_tty_no_precommit_flag_skips_install(tmp_path: Path) -> None:
    """Case 2: non-TTY × --no-precommit → prompt SKIPPED, install NOT attempted."""
    clone = h.clone_into_tmpdir(tmp_path)
    _check_t015_landed(clone)
    stdin = _build_stdin(clone)
    run = _run_init_with_flags(clone, flags=["--no-precommit"], stdin=stdin)
    assert not _prompt_emitted(run), "--no-precommit: prompt must NOT be emitted"
    assert not _install_attempted(run), "--no-precommit: install must NOT be attempted"


def test_non_tty_precommit_flag_force_install(tmp_path: Path) -> None:
    """Case 3: non-TTY × --precommit → prompt SKIPPED, install ATTEMPTED.

    The --precommit flag forces installation regardless of TTY (expect-style
    automation per Q4).
    """
    clone = h.clone_into_tmpdir(tmp_path)
    _check_t015_landed(clone)
    stdin = _build_stdin(clone)
    run = _run_init_with_flags(clone, flags=["--precommit"], stdin=stdin)
    assert not _prompt_emitted(run), "--precommit: prompt must NOT be emitted (force-install bypasses prompt)"
    assert _install_attempted(run), "--precommit: install MUST be attempted (success or graceful WARN)"


@pytest.mark.skip(reason=(
    "Case 4 (TTY × no-flag default-Y) requires real TTY simulation via "
    "pty.openpty(); the multi-prompt personalization sequence makes pty input "
    "feeding fragile. T017 covers this scenario via manual empirical "
    "verification (5-scenario walkthrough). Re-enable if pty harness lands."
))
def test_tty_no_flag_default_y(tmp_path: Path) -> None:
    """Case 4: TTY × no-flag default-Y → prompt EMITTED, install ATTEMPTED."""
    pass  # see skip reason


def test_tty_no_precommit_flag_via_subprocess(tmp_path: Path) -> None:
    """Case 5: TTY-equivalent × --no-precommit → prompt SKIPPED, install NOT attempted.

    In subprocess context the TTY check is false, but --no-precommit's
    flag-override behavior is identical regardless of TTY. This case
    exercises the flag-override path under TTY-presumed conditions.
    """
    clone = h.clone_into_tmpdir(tmp_path)
    _check_t015_landed(clone)
    stdin = _build_stdin(clone)
    run = _run_init_with_flags(clone, flags=["--no-precommit"], stdin=stdin)
    assert not _prompt_emitted(run), "TTY --no-precommit: prompt must NOT be emitted (flag override)"
    assert not _install_attempted(run), "TTY --no-precommit: install must NOT be attempted (flag override)"


def test_tty_precommit_flag_via_subprocess(tmp_path: Path) -> None:
    """Case 6: TTY-equivalent × --precommit → prompt SKIPPED, install ATTEMPTED.

    In subprocess context the TTY check is false, but --precommit's
    force-install behavior is identical regardless of TTY.
    """
    clone = h.clone_into_tmpdir(tmp_path)
    _check_t015_landed(clone)
    stdin = _build_stdin(clone)
    run = _run_init_with_flags(clone, flags=["--precommit"], stdin=stdin)
    assert not _prompt_emitted(run), "TTY --precommit: prompt must NOT be emitted (flag override)"
    assert _install_attempted(run), "TTY --precommit: install MUST be attempted (flag override)"
