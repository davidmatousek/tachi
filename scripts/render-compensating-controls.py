#!/usr/bin/env python3
"""Render ``compensating-controls.md`` from the control analyzer's part files (F-374; ADR-050 D1, D2, D4, D5).

The control analyzer writes judgment only: for each scored finding, whether a control was found, partial or missing,
its category, the code evidence, an optional effectiveness assessment, its own Section 2 row and the recommendation for
a gap. This script computes everything else and writes the whole file, so that no score, band, total, percentage or
count in it is a model's. It runs once, in the main session, after ``tachi-stage.py reconcile`` exits 0:

    python3 scripts/render-compensating-controls.py --out DIR --plan ID --plan-digest HEX

The order is D4's. It checks the plan (its digest, the pointer, every input and batch input), re-validates every part it
reads, refuses a value that it takes from ``threats.md`` or the scored input if the value holds a character that D3's
step 10 forbids, computes the rows, and writes the file to ``<plan_id>/staged/``. It reads the staged file back from
disk and checks it: the rows against the member set, Section 2's arithmetic, Section 1's and Section 5's totals against
the sums of the rows, and that the reader the next run uses (``parse_controls_assessment_inputs``) reads every finding's
persisted result back as it was written. Only when every check passes does it move the staged file onto its canonical
name with ``os.replace``. It then runs the declared-paths check and writes the stage record. A check that fails leaves
the canonical files untouched.

**What is computed here (ADR-050 D2, D5).** The inherent score of each finding is its Composite cell in this run's
``risk-scores.md``, read through D9's reader and never re-scored, and its band is ``band(inherent)``. The P0 effectiveness
and the reduction factor follow from the agent's status, and the residual score and its band follow from both, by
``q1`` (half up, so 4.55 is 4.6). ``CF``, ``carry_forward_count`` and ``rescan_scope`` follow from the agent's
``carried_forward`` once the renderer has accepted it: only for an UNCHANGED finding whose result the resolved baseline
``compensating-controls.md`` holds (otherwise it is cleared, and the reason is recorded). Which findings are scored is
the input's open rows (D8), and the text of each comes from the ``threats.md`` that the planner reached through the input's
validated ``source_file`` and holds as a plan input. When ``risk-scores.md`` is absent the plan reads ``risk-scores.sarif`` instead, and the member set and the scores
come from it (``parse_sarif_member_set``, D8's fallback).

**Sections.** The file is schema 1.1: Sections 1 to 7, ending in the provenance stamp. Section 7 holds the input issues,
each finding's flags, and ``### Assessment Inputs``, the single ID, Field and Value table of ``contracts/module-signatures.md``
that persists each finding's whole controls item, escaped on write, for the next run to carry (RR1, AR-T3). Its
``matrix_row`` is persisted canonically, rebuilt from the agent's 11 cells (the four computed cells as their slot tokens,
``CF`` as Section 2 shows it, every other cell as the agent wrote it).

**The SARIF (T053; ADR-050 D7, D8).** ``compensating-controls.sarif`` is written through the shared emitter
(``sarif_common``), one result for each scored open finding, in Section 2's order. A correlated peer is a result like any
other, with the ``correlation-*`` properties and ruling C's sentence; ``relatedLocations`` hold the finding's code evidence
that the resolver accepted, and nothing else. Correlation comes from Section 4a of the ``threats.md`` that the scored input's
validated ``source_file`` names (in D8's fallback, from the properties of ``risk-scores.sarif``). When that file can't be read
there is no correlation, the stage record says why, and no key changes, because correlation is never identity. ``recommendation`` and
``effort-estimate`` are read from the rendered Section 4 blocks: each block is found in the Section 4 that sits outside the code
fences, and its "What to Implement" text is read by the shared rule (``tachi_parsers.recommendation_text``, which is
``parse_compensating_controls_md``'s), so a consumer of either file reads one text. The from-disk check derives ``recommendation``
again from each validated part body instead of from the file, so a defect of the reader that built the SARIF can't agree with
itself (T067b H1). ``integrity-flags`` carries ``reused-id`` over from the input, and ``maestro-layer`` is the
value that the scorer's file holds for the finding. The result's properties are the contracted set and no other key
(``contracts/sarif-result.md``). Both files are written to ``staged/`` and checked on disk, against each other as well as
against the rows, before either replaces a canonical name.

**Sections 2 and 4 under R-34 (T059; ADR-050 D2).** The agent writes its own Section 2 row (``matrix_row``, 11 cells in K8's
order) and the body of each Section 4 block, and the renderer fills what is computed and checks what is not.
- Section 2. The band tables (by residual band, an empty band left out), the K8 header and the row order are the renderer's. The four
  computed cells are overwritten by column position, and each one that held anything but its own slot token is counted once, in the
  stage record's ``cell_overwrites`` (an eighth base count, ruled at W3, always written, ``0`` included, and never a flag). ``CF`` is
  filled from the accepted ``carried_forward`` and is never counted. The Control Status,
  Control Category, Component and MAESTRO Layer cells are the agent's text: each is checked against the structured value, and a cell
  that disagrees is flagged ``input:<field>:sources-disagree`` and never rejected, because the SARIF and every total follow the
  structured value. The Threat cell is model text, escaped and nothing more.
- Section 4. The group (the band of the inherent score), the block order, the numbers, the heading and the ``Current Status`` line are
  the renderer's. The body is the agent's text and is written as it is.
- The structure is the part validator's (D3 step 9, ``tachi_parts.read_part``): a row that isn't 11 cells or whose Threat ID isn't the
  finding's, and a body that lacks one of its four keys or has them out of order, an Effort that doesn't start with ``Low``, ``Medium``
  or ``High``, or a heading or table line, reject the item, and ``reconcile`` re-dispatches the batch. This script runs ``read_part``
  again on every part it reads, so a part that fails it never reaches a row: the render stops with exit 2 and writes nothing.

**An evidence file that the resolver refuses (ADR-050 D2, ruled at W3).** The part checked only the syntax of each evidence ``file``, so the
resolver can still refuse one at render time: it is missing, a link or not a regular file. That is flagged and never refused, because the
control analyzer copies an UNCHANGED finding's evidence verbatim, so a refusal would recur on every baseline-aware run and no re-run could
clear it. The entry stays in Section 3, in ``control-evidence`` and in Section 7 with its ``file`` as written, because it has no canonical
spelling, and the SARIF's ``relatedLocations`` leave it out (a result left with none has no key). The finding is flagged
``input:evidence.file:unresolved`` once, Section 1's warning lines name it, Section 7 lists each failed entry with the resolver's check,
and the stage record warns ``evidence-file-unresolved``, so the run exits 5. The status and every computed value follow the part.

Exit codes are ``contracts/cli.md``'s: 0 done, 1 an input is missing or unreadable, 2 a validation, usage or guard
failure (a digest or pointer mismatch, a part that fails re-validation, a forbidden character in an input), 4 a
completeness or parity check failed or a file could not be written, 5 done with warnings. A failure prints D4's
four-line message on stderr and writes nothing but what is already staged; ``tachi-stage.py fail`` writes the failed
record and puts earlier outputs back. The summary lines on stdout are the command's Step 6, so the model restates no
number.

Nothing here reads the clock except the stage record's ``finished_utc``, and the date is the plan's. The renderer never
rewrites ``plan.json``. Standard library plus the shared helpers, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("render-compensating-controls.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import datetime
import json
import os
import platform
import re
import stat
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import sarif_common as sc  # noqa: E402
import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402
import tachi_scoring as ts  # noqa: E402
import tachi_scoring_rules as rules  # noqa: E402

STAGE = "compensating-controls"
RENDERER = "render-compensating-controls.py"  # the stamp's name: the installed file name, as a literal (contracts/cli.md)
MD, SARIF = "compensating-controls.md", "compensating-controls.sarif"
TOOL = sc.TOOL_NAMES[SARIF]   # tachi-control-analyzer, verbatim: the tool name is a hash input (D7)
RISK_SCORES_SARIF = "risk-scores.sarif"
SCHEMA_VERSION = "1.1"
DASH = "—"
RETRY_REMEDY = "re-run the command; the earlier outputs were left or put back as they were"

# Section 3's Threat cell is cut here before it is escaped. Section 2's is the agent's own, which cuts it at 80 (control-analyzer.md).
THREAT_WIDTH = 80
# The finding IDs that a list in the rendered markdown names before "and N more": Section 5's Examples cell, Section 1's warning lines and
# Section 7's Input Issues alike. It is ``sarif_common.PEER_CAP``, the cap of ruling C's sentence, so that one convention holds across both
# rendered markdown files (ADR-050 D2, ruled at W3, 2026-11-23).
EXAMPLE_CAP = sc.PEER_CAP

# Section 2's header: K8's order, which the part's ``matrix_row`` follows cell by cell (contracts/module-signatures.md).
K8_HEADER = ("Threat ID", "CF", "Component", "MAESTRO Layer", "Threat", "Inherent Score", "Inherent Severity", "Control Status",
             "Control Category", "Residual Score", "Residual Severity")
CELL_COUNT = len(K8_HEADER)
CF_CELL = 1
# The four computed cells, by position, and the one slot token each holds in a ``matrix_row`` (ADR-050 D2, R-34). The renderer fills
# them, and counts each one that holds anything else as an overwrite.
COMPUTED_CELLS = {5: "{{score:inherent}}", 6: "{{band:inherent}}", 9: "{{score:residual}}", 10: "{{band:residual}}"}
# The four cells that are checked, never filled, in PR 1 (R-34): the agent's cell stays in Section 2 as it wrote it, a cell that
# disagrees with the structured result or the input is flagged ``input:<field>:sources-disagree`` (the scorer's cause for two sources
# that differ), and the SARIF and every total follow the structured value. FR-K8.1's follow-up turns each check into a fill.
SOURCES_DISAGREE = "sources-disagree"
CHECKED_CELLS = {"control_status": 7, "control_category": 8, "component": 2, "maestro_layer": 3}   # the flag's field -> its column of K8's header

# The Effort line of a Section 4 body, and its word. The body is the agent's text, which the part validator has checked and the
# renderer never rewrites (R-34): the four keys once each and in order, an Effort that starts with a level, no heading or table line.
EFFORT_MARKER = "**%s**:" % tp.RECOMMENDATION_KEYS[-1]
EFFORT_WORD = re.compile(r"(%s)(?!\w)" % "|".join(tp.EFFORT_LEVELS))

# Section 3's order of categories (the template's): (enum value, display name, the token of a control's ID).
CATEGORIES = (
    ("authentication", "Authentication", "AUTH"), ("access-control", "Access Control", "ACCESS"),
    ("input-validation", "Input Validation", "INPUT"), ("encryption", "Encryption", "ENC"),
    ("rate-limiting", "Rate Limiting", "RATE"), ("logging-audit", "Logging/Audit", "LOG"),
    ("csrf-protection", "CSRF Protection", "CSRF"), ("csp-security-headers", "CSP/Security Headers", "CSP"))
CATEGORY_NAME = {value: name for value, name, _token in CATEGORIES}

STATUS_CELL = {"found": "Control Found", "partial": "Partial Control", "missing": "No Control Found"}
EFFECTIVENESS = {"found": "strong", "partial": "moderate", "missing": "none"}  # the P0 effectiveness that each status implies
FACTOR_WORDS = {"found": "Control detected with evidence.", "partial": "Control exists but its coverage is incomplete.",
                "missing": "No matching control detected."}
STATUS_OF_CLASS = {"found": "found", "partial": "partial", "none": "missing"}  # ``classify_control_status``'s names -> ours

SECTION_TITLES = ("## 1. Executive Summary", "## 2. Coverage Matrix", "## 3. Control Details", "## 4. Recommendations",
                  "## 5. Residual Risk Summary", "## 6. Methodology", "## 7. Analysis Integrity")
BANDS = tuple(ts.SEVERITY_BANDS)
SHIFTS = (("Critical", "High"), ("Critical", "Medium"), ("Critical", "Low"), ("High", "Medium"), ("High", "Low"), ("Medium", "Low"))
# Section 4's groups, by the finding's inherent band: (heading, the bands it holds).
GAP_GROUPS = (("### Critical / High Risk Gaps", ("Critical", "High")), ("### Medium Risk Gaps", ("Medium",)), ("### Low Risk Gaps", ("Low",)))
GROUP_OF_BAND = {band: heading for heading, bands in GAP_GROUPS for band in bands}
GROUP_HEADINGS = tuple(heading for heading, _bands in GAP_GROUPS)

# The kinds of a flag, in the fixed order that Section 7 lists them (the scorer's closed vocabulary, ADR-050 D9).
FLAG_KINDS = ("corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input")

_LAYER = re.compile(r"L[1-7](?![0-9])", re.ASCII)

# The SARIF's logical location (ADR-050 D7): the zone of a component that no Section 2 row lists, and the DFD kind of each Section 1
# type, as render-risk-scores.py writes them. D8's fallback reads a kind back from ``risk-scores.sarif``, and ``threats.sarif``
# writes ``data-store`` where the scorer writes ``data``, so both name a data store.
DEFAULT_ZONE = "Application Zone"
DEFAULT_KIND = "process"
KIND_OF_DFD_TYPE = {"External Entity": "external-entity", "Process": "process", "Data Store": "data"}
KIND_SPELLINGS = {"external-entity": "external-entity", "process": "process", "data": "data", "data-store": "data"}
REUSED_FLAG = "reused-id:finding_id:baseline"   # ruling B (D7): the scored input's flag, carried over to ``integrity-flags``
# Ruling C's sentence at the end of a text, in the forms that ``sarif_common.correlation_sentence`` writes. The scorer's SARIF has
# it on a correlated result's message, so D8's fallback takes it off the member's text before this file writes its own.
_CORRELATION_TAIL = re.compile(r" Correlated in CG-[0-9]{1,6}; (?:primary [A-Za-z]+-[0-9]+"
                               r"|peers [A-Za-z]+-[0-9]+(?:, [A-Za-z]+-[0-9]+)*(?: and [0-9]+ more)?)\.\Z")

# The rules of compensating-controls.sarif are ``sarif_common.RULES``, the one table that both renderers write from, and
# ``sarif_common.build_rules`` writes them, ``relationships`` included (PM W3 ruling 2, gap A). A ``{{ref:...}}`` slot may cite the
# taxonomy IDs of the finding's rule (ADR-050 D3's table), which is entry 4 of its row.
RULE_BY_CATEGORY = {entry[0]: entry for entry in sc.RULES}


# =============================================================================
# Failure: D4's four-line message
# =============================================================================

class RenderError(Exception):
    """A stop with an exit code and D4's four-line message."""

    def __init__(self, code: int, reason: str, remedy: str = "", batch: Optional[Tuple[str, str]] = None,
                 kept: Optional[str] = None) -> None:
        super().__init__(reason)
        self.code, self.reason, self.remedy, self.batch, self.kept = code, reason, remedy, batch, kept

    def text(self) -> str:
        lines = ["TACHI COMPENSATING-CONTROLS FAILED: %s" % self.reason]
        if self.batch:
            lines.append("Batch %s: %s" % self.batch)
        if self.remedy:
            lines.append("Remedy: %s" % self.remedy)
        if self.kept:
            lines.append("Kept for diagnosis: %s" % self.kept)
        return "\n".join(lines)


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(obj: Any) -> str:
    """Stable JSON for a record: sorted keys, two-space indent, ASCII escapes, one trailing newline."""
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def _warning(code: str, detail: str) -> Dict[str, str]:
    """One stage-record warning, its code and detail made safe for the record's rules, the detail cut at 500."""
    return {"code": code[:64], "detail": "".join(char if char.isprintable() else " " for char in detail)[:500]}


def _shorten(text: str, limit: int) -> str:
    """output-formatting.md's rule: over ``limit`` characters, keep ``limit - 3`` and add three dots."""
    return text if len(text) <= limit else text[:limit - 3] + "..."


def _one(value: Decimal) -> str:
    """A score as text with exactly one decimal place."""
    return str(ts.q1(value))


def _signed(number: int) -> str:
    """A change of a count: ``+3``, ``-3`` or ``0``."""
    return "%+d" % number if number else "0"


def _named(names: Sequence[str]) -> str:
    """The first ``EXAMPLE_CAP`` names and then ``and N more``, with N exact: the one form of a list of finding IDs in this file, in Section 1,
    Section 5, Section 7's Input Issues, the stage record's warning for an evidence file and a check's message. There is no tail at the cap or below."""
    return ", ".join(names[:EXAMPLE_CAP]) + (" and %d more" % (len(names) - EXAMPLE_CAP) if len(names) > EXAMPLE_CAP else "")


# =============================================================================
# The plan: checked, never trusted (ADR-050 D3)
# =============================================================================

def _document(path: str, out: str, schema: str, what: str, kept: Optional[str] = None) -> Dict[str, Any]:
    """``tachi_parts.read_document`` with D4's exit codes: 1 for a missing file, 2 for anything the contract refuses."""
    try:
        return tp.read_document(path, out, schema)
    except tp.PartError as exc:
        if exc.kind == "missing":
            raise RenderError(1, "%s is missing" % what, "re-run the plan step", kept=kept) from None
        raise RenderError(2, "%s is not acceptable (%s)" % (what, exc.detail), "re-run the command", kept=kept) from None


def _read_plan_input(entry: Mapping[str, Any], name: str, kept: str) -> bytes:
    """A digest-checked plan input's bytes. A file that changed or vanished since plan is exit 2, as in ``reconcile``."""
    try:
        with open(entry["path"], "rb") as handle:
            raw = handle.read(tp.MAX_AGENT_INPUT_BYTES + 1)
    except OSError:
        raw = None
    if raw is None or len(raw) > tp.MAX_AGENT_INPUT_BYTES or tp.sha256_hex(raw) != entry["sha256"]:
        raise RenderError(2, "the input %s changed (or vanished) since plan" % name, "re-run the command", kept=kept)
    return raw


def _load_plan(out: str, plan_id: str, digest: str) -> Tuple[Dict[str, Any], Dict[str, bytes], Dict[str, str]]:
    """The plan ``--plan`` names, once the pointer, its digest, its inputs and every batch input check out.

    Returns ``(plan, the bytes of each plan input, the plan's refs)``. The refs are the plan's own, so a plan with no
    units keeps its pointers (ruled at W2, part-files.md section 4). Nothing is written.
    """
    kept = tp.plan_dir(out, STAGE, plan_id)
    pointer = _document(tp.pointer_path(out, STAGE), out, tp.POINTER_SCHEMA, "the plan pointer")
    if pointer["plan_id"] != plan_id:
        raise RenderError(2, "--plan %s disagrees with current.json, which names %s" % (plan_id, pointer["plan_id"]),
                          "pass the plan ID that plan printed", kept=kept)
    path = tp.plan_path(out, STAGE, plan_id)
    problem = tp.path_guard_problem(path, out)
    if problem == "missing":
        raise RenderError(1, "plan.json is missing", "re-run the plan step", kept=kept)
    if problem is not None:
        raise RenderError(2, "plan.json failed the path guard (%s)" % problem, "re-run the command", kept=kept)
    if tp.file_digest(path) != digest:
        raise RenderError(2, "the plan file's digest differs from --plan-digest",
                          "pass the digest that the last plan or reconcile printed; if the plan was edited, re-run the command", kept=kept)
    plan = _document(path, out, tp.PLAN_SCHEMA, "plan.json", kept)
    if (plan["plan_id"], plan["stage"]) != (plan_id, STAGE):
        raise RenderError(2, "plan.json is for another plan or stage", "re-run the command", kept=kept)
    unfinished = [entry for entry in plan["batches"] if entry["state"] in ("pending", "failed")]
    if unfinished:
        first = unfinished[0]
        raise RenderError(2, "batch %s is %s, so the plan is not complete" % (first["batch_id"], first["state"]),
                          "run reconcile until it exits 0, then render", batch=(first["batch_id"], ", ".join(first["finding_ids"])), kept=kept)
    inputs = {name: _read_plan_input(entry, name, kept) for name, entry in sorted(plan["inputs"].items())}
    for entry in plan["batches"]:
        stored = tp.input_path(out, STAGE, plan_id, entry["batch_id"])
        if tp.path_guard_problem(stored, out) is not None or tp.file_digest(stored) != entry["input_sha256"]:
            raise RenderError(2, "the batch input %s changed after plan" % entry["batch_id"], "re-run the command", kept=kept)
    return plan, inputs, dict(plan["refs"])


def _read_parts(out: str, plan: Mapping[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]], Dict[str, int]]:
    """Every done batch's part, re-validated against the plan: ``(items by canonical ID, flags by ID, counts)``.

    Only the current plan's parts at each batch's current attempt count, so an earlier plan's part or an earlier
    attempt never does. A part that no longer validates is a failure that names its batch.
    """
    items: Dict[str, Dict[str, Any]] = {}
    flags: Dict[str, List[str]] = {}
    counts = {"narrative_fallbacks": 0, "truncations": 0}
    kept = tp.plan_dir(out, STAGE, plan["plan_id"])
    for entry in plan["batches"]:
        if entry["state"] != "done":  # a halved parent holds no part of its own
            continue
        result = tp.read_part(tp.part_path(out, STAGE, plan["plan_id"], entry["batch_id"], entry["attempt"]), out,
                              plan["plan_id"], entry["batch_id"], STAGE, plan["agent_type"], entry["finding_ids"])
        if result.state != "done":
            raise RenderError(1 if result.state == "missing" else 2,
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


# =============================================================================
# Rows, controls and flags
# =============================================================================

class Flag(object):
    """One integrity flag, ``kind:field:cause`` (the scorer's closed vocabulary, ADR-050 D9)."""

    def __init__(self, kind: str, field: str, cause: str) -> None:
        self.kind, self.field, self.cause = kind, field, cause

    def text(self) -> str:
        return "%s:%s:%s" % (self.kind, self.field, self.cause)


def _flag_from_text(text: str) -> Flag:
    kind, _, rest = text.partition(":")
    field, _, cause = rest.rpartition(":")
    return Flag(kind, field, cause)


def _sorted_flags(flags: Sequence[Flag]) -> List[Flag]:
    return sorted(flags, key=lambda flag: (FLAG_KINDS.index(flag.kind) if flag.kind in FLAG_KINDS else len(FLAG_KINDS), flag.field, flag.cause))


class Row(object):
    """One scored open finding, as rendered: the inputs' identity, the agent's judgment and the computed values."""

    def __init__(self, finding_id: str, component: str, threat: str, layer: str, delta: str, inherent: Decimal,
                 item: Mapping[str, Any], attribution: Tuple[str, ...] = ()) -> None:
        self.finding_id = finding_id                       # as Section 7 of threats.md spells it, which is how it is printed
        self.canon = tp.canonical_finding_id(finding_id)
        self.component, self.threat, self.layer, self.delta = component, threat, layer, delta
        self.attribution = attribution
        self.threat_category = ts.category_for_prefix(self.canon.partition("-")[0])   # the finding's rule: spoofing, tampering ...
        self.kind, self.zone, self.mitigation = DEFAULT_KIND, DEFAULT_ZONE, ""         # the SARIF's logical location and ``message.markdown``
        self.inherent = inherent                           # this run's risk-scores.md composite, never re-scored
        self.inherent_band = ts.band(inherent)
        self.item = item                                   # the validated part item
        self.control: str = item["control_status"]         # found, partial or missing
        self.control_category: str = item["control_category"]
        self.confidence: Optional[str] = item["confidence"]
        self.factor = ts.REDUCTION_FACTOR_P0[self.control]
        self.effectiveness = EFFECTIVENESS[self.control]
        self.residual = ts.residual_score(inherent, self.factor)
        self.residual_band = ts.band(self.residual)
        self.carried = False                               # the agent's carried_forward, once the renderer has accepted it
        self.paths: List[str] = []                         # each evidence entry's path as both rendered files print it: canonical where the resolver accepted the file, as written where it did not
        self.unresolved: List[Tuple[int, str, str]] = []   # ``(entry index, file as written, the resolver's check)`` for each evidence entry whose file it refused
        self.agent_cells: List[str] = []                   # the agent's matrix_row, split into its 11 cells
        self.overwritten = 0                               # how many of its four computed cells held anything but their slot token
        self.persisted: Dict[str, str] = {}                # narrative address -> the validated, slotted text that Section 7 carries
        self.cell_text: Dict[str, str] = {}                # narrative address -> the text resolved for a table cell
        self.flags: List[Flag] = []

    @property
    def cf(self) -> str:
        """Section 2's ``CF`` cell: the renderer's, from the accepted ``carried_forward`` (ruled at W3, never counted)."""
        return "CF" if self.carried else DASH

    @property
    def located(self) -> List[Tuple[int, Mapping[str, Any]]]:
        """``(entry index, entry)`` for each evidence entry whose file the resolver accepted: the entries that have a ``relatedLocations`` entry.

        The SARIF's ``id`` of a location is its entry's index, so it still names the entry's place in ``control-evidence`` when an earlier entry has none.
        """
        refused = {index for index, _file, _check in self.unresolved}
        return [(index, entry) for index, entry in enumerate(self.item["evidence"]) if index not in refused]

    @property
    def matrix_row(self) -> str:
        """What Section 7 persists as ``matrix_row``: the agent's row rebuilt from its 11 cells (module-signatures.md).

        The four computed cells hold their slot tokens, never the numbers Section 2 shows, ``CF`` holds the value that
        Section 2 shows, and every other cell is as the agent wrote it. So a carried row is copied, read and checked with
        no overwrite, whatever the first run's agent put in the computed cells.
        """
        cells = list(self.agent_cells)
        cells[CF_CELL] = self.cf
        for position, token in COMPUTED_CELLS.items():
            cells[position] = token
        return "| " + " | ".join(cells) + " |"


class Control(object):
    """One detected control: one distinct ``(category, file, line)`` that at least one finding cites (ADR-050 D2)."""

    def __init__(self, category: str, path: str, line: int, row: Row, index: int) -> None:
        self.category, self.path, self.line = category, path, line
        self.row, self.index = row, index                   # the first finding (S-2 order) that cites it, and its entry's place there
        self.members: List[Row] = [row]
        self.control_id = ""

    @property
    def status(self) -> str:
        """The strongest status among the findings it mitigates (a control that two findings judge differently is unruled)."""
        return "found" if any(member.control == "found" for member in self.members) else "partial"


class Run(object):
    """Everything one render reads and computes. Plain attributes, filled by ``_prepare`` and ``_score``."""

    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.warnings: List[Dict[str, str]] = []
        self.issues: List[str] = []
        self.sources: Dict[str, str] = {}
        self.counts: Dict[str, int] = {"narrative_fallbacks": 0, "truncations": 0}
        self.rows: List[Row] = []                           # S-2 order
        self.by_residual: List[Row] = []                    # residual descending, then S-2 (Section 2's order)
        self.recommended: List[Row] = []                    # partial and missing: inherent descending, then S-2 (Section 4's order)
        self.controls: List[Control] = []
        self.resolved_count = 0
        self.resolved_ids: List[str] = []                   # canonical IDs of the RESOLVED findings that an input lists: they appear nowhere in the SARIF
        self.groups: List[Dict[str, Any]] = []              # every correlation group, one with no ID (D8's fallback) included
        self.assignments: Dict[str, Any] = {}               # the emitter's roles, for the groups that have an ID only
        self.open_ids: set = set()
        self.threats_text: Optional[str] = None
        self.threats_path: Optional[str] = None
        self.finding_layer: Dict[str, str] = {}
        self.component_info: Dict[str, Tuple[str, str]] = {}
        self.component_zone: Dict[str, str] = {}            # a component's name, case-folded -> its Section 2 zone
        self.source_file: Optional[str] = None
        self.target: Optional[str] = None                   # the scanned directory, absolute (refs.target)
        self.target_path: Optional[str] = None              # ... and relative to the working directory, or None
        self.uri = ""                                       # the architecture file's URI: every SARIF result's one ``artifactLocation.uri`` (D7)
        self.baseline_resolved = False
        self.baseline_held: frozenset = frozenset()         # canonical IDs of the findings whose result the resolved baseline controls file holds (D2, W4)
        self.carry_forward_count: Optional[int] = None
        self.rescan_scope = "full"
        self.overwritten = 0                                # the computed cells of Section 2 that the renderer overwrote, over every row (R-34)
        self.inherent_total = self.residual_total = Decimal("0.0")
        self.evidence_cache: Dict[str, Any] = {}            # an evidence entry's ``file`` as written -> ``sc.resolve_file``'s answer (path and URI), for the files it accepted

    def warn(self, code: str, detail: str) -> None:
        self.warnings.append(_warning(code, detail))


# =============================================================================
# Forbidden characters in what an input holds (NFR-10, P0-4)
# =============================================================================

def _first_forbidden(value: Any, path: str = "") -> Optional[Tuple[str, str]]:
    """``(path, character)`` of the first string under ``value`` that holds a character D3's step 10 forbids, or ``None``.

    Text, mapping keys, list and tuple items and the fields of a plain object are searched in order. A number or
    ``None`` holds no text. ``path`` is dotted, and is for a message only. The character set is
    ``tachi_parts.forbidden_character``'s, so the parts, the inputs and the written files share one definition.
    """
    if isinstance(value, str):
        found = tp.forbidden_character(value)
        return (path, found) if found is not None else None
    if isinstance(value, Mapping):
        children = value.items()
    elif isinstance(value, (list, tuple)):
        children = enumerate(value)
    elif hasattr(value, "__dict__"):
        children = vars(value).items()
    else:
        return None
    for key, child in children:
        label = "%s.%s" % (path, key) if path else str(key)
        found = _first_forbidden(key, label) or _first_forbidden(child, label)   # a key is text too
        if found is not None:
            return found
    return None


def _refuse_forbidden(source: str, finding_id: Optional[str], value: Any, remedy: str, kept: str) -> None:
    """Exit 2 when ``value``, which the renderer takes from an input that isn't a part, holds a character that D3's step 10 forbids.

    Step 10 checks a part. Text from ``threats.md`` or the scored input reaches the escapers unchecked, and a carriage
    return, an escape or a bidi control would then forge a heading, drive a terminal or reorder what a reader sees
    (NFR-10, P0-4). So each value is checked where it is taken. ``finding_id`` names the finding the value belongs to,
    and ``None`` a component or layer name. The message gives the character's code point and never the text.
    """
    found = _first_forbidden(value)
    if found is not None:
        where = "the %s of %s" % (ascii(found[0])[1:-1], finding_id) if finding_id else "a component, zone or layer name"
        raise RenderError(2, "%s holds the character U+%04X, which the part contract forbids, in %s" % (source, ord(found[1]), where),
                          remedy, kept=kept)


# =============================================================================
# The inputs: the scored input, the threat model, the architecture file, the baseline
# =============================================================================

def _relative(path: str, cwd: str) -> Optional[str]:
    """``path`` relative to the working directory with ``/`` separators, or ``None`` when it isn't under it.

    The working directory is found by file identity, as ``under`` finds it, so a path that is spelled through a symbolic
    link (as macOS spells its temporary directory) still reads as the tail below the directory, never as a ``..`` climb.
    """
    if not tp.under(cwd, path):
        return None
    tail: List[str] = []
    current = os.path.abspath(path)
    while not (os.path.lexists(current) and os.path.samefile(current, cwd)):
        tail.append(os.path.basename(current))
        current = os.path.dirname(current)
    return "/".join(reversed(tail)) or "."


def _quoted(text: Optional[str]) -> str:
    """A YAML double-quoted scalar, or ``null`` for ``None`` or text that the frontmatter readers can't carry."""
    if text is None or any(char in text for char in '"\\') or not text.isprintable():
        return "null"
    return '"%s"' % text


def _read_text_file(path: str, limit: int = tp.MAX_AGENT_INPUT_BYTES) -> Tuple[Optional[bytes], Optional[str]]:
    """A regular file's bytes through no link, or ``(None, reason)``. The threat model and the staged files use it."""
    flags = os.O_RDONLY
    for name in ("O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):
        flags |= getattr(os, name, 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return None, "unreadable"
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return None, "not-a-regular-file"
        chunks, total = [], 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                return b"".join(chunks), None
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                return None, "too-large"
    except OSError:
        return None, "unreadable"
    finally:
        os.close(descriptor)


def _same_file(first: str, second: str) -> bool:
    try:
        return os.path.samefile(first, second)
    except OSError:
        return False


# The two frontmatter forms the other readers accept (``tachi_parsers.parse_frontmatter``): plain, and inside a ``yaml`` fence.
_FRONTMATTER = (re.compile(r"\A---[ \t\r]*\n(.*?)\n---", re.DOTALL), re.compile(r"```yaml[ \t\r]*\n---[ \t\r]*\n(.*?)\n---[ \t\r]*\n```", re.DOTALL))
_SOURCE_FILE_LINE = re.compile(r"^source_file[ \t]*:[ \t]*(?P<value>.*)$")


def _scored_source_file(text: str) -> Optional[str]:
    """The ``source_file`` of a ``risk-scores.md``'s frontmatter, or ``None``: the threat model that was scored (D7, D8).

    The planner's own reading (``tachi-stage.py``'s ``_scored_source_file``), so the two agree on what a file names. The first
    top-level ``source_file`` line of the frontmatter counts. A quoted value loses its quotes, and ``null``, ``~`` and an empty
    value mean none. What comes back is a candidate only: ``check_run_file`` validates it. The renderer needs it only to work
    out why the plan holds no threat model, because the plan has no slot for the reason.
    """
    text = text.lstrip("\ufeff")
    for pattern in _FRONTMATTER:
        found = pattern.search(text)
        if found is None:
            continue
        for line in found.group(1).split("\n"):
            match = _SOURCE_FILE_LINE.match(line.rstrip())
            if match is None:
                continue
            value = match.group("value").strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return None if value.strip() in ("", "null", "~") else value
        return None
    return None


def _delta_status(finding: Mapping[str, Any]) -> str:
    """A finding's delta status as the planner reads it: a row without a usable one counts as NEW."""
    status = tachi_parsers.normalize_delta_status(finding["delta_status"]) if isinstance(finding.get("delta_status"), str) else ""
    return status if status in ("NEW", "UPDATED", "UNCHANGED") else "NEW"


def _reused_ids(text: str) -> set:
    """The canonical IDs that the input ``risk-scores.md``'s Score Flags table marks ``reused-id`` (ruling B, D7).

    The controls renderer carries the flag over for the same finding. The heading is found as an exact line outside every code
    fence, so a threat or a rationale that quotes ``### Score Flags`` can't take the reader's place.
    """
    start = tachi_parsers.match_heading(r"^###[ \t]+Score Flags[ \t]*$", text, outside_fences=True)
    found: set = set()
    for row in tachi_parsers.parse_markdown_table(text, start_line=start, keep_bold=True) if start is not None else []:
        if (row.get("Flag"), row.get("Field"), row.get("Cause")) == ("reused-id", "finding_id", "baseline") and tp.id_matches("finding", row.get("ID", "")):
            found.add(tp.canonical_finding_id(row["ID"]))
    return found


def _valid_inherent(name: str, canonical: str, score: Optional[Decimal], kept: str) -> Decimal:
    """The inherent score of a member: a one-decimal score from 0.0 to 10.0 that the input holds, never re-scored."""
    try:
        if score is None:
            raise ValueError("no score")
        ts.band(score)
        return score
    except (ValueError, TypeError):
        raise RenderError(2, "the input %s holds no score from 0.0 to 10.0 on the 0.1 grid for %s, so its residual risk can't be computed" % (name, canonical),
                          "regenerate it with /tachi.risk-score", kept=kept) from None


def _members_from_markdown(run: Run, entry: Mapping[str, Any], raw: bytes, kept: str) -> List[Dict[str, Any]]:
    """The open rows of the input ``risk-scores.md``, through D9's reader (D8: this is the member set).

    A row that the reader can't use goes to Input Issues, so no finding drops out unseen (FR-K7.4). Each member's
    inherent score is its Composite cell.
    """
    name = os.path.basename(entry["path"])
    scores = rules.read_baseline_scores(Path(entry["path"]))
    for issue in scores.issues:
        run.issues.append("%s: %s" % (name, issue.detail))
    if not scores.readable:
        raise RenderError(2, "the input %s can't be read as scored findings (%s)" % (name, scores.reason), "regenerate it with /tachi.risk-score", kept=kept)
    if not scores.rows:
        raise RenderError(2, "the input %s lists no scored open finding" % name, "regenerate it with /tachi.risk-score", kept=kept)
    text = raw.decode("utf-8").lstrip("\ufeff")
    run.resolved_count = len(scores.resolved_rows)
    run.resolved_ids = list(scores.resolved_rows)
    reused = _reused_ids(text)
    members = []
    for canonical in sorted(scores.rows, key=tp.finding_sort_key):
        row = scores.rows[canonical]
        members.append({"id": canonical, "canon": canonical, "inherent": _valid_inherent(name, canonical, row.stored.get("composite"), kept),
                        "component": row.component or "", "threat": row.threat or "", "layer": "", "reused": canonical in reused})
        _refuse_forbidden(name, canonical, {"component": members[-1]["component"], "threat": members[-1]["threat"]},
                          "regenerate %s with /tachi.risk-score, or edit the value to remove the character, then re-run the command" % name, kept)
    return members


def _logical_location(result: Mapping[str, Any]) -> Mapping[str, Any]:
    """A result's logical location, in the order that ``tachi_parsers.parse_sarif_member_set`` reads it (its own helper stays private):
    ``locations[0].logicalLocations[0]``, else the singular ``locations[0].logicalLocation`` that tachi's older scorer and controls SARIF
    write (ADR-050 D8, ruled at W3, 7a), else ``{}``. It is one object either way, and a value that isn't an object doesn't count."""
    locations = result.get("locations")
    location = locations[0] if isinstance(locations, list) and locations else None
    if not isinstance(location, dict):
        return {}
    plural = location.get("logicalLocations")
    plural = plural[0] if isinstance(plural, list) and plural else None
    logical = plural if isinstance(plural, dict) else location.get("logicalLocation")
    return logical if isinstance(logical, dict) else {}


def _sarif_details(text: str, shared: Mapping[str, Mapping[str, Optional[str]]]) -> Dict[str, Dict[str, Any]]:
    """Each member's identity text by canonical ID: its ID as the file spells it, component, threat and MAESTRO layer, and
    what the SARIF needs besides: the mitigation, the DFD kind, the zone, and whether the scorer flagged the ID as reused.

    ``shared`` is ``parse_sarif_member_set(..., with_details=True)["details"]``, D8's one reading of a member's own result (P0-3; ruled
    at W3, 7a): the component from the logical location's ``name``, else ``properties.component``, the threat from ``message.text``,
    the mitigation from ``message.markdown``, the layer from ``maestro-layer`` and the kind from the logical location's ``kind``, each
    as written or ``None``. Neither renderer reads a result a second way, so this takes from the same result only what ``shared``
    lacks: the ID (the result's ``findingId/v1``, or ``properties.id`` where tachi's older SARIF has no fingerprint), the zone (the
    logical location's ``fullyQualifiedName`` is ``<zone>/<component>``, read from the object the component came from) and ``reused``
    (the ``reused-id`` flag in ``score-flags``, ruling B). The threat also loses ruling C's sentence, which this file writes for
    itself, and the kind is read back through ``KIND_SPELLINGS``, so that ``data-store`` is ``data``.
    """
    try:
        results = json.loads(text)["runs"][0].get("results", [])
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        results = []
    found: Dict[str, Dict[str, Any]] = {}
    for result in results if isinstance(results, list) else []:
        if not isinstance(result, dict):
            continue
        properties = result.get("properties") if isinstance(result.get("properties"), dict) else {}
        fingerprints = result.get("partialFingerprints") if isinstance(result.get("partialFingerprints"), dict) else {}
        identifier = fingerprints.get("findingId/v1")
        if identifier is None:
            identifier = properties.get("id")
        if not tp.id_matches("finding", identifier):
            continue
        canonical = tp.canonical_finding_id(identifier)
        if canonical in found or canonical not in shared:   # the first result of an ID, as ``shared`` has it, and none for an ID that has no result of its own
            continue
        own = shared[canonical]
        component = own["component"] or ""
        qualified = _logical_location(result).get("fullyQualifiedName")
        qualified = qualified if isinstance(qualified, str) else ""
        flags = properties.get("score-flags")
        found[canonical] = {
            "id": identifier, "component": component, "threat": _CORRELATION_TAIL.sub("", own["threat"] or ""), "layer": own["layer"] or "",
            "mitigation": own["mitigation"] or "", "kind": KIND_SPELLINGS.get(own["kind"] or "", DEFAULT_KIND),
            "zone": qualified[:-len(component) - 1] if component and qualified.endswith("/" + component) else "",
            "reused": isinstance(flags, list) and REUSED_FLAG in flags}
    return found


def _members_from_sarif(run: Run, entry: Mapping[str, Any], raw: bytes, kept: str) -> List[Dict[str, Any]]:
    """D8's fallback: the member set and the inherent scores of ``risk-scores.sarif``, through ``parse_sarif_member_set``.

    An empty extraction stops the run before anything is written (KB 22). A member that has no result of its own (a
    legacy peer reference) has no score, so it can't be rendered. The file records no status, so every member lacks
    ``delta_status`` (S-12(b)) and is flagged ``input:delta_status:not-in-form``. A member's own result also gives what
    this file's SARIF repeats: its MAESTRO layer (``Unclassified`` when the result holds none, gap B), mitigation, DFD kind,
    zone and ``reused-id`` flag, read by the shared reader (``with_details``) except the zone and the flag (``_sarif_details``).
    The groups are the file's own correlation properties, and a group that names no ID is kept in ``run.groups`` for
    ``_prepare`` to count.
    """
    name = os.path.basename(entry["path"])
    try:
        text = raw.decode("utf-8")
        found = tachi_parsers.parse_sarif_member_set(text, with_scores=True, with_details=True)
    except (UnicodeDecodeError, ValueError) as exc:
        raise RenderError(2, "%s holds no findings to assess: %s" % (name, str(exc)[:200]), "regenerate it with /tachi.risk-score", kept=kept) from None
    details = _sarif_details(text, found["details"])
    run.groups = found["groups"]
    members = []
    for canonical in sorted(found["members"], key=tp.finding_sort_key):
        shown = details.get(canonical)
        if shown is None:
            raise RenderError(2, "%s names %s only as a peer reference, so it holds no result and no score for it" % (name, canonical),
                              "regenerate it with /tachi.risk-score", kept=kept)
        score = found["scores"].get(canonical, {}).get("composite")
        members.append({"id": shown["id"], "canon": canonical, "inherent": _valid_inherent(name, canonical, score, kept),
                        "component": shown["component"].strip() or "Unspecified", "threat": shown["threat"].strip() or "No threat description.",
                        "layer": shown["layer"].strip() or "Unclassified", "reused": shown["reused"], "mitigation": shown["mitigation"],
                        "kind": shown["kind"], "zone": shown["zone"].strip() or DEFAULT_ZONE})
        _refuse_forbidden(name, canonical, shown, "regenerate %s with /tachi.risk-score, or edit the value to remove the character, then re-run the command" % name, kept)
    return members


def _threats_why(risk_text: Optional[str]) -> str:
    """Why the planner reached no ``threats.md``, worked out again: it printed the reason on stderr, and the plan has no slot for it."""
    if risk_text is None:
        return "%s names no source" % RISK_SCORES_SARIF
    source = _scored_source_file(risk_text)
    if source is None:
        return "the scored input's source_file names no threat model"
    checked = rules.check_run_file(source, cwd=Path(os.getcwd()), expected_name="threats.md")
    if checked.path is None:
        return "source_file %s can't be used: %s" % (ascii(source[:80]), checked.reason)
    return "the plan holds no threats.md input for the usable source_file %s" % ascii(source[:80])


def _without_threats(risk_text: Optional[str]) -> str:
    """What follows from reading no threat model, for the warning's detail (gap B, T053).

    A scored ``risk-scores.md`` holds no layer and no group, so without the threat model every layer is Unclassified and no
    finding is correlated. D8's fallback input, ``risk-scores.sarif``, holds each member's own text, layer and correlation.
    """
    if risk_text is None:
        return ("the text of each finding comes from the scored SARIF, a MAESTRO layer that its result doesn't hold is Unclassified, and the "
                "correlation groups are the SARIF's own")
    return "the text of each finding comes from the scored input, every MAESTRO layer falls back to Unclassified, and no finding is correlated"


def _load_threats(run: Run, plan: Mapping[str, Any], inputs: Mapping[str, bytes], risk_text: Optional[str]) -> None:
    """The threat model that the planner read (ADR-050 D2, D8).

    The planner reaches ``threats.md`` through the scored input's validated ``source_file`` and holds it as a digest-checked
    plan input, so these are the bytes it read. When the plan has none (the input names no usable source, or it is
    ``risk-scores.sarif``), the reason is worked out again for the record. That isn't fatal, because the member set doesn't
    come from this file: the text of each finding then comes from the scored input, a layer that the input doesn't record is
    Unclassified, no finding is correlated (unless the scored SARIF's own properties group it), there is no body line for the
    architecture path, and the stage record says why.
    """
    planned = plan["inputs"].get("threats")
    if planned is None:
        run.warn("threats-unreadable", "no threat model was read (%s), so %s" % (_threats_why(risk_text), _without_threats(risk_text)))
        return
    try:
        run.threats_text = inputs["threats"].decode("utf-8")
    except UnicodeDecodeError:
        run.warn("threats-unreadable", "the threat model %s is not strict UTF-8, so %s" % (os.path.basename(planned["path"]), _without_threats(risk_text)))
        return
    run.threats_path = planned["path"]


def _read_reference(run: Run, kept: str) -> Optional[Dict[str, Any]]:
    """The reference set of the threat model that was read: its open findings, with each one's layer and status.

    Returns ``None`` when there is none or Section 7 can't be read, with a warning, because the member set doesn't come
    from this file. Every value taken from it is checked for a forbidden character first (P0-4).
    """
    if run.threats_text is None:
        return None
    source = os.path.basename(run.threats_path or "threats.md")
    try:
        reference = tachi_parsers.parse_reference_set(run.threats_text, source=source)
    except tachi_parsers.ReferenceSetError as exc:
        run.warn("threats-unreadable", "%s: %s, so the text of each finding comes from the scored input and every MAESTRO layer is Unclassified"
                 % (source, exc.reason))
        return None
    remedy = "regenerate %s with /tachi.threat-model, or edit the value to remove the character, then re-run the command" % source
    for finding in list(reference["open"]) + list(reference["resolved"]):
        _refuse_forbidden(source, finding["id"], finding, remedy, kept)
    run.resolved_ids = sorted({*run.resolved_ids, *(tp.canonical_finding_id(finding["id"]) for finding in reference["resolved"])}, key=tp.finding_sort_key)
    for row in tachi_parsers.parse_markdown_table(run.threats_text, "### Components"):
        name = row.get("Component", "").strip()
        if name and name not in run.component_info:
            run.component_info[name] = (row.get("Type", "").strip(), row.get("MAESTRO Layer", "").strip())
    for canonical, layer in tachi_parsers.parse_finding_layers(run.threats_text).items():   # D2's chain, steps 1 and 2: Section 7's cell, else the finding's own row in §3 or §4
        run.finding_layer.setdefault(canonical, layer)
    for row in tachi_parsers.parse_markdown_table(run.threats_text, "### Trust Zones"):   # the SARIF's logical location names each component's zone
        zone = row.get("Zone", "").strip()
        for member in (part.strip() for part in row.get("Components", "").split(",")):
            if zone and member:
                run.component_zone.setdefault(member.casefold(), zone)
    _refuse_forbidden(source, None, (run.component_info, run.finding_layer, run.component_zone), remedy, kept)
    lacking = reference.get("lacking", {})
    if lacking:   # S-12(b): each such finding carries the flags, and the stage record lists them
        names = sorted({name for found in lacking.values() for name in found})
        where = "Section 7 of %s (the %s form)" % (source, reference["form"])
        run.issues.append("%s lacks %s for %d of %d findings: each carries the flag %s" % (
            where, ", ".join(names), len(lacking), len(reference["open"]), ", ".join(tachi_parsers.FORM_LACKS_FLAG % name for name in names)))
        run.warn("value-not-in-form", "%s lacks %s for %d findings, such as %s"
                 % (where, ", ".join(names), len(lacking), ", ".join(sorted(lacking, key=tp.finding_sort_key)[:5])))
    for canonical in reference["duplicates"]:
        run.issues.append("Section 7 or Section 4c of %s lists %s more than once: the first row is used, and an open row beats a resolved one" % (source, canonical))
    if reference["duplicates"]:
        run.warn("duplicate-finding-id", "%s lists these findings more than once, and the first row of each is used: %s"
                 % (source, ", ".join(reference["duplicates"])))
    return reference


def _overlay_reference(run: Run, members: List[Dict[str, Any]], reference: Optional[Mapping[str, Any]]) -> None:
    """Give each member the identity text of the threat model: the finding ID as Section 7 spells it, its component,
    threat, layer and status, its source attribution, and what its SARIF result repeats (the mitigation, the DFD kind and
    the zone). The layer is the scorer's chain (``_identity``), so that this file's ``maestro-layer`` is the scorer file's
    for the same finding (gap B): the reference set's MAESTRO Layer cell, else the finding's own row in a per-finding table (§3 and §4;
    both through ``tachi_parsers.parse_finding_layers``, so ``run.finding_layer`` holds them), else the member's own, else its
    component's Section 1 layer (found by name, then case-folded), else ``Unclassified``. A kind is the component's Section 1 type, as the scorer
    reads it, and a zone is the one that Section 2 lists the component under."""
    by_canon = {tp.canonical_finding_id(finding["id"]): finding for finding in reference["open"]} if reference is not None else {}
    lacking = reference.get("lacking", {}) if reference is not None else {}
    for member in members:
        finding = by_canon.get(member["canon"])
        if reference is not None and finding is None:
            run.issues.append("%s is a scored open finding, but the threat model has no open row for it, so its component, threat and layer "
                              "come from the scored input" % member["id"])
        if finding is not None:
            member["id"] = finding["id"]
            member["component"] = finding["component"] or member["component"]
            member["threat"] = finding["threat"] or member["threat"]
            member["attribution"] = tuple(entry.get("id", "") for entry in finding.get("source_attribution", ()) if entry.get("id"))
        member["delta"] = _delta_status(finding) if finding is not None else "NEW"
        member["component"] = member["component"] or "Unspecified"
        member["threat"] = member["threat"] or "No threat description."
        info = run.component_info.get(member["component"])
        if info is None:   # the scorer's own lookup: by name, then case-folded
            folded = member["component"].casefold()
            info = next((value for name, value in run.component_info.items() if name.casefold() == folded), ("", ""))
        member["layer"] = run.finding_layer.get(member["canon"]) or member["layer"] or info[1] or "Unclassified"
        member["kind"] = KIND_OF_DFD_TYPE.get(info[0], DEFAULT_KIND)
        member["zone"] = run.component_zone.get(member["component"].casefold()) or DEFAULT_ZONE
        member["mitigation"] = finding["mitigation"] if finding is not None else ""
        member["form_flags"] = list(reference["flags"].get(member["canon"], ())) if reference is not None and member["canon"] in lacking else []


def _prepare_correlation(run: Run) -> None:
    """The correlation groups of the scored findings, and each correlated finding's role (D8).

    Correlation comes from Section 4a of the ``threats.md`` that the scored input's validated ``source_file`` names, read
    by D8's rules and filtered to the member set, or, in D8's fallback, from the correlation properties of the scored SARIF
    (already in ``run.groups``). With no threat model there is no correlation, and the stage record already says why
    (``_load_threats``). Correlation is a property and a sentence and never part of a key, so no key changes either way.
    Only a group with an ID reaches the emitter, whose roles, ``correlation-*`` properties and ruling C's sentence all name
    it. A group that the SARIF names no ID for is counted in a warning, and its members carry none of them. A finding that two
    groups of Section 4a list stays in the first, as D8 says, and is never dropped without a word: each one is an Input Issue, and
    the stage record's warning ``correlation-member-repeated`` counts them (PM W4 ruling R-F).
    """
    if run.threats_text is not None:
        source = os.path.basename(run.threats_path or "threats.md")
        grouped = tachi_parsers.parse_correlation_groups(run.threats_text, member_ids=sorted(run.open_ids, key=tp.finding_sort_key))
        for problem in grouped["errors"]:
            run.issues.append("Section 4a of %s, line %d: the row %s %s, so it is skipped" % (source, problem["line"], repr(problem["row"][:60]), problem["reason"]))
        for repeat in grouped["repeated"]:   # PM W4 ruling R-F: D8's claim rule keeps an ID in the first group that lists it, and a run says so
            run.issues.append("Section 4a of %s: %s" % (source, repeat["reason"]))
        if grouped["repeated"]:
            count = len(grouped["repeated"])
            run.warn("correlation-member-repeated", "Section 4a of %s lists %d finding%s in more than one correlation group, and the first group "
                     "claims each: %s" % (source, count, "" if count == 1 else "s", _named([repeat["id"] for repeat in grouped["repeated"]])))
        run.groups = grouped["groups"]
    named = [(group["group_id"], group["members"]) for group in run.groups if group["group_id"] is not None]
    if len(named) != len(run.groups):
        run.warn("correlation-group-unnamed", "%s gives no group ID to %d of its %d correlation groups, so their members carry no correlation "
                 "properties and no correlation sentence" % (RISK_SCORES_SARIF, len(run.groups) - len(named), len(run.groups)))
    run.assignments = sc.correlation_assignments(named, run.open_ids)


def _baseline_held(text: str) -> frozenset:
    """The canonical IDs of the findings whose result a baseline ``compensating-controls.md`` holds: the only findings whose
    ``carried_forward`` the renderer accepts (ADR-050 D2, amended at W4).

    A 1.1 file holds a result in Section 7's ``### Assessment Inputs``, which ``parse_controls_assessment_inputs`` reads as the planner
    does for a unit's row (AR-T3). A rendered Section 2 row doesn't count there: its text is escaped, and the agent never copies from
    it (RR1). A 1.0 file persists nothing, so it holds a result as a Section 2 row with the finding's ID under one of the four band
    headings, read by ``_rows_under`` as this renderer's own from-disk check reads it. The split is the file's ``schema_version`` as
    ``parse_frontmatter`` reads it, which is ``"1.0"`` for a file that has none. Nothing is written, and no warning is raised.
    """
    if tachi_parsers.parse_frontmatter(text)["schema_version"] == "1.0":
        named = [row.get("Threat ID", "") for band in BANDS for row in _rows_under(text, r"^### %s Residual Severity[ \t]*$" % band)[0]]
    else:
        named = list(tachi_parsers.parse_controls_assessment_inputs(text)["inputs"])
    return frozenset(tp.canonical_finding_id(name) for name in named if tp.id_matches("finding", name))


def _prepare_baseline(run: Run, plan: Mapping[str, Any], refs: Mapping[str, str], inputs: Mapping[str, bytes]) -> None:
    """Whether a baseline ``compensating-controls.md`` resolved (R-6, D9), and which findings' results it holds: with the finding's
    status, the conditions under which the renderer accepts ``carried_forward`` (ADR-050 D2, amended at W4).

    The planner resolved the baseline and recorded its controls file as the digest-checked input
    ``baseline_compensating_controls``, so that input is the answer, and its bytes are the file that ``_baseline_held`` reads. The
    planner decoded them as strict UTF-8 before it recorded the input, so decoding them again can't fail. When there is no input,
    why is worked out again for the record.
    """
    if "baseline_compensating_controls" in plan["inputs"]:
        run.baseline_resolved = True
        run.baseline_held = _baseline_held(inputs["baseline_compensating_controls"].decode("utf-8"))
        return
    source = tachi_parsers.parse_baseline_frontmatter(run.threats_text)["source"] if run.threats_text is not None else None
    resolution = rules.resolve_baseline(flag=refs.get("baseline_dir"), baseline_source=source, cwd=Path(run.cwd))
    if resolution.run_dir is None:
        if resolution.reason != "not-named":   # free text, an unresolvable path or a failed check: no baseline, and the record says why
            run.warn("baseline-unresolved", "the baseline named by %s was not used (%s), so no finding is carried forward"
                     % ("--baseline" if resolution.origin == "flag" else "baseline.source", resolution.reason))
    elif MD in resolution.files:   # the file passes the checks, and the plan recorded no input for it: the planner could not read it
        run.warn("baseline-unreadable", "the baseline %s could not be read, so no finding is carried forward" % MD)
    else:
        run.warn("baseline-unresolved", "the baseline run directory has no usable %s (%s), so no finding is carried forward"
                 % (MD, resolution.file_reasons.get(MD, "missing")))


def _prepare(run: Run, plan: Mapping[str, Any], inputs: Mapping[str, bytes], refs: Mapping[str, str], kept: str) -> List[Dict[str, Any]]:
    """Read the scored input, the threat model, the target, the architecture path and the baseline. Returns the members."""
    entry = plan["inputs"].get("risk_scores")
    if entry is None:
        raise RenderError(2, "the plan names no risk-scores input", "re-run the command with the run's risk-scores.md", kept=kept)
    refused = plan.get("architecture_warning")   # D7: the planner refused the --architecture candidate, and the record lists that first
    if isinstance(refused, dict):
        run.warn(refused["code"], refused["detail"])
    run.sources = {name: item["sha256"] for name, item in sorted(plan["inputs"].items())}
    run.source_file = _relative(entry["path"], run.cwd)
    target = refs.get("target")   # the planner requires --target for this stage, because every evidence file is resolved under it
    if target is None:
        raise RenderError(2, "the plan names no target directory, which this stage requires", "re-run the command with --target naming the scanned directory", kept=kept)
    if tp.path_problem(target, allow_absolute=True) is not None or not os.path.isdir(target):
        raise RenderError(2, "refs.target is not a directory the renderer can use", "re-run the command with --target naming the scanned directory", kept=kept)
    run.target, run.target_path = target, _relative(target, run.cwd)

    if os.path.basename(entry["path"]) == RISK_SCORES_SARIF:
        members = _members_from_sarif(run, entry, inputs["risk_scores"], kept)
        _load_threats(run, plan, inputs, None)
        for member in members:
            member["form_flags"] = [tachi_parsers.FORM_LACKS_FLAG % "delta_status"]
        run.issues.append("%s is the scored input (D8's fallback), so it lacks delta_status for every finding: each carries the flag %s"
                          % (os.path.basename(entry["path"]), tachi_parsers.FORM_LACKS_FLAG % "delta_status"))
        run.warn("value-not-in-form", "%s lacks delta_status for %d findings, such as %s" % (
            os.path.basename(entry["path"]), len(members), ", ".join(member["canon"] for member in members[:5])))
        for member in members:
            member["delta"], member["attribution"] = "NEW", ()
    else:
        members = _members_from_markdown(run, entry, inputs["risk_scores"], kept)
        _load_threats(run, plan, inputs, inputs["risk_scores"].decode("utf-8"))
        _overlay_reference(run, members, _read_reference(run, kept))
    run.open_ids = {member["canon"] for member in members}
    _prepare_correlation(run)

    # The architecture file: the one path that gives the URI (ADR-050 D7). The controls stage elevates nothing, so it reads no tags.
    resolution = sc.resolve_architecture(refs.get("architecture"), threats_text=run.threats_text,
                                         run_dir=os.path.dirname(run.threats_path) if run.threats_path else None, root=run.cwd)
    run.uri = resolution.uri
    for found in resolution.warnings:
        run.warn(found["code"], found["detail"])
    _prepare_baseline(run, plan, refs, inputs)
    return members


# =============================================================================
# Computing the rows
# =============================================================================

def _evidence_path(run: Run, row: Row, index: int, file: str) -> str:
    """The spelling of an evidence entry's ``file`` that both rendered files print, checked against the target (ADR-050 D7, F16).

    ``resolve_file`` walks the target without following a link, so a file that is missing, a link or not a regular file is refused.
    The part only checked the syntax, because the target's files are not its input. A file that it accepts takes its canonical spelling,
    and is cached for the SARIF's ``relatedLocations``. One that it refuses has no canonical spelling: the entry is kept as written,
    recorded on the row as ``(entry index, file, check)`` and left out of ``relatedLocations``. It is flagged, never refused (ruled at
    W3, question 5), because the control analyzer copies an UNCHANGED finding's evidence verbatim, so a refusal would recur on every
    later run once a file moves, and no re-run could clear it.
    """
    if file not in run.evidence_cache:
        try:
            run.evidence_cache[file] = sc.resolve_file(file, root=str(run.target))
        except sc.PathCheckError as exc:
            row.unresolved.append((index, file, exc.check))
            return file
    return run.evidence_cache[file].path


def _layer_code(text: str) -> Optional[str]:
    """``L1`` to ``L7`` when ``text`` starts with a MAESTRO layer code, else ``None``."""
    found = _LAYER.match(text)
    return found.group(0) if found else None


def _check_cells(run: Run, row: Row) -> None:
    """R-34's two row checks (ADR-050 D2, ``contracts/module-signatures.md``). They never reject the item: the part validator does
    that, for the cell count and the Threat ID.

    **Fill.** The four computed cells are the renderer's, by column position. A cell that holds anything but its own slot token
    (a wrong number, the right number, prose, an empty cell, another cell's token) is overwritten when Section 2 is written, and
    counted once here. ``CF`` is filled from the accepted ``carried_forward`` and is never counted.

    **Check.** Control Status, Control Category, Component and MAESTRO Layer are the agent's text, and each is compared with the
    structured value that the SARIF and every total follow: the status through ``classify_control_status`` (so ``Partial`` and
    ``partial`` agree), the category by its display name or its slug, the component exactly, and the layer by its code (``L1`` to
    ``L7``, where a layer with no code, such as ``Unclassified``, matches only itself). A cell that disagrees is flagged, once.
    """
    cells = row.agent_cells
    row.overwritten = sum(1 for position, token in COMPUTED_CELLS.items() if cells[position] != token)
    run.overwritten += row.overwritten
    status, category, component, layer = (cells[position] for position in CHECKED_CELLS.values())
    code = _layer_code(row.layer)
    agree = {"control_status": STATUS_OF_CLASS[tachi_parsers.classify_control_status(status)[0]] == row.control,
             "control_category": category.casefold() in (row.control_category, CATEGORY_NAME[row.control_category].casefold()),
             "component": component == row.component,
             "maestro_layer": layer == row.layer if code is None else _layer_code(layer) == code}
    row.flags += [Flag("input", field, SOURCES_DISAGREE) for field in CHECKED_CELLS if not agree[field]]


def _lookup_for(run: Run, row: Row) -> Any:
    """The slot lookup of ADR-050 D3's table for this stage: this finding's rendered values."""
    allowed_refs = set(RULE_BY_CATEGORY[row.threat_category][4]) | set(row.attribution)   # its rule's relationships, and its reference cell (D3)
    layer = _LAYER.match(row.layer)
    if layer:
        allowed_refs.add(layer.group(0))
    values = {("score", "inherent"): _one(row.inherent), ("score", "residual"): _one(row.residual), ("band", "inherent"): row.inherent_band,
              ("band", "residual"): row.residual_band, ("count", "evidence"): str(len(row.item["evidence"])),
              ("pct", "reduction"): str(ts.reduction_percentage(row.inherent, row.residual)), ("name", "component"): row.component}

    def lookup(kind: str, argument: str) -> Optional[str]:
        if kind == "finding":
            return argument if argument in run.open_ids else None
        if kind == "ref":
            return argument if argument in allowed_refs else None
        return values.get((kind, argument))

    return lookup


def _narrate(run: Run, row: Row) -> None:
    """Resolve each assessment rationale into ``cell_text`` and the persisted text (D3 step 11, RR1).

    A field whose text or slots don't resolve takes its fixed sentence, is flagged ``input:<field>:narrative-fallback``
    and counted, and the sentence is what is persisted. A field that already fell back in the part holds that sentence,
    which resolves, so nothing is counted twice.
    """
    lookup = _lookup_for(run, row)
    for index, entry in enumerate(row.item["evidence"]):
        assessment = entry.get("assessment")
        if not assessment:
            continue
        for dimension in tp.ASSESSMENT_DIMENSIONS:
            field, address = "evidence.assessment." + dimension, "evidence.%d.assessment.%s.rationale" % (index, dimension)
            text = assessment[dimension]["rationale"]
            cell = tp.resolve_narrative(text, STAGE, lookup, sink="cell") if tp.narrative_problem(text, STAGE) is None else None
            if cell is None:
                text = tp.FALLBACK_SENTENCES[field]
                cell = tp.escape_cell(text)
                if not any(flag.field == field and flag.cause == "narrative-fallback" for flag in row.flags):
                    row.flags.append(Flag("input", field, "narrative-fallback"))
                run.counts["narrative_fallbacks"] += 1
            row.persisted[address], row.cell_text[address] = text, cell


def _score(run: Run, members: Sequence[Mapping[str, Any]], items: Mapping[str, Mapping[str, Any]],
           part_flags: Mapping[str, List[str]], kept: str) -> None:
    """Make every row: the input's identity, the agent's judgment, and every number computed (D2, D5)."""
    extra = sorted(set(items) - run.open_ids, key=tp.finding_sort_key)
    if extra:
        run.issues.append("The parts hold items for findings that the scored input doesn't list as open, so they are not rendered: %s" % _named(extra))
    cleared: List[Tuple[str, str]] = []
    for member in members:
        item = items.get(member["canon"])
        if item is None:
            raise RenderError(4, "the parts hold no item for %s, so the run is incomplete" % member["id"], "re-run the command", kept=kept)
        row = Row(member["id"], member["component"], member["threat"], member["layer"], member["delta"], member["inherent"], item,
                  member.get("attribution", ()))
        row.kind, row.zone, row.mitigation = member["kind"], member["zone"], member["mitigation"]
        run.rows.append(row)
        row.agent_cells = tp.matrix_row_cells(item["matrix_row"])   # 11 cells, the first this finding's ID: ``read_part`` has checked it (D3 step 9)
        _check_cells(run, row)
        row.paths = [_evidence_path(run, row, index, entry["file"]) for index, entry in enumerate(item["evidence"])]
        if row.unresolved:   # W3 question 5: the finding is flagged once however many entries fail, and Section 7 lists each failed entry
            row.flags.append(Flag("input", "evidence.file", "unresolved"))
            run.issues += ["%s: evidence entry %d, %s, is not a usable file under the target (%s), so it is kept as written and has no relatedLocations entry"
                           % (row.finding_id, number + 1, ascii(_shorten(file, 80)), check) for number, file, check in row.unresolved]
        if item["carried_forward"]:   # accepted only for an UNCHANGED finding whose result the resolved baseline controls file holds (D2, W4); else cleared
            if not run.baseline_resolved:
                cleared.append((row.finding_id, "no baseline %s resolved" % MD))
            elif row.delta != "UNCHANGED":
                cleared.append((row.finding_id, "its status in the threat model is %s, not UNCHANGED" % row.delta))
            elif row.canon not in run.baseline_held:
                cleared.append((row.finding_id, "the baseline %s holds no result for it" % MD))
            else:
                row.carried = True
        _narrate(run, row)
        for text in part_flags.get(row.canon, ()):
            if not any(known.text() == text for known in row.flags):
                row.flags.append(_flag_from_text(text))
        for text in member.get("form_flags", ()):   # S-12(b): a value that the input's form lacks
            row.flags.append(_flag_from_text(text))
        if member["reused"]:   # ruling B: the same finding carries the flag in this file too
            row.flags.append(Flag("reused-id", "finding_id", "baseline"))
        seen: set = set()   # a finding carries each flag once, whichever step raised it
        row.flags = [flag for flag in row.flags if not (flag.text() in seen or seen.add(flag.text()))]
    refused = [row for row in run.rows if row.unresolved]
    if refused:   # ruled at W3: the run finishes with exit 5, and the warning counts the entries and the findings and names up to ``EXAMPLE_CAP`` of them
        run.warn("evidence-file-unresolved", "%d evidence entries of %d findings name a file that the resolver refuses under the target, so each is kept as written "
                 "and has no relatedLocations entry: %s" % (sum(len(row.unresolved) for row in refused), len(refused), _named([row.finding_id for row in refused])))
    if cleared:
        run.issues.append("%d findings had carried_forward cleared (%s), so they count as scanned: %s" % (
            len(cleared), "carried_forward is accepted only for an UNCHANGED finding whose result the resolved baseline %s holds" % MD,
            _named([name for name, _why in cleared])))
        run.warn("carried-forward-cleared", "the control analyzer set carried_forward on %d findings that can't be carried (%s), such as %s"
                 % (len(cleared), cleared[0][1], ", ".join(name for name, _why in cleared[:5])))
    run.carry_forward_count = sum(1 for row in run.rows if row.carried) if run.baseline_resolved else None
    run.rescan_scope = "incremental" if run.carry_forward_count else "full"
    run.by_residual = sorted(run.rows, key=lambda row: (-row.residual, tp.finding_sort_key(row.canon)))
    run.recommended = sorted((row for row in run.rows if row.control != "found"), key=lambda row: (-row.inherent, tp.finding_sort_key(row.canon)))
    run.inherent_total = sum((row.inherent for row in run.rows), Decimal("0.0"))
    run.residual_total = sum((row.residual for row in run.rows), Decimal("0.0"))
    _group_controls(run)


def _group_controls(run: Run) -> None:
    """Section 3's controls: one for each distinct ``(category, file, line)``, and the findings that cite it (D2).

    A control is shown through the first finding in S-2 order that cites it, and the Section 3 order is the template's
    categories, then the file, then the line. Each control gets an ID, ``CTL-<category token>-<n>``.
    """
    found: Dict[Tuple[str, str, int], Control] = {}
    for row in run.rows:
        for index, entry in enumerate(row.item["evidence"]):
            key = (row.control_category, row.paths[index], entry["line"])
            control = found.get(key)
            if control is None:
                found[key] = Control(key[0], key[1], key[2], row, index)
            elif control.members[-1] is not row:
                control.members.append(row)
    run.controls = []
    for value, _name, token in CATEGORIES:
        for number, key in enumerate(sorted((key for key in found if key[0] == value), key=lambda each: (each[1], each[2])), 1):
            found[key].control_id = "CTL-%s-%02d" % (token, number)
            run.controls.append(found[key])


# =============================================================================
# compensating-controls.md
# =============================================================================

def _section_2_cells(row: Row) -> List[str]:
    """Section 2's row of a finding, as 11 raw cells in K8's order (the writer escapes each): the agent's own row with the
    renderer's cells filled in by column position (ADR-050 D2, R-34).

    The Threat ID is the finding's ID as Section 7 of ``threats.md`` spells it, ``CF`` is ``CF`` or a dash from the accepted
    ``carried_forward``, and the four computed cells are this run's inherent and residual score and band. Every other cell is the
    agent's text as written: the Threat is model text (NFR-10's escaping is all that is asked of it), and the other four are checked
    at ``_check_cells`` (flagged where they disagree) and never filled, as D2 says for PR 1.
    """
    cells = list(row.agent_cells)
    cells[0], cells[CF_CELL] = row.finding_id, row.cf
    for position, value in zip(COMPUTED_CELLS, (_one(row.inherent), row.inherent_band, _one(row.residual), row.residual_band)):
        cells[position] = value
    return cells


def _frontmatter(run: Run, scoring: str) -> List[str]:
    return ["---", 'schema_version: "%s"' % SCHEMA_VERSION, 'date: "%s"' % scoring, "source_file: %s" % _quoted(run.source_file),
            "target_path: %s" % _quoted(run.target_path), 'classification: "security"', 'rescan_scope: "%s"' % run.rescan_scope,
            "carry_forward_count: %s" % ("null" if run.carry_forward_count is None else run.carry_forward_count), "---", ""]


def _status_counts(run: Run) -> Dict[str, int]:
    return {status: sum(1 for row in run.rows if row.control == status) for status in STATUS_CELL}


def _md_section_1(run: Run, out: List[str], scoring: str) -> None:
    counts = _status_counts(run)
    shares = ts.largest_remainder(counts)
    total = len(run.rows)
    out += ["## 1. Executive Summary", "",
            "**%d** threats analyzed | **%d** Control Found | **%d** Partial Control | **%d** No Control Found"
            % (total, counts["found"], counts["partial"], counts["missing"]), "",
            "**Coverage**: %d%% Found | %d%% Partial | %d%% Missing" % (shares["found"], shares["partial"], shares["missing"]), "",
            "**Risk Reduction**: %s inherent -> %s residual (**%s%%** reduction)"
            % (_one(run.inherent_total), _one(run.residual_total), ts.reduction_percentage(run.inherent_total, run.residual_total)), ""]
    if run.recommended:
        top = run.recommended[0]
        out += ["**Highest-Risk Unmitigated Finding**: %s %s %s %s Composite %s (%s)"
                % (top.finding_id, DASH, tp.escape_prose(top.component), DASH, _one(top.inherent), top.inherent_band), ""]
    else:
        out += ["**Highest-Risk Unmitigated Finding**: None (a control was found for every scored finding)", ""]
    out += ["| Metric | Value |", "|--------|-------|", "| Analysis date | %s |" % scoring,
            "| Source file | %s |" % ("`%s`" % tp.escape_cell(run.source_file) if run.source_file else DASH),
            "| Target codebase | %s |" % ("`%s`" % tp.escape_cell(run.target_path) if run.target_path else DASH),
            "| Schema version | %s |" % SCHEMA_VERSION, "",
            "**Coverage Distribution:**", "", "| Status | Count | Percentage |", "|--------|-------|------------|"]
    out += ["| %s | %d | %d%% |" % (STATUS_CELL[status], counts[status], shares[status]) for status in STATUS_CELL]
    out += ["| **Total** | **%d** | **%d%%** |" % (total, sum(shares.values())), ""]
    flagged = sum(1 for row in run.rows if row.flags)
    if flagged:
        out += ["> %d finding(s) carry integrity flags. Section 7 lists each one." % flagged, ""]
    disagree = [row.finding_id for row in run.rows if any(flag.field in CHECKED_CELLS and flag.cause == SOURCES_DISAGREE for flag in row.flags)]
    if disagree:
        out += ["> For %d finding(s), the control analyzer's own Control Status, Control Category, Component or MAESTRO Layer cell in Section 2 "
                "disagrees with its structured result or the scored input: %s. Section 2 shows the cell as the analyzer wrote it, and the SARIF "
                "and every total follow the structured value." % (len(disagree), _named(disagree)), ""]
    unresolved = [row.finding_id for row in run.rows if row.unresolved]
    if unresolved:
        out += ["> For %d finding(s), an evidence file is not a usable regular file under the target: %s. Section 3 and the SARIF's control-evidence "
                "show each as the control analyzer wrote it, the SARIF's relatedLocations leave it out, and Section 7 gives the resolver's check."
                % (len(unresolved), _named(unresolved)), ""]
    if run.issues:
        out += ["> %d input issue(s) are listed in Section 7." % len(run.issues), ""]


def _md_section_2(run: Run, out: List[str]) -> None:
    out += ["---", "", "## 2. Coverage Matrix", "",
            "Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual "
            "score descending, and by finding ID within equal scores. A band with no threat has no table.", ""]
    counts = {band: 0 for band in BANDS}
    for band in BANDS:
        mine = [row for row in run.by_residual if row.residual_band == band]
        counts[band] = len(mine)
        if not mine:
            continue
        out += ["### %s Residual Severity" % band, "", "| " + " | ".join(K8_HEADER) + " |", "|" + "---|" * CELL_COUNT]
        out += ["| " + " | ".join(tp.escape_cell(cell) for cell in _section_2_cells(row)) + " |" for row in mine]
        out.append("")
    shares = ts.largest_remainder(counts)
    out += ["### Summary Statistics", "", "| Residual Severity | Count | Percentage |", "|-------------------|-------|------------|"]
    out += ["| %s | %d | %d%% |" % (band, counts[band], shares[band]) for band in BANDS]
    out += ["| **Total** | **%d** | **%d%%** |" % (len(run.rows), sum(shares.values())), ""]


def _md_control(run: Run, control: Control, out: List[str]) -> None:
    row, index = control.row, control.index
    entry = row.item["evidence"][index]
    status = control.status
    fence = tp.fence_for(entry["snippet"])
    out += ["#### %s %s %s" % (control.control_id, DASH, tp.escape_cell(entry["summary"])), "",
            "**Category**: %s | **Status**: %s | **Effectiveness**: %s" % (CATEGORY_NAME[control.category], STATUS_CELL[status], EFFECTIVENESS[status]), "",
            "**Detected in**: `%s`" % tp.escape_cell("%s:%d" % (control.path, control.line)), "",
            fence + entry["language"], entry["snippet"], fence, ""]
    assessment = entry.get("assessment")
    if assessment:
        out += ["**Effectiveness Assessment**:", "", "| Dimension | Rating | Rationale |", "|-----------|--------|-----------|"]
        for dimension in tp.ASSESSMENT_DIMENSIONS:
            out.append("| %s | %s | %s |" % (dimension.capitalize(), assessment[dimension]["rating"],
                                              row.cell_text["evidence.%d.assessment.%s.rationale" % (index, dimension)]))
        out.append("")
    out += ["**Threats Mitigated by This Control**:", "", "| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |",
            "|-----------|-----------|--------|----------------|------------------|----------------|"]
    out += ["| %s | %s | %s | %s | %s | %s |" % (member.finding_id, tp.escape_cell(member.component), tp.escape_cell(_shorten(member.threat, THREAT_WIDTH)),
                                                  _one(member.inherent), member.factor, _one(member.residual)) for member in control.members]
    out += ["", "---", ""]


def _md_section_3(run: Run, out: List[str]) -> None:
    out += ["---", "", "## 3. Control Details", "",
            "Per-control evidence showing detected security controls with their location, code evidence and threat coverage. One subsection "
            "per detected control, grouped by control category.", ""]
    if not run.controls:
        out += ["No security control was detected for any scored finding.", ""]
        return
    for value, name, _token in CATEGORIES:
        mine = [control for control in run.controls if control.category == value]
        if mine:
            out += ["### %s" % name, ""]
            for control in mine:
                _md_control(run, control, out)


def _block_head(number: int, row: Row) -> List[str]:
    """The renderer's own lines of one Section 4 block, ahead of the agent's body (ADR-050 D2, R-34): the numbered heading with the
    component and the inherent score and band, a blank line, and the ``Current Status`` line in the structured status's display form."""
    heading = "#### %d. %s %s %s (Composite: %s, %s)" % (number, row.finding_id, DASH, tp.escape_prose(row.component), _one(row.inherent), row.inherent_band)
    return [heading, "", "**Current Status**: %s" % STATUS_CELL[row.control]]


def _md_section_4(run: Run, out: List[str]) -> None:
    """Section 4 under R-34. The renderer writes the group each block sits under (the band of its inherent score), the block order
    (inherent score descending, then S-2 order), the numbers, which run on through the groups, the heading and the ``Current Status``
    line. The agent's body follows, line for line as escaped prose: the part validator has checked its structure."""
    out += ["---", "", "## 4. Recommendations", "",
            "Actionable recommendations for threats classified as \"No Control Found\" or \"Partial Control\", grouped by inherent severity and "
            "sorted by inherent score descending (highest risk gaps first).", ""]
    if not run.recommended:
        out += ["Every scored finding has a control found, so there is nothing to recommend.", ""]
        return
    number = 0
    for heading, bands in GAP_GROUPS:
        mine = [row for row in run.recommended if row.inherent_band in bands]
        if not mine:
            continue
        out += [heading, ""]
        for row in mine:
            number += 1
            out += _block_head(number, row) + ["", tp.escape_prose(row.item["recommendation_body"]), "", "---", ""]
    out += ["### Recommendation Field Definitions", "", "| Field | Description |", "|-------|-------------|",
            "| **What to Implement** | Specific control to add or harden. For \"No Control Found\": full implementation guidance. For \"Partial Control\": "
            "targeted hardening of the existing control. |",
            "| **Where to Implement** | Suggested file path or module in the target codebase. |",
            "| **Reference Patterns** | Industry-standard patterns, libraries or framework features to use as implementation reference. |",
            "| **Effort Estimate** | **Low**: configuration change or flag toggle. **Medium**: new middleware, function or module. "
            "**High**: architectural change affecting multiple components. |", ""]


def _shift_label(inherent: str, residual: str) -> str:
    return "%s -> %s" % (inherent, residual)


def _md_section_5(run: Run, out: List[str]) -> None:
    total = len(run.rows)
    out += ["---", "", "## 5. Residual Risk Summary", "",
            "Comparison of inherent risk (before controls) to residual risk (after controls), showing the risk reduction achieved by existing controls.", "",
            "### Aggregate Risk Reduction", "", "| Metric | Value |", "|--------|-------|",
            "| Total Inherent Risk Score | %s |" % _one(run.inherent_total), "| Total Residual Risk Score | %s |" % _one(run.residual_total),
            "| Delta | %s |" % _one(run.inherent_total - run.residual_total),
            "| Overall Reduction | %s%% |" % ts.reduction_percentage(run.inherent_total, run.residual_total), "",
            "### Per-Severity-Band Shift", "",
            "Breakdown of how threats shifted between severity bands after residual risk calculation. \"Shifted\" means a threat moved from a higher "
            "inherent severity band to a lower residual severity band due to detected controls.", "",
            "| Shift | Count | Examples |", "|-------|-------|----------|"]

    def examples(rows: Sequence[Row]) -> str:
        if not rows:
            return DASH
        return _named([row.finding_id for row in rows])

    for inherent, residual in SHIFTS:
        mine = [row for row in run.rows if (row.inherent_band, row.residual_band) == (inherent, residual)]
        out.append("| %s | %d | %s |" % (_shift_label(inherent, residual), len(mine), examples(mine)))
    unmoved = [row for row in run.rows if row.inherent_band == row.residual_band]
    out += ["| No Shift | %d | %s |" % (len(unmoved), examples(unmoved)), "| **Total** | **%d** | |" % total, "",
            "### Severity Distribution Comparison", "", "| Severity | Inherent Count | Residual Count | Change |", "|----------|----------------|----------------|--------|"]
    for band in BANDS:
        before, after = sum(1 for row in run.rows if row.inherent_band == band), sum(1 for row in run.rows if row.residual_band == band)
        out.append("| %s | %d | %d | %s |" % (band, before, after, _signed(after - before)))
    out += ["| **Total** | **%d** | **%d** | |" % (total, total), "",
            "### Reduction Factor Reference", "", "| Control Status | Reduction Factor | Formula | Description |", "|----------------|------------------|---------|-------------|"]
    out += ["| %s | %s | Inherent * %s | %s |" % (STATUS_CELL[status], factor, Decimal(1) - factor, FACTOR_WORDS[status])
            for status, factor in ts.REDUCTION_FACTOR_P0.items()]
    out.append("")


METHODOLOGY = """\
---

## 6. Methodology

This section documents how the control analyzer's judgments become the numbers in this report. For each scored finding the analyzer decides whether a control was found, partial or missing, cites the code that shows it, and recommends a fix for a gap. The renderer computes every inherent score, residual score, severity band, reduction factor, total and percentage from those judgments and the scored input, with exact decimal arithmetic and the date as an input, so the same parts, the same scores and the same date give the same file, byte for byte.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware, RBAC/ABAC patterns | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing algorithms, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

Each scored threat receives exactly one classification based on detected controls:

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

Residual risk per threat is calculated from the inherent score that the scored input records, which is never re-scored:

```
Residual Score = Inherent Score * (1 - Reduction Factor)
```

The result is rounded half up to one decimal (4.55 is 4.6), and mapped to a severity band with the thresholds of risk scoring:

| Severity | Residual Score Range |
|----------|---------------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 to 8.9 |
| **Medium** | 4.0 to 6.9 |
| **Low** | < 4.0 |

The totals in Sections 1 and 5 are the sums of the rounded rows, and the reduction percentage is rounded half up to one decimal.

### 6.4 Data Sources

- **Scored threats**: the open rows of `risk-scores.md` (or `risk-scores.sarif` when the markdown is absent). Each finding's composite score is its inherent score. Its component, threat text and MAESTRO layer come from the threat model that the scored input names as its source.
- **Target codebase**: scanned through the `--target` path. When an architecture description is available, its component definitions map components to files. Otherwise heuristic directories are prioritized.
- **STRIDE-to-control mapping**: the canonical mapping from threat categories to control categories decides which controls are searched for each threat.

### 6.5 Limitations

- Static analysis only: runtime control behavior is not evaluated
- A 200-file read budget for each dispatch: large codebases may have directories skipped
- Files over 5,000 tokens are truncated to their security-relevant sections
- Binary reduction factors (P0) approximate control impact
- AI-specific control patterns (agentic, LLM) are limited to the general categories
"""


def _inputs_rows(row: Row) -> List[Tuple[str, str, bool]]:
    """One finding's ``### Assessment Inputs`` (contracts/module-signatures.md): ``(field, value, keep slots)`` for each value
    that exists, in the payload's key order. A null field writes no row. The narrative rationales and ``matrix_row`` keep
    their slot tokens, and every other value is escaped whole."""
    item = row.item
    found: List[Tuple[str, str, bool]] = [("control_status", row.control, False), ("control_category", row.control_category, False)]
    if row.confidence is not None:
        found.append(("confidence", row.confidence, False))
    found.append(("carried_forward", "true" if row.carried else "false", False))
    for index, entry in enumerate(item["evidence"]):
        found += [("evidence.%d.%s" % (index, name), str(entry[name]), False) for name in ("file", "line", "language", "snippet", "summary")]
        if "assessment" in entry:
            for dimension in tp.ASSESSMENT_DIMENSIONS:
                address = "evidence.%d.assessment.%s" % (index, dimension)
                found.append((address + ".rating", entry["assessment"][dimension]["rating"], False))
                found.append((address + ".rationale", row.persisted[address + ".rationale"], True))
    found.append(("matrix_row", row.matrix_row, True))
    if item["recommendation_body"] is not None:
        found.append(("recommendation_body", item["recommendation_body"], False))
    return found


def _expected_input(row: Row) -> Dict[str, Any]:
    """What ``parse_controls_assessment_inputs`` must give back for a finding: its validated item as Section 7 persists it."""
    evidence = []
    for index, entry in enumerate(row.item["evidence"]):
        shown: Dict[str, Any] = {name: entry[name] for name in ("file", "line", "language", "snippet", "summary")}
        if "assessment" in entry:
            shown["assessment"] = {dimension: {"rating": entry["assessment"][dimension]["rating"],
                                               "rationale": row.persisted["evidence.%d.assessment.%s.rationale" % (index, dimension)]}
                                   for dimension in tp.ASSESSMENT_DIMENSIONS}
        evidence.append(shown)
    return {"control_status": row.control, "control_category": row.control_category, "confidence": row.confidence, "carried_forward": row.carried,
            "evidence": evidence, "matrix_row": row.matrix_row, "recommendation_body": row.item["recommendation_body"]}


def _md_section_7(run: Run, out: List[str]) -> None:
    flagged = [(row, flag) for row in run.rows for flag in _sorted_flags(row.flags)]
    summary: Dict[Tuple[str, str], int] = {}
    for _row, flag in flagged:
        summary[(flag.kind, flag.cause)] = summary.get((flag.kind, flag.cause), 0) + 1
    out += ["---", "", "## 7. Analysis Integrity", "",
            "What the renderer checked, corrected or could not check, and the control results it keeps for the next run. The control analyzer's "
            "judgments are persisted under Assessment Inputs, so a finding that is carried forward is copied from there and never from the text above.", "",
            "### Integrity Summary", "", "| Kind | Cause | Count |", "|------|-------|-------|"]
    out += ["| %s | %s | %d |" % (kind, tp.escape_cell(cause), summary[(kind, cause)])
            for kind, cause in sorted(summary, key=lambda key: (FLAG_KINDS.index(key[0]) if key[0] in FLAG_KINDS else len(FLAG_KINDS), key[1]))]
    out += ["", "### Finding Flags", "", "| ID | Flag | Field | Cause |", "|----|------|-------|-------|"]
    out += ["| %s | %s | %s | %s |" % (row.finding_id, flag.kind, tp.escape_cell(flag.field), tp.escape_cell(flag.cause)) for row, flag in flagged]
    out += ["", "### Input Issues", ""]
    out += ["- %s" % tp.escape_prose(issue) for issue in run.issues[:rules.ISSUE_LIMIT]] if run.issues else ["None."]
    if len(run.issues) > rules.ISSUE_LIMIT:
        out.append("- %d more issues were not listed" % (len(run.issues) - rules.ISSUE_LIMIT))
    out += ["", "### Assessment Inputs", "", "| ID | Field | Value |", "|----|-------|-------|"]
    for row in run.rows:
        out += ["| %s | %s | %s |" % (row.finding_id, field, tp.escape_cell(value, keep_slots=keep)) for field, value, keep in _inputs_rows(row)]
    out.append("")


def _render_md(run: Run, scoring: str, digest: str) -> str:
    out = _frontmatter(run, scoring)
    out += ["# Compensating Controls Report", ""]
    _md_section_1(run, out, scoring)
    _md_section_2(run, out)
    _md_section_3(run, out)
    _md_section_4(run, out)
    _md_section_5(run, out)
    out += METHODOLOGY.split("\n")
    _md_section_7(run, out)
    out += [tp.stamp_comment(RENDERER, digest), ""]
    return "\n".join(out)


# =============================================================================
# compensating-controls.sarif (T053; ADR-050 D7, D8; contracts/sarif-result.md)
# =============================================================================

CATEGORY_OF_RULE = {rule_id: category for category, rule_id in sc.RULE_ID_BY_CATEGORY.items()}


def _section_4_blocks(md_text: str) -> Dict[str, List[str]]:
    """The lines of each Section 4 block, by canonical ID, block by block under the renderer's own ``#### n. ID — `` headings.

    Section 4 is found as every lookup of this file finds a section: from its exact heading line to the exact heading line of
    Section 5, both outside the code fences (``_lines_of``). A snippet of Section 3 that quotes ``## 4. Recommendations`` and a
    later section heading can't end it early (P0-1; ADR-050 D3, "Finding a section"; T067b H1). A block is the lines after its
    heading, up to the next block's heading, so the last block of a group also holds the group heading that follows it, and every
    reader of a block stops at a heading line. A finding with no block, such as one whose control was found, has no entry.
    """
    blocks: Dict[str, List[str]] = {}
    current: Optional[List[str]] = None
    for line in _lines_of(md_text, SECTION_TITLES[3], SECTION_TITLES[4]):
        heading = re.match(r"#### [0-9]+\. (\S+) %s " % DASH, line)
        if heading is not None:
            current = blocks.setdefault(tp.canonical_finding_id(heading.group(1)), []) if tp.id_matches("finding", heading.group(1)) else None
        elif current is not None:
            current.append(line)
    return blocks


def _section_4_efforts(md_text: str) -> Dict[str, str]:
    """The Effort word (``Low``, ``Medium`` or ``High``) of each Section 4 block, by canonical ID.

    The first line of a block that starts with ``**Effort Estimate**:`` and goes on with one of the three words gives it. A block
    with no such line, and a finding with no block, has none.
    """
    found: Dict[str, str] = {}
    for canonical, lines in _section_4_blocks(md_text).items():
        for line in lines:
            text = line.strip()
            word = EFFORT_WORD.match(text[len(EFFORT_MARKER):].strip()) if text.startswith(EFFORT_MARKER) else None
            if word is not None:
                found[canonical] = word.group(1)
                break
    return found


def _section_4_recommendations(md_text: str) -> Dict[str, str]:
    """The ``recommendation`` of each Section 4 block, by canonical ID: its "What to Implement" text, decoded, read from the block by
    the shared rule (ADR-050 D2: ``parse_compensating_controls_md``'s). A consumer reads the same text in the markdown and in the SARIF.

    The blocks are found in the fence-aware Section 4 (``_section_4_blocks``), not in the whole file as the shipped reader finds its
    own section: a code snippet is raw text, and a line of it that reads like a section heading must not move the section (T067b H1).
    A finding whose control was found has no block, and so no entry.
    """
    return {canonical: tachi_parsers.recommendation_text(lines) for canonical, lines in _section_4_blocks(md_text).items()}


def _recommendation_of_body(body: Optional[str]) -> str:
    """The ``recommendation`` that a validated part's ``recommendation_body`` gives, derived without the rendered file (T067b H1).

    The body goes through the escape that Section 4 writes it with (``escape_prose``) and the shared rule reads it as it reads a block, so
    the value is the one that the file's Section 4 holds for the finding. It is what the from-disk check compares the SARIF with. The SARIF
    is built from the file (``_section_4_recommendations``), so a check that read the file by the same function would pass whatever that
    function did. ``None`` is a finding whose control was found: it has no body and no block, and its recommendation is empty.
    """
    return "" if body is None else tachi_parsers.recommendation_text(tp.escape_prose(body).split("\n"))


def _properties(row: Row, recommendation: str, effort: str) -> Dict[str, Any]:
    """A result's properties: the contracted set, in the 1.1 template's order, and no other key (``contracts/sarif-result.md``).

    The emitter appends the ``correlation-*`` keys of a group member. Scores are strings with one decimal place, and
    ``security-severity`` is the residual score (the markdown's Section 2 shows the same numbers). ``control-carry-forward`` is a
    JSON boolean, the renderer's accepted value. ``control-evidence`` repeats the finding's evidence in its canonical spelling, and an
    entry whose file the resolver refused as the agent wrote it (W3, question 5). ``maestro-layer`` is the value that the scorer file
    writes for the finding (gap B). The flags are always present and sorted.
    """
    return {
        "security-severity": _one(row.residual), "control-status": row.control,
        "control-evidence": [{"file": path, "line": entry["line"], "snippet": entry["snippet"]} for path, entry in zip(row.paths, row.item["evidence"])],
        "control-carry-forward": row.carried, "control-effectiveness": row.effectiveness,
        "inherent-risk": _one(row.inherent), "residual-risk": _one(row.residual), "maestro-layer": row.layer,
        "recommendation": recommendation, "effort-estimate": effort, "integrity-flags": sorted(flag.text() for flag in row.flags)}


def _render_sarif(run: Run, digest: str, md_text: str) -> str:
    """``compensating-controls.sarif`` through the shared emitter: one result for each scored open finding, in Section 2's order.

    The message is the finding's threat text and its control status, and its ``markdown`` is the reference set's mitigation
    (``""`` when there is none, which is still written: P0-8). A correlated finding gets the group's properties and ruling C's
    sentence. ``relatedLocations`` are the finding's evidence in the resolver's spelling, leaving out an entry whose file the resolver
    refused (a result left with none has no key; each location's ``id`` is its entry's index). The level follows the residual band.
    """
    recommendations, efforts = _section_4_recommendations(md_text), _section_4_efforts(md_text)
    results = []
    for row in run.by_residual:
        evidence = [sc.evidence_location(index, CATEGORY_NAME[row.control_category], run.evidence_cache[entry["file"]], entry["line"])
                    for index, entry in row.located]
        results.append(sc.build_result(
            tool=TOOL, finding_id=row.finding_id, message="%s [Control: %s]" % (row.threat, row.control), markdown=row.mitigation,
            level=sc.level_for_band(row.residual_band), uri=run.uri, component=row.component, zone=row.zone, kind=row.kind,
            properties=_properties(row, recommendations.get(row.canon, ""), efforts.get(row.canon, "")),
            correlation=run.assignments.get(row.canon), related_locations=evidence))
    highest: Dict[str, Decimal] = {}
    for row in run.rows:
        highest[row.threat_category] = max(highest.get(row.threat_category, row.residual), row.residual)
    driver = sc.build_driver(SARIF, semantic_version=tp.VERSION, version=tp.VERSION, rules=sc.build_rules(highest),
                             supported=sc.supported_taxonomies())
    return sc.to_json(sc.build_document(driver, sc.TAXONOMIES, results, sc.provenance_stamp(RENDERER, tp.VERSION, digest)))


def _outputs(run: Run, scoring: str, digest: str) -> Dict[str, str]:
    """The files this build writes, by canonical name, in the order they move onto it: the markdown first. The SARIF is built from the
    rendered markdown, so that its recommendations are what the shipped reader reads there."""
    md_text = _render_md(run, scoring, digest)
    return {MD: md_text, SARIF: _render_sarif(run, digest, md_text)}


# =============================================================================
# The staged write and its checks (ADR-050 D4 steps 5 and 6; KB 22)
# =============================================================================

def _lines_matching(text: str, pattern: str) -> List[int]:
    """The 0-based number of every line of ``text`` that ``pattern`` matches outside a code fence, through the one shared fence rule.

    A code snippet is the one raw text in the file, and a line of it that looks like a heading, a control title or a table is not
    one (ADR-050 D3, "Finding a section"). ``match_heading`` finds the first such line, so this looks again after each one.
    """
    found: List[int] = []
    lines = text.split("\n")
    while True:
        offset = found[-1] + 1 if found else 0
        at = tachi_parsers.match_heading(pattern, "\n".join(lines[offset:]), outside_fences=True)
        if at is None:
            return found
        found.append(offset + at)


def _heading_pattern(title: str) -> str:
    """A pattern for the line that is exactly ``title`` (trailing spaces and tabs aside), never one that only starts with it."""
    return r"^%s[ \t]*$" % re.escape(title)


def _lines_of(text: str, start: str, stop: Optional[str]) -> List[str]:
    """The lines of ``text`` from the heading line ``start`` to the heading line ``stop`` (or the end), both found as exact lines
    outside every code fence, so a snippet that quotes a later heading can't end the section early (P0-1, ADR-050 D3)."""
    lines = text.split("\n")
    begin = tachi_parsers.match_heading(_heading_pattern(start), text, outside_fences=True)
    if begin is None:
        return []
    end = tachi_parsers.match_heading(_heading_pattern(stop), "\n".join(lines[begin + 1:]), outside_fences=True) if stop is not None else None
    return lines[begin:len(lines) if end is None else begin + 1 + end]


def _rows_under(text: str, pattern: str) -> Tuple[List[Dict[str, str]], bool]:
    """The first table after the line that ``pattern`` matches in full (an exact heading outside every code fence, never a
    substring), and whether it was found."""
    start = tachi_parsers.match_heading(pattern, text, outside_fences=True)
    if start is None:
        return [], False
    return tachi_parsers.parse_markdown_table(text, start_line=start, keep_bold=True), True


def _check_matrix(run: Run, md_text: str) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
    """Section 2 as it sits on disk: every row once, under its residual band, in order, with the cells it should have.

    Returns ``(problems, [(canonical ID, cells)] in file order)``. Each row is compared cell by cell with ``_section_2_cells``, which
    holds the agent's own text in the cells that PR 1 checks and never fills (R-34). The arithmetic is also re-derived from the row's
    own score cells and the finding's structured status, so a wrong residual or band is found whichever way it got there. The
    status is the structured one because Section 2's Control Status cell is the agent's text, and a flagged mismatch there is not
    an error of this file.
    """
    problems: List[str] = []
    structured = {row.canon: row for row in run.rows}
    expected = {canonical: _section_2_cells(row) for canonical, row in structured.items()}
    read: List[Tuple[str, List[str]]] = []
    for band in BANDS:
        rows, found = _rows_under(md_text, r"^### %s Residual Severity[ \t]*$" % band)
        wanted = [row for row in run.by_residual if row.residual_band == band]
        if found != bool(wanted):
            problems.append("Section 2 %s a %s table" % ("has" if found else "lacks", band))
        for table_row in rows:
            cells = [table_row.get(name, "") for name in K8_HEADER]
            if not tp.id_matches("finding", cells[0]):
                problems.append("Section 2 holds a row whose Threat ID %s is not a finding ID" % ascii(cells[0][:20]))
                continue
            canonical = tp.canonical_finding_id(cells[0])
            read.append((canonical, cells))
            if cells[K8_HEADER.index("Residual Severity")] != band:
                problems.append("%s: its Residual Severity is not the band of the table it sits in" % canonical)
            if canonical not in structured:
                continue   # reported below as an unexpected row
            if cells != expected[canonical]:
                differs = [name for name, got, want in zip(K8_HEADER, cells, expected[canonical]) if got != want]
                problems.append("%s: Section 2 differs from the computed row in %s" % (canonical, ", ".join(differs)))
            inherent, residual = tachi_parsers.parse_score(cells[5]), tachi_parsers.parse_score(cells[9])
            try:
                if inherent is None or residual is None:
                    raise ValueError("not a score")
                if ts.residual_score(inherent, ts.REDUCTION_FACTOR_P0[structured[canonical].control]) != residual \
                        or ts.band(inherent) != cells[6] or ts.band(residual) != cells[10]:
                    problems.append("%s: Section 2's residual or band does not follow from its inherent score and the finding's status" % canonical)
            except (ValueError, TypeError):
                problems.append("%s: a score in Section 2 is not a one-decimal score from 0.0 to 10.0" % canonical)
    got = [canonical for canonical, _cells in read]
    if sorted(got, key=tp.finding_sort_key) != sorted(expected, key=tp.finding_sort_key):
        missing = sorted(set(expected) - set(got), key=tp.finding_sort_key)
        extra = sorted(set(got) - set(expected), key=tp.finding_sort_key)
        problems.append("Section 2 has %d rows for %d scored findings (missing: %s; unexpected: %s)" % (
            len(got), len(expected), ", ".join(missing[:10]) or "none", ", ".join(extra[:10]) or "none"))
    elif got != [row.canon for row in run.by_residual]:
        problems.append("Section 2 is not in residual-descending, S-2 order")
    return problems, read


def _check_totals(run: Run, md_text: str, read: Sequence[Tuple[str, List[str]]]) -> List[str]:
    """Section 1's and Section 5's numbers against the sums of the scores that Section 2 holds on disk, and the counts of the
    structured statuses (KB 22). Every total follows the structured status, never Section 2's own Control Status cell (R-34)."""
    problems: List[str] = []
    scores = [(tachi_parsers.parse_score(cells[5]), tachi_parsers.parse_score(cells[9])) for _canonical, cells in read]
    if any(inherent is None or residual is None for inherent, residual in scores):
        return ["a score in Section 2 is not a number, so its totals can't be checked"]
    inherent_total = sum((inherent for inherent, _r in scores), Decimal("0.0"))
    residual_total = sum((residual for _i, residual in scores), Decimal("0.0"))
    reduction = ts.reduction_percentage(inherent_total, residual_total)
    counts = _status_counts(run)
    section_1 = "\n".join(_lines_of(md_text, SECTION_TITLES[0], SECTION_TITLES[1]))
    summary = re.search(r"(?m)^\*\*([0-9]+)\*\* threats analyzed \| \*\*([0-9]+)\*\* Control Found \| \*\*([0-9]+)\*\* Partial Control \| \*\*([0-9]+)\*\* No Control Found$", section_1)
    if summary is None or [int(each) for each in summary.groups()] != [len(read), counts["found"], counts["partial"], counts["missing"]]:
        problems.append("Section 1's counts are not the counts of the rows")
    shares = ts.largest_remainder(counts)
    coverage = re.search(r"(?m)^\*\*Coverage\*\*: ([0-9]+)% Found \| ([0-9]+)% Partial \| ([0-9]+)% Missing$", section_1)
    if coverage is None or [int(each) for each in coverage.groups()] != [shares["found"], shares["partial"], shares["missing"]]:
        problems.append("Section 1's coverage percentages are not those of the rows")
    reduced = re.search(r"(?m)^\*\*Risk Reduction\*\*: ([0-9.]+) inherent -> ([0-9.]+) residual \(\*\*([0-9.]+)%\*\* reduction\)$", section_1)
    if reduced is None or reduced.groups() != (_one(inherent_total), _one(residual_total), str(reduction)):
        problems.append("Section 1's risk reduction is not the sums of the rows (%s inherent, %s residual)" % (_one(inherent_total), _one(residual_total)))
    distribution, found = _rows_under(section_1, r"^\*\*Coverage Distribution:\*\*[ \t]*$")
    shown = {row.get("Status", ""): (row.get("Count", ""), row.get("Percentage", "")) for row in distribution}
    if not found or any(shown.get(STATUS_CELL[status]) != (str(counts[status]), "%d%%" % shares[status]) for status in STATUS_CELL):
        problems.append("Section 1's coverage table is not the counts of the rows")
    aggregate, found = _rows_under(md_text, r"^### Aggregate Risk Reduction[ \t]*$")
    shown = {row.get("Metric", ""): row.get("Value", "") for row in aggregate}
    if not found or shown != {"Total Inherent Risk Score": _one(inherent_total), "Total Residual Risk Score": _one(residual_total),
                              "Delta": _one(inherent_total - residual_total), "Overall Reduction": "%s%%" % reduction}:
        problems.append("Section 5's aggregate table is not the sums of the rows")
    return problems


def _check_controls_and_recommendations(run: Run, md_text: str) -> List[str]:
    """Section 3 holds one control for each distinct triple. Section 4 holds one block for each partial or missing finding, in order
    and numbered, each under the group of its inherent band, and each with the renderer's own heading and ``Current Status`` line
    (ADR-050 D2, R-34: the cells that the renderer fills). Section 3's lines are found outside the code fences, because a snippet is raw."""
    problems: List[str] = []
    section_3 = "\n".join(_lines_of(md_text, SECTION_TITLES[2], SECTION_TITLES[3]))
    lines_3 = section_3.split("\n")
    titles = [lines_3[number] for number in _lines_matching(section_3, r"^#### ")]
    expected = ["#### %s %s %s" % (control.control_id, DASH, tp.escape_cell(control.row.item["evidence"][control.index]["summary"])) for control in run.controls]
    if sorted(titles) != sorted(expected):
        problems.append("Section 3 has %d control blocks for %d detected controls" % (len(titles), len(expected)))
    found_in = (re.match(r"\*\*Detected in\*\*: `([^`]*)`$", lines_3[number]) for number in _lines_matching(section_3, r"^\*\*Detected in\*\*: "))
    detected = sorted(tachi_parsers.decode_references(match.group(1)) for match in found_in if match)
    if detected != sorted("%s:%d" % (control.path, control.line) for control in run.controls):
        problems.append("Section 3's 'Detected in' lines are not the detected controls")
    section_4 = _lines_of(md_text, SECTION_TITLES[3], SECTION_TITLES[4])   # no raw text here, so no fence can hide a line
    group, shown = None, []
    for at, line in enumerate(section_4):
        if line in GROUP_HEADINGS:
            group = line
        elif line.startswith("#### "):
            shown.append((group, section_4[at:at + 3]))
    wanted = [(GROUP_OF_BAND[row.inherent_band], _block_head(number, row)) for number, row in enumerate(run.recommended, 1)]
    if shown != wanted:
        problems.append("Section 4 does not hold exactly one block for each partial or missing finding, in inherent-descending order, numbered "
                        "without a break, under the group of its inherent band, with the renderer's heading and status line")
    return problems


def _check_persisted(run: Run, md_text: str) -> List[str]:
    """What the next run would read from Section 7, by the reader that run uses (P0-1; KB 22; AR-T3).

    ``parse_controls_assessment_inputs`` finds its heading by an exact line and reads the first table after it, so a line
    of untrusted text that forges a heading or a fence (a code snippet is the one text that stays raw) would give the next
    run another result than the one written, with no warning. Every finding must come back equal to its validated item.
    """
    read = tachi_parsers.parse_controls_assessment_inputs(md_text)
    problems = ["Section 7's Assessment Inputs, line %d: %s" % (error["line"], error["reason"]) for error in read["errors"][:5]]
    expected = {row.canon: _expected_input(row) for row in run.rows}
    if set(read["inputs"]) != set(expected):
        problems.append("the next run would read %d of the %d persisted results (missing: %s)" % (
            len(set(read["inputs"]) & set(expected)), len(expected), _named(sorted(set(expected) - set(read["inputs"]), key=tp.finding_sort_key))))
    changed = sorted((canonical for canonical in set(read["inputs"]) & set(expected) if read["inputs"][canonical] != expected[canonical]), key=tp.finding_sort_key)
    if changed:
        problems.append("the next run would read another result than was written for %d finding(s): %s" % (len(changed), _named(changed)))
    return problems


def _quoted_value(value: Any) -> str:
    """A value for a check message: its ``ascii`` form, cut at 60 characters (a message never carries a model's text whole)."""
    shown = ascii(value)
    return shown if len(shown) <= 60 else shown[:57] + "..."


def _related_pairs(result: Mapping[str, Any]) -> Optional[List[Tuple[Any, Any]]]:
    """``(uri, line)`` of each ``relatedLocations`` entry of a result, in order, or ``None`` when an entry isn't evidence's shape."""
    try:
        return [(shown["physicalLocation"]["artifactLocation"]["uri"], shown["physicalLocation"]["region"]["startLine"])
                for shown in result.get("relatedLocations", [])]
    except (KeyError, TypeError, AttributeError):
        return None


def _check_sarif(run: Run, rendered: str, text: str, md_text: str, matrix: Sequence[Tuple[str, List[str]]], digest: str) -> List[str]:
    """Everything that can be wrong with the staged SARIF as it sits on disk, and with its agreement with the staged markdown.

    The text is the one that was rendered. It is a SARIF document with a driver, results and the provenance stamp. No decoded
    string holds a character that D3's step 10 forbids (the file is ASCII, so only the decoded strings show it: P0-4). The
    shared self-check passes (N/N, the shape and key order, the hashes, the one URI, no RESOLVED finding, correlation). The
    results are in Section 2's order. Each rule is the rule table's, with the highest residual score of its results. Each
    result agrees with the row that Section 2 holds on disk (the scores, the level, ``CF``), with the staged Section 4 (the effort) and
    with the validated part (the recommendation). The recommendation is derived again from the part's own ``recommendation_body``
    (``_recommendation_of_body``) and never read from the file by the function that built the SARIF, because a defect in that reader
    would agree with itself (T067b H1). Its status is the structured one, which a Control Status cell of the agent's own may
    disagree with (R-34, flagged). It carries the evidence, the layer and the flags of its finding.
    """
    problems: List[str] = []
    if text != rendered:
        problems.append("the staged %s is not the text that was rendered" % SARIF)
    try:
        document = json.loads(text)
        content = document["runs"][0]
        results, driver, stamp = content["results"], content["tool"]["driver"], content["properties"]["tachi_provenance"]
        if not (isinstance(results, list) and isinstance(driver, dict) and isinstance(stamp, dict)):
            raise TypeError("a part of the document is not the shape it should be")
    except (ValueError, KeyError, IndexError, TypeError):
        return problems + ["the staged %s is not a SARIF document with a driver, results and a provenance stamp" % SARIF]
    forbidden = _first_forbidden(document)
    if forbidden is not None:
        problems.append("the staged %s holds the character U+%04X, which the part contract forbids, in %s" % (SARIF, ord(forbidden[1]), ascii(forbidden[0])[1:-1]))
    if stamp != {"renderer": RENDERER, "version": tp.VERSION, "input_digest": digest}:
        problems.append("the SARIF's provenance stamp is missing or wrong")
    if (driver.get("name"), driver.get("informationUri"), driver.get("semanticVersion"), driver.get("version")) != (TOOL, sc.INFORMATION_URI, tp.VERSION, tp.VERSION):
        problems.append("the SARIF's driver is not the tool's name, the real informationUri and the release version in both version fields")
    expected = [row.canon for row in run.by_residual]
    try:
        sc.self_check(results, tool=TOOL, member_ids=expected, assignments=run.assignments, resolved_ids=run.resolved_ids, uri=run.uri)
    except sc.SelfCheckError as exc:
        problems += exc.problems[:10]
    by_id: Dict[str, Mapping[str, Any]] = {}
    written: List[str] = []
    for result in results:
        try:
            canonical = tp.canonical_finding_id(result["partialFingerprints"]["findingId/v1"])
            if not isinstance(result["properties"], dict):
                raise TypeError("properties is not an object")
        except (KeyError, ValueError, TypeError):
            continue
        written.append(canonical)
        by_id.setdefault(canonical, result)
    if len(results) != len(run.rows):
        problems.append("the SARIF has %d results for %d scored findings" % (len(results), len(run.rows)))
    elif written != expected and sorted(written, key=tp.finding_sort_key) == sorted(expected, key=tp.finding_sort_key):   # a wrong set is reported above
        problems.append("the SARIF's results are not in Section 2's order (residual descending, then finding ID order)")

    highest: Dict[str, Decimal] = {}   # each rule's highest residual among the results of this file, as the file spells them
    for result in by_id.values():
        category = CATEGORY_OF_RULE.get(result.get("ruleId"))
        score = tachi_parsers.parse_score(result["properties"].get("security-severity")) if category is not None else None
        if score is not None:
            highest[category] = max(highest.get(category, score), score)
    if driver.get("rules") != sc.build_rules(highest):
        problems.append("the SARIF's rules are not the rule table's, one for each category with a result, each with the highest residual of its results")

    cells = dict(matrix)
    efforts = _section_4_efforts(md_text)
    for row in run.rows:
        result, cell = by_id.get(row.canon), cells.get(row.canon)
        if result is None or cell is None:
            continue   # reported above: a row or a result that is missing
        properties = result["properties"]
        recommendation = _recommendation_of_body(row.item["recommendation_body"])   # from the validated part, never from the file (T067b H1)
        effort = efforts.get(row.canon, "")
        evidence = [{"file": path, "line": entry["line"], "snippet": entry["snippet"]} for path, entry in zip(row.paths, row.item["evidence"])]
        wanted_related = [(run.evidence_cache[entry["file"]].uri, entry["line"]) for _index, entry in row.located]   # none for an entry whose file was refused
        pairs = (("security-severity", properties.get("security-severity"), cell[9]), ("residual-risk", properties.get("residual-risk"), cell[9]),
                 ("inherent-risk", properties.get("inherent-risk"), cell[5]),
                 ("control-status", properties.get("control-status"), row.control),
                 ("level", result.get("level"), sc.level_for_band(cell[10])),
                 ("control-carry-forward", properties.get("control-carry-forward"), cell[CF_CELL] == "CF"),
                 ("recommendation", properties.get("recommendation"), recommendation), ("effort-estimate", properties.get("effort-estimate"), effort),
                 ("maestro-layer", properties.get("maestro-layer"), row.layer), ("control-effectiveness", properties.get("control-effectiveness"), row.effectiveness),
                 ("control-evidence", properties.get("control-evidence"), evidence), ("relatedLocations", _related_pairs(result), wanted_related),
                 ("integrity-flags", properties.get("integrity-flags"), sorted(flag.text() for flag in row.flags)))
        for name, in_sarif, wanted in pairs:
            if in_sarif != wanted:
                problems.append("%s: the %s is %s in the SARIF and %s in the markdown or the rows" % (row.canon, name, _quoted_value(in_sarif), _quoted_value(wanted)))
    return problems


def _check_staged(run: Run, rendered: Mapping[str, str], staged: Mapping[str, str], digest: str) -> List[str]:
    """Everything that can be wrong with the files as they now sit on disk. Empty when they are right.

    The markdown is checked against the rows (parity, order, Section 2's arithmetic, the totals of Sections 1 and 5, Sections
    3 and 4), by the readers that consume it (the persisted inputs), for the stamp, and for a character that D3's step 10
    forbids, raw (P0-4). The SARIF is checked on its own and against the markdown's rows (``_check_sarif``): N/N, the shared
    self-check, and the two files' agreement on decoded values.
    """
    md_text = staged[MD]
    problems: List[str] = []
    if md_text != rendered[MD]:
        problems.append("the staged %s is not the text that was rendered" % MD)
    forbidden = tp.forbidden_character(md_text)
    if forbidden is not None:
        problems.append("the staged %s holds the character U+%04X, which the part contract forbids, at line %d"
                        % (MD, ord(forbidden), md_text.count("\n", 0, md_text.find(forbidden)) + 1))
    positions = []
    for title in SECTION_TITLES:
        found = _lines_matching(md_text, _heading_pattern(title))   # outside the code fences: a snippet can quote a heading
        if len(found) != 1:
            problems.append("%s has %d headings" % (title, len(found)))
        else:
            positions.append(found[0])
    if positions != sorted(positions):
        problems.append("the sections are not in order")
    stamp = tp.read_stamp(md_text)
    if stamp is None or (stamp["renderer"], stamp["version"], stamp["input_digest"]) != (RENDERER, tp.VERSION, digest):
        problems.append("the markdown's provenance stamp is missing or wrong")
    elif md_text.rstrip("\n").split("\n")[-1] != tp.stamp_comment(RENDERER, digest):
        problems.append("the provenance stamp is not the last line of the markdown")
    matrix_problems, read = _check_matrix(run, md_text)
    problems += matrix_problems
    problems += _check_totals(run, md_text, read)
    problems += _check_controls_and_recommendations(run, md_text)
    problems += _check_persisted(run, md_text)
    problems += _check_sarif(run, rendered[SARIF], staged[SARIF], md_text, read, digest)
    return problems


def _stage_and_move(run: Run, out: str, plan_id: str, files: Mapping[str, str], digest: str, kept: str) -> None:
    """Write each file to ``staged/``, read it back, check it, and only then move each onto its canonical name."""
    staged_dir = tp.plan_subdir(out, STAGE, plan_id, "staged")
    try:
        if os.path.islink(staged_dir) or (os.path.lexists(staged_dir) and not os.path.isdir(staged_dir)):
            raise RenderError(2, "staged is a symbolic link or not a directory", "remove it and re-run", kept=kept)
        os.makedirs(staged_dir, exist_ok=True)
        for name, text in files.items():
            tp.atomic_write(tp.staged_path(out, STAGE, plan_id, name), text)
    except OSError as exc:
        raise RenderError(4, "the staged files could not be written (%s)" % (exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None
    texts: Dict[str, str] = {}
    for name in files:
        raw, reason = _read_text_file(tp.staged_path(out, STAGE, plan_id, name))
        if raw is None:
            raise RenderError(4, "the staged %s could not be read back (%s)" % (name, reason), RETRY_REMEDY, kept=kept)
        try:
            texts[name] = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise RenderError(4, "the staged %s is not strict UTF-8" % name, RETRY_REMEDY, kept=kept) from None
    problems = _check_staged(run, files, texts, digest)
    if problems:
        raise RenderError(4, "a completeness or parity check failed on the staged files: %s%s" % (
            "; ".join(problems[:5]), "; and %d more" % (len(problems) - 5) if len(problems) > 5 else ""), RETRY_REMEDY, kept=kept)
    for name in files:
        try:
            os.replace(tp.staged_path(out, STAGE, plan_id, name), os.path.join(out, name))
        except OSError as exc:
            raise RenderError(4, "the move of %s onto its canonical name failed (%s)" % (name, exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None


# =============================================================================
# The stage record, the declared-paths check and the summary
# =============================================================================

def _walk(out: str) -> Iterable[Tuple[str, int, int]]:
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


def _undeclared(out: str, plan: Mapping[str, Any]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Paths new or changed since the plan that the stage's grammar doesn't declare (D4), sorted and capped."""
    snapshot = plan["out_snapshot"]
    if snapshot is None:
        return [], [_warning("declared-paths-skipped", "the plan took no snapshot of the output directory")]
    found = sorted(relpath for relpath, size, mtime in _walk(out)
                   if snapshot.get(relpath) != [size, mtime] and not tp.is_declared_path(relpath, STAGE, plan["plan_id"]))
    recordable = [relpath for relpath in found if tp.path_problem(relpath) is None]
    warnings = []
    if len(recordable) != len(found):
        warnings.append(_warning("undeclared-paths-unrecordable", "%d undeclared paths have names a record can't hold" % (len(found) - len(recordable))))
    if len(recordable) > tp.MAX_UNDECLARED_PATHS:
        warnings.append(_warning("undeclared-paths-truncated", "%d undeclared paths in all; the first %d are listed" % (len(recordable), tp.MAX_UNDECLARED_PATHS)))
    return recordable[:tp.MAX_UNDECLARED_PATHS], warnings


def _write_record(run: Run, out: str, plan: Mapping[str, Any], digest: str, files: Iterable[str], kept: str) -> Dict[str, Any]:
    undeclared, extra = _undeclared(out, plan)
    warnings = run.warnings + extra
    # The eighth base count, ``cell_overwrites``, is this renderer's alone and always written, ``0`` included (ADR-050 D2, ruled at W3): the computed
    # Section 2 cells, over every row, that held anything but their own slot token. It is no flag, so it adds to no flag kind's count.
    counts: Dict[str, int] = {"units": plan["unit_count"], "open": len(run.rows), "resolved": run.resolved_count, "rendered": len(run.rows),
                              "parse_errors": len(run.issues), "narrative_fallbacks": run.counts["narrative_fallbacks"],
                              "truncations": run.counts["truncations"], "cell_overwrites": run.overwritten}
    for row in run.rows:
        for flag in row.flags:
            counts[flag.kind] = counts.get(flag.kind, 0) + 1
    events, retries = tp.retry_history(STAGE, out, dict(plan))
    batches = plan["batches"]
    record = {
        "schema": tp.STAGE_RECORD_SCHEMA, "stage": STAGE, "plan_id": plan["plan_id"],
        "status": "success-with-warnings" if warnings or undeclared else "success", "tachi_version": tp.VERSION,
        "started_utc": plan["created_utc"], "finished_utc": _utc_now(), "input_digest": digest, "counts": counts,
        "batches": {"planned": sum(1 for e in batches if e["parent"] is None),
                    "dispatched": sum(1 for e in batches if e["parent"] is None) + plan["retry_budget"]["used"],
                    "done": sum(1 for e in batches if e["state"] == "done"), "retried": plan["retry_budget"]["used"],
                    "split": sum(1 for e in batches if e["state"] == "split"), "exhausted": sum(1 for e in batches if e["state"] == "failed")},
        "overflow_events": events, "retries": retries, "warnings": warnings, "undeclared_paths": undeclared,
        "outputs": [{"path": name, "sha256": tp.file_digest(os.path.join(out, name))} for name in files], "error": None,
    }
    try:
        tp.validate_stage_record(record)
        text = _dump(record)
        if len(text) > tp.MAX_DOCUMENT_BYTES[tp.STAGE_RECORD_SCHEMA]:
            raise tp.PartError("invalid", "the record is over its size cap")
        tp.atomic_write(tp.stage_record_path(out, STAGE, plan["plan_id"]), text)
    except tp.PartError as exc:
        raise RenderError(4, "the stage record this step wrote fails its own contract (%s)" % exc.detail,
                          "report this as a bug in render-compensating-controls.py", kept=kept) from None
    except OSError as exc:
        raise RenderError(4, "the stage record could not be written (%s)" % (exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None
    return record


def _summary(run: Run, files: Iterable[str], record: Mapping[str, Any]) -> List[str]:
    counts = _status_counts(run)
    lines = ["TACHI COMPENSATING-CONTROLS: wrote %s" % " and ".join(files),
             "%d scored findings assessed: %d Control Found, %d Partial Control, %d No Control Found" % (len(run.rows), counts["found"], counts["partial"], counts["missing"]),
             "Risk reduction: %s inherent -> %s residual (%s%% reduction)"
             % (_one(run.inherent_total), _one(run.residual_total), ts.reduction_percentage(run.inherent_total, run.residual_total))]
    if run.carry_forward_count is not None:
        lines.append("%d findings carried forward from the baseline, %d scanned" % (run.carry_forward_count, len(run.rows) - run.carry_forward_count))
    flagged = sum(1 for row in run.rows if row.flags)
    if flagged:
        lines.append("%d findings carry integrity flags (Section 7 lists them)" % flagged)
    if run.overwritten:
        lines.append("%d computed cell(s) of Section 2 held something other than their slot token, and were overwritten" % run.overwritten)
    lines += ["Warning: %s: %s" % (warning["code"], warning["detail"]) for warning in record["warnings"]]
    if record["undeclared_paths"]:
        lines.append("Warning: %d paths under --out are not declared by the stage: %s" % (
            len(record["undeclared_paths"]), ", ".join(record["undeclared_paths"][:5])))
    return lines


# =============================================================================
# The command line
# =============================================================================

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=RENDERER, description="Render compensating-controls.md from the control analyzer's parts (F-374).")
    parser.add_argument("--version", action="version", version="%s %s (python %s)" % (RENDERER, tp.VERSION, platform.python_version()))
    parser.add_argument("--out", required=True, help="the run's output directory; everything is written under it")
    parser.add_argument("--plan", required=True, help="the plan ID that plan printed")
    parser.add_argument("--plan-digest", required=True, help="the plan_digest that the last plan or reconcile printed")
    return parser


def _run(args: argparse.Namespace) -> int:
    out = os.path.abspath(os.fspath(args.out))
    if not os.path.isdir(out):
        raise RenderError(1, "--out is not a directory", "create it or correct --out")
    if not tp.id_matches("plan", args.plan):
        raise RenderError(2, "--plan is not a plan ID", "pass the plan ID that plan printed")
    if re.fullmatch(r"[0-9a-f]{64}", args.plan_digest, re.ASCII) is None:
        raise RenderError(2, "--plan-digest is not a SHA-256 in lowercase hex", "pass the digest that the last plan or reconcile printed")
    kept = tp.plan_dir(out, STAGE, args.plan)

    plan, inputs, refs = _load_plan(out, args.plan, args.plan_digest)
    try:
        scoring_date = ts.parse_date(plan["params"].get("scoring_date"))
    except ValueError:
        raise RenderError(2, "the plan has no valid scoring date", "re-run the command", kept=kept) from None
    items, part_flags, part_counts = _read_parts(out, plan)

    run = Run()
    run.counts.update(part_counts)
    members = _prepare(run, plan, inputs, refs, kept)
    _score(run, members, items, part_flags, kept)
    accepted = [items[key] for key in sorted(items, key=tp.finding_sort_key) if key in run.open_ids]
    digest = tp.input_digest({"sources": run.sources, "params": plan["params"], "items": accepted, "fragments": []})

    files = _outputs(run, scoring_date.isoformat(), digest)
    _stage_and_move(run, out, args.plan, files, digest, kept)
    record = _write_record(run, out, plan, digest, files, kept)
    for line in _summary(run, files, record):
        print(line)
    return 5 if record["status"] == "success-with-warnings" else 0


def _defect(exc: Exception, kept: Optional[str]) -> RenderError:
    """An exception that no check meant to raise is a bug in this script (or a hostile input it didn't expect): name it."""
    frame = exc.__traceback__
    while frame is not None and frame.tb_next is not None:
        frame = frame.tb_next
    where = "%s:%d" % (os.path.basename(frame.tb_frame.f_code.co_filename), frame.tb_lineno) if frame is not None else "unknown"
    detail = "".join(char if char.isprintable() else " " for char in str(exc))[:200]
    return RenderError(4, "an unexpected error stopped the render (%s: %s, at %s)" % (type(exc).__name__, detail, where),
                       "report this as a bug in render-compensating-controls.py; the earlier outputs were left or put back as they were", kept=kept)


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return _run(args)
    except RenderError as exc:
        sys.stderr.write(exc.text() + "\n")
        return exc.code
    except Exception as exc:  # the D4 message, so the command's Step F runs on a defect too
        failure = _defect(exc, tp.plan_dir(os.path.abspath(args.out), STAGE, args.plan) if tp.id_matches("plan", args.plan) else None)
        sys.stderr.write(failure.text() + "\n")
        return failure.code


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_runtime_floor_374.py, test_write_confinement.py)
    raise SystemExit(main())
