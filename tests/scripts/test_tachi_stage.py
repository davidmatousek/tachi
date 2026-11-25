"""Tests for ``scripts/tachi-stage.py``, written before the script (F-374 T017; TDD).

They target ``contracts/cli.md`` (the CLI and its exit table) and ADR-050 D3 (the part-file
contract), D4 (exit codes, failed outputs) and D6 (batching, retries, limits), never an
implementation. T018 writes the script to them, and T140 adds ``architecture-source`` last. Until
then they fail: the script doesn't exist.

How they run (ADR-050 D16, H15): gated tests drive the entry **in-process**, through
``tests/conftest.py``'s ``_load_hyphenated_script`` and ``main(argv)``, so pytest-cov counts them.
One subprocess case covers only what a process alone shows: exit codes from a real interpreter. The
3.9 guard's refusal before any import is the other such case, and it lives in
``test_runtime_floor_374.py``, which runs every entry through a fresh interpreter.

The planner's function interface (ADR-050 D6: batch sizes are constants, "tests can set smaller
sizes only through the planner's function interface")::

    plan_stage(stage=, out=, date=, threats=, risk_scores=None, baseline_dir=None,
               architecture=None, target=None, batch_size=None) -> {plan_id, plan_digest, waves}

``batch_size=None`` means the stage's constant. ``main(["plan", ...])`` calls the same function with
``None``, so a size reaches the planner only through it. ``Harness.plan`` below is the one place the
tests call it.

Where the contract left a shape open, these tests pinned a reading, marked ``# reading:``. The architect ruled
every one at W1 (2026-11-22, T023; ``contracts/cli.md`` and ``contracts/part-files.md``, "Readings ruled at
W1") and confirmed them with three additions that the tests below follow: a one-unit batch retries with the
same member and ID, ``error`` names the first exhausted lineage in plan order while ``batches.exhausted`` counts
them all, and ``--version`` prints to stdout (its refusal below 3.9 goes to stderr). The marker stays where a
test depends on one of those readings.

Standard library and pytest only, and Python 3.9 syntax.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from collections import namedtuple
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCRIPT = SCRIPTS_DIR / "tachi-stage.py"
SUBPROCESS_TIMEOUT = 120

DATE = "2026-11-22"
STAGE_NAMES = ("risk-score", "compensating-controls")
AGENT_FOR = {"risk-score": "tachi-risk-scorer", "compensating-controls": "tachi-control-analyzer"}
OUTPUTS_FOR = {
    "risk-score": ("risk-scores.md", "risk-scores.sarif"),
    "compensating-controls": ("compensating-controls.md", "compensating-controls.sarif"),
}

# --------------------------------------------------------------------------- contract constants

PLAN_ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}\Z")
ISO_UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z\Z")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+\Z")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}\Z")
PREFIX_ORDER = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")

PLAN_KEYS = {
    "schema", "plan_id", "stage", "agent_type", "created_utc", "tachi_version", "inputs", "refs", "architecture_warning",
    "params", "batch_size", "unit_count", "preimage", "out_snapshot", "retry_budget", "batches",
}
BATCH_ENTRY_KEYS = {"batch_id", "parent", "attempt", "finding_ids", "input_sha256", "state"}
BATCH_INPUT_KEYS = {
    "schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "attempt", "part_path",
    "tree_paths", "units", "refs", "params",
}
RECORD_KEYS = {
    "schema", "stage", "plan_id", "status", "tachi_version", "started_utc", "finished_utc", "input_digest",
    "counts", "batches", "overflow_events", "retries", "warnings", "undeclared_paths", "outputs", "error",
}
RECORD_BATCH_KEYS = {"planned", "dispatched", "done", "retried", "split", "exhausted"}
ERROR_KEYS = {"code", "message", "batch_id", "finding_ids", "remedy"}
RECONCILE_KEYS = {"status", "plan_digest", "done", "waves", "exhausted"}
FAIL_REASONS = ("agent-not-spawned", "unrecoverable-batch", "check-failed", "render-failed")


def canon(finding_id):
    """The canonical ID: the prefix, a hyphen and the number without leading zeros (ADR-050 D3)."""
    prefix, _, number = finding_id.partition("-")
    return "%s-%d" % (prefix, int(number))


def s2_key(finding_id):
    """S-2's total order: prefix rank, then the numeric suffix as an integer."""
    prefix, _, number = canon(finding_id).partition("-")
    return (PREFIX_ORDER.index(prefix), int(number))


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# 16 IDs over every prefix but three, listed out of S-2 order. AGP-01 is spelled with a leading zero
# on purpose: it compares as AGP-1.
MIXED_IDS = [
    "T-10", "S-2", "AGP-01", "T-9", "LLM-3", "S-1", "AG-1", "OI-1",
    "E-1", "D-2", "R-1", "I-3", "MI-1", "TE-1", "AGP-2", "AGP-10",
]
EARLIER_MD = b"# the earlier run's markdown\n"
EARLIER_SARIF = b'{"earlier": "run"}\n'
NEW_MD = b"# a run that went wrong\n"
NEW_SARIF = b'{"new": "run"}\n'

# --------------------------------------------------------------------------- synthetic inputs

_CATEGORY = {
    "S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information Disclosure",
    "D": "Denial of Service", "E": "Elevation of Privilege", "AG": "Agentic", "AGP": "Agentic",
    "LLM": "LLM", "OI": "LLM", "MI": "LLM", "TE": "Agentic",
}
_DASH = "—"


def make_threats_md(open_ids, resolved_ids=(), section7="table", preamble="", statuses=None, groups=(), baseline_source=None):
    """A synthetic ``threats.md``: Section 7 lists the open findings, Section 4c the resolved ones.

    Rows are written in reverse S-2 order, as Section 7 is sorted by risk and not by ID. ``section7``
    breaks the section for the S-12(c) cases: ``missing``, ``empty`` (a header and no rows) or
    ``prose`` (no table). ``preamble`` goes between the title and the first ``## `` heading. T044's routing
    cases add ``statuses`` (finding ID to its Status cell, ``NEW`` when absent), ``groups`` (Section 4a rows as
    ``(group ID, [finding IDs])``) and the frontmatter's ``baseline.source``.
    """
    lines = [
        "---", 'schema_version: "1.4"', 'date: "2026-11-22"', 'input_format: "mermaid"',
        'classification: "confidential"', 'run_id: "2026-11-22T10-00-00"',
        "baseline:", "  source: %s" % ("null" if baseline_source is None else '"%s"' % baseline_source),
        "  date: null", "  finding_count: null", "  run_id: null",
        "coverage_gate:", '  status: "pass"', "  gaps: []", "---", "",
        "# Threat Model: Synthetic Fixture", "",
    ]
    if preamble:
        lines += [preamble, ""]
    lines += ["## 1. System Overview", "", "A synthetic system for the tests.", ""]
    if groups:
        lines += ["## 4a. Correlated Findings", "", "| Group | Findings | Component |", "|-------|----------|-----------|"]
        lines += ["| %s | %s | Gateway |" % (group, ", ".join(members)) for group, members in groups] + [""]
    if resolved_ids:
        lines += [
            "## 4c. Resolved Findings", "",
            "| ID | Component | Threat | Last Risk Level | Resolution Reason |",
            "|----|-----------|--------|-----------------|-------------------|",
        ]
        lines += ["| %s | Legacy %d | Old threat %s | High | Component removed |" % (fid, n, fid)
                  for n, fid in enumerate(resolved_ids, 1)]
        lines += [""]
    lines += ["## 6. Risk Summary", "", "The counts here are not read by the planner.", ""]
    if section7 != "missing":
        lines += ["## 7. Recommended Actions", ""]
        if section7 == "prose":
            lines += ["Every finding was mitigated. Nothing is listed here.", ""]
        else:
            lines += [
                "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
            if section7 == "table":
                for n, fid in enumerate(sorted(open_ids, key=s2_key, reverse=True), 1):
                    prefix = fid.partition("-")[0]
                    lines.append(
                        "| %s | %s | %s | %s | Gateway %d | L4 %s Deployment | Threat text for %s | High | Mitigation text for %s |"
                        % (fid, (statuses or {}).get(fid, "NEW"), _CATEGORY[prefix], _DASH, n, _DASH, fid, fid)
                    )
            lines += [""]
    return "\n".join(lines) + "\n"


def make_scored_md(open_ids, resolved_ids=(), source_file="run/threats.md"):
    """A synthetic ``risk-scores.md``: the controls stage's input (T036). Frontmatter names the threat model it scored, §2 lists the
    open findings (in reverse S-2 order, as a sort by risk leaves them) and §2a the RESOLVED ones, which are never planned."""
    head = ["---", 'schema_version: "1.1"', 'date: "2026-11-22"', "source_file: %s" % ("null" if source_file is None else '"%s"' % source_file),
            'classification: "confidential"', "---", "", "# Risk Scores Report", "", "## 2. Scored Threat Table", "",
            "| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Flags |",
            "|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|-------|"]
    rows = ["| %s | fresh | Gateway | Threat text for %s | 7.1 | 6.0 | 6.0 | 6.0 | 6.4 | Medium | 30d | Review | \u2014 |" % (fid, fid)
            for fid in sorted(open_ids, key=s2_key, reverse=True)]
    tail = []
    if resolved_ids:
        tail = ["", "## 2a. Resolved Findings", "",
                "| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Status | Owner | Review Date | Flags |",
                "|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|--------|-------|-------------|-------|"]
        tail += ["| %s | inherited | Legacy | Old threat | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | \u2014 | RESOLVED | Unassigned | \u2014 | resolved |" % fid
                 for fid in resolved_ids]
    return "\n".join(head + rows + tail) + "\n"


def scorer_item(finding_id):
    """One valid risk-score item (``contracts/part-files.md`` §1): no digits in narrative prose."""
    return {
        "finding_id": finding_id,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "exploitability": {"known_techniques": 5, "attack_complexity": 5, "tooling_availability": 5, "skill_level": 5},
        "scalability": {"scriptability": 5, "target_scope": 5, "resource_requirements": 5, "detection_difficulty": 5},
        "reachability": {"zone": None, "trust_level": None, "auth_barriers": 5, "network_boundaries": 5},
        "rationale": {
            "cvss": "Remote and unauthenticated.",
            "exploitability": "Public techniques exist.",
            "scalability": "Easy to repeat.",
            "reachability": "Exposed to the edge.",
        },
    }


def matrix_cells(finding_id):
    """The 11 cells of K8's section 2 row for a missing control, in the order ``contracts/module-signatures.md`` pins."""
    return [finding_id, _DASH, "Gateway", "L1", "A threat", "{{score:inherent}}", "{{band:inherent}}", "No Control Found",
            "authentication", "{{score:residual}}", "{{band:residual}}"]


def matrix_row_of(cells):
    """``cells`` as the GFM table line that the row is, with its outer pipes."""
    return "| " + " | ".join(cells) + " |"


# The four keys of the 1.1 template's section 4 block, each once and in order, with the Effort Estimate starting at a level.
CONTROLS_BODY = "\n".join([
    "**What to Implement**: Add the missing control at the trust boundary.",
    "**Where to Implement**: `gateway/`, beside the existing request handlers.",
    "**Reference Patterns**: The framework's own middleware.",
    "**Effort Estimate**: Medium",
])


def controls_item(finding_id):
    """One valid compensating-controls item for a missing control (``contracts/part-files.md`` §1)."""
    return {
        "finding_id": finding_id,
        "control_status": "missing",
        "control_category": "authentication",
        "confidence": None,
        "carried_forward": False,
        "evidence": [],
        "matrix_row": matrix_row_of(matrix_cells(finding_id)),
        "recommendation_body": CONTROLS_BODY,
    }


ITEM_FOR = {"risk-score": scorer_item, "compensating-controls": controls_item}


def unit_ids(units):
    """The finding IDs of a batch input's unit rows. The row's key for it isn't pinned, so accept both."""
    found = []
    for row in units:
        for key in ("finding_id", "id"):
            if key in row:
                found.append(row[key])
                break
        else:
            raise AssertionError("a unit row names no finding: keys %r" % sorted(row))
    return found


def tree_state(root):
    """{relative path: sha256} for every file under ``root``, to prove nothing there changed."""
    root = Path(root)
    if not root.exists():
        return {}
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}


# --------------------------------------------------------------------------- harness


class Result(object):
    def __init__(self, code, out, err):
        self.code, self.out, self.err = code, out, err

    @property
    def json(self):
        """The one JSON object on stdout (contracts/cli.md: errors go to stderr, never mixed in)."""
        return json.loads(self.out)

    def describe(self):
        return "exit %r\n--- stdout ---\n%s\n--- stderr ---\n%s" % (self.code, self.out, self.err)


@pytest.fixture(scope="module")
def stage():
    if not SCRIPT.is_file():
        pytest.fail("scripts/tachi-stage.py does not exist yet: T018 writes it to these tests (TDD)", pytrace=False)
    return _load_hyphenated_script("tachi_stage_under_test", "tachi-stage.py")


@pytest.fixture(scope="module")
def tachi_version():
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parts  # W1's helper (T012, T013); the version is its constant, never a literal (ADR-050 D4)

    return tachi_parts.VERSION


@pytest.fixture
def cli(stage, capsys):
    """``cli("plan", ...)`` runs ``main(argv)`` in-process and returns exit code, stdout and stderr."""

    def run(*argv):
        capsys.readouterr()
        try:
            code = stage.main([str(a) for a in argv])
        except SystemExit as exc:  # argparse's usage errors and --help
            code = exc.code
            if code is None:
                code = 0
            elif not isinstance(code, int):
                sys.stderr.write(str(code))
                code = 1
        out, err = capsys.readouterr()
        return Result(code, out, err)

    return run


class Harness(object):
    """One run directory, one stage, and the calls every test makes."""

    def __init__(self, stage, cli, root, name="risk-score", ids=None, resolved=(), section7="table"):
        self.stage, self.cli, self.name = stage, cli, name
        self.root = Path(root)
        self.out = self.root / "run"
        self.out.mkdir(parents=True)
        self.ids = list(MIXED_IDS if ids is None else ids)
        self.threats = self.out / "threats.md"
        self.threats.write_text(make_threats_md(self.ids, resolved, section7), encoding="utf-8")
        self.md, self.sarif = OUTPUTS_FOR[name]
        self.plan_id = None
        self.digest = None
        if name == "compensating-controls":
            # The controls stage plans from the scorer's risk-scores.md, which names its threat model in source_file (ADR-050 D8),
            # and scans a codebase (T036). source_file is relative to the working directory, so a test that reads unit rows chdirs
            # to the root first, as the command runs.
            self.risk_scores = self.out / "risk-scores.md"
            self.risk_scores.write_text(make_scored_md(self.ids, resolved), encoding="utf-8")
            self.target = self.root / "app"
            self.target.mkdir()

    @property
    def expected_inputs(self):
        """The logical names of the plan's digest-checked inputs when no baseline is named."""
        return {"risk_scores", "threats"} if self.name == "compensating-controls" else {"threats"}

    @property
    def expected_refs(self):
        """The plan's ``refs`` when no optional pointer is named (``contracts/part-files.md`` §4)."""
        refs = {"threats": str(self.threats)}
        if self.name == "compensating-controls":
            refs.update(risk_scores=str(self.risk_scores), target=str(self.target))
        return refs

    # ---- layout
    @property
    def build(self):
        return self.out / ".tachi-build" / self.name

    @property
    def plan_dir(self):
        return self.build / self.plan_id

    def read_json(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def plan_json(self):
        return self.read_json(self.plan_dir / "plan.json")

    def batches(self):
        return {b["batch_id"]: b for b in self.plan_json()["batches"]}

    def batch_input(self, batch_id):
        return self.read_json(self.plan_dir / "inputs" / ("%s.json" % batch_id))

    # ---- earlier outputs and a failed render
    def earlier(self, md=True, sarif=True):
        """The outputs of an earlier successful run, before the plan takes its pre-images."""
        if md:
            (self.out / self.md).write_bytes(EARLIER_MD)
        if sarif:
            (self.out / self.sarif).write_bytes(EARLIER_SARIF)

    def render(self, md=True, sarif=True):
        """What a renderer that got part way does: it replaced these canonical files."""
        if md:
            (self.out / self.md).write_bytes(NEW_MD)
        if sarif:
            (self.out / self.sarif).write_bytes(NEW_SARIF)

    def assert_earlier_outputs_untouched(self, md=True, sarif=True):
        if md:
            assert (self.out / self.md).read_bytes() == EARLIER_MD
        if sarif:
            assert (self.out / self.sarif).read_bytes() == EARLIER_SARIF

    # ---- plan
    def plan(self, batch_size=None, **optional):
        """The planner through its function interface: the one way a size gets in (ADR-050 D6).

        The pointers every plan of the stage needs are the default: ``threats`` for the scorer, and ``risk_scores`` and
        ``target`` for the controls stage, which reaches ``threats.md`` through ``risk-scores.md`` (T036).
        """
        pointers = {"risk_scores": self.risk_scores, "target": self.target} if self.name == "compensating-controls" else {"threats": self.threats}
        result = self.stage.plan_stage(stage=self.name, out=self.out, date=DATE, batch_size=batch_size, **dict(pointers, **optional))
        self.plan_id, self.digest = result["plan_id"], result["plan_digest"]
        return result

    def plan_cli(self, *extra):
        pointers = ["--risk-scores", self.risk_scores, "--target", self.target] if self.name == "compensating-controls" else ["--threats", self.threats]
        res = self.cli("plan", "--stage", self.name, "--out", self.out, "--date", DATE, *pointers, *extra)
        if res.code == 0:
            printed = res.json
            self.plan_id, self.digest = printed["plan_id"], printed["plan_digest"]
        return res

    # ---- reconcile and fail
    def plan_args(self, plan_id=None, digest=None):
        return ["--plan", plan_id or self.plan_id, "--plan-digest", digest or self.digest]

    def reconcile(self, plan_id=None, digest=None):
        res = self.cli("reconcile", "--stage", self.name, "--out", self.out, *self.plan_args(plan_id, digest))
        if res.code in (0, 3, 4):
            self.digest = res.json["plan_digest"]
        return res

    def fail(self, reason="check-failed", detail=None, plan_id=None, digest=None):
        extra = ["--detail", detail] if detail is not None else []
        return self.cli("fail", "--stage", self.name, "--out", self.out, *self.plan_args(plan_id, digest),
                        "--reason", reason, *extra)

    @staticmethod
    def pending(printed):
        """The batch IDs a ``reconcile`` or ``plan`` result tells the caller to dispatch."""
        return sorted(batch["batch_id"] for wave in printed["waves"] for batch in wave)

    # ---- parts
    def part_for(self, batch_id):
        bi = self.batch_input(batch_id)
        return {
            "schema": "tachi.part/1",
            "plan_id": bi["plan_id"],
            "batch_id": bi["batch_id"],
            "stage": bi["stage"],
            "agent_type": bi["agent_type"],
            "finding_ids": list(bi["finding_ids"]),
            "items": [ITEM_FOR[self.name](fid) for fid in bi["finding_ids"]],
            "fragments": [],
        }

    def part_path(self, batch_id):
        return Path(self.batch_input(batch_id)["part_path"])

    def write_part(self, batch_id, mutate=None, raw=None):
        """A writer agent's Write: a valid part at the path the batch input names, or ``raw`` bytes."""
        path = self.part_path(batch_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            path.write_bytes(raw)
        else:
            part = self.part_for(batch_id)
            if mutate is not None:
                mutate(part)
            path.write_text(json.dumps(part), encoding="utf-8")
        return path

    def write_valid_parts(self, only=None):
        for batch_id, entry in self.batches().items():
            if entry["state"] != "split" and (only is None or batch_id in only):
                self.write_part(batch_id)

    def overflow_object(self, batch_id, reason="output-budget"):
        bi = self.batch_input(batch_id)
        return {"schema": "tachi.overflow/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"],
                "stage": bi["stage"], "agent_type": bi["agent_type"], "reason": reason}


def check_record(rec, name, plan_id, version):
    """A failed stage record has the closed key set of ``contracts/part-files.md`` §5."""
    assert set(rec) == RECORD_KEYS
    assert rec["schema"] == "tachi.stage-record/1"
    assert (rec["stage"], rec["plan_id"], rec["status"]) == (name, plan_id, "failed")
    assert rec["tachi_version"] == version
    assert ISO_UTC.match(rec["started_utc"]) and ISO_UTC.match(rec["finished_utc"])
    assert re.match(r"^sha256:[0-9a-f]{64}\Z", rec["input_digest"])
    assert isinstance(rec["counts"], dict)
    assert all(isinstance(v, int) and v >= 0 for v in rec["counts"].values())
    assert set(rec["batches"]) == RECORD_BATCH_KEYS
    assert all(isinstance(v, int) and v >= 0 for v in rec["batches"].values())
    for key in ("overflow_events", "retries", "warnings", "undeclared_paths", "outputs"):
        assert isinstance(rec[key], list), key
    assert isinstance(rec["error"], dict) and set(rec["error"]) == ERROR_KEYS


# =========================================================================== plan: the contract


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_plan_writes_the_layout_and_prints_the_contract_object(stage, cli, tmp_path, monkeypatch, tachi_version, name):
    """D3's layout, ``contracts/part-files.md`` §3 and §4, and the object ``plan`` prints (cli.md)."""
    monkeypatch.chdir(tmp_path)  # the controls stage reaches threats.md through source_file, which is relative to the working directory
    h = Harness(stage, cli, tmp_path, name)
    h.earlier(sarif=False)  # an earlier .md and no .sarif: one pre-image has a digest, the other is null
    res = h.plan(batch_size=4)  # 16 units -> B001..B004

    assert set(res) == {"plan_id", "plan_digest", "waves"}
    assert PLAN_ID.match(res["plan_id"])
    assert sha256_of(h.plan_dir / "plan.json") == res["plan_digest"], "plan_digest is the SHA-256 of the plan file"
    assert h.read_json(h.build / "current.json") == {"schema": "tachi.plan-pointer/1", "plan_id": res["plan_id"]}

    plan = h.plan_json()
    assert set(plan) == PLAN_KEYS
    assert plan["schema"] == "tachi.plan/1"
    assert (plan["plan_id"], plan["stage"], plan["agent_type"]) == (res["plan_id"], name, AGENT_FOR[name])
    assert ISO_UTC.match(plan["created_utc"])
    assert VERSION.match(plan["tachi_version"]) and plan["tachi_version"] == tachi_version
    assert (plan["batch_size"], plan["unit_count"]) == (4, len(MIXED_IDS))
    assert DATE in plan["params"].values(), "the scoring date is an input, and it is recorded"
    assert plan["retry_budget"] == {"limit": 2 * 4, "used": 0}, "limit is 2 x the planned batch count"
    assert plan["refs"] == h.expected_refs, "the plan holds the pointers once, and is their authority (ruled at W2)"
    assert set(plan["inputs"]) == h.expected_inputs
    assert plan["architecture_warning"] is None, "no --architecture was given, so there is nothing to warn of"

    threats_bytes = h.threats.read_bytes()
    recorded = [v for v in plan["inputs"].values() if v["sha256"] == hashlib.sha256(threats_bytes).hexdigest()]
    assert len(recorded) == 1, "the threats file is a recorded input"
    assert recorded[0]["bytes"] == len(threats_bytes)
    assert Path(recorded[0]["path"]).resolve() == h.threats.resolve()

    assert plan["preimage"] == {h.md: hashlib.sha256(EARLIER_MD).hexdigest(), h.sarif: None}
    assert (h.plan_dir / "preimage" / h.md).read_bytes() == EARLIER_MD
    assert not (h.plan_dir / "preimage" / h.sarif).exists()

    snapshot = plan["out_snapshot"]
    assert isinstance(snapshot, dict), "a small tree is snapshotted (the check is skipped above 20,000 entries)"
    stat = h.threats.stat()
    assert snapshot["threats.md"] == [stat.st_size, stat.st_mtime_ns]

    batches = plan["batches"]
    assert [b["batch_id"] for b in batches] == ["B001", "B002", "B003", "B004"]
    for entry in batches:
        assert set(entry) == BATCH_ENTRY_KEYS
        assert (entry["parent"], entry["attempt"], entry["state"]) == (None, 1, "pending")
        input_file = h.plan_dir / "inputs" / ("%s.json" % entry["batch_id"])
        assert sha256_of(input_file) == entry["input_sha256"]
        bi = h.read_json(input_file)
        assert set(bi) == BATCH_INPUT_KEYS
        assert bi["schema"] == "tachi.batch-input/1"
        assert (bi["plan_id"], bi["batch_id"], bi["stage"], bi["agent_type"]) == (
            res["plan_id"], entry["batch_id"], name, AGENT_FOR[name])
        assert bi["finding_ids"] == entry["finding_ids"] and bi["attempt"] == 1
        assert Path(bi["part_path"]).is_absolute()
        assert Path(bi["part_path"]).resolve() == (h.plan_dir / "parts" / ("%s.a1.json" % entry["batch_id"])).resolve()
        assert bi["tree_paths"] == {}, "only the trees stage names tree paths"
        assert unit_ids(bi["units"]) == entry["finding_ids"]
        assert bi["refs"] == plan["refs"], "each batch input keeps a verbatim copy, for its agent"
        assert DATE in bi["params"].values()

    flat = [w for wave in res["waves"] for w in wave]
    assert [w["batch_id"] for w in flat] == [b["batch_id"] for b in batches]
    for w in flat:
        assert set(w) == {"batch_id", "input_path"}
        assert Path(w["input_path"]).resolve() == (h.plan_dir / "inputs" / ("%s.json" % w["batch_id"])).resolve()


def test_plan_with_no_earlier_output_has_null_preimages_and_copies_nothing(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    assert h.plan_json()["preimage"] == {"risk-scores.md": None, "risk-scores.sarif": None}
    preimage_dir = h.plan_dir / "preimage"
    assert not preimage_dir.exists() or list(preimage_dir.iterdir()) == []


def test_plan_through_the_cli_below_the_stage_size_makes_one_batch(stage, cli, tmp_path):
    """NFR-4: at or below its size a stage plans one batch, so the agent is invoked once (ADR-050 D6)."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:6])
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    printed = res.json
    assert set(printed) == {"plan_id", "plan_digest", "waves"}
    assert [len(wave) for wave in printed["waves"]] == [1]
    plan = h.plan_json()
    assert 1 <= plan["batch_size"] <= 500
    assert plan["unit_count"] == 6 <= plan["batch_size"], "the fixture assumes the stage's size is at least 6"
    assert [b["batch_id"] for b in plan["batches"]] == ["B001"]


@pytest.mark.parametrize("flag", ["--batch-size", "--size", "--max-batch-size"])
def test_a_batch_size_is_not_a_command_line_setting(stage, cli, tmp_path, flag):
    """ADR-050 D6 and S-1: the sizes are constants, not adopter settings. Only the function interface sets one."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:6])
    res = h.plan_cli(flag, "2")
    assert res.code == 2, res.describe()
    assert not (h.build / "current.json").exists()


@pytest.mark.parametrize("variable", ["TACHI_BATCH_SIZE", "BATCH_SIZE", "TACHI_STAGE_BATCH_SIZE", "TACHI_RISK_SCORE_BATCH_SIZE"])
def test_a_batch_size_is_not_an_environment_setting(stage, cli, tmp_path, monkeypatch, variable):
    monkeypatch.setenv(variable, "2")
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:6])
    assert h.plan_cli().code == 0
    assert len(h.plan_json()["batches"]) == 1, "six units fit one batch whatever the environment says"


def test_batch_sizes_are_one_module_level_mapping_of_the_amended_constants(stage):
    """ADR-050 D6's "Amended at W1" table, as the one mapping that T020's sizing check reads. A change to a size is
    an ADR amendment, so it changes the table and this pin in the same commit."""
    assert stage.BATCH_SIZES == {"risk-score": 13, "compensating-controls": 11, "trees": 12}


@pytest.mark.parametrize("name", STAGE_NAMES)
@pytest.mark.parametrize("size", [3, 5, 7])
def test_every_batched_path_gets_two_or_more_balanced_contiguous_batches(stage, cli, tmp_path, monkeypatch, name, size):
    """D3's batch granularity: contiguous runs of the units in S-2 order, balanced to within 1, each unit once."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name)
    h.plan(batch_size=size)
    batches = h.plan_json()["batches"]

    assert len(batches) == math.ceil(len(MIXED_IDS) / size) >= 2
    sizes = [len(b["finding_ids"]) for b in batches]
    assert max(sizes) - min(sizes) <= 1 and max(sizes) <= size
    flat = [fid for b in batches for fid in b["finding_ids"]]
    assert [canon(f) for f in flat] == [canon(f) for f in sorted(MIXED_IDS, key=s2_key)], "S-2 order, T-9 before T-10"
    assert len(set(canon(f) for f in flat)) == len(MIXED_IDS), "every unit is in exactly one batch"
    assert [b["batch_id"] for b in batches] == ["B%03d" % n for n in range(1, len(batches) + 1)]


def test_a_stage_at_its_size_plans_one_batch_and_one_unit_more_plans_two(stage, cli, tmp_path):
    at = Harness(stage, cli, tmp_path / "at", "risk-score")
    at.plan(batch_size=len(MIXED_IDS))
    assert len(at.plan_json()["batches"]) == 1

    over = Harness(stage, cli, tmp_path / "over", "risk-score")
    over.plan(batch_size=len(MIXED_IDS) - 1)
    sizes = [len(b["finding_ids"]) for b in over.plan_json()["batches"]]
    assert sizes == [8, 8], "16 units at a size of 15 balance to 8 and 8, not 15 and 1"


def test_planning_the_same_input_twice_gives_the_same_batches(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=5)
    first = [b["finding_ids"] for b in h.plan_json()["batches"]]
    h.plan(batch_size=5)
    assert [b["finding_ids"] for b in h.plan_json()["batches"]] == first


def test_resolved_findings_are_never_dispatched(stage, cli, tmp_path):
    """The units are the open findings of the reference set. Section 4c's RESOLVED IDs are in no batch."""
    open_ids = ["S-1", "S-2", "T-1", "T-3", "LLM-1", "LLM-4"]
    h = Harness(stage, cli, tmp_path, "risk-score", ids=open_ids, resolved=["T-2", "LLM-9"])
    h.plan(batch_size=2)
    plan = h.plan_json()
    flat = [canon(f) for b in plan["batches"] for f in b["finding_ids"]]
    assert sorted(flat, key=s2_key) == sorted(open_ids, key=s2_key)
    assert "T-2" not in flat and "LLM-9" not in flat
    assert plan["unit_count"] == len(open_ids)


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_batch_inputs_carry_each_units_row_verbatim(stage, cli, tmp_path, monkeypatch, name):
    """Agents read their rows from the batch input, so no layer re-reads ``threats.md`` (D6)."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name)
    h.plan(batch_size=5)
    written = {canon(fid): fid for fid in MIXED_IDS}  # Section 7 spells AGP-01 with a zero, whatever the plan calls it
    for batch_id, entry in h.batches().items():
        units = json.dumps(h.batch_input(batch_id)["units"])
        for fid in entry["finding_ids"]:
            assert "Threat text for %s" % written[canon(fid)] in units
            assert "Mitigation text for %s" % written[canon(fid)] in units


def test_each_plan_is_fresh_and_nothing_under_the_build_directory_is_deleted(stage, cli, tmp_path):
    """D3, retention: a fresh plan ID per invocation, the pointer replaced, nothing deleted (KB 21)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    first = h.plan_id
    first_tree = tree_state(h.plan_dir)
    h.plan(batch_size=4)
    second = h.plan_id

    assert first != second and PLAN_ID.match(first) and PLAN_ID.match(second)
    assert h.read_json(h.build / "current.json")["plan_id"] == second
    assert tree_state(h.build / first) == first_tree
    assert sorted(p.name for p in h.build.iterdir()) == sorted(["current.json", first, second]), "no temporary file is left"


@pytest.mark.parametrize("units,expected", [(16, [16]), (17, [16, 1]), (40, [16, 16, 8])])
def test_plan_waves_hold_at_most_16_batches(stage, cli, tmp_path, units, expected):
    """S-8 and D6: at most 16 in flight per wave, which leaves margin under 20."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, units + 1)])
    res = h.plan(batch_size=1)
    assert [len(wave) for wave in res["waves"]] == expected
    assert len(h.plan_json()["batches"]) == units


# =========================================================================== plan: failures


@pytest.mark.parametrize("variant", ["missing", "empty", "prose"])
def test_plan_exits_2_before_dispatch_on_an_unreadable_section_7(stage, cli, tmp_path, variant):
    """S-12(c): any other unreadable Section 7 ends the run before any agent is dispatched. An empty
    extraction is an error, never a pass (KB 22). The error names the file and the section, and the remedy."""
    h = Harness(stage, cli, tmp_path, "risk-score", section7=variant)
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "waves" not in res.out
    assert not (h.build / "current.json").exists(), "no plan is made"
    assert re.search(r"TACHI\s+RISK[- ]SCORE\s+FAILED", res.err, re.I), res.err
    assert "threats.md" in res.err and re.search(r"Section 7|Recommended Actions", res.err), res.err
    assert "Remedy:" in res.err


def test_plan_reads_a_gfm_escaped_pipe_in_a_section_7_cell_as_a_pipe_and_refuses_a_raw_one_with_the_remedy(stage, cli, tmp_path):
    """P1-3 (the architect's ruling at T070; the PM moved it into PR 1 at W6, Q1). GFM, and GitHub's rendering of ``threats.md``, read ``\\|`` as a
    pipe inside its cell, and the threat-model contract never tells its writer to avoid one. Section 7's reader reads it so, and the plan goes on
    with the cell's text as the unit row holds it, every other value in its own column. A raw ``|`` still shifts every value after it (T067a M1), so
    it ends the run at plan with exit 2, the remedy and no plan."""
    threat = "Threat text for S-2"
    piped = Harness(stage, cli, tmp_path / "escaped", "risk-score")
    original = piped.threats.read_text(encoding="utf-8")
    assert original.count(threat + " |") == 1, "premise: the row's Threat cell"
    piped.threats.write_text(original.replace(threat, "Output piped through cat \\| sh"), encoding="utf-8")
    res = piped.plan_cli()
    assert res.code == 0, res.describe()
    rows = unit_rows(piped)
    assert (rows["S-2"]["threat"], rows["S-2"]["risk_level"], rows["S-2"]["mitigation"]) == ("Output piped through cat | sh", "High", "Mitigation text for S-2")
    assert rows["T-9"]["threat"] == "Threat text for T-9" and len(rows) == len(MIXED_IDS)

    raw = Harness(stage, cli, tmp_path / "raw", "risk-score")
    raw.threats.write_text(raw.threats.read_text(encoding="utf-8").replace(threat, "Output piped through cat | sh"), encoding="utf-8")
    refused = raw.plan_cli()
    assert refused.code == 2, refused.describe()
    assert re.search(r"TACHI\s+RISK[- ]SCORE\s+FAILED", refused.err, re.I) and "more cells than its header" in refused.err, refused.err
    assert "Remedy:" in refused.err and "&#124;" in refused.err and "waves" not in refused.out
    assert not (raw.build / "current.json").exists(), "no plan is made"


def test_a_plan_that_fails_leaves_the_current_pointer_alone(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    pointer = (h.build / "current.json").read_bytes()
    h.threats.write_text(make_threats_md(h.ids, section7="missing"), encoding="utf-8")
    assert h.plan_cli().code == 2
    assert (h.build / "current.json").read_bytes() == pointer


def test_plan_exits_1_when_the_threats_file_is_missing(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    res = h.cli("plan", "--stage", "risk-score", "--out", h.out, "--date", DATE, "--threats", h.out / "absent.md")
    assert res.code == 1, res.describe()
    assert "absent.md" in res.err


@pytest.mark.parametrize(
    "extra",
    [
        ["--stage", "nonsense"],
        ["--date", "2026-13-45"],
        ["--date", "22/11/2026"],
        ["--date", "2026-11-22\n"],  # a trailing newline: the KB 24 class that `$` lets through
        ["--date", ""],
    ],
    ids=["unknown-stage", "impossible-date", "wrong-format", "trailing-newline", "empty-date"],
)
def test_plan_usage_and_validation_failures_exit_2(stage, cli, tmp_path, extra):
    h = Harness(stage, cli, tmp_path, "risk-score")
    argv = {"--stage": "risk-score", "--out": str(h.out), "--date": DATE, "--threats": str(h.threats)}
    argv[extra[0]] = extra[1]
    flat = [item for pair in argv.items() for item in pair]
    res = h.cli("plan", *flat)
    assert res.code == 2, res.describe()
    assert not (h.build / "current.json").exists()


def test_plan_without_threats_exits_2_for_a_batched_stage(stage, cli, tmp_path):
    """``--threats`` is required except for the run-level ``threat-model`` plan (cli.md)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    res = h.cli("plan", "--stage", "risk-score", "--out", h.out, "--date", DATE)
    assert res.code == 2, res.describe()


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_plan_records_the_optional_pointers_as_refs_and_the_risk_scores_file_as_an_input(stage, cli, tmp_path, monkeypatch, name):
    """``contracts/cli.md``'s optional flags reach each batch input as absolute ``refs``, and a file the stage reads is
    a digest-checked input, so a change during the run is caught (D6). The architecture goes through the shared
    resolver (T044), which takes a file below the working directory, so the project root is the working directory.
    The scorer only records ``--risk-scores``, and the controls stage plans from it (T036), so each reads its own file."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name, ids=MIXED_IDS[:6])
    scores = h.out / "risk-scores.md"
    if name == "risk-score":
        scores.write_text("# the scores\n", encoding="utf-8")
    baseline, target = tmp_path / "baseline", tmp_path / "target"
    baseline.mkdir()
    target.mkdir()
    architecture = tmp_path / "architecture.md"
    architecture.write_text("# architecture\n", encoding="utf-8")

    res = h.plan_cli("--risk-scores", scores, "--baseline-dir", baseline, "--architecture", architecture, "--target", target)
    assert res.code == 0, res.describe()
    expected = {"threats": str(h.threats), "risk_scores": str(scores), "baseline_dir": str(baseline),
                "architecture": str(architecture), "target": str(target)}
    assert h.plan_json()["refs"] == expected, "the plan holds them once, as the authority (ruled at W2)"
    assert h.batch_input("B001")["refs"] == expected, "and each batch input keeps a verbatim copy"
    assert h.plan_json()["architecture_warning"] is None
    assert set(h.plan_json()["inputs"]) == {"threats", "risk_scores"}
    scores.write_text("# edited since plan\n", encoding="utf-8")
    assert h.reconcile().code == 2


@pytest.mark.parametrize("name", STAGE_NAMES)
@pytest.mark.parametrize("flag", ["--risk-scores", "--baseline-dir", "--target"])
def test_a_pointer_that_names_nothing_exits_1(stage, cli, tmp_path, name, flag):
    h = Harness(stage, cli, tmp_path, name)
    assert h.plan_cli(flag, tmp_path / "absent").code == 1
    assert not (h.build / "current.json").exists()


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_a_risk_scores_pointer_must_be_a_file_and_a_target_a_directory(stage, cli, tmp_path, name):
    h = Harness(stage, cli, tmp_path, name)
    assert h.plan_cli("--risk-scores", tmp_path).code == 1
    assert h.plan_cli("--target", h.threats).code == 1


def test_an_architecture_candidate_that_is_not_a_file_is_dropped_with_a_warning(stage, cli, tmp_path, monkeypatch):
    """ADR-050 D7's fallback: a stage never stops for the architecture path. The plan records the warning (ruled at W2)."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:6])
    candidate = tmp_path / "docs" / "absent.md"
    res = h.plan_cli("--architecture", candidate)
    assert res.code == 0, res.describe()
    assert "architecture" not in h.batch_input("B001")["refs"] and "architecture" not in h.plan_json()["refs"]
    assert "WARNING" in res.err and "absent.md" in res.err
    warning = h.plan_json()["architecture_warning"]
    assert warning == stage.sc.resolve_explicit(str(candidate), root=os.getcwd())[1], "the resolver's own warning, byte for byte"
    assert warning["code"] == "architecture-path:explicit:missing" and "missing check" in warning["detail"]
    assert "--architecture-path" in warning["detail"], "the detail shortens the candidate to 80 characters, so only stderr is sure to name it"


@pytest.mark.parametrize("flag", ["--risk-scores", "--baseline-dir", "--target", "--threats"])
def test_a_pointer_with_a_forbidden_character_exits_2(stage, cli, tmp_path, flag):
    """Each pointer becomes an absolute path in a document, so it must pass D7's syntactic rule first. ``--architecture``
    is not one of them: the shared resolver judges that candidate, and every refusal of it warns and falls back (ruled at W2)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    argv = ["plan", "--stage", "risk-score", "--out", h.out, "--date", DATE, "--threats", h.threats]
    if flag == "--threats":
        argv[argv.index("--threats") + 1] = str(h.out) + "/a\\b.md"
    else:
        argv += [flag, str(tmp_path) + "/a\\b"]
    res = cli(*argv)
    assert res.code == 2, res.describe()
    assert not (h.build / "current.json").exists()


@pytest.mark.parametrize("size", [0, -1, 501, True, "4"], ids=["zero", "negative", "over-500", "bool", "text"])
def test_plan_stage_refuses_a_batch_size_outside_1_to_500(stage, cli, tmp_path, size):
    h = Harness(stage, cli, tmp_path, "risk-score")
    with pytest.raises(stage.StageError) as info:
        h.plan(batch_size=size)
    assert info.value.code == 2


def test_plan_stage_refuses_a_stage_this_version_does_not_plan(stage, cli, tmp_path):
    """``tachi_parts.STAGE_AGENTS`` names the stages that this version plans, and every other name is refused (ruled at W1). PR 2 added ``trees`` to them, so
    the case is the one name that item O-alpha leaves without a plan: Phase 2 writes records, not parts, and has no stage."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    with pytest.raises(stage.StageError) as info:
        stage.plan_stage(stage="phase2", out=h.out, date=DATE, threats=h.threats)
    assert info.value.code == 2


def test_plan_refuses_more_batches_than_a_batch_id_can_name(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 1001)])
    with pytest.raises(stage.StageError) as info:
        h.plan(batch_size=1)  # 1,000 batches, and a batch ID is B and three digits
    assert info.value.code == 2 and "999" in str(info.value)
    assert not (h.out / ".tachi-build").exists(), "nothing is written before the check"


def test_plan_reads_threats_as_strict_utf8_of_bounded_size(stage, cli, tmp_path, monkeypatch):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.threats.write_bytes(b"\xff\xfe not utf-8")
    assert h.plan_cli().code == 2
    h.threats.write_text(make_threats_md(h.ids), encoding="utf-8")
    monkeypatch.setattr(stage.tp, "MAX_AGENT_INPUT_BYTES", 200)  # D3 step 2's 16 MiB, made small
    res = h.plan_cli()
    assert res.code == 2 and "200" in res.err


def test_plan_refuses_an_out_directory_that_documents_cannot_carry_or_that_is_missing(stage, cli, tmp_path):
    odd = tmp_path / "a`b"
    odd.mkdir()
    (odd / "threats.md").write_text(make_threats_md(MIXED_IDS[:3]), encoding="utf-8")
    res = cli("plan", "--stage", "risk-score", "--out", odd, "--date", DATE, "--threats", odd / "threats.md")
    assert res.code == 2, res.describe()
    assert not (odd / ".tachi-build").exists()
    missing = cli("plan", "--stage", "risk-score", "--out", tmp_path / "nothing", "--date", DATE, "--threats", odd / "threats.md")
    assert missing.code == 1, missing.describe()


def test_a_writer_never_writes_a_document_over_its_cap(stage, cli, tmp_path):
    """Ruled at W1: a batch input is capped at 4 MiB, and a writer never exceeds its own cap. The stop names the cap,
    and the pointer is never replaced, so the failed plan is never the current one."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-1"])
    h.threats.write_text(make_threats_md(["T-1"]).replace("Threat text for T-1", "x" * (4 * 1024 * 1024 + 100)), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "cap" in res.err and "tachi.batch-input/1" in res.err
    assert not (h.build / "current.json").exists()


def test_a_plan_file_over_its_cap_leaves_the_pointer_on_the_earlier_plan(stage, cli, tmp_path, monkeypatch):
    """The pointer is the last thing ``plan`` writes, so a plan that fails part way is never the current one."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    earlier = h.plan_id
    monkeypatch.setitem(stage.tp.MAX_DOCUMENT_BYTES, stage.tp.PLAN_SCHEMA, 100)  # the plan's 8 MiB cap, made small
    res = h.plan_cli()
    assert res.code == 2 and "tachi.plan/1" in res.err, res.describe()
    assert h.read_json(h.build / "current.json")["plan_id"] == earlier


def test_plan_exits_2_when_a_section_7_row_is_malformed(stage, cli, tmp_path):
    """A row with too few cells is dropped by the table reader, which would shrink the reference set without a word.
    The wrapper refuses, naming the line, so no finding is silently left unscored."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["S-1", "S-2", "T-1"])
    lines = h.threats.read_text(encoding="utf-8").split("\n")
    at = next(i for i, line in enumerate(lines) if line.startswith("| S-2 "))
    lines[at] = "| S-2 | NEW | only three cells"
    h.threats.write_text("\n".join(lines), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "malformed row" in res.err and "line %d" % (at + 1) in res.err
    assert not (h.build / "current.json").exists()


def test_a_writer_checks_what_it_writes_against_its_readers_validator(stage, cli, tmp_path, monkeypatch):
    """A document that this step's own reader would refuse is never written: the stop names the document, and the
    pointer is not replaced."""
    h = Harness(stage, cli, tmp_path, "risk-score")

    def refuse(_document):
        raise stage.tp.PartError("invalid", "a synthetic problem")

    monkeypatch.setattr(stage.tp, "validate_plan", refuse)
    res = h.plan_cli()
    assert res.code == 2 and "fails its own contract" in res.err and "a synthetic problem" in res.err, res.describe()
    assert not (h.build / "current.json").exists()


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason="needs an ordinary user: root ignores permission bits")
def test_plan_exits_cleanly_when_an_input_or_the_stage_directory_cannot_be_used(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    scores = h.out / "risk-scores.md"
    scores.write_text("# scores\n", encoding="utf-8")
    scores.chmod(0)
    try:
        res = h.plan_cli("--risk-scores", scores)
        assert res.code == 1 and "cannot read" in res.err, res.describe()
    finally:
        scores.chmod(0o644)

    h.build.mkdir(parents=True)
    h.build.chmod(0o500)  # no write permission: the plan directory can't be made
    try:
        res = h.plan_cli()
        assert res.code == 2 and "cannot make the plan directory" in res.err, res.describe()
    finally:
        h.build.chmod(0o755)
    assert not (h.build / "current.json").exists()


def test_two_spellings_of_one_finding_plan_once_and_warn(stage, cli, tmp_path):
    """D-4: a finding appears once in the reference set. ``maestro-reference``'s shipped Section 7 lists one twice,
    so the first row is used and the repeat is reported, never a reason to refuse a readable file."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["AGP-01", "AGP-1", "T-1"])
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "WARNING" in res.err and "AGP-1" in res.err
    plan = h.plan_json()
    assert plan["unit_count"] == 2
    assert [fid for b in plan["batches"] for fid in b["finding_ids"]] == ["T-1", "AGP-1"]


@pytest.mark.parametrize("link", [".tachi-build", ".tachi-build/risk-score"])
def test_plan_refuses_to_write_through_a_symlinked_build_directory(stage, cli, tmp_path, link):
    """cli.md: an entry writes only under ``--out``, by resolved identity, and no symlink counts (D3, KB 24)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    if link == ".tachi-build":
        (h.out / ".tachi-build").symlink_to(elsewhere, target_is_directory=True)
    else:
        (h.out / ".tachi-build").mkdir()
        (h.out / ".tachi-build" / "risk-score").symlink_to(elsewhere, target_is_directory=True)
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert list(elsewhere.iterdir()) == [], "nothing was written through the link"


def test_every_write_lands_under_the_out_directory(stage, cli, tmp_path):
    """cli.md: an entry writes only under ``--out``. Whatever lies beside the run directory stays as it was,
    and inside it only ``.tachi-build`` and the stage's canonical outputs may change (D3, D4)."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 9)])
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.md").write_text("beside the run directory\n", encoding="utf-8")
    (tmp_path / "elsewhere").mkdir()
    (tmp_path / "elsewhere" / "kept.txt").write_text("kept\n", encoding="utf-8")
    h.earlier()

    def outside():
        return {k: v for k, v in tree_state(tmp_path).items() if not k.startswith("run/")}

    def inside_without_build():
        return {k: v for k, v in tree_state(h.out).items() if not k.startswith(".tachi-build/")}

    before_outside, before_inside = outside(), inside_without_build()
    assert h.plan_cli().code == 0
    assert h.reconcile().code == 3  # halves
    h.write_valid_parts()
    assert h.reconcile().code == 0
    h.render()
    assert h.fail("render-failed").code == 0

    assert outside() == before_outside
    assert inside_without_build() == before_inside, "the failed render was undone, and nothing else was written"


# =========================================================================== reconcile: parts and staleness


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_valid_parts_for_every_batch_reconcile_to_complete(stage, cli, tmp_path, monkeypatch, name):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name)
    h.plan(batch_size=4)
    h.write_valid_parts()
    res = h.reconcile()
    assert res.code == 0, res.describe()
    printed = res.json
    assert set(printed) == RECONCILE_KEYS
    assert printed["status"] == "complete" and printed["waves"] == [] and printed["exhausted"] == []
    assert printed["done"] == ["B001", "B002", "B003", "B004"]  # reading: a list of batch IDs, in plan order
    assert sha256_of(h.plan_dir / "plan.json") == printed["plan_digest"]
    assert {b["state"] for b in h.plan_json()["batches"]} == {"done"}


def test_reconcile_lists_only_the_unfinished_batches(stage, cli, tmp_path):
    """US-1a #4: a resume re-dispatches only the unfinished batches, narrower if the batch overflowed."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    h.write_part("B001")
    h.write_part("B002", mutate=lambda p: p.__setitem__("extra", 1))  # invalid: retried as it is
    h.write_part("B003")
    # B004 wrote nothing: it is missing, so it is halved
    res = h.reconcile()
    assert res.code == 3, res.describe()
    printed = res.json
    assert printed["status"] == "pending" and printed["exhausted"] == []
    assert sorted(printed["done"]) == ["B001", "B003"]
    assert h.pending(printed) == ["B002", "B004-1", "B004-2"]


def test_a_part_from_an_earlier_plan_never_counts(stage, cli, tmp_path):
    """D3: a part counts only if its ``plan_id`` equals the pointer's. A stale part is not deleted either."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    h.write_valid_parts()
    first_id = h.plan_id
    assert h.reconcile().code == 0, "control: the first plan's own parts are valid"
    stale = {b: h.part_path(b).read_bytes() for b in ("B001", "B002")}

    h.plan(batch_size=8)  # a re-run: a fresh plan ID and a fresh pointer
    assert h.plan_id != first_id
    for batch_id, data in stale.items():  # the earlier plan's bytes, at the new plan's part paths
        path = h.part_path(batch_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert res.json["done"] == []
    assert h.pending(res.json) == ["B001", "B002"], "the batches are retried as they are: the part was invalid"
    assert (tmp_path / "run" / ".tachi-build" / "risk-score" / first_id / "parts" / "B001.a1.json").exists()


def test_a_part_from_an_earlier_attempt_never_counts(stage, cli, tmp_path):
    """D3: an earlier attempt's part never counts. An agent that finishes late and writes attempt 1 is ignored."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    h.write_part("B001", mutate=lambda p: p.__setitem__("extra", 1))  # attempt 1 is invalid
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3 and h.pending(res.json) == ["B001"]
    assert h.batch_input("B001")["attempt"] == 2

    late = h.plan_dir / "parts" / "B001.a1.json"
    late.write_text(json.dumps(h.part_for("B001")), encoding="utf-8")  # a valid part, for attempt 1
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert "B001" not in res.json["done"], "the attempt-1 file was never read"
    assert res.json["done"] == ["B002"]
    assert not h.part_path("B001").exists()


def test_a_part_for_the_current_attempt_counts_after_a_retry(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    h.write_part("B001", mutate=lambda p: p.__setitem__("extra", 1))
    h.write_part("B002")
    assert h.reconcile().code == 3
    h.write_part("B001")  # attempt 2, valid
    res = h.reconcile()
    assert res.code == 0, res.describe()
    assert res.json["done"] == ["B001", "B002"]


def test_a_symlinked_part_never_counts(stage, cli, tmp_path):
    """D3 validation step 1: the part is a regular file with no symlink below ``{out}``."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    real = tmp_path / "real-part.json"
    real.write_text(json.dumps(h.part_for("B001")), encoding="utf-8")
    link = h.part_path("B001")
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(real)
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert "B001" not in res.json["done"]


# =========================================================================== exit 2: planner state is checked, not trusted


def _planned(stage, cli, tmp_path, name="risk-score"):
    h = Harness(stage, cli, tmp_path, name)
    h.plan(batch_size=8)
    h.write_valid_parts()
    return h


def test_reconcile_exits_2_after_the_plan_file_is_edited(stage, cli, tmp_path):
    """D3: ``reconcile``, the renderer, ``fail`` and ``close`` refuse a plan file with another digest."""
    h = _planned(stage, cli, tmp_path)
    plan = h.plan_json()
    plan["batch_size"] = 99  # any edit
    (h.plan_dir / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    res = h.reconcile()
    assert res.code == 2, res.describe()


def test_a_whitespace_only_edit_of_the_plan_file_is_a_digest_mismatch_too(stage, cli, tmp_path):
    h = _planned(stage, cli, tmp_path)
    path = h.plan_dir / "plan.json"
    path.write_bytes(path.read_bytes() + b"\n")
    assert h.reconcile().code == 2


@pytest.mark.parametrize("edit", ["units", "part_path", "finding_ids", "attempt"])
def test_reconcile_exits_2_after_a_batch_input_is_edited(stage, cli, tmp_path, edit):
    """D6: each batch input's digest is in the plan, and a change makes ``reconcile`` exit 2. The plan file
    is untouched, so only the batch input's own digest can catch it."""
    h = _planned(stage, cli, tmp_path)
    path = h.plan_dir / "inputs" / "B001.json"
    bi = h.read_json(path)
    if edit == "units":
        bi["units"][0]["tampered"] = True
    elif edit == "part_path":
        bi["part_path"] = str(tmp_path / "elsewhere.json")
    elif edit == "finding_ids":
        bi["finding_ids"] = bi["finding_ids"][:-1]
    else:
        bi["attempt"] = 3
    path.write_text(json.dumps(bi), encoding="utf-8")
    res = h.reconcile()
    assert res.code == 2, res.describe()


def test_reconcile_exits_2_when_plan_disagrees_with_current_json(stage, cli, tmp_path):
    """cli.md: ``--plan`` names the plan ID, and a disagreement with ``current.json`` exits 2."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    old_id, old_digest = h.plan_id, h.digest
    h.plan(batch_size=8)  # the pointer now names the second plan
    assert h.reconcile(plan_id=old_id, digest=old_digest).code == 2
    assert h.reconcile().code == 3, "control: the pointer's own plan reconciles"


@pytest.mark.parametrize(
    "plan_id",
    ["../../etc", "20261122T000000Z-0123456789AB", "20261122T000000Z-0123456789a", "B001", "20261122T000000Z-0123456789ab\n", ""],
    ids=["traversal", "uppercase-hex", "short", "not-a-plan-id", "trailing-newline", "empty"],
)
def test_reconcile_exits_2_on_a_plan_id_outside_the_allow_list(stage, cli, tmp_path, plan_id):
    """D3: IDs pass the allow-list as ASCII full matches before they become paths (KB 24)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    res = h.cli("reconcile", "--stage", "risk-score", "--out", h.out, "--plan", plan_id, "--plan-digest", h.digest)
    assert res.code == 2, res.describe()


@pytest.mark.parametrize("digest", ["0" * 64, "f" * 64, "xyz", "A" * 64, "0" * 63, ""], ids=["wrong", "wrong-2", "not-hex", "uppercase", "short", "empty"])
def test_reconcile_exits_2_on_a_wrong_or_malformed_digest(stage, cli, tmp_path, digest):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    res = h.cli("reconcile", "--stage", "risk-score", "--out", h.out, "--plan", h.plan_id, "--plan-digest", digest)
    assert res.code == 2, res.describe()


def test_reconcile_exits_2_without_a_digest(stage, cli, tmp_path):
    """The check is never optional, or a caller could skip it."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    res = h.cli("reconcile", "--stage", "risk-score", "--out", h.out, "--plan", h.plan_id)
    assert res.code == 2, res.describe()


def test_the_digest_changes_with_the_plan_and_a_stale_one_is_refused(stage, cli, tmp_path):
    """``plan`` and ``reconcile`` print the digest, and the caller passes back the latest one."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    first_digest = h.digest
    res = h.reconcile()  # nothing written: both batches halve, so the plan file is replaced
    assert res.code == 3
    assert h.digest != first_digest and h.digest == sha256_of(h.plan_dir / "plan.json")
    h.write_valid_parts()  # the children's parts
    assert h.reconcile(digest=first_digest).code == 2, "the digest from before the replacement is stale"
    assert h.reconcile().code == 0, "control: the latest digest is accepted"


def test_reconcile_exits_2_after_an_input_changes(stage, cli, tmp_path):
    """D6: a plan records its inputs' digests, and a change makes ``reconcile`` exit 2. The remedy is a re-run."""
    h = _planned(stage, cli, tmp_path)
    h.threats.write_text(make_threats_md(h.ids + ["E-9"]), encoding="utf-8")
    res = h.reconcile()
    assert res.code == 2, res.describe()
    assert re.search(r"re-?run", res.err, re.I), "the stop names its remedy: %r" % res.err


def test_reconcile_exits_2_when_plan_json_is_another_plans_file(stage, cli, tmp_path):
    """The digest can match and the file still be for another plan, so the IDs inside are checked as well."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    first_digest = h.digest
    first_bytes = (h.plan_dir / "plan.json").read_bytes()
    h.plan(batch_size=8)
    (h.plan_dir / "plan.json").write_bytes(first_bytes)  # the first plan's file in the second plan's directory
    res = h.reconcile(digest=first_digest)
    assert res.code == 2, res.describe()


def test_reconcile_exits_2_when_plan_json_is_a_symlink(stage, cli, tmp_path):
    h = _planned(stage, cli, tmp_path)
    real = h.plan_dir / "plan.real"
    (h.plan_dir / "plan.json").rename(real)
    (h.plan_dir / "plan.json").symlink_to(real)
    assert h.reconcile().code == 2


def test_reconcile_exits_2_when_the_pointer_is_not_a_pointer(stage, cli, tmp_path):
    h = _planned(stage, cli, tmp_path)
    (h.build / "current.json").write_text('{"schema": "nope"}', encoding="utf-8")
    assert h.reconcile().code == 2


def test_reconcile_exits_2_when_a_batch_input_becomes_a_symlink_or_an_input_vanishes(stage, cli, tmp_path):
    h = _planned(stage, cli, tmp_path)
    real = tmp_path / "copy-of-input.json"
    path = h.plan_dir / "inputs" / "B001.json"
    real.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(real)  # the same bytes, behind a link
    assert h.reconcile().code == 2

    other = _planned(stage, cli, tmp_path / "second")
    other.threats.unlink()  # an input that vanished is a changed input
    assert other.reconcile().code == 2


def test_reconcile_exits_1_when_the_plan_file_is_missing(stage, cli, tmp_path):
    h = _planned(stage, cli, tmp_path)
    (h.plan_dir / "plan.json").unlink()
    assert h.reconcile().code == 1


def test_reconcile_exits_1_with_no_plan_at_all(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    res = h.cli("reconcile", "--stage", "risk-score", "--out", h.out, "--plan", "20261122T000000Z-0123456789ab",
                "--plan-digest", "0" * 64)
    assert res.code == 1, res.describe()


# =========================================================================== retries: halving, invalid retries, caps


def test_a_missing_part_halves_the_batch_into_two_contiguous_children(stage, cli, tmp_path):
    """D6: on ``missing`` the batch is halved, children ``B001-1`` and ``B001-2``, and a halving counts 2."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)  # B001 and B002, eight units each
    first_digest = h.digest
    h.write_part("B002")  # B001 wrote nothing
    res = h.reconcile()
    assert res.code == 3, res.describe()
    printed = res.json
    assert printed["status"] == "pending" and printed["done"] == ["B002"] and printed["exhausted"] == []
    assert h.pending(printed) == ["B001-1", "B001-2"]

    plan = h.plan_json()
    by_id = {b["batch_id"]: b for b in plan["batches"]}
    parent, first, second = by_id["B001"], by_id["B001-1"], by_id["B001-2"]
    assert parent["state"] == "split"
    assert first["parent"] == second["parent"] == "B001"
    assert (first["attempt"], second["attempt"]) == (2, 2)  # reading: a child's attempt is its parent's plus one
    assert first["state"] == second["state"] == "pending"
    assert first["finding_ids"] + second["finding_ids"] == parent["finding_ids"], "contiguous, in order"
    assert len(first["finding_ids"]) == len(second["finding_ids"]) == 4
    assert plan["retry_budget"] == {"limit": 4, "used": 2}
    for child in (first, second):
        bi = h.batch_input(child["batch_id"])
        assert (bi["attempt"], bi["finding_ids"]) == (2, child["finding_ids"])
        assert Path(bi["part_path"]).name == "%s.a2.json" % child["batch_id"]
        assert unit_ids(bi["units"]) == child["finding_ids"]
        assert sha256_of(h.plan_dir / "inputs" / ("%s.json" % child["batch_id"])) == child["input_sha256"]
    assert printed["plan_digest"] == sha256_of(h.plan_dir / "plan.json") != first_digest

    h.write_part("B001-1")
    h.write_part("B001-2")
    done = h.reconcile()
    assert done.code == 0, done.describe()
    assert sorted(done.json["done"]) == ["B001-1", "B001-2", "B002"]


def test_children_sit_beside_their_parent_so_the_plan_and_done_stay_in_s2_order(stage, cli, tmp_path):
    """``done`` lists finished batches "in plan order" (ruled at W1). A halving puts its children right after the
    parent, so the plan, and ``done``, stay in S-2 order however late each lineage halves."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 17)])
    h.plan(batch_size=4)
    h.write_valid_parts(only=["B001", "B003", "B004"])  # B002 wrote nothing, so it halves
    res = h.reconcile()
    assert res.code == 3 and h.pending(res.json) == ["B002-1", "B002-2"]
    assert [b["batch_id"] for b in h.plan_json()["batches"]] == ["B001", "B002", "B002-1", "B002-2", "B003", "B004"]
    h.write_valid_parts()
    done = h.reconcile()
    assert done.code == 0, done.describe()
    assert done.json["done"] == ["B001", "B002-1", "B002-2", "B003", "B004"]
    flat = [fid for batch_id in done.json["done"] for fid in h.batches()[batch_id]["finding_ids"]]
    assert flat == ["T-%d" % n for n in range(1, 17)], "the finished batches, in plan order, are the units in S-2 order"


def test_an_odd_batch_halves_to_sizes_that_differ_by_one(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 6)])
    h.plan(batch_size=5)
    assert h.reconcile().code == 3
    plan = h.plan_json()
    children = [b for b in plan["batches"] if b["parent"] == "B001"]
    assert sorted(len(b["finding_ids"]) for b in children) == [2, 3]
    assert [f for b in sorted(children, key=lambda b: b["batch_id"]) for f in b["finding_ids"]] == [
        "T-1", "T-2", "T-3", "T-4", "T-5"], "contiguous, in order"


UNPARSEABLE = {
    "not-json": b"I could not finish this batch.",
    "empty-file": b"",
    "invalid-utf8": b'\xff\xfe{"a": 1}',
    "bom": b"\xef\xbb\xbf{}",
    "nan": b'{"schema": "tachi.part/1", "x": NaN}',
    "infinity": b'{"schema": "tachi.part/1", "x": Infinity}',
    "duplicate-keys": b'{"schema": "tachi.part/1", "schema": "tachi.part/1"}',
    "top-level-array": b"[]",
    "thirty-digit-integer": b'{"x": 123456789012345678901234567890}',
    "nested-too-deep": b'{"a":' * 12 + b"1" + b"}" * 12,
    "oversized": b'{"x": "' + b"a" * (512 * 1024 + 1) + b'"}',
}


@pytest.mark.parametrize("kind", sorted(UNPARSEABLE))
def test_an_unparseable_part_halves_the_batch(stage, cli, tmp_path, kind):
    """ADR-050 D3 steps 2 to 4 make a part ``unparseable``, and D6 halves the batch on it."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    h.write_part("B001", raw=UNPARSEABLE[kind])
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert h.pending(res.json) == ["B001-1", "B001-2"]
    assert h.batches()["B001"]["state"] == "split"


def test_a_truncated_part_halves_the_batch(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    whole = json.dumps(h.part_for("B001")).encode("utf-8")
    h.write_part("B001", raw=whole[: len(whole) // 2])
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3 and h.pending(res.json) == ["B001-1", "B001-2"]


@pytest.mark.parametrize("reason", ["output-budget", "input-too-large", "other"])
def test_a_reported_overflow_halves_the_batch(stage, cli, tmp_path, reason):
    """``tachi.overflow/1`` is advisory: a well-formed one is classified ``overflow``, never ``invalid``,
    and triggers the same halving as a missing part (D3, D6)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    h.write_part("B001", raw=json.dumps(h.overflow_object("B001", reason)).encode("utf-8"))
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert h.pending(res.json) == ["B001-1", "B001-2"], "halved, not retried as it was"


INVALID = {
    "another-plans-id": lambda p: p.__setitem__("plan_id", "20200101T000000Z-000000000000"),
    "another-batch": lambda p: p.__setitem__("batch_id", "B999"),
    "wrong-stage": lambda p: p.__setitem__("stage", "trees"),
    "wrong-agent": lambda p: p.__setitem__("agent_type", "tachi-threat-report"),
    "unknown-schema-version": lambda p: p.__setitem__("schema", "tachi.part/2"),
    "unknown-key": lambda p: p.__setitem__("extra", 1),
    "missing-key": lambda p: p.pop("fragments"),
    "finding-ids-short-one": lambda p: p["finding_ids"].pop(),
    "item-for-an-outside-id": lambda p: p["items"][0].__setitem__("finding_id", "S-999"),
    "duplicate-item": lambda p: p["items"].append(dict(p["items"][0])),
    "unknown-item-key": lambda p: p["items"][0].__setitem__("bonus", 1),
    "trailing-newline-id": lambda p: p["items"][0].__setitem__("finding_id", p["items"][0]["finding_id"] + "\n"),
    "unicode-digit-id": lambda p: p["items"][0].__setitem__("finding_id", "S-١"),
}


@pytest.mark.parametrize("kind", sorted(INVALID))
def test_an_invalid_part_is_retried_with_the_same_members(stage, cli, tmp_path, kind):
    """D6: on ``invalid`` the batch is retried as it was, so the ID stays, ``attempt`` rises and a retry costs 1."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    before = h.batches()["B001"]["finding_ids"]
    h.write_part("B001", mutate=INVALID[kind])
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert h.pending(res.json) == ["B001"] and res.json["done"] == ["B002"]

    plan = h.plan_json()
    entry = {b["batch_id"]: b for b in plan["batches"]}["B001"]
    assert (entry["state"], entry["attempt"], entry["parent"], entry["finding_ids"]) == ("pending", 2, None, before)
    assert not [b for b in plan["batches"] if b["parent"] == "B001"], "no children: it was not halved"
    assert plan["retry_budget"] == {"limit": 4, "used": 1}
    bi = h.batch_input("B001")
    assert (bi["attempt"], bi["finding_ids"]) == (2, before)
    assert Path(bi["part_path"]).name == "B001.a2.json"
    assert sha256_of(h.plan_dir / "inputs" / "B001.json") == entry["input_sha256"]


CONTROLS_BREAKS = {
    "row-with-ten-cells": lambda item: item.update(matrix_row=matrix_row_of(matrix_cells(item["finding_id"])[:10])),
    "row-with-twelve-cells": lambda item: item.update(matrix_row=matrix_row_of(matrix_cells(item["finding_id"]) + ["an extra cell"])),
    "row-for-another-finding": lambda item: item.update(matrix_row=matrix_row_of(["S-9999"] + matrix_cells(item["finding_id"])[1:])),
    "body-without-its-effort-estimate": lambda item: item.update(recommendation_body="\n".join(CONTROLS_BODY.split("\n")[:3])),
    "body-with-a-heading": lambda item: item.update(recommendation_body="# The plan\n" + CONTROLS_BODY),
    "effort-that-is-no-level": lambda item: item.update(recommendation_body=CONTROLS_BODY.replace("Medium", "Soon")),
}


@pytest.mark.parametrize("kind", sorted(CONTROLS_BREAKS))
def test_a_controls_part_that_breaks_the_row_or_the_body_structure_is_invalid_and_its_batch_re_dispatched(stage, cli, tmp_path, kind):
    """ADR-050 D2 and D3 step 9: the row's cell count (11) and Threat ID, and the body's four keys, Effort level and lack of a
    heading or table line, are structural. The part reads as invalid, so ``reconcile`` retries the batch as it was (exit 3),
    where the renderer would otherwise fail on it at render time."""
    h = Harness(stage, cli, tmp_path, "compensating-controls")
    h.plan(batch_size=8)  # 16 units: B001 and B002

    h.write_part("B001", mutate=lambda part: CONTROLS_BREAKS[kind](part["items"][0]))
    h.write_part("B002")
    res = h.reconcile()
    assert res.code == 3, res.describe()
    assert h.pending(res.json) == ["B001"] and res.json["done"] == ["B002"]
    entry = h.batches()["B001"]
    assert (entry["state"], entry["attempt"]) == ("pending", 2), "retried as it was: the same members, one attempt higher"
    assert not [b for b in h.plan_json()["batches"] if b["parent"] == "B001"], "not halved"
    assert h.plan_json()["retry_budget"] == {"limit": 4, "used": 1}

    h.write_part("B001")  # attempt 2 holds a valid row and body
    res = h.reconcile()
    assert res.code == 0, res.describe()
    assert res.json["done"] == ["B001", "B002"]


def test_invalid_retries_stop_after_two(stage, cli, tmp_path):
    """P-8: at most 2 retries per lineage, so the third invalid attempt exits 4 and names the batch."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 17)])
    h.plan(batch_size=4)
    h.write_valid_parts(only=["B002", "B003", "B004"])
    bad = lambda p: p.__setitem__("extra", 1)
    h.write_part("B001", mutate=bad)
    assert h.reconcile().code == 3  # attempt 2 next, used 1
    h.write_part("B001", mutate=bad)
    res = h.reconcile()
    assert res.code == 3 and h.batch_input("B001")["attempt"] == 3
    assert h.plan_json()["retry_budget"]["used"] == 2
    h.write_part("B001", mutate=bad)
    res = h.reconcile()
    assert res.code == 4, res.describe()
    assert [b["batch_id"] for b in res.json["exhausted"]] == ["B001"]


def test_the_lineage_cap_stops_a_batch_halved_twice(stage, cli, tmp_path):
    """D6: a batch halves at most twice. The third failure exits 4 with budget to spare, so the cap is
    the lineage's, and the error names the lineage and its IDs."""
    ids = ["T-%d" % n for n in range(1, 17)]
    h = Harness(stage, cli, tmp_path, "risk-score", ids=ids)
    h.plan(batch_size=4)  # B001..B004, limit 8
    h.write_valid_parts(only=["B002", "B003", "B004"])

    res = h.reconcile()  # B001 is missing: halves
    assert res.code == 3 and h.pending(res.json) == ["B001-1", "B001-2"]
    h.write_part("B001-2")
    res = h.reconcile()  # B001-1 is missing: halves again
    assert res.code == 3 and h.pending(res.json) == ["B001-1-1", "B001-1-2"]
    assert {b["attempt"] for b in h.plan_json()["batches"] if b["batch_id"].startswith("B001-1-")} == {3}
    h.write_part("B001-1-2")
    res = h.reconcile()  # B001-1-1 is missing, and no third retry exists
    assert res.code == 4, res.describe()

    printed = res.json
    assert printed["status"] == "exhausted" and printed["waves"] == []
    assert printed["exhausted"] == [{"batch_id": "B001-1-1", "finding_ids": ["T-1"]}]
    plan = h.plan_json()
    assert plan["retry_budget"] == {"limit": 8, "used": 4}, "the budget was not what stopped it"
    assert {b["batch_id"]: b["state"] for b in plan["batches"]}["B001-1-1"] == "failed"
    for text in ("B001-1-1", "T-1", "Remedy:", str(h.plan_dir)):
        assert text in res.err, "the failure message names %r: %s" % (text, res.err)
    assert re.search(r"TACHI\s+RISK[- ]SCORE\s+FAILED", res.err, re.I)


def test_a_second_attempt_that_halves_gives_attempt_three_children(stage, cli, tmp_path):
    """P-8's one counter per lineage: an invalid retry, then a halving, leaves one retry before exhaustion."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 17)])
    h.plan(batch_size=4)
    h.write_valid_parts(only=["B002", "B003", "B004"])
    h.write_part("B001", mutate=lambda p: p.__setitem__("extra", 1))
    assert h.reconcile().code == 3  # attempt 2 of B001, used 1
    res = h.reconcile()  # attempt 2 wrote nothing: halve
    assert res.code == 3 and h.pending(res.json) == ["B001-1", "B001-2"]
    plan = h.plan_json()
    assert {b["attempt"] for b in plan["batches"] if b["parent"] == "B001"} == {3}
    assert plan["retry_budget"] == {"limit": 8, "used": 3}
    assert Path(h.batch_input("B001-1")["part_path"]).name == "B001-1.a3.json"
    assert h.reconcile().code == 4, "attempt 3 has no retry left"


def test_the_stage_budget_is_twice_the_planned_batches_and_a_halving_costs_two(stage, cli, tmp_path):
    """P-8: at most 2 x the planned batch count in retry dispatches. Three batches give a budget of 6, which
    three halvings spend exactly, so the next failure exits 4 although no lineage has hit its cap."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 13)])
    h.plan(batch_size=4)  # B001..B003
    assert h.plan_json()["retry_budget"] == {"limit": 6, "used": 0}
    res = h.reconcile()  # nothing written: all three halve
    assert res.code == 3, res.describe()
    assert len(h.pending(res.json)) == 6
    assert h.plan_json()["retry_budget"] == {"limit": 6, "used": 6}
    assert {b["attempt"] for b in h.plan_json()["batches"] if b["parent"]} == {2}

    res = h.reconcile()  # every child is missing again, and a halving needs 2 more
    assert res.code == 4, res.describe()
    assert res.json["exhausted"], "the budget exhaustion names the batches it stopped"
    assert h.plan_json()["retry_budget"]["used"] <= 6, "the budget is never exceeded"


def test_the_budget_is_checked_before_each_retry_and_never_overspent(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 13)])
    h.plan(batch_size=4)  # limit 6
    h.write_part("B003")
    assert h.reconcile().code == 3  # B001 and B002 halve: used 4
    assert h.plan_json()["retry_budget"] == {"limit": 6, "used": 4}
    h.write_part("B001-2")
    h.write_part("B002-2")  # B001-1 and B002-1 are missing: two halvings would need 4 more, and only 2 remain
    res = h.reconcile()
    assert res.code == 4, res.describe()
    assert h.plan_json()["retry_budget"]["used"] <= 6


def test_with_one_planned_batch_the_first_halving_spends_the_whole_budget(stage, cli, tmp_path):
    """ADR-050 D6, consequences: with one planned batch, the first halving spends the whole budget."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 5)])
    h.plan(batch_size=4)
    assert h.plan_json()["retry_budget"] == {"limit": 2, "used": 0}
    assert h.reconcile().code == 3
    assert h.plan_json()["retry_budget"] == {"limit": 2, "used": 2}
    res = h.reconcile()
    assert res.code == 4, res.describe()


def test_reconcile_waves_hold_at_most_16_batches(stage, cli, tmp_path):
    """S-8: 40 batches that all halve give 80 children, dispatched in waves of at most 16."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 81)])
    h.plan(batch_size=2)  # 40 batches, limit 80
    res = h.reconcile()
    assert res.code == 3, res.describe()
    waves = res.json["waves"]
    assert all(1 <= len(wave) <= 16 for wave in waves)
    flat = [b["batch_id"] for wave in waves for b in wave]
    assert len(flat) == len(set(flat)) == 80
    assert sorted(len(wave) for wave in waves) == [16, 16, 16, 16, 16]
    assert h.plan_json()["retry_budget"] == {"limit": 80, "used": 80}


def test_a_single_unit_batch_cannot_retry_forever(stage, cli, tmp_path):
    """P-8 is why the loop ends: however a batch fails, ``reconcile`` reaches exit 4 within the caps."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-1"])
    h.plan(batch_size=1)
    codes = []
    for _ in range(8):
        res = h.reconcile()
        codes.append(res.code)
        plan = h.plan_json()
        assert plan["retry_budget"]["used"] <= plan["retry_budget"]["limit"]
        if res.code != 3:
            break
    assert codes[-1] == 4 and 0 not in codes, codes


@pytest.mark.parametrize("kind", ["missing", "overflow", "unparseable"])
def test_a_one_unit_batch_retries_with_the_same_member_and_id(stage, cli, tmp_path, kind):
    """Ruled at W1: a one-unit batch can't halve. When it is missing, overflowed or unparseable it is retried with
    the same member and ID, attempt + 1, at a cost of 1, as an invalid retry is. Then the cap ends it."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-1"])
    h.plan(batch_size=1)

    def write_attempt():
        if kind == "overflow":
            h.write_part("B001", raw=json.dumps(h.overflow_object("B001")).encode("utf-8"))
        elif kind == "unparseable":
            h.write_part("B001", raw=b"I could not write this.")

    for attempt in (2, 3):
        write_attempt()
        res = h.reconcile()
        assert res.code == 3 and h.pending(res.json) == ["B001"], res.describe()
        plan = h.plan_json()
        assert [(b["batch_id"], b["attempt"], b["state"], b["parent"]) for b in plan["batches"]] == [("B001", attempt, "pending", None)]
        assert plan["retry_budget"] == {"limit": 2, "used": attempt - 1}
        bi = h.batch_input("B001")
        assert (bi["attempt"], bi["finding_ids"]) == (attempt, ["T-1"])
        assert Path(bi["part_path"]).name == "B001.a%d.json" % attempt
    write_attempt()
    res = h.reconcile()
    assert res.code == 4 and res.json["exhausted"] == [{"batch_id": "B001", "finding_ids": ["T-1"]}], res.describe()


def test_reconcile_after_exhaustion_keeps_exiting_4(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 5)])
    h.plan(batch_size=4)
    assert h.reconcile().code == 3
    first = h.reconcile()
    assert first.code == 4
    again = h.reconcile()
    assert again.code == 4, again.describe()
    assert again.json["exhausted"] == first.json["exhausted"]


# =========================================================================== fail


@pytest.mark.parametrize("reason", FAIL_REASONS)
def test_fail_writes_the_stage_record_with_the_closed_key_set(stage, cli, tmp_path, tachi_version, reason):
    """D4: ``fail`` writes the failed stage record (``contracts/part-files.md`` §5) and prints
    ``{moved, restored, record}``."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    res = h.fail(reason, detail="a synthetic failure for the test")
    assert res.code == 0, res.describe()
    printed = res.json
    assert set(printed) == {"moved", "restored", "record"}
    assert printed["moved"] == [] and printed["restored"] == []
    record_path = h.plan_dir / "stage-record.json"
    assert Path(printed["record"]).resolve() == record_path.resolve()  # reading: the record's path
    rec = h.read_json(record_path)
    check_record(rec, "risk-score", h.plan_id, tachi_version)
    assert rec["error"]["code"] == reason  # reading: the code is the reason
    assert "a synthetic failure for the test" in json.dumps(rec)
    assert rec["batches"]["planned"] == 4


def test_fail_records_the_unrecoverable_lineage(stage, cli, tmp_path, tachi_version):
    """US-1a #5: the error names the stage, the batch, its finding IDs and the remedy."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 5)])
    h.plan(batch_size=4)
    assert h.reconcile().code == 3
    exhausted = h.reconcile()
    assert exhausted.code == 4
    res = h.fail("unrecoverable-batch")
    assert res.code == 0, res.describe()
    rec = h.read_json(h.plan_dir / "stage-record.json")
    check_record(rec, "risk-score", h.plan_id, tachi_version)
    error = rec["error"]
    assert error["batch_id"] in {b["batch_id"] for b in exhausted.json["exhausted"]}
    assert error["finding_ids"] and set(error["finding_ids"]) <= {"T-1", "T-2", "T-3", "T-4"}
    assert isinstance(error["remedy"], str) and error["remedy"].strip()
    assert rec["batches"]["exhausted"] >= 1 and rec["batches"]["split"] == 1


def _lineage_that_ran_out(stage, cli, tmp_path):
    """T-1 to T-16 in four batches. B001's first attempt is invalid, its second is missing so it halves, B001-1's
    part is an overflow object, and everything else is done. Returns the harness once ``reconcile`` has exited 4."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 17)])
    h.plan(batch_size=4)
    h.write_valid_parts(only=["B002", "B003", "B004"])
    h.write_part("B001", mutate=lambda p: p.__setitem__("extra", 1))
    assert h.reconcile().code == 3
    assert h.reconcile().code == 3  # attempt 2 wrote nothing: B001 halves
    h.write_part("B001-2")
    h.write_part("B001-1", raw=json.dumps(h.overflow_object("B001-1")).encode("utf-8"))
    assert h.reconcile().code == 4
    return h


def test_fail_derives_the_retry_history_from_the_parts_on_disk(stage, cli, tmp_path, tachi_version):
    """The stage record's ``overflow_events`` and ``retries`` (NFR-5), and the counts that follow from the plan."""
    h = _lineage_that_ran_out(stage, cli, tmp_path)
    assert h.fail("unrecoverable-batch").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    check_record(rec, "risk-score", h.plan_id, tachi_version)
    assert rec["overflow_events"] == [
        {"batch_id": "B001", "attempt": 1, "kind": "invalid"},
        {"batch_id": "B001", "attempt": 2, "kind": "missing"},
        {"batch_id": "B001-1", "attempt": 3, "kind": "overflow-reported"}]
    assert rec["retries"] == [
        {"batch_id": "B001", "attempt": 1, "cause": "invalid", "children": []},
        {"batch_id": "B001", "attempt": 2, "cause": "missing", "children": ["B001-1", "B001-2"]}]
    assert rec["batches"] == {"planned": 4, "dispatched": 7, "done": 4, "retried": 3, "split": 1, "exhausted": 1}
    assert rec["counts"] == {"units": 16, "open": 16}
    assert (rec["error"]["batch_id"], rec["error"]["finding_ids"]) == ("B001-1", ["T-1", "T-2"])


def test_several_exhausted_lineages_are_all_counted_and_the_first_in_plan_order_is_named(stage, cli, tmp_path):
    """Ruled at W1: ``error`` names the first exhausted lineage in plan order, and ``batches.exhausted`` counts them all.
    The plan keeps children beside their parent, so plan order is S-2 order."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["T-%d" % n for n in range(1, 13)])
    h.plan(batch_size=4)
    assert h.reconcile().code == 3  # all three halve, which spends the whole budget
    exhausted = h.reconcile()
    assert exhausted.code == 4 and len(exhausted.json["exhausted"]) == 6
    assert [b["batch_id"] for b in exhausted.json["exhausted"]] == ["B001-1", "B001-2", "B002-1", "B002-2", "B003-1", "B003-2"]

    assert h.fail("unrecoverable-batch").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["batches"]["exhausted"] == 6
    assert (rec["error"]["batch_id"], rec["error"]["finding_ids"]) == ("B001-1", ["T-1", "T-2"])
    assert "B001-1" in exhausted.err and "6 batches" in exhausted.err, "the message names the first and says how many"


def test_fail_lists_the_undeclared_paths_the_run_left(stage, cli, tmp_path):
    """D4's declared paths: a path that is new or changed since the plan, and that isn't one of the stage's canonical
    files or D3's exact layout, is recorded, sorted. Declared paths are never listed."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=8)
    h.write_part("B001")  # declared: parts/B001.a1.json
    h.render()  # declared: the stage's own canonical files
    (h.plan_dir / "staged").mkdir()
    (h.plan_dir / "staged" / h.md).write_bytes(b"declared\n")
    undeclared = ["gen.py", "scratch/x.txt", "notes.md", ".tachi-build/compensating-controls/x.json",
                  ".tachi-build/risk-score/20200101T000000Z-000000000000/y.json"]
    for relative in undeclared:
        (h.out / relative).parent.mkdir(parents=True, exist_ok=True)
        (h.out / relative).write_text("an improvised file\n", encoding="utf-8")
    inside = ["parts/B001.a9.json", "inputs/not-a-batch.json", "staged/other.md", "extra.txt", "parts/B001.a1.json.bak"]
    for relative in inside:
        (h.plan_dir / relative).write_text("not in D3's layout\n", encoding="utf-8")
    undeclared += [".tachi-build/risk-score/%s/%s" % (h.plan_id, relative) for relative in inside]

    assert h.fail("render-failed").code == 0
    assert h.read_json(h.plan_dir / "stage-record.json")["undeclared_paths"] == sorted(undeclared)


def test_a_record_keeps_at_most_1000_undeclared_paths_and_warns_with_the_full_count(stage, cli, tmp_path):
    """Ruled at W1: a writer never exceeds its cap, and the warning ``undeclared-paths-truncated`` carries the count."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    (h.out / "stray").mkdir()
    for number in range(stage.tp.MAX_UNDECLARED_PATHS + 3):
        (h.out / "stray" / ("f%04d.txt" % number)).write_bytes(b"x")
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == ["stray/f%04d.txt" % n for n in range(1000)]
    assert [w for w in rec["warnings"] if w["code"] == "undeclared-paths-truncated"] == [
        {"code": "undeclared-paths-truncated", "detail": "1003 undeclared paths in all; the first 1000 are listed"}]


def test_a_name_a_record_cannot_hold_is_counted_not_listed(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=8)
    (h.out / "gen.py").write_bytes(b"x")
    (h.out / "back\\slash.txt").write_bytes(b"x")  # D7's path rule refuses a backslash, so no record could hold it
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == ["gen.py"]
    assert [w["code"] for w in rec["warnings"]] == ["undeclared-paths-unrecordable"]


def test_a_plan_with_no_snapshot_skips_the_declared_paths_check_with_a_warning(stage, cli, tmp_path, monkeypatch):
    """ADR-050 D4: the snapshot is skipped, with a warning, above 20,000 files (made 2 here). A name that the plan can't record no longer
    skips it (SA-5, below)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    monkeypatch.setattr(stage.tp, "MAX_SNAPSHOT_ENTRIES", 2)
    for name in ("a.txt", "b.txt"):
        (h.out / name).write_bytes(b"x")  # with threats.md, three files
    res = h.plan_cli()
    assert res.code == 0 and "snapshot is skipped" in res.err and "more than 2 files" in res.err, res.describe()
    assert h.plan_json()["out_snapshot"] is None
    (h.out / "gen.py").write_bytes(b"x")
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == [] and [w["code"] for w in rec["warnings"]] == ["declared-paths-skipped"]


def test_a_snapshot_at_its_cap_is_still_taken(stage, cli, tmp_path, monkeypatch):
    h = Harness(stage, cli, tmp_path, "risk-score")
    monkeypatch.setattr(stage.tp, "MAX_SNAPSHOT_ENTRIES", 2)
    (h.out / "a.txt").write_bytes(b"x")  # threats.md and this: exactly the cap
    assert h.plan_cli().code == 0 and sorted(h.plan_json()["out_snapshot"]) == ["a.txt", "threats.md"]


# ---- SA-5: a name that the plan can't record doesn't switch the declared-paths check off
#
# One name with a colon in its first component, or a backslash, used to make the snapshot None, so a file that an agent wrote later (or a
# repository planted) was never reported. The name is now keyed by a stand-in made from its digest: an odd name that was there at plan time
# is unchanged, and a changed or new one is counted through ``undeclared-paths-unrecordable``, as it is when it turns up later.

ODD_NAMES = ["note:final.txt", "back\\slash.txt", "tick`name.txt"]  # a scheme-like first component, a backslash and a backtick: D7's rule refuses each


def keys_of_odd_names(snapshot):
    return sorted(key for key in snapshot if key.startswith("./unrecordable:"))


def test_an_odd_name_present_at_plan_time_does_not_hide_a_planted_file(stage, cli, tmp_path):
    """Probe C of the advisory: with ``note:final.txt`` in ``--out``, the plan had no snapshot and ``evil.sh`` was never listed."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    for name in ODD_NAMES:
        (h.out / name).write_bytes(b"x" * (len(name) + 1))
    res = h.plan_cli()
    assert res.code == 0 and "snapshot is skipped" not in res.err and "WARNING" not in res.err, res.describe()
    snapshot = h.plan_json()["out_snapshot"]
    assert snapshot is not None and "threats.md" in snapshot and len(keys_of_odd_names(snapshot)) == len(ODD_NAMES)
    assert not any(name in snapshot for name in ODD_NAMES), "no plan holds an odd name itself"
    (h.out / "evil.sh").write_bytes(b"x")
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == ["evil.sh"]
    assert rec["warnings"] == [], "the odd names were there at plan time and are unchanged, so nothing is said of them"


@pytest.mark.parametrize("change", ["a size", "a new odd name"])
def test_an_odd_name_that_changed_or_arrived_since_the_plan_is_counted_not_listed(stage, cli, tmp_path, change):
    h = Harness(stage, cli, tmp_path, "risk-score")
    (h.out / ODD_NAMES[0]).write_bytes(b"x")
    assert h.plan_cli().code == 0
    if change == "a size":
        (h.out / ODD_NAMES[0]).write_bytes(b"xx")
    else:
        (h.out / ODD_NAMES[1]).write_bytes(b"x")
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == []
    assert rec["warnings"] == [{"code": "undeclared-paths-unrecordable", "detail": "1 undeclared paths have names a record can't hold"}]


# Names that D7's rule came to refuse when SA-8 made ``path_problem`` follow step 10's set: a separator, a bidi control and a tag character. A copy of
# the rule's names would go stale each time it changes, so the test below sorts every name by asking ``path_problem`` itself, whichever version of it
# runs. (Before SA-8 these six are ordinary names and keep their own keys. After it they are refused and take a stand-in.)
WIDENED_NAMES = ["bidi" + chr(0x202E) + "name.txt", "separator" + chr(0x2028) + "name.txt", "paragraph" + chr(0x2029) + "name.txt",
                 "mark" + chr(0x200E) + "name.txt", "arabic" + chr(0x061C) + "name.txt", "tag" + chr(0xE0001) + "name.txt"]


def test_every_name_that_the_path_rule_refuses_gets_a_stand_in_whatever_the_rule_is(stage, cli, tmp_path):
    """SA-5 keys by ``path_problem`` and not by a list of cases, so a name that the rule comes to refuse needs no change here: it is a stand-in in
    the plan, an unchanged one is not reported, and a changed one is counted and not listed. A name that the rule accepts keeps its own key, is
    unchanged, and is listed when it changes. The planted file is found either way."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    names = ODD_NAMES + WIDENED_NAMES
    refused = [name for name in names if stage.tp.path_problem(name) is not None]
    accepted = [name for name in names if name not in refused]
    assert set(ODD_NAMES) <= set(refused), "a colon, a backslash and a backtick are refused by every version of the rule"
    for name in names:
        (h.out / name).write_bytes(b"x")
    res = h.plan_cli()
    assert res.code == 0 and "snapshot is skipped" not in res.err, res.describe()
    snapshot = h.plan_json()["out_snapshot"]
    assert snapshot is not None and set(accepted) <= set(snapshot) and not set(refused) & set(snapshot)
    assert len(keys_of_odd_names(snapshot)) == len(refused) and len(snapshot) == 1 + len(names), "threats.md and one key for each name"
    (h.out / "evil.sh").write_bytes(b"x")
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == ["evil.sh"] and rec["warnings"] == [], "nothing else is new or changed"
    for name in names:
        (h.out / name).write_bytes(b"xx")  # every name changes
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == sorted(["evil.sh"] + accepted)
    assert rec["warnings"] == [{"code": "undeclared-paths-unrecordable", "detail": "%d undeclared paths have names a record can't hold" % len(refused)}]


def test_the_stand_in_for_an_odd_name_is_stable_unique_and_valid_in_a_plan(stage):
    """The key is the name's digest, so it doesn't change between runs, two names never share one, and a name that isn't UTF-8 has one too. It
    passes the plan's own path check, which the ``./`` makes possible (the colon is then not in the first component)."""
    ordinary = ["threats.md", "a/b.txt", ".tachi-build/risk-score/current.json"]
    assert [stage._snapshot_key(name) for name in ordinary] == ordinary
    odd = ODD_NAMES + ["bad" + chr(0xDCFF) + ".txt", "tab\tname"]  # a surrogate stands for a byte that no UTF-8 name holds
    keys = [stage._snapshot_key(name) for name in odd]
    assert keys == [stage._snapshot_key(name) for name in odd] and len(set(keys)) == len(odd)
    for key in keys:
        assert re.fullmatch(r"\./unrecordable:[0-9a-f]{64}", key) and stage.tp.path_problem(key) is None and not key.startswith(("/", "../"))


def test_fail_leaves_earlier_outputs_alone_on_a_re_run(stage, cli, tmp_path):
    """KB 21, moment 1, the re-run: an earlier successful run's outputs stay where they are when this run
    fails before it writes anything, and the earlier plan's directory is left whole."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    h.write_valid_parts()
    assert h.reconcile().code == 0
    earlier_plan_dir, earlier_id = h.plan_dir, h.plan_id
    earlier_tree = tree_state(earlier_plan_dir)

    h.plan(batch_size=4)  # the re-run
    res = h.fail("check-failed")
    assert res.code == 0, res.describe()
    assert res.json["moved"] == [] and res.json["restored"] == []
    h.assert_earlier_outputs_untouched()
    assert tree_state(h.build / earlier_id) == earlier_tree
    assert not (h.plan_dir / "failed").exists() or list((h.plan_dir / "failed").iterdir()) == []


def test_fail_leaves_earlier_outputs_alone_on_a_resume(stage, cli, tmp_path):
    """KB 21, moment 2, the resume: the model keeps no state, so a later process fails the plan using only
    the digest the last ``reconcile`` printed. The digest from before that ``reconcile`` is refused."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=8)
    stale = h.digest
    assert h.reconcile().code == 3  # the plan file was replaced by a halving
    before = tree_state(h.out)

    refused = h.fail("unrecoverable-batch", digest=stale)
    assert refused.code == 2, refused.describe()
    assert (h.plan_dir / "stage-record.json").is_file(), "the record is still written (cli.md)"
    assert not (h.plan_dir / "failed").exists() or list((h.plan_dir / "failed").iterdir()) == []

    res = h.fail("unrecoverable-batch")
    assert res.code == 0, res.describe()
    assert res.json["moved"] == [] and res.json["restored"] == []
    h.assert_earlier_outputs_untouched()
    changed = {k for k, v in tree_state(h.out).items() if before.get(k) != v}
    assert all(k.startswith(".tachi-build/") for k in changed), "only the plan's own files may change: %s" % sorted(changed)


def test_fail_leaves_earlier_outputs_alone_after_a_failed_run(stage, cli, tmp_path):
    """KB 21, moment 3, the failed run: an earlier run that failed keeps its quarantined files. A later
    run that fails touches neither them nor the restored canonical files, and ``{out}`` never holds a
    failed file under a name any auto-detect site would take."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    h.render()  # the first run replaced both outputs and then failed
    first = h.fail("render-failed")
    assert first.code == 0, first.describe()
    assert sorted(first.json["moved"]) == sorted([h.md, h.sarif])
    assert sorted(first.json["restored"]) == sorted([h.md, h.sarif])
    first_id, first_failed = h.plan_id, tree_state(h.build / h.plan_id / "failed")
    assert first_failed == {h.md: hashlib.sha256(NEW_MD).hexdigest(), h.sarif: hashlib.sha256(NEW_SARIF).hexdigest()}
    h.assert_earlier_outputs_untouched()

    h.plan(batch_size=4)  # a later run, on the restored outputs
    second = h.fail("check-failed")
    assert second.code == 0 and second.json["moved"] == [] and second.json["restored"] == []
    assert tree_state(h.build / first_id / "failed") == first_failed
    h.assert_earlier_outputs_untouched()
    assert sorted(p.name for p in h.out.iterdir()) == sorted([".tachi-build", "threats.md", h.md, h.sarif])


def test_fail_with_output_dir_touches_only_that_directory(stage, cli, tmp_path):
    """KB 21, moment 4, ``--output-dir``: a run whose ``--out`` isn't the threat model's directory moves and
    restores inside it only. The default directory's outputs, and its ``.tachi-build``, are never touched."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    default_state = tree_state(h.out)

    custom = tmp_path / "custom"
    custom.mkdir()
    (custom / h.md).write_bytes(b"# the custom directory's earlier markdown\n")
    (custom / h.sarif).write_bytes(b'{"custom": "earlier"}\n')
    default, h.out = h.out, custom  # the threat model stays in the default directory, as with --output-dir
    h.plan(batch_size=4)
    (custom / h.md).write_bytes(NEW_MD)  # the custom run's render got part way, then failed
    res = h.fail("render-failed")
    assert res.code == 0, res.describe()
    assert res.json["moved"] == [h.md] and res.json["restored"] == [h.md]
    assert (custom / h.md).read_bytes() == b"# the custom directory's earlier markdown\n"
    assert (custom / h.sarif).read_bytes() == b'{"custom": "earlier"}\n'
    assert tree_state(default) == default_state, "the default directory is as it was, with no .tachi-build"


def test_a_failing_staged_check_changes_nothing(stage, cli, tmp_path):
    """D4: a check that fails on the staged files leaves the canonical files untouched, and ``fail`` then
    finds nothing changed. The staged files stay for diagnosis, as nothing under ``.tachi-build`` is deleted."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    staged = h.plan_dir / "staged"
    staged.mkdir()
    (staged / h.md).write_bytes(NEW_MD)
    (staged / h.sarif).write_bytes(NEW_SARIF)
    res = h.fail("check-failed")
    assert res.code == 0, res.describe()
    assert res.json["moved"] == [] and res.json["restored"] == []
    h.assert_earlier_outputs_untouched()
    assert (staged / h.md).read_bytes() == NEW_MD and (staged / h.sarif).read_bytes() == NEW_SARIF


@pytest.mark.parametrize("changed", ["md", "sarif"])
def test_a_half_applied_pair_is_restored(stage, cli, tmp_path, changed):
    """D4: a renderer that replaced one file of the pair and then failed is undone: the changed file moves to
    ``failed/``, the pre-image copy takes its place, and the file that never changed is not touched."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    h.render(md=changed == "md", sarif=changed == "sarif")
    name = h.md if changed == "md" else h.sarif
    other = h.sarif if changed == "md" else h.md
    new = NEW_MD if changed == "md" else NEW_SARIF

    res = h.fail("render-failed")
    assert res.code == 0, res.describe()
    assert res.json["moved"] == [name] and res.json["restored"] == [name]
    assert (h.plan_dir / "failed" / name).read_bytes() == new
    assert not (h.plan_dir / "failed" / other).exists()
    h.assert_earlier_outputs_untouched()


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
@pytest.mark.parametrize("name", STAGE_NAMES)
def test_plan_copies_each_pre_image_with_the_permission_bits_of_its_canonical_file(stage, cli, tmp_path, monkeypatch, name):
    """P1-2, the rest of SA-4: a pre-image is a copy of an earlier output that ``fail`` writes back where the output was, so the copy carries
    the output's own bits (an adopter's ``chmod 600``) and not the ordinary mode of a new file. Each of the two files keeps its own."""
    monkeypatch.chdir(tmp_path)  # the controls stage reaches threats.md through source_file, which is relative to the working directory
    monkeypatch.setattr(stage.tp, "_UMASK", 0o022)  # a new file is 0644 whatever umask this test runs under, so neither mode below is the ordinary one
    h = Harness(stage, cli, tmp_path, name)
    h.earlier()
    modes = {h.md: 0o600, h.sarif: 0o640}
    for output, mode in modes.items():
        os.chmod(str(h.out / output), mode)
    h.plan(batch_size=4)
    assert {output: (h.plan_dir / "preimage" / output).stat().st_mode & 0o777 for output in modes} == modes
    h.assert_earlier_outputs_untouched()
    assert {output: (h.out / output).stat().st_mode & 0o777 for output in modes} == modes, "the plan changes no output"


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
@pytest.mark.parametrize("name", STAGE_NAMES)
def test_fail_puts_a_pre_image_back_with_the_permission_bits_of_the_file_it_replaces(stage, cli, tmp_path, monkeypatch, name):
    """P1-2, the rest of SA-4: ``fail`` moves a changed output into ``failed/`` and writes the pre-image where the output was, onto a name that
    is no longer there, so the restored file took the ordinary mode and an adopter's ``chmod 600`` was undone by the first failed run. The
    restored file has the earlier output's bits, through the pre-image copy that holds them."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(stage.tp, "_UMASK", 0o022)
    h = Harness(stage, cli, tmp_path, name)
    h.earlier()
    modes = {h.md: 0o600, h.sarif: 0o640}
    for output, mode in modes.items():
        os.chmod(str(h.out / output), mode)
    h.plan(batch_size=4)
    h.render()  # a render got part way: both outputs were replaced
    res = h.fail("render-failed")
    assert res.code == 0, res.describe()
    assert sorted(res.json["moved"]) == sorted(res.json["restored"]) == sorted(modes)
    h.assert_earlier_outputs_untouched()
    assert {output: (h.out / output).stat().st_mode & 0o777 for output in modes} == modes
    assert (h.plan_dir / "failed" / h.md).read_bytes() == NEW_MD, "the failed render is kept for diagnosis"


def test_new_outputs_with_no_earlier_run_are_moved_and_nothing_is_restored(stage, cli, tmp_path):
    """D4, failed outputs: a first run's outputs stay for diagnosis but are marked failed, and no later
    command takes them as input or as a baseline, so they leave the canonical names."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    h.render()
    res = h.fail("render-failed")
    assert res.code == 0, res.describe()
    assert sorted(res.json["moved"]) == sorted([h.md, h.sarif]) and res.json["restored"] == []
    assert not (h.out / h.md).exists() and not (h.out / h.sarif).exists()
    assert (h.plan_dir / "failed" / h.md).read_bytes() == NEW_MD
    assert (h.plan_dir / "failed" / h.sarif).read_bytes() == NEW_SARIF
    kept = ".tachi-build/risk-score/%s/failed/" % h.plan_id
    assert h.read_json(h.plan_dir / "stage-record.json")["outputs"] == [
        {"path": kept + h.md, "sha256": hashlib.sha256(NEW_MD).hexdigest()},
        {"path": kept + h.sarif, "sha256": hashlib.sha256(NEW_SARIF).hexdigest()}]


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_fail_moves_only_files_in_the_stages_closed_set(stage, cli, tmp_path, monkeypatch, name):
    """KB 21's double gate, the name half: only the stage's own canonical names move, whatever else changed."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name)
    h.plan(batch_size=4)
    other_name = OUTPUTS_FOR["compensating-controls" if name == "risk-score" else "risk-score"][0]
    (h.out / other_name).write_bytes(b"another stage's output\n")
    (h.out / "notes.md").write_bytes(b"a stray file\n")
    (h.out / "gen.py").write_bytes(b"print('an improvised script')\n")
    h.render()
    res = h.fail("render-failed")
    assert res.code == 0, res.describe()
    assert sorted(res.json["moved"]) == sorted([h.md, h.sarif])
    assert (h.out / other_name).read_bytes() == b"another stage's output\n"
    assert (h.out / "notes.md").read_bytes() == b"a stray file\n"
    assert (h.out / "gen.py").exists()


@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_fail_refuses_a_symlink_or_a_directory_at_a_canonical_name(stage, cli, tmp_path, kind):
    """KB 21's double gate, the file half: only a regular file directly in ``{out}`` moves. A guard that
    refuses exits 2, and the record is still written."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    victim = tmp_path / "victim.txt"
    victim.write_bytes(b"outside the run directory\n")
    target = h.out / h.md
    if kind == "symlink":
        target.symlink_to(victim)
    else:
        target.mkdir()
        (target / "inner.txt").write_bytes(b"inside a directory\n")
    res = h.fail("render-failed")
    assert res.code == 2, res.describe()
    assert (h.plan_dir / "stage-record.json").is_file()
    assert victim.read_bytes() == b"outside the run directory\n"
    assert target.is_symlink() if kind == "symlink" else (target / "inner.txt").is_file()
    assert not (h.plan_dir / "failed" / h.md).exists()


def test_fail_never_overwrites_a_failed_copy(stage, cli, tmp_path):
    """D4: files move into ``failed/`` with ``os.replace`` and never overwrite. A second move onto an existing
    copy is refused with exit 2, and the first copy survives."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    failed = h.plan_dir / "failed"
    failed.mkdir()
    (failed / h.md).write_bytes(b"the first failure's copy\n")
    h.render(sarif=False)
    res = h.fail("render-failed")
    assert res.code == 2, res.describe()
    assert (failed / h.md).read_bytes() == b"the first failure's copy\n"
    assert (h.out / h.md).read_bytes() == NEW_MD, "a refused move leaves the file where it was"
    assert (h.plan_dir / "stage-record.json").is_file()


def test_fail_refuses_a_failed_directory_that_is_a_file_and_a_move_the_filesystem_refuses(stage, cli, tmp_path, monkeypatch):
    """A refusal is a guard's 2 with the record written, never a traceback, and the changed file stays where it was."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    h.render(sarif=False)
    (h.plan_dir / "failed").write_bytes(b"a file where the directory goes\n")
    res = h.fail("render-failed")
    assert res.code == 2 and res.json["moved"] == [], res.describe()
    assert (h.out / h.md).read_bytes() == NEW_MD and (h.plan_dir / "stage-record.json").is_file()
    (h.plan_dir / "failed").unlink()

    real_replace = os.replace

    def refuse_into_failed(source, destination):
        if "/failed/" in str(destination):
            raise OSError(18, "Invalid cross-device link")
        return real_replace(source, destination)

    monkeypatch.setattr(os, "replace", refuse_into_failed)
    res = h.fail("render-failed")
    assert res.code == 2 and res.json["moved"] == [] and "cross-device" in res.err, res.describe()
    assert (h.out / h.md).read_bytes() == NEW_MD


def test_fail_does_not_restore_a_pre_image_whose_digest_no_longer_matches(stage, cli, tmp_path):
    """D4: the copy goes back only when its digest matches the one the plan recorded."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    (h.plan_dir / "preimage" / h.md).write_bytes(b"# a tampered copy\n")
    h.render(sarif=False)
    res = h.fail("render-failed")
    assert res.code == 2, res.describe()  # a restore that can't happen is a guard's refusal
    assert res.json["moved"] == [h.md] and res.json["restored"] == []
    assert (h.plan_dir / "failed" / h.md).read_bytes() == NEW_MD, "the failed render is still kept for diagnosis"
    assert b"# a tampered copy" not in b"".join(p.read_bytes() for p in h.out.iterdir() if p.is_file())
    record = h.read_json(h.plan_dir / "stage-record.json")
    assert any(w["code"] == "move-refused" and h.md in w["detail"] for w in record["warnings"]), record["warnings"]


def test_fail_exits_2_on_a_digest_mismatch_and_still_writes_the_record(stage, cli, tmp_path, tachi_version):
    """cli.md: ``fail`` exits 2 if the digest differs, and the record is still written. A plan file we
    can't trust moves and restores nothing."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    h.render()
    res = h.fail("render-failed", digest="0" * 64)
    assert res.code == 2, res.describe()
    rec = h.read_json(h.plan_dir / "stage-record.json")
    check_record(rec, "risk-score", h.plan_id, tachi_version)
    assert (h.out / h.md).read_bytes() == NEW_MD and (h.out / h.sarif).read_bytes() == NEW_SARIF
    assert not (h.plan_dir / "failed").exists() or list((h.plan_dir / "failed").iterdir()) == []


@pytest.mark.parametrize(
    "detail",
    ["x" * 501, "red\x1b[31m", "nul\x00byte", "c1\x85control", "bidi\u202eoverride", "mark\u200eleft", "line\u2028separator", "para\u2029separator"],
    ids=["too-long", "escape", "nul", "c1-control", "bidi-override", "bidi-mark", "line-separator", "paragraph-separator"],
)
def test_fail_refuses_a_detail_that_breaks_the_string_rules(stage, cli, tmp_path, detail):
    """cli.md: ``--detail`` is at most 500 characters and is validated as a string field: no control
    character other than a newline or a tab, no bidi control and no line or paragraph separator (D3)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    res = h.fail("check-failed", detail=detail)
    assert res.code == 2, res.describe()


def test_fail_accepts_a_detail_at_the_limit_and_one_with_a_newline_and_a_tab(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    assert h.fail("check-failed", detail="x" * 500).code == 0
    assert h.fail("check-failed", detail="two lines\n\tindented").code == 0


def test_fail_does_not_act_on_a_plan_the_pointer_no_longer_names(stage, cli, tmp_path):
    """A newer plan owns the canonical files now, so an older plan's pre-images are stale. The record is still written."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    older_id, older_digest = h.plan_id, h.digest
    h.render()
    h.plan(batch_size=4)  # the pointer moves to a newer plan
    res = h.fail("render-failed", plan_id=older_id, digest=older_digest)
    assert res.code == 2, res.describe()
    assert res.json["moved"] == [] and res.json["restored"] == []
    assert (h.out / h.md).read_bytes() == NEW_MD and (h.out / h.sarif).read_bytes() == NEW_SARIF
    record = h.read_json(h.build / older_id / "stage-record.json")
    assert [w["code"] for w in record["warnings"]] == ["pointer-mismatch"]


def test_fail_with_a_garbled_pointer_acts_on_nothing(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.earlier()
    h.plan(batch_size=4)
    h.render()
    (h.build / "current.json").write_text("not json", encoding="utf-8")
    res = h.fail("render-failed")
    assert res.code == 2 and res.json["moved"] == []
    assert (h.out / h.md).read_bytes() == NEW_MD


def test_fail_with_an_unreadable_plan_writes_no_record_and_exits_2(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    (h.plan_dir / "plan.json").write_text("{}", encoding="utf-8")
    res = h.fail("check-failed", digest=sha256_of(h.plan_dir / "plan.json"))
    assert res.code == 2, res.describe()
    assert not (h.plan_dir / "stage-record.json").exists()


def test_fail_with_a_missing_out_directory_exits_2(stage, cli, tmp_path):
    """``fail`` has no exit 1, so a directory that isn't there is its 2, like a plan that isn't there."""
    res = cli("fail", "--stage", "risk-score", "--out", tmp_path / "nothing", "--plan", "20261122T000000Z-0123456789ab",
              "--plan-digest", "0" * 64, "--reason", "check-failed")
    assert res.code == 2, res.describe()


def test_fail_stage_refuses_an_unknown_reason_through_the_function_too(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    with pytest.raises(stage.StageError) as info:
        stage.fail_stage("risk-score", h.out, h.plan_id, h.digest, "because")
    assert info.value.code == 2


@pytest.mark.parametrize("reason,fragment", [
    ("agent-not-spawned", "scripts/install.sh"), ("unrecoverable-batch", "report the kept plan directory"),
    ("check-failed", "re-run"), ("render-failed", "re-run")])
def test_fail_prints_d4s_message_with_its_remedy_and_the_kept_directory(stage, cli, tmp_path, reason, fragment):
    """AR-T5: every entry prints ``TACHI <STAGE> FAILED`` on a failure path. ``agent-not-spawned`` names the agent and
    the install remedy (D4's path 1)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    res = h.fail(reason, detail="tachi-risk-scorer")
    assert res.code == 0, res.describe()
    assert re.search(r"^TACHI RISK-SCORE FAILED: ", res.err, re.M) and "Remedy: " in res.err
    assert fragment in res.err and "Kept for diagnosis: %s" % h.plan_dir in res.err
    if reason == "agent-not-spawned":
        assert "Agent: tachi-risk-scorer" in res.err


def test_fail_rejects_an_unknown_reason(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    h.plan(batch_size=4)
    assert h.fail("because").code == 2


def test_fail_with_no_plan_exits_2(stage, cli, tmp_path):
    """``fail`` has no exit 1: with nothing to fail it stops with its own 2, and never runs twice."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    res = h.cli("fail", "--stage", "risk-score", "--out", h.out, "--plan", "20261122T000000Z-0123456789ab",
                "--plan-digest", "0" * 64, "--reason", "check-failed")
    assert res.code == 2, res.describe()


# =========================================================================== architecture-source (FR-E.18, D7)

ARCH_LINE = re.compile(r"^\*\*Architecture source\*\*: `([^`]+)`$")
FENCED_PREAMBLE = (
    "Background reading.\n\n```text\n## 9. A heading-shaped line inside a fence\n"
    "**Architecture source**: `docs/forged/inside-a-fence.md`\n```"
)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A project root with a real architecture file, as the command's working directory."""
    (tmp_path / "docs" / "security").mkdir(parents=True)
    (tmp_path / "docs" / "security" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    (tmp_path / "run").mkdir()
    (tmp_path / "run" / "threats.md").write_text(make_threats_md(MIXED_IDS[:4], preamble=FENCED_PREAMBLE), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def arch_source(cli, architecture="docs/security/architecture.md", threats="run/threats.md"):
    return cli("architecture-source", "--threats", threats, "--architecture", architecture)


def body_lines(text):
    """(index, value, inside a fence) for each line that looks like the carrier line."""
    found, in_fence = [], False
    for index, line in enumerate(text.split("\n")):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        match = ARCH_LINE.match(line)
        if match:
            found.append((index, match.group(1), in_fence))
    return found


def first_heading_outside_fences(text):
    in_fence = False
    for index, line in enumerate(text.split("\n")):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            return index
    raise AssertionError("no heading")


def frontmatter_end(text):
    lines = text.split("\n")
    assert lines[0] == "---"
    return lines.index("---", 1)


def real_lines(text):
    """The carrier lines outside code fences, the only ones that count."""
    return [(i, v) for i, v, fenced in body_lines(text) if not fenced]


def without_blank_lines(text):
    return [line for line in text.split("\n") if line.strip()]


def test_architecture_source_upserts_one_line_between_the_frontmatter_and_the_first_heading(stage, cli, repo):
    """D7 step 6: the line appears once, between the frontmatter and the first ``## `` heading, outside code
    fences. A forged copy inside a fence is not the line, and is left alone."""
    threats = repo / "run" / "threats.md"
    before = threats.read_text(encoding="utf-8")
    res = arch_source(cli)
    assert res.code == 0, res.describe()
    text = threats.read_text(encoding="utf-8")

    assert [value for _, value in real_lines(text)] == ["docs/security/architecture.md"]
    index = real_lines(text)[0][0]
    assert frontmatter_end(text) < index < first_heading_outside_fences(text)
    assert "**Architecture source**: `docs/forged/inside-a-fence.md`" in text, "the fenced copy is not touched"
    kept = [l for l in without_blank_lines(text) if l != "**Architecture source**: `docs/security/architecture.md`"]
    assert kept == without_blank_lines(before), "nothing else in the file changed"


def test_architecture_source_is_idempotent_and_replaces_a_stale_value(stage, cli, repo):
    threats = repo / "run" / "threats.md"
    assert arch_source(cli).code == 0
    first = threats.read_bytes()
    assert arch_source(cli).code == 0 and threats.read_bytes() == first, "a second run changes no byte"

    (repo / "docs" / "other").mkdir()
    (repo / "docs" / "other" / "architecture.md").write_text("# Another\n", encoding="utf-8")
    assert arch_source(cli, "docs/other/architecture.md").code == 0
    assert [v for _, v in real_lines(threats.read_text(encoding="utf-8"))] == ["docs/other/architecture.md"]


def test_architecture_source_collapses_several_lines_to_one(stage, cli, repo):
    """D7: zero matches, or several, read as absent, so the upsert leaves exactly one."""
    threats = repo / "run" / "threats.md"
    lines = threats.read_text(encoding="utf-8").split("\n")
    at = lines.index("## 1. System Overview")
    lines[at:at] = ["**Architecture source**: `docs/one.md`", "", "**Architecture source**: `docs/two.md`", ""]
    threats.write_text("\n".join(lines), encoding="utf-8")
    assert len(real_lines(threats.read_text(encoding="utf-8"))) == 2

    assert arch_source(cli).code == 0
    assert [v for _, v in real_lines(threats.read_text(encoding="utf-8"))] == ["docs/security/architecture.md"]


def test_architecture_source_writes_a_repo_relative_path_for_an_absolute_one(stage, cli, repo):
    """D7 step 2: an absolute path counts only if an ancestor is the working directory, and is made relative."""
    res = arch_source(cli, str(repo / "docs" / "security" / "architecture.md"))
    assert res.code == 0, res.describe()
    assert [v for _, v in real_lines((repo / "run" / "threats.md").read_text(encoding="utf-8"))] == ["docs/security/architecture.md"]


def test_architecture_source_drops_dot_components(stage, cli, repo):
    assert arch_source(cli, "./docs/./security/architecture.md").code == 0
    assert [v for _, v in real_lines((repo / "run" / "threats.md").read_text(encoding="utf-8"))] == ["docs/security/architecture.md"]


def _break(repo, kind):
    """Returns the bad candidate for ``kind``, with whatever it needs on disk."""
    if kind == "symlinked-file":
        (repo / "docs" / "security" / "link.md").symlink_to(repo / "docs" / "security" / "architecture.md")
        return "docs/security/link.md"
    if kind == "symlinked-directory":
        (repo / "docs" / "linked").symlink_to(repo / "docs" / "security", target_is_directory=True)
        return "docs/linked/architecture.md"
    return {
        "missing-file": "docs/security/absent.md",
        "parent-reference": "docs/../docs/security/architecture.md",
        "outside-the-repo": "../outside.md",
        "directory": "docs/security",
        "backslash": "docs\\security\\architecture.md",
        "backtick": "docs/`x`.md",
        "control-byte": "docs/security/arch\x01.md",
        "empty": "",
    }[kind]


BAD_CANDIDATES = [
    "missing-file", "parent-reference", "outside-the-repo", "directory", "backslash", "backtick",
    "control-byte", "empty", "symlinked-file", "symlinked-directory",
]


@pytest.mark.parametrize("kind", BAD_CANDIDATES)
def test_architecture_source_removes_a_stale_line_when_the_resolver_fails(stage, cli, repo, kind):
    """D7 step 6: if the resolver fails, the upsert removes any existing line, so a line the orchestrator wrote
    can't survive. It warns (exit 5, ``contracts/cli.md``), and nothing else in the file changes."""
    threats = repo / "run" / "threats.md"
    assert arch_source(cli).code == 0 and real_lines(threats.read_text(encoding="utf-8"))
    with_line = threats.read_text(encoding="utf-8")
    candidate = _break(repo, kind)

    res = arch_source(cli, candidate)
    assert res.code == 5, res.describe()
    text = threats.read_text(encoding="utf-8")
    assert real_lines(text) == [], "the stale line is gone"
    assert without_blank_lines(text) == [l for l in without_blank_lines(with_line)
                                         if l != "**Architecture source**: `docs/security/architecture.md`"]
    assert res.err.strip(), "a carrier failure warns"
    if kind in ("missing-file", "parent-reference", "outside-the-repo", "directory"):
        assert candidate in res.err + res.out, "the warning names the candidate"


@pytest.mark.parametrize("kind", BAD_CANDIDATES)
def test_architecture_source_with_no_line_and_a_bad_path_changes_nothing(stage, cli, repo, kind):
    threats = repo / "run" / "threats.md"
    before = threats.read_bytes()
    candidate = _break(repo, kind)
    res = arch_source(cli, candidate)
    assert res.code == 5, res.describe()
    assert threats.read_bytes() == before


ARCH_LINE_TEXT = "**Architecture source**: `docs/security/architecture.md`"


def test_architecture_source_prints_what_it_did_and_every_warning(stage, cli, repo):
    """One JSON object: the canonical path it wrote (or null), what it did, and the warnings, each ``{code, detail}``.
    The warning's code is the resolver's own naming (``architecture-path:explicit:<check>``) and its detail names the flag."""
    (repo / "docs" / "other").mkdir()
    (repo / "docs" / "other" / "architecture.md").write_text("# Another\n", encoding="utf-8")
    steps = [
        (("docs/security/architecture.md",), 0, "docs/security/architecture.md", "added"),
        (("docs/security/architecture.md",), 0, "docs/security/architecture.md", "unchanged"),
        (("docs/other/architecture.md",), 0, "docs/other/architecture.md", "replaced"),
        (("docs/other/absent.md",), 5, None, "removed"),
        (("docs/other/absent.md",), 5, None, "unchanged"),
    ]
    for (candidate,), code, written, action in steps:
        res = arch_source(cli, candidate)
        assert res.code == code, res.describe()
        printed = res.json
        assert set(printed) == {"architecture_source", "action", "warnings"}
        assert (printed["architecture_source"], printed["action"]) == (written, action)
        assert (printed["warnings"] != []) == (code == 5)
    warning = printed["warnings"][0]
    assert warning["code"] == "architecture-path:explicit:missing"
    assert "'docs/other/absent.md'" in warning["detail"] and "--architecture-path" in warning["detail"]
    assert warning["detail"] in res.err


@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_architecture_source_edits_only_a_regular_threats_file(stage, cli, repo, kind):
    """The edit replaces the file whole, so a link would be detached from its target and a directory can't be edited."""
    threats = repo / "run" / "threats.md"
    before = threats.read_bytes()
    if kind == "symlink":
        (repo / "run" / "link.md").symlink_to(threats)
        res = arch_source(cli, threats="run/link.md")
        assert (repo / "run" / "link.md").is_symlink()
    else:
        res = arch_source(cli, threats="run")
    assert res.code == 2, res.describe()
    assert re.search(r"^TACHI THREAT-MODEL FAILED: ", res.err, re.M) and "Remedy: " in res.err
    assert threats.read_bytes() == before


def test_architecture_source_refuses_a_threats_file_that_is_not_utf8(stage, cli, repo):
    (repo / "run" / "threats.md").write_bytes(b"# \xff\xfe not utf-8\n")
    res = arch_source(cli)
    assert res.code == 2 and "UTF-8" in res.err, res.describe()


@pytest.mark.parametrize("text,expected", [
    ("", ARCH_LINE_TEXT + "\n"),
    ("# Title\n", "# Title\n" + ARCH_LINE_TEXT + "\n"),
    ("# Title", "# Title\n" + ARCH_LINE_TEXT + "\n"),
    ("---\nk: v\n---\n## 1. A\n", "---\nk: v\n---\n" + ARCH_LINE_TEXT + "\n\n## 1. A\n"),
    ("# Title\n\n## 1. A\n", "# Title\n\n" + ARCH_LINE_TEXT + "\n\n## 1. A\n"),
    ("~~~\n## fake\n~~~\n## 1. A\n", "~~~\n## fake\n~~~\n" + ARCH_LINE_TEXT + "\n\n## 1. A\n"),
    ("# T\n\n    ## code, not a heading\n\n## 1. A\n", "# T\n\n    ## code, not a heading\n\n" + ARCH_LINE_TEXT + "\n\n## 1. A\n"),
], ids=["empty", "no-heading", "no-final-newline", "frontmatter-then-heading", "no-frontmatter", "tilde-fence", "indented-code"])
def test_architecture_source_places_the_line_in_files_of_every_shape(stage, cli, repo, text, expected):
    """D7 item 6: one line between the frontmatter and the first ``## `` heading, outside code fences. A second run
    changes no byte."""
    threats = repo / "run" / "threats.md"
    threats.write_text(text, encoding="utf-8")
    assert arch_source(cli).code == 0
    assert threats.read_text(encoding="utf-8") == expected
    assert arch_source(cli).json["action"] == "unchanged"
    assert threats.read_text(encoding="utf-8") == expected


def test_a_line_that_an_earlier_run_added_comes_out_whole(stage, cli, repo):
    """The removal takes the blank line the insert added, so insert and then a refusal give back the original bytes."""
    threats = repo / "run" / "threats.md"
    original = threats.read_bytes()
    assert arch_source(cli).code == 0 and threats.read_bytes() != original
    assert arch_source(cli, "docs/security/absent.md").code == 5
    assert threats.read_bytes() == original


def test_architecture_source_removes_a_stale_line_from_a_file_with_crlf_endings(stage, cli, repo):
    threats = repo / "run" / "threats.md"
    threats.write_bytes(b"---\r\nk: v\r\n---\r\n\r\n**Architecture source**: `docs/old.md`\r\n\r\n## 1. A\r\n")
    assert arch_source(cli, "docs/security/absent.md").code == 5
    assert threats.read_bytes() == b"---\r\nk: v\r\n---\r\n\r\n## 1. A\r\n"


def test_architecture_source_never_falls_back_to_the_default_path_or_the_body_line(stage, cli, repo):
    """Ruled at W1: it writes from the command's own path only. ``docs/security/architecture.md`` exists, and so does a
    line naming it, yet a refused path writes nothing and removes the line."""
    assert arch_source(cli).code == 0 and real_lines((repo / "run" / "threats.md").read_text(encoding="utf-8"))
    res = arch_source(cli, "docs/security/not-there.md")
    assert res.code == 5 and res.json["architecture_source"] is None
    assert real_lines((repo / "run" / "threats.md").read_text(encoding="utf-8")) == []


def test_architecture_source_treats_a_canonical_spelling_the_line_cannot_carry_as_a_refusal(stage, cli, repo, monkeypatch):
    def cannot_carry(_path):
        raise ValueError("a synthetic problem")

    monkeypatch.setattr(stage.sc, "format_architecture_source_line", cannot_carry)
    res = arch_source(cli)
    assert res.code == 5 and res.json["warnings"][0]["code"] == "architecture-path:explicit:unrepresentable", res.describe()
    assert real_lines((repo / "run" / "threats.md").read_text(encoding="utf-8")) == []


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason="needs an ordinary user: root ignores permission bits")
def test_architecture_source_exits_1_when_it_cannot_write_beside_the_file(stage, cli, repo):
    (repo / "run").chmod(0o500)
    try:
        res = arch_source(cli)
    finally:
        (repo / "run").chmod(0o755)
    assert res.code == 1 and "cannot write" in res.err, res.describe()


def test_architecture_source_exits_1_for_a_missing_threats_file(stage, cli, repo):
    res = arch_source(cli, threats="run/absent.md")
    assert res.code == 1, res.describe()
    assert "absent.md" in res.err


def test_architecture_source_exits_2_on_a_usage_error(stage, cli, repo):
    res = cli("architecture-source", "--threats", "run/threats.md")
    assert res.code == 2, res.describe()


# =========================================================================== --version, --help, the floor


def test_version_prints_the_script_and_interpreter_versions(stage, cli, tachi_version):
    """cli.md: ``--version`` prints the script's version and the interpreter's."""
    import platform

    res = cli("--version")
    assert res.code == 0, res.describe()
    assert tachi_version in res.out and platform.python_version() in res.out, "the version goes to stdout (ruled at W1)"


def test_help_exits_0_and_names_every_command(stage, cli):
    for argv in (["--help"], ["plan", "--help"], ["reconcile", "--help"], ["fail", "--help"], ["architecture-source", "--help"]):
        res = cli(*argv)
        assert res.code == 0, (argv, res.describe())
    assert all(word in cli("--help").out for word in ("plan", "reconcile", "fail", "architecture-source"))


def test_no_command_is_a_usage_error(stage, cli):
    assert cli().code == 2


OLD_PYTHON = namedtuple("version_info", "major minor micro releaselevel serial")(3, 8, 18, "final", 0)


def test_python_below_39_exits_2_naming_the_version_found(stage, cli, monkeypatch, capsys):
    """cli.md and D4: an entry refuses Python below 3.9, with exit 2, and names the version it found, so the
    command's Step 1 stops before any dispatch. A 3.8 interpreter isn't available to CI, so ``sys.version_info``
    is patched. The guard may sit at module level or in ``main``, so both are tried."""
    capsys.readouterr()
    with monkeypatch.context() as patched:  # scoped, so pytest's own reporting never sees a 3.8
        patched.setattr(sys, "version_info", OLD_PYTHON)
        patched.setattr(sys, "version", "3.8.18 (default, Jan  1 2024, 00:00:00) \n[GCC 12.2.0]")
        try:
            module = _load_hyphenated_script("tachi_stage_floor_probe", "tachi-stage.py")
            code = module.main(["--version"])
        except SystemExit as exc:
            code = exc.code
    out, err = capsys.readouterr()
    assert code == 2
    assert "3.8.18" in out + err


def _run_script(*argv):
    return subprocess.run([sys.executable, "-B", str(SCRIPT)] + [str(a) for a in argv],
                          capture_output=True, encoding="utf-8", timeout=SUBPROCESS_TIMEOUT)


def test_exit_codes_come_from_a_real_interpreter(tmp_path):
    """What a process alone shows (H15): the ``__main__`` guard turns ``main``'s result into the exit status,
    one JSON object reaches stdout, and an error reaches stderr alone."""
    out = tmp_path / "run"
    out.mkdir()
    (out / "threats.md").write_text(make_threats_md(MIXED_IDS[:6]), encoding="utf-8")
    base = ["--stage", "risk-score", "--out", out]

    missing = _run_script("plan", *base, "--date", DATE, "--threats", out / "absent.md")
    assert missing.returncode == 1 and missing.stdout == "" and missing.stderr.strip()

    planned = _run_script("plan", *base, "--date", DATE, "--threats", out / "threats.md")
    assert planned.returncode == 0, planned.stderr
    printed = json.loads(planned.stdout)
    plan_args = ["--plan", printed["plan_id"], "--plan-digest", printed["plan_digest"]]

    pending = _run_script("reconcile", *base, *plan_args)
    assert pending.returncode == 3, pending.stderr
    halved = json.loads(pending.stdout)
    assert halved["status"] == "pending"
    for wave in halved["waves"]:
        for batch in wave:
            bi = json.loads(Path(batch["input_path"]).read_text(encoding="utf-8"))
            part = {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": bi["stage"],
                    "agent_type": bi["agent_type"], "finding_ids": bi["finding_ids"],
                    "items": [scorer_item(f) for f in bi["finding_ids"]], "fragments": []}
            Path(bi["part_path"]).parent.mkdir(parents=True, exist_ok=True)
            Path(bi["part_path"]).write_text(json.dumps(part), encoding="utf-8")
    finished = _run_script("reconcile", *base, "--plan", printed["plan_id"], "--plan-digest", halved["plan_digest"])
    assert finished.returncode == 0, finished.stderr
    assert json.loads(finished.stdout)["status"] == "complete"

    version = _run_script("--version")
    assert version.returncode == 0 and (version.stdout + version.stderr).strip()


# =========================================================================== one case per exit code


def _scenario_plan_0(h):
    return h.plan_cli()


def _scenario_plan_1(h):
    return h.cli("plan", "--stage", h.name, "--out", h.out, "--date", DATE, "--threats", h.out / "absent.md")


def _scenario_plan_2(h):
    h.threats.write_text(make_threats_md(h.ids, section7="missing"), encoding="utf-8")
    return h.plan_cli()


def _scenario_reconcile_0(h):
    h.plan(batch_size=4)
    h.write_valid_parts()
    return h.reconcile()


def _scenario_reconcile_1(h):
    h.plan(batch_size=4)
    (h.plan_dir / "plan.json").unlink()
    return h.reconcile()


def _scenario_reconcile_2(h):
    h.plan(batch_size=4)
    return h.reconcile(digest="0" * 64)


def _scenario_reconcile_3(h):
    h.plan(batch_size=4)
    return h.reconcile()


def _scenario_reconcile_4(h):
    h.ids = ["T-1", "T-2", "T-3", "T-4"]
    h.threats.write_text(make_threats_md(h.ids), encoding="utf-8")
    h.plan(batch_size=4)
    assert h.reconcile().code == 3
    return h.reconcile()


def _scenario_fail_0(h):
    h.plan(batch_size=4)
    return h.fail("check-failed")


def _scenario_fail_2(h):
    h.plan(batch_size=4)
    return h.fail("check-failed", digest="0" * 64)


def _scenario_arch_0(h):
    return arch_source(h.cli)


def _scenario_arch_1(h):
    return arch_source(h.cli, threats="run/absent.md")


def _scenario_arch_2(h):
    return h.cli("architecture-source", "--threats", "run/threats.md")


def _scenario_arch_5(h):
    return arch_source(h.cli, "docs/security/absent.md")


def _scenario_version_0(h):
    return h.cli("--version")


EXIT_CASES = [
    ("plan", 0, _scenario_plan_0), ("plan", 1, _scenario_plan_1), ("plan", 2, _scenario_plan_2),
    ("reconcile", 0, _scenario_reconcile_0), ("reconcile", 1, _scenario_reconcile_1),
    ("reconcile", 2, _scenario_reconcile_2), ("reconcile", 3, _scenario_reconcile_3),
    ("reconcile", 4, _scenario_reconcile_4),
    ("fail", 0, _scenario_fail_0), ("fail", 2, _scenario_fail_2),
    ("architecture-source", 0, _scenario_arch_0), ("architecture-source", 1, _scenario_arch_1),
    ("architecture-source", 2, _scenario_arch_2), ("architecture-source", 5, _scenario_arch_5),
    ("--version", 0, _scenario_version_0),
]


@pytest.mark.parametrize("command,code,scenario", EXIT_CASES, ids=["%s-%d" % (c, n) for c, n, _ in EXIT_CASES])
def test_one_case_per_exit_code(stage, cli, tmp_path, monkeypatch, command, code, scenario):
    """contracts/cli.md's table: each (invocation, code) pair has one case here. The code 3 belongs to
    ``reconcile`` alone, so no other invocation may return it. (``--version`` exiting 2 below 3.9 is
    ``test_python_below_39_exits_2_naming_the_version_found``.)"""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:8])
    (tmp_path / "docs" / "security").mkdir(parents=True)
    (tmp_path / "docs" / "security" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    res = scenario(h)
    assert res.code == code, res.describe()
    if command != "reconcile":
        assert res.code != 3


# =========================================================================== scorer planning (T044; ADR-050 D2, D8, D9)

def baseline_scores_md(ids):
    """A legacy ``risk-scores.md`` with one complete row for each ID: what the tolerant reader (R-26) calls a usable row."""
    rows = "".join("| %s | c | t | 7.1 | 6.0 | 6.0 | 6.0 | 6.4 | Medium | 30d | Review |\n" % fid for fid in ids)
    return ("## 2. Scored Threat Table\n\n| ID | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|\n" + rows)


def write_baseline(root, ids, name="prev", content=None):
    """A baseline run directory under the working directory; returns the relative path of its ``threats.md``."""
    run = Path(root) / "baseline-runs" / name
    run.mkdir(parents=True)
    (run / "threats.md").write_text("# an earlier run\n", encoding="utf-8")
    (run / "risk-scores.md").write_bytes(baseline_scores_md(ids).encode("utf-8") if content is None else content)
    return "baseline-runs/%s/threats.md" % name


def routed(stage, cli, tmp_path, monkeypatch, statuses, groups=(), baseline_ids=None, source=None, name="risk-score"):
    """A project whose working directory is ``tmp_path``, with a threats.md of these statuses and groups."""
    Path(tmp_path).mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name, ids=list(statuses))
    if baseline_ids is not None:
        source = write_baseline(tmp_path, baseline_ids)
    h.threats.write_text(make_threats_md(list(statuses), statuses=statuses, groups=groups, baseline_source=source), encoding="utf-8")
    return h


def agent_ids(h):
    """The findings the plan hands to an agent, across every batch, in plan order."""
    return [fid for entry in h.plan_json()["batches"] for fid in entry["finding_ids"]]


ROUTED = {"S-1": "NEW", "T-2": "UNCHANGED", "I-3": "NEW", "D-1": "UNCHANGED", "D-2": "UNCHANGED", "R-1": "UPDATED", "E-1": "UNCHANGED"}
ROUTED_GROUPS = [("CG-1", ["S-1", "T-2", "I-3"])]


def test_the_scorer_plan_sends_only_the_findings_that_need_judgment_to_the_agent(stage, cli, tmp_path, monkeypatch):
    """Non-peers that are NEW or UPDATED, or lack a usable baseline row. S-1 is a primary, T-2 an UNCHANGED peer with a
    row (carried), I-3 a NEW peer (copies S-1), D-1 and E-1 are UNCHANGED with rows, and D-2 has none."""
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1", "R-1", "E-1"])
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert agent_ids(h) == ["S-1", "R-1", "D-2"], "in S-2 order"
    assert h.plan_json()["unit_count"] == 3
    assert [unit["finding_id"] for unit in h.batch_input("B001")["units"]] == ["S-1", "R-1", "D-2"]
    assert "T-2" not in agent_ids(h) and "I-3" not in agent_ids(h) and "D-1" not in agent_ids(h)


def test_the_plan_carries_the_baseline_the_architecture_and_the_command_date(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1"])
    architecture = tmp_path / "docs" / "architecture.md"
    architecture.parent.mkdir()
    architecture.write_text("# architecture\n", encoding="utf-8")
    assert h.plan_cli("--architecture", "docs/architecture.md").code == 0
    refs = h.batch_input("B001")["refs"]
    assert refs == {"threats": str(h.threats), "baseline_dir": str(tmp_path / "baseline-runs" / "prev"), "architecture": str(architecture)}
    assert h.plan_json()["params"] == {"scoring_date": DATE} == h.batch_input("B001")["params"]
    assert set(h.plan_json()["inputs"]) == {"threats", "baseline_risk_scores"}
    assert h.plan_json()["inputs"]["baseline_risk_scores"]["sha256"] == sha256_of(tmp_path / "baseline-runs" / "prev" / "risk-scores.md")


def test_a_baseline_file_that_changes_after_plan_is_caught(stage, cli, tmp_path, monkeypatch):
    """The renderer routes against the baseline the plan routed against, so an edit between the two exits 2 (D3)."""
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1"])
    assert h.plan_cli().code == 0
    (tmp_path / "baseline-runs" / "prev" / "risk-scores.md").write_text(baseline_scores_md(["S-1"]), encoding="utf-8")
    assert h.reconcile().code == 2


def test_the_baseline_sarif_is_a_digest_checked_input_when_there_is_one(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2"])
    (tmp_path / "baseline-runs" / "prev" / "risk-scores.sarif").write_text('{"runs": []}\n', encoding="utf-8")
    assert h.plan_cli().code == 0
    assert set(h.plan_json()["inputs"]) == {"threats", "baseline_risk_scores", "baseline_risk_scores_sarif"}


def test_with_no_baseline_every_non_peer_goes_to_the_agent_and_the_peers_copy_their_primary(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS)
    res = h.plan_cli()
    assert res.code == 0 and "WARNING" not in res.err, "a first run names no baseline, and warns of none"
    assert agent_ids(h) == ["S-1", "R-1", "D-1", "D-2", "E-1"]
    assert "baseline_dir" not in h.batch_input("B001")["refs"] and set(h.plan_json()["inputs"]) == {"threats"}


def test_the_baseline_dir_flag_comes_before_baseline_source(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["D-1"])
    flagged = Path(tmp_path) / "baseline-runs" / "flagged"
    flagged.mkdir()
    (flagged / "risk-scores.md").write_text(baseline_scores_md(["D-2"]), encoding="utf-8")
    assert h.plan_cli("--baseline-dir", "baseline-runs/flagged").code == 0
    assert "D-2" not in agent_ids(h) and "D-1" in agent_ids(h), "the flag's baseline has a row for D-2, and none for D-1"
    assert h.batch_input("B001")["refs"]["baseline_dir"] == str(flagged)


def test_a_file_path_given_as_the_baseline_counts_as_its_directory(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS)
    write_baseline(tmp_path, ["D-1", "D-2"])
    assert h.plan_cli("--baseline-dir", "baseline-runs/prev/risk-scores.md").code == 0
    assert "D-1" not in agent_ids(h) and "D-2" not in agent_ids(h)


@pytest.mark.parametrize("source,reason", [
    ("none (first run — stateless mode)", "free-text"), ("baseline-runs/absent/threats.md", "missing"),
    ("../elsewhere/threats.md", "outside-working-directory"),
])
def test_a_baseline_source_that_does_not_resolve_means_a_fresh_score_and_a_stated_reason(stage, cli, tmp_path, monkeypatch, source, reason):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, source=source)
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "WARNING" in res.err and reason in res.err and "scored fresh" in res.err
    assert agent_ids(h) == ["S-1", "R-1", "D-1", "D-2", "E-1"] and "baseline_dir" not in h.batch_input("B001")["refs"]


def test_a_baseline_flag_outside_the_working_directory_is_refused_with_its_reason(stage, cli, tmp_path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "risk-scores.md").write_text(baseline_scores_md(["D-1"]), encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    h = routed(stage, cli, project, monkeypatch, ROUTED, ROUTED_GROUPS)
    res = h.plan_cli("--baseline-dir", elsewhere)
    assert res.code == 0 and "outside-working-directory" in res.err and "D-1" in agent_ids(h)


def test_a_baseline_directory_without_risk_scores_md_scores_fresh_and_says_why(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["D-1"])
    (tmp_path / "baseline-runs" / "prev" / "risk-scores.md").unlink()
    res = h.plan_cli()
    assert res.code == 0 and "no usable risk-scores.md (missing)" in res.err
    assert "D-1" in agent_ids(h) and h.batch_input("B001")["refs"]["baseline_dir"] == str(tmp_path / "baseline-runs" / "prev")


@pytest.mark.parametrize("content,reason", [(b"\xff\xfe not utf-8", "not-utf8"), (b"# Nothing tabular\n", "no-rows")])
def test_an_unreadable_baseline_counts_as_missing_and_warns_that_its_overrides_were_not_carried(stage, cli, tmp_path, monkeypatch, content, reason):
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS)
    source = write_baseline(tmp_path, [], content=content)
    h.threats.write_text(make_threats_md(list(ROUTED), statuses=ROUTED, groups=ROUTED_GROUPS, baseline_source=source), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "owners, SLAs and dispositions are not carried" in res.err and reason in res.err
    assert agent_ids(h) == ["S-1", "R-1", "D-1", "D-2", "E-1"] and "baseline_risk_scores" not in h.plan_json()["inputs"]


def test_a_plan_with_nothing_for_an_agent_has_no_batches_and_reconciles_as_complete(stage, cli, tmp_path, monkeypatch):
    statuses = {"S-1": "UNCHANGED", "T-2": "UNCHANGED", "D-1": "UNCHANGED"}
    h = routed(stage, cli, tmp_path, monkeypatch, statuses, [("CG-1", ["S-1", "T-2"])], baseline_ids=list(statuses))
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert res.json["waves"] == []
    plan = h.plan_json()
    assert (plan["unit_count"], plan["batch_size"], plan["batches"], plan["retry_budget"]) == (0, None, [], {"limit": 0, "used": 0})
    done = h.reconcile()
    assert done.code == 0 and done.json["status"] == "complete" and done.json["waves"] == [] and done.json["done"] == []


def test_the_controls_stage_is_not_routed_by_the_scorer_rules(stage, cli, tmp_path, monkeypatch):
    """Controls get every scored open finding (D2), peers included, whatever a scorer baseline holds (T036 plans them)."""
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1"], name="compensating-controls")
    assert h.plan_cli().code == 0
    assert agent_ids(h) == sorted(ROUTED, key=s2_key) and h.plan_json()["unit_count"] == len(ROUTED)


def test_a_reused_id_is_scored_fresh_never_carried(stage, cli, tmp_path, monkeypatch):
    """Ruling B: a NEW finding whose ID the baseline used goes to the agent, however good that baseline row looks."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW", "D-1": "UNCHANGED"}, baseline_ids=["S-1", "D-1"])
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1"]


def test_the_planner_and_the_renderers_function_agree_on_who_is_carried(stage, cli, tmp_path, monkeypatch):
    """Both call ``tachi_scoring_rules.route_scorer_units`` (D2), so the plan's units are exactly its ``to_agent``."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers
    import tachi_scoring_rules as rules

    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1", "R-1", "E-1"])
    assert h.plan_cli().code == 0
    text = h.threats.read_text(encoding="utf-8")
    rows = tachi_parsers.parse_reference_set(text)["open"]
    groups = tachi_parsers.parse_correlation_groups(text, member_ids=[row["id"] for row in rows])["groups"]
    baseline = rules.read_baseline_scores(tmp_path / "baseline-runs" / "prev" / "risk-scores.md")
    routing = rules.route_scorer_units(rows, groups=groups, baseline=baseline)
    assert set(agent_ids(h)) == set(routing.to_agent) and set(routing.carried) == {"T-2", "D-1", "E-1"}


# ---- S-12(b): a form that lacks delta_status takes each status from the baseline (ruled at W2; ADR-050 D9)

def without_status_column(text):
    """``threats.md`` with Section 7's Status column removed: the drift form that leaves ``delta_status`` out of every row."""
    lines, inside = [], False
    for line in text.split("\n"):
        inside = inside or line.startswith("## 7.")
        if inside and line.startswith("|"):
            cells = line.split("|")
            del cells[2]
            line = "|".join(cells)
        lines.append(line)
    return "\n".join(lines)


def drifted(stage, cli, tmp_path, monkeypatch, statuses, groups=(), baseline_ids=None):
    """``routed``'s project with its Section 7 rewritten to the form that has no Status column."""
    h = routed(stage, cli, tmp_path, monkeypatch, statuses, groups, baseline_ids=baseline_ids)
    h.threats.write_text(without_status_column(h.threats.read_text(encoding="utf-8")), encoding="utf-8")
    assert "Status" not in h.threats.read_text(encoding="utf-8").split("## 7.")[1]
    return h


def test_a_form_without_a_status_column_carries_a_finding_the_baseline_has_a_usable_row_for_and_scores_the_rest_fresh(
        stage, cli, tmp_path, monkeypatch):
    """The baseline decides, in ``route_scorer_units``: UNCHANGED when it holds an open row for the ID, NEW otherwise.
    R-1 would be UPDATED in the table form and go to the agent. Without a status it is carried like the rest (ruled at W2:
    deriving UPDATED would re-score every drift-form finding). I-3 is a peer with no row, so it copies its primary."""
    h = drifted(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1", "R-1", "E-1"])
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert agent_ids(h) == ["S-1", "D-2"], "S-1 and D-2 have no row: NEW, and scored fresh"
    assert h.plan_json()["unit_count"] == 2


def test_a_form_without_a_status_column_and_with_no_baseline_scores_every_non_peer_fresh(stage, cli, tmp_path, monkeypatch):
    h = drifted(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS)
    assert h.plan_cli().code == 0
    assert agent_ids(h) == ["S-1", "R-1", "D-1", "D-2", "E-1"], "every status is NEW, and the peers T-2 and I-3 copy S-1"


def test_an_id_that_only_the_baselines_resolved_section_lists_is_new_in_a_form_without_a_status(stage, cli, tmp_path, monkeypatch):
    """D9: the baseline supplies a status only from a usable open row, never from a RESOLVED one (§2a)."""
    statuses = {"S-1": "NEW", "T-2": "UNCHANGED", "D-1": "UNCHANGED"}
    h = routed(stage, cli, tmp_path, monkeypatch, statuses)
    resolved = ("\n## 2a. Resolved Findings\n\n| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA "
                "| Disposition | Status | Owner | Review Date | Flags |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| D-1 | inherited | c | t | 7.1 | 6.0 | 6.0 | 6.0 | 6.4 | Medium | 30d | Review | RESOLVED | alice | 2026-10-01 | resolved |\n")
    source = write_baseline(tmp_path, [], content=(baseline_scores_md(["T-2"]) + resolved).encode("utf-8"))
    h.threats.write_text(without_status_column(make_threats_md(list(statuses), statuses=statuses, baseline_source=source)), encoding="utf-8")
    assert h.plan_cli().code == 0
    assert agent_ids(h) == ["S-1", "D-1"], "T-2 has an open row and is carried; D-1 has only a resolved one, so it is NEW"


def test_a_form_without_a_status_column_is_routed_as_the_routing_function_routes_it(stage, cli, tmp_path, monkeypatch):
    """The planner passes the reference set's own ``lacking`` map, so the renderer can pass the same one and agree (D2)."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers
    import tachi_scoring_rules as rules

    h = drifted(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1", "R-1", "E-1"])
    assert h.plan_cli().code == 0
    reference = tachi_parsers.parse_reference_set(h.threats.read_text(encoding="utf-8"))
    assert set(reference["lacking"]) == set(ROUTED) and all("delta_status" in names for names in reference["lacking"].values())
    groups = tachi_parsers.parse_correlation_groups(h.threats.read_text(encoding="utf-8"), member_ids=[row["id"] for row in reference["open"]])["groups"]
    baseline = rules.read_baseline_scores(tmp_path / "baseline-runs" / "prev" / "risk-scores.md")
    routing = rules.route_scorer_units(reference["open"], groups=groups, baseline=baseline, lacking=reference["lacking"])
    assert set(agent_ids(h)) == set(routing.to_agent) == {"S-1", "D-2"}
    assert routing.status == {"S-1": "NEW", "T-2": "UNCHANGED", "I-3": "NEW", "D-1": "UNCHANGED", "D-2": "NEW", "R-1": "UNCHANGED", "E-1": "UNCHANGED"}


# ---- the architecture pointer goes through the shared resolver (D7)

def test_the_architecture_is_recorded_in_its_canonical_absolute_spelling(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "architecture.md").write_text("# a\n", encoding="utf-8")
    for given in ("docs/architecture.md", "./docs//architecture.md", str(tmp_path / "docs" / "architecture.md")):
        res = h.plan_cli("--architecture", given)
        assert res.code == 0 and "WARNING" not in res.err, given
        assert h.batch_input("B001")["refs"]["architecture"] == str(tmp_path / "docs" / "architecture.md"), given
        assert h.plan_json()["refs"]["architecture"] == str(tmp_path / "docs" / "architecture.md") and h.plan_json()["architecture_warning"] is None, given


@pytest.mark.parametrize("kind", ["symlink", "outside", "directory", "missing", "parent"])
def test_an_architecture_the_resolver_refuses_is_dropped_with_its_check_named(stage, cli, tmp_path, monkeypatch, kind):
    project = tmp_path / "project"
    h = routed(stage, cli, project, monkeypatch, {"S-1": "NEW"})
    (project / "docs").mkdir()
    real = project / "docs" / "architecture.md"
    real.write_text("# a\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("# elsewhere\n", encoding="utf-8")
    given, check = {
        "symlink": ("docs/link.md", "symlink"), "outside": (str(outside), "outside-root"), "directory": ("docs", "not-a-regular-file"),
        "missing": ("docs/absent.md", "missing"), "parent": ("docs/../docs/architecture.md", "parent-reference"),
    }[kind]
    if kind == "symlink":
        try:
            (project / "docs" / "link.md").symlink_to(real)
        except OSError:  # pragma: no cover
            pytest.skip("this platform cannot create a symlink")
    res = h.plan_cli("--architecture", given)
    assert res.code == 0, res.describe()
    assert "architecture" not in h.batch_input("B001")["refs"] and "architecture" not in h.plan_json()["refs"]
    assert "WARNING" in res.err and check in res.err
    # The plan records the resolver's own warning, so the renderer's record and the plan's agree on its code and text (D7).
    expected = stage.sc.resolve_explicit(given, root=os.getcwd())[1]
    assert h.plan_json()["architecture_warning"] == expected
    assert expected["code"] == "architecture-path:explicit:%s" % check and "--architecture-path" in expected["detail"]


@pytest.mark.parametrize("given,check", [
    ("docs/a\\b.md", "backslash"), ("docs/a`b.md", "backtick"), ("docs/a\nb.md", "control-char"), ("docs/a\tb.md", "control-char"),
    ("", "empty"), ("https://example.invalid/a.md", "scheme"), ("C:docs/a.md", "drive-letter"),
], ids=["backslash", "backtick", "newline", "tab", "empty", "scheme", "drive-letter"])
def test_a_syntactically_refused_architecture_warns_and_falls_back_where_it_used_to_exit_2(stage, cli, tmp_path, monkeypatch, given, check):
    """Ruled at W2: ``plan`` no longer pre-checks ``--architecture`` with ``path_problem``. Every refusal of the candidate, a
    control character, backslash or backtick included, is left out of ``refs``, printed on stderr and recorded, and ``plan``
    exits 0, because nothing in D7 stops a run (``architecture-source`` already treats them alike)."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    res = h.plan_cli("--architecture", given)
    assert res.code == 0, res.describe()
    assert "architecture" not in h.plan_json()["refs"] and "architecture" not in h.batch_input("B001")["refs"]
    assert h.plan_json()["architecture_warning"] == {"code": "architecture-path:explicit:%s" % check, "detail": h.plan_json()["architecture_warning"]["detail"]}
    assert "--architecture-path" in h.plan_json()["architecture_warning"]["detail"]
    lines = [line for line in res.err.splitlines() if line.startswith("WARNING")]
    assert lines == ["WARNING: the architecture path %r is not used (%s), so it is not passed to the agents" % (given, check)], (
        "stderr names the candidate escaped, so a newline or a tab shows as an escape and the line stays one line")
    assert h.reconcile().code == 3, "the plan is a working plan: its one batch still waits for its agent"


def test_the_stderr_line_names_the_whole_candidate_and_the_recorded_warning_the_resolvers_short_form(stage, cli, tmp_path, monkeypatch):
    """The resolver shortens the candidate to 80 characters of its ``repr``, which could cut a long temporary path, so the
    planner's own stderr line keeps it whole, and only the recorded warning uses the resolver's text (ruled at W2)."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    given = "docs/" + "x" * 150 + ".md"
    res = h.plan_cli("--architecture", given)
    assert res.code == 0, res.describe()
    assert repr(given) in res.err
    detail = h.plan_json()["architecture_warning"]["detail"]
    assert repr(given)[:80] in detail and repr(given)[:81] not in detail and given not in detail
    assert detail == stage.sc.resolve_explicit(given, root=os.getcwd())[1]["detail"]


def test_a_candidate_the_working_directory_cannot_carry_exits_2_as_every_other_unacceptable_path_does(stage, cli, tmp_path, monkeypatch):
    """The candidate is fine, and the working directory it resolves under holds a backtick, which no document can carry. That
    is an environment fault like ``--out`` and ``--threats``, so it exits 2 before anything is written, not a warning."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["S-1"])
    odd = tmp_path / "a`b"
    (odd / "docs").mkdir(parents=True)
    (odd / "docs" / "architecture.md").write_text("# a\n", encoding="utf-8")
    monkeypatch.chdir(odd)
    res = h.plan_cli("--architecture", "docs/architecture.md")
    assert res.code == 2, res.describe()
    assert "backtick" in res.err and not (h.build / "current.json").exists()


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_a_refused_architecture_is_recorded_in_the_plan_for_either_stage(stage, cli, tmp_path, monkeypatch, name):
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"}, name=name)
    assert h.plan_cli("--architecture", "docs/absent.md").code == 0
    assert h.plan_json()["architecture_warning"]["code"] == "architecture-path:explicit:missing"
    assert h.plan_json()["architecture_warning"] == stage.sc.resolve_explicit("docs/absent.md", root=os.getcwd())[1]


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_with_no_architecture_flag_the_plan_carries_no_architecture_pointer_on_either_stage(stage, cli, tmp_path, monkeypatch, name):
    """ADR-050 D7, ruled at W3: ``refs.architecture`` is the ``--architecture`` flag alone, on both stages. Here the threat model's body line
    names a live file that D7's chain accepts (the run directory holds the snapshot, so the name check passes), and still the plan holds no
    pointer and no warning. The agents read the run's snapshot, and the renderer resolves the chain itself, which is how its URI keeps the
    body line's warnings. A planner that filled the pointer from the chain would turn that line into an explicit candidate."""
    statuses = {"S-1": "NEW", "T-2": "NEW"}
    h = routed(stage, cli, tmp_path, monkeypatch, statuses, name=name)
    (tmp_path / "docs" / "security").mkdir(parents=True)
    (tmp_path / "docs" / "security" / "architecture.md").write_text("# the live source\n", encoding="utf-8")
    (h.out / "architecture.md").write_text("# the run's snapshot\n", encoding="utf-8")
    text = make_threats_md(list(statuses), statuses=statuses, preamble="**Architecture source**: `docs/security/architecture.md`\n")
    h.threats.write_text(text, encoding="utf-8")
    chain = stage.sc.resolve_architecture(None, threats_text=text, run_dir=str(h.out), root=str(tmp_path))
    assert chain.source == "body-line" and chain.warnings == (), "the premise: the chain would accept this body line"
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "architecture" not in h.plan_json()["refs"] and h.plan_json()["architecture_warning"] is None
    assert "architecture" not in h.batch_input("B001")["refs"] and "architecture" not in res.err


def test_an_architecture_pathlike_candidate_resolves_as_its_string_does(stage, cli, tmp_path, monkeypatch):
    """The function interface takes a ``Path`` as the render tests pass one; the warning names the path as text."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "architecture.md").write_text("# a\n", encoding="utf-8")
    h.plan(architecture=tmp_path / "docs" / "architecture.md")
    assert h.plan_json()["refs"]["architecture"] == str(tmp_path / "docs" / "architecture.md") and h.plan_json()["architecture_warning"] is None
    h.plan(architecture=tmp_path / "docs" / "absent.md")
    assert h.plan_json()["architecture_warning"]["code"] == "architecture-path:explicit:missing"
    assert repr(str(tmp_path / "docs" / "absent.md"))[:80] in h.plan_json()["architecture_warning"]["detail"]


# ---- the plan holds the pointers: refs and architecture_warning are plan-level (ruled at W2)

def test_a_plan_with_nothing_for_an_agent_keeps_its_pointers_and_its_architecture_warning(stage, cli, tmp_path, monkeypatch):
    """Why ``refs`` moved to the plan: an all-carried run has no batch input, so pointers kept only there were lost, and the
    renderer's URI fell back to the body line or the default. That re-keys every alert if it differs from an earlier run's."""
    statuses = {"S-1": "UNCHANGED", "T-2": "UNCHANGED"}
    h = routed(stage, cli, tmp_path, monkeypatch, statuses, baseline_ids=list(statuses))
    (tmp_path / "docs").mkdir()
    architecture = tmp_path / "docs" / "architecture.md"
    architecture.write_text("# a\n", encoding="utf-8")
    assert h.plan_cli("--architecture", "docs/architecture.md").code == 0
    plan = h.plan_json()
    assert plan["batches"] == [] and plan["unit_count"] == 0, "nothing for an agent, so no batch input exists"
    assert plan["refs"] == {"threats": str(h.threats), "baseline_dir": str(tmp_path / "baseline-runs" / "prev"), "architecture": str(architecture)}
    assert plan["architecture_warning"] is None
    assert not list((h.plan_dir / "inputs").iterdir())

    assert h.plan_cli("--architecture", "docs/absent.md").code == 0
    plan = h.plan_json()
    assert plan["batches"] == [] and "architecture" not in plan["refs"] and "baseline_dir" in plan["refs"]
    assert plan["architecture_warning"]["code"] == "architecture-path:explicit:missing"


def test_the_plan_is_the_authority_for_refs_and_a_retry_copies_the_plans_not_its_parents(stage, cli, tmp_path, monkeypatch):
    """Ruled at W2: ``reconcile`` writes each retry's input from ``plan["refs"]``. The parent input here names another
    pointer (written consistently, so its digest checks out), and neither a halving nor an ``invalid`` retry takes it."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW", "T-2": "NEW", "D-1": "NEW", "E-1": "NEW"})
    h.plan(batch_size=2)   # B001 holds S-1 and T-2, B002 holds D-1 and E-1, and the budget is four
    parent = h.plan_dir / "inputs" / "B001.json"
    body = json.loads(parent.read_text(encoding="utf-8"))
    body["refs"] = {"threats": str(h.threats) + ".parent"}
    parent.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan = h.plan_json()
    plan["batches"][0]["input_sha256"] = sha256_of(parent)
    (h.plan_dir / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    h.digest = sha256_of(h.plan_dir / "plan.json")

    h.write_part("B002")
    assert h.reconcile().code == 3, "B001 has no part: it is halved into B001-1 and B001-2"
    for child in ("B001-1", "B001-2"):
        assert h.batch_input(child)["refs"] == plan["refs"] == {"threats": str(h.threats)}, child

    h.write_part("B001-1", mutate=lambda part: part.update(finding_ids=["T-2"]))   # a part for the wrong finding: invalid
    h.write_part("B001-2")
    assert h.reconcile().code == 3, "B001-1 is retried as it is, at attempt 3"
    assert h.batch_input("B001-1")["attempt"] == 3 and h.batch_input("B001-1")["refs"] == plan["refs"]


def test_fail_lists_the_plans_architecture_warning_first_when_the_plan_checks_out(stage, cli, tmp_path, monkeypatch):
    """D7: the explicit candidate's warning comes first in every stage record of the plan, the failed record included."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    assert h.plan_cli("--architecture", "docs/absent.md").code == 0
    warning = h.plan_json()["architecture_warning"]
    res = h.fail("check-failed")
    assert res.code == 0, res.describe()
    record = h.read_json(h.plan_dir / "stage-record.json")
    assert record["status"] == "failed" and record["warnings"] == [warning] and set(warning) == {"code", "detail"}


def test_fail_leaves_the_architecture_warning_out_when_the_plan_fails_its_trust_checks(stage, cli, tmp_path, monkeypatch):
    """A plan whose digest or pointer doesn't check out has no say in the record: only the reasons it can't be trusted are listed."""
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    assert h.plan_cli("--architecture", "docs/absent.md").code == 0
    refused = h.fail("check-failed", digest="0" * 64)
    assert refused.code == 2, refused.describe()
    assert [w["code"] for w in h.read_json(h.plan_dir / "stage-record.json")["warnings"]] == ["plan-digest-mismatch"]
    assert h.plan_cli("--architecture", "docs/absent.md").code == 0, "a newer plan takes the pointer"
    older = h.plan_dir
    h.plan_cli()
    stale = h.fail("check-failed", plan_id=older.name, digest=sha256_of(older / "plan.json"))
    assert stale.code == 2, stale.describe()
    assert [w["code"] for w in h.read_json(older / "stage-record.json")["warnings"]] == ["pointer-mismatch"]


# ---- the SARIF fallback (D8, AR-T2)

def make_threats_sarif(ids, peers=None, absent=(), score=None):
    """A ``threats.sarif`` with one result for each ID. ``peers`` maps a peer to its primary, which are grouped as CG-1. ``score`` gives
    each result that composite (a scored SARIF: the controls stage needs one on every member of its fallback)."""
    results = []
    for fid in ids:
        properties = {"baseline-state": "absent"} if fid in absent else {}
        if score is not None:
            properties["composite"] = score
        if peers and fid in peers:
            properties.update({"correlation-group": "CG-1", "correlation-role": "peer", "correlation-primary": peers[fid]})
        elif peers and fid in peers.values():
            properties.update({"correlation-group": "CG-1", "correlation-role": "primary", "correlation-primary": fid})
        results.append({"ruleId": "tachi/stride/spoofing", "message": {"text": "a finding"},
                        "partialFingerprints": {"findingId/v1": fid}, "properties": properties})
    return json.dumps({"version": "2.1.0", "runs": [{"results": results}]})


def sarif_only(stage, cli, tmp_path, monkeypatch, sarif, name="risk-score"):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name, ids=["S-1"])
    h.threats.unlink()
    (h.out / "threats.sarif").write_text(sarif, encoding="utf-8")
    return h


def test_plan_falls_back_to_threats_sarif_when_threats_md_is_absent(stage, cli, tmp_path, monkeypatch):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["T-2", "S-1", "AGP-01", "I-3"], peers={"I-3": "S-1"}))
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "threats.sarif" in res.err and "WARNING" in res.err
    assert agent_ids(h) == ["S-1", "T-2", "AGP-1"], "S-2 order, canonical IDs, and the peer I-3 copies its primary"
    sarif = h.out / "threats.sarif"
    assert h.batch_input("B001")["refs"]["threats"] == str(sarif)
    assert h.plan_json()["inputs"]["threats"]["sha256"] == sha256_of(sarif)
    assert h.batch_input("B001")["units"] == [{"finding_id": "S-1", "threat": "a finding"}, {"finding_id": "T-2", "threat": "a finding"},
                                              {"finding_id": "AGP-1", "threat": "a finding"}], (
        "each row holds the text of its own result and no more: the agent reads the rest from refs.threats (P0-3)")


def test_results_the_sarif_marks_absent_are_resolved_and_are_not_planned(stage, cli, tmp_path, monkeypatch):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1", "T-2", "D-1"], absent=["T-2"]))
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "D-1"]


@pytest.mark.parametrize("sarif", ['{"version": "2.1.0", "runs": [{"results": []}]}', '{"runs": []}', "[]",
                                   '{"runs": [{"results": [{"partialFingerprints": {"findingId/v1": "not an id"}}]}]}'],
                         ids=["no-results", "no-runs", "not-an-object", "no-valid-id"])
def test_an_empty_extraction_from_the_sarif_stops_before_dispatch(stage, cli, tmp_path, monkeypatch, sarif):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "TACHI RISK-SCORE FAILED" in res.err and "threats.sarif" in res.err
    assert not (h.build / "current.json").exists() and not list(h.out.glob(".tachi-build/risk-score/*/plan.json"))


@pytest.mark.parametrize("text", ["{not json", '{"runs": [{"results": [{"x": NaN}]}]}'], ids=["not-json", "nan"])
def test_a_sarif_that_is_not_strict_json_stops_before_dispatch(stage, cli, tmp_path, monkeypatch, text):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, text)
    assert h.plan_cli().code == 2 and not (h.build / "current.json").exists()


def test_the_sarif_fallback_has_no_status_for_any_member_so_the_baseline_decides(stage, cli, tmp_path, monkeypatch):
    """D8's fallback lacks ``delta_status`` for every member (ruled at W2): a member with a usable open row in the baseline is
    UNCHANGED and carried, and every other is NEW. Without the derivation each would count as NEW and be scored again."""
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1", "T-2", "D-1", "E-1"], peers={"E-1": "S-1"}))
    write_baseline(tmp_path, ["T-2", "E-1"])
    res = h.plan_cli("--baseline-dir", "baseline-runs/prev")
    assert res.code == 0, res.describe()
    assert agent_ids(h) == ["S-1", "D-1"], "T-2 is carried, and the peer E-1 is carried too, because it has a usable row"


def test_the_sarif_fallback_with_no_baseline_scores_every_non_peer_fresh(stage, cli, tmp_path, monkeypatch):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1", "T-2", "D-1"], peers={"T-2": "S-1"}))
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "D-1"]


def test_threats_md_wins_when_both_exist_and_the_fallback_is_the_scorers_alone(stage, cli, tmp_path, monkeypatch):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["S-1", "T-2"])
    (h.out / "threats.sarif").write_text(make_threats_sarif(["D-1"]), encoding="utf-8")
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "T-2"]
    (tmp_path / "controls").mkdir()
    controls = sarif_only(stage, cli, tmp_path / "controls", monkeypatch, make_threats_sarif(["S-1"]), name="compensating-controls")
    controls.risk_scores.unlink()
    assert controls.plan_cli().code == 1, "controls fall back to risk-scores.sarif (T036), never to threats.sarif"


def test_no_threats_md_and_no_sarif_beside_it_is_a_missing_input(stage, cli, tmp_path, monkeypatch):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1"]))
    (h.out / "threats.sarif").unlink()
    assert h.plan_cli().code == 1
    elsewhere = h.cli("plan", "--stage", "risk-score", "--out", h.out, "--date", DATE, "--threats", h.out / "renamed.md")
    assert elsewhere.code == 1, "only threats.md has a SARIF to fall back to"


# ---- the fallback's unit rows hold each member's own text, and a group with no ID still routes its peers (D8, P0-3)
#
# A SARIF result gives its member's component, threat, mitigation, risk level and layer, in either ID form, and the unit rows of both
# stages' fallbacks carry them: ``risk-scorer.md`` tells the agent that its units hold the details, and a row of the ID alone left a
# legacy-form member with nothing. The planner and the renderer take the text from one reader, ``parse_sarif_member_set(...,
# with_details=True)``. The three shipped shapes that P0-3 names are copied into ``tmp_path`` and planned there, and nothing here
# writes under ``examples/``. The controls stage reads any SARIF the same way, so a copy of each shape also stands in for its
# ``risk-scores.sarif``, where every member (peers too) is a unit.

SARIF_SHAPES = {
    "modern": "agentic-app/sample-report/threats.sarif",          # findingId/v1 on every result
    "unnamed-groups": "maestro-reference/threats.sarif",          # correlation groups that the file gives no group ID
    "legacy": "mobile-banking-app/sample-report/threats.sarif",   # no findingId/v1: the ID is in properties.id only
}
ROW_KEYS = ("component", "threat", "risk_level", "mitigation", "layer")
BAND_WORDS = ("Critical", "High", "Medium", "Low", "Note")


def shipped_sarif(shape):
    return (REPO_ROOT / "examples" / SARIF_SHAPES[shape]).read_text(encoding="utf-8")


def fallback_only(stage, cli, tmp_path, monkeypatch, sarif, name="risk-score"):
    """A project whose only scored input is a SARIF: ``threats.sarif`` for the scorer, ``risk-scores.sarif`` for the controls stage.

    The controls stage plans only a member that its renderer can score, so the SARIF that stands in for its ``risk-scores.sarif`` gets a
    composite on each result that has none. A row's text is what the results give, so nothing else changes."""
    if name == "risk-score":
        return sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    return scores_sarif_only(stage, cli, tmp_path, monkeypatch, with_composites(sarif))


def sarif_of(*results):
    return json.dumps({"version": "2.1.0", "runs": [{"results": list(results)}]})


def detail_result(finding_id, form="fingerprint", name=None, text=None, markdown=None, properties=None):
    """One result of a synthetic SARIF: its ID in ``findingId/v1`` or, as tachi's older files have it, in ``properties.id``, and only the text given."""
    result = {"ruleId": "tachi/stride/spoofing", "properties": dict(properties or {})}
    if form == "fingerprint":
        result["partialFingerprints"] = {"findingId/v1": finding_id}
    else:
        result["properties"]["id"] = finding_id
    if name is not None:
        result["locations"] = [{"logicalLocations": [{"name": name}]}]
    message = {key: value for key, value in (("text", text), ("markdown", markdown)) if value is not None}
    if message:
        result["message"] = message
    return result


def own_text(result):
    """D8's reading of one result, written out here and apart from the reader that the planner uses: the first usable string for each
    detail (a missing key, a blank string and a value that isn't a string are no value). The logical location is the first of
    ``logicalLocations``, else the singular ``logicalLocation`` that tachi's older scorer and controls files write, and the risk level is
    ``risk_level``, else ``severity``, else ``security-severity`` (ruled at W3: a word comes before a score)."""
    properties = result.get("properties") or {}
    location = (result.get("locations") or [{}])[0]
    logical = (location.get("logicalLocations") or [location.get("logicalLocation") or {}])[0]
    message = result.get("message") or {}

    def first(*values):
        return next((value for value in values if isinstance(value, str) and value.strip()), None)

    return {"component": first(logical.get("name"), properties.get("component")), "threat": first(message.get("text")),
            "risk_level": first(properties.get("risk_level"), properties.get("severity"), properties.get("security-severity")),
            "mitigation": first(message.get("markdown")), "layer": first(properties.get("maestro-layer"))}


def kept_results(sarif_text):
    """The first kept result of each ID, by canonical ID: a result that is ``absent`` (RESOLVED) is dropped, as the reader drops it."""
    kept = {}
    for result in json.loads(sarif_text)["runs"][0]["results"]:
        properties = result.get("properties") or {}
        finding_id = (result.get("partialFingerprints") or {}).get("findingId/v1") or properties.get("id")
        if finding_id and "absent" not in (result.get("baselineState"), properties.get("baselineState"), properties.get("baseline-state")):
            kept.setdefault(canon(finding_id), result)
    return kept


def expected_rows(sarif_text):
    """The unit row that each result of a SARIF should give, by canonical ID: the file's own values, the first result of an ID winning.

    A risk level is written as the file has it, which holds for the shipped ``threats.sarif`` shapes (a band word, or none). The score table
    below pins a score, and the agreement test checks both against the renderer."""
    rows = {}
    for finding_id, result in kept_results(sarif_text).items():
        text = own_text(result)
        rows[finding_id] = dict({"finding_id": finding_id}, **{key: text[key] for key in ROW_KEYS if text[key] is not None})
    return rows


def peers_of(sarif_text):
    """The members that the file's groups make peers (each group's members but its primary), whether or not a group has an ID."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers

    return {member for group in tachi_parsers.parse_sarif_member_set(sarif_text)["groups"] for member in group["members"][1:]}


def test_the_shipped_shapes_still_show_the_forms_they_stand_for():
    """The cases below rest on what each sample is, so a sample that changes fails here and can't turn them into vacuous passes."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers

    modern = json.loads(shipped_sarif("modern"))["runs"][0]["results"]
    assert modern and all("findingId/v1" in r["partialFingerprints"] and "id" not in r["properties"] for r in modern)
    legacy = json.loads(shipped_sarif("legacy"))["runs"][0]["results"]
    assert legacy and all("findingId/v1" not in r.get("partialFingerprints", {}) and r["properties"]["id"] for r in legacy)
    groups = tachi_parsers.parse_sarif_member_set(shipped_sarif("unnamed-groups"))["groups"]
    assert len(groups) >= 3 and all(group["group_id"] is None for group in groups)


@pytest.mark.parametrize("name", STAGE_NAMES)
@pytest.mark.parametrize("shape", sorted(SARIF_SHAPES))
def test_each_fallback_row_equals_its_results_own_text_whichever_id_form_it_uses(stage, cli, tmp_path, monkeypatch, shape, name):
    """P0-3 (b): the legacy form's rows used to hold the ID alone. Each row is the file's own values for that member. The scorer's agent
    set is every member but the peers of the file's groups (a group with no ID included), and the controls stage plans every member."""
    text = shipped_sarif(shape)
    expected = expected_rows(text)
    h = fallback_only(stage, cli, tmp_path, monkeypatch, text, name)
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    planned = set(expected) - (peers_of(text) if name == "risk-score" else set())
    rows = unit_rows(h)
    assert len(planned) > 20 and rows == {finding_id: expected[finding_id] for finding_id in planned}
    assert all(set(row) > {"finding_id"} for row in rows.values()), "every row holds some of its result's text"


def test_a_legacy_form_member_keeps_its_identity_text(stage, cli, tmp_path, monkeypatch):
    """P0-3 (b), by name: a result with only ``properties.id`` gives its component, threat and risk level, and none comes back blank."""
    h = sarif_only(stage, cli, tmp_path, monkeypatch, shipped_sarif("legacy"))
    assert h.plan_cli().code == 0
    rows = unit_rows(h)
    assert len(rows) == len(expected_rows(shipped_sarif("legacy"))) > 20
    assert all(row["component"] and row["threat"] and row["risk_level"] in BAND_WORDS for row in rows.values())


def test_either_id_form_gives_the_same_row(stage, cli, tmp_path, monkeypatch):
    text = dict(name="Gateway", text="a threat", markdown="a fix", properties={"risk_level": "High", "maestro-layer": "L3"})
    sarif = sarif_of(detail_result("AGP-01", **text), detail_result("AGP-02", form="properties", **text))
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    assert h.plan_cli().code == 0
    rows = unit_rows(h)
    assert rows["AGP-1"] == {"finding_id": "AGP-1", "component": "Gateway", "threat": "a threat", "risk_level": "High", "mitigation": "a fix", "layer": "L3"}
    assert dict(rows["AGP-2"], finding_id="AGP-1") == rows["AGP-1"], "the ID in properties.id is read as the canonical ID too"


def test_groups_the_sarif_gives_no_id_still_route_their_peers_with_no_baseline(stage, cli, tmp_path, monkeypatch):
    """P0-3 (a), the planner's half. maestro-reference's threats.sarif gives correlation groups and no group ID. They are passed to the
    routing as the reader gives them, so a peer is never sent to the agent: its primary is, and the peer copies it."""
    text = shipped_sarif("unnamed-groups")
    h = sarif_only(stage, cli, tmp_path, monkeypatch, text)
    assert h.plan_cli().code == 0
    members = set(expected_rows(text))
    peers = peers_of(text)
    assert len(peers) >= 3 and set(agent_ids(h)) == members - peers
    assert h.plan_json()["unit_count"] == len(members) - len(peers)


def test_groups_the_sarif_gives_no_id_split_unchanged_from_new_as_the_renderer_splits_them(stage, cli, tmp_path, monkeypatch):
    """With a baseline, the renderer's call is ``route_scorer_units`` over the reader's groups, with no status for any member. The plan's
    agent set is its ``to_agent``. One group has both members in the baseline (both carried), one only its peer (the peer is carried and
    its primary is scored fresh) and one neither (the peer copies its primary, which is scored fresh)."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers
    import tachi_scoring_rules as rules

    text = shipped_sarif("unnamed-groups")
    found = tachi_parsers.parse_sarif_member_set(text)
    (both, peer_only, neither) = [group["members"] for group in found["groups"][:3]]
    assert all(group["group_id"] is None for group in found["groups"][:3])
    grouped = {member for group in found["groups"] for member in group["members"]}
    loners = [member for member in found["members"] if member not in grouped][:2]
    h = sarif_only(stage, cli, tmp_path, monkeypatch, text)
    write_baseline(tmp_path, both + [peer_only[1]] + loners)
    res = h.plan_cli("--baseline-dir", "baseline-runs/prev")
    assert res.code == 0, res.describe()
    baseline = rules.read_baseline_scores(tmp_path / "baseline-runs" / "prev" / "risk-scores.md")
    routing = rules.route_scorer_units([{"id": member} for member in found["members"]], groups=found["groups"], baseline=baseline,
                                       lacking={member: ["delta_status"] for member in found["members"]})
    assert set(agent_ids(h)) == set(routing.to_agent) and len(agent_ids(h)) == len(routing.to_agent)
    agent = set(agent_ids(h))
    assert not agent & set(both) and not agent & set(loners), "carried: UNCHANGED, with a usable baseline row"
    assert peer_only[0] in agent and peer_only[1] not in agent, "the peer is carried, and its primary has no row, so it is NEW"
    assert neither[0] in agent and neither[1] not in agent, "the peer has no row and copies its primary"
    assert set(routing.carried) == set(both) | {peer_only[1]} | set(loners)
    assert unit_rows(h)[neither[0]] == expected_rows(text)[neither[0]], "and the primary's row holds its own text"


# The score table: ``security-severity`` is a score and never a band, so a row that carries only that gets the band that the renderer shows
# (``tachi_scoring.band`` after the score is rounded half up to one decimal and held in 0.0 to 10.0). The pairs are written out, not computed.
SCORE_LABELS = [
    ("10", "Critical"), ("10.0", "Critical"), ("9.0", "Critical"), ("9", "Critical"), ("8.95", "Critical"), ("8.94", "High"), ("8.2", "High"),
    ("7.0", "High"), ("6.95", "High"), ("6.94", "Medium"), ("4.0", "Medium"), ("3.95", "Medium"), ("3.94", "Low"), ("1", "Low"),
    ("0.5", "Low"), ("0.04", "Low"), ("0", "Low"), ("-1", "Low"), ("11", "Critical"), ("1e3", "Critical"), (" 7.5 ", "High"),
]


@pytest.mark.parametrize("value,label", SCORE_LABELS, ids=[value.strip() or "blank" for value, _ in SCORE_LABELS])
def test_a_score_only_result_gets_the_band_of_its_score(stage, cli, tmp_path, monkeypatch, value, label):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif_of(detail_result("S-1", properties={"security-severity": value})))
    assert h.plan_cli().code == 0
    assert unit_rows(h) == {"S-1": {"finding_id": "S-1", "risk_level": label}}


@pytest.mark.parametrize("properties,level", [
    ({"risk_level": "Critical"}, "Critical"), ({"risk_level": "high"}, "high"), ({"risk_level": "Note"}, "Note"),
    ({"risk_level": "n/a"}, "n/a"), ({"security-severity": "NaN"}, "NaN"), ({"security-severity": "Infinity"}, "Infinity"),
    ({"risk_level": "Medium", "security-severity": "9.5"}, "Medium"), ({"risk_level": "  ", "security-severity": "9.5"}, "Critical"),
    ({"risk_level": "7.2"}, "High"), ({"risk_level": 7, "security-severity": "2.0"}, "Low"),
], ids=["word", "lowercase-word", "note", "not-a-score", "nan", "infinity", "risk_level-wins", "blank-falls-through", "score-in-risk_level", "not-a-string"])
def test_a_word_stays_as_the_file_writes_it_and_the_risk_level_property_comes_first(stage, cli, tmp_path, monkeypatch, properties, level):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif_of(detail_result("S-1", properties=properties)))
    assert h.plan_cli().code == 0
    assert unit_rows(h) == {"S-1": {"finding_id": "S-1", "risk_level": level}}


# The planner and the renderer give a fallback member one risk label, each from its own copy of the steps (the planner's ``_sarif_risk_level``,
# the renderer's ``_risk_level``): a string that ``parse_score`` doesn't read as finite stays as written, a score is held to 0.0 to 10.0, rounded
# half up to one decimal and banded by ``tachi_scoring.band``, and no level at all is a dash in the renderer and no key in the planner's row.
# Two copies are the most the Rule of Three allows, so this test runs the renderer's function over the same values, loaded as its own tests load it.
# It needs the renderer that P0-3 rewrote: an older ``_risk_level`` read only a score, gave ``Note`` for a score under 1.0 and did not round.

@pytest.fixture(scope="module")
def renderer():
    return _load_hyphenated_script("render_risk_scores_for_stage_tests", "render-risk-scores.py")


EDGE_LEVELS = ["8.95", "6.95", "-1", "10.5", "NaN", "High"]
EDGE_LABELS = ["Critical", "High", "Low", "Critical", "NaN", "High"]
# the four threats.sarif samples (a band word, or none) and the shipped files that carry scores, which no threats.sarif does
AGREEMENT_SAMPLES = (
    "agentic-app/sample-report/threats.sarif", "maestro-reference/threats.sarif", "mobile-banking-app/sample-report/threats.sarif",
    "predictive-ml-app/sample-report/threats.sarif",
    "agentic-app/sample-report/risk-scores.sarif", "consumer-agent-app/sample-report/risk-scores.sarif", "maestro-reference/risk-scores.sarif",
    "mobile-banking-app/sample-report/risk-scores.sarif", "predictive-ml-app/sample-report/risk-scores.sarif",
)


def test_the_planners_risk_label_equals_the_renderers_on_the_edges(stage, cli, renderer, tmp_path, monkeypatch):
    """The six edges of the sweep, then the whole score table and more words, then a result with no level, all in one plan."""
    values = EDGE_LEVELS + [value for value, _ in SCORE_LABELS] + ["Critical", "high", "Note", "n/a", "Infinity", "-Infinity"]
    results = [detail_result("T-%d" % number, properties={"risk_level": value}) for number, value in enumerate(values, 1)]
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif_of(detail_result("D-1"), *results))
    assert h.plan_cli().code == 0
    rows = unit_rows(h)
    assert [rows["T-%d" % number]["risk_level"] for number in range(1, len(EDGE_LEVELS) + 1)] == EDGE_LABELS
    for number, value in enumerate(values, 1):
        assert rows["T-%d" % number]["risk_level"] == renderer._risk_level(value), value
    assert "risk_level" not in rows["D-1"] and renderer._risk_level(None) == renderer.DASH, "no level: no key here, a dash there"


@pytest.mark.parametrize("sample", AGREEMENT_SAMPLES)
def test_the_planners_risk_label_equals_the_renderers_over_each_shipped_sample(stage, cli, renderer, tmp_path, monkeypatch, sample):
    """Each member's own level, read as D8 reads it, gets the same label from the renderer's function as the controls stage's row holds (that
    stage plans every member, peers too). The threats.sarif samples hold a band word or none, and the other five hold a score."""
    text = (REPO_ROOT / "examples" / sample).read_text(encoding="utf-8")
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, with_composites(text))   # a threats.sarif has no composite, which the controls stage now needs
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    rows = unit_rows(h)
    levels = {finding_id: own_text(result)["risk_level"] for finding_id, result in kept_results(text).items()}
    assert len(levels) > 5 and set(levels) <= set(rows)
    for finding_id, level in levels.items():
        assert rows[finding_id].get("risk_level", renderer.DASH) == renderer._risk_level(level), (finding_id, level)


def test_a_result_with_no_usable_text_gives_a_row_of_the_id_alone(stage, cli, tmp_path, monkeypatch):
    """A missing key, a blank string and a value of another type are no text: the row leaves the key out, as ``_unit_row`` does."""
    sarif = sarif_of(detail_result("S-1"),
                     detail_result("T-2", name="  ", text="", markdown=" \t", properties={"component": "", "maestro-layer": " ", "risk_level": ""}),
                     detail_result("D-3", name=5, text=["x"], markdown=7, properties={"component": None, "maestro-layer": 3}))
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    assert h.plan_cli().code == 0
    assert unit_rows(h) == {fid: {"finding_id": fid} for fid in ("S-1", "T-2", "D-3")}


def test_the_component_falls_back_to_the_property_when_the_location_has_no_name(stage, cli, tmp_path, monkeypatch):
    sarif = sarif_of(detail_result("S-1", form="properties", name="", properties={"component": "Gateway"}),
                     detail_result("T-2", name="Broker", properties={"component": "Other"}))
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    assert h.plan_cli().code == 0
    assert (unit_rows(h)["S-1"]["component"], unit_rows(h)["T-2"]["component"]) == ("Gateway", "Broker")


def test_the_rows_hold_each_text_as_the_file_writes_it_and_the_first_result_of_an_id_wins(stage, cli, tmp_path, monkeypatch):
    """The planner neither escapes nor trims a value, and refuses only a character that step 10 forbids (``test_a_character_that_step_10_forbids_...``
    below): the agent reads the rest as data, and the renderer escapes it where it writes it. Two results for one ID give the first one's
    text, as the reader says. The batch input that holds the rows reads back through the document reader (a retry does that), a character
    outside the basic plane included: JSON spells it as a surrogate pair, which is not a lone surrogate."""
    awkward = " a < b & c | `d` {{e}} " + chr(0xE9) + chr(0x2014) + "[0m" + chr(0x1F600) + "\n\t "
    sarif = sarif_of(detail_result("S-1", name=awkward, text=awkward, markdown=awkward, properties={"maestro-layer": awkward, "risk_level": awkward}),
                     detail_result("S-1", name="second", text="second"))
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    assert h.plan_cli().code == 0
    expected = {"S-1": {"finding_id": "S-1", "component": awkward, "threat": awkward, "risk_level": awkward, "mitigation": awkward, "layer": awkward}}
    assert unit_rows(h) == expected
    assert h.reconcile().code == 3, "no part is there, so the batch is retried from its own input, which is read back"
    assert unit_rows(h) == expected and h.plan_json()["batches"][0]["attempt"] == 2


@pytest.mark.parametrize("name", STAGE_NAMES)
@pytest.mark.parametrize("detail,result", [
    ("component", dict(name="a" + chr(0xD800))), ("threat", dict(text="a" + chr(0xDFFF) + "b")), ("mitigation", dict(markdown=chr(0xDC00))),
    ("layer", dict(properties={"maestro-layer": "L" + chr(0xD83D)})), ("risk_level", dict(properties={"risk_level": chr(0xDE00) + "High"})),
], ids=["component", "threat", "mitigation", "layer", "risk_level"])
def test_a_lone_surrogate_in_the_sarif_ends_the_run_before_anything_is_written(stage, cli, tmp_path, monkeypatch, name, detail, result):
    """JSON can spell a lone surrogate, which no markdown input can, and the document reader refuses a document that holds one, so a batch
    input with it would plan and then fail its first retry. The plan stops instead, with exit 2, and names the finding, the detail and the
    file, with nothing written."""
    sarif = sarif_of(detail_result("S-1", name="Gateway", text="a threat"), detail_result("T-2", **result))
    h = fallback_only(stage, cli, tmp_path, monkeypatch, sarif, name)
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "lone surrogate" in res.err and "the %s of T-2" % detail in res.err and ".sarif" in res.err and "Remedy:" in res.err
    assert not (h.build / "current.json").exists() and not list(h.out.glob(".tachi-build/*/*/plan.json"))


def test_a_lone_surrogate_in_a_peers_text_stops_the_scorer_too(stage, cli, tmp_path, monkeypatch):
    """A peer copies its primary and no batch input holds its row, but the SARIF is one that a document can't carry, and the controls stage
    would plan that peer, so the scorer's plan refuses it as well."""
    peer = detail_result("E-1", text="a" + chr(0xD800), properties={"correlation-group": "CG-1", "correlation-role": "peer", "correlation-primary": "S-1"})
    primary = detail_result("S-1", properties={"correlation-group": "CG-1", "correlation-role": "primary", "correlation-primary": "S-1"})
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif_of(primary, peer))
    res = h.plan_cli()
    assert res.code == 2 and "the threat of E-1" in res.err, res.describe()


def test_a_member_that_only_a_legacy_peer_reference_names_is_never_planned_by_the_scorer(stage, cli, tmp_path, monkeypatch):
    """It has no result of its own, so it has no text, and a peer copies its primary, so the scorer never plans it. (The controls stage
    would plan it, and its renderer could not score it: ``test_the_controls_plan_refuses_a_member_...`` below.)"""
    primary = detail_result("S-1", name="Gateway", text="the primary's threat")
    primary["relatedLocations"] = [{"message": {"text": "E-1: a legacy peer reference"}}]
    h = sarif_only(stage, cli, tmp_path, monkeypatch, sarif_of(primary))
    assert h.plan_cli().code == 0
    assert unit_rows(h) == {"S-1": {"finding_id": "S-1", "component": "Gateway", "threat": "the primary's threat"}}


# ---- the controls fallback plans only a member that its renderer can score (ADR-050 D8; KB 22)
#
# D8's member set is the SARIF's results plus any legacy peer reference in ``relatedLocations``. ``render-compensating-controls.py`` can't
# score a member that no result of its own names (a peer reference holds no score), or one whose result has no composite from 0.0 to 10.0
# on the 0.1 grid, and it ended the run with exit 2 after every agent had run. The planner refuses such a member before any is dispatched,
# with the renderer's message and remedy (``_members_from_sarif`` and ``_valid_inherent``), which the tests below read from the renderer
# itself, so the two can't drift apart.

@pytest.fixture(scope="module")
def controls_renderer():
    return _load_hyphenated_script("render_compensating_controls_for_stage_tests", "render-compensating-controls.py")


def renderer_refusal(controls_renderer, sarif_text):
    """The error that the controls renderer's reader of D8's fallback raises for this SARIF."""
    run = controls_renderer.Run()
    with pytest.raises(controls_renderer.RenderError) as caught:
        controls_renderer._members_from_sarif(run, {"path": "/run/risk-scores.sarif"}, sarif_text.encode("utf-8"), "kept")
    return caught.value


def assert_refused_before_dispatch(h, res, controls_renderer, sarif_text, needle):
    """Exit 2 with the renderer's own reason and remedy, and nothing written. ``needle`` is what that reason has to say."""
    refusal = renderer_refusal(controls_renderer, sarif_text)
    assert refusal.code == 2 and needle in refusal.reason, "the renderer ends the run on this member, so the planner must too"
    assert res.code == 2, res.describe()
    assert "TACHI COMPENSATING-CONTROLS FAILED: " + refusal.reason in res.err and "Remedy: " + refusal.remedy in res.err, res.describe()
    assert refusal.remedy == "regenerate it with /tachi.risk-score"
    assert not (h.build / "current.json").exists() and not list(h.out.glob(".tachi-build/compensating-controls/*/plan.json"))


def test_the_controls_plan_refuses_a_member_that_only_a_legacy_peer_reference_names(stage, cli, controls_renderer, tmp_path, monkeypatch):
    """The v4.48.x scorer lists each peer in its primary's ``relatedLocations`` and gives it no result. A plan made from such a file
    exited 0 with a unit for that peer, every agent ran, and the render then exited 2."""
    primary = detail_result("S-1", name="Gateway", text="the primary's threat", properties={"composite": SCORE})
    primary["relatedLocations"] = [{"message": {"text": "E-1: a legacy peer reference"}}]
    sarif = sarif_of(primary)
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    res = h.plan_cli()
    assert_refused_before_dispatch(h, res, controls_renderer, sarif, "E-1 only as a peer reference")
    assert "risk-scores.sarif names E-1 only as a peer reference, so it holds no result and no score for it" in res.err


def test_the_controls_plan_refuses_the_shipped_scorer_sarif_once_its_peers_are_only_peer_references(stage, cli, controls_renderer, tmp_path, monkeypatch):
    """``examples/maestro-reference/risk-scores.sarif`` lists its peers in ``relatedLocations`` and gives each one a result too, so the file
    plans as shipped (``test_the_planners_risk_label_equals_the_renderers_over_each_shipped_sample``). Taking the peers' results out of a copy
    leaves the form that the v4.48.x scorer wrote (primaries and uncorrelated findings only), and the plan refuses it."""
    text = (REPO_ROOT / "examples" / "maestro-reference" / "risk-scores.sarif").read_text(encoding="utf-8")
    document = json.loads(text)
    results = document["runs"][0]["results"]
    named = {canon(match.group("id")) for result in results for location in result.get("relatedLocations", [])
             for match in [re.match(r"(?P<id>[A-Z]+-[0-9]+): ", location["message"]["text"])] if match}
    assert len(named) >= 3 and {canon(kept["partialFingerprints"]["findingId/v1"]) for kept in results} >= named, "each peer has a result of its own in the sample"
    document["runs"][0]["results"] = [result for result in results if canon(result["partialFingerprints"]["findingId/v1"]) not in named]
    sarif = json.dumps(document)
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    res = h.plan_cli()
    assert_refused_before_dispatch(h, res, controls_renderer, sarif, "only as a peer reference")
    assert re.search(r"risk-scores\.sarif names [A-Z]+-[0-9]+ only as a peer reference", res.err)


@pytest.mark.parametrize("composite", [None, "not a number", "", "11", "-1", 11, -1, 7.25, "7.25", "6.45", True],
                         ids=["absent", "text", "empty", "above-10-text", "below-0-text", "above-10", "below-0", "off-grid-number", "off-grid-text",
                              "off-grid-hundredths", "boolean"])
def test_the_controls_plan_refuses_a_member_whose_result_has_no_composite_on_the_grid(stage, cli, controls_renderer, tmp_path, monkeypatch, composite):
    """A result that gives no composite the reader accepts, or one off the 0.1 grid, has no inherent score for the renderer. The first such
    member in S-2 order is named, though a later one has the same fault."""
    properties = {} if composite is None else {"composite": composite}
    sarif = sarif_of(detail_result("S-1", text="scored", properties={"composite": SCORE}), detail_result("T-2", text="unscored", properties=properties),
                     detail_result("D-1", text="also unscored"))
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    res = h.plan_cli()
    assert_refused_before_dispatch(h, res, controls_renderer, sarif, "for T-2,")
    assert "the input risk-scores.sarif holds no score from 0.0 to 10.0 on the 0.1 grid for T-2, so its residual risk can't be computed" in res.err


def test_a_score_in_security_severity_counts_and_so_does_a_composite_on_the_grid_at_each_end(stage, cli, tmp_path, monkeypatch):
    """The reader takes the composite from ``composite``, else ``security-severity`` (the scorer agent's own property), and 0.0 and 10.0 are on the grid."""
    sarif = sarif_of(detail_result("S-1", properties={"security-severity": "8.4"}), detail_result("T-2", properties={"composite": "0.0"}),
                     detail_result("D-1", properties={"composite": 10}), detail_result("E-1", properties={"composite": "9.95", "security-severity": "4.0"}))
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    res = h.plan_cli()
    assert res.code == 2 and "for E-1" in res.err, "a composite that is set wins over security-severity, and 9.95 is off the grid"
    (tmp_path / "again").mkdir()
    h = scores_sarif_only(stage, cli, tmp_path / "again", monkeypatch, sarif.replace("9.95", "9.9"))
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "T-2", "D-1", "E-1"]


# =========================================================================== controls planning (T036; ADR-050 D2, D8, D9)
#
# The controls stage plans from the scorer's risk-scores.md: its units are the open rows of that file, each with the Section 7 values
# of the threats.md that its frontmatter names. An UNCHANGED finding's row also carries its baseline's persisted result (AR-T3).

CONTROLS = "compensating-controls"
CARRIED = ("control_status", "control_category", "confidence", "evidence", "matrix_row", "recommendation_body")
_RATINGS = {"coverage": "High", "configuration": "Medium", "currency": "Low", "completeness": "High"}


def _matrix_row(finding_id, display, category):
    return ("| %s | \u2014 | Gateway | L4 | A <threat> | {{score:inherent}} | {{band:inherent}} | %s | %s | {{score:residual}} | {{band:residual}} |"
            % (finding_id, display, category))


# Three results of the three kinds, with the text the cell escape has to carry: `<`, `&`, `|`, a backtick, a newline, a literal `&lt;`
# the agent wrote, a `{{` that is no slot, and the slot tokens that stay.
CARRY_PARTIAL = {
    "control_status": "partial", "control_category": "input-validation", "confidence": "Medium", "carried_forward": False,
    "evidence": [
        {"file": "src/validate.py", "line": 42, "language": "python",
         "snippet": "if a < b && c > d:\n    run(\"x|y\")  # `tick` & {{7*7}}", "summary": "Checks a < b and a | b only",
         "assessment": {name: {"rating": rating, "rationale": "The %s check is {{count:evidence}} deep, &lt; kept" % name}
                        for name, rating in _RATINGS.items()}},
        {"file": "src/forms/parse.ts", "line": 7, "language": "typescript", "snippet": "const ok = a>b;", "summary": "A second place"},
    ],
    "matrix_row": _matrix_row("T-2", "Partial Control", "input-validation"),
    "recommendation_body": "**What to Implement**: Validate `a` and `b`.\nAnd escape the | character, keeping &amp; as written.\n\n**Effort Estimate**: Low",
}
CARRY_MISSING = {
    "control_status": "missing", "control_category": "authentication", "confidence": None, "carried_forward": True, "evidence": [],
    "matrix_row": _matrix_row("D-1", "No Control Found", "authentication"),
    "recommendation_body": "**What to Implement**: Add one.\n\n**Effort Estimate**: Medium",
}
CARRY_FOUND = {
    "control_status": "found", "control_category": "csp-security-headers", "confidence": "High", "carried_forward": False,
    "evidence": [{"file": "web/headers.py", "line": 3, "language": "python", "snippet": "set_csp()", "summary": "A CSP header"}],
    "matrix_row": _matrix_row("E-1", "Control Found", "csp-security-headers"), "recommendation_body": None,
}
CARRY_STATUSES = {"S-1": "NEW", "T-2": "UNCHANGED", "D-1": "UNCHANGED", "E-1": "UNCHANGED", "D-2": "UNCHANGED", "R-1": "UPDATED"}


def persisted_values(item):
    """``(field address, text, slots kept)`` for each value of a controls item that exists, in the payload's key order
    (``contracts/module-signatures.md``): a null or an empty list writes no row."""
    out = []
    for name in ("control_status", "control_category", "confidence", "carried_forward"):
        value = item[name]
        if value is not None:
            out.append((name, ("true" if value else "false") if name == "carried_forward" else value, False))
    for index, entry in enumerate(item["evidence"]):
        for name in ("file", "line", "language", "snippet", "summary"):
            out.append(("evidence.%d.%s" % (index, name), str(entry[name]), False))
        for dimension in _RATINGS if "assessment" in entry else ():
            out.append(("evidence.%d.assessment.%s.rating" % (index, dimension), entry["assessment"][dimension]["rating"], False))
            out.append(("evidence.%d.assessment.%s.rationale" % (index, dimension), entry["assessment"][dimension]["rationale"], True))
    out.append(("matrix_row", item["matrix_row"], True))
    if item["recommendation_body"] is not None:
        out.append(("recommendation_body", item["recommendation_body"], False))
    return out


def persisted_table(items):
    """What a renderer writes under ``### Assessment Inputs``: rows in S-2 order of ID, then the payload's key order, each value
    escaped on write by D3's table-cell rule (a narrative value and ``matrix_row`` keep their slot tokens)."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parts

    rows = ["| ID | Field | Value |", "|----|-------|-------|"]
    for finding_id in sorted(items, key=s2_key):
        for field, text, keep in persisted_values(items[finding_id]):
            rows.append("| %s | %s | %s |" % (finding_id, field, tachi_parts.escape_cell(text, keep_slots=keep)))
    return "\n".join(rows) + "\n"


def controls_md(items, schema="1.1"):
    """A ``compensating-controls.md`` as far as the planner reads one: schema 1.1 persists each result in Section 7, and an earlier file has none."""
    head = '---\nschema_version: "%s"\ndate: "2026-11-21"\n---\n\n# Compensating Controls Report\n\n' % schema
    if schema != "1.1":
        return head + "## 2. Control Coverage Matrix\n\nRows that an agent wrote, with no persisted section.\n"
    return head + "## 7. Analysis Integrity\n\n### Input Issues\n\nNone.\n\n### Assessment Inputs\n\n" + persisted_table(items) + "\n"


def write_controls_baseline(root, items, name="prev", schema="1.1", content=None):
    """A baseline run directory under the working directory, with a ``compensating-controls.md`` that persists ``items``
    (or exactly ``content``). Returns the relative path of its ``threats.md``, which is what ``baseline.source`` names."""
    run = Path(root) / "baseline-runs" / name
    run.mkdir(parents=True)
    (run / "threats.md").write_text("# an earlier run\n", encoding="utf-8")
    (run / "compensating-controls.md").write_bytes(controls_md(items, schema).encode("utf-8") if content is None else content)
    return "baseline-runs/%s/threats.md" % name


def controls_routed(stage, cli, tmp_path, monkeypatch, statuses, items=None, groups=(), schema="1.1", content=None):
    """The controls stage over a project whose working directory is ``tmp_path``: a threats.md of these statuses, and, when ``items``
    or ``content`` is given, a baseline that persisted them, which the threats.md's ``baseline.source`` names."""
    source = write_controls_baseline(tmp_path, items, schema=schema, content=content) if items is not None or content is not None else None
    return routed(stage, cli, tmp_path, monkeypatch, statuses, groups, source=source, name=CONTROLS)


def unit_rows(h):
    """The unit row of every planned finding, by canonical ID, across the plan's batch inputs."""
    return {row["finding_id"]: row for batch_id in h.batches() for row in h.batch_input(batch_id)["units"]}


def carried_values(row):
    return {key: row[key] for key in CARRIED if key in row}


def test_the_controls_plan_sends_every_scored_finding_with_its_section_7_row_and_records_what_it_read(stage, cli, tmp_path, monkeypatch):
    """D2: the controls agent gets every scored open finding, peers included, because it copies an UNCHANGED result from its row. Each
    row holds the finding's Section 7 values from the threats.md that risk-scores.md names (D8). The plan records the input and that
    threat model as digest-checked inputs, and as refs for the renderer to read."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, ROUTED, groups=ROUTED_GROUPS)
    res = h.plan_cli()
    assert res.code == 0 and "WARNING" not in res.err, res.describe()
    assert agent_ids(h) == sorted(ROUTED, key=s2_key) and h.plan_json()["unit_count"] == len(ROUTED)
    rows = unit_rows(h)
    for finding_id, status in ROUTED.items():
        assert rows[finding_id]["delta_status"] == status, finding_id
        assert rows[finding_id]["threat"] == "Threat text for %s" % finding_id
        assert rows[finding_id]["mitigation"] == "Mitigation text for %s" % finding_id
        assert rows[finding_id]["layer"] == "L4 " + _DASH + " Deployment", "Section 7's MAESTRO Layer cell"
    assert set(rows["S-1"]) == {"finding_id", "component", "threat", "risk_level", "mitigation", "agentic_pattern", "delta_status", "layer"}
    plan = h.plan_json()
    assert plan["refs"] == h.expected_refs and set(plan["inputs"]) == {"risk_scores", "threats"}
    assert plan["inputs"]["risk_scores"]["sha256"] == sha256_of(h.risk_scores) and plan["inputs"]["threats"]["sha256"] == sha256_of(h.threats)
    assert plan["params"] == {"scoring_date": DATE} and h.batch_input("B001")["refs"] == plan["refs"]


def test_the_controls_units_are_the_open_rows_of_risk_scores_md_and_never_a_resolved_one(stage, cli, tmp_path, monkeypatch):
    """D8: the member set of the controls files is the open rows of the input risk-scores.md, not the threat model's own set."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1", "T-2", "E-1"])
    h.risk_scores.write_text(make_scored_md(["S-1", "T-2", "D-9"], resolved_ids=["R-1"]), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert agent_ids(h) == ["S-1", "T-2", "D-9"], "the scored set in S-2 order: R-1 is RESOLVED (Section 2a), and E-1 was never scored"
    assert unit_rows(h)["D-9"] == {"finding_id": "D-9"}, "a scored finding that threats.md doesn't list has its ID only"
    assert "D-9" in res.err and "E-1" in res.err and "not planned" in res.err, "both gaps are named, so a stale input is seen"


def test_the_controls_units_are_the_set_the_renderers_reader_returns(stage, cli, tmp_path, monkeypatch):
    """The planner and the renderer both read risk-scores.md through ``read_baseline_scores`` (R-26), so they see one member set."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_scoring_rules as rules

    h = controls_routed(stage, cli, tmp_path, monkeypatch, ROUTED, groups=ROUTED_GROUPS)
    assert h.plan_cli().code == 0
    assert agent_ids(h) == list(rules.read_baseline_scores(h.risk_scores).rows) == sorted(ROUTED, key=s2_key)


def test_a_scored_row_that_cannot_be_read_is_warned_of_and_not_planned(stage, cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1", "T-2"])
    bogus = "| NOT-AN-ID | fresh | Gateway | x | 7.1 | 6.0 | 6.0 | 6.0 | 6.4 | Medium | 30d | Review | \u2014 |\n"
    h.risk_scores.write_text(h.risk_scores.read_text(encoding="utf-8").replace("| T-2 |", bogus + "| T-2 |"), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0 and agent_ids(h) == ["S-1", "T-2"], res.describe()
    assert "input issue" in res.err and "Input Issues" in res.err


@pytest.mark.parametrize("kind", ["no-table", "only-resolved", "not-utf8"])
def test_a_scored_input_with_no_open_finding_stops_the_plan_before_dispatch(stage, cli, tmp_path, monkeypatch, kind):
    """An empty extraction is an error, never a pass (KB 22): nothing is written, and the remedy names the scorer."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1"])
    h.risk_scores.write_bytes({"no-table": b"# Risk Scores\n\nNothing tabular.\n", "only-resolved": make_scored_md([], resolved_ids=["R-1"]).encode("utf-8"),
                               "not-utf8": b"\xff\xfe not utf-8"}[kind])
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "TACHI COMPENSATING-CONTROLS FAILED" in res.err and "/tachi.risk-score" in res.err
    assert not (h.build / "current.json").exists() and not list(h.out.glob(".tachi-build/compensating-controls/*/plan.json"))


def test_a_symlinked_scored_input_is_refused_and_says_why(stage, cli, tmp_path, monkeypatch):
    """NFR-10 and KB 24: the renderer's reader opens the input through no link, so the planner, which would otherwise follow one
    when it takes the digest, refuses it too, with a message that names the cause."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1", "T-2"])
    real = tmp_path / "real-scores.md"
    real.write_text(h.risk_scores.read_text(encoding="utf-8"), encoding="utf-8")
    h.risk_scores.unlink()
    os.symlink(str(real), str(h.risk_scores))
    res = h.plan_cli()
    assert res.code == 2 and "symbolic link" in res.err and not (h.build / "current.json").exists(), res.describe()


# ---- an UNCHANGED finding's row carries its baseline's persisted result (AR-T3; ADR-050 D2, RR1 rev. 2)

def test_an_unchanged_units_row_carries_its_baselines_persisted_result(stage, cli, tmp_path, monkeypatch):
    """The result comes from the baseline's Section 7 ``### Assessment Inputs`` through ``parse_controls_assessment_inputs``, and only
    for an UNCHANGED finding: NEW and UPDATED ones are scanned, and an UNCHANGED one that the baseline holds no result for is
    left to the agent, which then reads the baseline file itself (a pre-1.1 baseline) or scans it."""
    items = {"T-2": CARRY_PARTIAL, "D-1": CARRY_MISSING, "E-1": CARRY_FOUND, "R-1": CARRY_MISSING}
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, items)
    res = h.plan_cli()
    assert res.code == 0 and "WARNING" not in res.err, res.describe()
    rows = unit_rows(h)
    for finding_id in ("T-2", "D-1", "E-1"):
        assert carried_values(rows[finding_id]) == {key: items[finding_id][key] for key in CARRIED}, finding_id
        assert rows[finding_id]["delta_status"] == "UNCHANGED" and "carried_forward" not in rows[finding_id], "the agent sets it true"
    for finding_id in ("S-1", "R-1", "D-2"):
        assert carried_values(rows[finding_id]) == {}, finding_id
    baseline = tmp_path / "baseline-runs" / "prev"
    assert h.plan_json()["refs"]["baseline_dir"] == str(baseline) == h.batch_input("B001")["refs"]["baseline_dir"]
    assert h.plan_json()["inputs"]["baseline_compensating_controls"]["sha256"] == sha256_of(baseline / "compensating-controls.md")
    assert set(h.plan_json()["inputs"]) == {"risk_scores", "threats", "baseline_compensating_controls"}


def test_a_carried_string_comes_back_decoded_so_a_render_escapes_it_once(stage, cli, tmp_path, monkeypatch):
    """RR1, rev. 2: the row holds the text as the agent wrote it, never as the file shows it, so the renderer's one escape on write is
    the only one. A `&lt;` the agent wrote literally stays one decode deep (a double decode would turn it into `<`)."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {"T-2": "UNCHANGED"}, {"T-2": CARRY_PARTIAL})
    assert h.plan_cli().code == 0
    row = unit_rows(h)["T-2"]
    shown = (tmp_path / "baseline-runs" / "prev" / "compensating-controls.md").read_text(encoding="utf-8")
    assert "&lt;" in shown and "&#124;" in shown and "&#10;" in shown, "the rendered file holds the escaped text"
    snippet = row["evidence"][0]["snippet"]
    assert "a < b && c > d" in snippet and 'run("x|y")' in snippet and "&amp;" not in snippet and "&#124;" not in snippet
    assert row["evidence"][0]["assessment"]["coverage"]["rationale"] == "The coverage check is {{count:evidence}} deep, &lt; kept"
    assert row["recommendation_body"].count("&amp;") == 1 and "{{score:inherent}}" in row["matrix_row"], "the slot tokens stay"


def agent_writes(rows, fresh):
    """What the controls agent writes for a batch: an UNCHANGED finding's result copied from its row, anything else judged afresh."""
    items = {}
    for finding_id, row in rows.items():
        if row.get("delta_status") == "UNCHANGED" and all(key in row for key in CARRIED):
            items[finding_id] = dict({key: row[key] for key in CARRIED}, carried_forward=True)
        else:
            items[finding_id] = dict(fresh[finding_id], carried_forward=False)
    return items


def only_values(items, finding_ids):
    """The persisted rows of the carried values alone (``carried_forward`` set the same on each), to compare runs byte for byte."""
    return persisted_table({finding_id: dict(items[finding_id], carried_forward=True) for finding_id in finding_ids})


def test_a_carried_result_is_persisted_the_same_bytes_run_after_run(stage, cli, tmp_path, monkeypatch):
    """The two-run case: an UNCHANGED result that holds `<`, `&`, `|`, a backtick, a newline and a literal `&lt;` goes
    agent -> persisted (escaped) -> next plan (decoded) -> agent copies it -> persisted again, and its rows are the same bytes in
    every generation, so no escape compounds (AR-T3, D16). Run 1 judges, run 2 carries three of five, run 3 carries all five."""
    fresh = {"S-1": CARRY_PARTIAL, "T-2": CARRY_MISSING, "E-1": CARRY_FOUND, "D-1": CARRY_PARTIAL, "I-3": CARRY_MISSING}
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=list(fresh))

    def run(statuses, baseline=None):
        h.threats.write_text(make_threats_md(list(statuses), statuses=statuses), encoding="utf-8")
        h.risk_scores.write_text(make_scored_md(list(statuses)), encoding="utf-8")
        res = h.plan_cli(*(["--baseline-dir", baseline] if baseline else []))
        assert res.code == 0 and "WARNING" not in res.err, res.describe()
        return agent_writes(unit_rows(h), fresh)

    first = run({fid: "NEW" for fid in fresh})
    assert not any(item["carried_forward"] for item in first.values())
    write_controls_baseline(tmp_path, first, name="one")
    second = run({"S-1": "UNCHANGED", "T-2": "UNCHANGED", "D-1": "UNCHANGED", "E-1": "UPDATED", "I-3": "NEW"}, "baseline-runs/one")
    carried = ["S-1", "T-2", "D-1"]
    assert [fid for fid, item in second.items() if item["carried_forward"]] == carried
    for finding_id in carried:
        assert {key: second[finding_id][key] for key in CARRIED} == {key: first[finding_id][key] for key in CARRIED}, finding_id
    assert only_values(second, carried) == only_values(first, carried), "one escape per render: the carried rows are byte for byte"
    write_controls_baseline(tmp_path, second, name="two")
    third = run({fid: "UNCHANGED" for fid in fresh}, "baseline-runs/two")
    assert all(item["carried_forward"] for item in third.values())
    assert only_values(third, list(fresh)) == only_values(second, list(fresh))
    assert only_values(third, carried) == only_values(first, carried), "and the third generation is the first one's bytes"


def test_a_halved_batch_keeps_the_carried_results_in_its_children(stage, cli, tmp_path, monkeypatch):
    """A retry's rows come from the plan's batch input, so a halving loses no carried result (``_retry``)."""
    statuses = {"T-2": "UNCHANGED", "D-1": "UNCHANGED", "E-1": "UNCHANGED", "S-1": "NEW"}
    items = {"T-2": CARRY_PARTIAL, "D-1": CARRY_MISSING, "E-1": CARRY_FOUND}
    h = controls_routed(stage, cli, tmp_path, monkeypatch, statuses, items)
    h.plan(batch_size=2)   # B001 holds S-1 and T-2, and B002 holds D-1 and E-1
    assert h.reconcile().code == 3, "no part was written, so both batches halve"
    for child, finding_id in (("B001-2", "T-2"), ("B002-1", "D-1"), ("B002-2", "E-1")):
        (row,) = h.batch_input(child)["units"]
        assert row["finding_id"] == finding_id and carried_values(row) == {key: items[finding_id][key] for key in CARRIED}, child
    assert carried_values(h.batch_input("B001-1")["units"][0]) == {}, "S-1 is NEW"


# ---- the baseline the controls stage resolves (D9, R-6)

def test_a_baseline_written_before_1_1_has_no_persisted_results_and_the_agent_reads_its_file(stage, cli, tmp_path, monkeypatch):
    """D2: a pre-1.1 baseline has no Section 7, so the reader returns nothing and no row carries a result. ``refs.baseline_dir`` is
    there all the same, because the agent copies the UNCHANGED result from that file, which is a digest-checked input."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {}, schema="1.0")
    res = h.plan_cli()
    assert res.code == 0 and "WARNING" not in res.err, res.describe()
    assert all(carried_values(row) == {} for row in unit_rows(h).values())
    assert h.batch_input("B001")["refs"]["baseline_dir"] == str(tmp_path / "baseline-runs" / "prev")
    assert "baseline_compensating_controls" in h.plan_json()["inputs"]


def test_a_baseline_controls_file_that_is_missing_counts_as_missing_and_says_so(stage, cli, tmp_path, monkeypatch):
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"T-2": CARRY_PARTIAL})
    (tmp_path / "baseline-runs" / "prev" / "compensating-controls.md").unlink()
    res = h.plan_cli()
    assert res.code == 0 and "no usable compensating-controls.md (missing)" in res.err and "scanned fresh" in res.err, res.describe()
    assert h.plan_json()["refs"]["baseline_dir"] == str(tmp_path / "baseline-runs" / "prev"), "the directory resolved"
    assert "baseline_compensating_controls" not in h.plan_json()["inputs"] and all(carried_values(row) == {} for row in unit_rows(h).values())


def test_an_unreadable_baseline_controls_file_counts_as_missing(stage, cli, tmp_path, monkeypatch):
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, content=b"\xff\xfe not utf-8")
    res = h.plan_cli()
    assert res.code == 0 and "can't be read" in res.err and "not strict UTF-8" in res.err and "scanned fresh" in res.err, res.describe()
    assert "baseline_compensating_controls" not in h.plan_json()["inputs"] and all(carried_values(row) == {} for row in unit_rows(h).values())


def test_a_persisted_row_the_reader_refuses_leaves_that_finding_scanned_fresh_and_warns(stage, cli, tmp_path, monkeypatch):
    """The reader leaves out an item whose row fails its check, so no stage carries a result it can't trust (T143)."""
    text = controls_md({"T-2": CARRY_PARTIAL, "D-1": CARRY_MISSING}).replace("| D-1 | control_status | missing |", "| D-1 | control_status | maybe |")
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, content=text.encode("utf-8"))
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "unreadable persisted row" in res.err and "control_status is not found, partial or missing" in res.err and "scanned fresh" in res.err
    rows = unit_rows(h)
    assert carried_values(rows["D-1"]) == {} and carried_values(rows["T-2"]) == {key: CARRY_PARTIAL[key] for key in CARRIED}


def test_the_baseline_dir_flag_comes_before_baseline_source_and_a_file_counts_as_its_directory(stage, cli, tmp_path, monkeypatch):
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"T-2": CARRY_PARTIAL})   # baseline.source names prev
    flagged = tmp_path / "baseline-runs" / "flagged"
    flagged.mkdir()
    (flagged / "compensating-controls.md").write_text(controls_md({"D-1": CARRY_MISSING}), encoding="utf-8")
    assert h.plan_cli("--baseline-dir", "baseline-runs/flagged/compensating-controls.md").code == 0
    rows = unit_rows(h)
    assert carried_values(rows["D-1"]) and carried_values(rows["T-2"]) == {}, "the flag's baseline holds D-1 and not T-2"
    assert h.batch_input("B001")["refs"]["baseline_dir"] == str(flagged)


@pytest.mark.parametrize("source,reason", [
    ("none (first run \u2014 stateless mode)", "free-text"), ("baseline-runs/absent/threats.md", "missing"),
    ("../elsewhere/threats.md", "outside-working-directory"),
])
def test_a_baseline_source_that_does_not_resolve_means_a_fresh_scan_and_a_stated_reason(stage, cli, tmp_path, monkeypatch, source, reason):
    h = routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, source=source, name=CONTROLS)
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "WARNING" in res.err and reason in res.err and "scanned fresh" in res.err
    assert "baseline_dir" not in h.plan_json()["refs"] and all(carried_values(row) == {} for row in unit_rows(h).values())


def test_a_baseline_flag_outside_the_working_directory_is_refused_with_its_reason_for_controls_too(stage, cli, tmp_path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "compensating-controls.md").write_text(controls_md({"D-1": CARRY_MISSING}), encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    h = routed(stage, cli, project, monkeypatch, CARRY_STATUSES, name=CONTROLS)
    res = h.plan_cli("--baseline-dir", elsewhere)
    assert res.code == 0 and "outside-working-directory" in res.err and "baseline_dir" not in h.plan_json()["refs"]


def test_a_baseline_controls_file_that_changes_after_plan_is_caught(stage, cli, tmp_path, monkeypatch):
    """The renderer reads the baseline file that the plan read, so an edit between the two exits 2 (D3)."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"T-2": CARRY_PARTIAL})
    assert h.plan_cli().code == 0
    (tmp_path / "baseline-runs" / "prev" / "compensating-controls.md").write_text(controls_md({}), encoding="utf-8")
    assert h.reconcile().code == 2


def test_a_form_without_a_status_column_gets_no_status_so_nothing_is_carried(stage, cli, tmp_path, monkeypatch):
    """The agent spec: a row with no ``delta_status`` has no baseline, so the agent scans it fresh. (The scorer derives UNCHANGED
    from its baseline for such a form, S-12(b); for the controls stage that derivation is not ruled, so none is made.)"""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"T-2": CARRY_PARTIAL, "D-1": CARRY_MISSING})
    h.threats.write_text(without_status_column(h.threats.read_text(encoding="utf-8")), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0 and "has no Status" in res.err and "none is carried forward" in res.err, res.describe()
    assert all("delta_status" not in row and carried_values(row) == {} for row in unit_rows(h).values())


# ---- the threat model is reached through risk-scores.md's validated source_file (D7, D8)

def _break_source(h, tmp_path, kind):
    """Make ``risk-scores.md``'s ``source_file`` unusable, in each way ``check_run_file`` refuses, and return the reason it gives."""
    source = {"free-text": "the scored threat model (first run)", "outside": "../elsewhere/threats.md", "missing": "run/absent/threats.md",
              "wrong-name": "run/other.md"}.get(kind)
    if kind == "wrong-name":
        (h.out / "other.md").write_text(h.threats.read_text(encoding="utf-8"), encoding="utf-8")
    if kind == "symlink":
        real = tmp_path / "real"
        real.mkdir()
        (real / "threats.md").write_text(h.threats.read_text(encoding="utf-8"), encoding="utf-8")
        h.threats.unlink()
        os.symlink(str(real / "threats.md"), str(h.threats))
        source = "run/threats.md"
    h.risk_scores.write_text(make_scored_md(h.ids, source_file=source), encoding="utf-8")
    return {"null": "names no threat model", "free-text": "free-text", "outside": "outside-working-directory", "missing": "missing",
            "wrong-name": "wrong-name", "symlink": "symlink"}[kind]


@pytest.mark.parametrize("kind", ["null", "free-text", "outside", "missing", "wrong-name", "symlink"])
def test_a_source_file_that_cannot_be_used_leaves_each_unit_with_its_id_only(stage, cli, tmp_path, monkeypatch, kind):
    """Nothing here stops a run (D7's spirit, D8): the plan warns, records no threats pointer, and sends the finding IDs. With no
    ``delta_status`` nothing is carried, and the agent reads the rest from ``refs.risk_scores``."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1", "T-2", "D-1"])
    reason = _break_source(h, tmp_path, kind)
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert "threats.md is not read" in res.err and reason in res.err and "finding ID only" in res.err
    assert list(unit_rows(h).values()) == [{"finding_id": "S-1"}, {"finding_id": "T-2"}, {"finding_id": "D-1"}]
    plan = h.plan_json()
    assert "threats" not in plan["refs"] and "threats" not in plan["inputs"] and set(plan["inputs"]) == {"risk_scores"}


@pytest.mark.parametrize("text,expected", [
    ('---\nsource_file: "run/threats.md"\n---\n', "run/threats.md"),
    ('---\r\nsource_file: "run/threats.md"\r\n---\r\n', "run/threats.md"),
    ('\ufeff---\nsource_file: "run/threats.md"\n---\n', "run/threats.md"),
    ("---\nsource_file: 'run/threats.md'\n---\n", "run/threats.md"),
    ("---\nsource_file: run/threats.md\n---\n", "run/threats.md"),
    ('```yaml\n---\nsource_file: "run/threats.md"\n---\n```\n', "run/threats.md"),
    ('---\nsource_file: "a/threats.md"\nsource_file: "b/threats.md"\n---\n', "a/threats.md"),
    ("---\nsource_file: null\n---\n", None), ("---\nsource_file: ~\n---\n", None), ("---\nsource_file:\n---\n", None),
    ('---\nsource_file: ""\n---\n', None), ('---\ndate: "2026-11-22"\n---\n', None),
    ('---\nbaseline:\n  source_file: "run/threats.md"\n---\n', None), ('# No frontmatter\nsource_file: "run/threats.md"\n', None),
], ids=["plain", "crlf", "bom", "single-quoted", "unquoted", "fenced", "first-wins", "null", "tilde", "empty", "empty-quotes", "absent", "nested", "no-frontmatter"])
def test_the_source_file_is_read_from_the_frontmatters_top_level_in_either_form(stage, text, expected):
    """D8's ``source_file``, as the scorer's renderer writes it (a double-quoted scalar, or ``null``) and as the other frontmatter
    readers accept it. What comes back is a candidate: ``check_run_file`` validates it."""
    assert stage._scored_source_file(text) == expected


def test_a_risk_scores_path_that_a_document_cannot_carry_exits_2(stage, cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS)
    res = h.plan_cli("--risk-scores", tmp_path / "a`b.md")
    assert res.code == 2 and "backtick" in res.err and not (h.build / "current.json").exists(), res.describe()


def test_a_threat_model_path_the_working_directory_cannot_carry_exits_2(stage, cli, tmp_path, monkeypatch):
    """The source_file is fine, and the working directory it resolves under holds a backtick, which no document can carry. That is an
    environment fault like ``--out``, so it exits 2 before anything is written, and no warning stands in for it."""
    h = Harness(stage, cli, tmp_path / "clean", CONTROLS, ids=["S-1"])
    odd = tmp_path / "a`b"
    (odd / "run").mkdir(parents=True)
    (odd / "run" / "threats.md").write_text(h.threats.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.chdir(odd)
    res = h.plan_cli()
    assert res.code == 2 and "backtick" in res.err and not (h.build / "current.json").exists(), res.describe()


def test_a_source_file_may_be_spelled_with_dot_components_and_still_reaches_the_threat_model(stage, cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1"])
    h.risk_scores.write_text(make_scored_md(["S-1"], source_file="./run//threats.md"), encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0 and "WARNING" not in res.err and h.plan_json()["refs"]["threats"] == str(h.threats), res.describe()


def test_threats_is_optional_for_controls_and_must_be_the_file_source_file_names(stage, cli, tmp_path, monkeypatch):
    """The command passes no ``--threats`` (the planner reaches the file through ``source_file``). One that is passed has to be that
    file, because the renderer reads the plan's, and one stage must read one threat model (an existing harness passes both)."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    assert h.plan_cli().code == 0
    assert h.plan_cli("--threats", h.threats).code == 0 and h.plan_json()["refs"]["threats"] == str(h.threats)
    assert h.plan_cli("--threats", "run/../run/threats.md").code == 0, "the same file by another spelling"
    other = tmp_path / "other"
    other.mkdir()
    (other / "threats.md").write_text(h.threats.read_text(encoding="utf-8"), encoding="utf-8")
    before = h.plan_id
    refused = h.plan_cli("--threats", other / "threats.md")
    assert refused.code == 2 and "--threats" in refused.err and "source" in refused.err, refused.describe()
    assert h.read_json(h.build / "current.json")["plan_id"] == before == h.plan_id, "a refused plan leaves the pointer alone"
    assert h.plan_cli("--threats", tmp_path / "absent.md").code == 2, "a file that doesn't exist is not the one source_file names"
    h.risk_scores.write_text(make_scored_md(["S-1"], source_file=None), encoding="utf-8")
    ignored = h.plan_cli("--threats", other / "threats.md")
    assert ignored.code == 0 and "--threats is not used by this stage" in ignored.err, "with no source_file there is nothing to contradict"


def test_an_unreadable_section_7_of_the_source_threat_model_stops_the_controls_plan(stage, cli, tmp_path, monkeypatch):
    """S-12(c): an unreadable reference set ends the run before dispatch, for this stage as for the scorer."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, section7="missing")
    res = h.plan_cli()
    assert res.code == 2 and "TACHI COMPENSATING-CONTROLS FAILED" in res.err and "Section 7" in res.err, res.describe()
    assert not (h.build / "current.json").exists()


@pytest.mark.parametrize("missing", ["--risk-scores", "--target"])
def test_the_controls_stage_needs_its_scored_input_and_its_target(stage, cli, tmp_path, monkeypatch, missing):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS)
    given = [] if missing == "--risk-scores" else ["--risk-scores", h.risk_scores]
    given += [] if missing == "--target" else ["--target", h.target]
    res = h.cli("plan", "--stage", CONTROLS, "--out", h.out, "--date", DATE, *given)
    assert res.code == 2 and missing in res.err and not (h.build / "current.json").exists(), res.describe()


def test_the_scorer_still_needs_its_threats(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    res = h.cli("plan", "--stage", "risk-score", "--out", h.out, "--date", DATE)
    assert res.code == 2 and "--threats is required" in res.err


# ---- the SARIF fallback: risk-scores.sarif when risk-scores.md is absent (D8, AR-T2)

SCORE = "6.4"


def make_scores_sarif(ids, peers=None, absent=()):
    """The same shape as ``make_threats_sarif``, scored: one result for each finding, with its findingId/v1 and a composite."""
    return make_threats_sarif(ids, peers=peers, absent=absent, score=SCORE)


def with_composites(sarif_text, score=SCORE):
    """``sarif_text`` with a composite on each result that has none, so a ``threats.sarif`` can stand in for a ``risk-scores.sarif``. A result that has
    one keeps it, and nothing else about a result changes, so a row's text, level and layer are what they were."""
    document = json.loads(sarif_text)
    for result in document["runs"][0]["results"]:
        properties = result.setdefault("properties", {})
        if "composite" not in properties and "security-severity" not in properties:
            properties["composite"] = score
    return json.dumps(document)


def scores_sarif_only(stage, cli, tmp_path, monkeypatch, sarif):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, CONTROLS, ids=["S-1"])
    h.risk_scores.unlink()
    (h.out / "risk-scores.sarif").write_text(sarif, encoding="utf-8")
    return h


def test_controls_fall_back_to_risk_scores_sarif_when_the_markdown_is_absent(stage, cli, tmp_path, monkeypatch):
    """Every member is a unit, peers included, in S-2 order and canonical. The SARIF names no threat model, so a row holds what the
    member's own result gives (D8's details, P0-3), and the plan's input and ref are the SARIF that was read."""
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, make_scores_sarif(["T-2", "S-1", "AGP-01", "I-3"], peers={"I-3": "S-1"}))
    res = h.plan_cli("--threats", h.threats)
    assert res.code == 0, res.describe()
    assert "risk-scores.sarif" in res.err and "WARNING" in res.err and "--threats is not used by this stage" in res.err
    assert "only what its own result in the SARIF gives" in res.err and "finding ID only" not in res.err
    assert agent_ids(h) == ["S-1", "T-2", "I-3", "AGP-1"]
    sarif = h.out / "risk-scores.sarif"
    plan = h.plan_json()
    assert plan["refs"] == {"risk_scores": str(sarif), "target": str(h.target)} and set(plan["inputs"]) == {"risk_scores"}
    assert plan["inputs"]["risk_scores"]["sha256"] == sha256_of(sarif)
    assert list(unit_rows(h).values()) == [{"finding_id": fid, "threat": "a finding"} for fid in ("S-1", "T-2", "I-3", "AGP-1")]


def test_results_the_scores_sarif_marks_absent_are_resolved_and_are_not_planned(stage, cli, tmp_path, monkeypatch):
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, make_scores_sarif(["S-1", "T-2", "D-1"], absent=["T-2"]))
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "D-1"]


@pytest.mark.parametrize("sarif", ['{"version": "2.1.0", "runs": [{"results": []}]}', '{"runs": []}', "[]",
                                   '{"runs": [{"results": [{"partialFingerprints": {"findingId/v1": "not an id"}}]}]}'],
                         ids=["no-results", "no-runs", "not-an-object", "no-valid-id"])
def test_an_empty_extraction_from_the_scores_sarif_stops_before_dispatch(stage, cli, tmp_path, monkeypatch, sarif):
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, sarif)
    res = h.plan_cli()
    assert res.code == 2, res.describe()
    assert "TACHI COMPENSATING-CONTROLS FAILED" in res.err and "risk-scores.sarif" in res.err
    assert not (h.build / "current.json").exists() and not list(h.out.glob(".tachi-build/compensating-controls/*/plan.json"))


@pytest.mark.parametrize("text", ["{not json", '{"runs": [{"results": [{"x": NaN}]}]}'], ids=["not-json", "nan"])
def test_a_scores_sarif_that_is_not_strict_json_stops_before_dispatch(stage, cli, tmp_path, monkeypatch, text):
    h = scores_sarif_only(stage, cli, tmp_path, monkeypatch, text)
    assert h.plan_cli().code == 2 and not (h.build / "current.json").exists()


def test_risk_scores_md_wins_when_both_exist_and_the_fallback_has_no_other_file(stage, cli, tmp_path, monkeypatch):
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW", "T-2": "NEW"})
    (h.out / "risk-scores.sarif").write_text(make_scores_sarif(["D-1"]), encoding="utf-8")
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "T-2"]
    h.risk_scores.unlink()
    (h.out / "risk-scores.sarif").unlink()
    assert h.plan_cli().code == 1, "neither input is there"
    (h.out / "threats.sarif").write_text(make_threats_sarif(["S-1"]), encoding="utf-8")
    assert h.plan_cli().code == 1, "the scorer's fallback is not the controls stage's"
    renamed = h.cli("plan", "--stage", CONTROLS, "--out", h.out, "--date", DATE, "--risk-scores", h.out / "renamed.md", "--target", h.target)
    assert renamed.code == 1, "only risk-scores.md has a SARIF to fall back to"


# =========================================================================== a character that step 10 forbids ends the plan before dispatch (P0-4, SA-1)
#
# Step 10 checks a part, and a batch input carries text that no part check has seen: each row's text, from threats.md or a SARIF, and, for an
# UNCHANGED controls finding, the baseline's persisted result, which the agent copies into its part verbatim. One forbidden character in that
# result made the part invalid on every attempt (the advisory's probe K: exit 3, 3, then 4, with the whole batch exhausted), and the renderer
# refuses a row's text only after every agent has run. So the planner refuses it first, with exit 2, naming the finding, the field and the
# file, and giving the character's code point and never the character.

FORBIDDEN_CHARACTERS = {"escape": "\x1b", "bidi-override": chr(0x202E), "line-separator": chr(0x2028), "next-line": "\x85", "carriage-return": "\r"}
ESC = FORBIDDEN_CHARACTERS["escape"]
REGENERATE = "regenerate %s with %s, or edit the value to remove the character, then re-run the command"


def assert_forbidden_refusal(h, res, char, where, field, finding_id, command):
    """Exit 2 before anything is written: the message names the file, the character's code point, the field and the finding, and the remedy
    names the file and the command. The character itself is nowhere in the output."""
    assert res.code == 2, res.describe()
    assert ("TACHI %s FAILED: %s holds the character U+%04X, which the part contract forbids, in the %s of %s"
            % (h.name.upper(), where, ord(char), field, finding_id)) in res.err, res.describe()
    assert "Remedy: " + REGENERATE % (where, command) in res.err, res.describe()
    assert char not in res.err and char not in res.out, "the code point is given, never the text"
    assert not (h.build / "current.json").exists() and not list(h.out.glob(".tachi-build/*/*/plan.json")), "nothing is written"


@pytest.mark.parametrize("kind", sorted(FORBIDDEN_CHARACTERS))
@pytest.mark.parametrize("field,cell", [("threat", "Threat text for T-2"), ("mitigation", "Mitigation text for T-2")])
def test_a_character_that_step_10_forbids_in_a_scorer_row_ends_the_plan_before_dispatch(stage, cli, tmp_path, kind, field, cell):
    char = FORBIDDEN_CHARACTERS[kind]
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["S-1", "T-2"])
    h.threats.write_bytes(h.threats.read_bytes().replace(cell.encode(), cell.replace("text", char + "text").encode("utf-8")))
    assert_forbidden_refusal(h, h.plan_cli(), char, "threats.md", field, "T-2", "/tachi.threat-model")


SARIF_FIELDS = [
    ("component", dict(name="Gate" + ESC + "way")), ("threat", dict(text="a" + ESC + "b")), ("mitigation", dict(markdown="a" + ESC + "b")),
    ("layer", dict(properties={"maestro-layer": "L" + ESC + "3"})), ("risk_level", dict(properties={"risk_level": "Hi" + ESC + "gh"})),
]


@pytest.mark.parametrize("name", STAGE_NAMES)
@pytest.mark.parametrize("field,result", SARIF_FIELDS, ids=[field for field, _ in SARIF_FIELDS])
def test_a_character_that_step_10_forbids_in_a_sarif_fallback_row_ends_the_plan_before_dispatch(stage, cli, tmp_path, monkeypatch, name, field, result):
    """Each stage names its own SARIF and the command that writes it. (A lone surrogate, which only JSON can spell, is refused as it always was.)"""
    sarif = sarif_of(detail_result("S-1", name="Gateway", text="a threat"), detail_result("T-2", **result))
    h = fallback_only(stage, cli, tmp_path, monkeypatch, sarif, name)
    where, command = ("threats.sarif", "/tachi.threat-model") if name == "risk-score" else ("risk-scores.sarif", "/tachi.risk-score")
    assert_forbidden_refusal(h, h.plan_cli(), ESC, where, field, "T-2", command)


@pytest.mark.parametrize("field,cell,finding_id", [("mitigation", "Mitigation text for T-2", "T-2"), ("layer", "L4 " + _DASH + " Deployment", "S-1")])
def test_a_character_that_step_10_forbids_in_a_controls_row_names_the_threat_model(stage, cli, tmp_path, monkeypatch, field, cell, finding_id):
    """The row's text comes from the ``threats.md`` that ``risk-scores.md`` names. The layer is in the row too, and the first row in plan order is named."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW", "T-2": "NEW"})
    h.threats.write_bytes(h.threats.read_bytes().replace(cell.encode("utf-8"), (cell[:3] + ESC + cell[3:]).encode("utf-8")))
    assert_forbidden_refusal(h, h.plan_cli(), ESC, "threats.md", field, finding_id, "/tachi.threat-model")


# What an UNCHANGED finding's row carries: each field of a persisted result that the agent copies back, whose text the reader doesn't check.
# (``evidence.0.file`` isn't here: the reader holds it to D7's path rule, and a row that fails it is scanned fresh, with a warning.)
CARRY_FIELDS = [
    ("evidence.0.summary", lambda item, char: item["evidence"][0].update(summary="Checks" + char + " a")),
    ("evidence.0.snippet", lambda item, char: item["evidence"][0].update(snippet="x = 1" + char + "[0m")),
    ("evidence.0.assessment.coverage.rationale",
     lambda item, char: item["evidence"][0]["assessment"]["coverage"].update(rationale="The check" + char + " is deep")),
    ("matrix_row", lambda item, char: item.update(matrix_row=item["matrix_row"].replace("A <threat>", "A " + char + "<threat>"))),
    ("recommendation_body", lambda item, char: item.update(recommendation_body=item["recommendation_body"].replace("Validate", "Val" + char + "idate"))),
]


@pytest.mark.parametrize("kind", ["bidi-override", "escape"])
@pytest.mark.parametrize("field,change", CARRY_FIELDS, ids=[field for field, _ in CARRY_FIELDS])
def test_a_character_that_step_10_forbids_in_a_baselines_persisted_result_ends_the_plan_before_dispatch(stage, cli, tmp_path, monkeypatch, field, change, kind):
    """Probe K of the advisory: the planner carried the value, the agent copied it into a part, step 10 refused the part, and ``reconcile`` re-dispatched
    the same batch (exit 3, 3, then 4), as often as the baseline was used. It now stops at the plan, and names the baseline's file and the field."""
    char = FORBIDDEN_CHARACTERS[kind]
    item = json.loads(json.dumps(CARRY_PARTIAL))
    change(item, char)
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"T-2": item, "D-1": CARRY_MISSING})
    assert_forbidden_refusal(h, h.plan_cli(), char, "the baseline compensating-controls.md", field, "T-2", "/tachi.compensating-controls")


def test_a_persisted_result_that_nothing_carries_is_not_checked(stage, cli, tmp_path, monkeypatch):
    """Only what a batch input would carry is refused. R-1 is UPDATED, so it is scanned fresh and its persisted result is not copied into its row."""
    item = json.loads(json.dumps(CARRY_MISSING))
    item["recommendation_body"] = item["recommendation_body"].replace("Add one", "Add" + ESC + " one")
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"R-1": item, "D-1": CARRY_MISSING})
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    assert carried_values(unit_rows(h)["R-1"]) == {} and carried_values(unit_rows(h)["D-1"]) != {}


def test_the_walk_for_a_forbidden_character_reads_text_keys_and_lists_and_nothing_else(stage):
    walk = stage._first_forbidden
    assert [walk(value, "x") for value in ("clean", "", 7, None, True, 1.5, ("a\x1b",), {"ok": 1})] == [None] * 8
    assert walk("a\x1bb", "x") == ("x", "\x1b")
    assert walk({"a": ["ok", {"b": "c" + chr(0x202E) + "d"}]}, "x") == ("x.a.1.b", chr(0x202E))
    assert walk({"k\x00ey": "fine"}, "x") == ("x.k\x00ey", "\x00"), "a key is text too"
    assert walk([0, "\ud800"], "x") == ("x.1", "\ud800"), "a lone surrogate is in the set (ruled at W3)"


# =========================================================================== SA-10 and S7-4: what the planner reads through a link, or with no cap
#
# A path that the planner derives (the SARIF beside a markdown input) lies in a directory that a repository may fill, and git stores symlinks. A
# file whose digest becomes a plan input is read at most 16 MiB and through no link, as every other input is.

SIBLINGS = {"risk-score": "threats.sarif", CONTROLS: "risk-scores.sarif"}


@pytest.mark.parametrize("kind", ["symlink", "dangling-symlink", "directory"])
@pytest.mark.parametrize("name", STAGE_NAMES)
def test_a_derived_sarif_that_is_a_link_or_not_a_file_is_left_unread(stage, cli, tmp_path, monkeypatch, name, kind):
    """Probe O of the advisory: a ``threats.sarif`` that was a symlink to a file outside the run directory was planned (33 units). It is left unread,
    with a warning, and the plan goes on by its rules for a markdown input that isn't there: exit 1."""
    h = fallback_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1", "T-2"]), name)
    sibling = h.out / SIBLINGS[name]
    outside = tmp_path / "outside.sarif"
    sibling.rename(outside)
    if kind == "symlink":
        os.symlink(str(outside), str(sibling))
    elif kind == "dangling-symlink":
        os.symlink(str(tmp_path / "nowhere.sarif"), str(sibling))
    else:
        sibling.mkdir()
    res = h.plan_cli()
    assert res.code == 1 and "cannot read" in res.err, res.describe()
    assert "WARNING: %s is a symbolic link or not a regular file, so it is not read as the fallback input" % sibling in res.err
    assert "the SARIF fallback" not in res.err and not (h.build / "current.json").exists()


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_a_sibling_link_is_not_looked_at_when_the_markdown_is_there(stage, cli, tmp_path, monkeypatch, name):
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, name, ids=["S-1"])
    os.symlink(str(tmp_path / "nowhere.sarif"), str(h.out / SIBLINGS[name]))
    res = h.plan_cli()
    assert res.code == 0 and "WARNING" not in res.err, res.describe()


def test_a_sibling_that_is_a_regular_file_in_a_directory_reached_through_a_link_is_read(stage, cli, tmp_path, monkeypatch):
    """The guard is over the file's own directory, so a link in that directory's path is followed, as it always was: only the file may not be one."""
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1", "T-2"]))
    (tmp_path / "linked").symlink_to(h.out, target_is_directory=True)
    res = h.cli("plan", "--stage", "risk-score", "--out", h.out, "--date", DATE, "--threats", tmp_path / "linked" / "threats.md")
    assert res.code == 0 and "the SARIF fallback" in res.err, res.describe()


def test_a_scorer_pointer_file_that_is_a_link_is_refused(stage, cli, tmp_path, monkeypatch):
    """S7-4: ``--risk-scores`` of the scorer was read whole, through any link, with no cap, and became a digest-checked input."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:3])
    (tmp_path / "real-scores.md").write_text("# scores\n", encoding="utf-8")
    os.symlink(str(tmp_path / "real-scores.md"), str(h.out / "risk-scores.md"))
    res = h.plan_cli("--risk-scores", h.out / "risk-scores.md")
    assert res.code == 2 and "risk-scores.md is a symbolic link or not a regular file" in res.err, res.describe()
    assert "Remedy: name the file itself, not a link to it" in res.err and not (h.build / "current.json").exists()


def test_a_scorer_pointer_file_over_the_cap_is_refused(stage, cli, tmp_path, monkeypatch):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:3])
    cap = h.threats.stat().st_size + 10
    monkeypatch.setattr(stage.tp, "MAX_AGENT_INPUT_BYTES", cap)  # D3 step 2's 16 MiB, made small: threats.md fits, the pointer file doesn't
    (h.out / "risk-scores.md").write_bytes(b"x" * (cap + 1))
    res = h.plan_cli("--risk-scores", h.out / "risk-scores.md")
    assert res.code == 2 and "risk-scores.md is over %d bytes" % cap in res.err and "Remedy: name a smaller file" in res.err, res.describe()
    assert not (h.build / "current.json").exists()


# =========================================================================== the controls row's MAESTRO layer
#
# The agent copies its row's ``layer`` into its Section 2 cell, and the renderer checks that cell against its own chain: the MAESTRO Layer cell of the
# finding's Section 7 row, else its component's Section 1 layer (found by name, then case-folded), else ``Unclassified``. A row without the layer left
# the agent to read the whole risk-scores.md for it, or to write ``Unclassified``, which the renderer flags for every classified finding.

COMPONENTS_TABLE = [("Alpha", "Process", "L5 " + _DASH + " Evaluation and Observability"), ("Beta", "Process", "L3 " + _DASH + " Agent Frameworks"),
                    ("Gamma", "Process", ""), ("GAMMA", "Process", "L6 " + _DASH + " Security and Compliance")]
LAYER_CELLS = {
    "S-1": ("Alpha", "L2 " + _DASH + " Data Operations"),   # a Section 7 cell comes first, whatever its component's layer is
    "T-2": ("Beta", ""),                                    # blank: the component's Section 1 layer
    "I-3": ("beta", ""),                                    # the same component in another case: found once the name isn't
    "D-1": ("Delta", ""),                                   # blank, and Section 1 doesn't list it
    "D-2": ("", ""),                                        # no component at all: ``Unspecified``, which Section 1 doesn't list either
    "E-1": ("Gamma", ""),                                   # the name is listed, with no layer: that is the answer, and ``GAMMA`` isn't tried
    "R-1": ("GAMMA", ""),                                   # an exact name of its own
}
LAYERS = {"S-1": "L2 " + _DASH + " Data Operations", "T-2": "L3 " + _DASH + " Agent Frameworks", "I-3": "L3 " + _DASH + " Agent Frameworks",
          "D-1": "Unclassified", "D-2": "Unclassified", "E-1": "Unclassified", "R-1": "L6 " + _DASH + " Security and Compliance"}


def with_layers(text, cells, components=COMPONENTS_TABLE):
    """``text`` with the Component and MAESTRO Layer cells of the listed Section 7 rows set (``{finding ID: (component, layer)}``), and a ``### Components``
    table in Section 1: the two tables that the renderer reads a layer from."""
    lines = text.split("\n")
    for number, line in enumerate(lines):
        for finding_id, (component, layer) in cells.items():
            if line.startswith("| %s | " % finding_id):
                parts = line.split(" | ")
                parts[4], parts[5] = component, layer
                lines[number] = " | ".join(parts)
    table = ["### Components", "", "| Component | Type | MAESTRO Layer |", "|---|---|---|"] + ["| %s | %s | %s |" % row for row in components] + [""]
    return "\n".join(lines).replace("A synthetic system for the tests.\n", "A synthetic system for the tests.\n\n" + "\n".join(table), 1)


def renderer_layers(controls_renderer, threats_text):
    """The layer that the controls renderer gives each open finding of this threat model, by canonical ID (``_read_reference``, then ``_overlay_reference``).
    The scored input's own component is what the scorer writes for a row that has none: ``Unspecified``."""
    run = controls_renderer.Run()
    run.threats_text, run.threats_path = threats_text, "threats.md"
    reference = controls_renderer._read_reference(run, "kept")
    members = [{"id": finding["id"], "canon": canon(finding["id"]), "component": "Unspecified", "threat": "", "layer": ""} for finding in reference["open"]]
    controls_renderer._overlay_reference(run, members, reference)
    return {member["canon"]: member["layer"] for member in members}


def test_a_controls_row_holds_the_layer_by_the_renderers_chain(stage, cli, controls_renderer, tmp_path, monkeypatch):
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {finding_id: "NEW" for finding_id in LAYER_CELLS})
    text = with_layers(h.threats.read_text(encoding="utf-8"), LAYER_CELLS)
    h.threats.write_text(text, encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    layers = {finding_id: row["layer"] for finding_id, row in unit_rows(h).items()}
    assert layers == LAYERS
    assert layers == renderer_layers(controls_renderer, text), "the planner's layer is the renderer's, finding by finding"


def test_a_numbered_list_section_7_gives_every_row_the_unclassified_layer_as_the_renderer_does(stage, cli, controls_renderer, tmp_path, monkeypatch):
    """The list form of Section 7 (S-12(a)) has no component and no layer cell, so a row's component is ``Unspecified``, which no Section 1 row
    lists, and its layer is ``Unclassified``: the planner reads it, and the renderer gives each finding the same."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW", "T-2": "NEW"})
    head = h.threats.read_text(encoding="utf-8").split("## 7. Recommended Actions")[0]
    text = head + "## 7. Recommended Actions\n\n1. **S-1** " + _DASH + " Add authentication\n2. **T-2** " + _DASH + " Validate input\n"
    h.threats.write_text(text, encoding="utf-8")
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    layers = {finding_id: row["layer"] for finding_id, row in unit_rows(h).items()}
    assert layers == {"S-1": "Unclassified", "T-2": "Unclassified"} == renderer_layers(controls_renderer, text)


# The v4.48.x form (T066's U-1, ADR-050 D2's chain, step 2): a threat model of that version holds each finding's layer in the MAESTRO Layer column of its
# own row in a §3 or §4 table, and in no Section 7 or Section 1 cell. ``tachi_parsers.parse_finding_layers`` reads those rows for the planner and both
# renderers, so a row's ``layer`` and the renderer's ``maestro-layer`` are one value (a second copy of the chain would flag every such finding).

FINDING_TABLE_HEAD = ["| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |", "|---|---|---|---|---|---|---|---|---|"]
DATA_OPS, ECOSYSTEM, SECURITY, FOUNDATION = ("L2 " + _DASH + " Data Operations", "L7 " + _DASH + " Agent Ecosystem", "L6 " + _DASH + " Security and Compliance",
                                             "L1 " + _DASH + " Foundation Model")
FINDING_TABLES = "\n".join(
    ["## 3. STRIDE Threat Tables", "", "### 3.1 Spoofing (S)", ""] + FINDING_TABLE_HEAD + [
        "| S-1 | [NEW] | Alpha | %s | A threat. | Medium | High | High | A fix. |" % DATA_OPS,          # Alpha's Section 1 layer is L5: the row comes first
        "| I-3 | [NEW] | beta | %s | A threat. | Medium | High | High | A fix. |" % ECOSYSTEM,       # Section 7's cell is set too, and comes before it
        "| D-1 | [NEW] | Delta | | A threat. | Medium | High | High | A fix. |",                       # a blank cell gives nothing
        "", "## 4. AI Threat Tables", "", "### 4.2 LLM Threats (LLM)", "", "---", "", "**OI Findings (Output Integrity)**:", ""] + FINDING_TABLE_HEAD + [
        "| D-2 | [NEW] |  | %s | A threat. | Medium | High | High | A fix. |" % SECURITY,              # a bold-labelled sub-table, and a row with no component
        "| R-1 | [NEW] | GAMMA | %s | Output piped through cat \\| sh | Medium | High | High | A fix. |" % FOUNDATION,   # a GFM pipe after the layer cell
        "", "```"] + FINDING_TABLE_HEAD + [
        "| E-1 | [NEW] | Gamma | L3 " + _DASH + " Agent Framework | A threat. | Medium | High | High | A fix. |", "```", ""])
V48_CELLS = {"S-1": ("Alpha", ""), "T-2": ("Beta", ""), "I-3": ("beta", FOUNDATION), "D-1": ("Delta", ""), "D-2": ("", ""), "E-1": ("Gamma", ""), "R-1": ("GAMMA", "")}
V48_LAYERS = {"S-1": DATA_OPS,                      # its own row, ahead of Alpha's Section 1 layer
              "T-2": "L3 " + _DASH + " Agent Frameworks",   # no row of its own: Beta's Section 1 layer, as before
              "I-3": FOUNDATION,                    # Section 7's cell, ahead of its row's
              "D-1": "Unclassified",                # a blank cell, and Section 1 doesn't list Delta
              "D-2": SECURITY,                      # a sub-table's row
              "E-1": "Unclassified",                # its only row is quoted in a code fence, and Gamma's Section 1 cell is blank
              "R-1": FOUNDATION}                    # a row wider than its header, read by position, ahead of GAMMA's Section 1 layer


def with_finding_tables(text, tables=FINDING_TABLES):
    """``text`` with the §3 and §4 tables of a v4.48.x threat model, ahead of Section 6."""
    assert "## 6. Risk Summary" in text
    return text.replace("## 6. Risk Summary", tables + "\n## 6. Risk Summary", 1)


def v48_project(stage, cli, tmp_path, monkeypatch):
    h = controls_routed(stage, cli, tmp_path, monkeypatch, {finding_id: "NEW" for finding_id in V48_CELLS})
    text = with_finding_tables(with_layers(h.threats.read_text(encoding="utf-8"), V48_CELLS))
    h.threats.write_text(text, encoding="utf-8")
    return h, text


def test_a_controls_row_holds_the_layer_of_its_own_row_in_a_per_finding_table_as_the_renderer_gives_it(stage, cli, controls_renderer, tmp_path, monkeypatch):
    h, text = v48_project(stage, cli, tmp_path, monkeypatch)
    res = h.plan_cli()
    assert res.code == 0, res.describe()
    layers = {finding_id: row["layer"] for finding_id, row in unit_rows(h).items()}
    assert layers == V48_LAYERS
    assert layers == renderer_layers(controls_renderer, text), "the planner's layer is the renderer's, finding by finding: one reader gives both steps 1 and 2"


def test_a_per_finding_table_that_a_code_fence_quotes_gives_no_layer_in_the_plan_or_the_renderer(stage, cli, controls_renderer, tmp_path, monkeypatch):
    h, text = v48_project(stage, cli, tmp_path, monkeypatch)
    assert h.plan_cli().code == 0
    assert unit_rows(h)["E-1"]["layer"] == renderer_layers(controls_renderer, text)["E-1"] == "Unclassified"
    unquoted = text.replace("```\n", "")
    assert "```" not in unquoted and renderer_layers(controls_renderer, unquoted)["E-1"] == "L3 " + _DASH + " Agent Framework", "premise: without the fence, the row is read"


def test_a_character_that_step_10_forbids_in_a_layer_that_a_per_finding_row_gives_ends_the_plan_naming_the_finding(stage, cli, tmp_path, monkeypatch):
    h, text = v48_project(stage, cli, tmp_path, monkeypatch)
    h.threats.write_text(text.replace(DATA_OPS, "L2 " + ESC + _DASH + " Data Operations", 1), encoding="utf-8")
    assert_forbidden_refusal(h, h.plan_cli(), ESC, "threats.md", "layer", "S-1", "/tachi.threat-model")


def test_a_carried_row_holds_its_layer_too_and_the_layer_is_not_a_carried_key(stage, cli, tmp_path, monkeypatch):
    """The layer is the current threat model's, like the row's other text. It is not in the baseline's persisted result, which holds the
    judgment values only."""
    h = controls_routed(stage, cli, tmp_path, monkeypatch, CARRY_STATUSES, {"T-2": CARRY_PARTIAL})
    assert h.plan_cli().code == 0
    row = unit_rows(h)["T-2"]
    assert row["layer"] == "L4 " + _DASH + " Deployment" and "layer" not in CARRIED and carried_values(row) != {}


# =========================================================================== PR 2: tachi-stage.py's new modes (F-374 T092, tests first)
#
# Written at W2' while the #443 hoist runs, and before the code, from ADR-050 rev. 3 (D3, D4, D6, D7's ruling B, D11 to D15) and the contracts
# (cli.md; part-files.md sections 4 to 6 and the stage payloads; threat-model-records.md). They drive ``main(argv)`` in-process through the ``cli``
# fixture and look only at what a caller can see: what a command prints, its exit code, the files it writes, and the stage records. The hoist moves
# the stage-entry plumbing into ``tachi_parts``, so no private helper is named here.
#
# Before T092's code they failed, and each failure named the missing behavior (``needs``). A negative case first shows that the mode exists: a
# refusal prints D4's ``TACHI <STAGE> FAILED`` message (``refused``), which an argparse usage error does not, so no refusal passes for the wrong
# reason. A shape that the contracts leave open is pinned as a reading, marked ``# reading:``, and listed for the architect in the lane's results file.
# T092's code, which follows the architect's pass-3 rulings (S1P-A43 to S1P-A63), needs two functions of ``tachi_parsers`` that lane OC writes:
# ``parse_chain_outcome`` (T116's first slice) for the report plan and ``attack_tree_source`` (T159) for ``reconcile --stage trees``.

THREAT_MODEL = "threat-model"
TM_OUTPUTS = ("threats.md", "threats.sarif", "threat-report.md", "attack-chains.md")  # ADR-050 D4's closed set for the run, in its order
TM_AGENT = "tachi-orchestrator"
TM_EARLIER = {name: ("# the earlier run's %s\n" % name).encode("utf-8") for name in TM_OUTPUTS}
TM_NEW = {name: ("# a run that went wrong: %s\n" % name).encode("utf-8") for name in TM_OUTPUTS}
FAKE_PLAN_ID = "20261122T000000Z-0123456789ab"
ODD_MODES = {"threats.md": 0o604, "threats.sarif": 0o640, "threat-report.md": 0o620, "attack-chains.md": 0o642}  # none is a new file's ordinary mode


def needs(res, code, behavior):
    """The first assertion of a new case: until T092's code lands the command isn't there, and the failure names what is missing."""
    assert res.code == code, "T092, %s: expected exit %d, got %d\n%s" % (behavior, code, res.code, res.describe())
    return res


def refused(res, label, behavior, code=2):
    """A refusal is D4's four-line message with its code, never an argparse usage error (AR-T5)."""
    assert res.code == code and re.search(r"^TACHI %s FAILED: " % label, res.err, re.M) and "Remedy: " in res.err, (
        "T092, %s: expected a refusal (exit %d, a 'TACHI %s FAILED' message with its Remedy)\n%s" % (behavior, code, label, res.describe()))
    return res


class RunDir(object):
    """One run directory and one stage of PR 2 (``name``), with the calls every test makes. The stage's plan is the one ``plan_cli`` made last."""

    def __init__(self, stage, cli, root, name=THREAT_MODEL):
        self.stage, self.cli, self.name = stage, cli, name
        self.root = Path(root)
        self.out = self.root / "run"
        self.out.mkdir(parents=True, exist_ok=True)
        self.plan_id = self.digest = None

    @property
    def build(self):
        return self.out / ".tachi-build" / self.name

    @property
    def plan_dir(self):
        return self.build / self.plan_id

    @staticmethod
    def read_json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def plan_json(self):
        return self.read_json(self.plan_dir / "plan.json")

    def record(self):
        return self.read_json(self.plan_dir / "stage-record.json")

    def batch_input(self, batch_id):
        return self.read_json(self.plan_dir / "inputs" / ("%s.json" % batch_id))

    def plan_args(self, plan_id=None, digest=None):
        return ["--plan", plan_id or self.plan_id, "--plan-digest", digest or self.digest]

    def plan_cli(self, *extra):
        res = self.cli("plan", "--stage", self.name, "--out", self.out, "--date", DATE, *extra)
        if res.code == 0:
            printed = res.json
            self.plan_id, self.digest = printed["plan_id"], printed["plan_digest"]
        return res

    def reconcile(self, plan_id=None, digest=None):
        res = self.cli("reconcile", "--stage", self.name, "--out", self.out, *self.plan_args(plan_id, digest))
        if res.code in (0, 3, 4):
            self.digest = res.json["plan_digest"]
        return res

    def fail(self, reason="check-failed", detail=None, plan_id=None, digest=None):
        extra = ["--detail", detail] if detail is not None else []
        return self.cli("fail", "--stage", self.name, "--out", self.out, *self.plan_args(plan_id, digest), "--reason", reason, *extra)

    def close(self, plan_id=None, digest=None):
        return self.cli("close", "--stage", self.name, "--out", self.out, *self.plan_args(plan_id, digest))

    # ---- the run's four files
    def earlier(self, names=TM_OUTPUTS):
        """The outputs of an earlier successful run, before the plan takes its pre-images."""
        for name in names:
            (self.out / name).write_bytes(TM_EARLIER[name])

    def run_wrote(self, names=TM_OUTPUTS):
        """What a run that got part way did: it replaced these canonical files."""
        for name in names:
            (self.out / name).write_bytes(TM_NEW[name])

    def assert_earlier_outputs_untouched(self, names=TM_OUTPUTS):
        for name in names:
            assert (self.out / name).read_bytes() == TM_EARLIER[name], name

    # ---- the checks' hand-off files (part-files.md section 6)
    def write_handoff(self, check, warnings=(), error=None, mutate=None, raw=None):
        path = self.plan_dir / "checks" / ("%s.json" % check)
        path.parent.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            path.write_bytes(raw)
        else:
            body = handoff(check, self.plan_id, warnings, error)
            if mutate is not None:
                mutate(body)
            path.write_text(json.dumps(body, indent=2), encoding="utf-8")
        return path


# The key set of ``tachi.check-handoff/1`` (``contracts/part-files.md`` section 6, fixed at rev. 3 by T088), with the counts and Phase 2's six batch counts
# that ``check-threat-model.py`` writes into ``provenance.json``. ``attack-chains.json`` has ``null`` for counts, batches and error.
HANDOFF_SCHEMA = "tachi.check-handoff/1"
PROVENANCE_COUNTS = {"open": 12, "resolved": 3, "recorded": 9, "carried": 2, "rule": 1, "renumbered": 1, "folded": 0, "reused-id": 0}
PHASE2_BATCHES = {"planned": 6, "dispatched": 8, "done": 6, "retried": 2, "split": 1, "exhausted": 0}
PROVENANCE_ERROR = {"code": "provenance", "message": "2 findings have no provenance entry: T-1, T-2", "finding_ids": ["T-1", "T-2"],
                    "remedy": "re-run /tachi.threat-model"}
WARN_CHAIN = {"code": "chain-outcome:rewritten", "detail": "recorded as skipped (attack-chains.md missing); no chain file was quarantined"}
WARN_SECTION6 = {"code": "section6:mismatch", "detail": "Section 6, row High: the cell says 3 and the reference set says 4"}
WARN_REISSUED = {"code": "id:reissued", "detail": "2 NEW findings carry an ID the baseline used: T-3, T-4"}
WARN_GAP = {"code": "coverage-gap:unrecovered:no_end_marker", "detail": "dsp-009, tachi-spoofing, component Gateway"}
WARN_REPEATED = {"code": "correlation-member-repeated", "detail": "Section 4a lists 1 finding in more than one group: T-2"}


def handoff(check, plan_id, warnings=(), error=None):
    """A valid ``tachi.check-handoff/1`` object. The status follows ``error``, then ``warnings`` (section 6), and ``attack-chains`` is never ``fail``."""
    provenance = check == "provenance"
    status = "fail" if provenance and error else ("warn" if warnings else "pass")
    return {"schema": HANDOFF_SCHEMA, "check": check, "plan_id": plan_id, "status": status,
            "counts": dict(PROVENANCE_COUNTS) if provenance else None, "batches": dict(PHASE2_BATCHES) if provenance else None,
            "warnings": [dict(w) for w in warnings], "error": dict(error) if provenance and error else None}


def closeable(stage, cli, root, chain=True, earlier=True, wrote=TM_OUTPUTS):
    """A run that reached Step 2.10: the earlier files, the run-level plan, the files this run wrote, and both hand-off files."""
    h = RunDir(stage, cli, root)
    if earlier:
        h.earlier()
    needs(h.plan_cli(), 0, "plan --stage threat-model, the run-level plan")
    h.run_wrote(wrote)
    if chain:
        h.write_handoff("attack-chains")
    h.write_handoff("provenance")
    return h


def assert_not_closed(h, plan_id=None):
    """A close that refuses leaves no success record: its record, if one exists, says ``failed``."""
    path = h.build / (plan_id or h.plan_id) / "stage-record.json"
    assert not path.exists() or h.read_json(path)["status"] == "failed", "a close that exits 2 must not leave a success record"


def check_close_record(rec, h, version, status):
    """The run-level stage record that ``close`` writes (``part-files.md`` section 5, PR 2's stage records)."""
    assert set(rec) == RECORD_KEYS and rec["schema"] == "tachi.stage-record/1"
    assert (rec["stage"], rec["plan_id"], rec["status"]) == (THREAT_MODEL, h.plan_id, status)
    assert rec["tachi_version"] == version and ISO_UTC.match(rec["started_utc"]) and ISO_UTC.match(rec["finished_utc"])
    assert re.match(r"^sha256:[0-9a-f]{64}\Z", rec["input_digest"])
    assert rec["overflow_events"] == [] and rec["retries"] == [], "Phase 2's events stay in its records (item O-alpha)"
    assert rec["error"] is None
    return rec


# ---------------------------------------------------------------------------- the run-level plan (Step 1.5; ADR-050 D4, ``part-files.md`` section 4)


def test_the_run_level_plan_plans_no_units_and_prints_the_plan_object(stage, cli, tmp_path, tachi_version):
    """D4's Step 1.5: ``plan --stage threat-model`` takes no ``--threats`` and plans no units, so it prints no waves and has no batches. It exists
    so that ``fail`` and ``close`` have a plan to read."""
    h = RunDir(stage, cli, tmp_path)
    printed = needs(h.plan_cli(), 0, "plan --stage threat-model, the run-level plan").json
    assert set(printed) == {"plan_id", "plan_digest", "waves"} and PLAN_ID.match(printed["plan_id"]) and printed["waves"] == []
    plan = h.plan_json()
    assert set(plan) == PLAN_KEYS and plan["schema"] == "tachi.plan/1"
    assert (plan["plan_id"], plan["stage"], plan["agent_type"]) == (printed["plan_id"], THREAT_MODEL, TM_AGENT)
    assert plan["tachi_version"] == tachi_version and ISO_UTC.match(plan["created_utc"])
    assert (plan["unit_count"], plan["batches"], plan["batch_size"]) == (0, [], None), "no units, so a null batch size (section 4)"
    assert plan["retry_budget"] == {"limit": 0, "used": 0} and plan["architecture_warning"] is None
    assert sha256_of(h.plan_dir / "plan.json") == printed["plan_digest"]
    assert h.read_json(h.build / "current.json") == {"schema": "tachi.plan-pointer/1", "plan_id": printed["plan_id"]}
    assert not (h.plan_dir / "inputs").exists() or list((h.plan_dir / "inputs").iterdir()) == []


def test_the_run_level_plan_copies_each_existing_canonical_file_as_a_pre_image(stage, cli, tmp_path):
    """D4's failed outputs: the plan records the digest of each of the four files that exists, and copies it into ``preimage/``. A name with
    no file records null, and has no copy. The plan changes no output."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier(("threats.md", "threats.sarif"))
    needs(h.plan_cli(), 0, "the run-level plan's pre-images")
    expected = {name: (hashlib.sha256(TM_EARLIER[name]).hexdigest() if name in ("threats.md", "threats.sarif") else None) for name in TM_OUTPUTS}
    assert h.plan_json()["preimage"] == expected
    for name in ("threats.md", "threats.sarif"):
        assert (h.plan_dir / "preimage" / name).read_bytes() == TM_EARLIER[name]
    assert sorted(p.name for p in (h.plan_dir / "preimage").iterdir()) == ["threats.md", "threats.sarif"]
    h.assert_earlier_outputs_untouched(("threats.md", "threats.sarif"))
    assert not (h.out / "threat-report.md").exists() and not (h.out / "attack-chains.md").exists()


def test_the_run_level_plan_reads_no_threat_model_so_an_earlier_one_nobody_can_parse_is_no_obstacle(stage, cli, tmp_path):
    """The earlier ``threats.md`` is only copied: it has no Section 7, which would stop a plan that reads a reference set (S-12(c))."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    assert b"## 7." not in TM_EARLIER["threats.md"]
    needs(h.plan_cli(), 0, "the run-level plan over an earlier output with no Section 7")
    assert h.plan_json()["preimage"]["threats.md"] == hashlib.sha256(TM_EARLIER["threats.md"]).hexdigest()


def test_the_run_level_plan_snapshots_out_before_it_writes_a_file_of_its_own(stage, cli, tmp_path):
    """D4: the plan records each path under ``{out}`` with its size and ``mtime_ns``, so ``close`` can tell what is new or changed. The plan's own
    files are new by construction, so they are not in it."""
    h = RunDir(stage, cli, tmp_path)
    (h.out / "architecture.md").write_bytes(b"# Architecture\n")
    (h.out / "attack-trees").mkdir()
    (h.out / "attack-trees" / "s-1-attack-tree.md").write_bytes(b"an earlier tree\n")
    h.earlier(("threats.md",))
    needs(h.plan_cli(), 0, "the run-level plan's {out} snapshot")
    snapshot = h.plan_json()["out_snapshot"]
    assert isinstance(snapshot, dict), "a small tree is snapshotted (the check is skipped above 20,000 entries)"
    for relpath in ("architecture.md", "attack-trees/s-1-attack-tree.md", "threats.md"):
        status = (h.out / relpath).stat()
        assert snapshot[relpath] == [status.st_size, status.st_mtime_ns], relpath
    assert set(snapshot) == {"architecture.md", "attack-trees/s-1-attack-tree.md", "threats.md"}, "nothing the plan wrote is in its own snapshot"


def test_each_run_level_plan_is_fresh_and_nothing_under_the_build_directory_is_deleted(stage, cli, tmp_path):
    """D3: each invocation makes a fresh ``<plan_id>/`` and moves the pointer. An earlier plan's directory is left whole (KB 21)."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    first_id, first_tree = h.plan_id, tree_state(h.build / h.plan_id)
    needs(h.plan_cli(), 0, "a second run-level plan")
    assert h.plan_id != first_id
    assert tree_state(h.build / first_id) == first_tree
    assert h.read_json(h.build / "current.json")["plan_id"] == h.plan_id


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_the_run_level_plan_copies_the_permission_bits_of_each_canonical_file(stage, cli, tmp_path):
    """P1-2: a pre-image is what ``fail`` writes back, so it carries its output's own bits, and each of the four keeps its own."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    for name, mode in ODD_MODES.items():
        os.chmod(str(h.out / name), mode)
    needs(h.plan_cli(), 0, "the run-level plan's pre-images")
    assert {name: (h.plan_dir / "preimage" / name).stat().st_mode & 0o777 for name in ODD_MODES} == ODD_MODES
    assert {name: (h.out / name).stat().st_mode & 0o777 for name in ODD_MODES} == ODD_MODES, "the plan changes no output"


def test_the_run_level_plan_refuses_a_missing_out_a_bad_date_and_a_linked_build_directory(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    refused(h.cli("plan", "--stage", THREAT_MODEL, "--out", tmp_path / "nothing", "--date", DATE), "THREAT-MODEL", "a missing --out", code=1)
    refused(h.cli("plan", "--stage", THREAT_MODEL, "--out", h.out, "--date", "2026-13-45"), "THREAT-MODEL", "a bad --date")
    (h.out / ".tachi-build").mkdir()
    (h.out / ".tachi-build" / THREAT_MODEL).symlink_to(tmp_path)
    refused(h.plan_cli(), "THREAT-MODEL", "a symlinked stage directory")
    assert list(tmp_path.glob("*/plan.json")) == [] and not (tmp_path / "current.json").exists(), "nothing was written through the link"
    (h.out / ".tachi-build" / THREAT_MODEL).unlink()
    needs(h.plan_cli(), 0, "the run-level plan, once the link is gone")


# ---------------------------------------------------------------------------- close (Step 2.10; part-files.md sections 5 and 6; ADR-050 D4)


def test_close_writes_the_run_record_from_the_two_hand_off_files(stage, cli, tmp_path, tachi_version):
    """The run-level record takes its counts and Phase 2's six batch counts from ``provenance.json``, and lists the four canonical files that are
    present, with their digests. A run with no warning closes with 0."""
    h = closeable(stage, cli, tmp_path)
    needs(h.close(), 0, "close, the run-level stage record")
    rec = check_close_record(h.record(), h, tachi_version, "success")
    assert rec["counts"] == PROVENANCE_COUNTS and rec["batches"] == PHASE2_BATCHES
    assert rec["warnings"] == [] and rec["undeclared_paths"] == []
    # reading: an output's path is its canonical name relative to {out}, as the renderers write it
    assert {(o["path"], o["sha256"]) for o in rec["outputs"]} == {(name, hashlib.sha256(TM_NEW[name]).hexdigest()) for name in TM_OUTPUTS}


def test_close_lists_only_the_canonical_files_that_are_present(stage, cli, tmp_path, tachi_version):
    """A run with no report and no chain file (a skipped chain outcome) has two of the four."""
    h = closeable(stage, cli, tmp_path, earlier=False, wrote=("threats.md", "threats.sarif"))
    needs(h.close(), 0, "close, with two of the four files present")
    rec = check_close_record(h.record(), h, tachi_version, "success")
    assert sorted(o["path"] for o in rec["outputs"]) == ["threats.md", "threats.sarif"]


def test_close_prints_one_json_object_that_names_the_record_and_holds_its_two_lists(stage, cli, tmp_path):
    """S1P-A50 (R1): ``{record, warnings, undeclared_paths}``. ``record`` is the stage record's path, as ``fail``'s is, and the two lists are the record's own,
    so that on exit 5 the command prints them without reading the record."""
    h = closeable(stage, cli, tmp_path)
    (h.out / "gen.py").write_text("print('an improvised script')\n", encoding="utf-8")
    h.write_handoff("provenance", warnings=[WARN_REISSUED])
    printed = needs(h.close(), 5, "close, its printed object").json
    assert set(printed) == {"record", "warnings", "undeclared_paths"}
    assert Path(printed["record"]).resolve() == (h.plan_dir / "stage-record.json").resolve()
    assert printed["warnings"] == h.record()["warnings"] == [WARN_REISSUED] and printed["undeclared_paths"] == h.record()["undeclared_paths"] == ["gen.py"]


def test_close_writes_the_stage_record_and_nothing_else(stage, cli, tmp_path):
    """``close`` moves and restores nothing: the files the run wrote stay where they are, and the only new file is the record."""
    h = closeable(stage, cli, tmp_path)
    before = tree_state(h.out)
    needs(h.close(), 0, "close")
    after = tree_state(h.out)
    assert {key for key in after if before.get(key) != after[key]} == {".tachi-build/threat-model/%s/stage-record.json" % h.plan_id}
    assert set(before) <= set(after), "nothing was deleted or moved"
    assert all((h.out / name).read_bytes() == TM_NEW[name] for name in TM_OUTPUTS)


def test_close_folds_the_hand_off_warnings_in_the_contract_order_and_exits_5(stage, cli, tmp_path, tachi_version):
    """Section 6: the record's warnings are ``attack-chains.json``'s, then ``provenance.json``'s, each as written. Any warning makes the status
    ``success-with-warnings`` and the exit 5. The counts and batches still come from ``provenance.json``."""
    h = closeable(stage, cli, tmp_path)
    h.write_handoff("attack-chains", warnings=[WARN_CHAIN])
    h.write_handoff("provenance", warnings=[WARN_SECTION6, WARN_REISSUED, WARN_GAP, WARN_REPEATED])
    needs(h.close(), 5, "close, folding the hand-off warnings")
    rec = check_close_record(h.record(), h, tachi_version, "success-with-warnings")
    assert rec["warnings"] == [WARN_CHAIN, WARN_SECTION6, WARN_REISSUED, WARN_GAP, WARN_REPEATED]
    assert rec["counts"] == PROVENANCE_COUNTS and rec["batches"] == PHASE2_BATCHES


def test_close_without_the_chain_hand_off_warns_and_goes_on(stage, cli, tmp_path, tachi_version):
    """The chain check's own 2 prints and continues (R-24) and writes no file, so a missing ``attack-chains.json`` is a warning, never a stop."""
    h = closeable(stage, cli, tmp_path, chain=False)
    needs(h.close(), 5, "close, with no attack-chains.json")
    rec = check_close_record(h.record(), h, tachi_version, "success-with-warnings")
    assert [w["code"] for w in rec["warnings"]] == ["handoff-missing:attack-chains"] and isinstance(rec["warnings"][0]["detail"], str)
    assert rec["counts"] == PROVENANCE_COUNTS


def test_close_puts_its_own_warnings_last_in_the_contract_order(stage, cli, tmp_path, monkeypatch):
    """Section 6: the hand-off warnings first, then ``handoff-missing:attack-chains``, then the declared-paths warnings."""
    monkeypatch.setattr(stage.tp, "MAX_SNAPSHOT_ENTRIES", 1)
    h = RunDir(stage, cli, tmp_path)
    for name in ("a.txt", "b.txt"):
        (h.out / name).write_bytes(b"x")  # two files: over a cap of one, so the plan takes no snapshot
    res = needs(h.plan_cli(), 0, "the run-level plan over the snapshot cap")
    assert "snapshot is skipped" in res.err and h.plan_json()["out_snapshot"] is None
    h.run_wrote(("threats.md",))
    h.write_handoff("provenance", warnings=[WARN_REISSUED])
    needs(h.close(), 5, "close, with its own warnings")
    rec = h.record()
    assert [w["code"] for w in rec["warnings"]] == ["id:reissued", "handoff-missing:attack-chains", "declared-paths-skipped"]
    assert rec["undeclared_paths"] == []


def test_close_keeps_the_first_999_warnings_and_counts_the_rest(stage, cli, tmp_path):
    """Section 6, the record's cap: folded warnings past §5's 1,000 keep the first 999 in order, then ``warnings-truncated`` with the full count."""
    h = closeable(stage, cli, tmp_path)
    chain = [{"code": "chain-outcome:rewritten", "detail": "chain warning %d" % n} for n in range(600)]
    prov = [{"code": "id:reissued", "detail": "provenance warning %d" % n} for n in range(700)]
    h.write_handoff("attack-chains", warnings=chain)
    h.write_handoff("provenance", warnings=prov)
    needs(h.close(), 5, "close, over the record's warning cap")
    warnings = h.record()["warnings"]
    assert len(warnings) == 1000 and warnings[:999] == (chain + prov)[:999]
    assert warnings[999]["code"] == "warnings-truncated" and "1300" in warnings[999]["detail"]


# ---- the declared-paths check, over the whole run (D4's PR 2 grammar)


def declared_run_files():
    """One file of every kind that a threat-model run writes under ``{out}``, by D3's layout and D11 to D14's names (ADR-050 D4). The hand-off files
    and the run-level record belong to the plan under test, so the test writes those on their own."""
    plan = ".tachi-build/%s/" + FAKE_PLAN_ID + "/"
    return [
        "threats.md", "threats.sarif", "threat-report.md", "attack-chains.md", "architecture.md",
        "attack-chains.inconsistent.md",  # D13: the name that the chain check gives a file it rewrote the record against
        "attack-trees/.manifest.json", "attack-trees/s-1-attack-tree.md", "attack-trees/llm-12-attack-tree.md",
        ".tachi-build/phase1/inventory.json", ".tachi-build/phase1/dispatch.json", ".tachi-build/briefs/dsp-001.json",
        ".tachi-build/records/dsp-001.json", ".tachi-build/idmap.json", ".tachi-build/chains/chains.json", ".tachi-build/chains/narratives.json",
        ".tachi-build/sections.json",
        ".tachi-build/threats-md/current.json", plan % "threats-md" + "plan.json", plan % "threats-md" + "inputs/B001.json",
        plan % "threats-md" + "parts/B001.a1.json", plan % "threats-md" + "parts/B001-1.a2.json", plan % "threats-md" + "staged/threats.md",
        plan % "threats-md" + "stage-record.json",
        ".tachi-build/trees/current.json", plan % "trees" + "plan.json", plan % "trees" + "inputs/B001.json", plan % "trees" + "parts/B001.a1.json",
        plan % "trees" + "trees/s-1-attack-tree.md", plan % "trees" + "stage-record.json",
        ".tachi-build/report/current.json", plan % "report" + "plan.json", plan % "report" + "inputs/B002.json", plan % "report" + "parts/B002.a1.json",
        plan % "report" + "staged/threat-report.md", plan % "report" + "stage-record.json",
    ]


def test_close_declares_the_files_a_run_writes_and_lists_every_other_new_file(stage, cli, tmp_path, tachi_version):
    """D4: a path that is new or changed since the plan must match the grammar: the four canonical files, D3's exact layout, and in PR 2 also
    ``architecture.md``, ``attack-trees/*`` and D11 to D14's names. Anything else, such as a ``gen.py``, is ``undeclared_paths`` and exits 5."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    h.write_handoff("attack-chains")
    h.write_handoff("provenance")
    in_plan = ".tachi-build/threat-model/%s/" % h.plan_id
    declared = declared_run_files() + [in_plan + "preimage/" + name for name in TM_OUTPUTS] + [in_plan + "failed/" + name for name in TM_OUTPUTS]
    undeclared = ["gen.py", "scratch/x.txt", "notes.md", ".tachi-build/records/gen.py", ".tachi-build/chains/notes.md",
                  in_plan + "checks/gen.py", ".tachi-build/compensating-controls/x.json"]
    for relpath in declared + undeclared:
        (h.out / relpath).parent.mkdir(parents=True, exist_ok=True)
        (h.out / relpath).write_bytes(b"a file of this run\n")
    needs(h.close(), 5, "close, the declared-paths check over the whole run")
    rec = check_close_record(h.record(), h, tachi_version, "success-with-warnings")
    assert rec["undeclared_paths"] == sorted(undeclared)
    assert rec["warnings"] == [], "undeclared paths are listed, not warned of: the code is the exit 5 and the status (D4)"


def test_close_lists_a_file_that_changed_since_the_plan_and_not_one_that_was_already_there(stage, cli, tmp_path):
    """The snapshot is the baseline of "new or changed": an adopter's own file that the run never touched is not the run's to explain."""
    h = RunDir(stage, cli, tmp_path)
    (h.out / "adopter-notes.txt").write_text("the adopter's own file\n", encoding="utf-8")
    (h.out / "old-script.py").write_text("print(1)\n", encoding="utf-8")
    needs(h.plan_cli(), 0, "the run-level plan")
    (h.out / "old-script.py").write_text("print(1)\nprint(2)\n", encoding="utf-8")
    h.write_handoff("attack-chains")
    h.write_handoff("provenance")
    needs(h.close(), 5, "close, listing a changed file")
    assert h.record()["undeclared_paths"] == ["old-script.py"]


def test_close_caps_the_undeclared_paths_it_lists_and_says_how_many_there_were(stage, cli, tmp_path):
    """The same cap and warning as ``fail``'s record (ruled at W1)."""
    h = closeable(stage, cli, tmp_path)
    (h.out / "stray").mkdir()
    for number in range(stage.tp.MAX_UNDECLARED_PATHS + 3):
        (h.out / "stray" / ("f%04d.txt" % number)).write_bytes(b"x")
    needs(h.close(), 5, "close, over the undeclared-paths cap")
    rec = h.record()
    assert rec["undeclared_paths"] == ["stray/f%04d.txt" % n for n in range(1000)]
    assert [w for w in rec["warnings"] if w["code"] == "undeclared-paths-truncated"] == [
        {"code": "undeclared-paths-truncated", "detail": "1003 undeclared paths in all; the first 1000 are listed"}]


# ---- what close refuses (exit 2): a run whose check failed, or whose records can't be trusted, can't be closed


def loader_variants(valid):
    """Bytes for a hand-off file that the strict loader refuses: closed keys aside, at most 1 MiB, no NaN, Infinity or duplicate key (section 6)."""
    text = json.dumps(valid, indent=2)
    tail = text.rstrip()[:-1].rstrip()  # the object without its closing brace
    return {
        "not-json": b"{not json", "empty-file": b"", "top-level-array": b"[]",
        "duplicate-key": (tail + ',\n  "schema": "%s"\n}' % HANDOFF_SCHEMA).encode("utf-8"),
        "nan": (tail + ',\n  "x": NaN\n}').encode("utf-8"), "infinity": (tail + ',\n  "x": Infinity\n}').encode("utf-8"),
        "byte-order-mark": b"\xef\xbb\xbf" + text.encode("utf-8"), "not-utf8": b'{"schema": "\xff"}',
        "over-1-mib": (tail + ',\n  "x": "%s"\n}' % ("A" * (1024 * 1024))).encode("utf-8"),
        "nested-too-deep": (tail + ',\n  "x": ' + "[" * 9 + "]" * 9 + "\n}").encode("utf-8"),
    }


@pytest.mark.parametrize("check", ["provenance", "attack-chains"])
@pytest.mark.parametrize("variant", sorted(loader_variants(handoff("provenance", FAKE_PLAN_ID))))
def test_close_strict_loads_each_hand_off_file(stage, cli, tmp_path, check, variant):
    h = closeable(stage, cli, tmp_path)
    h.write_handoff(check, raw=loader_variants(handoff(check, h.plan_id))[variant])
    refused(h.close(), "THREAT-MODEL", "close over a %s.json that is %s" % (check, variant))
    assert_not_closed(h)


def test_close_does_not_read_a_hand_off_file_through_a_link(stage, cli, tmp_path):
    h = closeable(stage, cli, tmp_path)
    real = tmp_path / "elsewhere.json"
    real.write_text(json.dumps(handoff("provenance", h.plan_id)), encoding="utf-8")
    path = h.plan_dir / "checks" / "provenance.json"
    path.unlink()
    path.symlink_to(real)
    refused(h.close(), "THREAT-MODEL", "close over a linked provenance.json")
    assert_not_closed(h)


def test_close_refuses_a_run_with_no_provenance_hand_off(stage, cli, tmp_path):
    """``provenance.json`` is required: a run whose check never ran can't be closed. (A missing chain file is only a warning, above.)"""
    h = closeable(stage, cli, tmp_path)
    (h.plan_dir / "checks" / "provenance.json").unlink()
    refused(h.close(), "THREAT-MODEL", "close with no provenance.json")
    assert_not_closed(h)


def _set(key, value):
    def apply(body):
        body[key] = value
    return apply


def _drop(key):
    def apply(body):
        del body[key]
    return apply


def _count(key, value):
    def apply(body):
        body["counts"][key] = value
    return apply


def _drop_count(key):
    def apply(body):
        del body["counts"][key]
    return apply


def _warns(code, detail="a detail"):
    def apply(body):
        body["status"], body["warnings"] = "warn", [{"code": code, "detail": detail}]
    return apply


def _failed(body):
    body["status"], body["error"] = "fail", dict(PROVENANCE_ERROR)


# reading: the last two provenance cases below take section 6's status rule ("fail when error isn't null; otherwise warn when warnings isn't
# empty; otherwise pass") as part of a file's validity, since the status "matches the check's exit code".
BREAKS = [
    ("provenance", "unknown-key", _set("extra", 1)), ("provenance", "missing-key", _drop("batches")),
    ("provenance", "wrong-schema", _set("schema", "tachi.check-handoff/2")),
    ("provenance", "check-is-not-the-stem", _set("check", "attack-chains")),
    ("provenance", "another-plan", _set("plan_id", "20200101T000000Z-000000000000")),
    ("provenance", "plan-id-off-the-allow-list", _set("plan_id", "../escape")),
    ("provenance", "a-failed-check", _failed),
    ("provenance", "unknown-warning-code", _warns("made-up:code")),
    ("provenance", "unrecovered-reason-off-the-list", _warns("coverage-gap:unrecovered:other")),
    ("provenance", "warning-detail-over-500", _warns("id:reissued", "x" * 501)),
    ("provenance", "counts-missing-key", _drop_count("folded")), ("provenance", "counts-extra-key", _count("extra", 1)),
    ("provenance", "counts-negative", _count("open", -1)), ("provenance", "counts-boolean", _count("open", True)),
    ("provenance", "counts-over-1000000", _count("open", 1000001)), ("provenance", "counts-null", _set("counts", None)),
    ("provenance", "batches-null", _set("batches", None)),
    ("provenance", "status-disagrees-with-warnings", lambda body: body.update(warnings=[dict(WARN_REISSUED)])),
    ("provenance", "status-disagrees-with-error", _set("error", dict(PROVENANCE_ERROR))),
    ("attack-chains", "unknown-key", _set("extra", 1)), ("attack-chains", "check-is-not-the-stem", _set("check", "provenance")),
    ("attack-chains", "another-plan", _set("plan_id", "20200101T000000Z-000000000000")),
    ("attack-chains", "counts-not-null", _set("counts", {})), ("attack-chains", "batches-not-null", _set("batches", dict(PHASE2_BATCHES))),
    ("attack-chains", "error-not-null", _set("error", dict(PROVENANCE_ERROR))),
    ("attack-chains", "a-failed-check", _set("status", "fail")),
]


@pytest.mark.parametrize("check,name,mutate", BREAKS, ids=["%s-%s" % (check, name) for check, name, _ in BREAKS])
def test_close_refuses_a_hand_off_file_that_breaks_its_contract(stage, cli, tmp_path, check, name, mutate):
    """Section 6: closed keys, the closed warning codes, ``counts`` and ``batches`` as the check writes them, the plan's own ID, and a status that
    isn't ``fail``. ``attack-chains`` is never ``fail`` and has ``null`` for counts, batches and error."""
    h = closeable(stage, cli, tmp_path)
    h.write_handoff(check, mutate=mutate)
    refused(h.close(), "THREAT-MODEL", "close over a %s.json with %s" % (check, name))
    assert_not_closed(h)


@pytest.mark.parametrize("fault", ["wrong-digest", "edited-plan", "newer-plan", "missing-plan", "plan-id-off-the-allow-list"])
def test_close_refuses_a_plan_it_cannot_trust(stage, cli, tmp_path, fault):
    """D3: ``fail`` and ``close`` refuse a plan file with another digest, a ``--plan`` that the pointer doesn't name, and an ID off the allow-list.
    Its table has no exit 1, so even a plan that isn't there is a 2."""
    h = closeable(stage, cli, tmp_path)
    plan_id, digest = h.plan_id, h.digest
    if fault == "wrong-digest":
        res = h.close(digest="0" * 64)
    elif fault == "edited-plan":
        path = h.plan_dir / "plan.json"
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        res = h.close()
    elif fault == "newer-plan":
        needs(h.plan_cli(), 0, "a newer run-level plan")
        res = h.close(plan_id=plan_id, digest=digest)
    elif fault == "missing-plan":
        (h.plan_dir / "plan.json").unlink()
        res = h.close()
    else:
        res = h.close(plan_id="../escape")
    refused(res, "THREAT-MODEL", "close over a plan with %s" % fault)
    if fault != "plan-id-off-the-allow-list":
        assert_not_closed(h, plan_id)


def test_close_takes_only_the_threat_model_stage(stage, cli, tmp_path):
    h = closeable(stage, cli, tmp_path)
    needs(h.close(), 0, "close")
    for other in ("risk-score", "compensating-controls", "threats-md", "trees", "report"):
        res = h.cli("close", "--stage", other, "--out", h.out, *h.plan_args())
        assert res.code == 2, (other, res.describe())


# ---------------------------------------------------------------------------- id-mark (Step 2.7; ADR-050 D7, the PM's ruling B; FR-E.19)
#
# ``id-mark`` upserts the ID high-water mark line into this run's ``threats.md``: per prefix, the larger of this run's highest ID and the baseline's
# mark, or, where the baseline has no mark, the highest ID among its live findings and its Section 4c. The line is one body line under P-2's anchors,
# written by shipped code and never by the model, in S-2 prefix order, and zero matches or several read as absent.

MARK_TEXT = "**ID high-water mark**: `%s`"
MARK_LINE = re.compile(r"^\*\*ID high-water mark\*\*: `([^`]*)`$")
FENCED_MARK = "```text\n**ID high-water mark**: `S-999`\n```"
SECTION_7_ONE_ROW = (
    "## 7. Recommended Actions\n\n| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |\n"
    "|---|---|---|---|---|---|---|---|---|\n| T-1 | NEW | Tampering | " + _DASH + " | Gateway | L4 " + _DASH + " Deployment | A threat | High | A fix |\n")


def mark_lines(text):
    """(index, the marks it names, inside a fence) for each line that looks like the mark line."""
    found, in_fence = [], False
    for index, line in enumerate(text.split("\n")):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        match = MARK_LINE.match(line)
        if match:
            found.append((index, match.group(1), in_fence))
    return found


def real_marks(text):
    """The marks of the lines outside code fences, the only ones that count."""
    return [value for _, value, fenced in mark_lines(text) if not fenced]


@pytest.fixture
def marked(tmp_path, monkeypatch):
    """A working directory with a ``run/`` directory for this run's ``threats.md`` and the baseline's."""
    (tmp_path / "run").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write_run(root, name, open_ids, resolved=(), mark=None, preamble=""):
    """``run/<name>``: a synthetic threats.md, with the mark line (when ``mark`` is given) and any other ``preamble`` before its first heading."""
    lead = "\n\n".join(part for part in (MARK_TEXT % mark if mark else "", preamble) if part)
    path = root / "run" / name
    path.write_text(make_threats_md(open_ids, resolved, preamble=lead), encoding="utf-8")
    return path


def id_mark(cli, baseline="run/baseline.md", threats="run/threats.md"):
    return cli("id-mark", "--threats", threats, *(["--baseline", baseline] if baseline else ["--no-baseline"]))


# (case, this run's open IDs, the baseline, the mark that ruling B gives). A baseline is {"open", "resolved", "mark"}.
MARK_CASES = [
    ("no-baseline-takes-the-numeric-maximum-in-canonical-form", ["T-9", "T-10", "S-2", "AGP-01", "LLM-3", "LLM-12"], None, "S-2, T-10, AGP-1, LLM-12"),
    ("every-prefix-is-in-s2-order", ["%s-1" % prefix for prefix in reversed(PREFIX_ORDER)], None, ", ".join("%s-1" % prefix for prefix in PREFIX_ORDER)),
    ("a-mark-above-every-live-id-wins", ["S-3", "T-5"], {"open": ["S-3", "T-5"], "resolved": [], "mark": "S-14, T-22"}, "S-14, T-22"),
    ("this-run-above-the-mark-wins", ["S-9"], {"open": ["S-1"], "resolved": [], "mark": "S-4"}, "S-9"),
    ("each-prefix-takes-its-own-larger-value", ["S-3", "T-8", "LLM-1"], {"open": ["S-3", "T-2"], "resolved": [], "mark": "S-14, T-2"}, "S-14, T-8, LLM-1"),
    ("a-prefix-that-only-the-mark-names-stays", ["S-3"], {"open": ["S-3", "E-3"], "resolved": [], "mark": "S-14, E-3"}, "S-14, E-3"),
    ("no-mark-seeds-from-the-live-ids-and-section-4c", ["S-3", "T-5"], {"open": ["S-3", "T-5"], "resolved": ["S-9", "LLM-7"], "mark": None}, "S-9, T-5, LLM-7"),
    ("a-new-id-above-the-seed-wins", ["S-3", "S-10"], {"open": ["S-3"], "resolved": ["S-9"], "mark": None}, "S-10"),
    ("section-4c-alone-sets-the-seed", ["T-1"], {"open": ["T-1"], "resolved": ["T-4"], "mark": None}, "T-4"),
    ("a-live-baseline-id-that-this-run-dropped-sets-the-seed", ["S-2"], {"open": ["S-2", "S-7"], "resolved": [], "mark": None}, "S-7"),
]


@pytest.mark.parametrize("case", MARK_CASES, ids=[case[0] for case in MARK_CASES])
def test_id_mark_writes_per_prefix_the_larger_of_this_runs_highest_id_and_the_baselines_mark(stage, cli, marked, case):
    """Ruling B (ADR-050 D7). A first PR 2 run, on a baseline with no mark, seeds it from the baseline's live IDs and Section 4c (PM-T7), so an ID that
    was resolved before this run is never numbered again."""
    _, open_ids, baseline, expected = case
    threats = write_run(marked, "threats.md", open_ids)
    if baseline is not None:
        write_run(marked, "baseline.md", baseline["open"], baseline["resolved"], mark=baseline["mark"])
    baseline_bytes = (marked / "run" / "baseline.md").read_bytes() if baseline is not None else None
    needs(id_mark(cli, "run/baseline.md" if baseline is not None else None), 0, "id-mark, ruling B's high-water mark line")
    assert real_marks(threats.read_text(encoding="utf-8")) == [expected]
    if baseline is not None:
        assert (marked / "run" / "baseline.md").read_bytes() == baseline_bytes, "the baseline is only read"


@pytest.mark.parametrize("preamble", [FENCED_MARK, MARK_TEXT % "S-90" + "\n\n" + MARK_TEXT % "S-91"], ids=["a-mark-inside-a-fence", "two-mark-lines"])
def test_a_baseline_mark_that_sits_in_a_fence_or_repeats_reads_as_absent_so_the_seed_applies(stage, cli, marked, preamble):
    """D7: the line sits between the frontmatter and the first heading, outside code fences, and zero matches or several read as absent. A forged or
    quoted mark in a baseline must not set this run's."""
    threats = write_run(marked, "threats.md", ["S-3"])
    write_run(marked, "baseline.md", ["S-3"], ["S-5"], preamble=preamble)
    needs(id_mark(cli), 0, "id-mark over a baseline whose mark line doesn't count")
    assert real_marks(threats.read_text(encoding="utf-8")) == ["S-5"], "seeded from the baseline's Section 4c, not from the quoted mark"


def test_id_mark_never_reads_the_mark_this_runs_own_file_already_holds(stage, cli, marked):
    """The reissue check reads the baseline's line, never this run's, and shipped code writes the line: a stale or forged one in this file is replaced,
    and a second run changes no byte."""
    threats = write_run(marked, "threats.md", ["S-3", "T-5"], mark="S-999")
    needs(id_mark(cli, None), 0, "id-mark over a file with a stale mark")
    text = threats.read_text(encoding="utf-8")
    assert real_marks(text) == ["S-3, T-5"] and "S-999" not in text
    needs(id_mark(cli, None), 0, "id-mark, again")
    assert threats.read_text(encoding="utf-8") == text, "a second run changes no byte"


def test_id_mark_collapses_several_lines_to_one_and_leaves_a_fenced_copy_alone(stage, cli, marked):
    threats = write_run(marked, "threats.md", ["S-3", "T-5"], mark="S-98", preamble=MARK_TEXT % "S-99" + "\n\n" + FENCED_MARK)
    assert len(real_marks(threats.read_text(encoding="utf-8"))) == 2
    needs(id_mark(cli, None), 0, "id-mark over a file with two mark lines")
    text = threats.read_text(encoding="utf-8")
    assert real_marks(text) == ["S-3, T-5"]
    assert [value for _, value, fenced in mark_lines(text) if fenced] == ["S-999"], "the quoted copy in the fence is not the line, and is left alone"


def test_id_mark_changes_nothing_in_the_file_but_the_mark_line(stage, cli, marked):
    threats = write_run(marked, "threats.md", ["S-3", "T-5"], resolved=["T-2"], preamble=FENCED_PREAMBLE)
    before = threats.read_text(encoding="utf-8")
    needs(id_mark(cli, None), 0, "id-mark")
    after = threats.read_text(encoding="utf-8")
    assert [line for line in without_blank_lines(after) if not MARK_LINE.match(line)] == without_blank_lines(before)
    index = [i for i, _, fenced in mark_lines(after) if not fenced][0]
    assert frontmatter_end(after) < index < first_heading_outside_fences(after)


@pytest.mark.parametrize("lead", ["---\nk: v\n---\n", "# Title\n\n", "~~~\n## fake\n~~~\n", "# T\n\n    ## code, not a heading\n\n"],
                         ids=["frontmatter-then-heading", "no-frontmatter", "tilde-fence", "indented-code"])
def test_id_mark_places_the_line_before_the_first_heading_outside_fences(stage, cli, marked, lead):
    """The same placement as the architecture-source line (P-2's anchors), for files of every shape that Section 7 can follow."""
    threats = marked / "run" / "threats.md"
    threats.write_text(lead + SECTION_7_ONE_ROW, encoding="utf-8")
    needs(id_mark(cli, None), 0, "id-mark")
    expected = lead + MARK_TEXT % "T-1" + "\n\n" + SECTION_7_ONE_ROW
    assert threats.read_text(encoding="utf-8") == expected
    assert id_mark(cli, None).code == 0 and threats.read_text(encoding="utf-8") == expected, "a second run changes no byte"


@pytest.mark.parametrize("order", ["mark-first", "source-first"])
def test_id_mark_and_architecture_source_each_leave_the_others_line_alone(stage, cli, repo, order):
    """Step 2.7 runs both. Each is an upsert of its own body line, so neither may remove, alter or duplicate the other's."""
    threats = repo / "run" / "threats.md"
    steps = [lambda: id_mark(cli, None), lambda: arch_source(cli)]
    for step in (steps if order == "mark-first" else steps[::-1]):
        needs(step(), 0, "Step 2.7's two upserts")
    text = threats.read_text(encoding="utf-8")
    assert real_marks(text) == ["S-2, T-10, AGP-1"] and [value for _, value in real_lines(text)] == ["docs/security/architecture.md"]
    for index in [i for i, _, fenced in mark_lines(text) if not fenced] + [i for i, _ in real_lines(text)]:
        assert frontmatter_end(text) < index < first_heading_outside_fences(text)
    kept = sorted(without_blank_lines(text))
    for step in steps:  # a second upsert may place its own line again, but it never drops, repeats or alters the other's
        assert step().code == 0
        again = threats.read_text(encoding="utf-8")
        assert sorted(without_blank_lines(again)) == kept and len(real_marks(again)) == 1 and len(real_lines(again)) == 1


def test_id_mark_exits_1_for_a_missing_threats_file_or_baseline_and_2_for_what_it_cannot_edit_or_read(stage, cli, marked):
    threats = write_run(marked, "threats.md", ["S-3"])
    write_run(marked, "baseline.md", ["S-3"])
    needs(id_mark(cli), 0, "id-mark")
    refused(id_mark(cli, threats="run/absent.md"), "THREAT-MODEL", "id-mark with no threats file", code=1)
    refused(id_mark(cli, baseline="run/absent.md"), "THREAT-MODEL", "id-mark with no baseline file", code=1)
    (marked / "run" / "link.md").symlink_to(threats)
    refused(id_mark(cli, threats="run/link.md"), "THREAT-MODEL", "id-mark over a linked threats file")
    assert (marked / "run" / "link.md").is_symlink()
    refused(id_mark(cli, threats="run"), "THREAT-MODEL", "id-mark over a directory")
    (marked / "run" / "binary.md").write_bytes(b"# \xff\xfe not utf-8\n")
    refused(id_mark(cli, threats="run/binary.md"), "THREAT-MODEL", "id-mark over a threats file that is not UTF-8")
    refused(id_mark(cli, baseline="run/binary.md"), "THREAT-MODEL", "id-mark over a baseline that is not UTF-8")


def test_id_mark_stops_when_this_runs_section_7_cannot_be_read_and_leaves_the_file_as_it_was(stage, cli, marked):
    """reading: the mark is the larger of two values, and one that can't be read would lower it silently, the direction that lets an ID come back.
    A Section 7 that the reference-set wrapper refuses (S-12(c), KB 22) is exit 2, with no write."""
    threats = write_run(marked, "threats.md", ["S-3"])
    needs(id_mark(cli, None), 0, "id-mark")
    threats.write_text(make_threats_md(["S-3"], section7="missing"), encoding="utf-8")
    before = threats.read_bytes()
    refused(id_mark(cli, None), "THREAT-MODEL", "id-mark over a file with no Section 7")
    assert threats.read_bytes() == before


def test_id_mark_needs_exactly_one_of_baseline_and_no_baseline(stage, cli, marked):
    write_run(marked, "threats.md", ["S-3"])
    write_run(marked, "baseline.md", ["S-3"])
    needs(id_mark(cli), 0, "id-mark")
    assert cli("id-mark", "--threats", "run/threats.md").code == 2
    assert cli("id-mark", "--threats", "run/threats.md", "--baseline", "run/baseline.md", "--no-baseline").code == 2
    assert cli("id-mark", "--baseline", "run/baseline.md").code == 2


def test_id_mark_prints_one_json_object(stage, cli, marked):
    write_run(marked, "threats.md", ["S-3"])
    assert isinstance(needs(id_mark(cli, None), 0, "id-mark, its printed object").json, dict)


# ---------------------------------------------------------------------------- fail --stage threat-model: the four-file set and the hand-off fold
#
# D4's failed outputs for the run: the four files ``threats.md``, ``threats.sarif``, ``threat-report.md`` and ``attack-chains.md`` move to
# ``<plan_id>/failed/`` when their bytes changed since the plan, and the pre-image goes back when its digest matches (KB 21's double gate, the
# four moments, and AR-T6). ``fail`` also folds whichever hand-off files exist and load, in ``close``'s order (part-files.md section 6).


def test_fail_moves_each_changed_file_of_the_four_and_puts_the_earlier_run_back(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    res = needs(h.fail("render-failed"), 0, "fail --stage threat-model, the four-file set")
    printed = res.json
    assert set(printed) == {"moved", "restored", "record"}
    assert sorted(printed["moved"]) == sorted(printed["restored"]) == sorted(TM_OUTPUTS)
    assert Path(printed["record"]).resolve() == (h.plan_dir / "stage-record.json").resolve()
    h.assert_earlier_outputs_untouched()
    assert {name: (h.plan_dir / "failed" / name).read_bytes() for name in TM_OUTPUTS} == TM_NEW, "the failed run is kept for diagnosis"


@pytest.mark.parametrize("reason", FAIL_REASONS)
def test_fail_writes_the_failed_run_record_and_with_no_hand_off_its_counts_are_empty_and_its_batches_zero(stage, cli, tmp_path, tachi_version, reason):
    """Section 5: with no hand-off, ``fail`` writes the run's ``counts`` as ``{}`` and its ``batches`` as zeros, and warns of no missing file, because
    a run can fail before Step 2.8."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    needs(h.fail(reason, detail="a synthetic failure for the test"), 0, "fail --stage threat-model")
    rec = h.record()
    check_record(rec, THREAT_MODEL, h.plan_id, tachi_version)
    assert rec["error"]["code"] == reason and "a synthetic failure for the test" in rec["error"]["message"]
    assert rec["counts"] == {} and rec["batches"] == {key: 0 for key in RECORD_BATCH_KEYS}
    assert rec["warnings"] == [] and rec["undeclared_paths"] == []


@pytest.mark.parametrize("reason,fragment", [
    ("agent-not-spawned", "scripts/install.sh"), ("unrecoverable-batch", "report the kept plan directory"),
    ("check-failed", "re-run"), ("render-failed", "re-run")])
def test_fail_prints_d4s_message_for_the_run_with_its_remedy_and_the_kept_directory(stage, cli, tmp_path, reason, fragment):
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    res = needs(h.fail(reason, detail="tachi-spoofing"), 0, "fail --stage threat-model")
    assert re.search(r"^TACHI THREAT-MODEL FAILED: ", res.err, re.M) and "Remedy: " in res.err
    assert fragment in res.err and "Kept for diagnosis: %s" % h.plan_dir in res.err
    if reason == "agent-not-spawned":
        assert "Agent: tachi-spoofing" in res.err


def test_fail_folds_the_hand_off_files_it_finds_in_the_order_close_does(stage, cli, tmp_path, tachi_version):
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    h.write_handoff("attack-chains", warnings=[WARN_CHAIN])
    h.write_handoff("provenance", warnings=[WARN_SECTION6, WARN_REISSUED])
    needs(h.fail("render-failed"), 0, "fail --stage threat-model, folding the hand-off files")
    rec = h.record()
    check_record(rec, THREAT_MODEL, h.plan_id, tachi_version)
    assert rec["counts"] == PROVENANCE_COUNTS and rec["batches"] == PHASE2_BATCHES
    assert rec["warnings"] == [WARN_CHAIN, WARN_SECTION6, WARN_REISSUED] and rec["error"]["code"] == "render-failed"


def test_fail_folds_the_chain_hand_off_alone_when_the_run_failed_before_the_provenance_check(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    h.write_handoff("attack-chains", warnings=[WARN_CHAIN])
    needs(h.fail("check-failed"), 0, "fail --stage threat-model, with one hand-off file")
    rec = h.record()
    assert rec["warnings"] == [WARN_CHAIN] and rec["counts"] == {} and rec["batches"] == {key: 0 for key in RECORD_BATCH_KEYS}


def test_fail_takes_the_error_text_from_a_failed_provenance_check_and_puts_the_earlier_run_back(stage, cli, tmp_path, tachi_version):
    """D-3's second path, driven through ``fail`` to the pre-image restore (AR-T6): the check exits 4 with the run's four files already written. When
    ``provenance.json`` says ``fail``, the record's message, finding IDs and remedy come from its ``error``, and its code is ``--reason``."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    h.write_handoff("attack-chains")
    h.write_handoff("provenance", error=PROVENANCE_ERROR)
    res = needs(h.fail("check-failed"), 0, "fail --stage threat-model, over a failed provenance check")
    assert sorted(res.json["moved"]) == sorted(res.json["restored"]) == sorted(TM_OUTPUTS)
    h.assert_earlier_outputs_untouched()
    rec = h.record()
    check_record(rec, THREAT_MODEL, h.plan_id, tachi_version)
    assert rec["error"] == {"code": "check-failed", "message": PROVENANCE_ERROR["message"], "batch_id": None,
                            "finding_ids": PROVENANCE_ERROR["finding_ids"], "remedy": PROVENANCE_ERROR["remedy"]}
    assert rec["counts"] == PROVENANCE_COUNTS and rec["batches"] == PHASE2_BATCHES


@pytest.mark.parametrize("fault", ["not-json", "another-plan"])
def test_fail_leaves_out_a_hand_off_file_that_does_not_load_and_still_ends_the_run(stage, cli, tmp_path, fault):
    """Section 6: ``fail`` folds whichever hand-off files exist and load. A file that doesn't, or that another plan wrote, must not put its numbers
    in this run's record, and must not stop the run from failing."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    if fault == "not-json":
        h.write_handoff("provenance", raw=b"{not json")
    else:
        h.write_handoff("provenance", mutate=_set("plan_id", "20200101T000000Z-000000000000"))  # reading: a file of another plan doesn't load
    res = needs(h.fail("check-failed"), 0, "fail --stage threat-model, over a hand-off file that does not load")
    assert sorted(res.json["restored"]) == sorted(TM_OUTPUTS)
    rec = h.record()
    assert rec["counts"] == {} and rec["batches"] == {key: 0 for key in RECORD_BATCH_KEYS}
    # S1P-A53 (R4): in that file's place the record says why its counts are missing, with the loader's reason and never the file's text
    assert [w["code"] for w in rec["warnings"]] == ["handoff-invalid:provenance"] and rec["warnings"][0]["detail"]
    assert "{not json" not in rec["warnings"][0]["detail"]


# ---- KB 21's four moments, for the four files


def test_fail_leaves_earlier_outputs_alone_on_a_re_run_of_the_run(stage, cli, tmp_path):
    """Moment 1: an earlier run's outputs stay where they are when this run fails before it writes anything, and the earlier plan's directory is left whole."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    earlier_id, earlier_tree = h.plan_id, tree_state(h.plan_dir)
    needs(h.plan_cli(), 0, "the re-run's plan")
    res = needs(h.fail("check-failed"), 0, "fail --stage threat-model")
    assert res.json["moved"] == [] and res.json["restored"] == []
    h.assert_earlier_outputs_untouched()
    assert tree_state(h.build / earlier_id) == earlier_tree
    assert not (h.plan_dir / "failed").exists() or list((h.plan_dir / "failed").iterdir()) == []


def test_fail_leaves_earlier_outputs_alone_on_a_resume_and_refuses_another_digest(stage, cli, tmp_path):
    """Moment 2: the model keeps no state, so a later process fails the plan using only the plan ID and the digest ``plan`` printed. Any other digest
    is refused with exit 2, the record is still written, and nothing moves."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    refused_res = h.fail("check-failed", digest="0" * 64)
    assert refused_res.code == 2 and (h.plan_dir / "stage-record.json").is_file(), refused_res.describe()
    assert [w["code"] for w in h.record()["warnings"]] == ["plan-digest-mismatch"]
    assert all((h.out / name).read_bytes() == TM_NEW[name] for name in TM_OUTPUTS), "a plan that can't be trusted moves and restores nothing"
    assert not (h.plan_dir / "failed").exists() or list((h.plan_dir / "failed").iterdir()) == []
    res = needs(h.fail("check-failed"), 0, "fail --stage threat-model, with the digest plan printed")
    assert sorted(res.json["restored"]) == sorted(TM_OUTPUTS)
    h.assert_earlier_outputs_untouched()


def test_fail_leaves_earlier_outputs_alone_after_a_failed_run_of_the_run(stage, cli, tmp_path):
    """Moment 3: a run that failed keeps its quarantined files. A later run that fails touches neither them nor the restored canonical files, and
    ``{out}`` never holds a failed file under a name that an auto-detect site would take."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    first = needs(h.fail("render-failed"), 0, "fail --stage threat-model")
    assert sorted(first.json["moved"]) == sorted(first.json["restored"]) == sorted(TM_OUTPUTS)
    first_id, first_failed = h.plan_id, tree_state(h.build / h.plan_id / "failed")
    assert first_failed == {name: hashlib.sha256(TM_NEW[name]).hexdigest() for name in TM_OUTPUTS}
    h.assert_earlier_outputs_untouched()

    needs(h.plan_cli(), 0, "a later run's plan, on the restored outputs")
    second = needs(h.fail("check-failed"), 0, "fail --stage threat-model, a second time")
    assert second.json["moved"] == [] and second.json["restored"] == []
    assert tree_state(h.build / first_id / "failed") == first_failed
    h.assert_earlier_outputs_untouched()
    assert sorted(path.name for path in h.out.iterdir()) == sorted([".tachi-build"] + list(TM_OUTPUTS))


def test_fail_with_output_dir_touches_only_that_directory_for_the_run(stage, cli, tmp_path):
    """Moment 4: a run whose ``--out`` isn't the default moves and restores inside it only. The other directory's outputs and ``.tachi-build`` stay."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    default_state = tree_state(h.out)
    custom = tmp_path / "custom"
    custom.mkdir()
    (custom / "threats.md").write_bytes(b"# the custom directory's earlier threats.md\n")
    default, h.out = h.out, custom
    needs(h.plan_cli(), 0, "the run-level plan, in --output-dir")
    (custom / "threats.md").write_bytes(NEW_MD)
    res = needs(h.fail("render-failed"), 0, "fail --stage threat-model, in --output-dir")
    assert res.json["moved"] == ["threats.md"] and res.json["restored"] == ["threats.md"]
    assert (custom / "threats.md").read_bytes() == b"# the custom directory's earlier threats.md\n"
    assert tree_state(default) == default_state, "the default directory is as it was, with no .tachi-build"


def test_a_failing_staged_check_changes_nothing_for_the_run(stage, cli, tmp_path):
    """D4: a check that fails on the staged files, the joiner's or the assembler's, leaves the canonical files untouched, and ``fail`` finds nothing
    changed. The staged files stay for diagnosis, as nothing under ``.tachi-build`` is deleted."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    staged = [".tachi-build/threats-md/%s/staged/threats.md" % FAKE_PLAN_ID, ".tachi-build/report/%s/staged/threat-report.md" % FAKE_PLAN_ID]
    for relpath in staged:
        (h.out / relpath).parent.mkdir(parents=True)
        (h.out / relpath).write_bytes(NEW_MD)
    res = needs(h.fail("check-failed"), 0, "fail --stage threat-model")
    assert res.json["moved"] == [] and res.json["restored"] == []
    h.assert_earlier_outputs_untouched()
    assert all((h.out / relpath).read_bytes() == NEW_MD for relpath in staged)


HALF_APPLIED = {
    "the-markdown-alone": ("threats.md",), "the-sarif-and-the-report": ("threats.sarif", "threat-report.md"),
    "the-chain-file-alone": ("attack-chains.md",), "three-of-the-four": ("threats.md", "threats.sarif", "attack-chains.md"),
}


@pytest.mark.parametrize("changed", sorted(HALF_APPLIED))
def test_a_half_applied_set_is_restored_file_by_file(stage, cli, tmp_path, changed):
    """D4: a run that replaced some of the four and then failed is undone. Each changed file moves to ``failed/``, its pre-image takes its place,
    and a file that never changed is not touched."""
    names = HALF_APPLIED[changed]
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote(names)
    res = needs(h.fail("render-failed"), 0, "fail --stage threat-model")
    assert sorted(res.json["moved"]) == sorted(res.json["restored"]) == sorted(names)
    for name in TM_OUTPUTS:
        assert (h.plan_dir / "failed" / name).exists() == (name in names)
    h.assert_earlier_outputs_untouched()


def test_new_outputs_with_no_earlier_run_are_moved_and_nothing_is_restored_for_the_run(stage, cli, tmp_path):
    """A first run's files stay for diagnosis but leave the canonical names, so no later command takes them as input or as a baseline."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    res = needs(h.fail("render-failed"), 0, "fail --stage threat-model")
    assert sorted(res.json["moved"]) == sorted(TM_OUTPUTS) and res.json["restored"] == []
    assert not any((h.out / name).exists() for name in TM_OUTPUTS)
    assert {name: (h.plan_dir / "failed" / name).read_bytes() for name in TM_OUTPUTS} == TM_NEW


def test_fail_puts_an_earlier_chain_file_back_when_this_run_moved_its_own_away(stage, cli, tmp_path):
    """reading: D13's check renames a chain file that it rewrote the outcome record against to ``attack-chains.inconsistent.md``, so the canonical
    name is empty when a later step fails the run. This run had overwritten the earlier run's file before that, so the pre-image goes back (KB 21: wire
    every moment that the state can exist). The quarantined copy is this run's own file and stays where the check put it."""
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    os.replace(str(h.out / "attack-chains.md"), str(h.out / "attack-chains.inconsistent.md"))
    res = needs(h.fail("check-failed"), 0, "fail --stage threat-model, with the chain file quarantined")
    assert (h.out / "attack-chains.md").read_bytes() == TM_EARLIER["attack-chains.md"]
    assert (h.out / "attack-chains.inconsistent.md").read_bytes() == TM_NEW["attack-chains.md"]
    assert sorted(res.json["restored"]) == sorted(TM_OUTPUTS) and sorted(res.json["moved"]) == sorted(set(TM_OUTPUTS) - {"attack-chains.md"})


def test_fail_moves_only_the_four_names_of_the_run(stage, cli, tmp_path):
    """KB 21's double gate, the name half: only the four names move, whatever else the run changed or wrote."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    others = {"attack-chains.inconsistent.md": b"a quarantined chain file\n", "risk-scores.md": b"another stage's output\n", "notes.md": b"a stray file\n",
              "gen.py": b"print('an improvised script')\n", "architecture.md": b"# Architecture\n", "attack-trees/s-1-attack-tree.md": b"a tree\n"}
    for relpath, data in others.items():
        (h.out / relpath).parent.mkdir(parents=True, exist_ok=True)
        (h.out / relpath).write_bytes(data)
    res = needs(h.fail("render-failed"), 0, "fail --stage threat-model")
    assert sorted(res.json["moved"]) == sorted(TM_OUTPUTS)
    assert {relpath: (h.out / relpath).read_bytes() for relpath in others} == others


@pytest.mark.parametrize("name", TM_OUTPUTS)
@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_fail_refuses_a_symlink_or_a_directory_at_any_of_the_four_names(stage, cli, tmp_path, name, kind):
    """KB 21's double gate, the file half: only a regular file directly in ``{out}`` moves. A refusal is exit 2, the record is still written, and the
    link's target is untouched."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    victim = tmp_path / "victim.txt"
    victim.write_bytes(b"outside the run directory\n")
    target = h.out / name
    if kind == "symlink":
        target.symlink_to(victim)
    else:
        target.mkdir()
        (target / "inner.txt").write_bytes(b"inside a directory\n")
    res = h.fail("render-failed")
    assert res.code == 2 and (h.plan_dir / "stage-record.json").is_file(), res.describe()
    assert victim.read_bytes() == b"outside the run directory\n"
    assert target.is_symlink() if kind == "symlink" else (target / "inner.txt").is_file()
    assert not (h.plan_dir / "failed" / name).exists()


def test_fail_never_overwrites_a_failed_copy_and_restores_only_a_pre_image_that_still_matches_for_the_run(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    (h.plan_dir / "failed").mkdir(exist_ok=True)
    (h.plan_dir / "failed" / "threats.md").write_bytes(b"the first failure's copy\n")
    (h.plan_dir / "preimage" / "threats.sarif").write_bytes(b"# a tampered copy\n")
    h.run_wrote(("threats.md", "threats.sarif"))
    res = h.fail("render-failed")
    assert res.code == 2 and (h.plan_dir / "stage-record.json").is_file(), res.describe()
    assert (h.plan_dir / "failed" / "threats.md").read_bytes() == b"the first failure's copy\n"
    assert (h.out / "threats.md").read_bytes() == TM_NEW["threats.md"], "a refused move leaves the file where it was"
    assert res.json["moved"] == ["threats.sarif"] and res.json["restored"] == []
    assert not (h.out / "threats.sarif").exists(), "a copy whose digest no longer matches never goes back"
    assert {w["code"] for w in h.record()["warnings"]} == {"move-refused"}


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_fail_puts_each_pre_image_back_with_the_permission_bits_of_the_file_it_replaces(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    for name, mode in ODD_MODES.items():
        os.chmod(str(h.out / name), mode)
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote()
    needs(h.fail("render-failed"), 0, "fail --stage threat-model")
    assert {name: (h.out / name).stat().st_mode & 0o777 for name in ODD_MODES} == ODD_MODES


def test_fail_does_not_act_on_a_run_level_plan_the_pointer_no_longer_names(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    older_id, older_digest = h.plan_id, h.digest
    h.run_wrote()
    needs(h.plan_cli(), 0, "a newer run-level plan")
    res = h.fail("render-failed", plan_id=older_id, digest=older_digest)
    assert res.code == 2 and res.json["moved"] == [] and res.json["restored"] == [], res.describe()
    assert all((h.out / name).read_bytes() == TM_NEW[name] for name in TM_OUTPUTS)
    assert [w["code"] for w in h.read_json(h.build / older_id / "stage-record.json")["warnings"]] == ["pointer-mismatch"]


# ---------------------------------------------------------------------------- the threats-md batch stage (item O-beta; part-files.md, "Stage payload: threats-md")
#
# The orchestrator writes ``{out}/.tachi-build/sections.json`` once after Phase 4. ``plan --stage threats-md`` strict-loads it from that fixed path and
# splits the template's 24 tables into parts: a table keyed by row has the manifest's row count, and a table keyed by finding has the open IDs of its
# prefixes (Section 7: every open ID; Section 4c: the resolved ones). The orchestrator writes each part itself, and ``reconcile`` validates them.

_STRIDE_KEYS = ("finding_id", "status", "component", "maestro_layer", "threat", "likelihood", "impact", "risk_level", "mitigation")
_AI_KEYS = ("finding_id", "status", "component", "maestro_layer", "threat", "owasp_reference", "likelihood", "impact", "risk_level", "mitigation")
# (section, its units: "rows", "open", "resolved" or the finding prefixes of its table, the item keys in header order, the size per part), in the
# template's order, as ``contracts/part-files.md`` lists them.
THREATS_MD = [
    ("components", "rows", ("component", "type", "maestro_layer", "description"), 59), ("data_flows", "rows", ("source", "destination", "data", "protocol"), 59),
    ("technologies", "rows", ("category", "technology", "version"), 59), ("trust_zones", "rows", ("zone", "trust_level", "components"), 59),
    ("boundary_crossings", "rows", ("crossing", "from_zone", "to_zone", "components", "controls"), 59),
    ("spoofing", ("S",), _STRIDE_KEYS, 16), ("tampering", ("T",), _STRIDE_KEYS, 16), ("repudiation", ("R",), _STRIDE_KEYS, 16),
    ("information_disclosure", ("I",), _STRIDE_KEYS, 16), ("denial_of_service", ("D",), _STRIDE_KEYS, 16),
    ("elevation_of_privilege", ("E",), _STRIDE_KEYS, 16), ("agentic", ("AG", "AGP", "TE"), _AI_KEYS, 16), ("llm", ("LLM", "OI", "MI"), _AI_KEYS, 16),
    ("correlated", "rows", ("group", "findings", "component", "threat_summary", "risk_level"), 27), ("patterns", "rows", ("pattern", "count", "findings"), 59),
    ("resolved", "resolved", ("finding_id", "component", "threat", "last_risk_level", "resolution_reason"), 59),
    ("coverage", "rows", ("component", "s", "t", "r", "i", "d", "e", "ag", "llm", "total"), 59),
    ("gate_requirements", "rows", ("component", "determined_type", "required_categories", "evaluated", "gaps"), 59),
    ("gate_gaps", "rows", ("component", "missing_category", "agents_dispatched", "resolution", "findings_added"), 59),
    ("risk_by_layer", "rows", ("maestro_layer", "finding_count", "highest_severity"), 59), ("risk_levels", "rows", ("risk_level", "count", "percentage"), 59),
    ("actions", "open", ("finding_id", "status", "pattern", "component", "maestro_layer", "threat", "risk_level", "mitigation"), 41),
    ("lifecycle", "rows", ("status", "count", "description"), 59), ("baseline_reference", "rows", ("field", "value"), 59),
]
ROWS_DEFAULT = {"components": 3, "data_flows": 2, "technologies": 1, "trust_zones": 2, "boundary_crossings": 1, "correlated": 0, "patterns": 0, "coverage": 3,
                "gate_requirements": 3, "gate_gaps": 0, "risk_by_layer": 2, "risk_levels": 4, "lifecycle": 0, "baseline_reference": 0}
ROWS_ZERO = {key: 0 for key in ROWS_DEFAULT}
OPEN_DEFAULT = ["S-1", "S-2", "T-1", "I-1", "E-1", "AG-1", "LLM-1", "LLM-2"]
BASELINE_FRONTMATTER = {"source": "reports/earlier/threats.md", "date": "2026-11-01", "finding_count": 5, "run_id": "2026-11-01T10-00-00"}
PART_FOR = {}  # stage -> the function that builds a valid part from a batch input (filled in beside each stage)


def sections_manifest(open_ids=OPEN_DEFAULT, resolved=None, rows=None):
    """A valid ``tachi.sections/1`` manifest (``threat-model-records.md``, "The section manifest"). A run with a baseline has ``resolved`` IDs, and the
    baseline's frontmatter values; one without has ``null`` for both."""
    counts = dict(ROWS_DEFAULT)
    counts.update(rows or {})
    baseline = dict(BASELINE_FRONTMATTER) if resolved is not None else {"source": None, "date": None, "finding_count": None, "run_id": None}
    return {"schema": "tachi.sections/1",
            "frontmatter": {"date": "2026-11-22", "input_format": "mermaid", "classification": "confidential", "run_id": "2026-11-22T10-00-00",
                            "baseline": baseline, "coverage_gate": {"status": "pass", "gaps": []}},
            "open": list(open_ids), "resolved": None if resolved is None else list(resolved), "rows": counts}


def write_sections(h, manifest, raw=None):
    path = h.out / ".tachi-build" / "sections.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw if raw is not None else json.dumps(manifest, indent=2).encode("utf-8"))
    return path


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


def threats_md_sections(manifest):
    """``[(section, its units, its size)]`` for each table that has a unit, in the template's order, from the manifest alone (item O-beta)."""
    ids = sorted(manifest["open"], key=s2_key)
    found = []
    for section, which, _, size in THREATS_MD:
        if which == "rows":
            units = [{"section": section, "row": number} for number in range(1, manifest["rows"][section] + 1)]
        else:
            chosen = ids if which == "open" else sorted(manifest["resolved"] or [], key=s2_key) if which == "resolved" else [
                fid for fid in ids if fid.partition("-")[0] in which]
            units = [{"section": section, "finding_id": fid} for fid in chosen]
        if units:
            found.append((section, units, size))
    return found


def expected_threats_md_batches(manifest):
    """``[(section, units)]`` for each part, in plan order."""
    return [(section, units[start:stop]) for section, units, size in threats_md_sections(manifest) for start, stop in balanced_runs(len(units), size)]


def threats_md_item(section, keys, unit):
    values = {"status": "NEW", "likelihood": "HIGH", "impact": "HIGH", "risk_level": "High", "last_risk_level": "High",
              "maestro_layer": "L4 " + _DASH + " Deployment", "pattern": _DASH}
    return {key: unit["finding_id"] if key == "finding_id" else values.get(key, "%s of %s" % (key, section)) for key in keys}


def threats_md_part(bi):
    keys = {section: item_keys for section, _, item_keys, _ in THREATS_MD}[bi["units"][0]["section"]]
    return {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": "threats-md", "agent_type": TM_AGENT,
            "finding_ids": list(bi["finding_ids"]), "items": [threats_md_item(unit["section"], keys, unit) for unit in bi["units"]], "fragments": []}


PART_FOR["threats-md"] = threats_md_part


def write_part(h, batch_id, mutate=None, raw=None, files=True):
    """A writer's Write: a valid part at the path the batch input names (or ``raw`` bytes there), with ``mutate`` applied to the part first. A ``trees``
    batch also writes each tree file that its input names, unless ``files`` is false."""
    bi = h.batch_input(batch_id)
    path = Path(bi["part_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    if raw is not None:
        path.write_bytes(raw)
    else:
        part = PART_FOR[h.name](bi)
        if mutate is not None:
            mutate(part, bi)
        path.write_text(json.dumps(part), encoding="utf-8")
    if h.name == "trees" and files:
        for finding_id, tree_path in bi["tree_paths"].items():
            Path(tree_path).parent.mkdir(parents=True, exist_ok=True)
            Path(tree_path).write_text(tree_text(finding_id), encoding="utf-8")
    return path


def write_valid_parts(h, skip=()):
    """A valid part for every batch the plan still waits for, except ``skip``."""
    for entry in h.plan_json()["batches"]:
        if entry["state"] == "pending" and entry["batch_id"] not in skip:
            write_part(h, entry["batch_id"])


def pending_ids(printed):
    return sorted(entry["batch_id"] for wave in printed["waves"] for entry in wave)


def wave_entries(printed):
    return [entry for wave in printed["waves"] for entry in wave]


def threats_md_run(stage, cli, root, manifest=None):
    h = RunDir(stage, cli, root, "threats-md")
    write_sections(h, manifest or sections_manifest())
    needs(h.plan_cli(), 0, "plan --stage threats-md, from the section manifest")
    return h


# ---- plan


def test_the_threats_md_plan_makes_a_part_for_each_section_that_has_a_unit_in_the_templates_order(stage, cli, tmp_path):
    manifest = sections_manifest()
    h = RunDir(stage, cli, tmp_path, "threats-md")
    write_sections(h, manifest)
    printed = needs(h.plan_cli(), 0, "plan --stage threats-md, from the section manifest").json
    assert set(printed) == {"plan_id", "plan_digest", "waves"}
    expected = expected_threats_md_batches(manifest)
    assert len(expected) == 16, "the default manifest has 16 tables with a unit: 5 row tables, 4 STRIDE tables, 2 AI tables and 5 summary tables"
    flat = wave_entries(printed)
    assert [entry["batch_id"] for entry in flat] == ["B%03d" % n for n in range(1, len(expected) + 1)]
    assert [entry["section"] for entry in flat] == [section for section, _ in expected]
    for entry, (section, units) in zip(flat, expected):
        assert set(entry) == {"batch_id", "input_path", "part_path", "section", "finding_ids", "rows", "problem"}, "what plan prints for this stage (cli.md)"
        assert entry["finding_ids"] == [unit["finding_id"] for unit in units if "finding_id" in unit] and entry["problem"] is None
        assert entry["rows"] == ([units[0]["row"], units[-1]["row"]] if "row" in units[0] else None)  # reading: rows are 1-based, [first, last]
        assert Path(entry["input_path"]).resolve() == (h.plan_dir / "inputs" / ("%s.json" % entry["batch_id"])).resolve()
        assert Path(entry["part_path"]).resolve() == (h.plan_dir / "parts" / ("%s.a1.json" % entry["batch_id"])).resolve()
        bi = h.batch_input(entry["batch_id"])
        assert set(bi) == BATCH_INPUT_KEYS and bi["schema"] == "tachi.batch-input/1"
        assert (bi["plan_id"], bi["batch_id"], bi["stage"], bi["agent_type"], bi["attempt"]) == (printed["plan_id"], entry["batch_id"], "threats-md", TM_AGENT, 1)
        assert bi["finding_ids"] == entry["finding_ids"] and bi["units"] == units and bi["part_path"] == entry["part_path"]
        assert bi["tree_paths"] == {} and bi["refs"] == {}


def test_the_threats_md_plan_file_holds_no_snapshot_no_refs_and_the_manifests_digest(stage, cli, tmp_path, tachi_version):
    manifest = sections_manifest()
    h = threats_md_run(stage, cli, tmp_path, manifest)
    plan = h.plan_json()
    expected = expected_threats_md_batches(manifest)
    assert set(plan) == PLAN_KEYS and (plan["stage"], plan["agent_type"], plan["tachi_version"]) == ("threats-md", TM_AGENT, tachi_version)
    assert plan["batch_size"] is None, "a stage with per-section sizes records a null batch size (section 4)"
    assert plan["refs"] == {} and plan["architecture_warning"] is None and plan["out_snapshot"] is None
    assert plan["unit_count"] == sum(len(units) for _, units in expected)
    assert plan["retry_budget"] == {"limit": 2 * len(expected), "used": 0}
    assert [entry["batch_id"] for entry in plan["batches"]] == ["B%03d" % n for n in range(1, len(expected) + 1)]
    assert all((entry["parent"], entry["attempt"], entry["state"]) == (None, 1, "pending") for entry in plan["batches"])
    manifest_path = h.out / ".tachi-build" / "sections.json"
    recorded = [value for value in plan["inputs"].values() if value["sha256"] == sha256_of(manifest_path)]
    assert len(recorded) == 1 and Path(recorded[0]["path"]).resolve() == manifest_path.resolve(), "one version: the joiner checks this digest too"


def _manifest_with(section, count):
    """A manifest whose table ``section`` has ``count`` units, and that has no other unit that this test counts."""
    which = {key: kind for key, kind, _, _ in THREATS_MD}[section]
    if which == "rows":
        return sections_manifest(rows={section: count})
    if which == "resolved":
        return sections_manifest(resolved=["D-%d" % n for n in range(1, count + 1)])  # a prefix that the default open IDs don't use
    prefix = "S" if which == "open" else which[0]
    return sections_manifest(open_ids=["%s-%d" % (prefix, n) for n in range(1, count + 1)])


@pytest.mark.parametrize("section,count,sizes", [
    ("components", 59, [59]), ("components", 60, [30, 30]), ("components", 61, [31, 30]), ("spoofing", 16, [16]), ("spoofing", 17, [9, 8]),
    ("agentic", 17, [9, 8]), ("llm", 33, [11, 11, 11]), ("correlated", 27, [27]), ("correlated", 28, [14, 14]), ("actions", 41, [41]),
    ("actions", 42, [21, 21]), ("resolved", 60, [30, 30])])
def test_a_threats_md_section_at_its_size_plans_one_part_and_one_more_unit_plans_balanced_parts(stage, cli, tmp_path, section, count, sizes):
    """NFR-4 and D3's batch granularity, at each size part-files.md gives: 59 rows, 16 findings, 27 groups and 41 actions."""
    h = threats_md_run(stage, cli, tmp_path, _manifest_with(section, count))
    inputs = [h.batch_input(entry["batch_id"]) for entry in h.plan_json()["batches"]]
    found = [len(bi["units"]) for bi in inputs if bi["units"][0]["section"] == section]
    assert sorted(found, reverse=True) == sizes and max(found) - min(found) <= 1


def test_row_units_number_the_rows_of_their_section_and_finding_units_come_in_s2_order(stage, cli, tmp_path):
    manifest = sections_manifest(open_ids=["T-10", "T-9", "T-1", "S-2", "S-1"], rows=dict(ROWS_ZERO, components=61))
    h = threats_md_run(stage, cli, tmp_path, manifest)
    batches = [h.batch_input(entry["batch_id"]) for entry in h.plan_json()["batches"]]
    components = [bi for bi in batches if bi["units"][0]["section"] == "components"]
    # reading: a row unit is {section, row}, and its number is the table's row number, so a second part continues where the first stopped
    spans = [(bi["units"][0]["row"], bi["units"][-1]["row"]) for bi in components]
    assert len(components) == 2 and spans[0][0] == 1 and spans[1][0] == spans[0][1] + 1 and spans[1][1] == 61
    assert abs(len(components[0]["units"]) - len(components[1]["units"])) <= 1
    assert all(set(unit) == {"section", "row"} and unit["row"] == span[0] + number
               for bi, span in zip(components, spans) for number, unit in enumerate(bi["units"]))
    tampering = [bi for bi in batches if bi["units"][0]["section"] == "tampering"]
    assert [bi["units"] for bi in tampering] == [[{"section": "tampering", "finding_id": fid} for fid in ("T-1", "T-9", "T-10")]]
    assert tampering[0]["finding_ids"] == ["T-1", "T-9", "T-10"]


def test_a_baseline_run_plans_the_resolved_lifecycle_and_baseline_tables_too(stage, cli, tmp_path):
    manifest = sections_manifest(resolved=["T-2", "LLM-9"], rows={"lifecycle": 3, "baseline_reference": 4})
    h = threats_md_run(stage, cli, tmp_path, manifest)
    sections = [h.batch_input(entry["batch_id"])["units"][0]["section"] for entry in h.plan_json()["batches"]]
    assert sections == [section for section, _ in expected_threats_md_batches(manifest)]
    assert {"resolved", "lifecycle", "baseline_reference"} <= set(sections)
    resolved = h.batch_input("B%03d" % (sections.index("resolved") + 1))
    assert resolved["finding_ids"] == ["T-2", "LLM-9"]


def test_planning_the_same_manifest_twice_gives_the_same_parts(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path)
    first = [(entry["batch_id"], h.batch_input(entry["batch_id"])["units"]) for entry in h.plan_json()["batches"]]
    needs(h.plan_cli(), 0, "the same plan, again")
    assert [(entry["batch_id"], h.batch_input(entry["batch_id"])["units"]) for entry in h.plan_json()["batches"]] == first


def _manifest_raw(valid, variant):
    text = json.dumps(valid, indent=2)
    tail = text.rstrip()[:-1].rstrip()
    return {"not-json": b"{not json", "top-level-array": b"[]", "empty-file": b"",
            "duplicate-key": (tail + ',\n  "schema": "tachi.sections/1"\n}').encode("utf-8"), "nan": (tail + ',\n  "x": NaN\n}').encode("utf-8"),
            "over-256-kib": (tail + ',\n  "x": "%s"\n}' % ("A" * (256 * 1024))).encode("utf-8")}[variant]


def _fm(**changes):
    def apply(manifest):
        manifest["frontmatter"].update(changes)
    return apply


def _baseline_text(value):
    def apply(manifest):
        manifest["frontmatter"]["baseline"]["source"] = value
    return apply


def _gap(**changes):
    def apply(manifest):
        gap = {"component": "Gateway", "missing_category": "spoofing", "resolution": "findings_produced"}
        gap.update(changes)
        manifest["frontmatter"]["coverage_gate"] = {"status": "warn", "gaps": [gap]}
    return apply


def _rows(**changes):
    def apply(manifest):
        manifest["rows"].update(changes)
    return apply


def _no_rows_key(key):
    def apply(manifest):
        del manifest["rows"][key]
    return apply


# (case, whether the base manifest has a baseline, what to break). Each is a rule of the manifest's contract, and each ends the plan with exit 2.
MANIFEST_BREAKS = [
    ("unknown-key", False, _set("extra", 1)), ("missing-key", False, _drop("rows")), ("wrong-schema", False, _set("schema", "tachi.sections/2")),
    ("no-open-findings", False, _set("open", [])), ("a-repeated-open-id", False, _set("open", ["T-1", "T-1"])),
    ("two-spellings-of-one-id", False, _set("open", ["T-1", "T-01"])), ("an-id-off-the-allow-list", False, _set("open", ["T-1", "X-1"])),
    ("resolved-overlaps-open", True, _set("resolved", ["T-1"])), ("the-same-id-in-two-spellings-across-the-lists", True, _set("resolved", ["S-01"])),
    ("resolved-without-a-baseline", False, _set("resolved", ["T-9"])), ("a-baseline-without-resolved", True, _set("resolved", None)),
    ("a-row-count-missing", False, _no_rows_key("components")), ("an-unknown-row-table", False, _rows(extra=1)),
    ("a-negative-row-count", False, _rows(components=-1)), ("a-row-count-over-5000", False, _rows(components=5001)),
    ("a-boolean-row-count", False, _rows(components=True)),
    ("a-frontmatter-key-too-many", False, _fm(extra="x")), ("a-bad-date", False, _fm(date="22-11-2026")), ("an-input-format-off-the-list", False, _fm(input_format="pdf")),
    ("a-bad-run-id", False, _fm(run_id="yesterday")), ("a-bad-classification-token", False, _fm(classification="Top Secret")),
    ("a-quote-in-a-string", True, _baseline_text('reports/"earlier"/threats.md')), ("a-backslash-in-a-string", True, _baseline_text("reports\\earlier\\threats.md")),
    ("a-bidi-control-in-a-string", True, _baseline_text("reports/" + chr(0x202E) + "earlier/threats.md")),
    ("an-escape-in-a-string", True, _baseline_text("reports/\x1b[31mearlier/threats.md")),
    ("a-quote-in-a-gap-component", False, _gap(component='Gate"way')), ("a-control-in-a-gap-component", False, _gap(component="Gate\x1bway")),
    ("a-gap-resolution-off-the-list", False, _gap(resolution="fixed")), ("a-gap-category-off-the-token-pattern", False, _gap(missing_category="Spoofing Attacks")),
    ("a-coverage-gate-status-off-the-list", False, _fm(coverage_gate={"status": "fail", "gaps": []})),
]


@pytest.mark.parametrize("case,baseline,mutate", MANIFEST_BREAKS, ids=[case for case, _, _ in MANIFEST_BREAKS])
def test_the_threats_md_plan_refuses_a_manifest_that_breaks_its_contract_before_it_writes_anything(stage, cli, tmp_path, case, baseline, mutate):
    """``plan --stage threats-md`` strict-loads the manifest and exits 2 when any rule of its contract fails, so the orchestrator stops with D4's
    error (item O-beta; errata S1P-A18 for the strings, which the joiner writes double-quoted)."""
    h = RunDir(stage, cli, tmp_path, "threats-md")
    manifest = sections_manifest(resolved=["T-2", "LLM-9"] if baseline else None)
    mutate(manifest)
    write_sections(h, manifest)
    refused(h.plan_cli(), "THREATS-MD", "plan --stage threats-md over a manifest with %s" % case)
    assert not (h.build / "current.json").exists(), "a plan that fails leaves no pointer"


@pytest.mark.parametrize("variant", ["not-json", "top-level-array", "empty-file", "duplicate-key", "nan", "over-256-kib"])
def test_the_threats_md_plan_loads_the_manifest_strictly(stage, cli, tmp_path, variant):
    h = RunDir(stage, cli, tmp_path, "threats-md")
    write_sections(h, None, raw=_manifest_raw(sections_manifest(), variant))
    refused(h.plan_cli(), "THREATS-MD", "plan --stage threats-md over a manifest that is %s" % variant)


def test_the_threats_md_plan_exits_1_for_a_missing_manifest_and_reads_no_threats_md(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path, "threats-md")
    refused(h.plan_cli(), "THREATS-MD", "plan --stage threats-md with no section manifest", code=1)
    write_sections(h, sections_manifest())
    assert not (h.out / "threats.md").exists()
    needs(h.plan_cli(), 0, "plan --stage threats-md takes no --threats and reads the manifest alone")


# ---- reconcile


def test_valid_threats_md_parts_for_every_batch_reconcile_to_complete(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path)
    write_valid_parts(h)
    printed = needs(h.reconcile(), 0, "reconcile --stage threats-md").json
    assert set(printed) == RECONCILE_KEYS and printed["status"] == "complete" and printed["waves"] == [] and printed["exhausted"] == []
    assert printed["done"] == [entry["batch_id"] for entry in h.plan_json()["batches"]]


def test_a_missing_threats_md_part_halves_a_row_batch_by_rows_and_says_so(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=dict(ROWS_ZERO, components=4)))
    write_valid_parts(h, skip=["B001"])
    res = needs(h.reconcile(), 3, "reconcile --stage threats-md, a missing part")
    entries = wave_entries(res.json)
    assert [(e["batch_id"], e["section"], e["rows"], e["finding_ids"], e["problem"]) for e in entries] == [
        ("B001-1", "components", [1, 2], [], "missing"), ("B001-2", "components", [3, 4], [], "missing")]
    by_id = {entry["batch_id"]: entry for entry in h.plan_json()["batches"]}
    assert by_id["B001"]["state"] == "split" and (by_id["B001-1"]["attempt"], by_id["B001-2"]["attempt"]) == (2, 2)
    assert h.plan_json()["retry_budget"] == {"limit": 2 * 3, "used": 2}, "a halving counts 2"
    assert [unit["row"] for unit in h.batch_input("B001-2")["units"]] == [3, 4]
    assert Path(h.batch_input("B001-2")["part_path"]).name == "B001-2.a2.json" and Path(entries[1]["part_path"]).name == "B001-2.a2.json"
    write_part(h, "B001-1")
    write_part(h, "B001-2")
    assert needs(h.reconcile(), 0, "reconcile --stage threats-md, after the retry").json["status"] == "complete"


def test_a_missing_threats_md_part_halves_a_finding_batch_by_findings(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1", "T-2", "T-3", "T-4"], rows=ROWS_ZERO))
    assert [h.batch_input(e["batch_id"])["units"][0]["section"] for e in h.plan_json()["batches"]] == ["tampering", "actions"]
    write_valid_parts(h, skip=["B001"])
    entries = wave_entries(needs(h.reconcile(), 3, "reconcile --stage threats-md, a missing finding part").json)
    assert [(e["batch_id"], e["finding_ids"], e["rows"], e["problem"]) for e in entries] == [
        ("B001-1", ["T-1", "T-2"], None, "missing"), ("B001-2", ["T-3", "T-4"], None, "missing")]


def test_a_missing_part_of_one_unit_is_retried_as_it_is(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=ROWS_ZERO))
    write_valid_parts(h, skip=["B001"])
    entries = wave_entries(needs(h.reconcile(), 3, "reconcile --stage threats-md, a missing one-unit part").json)
    assert [(e["batch_id"], e["finding_ids"], e["problem"]) for e in entries] == [("B001", ["T-1"], "missing")]
    by_id = {entry["batch_id"]: entry for entry in h.plan_json()["batches"]}
    assert (by_id["B001"]["attempt"], by_id["B001"]["state"]) == (2, "pending") and h.plan_json()["retry_budget"]["used"] == 1


def _first(key, value):
    def apply(part, bi):
        part["items"][0][key] = value
    return apply


def _drop_item_key(key):
    def apply(part, bi):
        del part["items"][0][key]
    return apply


def _part_key(key, value):
    def apply(part, bi):
        part[key] = value
    return apply


def _extra_row(part, bi):
    part["items"].append(dict(part["items"][0]))


def _short_row(part, bi):
    part["items"].pop()


BAD_VALUE = "SEVERE-9731"
# (case, the section to break, what to break, a key the problem must name, the bad value it must not echo)
THREATS_MD_BREAKS = [
    ("an-unknown-key", "tampering", _first("extra", "x"), "extra", None), ("a-missing-key", "tampering", _drop_item_key("mitigation"), "mitigation", None),
    ("a-number-for-a-string", "components", _first("description", 3), "description", None),
    ("a-risk-level-off-the-list", "tampering", _first("risk_level", BAD_VALUE), "risk_level", BAD_VALUE),
    ("a-status-off-the-list", "tampering", _first("status", BAD_VALUE), "status", BAD_VALUE),
    ("a-likelihood-off-the-list", "tampering", _first("likelihood", BAD_VALUE), "likelihood", BAD_VALUE),
    ("a-layer-off-the-list", "tampering", _first("maestro_layer", BAD_VALUE), "maestro_layer", BAD_VALUE),
    ("a-pattern-off-the-list", "actions", _first("pattern", BAD_VALUE), "pattern", BAD_VALUE),
    ("a-finding-outside-the-batch", "tampering", _first("finding_id", "T-99"), None, None),
    ("a-forbidden-character", "tampering", _first("mitigation", "fix\x1b[31m the thing"), "mitigation", "\x1b"),
    ("a-value-that-is-empty-once-its-edges-are-stripped", "components", _first("description", "   "), "description", None),
    ("a-row-too-many", "components", _extra_row, None, None), ("a-row-too-few", "components", _short_row, None, None),
    ("the-wrong-agent", "components", _part_key("agent_type", "tachi-threat-report"), None, None),
    ("the-wrong-stage", "components", _part_key("stage", "report"), None, None),
    ("a-fragment", "components", _part_key("fragments", [{"slot_key": "x", "text": "y"}]), None, None),
]


@pytest.mark.parametrize("case,section,mutate,key,value", THREATS_MD_BREAKS, ids=[case[0] for case in THREATS_MD_BREAKS])
def test_a_threats_md_part_that_breaks_its_contract_is_invalid_and_retried_with_what_to_fix(stage, cli, tmp_path, case, section, mutate, key, value):
    """An ``invalid`` batch is retried with the same units. The retry's wave entry names the earlier attempt's first failure, the item and the key, never
    the value (part-files.md, "What plan and reconcile print")."""
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1", "T-2", "T-3"], rows=dict(ROWS_ZERO, components=3)))
    target = next(entry["batch_id"] for entry in h.plan_json()["batches"] if h.batch_input(entry["batch_id"])["units"][0]["section"] == section)
    write_valid_parts(h, skip=[target])
    write_part(h, target, mutate=mutate)
    res = needs(h.reconcile(), 3, "reconcile --stage threats-md, an invalid part (%s)" % case)
    entries = wave_entries(res.json)
    assert [e["batch_id"] for e in entries] == [target], "an invalid batch is retried as it is, not halved"
    problem = entries[0]["problem"]
    assert isinstance(problem, str) and problem and problem != "missing"
    if key is not None:
        assert key in problem
    if value is not None:
        assert value not in problem
    retried = {entry["batch_id"]: entry for entry in h.plan_json()["batches"]}[target]
    assert (retried["attempt"], retried["state"]) == (2, "pending") and h.plan_json()["retry_budget"]["used"] == 1
    write_part(h, target)
    assert needs(h.reconcile(), 0, "reconcile --stage threats-md, after the retry").json["status"] == "complete"


def test_threats_md_values_are_evidence_so_digits_markup_and_pipes_are_accepted(stage, cli, tmp_path):
    """No ``threats-md`` value is narrative (step 11 doesn't run): digits stand, and the joiner escapes on output. Only a closed value, a forbidden
    character or an empty value rejects a part."""
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=dict(ROWS_ZERO, components=1)))
    text = "  Port 8443 | <b>bold</b> `code` {{7*7}} &amp; ### a heading-shaped word, two-factor  "
    write_valid_parts(h, skip=["B001", "B002"])
    write_part(h, "B001", mutate=_first("description", text))
    write_part(h, "B002", mutate=_first("threat", text))
    assert needs(h.reconcile(), 0, "reconcile --stage threats-md, a part of evidence").json["status"] == "complete"


def test_reconcile_exits_2_for_a_threats_md_plan_whose_manifest_changed_after_it(stage, cli, tmp_path):
    """One version (item O-beta): the plan pins the manifest's digest, as it pins every input, so a changed manifest can't be joined into this plan."""
    h = threats_md_run(stage, cli, tmp_path)
    write_valid_parts(h)
    path = h.out / ".tachi-build" / "sections.json"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    refused(h.reconcile(), "THREATS-MD", "reconcile --stage threats-md after the manifest changed")


def test_a_threats_md_part_from_an_earlier_plan_never_counts(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path)
    write_valid_parts(h)
    needs(h.plan_cli(), 0, "a second plan")
    res = needs(h.reconcile(), 3, "reconcile --stage threats-md over a fresh plan")
    assert len(wave_entries(res.json)) >= 16 and res.json["done"] == []


def test_threats_md_runs_out_of_attempts_and_exits_4_naming_the_part(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["S-1"], rows=ROWS_ZERO))
    assert [h.batch_input(e["batch_id"])["units"][0]["section"] for e in h.plan_json()["batches"]] == ["spoofing", "actions"]
    for _ in range(2):  # attempts 2 and 3
        needs(h.reconcile(), 3, "reconcile --stage threats-md, nothing written")
    res = needs(h.reconcile(), 4, "reconcile --stage threats-md, the attempts exhausted")
    assert [(e["batch_id"], e["finding_ids"]) for e in res.json["exhausted"]] == [("B001", ["S-1"]), ("B002", ["S-1"])] and res.json["status"] == "exhausted"
    assert "B001" in res.err and "TACHI THREATS-MD FAILED" in res.err


# ---------------------------------------------------------------------------- the joined threats.md: the input of the trees and report stages


def finding(finding_id, status="NEW", risk="High", pattern=_DASH, component="Gateway"):
    return {"id": finding_id, "status": status, "risk": risk, "pattern": pattern, "component": component}


# (the prefixes of a per-finding table, the section heading that precedes it or None, its own heading)
_PER_FINDING = [
    (("S",), None, "### 3.1 Spoofing (S)"), (("T",), None, "### 3.2 Tampering (T)"), (("R",), None, "### 3.3 Repudiation (R)"),
    (("I",), None, "### 3.4 Information Disclosure (I)"), (("D",), None, "### 3.5 Denial of Service (D)"),
    (("E",), None, "### 3.6 Elevation of Privilege (E)"), (("AG", "AGP", "TE"), "## 4. AI Threat Tables", "### 4.1 Agentic Threats (AG)"),
    (("LLM", "OI", "MI"), None, "### 4.2 LLM Threats (LLM)"),
]
CHAINS_OUTCOME = "chains written (3); candidates 5; surfaced 2"
ATTACK_CHAINS_MD = "\n".join([
    "---", 'schema_version: "1.1"', 'date: "2026-11-22"', "chain_count: 3", "surfaced_count: 2", "candidate_count: 5", "---", "", "# Attack Chains", "",
    "## 1. Chain Summary", "", "| Chain ID | Layers | Findings | Max Severity | Chain-Breaking Target | Converging Chains |", "|---|---|---|---|---|---|",
    "| CHAIN-001 | L2 → L3 | S-1 → T-2 | High | T-2 | 1 |", "| CHAIN-002 | L3 → L7 | T-2 → D-4 | Critical | D-4 | 0 |", "",
    "## 2. Chain Details", "", "### CHAIN-001: A first chain", "", "**Surfaced**: Yes", "**Converging chains**: 1", "",
    "### CHAIN-002: A second chain", "", "**Surfaced**: Yes", "**Converging chains**: 0", "",
    "## 3. Other Consolidated Chains", "", "| Chain ID | Layers | Findings | Max Severity | Chain-Breaking Target |", "|---|---|---|---|---|",
    "| CHAIN-003 | L2 → L3 | S-1 → D-4 | High | D-4 |", "", "**Consolidated chains not listed**: 0", ""])


def joined_md(findings, resolved=(), baseline_source=None, outcome=None, groups=(), preamble=""):
    """A synthetic joined ``threats.md`` (a list of ``finding(...)``), with every section that the trees and report planners read: Sections 1 and 2's
    tables, the per-finding tables of Sections 3 and 4, Section 4a's groups, 4c's resolved findings, the outcome record (D13's place, before Section 5),
    and Section 7, whose rows are in reverse S-2 order as a sort by risk leaves them."""
    lines = ["---", 'schema_version: "1.4"', 'date: "2026-11-22"', 'input_format: "mermaid"', 'classification: "confidential"', 'run_id: "2026-11-22T10-00-00"',
             "baseline:", "  source: %s" % ("null" if baseline_source is None else '"%s"' % baseline_source), "  date: null", "  finding_count: null",
             "  run_id: null", "coverage_gate:", '  status: "pass"', "  gaps: []", "---", "", "# Threat Model Report", ""]
    if preamble:
        lines += [preamble, ""]
    lines += ["## 1. System Overview", "", "### Components", "", "| Component | Type | MAESTRO Layer | Description |", "|---|---|---|---|",
              "| Gateway | Process | L4 " + _DASH + " Deployment | The edge gateway |", "", "### Data Flows", "",
              "| Source | Destination | Data | Protocol |", "|---|---|---|---|", "| Client | Gateway | Requests | HTTPS |", "",
              "## 2. Trust Boundaries", "", "### Trust Zones", "", "| Zone | Trust Level | Components |", "|---|---|---|", "| Edge | Untrusted | Gateway |", ""]
    stride_head = ["| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |", "|---|---|---|---|---|---|---|---|---|"]
    ai_head = ["| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |", "|---|---|---|---|---|---|---|---|---|---|"]
    lines += ["## 3. STRIDE Tables", ""]
    for prefixes, section_heading, heading in _PER_FINDING:
        if section_heading is not None:
            lines += [section_heading, ""]
        rows = [f for f in sorted(findings, key=lambda f: s2_key(f["id"])) if f["id"].partition("-")[0] in prefixes]
        if not rows:
            continue
        ai = prefixes[0] in ("AG", "LLM")
        lines += [heading, ""] + (ai_head if ai else stride_head)
        for f in rows:
            owasp = " | LLM01:2026" if ai else ""
            lines.append("| %s | [%s] | %s | L4 %s Deployment | Threat text for %s%s | Medium | High | %s | Mitigation text for %s |"
                         % (f["id"], f["status"], f["component"], _DASH, f["id"], owasp, f["risk"], f["id"]))
        lines.append("")
    if groups:
        lines += ["## 4a. Correlated Findings", "", "| Group | Findings | Component |", "|-------|----------|-----------|"]
        lines += ["| %s | %s | Gateway |" % (group, ", ".join(members)) for group, members in groups] + [""]
    if resolved:
        lines += ["## 4c. Resolved Findings", "", "| ID | Component | Threat | Last Risk Level | Resolution Reason |",
                  "|----|-----------|--------|-----------------|-------------------|"]
        lines += ["| %s | Legacy %d | Old threat %s | High | Component removed |" % (fid, n, fid) for n, fid in enumerate(resolved, 1)] + [""]
    if outcome is not None:
        lines += ["## Attack Chain Outcome", "", "**Attack chain outcome**: %s" % outcome, ""]
    lines += ["## 5. Coverage Matrix", "", "| Component | S | T | R | I | D | E | AG | LLM | Total |", "|---|---|---|---|---|---|---|---|---|---|",
              "| Gateway | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |", "", "## 6. Risk Summary", "", "The counts here are not read by the planners.", "",
              "## 7. Recommended Actions", "",
              "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |", "|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(findings, key=lambda f: s2_key(f["id"]), reverse=True):
        lines.append("| %s | %s | %s | %s | %s | L4 %s Deployment | Threat text for %s | %s | Mitigation text for %s |"
                     % (f["id"], f["status"], _CATEGORY[f["id"].partition("-")[0]], f["pattern"], f["component"], _DASH, f["id"], f["risk"], f["id"]))
    lines += [""]
    if baseline_source is not None:
        lines += ["## 8. Delta Summary", "", "### Finding Lifecycle", "", "| Status | Count | Description |", "|---|---|---|", "| NEW | 1 | New this run |", ""]
    return "\n".join(lines) + "\n"


@pytest.fixture(scope="module")
def parsers(stage):
    sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers

    return tachi_parsers


def test_the_joined_fixture_reads_through_the_shipped_reference_set_reader(parsers):
    """The fixture is what the planners will read, so the shipped reader must read it as it was built: this guards the tests, not the script."""
    items = [finding("S-1", "NEW", "Critical"), finding("T-2", "UNCHANGED", "High"), finding("LLM-3", "UPDATED", "Medium"), finding("AG-4", "NEW", "Low", "trust_exploitation")]
    reference = parsers.parse_reference_set(joined_md(items, resolved=["D-9"], baseline_source="reports/earlier/threats.md", outcome=CHAINS_OUTCOME,
                                                      groups=[("CG-1", ["S-1", "T-2"])]), "threats.md")
    assert sorted(f["id"] for f in reference["open"]) == ["AG-4", "LLM-3", "S-1", "T-2"]
    assert {f["id"]: (f["delta_status"], f["risk_level"]) for f in reference["open"]} == {
        "S-1": ("NEW", "Critical"), "T-2": ("UNCHANGED", "High"), "LLM-3": ("UPDATED", "Medium"), "AG-4": ("NEW", "Low")}
    assert [f["id"] for f in reference["resolved"]] == ["D-9"]
    assert parsers.parse_correlation_groups(joined_md(items, groups=[("CG-1", ["S-1", "T-2"])]), ["S-1", "T-2"])["groups"][0]["members"] == ["S-1", "T-2"]


# ---------------------------------------------------------------------------- the trees batch stage (D6's table, D14; contracts/cli.md, rev. 3)
#
# ``plan --stage trees`` reads the joined threats.md's reference set and the baseline's ``attack-trees/`` listing, and plans a unit for each open Critical
# or High finding whose tree is generated: every one with no baseline or under Rule 2, and the ones with no baseline file under Rule 1. A tree is one Write,
# to the path its batch input names under ``<plan_id>/trees/``, and the part is the batch manifest.

TREE_FINDINGS = [finding("S-1", "UNCHANGED", "Critical"), finding("T-2", "UNCHANGED", "High"), finding("I-3", "UNCHANGED", "High"),
                 finding("D-4", "UNCHANGED", "Medium"), finding("E-5", "UNCHANGED", "Low")]


def tree_text(finding_id):
    return ("# Attack Tree: %s " % finding_id + _DASH + " A synthetic threat\n\n**Finding**: %s | Risk Level: High\n\n```mermaid\ngraph TD\n"
            "    ROOT[\"%s\"]\n    ROOT --> A[\"A step\"]\n```\n" % (finding_id, finding_id))


def trees_item(unit, action=None, score=None):
    """A tree part's item for ``unit``. A Rule 3 unit, planned ``regenerated``, is the one whose item may say another action and the only one that carries
    ``similarity_score`` (S1P-A43, RD-6), so it takes a score from here, 0.5 unless the caller gives one."""
    item = {"finding_id": unit["finding_id"], "delta_status": unit["delta_status"], "action": action or unit["action"]}
    if unit["action"] == "regenerated":
        item["similarity_score"] = 0.5 if score is None else score
    return item


def trees_part(bi):
    return {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": "trees", "agent_type": "tachi-attack-tree-delta",
            "finding_ids": list(bi["finding_ids"]), "items": [trees_item(unit) for unit in bi["units"]], "fragments": []}


PART_FOR["trees"] = trees_part


def plan_trees(stage, cli, root, items, resolved=(), baseline=None, outcome=None):
    """A run directory with a joined threats.md, and ``plan --stage trees`` over it. ``baseline`` is None for no ``--baseline-dir``, or the finding IDs
    whose tree files the baseline directory holds (``[]`` for a baseline whose ``attack-trees/`` is empty, ``False`` for one with none)."""
    h = RunDir(stage, cli, root, "trees")
    threats = h.out / "threats.md"
    threats.write_text(joined_md(items, resolved, baseline_source=None if baseline is None else "reports/earlier/threats.md", outcome=outcome), encoding="utf-8")
    args = ["--threats", threats]
    if baseline is not None:
        directory = Path(root) / "baseline"
        directory.mkdir(parents=True, exist_ok=True)
        if baseline is not False:
            (directory / "attack-trees").mkdir(exist_ok=True)
            for fid in baseline:
                (directory / "attack-trees" / ("%s-attack-tree.md" % fid.lower())).write_text(tree_text(fid), encoding="utf-8")
        args += ["--baseline-dir", directory]
    h.threats, h.args = threats, args
    previous = os.getcwd()
    os.chdir(str(root))  # R-6 resolves a baseline below the working directory, as the command runs: the run's root is the project's
    try:
        return h, h.plan_cli(*args)
    finally:
        os.chdir(previous)


def tree_units(h):
    """``{finding ID: its unit row}``, and the batch inputs in plan order."""
    inputs = [h.batch_input(entry["batch_id"]) for entry in h.plan_json()["batches"]]
    return {unit["finding_id"]: unit for bi in inputs for unit in bi["units"]}, inputs


TREES_CASES = [
    # (case, the findings' statuses, resolved, the baseline's trees, the rule it applies, the findings it plans)
    ("no-baseline-flag", ["NEW", "NEW", "NEW"], (), None, "no-baseline", {"S-1", "T-2", "I-3"}),
    ("a-baseline-directory-with-no-attack-trees", ["UNCHANGED"] * 3, (), False, "no-baseline", {"S-1", "T-2", "I-3"}),
    ("a-baseline-whose-attack-trees-is-empty", ["UNCHANGED"] * 3, (), [], "no-baseline", {"S-1", "T-2", "I-3"}),
    ("rule-1-every-tree-carried", ["UNCHANGED"] * 3, (), ["S-1", "T-2", "I-3"], "Rule 1", set()),
    ("rule-1-one-tree-missing", ["UNCHANGED"] * 3, (), ["S-1", "T-2"], "Rule 1", {"I-3"}),
    ("rule-2-a-new-finding", ["NEW", "UNCHANGED", "UNCHANGED"], (), ["S-1", "T-2", "I-3"], "Rule 2", {"S-1", "T-2", "I-3"}),
    ("rule-2-an-updated-finding", ["UNCHANGED", "UPDATED", "UNCHANGED"], (), ["S-1", "T-2", "I-3"], "Rule 2", {"S-1", "T-2", "I-3"}),
    ("rule-2-a-resolved-finding", ["UNCHANGED"] * 3, ["D-9"], ["S-1", "T-2", "I-3"], "Rule 2", {"S-1", "T-2", "I-3"}),
]


def _tree_case_findings(statuses):
    return [dict(item, status=status) for item, status in zip(TREE_FINDINGS[:3], statuses)] + TREE_FINDINGS[3:]


@pytest.mark.parametrize("case", TREES_CASES, ids=[case[0] for case in TREES_CASES])
def test_the_trees_plan_plans_a_unit_for_each_open_critical_or_high_finding_whose_tree_is_generated(stage, cli, tmp_path, case):
    """D14: the planner, not the agent, applies today's Step 1 table: no baseline generates every tree, Rule 1 carries the trees that have a baseline file
    and generates only the missing ones, and Rule 2 regenerates every one. A Medium, Low or Note finding has no tree, and neither has a resolved one."""
    _, statuses, resolved, baseline, _, expected = case
    h, res = plan_trees(stage, cli, tmp_path, _tree_case_findings(statuses), resolved, baseline)
    needs(res, 0, "plan --stage trees")
    units, inputs = tree_units(h)
    assert set(units) == expected
    assert [fid for bi in inputs for fid in bi["finding_ids"]] == sorted(expected, key=s2_key), "S-2 order, across the batches"
    if not expected:
        assert res.json["waves"] == [] and h.plan_json()["batches"] == [] and h.plan_json()["batch_size"] is None
    for fid, unit in units.items():
        assert unit["delta_status"] == {item["id"]: item["status"] for item in _tree_case_findings(statuses)}[fid]


@pytest.mark.parametrize("case", TREES_CASES, ids=[case[0] for case in TREES_CASES])
def test_the_trees_plan_records_the_rule_it_applied(stage, cli, tmp_path, case):
    """The merged manifest's ``rule_applied`` is "the plan's" (part-files.md and threat-model-records.md), so the assembler can read it from the plan."""
    _, statuses, resolved, baseline, rule, _ = case
    h, res = plan_trees(stage, cli, tmp_path, _tree_case_findings(statuses), resolved, baseline)
    needs(res, 0, "plan --stage trees")
    assert h.plan_json()["params"]["rule_applied"] == rule  # reading: the plan's params hold it, beside reference_digest


def test_a_trees_plan_with_no_critical_or_high_finding_applies_no_op_and_reconciles_complete(stage, cli, tmp_path):
    h, res = plan_trees(stage, cli, tmp_path, TREE_FINDINGS[3:], baseline=None)
    needs(res, 0, "plan --stage trees, with nothing to draw")
    assert res.json["waves"] == [] and h.plan_json()["params"]["rule_applied"] == "no-op"  # reading: the rule is recorded as the agent's manifest does
    done = needs(h.reconcile(), 0, "reconcile --stage trees, a plan with no units").json
    assert done["status"] == "complete" and done["done"] == []


def test_the_trees_plan_file_has_the_trees_agent_a_size_of_12_and_no_snapshot(stage, cli, tmp_path, tachi_version):
    h, res = plan_trees(stage, cli, tmp_path, [finding("S-1", "NEW", "High"), finding("T-2", "NEW", "Critical")])
    needs(res, 0, "plan --stage trees")
    plan = h.plan_json()
    assert set(plan) == PLAN_KEYS and (plan["stage"], plan["agent_type"], plan["tachi_version"]) == ("trees", "tachi-attack-tree-delta", tachi_version)
    assert plan["batch_size"] == 12 and plan["unit_count"] == 2 and plan["out_snapshot"] is None and plan["architecture_warning"] is None
    assert plan["retry_budget"] == {"limit": 2, "used": 0}
    assert re.match(r"^[0-9a-f]{64}\Z", plan["params"]["reference_digest"])
    assert [value["sha256"] for value in plan["inputs"].values() if Path(value["path"]).resolve() == h.threats.resolve()] == [sha256_of(h.threats)]


@pytest.mark.parametrize("count,sizes", [(12, [12]), (13, [7, 6]), (25, [9, 8, 8])])
def test_the_trees_plan_batches_at_most_12_trees_balanced(stage, cli, tmp_path, count, sizes):
    h, res = plan_trees(stage, cli, tmp_path, [finding("S-%d" % n, "NEW", "High") for n in range(1, count + 1)])
    needs(res, 0, "plan --stage trees")
    found = [len(entry["finding_ids"]) for entry in h.plan_json()["batches"]]
    assert sorted(found, reverse=True) == sizes and max(found) - min(found) <= 1


def test_a_trees_batch_input_names_one_path_for_each_tree_under_its_plans_trees_directory(stage, cli, tmp_path):
    """Each tree goes to the path the batch input's ``tree_paths`` names, one for each finding (part-files.md section 3, D6): no path is built from content."""
    h, res = plan_trees(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical"), finding("LLM-12", "NEW", "High")])
    needs(res, 0, "plan --stage trees")
    bi = h.batch_input("B001")
    assert set(bi["tree_paths"]) == {"S-1", "LLM-12"} and bi["finding_ids"] == ["S-1", "LLM-12"]
    for fid, path in bi["tree_paths"].items():
        assert Path(path).is_absolute() and Path(path).parent.resolve() == (h.plan_dir / "trees").resolve()
        assert Path(path).name == "%s-attack-tree.md" % fid.lower(), "D14's file naming: the lowercase ID, then -attack-tree.md"
    assert [(unit["finding_id"], unit["delta_status"], unit["action"]) for unit in bi["units"]] == [
        ("S-1", "NEW", "generated_fresh"), ("LLM-12", "NEW", "generated_fresh")]


def test_the_trees_plan_generates_a_baseline_tree_that_rule_1_finds_missing_as_a_fresh_one(stage, cli, tmp_path):
    h, res = plan_trees(stage, cli, tmp_path, _tree_case_findings(["UNCHANGED"] * 3), baseline=["S-1", "T-2"])
    needs(res, 0, "plan --stage trees, Rule 1")
    units, _ = tree_units(h)
    assert {fid: (unit["delta_status"], unit["action"]) for fid, unit in units.items()} == {"I-3": ("UNCHANGED", "generated_fresh")}


def test_the_reference_digest_is_the_reference_sets_and_survives_the_body_lines_that_steps_2_5_to_2_8_add(stage, cli, tmp_path):
    """RR3: the report plan compares ``params.reference_digest`` with the reference set of the ``threats.md`` that Step 2.9 finds, because Steps 2.5 to
    2.8 change that file by design: the outcome record, the populator's block and the two body lines. A change to a finding must change it."""
    items = [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High")]
    h, res = plan_trees(stage, cli, tmp_path, items)
    needs(res, 0, "plan --stage trees")
    digest = h.plan_json()["params"]["reference_digest"]
    body_lines = "**Architecture source**: `docs/security/architecture.md`\n\n**ID high-water mark**: `S-1, T-2`"
    changed = joined_md(items, outcome=CHAINS_OUTCOME, preamble=body_lines) + "\n## Affected Assets\n\n| Asset | Finding |\n|---|---|\n| Records | S-1 |\n"
    h.threats.write_text(changed, encoding="utf-8")
    needs(h.plan_cli(*h.args), 0, "plan --stage trees over the file with its body lines added")
    assert h.plan_json()["params"]["reference_digest"] == digest
    h.threats.write_text(joined_md([finding("S-1", "NEW", "High"), finding("T-2", "NEW", "High")]), encoding="utf-8")
    needs(h.plan_cli(*h.args), 0, "plan --stage trees over a changed finding")
    assert h.plan_json()["params"]["reference_digest"] != digest


# ---- reconcile


def trees_run(stage, cli, root, items, **kwargs):
    h, res = plan_trees(stage, cli, root, items, **kwargs)
    needs(res, 0, "plan --stage trees")
    return h


def test_valid_tree_parts_and_files_reconcile_to_complete(stage, cli, tmp_path):
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High")])
    write_valid_parts(h)
    printed = needs(h.reconcile(), 0, "reconcile --stage trees").json
    assert printed["status"] == "complete" and printed["done"] == ["B001"] and printed["waves"] == [] and printed["exhausted"] == []


def test_a_trees_batch_with_a_missing_tree_is_missing_and_halves_by_findings(stage, cli, tmp_path):
    """D6's table: done when the part validates and every named tree passes the per-file checks. A missing tree makes the batch ``missing``."""
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High")])
    write_part(h, "B001", files=False)
    Path(h.batch_input("B001")["tree_paths"]["S-1"]).parent.mkdir(parents=True, exist_ok=True)
    Path(h.batch_input("B001")["tree_paths"]["S-1"]).write_text(tree_text("S-1"), encoding="utf-8")  # T-2's tree was never written
    res = needs(h.reconcile(), 3, "reconcile --stage trees, a missing tree")
    assert pending_ids(res.json) == ["B001-1", "B001-2"]
    assert [h.batch_input(b)["finding_ids"] for b in ("B001-1", "B001-2")] == [["S-1"], ["T-2"]]
    for batch_id in ("B001-1", "B001-2"):
        write_part(h, batch_id)
    assert needs(h.reconcile(), 0, "reconcile --stage trees, after the retry").json["status"] == "complete"


@pytest.mark.parametrize("text", [
    "# Attack Tree: S-1\n\nA description and no diagram.\n", tree_text("S-1") + "\n```mermaid\ngraph TD\n    X --> Y\n```\n",
    tree_text("S-1").replace("A step", "A step " + chr(0x202E) + "reversed"), tree_text("S-1").replace("A step", "A step \x1b[31m")],
    ids=["no-mermaid-block", "two-mermaid-blocks", "a-bidi-control", "an-escape-character"])
def test_a_generated_tree_that_fails_the_per_file_checks_is_retried(stage, cli, tmp_path, text):
    """D14's checks (one Mermaid block, no character that ``forbidden_character`` returns), held at ``reconcile`` so that a failing generated tree is
    retried and never reaches Step 2.9 (ADR-050 D14, rev. 3's erratum S1P-A18). One unit, so the retry is the same batch whichever way it is read."""
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical")])
    write_part(h, "B001")
    Path(h.batch_input("B001")["tree_paths"]["S-1"]).write_text(text, encoding="utf-8")
    res = needs(h.reconcile(), 3, "reconcile --stage trees, a tree that fails its per-file checks")
    assert pending_ids(res.json) == ["B001"] and h.plan_json()["batches"][0]["attempt"] == 2


@pytest.mark.parametrize("mutate", [
    lambda part, bi: part["items"][0].update(action="regenerated"), lambda part, bi: part["items"][0].update(delta_status="UPDATED"),
    lambda part, bi: part["items"][0].update(action="invented"), lambda part, bi: part["items"][0].update(extra="x"),
    lambda part, bi: part.update(agent_type="tachi-threat-report")],
    ids=["an-action-that-differs-from-the-batch-input", "a-delta-status-that-differs-from-the-batch-input", "an-action-off-the-list", "an-unknown-key",
         "the-wrong-agent"])
def test_a_trees_part_that_disagrees_with_its_batch_input_is_invalid_and_retried(stage, cli, tmp_path, mutate):
    """The part is the batch manifest: ``delta_status`` and ``action`` equal the batch input's (D6)."""
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical")])
    write_part(h, "B001", mutate=mutate)
    res = needs(h.reconcile(), 3, "reconcile --stage trees, a part that disagrees with its batch input")
    assert pending_ids(res.json) == ["B001"]


# ---------------------------------------------------------------------------- the report batch stage (item O-gamma; part-files.md, "Stage payload: report")
#
# ``plan --stage report --trees-plan ID --trees-plan-digest HEX`` runs after ``assemble-report.py trees``. It refuses a trees plan whose digest or pointer
# differs, or that has a batch that isn't done, and records the trees plan file, the merged tree manifest, ``threats.md`` and, for ``chains written``,
# ``attack-chains.md`` as inputs. A section part holds the fragments of one template section, and a findings part holds one item for each finding.

REPORT_AGENT = "tachi-threat-report"
THREE_FINDINGS = [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High"), finding("D-4", "NEW", "Medium")]


def report_ready(stage, cli, root, items, resolved=(), baseline=False, outcome=None, groups=(), attack_chains=False):
    """The trees stage planned and reconciled to done over a joined ``threats.md``, its merged manifest in place, and what ``plan --stage report`` takes.
    Returns the report run, with its plan arguments in ``args``, and the trees run."""
    ht = RunDir(stage, cli, root, "trees")
    threats = ht.out / "threats.md"
    threats.write_text(joined_md(items, resolved, baseline_source="reports/earlier/threats.md" if baseline else None, outcome=outcome, groups=groups),
                       encoding="utf-8")
    needs(ht.plan_cli("--threats", threats), 0, "plan --stage trees")
    if ht.plan_json()["batches"]:
        write_valid_parts(ht)
        needs(ht.reconcile(), 0, "reconcile --stage trees")
    drawn = [item for item in sorted(items, key=lambda item: (item["risk"] != "Critical", s2_key(item["id"]))) if item["risk"] in ("Critical", "High")]
    (ht.out / "attack-trees").mkdir(exist_ok=True)
    for item in drawn:
        (ht.out / "attack-trees" / ("%s-attack-tree.md" % item["id"].lower())).write_text(tree_text(item["id"]), encoding="utf-8")
    manifest = {"schema_version": "1.0", "rule_applied": "no-baseline", "attack_tree_count": len(drawn),
                "trees": [{"finding_id": item["id"], "delta_status": item["status"], "action": "generated_fresh",
                           "file_path": "attack-trees/%s-attack-tree.md" % item["id"].lower()} for item in drawn],
                "summary": {"fresh": len(drawn), "carried_forward": 0, "regenerated": 0}}
    (ht.out / "attack-trees" / ".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if attack_chains:
        (ht.out / "attack-chains.md").write_text(ATTACK_CHAINS_MD, encoding="utf-8")
    hr = RunDir(stage, cli, root, "report")
    hr.threats, hr.args = threats, ["--threats", threats, "--trees-plan", ht.plan_id, "--trees-plan-digest", ht.digest]
    return hr, ht


def report_batches(hr):
    """``(the section of each batch of the plan, in plan order, the batch inputs)``."""
    inputs = [hr.batch_input(entry["batch_id"]) for entry in hr.plan_json()["batches"]]
    return [bi["units"][0]["section"] for bi in inputs], inputs


def planned_report(stage, cli, root, items, **kwargs):
    hr, ht = report_ready(stage, cli, root, items, **kwargs)
    needs(hr.plan_cli(*hr.args), 0, "plan --stage report, after the trees stage")
    return hr, ht


def report_part(bi):
    base = {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": "report", "agent_type": REPORT_AGENT}
    first = bi["units"][0]
    if "key" in first:  # a section part: prose in fragments, with no finding and no item
        fragments = []
        for unit in bi["units"]:
            if unit["key"] == "themes":
                fragments += [{"slot_key": "theme.1.title", "text": "A first theme"}, {"slot_key": "theme.1.body", "text": "Why it matters to the gateway."}]
            else:
                fragments.append({"slot_key": unit["key"], "text": "A passage that holds no numeral."})
        return dict(base, finding_ids=[], items=[], fragments=fragments)
    items = []
    for unit in bi["units"]:
        if first["section"] == "threat_analysis":
            items.append({"finding_id": unit["finding_id"], "narrative": "A narrative about the finding.",
                          "tree_summary": "A one-line summary of the attack tree." if unit.get("tree") else None})
        else:
            items.append({"finding_id": unit["finding_id"], "effort": "Medium", "dependencies": None})
    return dict(base, finding_ids=list(bi["finding_ids"]), items=items, fragments=[])


PART_FOR["report"] = report_part
BASE_SECTIONS = ["exec_summary", "architecture_overview", "threat_categories", "threat_analysis", "cross_cutting_themes", "remediation_roadmap"]
PATTERNED = [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High"), finding("LLM-3", "NEW", "Medium"), finding("AG-4", "NEW", "Low", "trust_exploitation")]
REPORT_CASES = [
    # (case, the findings, the run's options, the sections that the plan has, in the template's order)
    ("a-first-run-with-no-pattern", THREE_FINDINGS, {}, BASE_SECTIONS),
    ("a-baseline-run-with-a-pattern", PATTERNED, {"baseline": True, "resolved": ["D-9"]},
     BASE_SECTIONS[:5] + ["agentic_patterns", "remediation_roadmap", "delta_summary"]),
    ("an-outcome-of-no-chains-and-a-stale-chain-file", THREE_FINDINGS, {"outcome": "0 chains passed filter (no candidate links); candidates 4", "attack_chains": True}, BASE_SECTIONS),
    ("a-skipped-outcome-and-a-stale-chain-file", THREE_FINDINGS, {"outcome": "skipped (inventory missing)", "attack_chains": True}, BASE_SECTIONS),
]


@pytest.mark.parametrize("case", REPORT_CASES, ids=[case[0] for case in REPORT_CASES])
def test_the_report_plan_has_a_part_for_each_section_that_the_run_has_in_the_templates_order(stage, cli, tmp_path, case):
    """D14: three sections are always planned beside the findings parts, and three are conditional: ``attack_chains`` only for ``chains written``,
    ``agentic_patterns`` when an open finding has a pattern, and ``delta_summary`` when the run has a baseline."""
    _, items, options, sections = case
    hr, ht = planned_report(stage, cli, tmp_path, items, **options)
    found, inputs = report_batches(hr)
    assert found == sections
    chains = [value for value in hr.plan_json()["inputs"].values() if Path(value["path"]).name == "attack-chains.md"]
    assert chains == [], "attack-chains.md is an input for chains written alone, whatever file is in {out}"


def test_the_report_plan_records_its_inputs_and_has_no_refs_no_snapshot_and_a_null_size(stage, cli, tmp_path, tachi_version):
    hr, ht = report_ready(stage, cli, tmp_path, THREE_FINDINGS)
    printed = needs(hr.plan_cli(*hr.args), 0, "plan --stage report, after the trees stage").json
    assert set(printed) == {"plan_id", "plan_digest", "waves"}
    plan = hr.plan_json()
    assert set(plan) == PLAN_KEYS and (plan["stage"], plan["agent_type"], plan["tachi_version"]) == ("report", REPORT_AGENT, tachi_version)
    assert plan["refs"] == {} and plan["batch_size"] is None and plan["out_snapshot"] is None and plan["architecture_warning"] is None
    assert {Path(value["path"]).resolve() for value in plan["inputs"].values()} == {
        (ht.plan_dir / "plan.json").resolve(), (hr.out / "attack-trees" / ".manifest.json").resolve(), hr.threats.resolve()}
    assert all(value["sha256"] == sha256_of(value["path"]) for value in plan["inputs"].values())
    assert plan["params"]["reference_digest"] == ht.plan_json()["params"]["reference_digest"] and re.match(r"^[0-9a-f]{64}\Z", plan["params"]["reference_digest"])
    assert plan["retry_budget"]["limit"] == 2 * len(plan["batches"]) and plan["unit_count"] >= len(plan["batches"])


def test_the_report_plan_records_attack_chains_md_for_chains_written_and_plans_a_unit_for_each_surfaced_chain(stage, cli, tmp_path):
    """R9 (S1P-A58): the outcome record is read through ``tachi_parsers.parse_chain_outcome`` (T116's slice), and the surfaced chains are the Chain Details
    sections of ``attack-chains.md`` that ``parse_attack_chains`` returns with ``surfaced`` true, in file order, which is rank order. The Chain Summary
    table is not read a second time. The file is an input of the plan, and each chain is the unit ``chain.<chain ID>`` of the ``attack_chains`` section."""
    hr, _ = planned_report(stage, cli, tmp_path, THREE_FINDINGS, outcome=CHAINS_OUTCOME, attack_chains=True)
    sections, inputs = report_batches(hr)
    assert sections == BASE_SECTIONS[:5] + ["attack_chains", "remediation_roadmap"]
    assert [unit["key"] for unit in inputs[5]["units"]] == ["chain.CHAIN-001", "chain.CHAIN-002"]
    recorded = [value for value in hr.plan_json()["inputs"].values() if Path(value["path"]).name == "attack-chains.md"]
    assert len(recorded) == 1 and recorded[0]["sha256"] == sha256_of(hr.out / "attack-chains.md")


def test_each_report_section_part_has_a_unit_for_each_fragment_key_of_the_contract(stage, cli, tmp_path):
    hr, _ = planned_report(stage, cli, tmp_path, PATTERNED, baseline=True, resolved=["D-9"])
    sections, inputs = report_batches(hr)
    keys = {bi["units"][0]["section"]: [unit["key"] for unit in bi["units"]] for bi in inputs if "key" in bi["units"][0]}
    assert keys["exec_summary"][:3] == ["risk_posture", "top_threats", "key_recommendations"] and set(keys["exec_summary"]) <= {
        "risk_posture", "top_threats", "key_recommendations", "compliance"}
    assert keys["architecture_overview"] == ["system_context", "trust_boundaries"]
    categories = set(keys["threat_categories"])
    assert {"category.spoofing", "category.tampering", "category.llm", "category.agentic"} <= categories and categories - {
        "category.spoofing", "category.tampering", "category.llm", "category.agentic"} <= {"overview"}, "no summary key: the run has 4 open findings"
    assert keys["cross_cutting_themes"] == ["themes"] and keys["agentic_patterns"] == ["pattern.trust_exploitation"] and keys["delta_summary"] == ["progress"]
    for bi in inputs:
        if "key" in bi["units"][0]:
            assert bi["finding_ids"] == [] and all(unit["section"] == bi["units"][0]["section"] for unit in bi["units"]), "a section part has no finding"
    assert len(inputs) == len(set(sections)) == 8, "a section part is one batch at planning"


def test_a_finding_is_narrated_one_by_one_and_over_30_open_the_medium_low_and_note_ones_are_summarized_by_category(stage, cli, tmp_path):
    """Section 3's rule (part-files.md, "Narrated or summarized"): over 30 open findings, a Medium, Low or Note finding has no item of its own."""
    items = [finding("S-1", "NEW", "High")] + [finding("T-%d" % n, "NEW", "Medium") for n in range(1, 31)]
    hr, _ = planned_report(stage, cli, tmp_path, items)
    sections, inputs = report_batches(hr)
    analysis = [unit for bi in inputs if bi["units"][0]["section"] == "threat_analysis" for unit in bi["units"]]
    assert [unit["finding_id"] for unit in analysis] == ["S-1"] and analysis[0]["tree"] is True
    categories = {unit["key"] for bi in inputs if bi["units"][0]["section"] == "threat_categories" for unit in bi["units"]}
    assert {"category.spoofing", "category.tampering", "summary.tampering"} <= categories and "summary.spoofing" not in categories


def test_a_run_whose_open_findings_are_all_summarized_has_no_analysis_part(stage, cli, tmp_path):
    hr, _ = planned_report(stage, cli, tmp_path, [finding("T-%d" % n, "NEW", "Medium") for n in range(1, 32)])
    sections, _ = report_batches(hr)
    assert "threat_analysis" not in sections and "remediation_roadmap" in sections


@pytest.mark.parametrize("count,sizes", [(22, [22]), (23, [12, 11])])
def test_the_analysis_part_holds_at_most_22_findings_balanced(stage, cli, tmp_path, count, sizes):
    hr, _ = planned_report(stage, cli, tmp_path, [finding("S-%d" % n, "NEW", "High") for n in range(1, count + 1)])
    sections, inputs = report_batches(hr)
    assert sorted((len(bi["units"]) for bi in inputs if bi["units"][0]["section"] == "threat_analysis"), reverse=True) == sizes
    assert all(unit["tree"] is True for bi in inputs if bi["units"][0]["section"] == "threat_analysis" for unit in bi["units"])


@pytest.mark.parametrize("count,sizes", [(144, [144]), (145, [73, 72])])
def test_the_roadmap_part_holds_at_most_144_rows_balanced(stage, cli, tmp_path, count, sizes):
    hr, _ = planned_report(stage, cli, tmp_path, [finding("T-%d" % n, "NEW", "Medium") for n in range(1, count + 1)])
    sections, inputs = report_batches(hr)
    assert sorted((len(bi["units"]) for bi in inputs if bi["units"][0]["section"] == "remediation_roadmap"), reverse=True) == sizes


def test_the_roadmap_has_a_row_for_each_open_finding_that_is_not_a_correlation_groups_non_primary_member(stage, cli, tmp_path):
    """A group's primary is its first member left after the claim rule, among the run's open IDs (D8; erratum S1P-A20), so the roadmap and ``threats.sarif``
    name the same one. T-9 isn't open, so T-1 is the primary, and T-2 has no row of its own."""
    items = [finding("S-1", "NEW", "High"), finding("T-1", "NEW", "High"), finding("T-2", "NEW", "High"), finding("T-3", "NEW", "High")]
    hr, _ = planned_report(stage, cli, tmp_path, items, groups=[("CG-1", ["T-9", "T-1", "T-2"])])
    sections, inputs = report_batches(hr)
    roadmap = [unit["finding_id"] for bi in inputs if bi["units"][0]["section"] == "remediation_roadmap" for unit in bi["units"]]
    analysis = [unit["finding_id"] for bi in inputs if bi["units"][0]["section"] == "threat_analysis" for unit in bi["units"]]
    assert roadmap == ["S-1", "T-1", "T-3"] and analysis == ["S-1", "T-1", "T-2", "T-3"], "every open finding is narrated, and a peer has no roadmap row"


@pytest.mark.parametrize("fault", ["wrong-digest", "newer-trees-plan", "a-batch-that-is-not-done"])
def test_the_report_plan_refuses_a_trees_plan_it_cannot_trust_before_it_writes_anything(stage, cli, tmp_path, fault):
    hr, ht = report_ready(stage, cli, tmp_path, THREE_FINDINGS)
    args = list(hr.args)
    if fault == "wrong-digest":
        args[-1] = "0" * 64
    elif fault == "newer-trees-plan":
        needs(ht.plan_cli("--threats", hr.threats), 0, "a newer trees plan")  # the pointer now names it, so the plan in args is an earlier one
    else:
        waiting = RunDir(stage, cli, tmp_path / "other", "trees")
        (waiting.out / "attack-trees").mkdir()
        (waiting.out / "attack-trees" / ".manifest.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
        waiting.threats = waiting.out / "threats.md"
        waiting.threats.write_text(joined_md(THREE_FINDINGS), encoding="utf-8")
        needs(waiting.plan_cli("--threats", waiting.threats), 0, "a trees plan that waits for its parts")
        hr = RunDir(stage, cli, tmp_path / "other", "report")
        args = ["--threats", waiting.threats, "--trees-plan", waiting.plan_id, "--trees-plan-digest", waiting.digest]
    refused(hr.plan_cli(*args), "REPORT", "plan --stage report over a trees plan with %s" % fault)
    assert not (hr.build / "current.json").exists(), "a plan that fails leaves no pointer"


def test_the_report_plan_exits_1_for_a_missing_merged_manifest(stage, cli, tmp_path):
    hr, _ = report_ready(stage, cli, tmp_path, THREE_FINDINGS)
    (hr.out / "attack-trees" / ".manifest.json").unlink()
    refused(hr.plan_cli(*hr.args), "REPORT", "plan --stage report with no merged tree manifest", code=1)


# ---- reconcile


def test_valid_report_parts_for_every_batch_reconcile_to_complete(stage, cli, tmp_path):
    hr, _ = planned_report(stage, cli, tmp_path, PATTERNED, baseline=True, resolved=["D-9"])
    write_valid_parts(hr)
    printed = needs(hr.reconcile(), 0, "reconcile --stage report").json
    assert printed["status"] == "complete" and printed["done"] == [entry["batch_id"] for entry in hr.plan_json()["batches"]]


def _fragments(**by_index):
    def apply(part, bi):
        for index, change in by_index.items():
            part["fragments"][int(index[1:])].update(change)
    return apply


REPORT_BREAKS = [
    ("a-required-fragment-missing", "exec_summary", lambda part, bi: part["fragments"].pop(0)),
    ("a-fragment-key-twice", "exec_summary", lambda part, bi: part["fragments"].append(dict(part["fragments"][0]))),
    ("an-unknown-fragment-key", "exec_summary", lambda part, bi: part["fragments"].append({"slot_key": "made_up", "text": "x"})),
    ("a-fragment-text-that-is-not-a-string", "exec_summary", _fragments(f0={"text": 3})),
    ("a-fragment-text-that-is-empty-once-stripped", "exec_summary", _fragments(f0={"text": "   "})),
    ("an-item-in-a-section-part", "exec_summary", lambda part, bi: part.update(items=[{"finding_id": "S-1"}])),
    ("a-finding-in-a-section-part", "exec_summary", lambda part, bi: part.update(finding_ids=["S-1"])),
    ("the-wrong-agent", "exec_summary", lambda part, bi: part.update(agent_type="tachi-orchestrator")),
    ("a-theme-with-a-gap", "cross_cutting_themes", lambda part, bi: part.update(
        fragments=[{"slot_key": "theme.2.title", "text": "A"}, {"slot_key": "theme.2.body", "text": "B"}])),
    ("a-theme-title-without-its-body", "cross_cutting_themes", lambda part, bi: part.update(fragments=[{"slot_key": "theme.1.title", "text": "A"}])),
    ("an-effort-off-the-list", "remediation_roadmap", lambda part, bi: part["items"][0].update(effort="Trivial")),
    ("a-null-tree-summary-for-a-critical-finding", "threat_analysis", lambda part, bi: part["items"][0].update(tree_summary=None)),
    ("a-tree-summary-for-a-medium-finding", "threat_analysis", lambda part, bi: part["items"][2].update(tree_summary="A summary that must not be there.")),
    ("a-finding-outside-the-batch", "threat_analysis", lambda part, bi: part["items"][0].update(finding_id="S-99")),
    ("an-unknown-item-key", "remediation_roadmap", lambda part, bi: part["items"][0].update(extra="x")),
    ("a-fragment-in-a-findings-part", "threat_analysis", lambda part, bi: part.update(fragments=[{"slot_key": "x", "text": "y"}])),
]


@pytest.mark.parametrize("case,section,mutate", REPORT_BREAKS, ids=[case[0] for case in REPORT_BREAKS])
def test_a_report_part_that_breaks_its_contract_is_invalid_and_retried_as_it_is(stage, cli, tmp_path, case, section, mutate):
    """Closed values reject the part: the finding, ``effort``, each fragment's key, and whether ``tree_summary`` is null. A section part has no item and
    no finding, and a findings part has no fragment. An invalid batch is retried with the same units, never halved."""
    hr, _ = planned_report(stage, cli, tmp_path, THREE_FINDINGS)
    sections, inputs = report_batches(hr)
    target = hr.plan_json()["batches"][sections.index(section)]["batch_id"]
    write_valid_parts(hr, skip=[target])
    write_part(hr, target, mutate=mutate)
    res = needs(hr.reconcile(), 3, "reconcile --stage report, an invalid part (%s)" % case)
    assert pending_ids(res.json) == [target]
    write_part(hr, target)
    assert needs(hr.reconcile(), 0, "reconcile --stage report, after the retry").json["status"] == "complete"


def test_a_narrative_that_breaks_the_numeral_ban_or_its_limit_does_not_reject_the_part(stage, cli, tmp_path):
    """D3's per-field fallback and step 9: a narrative field with a numeral outside a slot takes the fixed sentence, and one over its limit is cut. The
    part stays valid (the record counts both, at Step 2.9)."""
    hr, _ = planned_report(stage, cli, tmp_path, THREE_FINDINGS)
    sections, _ = report_batches(hr)
    ids = {section: entry["batch_id"] for section, entry in zip(sections, hr.plan_json()["batches"])}
    write_valid_parts(hr, skip=[ids["exec_summary"], ids["threat_analysis"], ids["remediation_roadmap"]])
    write_part(hr, ids["exec_summary"], mutate=_fragments(f0={"text": "There are 42 findings across 3 components. " + "x" * 3000}))
    write_part(hr, ids["threat_analysis"], mutate=lambda part, bi: part["items"][0].update(narrative="This takes 3 steps and 2 hours."))
    write_part(hr, ids["remediation_roadmap"], mutate=lambda part, bi: part["items"][0].update(dependencies="Needs 2 teams, as in {{7*7}}."))
    assert needs(hr.reconcile(), 0, "reconcile --stage report, parts with narrative that falls back").json["status"] == "complete"


def test_a_missing_section_part_halves_by_its_fragment_keys(stage, cli, tmp_path):
    """§4's readings, with a batch's units in place of its IDs: a section part of two or more units that is missing is halved, contiguously."""
    hr, _ = planned_report(stage, cli, tmp_path, THREE_FINDINGS)
    sections, _ = report_batches(hr)
    target = hr.plan_json()["batches"][sections.index("architecture_overview")]["batch_id"]
    write_valid_parts(hr, skip=[target])
    res = needs(hr.reconcile(), 3, "reconcile --stage report, a missing section part")
    assert pending_ids(res.json) == [target + "-1", target + "-2"]
    assert all(set(entry) == {"batch_id", "input_path"} for entry in wave_entries(res.json)), "the report stage prints PR 1's wave entries"
    assert [[unit["key"] for unit in hr.batch_input(batch)["units"]] for batch in (target + "-1", target + "-2")] == [["system_context"], ["trust_boundaries"]]
    for batch in (target + "-1", target + "-2"):
        write_part(hr, batch)
    assert needs(hr.reconcile(), 0, "reconcile --stage report, after the retry").json["status"] == "complete"


# ---------------------------------------------------------------------------- fail for a batch stage: its failed record, and nothing moved (cli.md, rev. 3; RR3)


def planned_stage(stage, cli, root, name):
    if name == "threats-md":
        return threats_md_run(stage, cli, root)
    if name == "trees":
        return trees_run(stage, cli, root, [finding("S-1", "NEW", "Critical")])
    return planned_report(stage, cli, root, THREE_FINDINGS)[0]


BATCH_STAGES = ["threats-md", "trees", "report"]


@pytest.mark.parametrize("name", BATCH_STAGES)
def test_fail_for_a_batch_stage_writes_its_failed_record_and_moves_nothing(stage, cli, tmp_path, tachi_version, name):
    """Only ``fail --stage threat-model`` moves and restores the four canonical files. A batch stage's ``fail`` writes its own record, and the plan's
    ``out_snapshot`` is null, so the record carries no declared-paths warning and no undeclared paths: ``close`` checks the run."""
    h = planned_stage(stage, cli, tmp_path, name)
    (h.out / "threat-report.md").write_bytes(NEW_MD)
    (h.out / "gen.py").write_bytes(b"print('an improvised script')\n")
    res = needs(h.fail("check-failed", detail="a synthetic failure"), 0, "fail --stage %s" % name)
    assert res.json["moved"] == [] and res.json["restored"] == []
    assert (h.out / "threat-report.md").read_bytes() == NEW_MD and (h.out / "gen.py").exists()
    rec = h.record()
    check_record(rec, name, h.plan_id, tachi_version)
    assert rec["error"]["code"] == "check-failed" and rec["warnings"] == [] and rec["undeclared_paths"] == []
    assert rec["counts"] == {"units": h.plan_json()["unit_count"]} and rec["outputs"] == [], "R10: a failed batch stage knows only its units"
    assert Path(res.json["record"]).resolve() == (h.plan_dir / "stage-record.json").resolve()
    assert re.search(r"^TACHI %s FAILED: " % name.upper(), res.err, re.M) and "Kept for diagnosis: %s" % h.plan_dir in res.err


@pytest.mark.parametrize("name", BATCH_STAGES)
def test_a_batch_stage_whose_plan_digest_was_copied_wrong_still_gets_its_failed_record(stage, cli, tmp_path, name):
    """RR3's Step F order relies on this: a report plan whose digest was copied wrong is exit 2 with ``plan-digest-mismatch``, and the record is written."""
    h = planned_stage(stage, cli, tmp_path, name)
    res = h.fail("check-failed", digest="0" * 64)
    assert res.code == 2 and (h.plan_dir / "stage-record.json").is_file(), res.describe()
    assert [w["code"] for w in h.record()["warnings"]] == ["plan-digest-mismatch"]


@pytest.mark.parametrize("name", BATCH_STAGES)
def test_a_batch_stage_stops_at_a_digest_that_differs_and_at_a_stage_that_is_not_the_plans(stage, cli, tmp_path, name):
    h = planned_stage(stage, cli, tmp_path, name)
    refused(h.reconcile(digest="0" * 64), name.upper(), "reconcile --stage %s with another digest" % name)
    other = "report" if name != "report" else "trees"
    res = h.cli("reconcile", "--stage", other, "--out", h.out, *h.plan_args())
    assert res.code in (1, 2), res.describe()  # the plan ID and its pointer belong to this stage only


# ---------------------------------------------------------------------------- one case per exit code for the new invocations (contracts/cli.md), --help, and a real interpreter


def _x_tm_plan_0(stage, cli, root, monkeypatch):
    return RunDir(stage, cli, root).plan_cli()


def _x_tm_plan_1(stage, cli, root, monkeypatch):
    return cli("plan", "--stage", THREAT_MODEL, "--out", Path(root) / "nothing", "--date", DATE)


def _x_tm_plan_2(stage, cli, root, monkeypatch):
    return cli("plan", "--stage", THREAT_MODEL, "--out", RunDir(stage, cli, root).out, "--date", "2026-13-45")


def _x_md_plan_0(stage, cli, root, monkeypatch):
    h = RunDir(stage, cli, root, "threats-md")
    write_sections(h, sections_manifest())
    return h.plan_cli()


def _x_md_plan_1(stage, cli, root, monkeypatch):
    return RunDir(stage, cli, root, "threats-md").plan_cli()


def _x_md_plan_2(stage, cli, root, monkeypatch):
    h = RunDir(stage, cli, root, "threats-md")
    write_sections(h, sections_manifest(open_ids=[]))
    return h.plan_cli()


def _x_md_reconcile_0(stage, cli, root, monkeypatch):
    h = threats_md_run(stage, cli, root)
    write_valid_parts(h)
    return h.reconcile()


def _x_md_reconcile_1(stage, cli, root, monkeypatch):
    h = threats_md_run(stage, cli, root)
    (h.plan_dir / "plan.json").unlink()
    return h.reconcile()


def _x_md_reconcile_2(stage, cli, root, monkeypatch):
    return threats_md_run(stage, cli, root).reconcile(digest="0" * 64)


def _x_md_reconcile_3(stage, cli, root, monkeypatch):
    return threats_md_run(stage, cli, root).reconcile()


def _x_md_reconcile_4(stage, cli, root, monkeypatch):
    h = threats_md_run(stage, cli, root, sections_manifest(open_ids=["S-1"], rows=ROWS_ZERO))
    assert h.reconcile().code == 3 and h.reconcile().code == 3
    return h.reconcile()


def _x_tm_fail_0(stage, cli, root, monkeypatch):
    h = RunDir(stage, cli, root)
    needs(h.plan_cli(), 0, "the run-level plan")
    return h.fail("check-failed")


def _x_tm_fail_2(stage, cli, root, monkeypatch):
    h = RunDir(stage, cli, root)
    needs(h.plan_cli(), 0, "the run-level plan")
    return h.fail("check-failed", digest="0" * 64)


def _x_close_0(stage, cli, root, monkeypatch):
    return closeable(stage, cli, root).close()


def _x_close_2(stage, cli, root, monkeypatch):
    h = closeable(stage, cli, root)
    (h.plan_dir / "checks" / "provenance.json").unlink()
    return h.close()


def _x_close_5(stage, cli, root, monkeypatch):
    return closeable(stage, cli, root, chain=False).close()


def _x_mark_0(stage, cli, root, monkeypatch):
    (Path(root) / "run").mkdir()
    monkeypatch.chdir(root)
    write_run(Path(root), "threats.md", ["S-3"])
    return id_mark(cli, None)


def _x_mark_1(stage, cli, root, monkeypatch):
    (Path(root) / "run").mkdir()
    monkeypatch.chdir(root)
    return id_mark(cli, None, threats="run/absent.md")


def _x_mark_2(stage, cli, root, monkeypatch):
    (Path(root) / "run").mkdir()
    monkeypatch.chdir(root)
    write_run(Path(root), "threats.md", ["S-3"])
    needs(id_mark(cli, None), 0, "id-mark, before its usage error")
    return cli("id-mark", "--threats", "run/threats.md")


PR2_EXIT_CASES = [
    ("plan threat-model", 0, _x_tm_plan_0), ("plan threat-model", 1, _x_tm_plan_1), ("plan threat-model", 2, _x_tm_plan_2),
    ("plan threats-md", 0, _x_md_plan_0), ("plan threats-md", 1, _x_md_plan_1), ("plan threats-md", 2, _x_md_plan_2),
    ("reconcile threats-md", 0, _x_md_reconcile_0), ("reconcile threats-md", 1, _x_md_reconcile_1), ("reconcile threats-md", 2, _x_md_reconcile_2),
    ("reconcile threats-md", 3, _x_md_reconcile_3), ("reconcile threats-md", 4, _x_md_reconcile_4),
    ("fail threat-model", 0, _x_tm_fail_0), ("fail threat-model", 2, _x_tm_fail_2),
    ("close", 0, _x_close_0), ("close", 2, _x_close_2), ("close", 5, _x_close_5),
    ("id-mark", 0, _x_mark_0), ("id-mark", 1, _x_mark_1), ("id-mark", 2, _x_mark_2),
]


@pytest.mark.parametrize("command,code,scenario", PR2_EXIT_CASES, ids=["%s-%d" % (command.replace(" ", "-"), code) for command, code, _ in PR2_EXIT_CASES])
def test_one_case_per_exit_code_for_the_pr2_invocations(stage, cli, tmp_path, monkeypatch, command, code, scenario):
    """contracts/cli.md's table, for what PR 2 adds: each (invocation, code) pair has one case, and the code 3 belongs to ``reconcile`` alone."""
    res = scenario(stage, cli, tmp_path, monkeypatch)
    assert res.code == code, "T092, %s exiting %d\n%s" % (command, code, res.describe())
    if command.split()[0] != "reconcile":
        assert res.code != 3
    if code in (1, 2) and (command, code) != ("id-mark", 2):  # id-mark's 2 is a usage error, which argparse prints
        assert re.search(r"^TACHI [A-Z-]+ FAILED: ", res.err, re.M), "T092, %s exiting %d, with D4's message\n%s" % (command, code, res.describe())


def test_help_names_the_pr2_commands_and_the_pr2_arguments(stage, cli):
    top = needs(cli("--help"), 0, "--help, naming close and id-mark").out
    assert "close" in top and "id-mark" in top, "T092, --help must name close and id-mark\n" + top
    for argv in (["close", "--help"], ["id-mark", "--help"]):
        assert needs(cli(*argv), 0, "%s" % " ".join(argv)).out
    assert "--no-baseline" in cli("id-mark", "--help").out and "--baseline" in cli("id-mark", "--help").out
    plan_help = cli("plan", "--help").out
    for name in ("threat-model", "threats-md", "trees", "report", "--trees-plan", "--trees-plan-digest"):
        assert name in plan_help, name


def test_the_pr2_invocations_exit_with_their_codes_from_a_real_interpreter(tmp_path):
    """What a process alone shows (H15): the ``__main__`` guard turns the result into the exit status, one JSON object reaches stdout, and an error
    reaches stderr alone. ``close`` ends with 5 here (a warning), which no earlier process case shows."""
    out = tmp_path / "run"
    out.mkdir()
    threats = out / "threats.md"
    threats.write_text(make_threats_md(["S-3", "T-5"]), encoding="utf-8")
    marked_run = _run_script("id-mark", "--threats", threats, "--no-baseline")
    assert marked_run.returncode == 0, "T092, id-mark from a real interpreter\n" + marked_run.stderr
    assert isinstance(json.loads(marked_run.stdout), dict) and real_marks(threats.read_text(encoding="utf-8")) == ["S-3, T-5"]
    absent = _run_script("id-mark", "--threats", out / "absent.md", "--no-baseline")
    assert absent.returncode == 1 and absent.stdout == "" and absent.stderr.strip(), "T092, id-mark on a missing file\n" + absent.stderr

    planned = _run_script("plan", "--stage", THREAT_MODEL, "--out", out, "--date", DATE)
    assert planned.returncode == 0, "T092, plan --stage threat-model from a real interpreter\n" + planned.stderr
    printed = json.loads(planned.stdout)
    checks = out / ".tachi-build" / THREAT_MODEL / printed["plan_id"] / "checks"
    checks.mkdir()
    (checks / "provenance.json").write_text(json.dumps(handoff("provenance", printed["plan_id"], warnings=[WARN_REISSUED])), encoding="utf-8")
    closed = _run_script("close", "--stage", THREAT_MODEL, "--out", out, "--plan", printed["plan_id"], "--plan-digest", printed["plan_digest"])
    assert closed.returncode == 5, closed.stderr
    assert isinstance(json.loads(closed.stdout), dict)
    wrong = _run_script("close", "--stage", THREAT_MODEL, "--out", out, "--plan", printed["plan_id"], "--plan-digest", "0" * 64)
    assert wrong.returncode == 2 and wrong.stderr.strip() and "TACHI THREAT-MODEL FAILED" in wrong.stderr


# ---------------------------------------------------------------------------- the second pass over T092: what the first pass left unpinned (S1P-A43 to S1P-A63)
#
# The cases above were written before the code, from the contracts and OS's own readings of them (R1 to R13), which the architect then ruled. These pin
# what the rulings left to the code: the pointers that a plan takes, R6's restore for every stage, what a failed run's record holds, the baseline readings of
# ``id-mark``, and the shapes that the planners print and the units hold.

PR2_POINTERS = {THREAT_MODEL: (), "threats-md": (), "trees": ("threats", "baseline_dir"), "report": ("threats", "trees_plan", "trees_plan_digest")}
POINTER_FLAGS = {"threats": "--threats", "risk_scores": "--risk-scores", "baseline_dir": "--baseline-dir", "architecture": "--architecture",
                 "target": "--target", "trees_plan": "--trees-plan", "trees_plan_digest": "--trees-plan-digest"}
FOREIGN_POINTERS = [(name, pointer) for name, own in PR2_POINTERS.items() for pointer in POINTER_FLAGS if pointer not in own]


@pytest.mark.parametrize("name,pointer", FOREIGN_POINTERS, ids=["%s-%s" % pair for pair in FOREIGN_POINTERS])
def test_a_pr2_plan_refuses_a_pointer_that_is_not_its_own_and_writes_nothing(stage, cli, tmp_path, name, pointer):
    """S1P-A63: each PR 2 plan takes only its own pointers, so a stale pointer in a command line is refused, never ignored."""
    h = RunDir(stage, cli, tmp_path, name)
    res = h.cli("plan", "--stage", name, "--out", h.out, "--date", DATE, POINTER_FLAGS[pointer], "0" * 64)
    refused(res, name.upper(), "plan --stage %s with %s" % (name, POINTER_FLAGS[pointer]))
    assert POINTER_FLAGS[pointer] in res.err and not (h.out / ".tachi-build").exists(), "nothing is written"


@pytest.mark.parametrize("name", STAGE_NAMES)
@pytest.mark.parametrize("flag,value", [("--trees-plan", FAKE_PLAN_ID), ("--trees-plan-digest", "0" * 64)])
def test_a_pr1_plan_refuses_the_two_pointers_that_only_the_report_stage_takes(stage, cli, tmp_path, name, flag, value):
    """PR 1's two stages keep every pointer they had, and a flag that is the report stage's alone is a stale one for them."""
    h = Harness(stage, cli, tmp_path, name)
    refused(h.plan_cli(flag, value), name.upper(), "plan --stage %s with %s" % (name, flag))
    assert not (h.out / ".tachi-build").exists()


def test_a_pr2_plan_takes_its_batch_size_through_the_function_interface_only(stage, cli, tmp_path):
    """D6: a size is a constant of the script, and a smaller one reaches the planner through ``plan_stage``'s argument alone. For a stage whose sizes
    are per section it sets every part's size."""
    h = RunDir(stage, cli, tmp_path, "threats-md")
    write_sections(h, sections_manifest(open_ids=["S-1", "S-2", "S-3", "S-4", "S-5"], rows=dict(ROWS_ZERO, components=5)))
    printed = stage.plan_stage(stage="threats-md", out=h.out, date=DATE, batch_size=2)
    h.plan_id = printed["plan_id"]
    sizes = [len(h.batch_input(entry["batch_id"])["units"]) for entry in h.plan_json()["batches"]]
    assert sizes == [2, 2, 1, 2, 2, 1, 2, 2, 1], "components, spoofing and actions: 5 units each, cut at 2 into three balanced runs"
    for size in (0, 501, True, "4"):
        with pytest.raises(stage.StageError):
            stage.plan_stage(stage="threats-md", out=h.out, date=DATE, batch_size=size)


# ---- R6 for PR 1's two stages (S1P-A55)


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_fail_puts_back_a_pr1_output_that_was_deleted_after_the_plan(stage, cli, tmp_path, name):
    """S1P-A55 (R6): D4's "changed since the plan" includes a file that is gone. Nothing moves for it, the pre-image goes back with the copy's bits, and the
    name is listed in ``restored`` alone. A name that the plan recorded no pre-image for stays empty, and a file that a run wrote there still moves aside."""
    h = Harness(stage, cli, tmp_path, name, ids=MIXED_IDS[:3])
    h.earlier(sarif=False)  # only the markdown was there when the plan was made
    needs(h.plan_cli(), 0, "plan --stage %s" % name)
    (h.out / h.md).unlink()
    (h.out / h.sarif).write_bytes(NEW_SARIF)
    res = needs(h.fail(), 0, "fail --stage %s over a deleted output" % name)
    assert res.json["moved"] == [h.sarif] and res.json["restored"] == [h.md]
    assert (h.out / h.md).read_bytes() == EARLIER_MD and not (h.out / h.sarif).exists()
    assert [Path(output["path"]).name for output in h.read_json(h.plan_dir / "stage-record.json")["outputs"]] == [h.sarif], "only a file that moved is listed"


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_fail_leaves_a_name_empty_when_the_plan_recorded_no_pre_image_for_it(stage, cli, tmp_path, name):
    h = Harness(stage, cli, tmp_path, name, ids=MIXED_IDS[:3])
    needs(h.plan_cli(), 0, "plan --stage %s" % name)
    res = needs(h.fail(), 0, "fail --stage %s over names that were empty at plan time" % name)
    assert res.json["moved"] == [] and res.json["restored"] == [] and not (h.out / h.md).exists() and not (h.out / h.sarif).exists()


@pytest.mark.parametrize("name", STAGE_NAMES)
def test_fail_does_not_put_back_a_deleted_output_whose_pre_image_no_longer_matches(stage, cli, tmp_path, name):
    """KB 21's double gate holds for the empty name too: a copy whose digest differs from the one the plan recorded never goes back."""
    h = Harness(stage, cli, tmp_path, name, ids=MIXED_IDS[:3])
    h.earlier()
    needs(h.plan_cli(), 0, "plan --stage %s" % name)
    (h.plan_dir / "preimage" / h.md).write_bytes(b"# a tampered copy\n")
    (h.out / h.md).unlink()
    res = h.fail()
    assert res.code == 2 and (h.plan_dir / "stage-record.json").is_file(), res.describe()
    assert not (h.out / h.md).exists() and res.json["restored"] == []
    assert {w["code"] for w in h.read_json(h.plan_dir / "stage-record.json")["warnings"]} == {"move-refused"}


# ---- fail takes its plan from its arguments (T092's pin; whether fail should refuse such a plan is T136's follow-up)


@pytest.mark.parametrize("name", [THREAT_MODEL, "risk-score"])
def test_fail_sets_the_records_plan_id_from_its_arguments_and_never_checks_that_plan_json_names_itself(stage, cli, tmp_path, name):
    """A plan directory whose ``plan.json`` names another plan, with the pointer on the directory and the digest of that file, passes every check that
    ``fail`` makes: it takes the record's ``plan_id`` from ``--plan``. ``trusted_plan`` would refuse such a plan, and ``fail`` doesn't call it."""
    h = RunDir(stage, cli, tmp_path, name) if name == THREAT_MODEL else Harness(stage, cli, tmp_path, name)
    needs(h.plan_cli(), 0, "the plan")
    named_by_the_file = h.plan_id
    other = "20200101T000000Z-aaaaaaaaaaaa"
    (h.build / other).mkdir()
    (h.build / other / "plan.json").write_bytes((h.plan_dir / "plan.json").read_bytes())
    (h.build / "current.json").write_text(json.dumps({"schema": "tachi.plan-pointer/1", "plan_id": other}), encoding="utf-8")
    res = h.cli("fail", "--stage", name, "--out", h.out, "--plan", other, "--plan-digest", sha256_of(h.build / other / "plan.json"), "--reason", "check-failed")
    needs(res, 0, "fail --stage %s over a plan.json that names another plan" % name)
    record = h.read_json(h.build / other / "stage-record.json")
    assert record["plan_id"] == other and Path(res.json["record"]).resolve() == (h.build / other / "stage-record.json").resolve()
    assert h.read_json(h.build / other / "plan.json")["plan_id"] == named_by_the_file
    assert not (h.build / named_by_the_file / "stage-record.json").exists()


# ---- the run's record, what fail and close hold in it


def test_close_has_no_exit_1_so_a_missing_out_directory_is_a_2(stage, cli, tmp_path):
    """S1P-A61: the table of ``close`` has no 1. A run-level plan or pointer that is missing is a 2, and so is the directory that holds them."""
    refused(cli("close", "--stage", THREAT_MODEL, "--out", tmp_path / "nothing", "--plan", FAKE_PLAN_ID, "--plan-digest", "0" * 64), "THREAT-MODEL",
            "close over a missing --out")
    h = RunDir(stage, cli, tmp_path)
    refused(h.close(plan_id=FAKE_PLAN_ID, digest="0" * 64), "THREAT-MODEL", "close over a plan that was never made")


def test_close_stage_takes_the_run_level_plan_alone(stage, tmp_path):
    for other in ("risk-score", "compensating-controls", "threats-md", "trees", "report"):
        with pytest.raises(stage.StageError) as info:
            stage.close_stage(other, tmp_path, FAKE_PLAN_ID, "0" * 64)
        assert info.value.code == 2


def test_fail_lists_the_undeclared_paths_of_the_run_in_its_record(stage, cli, tmp_path):
    """The run-level plan snapshots {out}, so its ``fail`` runs the declared-paths check as PR 1's does, and a batch stage's, which takes no snapshot, doesn't."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    (h.out / "gen.py").write_text("print('an improvised script')\n", encoding="utf-8")
    needs(h.fail("check-failed"), 0, "fail --stage threat-model")
    assert h.record()["undeclared_paths"] == ["gen.py"]


def test_fail_keeps_its_record_within_the_warning_cap_when_the_hand_off_files_hold_more(stage, cli, tmp_path):
    """Section 6, the record's cap, for ``fail`` as for ``close``: the first 999 stay, then ``warnings-truncated`` with the full count. A move that is
    refused still shows in a record that is full: the folded warnings give way to it, so the record stays valid and says why the exit is 2."""
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    chain = [{"code": "chain-outcome:rewritten", "detail": "chain warning %d" % n} for n in range(600)]
    prov = [{"code": "id:reissued", "detail": "provenance warning %d" % n} for n in range(700)]
    h.write_handoff("attack-chains", warnings=chain)
    h.write_handoff("provenance", warnings=prov)
    needs(h.fail("check-failed"), 0, "fail --stage threat-model, over a full record")
    warnings = h.record()["warnings"]
    assert len(warnings) == 1000 and warnings[:999] == (chain + prov)[:999]
    assert warnings[999]["code"] == "warnings-truncated" and "1300" in warnings[999]["detail"]

    (h.out / "threats.md").mkdir()  # a directory at a canonical name: the move is refused
    res = h.fail("check-failed")
    assert res.code == 2, res.describe()
    warnings = h.record()["warnings"]
    assert len(warnings) == 1000 and warnings[:998] == (chain + prov)[:998] and warnings[998]["code"] == "warnings-truncated"
    assert warnings[999]["code"] == "move-refused"


@pytest.mark.parametrize("name", BATCH_STAGES)
def test_fail_after_the_batches_are_done_records_each_of_them(stage, cli, tmp_path, name):
    """A batch stage's failed record knows its batches: the parts that it accepted give its ``input_digest`` and its ``done`` count, though it moves nothing."""
    h = planned_stage(stage, cli, tmp_path, name)
    write_valid_parts(h)
    needs(h.reconcile(), 0, "reconcile --stage %s" % name)
    needs(h.fail("render-failed"), 0, "fail --stage %s over done batches" % name)
    rec, plan = h.record(), h.plan_json()
    assert rec["batches"]["done"] == rec["batches"]["planned"] == len(plan["batches"]) and rec["counts"] == {"units": plan["unit_count"]}
    assert re.match(r"^sha256:[0-9a-f]{64}\Z", rec["input_digest"]) and rec["outputs"] == []


@pytest.mark.parametrize("name", BATCH_STAGES)
def test_a_failed_record_is_still_written_when_the_part_of_a_done_batch_no_longer_validates(stage, cli, tmp_path, name):
    """The digest of a failed record covers the parts that still validate, so a part that has turned invalid since is left out and ``fail`` still writes."""
    h = planned_stage(stage, cli, tmp_path, name)
    write_valid_parts(h)
    needs(h.reconcile(), 0, "reconcile --stage %s" % name)
    first = h.plan_json()["batches"][0]
    Path(h.batch_input(first["batch_id"])["part_path"]).write_bytes(b"{not json")
    needs(h.fail("check-failed"), 0, "fail --stage %s over a part that no longer validates" % name)
    assert h.record()["batches"]["done"] == len(h.plan_json()["batches"])


# ---- id-mark's baseline (S1P-A54, ruling B)


def test_id_mark_takes_a_baseline_whose_mark_line_reads_whatever_its_section_7_holds(stage, cli, marked):
    """S1P-A54: a baseline whose mark line reads is enough. Its Section 7, which can't be read here, is never asked for."""
    threats = write_run(marked, "threats.md", ["S-3"])
    (marked / "run" / "baseline.md").write_text(make_threats_md(["S-1"], section7="missing", preamble=MARK_TEXT % "S-14, T-22"), encoding="utf-8")
    res = needs(id_mark(cli), 0, "id-mark over a baseline with a mark and no Section 7")
    assert real_marks(threats.read_text(encoding="utf-8")) == ["S-14, T-22"] and res.json["floor"] == "mark"


def test_id_mark_stops_when_the_baseline_has_no_mark_and_its_findings_cannot_be_read(stage, cli, marked):
    """S1P-A54: with no mark to take, the seed needs the baseline's findings, and a mark that it can't compute is never written (a lower one lets an ID come back)."""
    threats = write_run(marked, "threats.md", ["S-3"])
    (marked / "run" / "baseline.md").write_text(make_threats_md(["S-1"], section7="missing"), encoding="utf-8")
    before = threats.read_bytes()
    refused(id_mark(cli), "THREAT-MODEL", "id-mark over a baseline with no mark and no Section 7")
    assert threats.read_bytes() == before


@pytest.mark.parametrize("value", ["S-5,T-2", "S-5, S-6", "not an id", "", "S-5 T-6", "S-5, "],
                         ids=["no-space-after-the-comma", "a-prefix-twice", "no-id", "empty", "no-comma", "a-trailing-comma"])
def test_a_baseline_mark_line_that_does_not_hold_marks_reads_as_absent(stage, cli, marked, value):
    """The line is ``MARKS``, a backtick-quoted run of IDs separated by ``, `` with no prefix twice. Any other value is no mark, so the seed applies."""
    threats = write_run(marked, "threats.md", ["S-3"])
    write_run(marked, "baseline.md", ["S-3"], ["S-9"], preamble=MARK_TEXT % value)
    res = needs(id_mark(cli), 0, "id-mark over a baseline whose mark line is %r" % value)
    assert real_marks(threats.read_text(encoding="utf-8")) == ["S-9"] and res.json["floor"] == "seed"


def test_id_mark_counts_the_runs_own_section_4c_and_prints_what_it_did(stage, cli, marked):
    """An ID in this run's Section 4c has been used, so it is never numbered again. The printed object says what the line is, what happened to the file and
    where the baseline's side came from."""
    threats = write_run(marked, "threats.md", ["S-3"], resolved=["T-7"])
    assert needs(id_mark(cli, None), 0, "id-mark").json == {"mark": "S-3, T-7", "action": "added", "floor": "none"}
    assert real_marks(threats.read_text(encoding="utf-8")) == ["S-3, T-7"]
    assert needs(id_mark(cli, None), 0, "id-mark, again").json["action"] == "unchanged"
    threats.write_text(threats.read_text(encoding="utf-8").replace("S-3, T-7", "S-999"), encoding="utf-8")
    assert needs(id_mark(cli, None), 0, "id-mark over a stale mark").json["action"] == "replaced"


def test_id_mark_refuses_a_baseline_that_is_a_link(stage, cli, marked):
    write_run(marked, "threats.md", ["S-3"])
    real = write_run(marked, "real.md", ["S-3"])
    (marked / "run" / "baseline.md").symlink_to(real)
    refused(id_mark(cli), "THREAT-MODEL", "id-mark over a linked baseline")


# ---- the run-level plan, and the threats-md stage (S1P-A56)


def test_the_run_level_plan_reconciles_complete_with_nothing_to_do(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path)
    needs(h.plan_cli(), 0, "the run-level plan")
    printed = needs(h.reconcile(), 0, "reconcile --stage threat-model").json
    assert printed["status"] == "complete" and printed["done"] == [] and printed["waves"] == [] and printed["exhausted"] == []


def test_a_missing_part_of_an_odd_number_of_rows_halves_with_the_extra_row_in_the_first_child(stage, cli, tmp_path):
    """S1P-A56: a halving cuts the units contiguously, and ``<parent>-1`` takes the extra unit of an odd count, as the planner cuts a table."""
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=dict(ROWS_ZERO, components=5)))
    write_valid_parts(h, skip=["B001"])
    entries = wave_entries(needs(h.reconcile(), 3, "reconcile --stage threats-md, a missing part of 5 rows").json)
    assert [(entry["batch_id"], entry["rows"]) for entry in entries] == [("B001-1", [1, 3]), ("B001-2", [4, 5])]


def test_an_overflow_object_halves_a_threats_md_batch_and_its_problem_is_the_reason(stage, cli, tmp_path):
    """An overflow object is a kind of failure that the planner halves for, and the wave entry's ``problem`` is the part reader's detail, unchanged."""
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=dict(ROWS_ZERO, components=2)))
    write_valid_parts(h, skip=["B001"])
    bi = h.batch_input("B001")
    overflow = {"schema": "tachi.overflow/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": bi["stage"], "agent_type": bi["agent_type"],
                "reason": "output-budget"}
    write_part(h, "B001", raw=json.dumps(overflow).encode("utf-8"))
    entries = wave_entries(needs(h.reconcile(), 3, "reconcile --stage threats-md, an overflow object").json)
    assert [(e["batch_id"], e["rows"], e["problem"]) for e in entries] == [("B001-1", [1, 1], "output-budget"), ("B001-2", [2, 2], "output-budget")]


def test_the_exit_4_message_names_the_rows_of_a_batch_that_holds_no_finding(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=dict(ROWS_ZERO, components=2)))
    write_valid_parts(h, skip=["B001"])  # no part of B001 or of its halves is ever written
    for _ in range(2):
        needs(h.reconcile(), 3, "reconcile --stage threats-md, a part that never comes")
    res = needs(h.reconcile(), 4, "reconcile --stage threats-md, the attempts exhausted")
    assert "Batch B001-1: components rows 1 to 1" in res.err
    needs(h.fail("unrecoverable-batch"), 0, "fail --stage threats-md")
    assert h.record()["error"]["batch_id"] == "B001-1"


def test_the_exit_4_message_names_the_fragment_keys_of_a_report_section(stage, cli, tmp_path):
    hr, _ = planned_report(stage, cli, tmp_path, THREE_FINDINGS)
    sections, _ = report_batches(hr)
    target = hr.plan_json()["batches"][sections.index("architecture_overview")]["batch_id"]
    write_valid_parts(hr, skip=[target])
    for _ in range(2):
        needs(hr.reconcile(), 3, "reconcile --stage report, a part that never comes")
    res = needs(hr.reconcile(), 4, "reconcile --stage report, the attempts exhausted")
    assert "architecture_overview: system_context" in res.err and "TACHI REPORT FAILED" in res.err


# ---- the trees stage: Rule 3's units, the baseline and the tree files (S1P-A43, S1P-A44, R11, RD-6, RD-8, RD-16)


def _rule_3_run(stage, cli, tmp_path):
    items = [finding("S-1", "NEW", "Critical"), finding("T-2", "UNCHANGED", "High"), finding("I-3", "UNCHANGED", "High"), finding("D-4", "UPDATED", "High")]
    h, res = plan_trees(stage, cli, tmp_path, items, baseline=["T-2", "D-4"])  # the baseline has trees for T-2 and D-4 only
    needs(res, 0, "plan --stage trees, Rule 2")
    return h


def test_a_rule_2_plan_plans_a_rule_3_unit_for_an_unchanged_finding_whose_baseline_has_a_tree(stage, cli, tmp_path):
    """Rule 2 regenerates every tree, and an UNCHANGED finding that the baseline has a tree for is Rule 3's: planned ``regenerated``, which the agent's
    item may answer with ``regenerated`` or ``carried_forward``. A finding that is NEW or UPDATED, or has no baseline tree, is generated fresh."""
    h = _rule_3_run(stage, cli, tmp_path)
    units, _ = tree_units(h)
    assert {fid: unit["action"] for fid, unit in units.items()} == {
        "S-1": "generated_fresh", "T-2": "regenerated", "I-3": "generated_fresh", "D-4": "generated_fresh"}
    plan = h.plan_json()
    assert plan["params"]["rule_applied"] == "Rule 2" and Path(plan["refs"]["baseline_dir"]).resolve() == (tmp_path / "baseline").resolve()
    assert plan["batch_size"] == 12 and plan["preimage"] == {} and plan["out_snapshot"] is None


def test_a_rule_3_unit_may_be_carried_forward_and_its_item_says_so(stage, cli, tmp_path):
    h = _rule_3_run(stage, cli, tmp_path)

    def carry(part, bi):
        for item in part["items"]:
            if item["finding_id"] == "T-2":
                item.update(action="carried_forward", similarity_score=0.93)

    write_part(h, "B001", mutate=carry)
    assert needs(h.reconcile(), 0, "reconcile --stage trees, a Rule 3 unit that the baseline's tree wins").json["status"] == "complete"


@pytest.mark.parametrize("fault", ["no-score", "a-score-on-a-fresh-tree", "a-fresh-action-for-a-rule-3-unit", "a-score-above-1", "a-boolean-score"])
def test_a_trees_item_that_breaks_rule_3s_readings_is_invalid_and_retried_as_it_is(stage, cli, tmp_path, fault):
    h = _rule_3_run(stage, cli, tmp_path)

    def break_it(part, bi):
        by_id = {item["finding_id"]: item for item in part["items"]}
        if fault == "no-score":
            del by_id["T-2"]["similarity_score"]
        elif fault == "a-score-on-a-fresh-tree":
            by_id["S-1"]["similarity_score"] = 0.5
        elif fault == "a-fresh-action-for-a-rule-3-unit":
            by_id["T-2"]["action"] = "generated_fresh"
        elif fault == "a-score-above-1":
            by_id["T-2"]["similarity_score"] = 1.5
        else:
            by_id["T-2"]["similarity_score"] = True

    write_part(h, "B001", mutate=break_it)
    assert pending_ids(needs(h.reconcile(), 3, "reconcile --stage trees, an item that breaks Rule 3's readings").json) == ["B001"]


def test_a_baseline_outside_the_working_directory_is_not_used_so_every_tree_is_generated(stage, cli, tmp_path, monkeypatch):
    """R-6 resolves a baseline below the working directory. One outside it warns, and the plan generates every tree, as the scorer's plan scores every finding."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    h = RunDir(stage, cli, tmp_path, "trees")
    threats = h.out / "threats.md"
    threats.write_text(joined_md([finding("S-1", "UNCHANGED", "Critical")], baseline_source="x/threats.md"), encoding="utf-8")
    (tmp_path / "baseline" / "attack-trees").mkdir(parents=True)
    (tmp_path / "baseline" / "attack-trees" / "s-1-attack-tree.md").write_text(tree_text("S-1"), encoding="utf-8")
    res = needs(h.plan_cli("--threats", threats, "--baseline-dir", tmp_path / "baseline"), 0, "plan --stage trees, a baseline outside the working directory")
    assert "outside-working-directory" in res.err
    plan = h.plan_json()
    assert plan["params"]["rule_applied"] == "no-baseline" and plan["refs"] == {}
    assert [unit["action"] for unit in tree_units(h)[0].values()] == ["generated_fresh"]


def test_the_baseline_is_found_through_baseline_source_when_no_flag_names_one(stage, cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    h = RunDir(stage, cli, tmp_path, "trees")
    earlier = tmp_path / "reports" / "earlier"
    (earlier / "attack-trees").mkdir(parents=True)
    (earlier / "threats.md").write_text("# an earlier threats.md\n", encoding="utf-8")
    (earlier / "attack-trees" / "s-1-attack-tree.md").write_text(tree_text("S-1"), encoding="utf-8")
    threats = h.out / "threats.md"
    threats.write_text(joined_md([finding("S-1", "UNCHANGED", "Critical")], baseline_source="reports/earlier/threats.md"), encoding="utf-8")
    needs(h.plan_cli("--threats", threats), 0, "plan --stage trees, a baseline from baseline.source")
    plan = h.plan_json()
    assert plan["params"]["rule_applied"] == "Rule 1" and plan["batches"] == [] and Path(plan["refs"]["baseline_dir"]).resolve() == earlier.resolve()


def test_a_baseline_tree_that_is_a_link_or_has_another_name_is_no_tree(stage, cli, tmp_path, monkeypatch):
    """A tree counts when it is the file that ``assemble-report.py trees`` would copy: the canonical ID in lower case, a regular file, no link on the way."""
    monkeypatch.chdir(tmp_path)
    h = RunDir(stage, cli, tmp_path, "trees")
    trees = tmp_path / "baseline" / "attack-trees"
    trees.mkdir(parents=True)
    (tmp_path / "real.md").write_text(tree_text("S-1"), encoding="utf-8")
    (trees / "s-1-attack-tree.md").symlink_to(tmp_path / "real.md")
    (trees / "agp-01-attack-tree.md").write_text(tree_text("AGP-1"), encoding="utf-8")  # AGP-1's file is agp-1-attack-tree.md
    (trees / "notes.md").write_text("not a tree\n", encoding="utf-8")
    threats = h.out / "threats.md"
    threats.write_text(joined_md([finding("S-1", "UNCHANGED", "Critical"), finding("AGP-1", "UNCHANGED", "High")], baseline_source="x/threats.md"), encoding="utf-8")
    needs(h.plan_cli("--threats", threats, "--baseline-dir", tmp_path / "baseline"), 0, "plan --stage trees, a baseline with no usable tree")
    assert h.plan_json()["params"]["rule_applied"] == "no-baseline" and sorted(tree_units(h)[0]) == ["AGP-1", "S-1"]


def test_a_missing_tree_outranks_a_tree_that_fails_a_check_so_the_batch_is_halved(stage, cli, tmp_path):
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High")])
    write_part(h, "B001", files=False)
    Path(h.batch_input("B001")["tree_paths"]["S-1"]).write_text("# no diagram here\n", encoding="utf-8")  # S-1's tree fails a check, and T-2's was never written
    assert pending_ids(needs(h.reconcile(), 3, "reconcile --stage trees, one tree missing and one that fails").json) == ["B001-1", "B001-2"]


def test_a_tree_that_is_a_link_is_refused_and_the_batch_is_retried_as_it_is(stage, cli, tmp_path):
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical")])
    write_part(h, "B001", files=False)
    (tmp_path / "elsewhere.md").write_text(tree_text("S-1"), encoding="utf-8")
    Path(h.batch_input("B001")["tree_paths"]["S-1"]).symlink_to(tmp_path / "elsewhere.md")
    assert pending_ids(needs(h.reconcile(), 3, "reconcile --stage trees, a linked tree").json) == ["B001"] and h.plan_json()["batches"][0]["attempt"] == 2


def test_a_batch_input_whose_tree_path_is_not_the_plans_is_exit_2(stage, cli, tmp_path):
    """The path is built from ``--out``, the plan ID and the ID, and the batch input's own entry must equal it (S1P-A44). Here the input and the plan are
    re-pinned, so only that check refuses."""
    h = trees_run(stage, cli, tmp_path, [finding("S-1", "NEW", "Critical")])
    write_part(h, "B001")
    path = h.plan_dir / "inputs" / "B001.json"
    body = json.loads(path.read_text(encoding="utf-8"))
    body["tree_paths"]["S-1"] = str(h.plan_dir / "trees" / "another-attack-tree.md")
    path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    plan = json.loads((h.plan_dir / "plan.json").read_text(encoding="utf-8"))
    plan["batches"][0]["input_sha256"] = sha256_of(path)
    (h.plan_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    h.digest = sha256_of(h.plan_dir / "plan.json")
    refused(h.reconcile(), "TREES", "reconcile --stage trees over a tree path that is not the plan's")


def test_each_pr2_plan_records_its_closed_params_and_no_pre_image_for_a_batch_stage(stage, cli, tmp_path):
    """S1P-A57 (R8): ``threat-model`` and ``threats-md`` hold ``{scoring_date}``, ``trees`` adds the rule and the reference digest, and ``report`` the digest
    and the trees plan's ID. A batch stage owns no canonical file, so its plan copies none."""
    run = RunDir(stage, cli, tmp_path / "run-level")
    needs(run.plan_cli(), 0, "the run-level plan")
    assert run.plan_json()["params"] == {"scoring_date": DATE} and set(run.plan_json()["preimage"]) == set(TM_OUTPUTS)
    md = threats_md_run(stage, cli, tmp_path / "md")
    assert md.plan_json()["params"] == {"scoring_date": DATE} and md.plan_json()["preimage"] == {}
    ht = trees_run(stage, cli, tmp_path / "trees", [finding("S-1", "NEW", "Critical")])
    assert set(ht.plan_json()["params"]) == {"scoring_date", "rule_applied", "reference_digest"} and ht.plan_json()["preimage"] == {}
    hr, trees = planned_report(stage, cli, tmp_path / "report", THREE_FINDINGS)
    assert hr.plan_json()["params"] == {"scoring_date": DATE, "reference_digest": trees.plan_json()["params"]["reference_digest"], "trees_plan_id": trees.plan_id}
    assert hr.plan_json()["preimage"] == {}


# ---- the report stage: its chain file (R9), its trees plan and what a unit holds


def test_the_report_plan_refuses_a_threats_md_that_the_trees_plan_was_not_made_from(stage, cli, tmp_path):
    """Both plans record the reference set's digest and ``report`` compares them at Step 2.9, so a plan over other findings is refused at the start."""
    hr, ht = report_ready(stage, cli, tmp_path, THREE_FINDINGS)
    other = hr.out / "other-threats.md"
    other.write_text(joined_md([finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High")]), encoding="utf-8")
    args = list(hr.args)
    args[1] = other
    res = refused(hr.plan_cli(*args), "REPORT", "plan --stage report over another threats.md")
    assert "Kept for diagnosis: %s" % ht.plan_dir in res.err and not (hr.build / "current.json").exists()


@pytest.mark.parametrize("fault", ["no-file", "a-link", "no-surfaced-chain", "not-utf-8"])
def test_a_chains_written_record_with_a_chain_file_that_cannot_be_used_plans_no_attack_chains_part(stage, cli, tmp_path, fault):
    """R9 (S1P-A58): when the file is missing or unreadable or holds no surfaced chain, the planner plans no ``attack_chains`` part, records no file, says so on
    stderr and exits 0. Step 2.8's check then rewrites the record (D13) and the run goes on (R-24)."""
    hr, ht = report_ready(stage, cli, tmp_path, THREE_FINDINGS, outcome=CHAINS_OUTCOME, attack_chains=(fault != "no-file"))
    chains = hr.out / "attack-chains.md"
    if fault == "a-link":
        (tmp_path / "elsewhere.md").write_text(ATTACK_CHAINS_MD, encoding="utf-8")
        chains.unlink()
        chains.symlink_to(tmp_path / "elsewhere.md")
    elif fault == "no-surfaced-chain":
        chains.write_text(ATTACK_CHAINS_MD.replace("**Surfaced**: Yes", "**Surfaced**: No"), encoding="utf-8")
    elif fault == "not-utf-8":
        chains.write_bytes(b"\xff\xfe not utf-8")
    res = needs(hr.plan_cli(*hr.args), 0, "plan --stage report over a chain file that can't be used (%s)" % fault)
    assert "attack-chains.md can't be used" in res.err
    sections, _ = report_batches(hr)
    assert sections == BASE_SECTIONS and not [value for value in hr.plan_json()["inputs"].values() if Path(value["path"]).name == "attack-chains.md"]


def test_a_report_unit_holds_the_rows_that_its_key_is_about(stage, cli, tmp_path):
    """What each unit holds (``_report_parts``), so that no report agent reads threats.md: the counts, the Critical and High rows, the tables of Sections 1, 2
    and 4a, a finding's Section 7 row with its category-table row, a group's members and Section 4c's rows."""
    items = [finding("S-1", "NEW", "Critical"), finding("T-2", "NEW", "High"), finding("T-3", "NEW", "High"), finding("LLM-4", "NEW", "Medium", "trust_exploitation")]
    hr, _ = planned_report(stage, cli, tmp_path, items, baseline=True, resolved=["D-9"], groups=[("CG-1", ["T-2", "T-3"])])
    _, inputs = report_batches(hr)
    keyed = {unit["key"]: unit for bi in inputs for unit in bi["units"] if "key" in unit}
    found = {(unit["section"], unit["finding_id"]): unit for bi in inputs for unit in bi["units"] if "finding_id" in unit}
    counts = {"open": 4, "resolved": 1, "new": 4, "unchanged": 0, "updated": 0, "critical": 1, "high": 2, "medium": 1, "low": 0, "note": 0}
    assert keyed["risk_posture"]["counts"] == counts and "rows" not in keyed["risk_posture"]
    assert [row["finding_id"] for row in keyed["top_threats"]["rows"]] == [row["finding_id"] for row in keyed["key_recommendations"]["rows"]] == ["S-1", "T-2", "T-3"]
    assert keyed["system_context"]["components"][0]["component"] == "Gateway" and keyed["system_context"]["data_flows"][0]["protocol"] == "HTTPS"
    assert keyed["trust_boundaries"]["trust_zones"][0]["zone"] == "Edge" and keyed["trust_boundaries"]["boundary_crossings"] == []
    assert keyed["category.tampering"]["narrated"] == ["T-2", "T-3"] and keyed["category.tampering"]["summarized"] == []
    assert sorted(keyed["overview"]["categories"]) == ["llm", "spoofing", "tampering"]
    assert keyed["themes"]["groups"][0]["group"] == "CG-1" and keyed["themes"]["groups"][0]["findings"] == "T-2, T-3"
    lead = found[("threat_analysis", "S-1")]
    assert lead["tree"] is True and lead["category_row"]["likelihood"] == "Medium" and lead["category_row"]["impact"] == "High"
    assert lead["category_row"]["maestro_layer"].startswith("L4") and lead["component"] == "Gateway" and lead["risk_level"] == "Critical"
    assert found[("threat_analysis", "LLM-4")]["tree"] is False and found[("threat_analysis", "LLM-4")]["category_row"]["owasp_reference"] == "LLM01:2026"
    primary = found[("remediation_roadmap", "T-2")]
    assert primary["group_id"] == "CG-1" and [row["finding_id"] for row in primary["members"]] == ["T-2", "T-3"]
    assert ("remediation_roadmap", "T-3") not in found and "group_id" not in found[("remediation_roadmap", "S-1")]
    assert [row["finding_id"] for row in keyed["pattern.trust_exploitation"]["rows"]] == ["LLM-4"]
    assert keyed["progress"]["lifecycle"] == {"new": 4, "unchanged": 0, "updated": 0, "resolved": 1} and keyed["progress"]["baseline"]["source"] == "reports/earlier/threats.md"
    assert keyed["progress"]["resolved"] == [{"finding_id": "D-9", "component": "Legacy 1", "threat": "Old threat D-9", "last_risk_level": "High",
                                              "resolution_reason": "Component removed"}]


# ---- the edges: what the plans refuse before they write, and what a record still gets when a file has gone


def test_a_pr2_plan_refuses_more_batches_than_a_batch_id_can_name_before_it_writes(stage, cli, tmp_path):
    h = RunDir(stage, cli, tmp_path, "threats-md")
    write_sections(h, sections_manifest(open_ids=["S-1"], rows=dict(ROWS_ZERO, components=1000)))
    with pytest.raises(stage.StageError) as info:
        stage.plan_stage(stage="threats-md", out=h.out, date=DATE, batch_size=1)  # 1,002 batches, and a batch ID is B and three digits
    assert info.value.code == 2 and "999" in str(info.value) and not (h.build / "current.json").exists() and not h.build.exists()


@pytest.mark.parametrize("name", ["trees", "report"])
def test_a_plan_that_reads_a_threats_md_needs_the_pointer_that_names_it(stage, cli, tmp_path, name):
    refused(RunDir(stage, cli, tmp_path, name).plan_cli(), name.upper(), "plan --stage %s with no --threats" % name)


def test_the_report_plan_needs_its_trees_plan_and_checks_the_two_arguments_that_name_it(stage, cli, tmp_path):
    hr, ht = report_ready(stage, cli, tmp_path, THREE_FINDINGS)
    threats = ["--threats", hr.threats]
    for extra, why in (([], "no trees plan"), (["--trees-plan", ht.plan_id], "no digest"), (["--trees-plan-digest", ht.digest], "no plan ID"),
                       (["--trees-plan", "../escape", "--trees-plan-digest", ht.digest], "a plan ID off the allow-list"),
                       (["--trees-plan", ht.plan_id, "--trees-plan-digest", ht.digest.upper()], "a digest in upper case")):
        refused(hr.plan_cli(*threats, *extra), "REPORT", "plan --stage report with %s" % why)
    assert not (hr.build / "current.json").exists()


def test_a_finding_with_several_patterns_gets_the_multi_unit_after_the_six_patterns(stage, cli, tmp_path):
    hr, _ = planned_report(stage, cli, tmp_path, [finding("AG-1", "NEW", "High", "multiple"), finding("AG-2", "NEW", "High", "agent_collusion")])
    _, inputs = report_batches(hr)
    assert [unit["key"] for bi in inputs if bi["units"][0]["section"] == "agentic_patterns" for unit in bi["units"]] == ["pattern.agent_collusion", "multi"]


def test_a_message_still_names_a_batch_whose_input_can_no_longer_be_read(stage, cli, tmp_path):
    h = threats_md_run(stage, cli, tmp_path, sections_manifest(open_ids=["T-1"], rows=dict(ROWS_ZERO, components=2)))
    write_valid_parts(h, skip=["B001"])
    for _ in range(2):
        needs(h.reconcile(), 3, "reconcile --stage threats-md, a part that never comes")
    needs(h.reconcile(), 4, "reconcile --stage threats-md, the attempts exhausted")
    (h.plan_dir / "inputs" / "B001-1.json").unlink()
    res = needs(h.fail("unrecoverable-batch"), 0, "fail --stage threats-md, a batch whose input is gone")
    assert "Batch B001-1:" in res.err


@pytest.mark.parametrize("name", BATCH_STAGES)
def test_fail_leaves_out_a_done_batch_whose_input_can_no_longer_be_read(stage, cli, tmp_path, name):
    h = planned_stage(stage, cli, tmp_path, name)
    write_valid_parts(h)
    needs(h.reconcile(), 0, "reconcile --stage %s" % name)
    (h.plan_dir / "inputs" / ("%s.json" % h.plan_json()["batches"][0]["batch_id"])).unlink()
    needs(h.fail("check-failed"), 0, "fail --stage %s over a batch whose input is gone" % name)
    assert h.record()["batches"]["done"] == len(h.plan_json()["batches"])


def test_a_pre_image_that_cannot_be_written_back_is_refused_and_not_a_crash(stage, cli, tmp_path, monkeypatch):
    h = RunDir(stage, cli, tmp_path)
    h.earlier()
    needs(h.plan_cli(), 0, "the run-level plan")
    h.run_wrote(("threats.md",))
    real = stage.tp.atomic_write

    def failing(path, data, mode_of=None):
        if os.path.basename(str(path)) == "threats.md":
            raise OSError(13, "Permission denied")
        return real(path, data, mode_of=mode_of)

    monkeypatch.setattr(stage.tp, "atomic_write", failing)
    res = h.fail("render-failed")
    assert res.code == 2 and res.json["moved"] == ["threats.md"] and res.json["restored"] == [], res.describe()
    assert any(w["code"] == "move-refused" and "could not be put back" in w["detail"] for w in h.record()["warnings"])


def test_a_hand_off_file_that_is_the_other_checks_is_refused_by_close_and_noted_by_fail(stage, cli, tmp_path):
    """A file that is valid, but for the other check, is no hand-off of this one: ``check`` must be its file's name (part-files.md section 6)."""
    h = closeable(stage, cli, tmp_path)
    h.write_handoff("provenance", raw=json.dumps(handoff("attack-chains", h.plan_id)).encode("utf-8"))
    refused(h.close(), "THREAT-MODEL", "close over a provenance.json that is the chain check's")
    needs(h.fail("check-failed"), 0, "fail --stage threat-model over a provenance.json that is the chain check's")
    warnings = h.record()["warnings"]
    assert [w["code"] for w in warnings] == ["handoff-invalid:provenance"] and "attack-chains" in warnings[0]["detail"]


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="a mode of 0 stops no read by root")
def test_close_refuses_a_canonical_file_that_it_cannot_read(stage, cli, tmp_path):
    h = closeable(stage, cli, tmp_path)
    os.chmod(str(h.out / "threats.md"), 0)
    try:
        refused(h.close(), "THREAT-MODEL", "close over an output that can't be read")
        assert_not_closed(h)
    finally:
        os.chmod(str(h.out / "threats.md"), 0o644)


def test_id_mark_that_cannot_write_its_file_is_exit_1(stage, cli, marked, monkeypatch):
    write_run(marked, "threats.md", ["S-3"])

    def failing(path, data, mode_of=None):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(stage.tp, "atomic_write", failing)
    refused(id_mark(cli, None), "THREAT-MODEL", "id-mark that can't write", code=1)


def test_a_baseline_mark_line_without_backticks_reads_as_absent(stage, cli, marked):
    threats = write_run(marked, "threats.md", ["S-3"])
    write_run(marked, "baseline.md", ["S-3"], ["S-9"], preamble="**ID high-water mark**: S-50")
    res = needs(id_mark(cli), 0, "id-mark over a baseline whose mark line has no backticks")
    assert real_marks(threats.read_text(encoding="utf-8")) == ["S-9"] and res.json["floor"] == "seed"


def test_a_baseline_with_windows_line_endings_reads_its_mark_line(stage, cli, marked):
    threats = write_run(marked, "threats.md", ["S-3"])
    baseline = write_run(marked, "baseline.md", ["S-3"], mark="S-14, T-22")
    baseline.write_bytes(baseline.read_bytes().replace(b"\n", b"\r\n"))
    res = needs(id_mark(cli), 0, "id-mark over a baseline with CRLF line ends")
    assert real_marks(threats.read_text(encoding="utf-8")) == ["S-14, T-22"] and res.json["floor"] == "mark"


# ---------------------------------------------------------------------------- watch: Phase 2's bound (T156; ADR-050 D6, S1P-PM9; threat-model-records.md, "The watch")
#
# ``watch --out DIR DSP [DSP ...]`` waits until each named dispatch has its record, and exits 3 with the IDs that have none if the deadline passes first.
# It writes nothing. The orchestrator writes each timed-out dispatch's ``timed_out`` record from that exit, so no case here needs a record that validates
# under that status, and none waits on T091b. The cases run in-process (H15) with ``time.monotonic`` and ``time.sleep`` replaced by a clock that only
# counts, so none of them sleeps. A smaller deadline reaches the script only through the function interface (D6). A record here is a stand-in: the
# watch looks at a file's kind and never at its content.

WATCH_BANNER = "THREAT-MODEL"


class WatchClock(object):
    """``time.monotonic`` and ``time.sleep`` for a watch that must not wait: a sleep moves the clock on and does nothing else.

    ``after(n, action)`` runs ``action`` when the n-th sleep ends, so that a record can appear during the wait. A loop that sleeps more than ``RUNAWAY``
    times is not following its deadline and fails here, so a regression ends its case and never hangs the run.
    """

    RUNAWAY = 3000

    def __init__(self, start=1000.0):
        self.start, self.now, self.sleeps, self.actions = start, start, [], {}

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        assert seconds >= 0, "T156, a sleep of %r seconds" % (seconds,)
        self.sleeps.append(seconds)
        assert len(self.sleeps) <= self.RUNAWAY, "T156, the watch kept sleeping past any deadline (%d sleeps)" % len(self.sleeps)
        self.now += seconds
        for action in self.actions.get(len(self.sleeps), ()):
            action()

    def after(self, count, action):
        self.actions.setdefault(count, []).append(action)

    @property
    def elapsed(self):
        return self.now - self.start


@pytest.fixture
def clock(monkeypatch):
    fake = WatchClock()
    monkeypatch.setattr(time, "monotonic", fake.monotonic)
    monkeypatch.setattr(time, "sleep", fake.sleep)
    return fake


def watch_out(root):
    out = Path(root) / "run"
    out.mkdir()
    return out


def watch_record(out, dispatch_id, content=b"{}\n"):
    """A dispatch's record, where the orchestrator leaves it. Its content is a stand-in: the watch never reads it."""
    path = Path(out) / ".tachi-build" / "records" / (dispatch_id + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def watch_ids(count, first=1):
    return ["dsp-%03d" % number for number in range(first, first + count)]


def watch_said(res, code, status, pending, behavior):
    """An exit 0 or an exit 3: the code, one JSON object with its two keys on stdout, and nothing on stderr."""
    assert res.code == code and res.err == "", "T156, %s: expected exit %d with nothing on stderr\n%s" % (behavior, code, res.describe())
    assert res.json == {"status": status, "pending": pending}, "T156, %s\n%s" % (behavior, res.describe())
    return res


def watch_refused(res, behavior, code=2):
    """A refusal is D4's four-line message with its code, never an argparse usage error: ``TACHI THREAT-MODEL FAILED``, a reason and a ``Remedy:`` line,
    and nothing on stdout."""
    assert res.code == code and res.out == "" and re.search(r"^TACHI %s FAILED: " % WATCH_BANNER, res.err, re.M) and "Remedy: " in res.err, (
        "T156, %s: expected a refusal (exit %d, D4's message with its Remedy, nothing on stdout)\n%s" % (behavior, code, res.describe()))
    return res


def watch_tree_state(root):
    """Every path under ``root`` with its kind, size, modification time and bytes: what a command that writes nothing leaves as it found it."""
    state = {}
    for base, dirs, files in os.walk(str(root)):
        for name in sorted(dirs + files):
            path = os.path.join(base, name)
            kind = "link" if os.path.islink(path) else "dir" if os.path.isdir(path) else "file"
            state[os.path.relpath(path, str(root))] = (kind, os.lstat(path).st_mtime_ns, Path(path).read_bytes() if kind == "file" else None)
    return state


# ---- what it waits for

def test_watch_exits_0_at_once_when_every_record_is_already_there(stage, cli, clock, tmp_path):
    """The first look comes before the first sleep, so a wave that is already recorded costs nothing (S1P-A38, item 5)."""
    out = watch_out(tmp_path)
    ids = watch_ids(4)
    for dsp in ids:
        watch_record(out, dsp)
    watch_said(cli("watch", "--out", out, *ids), 0, "done", [], "every record there at the start")
    assert clock.sleeps == [] and clock.elapsed == 0


def test_watch_exits_0_as_soon_as_the_last_record_appears_during_the_wait(stage, cli, clock, tmp_path):
    """It looks every 5 seconds, and it ends when the last record is there, not at the deadline."""
    out = watch_out(tmp_path)
    ids = watch_ids(3)
    watch_record(out, ids[0])
    clock.after(1, lambda: watch_record(out, ids[2]))
    clock.after(3, lambda: watch_record(out, ids[1]))
    watch_said(cli("watch", "--out", out, *ids), 0, "done", [], "the last record appears during the third wait")
    assert clock.sleeps == [5, 5, 5] and clock.elapsed == 15


def test_watch_keeps_waiting_while_any_one_record_is_missing(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    ids = watch_ids(3)
    for dsp in ids[:2]:
        watch_record(out, dsp)
    clock.after(7, lambda: watch_record(out, ids[2]))
    watch_said(cli("watch", "--out", out, *ids), 0, "done", [], "two of three there, the third after seven waits")
    assert len(clock.sleeps) == 7 and clock.elapsed == 35


def test_watch_exits_3_at_the_deadline_and_names_the_dispatches_with_no_record_in_argument_order(stage, cli, clock, tmp_path):
    """The deadline is the constant, 5,400 seconds from the watch's start, and the poll is 5. ``pending`` follows the arguments, not the sort order."""
    out = watch_out(tmp_path)
    watch_record(out, "dsp-002")
    watch_said(cli("watch", "--out", out, "dsp-004", "dsp-002", "dsp-010", "dsp-003"), 3, "timed-out", ["dsp-004", "dsp-010", "dsp-003"],
               "a deadline with one record of four")
    assert clock.elapsed == 5400 and len(clock.sleeps) == 1080 and set(clock.sleeps) == {5}


def test_watch_exits_3_naming_every_dispatch_when_none_has_a_record(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    ids = ["dsp-016", "dsp-001", "dsp-009"]
    watch_said(cli("watch", "--out", out, *ids), 3, "timed-out", ids, "no record at all")
    assert not (out / ".tachi-build").exists()


def test_a_record_that_arrives_during_the_wait_leaves_the_pending_list(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    watch_record(out, "dsp-001")
    clock.after(2, lambda: watch_record(out, "dsp-003"))
    watch_said(cli("watch", "--out", out, "dsp-003", "dsp-001", "dsp-002"), 3, "timed-out", ["dsp-002"], "dsp-003 recorded during the wait, dsp-002 never")
    assert clock.elapsed == 5400


@pytest.mark.parametrize("start", [0.0, 1000.0, 86400.5])
def test_the_deadline_runs_from_the_watchs_own_start_on_the_monotonic_clock(stage, cli, clock, tmp_path, start):
    clock.start = clock.now = start
    out = watch_out(tmp_path)
    watch_said(cli("watch", "--out", out, "dsp-001"), 3, "timed-out", ["dsp-001"], "a clock that starts at %r" % start)
    assert clock.elapsed == 5400


def test_the_deadline_and_the_poll_are_the_documented_constants(stage):
    assert stage.WATCH_SECONDS == 5400 and stage.WATCH_POLL_SECONDS == 5


# ---- the function interface: the one way a smaller deadline gets in (D6)

def test_watch_function_takes_the_deadline_and_the_poll_and_its_last_sleep_ends_at_the_deadline(stage, clock, tmp_path):
    out = watch_out(tmp_path)
    assert stage.watch(out, ["dsp-001", "dsp-002"], seconds=12, poll=5) == (3, {"status": "timed-out", "pending": ["dsp-001", "dsp-002"]})
    assert clock.sleeps == [5, 5, 2] and clock.elapsed == 12  # cut to what is left, so it ends at the deadline and not a poll after


def test_a_record_that_arrives_during_the_last_sleep_still_counts(stage, clock, tmp_path):
    out = watch_out(tmp_path)
    clock.after(3, lambda: watch_record(out, "dsp-001"))
    assert stage.watch(out, ["dsp-001"], seconds=12, poll=5) == (0, {"status": "done", "pending": []})
    assert clock.elapsed == 12


def test_a_deadline_of_zero_looks_once_and_never_sleeps(stage, clock, tmp_path):
    out = watch_out(tmp_path)
    assert stage.watch(out, ["dsp-001"], seconds=0) == (3, {"status": "timed-out", "pending": ["dsp-001"]})
    watch_record(out, "dsp-001")
    assert stage.watch(out, ["dsp-001"], seconds=0) == (0, {"status": "done", "pending": []})
    assert clock.sleeps == []


def test_watch_works_on_the_real_clock(stage, tmp_path):
    """The cases above replace the clock. This one doesn't: a record that another thread writes during the wait ends it, and a deadline that passes
    first ends it with exit 3. The bounds are loose, so a loaded machine can't fail them, but a loop that ignores its poll or its deadline can."""
    out = watch_out(tmp_path)
    started = time.monotonic()
    writer = threading.Timer(0.15, watch_record, args=(out, "dsp-001"))
    writer.start()
    try:
        assert stage.watch(out, ["dsp-001"], seconds=60, poll=0.05) == (0, {"status": "done", "pending": []})
    finally:
        writer.join()
    assert 0.1 <= time.monotonic() - started < 30
    started = time.monotonic()
    assert stage.watch(out, ["dsp-001", "dsp-002"], seconds=0.3, poll=0.05) == (3, {"status": "timed-out", "pending": ["dsp-002"]})
    assert 0.3 <= time.monotonic() - started < 30


# ---- a record counts by its kind and its place, never by its content

def _plant_link_to_a_file(out, root):
    path = watch_record(out, "dsp-001")
    path.unlink()
    elsewhere = Path(root) / "elsewhere.json"
    elsewhere.write_bytes(b"{}\n")
    os.symlink(str(elsewhere), str(path))


def _plant_dangling_link(out, root):
    path = watch_record(out, "dsp-001")
    path.unlink()
    os.symlink(str(Path(root) / "nowhere.json"), str(path))


def _plant_directory(out, root):
    path = watch_record(out, "dsp-001")
    path.unlink()
    path.mkdir()


def _plant_linked_records_directory(out, root):
    elsewhere = Path(root) / "other-records"
    elsewhere.mkdir()
    (elsewhere / "dsp-001.json").write_bytes(b"{}\n")
    (Path(out) / ".tachi-build").mkdir()
    os.symlink(str(elsewhere), str(Path(out) / ".tachi-build" / "records"))


def _plant_linked_build_directory(out, root):
    elsewhere = Path(root) / "other-build"
    (elsewhere / "records").mkdir(parents=True)
    (elsewhere / "records" / "dsp-001.json").write_bytes(b"{}\n")
    os.symlink(str(elsewhere), str(Path(out) / ".tachi-build"))


NOT_A_RECORD = {
    "a link to a regular file": _plant_link_to_a_file,
    "a dangling link": _plant_dangling_link,
    "a directory": _plant_directory,
    "a link in the place of records/": _plant_linked_records_directory,
    "a link in the place of .tachi-build/": _plant_linked_build_directory,
}


@pytest.mark.parametrize("kind", sorted(NOT_A_RECORD))
def test_a_record_counts_only_as_a_regular_file_with_no_link_in_its_path(stage, cli, clock, tmp_path, kind):
    out = watch_out(tmp_path)
    NOT_A_RECORD[kind](out, tmp_path)
    watch_said(cli("watch", "--out", out, "dsp-001"), 3, "timed-out", ["dsp-001"], "a record that is %s" % kind)


@pytest.mark.parametrize("content", [b"", b"not json at all", b"\xff\xfe\x00", b"{}\n"], ids=["empty", "text", "bytes", "object"])
def test_a_record_counts_by_its_kind_and_never_by_its_content(stage, cli, clock, tmp_path, content):
    """Reading a record is the check's job at Step 2.8. The watch only has to know that the orchestrator has written one."""
    out = watch_out(tmp_path)
    watch_record(out, "dsp-001", content)
    watch_said(cli("watch", "--out", out, "dsp-001"), 0, "done", [], "a record holding %r" % content)


def test_a_record_of_another_dispatch_counts_for_nothing(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    watch_record(out, "dsp-002")
    (out / ".tachi-build" / "records" / "dsp-001.json.partial").write_bytes(b"{}\n")
    (out / ".tachi-build" / "briefs").mkdir()
    (out / ".tachi-build" / "briefs" / "dsp-001.json").write_bytes(b"{}\n")  # the brief is not the record
    watch_said(cli("watch", "--out", out, "dsp-001"), 3, "timed-out", ["dsp-001"], "a brief, a partial file and another dispatch's record")


def test_watch_takes_an_out_that_is_itself_a_link(stage, cli, clock, tmp_path):
    """The guard walks down from ``--out``, so a link in ``--out`` itself is fine: only what lies below it may not be one."""
    real = tmp_path / "real-run"
    real.mkdir()
    watch_record(real, "dsp-001")
    os.symlink(str(real), str(tmp_path / "run-link"))
    watch_said(cli("watch", "--out", tmp_path / "run-link", "dsp-001"), 0, "done", [], "--out a link to the run directory")


# ---- it writes nothing

@pytest.mark.parametrize("deadline", [False, True], ids=["exit-0", "exit-3"])
def test_watch_writes_nothing_and_least_of_all_a_timed_out_record(stage, cli, clock, tmp_path, deadline):
    """It exits 3 and names the dispatches. The orchestrator writes each one's ``timed_out`` record (ADR-050 D6), and the watch writes no record, no
    stage record and no directory, so a dispatch that timed out has the one record the orchestrator wrote and no other."""
    out = watch_out(tmp_path)
    ids = watch_ids(3)
    recorded = ids[:1] if deadline else ids
    for dsp in recorded:
        watch_record(out, dsp)
    (out / "threats.md").write_bytes(b"# a threat model\n")
    before = watch_tree_state(tmp_path)
    assert cli("watch", "--out", out, *ids).code == (3 if deadline else 0)
    assert watch_tree_state(tmp_path) == before
    assert not (out / ".tachi-build" / THREAT_MODEL).exists()
    assert sorted(path.name for path in (out / ".tachi-build" / "records").iterdir()) == [dsp + ".json" for dsp in recorded]


# ---- what it refuses, before it waits

BAD_DISPATCH_IDS = [
    "dsp-1", "dsp-12", "dsp-12345", "DSP-001", "dsp-00a", "dsp-001.json", "dsp_001", "dsp-001 ", " dsp-001", "dsp-001\n", "dsp-0 01", "dsp--01", "dsp-+01",
    "dsp-", "B001", "", "../dsp-001", "dsp-001/..", "/dsp-001", "dsp-\uff10\uff10\uff11",
]


@pytest.mark.parametrize("bad", BAD_DISPATCH_IDS, ids=repr)
def test_watch_refuses_an_id_that_is_not_a_dispatch_id_before_it_waits(stage, cli, clock, tmp_path, bad):
    """Each ID fully matches ``tachi_parts``' dispatch pattern, as an ASCII full match, before it becomes part of a path."""
    out = watch_out(tmp_path)
    watch_record(out, "dsp-001")
    before = watch_tree_state(tmp_path)
    watch_refused(cli("watch", "--out", out, "dsp-001", bad), "the argument %r" % bad)
    assert clock.sleeps == [] and watch_tree_state(tmp_path) == before


def test_a_refusal_never_prints_a_control_character_from_an_id(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    res = watch_refused(cli("watch", "--out", out, "dsp-001\x1b[31m\r"), "an ID with an escape sequence")
    assert "\x1b" not in res.err and "\r" not in res.err


def test_watch_refuses_an_id_named_twice(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    for dsp in watch_ids(2):
        watch_record(out, dsp)
    res = watch_refused(cli("watch", "--out", out, "dsp-001", "dsp-002", "dsp-001"), "a repeated ID")
    assert "dsp-001" in res.err and clock.sleeps == []


@pytest.mark.parametrize("count", [0, 17, 40])
def test_watch_refuses_no_id_and_more_than_one_wave_of_16(stage, cli, clock, tmp_path, count):
    """A wave holds at most 16 dispatches in flight (S-8). Even with a record for each, 17 is refused."""
    out = watch_out(tmp_path)
    ids = watch_ids(count)
    for dsp in ids:
        watch_record(out, dsp)
    watch_refused(cli("watch", "--out", out, *ids), "%d IDs" % count)
    assert clock.sleeps == []


@pytest.mark.parametrize("count", [1, 16])
def test_watch_takes_from_one_to_16_ids(stage, cli, clock, tmp_path, count):
    out = watch_out(tmp_path)
    ids = watch_ids(count, first=100)
    for dsp in ids:
        watch_record(out, dsp)
    watch_said(cli("watch", "--out", out, *ids), 0, "done", [], "%d IDs, all recorded" % count)


def test_watch_takes_the_four_digit_ids_of_a_long_run(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    ids = ["dsp-999", "dsp-1000", "dsp-9999"]
    for dsp in ids:
        watch_record(out, dsp)
    watch_said(cli("watch", "--out", out, *ids), 0, "done", [], "3- and 4-digit IDs")


def test_watch_refuses_an_out_that_is_not_a_directory(stage, cli, clock, tmp_path):
    """``watch`` has no exit 1 (``cli.md``: 0, 2 and 3), so a missing directory is exit 2, as for ``fail``. Nothing is created, and it never waits."""
    missing = tmp_path / "nothing"
    watch_refused(cli("watch", "--out", missing, "dsp-001"), "a missing --out")
    assert not missing.exists()
    a_file = tmp_path / "a-file"
    a_file.write_bytes(b"x")
    res = watch_refused(cli("watch", "--out", a_file, "dsp-001"), "--out a file")
    assert "--out" in res.err and clock.sleeps == []


def test_watch_refuses_an_out_whose_path_a_document_cannot_carry(stage, cli, clock, tmp_path):
    """``--out`` is checked as the other subcommands check it, with D7's rule for the path first."""
    odd = tmp_path / "back`tick"
    odd.mkdir()
    watch_record(odd, "dsp-001")
    res = watch_refused(cli("watch", "--out", odd, "dsp-001"), "an --out with a backtick")
    assert "--out" in res.err and clock.sleeps == []


def test_watch_checks_out_before_it_checks_the_ids(stage, cli, clock, tmp_path):
    """The contract's order: ``--out`` first, then the IDs, so the first check that fails is the one reported."""
    res = watch_refused(cli("watch", "--out", tmp_path / "nothing", "dsp-1", "dsp-1"), "a missing --out with two bad IDs")
    assert "--out" in res.err and "dsp-1" not in res.err and clock.sleeps == []


def test_watch_needs_an_out(stage, cli, clock, tmp_path):
    out = watch_out(tmp_path)
    watch_record(out, "dsp-001")
    watch_said(cli("watch", "--out", out, "dsp-001"), 0, "done", [], "the command with its --out")  # the command is there, so the refusal below is the missing option's
    res = cli("watch", "dsp-001")
    assert res.code == 2 and res.out == "" and "required" in res.err and "--out" in res.err  # argparse's usage error
    assert clock.sleeps == []


# ---- the deadline is not a setting

@pytest.mark.parametrize("flag", [["--seconds", "1"], ["--deadline", "1"], ["--poll", "1"], ["--timeout", "1"]], ids=lambda flag: flag[0])
def test_the_deadline_is_not_a_command_line_setting(stage, cli, clock, tmp_path, flag):
    out = watch_out(tmp_path)
    watch_record(out, "dsp-001")
    watch_said(cli("watch", "--out", out, "dsp-001"), 0, "done", [], "the command without the flag")  # the command is there, so the refusal below is the flag's
    res = cli("watch", "--out", out, *flag, "dsp-001")
    assert res.code == 2 and res.out == "" and "unrecognized arguments" in res.err and clock.sleeps == []


@pytest.mark.parametrize("variable", ["WATCH_SECONDS", "WATCH_POLL_SECONDS", "TACHI_WATCH_SECONDS", "TACHI_WATCH_DEADLINE"])
def test_the_deadline_is_not_an_environment_setting(stage, cli, clock, tmp_path, monkeypatch, variable):
    monkeypatch.setenv(variable, "1")
    out = watch_out(tmp_path)
    watch_said(cli("watch", "--out", out, "dsp-001"), 3, "timed-out", ["dsp-001"], "%s set to 1" % variable)
    assert clock.elapsed == 5400 and set(clock.sleeps) == {5}


# ---- --help, and a real interpreter

def test_help_names_watch_and_its_arguments(stage, cli):
    top = cli("--help")
    assert top.code == 0 and "watch" in top.out
    text = cli("watch", "--help")
    assert text.code == 0 and "--out" in text.out and "DSP" in text.out
    assert "--seconds" not in text.out and "--deadline" not in text.out


def test_watch_exits_from_a_real_interpreter(tmp_path):
    """What a process alone shows (H15): the ``__main__`` guard turns ``main``'s result into the exit status, one JSON object reaches stdout, and a refusal
    reaches stderr alone. The deadline can't be shown this way: it is 90 minutes of a real clock, and ``test_watch_works_on_the_real_clock`` covers the loop."""
    out = watch_out(tmp_path)
    for dsp in watch_ids(2):
        watch_record(out, dsp)
    done = _run_script("watch", "--out", out, "dsp-001", "dsp-002")
    assert done.returncode == 0 and done.stderr == "", done.stderr
    assert json.loads(done.stdout) == {"status": "done", "pending": []}
    bad = _run_script("watch", "--out", out, "dsp-001", "dsp-1")
    assert bad.returncode == 2 and bad.stdout == "" and "TACHI THREAT-MODEL FAILED" in bad.stderr and "Remedy: " in bad.stderr
    absent = _run_script("watch", "--out", tmp_path / "nothing", "dsp-001")
    assert absent.returncode == 2 and absent.stdout == "" and "TACHI THREAT-MODEL FAILED" in absent.stderr
