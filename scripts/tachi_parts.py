"""Part-file loader, validator and guards for the F-374 pipeline (ADR-050 D3).

Every agent-written file the shipped scripts read is untrusted input (NFR-10). This
helper is the one place that decides what such a file may contain. It is imported,
never run, and it is stdlib-only. It imports neither ``sarif_common`` nor
``tachi_parsers`` (C1), so both of them can import it without a cycle.

Written in two slices (T012, T013). **Slice 1, below, is the identifier module:**

* ``ID_PATTERNS``: the source text of every allow-list, as the contracts spell it.
  Each is matched as an ASCII ``re.fullmatch`` with ``[0-9]``, never ``\\d`` or ``$``
  (KB 24: ``\\d`` admits non-ASCII digits and ``$`` admits a trailing newline).
* ``id_matches(kind, value)``: the allow-list test. ``kind`` is a key of ``ID_PATTERNS``:
  ``finding``, ``plan``, ``batch``, ``dispatch``, ``group``, ``chain`` or ``language``.
* ``FINDING_PREFIXES``, ``canonical_finding_id(value)`` and ``finding_sort_key(value)``:
  the canonical spelling (``AGP-01`` is ``AGP-1``) and S-2's total order.
* ``PATH_MAX_BYTES``, ``path_problem(value, allow_absolute=False)`` and
  ``path_parts(value, allow_absolute=False)``: ADR-050 D7's syntactic path rule, for
  evidence ``file`` values (relative) and, with ``allow_absolute=True``, for the URI
  resolver's candidates. The filesystem checks (lstat walk, spelling) are not here.

**Strict loader and validators (T012, slice 2):**

* ``KEY_SETS`` (name -> required keys, optional keys): every closed key set of the part,
  overflow, batch-input, plan, plan-pointer and stage-record schemas, the two PR 1 stage
  payloads and their sub-objects, in the contracts' order. ``STAGE_AGENTS``, ``COUNT_KEYS``,
  ``SUBSCORE_NAMES``, ``METRIC_NAMES``, ``CONTROL_CATEGORIES`` and ``NARRATIVE_FIELDS`` (the 24
  flag fields) are the closed values. T010 drift-tests the shared reference against these.
* ``under(base, path)`` and ``path_guard_problem(path, out)``: KB 24's identity checks (step 1).
* ``load_json(path, out, max_bytes)``: steps 1 to 4. Raises ``PartError(kind, detail)`` with
  ``kind`` ``missing``, ``unparseable`` or ``invalid``.
* ``read_part(path, out, plan_id, batch_id, stage, agent_type, finding_ids)`` and
  ``classify_part(obj, ...)``: steps 1 to 10, returning a ``PartResult`` whose ``state`` is
  ``done``, ``missing``, ``overflow``, ``unparseable`` or ``invalid``. A ``done`` part comes back
  with canonical IDs and its items in the planned order; ``flags`` maps each canonical ID to its
  sorted ``input:<field>:truncated`` flags and ``counts`` totals the cuts. Step 11 (the narrative
  grammar, numeral ban and fallback) is T013's and plugs into ``_narrative``.
* ``validate_plan``, ``validate_pointer``, ``validate_batch_input`` and ``validate_stage_record``
  return the object they were given, or raise ``PartError("invalid", ...)``.
  ``read_document(path, out, schema)`` loads one of those four documents and validates it.

**I/O helpers and D3's layout (T013, slice 1):**

* ``atomic_write(path, data)``: a temp file in the target's directory, then ``os.replace``. The file gets the
  mode an ordinary write would (``0666 & ~umask``), and ``str`` is written as UTF-8 with no newline translation.
* ``sha256_hex(data)``; ``file_digest(path)``, lowercase hex with no prefix, the form of ``plan_digest`` and of
  the plan's ``sha256`` fields; ``input_digest(obj)``, ``sha256:`` and the hex digest of ``obj``'s canonical JSON
  (sorted keys, no spaces, ASCII), the form of the stamp's and the stage record's ``input_digest``.
* ``stamp_comment(renderer, digest)`` and ``read_stamp(text)``: ADR-050 D4's provenance comment and its reader.
  The last comment in the text wins, and a malformed last one is no stamp. ``VERSION`` is the version it carries.
* The layout builders, ADR-050 D3 (P-6). Each returns an absolute path as ``str`` and raises ``ValueError`` for a
  stage, ID, attempt or file name that is not allow-listed, so a hostile value never becomes part of a path.
  ``out`` is ``--out``; ``BUILD_DIR`` is ``.tachi-build``; ``PLAN_SUBDIRS`` is ``inputs``, ``parts``,
  ``preimage``, ``staged`` and ``failed``; a file ``name`` is one of ``CANONICAL_OUTPUTS[stage]``::

      stage_dir(out, stage)                            <out>/.tachi-build/<stage>
      pointer_path(out, stage)                         <stage dir>/current.json
      plan_dir(out, stage, plan_id)                    <stage dir>/<plan_id>
      plan_subdir(out, stage, plan_id, name)           <plan dir>/<name>, name in PLAN_SUBDIRS
      plan_path(out, stage, plan_id)                   <plan dir>/plan.json
      input_path(out, stage, plan_id, batch_id)        <plan dir>/inputs/<batch_id>.json
      part_path(out, stage, plan_id, batch_id, attempt)   <plan dir>/parts/<batch_id>.a<attempt>.json
      stage_record_path(out, stage, plan_id)           <plan dir>/stage-record.json
      preimage_path(out, stage, plan_id, name)         <plan dir>/preimage/<name>
      staged_path(out, stage, plan_id, name)           <plan dir>/staged/<name>
      failed_path(out, stage, plan_id, name)           <plan dir>/failed/<name>

**Step 11, slots, escaping and the file guards (T013, slice 2):**

* ``SLOT_TABLE`` (stage -> kind -> arguments), ``narrative_problem(text, stage)`` and ``FALLBACK_SENTENCES``, with
  ``narrative_fallback(field)``: step 11. A narrative field that breaks the slot grammar or the numeral ban takes
  its fixed sentence and is flagged ``input:<field>:narrative-fallback``; the part is never rejected for it.
  ``FLAG_FIELDS`` are the 28 names a flag's ``<field>`` can take (the first 24 are ``NARRATIVE_FIELDS``).
* ``resolve_narrative(text, stage, lookup, sink="cell")``: fills the slots from ``lookup(kind, argument)``, escapes
  the result, and returns ``None`` when the text or a slot doesn't resolve.
* ``ESCAPE_REFERENCES`` (the closed set that ``tachi_parsers`` decodes), ``escape_cell(text, keep_slots=False)``,
  ``escape_prose(text, keep_slots=False)`` and ``fence_for(snippet)``. SARIF strings go through ``json.dumps`` only.
* ``expected_file_problem(path, base, names=None)``: KB 24's guard for a path that a file names.
  ``evidence_path_problem(file, target)``: F16's check of an evidence ``file`` against the target directory.
* ``MAX_UNDECLARED_PATHS`` (1,000): the most ``undeclared_paths`` a stage record keeps.
"""
from __future__ import annotations

import copy
import dataclasses
import datetime
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

# Turn bytecode writing off before anything else loads (feature 391, FR-007; ADR-049 D8).
# This helper is already compiled when this line runs and imports no local module itself,
# so the line protects the local modules that an importer loads after it.
sys.dont_write_bytecode = True


# =============================================================================
# Identifier allow-lists (ADR-050 D3, "Identifiers"; S-2)
# =============================================================================

# S-2's prefix rank: the order of this tuple is the order of finding IDs.
FINDING_PREFIXES = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")

# The source text of each allow-list, exactly as contracts/part-files.md and
# contracts/threat-model-records.md spell it, so a drift test can compare the text.
ID_PATTERNS: Dict[str, str] = {
    "finding": "(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}",
    "plan": "[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}",
    "batch": "B[0-9]{3}(-[12]){0,2}",
    "dispatch": "dsp-[0-9]{3,4}",
    "group": "CG-[0-9]{1,6}",
    "chain": "CHAIN-[0-9]{3,6}",
    "language": "[a-z0-9+#-]{1,20}",
}

_COMPILED = {kind: re.compile(source, re.ASCII) for kind, source in ID_PATTERNS.items()}


def id_matches(kind: str, value: object) -> bool:
    """True when ``value`` is a ``str`` that fully matches the ``kind`` allow-list.

    An unknown ``kind`` raises ``KeyError``, so a typo fails loudly.
    """
    pattern = _COMPILED[kind]
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def canonical_finding_id(value: object) -> str:
    """The canonical spelling ``{PREFIX}-{N}``, leading zeros dropped: ``AGP-01`` -> ``AGP-1``.

    Raises ``ValueError`` when ``value`` is not an allow-listed finding ID.
    """
    if not id_matches("finding", value):
        raise ValueError("not a finding ID: %r" % (value,))
    prefix, _, number = value.partition("-")  # type: ignore[union-attr]
    return "%s-%d" % (prefix, int(number))


def finding_sort_key(value: object) -> Tuple[int, int]:
    """S-2's total order: prefix rank, then the numeric suffix as an integer (``T-9`` < ``T-10``).

    Two spellings of one canonical ID have one key. Raises ``ValueError`` on a non-ID.
    """
    prefix, _, number = canonical_finding_id(value).partition("-")
    return (FINDING_PREFIXES.index(prefix), int(number))


# =============================================================================
# D7's syntactic path rule (evidence ``file`` values and URI candidates)
# =============================================================================

PATH_MAX_BYTES = 4096


def path_problem(value: object, allow_absolute: bool = False) -> Optional[str]:
    """ADR-050 D7's syntactic checks on a path. ``None`` when it passes, else the check's name.

    The checks run in this order, and the first failure names the problem:
    ``type``, ``empty``, ``encoding``, ``too-long`` (over ``PATH_MAX_BYTES`` bytes of UTF-8),
    ``control-char`` (any Cc character), ``backslash``, ``backtick``, ``leading-slash``
    (unless ``allow_absolute``), ``drive-letter``, ``scheme``, ``parent-reference`` (a ``..``
    component) and ``empty`` again when no component is left after dropping ``.`` and empty ones.

    A relative path whose first component holds a colon is refused as a drive letter
    (``C:``) or a scheme (``https:``), as RFC 3986 section 4.2 requires of a relative reference.
    An absolute path (``allow_absolute``) skips the drive-letter and scheme checks, because its
    leading slash already settles how it parses. This function never touches the filesystem.
    """
    if not isinstance(value, str):
        return "type"
    if value == "":
        return "empty"
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        return "encoding"
    if size > PATH_MAX_BYTES:
        return "too-long"
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        return "control-char"
    if "\\" in value:
        return "backslash"
    if "`" in value:
        return "backtick"
    if value.startswith("/"):
        if not allow_absolute:
            return "leading-slash"
    else:
        first = value.split("/", 1)[0]
        if ":" in first:
            letter = len(first) >= 2 and first[1] == ":" and first[0].isascii() and first[0].isalpha()
            return "drive-letter" if letter else "scheme"
    parts = [part for part in value.split("/") if part not in ("", ".")]
    if ".." in parts:
        return "parent-reference"
    if not parts:
        return "empty"
    return None


def path_parts(value: object, allow_absolute: bool = False) -> Tuple[str, ...]:
    """The path's components with ``.`` and empty ones dropped (D7).

    Raises ``ValueError`` carrying ``path_problem``'s name when the path fails the rule.
    """
    problem = path_problem(value, allow_absolute=allow_absolute)
    if problem is not None:
        raise ValueError(problem)
    return tuple(part for part in value.split("/") if part not in ("", "."))  # type: ignore[union-attr]


# =============================================================================
# The closed key sets and values (contracts/part-files.md; part-file-contract-shared.md)
# =============================================================================

PART_SCHEMA = "tachi.part/1"
OVERFLOW_SCHEMA = "tachi.overflow/1"
BATCH_INPUT_SCHEMA = "tachi.batch-input/1"
PLAN_SCHEMA = "tachi.plan/1"
POINTER_SCHEMA = "tachi.plan-pointer/1"
STAGE_RECORD_SCHEMA = "tachi.stage-record/1"

# The stages this version knows, each with its agent. Later stages join this table when they ship.
STAGE_AGENTS: Dict[str, str] = {
    "risk-score": "tachi-risk-scorer",
    "compensating-controls": "tachi-control-analyzer",
}

SUBSCORE_NAMES = ("known_techniques", "attack_complexity", "tooling_availability", "skill_level",
                  "scriptability", "target_scope", "resource_requirements", "detection_difficulty")
METRIC_NAMES = ("AV", "AC", "PR", "UI", "S", "C", "I", "A")
ASSESSMENT_DIMENSIONS = ("coverage", "configuration", "currency", "completeness")
CONTROL_CATEGORIES = ("authentication", "input-validation", "rate-limiting", "encryption", "logging-audit",
                      "csrf-protection", "csp-security-headers", "access-control")
CONTROL_STATUSES = ("found", "partial", "missing")
CONFIDENCES = ("High", "Medium", "Low")
TRUST_LEVELS = ("Untrusted", "Semi-Trusted", "Trusted")
OVERFLOW_REASONS = ("output-budget", "input-too-large", "other")
BATCH_STATES = ("pending", "done", "failed", "split")
RECORD_STATUSES = ("success", "success-with-warnings", "failed")
OVERFLOW_EVENT_KINDS = ("missing", "overflow-reported", "unparseable", "invalid")

# The stage record's closed `counts` keys: the base counts, and one count per flag kind (ADR-050 D9).
COUNT_KEYS = frozenset((
    "units", "open", "resolved", "rendered", "parse_errors", "narrative_fallbacks", "truncations",
    "corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input"))

# name -> (required keys, optional keys), in the contracts' order. Every key is required unless listed optional.
KEY_SETS: Dict[str, Tuple[Tuple[str, ...], Tuple[str, ...]]] = {
    "part": (("schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "items", "fragments"), ()),
    "overflow": (("schema", "plan_id", "batch_id", "stage", "agent_type", "reason"), ()),
    "batch-input": (("schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "attempt", "part_path",
                     "tree_paths", "units", "refs", "params"), ()),
    "plan": (("schema", "plan_id", "stage", "agent_type", "created_utc", "tachi_version", "inputs", "params",
              "batch_size", "unit_count", "preimage", "out_snapshot", "retry_budget", "batches"), ()),
    "plan-pointer": (("schema", "plan_id"), ()),
    "stage-record": (("schema", "stage", "plan_id", "status", "tachi_version", "started_utc", "finished_utc",
                      "input_digest", "counts", "batches", "overflow_events", "retries", "warnings",
                      "undeclared_paths", "outputs", "error"), ()),
    "scorer-item": (("finding_id", "cvss_vector", "exploitability", "scalability", "reachability", "rationale"),
                    ("metric_rationale", "subscore_rationale")),
    "controls-item": (("finding_id", "control_status", "control_category", "confidence", "carried_forward",
                       "evidence", "matrix_row", "recommendation_body"), ()),
    "exploitability": (SUBSCORE_NAMES[:4], ()),
    "scalability": (SUBSCORE_NAMES[4:], ()),
    "reachability": (("zone", "trust_level", "auth_barriers", "network_boundaries"), ()),
    "rationale": (("cvss", "exploitability", "scalability", "reachability"), ()),
    "evidence-entry": (("file", "line", "language", "snippet", "summary"), ("assessment",)),
    "assessment": (ASSESSMENT_DIMENSIONS, ()),
    "assessment-dimension": (("rating", "rationale"), ()),
    "plan-input": (("path", "sha256", "bytes"), ()),
    "plan-batch": (("batch_id", "parent", "attempt", "finding_ids", "input_sha256", "state"), ()),
    "retry-budget": (("limit", "used"), ()),
    "stage-batches": (("planned", "dispatched", "done", "retried", "split", "exhausted"), ()),
    "overflow-event": (("batch_id", "attempt", "kind"), ()),
    "retry-entry": (("batch_id", "attempt", "cause", "children"), ()),
    "warning": (("code", "detail"), ()),
    "output": (("path", "sha256"), ()),
    "error": (("code", "message", "batch_id", "finding_ids", "remedy"), ()),
}

# The 24 flag fields: the `<field>` of `input:<field>:narrative-fallback` and `input:<field>:truncated`,
# dotted, with no list index (part-file-contract-shared.md, "Fixed Fallback Sentences").
NARRATIVE_FIELDS: Tuple[str, ...] = (
    tuple("rationale." + key for key in KEY_SETS["rationale"][0])
    + tuple("metric_rationale." + key for key in METRIC_NAMES)
    + tuple("subscore_rationale." + key for key in SUBSCORE_NAMES)
    + tuple("evidence.assessment." + key for key in ASSESSMENT_DIMENSIONS))

# Size caps (ADR-050 D3 step 2). The part cap and the agent-input cap are the ADR's; the four document
# caps are this module's own, sized to the largest legitimate file (a plan holds up to 20,000 snapshot entries).
MAX_PART_BYTES = 512 * 1024
MAX_AGENT_INPUT_BYTES = 16 * 1024 * 1024
MAX_DOCUMENT_BYTES: Dict[str, int] = {
    PLAN_SCHEMA: 8 * 1024 * 1024,
    BATCH_INPUT_SCHEMA: 4 * 1024 * 1024,
    POINTER_SCHEMA: 4096,
    STAGE_RECORD_SCHEMA: 1024 * 1024,
}
MAX_NESTING = 8
MAX_INT_DIGITS = 20
MAX_STRING_CHARS = 16384
MAX_SNAPSHOT_ENTRIES = 20000
MAX_IDS = 500
# A stage record keeps at most this many `undeclared_paths`, sorted. Past it the writer adds the warning
# `undeclared-paths-truncated`, whose detail carries the full count (ruled at W1, T023).
MAX_UNDECLARED_PATHS = 1000


# =============================================================================
# Step 1: the planned path, by identity (KB 24)
# =============================================================================

def under(base: object, path: object) -> bool:
    """True when ``path`` is ``base`` or lies inside it, decided by file identity, never by spelling.

    The walk goes up from ``path`` (past any tail that does not exist yet) and compares each ancestor
    with ``base`` by ``os.path.samefile``. A ``..`` component is never inside, and any OS error is False.
    A string prefix is not containment: ``out-evil`` is not under ``out``.
    """
    base, path = os.fspath(base), os.fspath(path)
    if ".." in path.split(os.sep):
        return False
    current = os.path.abspath(path)
    while True:
        try:
            if os.path.lexists(current) and os.path.samefile(current, base):
                return True
        except OSError:
            return False
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent


def _walk_problem(base: str, names: List[str]) -> Optional[str]:
    """Walk ``names`` down from ``base`` with ``lstat``, never following a link.

    ``None`` when every component exists, none is a symlink and the last is a regular file. Otherwise
    ``missing``, ``symlink`` or ``not-regular``. ``base`` itself may be a link; only what is below it may not.
    """
    walk, mode = base, 0
    for name in names:
        walk = os.path.join(walk, name)
        try:
            mode = os.lstat(walk).st_mode
        except OSError:
            return "missing"
        if stat.S_ISLNK(mode):
            return "symlink"
    return None if names and stat.S_ISREG(mode) else "not-regular"


def path_guard_problem(path: object, out: object) -> Optional[str]:
    """ADR-050 D3 step 1: ``None`` when ``path`` is a regular file under ``out`` with no symlink below it.

    Otherwise the first problem: ``outside`` (not under ``out`` by identity), ``missing``, ``symlink``
    (the file or any directory between ``out`` and it) or ``not-regular``. ``out`` itself may be a symlink.
    """
    path, out = os.fspath(path), os.fspath(out)
    if not under(out, path):
        return "outside"
    names, current = [], os.path.abspath(path)
    try:
        while not (os.path.lexists(current) and os.path.samefile(current, out)):
            names.append(os.path.basename(current))
            parent = os.path.dirname(current)
            if parent == current:
                return "outside"
            current = parent
    except OSError:
        return "outside"
    return _walk_problem(out, list(reversed(names)))


def expected_file_problem(path: object, base: object, names: Any = None) -> Optional[str]:
    """KB 24 and NFR-10, for a path that a file names (``baseline.source``, ``source_file``, the architecture path).

    ``None`` when ``path`` passes D7's syntactic rule (absolute allowed, so no control byte, backslash, backtick or
    ``..``), is a regular file under ``base`` by identity with no symlink below it (a relative path means the
    working directory), and, when ``names`` is given, has one of those base names. Otherwise the first problem:
    ``path_problem``'s names, then ``outside``, ``missing``, ``symlink``, ``not-regular`` or ``unexpected-name``.
    """
    text = os.fspath(path)
    problem = path_problem(text, allow_absolute=True)
    if problem is None:
        problem = path_guard_problem(text, base)
    if problem is None and names is not None and os.path.basename(text) not in names:
        problem = "unexpected-name"
    return problem


def evidence_path_problem(file: object, target: object) -> Optional[str]:
    """F16: an evidence ``file`` value against the target directory, by the resolver's checks (ADR-050 D7).

    D7's relative-path rule first (``path_problem``: no scheme, leading ``/``, backslash, drive letter or ``..``),
    then a walk down from ``target`` without following a link: every component exists, none is a symlink, and the
    last is a regular file. ``None`` when it passes, else the problem's name (``missing``, ``symlink``,
    ``not-regular`` or one of ``path_problem``'s). The part validator applies only the first step, because the
    target's files are not its input; the controls renderer applies both.
    """
    problem = path_problem(file)
    if problem is not None:
        return problem
    return _walk_problem(os.path.abspath(os.fspath(target)), list(path_parts(file)))


# =============================================================================
# Steps 2 to 4: the strict loader
# =============================================================================

class PartError(Exception):
    """A file or object failed validation. ``kind`` is ``missing``, ``unparseable`` or ``invalid``.

    ``detail`` is a short message that never echoes the file's content.
    """

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__(detail)
        self.kind = kind
        self.detail = detail


def _fail(detail: str, kind: str = "invalid") -> None:
    raise PartError(kind, detail)


def _no_duplicates(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _refuse_constant(name: str) -> None:
    raise ValueError("%s is not allowed" % name)


def _bounded_int(text: str) -> int:
    if len(text.lstrip("-")) > MAX_INT_DIGITS:
        raise ValueError("integer literal of more than %d digits" % MAX_INT_DIGITS)
    return int(text)


def _scan(obj: Any) -> Tuple[int, bool]:
    """The deepest nesting level, and whether any string or key holds a surrogate. Iterative, so it cannot recurse."""
    stack, deepest, surrogate = [(obj, 1)], 1, False
    while stack:
        current, level = stack.pop()
        deepest = max(deepest, level)
        strings = []
        if isinstance(current, dict):
            strings = list(current)
            stack.extend((value, level + 1) for value in current.values())
        elif isinstance(current, list):
            stack.extend((value, level + 1) for value in current)
        elif isinstance(current, str):
            strings = [current]
        for text in strings:
            try:
                text.encode("utf-8")
            except UnicodeEncodeError:
                surrogate = True
    return deepest, surrogate


def _read_regular_file(path: object, max_bytes: int) -> bytes:
    flags = os.O_RDONLY
    for name in ("O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):
        flags |= getattr(os, name, 0)
    try:
        fd = os.open(os.fspath(path), flags)
    except FileNotFoundError:
        raise PartError("missing", "no file at the planned path")
    except OSError:
        raise PartError("invalid", "the file cannot be opened without following a link")
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise PartError("invalid", "the planned path is not a regular file")
        chunks, total = [], 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                raise PartError("unparseable", "the file is over the size cap of %d bytes" % max_bytes)
    except OSError:
        raise PartError("invalid", "the file could not be read")
    finally:
        os.close(fd)


def load_json(path: object, out: object, max_bytes: int = MAX_PART_BYTES) -> Dict[str, Any]:
    """ADR-050 D3 steps 1 to 4: the planned path, the size cap, strict UTF-8 and strict JSON.

    Step 1 failures are ``invalid`` (``missing`` when the file is absent); steps 2 to 4 are ``unparseable``.
    The four ``json.loads`` hooks reject duplicate keys, ``NaN`` and ``Infinity``, and an integer literal of
    more than 20 digits; floats arrive as ``Decimal``, so ``1e999`` never becomes ``inf``. Nesting is at
    most 8 levels, the top level is an object, and no string holds a surrogate.
    """
    problem = path_guard_problem(path, out)
    if problem == "missing":
        _fail("no file at the planned path", "missing")
    if problem is not None:
        _fail("the planned path failed the path guard (%s)" % problem)
    raw = _read_regular_file(path, max_bytes)
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("the file starts with a byte order mark", "unparseable")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _fail("the file is not strict UTF-8", "unparseable")
    try:
        obj = json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_refuse_constant,
                         parse_float=Decimal, parse_int=_bounded_int)
    except (ValueError, RecursionError) as exc:
        _fail("the file is not strict JSON (%s)" % str(exc)[:80].replace("\n", " "), "unparseable")
    if not isinstance(obj, dict):
        _fail("the top level is not an object", "unparseable")
    depth, surrogate = _scan(obj)
    if depth > MAX_NESTING:
        _fail("the file nests deeper than %d levels" % MAX_NESTING, "unparseable")
    if surrogate:
        _fail("a string holds a surrogate code point", "unparseable")
    return obj


# =============================================================================
# Step 11 and the output rules (T013, slice 2): slots, the numeral ban, the fixed sentences, escaping
# =============================================================================

# The 28 names of a flag's `<field>`: the 24 narrative fields, which serve `input:<field>:narrative-fallback`,
# and four evidence-class prose fields. All 28 serve `input:<field>:truncated` (contracts/part-files.md).
FLAG_FIELDS: Tuple[str, ...] = NARRATIVE_FIELDS + ("evidence.snippet", "evidence.summary", "matrix_row", "recommendation_body")

# Slots (ADR-050 D3's table; part-file-contract-shared.md, "Slots in use"): stage -> kind -> the arguments that
# stage accepts. `None` marks an argument checked another way: a finding ID by its allow-list, and a taxonomy
# ID by the slot's argument pattern and then the caller's lookup.
SLOT_TABLE: Dict[str, Dict[str, Optional[frozenset]]] = {
    "risk-score": {
        "score": frozenset(("cvss_base", "exploitability", "scalability", "reachability", "composite") + SUBSCORE_NAMES),
        "count": frozenset(("auth_barriers", "network_boundaries")),
        "band": frozenset(("severity",)),
        "date": frozenset(("scored", "review")),
        "finding": None,
        "ref": None,
        "name": frozenset(("component", "zone")),
    },
    "compensating-controls": {
        "score": frozenset(("inherent", "residual")),
        "count": frozenset(("evidence",)),
        "band": frozenset(("inherent", "residual")),
        "pct": frozenset(("reduction",)),
        "finding": None,
        "ref": None,
        "name": frozenset(("component",)),
    },
}

# A slot is recognized only as `{{`, a kind, then `:`. Every kind that any stage will ever have is listed, so a
# kind that this stage doesn't accept (a slot reserved for a later stage) fails the grammar instead of passing as text.
_SLOT_OPEN = re.compile(r"\{\{(score|count|band|pct|date|finding|ref|name):")
_SLOT_ARG = re.compile(r"[A-Za-z0-9_.:-]{1,64}", re.ASCII)

FALLBACK_SENTENCES: Dict[str, str] = {
    "rationale.cvss":
        "No CVSS rationale is shown because the text the agent wrote broke the narrative rules.",
    "rationale.exploitability":
        "No exploitability rationale is shown because the text the agent wrote broke the narrative rules.",
    "rationale.scalability":
        "No scalability rationale is shown because the text the agent wrote broke the narrative rules.",
    "rationale.reachability":
        "No reachability rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.AV":
        "No attack vector metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.AC":
        "No attack complexity metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.PR":
        "No privileges required metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.UI":
        "No user interaction metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.S":
        "No scope metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.C":
        "No confidentiality impact metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.I":
        "No integrity impact metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "metric_rationale.A":
        "No availability impact metric rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.known_techniques":
        "No known techniques sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.attack_complexity":
        "No attack complexity sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.tooling_availability":
        "No tooling availability sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.skill_level":
        "No skill level sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.scriptability":
        "No scriptability sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.target_scope":
        "No target scope sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.resource_requirements":
        "No resource requirements sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "subscore_rationale.detection_difficulty":
        "No detection difficulty sub-score rationale is shown because the text the agent wrote broke the narrative rules.",
    "evidence.assessment.coverage":
        "No coverage assessment rationale is shown because the text the agent wrote broke the narrative rules.",
    "evidence.assessment.configuration":
        "No configuration assessment rationale is shown because the text the agent wrote broke the narrative rules.",
    "evidence.assessment.currency":
        "No currency assessment rationale is shown because the text the agent wrote broke the narrative rules.",
    "evidence.assessment.completeness":
        "No completeness assessment rationale is shown because the text the agent wrote broke the narrative rules.",
}

ESCAPE_REFERENCES: Dict[str, str] = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">", "&#124;": "|", "&#96;": "`", "&#123;": "{", "&#10;": "\n", "&#35;": "#"}
_REFERENCE_OF = {char: reference for reference, char in ESCAPE_REFERENCES.items()}
_CELL_TRANSLATION = {ord(char): _REFERENCE_OF[char] for char in "&<>|`\n"}
_PROSE_TRANSLATION = {ord(char): _REFERENCE_OF[char] for char in "&<>|`"}
_BRACE_OF_A_PAIR = re.compile(r"\{(?=\{)|(?<=\{)\{")
_HEADING_START = re.compile(r"(?m)^([ \t]*)#")


def _tokens(text: str, stage: str) -> List[Tuple[str, ...]]:
    """Split a narrative into ``("text", plain)`` and ``("slot", kind, argument)`` tokens.

    Raises ``ValueError`` naming the first problem: ``slot-syntax`` (an unterminated slot, or an argument outside
    its pattern), ``slot-kind`` (a kind this stage doesn't have), ``slot-argument`` (an argument this stage's table
    doesn't give that kind, or a finding slot that isn't an allow-listed ID) or ``numeral``.
    """
    table = SLOT_TABLE[stage]
    tokens: List[Tuple[str, ...]] = []
    position = 0
    while True:
        opener = _SLOT_OPEN.search(text, position)
        if opener is None:
            break
        argument = _SLOT_ARG.match(text, opener.end())
        if argument is None or text[argument.end():argument.end() + 2] != "}}":
            raise ValueError("slot-syntax")
        kind, name = opener.group(1), argument.group(0)
        if kind not in table:
            raise ValueError("slot-kind")
        allowed = table[kind]
        if (allowed is not None and name not in allowed) or (kind == "finding" and not id_matches("finding", name)):
            raise ValueError("slot-argument")
        if opener.start() > position:
            tokens.append(("text", text[position:opener.start()]))
        tokens.append(("slot", kind, name))
        position = argument.end() + 2
    if position < len(text):
        tokens.append(("text", text[position:]))
    for token in tokens:
        if token[0] == "text" and any(char.isnumeric() for char in token[1]):
            raise ValueError("numeral")
    return tokens


def narrative_problem(text: str, stage: str) -> Optional[str]:
    """Step 11's check: ``None`` when ``text`` follows the stage's slot grammar and holds no numeral outside a slot.

    Otherwise the first problem's name (see ``_tokens``). "No numeral" means no character for which
    ``str.isnumeric()`` is true, so every Unicode numeral is out as well as ``0`` to ``9``. A number word such as
    "two-factor" passes. Raises ``KeyError`` for a stage with no slot table.
    """
    if not isinstance(text, str):
        return "type"
    try:
        _tokens(text, stage)
    except ValueError as exc:
        return str(exc)
    return None


def narrative_fallback(field: str) -> str:
    """The fixed sentence for one of the 24 narrative fields (``FALLBACK_SENTENCES``). ``KeyError`` for any other name."""
    if not isinstance(field, str) or field not in FALLBACK_SENTENCES:
        raise KeyError(field)
    return FALLBACK_SENTENCES[field]


def _escape_text(text: str, cell: bool) -> str:
    translated = text.translate(_CELL_TRANSLATION if cell else _PROSE_TRANSLATION)
    return _BRACE_OF_A_PAIR.sub(_REFERENCE_OF["{"], translated)


def _split_slots(text: str) -> List[Tuple[bool, str]]:
    """Cut ``text`` into ``(is_slot, piece)`` at each complete slot (a recognized opener, an argument and ``}}``)."""
    pieces: List[Tuple[bool, str]] = []
    plain_from = position = 0
    while True:
        opener = _SLOT_OPEN.search(text, position)
        if opener is None:
            break
        argument = _SLOT_ARG.match(text, opener.end())
        if argument is None or text[argument.end():argument.end() + 2] != "}}":
            position = opener.start() + 1
            continue
        if opener.start() > plain_from:
            pieces.append((False, text[plain_from:opener.start()]))
        plain_from = position = argument.end() + 2
        pieces.append((True, text[opener.start():plain_from]))
    if plain_from < len(text):
        pieces.append((False, text[plain_from:]))
    return pieces


def _escape(text: str, keep_slots: bool, cell: bool) -> str:
    if not keep_slots:
        return _escape_text(text, cell)
    return "".join(piece if is_slot else _escape_text(piece, cell) for is_slot, piece in _split_slots(text))


def _guard_headings(text: str) -> str:
    return _HEADING_START.sub(lambda match: match.group(1) + _REFERENCE_OF["#"], text)


def escape_cell(text: str, keep_slots: bool = False) -> str:
    """Escape untrusted text for a markdown table cell (ADR-050 D3, "Output"), with the closed ``ESCAPE_REFERENCES``.

    ``&``, ``<``, ``>``, ``|`` and a backtick become references, each ``{`` of a ``{{`` becomes ``&#123;`` and a
    newline becomes ``&#10;``. With ``keep_slots`` a complete slot stays as it is, for the narrative text that a
    renderer persists with its slots (carried text, RR1). The one decoder in ``tachi_parsers`` reverses exactly these.
    """
    return _escape(text, keep_slots, True)


def escape_prose(text: str, keep_slots: bool = False) -> str:
    """Escape untrusted text for prose: the cell rules, but line breaks stay and no line starts with ``#`` or ``|``.

    A line that would start with ``#`` (after any spaces or tabs) starts with ``&#35;`` instead, and a ``|`` is
    always ``&#124;``, so agent text can neither forge a heading nor a table row.
    """
    return _guard_headings(_escape(text, keep_slots, False))


def fence_for(snippet: str) -> str:
    """A code fence of backticks, at least three and longer than the longest backtick run in ``snippet``."""
    return "`" * max(3, max((len(run) for run in re.findall(r"`+", snippet)), default=0) + 1)


def resolve_narrative(text: str, stage: str, lookup: Any, sink: str = "cell") -> Optional[str]:
    """Fill a narrative's slots from ``lookup(kind, argument)`` and escape the result for ``sink``.

    ``sink`` is ``cell`` (a table cell, the default) or ``prose``. Returns ``None``, and the caller writes the
    field's fixed sentence, when the text breaks the grammar or the numeral ban or when a slot doesn't resolve
    (the lookup returned ``None``). A finding slot is canonicalized before it is looked up. A lookup that returns
    anything but text or ``None`` is a bug and raises ``TypeError``. Every resolved value is untrusted text: it is
    escaped, and never read for slots again.
    """
    if sink not in ("cell", "prose"):
        raise ValueError("sink is cell or prose")
    if not isinstance(text, str):
        return None
    try:
        tokens = _tokens(text, stage)
    except ValueError:
        return None
    cell = sink == "cell"
    pieces = []
    for token in tokens:
        if token[0] == "text":
            pieces.append(_escape_text(token[1], cell))
            continue
        kind, name = token[1], token[2]
        value = lookup(kind, canonical_finding_id(name) if kind == "finding" else name)
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("a slot lookup returns text or None")
        pieces.append(_escape_text(value, cell))
    result = "".join(pieces)
    return result if cell else _guard_headings(result)


# =============================================================================
# Steps 5 to 10: classifying a part
# =============================================================================

@dataclasses.dataclass
class PartResult:
    """What a part file turned out to be.

    ``state`` is ``done``, ``missing``, ``overflow``, ``unparseable`` or ``invalid``. ``detail`` is a short
    message (the ``reason`` for ``overflow``). ``part`` is the validated part, only when ``done``: IDs in
    canonical form, items in the planned order, prose cut at its limits. ``flags`` maps each canonical
    finding ID to its sorted ``input:<field>:<cause>`` flags, and ``counts`` totals the cuts and the fallbacks.
    """

    state: str
    detail: str = ""
    part: Optional[Dict[str, Any]] = None
    flags: Dict[str, List[str]] = dataclasses.field(default_factory=dict)
    counts: Dict[str, int] = dataclasses.field(default_factory=lambda: {"narrative_fallbacks": 0, "truncations": 0})


class _ItemState(object):
    """The flags and counts that validating one item collects."""

    def __init__(self, stage: str) -> None:
        self.stage = stage
        self.flags: set = set()
        self.fallbacks = 0
        self.truncations = 0


_CVSS_VECTOR = re.compile(r"CVSS:3\.1/AV:[NALP]/AC:[LH]/PR:[NLH]/UI:[NR]/S:[UC]/C:[NLH]/I:[NLH]/A:[NLH]", re.ASCII)
# Cc other than tab and newline, then U+2028, U+2029, U+200E, U+200F, U+061C, U+202A-U+202E and U+2066-U+2069 (step 10).
_FORBIDDEN_CHARACTERS = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f  ‎‏؜‪-‮⁦-⁩]")


def _check_keys(obj: Any, name: str) -> None:
    """Step 6: ``obj`` is an object whose keys are the closed set ``name``: every required key, and no other."""
    required, optional = KEY_SETS[name]
    if not isinstance(obj, dict):
        _fail("%s is not an object" % name)
    keys = set(obj)
    if not set(required) <= keys or not keys <= set(required) | set(optional):
        _fail("%s does not have exactly the contract's keys" % name)


def _int(value: Any, low: int, high: Optional[int], what: str) -> int:
    if type(value) is not int or value < low or (high is not None and value > high):
        _fail("%s is not an integer in range" % what)
    return value


def _check_characters(text: str, what: str) -> None:
    """Step 10: at most 16,384 characters, and none of the forbidden control, bidi or separator characters."""
    if len(text) > MAX_STRING_CHARS or _FORBIDDEN_CHARACTERS.search(text):
        _fail("%s is over %d characters or holds a character the contract forbids" % (what, MAX_STRING_CHARS))


def _closed(value: Any, what: str, low: int = 1, high: Optional[int] = None) -> str:
    """A closed-value string: a range here, then the pattern or enum its field has. Over its range, it rejects."""
    if not isinstance(value, str) or len(value) < low or (high is not None and len(value) > high):
        _fail("%s is not text in range" % what)
    _check_characters(value, what)
    return value


def _enum(value: Any, allowed: Tuple[str, ...], what: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        _fail("%s is not one of the allowed values" % what)
    return value


def _narrative(text: str, field: str, state: _ItemState) -> str:
    """Step 11: a narrative field that breaks the slot grammar or the numeral ban takes its fixed sentence.

    The field is flagged ``input:<field>:narrative-fallback`` and counted, and the part is never rejected for it.
    A field that passes is kept with its slots as written.
    """
    if narrative_problem(text, state.stage) is None:
        return text
    state.flags.add("input:%s:narrative-fallback" % field)
    state.fallbacks += 1
    return FALLBACK_SENTENCES[field]


def _prose(value: Any, limit: int, field: str, state: _ItemState, narrative: bool = False,
           minimum: int = 0, lines: Optional[int] = None) -> str:
    """A prose field: cut at its limit (and at ``lines`` lines) and flagged, never rejected for length (RR2).

    The cut comes first, then step 10 on what is left, then step 11 for a narrative field.
    """
    if not isinstance(value, str):
        _fail("%s is not text" % field)
    cut = False
    if lines is not None and len(value.split("\n")) > lines:
        value, cut = "\n".join(value.split("\n")[:lines]), True
    if len(value) > limit:
        value, cut = value[:limit], True
    if cut:
        state.flags.add("input:%s:truncated" % field)
        state.truncations += 1
    if len(value) < minimum:
        _fail("%s is empty" % field)
    _check_characters(value, field)
    return _narrative(value, field, state) if narrative else value


def _scorer_item(item: Dict[str, Any], state: _ItemState) -> None:
    _check_keys(item, "scorer-item")
    vector = item["cvss_vector"]
    if not isinstance(vector, str) or _CVSS_VECTOR.fullmatch(vector) is None:
        _fail("cvss_vector does not match the CVSS 3.1 pattern")
    for group in ("exploitability", "scalability"):
        _check_keys(item[group], group)
        for name in KEY_SETS[group][0]:
            _int(item[group][name], 0, 10, "%s.%s" % (group, name))
    reach = item["reachability"]
    _check_keys(reach, "reachability")
    if (reach["zone"] is None) != (reach["trust_level"] is None):
        _fail("reachability.zone and trust_level must be null together")
    if reach["zone"] is not None:
        _closed(reach["zone"], "reachability.zone", 1, 120)
        _enum(reach["trust_level"], TRUST_LEVELS, "reachability.trust_level")
    _int(reach["auth_barriers"], 0, 10, "reachability.auth_barriers")
    _int(reach["network_boundaries"], 0, 10, "reachability.network_boundaries")
    _check_keys(item["rationale"], "rationale")
    for key in KEY_SETS["rationale"][0]:
        item["rationale"][key] = _prose(item["rationale"][key], 400, "rationale." + key, state, narrative=True, minimum=1)
    for group, names in (("metric_rationale", METRIC_NAMES), ("subscore_rationale", SUBSCORE_NAMES)):
        if group in item:
            block = item[group]
            if not isinstance(block, dict) or not set(block) <= set(names):
                _fail("%s has a key outside the contract's names" % group)
            for key in names:
                if key in block:
                    block[key] = _prose(block[key], 160, "%s.%s" % (group, key), state, narrative=True)


def _evidence_entry(entry: Dict[str, Any], state: _ItemState) -> None:
    _check_keys(entry, "evidence-entry")
    if path_problem(_closed(entry["file"], "evidence.file", 1, 300)) is not None:
        _fail("evidence.file breaks D7's relative path rule")
    _int(entry["line"], 1, None, "evidence.line")
    if not id_matches("language", entry["language"]):
        _fail("evidence.language does not match the language pattern")
    entry["snippet"] = _prose(entry["snippet"], 600, "evidence.snippet", state, lines=5)
    entry["summary"] = _prose(entry["summary"], 160, "evidence.summary", state)
    if "assessment" in entry:
        _check_keys(entry["assessment"], "assessment")
        for dimension in ASSESSMENT_DIMENSIONS:
            cell = entry["assessment"][dimension]
            _check_keys(cell, "assessment-dimension")
            _enum(cell["rating"], CONFIDENCES, "evidence.assessment.%s.rating" % dimension)
            cell["rationale"] = _prose(cell["rationale"], 160, "evidence.assessment." + dimension, state, narrative=True)


def _controls_item(item: Dict[str, Any], state: _ItemState) -> None:
    _check_keys(item, "controls-item")
    status = _enum(item["control_status"], CONTROL_STATUSES, "control_status")
    _enum(item["control_category"], CONTROL_CATEGORIES, "control_category")
    if (item["confidence"] is None) != (status == "missing"):
        _fail("confidence is null exactly when the status is missing")
    if item["confidence"] is not None:
        _enum(item["confidence"], CONFIDENCES, "confidence")
    if type(item["carried_forward"]) is not bool:
        _fail("carried_forward is not a boolean")
    evidence = item["evidence"]
    if not isinstance(evidence, list) or len(evidence) > 5 or (len(evidence) == 0) != (status == "missing"):
        _fail("evidence has 1 to 5 entries for found or partial, and none for missing")
    for entry in evidence:
        _evidence_entry(entry, state)
    item["matrix_row"] = _prose(item["matrix_row"], 1200, "matrix_row", state)
    if (item["recommendation_body"] is None) != (status == "found"):
        _fail("recommendation_body is null exactly when the status is found")
    if item["recommendation_body"] is not None:
        item["recommendation_body"] = _prose(item["recommendation_body"], 2000, "recommendation_body", state)


# Stage -> its payload validator. PR 2's stages join this table with their payloads.
_PAYLOADS = {"risk-score": _scorer_item, "compensating-controls": _controls_item}


def _planned_ids(plan_id: Any, batch_id: Any, stage: Any, agent_type: Any, finding_ids: Any) -> List[str]:
    """The planned batch, checked: a caller that passes a malformed plan gets ``invalid``, never a crash."""
    if not (id_matches("plan", plan_id) and id_matches("batch", batch_id)):
        _fail("the planned batch has a malformed ID")
    if not isinstance(stage, str) or STAGE_AGENTS.get(stage) != agent_type:
        _fail("the planned stage and agent do not pair up")
    if not isinstance(finding_ids, (list, tuple)) or not all(id_matches("finding", v) for v in finding_ids):
        _fail("a planned finding ID is malformed")
    canonical = [canonical_finding_id(v) for v in finding_ids]
    if not 1 <= len(canonical) <= MAX_IDS or len(set(canonical)) != len(canonical):
        _fail("the planned finding IDs are empty, too many or duplicated")
    return canonical


def _classify(obj: Any, plan_id: Any, batch_id: Any, stage: Any, agent_type: Any, finding_ids: Any) -> PartResult:
    planned = _planned_ids(plan_id, batch_id, stage, agent_type, finding_ids)
    if not isinstance(obj, dict):
        _fail("the part is not an object")
    # Step 5: `schema` selects the key set first, so a well-formed overflow object is never `invalid`.
    if obj.get("schema") == OVERFLOW_SCHEMA:
        _check_keys(obj, "overflow")
        if (obj["plan_id"], obj["batch_id"], obj["stage"], obj["agent_type"]) != (plan_id, batch_id, stage, agent_type):
            _fail("the overflow object is for another plan, batch, stage or agent")
        return PartResult("overflow", _enum(obj["reason"], OVERFLOW_REASONS, "reason"))
    if obj.get("schema") != PART_SCHEMA:
        _fail("schema is not %s" % PART_SCHEMA)
    _check_keys(obj, "part")
    # Step 7: the plan match.
    if (obj["plan_id"], obj["batch_id"], obj["stage"], obj["agent_type"]) != (plan_id, batch_id, stage, agent_type):
        _fail("plan_id, batch_id, stage or agent_type differs from the planned batch")
    # Step 8: every ID passes the allow-list before any other use.
    ids = obj["finding_ids"]
    if not isinstance(ids, list) or not 1 <= len(ids) <= MAX_IDS or not all(id_matches("finding", v) for v in ids):
        _fail("finding_ids is not 1 to %d allow-listed IDs" % MAX_IDS)
    canonical = [canonical_finding_id(v) for v in ids]
    if len(set(canonical)) != len(canonical) or set(canonical) != set(planned):
        _fail("finding_ids differ from the planned set")
    items = obj["items"]
    if not isinstance(items, list) or len(items) != len(planned) or not all(isinstance(i, dict) for i in items):
        _fail("items is not one object per finding ID")
    if not all(id_matches("finding", i.get("finding_id")) for i in items):
        _fail("an item's finding_id is not an allow-listed ID")
    by_id: Dict[str, Dict[str, Any]] = {}
    for item in items:
        key = canonical_finding_id(item["finding_id"])
        if key in by_id:
            _fail("two items for one finding ID")
        by_id[key] = item
    if set(by_id) != set(planned):
        _fail("the items differ from the planned set")
    if obj["fragments"] != []:
        _fail("fragments must be empty for this stage")
    # Steps 9 and 10: the payload, field by field, on a copy, in the planned order.
    flags: Dict[str, List[str]] = {}
    cuts = fallbacks = 0
    checked = []
    for key in planned:
        item = copy.deepcopy(by_id[key])
        item["finding_id"] = key
        state = _ItemState(stage)
        _PAYLOADS[stage](item, state)
        if state.flags:
            flags[key] = sorted(state.flags)
        cuts += state.truncations
        fallbacks += state.fallbacks
        checked.append(item)
    part = dict(obj, finding_ids=list(planned), items=checked, fragments=[])
    return PartResult("done", "", part, flags, {"narrative_fallbacks": fallbacks, "truncations": cuts})


def classify_part(obj: Any, plan_id: str, batch_id: str, stage: str, agent_type: str, finding_ids: Any) -> PartResult:
    """Steps 5 to 10 on a parsed object, against the planned batch. Never raises; see ``PartResult``."""
    try:
        return _classify(obj, plan_id, batch_id, stage, agent_type, finding_ids)
    except PartError as exc:
        return PartResult(exc.kind, exc.detail)


def read_part(path: object, out: object, plan_id: str, batch_id: str, stage: str, agent_type: str,
              finding_ids: Any) -> PartResult:
    """Steps 1 to 10 on the part file at ``path``: ``load_json``, then ``classify_part``. Never raises."""
    try:
        obj = load_json(path, out)
    except PartError as exc:
        return PartResult(exc.kind, exc.detail)
    return classify_part(obj, plan_id, batch_id, stage, agent_type, finding_ids)


# =============================================================================
# The batch-plan documents: plan, pointer, batch input, stage record (contracts/part-files.md sections 3 to 5)
# =============================================================================

# D4's closed output sets: the canonical file names a stage's plan may record a pre-image for.
# Keep this table in step with STAGE_AGENTS: a stage that ships adds its row to both.
CANONICAL_OUTPUTS: Dict[str, Tuple[str, ...]] = {
    "risk-score": ("risk-scores.md", "risk-scores.sarif"),
    "compensating-controls": ("compensating-controls.md", "compensating-controls.sarif"),
}

_UTC = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z", re.ASCII)
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.ASCII)
_VERSION_TRIPLE = re.compile(r"[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}", re.ASCII)
_HEX64 = re.compile(r"[0-9a-f]{64}", re.ASCII)
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}", re.ASCII)
_NAME = re.compile(r"[a-z][a-z0-9_]{0,39}", re.ASCII)
_CODE = re.compile(r"[a-z0-9:_.-]{1,64}", re.ASCII)


def _stamp(value: Any, pattern: Any, what: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        _fail("%s is not in its contract form" % what)
    return value


def _utc(value: Any, what: str) -> str:
    """ISO 8601 UTC ending in ``Z``, and a real calendar time."""
    _stamp(value, _UTC, what)
    try:
        datetime.datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]),
                          int(value[11:13]), int(value[14:16]), int(value[17:19]))
    except ValueError:
        _fail("%s is not a real calendar time" % what)
    return value


def _calendar_date(value: Any, what: str) -> str:
    _stamp(value, _DATE, what)
    try:
        datetime.date(int(value[0:4]), int(value[5:7]), int(value[8:10]))
    except ValueError:
        _fail("%s is not a real calendar date" % what)
    return value


def _id(kind: str, value: Any, what: str) -> str:
    if not id_matches(kind, value):
        _fail("%s is not an allow-listed %s ID" % (what, kind))
    return value


def _id_list(value: Any, what: str, minimum: int = 1) -> List[str]:
    """A list of allow-listed finding IDs with no two spellings of one canonical ID."""
    if not isinstance(value, list) or not minimum <= len(value) <= MAX_IDS or not all(id_matches("finding", v) for v in value):
        _fail("%s is not %d to %d allow-listed finding IDs" % (what, minimum, MAX_IDS))
    if len({canonical_finding_id(v) for v in value}) != len(value):
        _fail("%s names one finding twice" % what)
    return value


def _path_text(value: Any, what: str, absolute: bool = False) -> str:
    """A path that passes D7's syntactic rule (absolute allowed only where the caller says so)."""
    problem = path_problem(value, allow_absolute=absolute)
    if problem is not None or (absolute and not value.startswith("/")):
        _fail("%s is not an acceptable %s path (%s)" % (what, "absolute" if absolute else "relative", problem or "relative"))
    return value


def _params(value: Any) -> None:
    """The closed parameters of a stage: a small object of scalars, and ``scoring_date`` as a real ``YYYY-MM-DD``."""
    if not isinstance(value, dict) or len(value) > 20:
        _fail("params is not a small object")
    for key, item in value.items():
        _stamp(key, _NAME, "a params key")
        if key == "scoring_date":
            _calendar_date(item, "params.scoring_date")
        elif isinstance(item, str):
            _closed(item, "params." + key, 0, 1024)
        elif item is not None and type(item) not in (bool, int):
            _fail("params.%s is not a scalar" % key)


def _stage_pair(stage: Any, agent_type: Any) -> None:
    if not isinstance(stage, str) or STAGE_AGENTS.get(stage) != agent_type:
        _fail("stage is unknown, or agent_type is not the stage's agent")


def validate_plan(obj: Any) -> Dict[str, Any]:
    """``tachi.plan/1`` (contracts/part-files.md section 4). Returns ``obj``, or raises ``PartError("invalid")``."""
    _check_keys(obj, "plan")
    if obj["schema"] != PLAN_SCHEMA:
        _fail("schema is not %s" % PLAN_SCHEMA)
    _id("plan", obj["plan_id"], "plan_id")
    _stage_pair(obj["stage"], obj["agent_type"])
    _utc(obj["created_utc"], "created_utc")
    _stamp(obj["tachi_version"], _VERSION_TRIPLE, "tachi_version")
    if not isinstance(obj["inputs"], dict) or len(obj["inputs"]) > 20:
        _fail("inputs is not a small object")
    for name, entry in obj["inputs"].items():
        _stamp(name, _NAME, "an inputs name")
        _check_keys(entry, "plan-input")
        if path_problem(entry["path"], allow_absolute=True) is not None:
            _fail("inputs.%s.path is not an acceptable path" % name)
        _stamp(entry["sha256"], _HEX64, "inputs.%s.sha256" % name)
        _int(entry["bytes"], 0, None, "inputs.%s.bytes" % name)
    _params(obj["params"])
    if obj["batch_size"] is not None:
        _int(obj["batch_size"], 1, MAX_IDS, "batch_size")
    _int(obj["unit_count"], 0, 1000000, "unit_count")
    if not isinstance(obj["preimage"], dict) or set(obj["preimage"]) != set(CANONICAL_OUTPUTS[obj["stage"]]):
        _fail("preimage does not name exactly the stage's canonical outputs")
    for name, digest in obj["preimage"].items():
        if digest is not None:
            _stamp(digest, _HEX64, "preimage.%s" % name)
    snapshot = obj["out_snapshot"]
    if snapshot is not None:
        if not isinstance(snapshot, dict) or len(snapshot) > MAX_SNAPSHOT_ENTRIES:
            _fail("out_snapshot is not an object of at most %d entries" % MAX_SNAPSHOT_ENTRIES)
        for relpath, entry in snapshot.items():
            _path_text(relpath, "an out_snapshot path")
            if not isinstance(entry, list) or len(entry) != 2:
                _fail("an out_snapshot entry is not [size, mtime_ns]")
            _int(entry[0], 0, None, "out_snapshot size")
            _int(entry[1], 0, None, "out_snapshot mtime_ns")
    _check_keys(obj["retry_budget"], "retry-budget")
    _int(obj["retry_budget"]["limit"], 0, 100000, "retry_budget.limit")
    _int(obj["retry_budget"]["used"], 0, 100000, "retry_budget.used")
    batches = obj["batches"]
    if not isinstance(batches, list) or len(batches) > 10000:
        _fail("batches is not a list of at most 10,000 batches")
    seen = set()
    for entry in batches:
        _check_keys(entry, "plan-batch")
        batch_id = _id("batch", entry["batch_id"], "batches.batch_id")
        if batch_id in seen:
            _fail("two batches share one batch_id")
        seen.add(batch_id)
        _int(entry["attempt"], 1, 3, "batches.attempt")
        _id_list(entry["finding_ids"], "batches.finding_ids")
        _stamp(entry["input_sha256"], _HEX64, "batches.input_sha256")
        _enum(entry["state"], BATCH_STATES, "batches.state")
    for entry in batches:
        batch_id = entry["batch_id"]
        if entry["parent"] != (batch_id.rsplit("-", 1)[0] if "-" in batch_id else None):
            _fail("a batch's parent is not the batch its ID derives from")
        if entry["parent"] is not None and entry["parent"] not in seen:
            _fail("a batch's parent is not in the plan")
    return obj


def validate_pointer(obj: Any) -> Dict[str, Any]:
    """``tachi.plan-pointer/1``: two keys. Returns ``obj``, or raises ``PartError("invalid")``."""
    _check_keys(obj, "plan-pointer")
    if obj["schema"] != POINTER_SCHEMA:
        _fail("schema is not %s" % POINTER_SCHEMA)
    _id("plan", obj["plan_id"], "plan_id")
    return obj


def validate_batch_input(obj: Any) -> Dict[str, Any]:
    """``tachi.batch-input/1`` (contracts/part-files.md section 3). Returns ``obj``, or raises ``PartError("invalid")``."""
    _check_keys(obj, "batch-input")
    if obj["schema"] != BATCH_INPUT_SCHEMA:
        _fail("schema is not %s" % BATCH_INPUT_SCHEMA)
    plan_id = _id("plan", obj["plan_id"], "plan_id")
    batch_id = _id("batch", obj["batch_id"], "batch_id")
    _stage_pair(obj["stage"], obj["agent_type"])
    _id_list(obj["finding_ids"], "finding_ids")
    attempt = _int(obj["attempt"], 1, 3, "attempt")
    parts = path_parts(_path_text(obj["part_path"], "part_path", absolute=True), allow_absolute=True)
    if parts[-3:] != (plan_id, "parts", "%s.a%d.json" % (batch_id, attempt)):
        _fail("part_path is not <plan_id>/parts/<batch_id>.a<attempt>.json")
    if obj["tree_paths"] != {}:
        _fail("tree_paths is {} outside the trees stage")
    if not isinstance(obj["units"], list) or len(obj["units"]) > MAX_IDS or not all(isinstance(u, dict) for u in obj["units"]):
        _fail("units is not a list of at most %d objects" % MAX_IDS)
    if not isinstance(obj["refs"], dict) or len(obj["refs"]) > 20:
        _fail("refs is not a small object")
    for name, path in obj["refs"].items():
        _stamp(name, _NAME, "a refs name")
        _path_text(path, "refs.%s" % name, absolute=True)
    _params(obj["params"])
    return obj


def validate_stage_record(obj: Any) -> Dict[str, Any]:
    """``tachi.stage-record/1`` (contracts/part-files.md section 5). Returns ``obj``, or raises ``PartError("invalid")``."""
    _check_keys(obj, "stage-record")
    if obj["schema"] != STAGE_RECORD_SCHEMA:
        _fail("schema is not %s" % STAGE_RECORD_SCHEMA)
    if not isinstance(obj["stage"], str) or obj["stage"] not in STAGE_AGENTS:
        _fail("stage is unknown")
    _id("plan", obj["plan_id"], "plan_id")
    _enum(obj["status"], RECORD_STATUSES, "status")
    _stamp(obj["tachi_version"], _VERSION_TRIPLE, "tachi_version")
    _utc(obj["started_utc"], "started_utc")
    _utc(obj["finished_utc"], "finished_utc")
    _stamp(obj["input_digest"], _DIGEST, "input_digest")
    if not isinstance(obj["counts"], dict) or not set(obj["counts"]) <= COUNT_KEYS:
        _fail("counts has a key outside the closed set")
    for name, count in obj["counts"].items():
        _int(count, 0, 10 ** 9, "counts.%s" % name)
    _check_keys(obj["batches"], "stage-batches")
    for name in KEY_SETS["stage-batches"][0]:
        _int(obj["batches"][name], 0, 1000000, "batches.%s" % name)
    for field, limit in (("overflow_events", 10000), ("retries", 10000), ("warnings", 1000),
                         ("undeclared_paths", MAX_UNDECLARED_PATHS), ("outputs", 100)):
        if not isinstance(obj[field], list) or len(obj[field]) > limit:
            _fail("%s is not a list of at most %d entries" % (field, limit))
    for event in obj["overflow_events"]:
        _check_keys(event, "overflow-event")
        _id("batch", event["batch_id"], "overflow_events.batch_id")
        _int(event["attempt"], 1, 3, "overflow_events.attempt")
        _enum(event["kind"], OVERFLOW_EVENT_KINDS, "overflow_events.kind")
    for retry in obj["retries"]:
        _check_keys(retry, "retry-entry")
        _id("batch", retry["batch_id"], "retries.batch_id")
        _int(retry["attempt"], 1, 3, "retries.attempt")
        _stamp(retry["cause"], _CODE, "retries.cause")
        children = retry["children"]
        if not isinstance(children, list) or len(children) > 2:
            _fail("retries.children is not a list of at most two batch IDs")
        for child in children:
            _id("batch", child, "retries.children")
    for warning in obj["warnings"]:
        _check_keys(warning, "warning")
        _stamp(warning["code"], _CODE, "warnings.code")
        _closed(warning["detail"], "warnings.detail", 0, 500)
    for relpath in obj["undeclared_paths"]:
        _path_text(relpath, "an undeclared path")
    for output in obj["outputs"]:
        _check_keys(output, "output")
        _path_text(output["path"], "outputs.path")
        _stamp(output["sha256"], _HEX64, "outputs.sha256")
    error = obj["error"]
    if error is not None:
        _check_keys(error, "error")
        _stamp(error["code"], _CODE, "error.code")
        _closed(error["message"], "error.message", 0, 2000)
        if error["batch_id"] is not None:
            _id("batch", error["batch_id"], "error.batch_id")
        _id_list(error["finding_ids"], "error.finding_ids", minimum=0)
        _closed(error["remedy"], "error.remedy", 0, 2000)
    return obj


_DOCUMENTS = {PLAN_SCHEMA: validate_plan, POINTER_SCHEMA: validate_pointer,
              BATCH_INPUT_SCHEMA: validate_batch_input, STAGE_RECORD_SCHEMA: validate_stage_record}


def read_document(path: object, out: object, schema: str) -> Dict[str, Any]:
    """Load one of the four planner and record documents (steps 1 to 4), then validate it against ``schema``.

    ``schema`` is the document the caller expects, so a file that names another schema is ``invalid``: the
    key set is chosen by the caller's expectation and the file's own ``schema`` must agree (F5). Raises
    ``ValueError`` for a ``schema`` that is not one of the four, and ``PartError`` for anything wrong with the file.
    """
    if schema not in _DOCUMENTS:
        raise ValueError("not a document schema: %r" % (schema,))
    obj = load_json(path, out, MAX_DOCUMENT_BYTES[schema])
    if obj.get("schema") != schema:
        _fail("schema is not %s" % schema)
    return _DOCUMENTS[schema](obj)


# =============================================================================
# I/O helpers (T013, slice 1): digests, the atomic write and the provenance stamp
# =============================================================================

def sha256_hex(data: bytes) -> str:
    """The SHA-256 of ``data`` as 64 lowercase hex digits."""
    return hashlib.sha256(data).hexdigest()


def file_digest(path: object) -> str:
    """The SHA-256 of a file's bytes as lowercase hex with no prefix (``plan_digest``, the plan's ``sha256``)."""
    digest = hashlib.sha256()
    with open(os.fspath(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_digest(obj: Any) -> str:
    """``sha256:`` and the hex digest of ``obj``'s canonical JSON: sorted keys, no spaces, ASCII only (NFR-2).

    ``obj`` holds only JSON scalars, lists and objects, so the digest never depends on dictionary order or on
    the plan ID, which the caller leaves out. A ``Decimal`` or any other type raises ``TypeError``.
    """
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256_hex(text.encode("utf-8"))


def atomic_write(path: object, data: Any) -> None:
    """Write ``data`` to ``path`` all at once: a temp file in the same directory, then ``os.replace``.

    ``str`` is written as UTF-8 with no newline translation, ``bytes`` as they are. The file gets the mode an
    ordinary write would (``0666 & ~umask``), not the temp file's ``0600``. A symlink at ``path`` is replaced,
    never followed. If anything fails, the temp file is removed and the error propagates, so a failed write
    leaves the old file and no stray file behind.
    """
    if isinstance(data, str):
        payload = data.encode("utf-8")
    elif isinstance(data, (bytes, bytearray, memoryview)):
        payload = bytes(data)
    else:
        raise TypeError("atomic_write takes text or bytes")
    target = os.fspath(path)
    descriptor, temporary = tempfile.mkstemp(prefix=".tmp-", dir=os.path.dirname(os.path.abspath(target)))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        mask = os.umask(0)
        os.umask(mask)
        os.chmod(temporary, 0o666 & ~mask)
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


VERSION = "4.48.4"  # x-release-please-version

_STAMP_PREFIX = "<!-- tachi-provenance:"
_RENDERER = re.compile(r"[A-Za-z0-9_.-]{1,64}", re.ASCII)
_STAMP = re.compile(r"<!-- tachi-provenance: renderer=([A-Za-z0-9_.-]{1,64}); "
                    r"version=([0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}); input-digest=(sha256:[0-9a-f]{64}) -->", re.ASCII)


def stamp_comment(renderer: str, digest: str) -> str:
    """ADR-050 D4's provenance comment, one line, for the end of a stamped markdown file.

    ``renderer`` is the entry's name (up to 64 of ``A-Za-z0-9_.-``) and ``digest`` is an ``input_digest``.
    Anything else raises ``ValueError``, so the comment can never carry text that ends it early.
    """
    if not isinstance(renderer, str) or _RENDERER.fullmatch(renderer) is None \
            or not isinstance(digest, str) or _DIGEST.fullmatch(digest) is None:
        raise ValueError("a stamp takes an entry name and a sha256: digest in their contract forms")
    return "<!-- tachi-provenance: renderer=%s; version=%s; input-digest=%s -->" % (renderer, VERSION, digest)


def read_stamp(text: str) -> Optional[Dict[str, str]]:
    """The last provenance comment in ``text`` as ``{renderer, version, input_digest}``, or ``None``.

    The last comment wins (the populator's block can follow the stamp). A last comment that is malformed or
    cut short is no stamp: an earlier, valid one is never used in its place.
    """
    if not isinstance(text, str):
        return None
    start = text.rfind(_STAMP_PREFIX)
    if start < 0:
        return None
    match = _STAMP.fullmatch(text[start:].split("\n", 1)[0].rstrip(" \t\r"))
    if match is None:
        return None
    return {"renderer": match.group(1), "version": match.group(2), "input_digest": match.group(3)}


# =============================================================================
# D3's layout (P-6): the path builders every script shares (T013, slice 1)
# =============================================================================

BUILD_DIR = ".tachi-build"
PLAN_SUBDIRS = ("inputs", "parts", "preimage", "staged", "failed")


def _out_dir(out: object) -> str:
    text = os.fspath(out)  # TypeError for None and numbers
    if not isinstance(text, str) or text == "" or "\x00" in text:
        raise ValueError("out is not a usable directory name")
    return os.path.abspath(text)


def _known_stage(stage: object) -> str:
    if not isinstance(stage, str) or stage not in STAGE_AGENTS:
        raise ValueError("stage is not a stage this version knows")
    return stage


def _allow_listed(kind: str, value: object, what: str) -> str:
    if not id_matches(kind, value):
        raise ValueError("%s is not an allow-listed %s ID" % (what, kind))
    return value  # type: ignore[return-value]


def stage_dir(out: object, stage: str) -> str:
    """``<out>/.tachi-build/<stage>``."""
    return os.path.join(_out_dir(out), BUILD_DIR, _known_stage(stage))


def pointer_path(out: object, stage: str) -> str:
    """The current-plan pointer, ``<stage dir>/current.json``."""
    return os.path.join(stage_dir(out, stage), "current.json")


def plan_dir(out: object, stage: str, plan_id: str) -> str:
    """``<stage dir>/<plan_id>``."""
    return os.path.join(stage_dir(out, stage), _allow_listed("plan", plan_id, "plan_id"))


def plan_subdir(out: object, stage: str, plan_id: str, name: str) -> str:
    """One of the plan directory's subdirectories: ``name`` is in ``PLAN_SUBDIRS``."""
    if not isinstance(name, str) or name not in PLAN_SUBDIRS:
        raise ValueError("name is not one of the plan directory's subdirectories")
    return os.path.join(plan_dir(out, stage, plan_id), name)


def plan_path(out: object, stage: str, plan_id: str) -> str:
    """The batch plan, ``<plan dir>/plan.json``."""
    return os.path.join(plan_dir(out, stage, plan_id), "plan.json")


def input_path(out: object, stage: str, plan_id: str, batch_id: str) -> str:
    """A batch input, ``<plan dir>/inputs/<batch_id>.json``."""
    return os.path.join(plan_subdir(out, stage, plan_id, "inputs"), _allow_listed("batch", batch_id, "batch_id") + ".json")


def part_path(out: object, stage: str, plan_id: str, batch_id: str, attempt: int) -> str:
    """The part for one attempt, ``<plan dir>/parts/<batch_id>.a<attempt>.json``, ``attempt`` 1 to 3."""
    if type(attempt) is not int or not 1 <= attempt <= 3:
        raise ValueError("attempt is not 1, 2 or 3")
    name = "%s.a%d.json" % (_allow_listed("batch", batch_id, "batch_id"), attempt)
    return os.path.join(plan_subdir(out, stage, plan_id, "parts"), name)


def stage_record_path(out: object, stage: str, plan_id: str) -> str:
    """The stage record, ``<plan dir>/stage-record.json``."""
    return os.path.join(plan_dir(out, stage, plan_id), "stage-record.json")


def _canonical_file(out: object, stage: str, plan_id: str, subdir: str, name: str) -> str:
    if not isinstance(name, str) or name not in CANONICAL_OUTPUTS[_known_stage(stage)]:
        raise ValueError("name is not one of the stage's canonical outputs")
    return os.path.join(plan_subdir(out, stage, plan_id, subdir), name)


def preimage_path(out: object, stage: str, plan_id: str, name: str) -> str:
    """An earlier output that ``plan`` copied, ``<plan dir>/preimage/<name>``."""
    return _canonical_file(out, stage, plan_id, "preimage", name)


def staged_path(out: object, stage: str, plan_id: str, name: str) -> str:
    """A rendered output, checked before it replaces the canonical file, ``<plan dir>/staged/<name>``."""
    return _canonical_file(out, stage, plan_id, "staged", name)


def failed_path(out: object, stage: str, plan_id: str, name: str) -> str:
    """A changed canonical file that ``fail`` moved aside, ``<plan dir>/failed/<name>``."""
    return _canonical_file(out, stage, plan_id, "failed", name)
