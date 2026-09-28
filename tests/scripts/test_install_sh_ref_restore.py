"""`--version` ref-restore tests for `scripts/install.sh` (Feature 373, K3).

Scope (tasks.md T008, Lane A', W1): FR-K3.5 / PD-11 -- the source repo is
always back on its original ref after a `--version` install, whatever the
outcome (success, failure or refusal), and a failed restore warns without
ever changing the run's exit status. Built on the throwaway-repo and
forced-checkout-failure-shim harness in `tests/scripts/install_sh_helpers.py`
(contracts/installer-cli.md Sec. "Test harness contract").

Every throwaway repo here is hermetic (`GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, explicit commit identity) and none of it ever
touches the live tachi checkout.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from install_sh_helpers import (
    GIT_SHIM_FAIL_REF_ENV,
    GIT_SHIM_REAL_GIT_ENV,
    add_symlink,
    build_forced_checkout_failure_git_shim,
    build_project_tree,
    build_version_tagged_source_repo,
    current_ref,
    detach_head,
    run_install_sh,
)

TAG = "v0.0.1-test"


def _run_version(source_root: Path, project_root: Path, *extra_args: str, **kwargs):
    return run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(source_root), "--version", TAG, *extra_args),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Harness self-check: the version-repo builder itself satisfies the
# contract ("install.sh is identical in both [tag and HEAD]"). A broken
# harness would silently invalidate every test below it.
# ---------------------------------------------------------------------------


def test_harness_keeps_install_sh_identical_at_tag_and_head(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    head_text = (source_root / "scripts" / "install.sh").read_text(encoding="utf-8")

    original_ref = current_ref(source_root)
    project_root = build_project_tree(tmp_path / "project")
    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(source_root), "--version", TAG),
    )
    assert result.returncode == 0, result.combined
    tagged_text = (source_root / "scripts" / "install.sh").read_text(encoding="utf-8")
    assert tagged_text == head_text, "install.sh must be byte-identical at the tag and at HEAD"
    assert current_ref(source_root) == original_ref, "must already be back on the original ref"


# ---------------------------------------------------------------------------
# Success path: ref restored after a completed --version install (US-2 #11).
# ---------------------------------------------------------------------------


def test_ref_restored_after_successful_version_install_on_branch(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    original_ref = current_ref(source_root)
    assert original_ref != "HEAD"  # sanity: really is a branch name
    project_root = build_project_tree(tmp_path / "project")

    result = _run_version(source_root, project_root)

    assert result.returncode == 0, result.combined
    assert current_ref(source_root) == original_ref


def test_ref_restored_after_successful_version_install_detached_head(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    original_sha = detach_head(source_root)
    assert current_ref(source_root) == original_sha
    project_root = build_project_tree(tmp_path / "project")

    result = _run_version(source_root, project_root)

    assert result.returncode == 0, result.combined
    assert current_ref(source_root) == original_sha


# ---------------------------------------------------------------------------
# Failure path: a tagged manifest entry with no real backing file makes the
# copy loop hit COPY_FAIL (exit 1 via the final "Failed: N item(s)" branch,
# never a die()). Ref must still be restored (US-2 #11).
# ---------------------------------------------------------------------------


def test_ref_restored_after_copy_failure(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(
        source_root,
        tag=TAG,
        remove_from_tagged=("scripts/example_script.py",),
    )
    original_ref = current_ref(source_root)
    project_root = build_project_tree(tmp_path / "project")

    result = _run_version(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Failed:" in result.combined
    assert current_ref(source_root) == original_ref


# ---------------------------------------------------------------------------
# Refusal path: a K3 symlink refusal combined with --version. Depends on
# T009's not-yet-implemented pre-flight, so this is expected to be RED
# against today's installer (today's script has no such refusal at all --
# it would silently write through the link and exit 0). Recorded as such.
# ---------------------------------------------------------------------------


def test_ref_restored_after_symlink_refusal_with_version(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    original_ref = current_ref(source_root)
    project_root = build_project_tree(tmp_path / "project")
    outside_target = tmp_path / "outside-target"
    outside_target.mkdir()
    add_symlink(project_root, ".claude/skills/tachi-example", outside_target)

    result = _run_version(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert current_ref(source_root) == original_ref


# ---------------------------------------------------------------------------
# A refusal that already exists TODAY (an invalid --version tag), so the
# ref-restore half of this test is meaningful even pre-K3.
# ---------------------------------------------------------------------------


def test_ref_restored_after_invalid_version_tag(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    original_ref = current_ref(source_root)
    project_root = build_project_tree(tmp_path / "project")

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(source_root), "--version", "v9.9.9-does-not-exist"),
    )

    assert result.returncode == 1, result.combined
    assert "Invalid version tag" in result.combined
    assert current_ref(source_root) == original_ref


# ---------------------------------------------------------------------------
# Forced restore failure: warns on stderr, names the ref and the exact
# restore command, and never changes the run's exit status (US-2 #11).
# ---------------------------------------------------------------------------


def test_forced_restore_failure_warns_and_preserves_success_exit_code(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    original_ref = current_ref(source_root)
    project_root = build_project_tree(tmp_path / "project")
    real_git = shutil.which("git")
    assert real_git is not None
    shim_dir = build_forced_checkout_failure_git_shim(tmp_path / "shim")

    result = _run_version(
        source_root,
        project_root,
        path_prepend=(shim_dir,),
        extra_env={
            GIT_SHIM_REAL_GIT_ENV: real_git,
            GIT_SHIM_FAIL_REF_ENV: original_ref,
        },
    )

    assert result.returncode == 0, (
        "a failed restore must never change the run's exit status"
        f"\n---\n{result.combined}"
    )
    stderr = result.clean_stderr
    assert "Warning: could not restore the tachi source repo to its original ref" in stderr
    assert f"'{original_ref}'" in stderr
    assert f"git -C '{source_root}' checkout '{original_ref}'" in stderr


def test_forced_restore_failure_warns_and_preserves_refusal_exit_code(tmp_path):
    """Same forced failure, but on top of the (already-existing-today)
    invalid-tag refusal path, so the warning mechanic is isolated from K3."""
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    original_ref = current_ref(source_root)
    project_root = build_project_tree(tmp_path / "project")
    real_git = shutil.which("git")
    assert real_git is not None
    shim_dir = build_forced_checkout_failure_git_shim(tmp_path / "shim")

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(source_root), "--version", "v9.9.9-does-not-exist"),
        path_prepend=(shim_dir,),
        extra_env={
            GIT_SHIM_REAL_GIT_ENV: real_git,
            GIT_SHIM_FAIL_REF_ENV: original_ref,
        },
    )

    assert result.returncode == 1, result.combined
    assert "Invalid version tag" in result.combined
    stderr = result.clean_stderr
    assert "Warning: could not restore the tachi source repo to its original ref" in stderr
    assert f"'{original_ref}'" in stderr


def test_successful_restore_prints_no_warning(tmp_path):
    """Positive control: with the shim in place but its fail-ref selector
    unset (empty), every git call -- including the real restore checkout --
    passes through untouched, and no warning is ever printed."""
    source_root = tmp_path / "tachi-src"
    build_version_tagged_source_repo(source_root, tag=TAG)
    project_root = build_project_tree(tmp_path / "project")
    real_git = shutil.which("git")
    assert real_git is not None
    shim_dir = build_forced_checkout_failure_git_shim(tmp_path / "shim")

    result = _run_version(
        source_root,
        project_root,
        path_prepend=(shim_dir,),
        extra_env={GIT_SHIM_REAL_GIT_ENV: real_git, GIT_SHIM_FAIL_REF_ENV: ""},
    )

    assert result.returncode == 0, result.combined
    assert "Warning" not in result.clean_stderr
    assert "could not restore" not in result.clean_stderr
