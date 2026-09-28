"""Symlink sandbox builders for `scripts/install.sh` tests (Feature 373, K3).

Scope (tasks.md T003): this module holds only the BUILDERS that construct
synthetic project ("target") and source ("tachi clone") directory trees at
test time, inside a caller-given ``tmp_path``. It covers every symlink class
the K3 pre-flight (`contracts/installer-cli.md` Sec. "Pre-flight algorithm",
data-model.md Sec. 2) needs a fixture for.

Out of scope, added later by Lane A' (tasks.md T008, W1): the harness
RUNNER — pinning `/bin/bash`, stripping ANSI codes, the `/bin/sh` git shim
for the forced ref-restore failure, before/after tree snapshots, and the
throwaway `--version` git repos. Those consume the trees this module builds;
they do not belong here.

Hard constraints (tasks.md T003 standing rules):
- stdlib only, importable with no side effects;
- no ``test_`` functions and no pytest collection here;
- every symlink this module creates lives under a path the CALLER supplies
  (normally a pytest ``tmp_path``) — nothing here ever touches the repo.

Self-check: run this file's functions from a scratch tmp dir with plain
python3 (not pytest, and never against the main tree) — see the fixture
README for the exact recipe used to validate this module.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

__all__ = [
    "DEPRECATED_COMMANDS",
    "MANIFEST_BEGIN_MARKER",
    "MANIFEST_END_MARKER",
    "DEFAULT_MANIFEST_ENTRIES",
    "make_symlink",
    "build_source_tree",
    "build_project_tree",
    "add_symlink",
    "add_nested_symlink",
    "add_dangling_symlink",
    "add_looping_symlink",
    "build_symlink_chain",
    "add_wrong_type_symlink",
    "add_symlink_into_source_clone",
    "add_symlink_to_source_clone_parent",
    "filesystem_is_case_sensitive",
    "case_variant_path",
    "add_case_variant_symlink_to_source_clone",
    "vendor_source_tree_inside_project",
    "add_dangling_deprecated_command_link",
]

# Mirrors scripts/install.sh's own DEPRECATED_COMMANDS array verbatim (the
# five pre-namespace command files a target project may still have lying
# around from a tachi <5.0 install). Kept as a tuple of relative paths, same
# spelling and order as install.sh, so tests can index into it by name
# instead of a magic number.
DEPRECATED_COMMANDS = (
    ".claude/commands/threat-model.md",
    ".claude/commands/risk-score.md",
    ".claude/commands/compensating-controls.md",
    ".claude/commands/infographic.md",
    ".claude/commands/security-report.md",
)

# Mirrors install.sh's parse_manifest() markers exactly (string equality,
# not a regex -- data-model.md Sec. 1).
MANIFEST_BEGIN_MARKER = "<!-- BEGIN MANIFEST -->"
MANIFEST_END_MARKER = "<!-- END MANIFEST -->"

# A small, self-contained manifest: one directory entry and one file entry.
# Deliberately NOT the real tachi manifest (that's ~220 checked paths per
# contracts/installer-cli.md) -- these builders exist to make synthetic,
# fast, deterministic sources, not to replay production content.
DEFAULT_MANIFEST_ENTRIES = (
    ".claude/skills/tachi-example/",
    ".claude/commands/tachi.example.md",
    "scripts/example_script.py",
)


# ---------------------------------------------------------------------------
# Low-level primitive
# ---------------------------------------------------------------------------


def make_symlink(link_path: Path, target: Path, *, relative: bool = False) -> Path:
    """Create (or replace) a symlink at ``link_path`` pointing at ``target``.

    Creates ``link_path``'s parent directories first. Removes anything
    already at ``link_path`` (file, dir, or another link) before linking, so
    callers can layer scenarios onto an already-populated project tree.
    ``target`` need not exist -- callers build dangling links this way.

    Args:
        link_path: absolute path where the symlink is created.
        target: absolute path the link should point at (or, with
            ``relative=True``, a path to render relative to ``link_path``'s
            parent directory before writing it into the link).
        relative: write a relative link (as ``os.symlink`` would with a
            relative ``target`` argument) instead of an absolute one.
            Default is ``False`` -- bash's ``resolve()`` in
            contracts/installer-cli.md handles both forms, but an absolute
            link is easier to reason about across fixtures moved between
            tmp dirs.

    Returns:
        ``link_path``, for chaining.
    """
    link_path = Path(link_path)
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() or link_path.exists():
        if link_path.is_dir() and not link_path.is_symlink():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()

    if relative:
        target_text = os.path.relpath(Path(target), start=link_path.parent)
    else:
        target_text = str(target)

    os.symlink(target_text, link_path)
    return link_path


# ---------------------------------------------------------------------------
# Tree builders
# ---------------------------------------------------------------------------


def build_source_tree(
    root: Path,
    *,
    entries: tuple[str, ...] = DEFAULT_MANIFEST_ENTRIES,
    extra_files: dict[str, str] | None = None,
) -> Path:
    """Build a minimal synthetic tachi-like source clone at ``root``.

    Writes ``INSTALL_MANIFEST.md`` with ``entries`` inside the marker block,
    plus real content at every one of those paths (a directory entry gets
    one placeholder file inside it; a file entry gets a one-line file), so
    ``install.sh --source root`` has something real to copy. Also writes
    ``root/scripts/install.sh`` as a placeholder (callers that exercise the
    real installer overwrite this with a copy of the working-tree script --
    that copy step is the harness runner's job, not this builder's).

    Args:
        root: directory to populate (created if absent).
        entries: manifest entries, in the exact `.claude/skills/tachi-*` /
            `.claude/commands/tachi.*.md` / `scripts/*.py` shapes the real
            manifest uses. Directory entries end in ``/``.
        extra_files: optional ``{relative_path: content}`` map for
            additional source-tree files a scenario needs (for example, a
            file at a path a "nested" or "wrong-type" link will collide
            with).

    Returns:
        ``root`` (already resolved to a ``Path``), i.e. the value to pass
        as ``--source`` to ``install.sh``.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    manifest_lines = [
        "# Install Manifest (synthetic, F-373 fixture)",
        "",
        MANIFEST_BEGIN_MARKER,
        *entries,
        MANIFEST_END_MARKER,
        "",
    ]
    (root / "INSTALL_MANIFEST.md").write_text("\n".join(manifest_lines), encoding="utf-8")

    for entry in entries:
        entry_path = root / entry
        if entry.endswith("/"):
            entry_path.mkdir(parents=True, exist_ok=True)
            (entry_path / "PLACEHOLDER.md").write_text(
                f"Synthetic content for manifest entry {entry!r}.\n", encoding="utf-8"
            )
        else:
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(
                f"Synthetic content for manifest entry {entry!r}.\n", encoding="utf-8"
            )

    (root / "scripts").mkdir(parents=True, exist_ok=True)
    install_sh = root / "scripts" / "install.sh"
    if not install_sh.exists():
        install_sh.write_text(
            "#!/usr/bin/env bash\n"
            "# Placeholder -- the harness runner (tasks.md T008) overwrites this\n"
            "# with a copy of the working-tree scripts/install.sh under test.\n",
            encoding="utf-8",
        )
        install_sh.chmod(0o755)

    for rel_path, content in (extra_files or {}).items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    return root


def build_project_tree(root: Path) -> Path:
    """Build an empty target project directory at ``root``.

    This is the "no-link project" baseline (US-2 rev-1 case): a clean
    directory with nothing installed and no symlinks anywhere, used both as
    its own regression-guard scenario and as the starting point every other
    ``add_*`` builder layers a symlink class onto.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


# ---------------------------------------------------------------------------
# Link-class builders
# ---------------------------------------------------------------------------


def add_symlink(
    project_root: Path,
    relpath: str,
    target: Path,
    *,
    target_is_dir: bool = True,
    relative: bool = False,
) -> Path:
    """Make ``project_root/relpath`` a symlink to ``target``.

    Covers two of the data-model.md Sec. 2.1 origin classes with one
    mechanism, since they differ only in which path depth the caller picks:
      - "a link AT an entry" -- ``relpath`` equal to the manifest entry's
        own destination (a `tachi-*` skill dir, or a single file);
      - "an ancestor link" -- ``relpath`` a strict prefix of an entry's
        destination (for example ``.claude`` when the entry is
        ``.claude/skills/tachi-foo/``).

    ``target`` is NOT created by this function -- point it at a real
    directory or file the caller already built (typically another spot in
    the same project tree, or a sibling tmp directory) if the link should
    resolve.
    """
    del target_is_dir  # documents intent only; the target's real type governs resolution
    return make_symlink(Path(project_root) / relpath, Path(target), relative=relative)


def add_nested_symlink(
    project_root: Path,
    dir_entry_relpath: str,
    inner_relpath: str,
    target: Path,
    *,
    target_is_dir: bool = True,
) -> Path:
    """Make a directory entry real, then link to something INSIDE it.

    Builds ``project_root/dir_entry_relpath`` as an ordinary directory (so
    the entry itself is not a link), then creates a symlink at
    ``project_root/dir_entry_relpath/inner_relpath`` pointing at ``target``.
    This is the data-model.md Sec. 2.1 ``nested`` class (``subtree`` in
    ``origins``): always refused, flag or not, because BSD ``cp -r`` cannot
    write through a symlinked subdirectory or file nested inside a copied
    tree (spec ruling S-6).
    """
    del target_is_dir  # documents intent only; see add_symlink
    dir_entry = Path(project_root) / dir_entry_relpath
    dir_entry.mkdir(parents=True, exist_ok=True)
    return make_symlink(dir_entry / inner_relpath, Path(target))


def add_dangling_symlink(project_root: Path, relpath: str) -> Path:
    """Make ``project_root/relpath`` a symlink to a target that does not exist."""
    nonexistent = Path(project_root) / ".nonexistent-dangling-target"
    return make_symlink(Path(project_root) / relpath, nonexistent)


def add_looping_symlink(project_root: Path, relpath: str) -> Path:
    """Make ``project_root/relpath`` a two-node symlink cycle (a -> b -> a).

    Chasing either node never reaches a real file, so bash's ``resolve()``
    (contracts/installer-cli.md) gives up after 40 hops and classifies it
    ``unresolvable`` (looping). A self-loop (``a -> a``) is an equally valid
    one-node cycle if a test specifically wants that shape instead; build it
    directly with :func:`make_symlink` (``make_symlink(p, p)``).
    """
    link_path = Path(project_root) / relpath
    partner_path = link_path.parent / f"{link_path.name}.loop-partner"
    make_symlink(partner_path, link_path)
    return make_symlink(link_path, partner_path)


def build_symlink_chain(
    project_root: Path,
    relpath: str,
    *,
    hops: int,
    terminal_target: Path | None = None,
) -> Path:
    """Build a chain of exactly ``hops`` symlinks starting at ``relpath``.

    Useful for the 40/41-hop boundary contracts/installer-cli.md pins:
    ``hops=40`` with a real ``terminal_target`` resolves; ``hops=41`` (or any
    ``hops`` with ``terminal_target=None``) is unresolvable. Intermediate
    link nodes are written next to ``relpath`` as
    ``<name>.hop-1``, ``<name>.hop-2``, ....

    Args:
        project_root: project root the chain is built under.
        relpath: path of the first (outermost) link in the chain -- the one
            a test points ``install.sh`` at.
        hops: chain length (number of ``readlink`` calls to fully resolve
            ``relpath``). Must be >= 1.
        terminal_target: what the last link in the chain points at. ``None``
            leaves the chain dangling (its last hop points at a path that
            never exists).

    Returns:
        The path of the first (outermost) link, i.e. ``project_root/relpath``.
    """
    if hops < 1:
        raise ValueError("hops must be >= 1")
    head = Path(project_root) / relpath
    nodes = [head] + [head.parent / f"{head.name}.hop-{i}" for i in range(1, hops)]
    final_target = (
        Path(terminal_target) if terminal_target is not None else head.parent / ".nonexistent-chain-end"
    )
    # Link the chain from the tail backwards so every intermediate node
    # already exists (as a dangling-or-not link) by the time its predecessor
    # is created; order doesn't affect the final graph, only readability.
    for i in range(len(nodes) - 1, -1, -1):
        next_hop = nodes[i + 1] if i + 1 < len(nodes) else final_target
        make_symlink(nodes[i], next_hop)
    return head


def add_wrong_type_symlink(project_root: Path, relpath: str, *, need: str) -> Path:
    """Make ``project_root/relpath`` a symlink whose target is the wrong type.

    Builds a real target of the OPPOSITE type from ``need`` right next to
    the link (``<relpath>.wrong-type-target``), then links to it. Per
    data-model.md Sec. 2.1, this is ``unresolvable`` regardless of
    ``--follow-symlinks``: ``mkdir -p`` or ``cp`` would otherwise fail
    mid-copy with a partial install.

    Args:
        need: ``"dir"`` (the entry needs a directory, but the link resolves
            to a file -- builds a file target) or ``"file"`` (the entry
            needs a file, but the link resolves to a directory -- builds a
            directory target).
    """
    if need not in ("dir", "file"):
        raise ValueError('need must be "dir" or "file"')
    link_path = Path(project_root) / relpath
    wrong_target = link_path.parent / f"{link_path.name}.wrong-type-target"
    wrong_target.parent.mkdir(parents=True, exist_ok=True)
    if need == "dir":
        # Entry needs a directory; give it a file instead.
        wrong_target.write_text("Synthetic wrong-type target (file where a directory is needed).\n", encoding="utf-8")
    else:
        # Entry needs a file; give it a directory instead.
        wrong_target.mkdir(parents=True, exist_ok=True)
    return make_symlink(link_path, wrong_target)


def add_symlink_into_source_clone(
    project_root: Path,
    relpath: str,
    source_root: Path,
    *,
    subpath: str = "",
) -> Path:
    """Make ``project_root/relpath`` a symlink straight into the source clone.

    Per data-model.md Sec. 2.2, this is ``source-tree``: refused regardless
    of ``--follow-symlinks``, because the destination physically resolves
    inside ``SRC_P``.

    Args:
        subpath: optional path inside ``source_root`` to point at (default:
            the clone root itself).
    """
    target = Path(source_root) / subpath if subpath else Path(source_root)
    return make_symlink(Path(project_root) / relpath, target)


def add_symlink_to_source_clone_parent(
    project_root: Path,
    relpath: str,
    source_root: Path,
) -> Path:
    """Make ``project_root/relpath`` a symlink to the source clone's PARENT.

    Reproduces the contract's own example (``templates -> ..``, where entry
    ``templates/tachi/`` lands back at the clone root): pick ``relpath`` so
    that whatever the manifest entry appends after it equals
    ``source_root.name``. For example, with ``source_root`` named
    ``tachi``, link ``project_root/templates`` to ``source_root.parent``,
    then check the entry ``templates/tachi/`` -- ``resolve()`` walks
    ``templates -> <source_root's parent>``, then appends ``/tachi``,
    landing back on ``source_root`` itself (``phys_dest`` sees it as
    ``source-tree`` per data-model.md Sec. 2.2, with no link directly on the
    entry itself).
    """
    return make_symlink(Path(project_root) / relpath, Path(source_root).parent)


# ---------------------------------------------------------------------------
# Case-sensitivity probe and case-variant links (rev. 2, ruling AR-1)
# ---------------------------------------------------------------------------


def filesystem_is_case_sensitive(root: Path) -> bool:
    """Probe whether the filesystem under ``root`` is case-sensitive.

    Writes a small marker file, then checks whether an upper-cased spelling
    of its name resolves to the same file. macOS (APFS, HFS+) is normally
    case-insensitive; Linux is normally case-sensitive. Callers should skip
    the case-variant scenarios below when this returns ``True`` (rev. 2
    cases run on macOS only).
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    probe = root / ".case-sensitivity-probe"
    probe.write_text("probe\n", encoding="utf-8")
    variant = root / probe.name.upper()
    try:
        return not variant.exists()
    finally:
        probe.unlink(missing_ok=True)


def case_variant_path(path: Path) -> Path:
    """Return ``path`` with its final component's case flipped.

    On a case-insensitive volume this names the SAME physical file or
    directory through a different string. Used both to build a
    case-variant link target and to build "a project reached through a
    case-variant path" (rev. 2's second AR-1 case), where ``path`` itself
    is handed to ``install.sh`` as the target directory (never through a
    symlink at all).
    """
    path = Path(path)
    name = path.name
    flipped = name.lower() if name != name.lower() else name.upper()
    return path.with_name(flipped)


def add_case_variant_symlink_to_source_clone(
    project_root: Path,
    relpath: str,
    source_root: Path,
) -> Path:
    """Make ``project_root/relpath`` a link whose TEXT spells the clone in a different case.

    On a case-insensitive volume (macOS APFS/HFS+) this still resolves to
    ``source_root`` by identity, so containment must catch it by
    ``[ -ef ]`` (device+inode), never by string prefix (ruling AR-1) --
    ``case "$X/" in "$SRC_P"/*)`` would miss it. Skip this scenario on a
    case-sensitive volume (see :func:`filesystem_is_case_sensitive`): there
    the case-variant path is simply a different, nonexistent path, so it
    would dangle instead of exercising the identity check.
    """
    return make_symlink(Path(project_root) / relpath, case_variant_path(Path(source_root)))


# ---------------------------------------------------------------------------
# Vendored clone (no link at all) and the dangling deprecated-command link
# ---------------------------------------------------------------------------


def vendor_source_tree_inside_project(
    project_root: Path,
    entry_relpath: str,
    **source_tree_kwargs,
) -> Path:
    """Nest a real (non-symlink) source clone at a manifest entry's own destination.

    Builds a synthetic source tree (:func:`build_source_tree`) physically
    AT ``project_root/entry_relpath`` -- no symlink anywhere. Since the
    manifest entry ``entry_relpath`` and the clone now occupy the identical
    directory, ``phys_dest(TARGET_P/entry_relpath)`` trivially equals the
    clone's own physical path, so ``under(dest, SRC_P)`` is true by
    identity (data-model.md Sec. 2.2: "a clone vendored at a destination
    path with no link at all"). The earlier per-link check (which only
    ever inspected whether the entry ITSELF was a symlink) could not catch
    this, because there is no symlink to inspect.

    Args:
        entry_relpath: the manifest entry's destination path inside the
            project, with or without a trailing ``/`` (both are accepted;
            the trailing slash is stripped before use as a directory name).
        **source_tree_kwargs: forwarded to :func:`build_source_tree`
            (``entries``, ``extra_files``).

    Returns:
        The nested source root, i.e. the value to pass as ``--source`` to
        ``install.sh`` while ``project_root`` is the target/CWD.
    """
    nested_root = Path(project_root) / entry_relpath.rstrip("/")
    return build_source_tree(nested_root, **source_tree_kwargs)


def add_dangling_deprecated_command_link(project_root: Path, *, which: int = 0) -> Path:
    """Make one of the five real deprecated-command files a dangling symlink.

    Uses :data:`DEPRECATED_COMMANDS` (mirrors ``install.sh``'s own array),
    so the path is exactly one ``install.sh`` already knows to clean up.
    Without ``--follow-symlinks`` the cleanup is refused and the link
    survives; with the flag, the cleanup is skipped (listed as skipped) and
    the link still survives -- ``install.sh`` never deletes through a link.

    Args:
        which: index into :data:`DEPRECATED_COMMANDS` (default: the first,
            ``threat-model.md``).
    """
    return add_dangling_symlink(project_root, DEPRECATED_COMMANDS[which])
