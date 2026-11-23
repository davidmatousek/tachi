"""Completeness tests for ``INSTALL_MANIFEST.md`` and the manual install loop.

Feature 373 (K1/K2, US-1/US-5). Normative contract:
``specs/373-adopter-install-output-fidelity/contracts/manifest-completeness.md``.
Required-set definitions: ``specs/373-adopter-install-output-fidelity/data-model.md``
Sec. 1 (the install manifest block) and Sec. 2 (n/a here -- K3 has its own
harness in ``test_install_sh_symlink_preflight.py`` /
``test_install_sh_ref_restore.py``).

This module is part of the W1 cut line: it is the ONLY module the
``manifest-completeness`` job in ``.github/workflows/tachi-install-fidelity.yml``
invokes (the pre-existing extraction modules join that workflow afterward, in
their own commit). It does NOT import ``install_sh_helpers.py`` -- that
module builds symlink sandboxes for K3's installer tests and has nothing to
do with manifest completeness.

Four required-set categories (data-model.md Sec. 1), each with a cardinality
floor verified non-vacuous at HEAD:
    (a) every ``.claude/skills/tachi-*`` directory                (>= 21)
    (b) every ``.claude/commands/tachi.*.md`` file                (>= 6)
    (c) every ``scripts/*.py`` a distributed doc references       (>= 4)
    (d) the transitive closure of those scripts' local imports    (>= 1)

Plus: manifest reader parity with ``scripts/install.sh``'s own
``parse_manifest`` (byte-for-byte, never a regex); entry hygiene; a
fail-closed exclusion list for (c); the S-13 stdlib-only-imports assertion;
a negative matrix (one case per category, plus marker and hygiene defects);
a manifest-driven, ``.git``-less end-to-end install; and the manual install
loop that must read byte-identical (and comment-free) across README.md and
both ``docs/guides/DEVELOPER_GUIDE_TACHI.md`` blocks, executable under both
bash and (when present) interactive zsh.

Feature 391 (T028) adds two groups at the end of the module. (1) The
isolated-operation runbook (``docs/guides/ISOLATED_OPERATION_TACHI.md``) is a
row of the manifest's docs table, an entry of its block, and a file that
``install.sh`` places. (2) SC-A4: after each documented install path (the
installer, the manual loop under bash, the manual loop under zsh) every
installed agent's ``tools:`` set equals its row in section 8 of
``docs/standards/CLAUDE_PERMISSIONS.md``. Both sides are read with the CI
guard's own parser (``scripts/check-agent-privileges.py``, loaded by path), so
the test and the guard cannot disagree about a cell or a ``tools:`` shape; a
synthetic negative matrix keeps the comparison from going vacuous. Nothing
here reads the version marker (Part B).
"""

from __future__ import annotations

import ast
import functools
import importlib.util
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "INSTALL_MANIFEST.md"
README_PATH = REPO_ROOT / "README.md"
DEV_GUIDE_PATH = REPO_ROOT / "docs" / "guides" / "DEVELOPER_GUIDE_TACHI.md"
SCRIPTS_DIR = REPO_ROOT / "scripts"

SKILLS_ROOT = REPO_ROOT / ".claude" / "skills"
AGENTS_ROOT = REPO_ROOT / ".claude" / "agents" / "tachi"
COMMANDS_ROOT = REPO_ROOT / ".claude" / "commands"
TEMPLATES_ROOT = REPO_ROOT / "templates" / "tachi"

BEGIN_MARKER = "<!-- BEGIN MANIFEST -->"
END_MARKER = "<!-- END MANIFEST -->"
LOOP_BEGIN_MARKER = "<!-- BEGIN MANUAL INSTALL LOOP -->"
LOOP_END_MARKER = "<!-- END MANUAL INSTALL LOOP -->"

# FR-K2.4's root-anchored reference pattern, widened to also catch a
# "./scripts/" spelling (the PRD's pattern, per spec Group A / K2).
SCRIPT_REF_RE = re.compile(r"(?<![\w./-])(?:\./)?scripts/[\w-]+\.py")

# Fail-closed exclusion list (FR-K2.4): {path: reason}. A distributed
# reference this scan matches that is NOT in the manifest and NOT here fails
# test_referenced_scripts_covered. Every other distributed reference
# (extract-report-data.py, extract-infographic-data.py,
# populate-affected-assets.py, tachi_parsers.py, tachi_parts.py,
# tachi_scoring.py, tachi_scoring_rules.py, sarif_common.py, tachi-stage.py,
# render-risk-scores.py) is a required script.
EXCLUDED: dict[str, str] = {
    # F-374 (T022). sarif-identity-shared.md's dormant `threats.sarif` section names the generator that takes over
    # when it ships. Until then the file is still written under sarif-specification.md, and the script stays
    # tachi-internal: ADR-050 D1 rewrites it and installs it at PR 2. T114 adds it to the manifest, and deletes this
    # entry in the same commit.
    "scripts/generate-threats-sarif.py": "named by the dormant threats.sarif section; installed at PR 2 (ADR-050 D1, T114)",
}

# The distributable scripts (spec FR-K2.1, NFR-2, S-13) -- named
# explicitly rather than derived from the reference scan, so S-13 keeps
# checking each of them even if the scan's result set ever changes. The F-374
# scripts (ADR-050 D16) join the original four, wave by wave: W1's three
# helpers (imported by the entries) and tachi-stage.py (an entry), then W2's
# tachi_scoring_rules.py (a helper) and render-risk-scores.py (an entry).
REQUIRED_SCRIPT_NAMES = (
    "extract-report-data.py",
    "extract-infographic-data.py",
    "tachi_parsers.py",
    "populate-affected-assets.py",
    "tachi_parts.py",
    "tachi_scoring.py",
    "sarif_common.py",
    "tachi-stage.py",
    "tachi_scoring_rules.py",
    "render-risk-scores.py",
)

# The sibling modules a distributable script may import at module load besides the standard library: the
# distributed helpers themselves. S-13 widens from tachi_parsers alone to each helper as it ships (ADR-050 D16).
DISTRIBUTED_HELPERS = frozenset(
    {"tachi_parsers", "tachi_parts", "tachi_scoring", "tachi_scoring_rules", "sarif_common"}
)


# ---------------------------------------------------------------------------
# Manifest reader (parity with scripts/install.sh's parse_manifest)
# ---------------------------------------------------------------------------


def read_manifest(text: str) -> list[str]:
    """Mirror ``scripts/install.sh``'s ``parse_manifest()`` exactly.

    Splits on ``"\\n"`` only -- never ``str.splitlines()``, which also
    breaks on ``\\r``, ``\\x0b``, ``\\x0c`` and the U+2028/U+2029 line
    separators, none of which install.sh's ``IFS= read -r`` loop treats as a
    line terminator. Matches the BEGIN/END markers by exact string equality
    (never a regex, matching ``[ "$line" = "..." ]``). Inside the block,
    skips a blank line or one whose first character is ``#`` (mirrors
    ``case "$line" in ""|\\#*) continue ;; esac``), and never strips a
    surviving line, because ``IFS= read -r`` disables word-splitting and
    backslash processing but does not trim whitespace.
    """
    lines = text.split("\n")
    begin_count = lines.count(BEGIN_MARKER)
    end_count = lines.count(END_MARKER)
    assert begin_count == 1, f"expected exactly one {BEGIN_MARKER!r} line, found {begin_count}"
    assert end_count == 1, f"expected exactly one {END_MARKER!r} line, found {end_count}"

    entries: list[str] = []
    inside = False
    for line in lines:
        if line == BEGIN_MARKER:
            inside = True
            continue
        if line == END_MARKER:
            inside = False
            continue
        if inside and line != "" and not line.startswith("#"):
            entries.append(line)
    return entries


def _manifest_text() -> str:
    return MANIFEST_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def manifest_text() -> str:
    return _manifest_text()


@pytest.fixture(scope="module")
def manifest_entries(manifest_text: str) -> list[str]:
    return read_manifest(manifest_text)


# ---------------------------------------------------------------------------
# Coverage relation (data-model.md Sec. 1)
# ---------------------------------------------------------------------------


def covers(entries: list[str], required: str) -> bool:
    """A required path ``required`` is covered by some entry E when E == P,
    or E is a directory entry (ends "/") that is a strict prefix of P.

    Callers of this module always spell a directory ``required`` path WITH
    its trailing "/", which collapses the coverage relation's third clause
    (P a directory, E == P + "/") into the first (E == P) -- so it is not
    encoded as a separate branch here.
    """
    for entry in entries:
        if entry == required:
            return True
        if entry.endswith("/") and required.startswith(entry):
            return True
    return False


def _assert_path_covered(entries: list[str], path: str, category: str) -> None:
    assert covers(entries, path), (
        f"INSTALL_MANIFEST.md is missing {path} ({category}). "
        "Add it to the block between the BEGIN/END MANIFEST markers."
    )


# ---------------------------------------------------------------------------
# Required-set derivation
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=None)
def _skill_dir_names() -> tuple[str, ...]:
    return tuple(sorted(p.name for p in SKILLS_ROOT.glob("tachi-*") if p.is_dir()))


@functools.lru_cache(maxsize=None)
def _command_file_names() -> tuple[str, ...]:
    return tuple(sorted(p.name for p in COMMANDS_ROOT.glob("tachi.*.md") if p.is_file()))


def _distributed_files() -> list[Path]:
    """Every file the pinned distributed globs cover (spec FR-K2.4 Scope).

    Walked with per-root ``rglob`` rather than a single ``**`` pattern
    string, sidestepping any ambiguity in how a given Python version
    matches a bare ``**`` path component against zero intermediate
    directories.

    T036 L-7 (code-reviewer-373.md): scans every FILE under each root
    (``rglob("*")`` + ``is_file()``), not just ``*.md``. The scope is the
    manifest's own ``**`` globs (data-model.md Sec. 1) -- every file, not
    a markdown subset. 18 ``.typ`` files sit under ``templates/tachi/``,
    and two reference ``scripts/extract-report-data.py`` (including
    main.typ's K13-posture panic text, T036 L-6); today they are also
    covered via a ``.md`` reference, so a script referenced ONLY from a
    non-markdown file would otherwise pass this guard with nothing
    scanning for it. ``COMMANDS_ROOT`` keeps its own ``tachi.*.md`` glob
    unchanged -- that root's required set (data-model.md Sec. 1 category
    (b)) is itself defined as "every .md command file," not "every file
    under commands/," so widening it here would scan files the manifest
    was never meant to require in the first place.
    """
    files: list[Path] = []
    files.extend(sorted(COMMANDS_ROOT.glob("tachi.*.md")))
    files.extend(sorted(p for p in AGENTS_ROOT.rglob("*") if p.is_file()))
    for skill_dir in sorted(SKILLS_ROOT.glob("tachi-*")):
        if skill_dir.is_dir():
            files.extend(sorted(p for p in skill_dir.rglob("*") if p.is_file()))
    files.extend(sorted(p for p in TEMPLATES_ROOT.rglob("*") if p.is_file()))
    return files


@functools.lru_cache(maxsize=None)
def _scan_referenced_scripts() -> frozenset[str]:
    refs: set[str] = set()
    for path in _distributed_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in SCRIPT_REF_RE.findall(text):
            refs.add(match[2:] if match.startswith("./") else match)
    return frozenset(refs)


def _module_level_import_nodes(tree: ast.Module) -> list[ast.stmt]:
    """Import/ImportFrom nodes reachable at module load time.

    Descends into If/Try/With bodies (their contents run at import time
    too), but never into a FunctionDef, AsyncFunctionDef or ClassDef body --
    those only execute when called or instantiated, which "imported at
    module load" (S-13; data-model.md Sec. 1) excludes by definition.
    """
    nodes: list[ast.stmt] = []

    def walk(stmts: list[ast.stmt]) -> None:
        """Collect Import/ImportFrom nodes from ``stmts`` into ``nodes``.

        Recurses into If/Try/TryStar/With bodies, never into function or class bodies.
        """
        for stmt in stmts:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                nodes.append(stmt)
            elif isinstance(stmt, ast.If):
                walk(stmt.body)
                walk(stmt.orelse)
            elif isinstance(stmt, ast.Try):
                walk(stmt.body)
                for handler in stmt.handlers:
                    walk(handler.body)
                walk(stmt.orelse)
                walk(stmt.finalbody)
            elif hasattr(ast, "TryStar") and isinstance(stmt, ast.TryStar):
                walk(stmt.body)
                for handler in stmt.handlers:
                    walk(handler.body)
                walk(stmt.orelse)
                walk(stmt.finalbody)
            elif isinstance(stmt, (ast.With, ast.AsyncWith)):
                walk(stmt.body)
            # FunctionDef / AsyncFunctionDef / ClassDef: do not descend.

    walk(tree.body)
    return nodes


def _resolve_local_imports(script_path: Path) -> set[str]:
    """Local sibling ``scripts/<name>.py`` files imported at module load."""
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    names: set[str] = set()
    for node in _module_level_import_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif node.module:
            names.add(node.module.split(".")[0])

    resolved: set[str] = set()
    for name in names:
        candidate = SCRIPTS_DIR / f"{name}.py"
        if candidate.is_file() and candidate.resolve() != script_path.resolve():
            resolved.add(f"scripts/{name}.py")
    return resolved


def _import_closure(seed_refs: set[str]) -> set[str]:
    """Every ``scripts/<name>.py`` reachable via local imports from
    ``seed_refs``, transitively.

    Returns every discovered edge target, including one that also happens
    to already be in ``seed_refs`` for an unrelated reason: the cardinality
    floor (data-model.md Sec. 1, "(d) >= 1") counts set (d) on its own
    terms, not "new beyond (c)".
    """
    discovered: set[str] = set()
    walked: set[str] = set()
    frontier = list(seed_refs)
    while frontier:
        ref = frontier.pop()
        if ref in walked:
            continue
        walked.add(ref)
        script_path = REPO_ROOT / ref
        if not script_path.is_file():
            continue
        for local in _resolve_local_imports(script_path):
            discovered.add(local)
            if local not in walked:
                frontier.append(local)
    return discovered


def _all_required_paths() -> list[str]:
    """The union of required-set categories (a)-(d), data-model.md Sec. 1."""
    paths: list[str] = []
    paths.extend(f".claude/skills/{name}/" for name in _skill_dir_names())
    paths.extend(f".claude/commands/{name}" for name in _command_file_names())
    non_excluded = sorted(frozenset(_scan_referenced_scripts()) - set(EXCLUDED))
    paths.extend(non_excluded)
    paths.extend(sorted(_import_closure(set(non_excluded))))
    return paths


def _assert_required_set_exists(root: Path) -> None:
    for rel in _all_required_paths():
        target = root / rel[:-1] if rel.endswith("/") else root / rel
        assert target.exists(), f"expected {rel!r} to exist under {root} after install"


# ---------------------------------------------------------------------------
# test_skills_covered / test_commands_covered / test_referenced_scripts_covered
# / test_import_closure_covered (required set (a)-(d))
# ---------------------------------------------------------------------------


def _assert_all_covered(entries: list[str], required: list[str], category: str) -> None:
    """Batched sibling of :func:`_assert_path_covered`.

    Reports EVERY missing path in one assertion (not just the first),
    joined but each still following the contract's per-path message shape,
    so a single CI run's output is enough to see every gap at once.
    """
    missing = [path for path in required if not covers(entries, path)]
    assert not missing, (
        "INSTALL_MANIFEST.md is missing "
        + ", ".join(missing)
        + f" ({category}). Add them to the block between the BEGIN/END MANIFEST markers."
    )


def test_skills_covered(manifest_entries: list[str]) -> None:
    names = _skill_dir_names()
    assert len(names) >= 21, f"expected >= 21 tachi-* skill dirs, found {len(names)}: {names}"
    required = [f".claude/skills/{name}/" for name in names]
    _assert_all_covered(manifest_entries, required, "skills, category a")


def test_commands_covered(manifest_entries: list[str]) -> None:
    names = _command_file_names()
    assert len(names) >= 6, f"expected >= 6 tachi.*.md command files, found {len(names)}: {names}"
    required = [f".claude/commands/{name}" for name in names]
    _assert_all_covered(manifest_entries, required, "commands, category b")


def test_referenced_scripts_covered(manifest_entries: list[str]) -> None:
    refs = _scan_referenced_scripts()
    assert len(refs) >= 4, f"expected >= 4 scripts/*.py references, found {len(refs)}: {sorted(refs)}"
    required = sorted(ref for ref in refs if ref not in EXCLUDED)
    _assert_all_covered(manifest_entries, required, "scripts, category c")


def test_import_closure_covered(manifest_entries: list[str]) -> None:
    non_excluded = frozenset(_scan_referenced_scripts()) - set(EXCLUDED)
    closure = _import_closure(set(non_excluded))
    assert len(closure) >= 1, (
        f"expected >= 1 transitively-imported local script (tachi_parsers), found {len(closure)}"
    )
    _assert_all_covered(manifest_entries, sorted(closure), "imports, category d")


# ---------------------------------------------------------------------------
# test_distributable_imports_stdlib_only (S-13, NFR-2)
# ---------------------------------------------------------------------------


def test_distributable_imports_stdlib_only() -> None:
    """S-13/NFR-2: required distributable scripts import only stdlib or a distributed helper.

    A distributed helper is one of ``DISTRIBUTED_HELPERS``: ``tachi_parsers`` and, from F-374
    (ADR-050 D16), ``tachi_parts``, ``tachi_scoring``, ``tachi_scoring_rules`` and ``sarif_common``.
    Each is itself a required script, so an import of one can never name a file that isn't installed.

    Checks module-level imports only (see ``_module_level_import_nodes``);
    needs Python 3.10+ for ``sys.stdlib_module_names``.
    """
    if sys.version_info < (3, 10):
        pytest.skip("sys.stdlib_module_names requires Python >= 3.10 (S-13)")

    assert {Path(name).stem for name in REQUIRED_SCRIPT_NAMES} >= DISTRIBUTED_HELPERS, (
        "every distributed helper must itself be a required script"
    )
    allowed = set(sys.stdlib_module_names) | DISTRIBUTED_HELPERS
    for name in REQUIRED_SCRIPT_NAMES:
        path = SCRIPTS_DIR / name
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in _module_level_import_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top in allowed, (
                        f"{name}: module-level `import {alias.name}` (line {node.lineno}) "
                        "is neither stdlib nor a distributed helper (NFR-2, S-13)"
                    )
            else:
                top = (node.module or "").split(".")[0]
                assert top in allowed, (
                    f"{name}: module-level `from {node.module} import ...` (line {node.lineno}) "
                    "is neither stdlib nor a distributed helper (NFR-2, S-13)"
                )


# ---------------------------------------------------------------------------
# test_manifest_hygiene / test_negative_matrix (FR-K2.5)
# ---------------------------------------------------------------------------


def _hygiene_violations(entries: list[str]) -> list[str]:
    """FR-K2.5: list the manifest entries that break the hygiene rules.

    Flags surrounding whitespace, a leading '/', '~' or '<!--', a '..'
    segment, and any entry that is a path prefix of another entry.
    """
    violations: list[str] = []
    for entry in entries:
        if entry != entry.strip():
            violations.append(f"{entry!r} has leading or trailing whitespace")
            continue
        if entry.startswith("/"):
            violations.append(f"{entry!r} starts with '/'")
            continue
        if entry.startswith("~"):
            violations.append(f"{entry!r} starts with '~'")
            continue
        if entry.startswith("<!--"):
            violations.append(
                f"{entry!r} starts with '<!--' (install.sh would copy it as an entry; "
                "the manual loop drops it)"
            )
            continue
        if ".." in entry.split("/"):
            violations.append(f"{entry!r} contains a '..' segment")
            continue

    for i, entry_a in enumerate(entries):
        for j, entry_b in enumerate(entries):
            if i != j and entry_a != entry_b and entry_b.startswith(entry_a):
                violations.append(f"{entry_a!r} is a path prefix of {entry_b!r}")

    return violations


def test_manifest_hygiene(manifest_text: str, manifest_entries: list[str]) -> None:
    lines = manifest_text.split("\n")
    assert lines.count(BEGIN_MARKER) == 1, f"expected exactly one {BEGIN_MARKER!r} line"
    assert lines.count(END_MARKER) == 1, f"expected exactly one {END_MARKER!r} line"
    assert len(manifest_entries) >= 1, "the manifest block yielded zero entries"

    violations = _hygiene_violations(manifest_entries)
    assert not violations, "INSTALL_MANIFEST.md hygiene violations: " + "; ".join(violations)


def test_negative_matrix(manifest_entries: list[str], manifest_text: str) -> None:
    # (a) skills: remove one required skill-dir entry.
    victim = ".claude/skills/tachi-shared/"
    assert victim in manifest_entries, "test setup assumption broken: entry not present"
    modified = [e for e in manifest_entries if e != victim]
    with pytest.raises(AssertionError, match=re.escape(f"INSTALL_MANIFEST.md is missing {victim}")):
        _assert_path_covered(modified, victim, "skills, category a")

    # (b) commands: remove one required command entry.
    victim = ".claude/commands/tachi.threat-model.md"
    assert victim in manifest_entries, "test setup assumption broken: entry not present"
    modified = [e for e in manifest_entries if e != victim]
    with pytest.raises(AssertionError, match=re.escape(f"INSTALL_MANIFEST.md is missing {victim}")):
        _assert_path_covered(modified, victim, "commands, category b")

    # (c) scripts: remove one required script entry.
    victim = "scripts/extract-report-data.py"
    assert victim in manifest_entries, "test setup assumption broken: entry not present"
    modified = [e for e in manifest_entries if e != victim]
    with pytest.raises(AssertionError, match=re.escape(f"INSTALL_MANIFEST.md is missing {victim}")):
        _assert_path_covered(modified, victim, "scripts, category c")

    # (d) import closure: remove tachi_parsers.py.
    victim = "scripts/tachi_parsers.py"
    assert victim in manifest_entries, "test setup assumption broken: entry not present"
    modified = [e for e in manifest_entries if e != victim]
    with pytest.raises(AssertionError, match=re.escape(f"INSTALL_MANIFEST.md is missing {victim}")):
        _assert_path_covered(modified, victim, "imports, category d")

    # A leading-space entry fails hygiene.
    modified = list(manifest_entries)
    modified[0] = " " + modified[0]
    assert _hygiene_violations(modified), "expected a leading-space entry to be flagged"

    # A duplicated BEGIN marker: read_manifest itself must reject it.
    duplicated = manifest_text.replace(BEGIN_MARKER, BEGIN_MARKER + "\n" + BEGIN_MARKER, 1)
    with pytest.raises(AssertionError):
        read_manifest(duplicated)

    # A missing END marker: read_manifest itself must reject it.
    missing_end = manifest_text.replace(END_MARKER, "", 1)
    with pytest.raises(AssertionError):
        read_manifest(missing_end)

    # A nested entry pair: one entry is a path prefix of another.
    modified = list(manifest_entries) + [".claude/skills/tachi-shared/nested-example.md"]
    violations = _hygiene_violations(modified)
    assert any("prefix" in v for v in violations), (
        f"expected a nested-entry-pair violation, got: {violations}"
    )


# ---------------------------------------------------------------------------
# test_end_to_end_install (rev. 1)
# ---------------------------------------------------------------------------


def _build_source_from_manifest(entries: list[str], dest_root: Path) -> None:
    """Build a ``--source``-shaped tree at ``dest_root`` from ONLY what the
    manifest lists, plus ``scripts/install.sh`` itself (which the manifest
    never lists, since it is not something the installer copies INTO a
    target project).

    Manifest-driven rather than a whole-tree copy: a real working tree can
    hold large untracked or ignored content a whole-tree copy would drag in
    (contract, rev. 1: a 29 MB ``.venv`` with symlinks is the cited case).
    Driving the copy from the manifest loses nothing for THIS test's
    purpose: a required path missing from the manifest is then also missing
    from ``dest_root``, so a completeness regression still fails the
    assertion this exists to protect.
    """
    dest_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MANIFEST_PATH, dest_root / "INSTALL_MANIFEST.md")

    scripts_dest = dest_root / "scripts"
    scripts_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPTS_DIR / "install.sh", scripts_dest / "install.sh")

    for entry in entries:
        src = REPO_ROOT / entry
        dst = dest_root / entry
        if entry.endswith("/"):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def test_end_to_end_install(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    project_root = tmp_path / "project"
    project_root.mkdir()

    _build_source_from_manifest(read_manifest(_manifest_text()), src_root)
    assert not (src_root / ".git").exists(), (
        "test setup bug: a .git dir would let install.sh's post-copy "
        "`git fetch --tags` run for real"
    )

    result = subprocess.run(
        ["/bin/bash", str(src_root / "scripts" / "install.sh")],
        cwd=project_root,
        env={**os.environ, "LC_ALL": "C"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"install.sh exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    _assert_required_set_exists(project_root)


# ---------------------------------------------------------------------------
# test_manual_install_loop / test_manual_install_loop_zsh (RC-4, rev. 1)
# ---------------------------------------------------------------------------


_COMMENT_LINE_RE = re.compile(r"(^|[ \t])#")


def _extract_all_between_markers(text: str, begin: str, end: str) -> list[str]:
    """All blocks strictly between paired ``begin``/``end`` marker lines.

    A file may hold more than one marker pair (the developer guide has
    two); each pair is extracted independently, in document order.
    """
    lines = text.split("\n")
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i] == begin:
            try:
                j = lines.index(end, i)
            except ValueError as exc:
                raise AssertionError(
                    f"{begin!r} at line {i + 1} has no matching {end!r}"
                ) from exc
            blocks.append("\n".join(lines[i + 1 : j]))
            i = j + 1
        else:
            i += 1
    return blocks


def _shell_script_from_loop_block(block: str) -> str:
    """Strip the ```bash / ``` fence lines, leaving the runnable shell text."""
    lines = block.split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[0].strip() == "```bash", f"expected an opening ```bash fence, got {lines[0]!r}"
    assert lines[-1].strip() == "```", f"expected a closing ``` fence, got {lines[-1]!r}"
    return "\n".join(lines[1:-1])


def _rewritten_loop_script(tachi_path: Path) -> str:
    """The README's loop block, with its first line's ``TACHI=`` rewritten
    to point at ``tachi_path`` (a throwaway, manifest-driven copy -- never
    the developer's real clone).
    """
    readme_blocks = _extract_all_between_markers(
        README_PATH.read_text(encoding="utf-8"), LOOP_BEGIN_MARKER, LOOP_END_MARKER
    )
    assert len(readme_blocks) == 1, (
        f"expected exactly 1 manual-install-loop block in README.md, found {len(readme_blocks)}"
    )
    script_lines = _shell_script_from_loop_block(readme_blocks[0]).split("\n")
    assert script_lines[0].startswith("TACHI="), (
        f"expected the loop's first line to set TACHI=, got {script_lines[0]!r}"
    )
    script_lines[0] = f"TACHI={shlex.quote(str(tachi_path))}"
    return "\n".join(script_lines)


def _snapshot_relative_paths(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*")}


def test_manual_install_loop(tmp_path: Path) -> None:
    readme_blocks = _extract_all_between_markers(
        README_PATH.read_text(encoding="utf-8"), LOOP_BEGIN_MARKER, LOOP_END_MARKER
    )
    dev_guide_blocks = _extract_all_between_markers(
        DEV_GUIDE_PATH.read_text(encoding="utf-8"), LOOP_BEGIN_MARKER, LOOP_END_MARKER
    )
    assert len(readme_blocks) == 1, (
        f"expected exactly 1 manual-install-loop block in README.md, found {len(readme_blocks)}"
    )
    assert len(dev_guide_blocks) == 2, (
        "expected exactly 2 manual-install-loop blocks in "
        f"docs/guides/DEVELOPER_GUIDE_TACHI.md, found {len(dev_guide_blocks)}"
    )

    labeled_blocks = [("README.md", readme_blocks[0])]
    labeled_blocks += [
        (f"docs/guides/DEVELOPER_GUIDE_TACHI.md[{i}]", block)
        for i, block in enumerate(dev_guide_blocks)
    ]
    reference_label, reference_block = labeled_blocks[0]
    for label, block in labeled_blocks[1:]:
        assert block == reference_block, (
            f"manual-install-loop block in {label} differs from {reference_label} "
            "(all three must be byte-identical)"
        )

    for line in reference_block.split("\n"):
        assert not _COMMENT_LINE_RE.search(line), (
            f"manual-install-loop block contains a comment-shaped line: {line!r} "
            "(interactive zsh does not treat '#' as a comment by default)"
        )

    src_root = tmp_path / "src"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _build_source_from_manifest(read_manifest(_manifest_text()), src_root)
    script = _rewritten_loop_script(src_root)
    run_env = {**os.environ, "LC_ALL": "C"}

    result = subprocess.run(
        ["/bin/bash", "-c", script],
        cwd=project_root,
        env=run_env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"manual install loop exited {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    _assert_required_set_exists(project_root)

    before = _snapshot_relative_paths(project_root)
    result2 = subprocess.run(
        ["/bin/bash", "-c", script],
        cwd=project_root,
        env=run_env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result2.returncode == 0, (
        f"second manual install loop run exited {result2.returncode}\n"
        f"stdout:\n{result2.stdout}\nstderr:\n{result2.stderr}"
    )
    after = _snapshot_relative_paths(project_root)
    assert after == before, (
        "second run changed the installed file set (possible nested duplication): "
        f"added={sorted(after - before)}, removed={sorted(before - after)}"
    )


def test_manual_install_loop_zsh(tmp_path: Path) -> None:
    if shutil.which("zsh") is None:
        pytest.skip("zsh not on PATH (ubuntu runners may lack it)")

    src_root = tmp_path / "src"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _build_source_from_manifest(read_manifest(_manifest_text()), src_root)
    script = _rewritten_loop_script(src_root)

    result = subprocess.run(
        ["zsh", "-f", "-i"],
        input=script,
        cwd=project_root,
        env={**os.environ, "LC_ALL": "C"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"zsh -f -i exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    _assert_required_set_exists(project_root)


# ---------------------------------------------------------------------------
# F-391 (T028): the runbook's manifest entries, and SC-A4 (the installed
# agents' tools equal the section 8 matrix on every documented install path)
# ---------------------------------------------------------------------------

RUNBOOK_REL = "docs/guides/ISOLATED_OPERATION_TACHI.md"
MATRIX_PATH = REPO_ROOT / "docs" / "standards" / "CLAUDE_PERMISSIONS.md"
GUARD_PATH = SCRIPTS_DIR / "check-agent-privileges.py"


def _fresh_install_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """A manifest-driven, ``.git``-less source tree and an empty project.

    Built the way the existing install cases build theirs, so a path that
    installs from this source is the same path those cases exercise.
    """
    src_root = tmp_path / "src"
    project_root = tmp_path / "project"
    project_root.mkdir()
    _build_source_from_manifest(read_manifest(_manifest_text()), src_root)
    assert not (src_root / ".git").exists(), (
        "test setup bug: a .git dir would let install.sh's post-copy "
        "`git fetch --tags` run for real"
    )
    return src_root, project_root


def _require_clean_exit(result: subprocess.CompletedProcess, label: str) -> None:
    assert result.returncode == 0, (
        f"{label} exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def _install_via_install_sh(tmp_path: Path) -> Path:
    """Install with ``scripts/install.sh``; returns the project root."""
    src_root, project_root = _fresh_install_dirs(tmp_path)
    result = subprocess.run(
        ["/bin/bash", str(src_root / "scripts" / "install.sh")],
        cwd=project_root,
        env={**os.environ, "LC_ALL": "C"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    _require_clean_exit(result, "install.sh")
    return project_root


def _install_via_manual_loop(tmp_path: Path) -> Path:
    """Install with the README's manual loop under bash; returns the project root."""
    src_root, project_root = _fresh_install_dirs(tmp_path)
    result = subprocess.run(
        ["/bin/bash", "-c", _rewritten_loop_script(src_root)],
        cwd=project_root,
        env={**os.environ, "LC_ALL": "C"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    _require_clean_exit(result, "the manual install loop (bash)")
    return project_root


def _install_via_manual_loop_zsh(tmp_path: Path) -> Path:
    """Install with the README's manual loop under interactive zsh; returns the project root."""
    if shutil.which("zsh") is None:
        pytest.skip("zsh not on PATH (ubuntu runners may lack it)")
    src_root, project_root = _fresh_install_dirs(tmp_path)
    result = subprocess.run(
        ["zsh", "-f", "-i"],
        input=_rewritten_loop_script(src_root),
        cwd=project_root,
        env={**os.environ, "LC_ALL": "C"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    _require_clean_exit(result, "the manual install loop (zsh -f -i)")
    return project_root


# ---------------------------------------------------------------------------
# The runbook's manifest entries (T018 edits the manifest; these pin it)
# ---------------------------------------------------------------------------


def _distributable_table_paths(text: str) -> list[str]:
    """Paths in the first cell of each row of the manifest's docs table.

    The table sits under the ``## Distributable Directories`` heading. A first
    cell reads as a backticked path, optionally followed by a note; the header
    and separator rows have no backticked first cell and are skipped.
    """
    heading = "## Distributable Directories"
    lines = text.split("\n")
    assert lines.count(heading) == 1, f"expected exactly one {heading!r} line in the manifest"
    paths: list[str] = []
    for line in lines[lines.index(heading) + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("|"):
            match = re.match(r"`([^`]+)`", line.split("|")[1].strip())
            if match:
                paths.append(match.group(1))
    return paths


def test_runbook_in_manifest_docs_table(manifest_text: str) -> None:
    paths = _distributable_table_paths(manifest_text)
    assert "docs/guides/DEVELOPER_GUIDE_TACHI.md" in paths, (
        f"test setup assumption broken: the developer guide's docs row was not read, got {paths}"
    )
    assert RUNBOOK_REL in paths, (
        f"INSTALL_MANIFEST.md's Distributable Directories table has no row for {RUNBOOK_REL}. "
        "Add one next to the developer guide's row."
    )

    # Negative control: the same text without the runbook's row must not list it.
    without_row = "\n".join(
        line for line in manifest_text.split("\n") if not line.startswith(f"| `{RUNBOOK_REL}`")
    )
    assert without_row != manifest_text, "test setup assumption broken: the row was not found"
    assert RUNBOOK_REL not in _distributable_table_paths(without_row)


def test_runbook_in_manifest_block(manifest_entries: list[str]) -> None:
    assert RUNBOOK_REL in manifest_entries, (
        f"INSTALL_MANIFEST.md is missing {RUNBOOK_REL} (docs, runbook). "
        "Add it to the block between the BEGIN/END MANIFEST markers."
    )
    assert (REPO_ROOT / RUNBOOK_REL).is_file(), (
        f"{RUNBOOK_REL} is in the manifest block but is not a file in the repository"
    )


def test_end_to_end_install_places_runbook(tmp_path: Path) -> None:
    project_root = _install_via_install_sh(tmp_path)
    placed = project_root / RUNBOOK_REL
    assert placed.is_file(), f"install.sh did not place {RUNBOOK_REL} in the project"
    assert placed.read_bytes() == (REPO_ROOT / RUNBOOK_REL).read_bytes(), (
        f"the installed {RUNBOOK_REL} differs from the source file"
    )


# ---------------------------------------------------------------------------
# SC-A4: the installed agents' tools equal the section 8 rows
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=None)
def _guard() -> ModuleType:
    """``scripts/check-agent-privileges.py``, loaded from its path (the hyphen rules out ``import``).

    Both sides of SC-A4 are read with this module: section 8 by its table
    parser, each agent's ``tools:`` by its frontmatter reader. The test and the
    CI guard therefore agree on the cell syntax and on every accepted
    ``tools:`` shape (block list, flow list, comma string).
    """
    assert GUARD_PATH.is_file(), (
        f"{GUARD_PATH} is missing: SC-A4 reads section 8 and each tools: with the guard's parser"
    )
    spec = importlib.util.spec_from_file_location("check_agent_privileges", str(GUARD_PATH))
    assert spec is not None and spec.loader is not None, (
        f"cannot build an import spec for {GUARD_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _section8_tool_sets() -> dict[str, frozenset[str]]:
    """Agent ``name:`` -> the Tools cell of its section 8 row."""
    guard = _guard()
    try:
        matrix = guard.parse_matrix(MATRIX_PATH.read_text(encoding="utf-8-sig"))
    except guard.InfraError as exc:
        raise AssertionError(
            f"the guard cannot parse section 8 of {MATRIX_PATH.name}: {exc}"
        ) from exc
    rows = {name: row.tools for name, row in matrix.agents.items()}
    assert len(rows) >= 21, f"expected >= 21 agent rows in section 8, found {len(rows)}"
    return rows


def _installed_agent_tool_sets(agents_dir: Path) -> dict[str, frozenset[str]]:
    """Agent ``name:`` -> its ``tools:`` set, for each agent file under ``agents_dir``.

    A ``*.md`` file with leading frontmatter is an agent (the guard's C1 rule);
    one without (``_TACHI_AGENT_BEST_PRACTICES.md``) is a document and is
    skipped. A missing ``name:`` or ``tools:`` key, an unreadable ``tools:``
    shape and a repeated name all fail here: an agent without ``tools:``
    inherits every tool, so it can never "match".
    """
    guard = _guard()
    assert agents_dir.is_dir(), f"no agents directory was installed at {agents_dir}"
    installed: dict[str, frozenset[str]] = {}
    origin: dict[str, str] = {}
    for path in sorted(agents_dir.rglob("*.md")):
        rel = path.relative_to(agents_dir).as_posix()
        try:
            agent = guard.load_agent_file(path, rel, rel)
            if agent is None:
                continue
            assert "name" in agent.entries, f"{rel}: frontmatter has no name: key"
            assert "tools" in agent.entries, (
                f"{rel}: no tools: key (an agent without tools: inherits every tool)"
            )
            name = guard.parse_scalar(agent.entries["name"], "name")
            tools = frozenset(guard.parse_tools(agent.entries["tools"]))
        except guard.InfraError as exc:
            raise AssertionError(
                f"{rel}: the guard's parser cannot read this agent: {exc}"
            ) from exc
        assert name not in installed, f"duplicate agent name {name!r} in {origin[name]} and {rel}"
        installed[name] = tools
        origin[name] = rel
    return installed


def _tools_drift(
    installed: dict[str, frozenset[str]], expected: dict[str, frozenset[str]]
) -> list[str]:
    """Every way the installed agents differ from the section 8 rows (empty = they match)."""
    problems: list[str] = []
    for name in sorted(set(installed) | set(expected)):
        if name not in expected:
            problems.append(f"{name}: installed, but section 8 has no row for it")
        elif name not in installed:
            problems.append(f"{name}: section 8 lists it, but no installed agent file has that name")
        elif installed[name] != expected[name]:
            have, want = installed[name], expected[name]
            problems.append(
                f"{name}: installed tools {sorted(have)} differ from the section 8 row "
                f"{sorted(want)} (added {sorted(have - want)}, removed {sorted(want - have)})"
            )
    return problems


def _assert_installed_tools_match_matrix(
    project_root: Path, expected: dict[str, frozenset[str]], via: str
) -> None:
    # AOD-SIMPLIFICATION: tools only, as SC-A4 states -- upgrade: compare model: and the key set too
    agents_dir = project_root / ".claude" / "agents" / "tachi"
    installed = _installed_agent_tool_sets(agents_dir)
    problems = _tools_drift(installed, expected)
    assert not problems, (
        f"after {via}, the installed agents differ from section 8 of "
        "docs/standards/CLAUDE_PERMISSIONS.md: " + "; ".join(problems)
    )


_INSTALL_PATHS = {
    "install-sh": _install_via_install_sh,
    "manual-loop": _install_via_manual_loop,
    "manual-loop-zsh": _install_via_manual_loop_zsh,
}


@pytest.mark.parametrize("install_path", list(_INSTALL_PATHS))
def test_installed_agent_tools_match_matrix(install_path: str, tmp_path: Path) -> None:
    project_root = _INSTALL_PATHS[install_path](tmp_path)
    _assert_installed_tools_match_matrix(project_root, _section8_tool_sets(), install_path)


def _agent_text(name: str, tools_lines: str) -> str:
    """A minimal agent file; ``tools_lines`` is the whole ``tools:`` entry, or "" for none."""
    return (
        "---\n"
        f"name: {name}\n"
        'description: "synthetic agent for the SC-A4 negative controls"\n'
        f"{tools_lines}"
        "model: sonnet\n"
        "---\n"
        "# Synthetic agent\n"
    )


def _tools_block(tools: list[str]) -> str:
    """The block-list shape the real agent files use."""
    return "tools:\n" + "".join(f"  - {tool}\n" for tool in tools)


def test_installed_tools_negative_matrix(tmp_path: Path) -> None:
    base = _section8_tool_sets()
    victim = "tachi-spoofing"
    assert victim in base and base[victim] == {"Read", "Glob", "Grep"}, (
        "test setup assumption broken: section 8 no longer lists tachi-spoofing as Read, Glob, Grep"
    )
    ordered = sorted(base[victim])

    def project(label: str, mutate) -> Path:
        """A project whose agents match section 8, then ``mutate(agents_dir)``."""
        root = tmp_path / re.sub(r"\W+", "-", label)
        agents_dir = root / ".claude" / "agents" / "tachi"
        agents_dir.mkdir(parents=True)
        for name, tools in sorted(base.items()):
            text = _agent_text(name, _tools_block(sorted(tools)))
            (agents_dir / f"{name}.md").write_text(text, encoding="utf-8")
        mutate(agents_dir)
        return root

    def put(filename: str, name: str, tools_lines: str):
        """A mutation that writes one synthetic agent file (replacing it when it exists)."""

        def apply(agents_dir: Path) -> None:
            (agents_dir / filename).write_text(_agent_text(name, tools_lines), encoding="utf-8")

        return apply

    own = f"{victim}.md"
    without_grep = [t for t in ordered if t != "Grep"]
    grep_for_bash = ["Bash" if t == "Grep" else t for t in ordered]

    # Green: the unmutated tree, and the same set in the guard's other two accepted shapes.
    green = [
        ("unmutated tree", lambda agents_dir: None),
        ("block list", put(own, victim, _tools_block(ordered))),
        ("flow list", put(own, victim, "tools: [" + ", ".join(ordered) + "]\n")),
        ("comma string", put(own, victim, "tools: " + ", ".join(ordered) + "\n")),
    ]
    for label, mutate in green:
        _assert_installed_tools_match_matrix(project(label, mutate), base, label)

    # Red: each drift the assertion exists to catch, with the message that names it.
    red = [
        (
            "tool added",
            put(own, victim, _tools_block(ordered + ["Bash"])),
            r"added \['Bash'\], removed \[\]",
        ),
        (
            "tool removed",
            put(own, victim, _tools_block(without_grep)),
            r"added \[\], removed \['Grep'\]",
        ),
        (
            "tool swapped",
            put(own, victim, _tools_block(grep_for_bash)),
            r"added \['Bash'\], removed \['Grep'\]",
        ),
        ("no tools key", put(own, victim, ""), r"tachi-spoofing\.md: no tools: key"),
        (
            "unreadable tools shape",
            put(own, victim, "tools: {Read: 1}\n"),
            r"cannot read this agent",
        ),
        (
            "agent file missing",
            lambda agents_dir: (agents_dir / own).unlink(),
            r"tachi-spoofing: section 8 lists it",
        ),
        (
            "agent without a row",
            put("helper.md", "helper", _tools_block(ordered)),
            r"helper: installed, but section 8 has no row",
        ),
        (
            "duplicate agent name",
            put("copy.md", victim, _tools_block(ordered)),
            r"duplicate agent name 'tachi-spoofing'",
        ),
    ]
    for label, mutate, message in red:
        with pytest.raises(AssertionError, match=message):
            _assert_installed_tools_match_matrix(project(label, mutate), base, label)

    # Red, matrix side: the installed tree is untouched and one section 8 cell loses a tool.
    edited = {**base, victim: base[victim] - {"Grep"}}
    with pytest.raises(AssertionError, match=r"added \['Grep'\], removed \[\]"):
        _assert_installed_tools_match_matrix(
            project("matrix cell edited", lambda agents_dir: None), edited, "a section 8 edit"
        )
