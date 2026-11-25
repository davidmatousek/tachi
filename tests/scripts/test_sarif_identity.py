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

T049 and T052, T142 and the message text: the renderers' files
16. ``risk-scores.sarif`` and ``compensating-controls.sarif`` through their renderers (FR-E.2's two-run model)
17. D8's fallback reader (T142)
18. ``message.markdown``
19. ``compensating-controls.sarif``: the cases that are the controls file's own (T052)

PM W3 ruling 2, gaps A and C, and T052's evidence-URI finding: what both renderers share
20. The shared rules table (``RULES``, ``build_rules``) against both 1.1 templates

The architect's W3 ruling d, question 9 (P0-10): what the RESOLVED scan reads
21. The scan reads what a renderer composes, and not text it copies (the scorer's renderer drives the last cases)

T099, PR 2: ``threats.sarif`` through its generator (``scripts/generate-threats-sarif.py``, red until T100)
22. FR-E.2's two-run model for the third file, D7's carrier chain, ruling C's 10-peer cap, the three files side by side, and FR-E.13's pin

Section 11 also holds the guard that a result's URI and an evidence URI are relative, as written and as decoded (SA-11),
and section 12 the driver's ``version``.

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


def test_the_rule_map_agrees_with_the_identifier_allow_list_and_the_scoring_resolver():
    prefixes = set(sc.RULE_ID_BY_PREFIX)
    assert prefixes == set(tachi_parts.FINDING_PREFIXES) == set(tachi_scoring.PREFIX_CATEGORY)
    for prefix in prefixes:
        category = tachi_scoring.category_for_prefix(prefix)
        assert sc.RULE_ID_BY_PREFIX[prefix] == sc.RULE_ID_BY_CATEGORY[category]


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


@pytest.mark.parametrize("tool", [SCORER, CONTROLS, THREATS], ids=["risk-scores", "compensating-controls", "threats"])
def test_a_resolved_id_may_not_appear_in_a_property_however_deep(tool):
    """The scan reads every property that a renderer composes (Section 21 holds what it does not read: copied text)."""
    results, assignments = build_run(tool=tool)
    results[0]["properties"]["notes"] = ["fine", {"deep": "relates to R-09"}]
    problems = problems_of(results, assignments, tool=tool)
    assert "S-1: the RESOLVED finding R-09 appears in properties.notes[1].deep" in problems, problems


def test_a_resolved_id_that_a_member_also_uses_is_not_resolved_for_this_check():
    results, assignments = build_run()
    check(results, assignments, resolved=["S-1", "R-9"])  # S-1 is a member (a reused ID), so it may appear


def test_a_resolved_id_inside_another_token_or_a_uri_is_not_a_hit():
    results, assignments = build_run()
    results[4]["properties"]["notes"] = "Mentions R-90, XR-9, R-9x and R-9-2."  # AG-5 is uncorrelated; a property is read
    check(results, assignments)
    results[4]["properties"]["notes"] += " And R-9 itself."
    assert "AG-5: the RESOLVED finding R-9 appears in properties.notes" in problems_of(results, assignments)


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


@pytest.mark.parametrize("physical", ["oops", ["x"], 7, None], ids=repr)
def test_a_related_location_whose_physical_location_is_not_an_object_is_refused_and_never_a_crash(physical):
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [{"id": 0, "message": {"text": "Control evidence: x detected in y"}, "physicalLocation": physical}])
    assert any("not code evidence" in p for p in problems_of(results, assignments, tool=CONTROLS))


def evidence_at(uri):
    """A controls evidence entry that points at this URI, for the relative-path cases."""
    return {
        "id": 0, "message": {"text": "Control evidence: authentication detected in a.py"},
        "physicalLocation": {"artifactLocation": {"uri": uri}, "region": {"startLine": 1}},
    }


RELATIVITY_VIOLATIONS = [  # the URI, then the check of the resolver's one syntactic rule (tachi_parts.path_problem) that names it
    ("/etc/passwd", "leading-slash"), ("/docs/security/architecture.md", "leading-slash"),
    ("../secrets.py", "parent-reference"), ("src/../../secrets.py", "parent-reference"),
    ("https://example.test/a.py", "scheme"), ("file:///a.py", "scheme"), ("C:/src/a.py", "drive-letter"),
    ("src\\a.py", "backslash"),
]


@pytest.mark.parametrize(
    "uri,failed", RELATIVITY_VIOLATIONS, ids=["%s:%s" % (failed, uri) for uri, failed in RELATIVITY_VIOLATIONS])
def test_an_evidence_uri_that_is_not_relative_is_refused_naming_the_result_and_the_check(uri, failed):
    """ADR-050 D7: a ``relatedLocations`` URI passes the resolver's relative-path checks (T052's finding).

    The rule is ``tachi_parts.path_problem``, the one the resolver runs, so each case also names its check there.
    """
    assert tachi_parts.path_problem(uri) == failed
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_at("src/auth/login.py"), evidence_at(uri)])  # the good entry beside the bad one is not named
    named = [p for p in problems_of(results, assignments, tool=CONTROLS) if "relatedLocations uri" in p]
    assert len(named) == 1 and named[0].startswith("S-1: ") and sc._short(uri) in named[0] and failed in named[0], named


def test_every_result_with_a_bad_evidence_uri_is_named_once_for_each_bad_entry():
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_at("/etc/passwd")])
    add_related(results[2], [evidence_at("../x.py"), evidence_at("https://example.test/y")])
    named = [p for p in problems_of(results, assignments, tool=CONTROLS) if "relatedLocations uri" in p]
    assert [p.split(":", 1)[0] for p in named] == ["S-1", "I-3", "I-3"]


@pytest.mark.parametrize("uri", ["src/auth/login.py", "login.py", "src/My%20Dir/%C3%A9.py", "a/b/c/d/e.txt"])
def test_a_plain_relative_evidence_uri_passes_the_self_check(uri):
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_at(uri)])
    check(results, assignments, tool=CONTROLS)


def test_an_entry_the_emitter_writes_for_a_resolved_file_passes_the_relative_path_guard():
    evidence = sc.ResolvedPath("src/My Dir/\u00e9.py", "src/My%20Dir/%C3%A9.py")
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [sc.evidence_location(0, "rate-limiting", evidence, 7)])
    check(results, assignments, tool=CONTROLS)


def test_the_evidence_uri_guard_has_no_rule_of_its_own_it_calls_the_resolvers(monkeypatch):
    """Swap ``tachi_parts.path_problem`` out and the guard follows it, both ways: the rule is called, never restated."""
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_at("/etc/passwd")])
    monkeypatch.setattr(tachi_parts, "path_problem", lambda value, allow_absolute=False: None)
    check(results, assignments, tool=CONTROLS)  # a rule that passes everything passes an absolute path too
    monkeypatch.setattr(tachi_parts, "path_problem", lambda value, allow_absolute=False: "a-check-from-tachi-parts")
    named = [p for p in problems_of(results, assignments, tool=CONTROLS) if "relatedLocations uri" in p]
    assert len(named) == 1 and "a-check-from-tachi-parts" in named[0] and named[0].startswith("S-1: ")


# --- SA-11 (T064, T146): the run's own URI is relative too, and each URI is read as a decoder would read it ------------


def run_at(uri, tool=SCORER):
    """A correct run whose every result has this one URI, so the URI guard is all the self-check has to say."""
    assignments = sc.correlation_assignments(GROUPS, MEMBERS)
    return [make_result(m, tool=tool, uri=uri, correlation=assignments.get(m)) for m in MEMBERS], assignments


def check_uri(uri, tool=SCORER):
    results, assignments = run_at(uri, tool)
    sc.self_check(results, tool=tool, member_ids=MEMBERS, assignments=assignments, resolved_ids=["R-9"], uri=uri)


def uri_problems(uri, tool=SCORER):
    with pytest.raises(sc.SelfCheckError) as excinfo:
        check_uri(uri, tool)
    return excinfo.value.problems


def primary_problem(uri, failed):
    return "artifactLocation.uri %s fails the resolver's %s check" % (sc._short(uri), failed)


PRIMARY_VIOLATIONS = RELATIVITY_VIOLATIONS + [("https://evil.invalid/x", "scheme"), ("../x", "parent-reference")]  # the advisory's probes


@pytest.mark.parametrize("uri,failed", PRIMARY_VIOLATIONS, ids=["%s:%s" % (failed, uri) for uri, failed in PRIMARY_VIOLATIONS])
def test_a_primary_uri_that_is_not_relative_is_refused_once_naming_the_uri_and_the_check(uri, failed):
    """SA-11: all five results carry the one bad URI, so the equality check has nothing to say, and nothing else did either."""
    assert tachi_parts.path_problem(uri) == failed
    assert uri_problems(uri) == [primary_problem(uri, failed)], "one problem for the run, not one per result"


@pytest.mark.parametrize("tool", [SCORER, CONTROLS, THREATS], ids=["risk-scores", "compensating-controls", "threats"])
def test_the_primary_uri_guard_covers_each_of_the_three_files(tool):
    """The scorer's file has no other URI to check, so for it this guard is the only one."""
    assert uri_problems("/etc/passwd", tool) == [primary_problem("/etc/passwd", "leading-slash")]


DECODED_VIOLATIONS = [  # the URI as written, which the rule passes, then the check it fails once decoded
    ("%2e%2e/secrets.py", "parent-reference"), ("%2E%2E/secrets.py", "parent-reference"),
    ("docs/%2e%2e/%2e%2e/secrets.py", "parent-reference"), ("..%2Fsecrets.py", "parent-reference"),
    ("docs%2F..%2F..%2Fsecrets.py", "parent-reference"), ("%2Fetc%2Fpasswd", "leading-slash"),
    ("docs%5Carchitecture.md", "backslash"), ("docs/%60x%60.md", "backtick"),
    ("docs/a%0Ab.md", "control-char"), ("docs/a%00b.md", "control-char"), ("docs/a%7Fb.md", "control-char"),
    ("%2e", "empty"), ("https%3A%2F%2Fevil.invalid%2Fx", "scheme"), ("C%3A%2Fx.md", "drive-letter"),
    ("docs/%C0%AE%C0%AE/x.md", "encoding"), ("docs/%FF.md", "encoding"), ("docs/%E2%82.md", "encoding"),
]


@pytest.mark.parametrize("uri,failed", DECODED_VIOLATIONS, ids=["%s:%s" % (failed, uri) for uri, failed in DECODED_VIOLATIONS])
def test_a_uri_that_fails_only_once_decoded_is_refused_as_the_primary_and_as_evidence(uri, failed):
    """SA-11: ``%2e%2e`` passed, because the guard read the URI as written. A consumer that decodes reads ``..``.

    ``%C0%AE`` is an overlong ``.`` and ``%E2%82`` a cut-off character: the decode is strict, so a lenient decoder's
    U+FFFD (or a legacy one's ``.``) is never what the guard reads.
    """
    assert tachi_parts.path_problem(uri) is None, "the written form passes the rule, so only the decode can refuse it"
    assert uri_problems(uri) == [primary_problem(uri, failed)]
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_at("src/auth/login.py"), evidence_at(uri)])
    named = [p for p in problems_of(results, assignments, tool=CONTROLS) if "relatedLocations uri" in p]
    assert named == ["S-1: a relatedLocations uri %s fails the resolver's %s check" % (sc._short(uri), failed)]


EMITTER_URIS = [  # what ``percent_encode`` writes component by component: escapes, a colon, and a "%" that decoding must not read twice
    "docs/security/architecture.md", "docs/My%20Design/architecture.md", "docs/%C3%A9tude/arch%231%2B%25.md",
    "%E6%97%A5%E6%9C%AC/%E6%96%87.md", ".hidden/~x_y-z.md",
    "a%3Ab/architecture.md", "docs/a%3Ab/architecture.md", "C%3A/architecture.md", "%3A",
    "%252e%252e/architecture.md", "docs/%2520%252F.md",
]


@pytest.mark.parametrize("uri", EMITTER_URIS)
def test_a_uri_in_the_form_the_emitter_writes_passes_as_the_runs_one_uri_and_as_evidence(uri):
    for tool in (SCORER, CONTROLS, THREATS):
        check_uri(uri, tool)
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_at(uri)])
    check(results, assignments, tool=CONTROLS)


def test_every_uri_the_resolver_writes_passes_the_guard_as_the_runs_uri_and_as_evidence():
    """The guard may not refuse what the renderers write: each name goes through ``resolve_file``'s own ``percent_encode``."""
    relative = ["docs/security/architecture.md", "docs/My Design/architecture.md", "docs/\u00e9tude/arch#1+%.md", "\u65e5\u672c/\u6587.md",
                "docs/a:b/architecture.md", "%2e%2e/architecture.md", "%252e/%2F.md", "100%/a b.md", ".hidden/~x_y-z.md"]
    colon_first = ["a:b/architecture.md", "C:/architecture.md", ":/architecture.md"]
    fs = FakeFilesystem("/repo")
    for name in relative + colon_first:
        fs.file("/repo/" + name)
    for name in colon_first:
        assert refusal(name, fs) in ("scheme", "drive-letter"), "typed relative, a colon in the first segment is refused"
    for name in relative + colon_first:
        # An absolute path through the working directory is the one way in for a colon in the first segment.
        absolute = sc.resolve_file("/repo/" + name, root="/repo", allow_absolute=True, fs=fs)
        assert absolute.path == name
        for tool in (SCORER, CONTROLS, THREATS):
            check_uri(absolute.uri, tool)
    for name in relative:  # evidence is typed relative to the target directory
        results, assignments = build_run(tool=CONTROLS)
        add_related(results[0], [sc.evidence_location(0, "rate-limiting", sc.resolve_file(name, root="/repo", fs=fs), 7)])
        check(results, assignments, tool=CONTROLS)


def test_the_architecture_resolvers_uri_passes_from_each_source_including_a_directory_with_a_colon():
    fs = FakeFilesystem("/repo")
    fs.file("/repo/a:b/architecture.md")
    colon = sc.resolve_architecture("/repo/a:b/architecture.md", root="/repo", fs=fs)
    assert (colon.source, colon.uri, colon.warnings) == ("explicit", "a%3Ab/architecture.md", ())
    literal = sc.resolve_architecture(root="/repo", fs=fs)
    assert (literal.source, literal.uri) == ("default-literal", sc.DEFAULT_ARCHITECTURE_PATH)
    fs.file("/repo/docs/security/architecture.md")
    default = sc.resolve_architecture(root="/repo", fs=fs)
    assert (default.source, default.uri) == ("default", sc.DEFAULT_ARCHITECTURE_PATH)
    for resolution in (colon, literal, default):
        for tool in (SCORER, CONTROLS, THREATS):
            check_uri(resolution.uri, tool)


def test_the_primary_uri_guard_has_no_rule_of_its_own_it_calls_the_resolvers(monkeypatch):
    """The same swap as the evidence guard's: the rule is called, never restated."""
    uri = "https://evil.invalid/x"
    results, assignments = run_at(uri)
    run = dict(tool=SCORER, member_ids=MEMBERS, assignments=assignments, resolved_ids=["R-9"], uri=uri)
    monkeypatch.setattr(tachi_parts, "path_problem", lambda value, allow_absolute=False: None)
    sc.self_check(results, **run)  # a rule that passes everything passes a scheme too
    monkeypatch.setattr(tachi_parts, "path_problem", lambda value, allow_absolute=False: "a-check-from-tachi-parts")
    with pytest.raises(sc.SelfCheckError) as excinfo:
        sc.self_check(results, **run)
    assert excinfo.value.problems == [primary_problem(uri, "a-check-from-tachi-parts")]


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


# --- PM W3 ruling 2, gap C: the driver's optional ``version`` ----------------------------------------------------------


def test_a_driver_given_a_version_writes_it_right_after_the_name_and_one_without_is_unchanged():
    """The two PR 1 renderers pass ``tachi_parts.VERSION``, which ``semanticVersion`` holds too; ``threats.sarif`` passes none."""
    release = tachi_parts.VERSION
    for sarif_file, name in sc.TOOL_NAMES.items():
        driver = sc.build_driver(sarif_file, semantic_version=release, rules=[], version=release)
        assert list(driver) == ["name", "version", "semanticVersion", "informationUri", "rules"], sarif_file
        assert driver["name"] == name and driver["version"] == driver["semanticVersion"] == release
        bare = sc.build_driver(sarif_file, semantic_version=release, rules=[])
        assert list(bare) == ["name", "semanticVersion", "informationUri", "rules"] and "version" not in bare
        assert sc.build_driver(sarif_file, semantic_version=release, rules=[], version=None) == bare
    full = sc.build_driver(
        "risk-scores.sarif", semantic_version=release, rules=[], supported=sc.supported_taxonomies(), version=release)
    assert list(full) == ["name", "version", "semanticVersion", "informationUri", "supportedTaxonomies", "rules"]


@pytest.mark.parametrize("bad", ["", 0, False, 4, ["4.48.4"], b"4.48.4"], ids=repr)
def test_a_version_that_is_not_a_non_empty_string_is_refused(bad):
    with pytest.raises(ValueError):
        sc.build_driver("risk-scores.sarif", semantic_version="4.48.4", rules=[], version=bad)


def test_a_driver_with_a_version_passes_the_document_builder_and_keeps_its_key_order_in_the_json():
    driver = sc.build_driver(
        "compensating-controls.sarif", semantic_version=tachi_parts.VERSION, rules=[], supported=sc.supported_taxonomies(),
        version=tachi_parts.VERSION)
    written = json.loads(sc.to_json(sc.build_document(driver, sc.TAXONOMIES, [], stamp())))["runs"][0]["tool"]["driver"]
    assert list(written) == list(driver) and list(written)[:3] == ["name", "version", "semanticVersion"]


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
    assert standard <= {"decimal", "hashlib", "json", "os", "posixpath", "re", "stat", "sys", "typing", "pathlib", "urllib"}, standard  # urllib.parse: SA-11's decode


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
    assert not hasattr(sc, "PREFIX_TO_RULE"), "the short-form rule map went with its last user (S1P-A84)"
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
# 16. risk-scores.sarif and compensating-controls.sarif through their renderers: FR-E.2's two-run model
#     (T049 for the scorer's file, red until T050; T052 for the controls file, red until T035 and T053)
# =============================================================================
#
# Section 13 builds runs with the emitter and checks the model on them. The cases below drive the entries,
# ``render-risk-scores.py`` and ``render-compensating-controls.py``, in-process through ``main(argv)`` (ADR-050 D16,
# H15), on the project harness of ``test_render_risk_scores.py`` (T027), so what they read is the file an adopter
# uploads. A case that holds for both files takes ``sarif_file`` and runs once for each; Section 19 holds the cases
# that are the controls file's own. The scorer's cases need its renderer (T028, T045, T046 and T050), and the controls
# cases need T035 and T053; each fails with the absence of its renderer until it exists. The peer and baseline-aware
# cases also need T044's routing, T048's parser and T042's reader. The matching key is the tool, the upload category,
# the rule, the line hash and the URI (ADR-050 D7); nothing else is identity.
#
# The controls stage reads the scorer's ``risk-scores.md`` and, through its ``source_file``, ``threats.md``. So a
# controls project renders the scorer first, and then drives the stage the way ``/tachi.compensating-controls`` does:
# ``tachi-stage.py plan``, one valid part per batch, ``reconcile`` and the renderer. What the agent writes is
# ``controls_item``, which is a function of the finding's ID alone, so a finding that the agent assesses in two runs
# gets the same judgment in both.

SCORER_FILE, CONTROLS_FILE = "risk-scores.sarif", "compensating-controls.sarif"
SCORER_CATEGORY = "risk-score"  # the upload category of risk-scores.sarif: tachi recommends it and never writes it
CONTROLS_CATEGORY = "compensating-controls"  # the upload category of compensating-controls.sarif: the same rule
TOOL_OF = {SCORER_FILE: SCORER, CONTROLS_FILE: CONTROLS}
CATEGORY_OF_TOOL = {SCORER: SCORER_CATEGORY, CONTROLS: CONTROLS_CATEGORY}
# The exit codes of a run over the clean synthetic project. The scorer's are asserted exactly, as T049 does. A controls
# run may be 5 here, so that a warning the harness doesn't foresee can't hide every identity case behind it:
# ``test_a_clean_controls_run_exits_0_with_no_warning`` asserts the clean run exactly, in one place.
RUN_CODES = {SCORER_FILE: (0,), CONTROLS_FILE: (0, 5)}
BOTH_FILES = pytest.mark.parametrize("sarif_file", [SCORER_FILE, CONTROLS_FILE], ids=["risk-scores", "compensating-controls"])
FIRST_RUN_GROUPS = [("CG-1", ["S-2", "S-10", "T-1"]), ("CG-2", ["E-3", "E-5"])]
SECOND_RUN_GROUPS = [("CG-1", ["T-1", "S-2"]), ("CG-3", ["S-10", "E-3", "AG-1"])]  # a new primary, a dissolved group, a new one
PLANTED_HASHES = ["%016x:1" % n for n in range(1, 41)]  # what an upstream file or an older run could carry: never copied


@pytest.fixture(scope="module")
def rrs():
    """The renderer goldens' project harness, imported when a case first needs it, so Sections 1 to 15 never depend on it."""
    from . import test_render_risk_scores
    return test_render_risk_scores


CONTROLS_STAGE = "compensating-controls"
CONTROLS_MD = "compensating-controls.md"
CONTROLS_RENDERER = SCRIPTS_DIR / "render-compensating-controls.py"


class Entries(tuple):
    """``(tachi-stage.py, render-risk-scores.py)`` as loaded modules, and ``.controls``: ``render-compensating-controls.py``.

    The controls renderer is loaded when a case first asks for it, so the scorer's cases never depend on it.
    """

    _controls = None

    @property
    def controls(self):
        if self._controls is None:
            if not CONTROLS_RENDERER.is_file():
                pytest.fail("scripts/render-compensating-controls.py does not exist yet: T035 and T053 write it to these cases (TDD)",
                            pytrace=False)
            self._controls = _load_hyphenated_script("render_controls_for_identity_cases", "render-compensating-controls.py")
        return self._controls


@pytest.fixture(scope="module")
def entries(rrs):
    """``(tachi-stage.py, render-risk-scores.py)`` as loaded modules, and ``.controls`` for the controls renderer."""
    if not rrs.RENDERER.is_file():
        pytest.fail("scripts/render-risk-scores.py does not exist yet: T028 and T050 write it to these cases (TDD)", pytrace=False)
    return Entries((_load_hyphenated_script("tachi_stage_for_identity_cases", "tachi-stage.py"),
                    _load_hyphenated_script("render_risk_scores_for_identity_cases", "render-risk-scores.py")))


def scorer_project(rrs, entries, root, **kwargs):
    return rrs.Project(entries[0], entries[1], root, **kwargs)


# --- the controls stage: the agent's part, and a project that drives the stage the way the command does ---------------

EVIDENCE_NUMBERS = (1, 2, 3)  # the modules that the synthetic codebase holds for each control category
DEFAULT_LAYER = "L4 \u2014 Deployment Infrastructure"  # a MAESTRO layer for a component that a project's table doesn't list
STATUS_DISPLAY = {"found": "Control Found", "partial": "Partial Control", "missing": "No Control Found"}
SAME = object()  # ``ControlsProject.run(controls_baseline=SAME)``: the controls stage takes the baseline that the scorer takes


def evidence_path(category, number):
    """A file of the synthetic codebase, relative to its root (``ControlsProject.target``)."""
    return "src/%s/module%d.py" % (category.replace("-", "_"), number)


def matrix_row(finding_id, component, layer, status, category):
    """One Section 2 row in K8's column order, as the agent writes it (ADR-050 D2, R-34): 11 cells.

    The order is the agent spec's, ``test_tachi_parsers.py``'s ``_K8_HEADER``. The cells that D2 gives the renderer are
    slots, and ``CF`` is not set (this agent re-assesses). ``Threat`` is model text that only NFR-10 reads.
    """
    cells = [finding_id, "\u2014", component, layer, "A synthetic threat to the component.", "{{score:inherent}}", "{{band:inherent}}",
             STATUS_DISPLAY[status], category.replace("-", " ").title(), "{{score:residual}}", "{{band:residual}}"]
    return "| " + " | ".join(cells) + " |"


def recommendation_body(component, category):
    """A Section 4 body (ADR-050 D2, R-34): the four keys, once each and in order, and Effort in its enum."""
    return ("**What to Implement**: Add a %s check in front of every handler of %s.\n\n"
            "**Where to Implement**: src/%s/module1.py\n\n"
            "**Reference Patterns**: One shared middleware that every route passes through.\n\n"
            "**Effort Estimate**: Medium \u2014 one new module.") % (category.replace("-", " "), component, category.replace("-", "_"))


def controls_item(finding_id, component, layer, variant=0):
    """One valid ``compensating-controls`` item (``contracts/part-files.md``) for a synthetic finding.

    Every value is a function of the canonical ID, so the agent gives a finding the same judgment in every run, and a
    batch holds all three control statuses. ``variant`` re-assesses the finding: the status and the category move, and
    with them the evidence, the level and the message, so a case can show that none of it is identity. Evidence is
    files of the synthetic codebase, from at most three distinct modules.
    """
    canonical = tachi_parts.canonical_finding_id(finding_id)
    seed = sum(ord(char) for char in canonical)
    status = ("found", "partial", "missing")[(seed + variant) % 3]
    category = tachi_parts.CONTROL_CATEGORIES[(seed + variant) % len(tachi_parts.CONTROL_CATEGORIES)]
    evidence = []
    if status != "missing":
        for step in range(1 + seed % 3):
            evidence.append({
                "file": evidence_path(category, EVIDENCE_NUMBERS[(seed + step) % len(EVIDENCE_NUMBERS)]),
                "line": 4 + (seed * (step + 2)) % 27, "language": "python",
                "snippet": "def check(request):\n    return verify(request.token)",
                "summary": "The handler verifies the caller before it runs."})
    return {
        "finding_id": canonical, "control_status": status, "control_category": category,
        "confidence": None if status == "missing" else ("High", "Medium", "Low")[seed % 3],
        "carried_forward": False, "evidence": evidence,
        "matrix_row": matrix_row(canonical, component, layer, status, category),
        "recommendation_body": None if status == "found" else recommendation_body(component, category),
    }


class ControlsProject(object):
    """The controls stage over one synthetic project (ADR-050 D2, D4, D6, D7 and D8; T052).

    Its input is the scorer's ``risk-scores.md``, so ``run`` renders the scorer first, on the scorer's own project
    (``test_render_risk_scores.Project``), and then drives the stage as the command does, all in-process through
    ``main(argv)`` (H15): ``tachi-stage.py plan`` with the pointers that ``contracts/cli.md`` lists, one valid part per
    batch, ``reconcile``, and ``render-compensating-controls.py --out DIR PLAN``. It answers what the scorer's project
    answers (``root``, ``out``, ``specs``, ``md``, ``sarif``, ``record``, ``run``), so one case can drive either.

    The scanned codebase is ``app/``. It holds every file that ``controls_item`` can cite, made when the project is, so
    a case that mirrors the project into a fake volume mirrors the evidence too. ``variant`` re-assesses every finding.
    ``items`` holds the item that the agent last wrote for each finding, before ``mutate`` touched the part.
    """

    stage_files = (CONTROLS_MD, CONTROLS_FILE)  # what a later run's ``--baseline`` directory holds, beside the scorer's files

    def __init__(self, rrs, entries, scorer, renderer=None):
        self.rrs, self.stage, self.renderer, self.scorer = rrs, entries[0], renderer, scorer
        self.root, self.out, self.architecture = scorer.root, scorer.out, scorer.architecture
        self.target = self.root / "app"
        for category in tachi_parts.CONTROL_CATEGORIES:
            for number in EVIDENCE_NUMBERS:
                path = self.target / evidence_path(category, number)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# synthetic module %d of the %s controls\n" % (number, category), encoding="utf-8")
        self.plan_id = self.digest = self.last = None
        self.variant = 0
        self.items = {}

    # ---- what the scorer's project holds, shared
    specs = property(lambda self: self.scorer.specs, lambda self, value: setattr(self.scorer, "specs", value))
    resolved = property(lambda self: self.scorer.resolved, lambda self, value: setattr(self.scorer, "resolved", value))
    threats = property(lambda self: self.scorer.threats)

    # ---- layout
    def read_json(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @property
    def plan_dir(self):
        return Path(tachi_parts.plan_dir(self.out, CONTROLS_STAGE, self.plan_id))

    def batches(self):
        return {entry["batch_id"]: entry for entry in self.read_json(self.plan_dir / "plan.json")["batches"]}

    def batch_input(self, batch_id):
        return self.read_json(tachi_parts.input_path(self.out, CONTROLS_STAGE, self.plan_id, batch_id))

    # ---- the stages
    def score(self, date=None, architecture=True, baseline_dir=None):
        """Render the scorer's files, which are this stage's input."""
        res = self.scorer.run(None, date or self.rrs.DATE, None, architecture, baseline_dir)
        assert res.code in (0, 5), "the scorer's render, which is the input of the controls stage:\n" + res.describe()
        return res

    def plan(self, date=None, architecture=True, baseline_dir=None):
        """``tachi-stage.py plan``, as the command calls it. ``architecture`` and ``baseline_dir`` are the scorer harness's.

        The call passes no ``--threats``: the controls planner reaches ``threats.md`` through ``risk-scores.md``'s ``source_file`` (T036).
        """
        argv = ["plan", "--stage", CONTROLS_STAGE, "--out", self.out, "--date", date or self.rrs.DATE,
                "--risk-scores", self.out / self.rrs.MD, "--target", self.target]
        explicit = self.architecture if architecture is True else (architecture or None)
        if explicit is not None:
            argv += ["--architecture", explicit]
        if baseline_dir is not None:
            argv += ["--baseline-dir", baseline_dir]
        res = self.rrs.invoke(self.stage, argv, self.root)
        assert res.code == 0, "tachi-stage.py plan:\n" + res.describe()
        printed = json.loads(res.out)
        self.plan_id, self.digest = printed["plan_id"], printed["plan_digest"]
        return printed

    def write_parts(self, mutate=None):
        """One valid part for each batch that is to be dispatched: ``controls_item`` for each of its findings."""
        text = self.threats.read_text(encoding="utf-8")
        rows = {tachi_parts.canonical_finding_id(row["id"]): row for row in tachi_parsers.parse_reference_set(text)["open"]}
        layers = {row["Component"]: row["MAESTRO Layer"] for row in tachi_parsers.parse_markdown_table(text, "### Components")}
        for batch_id, entry in self.batches().items():
            if entry["state"] == "split":
                continue
            bi = self.batch_input(batch_id)
            items = []
            for finding_id in bi["finding_ids"]:
                component = rows[finding_id]["component"]
                item = controls_item(finding_id, component, layers.get(component, DEFAULT_LAYER), self.variant)
                self.items[finding_id] = copy.deepcopy(item)
                items.append(item)
            part = {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": bi["stage"],
                    "agent_type": bi["agent_type"], "finding_ids": list(bi["finding_ids"]), "items": items, "fragments": []}
            if mutate is not None:
                mutate(part)
            path = Path(bi["part_path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(part), encoding="utf-8")

    def reconcile(self):
        res = self.rrs.invoke(self.stage, ["reconcile", "--stage", CONTROLS_STAGE, "--out", self.out, "--plan", self.plan_id,
                                           "--plan-digest", self.digest], self.root)
        if res.code in (0, 3, 4):
            self.digest = json.loads(res.out)["plan_digest"]
        return res

    def prepare(self, date=None, mutate=None, architecture=True, baseline_dir=None):
        """Plan, write a valid part for every batch and reconcile to complete (the command's loop)."""
        self.plan(date, architecture, baseline_dir)
        self.write_parts(mutate)
        res = self.reconcile()
        assert res.code == 0, res.describe()

    def render(self, *extra):
        assert self.renderer is not None, "this controls project was built without the renderer"
        self.last = self.rrs.invoke(
            self.renderer, ["--out", self.out, "--plan", self.plan_id, "--plan-digest", self.digest] + list(extra), self.root)
        return self.last

    def run(self, date=None, mutate=None, architecture=True, baseline_dir=None, controls_baseline=SAME, score=True):
        """The scorer (unless ``score`` is false), then the controls stage, which is baseline-aware when ``baseline_dir`` is.

        ``controls_baseline`` is the controls stage's own ``--baseline``: ``SAME``, a directory, or ``None`` for none.
        """
        assert self.renderer is not None, "this controls project was built without the renderer"
        if score:
            self.score(date, architecture, baseline_dir)
        self.prepare(date, mutate, architecture, baseline_dir if controls_baseline is SAME else controls_baseline)
        return self.render()

    # ---- what the render wrote
    @property
    def md(self):
        return (self.out / CONTROLS_MD).read_text(encoding="utf-8")

    @property
    def sarif_text(self):
        return (self.out / CONTROLS_FILE).read_text(encoding="utf-8")

    @property
    def sarif(self):
        return json.loads(self.sarif_text)

    @property
    def scorer_sarif(self):
        return self.scorer.sarif

    @property
    def record(self):
        return self.read_json(tachi_parts.stage_record_path(self.out, CONTROLS_STAGE, self.plan_id))


def make_project(sarif_file, rrs, entries, root, **kwargs):
    """The project that renders ``sarif_file``: the scorer's own, or the controls stage over a scorer project."""
    scorer = scorer_project(rrs, entries, root, **kwargs)
    return scorer if sarif_file == SCORER_FILE else ControlsProject(rrs, entries, scorer, renderer=entries.controls)


def make_subset(sarif_file, rrs, entries, root):
    """``rrs.subset_project``'s 42 open findings, for the scorer or for the controls stage. Returns ``(project, reference)``."""
    scorer, reference = rrs.subset_project(entries[0], entries[1], root)
    return (scorer if sarif_file == SCORER_FILE else ControlsProject(rrs, entries, scorer, renderer=entries.controls)), reference


def alert_keys(document):
    """GitHub's matching key of each result in a scorer or controls document, by the finding's ``findingId/v1``.

    The upload category is the file's own (ADR-050 D7): the document names its tool, and the tool names its category.
    """
    run = document["runs"][0]
    tool = run["tool"]["driver"]["name"]
    return {finding_id: (tool, CATEGORY_OF_TOOL[tool]) + key for finding_id, key in keys_of(run["results"]).items()}


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


def expected_sentence(assignment):
    """Ruling C's sentence for a finding's assignment, or ``None`` when the finding isn't correlated."""
    if assignment is None:
        return None
    peers = list(assignment.peers) if assignment.role == "primary" else None
    return ruling_c(assignment.group, assignment.primary, peers)


def expected_text(threat, assignment):
    """The scorer's ``message.text``: the reference set's threat text, then the sentence after one space."""
    sentence = expected_sentence(assignment)
    return threat if sentence is None else threat + " " + sentence


def message_parts(text):
    """``(the file's own text, ruling C's sentence or None)``: the sentence is appended after one space (``contracts/sarif-result.md``)."""
    own, found, tail = text.rpartition(" Correlated in CG-")
    return (own, "Correlated in CG-" + tail) if found else (text, None)


def snapshot_run(rrs, project, name="baseline-1"):
    """Copy a finished run's input and outputs under their canonical names: what a later run's ``--baseline`` names.

    A controls project's baseline holds the controls files too.
    """
    target = project.root / name
    target.mkdir()
    for source in ("threats.md", rrs.MD, rrs.SARIF) + tuple(getattr(project, "stage_files", ())):
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


def planted_sarif(ids, offset=0, tool=SCORER):
    """A SARIF file as an older tachi would write it: a ``findingId/v1`` and a hash of its own on every result."""
    results = [{"ruleId": "tachi/stride/spoofing", "message": {"text": "x"}, "level": "error",
                "partialFingerprints": {"primaryLocationLineHash": PLANTED_HASHES[offset + n], "findingId/v1": finding_id},
                "properties": {"security-severity": "5.0"}} for n, finding_id in enumerate(ids)]
    return json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": tool}}, "results": results}]}, indent=2) + "\n"


def run_pair(rrs, entries, root, baseline_aware, plant=False, replace_baseline_sarif=False, sarif_file=SCORER_FILE):
    """Render run 1, then run 2 (regrouped, with one more finding), in one project.

    Run 2 is baseline-aware when asked: run 1's files become its ``--baseline``, and its carried findings are
    UNCHANGED. ``plant`` puts an upstream ``threats.sarif`` with hashes of its own beside run 1's input, and
    ``replace_baseline_sarif`` swaps each SARIF in the baseline for one that lists other findings under other hashes.

    ``sarif_file`` names the file that ``first`` and ``second`` hold. For the controls file each run renders the scorer
    first, and the controls stage is baseline-aware exactly when the scorer is: run 1's directory holds both stages'
    files. ``upstream_1`` and ``upstream_2`` are then the scorer's SARIF of each run, which is this stage's input.
    """
    project = make_project(sarif_file, rrs, entries, root, groups=FIRST_RUN_GROUPS)
    ids_1 = [item["id"] for item in rrs.SPECS]
    if plant:
        (project.out / "threats.sarif").write_text(planted_sarif(ids_1), encoding="utf-8")
    first = project.run()
    assert first.code in RUN_CODES[sarif_file], first.describe()
    pair = SimpleNamespace(project=project, ids_1=ids_1, specs_1=list(rrs.SPECS), baseline=None,
                           first=project.sarif, first_text=project.sarif_text, first_md=project.md,
                           upstream_1=getattr(project, "scorer_sarif", None))
    if baseline_aware:
        pair.baseline = snapshot_run(rrs, project)
        if replace_baseline_sarif:
            for name, tool in ((rrs.SARIF, SCORER), (CONTROLS_FILE, CONTROLS)):
                if (pair.baseline / name).exists():
                    (pair.baseline / name).write_text(planted_sarif(ids_1 + ["S-99"], offset=20, tool=tool), encoding="utf-8")
    pair.specs_2 = second_run_specs(rrs, baseline_aware)
    pair.ids_2 = [item["id"] for item in pair.specs_2]
    rewrite_inputs(rrs, project, pair.specs_2, SECOND_RUN_GROUPS)
    second = project.run(baseline_dir=pair.baseline)
    assert second.code in (0, 5), second.describe()
    pair.second, pair.second_text, pair.second_md = project.sarif, project.sarif_text, project.md
    pair.upstream_2 = getattr(project, "scorer_sarif", None)
    return pair


BOTH_MODES = pytest.mark.parametrize("baseline_aware", [False, True], ids=["stateless", "baseline-aware"])


@BOTH_FILES
@BOTH_MODES
def test_the_regroup_pair_keeps_every_carried_key_and_changes_only_the_text(rrs, entries, tmp_path, sarif_file, baseline_aware):
    """US-6a #1: run 2 regroups carried findings, changes a primary and dissolves a group, and no key moves, in each file."""
    pair = run_pair(rrs, entries, tmp_path, baseline_aware, sarif_file=sarif_file)
    keys_1, keys_2 = alert_keys(pair.first), alert_keys(pair.second)
    assert sorted(keys_1) == sorted(pair.ids_1) and sorted(keys_2) == sorted(pair.ids_2), "no finding drops out"
    for finding_id in pair.ids_1:
        assert keys_2[finding_id] == keys_1[finding_id], "%s: a regroup never moves a key" % finding_id
    assert "T-7" in keys_2 and "T-7" not in keys_1, "the finding only run 2 has gets a key of its own"
    for keys in (keys_1, keys_2):
        assert len(set(keys.values())) == len(keys), "no two present results share a key (the F-012 lesson)"
    texts, owns = {}, {}
    for run, document, specs, groups, ids in ((1, pair.first, pair.specs_1, FIRST_RUN_GROUPS, pair.ids_1),
                                              (2, pair.second, pair.specs_2, SECOND_RUN_GROUPS, pair.ids_2)):
        assignments = sc.correlation_assignments(groups, ids)
        sc.self_check(document["runs"][0]["results"], tool=TOOL_OF[sarif_file], member_ids=ids, assignments=assignments,
                      resolved_ids=rrs.RESOLVED_IDS, uri=URI)
        by_id = results_by(document)
        for item in specs:
            text = by_id[item["id"]]["message"]["text"]
            assignment = assignments.get(tachi_parts.canonical_finding_id(item["id"]))
            own, sentence = message_parts(text)
            assert sentence == expected_sentence(assignment), (run, item["id"])
            assert own, "the file's own text is never empty"
            if sarif_file == SCORER_FILE:
                assert text == expected_text(item["threat"], assignment), (run, item["id"])
            texts[(run, item["id"])], owns[(run, item["id"])] = text, own
    for finding_id in ("T-1", "E-5", "AG-1"):
        assert texts[(1, finding_id)] != texts[(2, finding_id)], "%s: a regroup changes its text (ruling C)" % finding_id
        assert owns[(1, finding_id)] == owns[(2, finding_id)], "%s: and only the sentence, never the file's own text" % finding_id


@BOTH_FILES
@BOTH_MODES
def test_an_unchanged_rerun_of_the_renderer_keeps_its_keys_and_its_bytes(rrs, entries, tmp_path, sarif_file, baseline_aware):
    """US-6a #2: the same inputs under a fresh plan give the same keys, and the same bytes, in both files."""
    pair = run_pair(rrs, entries, tmp_path, baseline_aware, sarif_file=sarif_file)
    again = pair.project.run(baseline_dir=pair.baseline)
    assert again.code in (0, 5), again.describe()
    assert pair.project.sarif_text == pair.second_text and pair.project.md == pair.second_md
    assert alert_keys(pair.project.sarif) == alert_keys(pair.second)


@BOTH_FILES
@BOTH_MODES
def test_the_hash_recomputes_from_the_tool_and_the_id_and_no_upstream_hash_is_copied(rrs, entries, tmp_path, sarif_file, baseline_aware):
    """S-6, FR-E.12: the hash is tachi's own, in each file. The controls file's upstream is the scorer's file, whose hashes
    are real and differ by the tool term: the legacy analyzer copied them (``control-analyzer.md`` Phase 6c), and no result may now."""
    pair = run_pair(rrs, entries, tmp_path, baseline_aware, plant=True, replace_baseline_sarif=baseline_aware, sarif_file=sarif_file)
    tool = TOOL_OF[sarif_file]
    for document, text, upstream in ((pair.first, pair.first_text, pair.upstream_1), (pair.second, pair.second_text, pair.upstream_2)):
        for result in document["runs"][0]["results"]:
            written = result["partialFingerprints"]["findingId/v1"]
            assert result["partialFingerprints"]["primaryLocationLineHash"] == recipe(tool, tachi_parts.canonical_finding_id(written)), written
        assert not [planted for planted in PLANTED_HASHES if planted in text], "an upstream or earlier hash was copied (S-6)"
        assert "automationDetails" not in text and "runAutomationDetails" not in text, "the upload step's category governs (D7)"
        if upstream is not None:
            copied = [r["partialFingerprints"]["primaryLocationLineHash"] for r in upstream["runs"][0]["results"]
                      if r["partialFingerprints"]["primaryLocationLineHash"] in text]
            assert not copied, "the scorer file's hashes were copied into the controls file: %s" % copied
    assert results_by(pair.first)["AGP-01"]["partialFingerprints"]["primaryLocationLineHash"] == recipe(tool, "AGP-1"), \
        "the hash is over the canonical ID, and findingId/v1 keeps Section 7's spelling"


@BOTH_FILES
def test_no_stage_reads_a_baseline_sarifs_membership_or_hashes(rrs, entries, tmp_path, sarif_file):
    """ADR-050 D8: SV-3's trigger does not fire, because no stage reads a baseline SARIF's membership or hashes."""
    pair = run_pair(rrs, entries, tmp_path, True, replace_baseline_sarif=True, sarif_file=sarif_file)
    assert sorted(alert_keys(pair.second)) == sorted(pair.ids_2), "the member set is Section 7's"
    assert "S-99" not in pair.second_text
    keys_1, keys_2 = alert_keys(pair.first), alert_keys(pair.second)
    assert all(keys_2[finding_id] == keys_1[finding_id] for finding_id in pair.ids_1)


@BOTH_FILES
def test_no_two_present_results_share_a_key_in_a_run_of_forty_two_findings(rrs, entries, tmp_path, sarif_file):
    project, reference = make_subset(sarif_file, rrs, entries, tmp_path)
    res = project.run()
    assert res.code in (0, 5), res.describe()  # the subset's Affected Assets block is stale, so the scorer may warn
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


@BOTH_FILES
@pytest.mark.parametrize("flag,body,snapshot,uri,warning_codes", [case[1:] for case in URI_CASES], ids=[case[0] for case in URI_CASES])
def test_the_flag_then_the_body_line_then_the_default_and_each_failed_carrier_warns(
        rrs, entries, tmp_path, outside_file, sarif_file, flag, body, snapshot, uri, warning_codes):
    """FR-E.18, US-6a #7 to #9, in each file. The controls renderer reaches the body line through ``source_file``."""
    project = make_project(sarif_file, rrs, entries, tmp_path, body_line=body)
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
    sc.self_check(results, tool=TOOL_OF[sarif_file], member_ids=[item["id"] for item in rrs.SPECS], assignments={},
                  resolved_ids=rrs.RESOLVED_IDS, uri=uri)


@BOTH_FILES
def test_a_run_always_gets_a_uri_even_when_nothing_validates(rrs, entries, tmp_path, outside_file, sarif_file):
    project = make_project(sarif_file, rrs, entries, tmp_path)
    project.architecture.unlink()
    res = project.run(architecture=str(outside_file))
    assert res.code == 5, res.describe()
    chain = ["architecture-path:explicit:outside-root", "architecture-path:body-line:absent", "architecture-path:default:missing"]
    if sarif_file == SCORER_FILE:
        assert [w["code"] for w in project.record["warnings"]] == chain + ["tag-source:no-architecture-file"], (
            "D7's chain in order, then the tag source: with no architecture file the block's tags are applied unverified, and "
            "that warns, because the stage record has no other trace of it (ruled at W2, ADR-050 D2)")
        assert "unverified" in project.record["warnings"][-1]["detail"]
    else:  # the controls stage elevates nothing (its inherent score is the scorer's), so the tag source is not its concern
        assert [w["code"] for w in project.record["warnings"]] == chain, "D7's chain in order, and nothing else"
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {sc.DEFAULT_ARCHITECTURE_PATH}, "the constant is emitted as written, and nothing here stops a run"


@BOTH_FILES
def test_a_directory_named_with_a_colon_is_written_encoded_and_the_renderers_self_check_accepts_it(rrs, entries, tmp_path, sarif_file):
    """SA-11's decoding: ``a%3Ab`` decodes to a first segment that holds a colon, and the guard must not take it for a scheme.

    Typed relative, ``a:b/architecture.md`` fails the resolver as a scheme. Typed as an absolute path through the
    working directory, it resolves, and RFC 3986 section 4.2 has the colon written encoded. Each renderer's own
    self-check runs on the result, so a guard that refused it would fail the render here.
    """
    project = make_project(sarif_file, rrs, entries, tmp_path)
    architecture = project.root / "a:b" / "architecture.md"
    try:
        architecture.parent.mkdir()
        architecture.write_text("# an architecture file in a directory whose name holds a colon\n", encoding="utf-8")
    except OSError:  # pragma: no cover  (a filesystem that cannot name a directory with a colon)
        pytest.skip("this filesystem cannot name a directory with a colon")
    res = project.run(architecture=str(architecture))
    assert res.code == 0, res.describe()
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {"a%3Ab/architecture.md"}
    assert project.record["warnings"] == []


def mirror(fake, root):
    """Copy the layout of a real project (its directories and regular files) into the fake filesystem."""
    for path in sorted(Path(root).rglob("*")):
        if path.relative_to(root).parts[0] == ".tachi-build":
            continue
        if path.is_dir():
            fake.mkdir(str(path))
        elif path.is_file():
            fake.file(str(path))


@BOTH_FILES
@pytest.mark.parametrize("body", ["docs/other/architecture.md", "DOCS/Other/ARCHITECTURE.md"], ids=["canonical", "case-variant"])
def test_a_case_variant_body_line_gives_every_result_the_same_uri_on_a_case_insensitive_volume(
        rrs, entries, tmp_path, monkeypatch, sarif_file, body):
    """KB 24 and FR-E.2: the resolver, not the renderer, spells the path, so a case variant gives one URI.

    The renderer reaches the filesystem through ``sarif_common.OS_FILESYSTEM`` for this, so a fake case-insensitive
    volume stands in for the one an adopter's laptop has. A controls run renders the scorer first, on the real volume,
    so that the mirror holds every file the controls stage reads.
    """
    project = make_project(sarif_file, rrs, entries, tmp_path, body_line=body)
    add_architecture_files(project)
    (project.out / "architecture.md").write_text("# the snapshot\n", encoding="utf-8")
    options = {"architecture": False}
    if sarif_file == CONTROLS_FILE:
        project.score(architecture=False)
        options["score"] = False
    fake = FakeFilesystem(str(tmp_path), case_insensitive=True)
    mirror(fake, tmp_path)
    monkeypatch.setattr(sc, "OS_FILESYSTEM", fake)
    res = project.run(**options)
    assert res.code == 0, res.describe()
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {"docs/other/architecture.md"}


# --- ruling C: a primary with more than ten peers; ruling B: reused IDs -----------------------------------------------

@BOTH_FILES
@pytest.mark.parametrize("size,more", [(11, 0), (12, 1), (13, 2)], ids=["ten-peers", "eleven-peers", "twelve-peers"])
def test_a_primary_with_more_than_ten_peers_names_ten_and_then_a_count(rrs, entries, tmp_path, sarif_file, size, more):
    """PM-T7, ruling C: the first ten in group order, joined by a comma and a space, then `` and N more``."""
    specs = [rrs.spec("S-%d" % n, "edge-gateway", "Threat %d on the gateway." % n, "Medium", "NEW",
                      "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0)
             for n in range(1, size + 1)]
    ids = [item["id"] for item in specs]
    project = make_project(sarif_file, rrs, entries, tmp_path, specs=specs, resolved=[], groups=[("CG-1", ids)])
    res = project.run()
    assert res.code in (0, 5), res.describe()
    results = results_by(project.sarif)
    assert len(results) == size, "every peer is a result, once"
    tail = "Correlated in CG-1; peers " + ", ".join(ids[1:11]) + (" and %d more" % more if more else "") + "."
    own, sentence = message_parts(results["S-1"]["message"]["text"])
    assert sentence == tail == ruling_c("CG-1", "S-1", ids[1:])
    if sarif_file == SCORER_FILE:
        assert results["S-1"]["message"]["text"] == "Threat 1 on the gateway. " + tail
    for peer in ids[1:]:
        peer_own, peer_sentence = message_parts(results[peer]["message"]["text"])
        assert peer_sentence == "Correlated in CG-1; primary S-1.", peer
        if sarif_file == SCORER_FILE:
            assert peer_own == "Threat %s on the gateway." % peer[2:], peer
    sc.self_check(project.sarif["runs"][0]["results"], tool=TOOL_OF[sarif_file], member_ids=ids,
                  assignments=sc.correlation_assignments([("CG-1", ids)], ids), resolved_ids=[], uri=URI)


REUSED_ID_FLAG = "reused-id:finding_id:baseline"


def reissue_ids(rrs, project, codes=(0,)):
    """Render run 1, keep it as the baseline, and rewrite the inputs of run 2: two IDs are given to NEW findings (ruling B).

    S-2 was open in the baseline, and S-1 was RESOLVED there. The caller renders run 2. Returns ``(run 1's keys, the baseline)``.
    """
    first = project.run()
    assert first.code in codes, first.describe()
    keys_1 = alert_keys(project.sarif)
    baseline = snapshot_run(rrs, project)
    reissued = [
        rrs.spec("S-2", "auth-broker", "A different threat that was given S-2 after the first one went away.", "Medium", "NEW",
                 "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0),
        rrs.spec("S-1", "edge-gateway", "A new threat that was given S-1, which the baseline lists as RESOLVED.", "Medium", "NEW",
                 "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0)]
    specs_2 = [dict(item, status="UNCHANGED") for item in rrs.SPECS if item["id"] != "S-2"] + reissued
    rewrite_inputs(rrs, project, specs_2, (), resolved=[row for row in rrs.RESOLVED if row[0] != "S-1"])
    return keys_1, baseline


@BOTH_FILES
def test_a_new_finding_that_reuses_a_baseline_id_is_flagged_and_keeps_the_old_key(rrs, entries, tmp_path, sarif_file):
    """Ruling B (D7), PR 1's half: the flag marks the exposure, and the key shows it: the old alert's key is reused.

    US-6a #10: both files flag the finding. The scorer finds the reuse in its baseline, and the controls renderer
    carries the flag from its input ``risk-scores.md`` (the flag's property is ``score-flags`` or ``integrity-flags``).
    """
    project = make_project(sarif_file, rrs, entries, tmp_path)
    keys_1, baseline = reissue_ids(rrs, project, RUN_CODES[sarif_file])
    res = project.run(baseline_dir=baseline)
    assert res.code in (0, 5), res.describe()
    results = results_by(project.sarif)
    flags_property = sc.FLAG_PROPERTIES[sarif_file]
    assert sorted(i for i, r in results.items() if REUSED_ID_FLAG in r["properties"][flags_property]) == ["S-1", "S-2"], \
        "a NEW finding whose ID is in any baseline row, open or RESOLVED, is flagged"
    assert all(r["properties"][flags_property] == sorted(r["properties"][flags_property]) for r in results.values()), \
        "the flags are a sorted array, present on every result"
    assert alert_keys(project.sarif)["S-2"] == keys_1["S-2"], "the reissued ID inherits the old alert: the exposure the flag marks (ruling B)"
    if sarif_file == SCORER_FILE:
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


def test_the_self_check_reads_no_markdown_for_a_resolved_id():
    """The mitigation is copied text: an ID in it is a mention and not a reference (ruled at W3, P0-10; Section 21)."""
    check([make_result("T-2", markdown="This is related to S-9, which was fixed.")], {}, members=["T-2"], resolved=["S-9"])


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


# =============================================================================
# 19. compensating-controls.sarif: the cases that are the controls file's own (T052; red until T035 and T053)
# =============================================================================
#
# Section 16 runs FR-E.2's two-run model on both files. What follows is what only the controls file has: ``relatedLocations``
# that hold code evidence, a flag that the stage carries from its input instead of deriving, and a stage that renders after
# the scorer. A few cases hold for both files and take ``sarif_file``, as Section 16's do. The cases drive the entry
# ``render-compensating-controls.py --out DIR PLAN`` (``contracts/cli.md``) on the project harness of Section 16.
#
# The ``test_harness_*`` cases check that harness and need no controls renderer: they pass now, so the cases after them
# can fail only for the renderer's absence. Where a contract leaves a form open, the case says ``# reading:``, and T035 or
# T053 either meets it or rules on it with the architect.

K8_HEADER = ["Threat ID", "CF", "Component", "MAESTRO Layer", "Threat", "Inherent Score", "Inherent Severity", "Control Status",
             "Control Category", "Residual Score", "Residual Severity"]  # the agent-spec order (test_tachi_parsers.py's _K8_HEADER)
FINDING_TOKEN = re.compile(r"(?<![A-Za-z0-9-])(?:S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}(?![A-Za-z0-9-])")
LAYER = DEFAULT_LAYER


def row_cells(row):
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def controls_with_scorer(rrs, entries, root, **kwargs):
    """A controls project with no renderer, for the harness checks: the scorer's project, and the controls stage over it."""
    return ControlsProject(rrs, entries, scorer_project(rrs, entries, root, **kwargs))


def test_harness_the_matrix_row_has_the_eleven_cells_in_the_k8_order():
    cells = row_cells(matrix_row("S-2", "edge-gateway", LAYER, "partial", "rate-limiting"))
    assert len(cells) == len(K8_HEADER) == 11
    assert dict(zip(K8_HEADER, cells)) == {
        "Threat ID": "S-2", "CF": "\u2014", "Component": "edge-gateway", "MAESTRO Layer": LAYER,
        "Threat": "A synthetic threat to the component.", "Inherent Score": "{{score:inherent}}",
        "Inherent Severity": "{{band:inherent}}", "Control Status": "Partial Control", "Control Category": "Rate Limiting",
        "Residual Score": "{{score:residual}}", "Residual Severity": "{{band:residual}}"}
    assert "|" not in " ".join(cells), "a literal pipe in a cell would shift the columns (D2)"


def test_harness_an_item_is_a_function_of_the_id_and_a_variant_moves_the_judgment_and_nothing_else():
    first = controls_item("AGP-01", "vector-store", LAYER)
    assert first == controls_item("AGP-1", "vector-store", LAYER) and first["finding_id"] == "AGP-1", "the canonical ID, however it is spelled"
    moved = controls_item("AGP-1", "vector-store", LAYER, variant=1)
    assert moved["finding_id"] == "AGP-1" and (moved["control_status"], moved["control_category"]) != (first["control_status"], first["control_category"])
    for item in (first, moved):
        assert (item["control_status"] == "missing") == (item["confidence"] is None) == (item["evidence"] == [])
        assert (item["control_status"] == "found") == (item["recommendation_body"] is None)


def test_harness_every_evidence_file_the_items_can_cite_is_a_regular_file_that_the_resolver_accepts(rrs, entries, tmp_path):
    project = controls_with_scorer(rrs, entries, tmp_path)
    for category in tachi_parts.CONTROL_CATEGORIES:
        for number in EVIDENCE_NUMBERS:
            path = evidence_path(category, number)
            assert sc.resolve_file(path, root=str(project.target)) == (path, path), path


def test_harness_the_controls_items_pass_the_shipped_validator_and_the_stage_reconciles(rrs, entries, tmp_path):
    """The planner and the part validator are the shipped ones: ``prepare`` plans, writes a part per batch and reconciles to complete."""
    project = controls_with_scorer(rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    project.score()
    project.prepare()
    assert sorted(project.items) == sorted(tachi_parts.canonical_finding_id(item["id"]) for item in rrs.SPECS)
    statuses = {finding_id: item["control_status"] for finding_id, item in project.items.items()}
    assert set(statuses.values()) == {"found", "partial", "missing"}, "the nine findings hold every control status: %s" % statuses
    assert max(len(item["evidence"]) for item in project.items.values()) >= 2, "and a finding with more than one evidence entry"
    for item in project.items.values():
        cells = row_cells(item["matrix_row"])
        assert len(cells) == 11 and cells[0] == item["finding_id"] and cells[7] == STATUS_DISPLAY[item["control_status"]]
        for cited in item["evidence"]:
            assert (project.target / cited["file"]).is_file()
    assert project.plan_dir.is_dir() and project.batches() and all(entry["state"] == "done" for entry in project.batches().values())


def test_harness_a_plan_over_the_subset_spreads_every_finding_over_several_batches(rrs, entries, tmp_path):
    scorer, reference = rrs.subset_project(entries[0], entries[1], tmp_path)
    project = ControlsProject(rrs, entries, scorer)
    project.score()
    project.prepare()
    sizes = [len(entry["finding_ids"]) for entry in project.batches().values()]
    assert sum(sizes) == len(project.items) == len(reference["open"]) == 42 and len(sizes) > 1, sizes


# --- FR-K7.1: each peer is counted once -------------------------------------------------------------------------------

@BOTH_FILES
def test_each_peer_is_one_result_and_no_related_location_names_a_finding(rrs, entries, tmp_path, sarif_file):
    """FR-K6.2, FR-K7.1 and D8: N is the number of results, so a peer is a result and is counted once.

    A peer's link to its group is a property and a sentence, never a second listing. No ``relatedLocations`` entry names
    a finding, and no RESOLVED finding appears anywhere in the file (US-6a #5).
    """
    project = make_project(sarif_file, rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    res = project.run()
    assert res.code in RUN_CODES[sarif_file], res.describe()
    results = project.sarif["runs"][0]["results"]
    ids = [item["id"] for item in rrs.SPECS]
    assignments = sc.correlation_assignments(FIRST_RUN_GROUPS, ids)
    peers = sorted(finding_id for finding_id, assignment in assignments.items() if assignment.role == "peer")
    assert peers == ["E-5", "S-10", "T-1"], "the project has three peers, in two groups"
    written = [result["partialFingerprints"]["findingId/v1"] for result in results]
    assert len(results) == len(set(written)) == len(ids) == 9, "N is the number of results, and each finding is one of them"
    by_id = results_by(project.sarif)
    for peer in peers:
        properties = by_id[peer]["properties"]
        assert (properties["correlation-role"], properties["correlation-primary"]) == ("peer", assignments[peer].primary), peer
    for result in results:
        for entry in result.get("relatedLocations", ()):
            assert not FINDING_TOKEN.search(json.dumps(entry)), "a relatedLocations entry names a finding: %s" % (entry,)
    named = {rrs.canon(token) for token in FINDING_TOKEN.findall(project.sarif_text)}
    assert named == {rrs.canon(finding_id) for finding_id in ids}, "the open findings are named, and no RESOLVED one is"
    sc.self_check(results, tool=TOOL_OF[sarif_file], member_ids=ids, assignments=assignments, resolved_ids=rrs.RESOLVED_IDS, uri=URI)


# --- D7, D8: relatedLocations hold evidence only, and pass the resolver's relative-path checks --------------------------

def assert_relative(uri):
    """ADR-050 D7: an evidence URI is relative to the target: no scheme or drive letter, no leading ``/``, no backslash, no ``..``."""
    parts = uri.split("/")
    assert uri and not uri.startswith("/") and "\\" not in uri, uri
    assert re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", uri) is None, "a scheme or a drive letter: %s" % uri
    assert not {"", ".", ".."} & set(parts), uri


def loosely_typed(part):
    """Respell every cited file as an agent might: with a ``./`` and a doubled ``/``. The part validator keeps it as written."""
    for item in part["items"]:
        for cited in item["evidence"]:
            head, _, tail = cited["file"].partition("/")
            cited["file"] = "./%s//%s" % (head, tail)


def test_related_locations_hold_evidence_only_and_pass_the_resolvers_relative_path_checks(rrs, entries, tmp_path):
    """FR-K7.1, D7 and D8: a controls result's ``relatedLocations`` are its evidence, one entry for each, and nothing else.

    A control with no evidence (``missing``) has no key, never an empty array. Each entry names a file under the target
    directory, spelled and encoded by the resolver whatever way the part typed it (``part-files.md``: a ``file`` is
    checked, never rewritten, and the resolver canonicalizes it at render time), so the URI is relative.
    """
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    res = project.run(mutate=loosely_typed)
    assert res.code in RUN_CODES[CONTROLS_FILE], res.describe()
    results = results_by(project.sarif)
    with_evidence = without_evidence = 0
    for item in rrs.SPECS:
        want = project.items[tachi_parts.canonical_finding_id(item["id"])]
        result = results[item["id"]]
        if not want["evidence"]:
            without_evidence += 1
            assert want["control_status"] == "missing" and "relatedLocations" not in result, item["id"]
            continue
        with_evidence += 1
        related = result["relatedLocations"]
        assert len(related) == len(want["evidence"]), item["id"]
        assert sorted(entry["id"] for entry in related) == list(range(len(related))), "the entries are numbered from 0"  # reading: their order isn't pinned
        expected = {}
        for cited in want["evidence"]:
            good = sc.resolve_file(cited["file"], root=str(project.target))  # the cited file passes the resolver's checks
            expected[(good.uri, cited["line"])] = good.path
        got = {}
        for entry in related:
            assert list(entry) == ["id", "message", "physicalLocation"], "evidence has the shape of sc.evidence_location"
            uri = entry["physicalLocation"]["artifactLocation"]["uri"]
            assert_relative(uri)
            assert list(entry["physicalLocation"]["region"]) == ["startLine"]
            got[(uri, entry["physicalLocation"]["region"]["startLine"])] = entry["message"]["text"]
        assert set(got) == set(expected), "each cited file and line, in the resolver's spelling: %s" % item["id"]
        for key, text in got.items():  # reading: the category's wording is the renderer's; the file named is the resolver's spelling of the cited one
            shape = sc.EVIDENCE_MESSAGE.format(category="\0", file=expected[key])
            assert re.fullmatch(".+".join(re.escape(piece) for piece in shape.split("\0")), text), (item["id"], text)
            assert not FINDING_TOKEN.search(text), "an evidence entry names a finding"
    assert with_evidence >= 4 and without_evidence >= 1, "the project has results with evidence and a result without"
    ids = [item["id"] for item in rrs.SPECS]
    sc.self_check(project.sarif["runs"][0]["results"], tool=CONTROLS, member_ids=ids,
                  assignments=sc.correlation_assignments(FIRST_RUN_GROUPS, ids), resolved_ids=rrs.RESOLVED_IDS, uri=URI)


# --- ruling B (D7): reused-id is carried over from the input ---------------------------------------------------------

def test_reused_id_is_carried_over_from_the_input_risk_scores(rrs, entries, tmp_path):
    """FR-E.19, D7 and US-6a #10: ``render-compensating-controls.py`` carries the flag from its input into ``integrity-flags``.

    The scorer finds the reuse in its baseline. The controls stage is given no baseline here, so the flag can only be its
    input's. Both files flag the same findings under the same string, and the reissued ID inherits the old alert in each.
    """
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path)
    keys_1, baseline = reissue_ids(rrs, project, RUN_CODES[CONTROLS_FILE])
    res = project.run(baseline_dir=baseline, controls_baseline=None)
    assert res.code in (0, 5), res.describe()
    controls = results_by(project.sarif)
    scorer = results_by(project.scorer_sarif)
    assert sorted(i for i, r in controls.items() if REUSED_ID_FLAG in r["properties"]["integrity-flags"]) == ["S-1", "S-2"]
    assert sorted(i for i, r in scorer.items() if REUSED_ID_FLAG in r["properties"]["score-flags"]) == ["S-1", "S-2"]
    assert all(r["properties"]["integrity-flags"] == sorted(r["properties"]["integrity-flags"]) for r in controls.values()), \
        "a sorted array, present on every result"
    assert alert_keys(project.sarif)["S-2"] == keys_1["S-2"], "the reissued ID inherits the old alert: the exposure the flag marks (ruling B)"


def test_a_controls_baseline_alone_does_not_make_the_stage_flag_a_reused_id(rrs, entries, tmp_path):
    """The converse of the case above: the stage carries what its input says and derives nothing.

    The scorer has no baseline in run 2, so it flags nothing, and the controls stage, whose baseline lists the reused IDs, does not either.
    """
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path)
    keys_1, baseline = reissue_ids(rrs, project, RUN_CODES[CONTROLS_FILE])
    res = project.run(baseline_dir=None, controls_baseline=baseline)  # reading: a baseline names a directory of both stages' files
    assert res.code in (0, 5), res.describe()
    assert not [r for r in project.scorer_sarif["runs"][0]["results"] if REUSED_ID_FLAG in r["properties"]["score-flags"]]
    for result in project.sarif["runs"][0]["results"]:
        assert REUSED_ID_FLAG not in result["properties"]["integrity-flags"], result["partialFingerprints"]["findingId/v1"]


# --- R-33: the three (tool, category) pairs differ across the files ---------------------------------------------------

def test_the_three_tool_and_category_pairs_differ_across_the_rendered_files(rrs, entries, tmp_path):
    """R-33, US-6a #3 and FR-E.2's cross-file assertion, on the files the renderers write.

    ``threats.sarif`` is still the orchestrator's until PR 2, so its pair is ADR-050 D7's constant, written out here. Section 22 puts the
    generator's own file beside these two (``test_the_three_files_have_three_different_tool_and_category_pairs_...``), once T100 lands.
    """
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    res = project.run()
    assert res.code in RUN_CODES[CONTROLS_FILE], res.describe()
    documents = {SCORER_FILE: project.scorer_sarif, CONTROLS_FILE: project.sarif}
    drivers = {name: document["runs"][0]["tool"]["driver"] for name, document in documents.items()}
    assert drivers[SCORER_FILE]["name"] == "tachi-risk-scorer" and drivers[CONTROLS_FILE]["name"] == "tachi-control-analyzer", "verbatim"
    pairs = {("Tachi", "threat-model"), (drivers[SCORER_FILE]["name"], SCORER_CATEGORY), (drivers[CONTROLS_FILE]["name"], CONTROLS_CATEGORY)}
    assert len(pairs) == 3
    assert {driver["informationUri"] for driver in drivers.values()} == {"https://github.com/davidmatousek/tachi"}
    for document in documents.values():
        assert "automationDetails" not in document["runs"][0], "the upload step's category governs (D7)"
    scorer, controls = results_by(documents[SCORER_FILE]), results_by(documents[CONTROLS_FILE])
    assert sorted(scorer) == sorted(controls), "both files hold the open findings"
    for finding_id in controls:
        canonical = tachi_parts.canonical_finding_id(finding_id)
        hashes = {file: result[finding_id]["partialFingerprints"]["primaryLocationLineHash"]
                  for file, result in ((SCORER_FILE, scorer), (CONTROLS_FILE, controls))}
        assert hashes == {SCORER_FILE: recipe(SCORER, canonical), CONTROLS_FILE: recipe(CONTROLS, canonical)}, finding_id
        assert len(set(hashes.values()) | {recipe(THREATS, canonical)}) == 3, "one finding, three files, three hashes"
        assert scorer[finding_id]["ruleId"] == controls[finding_id]["ruleId"] == EXPECTED_RULES[finding_id.partition("-")[0]], \
            "the rule is a function of the finding, shared by the files (ADR-013 D2)"
        assert scorer[finding_id]["locations"][0]["physicalLocation"] == controls[finding_id]["locations"][0]["physicalLocation"], \
            "and so is the location"


# --- KB 24: a case variant gives one URI, on a real case-insensitive volume (f374-macos) -----------------------------

def capitals(part):
    """Respell every cited file in capitals: the same files on a case-insensitive volume, so each must come out spelled as the volume spells it."""
    for item in part["items"]:
        for cited in item["evidence"]:
            cited["file"] = cited["file"].upper()


def assert_evidence_spelled(project, results):
    """Each result's evidence entries are the files its item cites, in their canonical spelling, however the part typed them."""
    by_id = {tachi_parts.canonical_finding_id(r["partialFingerprints"]["findingId/v1"]): r for r in results}
    checked = 0
    for finding_id, item in project.items.items():
        related = by_id[finding_id].get("relatedLocations", [])
        got = {(e["physicalLocation"]["artifactLocation"]["uri"], e["physicalLocation"]["region"]["startLine"]) for e in related}
        assert got == {(cited["file"], cited["line"]) for cited in item["evidence"]}, finding_id
        checked += len(related)
    assert checked >= 5, "the project has evidence to spell"


@BOTH_FILES
def test_a_case_variant_gives_every_result_the_same_uri_on_a_real_case_insensitive_volume(rrs, entries, tmp_path, sarif_file):
    """KB 24, FR-E.2 and D16's macOS job: Section 16's fake volume holds this offline, and here the volume is real.

    ``f374-macos`` runs this module alone, so it runs this case. It is skipped on a case-sensitive volume, as Section 6's
    real-volume case is. The body line names the architecture file in capitals, and the controls part cites its evidence
    in capitals too, so one URI is each result's, and one spelling is each evidence entry's.
    """
    if not _case_insensitive(tmp_path):
        pytest.skip("this volume is case-sensitive; the fake filesystem covers the case offline")
    project = make_project(sarif_file, rrs, entries, tmp_path, body_line="DOCS/Other/ARCHITECTURE.md")
    add_architecture_files(project)
    (project.out / "architecture.md").write_text("# the snapshot\n", encoding="utf-8")
    options = {"architecture": False}
    if sarif_file == CONTROLS_FILE:
        options["mutate"] = capitals
    res = project.run(**options)
    assert res.code == 0, res.describe()
    results = project.sarif["runs"][0]["results"]
    assert {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in results} == {"docs/other/architecture.md"}
    if sarif_file == CONTROLS_FILE:
        assert_evidence_spelled(project, results)


def test_evidence_cited_in_a_case_variant_is_spelled_by_the_resolver_on_a_case_insensitive_volume(rrs, entries, tmp_path, monkeypatch):
    """The same case offline and on every platform: a fake case-insensitive volume stands in for the adopter's laptop."""
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path)
    project.score(architecture=False)
    fake = FakeFilesystem(str(tmp_path), case_insensitive=True)
    mirror(fake, tmp_path)
    monkeypatch.setattr(sc, "OS_FILESYSTEM", fake)
    res = project.run(mutate=capitals, architecture=False, score=False)  # no flag: the default path warns, so exit 5 is fine
    assert res.code in RUN_CODES[CONTROLS_FILE], res.describe()
    assert_evidence_spelled(project, project.sarif["runs"][0]["results"])


# --- the clean run, and a reassessment ---------------------------------------------------------------------------------

def test_a_clean_controls_run_exits_0_with_no_warning(rrs, entries, tmp_path):
    """The synthetic project is clean, so a controls run has nothing to warn about: exit 0 and an empty ``warnings`` list.

    Section 16's pair cases accept exit 5 from a controls run, so that one warning the harness didn't foresee can't hide
    all of them. This is the case where such a warning shows.
    """
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    res = project.run()
    assert res.code == 0, res.describe()
    record = project.record
    assert (record["status"], record["warnings"], record["error"], record["undeclared_paths"]) == ("success", [], None, [])


def test_a_reassessment_changes_the_results_and_never_their_keys(rrs, entries, tmp_path):
    """FR-E.2 and D7: nothing but the tool, the category, the rule, the line hash and the URI is identity.

    In run 2 the agent re-assesses every finding: another control status and another category, so other evidence, levels,
    messages and properties. Run 2 renders into the same directory, with no baseline, and no key moves.
    """
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    assert project.run().code in RUN_CODES[CONTROLS_FILE]
    first, keys_1 = results_by(project.sarif), alert_keys(project.sarif)
    project.variant = 1
    assert project.run().code in RUN_CODES[CONTROLS_FILE]
    second = results_by(project.sarif)
    assert alert_keys(project.sarif) == keys_1, "a re-assessment moves no key"
    own = lambda result: {key: value for key, value in result.items() if key not in ("ruleId", "partialFingerprints", "locations")}  # noqa: E731
    assert sum(1 for finding_id in first if own(first[finding_id]) != own(second[finding_id])) >= 5, \
        "the re-assessment is not vacuous: it changes what a result says"


# =============================================================================
# 20. The rules both renderers share (PM W3 ruling 2, gap A)
# =============================================================================
#
# ``sarif_common.RULES`` and ``build_rules`` are the one table that ``render-risk-scores.py`` and
# ``render-compensating-controls.py`` write their rules from. These cases need no renderer: they pin the table to the two
# 1.1 templates, which is where an adopter reads the output schema.

SCHEMAS = REPO_ROOT / "templates" / "tachi" / "output-schemas"
RULE_TEMPLATES = ["risk-scores.sarif", "compensating-controls.sarif"]
RULE_CATEGORIES = [
    "spoofing", "tampering", "repudiation", "info-disclosure", "denial-of-service", "privilege-escalation", "agentic", "llm"]
EVERY_CATEGORY = {category: Decimal("7.5") for category in RULE_CATEGORIES}
RULE_KEYS = ["id", "shortDescription", "fullDescription", "properties", "relationships"]


def template_driver(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))["runs"][0]["tool"]["driver"]


def relationships_of(taxon_ids):
    """The architect's form, written out here and not imported: one ``relevant`` link for each ID, in order."""
    return [
        {"target": {"id": taxon_id, "toolComponent": {"name": "CWE" if taxon_id.startswith("CWE-") else "OWASP"}},
         "kinds": ["relevant"]}
        for taxon_id in taxon_ids
    ]


def test_the_table_has_one_row_for_each_of_the_eight_categories_in_the_rule_maps_order():
    assert [row[0] for row in sc.RULES] == RULE_CATEGORIES == list(sc.RULE_ID_BY_CATEGORY)
    assert set(RULE_CATEGORIES) == set(tachi_scoring.PREFIX_CATEGORY.values()), "every category the resolver can return has a rule"
    for category, short, full, tags, taxon_ids in sc.RULES:
        assert short and full and tags and taxon_ids, category
        assert isinstance(tags, tuple) and isinstance(taxon_ids, tuple), "a row can't be changed by a caller"
        assert len(set(tags)) == len(tags) and len(set(taxon_ids)) == len(taxon_ids), category


@pytest.mark.parametrize("name", RULE_TEMPLATES)
def test_each_shared_rule_equals_the_templates_rule_with_the_same_id_field_for_field_and_in_key_order(name):
    wanted = {rule["id"]: rule for rule in template_driver(name)["rules"]}
    built = sc.build_rules(EVERY_CATEGORY)
    assert sorted(rule["id"] for rule in built) == sorted(wanted), "the same eight rules, no more and no fewer"
    for rule in built:
        template = wanted[rule["id"]]
        where = "%s %s" % (name, rule["id"])
        assert list(rule) == list(template) == RULE_KEYS, where
        for field in ("id", "shortDescription", "fullDescription", "relationships"):
            assert json.dumps(rule[field]) == json.dumps(template[field]), (where, field)  # dumps keeps nested key order
        assert list(rule["properties"]) == list(template["properties"]) == ["tags", "security-severity"], where
        assert rule["properties"]["tags"] == template["properties"]["tags"], where
        # ``security-severity`` is the one field excepted: the template shows a placeholder, and the renderer a score
        assert rule["properties"]["security-severity"] == "7.5", where


def test_each_rule_relates_to_every_taxonomy_id_of_its_row_in_order_in_the_architects_form():
    built = {rule["id"]: rule for rule in sc.build_rules(EVERY_CATEGORY)}
    for category, _short, _full, _tags, taxon_ids in sc.RULES:
        rule = built[sc.RULE_ID_BY_CATEGORY[category]]
        assert rule["relationships"] == relationships_of(taxon_ids), category
        assert [link["target"]["id"] for link in rule["relationships"]] == list(taxon_ids), category
        for link in rule["relationships"]:  # dict equality ignores key order, so the order is pinned here
            assert list(link) == ["target", "kinds"] and list(link["target"]) == ["id", "toolComponent"], category
            assert list(link["target"]["toolComponent"]) == ["name"] and link["kinds"] == ["relevant"], category


@pytest.mark.parametrize("name", RULE_TEMPLATES)
def test_the_driver_with_a_version_has_the_key_order_of_the_1_1_templates(name):
    driver = sc.build_driver(
        name, semantic_version=tachi_parts.VERSION, rules=sc.build_rules(EVERY_CATEGORY),
        supported=sc.supported_taxonomies(), version=tachi_parts.VERSION)
    assert list(driver) == list(template_driver(name)) == [
        "name", "version", "semanticVersion", "informationUri", "supportedTaxonomies", "rules"]


@pytest.mark.parametrize("taxon_id,name", [
    ("A01", "OWASP"), ("A05", "OWASP"), ("A07", "OWASP"), ("A09", "OWASP"), ("A10", "OWASP"),
    ("CWE-74", "CWE"), ("CWE-693", "CWE"), ("CWE-1427", "CWE"),
])
def test_the_taxonomy_name_map_is_cwe_for_cwe_n_and_owasp_for_a01_to_a10(taxon_id, name):
    assert sc.taxonomy_name_for(taxon_id) == name


@pytest.mark.parametrize("bad", [
    "", "A00", "A11", "A1", "A001", "a01", "A01 ", " A01", "A01\n", "A0\u0661", "LLM01", "ASI01", "ASI09",
    "CWE", "CWE-", "CWE-0", "CWE-074", "CWE-x", "CWE-7\n", "cwe-79", "CWE 79", "CWE_79", "CWE-\u0661", "ID",
    None, 7, ["A01"],
], ids=repr)
def test_an_id_that_is_neither_cwe_n_nor_a01_to_a10_is_a_shipped_code_defect_and_raises(bad):
    with pytest.raises(ValueError):
        sc.taxonomy_name_for(bad)


def test_a_rule_is_written_only_for_a_category_with_results_and_in_the_tables_order():
    assert sc.build_rules({}) == []
    assert [rule["id"] for rule in sc.build_rules({"llm": Decimal("3.0")})] == ["tachi/ai/llm-threats"]
    # the mapping's own order does not matter: the table's does
    unordered = {"llm": Decimal("3.0"), "spoofing": Decimal("9.1"), "agentic": Decimal("1.0")}
    assert [rule["id"] for rule in sc.build_rules(unordered)] == [
        "tachi/stride/spoofing", "tachi/ai/agentic-threats", "tachi/ai/llm-threats"]


@pytest.mark.parametrize("score,text", [
    (Decimal("7.5"), "7.5"), (Decimal("7"), "7.0"), (7, "7.0"), (Decimal("10"), "10.0"), (Decimal("0.0"), "0.0"),
    (Decimal("4.55"), "4.6"), (Decimal("9.04"), "9.0"), (Decimal("9.05"), "9.1"),
])
def test_a_rules_security_severity_is_its_highest_score_as_text_with_one_decimal_rounded_half_up(score, text):
    (rule,) = sc.build_rules({"tampering": score})
    assert rule["properties"]["security-severity"] == text


@pytest.mark.parametrize("bad", [7.5, "7.5", None, True], ids=repr)
def test_a_score_that_is_not_a_decimal_or_an_int_is_refused_as_the_scoring_module_refuses_it(bad):
    with pytest.raises(TypeError):
        sc.build_rules({"tampering": bad})


@pytest.mark.parametrize("bad", ["", "stride", "Spoofing", "tachi/stride/spoofing", "AG", None], ids=repr)
def test_a_key_that_is_not_one_of_the_eight_categories_raises_and_never_drops_a_rule_silently(bad):
    with pytest.raises(ValueError) as excinfo:
        sc.build_rules({"llm": Decimal("1.0"), bad: Decimal("2.0")})
    assert "not a rule category" in str(excinfo.value)


def test_the_rules_are_new_on_every_call_so_a_caller_cannot_change_the_table():
    before = json.dumps(sc.build_rules(EVERY_CATEGORY))
    changed = sc.build_rules(EVERY_CATEGORY)
    changed[0]["properties"]["tags"].append("x")
    changed[0]["relationships"][0]["target"]["id"] = "A99"
    changed[0]["relationships"].append({})
    changed[0]["shortDescription"]["text"] = "changed"
    assert json.dumps(sc.build_rules(EVERY_CATEGORY)) == before


# =============================================================================
# 21. The RESOLVED scan reads what a renderer composes, and not text it copies (ADR-050 D8; ruled at W3 from T053; P0-10)
# =============================================================================
#
# T-3 is RESOLVED in these cases, and it is none of ``MEMBERS``. An ID in text that a renderer copies from an input is a
# mention, not a reference: a threat or a mitigation (the reference set's), a person's owner, a snippet or a path in the
# scanned repository, a recommendation. The self-check lets it pass, so a repository that annotates its code with finding IDs
# can't fail every baseline-aware render with exit 4. The IDs, the correlation keys and the flags that a renderer composes
# still may not name a RESOLVED finding. The first cases need no renderer. The last ones drive the scorer's renderer, on the
# project harness of Section 16, where T-3 is in Section 4c. None of them needs the controls renderer.

COPIED_PROPERTIES = {  # the ruling's table, written out here and not imported: each file skips the text that its renderer copies
    SCORER: ("risk-owner",),
    CONTROLS: ("control-evidence", "recommendation"),
}
FLAG_NAMES = {SCORER: "score-flags", CONTROLS: "integrity-flags"}
EACH_FILE_THAT_COPIES_TEXT = pytest.mark.parametrize("tool", [SCORER, CONTROLS], ids=["risk-scores", "compensating-controls"])


def mention_in_threat(result):
    """``message.text``, before ruling C's sentence when the result is correlated (the text ends with the sentence)."""
    own, sentence, tail = result["message"]["text"].partition(" Correlated in ")
    result["message"]["text"] = own + " It is what T-3 once was." + sentence + tail


def mention_in_mitigation(result):
    result["message"]["markdown"] = "Rotate the token, the fix that closed T-3."


def mention_in_owner(result):
    result["properties"]["risk-owner"] = "T-3 team"


def mention_in_snippet(result):
    result["properties"]["control-evidence"] = [{"file": "src/auth.py", "line": 4, "snippet": "# mitigates T-3\nverify(token)"}]


def mention_in_evidence_path(result):
    """The path that the renderer writes in both places: the ``control-evidence`` entry and the ``relatedLocations`` entry."""
    path = sc.ResolvedPath("docs/T-3.md", "docs/T-3.md")
    result["properties"]["control-evidence"] = [{"file": path.path, "line": 1, "snippet": "A design note."}]
    add_related(result, [sc.evidence_location(0, "authentication", path, 1)])


def mention_in_recommendation(result):
    result["properties"]["recommendation"] = "**What to Implement**: Redo the check that T-3 once had."


MENTIONS = [  # (case, the file whose renderer copies this text, how the mention gets in)
    ("risk-scores-threat", SCORER, mention_in_threat),
    ("risk-scores-mitigation", SCORER, mention_in_mitigation),
    ("risk-scores-owner", SCORER, mention_in_owner),
    ("controls-threat", CONTROLS, mention_in_threat),
    ("controls-mitigation", CONTROLS, mention_in_mitigation),
    ("controls-snippet", CONTROLS, mention_in_snippet),
    ("controls-evidence-path", CONTROLS, mention_in_evidence_path),
    ("controls-recommendation", CONTROLS, mention_in_recommendation),
]


@pytest.mark.parametrize("tool,plant", [pytest.param(tool, plant, id=case) for case, tool, plant in MENTIONS])
def test_a_resolved_id_in_text_that_a_renderer_copies_is_a_mention_and_passes(tool, plant):
    """Every result of the run, correlated or not, carries the mention, so primaries and peers are both covered."""
    results, assignments = build_run(tool=tool)
    assert {assignment.role for assignment in assignments.values()} == {"primary", "peer"}
    for result in results:
        plant(result)
        assert "T-3" in json.dumps(result), "the mention is in the result"
    check(results, assignments, tool=tool, resolved=["T-3"])


def test_a_threat_that_names_a_resolved_id_still_ends_with_ruling_cs_sentence_exactly():
    """The sentence keeps its own exact check against the member set, whatever the text before it says."""
    results, assignments = build_run()
    primary = results[0]
    assert assignments["S-1"].role == "primary"
    mention_in_threat(primary)
    primary["message"]["text"] = primary["message"]["text"].replace("peers T-2.", "peers T-2, T-3.")
    problems = problems_of(results, assignments, resolved=["T-3"])
    assert any(p.startswith("S-1: the message does not end with ruling C's sentence") for p in problems), problems


def test_the_properties_that_carry_copied_text_are_the_ones_the_ruling_names():
    assert sc.COPIED_TEXT_PROPERTIES == COPIED_PROPERTIES


@pytest.mark.parametrize("name,tool", [("risk-scores.sarif", SCORER), ("compensating-controls.sarif", CONTROLS)], ids=["risk-scores", "compensating-controls"])
def test_each_skipped_property_is_one_that_the_files_template_writes(name, tool):
    """A template rename can't leave a stale skip behind: every name is a property of the 1.1 template's results."""
    document = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    written = {key for result in document["runs"][0]["results"] for key in result["properties"]}
    assert set(COPIED_PROPERTIES[tool]) <= written, sorted(written)


# --- what the scan still reads ------------------------------------------------------------------------------------------

@EACH_FILE_THAT_COPIES_TEXT
def test_a_correlation_key_that_names_a_resolved_id_is_still_refused(tool):
    results, assignments = build_run(tool=tool)
    assert assignments["T-2"].role == "peer"
    results[1]["properties"]["correlation-primary"] = "T-3"
    problems = problems_of(results, assignments, tool=tool, resolved=["T-3"])
    assert "T-2: the RESOLVED finding T-3 appears in properties.correlation-primary" in problems, problems


@EACH_FILE_THAT_COPIES_TEXT
def test_a_result_for_a_resolved_finding_is_still_refused_in_findingid_v1(tool):
    results, assignments = build_run(tool=tool)
    results.append(make_result("T-3", tool=tool))
    problems = problems_of(results, assignments, tool=tool, resolved=["T-3"])
    assert "T-3: the RESOLVED finding T-3 appears in findingId/v1" in problems, problems
    assert any("results for findings outside the member set: T-3" in p for p in problems), problems


@EACH_FILE_THAT_COPIES_TEXT
def test_a_flag_that_names_a_resolved_id_is_still_refused(tool):
    """A flag is composed, ``kind:field:cause``, so its ID is a reference: ``divergent:composite_score:primary=T-3``."""
    results, assignments = build_run(tool=tool)
    results[2]["properties"][FLAG_NAMES[tool]] = ["divergent:composite_score:primary=T-3"]
    problems = problems_of(results, assignments, tool=tool, resolved=["T-3"])
    assert "I-3: the RESOLVED finding T-3 appears in properties.%s[0]" % FLAG_NAMES[tool] in problems, problems


COPIED_VALUES = {
    "risk-owner": "T-3 team",
    "control-evidence": [{"file": "docs/T-3.md", "line": 1, "snippet": "A design note."}],
    "recommendation": "**What to Implement**: Redo the check that T-3 once had.",
}


@pytest.mark.parametrize("tool,name", [
    (CONTROLS, "risk-owner"), (THREATS, "risk-owner"),
    (SCORER, "control-evidence"), (THREATS, "control-evidence"),
    (SCORER, "recommendation"), (THREATS, "recommendation"),
], ids=["controls-risk-owner", "threats-risk-owner", "risk-scores-control-evidence", "threats-control-evidence",
        "risk-scores-recommendation", "threats-recommendation"])
def test_a_property_is_skipped_only_in_the_file_that_writes_it(tool, name):
    """The scorer writes ``risk-owner`` and the controls file the other two. Anywhere else the property isn't known copied text."""
    assert name not in COPIED_PROPERTIES.get(tool, ())
    results, assignments = build_run(tool=tool)
    results[0]["properties"][name] = COPIED_VALUES[name]
    problems = problems_of(results, assignments, tool=tool, resolved=["T-3"])
    assert any(p.startswith("S-1: the RESOLVED finding T-3 appears in properties.%s" % name) for p in problems), problems


def test_a_skipped_property_is_skipped_at_the_top_level_only():
    results, assignments = build_run(tool=SCORER)
    results[0]["properties"]["notes"] = {"risk-owner": "T-3 team"}
    problems = problems_of(results, assignments, tool=SCORER, resolved=["T-3"])
    assert "S-1: the RESOLVED finding T-3 appears in properties.notes.risk-owner" in problems, problems


def test_a_related_location_that_leads_with_a_resolved_finding_is_still_refused_as_a_peer_reference():
    """The scan no longer reads a ``relatedLocations`` message, but D8's other rule stands: none names a finding, whichever one."""
    results, assignments = build_run(tool=CONTROLS)
    add_related(results[0], [evidence_entry("T-3: a peer that was resolved")])
    problems = problems_of(results, assignments, tool=CONTROLS, resolved=["T-3"])
    assert "S-1: a relatedLocations entry names the finding T-3" in problems, problems


# --- through the scorer's renderer (Section 16's project harness) ---------------------------------------------------------

def test_an_open_findings_threat_and_mitigation_that_name_a_resolved_finding_render_cleanly(rrs, entries, tmp_path):
    """P0-10's own case: the reference set's threat and mitigation are copied text, and T-3 is listed in Section 4c.

    S-2 is the primary of CG-1, so its text ends with ruling C's sentence after the mention.
    """
    threat = "Shared tokens let callers impersonate each other, as they did in T-3."
    mitigation = "Rotate the token, the fix that closed T-3."
    text = rrs.edit_table_cell(rrs.make_threats_md(groups=FIRST_RUN_GROUPS), "## 7. Recommended Actions", "S-2", "Threat", threat)
    text = rrs.edit_table_cell(text, "## 7. Recommended Actions", "S-2", "Mitigation", mitigation)
    project = scorer_project(rrs, entries, tmp_path, threats_text=text)
    res = project.run()
    assert "T-3" in rrs.RESOLVED_IDS and res.code in RUN_CODES[SCORER_FILE], res.describe()
    assignment = sc.correlation_assignments(FIRST_RUN_GROUPS, [item["id"] for item in rrs.SPECS])["S-2"]
    assert assignment.role == "primary"
    result = results_by(project.sarif)["S-2"]
    assert result["message"] == {"text": expected_text(threat, assignment), "markdown": mitigation}


def test_an_owner_that_names_a_resolved_finding_is_carried_and_renders_cleanly(rrs, entries, tmp_path):
    """A person's owner is carried verbatim from the baseline (D9), so ``T-3 team`` is a mention and not a reference."""
    first = scorer_project(rrs, entries, tmp_path / "first")
    res = first.run()
    assert res.code in RUN_CODES[SCORER_FILE], res.describe()
    second = rrs.second_run(entries[0], entries[1], tmp_path / "second", first, edit_baseline=lambda md: rrs.edit_table_cell(
        md, "## 4. Governance Fields", "S-2", "Owner", "T-3 team"))
    res = second.run()
    assert "T-3" in rrs.RESOLVED_IDS and res.code in RUN_CODES[SCORER_FILE], res.describe()
    assert results_by(second.sarif)["S-2"]["properties"]["risk-owner"] == "T-3 team"


def name_resolved_in_correlation_primary(document):
    peer = next(result for result in document["runs"][0]["results"] if result["properties"].get("correlation-role") == "peer")
    peer["properties"]["correlation-primary"] = "T-3"


def name_resolved_in_findingid(document):
    """Add a result for T-3 with the hash and the rule of its own: a renderer that kept a RESOLVED finding."""
    results = document["runs"][0]["results"]
    extra = copy.deepcopy(next(result for result in results if "correlation-group" not in result["properties"]))
    extra["ruleId"] = sc.rule_id_for("T-3")
    extra["partialFingerprints"] = sc.partial_fingerprints(SCORER, "T-3")
    results.append(extra)


def name_resolved_in_a_flag(document):
    document["runs"][0]["results"][0]["properties"]["score-flags"] = ["divergent:composite_score:primary=T-3"]


@pytest.mark.parametrize("poison,where", [
    pytest.param(name_resolved_in_correlation_primary, "properties.correlation-primary", id="correlation-primary"),
    pytest.param(name_resolved_in_findingid, "findingId/v1", id="findingid-v1"),
    pytest.param(name_resolved_in_a_flag, "properties.score-flags[0]", id="score-flags"),
])
def test_a_composed_value_that_names_a_resolved_finding_still_fails_the_scorers_render_with_exit_4(rrs, entries, tmp_path, poison, where):
    """A seeded renderer bug, in the staged SARIF only: the from-disk self-check is the one that sees it (ADR-050 D4)."""
    project = scorer_project(rrs, entries, tmp_path, threats_text=rrs.make_threats_md(groups=FIRST_RUN_GROUPS))
    project.earlier()
    project.prepare()
    with rrs.tampering_with_staged(rrs.SARIF, rrs.json_edit(poison)):
        res = project.render()
    rrs.assert_failed_closed(project, res, "the RESOLVED finding T-3 appears in " + where)


def test_an_affected_assets_cell_holding_a_line_separator_forges_no_second_row():
    """SA-13 (T064): the Affected Assets block splits rows on a newline only. ``str.splitlines()`` also broke a row at U+2028,
    so a cell that held one read as a second, phantom row (here T-9's)."""
    block = "## Affected Assets\n\n| Finding ID | Affected Assets |\n|---|---|\n| S-1 | [phi]" + chr(0x2028) + "| T-9 | [pci] |\n"
    assets = sc.parse_affected_assets(block)
    assert "T-9" not in assets, "a line separator inside a cell must not start a row"
    assert assets.get("S-1") is not None, "the real row still reads"


# =============================================================================
# 22. threats.sarif through its generator: FR-E.2's model for the third file, the three files side by side and FR-E.13's pin
#     (T099, red until T100; ADR-050 D1, D7, D8)
# =============================================================================
#
# From PR 2 the third file is written by shipped code too: ``scripts/generate-threats-sarif.py`` reads the compiled ``threats.md`` and
# writes ``threats.sarif`` through the same emitter as the two renderers. The generator's own cases (its command line and exit codes, N/N on
# every committed ``threats.md`` with the drift forms among them, what each result carries, the write) are ``test_threats_sarif.py``'s. This
# section holds what is the identity test's: FR-E.2's two-run model (the regroup pair, an unchanged re-run, no shared key, a case variant),
# D7's carrier chain (the flag, the body line, the default, and a warning for each carrier that fails), ruling C's cap, the three files
# compared, and FR-E.13's pin. It is driven in-process through ``main(argv)`` (H15) on ``test_threats_sarif.py``'s project.
#
# The generator takes no plan and writes no stage record, so a warning is on stderr and its codes are 0, 1, 2 and 4 (``contracts/cli.md``): a
# case reads the streams where Sections 16 and 19 read the record. The scorer's files carry ``score-flags`` and the controls file
# ``integrity-flags``; this file has no flag property, because ruling B's reissue check for ``threats.md`` is ``check-threat-model.py``'s.

THREATS_FILE = "threats.sarif"
THREATS_CATEGORY = "threat-model"  # the upload category of threats.sarif: tachi recommends it and never writes it


@pytest.fixture(scope="module")
def tsh():
    """``test_threats_sarif.py``'s harness, imported when a case first needs it: the project that the generator runs on."""
    from . import test_threats_sarif
    return test_threats_sarif


@pytest.fixture(scope="module")
def gen(tsh):
    """The generator, loaded when a case first asks. Until T100 rewrites it, the case fails and says so."""
    return tsh.load_generator()


def threats_keys(document):
    """GitHub's matching key of each result in a ``threats.sarif`` document, by ``findingId/v1``: tool, category, rule, hash and URI."""
    run = document["runs"][0]
    tool = run["tool"]["driver"]["name"]
    assert tool == THREATS, "the tool is Tachi, verbatim"
    return {finding_id: (tool, THREATS_CATEGORY) + key for finding_id, key in keys_of(run["results"]).items()}


def run_threats_pair(rrs, tsh, gen, root, baseline_aware, plant=False, replace_baseline_sarif=False):
    """The generator's ``run_pair``: run 1, then run 2 (regrouped, with one more finding), in one project.

    Run 2 is baseline-aware when asked: its ``threats.md`` names run 1's directory as its baseline source and a run ID, and its carried
    findings are UNCHANGED. The generator takes no baseline argument: ``baseline-run-id`` comes from that block alone. ``plant`` puts an
    older ``threats.sarif`` with hashes of its own where run 1 will write its file, and ``replace_baseline_sarif`` swaps the baseline
    directory's SARIF for one that lists other findings under other hashes.
    """
    project = tsh.Project(gen, root, groups=FIRST_RUN_GROUPS)
    ids_1 = [item["id"] for item in rrs.SPECS]
    if plant:
        project.sarif_path.write_text(planted_sarif(ids_1, tool=THREATS), encoding="utf-8")
    first = project.generate()
    assert first.code == 0, first.describe()
    pair = SimpleNamespace(project=project, ids_1=ids_1, specs_1=list(rrs.SPECS), baseline=None,
                           first=project.sarif, first_text=project.sarif_text)
    if baseline_aware:
        pair.baseline = Path(root) / "baseline-1"
        pair.baseline.mkdir()
        for name in ("threats.md", THREATS_FILE):
            shutil.copyfile(str(project.out / name), str(pair.baseline / name))
        if replace_baseline_sarif:
            (pair.baseline / THREATS_FILE).write_text(planted_sarif(ids_1 + ["S-99"], offset=20, tool=THREATS), encoding="utf-8")
    pair.specs_2 = second_run_specs(rrs, baseline_aware)
    pair.ids_2 = [item["id"] for item in pair.specs_2]
    text_2 = rrs.make_threats_md(pair.specs_2, rrs.RESOLVED, groups=SECOND_RUN_GROUPS,
                                 baseline_source="baseline-1/threats.md" if baseline_aware else None)
    project.threats.write_text(tsh.with_baseline(text_2) if baseline_aware else text_2, encoding="utf-8")
    second = project.generate()
    assert second.code == 0, second.describe()
    pair.second, pair.second_text = project.sarif, project.sarif_text
    return pair


@BOTH_MODES
def test_threats_sarif_the_regroup_pair_keeps_every_carried_key_and_changes_only_the_text(rrs, tsh, gen, tmp_path, baseline_aware):
    """US-6b #1: run 2 regroups carried findings, changes a primary and dissolves a group, and no key moves."""
    pair = run_threats_pair(rrs, tsh, gen, tmp_path, baseline_aware)
    keys_1, keys_2 = threats_keys(pair.first), threats_keys(pair.second)
    assert sorted(keys_1) == sorted(pair.ids_1) and sorted(keys_2) == sorted(pair.ids_2), "no finding drops out"
    for finding_id in pair.ids_1:
        assert keys_2[finding_id] == keys_1[finding_id], "%s: a regroup never moves a key" % finding_id
    assert "T-7" in keys_2 and "T-7" not in keys_1, "the finding only run 2 has gets a key of its own"
    for keys in (keys_1, keys_2):
        assert len(set(keys.values())) == len(keys), "no two present results share a key (the F-012 lesson)"
    texts, owns = {}, {}
    for run, document, specs, groups, ids in ((1, pair.first, pair.specs_1, FIRST_RUN_GROUPS, pair.ids_1),
                                              (2, pair.second, pair.specs_2, SECOND_RUN_GROUPS, pair.ids_2)):
        assignments = sc.correlation_assignments(groups, ids)
        sc.self_check(document["runs"][0]["results"], tool=THREATS, member_ids=ids, assignments=assignments,
                      resolved_ids=rrs.RESOLVED_IDS, uri=URI)
        by_id = results_by(document)
        for item in specs:
            text = by_id[item["id"]]["message"]["text"]
            assignment = assignments.get(tachi_parts.canonical_finding_id(item["id"]))
            own, sentence = message_parts(text)
            assert sentence == expected_sentence(assignment), (run, item["id"])
            assert text == expected_text(item["threat"], assignment), (run, item["id"])
            texts[(run, item["id"])], owns[(run, item["id"])] = text, own
    for finding_id in ("T-1", "E-5", "AG-1"):
        assert texts[(1, finding_id)] != texts[(2, finding_id)], "%s: a regroup changes its text (ruling C)" % finding_id
        assert owns[(1, finding_id)] == owns[(2, finding_id)], "%s: and only the sentence, never the file's own text" % finding_id


@BOTH_MODES
def test_threats_sarif_an_unchanged_rerun_of_the_generator_keeps_its_keys_and_its_bytes(rrs, tsh, gen, tmp_path, baseline_aware):
    """US-6b #3, FR-E.2: the same inputs give the same keys and the same bytes."""
    pair = run_threats_pair(rrs, tsh, gen, tmp_path, baseline_aware)
    again = pair.project.generate()
    assert again.code == 0, again.describe()
    assert pair.project.sarif_text == pair.second_text
    assert threats_keys(pair.project.sarif) == threats_keys(pair.second)


@BOTH_MODES
def test_threats_sarif_the_hash_recomputes_from_the_tool_and_the_id_and_no_upstream_hash_is_copied(rrs, tsh, gen, tmp_path, baseline_aware):
    """S-6, FR-E.12: the hash is tachi's own. An older model-authored ``threats.sarif`` in the run directory, and a baseline SARIF under
    other hashes, are never read: the old orchestrator wrote hashes of its own, and no result may copy one now."""
    pair = run_threats_pair(rrs, tsh, gen, tmp_path, baseline_aware, plant=True, replace_baseline_sarif=baseline_aware)
    for document, text in ((pair.first, pair.first_text), (pair.second, pair.second_text)):
        for result in document["runs"][0]["results"]:
            written = result["partialFingerprints"]["findingId/v1"]
            assert result["partialFingerprints"]["primaryLocationLineHash"] == recipe(THREATS, tachi_parts.canonical_finding_id(written)), written
        assert not [planted for planted in PLANTED_HASHES if planted in text], "an upstream or earlier hash was copied (S-6)"
        assert "automationDetails" not in text and "runAutomationDetails" not in text, "the upload step's category governs (D7)"
    assert results_by(pair.first)["AGP-01"]["partialFingerprints"]["primaryLocationLineHash"] == recipe(THREATS, "AGP-1"), \
        "the hash is over the canonical ID, and findingId/v1 keeps Section 7's spelling"


def test_threats_sarif_no_stage_reads_a_baseline_sarifs_membership_or_hashes(rrs, tsh, gen, tmp_path):
    """ADR-050 D8: SV-3's trigger does not fire, because no stage reads a baseline SARIF's membership or hashes."""
    pair = run_threats_pair(rrs, tsh, gen, tmp_path, True, replace_baseline_sarif=True)
    assert sorted(threats_keys(pair.second)) == sorted(pair.ids_2), "the member set is Section 7's"
    assert "S-99" not in pair.second_text
    keys_1, keys_2 = threats_keys(pair.first), threats_keys(pair.second)
    assert all(keys_2[finding_id] == keys_1[finding_id] for finding_id in pair.ids_1)


def test_threats_sarif_no_two_present_results_share_a_key_in_a_run_of_forty_two_findings(rrs, tsh, gen, tmp_path):
    text = (rrs.GATED_SUBSET / "baseline" / "threats.md").read_text(encoding="utf-8")
    project = tsh.Project(gen, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 0, res.describe()
    keys = threats_keys(project.sarif)
    assert len(keys) == 42 and len(set(keys.values())) == 42 and len({key[3] for key in keys.values()}) == 42, "42 findings, 42 keys and 42 hashes"


# --- the architecture path: the flag, then the body line, then the default (FR-E.18; D7) --------------------------------

def assert_warned(res, expected):
    """Each warning that the shared resolver gives is on stderr, by its code or its text, and a clean chain is silent."""
    for warning in expected.warnings:
        assert warning["code"] in res.err or warning["detail"] in res.err, "stderr names the failed carrier: %s\n%s" % (warning["code"], res.describe())
    if not expected.warnings:
        assert res.err == "", res.describe()


@pytest.mark.parametrize("flag,body,snapshot,uri,warning_codes", [case[1:] for case in URI_CASES], ids=[case[0] for case in URI_CASES])
def test_threats_sarif_the_flag_then_the_body_line_then_the_default_and_each_failed_carrier_warns(
        rrs, tsh, gen, tmp_path, outside_file, flag, body, snapshot, uri, warning_codes):
    """FR-E.18, in the third file: the generator's own path is the first candidate. A warning never changes its exit code."""
    project = tsh.Project(gen, tmp_path, body_line=body)
    add_architecture_files(project)
    if snapshot:
        (project.out / "architecture.md").write_text("# the snapshot the threat model copied\n", encoding="utf-8")
    candidate = str(outside_file) if flag == "OUTSIDE" else flag
    res = project.generate(architecture=candidate)
    assert res.code == 0, res.describe()
    results = project.sarif["runs"][0]["results"]
    assert {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in results} == {uri}
    expected = sc.resolve_architecture(candidate, threats_text=project.text, run_dir=str(project.out), root=str(tmp_path))
    assert [warning["code"] for warning in expected.warnings] == warning_codes, "the chain is the table's"
    assert_warned(res, expected)
    sc.self_check(results, tool=THREATS, member_ids=[item["id"] for item in rrs.SPECS], assignments={},
                  resolved_ids=rrs.RESOLVED_IDS, uri=uri)


def test_threats_sarif_a_run_always_gets_a_uri_even_when_nothing_validates(rrs, tsh, gen, tmp_path, outside_file):
    project = tsh.Project(gen, tmp_path)
    project.architecture.unlink()
    res = project.generate(architecture=str(outside_file))
    assert res.code == 0, res.describe()
    chain = ["architecture-path:explicit:outside-root", "architecture-path:body-line:absent", "architecture-path:default:missing"]
    expected = sc.resolve_architecture(str(outside_file), threats_text=project.text, run_dir=str(project.out), root=str(tmp_path))
    assert [w["code"] for w in expected.warnings] == chain, "D7's chain, in order"
    assert_warned(res, expected)
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {sc.DEFAULT_ARCHITECTURE_PATH}, "the constant is emitted as written, and nothing here stops a run"


def test_threats_sarif_a_directory_named_with_a_colon_is_written_encoded_and_the_generators_self_check_accepts_it(tsh, gen, tmp_path):
    """SA-11's decoding, as for the other two files: ``a%3Ab`` decodes to a first segment with a colon, which isn't a scheme."""
    project = tsh.Project(gen, tmp_path)
    architecture = project.root / "a:b" / "architecture.md"
    try:
        architecture.parent.mkdir()
        architecture.write_text("# an architecture file in a directory whose name holds a colon\n", encoding="utf-8")
    except OSError:  # pragma: no cover  (a filesystem that cannot name a directory with a colon)
        pytest.skip("this filesystem cannot name a directory with a colon")
    res = project.generate(architecture=str(architecture))
    assert res.code == 0, res.describe()
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {"a%3Ab/architecture.md"}
    assert res.err == ""


@pytest.mark.parametrize("body", ["docs/other/architecture.md", "DOCS/Other/ARCHITECTURE.md"], ids=["canonical", "case-variant"])
def test_threats_sarif_a_case_variant_body_line_gives_every_result_the_same_uri_on_a_case_insensitive_volume(tsh, gen, tmp_path, monkeypatch, body):
    """KB 24 and FR-E.2: the resolver, not the generator, spells the path, so a case variant gives one URI. The fake volume stands in for
    the one an adopter's laptop has, and the generator reaches the filesystem through ``sarif_common.OS_FILESYSTEM`` for it."""
    project = tsh.Project(gen, tmp_path, body_line=body)
    add_architecture_files(project)
    (project.out / "architecture.md").write_text("# the snapshot\n", encoding="utf-8")
    fake = FakeFilesystem(str(tmp_path), case_insensitive=True)
    mirror(fake, tmp_path)
    monkeypatch.setattr(sc, "OS_FILESYSTEM", fake)
    res = project.generate(architecture=False)
    assert res.code == 0, res.describe()
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {"docs/other/architecture.md"}


def test_threats_sarif_a_case_variant_gives_every_result_the_same_uri_on_a_real_case_insensitive_volume(tsh, gen, tmp_path):
    """The same case on the real volume (D16's ``f374-macos`` runs this module alone). Skipped on a case-sensitive volume."""
    if not _case_insensitive(tmp_path):
        pytest.skip("this volume is case-sensitive; the fake filesystem covers the case offline")
    project = tsh.Project(gen, tmp_path, body_line="DOCS/Other/ARCHITECTURE.md")
    add_architecture_files(project)
    (project.out / "architecture.md").write_text("# the snapshot\n", encoding="utf-8")
    res = project.generate(architecture=False)
    assert res.code == 0, res.describe()
    uris = {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.sarif["runs"][0]["results"]}
    assert uris == {"docs/other/architecture.md"}


# --- ruling C: a primary with more than ten peers (PM-T7) ---------------------------------------------------------------

@pytest.mark.parametrize("size,more", [(11, 0), (12, 1), (13, 2)], ids=["ten-peers", "eleven-peers", "twelve-peers"])
def test_threats_sarif_a_primary_with_more_than_ten_peers_names_ten_and_then_a_count(rrs, tsh, gen, tmp_path, size, more):
    """Ruling C's sentence in ``threats.sarif``: the first ten in group order, joined by a comma and a space, then `` and N more``."""
    specs = [rrs.spec("S-%d" % n, "edge-gateway", "Threat %d on the gateway." % n, "Medium", "NEW",
                      "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 0, 0)
             for n in range(1, size + 1)]
    ids = [item["id"] for item in specs]
    project = tsh.Project(gen, tmp_path, specs=specs, resolved=[], groups=[("CG-1", ids)])
    res = project.generate()
    assert res.code == 0, res.describe()
    results = results_by(project.sarif)
    assert len(results) == size, "every peer is a result, once"
    tail = "Correlated in CG-1; peers " + ", ".join(ids[1:11]) + (" and %d more" % more if more else "") + "."
    own, sentence = message_parts(results["S-1"]["message"]["text"])
    assert sentence == tail == ruling_c("CG-1", "S-1", ids[1:])
    assert results["S-1"]["message"]["text"] == "Threat 1 on the gateway. " + tail
    for peer in ids[1:]:
        peer_own, peer_sentence = message_parts(results[peer]["message"]["text"])
        assert peer_sentence == "Correlated in CG-1; primary S-1.", peer
        assert peer_own == "Threat %s on the gateway." % peer[2:], peer
    sc.self_check(project.sarif["runs"][0]["results"], tool=THREATS, member_ids=ids,
                  assignments=sc.correlation_assignments([("CG-1", ids)], ids), resolved_ids=[], uri=URI)


# --- the three files side by side (R-33; FR-E.2's cross-file assertion; D7's re-key table) ----------------------------

def test_the_three_files_have_three_different_tool_and_category_pairs_and_one_result_per_finding_in_each(rrs, entries, tsh, gen, tmp_path):
    """R-33, US-6a #3 and FR-E.2, now on the three files that shipped code writes: the generator runs on the very ``threats.md`` that the
    scorer and the controls stage read. Each finding then has one result per tool, with the same rule, location and correlation outcome and
    three different hashes, and no hash is shared across the files."""
    project = make_project(CONTROLS_FILE, rrs, entries, tmp_path, groups=FIRST_RUN_GROUPS)
    res = project.run()
    assert res.code in RUN_CODES[CONTROLS_FILE], res.describe()
    made = rrs.invoke(gen, ["--threats", project.threats, "--out", project.out, "--architecture", URI], project.root)
    assert made.code == 0, made.describe()
    documents = {THREATS_FILE: json.loads((project.out / THREATS_FILE).read_text(encoding="utf-8")), SCORER_FILE: project.scorer_sarif,
                 CONTROLS_FILE: project.sarif}
    drivers = {name: document["runs"][0]["tool"]["driver"] for name, document in documents.items()}
    assert [drivers[name]["name"] for name in (THREATS_FILE, SCORER_FILE, CONTROLS_FILE)] == ["Tachi", "tachi-risk-scorer", "tachi-control-analyzer"], "verbatim"
    categories = {THREATS_FILE: THREATS_CATEGORY, SCORER_FILE: SCORER_CATEGORY, CONTROLS_FILE: CONTROLS_CATEGORY}
    assert len({(drivers[name]["name"], categories[name]) for name in documents}) == 3, "the three (tool, category) pairs differ"
    assert {driver["informationUri"] for driver in drivers.values()} == {"https://github.com/davidmatousek/tachi"}, "one real URL, in all three"
    for document in documents.values():
        assert "automationDetails" not in document["runs"][0], "the upload step's category governs (D7)"
    found = {name: results_by(document) for name, document in documents.items()}
    assert sorted(found[THREATS_FILE]) == sorted(found[SCORER_FILE]) == sorted(found[CONTROLS_FILE]), "one result per open finding, in each file"
    every_hash = []
    for finding_id in found[THREATS_FILE]:
        canonical = tachi_parts.canonical_finding_id(finding_id)
        hashes = {name: found[name][finding_id]["partialFingerprints"]["primaryLocationLineHash"] for name in documents}
        assert hashes == {THREATS_FILE: recipe(THREATS, canonical), SCORER_FILE: recipe(SCORER, canonical),
                          CONTROLS_FILE: recipe(CONTROLS, canonical)}, finding_id
        assert len(set(hashes.values())) == 3, "one finding, three files, three hashes"
        every_hash += list(hashes.values())
        rules = {found[name][finding_id]["ruleId"] for name in documents}
        assert rules == {EXPECTED_RULES[canonical.partition("-")[0]]}, "the rule is a function of the finding, shared by the files (ADR-013 D2)"
        places = [found[name][finding_id]["locations"][0]["physicalLocation"] for name in documents]
        assert places[0] == places[1] == places[2], "and so is the location"
        outcomes = {name: tuple(found[name][finding_id]["properties"].get(key) for key in sc.CORRELATION_KEYS) for name in documents}
        assert len(set(outcomes.values())) == 1, "%s: the correlation outcome is one, in each file: %s" % (finding_id, outcomes)
        tails = {name: message_parts(found[name][finding_id]["message"]["text"])[1] for name in documents}
        assert len(set(tails.values())) == 1, "and so is ruling C's sentence: %s" % tails
    assert len(set(every_hash)) == len(every_hash), "no hash is shared across the files"


# --- FR-E.13: the regroup pair's correlation outcome is unchanged (S-7) -------------------------------------------------

def groups_in(results):
    """``{group: (primary, {members})}`` as the results' correlation properties give them."""
    found = {}
    for finding_id, result in results.items():
        properties = result["properties"]
        if "correlation-group" in properties:
            primary, members = found.setdefault(properties["correlation-group"], [properties["correlation-primary"], set()])
            assert properties["correlation-primary"] == primary, "one primary per group"
            members.add(finding_id)
    return {group: (primary, members) for group, (primary, members) in found.items()}


def test_fr_e13_the_regroup_pairs_correlation_outcome_is_the_committed_one_whatever_the_sarif_recipe_does(tsh, gen, tmp_path):
    """Phase 3's baseline correlation keeps matching findings as it does today (FR-E.13, spec S-7). The pair commits that outcome: which
    findings group, and each group's primary, per run. It is read three ways, and all three are one. Section 4a through the shared
    parser is what correlation starts from, and the new recipe never feeds it. The generator's file says the same, in its properties. And
    a baseline SARIF in the old recipe, planted where an earlier run left its file, changes no byte of any run's output: no stage reads
    a baseline SARIF's hashes."""
    outcomes = json.loads((tsh.PAIR / "expected-outcomes.json").read_text(encoding="utf-8"))
    pinned = {name: {group["id"]: (group["primary"], set(group["members"])) for group in outcomes["runs"][name]["groups"]}
              for name in ("run1", "run2", "run3")}
    for name in pinned:
        read = tsh.reference_of((tsh.PAIR / name / "threats.md").read_text(encoding="utf-8"))
        assert {group["group_id"]: (group["primary"], set(group["members"])) for group in read.groups} == pinned[name], \
            "%s: Section 4a gives the committed groups and primaries" % name
    scenario = tsh.copy_pair(tmp_path)
    first = tsh.generate_pair(gen, scenario)
    for name, run in first.items():
        assert groups_in(run.results) == pinned[name], "%s: the generator's properties give the same outcome" % name
    legacy = (tsh.GATED_SUBSET / "baseline" / "threats.sarif").read_bytes()  # a model-authored file: the old recipe, a collapsed key and its own hashes

    def plant_the_old_recipe(root, current):
        for earlier in ("baseline", "run1", "run2", "run3"):
            if earlier != current:
                (Path(root) / earlier / THREATS_FILE).write_bytes(legacy)

    again = tsh.generate_pair(gen, scenario, plant=plant_the_old_recipe)
    for name in pinned:
        assert again[name].text == first[name].text, "%s: an old baseline SARIF moved a byte" % name
        assert groups_in(again[name].results) == pinned[name]
