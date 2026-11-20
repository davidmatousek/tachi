#!/usr/bin/env python3
"""check-agent-privileges.py -- CI privilege guard for tachi agents and commands (Feature 391, T025).

Pins what ``docs/standards/CLAUDE_PERMISSIONS.md`` section 8 (the privilege
matrix) says about tachi's agents and commands to what the files under
``.claude/agents/tachi/`` and ``.claude/commands/tachi.*.md`` actually declare,
so a privilege change cannot land unseen. It is a drift guard: it makes a change
visible in review and in CI. It sandboxes nothing (the matrix legend separates
what Claude Code enforces from what is only declared).

Checks (all run, all reported; contract: specs/391-isolated-auditable-operation/
contracts/cli-contracts.md, plan AD-3 and AD-8):

  C1 roster       Bidirectional. Walk the agents directory recursively. Only ``*.md``
                  files are allowed; any other *tracked* file is red (``git ls-files``
                  when the repo root has a ``.git``, and untracked junk such as
                  ``.DS_Store`` is then ignored; with no git tree every other file is
                  red, bar ``.DS_Store``, ``Thumbs.db`` and ``desktop.ini``). A symlink
                  anywhere is red. A file with leading YAML
                  frontmatter (BOM, blank lines and CRLF tolerated) is an agent
                  candidate: ``name:`` must be ``tachi-*``, unique and have a section 8
                  row. A file without frontmatter is allowed only when it is on the
                  allow-list (``_TACHI_AGENT_BEST_PRACTICES.md``), so an allow-listed
                  name that gains frontmatter is classified as an agent candidate.
                  Every section 8 row must have a file.
  C2 tools        ``tools:`` equals the row's Tools cell, as sets. Block list, flow
                  list and comma string are parsed; any other shape exits 2.
  C3 model        ``model:`` equals the row's Model cell.
  C4 key set      The frontmatter keys are exactly {name, description, tools, model}.
  C5 commands     Each ``.claude/commands/tachi.*.md`` has a row in the commands table
                  and its frontmatter keys equal the row's Frontmatter keys cell (and
                  every row has a file). Keys only: no command sets ``allowed-tools``
                  or ``model`` today, so their values are not compared.
  C6 bash         The command families in fences labelled bash, sh, shell or zsh
                  (indented fences included; unlabelled fences are out of scope) of the
                  Bash-capable agents (``Bash`` in the file's tools or the row's) must be
                  a subset of the row's Bash families cell. Backslash continuations are
                  joined; each line is tokenized with ``shlex.shlex(posix=True,
                  punctuation_chars=True)`` and ``whitespace_split``; ``&&``, ``||``,
                  ``;``, ``|`` (and ``&``, ``|&``) split commands; leading ``VAR=value``
                  words and the shell reserved words (if then elif else fi for while until
                  do done case esac in ! { } [[ ]]) are skipped so the next word is the
                  family (``[`` and ``test`` are families). ``$(``, backticks, ``eval``,
                  ``bash -c``, ``sh -c`` and ``xargs`` are red, with no construct
                  allow-list in 391; so are process substitution (``<(``, ``>(``) and
                  ``-c`` on dash, ksh and zsh. ``$(`` and backticks are looked for on the raw
                  line, so quoting does not hide them. Prose is never scanned.
  C7 writes       The set of Path tokens in the runbook's section 5 table equals the
                  union of the Writes cells of the section 8 agents and commands tables.
                  The section 8.5 canonical table is held to the same union.
  C8 self-test    ``--self-test``: after C1-C7, copy the inputs to a temp directory and
                  apply five mutations (a tool added; a planted ``name: helper``; an
                  unlisted file without frontmatter; a duplicate name; the allow-listed
                  file with planted frontmatter). Each mutated copy must gain a finding,
                  in the expected check and file, that the unmutated copy lacked; one that
                  does not is exit 2, unless that check and file is already red in the
                  unmutated copy (reported as "already red", not a failure: the tree is red
                  and exit 1 lists the finding). The tool is added to an agent that has a
                  section 8 row, so a planted rowless agent cannot become the target. It
                  runs on a drifted tree too, and is skipped only when C1-C7 hit an
                  infrastructure error.

Section 8 is parsed between ``## 8.`` and the next level-2 heading (today
``## Cross-references``). Tables are found by their exact header row and cells follow
the section 8.2 syntax (backticked tokens separated by a comma and a space, a single
em dash for the empty set). The runbook's table sits under ``## 5. Write locations``.

Exit codes:
  0  every check passed (with --self-test: and every mutation was detected)
  1  drift: at least one finding; each is listed with its check id and file
  2  infrastructure: matrix, runbook or section missing; a cell, frontmatter or
     ``tools:`` shape the guard cannot parse (a duplicate key, a multi-line value, an
     alias, a flow mapping); an unreadable input or a git failure; a self-test
     mutation that failed to fail (not one that is already red); or a bug in the
     guard itself

``--json`` prints ``json.dumps(summary, sort_keys=True, indent=2)`` where the summary is
``{status: pass|drift|infra, roster: {agents, allowlisted, red}, drift: [{agent, check,
expected, actual, ...}], self_test: pass|fail|skipped|null, ...}`` (data-model.md,
GuardResult) plus ``violations`` (every finding with its check id), ``infra`` (every
exit-2 cause), ``bash_families`` (the families found and allowed per Bash-capable
agent) and, with ``--self-test``, ``self_test_detail`` (per mutation: id, mutation,
expected_check, expected_file, exit_code, detected, already_red). Human output goes to
stdout, infrastructure errors to stderr, both with a ``[391]`` prefix.

Constraints: stdlib only, Python >= 3.9, no network, reads the tree and writes
nothing outside the temp directory that --self-test uses.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

PREFIX = "[391]"
DEFAULT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MATRIX = "docs/standards/CLAUDE_PERMISSIONS.md"
DEFAULT_AGENTS_DIR = ".claude/agents/tachi"
DEFAULT_COMMANDS_GLOB = ".claude/commands/tachi.*.md"
DEFAULT_RUNBOOK = "docs/guides/ISOLATED_OPERATION_TACHI.md"

AGENT_KEYS = frozenset({"name", "description", "tools", "model"})
ALLOW_LISTED_DOCS = frozenset({"_TACHI_AGENT_BEST_PRACTICES.md"})
NAME_PREFIX = "tachi-"
OS_JUNK = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})   # never red when there is no git tree to ask
SHELL_FENCE_LABELS = frozenset({"bash", "sh", "shell", "zsh"})
RESERVED_WORDS = frozenset(
    "if then elif else fi for while until do done case esac in ! { } [[ ]]".split()
)
SHELL_PROGRAMS = frozenset({"bash", "sh", "zsh", "dash", "ksh"})

AGENTS_HEADER = ["Agent", "Tier", "Tools", "Model", "Bash families", "Writes", "Hosts"]
COMMANDS_HEADER = [
    "Command", "Frontmatter keys", "Dispatches", "Bash it instructs", "Writes", "Child processes",
]
WRITES_HEADER = ["Path", "Written by", "Condition"]

# Check id -> the word the GuardResult drift entries use (data-model.md).
CHECK_WORD = {
    "C1": "roster", "C2": "tools", "C3": "model", "C4": "keyset",
    "C5": "command", "C6": "bash", "C7": "writes",
}
ALL_CHECKS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")
CHECK_LABEL = {
    "C1": "roster", "C2": "tools", "C3": "model", "C4": "frontmatter keys",
    "C5": "command keys", "C6": "bash families", "C7": "write locations",
}

_EM_DASH = chr(0x2014)
_PUNCT_CHARS = frozenset("();<>|&")
# A quoted or escaped metacharacter is swapped for a private-use stand-in before tokenizing, so a
# lone ';' or '|' that is data (not an operator) stays a word; shlex's posix mode drops the quotes.
_STAND_IN = {c: chr(0xE000 + i) for i, c in enumerate(";|&()<>")}
_RESTORE = {ord(v): k for k, v in _STAND_IN.items()}
_REDIRECTIONS = re.compile(r"&>>|&>|<<<|<<-|>>|<<|>&|<&|>\||<>|>|<")
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_SHELL_C_FLAG = re.compile(r"^-[A-Za-z]*c[A-Za-z]*$")
# A fence opens after optional indentation, blockquote markers and list markers.
_FENCE = re.compile(
    r"^(?P<prefix>(?:[ \t]*(?:>|[-*+](?=[ \t])|\d{1,9}[.)](?=[ \t])))*[ \t]*)"
    r"(?P<marker>`{3,}|~{3,})[ \t]*(?P<info>[^`]*)$"
)
_QUOTE_PREFIX = re.compile(r"^[ \t]*(?:>[ \t]?)+")
_KEY_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*)[ \t]*:(?:[ \t]+(.*))?$")
_SET_CELL = re.compile(r"`[^`|]+`(?:, `[^`|]+`)*")
_SINGLE_CELL = re.compile(r"`([^`|]+)`")
_YAML_INDICATORS = frozenset("&*!|>%@`")


class InfraError(Exception):
    """An input the guard cannot interpret (exit 2); not a drift finding."""


# --------------------------------------------------------------------------- report


class Report:
    """Findings (drift, exit 1) and infrastructure errors (exit 2) of one run."""

    def __init__(self):
        self.findings = []   # dicts: check_id, file, message, agent, expected, actual
        self.infra = []      # dicts: check_id, file, message
        self.agent_files = []
        self.allowlisted = []
        self.matrix = None   # the parsed section 8 matrix; stays None when it could not be read
        self.bash = {}       # agent name -> {"found": [...], "allowed": [...]}
        self.counts = {"agents": 0, "commands": 0, "paths": 0, "bash_agents": 0}

    def red(self, check_id, file, message, agent=None, expected=None, actual=None):
        self.findings.append({
            "check_id": check_id, "file": file, "message": message,
            "agent": agent, "expected": expected, "actual": actual,
        })

    def broken(self, check_id, file, message):
        self.infra.append({"check_id": check_id, "file": file, "message": message})

    def status(self):
        if self.infra:
            return "infra"
        return "drift" if self.findings else "pass"

    def check_status(self, check_id):
        if any(i["check_id"] in (check_id, "MATRIX") for i in self.infra):
            return "infra"
        return "fail" if any(f["check_id"] == check_id for f in self.findings) else "pass"


class Ctx:
    """The inputs of one run; each path is kept relative to the repo root (an absolute one is converted)."""

    def __init__(self, root, matrix, agents_dir, commands_glob, runbook):
        self.root = Path(root)

        def norm(p):
            if not os.path.isabs(p):
                return p
            parent, name = os.path.split(p)   # resolve the parent only: the last part may be a symlink to report
            real = os.path.join(os.path.realpath(parent), name)
            return Path(os.path.relpath(real, os.path.realpath(str(self.root)))).as_posix()

        self.matrix_rel = norm(matrix)
        self.agents_rel = norm(agents_dir)
        self.commands_glob = norm(commands_glob)
        self.runbook_rel = norm(runbook)
        self.matrix_path = self.root / self.matrix_rel
        self.agents_dir = self.root / self.agents_rel
        self.runbook_path = self.root / self.runbook_rel

    def rel(self, path):
        return Path(os.path.relpath(str(path), str(self.root))).as_posix()


# --------------------------------------------------------------------------- text helpers


def _read_text(path):
    """UTF-8 text with the BOM dropped and every newline normalised to LF."""
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise InfraError(f"cannot read file: {exc}")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InfraError(f"file is not valid UTF-8: {exc}")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def scan_fences(lines):
    """Fenced code blocks as (open_index, close_index, info, quoted); an unclosed fence runs to EOF.

    ``quoted`` is true when the opening line sits in a blockquote, so the block's lines carry the
    ``>`` prefix too.
    """
    fences = []
    i, n = 0, len(lines)
    while i < n:
        m = _FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        marker, info = m.group("marker"), m.group("info").strip()
        quoted = ">" in m.group("prefix")
        j = i + 1
        while j < n:
            s = (_QUOTE_PREFIX.sub("", lines[j]) if quoted else lines[j]).strip()
            if len(s) >= len(marker) and set(s) == {marker[0]}:
                break
            j += 1
        fences.append((i, j, info, quoted))
        i = j + 1
    return fences


def fence_mask(lines):
    mask = [False] * len(lines)
    for open_i, close_i, _info, _quoted in scan_fences(lines):
        for k in range(open_i, min(close_i, len(lines) - 1) + 1):
            mask[k] = True
    return mask


def _table_cells(line):
    s = line.strip()
    if len(s) < 2 or s[0] != "|" or s[-1] != "|":
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def _find_table(lines, mask, header, label):
    """Rows (line_number, cells) of the one table with this exact header row."""
    found = []
    i = 0
    while i < len(lines):
        cells = None if mask[i] else _table_cells(lines[i])
        if cells is None or [re.sub(r"\s+", " ", c) for c in cells] != header:
            i += 1
            continue
        sep = _table_cells(lines[i + 1]) if i + 1 < len(lines) else None
        if sep is None or len(sep) != len(header) or not all(
            re.fullmatch(r":?-+:?", c) for c in sep
        ):
            raise InfraError(f"{label}: the header row is not followed by a separator row")
        rows = []
        j = i + 2
        while j < len(lines) and not mask[j]:
            row = _table_cells(lines[j])
            if row is None:
                break
            if len(row) != len(header):
                raise InfraError(
                    f"{label}: line {j + 1} has {len(row)} cells, the header has {len(header)}"
                )
            rows.append((j + 1, row))
            j += 1
        found.append(rows)
        i = j
    if not found:
        raise InfraError(f"{label} not found (header row: | {' | '.join(header)} |)")
    if len(found) > 1:
        raise InfraError(f"{label} appears {len(found)} times; the guard needs exactly one")
    return found[0]


def _set_cell(cell, where):
    """Tokens of a set-valued cell (section 8.2): `a`, `b` or a single em dash."""
    if cell == _EM_DASH:
        return []
    if not _SET_CELL.fullmatch(cell):
        raise InfraError(
            f"{where}: cell {cell[:70]!r} breaks the set syntax (backticked tokens "
            f"separated by a comma and a space, or a single em dash)"
        )
    tokens = _SINGLE_CELL.findall(cell)
    if len(set(tokens)) != len(tokens):
        raise InfraError(f"{where}: cell repeats a token: {cell[:70]!r}")
    return tokens


def _single_cell(cell, where):
    m = re.fullmatch(r"`([^`|]+)`", cell)
    if not m:
        raise InfraError(f"{where}: cell {cell[:70]!r} is not exactly one backticked token")
    return m.group(1)


def _section(lines, mask, start_pattern, label):
    """Line range (start+1, end) of the section whose level-2 heading matches start_pattern."""
    starts = [i for i, ln in enumerate(lines) if not mask[i] and re.match(start_pattern, ln)]
    if not starts:
        raise InfraError(f"{label}: heading not found")
    if len(starts) > 1:
        raise InfraError(f"{label}: heading appears {len(starts)} times")
    end = next(
        (j for j in range(starts[0] + 1, len(lines)) if not mask[j] and re.match(r"^##\s", lines[j])),
        len(lines),
    )
    return starts[0] + 1, end


# --------------------------------------------------------------------------- matrix (section 8)


class AgentRow:
    def __init__(self, tools, model, bash, writes):
        self.tools, self.model, self.bash, self.writes = (
            frozenset(tools), model, frozenset(bash), frozenset(writes),
        )


class CommandRow:
    def __init__(self, keys, writes):
        self.keys, self.writes = frozenset(keys), frozenset(writes)


class Matrix:
    def __init__(self):
        self.agents = {}      # name -> AgentRow
        self.commands = {}    # "/tachi.x" -> CommandRow
        self.canonical = []   # section 8.5 Path tokens, in table order

    def writes_union(self):
        union = set()
        for row in list(self.agents.values()) + list(self.commands.values()):
            union |= row.writes
        return union


def parse_matrix(text):
    lines = text.split("\n")
    mask = fence_mask(lines)
    first, last = _section(lines, mask, r"^## 8\.(\s|$)", "section 8")
    region, rmask = lines[first:last], mask[first:last]
    matrix = Matrix()
    for lineno, c in _find_table(region, rmask, AGENTS_HEADER, "section 8.3 agents table"):
        where = f"agents table, line {first + lineno}"
        name = _single_cell(c[0], f"{where}, Agent")
        if name in matrix.agents:
            raise InfraError(f"agents table lists {name} twice")
        matrix.agents[name] = AgentRow(
            _set_cell(c[2], f"{where} ({name}), Tools"),
            _single_cell(c[3], f"{where} ({name}), Model"),
            _set_cell(c[4], f"{where} ({name}), Bash families"),
            _set_cell(c[5], f"{where} ({name}), Writes"),
        )
    for lineno, c in _find_table(region, rmask, COMMANDS_HEADER, "section 8.4 commands table"):
        where = f"commands table, line {first + lineno}"
        cmd = _single_cell(c[0], f"{where}, Command")
        if not re.fullmatch(r"/tachi\.[A-Za-z0-9._-]+", cmd):
            raise InfraError(f"{where}: command cell {cmd!r} is not /tachi.<name>")
        if cmd in matrix.commands:
            raise InfraError(f"commands table lists {cmd} twice")
        matrix.commands[cmd] = CommandRow(
            _set_cell(c[1], f"{where} ({cmd}), Frontmatter keys"),
            _set_cell(c[4], f"{where} ({cmd}), Writes"),
        )
    for lineno, c in _find_table(region, rmask, WRITES_HEADER, "section 8.5 write-locations table"):
        matrix.canonical.append(_single_cell(c[0], f"section 8.5, line {first + lineno}, Path"))
    return matrix


def parse_runbook_paths(text):
    """Path tokens of the runbook's section 5 write-locations table, in table order."""
    lines = text.split("\n")
    mask = fence_mask(lines)
    first, last = _section(lines, mask, r"^## 5\.\s+Write locations\s*$", "runbook section 5")
    rows = _find_table(
        lines[first:last], mask[first:last], WRITES_HEADER, "runbook section 5 write-locations table"
    )
    return [_single_cell(c[0], f"runbook section 5, line {first + n}, Path") for n, c in rows]


# --------------------------------------------------------------------------- frontmatter


def split_frontmatter(lines):
    """(open_index, close_index) of leading frontmatter, or None when there is none.

    Lenient on the way in (blank lines before the opening delimiter; the BOM and CRLF are
    already gone), strict on the way out: an opening delimiter with no closing one is
    infrastructure, not "no frontmatter".
    """
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or lines[i].strip() != "---":
        return None
    for j in range(i + 1, len(lines)):
        if lines[j].strip() in ("---", "..."):
            return i, j
    raise InfraError("frontmatter opens with --- but never closes")


def _strip_comment(s):
    """Drop a trailing YAML comment (a # at the start or after whitespace, outside quotes)."""
    quote, esc = "", False
    for i, ch in enumerate(s):
        if esc:
            esc = False
        elif quote:
            if ch == "\\" and quote == '"':
                esc = True
            elif ch == quote:
                quote = ""
        elif ch in "\"'" and (i == 0 or s[i - 1] in " \t[,"):
            quote = ch
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i]
    return s


def parse_entries(lines, first, last):
    """Top-level keys of the frontmatter body lines[first:last], strictly.

    An entry is {key, inline, cont, start, end}. A line the parser does not understand is
    infrastructure (fail closed): a quoted key, a duplicate key, a stray list item. A
    duplicate key is refused outright, because two parsers may disagree on which one wins.
    """
    entries = []
    for idx in range(first, last):
        raw = lines[idx]
        if not raw.strip():
            continue
        if raw[0] in " \t":
            if not entries:
                raise InfraError(f"line {idx + 1}: indented line before any key")
            entries[-1]["cont"].append(raw)
            continue
        if raw.startswith("#"):
            continue
        m = _KEY_LINE.match(raw.rstrip())
        if m:
            if any(e["key"] == m.group(1) for e in entries):
                raise InfraError(f"line {idx + 1}: duplicate frontmatter key {m.group(1)!r}")
            if entries:
                entries[-1]["end"] = idx
            entries.append({
                "key": m.group(1), "inline": m.group(2) or "", "cont": [],
                "start": idx, "end": last,
            })
            continue
        if (raw.startswith("- ") or raw.rstrip() == "-") and entries and not _strip_comment(
            entries[-1]["inline"]
        ).strip():
            entries[-1]["cont"].append(raw)
            continue
        raise InfraError(f"line {idx + 1}: unsupported frontmatter line {raw[:50]!r}")
    return entries


def _content_lines(entry):
    return [c for c in entry["cont"] if c.strip() and not c.lstrip().startswith("#")]


def _item(token, what):
    """One scalar item: plain or quoted; anything structural is infrastructure."""
    t = token.strip()
    if not t:
        raise InfraError(f"{what}: empty item")
    if t[0] in "\"'":
        if len(t) < 2 or t[-1] != t[0]:
            raise InfraError(f"{what}: unterminated quoted item {t!r}")
        inner = t[1:-1]
        if t[0] == "'":
            inner = inner.replace("''", "'")
        elif "\\" in inner:
            raise InfraError(f"{what}: escape sequence in quoted item {t!r}")
        if t[0] in inner or not inner.strip():
            raise InfraError(f"{what}: unsupported quoted item {t!r}")
        return inner
    if t[0] in _YAML_INDICATORS or t[0] in "{[" or t.startswith("- ") or t == "-":
        raise InfraError(f"{what}: unsupported YAML shape {t[:30]!r}")
    if "{" in t or "[" in t or "]" in t or "}" in t:
        raise InfraError(f"{what}: nested collection in item {t[:30]!r}")
    if re.search(r":(\s|$)", t):
        raise InfraError(f"{what}: mapping-shaped item {t[:30]!r}")
    return t


def _split_commas(text):
    parts, cur, quote = [], [], ""
    for ch in text:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = ""
        elif ch in "\"'" and not "".join(cur).strip():
            quote = ch
            cur.append(ch)
        elif ch == ",":
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if quote:
        raise InfraError("unterminated quote in a comma-separated value")
    parts.append("".join(cur))
    if len(parts) > 1 and not parts[-1].strip():
        parts.pop()   # one trailing comma is harmless
    return parts


def parse_tools(entry):
    """The tools of a ``tools:`` entry: block list, flow list or comma string; else InfraError."""
    inline = _strip_comment(entry["inline"]).strip()
    content = _content_lines(entry)
    what = "`tools:`"
    if not inline:
        if not content:
            raise InfraError("`tools:` has no value")
        items = []
        for c in content:
            m = re.match(r"^\s*-(?:\s+(.*))?$", c)
            if not m:
                raise InfraError(f"`tools:` block list line is not '- item': {c.strip()[:40]!r}")
            items.append(_item(_strip_comment(m.group(1) or ""), what))
        return items
    if content:
        raise InfraError("`tools:` value continues on later lines (unsupported shape)")
    if inline[0] == "[":
        if not inline.endswith("]"):
            raise InfraError("`tools:` flow list must close on the same line")
        inner = inline[1:-1]
        return [] if not inner.strip() else [_item(p, what) for p in _split_commas(inner)]
    if inline[0] == "{" or inline[0] in _YAML_INDICATORS:
        raise InfraError(f"`tools:` shape {inline[:30]!r} is not a list or a comma string")
    text = _item(inline, what) if inline[0] in "\"'" else inline
    return [_item(p, what) for p in _split_commas(text)]


def parse_scalar(entry, what):
    inline = _strip_comment(entry["inline"]).strip()
    if not inline:
        raise InfraError(f"`{what}:` has no inline value")
    if _content_lines(entry):
        raise InfraError(f"`{what}:` value continues on later lines (unsupported shape)")
    return _item(inline, f"`{what}:`")


class AgentFile:
    def __init__(self, path, rel, rel_in, lines, entries):
        self.path, self.rel, self.rel_in, self.lines = path, rel, rel_in, lines
        self.keys = [e["key"] for e in entries]
        self.entries = {e["key"]: e for e in entries}
        self.name = self.tools = self.model = None


def load_agent_file(path, rel, rel_in):
    """An AgentFile for a file with leading frontmatter; None for one without."""
    lines = _read_text(path).split("\n")
    span = split_frontmatter(lines)
    if span is None:
        return None
    return AgentFile(path, rel, rel_in, lines, parse_entries(lines, span[0] + 1, span[1]))


# --------------------------------------------------------------------------- C1 roster


def tracked_files(root, rel_dir):
    """Tracked paths below rel_dir (posix, relative to root), or None when root has no .git."""
    if not (root / ".git").exists():
        return None
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX")}
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", rel_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise InfraError(f"cannot run git ls-files: {exc}")
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip()[:200]
        raise InfraError(f"git ls-files failed (exit {proc.returncode}): {detail}")
    return {p for p in proc.stdout.decode("utf-8", "surrogateescape").split("\0") if p}


def _walk(directory):
    """Every entry below directory as (path, kind); kind is file, symlink or other. No symlink is followed."""
    out, stack = [], [directory]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda e: e.name)
        except OSError as exc:
            raise InfraError(f"cannot list {current}: {exc}")
        for e in entries:
            if e.is_symlink():
                out.append((Path(e.path), "symlink"))
            elif e.is_dir(follow_symlinks=False):
                stack.append(Path(e.path))
            elif e.is_file(follow_symlinks=False):
                out.append((Path(e.path), "file"))
            else:
                out.append((Path(e.path), "other"))
    return sorted(out, key=lambda t: str(t[0]))


def check_roster(ctx, matrix, rep):
    """C1. Returns the agent candidates (files with leading frontmatter)."""
    agents_rel = ctx.agents_rel.rstrip("/")
    if os.path.islink(ctx.agents_dir):
        rep.red("C1", agents_rel, "the agents directory is a symlink (symlinks are not allowed)")
    if not ctx.agents_dir.is_dir():
        rep.broken("C1", agents_rel, "agents directory not found")
        return []
    try:
        tracked = tracked_files(ctx.root, ctx.rel(ctx.agents_dir))
    except InfraError as exc:
        rep.broken("C1", agents_rel, str(exc))
        return []
    candidates = []
    try:
        entries = _walk(ctx.agents_dir)
    except InfraError as exc:
        rep.broken("C1", agents_rel, str(exc))
        return []
    for path, kind in entries:
        rel = ctx.rel(path)
        rel_in = Path(os.path.relpath(str(path), str(ctx.agents_dir))).as_posix()
        if kind == "symlink":
            rep.red("C1", rel, "symlink in the agents directory (symlinks are not allowed)")
        elif kind == "other":
            rep.red("C1", rel, "not a regular file")
        elif not rel_in.endswith(".md"):
            # tracked per git; with no git tree to ask, everything counts except known OS junk
            counts = rel in tracked if tracked is not None else path.name not in OS_JUNK
            if counts:
                rep.red("C1", rel, "tracked non-.md file in the agents directory (only *.md files are allowed)")
        else:
            try:
                af = load_agent_file(path, rel, rel_in)
            except InfraError as exc:
                rep.broken("C1", rel, str(exc))
                continue
            if af is None:
                if rel_in in ALLOW_LISTED_DOCS:
                    rep.allowlisted.append(rel)
                else:
                    rep.red("C1", rel, ".md file without frontmatter that is not on the allow-list "
                            f"({', '.join(sorted(ALLOW_LISTED_DOCS))})")
            else:
                candidates.append(af)
    by_name = {}
    for af in candidates:
        if af.rel_in in ALLOW_LISTED_DOCS:
            rep.red("C1", af.rel, "allow-listed document has leading frontmatter, so it is an "
                    "agent candidate and must meet the agent rules")
        if "name" not in af.entries:
            rep.red("C1", af.rel, "frontmatter has no name: key")
            continue
        try:
            af.name = parse_scalar(af.entries["name"], "name")
        except InfraError as exc:
            rep.broken("C1", af.rel, str(exc))
            continue
        if not af.name.startswith(NAME_PREFIX):
            rep.red("C1", af.rel, f"agent name {af.name!r} does not start with {NAME_PREFIX!r}", agent=af.name)
        by_name.setdefault(af.name, []).append(af)
    for name, group in sorted(by_name.items()):
        if len(group) > 1:
            for af in group:
                others = ", ".join(o.rel for o in group if o is not af)
                rep.red("C1", af.rel, f"duplicate agent name {name!r} (also in: {others})", agent=name)
        if name not in matrix.agents:
            for af in group:
                rep.red("C1", af.rel, f"agent {name!r} has no row in the section 8 agents table", agent=name)
    for name in sorted(matrix.agents):
        if name not in by_name:
            rep.red("C1", agents_rel, f"section 8 row {name!r} has no agent file under {agents_rel}/", agent=name)
    return candidates


# --------------------------------------------------------------------------- C2, C3, C4


def check_frontmatter(matrix, candidates, rep):
    for af in candidates:
        subject = af.name or af.rel
        row = matrix.agents.get(af.name) if af.name else None
        keys = set(af.keys)
        if keys != AGENT_KEYS:
            rep.red(
                "C4", af.rel,
                f"frontmatter keys differ from {{{', '.join(sorted(AGENT_KEYS))}}}: "
                f"missing {sorted(AGENT_KEYS - keys)}, unexpected {sorted(keys - AGENT_KEYS)}",
                agent=subject, expected=sorted(AGENT_KEYS), actual=sorted(keys),
            )
        if "tools" in af.entries:
            try:
                af.tools = parse_tools(af.entries["tools"])
            except InfraError as exc:
                rep.broken("C2", af.rel, str(exc))
        if "model" in af.entries:
            try:
                af.model = parse_scalar(af.entries["model"], "model")
            except InfraError as exc:
                rep.broken("C3", af.rel, str(exc))
        if row is None:
            continue
        if "tools" not in af.entries:
            rep.red("C2", af.rel, "no tools: key (an agent without tools: inherits every tool); "
                    f"section 8 lists {sorted(row.tools)}", agent=subject,
                    expected=sorted(row.tools), actual=None)
        elif af.tools is not None and set(af.tools) != row.tools:
            have, want = set(af.tools), row.tools
            rep.red(
                "C2", af.rel,
                f"tools differ from the section 8 row {af.name!r}: file has {sorted(have)}, matrix "
                f"has {sorted(want)} (added {sorted(have - want)}, removed {sorted(want - have)})",
                agent=subject, expected=sorted(want), actual=sorted(have),
            )
        if "model" not in af.entries:
            rep.red("C3", af.rel, f"no model: key; section 8 lists {row.model!r}", agent=subject,
                    expected=row.model, actual=None)
        elif af.model is not None and af.model != row.model:
            rep.red("C3", af.rel, f"model {af.model!r} differs from the section 8 row {af.name!r} "
                    f"({row.model!r})", agent=subject, expected=row.model, actual=af.model)


# --------------------------------------------------------------------------- C5 commands


def check_commands(ctx, matrix, rep):
    pattern = os.path.join(glob.escape(str(ctx.root)), ctx.commands_glob)
    seen = set()
    for p in sorted(glob.glob(pattern)):
        path = Path(p)
        if not path.is_file():
            continue
        rel = ctx.rel(path)
        cmd = "/" + (path.name[:-3] if path.name.endswith(".md") else path.name)
        seen.add(cmd)
        try:
            lines = _read_text(path).split("\n")
            span = split_frontmatter(lines)
            keys = set() if span is None else {
                e["key"] for e in parse_entries(lines, span[0] + 1, span[1])
            }
        except InfraError as exc:
            rep.broken("C5", rel, str(exc))
            continue
        rep.counts["commands"] += 1
        row = matrix.commands.get(cmd)
        if row is None:
            rep.red("C5", rel, f"command {cmd} has no row in the section 8 commands table", agent=cmd)
        elif keys != row.keys:
            # AOD-SIMPLIFICATION: keys only, values are not compared (no command sets allowed-tools
            # or model in 391) -- upgrade: pin the values when a command starts to declare them
            rep.red("C5", rel, f"command {cmd} frontmatter keys {sorted(keys)} differ from the "
                    f"section 8 row {sorted(row.keys)}", agent=cmd,
                    expected=sorted(row.keys), actual=sorted(keys))
    for cmd in sorted(matrix.commands):
        if cmd not in seen:
            rep.red("C5", ctx.matrix_rel, f"section 8 row {cmd} has no command file matching "
                    f"{ctx.commands_glob}", agent=cmd)


# --------------------------------------------------------------------------- C6 bash families


def _logical_lines(body, base):
    """(file_line_number, text) of each shell command line of a fence body, continuations joined.

    ``base`` is the file line number of ``body[0]``. A backslash that ends a comment is part of
    the comment and continues nothing.
    """
    buf, first = "", None
    for idx, line in enumerate(body):
        if first is None:
            first = base + idx
        cur = buf + line
        in_comment = _scan_shell(cur)[1]
        trailing = len(cur) - len(cur.rstrip("\\"))
        if trailing % 2 == 1 and not in_comment:
            buf = cur[:-1]
            continue
        yield first, cur
        buf, first = "", None
    if first is not None:
        yield first, buf


def _scan_shell(text):
    """(code, had_comment): the text up to a shell comment, metacharacters that are data protected.

    A comment is a # outside quotes at the start of a word. Inside quotes, or after a backslash, each
    of ``; | & ( ) < >`` is replaced by a stand-in (see _STAND_IN).
    """
    out, quote, esc, prev = [], "", False, " "
    for i, ch in enumerate(text):
        if esc:
            esc = False
            out.append(_STAND_IN.get(ch, ch))
        elif quote:
            if quote == '"' and ch == "\\":
                esc = True
                out.append(ch)
            elif ch == quote:
                quote = ""
                out.append(ch)
            else:
                out.append(_STAND_IN.get(ch, ch))
        elif ch == "\\":
            esc = True
            out.append(ch)
        elif ch in "'\"":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or prev in " \t;&|()<>"):
            return "".join(out), True
        else:
            out.append(ch)
        prev = ch
    return "".join(out), False


def _tokenize(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""   # shlex would end the line at any #, even inside a word; comments are cut above
    return list(lex)


def _is_separator(token):
    if not token or not all(c in _PUNCT_CHARS for c in token):
        return False
    return any(c in ";|&" for c in _REDIRECTIONS.sub("", token))


def _segments(tokens):
    segments, current = [], []
    for tok in tokens:
        if _is_separator(tok):
            segments.append(current)
            current = []
        else:
            current.append(tok)
    segments.append(current)
    return segments


def _family(segment):
    """(family, arguments) of a command segment, or (None, [])."""
    for i, tok in enumerate(segment):
        if tok in RESERVED_WORDS or _ASSIGNMENT.match(tok):
            continue
        return tok, segment[i + 1:]
    return None, []


def extract_families(lines):
    """(families, problems) of the labelled shell fences in a markdown file's lines.

    families maps a family to (line, snippet) of its first use; problems is a list of
    (line, snippet, message). Pure function of the text, so a test can call it directly.
    """
    families, problems = {}, []
    for open_i, close_i, info, quoted in scan_fences(lines):
        label = re.match(r"[A-Za-z0-9_+-]*", info).group(0).lower()
        if label not in SHELL_FENCE_LABELS:
            continue
        body = lines[open_i + 1:close_i]
        if quoted:
            body = [_QUOTE_PREFIX.sub("", ln) for ln in body]
        for lineno, raw in _logical_lines(body, open_i + 2):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            snippet = raw.strip()[:90]
            for needle, what in (("$(", "command substitution $("), ("`", "backtick command substitution"),
                                 ("<(", "process substitution <("), (">(", "process substitution >(")):
                if needle in raw:   # on the raw line, before any tokenizing (quotes do not hide it)
                    problems.append((lineno, snippet, f"{what} is not allowed in a fenced command"))
            try:
                tokens = _tokenize(_scan_shell(raw)[0])
            except ValueError as exc:
                # AOD-SIMPLIFICATION: one command line at a time, so a quote or heredoc that spans
                # lines is red -- upgrade: model heredocs and multi-line quotes if a recipe needs them
                problems.append((lineno, snippet, f"cannot tokenize the command line ({exc})"))
                continue
            for segment in _segments(tokens):
                family, args = _family([t.translate(_RESTORE) for t in segment])
                if family is None:
                    continue
                families.setdefault(family, (lineno, snippet))
                base = os.path.basename(family)
                if base in ("eval", "xargs"):
                    problems.append((lineno, snippet, f"{base} is not allowed in a fenced command"))
                elif base in SHELL_PROGRAMS and any(_SHELL_C_FLAG.match(a) for a in args):
                    problems.append((lineno, snippet, f"{base} -c (inline shell evaluation) is not allowed"))
    return families, problems


def check_bash_families(matrix, candidates, rep):
    for af in candidates:
        row = matrix.agents.get(af.name) if af.name else None
        capable = "Bash" in set(af.tools or ()) or (row is not None and "Bash" in row.tools)
        if not capable:
            continue
        rep.counts["bash_agents"] += 1
        allowed = set(row.bash) if row is not None else set()
        families, problems = extract_families(af.lines)
        subject = af.name or af.rel
        rep.bash[subject] = {"found": sorted(families), "allowed": sorted(allowed)}
        for family, (lineno, snippet) in sorted(families.items()):
            if family not in allowed:
                rep.red(
                    "C6", f"{af.rel}:{lineno}",
                    f"command family {family!r} (`{snippet}`) is not in the section 8 Bash families "
                    f"cell for {subject!r} ({sorted(allowed)})",
                    agent=subject, expected=sorted(allowed), actual=sorted(families),
                )
        for lineno, snippet, message in problems:
            rep.red("C6", f"{af.rel}:{lineno}", f"{message} (`{snippet}`)", agent=subject,
                    expected=sorted(allowed), actual=sorted(families))


# --------------------------------------------------------------------------- C7 writes


def check_write_locations(ctx, matrix, rep):
    union = matrix.writes_union()
    rep.counts["paths"] = len(union)
    for label, rel, tokens in (
        ("section 8.5 canonical list", ctx.matrix_rel, matrix.canonical),
        ("runbook section 5", ctx.runbook_rel, None),
    ):
        if tokens is None:
            try:
                tokens = parse_runbook_paths(_read_text(ctx.runbook_path))
            except InfraError as exc:
                rep.broken("C7", rel, str(exc))
                continue
        for token in sorted(set(tokens)):
            if tokens.count(token) > 1:
                rep.red("C7", rel, f"{label} lists path {token!r} more than once", agent=label)
        for token in sorted(set(tokens) - union):
            rep.red("C7", rel, f"{label} lists path {token!r} that no section 8 Writes cell contains",
                    agent=label, expected=sorted(union), actual=sorted(set(tokens)))
        for token in sorted(union - set(tokens)):
            rep.red("C7", rel, f"{label} omits path {token!r} that a section 8 Writes cell lists",
                    agent=label, expected=sorted(union), actual=sorted(set(tokens)))


# --------------------------------------------------------------------------- run


def run_checks(ctx):
    """C1-C7 against the tree under ctx.root."""
    rep = Report()
    try:
        matrix = parse_matrix(_read_text(ctx.matrix_path))
    except InfraError as exc:
        rep.broken("MATRIX", ctx.matrix_rel, str(exc))
        return rep
    rep.matrix = matrix
    candidates = check_roster(ctx, matrix, rep)
    rep.agent_files = candidates
    rep.counts["agents"] = len(candidates)
    check_frontmatter(matrix, candidates, rep)
    check_commands(ctx, matrix, rep)
    check_bash_families(matrix, candidates, rep)
    check_write_locations(ctx, matrix, rep)
    return rep


# --------------------------------------------------------------------------- C8 self-test


def _copy_inputs(ctx, dest):
    """Copy the guard's inputs (regular *.md agent files only) under dest, same relative paths."""
    def put(src):
        rel = ctx.rel(src)
        if rel == ".." or rel.startswith("../"):
            raise InfraError(f"--self-test needs every input under --repo-root; {src} is outside it")
        target = Path(dest) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)

    put(ctx.matrix_path)
    put(ctx.runbook_path)
    for path, kind in _walk(ctx.agents_dir):
        if kind == "file" and path.name.endswith(".md"):
            put(path)
    for p in sorted(glob.glob(os.path.join(glob.escape(str(ctx.root)), ctx.commands_glob))):
        if os.path.isfile(p):
            put(p)


def _planted_agent(name):
    return (
        "---\n"
        f"name: {name}\n"
        'description: "planted by the self-test"\n'
        "tools:\n"
        "  - Read\n"
        "model: sonnet\n"
        "---\n"
        "# Planted by the self-test\n"
    )


def _hit(findings, check_id, rel):
    """True when one of the findings is a check_id finding on the file rel (or names it)."""
    return any(
        f["check_id"] == check_id and (f["file"].split(":")[0] == rel or rel in f["message"])
        for f in findings
    )


def run_self_test(ctx):
    """C8: five mutations of a temp copy, each of which must add a finding in the expected check.

    A mutation counts only for a finding that the unmutated copy did not already have, so the
    proof holds on a drifted tree too. Two rules keep a drifted tree from being misread as a blind
    guard (exit 2 instead of exit 1):

    - M1 mutates an agent that has a section 8 row. C2 compares an agent with its row, so it can
      never fire for a rowless agent, whatever path that agent sorts to (``Evil.md``, ``0-x.md``,
      ``_TACHI_...``).
    - A mutation whose expected check and file is already red in the unmutated copy (a planted
      unlisted file, frontmatter already in the allow-listed document) cannot add a finding
      there. When its mutated copy is still red there it is reported as ``already_red``, which is
      not a failure: the tree is red and exit 1 lists the finding. It cannot hide a blind guard
      on a green tree, because the unmutated copy of a green tree has no finding to be already
      red on; a guard that stops reporting the mutated copy is still exit 2.

    Returns (results, problem); problem is a message when the self-test could not run.
    """
    def copy_to(tmp):
        root = Path(tmp)
        _copy_inputs(ctx, root)
        return root, Ctx(root, ctx.matrix_rel, ctx.agents_rel, ctx.commands_glob, ctx.runbook_rel)

    try:
        with tempfile.TemporaryDirectory(prefix="check-agent-privileges-") as tmp:
            baseline = run_checks(copy_to(tmp)[1])
    except (InfraError, OSError) as exc:
        return [], f"cannot copy the inputs for the self-test: {exc}"
    if baseline.infra:
        return [], "the unmutated copy raises infrastructure errors, so the mutations prove nothing"
    known = {(f["check_id"], f["file"], f["message"]) for f in baseline.findings}
    rows = baseline.matrix.agents   # the baseline has no infra errors, so the matrix was parsed
    target = next((af for af in sorted(baseline.agent_files, key=lambda a: a.rel)
                   if af.name in rows and af.tools and not _hit(baseline.findings, "C2", af.rel)), None)
    if target is None:
        return [], "no agent with a section 8 row and a parsable tools: entry to mutate"
    agents = ctx.agents_rel.rstrip("/")
    allow_doc = f"{agents}/{sorted(ALLOW_LISTED_DOCS)[0]}"
    extra_tool = next(t for t in ("Bash", "Write", "Agent", "Edit", "WebFetch") if t not in target.tools)

    def add_tool(root):
        lines = list(target.lines)
        entry = target.entries["tools"]
        lines[entry["start"]:entry["end"]] = ["tools:"] + [f"  - {t}" for t in target.tools + [extra_tool]]
        (root / target.rel).write_text("\n".join(lines), encoding="utf-8")

    def plant(rel, text):
        def apply(root):
            (root / rel).write_text(text, encoding="utf-8")
        return apply

    def prepend_frontmatter(root):
        path = root / allow_doc
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(_planted_agent("tachi-planted-doc") + old, encoding="utf-8")

    mutations = [
        ("M1", f"a tool ({extra_tool}) added to {target.name}", "C2", target.rel, add_tool),
        ("M2", "a planted agent with name: helper", "C1", f"{agents}/_selftest-helper.md",
         plant(f"{agents}/_selftest-helper.md", _planted_agent("helper"))),
        ("M3", "an unlisted .md file without frontmatter", "C1", f"{agents}/_selftest-unlisted.md",
         plant(f"{agents}/_selftest-unlisted.md", "# Not an agent and not on the allow-list\n")),
        ("M4", f"a duplicate of the name {target.name}", "C1", f"{agents}/_selftest-duplicate.md",
         plant(f"{agents}/_selftest-duplicate.md", "\n".join(target.lines))),
        ("M5", "the allow-listed document with planted frontmatter", "C1", allow_doc, prepend_frontmatter),
    ]
    results = []
    for mid, label, check_id, rel, apply in mutations:
        try:
            with tempfile.TemporaryDirectory(prefix="check-agent-privileges-") as tmp:
                root, copy = copy_to(tmp)
                apply(root)
                rep = run_checks(copy)
        except (InfraError, OSError) as exc:
            return results, f"cannot build the mutated copy for {mid}: {exc}"
        added = [f for f in rep.findings if (f["check_id"], f["file"], f["message"]) not in known]
        caught = _hit(added, check_id, rel) and not rep.infra
        results.append({
            "id": mid, "mutation": label, "expected_check": check_id, "expected_file": rel,
            "exit_code": 2 if rep.infra else (1 if rep.findings else 0),
            "detected": caught,
            # not caught means every finding here is one the unmutated copy already had: the mutated
            # copy is red where expected and the tree was red there before, so nothing new can show
            "already_red": not caught and not rep.infra and _hit(rep.findings, check_id, rel),
        })
    return results, None


# --------------------------------------------------------------------------- output


def build_summary(rep, self_test, self_test_detail):
    drift = []
    for f in rep.findings:
        if f["check_id"] in ("C2", "C3", "C4", "C5", "C6", "C7"):
            drift.append({
                "agent": f["agent"], "check": CHECK_WORD[f["check_id"]], "check_id": f["check_id"],
                "expected": f["expected"], "actual": f["actual"],
                "file": f["file"], "message": f["message"],
            })
    return {
        "status": rep.status(),
        "roster": {
            "agents": rep.counts["agents"],
            "allowlisted": sorted(rep.allowlisted),
            "red": sorted({f["file"] for f in rep.findings if f["check_id"] == "C1"}),
        },
        "drift": drift,
        "violations": [
            {"check_id": f["check_id"], "check": CHECK_WORD[f["check_id"]],
             "file": f["file"], "message": f["message"]}
            for f in rep.findings
        ],
        "infra": rep.infra,
        "bash_families": rep.bash,
        "counts": rep.counts,
        "self_test": self_test,
        "self_test_detail": self_test_detail,
    }


def _human_report(rep, self_test, detail):
    out = []
    if any(i["check_id"] == "MATRIX" for i in rep.infra):
        out.append(f"{PREFIX} C1-C7 not run: the privilege matrix could not be read")
    else:
        for check_id in ALL_CHECKS:
            n = sum(1 for f in rep.findings if f["check_id"] == check_id)
            extra = {
                "C1": f"{rep.counts['agents']} agents, {len(rep.allowlisted)} allow-listed document(s)",
                "C5": f"{rep.counts['commands']} commands",
                "C6": f"{rep.counts['bash_agents']} Bash-capable agents",
                "C7": f"{rep.counts['paths']} paths",
            }.get(check_id, f"{rep.counts['agents']} agents")
            status = rep.check_status(check_id).upper()
            out.append(f"{PREFIX} {check_id} {CHECK_LABEL[check_id]:<16} {status:<5} "
                       f"{f'{n} finding(s)' if n else extra}")
    for d in detail or []:
        if d["detected"]:
            got = f"detected by {d['expected_check']}"
        elif d["already_red"]:
            got = f"already red in {d['expected_check']} (the unmutated copy has this finding)"
        else:
            got = f"NOT DETECTED (exit {d['exit_code']})"
        out.append(f"{PREFIX} C8 {d['id']} {d['mutation']}: {got}")
    if self_test is not None:
        out.append(f"{PREFIX} C8 {'self-test':<16} {self_test.upper()}")
    for f in sorted(rep.findings, key=lambda f: (f["check_id"], f["file"], f["message"])):
        out.append(f"{PREFIX} FAIL {f['check_id']} {f['file']}: {f['message']}")
    return out


def _build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="check-agent-privileges.py",
        description=(
            "Compare CLAUDE_PERMISSIONS.md section 8 with the tachi agent and command files "
            "(checks C1-C7) and, with --self-test, prove the guard goes red on five mutations (C8). "
            "Exit 0 pass, 1 drift, 2 infrastructure."
        ),
    )
    parser.add_argument("--repo-root", default=None, help="repository root (default: the parent of scripts/)")
    parser.add_argument("--matrix", default=DEFAULT_MATRIX, help="privilege matrix, relative to the root")
    parser.add_argument("--agents-dir", default=DEFAULT_AGENTS_DIR, help="tachi agents directory")
    parser.add_argument("--commands-glob", default=DEFAULT_COMMANDS_GLOB, help="glob of the tachi command files")
    parser.add_argument("--runbook", default=DEFAULT_RUNBOOK, help="runbook with the section 5 write-locations table")
    parser.add_argument("--self-test", action="store_true", help="run C1-C7, then the five C8 mutations")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON (sort_keys, indent 2)")
    return parser


def _say(text, stream=None):
    """print() that cannot die on a console that cannot encode a character."""
    stream = stream or sys.stdout
    try:
        print(text, file=stream)
    except UnicodeEncodeError:
        print(text.encode("ascii", "backslashreplace").decode("ascii"), file=stream)


def _run(args):
    root = Path(args.repo_root).resolve() if args.repo_root else DEFAULT_ROOT
    ctx = Ctx(root, args.matrix, args.agents_dir, args.commands_glob, args.runbook)
    rep = run_checks(ctx)
    exit_code = 2 if rep.infra else (1 if rep.findings else 0)

    self_test = detail = None
    if args.self_test:
        if rep.infra:
            self_test = "skipped"   # C1-C7 hit an infrastructure error on the live tree; exit 2 stands
        else:
            detail, problem = run_self_test(ctx)
            if problem is not None:
                rep.broken("C8", "", problem)
                self_test, exit_code = "fail", 2
            elif all(d["detected"] or d["already_red"] for d in detail):
                self_test = "pass"   # an already-red mutation is no failure: C1-C7 report that finding (exit 1)
            else:
                self_test, exit_code = "fail", 2
                for d in detail:
                    if not (d["detected"] or d["already_red"]):
                        rep.broken("C8", d["expected_file"],
                                   f"mutation {d['id']} ({d['mutation']}) did not turn the guard red "
                                   f"in {d['expected_check']} (exit {d['exit_code']})")
    summary = build_summary(rep, self_test, detail)
    summary["status"] = {0: "pass", 1: "drift", 2: "infra"}[exit_code]
    for item in rep.infra:
        where = f" {item['file']}:" if item["file"] else ""
        _say(f"{PREFIX} ERROR {item['check_id']}{where} {item['message']}", sys.stderr)
    if args.json:
        _say(json.dumps(summary, sort_keys=True, indent=2))
    else:
        for line in _human_report(rep, self_test, detail):
            _say(line)
        _say(f"{PREFIX} RESULT: {summary['status']} (exit {exit_code})")
        if summary["status"] == "drift":
            _say(f"{PREFIX} HINT: a deliberate privilege change edits the file and {ctx.matrix_rel} "
                 f"(and the runbook's section 5 for write paths) in the same commit")
    return exit_code


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        return _run(args)
    except Exception:  # a bug, or an input nobody anticipated, must never read as drift (exit 1)
        traceback.print_exc()
        _say(f"{PREFIX} ERROR internal error in the guard; this is exit 2, not drift", sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
