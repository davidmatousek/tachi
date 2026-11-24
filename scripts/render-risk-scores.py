#!/usr/bin/env python3
"""Render ``risk-scores.md`` and ``risk-scores.sarif`` from the scorer's part files (F-374; ADR-050 D1, D2, D4, D9).

The scorer agent writes judgment only: a CVSS vector, eight sub-scores, the reachability inputs and prose. This
script computes everything else and writes both whole files, so that no number, band, total or identity in them is
a model's. It runs once, in the main session, after ``tachi-stage.py reconcile`` exits 0:

    python3 scripts/render-risk-scores.py --out DIR --plan ID --plan-digest HEX

The order is D4's. It runs the CVSS self-test, checks the plan (its digest, the pointer, every input and batch
input), re-validates every part it reads, refuses a value that it takes from ``threats.md``, ``threats.sarif`` or the
baseline (``risk-scores.md`` and its SARIF) if the value holds a character that D3's step 10 forbids, computes the
rows, and writes both files to ``<plan_id>/staged/``. It reads the staged files back from disk and checks row parity
against the reference set, SARIF N/N, that the two files agree on decoded values, that the reader the next run uses
(``read_baseline_scores``) reads every open row back as it was written, and that neither file holds a character that
step 10 forbids. Only when every check passes does it move each staged file onto its canonical name with
``os.replace``. It then runs the declared-paths check and writes the stage record. A check that fails leaves the
canonical files untouched.

Which findings the agent scored is the planner's partition, ``tachi_scoring_rules.route_scorer_units``, and this
script calls the same function: an UNCHANGED finding with a usable baseline row is carried (its inputs, owner and
SLA come from the baseline, and everything derived is recomputed), any other peer copies its group's primary, and
the rest come from the parts. The reference set is ``threats.md``; when the plan reads ``threats.sarif`` instead
(D8's fallback) the member set and each finding's text come from that file.

Exit codes are ``contracts/cli.md``'s: 0 done, 1 an input is missing or unreadable, 2 a validation, usage or guard
failure (a digest or pointer mismatch, a part that fails re-validation, a forbidden character in an input), 4 a
completeness or parity check failed or a file could not be written, 5 done with warnings. A failure prints D4's
four-line message on stderr and writes nothing but what is already staged; ``tachi-stage.py fail`` writes the failed
record and puts earlier outputs back.
The summary lines on stdout are the command's Step 6, so the model restates no number.

Nothing here reads the clock except the stage record's ``finished_utc``, and the scoring date is the plan's. The
renderer never rewrites ``plan.json``. Standard library plus the shared helpers, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("render-risk-scores.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import datetime
import importlib.util
import json
import os
import platform
import re
import stat
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
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

STAGE = "risk-score"
RENDERER = "render-risk-scores.py"  # the stamp's name: the installed file name, as a literal (contracts/cli.md)
MD, SARIF = "risk-scores.md", "risk-scores.sarif"
TOOL = sc.TOOL_NAMES[SARIF]
SCHEMA_VERSION = "1.1"
DASH = "—"
WEIGHTS_TEXT = "0.35/0.30/0.15/0.20"
RETRY_REMEDY = "re-run the command; the earlier outputs were left or put back as they were"

# Section 2 and 2a: the widths at which output-formatting.md shortens a name and a threat (before escaping).
COMPONENT_WIDTH, THREAT_WIDTH = 30, 60

# The kinds of a flag, in the fixed order that Section 2's Flags column and Section 6 list them (D9).
FLAG_KINDS = ("corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input")

METRIC_LABELS = (
    ("AV", "Attack Vector (AV)"), ("AC", "Attack Complexity (AC)"), ("PR", "Privileges Required (PR)"),
    ("UI", "User Interaction (UI)"), ("S", "Scope (S)"), ("C", "Confidentiality (C)"), ("I", "Integrity (I)"),
    ("A", "Availability (A)"))
METRIC_VALUES = {
    "AV": {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"},
    "AC": {"L": "Low", "H": "High"},
    "PR": {"N": "None", "L": "Low", "H": "High"},
    "UI": {"N": "None", "R": "Required"},
    "S": {"U": "Unchanged", "C": "Changed"},
    "C": {"N": "None", "L": "Low", "H": "High"},
    "I": {"N": "None", "L": "Low", "H": "High"},
    "A": {"N": "None", "L": "Low", "H": "High"},
}
SUBSCORE_LABELS = {
    "known_techniques": "Known Techniques", "attack_complexity": "Attack Complexity",
    "tooling_availability": "Tooling Availability", "skill_level": "Skill Level", "scriptability": "Scriptability",
    "target_scope": "Target Scope", "resource_requirements": "Resource Requirements",
    "detection_difficulty": "Detection Difficulty"}
RATIONALE_KEYS = ("cvss", "exploitability", "scalability", "reachability")

# What each rule says in risk-scores.sarif, copied from the template (templates/tachi/output-schemas/risk-scores.sarif)
# in that file's order: (category, short description, full description, tags, taxonomy IDs the rule relates to). The IDs
# are what a ``{{ref:...}}`` slot may cite for a finding of that category (ADR-050 D3's table); they are not emitted.
RULES = (
    ("spoofing", "Identity spoofing threats",
     "Threats where an attacker pretends to be something or someone else, such as forging authentication credentials, "
     "replaying tokens, or impersonating trusted components to gain unauthorized access.",
     ("security", "stride", "spoofing", "authentication", "owasp", "cwe"), ("A07", "CWE-287")),
    ("tampering", "Data tampering threats",
     "Threats where an attacker modifies data, code, or configuration without authorization, violating integrity "
     "guarantees and causing systems to operate on corrupted inputs or persist falsified records.",
     ("security", "stride", "tampering", "data-integrity", "owasp", "cwe"), ("A08", "CWE-345")),
    ("repudiation", "Repudiation threats",
     "Threats where a user or system can deny having performed an action, and the system lacks sufficient evidence to "
     "prove otherwise, undermining accountability and forensic investigation.",
     ("security", "stride", "repudiation", "logging", "accountability", "owasp", "cwe"), ("A09", "CWE-778")),
    ("info-disclosure", "Information disclosure threats",
     "Threats where sensitive information is exposed to unauthorized parties through direct data leaks, verbose error "
     "messages, side-channel observations, or insufficient access controls on stored data.",
     ("security", "stride", "information-disclosure", "data-exposure", "owasp", "cwe"), ("A01", "CWE-200")),
    ("denial-of-service", "Denial of service threats",
     "Threats where an attacker degrades or eliminates system availability through resource exhaustion, flooding, "
     "algorithmic complexity exploitation, or cascading dependency failures.",
     ("security", "stride", "denial-of-service", "availability", "owasp", "cwe"), ("A05", "CWE-400")),
    ("privilege-escalation", "Privilege escalation threats",
     "Threats where an attacker gains higher privileges than authorized, performing actions reserved for "
     "administrators, accessing other users' resources, or bypassing access control boundaries.",
     ("security", "stride", "elevation-of-privilege", "access-control", "owasp", "cwe"), ("A01", "CWE-269")),
    ("agentic", "AI agent autonomy and misuse threats",
     "Threats arising from autonomous agent behavior, including uncontrolled tool use, excessive autonomy, "
     "agent-to-agent trust violations, and lack of human oversight in high-impact operations.",
     ("security", "ai", "agentic", "autonomy", "tool-use", "mcp"), ("CWE-693",)),
    ("llm", "LLM-specific threats",
     "Threats from prompt injection vulnerabilities, data poisoning risks, and model theft in LLM-integrated "
     "components, covering direct and indirect injection, RAG pipeline manipulation, and model extraction.",
     ("security", "ai", "llm", "prompt-injection", "data-poisoning", "model-theft"), ("CWE-74",)),
)
RULE_BY_CATEGORY = {entry[0]: entry for entry in RULES}

KIND_OF_DFD_TYPE = {"External Entity": "external-entity", "Process": "process", "Data Store": "data"}
# The reverse, for D8's fallback: the ``kind`` of a ``threats.sarif`` result's logical location, back to a DFD type.
# ``threats.sarif`` writes ``data-store`` where this file writes ``data``, so both name a Data Store.
DFD_TYPE_OF_KIND = dict({kind: dfd_type for dfd_type, kind in KIND_OF_DFD_TYPE.items()}, **{"data-store": "Data Store"})

# ``trust-zones.md`` section 2c: a §2 label names a trust level when it matches a canonical value, or when its
# keywords all point to one level. The words are matched after any ``untrusted`` or ``semi-trusted`` is taken out of
# the text for the Trusted level, so the "trust" inside them doesn't count there.
_TRUST_CANONICAL = {"untrusted": "Untrusted", "semi-trusted": "Semi-Trusted", "semi trusted": "Semi-Trusted", "trusted": "Trusted"}
_TRUST_WORDS = (("Untrusted", ("untrust", "external", "public", "internet", "unauth")),
                ("Semi-Trusted", ("semi", "dmz", "perimeter", "gateway", "partial")),
                ("Trusted", ("trust", "internal", "private", "backend", "core")))
_TRUST_PREFIXED = re.compile(r"un-?trust\w*|semi[- ]?trust\w*")
_LAYER = re.compile(r"L[1-7](?![0-9])", re.ASCII)

_populator: Any = None


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
        lines = ["TACHI RISK-SCORE FAILED: %s" % self.reason]
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


def _grid(value: Optional[Decimal]) -> Decimal:
    """A stored legacy value as a score on the 0.1 grid inside 0.0 to 10.0, so the arithmetic can take it."""
    if value is None:
        return Decimal("0.0")
    return ts.q1(max(Decimal("0.0"), min(Decimal("10.0"), value)))


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
    units (every finding carried) keeps its architecture path (ruled at W2, part-files.md §4). Nothing is written.
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
    return plan, inputs, dict(plan["refs"])   # validate_plan requires refs, and no script reads a path from a batch input (W2 ruling 2, P0-7)


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
# Rows and flags
# =============================================================================

class Flag(object):
    """One integrity flag, ``kind:field:cause``, with the stored and rendered values that Section 6's table shows.

    A value that isn't there is ``None``: the table writes a dash for it and the SARIF's ``score-corrections`` writes null.
    """

    def __init__(self, kind: str, field: str, cause: str, stored: Optional[str] = None, rendered: Optional[str] = None) -> None:
        self.kind, self.field, self.cause, self.stored, self.rendered = kind, field, cause, stored, rendered

    def text(self) -> str:
        return "%s:%s:%s" % (self.kind, self.field, self.cause)


def _flag_from_text(text: str) -> Flag:
    kind, _, rest = text.partition(":")
    field, _, cause = rest.rpartition(":")
    return Flag(kind, field, cause)


class Row(object):
    """One open finding, as rendered: the reference set's identity, its computed values and its governance."""

    def __init__(self, finding_id: str, component: str, threat: str, mitigation: str, risk_level: str, layer: str, kind: str,
                 status: str, attribution: Tuple[str, ...] = ()) -> None:
        self.finding_id = finding_id
        self.canon = tp.canonical_finding_id(finding_id)
        self.component, self.threat, self.mitigation, self.risk_level = component, threat, mitigation, risk_level
        self.category = ts.category_for_prefix(self.canon.partition("-")[0])
        self.layer, self.kind, self.status, self.attribution = layer, kind, status, attribution
        self.source = "fresh"
        self.vector: Optional[str] = None
        self.cvss = self.exploit = self.scale = self.reach = self.composite = Decimal("0.0")
        self.band = "Low"
        self.subs: Optional[Dict[str, int]] = None
        self.zone: Optional[str] = None
        self.trust: Optional[str] = None
        self.auth: Optional[int] = None
        self.net: Optional[int] = None
        self.tags: Tuple[str, ...] = ()
        self.bounds: Optional[Tuple[Decimal, Decimal]] = None
        self.scored_on: Optional[datetime.date] = None
        self.owner, self.sla, self.disposition, self.review_date = "Unassigned", "", "", ""
        self.legacy_prose: Dict[str, str] = {}  # field -> a legacy baseline's prose (evidence-class, never resolved)
        self.persisted: Dict[str, str] = {}   # field -> the validated, slotted text that Section 6 carries
        self.cell_text: Dict[str, str] = {}   # field -> the text resolved for a table cell
        self.prose_text: Dict[str, str] = {}  # field -> the text resolved for prose
        self.flags: List[Flag] = []
        self.defaulted_reach = False
        self.copied = False                    # a peer that took its primary's scores


class Run(object):
    """Everything one render reads and computes. Plain attributes, filled by ``_prepare`` and ``_score``."""

    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.warnings: List[Dict[str, str]] = []
        self.issues: List[str] = []
        self.sources: Dict[str, str] = {}
        self.counts: Dict[str, int] = {"narrative_fallbacks": 0, "truncations": 0}
        self.rows: List[Row] = []
        self.ordered: List[Row] = []
        self.resolved: List[Dict[str, Any]] = []
        self.groups: List[Dict[str, Any]] = []      # every group, a fallback group with no ID (D8) included: its peers still route
        self.assignments: Dict[str, Any] = {}       # the emitter's roles, for the groups that have an ID only
        self.baseline: Any = None
        self.baseline_path: Optional[str] = None
        self.baseline_note = "none"
        self.baseline_vectors: Dict[str, str] = {}  # canonical ID -> the baseline SARIF's ``cvss-vector`` (the second source, R-26)
        self.lacking: Dict[str, List[str]] = {}     # canonical ID -> the values its input's form lacks (S-12(b))
        self.routing: Any = None
        self.tag_source: Any = None
        self.tag_line = "none"
        self.zones: Dict[str, Tuple[str, str]] = {}
        self.component_zone: Dict[str, str] = {}
        self.component_info: Dict[str, Tuple[str, str]] = {}
        self.finding_layer: Dict[str, str] = {}
        self.spelling: Dict[str, str] = {}
        self.open_ids: set = set()
        self.threats_text: Optional[str] = None
        self.threats_path = ""
        self.source_file: Optional[str] = None
        self.uri = ""
        self.normalized = 0

    def warn(self, code: str, detail: str) -> None:
        self.warnings.append(_warning(code, detail))


# =============================================================================
# Forbidden characters in what an input holds (NFR-10, P0-4)
# =============================================================================

def _first_forbidden(value: Any, path: str = "") -> Optional[Tuple[str, str]]:
    """``(path, character)`` of the first string under ``value`` that holds a character D3's step 10 forbids, or ``None``.

    Text, mapping keys, list and tuple items and the fields of a plain object (a ``BaselineRow``) are searched in order.
    A number, a date or ``None`` holds no text. ``path`` is dotted, and is for a message only. The character set is
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

    Step 10 checks a part. Text from ``threats.md``, the baseline ``risk-scores.md`` or ``threats.sarif`` reaches the
    escapers unchecked, and a carriage return, an escape or a bidi control would then forge a heading, drive a terminal
    or reorder what a reader sees (NFR-10, P0-4). So each value is checked where it is taken, before anything is computed.
    ``finding_id`` names the finding the value belongs to, and ``None`` a Section 1 or 2 name or label. The message gives
    the character's code point and never the text, so it can't carry the character to a terminal.
    """
    found = _first_forbidden(value)
    if found is not None:
        where = "the %s of %s" % (ascii(found[0])[1:-1], finding_id) if finding_id else "a component, zone or layer name"
        raise RenderError(2, "%s holds the character U+%04X, which the part contract forbids, in %s" % (source, ord(found[1]), where),
                          remedy, kept=kept)


def _refuse_forbidden_inputs(run: Run, reference: Mapping[str, Any], source: str, kept: str) -> None:
    """The refusal for what ``threats.md`` gives the renderer, or ``threats.sarif`` in D8's fallback.

    That is every finding's fields (open and RESOLVED), each finding's MAESTRO layer, and the names and labels of
    Sections 1 and 2. It runs once those are read and before any of them is used. The reader strips a cell's edges
    first, so a character that ``str.strip`` removes there never reaches this check, as it never reaches an output.
    """
    remedy = "regenerate %s with /tachi.threat-model, or edit the value to remove the character, then re-run the command" % source
    for finding in list(reference["open"]) + list(reference["resolved"]):
        _refuse_forbidden(source, finding["id"], finding, remedy, kept)
    for canonical, layer in run.finding_layer.items():
        _refuse_forbidden(source, canonical, {"layer": layer}, remedy, kept)
    _refuse_forbidden(source, None, (run.component_info, run.zones, run.component_zone), remedy, kept)


def _refuse_forbidden_baseline(run: Run, reference: Mapping[str, Any], kept: str) -> None:
    """The same refusal for the baseline's rows of the findings that this run lists, open or RESOLVED: the rows it takes values from.

    A row of a finding that this run no longer lists is never read into an output, so it isn't checked. The baseline SARIF's
    vectors are checked too: they are the second source of a vector (R-26), and Section 6 shows one when the two disagree.
    """
    listed = {tp.canonical_finding_id(finding["id"]) for finding in list(reference["open"]) + list(reference["resolved"])}
    remedy = "edit that value in the baseline to remove the character, then re-run the command"
    for rows in (run.baseline.rows, run.baseline.resolved_rows):
        for canonical in sorted(listed & set(rows), key=tp.finding_sort_key):
            _refuse_forbidden("the baseline " + MD, canonical, rows[canonical], remedy, kept)
    for canonical in sorted(listed & set(run.baseline_vectors), key=tp.finding_sort_key):
        _refuse_forbidden("the baseline " + SARIF, canonical, {"cvss-vector": run.baseline_vectors[canonical]}, remedy, kept)


# =============================================================================
# The inputs: the reference set, §1 and §2 of threats.md, the architecture file, the baseline, the asset tags
# =============================================================================

def _loaded_populator() -> Any:
    """``populate-affected-assets.py``, loaded by path for its ``match_component`` (ADR-050 D2: S-13's one tag join)."""
    global _populator
    if _populator is None:
        path = os.path.join(SCRIPTS_DIR, "populate-affected-assets.py")
        if not os.path.isfile(path):
            raise RenderError(1, "scripts/populate-affected-assets.py is not installed",
                              "run scripts/install.sh to install the tachi scripts, then re-run the command")
        spec = importlib.util.spec_from_file_location("populate_affected_assets_for_render", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _populator = module
    return _populator


def _label_level(label: str) -> Optional[str]:
    """The trust level a §2 label names, or ``None`` when it names none or more than one (``trust-zones.md`` 2c)."""
    text = " ".join(label.casefold().split())
    if text in _TRUST_CANONICAL:
        return _TRUST_CANONICAL[text]
    bare = _TRUST_PREFIXED.sub(" ", text)
    hits = [level for level, words in _TRUST_WORDS if any(word in (bare if level == "Trusted" else text) for word in words)]
    return hits[0] if len(hits) == 1 else None


def _relative(path: str, cwd: str) -> Optional[str]:
    """``path`` relative to the working directory with ``/`` separators, or ``None`` when it isn't under it.

    The working directory is found by file identity, as ``under`` finds it, so a path that is spelled through a symbolic
    link (macOS's ``/var`` for ``/private/var``) still reads as the tail below the directory, never as a ``..`` climb.
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
    """A regular file's bytes through no link, or ``(None, reason)``. The architecture file and the staged files use it."""
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


def _delta_status(finding: Mapping[str, Any]) -> str:
    """A finding's delta status as the planner reads it: a row without a usable one counts as NEW."""
    status = tachi_parsers.normalize_delta_status(finding["delta_status"]) if isinstance(finding.get("delta_status"), str) else ""
    return status if status in ("NEW", "UPDATED", "UNCHANGED") else "NEW"


def _risk_level(level: Optional[str]) -> str:
    """The "Original Risk Level" of a fallback member (D8, P0-3), from what its result holds: ``properties.risk_level``, else ``security-severity``.

    A word (``Critical``, ``Note``) stays as written. A score, which is all that ``security-severity`` ever is, becomes
    its severity band through ``tachi_scoring.band``, after the score is put on the 0.1 grid inside 0.0 to 10.0 that the
    band function takes. That function has four bands, so a score under 1.0 is Low and never Note. A result with neither
    a level nor a score gets a dash.
    """
    if level is None:
        return DASH
    score = tachi_parsers.parse_score(level)
    return level if score is None else ts.band(_grid(score))


def _sarif_reference(text: str) -> Dict[str, Any]:
    """The reference set of a plan that read ``threats.sarif`` (D8's fallback): each finding's text from its own result.

    The member set, the groups and each member's details are ``parse_sarif_member_set(..., with_details=True)``'s, the one
    reader that the planner uses too, so both sides see the same findings and the same groups. A result gives its
    component, threat, mitigation, risk level, layer and DFD kind whichever ID form it uses (``findingId/v1``, else
    ``properties.id``), and a value it lacks is empty (the risk level is a dash). An ID that only a legacy peer reference
    names has no result, so its text is empty. A group the file names no ID for stays in ``groups`` with a ``None`` ID,
    because its peers still route (``_prepare`` passes only the named ones to the emitter). There are no RESOLVED
    findings: a result that is ``absent`` is dropped, and nothing here lists a resolved one. Nothing is stripped or
    escaped here, so that ``_refuse_forbidden_inputs`` sees each value as the file wrote it (P0-4).
    """
    found = tachi_parsers.parse_sarif_member_set(text, with_details=True)
    rows = []
    for member in sorted(found["members"], key=tp.finding_sort_key):
        own = found["details"].get(member, {})
        rows.append({"id": member, "component": own.get("component") or "", "type": DFD_TYPE_OF_KIND.get(own.get("kind"), ""),
                     "threat": own.get("threat") or "", "mitigation": own.get("mitigation") or "",
                     "risk_level": _risk_level(own.get("risk_level")), "layer": own.get("layer") or "", "agentic_pattern": "none"})
    lacking = {row["id"]: ["delta_status"] for row in rows}  # S-12(b): the file has no place for a status, on any member
    return {"open": rows, "resolved": [], "duplicates": [], "groups": found["groups"],
            "lacking": lacking, "flags": {finding_id: [tachi_parsers.FORM_LACKS_FLAG % "delta_status"] for finding_id in lacking}}


def _prepare(run: Run, plan: Mapping[str, Any], inputs: Mapping[str, bytes], refs: Mapping[str, str], kept: str) -> Dict[str, Any]:
    """Read the reference set and everything around it. Returns the reference set; fills ``run``."""
    if "threats" not in inputs:
        raise RenderError(2, "the plan names no threats.md input", "re-run the command with a threats.md", kept=kept)
    try:
        text = inputs["threats"].decode("utf-8")
    except UnicodeDecodeError:
        raise RenderError(2, "the threat model input is not strict UTF-8", "regenerate threats.md with /tachi.threat-model", kept=kept) from None
    refused = plan.get("architecture_warning")   # D7: the planner refused the --architecture candidate, and the record lists that first
    if isinstance(refused, dict):
        run.warn(refused["code"], refused["detail"])
    run.threats_path = plan["inputs"]["threats"]["path"]
    run.source_file = _relative(run.threats_path, run.cwd)
    run.sources = {name: entry["sha256"] for name, entry in sorted(plan["inputs"].items())}
    from_sarif = os.path.basename(run.threats_path) == "threats.sarif"
    if from_sarif:
        try:
            reference = _sarif_reference(text)
        except ValueError as exc:
            raise RenderError(2, "threats.sarif holds no findings to score: %s" % str(exc)[:200], "regenerate it with /tachi.threat-model", kept=kept) from None
    else:
        run.threats_text = text
        try:
            reference = tachi_parsers.parse_reference_set(text)
        except tachi_parsers.ReferenceSetError as exc:
            raise RenderError(2, "%s. Expected %s" % (exc.reason, exc.expected), exc.remedy, kept=kept) from None

    lacking = reference.get("lacking", {})
    if lacking:   # S-12(b): each such finding carries the flags, and the stage record lists them
        names = sorted({name for found in lacking.values() for name in found})
        where = "threats.sarif (the fallback input)" if from_sarif else "Section 7 of threats.md (the %s form)" % reference["form"]
        run.issues.append("%s lacks %s for %d of %d findings: each carries the flag %s%s" % (
            where, ", ".join(names), len(lacking), len(reference["open"]), ", ".join(tachi_parsers.FORM_LACKS_FLAG % name for name in names),
            ". A status that the input lacks is taken from the baseline when it holds the finding, and is NEW otherwise" if "delta_status" in names else ""))
        run.warn("value-not-in-form", "%s lacks %s for %d findings, such as %s"
                 % (where, ", ".join(names), len(lacking), ", ".join(sorted(lacking, key=tp.finding_sort_key)[:5])))
    for canonical in reference["duplicates"]:
        run.issues.append("Section 7 or Section 4c of threats.md lists %s more than once: the first row is used, and an open row "
                          "beats a resolved one" % canonical)
    if reference["duplicates"]:
        run.warn("duplicate-finding-id", "threats.md lists these findings more than once, and the first row of each is used: %s"
                 % ", ".join(reference["duplicates"]))

    open_ids = [tp.canonical_finding_id(row["id"]) for row in reference["open"]]
    if from_sarif:
        for row in reference["open"]:
            run.component_info.setdefault(row["component"], (row["type"], row["layer"]))
            run.finding_layer.setdefault(tp.canonical_finding_id(row["id"]), row["layer"])
        run.groups = reference["groups"]
    else:
        for row in tachi_parsers.parse_markdown_table(text, "### Components"):
            name = row.get("Component", "").strip()
            if name and name not in run.component_info:
                run.component_info[name] = (row.get("Type", "").strip(), row.get("MAESTRO Layer", "").strip())
        for row in tachi_parsers.parse_markdown_table(text, tachi_parsers.REFERENCE_SET_SECTION):
            finding_id = row.get("Finding ID", "").strip()
            if tp.id_matches("finding", finding_id):
                run.finding_layer.setdefault(tp.canonical_finding_id(finding_id), row.get("MAESTRO Layer", "").strip())
        for zone_row in tachi_parsers.parse_scope_data(text)["trust_boundaries"]:
            zone, label = zone_row["zone"], zone_row["trust-level"]
            if not zone:
                continue
            run.zones.setdefault(zone, (zone, label))
            for member in (part.strip() for part in zone_row["components"].split(",")):
                if member:
                    run.component_zone.setdefault(member.casefold(), zone)
        grouped = tachi_parsers.parse_correlation_groups(text, member_ids=open_ids)
        for problem in grouped["errors"]:
            run.issues.append("Section 4a of threats.md, line %d: the row %s %s, so it is skipped" % (problem["line"], repr(problem["row"][:60]), problem["reason"]))
        run.groups = grouped["groups"]
    _refuse_forbidden_inputs(run, reference, os.path.basename(run.threats_path), kept)   # NFR-10: a value from an input is checked where it is taken
    # D8 (P0-3): only a group with an ID reaches the emitter, whose role assignment, ``correlation-*`` properties and ruling C's
    # sentence all name it. A group the SARIF names no ID for (``group_id`` is ``None``) still routes its peers through
    # ``run.groups`` (copy and divergence, D9), and the record counts it. No ID is invented.
    named = [(group["group_id"], group["members"]) for group in run.groups if group["group_id"] is not None]
    if len(named) != len(run.groups):
        run.warn("correlation-group-unnamed", "%s gives no group ID to %d of its %d correlation groups, so their members carry no correlation "
                 "properties and no correlation sentence. Their peers are still peers: a new or updated one copies its primary, and a "
                 "carried one is compared with it" % (os.path.basename(run.threats_path), len(run.groups) - len(named), len(run.groups)))
    run.assignments = sc.correlation_assignments(named, open_ids)

    # The baseline first: S-12(b) needs it to route and to supply a carried finding's component before the tag join.
    run.lacking = {finding_id: list(names) for finding_id, names in reference.get("lacking", {}).items()}
    _prepare_baseline(run, plan, refs, text if run.threats_text is not None else None, inputs)
    if run.baseline is not None:
        _refuse_forbidden_baseline(run, reference, kept)
    run.routing = _route(run, reference)
    _supply(run, reference)

    # The architecture file: the one path that gives the URI and the asset tags (ADR-050 D7, and D2's S-13).
    resolution = sc.resolve_architecture(refs.get("architecture"), threats_text=run.threats_text, run_dir=os.path.dirname(run.threats_path), root=run.cwd)
    run.uri = resolution.uri
    for found in resolution.warnings:
        run.warn(found["code"], found["detail"])
    architecture_text: Optional[str] = None
    if resolution.source != "default-literal":
        raw, reason = _read_text_file(os.path.join(run.cwd, resolution.path))
        if raw is not None:
            try:
                architecture_text = raw.decode("utf-8")
                run.sources["architecture"] = tp.sha256_hex(raw)
            except UnicodeDecodeError:
                reason = "not-utf8"
        if architecture_text is None:
            run.warn("architecture-unreadable", "the architecture file could not be read (%s), so its asset tags were not used" % reason)
    block = sc.parse_affected_assets(text) if run.threats_text is not None else {}
    recomputed = None
    if architecture_text is not None:
        recomputed = rules.recompute_tags(architecture_text, [{"id": row["id"], "component": row["component"]} for row in reference["open"]],
                                          _loaded_populator().match_component)
    run.tag_source = rules.select_tag_source(open_ids=open_ids, block=block, recomputed=recomputed)
    if run.tag_source.warning:
        run.warn("tag-source:%s" % run.tag_source.cause, run.tag_source.warning)
    run.tag_line = {
        "block": "the Affected Assets block of threats.md, which equals the architecture file's own tags",
        "recomputed": "the architecture file's own tags (the Affected Assets block of threats.md was not used: %s)" % (run.tag_source.cause or ""),
        "block-unverified": "the Affected Assets block of threats.md, unverified because there was no architecture file to check it against",
        "none": "none: no asset tags were applied",
    }[run.tag_source.source]
    return reference


def _sarif_vectors(raw: bytes) -> Dict[str, str]:
    """The baseline SARIF's ``cvss-vector`` of each result by canonical ID: R-26's second source of a vector, which
    Section 6 shows as the stored value when it and the markdown's disagree. A file that doesn't read gives none."""
    try:
        results = json.loads(raw.decode("utf-8"))["runs"][0]["results"]
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return {}
    found: Dict[str, str] = {}
    for result in results if isinstance(results, list) else []:
        try:
            identifier, vector = result["partialFingerprints"]["findingId/v1"], result["properties"]["cvss-vector"]
        except (KeyError, TypeError):
            continue
        if isinstance(identifier, str) and isinstance(vector, str) and tp.id_matches("finding", identifier):
            found.setdefault(tp.canonical_finding_id(identifier), vector)
    return found


def _route(run: Run, reference: Mapping[str, Any]) -> Any:
    """The partition of the open findings, by the one function the planner calls too (D2). ``lacking`` is S-12(b)'s, so the
    router derives a status from the baseline for a value that the input's form has no place for; it is passed only
    when there is something lacking, and the router's default leaves every other caller as it was."""
    rows = [{"id": tp.canonical_finding_id(finding["id"]), "component": finding["component"], "delta_status": finding.get("delta_status")}
            for finding in reference["open"]]
    return rules.route_scorer_units(rows, groups=run.groups, baseline=run.baseline, **({"lacking": run.lacking} if run.lacking else {}))


def _supply(run: Run, reference: Mapping[str, Any]) -> None:
    """S-12(b): a carried finding's component, threat and risk level come from its baseline row when the input's form
    lacks them, and only a value that the row records. It happens before S-13's tag join, so the tags follow the finding's
    own component and a drift form raises no false ``retagged`` flag. A fresh finding is never supplied (D9)."""
    carried = set(run.routing.carried)
    for finding in reference["open"]:
        canonical = tp.canonical_finding_id(finding["id"])
        if canonical not in carried:
            continue
        stored = run.baseline.rows[canonical]
        for name in run.lacking.get(canonical, ()):
            value = getattr(stored, name, None) if name in ("component", "threat", "risk_level") else None
            if value:
                finding[name] = value


def _prepare_baseline(run: Run, plan: Mapping[str, Any], refs: Mapping[str, str], threats_text: Optional[str],
                      inputs: Mapping[str, bytes]) -> None:
    """The baseline the planner used: its recorded, digest-checked files. Why there is none is worked out again (R-6, D9)."""
    entry = plan["inputs"].get("baseline_risk_scores")
    if entry is not None:
        sarif = plan["inputs"].get("baseline_risk_scores_sarif")
        scores = rules.read_baseline_scores(Path(entry["path"]), sarif_path=Path(sarif["path"]) if sarif is not None else None)
        for issue in scores.issues:
            run.issues.append("Baseline %s: %s" % (MD, issue.detail))
        if scores.readable:
            run.baseline, run.baseline_path = scores, _relative(entry["path"], run.cwd)
            run.baseline_note = run.baseline_path or "a baseline file"
            if "baseline_risk_scores_sarif" in inputs:
                run.baseline_vectors = _sarif_vectors(inputs["baseline_risk_scores_sarif"])
            return
        run.warn("baseline-unreadable", "the baseline %s could not be read (%s), so its owners, SLAs and dispositions were not carried" % (MD, scores.reason))
        run.issues.append("The baseline %s could not be read (%s): its owners, SLAs and dispositions were not carried" % (MD, scores.reason))
        return
    source = tachi_parsers.parse_baseline_frontmatter(threats_text)["source"] if threats_text is not None else None
    resolution = rules.resolve_baseline(flag=refs.get("baseline_dir"), baseline_source=source, cwd=Path(run.cwd))
    if resolution.run_dir is None:
        if resolution.reason != "not-named":   # free text, an unresolvable path or a failed check: scored fresh, and the record says why (D9)
            run.warn("baseline-unresolved", "the baseline named by %s was not used (%s), so every finding is scored fresh"
                     % ("--baseline" if resolution.origin == "flag" else "baseline.source", resolution.reason))
        return
    path = resolution.files.get(MD)
    if path is None:   # the run directory has no risk-scores.md that passes the checks: missing, a link, not a regular file
        reason = resolution.file_reasons.get(MD, "missing")
        if reason == "missing":
            run.warn("baseline-unresolved", "the baseline run directory has no %s (%s), so every finding is scored fresh" % (MD, reason))
            return
        refused = "refused"
    else:   # the file is there and the plan recorded no input for it, so the planner could not read it (S-12(d))
        reason = rules.read_baseline_scores(path).reason or "changed-since-plan"
        refused = "unreadable"
    run.warn("baseline-unreadable", "the baseline %s was %s (%s), so its owners, SLAs and dispositions were not carried" % (MD, refused, reason))
    run.issues.append("The baseline %s was %s (%s): its owners, SLAs and dispositions were not carried" % (MD, refused, reason))


# =============================================================================
# Scoring: reachability, and the three ways a row is made
# =============================================================================

def _reachability(trust: Optional[str], zone: Optional[str], auth: int, net: int) -> Decimal:
    """``reachability-analysis.md``: the trust level's baseline, the zone-name keywords, the barrier and boundary
    adjustments with their caps, each step clamped to the level's range, or the flat 5.0 when there is no zone data."""
    if trust is None or zone is None:
        score, (low, high) = ts.REACHABILITY_DEFAULT, ts.REACHABILITY_DEFAULT_RANGE
    else:
        score = ts.REACHABILITY_BASELINES[trust]
        low, high = ts.REACHABILITY_RANGES[trust]
        lowered = zone.lower()
        for keywords, adjustment in ts.REACHABILITY_KEYWORDS:
            score += adjustment * sum(1 for keyword in keywords if keyword in lowered)
        score = max(low, min(high, score))
    score += ts.AUTH_BARRIER_ADJUSTMENT * min(auth, ts.AUTH_BARRIER_CAP) + ts.NETWORK_BOUNDARY_ADJUSTMENT * min(net, ts.NETWORK_BOUNDARY_CAP)
    return ts.q1(max(low, min(high, score)))


def _identity(run: Run, finding: Mapping[str, Any]) -> Row:
    """A row's identity, from the reference set and §1 of threats.md."""
    component = finding["component"] or "Unspecified"
    info = run.component_info.get(component)
    if info is None:
        folded = component.casefold()
        info = next((value for name, value in run.component_info.items() if name.casefold() == folded), ("", ""))
    canonical = tp.canonical_finding_id(finding["id"])
    layer = run.finding_layer.get(canonical) or finding.get("layer") or info[1] or "Unclassified"
    attribution = tuple(entry.get("id", "") for entry in finding.get("source_attribution", ()) if entry.get("id"))
    return Row(finding["id"], component, finding["threat"] or "No threat description.", finding["mitigation"], finding["risk_level"],
               layer, KIND_OF_DFD_TYPE.get(finding.get("type") or info[0], "process"), _delta_status(finding), attribution)


def _effective_zone(run: Run, row: Row, zone: Optional[str], trust: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """The zone and trust level the reachability uses for an agent-assessed finding.

    The zone must name a §2 row (D2). One that doesn't is an Input Issue (no flag: the vocabulary is closed), and the
    component's own §2 zone stands in for it, or the default reachability when the component has none. A trust level
    that contradicts an unambiguous §2 label is corrected to the label's (``corrected:trust_level:trust-label``).
    """
    if zone is None or trust is None:
        return None, None
    entry = run.zones.get(zone)
    if entry is None:
        folded = zone.casefold()
        entry = next((found for name, found in run.zones.items() if name.casefold() == folded), None)
    if entry is None:
        own = run.component_zone.get(row.component.casefold())
        entry = run.zones.get(own) if own is not None else None
        run.issues.append("%s: the scorer named the zone %s, which is not a Section 2 zone, so %s" % (
            row.finding_id, repr(zone[:60]), "the component's own zone %s was used" % repr(entry[0]) if entry is not None
            else "its reachability is the default %s" % ts.REACHABILITY_DEFAULT))
        if entry is None:
            return None, None
    level = _label_level(entry[1])
    if level is not None and level != trust:
        row.flags.append(Flag("corrected", "trust_level", "trust-label", stored=trust, rendered=level))
        trust = level
    return entry[0], trust


def _lookup_for(run: Run, row: Row) -> Any:
    """The slot lookup of ADR-050 D3's table for the scorer: this finding's rendered values."""
    allowed_refs = set(RULE_BY_CATEGORY[row.category][4]) | set(row.attribution)
    layer = _LAYER.match(row.layer)
    if layer:
        allowed_refs.add(layer.group(0))
    values = {("score", "cvss_base"): _one(row.cvss), ("score", "exploitability"): _one(row.exploit), ("score", "scalability"): _one(row.scale),
              ("score", "reachability"): _one(row.reach), ("score", "composite"): _one(row.composite), ("band", "severity"): row.band,
              ("date", "scored"): row.scored_on.isoformat() if row.scored_on else None, ("date", "review"): row.review_date or None,
              ("name", "component"): row.component, ("name", "zone"): row.zone}
    if row.auth is not None:
        values[("count", "auth_barriers")] = str(row.auth)
    if row.net is not None:
        values[("count", "network_boundaries")] = str(row.net)
    for name, number in (row.subs or {}).items():
        values[("score", name)] = str(number)

    def lookup(kind: str, argument: str) -> Optional[str]:
        if kind == "finding":
            return argument if argument in run.open_ids else None
        if kind == "ref":
            return argument if argument in allowed_refs else None
        return values.get((kind, argument))

    return lookup


def _narrate(run: Run, row: Row, texts: Mapping[str, str], legacy: Mapping[str, str]) -> None:
    """Resolve a finding's narrative into ``cell_text``, ``prose_text`` and the persisted text (D3 step 11, RR1).

    ``texts`` holds the validated, slotted text of each field. A field whose text or slots don't resolve takes its fixed
    sentence, is flagged ``input:<field>:narrative-fallback`` and counted, and the sentence is what is persisted.
    ``legacy`` is a legacy baseline's prose: evidence-class text that is escaped and never resolved.
    """
    lookup = _lookup_for(run, row)
    for field in sorted(texts, key=lambda name: tp.NARRATIVE_FIELDS.index(name) if name in tp.NARRATIVE_FIELDS else len(tp.NARRATIVE_FIELDS)):
        text = texts[field]
        if field not in tp.FALLBACK_SENTENCES:
            continue
        cell = prose = None
        if tp.narrative_problem(text, STAGE) is None:
            cell = tp.resolve_narrative(text, STAGE, lookup, sink="cell")
            prose = tp.resolve_narrative(text, STAGE, lookup, sink="prose")
        if cell is None or prose is None:
            text = tp.FALLBACK_SENTENCES[field]
            cell, prose = tp.escape_cell(text), tp.escape_prose(text)
            if not any(flag.field == field and flag.cause == "narrative-fallback" for flag in row.flags):
                row.flags.append(Flag("input", field, "narrative-fallback"))
                run.counts["narrative_fallbacks"] += 1
        row.persisted[field] = text
        row.cell_text[field], row.prose_text[field] = cell, prose
    for field, text in legacy.items():
        if field in tp.FALLBACK_SENTENCES and field not in row.cell_text:
            row.cell_text[field], row.prose_text[field] = tp.escape_cell(text), tp.escape_prose(text)


def _finish_numbers(row: Row) -> None:
    row.composite = ts.composite(row.cvss, row.exploit, row.scale, row.reach)
    row.band = ts.band(row.composite)


def _shown(value: Any) -> Optional[str]:
    """A value as Section 6 shows it: a score on the 0.1 grid as one decimal, a score off it as written, a date as ISO text."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        try:
            return _one(value) if value == ts.q1(value) else str(value)
        except ValueError:
            return str(value)
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _flag_with_values(text: str, stored: Any, row: Row) -> Flag:
    """A flag from ``tachi_scoring_rules`` (kept as it is), with the baseline's value and this file's for Section 6."""
    flag = _flag_from_text(text)
    if stored is not None:
        was = {"cvss_base": stored.stored.get("cvss_base"), "remediation_sla": stored.sla, "risk_disposition": stored.disposition,
               "review_date": stored.review_date}.get(flag.field)
        now = {"cvss_base": row.cvss, "remediation_sla": row.sla, "risk_disposition": row.disposition, "review_date": row.review_date}.get(flag.field)
        flag.stored, flag.rendered = _shown(was), _shown(now)
    return flag


def _govern(run: Run, row: Row, stored: Any, change: str, scoring_date: datetime.date) -> None:
    """The owner, SLA, disposition, review date and scored-on date from ``governance_for``, and every flag it returns (D9)."""
    baseline_date = run.baseline.frontmatter_date if run.baseline is not None else None
    gov = rules.governance_for(row.status, rendered_band=row.band, run_date=scoring_date, row=stored, band_change=change, baseline_date=baseline_date)
    row.owner, row.sla, row.disposition, row.review_date, row.scored_on = gov.owner, gov.sla, gov.disposition, gov.review_date.isoformat(), gov.scored_on
    for text in gov.flags:
        row.flags.append(_flag_with_values(text, stored, row))


def _score_fresh(run: Run, row: Row, item: Mapping[str, Any], stored: Any, scoring_date: datetime.date) -> None:
    """An agent-assessed finding: the scorer's judgment in, every number computed (D2)."""
    row.vector = item["cvss_vector"]
    row.subs = {name: item["exploitability"][name] for name in tp.SUBSCORE_NAMES[:4]}
    row.subs.update({name: item["scalability"][name] for name in tp.SUBSCORE_NAMES[4:]})
    reach = item["reachability"]
    row.zone, row.trust = _effective_zone(run, row, reach["zone"], reach["trust_level"])
    row.auth, row.net = reach["auth_barriers"], reach["network_boundaries"]
    row.tags = tuple(run.tag_source.tags.get(row.canon, ()))
    if run.baseline is not None and row.status == "NEW":
        row.bounds = ts.bounds(ts.default_score(row.category))
    row.cvss = rules.cvss_chain(row.vector, tags=row.tags, score_bounds=row.bounds).cvss_base
    row.exploit = ts.sub_score_mean([row.subs[name] for name in tp.SUBSCORE_NAMES[:4]])
    row.scale = ts.sub_score_mean([row.subs[name] for name in tp.SUBSCORE_NAMES[4:]])
    row.reach = _reachability(row.trust, row.zone, row.auth, row.net)
    row.defaulted_reach = row.trust is None
    _finish_numbers(row)
    change = "none"
    if stored is not None and row.status == "UPDATED":
        change = rules.classify_band_change(stored_band=stored.band, rendered_band=row.band, band_with_baseline_tags=None)
    _govern(run, row, stored, change, scoring_date)
    texts = dict(("rationale." + key, item["rationale"][key]) for key in RATIONALE_KEYS)
    for group in ("metric_rationale", "subscore_rationale"):
        texts.update(("%s.%s" % (group, key), text) for key, text in item.get(group, {}).items())
    _narrate(run, row, texts, {})


def _exact_composite(cvss: Decimal, exploit: Decimal, scale: Decimal, reach: Decimal) -> Decimal:
    """The weighted sum before it is rounded, so that a tie, a sum that ends in exactly ``.x5``, can be told from an error (R-11)."""
    return sum((ts.WEIGHTS[name] * value for name, value in
                (("cvss_base", cvss), ("exploitability", exploit), ("scalability", scale), ("reachability", reach))), Decimal(0))


def _rounding_only(stored: Optional[Decimal], exact: Decimal) -> bool:
    """R-11: whether ``stored`` is the one-decimal neighbour of ``exact`` that the half-up rounding did not pick."""
    if stored is None or not stored.is_finite():
        return False
    below, above = exact.quantize(Decimal("0.1"), rounding=ROUND_FLOOR), exact.quantize(Decimal("0.1"), rounding=ROUND_CEILING)
    return below != above and stored != ts.q1(exact) and stored in (below, above)


def _mean(values: Sequence[int]) -> Tuple[Decimal, Decimal]:
    """A sub-score mean as the renderer rounds it and as it is before it is rounded (the four values over four, exactly)."""
    return ts.sub_score_mean(values), sum((Decimal(value) for value in values), Decimal(0)) / 4


def _stored_grid(run: Run, row: Row, name: str, value: Optional[Decimal]) -> Decimal:
    """A legacy row's stored value as a score the arithmetic can take. One off the grid or outside 0.0 to 10.0 is clamped
    onto it, and an Input Issue says so, because the vocabulary has no flag for it and no step is silent."""
    grid = _grid(value)
    if value is not None and value != grid:
        run.issues.append("%s: the stored %s %s is not a score from 0.0 to 10.0 on the 0.1 grid, so %s was used" % (
            row.finding_id, name, str(value)[:20], grid))
    return grid


def _reach_flag(run: Run, row: Row, stored: Decimal) -> Optional[Flag]:
    """D10's range check of a legacy finding's reachability (R-10). The component's Section 2 label gives the trust level,
    and only when it names one (``trust-zones.md`` 2c). A value out of that level's range is kept and flagged ``input``,
    and an ambiguous label is ``unchecked``, never a violation. A component with no label has nothing to check against."""
    zone = run.component_zone.get(row.component.casefold())
    entry = run.zones.get(zone) if zone is not None else None
    if entry is None:
        return None
    level = _label_level(entry[1])
    if level is None:
        return Flag("unchecked", "reachability", "compound-trust-label", stored=_shown(stored))
    low, high = ts.REACHABILITY_RANGES[level]
    return None if low <= stored <= high else Flag("input", "reachability", "out-of-range", stored=_shown(stored))


def _carry(run: Run, row: Row, stored: Any, scoring_date: datetime.date) -> None:
    """An UNCHANGED finding with a usable baseline row (D9 steps 1 to 4, D10).

    **Inherited verbatim** (step 1): from a renderer-form row the vector, bounds, sub-scores, zone, trust level, barrier
    counts and tags used; from a legacy row the vector and the stored C, E, S and R; from either the owner, SLA,
    disposition, review date and, whenever §6 records them, the tags used and the scored-on date (P0-2: a legacy
    finding that an earlier run carried records both). **Recomputed** (step 2): the CVSS chain through
    ``check_carried_vector``, then E, S and R (a legacy R is only range-checked), then the composite and the band.
    **Compared** (steps 3 and 4): a difference that is only rounding is normalized and counted when the band holds; one
    that the asset tags alone explain is ``retagged`` (ruling A: recomputing with the baseline's recorded tags gives the
    stored value); anything else is ``corrected``, and a missing vector is ``unverifiable``. The governance and its flags
    are ``governance_for``'s, unioned, never re-derived.
    """
    row.source = "inherited"
    row.tags = tuple(run.tag_source.tags.get(row.canon, ()))
    renderer_form = stored.form == "renderer"
    baseline_tags = tuple(stored.tags_used or ())   # ruling A's recorded tags, whatever the form: a pre-1.1 row has none (P0-2)
    held = stored.stored
    row.vector, row.bounds, row.zone, row.trust = stored.cvss_vector, stored.score_bounds, stored.zone, stored.trust_level
    check = rules.check_carried_vector(stored, tags=row.tags)
    row.cvss = _grid(check.cvss_base)
    rounded = False   # some difference was only rounding (R-11)
    if renderer_form:
        row.subs = dict(stored.subscores)
        row.auth, row.net = stored.auth_barriers or 0, stored.network_boundaries or 0
        row.defaulted_reach = row.trust is None
        row.exploit, exact_exploit = _mean([row.subs[name] for name in tp.SUBSCORE_NAMES[:4]])
        row.scale, exact_scale = _mean([row.subs[name] for name in tp.SUBSCORE_NAMES[4:]])
        row.reach = _reachability(row.trust, row.zone, row.auth, row.net)
        for name, value, exact in (("exploitability", row.exploit, exact_exploit), ("scalability", row.scale, exact_scale),
                                   ("reachability", row.reach, row.reach)):
            was = held.get(name)
            if was is not None and was != value:
                if _rounding_only(was, exact):
                    rounded = True
                else:
                    row.flags.append(Flag("corrected", name, "arithmetic", _shown(was), _shown(value)))
    else:
        row.exploit, row.scale, row.reach = (_stored_grid(run, row, name, held.get(name)) for name in ("exploitability", "scalability", "reachability"))
        flag = _reach_flag(run, row, row.reach)
        if flag is not None:
            row.flags.append(flag)
    _finish_numbers(row)
    if check.flag is not None:
        row.flags.append(_flag_with_values(check.flag, stored, row))
    for text in stored.flags:   # raised while the baseline was read: the markdown's vector was used over the SARIF's
        flag = _flag_from_text(text)
        if text == "input:cvss_vector:sources-disagree":
            flag.stored, flag.rendered = run.baseline_vectors.get(row.canon), row.vector
        row.flags.append(flag)

    # The composite and the band, against what the baseline stored. "The tags alone" means that recomputing with the
    # baseline's own tags gives the stored value (ruling A); a pre-1.1 legacy row records none, so baseline_tags is empty for it.
    then_cvss = _grid(rules.check_carried_vector(stored, tags=baseline_tags).cvss_base)
    then_composite = ts.composite(then_cvss, row.exploit, row.scale, row.reach)
    was = held.get("composite")
    rounding_composite = False
    if was is not None and was != row.composite:
        if was == then_composite:
            row.flags.append(Flag("retagged", "composite_score", "asset-tags", _shown(was), _shown(row.composite)))
        elif _rounding_only(was, _exact_composite(row.cvss, row.exploit, row.scale, row.reach)):
            rounded = rounding_composite = True
        else:
            row.flags.append(Flag("corrected", "composite_score", "arithmetic", _shown(was), _shown(row.composite)))
    change = rules.classify_band_change(stored_band=stored.band, rendered_band=row.band, band_with_baseline_tags=ts.band(then_composite))
    if change == "corrected":   # only rounding moved the band when the composite is a tie that the stored band follows
        cause = "rounding" if rounding_composite and ts.band(was) == stored.band else "band-mapping"
        row.flags.append(Flag("corrected", "severity_band", cause, stored.band, row.band))
    elif change != "none":
        row.flags.append(Flag("retagged", "severity_band", "asset-tags", stored.band, row.band))
    if rounded and change == "none":
        run.normalized += 1
    _govern(run, row, stored, change, scoring_date)
    row.legacy_prose = dict(stored.legacy_prose)
    _narrate(run, row, stored.narrative if renderer_form else {}, row.legacy_prose)


def _copy_peer(run: Run, row: Row, primary: Row, stored: Any, scoring_date: datetime.date) -> None:
    """A NEW or UPDATED peer takes its primary's vector, bounds, dimensions and derived scores (R-31). It keeps its own
    identity and its own governance. Its prose is its primary's slotted text, resolved against the peer's own values,
    so the text reads true for the peer now and again on the run that carries it."""
    for name in ("source", "vector", "cvss", "exploit", "scale", "reach", "composite", "band", "subs", "zone", "trust", "auth", "net",
                 "tags", "bounds", "defaulted_reach"):
        setattr(row, name, getattr(primary, name))
    row.copied = True
    change = "none"
    if stored is not None and row.status == "UPDATED":
        change = rules.classify_band_change(stored_band=stored.band, rendered_band=row.band, band_with_baseline_tags=None)
    _govern(run, row, stored, change, scoring_date)
    row.legacy_prose = dict(primary.legacy_prose)
    _narrate(run, row, primary.persisted, row.legacy_prose)


def _score(run: Run, reference: Mapping[str, Any], items: Mapping[str, Mapping[str, Any]], part_flags: Mapping[str, List[str]],
           scoring_date: datetime.date, kept: str) -> None:
    """Make every open row, by the planner's partition (``route_scorer_units``): carried, copied from a primary, or the agent's."""
    for finding in reference["open"]:
        run.rows.append(_identity(run, finding))
    for row in run.rows:
        run.spelling[row.canon] = row.finding_id
    run.open_ids = set(run.spelling)
    routing = run.routing
    if run.lacking:   # S-12(b): the router derived a status for each finding whose form has none
        derived = routing.status
        for row in run.rows:
            if "delta_status" in run.lacking.get(row.canon, ()):
                row.status = derived[row.canon]
    carried, copied = set(routing.carried), routing.copy_primary
    stored_rows = run.baseline.rows if run.baseline is not None else {}
    by_canon = {row.canon: row for row in run.rows}
    for row in run.rows:
        if row.canon in carried:
            _carry(run, row, stored_rows[row.canon], scoring_date)
        elif row.canon not in copied:
            item = items.get(row.canon)
            if item is None:
                raise RenderError(4, "the parts hold no item for %s, so the run is incomplete" % row.finding_id, "re-run the command", kept=kept)
            _score_fresh(run, row, item, stored_rows.get(row.canon), scoring_date)
            for text in part_flags.get(row.canon, ()):
                if not any(known.text() == text for known in row.flags):
                    row.flags.append(_flag_from_text(text))
    for row in run.rows:
        if row.canon in copied:
            _copy_peer(run, row, by_canon[copied[row.canon]], stored_rows.get(row.canon), scoring_date)
        if run.baseline is not None and row.status == "NEW" and row.canon in run.baseline.ids_in_any_row:
            row.flags.append(Flag("reused-id", "finding_id", "baseline", stored=row.finding_id))  # ruling B: scored fresh, and never from that row
        for text in reference.get("flags", {}).get(row.canon, ()):  # S-12(b): a value that the input's form lacks
            row.flags.append(_flag_from_text(text))
    for peer, primary in routing.carried_peers.items():   # R-4: an UNCHANGED peer keeps its own score, and a difference is flagged
        found = rules.peer_divergence(peer_composite=by_canon[peer].composite, primary_id=primary, primary_composite=by_canon[primary].composite)
        if found is not None:
            flag = _flag_from_text(found)
            flag.stored, flag.rendered = _shown(by_canon[peer].composite), _shown(by_canon[primary].composite)
            by_canon[peer].flags.append(flag)
    for row in run.rows:  # a finding carries each flag once, whichever step raised it (the closed vocabulary's rule)
        seen: set = set()
        row.flags = [flag for flag in row.flags if not (flag.text() in seen or seen.add(flag.text()))]
    run.ordered = sorted(run.rows, key=lambda row: (-row.composite, tp.finding_sort_key(row.canon)))
    for finding in reference["resolved"]:
        run.resolved.append(dict(finding, canon=tp.canonical_finding_id(finding["id"])))
    defaulted = [row for row in run.ordered if row.defaulted_reach]
    if defaulted:
        run.warn("reachability-defaulted", "%d findings had no trust zone data, so their reachability is the default 5.0: %s"
                 % (len(defaulted), ", ".join(row.finding_id for row in defaulted[:5]) + (", and more" if len(defaulted) > 5 else "")))


# =============================================================================
# risk-scores.md
# =============================================================================

def _flag_kinds(flags: Sequence[Flag]) -> str:
    present = {flag.kind for flag in flags}
    return ", ".join(kind for kind in FLAG_KINDS if kind in present) or DASH


def _sorted_flags(flags: Sequence[Flag]) -> List[Flag]:
    return sorted(flags, key=lambda flag: (FLAG_KINDS.index(flag.kind) if flag.kind in FLAG_KINDS else len(FLAG_KINDS), flag.field, flag.cause))


def _inputs_rows(row: Row) -> List[Tuple[str, str]]:
    """One row's ``### Scoring Inputs`` (contracts/module-signatures.md): one per value, in the part's key order, with
    ``score_bounds``, ``tags`` and ``scored_on`` last. ``tags`` is always written; a null field writes no row."""
    found: List[Tuple[str, str]] = []
    if row.vector is not None:
        found.append(("cvss_vector", row.vector))
    if row.subs is not None:
        for group, names in (("exploitability", tp.SUBSCORE_NAMES[:4]), ("scalability", tp.SUBSCORE_NAMES[4:])):
            found += [("%s.%s" % (group, name), str(row.subs[name])) for name in names]
        if row.zone is not None:
            found.append(("reachability.zone", row.zone))
        if row.trust is not None:
            found.append(("reachability.trust_level", row.trust))
        found.append(("reachability.auth_barriers", str(row.auth)))
        found.append(("reachability.network_boundaries", str(row.net)))
    found += [("rationale." + key, row.persisted["rationale." + key]) for key in RATIONALE_KEYS if "rationale." + key in row.persisted]
    found += [("metric_rationale." + name, row.persisted["metric_rationale." + name]) for name in tp.METRIC_NAMES
              if "metric_rationale." + name in row.persisted]
    found += [("subscore_rationale." + name, row.persisted["subscore_rationale." + name]) for name in tp.SUBSCORE_NAMES
              if "subscore_rationale." + name in row.persisted]
    if row.bounds is not None:
        found.append(("score_bounds", "%s,%s" % (row.bounds[0], row.bounds[1])))
    found.append(("tags", ",".join(sorted(row.tags))))
    if row.scored_on is not None:
        found.append(("scored_on", row.scored_on.isoformat()))
    return found


def _distribution(run: Run) -> Tuple[Dict[str, int], Dict[str, int]]:
    counts = {band: sum(1 for row in run.rows if row.band == band) for band in ts.SEVERITY_BANDS}
    return counts, ts.largest_remainder(counts)


def _resolved_cells(run: Run, finding: Mapping[str, Any]) -> List[str]:
    """§2a's cells: the baseline's values for the finding, verbatim, or a dash where it holds none."""
    stored = None
    if run.baseline is not None:
        stored = run.baseline.rows.get(finding["canon"]) or run.baseline.resolved_rows.get(finding["canon"])

    def text(value: Any) -> str:
        return tp.escape_cell(str(value)) if value is not None and str(value) != "" else DASH

    scores = [text(stored.stored.get(key)) if stored is not None else DASH
              for key in ("cvss_base", "exploitability", "scalability", "reachability", "composite")]

    def held(name: str) -> str:
        return text(getattr(stored, name)) if stored is not None else DASH

    return ([finding["id"], "inherited", tp.escape_cell(_shorten(finding["component"], COMPONENT_WIDTH)),
             tp.escape_cell(_shorten(finding["threat"], THREAT_WIDTH))] + scores
            + [held("band"), held("sla"), held("disposition"), "RESOLVED", held("owner"), held("review_date"), "resolved"])


def _md_section_1(run: Run, out: List[str], scoring: str) -> None:
    counts, shares = _distribution(run)
    total = len(run.rows)
    out += ["## 1. Executive Summary", "",
            "%d open findings were scored on %s: %d Critical, %d High, %d Medium and %d Low."
            % (total, scoring, counts["Critical"], counts["High"], counts["Medium"], counts["Low"]), ""]
    by_component: Dict[str, List[Row]] = {}
    for row in run.rows:
        by_component.setdefault(row.component, []).append(row)
    if by_component:
        name, members = sorted(by_component.items(), key=lambda entry: (-max(row.composite for row in entry[1]), -len(entry[1]), entry[0]))[0]
        out += ["**Highest-Risk Component**: %s %s %d finding(s), max composite %s"
                % (tp.escape_prose(name), DASH, len(members), _one(max(row.composite for row in members))), ""]
    out += ["**Resolved findings** (Section 2a, outside the distribution below): %d" % len(run.resolved), "",
            "**Severity Distribution:**", "", "| Severity | Count | Percentage |", "|----------|-------|------------|"]
    out += ["| %s | %d | %d%% |" % (band, counts[band], shares[band]) for band in ts.SEVERITY_BANDS]
    out += ["| **Total** | **%d** | **%d%%** |" % (total, sum(shares.values())), "",
            "| Metric | Value |", "|--------|-------|", "| Scoring date | %s |" % scoring,
            "| Source file | %s |" % ("`%s`" % tp.escape_cell(run.source_file) if run.source_file else DASH),
            "| Schema version | %s |" % SCHEMA_VERSION, ""]
    defaulted = [row for row in run.ordered if row.defaulted_reach]
    if defaulted:
        out += ["> Reachability defaulted to 5.0 for %d finding(s) with no trust zone data: %s." % (
            len(defaulted), ", ".join(row.finding_id for row in defaulted[:5]) + (", and more" if len(defaulted) > 5 else "")), ""]


def _md_section_2(run: Run, out: List[str]) -> None:
    out += ["---", "", "## 2. Scored Threat Table", "",
            "Findings sorted by Composite score descending (highest risk first), and by finding ID within equal scores. "
            "Boundary values map to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).", "",
            "| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Flags |",
            "|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|-------|"]
    for row in run.ordered:
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            row.finding_id, row.source, tp.escape_cell(_shorten(row.component, COMPONENT_WIDTH)),
            tp.escape_cell(_shorten(row.threat, THREAT_WIDTH)), _one(row.cvss), _one(row.exploit), _one(row.scale), _one(row.reach),
            _one(row.composite), row.band, tp.escape_cell(row.sla), tp.escape_cell(row.disposition), _flag_kinds(row.flags)))
    out.append("")
    if run.resolved:
        out += ["---", "", "## 2a. Resolved Findings", "",
                "Findings that the source threat model lists in Section 4c as RESOLVED. Each row keeps the values it last had in the "
                "baseline, verbatim: the renderer recomputes nothing for it, and the SLA clock doesn't run for it.", "",
                "| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Status | Owner | Review Date | Flags |",
                "|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|--------|-------|-------------|-------|"]
        out += ["| %s |" % " | ".join(_resolved_cells(run, finding)) for finding in run.resolved]
        out.append("")


def _correlation_line(run: Run, row: Row) -> Optional[str]:
    found = run.assignments.get(row.canon)
    if found is None:
        return None

    def name(canonical: str) -> str:
        return run.spelling.get(canonical, canonical)

    if found.role == "primary":
        named = ", ".join(name(peer) for peer in found.peers[:sc.PEER_CAP])
        more = " and %d more" % (len(found.peers) - sc.PEER_CAP) if len(found.peers) > sc.PEER_CAP else ""
        return "**Correlation Group**: %s, primary of %s%s" % (found.group, named, more)
    if row.copied:
        return "**Correlation Group**: Scores inherited from primary finding %s (%s)" % (name(found.primary), found.group)
    return "**Correlation Group**: %s, peer of primary %s (this finding keeps its own score)" % (found.group, name(found.primary))


def _md_finding(run: Run, row: Row, out: List[str]) -> None:
    out += ["### %s %s %s" % (row.finding_id, DASH, tp.escape_prose(row.component)), "",
            "**Threat**: %s" % tp.escape_prose(row.threat), "",
            "**Category**: %s | **Original Risk Level**: %s | **Composite**: %s (%s)"
            % (row.category, tp.escape_prose(row.risk_level), _one(row.composite), row.band), ""]
    line = _correlation_line(run, row)
    if line:
        out += [line, ""]
    if row.flags:
        out += ["**Integrity**: %s" % ", ".join(tp.escape_prose(flag.text()) for flag in _sorted_flags(row.flags)), ""]
    out += ["#### CVSS 3.1 Base", ""]
    if row.vector is not None:
        out += ["**Score**: %s | **Vector**: `%s`" % (_one(row.cvss), row.vector), ""]
        letters = dict(part.split(":") for part in row.vector.split("/")[1:])
        out += ["| Metric | Value | Rationale |", "|--------|-------|-----------|"]
        out += ["| %s | %s | %s |" % (label, METRIC_VALUES[key][letters[key]], row.cell_text.get("metric_rationale." + key, DASH))
                for key, label in METRIC_LABELS]
        out.append("")
    else:
        out += ["**Score**: %s | **Vector**: %s" % (_one(row.cvss), DASH), ""]
    if "rationale.cvss" in row.prose_text:
        out += [row.prose_text["rationale.cvss"], ""]
    for title, group, names, score in (("Exploitability", "exploitability", tp.SUBSCORE_NAMES[:4], row.exploit),
                                       ("Scalability", "scalability", tp.SUBSCORE_NAMES[4:], row.scale)):
        out += ["#### %s" % title, "", "**Score**: %s (average of sub-dimensions)" % _one(score), ""]
        if row.subs is not None:
            out += ["| Sub-Dimension | Score | Rationale |", "|---------------|-------|-----------|"]
            out += ["| %s | %d | %s |" % (SUBSCORE_LABELS[name], row.subs[name], row.cell_text.get("subscore_rationale." + name, DASH))
                    for name in names]
            out.append("")
        if "rationale." + group in row.prose_text:
            out += [row.prose_text["rationale." + group], ""]
    zone = ("%s (%s)" % (tp.escape_prose(row.zone), row.trust) if row.zone is not None
            else "%s (no trust zone data; default %s)" % (DASH, ts.REACHABILITY_DEFAULT))
    out += ["#### Reachability", "", "**Score**: %s | **Trust Zone**: %s" % (_one(row.reach), zone), ""]
    if "rationale.reachability" in row.prose_text:
        out += [row.prose_text["rationale.reachability"], ""]
    out += ["---", ""]


def _md_section_4(run: Run, out: List[str]) -> None:
    out += ["## 4. Governance Fields", "",
            "Remediation tracking metadata for each scored finding. Default values are severity-driven. Edit the Owner, SLA, Disposition "
            "and Review Date here: the next run carries them, and flags an Accept or Transfer disposition, or an SLA or disposition that "
            "differs from the band's default, as an `override`.", "",
            "| ID | Severity | Owner | SLA | Disposition | Review Date |", "|----|----------|-------|-----|-------------|-------------|"]
    out += ["| %s | %s | %s | %s | %s | %s |" % (row.finding_id, row.band, tp.escape_cell(row.owner), tp.escape_cell(row.sla),
                                                 tp.escape_cell(row.disposition), row.review_date) for row in run.ordered]
    out += ["", "---", ""]


METHODOLOGY = """\
## 5. Scoring Methodology

This section documents the quantitative scoring model used to produce the risk scores in this report. All scores are derived from the threat findings identified during threat modeling and are intended to replace qualitative risk ratings with data-backed, reproducible numeric assessments.

### 5.1 Scoring Dimensions

Each threat finding is assessed across four independent dimensions, each producing a score on a 0.0 to 10.0 scale.

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity of the vulnerability using CVSS 3.1 base metrics: attack vector, attack complexity, privileges required, user interaction, scope, and confidentiality/integrity/availability impact. Each finding includes the full CVSS vector string for auditability. |
| **Exploitability** | 30% | Practical likelihood of exploitation based on known attack techniques, tooling availability, required skill level, and attack complexity. Higher scores indicate threats with well-documented exploit paths and readily available tooling. |
| **Scalability** | 15% | Potential for automated, large-scale exploitation based on scriptability, breadth of target scope, resource requirements for the attacker, and difficulty of detection. Higher scores indicate threats that can be weaponized across many targets with minimal effort. |
| **Reachability** | 20% | Exposure of the targeted component within the system's trust boundary architecture. Derived from trust zone data in the threat model and supplemented by architecture documentation when available. Higher scores indicate components directly exposed to untrusted networks. |

### 5.2 Default Weights and Rationale

The default weight allocation reflects the following priorities:

- **CVSS Base (35%)** receives the highest weight because intrinsic vulnerability severity is the strongest predictor of potential damage. CVSS 3.1 is an industry-standard metric with well-understood interpretation.
- **Exploitability (30%)** is weighted second because a severe vulnerability that is difficult to exploit in practice poses less immediate risk than one with known, tooled attack paths.
- **Reachability (20%)** accounts for architectural context. A critical vulnerability behind multiple trust boundaries and authentication layers presents less operational risk than the same vulnerability on an internet-facing endpoint.
- **Scalability (15%)** receives the lowest weight because while automation potential increases aggregate risk, it is less deterministic than the other dimensions and often correlates with exploitability.

These weights are fixed for this scoring run and are recorded in the report frontmatter for reproducibility.

### 5.3 Composite Score Formula

The composite risk score for each finding is calculated as a weighted sum of the four dimension scores:

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The sum runs over the stored one-decimal values and is rounded half up to one decimal (a composite of 4.55 is 4.6). The composite score is bounded to the 0.0-10.0 range. Because each dimension is independently scored on a 0.0-10.0 scale and the weights sum to 1.0, the composite inherently falls within this range.

### 5.4 Severity Band Mapping

Composite scores are mapped to severity bands that drive default governance actions:

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band (e.g., a composite score of exactly 7.0 maps to High, not Medium). These bands are aligned with the severity classifications defined in `schemas/output.yaml` to maintain backward compatibility with existing tachi threat model output.

### 5.5 Data Sources

Scoring draws on the following inputs:

- **Threat findings**: Parsed from `threats.md` (markdown table format) or `threats.sarif` (SARIF 2.1.0 JSON). All original threat metadata (ID, component, category, description, likelihood, impact) is preserved through the scoring pipeline.
- **Trust zone data**: Extracted from `threats.md` Section 2 (trust zone table) as the primary source for reachability scoring. Components in Untrusted/External zones score 8.0-10.0 reachability; Semi-Trusted/Application zones score 4.0-7.0; Trusted/Internal zones score 1.0-4.0.
- **Architecture documentation**: When `architecture.md` is available, it provides supplementary context such as authentication barriers and network exposure details that refine the baseline reachability score derived from trust zones.
- **Category default vectors**: CVSS 3.1 baseline vectors are defined per STRIDE threat category in `schemas/risk-scoring.yaml`. This includes tachi-specific defaults for AI threat categories (agentic and LLM) that lack standard CVSS mappings. Per-threat analysis may refine these baselines based on the specific threat description.
- **The baseline**: When a baseline `risk-scores.md` is available, a carried finding's inputs (its vector, sub-scores, reachability inputs and human governance fields) come from it, and Section 6 records which baseline was used.

When trust zone data is unavailable (no Section 2 in `threats.md` and no `architecture.md`), a default reachability score of 5.0 is applied with a warning in the output.

### 5.6 Reproducibility

The scorer's assessments (the CVSS vector, the eight sub-scores and the reachability inputs) are produced by an LLM at temperature 0. For the same threat model input, each of them is expected to be reproducible within a **+/- 0.5 tolerance** across runs. This tolerance reflects the inherent variability in LLM-based analysis and is considered acceptable for risk prioritization purposes.

Everything the renderer computes from those assessments is deterministic: the averages, the CVSS base score, the composite, the severity band, the SLA and the review date. The renderer uses exact decimal arithmetic and takes the date as an input, so the same parts and the same date give the same file, byte for byte. The composite formula, weights, and severity band mappings carry no tolerance.
"""


def _md_section_6(run: Run, out: List[str]) -> None:
    by_id = sorted(run.rows, key=lambda row: tp.finding_sort_key(row.canon))
    flagged = [(row, flag) for row in by_id for flag in _sorted_flags(row.flags)]
    summary: Dict[Tuple[str, str], int] = {}
    for _row, flag in flagged:
        summary[(flag.kind, flag.cause)] = summary.get((flag.kind, flag.cause), 0) + 1
    out += ["---", "", "## 6. Score Integrity", "",
            "What the renderer checked, corrected or could not check, and the inputs it scored from. A first run with no baseline has "
            "nothing to correct, so its Score Flags table is empty.", "",
            "### Integrity Summary", "", "| Kind | Cause | Count |", "|------|-------|-------|"]
    out += ["| %s | %s | %d |" % (kind, tp.escape_cell(cause), summary[(kind, cause)])
            for kind, cause in sorted(summary, key=lambda key: (FLAG_KINDS.index(key[0]) if key[0] in FLAG_KINDS else len(FLAG_KINDS), key[1]))]
    out += ["", "**Normalized (rounding only)**: %d" % run.normalized, "",
            "**Baseline source**: %s" % ("`%s`" % tp.escape_prose(run.baseline_path) if run.baseline_path else tp.escape_prose(run.baseline_note)), "",
            "**Tag source**: %s" % tp.escape_prose(run.tag_line), "",
            "### Score Flags", "", "| ID | Flag | Field | Stored | Rendered | Cause |", "|----|------|-------|--------|----------|-------|"]
    out += ["| %s | %s | %s | %s | %s | %s |" % (row.finding_id, flag.kind, tp.escape_cell(flag.field), tp.escape_cell(flag.stored or DASH),
                                                  tp.escape_cell(flag.rendered or DASH), tp.escape_cell(flag.cause)) for row, flag in flagged]
    out += ["", "### Input Issues", ""]
    out += ["- %s" % tp.escape_prose(issue) for issue in run.issues[:rules.ISSUE_LIMIT]] if run.issues else ["None."]
    if len(run.issues) > rules.ISSUE_LIMIT:
        out.append("- %d more issues were not listed" % (len(run.issues) - rules.ISSUE_LIMIT))
    out += ["", "### Scoring Inputs", "", "| ID | Field | Value |", "|----|-------|-------|"]
    for row in by_id:
        for field, value in _inputs_rows(row):
            out.append("| %s | %s | %s |" % (row.finding_id, field, tp.escape_cell(value, keep_slots=field in tp.NARRATIVE_FIELDS)))
    out.append("")


def _frontmatter(run: Run, scoring: str) -> List[str]:
    inherited = sum(1 for row in run.rows if row.source == "inherited") if run.baseline is not None else None
    fresh = len(run.rows) - inherited if inherited is not None else None
    return ["---", 'schema_version: "%s"' % SCHEMA_VERSION, 'date: "%s"' % scoring, "source_file: %s" % _quoted(run.source_file),
            'classification: "confidential"', "scoring_weights:", "  cvss_base: 0.35", "  exploitability: 0.30", "  scalability: 0.15",
            "  reachability: 0.20", "baseline:", "  source: %s" % _quoted(run.baseline_path),
            "  inherited_count: %s" % ("null" if inherited is None else inherited), "  fresh_count: %s" % ("null" if fresh is None else fresh),
            "---", ""]


def _render_md(run: Run, scoring: str, digest: str) -> str:
    out = _frontmatter(run, scoring)
    out += ["# Risk Scores Report", ""]
    _md_section_1(run, out, scoring)
    _md_section_2(run, out)
    out += ["---", "", "## 3. Dimensional Breakdown", "",
            "Per-finding detail showing the full scoring rationale for each dimension. One subsection per open finding, ordered by "
            "composite score descending (matching Section 2 sort order).", ""]
    for row in run.ordered:
        _md_finding(run, row, out)
    _md_section_4(run, out)
    out += METHODOLOGY.split("\n")
    _md_section_6(run, out)
    out += [tp.stamp_comment(RENDERER, digest), ""]
    return "\n".join(out)


# =============================================================================
# risk-scores.sarif
# =============================================================================

def _properties(row: Row) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        "security-severity": _one(row.composite), "cvss-base-score": _one(row.cvss), "cvss-vector": row.vector,
        "exploitability": _one(row.exploit), "scalability": _one(row.scale), "reachability": _one(row.reach),
        "composite-weights": WEIGHTS_TEXT, "score-source": row.source, "score-flags": sorted(flag.text() for flag in row.flags),
    }
    corrections = [{"field": flag.field, "from": flag.stored, "to": flag.rendered, "cause": flag.cause}
                   for flag in _sorted_flags(row.flags) if flag.kind in ("corrected", "retagged")]
    if corrections:
        props["score-corrections"] = corrections
    props.update({"severity-band": row.band, "risk-owner": row.owner, "remediation-sla": row.sla, "risk-disposition": row.disposition,
                  "review-date": row.review_date, "maestro-layer": row.layer, "affected_assets": list(row.tags)})
    return props


def _zone_of(run: Run, row: Row) -> str:
    return run.component_zone.get(row.component.casefold()) or row.zone or "Application Zone"


def _render_sarif(run: Run, digest: str) -> str:
    # ``markdown`` is always written, an empty mitigation's empty string included: the shipped scorer files carry it (P0-8, NFR-1)
    results = [sc.build_result(tool=TOOL, finding_id=row.finding_id, message=row.threat, markdown=row.mitigation or "",
                               level=sc.level_for_band(row.band), uri=run.uri, component=row.component, zone=_zone_of(run, row),
                               kind=row.kind, properties=_properties(row), correlation=run.assignments.get(row.canon))
               for row in run.ordered]
    highest: Dict[str, Decimal] = {}
    for row in run.rows:
        highest[row.category] = max(highest.get(row.category, row.composite), row.composite)
    rule_list = [{"id": sc.RULE_ID_BY_CATEGORY[category], "shortDescription": {"text": short}, "fullDescription": {"text": full},
                  "properties": {"tags": list(tags), "security-severity": _one(highest[category])}}
                 for category, short, full, tags, _ids in RULES if category in highest]
    driver = sc.build_driver(SARIF, semantic_version=tp.VERSION, rules=rule_list, supported=sc.supported_taxonomies())
    return sc.to_json(sc.build_document(driver, sc.TAXONOMIES, results, sc.provenance_stamp(RENDERER, tp.VERSION, digest)))


# =============================================================================
# The staged write and its checks (ADR-050 D4 steps 5 and 6; KB 22)
# =============================================================================

def _canonical_of(cell: Any) -> Optional[str]:
    return tp.canonical_finding_id(cell) if tp.id_matches("finding", cell) else None


def _read_back_problems(run: Run, md_path: str) -> List[str]:
    """What the next run would read from the staged markdown, by the reader that run uses (P0-1; KB 22).

    ``read_baseline_scores`` honors code fences and headings, which ``parse_markdown_table`` doesn't. So a line in one
    finding's prose that forges structure (a code fence, a heading) hides Sections 4 and 6 from it, and every owner, SLA,
    review date and persisted input would be lost on the next run, with no warning. Every open row must come back, in
    renderer form wherever its sub-scores were written, with its owner, SLA, disposition and review date as rendered.
    """
    scores = rules.read_baseline_scores(Path(md_path))
    if not scores.readable:
        return ["the staged %s would not read back as a baseline (%s)" % (MD, scores.reason)]

    def listed(ids: List[str]) -> str:
        return ", ".join(ids[:5]) + (", and more" if len(ids) > 5 else "")

    problems: List[str] = []
    expected = [row.canon for row in run.ordered]
    if set(scores.rows) != set(expected):
        problems.append("the next run would read %d of the %d open rows from the staged %s (missing: %s; unexpected: %s)" % (
            len(set(scores.rows) & set(expected)), len(expected), MD,
            ", ".join(sorted(set(expected) - set(scores.rows), key=tp.finding_sort_key)[:10]) or "none",
            ", ".join(sorted(set(scores.rows) - set(expected), key=tp.finding_sort_key)[:10]) or "none"))
    legacy = [row.canon for row in run.ordered if row.subs is not None and row.canon in scores.rows and scores.rows[row.canon].form != "renderer"]
    if legacy:
        problems.append("%d open finding(s) would read back in the legacy form although their sub-scores were written (%s): "
                        "a line in the file may forge structure, such as a code fence or a heading" % (len(legacy), listed(legacy)))
    changed = []
    for row in run.ordered:
        stored = scores.rows.get(row.canon)
        if stored is not None and (stored.owner, stored.sla, stored.disposition, stored.review_date.isoformat() if stored.review_date else None) != (
                row.owner, row.sla, row.disposition, row.review_date):
            changed.append(row.canon)
    if changed:
        problems.append("the next run would read another owner, SLA, disposition or review date than was written for %d open finding(s) (%s)"
                        % (len(changed), listed(changed)))
    return problems


def _check_staged(run: Run, md_text: str, sarif_text: str, digest: str, md_path: str) -> List[str]:
    """Everything that can be wrong with the two files as they now sit on disk. Empty when they are right.

    Row parity against the reference set, Section 2's arithmetic, SARIF N/N and the shared self-check, and the two
    files' agreement on decoded values. The markdown is read back through ``tachi_parsers`` and the SARIF through ``json``.
    The markdown at ``md_path`` is also read back through ``read_baseline_scores``, the reader the next run uses, so a
    carry that this file would break fails here (P0-1). Neither file may hold a character that D3's step 10 forbids, the
    raw markdown or any decoded SARIF string, whatever path it took to reach them (NFR-10, P0-4).
    """
    problems: List[str] = []
    forbidden = tp.forbidden_character(md_text)
    if forbidden is not None:
        problems.append("the staged %s holds the character U+%04X, which the part contract forbids, at line %d"
                        % (MD, ord(forbidden), md_text.count("\n", 0, md_text.find(forbidden)) + 1))
    expected = [row.canon for row in run.ordered]
    scored = tachi_parsers.parse_markdown_table(md_text, "## 2. Scored Threat Table", keep_bold=True)
    got = [_canonical_of(row.get("ID", "")) for row in scored]
    if sorted(map(str, got)) != sorted(expected):
        missing = sorted(set(expected) - set(got), key=tp.finding_sort_key)
        extra = sorted({str(found) for found in got} - set(expected))
        problems.append("Section 2 has %d rows for %d open findings (missing: %s; unexpected: %s)" % (
            len(got), len(expected), ", ".join(missing[:10]) or "none", ", ".join(extra[:10]) or "none"))
    elif got != expected:
        problems.append("Section 2 is not in composite-descending, S-2 order")
    expected_resolved = [finding["canon"] for finding in run.resolved]
    resolved = tachi_parsers.parse_markdown_table(md_text, "## 2a. Resolved Findings") if run.resolved else []
    if [_canonical_of(row.get("ID", "")) for row in resolved] != expected_resolved or (not run.resolved and "## 2a." in md_text):
        problems.append("Section 2a does not hold exactly the %d resolved findings of Section 4c" % len(expected_resolved))
    governed = {_canonical_of(row.get("ID", "")): row
                for row in tachi_parsers.parse_markdown_table(md_text, "## 4. Governance Fields", keep_bold=True)}
    if set(governed) != set(expected):
        problems.append("Section 4 does not hold exactly the open findings")
    headings = re.findall(r"(?m)^### (\S+) %s " % DASH, md_text)
    if sorted(map(str, (_canonical_of(heading) for heading in headings))) != sorted(expected):
        problems.append("Section 3 does not have one subsection for each open finding")
    if tachi_parsers.parse_risk_scores_severity(md_text)["total"] != len(expected):
        problems.append("Section 1's total is not the number of open findings")
    stamp = tp.read_stamp(md_text)
    if stamp is None or (stamp["renderer"], stamp["version"], stamp["input_digest"]) != (RENDERER, tp.VERSION, digest):
        problems.append("the markdown's provenance stamp is missing or wrong")
    problems += _read_back_problems(run, md_path)

    by_id = {}
    for row in scored:
        canonical = _canonical_of(row.get("ID", ""))
        if canonical is None:
            continue
        by_id[canonical] = row
        values = [tachi_parsers.parse_score(row.get(column, "")) for column in ("CVSS", "Exploit.", "Scale.", "Reach.", "Composite")]
        if any(value is None for value in values):
            problems.append("%s: a score in Section 2 is not a number" % canonical)
            continue
        try:
            composite = ts.composite(*values[:4])
            if composite != values[4] or ts.band(values[4]) != row.get("Severity"):
                problems.append("%s: Section 2's composite or severity does not follow from its four scores" % canonical)
        except ValueError:
            problems.append("%s: a score in Section 2 is not a one-decimal score from 0.0 to 10.0" % canonical)
    try:
        document = json.loads(sarif_text)
        results = document["runs"][0]["results"]
        sarif_stamp = document["runs"][0]["properties"]["tachi_provenance"]
    except (ValueError, KeyError, IndexError, TypeError):
        return problems + ["the staged SARIF is not a SARIF document with results and a provenance stamp"]
    offender = _first_forbidden(document)
    if offender is not None:
        problems.append("the staged %s holds the character U+%04X, which the part contract forbids, in %s" % (SARIF, ord(offender[1]), ascii(offender[0])))
    if sarif_stamp != {"renderer": RENDERER, "version": tp.VERSION, "input_digest": digest}:
        problems.append("the SARIF's provenance stamp is missing or wrong")
    try:
        sc.self_check(results, tool=TOOL, member_ids=expected, assignments=run.assignments, resolved_ids=expected_resolved, uri=run.uri)
    except sc.SelfCheckError as exc:
        problems += exc.problems[:10]
    for result in results:
        try:
            canonical = tp.canonical_finding_id(result["partialFingerprints"]["findingId/v1"])
            properties = result["properties"]
        except (KeyError, ValueError, TypeError):
            continue
        row, gov = by_id.get(canonical), governed.get(canonical)
        if row is None or gov is None:
            continue
        pairs = ((properties.get("security-severity"), row.get("Composite"), "composite"), (properties.get("severity-band"), row.get("Severity"), "severity"),
                 (properties.get("cvss-base-score"), row.get("CVSS"), "CVSS"), (properties.get("exploitability"), row.get("Exploit."), "exploitability"),
                 (properties.get("scalability"), row.get("Scale."), "scalability"), (properties.get("reachability"), row.get("Reach."), "reachability"),
                 (properties.get("remediation-sla"), row.get("SLA"), "SLA"), (properties.get("risk-disposition"), row.get("Disposition"), "disposition"),
                 (properties.get("risk-owner"), gov.get("Owner"), "owner"), (properties.get("review-date"), gov.get("Review Date"), "review date"),
                 (properties.get("severity-band"), gov.get("Severity"), "severity in Section 4"))
        for sarif_value, md_value, what in pairs:
            if sarif_value != md_value:
                problems.append("%s: the %s is %r in the SARIF and %r in the markdown" % (canonical, what, sarif_value, md_value))
    return problems


def _stage_and_move(run: Run, out: str, plan_id: str, md_text: str, sarif_text: str, digest: str, kept: str) -> None:
    """Write both files to ``staged/``, read them back, check them, and only then move each onto its canonical name."""
    staged_dir = tp.plan_subdir(out, STAGE, plan_id, "staged")
    try:
        if os.path.islink(staged_dir) or (os.path.lexists(staged_dir) and not os.path.isdir(staged_dir)):
            raise RenderError(2, "staged is a symbolic link or not a directory", "remove it and re-run", kept=kept)
        os.makedirs(staged_dir, exist_ok=True)
        tp.atomic_write(tp.staged_path(out, STAGE, plan_id, MD), md_text)
        tp.atomic_write(tp.staged_path(out, STAGE, plan_id, SARIF), sarif_text)
    except OSError as exc:
        raise RenderError(4, "the staged files could not be written (%s)" % (exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None
    texts = []
    for name in (MD, SARIF):
        raw, reason = _read_text_file(tp.staged_path(out, STAGE, plan_id, name))
        if raw is None:
            raise RenderError(4, "the staged %s could not be read back (%s)" % (name, reason), RETRY_REMEDY, kept=kept)
        try:
            texts.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            raise RenderError(4, "the staged %s is not strict UTF-8" % name, RETRY_REMEDY, kept=kept) from None
    problems = _check_staged(run, texts[0], texts[1], digest, tp.staged_path(out, STAGE, plan_id, MD))
    if problems:
        raise RenderError(4, "a completeness or parity check failed on the staged files: %s%s" % (
            "; ".join(problems[:5]), "; and %d more" % (len(problems) - 5) if len(problems) > 5 else ""), RETRY_REMEDY, kept=kept)
    for name in (MD, SARIF):
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


def _write_record(run: Run, out: str, plan: Mapping[str, Any], digest: str, kept: str) -> Dict[str, Any]:
    undeclared, extra = _undeclared(out, plan)
    warnings = run.warnings + extra
    counts: Dict[str, int] = {"units": plan["unit_count"], "open": len(run.rows), "resolved": len(run.resolved), "rendered": len(run.rows),
                              "parse_errors": len(run.issues), "narrative_fallbacks": run.counts["narrative_fallbacks"],
                              "truncations": run.counts["truncations"]}
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
        "outputs": [{"path": name, "sha256": tp.file_digest(os.path.join(out, name))} for name in (MD, SARIF)], "error": None,
    }
    try:
        tp.validate_stage_record(record)
        text = _dump(record)
        if len(text) > tp.MAX_DOCUMENT_BYTES[tp.STAGE_RECORD_SCHEMA]:
            raise tp.PartError("invalid", "the record is over its size cap")
        tp.atomic_write(tp.stage_record_path(out, STAGE, plan["plan_id"]), text)
    except tp.PartError as exc:
        raise RenderError(4, "the stage record this step wrote fails its own contract (%s)" % exc.detail,
                          "report this as a bug in render-risk-scores.py", kept=kept) from None
    except OSError as exc:
        raise RenderError(4, "the stage record could not be written (%s)" % (exc.strerror or "error"), RETRY_REMEDY, kept=kept) from None
    return record


def _summary(run: Run, record: Mapping[str, Any]) -> List[str]:
    counts, _shares = _distribution(run)
    lines = ["TACHI RISK-SCORE: wrote %s and %s" % (MD, SARIF),
             "%d open findings scored: %d Critical, %d High, %d Medium, %d Low" % (len(run.rows), counts["Critical"], counts["High"], counts["Medium"], counts["Low"]),
             "%d resolved findings listed in Section 2a" % len(run.resolved)]
    if run.baseline is not None:
        inherited = sum(1 for row in run.rows if row.source == "inherited")
        lines.append("%d findings carried from the baseline, %d scored fresh" % (inherited, len(run.rows) - inherited))
    flagged = sum(1 for row in run.rows if row.flags)
    if flagged:
        lines.append("%d findings carry integrity flags (Section 6 lists them)" % flagged)
    lines += ["Warning: %s: %s" % (warning["code"], warning["detail"]) for warning in record["warnings"]]
    if record["undeclared_paths"]:
        lines.append("Warning: %d paths under --out are not declared by the stage: %s" % (
            len(record["undeclared_paths"]), ", ".join(record["undeclared_paths"][:5])))
    return lines


# =============================================================================
# The command line
# =============================================================================

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=RENDERER, description="Render risk-scores.md and risk-scores.sarif from the scorer's parts (F-374).")
    parser.add_argument("--version", action="version", version="%s %s (python %s)" % (RENDERER, tp.VERSION, platform.python_version()))
    parser.add_argument("--out", required=True, help="the run's output directory; everything is written under it")
    parser.add_argument("--plan", required=True, help="the plan ID that plan printed")
    parser.add_argument("--plan-digest", required=True, help="the plan_digest that the last plan or reconcile printed")
    return parser


def _run(args: argparse.Namespace) -> int:
    try:
        ts.self_test()
    except Exception as exc:  # a calculator that drifted from FIRST's examples stops the run before a score is written
        raise RenderError(2, "the CVSS 3.1 calculator failed its self-test: %s" % str(exc)[:300],
                          "report this as a bug in tachi_scoring.py; nothing was written") from None
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
    reference = _prepare(run, plan, inputs, refs, kept)
    _score(run, reference, items, part_flags, scoring_date, kept)
    accepted = [items[key] for key in sorted(items, key=tp.finding_sort_key)]
    digest = tp.input_digest({"sources": run.sources, "params": plan["params"], "items": accepted, "fragments": []})

    md_text = _render_md(run, scoring_date.isoformat(), digest)
    sarif_text = _render_sarif(run, digest)
    _stage_and_move(run, out, args.plan, md_text, sarif_text, digest, kept)
    record = _write_record(run, out, plan, digest, kept)
    for line in _summary(run, record):
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
                       "report this as a bug in render-risk-scores.py; the earlier outputs were left or put back as they were", kept=kept)


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
