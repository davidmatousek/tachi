#!/usr/bin/env python3
"""Plan, reconcile and fail a batched stage: the one script that owns batching and resume (F-374).

A stage that has more units than one agent can write in one response is split into batches. A fresh
plan holds the batches, each with a batch input an agent reads and a part path it writes. The command
dispatches what the plan lists, and this script works out from the files on disk what is done and what
isn't, never from an agent's reply (ADR-050 D3, D4, D6; ``contracts/cli.md``).

    python3 scripts/tachi-stage.py --version
    python3 scripts/tachi-stage.py plan      --stage risk-score --out DIR --date YYYY-MM-DD --threats FILE [...]
    python3 scripts/tachi-stage.py plan      --stage compensating-controls --out DIR --date YYYY-MM-DD --risk-scores FILE --target DIR [...]
    python3 scripts/tachi-stage.py plan      --stage threat-model|threats-md --out DIR --date YYYY-MM-DD
    python3 scripts/tachi-stage.py plan      --stage trees --out DIR --date YYYY-MM-DD --threats FILE [--baseline-dir DIR]
    python3 scripts/tachi-stage.py plan      --stage report --out DIR --date YYYY-MM-DD --threats FILE --trees-plan ID --trees-plan-digest HEX
    python3 scripts/tachi-stage.py reconcile --stage S --out DIR --plan ID --plan-digest HEX
    python3 scripts/tachi-stage.py fail      --stage S --out DIR --plan ID --plan-digest HEX --reason R [--detail TEXT]
    python3 scripts/tachi-stage.py close     --stage threat-model --out DIR --plan ID --plan-digest HEX
    python3 scripts/tachi-stage.py architecture-source --threats FILE --architecture PATH
    python3 scripts/tachi-stage.py id-mark   --threats FILE (--baseline FILE | --no-baseline)
    python3 scripts/tachi-stage.py watch     --out DIR DSP [DSP ...]

Each command prints one JSON object on stdout and errors on stderr, in D4's four-line form (``TACHI <STAGE>
FAILED``, the batch or agent, ``Remedy:``, ``Kept for diagnosis:``). The exit codes are D4's:

    0 done           1 an input is missing or unreadable      2 a validation, usage or guard failure
    3 batches pending (``reconcile``), or a wave's deadline passed (``watch``)
    4 a cap or the retry budget is exhausted                  5 done, with a warning (``architecture-source`` and ``close``)

The scorer's plan sends the agent only the findings that need judgment (ADR-050 D2): the non-peers that are NEW or
UPDATED, or have no usable row in the baseline. The renderer inherits the rest, through the same
``tachi_scoring_rules.route_scorer_units``, so the planner and the renderer always agree. When ``threats.md`` is absent
the member set is read from the ``threats.sarif`` beside it (D8's fallback), and each member's unit row holds the text
of its own result (component, threat, mitigation, risk level and layer), in either ID form, from the reader that the
renderer takes the same text from (``parse_sarif_member_set(..., with_details=True)``, P0-3).

The controls plan sends the agent every scored open finding (ADR-050 D2, D8, D9), because the agent copies an UNCHANGED
result from its batch input. The units are the open rows of ``--risk-scores``, read through the tolerant reader that the
renderer reads that file with (``tachi_scoring_rules.read_baseline_scores``), or, when it is absent, the ``risk-scores.sarif``
beside it. Each row holds the finding's Section 7 values from the ``threats.md`` that the input's validated ``source_file``
names (a SARIF names none, so its rows hold each member's own text instead). An UNCHANGED finding's row also holds its
baseline's persisted result (``evidence[]``, ``matrix_row``, ``recommendation_body`` and the judgment values, narrative text
included), decoded, from the baseline's Section 7 ``### Assessment Inputs`` through
``tachi_parsers.parse_controls_assessment_inputs``, never from the rendered file (AR-T3). A row built from ``threats.md`` also holds
the finding's MAESTRO ``layer``, by the renderer's chain (Section 7's cell, else the finding's own row in a per-finding table,
else the component's Section 1 layer, else ``Unclassified``), under the key that the SARIF fallback's rows use. In that fallback, a member that the renderer
could not score ends the plan here, before dispatch (KB 22): one that no result of its own names (a legacy peer reference), or whose
result gives no composite from 0.0 to 10.0 on the 0.1 grid.

Every string that a batch input would carry is checked against D3 step 10's character set before anything is written, a
baseline's persisted result included, and a character that it forbids is exit 2, naming the finding, the field and the file
(P0-4, SA-1). A file whose path this step derives (the SARIF beside a markdown input) is read only when it is a regular file
and no link (SA-10). A file that this step reads only to take its digest as a plan input is read the same way, and at most 16 MiB (S7-4).

The plan holds the stage's pointers as ``refs`` (the authority, so a plan with no units keeps them), and each batch input
copies them for its agent. A ``--architecture`` candidate that the shared resolver refuses, whatever check fails, is left
out of ``refs`` and recorded as the plan's ``architecture_warning``, which the renderer's stage record lists first (D7).

The planner is also a function, :func:`plan_stage`. Batch sizes are constants in ``BATCH_SIZES``, not adopter
settings, so ``plan_stage``'s ``batch_size`` argument is the one way a test sets a smaller one (D6).

PR 2 adds four stages and two modes (``contracts/cli.md``; ``contracts/part-files.md``). Each stage takes only its own pointers (S1P-A63):

* ``threat-model``, the run-level plan of Step 1.5, plans no unit and reads no file. It copies the pre-images of the run's four canonical files and takes
  the ``{out}`` snapshot, so that ``fail`` can move and restore those four and ``close`` can check the whole run against the snapshot (D4).
* ``threats-md`` plans the template's 24 tables as parts from the section manifest that the orchestrator wrote at ``{out}/.tachi-build/sections.json``
  (item O-beta). The orchestrator writes each part itself, so ``plan`` and ``reconcile`` also print each batch's part path, table, rows and last problem.
* ``trees`` plans the open Critical and High findings whose tree an agent generates, by the tree agent's own Step 1 table (Rule 1, Rule 2 with Rule 3's
  units, no baseline, no-op), from the joined ``threats.md`` and the baseline's ``attack-trees/``. ``reconcile`` also holds each tree file to
  ``tachi_parsers.attack_tree_source`` (D14).
* ``report`` plans the report's sections as parts, after ``assemble-report.py trees`` and over the trees plan it pins (item O-gamma, RR3).
* ``close`` ends the run-level plan on the success path: it folds in the two checks' hand-off files (``part-files.md`` section 6), checks the declared
  paths of the whole run and writes the run's stage record. ``fail`` folds the same files, and for a batch stage it writes its failed record and moves nothing.
* ``id-mark`` writes the ID high-water mark line of ``threats.md`` (ruling B).

``watch`` is Phase 2's bound (ADR-050 D6; ``contracts/threat-model-records.md``, "The watch"). The orchestrator starts one in the
background with each wave of threat-agent dispatches, naming the wave's dispatch IDs. It looks every ``WATCH_POLL_SECONDS`` for each
dispatch's record under ``--out``, and exits 0 once every one has it, or exits 3 when ``WATCH_SECONDS`` have passed on the monotonic clock,
printing the IDs that have none, so a dispatch whose agent never returns can't hold the run for good. It writes nothing, not even a stage
record: the orchestrator writes each timed-out dispatch's record from that exit. The deadline is a constant and not an adopter setting, and
:func:`watch`'s ``seconds`` and ``poll`` arguments are the one way a test sets a smaller one.

Everything the batch commands write sits under ``--out``, and every path under it is recomputed from ``--out``, the
stage and allow-listed IDs by ``tachi_parts``' layout builders, never read from a file, except the plan's
digest-checked ``inputs``. ``architecture-source`` is the one other writer: it edits the one ``--threats`` file in
place. Standard library only, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("tachi-stage.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import datetime
import os
import platform
import re
import stat
import time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_write_confinement.py)
    sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sarif_common as sc  # noqa: E402
import tachi_parsers as tpar  # noqa: E402  (PR 2 calls `parse_chain_outcome` and `attack_tree_source` through the module: the assemblers share them)
import tachi_parts as tp  # noqa: E402
import tachi_scoring as ts  # noqa: E402
import tachi_scoring_rules as rules  # noqa: E402
from tachi_parsers import (  # noqa: E402
    ReferenceSetError, parse_attack_chains, parse_baseline_frontmatter, parse_controls_assessment_inputs, parse_correlation_groups,
    parse_finding_layers, parse_markdown_table, parse_reference_set, parse_sarif_member_set, parse_score)

CONTROLS = "compensating-controls"
THREAT_MODEL = "threat-model"   # PR 2's run-level plan (Step 1.5): it plans no unit, and it owns D4's four canonical files
THREATS_MD = "threats-md"       # PR 2's batch stages: the parts of threats.md, the tree files, and the sections of the report
TREES = "trees"
REPORT = "report"
PR2_STAGES = (THREAT_MODEL, THREATS_MD, TREES, REPORT)

# ADR-050 D6, "Amended at W1": the output budget per stage in units per batch. A stage at or below its size
# plans one batch, so its agent runs once (NFR-4). `trees` is PR 2's stage, listed so the sizes live in one table. The sizes of `threats-md` are the
# template's tables' own (``tachi_parts.THREATS_MD_SECTIONS``), and those of `report` are its findings parts' (``REPORT_SIZES``).
BATCH_SIZES = {"risk-score": 13, CONTROLS: 11, TREES: 12}
# Item O-gamma's findings parts: rows per part, as floor(8,000 x 2.598 / p90) (part-files.md, "Sizes"). A section part is never split at planning.
REPORT_SIZES = {"threat_analysis": 22, "remediation_roadmap": 144}
LARGE_RUN = 30  # part-files.md, "Narrated or summarized": over this many open findings, a Medium, Low or Note finding is summarized by its category

# The pointers that each PR 2 plan takes (S1P-A63): any other pointer flag is exit 2, so a stale pointer in a command line is refused and never ignored.
PLAN_POINTERS = {THREAT_MODEL: (), THREATS_MD: (), TREES: ("threats", "baseline_dir"), REPORT: ("threats", "trees_plan", "trees_plan_digest"),
                 "risk-score": ("threats", "risk_scores", "baseline_dir", "architecture", "target"),
                 CONTROLS: ("threats", "risk_scores", "baseline_dir", "architecture", "target")}

# What an UNCHANGED controls unit's row takes from its baseline's persisted result (ADR-050 D2, AR-T3): the controls payload's
# keys that the agent copies as they stand. `carried_forward` is left out, because the agent sets it true when it copies.
CARRIED_KEYS = ("control_status", "control_category", "confidence", "evidence", "matrix_row", "recommendation_body")

WAVE_SIZE = 16          # S-8: at most 16 in flight per wave, which leaves margin under Claude Code's 20
MAX_ATTEMPT = 3         # P-8: the original and at most two retries per lineage
MAX_BATCHES = 999       # the batch ID is B followed by three digits

# --reason -> (what failed, the remedy). The first is the message's reason, and the second its `Remedy:` line.
REASONS = {
    "agent-not-spawned": (
        "a typed agent could not be spawned",
        "run scripts/install.sh to install the tachi agents and scripts, then re-run the command"),
    "unrecoverable-batch": (
        "a batch could not be completed within the retry caps",
        "re-run the command, and report the kept plan directory if the same batch fails again"),
    "check-failed": (
        "a completeness or parity check failed",
        "re-run the command; the earlier outputs were left or put back as they were"),
    "render-failed": (
        "the renderer failed",
        "re-run the command; the earlier outputs were left or put back as they were"),
}

_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.ASCII)


# D4's stop, with its exit code and its four-line message, is ``tachi_parts``' (#443): this entry's own name for it, with the same constructor and
# ``text()``. The plan guard and the document reader that moved there raise it too, so ``main`` catches one class (S1P-A11).
StageError = tp.StageFailure


# =============================================================================
# Small helpers: time, documents, arguments
# =============================================================================

# This entry's names for what ``tachi_parts`` shares with the renderers (#443): the clock, and stable JSON (sorted keys, two-space indent, ASCII
# escapes, one trailing newline).
_utc_now = tp.utc_now
_dump = tp.dump_json


def _write_document(stage: str, path: str, obj: Dict[str, Any], schema: str, validator: Any) -> str:
    """Write one planner or record document, only if it passes its own validator and its size cap. Returns its text.

    The validator is the reader's: a writer that produced a document its readers refuse would end the stage later,
    far from the cause. A writer never writes a document over its cap (ruled at W1).
    """
    try:
        validator(obj)
    except tp.PartError as exc:
        raise StageError(2, stage, "a %s this step wrote fails its own contract (%s)" % (schema, exc.detail),
                         "report this as a bug in tachi-stage.py") from None
    text = _dump(obj)
    if len(text) > tp.MAX_DOCUMENT_BYTES[schema]:
        raise StageError(2, stage, "a %s would be %d bytes, over its cap of %d" % (schema, len(text), tp.MAX_DOCUMENT_BYTES[schema]),
                         "reduce the input (fewer or shorter findings) and re-run")
    tp.atomic_write(path, text)
    return text


def _out_dir(stage: str, out: Any, missing_code: int = 1) -> str:
    """``--out`` as an absolute path that every document can carry, and that is a directory (``missing_code`` if not)."""
    text = os.path.abspath(os.fspath(out))
    problem = tp.path_problem(text, allow_absolute=True)
    if problem is not None:
        raise StageError(2, stage, "--out is not an acceptable path (%s)" % problem,
                         "use a directory whose path has no backslash, backtick or control character")
    if not os.path.isdir(text):
        raise StageError(missing_code, stage, "--out %s is not a directory" % text, "create it or correct --out")
    return text


# D3: IDs and digests pass their allow-lists, as ASCII full matches, before they become paths. These two checks are ``tachi_parts``' (#443), which the
# renderers and the new entries share. ``_out_dir`` stays this entry's own: it vets the path (D7), names it in its message and takes its exit code.
_plan_arguments = tp.plan_arguments


# A file's digest, or None when it is missing, unreadable, or (given ``out``) fails the path guard. ``reconcile`` and ``fail`` check what the plan
# recorded through it, so a file that can't be read counts as one that changed.
_digest_or_none = tp.digest_or_none


def _wave_entry(out: str, stage: str, plan_id: str, entry: Dict[str, Any], units: Optional[List[Dict[str, Any]]], problem: Optional[str]) -> Dict[str, Any]:
    """What ``plan`` and ``reconcile`` print for one batch to dispatch: PR 1's ``{batch_id, input_path}``, and for ``threats-md``, whose parts the
    orchestrator writes without reading the batch input, also ``{part_path, section, finding_ids, rows, problem}`` (item O-beta; part-files.md).

    ``rows`` is ``[first, last]``, 1-based and both included, for a row section, and ``None`` for a finding section. ``problem`` is ``None`` on a first
    attempt, and otherwise what was wrong with the attempt before (``_problem``).
    """
    shown: Dict[str, Any] = {"batch_id": entry["batch_id"], "input_path": tp.input_path(out, stage, plan_id, entry["batch_id"])}
    if stage == THREATS_MD:
        numbers = [unit["row"] for unit in units or [] if "row" in unit]
        shown.update(part_path=tp.part_path(out, stage, plan_id, entry["batch_id"], entry["attempt"]), section=units[0]["section"] if units else None,
                     finding_ids=list(entry["finding_ids"]), rows=[numbers[0], numbers[-1]] if numbers else None, problem=problem)
    return shown


def _waves(out: str, stage: str, plan_id: str, entries: List[Dict[str, Any]], units: Optional[Dict[str, List[Dict[str, Any]]]] = None,
           problems: Optional[Dict[str, str]] = None) -> List[List[Dict[str, Any]]]:
    """The batches to dispatch, in waves of at most ``WAVE_SIZE`` (S-8). ``units`` and ``problems`` are by batch ID, for the one stage that prints them."""
    flat = [_wave_entry(out, stage, plan_id, e, (units or {}).get(e["batch_id"]), (problems or {}).get(e["batch_id"])) for e in entries]
    return [flat[start:start + WAVE_SIZE] for start in range(0, len(flat), WAVE_SIZE)]


def _runs(count: int, size: int) -> List[tuple]:
    """``(start, stop)`` of each batch of ``count`` units at most ``size`` each: contiguous, balanced, differing by at most 1 (D3's batch granularity)."""
    planned = -(-count // size)
    base, extra = divmod(count, planned) if planned else (0, 0)
    runs, at = [], 0
    for number in range(planned):
        take = base + (1 if number < extra else 0)
        runs.append((at, at + take))
        at += take
    return runs


# =============================================================================
# plan
# =============================================================================

def _read_capped(stage: str, path: str, remedy: str, regular: bool = False) -> bytes:
    """A file's bytes, at most 16 MiB (D3 step 2), or a ``StageError``: exit 1 when it can't be read, exit 2 when it is over the cap.

    With ``regular``, a file that is a link, or isn't a regular file, is refused first with exit 2 (SA-10, S7-4). That is
    ``tachi_parts.path_guard_problem`` over the file's own directory, so a link in the directory's path is followed and the file
    itself may be none. It is for a path that this step derives, and for a file whose digest becomes a plan input. It is not for
    ``--threats``, which the operator names and may point through a link. A file that isn't there is left to the read, which
    gives the ordinary exit 1.
    """
    if regular and tp.path_guard_problem(path, os.path.dirname(path)) not in (None, "missing"):
        raise StageError(2, stage, "%s is a symbolic link or not a regular file" % path, "name the file itself, not a link to it")
    try:
        with open(path, "rb") as handle:
            raw = handle.read(tp.MAX_AGENT_INPUT_BYTES + 1)
    except OSError as exc:
        raise StageError(1, stage, "cannot read %s (%s)" % (path, exc.strerror or "error"), "check the path and re-run") from None
    if len(raw) > tp.MAX_AGENT_INPUT_BYTES:
        raise StageError(2, stage, "%s is over %d bytes" % (path, tp.MAX_AGENT_INPUT_BYTES), remedy)
    return raw


def _read_threats(stage: str, path: str, remedy: str = "regenerate threats.md with /tachi.threat-model", regular: bool = False) -> tuple:
    """The bytes and text of ``threats.md`` (or of another input, with its own ``remedy``): at most 16 MiB (D3 step 2) and strict UTF-8.

    ``regular`` is ``_read_capped``'s: a file that is a link, or isn't a regular file, is refused first (exit 2)."""
    raw = _read_capped(stage, path, remedy, regular=regular)
    try:
        return raw, raw.decode("utf-8")
    except UnicodeDecodeError:
        raise StageError(2, stage, "%s is not strict UTF-8" % path, remedy) from None


def _read_reference(stage: str, threats: Any, threats_path: str) -> tuple:
    """``threats.md`` read as the stages read it: ``(raw bytes, text, the reference set)`` (S-12, KB 22).

    The reference set is ``parse_reference_set``'s, so an unreadable Section 7 ends the run here, before anything is written or dispatched (exit 2, with
    the reader's reason and remedy). A canonical ID that Section 7 repeats is read once, and stderr says which (the first row wins).
    """
    raw, text = _read_threats(stage, threats_path)
    try:
        reference = parse_reference_set(text, source=os.fspath(threats))
    except ReferenceSetError as exc:
        raise StageError(2, stage, "%s. Expected %s" % (exc.reason, exc.expected), exc.remedy) from None
    for canonical in reference["duplicates"]:
        sys.stderr.write("WARNING: %s lists %s more than once; the first row is used\n" % (threats_path, canonical))
    return raw, text, reference


def _derived_sibling(path: str) -> bool:
    """Whether ``path``, a file that this step derives from another input's name (the SARIF beside a markdown input), is there and may be read.

    A link, or anything that isn't a regular file, is left unread with a warning, so the fallback isn't taken and the run goes on by the
    rules it already has for a missing input (SA-10). The directory is one that a repository may fill, and git stores links.
    """
    if not os.path.lexists(path):
        return False
    if tp.path_guard_problem(path, os.path.dirname(path)) is not None:
        sys.stderr.write("WARNING: %s is a symbolic link or not a regular file, so it is not read as the fallback input\n" % path)
        return False
    return True


def _unit_row(finding: Dict[str, Any]) -> Dict[str, Any]:
    """One unit row for a batch input: Section 7's row as verbatim data, with the canonical ID."""
    row = {"finding_id": tp.canonical_finding_id(finding["id"])}
    for key in ("component", "threat", "risk_level", "mitigation", "agentic_pattern", "delta_status"):
        if key in finding:
            row[key] = finding[key]
    return row


# What a unit row of D8's SARIF fallback takes from its member's own result (P0-3): the keys of
# ``parse_sarif_member_set(..., with_details=True)`` that a row has a place for, in ``_unit_row``'s order, and the layer after them.
_SARIF_ROW_KEYS = ("component", "threat", "risk_level", "mitigation", "layer")
_SCORE_MIN, _SCORE_MAX = Decimal("0.0"), Decimal("10.0")


def _sarif_risk_level(level: str) -> str:
    """A fallback member's risk level, as the renderer shows it (D8, P0-3): a word stays as the file writes it, a score becomes its band.

    ``security-severity`` is a score, never a band. It is put on the 0.1 grid inside 0.0 to 10.0 that ``tachi_scoring.band`` takes
    (the steps of ``render-risk-scores.py``'s own ``_risk_level``), so the planner's row and the renderer's "Original Risk Level" are
    one label whatever the result carries.
    """
    score = parse_score(level)
    return level if score is None else ts.band(ts.q1(max(_SCORE_MIN, min(_SCORE_MAX, score))))


def _sarif_unit_row(finding_id: str, details: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """The unit row of a member of D8's SARIF fallback: its canonical ID, and each detail that its own result gives (P0-3).

    ``details`` is the member's entry of ``parse_sarif_member_set(..., with_details=True)``, the one reader that the renderer takes the
    same text from, so a result gives its component, threat, mitigation, risk level and layer here as it gives them there, in either
    ID form. A detail the result lacks is left out, as ``_unit_row`` leaves out a value the finding lacks. A member that only a legacy
    peer reference names has no result, so it has no entry (``{}``) and its row holds the ID alone. A result records no status, so
    there is none here: the routing derives it from the baseline (S-12(b)). Each string is verbatim data, as in ``_unit_row``, with
    one refusal: JSON can spell a lone surrogate (``\\ud800``), which no markdown input can, and ``tachi_parts.load_json`` refuses a
    document with one, so a batch input that held it would plan and then fail its first retry. It raises ``ValueError`` instead, and
    the caller ends the run here, as for any other SARIF it can't use.
    """
    row: Dict[str, Any] = {"finding_id": finding_id}
    for key in _SARIF_ROW_KEYS:
        value = details.get(key)
        if value is None:
            continue
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("the %s of %s holds a lone surrogate code point, which a batch input cannot carry" % (key, finding_id)) from None
        row[key] = _sarif_risk_level(value) if key == "risk_level" else value
    return row


def _first_forbidden(value: Any, path: str) -> Optional[tuple]:
    """``(path, character)`` of the first string under ``value`` that holds a character D3's step 10 forbids, or ``None`` (P0-4).

    ``tachi_parts.first_forbidden``, the one walk that the parts, the renderers' inputs and this planner share, limited here to what a JSON
    document holds (S1P-A12): text, ``dict`` keys and values, and ``list`` items, in order. A tuple, another kind of mapping, an object, a
    number and ``None`` hold no text. ``path`` is dotted, and is for a message only.
    """
    return tp.first_forbidden(value, path, json_only=True)


def _refuse_forbidden_units(stage: str, units: List[Dict[str, Any]], text_path: str) -> None:
    """Exit 2, before anything is written, when a value that a batch input would carry holds a character that D3's step 10 forbids (P0-4, SA-1).

    Step 10 checks a part. A row's text comes from ``threats.md`` or a SARIF, and the renderer would refuse it only after every agent had
    run. A controls unit also carries its baseline's persisted result, which the agent copies back into its part verbatim, so one
    forbidden character in it would fail that part on every attempt and the batch would be dispatched until its retries ran out.
    So each string of each unit is checked here, and the message names the finding, the field and the file that the value came from
    (``text_path`` for a row's text, the baseline's ``compensating-controls.md`` for a carried result), with the regenerate-or-edit
    remedy. It gives the character's code point and never the text, so it can't carry the character to a terminal.
    """
    plain = os.path.basename(text_path)
    for unit in units:
        for key, value in unit.items():
            carried = key in CARRIED_KEYS
            where = "the baseline compensating-controls.md" if carried else plain
            # a finding's unit names the finding; PR 2's section units (a report fragment key, a table's rows) name their key
            problem = tp.forbidden_problem(where, unit.get("finding_id") or unit.get("key") or unit.get("section"), value, json_only=True, path=key)
            if problem is None:
                continue
            command = "/tachi.compensating-controls" if carried else "/tachi.risk-score" if plain == "risk-scores.sarif" else "/tachi.threat-model"
            raise StageError(2, stage, problem,
                             "regenerate %s with %s, or edit the value to remove the character, then re-run the command" % (where, command))


def _architecture_ref(stage: str, candidate: Any) -> tuple:
    """The architecture candidate through the shared resolver's first step (ADR-050 D7), as ``(path, warning)``.

    ``sarif_common.resolve_explicit`` is the step ``resolve_architecture`` runs first, so ``plan`` and the renderer
    agree on every check and on the warning's code and text, and ``architecture-source`` makes the same checks under
    the same code. The path is absolute and in its canonical spelling: a regular file below the working directory,
    with no symlink on the way, spelled as the volume spells it. So ``refs.architecture`` and the body line name one
    path. A candidate it refuses, whatever check fails (a control character, backslash or backtick included, which
    used to exit 2), is left out of ``refs``, so the agents never see it, and ``(None, warning)`` comes back for the
    plan to record as its ``architecture_warning`` (ruled at W2). Nothing here stops a run (D7). stderr gets one
    ``WARNING`` line that names the candidate, escaped and untruncated, and the failed check, which is the last part
    of the warning's code. The line is this step's own: the warning's detail shortens the candidate to 80 characters.
    """
    given = os.fspath(candidate) if isinstance(candidate, os.PathLike) else candidate  # as typed, so a `..` or a link is refused as `architecture-source` refuses it
    root = os.getcwd()
    resolved, warning = sc.resolve_explicit(given, root=root)
    if resolved is None:
        check = warning["code"].rpartition(":")[2]  # a refusal always comes with its warning
        sys.stderr.write("WARNING: the architecture path %r is not used (%s), so it is not passed to the agents\n" % (given, check))
        return None, warning
    path = os.path.join(root, resolved.path)
    problem = tp.path_problem(path, allow_absolute=True)  # the working directory itself can hold a character a document can't carry
    if problem is not None:
        raise StageError(2, stage, "--architecture resolves to a path that documents cannot carry (%s)" % problem,
                         "run from a directory whose path has no backslash, backtick or control character")
    return path, None


def _pointer_refs(stage: str, risk_scores: Any, baseline_dir: Any, architecture: Any, target: Any) -> tuple:
    """The optional ``--risk-scores``, ``--baseline-dir``, ``--architecture`` and ``--target`` pointers.

    Each becomes an absolute path under its closed ``refs`` name, and a file that the stage reads also becomes a
    digest-checked input, so a change during the run is caught. The architecture goes through the shared resolver
    (``_architecture_ref``) and needs no syntactic pre-check: a candidate it refuses is dropped with a warning, which
    the plan records, because a stage never stops for it (ADR-050 D7). ``--baseline-dir`` is only checked here: it
    may name a run directory or a file in one (D9), and each stage's routing resolves it. The controls stage passes
    ``risk_scores=None``, because it reads that input itself (``_controls_scored_input``). It returns
    ``(inputs, refs, baseline, architecture_warning)``, where ``baseline`` is that checked path or ``None``.
    """
    inputs: Dict[str, Dict[str, Any]] = {}
    refs: Dict[str, str] = {}
    baseline: Optional[str] = None
    architecture_warning: Optional[Dict[str, str]] = None
    for name, given, kind in (("risk_scores", risk_scores, "file"), ("baseline_dir", baseline_dir, "baseline"),
                              ("architecture", architecture, "candidate"), ("target", target, "dir")):
        if given is None:
            continue
        if kind == "candidate":
            resolved, architecture_warning = _architecture_ref(stage, given)
            if resolved is not None:
                refs[name] = resolved
            continue
        path = os.path.abspath(os.fspath(given))
        problem = tp.path_problem(path, allow_absolute=True)
        if problem is not None:
            raise StageError(2, stage, "--%s is not an acceptable path (%s)" % (name.replace("_", "-"), problem),
                             "use a path with no backslash, backtick or control character")
        if kind == "baseline":
            if not os.path.exists(path):
                raise StageError(1, stage, "--baseline-dir %s names nothing" % path, "check the path and re-run")
            baseline = path
            continue
        if not (os.path.isfile(path) if kind == "file" else os.path.isdir(path)):
            raise StageError(1, stage, "--%s %s is not a %s" % (name.replace("_", "-"), path, "file" if kind == "file" else "directory"),
                             "check the path and re-run")
        refs[name] = path
        if kind == "file":
            inputs[name] = _input_entry(stage, path)
    return inputs, refs, baseline, architecture_warning


def _input_entry(stage: str, path: str, raw: Optional[bytes] = None) -> Dict[str, Any]:
    """A digest-checked plan input: its absolute path, SHA-256 and size. Given no ``raw``, the file is read here: at most 16 MiB,
    and not through a link, as every other read of an input is (S7-4)."""
    if raw is None:
        raw = _read_capped(stage, path, "name a smaller file", regular=True)
    return {"path": os.path.abspath(path), "sha256": tp.sha256_hex(raw), "bytes": len(raw)}


# ``(relative path, size, mtime_ns)`` for every file under ``out``, in a fixed order, links to directories not followed: the walk that D4's snapshot
# and the declared-paths check share with the renderers (#443).
_walk = tp.walk_out


# A file's key in the plan's ``out_snapshot`` is ``tachi_parts.snapshot_key`` (SA-5), which both renderers look a file up by too (EC-2). This name is
# the planner's own, as its tests call it.
_snapshot_key = tp.snapshot_key


def _snapshot(out: str) -> Optional[Dict[str, List[int]]]:
    """D4's ``{out}`` snapshot: each path with its size and ``mtime_ns``, under the key that ``_snapshot_key`` gives it. None above
    20,000 entries, and the declared-paths check is then skipped with a warning."""
    entries: Dict[str, List[int]] = {}
    for relpath, size, mtime in _walk(out):
        if len(entries) >= tp.MAX_SNAPSHOT_ENTRIES:
            sys.stderr.write("WARNING: the {out} snapshot is skipped, so the declared-paths check is too (more than %d files)\n"
                             % tp.MAX_SNAPSHOT_ENTRIES)
            return None
        entries[_snapshot_key(relpath)] = [size, mtime]
    return entries


def _take_preimages(stage: str, out: str, plan_id: str) -> Dict[str, Optional[str]]:
    """Copy each existing canonical output of the stage into ``preimage/`` and record its digest (D4).

    A name that holds no regular file records null: ``fail`` then puts nothing back.
    """
    preimage: Dict[str, Optional[str]] = {}
    for name in tp.CANONICAL_OUTPUTS[stage]:
        path = os.path.join(out, name)
        try:
            is_regular = stat.S_ISREG(os.lstat(path).st_mode)
        except OSError:
            is_regular = False
        if not is_regular:
            preimage[name] = None
            continue
        with open(path, "rb") as handle:
            data = handle.read()
        tp.atomic_write(tp.preimage_path(out, stage, plan_id, name), data, mode_of=path)  # the copy keeps the output's bits, for ``fail`` to put back (P1-2)
        preimage[name] = tp.sha256_hex(data)
    return preimage


def _prepare_directories(stage: str, out: str, plan_id: str) -> None:
    """Make ``.tachi-build/<stage>/<plan_id>/`` and its first three subdirectories, through no link (KB 24).

    ``.tachi-build`` and the stage directory are checked one by one, and the plan directory is new, so everything
    this step makes lies under ``--out`` by identity.
    """
    for directory in (os.path.join(out, tp.BUILD_DIR), tp.stage_dir(out, stage)):
        if os.path.islink(directory) or (os.path.lexists(directory) and not os.path.isdir(directory)):
            raise StageError(2, stage, "%s is a symbolic link or not a directory" % directory, "remove it and re-run")
        os.makedirs(directory, exist_ok=True)
    try:
        os.mkdir(tp.plan_dir(out, stage, plan_id))
        for name in ("inputs", "parts", "preimage"):
            os.mkdir(tp.plan_subdir(out, stage, plan_id, name))
        if stage == TREES:  # the trees an agent writes sit beside the parts, and no later step makes the directory (D6, D14)
            os.mkdir(os.path.join(tp.plan_dir(out, stage, plan_id), "trees"))
    except OSError as exc:
        raise StageError(2, stage, "cannot make the plan directory (%s)" % (exc.strerror or "error"), "re-run the command") from None


def _tree_path(out: str, plan_id: str, finding_id: str) -> str:
    """Where the agent writes a finding's tree: ``<plan dir>/trees/<id in lower case>-attack-tree.md`` (D3, D14), built from ``--out``, the plan ID and the
    finding ID, which passes its allow-list first, and from nothing that a file says. The ID is canonical, so ``AGP-1`` is ``agp-1-attack-tree.md``."""
    return os.path.join(tp.plan_dir(out, TREES, plan_id), "trees", "%s-attack-tree.md" % tp.canonical_finding_id(finding_id).lower())


def _write_batch_input(stage: str, out: str, plan: Dict[str, Any], entry: Dict[str, Any], units: List[Dict[str, Any]]) -> None:
    """Write a batch's input for its current attempt, and record its digest in the plan's entry.

    The input's ``refs`` and ``params`` are verbatim copies of the plan's: the plan is the authority, and the agent
    reads only its batch input (the dispatch prompt is fixed). A retry's input is written the same way, so it
    copies the plan's ``refs`` and not its parent's (ruled at W2). A ``trees`` batch also names the path of each of its trees (``_tree_path``).
    """
    body = {
        "schema": tp.BATCH_INPUT_SCHEMA, "plan_id": plan["plan_id"], "batch_id": entry["batch_id"], "stage": stage,
        "agent_type": plan["agent_type"], "finding_ids": list(entry["finding_ids"]), "attempt": entry["attempt"],
        "part_path": tp.part_path(out, stage, plan["plan_id"], entry["batch_id"], entry["attempt"]),
        "tree_paths": {finding_id: _tree_path(out, plan["plan_id"], finding_id) for finding_id in entry["finding_ids"]} if stage == TREES else {},
        "units": units, "refs": plan["refs"], "params": plan["params"],
    }
    text = _write_document(stage, tp.input_path(out, stage, plan["plan_id"], entry["batch_id"]), body,
                           tp.BATCH_INPUT_SCHEMA, tp.validate_batch_input)
    entry["input_sha256"] = tp.sha256_hex(text.encode("utf-8"))


def _read_member_set(stage: str, threats: Any, threats_path: str) -> tuple:
    """The open findings of the run, as ``(raw bytes, [(finding row, unit row)], threats.md text, path read, SARIF groups, lacking)``.

    They come from the reference set of ``threats.md`` (S-12). The scorer falls back to the ``threats.sarif`` beside it
    when ``threats.md`` is absent, and that file is a regular file and no link (``_derived_sibling``, SA-10). It is read through
    ``parse_sarif_member_set`` (ADR-050 D8, AR-T2): each unit row holds the
    text of that member's own result, in either ID form (``_sarif_unit_row``, P0-3), and the agent reads the rest from
    ``refs.threats``. An empty extraction is an error, never a pass (KB 22), and it ends the run here, before anything is
    written or dispatched.

    ``lacking`` maps each canonical ID to the names of the values its form lacks (S-12(b)): the reference set's own
    map, or, for the SARIF fallback, ``{id: ["delta_status"]}`` for every member, since a SARIF result records no
    status. The routing derives each missing status from the baseline, and the renderer passes the same map (ruled at W2).
    The SARIF's groups come back as the reader gives them, a group with no ID included: its peers route like any other
    (D9), and the renderer routes the same groups, so the two sides cut one partition.
    """
    beside = os.path.join(os.path.dirname(threats_path), "threats.sarif")
    if not (stage == "risk-score" and os.path.basename(threats_path) == "threats.md"
            and not os.path.lexists(threats_path) and _derived_sibling(beside)):
        raw, text, reference = _read_reference(stage, threats, threats_path)
        return raw, [(finding, _unit_row(finding)) for finding in reference["open"]], text, threats_path, [], reference["lacking"]
    sys.stderr.write("WARNING: %s is absent, so the findings are read from %s (the SARIF fallback)\n" % (threats_path, beside))
    raw, text = _read_threats(stage, beside)
    try:
        member_set = parse_sarif_member_set(text, with_details=True)
        members = sorted(member_set["members"], key=tp.finding_sort_key)
        units = [({"id": member}, _sarif_unit_row(member, member_set["details"].get(member, {}))) for member in members]
    except ValueError as exc:
        raise StageError(2, stage, "%s: %s" % (beside, str(exc)[:200]), "restore threats.md, or regenerate it with /tachi.threat-model") from None
    return raw, units, None, beside, member_set["groups"], {member: ["delta_status"] for member in members}


def _scorer_routing(stage: str, members: list, text: Optional[str], sarif_groups: list, lacking: Dict[str, List[str]],
                    baseline_flag: Optional[str], extra_inputs: Dict[str, Dict[str, Any]], refs: Dict[str, str]) -> "rules.ScorerRouting":
    """Who the scorer agent scores (ADR-050 D2, D9): the baseline is resolved, read, and the units are partitioned.

    The baseline is the ``--baseline-dir`` pointer, else ``baseline.source`` of the input ``threats.md`` (R-6). A
    baseline that does not resolve, or whose ``risk-scores.md`` is missing or unreadable, means every finding is
    scored fresh, and a warning says why (S-12(d)): it never stops the run. A baseline in use is recorded as
    ``refs.baseline_dir`` and its files as digest-checked inputs, so the renderer routes against the same files.
    A finding whose form lacks ``delta_status`` takes its status from the baseline in ``route_scorer_units``, the one
    place that derives it: UNCHANGED, and carried, when the baseline has a usable open row for its ID, and NEW otherwise.
    """
    source = parse_baseline_frontmatter(text)["source"] if text is not None else None
    resolution = rules.resolve_baseline(flag=baseline_flag, baseline_source=source, cwd=Path(os.getcwd()))
    scores = None
    if resolution.run_dir is not None:
        refs["baseline_dir"] = os.fspath(resolution.run_dir)
        scored, sarif = resolution.files.get("risk-scores.md"), resolution.files.get("risk-scores.sarif")
        if scored is None:
            sys.stderr.write("WARNING: the baseline run directory has no usable risk-scores.md (%s), so every finding is scored fresh\n"
                             % resolution.file_reasons.get("risk-scores.md", "missing"))
        else:
            scores = rules.read_baseline_scores(scored, sarif_path=sarif)
            if scores.readable:
                extra_inputs["baseline_risk_scores"] = _input_entry(stage, os.fspath(scored))
                if sarif is not None and os.path.getsize(sarif) <= tp.MAX_AGENT_INPUT_BYTES:
                    extra_inputs["baseline_risk_scores_sarif"] = _input_entry(stage, os.fspath(sarif))
            else:
                sys.stderr.write("WARNING: the baseline risk-scores.md can't be read (%s), so it counts as missing: its owners, SLAs and "
                                 "dispositions are not carried, and every finding is scored fresh\n" % scores.reason)
    elif resolution.reason != "not-named":
        sys.stderr.write("WARNING: no baseline is used (%s: %s), so every finding is scored fresh\n" % (resolution.origin, resolution.reason))
    rows = [row for row, _ in members]
    groups = parse_correlation_groups(text, member_ids=[row["id"] for row in rows])["groups"] if text is not None else sarif_groups
    return rules.route_scorer_units(rows, groups=groups, baseline=scores, lacking=lacking)


# =============================================================================
# The controls stage's units (T036; ADR-050 D2, D8, D9)
# =============================================================================

# The two frontmatter forms the other readers accept (``tachi_parsers.parse_frontmatter``): plain, and inside a ``yaml`` fence.
_FRONTMATTER = (re.compile(r"\A---[ \t\r]*\n(.*?)\n---", re.DOTALL), re.compile(r"```yaml[ \t\r]*\n---[ \t\r]*\n(.*?)\n---[ \t\r]*\n```", re.DOTALL))
_SOURCE_FILE_LINE = re.compile(r"^source_file[ \t]*:[ \t]*(?P<value>.*)$")


def _scored_source_file(text: str) -> Optional[str]:
    """The ``source_file`` of a ``risk-scores.md``'s frontmatter, or ``None``: the threat model that was scored (D7, D8).

    The first top-level ``source_file`` line of the frontmatter counts. A quoted value loses its quotes, and ``null``, ``~``
    and an empty value mean none. What comes back is a candidate only: ``tachi_scoring_rules.check_run_file`` validates it.
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


def _same_file(first: Any, second: Any) -> bool:
    try:
        return os.path.samefile(os.fspath(first), os.fspath(second))
    except OSError:
        return False


def _id_list(finding_ids: List[str]) -> str:
    """A short list of IDs for a warning: the first five, and a count of the rest."""
    shown = ", ".join(finding_ids[:5])
    return shown + (" and %d more" % (len(finding_ids) - 5) if len(finding_ids) > 5 else "")


def _refuse_unscorable(stage: str, name: str, found: Dict[str, Any], remedy: str) -> None:
    """Exit 2, before dispatch, for a member of D8's controls fallback that the renderer could not render (KB 22).

    ``found`` is ``parse_sarif_member_set(..., with_scores=True)``. Its ``scores`` has an entry for each member that has a result of
    its own, so a member that only a legacy peer reference names (D8 counts it a member) has none, and no score either. A member also
    needs a composite from 0.0 to 10.0 on the 0.1 grid, which is what ``render-compensating-controls.py`` takes as its inherent score
    (``_valid_inherent``). The messages and the remedy are the renderer's, from the same member data, so a run that would end there,
    after every agent had run, ends here, before any has.
    """
    for member in sorted(found["members"], key=tp.finding_sort_key):
        score = found["scores"].get(member)
        if score is None:
            raise StageError(2, stage, "%s names %s only as a peer reference, so it holds no result and no score for it" % (name, member), remedy)
        try:
            ts.band(score["composite"])
        except (ValueError, TypeError):   # no composite (None), or one off the 0.1 grid
            raise StageError(2, stage, "the input %s holds no score from 0.0 to 10.0 on the 0.1 grid for %s, so its residual risk can't be computed"
                             % (name, member), remedy) from None


def _controls_scored_input(stage: str, given: Any) -> tuple:
    """The controls stage's input, as ``(path read, its bytes, the scored finding IDs in S-2 order, markdown text or None, unit rows)``.

    The members are the open rows of ``risk-scores.md``, read through ``tachi_scoring_rules.read_baseline_scores``, the tolerant
    reader (R-26) that the renderer reads the file with, so the planner and the renderer see one set. Section 2a's RESOLVED rows
    are not in it (D8). When ``risk-scores.md`` is absent and a ``risk-scores.sarif`` lies beside it, that file is read
    instead, through ``parse_sarif_member_set`` (D8's fallback, AR-T2), and no markdown text comes back: the last item is then
    each member's unit row (``_sarif_unit_row``, P0-3), and ``{}`` for the markdown input. An empty extraction, a SARIF string
    that a document can't carry, a member that the renderer could not score (``_refuse_unscorable``), or an input that can't
    be read, is an error and ends the run here, before anything is written or dispatched (KB 22). The SARIF is read only when it
    is a regular file and no link (``_derived_sibling``, SA-10).
    """
    path = os.path.abspath(os.fspath(given))
    problem = tp.path_problem(path, allow_absolute=True)
    if problem is not None:
        raise StageError(2, stage, "--risk-scores is not an acceptable path (%s)" % problem, "use a path with no backslash, backtick or control character")
    remedy = "regenerate it with /tachi.risk-score"
    beside = os.path.join(os.path.dirname(path), "risk-scores.sarif")
    if os.path.basename(path) == "risk-scores.md" and not os.path.lexists(path) and _derived_sibling(beside):
        sys.stderr.write("WARNING: %s is absent, so the findings are read from %s (the SARIF fallback)\n" % (path, beside))
        raw, text = _read_threats(stage, beside, remedy)
        try:
            found = parse_sarif_member_set(text, with_scores=True, with_details=True)
            members = sorted(found["members"], key=tp.finding_sort_key)
            rows = {member: _sarif_unit_row(member, found["details"].get(member, {})) for member in members}
        except ValueError as exc:
            raise StageError(2, stage, "%s: %s" % (beside, str(exc)[:200]), "restore risk-scores.md, or " + remedy) from None
        _refuse_unscorable(stage, os.path.basename(beside), found, remedy)
        return beside, raw, members, None, rows
    raw, text = _read_threats(stage, path, remedy)
    scores = rules.read_baseline_scores(Path(path))
    if not scores.rows:  # the reader opens through no link, so `missing` here, after the read above, means a link or a file that isn't regular
        why = {"missing": "it is a symbolic link or not a regular file", "no-rows": "it has no scored row"}.get(scores.reason or "", "it lists no open finding")
        raise StageError(2, stage, "%s can't be the scored input (%s)" % (path, why), remedy)
    if scores.issues:
        sys.stderr.write("WARNING: %s has %d input issue(s), the first being: %s. A row that can't be read is not planned, "
                         "and the renderer lists the issues under Input Issues\n" % (path, len(scores.issues), scores.issues[0].detail[:160]))
    return path, raw, list(scores.rows), text, {}


def _controls_baseline(stage: str, resolution: "rules.BaselineResolution", inputs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """The baseline's persisted controls results by canonical ID (AR-T3), and its file as a digest-checked input.

    The file is ``compensating-controls.md`` in the baseline run directory. A result is read from its Section 7 ``### Assessment
    Inputs``, decoded, through ``parse_controls_assessment_inputs`` (T143): never from the rendered Sections 2, 3 or 4, whose text
    the renderer escaped. A pre-1.1 file has no Section 7 and gives none, and the agent copies from the file itself then (D2). A row
    the reader refuses leaves that finding without a result, so it is scanned fresh. A file that is missing or unreadable
    counts as missing (S-12(d)): it never stops the run.
    """
    path = resolution.files.get("compensating-controls.md")
    if path is None:
        sys.stderr.write("WARNING: the baseline run directory has no usable compensating-controls.md (%s), so every finding is scanned fresh\n"
                         % resolution.file_reasons.get("compensating-controls.md", "missing"))
        return {}
    try:
        raw, text = _read_threats(stage, os.fspath(path), "regenerate it with /tachi.compensating-controls")
    except StageError as exc:
        sys.stderr.write("WARNING: the baseline compensating-controls.md can't be read (%s), so it counts as missing and every finding "
                         "is scanned fresh\n" % exc.reason)
        return {}
    inputs["baseline_compensating_controls"] = _input_entry(stage, os.fspath(path), raw)
    persisted = parse_controls_assessment_inputs(text)
    if persisted["errors"]:
        sys.stderr.write("WARNING: the baseline compensating-controls.md has %d unreadable persisted row(s), the first being: %s. "
                         "Those findings are scanned fresh\n" % (len(persisted["errors"]), persisted["errors"][0]["reason"][:160]))
    return persisted["inputs"]


def _finding_layers(text: str, findings: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """Each finding's MAESTRO layer, by canonical ID, as the controls renderer takes it.

    ``findings`` holds the open rows of ``threats.md``'s Section 7 (``parse_reference_set``) and ``text`` is that file. The chain is the
    renderer's (``render-compensating-controls.py``, ``_read_reference`` and ``_overlay_reference``), and ADR-050 D2 gives it one
    reader for its first two steps (``parse_finding_layers``), so the planner's copy can't drift from the renderers': the MAESTRO Layer
    cell of the finding's own Section 7 row, else its own row in a per-finding table (§3 and §4), else the MAESTRO Layer of its
    component's Section 1 row (found by name, then case-folded; ``Unspecified`` for a row with no component, as the scorer writes
    it), else ``Unclassified``. The agent copies it, and the renderer checks the agent's cell against it, so a row without it
    would have the agent guess and every classified finding flagged ``input:maestro_layer:sources-disagree``.
    """
    by_component: Dict[str, str] = {}
    for row in parse_markdown_table(text, "### Components"):
        name = row.get("Component", "").strip()
        if name and name not in by_component:
            by_component[name] = row.get("MAESTRO Layer", "").strip()
    by_finding = parse_finding_layers(text)
    layers: Dict[str, str] = {}
    for canonical, finding in findings.items():
        component = finding["component"] or "Unspecified"
        of_component = by_component.get(component)
        if of_component is None:
            folded = component.casefold()
            of_component = next((layer for name, layer in by_component.items() if name.casefold() == folded), "")
        layers[canonical] = by_finding.get(canonical) or of_component or "Unclassified"
    return layers


def _controls_units(stage: str, risk_scores: Any, threats: Any, baseline_flag: Optional[str], inputs: Dict[str, Dict[str, Any]],
                    refs: Dict[str, str]) -> List[Dict[str, Any]]:
    """The controls plan's units: every scored open finding of ``risk-scores.md``, in S-2 order (ADR-050 D2, D8, D9).

    The agent gets every scored finding, because it copies an UNCHANGED result from its row. A row holds the finding's
    Section 7 values (``_unit_row``) and its MAESTRO ``layer`` from the ``threats.md`` that the input's validated
    ``source_file`` names. The layer is the renderer's chain (``_finding_layers``), so the agent copies the value that the
    renderer checks its cell against. The path must pass ``check_run_file`` (a regular file called ``threats.md``, no symlink
    on the way, under the working directory), the reach that D8 gives the renderer too. A ``--threats`` that is also given
    must be that file, because one stage must read one threat model. When the file can't be reached, a row holds the finding's
    ID only. When the input is ``risk-scores.sarif``, which names no threat model, a row holds what the member's own result
    gives (``_sarif_unit_row``: D8's details, from the reader that the renderer uses too, P0-3), the layer included, and
    ``_controls_scored_input`` has already refused a member with no result of its own. In both, nothing is carried forward, with
    a warning: the agent reads the rest from ``refs.risk_scores``.

    An UNCHANGED finding's row also takes its baseline's persisted result (``CARRIED_KEYS``), decoded, from
    ``_controls_baseline``. A finding whose form has no Status gets no ``delta_status`` and no carried result: the agent
    scans it fresh, whatever the baseline holds. ``--baseline-dir`` comes first, then the ``baseline.source`` of that
    ``threats.md`` (R-6). The input, the threat model and the baseline's controls file become digest-checked ``inputs``, and
    ``refs`` gains ``risk_scores``, ``threats`` and ``baseline_dir`` where they apply, so the renderer reads what the plan
    read. Nothing here stops a run for a baseline or a threat model that can't be used (S-12(d), D7's spirit).
    """
    cwd = os.getcwd()
    scored, scored_raw, members, scored_text, sarif_rows = _controls_scored_input(stage, risk_scores)
    refs["risk_scores"] = scored
    inputs["risk_scores"] = _input_entry(stage, scored, scored_raw)

    source = _scored_source_file(scored_text) if scored_text is not None else None
    checked = rules.check_run_file(source, cwd=Path(cwd), expected_name="threats.md")
    reference: Dict[str, tuple] = {}
    layers: Dict[str, str] = {}
    threats_text: Optional[str] = None
    lacking: Dict[str, List[str]] = {}
    if checked.path is not None:
        threats_path = os.fspath(checked.path)
        problem = tp.path_problem(threats_path, allow_absolute=True)  # the working directory itself can hold a character a document can't carry
        if problem is not None:
            raise StageError(2, stage, "the threat model that source_file names resolves to a path that documents cannot carry (%s)" % problem,
                             "run from a directory whose path has no backslash, backtick or control character")
        if threats is not None and not _same_file(threats, threats_path):
            raise StageError(2, stage, "--threats %s is not the threat model that risk-scores.md names as its source (%s)" % (os.fspath(threats), source),
                             "drop --threats: this stage reaches threats.md through risk-scores.md's source_file")
        raw, pairs, threats_text, _, _, lacking = _read_member_set(stage, threats_path, threats_path)
        reference = {tp.canonical_finding_id(finding["id"]): (finding, unit) for finding, unit in pairs}
        layers = _finding_layers(threats_text, {finding_id: pair[0] for finding_id, pair in reference.items()})
        refs["threats"] = threats_path
        inputs["threats"] = _input_entry(stage, threats_path, raw)
    else:
        why = ("risk-scores.sarif names no source" if scored_text is None else "source_file names no threat model" if source is None
               else "source_file %r can't be used: %s" % (source[:80], checked.reason))
        holds = "the finding ID only" if scored_text is not None else "only what its own result in the SARIF gives"
        sys.stderr.write("WARNING: threats.md is not read (%s), so each unit holds %s and nothing is carried forward%s\n"
                         % (why, holds, "; --threats is not used by this stage" if threats is not None else ""))

    baseline_source = parse_baseline_frontmatter(threats_text)["source"] if threats_text is not None else None
    resolution = rules.resolve_baseline(flag=baseline_flag, baseline_source=baseline_source, cwd=Path(cwd))
    persisted: Dict[str, Dict[str, Any]] = {}
    if resolution.run_dir is not None:
        refs["baseline_dir"] = os.fspath(resolution.run_dir)
        persisted = _controls_baseline(stage, resolution, inputs)
    elif resolution.reason != "not-named":
        sys.stderr.write("WARNING: no baseline is used (%s: %s), so every finding is scanned fresh\n" % (resolution.origin, resolution.reason))

    units: List[Dict[str, Any]] = []
    for finding_id in members:
        found = reference.get(finding_id)
        unit = dict(found[1]) if found is not None else sarif_rows.get(finding_id, {"finding_id": finding_id})  # a SARIF member's own row, else the ID
        if found is not None:
            unit["layer"] = layers[finding_id]
            if found[0].get("delta_status") == "UNCHANGED" and finding_id in persisted:
                unit.update({key: persisted[finding_id][key] for key in CARRIED_KEYS})
        units.append(unit)

    if threats_text is not None:
        scored_ids = set(members)
        strangers = [finding_id for finding_id in members if finding_id not in reference]
        unscored = [finding_id for finding_id in reference if finding_id not in scored_ids]
        no_status = [finding_id for finding_id in members if "delta_status" in lacking.get(finding_id, ())]
        if strangers:
            sys.stderr.write("WARNING: %d scored finding(s) are not open findings of %s (%s), so their rows hold the ID only\n"
                             % (len(strangers), refs["threats"], _id_list(strangers)))
        if unscored:
            sys.stderr.write("WARNING: %d open finding(s) of %s are not in %s and are not planned (%s)\n"
                             % (len(unscored), refs["threats"], refs["risk_scores"], _id_list(unscored)))
        if no_status:
            sys.stderr.write("WARNING: Section 7 of %s has no Status for %d scored finding(s) (%s), so each is scanned fresh and none is "
                             "carried forward\n" % (refs["threats"], len(no_status), _id_list(no_status)))
    return units


def _write_plan(stage: str, out: str, inputs: Dict[str, Dict[str, Any]], refs: Dict[str, str], architecture_warning: Optional[Dict[str, str]],
                params: Dict[str, Any], batch_size: Optional[int], batches: List[tuple], snapshot: bool) -> Dict[str, Any]:
    """Write a plan, one batch input for each batch and the pre-image copies, then replace the current-plan pointer, and return what ``plan`` prints.

    ``batches`` is ``[(finding IDs, unit rows)]`` in plan order, and the units of a batch are its unit rows, as verbatim data. ``batch_size`` is the plan's
    ``batch_size`` (``None`` for a plan with no unit and for a stage whose sizes are per section). ``snapshot`` says whether the plan snapshots ``{out}``:
    PR 1's two stages and the run-level plan do, and the batch stages don't (``close`` checks the run, RR3). Nothing is written until here, so a plan that
    ends earlier leaves no pointer, and the pointer comes last, so a failed write never makes a half plan the current one.
    """
    if len(batches) > MAX_BATCHES:
        raise StageError(2, stage, "the plan needs %d batches, and a batch ID allows %d" % (len(batches), MAX_BATCHES), "reduce the input, or report this as a bug")
    plan_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + os.urandom(6).hex()
    _prepare_directories(stage, out, plan_id)
    taken = _snapshot(out) if snapshot else None  # before this plan writes a file of its own, so its files are new
    preimage = _take_preimages(stage, out, plan_id)

    plan: Dict[str, Any] = {
        "schema": tp.PLAN_SCHEMA, "plan_id": plan_id, "stage": stage, "agent_type": tp.STAGE_AGENTS[stage],
        "created_utc": _utc_now(), "tachi_version": tp.VERSION,
        "inputs": inputs, "refs": refs, "architecture_warning": architecture_warning,
        "params": params, "batch_size": batch_size, "unit_count": sum(len(units) for _, units in batches), "preimage": preimage,
        "out_snapshot": taken, "retry_budget": {"limit": 2 * len(batches), "used": 0}, "batches": [],
    }
    for number, (finding_ids, units) in enumerate(batches, 1):
        entry = {"batch_id": "B%03d" % number, "parent": None, "attempt": 1, "finding_ids": list(finding_ids), "input_sha256": "0" * 64, "state": "pending"}
        _write_batch_input(stage, out, plan, entry, units)
        plan["batches"].append(entry)
    text = _write_document(stage, tp.plan_path(out, stage, plan_id), plan, tp.PLAN_SCHEMA, tp.validate_plan)
    _write_document(stage, tp.pointer_path(out, stage), {"schema": tp.POINTER_SCHEMA, "plan_id": plan_id}, tp.POINTER_SCHEMA, tp.validate_pointer)
    units_of = {entry["batch_id"]: units for entry, (_, units) in zip(plan["batches"], batches)}
    return {"plan_id": plan_id, "plan_digest": tp.sha256_hex(text.encode("utf-8")), "waves": _waves(out, stage, plan_id, plan["batches"], units_of)}


def _refuse_other_pointers(stage: str, given: Dict[str, Any]) -> None:
    """S1P-A63: a plan takes only its own pointers, so a pointer flag that the stage doesn't take is exit 2 with nothing written (a stale pointer in a
    command line is refused, never ignored). PR 1's two stages keep every pointer they had, and refuse PR 2's two."""
    for name, value in given.items():
        if value is not None and name not in PLAN_POINTERS[stage]:
            raise StageError(2, stage, "--%s is not a pointer of the %s stage" % (name.replace("_", "-"), stage),
                             "pass only %s" % (", ".join("--" + pointer.replace("_", "-") for pointer in PLAN_POINTERS[stage]) or "--out and --date"))


def plan_stage(stage: str, out: Any, date: str, threats: Any = None, risk_scores: Any = None, baseline_dir: Any = None,
               architecture: Any = None, target: Any = None, batch_size: Optional[int] = None, trees_plan: Any = None,
               trees_plan_digest: Any = None) -> Dict[str, Any]:
    """Plan one stage and return ``{plan_id, plan_digest, waves}``, the object ``plan`` prints.

    Reads the reference finding set from ``threats`` through the shared wrapper, so an unreadable Section 7 ends the
    run here, before anything is written or dispatched (S-12(c)). For the scorer it keeps only the findings that need
    judgment (D2: ``_scorer_routing``), and reads ``threats.sarif`` instead when ``threats.md`` is absent (D8). The
    controls stage plans from ``risk_scores`` and ``target`` instead (``_controls_units``): every scored open finding,
    each UNCHANGED one with its baseline's persisted result, and ``threats`` is optional there, because the
    ``threats.md`` comes from the input's ``source_file``. Splits those units, in S-2 order, into balanced contiguous
    batches of at most ``batch_size`` (the stage's constant when ``None``), writes the plan, one batch input for each
    batch and the pre-image copies, and only then replaces the current-plan pointer. A plan with no units (every
    finding carried or copied) has no batches and a null ``batch_size``, and reconciles as complete. A value that a batch
    input would carry, and that D3's step 10 forbids, ends the plan before anything is written (exit 2,
    ``_refuse_forbidden_units``; P0-4, SA-1).

    The plan holds the stage's pointers as ``refs``, built once after the routing (which adds ``baseline_dir``), and each
    batch input copies them for its agent, so a plan with no units keeps them for the renderer's URI. It also holds
    ``architecture_warning``: the warning the shared resolver raised when it refused the ``--architecture`` candidate, or
    ``None`` (``_architecture_ref``; ruled at W2).

    PR 2's four stages are planned by ``_plan_pr2`` (the run-level plan, ``threats-md``, ``trees`` and ``report``), each from its own pointers alone
    (``_refuse_other_pointers``, S1P-A63). ``batch_size``, in the function interface only, sets the size of every part of a stage whose sizes are per
    section (``threats-md``, ``report``'s findings parts) as it sets ``trees``'s.
    """
    if stage not in tp.STAGE_AGENTS:
        raise StageError(2, stage, "%r is not a stage this version plans" % (stage,),
                         "use risk-score, compensating-controls, threat-model, threats-md, trees or report")
    if not isinstance(date, str) or _DATE.fullmatch(date) is None:
        raise StageError(2, stage, "--date is not YYYY-MM-DD", "pass the scoring date as YYYY-MM-DD")
    try:
        datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
    except ValueError:
        raise StageError(2, stage, "--date is not a calendar date", "pass the scoring date as YYYY-MM-DD") from None
    _refuse_other_pointers(stage, {"threats": threats, "risk_scores": risk_scores, "baseline_dir": baseline_dir, "architecture": architecture,
                                   "target": target, "trees_plan": trees_plan, "trees_plan_digest": trees_plan_digest})
    if stage == CONTROLS:  # the agent scans a codebase, and the renderer resolves each evidence file under it (D7)
        if risk_scores is None:
            raise StageError(2, stage, "--risk-scores is required for the %s stage" % stage, "pass the risk-scores.md to plan from")
        if target is None:
            raise StageError(2, stage, "--target is required for the %s stage" % stage, "pass the codebase directory to scan")
    elif stage not in (THREAT_MODEL, THREATS_MD):  # the scorer, the trees and the report read a threats.md
        if threats is None:
            raise StageError(2, stage, "--threats is required for the %s stage" % stage, "pass the threats.md to plan from")
        if stage == REPORT and (trees_plan is None or trees_plan_digest is None):
            raise StageError(2, stage, "--trees-plan and --trees-plan-digest are required for the report stage",
                             "pass the trees plan's ID and the digest that its last reconcile printed")
    size = BATCH_SIZES.get(stage) if batch_size is None else batch_size
    if size is not None and (type(size) is not int or not 1 <= size <= tp.MAX_IDS):
        raise StageError(2, stage, "the batch size must be an integer from 1 to %d" % tp.MAX_IDS)
    out = _out_dir(stage, out)
    if stage in PR2_STAGES:
        return _plan_pr2(stage, out, date, batch_size, threats, baseline_dir, trees_plan, trees_plan_digest)

    if stage == CONTROLS:
        # refs.architecture is the --architecture flag alone, on both stages: with no flag the agents read the run's snapshot and the renderer resolves D7's chain (ADR-050 D7, ruled at W3)
        plan_inputs, refs, baseline_flag, architecture_warning = _pointer_refs(stage, None, baseline_dir, architecture, target)
        units = _controls_units(stage, risk_scores, threats, baseline_flag, plan_inputs, refs)
    else:
        threats_path = _threats_argument(stage, threats)
        raw, members, text, threats_path, sarif_groups, lacking = _read_member_set(stage, threats, threats_path)
        extra_inputs, refs, baseline_flag, architecture_warning = _pointer_refs(stage, risk_scores, baseline_dir, architecture, target)
        refs = dict(refs, threats=threats_path)
        if stage == "risk-score":  # D2: only the findings that need judgment go to the agent
            to_agent = set(_scorer_routing(stage, members, text, sarif_groups, lacking, baseline_flag, extra_inputs, refs).to_agent)
            members = [pair for pair in members if tp.canonical_finding_id(pair[0]["id"]) in to_agent]
        units = [unit for _, unit in members]
        plan_inputs = dict(extra_inputs, threats=_input_entry(stage, threats_path, raw))

    _refuse_forbidden_units(stage, units, refs.get("threats") or refs["risk_scores"])  # before anything is written (P0-4, SA-1)
    count = len(units)
    planned = -(-count // size)
    if planned > MAX_BATCHES:
        raise StageError(2, stage, "%d findings at %d a batch need %d batches, and a batch ID allows %d" % (count, size, planned, MAX_BATCHES),
                         "reduce the findings, or report this as a bug")
    batches = [([row["finding_id"] for row in units[start:stop]], units[start:stop]) for start, stop in _runs(count, size)]
    return _write_plan(stage, out, plan_inputs, refs, architecture_warning, {"scoring_date": date}, size if count else None, batches, snapshot=True)


# =============================================================================
# PR 2's plans: the run-level plan, threats-md, trees and report (ADR-050 D4, D6 items O-beta and O-gamma, D14; contracts/cli.md, part-files.md)
# =============================================================================

# A finding's category table by the prefix of its ID: item O-beta's category keys (``spoofing`` to ``elevation_of_privilege``, ``agentic``, ``llm``), read off
# the 24-table constant, so the planners and the joiner share one mapping.
_CATEGORY_OF = {prefix: section.key for section in tp.THREATS_MD_SECTIONS if section.keyed == "prefixes" for prefix in section.prefixes}
# A tree file's name, as the planner and the assembler build it: the finding ID in lower case, as an ASCII full match, then ``-attack-tree.md``.
_TREE_NAME = re.compile("(%s)-attack-tree\\.md" % tp.ID_PATTERNS["finding"].lower(), re.ASCII)
_HEX64 = re.compile(r"[0-9a-f]{64}", re.ASCII)


def _threats_argument(stage: str, threats: Any) -> str:
    """``--threats`` as an absolute path that a document can carry, or exit 2 (the path is the operator's, and may be a link)."""
    path = os.path.abspath(os.fspath(threats))
    problem = tp.path_problem(path, allow_absolute=True)
    if problem is not None:
        raise StageError(2, stage, "--threats is not an acceptable path (%s)" % problem, "use a path with no backslash, backtick or control character")
    return path


def _plan_pr2(stage: str, out: str, date: str, batch_size: Optional[int], threats: Any, baseline_dir: Any, trees_plan: Any, trees_plan_digest: Any) -> Dict[str, Any]:
    """Plan one of PR 2's four stages, once ``plan_stage`` has checked the date, the pointer flags and ``--out``.

    ``threat-model`` is the run-level plan of Step 1.5 (D4): it plans no unit and reads no file, and it exists so that ``fail`` and ``close`` have a plan. It
    copies the pre-images of the run's four canonical files and takes the ``{out}`` snapshot that ``close``'s declared-paths check compares with.
    """
    params = {"scoring_date": date}
    if stage == THREAT_MODEL:
        return _write_plan(stage, out, {}, {}, None, params, None, [], snapshot=True)
    if stage == THREATS_MD:
        return _plan_threats_md(stage, out, params, batch_size)
    if stage == TREES:
        return _plan_trees(stage, out, params, BATCH_SIZES[TREES] if batch_size is None else batch_size, threats, baseline_dir)
    return _plan_report(stage, out, params, batch_size, threats, trees_plan, trees_plan_digest)


def _plan_threats_md(stage: str, out: str, params: Dict[str, Any], size: Optional[int]) -> Dict[str, Any]:
    """``plan --stage threats-md`` (item O-beta): the parts that the orchestrator writes itself, one table of ``threats.md`` each, from the section manifest.

    The manifest at its fixed path is the planner's only source (the compiled findings live only in the orchestrator's context, C-7), strict-loaded and
    checked by ``tachi_parts.validate_sections``, so a rule that it breaks is exit 2 and nothing is written, and a manifest that isn't there is exit 1. Its
    digest is the plan's input ``sections``, which the joiner checks again. Each of the template's 24 tables that has a unit is cut into parts of its own size
    (``THREATS_MD_SECTIONS``), contiguous and balanced: a table keyed by row has the manifest's row count, and a table keyed by finding has the open IDs of its
    prefixes (Section 7: every open ID; Section 4c: the resolved ones). A row unit is ``{section, row}`` with the table's 1-based row number, a finding unit
    ``{section, finding_id}`` in S-2 order, and a row part's batch names no finding.
    """
    path = os.path.join(out, tp.BUILD_DIR, "sections.json")
    manifest = _read_document(stage, path, out, tp.SECTIONS_SCHEMA, "the section manifest")
    opened = sorted((tp.canonical_finding_id(found) for found in manifest["open"]), key=tp.finding_sort_key)
    resolved = sorted((tp.canonical_finding_id(found) for found in manifest["resolved"] or []), key=tp.finding_sort_key)
    batches: List[tuple] = []
    for section in tp.THREATS_MD_SECTIONS:
        if section.keyed == "row":
            ids: List[str] = []
            units = [{"section": section.key, "row": number} for number in range(1, manifest["rows"][section.key] + 1)]
        else:
            ids = (opened if section.keyed == "open" else resolved if section.keyed == "resolved"
                   else [found for found in opened if found.partition("-")[0] in section.prefixes])
            units = [{"section": section.key, "finding_id": found} for found in ids]
        for start, stop in _runs(len(units), size or section.size):
            batches.append((ids[start:stop], units[start:stop]))
    return _write_plan(stage, out, {"sections": _input_entry(stage, path)}, {}, None, params, None, batches, snapshot=False)


def _band(finding: Dict[str, Any]) -> str:
    """A finding's risk level as a lower-case band (``critical`` to ``note``), however Section 7 spells its case."""
    return str(finding.get("risk_level", "")).strip().lower()


def _baseline_trees(run_dir: str) -> Optional[set]:
    """The canonical IDs whose tree file a baseline run directory holds under ``attack-trees/``, or ``None`` when it holds none.

    ``None`` is the first row of the tree agent's own Step 1 table: no baseline for trees (D14). A file counts when its name is the one that ``_tree_path``
    builds for a finding (the canonical ID in lower case, then ``-attack-tree.md``, so the name that ``assemble-report.py trees`` looks for), and it is a
    regular file with no link on the way down from the working directory, as R-6 holds every baseline file (``path_guard_problem``).
    """
    base = os.getcwd()
    directory = os.path.join(run_dir, "attack-trees")
    try:
        with os.scandir(directory) as listing:
            names = [entry.name for entry in listing]
    except OSError:
        return None
    held = set()
    for name in names:
        found = _TREE_NAME.fullmatch(name)
        if found is None:
            continue
        canonical = tp.canonical_finding_id(found.group(1).upper())
        if name == "%s-attack-tree.md" % canonical.lower() and tp.path_guard_problem(os.path.join(directory, name), base) is None:
            held.add(canonical)
    return held or None


def _plan_trees(stage: str, out: str, params: Dict[str, Any], size: int, threats: Any, baseline_dir: Any) -> Dict[str, Any]:
    """``plan --stage trees`` (D6's table, D14): a unit for each open Critical or High finding whose tree an agent generates, from the joined ``threats.md``'s
    reference set and the baseline's ``attack-trees/`` listing.

    The planner, not the agent, applies today's Step 1 table (``attack-tree-delta.md``), by R-6's reading of the baseline (``--baseline-dir``, else
    ``baseline.source``, resolved below the working directory as the scorer's routing resolves it):

    * ``no-op``: no Critical or High finding, so no unit;
    * ``no-baseline``: no baseline, or one with no tree (no ``attack-trees/`` directory, or no tree file in it): every tree is generated;
    * ``Rule 1``: a baseline, and no NEW or UPDATED finding and no RESOLVED one in the run: a tree that the baseline holds is carried (``assemble-report.py
      trees`` copies it), and only a missing one is generated;
    * ``Rule 2``: a baseline and any change: every tree is generated, and an UNCHANGED finding whose baseline holds a tree is a Rule 3 unit, planned
      ``regenerated`` (S1P-A43, RD-6). The agent writes its fresh tree and decides, by Rule 3's three tests, whether the baseline's stands.

    A unit is the finding's Section 7 row (``_unit_row``) with its ``delta_status`` (NEW when the row has none, as the scorer's routing reads it) and its
    planned ``action``. The plan records ``params.rule_applied`` and ``params.reference_digest`` (the reference set's, so Step 2.9 can follow a file that
    Steps 2.5 to 2.8 change by design), and ``refs.baseline_dir`` for Rule 1 and Rule 2, whose carried and Rule 3 trees come from it.
    """
    threats_path = _threats_argument(stage, threats)
    raw, text, reference = _read_reference(stage, threats, threats_path)
    flag = _pointer_refs(stage, None, baseline_dir, None, None)[2]  # the flag's own checks: a path that a document can carry, and one that exists
    resolution = rules.resolve_baseline(flag=flag, baseline_source=parse_baseline_frontmatter(text)["source"], cwd=Path(os.getcwd()))
    if resolution.run_dir is None and resolution.reason != "not-named":
        sys.stderr.write("WARNING: no baseline is used (%s: %s), so every tree is generated\n" % (resolution.origin, resolution.reason))
    drawn = [finding for finding in reference["open"] if _band(finding) in ("critical", "high")]
    held = _baseline_trees(os.fspath(resolution.run_dir)) if resolution.run_dir is not None else None
    statuses = {tp.canonical_finding_id(found["id"]): found.get("delta_status") if found.get("delta_status") in tp.DELTA_STATUSES else "NEW"
                for found in reference["open"]}
    if not drawn:
        rule = "no-op"
    elif held is None:
        rule = "no-baseline"
    else:
        changed = bool(reference["resolved"]) or any(status in ("NEW", "UPDATED") for status in statuses.values())
        rule = "Rule 2" if changed else "Rule 1"
    units: List[Dict[str, Any]] = []
    for finding in drawn:
        unit = _unit_row(finding)
        unit["delta_status"] = statuses[unit["finding_id"]]
        has_tree = held is not None and unit["finding_id"] in held
        if rule == "Rule 1" and has_tree:
            continue  # carried: nothing to generate
        unit["action"] = "regenerated" if rule == "Rule 2" and has_tree and unit["delta_status"] == "UNCHANGED" else "generated_fresh"
        units.append(unit)
    _refuse_forbidden_units(stage, units, threats_path)  # before anything is written (P0-4)
    refs = {"baseline_dir": os.fspath(resolution.run_dir)} if rule in ("Rule 1", "Rule 2") else {}
    batches = [([unit["finding_id"] for unit in units[start:stop]], units[start:stop]) for start, stop in _runs(len(units), size)]
    return _write_plan(stage, out, {"threats": _input_entry(stage, threats_path, raw)}, refs, None,
                       dict(params, rule_applied=rule, reference_digest=tp.reference_digest(reference)), size if units else None, batches, snapshot=False)


def _trusted_trees_plan(stage: str, out: str, trees_plan: Any, trees_plan_digest: Any) -> Dict[str, Any]:
    """The trees plan that a report plan pins, once its pointer, digest, inputs and batch inputs check out and every batch is done (D3, RR3).

    The two arguments pass their allow-lists first, as ASCII full matches. A refusal is the report stage's own, in D4's form, with the guard's exit code
    (2, or 1 for a file that is missing), its reason with the trees plan named, and that plan's directory in ``Kept for diagnosis``.
    """
    if not tp.id_matches("plan", trees_plan):
        raise StageError(2, stage, "--trees-plan is not a plan ID", "pass the plan ID that plan --stage trees printed")
    if not isinstance(trees_plan_digest, str) or _HEX64.fullmatch(trees_plan_digest) is None:
        raise StageError(2, stage, "--trees-plan-digest is not a SHA-256 in lowercase hex", "pass the digest that the trees plan's last reconcile printed")
    try:
        return tp.trusted_plan(TREES, out, trees_plan, trees_plan_digest, complete=True, kept=True)[0]
    except StageError as exc:
        raise StageError(exc.code, stage, "the trees plan %s can't be used: %s" % (trees_plan, exc.reason), exc.remedy, batch=exc.batch, kept=exc.kept) from None


def _table_rows(text: str, key: str) -> List[Dict[str, str]]:
    """The rows of one table of ``threats.md``, decoded, under that table's item keys (``tachi_parts.THREATS_MD_SECTIONS``): ``[]`` when it has none.

    The table is found by its own heading, as every reader finds one, and a cell that holds none of the template's header words reads as empty.
    """
    section = tp.THREATS_MD_BY_KEY[key]
    return [{item: row.get(header, "").strip() for header, item in zip(section.header, section.keys)} for row in parse_markdown_table(text, section.headings[-1])]


def _category_rows(text: str) -> Dict[str, Dict[str, str]]:
    """Each finding's row of its category table (Sections 3 and 4), by canonical ID, decoded and without its ID: the first row of an ID wins."""
    found: Dict[str, Dict[str, str]] = {}
    for section in tp.THREATS_MD_SECTIONS:
        if section.keyed != "prefixes":
            continue
        for row in _table_rows(text, section.key):
            if tp.id_matches("finding", row["finding_id"]):
                found.setdefault(tp.canonical_finding_id(row["finding_id"]), {key: value for key, value in row.items() if key != "finding_id"})
    return found


def _surfaced_chains(stage: str, out: str, text: str) -> Optional[tuple]:
    """``(the surfaced chains, attack-chains.md's bytes)`` for a run whose outcome record says ``chains written``, and ``None`` for any other form (R9).

    The record is read through ``tachi_parsers.parse_chain_outcome`` and the file through ``parse_attack_chains``, the shipped reader, which returns each
    chain of the Chain Details sections with its ``surfaced`` flag; the Chain Summary table is not read a second time. When the file is missing or
    unreadable, or holds no surfaced chain, there is nothing to plan: stderr says so, the plan has no ``attack_chains`` part and exits 0, and Step 2.8's check
    rewrites the record (D13), so the run goes on (R-24). A chain listed twice counts once, and a file with more surfaced chains than a part holds counts
    as one with none (the record allows 5).
    """
    if tpar.parse_chain_outcome(text)["form"] != "written":
        return None
    why = ""
    try:
        raw, chains_text = _read_threats(stage, os.path.join(out, "attack-chains.md"), "re-run the chain script", regular=True)
    except StageError as exc:
        why = exc.reason
    else:
        chains = []
        for chain in parse_attack_chains(chains_text):
            if chain["surfaced"] and tp.id_matches("chain", chain["chain_id"]) and all(chain["chain_id"] != held["chain_id"] for held in chains):
                chains.append(chain)
        if 1 <= len(chains) <= tp.MAX_FRAGMENTS:
            return chains, raw
        why = "it holds no surfaced chain" if not chains else "it holds more surfaced chains than a part can take"
    sys.stderr.write("WARNING: the outcome record says chains were written, but attack-chains.md can't be used (%s), so the report plan has no "
                     "attack_chains part\n" % why)
    return None


def _report_parts(text: str, reference: Dict[str, Any], chains: Optional[List[Dict[str, Any]]], size: Optional[int]) -> List[tuple]:
    """``[(finding IDs, units)]``: the batches of the report plan, in the template's order (``tachi_parts.REPORT_PARTS``; item O-gamma).

    A section part is one batch, with one unit ``{section, key, ...}`` for each fragment key that it plans and no finding. A findings part is cut into
    balanced batches (``REPORT_SIZES``), with one unit ``{section, finding_id, ...}`` for each finding, in S-2 order. What a unit holds besides its key is
    the data that its key is about, as verbatim rows (the reference set's ``_unit_row``, and the cells of Sections 1, 2, 4a and 4c as their tables
    give them), so that no report agent reads ``threats.md``:

    * ``exec_summary``: the counts of the run for each key, and the open Critical and High findings' rows for ``top_threats`` and ``key_recommendations``;
    * ``architecture_overview``: ``system_context`` holds Section 1's components, data flows and technologies, and ``trust_boundaries`` Section 2's zones
      and crossings;
    * ``threat_categories``: ``overview`` holds each category's narrated and summarized IDs, ``category.<key>`` those IDs and its narrated findings' rows,
      and ``summary.<key>`` its summarized findings' rows (a finding is summarized when the run has more than 30 open and it is Medium, Low or Note);
    * ``cross_cutting_themes``: ``themes`` holds the counts, the Critical and High rows and Section 4a's groups;
    * ``attack_chains``: ``chain.<ID>`` holds the chain's title, layers, severity, members and narrative;
    * ``agentic_patterns``: ``pattern.<value>`` and ``multi`` hold the rows of the findings with that pattern;
    * ``delta_summary``: ``progress`` holds the counts, the lifecycle counts, Section 4c's rows and the baseline's frontmatter.

    A findings unit is the finding's Section 7 row with its category-table row (``category_row``: the cells of its row in Section 3 or 4, under
    ``tachi_parts``' item keys, so ``likelihood``, ``impact``, ``maestro_layer`` and the rest). ``threat_analysis`` adds ``tree``, whether the finding is
    Critical or High, and ``remediation_roadmap`` adds, for a correlation group's primary, ``group_id`` and ``members``, the Section 7 rows of the group.
    """
    findings = reference["open"]
    ids = [tp.canonical_finding_id(found["id"]) for found in findings]
    rows = {tp.canonical_finding_id(found["id"]): _unit_row(found) for found in findings}
    band = {tp.canonical_finding_id(found["id"]): _band(found) for found in findings}
    category_rows = _category_rows(text)
    summarized = {found for found in ids if len(ids) > LARGE_RUN and band[found] in ("medium", "low", "note")}
    narrated = [found for found in ids if found not in summarized]
    drawn = [found for found in ids if band[found] in ("critical", "high")]
    statuses = {name: sum(1 for found in findings if found.get("delta_status") == name.upper()) for name in ("new", "unchanged", "updated")}
    counts: Dict[str, int] = dict({"open": len(ids), "resolved": len(reference["resolved"])}, **statuses)
    counts.update({name: sum(1 for found in ids if band[found] == name) for name in tp.REPORT_BANDS})
    by_category: Dict[str, tuple] = {}
    for found in ids:
        by_category.setdefault(_CATEGORY_OF[found.partition("-")[0]], ([], []))[1 if found in summarized else 0].append(found)
    baseline = parse_baseline_frontmatter(text)

    def unit(section: str, key: str, **data: Any) -> Dict[str, Any]:
        return dict({"section": section, "key": key}, **data)

    def of(found_ids: List[str]) -> List[Dict[str, Any]]:
        return [rows[found] for found in found_ids]

    def exec_summary() -> List[Dict[str, Any]]:
        return [unit("exec_summary", key, counts=counts, **({"rows": of(drawn)} if key in ("top_threats", "key_recommendations") else {}))
                for key in ("risk_posture", "top_threats", "key_recommendations", "compliance")]

    def architecture_overview() -> List[Dict[str, Any]]:
        return [unit("architecture_overview", "system_context", components=_table_rows(text, "components"), data_flows=_table_rows(text, "data_flows"),
                     technologies=_table_rows(text, "technologies")),
                unit("architecture_overview", "trust_boundaries", trust_zones=_table_rows(text, "trust_zones"),
                     boundary_crossings=_table_rows(text, "boundary_crossings"))]

    def threat_categories() -> List[Dict[str, Any]]:
        present = [name for name in tp.REPORT_CATEGORY_KEYS if name in by_category]
        return ([unit("threat_categories", "overview", counts=counts,
                      categories={name: {"narrated": by_category[name][0], "summarized": by_category[name][1]} for name in present})]
                + [unit("threat_categories", "category." + name, category=name, narrated=by_category[name][0], summarized=by_category[name][1],
                        rows=of(by_category[name][0])) for name in present]
                + [unit("threat_categories", "summary." + name, category=name, rows=of(by_category[name][1])) for name in present if by_category[name][1]])

    def findings_unit(section: str, found: str, **data: Any) -> Dict[str, Any]:
        return dict(rows[found], section=section, category_row=category_rows.get(found, {}), **data)

    def threat_analysis() -> List[Dict[str, Any]]:
        return [findings_unit("threat_analysis", found, tree=band[found] in ("critical", "high")) for found in narrated]

    def cross_cutting_themes() -> List[Dict[str, Any]]:
        return [unit("cross_cutting_themes", "themes", counts=counts, rows=of(drawn), groups=_table_rows(text, "correlated"))]

    def attack_chains() -> Optional[List[Dict[str, Any]]]:
        return None if chains is None else [
            unit("attack_chains", "chain." + chain["chain_id"], chain_id=chain["chain_id"], title=chain["title"], layers=chain["layers"],
                 max_severity=chain["max_severity"], findings=chain["findings"], narrative=chain["narrative"]) for chain in chains]

    def agentic_patterns() -> Optional[List[Dict[str, Any]]]:
        by_pattern: Dict[str, List[str]] = {}
        for found in ids:
            by_pattern.setdefault(rows[found].get("agentic_pattern", "none"), []).append(found)
        units = [unit("agentic_patterns", "pattern." + name, pattern=name, rows=of(by_pattern[name])) for name in tp.REPORT_PATTERNS if name in by_pattern]
        if "multiple" in by_pattern:
            units.append(unit("agentic_patterns", "multi", pattern="multiple", rows=of(by_pattern["multiple"])))
        return units or None

    def remediation_roadmap() -> List[Dict[str, Any]]:
        groups = parse_correlation_groups(text, member_ids=ids)["groups"]
        peers = {member for group in groups for member in group["members"][1:]}
        primaries = {group["members"][0]: group for group in groups}
        units = []
        for found in ids:
            if found in peers:
                continue
            extra = {"group_id": primaries[found]["group_id"], "members": of(primaries[found]["members"])} if found in primaries else {}
            units.append(findings_unit("remediation_roadmap", found, **extra))
        return units

    def delta_summary() -> Optional[List[Dict[str, Any]]]:
        if not baseline["has_baseline"]:
            return None
        lifecycle = dict(statuses, resolved=len(reference["resolved"]))
        resolved = [{"finding_id": tp.canonical_finding_id(found["id"]), "component": found["component"], "threat": found["threat"],
                     "last_risk_level": found["risk_level"], "resolution_reason": found["resolution_reason"]} for found in reference["resolved"]]
        return [unit("delta_summary", "progress", counts=counts, lifecycle=lifecycle, resolved=resolved,
                     baseline={name: baseline[name] for name in ("source", "date", "finding_count", "run_id")})]

    builders = {"exec_summary": exec_summary, "architecture_overview": architecture_overview, "threat_categories": threat_categories,
                "threat_analysis": threat_analysis, "cross_cutting_themes": cross_cutting_themes, "attack_chains": attack_chains,
                "agentic_patterns": agentic_patterns, "remediation_roadmap": remediation_roadmap, "delta_summary": delta_summary}
    batches: List[tuple] = []
    for name, kind in tp.REPORT_PARTS:
        units = builders[name]()
        if not units:
            continue
        if kind == "section":
            batches.append(([], units))
            continue
        for start, stop in _runs(len(units), size or REPORT_SIZES[name]):
            batches.append(([unit_["finding_id"] for unit_ in units[start:stop]], units[start:stop]))
    return batches


def _plan_report(stage: str, out: str, params: Dict[str, Any], size: Optional[int], threats: Any, trees_plan: Any, trees_plan_digest: Any) -> Dict[str, Any]:
    """``plan --stage report`` (item O-gamma, RR3): the sections of the report, after ``assemble-report.py trees``.

    The trees plan that ``--trees-plan`` names is held to D3's checks as ``reconcile`` holds it (``_trusted_trees_plan``), before anything else is read. The
    plan then reads the joined ``threats.md``, whose reference set must be the one that the trees plan recorded (``params.reference_digest``), and pins as
    its inputs ``threats``, ``trees_plan``, the merged manifest (``tree_manifest``, exit 1 when it isn't there) and, for ``chains written``, ``attack_chains``
    (``_surfaced_chains``). Its ``params`` are ``scoring_date``, ``reference_digest`` and ``trees_plan_id``, its ``refs`` are ``{}`` (no report agent reads
    ``threats.md``), and its ``batch_size`` is null, because its sizes are per section. The batches are ``_report_parts``'.
    """
    trees = _trusted_trees_plan(stage, out, trees_plan, trees_plan_digest)
    threats_path = _threats_argument(stage, threats)
    raw, text, reference = _read_reference(stage, threats, threats_path)
    digest = tp.reference_digest(reference)
    if trees["params"]["reference_digest"] != digest:
        raise StageError(2, stage, "the findings of %s are not those that the trees plan %s was made from" % (threats_path, trees_plan),
                         "plan the trees again over this threats.md, or pass the threats.md that the trees plan read", kept=tp.plan_dir(out, TREES, trees_plan))
    inputs = {"threats": _input_entry(stage, threats_path, raw), "trees_plan": _input_entry(stage, tp.plan_path(out, TREES, trees_plan)),
              "tree_manifest": _input_entry(stage, os.path.join(out, "attack-trees", ".manifest.json"))}
    found = _surfaced_chains(stage, out, text)
    if found is not None:
        inputs["attack_chains"] = _input_entry(stage, os.path.join(out, "attack-chains.md"), found[1])
    batches = _report_parts(text, reference, None if found is None else found[0], size)
    _refuse_forbidden_units(stage, [unit for _, units in batches for unit in units], threats_path)  # before anything is written (P0-4)
    return _write_plan(stage, out, inputs, {}, None, dict(params, reference_digest=digest, trees_plan_id=trees_plan), None, batches, snapshot=False)


# =============================================================================
# reconcile
# =============================================================================

# ``tachi_parts.read_document`` with D4's exit codes: 1 for a missing file, 2 for anything the contract refuses. The renderers read their documents
# through it too (#443).
_read_document = tp.entry_document


def _trusted_plan(stage: str, out: str, plan_id: str, digest: str) -> Dict[str, Any]:
    """The plan ``--plan`` names, once the pointer, its digest, its inputs and every batch input check out.

    Planner state is checked, not trusted (D3): a plan file or batch input edited after ``plan``, a ``--plan`` that
    disagrees with ``current.json``, an input that changed, or a digest that differs all exit 2. The guard is
    ``tachi_parts.trusted_plan``, which the renderers share. This is the planner's use of it: a plan with a batch still
    pending or failed is fine (``reconcile`` and ``fail`` work with those), each input is digested and never read, and
    a refusal names no kept directory.
    """
    return tp.trusted_plan(stage, out, plan_id, digest)[0]


def _batch_input(stage: str, out: str, plan_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    """A batch's input, as the planner wrote it for the batch's current attempt (its digest was checked with the plan, D3)."""
    return _read_document(stage, tp.input_path(out, stage, plan_id, entry["batch_id"]), out, tp.BATCH_INPUT_SCHEMA, "the batch input %s" % entry["batch_id"])


def _tree_result(out: str, plan_id: str, entry: Dict[str, Any], batch_input: Dict[str, Any]) -> Optional[tp.PartResult]:
    """What the trees of a ``trees`` batch whose part is valid make of it (R11; part-files.md, "The tree files"): ``None`` when each passes its checks,
    ``missing`` when one isn't there (so the batch is halved) and otherwise ``invalid`` (so it is retried as it is). A tree that is missing outranks one that
    fails, because halving puts each unit in a batch of its own.

    A tree's path is built from ``--out``, the plan ID and the finding's ID (``_tree_path``), and the batch input's own entry must equal it. The path passes
    D3's guard under ``--out``, the bytes are read through ``read_capped`` at most ``MAX_PART_BYTES``, and ``tachi_parsers.attack_tree_source`` makes the
    content checks that ``assemble-report.py trees`` makes again on every tree it copies (strict UTF-8, no forbidden character, one Mermaid block). A detail
    names the finding and the check, and never quotes the file.
    """
    missing = invalid = None
    for finding_id in entry["finding_ids"]:
        path = _tree_path(out, plan_id, finding_id)
        if batch_input["tree_paths"].get(finding_id) != path:
            raise StageError(2, TREES, "the batch input %s names another path for the tree of %s than the plan's" % (entry["batch_id"], finding_id),
                             "re-run the command", kept=tp.plan_dir(out, TREES, plan_id))
        problem = tp.path_guard_problem(path, out)
        if problem is None:
            data, problem = tp.read_capped(path, tp.MAX_PART_BYTES)
            if data is not None:
                problem = tpar.attack_tree_source(data)[1]
        if problem == "missing":
            missing = missing or "the tree of %s is missing" % finding_id
        elif problem is not None:
            invalid = invalid or "the tree of %s fails a check (%s)" % (finding_id, problem)
    if missing is not None:
        return tp.PartResult("missing", missing)
    return None if invalid is None else tp.PartResult("invalid", invalid)


def _read_batch(stage: str, out: str, plan: Dict[str, Any], entry: Dict[str, Any]) -> tp.PartResult:
    """A batch's part for its current attempt, read as D3 reads it. A part of PR 2's three batch stages is valid only against its batch input's units, so
    the input is read too, and a ``trees`` batch whose part is valid is held to its tree files (``_tree_result``)."""
    batch_input = _batch_input(stage, out, plan["plan_id"], entry) if stage in tp.BATCH_STAGES else None
    result = tp.read_part(tp.part_path(out, stage, plan["plan_id"], entry["batch_id"], entry["attempt"]), out,
                          plan["plan_id"], entry["batch_id"], stage, plan["agent_type"], entry["finding_ids"], batch_input and batch_input["units"])
    if stage == TREES and result.state == "done":
        return _tree_result(out, plan["plan_id"], entry, batch_input) or result
    return result


def _retry(stage: str, out: str, plan: Dict[str, Any], entry: Dict[str, Any], kind: str) -> bool:
    """Retry the batch ``entry``, whose attempt came back ``kind``. False when the caps leave no retry.

    A missing, overflowed or unparseable batch of two or more units is halved into ``<id>-1`` and ``<id>-2``, each
    with the parent's attempt plus one, at a cost of 2. Any other batch (``invalid``, or one unit) is retried as it
    is, with its attempt raised and its input rewritten, at a cost of 1 (ADR-050 D6; ``contracts/part-files.md``).
    Each input is written from the plan: its ``refs`` are the plan's, never the parent input's (ruled at W2).

    The units are the batch input's, whatever they are: a finding, a row of a table, a fragment key (PR 2's stages count their units where PR 1's count
    their IDs). A halving cuts them contiguously, and the first child takes the extra unit of an odd count, as the planner cuts a batch (part-files.md,
    "The `threats-md` units"); a child names the findings of its own units.
    """
    budget = plan["retry_budget"]
    parent_input = _batch_input(stage, out, plan["plan_id"], entry)
    units = parent_input["units"]
    halve = kind in ("missing", "overflow", "unparseable") and len(units) >= 2
    cost = 2 if halve else 1
    if entry["attempt"] >= MAX_ATTEMPT or budget["used"] + cost > budget["limit"]:
        return False
    budget["used"] += cost
    if not halve:
        entry["attempt"] += 1
        entry["state"] = "pending"
        _write_batch_input(stage, out, plan, entry, units)
        return True
    middle = (len(units) + 1) // 2
    entry["state"] = "split"
    at = plan["batches"].index(entry)
    for offset, (suffix, chunk) in enumerate((("-1", units[:middle]), ("-2", units[middle:]))):
        child = {"batch_id": entry["batch_id"] + suffix, "parent": entry["batch_id"], "attempt": entry["attempt"] + 1,
                 "finding_ids": [row["finding_id"] for row in chunk if "finding_id" in row], "input_sha256": "0" * 64, "state": "pending"}
        plan["batches"].insert(at + 1 + offset, child)  # next to its parent, so the plan stays in S-2 order
        _write_batch_input(stage, out, plan, child, chunk)
    return True


def _units_label(units: List[Dict[str, Any]]) -> str:
    """What names a batch that holds no finding, for a message: a table's rows (``threats-md``) or a report section's fragment keys."""
    first = units[0] if units else {}
    if "row" in first:
        return "%s rows %d to %d" % (first.get("section", "?"), first["row"], units[-1]["row"])
    return "%s: %s" % (first.get("section", "?"), ", ".join(str(unit.get("key")) for unit in units)) if first else ""


def _batch_label(stage: str, out: str, plan_id: str, entry: Dict[str, Any]) -> str:
    """The IDs of a batch's findings for D4's ``Batch`` line, and for a batch with none (a table's rows, a report section) what its units are."""
    if entry["finding_ids"] or stage not in tp.SECTION_STAGES:
        return ", ".join(entry["finding_ids"])
    try:
        return _units_label(_batch_input(stage, out, plan_id, entry)["units"])
    except StageError:
        return ""  # the message is for a human, and a batch input that can't be read is told elsewhere


def reconcile_stage(stage: str, out: Any, plan_id: str, digest: str) -> tuple:
    """Work out from the files on disk what is done, and return ``(exit code, printed object, exhausted entries)``.

    Each batch's part is read for its current attempt only, so a part from an earlier plan or attempt never counts.
    Whatever isn't done is retried within the caps, and the plan file is replaced if anything changed. Exit 0 means
    every batch is done, 3 that batches are pending, and 4 that a cap or the retry budget ran out. A ``threats-md`` wave entry
    also says what was wrong with the attempt before (``problem``: ``missing``, or the part reader's own detail, unchanged), and a batch that was halved
    gives each child its parent's.
    """
    out = _out_dir(stage, out)
    _plan_arguments(stage, plan_id, digest)
    plan = _trusted_plan(stage, out, plan_id, digest)
    before = _dump(plan)
    exhausted = []
    problems: Dict[str, str] = {}  # what was wrong with the attempt just judged, by the ID of each batch that now waits for a retry
    for entry in list(plan["batches"]):  # a snapshot: children inserted below wait for the next reconcile
        if entry["state"] == "split":
            continue
        if entry["state"] != "failed":
            result = _read_batch(stage, out, plan, entry)
            if result.state == "done":
                entry["state"] = "done"
                continue
            if _retry(stage, out, plan, entry, result.state):
                retried = [entry["batch_id"]] if entry["state"] == "pending" else [entry["batch_id"] + "-1", entry["batch_id"] + "-2"]
                problems.update({batch_id: "missing" if result.state == "missing" else result.detail or result.state for batch_id in retried})
                continue
            entry["state"] = "failed"
        exhausted.append(entry)
    if _dump(plan) != before:
        digest = tp.sha256_hex(_write_document(stage, tp.plan_path(out, stage, plan_id), plan, tp.PLAN_SCHEMA, tp.validate_plan).encode("utf-8"))
    pending = [e for e in plan["batches"] if e["state"] == "pending"]
    printed: Dict[str, Any] = {"status": "complete", "plan_digest": digest,
                               "done": [e["batch_id"] for e in plan["batches"] if e["state"] == "done"], "waves": [], "exhausted": []}
    code = 0
    if exhausted:
        printed.update(status="exhausted", exhausted=[{"batch_id": e["batch_id"], "finding_ids": e["finding_ids"]} for e in exhausted])
        code = 4
    elif pending:
        units = {e["batch_id"]: _batch_input(stage, out, plan_id, e)["units"] for e in pending} if stage == THREATS_MD else None  # the one stage that prints them
        printed.update(status="pending", waves=_waves(out, stage, plan_id, pending, units, problems))
        code = 3
    return code, printed, exhausted


# =============================================================================
# fail and close (D4's failed outputs; KB 21's double gate)
# =============================================================================

def _detail_problem(detail: str) -> Optional[str]:
    """``--detail`` is at most 500 characters and a string field: D3's character rules apply (ruled at W1)."""
    try:
        tp.closed_string(detail, "--detail", 0, 500)
    except tp.PartError as exc:
        return exc.detail
    return None


def _current_plan(out: str, stage: str) -> Optional[str]:
    """The plan ID ``current.json`` names, or None if there is no acceptable pointer."""
    try:
        return tp.read_document(tp.pointer_path(out, stage), out, tp.POINTER_SCHEMA)["plan_id"]
    except tp.PartError:
        return None


def _undeclared_paths(out: str, stage: str, plan: Dict[str, Any]) -> tuple:
    """Paths that are new or changed since the plan and that the stage's grammar doesn't declare.

    Returns ``(paths, warnings)``. The paths are sorted and capped at ``MAX_UNDECLARED_PATHS``, and a cut adds the
    warning ``undeclared-paths-truncated`` with the full count (ruled at W1). A plan with no snapshot skips the check.
    This is ``tachi_parts.undeclared_paths``, which the renderers share, in this entry's argument order (#443).
    """
    return tp.undeclared_paths(stage, out, plan)


def _put_back(stage: str, out: str, plan_id: str, name: str, recorded: str, refusals: List[str]) -> bool:
    """Put the pre-image copy of ``name`` back onto its empty canonical name, when its digest is still the one that the plan recorded. False, with a
    refusal, when the copy is missing or has changed, or can't be written."""
    copy = tp.preimage_path(out, stage, plan_id, name)
    if _digest_or_none(copy, out) != recorded:
        refusals.append("the pre-image of %s is missing or no longer matches its recorded digest, so it was not put back" % name)
        return False
    try:
        with open(copy, "rb") as handle:
            tp.atomic_write(os.path.join(out, name), handle.read(), mode_of=copy)  # the name is empty, so the pre-image's bits are the ones to keep (P1-2)
    except OSError as exc:
        refusals.append("the pre-image of %s could not be put back (%s)" % (name, exc.strerror or "error"))
        return False
    return True


def _move_and_restore(stage: str, out: str, plan: Dict[str, Any]) -> tuple:
    """Move each changed canonical output into ``failed/`` and put its pre-image copy back (D4; KB 21's double gate).

    A file moves only if its name is in the stage's closed set, and it is a regular file directly in ``{out}``.
    Nothing is overwritten, and a pre-image goes back only if its digest matches the one the plan recorded. A
    refused file stays where it is, and the others still go. Returns ``(moved, restored, refusals)``.

    A canonical name that is empty although the plan recorded a pre-image for it counts as changed, for every stage (S1P-A55, R6): nothing moves, and the
    pre-image goes back when its copy still matches. That is D13's case, where the chain check renamed this run's ``attack-chains.md`` to
    ``attack-chains.inconsistent.md`` and the earlier run's file must come back; for PR 1's two stages it arises only when a canonical file is deleted while
    its stage runs. The name is listed in ``restored`` alone. An empty name for which the plan recorded no pre-image stays empty.
    """
    plan_id = plan["plan_id"]
    moved: List[str] = []
    restored: List[str] = []
    refusals: List[str] = []
    for name in tp.CANONICAL_OUTPUTS[stage]:  # the name gate: only the stage's own outputs are ever touched
        path = os.path.join(out, name)
        recorded = plan["preimage"].get(name)
        try:
            mode = os.lstat(path).st_mode
        except OSError:  # nothing there
            if recorded is not None and _put_back(stage, out, plan_id, name, recorded, refusals):
                restored.append(name)
            continue
        if not stat.S_ISREG(mode):  # the file gate: a link or a directory is never moved
            refusals.append("%s is not a regular file" % name)
            continue
        if tp.file_digest(path) == recorded:
            continue  # unchanged since the plan: an earlier run's output stays where it is
        destination = tp.failed_path(out, stage, plan_id, name)
        failed_directory = os.path.dirname(destination)
        if os.path.islink(failed_directory) or os.path.lexists(destination) or (
                os.path.lexists(failed_directory) and not os.path.isdir(failed_directory)):
            refusals.append("%s would overwrite or pass through something in failed/" % name)
            continue
        try:
            os.makedirs(failed_directory, exist_ok=True)
            os.replace(path, destination)
        except OSError as exc:
            refusals.append("%s could not be moved into failed/ (%s)" % (name, exc.strerror or "error"))
            continue
        moved.append(name)
        if recorded is not None and _put_back(stage, out, plan_id, name, recorded, refusals):
            restored.append(name)
    return moved, restored, refusals


# ---- the checks' hand-off files (part-files.md section 6): what ``close`` and ``fail`` fold into the run-level record, and ``close`` itself, then ``fail``

def _read_handoff(out: str, plan_id: str, check: str) -> tuple:
    """One check's hand-off file, ``<run-level plan dir>/checks/<check>.json``, through the strict loader: ``(body, None, None)``, or ``(None, kind, why)``.

    ``kind`` is the loader's: ``missing`` for a file that isn't there, and ``invalid`` or ``unparseable`` for anything else, a link included. The body is
    ``tachi_parts.validate_check_handoff``'s, which holds the closed keys, each check's own warning codes and the status that the error and the warnings give
    (R3); and its ``check`` must be its file's name and its ``plan_id`` the plan's (R4: a file of another plan doesn't load). ``why`` never quotes the file.
    """
    path = os.path.join(tp.plan_dir(out, THREAT_MODEL, plan_id), "checks", check + ".json")
    try:
        body = tp.read_document(path, out, tp.HANDOFF_SCHEMA)
    except tp.PartError as exc:
        return None, exc.kind, exc.detail
    if body["check"] != check:
        return None, "invalid", "its check is %s, not %s" % (body["check"], check)
    if body["plan_id"] != plan_id:
        return None, "invalid", "it is the hand-off of another plan"
    return body, None, None


def _cap_warnings(warnings: List[Dict[str, str]], room: int = 0) -> List[Dict[str, str]]:
    """A stage record's warnings, within §5's 1,000 (less ``room``, for a few that the caller appends later): past it, the first 999 less ``room`` stay in
    order, then ``warnings-truncated``, whose detail gives the full count (part-files.md section 6, "The record's cap")."""
    limit = 1000 - room
    if len(warnings) <= limit:
        return warnings
    return warnings[:limit - 1] + [tp.record_warning("warnings-truncated", "%d warnings in all; the first %d are listed" % (len(warnings), limit - 1))]


def _present_outputs(out: str) -> List[Dict[str, str]]:
    """The run's canonical files that are there, each a regular file in ``{out}``, in D4's order, as a record's ``outputs``: ``{path, sha256}``."""
    names = []
    for name in tp.CANONICAL_OUTPUTS[THREAT_MODEL]:
        try:
            if stat.S_ISREG(os.lstat(os.path.join(out, name)).st_mode):
                names.append(name)
        except OSError:
            continue
    try:
        return tp.output_entries(out, names)
    except OSError as exc:
        raise StageError(2, THREAT_MODEL, "cannot read an output of the run (%s)" % (exc.strerror or "error"), "check the permissions of {out} and re-run") from None


def close_stage(stage: str, out: Any, plan_id: str, digest: str) -> tuple:
    """End the run-level plan on the success path (Step 2.10; D4), and return ``(exit code, printed object)``.

    The plan is held to D3's guard (``tachi_parts.trusted_plan``), and its two hand-off files are strict-loaded. ``provenance.json`` is required, and a
    run whose check failed can't be closed, so a file that is missing, that fails to load, that another plan wrote or whose status is ``fail`` is exit 2.
    A missing ``attack-chains.json`` is only the warning ``handoff-missing:attack-chains``, because the chain check's own 2 prints and continues (R-24) and
    writes no file; one that fails to load is exit 2. ``close`` has no exit 1 (S1P-A61): a plan or a pointer that is missing is exit 2 too.

    The run's record takes its counts and Phase 2's six batch counts from ``provenance.json`` and lists the canonical files that are present, with their
    digests. Its warnings are ``attack-chains.json``'s, then ``provenance.json``'s, then ``handoff-missing:attack-chains`` and the declared-paths check's
    (``_undeclared_paths``, over the whole run, against Step 1.5's snapshot, with D4's PR 2 grammar), and past 1,000 the first 999 stay (``_cap_warnings``).
    Any warning or undeclared path makes the status ``success-with-warnings`` and the exit 5. Nothing is moved or restored, and nothing is written until
    every check has passed, so a ``close`` that exits 2 leaves no success record.

    Prints ``{record, warnings, undeclared_paths}``: the record's path, and its own two lists, so the command prints them on exit 5 without reading it (S1P-A50).
    """
    if stage != THREAT_MODEL:
        raise StageError(2, stage, "close takes the threat-model stage only", "pass --stage threat-model")
    out = _out_dir(stage, out, missing_code=2)
    _plan_arguments(stage, plan_id, digest)
    kept = tp.plan_dir(out, stage, plan_id)
    try:
        plan = tp.trusted_plan(stage, out, plan_id, digest, kept=True)[0]
    except StageError as exc:
        if exc.code != 1:
            raise
        raise StageError(2, exc.stage, exc.reason, exc.remedy, kept=exc.kept) from None
    handoffs = {}
    for check in tp.HANDOFF_CHECKS:
        body, kind, why = _read_handoff(out, plan_id, check)
        if body is None and (check == "provenance" or kind != "missing"):
            raise StageError(2, stage, "%s.json %s" % (check, "is missing, so the check never ran" if kind == "missing" else "is not acceptable (%s)" % why),
                             "run the check again, or run fail if the run can't go on", kept=kept)
        handoffs[check] = body
    provenance = handoffs["provenance"]
    if provenance["status"] == "fail":
        raise StageError(2, stage, "the provenance check failed (%s), so the run can't be closed" % provenance["error"]["code"],
                         "run fail --reason check-failed, which puts the earlier run's files back", kept=kept)
    warnings = [dict(warning) for check in tp.HANDOFF_CHECKS if handoffs[check] is not None for warning in handoffs[check]["warnings"]]
    if handoffs["attack-chains"] is None:
        warnings.append(tp.record_warning("handoff-missing:attack-chains", "the chain check wrote no hand-off file, so its events are not in this record"))
    undeclared, undeclared_warnings = _undeclared_paths(out, stage, plan)
    outputs = _present_outputs(out)
    sources = dict({"output:" + output["path"]: output["sha256"] for output in outputs},
                   **{"handoff:" + check: tp.file_digest(os.path.join(kept, "checks", check + ".json")) for check in tp.HANDOFF_CHECKS if handoffs[check] is not None})
    record = tp.stage_record(stage, out, plan, tp.input_digest({"sources": sources, "params": plan["params"], "items": [], "fragments": []}),
                             dict(provenance["counts"]), outputs, _cap_warnings(warnings + undeclared_warnings), undeclared)
    record["batches"] = dict(provenance["batches"])  # Phase 2's six counts: the plan has no batch of its own
    record_path = tp.stage_record_path(out, stage, plan_id)
    _write_document(stage, record_path, record, tp.STAGE_RECORD_SCHEMA, tp.validate_stage_record)
    return (5 if record["status"] == "success-with-warnings" else 0), {"record": record_path, "warnings": record["warnings"], "undeclared_paths": record["undeclared_paths"]}


def _accepted_parts(stage: str, out: str, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The parts of the plan's ``done`` batches that still validate, in plan order. A batch whose part or input can't be read any more is left out: this is
    for a failed record, which a stage that can't be read must still get."""
    parts = []
    for entry in plan["batches"]:
        if entry["state"] != "done":
            continue
        try:
            result = _read_batch(stage, out, plan, entry)
        except StageError:
            continue
        if result.state == "done":
            parts.append(result.part)
    return parts


def fail_stage(stage: str, out: Any, plan_id: str, digest: str, reason: str, detail: Optional[str] = None) -> tuple:
    """End a stage that can't finish, and return ``(exit code, printed object, the message to print)``.

    Writes the failed stage record first. If the plan file's digest and the pointer both check out, it then moves
    each changed canonical output into ``failed/`` and restores the earlier run's copy, so an earlier run's outputs
    survive, a check that failed on staged files changed nothing, and a half-applied pair is undone. Exit 2 means a
    guard refused a move or the plan couldn't be trusted, and the record is written either way.

    PR 2's stages differ in what they own and what their record holds (part-files.md section 5). A batch stage (``threats-md``, ``trees``, ``report``)
    owns no canonical file, so it moves and restores nothing; its record's ``counts`` are ``{units}``, its warnings only the trust warnings below, and it
    names no undeclared path (``close`` checks the run, and its plan takes no snapshot). The run-level ``threat-model`` stage owns D4's four files and
    ``fail`` runs the declared-paths check over the run, as for PR 1's stages. It also folds whichever of the two hand-off files exist and load
    (``_read_handoff``), in ``close``'s order: the record's ``counts`` and Phase 2's ``batches`` come from ``provenance.json``, and when that check failed the
    record's message, finding IDs and remedy come from its error, with ``--reason`` as the code. A file that exists but doesn't load is left out and the run
    still fails, with the warning ``handoff-invalid:<check>`` in its place; a missing file raises none, because a run can fail before Step 2.8.

    The record is for the plan this step was asked to fail: its ``plan_id`` is ``--plan``, and this step never checks that ``plan.json`` names itself.
    """
    if reason not in REASONS:
        raise StageError(2, stage, "--reason is not one of %s" % ", ".join(sorted(REASONS)))
    if detail is not None:
        problem = _detail_problem(detail)
        if problem is not None:
            raise StageError(2, stage, "--detail is not acceptable (%s)" % problem, "pass at most 500 characters of plain text")
    out = _out_dir(stage, out, missing_code=2)  # fail has no exit 1 (cli.md)
    _plan_arguments(stage, plan_id, digest)
    path = tp.plan_path(out, stage, plan_id)
    if tp.path_guard_problem(path, out) is not None:
        raise StageError(2, stage, "there is no plan %s to fail" % plan_id, "check --plan and --out")
    trusted, warnings = True, []
    if tp.file_digest(path) != digest:
        trusted = False
        warnings.append({"code": "plan-digest-mismatch", "detail": "the plan file's digest differs from --plan-digest, so nothing was moved"})
    try:
        plan = tp.read_document(path, out, tp.PLAN_SCHEMA)
    except tp.PartError as exc:
        raise StageError(2, stage, "plan.json is not acceptable (%s)" % exc.detail, "re-run the command") from None
    if _current_plan(out, stage) != plan_id:
        trusted = False
        warnings.append({"code": "pointer-mismatch", "detail": "current.json does not name this plan, so nothing was moved"})

    what, remedy = REASONS[reason]
    first = next((e for e in plan["batches"] if e["state"] == "failed"), None) if reason == "unrecoverable-batch" else None
    kept = tp.plan_dir(out, stage, plan_id)
    batch_stage = stage in tp.BATCH_STAGES
    undeclared, undeclared_warnings = ([], []) if batch_stage else _undeclared_paths(out, stage, plan)
    # D7's order puts the explicit candidate's warning first. A plan that fails its trust checks has no say in the record.
    planned_warning = [dict(plan["architecture_warning"])] if trusted and plan["architecture_warning"] is not None else []
    parts = _accepted_parts(stage, out, plan)
    if batch_stage:  # parts in plan order: a table's rows and a section's fragments name no finding to sort them by
        items, fragments = [item for part in parts for item in part["items"]], [fragment for part in parts for fragment in part["fragments"]]
    else:
        accepted = {item["finding_id"]: item for part in parts for item in part["items"]}
        items, fragments = [accepted[key] for key in sorted(accepted, key=tp.finding_sort_key)], []
    input_digest = tp.input_digest({
        "sources": {name: entry["sha256"] for name, entry in sorted(plan["inputs"].items())}, "params": plan["params"], "items": items, "fragments": fragments})
    folded: List[Dict[str, str]] = []
    provenance = None
    if stage == THREAT_MODEL:
        for check in tp.HANDOFF_CHECKS:
            body, kind, why = _read_handoff(out, plan_id, check)
            if body is not None:
                folded.extend(dict(warning) for warning in body["warnings"])
                provenance = body if check == "provenance" else provenance
            elif kind != "missing":
                folded.append(tp.record_warning("handoff-invalid:" + check, why))
    error = {"code": reason, "message": what + (": " + detail if detail else ""),
             "batch_id": first["batch_id"] if first else None, "finding_ids": list(first["finding_ids"]) if first else [], "remedy": remedy}
    if provenance is not None and provenance["error"] is not None:  # the check that failed says why, in its own words
        error.update(message=provenance["error"]["message"], finding_ids=list(provenance["error"]["finding_ids"]), remedy=provenance["error"]["remedy"])
    counts = ({"units": plan["unit_count"]} if batch_stage else dict(provenance["counts"]) if provenance is not None
              else {} if stage == THREAT_MODEL else {"units": plan["unit_count"], "open": plan["unit_count"]})
    every_warning = planned_warning + warnings + folded + undeclared_warnings
    record = tp.stage_record(stage, out, plan, input_digest, counts, [], _cap_warnings(every_warning), undeclared, status="failed", error=error)
    if provenance is not None:
        record["batches"] = dict(provenance["batches"])  # Phase 2's six counts: the run-level plan has no batch of its own
    record["plan_id"] = plan_id  # the plan this step was asked to fail: unlike ``trusted_plan``, this step never checks that plan.json names itself
    record_path = tp.stage_record_path(out, stage, plan_id)
    _write_document(stage, record_path, record, tp.STAGE_RECORD_SCHEMA, tp.validate_stage_record)  # first, before any move

    moved: List[str] = []
    restored: List[str] = []
    refusals: List[str] = []
    if trusted:
        moved, restored, refusals = _move_and_restore(stage, out, plan)
        record["outputs"] = [{"path": "%s/%s/%s/failed/%s" % (tp.BUILD_DIR, stage, plan_id, name),
                              "sha256": tp.file_digest(tp.failed_path(out, stage, plan_id, name))} for name in moved]
        if refusals:  # a refusal says why the exit is 2, so it keeps its place in a record that is full: the folded warnings give way to it
            record["warnings"] = _cap_warnings(every_warning, room=len(refusals)) + [{"code": "move-refused", "detail": refusal} for refusal in refusals]
        if moved or refusals:
            _write_document(stage, record_path, record, tp.STAGE_RECORD_SCHEMA, tp.validate_stage_record)
    code = 0 if trusted and not refusals else 2
    named_agent = reason == "agent-not-spawned"
    headline = what + (": " + detail if detail and not named_agent else "")
    problems = [w["detail"] for w in warnings] + refusals
    message = StageError(code, stage, headline + ("; " + "; ".join(problems) if problems else ""), remedy,
                         batch=(first["batch_id"], _batch_label(stage, out, plan_id, first)) if first else None,
                         agent=detail if named_agent and detail else None, kept=kept)
    return code, {"moved": moved, "restored": restored, "record": record_path}, message.text()


# =============================================================================
# architecture-source (FR-E.18; ADR-050 D7 item 6)
# =============================================================================

def _edit_architecture_line(text: str, path: Optional[str]) -> tuple:
    """``threats.md``'s text with its architecture-source lines removed and, given a ``path``, one put back.

    Returns ``(new text, what happened)``: ``added``, ``replaced``, ``removed`` or ``unchanged``. Only the lines that
    ``sarif_common``'s reader finds count (after the frontmatter, before the first ``## `` heading, outside code
    fences), so a forged copy inside a fence is neither read nor changed. A removed line takes the one blank line
    after it, so a line that an earlier run added leaves the text as it was, and a second upsert changes no byte.
    The new line goes at the region's end, followed by a blank line when a heading follows.
    """
    found = sc.find_architecture_source_lines(text)
    edited = text
    for start, end, _path in reversed(found):  # from the end, so the earlier offsets stay true
        for blank in ("\n", "\r\n"):
            if edited.startswith(blank, end):
                end += len(blank)
                break
        edited = edited[:start] + edited[end:]
    if path is not None:
        _begin, stop = sc.architecture_source_region(edited)
        joiner = "" if stop == 0 or edited[stop - 1] == "\n" else "\n"
        gap = "\n\n" if stop < len(edited) else "\n"
        edited = edited[:stop] + joiner + sc.format_architecture_source_line(path) + gap + edited[stop:]
    if edited == text:
        return edited, "unchanged"
    if path is None:
        return edited, "removed"
    return edited, "replaced" if found else "added"


def architecture_source(threats: Any, candidate: str) -> tuple:
    """Write, replace or remove the ``**Architecture source**`` line of a ``threats.md``, and return ``(code, printed)``.

    ``candidate`` is the command's own path to the architecture file. The shared resolver checks it (ADR-050 D7) and
    gives its canonical spelling, which the line carries. This never falls back to the body line or the default
    constant (ruled at W1): if the resolver refuses the path, any line already in the file is removed, so a line that
    the orchestrator wrote can't survive, a warning goes to stderr, and the exit code is 5. The run goes on.

    ``threats`` is edited in place, atomically, and only when its text changes. It must be a regular file and not a
    link, so the edit never detaches a link from its target.
    """
    stage = "threat-model"
    path = os.path.abspath(os.fspath(threats))
    try:
        mode = os.lstat(path).st_mode
    except OSError as exc:
        raise StageError(1, stage, "cannot read %s (%s)" % (path, exc.strerror or "error"), "check the path and re-run") from None
    if not stat.S_ISREG(mode):
        raise StageError(2, stage, "%s is a link or not a regular file, so it is not edited in place" % path, "pass the threats.md itself")
    _raw, text = _read_threats(stage, path)

    resolved: Optional[str] = None
    warnings: List[Dict[str, str]] = []
    try:
        resolved = sc.resolve_file(candidate, allow_absolute=True).path
        sc.format_architecture_source_line(resolved)  # a canonical spelling the line can't carry is a failure too
    except (sc.PathCheckError, ValueError) as exc:
        check = exc.check if isinstance(exc, sc.PathCheckError) else "unrepresentable"
        resolved = None
        warnings.append({"code": "architecture-path:explicit:%s" % check,
                         "detail": "the --architecture path %s failed the %s check, so no architecture-source line was written "
                                   "and any existing one was removed. Pass %s with the repo-relative path of the architecture file."
                                   % (repr(candidate)[:80], check, sc.ARCHITECTURE_FLAG)})
    edited, action = _edit_architecture_line(text, resolved)
    if edited != text:
        try:
            tp.atomic_write(path, edited)
        except OSError as exc:
            raise StageError(1, stage, "cannot write %s (%s)" % (path, exc.strerror or "error"), "check the directory's permissions and re-run") from None
    return (5 if warnings else 0), {"architecture_source": resolved, "action": action, "warnings": warnings}


# =============================================================================
# id-mark (the PM's ruling B, FR-E.19; ADR-050 D7; Step 2.7)
# =============================================================================

MARK_LABEL = "**ID high-water mark**: "
_H2 = re.compile(r" {0,3}## ")
_MARK_VALUE = re.compile(r"`([^`]*)`[ \t\r]*")


def _mark_scan(text: str) -> tuple:
    """Where the mark line lives in a ``threats.md``: ``([(start, end)], stop)``, as character offsets of the text.

    The first is each mark line, its newline included. A mark line starts, at its first character, with ``MARK_LABEL``, lies between the frontmatter (when the
    text opens with one) and the first ``## `` heading, and lies outside code fences, which are ``tachi_parsers``' one fence rule (``match_heading``'s
    ``outside_fences``): P-2's anchors, as the architecture-source line has them. A line in the region that is a fence's line, or inside a fence, is no line
    and no heading. ``stop`` is where a new line goes: the start of that heading, or the end of the text.
    """
    lines = text.split("\n")  # "\n" only: a line is what lies between two of them, so U+2028 and the rest can't forge one (NFR-10)
    first = 0
    if lines[0].rstrip("\r") == "---":
        for index in range(1, len(lines)):
            if lines[index].rstrip("\r") == "---":
                first = index + 1
                break
    starts, at = [], 0
    for line in lines:
        starts.append(at)
        at += len(line) + 1
    found: List[tuple] = []
    stop = len(text)
    for index, line in tpar._unfenced_lines(lines[first:]):
        index += first
        if _H2.match(line.rstrip("\r")):
            stop = starts[index]
            break
        if line.startswith(MARK_LABEL):
            found.append((starts[index], min(len(text), starts[index] + len(line) + 1)))
    return found, stop


def _read_mark(line: str) -> Optional[Dict[str, int]]:
    """The number of each prefix in a mark line, or ``None`` when the line doesn't hold ``MARKS`` (threat-model-records.md): one backtick-quoted run of
    allow-listed finding IDs, separated by ``, ``, no prefix twice. Each ID is read in canonical form, so ``AGP-01`` is 1 of ``AGP``."""
    found = _MARK_VALUE.fullmatch(line[len(MARK_LABEL):])
    if found is None:
        return None
    numbers: Dict[str, int] = {}
    for token in found.group(1).split(", "):
        if not tp.id_matches("finding", token):
            return None
        prefix, number = tp.canonical_finding_id(token).split("-")
        if prefix in numbers:
            return None
        numbers[prefix] = int(number)
    return numbers


def _highest(finding_ids: List[str]) -> Dict[str, int]:
    """The highest number of each prefix among some finding IDs, in canonical form: ``AGP-01`` counts as 1."""
    numbers: Dict[str, int] = {}
    for found in finding_ids:
        prefix, number = tp.canonical_finding_id(found).split("-")
        numbers[prefix] = max(numbers.get(prefix, 0), int(number))
    return numbers


def _edit_mark_line(text: str, line: str) -> tuple:
    """``threats.md``'s text with its mark lines removed and ``line`` put at the end of the region: ``(new text, added, replaced or unchanged)``.

    As ``_edit_architecture_line`` does for its line: every mark line goes, each with the one blank line after it, so a second upsert changes no byte; the
    new line is followed by a blank line when a heading follows. A copy inside a code fence is not a mark line and is left alone.
    """
    found, _ = _mark_scan(text)
    edited = text
    for start, end in reversed(found):  # from the end, so the earlier offsets stay true
        for blank in ("\n", "\r\n"):
            if edited.startswith(blank, end):
                end += len(blank)
                break
        edited = edited[:start] + edited[end:]
    _, stop = _mark_scan(edited)
    joiner = "" if stop == 0 or edited[stop - 1] == "\n" else "\n"
    edited = edited[:stop] + joiner + line + ("\n\n" if stop < len(edited) else "\n") + edited[stop:]
    return (text, "unchanged") if edited == text else (edited, "replaced" if found else "added")


def id_mark(threats: Any, baseline: Any = None) -> tuple:
    """Write ``threats.md``'s ID high-water mark line, and return ``(exit code, printed object)`` (ADR-050 D7, ruling B).

    The mark is, for each prefix in use, the larger of this run's highest ID and the baseline's mark. This run's IDs are those of its reference set, the open
    findings and Section 4c's, read in canonical form. The baseline's mark is its mark line when it has exactly one that reads (``_read_mark``); any other
    baseline, a pre-PR 2 file above all, has none, and the mark is then seeded from its highest live or Section 4c ID, which is a first PR 2 run's rule. Only
    the baseline's line is read: this run's own is replaced, never believed. A run with no baseline (``baseline=None``) has this run's highest alone. The line
    is in canonical spelling and in S-2's prefix order (``tachi_parts.FINDING_PREFIXES``), and it goes where ``_mark_scan`` puts it.

    It never writes a mark it can't compute (S1P-A54): this run's Section 7 that can't be read, and a baseline with no mark line whose own can't, are exit 2 with
    nothing written, because a lower mark is the direction that lets an ID come back. A baseline whose mark line reads is enough, whatever its Section 7 holds.
    A ``threats`` or ``baseline`` file that is missing is exit 1. ``threats`` is edited in place, atomically, only when its text changes, and only when it is a
    regular file and no link, as the architecture-source line is; the baseline is only read, and a link is refused there too.

    Prints ``{mark, action, floor}``: the line's value, ``added``, ``replaced`` or ``unchanged``, and where the baseline's side came from (``none``, ``mark``
    or ``seed``).
    """
    stage = THREAT_MODEL
    path = os.path.abspath(os.fspath(threats))
    try:
        mode = os.lstat(path).st_mode
    except OSError as exc:
        raise StageError(1, stage, "cannot read %s (%s)" % (path, exc.strerror or "error"), "check the path and re-run") from None
    if not stat.S_ISREG(mode):
        raise StageError(2, stage, "%s is a link or not a regular file, so it is not edited in place" % path, "pass the threats.md itself")
    _raw, text = _read_threats(stage, path)
    try:
        reference = parse_reference_set(text, source=os.fspath(threats))
    except ReferenceSetError as exc:
        raise StageError(2, stage, "%s. Expected %s" % (exc.reason, exc.expected), exc.remedy) from None
    floor: Dict[str, int] = {}
    where = "none"
    if baseline is not None:
        _raw, base_text = _read_threats(stage, os.path.abspath(os.fspath(baseline)), "name the baseline run's threats.md", regular=True)
        spans, _ = _mark_scan(base_text)
        mark = _read_mark(base_text[spans[0][0]:spans[0][1]].rstrip("\n")) if len(spans) == 1 else None  # none or several lines read as absent
        if mark is not None:
            floor, where = mark, "mark"
        else:
            try:
                seed = parse_reference_set(base_text, source=os.fspath(baseline))
            except ReferenceSetError as exc:
                raise StageError(2, stage, "the baseline has no ID high-water mark, and its own findings can't be read: %s. Expected %s" % (exc.reason, exc.expected),
                                 exc.remedy) from None
            floor, where = _highest([found["id"] for found in seed["open"] + seed["resolved"]]), "seed"
    here = _highest([found["id"] for found in reference["open"] + reference["resolved"]])
    result = {prefix: max(here.get(prefix, 0), floor.get(prefix, 0)) for prefix in tp.FINDING_PREFIXES if prefix in here or prefix in floor}
    value = ", ".join("%s-%d" % (prefix, result[prefix]) for prefix in tp.FINDING_PREFIXES if prefix in result)
    edited, action = _edit_mark_line(text, "%s`%s`" % (MARK_LABEL, value))
    if edited != text:
        try:
            tp.atomic_write(path, edited)
        except OSError as exc:
            raise StageError(1, stage, "cannot write %s (%s)" % (path, exc.strerror or "error"), "check the directory's permissions and re-run") from None
    return 0, {"mark": value, "action": action, "floor": where}


# =============================================================================
# watch (Phase 2's bound; ADR-050 D6, S1P-PM9; contracts/threat-model-records.md, "The watch")
# =============================================================================

# The deadline is 90 minutes, about four times the longest working child that a live run measured (ADR-050 D6). It is a constant and not an adopter
# setting: a test sets a smaller one only through ``watch``'s arguments, and the live demonstration (T160) changes this one line in an installed copy.
WATCH_SECONDS = 5400
WATCH_POLL_SECONDS = 5
WATCH_STAGE = "threat-model"  # the banner of its refusals: Phase 2 belongs to the run-level stage


def _watch_ids(dispatch_ids: Any) -> List[str]:
    """The wave's dispatch IDs, checked before anything waits: 1 to ``WAVE_SIZE`` of them, each a full match of the dispatch allow-list, none twice.

    Anything else is exit 2, in D4's form. A bad ID is named as ``repr`` writes it, cut at 60 characters, so a control character in it is shown escaped
    and never printed.
    """
    ids = list(dispatch_ids)
    if not 1 <= len(ids) <= WAVE_SIZE:
        raise StageError(2, WATCH_STAGE, "watch takes 1 to %d dispatch IDs, not %d" % (WAVE_SIZE, len(ids)),
                         "name the dispatches of one wave, at most %d" % WAVE_SIZE)
    for position, value in enumerate(ids):
        if not tp.id_matches("dispatch", value):
            raise StageError(2, WATCH_STAGE, "%s is not a dispatch ID" % repr(value)[:60], "pass dispatch IDs such as dsp-001")
        if value in ids[:position]:
            raise StageError(2, WATCH_STAGE, "%s is named twice" % value, "name each dispatch of the wave once")
    return ids


def _recorded(out: str, dispatch_id: str) -> bool:
    """Whether the dispatch has its record: ``<out>/.tachi-build/records/<dispatch_id>.json`` as a regular file, with no link on the way down from ``out``.

    That is D3's path guard, so a link in the file's place, or in ``records/``'s or ``.tachi-build/``'s, counts for nothing. The file is never opened: the
    orchestrator has written it when it is there, and what it holds is Step 2.8's to read.
    """
    return tp.path_guard_problem(os.path.join(out, tp.BUILD_DIR, "records", dispatch_id + ".json"), out) is None


def watch(out: Any, dispatch_ids: Any, seconds: float = WATCH_SECONDS, poll: float = WATCH_POLL_SECONDS) -> tuple:
    """Wait until every named dispatch has its record, or ``seconds`` have passed, and return ``(code, printed)``. It writes nothing.

    Code 0 with ``{"status": "done", "pending": []}`` once every record is there, and code 3 with ``{"status": "timed-out", "pending": [...]}``, the IDs
    that have none in the order they were given, when the deadline passes first. The records are looked at before the first sleep, so a wave that is
    already recorded returns at once, and once more after each sleep, so a record that landed during the last one still counts. The deadline is
    ``seconds`` on ``time.monotonic()`` from the point where the arguments have passed, and the last sleep is cut to what is left, so the exit comes
    at the deadline and not a poll after it. ``seconds`` and ``poll`` are the function interface (ADR-050 D6): the command line takes neither.

    ``--out`` is checked as the other commands check it, so a path that a document can't carry is exit 2, and so is a directory that isn't there:
    ``watch`` has no exit 1.
    """
    out = _out_dir(WATCH_STAGE, out, missing_code=2)
    ids = _watch_ids(dispatch_ids)
    deadline = time.monotonic() + seconds
    while True:
        pending = [dispatch_id for dispatch_id in ids if not _recorded(out, dispatch_id)]
        if not pending:
            return 0, {"status": "done", "pending": []}
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return 3, {"status": "timed-out", "pending": pending}
        time.sleep(min(poll, remaining))


# =============================================================================
# The command line
# =============================================================================

def _emit(obj: Dict[str, Any]) -> None:
    sys.stdout.write(_dump(obj))


def _run_plan(args: argparse.Namespace) -> int:
    _emit(plan_stage(args.stage, args.out, args.date, threats=args.threats, risk_scores=args.risk_scores,
                     baseline_dir=args.baseline_dir, architecture=args.architecture, target=args.target,
                     trees_plan=args.trees_plan, trees_plan_digest=args.trees_plan_digest))
    return 0


def _run_reconcile(args: argparse.Namespace) -> int:
    code, printed, exhausted = reconcile_stage(args.stage, args.out, args.plan, args.plan_digest)
    _emit(printed)
    if exhausted:
        first = exhausted[0]
        more = "" if len(exhausted) == 1 else " (%d batches in all ran out of retries)" % len(exhausted)
        sys.stderr.write(StageError(4, args.stage, "batch %s could not be completed within the retry caps%s" % (first["batch_id"], more),
                                    "re-run the command, and report the kept plan directory if the same batch fails again",
                                    batch=(first["batch_id"], _batch_label(args.stage, os.path.abspath(args.out), args.plan, first)),
                                    kept=tp.plan_dir(args.out, args.stage, args.plan)).text() + "\n")
    return code


def _run_fail(args: argparse.Namespace) -> int:
    code, printed, message = fail_stage(args.stage, args.out, args.plan, args.plan_digest, args.reason, args.detail)
    _emit(printed)
    sys.stderr.write(message + "\n")
    return code


def _run_close(args: argparse.Namespace) -> int:
    code, printed = close_stage(args.stage, args.out, args.plan, args.plan_digest)
    _emit(printed)
    return code


def _run_architecture_source(args: argparse.Namespace) -> int:
    code, printed = architecture_source(args.threats, args.architecture)
    _emit(printed)
    for warning in printed["warnings"]:
        sys.stderr.write("WARNING: %s\n" % warning["detail"])
    return code


def _run_id_mark(args: argparse.Namespace) -> int:
    code, printed = id_mark(args.threats, None if args.no_baseline else args.baseline)
    _emit(printed)
    return code


def _run_watch(args: argparse.Namespace) -> int:
    code, printed = watch(args.out, args.dispatch_ids)
    _emit(printed)
    return code


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tachi-stage.py", description="Plan, reconcile and fail a batched tachi stage (F-374).")
    parser.add_argument("--version", action="version",
                        version="tachi-stage.py %s (python %s)" % (tp.VERSION, platform.python_version()))
    commands = parser.add_subparsers(dest="command", required=True)
    stages = sorted(tp.STAGE_AGENTS)

    plan = commands.add_parser("plan", help="split a stage's units into batches and write the plan",
                               epilog="Each stage takes only its own pointers, and any other is refused: " + "; ".join(
                                   "%s: %s" % (name, ", ".join("--" + pointer.replace("_", "-") for pointer in PLAN_POINTERS[name]) or "none")
                                   for name in (THREAT_MODEL, THREATS_MD, TREES, REPORT)) + "; risk-score and compensating-controls: every pointer but "
                               "--trees-plan and --trees-plan-digest.")
    plan.add_argument("--stage", required=True, choices=stages)
    plan.add_argument("--out", required=True, help="the run's output directory; everything is written under it")
    plan.add_argument("--date", required=True, help="the scoring date, YYYY-MM-DD")
    plan.add_argument("--threats", help="the threats.md to read the reference finding set from (required for risk-score, trees and report; "
                                        "compensating-controls reaches it through risk-scores.md's source_file, so there it is optional and must be that file; "
                                        "threat-model and threats-md take none)")
    plan.add_argument("--risk-scores", help="the risk-scores.md that compensating-controls plans from (required there; the risk-scores.sarif "
                                            "beside it is read when it is absent)")
    plan.add_argument("--baseline-dir", help="a baseline run directory (the scorer, the controls and the trees stage)")
    plan.add_argument("--architecture", help="a candidate path to the architecture file")
    plan.add_argument("--target", help="the codebase directory a stage reads (required for compensating-controls)")
    plan.add_argument("--trees-plan", help="the trees plan's ID, for the report stage (required there): the plan that its last reconcile finished")
    plan.add_argument("--trees-plan-digest", help="the digest that the trees plan's last reconcile printed (required for the report stage)")
    plan.set_defaults(run=_run_plan)

    for name, run, text, choices in (("reconcile", _run_reconcile, "work out what is done, and what to dispatch next", stages),
                                     ("fail", _run_fail, "end a stage that can't finish, and put earlier outputs back", stages),
                                     ("close", _run_close, "end the run-level plan on the success path: fold in the checks' hand-off files, check the "
                                                           "declared paths and write the stage record", [THREAT_MODEL])):
        command = commands.add_parser(name, help=text)
        command.add_argument("--stage", required=True, choices=choices)
        command.add_argument("--out", required=True)
        command.add_argument("--plan", required=True, help="the plan ID that plan printed")
        command.add_argument("--plan-digest", required=True, help="the plan_digest that the last plan or reconcile printed")
        if name == "fail":
            command.add_argument("--reason", required=True, choices=sorted(REASONS))
            command.add_argument("--detail", help="at most 500 characters of plain text, such as the agent that failed")
        command.set_defaults(run=run)

    source = commands.add_parser("architecture-source", help="write the threats.md line that names the architecture file")
    source.add_argument("--threats", required=True, help="the threats.md to edit in place")
    source.add_argument("--architecture", required=True, help="the command's own path to the architecture file; the shared resolver checks it")
    source.set_defaults(run=_run_architecture_source)

    mark = commands.add_parser("id-mark", help="write the threats.md line that holds the ID high-water mark, so an ID is never issued twice")
    mark.add_argument("--threats", required=True, help="the threats.md to edit in place")
    baseline = mark.add_mutually_exclusive_group(required=True)
    baseline.add_argument("--baseline", help="the baseline run's threats.md, which holds the earlier mark (or, with none, the findings to seed one from)")
    baseline.add_argument("--no-baseline", action="store_true", help="the run has no baseline")
    mark.set_defaults(run=_run_id_mark)

    waiting = commands.add_parser("watch", help="wait until every dispatch of a Phase 2 wave has its record, or the deadline passes")
    waiting.add_argument("--out", required=True, help="the run's output directory; the records are looked for under it, and nothing is written")
    waiting.add_argument("dispatch_ids", nargs="*", metavar="DSP", help="the wave's dispatch IDs, 1 to 16 of them, such as dsp-001")
    waiting.set_defaults(run=_run_watch)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    return tp.run_entry(stage=None, renderer="tachi-stage.py", args=args, run=args.run, defect=False)  # D4's four-line message and exit code; any other exception is raised again


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_exit_codes_come_from_a_real_interpreter)
    raise SystemExit(main())
