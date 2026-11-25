"""Tests for ``scripts/attack-chains.py``, written before the script (F-374 T115; TDD).

They target ADR-050 D13 (the chain script, the outcome record and its check), S-2 and S-3 of the spec (the ID order and the
chain rules), FR-K4.1, FR-K4.1b and R-24, ``contracts/cli.md`` (the three modes and their exit codes),
``contracts/threat-model-records.md`` (the outcome record, ``attack-chains.md`` at 1.1, the chain files) and
``contracts/part-files.md`` section 6 (the check's hand-off file), never an implementation. T116 writes ``plan`` to them and T117
writes ``render`` and ``check``. Until then they fail: the script does not exist, and each failure names the behavior it needed.

How they run (ADR-050 D16, H15): the entry is loaded through ``tests/conftest.py``'s ``_load_hyphenated_script``, inside a
fixture, and driven in-process through ``main(argv)``, so pytest-cov counts it. While the script is missing the fixture hands out
a stand-in whose ``main`` fails the test, so the import never fails. The one thing a process alone shows, the ``__main__`` guard's
exit status, is the last test. The tests read only public behavior: ``main(argv)``, its exit codes and streams, the files it
writes, and the contracts' records. They name no private helper of the script, so it may sit on the shared stage-entry path
(#443). Only the harness's own checks of its inputs import a shipped helper (``tachi_parsers``, ``tachi_parts``).

The material is synthetic (H8). The chain-cap variant (T148's ``fixtures/large_arch/chain-cap/main``) is the one committed input
that these tests read: 120 consolidated chains over 123 islands, with ``expected-outcomes.json`` as the oracle (its generator
declares the chains, and ``test_fixture_374.py`` re-derives them with its own coding of S-3). Everything else is built here, in
small runs whose expected chains are written out as literals and were worked out by hand from S-3.

What these tests assume of ``attack-chains.py`` (T116 and T117 follow them). Where a contract leaves a form open the test says
``# reading:`` and the architect rules it at integration; the open forms are collected under "Open forms" below.

1. **The CLI** is ``attack-chains.py plan|render|check --run-dir DIR``, and ``check`` also takes ``--plan ID``, with ``--help`` and
   ``--version``. ``main(argv=None) -> int``. ``plan`` and ``render`` exit with 0, 1 or 2, and ``check`` with 0, 2 or 5. Nothing
   in a run is ever a reason for the orchestrator to stop (R-24), so a run that cannot form chains still ends in a record.
2. **Where it reads and writes** (D13, P-6). ``--run-dir`` holds ``threats.md``, ``.tachi-build/phase1/inventory.json`` and, for
   the chains, ``.tachi-build/chains/``. ``plan`` writes ``chains/chains.json`` and nothing else. ``render`` writes
   ``attack-chains.md`` and upserts the outcome record in ``threats.md``, and nothing else. ``check`` may rewrite the record, may
   rename ``attack-chains.md`` to ``attack-chains.inconsistent.md``, and writes its hand-off file
   ``.tachi-build/threat-model/<plan_id>/checks/attack-chains.json`` (``tachi.check-handoff/1``), and nothing else.
3. **The algorithm** is S-3 with S-2's order wherever an ID decides an order: the finding set (STRIDE prefixes, layers L1 to L7,
   Section 7's layer cell first and the inventory's component layer after it), links through the flow graph's transitive closure
   in either direction and the transition table (embedded in the script, compared here with ``attack-chain-patterns-shared.md``
   by behavior), greedy assembly, deduplication, the filter, the folding of contiguous runs, ranking, ``CHAIN-`` IDs, surfacing
   (at most five, one per terminal finding, each with its converging count) and the chain-breaking target of Step 4.
4. **``attack-chains.md``** is schema 1.1: the frontmatter ``schema_version``, ``date``, ``chain_count``, ``surfaced_count`` and
   ``candidate_count``; ``## 1. Chain Summary`` and ``## 2. Chain Details`` with the surfaced chains in full; ``## 3. Other
   Consolidated Chains`` with at most 100 compact rows; the remainder line; and the stamp comment at the very end.
5. **The outcome record** is the single line ``**Attack chain outcome**: ...`` under an unnumbered ``## Attack Chain Outcome``
   heading, upserted by ``render``, and rewritten by ``check`` as ``skipped (<reason>)`` whenever it disagrees with the artifacts.

Open forms (each is a ``# reading:`` in the tests, and none is pinned beyond what the contracts say):

* ``chains.json`` and ``narratives.json`` keys. The contracts describe both files in prose, and ``tachi.chains/1`` and
  ``tachi.chain-narratives/1`` get their key sets from T091. Only ``schema`` is pinned in ``chains.json``, and its digests and counts
  are pinned by behavior (a stale input is refused, the record carries the counts). **PROVISIONAL:** ``narratives_document`` writes
  ``{"schema": "tachi.chain-narratives/1", "narratives": {CHAIN-ID: {"title", "narrative"}}}``, in one function, to change in one place.
* What ``plan`` prints. It is one JSON object that names every surfaced chain ID and no other chain ID.
* How ``render`` is told to take a rewrite. The tests model D13's flow, which is ``render``, rewrite the failing narratives once,
  ``render`` again, and read only the final file, so a stateless ``render`` and one that counts attempts both pass. The first
  ``render``'s output must name each chain whose narrative failed, because the orchestrator rewrites only those.
* ``check`` always runs with ``--plan`` here, and the tests make ``.tachi-build/threat-model/<plan_id>/checks/`` themselves, as the
  run-level plan leaves it (P-6). Whether ``check`` may run without ``--plan``, or create ``checks/``, is not pinned.
* The blank lines and any ``---`` around the record block, and the stamp's digest.

The groups of tests, by the task that turns them green:

* ``test_harness_*``: no script needed; they check the synthetic inputs, the readers and the oracle, and they pass now.
* ``test_cli_*``, ``test_plan_*``: T116 (the entry, ``plan``).
* ``test_links_*``, ``test_r21_*``, ``test_set_*`` (the finding set and the hostile text of Section 7), ``test_assembly_*``,
  ``test_tie_*``, ``test_consolidation_*``, ``test_rank_*``, ``test_surfacing_*``, ``test_breaking_*``: T116 (S-2, S-3, D13). The
  chains are observed in ``render``'s file, because ``plan`` prints only the surfaced ones and ``chains.json``'s keys are open.
* ``test_render_*``, ``test_narrative_*``, ``test_record_*``, ``test_writes_*``: T117 (``render``, the record, the write paths).
* ``test_check_*``: T117 (``check``, FR-K4.1b, R-24, RR6).
* ``test_exit_codes_come_from_a_real_interpreter``: what a process alone shows (H15).

Standard library and pytest only, and Python 3.9 syntax.
"""
from __future__ import annotations

import collections
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import types
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
ENTRY = SCRIPTS_DIR / "attack-chains.py"
PATTERNS = REPO_ROOT / ".claude" / "skills" / "tachi-shared" / "references" / "attack-chain-patterns-shared.md"
CHAIN_CAP = REPO_ROOT / "tests" / "scripts" / "fixtures" / "large_arch" / "chain-cap" / "main"
SUBPROCESS_TIMEOUT = 120

DATE = "2026-11-23"
RUN_ID = "2026-11-23T10-00-00"
PLAN_ID = "20261124T120000Z-0123456789ab"
RENDERER = "attack-chains.py"
RECORD_HEADING = "## Attack Chain Outcome"
RECORD_PREFIX = "**Attack chain outcome**: "
REMAINDER_PREFIX = "**Consolidated chains not listed**: "
EM = "\u2014"
ARROW = " \u2192 "
PREFIXES = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")  # S-2's prefix rank
RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
CATEGORY_OF_NAME = {"Spoofing": "S", "Tampering": "T", "Repudiation": "R", "Info-Disclosure": "I", "Denial-of-Service": "D",
                    "Privilege-Escalation": "E"}
CATEGORY_TITLE = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information Disclosure", "D": "Denial of Service",
                  "E": "Elevation of Privilege", "AG": "Agentic", "AGP": "Agentic", "TE": "Agentic", "LLM": "LLM", "OI": "LLM", "MI": "LLM"}
LAYER_NAME = {1: "Foundation Model", 2: "Data Operations", 3: "Agent Framework", 4: "Deployment Infrastructure",
              5: "Evaluation and Observability", 6: "Security and Compliance", 7: "Agent Ecosystem"}
STAMP = re.compile(r"^<!-- tachi-provenance: renderer=([A-Za-z0-9_.-]{1,64}); version=([0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}); "
                   r"input-digest=(sha256:[0-9a-f]{64}) -->$")
RECORD_LINE = re.compile(r"^\*\*Attack chain outcome\*\*: ", re.M)
OUTCOME_FORMS = (
    ("written", re.compile(r"chains written \((?P<n>[1-9][0-9]{0,5})\); candidates (?P<c>[0-9]{1,6}); surfaced (?P<s>[1-5])")),
    ("zero", re.compile(r"0 chains passed filter \((?P<reason>[A-Za-z0-9 .,:=-]{1,80})\); candidates (?P<c>[0-9]{1,6})")),
    ("skipped", re.compile(r"skipped \((?P<reason>[A-Za-z0-9 .,:=-]{1,80})\)")),
)
ZERO_REASONS = ("no STRIDE findings", "fewer than two layers with STRIDE findings", "no candidate links",
                "no chain with a Critical or High finding")
HANDOFF_KEYS = {"schema", "check", "plan_id", "status", "counts", "batches", "warnings", "error"}
VERBS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh")


def layer_cell(layer):
    """Section 7's MAESTRO Layer cell as the template writes it."""
    return "L%d %s %s" % (layer, EM, LAYER_NAME[layer]) if layer else "Unclassified"


def s2(finding_id):
    """S-2's total order: the prefix's rank, then the number as an integer."""
    prefix, _, number = finding_id.partition("-")
    return (PREFIXES.index(prefix), int(number))


def read_transitions():
    """``attack-chain-patterns-shared.md``'s transition table, read from the file: {((category, layer), (category, layer))}."""
    pairs, layer = set(), None
    for line in PATTERNS.read_text(encoding="utf-8").split("\n"):
        heading = re.match(r"### Source: L([1-7]) ", line)
        if heading:
            layer = int(heading.group(1))
            continue
        if layer is None or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[0] in CATEGORY_OF_NAME and re.fullmatch(r"L[1-7]", cells[1]):
            pairs.add(((CATEGORY_OF_NAME[cells[0]], layer), (CATEGORY_OF_NAME[cells[2]], int(cells[1][1:]))))
    return pairs


TRANSITIONS = read_transitions()


# =============================================================================
# 1. Synthetic runs: a threats.md, an inventory and a run directory
# =============================================================================


class Finding(collections.namedtuple("Finding", "id comp layer risk mit cell")):
    __slots__ = ()


def F(finding_id, comp, layer, risk, mit=None, cell=None):
    """One Section 7 row. ``layer`` is 1 to 7 or None (unclassified). ``cell`` replaces the layer cell's text (``""`` leaves it blank)."""
    return Finding(finding_id, comp, layer, risk, mit, cell)


def default_mitigation(finding_id):
    return "Close the gap behind finding %s by tightening the control that guards its component." % finding_id


def section7_row(f):
    layer = f.cell if f.cell is not None else layer_cell(f.layer)
    mitigation = f.mit if f.mit is not None else default_mitigation(f.id)
    return "| %s | NEW | %s | %s | %s | %s | %s | %s | %s |" % (
        f.id, CATEGORY_TITLE[f.id.partition("-")[0]], EM, f.comp, layer,
        "A synthetic weakness that the test project describes for %s." % f.comp, f.risk, mitigation)


def make_threats(findings, date=DATE, section5=True, section7=True, assets=True):
    """A threats.md cut to what the script reads and what its record lands between: front matter, Sections 5 to 8, Affected Assets."""
    out = ["---", 'schema_version: "1.4"', 'date: "%s"' % date, 'input_format: "free-text"', 'classification: "confidential"',
           'run_id: "%s"' % RUN_ID, "baseline:", "  source: null", "  date: null", "  finding_count: null", "  run_id: null",
           "coverage_gate:", '  status: "pass"', "  gaps: []", "---", "", "# Threat Model Report", "",
           "A synthetic threat model for the chain script's tests.", "", "---", ""]
    if section5:
        out += ["## 5. Coverage Matrix", "", "The coverage tables are left out of this file.", "", "---", ""]
    out += ["## 6. Risk Summary", "", "The risk summary is left out of this file.", "", "---", ""]
    if section7:
        out += ["## 7. Recommended Actions", "", "All findings sorted by risk level descending, then by table order.", "",
                "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |",
                "|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|"]
        out += [section7_row(f) for f in findings]
        out += ["", "---", ""]
    out += ["## 8. Delta Summary", "", "This run has no baseline, so every finding is NEW.", ""]
    if assets:
        out += ["---", "", "## Affected Assets", "", "| Finding ID | Affected Assets |", "|---|---|"] + ["| %s | [] |" % f.id for f in findings]
    return "\n".join(out) + "\n"


def make_inventory(components, flows, schema="tachi.phase1-inventory/1"):
    """tachi.phase1-inventory/1 (contracts/threat-model-records.md). ``components`` is [(name, layer or None)]."""
    names = [name for name, _ in components]
    doc = {"schema": schema,
           "components": [{"name": name, "dfd_type": "Process", "maestro_layer": "L%d" % layer if layer else "Unclassified",
                           "description": "A synthetic component of the test project."} for name, layer in components],
           "data_flows": [{"source": a, "destination": b, "data": "Task requests", "protocol": "HTTPS (TLS 1.3)"} for a, b in flows],
           "trust_zones": [{"name": "Test Zone", "components": names}] if names else []}
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def snapshot(root):
    """{relative path: sha256 of the bytes} of every file under ``root``."""
    root = Path(root)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def changed(before, after):
    """(added, removed, modified) path sets between two snapshots."""
    added = set(after) - set(before)
    removed = set(before) - set(after)
    return added, removed, {p for p in set(before) & set(after) if before[p] != after[p]}


class Run(object):
    """A run directory (``--run-dir``) and the paths in it."""

    def __init__(self, directory):
        self.dir = Path(directory)

    @property
    def threats(self):
        return self.dir / "threats.md"

    @property
    def inventory(self):
        return self.dir / ".tachi-build" / "phase1" / "inventory.json"

    @property
    def chains_json(self):
        return self.dir / ".tachi-build" / "chains" / "chains.json"

    @property
    def narratives(self):
        return self.dir / ".tachi-build" / "chains" / "narratives.json"

    @property
    def md(self):
        return self.dir / "attack-chains.md"

    @property
    def quarantined(self):
        return self.dir / "attack-chains.inconsistent.md"

    def handoff(self, plan_id=PLAN_ID):
        return self.dir / ".tachi-build" / "threat-model" / plan_id / "checks" / "attack-chains.json"

    def make_plan_dir(self, plan_id=PLAN_ID):
        """The run-level plan's directory, as ``tachi-stage.py plan --stage threat-model`` leaves it (P-6), with ``checks/``."""
        (self.dir / ".tachi-build" / "threat-model" / plan_id / "checks").mkdir(parents=True, exist_ok=True)

    def text(self):
        return self.threats.read_text(encoding="utf-8")

    def set_text(self, text):
        self.threats.write_text(text, encoding="utf-8")

    def files(self):
        return snapshot(self.dir)


class Project(Run):
    """A synthetic run: ``threats.md`` from findings, and an inventory from their components, ``hops`` and ``flows``."""

    def __init__(self, root, findings, flows=(), hops=(), layers=None, threats=None, inventory=None, **options):
        Run.__init__(self, Path(root) / "run")
        self.findings = list(findings)
        components = collections.OrderedDict()
        for f in self.findings:
            components.setdefault(f.comp, f.layer)
        for name, layer in hops:
            components.setdefault(name, layer)
        for name, layer in (layers or {}).items():
            components[name] = layer
        self.components, self.flows = list(components.items()), [tuple(flow) for flow in flows]
        if inventory is None:
            for a, b in self.flows:
                assert a in components and b in components, "a flow names a component that the project does not have: %s, %s" % (a, b)
        self.dir.mkdir(parents=True)
        self.set_text(make_threats(self.findings, **options) if threats is None else threats)
        if inventory is not False:
            self.inventory.parent.mkdir(parents=True)
            self.inventory.write_text(make_inventory(self.components, self.flows) if inventory is None else inventory, encoding="utf-8")


def copy_chain_cap(destination):
    """The chain-cap variant as a run directory: ``run/`` copied, with ``tachi-build/`` renamed ``.tachi-build/`` (its notes say how)."""
    run = Run(Path(destination) / "run")
    shutil.copytree(str(CHAIN_CAP / "run"), str(run.dir))
    os.rename(str(run.dir / "tachi-build"), str(run.dir / ".tachi-build"))
    return run


@pytest.fixture(scope="module")
def cap_doc():
    """The chain-cap variant's ``expected-outcomes.json``: the oracle for the 120-chain case."""
    return json.loads((CHAIN_CAP / "expected-outcomes.json").read_text(encoding="utf-8"))


# =============================================================================
# 2. The harness: loading the entry, invoking it, and the three modes
# =============================================================================


class Result(object):
    def __init__(self, code, out, err):
        self.code, self.out, self.err = code, out, err

    def describe(self):
        return "exit %r\n--- stdout ---\n%s\n--- stderr ---\n%s" % (self.code, self.out[-3000:], self.err[-3000:])

    @property
    def both(self):
        return self.out + "\n" + self.err


def invoke(module, argv, cwd=None):
    """``module.main(argv)`` in-process with stdout and stderr captured. ``SystemExit`` (argparse) becomes the code."""
    out, err = io.StringIO(), io.StringIO()
    previous = os.getcwd()
    if cwd is not None:
        os.chdir(str(cwd))
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = module.main([str(a) for a in argv])
            except SystemExit as exc:  # argparse's usage errors, --help and --version
                code = exc.code
                if code is None:
                    code = 0
                elif not isinstance(code, int):
                    err.write(str(code))
                    code = 1
    finally:
        os.chdir(previous)
    return Result(code, out.getvalue(), err.getvalue())


_ENTRY_MODULE = []


class MissingEntry(object):
    """Stands in for the entry while ``scripts/attack-chains.py`` does not exist, so that each test fails, in its own body, and says what
    behavior it needed. (A fixture that failed instead would show as an error at setup, and the import must never fail.)"""

    def __init__(self, behavior):
        self.behavior = behavior

    def main(self, argv=None):
        pytest.fail("scripts/attack-chains.py does not exist yet (T116 and T117 write it to these tests). Behavior missing: %s"
                    % self.behavior, pytrace=False)


@pytest.fixture
def chains(request):
    """The entry module, loaded once. While the script is missing it is a stand-in whose ``main`` fails the test with the test's behavior."""
    if not ENTRY.is_file():
        doc = " ".join((request.function.__doc__ or request.function.__name__).split())
        return MissingEntry(doc if len(doc) <= 260 else doc[:257].rsplit(" ", 1)[0] + " ...")
    if not _ENTRY_MODULE:
        _ENTRY_MODULE.append(_load_hyphenated_script("attack_chains_under_test", "attack-chains.py"))
    return _ENTRY_MODULE[0]


def run_plan(module, run):
    return invoke(module, ["plan", "--run-dir", run.dir])


def run_render(module, run):
    return invoke(module, ["render", "--run-dir", run.dir])


def run_check(module, run, plan_id=PLAN_ID, make_plan_dir=True):
    if make_plan_dir:
        run.make_plan_dir(plan_id)
    return invoke(module, ["check", "--run-dir", run.dir, "--plan", plan_id])


def must(result, codes, what):
    """Fail with the whole result when the exit code is not one of ``codes``."""
    codes = (codes,) if isinstance(codes, int) else tuple(codes)
    assert result.code in codes, "%s: expected exit %s\n%s" % (what, " or ".join(str(c) for c in codes), result.describe())
    return result


def surfaced_ids(plan_stdout):
    """Every chain ID that ``plan`` printed, once each, in the order printed.

    reading: ``plan`` prints the surfaced chains (D13), so the IDs on its stdout are the surfaced set.
    """
    seen = []
    for found in re.findall(r"CHAIN-[0-9]{3,6}", plan_stdout):
        if found not in seen:
            seen.append(found)
    return seen


def narratives_document(texts):
    """The orchestrator's ``chains/narratives.json``: ``texts`` maps a chain ID to ``(title, narrative)``.

    reading: PROVISIONAL. The contract says the file "maps each surfaced chain ID, and only those, to {title, narrative}" and that
    every new JSON file names its ``schema``. The container key ``narratives`` is a guess until T091 declares ``tachi.chain-narratives/1``;
    this is the one place that builds the shape.
    """
    return {"schema": "tachi.chain-narratives/1",
            "narratives": {cid: {"title": title, "narrative": narrative} for cid, (title, narrative) in texts.items()}}


TITLE = "A cross-layer path from an exposed weakness to its final impact"
NARRATIVE = ("The attacker starts at the first finding of the chain and uses what it gives to reach the next one, so that each step "
             "prepares the one after it. The last finding is where the impact lands. Removing the finding that the chain marks as its "
             "breaking target cuts the path in two, which is why its mitigation is listed first.")


def default_texts(ids):
    """A valid ``(title, narrative)`` for each chain ID: no numeral outside a slot, and each one different."""
    return {cid: ("%s (%s)" % (TITLE, VERBS[i % len(VERBS)]), "%s This is the %s chain of the run." % (NARRATIVE, VERBS[i % len(VERBS)]))
            for i, cid in enumerate(ids)}


def write_narratives(run, texts):
    run.narratives.parent.mkdir(parents=True, exist_ok=True)
    run.narratives.write_text(json.dumps(narratives_document(texts), indent=2, sort_keys=True) + "\n", encoding="utf-8")


class Flow(object):
    def __init__(self, plan, render, ids):
        self.plan, self.render, self.ids = plan, render, ids


def run_flow(module, run, texts=None):
    """The orchestrator's Phase 3.5: ``plan``, narratives for the surfaced chains only, then ``render``.

    ``texts`` maps chain IDs to ``(title, narrative)`` and replaces the default for those IDs. Neither call's exit code is a
    reason to stop (R-24), so both run whatever the first returns.
    """
    plan = must(run_plan(module, run), (0, 1, 2), "plan")
    ids = surfaced_ids(plan.out)
    if ids:
        merged = default_texts(ids)
        merged.update(texts or {})
        write_narratives(run, merged)
    return Flow(plan, must(run_render(module, run), (0, 1, 2), "render"), ids)


def good_flow(module, run, texts=None):
    """``run_flow`` for a run that must form chains: both calls exit 0 and ``attack-chains.md`` exists."""
    flow = run_flow(module, run, texts)
    must(flow.plan, 0, "plan")
    must(flow.render, 0, "render")
    assert run.md.is_file(), "render exited 0 but wrote no attack-chains.md\n%s" % flow.render.describe()
    return flow


# =============================================================================
# 3. Readers: attack-chains.md, the outcome record and the hand-off file
# =============================================================================


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_table(lines, start):
    """The table whose header row is ``lines[start]``: ``(header, rows as dicts, raw row lines, next index)``."""
    header, rows, raw, i = split_row(lines[start]), [], [], start + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append(dict(zip(header, split_row(lines[i]))))
        raw.append(lines[i].rstrip())
        i += 1
    return header, rows, raw, i


def split_arrow(text):
    return [part.strip() for part in re.split(r"\s*(?:\u2192|->)\s*", text.strip())] if text and text.strip() else []


def read_md(text):
    """``attack-chains.md`` as a namespace. Anything that is absent is ``None`` or empty, so a test fails on its own assertion."""
    lines = text.split("\n")
    doc = types.SimpleNamespace(lines=lines, front={}, summary=[], summary_header=[], summary_raw=[], details=collections.OrderedDict(),
                                compact=[], compact_raw=[], compact_header=[], remainder=None, stamp=None, last_content=None, text=text)
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        for line in lines[1:end] if end else ():
            key, _, value = line.partition(":")
            doc.front[key.strip()] = value.strip().strip('"')
    content = [line for line in lines if line.strip()]
    if content and STAMP.match(content[-1].strip()):
        doc.stamp = STAMP.match(content[-1].strip()).groups()
        content = content[:-1]
    doc.last_content = content[-1].strip() if content else None
    match = re.match(r"^\*\*Consolidated chains not listed\*\*: ([0-9]+)$", doc.last_content or "")
    doc.remainder = int(match.group(1)) if match else None
    headings = [i for i, line in enumerate(lines) if line.startswith("## ")]
    bounds = list(zip(headings, headings[1:] + [len(lines)]))
    for start, end in bounds:
        body = lines[start + 1:end]
        title = lines[start].strip()
        table = next((i for i, line in enumerate(body) if line.strip().startswith("|")), None)
        if title == "## 1. Chain Summary" and table is not None:
            doc.summary_header, doc.summary, doc.summary_raw, _ = read_table(body, table)
        elif title == "## 3. Other Consolidated Chains" and table is not None:
            doc.compact_header, doc.compact, doc.compact_raw, _ = read_table(body, table)
        elif title == "## 2. Chain Details":
            starts = [i for i, line in enumerate(body) if re.match(r"^### CHAIN-[0-9]{3,6}: ", line)]
            for first, last in zip(starts, starts[1:] + [len(body)]):
                detail = read_detail(body[first:last])
                doc.details[detail.id] = detail
    return doc


def read_detail(block):
    head = re.match(r"^### (CHAIN-[0-9]{3,6}): (.*)$", block[0])
    detail = types.SimpleNamespace(id=head.group(1), title=head.group(2).strip(), layers=None, max=None, surfaced=None,
                                   converging=None, members=[], narrative="", target=None, recommendation=None, raw="\n".join(block))
    for line in block:
        s = line.strip()
        for key, pattern in (("layers", r"\*\*Layers\*\*:\s*(.*)$"), ("max", r"\*\*Max Severity\*\*:\s*(.*)$"),
                             ("surfaced", r"\*\*Surfaced\*\*:\s*(.*)$"), ("converging", r"\*\*Converging chains\*\*:\s*(.*)$"),
                             ("target", r"\*\*Target\*\*:\s*(\S+)"), ("recommendation", r"\*\*Recommendation\*\*:\s*(.*)$")):
            found = re.match(pattern, s)
            if found:
                setattr(detail, key, found.group(1).strip())
    marker = next((i for i, line in enumerate(block) if line.strip() == "#### Member Findings"), None)
    if marker is not None:
        table = next((i for i in range(marker + 1, len(block)) if block[i].strip().startswith("|")), None)
        if table is not None:
            detail.members = read_table(block, table)[1]
    marker = next((i for i, line in enumerate(block) if line.strip() == "#### Attack Progression"), None)
    if marker is not None:
        prose = []
        for line in block[marker + 1:]:
            if line.startswith("#") or line.strip() == "---":
                break
            if line.strip():
                prose.append(line.strip())
        detail.narrative = " ".join(prose)
    return detail


def md_chains(doc):
    """Every chain the file lists, by ID: the surfaced ones from their detail sections, the others from the compact rows."""
    found = {}
    for cid, d in doc.details.items():
        found[cid] = {"id": cid, "members": [m.get("Finding ID") for m in d.members], "layers": split_arrow(d.layers), "max": d.max,
                      "target": d.target, "surfaced": True, "converging": int(d.converging) if (d.converging or "").isdigit() else None}
    for row in doc.compact:
        cid = row.get("Chain ID")
        found[cid] = {"id": cid, "members": split_arrow(row.get("Findings", "")), "layers": split_arrow(row.get("Layers", "")),
                      "max": row.get("Max Severity"), "target": row.get("Chain-Breaking Target"), "surfaced": False, "converging": None}
    return collections.OrderedDict(sorted(found.items(), key=lambda kv: int(kv[0].partition("-")[2])))


def record_lines(text):
    return [line for line in text.split("\n") if RECORD_LINE.match(line)]


def parse_outcome(value):
    """The outcome grammar of contracts/threat-model-records.md: ``{"form": ..., ...}``, or None for a line that is not one of the three."""
    for form, pattern in OUTCOME_FORMS:
        match = pattern.fullmatch(value)
        if match:
            fields = match.groupdict()
            if form == "written" and not (int(fields["c"]) >= int(fields["n"]) and int(fields["s"]) <= int(fields["n"])):
                return None
            return dict(fields, form=form)
    return None


def the_record(text):
    """The one outcome record of a threats.md, parsed. Fails the test when there is not exactly one, or when it breaks the grammar."""
    found = record_lines(text)
    assert len(found) == 1, "expected exactly one outcome record, found %d:\n%s" % (len(found), "\n".join(found))
    value = found[0][len(RECORD_PREFIX):]
    parsed = parse_outcome(value)
    assert parsed is not None, "the outcome record breaks the grammar: %r" % value
    parsed["value"] = value
    return parsed


def record_context(text):
    """Where the record sits: the heading before it and the next heading after it (blank lines and ``---`` rules are skipped)."""
    lines = text.split("\n")
    at = next(i for i, line in enumerate(lines) if RECORD_LINE.match(line))
    before = next((lines[i] for i in range(at - 1, -1, -1) if lines[i].strip() and lines[i].strip() != "---"), None)
    after = next((lines[i] for i in range(at + 1, len(lines)) if lines[i].strip() and lines[i].strip() != "---"), None)
    return types.SimpleNamespace(before=before, after=after, index=at, lines=lines)


def without_record(text):
    """``text`` with the outcome record, its heading and the blank line after each removed, as a file that was never rendered."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        if lines[i].strip() == RECORD_HEADING or RECORD_LINE.match(lines[i]):
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    assert len(keys) == len(set(keys)), "a JSON object repeats a key: %s" % keys
    return dict(pairs)


def read_handoff(run, plan_id=PLAN_ID):
    path = run.handoff(plan_id)
    assert path.is_file(), "check wrote no hand-off file at %s" % path.relative_to(run.dir)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def assert_handoff(run, status, plan_id=PLAN_ID, outcome=None):
    """``tachi.check-handoff/1`` for the chain check (part-files.md section 6): the closed key set, and the values it fixes."""
    doc = read_handoff(run, plan_id)
    assert set(doc) == HANDOFF_KEYS, "the hand-off's keys are %s" % sorted(doc)
    assert doc["schema"] == "tachi.check-handoff/1" and doc["check"] == "attack-chains" and doc["plan_id"] == plan_id
    assert doc["counts"] is None and doc["batches"] is None and doc["error"] is None, "attack-chains has no counts, batches or error"
    assert doc["status"] == status, "status is %r, not %r" % (doc["status"], status)
    assert isinstance(doc["warnings"], list) and len(doc["warnings"]) == (1 if status == "warn" else 0), doc["warnings"]
    for warning in doc["warnings"]:
        assert set(warning) == {"code", "detail"} and warning["code"] == "chain-outcome:rewritten", warning
        assert isinstance(warning["detail"], str) and len(warning["detail"]) <= 500
        if outcome is not None:
            assert outcome in warning["detail"], "the warning's detail does not carry the new record %r: %r" % (outcome, warning["detail"])
    return doc


# =============================================================================
# 4. Harness self-checks (no script needed)
# =============================================================================


def test_harness_the_transition_table_is_read_from_the_shared_reference():
    """The harness reads attack-chain-patterns-shared.md's table, which the drift test compares with the script's."""
    assert 30 <= len(TRANSITIONS) <= 200, len(TRANSITIONS)
    assert {source[0] for source, _ in TRANSITIONS} == {"S", "T", "R", "I", "D", "E"}
    assert all(source[1] != target[1] for source, target in TRANSITIONS), "a transition within one layer would never link (S-3(b))"
    assert any((target, source) in TRANSITIONS for source, target in TRANSITIONS), "the table has mutual pairs, which dedupe"


def test_harness_the_chain_cap_oracle_is_the_bound_case(cap_doc):
    """The chain-cap variant is the S-3(g) case: more than 105 chains, five in full, 100 compact rows, a remainder line."""
    counts = cap_doc["counts"]
    assert counts["consolidated"] == len(cap_doc["chains"]) == 120 and counts["consolidated"] > 105
    assert counts["surfaced"] == len(cap_doc["surfaced"]) == 5 and counts["compact_rows"] == len(cap_doc["compact_rows"]) == 100
    assert cap_doc["remainder_line"] == REMAINDER_PREFIX + "15" and counts["not_listed"] == 15
    assert parse_outcome(cap_doc["outcome_record"]) == dict(form="written", n="120", c="136", s="5")
    assert cap_doc["frontmatter_counts"] == {"chain_count": 120, "surfaced_count": 5, "candidate_count": 136}


def test_harness_the_chain_cap_run_copies_into_a_run_directory(tmp_path):
    """The committed chain-cap files become a run directory once tachi-build/ is renamed."""
    run = copy_chain_cap(tmp_path)
    assert run.threats.is_file() and run.inventory.is_file() and not run.md.exists() and not record_lines(run.text())


def test_harness_synthetic_runs_are_read_as_intended_by_the_shipped_reference_set_reader(tmp_path):
    """The builders write a Section 7 that the shipped reader reads back: IDs, components, risk, mitigation and layers."""
    tachi_parsers = shared_module("tachi_parsers")
    findings = [F("T-1", "ingest gateway", 5, "High"), F("S-12", "policy checker", 6, "Low", mit="Rotate the credential."),
                F("E-3", "agent core", None, "Critical"), F("AG-2", "agent core", 3, "High", cell="")]
    project = Project(tmp_path, findings)
    reference = tachi_parsers.parse_reference_set(project.text())
    assert {f["id"] for f in reference["open"]} == {f.id for f in findings} and not reference["resolved"]
    by_id = {f["id"]: f for f in reference["open"]}
    assert by_id["S-12"]["component"] == "policy checker" and by_id["S-12"]["risk_level"] == "Low"
    assert by_id["S-12"]["mitigation"] == "Rotate the credential."
    layers = tachi_parsers.parse_finding_layers(project.text())
    assert layers["T-1"].startswith("L5") and layers["S-12"].startswith("L6") and layers["E-3"] == "Unclassified" and "AG-2" not in layers
    inventory = json.loads(project.inventory.read_text(encoding="utf-8"))
    assert {c["name"]: c["maestro_layer"] for c in inventory["components"]} == {
        "ingest gateway": "L5", "policy checker": "L6", "agent core": "Unclassified"}


def shared_module(name):
    """A shipped helper module of scripts/, imported without leaving bytecode behind (ADR-049 D8)."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    keep, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        return __import__(name)
    finally:
        sys.dont_write_bytecode = keep


def test_harness_the_provisional_narratives_shape_follows_the_declared_key_set_once_there_is_one():
    """narratives_document is a guess until T091 declares tachi.chain-narratives/1: from then on it must use the declared keys."""
    declared = {name: keys for name, keys in getattr(shared_module("tachi_parts"), "KEY_SETS", {}).items()
                if re.search(r"chain.*narrat|narrat.*chain", name)}
    shape = narratives_document({"CHAIN-001": ("A title", "A narrative")})
    for name, (required, optional) in declared.items():
        assert set(required) <= set(shape) <= set(required) | set(optional), (
            "tachi_parts declares %r with keys %s; update narratives_document (one place) to build them, not %s" % (
                name, sorted(set(required) | set(optional)), sorted(shape)))


def test_harness_the_md_reader_reads_the_committed_example_format():
    """The reader understands today's attack-chains.md layout, which 1.1 extends."""
    example = REPO_ROOT / "examples" / "agentic-app" / "sample-report" / "attack-chains.md"
    doc = read_md(example.read_text(encoding="utf-8"))
    assert doc.front["chain_count"] == "5" and len(doc.summary) == 5 and len(doc.details) == 5
    first = doc.details["CHAIN-001"]
    assert [m["Finding ID"] for m in first.members] == ["S-1", "E-1", "E-5"] and first.layers == "L7 \u2192 L6 \u2192 L3"
    assert first.surfaced == "Yes" and first.target == "S-2" and first.narrative.startswith("An attacker initiates")


# =============================================================================
# 5. Small cases and how a test observes one
# =============================================================================
#
# Every expected chain below was worked out by hand from S-3 and then checked against a second, independent coding of the rules
# (which also reproduces the chain-cap oracle: 136 candidates, 120 consolidated chains). The tests assert the whole file's
# chain list, so one wrong rule shows as a wrong list.


def observe(module, project, texts=None):
    """Run the orchestrator's flow on a project that must form chains: ``(flow, the parsed attack-chains.md, the parsed record)``."""
    flow = good_flow(module, project, texts)
    return flow, read_md(project.md.read_text(encoding="utf-8")), the_record(project.text())


def observe_nothing(module, project):
    """Run the flow on a project that forms no chain: both calls exit 0, no ``attack-chains.md`` is written, and the record is parsed."""
    flow = run_flow(module, project)
    must(flow.plan, 0, "plan")
    must(flow.render, 0, "render")
    assert not project.md.exists(), "an outcome without chains must leave no attack-chains.md (FR-K4.1b)"
    return the_record(project.text())


def listing(doc):
    """``(ID, members, layers, max severity, breaking target)`` of every chain the file lists, in rank order."""
    return [(c["id"], c["members"], c["layers"], c["max"], c["target"]) for c in md_chains(doc).values()]


def surfaced_of(doc):
    """``{ID: converging count}`` of the chains shown in full."""
    return {cid: c["converging"] for cid, c in md_chains(doc).items() if c["surfaced"]}


def path3(root, mitigation=None):
    """T-1 (L5, High) to T-2 (L6, Medium) to E-1 (L3, Critical) along two flows: one chain of three and its tail."""
    return Project(root, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Medium", mit=mitigation),
                          F("E-1", "agent-core", 3, "Critical")],
                   flows=[("ingest-gateway", "policy-checker"), ("policy-checker", "agent-core")])


PATH3_LISTING = [("CHAIN-001", ["T-1", "T-2", "E-1"], ["L5", "L6", "L3"], "Critical", "T-2")]
PATH3_RECORD = "chains written (1); candidates 2; surfaced 1"


def plain_islands(root, count, risk="Critical"):
    """``count`` islands of two components and one flow each: one chain apiece, with its own terminal finding (so every one surfaces
    until five have). Each island takes a transition with no reverse row, so a pair makes exactly one chain."""
    kinds = sorted((a, b) for a, b in TRANSITIONS if (b, a) not in TRANSITIONS)
    numbers, findings, flows = collections.Counter(), [], []
    for k in range(count):
        (prefix_a, layer_a), (prefix_b, layer_b) = kinds[k % len(kinds)]
        ids = []
        for prefix in (prefix_a, prefix_b):
            numbers[prefix] += 1
            ids.append("%s-%d" % (prefix, numbers[prefix]))
        findings += [F(ids[0], "island-%d-source" % k, layer_a, risk), F(ids[1], "island-%d-target" % k, layer_b, risk)]
        flows.append(("island-%d-source" % k, "island-%d-target" % k))
    return Project(root, findings, flows=flows)


# =============================================================================
# 6. The command line
# =============================================================================


def shipped_version():
    return re.search(r'^VERSION = "([0-9]+\.[0-9]+\.[0-9]+)"', (SCRIPTS_DIR / "tachi_parts.py").read_text(encoding="utf-8"), re.M).group(1)


def test_cli_help_names_the_three_modes(chains):
    """--help lists the plan, render and check modes (contracts/cli.md)."""
    result = invoke(chains, ["--help"])
    assert result.code == 0 and all(mode in result.out for mode in ("plan", "render", "check")), result.describe()


@pytest.mark.parametrize("mode,option", [("plan", "--run-dir"), ("render", "--run-dir"), ("check", "--run-dir"), ("check", "--plan")])
def test_cli_every_mode_documents_its_options(chains, mode, option):
    """Each mode's --help names --run-dir, and check's names --plan, the run-level plan for its hand-off file."""
    result = invoke(chains, [mode, "--help"])
    assert result.code == 0 and option in result.out, result.describe()


def test_cli_version_prints_the_shipped_version_and_the_interpreters(chains):
    """--version exits 0 and prints tachi_parts.VERSION and the interpreter's version (contracts/cli.md)."""
    result = invoke(chains, ["--version"])
    assert result.code == 0, result.describe()
    assert shipped_version() in result.both and "%d.%d" % sys.version_info[:2] in result.both, result.describe()


@pytest.mark.parametrize("argv", [[], ["plan"], ["render"], ["check"], ["frobnicate", "--run-dir", "x"], ["plan", "--run-dir"],
                                  ["plan", "--run-dir", "x", "--bogus"], ["check", "--run-dir", "x", "--plan"]])
def test_cli_a_usage_error_exits_2_and_writes_nothing(chains, tmp_path, argv):
    """A missing mode or option, an unknown mode or option, or a missing value is argparse's usage error: exit 2, and no file."""
    result = invoke(chains, argv, cwd=tmp_path)
    assert result.code == 2 and result.err.strip(), result.describe()
    assert not list(tmp_path.iterdir()), "a usage error wrote %s" % [p.name for p in tmp_path.iterdir()]


@pytest.mark.parametrize("plan_id", ["", "not-a-plan", "../../escape", "20261124T120000Z-0123456789AB", "20261124T120000Z-0123456789a",
                                     "20261124T120000Z-0123456789abc", "20261124T120000-0123456789ab", PLAN_ID + "/../x"])
def test_cli_check_refuses_a_plan_id_outside_the_grammar_and_writes_nothing(chains, tmp_path, plan_id):
    """check --plan takes only a plan ID of the allow-list's grammar: anything else exits 2 and writes no file, in or out of the run."""
    run = Project(tmp_path, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Medium")],
                  flows=[("ingest-gateway", "policy-checker")])
    run.make_plan_dir()
    before = snapshot(tmp_path)
    result = invoke(chains, ["check", "--run-dir", run.dir, "--plan", plan_id])
    assert result.code == 2, result.describe()
    assert snapshot(tmp_path) == before, "a refused plan ID wrote %s" % sorted(set(snapshot(tmp_path)) ^ set(before))


# =============================================================================
# 7. plan
# =============================================================================


def test_plan_on_the_chain_cap_prints_only_the_surfaced_chains(chains, tmp_path, cap_doc):
    """plan prints one JSON object that names the five surfaced chains of the 120, in rank order, and no other chain."""
    run = copy_chain_cap(tmp_path)
    result = must(run_plan(chains, run), 0, "plan")
    assert isinstance(json.loads(result.out), dict), "plan prints one JSON object: %r" % result.out[:200]
    assert surfaced_ids(result.out) == cap_doc["surfaced"], "plan must print the surfaced chains, and only those"
    assert result.err.strip() == "", "a clean plan prints nothing on stderr: %r" % result.err


def test_plan_writes_chains_json_and_nothing_else(chains, tmp_path):
    """plan writes chains/chains.json (tachi.chains/1) and leaves threats.md, the inventory and everything else byte for byte as it was."""
    run = copy_chain_cap(tmp_path)
    before = run.files()
    must(run_plan(chains, run), 0, "plan")
    added, removed, modified = changed(before, run.files())
    assert added == {".tachi-build/chains/chains.json"} and not removed and not modified, (added, removed, modified)
    doc = json.loads(run.chains_json.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    assert isinstance(doc, dict) and doc.get("schema") == "tachi.chains/1", sorted(doc)


def test_plan_twice_gives_identical_output(chains, tmp_path):
    """Two plan runs on one finding set are byte-identical, in chains.json and on stdout (US-2 #5, NFR-2)."""
    run = copy_chain_cap(tmp_path)
    first = must(run_plan(chains, run), 0, "first plan")
    kept = run.chains_json.read_bytes()
    second = must(run_plan(chains, run), 0, "second plan")
    assert run.chains_json.read_bytes() == kept and second.out == first.out, "the second plan differs from the first"


def test_plan_a_replan_after_a_change_replaces_chains_json(chains, tmp_path):
    """A plan on changed inputs writes a different chains.json, so a stale one never survives a new plan."""
    project = path3(tmp_path)
    must(run_plan(chains, project), 0, "plan")
    kept = project.chains_json.read_bytes()
    project.set_text(make_threats([F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Critical"),
                                   F("E-1", "agent-core", 3, "Critical")]))
    must(run_plan(chains, project), 0, "second plan")
    assert project.chains_json.read_bytes() != kept


def test_plan_a_run_without_chains_exits_0_and_prints_no_chain(chains, tmp_path):
    """plan on findings that cannot link exits 0 and prints no chain (0 chains is an outcome, not an error)."""
    project = Project(tmp_path, [F("T-1", "ingest-gateway", 5, "High"), F("S-1", "policy-checker", 5, "High")])
    result = must(run_plan(chains, project), 0, "plan")
    assert surfaced_ids(result.out) == []


# =============================================================================
# 8. The transition table, the flow graph and the finding set (S-3(b))
# =============================================================================


def test_links_follow_the_shared_reference_table_exactly(chains, tmp_path):
    """The script's embedded table equals attack-chain-patterns-shared.md's: every one of the 903 pairs of (category, layer) links
    exactly when the reference has a row for it, in one direction or the other, and a pair with one row runs in that row's direction."""
    nodes = [(c, layer) for layer in range(1, 8) for c in ("S", "T", "R", "I", "D", "E")]
    pairs = [(a, b) for i, a in enumerate(nodes) for b in nodes[i:]]
    related = [p for p in pairs if (p[0], p[1]) in TRANSITIONS or (p[1], p[0]) in TRANSITIONS]
    others = [p for p in pairs if p not in related]
    assert related and others and len(pairs) == 903
    size = 110
    batches = [related + others[:size - len(related)]] + [others[i:i + size] for i in range(size - len(related), len(others), size)]
    seen = 0
    for number, batch in enumerate(batches):
        numbers, findings, flows, expected = collections.Counter(), [], [], {}
        for k, (a, b) in enumerate(batch):
            ids = []
            for category in (a[0], b[0]):
                numbers[category] += 1
                ids.append("%s-%d" % (category, numbers[category]))
            findings += [F(ids[0], "pair-%d-first" % k, a[1], "Critical"), F(ids[1], "pair-%d-second" % k, b[1], "Critical")]
            flows.append(("pair-%d-first" % k, "pair-%d-second" % k))
            if (a, b) in TRANSITIONS or (b, a) in TRANSITIONS:
                forward, backward = (a, b) in TRANSITIONS, (b, a) in TRANSITIONS
                order = [ids[0], ids[1]] if forward and not backward else [ids[1], ids[0]] if backward and not forward else sorted(ids, key=s2)
                expected[frozenset(ids)] = order
        project = Project(tmp_path / ("batch-%d" % number), findings, flows=flows)
        if expected:
            flow, doc, record = observe(chains, project)
            found = {frozenset(c["members"]): c["members"] for c in md_chains(doc).values()}
            assert found == expected, "batch %d: the links differ from the reference table: missing %s, unexpected %s" % (
                number, sorted(map(sorted, set(expected) - set(found)))[:5], sorted(map(sorted, set(found) - set(expected)))[:5])
            assert record["form"] == "written" and int(record["n"]) == len(expected), record
            seen += len(expected)
        else:
            record = observe_nothing(chains, project)
            assert record["value"] == "0 chains passed filter (no candidate links); candidates 0", record
    assert seen == len(related)


def test_links_a_flow_links_findings_whichever_way_it_runs(chains, tmp_path):
    """One component reachable from the other, in either direction, is enough (S-3(b), 'or vice versa'): the flow may run against the link."""
    for name, flows in (("with", [("gateway-a", "portal-b")]), ("against", [("portal-b", "gateway-a")])):
        project = Project(tmp_path / name, [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")], flows=flows)
        flow, doc, record = observe(chains, project)
        assert listing(doc) == [("CHAIN-001", ["I-1", "I-2"], ["L3", "L7"], "Critical", "I-2")], name
        assert record["value"] == "chains written (1); candidates 1; surfaced 1", name


@pytest.mark.parametrize("hops,flows", [
    pytest.param([("hop-node", 4)], [("gateway-a", "hop-node"), ("hop-node", "portal-b")], id="two-hops"),
    pytest.param([("hop-node", 4)], [("portal-b", "hop-node"), ("hop-node", "gateway-a")], id="two-hops-against-the-link"),
    pytest.param([("hop-one", 4), ("hop-two", 2)], [("gateway-a", "hop-one"), ("hop-one", "hop-two"), ("hop-two", "portal-b")], id="three-hops"),
    pytest.param([("hop-one", 4), ("hop-two", 2)], [("portal-b", "hop-two"), ("hop-two", "hop-one"), ("hop-one", "gateway-a")],
                 id="three-hops-against-the-link"),
])
def test_r21_a_link_may_run_through_the_transitive_closure(chains, tmp_path, hops, flows):
    """R-21 pin: components with no direct flow link through the flow graph's transitive closure (two or more hops, either way round).
    Narrowing it to direct flows, or to the link's direction, changes which findings can link and goes to the PM first."""
    project = Project(tmp_path, [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")], hops=hops, flows=flows)
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["I-1", "I-2"], ["L3", "L7"], "Critical", "I-2")]
    assert record["value"] == "chains written (1); candidates 1; surfaced 1"


def test_links_a_cycle_in_the_flows_is_no_problem(chains, tmp_path):
    """Flows that run in a circle still give one chain: reachability ends at the components it has seen."""
    project = Project(tmp_path, [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")], hops=[("hop-node", 4)],
                      flows=[("gateway-a", "hop-node"), ("hop-node", "portal-b"), ("portal-b", "gateway-a")])
    flow, doc, record = observe(chains, project)
    assert [c[1] for c in listing(doc)] == [["I-1", "I-2"]] and record["form"] == "written"


@pytest.mark.parametrize("name,findings,flows", [
    pytest.param("no flow at all", [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")], [], id="no-flow"),
    pytest.param("flows that do not join the two", [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")],
                 [("gateway-a", "hop-node")], id="flows-elsewhere"),
    pytest.param("a flow but no table row", [F("T-1", "gateway-a", 2, "High"), F("I-2", "portal-b", 3, "Critical")],
                 [("gateway-a", "portal-b")], id="no-row"),
    pytest.param("one layer for both", [F("T-1", "gateway-a", 3, "High"), F("S-2", "portal-b", 3, "Critical")],
                 [("gateway-a", "portal-b")], id="same-layer"),
])
def test_links_need_both_a_flow_path_and_a_table_row(chains, tmp_path, name, findings, flows):
    """No flow path, no transition row, or one layer for both: no link, no candidate, and the record says so."""
    project = Project(tmp_path, findings, hops=[("hop-node", 4)], flows=flows)
    record = observe_nothing(chains, project)
    assert record["form"] == "zero" and record["c"] == "0", (name, record)


def test_set_ai_findings_never_join_a_chain(chains, tmp_path):
    """Only STRIDE prefixes form chains (ADR-050 D13): AG and LLM findings on joined components change nothing."""
    project = Project(tmp_path, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Medium"),
                                 F("E-1", "agent-core", 3, "Critical"), F("AG-1", "planner-agent", 3, "Critical"),
                                 F("LLM-1", "model-host", 1, "Critical")],
                      flows=[("ingest-gateway", "policy-checker"), ("policy-checker", "agent-core"), ("planner-agent", "ingest-gateway"),
                             ("model-host", "ingest-gateway")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == PATH3_LISTING and record["value"] == PATH3_RECORD


def test_set_a_finding_on_an_unclassified_layer_is_left_out(chains, tmp_path):
    """A STRIDE finding that has no layer (Section 7 says Unclassified, and so does its component) takes no part in a chain."""
    project = Project(tmp_path, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Medium"),
                                 F("E-1", "agent-core", 3, "Critical"), F("S-9", "legacy-adapter", None, "Critical", cell="Unclassified")],
                      flows=[("ingest-gateway", "policy-checker"), ("policy-checker", "agent-core"), ("legacy-adapter", "ingest-gateway")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == PATH3_LISTING and record["value"] == PATH3_RECORD


def test_set_a_blank_layer_cell_falls_back_to_the_inventory(chains, tmp_path):
    """A finding whose Section 7 cell is blank takes its component's layer from the inventory (ADR-050 D13, D2's chain)."""
    project = Project(tmp_path, [F("I-1", "gateway-a", 3, "High", cell=""), F("I-2", "portal-b", 7, "Critical")],
                      flows=[("gateway-a", "portal-b")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["I-1", "I-2"], ["L3", "L7"], "Critical", "I-2")]


def test_set_section_7s_layer_cell_wins_over_the_inventory(chains, tmp_path):
    """A finding's own Section 7 layer comes before its component's: the inventory says L4, Section 7 says L3, and the chain uses L3."""
    project = Project(tmp_path, [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")],
                      flows=[("gateway-a", "portal-b")], layers={"gateway-a": 4})
    assert dict(project.components)["gateway-a"] == 4
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["I-1", "I-2"], ["L3", "L7"], "Critical", "I-2")]


def test_set_component_names_compare_after_casefolding_and_collapsing_whitespace(chains, tmp_path):
    """'Gateway  Node', 'gateway node' and 'GATEWAY NODE' are one component (ADR-050 D13): the layer and the flow are found."""
    findings = [F("I-1", "Gateway  Node", 3, "High", cell=""), F("I-2", "Portal Node", 7, "Critical")]
    inventory = make_inventory([("gateway node", 3), ("PORTAL   node", 7)], [("GATEWAY NODE", "portal  NODE")])
    project = Project(tmp_path, findings, inventory=inventory)
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["I-1", "I-2"], ["L3", "L7"], "Critical", "I-2")]


# =============================================================================
# 9. Assembly, ties, consolidation, ranking, surfacing (S-3(c) to S-3(f))
# =============================================================================


def test_assembly_a_path_of_three_is_one_chain_and_a_folded_tail(chains, tmp_path):
    """Each finding with an outgoing link starts one chain, and a chain that is the tail of a longer one is folded: C=2, N=1."""
    flow, doc, record = observe(chains, path3(tmp_path))
    assert listing(doc) == PATH3_LISTING and record["value"] == PATH3_RECORD
    assert surfaced_of(doc) == {"CHAIN-001": 0} and doc.remainder == 0


@pytest.mark.parametrize("name,candidates,expected", [
    pytest.param("severity comes before S-2's order", [F("S-1", "branch-b", 3, "Medium"), F("E-5", "branch-c", 3, "High")], "E-5", id="severity"),
    pytest.param("S-2 orders IDs by number, not as text", [F("S-10", "branch-b", 3, "High"), F("S-9", "branch-c", 3, "High")], "S-9", id="numeric"),
    pytest.param("S-2 orders prefixes before numbers", [F("E-2", "branch-b", 3, "High"), F("S-5", "branch-c", 3, "High")], "S-5", id="prefix"),
])
def test_tie_assembly_extends_to_the_first_candidate_by_severity_then_s2_order(chains, tmp_path, name, candidates, expected):
    """From one finding with two candidates on a layer, the chain takes the first in severity order, then S-2 order (S-3(c))."""
    project = Project(tmp_path, [F("T-9", "trunk-a", 1, "Critical")] + candidates, flows=[("trunk-a", c.comp) for c in candidates])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-9", expected], ["L1", "L3"], "Critical", "T-9")], name
    assert record["value"] == "chains written (1); candidates 1; surfaced 1", name


@pytest.mark.parametrize("second,third,expected,layers", [
    pytest.param("High", "High", "I-3", ["L1", "L7"], id="equal-severity-lower-id"),
    pytest.param("Critical", "High", "I-5", ["L1", "L2"], id="higher-severity-on-the-other-layer"),
])
def test_tie_assembly_chooses_between_layers_by_the_same_order(chains, tmp_path, second, third, expected, layers):
    """Two candidates on two layers: the order is severity, then S-2, whichever layer it lands on."""
    project = Project(tmp_path, [F("I-1", "trunk-a", 1, "Critical"), F("I-5", "branch-b", 2, second), F("I-3", "branch-c", 7, third)],
                      flows=[("trunk-a", "branch-b"), ("trunk-a", "branch-c")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["I-1", expected], layers, "Critical", "I-1")]


def test_assembly_skips_a_candidate_on_a_layer_the_chain_already_has(chains, tmp_path):
    """The best candidate of a step may sit on a layer the chain has already used; the next one on a new layer is taken instead.

    T-1 and T-2 are both on L2 and both reach E-3 (L3), which reaches T-2 and T-1 (L2) and E-4 (L7). From T-1 the first candidate, T-2,
    is on T-1's own layer, so the chain goes on to E-4. T-2's chain does the same, so the two end at E-4: only T-2's surfaces, with
    one other chain converging on E-4 (S-3(c), (f)).
    """
    project = Project(tmp_path, [F("T-1", "source-s", 2, "High"), F("T-2", "source-x", 2, "Critical"), F("E-3", "bridge-b", 3, "Medium"),
                                 F("E-4", "sink-y", 7, "High")],
                      flows=[("source-s", "bridge-b"), ("source-x", "bridge-b"), ("bridge-b", "sink-y")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-2", "E-3", "E-4"], ["L2", "L3", "L7"], "Critical", "E-3"),
                            ("CHAIN-002", ["E-3", "T-2"], ["L3", "L2"], "Critical", "T-2"),
                            ("CHAIN-003", ["T-1", "E-3", "E-4"], ["L2", "L3", "L7"], "High", "E-3")]
    assert record["value"] == "chains written (3); candidates 3; surfaced 2"
    assert surfaced_of(doc) == {"CHAIN-001": 1, "CHAIN-002": 0}, "CHAIN-003 ends where CHAIN-001 does, so it is passed over"
    assert [row["Chain ID"] for row in doc.compact] == ["CHAIN-003"] and doc.remainder == 0


def test_tie_a_mutual_pair_keeps_the_higher_ranked_chain(chains, tmp_path):
    """Two chains that hold the same two findings, one each way round, are one chain: the one whose IDs rank first stays (S-3(d), (e))."""
    project = Project(tmp_path, [F("T-1", "source-a", 2, "High"), F("T-2", "sink-b", 3, "Critical")], flows=[("source-a", "sink-b")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-1", "T-2"], ["L2", "L3"], "Critical", "T-2")]
    assert record["value"] == "chains written (1); candidates 2; surfaced 1"


def test_tie_equal_ranks_order_their_ids_by_number_not_as_text(chains, tmp_path):
    """Two chains that tie on severity and layers are ordered by their IDs in S-2 order: T-9 comes before T-10 (S-2)."""
    project = Project(tmp_path, [F("T-10", "first-p", 1, "Critical"), F("S-3", "second-p", 3, "High"),
                                 F("T-9", "first-q", 1, "Critical"), F("S-4", "second-q", 3, "High")],
                      flows=[("first-p", "second-p"), ("first-q", "second-q")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-9", "S-4"], ["L1", "L3"], "Critical", "T-9"),
                            ("CHAIN-002", ["T-10", "S-3"], ["L1", "L3"], "Critical", "T-10")]
    assert record["value"] == "chains written (2); candidates 2; surfaced 2"


def test_tie_equal_ranks_order_prefixes_before_numbers(chains, tmp_path):
    """On a tie the prefix rank decides before the number does: a chain of T-50 ranks before one of I-1 (S-2: S, T, R, I, D, E)."""
    project = Project(tmp_path, [F("I-1", "first-p", 1, "Critical"), F("I-2", "second-p", 2, "High"),
                                 F("T-50", "first-q", 1, "Critical"), F("S-60", "second-q", 3, "High")],
                      flows=[("first-p", "second-p"), ("first-q", "second-q")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-50", "S-60"], ["L1", "L3"], "Critical", "T-50"),
                            ("CHAIN-002", ["I-1", "I-2"], ["L1", "L2"], "Critical", "I-1")]


def test_rank_orders_by_severity_before_layers(chains, tmp_path):
    """Chains rank by max severity, then by layer count: a Critical chain of two layers precedes a High chain of five (S-3(e))."""
    findings = [F("T-5", "a-one", 5, "High"), F("T-6", "a-two", 6, "Medium"), F("E-7", "a-three", 3, "Critical"),
                F("I-1", "b-one", 1, "Critical"), F("I-2", "b-two", 2, "Medium"),
                F("T-20", "c-one", 5, "High"), F("T-21", "c-two", 6, "Low"), F("E-22", "c-three", 3, "Low"), F("T-23", "c-four", 2, "Low"),
                F("T-24", "c-five", 1, "Low")]
    flows = [("a-one", "a-two"), ("a-two", "a-three"), ("b-one", "b-two"), ("c-one", "c-two"), ("c-two", "c-three"), ("c-three", "c-four"),
             ("c-four", "c-five")]
    flow, doc, record = observe(chains, Project(tmp_path, findings, flows=flows))
    assert listing(doc) == [("CHAIN-001", ["T-5", "T-6", "E-7"], ["L5", "L6", "L3"], "Critical", "T-6"),
                            ("CHAIN-002", ["I-1", "I-2"], ["L1", "L2"], "Critical", "I-1"),
                            ("CHAIN-003", ["T-20", "T-21", "E-22", "T-23", "T-24"], ["L5", "L6", "L3", "L2", "L1"], "High", "E-22")]
    assert record["value"] == "chains written (3); candidates 8; surfaced 3", "every finding with an outgoing link starts one chain (S-3(d))"


def test_consolidation_chains_without_a_critical_or_high_finding_are_dropped(chains, tmp_path):
    """The filter keeps a chain only if one member is Critical or High; the dropped one still counts as a candidate."""
    project = Project(tmp_path, [F("T-1", "source-a", 5, "Medium"), F("T-2", "sink-b", 6, "Low")], flows=[("source-a", "sink-b")])
    record = observe_nothing(chains, project)
    assert record["value"] == "0 chains passed filter (no chain with a Critical or High finding); candidates 1"


def test_consolidation_converging_chains_from_different_starts_both_stay(chains, tmp_path):
    """Two chains that meet at one terminal finding, with neither a run of the other, are two attack paths, and both stay (S-3(d))."""
    project = Project(tmp_path, [F("T-1", "arm-a0", 5, "High"), F("T-2", "arm-a1", 6, "Medium"), F("E-3", "arm-a2", 3, "High"),
                                 F("T-4", "arm-b0", 4, "Medium"), F("T-5", "arm-b1", 6, "High"), F("E-6", "arm-b2", 3, "High"),
                                 F("E-7", "sink-z", 7, "Critical")],
                      flows=[("arm-a0", "arm-a1"), ("arm-a1", "arm-a2"), ("arm-a2", "sink-z"), ("arm-b0", "arm-b1"), ("arm-b1", "arm-b2"),
                             ("arm-b2", "sink-z")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-1", "T-2", "E-3", "E-7"], ["L5", "L6", "L3", "L7"], "Critical", "E-3"),
                            ("CHAIN-002", ["T-4", "T-5", "E-6", "E-7"], ["L4", "L6", "L3", "L7"], "Critical", "T-5")]
    assert record["value"] == "chains written (2); candidates 6; surfaced 1", "the tails fold: six candidates, two chains"
    assert surfaced_of(doc) == {"CHAIN-001": 1} and [row["Chain ID"] for row in doc.compact] == ["CHAIN-002"]


def test_surfacing_takes_one_chain_per_terminal_finding_and_counts_the_others(chains, tmp_path):
    """Three chains end at one finding: the best surfaces with converging 2, and the others keep a compact row (S-3(f))."""
    project = Project(tmp_path, [F("T-1", "start-one", 1, "High"), F("T-2", "start-two", 6, "High"), F("E-3", "start-three", 6, "High"),
                                 F("E-9", "terminal", 3, "Critical")],
                      flows=[("start-one", "terminal"), ("start-two", "terminal"), ("start-three", "terminal")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-1", "E-9"], ["L1", "L3"], "Critical", "E-9"),
                            ("CHAIN-002", ["T-2", "E-9"], ["L6", "L3"], "Critical", "E-9"),
                            ("CHAIN-003", ["E-3", "E-9"], ["L6", "L3"], "Critical", "E-9")]
    assert record["value"] == "chains written (3); candidates 3; surfaced 1", "fewer than five terminals: fewer than five surface"
    assert surfaced_of(doc) == {"CHAIN-001": 2} and doc.remainder == 0 and len(doc.compact) == 2


def test_surfacing_stops_at_five(chains, tmp_path):
    """Six chains with six terminal findings: five surface and the sixth has a compact row (S-3(f))."""
    flow, doc, record = observe(chains, plain_islands(tmp_path, 6))
    assert record["value"] == "chains written (6); candidates 6; surfaced 5"
    assert list(surfaced_of(doc)) == ["CHAIN-%03d" % k for k in range(1, 6)] and [r["Chain ID"] for r in doc.compact] == ["CHAIN-006"]
    assert set(surfaced_of(doc).values()) == {0}


# =============================================================================
# 10. The chain-breaking target (orchestrator.md Step 4; ADR-050 D13)
# =============================================================================


def test_breaking_two_findings_take_the_higher_severity_and_on_a_tie_the_first(chains, tmp_path):
    """Of two findings the higher severity is the target, and the initial exploit when they are equal."""
    findings = [F("I-1", "a-one", 1, "High"), F("I-2", "a-two", 2, "High"), F("I-3", "b-one", 1, "Critical"), F("I-4", "b-two", 2, "High"),
                F("I-5", "c-one", 1, "High"), F("I-6", "c-two", 2, "Critical")]
    project = Project(tmp_path, findings, flows=[("a-one", "a-two"), ("b-one", "b-two"), ("c-one", "c-two")])
    flow, doc, record = observe(chains, project)
    assert [(c[1], c[4]) for c in listing(doc)] == [(["I-3", "I-4"], "I-3"), (["I-5", "I-6"], "I-6"), (["I-1", "I-2"], "I-1")]


def test_breaking_three_findings_take_the_middle_one(chains, tmp_path):
    """Of three findings the middle one is the target, whatever the severities."""
    project = Project(tmp_path, [F("T-1", "step-one", 5, "Critical"), F("T-2", "step-two", 6, "Low"), F("E-3", "step-three", 3, "Critical")],
                      flows=[("step-one", "step-two"), ("step-two", "step-three")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-1", "T-2", "E-3"], ["L5", "L6", "L3"], "Critical", "T-2")]


def test_breaking_four_findings_tied_on_centrality_take_the_earlier_position(chains, tmp_path):
    """Of four findings the two middle ones tie on i x (n-1-i); equal severities then give the earlier position. The chain-cap oracle
    holds the other tie-break, the higher severity."""
    project = Project(tmp_path, [F("T-1", "step-one", 5, "High"), F("T-2", "step-two", 6, "High"), F("E-3", "step-three", 3, "High"),
                                 F("E-4", "step-four", 7, "Critical")],
                      flows=[("step-one", "step-two"), ("step-two", "step-three"), ("step-three", "step-four")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-1", "T-2", "E-3", "E-4"], ["L5", "L6", "L3", "L7"], "Critical", "T-2")]
    assert record["value"] == "chains written (1); candidates 3; surfaced 1"


def test_breaking_five_findings_take_the_center_whatever_the_severities(chains, tmp_path):
    """Of five findings the center scores highest (2 x 2), so it is the target even though a later intermediate has a higher severity."""
    project = Project(tmp_path, [F("T-20", "step-one", 5, "High"), F("T-21", "step-two", 6, "Low"), F("E-22", "step-three", 3, "Low"),
                                 F("T-23", "step-four", 2, "Medium"), F("T-24", "step-five", 1, "Low")],
                      flows=[("step-one", "step-two"), ("step-two", "step-three"), ("step-three", "step-four"), ("step-four", "step-five")])
    flow, doc, record = observe(chains, project)
    assert listing(doc) == [("CHAIN-001", ["T-20", "T-21", "E-22", "T-23", "T-24"], ["L5", "L6", "L3", "L2", "L1"], "High", "E-22")]
    assert record["value"] == "chains written (1); candidates 5; surfaced 1"


def test_breaking_the_recommendation_is_the_targets_mitigation_verbatim(chains, tmp_path):
    """The chain-breaking control's recommendation is the target finding's Mitigation from Section 7, word for word."""
    mitigation = "Rotate the shared credential of the policy checker and alert on any reuse of an old one."
    flow, doc, record = observe(chains, path3(tmp_path, mitigation=mitigation))
    detail = doc.details["CHAIN-001"]
    assert detail.target == "T-2" and detail.recommendation == mitigation, detail.raw
    assert default_mitigation("T-1") not in detail.raw and default_mitigation("E-1") not in detail.raw, "only the target's Mitigation is used"


# =============================================================================
# 11. render: the file, the bound and the chain-cap oracle (S-3(g), FR-K4.1b)
# =============================================================================


def section7(text):
    """Section 7's rows by finding ID."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.strip() == "## 7. Recommended Actions")
    table = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("|"))
    return {row["Finding ID"]: row for row in read_table(lines, table)[1]}


def fresh_copy(run, destination):
    """A copy of a run directory that a test may change."""
    target = Path(destination) / "run"
    shutil.copytree(str(run.dir), str(target))
    return Run(target)


def content_lines(text):
    """The lines of a file that carry content: no blank line, and no ``---`` rule (a writer may add or drop those around a block)."""
    return [line for line in text.split("\n") if line.strip() and line.strip() != "---"]


def body_without_stamp(path):
    """A rendered file's lines but for the provenance comment, whose digest may cover the narratives' bytes."""
    return [line for line in Path(path).read_text(encoding="utf-8").split("\n") if not line.startswith("<!-- tachi-provenance")]


def structure_of(text):
    """What a reader's markdown parser would take for structure: heading lines, table rows and code-fence lines."""
    lines = text.split("\n")
    return (sum(1 for line in lines if line.startswith("#")), sum(1 for line in lines if line.lstrip().startswith("|")),
            sum(1 for line in lines if line.lstrip().startswith(("~~~", "```"))))


_CAP = {}


class BuiltCap(object):
    """The chain-cap run after plan, the narratives and render, built on first use, once, and then only read: copy it to change it.

    It builds lazily, on the first attribute a test reads, so that a failure shows in the test and not as an error at setup."""

    def __init__(self, module, factory, doc):
        self._module, self._factory, self.doc = module, factory, doc

    def __getattr__(self, name):
        if name.startswith("_") or name == "doc":
            raise AttributeError(name)
        if "run" not in _CAP:
            run = copy_chain_cap(self._factory.mktemp("chain-cap"))
            flow = good_flow(self._module, run)
            _CAP.update(run=run, flow=flow, md=read_md(run.md.read_text(encoding="utf-8")), threats=run.text())
        return _CAP[name]


@pytest.fixture
def cap(chains, tmp_path_factory, cap_doc):
    return BuiltCap(chains, tmp_path_factory, cap_doc)


def test_render_chain_cap_frontmatter_and_sections(cap):
    """attack-chains.md is schema 1.1 with the date, the three counts and the three sections in order (D15, S-3(g))."""
    assert cap.md.front == {"schema_version": "1.1", "date": DATE, "chain_count": "120", "surfaced_count": "5", "candidate_count": "136"}
    assert [line for line in cap.md.lines if line.startswith("## ")] == [
        "## 1. Chain Summary", "## 2. Chain Details", "## 3. Other Consolidated Chains"]
    assert cap.doc["frontmatter_counts"] == {"chain_count": 120, "surfaced_count": 5, "candidate_count": 136}


def test_render_chain_cap_shows_the_surfaced_chains_in_full(cap):
    """The five surfaced chains of the 120 have a detail section each, in rank order, with their members, roles, layers, severity,
    breaking target and converging count (S-3(f), (g))."""
    oracle = {c["id"]: c for c in cap.doc["chains"]}
    assert list(cap.md.details) == cap.doc["surfaced"] == [row["Chain ID"] for row in cap.md.summary]
    rows = section7(cap.threats)
    for cid, detail in cap.md.details.items():
        want = oracle[cid]
        assert [m["Finding ID"] for m in detail.members] == want["members"], cid
        assert [m["Role"] for m in detail.members] == (["initial_exploit"] + ["intermediate_cascade"] * (len(want["members"]) - 2)
                                                       + ["terminal_impact"]), cid
        assert [m["Component"] for m in detail.members] == [rows[i]["Component"] for i in want["members"]], cid
        assert [m["Severity"] for m in detail.members] == [rows[i]["Risk Level"] for i in want["members"]], cid
        assert split_arrow(detail.layers) == want["layers"] and detail.max == want["max_severity"], cid
        assert detail.surfaced == "Yes" and detail.converging == str(want["converging"]), cid
        assert detail.target == want["breaking_target"], cid
        assert detail.recommendation == rows[want["breaking_target"]]["Mitigation"], "verbatim from Section 7 (%s)" % cid
        assert detail.narrative, "a narrative for %s" % cid


def test_render_chain_cap_summary_rows_carry_today_s_columns_and_the_converging_count(cap):
    """Section 1 has one row per surfaced chain: today's columns and 'Converging Chains' (contracts/threat-model-records.md)."""
    header = cap.md.summary_header
    assert header[:6] == ["Chain ID", "Title", "Layers", "Max Severity", "Finding Count", "Chain-Breaking Target"] and "Converging Chains" in header
    oracle = {c["id"]: c for c in cap.doc["chains"]}
    for row in cap.md.summary:
        want = oracle[row["Chain ID"]]
        assert row["Layers"] == ARROW.join(want["layers"]) and row["Max Severity"] == want["max_severity"], row
        assert row["Finding Count"] == str(len(want["members"])) and row["Chain-Breaking Target"] == want["breaking_target"], row
        assert row["Converging Chains"] == str(want["converging"]), row
        assert row["Title"] == cap.md.details[row["Chain ID"]].title


def test_render_chain_cap_lists_exactly_100_compact_rows_in_rank_order(cap):
    """Section 3 holds one compact row for each other consolidated chain in rank order, at most 100 (S-3(g))."""
    assert cap.md.compact_header == ["Chain ID", "Layers", "Findings", "Max Severity", "Chain-Breaking Target"]
    assert cap.md.compact_raw == cap.doc["compact_rows"], "the compact rows differ from the oracle"
    ids = [row["Chain ID"] for row in cap.md.compact]
    assert len(ids) == 100 and ids == sorted(ids) and not set(ids) & set(cap.doc["surfaced"])


def test_render_chain_cap_the_last_line_states_the_remainder(cap):
    """After the rows, one last line says how many consolidated chains are not listed: 120 - 5 - 100 = 15 (S-3(g))."""
    assert cap.md.remainder == 15 and cap.md.last_content == cap.doc["remainder_line"] == REMAINDER_PREFIX + "15"


def test_render_chain_cap_a_chain_passed_over_for_a_shared_terminal_has_a_row_and_no_section(cap):
    """CHAIN-002 ends where CHAIN-001 does and ranks within the first places: it is not surfaced, so it is a compact row (S-3(f))."""
    assert cap.doc["skipped_for_a_shared_terminal"] == ["CHAIN-002"]
    everything = md_chains(cap.md)
    assert "CHAIN-002" not in cap.md.details and everything["CHAIN-002"]["surfaced"] is False
    assert everything["CHAIN-002"]["members"] == next(c["members"] for c in cap.doc["chains"] if c["id"] == "CHAIN-002")


def test_render_chain_cap_the_record_carries_the_three_counts(cap):
    """The outcome record is the consolidated, candidate and surfaced counts: chains written (120); candidates 136; surfaced 5."""
    record = the_record(cap.threats)
    assert record["value"] == cap.doc["outcome_record"] == "chains written (120); candidates 136; surfaced 5"
    assert cap.flow.ids == cap.doc["surfaced"], "plan printed the five surfaced chains that render then showed"


def test_render_chain_cap_stamps_the_file_as_attack_chains_py(cap):
    """The file ends in the provenance comment of ADR-050 D4, with renderer attack-chains.py and the shipped version."""
    assert cap.md.stamp is not None, "the last line of attack-chains.md is not a tachi-provenance comment: %r" % cap.md.lines[-3:]
    assert cap.md.stamp[0] == RENDERER and cap.md.stamp[1] == shipped_version()


@pytest.mark.parametrize("count", [3, 5, 6, 104, 105, 106])
def test_render_the_bound_holds_at_its_edges(chains, tmp_path, count):
    """N chains give S in full, min(100, N-S) compact rows and a last line for the rest: the edge is 105 chains (S-3(g), FR-K4.1b)."""
    project = plain_islands(tmp_path, count)
    flow, doc, record = observe(chains, project)
    surfaced = min(5, count)
    rows = min(100, count - surfaced)
    assert record["value"] == "chains written (%d); candidates %d; surfaced %d" % (count, count, surfaced)
    assert doc.front["chain_count"] == str(count) and doc.front["surfaced_count"] == str(surfaced) and doc.front["candidate_count"] == str(count)
    assert len(doc.details) == len(doc.summary) == surfaced
    assert [row["Chain ID"] for row in doc.compact] == ["CHAIN-%03d" % k for k in range(surfaced + 1, surfaced + rows + 1)]
    assert doc.remainder == count - surfaced - rows and doc.last_content == REMAINDER_PREFIX + str(count - surfaced - rows)
    must(run_check(chains, project), 0, "check on a file that meets the bound")


def without_agent_text(md):
    """attack-chains.md without what the agent wrote (the titles and the narratives) and without the stamp: the script's own output."""
    out, skipping = [], False
    for line in md.split("\n"):
        if line.startswith("<!-- tachi-provenance"):
            continue
        if line.startswith("#### Attack Progression"):
            out.append(line)
            skipping = True
            continue
        if skipping:
            if not line.startswith("#"):
                continue
            skipping = False
        if re.match(r"^### CHAIN-[0-9]{3,6}: ", line):
            line = line.partition(":")[0] + ":"
        elif line.startswith("| CHAIN-") and len(split_row(line)) == 7:
            cells = split_row(line)
            cells[1] = ""
            line = "|".join(cells)
        out.append(line)
    return out


def test_render_the_agents_text_changes_nothing_but_titles_and_narratives(chains, tmp_path):
    """Two runs on one finding set with different valid titles and narratives give files that differ only in those (US-2 #5)."""
    def project(name):
        return Project(tmp_path / name, [F("T-1", "source-s", 2, "High"), F("T-2", "source-x", 2, "Critical"), F("E-3", "bridge-b", 3, "Medium"),
                                         F("E-4", "sink-y", 7, "High")],
                       flows=[("source-s", "bridge-b"), ("source-x", "bridge-b"), ("bridge-b", "sink-y")])
    one, two = project("one"), project("two")
    good_flow(chains, one)
    good_flow(chains, two, texts={"CHAIN-001": ("Another title for the first chain", "A different story, told in other words, for the first chain."),
                                  "CHAIN-002": ("Another title for the second chain", "A different story, told in other words, for the second chain.")})
    assert one.md.read_text(encoding="utf-8") != two.md.read_text(encoding="utf-8")
    assert without_agent_text(one.md.read_text(encoding="utf-8")) == without_agent_text(two.md.read_text(encoding="utf-8"))
    assert one.threats.read_bytes() == two.threats.read_bytes()


def test_render_a_thousand_chains_keep_the_bound_and_the_numeric_order(chains, tmp_path):
    """1,000 chains that end at one finding: one is surfaced with converging 999, 100 have rows in S-2's numeric order (I-9, I-10, I-100),
    and the last line says 899 are not listed."""
    sources = [F("I-%d" % k, "feed-node", 3, "Critical") for k in range(1, 1001)]
    project = Project(tmp_path, sources + [F("I-1001", "portal-node", 7, "Critical")], flows=[("feed-node", "portal-node")])
    flow, doc, record = observe(chains, project)
    assert record["value"] == "chains written (1000); candidates 1000; surfaced 1"
    assert surfaced_of(doc) == {"CHAIN-001": 999} and doc.details["CHAIN-001"].members[0]["Finding ID"] == "I-1"
    firsts = [row["Findings"].split(ARROW.strip())[0].strip() for row in doc.compact]
    assert [row["Chain ID"] for row in doc.compact] == ["CHAIN-%03d" % k for k in range(2, 102)]
    assert firsts == ["I-%d" % k for k in range(2, 102)], "chains with equal severity and layers rank by S-2's numeric order of their IDs"
    assert doc.remainder == 899 and doc.front["chain_count"] == "1000" and doc.front["candidate_count"] == "1000"
    must(run_check(chains, project), 0, "check at a thousand chains")


def test_render_the_output_does_not_depend_on_where_the_run_is(chains, tmp_path):
    """Two identical runs in two directories give byte-identical attack-chains.md and threats.md: no path, clock or order leaks in."""
    one, two = path3(tmp_path / "one"), path3(tmp_path / "two")
    good_flow(chains, one)
    good_flow(chains, two)
    assert one.md.read_bytes() == two.md.read_bytes() and one.threats.read_bytes() == two.threats.read_bytes()


def test_render_a_second_render_changes_nothing(chains, tmp_path):
    """render twice on the same inputs: the record it wrote makes no input stale, and every file is byte for byte the same."""
    project = path3(tmp_path)
    good_flow(chains, project)
    before = project.files()
    must(run_render(chains, project), 0, "second render")
    assert project.files() == before


def test_render_writes_the_chain_file_and_the_record_and_nothing_else(chains, tmp_path):
    """render adds attack-chains.md and changes threats.md by its record alone; chains.json and narratives.json are left as they were."""
    project = path3(tmp_path)
    ids = surfaced_ids(must(run_plan(chains, project), 0, "plan").out)
    write_narratives(project, default_texts(ids))
    before, text = project.files(), project.text()
    must(run_render(chains, project), 0, "render")
    added, removed, modified = changed(before, project.files())
    assert added == {"attack-chains.md"} and modified == {"threats.md"} and not removed, (added, removed, modified)
    assert content_lines(without_record(project.text())) == content_lines(text), "render changed more of threats.md than its record"


def test_render_refuses_inputs_that_changed_since_plan(chains, tmp_path):
    """render exits 2 and writes nothing when Section 7 or the inventory changed after plan (stale digests, D13); a new plan accepts it."""
    for name in ("threats", "inventory"):
        project = path3(tmp_path / name)
        ids = surfaced_ids(must(run_plan(chains, project), 0, "plan").out)
        write_narratives(project, default_texts(ids))
        if name == "threats":
            project.set_text(make_threats([F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Critical"),
                                           F("E-1", "agent-core", 3, "Critical")]))
        else:
            project.inventory.write_text(make_inventory(project.components, project.flows + [("agent-core", "ingest-gateway")]), encoding="utf-8")
        before = project.files()
        must(run_render(chains, project), 2, "render after a change to the %s" % name)
        assert project.files() == before and not project.md.exists(), "a refused render must change nothing (%s)" % name
        good_flow(chains, project)
        assert read_md(project.md.read_text(encoding="utf-8")).front["chain_count"] == "1", name


def test_render_refuses_a_chains_json_it_cannot_read(chains, tmp_path):
    """A chains.json that is not valid JSON is refused with exit 1 or 2 and no traceback, and render writes nothing."""
    project = path3(tmp_path)
    ids = surfaced_ids(must(run_plan(chains, project), 0, "plan").out)
    write_narratives(project, default_texts(ids))
    project.chains_json.write_text("{ this is not json", encoding="utf-8")
    before = project.files()
    must(run_render(chains, project), (1, 2), "render")
    assert project.files() == before and not project.md.exists()


@pytest.mark.parametrize("extra,why", [
    pytest.param("CHAIN-999", "an ID that no chain has", id="unknown-id"),
    pytest.param("CHAIN-003", "a consolidated chain that did not surface", id="not-surfaced"),
])
def test_render_refuses_narratives_for_chains_that_are_not_surfaced(chains, tmp_path, extra, why):
    """chains/narratives.json maps each surfaced chain ID, and only those: render exits 2 for any other (D13)."""
    project = Project(tmp_path, [F("T-1", "source-s", 2, "High"), F("T-2", "source-x", 2, "Critical"), F("E-3", "bridge-b", 3, "Medium"),
                                 F("E-4", "sink-y", 7, "High")],
                      flows=[("source-s", "bridge-b"), ("source-x", "bridge-b"), ("bridge-b", "sink-y")])
    ids = surfaced_ids(must(run_plan(chains, project), 0, "plan").out)
    assert ids == ["CHAIN-001", "CHAIN-002"], "CHAIN-003 is consolidated but passed over, so it is not surfaced: %s" % ids
    texts = default_texts(ids)
    texts[extra] = ("A chain that must not have a narrative", NARRATIVE)
    write_narratives(project, texts)
    before = project.files()
    must(run_render(chains, project), 2, "render with narratives for %s" % why)
    assert project.files() == before and not project.md.exists()


# =============================================================================
# 12. Narratives: validation, the one rewrite and the fixed text (D13, D3, NFR-10)
# =============================================================================


def with_side_finding(root):
    """path3 plus one STRIDE finding that is on no chain, so a slot can name a real finding that is not a member."""
    return Project(root, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Medium"), F("E-1", "agent-core", 3, "Critical"),
                          F("S-77", "side-node", 4, "Low")],
                   flows=[("ingest-gateway", "policy-checker"), ("policy-checker", "agent-core")])


def render_after_a_rewrite(module, project, first, second):
    """D13's flow for a narrative that fails: render, the orchestrator rewrites the narratives once, render again.

    ``first`` and ``second`` map chain IDs to ``(title, narrative)``. Returns the two renders' results. The first may exit 0, 1 or 2
    (the orchestrator ignores them, R-24), and the second must exit 0 and leave ``attack-chains.md``.
    """
    ids = surfaced_ids(must(run_plan(module, project), 0, "plan").out)
    write_narratives(project, dict(default_texts(ids), **first))
    one = must(run_render(module, project), (0, 1, 2), "first render")
    write_narratives(project, dict(default_texts(ids), **second))
    two = must(run_render(module, project), 0, "second render")
    assert project.md.is_file(), "the second render left no attack-chains.md\n%s" % two.describe()
    return one, two


def test_narrative_slots_resolve_in_the_title_and_the_narrative(chains, tmp_path):
    """A slot in a title or a narrative becomes the value it names: the finding, its component, the chain's counts, a layer (D3)."""
    title = "From {{finding:T-1}} to {{finding:E-1}}"
    narrative = ("{{finding:T-1}} on {{name:component:T-1}} leads through {{finding:T-2}} to {{finding:E-1}} on {{name:component:E-1}}, "
                 "a path of {{count:members}} findings over {{count:layers}} layers that {{count:converging}} other chains share, "
                 "as the layer {{ref:L6}} shows.")
    flow, doc, record = observe(chains, path3(tmp_path), texts={"CHAIN-001": (title, narrative)})
    detail = doc.details["CHAIN-001"]
    assert detail.title == "From T-1 to E-1" and doc.summary[0]["Title"] == "From T-1 to E-1"
    assert detail.narrative == ("T-1 on ingest-gateway leads through T-2 to E-1 on agent-core, a path of 3 findings over 3 layers "
                                "that 0 other chains share, as the layer L6 shows.")
    assert "{{" not in doc.text, "no slot is left in the file"


def test_narrative_number_words_and_the_limits_themselves_are_valid(chains, tmp_path):
    """Number words pass the numeral ban, and a title of 120 characters and a narrative of 2,000 are within their limits (D13)."""
    title = "a" * 120
    opening = "Two-factor checks and one-time codes fail here."
    narrative = opening + " word" * ((2000 - len(opening)) // 5)
    narrative += "w" * (2000 - len(narrative))
    assert len(title) == 120 and len(narrative) == 2000
    flow, doc, record = observe(chains, path3(tmp_path), texts={"CHAIN-001": (title, narrative)})
    assert doc.details["CHAIN-001"].title == title and doc.details["CHAIN-001"].narrative == narrative


INVALID_NARRATIVES = {  # a failure, and a second text that fails the same rule (the orchestrator's one rewrite)
    "a numeral": ("The attacker needs 3 steps to reach the last finding.", "The intruder needs 4 steps to reach the last finding."),
    "a unicode numeral": ("The attacker needs ٣ steps to reach the last finding.", "The intruder needs ٤ steps to reach the last finding."),
    "an unterminated slot": ("The attacker reaches {{finding:T-1 and goes on to the end of the chain.",
                             "The intruder reaches {{finding:T-2 and goes on to the end of the chain."),
    "a slot kind that chains lack": ("The score of the chain is {{score:composite}} in this run.", "The grade of the chain is {{score:composite}} here."),
    "a count that chains lack": ("The chain holds {{count:evidence}} entries of evidence.", "The path holds {{count:evidence}} items of evidence."),
    "a finding that is not a member": ("The attacker also reaches {{finding:S-77}} on the way.", "The intruder also reaches {{finding:S-77}} on its way."),
    "a finding that does not exist": ("The attacker reaches {{finding:T-999}} on the way.", "The intruder reaches {{finding:T-998}} on its way."),
    "a component of a non-member": ("The attacker passes through {{name:component:S-77}} on the way.",
                                    "The intruder passes through {{name:component:S-77}} on its way."),
    "a narrative over 2,000 characters": (("word " * 401)[:2001], ("term " * 401)[:2001]),
}


@pytest.mark.parametrize("kind", sorted(INVALID_NARRATIVES))
def test_narrative_text_that_breaks_the_rules_is_replaced_by_the_fixed_text(chains, tmp_path, kind):
    """A narrative that fails validation twice (D13's one rewrite) never reaches the file: its chain shows a fixed narrative instead,
    and the first render's output names the chain whose narrative failed."""
    bad, again = INVALID_NARRATIVES[kind]
    project = with_side_finding(tmp_path)
    one, two = render_after_a_rewrite(chains, project, {"CHAIN-001": (TITLE, bad)}, {"CHAIN-001": (TITLE, again)})
    assert "CHAIN-001" in one.both, "the first render must name the chain whose narrative failed, so that the orchestrator rewrites it"
    text = project.md.read_text(encoding="utf-8")
    assert bad[:60].strip() not in text and again[:60].strip() not in text, "the invalid text reached the file (%s)" % kind
    assert read_md(text).details["CHAIN-001"].narrative.strip(), "the chain still has a narrative: the fixed one"
    assert the_record(project.text())["value"] == "chains written (1); candidates 2; surfaced 1", "the chain is still written"


@pytest.mark.parametrize("bad,again", [("a" * 121, "b" * 121), ("Chain 3", "Chain 4"),
                                       ("A title with {{finding:S-77}} in it", "Another title with {{finding:S-77}} in it")],
                         ids=["over-120", "a-numeral", "a-non-member"])
def test_narrative_a_bad_title_is_replaced_too(chains, tmp_path, bad, again):
    """A title is narrative text as well: 121 characters, a numeral or a non-member's slot fails it, and it never reaches the file."""
    project = with_side_finding(tmp_path)
    one, two = render_after_a_rewrite(chains, project, {"CHAIN-001": (bad, NARRATIVE)}, {"CHAIN-001": (again, NARRATIVE)})
    assert "CHAIN-001" in one.both, "the first render must name the chain whose title failed"
    text = project.md.read_text(encoding="utf-8")
    assert bad not in text and again not in text and read_md(text).details["CHAIN-001"].title.strip(), \
        "the bad title reached the file, or the chain has none"


def test_narrative_the_fixed_text_depends_on_the_members_only(chains, tmp_path):
    """The fallback is built from the chain's members, never from the failed text: two different failures give the same file."""
    texts = [("The attacker needs 3 steps.", "The attacker reaches {{finding:T-999}} on the way."),
             ("{{score:composite}} is the score of this chain.", ("word " * 401)[:2001])]
    files = []
    for k, (first, second) in enumerate(texts):
        project = with_side_finding(tmp_path / ("run%d" % k))
        render_after_a_rewrite(chains, project, {"CHAIN-001": (TITLE, first)}, {"CHAIN-001": (TITLE, second)})
        files.append(body_without_stamp(project.md))
    assert files[0] == files[1], "the fixed text must not carry any of the agent's failed text"


def test_narrative_the_one_rewrite_replaces_the_fixed_text(chains, tmp_path):
    """A narrative that failed once and is rewritten validly shows its rewrite: the file ends as if it had been valid from the start."""
    clean = with_side_finding(tmp_path / "clean")
    good_flow(chains, clean)
    project = with_side_finding(tmp_path / "rewritten")
    bad = ("Chain 3 needs 3 steps.", "The attacker needs 3 steps.")
    render_after_a_rewrite(chains, project, {"CHAIN-001": bad}, {})
    assert body_without_stamp(project.md) == body_without_stamp(clean.md), "the rewrite did not replace the fixed text"
    assert project.text() == clean.text()


def test_narrative_other_chains_keep_their_valid_narratives(chains, tmp_path):
    """One chain's failed narrative does not touch another chain's: validation is per chain (D3's per-field fallback)."""
    project = Project(tmp_path, [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical"),
                                 F("T-1", "source-a", 5, "High"), F("T-2", "sink-b", 6, "Critical")],
                      flows=[("gateway-a", "portal-b"), ("source-a", "sink-b")])
    good = ("A valid title for the second chain", "The attacker takes the second path, and its narrative is valid as it stands.")
    bad = ("A title that is valid", "The attacker needs 4 steps.")
    ids = surfaced_ids(must(run_plan(chains, project), 0, "plan").out)
    assert len(ids) == 2
    for texts in ({ids[0]: good, ids[1]: bad}, {ids[0]: good, ids[1]: ("Another title", "Still needs 5 steps.")}):
        write_narratives(project, texts)
        must(run_render(chains, project), (0, 1, 2), "render")
    doc = read_md(project.md.read_text(encoding="utf-8"))
    assert doc.details[ids[0]].title == good[0] and doc.details[ids[0]].narrative == good[1]
    assert "4 steps" not in doc.text and "5 steps" not in doc.text and doc.details[ids[1]].narrative.strip()


def test_narrative_hostile_text_is_neutralized(chains, tmp_path):
    """Markup, a pipe, a backtick, a heading, a fence or a table row inside a title or a narrative adds no structure and no raw HTML (NFR-10)."""
    hostile_title = "Alpha | <b>Beta</b> `gamma`\n## Injected heading"
    hostile_narrative = "First line of the story.\n# A heading the text tries to add\n| a | b |\n~~~\n```\n<script>alert</script> and a closing line."
    benign = path3(tmp_path / "benign")
    good_flow(chains, benign)
    project = path3(tmp_path / "hostile")
    flow, doc, record = observe(chains, project, texts={"CHAIN-001": (hostile_title, hostile_narrative)})
    assert "<b>" not in doc.text and "<script>" not in doc.text, "raw HTML reached the file"
    assert structure_of(doc.text) == structure_of(benign.md.read_text(encoding="utf-8")), "the text added a heading, a row or a fence"
    assert len(split_row(doc.summary_raw[0])) == len(doc.summary_header), "a pipe in the title split the summary row"
    assert [k for k in doc.details] == ["CHAIN-001"] and record["value"] == PATH3_RECORD


# =============================================================================
# 12b. Untrusted text from threats.md and the paths it is written to (NFR-10, D3, D4)
# =============================================================================


def test_set_text_from_section_7_is_escaped_where_it_is_written(chains, tmp_path):
    """A component or a mitigation that Section 7 writes with escaped markup or an escaped pipe is escaped again in the chain file:
    no raw markup, every table row keeps its cells, and the recommendation decodes to the mitigation."""
    component = "edge &#124; gateway &lt;i&gt;"  # decodes to: edge | gateway <i>
    mitigation = "Rotate keys &lt;b&gt;now&lt;/b&gt; and &#124; alert on reuse."  # decodes to: Rotate keys <b>now</b> and | alert on reuse.
    inventory = make_inventory([("edge | gateway <i>", 5), ("policy-checker", 6), ("agent-core", 3)],
                               [("edge | gateway <i>", "policy-checker"), ("policy-checker", "agent-core")])
    project = Project(tmp_path, [F("T-1", component, 5, "High"), F("T-2", "policy-checker", 6, "Medium", mit=mitigation),
                                 F("E-1", "agent-core", 3, "Critical")], inventory=inventory)
    flow, doc, record = observe(chains, project)
    assert record["value"] == PATH3_RECORD, "the decoded component name is the inventory's, so the chain forms"
    decode = shared_module("tachi_parsers").decode_references
    detail = doc.details["CHAIN-001"]
    assert "<i>" not in doc.text and "<b>" not in doc.text, "raw markup from Section 7 reached the file"
    rows = [line for line in detail.raw.split("\n") if line.lstrip().startswith("|")][2:]
    assert len(rows) == 3 and all(len(split_row(line)) == 6 for line in rows), "a pipe in a component split a Member Findings row: %s" % rows
    assert len(split_row(doc.summary_raw[0])) == len(doc.summary_header)
    assert decode(detail.members[0]["Component"]) == "edge | gateway <i>"
    assert decode(detail.recommendation) == "Rotate keys <b>now</b> and | alert on reuse."


@pytest.mark.parametrize("character", ["‮", " ", "‏", "\x1b", "\U000e0041"], ids=["bidi-override", "line-separator", "bidi-mark", "escape", "tag-character"])
def test_set_a_forbidden_character_in_section_7_never_reaches_the_chain_file(chains, tmp_path, character):
    """A control, bidi, line-separator or tag character (D3's strings rule) in a component or mitigation is refused or neutralized:
    attack-chains.md never carries it. A run may refuse the input instead (exit 2), and then writes no file."""
    project = Project(tmp_path, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy%schecker" % character, 6, "Medium",
                                                                       mit="Rotate it%snow and watch for reuse." % character),
                                 F("E-1", "agent-core", 3, "Critical")],
                      flows=[("ingest-gateway", "policy%schecker" % character), ("policy%schecker" % character, "agent-core")])
    run_flow(chains, project)
    if project.md.exists():
        assert character not in project.md.read_text(encoding="utf-8"), "a forbidden character from Section 7 reached attack-chains.md"


@pytest.mark.parametrize("target", ["attack-chains.md", ".tachi-build/chains/chains.json"])
def test_writes_never_go_through_a_symlink(chains, tmp_path, target):
    """A symlink where an output belongs is replaced or refused, and the file it points at is never written (ADR-050 D3's atomic write)."""
    project = path3(tmp_path)
    victim = tmp_path / "victim.txt"
    victim.write_bytes(b"keep me\n")
    link = project.dir / target
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(str(victim), str(link))
    except (OSError, NotImplementedError):
        pytest.skip("this platform cannot make a symlink")
    run_flow(chains, project)
    assert victim.read_bytes() == b"keep me\n", "a write went through the link and changed the file it points at"


# =============================================================================
# 13. The outcome record: its three forms and its place (D13, P-3, R-24)
# =============================================================================

OK_FINDINGS = [F("I-1", "gateway-a", 3, "High"), F("I-2", "portal-b", 7, "Critical")]
OK_FLOWS = [("gateway-a", "portal-b")]


@pytest.mark.parametrize("findings,flows,reason,candidates", [
    pytest.param([F("AG-1", "planner-agent", 3, "Critical"), F("LLM-1", "model-host", 1, "Critical")], [("planner-agent", "model-host")],
                 "no STRIDE findings", 0, id="no-stride-findings"),
    pytest.param([F("T-1", "gateway-a", 3, "High"), F("S-2", "portal-b", 3, "Critical")], [("gateway-a", "portal-b")],
                 "fewer than two layers with STRIDE findings", 0, id="one-layer"),
    pytest.param([F("T-1", "gateway-a", 2, "High"), F("I-2", "portal-b", 3, "Critical")], [("gateway-a", "portal-b")],
                 "no candidate links", 0, id="no-table-row"),
    pytest.param(OK_FINDINGS, [], "no candidate links", 0, id="no-flow"),
    pytest.param([F("T-1", "gateway-a", 5, "Medium"), F("T-2", "portal-b", 6, "Low")], [("gateway-a", "portal-b")],
                 "no chain with a Critical or High finding", 1, id="no-severe-finding"),
])
def test_record_zero_chains_states_its_reason_and_the_candidates(chains, tmp_path, findings, flows, reason, candidates):
    """No chain: '0 chains passed filter (<reason>); candidates C', with one of the four reasons, and no attack-chains.md (D13)."""
    project = Project(tmp_path, findings, flows=flows)
    record = observe_nothing(chains, project)
    assert record["value"] == "0 chains passed filter (%s); candidates %d" % (reason, candidates)
    assert reason in ZERO_REASONS
    must(run_check(chains, project), 0, "check on a zero-chain record with no file")


def skipped_without_section_7(root):
    return Project(root, OK_FINDINGS, flows=OK_FLOWS, threats=make_threats(OK_FINDINGS, section7=False))


def skipped_without_inventory(root):
    return Project(root, OK_FINDINGS, flows=OK_FLOWS, inventory=False)


def skipped_with_inventory(text):
    return lambda root: Project(root, OK_FINDINGS, flows=OK_FLOWS, inventory=text)


@pytest.mark.parametrize("build,reason", [
    pytest.param(skipped_without_section_7, "Section 7 unreadable", id="section-7-missing"),
    pytest.param(skipped_without_inventory, "inventory missing", id="inventory-missing"),
    pytest.param(skipped_with_inventory("this is not json {"), "inventory invalid", id="inventory-not-json"),
    pytest.param(skipped_with_inventory(make_inventory([("gateway-a", 3), ("portal-b", 7)], OK_FLOWS, schema="tachi.phase1-inventory/9")),
                 "inventory invalid", id="inventory-wrong-schema"),
    pytest.param(skipped_with_inventory(make_inventory([], [])), "inventory invalid", id="inventory-no-components"),
    pytest.param(skipped_with_inventory(make_inventory([("gateway a", 3), ("GATEWAY  A", 7), ("portal b", 7)], [])), "inventory invalid",
                 id="inventory-repeated-name"),
])
def test_record_skipped_when_an_input_is_unusable(chains, tmp_path, build, reason):
    """An unusable input gives 'skipped (<reason>)' with the script's own reason, never a traceback, and no attack-chains.md (R-24)."""
    project = build(tmp_path)
    flow = run_flow(chains, project)  # plan and render exit with 0, 1 or 2, and the orchestrator carries on
    assert not project.md.exists()
    assert the_record(project.text())["value"] == "skipped (%s)" % reason
    must(run_check(chains, project), 0, "check on a skipped record with no file")


@pytest.mark.parametrize("options,after", [
    pytest.param({}, "## 5. Coverage Matrix", id="before-section-5"),
    pytest.param({"section5": False}, "## Affected Assets", id="before-affected-assets"),
    pytest.param({"section5": False, "assets": False}, None, id="at-the-end"),
])
def test_record_placement(chains, tmp_path, options, after):
    """The record sits under an unnumbered '## Attack Chain Outcome' directly before '## 5. Coverage Matrix', else before
    '## Affected Assets', else at the end of the file; nothing else in threats.md moves (D13)."""
    project = Project(tmp_path, [F("T-1", "ingest-gateway", 5, "High"), F("T-2", "policy-checker", 6, "Medium"),
                                 F("E-1", "agent-core", 3, "Critical")],
                      flows=[("ingest-gateway", "policy-checker"), ("policy-checker", "agent-core")], **options)
    before = content_lines(project.text())
    good_flow(chains, project)
    text = project.text()
    where = record_context(text)
    assert where.before == RECORD_HEADING, "the record's heading is '%s', unnumbered: %r" % (RECORD_HEADING, where.before)
    assert where.after == after, "the record is followed by %r, not by %r" % (where.after, after)
    assert content_lines(without_record(text)) == before and text.count(RECORD_HEADING) == 1


def test_record_there_is_exactly_one_and_a_later_render_replaces_it(chains, tmp_path):
    """The record is upserted: a second run with another outcome leaves exactly one record, holding the new outcome (D13)."""
    project = path3(tmp_path)
    good_flow(chains, project)
    first = the_record(project.text())["value"]
    where = record_context(project.text()).after
    project.inventory.write_text(make_inventory(project.components, []), encoding="utf-8")
    flow = run_flow(chains, project)
    must(flow.plan, 0, "second plan")
    must(flow.render, 0, "second render")
    second = the_record(project.text())
    assert first == PATH3_RECORD and second["value"] == "0 chains passed filter (no candidate links); candidates 0"
    assert project.text().count(RECORD_HEADING) == 1 and record_context(project.text()).after == where


# =============================================================================
# 14. check: the pass rules, the rewrite, the quarantine and the hand-off (FR-K4.1b, R-24, RR6)
# =============================================================================


def set_record(run, value):
    lines = run.text().split("\n")
    lines[next(i for i, line in enumerate(lines) if RECORD_LINE.match(line))] = RECORD_PREFIX + value
    run.set_text("\n".join(lines))


def duplicate_record(run):
    lines = run.text().split("\n")
    at = next(i for i, line in enumerate(lines) if RECORD_LINE.match(line))
    run.set_text("\n".join(lines[:at + 1] + [lines[at]] + lines[at + 1:]))


def edit_md(run, edit):
    run.md.write_text(edit(run.md.read_text(encoding="utf-8")), encoding="utf-8")


def drop_chain(md, chain_id):
    """The file without one surfaced chain's summary row and detail section: a truncated write."""
    lines = md.split("\n")
    details = next(i for i, line in enumerate(lines) if line.strip() == "## 2. Chain Details")
    lines = [line for i, line in enumerate(lines) if not (i < details and line.startswith("| %s |" % chain_id))]
    start = next(i for i, line in enumerate(lines) if line.startswith("### %s:" % chain_id))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("### CHAIN-") or lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[:start] + lines[end:])


def compact_rows_range(lines):
    start = next(i for i, line in enumerate(lines) if line.strip() == "## 3. Other Consolidated Chains")
    first = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("|")) + 2
    last = first
    while last < len(lines) and lines[last].strip().startswith("|"):
        last += 1
    return first, last


def drop_first_compact_row(md):
    lines = md.split("\n")
    first, _ = compact_rows_range(lines)
    return "\n".join(lines[:first] + lines[first + 1:])


def add_compact_rows(md, count):
    """The rows of a writer that ignores the cap: ``count`` more rows, and no chains left over for the last line."""
    lines = md.split("\n")
    _, last = compact_rows_range(lines)
    known = max(int(row.split("|")[1].strip().partition("-")[2]) for row in lines[compact_rows_range(lines)[0]:last])
    extra = ["| CHAIN-%03d | L3 %s L7 | I-1 %s I-2 | High | I-2 |" % (known + k, ARROW.strip(), ARROW.strip()) for k in range(1, count + 1)]
    return "\n".join(lines[:last] + extra + lines[last:])


def set_remainder(md, value):
    return re.sub(r"(?m)^\*\*Consolidated chains not listed\*\*: [0-9]+$", REMAINDER_PREFIX + str(value), md)


def set_front(md, key, value):
    return re.sub(r"(?m)^%s: .*$" % re.escape(key), "%s: %s" % (key, value), md, count=1)


def tamper_unreadable(run):
    run.md.write_bytes(b"\xff\xfe\x00 this is not text \xc3\x28")


CHECK_CASES = [
    # id, what is done to the finished chain-cap output, the reason that check writes, whether attack-chains.md is renamed
    pytest.param(lambda run: run.set_text(without_record(run.text())), "no outcome recorded", True, id="no-record"),
    pytest.param(lambda run: set_record(run, "all chains were written"), "outcome record malformed", True, id="malformed-words"),
    pytest.param(lambda run: set_record(run, "chains written (0); candidates 0; surfaced 0"), "outcome record malformed", True,
                 id="malformed-no-chains-written"),
    pytest.param(lambda run: set_record(run, "chains written (120); candidates 119; surfaced 5"), "outcome record malformed", True,
                 id="malformed-fewer-candidates-than-chains"),
    pytest.param(lambda run: set_record(run, "chains written (120); candidates 136; surfaced 6"), "outcome record malformed", True,
                 id="malformed-more-than-five-surfaced"),
    pytest.param(lambda run: set_record(run, "chains written (120); candidates 136; surfaced 5 and more"), "outcome record malformed", True,
                 id="malformed-trailing-text"),
    pytest.param(lambda run: set_record(run, "skipped ()"), "outcome record malformed", True, id="malformed-empty-reason"),
    pytest.param(duplicate_record, "multiple outcome records", True, id="duplicated"),
    pytest.param(lambda run: run.md.unlink(), "attack-chains.md missing", False, id="file-missing"),
    pytest.param(tamper_unreadable, "attack-chains.md unreadable", True, id="file-unreadable"),
    pytest.param(lambda run: set_record(run, "0 chains passed filter (no candidate links); candidates 136"), "attack-chains.md unexpected", True,
                 id="zero-chains-but-a-file"),
    pytest.param(lambda run: set_record(run, "skipped (inventory missing)"), "attack-chains.md unexpected", True, id="skipped-but-a-file"),
    pytest.param(lambda run: edit_md(run, lambda md: drop_chain(md, "CHAIN-006")), "full chains 4 expected 5", True, id="a-full-chain-missing"),
    pytest.param(lambda run: edit_md(run, drop_first_compact_row), "compact rows 99 expected 100", True, id="a-compact-row-missing"),
    pytest.param(lambda run: edit_md(run, lambda md: set_remainder(add_compact_rows(md, 15), 0)), "compact rows 115 expected 100", True,
                 id="rows-over-the-cap"),
    pytest.param(lambda run: edit_md(run, lambda md: set_remainder(md, 14)), "remainder 14 expected 15", True, id="remainder-off-by-one"),
    pytest.param(lambda run: edit_md(run, lambda md: set_front(md, "chain_count", 121)), "frontmatter counts differ", True,
                 id="frontmatter-chain-count"),
    pytest.param(lambda run: edit_md(run, lambda md: set_front(md, "surfaced_count", 4)), "frontmatter counts differ", True,
                 id="frontmatter-surfaced-count"),
    pytest.param(lambda run: edit_md(run, lambda md: set_front(md, "candidate_count", 135)), "frontmatter counts differ", True,
                 id="frontmatter-candidate-count"),
]


def test_check_passes_a_consistent_output_and_changes_nothing(chains, cap, tmp_path):
    """check on the finished chain-cap output exits 0: the file parses, has 5 full chains, 100 rows and the remainder, and matches
    the record. It rewrites and renames nothing, and writes its hand-off file (status pass, no warning)."""
    run = fresh_copy(cap.run, tmp_path)
    before = run.files()
    result = must(run_check(chains, run), 0, "check")
    added, removed, modified = changed(before, run.files())
    assert added == {".tachi-build/threat-model/%s/checks/attack-chains.json" % PLAN_ID} and not removed and not modified, (added, removed, modified)
    assert_handoff(run, "pass")
    assert "chains written" in run.text() and not run.quarantined.exists()


@pytest.mark.parametrize("tamper,reason,quarantine", CHECK_CASES)
def test_check_rewrites_a_record_that_disagrees_with_the_artifacts(chains, cap, tmp_path, tamper, reason, quarantine):
    """A missing, malformed or inconsistent record becomes 'skipped (<what disagreed>)', and the chain file is renamed to
    attack-chains.inconsistent.md so that nothing reads it as complete. check warns, writes its hand-off, and exits 5 (D13, R-24)."""
    run = fresh_copy(cap.run, tmp_path)
    tamper(run)
    md_before = run.md.read_bytes() if run.md.exists() else None
    threats_before = run.text()
    result = must(run_check(chains, run), 5, "check")
    assert result.both.strip(), "check must warn when it rewrites a record"
    record = the_record(run.text())
    assert record["form"] == "skipped" and record["reason"] == reason, "the record reads %r, not 'skipped (%s)'" % (record["value"], reason)
    assert not run.md.exists(), "attack-chains.md must not stay under its own name"
    if quarantine:
        assert run.quarantined.read_bytes() == md_before, "attack-chains.inconsistent.md must hold the file as it was"
    else:
        assert not run.quarantined.exists()
    assert_handoff(run, "warn", outcome="skipped (%s)" % reason)
    assert content_lines(without_record(run.text())) == content_lines(without_record(threats_before)), "check changed more than the record"
    must(run_check(chains, run), 0, "a second check on the rewritten record")
    assert the_record(run.text())["value"] == "skipped (%s)" % reason


def test_check_a_rewritten_record_is_in_the_same_place_as_a_rendered_one(chains, cap, tmp_path):
    """When check has to write the record because none exists, it goes where render puts it: before '## 5. Coverage Matrix'."""
    run = fresh_copy(cap.run, tmp_path)
    run.set_text(without_record(run.text()))
    must(run_check(chains, run), 5, "check")
    where = record_context(run.text())
    assert where.before == RECORD_HEADING and where.after == "## 5. Coverage Matrix", (where.before, where.after)


def test_check_exit_2_writes_no_hand_off_file(chains, cap, tmp_path):
    """A usage error is exit 2, argparse's, and a check that exits 2 writes no hand-off file (part-files.md section 6)."""
    run = fresh_copy(cap.run, tmp_path)
    run.make_plan_dir()
    before = run.files()
    result = invoke(chains, ["check", "--run-dir", run.dir, "--plan"])
    assert result.code == 2, result.describe()
    assert run.files() == before and not run.handoff().exists()


# =============================================================================
# 15. What a process alone shows (H15)
# =============================================================================


def run_script(*argv):
    return subprocess.run([sys.executable, "-B", str(ENTRY)] + [str(a) for a in argv], capture_output=True, encoding="utf-8",
                          timeout=SUBPROCESS_TIMEOUT)


def test_exit_codes_come_from_a_real_interpreter(tmp_path):
    """The __main__ guard turns main's result into the exit status: plan, render and check run as scripts, one JSON object reaches
    stdout, errors reach stderr, and the codes are 0, 5 and 2."""
    if not ENTRY.is_file():
        pytest.fail("scripts/attack-chains.py does not exist yet (T116 and T117 write it to these tests). Behavior missing: "
                    "the entry's __main__ guard gives a real process its exit codes", pytrace=False)
    project = path3(tmp_path)
    project.make_plan_dir()
    planned = run_script("plan", "--run-dir", project.dir)
    assert planned.returncode == 0, planned.stderr
    assert isinstance(json.loads(planned.stdout), dict) and planned.stderr == ""
    write_narratives(project, default_texts(surfaced_ids(planned.stdout)))
    rendered = run_script("render", "--run-dir", project.dir)
    assert rendered.returncode == 0, rendered.stderr
    assert the_record(project.text())["value"] == PATH3_RECORD
    checked = run_script("check", "--run-dir", project.dir, "--plan", PLAN_ID)
    assert checked.returncode == 0, checked.stderr
    project.md.unlink()
    rewritten = run_script("check", "--run-dir", project.dir, "--plan", PLAN_ID)
    assert rewritten.returncode == 5 and (rewritten.stdout + rewritten.stderr).strip(), rewritten.stderr
    assert the_record(project.text())["value"] == "skipped (attack-chains.md missing)"
    usage = run_script("check")
    assert usage.returncode == 2 and usage.stderr.strip()
    version = run_script("--version")
    assert version.returncode == 0 and shipped_version() in (version.stdout + version.stderr)
