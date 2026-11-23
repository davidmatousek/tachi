"""Scoring rules for the risk-scores renderer and the scorer planner (F-374, ADR-050 D5 and D9).

``tachi_scoring`` holds the arithmetic. This module holds the rules that decide which values the arithmetic
runs on: where a baseline comes from, what its files say, and which asset tags a run uses. Every function is
pure over its arguments and reads only the paths its caller passes (D5). It imports the standard library,
``tachi_scoring``, ``tachi_parts`` and ``tachi_parsers``, and never ``sarif_common``, an entry script or
``yaml``. Its public signatures are frozen in ``contracts/module-signatures.md``.

**Part 1 (T042)** is what the renderer's whole-file render (T028) and the scorer's planner (T044) need first:

* ``check_run_file`` and ``resolve_baseline`` (R-6, D9): the baseline. The command's ``--baseline`` comes first,
  then the input ``threats.md``'s ``baseline.source``, and every file the stages read from a baseline directory
  must be a regular file with its canonical name, no symlink on its path, under the working directory by file
  identity (NFR-10, KB 24). Free text, an unresolvable path or a failed check means no baseline, with the reason.
* ``read_baseline_scores`` (R-26, D9): the tolerant reader of a baseline ``risk-scores.md`` and, for a legacy
  file's vectors, its ``risk-scores.sarif``. It reads the renderer's own form (the ``### Scoring Inputs`` table
  of ``## 6. Score Integrity``) and every legacy form that tachi's shipped samples show.
* ``recompute_tags`` and ``select_tag_source`` (S-13, D2): the one source of a run's asset tags.

**Part 2 (T043)** is what the renderer's recompute-and-flag step (T045, T046) and the scorer's planner (T044) share:

* ``asset_outcome`` and ``cvss_chain`` (R-25, D10): the CVSS chain of a fresh finding, with the asset modifier.
* ``check_carried_vector`` (D10): the vector check on a carried finding, whose legacy list tests this run's tags first.
* ``route_scorer_units``, ``peer_divergence`` (R-31, D2, D9): who goes to the scorer agent, who is carried, and who
  copies a primary. The groups are the result of ``tachi_parsers.parse_correlation_groups``, the one authority for
  D8's rules, and none of those rules is restated here.
* ``original_scoring_date``, ``classify_band_change`` and ``governance_for`` (R-5, R-31, ruling A): the owner, SLA,
  disposition, review date and scored-on date of a finding, and the flag of each value that moves.

Rules this module holds:

* **A cell is decoded once.** The renderer escapes every untrusted string it writes (D3), so a reader decodes
  each cell exactly once, with ``tachi_parsers.decode_references``, after splitting the row on raw ``|``. This
  module reads its tables with its own splitter, and never through ``parse_markdown_table``, so the one decode
  neither depends on that parser's version nor runs twice, and a carried string is escaped once per render and
  never compounds across runs (RR1).
* **Stored values are verbatim.** A stored score comes back as the ``Decimal`` the file wrote, whether or not it
  is in range or on the 0.1 grid, so a wrong one can be compared and corrected. Pass it to ``tachi_scoring``'s
  ``band`` or ``composite`` only after checking it.
* **Nothing reads a number from prose.** Narrative and legacy prose come back as text.
* **Content problems never raise.** They come back as a reason, an issue or a flag. A caller that breaks a
  precondition (a finding ID that isn't allow-listed) raises ``ValueError``, because that is a shipped-code defect.
"""
from __future__ import annotations

import json
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

# Turn bytecode writing off before the local imports below (feature 391; ADR-049 D8).
sys.dont_write_bytecode = True
# Siblings are found beside this file, whether it is imported flat or as `scripts.tachi_scoring_rules`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tachi_parsers  # noqa: E402
import tachi_parts  # noqa: E402
import tachi_scoring  # noqa: E402

# The files a baseline run directory can supply to the scorer and controls stages (D9). Each is read under its
# canonical name only.
BASELINE_FILE_NAMES: Tuple[str, ...] = (
    "threats.md", "risk-scores.md", "risk-scores.sarif",
    "compensating-controls.md", "compensating-controls.sarif",
)


# =============================================================================
# R-6: the baseline resolver (D9; NFR-10, KB 24)
# =============================================================================

@dataclass(frozen=True)
class PathCheck:
    path: Optional[Path]    # set when every check passes
    reason: Optional[str]   # set when path is None


# D9's reasons for a path that fails, in the order the checks run. `path_guard_problem`'s names map onto them.
_GUARD_REASONS = {"outside": "outside-working-directory", "not-regular": "not-regular-file"}


def _present(value: Any) -> Optional[str]:
    """``value`` as text, or ``None`` when it is not given: ``None``, or text that is empty or only whitespace."""
    if isinstance(value, os.PathLike):
        value = os.fspath(value)
    if isinstance(value, str) and value.strip():
        return value
    return None


def _absolute(text: str, cwd: str) -> str:
    return os.path.abspath(text if os.path.isabs(text) else os.path.join(cwd, text))


def _free_text(text: str) -> bool:
    """True when ``text`` reads as a sentence or a bare word, not as a path to a file.

    ``baseline.source`` is sometimes prose such as ``none (first run, stateless mode)`` (#379). The shape is
    the whole test: no ``/``, and either whitespace or no ``.`` at all. A path to a wrong-named file in the
    working directory (``old-run.md``) is not free text, so it is reported as ``wrong-name`` instead. Either way
    the outcome is the same: no baseline, with the reason recorded.
    """
    return "/" not in text and (any(ch.isspace() for ch in text) or "." not in text)


def check_run_file(candidate: Optional[str], *, cwd: Path, expected_name: str) -> PathCheck:
    """D9's checks for one file that a run's baseline or input names (NFR-10, KB 24).

    ``candidate`` must name a regular file called ``expected_name``, with no symlink among its components,
    under ``cwd`` by ``os.path.samefile`` identity. A relative ``candidate`` means ``cwd``. Otherwise the result
    carries the first failing check's reason, in this order:

    * ``absent``: nothing was given;
    * ``free-text``: not a path (see ``_free_text``), or a string that ``tachi_parts.path_problem`` refuses for its
      syntax (a scheme, a drive letter, a backslash, a backtick, a control character, or too long);
    * ``outside-working-directory``: a ``..`` component, or the file is not under ``cwd``;
    * ``wrong-name``: the last component is not ``expected_name``;
    * ``missing``, ``symlink`` or ``not-regular-file``: the walk down from ``cwd``.

    The controls planner calls this on ``risk-scores.md``'s ``source_file`` too, with
    ``expected_name="threats.md"``.
    """
    text = _present(candidate)
    if text is None:
        return PathCheck(None, "absent")
    if _free_text(text):
        return PathCheck(None, "free-text")
    problem = tachi_parts.path_problem(text, allow_absolute=True)
    if problem == "parent-reference":
        return PathCheck(None, "outside-working-directory")
    if problem == "empty":  # "." names the directory itself, which no file name matches
        return PathCheck(None, "wrong-name")
    if problem is not None:
        return PathCheck(None, "free-text")
    if tachi_parts.path_parts(text, allow_absolute=True)[-1] != expected_name:
        return PathCheck(None, "wrong-name")
    base = os.fspath(cwd)
    full = _absolute(text, base)
    guard = tachi_parts.path_guard_problem(full, base)
    if guard is not None:
        return PathCheck(None, _GUARD_REASONS.get(guard, guard))
    return PathCheck(Path(full), None)


@dataclass(frozen=True)
class BaselineResolution:
    run_dir: Optional[Path]
    origin: Optional[str]       # "flag" | "baseline.source": the input that was used, or that failed
    files: Mapping[str, Path]   # each BASELINE_FILE_NAMES entry in run_dir that passes check_run_file
    reason: Optional[str]       # why run_dir is None; the stage record carries it
    # Additive (T042, with a default, last): why each BASELINE_FILE_NAMES entry that is not in `files` failed
    # check_run_file, so a present-but-refused file can be reported (S-12(d)). Empty when run_dir is None.
    file_reasons: Mapping[str, str] = field(default_factory=dict)


def _flag_run_dir(flag: str, cwd: str) -> Tuple[Optional[str], Optional[str]]:
    """``--baseline``'s run directory, or the reason it has none. A file path counts as its directory.

    The flag comes from the command, so it is not held to a file name. Every file read from the directory is
    checked on its own by ``check_run_file``, and that catches a symlinked directory or a file outside ``cwd``.
    """
    problem = tachi_parts.path_problem(flag, allow_absolute=True)
    if problem == "parent-reference":
        return None, "outside-working-directory"
    if problem not in (None, "empty"):  # "empty" is "." and "./": the working directory itself
        return None, "free-text"
    full = _absolute(flag, cwd)
    if not tachi_parts.under(cwd, full):
        return None, "outside-working-directory"
    if os.path.isdir(full):
        return full, None
    if os.path.isfile(full):
        return os.path.dirname(full), None
    return None, "missing"


def resolve_baseline(*, flag: Optional[str], baseline_source: Optional[str], cwd: Path) -> BaselineResolution:
    """R-6: the one baseline of a run. ``flag`` (``--baseline``) comes first, then ``baseline_source``.

    ``baseline_source`` is the input ``threats.md``'s ``baseline.source`` as ``parse_baseline_frontmatter``
    reads it, and it must pass ``check_run_file(..., expected_name="threats.md")``; its directory is the run
    directory. Free text, an unresolvable path or a failed check gives ``run_dir=None`` and the reason, and the
    stage scores fresh. When neither is given the reason is ``not-named``, which is a first run and no warning.
    Otherwise ``files`` holds each of ``BASELINE_FILE_NAMES`` that is in the run directory and passes
    ``check_run_file``, and ``file_reasons`` says why each of the others does not.
    """
    base = os.fspath(cwd)
    flag_text, source_text = _present(flag), _present(baseline_source)
    if flag_text is not None:
        origin = "flag"
        run_dir, reason = _flag_run_dir(flag_text, base)
    elif source_text is not None:
        origin = "baseline.source"
        checked = check_run_file(source_text, cwd=cwd, expected_name="threats.md")
        run_dir = os.path.dirname(os.fspath(checked.path)) if checked.path is not None else None
        reason = checked.reason
    else:
        return BaselineResolution(None, None, {}, "not-named")
    if run_dir is None:
        return BaselineResolution(None, origin, {}, reason)
    files: Dict[str, Path] = {}
    file_reasons: Dict[str, str] = {}
    for name in BASELINE_FILE_NAMES:
        checked = check_run_file(os.path.join(run_dir, name), cwd=cwd, expected_name=name)
        if checked.path is not None:
            files[name] = checked.path
        else:
            file_reasons[name] = checked.reason or "missing"
    return BaselineResolution(Path(run_dir), origin, files, None, file_reasons)


# =============================================================================
# R-26: the tolerant reader (D9, S-12(a), (d))
# =============================================================================

@dataclass(frozen=True)
class InputIssue:
    finding_id: Optional[str]   # None for a file-level issue
    field: str
    cause: str
    detail: str


@dataclass(frozen=True)
class BaselineRow:
    finding_id: str
    form: str                                        # "renderer" | "legacy"
    cvss_vector: Optional[str]
    vector_source: Optional[str]                     # "md" | "sarif"
    score_bounds: Optional[Tuple[Decimal, Decimal]]  # renderer form only
    subscores: Optional[Mapping[str, int]]           # by the eight bare sub-score names; renderer form only
    zone: Optional[str]
    trust_level: Optional[str]
    auth_barriers: Optional[int]
    network_boundaries: Optional[int]
    tags_used: Optional[Tuple[str, ...]]             # renderer form only; None means no tags were recorded
    scored_on: Optional[date]                        # renderer form only
    stored: Mapping[str, Optional[Decimal]]          # cvss_base, exploitability, scalability, reachability, composite
    band: Optional[str]
    owner: Optional[str]
    sla: Optional[str]                               # as written, such as "24h" or "7d"
    disposition: Optional[str]
    review_date: Optional[date]
    narrative: Mapping[str, str]                     # renderer form: field path -> decoded slotted text
    legacy_prose: Mapping[str, str]                  # legacy form: field path -> prose, evidence-class
    flags: Tuple[str, ...]                           # raised while reading, such as input:cvss_vector:sources-disagree
    component: Optional[str] = None                  # W2: the row's component, for S-12(b)'s supply (D9)
    threat: Optional[str] = None                     # W2: the row's threat text, for S-12(b)'s supply
    risk_level: Optional[str] = None                 # W2: the row's original risk level, for S-12(b)'s supply


@dataclass(frozen=True)
class BaselineScores:
    readable: bool
    reason: Optional[str]                     # "missing" | "not-utf8" | "too-large" | "no-rows"
    form: Optional[str]                       # "renderer" | "legacy"
    rows: Mapping[str, BaselineRow]           # the open rows
    resolved_rows: Mapping[str, BaselineRow]  # the §2a rows (R-30)
    ids_in_any_row: frozenset                 # for ruling B's reused-id test
    frontmatter_date: Optional[date]          # D9's review-date fallback
    issues: Tuple[InputIssue, ...]            # unreadable rows go to Input Issues and are scored fresh


_RENDERER, _LEGACY = "renderer", "legacy"
_BAND_NAMES = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}
_TRUST_NAMES = {name.lower(): name for name in tachi_parts.TRUST_LEVELS}
_PLACEHOLDER_TEXT = frozenset(("", "-", "\u2013", "\u2014", "n/a"))
_STORED_KEYS = ("cvss_base", "exploitability", "scalability", "reachability", "composite")

# Header aliases for the scored table, §2a and the governance table, matched after `normalize_header` (casefold,
# one trailing "." dropped, whitespace collapsed): "Exploit", "Exploit." and "Exploitability" are one column,
# as are "Disp" and "Disposition" (D9).
_COLUMN_ALIASES = {
    "id": "id", "finding id": "id", "threat id": "id",
    "component": "component", "threat": "threat",
    "cvss": "cvss_base", "cvss base": "cvss_base", "cvss base score": "cvss_base", "cvss score": "cvss_base",
    "exploit": "exploitability", "exploitability": "exploitability", "exploit score": "exploitability",
    "exploitability score": "exploitability",
    "scale": "scalability", "scalability": "scalability", "scalability score": "scalability",
    "reach": "reachability", "reachability": "reachability", "reachability score": "reachability",
    "composite": "composite", "composite score": "composite",
    "severity": "band", "severity band": "band", "band": "band",
    "sla": "sla", "remediation sla": "sla",
    "disposition": "disposition", "disp": "disposition", "risk disposition": "disposition",
    "owner": "owner", "risk owner": "owner",
    "review date": "review_date", "review": "review_date",
}

# The closed field names of `### Scoring Inputs` (contracts/module-signatures.md, "The persisted-inputs format").
_SUBSCORE_FIELDS = {
    ("exploitability." if position < 4 else "scalability.") + name: name
    for position, name in enumerate(tachi_parts.SUBSCORE_NAMES)
}
_COUNT_FIELDS = ("reachability.auth_barriers", "reachability.network_boundaries")
_TEXT_FIELDS = ("reachability.zone", "reachability.trust_level")
_NARRATIVE_FIELDS = frozenset(name for name in tachi_parts.NARRATIVE_FIELDS if not name.startswith("evidence."))
_INPUT_FIELDS = (frozenset(("cvss_vector", "score_bounds", "tags", "scored_on")) | frozenset(_SUBSCORE_FIELDS)
                 | frozenset(_COUNT_FIELDS) | frozenset(_TEXT_FIELDS) | _NARRATIVE_FIELDS)

_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")
_SECTION_NUMBER = re.compile(r"^(?:section[ \t]+)?([0-9]{1,2})([a-z]?)[ \t]*[.:\u2014\u2013-][ \t]*(.*)$", re.IGNORECASE)
_SEPARATOR_ROW = re.compile(r"^\|[\s\-:|]+\|$")
_STORED_NUMBER = re.compile(r"[0-9]{1,3}(?:\.[0-9]{1,3})?", re.ASCII)
_SMALL_INT = re.compile(r"10|[0-9]", re.ASCII)
_SCORE_BOUNDS = re.compile(r"([0-9]{1,2}\.[0-9])[ \t]*,[ \t]*([0-9]{1,2}\.[0-9])", re.ASCII)
# §3's vector labels: `**CVSS Vector**: `...`` and `**Score**: 9.1 | **Vector**: `...``, the colon inside or outside.
_VECTOR_LABEL = re.compile(r"\*\*(?:CVSS[ \t]+)?Vector(?::\*\*|\*\*[ \t]*:)[ \t]*`?[ \t]*([^`\s|]*)")
_TRUST_ZONE_LINE = re.compile(r"\*\*Trust Zone(?::\*\*|\*\*[ \t]*:)[ \t]*(.+?)[ \t]*\(([^()]*)\)[ \t]*$")
_RATIONALE_BULLET = re.compile(r"^[-*][ \t]+\*\*(CVSS|Exploitability|Scalability|Reachability)\*\*[ \t]*:[ \t]*(.+)$")
_METRIC_CELL = re.compile(r"\(([A-Z]{1,2})\)$")
# §3's identity values, for S-12(b)'s supply (D9): the `**Threat**:` line, the value of `**Original Risk Level**:` (it ends at the
# next raw `|`, because the renderer escapes a `|` in text as `&#124;`), and the component after a heading's dash.
_THREAT_LINE = re.compile(r"\*\*Threat(?::\*\*|\*\*[ \t]*:)[ \t]*(.*)$")
_RISK_LEVEL = re.compile(r"\*\*Original Risk Level(?::\*\*|\*\*[ \t]*:)[ \t]*([^|]*)")
_HEADING_COMPONENT = re.compile(r"^[^\s:\u2014\u2013]+[ \t]*[\u2014\u2013][ \t]*(\S.*)$")


# The most issues one read lists. An input with more unreadable rows than this is a hostile or a wrecked file, and
# the rest are only counted, so the output that lists them stays bounded (NFR-10's limits).
ISSUE_LIMIT = 200


class _IssueLog(list):
    """The issues of one read. Past ``ISSUE_LIMIT`` an issue is counted in ``dropped``, not kept."""

    dropped = 0

    def append(self, issue: InputIssue) -> None:
        if len(self) < ISSUE_LIMIT:
            super().append(issue)
        else:
            self.dropped += 1

    def finished(self) -> Tuple[InputIssue, ...]:
        """The issues, then one ``truncated`` issue that counts the ones that were dropped."""
        more = (InputIssue(None, "issues", "truncated", "%d more issues were not listed" % self.dropped),) if self.dropped else ()
        return tuple(self) + more


def _quote(text: str) -> str:
    """A short, escaped quotation of a cell for an issue's detail: control characters show as escapes."""
    return repr(text[:40])


def _decode(text: str) -> str:
    """The one decode of a cell or a line, by the shared closed decoder (ADR-050 D3)."""
    return tachi_parsers.decode_references(text)


def _read_bytes(path: Any) -> Tuple[Optional[bytes], Optional[str]]:
    """A regular file's bytes, or the reason it can't be read: ``missing`` or ``too-large``.

    The file is opened without following a link and must be a regular file, and the read stops at the
    16 MiB cap that D3 gives an agent-written markdown or SARIF input (step 2).
    """
    if path is None:
        return None, "missing"
    flags = os.O_RDONLY
    for name in ("O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):
        flags |= getattr(os, name, 0)
    try:
        descriptor = os.open(os.fspath(path), flags)
    except OSError:
        return None, "missing"
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return None, "missing"
        chunks, total = [], 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                return b"".join(chunks), None
            chunks.append(chunk)
            total += len(chunk)
            if total > tachi_parts.MAX_AGENT_INPUT_BYTES:
                return None, "too-large"
    except OSError:
        return None, "missing"
    finally:
        os.close(descriptor)


def _unreadable(reason: str, issues: Tuple[InputIssue, ...] = (), ids: frozenset = frozenset()) -> BaselineScores:
    return BaselineScores(False, reason, None, {}, {}, ids, None, issues)


# ---------------------------------------------------------------------------- the markdown's shape

def _outline(lines: List[str]) -> List[Tuple[int, int, str, int]]:
    """Every heading outside a code fence, as ``(line index, level, text, end index)``.

    A heading's end is the index of the next heading at or above its level, or the end of the file. They are
    found in one pass with a stack, so a file of many headings costs no more than its length (NFR-10's limits).
    """
    headings: List[Tuple[int, int, str]] = []
    fence: Optional[str] = None
    for index, raw in enumerate(lines):
        line = raw.strip()
        if line.startswith("```") or line.startswith("~~~"):
            if fence is None:
                fence = line[:3]
            elif line.startswith(fence):
                fence = None
            continue
        if fence is not None:
            continue
        match = _HEADING.match(line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2)))
    ends = [len(lines)] * len(headings)
    open_headings: List[int] = []
    for position, (index, level, _) in enumerate(headings):
        while open_headings and headings[open_headings[-1]][1] >= level:
            ends[open_headings.pop()] = index
        open_headings.append(position)
    return [(index, level, text, ends[position]) for position, (index, level, text) in enumerate(headings)]


def _section_ranges(outline: List[Tuple[int, int, str, int]]) -> Dict[Tuple[int, str], Tuple[int, int]]:
    """``(number, letter)`` -> ``(heading index, end index)`` for each level-2 heading ``## N.`` or ``## Section N:``.

    The first heading with a given number wins.
    """
    ranges: Dict[Tuple[int, str], Tuple[int, int]] = {}
    for index, level, text, end in outline:
        match = _SECTION_NUMBER.match(text.strip()) if level == 2 else None
        if match is not None:
            ranges.setdefault((int(match.group(1)), match.group(2).lower()), (index, end))
    return ranges


def _cells(line: str) -> List[str]:
    """A table row's cells, split on raw ``|`` and stripped. Nothing is decoded here."""
    return [cell.strip() for cell in line.strip().split("|")[1:-1]]


def _first_table(lines: List[str], start: int, stop: int) -> Optional[Tuple[List[str], List[Tuple[int, List[str]]], List[int]]]:
    """The first pipe table in ``lines[start:stop]``: ``(header cells, [(line number, cells)], malformed line numbers)``.

    A row whose cell count is not the header's is malformed and listed by its 1-based line number. A row with fewer
    cells is what ``parse_markdown_table`` drops too. One with more is stricter on purpose: a literal ``|`` in a
    cell shifts every later column, and a shifted score must never be inherited as another score.
    The table ends at the first line that does not start with ``|``.
    """
    index = start
    while index < stop and not (lines[index].strip().startswith("|") and "|" in lines[index].strip()[1:]):
        index += 1
    if index >= stop:
        return None
    header = _cells(lines[index])
    index += 1
    if index < stop and _SEPARATOR_ROW.match(lines[index].strip()):
        index += 1
    rows: List[Tuple[int, List[str]]] = []
    malformed: List[int] = []
    while index < stop and lines[index].strip().startswith("|"):
        cells = _cells(lines[index])
        if len(cells) != len(header):
            malformed.append(index + 1)
        else:
            rows.append((index + 1, cells))
        index += 1
    return header, rows, malformed


def _finding_id(cell: str) -> Optional[str]:
    """The canonical ID in a table cell (bold and code marks dropped), or ``None`` unless it is exactly one."""
    text = cell.replace("**", "").replace("`", "").strip()
    return tachi_parts.canonical_finding_id(text) if tachi_parts.id_matches("finding", text) else None


def _column_map(header: List[str]) -> Dict[str, int]:
    columns: Dict[str, int] = {}
    for position, cell in enumerate(header):
        name = _COLUMN_ALIASES.get(tachi_parsers.normalize_header(tachi_parsers.strip_bold(cell)))
        if name is not None:
            columns.setdefault(name, position)
    return columns


def _stored_score(cell: str) -> Optional[Decimal]:
    """A stored score as the file wrote it, as a ``Decimal``, or ``None`` when the cell is not a plain number."""
    text = cell.replace("**", "").strip()
    return Decimal(text) if _STORED_NUMBER.fullmatch(text) else None


def _text_value(cell: str) -> Optional[str]:
    """A text cell decoded once, its ``**`` dropped, or ``None`` for an empty cell or a dash placeholder.

    It reads the SLA and the disposition, whose emphasis is formatting around the value: the disposition is an enum
    and the SLA a duration, and the override test compares each with the band's default. So a bolded legacy ``**Accept**``
    or ``**7d**`` reads as the value the test compares (ruled at W2).
    """
    text = _decode(cell.replace("**", "").strip()).strip()
    return None if text.lower() in _PLACEHOLDER_TEXT else text


def _verbatim_text(cell: str) -> Optional[str]:
    """A free-text cell as the cell holds it: decoded once, edge whitespace stripped, its ``**`` kept.

    It reads the owner (``risk_owner``), which D9 carries verbatim and a human edits, so ``**Platform** team`` comes
    back byte for byte: the renderer's table-cell escape leaves ``*`` alone, so the value round-trips (ruled at W2). It
    reads a component and a threat the same way. A cell is no value only when it is a placeholder once its ``**`` is
    set aside: empty, a dash or ``n/a``.
    """
    text = _decode(cell.strip()).strip()
    return None if text.replace("**", "").strip().lower() in _PLACEHOLDER_TEXT else text


def _date_value(cell: str) -> Optional[date]:
    try:
        return tachi_scoring.parse_date(cell.replace("**", "").strip())
    except ValueError:
        return None


def _valid_vector(text: str) -> bool:
    try:
        tachi_scoring.base_score(text)
    except ValueError:
        return False
    return True


def _table_rows(lines: List[str], span: Optional[Tuple[int, int]], what: str, issues: List[InputIssue],
                seen: set) -> List[Tuple[int, str, Dict[str, str]]]:
    """The readable rows of the first table in a section: ``(line number, canonical ID, cells by column name)``.

    Every ID found goes into ``seen``. A malformed row, an ID cell that is not one allow-listed ID and a repeated
    ID each become an issue and yield no row (a repeat keeps the first). An empty or dash-only ID cell is a
    placeholder row and is dropped without one.
    """
    if span is None:
        return []
    table = _first_table(lines, span[0] + 1, span[1])
    if table is None:
        return []
    header, raw_rows, malformed = table
    columns = _column_map(header)
    for number in malformed:
        issues.append(InputIssue(None, "row", "malformed-row", "%s, line %d: the row does not have as many cells as its header" % (what, number)))
    if "id" not in columns:
        issues.append(InputIssue(None, "id", "no-id-column", "%s has no ID column" % what))
        return []
    rows: List[Tuple[int, str, Dict[str, str]]] = []
    kept: set = set()
    for number, cells in raw_rows:
        cell = cells[columns["id"]]
        if tachi_parsers.is_placeholder_id(cell.replace("**", "")):
            continue
        finding_id = _finding_id(cell)
        if finding_id is None:
            issues.append(InputIssue(None, "id", "not-a-finding-id", "%s, line %d: %s is not one finding ID, so the row is not read" % (what, number, _quote(cell))))
            continue
        seen.add(finding_id)
        if finding_id in kept:
            issues.append(InputIssue(finding_id, "id", "duplicate-id", "%s, line %d: the ID repeats, and the first row is kept" % (what, number)))
            continue
        kept.add(finding_id)
        rows.append((number, finding_id, {name: cells[position] for name, position in columns.items() if position < len(cells)}))
    return rows


# ---------------------------------------------------------------------------- §2, §2a and §4

def _scored_rows(lines: List[str], span: Optional[Tuple[int, int]], what: str, issues: List[InputIssue],
                 seen: set) -> Dict[str, Dict[str, Any]]:
    """§2 or §2a, by canonical ID: the stored values, the band and any governance columns the table has.

    The component and threat cells are read too, for S-12(b)'s supply. §2 holds them as the renderer shortened them
    (to 30 and 60 characters), so they are the fallback to §3's full text.
    """
    scored: Dict[str, Dict[str, Any]] = {}
    for number, finding_id, cells in _table_rows(lines, span, what, issues, seen):
        scored[finding_id] = {
            "line": number,
            "stored": {key: _stored_score(cells.get(key, "")) for key in _STORED_KEYS},
            "band": _BAND_NAMES.get(cells.get("band", "").replace("**", "").strip().lower()),
            "sla": _text_value(cells.get("sla", "")),
            "disposition": _text_value(cells.get("disposition", "")),
            "owner": _verbatim_text(cells.get("owner", "")),
            "review_date": _date_value(cells.get("review_date", "")),
            "component": _verbatim_text(cells.get("component", "")),
            "threat": _verbatim_text(cells.get("threat", "")),
        }
    return scored


def _governance_rows(lines: List[str], span: Optional[Tuple[int, int]], issues: List[InputIssue],
                     seen: set) -> Dict[str, Dict[str, Any]]:
    """§4's human-edited fields by canonical ID. §4 outranks §2's SLA and disposition columns (D9, R-31)."""
    return {
        finding_id: {
            "band": _BAND_NAMES.get(cells.get("band", "").replace("**", "").strip().lower()),
            "owner": _verbatim_text(cells.get("owner", "")),
            "sla": _text_value(cells.get("sla", "")),
            "disposition": _text_value(cells.get("disposition", "")),
            "review_date": _date_value(cells.get("review_date", "")),
        }
        for _, finding_id, cells in _table_rows(lines, span, "Section 4", issues, seen)
    }


# ---------------------------------------------------------------------------- §6's Scoring Inputs

@dataclass
class _Inputs:
    values: Dict[str, Any] = field(default_factory=dict)       # typed values by field name
    narrative: Dict[str, str] = field(default_factory=dict)    # decoded slotted text by field name

    def missing(self) -> List[str]:
        """What a renderer-form row needs and lacks: a valid vector and all eight sub-scores."""
        need = ["cvss_vector"] + sorted(_SUBSCORE_FIELDS)
        return [name for name in need if name not in self.values]


def _parse_input(name: str, value: str) -> Any:
    """One ``### Scoring Inputs`` value, re-checked against its class (D3, "Reading"). Raises ``ValueError`` if it fails."""
    if name == "cvss_vector":
        if not _valid_vector(value):
            raise ValueError("not a full CVSS 3.1 base vector")
        return value
    if name in _SUBSCORE_FIELDS or name in _COUNT_FIELDS:
        if _SMALL_INT.fullmatch(value) is None:
            raise ValueError("not an integer from 0 to 10")
        return int(value)
    if name == "reachability.zone":
        try:
            return tachi_parts.closed_string(value, name, 1, 120)
        except tachi_parts.PartError:
            raise ValueError("not text of 1 to 120 characters") from None
    if name == "reachability.trust_level":
        if value not in tachi_parts.TRUST_LEVELS:
            raise ValueError("not a trust level")
        return value
    if name == "score_bounds":
        match = _SCORE_BOUNDS.fullmatch(value)
        low, high = (Decimal(match.group(1)), Decimal(match.group(2))) if match else (None, None)
        if low is None or not (Decimal("0.0") <= low <= high <= Decimal("10.0")):
            raise ValueError("not two ascending scores from 0.0 to 10.0")
        return (low, high)
    if name == "tags":
        names = [tag.strip().lower() for tag in value.split(",")] if value.strip() else []
        if any(tag not in tachi_scoring.TAG_FORCES for tag in names):
            raise ValueError("a tag outside the closed set")
        return tuple(sorted(set(names)))
    return tachi_scoring.parse_date(value)  # the one field left is scored_on; narrative fields never come here


def _scoring_inputs(lines: List[str], outline: List[Tuple[int, int, str, int]], issues: List[InputIssue],
                    seen: set) -> Dict[str, _Inputs]:
    """The renderer's persisted inputs, by canonical ID, from the ``### Scoring Inputs`` table (empty for a legacy file).

    Each value is decoded once and re-checked against its class. A row with an unknown field, a repeated field
    or a value that fails its class becomes an issue and is dropped.
    """
    heading = next((entry for entry in outline if entry[1] >= 3 and entry[2].strip().lower() == "scoring inputs"), None)
    if heading is None:
        return {}
    table = _first_table(lines, heading[0] + 1, heading[3])
    if table is None:
        return {}
    header, rows, malformed = table
    if [tachi_parsers.normalize_header(tachi_parsers.strip_bold(cell)) for cell in header[:3]] != ["id", "field", "value"]:
        issues.append(InputIssue(None, "scoring_inputs", "unknown-form", "Scoring Inputs does not have the ID, Field and Value columns, so it is not read"))
        return {}
    for number in malformed:
        issues.append(InputIssue(None, "row", "malformed-row", "Scoring Inputs, line %d: the row does not have as many cells as its header" % number))
    inputs: Dict[str, _Inputs] = {}
    for number, cells in rows:
        finding_id = _finding_id(cells[0])
        if finding_id is None:
            issues.append(InputIssue(None, "id", "not-a-finding-id", "Scoring Inputs, line %d: %s is not one finding ID, so the row is not read" % (number, _quote(cells[0]))))
            continue
        seen.add(finding_id)
        name = cells[1]
        if name not in _INPUT_FIELDS:
            issues.append(InputIssue(finding_id, name[:40], "unknown-field", "Scoring Inputs, line %d: %s is not a field of the persisted inputs" % (number, _quote(name))))
            continue
        entry = inputs.setdefault(finding_id, _Inputs())
        if name in entry.values or name in entry.narrative:
            issues.append(InputIssue(finding_id, name, "duplicate-field", "Scoring Inputs, line %d: the field repeats, and the first row is kept" % number))
            continue
        value = _decode(cells[2])
        if name in _NARRATIVE_FIELDS:
            entry.narrative[name] = value
            continue
        try:
            entry.values[name] = _parse_input(name, value)
        except ValueError as exc:
            issues.append(InputIssue(finding_id, name, "invalid-value", "Scoring Inputs, line %d: the value %s is %s" % (number, _quote(value), exc)))
    return inputs


# ---------------------------------------------------------------------------- §3

def _heading_finding_id(text: str) -> Optional[str]:
    """The finding ID that a §3 subsection heading names: ``### ID — component`` or ``### ID: title``."""
    token = re.split(r"[\s:\u2014\u2013]", text.replace("**", "").replace("`", "").strip(), maxsplit=1)[0]
    return tachi_parts.canonical_finding_id(token) if tachi_parts.id_matches("finding", token) else None


def _read_subsection(body: List[str]) -> Dict[str, Any]:
    """What one §3 subsection holds: the first valid vector (and whether an invalid one was seen), the trust
    zone line, the threat line, the original risk level and the legacy prose by field name. Prose, the threat
    and the risk level are returned as written, not decoded.

    Legacy prose has two shipped forms. The older one is a ``**Scoring Rationale**:`` list with a bullet for each
    of CVSS, Exploitability, Scalability and Reachability. The v4.48.4 one is the rationale column of each metric
    and sub-score row, and the paragraph under the Reachability heading. Each fills the same field names that the
    renderer's narrative uses, and the first text for a field wins.
    """
    # AOD-SIMPLIFICATION: the two shipped prose forms only — upgrade: add a form here when a baseline needs one
    # AOD-SIMPLIFICATION: a threat is the one `**Threat**:` line, so a threat that spans lines loses the rest — upgrade: read to the next blank line
    found: Dict[str, Any] = {"vector": None, "invalid_vector": False, "zone": None, "trust": None, "prose": {},
                             "threat": None, "risk_level": None}
    prose: Dict[str, str] = found["prose"]
    for number, raw in enumerate(body):
        line = raw.strip()
        for match in _VECTOR_LABEL.finditer(line):
            if _valid_vector(match.group(1)):
                found["vector"] = found["vector"] or match.group(1)
            else:
                found["invalid_vector"] = True
        zone = _TRUST_ZONE_LINE.search(line)
        if zone and found["zone"] is None:
            found["zone"] = zone.group(1)
            found["trust"] = _TRUST_NAMES.get(zone.group(2).strip().lower())
        threat = _THREAT_LINE.match(line)
        if threat and found["threat"] is None:
            found["threat"] = threat.group(1)
        level = _RISK_LEVEL.search(line)
        if level and found["risk_level"] is None:
            found["risk_level"] = level.group(1)
        bullet = _RATIONALE_BULLET.match(line)
        if bullet:
            prose.setdefault("rationale." + bullet.group(1).lower(), bullet.group(2))
        elif line.startswith("|"):
            cells = _cells(line)
            if len(cells) >= 3 and cells[2].replace("**", "").strip().lower() not in _PLACEHOLDER_TEXT:
                label = cells[0].replace("**", "").strip()
                metric = _METRIC_CELL.search(label)
                if metric and metric.group(1) in tachi_parts.METRIC_NAMES:
                    prose.setdefault("metric_rationale." + metric.group(1), cells[2])
                elif label.lower().replace(" ", "_") in tachi_parts.SUBSCORE_NAMES:
                    prose.setdefault("subscore_rationale." + label.lower().replace(" ", "_"), cells[2])
        else:
            heading = _HEADING.match(line)
            if heading and heading.group(2).strip().lower() == "reachability" and "rationale.reachability" not in prose:
                paragraph: List[str] = []
                later = number + 1
                while later < len(body):
                    text = body[later].strip()
                    later += 1
                    if (not text and paragraph) or text.startswith(("#", "|", "---")):
                        break
                    if text and not text.startswith("**"):
                        paragraph.append(text)
                if paragraph:
                    prose["rationale.reachability"] = " ".join(paragraph)
    return found


def _finding_sections(lines: List[str], outline: List[Tuple[int, int, str, int]], span: Optional[Tuple[int, int]],
                      seen: set, wanted: Any) -> Dict[str, Dict[str, Any]]:
    """§3's per-finding subsections by canonical ID (a repeated heading keeps the first).

    Every ID goes into ``seen``, but only a finding in ``wanted`` (one with a §2 row) has its subsection read. A
    subsection also holds its heading's ``component``, as written: ``### ID — component`` names one, and ``### ID: title``
    names a title, so it gives none (D9, S-12(b)).
    """
    sections: Dict[str, Dict[str, Any]] = {}
    if span is None:
        return sections
    for index, level, text, end in outline:
        if level != 3 or not span[0] < index < span[1]:
            continue
        finding_id = _heading_finding_id(text)
        if finding_id is None:
            continue
        seen.add(finding_id)
        if finding_id in wanted and finding_id not in sections:
            section = _read_subsection(lines[index + 1:end])
            named = _HEADING_COMPONENT.match(text)
            section["component"] = named.group(1) if named else None
            sections[finding_id] = section
    return sections


# ---------------------------------------------------------------------------- the SARIF's vectors

def _sarif_vectors(path: Any, issues: List[InputIssue]) -> Dict[str, str]:
    """Each valid ``cvss-vector`` of the baseline SARIF by canonical ``findingId/v1`` (the first of a repeat wins).

    A SARIF that can't be read is one issue, and its vectors are simply missing: it is a fallback source only.
    """
    raw, reason = _read_bytes(path)
    data: Any = None
    if raw is not None:
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError, RecursionError):
            reason = "not-json"
    if raw is None or reason == "not-json":
        issues.append(InputIssue(None, "cvss_vector", "unreadable-sarif", "the baseline SARIF can't be read (%s), so its vectors are not used" % reason))
        return {}
    vectors: Dict[str, str] = {}
    runs = data.get("runs") if isinstance(data, dict) else None
    for run in runs if isinstance(runs, list) else ():
        results = run.get("results") if isinstance(run, dict) else None
        for result in results if isinstance(results, list) else ():
            fingerprints = result.get("partialFingerprints") if isinstance(result, dict) else None
            properties = result.get("properties") if isinstance(result, dict) else None
            if not isinstance(fingerprints, dict) or not isinstance(properties, dict):
                continue
            finding_id, vector = fingerprints.get("findingId/v1"), properties.get("cvss-vector")
            if tachi_parts.id_matches("finding", finding_id) and isinstance(vector, str) and _valid_vector(vector.strip()):
                vectors.setdefault(tachi_parts.canonical_finding_id(finding_id), vector.strip())
    return vectors


# ---------------------------------------------------------------------------- the rows

def _frontmatter_date(text: str) -> Optional[date]:
    try:
        return tachi_scoring.parse_date(tachi_parsers.parse_frontmatter(text)["date"])
    except ValueError:
        return None


def _build_row(finding_id: str, scored: Dict[str, Any], governance: Dict[str, Any], inputs: Optional[_Inputs],
               subsection: Optional[Dict[str, Any]], sarif_vector: Optional[str], issues: List[InputIssue]) -> Optional[BaselineRow]:
    """One open row, or ``None`` (with an issue) when the file leaves it unreadable: it is scored fresh.

    A row is carried only when it holds the exploitability, scalability and reachability values and either a
    CVSS base score or a vector to check it against. It is renderer form when its Scoring Inputs hold a valid
    vector and all eight sub-scores, and legacy form otherwise. Inputs that hold some sub-scores but not all are
    an issue; a vector alone is not, because a carried legacy finding has no sub-scores to persist.
    """
    stored = scored["stored"]
    markdown_vector = None
    if inputs is not None and "cvss_vector" in inputs.values:
        markdown_vector = inputs.values["cvss_vector"]
    elif subsection is not None and subsection["vector"] is not None:
        markdown_vector = subsection["vector"]
    if subsection is not None and subsection["invalid_vector"] and markdown_vector is None:
        issues.append(InputIssue(finding_id, "cvss_vector", "invalid-value", "Section 3 names a vector that is not a full CVSS 3.1 base vector"))
    if any(stored[key] is None for key in ("exploitability", "scalability", "reachability")) or (
            stored["cvss_base"] is None and markdown_vector is None and sarif_vector is None):
        issues.append(InputIssue(finding_id, "row", "incomplete-row", "Section 2, line %d: the row lacks a score the finding needs, so it is scored fresh" % scored["line"]))
        return None
    flags: List[str] = []
    if markdown_vector is not None:
        vector, source = markdown_vector, "md"
        if sarif_vector is not None and sarif_vector != markdown_vector:
            flags.append("input:cvss_vector:sources-disagree")
    else:
        vector, source = (sarif_vector, "sarif") if sarif_vector is not None else (None, None)
    renderer = inputs is not None and not inputs.missing()
    if inputs is not None and not renderer and any(name in inputs.values for name in _SUBSCORE_FIELDS):
        # Some sub-scores but not all: a renderer-form row that lost values. A carried legacy finding has none, so it is not this.
        issues.append(InputIssue(finding_id, "scoring_inputs", "incomplete-inputs", "Scoring Inputs lacks %s, so the row is read as a legacy row" % ", ".join(inputs.missing()[:3])))
    values = inputs.values if renderer and inputs is not None else {}
    section = subsection or {}  # S-12(b)'s identity values (D9): §3's heading, `**Threat**:` line and `**Original Risk Level**:` value, else §2's cells
    trust = subsection["trust"] if subsection is not None and not renderer else values.get("reachability.trust_level")
    zone = subsection["zone"] if subsection is not None and not renderer else values.get("reachability.zone")
    return BaselineRow(
        finding_id=finding_id,
        form=_RENDERER if renderer else _LEGACY,
        cvss_vector=vector,
        vector_source=source,
        score_bounds=values.get("score_bounds"),
        subscores={name: values[address] for address, name in _SUBSCORE_FIELDS.items()} if renderer else None,
        zone=zone,
        trust_level=trust,
        auth_barriers=values.get("reachability.auth_barriers"),
        network_boundaries=values.get("reachability.network_boundaries"),
        tags_used=values.get("tags"),
        scored_on=values.get("scored_on"),
        stored=dict(stored),
        band=scored["band"] or governance.get("band"),
        owner=governance.get("owner") or scored["owner"],
        sla=governance.get("sla") or scored["sla"],
        disposition=governance.get("disposition") or scored["disposition"],
        review_date=governance.get("review_date") or scored["review_date"],
        narrative=dict(inputs.narrative) if renderer and inputs is not None else {},
        legacy_prose={} if renderer or subsection is None else {name: _decode(text) for name, text in subsection["prose"].items()},
        flags=tuple(sorted(flags)),
        component=_verbatim_text(section.get("component") or "") or scored["component"],
        threat=_verbatim_text(section.get("threat") or "") or scored["threat"],
        risk_level=_verbatim_text(section.get("risk_level") or ""),
    )


def _resolved_row(finding_id: str, scored: Dict[str, Any]) -> BaselineRow:
    """A §2a row, as its last-known values: never recomputed, so it needs no vector and no completeness (R-30)."""
    return BaselineRow(
        finding_id=finding_id, form=_LEGACY, cvss_vector=None, vector_source=None, score_bounds=None, subscores=None,
        zone=None, trust_level=None, auth_barriers=None, network_boundaries=None, tags_used=None, scored_on=None,
        stored=dict(scored["stored"]), band=scored["band"], owner=scored["owner"], sla=scored["sla"],
        disposition=scored["disposition"], review_date=scored["review_date"], narrative={}, legacy_prose={}, flags=(),
    )


def read_baseline_scores(md_path: Optional[Path], *, sarif_path: Optional[Path] = None) -> BaselineScores:
    """R-26: read a ``risk-scores.md`` as a baseline (or, for the controls stage, as this run's input), tolerantly.

    ``md_path`` is read as strict UTF-8, at most 16 MiB, through no link. It accepts ``## N.`` and
    ``## Section N:`` headings; header aliases for every column; §3 subsections headed ``### ID — …`` or
    ``### ID: …``; vectors written as ``**CVSS Vector**: `…` `` or after ``**Vector**:``; §4's table; §2a's
    resolved rows; and the renderer's ``### Scoring Inputs``. An ID cell that isn't one allow-listed ID yields no
    row. A legacy vector comes from the markdown, or else from ``sarif_path``'s ``cvss-vector`` keyed by
    ``findingId/v1``, and when both exist and differ the markdown's is used and the row is flagged
    ``input:cvss_vector:sources-disagree``.

    A file that is missing, isn't UTF-8, is too large or yields no row comes back with ``readable=False`` and the
    reason, and counts as missing (S-12(d)). A single unreadable row is an entry of ``issues`` and is scored
    fresh. Narrative text is decoded with ``tachi_parsers.decode_references`` and returned unvalidated; a legacy
    file's prose comes back in ``legacy_prose`` as evidence-class text, and no number is read from either.

    **Values by class (ruled at W2).** The owner, like the component and the threat, is free text that a human may
    edit: it is read as its cell holds it, decoded once and stripped at its edges, with its ``**`` kept (``_verbatim_text``).
    The SLA and the disposition are a duration and an enum, so their emphasis is dropped (``_text_value``). The row also
    records what S-12(b) lets the baseline supply to a carried finding whose form lacks it (D9): ``component`` from §3's
    heading ``### ID — component`` (a ``### ID: title`` heading names a title, not a component) or else §2's cell,
    ``threat`` from §3's ``**Threat**:`` line or else §2's cell, and ``risk_level`` from §3's ``**Original Risk Level**:``
    value. §2a's RESOLVED rows record none of them.
    """
    raw, reason = _read_bytes(md_path)
    if raw is None:
        return _unreadable(reason or "missing")
    try:
        text = raw.decode("utf-8").lstrip("\ufeff")
    except UnicodeDecodeError:
        return _unreadable("not-utf8")
    lines = text.split("\n")
    issues = _IssueLog()
    seen: set = set()
    outline = _outline(lines)
    sections = _section_ranges(outline)
    open_scored = _scored_rows(lines, sections.get((2, "")), "Section 2", issues, seen)
    resolved_scored = _scored_rows(lines, sections.get((2, "a")), "Section 2a", issues, seen)
    governance = _governance_rows(lines, sections.get((4, "")), issues, seen)
    inputs = _scoring_inputs(lines, outline, issues, seen)
    subsections = _finding_sections(lines, outline, sections.get((3, "")), seen, open_scored)
    sarif = _sarif_vectors(sarif_path, issues) if sarif_path is not None else {}

    rows: Dict[str, BaselineRow] = {}
    for finding_id in sorted(open_scored, key=tachi_parts.finding_sort_key):
        row = _build_row(finding_id, open_scored[finding_id], governance.get(finding_id, {}), inputs.get(finding_id),
                         subsections.get(finding_id), sarif.get(finding_id), issues)
        if row is not None:
            rows[finding_id] = row
    resolved = {finding_id: _resolved_row(finding_id, resolved_scored[finding_id])
                for finding_id in sorted(resolved_scored, key=tachi_parts.finding_sort_key)}
    if not rows and not resolved:
        return _unreadable("no-rows", issues.finished(), frozenset(seen))
    form = _RENDERER if any(row.form == _RENDERER for row in rows.values()) else _LEGACY
    return BaselineScores(True, None, form, rows, resolved, frozenset(seen), _frontmatter_date(text), issues.finished())


# =============================================================================
# S-13: the one tag source (D2)
# =============================================================================

Matcher = Callable[[str, Sequence[str]], Optional[str]]


def recompute_tags(architecture_text: str, open_rows: Sequence[Mapping[str, str]], matcher: Matcher) -> Mapping[str, Tuple[str, ...]]:
    """The populator's join, run over the reference set's open rows: each canonical ID -> its component's tags.

    It calls ``tachi_parsers.parse_component_asset_map(architecture_text)`` and then
    ``matcher(component, keys)`` for each row, as ``populate-affected-assets.py``'s ``compute_affected_assets``
    does. A row takes the matched component's tags as the map holds them (sorted, lowercase, from the closed six),
    or ``()`` when nothing matches. ``matcher`` is the populator's ``match_component``, unchanged: the caller
    loads that script by path, so this module stays over ``tachi_scoring`` and ``tachi_parsers`` (D5).

    A row whose ID is not an allow-listed finding ID raises ``ValueError``: the reference-set wrapper has
    already checked every ID. A repeated canonical ID keeps its first row.
    """
    asset_map = tachi_parsers.parse_component_asset_map(architecture_text)
    keys = list(asset_map.keys())
    tags: Dict[str, Tuple[str, ...]] = {}
    for row in open_rows:
        finding_id = tachi_parts.canonical_finding_id(row["id"])
        if finding_id in tags:
            continue
        matched = matcher((row.get("component") or "").strip(), keys)
        tags[finding_id] = tuple(asset_map.get(matched, ())) if matched is not None else ()
    return tags


@dataclass(frozen=True)
class TagSource:
    source: str                          # "block" | "recomputed" | "block-unverified" | "none"
    tags: Mapping[str, Tuple[str, ...]]  # one entry per open ID, () when none
    warning: Optional[str]
    cause: Optional[str]


def _tag_tuple(tags: Sequence[str]) -> Tuple[str, ...]:
    return tuple(sorted({str(tag).strip().lower() for tag in tags} - {""}))


def _canonical_tags(tags_by_id: Mapping[str, Sequence[str]]) -> Optional[Dict[str, Tuple[str, ...]]]:
    """``tags_by_id`` keyed by canonical ID, with each tag list lowercased, deduplicated and sorted.

    A key that is not an allow-listed finding ID is ignored. Two spellings of one canonical ID (``AGP-1`` and
    ``AGP-01``) are a duplicate in one input (D3), so the whole mapping is refused: ``None``.
    """
    canonical: Dict[str, Tuple[str, ...]] = {}
    for key, tags in tags_by_id.items():
        if not tachi_parts.id_matches("finding", key):
            continue
        finding_id = tachi_parts.canonical_finding_id(key)
        if finding_id in canonical:
            return None
        canonical[finding_id] = _tag_tuple(tags)
    return canonical


def select_tag_source(*, open_ids: Sequence[str], block: Mapping[str, Sequence[str]],
                      recomputed: Optional[Mapping[str, Sequence[str]]]) -> TagSource:
    """S-13: the one source of asset tags for a run. It decides once, never per finding, and never mixes two sources.

    ``block`` is the input ``threats.md``'s ``## Affected Assets`` block as ``sarif_common.parse_affected_assets``
    reads it (``{}`` when absent), and ``recomputed`` is ``recompute_tags``'s result, or ``None`` when the run has
    no architecture file. The outcomes:

    * ``block``: the block equals the recomputation on every open ID;
    * ``recomputed``: the block is absent, differs, or misses an open ID (``cause`` ``block-absent``,
      ``block-differs`` or ``block-missing-id``), with a warning;
    * ``block-unverified``: there is no architecture file, so the block is used as it is, with each tag outside
      the closed set dropped (``cause`` ``no-architecture-file``). It always warns (ruled at W2): the stage record has
      no other key that names the tag source, so the warning is the only trace that the elevation was unverified. The
      text says so, and names each tag that was dropped;
    * ``none``: neither source. No finding is elevated, and the warning says so (``cause`` ``no-tag-source``).

    Every outcome except ``block`` warns, and the renderer records each warning as ``tag-source:<cause>``. No outcome
    stops the run. Every open ID has an entry in ``tags``, ``()`` when it has no tags.
    """
    ids = [tachi_parts.canonical_finding_id(finding_id) for finding_id in open_ids]
    block_tags = _canonical_tags(block)
    if recomputed is None:
        if not block_tags:
            return TagSource("none", {finding_id: () for finding_id in ids},
                             "no asset tags were applied, so no finding was elevated: the run has no architecture file "
                             "and its threats.md has no usable Affected Assets block", "no-tag-source")
        used: Dict[str, Tuple[str, ...]] = {}
        dropped = set()
        for finding_id in ids:
            tags = block_tags.get(finding_id, ())
            used[finding_id] = tuple(tag for tag in tags if tag in tachi_scoring.TAG_FORCES)
            dropped.update(tag for tag in tags if tag not in tachi_scoring.TAG_FORCES)
        warning = ("the Affected Assets block's tags were applied unverified, because the run has no architecture file to check them against"
                   + ("; the block names tags outside the closed set, which were ignored: %s" % ", ".join(sorted(dropped)) if dropped else ""))
        return TagSource("block-unverified", used, warning, "no-architecture-file")
    fresh = _canonical_tags(recomputed) or {}
    expected = {finding_id: fresh.get(finding_id, ()) for finding_id in ids}
    if block_tags is None:
        cause, why = "block-differs", "names one finding under two spellings"
    elif not block_tags:
        cause, why = "block-absent", "has no Affected Assets block"
    elif any(finding_id not in block_tags for finding_id in ids):
        cause, why = "block-missing-id", "lacks an open finding"
    elif any(block_tags[finding_id] != expected[finding_id] for finding_id in ids):
        cause, why = "block-differs", "differs from the architecture file's asset tags"
    else:
        return TagSource("block", expected, None, None)
    return TagSource("recomputed", expected,
                     "the input threats.md's Affected Assets block %s, so the asset tags were recomputed from the architecture file" % why,
                     cause)


# =============================================================================
# R-25 and the CVSS chain (D10)
# =============================================================================

@dataclass(frozen=True)
class CvssChain:
    base: Decimal                                    # base(v), FIRST's equations (tachi_scoring)
    score_bounds: Optional[Tuple[Decimal, Decimal]]
    assessed: Decimal                                # base, clamped to score_bounds when they're given
    forced: bool                                     # a tag forces a bit (asset-modifiers.md:13-22)
    elevated_vector: Optional[str]                   # elevate(v), when forced
    elevated_base: Optional[Decimal]                 # base(elevate(v)), when forced
    cvss_base: Decimal                               # the final score
    clamp_cause: Optional[str]                       # "bound" | "ceiling": the clamp that set cvss_base


def _decimal_score(value: Any, what: str) -> Decimal:
    """``value`` if it is a ``Decimal`` or an ``int``. A float never enters stored-value arithmetic (D5)."""
    if isinstance(value, bool) or not isinstance(value, (Decimal, int)):
        raise TypeError("%s must be a Decimal, not %s" % (what, type(value).__name__))
    return Decimal(value)


def asset_outcome(assessed: Decimal, vector: str, tags: Sequence[str]) -> Decimal:
    """R-25's t(a): ``max(a, min(base(elevate(v)), 9.2))`` when a tag forces a bit, otherwise ``a``.

    "A tag forces a bit" means a tag from the closed six is present: each forces its bits to ``H`` (floor only),
    whether or not ``v`` already carries them. So the modifier never lowers a score, and a finding assessed above
    9.2 keeps it. A tag outside the closed six raises ``ValueError`` (``tachi_scoring.elevate``): the tags come from
    :func:`select_tag_source`, which only gives the closed six.
    """
    score = _decimal_score(assessed, "the assessed score")
    tags = tuple(tags)
    if not tags:
        return score
    elevated = tachi_scoring.base_score(tachi_scoring.elevate(vector, tags))
    return max(score, min(elevated, tachi_scoring.MODIFIER_CEILING))


def cvss_chain(vector: str, *, tags: Sequence[str], score_bounds: Optional[Tuple[Decimal, Decimal]]) -> CvssChain:
    """D10's fresh-scoring chain, step by step: the base, the bound clamp, the elevation and the ceiling.

    ``assessed`` is ``base(v)`` clamped to ``score_bounds`` when they are given: a NEW finding in a baseline-aware run
    passes its own category's bounds (``tachi_scoring.bounds``), and a carried renderer-form row passes its stored
    ones. With a tag, ``cvss_base`` is :func:`asset_outcome`, so the elevated score lifts a bound-clamped one
    (the clamp comes first, and the modifier is meant to exceed it). ``clamp_cause`` names the clamp that set
    ``cvss_base``: ``bound`` when the bounds did, ``ceiling`` when the 9.2 ceiling cut the elevated score, otherwise
    ``None``. A vector that is not a full CVSS 3.1 base vector raises ``ValueError``.
    """
    tags = tuple(tags)
    base = tachi_scoring.base_score(vector)
    assessed = base if score_bounds is None else max(score_bounds[0], min(base, score_bounds[1]))
    if not tags:
        return CvssChain(base, score_bounds, assessed, False, None, None, assessed, "bound" if assessed != base else None)
    elevated_vector = tachi_scoring.elevate(vector, tags)
    elevated_base = tachi_scoring.base_score(elevated_vector)
    capped = min(elevated_base, tachi_scoring.MODIFIER_CEILING)
    if capped > assessed:
        cvss_base, cause = capped, "ceiling" if elevated_base > tachi_scoring.MODIFIER_CEILING else None
    else:
        cvss_base, cause = assessed, "bound" if assessed != base else None
    return CvssChain(base, score_bounds, assessed, True, elevated_vector, elevated_base, cvss_base, cause)


# =============================================================================
# D10: the vector check on a carried finding
# =============================================================================

@dataclass(frozen=True)
class VectorCheck:
    cvss_base: Optional[Decimal]   # the value to render: the stored one kept, or the corrected or retagged one
    flag: Optional[str]            # one kind:field:cause, or None when the carried value passes
    step: str                      # "renderer", or "1" to "6": D10's legacy step that decided


# Each category's ±1.0 bounds around its default score, for the N17c test of another category's clamp.
_BOUNDS_BY_CATEGORY = {
    category: tachi_scoring.bounds(tachi_scoring.default_score(category))
    for category in tachi_scoring.CATEGORY_DEFAULT_VECTORS
}


def _clamp(score: Decimal, bounds: Tuple[Decimal, Decimal]) -> Decimal:
    return max(bounds[0], min(score, bounds[1]))


def check_carried_vector(row: BaselineRow, *, tags: Sequence[str]) -> VectorCheck:
    """D10's check of a carried finding's CVSS base score against its vector, under this run's ``tags`` (R-9, R-25).

    **Renderer form.** The chain is recomputed from the stored vector, ``score_bounds`` and ``tags``. A different
    value is ``corrected:cvss_base:vector``, unless recomputing with the baseline's ``tags_used`` gives the stored
    value: then the tags alone moved it, and it is ``retagged:cvss_base:asset-tags`` (ruling A).

    **Legacy form.** The first matching step of D10's list decides, and this run's tags are part of every test (PM
    plan review, finding 2). With ``v`` the vector, ``s`` the stored score, ``a`` a candidate assessed score (``base(v)``
    or its own category's bound clamp) and ``t(a)`` R-25's outcome under ``tags``:

    1. no vector: ``unverifiable:cvss_base:no-vector``, ``s`` kept;
    2. a tag, ``v`` already carries its forced bits, and 9.2 < ``s`` <= ``base(v)``: ``unchecked:cvss_base:assessed-unrecorded``;
    3. ``s`` = ``t(a)`` for either ``a``, or a tag with ``s`` = 9.2 and ``base(elevate(v))`` above 9.2: passes;
    4. a tag, and ``s`` = ``a`` < ``t(a)``: ``retagged:cvss_base:asset-tags``, to ``t(a)``;
    5. ``s`` equals another category's bound clamp of ``base(v)`` (``unchecked:cvss_base:bound-n17c``), or a tag
       with 9.2 < ``s`` < ``base(elevate(v))`` (``unchecked:cvss_base:assessed-unrecorded``), ``s`` kept;
    6. otherwise ``corrected:cvss_base:vector``, to ``t(base(v))``.

    A stored score that is missing, where a vector can give one, is rendered from the chain and flagged
    ``input:cvss_base:missing`` (step ``renderer`` or ``6``). The stored score is compared as written and never
    rounded, so an off-grid or out-of-range one is simply corrected. ``tags`` must be in the closed six.
    """
    tags = tuple(tags)
    vector, stored = row.cvss_vector, row.stored.get("cvss_base")
    if vector is None:
        return VectorCheck(stored, "unverifiable:cvss_base:no-vector", "1")
    if row.form == _RENDERER:
        return _check_renderer_vector(row, vector, stored, tags)
    return _check_legacy_vector(row, vector, stored, tags)


def _check_renderer_vector(row: BaselineRow, vector: str, stored: Optional[Decimal], tags: Tuple[str, ...]) -> VectorCheck:
    now = cvss_chain(vector, tags=tags, score_bounds=row.score_bounds).cvss_base
    if stored is None:
        return VectorCheck(now, "input:cvss_base:missing", "renderer")
    if stored == now:
        return VectorCheck(stored, None, "renderer")
    then = cvss_chain(vector, tags=row.tags_used or (), score_bounds=row.score_bounds).cvss_base
    if stored == then:
        return VectorCheck(now, "retagged:cvss_base:asset-tags", "renderer")
    return VectorCheck(now, "corrected:cvss_base:vector", "renderer")


def _check_legacy_vector(row: BaselineRow, vector: str, stored: Optional[Decimal], tags: Tuple[str, ...]) -> VectorCheck:
    base = tachi_scoring.base_score(vector)
    own = tachi_scoring.category_for_prefix(row.finding_id.partition("-")[0])
    candidates = [base]
    if _clamp(base, _BOUNDS_BY_CATEGORY[own]) != base:
        candidates.append(_clamp(base, _BOUNDS_BY_CATEGORY[own]))
    outcomes = [asset_outcome(candidate, vector, tags) for candidate in candidates]
    if stored is None:
        return VectorCheck(outcomes[0], "input:cvss_base:missing", "6")
    ceiling = tachi_scoring.MODIFIER_CEILING
    elevated = tachi_scoring.elevate(vector, tags) if tags else vector
    elevated_base = tachi_scoring.base_score(elevated)
    if tags and elevated == vector and ceiling < stored <= base:   # step 2: R-25's legacy case
        return VectorCheck(stored, "unchecked:cvss_base:assessed-unrecorded", "2")
    if stored in outcomes or (tags and stored == ceiling and elevated_base > ceiling):   # step 3
        return VectorCheck(stored, None, "3")
    if tags:                                                       # step 4: the stored score lacks the elevation
        for candidate, outcome in zip(candidates, outcomes):
            if stored == candidate < outcome:
                return VectorCheck(outcome, "retagged:cvss_base:asset-tags", "4")
    if any(stored == _clamp(base, bounds) for category, bounds in _BOUNDS_BY_CATEGORY.items() if category != own):
        return VectorCheck(stored, "unchecked:cvss_base:bound-n17c", "5")   # step 5: a possible cross-category peer
    if tags and ceiling < stored < elevated_base:
        return VectorCheck(stored, "unchecked:cvss_base:assessed-unrecorded", "5")
    return VectorCheck(outcomes[0], "corrected:cvss_base:vector", "6")   # step 6, to t(base(v))


# =============================================================================
# R-31: routing, peers, dates and governance (D2, D9, ruling A)
# =============================================================================

@dataclass(frozen=True)
class ScorerRouting:
    to_agent: Tuple[str, ...]         # non-peers that are NEW or UPDATED, or have no usable baseline row
    carried: Tuple[str, ...]          # UNCHANGED findings with a usable row, peers included
    copy_primary: Mapping[str, str]   # every other peer -> its group's primary
    carried_peers: Mapping[str, str]  # each carried peer -> its primary, for the divergence check
    status: Mapping[str, str] = field(default_factory=dict)  # W2: each open ID -> the status it was routed under


def route_scorer_units(open_rows: Sequence[Mapping[str, str]], *, groups: Sequence[Mapping[str, object]],
                       baseline: Optional[BaselineScores], lacking: Optional[Mapping[str, Sequence[str]]] = None) -> ScorerRouting:
    """The one partition of a scorer run's open findings, for the planner (T044) and the renderer (T028, T045) alike.

    ``open_rows`` are the reference set's open rows (at least ``id`` and ``delta_status``, in S-2 order), and
    ``groups`` is ``tachi_parsers.parse_correlation_groups(...)["groups"]`` filtered to the open IDs: its result is used
    as it comes, because D8's rules (order, the claim, the primary, the two-member minimum) are applied there and
    nowhere else. A peer is a member that is not its group's primary. A row without a usable ``delta_status`` counts as
    NEW, unless ``lacking`` says its form has none (below). A usable baseline row is an entry of ``baseline.rows`` (an
    unreadable baseline has none).

    **S-12(b)'s derivation (ruled at W2; ADR-050 D9).** ``lacking`` is the reference set's ``lacking`` map, canonical ID to
    the names of the values its form lacks, and for D8's SARIF fallback ``{id: ["delta_status"]}`` for every member. For an
    ID whose names include ``delta_status`` the status is derived here and nowhere else: UNCHANGED, so carried, when
    ``baseline.rows`` holds the ID (never its RESOLVED rows, an unreadable row or another finding's), and NEW otherwise, so
    the agent scores it fresh and ruling B's test applies to it as to any NEW finding. The default, ``None``, changes no
    caller.

    * ``carried``: an UNCHANGED finding with a usable row, a peer or not. Its inputs are inherited (D9);
    * ``carried_peers``: each carried peer and its primary, whose composites ``peer_divergence`` compares;
    * ``copy_primary``: every other peer (NEW, UPDATED, or with no usable row) and its primary, whose values it copies;
    * ``to_agent``: every other finding. A NEW finding is never carried, however its ID sits in the baseline (ruling B);
    * ``status``: every open ID and the status it was routed under, the Section 7 value or the derived one. The renderer
      takes each row's status from it, so it can't disagree with the planner.
    """
    usable = baseline.rows if baseline is not None else {}
    derive = frozenset(tachi_parts.canonical_finding_id(finding_id) for finding_id, names in (lacking or {}).items()
                       if tachi_parts.id_matches("finding", finding_id) and "delta_status" in names)
    status: Dict[str, str] = {}
    for row in open_rows:
        finding_id = tachi_parts.canonical_finding_id(row["id"])
        if finding_id in derive:
            status.setdefault(finding_id, "UNCHANGED" if finding_id in usable else "NEW")
        else:
            status.setdefault(finding_id, _delta_status(row.get("delta_status")))
    primary_of: Dict[str, str] = {}
    for group in groups:
        primary = group["primary"]
        for member in group["members"]:
            if member != primary and member in status and primary in status:
                primary_of.setdefault(member, primary)
    to_agent: List[str] = []
    carried: List[str] = []
    copy_primary: Dict[str, str] = {}
    carried_peers: Dict[str, str] = {}
    for finding_id, state in status.items():
        primary = primary_of.get(finding_id)
        if state == "UNCHANGED" and finding_id in usable:
            carried.append(finding_id)
            if primary is not None:
                carried_peers[finding_id] = primary
        elif primary is not None:
            copy_primary[finding_id] = primary
        else:
            to_agent.append(finding_id)
    return ScorerRouting(tuple(to_agent), tuple(carried), copy_primary, carried_peers, status)


def _delta_status(value: Any) -> str:
    status = tachi_parsers.normalize_delta_status(value) if isinstance(value, str) else ""
    return status if status in ("NEW", "UPDATED", "UNCHANGED") else "NEW"


def peer_divergence(*, peer_composite: Decimal, primary_id: str, primary_composite: Decimal) -> Optional[str]:
    """``divergent:composite_score:primary=<ID>`` when an UNCHANGED peer's composite differs from its primary's (R-4, R-31)."""
    if _decimal_score(peer_composite, "the peer's composite") != _decimal_score(primary_composite, "the primary's composite"):
        return "divergent:composite_score:primary=%s" % primary_id
    return None


@dataclass(frozen=True)
class ScoringDate:
    value: Optional[date]
    flag: Optional[str]


def _before(day: date, sla: str) -> Optional[date]:
    """``day`` less the SLA's days, or ``None`` when the SLA is unparseable or the date would pass year 1."""
    try:
        return day - timedelta(days=tachi_scoring.sla_days(sla))
    except (ValueError, OverflowError):
        return None


def _after(day: date, sla: str) -> Optional[date]:
    """``day`` plus the SLA's days (``tachi_scoring``'s date arithmetic), or ``None`` when it can't be added."""
    try:
        return tachi_scoring.parse_date(tachi_scoring.review_date(day.isoformat(), sla))
    except ValueError:
        return None


def _known_original(row: BaselineRow) -> Optional[date]:
    """The stored scored-on date, or the stored review date less the stored SLA. No fallback, and no flag."""
    if row.scored_on is not None:
        return row.scored_on
    if row.review_date is not None and row.sla is not None:
        return _before(row.review_date, row.sla)
    return None


def original_scoring_date(row: BaselineRow, *, baseline_date: Optional[date]) -> ScoringDate:
    """The date a carried finding's SLA clock started (R-5): its stored scored-on date, else its stored review date
    less its stored SLA (a legacy row). If neither can be had, D9's fallbacks apply in order:

    1. the baseline file's frontmatter date, flagged ``corrected:review_date:baseline-date``;
    2. ``None``, flagged ``unchecked:review_date:scoring-date-unknown``, which tells ``governance_for`` to keep the
       stored review date.

    The last fallback, the run date plus the SLA (``corrected:review_date:clock-restarted``), is ``governance_for``'s.
    """
    known = _known_original(row)
    if known is not None:
        return ScoringDate(known, None)
    if baseline_date is not None:
        return ScoringDate(baseline_date, "corrected:review_date:baseline-date")
    return ScoringDate(None, "unchecked:review_date:scoring-date-unknown")


_BAND_RANK = {name: rank for rank, name in enumerate(reversed(list(tachi_scoring.SEVERITY_BANDS)))}   # Low is 0
_BAND_CHANGES = ("none", "corrected", "retagged-up", "retagged-down")


def classify_band_change(*, stored_band: Optional[str], rendered_band: str, band_with_baseline_tags: Optional[str]) -> str:
    """``none``, ``corrected``, ``retagged-up`` or ``retagged-down`` (ruling A).

    The band changed only when ``stored_band`` is a band and differs from ``rendered_band``. The tags alone explain
    it when recomputing with the baseline's recorded tags (``band_with_baseline_tags``; no tags for a legacy row)
    gives the stored band: then it is a retag, up or down by band order. Any other change is a correction.
    """
    if rendered_band not in _BAND_RANK:
        raise ValueError("not a severity band: %r" % (rendered_band,))
    if stored_band not in _BAND_RANK or stored_band == rendered_band:
        return "none"
    if band_with_baseline_tags != stored_band:
        return "corrected"
    return "retagged-up" if _BAND_RANK[rendered_band] > _BAND_RANK[stored_band] else "retagged-down"


@dataclass(frozen=True)
class Governance:
    owner: str
    sla: str
    disposition: str
    review_date: date
    scored_on: date
    flags: Tuple[str, ...]


# The schema's field names, as a flag's <field> (schemas/risk-scoring.yaml).
_SLA_FIELD, _DISPOSITION_FIELD, _REVIEW_FIELD = "remediation_sla", "risk_disposition", "review_date"
_HUMAN_DISPOSITIONS = frozenset(("accept", "transfer"))


def _stored_band(row: BaselineRow) -> Optional[str]:
    if row.band in tachi_scoring.SEVERITY_BANDS:
        return row.band
    composite = row.stored.get("composite")
    try:
        return tachi_scoring.band(composite) if composite is not None else None
    except (TypeError, ValueError):
        return None


def _fresh_governance(rendered_band: str, run_date: date) -> Governance:
    rule = tachi_scoring.SEVERITY_BANDS[rendered_band]
    review = tachi_scoring.parse_date(tachi_scoring.review_date(run_date.isoformat(), rule["sla"]))
    return Governance("Unassigned", rule["sla"], rule["disposition"], review, run_date, ())


def governance_for(status: str, *, rendered_band: str, run_date: date, row: Optional[BaselineRow], band_change: str,
                   baseline_date: Optional[date]) -> Governance:
    """The governance fields of one finding (D9: R-5, R-31 and ruling A). ``status`` is NEW, UPDATED or UNCHANGED.

    * **A fresh finding** (NEW, or one with no usable baseline ``row``; a NEW finding whose ID the baseline used does
      not take that row's owner, ruling B) is ``Unassigned``, takes the rendered band's SLA and disposition, and is
      scored on ``run_date``, so its review date is ``run_date`` plus the SLA.
    * **The owner** of a carried finding is always its stored owner, and is never flagged.
    * **Overrides** are an Accept or Transfer disposition, or an SLA or disposition that differs from the *stored*
      band's default. They are carried verbatim and flagged ``override:remediation_sla:human`` or
      ``override:risk_disposition:human``. The other two follow the rendered band.
    * **The review date** is kept when the SLA is an override ("an SLA override still keeps its review date") and
      when the band holds. A band change restarts an UPDATED finding's clock (``run_date`` plus the SLA). On an
      UNCHANGED finding it follows ``band_change``: ``corrected`` and ``retagged-down`` give the original scoring
      date plus the new SLA (R-5), through ``original_scoring_date``'s fallbacks and, last, the run date plus the SLA
      (``corrected:review_date:clock-restarted``); ``retagged-up`` gives the run date plus the new SLA unless the
      stored review date is earlier, which is kept (ruling A).
    * **Flags.** Each SLA, disposition or review date that moves on an UNCHANGED finding is flagged
      ``corrected:<field>:follows-band``, or ``retagged:<field>:asset-tags`` when the tags moved the band. A value
      absent from the baseline is filled silently, except a missing review date (``input:review_date:missing``).
    * ``scored_on`` is the date that the rendered review date's clock started, so the next run can read it back.

    Raises ``ValueError`` for a ``status``, ``rendered_band`` or ``band_change`` it doesn't know.
    """
    if status not in ("NEW", "UPDATED", "UNCHANGED"):
        raise ValueError("not a delta status: %r" % (status,))
    if rendered_band not in tachi_scoring.SEVERITY_BANDS:
        raise ValueError("not a severity band: %r" % (rendered_band,))
    if band_change not in _BAND_CHANGES:
        raise ValueError("not a band change: %r" % (band_change,))
    if status == "NEW" or row is None:
        return _fresh_governance(rendered_band, run_date)
    rule = tachi_scoring.SEVERITY_BANDS[rendered_band]
    stored_band = _stored_band(row)
    defaults = tachi_scoring.SEVERITY_BANDS.get(stored_band) if stored_band is not None else None
    sla_override = row.sla is not None and defaults is not None and row.sla != defaults["sla"]
    disposition_override = row.disposition is not None and (
        row.disposition.strip().lower() in _HUMAN_DISPOSITIONS or (defaults is not None and row.disposition != defaults["disposition"]))
    sla = row.sla if sla_override else rule["sla"]
    disposition = row.disposition if disposition_override else rule["disposition"]
    flags: List[str] = []
    if sla_override:
        flags.append("override:%s:human" % _SLA_FIELD)
    if disposition_override:
        flags.append("override:%s:human" % _DISPOSITION_FIELD)
    owner = row.owner or "Unassigned"
    dated = sla if _after(run_date, sla) is not None else rule["sla"]   # an unparseable override still needs days
    stored_review = row.review_date
    changed = band_change != "none"

    if sla_override and stored_review is not None:
        scored_on = _known_original(row) or _before(stored_review, dated) or run_date
        review = stored_review
    elif status == "UPDATED" and changed:
        scored_on, review = run_date, _after(run_date, dated)
    elif not changed and stored_review is not None:
        scored_on, review = _known_original(row) or _before(stored_review, dated) or run_date, stored_review
    elif band_change == "retagged-up":
        restarted = _after(run_date, dated)
        if stored_review is None or (restarted is not None and restarted <= stored_review):
            scored_on, review = run_date, restarted
            if stored_review is None:
                flags.append("input:review_date:missing")
        else:
            scored_on, review = _known_original(row) or _before(stored_review, dated) or run_date, stored_review
    else:
        scored_on, review = _from_original(row, dated, stored_review, run_date, baseline_date, flags)
        if stored_review is None and not any(flag.split(":")[1] == _REVIEW_FIELD for flag in flags):
            flags.append("input:review_date:missing")
    if review is None:   # the run date plus the SLA passed year 9999
        raise ValueError("the review date for %s is past 9999-12-31" % run_date)
    if status == "UNCHANGED":
        kind, cause = ("retagged", "asset-tags") if band_change.startswith("retagged") else ("corrected", "follows-band")
        for name, was, now in ((_SLA_FIELD, row.sla, sla), (_DISPOSITION_FIELD, row.disposition, disposition),
                               (_REVIEW_FIELD, stored_review, review)):
            if was is not None and was != now and not any(flag.split(":")[1] == name for flag in flags):
                flags.append("%s:%s:%s" % (kind, name, cause))
    return Governance(owner, sla, disposition, review, scored_on, tuple(sorted(set(flags))))


def _from_original(row: BaselineRow, sla: str, stored_review: Optional[date], run_date: date, baseline_date: Optional[date],
                   flags: List[str]) -> Tuple[date, Optional[date]]:
    """``(scored_on, review date)`` counted from the original scoring date, by D9's rungs (R-5)."""
    original = original_scoring_date(row, baseline_date=baseline_date)
    if original.value is not None:
        review = _after(original.value, sla)
        if review is not None:
            if original.flag is not None:
                flags.append(original.flag)
            return original.value, review
    elif stored_review is not None and original.flag is not None:   # rung 2: the stored review date is kept
        flags.append(original.flag)
        return _before(stored_review, sla) or run_date, stored_review
    flags.append("corrected:review_date:clock-restarted")   # rung 3
    return run_date, _after(run_date, sla)
