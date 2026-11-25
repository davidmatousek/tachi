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
  sorted ``input:<field>:truncated`` flags and ``counts`` totals the cuts. Every narrative and
  evidence-class string also loses its edge whitespace at intake, after any cut (a snippet is
  dedented first) and with no flag, so a value that a renderer writes and reads back is the same
  bytes on every run. Step 11 (the narrative grammar, numeral ban and fallback) plugs into
  ``_narrative``.
* ``validate_plan``, ``validate_pointer``, ``validate_batch_input`` and ``validate_stage_record``
  return the object they were given, or raise ``PartError("invalid", ...)``.
  ``read_document(path, out, schema)`` loads one of those four documents and validates it.

**I/O helpers and D3's layout (T013, slice 1):**

* ``atomic_write(path, data, mode_of=None)``: a temp file in the target's directory, then ``os.replace``. A regular
  file that it replaces keeps its permission bits (SA-4); a new file gets the mode an ordinary write would (``0666 &
  ~umask``, the umask read once at import). ``mode_of``, a path, takes the bits from that file instead, by the same
  rule: a renderer's staged write names its canonical file, and ``fail``'s restore names the pre-image (P1-2).
  ``str`` is written as UTF-8 with no newline translation.
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

**Shared by the stage entry and the renderers (W1 addendum):**

* ``closed_string(value, what, low=1, high=None)``: the one closed-value string check (D3 step 10), once private as
  ``_closed``, which stays as an alias.
* ``is_declared_path(relpath, stage, plan_id)``: D4's declared-paths grammar.
* ``snapshot_key(relpath)``: a file's key in the plan's ``out_snapshot``, which the planner and both renderers look a file up
  by (EC-2): its path, or a digest stand-in for a name that no plan can hold (SA-5).
* ``retry_history(stage, out, plan)``: a plan's ``(overflow_events, retries)``, read back from its parts on disk.

**The stage-entry path (W2' entry, #443 items 1 to 4).** What the planner and both renderers each held a copy of, and what an entry script written
later uses from its first commit. An entry keeps its own name for each (an alias or a thin wrapper), its ``STAGE`` and ``RENDERER`` literals, and every
message, exit code, reason string and cap it had (S1P-A11):

* ``StageFailure(code, stage, reason, remedy="", batch=None, agent=None, kept=None)``: a stop with D4's exit code and four-line message, ``text()``.
  ``tachi-stage.py``'s ``StageError`` is this class, and a renderer's ``RenderError`` is a subclass that fixes the stage.
  ``run_entry(stage, renderer, args, run, defect=True)`` is an entry's ``main``: it prints the message and returns the code, and turns an unexpected
  exception into ``entry_defect(stage, renderer, exc, kept)``'s exit 4. ``build_parser(renderer, description, out=True, plan=True)`` is the arguments
  entries share (``--version``, ``--out``, ``--plan`` and ``--plan-digest``), and ``entry_arguments(stage, out, plan_id, digest)`` is the first thing an
  entry does with them: ``--out`` is a directory (exit 1), then ``--plan`` and ``--plan-digest`` pass their allow-lists (exit 2), and it returns ``--out``
  as an absolute path. ``plan_arguments(stage, plan_id, digest)`` is its last two checks, for an entry that checks ``--out`` in its own way.
* D3's guard: ``trusted_plan(stage, out, plan_id, digest, complete=False, read_inputs=False, kept=False)`` returns ``(plan, inputs)`` once the pointer,
  the digest, the inputs and the batch inputs check out, with ``entry_document(stage, path, out, schema, what, kept=None)`` (``read_document`` with D4's
  exit codes), ``plan_input_bytes(stage, entry, name, kept=None)`` and ``digest_or_none(path, out=None)``. ``read_parts(stage, out, plan)`` returns
  ``(items, flags, counts)`` from every done batch's part.
* ``RunCore``: the fields that both renderers' ``Run`` hold alike (``warnings``, ``issues``, ``sources``, ``counts``, the threat model's bookkeeping),
  with ``warn(code, detail)``.
* ``read_capped(path, limit, reasons=None)``: the one capped reader that follows no link, returning ``(bytes, reason)``. The reason is ``missing``,
  ``unopenable``, ``not-a-regular-file``, ``unreadable`` or ``too-large``, and ``reasons`` is the caller's one-line map to its own words
  (``RENDERER_READ_REASONS`` is the renderers'). ``load_json`` reads through it, with its own ``PartError`` reasons.
* ``first_forbidden(value, path="", json_only=False)``: the one walker for a character that D3's step 10 forbids, which searches text, mapping keys, list and
  tuple items and a plain object's fields (``json_only``: ``dict`` and ``list`` only, the planner's). ``forbidden_problem(source, finding_id, value,
  place=None, json_only=False, path="")`` is the refusal's reason, or ``None``; the entry raises it with exit 2 and its own remedy.
* The write path: ``stage_and_move(stage, out, plan_id, files, check, kept, reason_text=None)`` stages, reads back, checks and moves the files;
  ``stage_record(...)`` builds a ``tachi.stage-record/1`` object and ``write_stage_record(...)`` checks and writes it with exit 4 (a renderer's end of
  run); ``output_entries(out, names)`` is its ``outputs``. ``walk_out(out)`` and ``undeclared_paths(stage, out, plan)`` are D4's declared-paths check.
* Small helpers: ``utc_now()``, ``dump_json(obj)``, ``record_warning(code, detail)``, ``shorten(text, limit)``, ``relative_path(path, cwd)``,
  ``yaml_quoted(text)`` and ``RETRY_REMEDY``.

**Added at W3 (P0-4):**

* ``forbidden_character(text)``: the first character of ``text`` that D3's step 10 forbids, or ``None``. Step 10 uses it,
  and a renderer calls it where it takes a value from an input that isn't a part, so the set has one definition.

**Added at W3 (the two structured text fields of a controls item, ADR-050 D2):**

* ``MATRIX_ROW_CELLS`` (11) and ``matrix_row_cells(row)``: the cells of a controls ``matrix_row``, split the one way that a
  reader splits a table line, so the part check and the renderer count the same cells (``contracts/module-signatures.md``).
  Step 9 uses them: a controls item whose ``matrix_row`` has any other count of cells, or whose first (Threat ID) cell isn't
  the item's own finding ID, rejects the part, and ``reconcile`` re-dispatches its batch. No other cell can reject an item.
* ``RECOMMENDATION_KEYS`` and ``EFFORT_LEVELS``: the four keys of the section 4 block and the levels that its Effort
  Estimate starts with. Step 9 rejects a ``recommendation_body`` that doesn't hold the keys once each and in order, whose
  Effort Estimate doesn't start with a level, or that has a heading line or a table line (the 1.1 template's "Who writes what").
"""
from __future__ import annotations

import argparse
import copy
import dataclasses
import datetime
import hashlib
import json
import os
import platform
import re
import stat
import sys
import tempfile
import textwrap
import unicodedata
from decimal import Decimal
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

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
    ``control-char`` (any Cc character, and any character that ``forbidden_character`` refuses: a line or paragraph
    separator, a bidi control or a tag character, SA-8), ``backslash``, ``backtick``, ``leading-slash``
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
    # Two definitions of an unsafe character agree here: a path is refused for any Cc character (a tab and a newline
    # included, which prose may hold) and for each one step 10 forbids, so no path holds a character that a part's text
    # may not (SA-8). A lone surrogate was refused above as "encoding".
    if any(unicodedata.category(ch) == "Cc" for ch in value) or forbidden_character(value) is not None:
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

# The stage record's closed `counts` keys: the base counts and the flag kinds (ADR-050 D2, D9). `cell_overwrites` is the
# eighth base count, the controls renderer's: the computed §2 cells that held anything but their own slot token.
COUNT_KEYS = frozenset((
    "units", "open", "resolved", "rendered", "parse_errors", "narrative_fallbacks", "truncations", "cell_overwrites",
    "corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input"))

# name -> (required keys, optional keys), in the contracts' order. Every key is required unless listed optional.
KEY_SETS: Dict[str, Tuple[Tuple[str, ...], Tuple[str, ...]]] = {
    "part": (("schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "items", "fragments"), ()),
    "overflow": (("schema", "plan_id", "batch_id", "stage", "agent_type", "reason"), ()),
    "batch-input": (("schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "attempt", "part_path",
                     "tree_paths", "units", "refs", "params"), ()),
    "plan": (("schema", "plan_id", "stage", "agent_type", "created_utc", "tachi_version", "inputs", "refs",
              "architecture_warning", "params", "batch_size", "unit_count", "preimage", "out_snapshot", "retry_budget",
              "batches"), ()),
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


# The loader's one-line map for ``read_capped``'s reasons: ``reason -> (PartError kind, detail)``. A file over the cap is ``unparseable`` and
# names the cap, so ``_read_regular_file`` builds that one where the cap is known.
_READ_FAILURES = {
    "missing": ("missing", "no file at the planned path"),
    "unopenable": ("invalid", "the file cannot be opened without following a link"),
    "not-a-regular-file": ("invalid", "the planned path is not a regular file"),
    "unreadable": ("invalid", "the file could not be read"),
}


def _read_regular_file(path: object, max_bytes: int) -> bytes:
    """A regular file's bytes through no link, or the ``PartError`` that says why not: ``read_capped`` with this loader's reasons."""
    raw, reason = read_capped(path, max_bytes)
    if raw is not None:
        return raw
    if reason == "too-large":
        raise PartError("unparseable", "the file is over the size cap of %d bytes" % max_bytes)
    raise PartError(*_READ_FAILURES[str(reason)])


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

# D3's closed set of nine references (P0-1 added ``&#126;``). ``tachi_parsers.decode_references`` is built from it, and
# ``part-file-contract-shared.md`` lists it, which T010's drift test compares.
ESCAPE_REFERENCES: Dict[str, str] = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">", "&#124;": "|", "&#96;": "`", "&#123;": "{", "&#10;": "\n", "&#35;": "#",
    "&#126;": "~"}
_REFERENCE_OF = {char: reference for reference, char in ESCAPE_REFERENCES.items()}
_CELL_TRANSLATION = {ord(char): _REFERENCE_OF[char] for char in "&<>|`\n"}
_PROSE_TRANSLATION = {ord(char): _REFERENCE_OF[char] for char in "&<>|`"}
_BRACE_OF_A_PAIR = re.compile(r"\{(?=\{)|(?<=\{)\{")
# The first ``#`` (a heading) or ``~`` (a code fence, as ``~~~``) of a prose line, after any whitespace but a newline.
# On a ``str`` pattern ``\s`` is ``str.isspace()``, which is what ``strip()`` drops, and leaving the newline out means a
# match can't span lines. The leading run is group 1, so the replacement keeps it byte for byte.
_LINE_START_GUARD = re.compile(r"(?m)^([^\S\n]*)([#~])")


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


def _brace_before_a_slot(escaped: str) -> str:
    """A ``{`` just before a slot forms, with the slot's first brace, a ``{{`` that isn't a slot: D3 escapes it too."""
    if escaped.endswith("{"):
        return escaped[:-1] + _REFERENCE_OF["{"]
    return escaped


def _escape(text: str, keep_slots: bool, cell: bool) -> str:
    if not keep_slots:
        return _escape_text(text, cell)
    pieces = _split_slots(text)
    return "".join(
        piece if is_slot else (_brace_before_a_slot if index + 1 < len(pieces) else str)(_escape_text(piece, cell))
        for index, (is_slot, piece) in enumerate(pieces))


def _guard_headings(text: str) -> str:
    """Write the first ``#`` or ``~`` of each line as its reference, so prose forges neither a heading nor a code fence.

    A line that starts with ``~~~``, after any whitespace but a newline, opens a code fence for the next run's tolerant
    reader, and every heading after it, §4 and §6 included, is then read as part of the fence (P0-1). Spaces and tabs
    do that for GitHub as well. A Unicode space (a no-break space, an ideographic space) does it for a reader that
    strips every whitespace character, so the guard looks past those too (ruled at W3). The whitespace before the
    ``#`` or ``~`` stays as it was, byte for byte. A ``~`` anywhere else stays as it is.
    """
    return _LINE_START_GUARD.sub(lambda match: match.group(1) + _REFERENCE_OF[match.group(2)], text)


def escape_cell(text: str, keep_slots: bool = False) -> str:
    """Escape untrusted text for a markdown table cell (ADR-050 D3, "Output"), with the closed ``ESCAPE_REFERENCES``.

    ``&``, ``<``, ``>``, ``|`` and a backtick become references, each ``{`` of a ``{{`` becomes ``&#123;`` and a
    newline becomes ``&#10;``. With ``keep_slots`` a complete slot stays as it is, for the narrative text that a
    renderer persists with its slots (carried text, RR1), and a ``{`` just before a slot is escaped too, so
    ``{{{score:x}}`` is written ``&#123;{{score:x}}``. The one decoder in ``tachi_parsers`` reverses exactly these.
    """
    return _escape(text, keep_slots, True)


def escape_prose(text: str, keep_slots: bool = False) -> str:
    """Escape untrusted text for prose: the cell rules, but line breaks stay and no line starts with ``#``, ``~`` or ``|``.

    A line that would start with ``#`` or ``~`` (after any whitespace but a newline, which is kept as it is) has
    ``&#35;`` or ``&#126;`` in its place, and a ``|`` is always ``&#124;``, so agent text can forge neither a
    heading, a code fence nor a table row. A ``~`` anywhere else, and any ``~`` in a cell, is left as it is.
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
    for index, token in enumerate(tokens):
        if token[0] == "text":
            escaped = _escape_text(token[1], cell)
            pieces.append(_brace_before_a_slot(escaped) if index + 1 < len(tokens) else escaped)
            continue
        kind, name = token[1], token[2]
        value = lookup(kind, canonical_finding_id(name) if kind == "finding" else name)
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("a slot lookup returns text or None")
        pieces.append(_escape_text(value, cell))
    # No slot is left in resolved text, so no `{{` may be: a value's edge brace can't join its neighbour into one.
    result = _BRACE_OF_A_PAIR.sub(_REFERENCE_OF["{"], "".join(pieces))
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
# Step 10's set: Cc other than tab and newline, the separators U+2028 and U+2029, the bidi controls U+200E, U+200F,
# U+061C, U+202A-U+202E and U+2066-U+2069, a lone surrogate (U+D800-U+DFFF, ADR-050 D3 as ruled at W3) and the Unicode
# tag block (U+E0000-U+E007F, SA-7). Each is written as an escape: a bidi control or a separator typed into this line
# would reorder or split what a reviewer reads (Trojan Source, CVE-2021-42574), and the line defines the very set.
_FORBIDDEN_CHARACTERS = re.compile(
    "[\x00-\x08\x0b-\x1f\x7f-\x9f"  # C0, DEL and C1 but not tab and newline
    "\u2028\u2029"  # the line and paragraph separators
    "\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069"  # the bidi controls
    "\ud800-\udfff"  # a lone surrogate
    "\U000e0000-\U000e007f]"  # the Unicode tag block
)


def forbidden_character(text: str) -> Optional[str]:
    """The first character of ``text`` that D3's step 10 forbids, or ``None`` (P0-4). ``text`` must be a ``str``.

    The set is the contract's: a control character other than tab and newline (C0, DEL and C1), the separators
    U+2028 and U+2029, the bidi controls U+200E, U+200F, U+061C, U+202A to U+202E and U+2066 to U+2069, a lone
    surrogate, U+D800 to U+DFFF (ADR-050 D3, ruled at W3), and a Unicode tag character, U+E0000 to U+E007F
    (SA-7: a tag shows as nothing, yet each one stands for an ASCII character, so it can carry text past a reader
    to a later agent). The variation selectors and the joiners are not in it.

    Only a JSON escape can spell a lone surrogate, and no UTF-8 file can carry one, so a part never reaches step 10
    with one: ``load_json`` refuses it first, as ``unparseable``. A tag character is another matter: it is a valid
    scalar value, so a part can hold it as UTF-8 or as an escaped surrogate pair, and step 10 refuses it either way.

    Step 10 uses this on every string of a part. A renderer calls it where it takes a value from an input that
    isn't a part (``threats.md``, a baseline file, ``threats.sarif``), so the character set has one definition,
    and a surrogate that such an input's JSON escape spells is refused where it is taken, before a write can fail
    on it. ``path_problem`` asks it too, so a path holds no character that a part's text may not. The length limit
    is step 10's too, but it isn't part of this predicate.
    """
    found = _FORBIDDEN_CHARACTERS.search(text)
    return found.group(0) if found is not None else None


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
    """Step 10: at most 16,384 characters, and none of the characters ``forbidden_character`` names."""
    if len(text) > MAX_STRING_CHARS or forbidden_character(text) is not None:
        _fail("%s is over %d characters or holds a character the contract forbids" % (what, MAX_STRING_CHARS))


def closed_string(value: Any, what: str, low: int = 1, high: Optional[int] = None) -> str:
    """The one check for a closed-value string (ADR-050 D3 steps 6 and 10). Returns ``value``, or raises.

    ``value`` must be text of ``low`` to ``high`` characters (no upper limit but the 16,384 of step 10 when ``high``
    is ``None``), with no control character other than tab and newline and none of the bidi, separator, surrogate
    or tag characters that D3 forbids. A closed value is checked and never cut, so a string over its range is
    rejected, not shortened.
    Raises ``PartError("invalid")`` whose detail names ``what`` and never echoes ``value``.
    """
    if not isinstance(value, str) or len(value) < low or (high is not None and len(value) > high):
        _fail("%s is not text in range" % what)
    _check_characters(value, what)
    return value


_closed = closed_string  # the name this function had before it was published; `tachi-stage.py` still calls it


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
           minimum: int = 0, lines: Optional[int] = None, dedent: bool = False) -> str:
    """A prose field: cut at its limit (and at ``lines`` lines) and flagged, never rejected for length (RR2).

    Step 9's order is the cut, then the edge whitespace: a snippet (``dedent``) is dedented with ``textwrap.dedent``
    so its lines keep their relative indentation, and every prose string is then ``strip()``ped, the predicate the
    table readers apply to a cell, so a carried value reads back byte for byte (T033, T056). The strip raises no
    flag, and a required field (``minimum``) that is empty afterwards rejects the part. Then step 10 on what is
    left, then step 11 for a narrative field.
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
    if dedent:
        value = textwrap.dedent(value)
    value = value.strip()
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
        closed_string(reach["zone"], "reachability.zone", 1, 120)
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
    if path_problem(closed_string(entry["file"], "evidence.file", 1, 300)) is not None:
        _fail("evidence.file breaks D7's relative path rule")
    _int(entry["line"], 1, None, "evidence.line")
    if not id_matches("language", entry["language"]):
        _fail("evidence.language does not match the language pattern")
    entry["snippet"] = _prose(entry["snippet"], 600, "evidence.snippet", state, lines=5, dedent=True)
    entry["summary"] = _prose(entry["summary"], 160, "evidence.summary", state)
    if "assessment" in entry:
        _check_keys(entry["assessment"], "assessment")
        for dimension in ASSESSMENT_DIMENSIONS:
            cell = entry["assessment"][dimension]
            _check_keys(cell, "assessment-dimension")
            _enum(cell["rating"], CONFIDENCES, "evidence.assessment.%s.rating" % dimension)
            cell["rationale"] = _prose(cell["rationale"], 160, "evidence.assessment." + dimension, state, narrative=True)


# The controls `matrix_row` (ADR-050 D2; `contracts/module-signatures.md`, "The controls `matrix_row`"): the 11 cells of
# K8's section 2 table, the finding's ID first. Only the count and the ID cell are structural, so only they reject an item.
MATRIX_ROW_CELLS = 11


def matrix_row_cells(row: str) -> List[str]:
    """The cells of a controls ``matrix_row``, split the one way that a reader splits a table line (ADR-050 D3).

    The line's edge whitespace goes first, then one leading and one trailing ``|`` where present, so a row reads the
    same with or without its outer pipes. The rest splits on raw ``|``, and each cell loses its edge whitespace, as
    ``tachi_parsers.parse_markdown_table`` strips a cell. A reference such as ``&#124;`` holds no ``|``, so it never
    splits a row; GFM's ``\\|`` does, as it always has (NFR-1). Nothing is decoded here: the readers decode a cell after
    the split, and no check on a row reads a decoded value, because no reference decodes to a character that a finding
    ID holds. ``row`` must be a ``str``.
    """
    line = row.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def _check_matrix_row(row: str, finding_id: str) -> None:
    """ADR-050 D2's two structural checks on a controls ``matrix_row``: 11 cells, and the item's own ID in the first.

    ``finding_id`` is the item's canonical ID, which ``_classify`` has checked against the allow-list, so a detail may
    name it. The row's own text is never echoed. A mismatch in any other cell is the renderer's to flag, or to overwrite
    and count (D2), so it never rejects the item here.
    """
    cells = matrix_row_cells(row)
    if len(cells) != MATRIX_ROW_CELLS:
        _fail("matrix_row of %s has a cell count of %d, not %d" % (finding_id, len(cells), MATRIX_ROW_CELLS))
    if not id_matches("finding", cells[0]):
        _fail("matrix_row of %s has a Threat ID cell that is not an allow-listed finding ID" % finding_id)
    if canonical_finding_id(cells[0]) != finding_id:
        _fail("matrix_row of %s has a Threat ID cell for another finding" % finding_id)


# The controls `recommendation_body` (ADR-050 D2, "The §4 body"; the 1.1 template's "Who writes what"): the four keys of
# the section 4 block, each once and in this order, each at the start of a line. The Effort Estimate starts with a level.
RECOMMENDATION_KEYS = ("What to Implement", "Where to Implement", "Reference Patterns", "Effort Estimate")
EFFORT_LEVELS = ("Low", "Medium", "High")
_EFFORT_LEVEL = re.compile(r"(?:%s)(?!\w)" % "|".join(EFFORT_LEVELS))


def _check_recommendation_body(body: str, finding_id: str) -> None:
    """ADR-050 D2's structural checks on a controls ``recommendation_body``: its keys, its Effort, and no heading or table.

    A key is a line that starts, after any whitespace, with ``**<key>**:``. The four have to come once each and in
    order. Other lines are the keys' own text, so a value may run on over more than one line. The Effort Estimate has
    to start with ``Low``, ``Medium`` or ``High``, and no line may start with ``#`` or ``|``, as a heading or a table
    row does (``escape_prose`` guards the same line start). ``finding_id`` is the item's canonical ID, which a detail may
    name. A key name comes from the closed set, so a detail may list the ones found. The body's own text is never echoed.
    """
    found: List[str] = []
    effort = ""
    for line in body.split("\n"):
        text = line.lstrip()
        if text.startswith("#"):
            _fail("recommendation_body of %s has a heading line" % finding_id)
        if text.startswith("|"):
            _fail("recommendation_body of %s has a table line" % finding_id)
        for key in RECOMMENDATION_KEYS:
            label = "**%s**:" % key
            if text.startswith(label):
                found.append(key)
                if key == RECOMMENDATION_KEYS[-1]:
                    effort = text[len(label):].lstrip()
                break
    if found != list(RECOMMENDATION_KEYS):
        _fail("recommendation_body of %s has the keys [%s], not the four once each and in order" % (finding_id, ", ".join(found)))
    if _EFFORT_LEVEL.match(effort) is None:
        _fail("recommendation_body of %s has an Effort Estimate that does not start with Low, Medium or High" % finding_id)


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
    _check_matrix_row(item["matrix_row"], item["finding_id"])  # after the cut, so it checks the row that is kept
    if (item["recommendation_body"] is None) != (status == "found"):
        _fail("recommendation_body is null exactly when the status is found")
    if item["recommendation_body"] is not None:
        item["recommendation_body"] = _prose(item["recommendation_body"], 2000, "recommendation_body", state)
        _check_recommendation_body(item["recommendation_body"], item["finding_id"])  # after the cut, as the row's check is


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
            closed_string(item, "params." + key, 0, 1024)
        elif item is not None and type(item) not in (bool, int):
            _fail("params.%s is not a scalar" % key)


def _refs(value: Any) -> None:
    """The stage's pointers: at most 20 closed names, each an absolute path that passes D7's syntactic rule.

    The plan holds them once (the authority) and each batch input holds a verbatim copy, so both are checked here.
    """
    if not isinstance(value, dict) or len(value) > 20:
        _fail("refs is not a small object")
    for name, path in value.items():
        _stamp(name, _NAME, "a refs name")
        _path_text(path, "refs.%s" % name, absolute=True)


def _warning_entry(entry: Any, what: str) -> None:
    """One ``{code, detail}`` warning, as a stage record lists it: a code of ``[a-z0-9:_.-]{1,64}`` and a detail of 0 to 500 characters."""
    _check_keys(entry, "warning")
    _stamp(entry["code"], _CODE, "%s.code" % what)
    closed_string(entry["detail"], "%s.detail" % what, 0, 500)


def _stage_pair(stage: Any, agent_type: Any) -> None:
    if not isinstance(stage, str) or STAGE_AGENTS.get(stage) != agent_type:
        _fail("stage is unknown, or agent_type is not the stage's agent")


def validate_plan(obj: Any) -> Dict[str, Any]:
    """``tachi.plan/1`` (contracts/part-files.md section 4). Returns ``obj``, or raises ``PartError("invalid")``.

    ``refs`` is the stage's pointers, as a batch input has them, and ``architecture_warning`` is ``null`` or the one
    warning that ``plan`` raised when it refused the ``--architecture`` candidate (ruled at W2).
    """
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
    _refs(obj["refs"])
    if obj["architecture_warning"] is not None:
        _warning_entry(obj["architecture_warning"], "architecture_warning")
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
    _refs(obj["refs"])
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
        _warning_entry(warning, "warnings")
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
        closed_string(error["message"], "error.message", 0, 2000)
        if error["batch_id"] is not None:
            _id("batch", error["batch_id"], "error.batch_id")
        _id_list(error["finding_ids"], "error.finding_ids", minimum=0)
        closed_string(error["remedy"], "error.remedy", 0, 2000)
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


def _read_umask() -> int:
    """The process umask. Python reads it only by setting it to 0 and putting it back, so this runs once (below)."""
    mask = os.umask(0)
    os.umask(mask)
    return mask


# A new file's mode needs the umask, and reading it leaves the process's umask at 0 for the moment between the two
# calls in ``_read_umask``, which a thread or a signal handler could observe. So it is read once, here at import,
# while the process is still starting up, and never in ``atomic_write`` (S7-3).
_UMASK = _read_umask()


def _mode_for(target: str) -> int:
    """The permission bits a file written in place of ``target`` gets (SA-4).

    A regular file at ``target`` hands over its own ``rwx`` bits for user, group and other, so a replace does not undo
    an adopter's ``chmod 600``. Anything else, such as nothing at all, a symlink (the replace removes the link and its
    own mode says nothing about the new file) or a device, gets what an ordinary write would give: ``0666 & ~umask``.
    """
    try:
        old = os.lstat(target)
    except OSError:
        old = None  # nothing is there yet, or nothing can be read: the replace itself says which
    if old is not None and stat.S_ISREG(old.st_mode):
        return stat.S_IMODE(old.st_mode) & 0o777
    return 0o666 & ~_UMASK


def atomic_write(path: object, data: Any, mode_of: Optional[object] = None) -> None:
    """Write ``data`` to ``path`` all at once: a temp file in the same directory, then ``os.replace``.

    ``str`` is written as UTF-8 with no newline translation, ``bytes`` as they are. A regular file that is replaced
    keeps its permission bits, so an adopter's ``chmod 600`` survives the next run (SA-4). A file that is new, a
    symlink or anything else that is not a regular file gets the mode an ordinary write would (``0666 & ~umask``,
    the umask as it was when this module was imported), not the temp file's ``0600``. The mode is set on the open
    descriptor, never on the temp file's path (S7-3). Ownership is not kept, because keeping it takes privilege: the
    new file belongs to the user who writes it. The old file's setuid, setgid and sticky bits, ACLs, extended
    attributes and hard links are not kept either. A symlink at ``path`` is replaced, never followed. If anything
    fails, the temp file is removed and the error propagates, so a failed write leaves the old file and no stray
    file behind.

    ``mode_of``, when given, is a path whose permission bits the new file takes in place of ``path``'s own, through
    the same rule (``_mode_for``): a regular file hands over its ``rwx`` bits, and anything else, nothing at all
    included, gives the ordinary mode. It is for a file that is written under one name and moved onto another. A
    renderer stages its output beside the canonical name and passes that name, and ``fail`` writes a pre-image back
    onto a name that no longer exists and passes the pre-image's path (P1-2, the rest of SA-4). ``None`` is the
    default, and then ``path`` names the file whose bits are kept.
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
            mode = _mode_for(target if mode_of is None else os.fspath(mode_of))
            if hasattr(os, "fchmod"):
                os.fchmod(handle.fileno(), mode)
            else:  # Windows before Python 3.13: a mode there is the read-only flag, and a symlink swap is no hazard
                os.chmod(temporary, mode)
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


VERSION = "4.48.5"  # x-release-please-version

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


# =============================================================================
# Shared by the stage entry and the renderers (W1 addendum: moved from `tachi-stage.py`, byte for byte)
# =============================================================================

def snapshot_key(relpath: str) -> str:
    """A file's key in the plan's ``out_snapshot``: its path, or, for a name that D7's rule refuses and so no plan could hold, a stand-in (SA-5; EC-2).

    The test is ``path_problem`` itself, the rule that the plan's own validator applies to each key, so the stand-in is for any name that the
    rule refuses, whatever it comes to refuse (SA-8 widened it to the separators, bidi controls and tag characters), and no list of cases is
    kept here. The stand-in is ``./unrecordable:`` and the SHA-256 of the name's bytes. It passes the plan's own path check, because the ``./``
    keeps the colon out of the first component, and no path that a walk of ``--out`` yields can equal it, because those never start with
    ``./``. So an odd name that was there when the plan was made is found again unchanged and is not reported, while a file planted beside it is.

    The planner keys the snapshot by it and looks each file up by it at ``fail``, and both renderers look each file up by it before the declared-paths
    check, so the three are one key (before EC-2 the renderers looked up the raw path, and a clean run that left such a name in place warned
    ``undeclared-paths-unrecordable`` and exited 5). Before SA-5, one such name skipped the whole check, which a repository could use to hide a file.
    """
    if path_problem(relpath) is None:
        return relpath
    return "./unrecordable:" + sha256_hex(os.fsencode(relpath))


def is_declared_path(relpath: str, stage: str, plan_id: str) -> bool:
    """D4's declared-paths grammar for a stage: its canonical files and D3's exact layout, nothing else.

    ``relpath`` is a path under ``--out`` written with ``/``. ``True`` for the stage's canonical outputs, for
    ``.tachi-build/<stage>/current.json``, and, under ``.tachi-build/<stage>/<plan_id>/``, for ``plan.json``,
    ``stage-record.json``, ``inputs/<batch_id>.json``, ``parts/<batch_id>.a<1 to 3>.json`` and a canonical output
    in ``preimage/``, ``staged/`` or ``failed/``. Anything else, such as a script an agent wrote, is undeclared.
    Every path that the layout builders make is declared. ``KeyError`` for a stage with no canonical outputs.
    """
    parts = relpath.split("/")
    if len(parts) == 1:
        return parts[0] in CANONICAL_OUTPUTS[stage]
    if parts[:2] != [BUILD_DIR, stage]:
        return False
    rest = parts[2:]
    if rest == ["current.json"]:
        return True
    if len(rest) < 2 or rest[0] != plan_id:
        return False
    rest = rest[1:]
    if rest in (["plan.json"], ["stage-record.json"]):
        return True
    if len(rest) != 2:
        return False
    subdirectory, name = rest
    if subdirectory == "inputs":
        return name.endswith(".json") and id_matches("batch", name[:-5])
    if subdirectory == "parts":
        batch_id, _, tail = name.partition(".a")
        return tail in ("1.json", "2.json", "3.json") and id_matches("batch", batch_id)
    return subdirectory in ("preimage", "staged", "failed") and name in CANONICAL_OUTPUTS[stage]


def retry_history(stage: str, out: object, plan: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """The overflow events and retries a plan implies, each failed attempt's cause read back from its part (NFR-5).

    Returns ``(overflow_events, retries)``, the two stage-record lists, in plan order. An attempt that was retried as
    it was, a batch that was halved, and a batch that ran out of retries each leave one event, and every attempt
    but a failed batch's last also leaves one retry. A halved batch's retry names its children, sorted. ``kind`` is
    the part's state, with an overflow object reported as ``overflow-reported``; a part that has turned valid since
    its attempt was given up was still not counted, so it reads as ``missing``. ``plan`` is a validated plan.
    """
    by_id = {entry["batch_id"]: entry for entry in plan["batches"]}
    children: Dict[str, List[str]] = {}
    for entry in plan["batches"]:
        if entry["parent"] is not None:
            children.setdefault(entry["parent"], []).append(entry["batch_id"])

    def cause(entry: Dict[str, Any], attempt: int) -> str:
        result = read_part(part_path(out, stage, plan["plan_id"], entry["batch_id"], attempt), out, plan["plan_id"],
                           entry["batch_id"], stage, plan["agent_type"], entry["finding_ids"])
        return "missing" if result.state == "done" else result.state

    events: List[Dict[str, Any]] = []
    retries: List[Dict[str, Any]] = []
    for entry in plan["batches"]:
        first = 1 if entry["parent"] is None else by_id[entry["parent"]]["attempt"] + 1
        failed_attempts = list(range(first, entry["attempt"]))
        if entry["state"] in ("split", "failed"):
            failed_attempts.append(entry["attempt"])
        for attempt in failed_attempts:
            reason = cause(entry, attempt)
            events.append({"batch_id": entry["batch_id"], "attempt": attempt,
                           "kind": "overflow-reported" if reason == "overflow" else reason})
            if attempt < entry["attempt"] or entry["state"] == "split":
                retries.append({"batch_id": entry["batch_id"], "attempt": attempt, "cause": reason,
                                "children": sorted(children.get(entry["batch_id"], [])) if attempt == entry["attempt"] else []})
    return events, retries


# =============================================================================
# The stage-entry path (W2' entry, #443 items 1 to 4): what every entry script shares
#
# Moved here from the two renderers and the planner, which each held a copy. Each entry keeps its own name for what it uses (an alias or a thin
# wrapper) and its own messages, exit codes, reason strings and caps, so a caller sees no change (S1P-A11, S1P-PM2). C1 holds: nothing here
# imports a tachi module, so a value from ``tachi_parsers``, ``tachi_scoring`` or ``sarif_common`` comes in as an argument.
# =============================================================================

# D4's remedy for a failure that a re-run clears: the earlier outputs were left or put back as they were. Both renderers say it.
RETRY_REMEDY = "re-run the command; the earlier outputs were left or put back as they were"

# ``read_capped``'s reasons in the renderers' words: a file that can't be opened, for any cause, is ``unreadable``. ``stage_and_move`` reads the staged
# files back under it, and a renderer's own read of an input passes it too, so a message that names a reason uses one vocabulary.
RENDERER_READ_REASONS = {"missing": "unreadable", "unopenable": "unreadable"}


def utc_now() -> str:
    """The current time as ``YYYY-MM-DDTHH:MM:SSZ``, UTC. The stage record's ``finished_utc`` is the one place a stage entry reads the clock."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump_json(obj: Any) -> str:
    """Stable JSON for a document or a record: sorted keys, two-space indent, ASCII escapes, one trailing newline."""
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def record_warning(code: str, detail: str) -> Dict[str, str]:
    """One stage-record warning, its code and detail made safe for the record's rules, the detail cut at 500."""
    return {"code": code[:64], "detail": "".join(char if char.isprintable() else " " for char in detail)[:500]}


def shorten(text: str, limit: int) -> str:
    """output-formatting.md's rule: over ``limit`` characters, keep ``limit - 3`` and add three dots."""
    return text if len(text) <= limit else text[:limit - 3] + "..."


def relative_path(path: str, cwd: str) -> Optional[str]:
    """``path`` relative to the working directory with ``/`` separators, or ``None`` when it isn't under it.

    The working directory is found by file identity, as ``under`` finds it, so a path that is spelled through a symbolic link (as macOS spells its
    temporary directory) still reads as the tail below the directory, never as a ``..`` climb.
    """
    if not under(cwd, path):
        return None
    tail: List[str] = []
    current = os.path.abspath(path)
    while not (os.path.lexists(current) and os.path.samefile(current, cwd)):
        tail.append(os.path.basename(current))
        current = os.path.dirname(current)
    return "/".join(reversed(tail)) or "."


def yaml_quoted(text: Optional[str]) -> str:
    """A YAML double-quoted scalar, or ``null`` for ``None`` or text that the frontmatter readers can't carry."""
    if text is None or any(char in text for char in '"\\') or not text.isprintable():
        return "null"
    return '"%s"' % text


class StageFailure(Exception):
    """A stop with D4's exit code and its four-line message: ``TACHI <STAGE> FAILED``, the batch or agent, ``Remedy:`` and ``Kept for diagnosis:``.

    ``stage`` names the stage in the banner (``None`` reads ``STAGE``). ``batch`` is ``(batch ID, its finding IDs)``, ``agent`` the typed agent that
    could not be spawned, and ``kept`` the plan directory that is kept for diagnosis. A line whose value is empty is left out. An entry's own class is
    this one (``tachi-stage.py``'s ``StageError``) or a subclass that fixes the stage (a renderer's ``RenderError``), and the code here raises this
    class, so an entry's ``main`` catches it through ``run_entry``.
    """

    def __init__(self, code: int, stage: Optional[str], reason: str, remedy: str = "", batch: Optional[Tuple[str, str]] = None,
                 agent: Optional[str] = None, kept: Optional[str] = None) -> None:
        super().__init__(reason)
        self.code, self.stage, self.reason, self.remedy = code, stage, reason, remedy
        self.batch, self.agent, self.kept = batch, agent, kept

    def text(self) -> str:
        lines = ["TACHI %s FAILED: %s" % ((self.stage or "STAGE").upper(), self.reason)]
        if self.batch:
            lines.append("Batch %s: %s" % self.batch)
        if self.agent:
            lines.append("Agent: %s" % self.agent)
        if self.remedy:
            lines.append("Remedy: %s" % self.remedy)
        if self.kept:
            lines.append("Kept for diagnosis: %s" % self.kept)
        return "\n".join(lines)


def read_capped(path: object, limit: int, reasons: Optional[Mapping[str, str]] = None) -> Tuple[Optional[bytes], Optional[str]]:
    """A regular file's bytes through no link, or ``(None, reason)``: the one capped reader (SA-12, EC-3).

    The file is opened with ``O_NOFOLLOW`` and without blocking, must be a regular file, and is read in chunks until it ends or passes ``limit`` bytes
    (a file of exactly ``limit`` bytes is read). It returns ``(bytes, None)``, and ``bytes`` is empty for an empty file. ``limit`` has no default: a
    caller reads the cap it means when it calls, so a cap that a test or a later amendment changes is the one that is used.

    The reason is canonical and names one cause: ``missing`` (nothing is there), ``unopenable`` (anything else stops the open, a link above all),
    ``not-a-regular-file``, ``unreadable`` (the read failed once the file was open) and ``too-large``. ``reasons``, when given, is the caller's one-line
    map from those to its own words; a reason that it doesn't list is kept as it is. A path that isn't text or a path-like object is a ``TypeError``,
    and one with a NUL is a ``ValueError``, as for ``os.open``.
    """
    flags = os.O_RDONLY
    for name in ("O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):
        flags |= getattr(os, name, 0)

    def said(reason: str) -> str:
        return reason if reasons is None else reasons.get(reason, reason)

    try:
        descriptor = os.open(os.fspath(path), flags)
    except FileNotFoundError:
        return None, said("missing")
    except OSError:
        return None, said("unopenable")
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return None, said("not-a-regular-file")
        chunks, total = [], 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                return b"".join(chunks), None
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                return None, said("too-large")
    except OSError:
        return None, said("unreadable")
    finally:
        os.close(descriptor)


def first_forbidden(value: Any, path: str = "", json_only: bool = False) -> Optional[Tuple[str, str]]:
    """``(path, character)`` of the first string under ``value`` that holds a character D3's step 10 forbids, or ``None``: the one walker (SA-12, EC-4).

    Text, mapping keys, list and tuple items and the fields of a plain object are searched in order. A number, a date or ``None`` holds no text.
    ``path`` is dotted, and is for a message only: ``a.0.b`` for the ``b`` of the first item under ``a``. The character set is
    ``forbidden_character``'s, so the parts, the inputs and the written files share one definition. ``json_only`` limits the search to what a JSON
    document holds, text, ``dict`` keys and values, and ``list`` items, which is all that the planner searches: a tuple, another kind of mapping and a
    plain object hold nothing then.
    """
    if isinstance(value, str):
        found = forbidden_character(value)
        return (path, found) if found is not None else None
    if json_only:
        if isinstance(value, dict):
            children = value.items()
        elif isinstance(value, list):
            children = enumerate(value)
        else:
            return None
    elif isinstance(value, Mapping):
        children = value.items()
    elif isinstance(value, (list, tuple)):
        children = enumerate(value)
    elif hasattr(value, "__dict__"):
        children = vars(value).items()
    else:
        return None
    for key, child in children:
        label = "%s.%s" % (path, key) if path else str(key)
        found = first_forbidden(key, label, json_only) or first_forbidden(child, label, json_only)   # a key is text too
        if found is not None:
            return found
    return None


def forbidden_problem(source: str, finding_id: Optional[str], value: Any, place: Optional[Callable[[str], Optional[str]]] = None,
                      json_only: bool = False, path: str = "") -> Optional[str]:
    """The reason to refuse ``value``, which an entry takes from an input that isn't a part, or ``None`` when it holds no forbidden character.

    Step 10 checks a part. Text from ``threats.md``, a SARIF or a baseline reaches the escapers unchecked, and a carriage return, an escape or a bidi
    control would then forge a heading, drive a terminal or reorder what a reader sees (NFR-10, P0-4). So each value is checked where it is taken, and
    the entry raises the reason with exit 2 and its own remedy. ``source`` names the file the value came from, and ``finding_id`` the finding it
    belongs to: ``None`` is a component, zone or layer name, which ``place``, given the character, names by its table and line when it can. The reason
    gives the character's code point and never the text, so it can't carry the character to a terminal. ``json_only`` is ``first_forbidden``'s, and
    ``path`` is the name that the reason gives ``value`` (the field it is the value of), which the places inside it follow.
    """
    found = first_forbidden(value, path, json_only)
    if found is None:
        return None
    if finding_id:
        where = "the %s of %s" % (ascii(found[0])[1:-1], finding_id)
    else:
        where = (place(found[1]) if place is not None else None) or "a component, zone or layer name"
    return "%s holds the character U+%04X, which the part contract forbids, in %s" % (source, ord(found[1]), where)


def entry_document(stage: str, path: str, out: str, schema: str, what: str, kept: Optional[str] = None) -> Dict[str, Any]:
    """``read_document`` with D4's exit codes: 1 for a missing file, 2 for anything the contract refuses (a ``StageFailure``)."""
    try:
        return read_document(path, out, schema)
    except PartError as exc:
        if exc.kind == "missing":
            raise StageFailure(1, stage, "%s is missing" % what, "re-run the plan step", kept=kept) from None
        raise StageFailure(2, stage, "%s is not acceptable (%s)" % (what, exc.detail), "re-run the command", kept=kept) from None


def digest_or_none(path: str, out: Optional[str] = None) -> Optional[str]:
    """A file's digest, or ``None`` when it is missing, unreadable, or (given ``out``) fails the path guard."""
    if out is not None and path_guard_problem(path, out) is not None:
        return None
    try:
        return file_digest(path)
    except OSError:
        return None


def plan_input_bytes(stage: str, entry: Mapping[str, Any], name: str, kept: Optional[str] = None) -> bytes:
    """A digest-checked plan input's bytes. A file that changed or vanished since plan, or one over ``MAX_AGENT_INPUT_BYTES``, is exit 2."""
    try:
        with open(entry["path"], "rb") as handle:
            raw = handle.read(MAX_AGENT_INPUT_BYTES + 1)
    except OSError:
        raw = None
    if raw is None or len(raw) > MAX_AGENT_INPUT_BYTES or sha256_hex(raw) != entry["sha256"]:
        raise StageFailure(2, stage, "the input %s changed (or vanished) since plan" % name, "re-run the command", kept=kept)
    return raw


def trusted_plan(stage: str, out: str, plan_id: str, digest: str, complete: bool = False, read_inputs: bool = False,
                 kept: bool = False) -> Tuple[Dict[str, Any], Dict[str, bytes]]:
    """The plan ``--plan`` names, once the pointer, its digest, its inputs and every batch input check out: D3's guard, "planner state is checked, not trusted".

    A plan file or batch input edited after ``plan``, a ``--plan`` that disagrees with ``current.json``, an input that changed, or a digest that
    differs is a ``StageFailure`` with exit 2 (1 for a file that is missing). Returns ``(plan, inputs)``. Nothing is written. Three flags choose how
    an entry uses the guard, and each keeps that entry's behavior:

    * ``complete``: refuse a plan with a batch still ``pending`` or ``failed`` (exit 2, naming the first), after the plan is known to be this one and
      before any input is read. A renderer needs every batch done. The planner's ``reconcile`` and ``fail`` work with the others.
    * ``read_inputs``: how the plan's files are checked. ``True`` is a renderer's: each input is read, at most ``MAX_AGENT_INPUT_BYTES``, in name order,
      and ``inputs`` holds its bytes (``plan_input_bytes``), and an I/O error while a batch input is checked is not caught, so it ends the run as an
      unexpected error. ``False`` is the planner's: each input is digested, in the plan's order, ``inputs`` is empty, and a file that can't be read
      counts as a changed one (``digest_or_none``).
    * ``kept``: each refusal after the pointer's names the plan directory in D4's ``Kept for diagnosis`` line. The pointer's own never does.
    """
    held = plan_dir(out, stage, plan_id) if kept else None
    pointer = entry_document(stage, pointer_path(out, stage), out, POINTER_SCHEMA, "the plan pointer")
    if pointer["plan_id"] != plan_id:
        raise StageFailure(2, stage, "--plan %s disagrees with current.json, which names %s" % (plan_id, pointer["plan_id"]),
                           "pass the plan ID that plan printed", kept=held)
    path = plan_path(out, stage, plan_id)
    problem = path_guard_problem(path, out)
    if problem == "missing":
        raise StageFailure(1, stage, "plan.json is missing", "re-run the plan step", kept=held)
    if problem is not None:
        raise StageFailure(2, stage, "plan.json failed the path guard (%s)" % problem, "re-run the command", kept=held)
    if file_digest(path) != digest:
        raise StageFailure(2, stage, "the plan file's digest differs from --plan-digest",
                           "pass the digest that the last plan or reconcile printed; if the plan was edited, re-run the command", kept=held)
    plan = entry_document(stage, path, out, PLAN_SCHEMA, "plan.json", held)
    if (plan["plan_id"], plan["stage"]) != (plan_id, stage):
        raise StageFailure(2, stage, "plan.json is for another plan or stage", "re-run the command", kept=held)
    if complete:
        unfinished = [entry for entry in plan["batches"] if entry["state"] in ("pending", "failed")]
        if unfinished:
            first = unfinished[0]
            raise StageFailure(2, stage, "batch %s is %s, so the plan is not complete" % (first["batch_id"], first["state"]),
                               "run reconcile until it exits 0, then render", batch=(first["batch_id"], ", ".join(first["finding_ids"])), kept=held)
    inputs: Dict[str, bytes] = {}
    if read_inputs:
        inputs = {name: plan_input_bytes(stage, entry, name, held) for name, entry in sorted(plan["inputs"].items())}
    else:
        for name, entry in plan["inputs"].items():
            if digest_or_none(entry["path"]) != entry["sha256"]:
                raise StageFailure(2, stage, "the input %s changed (or vanished) since plan" % name, "re-run the command", kept=held)
    for entry in plan["batches"]:
        stored = input_path(out, stage, plan_id, entry["batch_id"])
        if read_inputs:
            changed = path_guard_problem(stored, out) is not None or file_digest(stored) != entry["input_sha256"]
        else:
            changed = digest_or_none(stored, out) != entry["input_sha256"]
        if changed:
            raise StageFailure(2, stage, "the batch input %s changed after plan" % entry["batch_id"], "re-run the command", kept=held)
    return plan, inputs


def read_parts(stage: str, out: str, plan: Mapping[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]], Dict[str, int]]:
    """Every done batch's part, re-validated against the plan: ``(items by canonical ID, flags by ID, counts)``.

    Only the current plan's parts at each batch's current attempt count, so an earlier plan's part or an earlier attempt never does. A part that no
    longer validates is a ``StageFailure`` that names its batch: exit 1 for a missing one, 2 for any other.
    """
    items: Dict[str, Dict[str, Any]] = {}
    flags: Dict[str, List[str]] = {}
    counts = {"narrative_fallbacks": 0, "truncations": 0}
    kept = plan_dir(out, stage, plan["plan_id"])
    for entry in plan["batches"]:
        if entry["state"] != "done":  # a halved parent holds no part of its own
            continue
        result = read_part(part_path(out, stage, plan["plan_id"], entry["batch_id"], entry["attempt"]), out,
                           plan["plan_id"], entry["batch_id"], stage, plan["agent_type"], entry["finding_ids"])
        if result.state != "done":
            raise StageFailure(1 if result.state == "missing" else 2, stage,
                               "the part of batch %s is %s (%s)" % (entry["batch_id"], result.state, result.detail),
                               "re-run the command: only a part that validates counts",
                               batch=(entry["batch_id"], ", ".join(entry["finding_ids"])), kept=kept)
        for item in result.part["items"]:
            items[item["finding_id"]] = item
        for finding_id, found in result.flags.items():
            flags.setdefault(finding_id, []).extend(found)
        for key in counts:
            counts[key] += result.counts.get(key, 0)
    return items, flags, counts


class RunCore(object):
    """What every renderer's run holds, whichever its stage: the fields that both renderers declare alike, which an entry's own ``Run`` extends.

    ``warnings`` and ``issues`` are the stage record's warnings and the Input Issues, ``sources`` and ``counts`` the input digest's sources and the part
    reader's counts, and the rest is the threat model's bookkeeping: its text, its file, the findings' layers, the components and their zones, the
    reference set's rows and correlation groups and the architecture URI. ``threats_path`` isn't here, because the renderers start it differently.
    """

    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.warnings: List[Dict[str, str]] = []
        self.issues: List[str] = []
        self.sources: Dict[str, str] = {}
        self.counts: Dict[str, int] = {"narrative_fallbacks": 0, "truncations": 0}
        self.rows: List[Any] = []
        self.groups: List[Dict[str, Any]] = []
        self.assignments: Dict[str, Any] = {}
        self.open_ids: set = set()
        self.threats_text: Optional[str] = None
        self.finding_layer: Dict[str, str] = {}
        self.component_info: Dict[str, Tuple[str, str]] = {}
        self.component_zone: Dict[str, str] = {}
        self.source_file: Optional[str] = None
        self.uri = ""

    def warn(self, code: str, detail: str) -> None:
        self.warnings.append(record_warning(code, detail))


def stage_and_move(stage: str, out: str, plan_id: str, files: Mapping[str, str], check: Callable[[Dict[str, str]], List[str]], kept: str,
                   reason_text: Optional[Callable[[Optional[str]], str]] = None) -> None:
    """Write each file to ``staged/``, read it back, check it, and only then move each onto its canonical name (D4 steps 5 and 6; KB 22).

    ``files`` maps each canonical name to its text, in the order the files move. Each staged file takes the permission bits of the canonical file it
    will replace (P1-2), and a ``staged`` that is a link or not a directory stops the write with exit 2. The files are read back from disk, through
    no link and at most ``MAX_AGENT_INPUT_BYTES``, as strict UTF-8, and ``check`` gets the read-back texts by name and returns the problems that it
    found. Any problem stops with exit 4 before a canonical file is touched, and so does a failed write, read or move. ``reason_text`` words a read
    failure's reason (``RENDERER_READ_REASONS``' vocabulary) for the message, and is the reason itself when it is ``None``.
    """
    staged_dir = plan_subdir(out, stage, plan_id, "staged")
    try:
        if os.path.islink(staged_dir) or (os.path.lexists(staged_dir) and not os.path.isdir(staged_dir)):
            raise StageFailure(2, stage, "staged is a symbolic link or not a directory", "remove it and re-run", kept=kept)
        os.makedirs(staged_dir, exist_ok=True)
        for name, text in files.items():   # each staged file takes the permission bits of the canonical file it will replace (P1-2)
            atomic_write(staged_path(out, stage, plan_id, name), text, mode_of=os.path.join(out, name))
    except OSError as exc:
        raise StageFailure(4, stage, "the staged files could not be written (%s)" % (exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None
    texts: Dict[str, str] = {}
    for name in files:
        raw, reason = read_capped(staged_path(out, stage, plan_id, name), MAX_AGENT_INPUT_BYTES, RENDERER_READ_REASONS)
        if raw is None:
            raise StageFailure(4, stage, "the staged %s could not be read back (%s)" % (name, reason if reason_text is None else reason_text(reason)),
                               RETRY_REMEDY, kept=kept)
        try:
            texts[name] = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise StageFailure(4, stage, "the staged %s is not strict UTF-8" % name, RETRY_REMEDY, kept=kept) from None
    problems = check(texts)
    if problems:
        raise StageFailure(4, stage, "a completeness or parity check failed on the staged files: %s%s" % (
            "; ".join(problems[:5]), "; and %d more" % (len(problems) - 5) if len(problems) > 5 else ""), RETRY_REMEDY, kept=kept)
    for name in files:
        try:
            os.replace(staged_path(out, stage, plan_id, name), os.path.join(out, name))
        except OSError as exc:
            raise StageFailure(4, stage, "the move of %s onto its canonical name failed (%s)" % (name, exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None


def walk_out(out: str) -> Iterable[Tuple[str, int, int]]:
    """``(relative path, size, mtime_ns)`` for every file under ``out``, in a fixed order. Links to directories aren't followed."""
    for directory, subdirs, files in os.walk(out):
        subdirs.sort()
        for name in sorted(files):
            path = os.path.join(directory, name)
            try:
                status = os.lstat(path)
            except OSError:  # pragma: no cover  (a file removed while the walk runs)
                continue
            yield os.path.relpath(path, out).replace(os.sep, "/"), status.st_size, max(0, status.st_mtime_ns)


def undeclared_paths(stage: str, out: str, plan: Mapping[str, Any]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Paths new or changed since the plan that the stage's grammar doesn't declare (D4), sorted and capped: ``(paths, warnings)``.

    A file is looked up in the plan's ``out_snapshot`` by ``snapshot_key``, so a name that no plan holds is found (EC-2). A path that a record can't
    hold is left out of the list and counted in ``undeclared-paths-unrecordable``, and a list cut at ``MAX_UNDECLARED_PATHS`` adds
    ``undeclared-paths-truncated`` with the full count. A plan with no snapshot skips the check, with ``declared-paths-skipped``.
    """
    snapshot = plan["out_snapshot"]
    if snapshot is None:
        return [], [record_warning("declared-paths-skipped", "the plan took no snapshot of the output directory")]
    found = sorted(relpath for relpath, size, mtime in walk_out(out)   # a file is looked up by the planner's key for it, so a name that no plan holds is found (EC-2)
                   if snapshot.get(snapshot_key(relpath)) != [size, mtime] and not is_declared_path(relpath, stage, plan["plan_id"]))
    recordable = [relpath for relpath in found if path_problem(relpath) is None]
    warnings = []
    if len(recordable) != len(found):
        warnings.append(record_warning("undeclared-paths-unrecordable", "%d undeclared paths have names a record can't hold" % (len(found) - len(recordable))))
    if len(recordable) > MAX_UNDECLARED_PATHS:
        warnings.append(record_warning("undeclared-paths-truncated", "%d undeclared paths in all; the first %d are listed" % (len(recordable), MAX_UNDECLARED_PATHS)))
    return recordable[:MAX_UNDECLARED_PATHS], warnings


def output_entries(out: str, names: Iterable[str]) -> List[Dict[str, str]]:
    """A stage record's ``outputs`` for files that sit in ``out`` under their canonical names: each ``path`` with its SHA-256."""
    return [{"path": name, "sha256": file_digest(os.path.join(out, name))} for name in names]


def stage_record(stage: str, out: str, plan: Mapping[str, Any], digest: str, counts: Dict[str, int], outputs: List[Dict[str, str]],
                 warnings: List[Dict[str, str]], undeclared: List[str], status: Optional[str] = None,
                 error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """A ``tachi.stage-record/1`` object for ``plan``: the batch summary, the overflow events and retries and the finish time are derived here.

    ``status`` is given by the caller, and ``None`` reads ``success-with-warnings`` when there are warnings or undeclared paths and ``success``
    otherwise, the renderers' rule. ``error`` is ``None`` for a stage that finished. Nothing is validated or written: ``write_stage_record`` does that
    for a renderer, and a caller that ends a stage another way (``tachi-stage.py fail``) writes the record itself.
    """
    events, retries = retry_history(stage, out, dict(plan))
    batches = plan["batches"]
    return {
        "schema": STAGE_RECORD_SCHEMA, "stage": stage, "plan_id": plan["plan_id"],
        "status": status if status is not None else "success-with-warnings" if warnings or undeclared else "success", "tachi_version": VERSION,
        "started_utc": plan["created_utc"], "finished_utc": utc_now(), "input_digest": digest, "counts": counts,
        "batches": {"planned": sum(1 for e in batches if e["parent"] is None),
                    "dispatched": sum(1 for e in batches if e["parent"] is None) + plan["retry_budget"]["used"],
                    "done": sum(1 for e in batches if e["state"] == "done"), "retried": plan["retry_budget"]["used"],
                    "split": sum(1 for e in batches if e["state"] == "split"), "exhausted": sum(1 for e in batches if e["state"] == "failed")},
        "overflow_events": events, "retries": retries, "warnings": warnings, "undeclared_paths": undeclared,
        "outputs": outputs, "error": error,
    }


def write_stage_record(stage: str, renderer: str, out: str, plan: Mapping[str, Any], digest: str, counts: Dict[str, int],
                       outputs: List[Dict[str, str]], warnings: List[Dict[str, str]], undeclared: List[str], kept: str,
                       status: Optional[str] = None, error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a stage record (``stage_record``), check it against its own validator and its size cap, and write it to the plan directory; returns it.

    A renderer's end of run, with D4's exit 4 for a record that fails its own contract (the message says to report a bug in ``renderer``, the entry's
    installed file name) and for one that can't be written. The record is checked before it is written, so a stage never leaves a record that its
    readers would refuse.
    """
    record = stage_record(stage, out, plan, digest, counts, outputs, warnings, undeclared, status, error)
    try:
        validate_stage_record(record)
        text = dump_json(record)
        if len(text) > MAX_DOCUMENT_BYTES[STAGE_RECORD_SCHEMA]:
            raise PartError("invalid", "the record is over its size cap")
        atomic_write(stage_record_path(out, stage, plan["plan_id"]), text)
    except PartError as exc:
        raise StageFailure(4, stage, "the stage record this step wrote fails its own contract (%s)" % exc.detail,
                           "report this as a bug in %s" % renderer, kept=kept) from None
    except OSError as exc:
        raise StageFailure(4, stage, "the stage record could not be written (%s)" % (exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None
    return record


def build_parser(renderer: str, description: str, out: bool = True, plan: bool = True) -> argparse.ArgumentParser:
    """An entry's argument parser with the arguments that entries share: ``--version`` (the entry's name, ``VERSION`` and the interpreter's), then
    ``--out`` and ``--plan`` with ``--plan-digest``, each required and each left out when its flag is false. The entry adds its own."""
    parser = argparse.ArgumentParser(prog=renderer, description=description)
    parser.add_argument("--version", action="version", version="%s %s (python %s)" % (renderer, VERSION, platform.python_version()))
    if out:
        parser.add_argument("--out", required=True, help="the run's output directory; everything is written under it")
    if plan:
        parser.add_argument("--plan", required=True, help="the plan ID that plan printed")
        parser.add_argument("--plan-digest", required=True, help="the plan_digest that the last plan or reconcile printed")
    return parser


def plan_arguments(stage: str, plan_id: object, digest: object) -> None:
    """D3's allow-lists for ``--plan`` and ``--plan-digest``, as ASCII full matches, before either becomes a path or is compared: exit 2, ``--plan`` first.

    A value that isn't a ``str`` is refused the same way, so a library caller that passes the wrong type gets D4's message and never a ``TypeError``.
    """
    if not id_matches("plan", plan_id):
        raise StageFailure(2, stage, "--plan is not a plan ID", "pass the plan ID that plan printed")
    if not isinstance(digest, str) or _HEX64.fullmatch(digest) is None:
        raise StageFailure(2, stage, "--plan-digest is not a SHA-256 in lowercase hex", "pass the digest that the last plan or reconcile printed")


def entry_arguments(stage: str, out: object, plan_id: object, digest: object) -> str:
    """The checks that an entry with ``--out``, ``--plan`` and ``--plan-digest`` runs before it reads anything, in this order, so the first to fail is the one
    reported: ``--out`` is a directory (exit 1, D4's "an input is missing"), then ``plan_arguments``'s two (exit 2). Returns ``--out`` as an absolute path.

    This is both renderers' form, and the form for a new entry. An entry whose ``--out`` has a check of its own calls ``plan_arguments`` after it
    (``tachi-stage.py`` vets the path, and names it in its message, before it checks a plan).
    """
    text = os.path.abspath(os.fspath(out))
    if not os.path.isdir(text):
        raise StageFailure(1, stage, "--out is not a directory", "create it or correct --out")
    plan_arguments(stage, plan_id, digest)
    return text


def entry_defect(stage: str, renderer: str, exc: Exception, kept: Optional[str]) -> StageFailure:
    """An exception that no check meant to raise is a bug in the entry (or a hostile input it didn't expect): name it, with exit 4."""
    frame = exc.__traceback__
    while frame is not None and frame.tb_next is not None:
        frame = frame.tb_next
    where = "%s:%d" % (os.path.basename(frame.tb_frame.f_code.co_filename), frame.tb_lineno) if frame is not None else "unknown"
    detail = "".join(char if char.isprintable() else " " for char in str(exc))[:200]
    return StageFailure(4, stage, "an unexpected error stopped the render (%s: %s, at %s)" % (type(exc).__name__, detail, where),
                        "report this as a bug in %s; the earlier outputs were left or put back as they were" % renderer, kept=kept)


def run_entry(stage: Optional[str], renderer: str, args: argparse.Namespace, run: Callable[[argparse.Namespace], int], defect: bool = True) -> int:
    """``run(args)`` with D4's failure handling, for an entry's ``main``: its exit code, or the code of the ``StageFailure`` that stopped it.

    A ``StageFailure`` prints its four-line message on stderr and returns its code. With ``defect`` (the default), any other exception prints the same
    message as an unexpected error (``entry_defect``) with exit 4, so the command's Step F runs on a defect too, and the plan directory is kept when
    ``args`` names a plan. Without it, such an exception is raised again, as in ``tachi-stage.py``.
    """
    try:
        return run(args)
    except StageFailure as exc:
        sys.stderr.write(exc.text() + "\n")
        return exc.code
    except Exception as exc:
        if not defect:
            raise
        out, plan_id = getattr(args, "out", None), getattr(args, "plan", None)
        kept = plan_dir(os.path.abspath(out), stage, plan_id) if out is not None and id_matches("plan", plan_id) else None
        failure = entry_defect(stage, renderer, exc, kept)
        sys.stderr.write(failure.text() + "\n")
        return failure.code
