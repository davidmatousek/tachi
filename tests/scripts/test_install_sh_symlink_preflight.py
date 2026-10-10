"""K3 pre-flight and containment tests for `scripts/install.sh` (Feature 373).

Scope (tasks.md T008, Lane A', W1): every US-2 acceptance scenario (spec.md
US-2 #1-#12), the rev. 1 and rev. 2 (AR-1) additions, and N11, per
`contracts/installer-cli.md` Sec. "Test harness contract" and
`data-model.md` Sec. 2.

TEST-FIRST (FR-K3.6, L16): Sec. "A. Cleanup safety negatives" below was
written and run against TODAY's unmodified `scripts/install.sh` FIRST, and
that red run is recorded in
`specs/373-adopter-install-output-fidelity/test-results/k3-test-first.md`
before any other case in this file was written. `scripts/install.sh` itself
is untouched by this task -- DEVOPS-K3 (T009) implements the pre-flight
against this suite next.

Every assertion in this module checks ONLY installer-authored text (the
`Messages` and `Exit codes` sections of `contracts/installer-cli.md`, with
the always-refused wording per PM ruling P-11.1), never `cp`/`readlink`
error wording, which differs between BSD and GNU userlands.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from install_sh_helpers import (
    DEPRECATED_COMMANDS,
    WORKING_TREE_INSTALL_SH,
    add_case_variant_symlink_to_source_clone,
    add_dangling_deprecated_command_link,
    add_dangling_symlink,
    add_looping_symlink,
    add_nested_symlink,
    add_symlink,
    add_symlink_into_source_clone,
    add_symlink_to_source_clone_parent,
    add_wrong_type_symlink,
    assert_no_tree_changes,
    build_project_tree,
    build_source_tree,
    build_symlink_chain,
    case_variant_path,
    copy_working_tree_install_sh,
    filesystem_is_case_sensitive,
    run_install_sh,
    snapshot_path,
    snapshot_tree,
    vendor_source_tree_inside_project,
)

# ---------------------------------------------------------------------------
# Shared setup
# ---------------------------------------------------------------------------


def _standard_setup(tmp_path: Path) -> tuple[Path, Path]:
    """A synthetic tachi source clone (default manifest) plus an empty
    target project, install.sh copied in from the working tree.

    Returns (source_root, project_root).
    """
    source_root = tmp_path / "tachi-src"
    project_root = tmp_path / "project"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)
    build_project_tree(project_root)
    return source_root, project_root


def _run(source_root: Path, project_root: Path, *extra_args: str, **kwargs):
    script = source_root / "scripts" / "install.sh"
    return run_install_sh(
        script, cwd=project_root, args=("--source", str(source_root), *extra_args), **kwargs
    )


# ---------------------------------------------------------------------------
# A. Cleanup safety negatives -- WRITTEN AND RUN FIRST (FR-K3.6, L16; US-2 #8
# and the rev. 1 dangling-deprecated-command-link case). The evidence that
# these are red against today's installer is a recorded run, not a red
# commit (L16) -- see k3-test-first.md.
# ---------------------------------------------------------------------------


def test_ancestor_link_over_deprecated_commands_refused_without_flag(tmp_path):
    """US-2 #8, part 1: `.claude/commands` (ancestor of both a manifest file
    entry and all five deprecated-command cleanup paths) symlinked to a
    shared folder holding a real file with a deprecated tachi command name.
    Without --follow-symlinks: refused, nothing written, and the shared
    file survives untouched."""
    source_root, project_root = _standard_setup(tmp_path)
    shared = tmp_path / "shared-commands"
    shared.mkdir()
    sentinel = "SHARED CONTENT SENTINEL -- not tachi's, must survive\n"
    shared_file = shared / DEPRECATED_COMMANDS[0].rsplit("/", 1)[-1]  # threat-model.md
    shared_file.write_text(sentinel, encoding="utf-8")
    add_symlink(project_root, ".claude/commands", shared)

    before_project = snapshot_tree(project_root)
    before_shared = snapshot_tree(shared)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert "--follow-symlinks" in result.combined
    assert shared_file.read_text(encoding="utf-8") == sentinel, "shared file must survive"
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_shared, snapshot_tree(shared), label="shared folder")


def test_ancestor_link_over_deprecated_commands_skipped_with_flag(tmp_path):
    """US-2 #8, part 2: the same shared-folder link, WITH the flag. The
    manifest's own file entry under the same ancestor installs through the
    link, but cleanup for the deprecated file is skipped (never deleted),
    and the shared file survives."""
    source_root, project_root = _standard_setup(tmp_path)
    shared = tmp_path / "shared-commands"
    shared.mkdir()
    sentinel = "SHARED CONTENT SENTINEL -- not tachi's, must survive\n"
    shared_file = shared / DEPRECATED_COMMANDS[0].rsplit("/", 1)[-1]
    shared_file.write_text(sentinel, encoding="utf-8")
    add_symlink(project_root, ".claude/commands", shared)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined
    out = result.combined.lower()
    assert "skipped" in out
    assert shared_file.read_text(encoding="utf-8") == sentinel, "shared file must survive"
    # The manifest's own file entry (tachi.example.md) is a distinct path
    # under the same linked ancestor -- with the flag, copies ARE followed.
    assert (shared / "tachi.example.md").exists()


def test_dangling_deprecated_command_link_refused_without_flag(tmp_path):
    """Rev. 1 case: one deprecated-command file is ITSELF a dangling link
    (no ancestor link involved -- origins == {cleanup-file} exactly).
    Without the flag: refused, and the dangling link itself is untouched."""
    source_root, project_root = _standard_setup(tmp_path)
    add_dangling_deprecated_command_link(project_root)
    dep_path = project_root / DEPRECATED_COMMANDS[0]
    before = snapshot_path(dep_path)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    after = snapshot_path(dep_path)
    assert after == before, "the dangling link itself must be untouched"
    assert dep_path.is_symlink()


def test_dangling_deprecated_command_link_skipped_with_flag(tmp_path):
    """Rev. 1 case, with the flag: the dangling deprecated-command link is
    skipped (listed as skipped), never deleted, and the install otherwise
    succeeds."""
    source_root, project_root = _standard_setup(tmp_path)
    add_dangling_deprecated_command_link(project_root)
    dep_path = project_root / DEPRECATED_COMMANDS[0]
    before = snapshot_path(dep_path)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined
    assert "skipped" in result.combined.lower()
    after = snapshot_path(dep_path)
    assert after == before, "the dangling link must never be deleted, flag or not"
    assert dep_path.is_symlink()


# ---------------------------------------------------------------------------
# B. Basic refusal / opt-in: a manifest DIRECTORY entry's own destination is
# a symlink (US-2 #1, #2).
# ---------------------------------------------------------------------------


def test_directory_entry_symlink_refused_without_flag(tmp_path):
    """US-2 #1: `.claude/skills/tachi-example` (a directory entry) is a
    symlink to a folder outside the project. Refused, names the component
    and resolved destination plus inside/outside, states nothing was
    written, names both remedies, and writes/deletes zero files anywhere."""
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "agents-skills"
    outside_target.mkdir()
    add_symlink(project_root, ".claude/skills/tachi-example", outside_target)
    before_project = snapshot_tree(project_root)
    before_target = snapshot_tree(outside_target)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert ".claude/skills/tachi-example" in out
    assert str(outside_target) in out or os.path.realpath(outside_target) in out
    assert "outside project" in out
    assert "Nothing was written" in out
    assert "--follow-symlinks" in out
    assert "real directory" in out or "real directory or file" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_target, snapshot_tree(outside_target), label="link target")


def test_directory_entry_symlink_installs_with_flag(tmp_path):
    """US-2 #2: the same link, WITH the flag. Installs, naming the resolved
    destination before copying and again in the summary; the entry's
    content actually lands at the resolved (outside) location."""
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "agents-skills"
    outside_target.mkdir()
    add_symlink(project_root, ".claude/skills/tachi-example", outside_target)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined
    out = result.combined
    assert "Following symlinked destination(s)" in out
    assert "Installed through symlink(s):" in out
    assert ".claude/skills/tachi-example" in out
    assert (outside_target / "PLACEHOLDER.md").exists(), "copy must land at the resolved destination"


# ---------------------------------------------------------------------------
# C. A single-file destination's PARENT directory is a symlink (US-2 #3).
# ---------------------------------------------------------------------------


def test_ancestor_of_file_entry_refused_without_flag(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "shared-scripts"
    outside_target.mkdir()
    add_symlink(project_root, "scripts", outside_target)
    before_project = snapshot_tree(project_root)
    before_target = snapshot_tree(outside_target)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_target, snapshot_tree(outside_target), label="link target")


def test_ancestor_of_file_entry_installs_with_flag(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "shared-scripts"
    outside_target.mkdir()
    add_symlink(project_root, "scripts", outside_target)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined
    assert "Installed through symlink(s):" in result.combined
    assert (outside_target / "example_script.py").exists()


# ---------------------------------------------------------------------------
# D. A manifest entry's destination is ITSELF a symlink -- dir and file
# entries (US-2 #4). (The directory-entry variant is already covered by
# Group B; this group adds the FILE-entry variant.)
# ---------------------------------------------------------------------------


def test_file_entry_symlink_refused_without_flag(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)
    outside_file = tmp_path / "shared-example-script.py"
    outside_file.write_text("shared\n", encoding="utf-8")
    add_symlink(project_root, "scripts/example_script.py", outside_file, target_is_dir=False)
    before = snapshot_path(outside_file)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert snapshot_path(outside_file) == before


def test_file_entry_symlink_installs_with_flag(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)
    outside_file = tmp_path / "shared-example-script.py"
    outside_file.write_text("shared\n", encoding="utf-8")
    add_symlink(project_root, "scripts/example_script.py", outside_file, target_is_dir=False)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined
    assert "Installed through symlink(s):" in result.combined
    assert "Synthetic content" in outside_file.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# E. Nested links inside a directory entry's destination subtree -- ALWAYS
# refused, flag or not (US-2 #5, spec ruling S-6). The nested name must be
# one the SOURCE subtree actually contains (data-model Sec. 2: `subtree`
# origins are enumerated FROM the source's `find . -mindepth 1`), so these
# build their own source tree with an extra nested file and directory.
# ---------------------------------------------------------------------------

_NO_FLAG: tuple[str, ...] = ()
_WITH_FLAG: tuple[str, ...] = ("--follow-symlinks",)


def _setup_with_nested_subtree(tmp_path: Path) -> tuple[Path, Path]:
    source_root = tmp_path / "tachi-src"
    project_root = tmp_path / "project"
    build_source_tree(
        source_root,
        extra_files={".claude/skills/tachi-example/inner/nested-doc.md": "nested\n"},
    )
    copy_working_tree_install_sh(source_root)
    build_project_tree(project_root)
    return source_root, project_root


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_nested_symlinked_file_always_refused(tmp_path, flag_args):
    """US-2 #5: `PLACEHOLDER.md`, a name the source subtree actually
    contains, is a symlinked FILE nested inside the entry's destination.
    Refused with or without the flag; message names the nested link and
    says the copy cannot pass through it; nothing written."""
    source_root, project_root = _setup_with_nested_subtree(tmp_path)
    outside_file = tmp_path / "outside-file.md"
    outside_file.write_text("outside\n", encoding="utf-8")
    add_nested_symlink(
        project_root, ".claude/skills/tachi-example/", "PLACEHOLDER.md", outside_file
    )
    before_project = snapshot_tree(project_root)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert "cannot pass through it" in out
    assert "cannot help with these" in out, "nested links must offer no flag remedy"
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_nested_symlinked_directory_always_refused(tmp_path, flag_args):
    """US-2 #5: `inner`, a subdirectory name the source subtree actually
    contains, is a symlinked DIRECTORY nested inside the entry's
    destination. Refused with or without the flag."""
    source_root, project_root = _setup_with_nested_subtree(tmp_path)
    outside_dir = tmp_path / "outside-dir"
    outside_dir.mkdir()
    add_nested_symlink(project_root, ".claude/skills/tachi-example/", "inner", outside_dir)
    before_project = snapshot_tree(project_root)
    before_outside = snapshot_tree(outside_dir)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert "cannot pass through it" in out
    assert "cannot help with these" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_outside, snapshot_tree(outside_dir), label="outside dir")


# ---------------------------------------------------------------------------
# F. Unresolvable: dangling, looping, wrong-type -- ALWAYS refused, with the
# readlink text reported (US-2 #6).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_dangling_entry_link_always_refused(tmp_path, flag_args):
    source_root, project_root = _standard_setup(tmp_path)
    link_path = add_dangling_symlink(project_root, ".claude/skills/tachi-example/")
    readlink_text = os.readlink(link_path)
    before_project = snapshot_tree(project_root)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert readlink_text in out, "the raw readlink text must be reported for an unresolvable link"
    assert "cannot help with these" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_looping_entry_link_always_refused(tmp_path, flag_args):
    source_root, project_root = _standard_setup(tmp_path)
    add_looping_symlink(project_root, "scripts/example_script.py")
    before_project = snapshot_tree(project_root)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert "cannot help with these" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_wrong_type_link_dir_needed_always_refused(tmp_path, flag_args):
    """A directory entry's link resolves to a FILE (wrong type)."""
    source_root, project_root = _standard_setup(tmp_path)
    link_path = add_wrong_type_symlink(project_root, ".claude/skills/tachi-example/", need="dir")
    readlink_text = os.readlink(link_path)
    before_project = snapshot_tree(project_root)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert readlink_text in out
    assert "cannot help with these" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_wrong_type_link_file_needed_always_refused(tmp_path, flag_args):
    """A file entry's link resolves to a DIRECTORY (wrong type)."""
    source_root, project_root = _standard_setup(tmp_path)
    link_path = add_wrong_type_symlink(project_root, "scripts/example_script.py", need="file")
    readlink_text = os.readlink(link_path)
    before_project = snapshot_tree(project_root)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert readlink_text in out
    assert "cannot help with these" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")


@pytest.mark.parametrize(
    "hops,should_resolve",
    [(32, True), (33, False)],
    ids=["32-hops-resolves", "33-hops-unresolvable"],
)
def test_symlink_chain_hop_boundary(tmp_path, hops, should_resolve):
    """`resolve()`'s 32-hop ceiling (contracts/installer-cli.md; SEC-K3-01:
    lowered from an original 40 to the cross-platform-safe minimum of
    Darwin's MAXSYMLINKS and Linux's SYMLOOP_MAX), exercised through
    install.sh's own pre-flight rather than the bare helper: a 32-hop chain
    to a real outside directory resolves (refused as `outside`, WITH a flag
    remedy offered); a 33-hop chain is unresolvable (refused with NO flag
    remedy)."""
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "chain-target"
    outside_target.mkdir()
    build_symlink_chain(
        project_root, ".claude/skills/tachi-example", hops=hops, terminal_target=outside_target
    )

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    if should_resolve:
        assert "--follow-symlinks" in out
        assert "cannot help with these" not in out
    else:
        assert "cannot help with these" in out


def test_sec_k3_01_regression_33_hop_claude_chain_refused_with_follow_symlinks(tmp_path):
    """SEC-K3-01 regression (security-analyst T011 advisory review).

    Before the fix, `resolve()`'s ceiling (40) exceeded Darwin's real
    filesystem symlink-traversal limit (`MAXSYMLINKS` == 32, empirically
    measured: `mkdir -p` through a chain succeeds at 32 hops and fails with
    ELOOP at 33). A 33-40-hop `.claude` chain would pass the pre-flight's
    classification as `outside` (flag-eligible) and, WITH
    --follow-symlinks, proceed to the copy loop -- which then hit the real
    OS's ELOOP mid-copy and crashed, having already written an earlier,
    unrelated manifest entry first: a confirmed non-atomic partial install
    (probe3_partial.sh in the review's evidence).

    With the ceiling lowered to 32, a 33-hop `.claude` chain is now refused
    by the pre-flight itself as UNRESOLVABLE -- even WITH
    --follow-symlinks, since always-refused classes are never flag-gated
    (data-model.md Sec. 2.1) -- before the copy loop is ever reached, so
    nothing is written. This must hold on both CI legs: on Linux, the OS's
    own ELOOP ceiling (commonly 40, per SYMLOOP_MAX) would still let a
    33-hop chain resolve at the filesystem level, but the installer's OWN
    32-hop ceiling refuses it first regardless -- the fix does not depend
    on which OS is running it.
    """
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "chain-target-33"
    outside_target.mkdir()
    build_symlink_chain(project_root, ".claude", hops=33, terminal_target=outside_target)
    before_project = snapshot_tree(project_root)
    before_outside = snapshot_tree(outside_target)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert "cannot help with these" in out, (
        "a 33-hop chain must be refused as UNRESOLVABLE (no --follow-symlinks "
        "remedy offered), not merely flagged as outside-project"
    )
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_outside, snapshot_tree(outside_target), label="chain target")


def test_rc1_regression_21_plus_21_hop_linked_ancestor_chain_refused_with_follow_symlinks(tmp_path):
    """P0 RC-1 regression (architect P0 review Sec. 6(b) and Sec. 9: the
    residual of SEC-K3-01, `contracts/installer-cli.md` "The hop ceiling
    and the whole-path guard").

    `resolve()`'s 32-hop ceiling (`45bb8d6`, SEC-K3-01) bounds only ONE
    link's own chain. The real OS symlink-traversal limit (Darwin's
    `MAXSYMLINKS` == 32, Linux's `SYMLOOP_MAX`, commonly 40) instead counts
    EVERY link met while resolving a single path, linked ancestors
    included. So two chains that are each individually under the 32-hop
    ceiling can still sum past the platform limit when one is nested
    inside the other's resolved destination -- exactly what the P0 review
    reproduced on macOS with two 17-hop chains (`.claude` and, inside its
    target, `.claude/skills`).

    This test uses 21+21 (not P0's 17+17) so the combined 42-hop lookup
    deterministically exceeds BOTH Darwin's 32-hop limit AND Linux's
    40-hop limit on both CI legs -- 17+17 (34) clears Darwin's 32 but not
    Linux's 40, so it would silently pass on an Ubuntu runner. Each 21-hop
    chain alone is still comfortably under the shared 32-hop ceiling
    (`test_symlink_chain_hop_boundary` above pins that boundary
    separately), so only the new whole-path `[ -e "$p" ]` guard (P0 RC-1)
    -- not the pre-existing per-chain hop count -- can refuse this.

    Setup: `.claude` is a 21-hop chain to a real outside directory A; AT
    `A/skills` (the real place `.claude/skills` resolves through), `skills`
    is itself a 21-hop chain to a second real outside directory B.
    `scripts/example_script.py`, a plain file entry with no link anywhere
    on its own path, is listed FIRST in the manifest. Before the RC-1 fix,
    this is exactly how the bug manifested: the pre-flight's own
    `resolve()` call on each chain only ever counts that chain's OWN 21
    hops (an absolute link target decouples it from its ancestor textually
    after the first hop), so both `.claude` and `.claude/skills` pass
    pre-flight as merely `outside` the project. With `--follow-symlinks`,
    the copy loop then writes the plain entry first, and only the real
    `mkdir -p` call -- given the full, un-resolved logical path -- walks
    `.claude`'s chain and then `skills`'s chain back-to-back in one
    OS-level lookup, and crashes with ELOOP partway through
    `.claude/skills`: a non-atomic partial install.

    After RC-1, `resolve()`'s leading `[ -e "$p" ]` performs that same
    whole-path OS lookup itself (unlike `readlink`, `stat` follows the
    FINAL component too), so it fails with ELOOP on `.claude/skills`
    during the pre-flight -- before any copying starts -- and the plain
    entry is never written either.
    """
    source_root = tmp_path / "tachi-src"
    project_root = tmp_path / "project"
    build_source_tree(
        source_root,
        entries=(
            "scripts/example_script.py",
            ".claude/skills/tachi-example/",
        ),
    )
    copy_working_tree_install_sh(source_root)
    build_project_tree(project_root)

    outside_a = tmp_path / "outside-a"
    outside_a.mkdir()
    outside_b = tmp_path / "outside-b"
    outside_b.mkdir()
    build_symlink_chain(project_root, ".claude", hops=21, terminal_target=outside_a)
    skills_link = build_symlink_chain(outside_a, "skills", hops=21, terminal_target=outside_b)
    readlink_text = os.readlink(skills_link)

    before_project = snapshot_tree(project_root)
    before_a = snapshot_tree(outside_a)
    before_b = snapshot_tree(outside_b)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert "cannot help with these" in out, (
        "a 21+21-hop linked-ancestor chain must be refused as UNRESOLVABLE "
        "(no --follow-symlinks remedy offered) -- each chain alone passes "
        "the 32-hop ceiling, so only the whole-path `[ -e ]` guard (P0 "
        "RC-1) can catch the combined 42-hop lookup"
    )
    assert f".claude/skills -> '{readlink_text}'" in out, (
        "the always-refused block must name .claude/skills itself (the "
        "component whose WHOLE-PATH lookup exceeds the platform limit), "
        "with its raw readlink text -- not just .claude"
    )
    assert "[broken, looping or wrong-type link]" in out
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_a, snapshot_tree(outside_a), label="chain target A (.claude)")
    assert_no_tree_changes(before_b, snapshot_tree(outside_b), label="chain target B (.claude/skills)")


# ---------------------------------------------------------------------------
# G. Source-tree containment: destinations that resolve into the tachi
# clone, and project roots that ARE the clone or lie inside it (US-2 #7,
# spec ruling S-2, FR-K3.7), including the rev. 2 (AR-1) case-identity
# variants and N11 (the reverse direction: the clone nested inside a
# directory entry's own destination).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_link_straight_into_clone_always_refused(tmp_path, flag_args):
    source_root, project_root = _standard_setup(tmp_path)
    add_symlink_into_source_clone(project_root, ".claude/skills/tachi-example", source_root)
    before_source = snapshot_tree(source_root)

    result = _run(source_root, project_root, *flag_args)

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out
    assert "cannot help with these" in out
    assert "source clone" in out.lower() or "tachi clone" in out.lower()
    # The clone itself must never be written into, whatever the flag.
    assert_no_tree_changes(before_source, snapshot_tree(source_root), label="source clone")


@pytest.mark.parametrize("flag_args", [_NO_FLAG, _WITH_FLAG], ids=["no-flag", "with-flag"])
def test_link_to_clone_parent_always_refused(tmp_path, flag_args):
    """Reproduces the contract's own example: `templates -> ..`, where
    entry `templates/tachi/` lands back at the clone root. Requires a
    source clone literally named `tachi` (see the helper's docstring)."""
    source_root = tmp_path / "tachi"
    project_root = tmp_path / "project"
    build_source_tree(source_root, entries=("templates/tachi/",))
    copy_working_tree_install_sh(source_root)
    build_project_tree(project_root)
    add_symlink_to_source_clone_parent(project_root, "templates", source_root)
    before_source = snapshot_tree(source_root)

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(source_root), *flag_args),
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert "cannot help with these" in result.combined
    assert_no_tree_changes(before_source, snapshot_tree(source_root), label="source clone")


def test_vendored_clone_at_entry_destination_refused_without_flag(tmp_path):
    """A clone vendored (a real, non-symlink directory) AT one of its own
    manifest entries' destinations: `phys_dest` of that entry trivially
    equals the clone's own physical path, so containment fires with no
    symlink involved anywhere (data-model.md Sec. 2.2, third bullet)."""
    project_root = build_project_tree(tmp_path / "project")
    nested_source = vendor_source_tree_inside_project(
        project_root, ".claude/skills/tachi-example/"
    )
    copy_working_tree_install_sh(nested_source)

    result = run_install_sh(
        nested_source / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(nested_source)),
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert "cannot help with these" in result.combined


def test_vendored_clone_at_entry_destination_refused_with_flag(tmp_path):
    project_root = build_project_tree(tmp_path / "project")
    nested_source = vendor_source_tree_inside_project(
        project_root, ".claude/skills/tachi-example/"
    )
    copy_working_tree_install_sh(nested_source)

    result = run_install_sh(
        nested_source / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(nested_source), "--follow-symlinks"),
    )

    assert result.returncode == 1, result.combined
    assert "cannot help with these" in result.combined


def test_n11_clone_nested_inside_directory_entry_destination_refused(tmp_path):
    """N11: a tachi clone physically sitting AT A SUBTREE PATH of one of
    its own directory entries' destinations is refused -- the reverse
    containment direction from Group G's other cases (the CLONE is under
    the destination, not the destination under the clone). The always-
    refused remedy (move the clone) already covers it."""
    project_root = build_project_tree(tmp_path / "project")
    nested_source = (
        project_root / ".claude" / "skills" / "tachi-example" / "vendor" / "tachi-clone"
    )
    build_source_tree(nested_source)
    copy_working_tree_install_sh(nested_source)

    result = run_install_sh(
        nested_source / "scripts" / "install.sh",
        cwd=project_root,
        args=("--source", str(nested_source)),
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    # NOTE (handoff): contracts/installer-cli.md's Messages section does not
    # give N11's own per-line bracket text verbatim -- only the reverse-
    # direction "source-tree" line. T009's own words ("the always-refused
    # remedy already covers moving the clone") read as reusing that same
    # class/message. This assertion intentionally checks only the shape the
    # contract DOES pin (always-refused header, no flag remedy), not a
    # specific bracket phrase for this direction.


def test_project_root_is_source_clone_refused(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)

    result = run_install_sh(
        source_root / "scripts" / "install.sh", cwd=source_root, args=("--source", str(source_root))
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined


def test_project_root_inside_source_clone_refused(tmp_path):
    source_root = tmp_path / "tachi-src"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)
    nested_cwd = source_root / ".claude"

    result = run_install_sh(
        source_root / "scripts" / "install.sh", cwd=nested_cwd, args=("--source", str(source_root))
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined


def test_case_variant_link_into_clone_refused_without_flag(tmp_path):
    """Rev. 2, ruling AR-1: the link's TEXT spells the clone in a different
    case. On a case-insensitive volume this still resolves to the clone by
    identity, so containment must catch it via `[ -ef ]`, never a string
    prefix test. macOS-only; skips on a case-sensitive volume."""
    if filesystem_is_case_sensitive(tmp_path):
        pytest.skip("case-variant scenario requires a case-insensitive volume (macOS)")
    source_root, project_root = _standard_setup(tmp_path)
    add_case_variant_symlink_to_source_clone(
        project_root, ".claude/skills/tachi-example", source_root
    )

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined
    assert "cannot help with these" in result.combined


def test_case_variant_link_into_clone_refused_with_flag(tmp_path):
    if filesystem_is_case_sensitive(tmp_path):
        pytest.skip("case-variant scenario requires a case-insensitive volume (macOS)")
    source_root, project_root = _standard_setup(tmp_path)
    add_case_variant_symlink_to_source_clone(
        project_root, ".claude/skills/tachi-example", source_root
    )

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 1, result.combined
    assert "cannot help with these" in result.combined


def test_project_root_case_variant_of_clone_refused(tmp_path):
    """Rev. 2, ruling AR-1: the PROJECT root itself is reached through a
    case-variant spelling of the clone's own path (an alias of the
    self-install guard, generalized to physical identity).

    Non-vacuous requires `pwd_override` here, empirically verified while
    writing this suite: when bash starts with NO inherited `$PWD`, it
    derives one fresh via a real `getcwd()`, which -- on a case-insensitive,
    case-PRESERVING volume -- silently re-normalizes a case-variant cwd
    back to the on-disk stored case before install.sh ever sees a string to
    compare. That would make this test pass even under a naive string
    check, testing nothing. A real interactive shell carries the
    as-typed-case `$PWD` forward across `cd` and every subsequent command
    (bash trusts an inherited `$PWD` that `stat`-matches the real cwd
    instead of recomputing it) -- `pwd_override` reproduces exactly that,
    which is what actually exercises AR-1's `[ -ef ]` identity comparison
    instead of accidentally relying on kernel-level case normalization."""
    if filesystem_is_case_sensitive(tmp_path):
        pytest.skip("case-variant scenario requires a case-insensitive volume (macOS)")
    source_root = tmp_path / "tachi-src"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)
    variant_cwd = case_variant_path(source_root)

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=variant_cwd,
        args=("--source", str(source_root)),
        pwd_override=str(variant_cwd),
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined


def test_project_inside_clone_via_case_variant_path_refused(tmp_path):
    """Rev. 2, ruling AR-1, second case: a project reached through a
    case-variant path INSIDE the clone (not equal to its root). See
    `test_project_root_case_variant_of_clone_refused` for why
    `pwd_override` is required for this to be non-vacuous."""
    if filesystem_is_case_sensitive(tmp_path):
        pytest.skip("case-variant scenario requires a case-insensitive volume (macOS)")
    source_root = tmp_path / "tachi-src"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)
    nested = source_root / "nested-project"
    nested.mkdir()
    variant_cwd = case_variant_path(source_root) / "nested-project"

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=variant_cwd,
        args=("--source", str(source_root)),
        pwd_override=str(variant_cwd),
    )

    assert result.returncode == 1, result.combined
    assert "Nothing was written" in result.combined


# ---------------------------------------------------------------------------
# I. Reached through a link above the root, and an in-project link still
# classified correctly despite it (US-2 #9). Non-vacuous per the harness
# contract: cwd IS the link, $PWD is set to the logical path, and the
# ancestor link is built by the test itself (never relying on tmp_path
# happening to already sit through one).
# ---------------------------------------------------------------------------


def test_project_reached_through_ancestor_link_not_refused(tmp_path):
    real_home = tmp_path / "real-home"
    real_home.mkdir()
    link_home = tmp_path / "link-home"
    os.symlink(real_home, link_home)
    source_root = tmp_path / "tachi-src"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)
    project_root = real_home / "project"
    project_root.mkdir()
    logical_cwd = link_home / "project"

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=logical_cwd,
        args=("--source", str(source_root)),
        pwd_override=str(logical_cwd),
    )

    assert result.returncode == 0, result.combined
    assert "symlink" not in result.combined.lower()
    assert "Copied:   3 item(s)" in result.combined


def test_in_project_link_classified_inside_despite_ancestor_link(tmp_path):
    real_home = tmp_path / "real-home"
    real_home.mkdir()
    link_home = tmp_path / "link-home"
    os.symlink(real_home, link_home)
    source_root = tmp_path / "tachi-src"
    build_source_tree(source_root)
    copy_working_tree_install_sh(source_root)
    project_root = real_home / "project"
    project_root.mkdir()
    inside_target = project_root / "elsewhere-inside"
    inside_target.mkdir()
    add_symlink(project_root, ".claude/skills/tachi-example", inside_target)
    logical_cwd = link_home / "project"

    result = run_install_sh(
        source_root / "scripts" / "install.sh",
        cwd=logical_cwd,
        args=("--source", str(source_root)),
        pwd_override=str(logical_cwd),
    )

    assert result.returncode == 1, result.combined
    assert "inside project" in result.combined
    assert "outside project" not in result.combined


# ---------------------------------------------------------------------------
# J. Unchanged install, no symlinks anywhere (US-2 #10). Also the M8
# empty-checked-set regression guard: `run_install_sh` always pins
# `/bin/bash` (BASH_BIN), which IS macOS's system bash 3.2.57 on that leg,
# so this same test is what proves a no-link install doesn't crash there
# under `set -u` (an unbound-variable error from expanding an empty array).
# ---------------------------------------------------------------------------


def test_unchanged_install_no_symlinks_copies_same_files(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)

    result = _run(source_root, project_root)

    assert result.returncode == 0, result.combined
    assert "Copied:   3 item(s)" in result.combined
    assert "symlink" not in result.combined.lower()
    assert (project_root / ".claude" / "skills" / "tachi-example" / "PLACEHOLDER.md").exists()
    assert (project_root / ".claude" / "commands" / "tachi.example.md").exists()
    assert (project_root / "scripts" / "example_script.py").exists()


# ---------------------------------------------------------------------------
# K. Flag parsing (FR-K3.3): long form only, no short alias, no value.
# ---------------------------------------------------------------------------


def test_follow_symlinks_long_form_accepted(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "outside"
    outside_target.mkdir()
    add_symlink(project_root, ".claude/skills/tachi-example", outside_target)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined


def test_follow_symlinks_short_alias_rejected(tmp_path):
    """spec ruling S-1: no short alias. `-L` must NOT be accepted as a
    stand-in (today's parser's `*)` catch-all rejects any unrecognized
    option; this pins that `-L` stays unrecognized after K3 ships)."""
    source_root, project_root = _standard_setup(tmp_path)

    result = _run(source_root, project_root, "-L")

    assert result.returncode == 1
    assert "Unknown option" in result.combined


def test_follow_symlinks_with_value_rejected(tmp_path):
    """FR-K3.3: the flag takes no value. A `--follow-symlinks=...` spelling
    must not be silently accepted as the flag."""
    source_root, project_root = _standard_setup(tmp_path)

    result = _run(source_root, project_root, "--follow-symlinks=true")

    assert result.returncode == 1
    assert "Unknown option" in result.combined


# ---------------------------------------------------------------------------
# L. Report-line determinism: multiple flagged components print in
# `LC_ALL=C sort` order (contracts/installer-cli.md).
# ---------------------------------------------------------------------------


def test_multiple_refusals_sorted_deterministically(tmp_path):
    source_root, project_root = _standard_setup(tmp_path)
    outside_a = tmp_path / "outside-a"
    outside_a.mkdir()
    outside_b = tmp_path / "outside-b"
    outside_b.mkdir()
    # Link the file entry (scripts/...) FIRST so creation order is the
    # OPPOSITE of `LC_ALL=C sort` order ('.' < 's' byte-wise) -- a
    # passing assertion here can only be explained by an explicit sort,
    # never by incidental enumeration order.
    add_symlink(project_root, "scripts/example_script.py", outside_b / "f.py", target_is_dir=False)
    (outside_b / "f.py").write_text("x\n", encoding="utf-8")
    add_symlink(project_root, ".claude/skills/tachi-example", outside_a)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    stderr = result.clean_stderr
    dir_pos = stderr.find(".claude/skills/tachi-example")
    file_pos = stderr.find("scripts/example_script.py")
    assert dir_pos != -1 and file_pos != -1, stderr
    assert dir_pos < file_pos, (
        f"expected LC_ALL=C sort order ('.claude/...' before 'scripts/...'), got:\n{stderr}"
    )


# ---------------------------------------------------------------------------
# M. Help text and docs surfaces (US-2 #12, FR-K3.4).
# ---------------------------------------------------------------------------


def test_help_flag_documents_follow_symlinks_scope(tmp_path):
    source_root, _project_root = _standard_setup(tmp_path)

    result = run_install_sh(
        source_root / "scripts" / "install.sh", cwd=tmp_path, args=("--help",)
    )

    assert result.returncode == 0, result.combined
    out = result.combined
    assert "--follow-symlinks" in out
    for phrase in (
        "stops before writing anything",
        "only copies",
        "never deletes through a link",
        "broken, looping or wrong-type links",
        "nested inside an installed folder",
        "destinations inside the tachi source clone",
    ):
        assert phrase in out, f"missing from --help output: {phrase!r}\n---\n{out}"


def test_header_comment_documents_follow_symlinks_scope():
    """FR-K3.4: BOTH help surfaces document the flag -- `usage()` (checked
    above by executing `--help`) AND the top-of-file header comment, which
    is never printed by execution and so is checked by reading the
    working-tree script's own source text."""
    text = WORKING_TREE_INSTALL_SH.read_text(encoding="utf-8")
    header = text.split("set -euo pipefail", 1)[0]
    assert "--follow-symlinks" in header, (
        "the header comment block (top-of-file usage docs) must also "
        "document the flag, not just usage()"
    )


def test_release_please_markers_preserved_in_install_sh():
    """FR-K3.4: editing the help surfaces must keep the existing
    `x-release-please-version` markers intact (today: :13, :19, :43)."""
    text = WORKING_TREE_INSTALL_SH.read_text(encoding="utf-8")
    marker_lines = [line for line in text.splitlines() if "x-release-please-version" in line]
    assert len(marker_lines) == 3, (
        f"expected the 3 existing release-please markers to survive, "
        f"found {len(marker_lines)}: {marker_lines}"
    )


# ---------------------------------------------------------------------------
# N. strict_prefixes() glob-safety (SEC-K3-02, security-analyst T011 advisory
# review): a manifest entry's path segment containing a glob metacharacter
# must be treated as a literal string when the checked set's "ancestor"
# prefixes are built, never pathname-expanded against files that happen to
# exist in the target project (the installer's cwd when the pre-flight
# runs).
# ---------------------------------------------------------------------------


def test_glob_metacharacter_manifest_entry_treated_literally(tmp_path):
    """SEC-K3-02 regression: before the fix, `strict_prefixes()` split a
    manifest entry's relative path with unquoted `set -- $rel` under
    `IFS=/`, which subjects each resulting word to bash pathname expansion.
    A manifest entry whose directory segment is a glob pattern (here
    `gl*b/thing.md`, mirroring the review's `probe6_final.sh` P3
    demonstration) would silently glob-expand against files in the
    project -- if a real path like `glob` exists there (planted here as an
    unrelated symlink pointing OUTSIDE the project, so it is exactly the
    kind of destination the pre-flight would otherwise refuse), the
    corrupted checked set substitutes that decoy for the real ancestor and
    the install incorrectly refuses, citing a path with nothing to do with
    the actual manifest entry (a misdirected ancestor-containment check).

    With the fix, `gl*b` is always the literal ancestor: the decoy symlink
    is never added to the checked set, the pre-flight raises no refusal,
    and the literal `gl*b/thing.md` entry installs normally.
    """
    source_root = tmp_path / "tachi-src"
    project_root = tmp_path / "project"
    build_source_tree(source_root, entries=("gl*b/thing.md",))
    copy_working_tree_install_sh(source_root)
    build_project_tree(project_root)

    # A decoy that a buggy glob-expansion of "gl*b" would match ("gl" + "o"
    # + "b"), planted as a symlink to a real directory OUTSIDE the project
    # -- exactly the shape the pre-flight refuses when it is (wrongly)
    # pulled into the checked set as an "ancestor".
    outside_decoy = tmp_path / "outside-decoy"
    outside_decoy.mkdir()
    add_symlink(project_root, "glob", outside_decoy)
    before_decoy_link = snapshot_path(project_root / "glob")
    before_decoy_target = snapshot_tree(outside_decoy)

    result = _run(source_root, project_root)

    assert result.returncode == 0, result.combined
    out = result.combined
    assert "tachi installed successfully" in out, out
    assert "Nothing was written" not in out, (
        "no refusal should occur -- the decoy must never be pulled into "
        f"the checked set; full output:\n{out}"
    )
    # Precise (not substring-of-tmp_path-name) checks that the decoy's own
    # relpath and resolved target never appear in a classification line.
    assert "glob ->" not in out, f"decoy symlink must never be reported; full output:\n{out}"
    assert str(outside_decoy) not in out, f"decoy target must never be reported; full output:\n{out}"
    installed = project_root / "gl*b" / "thing.md"
    assert installed.exists(), "the literal glob-named entry must install normally"

    after_decoy_link = snapshot_path(project_root / "glob")
    after_decoy_target = snapshot_tree(outside_decoy)
    assert before_decoy_link == after_decoy_link, "decoy symlink must be untouched"
    assert_no_tree_changes(before_decoy_target, after_decoy_target, label="decoy target")


# ---------------------------------------------------------------------------
# O. T036 code-review regression (.aod/results/code-reviewer-373.md): H-1 and
# M-1 trace to the SAME two-line defect at install.sh's component
# classification, just above the cleanup-only check:
#   origins=$(... awk -F'\t' -v c="$component" '$1 == c {print $3}' ...)
#   comp_need=$(... awk -F'\t' -v c="$component" '$1 == c && $2 != "" {print $2; exit}')
# Written and run FIRST against the UNFIXED installer (test-first, mirroring
# Sec. "A" above) -- DEVOPS-K3 implements the ENVIRON-based fix against this
# suite next.
# ---------------------------------------------------------------------------


def test_h1_backslash_project_path_nested_link_refused_with_flag(tmp_path):
    """H-1: POSIX `awk -v var=value` escape-processes its ASSIGNED VALUE
    exactly like a string literal before use -- so when the project's
    physical path contains a `\\`, `-v c="$component"` hands awk a
    DIFFERENT string than the literal `$component` bash just built, and
    `$1 == c` never matches. `origins` and `comp_need` then come back
    EMPTY for every linked component in the checked set, which silently
    disables the nested-link check (data-model.md Sec. 2.1 class 3:
    `subtree` in origins) -- the link falls through to class 4/5
    (inside/outside) instead, which --follow-symlinks treats as safe to
    copy through. That is exactly backwards: `cp -r` cannot actually pass
    through a symlink nested inside a directory entry's own destination
    (spec ruling S-6), so this degrades a hard "always refuse, no flag
    remedy, nothing written" safety rule into a silent partial install.
    Reproduced in review scratch (`t036/probe_backslash.sh`) as a
    confirmed partial install: an unrelated plain manifest entry got
    written before `cp` aborted on the nested link mid-copy.

    This reproduces on both CI legs identically: Ubuntu's default `awk`
    is mawk, which applies the same POSIX `-v` escape processing as BSD
    awk (macOS, exercised here) and gawk -- the defect, and the
    `ENVIRON["c"]` fix, are awk-implementation-agnostic.
    """
    backslash_root = tmp_path / "back\\slash-proj"
    source_root, project_root = _setup_with_nested_subtree(backslash_root)
    outside_dir = backslash_root / "outside-dir"
    outside_dir.mkdir()
    add_nested_symlink(project_root, ".claude/skills/tachi-example/", "inner", outside_dir)
    before_project = snapshot_tree(project_root)
    before_outside = snapshot_tree(outside_dir)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 1, result.combined
    out = result.combined
    assert "Nothing was written" in out, (
        "the nested link must be refused BEFORE any copy -- a backslash in "
        f"the project path must never turn this into a partial install:\n{out}"
    )
    assert "cannot pass through it" in out
    assert "cannot help with these" in out, "a nested link must offer no --follow-symlinks remedy"
    assert_no_tree_changes(before_project, snapshot_tree(project_root), label="project")
    assert_no_tree_changes(before_outside, snapshot_tree(outside_dir), label="outside dir")
    assert not (project_root / ".claude" / "commands" / "tachi.example.md").exists(), (
        "a partial install must not write even an UNRELATED plain manifest "
        "entry once the nested link aborts the copy"
    )


def test_h1_backslash_project_path_cleanup_through_linked_ancestor_skipped_with_flag(tmp_path):
    """H-1, second reproduction: `.claude/commands` (an ANCESTOR, origin
    `cleanup-ancestor`) is linked to a shared folder holding a real file
    named like a deprecated tachi command. With the same
    backslash-in-project-path defect, `origins` for `.claude/commands`
    comes back empty, so the `*cleanup-ancestor*` case match never fires
    and the deprecated file's path is never added to SKIP_CLEANUP_FILES --
    the cleanup loop (install.sh's own unconditional `rm -f
    "$target_path"`) then deletes the user's real file THROUGH the link.
    Reproduced in review scratch (`t036/probe_backslash_cleanup.sh`) as a
    confirmed delete-through-a-link. With the fix, this must behave
    exactly like the no-backslash case (Sec. A above): the cleanup is
    listed as skipped, never deleted, and the shared file survives
    byte-identical."""
    backslash_root = tmp_path / "back\\slash-proj"
    source_root, project_root = _standard_setup(backslash_root)
    shared = tmp_path / "shared-commands"
    shared.mkdir()
    sentinel = "SHARED CONTENT SENTINEL -- not tachi's, must survive\n"
    shared_file = shared / DEPRECATED_COMMANDS[0].rsplit("/", 1)[-1]  # threat-model.md
    shared_file.write_text(sentinel, encoding="utf-8")
    add_symlink(project_root, ".claude/commands", shared)

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, result.combined
    assert "skipped" in result.combined.lower(), (
        "the cleanup under the linked ancestor must be listed as skipped, "
        f"never deleted, even with a backslash in the project path:\n{result.combined}"
    )
    assert shared_file.read_text(encoding="utf-8") == sentinel, (
        "the shared file must survive byte-identical -- it must never be "
        "deleted through the link"
    )
    assert (shared / "tachi.example.md").exists(), (
        "the manifest's own file entry under the same linked ancestor must "
        "still install through the link"
    )


def _padded_subtree_extra_files(entry: str, *, count: int = 600) -> dict[str, str]:
    """``count`` tiny placeholder files nested under a directory entry's
    own destination (data-model.md Sec. 2, `subtree` origin), so the
    pre-flight's checked set grows by one TAB-delimited line per file --
    about 130 KB at CI `tmp_path` lengths with ``count=600``, the size
    M-1's review reproduction (`t036/pipe_thresh.sh`) found reliably
    outgrows the pipe between `printf` and the classification `awk` once
    a linked ancestor is present. Sized well above the threshold (the
    review's own table showed intermittent, racy failures near it) so
    this test is deterministic, not flaky.
    """
    stem = entry.rstrip("/")
    return {f"{stem}/pad-{i:04d}.md": "x\n" for i in range(count)}


def _setup_with_padded_subtree_and_linked_claude(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A synthetic source tree whose `.claude/skills/tachi-example/`
    subtree is padded to ~600 extra files, plus a project whose `.claude`
    (an ANCESTOR of that entry, and the very FIRST line install.sh's own
    manifest loop appends to CHECKED_SET, per `strict_prefixes`) is itself
    a symlink. Returns ``(source_root, project_root, outside_claude)``.
    """
    source_root = tmp_path / "tachi-src"
    project_root = tmp_path / "project"
    build_source_tree(
        source_root, extra_files=_padded_subtree_extra_files(".claude/skills/tachi-example/")
    )
    copy_working_tree_install_sh(source_root)
    build_project_tree(project_root)
    outside_claude = tmp_path / "outside-claude"
    outside_claude.mkdir()
    add_symlink(project_root, ".claude", outside_claude)
    return source_root, project_root, outside_claude


def test_m1_oversized_checked_set_with_linked_claude_refused_without_flag(tmp_path):
    """M-1: `comp_need`'s awk exits as soon as it prints `.claude`'s own
    first matching line -- which, for a linked ANCESTOR, is the very
    first line install.sh's manifest loop ever appends to CHECKED_SET
    (`strict_prefixes` emits the shortest prefix first, for the first
    manifest entry) -- while `printf` is still writing the ~600 padded
    subtree lines that follow it into the same pipe. Once CHECKED_SET
    exceeds the pipe's capacity, the still-writing `printf` gets SIGPIPE,
    the pipeline exits 141 under `pipefail`, and `set -e` kills the
    installer with NO message at all, not even this no-flag refusal -- a
    silent, unexplained failure for any project whose checked set is
    large enough (growing every release as skills/templates/schemas are
    added). With the fix (`!n++` instead of `exit`), awk drains the rest
    of its input instead of closing the pipe early, so the refusal
    prints normally."""
    source_root, project_root, _outside_claude = _setup_with_padded_subtree_and_linked_claude(
        tmp_path
    )

    result = _run(source_root, project_root)

    assert result.returncode == 1, (
        f"must fail CLOSED with the ordinary no-flag refusal (exit 1), "
        f"never silently as exit 141 with no output: rc={result.returncode} "
        f"out={result.combined!r}"
    )
    out = result.combined
    assert out.strip(), "must never exit silently with empty output"
    assert "Nothing was written" in out
    assert "--follow-symlinks" in out
    assert ".claude ->" in out


def test_m1_oversized_checked_set_with_linked_claude_installs_with_flag(tmp_path):
    """M-1, with the flag: the same oversized checked set must let the
    pre-flight drain CHECKED_SET fully and complete the install, rather
    than exiting 141 partway through classification."""
    source_root, project_root, outside_claude = _setup_with_padded_subtree_and_linked_claude(
        tmp_path
    )

    result = _run(source_root, project_root, "--follow-symlinks")

    assert result.returncode == 0, (
        f"must complete the install, never exit 141 partway through "
        f"classification: rc={result.returncode} out={result.combined!r}"
    )
    assert "tachi installed successfully" in result.combined
    assert (outside_claude / "skills" / "tachi-example" / "pad-0000.md").exists()


def test_l1_flag_eligible_header_matches_contract_text(tmp_path):
    """L-1: the flag-eligible block's header must read EXACTLY as
    `contracts/installer-cli.md` Sec. "Messages" gives it -- `Error:
    install stopped: symlinked destination(s) found. Nothing was
    written.` -- not merely `Error: symlinked destination(s) found. ...`
    (missing the `install stopped:` stem the always-refused block already
    carries). Every earlier test in this file asserted only substrings of
    this header ("Nothing was written", "--follow-symlinks"), never the
    header phrase itself, so this drift from the contract went uncaught."""
    source_root, project_root = _standard_setup(tmp_path)
    outside_target = tmp_path / "agents-skills"
    outside_target.mkdir()
    add_symlink(project_root, ".claude/skills/tachi-example", outside_target)

    result = _run(source_root, project_root)

    assert result.returncode == 1, result.combined
    assert (
        "Error: install stopped: symlinked destination(s) found. Nothing was written."
        in result.combined
    ), result.combined
