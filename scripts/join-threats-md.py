#!/usr/bin/env python3
"""Join the ``threats-md`` parts into ``threats.md`` (F-374; ADR-050 D3, D4, D6 item O-beta, D15).

The orchestrator compiles the threat model in its own context (C-7), writes a section manifest after Phase 4 and then writes the model's rows, one
table to a part, and this script lays the whole file out around them. It runs once, after ``tachi-stage.py reconcile`` exits 0 for the ``threats-md``
stage:

    python3 scripts/join-threats-md.py --out DIR --plan ID --plan-digest HEX

The order is D4's. It checks the plan (its pointer and digest, every input and batch input, and that every batch is ``done``), reads the manifest at
its fixed path, ``{out}/.tachi-build/sections.json``, and re-validates it, then re-validates every part it joins against its batch input's units. It
refuses a plan whose batches don't cover exactly the rows and findings that the manifest names. It writes the file to ``<plan_id>/staged/``, reads it
back from disk and checks it, and only when every check passes does it move the file onto ``{out}/threats.md`` with ``os.replace``. It then writes the
``threats-md`` stage record. A check that fails leaves the canonical file as it was.

**What the model writes, and what is written here (item O-beta).** A part holds the rows of one table, under the table's closed keys, and nothing in it
is markdown. This script writes everything that isn't a row: the frontmatter (from the manifest, in the template's shape, ``schema_version`` 1.4), the
title, every heading, header and separator row, the fixed tables (Section 3's and Section 4's prefix tables, the 3x3 risk matrix of Sections 3 and 6)
and the notes that the contract lists, each printed only in its state. It writes no other prose, and nothing of Phase 3.5's outcome record, the
populator's block or the two body lines (FR-E.18's carrier and the ID mark): their scripts upsert those after the join. Section 7's rows are sorted by
risk level, Critical first, then in the order the findings appear in Sections 3 and 4, and its Category cell is a function of the ID. IDs are written
as the manifest spells them and compared in canonical form.

**Escaping (D3).** Every cell takes the cell sink, and every ``#`` in it is also written ``&#35;``, in the same pass, so that a cell that quotes
``## 7. Recommended Actions`` can't stand in for the heading that the reference-set reader finds by substring. Each row is written ``| cell | ... |``
with a space on each side of every delimiter, so a cell that ends in a backslash can't escape the pipe that closes it (S1P-A21: Section 7's readers
read GitHub's ``\\|`` as a pipe in a cell). A character that ``tachi_parts.forbidden_character`` returns never reaches a cell: the manifest's strings
and every part's values are refused at intake with exit 2 (S1P-A18), and the staged file is checked for one again.

**What is checked from disk (exit 4).** The staged file, read back through ``tachi_parsers.parse_reference_set``, must give exactly the manifest's open
IDs, each once and spelled as the manifest spells it, and exactly its resolved IDs (none when the run has no baseline), each with the values that its
item holds, under the reader's own normalization. Those values are compared with the validated items, the sources, and never with a second read of the
file by the same reader (P1-4, KB 22). The file must also hold no forbidden character, and end with this script's provenance stamp. Heading order and
the headers are constants, which a drift test pins against the template, so they are not checked at run time.

Exit codes are ``contracts/cli.md``'s: 0 done, 1 the plan, the manifest or a part is missing (or ``--out`` is no directory), 2 a validation or guard
failure (a digest or pointer mismatch, a batch that isn't done, a manifest or part that fails re-validation, a plan that doesn't match the manifest, a
forbidden character in an input), 4 a check on the staged file failed or a file could not be written. A failure prints D4's four-line message on stderr.
Stdout is one JSON object, ``{"record", "counts"}``.

Nothing here reads the clock except the stage record's ``finished_utc``. The input digest of the stamp covers the manifest's digest, the plan's
parameters and the accepted parts' items in plan order, and never the plan ID, so the file is byte-stable across plans (NFR-2). Standard library plus
the shared helpers, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("join-threats-md.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import json
import os
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402

STAGE = "threats-md"
RENDERER = "join-threats-md.py"  # the stamp's name: the installed file name, as a literal (contracts/cli.md)
MD = "threats.md"
MANIFEST = "sections.json"
SCHEMA_VERSION = "1.4"  # D15: threats.md stays 1.4
TITLE = "# Threat Model Report"

# The eight tables of Sections 3 and 4, in order: a finding is placed in one by its prefix, and Section 7's Category cell is the table's title.
FINDING_TABLES = [section for section in tp.THREATS_MD_SECTIONS if section.keyed == "prefixes"]
CATEGORY_TITLES = {"spoofing": "Spoofing", "tampering": "Tampering", "repudiation": "Repudiation", "information_disclosure": "Information Disclosure",
                   "denial_of_service": "Denial of Service", "elevation_of_privilege": "Elevation of Privilege", "agentic": "Agentic", "llm": "LLM"}
TABLE_OF_PREFIX = {prefix: (index, section.key) for index, section in enumerate(FINDING_TABLES) for prefix in section.prefixes}

# The template's fixed text (part-files.md, "The joiner's layout"). The notes are printed only in their state.
PREFIX_LABEL = "**ID prefix convention:**"
MATRIX_LABEL = "**Risk level computation (OWASP 3x3 matrix):**"
MATRIX = ("| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |", "|---|---|---|---|", "| **HIGH Impact** | Medium | High | Critical |",
          "| **MEDIUM Impact** | Low | Medium | High |", "| **LOW Impact** | Note | Low | Medium |")
STRIDE_PREFIXES = ("| Prefix | Category |", "|--------|----------|", "| S | Spoofing |", "| T | Tampering |", "| R | Repudiation |",
                   "| I | Information Disclosure |", "| D | Denial of Service |", "| E | Elevation of Privilege |")
AI_PREFIXES = ("| Prefix | Category |", "|--------|----------|", "| AG | Agentic Threats |", "| LLM | LLM Threats |")
CALIBRATION_HEADING = "### Risk Calibration Matrix"
NOTE_NO_BOUNDARIES = "No trust boundaries were identified in the architecture input."  # the contract names the state; these words are trust-boundaries.md's
NOTE_NO_AI = "No AI threat findings were recorded."
NOTE_NO_CORRELATIONS = "> No cross-agent correlations detected."
NOTE_NO_RESOLVED = "No baseline findings were resolved in this run."
NOTE_FOOTNOTE = "Counts reflect deduplicated findings: each correlation group counts once."
NOTE_GATE_PASSED = "Coverage gate passed \u2014 all required threat categories evaluated for every component."
SECTION_6_SENTENCE = ("Risk summary counts below reflect deduplicated findings. When correlation groups exist, correlated findings count as one "
                      "unique threat per group rather than individually.")

RECORD_REMEDY = "re-run the plan step: the plan and the section manifest must agree"
PROBLEM_LIMIT = 20  # a staged file that fails many ways reports the first few


# =============================================================================
# The plan and the manifest (ADR-050 D3, D6 item O-beta)
# =============================================================================

def _same_file(first: str, second: str) -> bool:
    try:
        return os.path.samefile(first, second)
    except OSError:
        return False


def _read_manifest(out: str, plan: Mapping[str, Any], kept: str) -> Tuple[Dict[str, Any], str]:
    """The re-validated section manifest, and the digest that the plan recorded for it.

    The plan trusts the manifest through that digest alone, and ``trusted_plan`` has already checked the file against it. The manifest is read at its
    fixed path, so the plan must record exactly that file. Reading it once more here (``entry_document`` is the strict loader of D3) then compares the
    digest again, so the version that was validated is the version the plan pinned.
    """
    path = os.path.join(out, tp.BUILD_DIR, MANIFEST)
    recorded = [entry for entry in plan["inputs"].values() if _same_file(entry["path"], path)]
    if len(recorded) != 1:
        raise tp.StageFailure(2, STAGE, "the plan does not record the section manifest at its fixed path", RECORD_REMEDY, kept=kept)
    manifest = tp.entry_document(STAGE, path, out, tp.SECTIONS_SCHEMA, "the section manifest", kept)
    if tp.file_digest(path) != recorded[0]["sha256"]:
        raise tp.StageFailure(2, STAGE, "the section manifest changed since plan", RECORD_REMEDY, kept=kept)
    rows = manifest["rows"]
    if manifest["resolved"] is None and (rows["lifecycle"] or rows["baseline_reference"]):
        raise tp.StageFailure(2, STAGE, "the section manifest counts rows for Section 8, and a run with no baseline has no Section 8",
                              "regenerate the manifest: Section 8 belongs to a run with a baseline", kept=kept)
    return manifest, recorded[0]["sha256"]


def _expected_units(manifest: Mapping[str, Any]) -> Dict[str, List[Any]]:
    """What the manifest says each table holds, in the order the file shows it: the row numbers of a table that no finding keys, and the canonical IDs of
    a finding table in S-2 order. Section 7 holds every open ID and Section 4c every resolved one, so one Section 7 row per ID and Section 4c's set hold
    by construction (the manifest refuses an ID that is in both)."""
    opened = sorted((tp.canonical_finding_id(value) for value in manifest["open"]), key=tp.finding_sort_key)
    resolved = sorted((tp.canonical_finding_id(value) for value in manifest["resolved"] or ()), key=tp.finding_sort_key)
    expected: Dict[str, List[Any]] = {}
    for section in tp.THREATS_MD_SECTIONS:
        if section.keyed == "row":
            expected[section.key] = list(range(1, manifest["rows"][section.key] + 1))
        elif section.keyed == "prefixes":
            expected[section.key] = [value for value in opened if value.partition("-")[0] in section.prefixes]
        else:
            expected[section.key] = list(opened if section.keyed == "open" else resolved)
    return expected


def _batch_label(entry: Mapping[str, Any], units: Sequence[Mapping[str, Any]]) -> str:
    """The ``Batch`` line of D4's message: the batch's findings, or for a table that no finding keys, its rows."""
    if entry["finding_ids"]:
        return ", ".join(entry["finding_ids"])
    rows = [unit["row"] for unit in units if isinstance(unit, dict) and type(unit.get("row")) is int]
    section = units[0].get("section") if units and isinstance(units[0], dict) else None
    return "rows %d to %d of %s" % (min(rows), max(rows), section) if rows and isinstance(section, str) else "no finding"


def _collect(out: str, plan: Mapping[str, Any], kept: str) -> Tuple[Dict[str, Dict[Any, Dict[str, Any]]], List[Dict[str, Any]]]:
    """Every ``done`` batch's part, re-validated against its batch input: ``(items by table and unit, the accepted items in plan order)``.

    A unit is a row number, or a canonical finding ID. The plan lists a halved batch's children next to it, so plan order is unit order. A halved parent
    holds no part of its own, and ``trusted_plan`` has already refused a batch that is still ``pending`` or ``failed``. A part that no longer validates
    is exit 1 if it is missing and exit 2 otherwise, and names its batch.
    """
    found: Dict[str, Dict[Any, Dict[str, Any]]] = {}
    accepted: List[Dict[str, Any]] = []
    plan_id = plan["plan_id"]
    for entry in plan["batches"]:
        if entry["state"] != "done":
            continue
        batch_id = entry["batch_id"]
        batch = tp.entry_document(STAGE, tp.input_path(out, STAGE, plan_id, batch_id), out, tp.BATCH_INPUT_SCHEMA, "the batch input %s" % batch_id, kept)
        units = batch["units"]
        result = tp.read_part(tp.part_path(out, STAGE, plan_id, batch_id, entry["attempt"]), out, plan_id, batch_id, STAGE, plan["agent_type"],
                              entry["finding_ids"], units)
        if result.state != "done":
            raise tp.StageFailure(1 if result.state == "missing" else 2, STAGE, "the part of batch %s is %s (%s)" % (batch_id, result.state, result.detail),
                                  "re-run the command: only a part that validates counts", batch=(batch_id, _batch_label(entry, units)), kept=kept)
        items = result.part["items"]
        table = found.setdefault(units[0]["section"], {})
        unit_keys = [unit["row"] for unit in units] if "row" in units[0] else [item["finding_id"] for item in items]
        for unit_key, item in zip(unit_keys, items):
            if unit_key in table:
                raise tp.StageFailure(2, STAGE, "two batches carry the same unit of %s" % units[0]["section"], RECORD_REMEDY,
                                      batch=(batch_id, _batch_label(entry, units)), kept=kept)
            table[unit_key] = item
        accepted.extend(items)
    return found, accepted


def _tables(expected: Mapping[str, List[Any]], found: Mapping[str, Mapping[Any, Dict[str, Any]]], kept: str) -> Dict[str, List[Dict[str, Any]]]:
    """Each table's items in the order the file shows them, once the plan is proven to cover exactly what the manifest names (exit 2 if it doesn't).

    Section 7 is then sorted by risk level, Critical first, then in the order the findings appear in Sections 3 and 4: the eight tables in order, and
    S-2 order within each.
    """
    for key in list(expected) + [name for name in found if name not in expected]:
        if set(found.get(key, {})) != set(expected.get(key, [])):
            raise tp.StageFailure(2, STAGE, "the plan's batches do not cover the rows that the section manifest names for %s" % key, RECORD_REMEDY, kept=kept)
    tables = {key: [found[key][unit] for unit in units] for key, units in expected.items() if units}
    tables = {section.key: tables.get(section.key, []) for section in tp.THREATS_MD_SECTIONS}
    tables["actions"].sort(key=lambda item: (tp.RISK_LEVELS.index(item["risk_level"]), TABLE_OF_PREFIX[_prefix(item["finding_id"])][0],
                                             tp.finding_sort_key(item["finding_id"])))
    return tables


def _prefix(finding_id: str) -> str:
    return tp.canonical_finding_id(finding_id).partition("-")[0]


# =============================================================================
# The layout (part-files.md, "The joiner's layout")
# =============================================================================

def _cell(text: str) -> str:
    """D3's cell sink, and every ``#`` written ``&#35;`` in the same pass, so that a reference the sink writes (``&#124;`` holds a ``#``) is never escaped
    twice. A ``{{`` can't span a ``#``, so each piece is escaped alone."""
    return "&#35;".join(tp.escape_cell(piece) for piece in text.split("#"))


def _row_line(cells: Sequence[str]) -> str:
    """``| cell | cell |``: a space on each side of every delimiter, so a cell that ends in a backslash can't escape the pipe after it (S1P-A21)."""
    return "| " + " | ".join(cells) + " |"


def _table(section: Any, items: Sequence[Mapping[str, Any]], spelling: Mapping[str, str]) -> List[str]:
    header = list(section.header)
    lines = [_row_line(header), "|" + "|".join("-" * (len(cell) + 2) for cell in header) + "|"]
    for item in items:
        values = [spelling[item["finding_id"]] if key == "finding_id" else item[key] for key in section.keys]
        if section.key == "actions":  # the joiner's one cell: the prefix's table title, after Status
            values.insert(header.index("Category"), CATEGORY_TITLES[TABLE_OF_PREFIX[_prefix(item["finding_id"])][1]])
        lines.append(_row_line([_cell(value) for value in values]))
    return lines


def _frontmatter(manifest: Mapping[str, Any]) -> List[str]:
    """The template's YAML shape. The manifest has refused a quote, a backslash and any forbidden character in each string, so each is written as it is."""
    front = manifest["frontmatter"]
    baseline, gate = front["baseline"], front["coverage_gate"]

    def scalar(value: Optional[str]) -> str:
        return "null" if value is None else '"%s"' % value

    lines = ["---", 'schema_version: "%s"' % SCHEMA_VERSION, 'date: "%s"' % front["date"], 'input_format: "%s"' % front["input_format"],
             'classification: "%s"' % front["classification"], 'run_id: "%s"' % front["run_id"], "baseline:", "  source: %s" % scalar(baseline["source"]),
             "  date: %s" % scalar(baseline["date"]), "  finding_count: %s" % ("null" if baseline["finding_count"] is None else baseline["finding_count"]),
             "  run_id: %s" % scalar(baseline["run_id"]), "coverage_gate:", '  status: "%s"' % gate["status"]]
    if gate["gaps"]:
        lines.append("  gaps:")
        lines += ['    - { component: "%s", missing_category: "%s", resolution: "%s" }' % (gap["component"], gap["missing_category"], gap["resolution"])
                  for gap in gate["gaps"]]
    else:
        lines.append("  gaps: []")
    return lines + ["---"]


def _present(manifest: Mapping[str, Any], tables: Mapping[str, Sequence[Any]], key: str) -> bool:
    """Whether a table is in the file: 4b and the gap details only when they have rows, and 4c and Section 8 only when the run has a baseline."""
    if key in ("patterns", "gate_gaps"):
        return bool(tables[key])
    if key in ("resolved", "lifecycle", "baseline_reference"):
        return manifest["resolved"] is not None
    return True


def _after_heading(heading: str, tables: Mapping[str, Sequence[Any]]) -> List[List[str]]:
    """The fixed tables and notes that follow a heading, as blocks of lines."""
    if heading == "## 2. Trust Boundaries":
        return [[NOTE_NO_BOUNDARIES]] if not tables["trust_zones"] and not tables["boundary_crossings"] else []
    if heading == "## 3. STRIDE Tables":
        return [[PREFIX_LABEL], list(STRIDE_PREFIXES), [MATRIX_LABEL], list(MATRIX)]
    if heading == "## 4. AI Threat Tables":
        return [[PREFIX_LABEL], list(AI_PREFIXES)] + ([[NOTE_NO_AI]] if not tables["agentic"] and not tables["llm"] else [])
    if heading == "## 4a. Correlated Findings":
        return [[NOTE_NO_CORRELATIONS]] if not tables["correlated"] else []
    if heading == "## 4c. Resolved Findings":
        return [[NOTE_NO_RESOLVED]] if not tables["resolved"] else []
    if heading == "## 5a. Coverage Gate Results":
        return [[NOTE_GATE_PASSED]] if not tables["gate_gaps"] else []
    if heading == "## 6. Risk Summary":
        return [[CALIBRATION_HEADING], list(MATRIX)]
    return []


def _render(manifest: Mapping[str, Any], tables: Mapping[str, Sequence[Dict[str, Any]]], spelling: Mapping[str, str], digest: str) -> str:
    """The whole file: blocks of lines with one blank line between them, ending in the provenance stamp."""
    blocks: List[List[str]] = [_frontmatter(manifest), [TITLE]]
    for section in tp.THREATS_MD_SECTIONS:
        if not _present(manifest, tables, section.key):
            continue
        for heading in section.headings:
            blocks.append([heading])
            blocks.extend(_after_heading(heading, tables))
        if section.key == "risk_levels":
            blocks.append([SECTION_6_SENTENCE])
        blocks.append(_table(section, tables[section.key], spelling))
        if section.key == "coverage" and tables["correlated"]:
            blocks.append([NOTE_FOOTNOTE])
    return "\n\n".join("\n".join(block) for block in blocks) + "\n\n" + tp.stamp_comment(RENDERER, digest) + "\n"


# =============================================================================
# The checks on the staged file (ADR-050 D4 steps 5 and 6; KB 22; P1-4)
# =============================================================================

def _ids(values: Sequence[str]) -> str:
    return ", ".join(values[:5]) + (" and %d more" % (len(values) - 5) if len(values) > 5 else "")


def _expected_findings(tables: Mapping[str, Sequence[Mapping[str, Any]]], spelling: Mapping[str, str]) -> Dict[str, Dict[str, Dict[str, str]]]:
    """What the reference-set reader must give back for each finding: the values of its validated item, under the reader's own normalization.

    The reader strips a cell, drops its bold markers and decodes it, and the validated item holds the text before any of that, so the bold markers go
    here too. The reader normalizes the status and the pattern with its own functions, so those are applied to the item's value. These are the sources,
    never a second read of the file (P1-4).
    """
    bold = tachi_parsers.strip_bold
    opened = {}
    for item in tables["actions"]:
        opened[item["finding_id"]] = {
            "id": spelling[item["finding_id"]], "component": bold(item["component"]).strip(), "threat": bold(item["threat"]).strip(),
            "risk_level": bold(item["risk_level"]).strip(), "mitigation": bold(item["mitigation"]).strip(),
            "delta_status": tachi_parsers.normalize_delta_status(item["status"]), "agentic_pattern": tachi_parsers.parse_finding_pattern(item["pattern"])}
    resolved = {}
    for item in tables["resolved"]:
        resolved[item["finding_id"]] = {
            "id": spelling[item["finding_id"]], "component": bold(item["component"]).strip(), "threat": bold(item["threat"]).strip(),
            "risk_level": bold(item["last_risk_level"]).strip(), "resolution_reason": bold(item["resolution_reason"]).strip()}
    return {"open": opened, "resolved": resolved}


def _compare(label: str, read: Sequence[Mapping[str, Any]], expected: Mapping[str, Mapping[str, str]], problems: List[str]) -> None:
    """One list of the reference set (``open`` for Section 7, ``resolved`` for Section 4c) against the manifest's IDs and the items' values."""
    by_id = {tp.canonical_finding_id(found["id"]): found for found in read}
    missing = sorted((key for key in expected if key not in by_id), key=tp.finding_sort_key)
    extra = sorted((key for key in by_id if key not in expected), key=tp.finding_sort_key)
    if missing:
        problems.append("%s has no row for %s" % (label, _ids(missing)))
    if extra:
        problems.append("%s has a row for %s, which the manifest does not name" % (label, _ids(extra)))
    for key in sorted((key for key in expected if key in by_id), key=tp.finding_sort_key):
        wanted, found = expected[key], by_id[key]
        if found["id"] != wanted["id"]:
            problems.append("%s spells %s as %s, and the manifest spells it %s" % (label, key, found["id"], wanted["id"]))
        for field in wanted:
            if field != "id" and found.get(field) != wanted[field]:
                problems.append("%s's %s for %s differs from the part's" % (label, field, key))


def _check_reference_set(text: str, expected: Mapping[str, Mapping[str, Mapping[str, str]]]) -> List[str]:
    """Section 7 and Section 4c, read back through the reference-set reader that the next stage uses, against the manifest and the validated items."""
    problems: List[str] = []
    try:
        reference = tachi_parsers.parse_reference_set(text, MD)
    except tachi_parsers.ReferenceSetError as exc:
        return ["Section 7 can't be read back from the staged file: %s" % exc.reason]
    if reference["duplicates"]:
        problems.append("the staged file repeats %s: the reference set holds each finding once" % _ids(reference["duplicates"]))
    if reference["form"] != "table" or reference["lacking"]:
        needs = sorted({name for names in reference["lacking"].values() for name in names})
        problems.append("Section 7 lacks a column that a stage needs (%s)" % (", ".join(needs) or "the table form"))
    _compare("Section 7", reference["open"], expected["open"], problems)
    _compare("Section 4c", reference["resolved"], expected["resolved"], problems)
    return problems


def _check_staged(staged: Mapping[str, str], rendered: str, digest: str, expected: Mapping[str, Mapping[str, Mapping[str, str]]]) -> List[str]:
    """Everything that can be wrong with the file as it now sits on disk. Empty when it is right."""
    text = staged[MD]
    problems: List[str] = []
    if text != rendered:
        problems.append("the staged %s is not the text that was rendered" % MD)
    forbidden = tp.forbidden_character(text)
    if forbidden is not None:
        problems.append("the staged %s holds the character U+%04X, which the part contract forbids, at line %d"
                        % (MD, ord(forbidden), text.count("\n", 0, text.find(forbidden)) + 1))
    stamp = tp.read_stamp(text)
    if stamp is None or (stamp["renderer"], stamp["version"], stamp["input_digest"]) != (RENDERER, tp.VERSION, digest):
        problems.append("the markdown's provenance stamp is missing or wrong")
    elif text.rstrip("\n").split("\n")[-1] != tp.stamp_comment(RENDERER, digest):
        problems.append("the provenance stamp is not the last line of the markdown")
    problems += _check_reference_set(text, expected)
    return problems[:PROBLEM_LIMIT]


# =============================================================================
# The command line
# =============================================================================

def _build_parser() -> argparse.ArgumentParser:
    return tp.build_parser(RENDERER, "Join the threats-md parts into threats.md (F-374).")


def _run(args: argparse.Namespace) -> int:
    out = tp.entry_arguments(STAGE, args.out, args.plan, args.plan_digest)
    kept = tp.plan_dir(out, STAGE, args.plan)
    if not os.path.lexists(os.path.join(out, tp.BUILD_DIR, MANIFEST)):  # D4 puts a missing manifest at exit 1, ahead of the guard's exit 2 for an input that vanished
        raise tp.StageFailure(1, STAGE, "the section manifest is missing", "re-run the command: the orchestrator writes it after Phase 4")

    plan, _inputs = tp.trusted_plan(STAGE, out, args.plan, args.plan_digest, complete=True, read_inputs=True, kept=True)
    manifest, manifest_digest = _read_manifest(out, plan, kept)
    expected = _expected_units(manifest)
    found, accepted = _collect(out, plan, kept)
    tables = _tables(expected, found, kept)

    spelling = {tp.canonical_finding_id(value): value for value in list(manifest["open"]) + list(manifest["resolved"] or ())}
    digest = tp.input_digest({"sources": {"sections": manifest_digest}, "params": plan["params"], "items": accepted, "fragments": []})
    rendered = _render(manifest, tables, spelling, digest)
    wanted = _expected_findings(tables, spelling)
    tp.stage_and_move(STAGE, out, args.plan, {MD: rendered}, lambda staged: _check_staged(staged, rendered, digest, wanted), kept)

    counts = {"units": plan["unit_count"], "open": len(manifest["open"]), "resolved": len(manifest["resolved"] or ()),
              "rendered": sum(len(items) for items in tables.values())}
    record = tp.write_stage_record(STAGE, RENDERER, out, plan, digest, counts, tp.output_entries(out, [MD]), [], [], kept)
    print(json.dumps({"record": tp.stage_record_path(out, STAGE, args.plan), "counts": record["counts"]}, sort_keys=True))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    return tp.run_entry(stage=STAGE, renderer=RENDERER, args=_build_parser().parse_args(argv), run=_run)


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_runtime_floor_374.py)
    raise SystemExit(main())
