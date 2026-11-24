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
    """``tachi_parts.STAGE_AGENTS`` holds PR 1's two stages, and PR 1 rejects every other (ruled at W1)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    with pytest.raises(stage.StageError) as info:
        stage.plan_stage(stage="trees", out=h.out, date=DATE, threats=h.threats)
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
