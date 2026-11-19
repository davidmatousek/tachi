"""Installed version marker tests for `scripts/install.sh` (Feature 391, T037, US5).

`templates/tachi/VERSION` is one line, `tachi_version: <value>`
(`specs/391-isolated-auditable-operation/contracts/version-marker.md`, plan.md
AD-7). The source ships it as a tracked placeholder that reads `unknown`, so
every copy path resets it. `scripts/install.sh` then writes the real value once
its copy loop is done (T036): the source clone's
`git describe --tags --always --dirty`; with no git tree of its own,
`<release manifest ".">-release-manifest`; otherwise `unknown`.

W1 cases (tasks.md T037) and the tests that carry them:
    1. the installer writes the describe value
         test_installer_writes_the_describe_value        (HEAD at a tag, and past it)
         test_version_install_writes_the_installed_tag    (`--version`)
         test_worktree_source_writes_the_describe_value  (`.git` is a file)
    2. a marker-writing install, then a marker-skipping one, reads `unknown`
         test_marker_writing_then_skipping_install_reads_unknown
    3. an install that skips the marker line reads `unknown`, the placeholder
         test_marker_skipping_install_reads_the_tracked_placeholder
         test_tracked_placeholder_is_one_unknown_line
    4. `-dirty`                       test_uncommitted_change_appends_dirty
    5. `-release-manifest` fallback   test_source_without_a_git_tree_reads_the_release_manifest
                                      test_source_inside_another_repo_reads_the_release_manifest
    6. `unknown` fallback             test_no_usable_version_reads_unknown
    7. manifest carries the placeholder
                                      test_manifest_entry_ships_the_placeholder

Every install is a real `scripts/install.sh` run (Bash 3.2 where the host has
it, see `install_sh_helpers.BASH_BIN`) against a synthetic source built at test
time. The repository itself is never installed from, and nothing reaches the
network: the throwaway repos have no remote, so the installer's best-effort
`git fetch --tags` fails at once.

Cases that expect the installer to have WRITTEN the marker start from a source
whose placeholder is SENTINEL, a value no install can produce. A pass therefore
cannot be a placeholder copied through, and the case goes red against an
installer that never writes. Cases about skipped writes start from the real
tracked placeholder. A marker-skipping install is the manual loop's copy step
for the `templates/tachi/` entry (`cp -R <src>/templates/tachi/. <dst>`), built
here directly rather than read out of the README (P0B0-10 (a)).

Environment: each test runs in its own temp dir, removed afterwards with Python
(`shutil`), under a hermetic environment: git config isolated, `$HOME` inside the
temp dir, repository-locating `GIT_*` variables scrubbed, and a git ceiling at the
temp dir so no repository above it can be found.

Repository inputs (the CI path anchor must list them):
    scripts/install.sh                 copied into every synthetic source
    templates/tachi/VERSION            the tracked placeholder (cases 2, 3, 7)
    INSTALL_MANIFEST.md                case 7
    tests/scripts/install_sh_helpers.py, tests/scripts/conftest.py
                                       sandbox builders and the `tests/scripts` sys.path entry

Python 3.9 compatible (CI adds a 3.9 leg): no `X | Y` outside annotations, no
`match`, no `ignore_cleanup_errors`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from install_sh_helpers import (
    DEFAULT_MANIFEST_ENTRIES,
    GIT_ISOLATION_ENV,
    build_project_tree,
    build_source_tree,
    copy_working_tree_install_sh,
    current_ref,
    run_install_sh,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSION_REL = "templates/tachi/VERSION"
VERSION_PATH = REPO_ROOT / VERSION_REL
MANIFEST_PATH = REPO_ROOT / "INSTALL_MANIFEST.md"

# Same markers as install.sh's parse_manifest (string equality, not a regex).
MANIFEST_BEGIN = "<!-- BEGIN MANIFEST -->"
MANIFEST_END = "<!-- END MANIFEST -->"

# The tracked placeholder, as contracts/version-marker.md fixes it.
PLACEHOLDER = "tachi_version: unknown\n"
# A placeholder no install can produce (see the module docstring).
SENTINEL = "tachi_version: placeholder-copied-from-the-source\n"

TAG = "v4.48.1"
# `templates/tachi/` as a directory entry is what makes install.sh handle the marker.
ENTRIES = (*DEFAULT_MANIFEST_ENTRIES, "templates/tachi/")

_DESCRIBE_AT_TAG = re.escape(TAG)
_DESCRIBE_PAST_TAG = re.escape(TAG) + r"-\d+-g[0-9a-f]{7,}"

# Variables that locate a repository (set when pytest itself runs inside a git hook,
# for one): left in place they would send every throwaway repo to the wrong place.
_GIT_LOCATION_VARS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_PREFIX",
)

_SUMMARY_VERSION_RE = re.compile(r"^  Version:  (\S+)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Sandbox and builders
# ---------------------------------------------------------------------------


@pytest.fixture
def sandbox(monkeypatch):
    """A fresh temp dir and a hermetic environment for every git and installer call.

    The dir is removed afterwards with `shutil`, never a shell. The environment
    is applied to `os.environ`, which both this module's git calls and
    `install_sh_helpers.run_install_sh` (it copies `os.environ`) inherit.
    """
    raw = tempfile.mkdtemp(prefix="tachi-t037-")
    try:
        root = Path(raw).resolve()
        home = root / "home"
        home.mkdir()
        for name in _GIT_LOCATION_VARS:
            monkeypatch.delenv(name, raising=False)
        hermetic = dict(GIT_ISOLATION_ENV)
        hermetic["HOME"] = str(home)
        hermetic["GIT_CEILING_DIRECTORIES"] = str(root)
        hermetic["GIT_TERMINAL_PROMPT"] = "0"
        for name, value in hermetic.items():
            monkeypatch.setenv(name, value)
        yield root
    finally:
        shutil.rmtree(raw, ignore_errors=True)


def _git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if check:
        assert proc.returncode == 0, f"git {' '.join(args)} failed in {cwd}:\n{proc.stderr}"
    return proc


def _commit(cwd: Path, message: str) -> None:
    identity = ("-c", "user.name=tachi-test", "-c", "user.email=test@example.invalid")
    _git(*identity, "commit", "--quiet", "-m", message, cwd=cwd)


def _describe(repo: Path) -> str:
    """The value the marker must hold for a git source: install.sh's own command."""
    return _git("describe", "--tags", "--always", "--dirty", cwd=repo).stdout.strip()


def _tracked_placeholder() -> str:
    return VERSION_PATH.read_text(encoding="utf-8")


def _build_source(root: Path, *, placeholder: str) -> Path:
    """A synthetic tachi source whose manifest lists `templates/tachi/`, with `placeholder` as its marker."""
    build_source_tree(root, entries=ENTRIES, extra_files={VERSION_REL: placeholder})
    copy_working_tree_install_sh(root)
    return root


def _build_tagged_source(
    root: Path, *, placeholder: str, commits_after_tag: int = 2, tag: str = TAG
) -> Path:
    """`_build_source`, committed and tagged, then `commits_after_tag` more commits.

    `scripts/install.sh` is committed once and never touched again, so it stays
    byte-identical at the tag and at HEAD (a `--version` checkout must not
    rewrite the script bash is running).
    """
    _build_source(root, placeholder=placeholder)
    _git("init", "--quiet", cwd=root)
    _git("add", "-A", cwd=root)
    _commit(root, "tagged commit")
    _git("tag", tag, cwd=root)
    for number in range(1, commits_after_tag + 1):
        (root / f"AFTER_TAG_{number}.txt").write_text(
            f"commit {number} after the tag\n", encoding="utf-8"
        )
        _git("add", "-A", cwd=root)
        _commit(root, f"commit {number} after the tag")
    return root


def _write_release_manifest(source: Path, packages: dict) -> None:
    """Write `.release-please-manifest.json` in release-please's own shape (two-space indent)."""
    (source / ".release-please-manifest.json").write_text(
        json.dumps(packages, indent=2) + "\n", encoding="utf-8"
    )


def _install(source: Path, project: Path, *extra: str):
    return run_install_sh(
        source / "scripts" / "install.sh",
        cwd=project,
        args=("--source", str(source), *extra),
    )


def _install_templates_without_marker_line(source: Path, project: Path) -> None:
    """A marker-skipping install: the manual loop's copy step for `templates/tachi/`, nothing after it."""
    destination = project / "templates" / "tachi"
    destination.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["cp", "-R", f"{source}/templates/tachi/.", str(destination)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def _assert_no_git_tree(source: Path) -> None:
    """Setup check: git finds no repository at or above `source` (the sandbox's ceiling guarantees it)."""
    found = _git("rev-parse", "--git-dir", cwd=source, check=False)
    assert found.returncode != 0, f"setup: {source} must have no git tree"


def _read_marker(project: Path) -> str:
    marker = project / VERSION_REL
    assert marker.is_file(), f"{VERSION_REL} was not installed into {project}"
    return marker.read_text(encoding="utf-8")


def _marker_line(value: str) -> str:
    return f"tachi_version: {value}\n"


def _summary_version(result) -> str:
    """The value on install.sh's `  Version:  <value>` summary line (it must be the marker's value)."""
    found = _SUMMARY_VERSION_RE.findall(result.clean_stdout)
    assert len(found) == 1, f"expected one 'Version:' summary line, got {found!r}\n{result.combined}"
    return found[0]


def _manifest_entries(path: Path) -> list:
    """The entries between the manifest markers, read the way install.sh's parse_manifest reads them."""
    entries = []
    inside = False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line == MANIFEST_BEGIN:
            inside = True
        elif line == MANIFEST_END:
            inside = False
        elif inside and line != "" and not line.startswith("#"):
            entries.append(line)
    return entries


# ---------------------------------------------------------------------------
# Case 1: the installer writes the describe value
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "commits_after_tag, describe_shape",
    [
        pytest.param(0, _DESCRIBE_AT_TAG, id="head-at-the-tag"),
        pytest.param(2, _DESCRIBE_PAST_TAG, id="two-commits-past-the-tag"),
    ],
)
def test_installer_writes_the_describe_value(sandbox, commits_after_tag, describe_shape):
    source = _build_tagged_source(
        sandbox / "tachi-src", placeholder=SENTINEL, commits_after_tag=commits_after_tag
    )
    project = build_project_tree(sandbox / "project")
    expected = _describe(source)
    assert re.fullmatch(describe_shape, expected), f"setup: unexpected describe value {expected!r}"

    result = _install(source, project)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == _marker_line(expected)
    assert _summary_version(result) == expected, "the summary line reuses the marker's value"
    # The atomic write leaves no temp file behind, and adds nothing else to the folder.
    assert sorted(p.name for p in (project / "templates" / "tachi").iterdir()) == [
        "PLACEHOLDER.md",
        "VERSION",
    ]
    assert (source / VERSION_REL).read_text(encoding="utf-8") == SENTINEL, (
        "the installer must never write the marker into the source tree"
    )


def test_version_install_writes_the_installed_tag(sandbox):
    """`--version <tag>` checks the tag out first: the marker names the tag it installed,
    not the describe value of the branch tip, and the ref is restored after the write."""
    source = _build_tagged_source(sandbox / "tachi-src", placeholder=SENTINEL, commits_after_tag=2)
    project = build_project_tree(sandbox / "project")
    original_ref = current_ref(source)
    tip_describe = _describe(source)
    assert re.fullmatch(_DESCRIBE_PAST_TAG, tip_describe), f"setup: {tip_describe!r}"

    result = _install(source, project, "--version", TAG)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == _marker_line(TAG)
    assert _summary_version(result) == TAG
    assert current_ref(source) == original_ref, "the source must be back on its original ref"
    assert _describe(source) == tip_describe


def test_worktree_source_writes_the_describe_value(sandbox):
    """A git worktree has a `.git` FILE, so a `-d .git` test would miss it; the contract's
    detection is `git rev-parse --git-dir`, which sees worktrees and submodules alike."""
    main = _build_tagged_source(sandbox / "tachi-main", placeholder=SENTINEL, commits_after_tag=2)
    worktree = sandbox / "tachi-worktree"
    _git("worktree", "add", "--detach", str(worktree), "HEAD", cwd=main)
    assert (worktree / ".git").is_file(), "setup: a worktree's .git is a file"
    project = build_project_tree(sandbox / "project")
    expected = _describe(worktree)
    assert re.fullmatch(_DESCRIBE_PAST_TAG, expected), f"setup: unexpected describe value {expected!r}"

    result = _install(worktree, project)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == _marker_line(expected)
    assert _summary_version(result) == expected


# ---------------------------------------------------------------------------
# Case 2: a marker-writing install, then a marker-skipping one
# ---------------------------------------------------------------------------


def test_marker_writing_then_skipping_install_reads_unknown(sandbox):
    """Re-installing by a path that skips the marker line must not leave the earlier value
    behind: the copy resets it to the tracked placeholder (P0B0-10)."""
    source = _build_tagged_source(sandbox / "tachi-src", placeholder=_tracked_placeholder())
    project = build_project_tree(sandbox / "project")

    writing = _install(source, project)

    assert writing.returncode == 0, writing.combined
    # Precondition (P0B0-10 (b)): the writing install left a describe value, not `unknown`.
    describe = _describe(source)
    assert re.fullmatch(_DESCRIBE_PAST_TAG, describe), f"setup: unexpected describe value {describe!r}"
    assert _read_marker(project) == _marker_line(describe)
    assert _read_marker(project) != PLACEHOLDER

    _install_templates_without_marker_line(source, project)

    assert _read_marker(project) == PLACEHOLDER


# ---------------------------------------------------------------------------
# Case 3: an install that skips the marker line reads the tracked placeholder
# ---------------------------------------------------------------------------


def test_marker_skipping_install_reads_the_tracked_placeholder(sandbox):
    # A describable source: a writing install would have named a version here.
    source = _build_tagged_source(sandbox / "tachi-src", placeholder=_tracked_placeholder())
    project = build_project_tree(sandbox / "project")
    assert re.fullmatch(_DESCRIBE_PAST_TAG, _describe(source))

    _install_templates_without_marker_line(source, project)

    assert _read_marker(project) == "tachi_version: unknown\n"


def test_tracked_placeholder_is_one_unknown_line():
    """The file every copy path carries: exactly `tachi_version: unknown`, newline-terminated."""
    assert VERSION_PATH.is_file(), f"{VERSION_REL} must be tracked in the repository"
    assert _tracked_placeholder() == "tachi_version: unknown\n"


# ---------------------------------------------------------------------------
# Case 4: -dirty
# ---------------------------------------------------------------------------


def test_uncommitted_change_appends_dirty(sandbox):
    source = _build_tagged_source(sandbox / "tachi-src", placeholder=SENTINEL, commits_after_tag=2)
    tracked = source / "AFTER_TAG_1.txt"
    tracked.write_text(
        tracked.read_text(encoding="utf-8") + "an edit that is never committed\n", encoding="utf-8"
    )
    project = build_project_tree(sandbox / "project")
    expected = _describe(source)
    assert re.fullmatch(_DESCRIBE_PAST_TAG + "-dirty", expected), f"setup: unexpected value {expected!r}"

    result = _install(source, project)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == _marker_line(expected)
    assert _summary_version(result) == expected


# ---------------------------------------------------------------------------
# Case 5: the -release-manifest fallback (a source with no git tree of its own)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "packages",
    [
        pytest.param({".": "7.6.5"}, id="root-package-only"),
        pytest.param({"packages/other": "1.0.0", ".": "7.6.5"}, id="root-package-after-another"),
    ],
)
def test_source_without_a_git_tree_reads_the_release_manifest(sandbox, packages):
    source = _build_source(sandbox / "tachi-src", placeholder=SENTINEL)
    _write_release_manifest(source, packages)
    _assert_no_git_tree(source)
    project = build_project_tree(sandbox / "project")

    result = _install(source, project)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == _marker_line("7.6.5-release-manifest")
    assert _summary_version(result) == "7.6.5-release-manifest"


def test_source_inside_another_repo_reads_the_release_manifest(sandbox):
    """A copy of tachi vendored in a project's own repo has no git tree of its own: describing it
    would name the OUTER project's version, so the installer falls back to the manifest."""
    outer = sandbox / "outer-project"
    outer.mkdir()
    _git("init", "--quiet", cwd=outer)
    (outer / "README.md").write_text("an unrelated project\n", encoding="utf-8")
    _git("add", "-A", cwd=outer)
    _commit(outer, "outer project")
    _git("tag", "v9.9.9-outer", cwd=outer)
    source = _build_source(outer / "vendor" / "tachi", placeholder=SENTINEL)
    _write_release_manifest(source, {".": "7.6.5"})
    # Setup: git does find a repository above the source, and the source is not its root.
    assert _git("rev-parse", "--git-dir", cwd=source, check=False).returncode == 0
    assert _git("rev-parse", "--show-cdup", cwd=source).stdout.strip() != ""
    project = build_project_tree(sandbox / "project")

    result = _install(source, project)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == _marker_line("7.6.5-release-manifest")
    assert _summary_version(result) == "7.6.5-release-manifest"


# ---------------------------------------------------------------------------
# Case 6: the unknown fallback
# ---------------------------------------------------------------------------


def _prepare_no_git_tree_and_no_manifest(source: Path) -> None:
    _assert_no_git_tree(source)


def _prepare_manifest_without_a_root_package(source: Path) -> None:
    _write_release_manifest(source, {"packages/other": "1.0.0"})
    _assert_no_git_tree(source)


def _prepare_repository_without_commits(source: Path) -> None:
    _git("init", "--quiet", cwd=source)
    describe = _git("describe", "--tags", "--always", "--dirty", cwd=source, check=False)
    assert describe.returncode != 0, "setup: git describe must fail with no commits"


@pytest.mark.parametrize(
    "prepare",
    [
        pytest.param(_prepare_no_git_tree_and_no_manifest, id="no-git-tree-no-manifest"),
        pytest.param(_prepare_manifest_without_a_root_package, id="manifest-without-a-root-package"),
        pytest.param(_prepare_repository_without_commits, id="git-describe-fails"),
    ],
)
def test_no_usable_version_reads_unknown(sandbox, prepare):
    """The source's own placeholder is SENTINEL, so `unknown` can only be what the installer wrote
    (and the old `untagged` fallback would show in the summary line)."""
    source = _build_source(sandbox / "tachi-src", placeholder=SENTINEL)
    prepare(source)
    project = build_project_tree(sandbox / "project")

    result = _install(source, project)

    assert result.returncode == 0, result.combined
    assert _read_marker(project) == PLACEHOLDER
    assert _summary_version(result) == "unknown"


# ---------------------------------------------------------------------------
# Case 7: INSTALL_MANIFEST.md carries the placeholder
# ---------------------------------------------------------------------------


def test_manifest_entry_ships_the_placeholder():
    """`templates/tachi/` is a directory entry (the spelling install.sh matches to handle the
    marker), and the placeholder sits inside it, so every manifest-driven copy carries it."""
    entries = _manifest_entries(MANIFEST_PATH)
    assert "templates/tachi/" in entries, "INSTALL_MANIFEST.md must keep its `templates/tachi/` entry"
    assert VERSION_PATH.is_file(), f"{VERSION_REL} must exist inside that entry's folder"
    assert _tracked_placeholder() == PLACEHOLDER


# README manual-loop write case: lands here after T048 adds the loop's marker line on part-b (red before).
