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
import re
import shutil
import subprocess
from dataclasses import dataclass
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
    # --- harness runner (T008, W1) ---
    "REPO_ROOT",
    "WORKING_TREE_INSTALL_SH",
    "BASH_BIN",
    "strip_ansi",
    "drop_mmdc_courtesy_warning",
    "clean_output",
    "InstallResult",
    "copy_working_tree_install_sh",
    "run_install_sh",
    "PathSnapshot",
    "snapshot_path",
    "snapshot_tree",
    "diff_snapshots",
    "assert_no_tree_changes",
    "GIT_ISOLATION_ENV",
    "build_version_tagged_source_repo",
    "current_ref",
    "detach_head",
    "GIT_SHIM_REAL_GIT_ENV",
    "GIT_SHIM_FAIL_REF_ENV",
    "build_forced_checkout_failure_git_shim",
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


# ---------------------------------------------------------------------------
# Harness runner (tasks.md T008, W1; contracts/installer-cli.md
# Sec. "Test harness contract"). Everything above this point (T003) builds
# the synthetic project/source trees; everything below RUNS a real
# install.sh against them and captures, cleans and snapshots the result.
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKING_TREE_INSTALL_SH = REPO_ROOT / "scripts" / "install.sh"

# N12 / spec ruling S-7: the strict leg must always exercise macOS's system
# bash 3.2, whatever a newer Homebrew bash sits earlier on PATH. This harness
# never honors an exported BASH override -- that is exactly the drift this
# pin exists to prevent.
BASH_BIN = "/bin/bash"

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# install.sh's best-effort "mmdc not on PATH" courtesy warning (the
# Prerequisite courtesy warning block at the end of the script). It is a
# real, environment-dependent message -- present whenever the test runner's
# own PATH lacks mmdc -- with nothing to do with K3. Tests that assert exact
# installer-authored text must not trip over it.
_MMDC_COURTESY_MARKERS = (
    "mmdc (@mermaid-js/mermaid-cli) is not on PATH",
    "mmdc is a prerequisite for attack path rendering",
    "npm install -g @mermaid-js/mermaid-cli",
    "README.md Prerequisites section",
)


def strip_ansi(text: str) -> str:
    """Strip install.sh's RED/GREEN/NC ANSI color escapes from captured output."""
    return _ANSI_RE.sub("", text)


def drop_mmdc_courtesy_warning(text: str) -> str:
    """Drop install.sh's best-effort "mmdc not on PATH" courtesy warning lines.

    Line-based rather than block-based on purpose: robust to the blank
    separator line around the warning without needing to match it too.
    """
    lines = text.splitlines(keepends=True)
    return "".join(
        line for line in lines if not any(marker in line for marker in _MMDC_COURTESY_MARKERS)
    )


def clean_output(text: str) -> str:
    """ANSI-stripped, mmdc-courtesy-warning-free text, ready to assert on."""
    return drop_mmdc_courtesy_warning(strip_ansi(text))


@dataclass
class InstallResult:
    """One ``install.sh`` invocation's outcome, with pre-cleaned text views."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def clean_stdout(self) -> str:
        return clean_output(self.stdout)

    @property
    def clean_stderr(self) -> str:
        return clean_output(self.stderr)

    @property
    def combined(self) -> str:
        """Cleaned stdout+stderr concatenated for "does this phrase appear
        anywhere" checks.

        The two streams are captured separately (as `subprocess.run` always
        does), so relative ORDER between a stdout line and a stderr line is
        not preserved here -- never use this property for line-order
        assertions, only for substring-presence ones.
        """
        return self.clean_stdout + self.clean_stderr


def copy_working_tree_install_sh(source_root: Path) -> Path:
    """Overwrite a synthetic source tree's placeholder install.sh with a
    real copy of THIS working tree's scripts/install.sh.

    ``build_source_tree()`` (T003) writes a harmless placeholder at
    ``<source_root>/scripts/install.sh`` instead of the real script, so a
    fixture builder never depends on the working tree by itself. Every test
    that actually EXECUTES install.sh calls this first. Preserves the
    executable bit. Reads only from ``WORKING_TREE_INSTALL_SH``; never
    touches it.
    """
    dest = Path(source_root) / "scripts" / "install.sh"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WORKING_TREE_INSTALL_SH, dest)
    dest.chmod(0o755)
    return dest


def run_install_sh(
    script_path: Path,
    *,
    cwd: Path,
    args: tuple[str, ...] = (),
    env: dict[str, str] | None = None,
    pwd_override: str | None = None,
    path_prepend: tuple[Path, ...] = (),
    extra_env: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> InstallResult:
    """Invoke ``/bin/bash <script_path> <args...>`` with ``cwd=cwd``.

    Pins the shell to :data:`BASH_BIN` (never an exported ``BASH`` -- N12)
    and always sets ``LC_ALL=C`` (spec ruling S-7), so the strict leg stays
    on bash 3.2 on a dev Mac even with a newer Homebrew bash first on the
    caller's own ``PATH``.

    Args:
        script_path: the install.sh COPY to run (normally
            ``<source_root>/scripts/install.sh``, after
            :func:`copy_working_tree_install_sh`).
        cwd: the child process's real working directory. For the "reached
            through a link" harness case, pass the LOGICAL (through-the-
            symlink) path here -- ``chdir`` resolves it at the OS level
            regardless of which spelling is given.
        args: extra argv, e.g. ``("--source", str(source_root))`` or
            ``("--follow-symlinks",)``.
        env: a full replacement environment (default: a copy of the
            caller's ``os.environ``).
        pwd_override: when given, sets ``$PWD`` in the child's environment
            to this LOGICAL path string, so bash's ``pwd`` builtin (which
            install.sh's own ``TARGET_DIR="$(pwd)"`` calls) echoes it back
            verbatim instead of recomputing a physical path -- this is what
            makes the "reached through a link" harness case non-vacuous.
            When omitted, ``$PWD`` is unset so no stale value from the test
            runner's own shell leaks in.
        path_prepend: directories prepended to ``$PATH`` (e.g. a git-shim
            directory), with the rest of the inherited ``$PATH`` kept
            after them so real ``git``, ``cp``, ``find``, etc. stay
            reachable.
        extra_env: additional env vars merged in on top of ``env``/PWD/PATH
            (e.g. the git-shim selector vars).
        timeout: seconds before the subprocess is killed.
    """
    run_env = dict(env) if env is not None else dict(os.environ)
    run_env["LC_ALL"] = "C"
    if pwd_override is not None:
        run_env["PWD"] = pwd_override
    else:
        run_env.pop("PWD", None)
    if path_prepend:
        existing = run_env.get("PATH", "")
        run_env["PATH"] = os.pathsep.join([*(str(p) for p in path_prepend), existing])
    if extra_env:
        run_env.update(extra_env)

    completed = subprocess.run(
        [BASH_BIN, str(script_path), *args],
        cwd=str(cwd),
        env=run_env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return InstallResult(completed.returncode, completed.stdout, completed.stderr)


# ---------------------------------------------------------------------------
# Before/after tree snapshots ("zero files written" -- FR-K3.6 test validity)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PathSnapshot:
    """One filesystem entry's identity: type, raw readlink text, size, mtime.

    Mirrors the harness contract verbatim ("before-and-after tree snapshots
    ... of the target and of each link's resolved directory").
    """

    kind: str  # "missing" | "file" | "dir" | "symlink" | "other"
    readlink_text: str | None
    size: int | None
    mtime_ns: int | None


def snapshot_path(path: Path) -> PathSnapshot:
    """Snapshot ONE path: its type, readlink text (if a link), size, mtime.

    A symlink is snapshotted as itself (``lstat``/``readlink``), never
    followed -- callers that also care about a link's target snapshot that
    target directory separately (see :func:`snapshot_tree`'s docstring).
    """
    path = Path(path)
    if path.is_symlink():
        try:
            target_text: str | None = os.readlink(path)
        except OSError:
            target_text = None
        try:
            st = path.lstat()
            return PathSnapshot("symlink", target_text, st.st_size, st.st_mtime_ns)
        except OSError:
            return PathSnapshot("symlink", target_text, None, None)
    if not path.exists():
        return PathSnapshot("missing", None, None, None)
    if path.is_dir():
        return PathSnapshot("dir", None, None, None)
    if path.is_file():
        st = path.stat()
        return PathSnapshot("file", None, st.st_size, st.st_mtime_ns)
    return PathSnapshot("other", None, None, None)


def snapshot_tree(root: Path) -> dict[str, PathSnapshot]:
    """Snapshot every entry strictly under ``root``, keyed by its path
    relative to ``root``.

    Never follows a symlinked directory into its target
    (``followlinks=False``): a linked subtree is recorded as ONE ``symlink``
    entry at its own path, exactly like a linked file, so "nothing changed
    under root" also means "no new descendant appeared through a link".
    Pair with a separate :func:`snapshot_tree` (or :func:`snapshot_path`)
    call on a link's resolved target directory to prove that side stayed
    untouched too.

    Returns ``{}`` for a root that does not exist yet (a valid "before"
    state for a project install.sh would create from scratch).
    """
    root = Path(root)
    if not root.exists():
        return {}
    snapshots: dict[str, PathSnapshot] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in list(dirnames) + list(filenames):
            full = Path(dirpath) / name
            rel = str(full.relative_to(root))
            snapshots[rel] = snapshot_path(full)
    return snapshots


def diff_snapshots(before: dict[str, PathSnapshot], after: dict[str, PathSnapshot]) -> str:
    """Human-readable diff for a failed "nothing was written" assertion."""
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in (set(before) & set(after)) if before[k] != after[k])
    return f"added={added} removed={removed} changed={changed}"


def assert_no_tree_changes(
    before: dict[str, PathSnapshot], after: dict[str, PathSnapshot], *, label: str = "tree"
) -> None:
    assert before == after, f"{label} changed unexpectedly: {diff_snapshots(before, after)}"


# ---------------------------------------------------------------------------
# --version harness: throwaway repos and the forced-restore-failure shim
# (FR-K3.5, PD-11; contract "Test harness contract")
# ---------------------------------------------------------------------------

# GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1 isolate every git
# call this harness makes from the CALLER's real git config (a developer's
# global aliases, signing settings, credential helpers, etc.) so the
# throwaway repos below are hermetic and never touch the live tachi
# checkout's own git state.
GIT_ISOLATION_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
_GIT_IDENTITY_ARGS = ("-c", "user.name=tachi-test", "-c", "user.email=test@example.invalid")


def _git_env() -> dict[str, str]:
    return {**os.environ, **GIT_ISOLATION_ENV}


def _git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        env=_git_env(),
        capture_output=True,
        text=True,
        check=check,
    )


def build_version_tagged_source_repo(
    root: Path,
    *,
    tag: str,
    tagged_entries: tuple[str, ...] = DEFAULT_MANIFEST_ENTRIES,
    head_entries: tuple[str, ...] | None = None,
    remove_from_tagged: tuple[str, ...] = (),
) -> Path:
    """Build a throwaway git repo at ``root``: a tagged commit, then a
    second (HEAD) commit that differs only in manifest/source content.

    ``scripts/install.sh`` is copied from the WORKING TREE identically into
    BOTH commits: the running script must never change under bash mid-run
    (contract). Isolated from the caller's real git identity and config
    (:data:`GIT_ISOLATION_ENV`, plus an explicit ``-c user.name=``/``-c
    user.email=`` on every commit), and never touches the live tachi
    checkout -- ``git init`` always starts a brand-new repo at ``root``.

    Args:
        tag: the version tag to create at the first commit.
        tagged_entries: manifest entries at the tagged commit.
        head_entries: manifest entries at the HEAD commit. Defaults to
            ``tagged_entries`` unchanged (only a content marker file
            differs between the two commits then). Pass a distinct tuple
            to make a manifest ENTRY itself differ between tag and HEAD --
            for example, a "fails" (COPY_FAIL) scenario wants a HEAD-only
            entry the TAGGED source tree lacks.
        remove_from_tagged: relative paths to delete from the source tree
            AFTER ``tagged_entries``' backing content is built but BEFORE
            the tagged commit is made -- so the tag's own manifest lists an
            entry with no real backing file/dir, a "fails" (COPY_FAIL)
            scenario's setup. Leave empty for a tag whose manifest and
            content agree (the common case).

    Returns ``root``, ready to pass as ``--source``. Leaves the repo
    checked out on HEAD (the second commit), as if a developer had never
    touched ``--version`` themselves -- install.sh's own tag checkout is
    what moves it from there.
    """
    root = Path(root)
    build_source_tree(root, entries=tagged_entries)
    for rel in remove_from_tagged:
        target = root / rel
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    copy_working_tree_install_sh(root)

    _git("init", "--quiet", cwd=root)
    _git("add", "-A", cwd=root)
    _git(*_GIT_IDENTITY_ARGS, "commit", "--quiet", "-m", "tagged commit", cwd=root)
    _git("tag", tag, cwd=root)

    effective_head_entries = tagged_entries if head_entries is None else head_entries
    if effective_head_entries != tagged_entries:
        build_source_tree(root, entries=effective_head_entries)
    else:
        (root / "HEAD_MARKER.txt").write_text(
            "head commit marker (F-373 K3 fixture)\n", encoding="utf-8"
        )
    copy_working_tree_install_sh(root)  # stays byte-identical at both commits
    _git("add", "-A", cwd=root)
    _git(*_GIT_IDENTITY_ARGS, "commit", "--quiet", "-m", "head commit", cwd=root)

    return root


def current_ref(root: Path) -> str:
    """Mirror install.sh's own ``ORIGINAL_REF`` derivation: the branch
    name, or a SHA if HEAD is detached."""
    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=root).stdout.strip()
    if branch == "HEAD":
        return _git("rev-parse", "HEAD", cwd=root).stdout.strip()
    return branch


def detach_head(root: Path) -> str:
    """Detach ``root``'s HEAD at its current commit. Returns the SHA."""
    sha = _git("rev-parse", "HEAD", cwd=root).stdout.strip()
    _git("checkout", "--quiet", "--detach", sha, cwd=root)
    return sha


# Selector env vars the shim script (below) reads AT RUN TIME -- never baked
# into the shim file itself, so one shim serves every test (contract:
# "selected by an environment variable").
GIT_SHIM_REAL_GIT_ENV = "INSTALL_SH_TEST_SHIM_REAL_GIT"
GIT_SHIM_FAIL_REF_ENV = "INSTALL_SH_TEST_SHIM_FAIL_CHECKOUT_REF"

# A static /bin/sh shim: execs the real git for everything except a
# `checkout <fail_ref>`, which it fails loudly on stderr. Kept as one
# module-level constant (never regenerated per test) precisely because it
# is generic -- both env vars above are read fresh on every invocation.
_GIT_SHIM_SCRIPT = """#!/bin/sh
real_git="$INSTALL_SH_TEST_SHIM_REAL_GIT"
fail_ref="$INSTALL_SH_TEST_SHIM_FAIL_CHECKOUT_REF"
prev=""
for arg in "$@"; do
  if [ "$prev" = "checkout" ] && [ -n "$fail_ref" ] && [ "$arg" = "$fail_ref" ]; then
    printf 'test-shim: forced failure for checkout %s\\n' "$arg" >&2
    exit 1
  fi
  prev="$arg"
done
exec "$real_git" "$@"
"""


def build_forced_checkout_failure_git_shim(shim_dir: Path) -> Path:
    """Write the ``/bin/sh`` ``git`` shim into ``shim_dir`` for the forced
    restore-failure harness case.

    Callers must PREPEND ``shim_dir`` to ``$PATH`` (via
    :func:`run_install_sh`'s ``path_prepend``, never replacing the rest of
    ``$PATH``) and set both :data:`GIT_SHIM_REAL_GIT_ENV` (to
    ``shutil.which("git")``, captured beforehand) and
    :data:`GIT_SHIM_FAIL_REF_ENV` (to the exact ``ORIGINAL_REF`` value the
    restore checkout will use, e.g. from :func:`current_ref`) via
    ``extra_env``. Every OTHER git invocation -- status, rev-parse, tag,
    fetch, describe, and ``checkout`` of any OTHER ref such as the initial
    ``--version`` tag checkout -- execs the real git untouched.

    Returns ``shim_dir``.
    """
    shim_dir = Path(shim_dir)
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim_path = shim_dir / "git"
    shim_path.write_text(_GIT_SHIM_SCRIPT, encoding="utf-8")
    shim_path.chmod(0o755)
    return shim_dir
