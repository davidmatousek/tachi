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
    "schema", "plan_id", "stage", "agent_type", "created_utc", "tachi_version", "inputs", "params",
    "batch_size", "unit_count", "preimage", "out_snapshot", "retry_budget", "batches",
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


def controls_item(finding_id):
    """One valid compensating-controls item for a missing control (``contracts/part-files.md`` §1)."""
    return {
        "finding_id": finding_id,
        "control_status": "missing",
        "control_category": "authentication",
        "confidence": None,
        "carried_forward": False,
        "evidence": [],
        "matrix_row": " | ".join("cell %d" % n for n in range(1, 12)),
        "recommendation_body": "Add the missing control at the trust boundary.",
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
        """The planner through its function interface: the one way a size gets in (ADR-050 D6)."""
        result = self.stage.plan_stage(
            stage=self.name, out=self.out, date=DATE, threats=self.threats, batch_size=batch_size, **optional
        )
        self.plan_id, self.digest = result["plan_id"], result["plan_digest"]
        return result

    def plan_cli(self, *extra):
        res = self.cli("plan", "--stage", self.name, "--out", self.out, "--date", DATE, "--threats", self.threats, *extra)
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
def test_plan_writes_the_layout_and_prints_the_contract_object(stage, cli, tmp_path, tachi_version, name):
    """D3's layout, ``contracts/part-files.md`` §3 and §4, and the object ``plan`` prints (cli.md)."""
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
        assert isinstance(bi["refs"], dict)
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
def test_every_batched_path_gets_two_or_more_balanced_contiguous_batches(stage, cli, tmp_path, name, size):
    """D3's batch granularity: contiguous runs of the units in S-2 order, balanced to within 1, each unit once."""
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
def test_batch_inputs_carry_each_units_row_verbatim(stage, cli, tmp_path, name):
    """Agents read their rows from the batch input, so no layer re-reads ``threats.md`` (D6)."""
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


def test_plan_records_the_optional_pointers_as_refs_and_the_risk_scores_file_as_an_input(stage, cli, tmp_path, monkeypatch):
    """``contracts/cli.md``'s optional flags reach each batch input as absolute ``refs``, and a file the stage reads is
    a digest-checked input, so a change during the run is caught (D6). The architecture goes through the shared
    resolver (T044), which takes a file below the working directory, so the project root is the working directory."""
    monkeypatch.chdir(tmp_path)
    h = Harness(stage, cli, tmp_path, "compensating-controls", ids=MIXED_IDS[:6])
    scores = h.out / "risk-scores.md"
    scores.write_text("# the scores\n", encoding="utf-8")
    baseline, target = tmp_path / "baseline", tmp_path / "target"
    baseline.mkdir()
    target.mkdir()
    architecture = tmp_path / "architecture.md"
    architecture.write_text("# architecture\n", encoding="utf-8")

    res = h.plan_cli("--risk-scores", scores, "--baseline-dir", baseline, "--architecture", architecture, "--target", target)
    assert res.code == 0, res.describe()
    assert h.batch_input("B001")["refs"] == {
        "threats": str(h.threats), "risk_scores": str(scores), "baseline_dir": str(baseline),
        "architecture": str(architecture), "target": str(target)}
    assert set(h.plan_json()["inputs"]) == {"threats", "risk_scores"}
    scores.write_text("# edited since plan\n", encoding="utf-8")
    assert h.reconcile().code == 2


@pytest.mark.parametrize("flag", ["--risk-scores", "--baseline-dir", "--target"])
def test_a_pointer_that_names_nothing_exits_1(stage, cli, tmp_path, flag):
    h = Harness(stage, cli, tmp_path, "risk-score")
    assert h.plan_cli(flag, tmp_path / "absent").code == 1
    assert not (h.build / "current.json").exists()


def test_a_risk_scores_pointer_must_be_a_file_and_a_target_a_directory(stage, cli, tmp_path):
    h = Harness(stage, cli, tmp_path, "risk-score")
    assert h.plan_cli("--risk-scores", tmp_path).code == 1
    assert h.plan_cli("--target", h.threats).code == 1


def test_an_architecture_candidate_that_is_not_a_file_is_dropped_with_a_warning(stage, cli, tmp_path):
    """ADR-050 D7's fallback: a stage never stops for the architecture path."""
    h = Harness(stage, cli, tmp_path, "risk-score", ids=MIXED_IDS[:6])
    res = h.plan_cli("--architecture", tmp_path / "docs" / "absent.md")
    assert res.code == 0, res.describe()
    assert "architecture" not in h.batch_input("B001")["refs"]
    assert "WARNING" in res.err and "absent.md" in res.err


@pytest.mark.parametrize("flag", ["--risk-scores", "--baseline-dir", "--architecture", "--target", "--threats"])
def test_a_pointer_with_a_forbidden_character_exits_2(stage, cli, tmp_path, flag):
    """Each pointer becomes an absolute path in a document, so it must pass D7's syntactic rule first."""
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
def test_valid_parts_for_every_batch_reconcile_to_complete(stage, cli, tmp_path, name):
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


def test_a_plan_with_no_snapshot_skips_the_declared_paths_check_with_a_warning(stage, cli, tmp_path):
    """ADR-050 D4: the snapshot is skipped, with a warning, for a name the plan can't record (or above 20,000 files)."""
    h = Harness(stage, cli, tmp_path, "risk-score")
    (h.out / "odd\\name.txt").write_bytes(b"x")
    res = h.plan_cli()
    assert res.code == 0 and "snapshot is skipped" in res.err, res.describe()
    assert h.plan_json()["out_snapshot"] is None
    (h.out / "gen.py").write_bytes(b"x")
    assert h.fail("check-failed").code == 0
    rec = h.read_json(h.plan_dir / "stage-record.json")
    assert rec["undeclared_paths"] == [] and [w["code"] for w in rec["warnings"]] == ["declared-paths-skipped"]


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
def test_fail_moves_only_files_in_the_stages_closed_set(stage, cli, tmp_path, name):
    """KB 21's double gate, the name half: only the stage's own canonical names move, whatever else changed."""
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
    """Controls get every scored open finding (D2). T036 plans them; T044 touches only the scorer."""
    h = routed(stage, cli, tmp_path, monkeypatch, ROUTED, ROUTED_GROUPS, baseline_ids=["T-2", "D-1"], name="compensating-controls")
    assert h.plan_cli().code == 0
    assert sorted(agent_ids(h), key=s2_key) == sorted(ROUTED, key=s2_key)


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


# ---- the architecture pointer goes through the shared resolver (D7)

def test_the_architecture_is_recorded_in_its_canonical_absolute_spelling(stage, cli, tmp_path, monkeypatch):
    h = routed(stage, cli, tmp_path, monkeypatch, {"S-1": "NEW"})
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "architecture.md").write_text("# a\n", encoding="utf-8")
    for given in ("docs/architecture.md", "./docs//architecture.md", str(tmp_path / "docs" / "architecture.md")):
        assert h.plan_cli("--architecture", given).code == 0, given
        assert h.batch_input("B001")["refs"]["architecture"] == str(tmp_path / "docs" / "architecture.md"), given


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
    assert "architecture" not in h.batch_input("B001")["refs"]
    assert "WARNING" in res.err and check in res.err


# ---- the SARIF fallback (D8, AR-T2)

def make_threats_sarif(ids, peers=None, absent=()):
    """A ``threats.sarif`` with one result for each ID. ``peers`` maps a peer to its primary, which are grouped as CG-1."""
    results = []
    for fid in ids:
        properties = {"baseline-state": "absent"} if fid in absent else {}
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
    assert h.batch_input("B001")["units"] == [{"finding_id": "S-1"}, {"finding_id": "T-2"}, {"finding_id": "AGP-1"}], (
        "the agent reads the rest from refs.threats")


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


def test_threats_md_wins_when_both_exist_and_the_fallback_is_the_scorers_alone(stage, cli, tmp_path, monkeypatch):
    h = Harness(stage, cli, tmp_path, "risk-score", ids=["S-1", "T-2"])
    (h.out / "threats.sarif").write_text(make_threats_sarif(["D-1"]), encoding="utf-8")
    assert h.plan_cli().code == 0 and agent_ids(h) == ["S-1", "T-2"]
    (tmp_path / "controls").mkdir()
    controls = sarif_only(stage, cli, tmp_path / "controls", monkeypatch, make_threats_sarif(["S-1"]), name="compensating-controls")
    assert controls.plan_cli().code == 1, "controls fall back to risk-scores.sarif (T036), never to threats.sarif"


def test_no_threats_md_and_no_sarif_beside_it_is_a_missing_input(stage, cli, tmp_path, monkeypatch):
    h = sarif_only(stage, cli, tmp_path, monkeypatch, make_threats_sarif(["S-1"]))
    (h.out / "threats.sarif").unlink()
    assert h.plan_cli().code == 1
    elsewhere = h.cli("plan", "--stage", "risk-score", "--out", h.out, "--date", DATE, "--threats", h.out / "renamed.md")
    assert elsewhere.code == 1, "only threats.md has a SARIF to fall back to"
