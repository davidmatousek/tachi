"""Goldens for ``scripts/join-threats-md.py`` (F-374 T106 and T107). They were written before the script, and T106 wrote the joiner to them.

They target ``contracts/part-files.md`` ("Stage payload: threats-md": the joiner's layout, its checks and its exit codes),
``contracts/cli.md`` (the exit table, ``PLAN``, the stamp's renderer), ``contracts/module-signatures.md`` (the shared stage-entry
path), ``contracts/threat-model-records.md`` ("The section manifest") and ADR-050 D3 (the strict loader, the cell sink), D4 (the
write order, failure, the stamp), D6's item O-beta (the ruling) and D15 (``threats.md`` is 1.4), never an implementation. The from-disk
seeds name every value that the reference-set reader gives back, so a comparison that drops one, or that compares the file with a second
read of itself, turns one red (P1-4).

Two errata of the W2' entry's cross-read are pinned where they apply. S1P-A18: the joiner refuses at intake, with exit 2, every
character that ``tachi_parts.forbidden_character`` returns, in the manifest and in a part. S1P-A21: each row is written with a space
on each side of every delimiter, so a Section 7 cell that ends in a backslash reads back whole under the reader that takes GitHub's
``\\|`` for a pipe. The binding P1-4 rule holds throughout: what the reference-set reader gives back from a file is compared with the
sources (the manifest and the validated items), never with a second read of the file by the same reader.

How they run (ADR-050 D16, H15): the entry is loaded through ``tests/conftest.py``'s ``_load_hyphenated_script`` and driven in-process
through ``main(argv)``, so pytest-cov counts it. Nothing here starts a subprocess: the one thing a process alone shows, the 3.9
refusal before any import, is ``test_runtime_floor_374.py``'s.

``tachi-stage.py plan --stage threats-md`` is T092's, and it is not in this lane's base. ``Run`` below stands in for it: it writes the
plan, the pointer and the batch inputs that ``part-files.md`` describes (one batch for each part, a table's rows in balanced contiguous
runs at the table's size, a halved batch's children next to their parent), and every document it writes is checked by
``tachi_parts``' own validators, so a stand-in that drifts from the contract fails here and not in a test below.

What these goldens assume of ``join-threats-md.py`` (where a contract left a form open, the test says ``# reading:``):

1. **The CLI** is ``join-threats-md.py --out DIR --plan ID --plan-digest HEX`` with ``--help`` and ``--version``, and
   ``main(argv=None) -> int``. Exit 0 writes ``{out}/threats.md`` and the stage record. 1 is a missing plan, manifest or part, and a
   ``--out`` that is no directory. 2 is a digest or pointer mismatch, a batch that is not ``done``, a manifest or a part that fails
   re-validation, and a character that the part contract forbids. 4 is a failed check on the staged file, or a failed write. There is no
   exit 3 or 5. A failure prints D4's message on stderr and writes nothing but what is already staged.
2. **Where it reads.** The manifest at its fixed path, ``{out}/.tachi-build/sections.json``, whose digest the plan recorded in its
   ``inputs`` (reading: under any name, so the joiner finds it by its path), and the plan's ``done`` batches, each part read at its batch's
   current attempt against its batch input's units. The plan's ``params`` and the manifest's digest are in the stamp's input digest.
3. **What it writes.** The frontmatter and every heading, header, fixed table and note, from constants, in the template's order, and the
   parts' rows between them. It writes no other prose, and nothing of Phase 3.5's record, the populator's block or the two body lines.
4. **Its checks** are the contract's: re-validation (exit 2), and from the staged file, read back through ``parse_reference_set``, the
   set of Section 7 and Section 4c, each finding's values, the stamp and the forbidden characters (exit 4).
5. **Stdout** is one JSON object, ``{record, counts}`` (reading: cli.md fixes no key set for the joiner), and the stage record is
   ``<plan>/stage-record.json`` with the four counts ``units``, ``open``, ``resolved`` and ``rendered``.

The groups of tests:

* ``test_harness_*``: no joiner needed; they check the synthetic run and the stand-in planner.
* ``test_cli_*``: the entry, the argument checks and the exit table.
* ``test_run_*``: a clean run, what it writes and what it leaves alone.
* ``test_layout_*``: the frontmatter, the golden, the notes and the conditional sections.
* ``test_order_*``: section order, row order, Section 7's sort, the manifest's spelling, halved batches and NFR-2.
* ``test_escape_*``: the cell sink, the extra ``#`` rule and S1P-A21's row form.
* ``test_stamp_*``: the provenance stamp and its digest.
* ``test_intake_*``: re-validation, exit 1 and 2, and S1P-A18.
* ``test_t107_*``: the heading order and the headers against the template, one Section 7 row for each ID, and Section 4c's set.
* ``test_disk_*``: the from-disk checks, seeded one bug at a time, and the write path.
* ``test_scale_*``: many parts per table, and halved batches among them.

Fixtures are synthetic (H8). Standard library and pytest only, and Python 3.9 syntax.
"""
from __future__ import annotations

import ast
import copy
import json
import os
import re
import sys
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script
from .test_render_compensating_controls import failing_replace, tampering_with_staged
from .test_render_risk_scores import invoke, sha256_of, tree_state

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common as sc  # noqa: E402  -- after the sys.path mutation
import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402

STAGE = "threats-md"
AGENT = "tachi-orchestrator"
RENDERER = SCRIPTS_DIR / "join-threats-md.py"
# The stamp's renderer is the installed file name, with .py, as one literal (cli.md, "The stamp's renderer").
RENDERER_NAME = "join-threats-md.py"
FAILED = "TACHI THREATS-MD FAILED:"
MD = "threats.md"
TEMPLATE = REPO_ROOT / "templates" / "tachi" / "output-schemas" / "threats.md"
OUTPUT_SCHEMAS = REPO_ROOT / ".claude" / "skills" / "tachi-orchestration" / "references" / "output-schemas.md"
PLAN_ID = "20261122T101500Z-0123456789ab"
OTHER_PLAN_ID = "20261123T090000Z-ba9876543210"
DATE = "2026-11-22"
RUN_ID = "2026-11-22T10-15-00"
BASELINE_RUN_ID = "2026-11-01T10-00-00"
EM = "\u2014"
LAYER = "L4 " + EM + " Deployment Infrastructure"
EARLIER = b"# the earlier run's threats.md\n"
CHECK_FAILED = "a completeness or parity check failed on the staged files"

# The notes and the sentence that the joiner writes in fixed text (part-files.md, "The joiner's layout"). Each is printed only in its state.
# Section 2's note: the contract gives the state and not the words, so these are the repo's own (see test_layout_section_2s_note_is_the_sentence_the_references_use)
NOTE_NO_BOUNDARIES = "No trust boundaries were identified in the architecture input."
TRUST_BOUNDARIES_REFERENCE = REPO_ROOT / ".claude" / "skills" / "tachi-orchestration" / "references" / "trust-boundaries.md"
NARRATIVE_TEMPLATES = REPO_ROOT / ".claude" / "skills" / "tachi-threat-reporting" / "references" / "narrative-templates.md"
NOTE_NO_AI = "No AI threat findings were recorded."
NOTE_NO_CORRELATIONS = "> No cross-agent correlations detected."
NOTE_NO_RESOLVED = "No baseline findings were resolved in this run."
NOTE_FOOTNOTE = "Counts reflect deduplicated findings: each correlation group counts once."
NOTE_GATE_PASSED = "Coverage gate passed " + EM + " all required threat categories evaluated for every component."
SECTION_6_SENTENCE = ("Risk summary counts below reflect deduplicated findings. When correlation groups exist, correlated findings count as one "
                      "unique threat per group rather than individually.")
NOTES = (NOTE_NO_BOUNDARIES, NOTE_NO_AI, NOTE_NO_CORRELATIONS, NOTE_NO_RESOLVED, NOTE_FOOTNOTE, NOTE_GATE_PASSED, SECTION_6_SENTENCE)
PREFIX_LABEL = "**ID prefix convention:**"
MATRIX_LABEL = "**Risk level computation (OWASP 3x3 matrix):**"
MATRIX = ["| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |", "|---|---|---|---|", "| **HIGH Impact** | Medium | High | Critical |",
          "| **MEDIUM Impact** | Low | Medium | High |", "| **LOW Impact** | Note | Low | Medium |"]
STRIDE_PREFIXES = ["| Prefix | Category |", "|--------|----------|", "| S | Spoofing |", "| T | Tampering |", "| R | Repudiation |",
                   "| I | Information Disclosure |", "| D | Denial of Service |", "| E | Elevation of Privilege |"]
AI_PREFIXES = ["| Prefix | Category |", "|--------|----------|", "| AG | Agentic Threats |", "| LLM | LLM Threats |"]

# Section 7's Category cell, from the finding's prefix, and the order of the eight tables of Sections 3 and 4 (part-files.md, "The joiner's layout").
CATEGORY_OF = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information Disclosure", "D": "Denial of Service",
               "E": "Elevation of Privilege", "AG": "Agentic", "AGP": "Agentic", "TE": "Agentic", "LLM": "LLM", "OI": "LLM", "MI": "LLM"}
TABLE_OF = {"S": 0, "T": 1, "R": 2, "I": 3, "D": 4, "E": 5, "AG": 6, "AGP": 6, "TE": 6, "LLM": 7, "OI": 7, "MI": 7}
RISK_RANK = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Note": 4}
RISK_PAIR = {"Critical": ("HIGH", "HIGH"), "High": ("MEDIUM", "HIGH"), "Medium": ("MEDIUM", "MEDIUM"), "Low": ("LOW", "MEDIUM"), "Note": ("LOW", "LOW")}
FIELD = {"status": "status", "component": "component", "maestro_layer": "layer", "threat": "threat", "likelihood": "likelihood", "impact": "impact",
         "risk_level": "risk", "mitigation": "mitigation", "owasp_reference": "owasp", "pattern": "pattern", "last_risk_level": "last_risk",
         "resolution_reason": "reason"}


# =============================================================================
# 1. The synthetic run: sixteen open findings, two resolved, and the 14 tables that no finding keys
# =============================================================================

def finding(fid, status, component, risk, pattern=EM, owasp="ASI-01", layer=LAYER, **override):
    likelihood, impact = RISK_PAIR[risk]
    record = {"id": fid, "status": status, "component": component, "layer": layer, "threat": "Threat %s against %s" % (fid, component),
              "likelihood": likelihood, "impact": impact, "risk": risk, "mitigation": "Mitigation for %s" % fid, "owasp": owasp, "pattern": pattern}
    record.update(override)
    return record


# Deliberately not in S-2 order: the manifest's order is the orchestrator's, and the joiner sorts. Three values are hostile on purpose: S-2's
# mitigation ends in a backslash, R-1's in two, and D-1's threat ends in one before the next cell (S1P-A21).
OPEN_FINDINGS = [
    finding("LLM-2", "UPDATED", "LLM Agent", "Low", owasp="LLM01:2026"),
    finding("T-10", "NEW", "User Database", "Low"),
    finding("S-2", "NEW", "API Gateway", "Critical", mitigation="Rotate keys; the path is C:\\temp\\"),
    finding("AGP-01", "NEW", "Fine-Tuning Pipeline", "Critical", pattern="temporal_attack", owasp="ASI-06"),
    finding("MI-1", "NEW", "Advisor", "High", owasp="LLM07:2026"),
    finding("T-2", "UPDATED", "User Database", "High",
            threat="Quotes ## 7. Recommended Actions, ## 5. Coverage Matrix and #### Risk by MAESTRO Layer in its text"),
    finding("R-1", "UNCHANGED", "Auth Service", "Critical", mitigation="Keep a log of \\\\"),
    finding("S-1", "UNCHANGED", "API Gateway", "Medium", threat="Sends a | b <i>&</i> `code` {{x}} **bold** text"),
    finding("TE-1", "NEW", "Specialist Agent", "Note", pattern="multiple", owasp="ASI-09"),
    finding("D-1", "NEW", "API Gateway", "Critical", threat="Wipes C:\\data\\"),
    finding("E-1", "NEW", "Auth Service", "Medium"),
    finding("AG-1", "UNCHANGED", "LLM Agent", "High", pattern="emergent_behavior"),
    finding("I-1", "NEW", "User Database", "Low"),
    finding("LLM-1", "NEW", "LLM Agent", "Note", owasp="LLM01:2026"),
    finding("OI-1", "NEW", "Renderer", "Medium", owasp="LLM05:2026"),
    finding("T-9", "NEW", "User Database", "Low", threat="line one\nline two"),
]
# Section 7's rows, as part-files.md orders them: by risk level, Critical first, then in the order the findings appear in Sections 3 and 4
# (the eight tables in order, and S-2 order within each). Written out by hand, so the rule is checked against a result and not against itself.
SECTION_7_ORDER = ["S-2", "R-1", "D-1", "AGP-01", "T-2", "AG-1", "MI-1", "S-1", "E-1", "OI-1", "T-9", "T-10", "I-1", "LLM-2", "TE-1", "LLM-1"]
RESOLVED_FINDINGS = [
    {"id": "I-7", "component": "Legacy Cache", "threat": "Stale entries leak data", "last_risk": "Medium", "reason": "Component removed from the architecture"},
    {"id": "T-5", "component": "Legacy API", "threat": "SQL injection | in a retired endpoint", "last_risk": "High", "reason": "Component 'Legacy API' removed"},
]
ROW_TABLES = [section.key for section in tp.THREATS_MD_SECTIONS if section.keyed == "row"]
ROWS = {"components": 4, "data_flows": 3, "technologies": 2, "trust_zones": 2, "boundary_crossings": 1, "correlated": 1, "patterns": 3, "coverage": 4,
        "gate_requirements": 4, "gate_gaps": 1, "risk_by_layer": 3, "risk_levels": 6, "lifecycle": 5, "baseline_reference": 4}
GAPS = [{"component": "LLM Agent", "missing_category": "model-theft", "resolution": "findings_produced"},
        {"component": "API Gateway", "missing_category": "repudiation", "resolution": "analyzed_clean"}]


def row_values(section, *rows):
    """``{(section, row number, key): value}`` for the rows of a table, each row given in the table's key order."""
    return {(section, number, key): value for number, row in enumerate(rows, 1) for key, value in zip(tp.THREATS_MD_BY_KEY[section].keys, row)}


HOSTILE_ROWS = {}
HOSTILE_ROWS.update(row_values("components", ("API Gateway", "Process", LAYER, "Runs `jobs` | queues <b>&</b> {{x}}\nsecond line ~~~ and ## not a heading")))
HOSTILE_ROWS.update(row_values("data_flows", ("Client", "API Gateway", "### Technologies", "HTTPS")))
HOSTILE_ROWS.update({("technologies", 1, "version"): "**3.12** \\"})
HOSTILE_ROWS.update(row_values("correlated", ("CG-1", "S-2, R-1", "API Gateway", "Spoofing: forged; Repudiation: denied", "Critical")))


def base_world(**changes):
    world = {"findings": copy.deepcopy(OPEN_FINDINGS), "resolved": copy.deepcopy(RESOLVED_FINDINGS), "rows": dict(ROWS), "gaps": [],
             "hostile": dict(HOSTILE_ROWS)}
    world.update(changes)
    return world


def first_run_world(**changes):
    """A run with no baseline: nothing resolved, and no Section 8."""
    world = base_world(resolved=None, rows=dict(ROWS, lifecycle=0, baseline_reference=0))
    world.update(changes)
    return world


def manifest_of(world):
    """The ``tachi.sections/1`` manifest that the orchestrator would write for ``world`` (threat-model-records.md, "The section manifest")."""
    with_baseline = world["resolved"] is not None
    baseline = ({"source": "reports/earlier/threats.md", "date": "2026-11-01", "finding_count": 18, "run_id": BASELINE_RUN_ID} if with_baseline
                else {"source": None, "date": None, "finding_count": None, "run_id": None})
    return {"schema": tp.SECTIONS_SCHEMA,
            "frontmatter": {"date": DATE, "input_format": "mermaid", "classification": "confidential", "run_id": RUN_ID, "baseline": baseline,
                            "coverage_gate": {"status": "pass", "gaps": copy.deepcopy(world["gaps"])}},
            "open": [f["id"] for f in world["findings"]], "resolved": [r["id"] for r in world["resolved"]] if with_baseline else None,
            "rows": dict(world["rows"])}


def balanced_runs(count, size):
    """The contiguous ``(start, stop)`` runs that D3 makes of ``count`` units: at most ``size`` each, differing by at most 1."""
    planned = -(-count // size)
    base, extra = divmod(count, planned)
    runs, at = [], 0
    for number in range(planned):
        take = base + (1 if number < extra else 0)
        runs.append((at, at + take))
        at += take
    return runs


def units_of(manifest):
    """``[(section key, its units, its size)]`` for each table that has a unit, in the template's order, from the manifest alone (item O-beta)."""
    opened = sorted(manifest["open"], key=tp.finding_sort_key)
    resolved = sorted(manifest["resolved"] or [], key=tp.finding_sort_key)
    found = []
    for section in tp.THREATS_MD_SECTIONS:
        if section.keyed == "row":
            units = [{"section": section.key, "row": n} for n in range(1, manifest["rows"][section.key] + 1)]
        else:
            ids = opened if section.keyed == "open" else resolved if section.keyed == "resolved" else [
                v for v in opened if v.partition("-")[0] in section.prefixes]
            units = [{"section": section.key, "finding_id": v} for v in ids]
        if units:
            found.append((section.key, units, section.size))
    return found


def item_for(world, unit):
    """The orchestrator's item for one unit: a row of its table, with the finding's own values or the row's."""
    section = tp.THREATS_MD_BY_KEY[unit["section"]]
    if "row" in unit:
        return {key: world["hostile"].get((section.key, unit["row"], key), "%s %d" % (key, unit["row"])) for key in section.keys}
    records = {tp.canonical_finding_id(r["id"]): r for r in world["findings"] + (world["resolved"] or [])}
    record = records[tp.canonical_finding_id(unit["finding_id"])]
    item = {"finding_id": unit["finding_id"]}
    item.update({key: record[FIELD[key]] for key in section.keys[1:]})
    return item


class Run(object):
    """One synthetic ``threats-md`` run under ``tmp_path``: the section manifest, a stand-in for ``plan --stage threats-md`` and the orchestrator's parts."""

    def __init__(self, tmp_path, world=None, plan_id=PLAN_ID):
        self.tmp = Path(tmp_path)
        self.out = self.tmp / "out"
        self.out.mkdir(parents=True, exist_ok=True)
        self.world = copy.deepcopy(base_world() if world is None else world)
        self.plan_id = plan_id
        self.build = self.out / ".tachi-build"
        self.manifest_path = self.build / "sections.json"
        self.plan_dir = self.build / STAGE / plan_id
        self.doc = None
        self.digest = None

    # ---- the orchestrator's manifest
    def write_manifest(self, manifest=None, raw=None):
        self.build.mkdir(parents=True, exist_ok=True)
        data = raw if raw is not None else json.dumps(manifest_of(self.world) if manifest is None else manifest, indent=2).encode("utf-8")
        self.manifest_path.write_bytes(data)
        return self

    def replace_manifest(self, manifest=None, raw=None):
        """Put another manifest at the fixed path AND in the plan's record of it, so the plan's digests pass and only the manifest's own checks can fail."""
        data = raw if raw is not None else json.dumps(manifest, indent=2).encode("utf-8")
        self.manifest_path.write_bytes(data)
        self.doc["inputs"]["sections"].update({"sha256": tp.sha256_hex(data), "bytes": len(data)})
        return self.write_plan()

    # ---- plan --stage threats-md (T092's; this follows part-files.md's units and sizes)
    def plan(self, shape=None, state="done"):
        raw = self.manifest_path.read_bytes()
        sections = units_of(json.loads(raw.decode("utf-8")))
        if shape is not None:
            sections = shape(sections)
        self.doc = {"schema": tp.PLAN_SCHEMA, "plan_id": self.plan_id, "stage": STAGE, "agent_type": AGENT, "created_utc": "2026-11-22T10:15:00Z",
                    "tachi_version": tp.VERSION, "inputs": {"sections": {"path": str(self.manifest_path), "sha256": tp.sha256_hex(raw), "bytes": len(raw)}},
                    "refs": {}, "architecture_warning": None, "params": {"scoring_date": DATE}, "batch_size": None, "unit_count": 0, "preimage": {},
                    "out_snapshot": None, "retry_budget": {"limit": 0, "used": 0}, "batches": []}
        for _key, units, size in sections:
            for start, stop in balanced_runs(len(units), size):
                chunk = units[start:stop]
                entry = {"batch_id": "B%03d" % (len(self.doc["batches"]) + 1), "parent": None, "attempt": 1,
                         "finding_ids": [u["finding_id"] for u in chunk if "finding_id" in u], "input_sha256": "0" * 64, "state": state}
                self.doc["batches"].append(entry)
                self.write_input(entry, chunk)
        self.doc["unit_count"] = sum(len(units) for _key, units, _size in sections)
        self.doc["retry_budget"]["limit"] = 2 * len(self.doc["batches"])
        return self.write_plan()

    def write_input(self, entry, units):
        body = {"schema": tp.BATCH_INPUT_SCHEMA, "plan_id": self.plan_id, "batch_id": entry["batch_id"], "stage": STAGE, "agent_type": AGENT,
                "finding_ids": list(entry["finding_ids"]), "attempt": entry["attempt"],
                "part_path": tp.part_path(str(self.out), STAGE, self.plan_id, entry["batch_id"], entry["attempt"]),
                "tree_paths": {}, "units": units, "refs": {}, "params": self.doc["params"]}
        tp.validate_batch_input(body)
        text = tp.dump_json(body)
        path = Path(tp.input_path(str(self.out), STAGE, self.plan_id, entry["batch_id"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        entry["input_sha256"] = tp.sha256_hex(text.encode("utf-8"))

    def write_plan(self):
        tp.validate_plan(self.doc)
        self.plan_dir.mkdir(parents=True, exist_ok=True)
        path = self.plan_dir / "plan.json"
        path.write_text(tp.dump_json(self.doc), encoding="utf-8")
        (self.build / STAGE / "current.json").write_text(tp.dump_json({"schema": tp.POINTER_SCHEMA, "plan_id": self.plan_id}), encoding="utf-8")
        self.digest = tp.file_digest(path)
        return self

    def batch_input(self, batch_id):
        return json.loads(Path(tp.input_path(str(self.out), STAGE, self.plan_id, batch_id)).read_text(encoding="utf-8"))

    def entry(self, batch_id):
        return next(e for e in self.doc["batches"] if e["batch_id"] == batch_id)

    def batches_of(self, section):
        """The batch IDs, in plan order, whose units name ``section`` (a halved parent included)."""
        return [e["batch_id"] for e in self.doc["batches"] if self.batch_input(e["batch_id"])["units"][0]["section"] == section]

    def split(self, batch_id):
        """What ``reconcile`` does to a missing batch of two or more units: halve it into ``<id>-1`` and ``<id>-2``, next to the parent, one attempt later."""
        entry = self.entry(batch_id)
        units = self.batch_input(batch_id)["units"]
        middle = (len(units) + 1) // 2
        entry["state"] = "split"
        at = self.doc["batches"].index(entry)
        for offset, (suffix, chunk) in enumerate((("-1", units[:middle]), ("-2", units[middle:]))):
            child = {"batch_id": batch_id + suffix, "parent": batch_id, "attempt": entry["attempt"] + 1,
                     "finding_ids": [u["finding_id"] for u in chunk if "finding_id" in u], "input_sha256": "0" * 64, "state": "done"}
            self.doc["batches"].insert(at + 1 + offset, child)
            self.write_input(child, chunk)
        self.doc["retry_budget"]["used"] += 2
        return self.write_plan()

    # ---- the orchestrator's parts
    def part_for(self, batch_id, canonical=False):
        bi = self.batch_input(batch_id)
        items = [item_for(self.world, unit) for unit in bi["units"]]
        if canonical:
            for item in items:
                if "finding_id" in item:
                    item["finding_id"] = tp.canonical_finding_id(item["finding_id"])
        return {"schema": tp.PART_SCHEMA, "plan_id": self.plan_id, "batch_id": batch_id, "stage": STAGE, "agent_type": AGENT,
                "finding_ids": list(bi["finding_ids"]), "items": items, "fragments": []}

    def part_path(self, batch_id):
        return Path(self.batch_input(batch_id)["part_path"])

    def write_part(self, batch_id, mutate=None, raw=None, canonical=False):
        path = self.part_path(batch_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            path.write_bytes(raw)
            return path
        part = self.part_for(batch_id, canonical)
        if mutate is not None:
            mutate(part)
        path.write_text(json.dumps(part, ensure_ascii=False), encoding="utf-8")
        return path

    def write_parts(self, skip=(), mutate=None, canonical=False):
        for entry in self.doc["batches"]:
            if entry["state"] == "done" and entry["batch_id"] not in skip:
                self.write_part(entry["batch_id"], mutate, canonical=canonical)
        return self

    def ready(self, **plan_options):
        return self.write_manifest().plan(**plan_options).write_parts()

    # ---- the joiner
    def argv(self, digest=None):
        return ["--out", self.out, "--plan", self.plan_id, "--plan-digest", self.digest if digest is None else digest]

    def join(self, joiner, extra=()):
        return invoke(joiner, self.argv() + list(extra), self.tmp)

    @property
    def text(self):
        return (self.out / MD).read_text(encoding="utf-8")

    def record(self):
        return json.loads((self.plan_dir / "stage-record.json").read_text(encoding="utf-8"))

    def earlier(self):
        (self.out / MD).write_bytes(EARLIER)
        return self


@pytest.fixture(scope="module")
def joiner():
    if not RENDERER.is_file():
        pytest.fail("scripts/join-threats-md.py is missing: T106 ships it, and these goldens test it", pytrace=False)
    return _load_hyphenated_script("join_threats_md_under_test", "join-threats-md.py")


@pytest.fixture
def run(tmp_path):
    return Run(tmp_path).ready()


@pytest.fixture
def done(joiner, run):
    """A run that has joined cleanly: the run, and the joined text."""
    res = run.join(joiner)
    assert res.code == 0, res.describe()
    return run


# ---- readers for the tests below (the shared readers, and a plain line reader that does not decode)

def plain(text):
    """What the readers give back for a cell that the file holds as ``text``: ``parse_markdown_table`` strips the bold markers."""
    return text.replace("**", "")


def esc(text):
    """ADR-050 D3's cell sink and the joiner's one extra rule (every ``#`` is ``&#35;``), written out here so that the test doesn't call what it checks."""
    table = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "|": "&#124;", "`": "&#96;", "\n": "&#10;", "#": "&#35;"}
    text = "".join(table.get(char, char) for char in text)
    return re.sub(r"\{(?=\{)|(?<=\{)\{", "&#123;", text)


def row_line(cells):
    return "| " + " | ".join(esc(cell) for cell in cells) + " |"


def header_line(header):
    return "| " + " | ".join(header) + " |"


def separator_line(header):
    return "|" + "|".join("-" * (len(cell) + 2) for cell in header) + "|"


def heading_at(text, heading):
    """The 0-based line of the exact heading line ``heading``, outside code fences (the one shared fence rule)."""
    return tachi_parsers.match_heading(r"^%s[ \t]*$" % re.escape(heading), text, outside_fences=True)


def table_rows(text, heading, escaped_pipes=False):
    """The rows under an exact heading, through the shared reader (decoded, bold stripped)."""
    start = heading_at(text, heading)
    assert start is not None, "no heading line %r" % heading
    return tachi_parsers.parse_markdown_table(text, start_line=start, escaped_pipes=escaped_pipes)


def raw_table(text, heading):
    """``(header line, separator line, [row lines])`` of the first table beneath an exact heading, as written."""
    lines = text.split("\n")
    at = heading_at(text, heading)
    assert at is not None, "no heading line %r" % heading
    index = at + 1
    while index < len(lines) and not lines[index].startswith("|"):
        assert not lines[index].startswith("#"), "no table under %r before the next heading" % heading
        index += 1
    block = []
    while index < len(lines) and lines[index].startswith("|"):
        block.append(lines[index])
        index += 1
    return block[0], block[1], block[2:]


def last_heading(section):
    return section.headings[-1] if section.headings else "#### Risk by MAESTRO Layer"


def expected_cells(world, section, unit):
    """The cells of one row as the file shows them before escaping: the item's values, and Section 7's Category after Status."""
    item = item_for(world, unit)
    cells = [item[key] for key in section.keys]
    if section.key == "actions":
        cells.insert(section.header.index("Category"), CATEGORY_OF[tp.canonical_finding_id(item["finding_id"]).partition("-")[0]])
    return cells


def expected_units(world, key):
    """The units of one table in the order the file shows them: Section 7 by the contract's sort, every other table in plan order."""
    manifest = manifest_of(world)
    units = {name: chunk for name, chunk, _size in units_of(manifest)}.get(key, [])
    if key == "actions":
        by_id = {tp.canonical_finding_id(f["id"]): f for f in world["findings"]}
        units = sorted(units, key=lambda u: (RISK_RANK[by_id[tp.canonical_finding_id(u["finding_id"])]["risk"]],
                                             TABLE_OF[u["finding_id"].partition("-")[0]], tp.finding_sort_key(u["finding_id"])))
    return units


def expected_rows(world, key):
    """What the shared reader must give back for table ``key``: one dict for each row, in file order."""
    section = tp.THREATS_MD_BY_KEY[key]
    return [dict(zip(section.header, [plain(cell) for cell in expected_cells(world, section, unit)])) for unit in expected_units(world, key)]


def new_files(before, after):
    return sorted(set(after) - set(before))


def changed_files(before, after):
    return sorted(path for path in before if path in after and before[path] != after[path])


def assert_failure(res, code, *words):
    assert res.code == code, res.describe()
    assert FAILED in res.err and "Remedy:" in res.err, res.describe()
    for word in words:
        assert word in res.err, "%r is not in the message:\n%s" % (word, res.describe())


# =============================================================================
# 2. Harness checks: no joiner needed
# =============================================================================

def test_harness_the_synthetic_world_is_what_the_contract_describes():
    world = base_world()
    assert len(world["findings"]) == 16 and len({tp.canonical_finding_id(f["id"]) for f in world["findings"]}) == 16
    assert [f["id"] for f in world["findings"]] != sorted((f["id"] for f in world["findings"]), key=tp.finding_sort_key), "the manifest is not in S-2 order"
    assert len(ROW_TABLES) == 14 and sorted(ROWS) == sorted(ROW_TABLES) and sorted(ROWS) == sorted(tp.KEY_SETS["sections-rows"][0])
    by_id = {f["id"]: f for f in world["findings"]}
    ranked = sorted(by_id, key=lambda i: (RISK_RANK[by_id[i]["risk"]], TABLE_OF[i.partition("-")[0]], tp.finding_sort_key(i)))
    assert ranked == SECTION_7_ORDER, "the by-hand order and the rule agree"
    manifest = manifest_of(world)
    assert tp.validate_sections(copy.deepcopy(manifest)) == manifest
    assert tp.validate_sections(copy.deepcopy(manifest_of(first_run_world())))["resolved"] is None


def test_harness_the_stand_in_plan_validates_and_every_part_it_lists_validates(run):
    tp.validate_plan(copy.deepcopy(run.doc))
    assert run.doc["unit_count"] == 77 == sum(len(units) for _key, units, _size in units_of(manifest_of(run.world)))
    # one part for each of the 8 finding tables, Section 7, Section 4c and the 14 row tables: every table of this world has rows and fits its size
    assert len(run.doc["batches"]) == 24 == 8 + 1 + 1 + len(ROW_TABLES)
    assert run.doc["batch_size"] is None and run.doc["refs"] == {} and run.doc["out_snapshot"] is None
    for entry in run.doc["batches"]:
        bi = run.batch_input(entry["batch_id"])
        result = tp.read_part(str(run.part_path(entry["batch_id"])), str(run.out), PLAN_ID, entry["batch_id"], STAGE, AGENT, entry["finding_ids"], bi["units"])
        assert result.state == "done", (entry["batch_id"], result.state, result.detail)


def test_harness_a_halved_batch_sits_next_to_its_parent_with_the_next_attempt(run):
    components = run.batches_of("components")
    assert len(components) == 1
    run.split(components[0])
    assert [e["batch_id"] for e in run.doc["batches"][:3]] == [components[0], components[0] + "-1", components[0] + "-2"]
    assert [e["state"] for e in run.doc["batches"][:3]] == ["split", "done", "done"] and run.doc["batches"][1]["attempt"] == 2
    assert [u["row"] for u in run.batch_input(components[0] + "-1")["units"]] == [1, 2]
    assert [u["row"] for u in run.batch_input(components[0] + "-2")["units"]] == [3, 4]


def test_harness_the_golden_constants_are_the_headers_of_the_contract(tmp_path):
    stride, ai = tp.THREATS_MD_BY_KEY["spoofing"].header, tp.THREATS_MD_BY_KEY["agentic"].header
    assert (STRIDE_ROW, STRIDE_SEPARATOR) == (header_line(stride), separator_line(stride))
    assert (AI_ROW, AI_SEPARATOR) == (header_line(ai), separator_line(ai))
    lines = GOLDEN.split("\n")
    for key in ("components", "data_flows", "technologies", "trust_zones", "boundary_crossings", "correlated", "coverage", "gate_requirements", "risk_by_layer",
                "risk_levels", "actions"):
        header = tp.THREATS_MD_BY_KEY[key].header
        assert header_line(header) in lines and separator_line(header) in lines, key
    run = golden_run(tmp_path)
    assert run.doc["unit_count"] == 2 + 1 + 1 + 1 + 1 + 1 + 2 + 2 + 2 + 6 + 2 and tp.validate_sections(manifest_of(run.world))["resolved"] is None


def test_harness_the_parts_follow_the_templates_sizes(tmp_path):
    world = base_world(rows=dict(ROWS, data_flows=130, correlated=30, risk_levels=59))
    run = Run(tmp_path, world).write_manifest().plan()
    assert len(run.batches_of("data_flows")) == 3 and len(run.batches_of("correlated")) == 2 and len(run.batches_of("risk_levels")) == 1
    assert [len(run.batch_input(b)["units"]) for b in run.batches_of("data_flows")] == [44, 43, 43]
    assert [len(run.batch_input(b)["units"]) for b in run.batches_of("correlated")] == [15, 15]


# =============================================================================
# 3. The CLI and the exit table
# =============================================================================

def test_cli_help_and_version_are_supported(joiner, tmp_path):
    helped = invoke(joiner, ["--help"], tmp_path)
    assert helped.code == 0 and all(flag in helped.out for flag in ("--out", "--plan", "--plan-digest")), helped.describe()
    versioned = invoke(joiner, ["--version"], tmp_path)
    assert versioned.code == 0, versioned.describe()
    assert tp.VERSION in versioned.out + versioned.err and RENDERER_NAME in versioned.out + versioned.err  # reading: cli.md says tests may accept either stream
    assert "%d.%d" % sys.version_info[:2] in versioned.out + versioned.err, "the interpreter's version too"


@pytest.mark.parametrize("argv", [[], ["--out", "x"], ["--out", "x", "--plan", PLAN_ID], ["--plan", PLAN_ID, "--plan-digest", "a" * 64]],
                         ids=["no-arguments", "no-plan", "no-digest", "no-out"])
def test_cli_a_missing_required_argument_is_a_usage_error(joiner, tmp_path, argv):
    assert invoke(joiner, argv, tmp_path).code == 2


def test_cli_an_out_that_is_no_directory_is_exit_1(joiner, tmp_path):
    res = invoke(joiner, ["--out", tmp_path / "missing", "--plan", PLAN_ID, "--plan-digest", "a" * 64], tmp_path)
    assert_failure(res, 1, "--out is not a directory", "create it or correct --out")


@pytest.mark.parametrize("plan_id", ["../" + PLAN_ID, PLAN_ID.upper(), PLAN_ID + "\n", "latest", PLAN_ID[:-1], ""],
                         ids=["traversal", "uppercase", "newline", "word", "short", "empty"])
def test_cli_a_plan_id_off_the_allow_list_is_exit_2_before_anything_is_read(joiner, tmp_path, plan_id):
    res = invoke(joiner, ["--out", tmp_path, "--plan", plan_id, "--plan-digest", "a" * 64], tmp_path)
    assert_failure(res, 2, "--plan is not a plan ID")
    assert not (tmp_path / ".tachi-build").exists()


@pytest.mark.parametrize("digest", ["A" * 64, "a" * 63, "a" * 65, "g" * 64, "a" * 64 + "\n", ""], ids=["uppercase", "short", "long", "not-hex", "newline", "empty"])
def test_cli_a_digest_that_is_not_lowercase_hex_is_exit_2(joiner, tmp_path, digest):
    res = invoke(joiner, ["--out", tmp_path, "--plan", PLAN_ID, "--plan-digest", digest], tmp_path)
    assert_failure(res, 2, "--plan-digest is not a SHA-256")


def test_cli_the_directory_check_comes_before_the_plan_checks(joiner, tmp_path):
    res = invoke(joiner, ["--out", tmp_path / "missing", "--plan", "nonsense", "--plan-digest", "nonsense"], tmp_path)
    assert res.code == 1, res.describe()


def test_cli_the_work_is_in_main_argv_none_returning_int_behind_a_thin_main_guard_and_the_stamps_name_is_a_literal(joiner):
    """H15: the gated tests count only what runs in-process, so the entry keeps its work in ``main(argv=None) -> int`` and the guard only exits."""
    tree = ast.parse(RENDERER.read_text(encoding="utf-8"))
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    assert [arg.arg for arg in main.args.args] == ["argv"] and [ast.unparse(default) for default in main.args.defaults] == ["None"]
    assert ast.unparse(main.returns) == "int"
    guard = tree.body[-1]
    assert isinstance(guard, ast.If) and ast.unparse(guard.test) == "__name__ == '__main__'"
    assert len(guard.body) == 1 and isinstance(guard.body[0], ast.Raise) and ast.unparse(guard.body[0]) == "raise SystemExit(main())"
    assert joiner.RENDERER == RENDERER_NAME and joiner.STAGE == STAGE


def test_cli_a_plan_that_does_not_exist_is_exit_1(joiner, tmp_path):
    run = Run(tmp_path).write_manifest()
    res = invoke(joiner, ["--out", run.out, "--plan", PLAN_ID, "--plan-digest", "a" * 64], tmp_path)
    assert_failure(res, 1, "plan pointer")


def test_cli_a_missing_plan_file_is_exit_1(joiner, run):
    (run.plan_dir / "plan.json").unlink()
    assert_failure(run.join(joiner), 1, "plan.json is missing")


def test_cli_a_missing_manifest_is_exit_1(joiner, run):
    run.manifest_path.unlink()
    assert_failure(run.join(joiner), 1, "section manifest")


def test_cli_the_wrong_digest_is_exit_2_and_names_the_plan_directory(joiner, run):
    res = run.join(joiner, [])  # a good run first, so the failure below is the digest's alone
    assert res.code == 0, res.describe()
    wrong = invoke(joiner, run.argv(digest="0" * 64), run.tmp)
    assert_failure(wrong, 2, "digest differs", "Kept for diagnosis: %s" % run.plan_dir)


def test_cli_a_plan_that_was_edited_after_plan_is_exit_2(joiner, run):
    stale = run.digest
    run.doc["retry_budget"]["limit"] += 1
    run.write_plan()
    assert run.digest != stale
    assert_failure(invoke(joiner, run.argv(digest=stale), run.tmp), 2, "digest differs")


def test_cli_a_pointer_that_names_another_plan_is_exit_2(joiner, run):
    (run.build / STAGE / "current.json").write_text(tp.dump_json({"schema": tp.POINTER_SCHEMA, "plan_id": OTHER_PLAN_ID}), encoding="utf-8")
    assert_failure(run.join(joiner), 2, "disagrees with current.json")


@pytest.mark.parametrize("state", ["pending", "failed"])
def test_cli_a_batch_that_is_not_done_is_exit_2_and_names_it(joiner, tmp_path, state):
    run = Run(tmp_path).write_manifest().plan()
    run.doc["batches"][2]["state"] = state
    run.write_plan().write_parts(skip=("B003",))
    res = run.join(joiner)
    assert_failure(res, 2, "B003", "not complete")
    assert not (run.out / MD).exists()


def test_cli_no_exit_3_and_no_exit_5_exist(joiner):
    source = RENDERER.read_text(encoding="utf-8")
    assert "return 3" not in source and "return 5" not in source and "exit(3" not in source and "exit(5" not in source


# =============================================================================
# 4. A clean run: what it writes and what it leaves alone
# =============================================================================

def test_run_a_clean_run_exits_0_and_writes_threats_md_and_the_stage_record_and_nothing_else(joiner, run):
    before = tree_state(run.tmp)
    res = run.join(joiner)
    assert res.code == 0 and res.err == "", res.describe()
    after = tree_state(run.tmp)
    assert new_files(before, after) == sorted(["out/" + MD, "out/.tachi-build/%s/%s/stage-record.json" % (STAGE, PLAN_ID)])
    assert changed_files(before, after) == [], "the plan, its inputs, its parts and the manifest are never rewritten"
    assert not any("/staged/" in path for path in after), "the staged file moved onto its name"


def test_run_stdout_is_one_json_object_with_the_records_path_and_counts(joiner, run):
    res = run.join(joiner)
    printed = json.loads(res.out)  # reading: cli.md names no key set for the joiner, so {record, counts}
    assert isinstance(printed, dict) and set(printed) == {"record", "counts"}
    assert printed["record"] == str(run.plan_dir / "stage-record.json") and printed["counts"] == run.record()["counts"]


def test_run_the_stage_record_is_a_valid_success_record_with_the_four_counts(joiner, run):
    assert run.join(joiner).code == 0
    record = run.record()
    tp.validate_stage_record(record)
    assert record["status"] == "success" and record["stage"] == STAGE and record["plan_id"] == PLAN_ID and record["tachi_version"] == tp.VERSION
    assert record["counts"] == {"units": 77, "open": 16, "resolved": 2, "rendered": 77}
    assert record["warnings"] == [] and record["undeclared_paths"] == [] and record["error"] is None
    assert record["outputs"] == [{"path": MD, "sha256": sha256_of(run.out / MD)}]
    assert record["batches"] == {"planned": 24, "dispatched": 24, "done": 24, "retried": 0, "split": 0, "exhausted": 0}
    assert record["overflow_events"] == [] and record["retries"] == []
    assert record["started_utc"] == run.doc["created_utc"] and record["input_digest"] == tp.read_stamp(run.text)["input_digest"]


def test_run_a_halved_batch_shows_in_the_record_as_a_retry(joiner, run):
    parent = run.batches_of("actions")[0]
    run.split(parent).write_parts()
    run.write_part(parent, raw=b"not json")  # the parent's own part, at attempt 1: never read, because the parent is split
    assert run.join(joiner).code == 0
    record = run.record()
    tp.validate_stage_record(record)
    # 24 planned parents; the halving is 2 retries, and it replaces one done batch with two
    assert record["batches"] == {"planned": 24, "dispatched": 26, "done": 25, "retried": 2, "split": 1, "exhausted": 0}
    assert [r["children"] for r in record["retries"]] == [[parent + "-1", parent + "-2"]]
    assert record["counts"]["units"] == 77 and record["counts"]["rendered"] == 77


def test_run_an_earlier_threats_md_is_replaced_and_a_second_run_is_byte_identical(joiner, run):
    run.earlier()
    assert run.join(joiner).code == 0
    first = (run.out / MD).read_bytes()
    assert first != EARLIER
    assert run.join(joiner).code == 0
    assert (run.out / MD).read_bytes() == first
    assert run.record()["status"] == "success"


def test_run_it_writes_nothing_outside_out_and_leaves_no_bytecode(joiner, run):
    before = tree_state(SCRIPTS_DIR)
    assert run.join(joiner).code == 0
    assert tree_state(SCRIPTS_DIR) == before
    assert sorted(p.name for p in run.tmp.iterdir()) == ["out"]


def test_run_it_never_writes_phase_3_5s_record_the_populators_block_or_the_two_body_lines(done):
    text = done.text
    for forbidden in ("**Attack chain outcome**", "## Attack Chain Outcome", "## Affected Assets", "**Architecture source**", "**ID high-water mark**"):
        assert forbidden not in text, forbidden
    assert sorted(p.name for p in done.out.iterdir()) == [".tachi-build", MD], "no attack-chains.md, no SARIF, no report"


def test_run_the_file_is_clean_utf8_with_unix_line_ends_and_one_final_newline(done):
    raw = (done.out / MD).read_bytes()
    text = raw.decode("utf-8")
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n") and "\r" not in text and not raw.startswith(b"\xef\xbb\xbf")
    assert tp.forbidden_character(text) is None


def test_run_it_keeps_the_mode_of_the_file_it_replaces(joiner, run):
    run.earlier()
    os.chmod(str(run.out / MD), 0o640)
    assert run.join(joiner).code == 0
    assert (run.out / MD).stat().st_mode & 0o777 == 0o640


# =============================================================================
# 5. The layout: the frontmatter, the golden, the notes and the conditional sections
# =============================================================================

def test_layout_the_frontmatter_has_the_templates_shape_with_a_baseline_and_gaps(joiner, tmp_path):
    run = Run(tmp_path, base_world(gaps=GAPS)).ready()
    assert run.join(joiner).code == 0
    head = run.text.split("\n---\n", 1)[0] + "\n---"
    assert head == "\n".join([
        "---", 'schema_version: "1.4"', 'date: "2026-11-22"', 'input_format: "mermaid"', 'classification: "confidential"', 'run_id: "2026-11-22T10-15-00"',
        "baseline:", '  source: "reports/earlier/threats.md"', '  date: "2026-11-01"', "  finding_count: 18", '  run_id: "2026-11-01T10-00-00"',
        "coverage_gate:", '  status: "pass"', "  gaps:",
        '    - { component: "LLM Agent", missing_category: "model-theft", resolution: "findings_produced" }',
        '    - { component: "API Gateway", missing_category: "repudiation", resolution: "analyzed_clean" }', "---"])
    assert run.text.startswith("---\n"), "the output begins with its frontmatter (output-schemas.md)"
    assert tachi_parsers.parse_frontmatter(run.text) == {"date": DATE, "classification": "confidential", "schema_version": "1.4"}
    assert tachi_parsers.parse_baseline_frontmatter(run.text) == {"has_baseline": True, "source": "reports/earlier/threats.md", "date": "2026-11-01",
                                                                   "finding_count": "18", "run_id": BASELINE_RUN_ID}


def test_layout_a_first_run_has_null_baseline_values_and_no_section_8_and_no_section_4c(joiner, tmp_path):
    run = Run(tmp_path, first_run_world()).ready()
    assert run.join(joiner).code == 0
    text = run.text
    assert "baseline:\n  source: null\n  date: null\n  finding_count: null\n  run_id: null\ncoverage_gate:\n  status: \"pass\"\n  gaps: []\n---\n" in text
    assert tachi_parsers.parse_baseline_frontmatter(text)["has_baseline"] is False
    for absent in ("## 4c. Resolved Findings", "## 8. Delta Summary", "### Finding Lifecycle", "### Baseline Reference", NOTE_NO_RESOLVED):
        assert absent not in text, absent
    assert tachi_parsers.parse_reference_set(text)["resolved"] == []


def test_layout_the_title_follows_the_frontmatter_and_the_carrier_lines_have_their_place(done):
    text = done.text
    begin, stop = sc.architecture_source_region(text)
    assert text[begin:stop].strip() == "# Threat Model Report", "the body lines of FR-E.18 and ruling B go between the frontmatter and the first ## heading"
    assert sc.find_architecture_source_lines(text) == [] and tachi_parsers.parse_project_name(text) == "Unknown Project"


GOLDEN_FINDINGS = [
    finding("S-1", "NEW", "API Gateway", "Critical", threat="Forged tokens", mitigation="Rotate keys"),
    finding("AGP-01", "NEW", "Fine-Tuning Pipeline", "High", pattern="temporal_attack", owasp="ASI-06", layer="L2 " + EM + " Data Operations",
            threat="Poisoned training data", mitigation="Attest provenance"),
]
GOLDEN_ROWS = {name: 0 for name in ROW_TABLES}
GOLDEN_ROWS.update(components=2, data_flows=1, technologies=1, trust_zones=1, coverage=2, gate_requirements=2, risk_by_layer=2, risk_levels=6)
GOLDEN_HOSTILE = {}
GOLDEN_HOSTILE.update(row_values("components", ("API Gateway", "Process", LAYER, "Routes requests"),
                                 ("Fine-Tuning Pipeline", "Process", "L2 " + EM + " Data Operations", "Trains models")))
GOLDEN_HOSTILE.update(row_values("data_flows", ("Client", "API Gateway", "Requests", "HTTPS")))
GOLDEN_HOSTILE.update(row_values("technologies", ("Runtime", "Python", "3.12")))
GOLDEN_HOSTILE.update(row_values("trust_zones", ("DMZ", "Semi-trusted", "API Gateway")))
GOLDEN_HOSTILE.update(row_values("coverage", ("API Gateway", "1", EM, EM, EM, EM, EM, "n/a", "n/a", "1"),
                                 ("Fine-Tuning Pipeline", EM, EM, EM, EM, EM, EM, "1", "n/a", "1")))
GOLDEN_HOSTILE.update(row_values("gate_requirements", ("API Gateway", "process", "S, T, R, I, D, E", "6 / 6", "None"),
                                 ("Fine-Tuning Pipeline", "llm_process", "S, T, R, I, D, E, AG", "7 / 7", "None")))
GOLDEN_HOSTILE.update(row_values("risk_by_layer", (LAYER, "1", "Critical"), ("L2 " + EM + " Data Operations", "1", "High")))
GOLDEN_HOSTILE.update(row_values("risk_levels", ("Critical", "1", "50.0%"), ("High", "1", "50.0%"), ("Medium", "0", "0.0%"), ("Low", "0", "0.0%"),
                                 ("Note", "0", "0.0%"), ("**Total**", "**2**", "**100%**")))

STRIDE_ROW = "| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |"
STRIDE_SEPARATOR = "|----|--------|-----------|---------------|--------|------------|--------|------------|------------|"
AI_ROW = "| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |"
AI_SEPARATOR = "|----|--------|-----------|---------------|--------|-----------------|------------|--------|------------|------------|"
GOLDEN = "\n".join(["""---
schema_version: "1.4"
date: "2026-11-22"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-11-22T10-15-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model Report

## 1. System Overview

### Components

| Component | Type | MAESTRO Layer | Description |
|-----------|------|---------------|-------------|
| API Gateway | Process | L4 \u2014 Deployment Infrastructure | Routes requests |
| Fine-Tuning Pipeline | Process | L2 \u2014 Data Operations | Trains models |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Client | API Gateway | Requests | HTTPS |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Runtime | Python | 3.12 |

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| DMZ | Semi-trusted | API Gateway |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|

## 3. STRIDE Tables

**ID prefix convention:**

| Prefix | Category |
|--------|----------|
| S | Spoofing |
| T | Tampering |
| R | Repudiation |
| I | Information Disclosure |
| D | Denial of Service |
| E | Elevation of Privilege |

**Risk level computation (OWASP 3x3 matrix):**

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

### 3.1 Spoofing (S)
""",
    STRIDE_ROW, STRIDE_SEPARATOR, "| S-1 | NEW | API Gateway | L4 \u2014 Deployment Infrastructure | Forged tokens | HIGH | HIGH | Critical | Rotate keys |",
    "\n### 3.2 Tampering (T)\n", STRIDE_ROW, STRIDE_SEPARATOR,
    "\n### 3.3 Repudiation (R)\n", STRIDE_ROW, STRIDE_SEPARATOR,
    "\n### 3.4 Information Disclosure (I)\n", STRIDE_ROW, STRIDE_SEPARATOR,
    "\n### 3.5 Denial of Service (D)\n", STRIDE_ROW, STRIDE_SEPARATOR,
    "\n### 3.6 Elevation of Privilege (E)\n", STRIDE_ROW, STRIDE_SEPARATOR,
    """
## 4. AI Threat Tables

**ID prefix convention:**

| Prefix | Category |
|--------|----------|
| AG | Agentic Threats |
| LLM | LLM Threats |

### 4.1 Agentic Threats (AG)
""", AI_ROW, AI_SEPARATOR,
    "| AGP-01 | NEW | Fine-Tuning Pipeline | L2 \u2014 Data Operations | Poisoned training data | ASI-06 | MEDIUM | HIGH | High | Attest provenance |",
    "\n### 4.2 LLM Threats (LLM)\n", AI_ROW, AI_SEPARATOR,
    """
## 4a. Correlated Findings

> No cross-agent correlations detected.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| API Gateway | 1 | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | n/a | n/a | 1 |
| Fine-Tuning Pipeline | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | 1 | n/a | 1 |

## 5a. Coverage Gate Results

Coverage gate passed \u2014 all required threat categories evaluated for every component.

### Coverage Requirements Matrix

| Component | Determined Type | Required Categories | Evaluated | Gaps |
|-----------|-----------------|---------------------|-----------|------|
| API Gateway | process | S, T, R, I, D, E | 6 / 6 | None |
| Fine-Tuning Pipeline | llm_process | S, T, R, I, D, E, AG | 7 / 7 | None |

## 6. Risk Summary

### Risk Calibration Matrix

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L4 \u2014 Deployment Infrastructure | 1 | Critical |
| L2 \u2014 Data Operations | 1 | High |

Risk summary counts below reflect deduplicated findings. When correlation groups exist, correlated findings count as one unique threat per group rather than individually.

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 1 | 50.0% |
| High | 1 | 50.0% |
| Medium | 0 | 0.0% |
| Low | 0 | 0.0% |
| Note | 0 | 0.0% |
| **Total** | **2** | **100%** |

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| S-1 | NEW | Spoofing | \u2014 | API Gateway | L4 \u2014 Deployment Infrastructure | Forged tokens | Critical | Rotate keys |
| AGP-01 | NEW | Agentic | temporal_attack | Fine-Tuning Pipeline | L2 \u2014 Data Operations | Poisoned training data | High | Attest provenance |
"""])


def golden_run(tmp_path):
    world = {"findings": copy.deepcopy(GOLDEN_FINDINGS), "resolved": None, "rows": dict(GOLDEN_ROWS), "gaps": [], "hostile": dict(GOLDEN_HOSTILE)}
    return Run(tmp_path, world).ready()


def test_layout_the_golden_the_whole_file_of_a_small_first_run(joiner, tmp_path):
    run = golden_run(tmp_path)
    assert run.join(joiner).code == 0
    stamp = tp.stamp_comment(RENDERER_NAME, run.record()["input_digest"])
    assert run.text == GOLDEN + "\n" + stamp + "\n"


def test_layout_every_line_is_a_heading_a_row_frontmatter_a_fixed_label_or_a_note_and_nothing_is_prose(done):
    lines = done.text.split("\n")
    closing = lines.index("---", 1)
    allowed = set(NOTES) | {PREFIX_LABEL, MATRIX_LABEL, "# Threat Model Report", ""}
    stray = [line for line in lines[closing + 1:-2] if not line.startswith(("|", "#")) and line not in allowed]
    assert stray == []
    assert lines[-1] == "" and lines[-2].startswith("<!-- tachi-provenance:") and lines[-3] == ""


def test_layout_a_row_has_a_space_on_each_side_of_every_delimiter(done):
    fixed = set(MATRIX) | set(STRIDE_PREFIXES) | set(AI_PREFIXES)
    seen = 0
    for line in done.text.split("\n"):
        if line.startswith("|") and not separator_row(line) and line not in fixed:
            assert re.fullmatch(r"\| .+ \|", line), line
            assert all("|" not in cell for cell in line[2:-2].split(" | ")), "a raw pipe inside a cell: %r" % line
            seen += 1
    assert seen > 100


def test_layout_the_fixed_tables_and_labels_are_the_templates(done):
    text = done.text
    stride = text.split("## 3. STRIDE Tables\n\n", 1)[1].split("\n### 3.1", 1)[0]
    assert stride == "\n".join([PREFIX_LABEL, ""] + STRIDE_PREFIXES + ["", MATRIX_LABEL, ""] + MATRIX + [""])
    ai = text.split("## 4. AI Threat Tables\n\n", 1)[1].split("\n### 4.1", 1)[0]
    assert ai == "\n".join([PREFIX_LABEL, ""] + AI_PREFIXES + [""])
    risk = text.split("## 6. Risk Summary\n\n", 1)[1].split("\n#### Risk by MAESTRO Layer", 1)[0]
    assert risk == "\n".join(["### Risk Calibration Matrix", ""] + MATRIX + [""])
    template = TEMPLATE.read_text(encoding="utf-8")
    for line in MATRIX + STRIDE_PREFIXES + AI_PREFIXES + [PREFIX_LABEL, MATRIX_LABEL, SECTION_6_SENTENCE, NOTE_NO_CORRELATIONS,
                                                           "Coverage gate passed " + EM + " all required threat categories evaluated for every component."]:
        assert line in template, "the template has no line %r" % line


def test_layout_section_2s_note_is_the_sentence_the_references_use():
    """The contract says in which state Section 2 carries a note and not in what words. These are the repo's: trust-boundaries.md tells the orchestrator to write
    them, and the threat-report agent's narrative template looks for that note by them, so a change to either reference shows here, and the next test holds the
    joiner to the same constant."""
    wanted = NOTE_NO_BOUNDARIES.rstrip(".")
    assert wanted in TRUST_BOUNDARIES_REFERENCE.read_text(encoding="utf-8")
    assert wanted in NARRATIVE_TEMPLATES.read_text(encoding="utf-8")


def test_layout_section_2s_note_stands_only_when_both_of_its_tables_are_empty(joiner, tmp_path):
    for rows, expected in (({"trust_zones": 0, "boundary_crossings": 0}, True), ({"trust_zones": 1, "boundary_crossings": 0}, False),
                           ({"trust_zones": 0, "boundary_crossings": 1}, False)):
        run = Run(tmp_path / ("%d%d" % (rows["trust_zones"], rows["boundary_crossings"])), base_world(rows=dict(ROWS, **rows))).ready()
        assert run.join(joiner).code == 0
        assert (NOTE_NO_BOUNDARIES in run.text) is expected, rows
        for heading in ("### Trust Zones", "### Boundary Crossings"):
            assert heading_at(run.text, heading) is not None, "the section keeps its headers: the section is never omitted"


def test_layout_section_4s_note_stands_only_when_both_ai_tables_are_empty(joiner, tmp_path):
    stride_only = [f for f in OPEN_FINDINGS if f["id"].partition("-")[0] in ("S", "T", "R", "I", "D", "E")]
    for name, findings, expected in (("none", stride_only, True), ("agentic", stride_only + [f for f in OPEN_FINDINGS if f["id"] == "AG-1"], False),
                                     ("llm", stride_only + [f for f in OPEN_FINDINGS if f["id"] == "OI-1"], False)):
        run = Run(tmp_path / name, base_world(findings=copy.deepcopy(findings))).ready()
        assert run.join(joiner).code == 0
        assert (NOTE_NO_AI in run.text) is expected, name
        assert heading_at(run.text, "### 4.1 Agentic Threats (AG)") is not None and heading_at(run.text, "### 4.2 LLM Threats (LLM)") is not None
        assert (raw_table(run.text, "### 4.1 Agentic Threats (AG)")[2] == []) is (name != "agentic"), name


def test_layout_section_4a_has_its_note_when_empty_and_the_matrix_footnote_when_it_has_rows(joiner, tmp_path):
    for correlated, note, footnote in ((0, True, False), (1, False, True)):
        run = Run(tmp_path / str(correlated), base_world(rows=dict(ROWS, correlated=correlated))).ready()
        assert run.join(joiner).code == 0
        assert (NOTE_NO_CORRELATIONS in run.text.split("\n")) is note and (NOTE_FOOTNOTE in run.text.split("\n")) is footnote
        assert len(raw_table(run.text, "## 4a. Correlated Findings")[2]) == correlated
    groups = tachi_parsers.parse_correlation_groups(run.text, member_ids=[f["id"] for f in OPEN_FINDINGS])
    assert [(g["group_id"], g["members"]) for g in groups["groups"]] == [("CG-1", ["S-2", "R-1"])] and groups["errors"] == []
    lines = run.text.split("\n")
    assert lines[lines.index(NOTE_FOOTNOTE) - 2].startswith("|"), "the footnote follows the coverage matrix"
    assert lines.index(NOTE_FOOTNOTE) < lines.index("## 5a. Coverage Gate Results")


def test_layout_section_4c_and_section_8_follow_the_baseline(joiner, tmp_path):
    for name, world, note in (("some", base_world(), False), ("none", base_world(resolved=[], rows=dict(ROWS)), True)):
        run = Run(tmp_path / name, world).ready()
        assert run.join(joiner).code == 0
        assert (NOTE_NO_RESOLVED in run.text.split("\n")) is note
        header, _separator, rows = raw_table(run.text, "## 4c. Resolved Findings")
        assert header == header_line(("ID", "Component", "Threat", "Last Risk Level", "Resolution Reason")) and len(rows) == (0 if note else 2)
        for heading in ("## 8. Delta Summary", "### Finding Lifecycle", "### Baseline Reference"):
            assert heading_at(run.text, heading) is not None


def test_layout_section_8_with_a_baseline_and_no_rows_keeps_its_headers(joiner, tmp_path):
    run = Run(tmp_path, base_world(rows=dict(ROWS, lifecycle=0, baseline_reference=0))).ready()
    assert run.join(joiner).code == 0
    assert raw_table(run.text, "### Finding Lifecycle")[2] == [] and raw_table(run.text, "### Baseline Reference")[2] == []


def test_layout_section_4b_and_the_gap_details_only_when_they_have_rows(joiner, tmp_path):
    for name, rows, present in (("rows", {"patterns": 3, "gate_gaps": 1}, True), ("none", {"patterns": 0, "gate_gaps": 0}, False)):
        run = Run(tmp_path / name, base_world(rows=dict(ROWS, **rows))).ready()
        assert run.join(joiner).code == 0
        assert (heading_at(run.text, "## 4b. Findings by Agentic Pattern") is not None) is present
        assert (heading_at(run.text, "### Gap Resolution Details") is not None) is present
        assert (NOTE_GATE_PASSED in run.text.split("\n")) is (not present), "the gate's pass note stands only when there is no gap"


def test_layout_every_conditional_heading_comes_once_or_not_at_all(joiner, tmp_path):
    run = Run(tmp_path, first_run_world(rows=dict(ROWS, lifecycle=0, baseline_reference=0, patterns=0, gate_gaps=0))).ready()
    assert run.join(joiner).code == 0
    headings = [line for line in run.text.split("\n") if line.startswith("#")]
    assert len(headings) == len(set(headings)), "no heading twice"


# =============================================================================
# 6. Order: sections, rows, Section 7's sort, the manifest's spelling, halved batches and NFR-2
# =============================================================================

def test_order_the_sections_come_in_the_templates_order(done):
    headings = [line for line in done.text.split("\n") if line.startswith("#")]
    wanted = ["# Threat Model Report", "## 1. System Overview", "### Components", "### Data Flows", "### Technologies", "## 2. Trust Boundaries", "### Trust Zones",
              "### Boundary Crossings", "## 3. STRIDE Tables", "### 3.1 Spoofing (S)", "### 3.2 Tampering (T)", "### 3.3 Repudiation (R)",
              "### 3.4 Information Disclosure (I)", "### 3.5 Denial of Service (D)", "### 3.6 Elevation of Privilege (E)", "## 4. AI Threat Tables",
              "### 4.1 Agentic Threats (AG)", "### 4.2 LLM Threats (LLM)", "## 4a. Correlated Findings", "## 4b. Findings by Agentic Pattern",
              "## 4c. Resolved Findings", "## 5. Coverage Matrix", "## 5a. Coverage Gate Results", "### Coverage Requirements Matrix", "### Gap Resolution Details",
              "## 6. Risk Summary", "### Risk Calibration Matrix", "#### Risk by MAESTRO Layer", "## 7. Recommended Actions", "## 8. Delta Summary",
              "### Finding Lifecycle", "### Baseline Reference"]
    assert headings == wanted


@pytest.mark.parametrize("key", [section.key for section in tp.THREATS_MD_SECTIONS])
def test_order_every_table_reads_back_as_its_items_in_the_orders_of_the_contract(done, key):
    section = tp.THREATS_MD_BY_KEY[key]
    rows = table_rows(done.text, last_heading(section), escaped_pipes=(key == "actions")) if key != "risk_levels" else None
    if key == "risk_levels":
        start = done.text.split("\n").index(SECTION_6_SENTENCE)
        rows = tachi_parsers.parse_markdown_table(done.text, start_line=start)
    assert rows == expected_rows(done.world, key)


def test_order_a_finding_table_is_in_s2_order_with_ids_as_the_manifest_spells_them(done):
    ids = {key: [row[tp.THREATS_MD_BY_KEY[key].header[0]] for row in table_rows(done.text, last_heading(tp.THREATS_MD_BY_KEY[key]))]
           for key in ("spoofing", "tampering", "agentic", "llm", "resolved")}
    assert ids == {"spoofing": ["S-1", "S-2"], "tampering": ["T-2", "T-9", "T-10"], "agentic": ["AG-1", "AGP-01", "TE-1"],
                   "llm": ["LLM-1", "LLM-2", "OI-1", "MI-1"], "resolved": ["T-5", "I-7"]}


def test_order_section_7_is_sorted_by_risk_then_by_the_order_of_sections_3_and_4(done):
    rows = table_rows(done.text, "## 7. Recommended Actions", escaped_pipes=True)
    assert [row["Finding ID"] for row in rows] == SECTION_7_ORDER
    assert [row["Category"] for row in rows[:5]] == ["Spoofing", "Repudiation", "Denial of Service", "Agentic", "Tampering"]
    assert {row["Finding ID"]: row["Category"] for row in rows} == {
        "S-1": "Spoofing", "S-2": "Spoofing", "T-2": "Tampering", "T-9": "Tampering", "T-10": "Tampering", "R-1": "Repudiation", "I-1": "Information Disclosure",
        "D-1": "Denial of Service", "E-1": "Elevation of Privilege", "AG-1": "Agentic", "AGP-01": "Agentic", "TE-1": "Agentic", "LLM-1": "LLM", "LLM-2": "LLM",
        "OI-1": "LLM", "MI-1": "LLM"}


def test_order_ids_keep_the_manifests_spelling_even_when_the_part_writes_the_canonical_one(joiner, tmp_path):
    run = Run(tmp_path).write_manifest().plan().write_parts(canonical=True)
    assert run.join(joiner).code == 0
    text = run.text
    assert "| AGP-01 | NEW | Agentic |" in text and "AGP-1 " not in text and "| AGP-1 |" not in text
    assert [f["id"] for f in tachi_parsers.parse_reference_set(text)["open"] if f["id"].startswith("AGP")] == ["AGP-01"]


def test_order_a_finding_listed_by_its_canonical_spelling_in_the_manifest_is_written_so(joiner, tmp_path):
    findings = copy.deepcopy(OPEN_FINDINGS)
    for record in findings:
        if record["id"] == "AGP-01":
            record["id"] = "AGP-1"
    run = Run(tmp_path, base_world(findings=findings)).ready()
    assert run.join(joiner).code == 0
    assert "| AGP-1 | NEW | Agentic |" in run.text and "| AGP-1 | NEW | Fine-Tuning Pipeline |" in run.text and "| AGP-01 |" not in run.text
    assert [f["id"] for f in tachi_parsers.parse_reference_set(run.text)["open"] if f["id"].startswith("AGP")] == ["AGP-1"]


def test_order_a_halved_batch_joins_in_the_same_place_and_the_file_is_byte_identical(joiner, tmp_path):
    plain_run = Run(tmp_path / "a").ready()
    assert plain_run.join(joiner).code == 0
    halved = Run(tmp_path / "b", plan_id=OTHER_PLAN_ID).write_manifest().plan()
    for section in ("components", "actions", "llm"):
        halved.split(halved.batches_of(section)[0])
    halved.write_parts()
    assert halved.doc["retry_budget"]["used"] == 6
    assert halved.join(joiner).code == 0
    assert halved.text == plain_run.text, "a retry changes neither a row, nor its place, nor the stamp (NFR-2)"
    assert halved.record()["input_digest"] == plain_run.record()["input_digest"]


def test_order_a_child_of_a_child_joins_in_place(joiner, tmp_path):
    reference = Run(tmp_path / "a").ready()
    assert reference.join(joiner).code == 0
    nested = Run(tmp_path / "b", plan_id=OTHER_PLAN_ID).write_manifest().plan()
    parent = nested.batches_of("actions")[0]
    nested.split(parent).split(parent + "-1").write_parts()
    assert nested.entry(parent + "-1-1")["attempt"] == 3
    assert nested.join(joiner).code == 0
    assert nested.text == reference.text


def test_order_a_part_of_an_earlier_attempt_and_a_stray_part_never_count(joiner, tmp_path):
    run = Run(tmp_path).write_manifest().plan()
    parent = run.batches_of("components")[0]
    run.split(parent)
    run.write_parts()
    run.write_part(parent, raw=b"{}")  # the parent's attempt-1 part: stale
    stray = run.part_path(parent).with_name("B999.a1.json")
    stray.write_text("not json", encoding="utf-8")
    assert run.join(joiner).code == 0 and run.record()["status"] == "success"


def test_order_the_file_is_the_same_for_two_plans_of_the_same_manifest_and_parts(joiner, tmp_path):
    first = Run(tmp_path / "a", plan_id=PLAN_ID).ready()
    second = Run(tmp_path / "b", plan_id=OTHER_PLAN_ID).ready()
    assert first.join(joiner).code == 0 and second.join(joiner).code == 0
    assert first.text == second.text, "the plan ID is in no byte of the output"


def test_order_the_manifests_own_order_of_ids_does_not_change_the_file(joiner, tmp_path):
    first = Run(tmp_path / "a").ready()
    second = Run(tmp_path / "b", base_world(findings=list(reversed(copy.deepcopy(OPEN_FINDINGS))), resolved=list(reversed(copy.deepcopy(RESOLVED_FINDINGS))))).ready()
    assert first.join(joiner).code == 0 and second.join(joiner).code == 0
    assert first.text.split("\n")[:-2] == second.text.split("\n")[:-2], "everything but the stamp, whose digest covers the manifest's bytes"


# =============================================================================
# 7. Escaping: the cell sink, the extra # rule and S1P-A21's row form
# =============================================================================

def test_escape_every_row_line_is_the_escaped_items_in_the_contracts_row_form(done):
    for section in tp.THREATS_MD_SECTIONS:
        heading = last_heading(section)
        header, separator, rows = raw_table(done.text, heading) if section.key != "risk_levels" else (None, None, None)
        if section.key == "risk_levels":
            lines = done.text.split("\n")
            at = lines.index(SECTION_6_SENTENCE) + 2
            header, separator = lines[at], lines[at + 1]
            rows = []
            for line in lines[at + 2:]:
                if not line.startswith("|"):
                    break
                rows.append(line)
        assert header == header_line(section.header) and separator == separator_line(section.header), section.key
        assert rows == [row_line(expected_cells(done.world, section, unit)) for unit in expected_units(done.world, section.key)], section.key


def test_escape_hostile_text_round_trips_through_the_shared_readers(done):
    rows = {row["Finding ID"]: row for row in table_rows(done.text, "## 7. Recommended Actions", escaped_pipes=True)}
    assert rows["S-1"]["Threat"] == "Sends a | b <i>&</i> `code` {{x}} bold text"
    assert rows["T-9"]["Threat"] == "line one\nline two"
    assert table_rows(done.text, "### Components")[0]["Description"] == "Runs `jobs` | queues <b>&</b> {{x}}\nsecond line ~~~ and ## not a heading"
    assert table_rows(done.text, "### Technologies")[0]["Version (if known)"] == "3.12 \\", "the reader strips the bold markers and keeps the backslash"
    raw = done.text
    assert "&#124;" in raw and "&lt;i&gt;&amp;&lt;/i&gt;" in raw and "&#96;code&#96;" in raw and "&#123;&#123;x}}" in raw and "&#10;" in raw
    assert "<i>" not in raw and "`code`" not in raw and "{{x}}" not in raw


def test_escape_a_hash_in_a_cell_is_written_as_its_reference_so_no_cell_can_stand_in_for_a_heading(done):
    text = done.text
    assert text.count("## 7. Recommended Actions") == 1 and text.count("## 5. Coverage Matrix") == 1 and text.count("#### Risk by MAESTRO Layer") == 1
    assert "&#35;&#35; 7. Recommended Actions" in text
    unreferenced = [re.sub(r"&#(?:10|35|96|123|124|126);", "", line) for line in text.split("\n")]  # D3's references hold a # of their own
    assert [line for line in unreferenced if "#" in line and not line.startswith("#")] == [], "a raw # appears at the start of a heading line only"
    assert len(tachi_parsers.parse_reference_set(text)["open"]) == 16, "the cell that quotes Section 7's heading does not capture the reference set"
    assert [r["Component"] for r in table_rows(text, "## 5. Coverage Matrix")] == ["component 1", "component 2", "component 3", "component 4"]
    assert len(tachi_parsers.parse_markdown_table(text, "## 5. Coverage Matrix")) == 4, "even a reader that finds a section by substring reads the real table"
    assert len(tachi_parsers.parse_markdown_table(text, "### Technologies")) == 2, "data flow row 1 quotes `### Technologies` and does not capture that table"


def test_escape_a_cell_that_ends_in_a_backslash_reads_back_whole_s1p_a21(done):
    raw = done.text.split("\n")
    s2 = next(line for line in raw if line.startswith("| S-2 | NEW | Spoofing |"))
    assert s2.endswith("C:\\temp\\ |") and " | Critical | Rotate keys; the path is C:\\temp\\ |" in s2
    d1 = next(line for line in raw if line.startswith("| D-1 | NEW | Denial of Service |"))
    assert "| Wipes C:\\data\\ | Critical |" in d1
    reference = tachi_parsers.parse_reference_set(done.text)
    by_id = {f["id"]: f for f in reference["open"]}
    assert by_id["S-2"]["mitigation"] == "Rotate keys; the path is C:\\temp\\" and by_id["R-1"]["mitigation"] == "Keep a log of \\\\"
    assert by_id["D-1"]["threat"] == "Wipes C:\\data\\" and by_id["D-1"]["risk_level"] == "Critical" and by_id["D-1"]["mitigation"] == "Mitigation for D-1"
    rows = {row["Finding ID"]: row for row in table_rows(done.text, "## 7. Recommended Actions", escaped_pipes=True)}
    assert all(len(row) == 9 for row in rows.values()), "no row shifted"
    assert rows["R-1"]["Mitigation"] == "Keep a log of \\\\" and rows["S-2"]["Risk Level"] == "Critical"


def test_escape_a_pipe_in_a_cell_never_splits_a_row_in_any_reader(done):
    s1 = next(line for line in done.text.split("\n") if line.startswith("| S-1 | UNCHANGED | Spoofing |"))
    assert len(s1[2:-2].split(" | ")) == 9, "the cell's pipe is a reference, so the row has its nine cells"
    legacy = tachi_parsers.parse_markdown_table(done.text, "## 7. Recommended Actions")
    assert len(legacy) == 16 and all(len(row) == 9 for row in legacy), "the extractors' reader, which splits on every raw pipe, agrees"
    assert {r["id"]: r["threat"] for r in tachi_parsers.parse_resolved_findings(done.text)}["T-5"] == "SQL injection | in a retired endpoint"


def test_escape_a_trailing_backslash_in_the_last_cell_of_a_row_cannot_escape_the_closing_pipe(joiner, tmp_path):
    world = base_world()
    for record in world["findings"]:
        if record["id"] == "T-9":
            record["mitigation"] = "ends with one \\"
    run = Run(tmp_path, world).ready()
    assert run.join(joiner).code == 0
    assert {r["id"]: r["mitigation"] for r in tachi_parsers.parse_reference_set(run.text)["open"]}["T-9"] == "ends with one \\"


def test_escape_values_that_the_reader_normalizes_are_no_false_alarm_for_the_from_disk_check(joiner, tmp_path):
    """The reader strips a cell, drops its ``**`` markers, decodes it, and the finding strips it again. The from-disk check applies the same to the items, so
    bold at a cell's edge, a bold pair that spans a line break and text that already looks like one of D3's references join cleanly (P1-4): a run is never
    failed for a value that the reader normalizes. Each value reads back as the item with its markers dropped and its edges stripped, which is computed here."""
    findings = copy.deepcopy(OPEN_FINDINGS)
    by_id = {f["id"]: f for f in findings}
    by_id["S-1"].update(threat="** edge bold", mitigation="edge bold **", component="**Bold** Name")
    by_id["T-2"].update(threat="&amp; &#124; &#35; &lt;b&gt; &#10; literal references", mitigation="**a\nb** and ** **")
    by_id["E-1"].update(threat="**", mitigation="***")
    resolved = copy.deepcopy(RESOLVED_FINDINGS)
    resolved[0].update(threat="** edge bold", reason="**bold** reason **")
    run = Run(tmp_path, base_world(findings=findings, resolved=resolved)).ready()
    res = run.join(joiner)
    assert res.code == 0, res.describe()
    reference = tachi_parsers.parse_reference_set(run.text)
    read = {f["id"]: f for f in reference["open"]}
    for fid in ("S-1", "T-2", "E-1"):
        for key in ("component", "threat", "mitigation"):
            assert read[fid][key] == plain(by_id[fid][key]).strip(), (fid, key)
    assert read["T-2"]["threat"] == "&amp; &#124; &#35; &lt;b&gt; &#10; literal references", "text that looks like a reference is the text, once"
    assert read["E-1"]["threat"] == "" and read["E-1"]["mitigation"] == "*"
    read_resolved = {f["id"]: f for f in reference["resolved"]}
    assert read_resolved["I-7"]["threat"] == "edge bold" and read_resolved["I-7"]["resolution_reason"] == "bold reason"


# =============================================================================
# 8. The stamp and its digest
# =============================================================================

def test_stamp_the_last_line_is_the_provenance_comment_with_the_joiners_name_and_the_version(done):
    stamp = tp.read_stamp(done.text)
    assert stamp is not None and stamp["renderer"] == RENDERER_NAME and stamp["version"] == tp.VERSION and re.fullmatch(r"sha256:[0-9a-f]{64}", stamp["input_digest"])
    assert done.text.rstrip("\n").split("\n")[-1] == tp.stamp_comment(RENDERER_NAME, stamp["input_digest"])
    assert done.text.count("tachi-provenance") == 1


def test_stamp_the_digest_covers_the_manifests_digest_the_parameters_and_the_accepted_items_in_plan_order(done):
    items = []
    for entry in done.doc["batches"]:
        result = tp.read_part(str(done.part_path(entry["batch_id"])), str(done.out), PLAN_ID, entry["batch_id"], STAGE, AGENT, entry["finding_ids"],
                              done.batch_input(entry["batch_id"])["units"])
        assert result.state == "done"
        items += result.part["items"]
    expected = tp.input_digest({"sources": {"sections": sha256_of(done.manifest_path)}, "params": done.doc["params"], "items": items, "fragments": []})
    assert tp.read_stamp(done.text)["input_digest"] == expected == done.record()["input_digest"]


def test_stamp_a_changed_item_a_changed_manifest_or_changed_parameters_change_the_digest(joiner, tmp_path):
    def digest_of(name, world=None, mutate=None, params=None):
        run = Run(tmp_path / name, world).write_manifest().plan()
        if params is not None:
            run.doc["params"] = params
            for entry in run.doc["batches"]:
                run.write_input(entry, run.batch_input(entry["batch_id"])["units"])
            run.write_plan()
        run.write_parts(mutate=mutate)
        assert run.join(joiner).code == 0, name
        return tp.read_stamp(run.text)["input_digest"]

    base = digest_of("base")
    assert digest_of("same", None) == base
    changed = base_world()
    changed["hostile"][("components", 3, "description")] = "a changed row"
    assert digest_of("item", changed) != base
    assert digest_of("manifest", base_world(rows=dict(ROWS, risk_levels=7))) != base
    assert digest_of("params", params={"scoring_date": "2026-11-23"}) != base


def test_stamp_the_digest_is_not_read_from_the_plan_id_or_the_clock(joiner, tmp_path):
    first = Run(tmp_path / "a", plan_id=PLAN_ID).ready()
    second = Run(tmp_path / "b", plan_id=OTHER_PLAN_ID).ready()
    assert first.join(joiner).code == 0 and second.join(joiner).code == 0
    assert tp.read_stamp(first.text) == tp.read_stamp(second.text)
    assert first.record()["input_digest"] == second.record()["input_digest"]


# =============================================================================
# 9. Intake: re-validation (exit 1 and 2) and S1P-A18
# =============================================================================

MANIFEST_EDITS = {
    "a wrong schema": lambda m: m.update(schema="tachi.sections/2"),
    "an extra key": lambda m: m.update(extra=1),
    "a missing key": lambda m: m.pop("rows"),
    "no open finding": lambda m: m.update(open=[]),
    "an open ID off the allow-list": lambda m: m["open"].append("X-1"),
    "a repeated open ID": lambda m: m["open"].append(m["open"][0]),
    "two spellings of one ID": lambda m: m["open"].append("S-01"),
    "an ID both open and resolved": lambda m: m["resolved"].append(m["open"][0]),
    "resolved set with no baseline": lambda m: m["frontmatter"]["baseline"].update(source=None),
    "resolved null with a baseline": lambda m: m.update(resolved=None),
    "a bad date": lambda m: m["frontmatter"].update(date="2026-13-40"),
    "a bad run ID": lambda m: m["frontmatter"].update(run_id="2026-11-22 10:15:00"),
    "a classification off the pattern": lambda m: m["frontmatter"].update(classification="Confidential"),
    "an unknown input format": lambda m: m["frontmatter"].update(input_format="yaml"),
    "a quote in a string": lambda m: m["frontmatter"]["baseline"].update(source='a"b'),
    "a backslash in a string": lambda m: m["frontmatter"]["baseline"].update(date="a\\b"),
    "a newline in a string": lambda m: m["frontmatter"]["baseline"].update(run_id="a\nb"),
    "an empty string": lambda m: m["frontmatter"]["baseline"].update(source=""),
    "a negative finding count": lambda m: m["frontmatter"]["baseline"].update(finding_count=-1),
    "a row count over its cap": lambda m: m["rows"].update(components=5001),
    "an unknown row table": lambda m: m["rows"].update(extra=1),
    "a bad coverage status": lambda m: m["frontmatter"]["coverage_gate"].update(status="ok"),
    "a bad gap resolution": lambda m: m["frontmatter"]["coverage_gate"].update(gaps=[dict(GAPS[0], resolution="gave_up")]),
}


@pytest.mark.parametrize("name", sorted(MANIFEST_EDITS))
def test_intake_a_manifest_that_fails_its_contract_is_exit_2_with_the_files_untouched(joiner, run, name):
    manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
    MANIFEST_EDITS[name](manifest)
    run.replace_manifest(manifest)
    run.earlier()
    res = run.join(joiner)
    assert_failure(res, 2, "section manifest", "Kept for diagnosis: %s" % run.plan_dir)
    assert (run.out / MD).read_bytes() == EARLIER and not (run.plan_dir / "stage-record.json").exists()


def test_intake_a_manifest_that_is_not_json_or_not_strict_json_is_exit_2(joiner, run):
    for name, raw in (("not json", b"{"), ("a duplicate key", b'{"schema": "a", "schema": "b"}'), ("a BOM", b"\xef\xbb\xbf{}"), ("an array", b"[]"),
                      ("NaN", b'{"rows": NaN}'), ("not UTF-8", b"\xff\xfe{}")):
        run.replace_manifest(raw=raw)
        res = run.join(joiner)
        assert res.code == 2 and "section manifest" in res.err, "%s:\n%s" % (name, res.describe())


def test_intake_a_manifest_that_changed_after_plan_is_exit_2_whether_or_not_it_still_validates(joiner, run):
    manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
    manifest["frontmatter"]["classification"] = "internal"
    run.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    res = run.join(joiner)
    assert_failure(res, 2, "changed (or vanished) since plan")
    run.manifest_path.write_bytes(b"{")
    assert_failure(run.join(joiner), 2, "changed (or vanished) since plan")


def test_intake_a_plan_that_does_not_record_the_manifest_at_its_fixed_path_is_exit_2(joiner, run):
    copy_path = run.out / "copy-of-sections.json"
    copy_path.write_bytes(run.manifest_path.read_bytes())
    run.doc["inputs"]["sections"]["path"] = str(copy_path)
    run.write_plan()
    assert_failure(run.join(joiner), 2, "section manifest")
    run.doc["inputs"] = {}
    run.write_plan()
    assert_failure(run.join(joiner), 2, "section manifest")


def test_intake_a_dangling_link_at_the_fixed_path_while_the_plan_records_a_copy_is_exit_2(joiner, run):
    """The fixed path exists as a link, so the first look at it passes, and what it names is nowhere: the plan's own record (a copy) is not that file."""
    copy_path = run.out / "copy-of-sections.json"
    copy_path.write_bytes(run.manifest_path.read_bytes())
    run.doc["inputs"]["sections"]["path"] = str(copy_path)
    run.write_plan()
    run.manifest_path.unlink()
    run.manifest_path.symlink_to(run.out / "nowhere.json")
    res = run.join(joiner)
    assert_failure(res, 2, "section manifest")
    assert not (run.out / MD).exists()


def test_intake_a_manifest_that_changes_after_it_validates_is_exit_2(joiner, run, monkeypatch):
    """The version that was validated must be the version that the plan pinned: the digest is compared again once the manifest has been read and checked."""
    real = tp.entry_document

    def swapping(stage, path, out, schema, what, kept=None):
        document = real(stage, path, out, schema, what, kept)
        if schema == tp.SECTIONS_SCHEMA:
            Path(path).write_bytes(Path(path).read_bytes() + b" ")  # the same JSON, other bytes
        return document

    monkeypatch.setattr(tp, "entry_document", swapping)
    assert_failure(run.join(joiner), 2, "section manifest changed since plan")
    assert not (run.out / MD).exists()


def test_intake_a_plan_with_two_batches_for_one_unit_is_exit_2_and_names_the_second(joiner, tmp_path):
    """Two parts for the same rows would hide a drop behind the other (a set comparison alone would not see it), so the second is refused where it is read."""
    run = Run(tmp_path).write_manifest().plan(shape=lambda sections: sections + [sections[0]]).write_parts()
    assert len(run.doc["batches"]) == 25
    res = run.join(joiner)
    assert_failure(res, 2, "two batches carry the same unit of components", "B025", "rows 1 to 4 of components")
    assert not (run.out / MD).exists()


def test_intake_the_manifest_is_found_by_its_path_whatever_the_plan_calls_it(joiner, run):
    """reading: the contract says the plan records the manifest's digest in its ``inputs`` and names no key, so the planner may call it what it likes."""
    run.doc["inputs"] = {"section_manifest": run.doc["inputs"]["sections"]}
    run.write_plan()
    assert run.join(joiner).code == 0


def test_intake_a_frontmatter_string_is_written_as_it_is_and_one_that_quotes_a_heading_fails_loudly(joiner, tmp_path):
    """A frontmatter string is a YAML scalar and no cell, so ``#`` is not escaped there (an escape would change the value that the next run reads). A name such
    as ``C# API`` is fine. One that holds a heading's text, here ``## 7. Recommended Actions`` in a coverage gap's component, is found by the readers that look
    a section up by substring, so the read-back can't find Section 7 and the run fails (exit 4, or 2 if a later ruling refuses the string at intake). The
    earlier file stays: a misread file is never shipped."""
    fine = Run(tmp_path / "fine", base_world(gaps=[dict(GAPS[0], component="C# API")])).ready()
    assert fine.join(joiner).code == 0 and '{ component: "C# API", ' in fine.text
    assert len(tachi_parsers.parse_reference_set(fine.text)["open"]) == 16
    hostile = Run(tmp_path / "hostile", base_world(gaps=[dict(GAPS[0], component="x ## 7. Recommended Actions y")])).ready().earlier()
    res = hostile.join(joiner)
    assert res.code in (2, 4) and FAILED in res.err, res.describe()
    assert (hostile.out / MD).read_bytes() == EARLIER and not (hostile.plan_dir / "stage-record.json").exists()


def test_intake_a_plan_whose_batches_do_not_cover_the_manifests_rows_is_exit_2(joiner, tmp_path):
    def drop_a_row(sections):
        return [(key, units[:-1] if key == "components" else units, size) for key, units, size in sections]

    def add_a_row(sections):
        return [(key, units + [{"section": key, "row": len(units) + 1}] if key == "components" else units, size) for key, units, size in sections]

    def drop_a_finding(sections):
        return [(key, [u for u in units if u["finding_id"] != "S-1"] if key == "spoofing" else units, size) for key, units, size in sections]

    def drop_a_section(sections):
        return [entry for entry in sections if entry[0] != "technologies"]

    for name, shape in (("a missing row", drop_a_row), ("an extra row", add_a_row), ("a missing finding", drop_a_finding), ("a missing table", drop_a_section)):
        run = Run(tmp_path / name.replace(" ", "-")).write_manifest().plan(shape=shape).write_parts()
        res = run.join(joiner)
        assert res.code == 2 and "cover" in res.err and FAILED in res.err, "%s:\n%s" % (name, res.describe())
        assert not (run.out / MD).exists(), name


def test_intake_a_manifest_with_section_8_rows_and_no_baseline_is_exit_2(joiner, tmp_path):
    world = base_world(resolved=None)  # no baseline, though the manifest's row counts still name Section 8's two tables
    assert manifest_of(world)["rows"]["lifecycle"] == 5 and tp.validate_sections(manifest_of(world)), "the manifest passes its own validator"
    run = Run(tmp_path, world).ready()
    assert_failure(run.join(joiner), 2, "baseline")
    assert not (run.out / MD).exists(), "the rows are not dropped in silence"


def test_intake_a_missing_part_is_exit_1_and_names_its_batch(joiner, tmp_path):
    run = Run(tmp_path).write_manifest().plan().write_parts(skip=("B004",))
    res = run.join(joiner)
    assert_failure(res, 1, "B004", "part of batch", "missing")


def test_intake_a_part_only_at_an_earlier_attempt_is_missing(joiner, tmp_path):
    run = Run(tmp_path).write_manifest().plan()
    parent = run.batches_of("components")[0]
    run.split(parent).write_parts(skip=(parent + "-2",))
    assert_failure(run.join(joiner), 1, parent + "-2", "missing")


PART_EDITS = {
    "an unknown key in a row": lambda p: p["items"][0].update(extra="x"),
    "a missing key in a row": lambda p: p["items"][0].pop(next(k for k in p["items"][0] if k != "finding_id")),
    "a value that is not text": lambda p: p["items"][0].update({next(k for k in p["items"][0] if k != "finding_id"): 3}),
    "an empty evidence value": lambda p: p["items"][0].update({next(k for k in p["items"][0] if k != "finding_id"): "  "}),
    "fewer rows than planned": lambda p: p["items"].pop(),
    "more rows than planned": lambda p: p["items"].append(copy.deepcopy(p["items"][0])),
    "another plan": lambda p: p.update(plan_id=OTHER_PLAN_ID),
    "another batch": lambda p: p.update(batch_id="B099"),
    "another agent": lambda p: p.update(agent_type="tachi-report"),
    "another stage": lambda p: p.update(stage="report"),
    "fragments": lambda p: p.update(fragments=[{"slot_key": "x", "text": "y"}]),
    "an extra envelope key": lambda p: p.update(extra=1),
    "another schema": lambda p: p.update(schema="tachi.part/2"),
}


@pytest.mark.parametrize("name", sorted(PART_EDITS))
def test_intake_a_part_that_fails_re_validation_is_exit_2_and_names_its_batch(joiner, run, name):
    batch = run.batches_of("components")[0]
    run.write_part(batch, mutate=PART_EDITS[name])
    run.earlier()
    res = run.join(joiner)
    assert_failure(res, 2, batch, "part of batch", "Kept for diagnosis")
    assert (run.out / MD).read_bytes() == EARLIER


@pytest.mark.parametrize("edit", [lambda p: p["items"][0].update(status="DONE"), lambda p: p["items"][0].update(likelihood="low"),
                                  lambda p: p["items"][0].update(risk_level="Severe"), lambda p: p["items"][0].update(maestro_layer="L9"),
                                  lambda p: p["items"][0].update(finding_id="S-2")],
                         ids=["status", "likelihood", "risk-level", "layer", "id-outside-the-batch"])
def test_intake_a_closed_value_of_a_finding_table_is_checked_and_never_cut(joiner, run, edit):
    batch = run.batches_of("spoofing")[0]
    run.write_part(batch, mutate=edit)
    assert_failure(run.join(joiner), 2, batch)


def test_intake_a_part_that_is_garbage_an_overflow_object_or_too_large_is_exit_2(joiner, run):
    batch = run.batches_of("components")[0]
    for raw in (b"not json", b"[]", b'{"schema": "tachi.part/1", "schema": "tachi.part/1"}', b"\xef\xbb\xbf{}", b"x" * (tp.MAX_PART_BYTES + 1),
                json.dumps({"schema": tp.OVERFLOW_SCHEMA, "plan_id": PLAN_ID, "batch_id": batch, "stage": STAGE, "agent_type": AGENT, "reason": "output-budget"}).encode()):
        run.write_part(batch, raw=raw)
        assert_failure(run.join(joiner), 2, batch)


FORBIDDEN = [("a C0 control", "\x01"), ("DEL", "\x7f"), ("a C1 control", "\x85"), ("the line separator", "\u2028"), ("the paragraph separator", "\u2029"),
             ("a bidi override", "\u202e"), ("a bidi mark", "\u200f"), ("the Arabic letter mark", "\u061c"), ("a bidi isolate", "\u2066"),
             ("a tag character", "\U000e0041")]


@pytest.mark.parametrize("label,char", FORBIDDEN, ids=[label for label, _char in FORBIDDEN])
def test_intake_s1p_a18_a_character_the_contract_forbids_in_a_part_is_exit_2_and_never_reaches_a_file(joiner, run, label, char):
    batch = run.batches_of("actions")[0]
    run.write_part(batch, mutate=lambda p: p["items"][0].update(threat="before " + char + " after"))
    run.earlier()
    res = run.join(joiner)
    assert_failure(res, 2, batch)
    assert char not in res.err, "the message never repeats the character"
    assert (run.out / MD).read_bytes() == EARLIER and not (run.plan_dir / "staged").exists()


@pytest.mark.parametrize("label,char", FORBIDDEN, ids=[label for label, _char in FORBIDDEN])
def test_intake_s1p_a18_a_character_the_contract_forbids_in_a_row_table_part_is_exit_2(joiner, run, label, char):
    batch = run.batches_of("data_flows")[0]
    run.write_part(batch, mutate=lambda p: p["items"][1].update(data=char))
    assert_failure(run.join(joiner), 2, batch)


def test_intake_s1p_a18_a_lone_surrogate_in_a_part_is_exit_2(joiner, run):
    batch = run.batches_of("components")[0]
    part = run.part_for(batch)
    part["items"][1]["component"] = "SENTINEL"
    good = json.dumps(part, ensure_ascii=False)
    assert good.count("SENTINEL") == 1
    run.write_part(batch, raw=good.replace("SENTINEL", "x\\ud800y").encode("utf-8"))
    assert_failure(run.join(joiner), 2, batch)
    run.write_part(batch, raw=good.replace("SENTINEL", "x\\ud83d\\ude00y").encode("utf-8"))  # a proper pair is an emoji: allowed
    assert run.join(joiner).code == 0 and "x\U0001f600y" in run.text


@pytest.mark.parametrize("label,char", FORBIDDEN + [("a lone surrogate", "\ud800")], ids=[label for label, _char in FORBIDDEN] + ["a lone surrogate"])
@pytest.mark.parametrize("field", ["source", "date", "run_id"])
def test_intake_s1p_a18_a_character_the_contract_forbids_in_a_manifest_string_is_exit_2(joiner, run, label, char, field):
    manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
    manifest["frontmatter"]["baseline"][field] = "a" + char + "b"
    run.replace_manifest(raw=json.dumps(manifest).encode("ascii"))
    run.earlier()
    res = run.join(joiner)
    assert_failure(res, 2, "section manifest")
    assert char not in res.err and (run.out / MD).read_bytes() == EARLIER


def test_intake_s1p_a18_a_character_the_contract_forbids_in_a_coverage_gap_is_exit_2(joiner, tmp_path):
    run = Run(tmp_path, base_world(gaps=copy.deepcopy(GAPS))).write_manifest().plan().write_parts()
    manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
    manifest["frontmatter"]["coverage_gate"]["gaps"][1]["component"] = "API \u202eGateway"
    run.replace_manifest(raw=json.dumps(manifest).encode("ascii"))
    assert_failure(run.join(joiner), 2, "section manifest")


def test_intake_a_variation_selector_a_joiner_and_a_tab_are_allowed(joiner, tmp_path):
    world = base_world()
    world["hostile"][("components", 1, "description")] = "a family \U0001f468\u200d\U0001f469\u200d\U0001f467 and \u2764\ufe0f\tand a tab"
    run = Run(tmp_path, world).ready()
    assert run.join(joiner).code == 0
    assert "\u200d" in run.text and "\ufe0f" in run.text and "\t" in run.text


# =============================================================================
# 10. T107: the heading order and the headers against the template, one Section 7 row for each ID, and Section 4c's set
# =============================================================================

def template_lines():
    return TEMPLATE.read_text(encoding="utf-8").split("\n")


def header_cells(line):
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


def separator_row(line):
    return re.fullmatch(r"\|[\s\-:|]+\|", line) is not None


def headers_beneath(lines, at):
    """The distinct table headers (as cell tuples) between the heading at ``at`` and the next heading, in first-seen order."""
    found = []
    for index in range(at + 1, len(lines) - 1):
        if lines[index].startswith("#"):
            break
        if lines[index].startswith("|") and separator_row(lines[index + 1]) and header_cells(lines[index]) not in found:
            found.append(header_cells(lines[index]))
    return found


def test_t107_the_headings_come_in_the_templates_order_and_each_is_a_line_of_it(done):
    template = template_lines()
    written = [line for line in done.text.split("\n") if line.startswith("#")]
    positions = []
    for heading in written:
        assert heading in template, "the template has no heading line %r" % heading
        positions.append(template.index(heading))
    assert positions == sorted(positions) and len(set(positions)) == len(positions)


def test_t107_every_table_header_the_joiner_writes_is_the_templates_beneath_the_same_heading(done):
    template = template_lines()
    lines = done.text.split("\n")
    schema = OUTPUT_SCHEMAS.read_text(encoding="utf-8").split("\n")
    checked = 0
    for index, line in enumerate(lines):
        if not line.startswith("#") or line == "# Threat Model Report":
            continue
        written = headers_beneath(lines, index)
        if line == "## 4b. Findings by Agentic Pattern":  # the one exception: Section 4b takes output-schemas.md's single table
            start = next(i for i, text in enumerate(schema) if text.startswith("### Section 4b: Findings by Agentic Pattern"))
            wanted = headers_beneath(schema, start)
        else:
            wanted = headers_beneath(template, template.index(line))
        position = 0
        for header in written:
            assert header in wanted[position:], "beneath %r the template has no table with the header %r" % (line, header)
            position = wanted.index(header, position) + 1
            checked += 1
    assert checked >= 28, "the check saw every table the joiner writes (24 tables and the fixed ones)"


def test_t107_a_table_with_no_rows_keeps_the_templates_header(joiner, tmp_path):
    empty = {name: 0 for name in ROW_TABLES}
    empty.update(components=1)
    run = Run(tmp_path, {"findings": [copy.deepcopy(OPEN_FINDINGS[2])], "resolved": [], "rows": empty, "gaps": [], "hostile": {}}).ready()
    assert run.join(joiner).code == 0
    for section in tp.THREATS_MD_SECTIONS:
        if section.key in ("components", "actions", "spoofing", "resolved") or section.key in ("patterns", "gate_gaps"):
            continue
        if section.key == "risk_levels":
            assert header_line(section.header) in run.text.split("\n")
            continue
        header, separator, rows = raw_table(run.text, last_heading(section))
        assert (header, separator) == (header_line(section.header), separator_line(section.header)) and rows == [], section.key


def test_t107_one_section_7_row_for_each_id_and_no_other(done):
    reference = tachi_parsers.parse_reference_set(done.text)
    assert sorted((tp.canonical_finding_id(f["id"]) for f in reference["open"]), key=tp.finding_sort_key) == sorted(
        (tp.canonical_finding_id(f["id"]) for f in done.world["findings"]), key=tp.finding_sort_key)
    assert reference["duplicates"] == [] and reference["lacking"] == {} and reference["form"] == "table"
    rows = table_rows(done.text, "## 7. Recommended Actions", escaped_pipes=True)
    assert len(rows) == 16 == len({tp.canonical_finding_id(row["Finding ID"]) for row in rows})


def test_t107_each_finding_reads_back_with_the_values_of_its_item_under_the_readers_normalization(done):
    by_id = {tp.canonical_finding_id(f["id"]): f for f in done.world["findings"]}
    for found in tachi_parsers.parse_reference_set(done.text)["open"]:
        record = by_id[tp.canonical_finding_id(found["id"])]
        assert (found["id"], found["component"], found["threat"], found["risk_level"], found["mitigation"], found["delta_status"]) == (
            record["id"], plain(record["component"]), plain(record["threat"]), record["risk"], plain(record["mitigation"]), record["status"])
        assert found["agentic_pattern"] == tachi_parsers.parse_finding_pattern(record["pattern"])


def test_t107_section_4cs_set_is_exactly_the_manifests_resolved_ids(done):
    reference = tachi_parsers.parse_reference_set(done.text)
    assert [f["id"] for f in reference["resolved"]] == ["T-5", "I-7"]
    by_id = {r["id"]: r for r in done.world["resolved"]}
    for found in reference["resolved"]:
        record = by_id[found["id"]]
        assert (found["component"], found["threat"], found["risk_level"], found["resolution_reason"]) == (
            record["component"], record["threat"], record["last_risk"], record["reason"])


def test_t107_the_open_and_resolved_sets_share_no_finding(done):
    reference = tachi_parsers.parse_reference_set(done.text)
    assert not {tp.canonical_finding_id(f["id"]) for f in reference["open"]} & {tp.canonical_finding_id(f["id"]) for f in reference["resolved"]}


# =============================================================================
# 11. The from-disk checks, seeded one bug at a time (ADR-050 D4; part-files.md, "The joiner's checks and exit codes")
# =============================================================================

def section_7_rows(text):
    lines = text.split("\n")
    start = lines.index("## 7. Recommended Actions") + 4
    stop = start
    while lines[stop].startswith("|"):
        stop += 1
    return lines, start, stop


def edit_lines(change):
    def edit(text):
        lines, start, stop = section_7_rows(text)
        return "\n".join(change(lines, start, stop))
    return edit


def duplicate_a_row(lines, start, stop):
    return lines[:start + 1] + [lines[start]] + lines[start + 1:]


def drop_a_row(lines, start, stop):
    return lines[:start] + lines[start + 1:]


def add_an_unnamed_row(lines, start, stop):
    return lines[:stop] + [lines[start].replace("| S-2 |", "| S-9 |", 1)] + lines[stop:]


def change_a_value(lines, start, stop):
    return lines[:start] + [lines[start].replace("| API Gateway |", "| Another Component |", 1)] + lines[start + 1:]


def respell_an_id(lines, start, stop):
    return [line.replace("| AGP-01 |", "| AGP-1 |") if start <= i < stop else line for i, line in enumerate(lines)]


def rename_the_status_column(lines, start, stop):
    return lines[:start - 2] + [lines[start - 2].replace("| Status |", "| Stat |")] + lines[start - 1:]


def drop_the_pattern_closed_value(lines, start, stop):
    return lines[:start] + [lines[start].replace("| Spoofing | \u2014 |", "| Spoofing | none |", 1)] + lines[start + 1:]


def edit_4c(change):
    def edit(text):
        lines = text.split("\n")
        start = lines.index("## 4c. Resolved Findings") + 4
        return "\n".join(change(lines, start))
    return edit


def set_cell(index, value, heading="## 7. Recommended Actions"):
    """A seeded edit: the first row beneath ``heading`` with its cell ``index`` replaced by ``value``. The contract's row form puts a space on each side of
    every delimiter, and a cell holds no raw pipe, so the cells split on ``" | "``. The heading, a blank line, the header and the separator come first."""
    def edit(text):
        lines = text.split("\n")
        at = lines.index(heading) + 4
        cells = lines[at][2:-2].split(" | ")
        cells[index] = value
        return "\n".join(lines[:at] + ["| " + " | ".join(cells) + " |"] + lines[at + 1:])
    return edit


SECTION_4C = "## 4c. Resolved Findings"
SEEDS = [  # (name, a word the message names, the seeded edit of the staged markdown)
    ("a repeated Section 7 row", "repeats", edit_lines(duplicate_a_row)),
    ("a missing Section 7 row", "no row for", edit_lines(drop_a_row)),
    ("a Section 7 row for an ID the manifest does not name", "does not name", edit_lines(add_an_unnamed_row)),
    ("a Section 7 value that is not the item's", "differs", edit_lines(change_a_value)),
    ("an ID spelled otherwise than the manifest spells it", "spells", edit_lines(respell_an_id)),
    ("a Section 7 table without its Status column", "column", edit_lines(rename_the_status_column)),
    ("a Section 4c row that is missing", "Section 4c", edit_4c(lambda lines, start: lines[:start] + lines[start + 1:])),
    ("a Section 4c row for an ID the manifest does not name", "Section 4c", edit_4c(lambda lines, start: lines[:start] + [
        lines[start].replace("| T-5 |", "| E-9 |", 1)] + lines[start:])),
    ("a Section 4c value that is not the item's", "Section 4c", edit_4c(lambda lines, start: lines[:start] + [
        lines[start].replace("| Legacy API |", "| Another API |", 1)] + lines[start + 1:])),
    # P1-4: every value that the reference-set reader gives back is compared with its source, one seed for each. The first Section 7 row is S-2 (NEW,
    # no pattern, Critical) and the first Section 4c row is T-5. A check that dropped a field, or that compared the file with a second read of itself,
    # would pass one of these.
    ("a Section 7 status that is not the item's", "delta_status for S-2 differs", set_cell(1, "UPDATED")),
    ("a Section 7 pattern that is not the item's", "agentic_pattern for S-2 differs", set_cell(3, "multiple")),
    ("a Section 7 component that is not the item's", "component for S-2 differs", set_cell(4, "Another Component")),
    ("a Section 7 threat that is not the item's", "threat for S-2 differs", set_cell(6, "Another threat")),
    ("a Section 7 risk level that is not the item's", "risk_level for S-2 differs", set_cell(7, "Low")),
    ("a Section 7 mitigation that is not the item's", "mitigation for S-2 differs", set_cell(8, "Another mitigation")),
    ("a Section 4c component that is not the item's", "component for T-5 differs", set_cell(1, "Another API", SECTION_4C)),
    ("a Section 4c threat that is not the item's", "threat for T-5 differs", set_cell(2, "Another threat", SECTION_4C)),
    ("a Section 4c risk level that is not the item's", "risk_level for T-5 differs", set_cell(3, "Note", SECTION_4C)),
    ("a Section 4c reason that is not the item's", "resolution_reason for T-5 differs", set_cell(4, "Another reason", SECTION_4C)),
    ("a character that the part contract forbids", "forbids", lambda text: text.replace("| API Gateway |", "| API \u202eGateway |", 1)),
    ("a provenance stamp with another digest", "provenance stamp", lambda text: re.sub(r"input-digest=sha256:[0-9a-f]{64}", "input-digest=sha256:" + "0" * 64, text)),
    ("a missing provenance stamp", "provenance stamp", lambda text: text[:text.rindex("<!-- tachi-provenance")]),
    ("a provenance stamp that is not the last line", "provenance stamp", lambda text: text + "trailing\n"),
    ("text that is not the text rendered", "not the text that was rendered", lambda text: text.replace("## 6. Risk Summary", "## 6. Risk Summary ", 1)),
]


@pytest.mark.parametrize("name,word,edit", SEEDS, ids=[seed[0] for seed in SEEDS])
def test_disk_a_seeded_bug_is_named_and_stops_the_run_before_any_canonical_file_is_replaced(joiner, run, name, word, edit):
    run.earlier()
    before = tree_state(run.out)
    with tampering_with_staged(MD, edit):
        res = run.join(joiner)
    assert_failure(res, 4, CHECK_FAILED, word, "Kept for diagnosis: %s" % run.plan_dir)
    assert (run.out / MD).read_bytes() == EARLIER, "the canonical file is untouched"
    assert (run.plan_dir / "staged" / MD).is_file(), "the staged file is kept for diagnosis"
    assert not (run.plan_dir / "stage-record.json").exists()
    after = tree_state(run.out)
    assert new_files(before, after) == [".tachi-build/%s/%s/staged/%s" % (STAGE, PLAN_ID, MD)] and changed_files(before, after) == []


def test_disk_the_seeded_edits_would_each_pass_the_checks_if_they_were_not_bugs(joiner, run):
    """A guard against vacuous seeds: an edit that changes nothing, applied the same way, leaves the run clean."""
    with tampering_with_staged(MD, lambda text: text + "\n"):  # a harmless-looking edit that is still not the rendered text
        assert run.join(joiner).code == 4
    clean = Run(run.tmp / "again", plan_id=OTHER_PLAN_ID).ready()
    assert clean.join(joiner).code == 0


def test_disk_a_failed_move_leaves_the_canonical_file_alone_and_is_exit_4(joiner, run):
    run.earlier()
    with failing_replace(MD):
        res = run.join(joiner)
    assert_failure(res, 4, "threats.md", "re-run the command")
    assert (run.out / MD).read_bytes() == EARLIER and not (run.plan_dir / "stage-record.json").exists()
    assert run.join(joiner).code == 0, "the same plan joins once the failure is gone"


def test_disk_a_failed_write_of_the_staged_file_is_exit_4(joiner, run, monkeypatch):
    run.earlier()

    def refuse(path, data, mode_of=None):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(tp, "atomic_write", refuse)
    res = run.join(joiner)
    assert_failure(res, 4, "could not be written")
    assert (run.out / MD).read_bytes() == EARLIER


def test_disk_a_staged_that_is_a_link_is_exit_2(joiner, run):
    (run.plan_dir / "staged").symlink_to(run.out)
    run.earlier()
    assert_failure(run.join(joiner), 2, "staged")
    assert (run.out / MD).read_bytes() == EARLIER


def test_disk_an_unexpected_error_is_a_defect_with_exit_4_and_the_plan_is_kept(joiner, run, monkeypatch):
    def boom(text, keep_slots=False):
        raise RuntimeError("seeded defect\x07")

    monkeypatch.setattr(tp, "escape_cell", boom)
    res = run.join(joiner)
    assert_failure(res, 4, "an unexpected error", "seeded defect", "report this as a bug in %s" % RENDERER_NAME, "Kept for diagnosis: %s" % run.plan_dir)
    assert "\x07" not in res.err
    assert not (run.out / MD).exists()


def test_disk_a_stage_record_that_fails_its_own_contract_is_exit_4_with_the_file_already_moved(joiner, run, monkeypatch):
    real = tp.stage_record

    def wrong(*args, **kwargs):
        record = real(*args, **kwargs)
        record["counts"]["surprise"] = 1
        return record

    monkeypatch.setattr(tp, "stage_record", wrong)
    res = run.join(joiner)
    assert_failure(res, 4, "stage record", "report this as a bug in %s" % RENDERER_NAME)
    assert not (run.plan_dir / "stage-record.json").exists()


# =============================================================================
# 12. Scale: many parts for one table, and halved batches among them
# =============================================================================

def scale_world(per_prefix=18):
    findings = []
    risks = ["Critical", "High", "Medium", "Low", "Note"]
    statuses = ["NEW", "UNCHANGED", "UPDATED"]
    count = 0
    for prefix in ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE"):
        for number in range(per_prefix, 0, -1):  # in reverse, so the manifest is not in S-2 order
            count += 1
            fid = "%s-%02d" % (prefix, number) if prefix == "AGP" and number < 10 else "%s-%d" % (prefix, number)
            findings.append(finding(fid, statuses[count % 3], "Component %d" % (count % 7), risks[count % 5], pattern=EM if count % 4 else "temporal_attack"))
    resolved = [{"id": "T-%d" % n, "component": "Old %d" % n, "threat": "Old threat %d" % n, "last_risk": risks[n % 5], "reason": "Removed"}
                for n in range(100, 170)]
    rows = {name: 3 for name in ROW_TABLES}
    rows.update(components=70, data_flows=130, trust_zones=60, correlated=30, coverage=70, risk_by_layer=7, risk_levels=6)
    return {"findings": findings, "resolved": resolved, "rows": rows, "gaps": [], "hostile": {}}


def test_scale_many_parts_and_halved_batches_join_into_the_same_file_as_one_part_each(joiner, tmp_path):
    world = scale_world()
    plain_run = Run(tmp_path / "a", world).ready()
    parts = len(plain_run.doc["batches"])
    assert parts > 40, "the world needs several parts for the big tables"
    assert plain_run.join(joiner).code == 0
    halved = Run(tmp_path / "b", world, plan_id=OTHER_PLAN_ID).write_manifest().plan()
    for number, entry in enumerate(list(halved.doc["batches"])):
        if number % 3 == 0 and len(halved.batch_input(entry["batch_id"])["units"]) >= 2:
            halved.split(entry["batch_id"])
    halved.write_parts()
    assert halved.doc["retry_budget"]["used"] > 20
    assert halved.join(joiner).code == 0
    assert halved.text == plain_run.text
    for key in ("components", "data_flows", "agentic", "llm", "actions", "resolved", "correlated"):
        section = tp.THREATS_MD_BY_KEY[key]
        rows = table_rows(plain_run.text, last_heading(section), escaped_pipes=(key == "actions"))
        assert rows == expected_rows(world, key), key
    reference = tachi_parsers.parse_reference_set(plain_run.text)
    assert len(reference["open"]) == 216 and len(reference["resolved"]) == 70 and reference["duplicates"] == []
    record = plain_run.record()
    assert record["counts"]["open"] == 216 and record["counts"]["resolved"] == 70 and record["counts"]["units"] == record["counts"]["rendered"]
