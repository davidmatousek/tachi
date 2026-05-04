"""Test-5': `scripts/init.sh` self-deletes after a successful run.

Per F-248 §Regression Protection Plan (Architect M-3 + Team-Lead Q-3
Option b), this test replaces the original Test-5 (re-init parity) which
became unnecessary once Q-3 Option b adjudicated re-init as NOT supported.
The new contract is: init.sh must self-delete itself after a successful
run, AND the pre-flight check at the top of init.sh must reject re-init
attempts (separate test).

This test asserts the existing self-delete at scripts/init.sh:354 still
fires post-F-1. It is a regression-protection test: pre-F-1 it already
passes. Its job is to catch any future change to init.sh that
inadvertently removes the self-delete (e.g., during the refactor in
T015–T021).
"""

from __future__ import annotations

# `init_run` is provided by conftest.py at session scope — see that fixture's
# docstring for the rationale (one shared init.sh invocation across all
# test_init_sh_* modules to avoid multiplying macos cold-cache cost).


def test_init_sh_does_not_exist_after_success(init_run):
    """`scripts/init.sh` is gone after a successful canonical run."""
    clone_root = init_run.tmpdir
    init_path = clone_root / "scripts" / "init.sh"
    assert not init_path.exists(), (
        f"init.sh did not self-delete; the file at {init_path} still exists. "
        "Self-delete is the hard re-init prevention (Q-3 Option b)."
    )


def test_personalization_snapshot_persists_after_init(init_run):
    """`.aod/personalization.env` MUST persist (it is the re-init signal)."""
    clone_root = init_run.tmpdir
    env_file = clone_root / ".aod" / "personalization.env"
    assert env_file.is_file(), (
        f".aod/personalization.env missing after init: {env_file}. "
        "This file is the soft re-init guard read by the post-F-1 pre-flight check."
    )


def test_aod_kit_version_persists_after_init(init_run):
    """`.aod/aod-kit-version` MUST persist (the version pin survives self-delete)."""
    clone_root = init_run.tmpdir
    version_file = clone_root / ".aod" / "aod-kit-version"
    assert version_file.is_file(), (
        f".aod/aod-kit-version missing after init: {version_file}. "
        "Version pin is required for /aod.update to function."
    )
