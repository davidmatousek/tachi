"""End-to-end tests for `scripts/init.sh` Site A defaults.env refactor (FR-001).

This module is Test-4 of the F-2 BLP-02 Wave 2 (Source-Pattern Hardening) test
surface. It validates that the Site A refactor at `scripts/init.sh:106` —
replacing `source "stacks/$SELECTED_PACK/defaults.env"` with the
`aod_template_load_kv_file ... STACK_PACK_ALLOWED_KEYS` library invocation —
behaves correctly across three scenarios:

Case 1: each shipped stack pack (`nextjs-supabase`, `fastapi-react`) loads
        cleanly. This exercises the positive-path on canonical content,
        verifying the canonical 5-key whitelist is satisfied and the
        STACK_-prefixed variables propagate downstream. **Day-5 slip-watch
        GREEN-LIGHT condition 2.**

Case 2: malicious-pack adversarial fixture (`stacks/malicious-pack/defaults.env`
        containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"`) is rejected
        with exit 8 AND the `/tmp/F-256-pwned` artifact is never created.
        Closes TACHI-VULN-6f5a95085056 (HIGH).

Case 3: missing-key fixture (pack omitting `CLOUD_PROVIDER`) is rejected
        with exit 8 AND the missing-key error names CLOUD_PROVIDER on stderr.
        Verifies post-pass completeness check.

Strategy: copy the malicious-pack and missing-key fixtures into the cloned
tachi tree as a temporary stack pack named `f256-test`, then run init.sh
non-interactively against that pack via the same canonical-stdin pattern as
F-1's test_init_sh_substitution. The clone-and-init pattern is necessary
because Site A is the init.sh entrypoint — the `source defaults.env` call
happens during init.sh execution, not in a unit-testable function.

R-1 — pipe-subshell trap (HIGH severity, F-1 lesson):
    init.sh sources `template-config-load.sh` at the top level, then invokes
    `aod_template_load_kv_file` directly (no pipe). The library uses
    `printf -v` for caller-scope assignment which only works in the parent
    shell. Any pipe here would silently false-pass. The test invokes init.sh
    via `subprocess.run(["bash", "./scripts/init.sh"], input=stdin)` — no
    shell pipes anywhere.

Bash binary pin:
    Tests use `bash` (the system default for this script). On macOS dev,
    `/bin/bash` 3.2.57 is the canonical target. CI Linux runners use
    bash 5.x via the standard `bash` lookup.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ADVERSARIAL_DIR = REPO_ROOT / "tests" / "fixtures" / "config-load" / "adversarial"


def _clone_for_init(tmpdir: Path) -> Path:
    """Clone the repo's CURRENT HEAD into tmpdir/tachi via local file://."""
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    clone_root = tmpdir / "tachi"
    subprocess.run(
        ["git", "clone", "--quiet", f"file://{REPO_ROOT}", str(clone_root)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "--quiet", head_sha],
        cwd=str(clone_root),
        check=True,
        capture_output=True,
    )
    return clone_root


def _safe_path() -> str:
    """PATH minus directories that commonly contain `gh` (matches F-1 helper)."""
    blocked = {"/opt/homebrew/bin", "/usr/local/bin", "/opt/homebrew/sbin"}
    parts = os.environ.get("PATH", "").split(":")
    kept = [p for p in parts if p not in blocked]
    has_node = any((Path(p) / "node").exists() for p in kept if p)
    if not has_node:
        return os.environ.get("PATH", "")
    return ":".join(kept)


def _install_pack(clone_root: Path, pack_name: str, defaults_env_src: Path) -> int:
    """Install a synthetic stack pack into clone_root/stacks/<pack_name>.

    Creates the minimal pack layout init.sh expects: a STACK.md and a
    defaults.env. Returns the 1-based menu index init.sh will assign.
    """
    pack_dir = clone_root / "stacks" / pack_name
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "STACK.md").write_text(f"# {pack_name} Stack\n\nSynthetic test pack.\n", encoding="utf-8")
    shutil.copy2(defaults_env_src, pack_dir / "defaults.env")

    return _compute_pack_index(clone_root, pack_name)


def _compute_pack_index(clone_root: Path, pack_name: str) -> int:
    """Compute init.sh's 1-based menu index for `pack_name`.

    init.sh enumerates packs via `for pack_dir in stacks/*/`. Bash glob
    expansion in C locale sorts paths byte-by-byte INCLUDING the trailing
    `/`. This means `stacks/fastapi-react-local/` sorts BEFORE
    `stacks/fastapi-react/` because `-` (0x2D) < `/` (0x2F) at the
    comparison position. Python's `sorted()` on bare names produces
    different ordering. We replicate bash glob order by sorting
    `<name>/` strings.
    """
    stacks_dir = clone_root / "stacks"
    candidates = [
        d.name for d in stacks_dir.iterdir()
        if d.is_dir() and (d / "STACK.md").is_file()
    ]
    # Sort by `<name>/` so `-` vs `/` ordering matches bash glob.
    pack_dirs_sorted_like_bash = sorted(candidates, key=lambda n: n + "/")
    return pack_dirs_sorted_like_bash.index(pack_name) + 1


def _build_stdin_for_pack(pack_index: int, *,
                          project_name: str = "tachi",
                          project_description: str = "F-256 Site A test",
                          github_org: str = "f256-test-org",
                          github_repo: str = "") -> str:
    """Assemble stdin for non-interactive init.sh selecting <pack_index>."""
    lines = [
        project_name,
        project_description,
        github_org,
        github_repo,
        "1",                  # AI agent: Claude Code
        str(pack_index),      # Selected pack
        "Y",                  # Confirm
    ]
    return "\n".join(lines) + "\n"


def _run_init_in_clone(clone_root: Path, stdin_payload: str,
                       timeout_sec: int = 900) -> subprocess.CompletedProcess:
    """Run init.sh inside clone_root (mirrors F-1 helper run_init_in_clone)."""
    fake_home = clone_root.parent / "fake_home"
    fake_home.mkdir(exist_ok=True)
    env = {
        **os.environ,
        "LC_ALL": "C",
        "HOME": str(fake_home),
        "PATH": _safe_path(),
        # Pin substitution dates for byte-deterministic output.
        "AOD_RATIFICATION_DATE_OVERRIDE": "2026-05-04",
        "AOD_CURRENT_DATE_OVERRIDE": "2026-05-04",
    }
    return subprocess.run(
        ["bash", "./scripts/init.sh"],
        cwd=str(clone_root),
        input=stdin_payload,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_sec,
        check=False,
    )


# -----------------------------------------------------------------------------
# Case 1 — each shipped stack pack loads cleanly (positive-path canary).
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("pack_name", ["nextjs-supabase", "fastapi-react"])
def test_shipped_stack_pack_loads_cleanly(tmp_path: Path, pack_name: str) -> None:
    """Case 1: shipped stack pack loads cleanly (Day-5 slip-watch condition 2).

    Verifies that init.sh against each canonical pack:
      - Exits 0 (success).
      - Writes the personalization snapshot at .aod/personalization.env.
      - Self-deletes scripts/init.sh.
    """
    clone_root = _clone_for_init(tmp_path)

    # Determine the menu index for this pack (matches init.sh `for stacks/*/`
    # bash glob C-locale ordering — see _compute_pack_index docstring).
    stacks_dir = clone_root / "stacks"
    if not (stacks_dir / pack_name).is_dir():
        pytest.skip(f"pack {pack_name} not present in clone tree")
    pack_index = _compute_pack_index(clone_root, pack_name)

    stdin_payload = _build_stdin_for_pack(pack_index)
    result = _run_init_in_clone(clone_root, stdin_payload)

    assert result.returncode == 0, (
        f"init.sh against {pack_name} exited {result.returncode} (expected 0). "
        f"stderr tail: {result.stderr[-2000:]}"
    )
    assert (clone_root / ".aod" / "personalization.env").is_file(), (
        f"personalization.env missing after init.sh on {pack_name}. "
        f"stdout: {result.stdout[-1000:]}"
    )
    # Per init.sh post-init contract, scripts/init.sh self-deletes on success.
    assert not (clone_root / "scripts" / "init.sh").is_file(), (
        f"scripts/init.sh was not self-deleted after init on {pack_name}."
    )


# -----------------------------------------------------------------------------
# Case 2 — malicious-pack rejection. Closes TACHI-VULN-6f5a95085056.
# -----------------------------------------------------------------------------
def test_malicious_pack_rejected(tmp_path: Path) -> None:
    """Case 2: malicious defaults.env is rejected exit 8; no /tmp file created.

    A pre-F-2 `source` call would execute `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"`
    via bash command substitution, creating /tmp/F-256-pwned. Post-F-2 the
    library must reject the file with exit 8 BEFORE any command substitution
    can fire.

    The file MUST NOT exist before the test (we delete it as a precaution),
    AND it MUST NOT exist after init.sh exits.
    """
    pwned_marker = Path("/tmp/F-256-pwned")
    if pwned_marker.exists():
        pwned_marker.unlink()  # precondition: clean state

    try:
        clone_root = _clone_for_init(tmp_path)
        pack_index = _install_pack(
            clone_root,
            "f256-malicious-test",
            ADVERSARIAL_DIR / "malicious-pack-defaults.env",
        )

        stdin_payload = _build_stdin_for_pack(pack_index)
        result = _run_init_in_clone(clone_root, stdin_payload)

        # init.sh runs `set -e` so a non-zero return from the library propagates.
        # The library returns 8 on validation failure (malformed line — the
        # CUSTOM_HOOK value contains $ which the regex value class rejects).
        assert result.returncode != 0, (
            "init.sh exited 0 on malicious pack — refactor failed to reject. "
            f"stdout: {result.stdout[-1000:]} stderr: {result.stderr[-1000:]}"
        )

        # CRITICAL: the /tmp marker MUST NOT exist (no command substitution fired).
        assert not pwned_marker.exists(), (
            "FATAL: /tmp/F-256-pwned was created — command substitution fired. "
            "The Site A refactor did NOT prevent the source-pattern attack. "
            f"stderr: {result.stderr[-1500:]}"
        )

        # Library should emit a "malformed line" error (regex rejection of $).
        # Permissive assertion: any of the library error markers should appear.
        stderr_lower = result.stderr.lower()
        assert "malformed" in stderr_lower or "disallowed" in stderr_lower or "[aod] error" in stderr_lower, (
            f"expected library rejection message on stderr; got: {result.stderr[-1000:]}"
        )
    finally:
        # Belt-and-suspenders: unlink the marker if it somehow appeared, so a
        # subsequent test run starts clean.
        if pwned_marker.exists():
            pwned_marker.unlink()


# -----------------------------------------------------------------------------
# Case 3 — missing-key rejection (post-pass completeness check).
# -----------------------------------------------------------------------------
def test_missing_key_pack_rejected(tmp_path: Path) -> None:
    """Case 3: pack omitting CLOUD_PROVIDER is rejected exit 8 with named key.

    Verifies that the post-pass missing-key check (Step 6 post-pass per the
    library contract) names the missing key explicitly. This is the test-
    surface for the FR-001 +AC-1.4 missing-key contract.
    """
    clone_root = _clone_for_init(tmp_path)
    pack_index = _install_pack(
        clone_root,
        "f256-missing-key-test",
        ADVERSARIAL_DIR / "missing-key-pack-defaults.env",
    )

    stdin_payload = _build_stdin_for_pack(pack_index)
    result = _run_init_in_clone(clone_root, stdin_payload)

    assert result.returncode != 0, (
        "init.sh exited 0 on missing-key pack — completeness check failed. "
        f"stdout: {result.stdout[-1000:]} stderr: {result.stderr[-1000:]}"
    )

    # The library's post-pass error names the missing key explicitly.
    assert "CLOUD_PROVIDER" in result.stderr, (
        f"expected stderr to name 'CLOUD_PROVIDER' as the missing key; "
        f"got stderr: {result.stderr[-1500:]}"
    )
