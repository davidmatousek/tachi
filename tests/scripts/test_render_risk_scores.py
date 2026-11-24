"""Goldens for ``scripts/render-risk-scores.py``, written before the script (F-374 T027; TDD).

They target ``contracts/cli.md`` (the CLI and the exit table), ``contracts/part-files.md`` (the scorer payload,
the stage record), ``contracts/module-signatures.md`` (the persisted-inputs format), ``contracts/sarif-result.md``
and ADR-050 D2 (field ownership), D3 (escaping, slots), D4 (the write order, failure, the stamp, declared paths),
D5 (arithmetic), D6 (batching), D7 and D8 (SARIF identity and membership), D9 (RESOLVED rows, Section 6, flags)
and D15 (schema 1.1), never an implementation. T028 writes the renderer to them (T045 and T046 add the recompute,
the flags, governance, peers, Section 2a and Section 6, and T050 emits the SARIF). Until then they fail: the
script does not exist. T041's SC-4 goldens on T040's variants (the seeded-error, legacy-format, tagged, id-reuse, ties
and regroup scenarios) are sections 17 to 27 below, and T049 puts FR-E.2's two-run model in ``test_sarif_identity.py``.

How they run (ADR-050 D16, H15): the entry is loaded through ``tests/conftest.py``'s ``_load_hyphenated_script``
and driven in-process through ``main(argv)``, so pytest-cov counts it. Nothing here starts a subprocess: the one
thing a process alone shows, the 3.9 refusal before any import, is ``test_runtime_floor_374.py``'s.

What these goldens assume of ``render-risk-scores.py`` (R1 follows them; where a contract left a form open the
test says ``# reading:`` and the architect rules it at integration):

1. **The CLI** is ``render-risk-scores.py --out DIR --plan ID --plan-digest HEX`` with ``--help`` and ``--version``
   (``contracts/cli.md``). ``main(argv=None) -> int``. The exit codes are the table's: 0 and 5 write both files,
   1 is a missing input, 2 a validation or guard failure (a digest or pointer mismatch), 4 a failed completeness
   or parity check. Anything else that is not 0 or 5 is a failure. The renderer never rewrites ``plan.json``.
2. **Where it reads.** The plan names ``threats.md`` (the reference set, Section 1's components, Section 2's zones,
   Section 4a's groups, the ``## Affected Assets`` block), the scoring date is the plan's ``params.scoring_date``,
   and the architecture candidate is the batch inputs' ``refs.architecture`` (else the body line, else the
   default). The parts are the current plan's ``done`` batches, each re-validated with ``tachi_parts.read_part``.
3. **Where it writes.** Both files go to ``<plan>/staged/`` first, are read back from disk and checked, and only
   then move onto the canonical names with ``os.replace``. The stage record is ``<plan>/stage-record.json``.
   stdout carries summary lines (not JSON), and every failure prints D4's ``TACHI RISK-SCORE FAILED:`` message.
4. **The files.** ``risk-scores.md`` is schema 1.1 with Sections 1 to 6 and 2a, ending in the stamp comment, and
   ``risk-scores.sarif`` is the shared emitter's file. The renderer's name in both stamps is the literal
   ``render-risk-scores.py`` (the architect's ruling), and the three digests (the two stamps and the stage
   record) are one value.

The renderer's rows are checked in two ways: ``GOLDEN`` holds literal numbers that
``test_harness_the_literal_goldens_equal_the_shipped_arithmetic`` re-derives from the shipped arithmetic (``tachi_scoring``), and every other test reads the literals, so a
wrong number in a test fails there first. Fixtures are synthetic (H8).

The groups of tests, by the task that turns them green:

* ``test_harness_*``: no renderer needed; they check the synthetic inputs and the literals.
* ``test_cli_*``: T028 (the entry, the exit table).
* ``test_md_*``: T028, T045 and T046 (the file's sections, rows, Section 6).
* ``test_sarif_*``: T050 (the shared emitter's file).
* ``test_agree_*`` and ``test_readers_*``: the ``.md``-``.sarif`` agreement and NFR-1's round trip.
* ``test_staged_*`` and ``test_failure_*``: D4's write order and the ``fail`` step (F2).
* ``test_record_*``: the stamp, the stage record and the declared-paths check.
* ``test_batching_*`` and ``test_determinism_*``: NFR-4 and NFR-2.
* ``test_issues_*`` and ``test_narrative_*``: Input Issues, the slots, the fallback and hostile text.
* ``test_template_*``: the 1.1 templates and the renderer agree (D15). They pass when T031 (lane C) lands, whatever
  the renderer does, and they fail until then.
* ``test_peers_*``: correlation groups. They need T044's routing (the planner leaves a peer out of the plan) and
  T048's parser, so they fail first on that precondition until both land.
* ``test_variants_*``, ``test_sc4_*``, ``test_ruling_*``, ``test_s13_*``, ``test_regroup_*``, ``test_baseline_*``,
  ``test_rr1_*``, ``test_vocabulary_*`` (T041, sections 17 to 25): each scenario's ``expected-outcomes.json``
  (``tachi.fixture-expected/1``) is the golden, so a regenerated variant flows through and no test restates a value.
  They fail until T045 and T046 land. ``test_harness_*`` and ``test_rules_*`` in those sections need no renderer: the
  first check the outcomes files and this module's readers, the second drive ``tachi_scoring_rules`` on the
  scenarios' baselines. ``basis`` ``pinned`` and ``derived`` flags are required, ``optional`` ones may be absent.
* ``test_carry_*``, ``test_readback_*``, ``test_refusal_*`` and ``test_backstop_*`` (section 28, W3's P0-1 and P0-4): a prose
  line that would forge structure, the from-disk read-back through ``read_baseline_scores``, a forbidden character in an
  input (exit 2, at intake) and in a staged file (exit 4, the whole-file backstop).
* ``test_fallback_*``, ``test_cli_*`` and ``test_sarif_*`` (section 29, W3's P0-3, P0-7 and P0-8): D8's ``threats.sarif`` fallback on
  copies of three shipped samples (the modern form, a file whose correlation groups have no ID, and the legacy ``properties.id``
  form), the plan's own ``refs``, and ``message.markdown`` written for an empty mitigation.

Standard library and pytest only, and Python 3.9 syntax.
"""
from __future__ import annotations

import ast
import collections
import contextlib
import copy
import datetime
import functools
import hashlib
import inspect
import io
import json
import math
import os
import re
import shutil
import sys
import time
import types
from decimal import Decimal
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common as sc  # noqa: E402  -- after the sys.path mutation
import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402
import tachi_scoring as ts  # noqa: E402
import tachi_scoring_rules as rules  # noqa: E402

RENDERER = SCRIPTS_DIR / "render-risk-scores.py"
GATED_SUBSET = REPO_ROOT / "tests" / "scripts" / "fixtures" / "large_arch" / "gated-subset"

STAGE = "risk-score"
MD, SARIF = "risk-scores.md", "risk-scores.sarif"
TOOL = "tachi-risk-scorer"
DATE = "2026-11-22"
# The stamp's renderer is the installed file name, with .py, as one literal in the markdown comment and in SARIF's
# tachi_provenance (architect, cli.md "The stamp's renderer"); it matches INSTALL_MANIFEST.md and REQUIRED_SCRIPT_NAMES.
RENDERER_NAME = "render-risk-scores.py"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}\Z")
DASH = "—"

# =============================================================================
# 1. The synthetic project: components, zones, findings and their goldens
# =============================================================================
#
# Nine open findings on six components in four zones, and three RESOLVED ones. They were chosen so that one
# render shows: all four bands; a four-way tie at 5.9 that S-2's order breaks (S-2 before S-10 by number, then
# T-1, then AG-1 by prefix); a mean that rounds half-up (7.25 gives 7.3); a composite whose sum ends in 5
# (5.875 gives 5.9); a reachability that a keyword raises, one that the architecture counts clamp at the zone's
# floor, and one that they pull below the floor; a leading-zero ID (AGP-01 compares as AGP-1); a component of
# 36 characters (the table shortens it); a threat over 60 characters; markup, a backtick and a ``{{`` in one
# threat; and non-ASCII text.

LONG_COMPONENT = "model-gateway-for-hosted-completions"  # 36 characters: Section 2 shortens it to 27 and "..."

# (zone, the label Section 2 gives its trust level, the level the agent writes, its components).
ZONES = (
    ("Internet Clients", "Untrusted", "Untrusted", ("client-portal",)),
    ("Edge DMZ", "Semi-trusted", "Semi-Trusted", ("edge-gateway", "auth-broker")),
    ("Agent Runtime Zone", "Trusted", "Trusted", ("planner-agent", LONG_COMPONENT)),
    ("Data Zone", "Trusted", "Trusted", ("vector-store",)),
)
COMPONENTS = {  # name -> (DFD type, MAESTRO layer)
    "client-portal": ("External Entity", "L7 " + DASH + " Agent Ecosystem"),
    "edge-gateway": ("Process", "L4 " + DASH + " Deployment Infrastructure"),
    "auth-broker": ("Process", "L6 " + DASH + " Security and Compliance"),
    "planner-agent": ("Process", "L3 " + DASH + " Agent Framework"),
    LONG_COMPONENT: ("Process", "L1 " + DASH + " Foundation Model"),
    "vector-store": ("Data Store", "L2 " + DASH + " Data Operations"),
}
KIND_OF = {"External Entity": "external-entity", "Process": "process", "Data Store": "data"}  # the legacy generator's kinds
CATEGORY_NAME = {
    "S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information Disclosure", "D": "Denial of Service",
    "E": "Elevation of Privilege", "AG": "Agentic", "AGP": "Agentic", "LLM": "LLM", "OI": "LLM", "MI": "LLM", "TE": "Agentic",
}

HOSTILE_THREAT = ("Untrusted <b>markup</b> and a `backtick` and {{7*7}} reach the model through the gateway "
                  "with no filter in between.")


def spec(finding_id, component, threat, risk, status, vector, e, s, zone, trust, auth, net, metric=None, subscore=None):
    return {"id": finding_id, "component": component, "threat": threat, "risk": risk, "status": status,
            "vector": vector, "e": e, "s": s, "zone": zone, "trust": trust, "auth": auth, "net": net,
            "metric": metric, "subscore": subscore}


SPECS = [
    spec("S-2", "edge-gateway", "Shared tokens let callers impersonate each other.", "High", "NEW",
         "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4), "Edge DMZ", "Semi-Trusted", 1, 0,
         metric={"AV": "Reachable over the network."}, subscore={"known_techniques": "Documented in public write-ups."}),
    spec("S-10", "auth-broker", "Étienne's service token " + DASH + " long-lived and shared " + DASH + " is accepted at the broker.",
         "Medium", "UPDATED", "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N", (6, 6, 6, 6), (4, 4, 4, 4),
         "Edge DMZ", "Semi-Trusted", 0, 0),
    spec("T-1", "auth-broker", "Backups of session grants are writable by operators.", "High", "UNCHANGED",
         "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L", (6, 6, 6, 6), (5, 5, 5, 5), "Edge DMZ", "Semi-Trusted", 1, 0),
    spec("E-3", "edge-gateway", "Admin routes skip the role check.", "High", "NEW",
         "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H", (6, 6, 6, 6), (5, 5, 5, 5), "Edge DMZ", "Semi-Trusted", 1, 1),
    spec("E-5", "client-portal", "Role claims in tokens presented to the portal are trusted without a second check, "
         "so any caller can act as an administrator.", "Critical", "NEW",
         "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H", (9, 9, 9, 9), (9, 8, 9, 8), "Internet Clients", "Untrusted", 0, 0),
    spec("AG-1", "planner-agent", "Memory entries written by the planner are trusted on later runs.", "Medium", "NEW",
         "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L", (5, 4, 5, 4), (4, 4, 4, 4), "Agent Runtime Zone", "Trusted", 0, 0),
    spec("AGP-01", "vector-store", "Worker agents coordinate through a shared bus and accept each other's instructions "
         "without verification.", "High", "NEW",
         "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L", (9, 8, 9, 8), (8, 8, 8, 8), "Data Zone", "Trusted", 0, 0),
    spec("LLM-4", LONG_COMPONENT, HOSTILE_THREAT, "Medium", "NEW",
         "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N", (7, 7, 7, 7), (5, 5, 5, 5), "Agent Runtime Zone", "Trusted", 2, 0),
    spec("R-1", "planner-agent", "Actions taken through the portal are logged without the acting identity.", "Low", "UPDATED",
         "CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:L/I:N/A:N", (2, 2, 2, 2), (2, 2, 2, 2), "Agent Runtime Zone", "Trusted", 0, 0),
]

# Section 4c. None of these IDs is open, and no open threat names one.
RESOLVED = [
    ("S-1", "legacy-gateway", "An unauthenticated callback route accepted requests from anyone.", "High", "Component removed from the architecture"),
    ("T-3", "edge-gateway", "Exports were writable by operators.", "Medium", "Threat no longer applies to the component"),
    ("LLM-2", "legacy-gateway", "Prompt content was logged and replayed to other users.", "Low", "Component removed from the architecture"),
]
RESOLVED_IDS = ["S-1", "T-3", "LLM-2"]  # in S-2 order

# What the renderer computes for each open finding: (CVSS, exploitability, scalability, reachability, composite, band).
# Derived by hand from the contract, and re-derived from the shipped arithmetic by the first harness test.
#   reachability: a trust level's baseline (9.0, 5.5, 2.5), plus a zone-name keyword (+0.5 for "internet" and
#   "client", "dmz"), less 1.5 per authentication layer and 1.0 per network boundary (three of each at most),
#   then clamped to the trust level's range (8.0-10.0, 4.0-7.0, 1.0-4.0) and rounded to one decimal.
GOLDEN = {
    "E-5": ("9.9", "9.0", "8.5", "10.0", "9.4", "Critical"),  # 9.0 + 1.0 = 10.0
    "AGP-01": ("9.9", "8.5", "8.0", "2.5", "7.7", "High"),    # 3.465 + 2.55 + 1.2 + 0.5 = 7.715
    "E-3": ("9.9", "6.0", "5.0", "4.0", "6.8", "Medium"),     # 5.5 + 0.5 - 1.5 - 1.0 = 3.5, raised to the floor
    "LLM-4": ("9.3", "7.0", "5.0", "1.0", "6.3", "Medium"),   # 2.5 - 3.0 = -0.5, raised to the floor
    "S-2": ("8.2", "5.0", "4.0", "4.5", "5.9", "Medium"),     # 5.87
    "S-10": ("6.5", "6.0", "4.0", "6.0", "5.9", "Medium"),    # 5.875: a sum that ends in 5 rounds up
    "T-1": ("7.1", "6.0", "5.0", "4.5", "5.9", "Medium"),     # 5.935
    "AG-1": ("9.9", "4.5", "4.0", "2.5", "5.9", "Medium"),    # 5.915
    "R-1": ("1.8", "2.0", "2.0", "2.5", "2.0", "Low"),        # 2.03
}
ORDER = ["E-5", "AGP-01", "E-3", "LLM-4", "S-2", "S-10", "T-1", "AG-1", "R-1"]  # composite descending, then S-2
OPEN_IDS = list(ORDER)
S2_ORDER = ["S-2", "S-10", "T-1", "R-1", "E-3", "E-5", "AG-1", "AGP-01", "LLM-4"]
GOVERNANCE = {  # band -> (SLA, disposition, the review date for DATE)
    "Critical": ("24h", "Mitigate", "2026-11-23"),
    "High": ("7d", "Mitigate", "2026-11-29"),
    "Medium": ("30d", "Review", "2026-12-22"),
    "Low": ("90d", "Review", "2027-02-20"),
}
BAND_COUNTS = {"Critical": 1, "High": 1, "Medium": 6, "Low": 1}
PERCENTAGES = {"Critical": 11, "High": 11, "Medium": 67, "Low": 11}  # largest remainder over 9 (ADR-050 D5): 66.67 gets the point

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
METRIC_LABEL = {"AV": "Attack Vector (AV)", "AC": "Attack Complexity (AC)", "PR": "Privileges Required (PR)",
                "UI": "User Interaction (UI)", "S": "Scope (S)", "C": "Confidentiality (C)", "I": "Integrity (I)",
                "A": "Availability (A)"}
SUBSCORE_LABEL = {"known_techniques": "Known Techniques", "attack_complexity": "Attack Complexity",
                  "tooling_availability": "Tooling Availability", "skill_level": "Skill Level",
                  "scriptability": "Scriptability", "target_scope": "Target Scope",
                  "resource_requirements": "Resource Requirements", "detection_difficulty": "Detection Difficulty"}

# The agent's narrative: digits only through slots (ADR-050 D3's table for the scorer).
RATIONALE = {
    "cvss": "The base score is {{score:cvss_base}} for {{name:component}}.",
    "exploitability": "Public techniques give a mean of {{score:exploitability}}.",
    "scalability": "Repeatable at scale, with a mean of {{score:scalability}}.",
    "reachability": "{{name:zone}} yields {{score:reachability}}, with {{count:auth_barriers}} authentication layers "
                    "and {{count:network_boundaries}} network boundaries.",
}

SECTION_2_HEADER = ["ID", "Source", "Component", "Threat", "CVSS", "Exploit.", "Scale.", "Reach.", "Composite",
                    "Severity", "SLA", "Disposition", "Flags"]
SECTION_4_HEADER = ["ID", "Severity", "Owner", "SLA", "Disposition", "Review Date"]
SECTION_TITLES = ["## 1. Executive Summary", "## 2. Scored Threat Table", "## 2a. Resolved Findings",
                  "## 3. Dimensional Breakdown", "## 4. Governance Fields", "## 5. Scoring Methodology",
                  "## 6. Score Integrity"]
SECTION_6_PARTS = ["### Integrity Summary", "### Score Flags", "### Input Issues", "### Scoring Inputs"]
EARLIER_MD = b"# the earlier run's markdown\n"
EARLIER_SARIF = b'{"earlier": "run"}\n'


def canon(finding_id):
    return tp.canonical_finding_id(finding_id)


def s2_key(finding_id):
    return tp.finding_sort_key(finding_id)


def truncate(text, limit):
    """Output-formatting's rule: over ``limit`` characters, keep ``limit - 3`` and append three dots."""
    return text if len(text) <= limit else text[:limit - 3] + "..."


def golden(finding_id):
    """The goldens of a finding by its canonical ID, whatever spelling the caller has (``AGP-01`` is ``AGP-1``)."""
    for key, value in GOLDEN.items():
        if canon(key) == canon(finding_id):
            return value
    raise KeyError(finding_id)


def by_id(finding_id, specs=None):
    for item in SPECS if specs is None else specs:
        if canon(item["id"]) == canon(finding_id):
            return item
    raise KeyError(finding_id)


def mitigation_of(item):
    """The Mitigation cell that ``make_threats_md`` writes for a finding: the reference set's mitigation text."""
    return "Mitigation text for %s." % item["id"]


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- the agent's part

def scorer_item(item, rationale=None):
    """One valid ``risk-score`` item (``contracts/part-files.md``) for a synthetic finding."""
    out = {
        "finding_id": item["id"],
        "cvss_vector": item["vector"],
        "exploitability": dict(zip(tp.SUBSCORE_NAMES[:4], item["e"])),
        "scalability": dict(zip(tp.SUBSCORE_NAMES[4:], item["s"])),
        "reachability": {"zone": item["zone"], "trust_level": item["trust"], "auth_barriers": item["auth"],
                         "network_boundaries": item["net"]},
        "rationale": dict(RATIONALE if rationale is None else rationale),
    }
    if item.get("metric"):
        out["metric_rationale"] = dict(item["metric"])
    if item.get("subscore"):
        out["subscore_rationale"] = dict(item["subscore"])
    return out


def lookup_for(item, composite=None):
    """The slot lookup the renderer must give a finding: this item's rendered values (ADR-050 D3's table)."""
    cvss, e, s, r, comp, band = golden(item["id"]) if composite is None else composite
    sla, _disposition, review = GOVERNANCE[band]
    values = {("score", "cvss_base"): cvss, ("score", "exploitability"): e, ("score", "scalability"): s,
              ("score", "reachability"): r, ("score", "composite"): comp, ("band", "severity"): band,
              ("date", "scored"): DATE, ("date", "review"): review, ("name", "component"): item["component"],
              ("name", "zone"): item["zone"], ("count", "auth_barriers"): str(item["auth"]),
              ("count", "network_boundaries"): str(item["net"])}
    for name, number in zip(tp.SUBSCORE_NAMES, tuple(item["e"]) + tuple(item["s"])):
        values[("score", name)] = str(number)

    def lookup(kind, argument):
        return values.get((kind, argument))

    return lookup


def narrative(item, text, sink="cell"):
    """What the renderer writes for a narrative field of ``item``: the slots filled, then escaped."""
    return tp.resolve_narrative(text, STAGE, lookup_for(item), sink=sink)


# --------------------------------------------------------------------------- threats.md and the architecture file

def make_architecture_md():
    return ("# Synthetic platform: architecture\n\n"
            "A small invented system for the tests. Operators reach a portal, a gateway screens requests, a broker "
            "issues tokens, a planner agent works through a model gateway, and a vector store holds documents.\n\n"
            "No component in this description carries an asset-sensitivity tag.\n")


def make_threats_md(specs=None, resolved=None, groups=(), repeated=(), affected="block", body_line=None,
                    baseline_source=None):
    """A synthetic ``threats.md`` with the sections the renderer reads.

    ``groups`` is ``[(group ID, [member IDs])]`` for Section 4a. ``repeated`` is ``[(ID, component)]``: extra
    Section 7 rows for an ID the file already lists (the architect's duplicate form). ``affected`` is ``block``
    (a row of ``[]`` for every open finding), ``missing`` (no block) or ``stale`` (a block that misses one finding).
    """
    specs = SPECS if specs is None else specs
    resolved = RESOLVED if resolved is None else resolved
    lines = ["---", 'schema_version: "1.4"', 'date: "%s"' % DATE, 'input_format: "mermaid"',
             'classification: "confidential"', 'run_id: "2026-11-22T10-00-00"', "baseline:",
             "  source: %s" % ('"%s"' % baseline_source if baseline_source else "null"),
             "  date: null", "  finding_count: null", "  run_id: null", "coverage_gate:", '  status: "pass"',
             "  gaps: []", "---", "", "# Threat Model: Synthetic Platform", ""]
    if body_line:
        lines += [sc.format_architecture_source_line(body_line), ""]
    lines += ["## 1. System Overview", "", "A synthetic system for the tests.", "", "### Components", "",
              "| Component | Type | MAESTRO Layer | Description |", "|-----------|------|---------------|-------------|"]
    for name, (kind, layer) in COMPONENTS.items():
        lines.append("| %s | %s | %s | A synthetic %s. |" % (name, kind, layer, kind.lower()))
    lines += ["", "---", "", "## 2. Trust Boundaries", "", "### Trust Zones", "",
              "| Zone | Trust Level | Components |", "|------|-------------|------------|"]
    for zone, label, _level, members in ZONES:
        lines.append("| %s | %s | %s |" % (zone, label, ", ".join(members)))
    lines.append("")
    if groups:
        lines += ["## 4a. Correlated Findings", "", "| Group | Findings | Component | Threat Summary | Risk Level |",
                  "|-------|----------|-----------|----------------|------------|"]
        for group, members in groups:
            lines.append("| %s | %s | %s | Related threats on one component. | High |" % (group, ", ".join(members), by_id(members[0], specs)["component"]))
        lines.append("")
    if resolved:
        lines += ["## 4c. Resolved Findings", "", "| ID | Component | Threat | Last Risk Level | Resolution Reason |",
                  "|----|-----------|--------|-----------------|-------------------|"]
        lines += ["| %s | %s | %s | %s | %s |" % row for row in resolved]
        lines.append("")
    lines += ["## 6. Risk Summary", "", "The counts here are not read by the renderer.", "", "## 7. Recommended Actions", "",
              "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |",
              "|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for item in specs:
        prefix = item["id"].partition("-")[0]
        rows.append("| %s | %s | %s | %s | %s | %s | %s | %s | Mitigation text for %s. |" % (
            item["id"], item["status"], CATEGORY_NAME[prefix], DASH, item["component"], COMPONENTS[item["component"]][1],
            item["threat"], item["risk"], item["id"]))
    for finding_id, component in repeated:
        rows.append("| %s | NEW | Spoofing | %s | %s | %s | A second row for the same finding. | Low | Mitigation. |" % (
            finding_id, DASH, component, COMPONENTS[component][1]))
    lines += rows + [""]
    if affected != "missing":
        shown = [item["id"] for item in specs]
        if affected == "stale":
            shown = shown[:-1]
        lines += ["## Affected Assets", "", "| Finding ID | Affected Assets |", "|------------|-----------------|"]
        lines += ["| %s | [] |" % finding_id for finding_id in shown]
        lines.append("")
    return "\n".join(lines) + "\n"


def scope_of(threats_text):
    """``{component: (zone, the agent's trust level)}`` read from a threats.md, for the generic items."""
    levels = {"untrusted": "Untrusted", "semi-trusted": "Semi-Trusted", "trusted": "Trusted"}
    out = {}
    for row in tachi_parsers.parse_scope_data(threats_text)["trust_boundaries"]:
        for member in [m.strip() for m in row["components"].split(",") if m.strip()]:
            out[member] = (row["zone"], levels[row["trust-level"].strip().lower()])
    return out


def generic_item(finding_id, component, scope):
    """A valid item for any synthetic finding: its category's default vector and numbers from its ID."""
    prefix = finding_id.partition("-")[0]
    seed = sum(ord(char) for char in finding_id)
    zone, trust = scope[component]
    return spec(finding_id, component, "", "Medium", "NEW",
                ts.CATEGORY_DEFAULT_VECTORS[ts.category_for_prefix(prefix)],
                tuple(1 + (seed + 3 * n) % 9 for n in range(4)), tuple(1 + (seed + 5 * n) % 9 for n in range(4)),
                zone, trust, seed % 3, (seed // 3) % 2)


# =============================================================================
# 2. Reading the output
# =============================================================================

_REFERENCE = re.compile("|".join(re.escape(reference) for reference in tp.ESCAPE_REFERENCES))


def decode(text):
    """ADR-050 D3's closed decoder: exactly the nine references in ``tp.ESCAPE_REFERENCES``, in one left-to-right pass."""
    return _REFERENCE.sub(lambda match: tp.ESCAPE_REFERENCES[match.group(0)], text)


def _level(line):
    """A heading's level (the count of leading ``#`` followed by a space), or 0 for any other line."""
    stripped = line.lstrip("#")
    hashes = len(line) - len(stripped)
    return hashes if hashes and stripped.startswith(" ") else 0


def split_headings(md, prefix):
    """``[(heading line, body text)]`` for every heading that starts with ``prefix`` (``## `` or ``### ``), in order.

    A body runs to the next heading of the same or a higher level, so a ``###`` subsection keeps its ``####`` blocks.
    """
    lines = md.split("\n")
    level = len(prefix.split(" ")[0])
    heads = [(n, line) for n, line in enumerate(lines) if _level(line)]
    found = []
    for index, (n, line) in enumerate(heads):
        if not line.startswith(prefix):
            continue
        end = len(lines)
        for later, other in heads[index + 1:]:
            if _level(other) <= level:
                end = later
                break
        found.append((line, "\n".join(lines[n + 1:end])))
    return found


def section(md, title):
    """The body of the one ``## `` section whose heading starts with ``title``."""
    found = split_headings(md, "## ")
    matches = [body for heading, body in found if heading.startswith(title)]
    assert len(matches) == 1, "expected one section %r, found %d (headings: %s)" % (title, len(matches), [h for h, _ in found])
    return matches[0]


def has_section(md, title):
    return any(heading.startswith(title) for heading, _ in split_headings(md, "## "))


def tables(body):
    """Every markdown table in ``body``: ``[(header cells, [row cells])]``, cells decoded after the split on raw ``|``."""
    found, current = [], None
    for line in body.split("\n"):
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1):
            current = None
            continue
        raw = [cell.strip() for cell in stripped[1:-1].split("|")]
        if current is None:
            current = ([decode(cell) for cell in raw], [])
            found.append(current)
        elif all(re.fullmatch(r":?-+:?", cell) for cell in raw):
            continue
        else:
            current[1].append([decode(cell) for cell in raw])
    return found


def table_of(body, first_column=None):
    """The first table in ``body``, or the first whose header starts with ``first_column``, as ``(header, rows)``."""
    for header, rows in tables(body):
        if first_column is None or header[0] == first_column:
            return header, rows
    raise AssertionError("no table%s in %r" % (" starting with %r" % first_column if first_column else "", body[:200]))


def records(header, rows):
    """Table rows as dicts keyed by the header (every row has exactly the header's cell count)."""
    for row in rows:
        assert len(row) == len(header), "a row has %d cells under a %d-column header: %s" % (len(row), len(header), row)
    return [dict(zip(header, row)) for row in rows]


def subsection_for(md, finding_id):
    """The text of Section 3's subsection for one finding, or ``None`` when it has none."""
    for heading, body in split_headings(section_text(md, "## 3. Dimensional Breakdown"), "### "):
        if heading.startswith("### " + finding_id + " " + DASH + " "):
            return heading + "\n" + body
    return None


def section_text(md, title):
    """A section as a heading and its body, so ``split_headings`` can see the subsections' own level."""
    return title + "\n" + section(md, title)


def frontmatter_text(md):
    match = re.match(r"^---\s*\n(.*?)\n---", md, re.DOTALL) or re.search(r"```yaml\s*\n---\s*\n(.*?)\n---\s*\n```", md, re.DOTALL)
    assert match, "no frontmatter"
    return match.group(1)


# =============================================================================
# 3. The harness
# =============================================================================


class Result(object):
    def __init__(self, code, out, err):
        self.code, self.out, self.err = code, out, err

    def describe(self):
        return "exit %r\n--- stdout ---\n%s\n--- stderr ---\n%s" % (self.code, self.out, self.err)


@contextlib.contextmanager
def working_directory(path):
    previous = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(previous)


def invoke(module, argv, cwd):
    """``module.main(argv)`` in-process, in ``cwd``, with stdout and stderr captured. ``SystemExit`` becomes the code."""
    out, err = io.StringIO(), io.StringIO()
    with working_directory(cwd), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = module.main([str(a) for a in argv])
        except SystemExit as exc:  # argparse's usage errors, --help and --version
            code = exc.code
            if code is None:
                code = 0
            elif not isinstance(code, int):
                err.write(str(code))
                code = 1
    return Result(code, out.getvalue(), err.getvalue())


@pytest.fixture(scope="module")
def stage():
    return _load_hyphenated_script("tachi_stage_for_render_tests", "tachi-stage.py")


@pytest.fixture(scope="module")
def renderer():
    if not RENDERER.is_file():
        pytest.fail("scripts/render-risk-scores.py does not exist yet: T028 writes it to these goldens (TDD)", pytrace=False)
    return _load_hyphenated_script("render_risk_scores_under_test", "render-risk-scores.py")


class Project(object):
    """One synthetic project: a working directory, an architecture file, a run directory and its ``threats.md``."""

    def __init__(self, stage_module, renderer_module, root, specs=None, resolved=None, threats_text=None, items=None,
                 **threats_options):
        self.stage, self.renderer = stage_module, renderer_module
        self.item_factory = items
        self.root = Path(root)
        self.out = self.root / "run"
        self.architecture = self.root / "docs" / "security" / "architecture.md"
        self.threats = self.out / "threats.md"
        self.specs = list(SPECS if specs is None else specs)
        self.resolved = list(RESOLVED if resolved is None else resolved)
        self.plan_id = self.digest = None
        self.plan_stderr = ""
        self.last = None
        self.architecture.parent.mkdir(parents=True)
        self.out.mkdir(parents=True)
        self.architecture.write_text(make_architecture_md(), encoding="utf-8")
        self.threats.write_text(make_threats_md(self.specs, self.resolved, **threats_options) if threats_text is None else threats_text,
                                encoding="utf-8")

    # ---- layout
    @property
    def plan_dir(self):
        return Path(tp.plan_dir(self.out, STAGE, self.plan_id))

    def read_json(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def plan_json(self):
        return self.read_json(self.plan_dir / "plan.json")

    def batches(self):
        return {entry["batch_id"]: entry for entry in self.plan_json()["batches"]}

    def batch_input(self, batch_id):
        return self.read_json(tp.input_path(self.out, STAGE, self.plan_id, batch_id))

    # ---- earlier outputs
    def earlier(self):
        (self.out / MD).write_bytes(EARLIER_MD)
        (self.out / SARIF).write_bytes(EARLIER_SARIF)

    def assert_earlier_outputs_untouched(self):
        assert (self.out / MD).read_bytes() == EARLIER_MD
        assert (self.out / SARIF).read_bytes() == EARLIER_SARIF

    # ---- plan, parts, reconcile
    def plan(self, batch_size=None, date=DATE, architecture=True, baseline_dir=None):
        """The planner through its function interface, as ``test_tachi_stage.py`` calls it (ADR-050 D6).

        ``architecture`` is ``True`` for the project's own file, a path for another candidate (the command's
        ``--architecture-path``), or falsy for none. ``baseline_dir`` is the command's ``--baseline``.
        """
        err = io.StringIO()
        explicit = self.architecture if architecture is True else (architecture or None)
        with working_directory(self.root), contextlib.redirect_stderr(err):
            result = self.stage.plan_stage(stage=STAGE, out=self.out, date=date, threats=self.threats, architecture=explicit,
                                           baseline_dir=baseline_dir, batch_size=batch_size)
        self.plan_stderr = err.getvalue()
        self.plan_id, self.digest = result["plan_id"], result["plan_digest"]
        return result

    def item_for(self, finding_id):
        if self.item_factory is not None:
            return self.item_factory(finding_id)
        return scorer_item(by_id(finding_id, self.specs))

    def part_for(self, batch_id, mutate=None):
        bi = self.batch_input(batch_id)
        part = {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": bi["stage"],
                "agent_type": bi["agent_type"], "finding_ids": list(bi["finding_ids"]),
                "items": [self.item_for(finding_id) for finding_id in bi["finding_ids"]], "fragments": []}
        if mutate is not None:
            mutate(part)
        return part

    def write_part(self, batch_id, mutate=None, raw=None):
        path = Path(self.batch_input(batch_id)["part_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            path.write_bytes(raw)
        else:
            path.write_text(json.dumps(self.part_for(batch_id, mutate)), encoding="utf-8")
        return path

    def write_parts(self, only=None, mutate=None):
        for batch_id, entry in self.batches().items():
            if entry["state"] != "split" and (only is None or batch_id in only):
                self.write_part(batch_id, mutate)

    def reconcile(self):
        res = invoke(self.stage, ["reconcile", "--stage", STAGE, "--out", self.out, "--plan", self.plan_id,
                                  "--plan-digest", self.digest], self.root)
        if res.code in (0, 3, 4):
            self.digest = json.loads(res.out)["plan_digest"]
        return res

    def prepare(self, batch_size=None, date=DATE, mutate=None, architecture=True, baseline_dir=None):
        """Plan, write a valid part for every batch and reconcile to complete (the command's Steps 2 to 4)."""
        self.plan(batch_size, date, architecture, baseline_dir)
        self.write_parts(mutate=mutate)
        res = self.reconcile()
        assert res.code == 0, res.describe()

    def render(self, *extra):
        self.last = invoke(self.renderer, ["--out", self.out, "--plan", self.plan_id, "--plan-digest", self.digest, *extra], self.root)
        return self.last

    def run(self, batch_size=None, date=DATE, mutate=None, architecture=True, baseline_dir=None):
        self.prepare(batch_size, date, mutate, architecture, baseline_dir)
        return self.render()

    def fail(self, reason="check-failed", detail=None):
        extra = ["--detail", detail] if detail is not None else []
        return invoke(self.stage, ["fail", "--stage", STAGE, "--out", self.out, "--plan", self.plan_id,
                                   "--plan-digest", self.digest, "--reason", reason, *extra], self.root)

    # ---- what the render wrote
    @property
    def md(self):
        return (self.out / MD).read_text(encoding="utf-8")

    @property
    def sarif_text(self):
        return (self.out / SARIF).read_text(encoding="utf-8")

    @property
    def sarif(self):
        return json.loads(self.sarif_text)

    @property
    def record(self):
        return self.read_json(tp.stage_record_path(self.out, STAGE, self.plan_id))

    def outputs(self):
        return {name: ((self.out / name).read_bytes() if (self.out / name).exists() else None) for name in (MD, SARIF)}


def subset_project(stage_module, renderer_module, root):
    """A project over the fixture's gated subset: 42 open findings, 3 RESOLVED, and generic scorer items for every one.

    Returns ``(project, reference)``. The subset's correlation groups are cut out (reading): T044's planner leaves a
    peer out of the plan, and the peer cases are ``test_peers_*``, so this input needs no routing. Its
    ``## Affected Assets`` block lists only some findings, so a run over it may warn that the block is stale (exit 5).
    """
    text = (GATED_SUBSET / "baseline" / "threats.md").read_text(encoding="utf-8")
    text = re.sub(r"(?ms)^## 4a\. Correlated Findings.*?(?=^## )", "", text)
    assert "## 4a." not in text
    reference = tachi_parsers.parse_reference_set(text)
    scope = scope_of(text)
    component = {canon(row["id"]): row["component"] for row in reference["open"]}
    project = Project(stage_module, renderer_module, root, threats_text=text,
                      items=lambda finding_id: scorer_item(generic_item(finding_id, component[canon(finding_id)], scope)))
    project.architecture.write_text((GATED_SUBSET / "architecture" / "architecture.md").read_text(encoding="utf-8"), encoding="utf-8")
    return project, reference


@pytest.fixture(scope="module")
def base(stage, renderer, tmp_path_factory):
    """One clean render of the nine-finding project, shared by the read-only goldens below."""
    project = Project(stage, renderer, tmp_path_factory.mktemp("base"))
    res = project.run()
    assert res.code in (0, 5), "the base render must finish for the goldens below to read it:\n" + res.describe()
    return project


@pytest.fixture
def project(stage, renderer, tmp_path):
    return Project(stage, renderer, tmp_path)


@contextlib.contextmanager
def watching_replace(log):
    """Record every ``os.replace(src, dst)`` as ``(absolute src, absolute dst, staged names then present, src's sha256)``."""
    real = os.replace

    def replace(src, dst, *args, **kwargs):
        source, destination = os.path.abspath(str(src)), os.path.abspath(str(dst))
        present = [name for name in (MD, SARIF) if os.path.exists(os.path.join(os.path.dirname(source), name))]
        seen = hashlib.sha256(Path(source).read_bytes()).hexdigest() if os.path.isfile(source) else None
        log.append((source, destination, present, seen))
        return real(src, dst, *args, **kwargs)

    os.replace = replace
    try:
        yield
    finally:
        os.replace = real


@contextlib.contextmanager
def tampering_with_staged(name, edit):
    """While active, the staged file ``name`` is edited on disk right after the renderer writes it.

    The renderer then reads it back from disk (ADR-050 D4), so this is a seeded renderer bug that only a
    from-disk check can see. It hooks ``os.replace``, which ``tachi_parts.atomic_write`` ends with.
    """
    real = os.replace

    def replace(src, dst, *args, **kwargs):
        result = real(src, dst, *args, **kwargs)
        destination = str(dst)
        if os.path.basename(destination) == name and (os.sep + "staged" + os.sep) in destination:
            text = Path(destination).read_text(encoding="utf-8")
            Path(destination).write_text(edit(text), encoding="utf-8")
        return result

    os.replace = replace
    try:
        yield
    finally:
        os.replace = real


@contextlib.contextmanager
def failing_replace(name):
    """While active, moving a staged file onto the canonical name ``name`` fails with an I/O error."""
    real = os.replace

    def replace(src, dst, *args, **kwargs):
        if os.path.basename(str(dst)) == name and (os.sep + "staged" + os.sep) in str(src) and (os.sep + "staged" + os.sep) not in str(dst):
            raise OSError(5, "Input/output error")
        return real(src, dst, *args, **kwargs)

    os.replace = replace
    try:
        yield
    finally:
        os.replace = real


# =============================================================================
# 4. Harness checks: no renderer needed
# =============================================================================


def reference_reachability(trust, zone, auth, net):
    """The reachability reference's reachability, restated for the cross-check only (``reachability-analysis.md``)."""
    low, high = ts.REACHABILITY_RANGES[trust]
    score = ts.REACHABILITY_BASELINES[trust]
    lowered = zone.lower()
    for keywords, adjustment in ts.REACHABILITY_KEYWORDS:
        score += adjustment * sum(1 for keyword in keywords if keyword in lowered)
    score += ts.AUTH_BARRIER_ADJUSTMENT * min(auth, ts.AUTH_BARRIER_CAP) + ts.NETWORK_BOUNDARY_ADJUSTMENT * min(net, ts.NETWORK_BOUNDARY_CAP)
    return ts.q1(max(low, min(high, score)))


def test_harness_the_literal_goldens_equal_the_shipped_arithmetic():
    """The expectations below are literals, so this is where a wrong number is caught: each one is re-derived."""
    assert sorted(GOLDEN) == sorted(item["id"] for item in SPECS)
    for item in SPECS:
        cvss, e, s, r, comp, band = GOLDEN[item["id"]]
        got_cvss = ts.base_score(item["vector"])
        got_e, got_s = ts.sub_score_mean(item["e"]), ts.sub_score_mean(item["s"])
        got_r = reference_reachability(item["trust"], item["zone"], item["auth"], item["net"])
        got_composite = ts.composite(got_cvss, got_e, got_s, got_r)
        assert (str(got_cvss), str(got_e), str(got_s), str(got_r), str(got_composite), ts.band(got_composite)) == (
            cvss, e, s, r, comp, band), item["id"]
    for band, (sla, disposition, review) in GOVERNANCE.items():
        assert ts.SEVERITY_BANDS[band]["sla"] == sla and ts.SEVERITY_BANDS[band]["disposition"] == disposition
        assert ts.review_date(DATE, sla) == review
    counts = {band: sum(1 for value in GOLDEN.values() if value[5] == band) for band in GOVERNANCE}
    assert counts == BAND_COUNTS
    assert ts.largest_remainder(BAND_COUNTS) == PERCENTAGES and sum(PERCENTAGES.values()) == 100


def test_harness_the_orders_are_composite_descending_then_s2():
    by_score = sorted(GOLDEN, key=lambda finding_id: (-Decimal(GOLDEN[finding_id][4]), s2_key(finding_id)))
    assert by_score == ORDER
    assert sorted(ORDER, key=s2_key) == S2_ORDER
    assert sorted(RESOLVED_IDS, key=s2_key) == RESOLVED_IDS
    tied = [finding_id for finding_id in ORDER if GOLDEN[finding_id][4] == "5.9"]
    assert tied == ["S-2", "S-10", "T-1", "AG-1"], "S-2 breaks the tie: by number within a prefix, then by prefix rank"


def test_harness_the_synthetic_threats_md_is_a_valid_reference_set():
    reference = tachi_parsers.parse_reference_set(make_threats_md())
    assert [canon(row["id"]) for row in reference["open"]] == [canon(i) for i in S2_ORDER]
    assert [row["id"] for row in reference["resolved"]] == RESOLVED_IDS
    assert reference["duplicates"] == []
    assert {row["id"]: row["delta_status"] for row in reference["open"]}["AGP-01"] == "NEW"
    assert sc.parse_affected_assets(make_threats_md()) == {item["id"]: [] for item in SPECS}
    scope = scope_of(make_threats_md())
    for item in SPECS:
        assert scope[item["component"]] == (item["zone"], item["trust"]), item["id"]
    assert tachi_parsers.parse_resolved_findings(make_threats_md())[0]["id"] == "S-1"


def test_harness_the_synthetic_parts_pass_the_shipped_validator(stage, tmp_path):
    root = Project(stage, None, tmp_path)
    root.prepare(batch_size=4)
    assert sorted(root.batches()) == ["B001", "B002", "B003"]
    seen = []
    for batch_id, entry in root.batches().items():
        result = tp.read_part(root.batch_input(batch_id)["part_path"], root.out, root.plan_id, batch_id, STAGE,
                              "tachi-risk-scorer", entry["finding_ids"])
        assert result.state == "done", (batch_id, result.detail)
        assert result.counts == {"narrative_fallbacks": 0, "truncations": 0} and result.flags == {}
        seen += [item["finding_id"] for item in result.part["items"]]
    assert sorted(seen, key=s2_key) == [canon(finding_id) for finding_id in S2_ORDER], "a validated part carries canonical IDs"


def test_harness_the_slot_lookup_resolves_every_slot_the_narrative_uses():
    for item in SPECS:
        for field, text in RATIONALE.items():
            assert narrative(item, text) is not None, (item["id"], field)
    assert narrative(by_id("S-2"), RATIONALE["cvss"]) == "The base score is 8.2 for edge-gateway."
    assert narrative(by_id("E-3"), RATIONALE["reachability"]) == (
        "Edge DMZ yields 4.0, with 1 authentication layers and 1 network boundaries.")


def test_harness_the_table_reader_decodes_after_the_split_on_raw_pipes():
    body = "| A | B |\n|---|---|\n| x &#124; y | &lt;b&gt; |\n| plain | &amp;lt; |\n"
    assert tables(body) == [(["A", "B"], [["x | y", "<b>"], ["plain", "&lt;"]])]
    assert decode("&amp;#124;") == "&#124;", "a decoded reference is never decoded again"


# =============================================================================
# 5. The entry: arguments and the exit table (T028; contracts/cli.md)
# =============================================================================

URI = "docs/security/architecture.md"


def tree_state(root):
    """``{relative path: sha256}`` for every file under ``root``, to prove that nothing there changed."""
    root = Path(root)
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}


def assert_failure_message(res, plan_id=None):
    """D4's failure message: the first line names the stage, then the remedy and where the plan was kept."""
    assert res.err.startswith("TACHI RISK-SCORE FAILED:") or "\nTACHI RISK-SCORE FAILED:" in res.err, res.describe()
    assert "Remedy:" in res.err, res.describe()
    if plan_id is not None:
        assert re.search(r"Kept for diagnosis: .*%s" % re.escape(plan_id), res.err), res.describe()


def test_cli_help_and_version_are_supported(renderer, tmp_path):
    helped = invoke(renderer, ["--help"], tmp_path)
    assert helped.code == 0 and all(flag in helped.out for flag in ("--out", "--plan", "--plan-digest")), helped.describe()
    versioned = invoke(renderer, ["--version"], tmp_path)
    assert versioned.code == 0, versioned.describe()
    assert tp.VERSION in versioned.out + versioned.err  # reading: cli.md says tests may accept either stream
    assert "%d.%d" % sys.version_info[:2] in versioned.out + versioned.err, "the interpreter's version too"


def test_cli_a_missing_plan_digest_is_a_usage_error(renderer, tmp_path):
    res = invoke(renderer, ["--out", tmp_path, "--plan", "20261122T100000Z-0123456789ab"], tmp_path)
    assert res.code == 2, res.describe()


def test_cli_a_run_directory_with_no_plan_is_a_missing_input(renderer, tmp_path):
    (tmp_path / "run").mkdir()
    res = invoke(renderer, ["--out", tmp_path / "run", "--plan", "20261122T100000Z-0123456789ab", "--plan-digest", "0" * 64], tmp_path)
    assert res.code == 1, res.describe()
    assert_failure_message(res)
    assert not (tmp_path / "run" / MD).exists() and not (tmp_path / "run" / SARIF).exists()


def test_cli_a_plan_digest_that_differs_exits_2_and_writes_nothing(project):
    project.earlier()
    project.prepare()
    before = tree_state(project.out)
    res = invoke(project.renderer, ["--out", project.out, "--plan", project.plan_id, "--plan-digest", "0" * 64], project.root)
    assert res.code == 2, res.describe()
    assert_failure_message(res)
    assert tree_state(project.out) == before, "a refused plan leaves every file as it was"
    project.assert_earlier_outputs_untouched()


def test_cli_a_plan_that_current_json_does_not_name_exits_2(project):
    project.prepare()
    older_id, older_digest = project.plan_id, project.digest
    project.plan()  # a newer plan replaces the pointer
    res = invoke(project.renderer, ["--out", project.out, "--plan", older_id, "--plan-digest", older_digest], project.root)
    assert res.code == 2, res.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists()


def test_cli_a_changed_plan_input_exits_2(project):
    project.prepare()
    project.threats.write_text(project.threats.read_text(encoding="utf-8") + "\nAn edit after plan.\n", encoding="utf-8")
    res = project.render()
    assert res.code == 2, res.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists()


def test_cli_the_summary_goes_to_stdout_and_the_renderer_leaves_the_plan_alone(base):
    assert base.last.code == 0, base.last.describe()
    assert base.last.out.strip(), "the renderer prints summary lines, so the command restates no number (D4 Step 6)"
    assert not base.last.out.lstrip().startswith("{"), "summary lines, not one JSON object (cli.md)"
    for number in (len(ORDER), len(RESOLVED_IDS)):
        assert re.search(r"(?<![\w.])%d(?![\w.])" % number, base.last.out), "the summary has the count %d: %s" % (number, base.last.out)
    assert tp.file_digest(base.plan_dir / "plan.json") == base.digest, "only plan and reconcile write the plan (contracts/part-files.md)"
    assert tp.read_document(tp.pointer_path(base.out, STAGE), base.out, tp.POINTER_SCHEMA)["plan_id"] == base.plan_id


# =============================================================================
# 6. risk-scores.md (T028, T045, T046; ADR-050 D2, D9, D15)
# =============================================================================


def test_md_the_run_is_clean(base):
    assert base.last.code == 0, base.last.describe()
    assert base.record["warnings"] == [] and base.record["status"] == "success"


def test_md_the_frontmatter_is_schema_1_1(base):
    front = tachi_parsers.parse_frontmatter(base.md)
    assert (front["schema_version"], front["date"], front["classification"]) == ("1.1", DATE, "confidential")
    text = frontmatter_text(base.md)
    for name, weight in (("cvss_base", "0.35"), ("exploitability", "0.30"), ("scalability", "0.15"), ("reachability", "0.20")):
        assert re.search(r"(?m)^\s+" + re.escape(name) + r"\s*:\s*\"?" + re.escape(weight) + r"\"?\s*$", text), name
    baseline = tachi_parsers.parse_baseline_frontmatter(base.md)
    assert baseline["has_baseline"] is False and baseline["source"] is None
    for key in ("inherited_count", "fresh_count"):  # the template says "null when no baseline"
        assert re.search(r"(?m)^\s+" + re.escape(key) + r"\s*:\s*(null|~)?\s*$", text), key
    source = re.search(r"(?m)^source_file:\s*\"?([^\"\n]+)\"?\s*$", text)
    assert source, "source_file names the input threats.md: the controls command reaches it from here (D7, D9)"
    assert os.path.samefile(str(base.root / source.group(1)), str(base.threats))


def test_md_the_sections_come_in_order(base):
    lines = base.md.split("\n")
    positions = []
    for title in SECTION_TITLES:
        found = [n for n, line in enumerate(lines) if line.startswith(title)]
        assert len(found) == 1, "%s: %d headings" % (title, len(found))
        positions.append(found[0])
    assert positions == sorted(positions), "Sections 1 to 6, with 2a after Section 2 (R-30)"


def test_md_section_2_holds_exactly_the_open_rows_in_score_order(base):
    header, rows = table_of(section(base.md, "## 2. Scored Threat Table"), "ID")
    assert header == SECTION_2_HEADER
    found = records(header, rows)
    assert [row["ID"] for row in found] == ORDER, "composite descending, then S-2's total order (ADR-050 D5)"
    for row in found:
        item = by_id(row["ID"])
        cvss, e, s, reach, composite, band = golden(row["ID"])
        sla, disposition, _review = GOVERNANCE[band]
        assert row["Source"] == "fresh"
        assert row["Component"] == truncate(item["component"], 30)
        assert row["Threat"] == truncate(item["threat"], 60)
        assert (row["CVSS"], row["Exploit."], row["Scale."], row["Reach."]) == (cvss, e, s, reach)
        assert (row["Composite"], row["Severity"], row["SLA"], row["Disposition"]) == (composite, band, sla, disposition)
        assert row["Flags"] == DASH, "a clean row has no flags"


def test_md_section_2_shortens_long_names_and_text_before_it_escapes(base):
    rows = {row["ID"]: row for row in records(*table_of(section(base.md, "## 2. Scored Threat Table"), "ID"))}
    assert len(LONG_COMPONENT) == 36 and rows["LLM-4"]["Component"] == LONG_COMPONENT[:27] + "..."
    assert rows["E-5"]["Threat"] == by_id("E-5")["threat"][:57] + "..." and len(rows["E-5"]["Threat"]) == 60
    assert rows["E-3"]["Threat"] == by_id("E-3")["threat"], "a short threat is shown whole"
    # The cut comes first, so no escape reference is ever cut in two (ADR-050 D3, "Output").
    line = raw_row(base.md, "## 2. Scored Threat Table", "LLM-4")
    assert tp.escape_cell(truncate(HOSTILE_THREAT, 60)) in line


def test_md_section_2a_holds_exactly_the_resolved_rows(base):
    header, rows = table_of(section(base.md, "## 2a. Resolved Findings"), "ID")
    assert header[-1] == "Flags" and set(SECTION_2_HEADER[:-1]) | {"Status", "Owner", "Review Date"} <= set(header)
    found = records(header, rows)
    assert [row["ID"] for row in found] == RESOLVED_IDS, "Section 4c's findings, in S-2 order: the split parity of R-30"
    for row, (finding_id, component, threat, _risk, _reason) in zip(found, RESOLVED):
        assert row["Status"] == "RESOLVED" and row["Flags"] == "resolved"
        assert row["Component"] == truncate(component, 30) and row["Threat"] == truncate(threat, 60)
        for column in ("CVSS", "Exploit.", "Scale.", "Reach.", "Composite"):
            assert not re.fullmatch(r"\d+\.\d", row[column]), "%s: a RESOLVED row is never recomputed (R-30)" % column
        assert not re.search(r"\d{4}-\d{2}-\d{2}", row["Review Date"]), "and it is outside the SLA clock"


def test_md_section_2a_is_omitted_when_there_is_no_section_4c_finding(stage, renderer, tmp_path):
    """Ruled by the architect, option (a): no ``## 2a`` heading and no empty table, as lane C's 1.1 template has it (D15)."""
    project = Project(stage, renderer, tmp_path, resolved=[])
    res = project.run()
    assert res.code == 0, res.describe()
    assert not has_section(project.md, "## 2a."), "no heading is written for an empty Section 4c"
    assert "Resolved Findings" not in project.md
    assert tachi_parsers.parse_markdown_table(project.md, "## 2a. Resolved Findings") == [], "no reader depends on the heading"
    rows = records(*table_of(section(project.md, "## 2. Scored Threat Table"), "ID"))
    assert [row["ID"] for row in rows] == ORDER and project.record["counts"]["resolved"] == 0
    assert has_section(project.md, "## 3. Dimensional Breakdown"), "Section 3 follows Section 2"


def test_md_resolved_findings_appear_only_in_section_2a(base):
    md = base.md
    for finding_id in RESOLVED_IDS:
        assert subsection_for(md, finding_id) is None, "Section 3 has no RESOLVED finding"
        for title, first_column in (("## 2. Scored Threat Table", "ID"), ("## 4. Governance Fields", "ID")):
            assert finding_id not in [row[0] for row in table_of(section(md, title), first_column)[1]], title
        inputs = table_of(subsection_of(md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")[1]
        assert finding_id not in [row[0] for row in inputs]


def test_md_section_3_has_one_subsection_per_open_finding_in_section_2_order(base):
    found = split_headings(section_text(base.md, "## 3. Dimensional Breakdown"), "### ")
    assert [re.match(r"### (\S+) " + DASH + " ", heading).group(1) for heading, _ in found] == ORDER
    for heading, _ in found:
        finding_id = heading.split(" ")[1]
        assert heading == "### %s %s %s" % (finding_id, DASH, tp.escape_prose(by_id(finding_id)["component"]))


def test_md_section_3_shows_each_findings_scores_and_inputs(base):
    for finding_id in ORDER:
        item, body = by_id(finding_id), subsection_for(base.md, finding_id)
        cvss, e, s, reach, composite, band = golden(finding_id)
        prefix = item["id"].partition("-")[0]
        assert "**Threat**: " + tp.escape_prose(item["threat"]) in body, finding_id
        assert "**Category**: %s | **Original Risk Level**: %s | **Composite**: %s (%s)" % (
            ts.category_for_prefix(prefix), item["risk"], composite, band) in body, finding_id
        assert "**Score**: %s | **Vector**: `%s`" % (cvss, item["vector"]) in body, finding_id
        assert "**Score**: %s (average of sub-dimensions)" % e in body, finding_id
        assert "**Score**: %s (average of sub-dimensions)" % s in body, finding_id
        assert "**Score**: %s | **Trust Zone**: %s (%s)" % (reach, tp.escape_prose(item["zone"]), item["trust"]) in body, finding_id
        letters = dict(part.split(":") for part in item["vector"].split("/")[1:])
        metrics = {row[0]: row[1] for row in table_of(body, "Metric")[1]}
        assert metrics == {METRIC_LABEL[m]: METRIC_VALUES[m][letters[m]] for m in tp.METRIC_NAMES}, finding_id
        sub = [table for table in tables(body) if table[0][0] == "Sub-Dimension"]
        assert len(sub) == 2, "one table for exploitability and one for scalability"
        for (_header, rows), names, scores in zip(sub, (tp.SUBSCORE_NAMES[:4], tp.SUBSCORE_NAMES[4:]), (item["e"], item["s"])):
            assert [(row[0], row[1]) for row in rows] == [(SUBSCORE_LABEL[n], str(v)) for n, v in zip(names, scores)], finding_id


def test_md_section_3_fills_the_slots_of_the_agents_narrative(base):
    for finding_id in ORDER:
        item, body = by_id(finding_id), subsection_for(base.md, finding_id)
        for field, text in RATIONALE.items():
            assert narrative(item, text, "prose") in body or narrative(item, text, "cell") in body, (finding_id, field)
        assert "{{" not in body, "no slot token survives into Section 3: %s" % finding_id
    body = subsection_for(base.md, "S-2")
    metric = {row[0]: row[2] for row in table_of(body, "Metric")[1]}
    assert metric["Attack Vector (AV)"] == "Reachable over the network."
    known = [row for _h, rows in tables(body) if _h[0] == "Sub-Dimension" for row in rows if row[0] == "Known Techniques"][0]
    assert known[2] == "Documented in public write-ups."


def test_md_section_4_holds_the_governance_fields_of_every_open_finding(base):
    header, rows = table_of(section(base.md, "## 4. Governance Fields"), "ID")
    assert header == SECTION_4_HEADER
    found = records(header, rows)
    assert [row["ID"] for row in found] == ORDER, "Section 4 follows Section 2; RESOLVED rows are outside the SLA clock"
    for row in found:
        band = golden(row["ID"])[5]
        sla, disposition, review = GOVERNANCE[band]
        assert (row["Severity"], row["Owner"], row["SLA"], row["Disposition"], row["Review Date"]) == (
            band, "Unassigned", sla, disposition, review)


def test_md_section_5_states_the_formula_and_the_bands(base):
    body = section(base.md, "## 5. Scoring Methodology")
    assert "(0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)" in body
    for band in GOVERNANCE:
        assert band in body


def test_md_section_6_has_its_four_subsections_in_order(base):
    body = section(base.md, "## 6. Score Integrity")
    assert [line for line in body.split("\n") if line.startswith("### ")] == SECTION_6_PARTS


def expected_scoring_inputs(finding_ids, scored_on=DATE, specs=None, tags=()):
    """The ``### Scoring Inputs`` rows (``contracts/module-signatures.md``): one per value, in S-2 order of ID and then
    the payload's key order, with the renderer's own step-1 inputs last. Values are the decoded cells."""
    rows = []
    for finding_id in sorted(finding_ids, key=s2_key):
        item = by_id(finding_id, specs)
        part = scorer_item(item)
        rows.append((finding_id, "cvss_vector", item["vector"]))
        for group, names in (("exploitability", tp.SUBSCORE_NAMES[:4]), ("scalability", tp.SUBSCORE_NAMES[4:])):
            rows += [(finding_id, "%s.%s" % (group, name), str(part[group][name])) for name in names]
        for name in ("zone", "trust_level", "auth_barriers", "network_boundaries"):
            rows.append((finding_id, "reachability." + name, str(part["reachability"][name])))
        rows += [(finding_id, "rationale." + name, part["rationale"][name]) for name in ("cvss", "exploitability", "scalability", "reachability")]
        rows += [(finding_id, "metric_rationale." + name, part["metric_rationale"][name]) for name in tp.METRIC_NAMES if name in part.get("metric_rationale", {})]
        rows += [(finding_id, "subscore_rationale." + name, part["subscore_rationale"][name]) for name in tp.SUBSCORE_NAMES if name in part.get("subscore_rationale", {})]
        rows += [(finding_id, "tags", ",".join(sorted(tags))), (finding_id, "scored_on", scored_on)]
    return rows


def subsection_of(md, title, subtitle):
    """The body of a ``###`` subsection of one ``##`` section."""
    found = [body for heading, body in split_headings(section_text(md, title), "### ") if heading.startswith(subtitle)]
    assert len(found) == 1, "%s under %s: %d" % (subtitle, title, len(found))
    return found[0]


def test_md_section_6_scoring_inputs_are_the_persisted_format_exactly(base):
    header, rows = table_of(subsection_of(base.md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")
    assert header == ["ID", "Field", "Value"]
    got = [(canon(row[0]), row[1], row[2]) for row in rows]
    want = [(canon(finding_id), field, value) for finding_id, field, value in expected_scoring_inputs(OPEN_IDS)]
    assert got == want  # reading: an ID's spelling is Section 7's or the canonical one; both compare as one


def test_md_section_6_keeps_the_agents_slots_in_the_persisted_text_and_escapes_them_on_write(base):
    raw = subsection_of(base.md, "## 6. Score Integrity", "### Scoring Inputs")
    assert "{{score:cvss_base}}" in raw and "{{name:zone}}" in raw, "narrative values keep their slot tokens (RR1)"
    line = raw_row(base.md, "## 6. Score Integrity", "S-2", field="rationale.reachability")
    assert tp.escape_cell(RATIONALE["reachability"], keep_slots=True) in line


def test_md_section_6_is_empty_of_flags_and_issues_for_a_clean_run(base):
    flags = tables(subsection_of(base.md, "## 6. Score Integrity", "### Score Flags"))
    assert flags == [] or (flags[0][0] == ["ID", "Flag", "Field", "Stored", "Rendered", "Cause"] and flags[0][1] == [])
    issues = subsection_of(base.md, "## 6. Score Integrity", "### Input Issues")
    assert all(not rows for _header, rows in tables(issues)), "Input Issues lists nothing for a clean run"
    for finding_id in OPEN_IDS:
        assert "**Integrity**:" not in subsection_for(base.md, finding_id), "only a flagged finding has an Integrity line"


def numbers_in(line):
    """The integers in a line of prose, with any ISO date taken out first."""
    return re.findall(r"\d+", re.sub(r"\d{4}-\d{2}-\d{2}", "", line))


def test_md_the_executive_summary_is_one_templated_sentence_with_the_computed_counts(base):
    body = section(base.md, "## 1. Executive Summary")
    prose = [re.sub(r"[*`>]", "", line).strip() for line in body.split("\n")
             if line.strip() and not line.strip().startswith(("|", "---", "<!--", "#"))]
    counts = ["%d" % n for n in (len(ORDER), BAND_COUNTS["Critical"], BAND_COUNTS["High"], BAND_COUNTS["Medium"], BAND_COUNTS["Low"])]
    sentences = [line for line in prose if numbers_in(line)[:5] == counts]
    # The sentence's wording is the template's (T031). The architect confirmed what the golden pins: it states the open
    # count, then Critical, High, Medium and Low, in that order (ADR-050 D2).
    assert len(sentences) == 1, "one line states the open count, then the four bands: %s" % prose
    sentence = sentences[0]
    positions = [sentence.index(band) for band in ("Critical", "High", "Medium", "Low")]
    assert positions == sorted(positions)
    assert len(re.findall(r"[.!?](?:\s|$)", sentence)) == 1, "one sentence"
    resolved_lines = [line for line in prose if line != sentence and "resolved" in line.lower() and str(len(RESOLVED_IDS)) in numbers_in(line)]
    assert resolved_lines, "RESOLVED findings are counted on a separate line (D9): %s" % prose


def test_md_the_first_table_of_the_executive_summary_is_the_severity_band_table(base):
    """Severity, Count and Percentage, percentages by largest remainder, and a Total row equal to the open count. The
    report and infographic extractors read it through ``parse_risk_scores_severity`` unchanged (NFR-1; ADR-050 D2)."""
    header, rows = tables(section(base.md, "## 1. Executive Summary"))[0]
    assert header == ["Severity", "Count", "Percentage"]
    plain = [[re.sub(r"\*", "", cell) for cell in row] for row in rows]
    assert plain == [[band, str(BAND_COUNTS[band]), "%d%%" % PERCENTAGES[band]] for band in ("Critical", "High", "Medium", "Low")] + [
        ["Total", str(len(ORDER)), "100%"]], "RESOLVED findings are never in the distribution (R-30)"


def test_md_the_file_ends_with_the_stamp(base):
    md = base.md
    stamp = tp.read_stamp(md)
    assert stamp is not None and md.rstrip("\n").split("\n")[-1] == tp.stamp_comment(stamp["renderer"], stamp["input_digest"])
    assert stamp["renderer"] == RENDERER_NAME and stamp["version"] == tp.VERSION and DIGEST.match(stamp["input_digest"])


def test_md_every_table_row_has_the_columns_of_its_header(base):
    for header, rows in tables(base.md):
        for row in rows:
            assert len(row) == len(header), "a cell broke its row: %s under %s" % (row, header)


def test_md_untrusted_text_is_escaped_in_every_markdown_sink(base):
    md = base.md
    assert "<b>" not in md and "{{7*7}}" not in md and "<script" not in md
    line = raw_row(md, "## 2. Scored Threat Table", "LLM-4")
    assert "&lt;b&gt;" in line and "&#96;" in line and "&#123;&#123;" in line
    heading = [h for h, _ in split_headings(section_text(md, "## 3. Dimensional Breakdown"), "### ") if h.startswith("### LLM-4 ")][0]
    assert heading == "### LLM-4 %s %s" % (DASH, LONG_COMPONENT)
    body = subsection_for(md, "LLM-4")
    assert "**Threat**: " + tp.escape_prose(HOSTILE_THREAT) in body
    assert "\u00c9tienne" in md, "the markdown is UTF-8 and keeps non-ASCII text as it is"


def raw_row(md, title, first_cell, field=None):
    """The raw line of the row in ``title`` whose first cell is ``first_cell`` (and second ``field``, when given)."""
    for line in section(md, title).split("\n"):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0] == first_cell and (field is None or (len(cells) > 1 and cells[1] == field)):
            return line
    raise AssertionError("no row %r in %s" % (first_cell, title))


# =============================================================================
# 7. risk-scores.sarif (T050; ADR-050 D7, D8; contracts/sarif-result.md)
# =============================================================================


def results_by_id(doc):
    return {result["partialFingerprints"]["findingId/v1"]: result for result in doc["runs"][0]["results"]}


def test_sarif_the_document_is_the_shared_emitters_two_space_ascii_json(base):
    text, doc = base.sarif_text, base.sarif
    assert text == json.dumps(doc, indent=2, ensure_ascii=True) + "\n", "the bytes are the emitter's: two spaces, ASCII, a final newline"
    assert text.isascii()
    assert doc["version"] == "2.1.0" and doc["$schema"] == sc.SARIF_SCHEMA_URI
    assert len(doc["runs"]) == 1
    run = doc["runs"][0]
    assert "automationDetails" not in run, "the upload step's category governs, and tachi never writes one (D7)"
    driver = run["tool"]["driver"]
    assert driver["name"] == TOOL == sc.TOOL_NAMES[SARIF]
    assert driver["informationUri"] == sc.INFORMATION_URI, "the real URI, never a placeholder (FR-E.9)"
    assert driver["supportedTaxonomies"] == sc.supported_taxonomies()
    assert run["taxonomies"] == sc.TAXONOMIES


def test_sarif_one_result_per_open_finding_and_none_for_a_resolved_one(base):
    doc = base.sarif
    results = doc["runs"][0]["results"]
    assert len(results) == len(ORDER), "N is the number of open findings (D8's counting rule)"
    assert sorted(results_by_id(doc)) == sorted(ORDER), "findingId/v1 keeps Section 7's spelling, AGP-01 included"
    for finding_id in RESOLVED_IDS:
        assert not re.search(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(finding_id), base.sarif_text), finding_id


def test_sarif_every_result_passes_the_shared_emitters_self_check(base):
    results = base.sarif["runs"][0]["results"]
    sc.self_check(results, tool=TOOL, member_ids=OPEN_IDS, assignments={}, resolved_ids=RESOLVED_IDS, uri=URI)


def test_sarif_each_result_carries_its_goldens(base):
    results = results_by_id(base.sarif)
    for finding_id in ORDER:
        item, result = by_id(finding_id), results[finding_id]
        cvss, e, s, reach, composite, band = golden(finding_id)
        sla, disposition, review = GOVERNANCE[band]
        assert result["ruleId"] == sc.rule_id_for(finding_id)
        assert result["level"] == sc.level_for_band(band)
        # The file's own text is the reference set's threat text, and `markdown` is its mitigation text, which NFR-1 keeps
        # (the architect's ruling; risk-scorer.md:195-196). `text` comes first in the key order.
        assert result["message"] == {"text": item["threat"], "markdown": mitigation_of(item)}
        assert list(result["message"]) == ["text", "markdown"]
        assert result["partialFingerprints"] == sc.partial_fingerprints(TOOL, finding_id)
        assert "relatedLocations" not in result, "the scorer's file has no related locations (D8)"
        location = result["locations"][0]
        assert location["physicalLocation"] == {"artifactLocation": {"uri": URI}, "region": {"startLine": 1}}
        assert location["logicalLocations"] == [{
            "name": item["component"], "fullyQualifiedName": "%s/%s" % (item["zone"], item["component"]),
            "kind": KIND_OF[COMPONENTS[item["component"]][0]]}]
        properties = result["properties"]
        for key, value in {
                "security-severity": composite, "cvss-base-score": cvss, "cvss-vector": item["vector"],
                "exploitability": e, "scalability": s, "reachability": reach, "composite-weights": "0.35/0.30/0.15/0.20",
                "score-source": "fresh", "severity-band": band, "risk-owner": "Unassigned", "remediation-sla": sla,
                "risk-disposition": disposition, "review-date": review, "affected_assets": []}.items():
            assert properties[key] == value, (finding_id, key)
        assert properties["score-flags"] == [], "always present, and sorted (D9)"
        assert properties.get("score-corrections", []) == []
        assert not [key for key in properties if key.startswith("correlation-")]


def test_sarif_each_rule_carries_the_highest_composite_of_its_findings(base):
    run = base.sarif["runs"][0]
    rules = {rule["id"]: rule for rule in run["tool"]["driver"]["rules"]}
    highest = {}
    for result in run["results"]:
        score = Decimal(result["properties"]["security-severity"])
        highest[result["ruleId"]] = max(highest.get(result["ruleId"], score), score)
    assert set(highest) <= set(rules)
    for rule_id, score in highest.items():
        assert rules[rule_id]["properties"]["security-severity"] == str(score), rule_id


def test_sarif_carries_the_provenance_stamp(base):
    stamp = base.sarif["runs"][0]["properties"]["tachi_provenance"]
    assert list(stamp) == ["renderer", "version", "input_digest"]
    assert stamp["renderer"] == RENDERER_NAME and stamp["version"] == tp.VERSION and DIGEST.match(stamp["input_digest"])


# =============================================================================
# 8. The two files agree, and the existing readers still read them (FR-K6.2; NFR-1)
# =============================================================================


def test_agree_the_md_and_the_sarif_agree_on_every_open_finding(base):
    results = results_by_id(base.sarif)
    scored = {row["ID"]: row for row in records(*table_of(section(base.md, "## 2. Scored Threat Table"), "ID"))}
    governed = {row["ID"]: row for row in records(*table_of(section(base.md, "## 4. Governance Fields"), "ID"))}
    assert set(scored) == set(governed) == set(results)
    for finding_id, result in results.items():
        properties, row, gov = result["properties"], scored[finding_id], governed[finding_id]
        assert (row["Composite"], row["Severity"], row["CVSS"], row["Exploit."], row["Scale."], row["Reach."]) == (
            properties["security-severity"], properties["severity-band"], properties["cvss-base-score"],
            properties["exploitability"], properties["scalability"], properties["reachability"])
        assert (row["SLA"], row["Disposition"], gov["Owner"], gov["Review Date"]) == (
            properties["remediation-sla"], properties["risk-disposition"], properties["risk-owner"], properties["review-date"])
        assert "`%s`" % properties["cvss-vector"] in subsection_for(base.md, finding_id)


def test_readers_the_existing_parsers_read_the_rendered_md_back(base):
    md = base.md
    rows = tachi_parsers.parse_risk_scores_findings(md)
    assert [row["id"] for row in rows] == ORDER, "Section 2's readers stop at the first table, so Section 2a never counts as open (D9)"
    for row in rows:
        cvss, e, _s, _r, composite, band = golden(row["id"])
        assert (row["cvss"], row["exploitability"], row["composite_score"], row["severity"]) == (cvss, e, composite, band)
    assert {key: str(value) for key, value in tachi_parsers.composite_scores_by_id(rows).items()} == {
        finding_id: golden(finding_id)[4] for finding_id in ORDER}
    # reading: the report and infographic extractors read the severity distribution from Section 1 (NFR-1, "parsers keep working")
    assert tachi_parsers.parse_risk_scores_severity(md) == {"critical": 1, "high": 1, "medium": 6, "low": 1, "note": 0, "total": len(ORDER)}
    resolved = tachi_parsers.parse_markdown_table(md, "## 2a. Resolved Findings")
    assert [row["ID"] for row in resolved] == RESOLVED_IDS


# =============================================================================
# 9. The staged write, and what a failure leaves behind (F2; ADR-050 D4; KB 21, 22)
# =============================================================================


def first_line_edit(prefix, change):
    """An edit of a staged markdown file: ``change`` applied to the first line that starts with ``prefix``."""
    def edit(text):
        lines = text.split("\n")
        index = next(n for n, line in enumerate(lines) if line.startswith(prefix))
        replaced = change(lines[index])
        if replaced is None:
            del lines[index]
        else:
            lines[index] = replaced
        return "\n".join(lines)
    return edit


def json_edit(change):
    """An edit of a staged SARIF file: parse it, change the document, write it back in the emitter's form."""
    def edit(text):
        document = json.loads(text)
        change(document)
        return json.dumps(document, indent=2, ensure_ascii=True) + "\n"
    return edit


def duplicate_a_result(document):
    document["runs"][0]["results"].append(copy.deepcopy(document["runs"][0]["results"][0]))


def lower_a_score(document):
    document["runs"][0]["results"][0]["properties"]["security-severity"] = "1.0"


def add_a_resolved_result(document):
    extra = copy.deepcopy(document["runs"][0]["results"][0])
    extra["partialFingerprints"] = sc.partial_fingerprints(TOOL, "S-1")
    document["runs"][0]["results"].append(extra)


# Each case seeds one renderer bug that only a check on the files read back from disk can see, and every one of them
# must stop the run before any canonical file is replaced (ADR-050 D4, steps 5 and 6).
CHECK_FAILURES = [
    ("md-lost-an-open-row", MD, first_line_edit("| E-5 |", lambda line: None)),
    ("md-lost-a-resolved-row", MD, first_line_edit("| S-1 |", lambda line: None)),
    ("md-a-composite-the-sarif-does-not-have", MD, first_line_edit("| E-5 |", lambda line: line.replace("| 9.4 |", "| 9.5 |", 1))),
    ("sarif-lost-a-result", SARIF, json_edit(lambda document: document["runs"][0]["results"].pop(0))),
    ("sarif-has-a-result-twice", SARIF, json_edit(duplicate_a_result)),
    ("sarif-names-a-resolved-finding", SARIF, json_edit(add_a_resolved_result)),
    ("sarif-score-the-md-does-not-have", SARIF, json_edit(lower_a_score)),
]


def test_staged_both_files_are_checked_on_disk_before_either_replaces_a_canonical_file(project):
    log = []
    with watching_replace(log):
        res = project.run()
    assert res.code == 0, res.describe()
    out = os.path.abspath(str(project.out))
    moves = [entry for entry in log if os.path.dirname(entry[1]) == out and os.path.basename(entry[1]) in (MD, SARIF)]
    assert sorted(os.path.basename(dst) for _src, dst, _present, _seen in moves) == [MD, SARIF], "each canonical file is replaced once"
    for src, dst, _present, seen in moves:
        assert os.sep + "staged" + os.sep in src and os.path.basename(src) == os.path.basename(dst), "only a staged file replaces a canonical one"
        assert seen == sha256_of(dst), "the bytes that were staged are the bytes now in place"
    assert sorted(moves[0][2]) == [MD, SARIF], "both staged files are on disk before the first move, so the checks ran on them"
    assert max(log.index(entry) for entry in log if os.sep + "staged" + os.sep in entry[1]) < min(log.index(entry) for entry in moves)


@pytest.mark.parametrize("name,target,edit", CHECK_FAILURES, ids=[case[0] for case in CHECK_FAILURES])
def test_staged_a_failing_check_leaves_the_canonical_files_untouched(project, name, target, edit):
    project.earlier()
    project.prepare()
    with tampering_with_staged(target, edit):
        res = project.render()
    assert res.code == 4, "a completeness or parity check that fails is exit 4 (cli.md): %s" % res.describe()
    assert_failure_message(res, project.plan_id)
    project.assert_earlier_outputs_untouched()
    assert (project.plan_dir / "staged" / target).is_file(), "the staged file stays for diagnosis (KB 21)"
    failed = project.fail("check-failed")
    assert failed.code == 0, failed.describe()
    assert json.loads(failed.out)["moved"] == [] and json.loads(failed.out)["restored"] == [], "there was nothing to put back"
    project.assert_earlier_outputs_untouched()
    assert project.record["status"] == "failed" and project.record["error"]["code"] == "check-failed"


def test_staged_a_failing_check_on_a_first_run_leaves_no_canonical_file(project):
    project.prepare()
    with tampering_with_staged(MD, first_line_edit("| E-5 |", lambda line: None)):
        res = project.render()
    assert res.code == 4, res.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists(), "a failed run never leaves a file under a canonical name"


def test_failure_render_failed_a_move_that_fails_half_way_is_undone_by_fail(project):
    project.earlier()
    project.prepare()
    with failing_replace(SARIF):  # the markdown moves, then the SARIF's move fails: a half-applied pair
        res = project.render()
    assert res.code not in (0, 5), res.describe()
    assert_failure_message(res, project.plan_id)
    assert tp.file_digest(project.plan_dir / "plan.json") == project.digest
    failed = project.fail("render-failed", detail="the move failed")
    assert failed.code == 0, failed.describe()
    project.assert_earlier_outputs_untouched()
    assert project.record["status"] == "failed" and project.record["error"]["code"] == "render-failed"


def test_failure_render_failed_on_a_first_run_moves_the_half_written_file_aside(project):
    project.prepare()
    with failing_replace(SARIF):
        res = project.render()
    assert res.code not in (0, 5), res.describe()
    failed = project.fail("render-failed")
    assert failed.code == 0, failed.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists()
    assert (project.plan_dir / "failed" / MD).is_file(), "kept for diagnosis, and under no name any auto-detect site would take"


def test_failure_a_cvss_calculator_that_fails_its_self_test_stops_the_run_before_any_write(project, monkeypatch):
    project.earlier()
    project.prepare()
    monkeypatch.setattr(ts, "base_score", lambda vector: Decimal("0.0"))
    res = project.render()
    assert res.code in (2, 4), "fails closed: a guard failure, before a score is written: %s" % res.describe()
    assert_failure_message(res)
    assert "self-test" in res.err.lower(), res.describe()  # reading: the message names the self-test
    project.assert_earlier_outputs_untouched()
    assert not (project.plan_dir / "staged").exists() or not list((project.plan_dir / "staged").iterdir())


@pytest.mark.parametrize("damage", ["missing", "invalid", "stale"])
def test_failure_a_batch_without_a_valid_part_is_never_rendered(project, damage):
    project.earlier()
    project.prepare(batch_size=4)  # three batches, all reconciled as done
    path = Path(project.batch_input("B002")["part_path"])
    if damage == "missing":
        path.unlink()
    elif damage == "invalid":
        path.write_bytes(b'{"schema": "tachi.part/1"}')
    else:  # a part that is valid for this batch but belongs to another plan
        stale = project.part_for("B002")
        stale["plan_id"] = "20250101T000000Z-0123456789ab"
        path.write_text(json.dumps(stale), encoding="utf-8")
    res = project.render()
    assert res.code in (1, 2, 4), "the renderer re-validates every part it reads: %s" % res.describe()
    assert_failure_message(res, project.plan_id)
    assert "B002" in res.err, "the message names the batch"
    project.assert_earlier_outputs_untouched()


# =============================================================================
# 10. Records: the stamp, the stage record, the declared-paths check (FR-E.7; NFR-5)
# =============================================================================


def test_record_the_stamp_and_the_digest_are_one_value_in_three_places(base):
    stamp = tp.read_stamp(base.md)
    sarif_stamp = base.sarif["runs"][0]["properties"]["tachi_provenance"]
    assert (sarif_stamp["renderer"], sarif_stamp["version"], sarif_stamp["input_digest"]) == (
        stamp["renderer"], stamp["version"], stamp["input_digest"])
    assert base.record["input_digest"] == stamp["input_digest"]


def test_record_the_stamp_reads_the_shipped_version_constant(project, monkeypatch):
    monkeypatch.setattr(tp, "VERSION", "9.8.7")
    res = project.run()
    assert res.code == 0, res.describe()
    assert tp.read_stamp(project.md)["version"] == "9.8.7", "the goldens read tachi_parts.VERSION, never a literal (D4)"
    assert project.sarif["runs"][0]["properties"]["tachi_provenance"]["version"] == "9.8.7"
    assert project.record["tachi_version"] == "9.8.7"


def test_record_the_stage_record_is_valid_and_complete(base):
    record = base.record
    tp.validate_stage_record(record)
    assert (record["schema"], record["stage"], record["plan_id"]) == ("tachi.stage-record/1", STAGE, base.plan_id)
    assert (record["status"], record["error"], record["tachi_version"]) == ("success", None, tp.VERSION)
    assert DIGEST.match(record["input_digest"])
    assert record["started_utc"] <= record["finished_utc"]
    counts = record["counts"]
    assert (counts["units"], counts["open"], counts["resolved"]) == (len(ORDER), len(ORDER), len(RESOLVED_IDS))
    assert [counts.get(key, 0) for key in ("parse_errors", "narrative_fallbacks", "truncations")] == [0, 0, 0]
    assert record["batches"] == {"planned": 1, "dispatched": 1, "done": 1, "retried": 0, "split": 0, "exhausted": 0}
    assert (record["overflow_events"], record["retries"], record["warnings"], record["undeclared_paths"]) == ([], [], [], [])
    assert sorted(record["outputs"], key=lambda entry: entry["path"]) == sorted(
        [{"path": MD, "sha256": sha256_of(base.out / MD)}, {"path": SARIF, "sha256": sha256_of(base.out / SARIF)}],
        key=lambda entry: entry["path"]), "paths are relative to --out, and each digest is the file in place"


def test_record_an_undeclared_path_exits_5_and_still_writes_both_files(project):
    project.prepare()
    (project.out / "gen.py").write_text("print('a helper nobody declared')\n", encoding="utf-8")
    res = project.render()
    assert res.code == 5, res.describe()
    record = project.record
    assert (record["status"], record["undeclared_paths"]) == ("success-with-warnings", ["gen.py"]), "SC-3 is measured, not gated (KB 17)"
    assert len(project.sarif["runs"][0]["results"]) == len(ORDER) and has_section(project.md, "## 6. Score Integrity")
    tp.validate_stage_record(record)


def test_record_a_path_the_run_changed_but_declared_is_not_reported(project):
    project.earlier()  # the earlier outputs are in the plan's snapshot, so the render changes them: declared
    project.prepare()
    res = project.render()
    assert res.code == 0, res.describe()
    assert project.record["undeclared_paths"] == []


def test_record_every_file_the_run_wrote_is_a_declared_path(base):
    """The renderer's own writes are the stage's canonical files and D3's layout, nothing else (ADR-050 D4)."""
    snapshot = base.plan_json()["out_snapshot"]
    written = []
    for path in sorted(base.out.rglob("*")):
        if path.is_file():
            relpath = path.relative_to(base.out).as_posix()
            status = path.stat()
            if snapshot.get(relpath) != [status.st_size, status.st_mtime_ns]:
                written.append(relpath)
    assert written, "the render wrote files"
    assert [relpath for relpath in written if not tp.is_declared_path(relpath, STAGE, base.plan_id)] == []
    assert {MD, SARIF, ".tachi-build/%s/%s/stage-record.json" % (STAGE, base.plan_id)} <= set(written)


def test_record_a_record_lists_at_most_the_cap_of_undeclared_paths_and_warns_with_the_full_count(project):
    project.prepare()
    extra = 5
    for number in range(tp.MAX_UNDECLARED_PATHS + extra):
        (project.out / ("stray-%04d.txt" % number)).write_text("x\n", encoding="utf-8")
    res = project.render()
    assert res.code == 5, res.describe()
    record = project.record
    assert record["undeclared_paths"] == sorted(record["undeclared_paths"]) and len(record["undeclared_paths"]) == tp.MAX_UNDECLARED_PATHS
    truncated = [warning for warning in record["warnings"] if warning["code"] == "undeclared-paths-truncated"]
    assert len(truncated) == 1 and str(tp.MAX_UNDECLARED_PATHS + extra) in truncated[0]["detail"], "ruled at W1: the full count is in the warning"
    tp.validate_stage_record(record)
    assert len(project.sarif["runs"][0]["results"]) == len(ORDER), "a stray file never stops the render (KB 17)"


# =============================================================================
# 11. Batching: more than one batch, one batch, and a halved batch (NFR-4; ADR-050 D6)
# =============================================================================


def test_batching_a_run_below_the_threshold_invokes_the_agent_once(project, stage):
    res = project.run()
    assert res.code == 0, res.describe()
    plan = project.plan_json()
    assert plan["unit_count"] == len(ORDER) <= stage.BATCH_SIZES[STAGE] and [b["batch_id"] for b in plan["batches"]] == ["B001"]
    assert project.record["batches"]["planned"] == 1 and project.record["batches"]["dispatched"] == 1


def test_batching_the_gated_subset_plans_two_or_more_batches_and_renders_every_row(stage, renderer, tmp_path):
    project, reference = subset_project(stage, renderer, tmp_path)
    res = project.run()
    assert res.code in (0, 5), res.describe()  # the subset's Affected Assets block lists only some findings: a stale block warns

    plan = project.plan_json()
    size = stage.BATCH_SIZES[STAGE]
    planned = [entry for entry in plan["batches"] if entry["parent"] is None]
    assert plan["batch_size"] == size and plan["unit_count"] == len(reference["open"]) == 42
    assert len(planned) == math.ceil(42 / size) >= 2, "every batched path gets two or more batches at the stage's size"
    assert project.record["batches"]["planned"] == len(planned) and project.record["batches"]["done"] == len(planned)

    open_ids = sorted((row["id"] for row in reference["open"]), key=s2_key)
    rows = records(*table_of(section(project.md, "## 2. Scored Threat Table"), "ID"))
    assert sorted((row["ID"] for row in rows), key=s2_key) == open_ids, "one open row per reference-set finding"
    resolved = records(*table_of(section(project.md, "## 2a. Resolved Findings"), "ID"))
    assert [row["ID"] for row in resolved] == [row["id"] for row in reference["resolved"]]
    results = project.sarif["runs"][0]["results"]
    assert len(results) == 42
    sc.self_check(results, tool=TOOL, member_ids=open_ids, assignments={},
                  resolved_ids=[row["id"] for row in reference["resolved"]], uri=URI)
    sorted_rows = sorted(rows, key=lambda row: (-Decimal(row["Composite"]), s2_key(row["ID"])))
    assert [row["ID"] for row in rows] == [row["ID"] for row in sorted_rows], "composite descending, then S-2's order"
    assert project.record["counts"]["open"] == 42 and project.record["counts"]["resolved"] == 3


@pytest.mark.parametrize("batch_size", [1, 2, 4])
def test_batching_a_run_in_several_batches_writes_the_same_bytes_as_one_batch(project, batch_size):
    assert project.run().code == 0
    one = project.outputs()
    res = project.run(batch_size=batch_size)  # the planner's function interface: the one way a test sets a smaller size
    assert res.code == 0, res.describe()
    assert project.record["batches"]["planned"] == math.ceil(len(ORDER) / batch_size) > 1
    assert project.outputs() == one, "the batch boundaries show nowhere in the output (NFR-2)"


def test_batching_a_halved_batch_writes_the_same_bytes_as_one_batch(project):
    assert project.run().code == 0
    one = project.outputs()
    project.plan(batch_size=3)  # B001, B002, B003
    project.write_parts(only={"B002", "B003"})  # B001's agent ran out of room, so it wrote nothing
    first = project.reconcile()
    assert first.code == 3, first.describe()
    pending = sorted(batch["batch_id"] for wave in json.loads(first.out)["waves"] for batch in wave)
    assert pending == ["B001-1", "B001-2"]
    project.write_parts(only=set(pending))
    assert project.reconcile().code == 0
    res = project.render()
    assert res.code == 0, res.describe()
    assert project.outputs() == one
    record = project.record
    # reading: counted as `tachi-stage.py fail` counts them: a halving spends 2 of the retry budget (ADR-050 D6)
    assert record["batches"] == {"planned": 3, "dispatched": 5, "done": 4, "retried": 2, "split": 1, "exhausted": 0}
    events, retries = tp.retry_history(STAGE, project.out, project.plan_json())
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "missing"}]
    assert (record["overflow_events"], record["retries"]) == (events, retries)


# =============================================================================
# 12. Determinism: the clock, the plan ID, the date and the digest (NFR-2; ADR-050 D4, D5)
# =============================================================================


@contextlib.contextmanager
def frozen_clock(moment):
    """Every clock the standard library offers reads ``moment`` (a UTC ``datetime``) while this is active."""
    real_datetime, real_date = datetime.datetime, datetime.date
    real_time, real_ns, real_gmtime, real_localtime = time.time, time.time_ns, time.gmtime, time.localtime

    class FrozenDatetime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return moment if tz is not None else moment.replace(tzinfo=None)

        @classmethod
        def utcnow(cls):
            return moment.replace(tzinfo=None)

        @classmethod
        def today(cls):
            return moment.replace(tzinfo=None)

    class FrozenDate(real_date):
        @classmethod
        def today(cls):
            return real_date(moment.year, moment.month, moment.day)

    datetime.datetime, datetime.date = FrozenDatetime, FrozenDate
    time.time, time.time_ns = (lambda: moment.timestamp()), (lambda: int(moment.timestamp()) * 10 ** 9)
    time.gmtime = lambda seconds=None: real_gmtime(moment.timestamp() if seconds is None else seconds)
    time.localtime = lambda seconds=None: real_localtime(moment.timestamp() if seconds is None else seconds)
    try:
        yield
    finally:
        datetime.datetime, datetime.date = real_datetime, real_date
        time.time, time.time_ns, time.gmtime, time.localtime = real_time, real_ns, real_gmtime, real_localtime


def test_determinism_the_output_is_byte_identical_under_a_patched_clock(project):
    moments = [datetime.datetime(2020, 2, 29, 12, 0, 0, tzinfo=datetime.timezone.utc),
               datetime.datetime(2031, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)]
    runs = []
    for moment in moments:
        with frozen_clock(moment):
            res = project.run()
        assert res.code == 0, res.describe()
        runs.append((project.outputs(), project.plan_id, project.record))
    res = project.run()  # the real clock
    assert res.code == 0, res.describe()
    runs.append((project.outputs(), project.plan_id, project.record))
    assert runs[0][0] == runs[1][0] == runs[2][0], "the clock never enters a rendered file (ADR-050 D5), and the plan ID never does (D4)"
    assert len({plan_id for _outputs, plan_id, _record in runs}) == 3
    for moment, (_outputs, _plan, record) in zip(moments, runs):
        assert record["finished_utc"] == moment.strftime("%Y-%m-%dT%H:%M:%SZ"), "the clock reaches the stage record, and only there"


def test_determinism_rendering_the_same_plan_again_changes_no_byte(project):
    assert project.run().code == 0
    first = project.outputs()
    again = project.render()
    assert again.code == 0, again.describe()
    assert project.outputs() == first


def test_determinism_the_scoring_date_is_the_plans_and_moves_every_date(project):
    assert project.run().code == 0
    first = tp.read_stamp(project.md)["input_digest"]
    res = project.run(date="2027-03-05")
    assert res.code == 0, res.describe()
    assert tachi_parsers.parse_frontmatter(project.md)["date"] == "2027-03-05"
    governed = {row["ID"]: row for row in records(*table_of(section(project.md, "## 4. Governance Fields"), "ID"))}
    for finding_id in ORDER:
        sla = GOVERNANCE[golden(finding_id)[5]][0]
        assert governed[finding_id]["Review Date"] == ts.review_date("2027-03-05", sla)
        assert results_by_id(project.sarif)[finding_id]["properties"]["review-date"] == ts.review_date("2027-03-05", sla)
    assert tp.read_stamp(project.md)["input_digest"] != first, "the date is a parameter of the input digest (ADR-050 D4)"
    scored = [row for row in table_of(subsection_of(project.md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")[1] if row[1] == "scored_on"]
    assert {row[2] for row in scored} == {"2027-03-05"} and len(scored) == len(ORDER)


def test_determinism_the_input_digest_follows_the_inputs_and_not_the_plan(project):
    assert project.run().code == 0
    first = tp.read_stamp(project.md)["input_digest"]
    assert project.run().code == 0 and tp.read_stamp(project.md)["input_digest"] == first, "a fresh plan ID, the same digest"

    def reword(part):
        part["items"][0]["rationale"]["cvss"] = "A different judgment of the base score."

    assert project.run(mutate=reword).code == 0
    assert tp.read_stamp(project.md)["input_digest"] != first, "an accepted part's items are in the digest"


# H8's roots, built in pieces so that this file holds no path itself (the same list as test_fixture_374.py's hygiene check).
H8_ROOTS = ("Us" + "ers", "ho" + "me", "pri" + "vate", "t" + "mp", "var/fol" + "ders")
LOCAL_PATH = re.compile("/(%s)/|(?<![A-Za-z0-9])[A-Za-z]:\\\\[A-Za-z]" % "|".join(H8_ROOTS))


def test_determinism_no_local_path_reaches_either_file(base):
    for text in (base.md, base.sarif_text):
        assert not LOCAL_PATH.search(text), "a local path in the output leaks the layout and differs between machines (NFR-2, NFR-6)"
        for path in {str(base.root), str(base.out), os.path.realpath(str(base.root))}:
            assert path not in text, "the project's own path is in the output: %s" % path


# =============================================================================
# 13. Input Issues: a repeated reference-set ID (the architect's W1 ruling; FR-K6.1)
# =============================================================================


def test_issues_a_repeated_id_is_read_listed_and_warned_and_the_run_exits_5(stage, renderer, tmp_path):
    """The first row wins, and an open row beats a resolved one. ``plan`` warns and exits 0. The renderer lists the IDs
    under Input Issues, writes the warning ``duplicate-finding-id`` and exits 5 (``contracts/part-files.md``)."""
    resolved = RESOLVED + [("E-3", "legacy-gateway", "An older threat on a route that no longer exists.", "Low", "Component removed")]
    project = Project(stage, renderer, tmp_path, resolved=resolved, repeated=[("S-2", "auth-broker")])
    res = project.run()
    assert project.plan_json()["unit_count"] == len(ORDER), "a repeated ID is one unit"
    assert "S-2" in project.plan_stderr and "E-3" in project.plan_stderr, "plan warns on stderr"
    assert res.code == 5, res.describe()
    record = project.record
    assert record["status"] == "success-with-warnings"
    warnings = [warning for warning in record["warnings"] if warning["code"] == "duplicate-finding-id"]
    assert warnings and all(finding_id in " ".join(w["detail"] for w in warnings) for finding_id in ("S-2", "E-3"))
    issues = subsection_of(project.md, "## 6. Score Integrity", "### Input Issues")
    assert "S-2" in issues and "E-3" in issues, "the IDs are listed in the defined place (FR-K6.1)"
    rows = records(*table_of(section(project.md, "## 2. Scored Threat Table"), "ID"))
    assert [row["ID"] for row in rows] == ORDER, "each repeated ID is one open row"
    assert {row["ID"]: row for row in rows}["S-2"]["Component"] == "edge-gateway", "the first row wins"
    resolved_rows = records(*table_of(section(project.md, "## 2a. Resolved Findings"), "ID"))
    assert [row["ID"] for row in resolved_rows] == RESOLVED_IDS, "an open row beats a resolved one: E-3 is not in Section 2a"
    assert len(project.sarif["runs"][0]["results"]) == len(ORDER)
    assert record["counts"]["open"] == len(ORDER) and record["counts"]["resolved"] == len(RESOLVED_IDS)


# =============================================================================
# 14. The agent's narrative: slots, the per-field fallback, cuts and hostile text (ADR-050 D3; PM rulings 1 and 2)
# =============================================================================


def damage_two_fields(part):
    for item in part["items"]:
        if canon(item["finding_id"]) == "T-1":
            item["rationale"]["exploitability"] = "There are 3 known exploits."  # a digit outside a slot
        if canon(item["finding_id"]) == "R-1":
            item["rationale"]["cvss"] = "x" * 401  # one over the limit of 400


def test_narrative_a_bad_field_takes_its_fixed_sentence_and_a_long_one_is_cut_and_both_are_flagged(project):
    res = project.run(mutate=damage_two_fields)
    assert res.code in (0, 5), res.describe()  # reading: a fallback is a flag and a count, not a warning
    fallback_flag, cut_flag = "input:rationale.exploitability:narrative-fallback", "input:rationale.cvss:truncated"

    assert tp.FALLBACK_SENTENCES["rationale.exploitability"] in subsection_for(project.md, "T-1")
    assert "known exploits" not in project.md, "the field's text is gone, and the row is not"
    assert "x" * 400 in subsection_for(project.md, "R-1") and "x" * 401 not in project.md

    flagged = {row["ID"]: row for row in records(*table_of(section(project.md, "## 2. Scored Threat Table"), "ID"))}
    assert flagged["T-1"]["Flags"] == "input" and flagged["R-1"]["Flags"] == "input"
    assert all(flagged[i]["Flags"] == DASH for i in ORDER if i not in ("T-1", "R-1"))

    header, rows = table_of(subsection_of(project.md, "## 6. Score Integrity", "### Score Flags"), "ID")
    found = [(row["ID"], row["Flag"], row["Field"], row["Cause"]) for row in records(header, rows)]
    assert found == [("T-1", "input", "rationale.exploitability", "narrative-fallback"), ("R-1", "input", "rationale.cvss", "truncated")], \
        "in S-2 order of ID, with the flag's three parts in their columns"
    for finding_id, text in (("T-1", "narrative-fallback"), ("R-1", "truncated")):
        line = [line for line in subsection_for(project.md, finding_id).split("\n") if line.startswith("**Integrity**:")]
        assert len(line) == 1 and text in line[0], "an Integrity line for each flagged finding (D9)"
    assert "**Integrity**:" not in subsection_for(project.md, "S-2")

    results = results_by_id(project.sarif)
    assert results["T-1"]["properties"]["score-flags"] == [fallback_flag]
    assert results["R-1"]["properties"]["score-flags"] == [cut_flag]
    assert all(results[i]["properties"]["score-flags"] == [] for i in ORDER if i not in ("T-1", "R-1"))

    counts = project.record["counts"]
    assert counts["narrative_fallbacks"] == 1 and counts["truncations"] == 1 and counts["input"] >= 2

    persisted = {(canon(row[0]), row[1]): row[2] for row in table_of(subsection_of(project.md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")[1]}
    assert persisted[("T-1", "rationale.exploitability")] == tp.FALLBACK_SENTENCES["rationale.exploitability"], "the validated text is what is carried"
    assert persisted[("R-1", "rationale.cvss")] == "x" * 400


def test_narrative_hostile_text_is_raw_in_the_sarif_and_escaped_in_the_markdown(base):
    result = results_by_id(base.sarif)["LLM-4"]
    assert result["message"]["text"] == HOSTILE_THREAT, "SARIF strings go through json.dumps only (ADR-050 D3)"
    assert result["message"]["markdown"] == mitigation_of(by_id("LLM-4"))
    assert results_by_id(base.sarif)["S-10"]["message"]["text"] == by_id("S-10")["threat"]
    assert "\\u00c9tienne" in base.sarif_text and "\\u2014" in base.sarif_text, "non-ASCII is written as an escape"


# =============================================================================
# 14a. The 1.1 template and the renderer agree (D15; they pass when T031 lands, whatever the renderer does)
# =============================================================================

TEMPLATES = REPO_ROOT / "templates" / "tachi" / "output-schemas"


def test_template_the_markdown_template_is_schema_1_1_and_has_the_renderers_headings():
    text = (TEMPLATES / MD).read_text(encoding="utf-8")
    assert re.search(r"Schema version\s*:\s*1\.1\b", text), "D15: risk-scores.md goes from 1.0 to 1.1"
    for heading in SECTION_TITLES + SECTION_6_PARTS:
        assert re.search(r"(?m)^%s\b" % re.escape(heading), text), "the template has no %r, which the renderer writes" % heading
    assert re.search(r"(?m)^\|[^\n]*\| Flags \|\s*$", text), "Sections 2 and 2a gain a trailing Flags column"
    assert "**Integrity**:" in text, "Section 3 gains an Integrity line for each flagged finding"


def test_template_the_sarif_template_carries_the_real_information_uri():
    document = json.loads((TEMPLATES / SARIF).read_text(encoding="utf-8"))
    assert document["runs"][0]["tool"]["driver"]["informationUri"] == sc.INFORMATION_URI, "FR-E.9 (#412)"


# =============================================================================
# 15. The entry's shape (H15)
# =============================================================================


def test_cli_the_entry_keeps_the_populators_shape(renderer):
    parameters = inspect.signature(renderer.main).parameters
    assert list(parameters) == ["argv"] and parameters["argv"].default is None
    tree = ast.parse(RENDERER.read_text(encoding="utf-8"))
    guards = [node for node in tree.body if isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
              and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"]
    assert guards, "a __main__ guard"
    guard = guards[-1]
    assert len(guard.body) == 1 and "main" in ast.dump(guard.body[0]), "a thin guard: the work is in main(argv)"


# =============================================================================
# 16. Peers: correlation groups (D8, D9; needs T044's routing and T048's parser)
# =============================================================================

GROUPS = [("CG-1", ["S-2", "S-10", "T-1"])]  # S-2 is first listed, so it is the primary; S-10 and T-1 are its peers


def test_peers_the_planner_leaves_a_peer_out_and_the_renderer_copies_the_primary(stage, renderer, tmp_path):
    project = Project(stage, renderer, tmp_path, groups=GROUPS)
    project.plan()
    planned = [canon(finding_id) for entry in project.plan_json()["batches"] for finding_id in entry["finding_ids"]]
    assert "S-10" not in planned and "T-1" not in planned, "precondition (T044): a peer is not dispatched, its primary's values are copied (D2)"
    assert "S-2" in planned and len(planned) == len(ORDER) - 2
    project.write_parts()
    assert project.reconcile().code == 0
    res = project.render()
    assert res.code in (0, 5), res.describe()

    rows = {row["ID"]: row for row in records(*table_of(section(project.md, "## 2. Scored Threat Table"), "ID"))}
    assert sorted(rows) == sorted(ORDER), "peers are rows"
    cvss, e, s, reach, composite, band = golden("S-2")
    for peer in ("S-10", "T-1"):
        assert (rows[peer]["CVSS"], rows[peer]["Exploit."], rows[peer]["Scale."], rows[peer]["Reach."], rows[peer]["Composite"],
                rows[peer]["Severity"]) == (cvss, e, s, reach, composite, band), "NEW and UPDATED peers copy their primary (R-31)"
        assert rows[peer]["Component"] == truncate(by_id(peer)["component"], 30), "but keep their own identity"
        body = subsection_for(project.md, peer)
        assert [line for line in body.split("\n") if line.startswith("**Correlation Group**:") and "S-2" in line], peer
    assert project.record["counts"]["units"] == len(ORDER) - 2 and project.record["counts"]["open"] == len(ORDER)
    # D9: Scoring Inputs lists every open finding, so a later run can carry any of them. A peer's rows hold the values it copied.
    inputs = [(canon(row[0]), row[1], row[2]) for row in table_of(subsection_of(project.md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")[1]]
    numeric = [field for field in ("cvss_vector",) + tuple("exploitability." + n for n in tp.SUBSCORE_NAMES[:4])
               + tuple("scalability." + n for n in tp.SUBSCORE_NAMES[4:]) + ("reachability.zone", "reachability.trust_level",
               "reachability.auth_barriers", "reachability.network_boundaries")]
    for finding_id in ORDER:
        assert [row for row in inputs if row[0] == canon(finding_id) and row[1] == "scored_on"], "%s has Scoring Inputs" % finding_id
    for peer in ("S-10", "T-1"):
        assert [(f, v) for i, f, v in inputs if i == canon(peer) and f in numeric] == [(f, v) for i, f, v in inputs if i == "S-2" and f in numeric], peer

    results = results_by_id(project.sarif)
    assert len(results) == len(ORDER), "every peer is a result, once (D8)"
    assignments = sc.correlation_assignments([(group, members) for group, members in GROUPS], ORDER)
    assert sorted(assignments) == ["S-10", "S-2", "T-1"]
    sc.self_check(project.sarif["runs"][0]["results"], tool=TOOL, member_ids=ORDER, assignments=assignments,
                  resolved_ids=RESOLVED_IDS, uri=URI)
    for finding_id, correlation in assignments.items():
        spelled = finding_id
        properties = results[spelled]["properties"]
        assert (properties["correlation-group"], properties["correlation-role"], properties["correlation-primary"]) == (
            correlation.group, correlation.role, correlation.primary)
        assert results[spelled]["message"] == {"text": sc.correlated_message(by_id(spelled)["threat"], correlation),
                                               "markdown": mitigation_of(by_id(spelled))}, "ruling C's sentence ends the text, not the markdown"
        assert "relatedLocations" not in results[spelled], "a peer is a result and never a related location"


# =============================================================================
# 17. S-4's variants: the scenarios, their outcomes, and one render of each (T041; SC-4)
# =============================================================================
#
# T040's scenarios each hold a baseline, a run and ``expected-outcomes.json`` (``tachi.fixture-expected/1``): per
# finding what the baseline ``stored``, what the renderer must write (``rendered``, its whole field set) and the
# ``flags`` it must raise (``{flag, kind, field, cause, stored, rendered, basis}``). Every golden below reads that file,
# so a regenerated variant flows through and no test restates a value. ``pinned`` and ``derived`` flags are required;
# an ``optional`` one may be absent (today: the three missing-SLA flags that wait for S-12(b)'s cause).
#
# How a scenario is run (reading: the outcomes file's ``run.how``). The scenario directory is copied whole into a
# working directory and the renderer runs from there, because ``baseline.source`` and every path are relative to it.
# The architecture file is also put at the default place, ``docs/security/architecture.md``, as in an adopter's
# project: a plan with no batch (every finding carried) holds no ``refs.architecture``, so the renderer finds it by the
# default. The agent's judgment for a finding routed to it comes from the file's ``agent_inputs``.

LARGE_ARCH = REPO_ROOT / "tests" / "scripts" / "fixtures" / "large_arch"
OUTCOMES_NAME, OUTCOMES_SCHEMA = "expected-outcomes.json", "tachi.fixture-expected/1"
SEEDED = "seeded-error/main"
LEGACY_FORMAT = "legacy-format/main"
NO_BASELINE_DATE = "legacy-format/no-baseline-date"
ID_REUSE = "id-reuse/pr1"
TIES = "ties/scorer"
TAGGED = ("tagged/legacy-form", "tagged/renderer-form")
S13 = ("tagged/s13-block-equal", "tagged/s13-stale-block", "tagged/s13-no-architecture", "tagged/s13-neither-source",
       "tagged/s13-drift-form")
SCORER_SCENARIOS = (SEEDED, LEGACY_FORMAT, NO_BASELINE_DATE, ID_REUSE, TIES) + TAGGED + S13
REGROUP, REGROUP_RUNS = "regroup-pair/main", ("run1", "run2", "run3")
CASES = SCORER_SCENARIOS + tuple("%s:%s" % (REGROUP, run) for run in REGROUP_RUNS)
PREFIXES = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")
COLUMN_OF = {"cvss_base": "CVSS", "exploitability": "Exploit.", "scalability": "Scale.", "reachability": "Reach.",
             "composite_score": "Composite", "severity_band": "Severity", "remediation_sla": "SLA", "risk_disposition": "Disposition"}
RENDERED_KEYS = set(COLUMN_OF) | {"cvss_vector", "review_date", "risk_owner"}
FRESH_KEYS = {"score_bounds", "score_source", "scored_on"}  # a fresh finding's rendered set also names these three
VALUE_FIELDS = tuple(COLUMN_OF) + ("risk_owner", "review_date")  # what the markdown shows for a finding, besides the vector
KIND_ORDER = ("corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input")  # the 1.1 template's
S12B_OPEN = ("tagged/s13-drift-form",)  # S-12(b)'s derivation may add one ``input:`` flag, whose cause T032 names (module-signatures.md)

# The scorer's flag vocabulary, closed (module-signatures.md, "The scorer's flag vocabulary, closed"): every string a renderer
# may emit, and nothing else. A rounding-only composite difference has no flag, and a value a tag moved is ``retagged``.
RETAGGED_FIELDS = ("cvss_base", "composite_score", "severity_band", "remediation_sla", "risk_disposition", "review_date")
CLOSED_FLAGS = re.compile("(?:%s)" % "|".join([
    r"corrected:cvss_base:vector",
    r"corrected:(?:composite_score|exploitability|scalability|reachability):arithmetic",
    r"corrected:severity_band:(?:band-mapping|rounding)",
    r"corrected:(?:remediation_sla|risk_disposition):follows-band",
    r"corrected:review_date:(?:follows-band|baseline-date|clock-restarted)",
    r"retagged:(?:%s):asset-tags" % "|".join(RETAGGED_FIELDS),
    r"unverifiable:cvss_base:no-vector",
    r"unchecked:cvss_base:(?:assessed-unrecorded|bound-n17c)",
    r"unchecked:reachability:compound-trust-label",
    r"unchecked:review_date:scoring-date-unknown",
    r"divergent:composite_score:primary=[A-Z]{1,4}-[0-9]{1,6}",
    r"override:(?:remediation_sla|risk_disposition):human",
    r"reused-id:finding_id:baseline",
    r"input:cvss_vector:sources-disagree",
    r"input:reachability:out-of-range",
    r"input:(?:%s):narrative-fallback" % "|".join(re.escape(name) for name in tp.NARRATIVE_FIELDS),
    r"input:(?:%s):truncated" % "|".join(re.escape(name) for name in tp.FLAG_FIELDS),
    r"resolved",
]))


@functools.lru_cache(maxsize=None)
def read_outcomes(name):
    return json.loads((LARGE_ARCH / name / OUTCOMES_NAME).read_text(encoding="utf-8"))


def split_case(case):
    name, _, run = case.partition(":")
    return name, (run or None)


def outcomes_of(case):
    """``(the whole outcomes file, the findings document)``: the same document for a scenario, a run's own for the regroup pair."""
    name, run = split_case(case)
    top = read_outcomes(name)
    return top, (top["runs"][run] if run else top)


def findings_of(case, *names):
    """``[(finding ID, finding)]`` of a case, restricted to the named ``case`` labels when any are given, in file order."""
    return [(finding_id, finding) for finding_id, finding in outcomes_of(case)[1]["findings"].items()
            if not names or finding["case"] in names]


def split_flags(finding):
    """``(required, optional)``: the flag strings of one expected finding, by ``basis``."""
    required = {flag["flag"] for flag in finding["flags"] if flag["basis"] != "optional"}
    return required, {flag["flag"] for flag in finding["flags"] if flag["basis"] == "optional"}


def kind_of(flag):
    return flag.partition(":")[0]


def matches_text(value, text):
    """Whether a JSON ``value`` is the ``text`` the outcomes file holds (``None`` is a value that is not there)."""
    return value is None if text is None else str(value) == text


def brief(mapping, limit=5):
    """A bounded description of a ``{key: detail}`` mapping, for an assertion message."""
    items = sorted(mapping.items(), key=lambda pair: s2_key(pair[0]))[:limit]
    return "%d finding(s), first %d: %s" % (len(mapping), len(items), json.dumps(dict(items), sort_keys=True)[:1600])


def tags_of(top, finding):
    """The tags this run applies to a finding's component, from the outcomes file's one named source."""
    return tuple(top["tag_source"]["tags"].get(finding["component"], ()))


# --------------------------------------------------------------------------- reading a render back

class MdView(object):
    """Sections 2, 2a and 4 of one ``risk-scores.md``, read back by canonical finding ID."""

    def __init__(self, md):
        self.md = md
        self.rows = {canon(row["ID"]): row for row in records(*table_of(section(md, "## 2. Scored Threat Table"), "ID"))}
        self.resolved = ({canon(row["ID"]): row for row in records(*table_of(section(md, "## 2a. Resolved Findings"), "ID"))}
                         if has_section(md, "## 2a. Resolved Findings") else {})
        self.governance = {canon(row["ID"]): row for row in records(*table_of(section(md, "## 4. Governance Fields"), "ID"))}

    def values(self, finding_id):
        """Section 2's eight fields, with the owner and review date of Section 4 (of Section 2a for a RESOLVED row)."""
        key = canon(finding_id)
        row = self.rows[key] if key in self.rows else self.resolved[key]
        governance = self.governance[key] if key in self.rows else row
        out = {field: row[column] for field, column in COLUMN_OF.items()}
        out["risk_owner"], out["review_date"] = governance["Owner"], governance["Review Date"]
        return out

    def subsections(self):
        """Section 3's subsections by canonical ID: the heading and its body."""
        out = {}
        for heading, body in split_headings(section_text(self.md, "## 3. Dimensional Breakdown"), "### "):
            match = re.match(r"### (\S+) " + DASH + " ", heading)
            if match:
                out[canon(match.group(1))] = heading + "\n" + body
        return out


class Rendered(object):
    """One render of a scenario's run, read back: the three tables, Section 3's subsections and the SARIF results."""

    def __init__(self, case, project, result):
        self.case, self.project, self.result = case, project, result
        self.top, self.doc = outcomes_of(case)
        self.view = MdView(project.md)
        self.subsection = self.view.subsections()
        self.results = {canon(key): value for key, value in results_by_id(project.sarif).items()}

    @property
    def md(self):
        return self.project.md

    @property
    def record(self):
        return self.project.record

    def values(self, finding_id):
        return self.view.values(finding_id)

    def emitted(self, finding_id):
        """The flags raised on a finding: the SARIF's ``score-flags`` for an open one, Section 2a's ``Flags`` cell for a RESOLVED one."""
        key = canon(finding_id)
        if key in self.results:
            return set(self.results[key]["properties"]["score-flags"])
        return {"resolved"} if "resolved" in self.view.resolved[key]["Flags"] else set()

    def all_emitted(self):
        return {finding_id: self.emitted(finding_id) for finding_id in self.doc["findings"]}


class ScenarioProject(Project):
    """The project harness over one run directory of a T040 scenario that was copied into ``root``."""

    def __init__(self, stage_module, renderer_module, root, out_dir, has_architecture, baseline_dir, agent_inputs=None):
        self.stage, self.renderer = stage_module, renderer_module
        self.root = Path(root)
        self.out = self.root / out_dir
        self.threats = self.out / "threats.md"
        self.architecture = (self.root / "docs" / "security" / "architecture.md") if has_architecture else None
        self.baseline_dir = (self.root / baseline_dir) if baseline_dir else None
        self.agent_inputs = {canon(key): value for key, value in (agent_inputs or {}).items()}
        self.item_factory = self.agent_item
        self.specs, self.resolved = [], []
        self.plan_id = self.digest = None
        self.plan_stderr = ""
        self.last = None

    def agent_item(self, finding_id):
        assert canon(finding_id) in self.agent_inputs, "the plan routed %s to the agent, and the outcomes file holds no judgment for it" % finding_id
        item = {"finding_id": finding_id}
        item.update(copy.deepcopy(self.agent_inputs[canon(finding_id)]))
        return item

    def run_on(self, date):
        return self.run(date=date, baseline_dir=self.baseline_dir)


def copy_scenario(name, root, top):
    """Copy the scenario into ``root`` (without its outcomes file) and put its architecture file at the default place."""
    shutil.copytree(str(LARGE_ARCH / name), str(root), ignore=shutil.ignore_patterns(OUTCOMES_NAME), dirs_exist_ok=True)
    architecture = top["run"].get("architecture")
    if architecture:
        target = Path(root) / "docs" / "security" / "architecture.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(Path(root) / architecture), str(target))
    return bool(architecture)


def finish(case, project, result):
    assert result.code in (0, 5), "%s did not finish:\n%s" % (case, result.describe())
    return Rendered(case, project, result)


def render_scenario(stage_module, renderer_module, root, name):
    top = read_outcomes(name)
    has_architecture = copy_scenario(name, root, top)
    project = ScenarioProject(stage_module, renderer_module, root, "run", has_architecture, top["run"].get("baseline_dir"),
                              top.get("agent_inputs"))
    return {name: finish(name, project, project.run_on(top["run"]["date"]))}


def render_regroup(stage_module, renderer_module, root):
    """The regroup pair: three runs in sequence, each run's output the next run's baseline (the outcomes file's ``run.how``)."""
    top = read_outcomes(REGROUP)
    copy_scenario(REGROUP, root, top)
    out = {}
    for run in top["run"]["sequence"]:
        project = ScenarioProject(stage_module, renderer_module, root, top["run"]["out_dirs"][run], True, top["runs"][run]["baseline_dir"])
        out["%s:%s" % (REGROUP, run)] = finish("%s:%s" % (REGROUP, run), project, project.run_on(top["run"]["date"]))
    return out


@pytest.fixture(scope="module")
def scenarios(stage, renderer, tmp_path_factory):
    """``scenarios(case)``: the ``Rendered`` of a scenario (the regroup pair's runs by ``regroup-pair/main:runN``), run once per module.

    A failed render is kept and raised again, so the one cause is reported by every test that needs it and nothing re-runs.
    """
    cache = {}

    def get(case):
        name = split_case(case)[0]
        if name not in cache:
            root = tmp_path_factory.mktemp(name.replace("/", "-"))
            try:
                cache[name] = (render_regroup if name == REGROUP else render_scenario)(stage, renderer, root, *([] if name == REGROUP else [name]))
            except Exception as failure:  # noqa: BLE001 -- kept for the next test that asks
                cache[name] = failure
        if isinstance(cache[name], Exception):
            raise cache[name]
        return cache[name][case]

    return get


# =============================================================================
# 18. Harness checks for the variants: no renderer needed
# =============================================================================


def test_harness_every_outcomes_file_this_module_reads_is_well_formed():
    for case in CASES:
        top, doc = outcomes_of(case)
        assert (top["schema"], top["stage"]) == (OUTCOMES_SCHEMA, "risk-score"), case
        assert {"findings", "counts", "routing", "unflagged"} <= set(doc), case
        assert doc["findings"], case
        for finding_id, finding in doc["findings"].items():
            where = "%s %s" % (case, finding_id)
            assert {"case", "component", "flags", "rendered", "stored", "treatment", "form", "normalized"} <= set(finding), where
            assert RENDERED_KEYS <= set(finding["rendered"]) <= RENDERED_KEYS | FRESH_KEYS, where
            assert finding["treatment"] in ("carried", "agent", "copy-primary", "resolved"), where
            for flag in finding["flags"]:
                assert flag["basis"] in ("pinned", "derived", "optional"), where
                assert flag["flag"] == ":".join(part for part in (flag["kind"], flag["field"], flag["cause"]) if part), where


def test_harness_every_expected_flag_is_inside_the_closed_vocabulary():
    """T040's strings and the scorer's closed vocabulary (``module-signatures.md``) are one set."""
    for case in CASES:
        outside = sorted({flag["flag"] for _id, finding in findings_of(case) for flag in finding["flags"]
                          if not CLOSED_FLAGS.fullmatch(flag["flag"])})
        assert not outside, "%s: outside the closed vocabulary: %s" % (case, outside)


def test_harness_the_outcomes_counts_follow_their_own_flags():
    for case in CASES:
        _top, doc = outcomes_of(case)
        findings = doc["findings"]
        by_kind = collections.Counter(kind_of(flag) for finding in findings.values() for flag in split_flags(finding)[0])
        assert doc["counts"]["flags_by_kind"] == dict(by_kind), case
        assert doc["counts"]["findings"] == len(findings), case
        assert doc["counts"]["normalized"] == sum(1 for finding in findings.values() if finding["normalized"]), case
        with_flags = sum(1 for finding in findings.values() if split_flags(finding)[0])
        anything = sum(1 for finding in findings.values() if finding["flags"])
        assert with_flags <= doc["counts"]["findings_with_flags"] <= anything, case
        assert set(doc["unflagged"]) <= {finding_id for finding_id, finding in findings.items() if not finding["flags"]}, case


def test_harness_the_seeded_error_scenario_seeds_every_kind_in_every_one_of_the_12_prefixes():
    """D10's list (PM plan review, finding 2): a wrong score corrected, an own-bound clamp passed and another category's
    bound marked unchecked, for each prefix; and SC-4's other seeded kinds in each prefix too."""
    for label in ("wrong-composite", "wrong-band", "bad-vector", "reach-out-of-range", "missing-vector", "clamp-control", "n17-bound"):
        assert sorted({finding["prefix"] for _id, finding in findings_of(SEEDED, label)}) == sorted(PREFIXES), label
    assert sorted({finding["prefix"] for _id, finding in findings_of(SEEDED)}) == sorted(PREFIXES)


def test_harness_the_readers_read_a_renderer_form_baseline_as_its_stored_values():
    """This module's table readers, run on the one renderer-form file T040 commits, give the values its outcomes call stored."""
    top = read_outcomes("tagged/renderer-form")
    view = MdView((LARGE_ARCH / "tagged/renderer-form" / top["run"]["baseline_dir"] / MD).read_text(encoding="utf-8"))
    wrong = {}
    for finding_id, finding in top["findings"].items():
        got = view.values(finding_id)
        want = {field: finding["stored"][field] for field in VALUE_FIELDS}
        if got != want:
            wrong[finding_id] = {field: (got[field], want[field]) for field in want if got[field] != want[field]}
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("composite,rounded,band", [
    ("4.55", "4.6", "Medium"), ("4.0", "4.0", "Medium"), ("7.0", "7.0", "High"), ("9.0", "9.0", "Critical"),
    ("3.95", "4.0", "Medium"), ("6.95", "7.0", "High"), ("8.95", "9.0", "Critical"), ("3.9", "3.9", "Low"), ("6.9", "6.9", "Medium"),
    ("8.9", "8.9", "High"), ("0.05", "0.1", "Low"), ("9.95", "10.0", "Critical")])
def test_arith_a_sum_that_ends_in_5_rounds_half_up_and_a_boundary_maps_to_the_higher_band(composite, rounded, band):
    """The sums the renderer meets at a tie (R-11): half up to one decimal, then the band. Section 2's column definition
    says 7.0 is High and 9.0 is Critical."""
    assert str(ts.q1(Decimal(composite))) == rounded
    assert ts.band(ts.q1(Decimal(composite))) == band


# =============================================================================
# 19. Every finding of every scenario: its values, its flags, and where each flag shows (SC-4; ADR-050 D9, D10)
# =============================================================================


def labelled(md, label):
    """The text after ``**label**: `` in Section 6 (Integrity Summary's ``Normalized``, ``Baseline source`` and ``Tag source`` lines)."""
    match = re.search(r"^\*\*%s[^*\n]*\*\*: (.*)$" % re.escape(label), section(md, "## 6. Score Integrity"), re.MULTILINE)
    assert match, "Section 6 has no ``**%s**:`` line" % label
    return match.group(1).strip()


def integrity_line(body):
    """The flags on a Section 3 subsection's ``**Integrity**:`` line (``kind:field:cause``, comma-separated), or ``None`` for no such line."""
    lines = [line for line in body.split("\n") if line.startswith("**Integrity**:")]
    assert len(lines) <= 1, "at most one Integrity line per finding"
    if not lines:
        return None
    return {part.strip() for part in decode(lines[0][len("**Integrity**:"):]).split(",") if part.strip()}


def score_flag_rows(md):
    """``{canonical ID: {flag string}}`` of Section 6's Score Flags table, and the rows (a RESOLVED row has no field or cause)."""
    header, rows = table_of(subsection_of(md, "## 6. Score Integrity", "### Score Flags"), "ID")
    assert header == ["ID", "Flag", "Field", "Stored", "Rendered", "Cause"], header
    found = collections.defaultdict(set)
    for row in records(header, rows):
        field, cause = [None if row[name] in (DASH, "") else row[name] for name in ("Field", "Cause")]
        found[canon(row["ID"])].add(":".join(part for part in (row["Flag"], field, cause) if part))
    return found, records(header, rows)


def cell_of(value):
    """A flag's stored or rendered value as its Score Flags cell reads (reading: a flag with no such value shows the dash)."""
    return DASH if value is None else value


def values_off(r):
    """``{finding ID: {field: (what the renderer wrote, what the outcomes file says)}}`` for every finding that differs."""
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        got = r.values(finding_id)
        bad = {field: (got[field], finding["rendered"][field]) for field in VALUE_FIELDS if got[field] != finding["rendered"][field]}
        if bad:
            wrong[finding_id] = bad
    return wrong


def flags_off(r):
    """``{finding ID: {missing, unexpected}}``: a ``pinned`` or ``derived`` flag not raised, and a flag the outcomes don't list."""
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        required, optional = split_flags(finding)
        got = r.emitted(finding_id)
        extra = got - required - optional
        if split_case(r.case)[0] in S12B_OPEN:
            extra = {flag for flag in extra if not flag.startswith("input:")}  # reading: S-12(b)'s own ``input:`` string is not listed yet
        if (required - got) or extra:
            wrong[finding_id] = {"missing": sorted(required - got), "unexpected": sorted(extra)}
    return wrong


@pytest.mark.parametrize("case", CASES)
def test_variants_every_finding_is_rendered_with_the_values_of_its_outcomes(scenarios, case):
    r = scenarios(case)
    findings = r.doc["findings"]
    open_ids = {canon(i) for i, f in findings.items() if f["treatment"] != "resolved"}
    resolved_ids = {canon(i) for i, f in findings.items() if f["treatment"] == "resolved"}
    assert (set(r.view.rows), set(r.view.resolved)) == (open_ids, resolved_ids), "Section 2 holds the open findings and Section 2a the RESOLVED ones"
    wrong = values_off(r)
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_every_finding_carries_exactly_the_flags_of_its_outcomes(scenarios, case):
    r = scenarios(case)
    wrong = flags_off(r)
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_a_finding_carries_at_most_one_flag_for_each_kind_and_field_and_one_for_the_review_date(scenarios, case):
    r = scenarios(case)
    wrong = {}
    for finding_id, flags in r.all_emitted().items():
        pairs = collections.Counter(tuple(flag.split(":")[:2]) for flag in flags)
        dates = [flag for flag in flags if flag.split(":")[1:2] == ["review_date"]]
        if any(count > 1 for count in pairs.values()) or len(dates) > 1:
            wrong[finding_id] = sorted(flags)
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_each_flag_shows_in_the_flags_column_the_integrity_line_and_the_score_flags_table(scenarios, case):
    r = scenarios(case)
    in_table, _rows = score_flag_rows(r.md)
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        key, flags = canon(finding_id), r.emitted(finding_id)
        row = r.view.resolved[key] if finding["treatment"] == "resolved" else r.view.rows[key]
        shown = [] if row["Flags"].strip() in (DASH, "") else re.findall(r"[a-z]+(?:-[a-z]+)*", row["Flags"])
        kinds = [kind for kind in KIND_ORDER + ("resolved",) if kind in {kind_of(flag) for flag in flags}]
        problems = []
        if shown != kinds:
            problems.append("Flags column %r, the kinds in the template's order %r" % (row["Flags"], kinds))
        if finding["treatment"] != "resolved":
            line = integrity_line(r.subsection[key])
            if line != (flags or None):
                problems.append("Integrity line %r" % (sorted(line) if line is not None else None))
            if in_table.get(key, set()) != flags:
                problems.append("Score Flags rows %r" % sorted(in_table.get(key, set())))
        if problems:
            wrong[finding_id] = {"flags": sorted(flags), "problems": problems}
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_the_score_flags_table_gives_each_flags_stored_and_rendered_values(scenarios, case):
    r = scenarios(case)
    _found, rows = score_flag_rows(r.md)
    by_key = {canon(finding_id): finding for finding_id, finding in r.doc["findings"].items()}
    wrong = {}
    for row in rows:
        want = [flag for flag in by_key[canon(row["ID"])]["flags"] if flag["kind"] == row["Flag"] and flag["field"] == row["Field"]]
        if row["Flag"] == "resolved" or not want:
            continue  # an optional flag the outcomes do not list, or an S-12(b) one: flags_off judges those
        if (row["Stored"], row["Rendered"], row["Cause"]) != (cell_of(want[0]["stored"]), cell_of(want[0]["rendered"]), want[0]["cause"]):
            wrong["%s %s" % (row["ID"], want[0]["flag"])] = (row["Stored"], row["Rendered"], row["Cause"])
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_the_sarif_properties_carry_the_flags_the_vector_and_the_score_source(scenarios, case):
    r = scenarios(case)
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        key = canon(finding_id)
        if finding["treatment"] == "resolved":
            assert key not in r.results, "no SARIF file carries a RESOLVED finding (R-30): %s" % finding_id
            continue
        props = r.results[key]["properties"]
        problems = []
        if props["score-flags"] != sorted(set(props["score-flags"])):
            problems.append("score-flags is not sorted and unique: %r" % props["score-flags"])
        if "cvss-vector" not in props or props["cvss-vector"] != finding["rendered"]["cvss_vector"]:
            problems.append("cvss-vector %r, want %r (JSON null when unverifiable)" % (props.get("cvss-vector"), finding["rendered"]["cvss_vector"]))
        want_source = finding["rendered"].get("score_source", "inherited" if finding["treatment"] == "carried" else None)
        if want_source is not None and props.get("score-source") != want_source:  # reading: the template's two words for the Source column
            problems.append("score-source %r, want %r" % (props.get("score-source"), want_source))
        corrections = props.get("score-corrections", [])
        for flag in finding["flags"]:
            if flag["kind"] == "corrected" and flag["basis"] != "optional":
                # reading: D9's {field, from, to, cause}, each value compared as the text the outcomes file holds
                if not any(c.get("field") == flag["field"] and c.get("cause") == flag["cause"] and matches_text(c.get("from"), flag["stored"])
                           and matches_text(c.get("to"), flag["rendered"]) for c in corrections):
                    problems.append("no score-corrections entry for %s" % flag["flag"])
        if problems:
            wrong[finding_id] = problems
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_the_source_column_says_inherited_for_a_carried_finding_and_fresh_for_the_agents(scenarios, case):
    r = scenarios(case)
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        key = canon(finding_id)
        want = {"carried": "inherited", "resolved": "inherited", "agent": "fresh"}.get(finding["treatment"])  # a copied peer: the template is silent
        row = r.view.resolved[key] if finding["treatment"] == "resolved" else r.view.rows[key]
        if want is not None and row["Source"] != want:
            wrong[finding_id] = row["Source"]
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_the_counts_of_the_record_section_6_and_the_executive_summary_are_the_outcomes_counts(scenarios, case):
    r = scenarios(case)
    findings, counts = r.doc["findings"], r.doc["counts"]
    emitted = r.all_emitted()
    got = collections.Counter(kind_of(flag) for flags in emitted.values() for flag in flags)
    optional = collections.Counter(kind_of(flag) for finding in findings.values() for flag in split_flags(finding)[1])
    want = counts["flags_by_kind"]
    open_string = split_case(case)[0] in S12B_OPEN  # reading: S-12(b)'s derivation may add ``input:`` flags the outcomes do not list
    for kind in set(want) | set(got):
        upper = 10 ** 6 if open_string and kind == "input" else want.get(kind, 0) + optional.get(kind, 0)
        assert want.get(kind, 0) <= got.get(kind, 0) <= upper, "%s: %s flags, outcomes %s" % (kind, got.get(kind, 0), want.get(kind, 0))
    record = r.record["counts"]
    opened = sum(1 for finding in findings.values() if finding["treatment"] != "resolved")
    resolved = len(findings) - opened
    assert (record["open"], record["resolved"], record["units"]) == (opened, resolved, len(r.doc["routing"]["to_agent"]))
    for kind in set(got) & tp.COUNT_KEYS:
        assert record.get(kind, 0) == got[kind], "the stage record's %s count is the number of such flags" % kind
    assert [record.get(key, 0) for key in ("narrative_fallbacks", "truncations")] == [0, 0]
    # Section 6: the table of counts by kind and cause, the normalized count, and the baseline source.
    table = collections.Counter()
    for row in records(*table_of(subsection_of(r.md, "## 6. Score Integrity", "### Integrity Summary"), "Kind")):
        table[row["Kind"]] += int(row["Count"])
    assert {kind: count for kind, count in table.items() if kind != "resolved"} == {kind: count for kind, count in got.items() if kind != "resolved"}
    assert int(labelled(r.md, "Normalized")) == counts["normalized"], "rounding-only differences are counted, never flagged"
    assert labelled(r.md, "Baseline source").lower() != "none", "every scenario has a baseline"
    # Section 1: the one templated sentence, and RESOLVED findings counted apart from the distribution.
    bands = collections.Counter(finding["rendered"]["severity_band"] for finding in findings.values() if finding["treatment"] != "resolved")
    sentence = "%d open findings were scored on %s: %d Critical, %d High, %d Medium and %d Low." % (
        opened, r.top["run"]["date"], bands["Critical"], bands["High"], bands["Medium"], bands["Low"])
    summary = section(r.md, "## 1. Executive Summary")
    assert sentence in summary
    if resolved:
        assert re.search(r"Resolved findings\*\*[^\n]*: %d\b" % resolved, summary)


@pytest.mark.parametrize("case", CASES)
def test_variants_every_open_composite_and_band_follow_the_rendered_dimensions(scenarios, case):
    """SC-4's first line: a carried error never survives. Whatever a finding's dimensions are (kept, corrected or retagged),
    its composite is their weighted sum rounded half up and its band is the composite's."""
    r = scenarios(case)
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        if finding["treatment"] == "resolved":
            continue
        got = r.values(finding_id)
        composite = ts.composite(*(Decimal(got[field]) for field in ("cvss_base", "exploitability", "scalability", "reachability")))
        if (str(composite), ts.band(composite)) != (got["composite_score"], got["severity_band"]):
            wrong[finding_id] = (got["composite_score"], got["severity_band"], str(composite), ts.band(composite))
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_variants_the_planner_sends_the_agent_only_the_findings_the_outcomes_route_to_it(scenarios, case):
    r = scenarios(case)
    planned = {canon(finding_id) for entry in r.project.plan_json()["batches"] for finding_id in entry["finding_ids"]}
    assert planned == {canon(finding_id) for finding_id in r.doc["routing"]["to_agent"]}


def test_variants_a_fresh_finding_records_its_bounds_its_source_and_its_date(scenarios):
    """The outcomes file names three more rendered values for a fresh finding in a baseline-aware run (D10: a NEW finding is held
    to its own category's bound, stored as ``score_bounds``): the renderer's persisted inputs hold two of them (D9, Section 6)."""
    r = scenarios(ID_REUSE)
    inputs = collections.defaultdict(dict)
    for row in table_of(subsection_of(r.md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")[1]:
        inputs[canon(row[0])][row[1]] = row[2]
    seen = 0
    for finding_id, finding in findings_of(ID_REUSE):
        if finding["treatment"] != "agent":
            continue
        seen += 1
        rendered = finding["rendered"]
        assert inputs[canon(finding_id)]["score_bounds"] == ",".join(rendered["score_bounds"]), finding_id
        assert inputs[canon(finding_id)]["scored_on"] == rendered["scored_on"], finding_id
        assert r.results[canon(finding_id)]["properties"]["score-source"] == rendered["score_source"], finding_id
    assert seen == len(r.doc["routing"]["to_agent"])


# =============================================================================
# 20. SC-4's statements, one test each (spec "Measurable Outcomes", SC-4; ADR-050 D9 steps 2 to 4 and D10)
# =============================================================================

SEEDED_ERRORS = (  # (the case label, the field its seed breaks, the flag that must correct it)
    ("wrong-composite", "composite_score", "corrected:composite_score:arithmetic"),
    ("wrong-band", "severity_band", "corrected:severity_band:band-mapping"),
    ("bad-vector", "cvss_base", "corrected:cvss_base:vector"),
    ("cascade-composite", "composite_score", "corrected:composite_score:arithmetic"),
    ("cascade-band", "severity_band", "corrected:severity_band:band-mapping"),
)
BOUNDARIES = {"boundary-exact-40": ("4.0", "Medium"), "boundary-exact-70": ("7.0", "High"), "boundary-exact-90": ("9.0", "Critical")}


def test_harness_the_documented_exceptions_and_the_ties_are_listed_as_unflagged():
    """SC-4's "0 documented exceptions are flagged": the clean findings and the own-bound clamps of all 12 prefixes, the exact
    boundaries and the tie that was stored half up, are the outcomes' own list of findings that carry no flag."""
    assert {i for i, _f in findings_of(SEEDED, "clean", "clamp-control")} <= set(outcomes_of(SEEDED)[1]["unflagged"])
    assert {i for i, _f in findings_of(TIES, "tie-stored-as-half-up", *BOUNDARIES)} <= set(outcomes_of(TIES)[1]["unflagged"])


def test_sc4_every_seeded_composite_band_and_vector_error_is_corrected_and_flagged(scenarios):
    r = scenarios(SEEDED)
    missed = {}
    for label, field, flag in SEEDED_ERRORS:
        for finding_id, finding in findings_of(SEEDED, label):
            now = r.values(finding_id)[field]
            if now == finding["stored"][field] or flag not in r.emitted(finding_id):
                missed[finding_id] = {"case": label, "stored": finding["stored"][field], "rendered": now, "flags": sorted(r.emitted(finding_id))}
    assert not missed, brief(missed)
    assert sum(len(findings_of(SEEDED, label)) for label, _field, _flag in SEEDED_ERRORS) >= 3 * len(PREFIXES), "the seed covers every prefix"


def test_sc4_a_seeded_missing_vector_is_unverifiable_keeps_its_score_and_has_a_null_vector(scenarios):
    r = scenarios(SEEDED)
    found = findings_of(SEEDED, "missing-vector")
    assert len(found) == len(PREFIXES)
    wrong = {}
    for finding_id, finding in found:
        props = r.results[canon(finding_id)]["properties"]
        if ("unverifiable:cvss_base:no-vector" not in r.emitted(finding_id) or r.values(finding_id)["cvss_base"] != finding["stored"]["cvss_base"]
                or props.get("cvss-vector", "absent") is not None):
            wrong[finding_id] = {"flags": sorted(r.emitted(finding_id)), "cvss-vector": props.get("cvss-vector", "absent")}
    assert not wrong, brief(wrong)


def test_sc4_an_out_of_range_reachability_under_an_unambiguous_label_is_flagged_and_kept(scenarios):
    r = scenarios(SEEDED)
    found = findings_of(SEEDED, "reach-out-of-range")
    assert len(found) == len(PREFIXES)
    wrong = {finding_id: sorted(r.emitted(finding_id)) for finding_id, finding in found
             if "input:reachability:out-of-range" not in r.emitted(finding_id)
             or r.values(finding_id)["reachability"] != finding["stored"]["reachability"]}
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", CASES)
def test_sc4_no_documented_exception_and_no_clean_finding_is_flagged(scenarios, case):
    r = scenarios(case)
    open_string = split_case(case)[0] in S12B_OPEN  # reading: an ``input:`` flag from S-12(b)'s derivation is outside that scenario's assertions
    wrong = {}
    for finding_id in r.doc["unflagged"]:
        key = canon(finding_id)
        row, line = r.view.rows[key], integrity_line(r.subsection[key])
        flags = {flag for flag in r.emitted(finding_id) if not (open_string and flag.startswith("input:"))}
        if flags or (not open_string and (row["Flags"].strip() != DASH or line is not None)):
            wrong[finding_id] = {"flags": sorted(flags), "Flags column": row["Flags"], "Integrity line": line and sorted(line)}
    assert not wrong, brief(wrong)


def n17_flags(case):
    """``[(finding ID, finding, flag)]``: the ``unchecked`` flags that name a score or a reachability, which a bound or a label leaves open."""
    return [(i, f, flag) for i, f in findings_of(case) for flag in f["flags"]
            if flag["kind"] == "unchecked" and flag["field"] in ("cvss_base", "reachability")]


N17_CASES = tuple(case for case in SCORER_SCENARIOS if n17_flags(case))


@pytest.mark.parametrize("case", N17_CASES)
def test_sc4_n17_dependent_cases_are_unchecked_keep_their_value_and_are_never_reported_as_a_violation(scenarios, case):
    unchecked = n17_flags(case)
    r = scenarios(case)
    wrong = {}
    for finding_id, finding, flag in unchecked:
        field, emitted = flag["field"], r.emitted(finding_id)
        violation = [f for f in emitted if f.startswith("corrected:%s:" % field) or f == "input:reachability:out-of-range"]
        if flag["flag"] not in emitted or r.values(finding_id)[field] != finding["stored"][field] or violation:
            wrong[finding_id] = {"flags": sorted(emitted), "stored": finding["stored"][field], "rendered": r.values(finding_id)[field]}
    assert not wrong, brief(wrong)


def test_harness_the_n17_cases_cover_every_prefix_and_the_tagged_legacy_cases():
    assert set(N17_CASES) >= {SEEDED, "tagged/legacy-form"}
    seeded = [f for _i, f in findings_of(SEEDED) if any(x["kind"] == "unchecked" for x in f["flags"])]
    assert {f["prefix"] for f in seeded if f["case"] == "n17-bound"} == set(PREFIXES)
    assert {f["case"] for f in seeded} >= {"n17-bound", "compound-label"}
    assert {f["case"] for _i, f in findings_of("tagged/legacy-form")} >= {"assessed-unrecorded", "n17-assessed-unrecorded"}


@pytest.mark.parametrize("case", (SEEDED, TIES))
def test_sc4_a_rounding_only_difference_is_normalized_and_counted_and_never_flagged(scenarios, case):
    """R-11: the stored value is the exact value's other one-decimal neighbour and the band, SLA, disposition and review date
    all hold. The composite is normalized to the half-up value, counted in Section 6, and nothing is flagged."""
    r = scenarios(case)
    normalized = [(i, f) for i, f in findings_of(case) if f["normalized"]]
    assert normalized
    wrong = {}
    for finding_id, finding in normalized:
        got, stored = r.values(finding_id), finding["stored"]
        step = abs(Decimal(got["composite_score"]) - Decimal(stored["composite_score"]))
        holds = all(got[field] == stored[field] for field in ("severity_band", "remediation_sla", "risk_disposition", "review_date", "risk_owner"))
        if r.emitted(finding_id) or step != Decimal("0.1") or not holds:
            wrong[finding_id] = {"flags": sorted(r.emitted(finding_id)), "stored": stored["composite_score"], "rendered": got["composite_score"]}
    assert not wrong, brief(wrong)
    assert int(labelled(r.md, "Normalized")) == len(normalized), "counted in the run summary"


def test_sc4_a_rounding_tie_that_moves_the_band_is_a_band_correction_with_rounding_as_its_cause(scenarios):
    """R-11 and R-5: flagged ``corrected:severity_band:rounding`` and never on the composite; the SLA, disposition and review date
    follow the new band, counted from the original scoring date (the stored review date less the stored SLA)."""
    r = scenarios(TIES)
    found = findings_of(TIES, "tie-band-moves-40", "tie-band-moves-70", "tie-band-moves-90")
    assert len(found) == 3
    wrong = {}
    for finding_id, finding in found:
        got, stored, emitted = r.values(finding_id), finding["stored"], r.emitted(finding_id)
        original = datetime.date.fromisoformat(stored["review_date"]) - datetime.timedelta(days=ts.sla_days(stored["remediation_sla"]))
        if ("corrected:severity_band:rounding" not in emitted or any(f.startswith("corrected:composite_score:") for f in emitted)
                or got["review_date"] != ts.review_date(original.isoformat(), got["remediation_sla"])
                or got["severity_band"] == stored["severity_band"]):
            wrong[finding_id] = {"flags": sorted(emitted), "review_date": got["review_date"], "original scoring date": original.isoformat()}
    assert not wrong, brief(wrong)


def test_sc4_a_composite_exactly_on_a_band_boundary_takes_the_higher_band_and_is_not_flagged(scenarios):
    r = scenarios(TIES)
    for label, want in BOUNDARIES.items():
        (finding_id, finding), = findings_of(TIES, label)
        got = r.values(finding_id)
        assert (got["composite_score"], got["severity_band"]) == want and not r.emitted(finding_id) and not finding["normalized"], label


def test_r26_the_legacy_baseline_takes_a_vector_from_the_markdown_else_the_sarif_and_flags_a_disagreement(scenarios):
    """R-26 (US-5 #10): a vector comes from the baseline's markdown or else from its SARIF's ``cvss-vector``; when both carry one and
    they differ the markdown's is used and the disagreement is flagged; with neither the finding is unverifiable and its vector is null."""
    r = scenarios(LEGACY_FORMAT)
    seen, wrong = collections.Counter(), {}
    for finding_id, finding in findings_of(LEGACY_FORMAT):
        markdown, sarif = finding["vector_sources"]["markdown"], finding["vector_sources"]["sarif"]
        disagree = bool(markdown and sarif and markdown != sarif)
        seen[("md" if markdown else "") + ("sarif" if sarif else "") + ("-disagree" if disagree else "")] += 1
        emitted, props = r.emitted(finding_id), r.results[canon(finding_id)]["properties"]
        if (props.get("cvss-vector", "absent") != (markdown or sarif or None) or ("input:cvss_vector:sources-disagree" in emitted) != disagree
                or ("unverifiable:cvss_base:no-vector" in emitted) != (not (markdown or sarif))):
            wrong[finding_id] = {"vector sources": finding["vector_sources"], "cvss-vector": props.get("cvss-vector", "absent"), "flags": sorted(emitted)}
    assert not wrong, brief(wrong)
    assert set(seen) >= {"md", "sarif", "mdsarif", "mdsarif-disagree", ""}, dict(seen)


R25_KEPT = (  # (scenario, case label, where its stored score sits against the 9.2 ceiling)
    ("tagged/renderer-form", "r25-assessed-above-ceiling", "above"), ("tagged/renderer-form", "r25-ceiling-binds", "at"),
    ("tagged/renderer-form", "r25-tag-is-no-op", "below"), ("tagged/legacy-form", "ceiling-pass", "at"),
    ("tagged/legacy-form", "documented-pass", "below"), ("tagged/legacy-form", "assessed-unrecorded", "above"),
    ("tagged/legacy-form", "n17-assessed-unrecorded", "above"))


@pytest.mark.parametrize("case,label,side", R25_KEPT)
def test_r25_a_tagged_finding_that_already_holds_the_asset_outcome_keeps_its_score_and_is_flagged_only_when_unrecorded(scenarios, case, label, side):
    """R-25: a finding's score is the larger of its assessed score and its elevated score capped at 9.2, so a finding assessed above
    9.2 keeps its score and a no-op tag changes nothing. A carried legacy score above 9.2 that may be only an elevated one is
    kept and reported ``unchecked``, never as a violation."""
    r = scenarios(case)
    (finding_id, finding), = findings_of(case, label)
    got = Decimal(r.values(finding_id)["cvss_base"])
    assert str(got) == finding["stored"]["cvss_base"], "kept"
    assert {"above": got > ts.MODIFIER_CEILING, "at": got == ts.MODIFIER_CEILING, "below": got < ts.MODIFIER_CEILING}[side]
    unrecorded = label.endswith("assessed-unrecorded")
    assert r.emitted(finding_id) == ({"unchecked:cvss_base:assessed-unrecorded"} if unrecorded else set())


# =============================================================================
# 21. The regroup pair: a regroup alone moves no carried score, and peers follow R-31 (US-5 #6; D9 "Peers")
# =============================================================================


def regroup_runs(scenarios):
    return [scenarios("%s:%s" % (REGROUP, run)) for run in REGROUP_RUNS]


def test_regroup_a_regroup_alone_changes_no_carried_findings_score_band_sla_owner_or_review_date(scenarios):
    runs = regroup_runs(scenarios)
    compared, wrong = 0, {}
    for before, after in zip(runs, runs[1:]):
        for finding_id, finding in after.doc["findings"].items():
            if finding["treatment"] == "carried" and canon(finding_id) in before.view.rows:
                compared += 1
                if after.values(finding_id) != before.values(finding_id):
                    wrong["%s %s" % (after.case, finding_id)] = (before.values(finding_id), after.values(finding_id))
    assert compared >= 2 * 8, "run 2 and run 3 carry every finding of the run before"
    assert not wrong, brief(wrong)


def test_regroup_new_and_updated_peers_copy_their_primary_and_an_unchanged_peer_keeps_its_own_score_and_is_flagged(scenarios):
    divergent = []
    wrong = {}
    for r in regroup_runs(scenarios):
        for peer, primary in r.doc["routing"]["copy_primary"].items():
            a, b = r.values(peer), r.values(primary)
            same = all(a[field] == b[field] for field in ("cvss_base", "exploitability", "scalability", "reachability", "composite_score", "severity_band"))
            if not same or r.results[canon(peer)]["properties"]["cvss-vector"] != r.results[canon(primary)]["properties"]["cvss-vector"]:
                wrong["%s %s" % (r.case, peer)] = "does not copy %s" % primary
        for peer, primary in r.doc["routing"]["carried_peers"].items():
            own, theirs = r.values(peer)["composite_score"], r.values(primary)["composite_score"]
            flag = "divergent:composite_score:primary=%s" % primary
            if (flag in r.emitted(peer)) != (own != theirs) or own != r.doc["findings"][peer]["stored"]["composite_score"]:
                wrong["%s %s" % (r.case, peer)] = {"own": own, "primary": theirs, "flags": sorted(r.emitted(peer))}
            if own != theirs:
                divergent.append((r.case, peer))
    assert not wrong, brief(wrong)
    assert {case for case, _peer in divergent} == {"%s:run2" % REGROUP, "%s:run3" % REGROUP}, "the two divergent peers stay flagged on the re-run"


# =============================================================================
# 22. Ruling A (tag-driven moves), ruling B (a reused ID) and D9's review-date fallbacks
# =============================================================================

BAND_ORDER = ("Low", "Medium", "High", "Critical")
RETAG_SCENARIOS = TAGGED + S13
BAND_FOLLOWERS = ("severity_band", "remediation_sla", "risk_disposition", "review_date")


def tag_moves(direction=None, cases=RETAG_SCENARIOS):
    """``[(case, finding ID, finding, "up" | "down")]``: the findings of the tagged scenarios whose band only a tag moved."""
    out = []
    for case in cases:
        for finding_id, finding in findings_of(case):
            if "retagged:severity_band:asset-tags" in split_flags(finding)[0]:
                way = "up" if BAND_ORDER.index(finding["rendered"]["severity_band"]) > BAND_ORDER.index(finding["stored"]["severity_band"]) else "down"
                if direction in (None, way):
                    out.append((case, finding_id, finding, way))
    return out


def band_holds_moves(cases=RETAG_SCENARIOS):
    """The findings whose CVSS score or composite a tag moved and whose band it left (PM-T7)."""
    return [(case, finding_id, finding) for case in cases for finding_id, finding in findings_of(case)
            if split_flags(finding)[0] & {"retagged:cvss_base:asset-tags", "retagged:composite_score:asset-tags"}
            and "retagged:severity_band:asset-tags" not in split_flags(finding)[0]]


UP_CASES = tuple(case for case in RETAG_SCENARIOS if tag_moves("up", (case,)))
DOWN_CASES = tuple(case for case in RETAG_SCENARIOS if tag_moves("down", (case,)))
HOLD_CASES = tuple(case for case in RETAG_SCENARIOS if band_holds_moves((case,)))


def test_harness_the_tagged_scenarios_cover_both_directions_both_review_date_cases_an_override_and_the_legacy_case():
    ups, downs = tag_moves("up"), tag_moves("down")
    assert ups and downs
    date = outcomes_of(TAGGED[0])[0]["run"]["date"]
    later = [m for m in ups if m[2]["stored"]["review_date"] > ts.review_date(date, m[2]["rendered"]["remediation_sla"])]
    earlier = [m for m in ups if m[2]["stored"]["review_date"] <= ts.review_date(date, m[2]["rendered"]["remediation_sla"])]
    assert later and earlier, "an up move whose stored review date is later, and one whose is earlier, than this run's date plus the new SLA"
    assert [m for m in ups if "override:remediation_sla:human" in split_flags(m[2])[0]], "an SLA override on an up move"
    assert [m for m in ups if m[0] == "tagged/legacy-form" and m[2]["form"] == "legacy"], "ruling A's legacy case"
    assert band_holds_moves(), "PM-T7: a tag move that leaves the band"


@pytest.mark.parametrize("case", UP_CASES)
def test_ruling_a_a_band_that_only_the_tags_raise_restarts_the_clock_but_never_past_the_stored_review_date(scenarios, case):
    """Up: the review date becomes this run's scoring date plus the new SLA, unless the stored review date is earlier, in which
    case the stored date is kept. An SLA override still keeps its review date (R-31). Tagging never makes a finding overdue."""
    moves = tag_moves("up", (case,))
    r = scenarios(case)
    wrong = {}
    for _case, finding_id, finding, _way in moves:
        got, stored = r.values(finding_id), finding["stored"]
        if "override:remediation_sla:human" in r.emitted(finding_id):
            want = stored["review_date"]
        else:
            want = min(stored["review_date"], ts.review_date(r.top["run"]["date"], got["remediation_sla"]))
        if got["review_date"] != want:
            wrong[finding_id] = {"review_date": got["review_date"], "want": want}
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", DOWN_CASES)
def test_ruling_a_a_band_that_only_a_removed_tag_lowers_keeps_the_original_scoring_date(scenarios, case):
    """Down: the original scoring date is kept, as for a correction (R-5), so a deadline missed under the lower band's SLA stays missed."""
    moves = tag_moves("down", (case,))
    r = scenarios(case)
    wrong = {}
    for _case, finding_id, finding, _way in moves:
        got, stored = r.values(finding_id), finding["stored"]
        original = datetime.date.fromisoformat(stored["review_date"]) - datetime.timedelta(days=ts.sla_days(stored["remediation_sla"]))
        if got["review_date"] != ts.review_date(original.isoformat(), got["remediation_sla"]) or "retagged:review_date:asset-tags" not in r.emitted(finding_id):
            wrong[finding_id] = {"review_date": got["review_date"], "original scoring date": original.isoformat(), "flags": sorted(r.emitted(finding_id))}
    assert not wrong, brief(wrong)


def test_ruling_a_a_legacy_row_that_records_no_tags_reads_the_elevation_this_runs_tags_apply_as_a_retag(scenarios):
    """The first renderer run ends the UNCHANGED exemption (D9), so the upgrade itself must not read as a correction or make
    a carried finding overdue: a legacy row's band change that only this run's tags explain is ``retagged``, and its review date is no later."""
    r = scenarios("tagged/legacy-form")
    moved = [(i, f) for case, i, f, _way in tag_moves() if case == "tagged/legacy-form"]
    assert moved and all(finding["form"] == "legacy" for _i, finding in moved)
    for finding_id, finding in moved:
        emitted = r.emitted(finding_id)
        assert "retagged:severity_band:asset-tags" in emitted and not [f for f in emitted if f.startswith("corrected:")], finding_id
        assert r.values(finding_id)["review_date"] <= finding["stored"]["review_date"], "%s: the upgrade makes nothing overdue" % finding_id


@pytest.mark.parametrize("case", RETAG_SCENARIOS)
def test_ruling_a_no_value_that_a_tag_moves_or_that_follows_a_tag_moved_band_is_flagged_corrected(scenarios, case):
    """PM confirmation, ruling 1: a retagged finding carries no ``corrected`` flag on any value the tags moved, ``follows-band`` included."""
    r = scenarios(case)
    wrong = {}
    for finding_id, flags in r.all_emitted().items():
        if any(flag.startswith("retagged:") for flag in flags):
            bad = sorted(flag for flag in flags if flag.startswith("corrected:") and flag.split(":")[1] in RETAGGED_FIELDS)
            if bad:
                wrong[finding_id] = bad
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", HOLD_CASES)
def test_ruling_a_a_tag_move_that_leaves_the_band_is_flagged_retagged_and_changes_nothing_that_follows_the_band(scenarios, case):
    """PM-T7: the CVSS score and composite move and are flagged ``retagged``; the band, SLA, disposition and review date hold, and none is flagged."""
    moves = band_holds_moves((case,))
    r = scenarios(case)
    wrong = {}
    for _case, finding_id, finding in moves:
        got, stored, emitted = r.values(finding_id), finding["stored"], r.emitted(finding_id)
        followers = [flag for flag in emitted if flag.split(":")[1] in BAND_FOLLOWERS and flag.startswith(("retagged:", "corrected:"))]
        if followers or any(got[field] != stored[field] for field in BAND_FOLLOWERS + ("risk_owner",)) or not split_flags(finding)[0] <= emitted:
            wrong[finding_id] = {"flags": sorted(emitted), "values": got}
    assert not wrong, brief(wrong)


def test_ruling_b_a_new_finding_whose_id_the_baseline_used_is_flagged_scored_fresh_and_inherits_nothing(scenarios):
    r = scenarios(ID_REUSE)
    (finding_id, finding), = findings_of(ID_REUSE, "reused-id")
    assert "reused-id:finding_id:baseline" in r.emitted(finding_id)
    assert canon(finding_id) in {canon(i) for i in r.doc["routing"]["to_agent"]} and finding["treatment"] == "agent", "it goes to the agent, never to the carried set"
    old = rules.read_baseline_scores(LARGE_ARCH / ID_REUSE / "baseline" / MD).rows[canon(finding_id)]
    got = r.values(finding_id)
    assert old.owner not in (None, "Unassigned"), "precondition: the baseline's row is another finding's, with a human owner"
    assert got["risk_owner"] == "Unassigned" and got["risk_disposition"] != old.disposition and got["review_date"] != old.review_date.isoformat(), \
        "nothing of the old row (its owner, disposition and review date) reaches the new finding"
    props = r.results[canon(finding_id)]["properties"]
    assert props["score-source"] == "fresh" and "reused-id:finding_id:baseline" in props["score-flags"]
    (control_id, _control), = findings_of(ID_REUSE, "new-finding")
    assert r.emitted(control_id) == set(), "a NEW finding with a number the baseline never used is scored fresh and not flagged"
    (resolved_id, _resolved), = findings_of(ID_REUSE, "resolved")
    assert r.emitted(resolved_id) == {"resolved"}, "a RESOLVED finding whose baseline row exists is carried verbatim, not a reuse"


REVIEW_RUNGS = {  # D9's fallback, in order: the baseline file's front matter date, else the stored review date kept, else the run date plus the SLA
    "corrected:review_date:baseline-date": "frontmatter_date",
    "unchecked:review_date:scoring-date-unknown": "stored",
    "corrected:review_date:clock-restarted": "run date",
}


def test_ruling_each_review_date_fallback_rung_raises_its_one_flag_and_counts_from_its_own_start(scenarios):
    seen, wrong = collections.Counter(), {}
    for case in (LEGACY_FORMAT, NO_BASELINE_DATE):
        r = scenarios(case)
        for finding_id, finding in findings_of(case):
            rung = [flag for flag in split_flags(finding)[0] if flag in REVIEW_RUNGS]
            if not rung:
                continue
            got = r.values(finding_id)
            start = {"frontmatter_date": r.top["baseline"]["frontmatter_date"], "run date": r.top["run"]["date"], "stored": None}[REVIEW_RUNGS[rung[0]]]
            want = finding["stored"]["review_date"] if start is None else ts.review_date(start, got["remediation_sla"])
            dated = [flag for flag in r.emitted(finding_id) if flag.split(":")[1] == "review_date"]
            seen[rung[0]] += 1
            if dated != rung or got["review_date"] != want:
                wrong["%s %s" % (case, finding_id)] = {"flags": dated, "review_date": got["review_date"], "want": want}
    assert not wrong, brief(wrong)
    assert set(seen) == set(REVIEW_RUNGS), dict(seen)


# =============================================================================
# 23. S-13: one source of asset tags for the whole run, never mixed (FR-N16.2; PM-T4, AR-T4)
# =============================================================================


def tag_source_matches(line, source):
    """Whether Section 6's ``**Tag source**:`` line names ``source``. Reading: the 1.1 template's words are the ``threats.md``
    block, the architecture file's own tags, or none, "marked unverified when the block was used and no architecture file existed"."""
    low = line.lower()
    return {"block": "block" in low and "unverified" not in low, "recomputed": "architecture" in low or "recomputed" in low,
            "block-unverified": "block" in low and "unverified" in low, "none": "none" in low}[source]


@pytest.mark.parametrize("case", S13)
def test_s13_the_run_reads_its_asset_tags_from_one_source_and_never_mixes_two(scenarios, case):
    """Each branch: a block equal to the recomputation, a stale block, no architecture file, neither source, and a drift form. The
    source is chosen once, so every result's ``affected_assets`` (the SARIF's own property) is that source's tags for its component,
    and the values are the ones that source gives (the generic goldens read those). A branch that cannot verify or find a source
    warns, records its cause in the stage record and finishes: it never stops the run."""
    r = scenarios(case)
    source = r.top["tag_source"]
    line = labelled(r.md, "Tag source")
    assert tag_source_matches(line, source["source"]), "Section 6 names the %r source, not %r" % (source["source"], line)
    wrong = {}
    for finding_id, finding in r.doc["findings"].items():
        want = sorted(source["tags"].get(finding["component"], []))
        got = sorted(r.results[canon(finding_id)]["properties"].get("affected_assets", []))
        if got != want:
            wrong[finding_id] = {"component": finding["component"], "affected_assets": got, "the one source": want}
    assert not wrong, brief(wrong)
    if source["warning"] and source["source"] != "block-unverified":
        # reading: ADR-050 D2 says an unverified block is "recorded as unverified" (Section 6 above) and warns only for the
        # recomputed and the neither-source branches, while the outcomes file also warns for it: an open ruling, so it is not asserted.
        detail = " ".join("%s %s" % (warning["code"], warning["detail"]) for warning in r.record["warnings"])
        assert (r.result.code, r.record["status"]) == (5, "success-with-warnings"), r.result.describe()
        assert re.search(r"tag|asset", detail, re.I), "the cause is in the stage record: %r" % detail


# =============================================================================
# 24. A baseline that cannot be used: free text, a missing file, an unreadable one (R-6; S-12(d); US-5 #11)
# =============================================================================

UNUSABLE_BASELINES = (("free-text", "free-text"), ("missing", "missing"), ("not-utf8", "not-utf8"), ("no-rows", "no-rows"))


def unusable_baseline_project(stage_module, renderer_module, root, how):
    """The nine-finding project whose ``baseline.source`` is free text, names a file that is not there, or names files that cannot be read."""
    source = "the scan from last week, before the rewrite" if how == "free-text" else "earlier/threats.md"
    project = Project(stage_module, renderer_module, root, baseline_source=source)
    if how in ("not-utf8", "no-rows"):
        earlier = Path(root) / "earlier"
        earlier.mkdir()
        shutil.copyfile(str(project.threats), str(earlier / "threats.md"))
        (earlier / MD).write_bytes(b"# Risk Scores Report\n\xff\xfe not text \x80\n" if how == "not-utf8"
                                   else "# Risk Scores Report\n\nNothing was scored.\n".encode("utf-8"))
    return project


@pytest.mark.parametrize("how,reason", UNUSABLE_BASELINES)
def test_baseline_one_that_cannot_be_used_means_every_finding_is_scored_fresh_and_the_reason_is_recorded(stage, renderer, tmp_path, how, reason):
    """D9: free text (#379), an unresolvable path, a failed check or a missing file means no baseline, and a present file that is not
    UTF-8 or yields no row counts as missing, with Section 6 saying that its owners, SLAs and dispositions weren't carried (S-12(d))."""
    project = unusable_baseline_project(stage, renderer, tmp_path, how)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert reason in project.plan_stderr, "the planner says why: %r" % project.plan_stderr
    assert project.plan_json()["unit_count"] == len(ORDER), "every finding, UNCHANGED ones too, goes to the agent"
    view = MdView(project.md)
    for finding_id in ORDER:
        cvss, e, s, reach, composite, band = golden(finding_id)
        sla, _disposition, review = GOVERNANCE[band]
        got = view.values(finding_id)
        assert [got[f] for f in ("cvss_base", "exploitability", "scalability", "reachability", "composite_score", "severity_band")] == [cvss, e, s, reach, composite, band]
        assert (got["risk_owner"], got["remediation_sla"], got["review_date"]) == ("Unassigned", sla, review), "fresh governance (R-5)"
        assert view.rows[canon(finding_id)]["Source"] == "fresh"
    integrity = section(project.md, "## 6. Score Integrity")
    why = integrity + " " + " ".join("%s %s" % (warning["code"], warning["detail"]) for warning in project.record["warnings"])
    assert reason in why, "the stage records why, in Section 6 or its warnings (D9)"
    assert labelled(project.md, "Baseline source").lower() == "none"
    if how in ("not-utf8", "no-rows"):
        issues = subsection_of(project.md, "## 6. Score Integrity", "### Input Issues")
        assert issues.strip() != "None." and MD in issues, "Input Issues names the unreadable file"


# =============================================================================
# 25. A second run on the first run's own 1.1 file: carried prose re-resolves against this run's values (RR1; AR-T4)
# =============================================================================

TAGGED_ARCHITECTURE = '```mermaid\nflowchart LR\n    edge_gateway["edge-gateway<br/>[asset:secrets]"]\n```\n'


def edit_table_cell(md, title, finding_id, column, value):
    """``md`` with one cell of one row replaced: the first table under the ``##`` heading ``title``, and the row whose first cell is ``finding_id``."""
    lines = md.split("\n")
    start = next(n for n, line in enumerate(lines) if line.startswith(title))
    header = None
    for n in range(start + 1, len(lines)):
        if lines[n].startswith("## "):
            break
        if header is None and lines[n].startswith("|"):
            header = [cell.strip() for cell in lines[n].strip().strip("|").split("|")]
        elif header is not None and lines[n].startswith("| %s |" % finding_id):
            cells = lines[n].split("|")
            cells[header.index(column) + 1] = " %s " % value
            lines[n] = "|".join(cells)
            return "\n".join(lines)
    raise AssertionError("no row for %s under %s" % (finding_id, title))


def edit_section_2_cell(md, finding_id, column, value):
    """``md`` with one cell of one Section 2 row replaced: the stored value that the next run reads back."""
    return edit_table_cell(md, "## 2. Scored Threat Table", finding_id, column, value)


def second_run(stage_module, renderer_module, root, first, edit_baseline=None, architecture_text=None, specs=None):
    """The nine findings again (or ``specs``), every one UNCHANGED, with the first run's own ``threats.md``, ``risk-scores.md`` and SARIF as the baseline."""
    project = Project(stage_module, renderer_module, root, specs=[dict(item, status="UNCHANGED") for item in (SPECS if specs is None else specs)],
                      baseline_source="baseline/threats.md")
    baseline = Path(root) / "baseline"
    baseline.mkdir()
    for name in ("threats.md", MD, SARIF):
        shutil.copyfile(str(first.out / name), str(baseline / name))
    if edit_baseline is not None:
        (baseline / MD).write_text(edit_baseline((baseline / MD).read_text(encoding="utf-8")), encoding="utf-8")
    if architecture_text is not None:
        project.architecture.write_text(architecture_text, encoding="utf-8")
    return project


def has_prose(body, item, field, values):
    """Whether Section 3's ``body`` holds the agent's ``field`` sentence with its slots filled by ``values`` (a golden's six values)."""
    return any(tp.resolve_narrative(RATIONALE[field], STAGE, lookup_for(item, composite=values), sink=sink) in body for sink in ("prose", "cell"))


def test_rr1_a_second_run_on_the_first_runs_own_file_carries_every_finding_and_its_prose_with_no_fallback(stage, renderer, base, tmp_path):
    project = second_run(stage, renderer, tmp_path, base)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert project.plan_json()["unit_count"] == 0, "the first run's file is a usable baseline: nothing goes to the agent"
    counts = project.record["counts"]
    assert (counts.get("narrative_fallbacks", 0), counts.get("truncations", 0)) == (0, 0), "zero fallbacks on carried prose"
    first, view, results = MdView(base.md), MdView(project.md), results_by_id(project.sarif)
    for finding_id in ORDER:
        assert results[finding_id]["properties"]["score-flags"] == [], "nothing moved, so nothing is flagged: %s" % finding_id
        assert view.values(finding_id) == first.values(finding_id), finding_id
        body = subsection_for(project.md, finding_id)
        for field in RATIONALE:
            assert has_prose(body, by_id(finding_id), field, golden(finding_id)), (finding_id, field)
        assert "{{" not in body, "no slot token survives into Section 3: %s" % finding_id


def test_rr1_a_corrected_value_moves_in_the_carried_prose(stage, renderer, base, tmp_path):
    stale = "3.3"
    project = second_run(stage, renderer, tmp_path, base, edit_baseline=lambda text: edit_section_2_cell(text, "S-2", "CVSS", stale))
    res = project.run()
    assert res.code in (0, 5), res.describe()
    flags = results_by_id(project.sarif)["S-2"]["properties"]["score-flags"]
    assert "corrected:cvss_base:vector" in flags and not [flag for flag in flags if flag.endswith(":narrative-fallback")], flags
    body = subsection_for(project.md, "S-2")
    assert has_prose(body, by_id("S-2"), "cvss", golden("S-2")), "the sentence's score slot takes this run's corrected value"
    assert stale not in body, "and the baseline's stale value is nowhere in the prose"
    assert project.record["counts"].get("narrative_fallbacks", 0) == 0


def test_rr1_a_retagged_value_moves_in_the_carried_prose_and_leaves_the_band_with_no_correction(stage, renderer, base, tmp_path):
    """A tag the first run did not apply raises S-2's CVSS score and composite and leaves its band (PM-T7); E-3 shares the component and
    its vector already carries every bit the tag forces, so its tag is a no-op and it is not flagged."""
    project = second_run(stage, renderer, tmp_path, base, architecture_text=make_architecture_md() + "\n" + TAGGED_ARCHITECTURE)
    res = project.run()
    assert res.code in (0, 5), res.describe()  # reading: the input block names no tag, so S-13 recomputes it and warns
    cvss, e, s, reach, _composite, band = golden("S-2")
    raised = rules.cvss_chain(by_id("S-2")["vector"], tags=("secrets",), score_bounds=None).cvss_base
    moved = ts.composite(raised, Decimal(e), Decimal(s), Decimal(reach))
    assert raised > Decimal(cvss) and ts.band(moved) == band, "precondition: the tag raises the score and the band holds"
    values = (str(raised), e, s, reach, str(moved), band)
    view = MdView(project.md)
    got = view.values("S-2")
    assert (got["cvss_base"], got["composite_score"], got["severity_band"]) == (str(raised), str(moved), band)
    before = MdView(base.md).values("S-2")
    assert (got["remediation_sla"], got["review_date"], got["risk_owner"]) == (before["remediation_sla"], before["review_date"], before["risk_owner"])
    results = results_by_id(project.sarif)
    flags = results["S-2"]["properties"]["score-flags"]
    assert {"retagged:cvss_base:asset-tags", "retagged:composite_score:asset-tags"} <= set(flags)
    assert not [flag for flag in flags if flag.startswith("corrected:") or flag.split(":")[1] in BAND_FOLLOWERS], flags
    assert results["E-3"]["properties"]["score-flags"] == [], "a no-op tag changes nothing and is not flagged"
    assert has_prose(subsection_for(project.md, "S-2"), by_id("S-2"), "cvss", values), "the carried sentence shows the retagged score"
    assert project.record["counts"].get("narrative_fallbacks", 0) == 0


# =============================================================================
# 26. tachi_scoring_rules at the renderer's boundary: the scenarios' baselines, read and checked directly (R-26, R-25, D10, S-13)
# =============================================================================
#
# These need no renderer. They run the shipped rules module over the committed baselines and compare with what each outcomes file
# says, so a disagreement between T040's expectations and R1b's module shows here, before it shows as a renderer failure. They do not
# repeat ``test_tachi_scoring_rules.py``: that module's cases are synthetic, and these are the fixture's.

RULE_CASES = SCORER_SCENARIOS + ("%s:run1" % REGROUP,)  # the regroup pair's runs 2 and 3 read a renderer's own output, which has no fixture file


@pytest.fixture(scope="module")
def populator():
    return _load_hyphenated_script("populate_affected_assets_variants_test", "populate-affected-assets.py")


def baseline_of(case):
    """``(outcomes file, findings document, BaselineScores)`` for the baseline files that a scenario commits."""
    name, _run = split_case(case)
    top, doc = outcomes_of(case)
    folder = LARGE_ARCH / name / doc.get("baseline_dir", top["run"].get("baseline_dir"))
    sarif = folder / SARIF
    return top, doc, rules.read_baseline_scores(folder / MD, sarif_path=sarif if sarif.is_file() else None)


@pytest.mark.parametrize("case", RULE_CASES)
def test_rules_the_tolerant_reader_gives_each_baseline_row_the_values_the_outcomes_call_stored(case):
    top, doc, scores = baseline_of(case)
    assert scores.readable, scores.reason
    assert scores.form == ("renderer" if top["baseline"]["form"] == "renderer" else "legacy")
    assert (scores.frontmatter_date.isoformat() if scores.frontmatter_date else None) == top["baseline"]["frontmatter_date"]
    wrong = {}
    for finding_id, finding in doc["findings"].items():
        stored = finding["stored"]
        if stored is None:
            continue
        key = canon(finding_id)
        row = scores.rows.get(key) or scores.resolved_rows.get(key)
        if row is None:
            wrong[finding_id] = "no baseline row"
            continue
        have = {"cvss_base": row.stored.get("cvss_base"), "exploitability": row.stored.get("exploitability"), "scalability": row.stored.get("scalability"),
                "reachability": row.stored.get("reachability"), "composite_score": row.stored.get("composite"), "severity_band": row.band,
                "remediation_sla": row.sla, "risk_disposition": row.disposition, "risk_owner": row.owner, "cvss_vector": row.cvss_vector,
                "review_date": row.review_date.isoformat() if row.review_date else None}
        bad = {field: (None if have[field] is None else str(have[field]), stored[field]) for field in have
               if stored.get(field) is not None and (None if have[field] is None else str(have[field])) != stored[field]}
        sources = finding.get("vector_sources")
        if sources is not None:
            if row.vector_source != ("md" if sources["markdown"] else ("sarif" if sources["sarif"] else None)):
                bad["vector_source"] = (row.vector_source, sources)
            if ("input:cvss_vector:sources-disagree" in row.flags) != bool(sources["markdown"] and sources["sarif"] and sources["markdown"] != sources["sarif"]):
                bad["sources-disagree"] = (list(row.flags), sources)
        outside = [flag for flag in row.flags if not CLOSED_FLAGS.fullmatch(flag)]
        if outside:
            bad["flags"] = outside
        if bad:
            wrong[finding_id] = bad
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", RULE_CASES)
def test_rules_the_vector_check_of_each_carried_finding_decides_at_the_step_the_outcomes_name(case):
    """D10 (R-25, R-9, R-7, R-10's score half) at the fixture's scale: the step that decides, the one flag it raises on the CVSS score,
    and the score it gives, for every carried finding of every scenario, under this run's tags for the finding's component."""
    top, doc, scores = baseline_of(case)
    wrong, checked = {}, 0
    for finding_id, finding in doc["findings"].items():
        if finding["treatment"] != "carried":
            continue
        checked += 1
        check = rules.check_carried_vector(scores.rows[canon(finding_id)], tags=tags_of(top, finding))
        want = {flag["flag"] for flag in finding["flags"] if flag["field"] == "cvss_base" and flag["basis"] != "optional"}
        got = {check.flag} - {None}
        rendered = None if check.cvss_base is None else str(check.cvss_base)
        if str(check.step) != str(finding["d10_step"]) or got != want or rendered != finding["rendered"]["cvss_base"]:
            wrong[finding_id] = {"step": check.step, "want step": finding["d10_step"], "flag": sorted(got), "want": sorted(want), "score": rendered,
                                 "want score": finding["rendered"]["cvss_base"]}
    assert checked
    assert not wrong, brief(wrong)


@pytest.mark.parametrize("case", RETAG_SCENARIOS)
def test_rules_the_tag_source_selector_picks_the_source_the_outcomes_name(case, populator):
    top = read_outcomes(case)
    folder = LARGE_ARCH / case
    text = (folder / "run" / "threats.md").read_text(encoding="utf-8")
    open_rows = tachi_parsers.parse_reference_set(text)["open"]
    architecture = top["run"].get("architecture")
    recomputed = (rules.recompute_tags((folder / architecture).read_text(encoding="utf-8"), open_rows, populator.match_component)
                  if architecture else None)
    chosen = rules.select_tag_source(open_ids=[row["id"] for row in open_rows], block=sc.parse_affected_assets(text), recomputed=recomputed)
    want = top["tag_source"]
    assert chosen.source == want["source"], chosen
    if want["source"] != "block-unverified":  # reading: the same open ruling as in test_s13_*: D2 records it as unverified, the outcomes also warn
        assert bool(chosen.warning) == want["warning"], chosen
    for row in open_rows:
        assert tuple(chosen.tags[canon(row["id"])]) == tuple(sorted(want["tags"].get(row["component"], ()))), row["id"]


# =============================================================================
# 27. The closed vocabulary, on what the renderer emits (module-signatures.md, "The scorer's flag vocabulary, closed")
# =============================================================================


@pytest.mark.parametrize("case", CASES)
def test_vocabulary_every_flag_the_renderer_emits_is_in_the_closed_vocabulary(scenarios, case):
    r = scenarios(case)
    open_string = split_case(case)[0] in S12B_OPEN  # reading: the one open string, an ``input:`` flag for a value the input's form lacks (S-12(b))

    def outside(flags):
        return sorted(flag for flag in flags if not CLOSED_FLAGS.fullmatch(flag) and not (open_string and re.fullmatch(r"input:[a-z_.]+:[a-z0-9-]+", flag)))

    wrong = {finding_id: outside(flags) for finding_id, flags in r.all_emitted().items() if outside(flags)}
    in_table, _rows = score_flag_rows(r.md)
    wrong.update({"Section 6, %s" % key: outside(flags) for key, flags in in_table.items() if outside(flags)})
    assert not wrong, brief(wrong)


# =============================================================================
# 28. P0-1 and P0-4: a structure leak that the next run would misread, and a forbidden character from an input (W3, lane FX0)
# =============================================================================
#
# P0-1. A prose line that starts with ``~~~`` opens a code fence for the next run's tolerant reader, which then loses Sections
# 4 and 6 and with them every human owner, SLA, review date and persisted input, with no warning. ``tachi_parts`` writes such a
# line as ``&#126;~~`` (R0a). The two-run cases pin the outcome that matters, a carry that keeps everything. The read-back cases
# pin the from-disk check that fails closed when any other leak would do the same: ``_check_staged`` reads the staged markdown
# back through ``read_baseline_scores``, the reader the next run uses (KB 22).
#
# P0-4. NFR-10 says that control bytes are refused before any write. Step 10 does that for a part. A value that the renderer takes
# from ``threats.md``, the baseline ``risk-scores.md`` or ``threats.sarif`` is refused where it is taken (exit 2, naming the input,
# the finding and the field), and each staged file is checked whole as a backstop (exit 4). The character set is
# ``tachi_parts.forbidden_character``'s. Every control and bidi character here is built with ``chr()``, so none sits in this source.

FORBIDDEN = {  # one of each class of D3 step 10's set: C0, DEL, C1, the separators and the bidi controls
    "escape": chr(0x1B), "carriage return": chr(0x0D), "delete": chr(0x7F), "next line": chr(0x85),
    "line separator": chr(0x2028), "paragraph separator": chr(0x2029), "left-to-right mark": chr(0x200E),
    "right-to-left override": chr(0x202E), "isolate": chr(0x2066), "arabic letter mark": chr(0x061C),
}
RLO = FORBIDDEN["right-to-left override"]
HUMAN_OWNERS = {"S-2": "Platform team", "T-1": "Data team"}   # a person puts these into Section 4 between the two runs


def fence_the_prose(indent):
    """S-2's prose rationale with one line that starts with ``~~~`` after ``indent``: a code fence that nothing closes.

    One line is the leak. A second ``~~~`` line would close the fence again, and the reader would lose nothing.
    """
    def mutate(part):
        for item in part["items"]:
            if canon(item["finding_id"]) == "S-2":
                item["rationale"]["cvss"] = "The base score is {{score:cvss_base}} for {{name:component}}.\n%s~~~\nA line that opens a code fence." % indent
    return mutate


def persisted_inputs(project):
    """``{(canonical ID, field): value}`` of Section 6's Scoring Inputs, decoded."""
    return {(canon(row[0]), row[1]): row[2] for row in table_of(subsection_of(project.md, "## 6. Score Integrity", "### Scoring Inputs"), "ID")[1]}


def carry_twice(stage_module, renderer_module, root, specs=None, mutate=None):
    """Run 1 over ``specs``, then run 2 with run 1's own files as its baseline and two owners that a person put into Section 4.

    Every finding is UNCHANGED in run 2, so each is carried: its owner, SLA, disposition, review date and persisted inputs come
    from Sections 4 and 6 of run 1's file, which is exactly what a structure leak in Section 3 hides from the reader.
    Returns ``(first, second)``.
    """
    root = Path(root)
    first = Project(stage_module, renderer_module, root / "first", specs=specs)
    res = first.run(mutate=mutate)
    assert res.code in (0, 5), res.describe()

    def put_owners(md):
        for finding_id, owner in HUMAN_OWNERS.items():
            md = edit_table_cell(md, "## 4. Governance Fields", finding_id, "Owner", owner)
        return md

    second = second_run(stage_module, renderer_module, root / "second", first, edit_baseline=put_owners, specs=specs)
    res = second.run()
    assert res.code in (0, 5), res.describe()
    return first, second


def assert_the_carry_kept_everything(first, second):
    assert second.plan_json()["unit_count"] == 0, "run 1's file is a usable baseline, so nothing goes to the agent"
    assert second.record["counts"].get("narrative_fallbacks", 0) == 0
    for heading in ("## 4. Governance Fields", "## 6. Score Integrity"):
        assert has_section(second.md, heading), heading
    before, after = MdView(first.md), MdView(second.md)
    for finding_id in ORDER:
        want = dict(before.values(finding_id))
        if finding_id in HUMAN_OWNERS:
            want["risk_owner"] = HUMAN_OWNERS[finding_id]
        assert after.values(finding_id) == want, "%s keeps its governance, and the owner that a person set" % finding_id
    results = results_by_id(second.sarif)
    assert {finding_id: results[finding_id]["properties"]["risk-owner"] for finding_id in HUMAN_OWNERS} == HUMAN_OWNERS
    read = rules.read_baseline_scores(second.out / MD)   # what a third run would read from run 2's file
    assert sorted(read.rows) == sorted(canon(finding_id) for finding_id in ORDER)
    assert {key: row.form for key, row in read.rows.items()} == {canon(finding_id): "renderer" for finding_id in ORDER}
    assert {finding_id: read.rows[canon(finding_id)].owner for finding_id in HUMAN_OWNERS} == HUMAN_OWNERS


@pytest.mark.parametrize("indent", ["", "  ", "\t"], ids=["bare", "two-spaces", "tab"])
def test_carry_a_tilde_fence_line_in_a_rationale_keeps_sections_4_and_6_and_every_owner(stage, renderer, tmp_path, indent):
    first, second = carry_twice(stage, renderer, tmp_path, mutate=fence_the_prose(indent))
    assert "\n%s&#126;~~\n" % indent in subsection_for(first.md, "S-2"), "Section 3 writes the line as a reference, after the same indent"
    for project in (first, second):
        assert not re.search(r"(?m)^[ \t]*~~~", project.md), "no line of the file opens a code fence"
    assert_the_carry_kept_everything(first, second)
    key = ("S-2", "rationale.cvss")
    assert re.search(r"\n[ \t]*~~~\n", persisted_inputs(first)[key]), "Section 6 keeps the line in the persisted text"
    assert persisted_inputs(second)[key] == persisted_inputs(first)[key], "and run 2 carries it unchanged"


def test_carry_a_tilde_fence_line_after_a_no_break_space_keeps_sections_4_and_6_and_every_owner(stage, renderer, tmp_path):
    """The architect's W3 residual ruling: the guard looks past any whitespace but a newline, and the reader's structure tests look
    past only spaces and tabs, so a Unicode space can't lead a fence past either. U+00A0 is not in step 10's set, so the part passes."""
    nbsp = chr(0xA0)
    first, second = carry_twice(stage, renderer, tmp_path, mutate=fence_the_prose(nbsp))
    assert "\n%s&#126;~~\n" % nbsp in subsection_for(first.md, "S-2"), "Section 3 writes the line as a reference, after the same no-break space"
    for project in (first, second):
        assert not re.search(r"(?m)^[^\S\n]*~~~", project.md), "no line of the file opens a code fence, whatever whitespace leads it"
    assert_the_carry_kept_everything(first, second)
    key = ("S-2", "rationale.cvss")
    assert re.search(r"\n%s~~~\n" % nbsp, persisted_inputs(first)[key]), "Section 6 keeps the line in the persisted text"
    assert persisted_inputs(second)[key] == persisted_inputs(first)[key], "and run 2 carries it unchanged"


def test_carry_a_tilde_fence_line_in_a_threat_text_keeps_sections_4_and_6_and_every_owner(stage, renderer, tmp_path):
    """A ``**Threat**:`` text that arrives from threats.md as ``&#10;~~~``: the parser decodes the reference, so the text has a line of its own."""
    specs = [dict(item, threat=item["threat"] + "&#10;~~~&#10;The text goes on.") if item["id"] == "S-2" else item for item in SPECS]
    first, second = carry_twice(stage, renderer, tmp_path, specs=specs)
    assert re.search(r"\*\*Threat\*\*: [^\n]*\n&#126;~~\nThe text goes on\.", subsection_for(first.md, "S-2"))
    for project in (first, second):
        assert not re.search(r"(?m)^[ \t]*~~~", project.md), "no line of the file opens a code fence"
    assert_the_carry_kept_everything(first, second)


# --------------------------------------------------------------------------- the from-disk read-back (P0-1)

def assert_failed_closed(project, res, *expected):
    """A check on the staged files that fails: exit 4 with D4's message, the named facts in it, the canonical files untouched, and Step F able to run."""
    assert res.code == 4, "a completeness or parity check that fails is exit 4 (cli.md): %s" % res.describe()
    assert_failure_message(res, project.plan_id)
    for text in expected:
        assert text in res.err, "%r is not in the message:\n%s" % (text, res.describe())
    project.assert_earlier_outputs_untouched()
    assert (project.plan_dir / "staged" / MD).is_file(), "the staged file stays for diagnosis (KB 21)"
    failed = project.fail("check-failed")
    assert failed.code == 0, failed.describe()
    assert json.loads(failed.out)["moved"] == [] and json.loads(failed.out)["restored"] == [], "there was nothing to put back"
    project.assert_earlier_outputs_untouched()
    assert project.record["status"] == "failed" and project.record["error"]["code"] == "check-failed"


# Each leak is in the staged markdown only, and every one of them passes the table readers that the other checks use, which are
# not fence-aware. Only the reader that the next run uses sees it. The expected text is the read-back's own wording.
READ_BACK_LEAKS = [
    ("a-tilde-fence", first_line_edit("**Threat**:", lambda line: line + "\n~~~\nA fence that nothing closes."),
     "9 open finding(s) would read back in the legacy form although their sub-scores were written"),
    ("a-backtick-fence", first_line_edit("**Threat**:", lambda line: line + "\n```\nA fence that nothing closes."),
     "9 open finding(s) would read back in the legacy form although their sub-scores were written"),
    ("a-persisted-sub-score-that-no-longer-reads", first_line_edit("| S-2 | exploitability.known_techniques |", lambda line: line.replace("| 5 |", "| five |")),
     "1 open finding(s) would read back in the legacy form although their sub-scores were written (S-2)"),
]


@pytest.mark.parametrize("name,edit,expected", READ_BACK_LEAKS, ids=[case[0] for case in READ_BACK_LEAKS])
def test_readback_a_leak_that_the_next_runs_reader_would_misread_fails_closed_before_any_move(project, name, edit, expected):
    project.earlier()
    project.prepare()
    with tampering_with_staged(MD, edit):
        res = project.render()
    assert_failed_closed(project, res, expected)
    assert "staged files: " + expected in res.err, "the read-back is the first check to fail: nothing else saw the leak"


def test_readback_a_fence_hides_every_owner_and_review_date_and_the_message_says_so(project):
    project.earlier()
    project.prepare()
    with tampering_with_staged(MD, first_line_edit("**Threat**:", lambda line: line + "\n~~~\nA fence that nothing closes.")):
        res = project.render()
    assert_failed_closed(project, res, "the next run would read another owner, SLA, disposition or review date than was written for 9 open finding(s)",
                         "a line in the file may forge structure, such as a code fence or a heading")


def test_readback_a_row_that_the_next_run_would_not_read_is_named(project):
    project.earlier()
    project.prepare()
    with tampering_with_staged(MD, first_line_edit("| E-5 |", lambda line: None)):   # Section 2 loses E-5's row
        res = project.render()
    assert_failed_closed(project, res, "the next run would read 8 of the 9 open rows from the staged risk-scores.md (missing: E-5; unexpected: none)")


def test_readback_a_staged_file_that_would_not_read_as_a_baseline_is_a_problem(renderer, tmp_path):
    path = tmp_path / MD
    path.write_text("# Risk Scores Report\n\nNothing was scored.\n", encoding="utf-8")
    problems = renderer._read_back_problems(types.SimpleNamespace(ordered=[]), str(path))
    assert problems == ["the staged %s would not read back as a baseline (no-rows)" % MD]


def test_readback_a_clean_render_reads_back_every_row_in_the_form_it_was_written(base):
    read = rules.read_baseline_scores(base.out / MD)
    assert sorted(read.rows) == sorted(canon(finding_id) for finding_id in ORDER)
    assert all(row.form == "renderer" for row in read.rows.values())


# --------------------------------------------------------------------------- a forbidden character in an input (P0-4)

def assert_refused(project, res, char, source, finding_id, field):
    """A forbidden character from an input: exit 2 before anything is computed, the input, the finding, the field and the remedy named,
    the code point given and the character never echoed, and no file written. D4's Step F (the fail step) then runs as it does for any exit 2."""
    assert res.code == 2, res.describe()
    assert_failure_message(res, project.plan_id)
    reason = next(line for line in res.err.split("\n") if line.startswith("TACHI RISK-SCORE FAILED:"))
    assert source in reason and "U+%04X" % ord(char) in reason, reason
    if finding_id is None:
        assert "a component, zone or layer name" in reason, reason
    else:
        assert "the %s of %s" % (field, finding_id) in reason, reason
    assert re.search(r"Remedy: .*\b(regenerate|edit)\b", res.err), res.describe()
    assert char not in res.err, "the message gives the code point and never the character"
    project.assert_earlier_outputs_untouched()
    assert not (project.plan_dir / "staged").exists(), "refused before anything was staged"
    failed = project.fail("render-failed", detail="a forbidden character in an input")
    assert failed.code == 0, failed.describe()
    project.assert_earlier_outputs_untouched()
    assert project.record["status"] == "failed" and project.record["error"]["code"] == "render-failed"


THREATS_MD_FIELDS = (  # (finding, the field the message names, the table's heading, its column, the cell, with {} where the character goes)
    ("S-2", "component", "## 7. Recommended Actions", "Component", "edge{}-gateway"),
    ("S-2", "threat", "## 7. Recommended Actions", "Threat", "Shared tokens let callers{} impersonate each other."),
    ("S-2", "mitigation", "## 7. Recommended Actions", "Mitigation", "Mitigation{} text for S-2."),
    ("S-2", "risk_level", "## 7. Recommended Actions", "Risk Level", "Hi{}gh"),
    ("S-2", "layer", "## 7. Recommended Actions", "MAESTRO Layer", "L4 {} Deployment Infrastructure"),
    ("S-1", "threat", "## 4c. Resolved Findings", "Threat", "An unauthenticated{} callback route."),
)


@pytest.mark.parametrize("finding_id,field,title,column,cell", THREATS_MD_FIELDS, ids=["%s-%s" % case[:2] for case in THREATS_MD_FIELDS])
def test_refusal_a_forbidden_character_in_a_threats_md_field_is_refused_naming_the_finding_and_the_field(stage, renderer, tmp_path, finding_id, field, title, column, cell):
    text = edit_table_cell(make_threats_md(), title, finding_id, column, cell.format(RLO))
    project = Project(stage, renderer, tmp_path, threats_text=text)
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), RLO, "threats.md", finding_id, field)


@pytest.mark.parametrize("name", sorted(FORBIDDEN))
def test_refusal_every_character_of_the_set_is_refused_in_a_threats_md_field(stage, renderer, tmp_path, name):
    char = FORBIDDEN[name]
    text = edit_table_cell(make_threats_md(), "## 7. Recommended Actions", "S-2", "Threat", "Shared tokens let callers{} impersonate each other.".format(char))
    project = Project(stage, renderer, tmp_path, threats_text=text)
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), char, "threats.md", "S-2", "threat")


SCOPE_CELLS = (  # a Section 1 or 2 name or label, which belongs to no finding
    ("a-zone-name", "| Edge DMZ | Semi-trusted |", "| Edge{} DMZ | Semi-trusted |"),
    ("a-trust-label", "| Edge DMZ | Semi-trusted |", "| Edge DMZ | Semi-{}trusted |"),
    ("a-component-type", "| edge-gateway | Process |", "| edge-gateway | Proc{}ess |"),
)


@pytest.mark.parametrize("name,old,new", SCOPE_CELLS, ids=[case[0] for case in SCOPE_CELLS])
def test_refusal_a_forbidden_character_in_a_section_1_or_2_name_is_refused_without_a_finding(stage, renderer, tmp_path, name, old, new):
    text = make_threats_md()
    assert old in text
    project = Project(stage, renderer, tmp_path, threats_text=text.replace(old, new.format(RLO), 1))
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), RLO, "threats.md", None, None)


BASELINE_CELLS = (  # (finding, the field the message names, the baseline's table, its column, the cell, with {} where the character goes)
    ("S-2", "owner", "## 4. Governance Fields", "Owner", "Platform {}team"),
    ("S-2", "sla", "## 4. Governance Fields", "SLA", "7{}d"),
    ("S-2", "disposition", "## 4. Governance Fields", "Disposition", "Miti{}gate"),
    ("S-1", "owner", "## 2a. Resolved Findings", "Owner", "Platform {}team"),   # a RESOLVED row's values reach Section 2a
)


@pytest.mark.parametrize("finding_id,field,title,column,cell", BASELINE_CELLS, ids=["%s-%s" % case[:2] for case in BASELINE_CELLS])
def test_refusal_a_forbidden_character_in_a_baseline_cell_is_refused_naming_the_finding_and_the_field(stage, renderer, base, tmp_path, finding_id, field, title, column, cell):
    project = second_run(stage, renderer, tmp_path, base, edit_baseline=lambda md: edit_table_cell(md, title, finding_id, column, cell.format(FORBIDDEN["left-to-right mark"])))
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), FORBIDDEN["left-to-right mark"], "the baseline risk-scores.md", finding_id, field)


def test_refusal_a_forbidden_character_in_a_persisted_narrative_of_the_baseline_is_refused(stage, renderer, base, tmp_path):
    """A carried narrative is re-checked only by step 11, which never looked at control characters: the baseline's own text reaches the output."""
    edit = first_line_edit("| S-2 | rationale.cvss |", lambda line: line.replace(" for ", " for " + RLO, 1))
    project = second_run(stage, renderer, tmp_path, base, edit_baseline=edit)
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), RLO, "the baseline risk-scores.md", "S-2", "narrative.rationale.cvss")


def test_refusal_a_forbidden_character_in_the_baseline_sarifs_vector_is_refused(stage, renderer, base, tmp_path):
    """The baseline SARIF is the second source of a vector (R-26), and Section 6 shows its text when the two sources disagree."""
    project = second_run(stage, renderer, tmp_path, base)
    path = tmp_path / "baseline" / SARIF
    document = json.loads(path.read_text(encoding="utf-8"))
    for result in document["runs"][0]["results"]:
        if result["partialFingerprints"]["findingId/v1"] == "S-2":
            result["properties"]["cvss-vector"] += RLO
    path.write_text(json.dumps(document), encoding="utf-8")
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), RLO, "the baseline risk-scores.sarif", "S-2", "cvss-vector")


@pytest.mark.parametrize("where", ["threats.md", "baseline"])
def test_refusal_a_file_saved_with_crlf_line_endings_is_not_refused(stage, renderer, base, tmp_path, where):
    """``\\r`` is in step 10's set, but it ends every line of a CRLF file and the readers strip it from each cell's edge,
    so a file that was saved on another system is read as it always was."""
    def crlf(path):
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))

    if where == "threats.md":
        project = Project(stage, renderer, tmp_path)
        crlf(project.threats)
    else:
        project = second_run(stage, renderer, tmp_path, base, edit_baseline=lambda md: edit_table_cell(md, "## 4. Governance Fields", "S-2", "Owner", "Platform team"))
        for name in ("threats.md", MD):
            crlf(tmp_path / "baseline" / name)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    results = results_by_id(project.sarif)
    assert results["S-2"]["message"]["text"] == by_id("S-2")["threat"]
    if where == "baseline":
        assert results["S-2"]["properties"]["risk-owner"] == "Platform team", "the carry reads the CRLF baseline as it reads any other"


def test_refusal_a_baseline_row_of_a_finding_that_this_run_no_longer_lists_is_not_taken(stage, renderer, base, tmp_path):
    """The renderer takes values only from the rows of the findings it lists, so a stale row's text is never checked and never read."""
    project = second_run(stage, renderer, tmp_path, base, edit_baseline=lambda md: edit_table_cell(md, "## 4. Governance Fields", "R-1", "Owner", "Ops {}team".format(RLO)),
                         specs=[dict(item, status="UNCHANGED") for item in SPECS if item["id"] != "R-1"])
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert RLO not in project.md and RLO not in json.dumps(project.sarif, ensure_ascii=False), "the stale row's text reached neither file"


def sarif_fallback_project(stage_module, renderer_module, root, text=None, items=None):
    """The nine-finding project whose threats.md is gone, so the plan reads the ``threats.sarif`` beside it (D8's fallback).

    ``items`` is the project's scorer-item factory, for a ``threats.sarif`` whose findings are not the nine.
    """
    project = Project(stage_module, renderer_module, root, items=items)
    project.threats.unlink()
    (project.out / "threats.sarif").write_text(make_threats_sarif() if text is None else text, encoding="utf-8")
    return project


def make_threats_sarif():
    """A synthetic ``threats.sarif`` in the form that D8's fallback reads: one result for each finding, with its text, component and layer."""
    results = []
    for item in SPECS:
        dfd_type, layer = COMPONENTS[item["component"]]
        results.append({"message": {"text": item["threat"], "markdown": mitigation_of(item)}, "level": "warning",
                        "locations": [{"logicalLocations": [{"name": item["component"], "kind": KIND_OF[dfd_type]}]}],
                        "partialFingerprints": {"findingId/v1": item["id"]},
                        "properties": {"security-severity": "6.0", "maestro-layer": layer}})
    return json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "Tachi"}}, "results": results}]}, indent=2) + "\n"


SARIF_FIELDS = (  # (the field the message names, how to put the character into S-2's result)
    ("component", lambda result, char: result["locations"][0]["logicalLocations"][0].update(name="edge" + char + "-gateway")),
    ("threat", lambda result, char: result["message"].update(text="Shared tokens" + char + " let callers impersonate each other.")),
    ("mitigation", lambda result, char: result["message"].update(markdown="Mitigation" + char + " text for S-2.")),
    ("layer", lambda result, char: result["properties"].update({"maestro-layer": "L4 " + char + " Deployment Infrastructure"})),
)


def test_refusal_a_clean_threats_sarif_renders_in_the_fallback(stage, renderer, tmp_path):
    project = sarif_fallback_project(stage, renderer, tmp_path)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert results_by_id(project.sarif)["S-2"]["message"]["text"] == by_id("S-2")["threat"], "the finding's text comes from its result"


@pytest.mark.parametrize("field,poison", SARIF_FIELDS, ids=[case[0] for case in SARIF_FIELDS])
def test_refusal_a_forbidden_character_in_threats_sarif_text_is_refused_in_the_fallback(stage, renderer, tmp_path, field, poison):
    char = FORBIDDEN["escape"]
    document = json.loads(make_threats_sarif())
    poison(next(result for result in document["runs"][0]["results"] if result["partialFingerprints"]["findingId/v1"] == "S-2"), char)
    project = sarif_fallback_project(stage, renderer, tmp_path, text=json.dumps(document))
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), char, "threats.sarif", "S-2", field)


def test_refusal_whitespace_that_the_reader_strips_from_a_cells_edge_never_reaches_the_check(stage, renderer, tmp_path):
    """A line separator, a vertical tab and a carriage return at a cell's edge are whitespace. The reader strips them, as it always did,
    so the value that the renderer takes is clean and the run is unchanged."""
    text = make_threats_md()
    text = edit_table_cell(text, "## 7. Recommended Actions", "S-2", "Threat", FORBIDDEN["line separator"] + by_id("S-2")["threat"] + chr(0x0B))
    text = edit_table_cell(text, "## 7. Recommended Actions", "T-1", "Mitigation", mitigation_of(by_id("T-1")) + FORBIDDEN["carriage return"])
    project = Project(stage, renderer, tmp_path, threats_text=text)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    results = results_by_id(project.sarif)
    assert results["S-2"]["message"]["text"] == by_id("S-2")["threat"]
    assert results["T-1"]["message"]["markdown"] == mitigation_of(by_id("T-1"))


def test_refusal_characters_beside_the_set_are_taken_as_they_are(stage, renderer, tmp_path):
    """Only step 10's set is refused: a tab, a no-break space, a soft hyphen, a zero-width space, a narrow no-break space, a word joiner,
    a byte order mark and an emoji pass, in the middle of a threat."""
    beside = "".join(chr(code) for code in (0x09, 0xA0, 0xAD, 0x200B, 0x202F, 0x2060, 0xFEFF, 0x1F600))
    threat = "Shared tokens" + beside + " let callers impersonate each other."
    text = edit_table_cell(make_threats_md(), "## 7. Recommended Actions", "S-2", "Threat", threat)
    project = Project(stage, renderer, tmp_path, threats_text=text)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert results_by_id(project.sarif)["S-2"]["message"]["text"] == threat


class Plain(object):
    def __init__(self, **fields):
        self.__dict__.update(fields)


def test_refusal_the_search_reads_text_keys_items_and_fields_and_nothing_else(renderer):
    found, escape = renderer._first_forbidden, FORBIDDEN["escape"]
    assert found("") is None and found("clean text, with a tab\tand a newline\n") is None
    assert found("a" + escape) == ("", escape)
    assert found({"a": [{"b": ("x", "y" + escape)}]}) == ("a.0.b.1", escape), "mappings, lists and tuples, with a dotted path"
    assert found({"k" + RLO: 1}) == ("k" + RLO, RLO), "a key is text too"
    assert found(Plain(owner="Ann", notes={"rationale.cvss": "ok" + escape})) == ("notes.rationale.cvss", escape), "a plain object's fields"
    assert found([1, 2.5, None, True, Decimal("1.0"), datetime.date(2026, 11, 22), b"bytes", object()]) is None, "a number, a date or None holds no text"


# --------------------------------------------------------------------------- the whole-file backstop (P0-4)

@pytest.mark.parametrize("name", sorted(FORBIDDEN))
def test_backstop_a_forbidden_character_in_the_staged_markdown_fails_closed(project, name):
    char = FORBIDDEN[name]
    project.earlier()
    project.prepare()
    with tampering_with_staged(MD, first_line_edit("**Threat**:", lambda line: line + char + " and on")):
        res = project.render()
    assert_failed_closed(project, res, "the staged risk-scores.md holds the character U+%04X, which the part contract forbids, at line " % ord(char))
    assert char not in res.err, "the message gives the code point and never the character"


@pytest.mark.parametrize("name", sorted(FORBIDDEN))
def test_backstop_a_forbidden_character_in_a_decoded_sarif_string_fails_closed(project, name):
    char = FORBIDDEN[name]

    def poison(document):
        document["runs"][0]["results"][0]["message"]["text"] += char

    project.earlier()
    project.prepare()
    with tampering_with_staged(SARIF, json_edit(poison)):
        res = project.render()
    assert_failed_closed(project, res, "the staged risk-scores.sarif holds the character U+%04X, which the part contract forbids, in " % ord(char))
    assert char not in res.err, "the message gives the code point and never the character"


# =============================================================================
# 29. P0-3, P0-7 and P0-8: the threats.sarif fallback, the plan's own refs and message.markdown (W3, lane FX0)
# =============================================================================
#
# P0-3. When the plan reads ``threats.sarif`` (D8's fallback), the planner and the renderer must see the same findings and the
# same groups, and the renderer must take each finding's text from its own result, whichever ID form the result uses. Two shipped
# shapes failed that: a file whose correlation groups have no ID crashed the render (the emitter raises on an ID it was not given),
# and the legacy form, with the ID only in ``properties.id``, rendered every finding blank, with no warning. D8's reading: a group
# the file gives no ID still routes its peers (copy and divergence, D9), but its members carry no ``correlation-*`` property and no
# ruling-C sentence, and the stage record warns ``correlation-group-unnamed`` with the count.
#
# These cases run copies of three shipped samples through plan, parts and render, in a temporary directory (nothing is written under
# examples/). Each is read back against the sample itself, by plain lookups, so the oracle is the file and not the reader that the
# renderer uses. The agent's parts are generic: the file has no Section 2, so every zone is an Input Issue and the run exits 5.
#
# P0-7. The plan's own ``refs`` are the renderer's refs. P0-8. ``message.markdown`` is always written, the empty string included.

EXAMPLES = REPO_ROOT / "examples"
FALLBACK_SHAPES = {   # shape -> the shipped threats.sarif that shows it
    "modern": "agentic-app/sample-report/threats.sarif",             # findingId/v1; a mitigation, a layer and a DFD kind on every result
    "unnamed": "maestro-reference/threats.sarif",                    # three correlation groups that the file gives no group ID
    "legacy": "mobile-banking-app/sample-report/threats.sarif",      # the ID only in properties.id; no mitigation and no layer
}
UNNAMED_GROUPS = {"modern": 0, "unnamed": 3, "legacy": 0}
UNNAMED_PEERS = (("T-7", "AG-7"), ("R-6", "AG-1"), ("I-7", "LLM-1"))   # maestro-reference's three groups: (primary, peer)
KIND_WRITTEN = {"external-entity": "external-entity", "process": "process", "data-store": "data", "component": "process"}
# What the renderer writes for each ``kind`` that a shipped threats.sarif has. ``data-store`` is a Data Store, which the scorer's file
# writes as ``data``. The legacy form's ``component`` is no DFD kind, so the finding is a process, as it is when threats.md has no type.


def shipped_sarif(shape):
    return (EXAMPLES / FALLBACK_SHAPES[shape]).read_text(encoding="utf-8")


def generic_scorer_item(finding_id):
    """A valid scorer item for any finding ID: its category's default vector, numbers from the ID and one made-up zone."""
    return scorer_item(generic_item(finding_id, "any", collections.defaultdict(lambda: ("Fallback Zone", "Semi-Trusted"))))


def sarif_results_of(document):
    """``{canonical ID: result}`` of a ``threats.sarif``, by plain lookups: ``findingId/v1``, else ``properties.id``; the first result of an ID wins."""
    found = {}
    for result in document["runs"][0]["results"]:
        identifier = result.get("partialFingerprints", {}).get("findingId/v1") or result["properties"]["id"]
        found.setdefault(canon(identifier), result)
    return found


def sarif_says(result):
    """What a shipped ``threats.sarif`` result says about its own finding (D8's reading, restated by plain lookups on the three shapes).

    The risk level is ``properties.risk_level``, else a dash. Only the legacy form writes one: the modern form writes its level as
    ``properties.severity``, which D8's reading does not take, so its findings show a dash, as they did before the reader changed.
    """
    logical = result["locations"][0]["logicalLocations"][0]
    return {"component": logical["name"], "kind": logical["kind"], "threat": result["message"]["text"],
            "mitigation": result["message"].get("markdown", ""), "risk_level": result["properties"].get("risk_level", DASH),
            "layer": result["properties"].get("maestro-layer", "Unclassified")}


def planned_agents(project):
    return {canon(finding_id) for entry in project.plan_json()["batches"] for finding_id in entry["finding_ids"]}


def render_fallback(stage_module, renderer_module, root, text):
    """Plan, score with generic parts and render the project whose only input is the ``threats.sarif`` ``text`` (D8's fallback).

    Returns ``(project, result, seen)``. ``seen`` is what the renderer itself was asked while it ran: ``agents``, the IDs that its routing sends
    to the agent, and ``joined``, the ``(ID, component)`` rows that its asset-tag join was given.
    """
    project = sarif_fallback_project(stage_module, renderer_module, root, text=text, items=generic_scorer_item)
    seen = {"agents": None, "joined": None}
    real_route, real_recompute = renderer_module._route, rules.recompute_tags

    def route(run, reference):
        routing = real_route(run, reference)
        seen["agents"] = set(routing.to_agent)
        return routing

    def recompute(architecture_text, open_rows, matcher):
        seen["joined"] = {(row["id"], row["component"]) for row in open_rows}
        return real_recompute(architecture_text, open_rows, matcher)

    project.prepare()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(renderer_module, "_route", route)
        patch.setattr(rules, "recompute_tags", recompute)
        res = project.render()
    return project, res, seen


def shipped_fallback(shape, stage_module, renderer_module, tmp_path_factory):
    text = shipped_sarif(shape)
    project, res, seen = render_fallback(stage_module, renderer_module, tmp_path_factory.mktemp("fallback-" + shape), text)
    return types.SimpleNamespace(shape=shape, text=text, source=json.loads(text), project=project, res=res, seen=seen)


@pytest.fixture(scope="module")
def fallback_modern(stage, renderer, tmp_path_factory):
    return shipped_fallback("modern", stage, renderer, tmp_path_factory)


@pytest.fixture(scope="module")
def fallback_unnamed(stage, renderer, tmp_path_factory):
    return shipped_fallback("unnamed", stage, renderer, tmp_path_factory)


@pytest.fixture(scope="module")
def fallback_legacy(stage, renderer, tmp_path_factory):
    return shipped_fallback("legacy", stage, renderer, tmp_path_factory)


@pytest.fixture(scope="module", params=sorted(FALLBACK_SHAPES))
def fallback(request):
    return request.getfixturevalue("fallback_" + request.param)


def test_fallback_each_shape_shows_the_form_it_is_there_for(fallback_modern, fallback_unnamed, fallback_legacy):
    """The premise of the cases below: if a sample stops showing its form, these fail instead of the cases passing for nothing."""
    modern = fallback_modern.source["runs"][0]["results"] + fallback_unnamed.source["runs"][0]["results"]
    legacy = fallback_legacy.source["runs"][0]["results"]
    assert modern and all("findingId/v1" in result["partialFingerprints"] for result in modern)
    assert legacy and all("partialFingerprints" not in result and "id" in result["properties"] for result in legacy), \
        "the legacy form has the ID only in properties.id"
    assert not [result for result in legacy if "markdown" in result["message"] or "maestro-layer" in result["properties"]]
    assert {sarif_says(result)["kind"] for result in modern} == {"external-entity", "process", "data-store"}
    groups = tachi_parsers.parse_sarif_member_set(fallback_unnamed.text)["groups"]
    assert [group["group_id"] for group in groups] == [None, None, None], "three groups, and the file names none of them"
    assert [(group["primary"], group["members"][1]) for group in groups] == list(UNNAMED_PEERS)


def test_fallback_a_run_over_each_shape_finishes_and_the_planners_agents_are_the_renderers(fallback):
    """D2: one partition. The planner reads the file through one path and the renderer through another, and they must name the same agent set."""
    assert fallback.res.code == 5, fallback.res.describe()
    members = set(sarif_results_of(fallback.source))
    peers = {peer for _primary, peer in UNNAMED_PEERS} if fallback.shape == "unnamed" else set()
    planned = planned_agents(fallback.project)
    assert planned == members - peers, "a peer of an unnamed group is not dispatched either: its primary's values are copied"
    assert fallback.seen["agents"] == planned
    counts = fallback.project.record["counts"]
    assert (counts["open"], counts["units"], counts["rendered"]) == (len(members), len(planned), len(members))


def test_fallback_every_findings_identity_text_is_its_own_results(fallback):
    """P0-3 (b): the legacy form rendered every finding as component ``Unspecified``, no threat, no mitigation and no risk level."""
    results = {canon(key): value for key, value in results_by_id(fallback.project.sarif).items()}
    source = sarif_results_of(fallback.source)
    assert sorted(results, key=s2_key) == sorted(source, key=s2_key)
    for finding_id, result in source.items():
        said, written = sarif_says(result), results[finding_id]
        logical = written["locations"][0]["logicalLocations"][0]
        assert logical["name"] == said["component"], finding_id
        assert logical["kind"] == KIND_WRITTEN[said["kind"]], finding_id
        assert written["message"] == {"text": said["threat"], "markdown": said["mitigation"]}, "%s: text, and markdown always (P0-8)" % finding_id
        assert written["properties"]["maestro-layer"] == said["layer"], finding_id
        level = re.search(r"\*\*Original Risk Level\*\*: (.*?) \| \*\*Composite\*\*", subsection_for(fallback.project.md, finding_id)).group(1)
        assert decode(level) == said["risk_level"], finding_id
    assert not [finding_id for finding_id, result in source.items() if sarif_says(result)["component"] == "Unspecified"]


def test_fallback_the_asset_tag_join_is_asked_about_each_findings_own_component(fallback):
    """P0-3 (b): with no component the join matched nothing, so a finding's tags (and its CVSS) never followed its component."""
    assert fallback.seen["joined"] == {(finding_id, sarif_says(result)["component"]) for finding_id, result in sarif_results_of(fallback.source).items()}


def test_fallback_correlation_follows_d8_when_no_group_has_an_id(fallback):
    """No result names a group, so none carries a ``correlation-*`` property or ruling C's sentence, and the record warns with the count."""
    results = fallback.project.sarif["runs"][0]["results"]
    assert not [key for result in results for key in result["properties"] if key.startswith("correlation-")]
    assert not [result for result in results if "Correlated in" in result["message"]["text"]]
    warnings = [warning for warning in fallback.project.record["warnings"] if warning["code"] == "correlation-group-unnamed"]
    count = UNNAMED_GROUPS[fallback.shape]
    if count:
        assert len(warnings) == 1 and warnings[0]["detail"].startswith("threats.sarif gives no group ID to %d of its %d correlation groups" % (count, count)), warnings
    else:
        assert warnings == [], "a file with no group has nothing to warn about"


def test_fallback_an_unnamed_group_still_routes_its_peers_so_each_copies_its_primary(fallback_unnamed):
    results = {canon(key): value for key, value in results_by_id(fallback_unnamed.project.sarif).items()}
    source = sarif_results_of(fallback_unnamed.source)
    copied = ("security-severity", "cvss-base-score", "cvss-vector", "exploitability", "scalability", "reachability", "severity-band")
    for primary, peer in UNNAMED_PEERS:
        assert peer not in fallback_unnamed.seen["agents"] and primary in fallback_unnamed.seen["agents"], (primary, peer)
        assert [results[peer]["properties"][key] for key in copied] == [results[primary]["properties"][key] for key in copied], (primary, peer)
        assert results[peer]["message"]["text"] == sarif_says(source[peer])["threat"], "but the peer keeps its own text"
        assert results[peer]["locations"][0]["logicalLocations"][0]["name"] == sarif_says(source[peer])["component"]
    sc.self_check(fallback_unnamed.project.sarif["runs"][0]["results"], tool=TOOL, member_ids=sorted(source), assignments={}, resolved_ids=[],
                  uri=URI)


def test_fallback_only_a_group_with_an_id_reaches_the_emitter_and_the_others_are_counted(stage, renderer, tmp_path):
    """The file names the first of its three groups: its two members get ``correlation-*`` and ruling C's sentence, the other four members get neither."""
    document = json.loads(shipped_sarif("unnamed"))
    named = {"T-7": "primary", "AG-7": "peer"}
    for result in document["runs"][0]["results"]:
        if result["partialFingerprints"]["findingId/v1"] in named:
            result["properties"].update({"correlation-group": "CG-2", "correlation-role": named[result["partialFingerprints"]["findingId/v1"]],
                                         "correlation-primary": "T-7"})
    project, res, seen = render_fallback(stage, renderer, tmp_path, json.dumps(document))
    assert res.code == 5, res.describe()
    results = {canon(key): value for key, value in results_by_id(project.sarif).items()}
    source = sarif_results_of(document)
    assignments = {"T-7": sc.Correlation("CG-2", "primary", "T-7", ("AG-7",)), "AG-7": sc.Correlation("CG-2", "peer", "T-7", ())}
    for finding_id, result in results.items():
        properties = result["properties"]
        found = assignments.get(finding_id)
        if found is None:
            assert not [key for key in properties if key.startswith("correlation-")] and result["message"]["text"] == sarif_says(source[finding_id])["threat"]
            continue
        assert (properties["correlation-group"], properties["correlation-role"], properties["correlation-primary"]) == (found.group, found.role, found.primary)
        assert result["message"]["text"] == sc.correlated_message(sarif_says(source[finding_id])["threat"], found)
    warnings = [warning for warning in project.record["warnings"] if warning["code"] == "correlation-group-unnamed"]
    assert len(warnings) == 1 and warnings[0]["detail"].startswith("threats.sarif gives no group ID to 2 of its 3 correlation groups"), warnings
    assert seen["agents"] == planned_agents(project) == set(source) - {"AG-7", "AG-1", "LLM-1"}, "all three groups route their peers, named or not"


def test_refusal_a_forbidden_character_in_a_legacy_form_results_text_is_refused_in_the_fallback(stage, renderer, tmp_path):
    """The legacy form reaches the renderer's intake check as the modern form does: the reader hands each value back as the file wrote it."""
    char = FORBIDDEN["escape"]
    document = json.loads(shipped_sarif("legacy"))
    next(result for result in document["runs"][0]["results"] if result["properties"]["id"] == "S-1")["message"]["text"] += char
    project = sarif_fallback_project(stage, renderer, tmp_path, text=json.dumps(document), items=generic_scorer_item)
    project.earlier()
    project.prepare()
    assert_refused(project, project.render(), char, "threats.sarif", "S-1", "threat")


def test_fallback_a_result_with_only_a_security_severity_shows_its_band_as_the_original_risk_level(stage, renderer, tmp_path):
    """D8: the risk level is ``properties.risk_level``, else ``security-severity``, which is a score, so it is read as its severity band."""
    project = sarif_fallback_project(stage, renderer, tmp_path)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert "**Original Risk Level**: Medium |" in subsection_for(project.md, "S-2"), "the synthetic file writes security-severity 6.0 and no risk level"


RISK_LEVELS = [(None, DASH), ("Critical", "Critical"), ("High", "High"), ("Note", "Note"), ("critical", "critical"),
               ("9.0", "Critical"), ("8.9", "High"), ("7.0", "High"), ("6.9", "Medium"), ("4.0", "Medium"), ("3.9", "Low"), ("0.0", "Low"),
               ("10", "Critical"), ("12.5", "Critical"), ("-1", "Low"), ("8.95", "Critical"), (" 6.0 ", "Medium")]


@pytest.mark.parametrize("level,expected", RISK_LEVELS, ids=[repr(case[0]) for case in RISK_LEVELS])
def test_fallback_a_risk_level_is_a_word_as_written_a_score_as_its_band_and_nothing_as_a_dash(renderer, level, expected):
    assert renderer._risk_level(level) == expected


def test_fallback_a_score_is_banded_by_the_shipped_band_function_at_every_point_of_the_grid(renderer):
    """The conversion is ``tachi_scoring.band`` and nothing of its own: it can't drift from the bands that Section 5 states."""
    for tenth in range(0, 101):
        score = Decimal(tenth) / 10
        assert renderer._risk_level(str(score)) == ts.band(score), score


def test_cli_a_plan_with_no_refs_is_refused_and_never_repaired_from_a_batch_input(project, renderer):
    """P0-7: ``validate_plan`` requires ``refs``, so the old fallback to the first batch input's ``refs`` could not run. It is gone."""
    project.plan()
    path = project.plan_dir / "plan.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["refs"] and project.batch_input("B001")["refs"], "the premise: both hold refs"
    del document["refs"]
    path.write_text(json.dumps(document), encoding="utf-8")
    res = invoke(renderer, ["--out", project.out, "--plan", project.plan_id, "--plan-digest", tp.file_digest(str(path))], project.root)
    assert res.code == 2 and "plan.json is not acceptable" in res.err, res.describe()
    assert not (project.out / MD).exists() and not (project.plan_dir / "staged").exists()


def test_cli_the_renderer_never_reads_a_batch_inputs_content(renderer):
    """W2 ruling 2: no script reads a path or a ref from a batch input. The renderer checks each one's digest and that is all."""
    names = {node.attr for node in ast.walk(ast.parse(RENDERER.read_text(encoding="utf-8"))) if isinstance(node, ast.Attribute)}
    assert "BATCH_INPUT_SCHEMA" not in names


def test_sarif_an_empty_mitigation_still_writes_message_markdown_as_the_empty_string(stage, renderer, tmp_path):
    """P0-8 (NFR-1): shipped scorer files carry ``"markdown": ""`` for a finding with no mitigation, so dropping the key loses a field."""
    text = edit_table_cell(make_threats_md(), "## 7. Recommended Actions", "S-2", "Mitigation", "")
    project = Project(stage, renderer, tmp_path, threats_text=text)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    results = results_by_id(project.sarif)
    assert results["S-2"]["message"] == {"text": by_id("S-2")["threat"], "markdown": ""}
    assert list(results["S-2"]["message"]) == ["text", "markdown"]
    assert [finding_id for finding_id, result in results.items() if "markdown" not in result["message"]] == [], "every result carries the key"
    assert results["T-1"]["message"]["markdown"] == mitigation_of(by_id("T-1")), "and a mitigation that is there is written as it was"
    sc.self_check(project.sarif["runs"][0]["results"], tool=TOOL, member_ids=OPEN_IDS, assignments={}, resolved_ids=RESOLVED_IDS, uri=URI)
