"""Clone timeout tests for `aod_template_fetch_upstream` (FR-006, F-2 Stream 4).

This module is Test-3 of the F-2 BLP-02 Wave 2 (Source-Pattern Hardening)
test surface. It validates the bash 3.2-portable background+kill watchdog
that wraps `git clone` in `aod_template_fetch_upstream`
(`.aod/scripts/bash/template-git.sh:102-104`).

Closes TACHI-VULN-851fd6a21ba9 (LOW).

Watchdog contract (per FR-006 + L-1 + Q-3):
  - `AOD_FETCH_TIMEOUT` env var validates against `^[1-9][0-9]*$`. Default 60.
  - Reject `=0` (Q-3 footgun), `=abc` (non-numeric), `=01` (leading zero).
  - Background `git clone &`; capture clone_pid.
  - Spawn `( sleep $TIMEOUT; kill -TERM $clone_pid ) &`; capture watchdog_pid.
  - Install trap `INT TERM EXIT` that kills the watchdog if the outer
    script is interrupted (L-1 process-leak window).
  - `wait $clone_pid; clone_rc=$?`.
  - On `clone_rc 143` (SIGTERM) or `130` (SIGINT) → `rm -rf $destdir`,
    emit timeout error, `trap - INT TERM EXIT`, return 9.
  - On any other exit → propagate rc.

Test cases (6):
  1. Hanging fixture + AOD_FETCH_TIMEOUT=3 → exit 9 within ~3-4s + destdir removed
  2. Hanging fixture + AOD_FETCH_TIMEOUT=10 → exit 9 at ~10s (not 60s default)
  3. AOD_FETCH_TIMEOUT=0 → exit 1 (Q-3 footgun)
  4. AOD_FETCH_TIMEOUT=abc → exit 1 (non-numeric)
  5. AOD_FETCH_TIMEOUT=01 → exit 1 (leading-zero rejection per regex `^[1-9][0-9]*$`)
  6. Fast clone + AOD_FETCH_TIMEOUT=60 → exit 0 + no zombie watchdog

R-1 — pipe-subshell trap:
  Test invokes `aod_template_fetch_upstream` directly via
  `subprocess.run([BASH_BIN, "-c", "source ...; aod_template_fetch_upstream ..."])`.
  No pipes anywhere.

Bash binary pin:
  `BASH = os.environ.get("BASH", "/bin/bash")` — system bash 3.2.57 on macOS.
  CI Linux runners use `bash` 5.x via env override.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_GIT_PATH = REPO_ROOT / ".aod" / "scripts" / "bash" / "template-git.sh"
LIB_PATH = REPO_ROOT / ".aod" / "scripts" / "bash" / "template-config-load.sh"
BASH_BIN = os.environ.get("BASH", "/bin/bash")


def _build_invocation(url: str, ref: str, destdir: str) -> str:
    """Build the bash script that sources the libs and invokes the function."""
    return (
        f"set +e; "
        f"source {LIB_PATH}; "
        f"source {TEMPLATE_GIT_PATH}; "
        f'aod_template_fetch_upstream "{url}" "{ref}" "{destdir}"; '
        f"echo RC=$?"
    )


def _run_with_timeout(bash_script: str, env_extra: dict, *, timeout: int = 30) -> subprocess.CompletedProcess:
    env = {
        "LC_ALL": "C",
        "PATH": os.environ["PATH"],
        **env_extra,
    }
    return subprocess.run(
        [BASH_BIN, "-c", bash_script],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


# -----------------------------------------------------------------------------
# Case 1 & 2 — hanging fixture exits 9 within the configured timeout.
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "timeout_seconds,upper_bound_seconds",
    [
        pytest.param(3, 5.0, id="case_1_timeout_3s"),
        pytest.param(10, 12.5, id="case_2_timeout_10s"),
    ],
)
def test_hanging_clone_times_out(
    hanging_upstream: str,
    tmp_path: Path,
    timeout_seconds: int,
    upper_bound_seconds: float,
) -> None:
    """Hanging upstream + AOD_FETCH_TIMEOUT=N → exit 9 within N+~2s, destdir gone.

    Verifies the watchdog kills the clone process, the function returns 9
    (not the underlying clone exit), and the partial destdir is cleaned up.
    """
    destdir = tmp_path / "fetched"
    bash_script = _build_invocation(hanging_upstream, "main", str(destdir))

    start = time.monotonic()
    result = _run_with_timeout(
        bash_script,
        {"AOD_FETCH_TIMEOUT": str(timeout_seconds)},
        timeout=int(upper_bound_seconds + 5),  # generous outer cap
    )
    elapsed = time.monotonic() - start

    rc_line = next(
        (line for line in result.stdout.splitlines() if line.startswith("RC=")),
        None,
    )
    assert rc_line is not None, (
        f"no RC line emitted; stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    rc = int(rc_line.split("=", 1)[1])
    assert rc == 9, (
        f"watchdog returned rc {rc} for hanging clone (expected 9). "
        f"elapsed {elapsed:.2f}s. stderr: {result.stderr!r}"
    )
    # Allow generous lower bound: AOD_FETCH_TIMEOUT - small slack for fork
    # latency (the watchdog is bash-level and depends on `sleep` precision).
    lower = max(0.5, timeout_seconds - 1.0)
    assert lower <= elapsed <= upper_bound_seconds, (
        f"elapsed {elapsed:.2f}s outside expected window "
        f"[{lower:.2f}, {upper_bound_seconds:.2f}] for timeout={timeout_seconds}"
    )
    assert not destdir.exists(), (
        f"destdir {destdir} not cleaned up after timeout. "
        f"stderr: {result.stderr!r}"
    )


# -----------------------------------------------------------------------------
# Cases 3, 4, 5 — invalid AOD_FETCH_TIMEOUT rejected exit 1.
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "timeout_value",
    [
        pytest.param("0", id="case_3_zero_footgun"),
        pytest.param("abc", id="case_4_non_numeric"),
        pytest.param("01", id="case_5_leading_zero"),
    ],
)
def test_invalid_timeout_rejected(
    tmp_path: Path,
    timeout_value: str,
) -> None:
    """Invalid AOD_FETCH_TIMEOUT (Q-3) rejected exit 1 BEFORE clone starts.

    Q-3 ruling: `=0` is a footgun (would mean "fail immediately"); Q-3
    rejects it. `=abc` is non-numeric. `=01` is leading-zero (regex
    `^[1-9][0-9]*$` rejects).

    Use a placeholder URL (file:// to a non-existent path) to ensure no
    network activity; the validation MUST run BEFORE clone is forked.
    """
    destdir = tmp_path / "fetched"
    fake_url = "file:///nonexistent/path/that/should/never/be/reached.git"
    bash_script = _build_invocation(fake_url, "main", str(destdir))

    result = _run_with_timeout(
        bash_script,
        {"AOD_FETCH_TIMEOUT": timeout_value},
        timeout=10,
    )

    rc_line = next(
        (line for line in result.stdout.splitlines() if line.startswith("RC=")),
        None,
    )
    assert rc_line is not None, (
        f"no RC line emitted; stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    rc = int(rc_line.split("=", 1)[1])
    assert rc == 1, (
        f"AOD_FETCH_TIMEOUT={timeout_value!r} returned rc {rc} (expected 1 — "
        f"Q-3 footgun rejection). stderr: {result.stderr!r}"
    )
    # Stderr should mention AOD_FETCH_TIMEOUT (specific footgun message).
    assert "AOD_FETCH_TIMEOUT" in result.stderr, (
        f"expected stderr to name AOD_FETCH_TIMEOUT for value {timeout_value!r}; "
        f"got stderr: {result.stderr!r}"
    )


# -----------------------------------------------------------------------------
# Case 6 — fast clone with default timeout completes cleanly.
# -----------------------------------------------------------------------------
def _build_tiny_upstream(tmp_path: Path) -> str:
    """Build a tiny in-tmp git repo to clone from. Returns the file:// URL.

    Avoids cloning the multi-GB tachi tree which can take 20+s on slow disks
    and inflate the test wall time beyond the watchdog. The synthetic repo
    has one commit and one file — clones in <100ms.
    """
    upstream = tmp_path / "tiny-upstream"
    upstream.mkdir()
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch=main", str(upstream)],
        check=True,
        capture_output=True,
    )
    (upstream / "README.md").write_text("tiny test upstream\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(upstream), "add", "README.md"],
        check=True,
        capture_output=True,
    )
    # Set author info via env so the test doesn't depend on the user's gitconfig.
    env_git = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(
        ["git", "-C", str(upstream), "commit", "--quiet", "-m", "init"],
        check=True,
        capture_output=True,
        env=env_git,
    )
    return f"file://{upstream}"


def test_fast_clone_succeeds(tmp_path: Path) -> None:
    """A reachable clone with generous timeout completes exit 0 + no zombie.

    Uses a tiny synthetic upstream (one commit, one file) so the wall time
    is dominated by bash + git fork-exec, not the actual byte transfer.
    Verifies the watchdog does NOT trigger on a fast clone, and the bash
    script exits cleanly without a zombie watchdog process.
    """
    upstream_url = _build_tiny_upstream(tmp_path)
    destdir = tmp_path / "fetched"

    bash_script = _build_invocation(upstream_url, "main", str(destdir))

    start = time.monotonic()
    result = _run_with_timeout(
        bash_script,
        {"AOD_FETCH_TIMEOUT": "60"},
        timeout=15,
    )
    elapsed = time.monotonic() - start

    rc_line = next(
        (line for line in result.stdout.splitlines() if line.startswith("RC=")),
        None,
    )
    assert rc_line is not None, (
        f"no RC line emitted; stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    rc = int(rc_line.split("=", 1)[1])
    assert rc == 0, (
        f"fast clone returned rc {rc} (expected 0). elapsed {elapsed:.2f}s. "
        f"stderr: {result.stderr!r}"
    )
    assert destdir.is_dir(), (
        f"destdir {destdir} not created after fast clone success. "
        f"stderr: {result.stderr!r}"
    )
    # Watchdog should NOT have triggered; bash exits cleanly post-clone.
    # If the watchdog leaked a zombie sleeper, bash wouldn't exit until the
    # full timeout (60s) elapsed. We allow 10s for fork+clone+process exit.
    assert elapsed < 10, (
        f"fast clone took {elapsed:.2f}s (suspicious — the watchdog cleanup "
        f"may have leaked a zombie sleeper. Expected <10s for the synthetic "
        f"upstream + bash overhead)"
    )

    # Clean up the destdir (tmp_path will be cleaned by pytest, but explicit
    # is better for debugging).
    shutil.rmtree(destdir, ignore_errors=True)
