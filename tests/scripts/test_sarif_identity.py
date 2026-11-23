"""Tests for the shared SARIF emitter in ``scripts/sarif_common.py`` (F-374 T016, T015; ADR-050 D7, D8).

``sarif_common`` is a helper, so the tests import it; there is no entry to drive. Every fixture
is synthetic. The cases follow the tasks, T016 first.

T016, the URI resolver (D7)
1. The fake filesystem these cases use
2. ``resolve_file``: the syntactic rule, the ``lstat`` walk, ``samefile`` and the spelling
3. Percent-encoding
4. The body line: where it sits and what reads as absent
5. ``resolve_architecture``: the three candidates, their order and every fallback warning
6. The same checks on a real filesystem, including a real case-insensitive volume

T015, the shared emitter (D7, D8)
7. Tools, categories and rule IDs
8. The ``tachi-plh/1`` hash and the two partial fingerprints
9. Correlation: assignments and ruling C's sentence
10. The result: shape, key order, evidence locations
11. The self-check, one violation at a time
12. The run, the document and the bytes
13. Identity across runs and across the three files (FR-E.2's model)
14. The taxa, against ``schemas/taxonomy``
15. Module hygiene and the legacy helpers

The fake filesystem is the offline stand-in for a case-insensitive volume (KB 24): it keeps each
entry's own spelling and finds an entry by its case-folded name, as macOS's default volume does,
so the case-variant cases run on every platform. Section 6 runs the same case on the real
volume when the test directory sits on one.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import itertools
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from ..conftest import _load_hyphenated_script

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common as sc  # noqa: E402  -- after the sys.path mutation
import tachi_parsers  # noqa: E402
import tachi_parts  # noqa: E402
import tachi_scoring  # noqa: E402


# =============================================================================
# 1. The fake filesystem
# =============================================================================


class FakeFilesystem:
    """An in-memory filesystem with inode identities, symlinks, hard links and case folding.

    It has the four methods the resolver calls (``getcwd``, ``lstat``, ``stat``, ``listdir``).
    With ``case_insensitive`` a lookup that misses by exact name falls back to the case-folded
    name, and a listing always shows the entry's own spelling.
    """

    def __init__(self, cwd: str = "/repo", case_insensitive: bool = False) -> None:
        self.case_insensitive = case_insensitive
        self._inode = 1000
        self._root = self._node("dir")
        self._cwd = cwd
        self.unreadable: set = set()
        self.mkdir(cwd)

    def _node(self, kind: str, target: str = "") -> dict:
        self._inode += 1
        return {"kind": kind, "ino": self._inode, "target": target, "kids": {} if kind == "dir" else None}

    # -- building -------------------------------------------------------------

    def mkdir(self, path: str) -> None:
        node = self._root
        for part in [p for p in path.split("/") if p]:
            node = node["kids"].setdefault(part, self._node("dir"))

    def file(self, path: str) -> None:
        parent, name = path.rsplit("/", 1)
        self.mkdir(parent or "/")
        self._dir(parent or "/")["kids"][name] = self._node("file")

    def symlink(self, path: str, target: str) -> None:
        parent, name = path.rsplit("/", 1)
        self.mkdir(parent or "/")
        self._dir(parent or "/")["kids"][name] = self._node("link", target)

    def link(self, existing: str, new: str) -> None:
        """A hard link: a second name for the same inode."""
        parent, name = new.rsplit("/", 1)
        self.mkdir(parent or "/")
        self._dir(parent or "/")["kids"][name] = self._find(existing, follow_last=False)

    # -- lookup ---------------------------------------------------------------

    def _child(self, directory: dict, name: str) -> dict:
        if name in directory["kids"]:
            return directory["kids"][name]
        if self.case_insensitive:
            for own, node in directory["kids"].items():
                if own.casefold() == name.casefold():
                    return node
        raise FileNotFoundError(2, "No such file or directory", name)

    def _find(self, path: str, follow_last: bool, depth: int = 0) -> dict:
        if depth > 16:
            raise OSError(40, "Too many levels of symbolic links", path)
        node = self._root
        parts = [p for p in path.split("/") if p]
        for index, part in enumerate(parts):
            if node["kind"] != "dir":
                raise NotADirectoryError(20, "Not a directory", path)
            node = self._child(node, part)
            if node["kind"] == "link" and (follow_last or index < len(parts) - 1):
                rest = "/".join(parts[index + 1:])
                target = node["target"]
                joined = target if not rest else target.rstrip("/") + "/" + rest
                return self._find(joined, follow_last, depth + 1)
        return node

    def _dir(self, path: str) -> dict:
        node = self._find(path, follow_last=True)
        if node["kind"] != "dir":
            raise NotADirectoryError(20, "Not a directory", path)
        return node

    @staticmethod
    def _stat(node: dict) -> SimpleNamespace:
        kind = {"dir": stat.S_IFDIR | 0o755, "file": stat.S_IFREG | 0o644, "link": stat.S_IFLNK | 0o777}[node["kind"]]
        return SimpleNamespace(st_mode=kind, st_dev=7, st_ino=node["ino"])

    # -- the four calls the resolver makes ------------------------------------

    def getcwd(self) -> str:
        return self._cwd

    def lstat(self, path: str) -> SimpleNamespace:
        return self._stat(self._find(path, follow_last=False))

    def stat(self, path: str) -> SimpleNamespace:
        return self._stat(self._find(path, follow_last=True))

    def listdir(self, path: str) -> list:
        if path in self.unreadable:
            raise PermissionError(13, "Permission denied", path)
        return list(self._dir(path)["kids"])


def make_repo(case_insensitive: bool = False) -> FakeFilesystem:
    """A small repository with a run directory that holds the snapshot ``/tachi.threat-model`` copied."""
    fs = FakeFilesystem("/repo", case_insensitive=case_insensitive)
    for path in (
        "/repo/README.md",
        "/repo/docs/security/architecture.md",
        "/repo/docs/design/architecture.md",
        "/repo/docs/design/other.md",
        "/repo/docs/My Design/architecture.md",
        "/repo/docs/\u00e9tude/arch#1+%.md",
        "/repo/threat-model/run1/threats.md",
        "/repo/threat-model/run1/architecture.md",
        "/repo/threat-model/run1/other.md",
    ):
        fs.file(path)
    return fs


def resolved(path: str, fs: FakeFilesystem, **kwargs) -> "sc.ResolvedPath":
    return sc.resolve_file(path, root="/repo", fs=fs, **kwargs)


def refusal(path, fs: FakeFilesystem, **kwargs) -> str:
    """The failed check's name for a path the resolver must refuse."""
    with pytest.raises(sc.PathCheckError) as excinfo:
        sc.resolve_file(path, root="/repo", fs=fs, **kwargs)
    assert isinstance(excinfo.value, ValueError)
    return excinfo.value.check


# =============================================================================
# 2. resolve_file: the rule, the lstat walk, samefile and the spelling
# =============================================================================


def test_a_plain_relative_path_resolves_to_itself():
    got = resolved("docs/security/architecture.md", make_repo())
    assert got == ("docs/security/architecture.md", "docs/security/architecture.md")
    assert isinstance(got, sc.ResolvedPath) and got.path == got.uri


def test_dot_and_empty_components_are_dropped():
    assert resolved("./docs//security/./architecture.md", make_repo()).path == "docs/security/architecture.md"


@pytest.mark.parametrize("path,check", [
    ("", "empty"), (".", "empty"), ("../x.md", "parent-reference"), ("docs/../README.md", "parent-reference"),
    ("docs\\security\\architecture.md", "backslash"), ("docs/`x`.md", "backtick"), ("docs/a\nb.md", "control-char"),
    ("docs/a\x00b.md", "control-char"), ("C:/docs/architecture.md", "drive-letter"), ("https://x.test/a.md", "scheme"),
    ("/docs/architecture.md", "leading-slash"), ("a" * 4097, "too-long"), ("docs/a\udc80b.md", "encoding"),
    (None, "type"), (7, "type"), (b"docs/a.md", "type"),
])
def test_the_syntactic_rule_is_tachi_parts_and_names_the_failed_check(path, check):
    fs = make_repo()
    assert refusal(path, fs) == check
    assert tachi_parts.path_problem(path) == check  # the same name, from the one rule


def test_the_syntactic_rule_is_imported_not_restated():
    import ast

    tree = ast.parse((SCRIPTS_DIR / "sarif_common.py").read_text(encoding="utf-8"))
    names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert {"path_problem", "path_parts", "PATH_MAX_BYTES"} <= names
    assert sc.MAX_PATH_BYTES == tachi_parts.PATH_MAX_BYTES == 4096


@pytest.mark.parametrize("path,check", [
    ("docs/security/missing.md", "missing"),
    ("nodir/architecture.md", "missing"),
    ("docs/security", "not-a-regular-file"),
    ("docs", "not-a-regular-file"),
    ("README.md/extra.md", "not-a-directory"),
])
def test_the_lstat_walk_needs_every_component_to_exist_and_the_last_to_be_a_regular_file(path, check):
    assert refusal(path, make_repo()) == check


def test_a_symlink_leaf_is_refused():
    fs = make_repo()
    fs.symlink("/repo/docs/linked.md", "/repo/docs/security/architecture.md")
    assert refusal("docs/linked.md", fs) == "symlink"


def test_a_symlinked_directory_in_the_middle_is_refused():
    fs = make_repo()
    fs.symlink("/repo/alias", "/repo/docs")
    assert refusal("alias/security/architecture.md", fs) == "symlink"


def test_a_dangling_symlink_is_refused_as_a_symlink_not_as_missing():
    fs = make_repo()
    fs.symlink("/repo/docs/dangling.md", "/repo/nowhere.md")
    assert refusal("docs/dangling.md", fs) == "symlink"


def test_an_unreadable_parent_directory_is_refused_with_its_own_name():
    fs = make_repo()
    fs.unreadable.add("/repo/docs/security")
    assert refusal("docs/security/architecture.md", fs) == "unreadable"


def test_a_component_that_cannot_be_examined_is_refused_as_unreadable_not_as_missing():
    class NoSearchPermission(FakeFilesystem):
        def lstat(self, path):
            if path == "/repo/docs/security":
                raise PermissionError(13, "Permission denied", path)
            return super().lstat(path)

    fs = NoSearchPermission("/repo")
    fs.file("/repo/docs/security/architecture.md")
    assert refusal("docs/security/architecture.md", fs) == "unreadable"


def test_an_absolute_path_counts_when_an_ancestor_is_the_working_directory_and_is_made_relative():
    got = resolved("/repo/docs/security/architecture.md", make_repo(), allow_absolute=True)
    assert got.path == "docs/security/architecture.md"


def test_an_absolute_path_is_refused_when_absolute_paths_are_not_allowed():
    assert refusal("/repo/docs/security/architecture.md", make_repo()) == "leading-slash"


def test_an_absolute_path_through_a_symlinked_ancestor_of_the_root_is_the_same_directory_by_samefile():
    fs = make_repo()
    fs.symlink("/alias", "/repo")  # /alias is /repo, spelled differently
    got = resolved("/alias/docs/security/architecture.md", fs, allow_absolute=True)
    assert got.path == "docs/security/architecture.md"


@pytest.mark.parametrize("path", ["/etc/passwd", "/repository/docs/security/architecture.md", "/docs/security/architecture.md"])
def test_an_absolute_path_with_no_ancestor_that_is_the_working_directory_is_outside_the_root(path):
    fs = make_repo()
    fs.file("/etc/passwd")
    fs.file("/repository/docs/security/architecture.md")
    fs.file("/docs/security/architecture.md")
    assert refusal(path, fs, allow_absolute=True) == "outside-root"


def test_an_absolute_path_naming_the_working_directory_itself_is_not_a_file():
    assert refusal("/repo", make_repo(), allow_absolute=True) == "not-a-regular-file"


def test_the_root_must_be_absolute():
    with pytest.raises(ValueError):
        sc.resolve_file("a.md", root="repo", fs=make_repo())


# --- the spelling: file identity, never the typed name -------------------------


def test_a_case_variant_gives_the_same_path_and_uri_on_a_case_insensitive_volume():
    fs = make_repo(case_insensitive=True)
    canonical = resolved("docs/security/architecture.md", fs)
    for variant in ("Docs/Security/Architecture.md", "DOCS/SECURITY/ARCHITECTURE.MD", "docs/SECURITY/architecture.MD"):
        got = resolved(variant, fs)
        assert got == canonical, variant
    assert canonical.path == "docs/security/architecture.md"


def test_the_spelling_is_the_directorys_own_name_even_when_it_has_capitals():
    fs = FakeFilesystem("/repo", case_insensitive=True)
    fs.file("/repo/Docs/Security/Architecture.MD")
    assert resolved("docs/security/architecture.md", fs).path == "Docs/Security/Architecture.MD"
    assert resolved("DOCS/security/ARCHITECTURE.md", fs).path == "Docs/Security/Architecture.MD"


def test_an_absolute_case_variant_is_made_relative_and_respelled():
    fs = make_repo(case_insensitive=True)
    got = resolved("/REPO/Docs/security/ARCHITECTURE.md", fs, allow_absolute=True)
    assert got.path == "docs/security/architecture.md"


def test_on_a_case_sensitive_volume_a_case_variant_is_a_different_path_and_does_not_exist():
    assert refusal("Docs/security/architecture.md", make_repo(case_insensitive=False)) == "missing"


def test_a_case_variant_of_a_symlink_is_still_refused():
    fs = make_repo(case_insensitive=True)
    fs.symlink("/repo/docs/Linked.md", "/repo/docs/security/architecture.md")
    assert refusal("DOCS/linked.MD", fs) == "symlink"


def test_the_typed_name_wins_a_tie_between_two_names_for_one_inode():
    fs = FakeFilesystem("/repo")
    fs.file("/repo/docs/zeta.md")
    fs.link("/repo/docs/zeta.md", "/repo/docs/alpha.md")  # a hard link: two names, one inode
    assert resolved("docs/zeta.md", fs).path == "docs/zeta.md"
    assert resolved("docs/alpha.md", fs).path == "docs/alpha.md"


def test_with_no_typed_match_the_lowest_code_point_wins_a_tie():
    fs = FakeFilesystem("/repo", case_insensitive=True)
    fs.file("/repo/docs/Zeta.md")
    fs.link("/repo/docs/Zeta.md", "/repo/docs/alpha.md")
    # "ALPHA.md" matches alpha.md by case, yet both names are one inode and neither is typed:
    # "Z" (U+005A) sorts before "a" (U+0061), so the lowest code point is Zeta.md.
    assert resolved("docs/ALPHA.md", fs).path == "docs/Zeta.md"
    assert resolved("docs/ZETA.MD", fs).path == "docs/Zeta.md"


def test_two_different_files_with_close_names_are_never_confused():
    fs = FakeFilesystem("/repo", case_insensitive=True)
    fs.file("/repo/docs/architecture.md")
    fs.file("/repo/docs/architecture.md.bak")
    assert resolved("DOCS/Architecture.md.BAK", fs).path == "docs/architecture.md.bak"


def test_a_spelling_with_no_entry_of_that_identity_is_refused_not_guessed():
    class Racy(FakeFilesystem):
        def listdir(self, path):
            return ["something-else.md"]  # the directory changed between the lstat and the listing

    fs = Racy("/repo")
    fs.file("/repo/docs/architecture.md")
    assert refusal("docs/architecture.md", fs) == "spelling"


# =============================================================================
# 3. Percent-encoding (RFC 3986: everything but the unreserved characters and "/")
# =============================================================================


@pytest.mark.parametrize("component,encoded", [
    ("architecture.md", "architecture.md"),
    ("A-z_0.9~", "A-z_0.9~"),
    ("My Design", "My%20Design"),
    ("arch#1+%.md", "arch%231%2B%25.md"),
    ("\u00e9tude", "%C3%A9tude"),
    ("\u65e5\u672c", "%E6%97%A5%E6%9C%AC"),
    ("a:b@c!d$e&f'g(h)i*j,k;l=m", "a%3Ab%40c%21d%24e%26f%27g%28h%29i%2Aj%2Ck%3Bl%3Dm"),
    ("", ""),
])
def test_percent_encode_keeps_only_the_unreserved_characters(component, encoded):
    assert sc.percent_encode(component) == encoded


def test_percent_encode_uses_upper_case_hex_and_utf8():
    assert sc.percent_encode("\u00ff") == "%C3%BF"
    assert sc.percent_encode("\n") == "%0A"


def test_percent_encode_refuses_a_lone_surrogate():
    with pytest.raises(UnicodeEncodeError):
        sc.percent_encode("a\udc80")


def test_the_uri_is_the_canonical_path_percent_encoded_component_by_component():
    fs = make_repo()
    spaced = resolved("docs/My Design/architecture.md", fs)
    assert (spaced.path, spaced.uri) == ("docs/My Design/architecture.md", "docs/My%20Design/architecture.md")
    odd = resolved("docs/\u00e9tude/arch#1+%.md", fs)
    assert odd.path == "docs/\u00e9tude/arch#1+%.md"
    assert odd.uri == "docs/%C3%A9tude/arch%231%2B%25.md"


def test_a_name_on_disk_that_is_not_valid_unicode_is_refused_by_the_encoding_check():
    class UndecodableNames(FakeFilesystem):
        """os.listdir shows an undecodable byte as a lone surrogate; the entry has the typed file's identity."""

        def listdir(self, path):
            return ["\udc80" + name if name == "architecture.md" else name for name in super().listdir(path)]

        def lstat(self, path):
            return super().lstat(path.replace("\udc80", ""))

    fs = UndecodableNames("/repo")
    fs.file("/repo/docs/architecture.md")
    assert refusal("docs/architecture.md", fs) == "encoding"


# =============================================================================
# 4. The body line
# =============================================================================

LINE = "**Architecture source**: `docs/security/architecture.md`"


def threats(*, front=True, title="# Threat Model", body="", after="## 1. System Overview\n\ntext\n"):
    head = '---\nschema_version: "1.7"\ndate: "2026-11-22"\n---\n\n' if front else ""
    return "%s%s\n\n%s%s" % (head, title, body, after)


def test_the_line_is_read_between_the_frontmatter_and_the_first_h2_heading():
    assert sc.read_architecture_source(threats(body=LINE + "\n\n")) == "docs/security/architecture.md"


def test_the_line_is_read_without_frontmatter_and_directly_after_it():
    assert sc.read_architecture_source(threats(front=False, body=LINE + "\n\n")) == "docs/security/architecture.md"
    text = '---\na: 1\n---\n%s\n## 1. Overview\n' % LINE
    assert sc.read_architecture_source(text) == "docs/security/architecture.md"


def test_the_line_is_read_with_crlf_line_endings():
    text = threats(body=LINE + "\n\n").replace("\n", "\r\n")
    assert sc.read_architecture_source(text) == "docs/security/architecture.md"


@pytest.mark.parametrize("text", [
    threats(body=""),                                                    # zero matches
    threats(body=LINE + "\n\n" + LINE + "\n\n"),                         # several matches, even if equal
    threats(body=LINE + "\n\n**Architecture source**: `docs/a.md`\n\n"),  # several, different
    threats(after="## 1. System Overview\n\n" + LINE + "\n"),            # after the first H2
    threats(body="```\n" + LINE + "\n```\n\n"),                          # inside a backtick fence
    threats(body="~~~\n" + LINE + "\n~~~\n\n"),                          # inside a tilde fence
    threats(body="````\n```\n" + LINE + "\n```\n````\n\n"),              # a shorter fence does not close a longer one
    threats(body="  " + LINE + "\n\n"),                                  # not at column 0
    threats(body="> " + LINE + "\n\n"),                                  # inside a block quote
    threats(body="**Architecture source**: docs/security/architecture.md\n\n"),  # no backticks
    threats(body="**Architecture source**: `docs/a.md` and `docs/b.md`\n\n"),    # two spans
    threats(body="**Architecture source**: `docs/a.md` trailing\n\n"),
    threats(body="**Architecture Source**: `docs/a.md`\n\n"),            # wrong case
    threats(body="**Architecture source**: ``\n\n"),                     # empty span
    "",
])
def test_zero_matches_or_several_or_a_misplaced_line_read_as_absent(text):
    assert sc.read_architecture_source(text) is None


def test_a_line_forged_inside_a_prose_line_by_a_separator_character_is_not_a_line():
    # str.splitlines() would split on U+2028, \x0b, \x0c and \x85, and show a line that
    # the author never wrote. Only "\n" ends a line here.
    for separator in ("\u2028", "\u2029", "\x0b", "\x0c", "\x85", "\r"):
        text = threats(body="prose" + separator + LINE + "\n\n")
        assert sc.read_architecture_source(text) is None, repr(separator)


def test_a_line_inside_the_frontmatter_is_not_the_body_line():
    forged = '---\n**Architecture source**: `docs/forged.md`\n---\n\n# T\n\n' + LINE + "\n\n## 1. Overview\n"
    assert sc.read_architecture_source(forged) == "docs/security/architecture.md"
    only_forged = '---\n**Architecture source**: `docs/forged.md`\n---\n\n# T\n\n## 1. Overview\n'
    assert sc.read_architecture_source(only_forged) is None


def test_a_yaml_comment_that_looks_like_a_heading_in_the_frontmatter_does_not_end_the_region():
    text = '---\n## a yaml comment\n---\n\n# T\n\n' + LINE + "\n\n## 1. Overview\n"
    assert sc.read_architecture_source(text) == "docs/security/architecture.md"


def test_a_fence_that_never_closes_hides_the_rest_of_the_region():
    assert sc.read_architecture_source(threats(body="```\n" + LINE + "\n\n")) is None


def test_a_heading_inside_a_fence_does_not_end_the_region():
    body = "```\n## not a heading\n```\n\n" + LINE + "\n\n"
    assert sc.read_architecture_source(threats(body=body)) == "docs/security/architecture.md"


def test_deeper_headings_do_not_end_the_region_but_h2_headings_do():
    assert sc.read_architecture_source(threats(body="### Sub\n\n" + LINE + "\n\n")) == "docs/security/architecture.md"
    assert sc.read_architecture_source(threats(body="## Early\n\n" + LINE + "\n\n")) is None


def test_the_region_and_the_line_spans_let_the_upsert_replace_or_cut_the_line():
    text = threats(body=LINE + "\n\n")
    (start, end, path), = sc.find_architecture_source_lines(text)
    assert text[start:end] == LINE + "\n" and path == "docs/security/architecture.md"
    region_start, region_end = sc.architecture_source_region(text)
    assert region_start <= start < end <= region_end
    assert text[region_end:].startswith("## 1. System Overview")
    assert (text[:start] + text[end:]).count("Architecture source") == 0


def test_the_region_of_a_text_with_no_heading_runs_to_the_end():
    text = "# Title\n\nprose\n"
    assert sc.architecture_source_region(text) == (0, len(text))


def test_an_unterminated_frontmatter_is_not_skipped():
    text = "---\nschema_version: 1\n" + LINE + "\n"
    assert sc.read_architecture_source(text) == "docs/security/architecture.md"


def test_the_line_is_formatted_from_a_canonical_path_and_round_trips():
    assert sc.format_architecture_source_line("docs/security/architecture.md") == LINE
    line = sc.format_architecture_source_line("docs/My Design/a b.md")
    assert sc.read_architecture_source("# T\n\n" + line + "\n") == "docs/My Design/a b.md"


@pytest.mark.parametrize("path", ["", "a`b", "a\nb", "../x", "https://x/y", "a\\b"])
def test_a_path_the_line_could_not_carry_is_refused_by_the_formatter(path):
    with pytest.raises(ValueError):
        sc.format_architecture_source_line(path)


# =============================================================================
# 5. resolve_architecture: the three candidates, in order
# =============================================================================


def resolve(fs, explicit=None, body=None, run_dir="/repo/threat-model/run1", **kwargs):
    text = None if body is None else threats(body=("" if body == "" else sc.format_architecture_source_line(body) + "\n\n"))
    return sc.resolve_architecture(explicit, threats_text=text, run_dir=run_dir, root="/repo", fs=fs, **kwargs)


def codes(result):
    return [w["code"] for w in result.warnings]


def test_the_flag_comes_first_and_a_good_flag_leaves_no_warning():
    got = resolve(make_repo(), explicit="docs/design/architecture.md", body="docs/security/architecture.md")
    assert (got.path, got.uri, got.source, got.warnings) == (
        "docs/design/architecture.md", "docs/design/architecture.md", "explicit", ())


def test_the_body_line_comes_second_and_a_good_line_leaves_no_warning():
    got = resolve(make_repo(), body="docs/design/architecture.md")
    assert (got.path, got.source, got.warnings) == ("docs/design/architecture.md", "body-line", ())


def test_the_default_comes_last_and_a_missing_line_warns_and_names_the_flag():
    got = resolve(make_repo(), body="")
    assert (got.path, got.uri, got.source) == ("docs/security/architecture.md", "docs/security/architecture.md", "default")
    assert codes(got) == ["architecture-path:body-line:absent"]
    detail = got.warnings[0]["detail"]
    assert "architecture-source line" in detail and "absent" in detail and "--architecture-path" in detail


def test_with_no_threats_md_there_is_no_line_and_the_warning_says_so():
    got = sc.resolve_architecture(None, threats_text=None, run_dir=None, root="/repo", fs=make_repo())
    assert got.source == "default" and codes(got) == ["architecture-path:body-line:absent"]
    assert "no threats.md was read" in got.warnings[0]["detail"]


def test_the_default_is_used_in_its_canonical_spelling_on_a_case_insensitive_volume():
    fs = FakeFilesystem("/repo", case_insensitive=True)
    fs.file("/repo/Docs/Security/Architecture.md")
    got = sc.resolve_architecture(None, root="/repo", fs=fs)
    assert (got.path, got.source) == ("Docs/Security/Architecture.md", "default")


def test_a_body_line_naming_an_architecture_md_outside_docs_security_resolves_to_that_path():
    got = resolve(make_repo(), body="docs/design/architecture.md")
    assert got.uri == "docs/design/architecture.md" and got.source == "body-line"


@pytest.mark.parametrize("flag,check", [
    ("docs/security/missing.md", "missing"), ("../outside.md", "parent-reference"), ("/etc/passwd", "outside-root"),
    ("docs", "not-a-regular-file"), ("docs\\x", "backslash"), ("", "empty"),
])
def test_a_failed_flag_falls_to_the_body_line_with_a_warning_that_names_the_candidate_the_check_and_the_flag(flag, check):
    fs = make_repo()
    fs.file("/etc/passwd")
    got = resolve(fs, explicit=flag, body="docs/design/architecture.md")
    assert got.source == "body-line" and got.path == "docs/design/architecture.md"
    assert codes(got) == ["architecture-path:explicit:%s" % check]
    detail = got.warnings[0]["detail"]
    assert "--architecture path" in detail and check in detail and "--architecture-path" in detail


def test_a_failed_flag_and_an_absent_line_fall_to_the_default_with_two_warnings_in_order():
    got = resolve(make_repo(), explicit="docs/nope.md", body="")
    assert got.source == "default"
    assert codes(got) == ["architecture-path:explicit:missing", "architecture-path:body-line:absent"]


def test_a_failed_line_falls_to_the_default_with_a_warning():
    got = resolve(make_repo(), body="docs/security/missing.md")
    assert got.source == "default" and codes(got) == ["architecture-path:body-line:missing"]


def test_the_flag_first_the_line_second_the_default_third_across_all_eight_combinations():
    fs = make_repo()
    cases = []
    for flag in (None, "docs/design/other.md", "docs/missing.md"):
        for body in (None, "", "docs/design/architecture.md", "docs/missing.md"):
            got = resolve(fs, explicit=flag, body=body)
            expected = (
                "docs/design/other.md" if flag == "docs/design/other.md"
                else "docs/design/architecture.md" if body == "docs/design/architecture.md"
                else "docs/security/architecture.md"
            )
            assert got.path == expected, (flag, body)
            cases.append((flag, body))
    assert len(cases) == 12


def test_when_the_default_does_not_validate_it_is_emitted_literally_with_a_warning():
    fs = FakeFilesystem("/repo")
    fs.file("/repo/README.md")
    got = sc.resolve_architecture(None, threats_text=threats(body=""), run_dir=None, root="/repo", fs=fs)
    assert (got.path, got.uri, got.source) == (sc.DEFAULT_ARCHITECTURE_PATH,) * 2 + ("default-literal",)
    assert codes(got) == ["architecture-path:body-line:absent", "architecture-path:default:missing"]
    assert "--architecture-path" in got.warnings[-1]["detail"]


def test_a_run_always_gets_a_path_whatever_fails():
    fs = FakeFilesystem("/repo")
    got = sc.resolve_architecture("", threats_text="x", run_dir="", root="/repo", fs=fs)
    assert got.path == sc.DEFAULT_ARCHITECTURE_PATH and got.source == "default-literal"
    assert len(got.warnings) == 3


def test_a_flag_that_is_a_case_variant_gives_the_same_uri_as_the_canonical_flag():
    fs = make_repo(case_insensitive=True)
    one = resolve(fs, explicit="docs/design/architecture.md")
    two = resolve(fs, explicit="DOCS/Design/ARCHITECTURE.md")
    three = resolve(fs, explicit="/REPO/docs/DESIGN/architecture.MD")
    assert one.uri == two.uri == three.uri == "docs/design/architecture.md"


# --- resolve_explicit: the resolver's first step, which `tachi-stage.py plan` runs too (ruled at W2, ADR-050 D7) --------


def explicit_of(fs, candidate, **kwargs):
    return sc.resolve_explicit(candidate, root="/repo", fs=fs, **kwargs)


def test_a_candidate_that_passes_comes_back_resolved_and_with_no_warning():
    fs = make_repo()
    got, warning = explicit_of(fs, "docs/design/architecture.md")
    assert warning is None
    assert got == sc.resolve_file("docs/design/architecture.md", root="/repo", allow_absolute=True, fs=fs)
    assert (got.path, got.uri) == ("docs/design/architecture.md", "docs/design/architecture.md")


def test_the_candidate_may_be_an_absolute_path_below_the_root_as_the_flag_may():
    got, warning = explicit_of(make_repo(), "/repo/docs/design/./architecture.md")
    assert warning is None and (got.path, got.uri) == ("docs/design/architecture.md", "docs/design/architecture.md")


def test_the_candidate_is_spelled_as_the_volume_spells_it():
    got, warning = explicit_of(make_repo(case_insensitive=True), "DOCS/Design/ARCHITECTURE.md")
    assert warning is None and got.path == "docs/design/architecture.md"


REFUSED = [  # the candidate, then the failed check: the filesystem ones, and the syntactic ones that `plan` used to exit 2 for
    ("docs/security/missing.md", "missing"), ("../outside.md", "parent-reference"), ("/etc/passwd", "outside-root"),
    ("docs", "not-a-regular-file"), ("docs/design/link.md", "symlink"), ("docs/architecture.md/x", "not-a-directory"),
    ("docs\\x", "backslash"), ("docs/a`b.md", "backtick"), ("docs/a\nb.md", "control-char"), ("docs/a\tb.md", "control-char"),
    ("", "empty"), ("./", "empty"), ("https://example.invalid/a.md", "scheme"), ("C:docs/a.md", "drive-letter"),
    ("docs/" + "x" * 5000, "too-long"), ("docs/\udc80.md", "encoding"), (None, "type"), (7, "type"), (b"docs/a.md", "type"),
]


def refusing_repo():
    fs = make_repo()
    fs.file("/etc/passwd")
    fs.file("/repo/docs/architecture.md")
    fs.symlink("/repo/docs/design/link.md", "other.md")
    return fs


@pytest.mark.parametrize("candidate,check", REFUSED, ids=[check + ":" + repr(candidate)[:20] for candidate, check in REFUSED])
def test_a_refused_candidate_comes_back_with_no_path_and_the_resolvers_own_warning(candidate, check):
    got, warning = explicit_of(refusing_repo(), candidate)
    assert got is None
    assert set(warning) == {"code", "detail"} and warning["code"] == "architecture-path:explicit:%s" % check
    detail = warning["detail"]
    assert "--architecture path" in detail and ("%s check" % check) in detail and "--architecture-path" in detail
    assert sc._short(candidate) in detail, "the candidate, in its escaped short form"
    assert len(detail) < 500 and detail.isprintable(), "a stage record's warning rules: at most 500 characters, nothing a record forbids"


@pytest.mark.parametrize("candidate,check", [case for case in REFUSED if case[0] is not None],
                         ids=[check + ":" + repr(candidate)[:20] for candidate, check in REFUSED if candidate is not None])
def test_plan_and_the_renderer_agree_on_the_warning_for_every_refusal(candidate, check):
    """``resolve_architecture`` runs this step first, so its first warning is this one, whatever check fails. (``None`` is
    the flag not given, which ``resolve_architecture`` never asks this step about.)"""
    fs = refusing_repo()
    _got, warning = explicit_of(fs, candidate)
    chain = sc.resolve_architecture(candidate, threats_text=None, run_dir=None, root="/repo", fs=fs)
    assert chain.warnings[0] == warning, "plan records what the renderer would list first"
    assert chain.source in ("default", "default-literal") and "architecture-path:body-line:absent" in codes(chain)


def test_a_long_candidate_is_named_in_its_80_character_short_form_and_never_whole():
    candidate = "docs/" + "y" * 300
    detail = explicit_of(make_repo(), candidate)[1]["detail"]
    assert sc._short(candidate) in detail and candidate not in detail and len(sc._short(candidate)) == 80


def test_a_control_character_is_escaped_in_the_warning_and_a_record_can_carry_it():
    detail = explicit_of(make_repo(), "docs/\x00\u202e\u2028b.md")[1]["detail"]
    assert "\\x00" in detail and "\\u202e" in detail and "\\u2028" in detail
    tachi_parts.closed_string(detail, "architecture_warning.detail", 0, 500)   # the rule of a stage record's warning detail


def test_a_root_that_is_not_absolute_is_the_callers_bug_and_raises():
    with pytest.raises(ValueError):
        sc.resolve_explicit("docs/design/architecture.md", root="repo", fs=make_repo())


def test_the_root_and_the_filesystem_default_to_the_working_directory_and_the_real_one(tmp_path, monkeypatch):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "architecture.md").write_text("# a\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    got, warning = sc.resolve_explicit("docs/architecture.md")
    assert warning is None and got.path == "docs/architecture.md"
    refused, warning = sc.resolve_explicit("docs/absent.md")
    assert refused is None and warning["code"] == "architecture-path:explicit:missing"


# --- NFR-10's name check on the body line --------------------------------------


def test_a_body_line_with_no_snapshot_fails_closed():
    fs = make_repo()
    got = resolve(fs, body="docs/design/other.md", run_dir="/repo/threat-model/empty")
    assert got.source == "default" and codes(got) == ["architecture-path:body-line:no-snapshot"]


def test_a_body_line_with_no_run_directory_fails_closed():
    got = resolve(make_repo(), body="docs/design/architecture.md", run_dir=None)
    assert codes(got) == ["architecture-path:body-line:no-snapshot"]


def test_the_snapshot_is_found_by_the_basename_so_a_different_file_name_needs_its_own_snapshot():
    fs = make_repo()
    assert resolve(fs, body="docs/design/other.md").source == "body-line"  # run1/other.md is a snapshot
    fs.file("/repo/docs/design/third.md")
    assert codes(resolve(fs, body="docs/design/third.md")) == ["architecture-path:body-line:no-snapshot"]


def test_a_snapshot_that_is_a_symlink_or_a_directory_is_refused():
    fs = make_repo()
    fs.symlink("/repo/threat-model/run1/linked.md", "/repo/docs/design/other.md")
    fs.file("/repo/docs/design/linked.md")
    assert codes(resolve(fs, body="docs/design/linked.md")) == ["architecture-path:body-line:snapshot-not-regular"]
    fs.mkdir("/repo/threat-model/run1/dirsnap.md")
    fs.file("/repo/docs/design/dirsnap.md")
    assert codes(resolve(fs, body="docs/design/dirsnap.md")) == ["architecture-path:body-line:snapshot-not-regular"]


@pytest.mark.parametrize("name", list(sc.CANONICAL_OUTPUT_NAMES))
def test_a_body_line_cannot_name_a_tachi_output_even_when_a_snapshot_of_that_name_exists(name):
    fs = make_repo()
    fs.file("/repo/docs/design/" + name)
    fs.file("/repo/threat-model/run1/" + name)
    got = resolve(fs, body="docs/design/" + name)
    assert got.source == "default"
    assert codes(got) == ["architecture-path:body-line:canonical-name"]


def test_a_body_line_cannot_name_a_tachi_output_by_a_case_variant():
    fs = make_repo(case_insensitive=True)
    fs.file("/repo/docs/design/Threats.MD")
    got = resolve(fs, body="docs/design/threats.md")
    assert codes(got) == ["architecture-path:body-line:canonical-name"]


def test_a_body_line_cannot_name_the_per_run_snapshot_itself():
    got = resolve(make_repo(), body="threat-model/run1/architecture.md")
    assert got.source == "default" and codes(got) == ["architecture-path:body-line:is-snapshot"]


def test_a_body_line_naming_the_snapshot_through_a_case_variant_or_absolute_path_is_still_the_snapshot():
    fs = make_repo(case_insensitive=True)
    assert codes(resolve(fs, body="THREAT-MODEL/Run1/architecture.md")) == ["architecture-path:body-line:is-snapshot"]
    assert codes(resolve(fs, body="/repo/threat-model/run1/architecture.md")) == ["architecture-path:body-line:is-snapshot"]


def test_the_default_snapshot_name_architecture_md_passes():
    got = resolve(make_repo(), body="docs/security/architecture.md")
    assert got.source == "body-line" and got.warnings == ()


def test_the_name_check_applies_to_the_body_line_only_never_to_the_flag_or_the_default():
    got = resolve(make_repo(), explicit="README.md", run_dir=None)
    assert got.source == "explicit" and got.path == "README.md"  # no snapshot named README.md, and none needed


def test_a_relative_run_directory_is_taken_relative_to_the_root():
    got = resolve(make_repo(), body="docs/design/architecture.md", run_dir="threat-model/run1")
    assert got.source == "body-line"


def test_a_symlinked_body_line_candidate_is_refused_before_the_name_check():
    fs = make_repo()
    fs.symlink("/repo/docs/design/sym.md", "/repo/docs/design/architecture.md")
    assert codes(resolve(fs, body="docs/design/sym.md")) == ["architecture-path:body-line:symlink"]


# =============================================================================
# 6. The same checks on a real filesystem
# =============================================================================


def real(path, root, **kwargs):
    return sc.resolve_file(path, root=str(root), **kwargs)


@pytest.fixture()
def tree(tmp_path):
    (tmp_path / "docs" / "security").mkdir(parents=True)
    (tmp_path / "docs" / "security" / "architecture.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "docs" / "My Design").mkdir()
    (tmp_path / "docs" / "My Design" / "a#b.md").write_text("x", encoding="utf-8")
    (tmp_path / "README.md").write_text("r", encoding="utf-8")
    return tmp_path


def test_a_real_relative_and_a_real_absolute_path_give_the_same_result(tree):
    assert real("docs/security/architecture.md", tree) == ("docs/security/architecture.md",) * 2
    absolute = str(tree / "docs" / "security" / "architecture.md")
    assert real(absolute, tree, allow_absolute=True).path == "docs/security/architecture.md"


def test_a_real_path_is_encoded(tree):
    got = real("docs/My Design/a#b.md", tree)
    assert (got.path, got.uri) == ("docs/My Design/a#b.md", "docs/My%20Design/a%23b.md")


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="no symlinks on this platform")
def test_a_real_symlink_leaf_or_directory_is_refused(tree):
    os.symlink(tree / "README.md", tree / "link.md")
    os.symlink(tree / "docs", tree / "dlink")
    for path in ("link.md", "dlink/security/architecture.md"):
        with pytest.raises(sc.PathCheckError) as excinfo:
            real(path, tree)
        assert excinfo.value.check == "symlink"


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="no symlinks on this platform")
def test_a_real_absolute_path_through_a_symlinked_ancestor_is_the_same_directory_by_samefile(tree, tmp_path_factory):
    alias_parent = tmp_path_factory.mktemp("alias")
    os.symlink(tree, alias_parent / "repo")
    via = alias_parent / "repo" / "docs" / "security" / "architecture.md"
    assert real(str(via), tree, allow_absolute=True).path == "docs/security/architecture.md"
    # ...and from outside the root it is refused
    with pytest.raises(sc.PathCheckError) as excinfo:
        real(str(via), alias_parent / "other", allow_absolute=True)
    assert excinfo.value.check in ("outside-root", "missing", "unreadable")


@pytest.mark.skipif(not hasattr(os, "link"), reason="no hard links on this platform")
def test_a_real_hard_link_pair_resolves_to_the_typed_name(tree):
    try:
        os.link(tree / "docs" / "security" / "architecture.md", tree / "docs" / "security" / "Architecture-Alias.md")
    except OSError:
        pytest.skip("this filesystem refuses hard links")
    assert real("docs/security/architecture.md", tree).path == "docs/security/architecture.md"
    assert real("docs/security/Architecture-Alias.md", tree).path == "docs/security/Architecture-Alias.md"


def _case_insensitive(directory: Path) -> bool:
    probe = directory / "CaseProbe.tmp"
    probe.write_text("x", encoding="utf-8")
    try:
        return (directory / "caseprobe.TMP").exists()
    finally:
        probe.unlink()


def test_a_real_case_variant_gives_the_same_uri_on_a_real_case_insensitive_volume(tree):
    if not _case_insensitive(tree):
        pytest.skip("this volume is case-sensitive; the fake filesystem covers the case offline")
    canonical = real("docs/security/architecture.md", tree)
    for variant in ("Docs/Security/Architecture.md", "DOCS/SECURITY/ARCHITECTURE.MD"):
        assert real(variant, tree) == canonical
        assert real(str(tree / variant), tree, allow_absolute=True) == canonical


def test_the_real_resolver_defaults_to_the_working_directory(tree, monkeypatch):
    monkeypatch.chdir(tree)
    assert sc.resolve_file("docs/security/architecture.md").path == "docs/security/architecture.md"
    got = sc.resolve_architecture(None)
    assert got.source == "default" and [w["code"] for w in got.warnings] == ["architecture-path:body-line:absent"]


def test_the_real_architecture_resolution_walks_the_three_candidates(tree):
    run = tree / "threat-model" / "run1"
    run.mkdir(parents=True)
    (run / "architecture.md").write_text("snapshot", encoding="utf-8")
    (run / "threats.md").write_text("t", encoding="utf-8")
    body = sc.format_architecture_source_line("docs/security/architecture.md")
    text = "---\nschema_version: '1.7'\n---\n\n# T\n\n%s\n\n## 1. Overview\n" % body
    got = sc.resolve_architecture(None, threats_text=text, run_dir=str(run), root=str(tree))
    assert (got.source, got.path, got.warnings) == ("body-line", "docs/security/architecture.md", ())
    snapshot = sc.resolve_architecture(
        None, threats_text="# T\n\n" + sc.format_architecture_source_line("threat-model/run1/architecture.md") + "\n",
        run_dir=str(run), root=str(tree))
    assert snapshot.source == "default" and [w["code"] for w in snapshot.warnings] == ["architecture-path:body-line:is-snapshot"]


# =============================================================================
# 7. Tools, categories and rule IDs (T005's tables, written out independently)
# =============================================================================

SCORER, CONTROLS, THREATS = "tachi-risk-scorer", "tachi-control-analyzer", "Tachi"
URI = "docs/security/architecture.md"

EXPECTED_RULES = {
    "S": "tachi/stride/spoofing",
    "T": "tachi/stride/tampering",
    "R": "tachi/stride/repudiation",
    "I": "tachi/stride/information-disclosure",
    "D": "tachi/stride/denial-of-service",
    "E": "tachi/stride/elevation-of-privilege",
    "AG": "tachi/ai/agentic-threats",
    "AGP": "tachi/ai/agentic-threats",
    "TE": "tachi/ai/agentic-threats",
    "LLM": "tachi/ai/llm-threats",
    "OI": "tachi/ai/llm-threats",
    "MI": "tachi/ai/llm-threats",
}


def test_each_file_has_its_verbatim_tool_name_and_category_and_the_three_pairs_differ():
    assert sc.TOOL_NAMES == {
        "threats.sarif": "Tachi",
        "risk-scores.sarif": "tachi-risk-scorer",
        "compensating-controls.sarif": "tachi-control-analyzer",
    }
    assert sc.UPLOAD_CATEGORIES == {
        "threats.sarif": "threat-model",
        "risk-scores.sarif": "risk-score",
        "compensating-controls.sarif": "compensating-controls",
    }
    pairs = {(sc.TOOL_NAMES[f], sc.UPLOAD_CATEGORIES[f]) for f in sc.TOOL_NAMES}
    assert len(pairs) == 3
    assert len(set(sc.TOOL_NAMES.values())) == 3 and len(set(sc.UPLOAD_CATEGORIES.values())) == 3
    assert sc.TOOL_NAMES["threats.sarif"][0].isupper()  # `Tachi`, never `tachi`


def test_twelve_prefixes_reach_eight_rule_ids():
    assert dict(sc.RULE_ID_BY_PREFIX) == EXPECTED_RULES
    assert len(sc.RULE_ID_BY_PREFIX) == 12 and len(set(sc.RULE_ID_BY_PREFIX.values())) == 8
    assert set(sc.RULE_ID_BY_CATEGORY.values()) == set(EXPECTED_RULES.values())


def test_the_short_forms_are_never_emitted():
    emitted = set(sc.RULE_ID_BY_PREFIX.values()) | set(sc.RULE_ID_BY_CATEGORY.values())
    assert "tachi/ai/agentic" not in emitted and "tachi/ai/llm" not in emitted
    assert {"tachi/ai/agentic-threats", "tachi/ai/llm-threats"} <= emitted


def test_the_rule_map_agrees_with_the_identifier_allow_list_the_scoring_resolver_and_the_legacy_map():
    prefixes = set(sc.RULE_ID_BY_PREFIX)
    assert prefixes == set(tachi_parts.FINDING_PREFIXES) == set(tachi_scoring.PREFIX_CATEGORY) == set(sc.PREFIX_TO_RULE)
    for prefix in prefixes:
        category = tachi_scoring.category_for_prefix(prefix)
        assert sc.RULE_ID_BY_PREFIX[prefix] == sc.RULE_ID_BY_CATEGORY[category]
        legacy = sc.PREFIX_TO_RULE[prefix]
        # The legacy map keeps the short AI forms for the two generators that still emit them.
        assert sc.RULE_ID_BY_PREFIX[prefix] == (legacy + "-threats" if legacy.startswith("tachi/ai/") else legacy)


def test_every_category_has_a_rule_and_the_resolver_never_leaves_one_out():
    assert set(sc.RULE_ID_BY_CATEGORY) == set(tachi_scoring.CATEGORY_DEFAULT_VECTORS)


@pytest.mark.parametrize("finding_id,rule", [
    ("S-1", "tachi/stride/spoofing"), ("E-9", "tachi/stride/elevation-of-privilege"),
    ("AGP-12", "tachi/ai/agentic-threats"), ("TE-3", "tachi/ai/agentic-threats"),
    ("OI-1", "tachi/ai/llm-threats"), ("MI-07", "tachi/ai/llm-threats"),
])
def test_rule_id_for_follows_the_prefix(finding_id, rule):
    assert sc.rule_id_for(finding_id) == rule


@pytest.mark.parametrize("bad", ["", "X-1", "s-1", "S-1\n", "S-\u0661", "S-", "S1", None, 7])
def test_rule_id_for_refuses_an_id_outside_the_allow_list(bad):
    with pytest.raises(ValueError):
        sc.rule_id_for(bad)


# =============================================================================
# 8. The hash and the partial fingerprints
# =============================================================================

VECTORS = [  # contracts/sarif-result.md and sarif-identity-shared.md
    (SCORER, "S-1", "4395a0c67e904b90:1"),
    (THREATS, "S-1", "6a1fd93f275ff00b:1"),
    (CONTROLS, "AGP-12", "40b3517771dc3a11:1"),
]


def recipe(tool, finding_id):
    """The documented recipe, written out again here so the module isn't tested against itself."""
    return hashlib.sha256(("tachi-plh/1|%s|%s" % (tool, finding_id)).encode("utf-8")).hexdigest()[:16] + ":1"


@pytest.mark.parametrize("tool,finding_id,expected", VECTORS)
def test_the_hash_reproduces_the_published_vectors_byte_for_byte(tool, finding_id, expected):
    assert sc.primary_location_line_hash(tool, finding_id) == expected == recipe(tool, finding_id)


def test_the_recipe_constants():
    assert (sc.HASH_RECIPE_TAG, sc.HASH_HEX_DIGITS, sc.HASH_SUFFIX) == ("tachi-plh/1", 16, ":1")


def test_the_hash_has_the_form_sixteen_lowercase_hex_digits_then_colon_one():
    for tool, prefix in itertools.product((SCORER, CONTROLS, THREATS), tachi_parts.FINDING_PREFIXES):
        value = sc.primary_location_line_hash(tool, prefix + "-7")
        assert re.fullmatch(r"[0-9a-f]{16}:1", value), value


@pytest.mark.parametrize("written,canonical", [("AGP-01", "AGP-1"), ("S-0001", "S-1"), ("T-000100", "T-100"), ("LLM-9", "LLM-9")])
def test_the_hash_is_over_the_canonical_id_so_leading_zeros_never_change_it(written, canonical):
    for tool in (SCORER, CONTROLS, THREATS):
        assert sc.primary_location_line_hash(tool, written) == recipe(tool, canonical)


def test_the_three_files_hash_one_id_to_three_different_values():
    assert len({sc.primary_location_line_hash(t, "T-2") for t in (SCORER, CONTROLS, THREATS)}) == 3


def test_no_two_ids_share_a_hash_in_a_large_sample():
    seen = {}
    for tool, prefix, number in itertools.product((SCORER, CONTROLS, THREATS), tachi_parts.FINDING_PREFIXES, range(1, 301)):
        value = sc.primary_location_line_hash(tool, "%s-%d" % (prefix, number))
        assert value not in seen, (value, seen.get(value))
        seen[value] = (tool, prefix, number)
    assert len(seen) == 3 * 12 * 300


@pytest.mark.parametrize("tool", ["tachi", "TACHI", "Tachi ", " Tachi", "tachi-risk-scorer\n", "risk-scorer", "", None, 7])
def test_a_tool_name_that_is_not_one_of_the_three_is_refused_not_hashed(tool):
    with pytest.raises(ValueError):
        sc.primary_location_line_hash(tool, "S-1")


@pytest.mark.parametrize("bad", [
    "", "X-1", "s-1", "S-1\n", "S-\u0661", "S-\uff11", "S-1234567", "S-", "-1", " S-1", "S-1 ", None, 1])
def test_an_id_outside_the_allow_list_is_refused_before_it_reaches_the_hash(bad):
    with pytest.raises(ValueError):
        sc.primary_location_line_hash(SCORER, bad)


def test_the_fingerprints_are_exactly_the_hash_and_the_id_as_written_in_that_order():
    got = sc.partial_fingerprints(CONTROLS, "AGP-12")
    assert list(got) == ["primaryLocationLineHash", "findingId/v1"] == list(sc.FINGERPRINT_KEYS)
    assert got == {"primaryLocationLineHash": "40b3517771dc3a11:1", "findingId/v1": "AGP-12"}
    zero_padded = sc.partial_fingerprints(CONTROLS, "AGP-012")
    assert zero_padded["primaryLocationLineHash"] == "40b3517771dc3a11:1" and zero_padded["findingId/v1"] == "AGP-012"


# =============================================================================
# 9. Correlation: assignments and ruling C's sentence
# =============================================================================


def assigned(groups, members):
    return sc.correlation_assignments(groups, members)


def test_the_first_remaining_member_is_the_primary_and_the_rest_are_peers_in_listed_order():
    got = assigned([("CG-1", ["T-2", "S-1", "I-3"])], ["S-1", "T-2", "I-3"])
    assert got == {
        "T-2": sc.Correlation("CG-1", "primary", "T-2", ("S-1", "I-3")),
        "S-1": sc.Correlation("CG-1", "peer", "T-2", ()),
        "I-3": sc.Correlation("CG-1", "peer", "T-2", ()),
    }


def test_members_are_filtered_to_the_file_s_member_set_before_the_primary_is_chosen():
    got = assigned([("CG-1", ["R-9", "T-2", "I-3"])], ["T-2", "I-3"])  # R-9 is RESOLVED
    assert got["T-2"].role == "primary" and got["T-2"].peers == ("I-3",) and "R-9" not in got


def test_a_group_left_with_fewer_than_two_members_emits_nothing():
    assert assigned([("CG-1", ["S-1", "R-9"])], ["S-1"]) == {}
    assert assigned([("CG-1", ["S-1"])], ["S-1"]) == {}
    assert assigned([("CG-1", [])], ["S-1"]) == {}


def test_an_id_listed_in_two_groups_stays_in_the_first():
    got = assigned([("CG-1", ["S-1", "T-2"]), ("CG-2", ["T-2", "I-3", "D-4"])], ["S-1", "T-2", "I-3", "D-4"])
    assert got["T-2"].group == "CG-1" and got["S-1"].group == "CG-1"
    assert got["I-3"] == sc.Correlation("CG-2", "primary", "I-3", ("D-4",))


def test_an_id_stays_in_the_first_group_that_lists_it_even_when_that_group_falls_away():
    # CG-1 keeps only T-2 once R-9 is filtered out, so it emits nothing, and CG-2 still loses T-2.
    got = assigned([("CG-1", ["R-9", "T-2"]), ("CG-2", ["T-2", "I-3"])], ["T-2", "I-3"])
    assert got == {}


def test_a_repeated_member_is_counted_once():
    got = assigned([("CG-1", ["S-1", "S-1", "T-2", "T-2"])], ["S-1", "T-2"])
    assert got["S-1"].peers == ("T-2",)


def test_groups_keep_the_order_of_section_4a_and_assignments_use_canonical_ids():
    got = assigned([("CG-2", ["T-02", "S-01"]), ("CG-1", ["I-3", "D-4"])], ["S-1", "T-2", "I-3", "D-4"])
    assert got["T-2"].primary == "T-2" and got["S-1"].primary == "T-2"
    assert got["I-3"].group == "CG-1"
    assert list(got) == ["T-2", "S-1", "I-3", "D-4"]


@pytest.mark.parametrize("group", ["", "CG-", "cg-1", "CG-1\n", "G-1", "CG-1234567", "CG-\u0661", None])
def test_a_malformed_group_id_is_refused(group):
    with pytest.raises(ValueError):
        assigned([(group, ["S-1", "T-2"])], ["S-1", "T-2"])


@pytest.mark.parametrize("member", ["X-1", "S-1\n", "", None])
def test_a_malformed_member_is_refused_not_skipped(member):
    with pytest.raises(ValueError):
        assigned([("CG-1", ["S-1", member])], ["S-1"])


def test_no_groups_means_no_assignments():
    assert assigned([], ["S-1", "T-2"]) == {}


def corr(role, primary="S-1", peers=(), group="CG-3"):
    return sc.Correlation(group, role, primary, tuple(peers))


def test_the_peer_sentence_names_its_group_and_its_primary():
    assert sc.correlation_sentence(corr("peer")) == "Correlated in CG-3; primary S-1."


def test_a_primary_names_its_peers_up_to_the_cap():
    assert sc.correlation_sentence(corr("primary", peers=["T-2", "I-4"])) == "Correlated in CG-3; peers T-2, I-4."
    assert sc.correlation_sentence(corr("primary", peers=["T-2"])) == "Correlated in CG-3; peers T-2."


def test_the_cap_is_ten_and_exactly_ten_peers_add_no_count():
    assert sc.PEER_CAP == 10
    peers = ["T-%d" % n for n in range(2, 12)]
    assert len(peers) == 10
    assert sc.correlation_sentence(corr("primary", peers=peers)) == "Correlated in CG-3; peers %s." % ", ".join(peers)


def test_more_than_ten_peers_name_the_first_ten_then_and_n_more():
    peers = ["T-2", "I-4", "S-5", "R-6", "D-7", "E-8", "AG-9", "LLM-10", "T-11", "I-12", "R-13", "D-14", "E-15"]
    assert sc.correlation_sentence(corr("primary", peers=peers)) == (
        "Correlated in CG-3; peers T-2, I-4, S-5, R-6, D-7, E-8, AG-9, LLM-10, T-11, I-12 and 3 more."
    )
    eleven = ["T-%d" % n for n in range(2, 13)]
    assert sc.correlation_sentence(corr("primary", peers=eleven)).endswith("T-11 and 1 more.")
    many = ["T-%d" % n for n in range(2, 27)]
    assert sc.correlation_sentence(corr("primary", peers=many)).endswith("T-11 and 15 more.")


def test_peers_are_named_in_group_order_not_in_id_order():
    # contracts/sarif-result.md (T023): every peer is named in group order, joined by ", ".
    members = ["S-1", "T-9", "LLM-3", "I-3", "S-2"]
    got = assigned([("CG-3", members)], members)
    assert sc.correlation_sentence(got["S-1"]) == "Correlated in CG-3; peers T-9, LLM-3, I-3, S-2."
    assert sc.correlation_sentence(got["S-2"]) == "Correlated in CG-3; primary S-1."


def test_the_sentence_is_exactly_the_contracts_form_end_to_end_through_a_result():
    members = ["S-1"] + ["T-%d" % n for n in range(2, 15)]  # a primary with 13 peers
    assignments = assigned([("CG-3", members)], members)
    results = [make_result(m, message="Own text.", correlation=assignments.get(m)) for m in members]
    assert results[0]["message"]["text"] == (
        "Own text. Correlated in CG-3; peers T-2, T-3, T-4, T-5, T-6, T-7, T-8, T-9, T-10, T-11 and 3 more."
    )
    assert results[1]["message"]["text"] == "Own text. Correlated in CG-3; primary S-1."
    assert results[0]["message"]["text"].count("  ") == 0  # one space, never two


def test_the_sentence_forms_are_the_documented_constants():
    assert sc.PEER_SENTENCE == "Correlated in {group}; primary {id}."
    assert sc.PRIMARY_SENTENCE == "Correlated in {group}; peers {ids}."
    assert sc.PRIMARY_SENTENCE_OVER_CAP == "Correlated in {group}; peers {ids} and {n} more."
    assert sc.CORRELATION_KEYS == ("correlation-group", "correlation-role", "correlation-primary")
    assert sc.CORRELATION_ROLES == ("primary", "peer")


def test_a_role_that_is_not_primary_or_peer_is_refused():
    with pytest.raises(ValueError):
        sc.correlation_sentence(corr("follower"))


def test_the_sentence_is_joined_to_the_file_s_own_text_by_one_space():
    assert sc.correlated_message("Spoofing of the API.", corr("peer")) == "Spoofing of the API. Correlated in CG-3; primary S-1."
    assert sc.correlated_message("Spoofing of the API.", None) == "Spoofing of the API."


@pytest.mark.parametrize("text", ["", None, 7])
def test_a_message_must_be_a_non_empty_string(text):
    with pytest.raises(ValueError):
        sc.correlated_message(text, None)


# =============================================================================
# 10. The result: shape, key order, evidence
# =============================================================================


def make_result(finding_id="T-2", tool=SCORER, **kwargs):
    base = dict(
        tool=tool, finding_id=finding_id, message="Tampering with the store.", level="warning", uri=URI,
        component="Store", zone="Data Zone", kind="data-store", properties={"score-source": "fresh"},
    )
    base.update(kwargs)
    return sc.build_result(**base)


def test_a_result_has_the_documented_shape_and_key_order():
    got = make_result()
    assert list(got) == ["ruleId", "message", "level", "locations", "partialFingerprints", "properties"]
    assert got == {
        "ruleId": "tachi/stride/tampering",
        "message": {"text": "Tampering with the store."},
        "level": "warning",
        "locations": [{
            "physicalLocation": {"artifactLocation": {"uri": URI}, "region": {"startLine": 1}},
            "logicalLocations": [{"name": "Store", "fullyQualifiedName": "Data Zone/Store", "kind": "data-store"}],
        }],
        "partialFingerprints": {"primaryLocationLineHash": recipe(SCORER, "T-2"), "findingId/v1": "T-2"},
        "properties": {"score-source": "fresh"},
    }


def test_a_controls_result_adds_related_locations_between_locations_and_the_fingerprints():
    evidence = sc.ResolvedPath("src/auth/login.py", "src/auth/login.py")
    entry = sc.evidence_location(0, "authentication", evidence, 42)
    got = make_result("S-1", tool=CONTROLS, related_locations=[entry])
    assert list(got) == ["ruleId", "message", "level", "locations", "relatedLocations", "partialFingerprints", "properties"]
    assert got["relatedLocations"] == [{
        "id": 0,
        "message": {"text": "Control evidence: authentication detected in src/auth/login.py"},
        "physicalLocation": {"artifactLocation": {"uri": "src/auth/login.py"}, "region": {"startLine": 42}},
    }]


def test_related_locations_are_omitted_when_there_are_none():
    assert "relatedLocations" not in make_result(related_locations=[])
    assert "relatedLocations" not in make_result(related_locations=())


@pytest.mark.parametrize("category", ["", None, 7])
def test_an_evidence_category_is_a_non_empty_string(category):
    with pytest.raises(ValueError):
        sc.evidence_location(0, category, sc.ResolvedPath("a.py", "a.py"), 1)


def test_an_evidence_message_names_the_canonical_path_and_its_location_the_encoded_uri():
    evidence = sc.ResolvedPath("src/My Dir/\u00e9.py", "src/My%20Dir/%C3%A9.py")
    entry = sc.evidence_location(3, "rate-limiting", evidence, 7)
    assert entry["message"]["text"] == "Control evidence: rate-limiting detected in src/My Dir/\u00e9.py"
    assert entry["physicalLocation"]["artifactLocation"]["uri"] == "src/My%20Dir/%C3%A9.py"
    assert entry["id"] == 3 and sc.EVIDENCE_MESSAGE == "Control evidence: {category} detected in {file}"


@pytest.mark.parametrize("line", [0, -1, 1.5, True, None, "7"])
def test_an_evidence_line_is_a_positive_integer(line):
    with pytest.raises(ValueError):
        sc.evidence_location(0, "encryption", sc.ResolvedPath("a.py", "a.py"), line)


def test_an_evidence_entry_with_braces_in_its_values_is_not_a_format_string():
    entry = sc.evidence_location(0, "{category}", sc.ResolvedPath("a{file}.py", "a%7Bfile%7D.py"), 1)
    assert entry["message"]["text"] == "Control evidence: {category} detected in a{file}.py"


def test_properties_keep_the_callers_order_and_the_correlation_keys_follow():
    got = make_result(properties={"z-key": 1, "a-key": 2}, correlation=corr("peer"))
    assert list(got["properties"]) == ["z-key", "a-key", "correlation-group", "correlation-role", "correlation-primary"]
    assert got["properties"]["correlation-primary"] == "S-1"
    assert got["message"]["text"].endswith(" Correlated in CG-3; primary S-1.")


def test_an_uncorrelated_result_carries_none_of_the_three_keys_and_no_sentence():
    got = make_result(message="Plain.")
    assert not set(sc.CORRELATION_KEYS) & set(got["properties"]) and got["message"]["text"] == "Plain."


def test_a_result_never_carries_the_forbidden_keys():
    got = make_result(correlation=corr("peer"))
    assert not set(sc.FORBIDDEN_RESULT_KEYS) & set(got)
    assert set(sc.FORBIDDEN_RESULT_KEYS) == {"guid", "correlationGuid", "fingerprints", "baselineState"}


def test_the_region_is_the_constant_and_each_result_gets_its_own_copy():
    first, second = make_result(), make_result("T-3")
    assert first["locations"][0]["physicalLocation"]["region"] == {"startLine": 1} == sc.REGION
    first["locations"][0]["physicalLocation"]["region"]["startLine"] = 99
    assert sc.REGION == {"startLine": 1} and second["locations"][0]["physicalLocation"]["region"] == {"startLine": 1}


def test_the_emitter_owns_the_correlation_keys():
    with pytest.raises(ValueError):
        make_result(properties={"correlation-group": "CG-9"})


@pytest.mark.parametrize("kwargs", [
    {"level": "critical"}, {"level": ""}, {"uri": ""}, {"uri": None}, {"component": ""}, {"zone": ""}, {"kind": ""},
    {"message": ""}, {"finding_id": "X-1"}, {"finding_id": "T-2\n"}, {"tool": "tachi"},
])
def test_build_result_refuses_unusable_inputs(kwargs):
    with pytest.raises(ValueError):
        make_result(**kwargs)


def test_every_level_the_files_use_is_allowed():
    assert set(sc.LEVELS) == {"error", "warning", "note", "none"}
    for band_level in set(sc.SEVERITY_TO_LEVEL.values()):
        assert band_level in sc.LEVELS


def test_the_flag_property_names():
    assert sc.FLAG_PROPERTIES == {"risk-scores.sarif": "score-flags", "compensating-controls.sarif": "integrity-flags"}


# =============================================================================
# 11. The self-check, one violation at a time
# =============================================================================

MEMBERS = ["S-1", "T-2", "I-3", "D-4", "AG-5"]
GROUPS = [("CG-1", ["S-1", "T-2", "R-9"]), ("CG-2", ["I-3", "D-4"])]


def build_run(tool=SCORER, members=MEMBERS, groups=GROUPS, **kwargs):
    assignments = sc.correlation_assignments(groups, members)
    results = [make_result(m, tool=tool, correlation=assignments.get(m)) for m in members]
    return results, assignments


def check(results, assignments, tool=SCORER, members=MEMBERS, resolved=("R-9",), **kwargs):
    sc.self_check(results, tool=tool, member_ids=members, assignments=assignments, resolved_ids=resolved, uri=URI, **kwargs)


def problems_of(results, assignments, **kwargs):
    with pytest.raises(sc.SelfCheckError) as excinfo:
        check(results, assignments, **kwargs)
    assert isinstance(excinfo.value, ValueError)
    return excinfo.value.problems


def test_a_correct_run_passes_for_each_of_the_three_tools():
    for tool in (SCORER, CONTROLS, THREATS):
        results, assignments = build_run(tool=tool)
        check(results, assignments, tool=tool)


def test_a_run_with_no_findings_and_no_groups_passes():
    check([], {}, members=[], resolved=[])


def test_a_duplicate_hash_fails_the_render_and_names_both_ids():
    results, assignments = build_run(groups=[])
    twin = copy.deepcopy(results[1])
    twin["partialFingerprints"]["findingId/v1"] = "T-02"  # two spellings of one canonical ID: one hash
    results.append(twin)
    problems = problems_of(results, {}, members=MEMBERS)
    assert any("T-2 and T-02 share primaryLocationLineHash" in p for p in problems), problems
    assert any("two results are for T-2" in p for p in problems)


def test_two_different_ids_forced_to_one_hash_are_reported():
    results, _ = build_run(groups=[])
    results[1]["partialFingerprints"]["primaryLocationLineHash"] = results[0]["partialFingerprints"]["primaryLocationLineHash"]
    problems = problems_of(results, {})
    assert any("S-1 and T-2 share primaryLocationLineHash" in p for p in problems)
    assert any("T-2: primaryLocationLineHash" in p and "not tachi's own" in p for p in problems)


@pytest.mark.parametrize("forged", ["49e22734237e23be", "49e22734237e23be:1", "4395A0C67E904B90:1", "4395a0c67e904b90:2", ""])
def test_a_hash_that_is_not_tachi_s_own_is_refused(forged):
    results, assignments = build_run()
    results[0]["partialFingerprints"]["primaryLocationLineHash"] = forged
    assert problems_of(results, assignments)


def test_the_hash_of_another_tool_is_not_tachi_s_own_for_this_file():
    results, assignments = build_run(tool=THREATS)
    assert problems_of(results, assignments, tool=SCORER)  # hashed for Tachi, checked as the scorer


def test_a_wrong_rule_id_is_refused():
    results, assignments = build_run()
    results[0]["ruleId"] = "tachi/ai/agentic"
    assert any("ruleId" in p for p in problems_of(results, assignments))


def test_results_must_share_the_one_uri():
    results, assignments = build_run()
    results[2]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] = "docs/other.md"
    assert any("artifactLocation.uri differs" in p for p in problems_of(results, assignments))


def test_the_uri_must_be_the_runs_when_given():
    results, assignments = build_run()
    with pytest.raises(sc.SelfCheckError) as excinfo:
        sc.self_check(results, tool=SCORER, member_ids=MEMBERS, assignments=assignments, resolved_ids=["R-9"], uri="other.md")
    assert any("not the run's" in p for p in excinfo.value.problems)


def test_a_member_with_no_result_and_a_result_for_a_non_member_are_both_named():
    results, assignments = build_run()
    gone = results.pop(3)  # D-4
    results.append(make_result("E-8"))
    problems = problems_of(results, assignments)
    assert any("member findings with no result: D-4" in p for p in problems)
    assert any("outside the member set: E-8" in p for p in problems)
    assert gone["partialFingerprints"]["findingId/v1"] == "D-4"


def test_the_result_count_must_equal_the_member_set():
    results, assignments = build_run()
    assert problems_of(results[:-1], assignments)  # one result short


def evidence_entry(text):
    return {
        "id": 0, "message": {"text": text},
        "physicalLocation": {"artifactLocation": {"uri": "a.py"}, "region": {"startLine": 1}},
    }


def add_related(result, entries):
    """Insert relatedLocations where the shared key order puts it: after locations, before the fingerprints."""
    tail = {key: result.pop(key) for key in ("partialFingerprints", "properties")}
    result["relatedLocations"] = entries
    result.update(tail)


@pytest.mark.parametrize("where", ["message", "property", "evidence"])
def test_a_resolved_id_may_appear_nowhere(where):
    results, assignments = build_run(tool=CONTROLS)
    victim = results[0]
    if where == "message":
        victim["message"]["text"] += " See also R-9."
    elif where == "property":
        victim["properties"]["notes"] = ["fine", {"deep": "relates to R-09"}]
    else:
        add_related(victim, [evidence_entry("Control evidence: logging-audit detected in R-9")])
    problems = problems_of(results, assignments, tool=CONTROLS)
    assert any("RESOLVED finding" in p and "R-9" in p.replace("R-09", "R-9") for p in problems), problems


def test_a_resolved_id_that_a_member_also_uses_is_not_resolved_for_this_check():
    results, assignments = build_run()
    check(results, assignments, resolved=["S-1", "R-9"])  # S-1 is a member (a reused ID), so it may appear


def test_a_resolved_id_inside_another_token_or_a_uri_is_not_a_hit():
    results, assignments = build_run()
    results[4]["message"]["text"] += " Mentions R-90, XR-9 and R-9x."  # AG-5 is uncorrelated
    check(results, assignments)


def test_a_related_location_that_names_a_finding_is_refused():
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_entry("T-2: peer of this finding")])
    assert any("names the finding T-2" in p for p in problems_of(results, assignments, tool=CONTROLS))


def test_related_locations_belong_to_the_controls_file_only():
    results, assignments = build_run(tool=SCORER)
    add_related(results[0], [evidence_entry("Control evidence: encryption detected in a.py")])
    assert any("controls file only" in p for p in problems_of(results, assignments))


def test_a_related_location_without_a_physical_location_is_refused():
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [{"id": 0, "message": {"text": "Control evidence: x detected in y"}}])
    assert any("not code evidence" in p for p in problems_of(results, assignments, tool=CONTROLS))


def test_a_correlated_result_whose_message_lacks_the_sentence_is_refused():
    results, assignments = build_run()
    results[1]["message"]["text"] = "Finding T-2."
    assert any("does not end with ruling C's sentence" in p for p in problems_of(results, assignments))


def test_a_correlated_result_whose_sentence_names_the_wrong_primary_is_refused():
    results, assignments = build_run()
    results[1]["message"]["text"] = results[1]["message"]["text"].replace("primary S-1", "primary I-3")
    assert any("T-2: the message does not end" in p for p in problems_of(results, assignments))


def test_a_sentence_repeated_in_one_message_is_refused():
    results, assignments = build_run()
    results[1]["message"]["text"] += " Correlated in CG-1; primary S-1."
    assert any("more than once" in p or "does not end" in p for p in problems_of(results, assignments))


@pytest.mark.parametrize("key,value", [
    ("correlation-group", "CG-7"), ("correlation-role", "primary"), ("correlation-primary", "I-3")])
def test_a_correlation_property_that_disagrees_with_the_group_is_refused(key, value):
    results, assignments = build_run()
    results[1]["properties"][key] = value
    assert any(key in p for p in problems_of(results, assignments))


def test_an_uncorrelated_result_that_carries_the_keys_or_the_sentence_is_refused():
    results, assignments = build_run()
    results[4]["properties"]["correlation-group"] = "CG-9"
    results[4]["message"]["text"] += " Correlated in CG-9; primary S-1."
    problems = problems_of(results, assignments)
    assert any("AG-5: not correlated, but carries" in p for p in problems)
    assert any("AG-5: not correlated, but its message holds the sentence" in p for p in problems)


def test_a_correlated_member_whose_result_is_missing_is_refused():
    results, assignments = build_run()
    results.pop(1)  # T-2 is a peer of S-1
    problems = problems_of(results, assignments)
    assert any("T-2" in p for p in problems)


def test_a_member_named_in_a_sentence_must_be_a_result():
    members = ["S-1", "T-2"]
    handmade = {
        "S-1": sc.Correlation("CG-1", "primary", "S-1", ("T-2", "D-4")),  # D-4 has no result
        "T-2": sc.Correlation("CG-1", "peer", "S-1", ()),
    }
    results = [make_result(m, correlation=handmade[m]) for m in members]
    with pytest.raises(sc.SelfCheckError) as excinfo:
        sc.self_check(results, tool=SCORER, member_ids=members, assignments=handmade, uri=URI)
    assert any("S-1: D-4, in its group CG-1, is not a result" in p for p in excinfo.value.problems)


def test_a_group_must_have_exactly_one_primary_result():
    results, assignments = build_run()
    twisted = dict(assignments)
    twisted["T-2"] = sc.Correlation("CG-1", "primary", "S-1", ("S-1",))
    problems = problems_of(results, twisted)
    assert any("group CG-1 has 2 primaries" in p for p in problems)


@pytest.mark.parametrize("mutate,expect", [
    (lambda r: r.pop("level"), "keys"),
    (lambda r: r.update(guid="x"), "it carries guid"),
    (lambda r: r.update(correlationGuid="x"), "it carries correlationGuid"),
    (lambda r: r.update(fingerprints={}), "it carries fingerprints"),
    (lambda r: r.update(baselineState="new"), "it carries baselineState"),
    (lambda r: r.update(level="critical"), "level"),
    (lambda r: r["message"].update(extra=1), "message"),
    (lambda r: r.update(message={"text": ""}), "message"),
    (lambda r: r["locations"].append({}), "locations"),
    (lambda r: r["locations"][0]["physicalLocation"].update(region={"startLine": 2}), "location"),
    (lambda r: r["locations"][0]["physicalLocation"]["artifactLocation"].update(extra="x"), "location"),
    (lambda r: r["locations"][0]["logicalLocations"][0].pop("kind"), "logicalLocations"),
    (lambda r: r["partialFingerprints"].update(baselineRunId="x"), "partialFingerprints"),
    (lambda r: r.update(partialFingerprints=dict(reversed(list(r["partialFingerprints"].items())))), "partialFingerprints"),
    (lambda r: r.update(properties=[]), "properties"),
    (lambda r: r.update(relatedLocations=[]), "relatedLocations"),
])
def test_a_result_that_leaves_the_shared_shape_is_refused(mutate, expect):
    results, assignments = build_run()
    mutate(results[0])
    problems = problems_of(results, assignments)
    assert any(expect in p for p in problems), (expect, problems)


def test_a_result_that_is_not_an_object_is_refused():
    results, assignments = build_run()
    results[0] = "not a result"
    assert any("not an object" in p for p in problems_of(results, assignments))


def test_a_findingid_that_is_not_an_id_is_refused():
    results, assignments = build_run()
    results[0]["partialFingerprints"]["findingId/v1"] = "S-1\n"
    assert any("is not a finding ID" in p for p in problems_of(results, assignments))


def test_member_and_resolved_ids_must_be_ids_too():
    results, assignments = build_run()
    problems = problems_of(results, assignments, members=MEMBERS + ["X-1"], resolved=["R-9", "bad"])
    assert any("member 'X-1' is not a finding ID" in p for p in problems)
    assert any("RESOLVED 'bad' is not a finding ID" in p for p in problems)


def test_the_error_lists_every_problem_but_shows_twenty_and_a_count():
    results, assignments = build_run()
    for result in results:
        result["partialFingerprints"]["primaryLocationLineHash"] = "0" * 16 + ":1"
    with pytest.raises(sc.SelfCheckError) as excinfo:
        check(results, assignments)
    err = excinfo.value
    assert len(err.problems) >= 5 and str(err).startswith("SARIF self-check failed: ")
    many = sc.SelfCheckError(["p%d" % n for n in range(25)])
    assert str(many).endswith("p19; and 5 more") and len(many.problems) == 25


def test_a_tool_that_is_not_one_of_the_three_is_a_usage_error_not_a_problem_list():
    with pytest.raises(ValueError) as excinfo:
        sc.self_check([], tool="tachi", member_ids=[])
    assert not isinstance(excinfo.value, sc.SelfCheckError)


def test_a_primary_with_more_than_ten_peers_passes_with_the_counted_sentence():
    members = ["S-1"] + ["T-%d" % n for n in range(2, 15)]
    groups = [("CG-1", members)]
    results, assignments = build_run(members=members, groups=groups)
    check(results, assignments, members=members, resolved=[])
    assert results[0]["message"]["text"].endswith("T-11 and 3 more.")


# =============================================================================
# 12. The run, the document and the bytes
# =============================================================================

DIGEST = "sha256:" + "ab" * 32


def stamp():
    return sc.provenance_stamp("render-risk-scores.py", "4.48.4", DIGEST)


def document(results=None, schema_first=False, sarif_file="risk-scores.sarif"):
    results = build_run()[0] if results is None else results
    driver = sc.build_driver(
        sarif_file, semantic_version="1.1", rules=[{"id": "tachi/stride/spoofing"}], supported=sc.supported_taxonomies())
    return sc.build_document(driver, sc.TAXONOMIES, results, stamp(), schema_first=schema_first)


def test_the_stamp_has_the_three_keys_in_order():
    assert stamp() == {"renderer": "render-risk-scores.py", "version": "4.48.4", "input_digest": DIGEST}
    assert list(stamp()) == list(sc.STAMP_KEYS) == ["renderer", "version", "input_digest"]


@pytest.mark.parametrize("field,value", [
    ("renderer", ""), ("renderer", "-x.py"), ("renderer", "a b"), ("renderer", "a" * 65), ("renderer", None),
    ("version", "4.48"), ("version", "v4.48.4"), ("version", "4.48.4\n"), ("version", "4.48.4-rc1"), ("version", None),
    ("input_digest", "sha256:" + "ab" * 31), ("input_digest", "sha256:" + "AB" * 32), ("input_digest", "ab" * 32),
    ("input_digest", "md5:" + "ab" * 16), ("input_digest", DIGEST + "\n"), ("input_digest", None),
])
def test_a_stamp_field_that_is_not_in_its_documented_form_is_refused(field, value):
    args = {"renderer": "render-risk-scores.py", "version": "4.48.4", "input_digest": DIGEST}
    args[field] = value
    with pytest.raises(ValueError):
        sc.provenance_stamp(**args)


def test_the_document_has_the_envelope_the_run_the_stamp_and_no_automation_details():
    doc = document()
    assert list(doc) == ["version", "$schema", "runs"] and doc["version"] == "2.1.0" and doc["$schema"] == sc.SARIF_SCHEMA_URI
    (run,) = doc["runs"]
    assert list(run) == ["tool", "taxonomies", "results", "properties"]
    assert run["properties"] == {"tachi_provenance": stamp()}
    assert "automationDetails" not in run and "automationDetails" not in json.dumps(doc)
    assert run["taxonomies"] == sc.TAXONOMIES and len(run["results"]) == 5


def test_the_threats_file_keeps_its_legacy_schema_first_order_when_asked():
    assert list(document(schema_first=True))[:2] == ["$schema", "version"]


def test_the_driver_has_the_verbatim_tool_name_and_the_real_information_uri():
    for sarif_file, name in sc.TOOL_NAMES.items():
        driver = sc.build_driver(sarif_file, semantic_version="1.0", rules=[])
        assert driver["name"] == name and driver["informationUri"] == "https://github.com/davidmatousek/tachi"
        assert list(driver) == ["name", "semanticVersion", "informationUri", "rules"]
    full = sc.build_driver("risk-scores.sarif", semantic_version="1.0", rules=[], supported=sc.supported_taxonomies())
    assert list(full) == ["name", "semanticVersion", "informationUri", "supportedTaxonomies", "rules"]
    assert "owner/tachi" not in sc.INFORMATION_URI and sc.INFORMATION_URI.startswith("https://github.com/")


def test_a_driver_for_a_file_that_is_not_one_of_the_three_is_refused():
    with pytest.raises(ValueError):
        sc.build_driver("other.sarif", semantic_version="1.0", rules=[])


def test_a_document_with_a_placeholder_information_uri_or_a_wrong_tool_is_refused():
    driver = sc.build_driver("risk-scores.sarif", semantic_version="1.0", rules=[])
    placeholder = dict(driver, informationUri="https://github.com/owner/tachi")
    for bad in (placeholder, dict(driver, name="tachi-risk-scorer "), dict(driver, name="tachi")):
        with pytest.raises(ValueError):
            sc.build_document(bad, [], [], stamp())
    with pytest.raises(ValueError):
        sc.build_document(driver, [], [], {"version": "4.48.4", "renderer": "r", "input_digest": DIGEST})


def test_the_json_is_two_space_ascii_with_a_final_newline_and_round_trips():
    doc = document()
    text = sc.to_json(doc)
    assert text.endswith("}\n") and not text.endswith("\n\n")
    assert text.splitlines()[1].startswith('  "') and not text.splitlines()[1].startswith('   ')
    assert text.isascii() and json.loads(text) == doc


def test_the_json_bytes_depend_on_the_document_alone():
    assert sc.to_json(document()) == sc.to_json(document()) == sc.to_json(copy.deepcopy(document()))


def test_a_bidi_or_line_separator_character_in_a_name_is_escaped_and_cannot_forge_structure():
    hostile = "Caf\u00e9\u202e\u2028\u200b**x**"
    results = [make_result("S-1", component=hostile, zone=hostile)]
    text = sc.to_json(document(results))
    assert text.isascii() and "\u2028" not in text and "\u202e" not in text
    assert json.loads(text)["runs"][0]["results"][0]["locations"][0]["logicalLocations"][0]["name"] == hostile


# =============================================================================
# 13. Identity across runs and across the three files (FR-E.2's model)
# =============================================================================


def keys_of(results):
    """GitHub's matching key for each result: rule, hash and URI (the tool and category are per file)."""
    return {
        r["partialFingerprints"]["findingId/v1"]: (
            r["ruleId"], r["partialFingerprints"]["primaryLocationLineHash"],
            r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
        )
        for r in results
    }


def test_a_regroup_keeps_every_carried_key_and_changes_only_the_text():
    run1, a1 = build_run(groups=[("CG-1", ["S-1", "T-2"]), ("CG-2", ["I-3", "D-4"])])
    run2, a2 = build_run(groups=[("CG-1", ["T-2", "I-3", "S-1"]), ("CG-4", ["D-4", "AG-5"])])
    assert a1 != a2
    assert keys_of(run1) == keys_of(run2)
    assert [r["message"]["text"] for r in run1] != [r["message"]["text"] for r in run2]
    for results, assignments in ((run1, a1), (run2, a2)):
        check(results, assignments, resolved=[])


def test_a_new_primary_and_a_dissolved_group_leave_every_key_alone():
    base, _ = build_run(groups=[("CG-1", ["S-1", "T-2", "I-3"])])
    new_primary, _ = build_run(groups=[("CG-1", ["I-3", "S-1", "T-2"])])
    none, _ = build_run(groups=[])
    assert keys_of(base) == keys_of(new_primary) == keys_of(none)


def test_an_unchanged_rerun_keeps_its_keys_and_its_bytes():
    first, _ = build_run()
    second, _ = build_run()
    assert keys_of(first) == keys_of(second)
    assert sc.to_json(document(first)) == sc.to_json(document(second))


def test_a_rescore_or_a_new_component_does_not_move_the_key():
    plain = make_result("T-2")
    moved = make_result("T-2", message="Different prose.", level="error", component="Other", zone="Elsewhere", kind="process",
                        properties={"score-source": "inherited", "composite_score": "9.9"})
    assert keys_of([plain]) == keys_of([moved])


def test_no_two_present_results_share_a_key_in_a_large_file():
    ids = ["%s-%d" % (prefix, n) for prefix in tachi_parts.FINDING_PREFIXES for n in range(1, 41)]
    assert len(ids) == 480
    results = [make_result(i) for i in ids]
    sc.self_check(results, tool=SCORER, member_ids=ids, resolved_ids=[], uri=URI)
    assert len({r["partialFingerprints"]["primaryLocationLineHash"] for r in results}) == 480


def test_one_finding_gets_three_different_keys_in_the_three_files():
    docs = {f: document([make_result("T-2", tool=t)], sarif_file=f) for f, t in sc.TOOL_NAMES.items()}
    hashes = {d["runs"][0]["results"][0]["partialFingerprints"]["primaryLocationLineHash"] for d in docs.values()}
    assert len(hashes) == 3
    assert all("automationDetails" not in run for d in docs.values() for run in d["runs"])
    assert {d["runs"][0]["tool"]["driver"]["name"] for d in docs.values()} == set(sc.TOOL_NAMES.values())


def test_a_case_variant_architecture_path_gives_every_result_the_same_uri():
    fs = make_repo(case_insensitive=True)
    uris = set()
    for variant in ("docs/security/architecture.md", "DOCS/Security/ARCHITECTURE.md", "/REPO/docs/SECURITY/architecture.MD"):
        resolution = sc.resolve_architecture(variant, root="/repo", fs=fs)
        results = [make_result(i, uri=resolution.uri) for i in ("S-1", "T-2")]
        uris |= {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in results}
    assert uris == {"docs/security/architecture.md"}


# =============================================================================
# 14. The taxa, against schemas/taxonomy
# =============================================================================

OWASP = REPO_ROOT / "schemas" / "taxonomy" / "owasp.yaml"
CWE = REPO_ROOT / "schemas" / "taxonomy" / "cwe.yaml"


def catalog(path):
    return [r for r in yaml.safe_load(path.read_text(encoding="utf-8")) if isinstance(r, dict)]


def llm_records():
    return sorted((r for r in catalog(OWASP) if r["id"].startswith("LLM")), key=lambda r: r["id"])


def entry(name, taxonomies=None):
    (found,) = [t for t in (sc.TAXONOMIES if taxonomies is None else taxonomies) if t["name"] == name]
    return found


def test_the_owasp_llm_taxa_are_the_catalog_s_ten_records_in_order():
    records = llm_records()
    assert [r["id"] for r in records] == ["LLM%02d" % n for n in range(1, 11)]
    assert entry("OWASP-LLM")["taxa"] == [{"id": r["id"], "name": r["name"]} for r in records]


def test_the_owasp_llm_url_and_edition_are_the_catalog_s_single_values():
    records = llm_records()
    assert {r["url"] for r in records} == {sc.LLM_INFORMATION_URI}
    assert {r["full_id"].split("-")[2] for r in records} == {sc.LLM_EDITION}
    llm = entry("OWASP-LLM")
    assert llm["version"] == sc.LLM_EDITION == "2026" and llm["informationUri"] == sc.LLM_INFORMATION_URI


def test_the_asi_and_cwe_taxa_are_ids_the_catalogs_hold():
    owasp_ids = {r["id"] for r in catalog(OWASP)}
    cwe_ids = {r["id"] for r in catalog(CWE)}
    assert {t["id"] for t in entry("OWASP-ASI")["taxa"]} <= owasp_ids
    assert {t["id"] for t in entry("CWE")["taxa"]} <= cwe_ids


def test_the_taxonomies_have_a_fixed_order_unique_guids_and_closed_entry_shapes():
    assert [t["name"] for t in sc.TAXONOMIES] == ["OWASP-LLM", "OWASP-ASI", "CWE"]
    assert len({t["guid"] for t in sc.TAXONOMIES}) == 3
    for taxonomy in sc.TAXONOMIES:
        assert list(taxonomy) == ["name", "version", "guid", "informationUri", "taxa"]
        assert all(list(taxon) == ["id", "name"] for taxon in taxonomy["taxa"])
        assert len({taxon["id"] for taxon in taxonomy["taxa"]}) == len(taxonomy["taxa"])


def test_supported_taxonomies_are_derived_from_the_taxonomies():
    supported = sc.supported_taxonomies()
    assert [s["name"] for s in supported] == [t["name"] for t in sc.TAXONOMIES]
    assert [s["index"] for s in supported] == [0, 1, 2]
    for entry_, taxonomy in zip(supported, sc.TAXONOMIES):
        assert list(entry_) == ["name", "index", "guid", "version", "informationUri"]
        assert all(entry_[k] == taxonomy[k] for k in ("name", "guid", "version", "informationUri"))
    supported[0]["name"] = "changed"
    assert sc.TAXONOMIES[0]["name"] == "OWASP-LLM"  # a fresh list each call


def test_the_document_builder_does_not_change_the_embedded_taxa():
    before = copy.deepcopy(sc.TAXONOMIES)
    document()
    assert sc.TAXONOMIES == before


def test_the_taxa_need_no_yaml_the_module_never_imports_it():
    tree = ast.parse((SCRIPTS_DIR / "sarif_common.py").read_text(encoding="utf-8"))
    assert "yaml" not in imported_modules(tree)


# =============================================================================
# 15. Module hygiene and the legacy helpers
# =============================================================================

SOURCE = SCRIPTS_DIR / "sarif_common.py"


def imported_modules(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_the_module_imports_the_standard_library_and_the_three_local_helpers_only():
    imported = imported_modules(ast.parse(SOURCE.read_text(encoding="utf-8")))
    local = {"tachi_parsers", "tachi_parts", "tachi_scoring"}
    assert local <= imported
    standard = imported - local - {"__future__"}
    assert standard <= {"hashlib", "json", "os", "posixpath", "re", "stat", "sys", "typing", "pathlib"}, standard


def test_the_bytecode_guard_comes_before_every_local_import():
    body = ast.parse(SOURCE.read_text(encoding="utf-8")).body
    guard = next(
        i for i, node in enumerate(body)
        if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "sys.dont_write_bytecode"
    )
    first_local = min(
        i for i, node in enumerate(body)
        if (isinstance(node, ast.Import) and node.names[0].name.startswith("tachi_"))
        or (isinstance(node, ast.ImportFrom) and (node.module or "").startswith("tachi_"))
    )
    assert guard < first_local and body[guard].value.value is True


def test_the_module_has_no_assert_no_clock_no_random_and_no_eval():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    assert [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)] == []
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not attributes & {"today", "now", "utcnow", "time", "monotonic", "random", "randint", "shuffle"}
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not names & {"eval", "exec", "compile", "__import__"}
    assert not {"random", "time", "datetime", "yaml"} & imported_modules(tree)


def test_the_module_keeps_python_3_9_grammar_and_future_annotations():
    source = SOURCE.read_text(encoding="utf-8")
    ast.parse(source, feature_version=(3, 9))
    assert "from __future__ import annotations" in source


def test_the_legacy_helpers_keep_their_names_and_values():
    assert sc.PREFIX_TO_RULE == {
        "S": "tachi/stride/spoofing", "T": "tachi/stride/tampering", "R": "tachi/stride/repudiation",
        "I": "tachi/stride/information-disclosure", "D": "tachi/stride/denial-of-service",
        "E": "tachi/stride/elevation-of-privilege",
        "AG": "tachi/ai/agentic", "AGP": "tachi/ai/agentic", "LLM": "tachi/ai/llm", "OI": "tachi/ai/llm",
        "MI": "tachi/ai/llm", "TE": "tachi/ai/agentic",
    }
    assert sc.SEVERITY_TO_LEVEL == {"Critical": "error", "High": "error", "Medium": "warning", "Low": "note", "Note": "note"}
    assert sc.prefix_for("AGP-12") == "AGP" and sc.level_for_band("Low") == "note" and sc.level_for_band("x") == "warning"
    assert sc.REPO_ROOT == REPO_ROOT
    envelope = sc.build_sarif_envelope({"name": "d"}, [], [])
    assert list(envelope) == ["version", "$schema", "runs"] and list(envelope["runs"][0]) == ["tool", "taxonomies", "results"]
    assert list(sc.build_sarif_envelope({"name": "d"}, [], [], schema_first=True))[:2] == ["$schema", "version"]
    assert callable(sc.parse_component_metadata) and callable(sc.parse_affected_assets)


def test_importing_the_module_leaves_no_bytecode_for_the_local_modules_it_loads_after_its_guard(tmp_path):
    for name in ("sarif_common.py", "tachi_parts.py", "tachi_scoring.py", "tachi_parsers.py"):
        (tmp_path / name).write_bytes((SCRIPTS_DIR / name).read_bytes())
    env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
    done = subprocess.run(
        [sys.executable, "-c", "import sarif_common"], cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=60,
    )
    assert done.returncode == 0, done.stderr
    written = {p.name.split(".")[0] for p in tmp_path.rglob("*.pyc")}
    # The module is compiled before its own guard runs, so its own file may be cached;
    # the helpers it loads afterwards must not be (ADR-049 D8).
    assert not written & {"tachi_parts", "tachi_scoring", "tachi_parsers"}, written


# =============================================================================
# 16. risk-scores.sarif through the renderer: FR-E.2's two-run model (T049; red until T050)
# =============================================================================
#
# Section 13 builds runs with the emitter and checks the model on them. The cases below drive the entry,
# ``render-risk-scores.py``, in-process through ``main(argv)`` (ADR-050 D16, H15), on the project harness of
# ``test_render_risk_scores.py`` (T027), so what they read is the file an adopter uploads. They need the renderer
# (T028, T045, T046 and T050) and fail with its absence until it exists. The peer and baseline-aware cases also need
# T044's routing, T048's parser and T042's reader. The matching key is the tool, the upload category, the rule, the
# line hash and the URI (ADR-050 D7); nothing else is identity.

SCORER_CATEGORY = "risk-score"  # the upload category of risk-scores.sarif: tachi recommends it and never writes it
FIRST_RUN_GROUPS = [("CG-1", ["S-2", "S-10", "T-1"]), ("CG-2", ["E-3", "E-5"])]
SECOND_RUN_GROUPS = [("CG-1", ["T-1", "S-2"]), ("CG-3", ["S-10", "E-3", "AG-1"])]  # a new primary, a dissolved group, a new one
PLANTED_HASHES = ["%016x:1" % n for n in range(1, 41)]  # what an upstream file or an older run could carry: never copied


@pytest.fixture(scope="module")
def rrs():
    """The renderer goldens' project harness, imported when a case first needs it, so Sections 1 to 15 never depend on it."""
    from . import test_render_risk_scores
    return test_render_risk_scores


@pytest.fixture(scope="module")
def entries(rrs):
    """``(tachi-stage.py, render-risk-scores.py)`` as loaded modules."""
    if not rrs.RENDERER.is_file():
        pytest.fail("scripts/render-risk-scores.py does not exist yet: T028 and T050 write it to these cases (TDD)", pytrace=False)
    return (_load_hyphenated_script("tachi_stage_for_identity_cases", "tachi-stage.py"),
            _load_hyphenated_script("render_risk_scores_for_identity_cases", "render-risk-scores.py"))


def scorer_project(rrs, entries, root, **kwargs):
    return rrs.Project(entries[0], entries[1], root, **kwargs)


def alert_keys(document):
    """GitHub's matching key of each result in a ``risk-scores.sarif`` document, by the finding's ``findingId/v1``."""
    run = document["runs"][0]
    tool = run["tool"]["driver"]["name"]
    return {finding_id: (tool, SCORER_CATEGORY) + key for finding_id, key in keys_of(run["results"]).items()}


def results_by(document):
    return {r["partialFingerprints"]["findingId/v1"]: r for r in document["runs"][0]["results"]}


def ruling_c(group, primary, peers=None):
    """Ruling C's sentence, written out from ``contracts/sarif-result.md`` and not taken from the emitter.

    ``peers`` is ``None`` on a peer. On a primary the first ten are named in group order, then `` and N more``.
    """
    if peers is None:
        return "Correlated in %s; primary %s." % (group, primary)
    more = len(peers) - 10
    return "Correlated in %s; peers %s%s." % (group, ", ".join(peers[:10]), " and %d more" % more if more > 0 else "")


def expected_text(threat, assignment):
    if assignment is None:
        return threat
    peers = list(assignment.peers) if assignment.role == "primary" else None
    return threat + " " + ruling_c(assignment.group, assignment.primary, peers)


def snapshot_run(rrs, project, name="baseline-1"):
    """Copy a finished run's input and outputs under their canonical names: what a later run's ``--baseline`` names."""
    target = project.root / name
    target.mkdir()
    for source in ("threats.md", rrs.MD, rrs.SARIF):
        shutil.copyfile(str(project.out / source), str(target / source))
    return target


def rewrite_inputs(rrs, project, specs, groups=(), resolved=None):
    """Replace the run's ``threats.md``, as the next run's threat model would."""
    project.specs = list(specs)
    if resolved is not None:
        project.resolved = list(resolved)
    project.threats.write_text(rrs.make_threats_md(project.specs, project.resolved, groups=groups), encoding="utf-8")


def second_run_specs(rrs, baseline_aware):
    """Run 2's findings: run 1's, carried (UNCHANGED against a baseline), and one that only run 2 finds."""
    carried = [dict(item, status="UNCHANGED") if baseline_aware else dict(item) for item in rrs.SPECS]
    found_later = rrs.spec("T-7", "auth-broker", "A threat that only the second run finds.", "Medium", "NEW",
                           "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L", (6, 6, 6, 6), (5, 5, 5, 5),
                           "Edge DMZ", "Semi-Trusted", 0, 0)
    return carried + [found_later]


def planted_sarif(ids, offset=0):
    """A SARIF file as an older tachi would write it: a ``findingId/v1`` and a hash of its own on every result."""
    results = [{"ruleId": "tachi/stride/spoofing", "message": {"text": "x"}, "level": "error",
                "partialFingerprints": {"primaryLocationLineHash": PLANTED_HASHES[offset + n], "findingId/v1": finding_id},
                "properties": {"security-severity": "5.0"}} for n, finding_id in enumerate(ids)]
    return json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": SCORER}}, "results": results}]}, indent=2) + "\n"


def run_pair(rrs, entries, root, baseline_aware, plant=False, replace_baseline_sarif=False):
    """Render run 1, then run 2 (regrouped, with one more finding), in one project.

    Run 2 is baseline-aware when asked: run 1's files become its ``--baseline``, and its carried findings are
    UNCHANGED. ``plant`` puts an upstream ``threats.sarif`` with hashes of its own beside run 1's input, and
    ``replace_baseline_sarif`` swaps the baseline's SARIF for one that lists other findings under other hashes.
    """
    project = scorer_project(rrs, entries, root, groups=FIRST_RUN_GROUPS)
    ids_1 = [item["id"] for item in rrs.SPECS]
    if plant:
        (project.out / "threats.sarif").write_text(planted_sarif(ids_1), encoding="utf-8")
    first = project.run()
    assert first.code == 0, first.describe()
    pair = SimpleNamespace(project=project, ids_1=ids_1, specs_1=list(rrs.SPECS), baseline=None,
                           first=project.sarif, first_text=project.sarif_text, first_md=project.md)
    if baseline_aware:
        pair.baseline = snapshot_run(rrs, project)
        if replace_baseline_sarif:
            (pair.baseline / rrs.SARIF).write_text(planted_sarif(ids_1 + ["S-99"], offset=20), encoding="utf-8")
    pair.specs_2 = second_run_specs(rrs, baseline_aware)
    pair.ids_2 = [item["id"] for item in pair.specs_2]
    rewrite_inputs(rrs, project, pair.specs_2, SECOND_RUN_GROUPS)
    second = project.run(baseline_dir=pair.baseline)
    assert second.code in (0, 5), second.describe()
    pair.second, pair.second_text, pair.second_md = project.sarif, project.sarif_text, project.md
    return pair


BOTH_MODES = pytest.mark.parametrize("baseline_aware", [False, True], ids=["stateless", "baseline-aware"])


@BOTH_MODES
def test_the_regroup_pair_keeps_every_carried_key_and_changes_only_the_text(rrs, entries, tmp_path, baseline_aware):
    """US-6a #1: run 2 regroups carried findings, changes a primary and dissolves a group, and no key moves."""
    pair = run_pair(rrs, entries, tmp_path, baseline_aware)
    keys_1, keys_2 = alert_keys(pair.first), alert_keys(pair.second)
    assert sorted(keys_1) == sorted(pair.ids_1) and sorted(keys_2) == sorted(pair.ids_2), "no finding drops out"
    for finding_id in pair.ids_1:
        assert keys_2[finding_id] == keys_1[finding_id], "%s: a regroup never moves a key" % finding_id
    assert "T-7" in keys_2 and "T-7" not in keys_1, "the finding only run 2 has gets a key of its own"
    for keys in (keys_1, keys_2):
        assert len(set(keys.values())) == len(keys), "no two present results share a key (the F-012 lesson)"
    texts = {}
    for run, document, specs, groups, ids in ((1, pair.first, pair.specs_1, FIRST_RUN_GROUPS, pair.ids_1),
                                              (2, pair.second, pair.specs_2, SECOND_RUN_GROUPS, pair.ids_2)):
        assignments = sc.correlation_assignments(groups, ids)
        sc.self_check(document["runs"][0]["results"], tool=SCORER, member_ids=ids, assignments=assignments,
                      resolved_ids=rrs.RESOLVED_IDS, uri=URI)
        by_id = results_by(document)
        for item in specs:
            text = by_id[item["id"]]["message"]["text"]
            assert text == expected_text(item["threat"], assignments.get(tachi_parts.canonical_finding_id(item["id"]))), (run, item["id"])
            texts[(run, item["id"])] = text
    for finding_id in ("T-1", "E-5", "AG-1"):
        assert texts[(1, finding_id)] != texts[(2, finding_id)], "%s: a regroup changes its text (ruling C)" % finding_id


@BOTH_MODES
def test_an_unchanged_rerun_of_the_renderer_keeps_its_keys_and_its_bytes(rrs, entries, tmp_path, baseline_aware):
    """US-6a #2: the same inputs under a fresh plan give the same keys, and the same bytes, in both files."""
    pair = run_pair(rrs, entries, tmp_path, baseline_aware)
    again = pair.project.run(baseline_dir=pair.baseline)
    assert again.code in (0, 5), again.describe()
    assert pair.project.sarif_text == pair.second_text and pair.project.md == pair.second_md
    assert alert_keys(pair.project.sarif) == alert_keys(pair.second)


@BOTH_MODES
def test_the_hash_recomputes_from_the_tool_and_the_id_and_no_upstream_hash_is_copied(rrs, entries, tmp_path, baseline_aware):
    pair = run_pair(rrs, entries, tmp_path, baseline_aware, plant=True, replace_baseline_sarif=baseline_aware)
    for document, text in ((pair.first, pair.first_text), (pair.second, pair.second_text)):
        for result in document["runs"][0]["results"]:
            written = result["partialFingerprints"]["findingId/v1"]
            assert result["partialFingerprints"]["primaryLocationLineHash"] == recipe(SCORER, tachi_parts.canonical_finding_id(written)), written
        assert not [planted for planted in PLANTED_HASHES if planted in text], "an upstream or earlier hash was copied (S-6)"
        assert "automationDetails" not in text and "runAutomationDetails" not in text, "the upload step's category governs (D7)"
    assert results_by(pair.first)["AGP-01"]["partialFingerprints"]["primaryLocationLineHash"] == recipe(SCORER, "AGP-1"), \
        "the hash is over the canonical ID, and findingId/v1 keeps Section 7's spelling"


def test_no_stage_reads_a_baseline_sarifs_membership_or_hashes(rrs, entries, tmp_path):
    """ADR-050 D8: SV-3's trigger does not fire, because no stage reads a baseline SARIF's membership or hashes."""
    pair = run_pair(rrs, entries, tmp_path, True, replace_baseline_sarif=True)
    assert sorted(alert_keys(pair.second)) == sorted(pair.ids_2), "the member set is Section 7's"
    assert "S-99" not in pair.second_text
    keys_1, keys_2 = alert_keys(pair.first), alert_keys(pair.second)
    assert all(keys_2[finding_id] == keys_1[finding_id] for finding_id in pair.ids_1)


def test_no_two_present_results_share_a_key_in_a_run_of_forty_two_findings(rrs, entries, tmp_path):
    project, reference = rrs.subset_project(entries[0], entries[1], tmp_path)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    document = project.sarif
    keys = alert_keys(document)
    assert len(keys) == len(reference["open"]) == 42
    assert len(set(keys.values())) == 42 and len({key[3] for key in keys.values()}) == 42, "42 findings, 42 keys and 42 hashes"
    shared = {}
    for result in document["runs"][0]["results"]:
        component = result["locations"][0]["logicalLocations"][0]["name"]
        shared.setdefault((result["ruleId"], component), []).append(result["partialFingerprints"]["findingId/v1"])
    sharing = [ids for ids in shared.values() if len(ids) > 1]
    assert sharing, "the subset has findings that share a rule and a component"
    for ids in sharing:
        assert len({keys[finding_id] for finding_id in ids}) == len(ids), "distinct findings on one component and rule get separate alerts"


# --- the architecture path: the flag, then the body line, then the default (FR-E.18; US-6a #7 to #9) ---------------

URI_CASES = [  # id, the flag, the body line, whether the run directory has the snapshot, the URI, the warnings' codes
    ("the-flag-wins", "docs/design/system.md", "docs/other/architecture.md", True, "docs/design/system.md", []),
    ("the-body-line-outside-docs-security", None, "docs/other/architecture.md", True, "docs/other/architecture.md", []),
    ("the-default-and-a-warning-that-names-the-flag", None, None, False, "docs/security/architecture.md",
     ["architecture-path:body-line:absent"]),
    ("a-flag-outside-the-repository-falls-to-the-body-line", "OUTSIDE", "docs/other/architecture.md", True,
     "docs/other/architecture.md", ["architecture-path:explicit:outside-root"]),
    ("a-symlinked-flag-falls-to-the-body-line", "docs/design/link.md", "docs/other/architecture.md", True,
     "docs/other/architecture.md", ["architecture-path:explicit:symlink"]),
    ("a-body-line-with-no-snapshot-falls-to-the-default", None, "docs/other/architecture.md", False,
     "docs/security/architecture.md", ["architecture-path:body-line:no-snapshot"]),
    ("a-body-line-naming-a-tachi-output-falls-to-the-default", None, "docs/security/threats.md", True,
     "docs/security/architecture.md", ["architecture-path:body-line:canonical-name"]),
    ("a-failed-flag-and-an-absent-line-fall-to-the-default", "OUTSIDE", None, False, "docs/security/architecture.md",
     ["architecture-path:explicit:outside-root", "architecture-path:body-line:absent"]),
]


@pytest.fixture
def outside_file(tmp_path_factory):
    path = tmp_path_factory.mktemp("outside") / "arch.md"
    path.write_text("# an architecture file outside the repository\n", encoding="utf-8")
    return path


def add_architecture_files(project):
    """The files the carrier cases name, beside the project's default ``docs/security/architecture.md``."""
    for relative in ("docs/design/system.md", "docs/other/architecture.md", "docs/security/threats.md"):
        path = project.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# %s\n" % relative, encoding="utf-8")
    (project.root / "docs" / "design" / "link.md").symlink_to("system.md")


@pytest.mark.parametrize("flag,body,snapshot,uri,warning_codes", [case[1:] for case in URI_CASES], ids=[case[0] for case in URI_CASES])
def test_the_flag_then_the_body_line_then_the_default_and_each_failed_carrier_warns(
        rrs, entries, tmp_path, outside_file, flag, body, snapshot, uri, warning_codes):
    project = scorer_project(rrs, entries, tmp_path, body_line=body)
    add_architecture_files(project)
    if snapshot:
        (project.out / "architecture.md").write_text("# the snapshot the threat model copied\n", encoding="utf-8")
    res = project.run(architecture=str(outside_file) if flag == "OUTSIDE" else flag)
    assert res.code == (5 if warning_codes else 0), res.describe()
    results = project.sarif["runs"][0]["results"]
    assert {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in results} == {uri}
    record = project.record
    assert [warning["code"] for warning in record["warnings"]] == warning_codes, "the stage record lists each warning, in order"
    assert record["status"] == ("success-with-warnings" if warning_codes else "success")
    assert all("--architecture-path" in warning["detail"] for warning in record["warnings"]), "each one names the override flag"
    sc.self_check(results, tool=SCORER, member_ids=[item["id"] for item in rrs.SPECS], assignments={},
                  resolved_ids=rrs.RESOLVED_IDS, uri=uri)


def test_a_run_always_gets_a_uri_even_when_nothing_validates(rrs, entries, tmp_path, outside_file):
    project = scorer_project(rrs, entries, tmp_path)
    project.architecture.unlink()
    res = project.run(architecture=str(outside_file))
    assert res.code == 5, res.describe()
    assert [w["code"] for w in project.record["warnings"]] == [
        "architecture-path:explicit:outside-root", "architecture-path:body-line:absent", "architecture-path:default:missing",
        "tag-source:no-architecture-file"], (
        "D7's chain in order, then the tag source: with no architecture file the block's tags are applied unverified, and "
        "that warns, because the stage record has no other trace of it (ruled at W2, ADR-050 D2)")
    assert "unverified" in project.record["warnings"][-1]["detail"]
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {sc.DEFAULT_ARCHITECTURE_PATH}, "the constant is emitted as written, and nothing here stops a run"


def mirror(fake, root):
    """Copy the layout of a real project (its directories and regular files) into the fake filesystem."""
    for path in sorted(Path(root).rglob("*")):
        if path.relative_to(root).parts[0] == ".tachi-build":
            continue
        if path.is_dir():
            fake.mkdir(str(path))
        elif path.is_file():
            fake.file(str(path))


@pytest.mark.parametrize("body", ["docs/other/architecture.md", "DOCS/Other/ARCHITECTURE.md"], ids=["canonical", "case-variant"])
def test_a_case_variant_body_line_gives_every_result_the_same_uri_on_a_case_insensitive_volume(
        rrs, entries, tmp_path, monkeypatch, body):
    """KB 24 and FR-E.2: the resolver, not the renderer, spells the path, so a case variant gives one URI.

    The renderer reaches the filesystem through ``sarif_common.OS_FILESYSTEM`` for this, so a fake case-insensitive
    volume stands in for the one an adopter's laptop has.
    """
    project = scorer_project(rrs, entries, tmp_path, body_line=body)
    add_architecture_files(project)
    (project.out / "architecture.md").write_text("# the snapshot\n", encoding="utf-8")
    fake = FakeFilesystem(str(tmp_path), case_insensitive=True)
    mirror(fake, tmp_path)
    monkeypatch.setattr(sc, "OS_FILESYSTEM", fake)
    res = project.run(architecture=False)
    assert res.code == 0, res.describe()
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {"docs/other/architecture.md"}


# --- ruling C: a primary with more than ten peers; ruling B: reused IDs -----------------------------------------------

@pytest.mark.parametrize("size,more", [(11, 0), (12, 1), (13, 2)], ids=["ten-peers", "eleven-peers", "twelve-peers"])
def test_a_primary_with_more_than_ten_peers_names_ten_and_then_a_count(rrs, entries, tmp_path, size, more):
    """PM-T7, ruling C: the first ten in group order, joined by a comma and a space, then `` and N more``."""
    specs = [rrs.spec("S-%d" % n, "edge-gateway", "Threat %d on the gateway." % n, "Medium", "NEW",
                      "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0)
             for n in range(1, size + 1)]
    ids = [item["id"] for item in specs]
    project = scorer_project(rrs, entries, tmp_path, specs=specs, resolved=[], groups=[("CG-1", ids)])
    res = project.run()
    assert res.code in (0, 5), res.describe()
    results = results_by(project.sarif)
    assert len(results) == size, "every peer is a result, once"
    tail = "Correlated in CG-1; peers " + ", ".join(ids[1:11]) + (" and %d more" % more if more else "") + "."
    assert results["S-1"]["message"]["text"] == "Threat 1 on the gateway. " + tail == "Threat 1 on the gateway. " + ruling_c("CG-1", "S-1", ids[1:])
    for peer in ids[1:]:
        assert results[peer]["message"]["text"] == "Threat %s on the gateway. Correlated in CG-1; primary S-1." % peer[2:], peer
    sc.self_check(project.sarif["runs"][0]["results"], tool=SCORER, member_ids=ids,
                  assignments=sc.correlation_assignments([("CG-1", ids)], ids), resolved_ids=[], uri=URI)


def test_a_new_finding_that_reuses_a_baseline_id_is_flagged_and_keeps_the_old_key(rrs, entries, tmp_path):
    """Ruling B (D7), PR 1's half: the flag marks the exposure, and the key shows it: the old alert's key is reused."""
    project = scorer_project(rrs, entries, tmp_path)
    assert project.run().code == 0
    keys_1 = alert_keys(project.sarif)
    baseline = snapshot_run(rrs, project)
    reissued = [
        rrs.spec("S-2", "auth-broker", "A different threat that was given S-2 after the first one went away.", "Medium", "NEW",
                 "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0),
        rrs.spec("S-1", "edge-gateway", "A new threat that was given S-1, which the baseline lists as RESOLVED.", "Medium", "NEW",
                 "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0)]
    specs_2 = [dict(item, status="UNCHANGED") for item in rrs.SPECS if item["id"] != "S-2"] + reissued
    rewrite_inputs(rrs, project, specs_2, (), resolved=[row for row in rrs.RESOLVED if row[0] != "S-1"])
    res = project.run(baseline_dir=baseline)
    assert res.code in (0, 5), res.describe()
    results = results_by(project.sarif)
    flag = "reused-id:finding_id:baseline"
    assert sorted(i for i, r in results.items() if flag in r["properties"]["score-flags"]) == ["S-1", "S-2"], \
        "a NEW finding whose ID is in any baseline row, open or RESOLVED, is flagged"
    assert all(r["properties"]["score-flags"] == sorted(r["properties"]["score-flags"]) for r in results.values())
    assert alert_keys(project.sarif)["S-2"] == keys_1["S-2"], "the reissued ID inherits the old alert: the exposure the flag marks (ruling B)"
    assert project.record["counts"]["reused-id"] == 2
    rows = {row["ID"]: row for row in rrs.records(*rrs.table_of(rrs.section(project.md, "## 2. Scored Threat Table"), "ID"))}
    assert "reused-id" in rows["S-2"]["Flags"] and "reused-id" in rows["S-1"]["Flags"] and rows["T-1"]["Flags"] == rrs.DASH


# =============================================================================
# 17. D8's fallback reader (T142): the new form, the legacy forms and an empty extraction
# =============================================================================
#
# ``tachi_parsers.parse_sarif_member_set(sarif_text, *, with_scores=False)`` returns ``{"members", "groups", "scores"}``
# (``contracts/module-signatures.md``). The member set of a stage whose markdown input is absent comes from here, so an
# empty extraction raises ``ValueError`` and the stage stops before dispatch (KB 22; AR-T2). Lane P's rulings:
# ``group_id`` is the ``correlation-group`` property, then the legacy ``partialFingerprints["correlationGroup"]``, then
# ``None``; named groups come in group-number order; and, by the architect's option (b), a result with no
# ``findingId/v1`` takes its ID from ``properties.id`` when that passes the finding allow-list.


def read_members(text, **kwargs):
    if not hasattr(tachi_parsers, "parse_sarif_member_set"):
        pytest.fail("tachi_parsers.parse_sarif_member_set does not exist yet: T142 (lane P) writes it to these cases", pytrace=False)
    return tachi_parsers.parse_sarif_member_set(text, **kwargs)


def hand_result(finding_id=None, *, properties=None, fingerprints=None, related=None, extra=None):
    """A result written by hand, in the older shapes the reader must still take."""
    result = {"ruleId": "tachi/stride/spoofing", "message": {"text": "A threat."}, "level": "error",
              "partialFingerprints": dict(fingerprints or {}), "properties": dict(properties or {})}
    if finding_id is not None:
        result["partialFingerprints"]["findingId/v1"] = finding_id
    if related:
        result["relatedLocations"] = [{"id": n, "message": {"text": text}} for n, text in enumerate(related)]
    result.update(extra or {})
    return result


def hand_sarif(results):
    return json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "Tachi"}}, "results": results}]})


def test_the_new_form_gives_members_in_result_order_and_groups_from_the_correlation_properties():
    results, _assignments = build_run()  # S-1, T-2, I-3, D-4 and AG-5; CG-1 holds S-1 and T-2 (R-9 is resolved), CG-2 I-3 and D-4
    got = read_members(sc.to_json(document(results)))
    assert got["members"] == MEMBERS
    assert got["groups"] == [{"group_id": "CG-1", "primary": "S-1", "members": ["S-1", "T-2"]},
                             {"group_id": "CG-2", "primary": "I-3", "members": ["I-3", "D-4"]}]
    assert got["scores"] == {}


def test_a_finding_id_is_canonical_in_the_member_set_and_a_repeat_is_one_member():
    got = read_members(hand_sarif([hand_result("AGP-01"), hand_result("S-1"), hand_result("AGP-1")]))
    assert got["members"] == ["AGP-1", "S-1"]


@pytest.mark.parametrize("marker", [
    {"extra": {"baselineState": "absent"}}, {"properties": {"baseline-state": "absent"}}, {"properties": {"baselineState": "absent"}},
], ids=["result-baselineState", "property-baseline-state", "property-baselineState"])
def test_a_resolved_result_appears_nowhere_not_even_as_a_legacy_peer_reference(marker):
    gone = hand_result("R-9", **marker)
    kept = hand_result("S-1", related=["R-9: a peer that is resolved", "T-2: a peer that is open"])
    got = read_members(hand_sarif([kept, gone, hand_result("I-3")]), with_scores=True)
    assert got["members"] == ["S-1", "T-2", "I-3"], "R-9 is neither a result nor a reference"
    assert "R-9" not in got["scores"] and all("R-9" not in group["members"] for group in got["groups"])


def test_the_legacy_form_reads_peers_from_related_locations_and_the_group_from_the_fingerprint():
    legacy = hand_sarif([
        hand_result("S-1", fingerprints={"correlationGroup": "CG-10"}, related=["T-2: a peer", "AGP-01: another peer"]),
        hand_result("I-3", fingerprints={"correlationGroup": "CG-2"}, related=["D-4: a peer"]),
        hand_result("E-1"),
    ])
    got = read_members(legacy)
    assert got["members"] == ["S-1", "T-2", "AGP-1", "I-3", "D-4", "E-1"], "a legacy peer follows its result"
    assert got["groups"] == [{"group_id": "CG-2", "primary": "I-3", "members": ["I-3", "D-4"]},
                             {"group_id": "CG-10", "primary": "S-1", "members": ["S-1", "T-2", "AGP-1"]}], \
        "the group ID is the legacy fingerprint, and named groups come in group-number order, not text order"


def test_the_correlation_group_property_wins_over_the_legacy_fingerprint_and_an_unnamed_group_has_none():
    got = read_members(hand_sarif([
        hand_result("S-1", properties={"correlation-group": "CG-3"}, fingerprints={"correlationGroup": "CG-9"}, related=["T-2: a peer"]),
        hand_result("I-3", related=["D-4: a peer"]),
    ]))
    assert got["groups"] == [{"group_id": "CG-3", "primary": "S-1", "members": ["S-1", "T-2"]},
                             {"group_id": None, "primary": "I-3", "members": ["I-3", "D-4"]}]


def test_a_result_with_no_findingid_takes_its_member_id_from_properties_id():
    """The architect's option (b): the form four shipped samples use. Red until lane P's follow-up lands."""
    got = read_members(hand_sarif([
        hand_result(None, properties={"id": "S-1"}), hand_result(None, properties={"id": "AGP-01"}),
        hand_result(None, properties={"id": "S-1\n"}), hand_result(None, properties={"id": "x"}), hand_result(None, properties={"id": 5}),
        hand_result(None, properties={"id": "\u0663-1"}), hand_result(None),
    ]))
    assert got["members"] == ["S-1", "AGP-1"], "an ID that fails the finding allow-list is skipped, never read"


def test_findingid_v1_wins_when_a_result_carries_both():
    got = read_members(hand_sarif([hand_result("S-1", properties={"id": "T-9"}), hand_result(None, properties={"id": "I-3"})]))
    assert got["members"] == ["S-1", "I-3"]


def test_scores_are_read_across_the_property_names_the_shipped_files_use():
    shipped = hand_result("S-1", properties={"security-severity": "8.0", "severity-band": "High"})
    generator = hand_result("T-2", properties={"composite": 7.5, "severity_band": "High"})
    older = hand_result("I-3", properties={"security-severity": "4.25", "severity": "medium"})
    unscored = hand_result("D-4", properties={"composite": "not a number", "severity-band": "Severe"})
    got = read_members(hand_sarif([shipped, generator, older, unscored]), with_scores=True)
    assert got["scores"] == {"S-1": {"composite": Decimal("8.0"), "band": "High"}, "T-2": {"composite": Decimal("7.5"), "band": "High"},
                             "I-3": {"composite": Decimal("4.25"), "band": "Medium"}, "D-4": {"composite": None, "band": None}}
    assert read_members(hand_sarif([shipped]))["scores"] == {}, "scores only when asked for"


EMPTY_EXTRACTIONS = [
    {"runs": [{"results": []}]},
    {"runs": []},
    {},
    [],
    {"runs": "not a list"},
    {"runs": [{"results": [hand_result("R-9", properties={"baseline-state": "absent"})]}]},
    {"runs": [{"results": [{"partialFingerprints": {"primaryLocationLineHash": "0123456789abcdef:1"}}]}]},
    {"runs": [{"results": [hand_result(None, properties={"id": "not an id"}), 42, "x", None]}]},
]


@pytest.mark.parametrize("document_", EMPTY_EXTRACTIONS, ids=[str(n) for n in range(len(EMPTY_EXTRACTIONS))])
def test_an_empty_extraction_raises_so_the_stage_stops_before_dispatch_and_the_error_names_the_remedy(document_):
    with pytest.raises(ValueError) as excinfo:
        read_members(json.dumps(document_))
    assert "regenerate" in str(excinfo.value).lower(), "the remedy is to regenerate the markdown input (the architect's ruling)"


@pytest.mark.parametrize("text", ["", "not json", "{", '{"runs": NaN}', '{"runs": Infinity}', '{"a": 123456789012345678901}'])
def test_text_that_is_not_strict_json_raises_value_error(text):
    with pytest.raises(ValueError):
        read_members(text)


def test_a_result_of_any_other_shape_is_skipped_and_never_raised_on():
    odd = [42, "x", None, [], {"partialFingerprints": "x"}, {"partialFingerprints": {"findingId/v1": ["S-1"]}},
           {"partialFingerprints": {"findingId/v1": "S-1"}, "properties": "x", "relatedLocations": "x"}]
    assert read_members(hand_sarif(odd + [hand_result("T-2")]))["members"] == ["S-1", "T-2"]


def test_no_hash_is_ever_read_so_files_that_differ_only_in_their_hashes_give_one_extraction():
    def build(prefix):
        return hand_sarif([hand_result(i, fingerprints={"primaryLocationLineHash": "%s%d:1" % (prefix, n)}) for n, i in enumerate(MEMBERS)])

    assert read_members(build("0000000000000")) == read_members(build("ffffffffffff"))


def shipped_sarif_files():
    return sorted(REPO_ROOT.glob("examples/**/*.sarif"))


def expected_result_ids(document_):
    """Each shipped result's own ID: ``findingId/v1``, else ``properties.id``; resolved results left out; once each."""
    found = []
    for result in document_["runs"][0]["results"]:
        properties = result.get("properties") or {}
        identifier = (result.get("partialFingerprints") or {}).get("findingId/v1") or properties.get("id")
        absent = "absent" in (result.get("baselineState"), properties.get("baseline-state"), properties.get("baselineState"))
        if tachi_parts.id_matches("finding", identifier) and not absent:
            canonical = tachi_parts.canonical_finding_id(identifier)
            if canonical not in found:
                found.append(canonical)
    return found


@pytest.mark.parametrize("path", shipped_sarif_files(), ids=lambda path: "/".join(path.parts[-3:]))
def test_every_shipped_sarif_is_read_into_its_own_member_set(path):
    """The four samples that carry only ``properties.id`` are red until lane P's follow-up lands (option (b))."""
    text = path.read_text(encoding="utf-8")
    document_ = json.loads(text)
    expected = expected_result_ids(document_)
    assert expected, "the sample has findings"
    scored = path.name == "risk-scores.sarif"
    got = read_members(text, with_scores=scored)
    assert len(got["members"]) == len(set(got["members"])), "each ID once"
    assert set(expected) <= set(got["members"]), "every result of the sample is a member"
    if not any(result.get("relatedLocations") for result in document_["runs"][0]["results"]):
        assert got["members"] == expected, "with no legacy peer reference, the sample's own results in result order"
    if scored:
        for finding_id in expected:
            assert got["scores"][finding_id]["composite"] is not None and got["scores"][finding_id]["band"] is not None, finding_id


def test_the_shipped_samples_are_found_so_the_cases_above_never_shrink_to_none():
    assert len(shipped_sarif_files()) >= 16


@pytest.mark.parametrize("name", ["threats.md", "threats.sarif"], ids=["markdown-absent", "sarif-as-the-input"])
def test_an_empty_extraction_stops_the_planner_before_dispatch_and_writes_nothing(tmp_path, name):
    """Today's command passes ``threats.sarif`` as the input when ``threats.md`` is absent; either spelling must stop."""
    stage = _load_hyphenated_script("tachi_stage_for_fallback_cases", "tachi-stage.py")
    (tmp_path / "threats.sarif").write_text(hand_sarif([hand_result("R-9", properties={"baseline-state": "absent"})]), encoding="utf-8")
    with pytest.raises(stage.StageError) as excinfo:
        stage.plan_stage(stage="risk-score", out=tmp_path, date="2026-11-22", threats=tmp_path / name)
    assert excinfo.value.code in (1, 2)
    assert not (tmp_path / ".tachi-build").exists(), "nothing was planned, so nothing is dispatched"


# =============================================================================
# 18. message.markdown: the scorer's mitigation text (the architect's ruling from T027; R0b's build_result and self_check)
# =============================================================================
#
# A file whose contract maps ``message.markdown`` keeps it, after ``text`` (NFR-1 keeps adopter fields, and the message
# isn't identity). ``build_result`` takes it as an optional ``markdown``. ``self_check`` takes ``{text}`` or
# ``{text, markdown}``, in that key order only. H8's roots are built in pieces, so this file holds no path itself.

H8_ROOTS = ("Us" + "ers", "ho" + "me", "pri" + "vate", "t" + "mp", "var/fol" + "ders")
MITIGATION = "Restrict write access to the store and sign each record."
LOCAL_PATHS_IN_MARKDOWN = (
    ["/%s/dev/app/src/auth.py" % root for root in H8_ROOTS]
    + ["Edit /%s/dev/app/src/auth.py to fix it." % H8_ROOTS[1], "See file:///%s/dev/app/notes.md" % H8_ROOTS[0],
       "C:\\" + "Users\\dev\\app\\notes.md", "D:\\work\\notes.md"])
MARKDOWN_THAT_IS_NOT_A_LOCAL_PATH = [
    "src/%s/k.js" % H8_ROOTS[2],  # a relative path with a segment that is named like a root
    "Move the check into src/%s/k.js." % H8_ROOTS[2],
    "See https://owasp.org/Top10/ and https://example.org/%s/page for the background." % H8_ROOTS[1],  # URL paths
    "https://example.org/%s/%s/page" % (H8_ROOTS[3], "x"),
    "Restrict read/write access, rotate keys and/or tokens, and use TLS 1.3/mTLS.",
    "Grant access per workload identity (docs/security/architecture.md).",
    "",  # two shipped mitigations are empty
]


def test_a_result_with_markdown_has_a_text_and_markdown_message_in_that_key_order():
    result = make_result("T-2", markdown=MITIGATION)
    assert result["message"] == {"text": "Tampering with the store.", "markdown": MITIGATION}
    assert list(result["message"]) == ["text", "markdown"]
    assert list(result) == ["ruleId", "message", "level", "locations", "partialFingerprints", "properties"], "nothing else moves"
    check([result], {}, members=["T-2"], resolved=[])


def test_without_markdown_the_message_stays_text_only_and_the_result_is_byte_identical():
    plain = make_result("T-2")
    expected = {
        "ruleId": "tachi/stride/tampering",
        "message": {"text": "Tampering with the store."},
        "level": "warning",
        "locations": [{"physicalLocation": {"artifactLocation": {"uri": URI}, "region": {"startLine": 1}},
                       "logicalLocations": [{"name": "Store", "fullyQualifiedName": "Data Zone/Store", "kind": "data-store"}]}],
        "partialFingerprints": {"primaryLocationLineHash": recipe(SCORER, "T-2"), "findingId/v1": "T-2"},
        "properties": {"score-source": "fresh"},
    }
    assert json.dumps(plain, indent=2) == json.dumps(expected, indent=2), "the shape the emitter wrote before the parameter existed"
    assert list(plain["message"]) == ["text"]
    assert json.dumps(make_result("T-2", markdown=None)) == json.dumps(plain)
    check([plain], {}, members=["T-2"], resolved=[])


def test_ruling_cs_sentence_goes_on_text_alone_and_markdown_is_kept_as_given():
    result = make_result("T-2", markdown=MITIGATION, correlation=corr("peer", primary="S-1", group="CG-3"))
    assert result["message"] == {"text": "Tampering with the store. Correlated in CG-3; primary S-1.", "markdown": MITIGATION}
    assert list(result["message"]) == ["text", "markdown"]
    primary = make_result("S-1", markdown=MITIGATION, correlation=corr("primary", primary="S-1", peers=("T-2", "I-4"), group="CG-3"))
    assert primary["message"]["text"].endswith(" " + ruling_c("CG-3", "S-1", ["T-2", "I-4"])) and primary["message"]["markdown"] == MITIGATION


def test_an_empty_markdown_is_kept_and_passes_the_self_check():
    result = make_result("T-2", markdown="")
    assert result["message"] == {"text": "Tampering with the store.", "markdown": ""}
    check([result], {}, members=["T-2"], resolved=[])


@pytest.mark.parametrize("bad", [5, 1.5, True, ["a"], {"a": 1}, b"bytes"], ids=repr)
def test_the_builder_refuses_a_markdown_that_is_not_a_string(bad):
    with pytest.raises(ValueError):
        make_result("T-2", markdown=bad)


@pytest.mark.parametrize("bad", [5, None, True, ["a"], {"a": 1}], ids=repr)
def test_the_self_check_refuses_a_markdown_that_is_not_a_string(bad):
    result = make_result("T-2", markdown=MITIGATION)
    result["message"]["markdown"] = bad
    assert any("markdown" in problem for problem in problems_of([result], {}, members=["T-2"], resolved=[]))


@pytest.mark.parametrize("text", LOCAL_PATHS_IN_MARKDOWN, ids=[str(n) for n in range(len(LOCAL_PATHS_IN_MARKDOWN))])
def test_the_self_check_refuses_a_local_path_in_markdown(text):
    result = make_result("T-2", markdown=text)
    assert any("markdown" in problem and "path" in problem for problem in problems_of([result], {}, members=["T-2"], resolved=[]))


@pytest.mark.parametrize("text", MARKDOWN_THAT_IS_NOT_A_LOCAL_PATH, ids=[str(n) for n in range(len(MARKDOWN_THAT_IS_NOT_A_LOCAL_PATH))])
def test_the_self_check_accepts_markdown_that_only_looks_like_a_path(text):
    check([make_result("T-2", markdown=text)], {}, members=["T-2"], resolved=[])


def test_the_self_check_refuses_a_resolved_id_in_markdown_and_not_one_inside_another_token():
    result = make_result("T-2", markdown="This is related to S-9, which was fixed.")
    assert any("S-9" in problem and "markdown" in problem for problem in problems_of([result], {}, members=["T-2"], resolved=["S-9"]))
    check([make_result("T-2", markdown="See S-90 and AS-9 for the background.")], {}, members=["T-2"], resolved=["S-9"])


@pytest.mark.parametrize("message", [
    {"markdown": "x", "text": "A threat."}, {"text": "A threat.", "markdown": "x", "html": "x"}, {"markdown": "x"}, {"text": "A threat.", "Markdown": "x"},
], ids=["markdown-first", "an-extra-key", "markdown-alone", "another-spelling"])
def test_the_self_check_takes_text_or_text_and_markdown_in_that_order_only(message):
    result = make_result("T-2", markdown=MITIGATION)
    result["message"] = message
    assert any("message" in problem for problem in problems_of([result], {}, members=["T-2"], resolved=[]))


def test_a_markdown_result_round_trips_through_the_document_as_ascii_json():
    result = make_result("T-2", markdown="Rotate the key \u2014 caf\u00e9 style.")
    text = sc.to_json(document([result]))
    assert text.isascii() and json.loads(text)["runs"][0]["results"][0]["message"]["markdown"] == "Rotate the key \u2014 caf\u00e9 style."
