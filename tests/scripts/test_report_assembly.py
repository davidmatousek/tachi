"""Tests for ``scripts/assemble-report.py``, written before the script (F-374 T108 and T109; TDD).

They target ``contracts/cli.md`` (the CLI and the exit table; both modes take PLAN, RR3), ``contracts/part-files.md``
(the ``trees`` and ``report`` payloads, the assembler's layout, checks and exit codes, §5's PR 2 stage records),
``contracts/threat-model-records.md`` (the merged tree manifest, the outcome record) and ADR-050 D3 (parts, P0-4), D4
(exit codes, the stamp), D6 (RR3) and D14 (the tree batches and the report assembly), with the W2' entry errata
S1P-A18 (the forbidden-character predicate at the assembler's intake and in the tree checks) and S1P-A20 (a group's
roadmap primary follows D8), never an implementation. T108 writes ``assemble-report.py trees`` and T109 writes
``assemble-report.py report`` to them, once the hoist's E1-E5 are green and T091's first slice has landed. Until then
they fail: the script does not exist. What is in sections 1 to 4 of this module of the code-built layout is what T109 lists or the errata name: the
numbering, Section 5, Section 6, the roadmap's rows and their groups, the frontmatter, and the prose and cell sinks, with the slots ``count``,
``finding`` and ``name``, the fixed sentence and the cut, only to show the sinks and the counts. T110's richer-payload cases are section 5, at the end:
the payload's validator cases, then Section 1's Remediation Timeline, Section 3's leads and subsections, the category summaries of a run of more than 30,
the pattern subsections, the roadmap's intro and group rows, the appendix, Section 9's tables, every kind of slot, and the drift tests. Its readings are
RD-22 to RD-27, in that section's header.

How they run (ADR-050 D16, H15): the entry is loaded lazily through ``tests/conftest.py``'s ``_load_hyphenated_script``
and driven in-process through ``main(argv)``, so pytest-cov counts it. Nothing here starts a subprocess: the one thing a
process alone shows, the 3.9 refusal before any import, is ``test_runtime_floor_374.py``'s (T150 extends it).
Every plan, batch input and part is built from the contracts' key sets below, never through a helper of the script
under test, so the tests and the script share no code. Fixtures are synthetic (H8).

The readings. Where a contract leaves a form open, the test pins one and says ``# reading:``. Each is listed in the
lane's results file, "For the code halves", for the architect and for T092's planner tests to confirm or change:

* **RD-1, the CLI.** ``assemble-report.py trees|report --run-dir DIR --plan ID --plan-digest HEX`` (cli.md: PLAN is the
  pair). ``main(argv=None) -> int``. Codes 0, 1, 2 and 4 only: the script never returns 3 or 5.
* **RD-2, the failure message** is D4's four-line pattern with ``TACHI TREES FAILED:`` or ``TACHI REPORT FAILED:``.
* **RD-3, the layout** is D3's, under ``<run-dir>/.tachi-build/<stage>/<plan_id>/``, for the stages ``trees`` and ``report``.
* **RD-4, the trees plan.** ``params`` holds ``scoring_date``, ``rule_applied`` (the manifest's field, "the plan's") and
  ``reference_digest`` (RD-9). ``refs.baseline_dir`` names the baseline run directory, and only a run with a baseline has
  it. ``inputs.threats`` pins ``threats.md``. ``preimage`` is ``{}`` and ``out_snapshot`` is ``null`` (a batch stage
  has no canonical output of its own). A unit row is ``{finding_id, delta_status, action}`` and ``tree_paths`` names one
  file under ``<plan_id>/trees/`` for each finding of the batch.
* **RD-5, the carried trees.** A Critical or High open finding that no batch generates is carried: its tree is copied
  from ``<refs.baseline_dir>/attack-trees/<id-lowercase>-attack-tree.md``. A plan with no units keeps its ``refs``.
* **RD-6, Rule 3.** A part item whose ``action`` is ``carried_forward`` (with a ``similarity_score``) for an UNCHANGED
  finding that Rule 2 regenerated means the baseline file is the one copied, though the batch input planned
  ``regenerated``. cli.md and threat-model-records.md say ``action`` equals the batch input's, which leaves no room for
  Rule 3's decision. The architect rules this one.
* **RD-7, validate everything, then write.** A ``trees`` run that exits 2 or 4 writes no tree, no manifest and no stage
  record; a ``report`` run that exits 2 or 4 writes no ``threat-report.md`` and no stage record (D4: only shipped steps
  write canonical files, after full validation; the stage record is written on 0 only, RR3).
* **RD-8, which failure is which.** A tree file that fails a per-file check (one Mermaid block, the size cap, the
  forbidden-character predicate, a path outside the plan's ``trees/`` directory, a link) exits 2, as does a plan, batch
  input or part that fails D3's checks. A tree still missing, and any Critical or High set that differs from the
  generated and carried trees, exits 4 (FR-K5.5 applied early).
* **RD-9, the reference digest.** ``params.reference_digest`` is the SHA-256, as 64 hex digits, of the canonical JSON
  (sorted keys, no spaces, ASCII) of ``{"open": ..., "resolved": ...}`` from ``tachi_parsers.parse_reference_set``.
  ``reference_digest()`` below is the one place the tests compute it; T092's shared helper must give the same string.
* **RD-10, the report plan.** ``inputs`` names ``threats``, ``trees_plan`` (the trees plan file), ``tree_manifest`` and,
  for ``chains written``, ``attack_chains``. ``params`` holds ``scoring_date`` (the report's date),
  ``reference_digest`` and ``trees_plan_id``. ``batch_size`` is ``null`` and ``unit_count`` counts the fragment keys
  and the findings of every batch.
* **RD-11, the numbering.** Sections are numbered by position, as ``## <n>. <title>``, so Agentic Pattern Analysis
  takes the number after Cross-Layer Attack Chains and the later sections move up by one. Section 6 is on every run.
* **RD-12, the unit rows of a findings batch** carry the reference set's row keys (``finding_id``, ``component``,
  ``threat``, ``risk_level``, ``mitigation``, ``agentic_pattern``, ``delta_status``), as the planner's ``_unit_row``
  does, with ``section``, and the category-table row under ``category_row`` (RD-22, where the leads' cells come from).
* **RD-13, the stage record** lists the merged manifest (``trees``) or ``threat-report.md`` (``report``) among its
  ``outputs``, with the digest of the file in place, and holds exactly the stage's closed ``counts`` keys.
* **RD-14, Section 5** prints ``### {ID}: {threat}``, then the metadata line, the ``tree_summary``, the fenced tree and
  the notes. Only the order of the heading, the summary and the fence is asserted.
* **RD-15, the pinned trees plan.** ``report`` holds the trees plan that its own plan pins to D3's checks as well (pointer, digest, batches,
  parts), but the trees plan's ``threats`` input is checked by ``params.reference_digest`` like the report plan's, since Steps 2.5-2.8 rewrite
  ``threats.md`` after the trees stage ran.
* **RD-16, an unclosed fence** is not a Mermaid block, so a tree file whose fence never closes is refused with the other bad trees.
* **RD-17, Section 5 with no tree** prints the template's note ("No Critical or High findings identified."), as the template says.
* **RD-18, the first checks** are ``tachi_parts.entry_arguments``' (S1P-A42), with ``option="--run-dir"``: the directory first (exit 1, ``--run-dir is not a
  directory``), then ``--plan`` and ``--plan-digest`` (exit 2), each in the contract's words. A plan file that is gone is exit 1, and one that is a link exit 2.
* **RD-19, a missing input and a vanished one.** A file that D3's guard pins by digest and that is gone since the plan is exit 2 (the guard's own words,
  "changed (or vanished)"), in ``trees`` for ``threats.md`` and in ``report`` for the trees plan and the manifest. A file that the plan doesn't pin,
  ``threats.md`` and ``attack-chains.md`` in ``report`` (RR3), is read when it is needed, and a missing one is exit 1 (part-files.md: "an input ... is missing").
* **RD-20, a write that fails part way.** ``trees`` writes the trees first and the manifest last, with no stage record, and exits 4 with a remedy that says to
  run ``trees`` again (it replaces every file it writes), not the staged writers' "the earlier outputs were left or put back".
* **RD-21, the staged-file backstop** (P0-4's, and D4's from-disk check) can't be reached through a part, because the intake refuses what it checks. So these tests
  replace ``_assemble`` with a copy that damages the text, and require exit 4, the agent's report left where it was, and nothing in the run but the staged copy.

Standard library, PyYAML (the tests' own dependency) and pytest only, and Python 3.9 syntax.
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
import sys
from pathlib import Path

import pytest
import yaml

from ..conftest import _load_hyphenated_script

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import tachi_parsers  # noqa: E402  -- after the sys.path mutation
import tachi_parts as tp  # noqa: E402

ASSEMBLER = SCRIPTS_DIR / "assemble-report.py"
TEMPLATE = REPO_ROOT / "templates" / "tachi" / "output-schemas" / "threat-report.md"

MODES = ("trees", "report")
STAGE_AGENT = {"trees": "tachi-attack-tree-delta", "report": "tachi-threat-report"}
FAILED_BANNER = {"trees": "TACHI TREES FAILED:", "report": "TACHI REPORT FAILED:"}

DATE = "2026-11-24"
BASELINE_DATE = "2026-11-10"
CREATED = "2026-11-24T10:00:00Z"
TREES_ID = "20261124T100000Z-aaaaaaaaaaaa"
REPORT_ID = "20261124T110000Z-bbbbbbbbbbbb"
OTHER_ID = "20261124T120000Z-cccccccccccc"
DASH = "—"
RULE_NAME = {"no-baseline": "no-baseline", "rule1": "Rule 1", "rule2": "Rule 2", "no-op": "no-op"}

# --------------------------------------------------------------------------- synthetic findings

F = collections.namedtuple("F", "id status risk component threat mitigation pattern layer likelihood impact")

# Nine open findings. The Critical and High ones (seven) have trees. In S-2 order across every finding:
# S-1, T-1, T-2, I-1, D-1, E-1, AG-1, LLM-1, OI-1. In the manifest's order: Critical (S-1, T-1, LLM-1), then High
# (T-2, I-1, AG-1, OI-1).
FINDINGS = [
    F("S-1", "NEW", "Critical", "Gateway", "Session token replay", "Bind each token to its client", DASH, "L4", "HIGH", "HIGH"),
    F("T-1", "UPDATED", "Critical", "Order Service", "Order payload tampering", "Sign every order payload", DASH, "L3", "MEDIUM", "HIGH"),
    F("T-2", "UNCHANGED", "High", "Order Service", "Queue message tampering", "Authenticate queue producers", DASH, "L3", "MEDIUM", "HIGH"),
    F("I-1", "NEW", "High", "Order Database", "Verbose errors leak internals", "Return generic error pages", DASH, "L2", "HIGH", "MEDIUM"),
    F("D-1", "UNCHANGED", "Medium", "Gateway", "Request flood", "Rate limit each client", DASH, "L4", "MEDIUM", "MEDIUM"),
    F("E-1", "UNCHANGED", "Low", "Admin Console", "Role confusion", "Enforce least privilege", DASH, "L4", "LOW", "MEDIUM"),
    F("AG-1", "NEW", "High", "Planner Agent", "Tool call escalation", "Allow list the tools of each task", DASH, "L3", "MEDIUM", "HIGH"),
    F("LLM-1", "NEW", "Critical", "Planner Agent", "Prompt injection through documents", "Isolate untrusted content from instructions", DASH, "L1", "HIGH", "HIGH"),
    F("OI-1", "UNCHANGED", "High", "Report Renderer", "Unescaped model output reaches the browser", "Encode all model output", DASH, "L7", "MEDIUM", "HIGH"),
]
RESOLVED = [("R-9", "Legacy Cache", "Stale cache poisoning", "High", "Component removed")]
RISK_RANK = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Note": 4}
# The OWASP Reference cell of an agentic or LLM finding (the AI tables' extra column). A finding with no entry shows the dash that the template's rows show.
OWASP_OF = {"AG-1": "OWASP ASI02:2026", "LLM-1": "OWASP LLM01:2026, CWE-77", "OI-1": "OWASP LLM05:2026"}
NARRATE_LIMIT = 30  # part-files.md, "Narrated or summarized": more than this many open findings summarizes the Medium, Low and Note ones
CATEGORY_OF_PREFIX = {
    "S": "spoofing", "T": "tampering", "R": "repudiation", "I": "information_disclosure", "D": "denial_of_service",
    "E": "elevation_of_privilege", "AG": "agentic", "AGP": "agentic", "TE": "agentic", "LLM": "llm", "OI": "llm", "MI": "llm",
}
CATEGORY_ORDER = ("spoofing", "tampering", "repudiation", "information_disclosure", "denial_of_service",
                  "elevation_of_privilege", "agentic", "llm")
CATEGORY_TITLE = {
    "spoofing": "Spoofing", "tampering": "Tampering", "repudiation": "Repudiation", "information_disclosure": "Information Disclosure",
    "denial_of_service": "Denial of Service", "elevation_of_privilege": "Elevation of Privilege", "agentic": "Agentic", "llm": "LLM",
}
CATEGORY_HEADING = {
    "spoofing": "### 3.1 Spoofing (S)", "tampering": "### 3.2 Tampering (T)", "repudiation": "### 3.3 Repudiation (R)",
    "information_disclosure": "### 3.4 Information Disclosure (I)", "denial_of_service": "### 3.5 Denial of Service (D)",
    "elevation_of_privilege": "### 3.6 Elevation of Privilege (E)", "agentic": "### 4.1 Agentic Threats (AG)", "llm": "### 4.2 LLM Threats (LLM)",
}
OUTCOME_ZERO = "0 chains passed filter (no candidate links); candidates 3"
OUTCOME_WRITTEN = "chains written (2); candidates 5; surfaced 2"
OUTCOME_SKIPPED = "skipped (attack-chains.md missing)"
CHAINS = [("CHAIN-001", "Token replay reaches order tampering"), ("CHAIN-002", "Injected documents escalate agent tools")]

# S1P-A18: the predicate's set, one sample for each class it returns, and the ones it leaves allowed (ADR-050 D3, step 10).
FORBIDDEN_SAMPLES = [
    ("nul", "\x00"), ("escape", "\x1b"), ("delete", "\x7f"), ("next-line", "\x85"), ("carriage-return", "\r"),
    ("line-separator", "\u2028"), ("paragraph-separator", "\u2029"), ("left-to-right-mark", "\u200e"),
    ("right-to-left-override", "\u202e"), ("left-to-right-isolate", "\u2066"), ("arabic-letter-mark", "\u061c"),
    ("tag-letter-a", "\U000e0041"),
]
ALLOWED_SAMPLES = [("tab", "\t"), ("zero-width-joiner", "\u200d"), ("variation-selector", "\ufe0f"), ("no-break-space", "\u00a0")]


def s2(finding_id):
    """S-2's total order, from the one definition in ``tachi_parts``."""
    return tp.finding_sort_key(finding_id)


def category_of(finding_id):
    return CATEGORY_OF_PREFIX[tp.canonical_finding_id(finding_id).partition("-")[0]]


def findings_for(rule, patterns=False):
    """The findings of one scenario. ``no-baseline`` is a first run (all NEW), ``rule1`` has nothing but UNCHANGED findings,
    ``rule2`` the mixed statuses above, and ``no-op`` only a Medium and a Low finding, so no tree is planned."""
    if rule == "no-op":
        return [f for f in FINDINGS if f.risk in ("Medium", "Low")]
    out = []
    for f in FINDINGS:
        status = f.status if rule == "rule2" else ("UNCHANGED" if rule == "rule1" else "NEW")
        pattern = "agent_collusion" if (patterns and f.id == "AG-1") else f.pattern
        out.append(f._replace(status=status, pattern=pattern))
    return out


def big_findings(rule="no-baseline"):
    """The nine findings above and 25 more Medium, Low and Note ones: 34 open findings, more than 30, so that the Medium, Low and Note ones are summarized by
    category and only the seven Critical and High ones are narrated (part-files.md, "Narrated or summarized"). They stay the run's only trees. Every category but
    LLM has an extra one, and LLM's two findings are narrated, so LLM alone has no summary."""
    extras = []
    for prefix, count, first in (("S", 4, 2), ("T", 4, 3), ("R", 4, 1), ("I", 4, 2), ("D", 3, 2), ("E", 3, 2), ("AG", 3, 2)):
        for n in range(first, first + count):
            extras.append("%s-%d" % (prefix, n))
    assert len(extras) == 25
    out = list(findings_for(rule))
    for k, finding_id in enumerate(extras):
        status = ("NEW", "UNCHANGED", "UPDATED")[k % 3] if rule == "rule2" else ("UNCHANGED" if rule == "rule1" else "NEW")
        out.append(F(finding_id, status, ("Medium", "Low", "Note")[k % 3], ("Gateway", "Order Service", "Admin Console")[k % 3], "Synthetic threat %s" % finding_id,
                     "Synthetic mitigation for %s" % finding_id, DASH, "L%d" % (k % 7 + 1), "MEDIUM", "LOW"))
    return out


def manifest_order(findings):
    """Critical findings first, then High, each in S-2 order: the merged manifest's order (threat-model-records.md)."""
    chosen = [f for f in findings if f.risk in ("Critical", "High")]
    return sorted(chosen, key=lambda f: (RISK_RANK[f.risk], s2(f.id)))


# --------------------------------------------------------------------------- synthetic threats.md and attack-chains.md

def make_threats_md(findings, resolved=(), groups=(), baseline=None, outcome=None, extra=""):
    """A synthetic joined ``threats.md``.

    ``baseline`` is ``None`` or ``(source, date, finding_count, run_id)`` for the frontmatter's ``baseline`` block, ``groups`` are
    Section 4a rows as ``(group ID, [finding IDs])``, and ``outcome`` is the text of the one outcome record
    (``threat-model-records.md``), or ``None`` for a file with none. ``extra`` is appended as it is.
    """
    lines = ["---", 'schema_version: "1.4"', 'date: "%s"' % DATE, 'input_format: "mermaid"', 'classification: "confidential"',
             'run_id: "2026-11-24T09-00-00"', "baseline:"]
    if baseline is None:
        lines += ["  source: null", "  date: null", "  finding_count: null", "  run_id: null"]
    else:
        source, date, count, run_id = baseline
        lines += ['  source: "%s"' % source, '  date: "%s"' % date, "  finding_count: %d" % count, '  run_id: "%s"' % run_id]
    lines += ["coverage_gate:", '  status: "pass"', "  gaps: []", "---", "", "# Threat Model Report", "",
              "## 1. System Overview", "", "### Components", "",
              "| Component | Type | MAESTRO Layer | Description |", "|---|---|---|---|",
              "| Gateway | Process | L4 | The edge of the synthetic system |", "",
              "## 2. Trust Boundaries", "", "### Trust Zones", "", "| Zone | Trust Level | Components |", "|---|---|---|",
              "| Edge | Untrusted | Gateway |", "", "## 3. STRIDE Tables", ""]
    by_category = collections.OrderedDict((key, []) for key in CATEGORY_ORDER)
    for f in sorted(findings, key=lambda f: s2(f.id)):
        by_category[category_of(f.id)].append(f)
    for key in CATEGORY_ORDER:
        if key == "agentic":
            lines += ["## 4. AI Threat Tables", ""]
        ai = key in ("agentic", "llm")
        lines += [CATEGORY_HEADING[key], ""]
        lines += ["| ID | Status | Component | MAESTRO Layer | Threat |%s Likelihood | Impact | Risk Level | Mitigation |" % (" OWASP Reference |" if ai else ""),
                  "|---|---|---|---|---|%s---|---|---|---|" % ("---|" if ai else "")]
        for f in by_category[key]:
            lines.append("| %s | %s | %s | %s | %s |%s %s | %s | %s | %s |" % (
                f.id, f.status, f.component, f.layer, f.threat, (" %s |" % OWASP_OF.get(f.id, DASH)) if ai else "", f.likelihood, f.impact, f.risk,
                f.mitigation))
        lines.append("")
    lines += ["## 4a. Correlated Findings", ""]
    if groups:
        lines += ["| Group | Findings | Component | Threat Summary | Risk Level |", "|---|---|---|---|---|"]
        lines += ["| %s | %s | Order Service | Related threats | High |" % (gid, ", ".join(members)) for gid, members in groups]
    else:
        lines += ["No cross-agent correlations detected."]
    lines.append("")
    if resolved:
        lines += ["## 4c. Resolved Findings", "", "| ID | Component | Threat | Last Risk Level | Resolution Reason |", "|---|---|---|---|---|"]
        lines += ["| %s | %s | %s | %s | %s |" % row for row in resolved]
        lines.append("")
    lines += ["## 7. Recommended Actions", "",
              "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |",
              "|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(findings, key=lambda f: (RISK_RANK[f.risk], s2(f.id))):
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            f.id, f.status, CATEGORY_TITLE[category_of(f.id)], f.pattern, f.component, f.layer, f.threat, f.risk, f.mitigation))
    lines.append("")
    if outcome is not None:
        lines += ["## Attack Chain Outcome", "", "**Attack chain outcome**: %s" % outcome, ""]
    return "\n".join(lines) + extra


# The members, the layers and the chain-breaking control of the chains that the harness knows. A chain that it doesn't know (a test that plants another ID) has the
# first one's members. The control's recommendation is stored as a renderer writes it, escaped: the reader decodes it, and the report has to write it again.
CHAIN_MEMBERS = {
    "CHAIN-001": [("S-1", "L4", "initial_exploit", "Gateway", "Spoofing", "Critical"),
                  ("T-1", "L3", "terminal_impact", "Order Service", "Tampering", "Critical")],
    "CHAIN-002": [("LLM-1", "L1", "initial_exploit", "Planner Agent", "LLM", "Critical"),
                  ("AG-1", "L3", "intermediate_cascade", "Planner Agent", "Agentic", "High"),
                  ("OI-1", "L7", "terminal_impact", "Report Renderer", "LLM", "High")],
}
CHAIN_LAYERS = {"CHAIN-001": ["L4", "L3"], "CHAIN-002": ["L1", "L3", "L7"]}
CHAIN_CONTROL = {"CHAIN-001": ("T-1", "L3", "Verify the signature of every order &#124; reject the unsigned ones"),
                 "CHAIN-002": ("AG-1", "L3 — Agent Framework", "Allow list the tools of each task")}


def make_attack_chains_md(chains, candidates=5):
    """A synthetic ``attack-chains.md`` (S-3(g)): every chain given is surfaced, and one more is consolidated into Section 3's table."""
    lines = ["---", 'schema_version: "1.1"', 'date: "%s"' % DATE, "chain_count: %d" % (len(chains) + 1), "surfaced_count: %d" % len(chains),
             "candidate_count: %d" % candidates, "---", "", "# Attack Chains", "", "## 1. Chain Summary", "",
             "| Chain ID | Title | Layers | Findings | Max Severity | Chain-Breaking Target | Converging Chains |", "|---|---|---|---|---|---|---|"]
    for chain_id, title in chains:
        members = CHAIN_MEMBERS.get(chain_id, CHAIN_MEMBERS["CHAIN-001"])
        lines.append("| %s | %s | %s | %s | Critical | %s | 1 |" % (chain_id, title, " → ".join(CHAIN_LAYERS.get(chain_id, ["L3", "L4"])),
                                                                 " → ".join(m[0] for m in members), CHAIN_CONTROL.get(chain_id, CHAIN_CONTROL["CHAIN-001"])[0]))
    lines += ["", "## 2. Chain Details", ""]
    for chain_id, title in chains:
        members = CHAIN_MEMBERS.get(chain_id, CHAIN_MEMBERS["CHAIN-001"])
        target, target_layer, recommendation = CHAIN_CONTROL.get(chain_id, CHAIN_CONTROL["CHAIN-001"])
        lines += ["### %s: %s" % (chain_id, title), "", "**Layers**: " + " → ".join(CHAIN_LAYERS.get(chain_id, ["L3", "L4"])), "**Max Severity**: Critical",
                  "**Surfaced**: Yes", "**Converging chains**: 1", "", "#### Member Findings", "",
                  "| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |", "|---|---|---|---|---|---|"]
        lines += ["| %s | %s | %s | %s | %s | %s |" % member for member in members]
        lines += ["", "#### Chain-Breaking Controls", "", "**Target**: %s (%s)" % (target, target_layer),
                  "**Rationale**: Removing this finding disconnects the chain.", "**Recommendation**: " + recommendation, ""]
    lines += ["## 3. Other Consolidated Chains", "", "| Chain ID | Layers | Findings | Max Severity | Chain-Breaking Target |", "|---|---|---|---|---|",
              "| CHAIN-007 | L2 \u2192 L3 \u2192 L7 | T-2 \u2192 I-1 \u2192 S-1 | High | I-1 |", "", "**Consolidated chains not listed**: 0", ""]
    return "\n".join(lines) + "\n"


def reference_digest(threats_text):
    """RD-9: the SHA-256 of the canonical JSON of the reference set's open and resolved rows."""
    try:
        rs = tachi_parsers.parse_reference_set(threats_text)
    except tachi_parsers.ReferenceSetError:
        return "0" * 64  # a file that the shared reader refuses has no reference set to digest, and the assembler must refuse it all the same
    body = json.dumps({"open": rs["open"], "resolved": rs["resolved"]}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- synthetic tree files

def tree_source(finding_id, variant, ticks=0):
    """Mermaid source for one tree. It holds a non-ASCII label and a tab, so a byte-for-byte copy shows. ``ticks`` puts a run of
    that many backticks inside a label, which the inline copy has to out-fence (FR-K5.2)."""
    lines = ["graph TD",
             '    Goal["[GOAL] Attack on %s (%s)"]' % (finding_id, variant),
             '    Goal --> A["[OR] First route"]',
             '    A --> A1["Café → leaf of %s\twith a tab"]' % finding_id,
             "    classDef critical fill:#d32f2f,color:#fff",
             "    class Goal critical"]
    if ticks:
        lines.insert(3, '    N["a run of %s inside a label"]' % ("`" * ticks))
    return "\n".join(lines)


def tree_file(finding_id, source, fence=3, label="fresh"):
    """A standalone tree file as the agent writes it: a header with trailing spaces, then one fenced Mermaid block."""
    ticks = "`" * fence
    return ("# Attack Tree: %s — %s   \n\n**Risk Level**: Critical\n**Component**: Synthetic\n**Threat**: Synthetic threat\n\n%smermaid\n%s\n%s\n"
            % (finding_id, label, ticks, source, ticks))


def tree_name(finding_id):
    return "%s-attack-tree.md" % finding_id.lower()


# --------------------------------------------------------------------------- reading rendered text

_FENCE_OPEN = re.compile(r"^( {0,3})(`{3,}|~{3,})([^\n]*)$")


def fenced_blocks(text):
    """Fenced code blocks by CommonMark's rule (a fence closes on a run of its own character at least as long as the opener, with
    nothing after it): ``[{info, fence, source, closed, start, end}]`` with 0-based line numbers, in order."""
    lines = text.split("\n")
    blocks, i = [], 0
    while i < len(lines):
        m = _FENCE_OPEN.match(lines[i])
        if m is None or (m.group(2)[0] == "`" and "`" in m.group(3)):
            i += 1
            continue
        char, size = m.group(2)[0], len(m.group(2))
        j, body, closed = i + 1, [], False
        closer = re.compile(r"^ {0,3}%s{%d,}[ \t]*$" % (re.escape(char), size))
        while j < len(lines):
            if closer.match(lines[j]):
                closed = True
                break
            body.append(lines[j])
            j += 1
        info = m.group(3).strip().split(" ")[0].lower() if m.group(3).strip() else ""
        blocks.append({"info": info, "fence": size, "source": "\n".join(body), "closed": closed, "start": i, "end": j})
        i = j + 1
    return blocks


def mermaid_sources(text):
    return [b["source"] for b in fenced_blocks(text) if b["info"] == "mermaid"]


def longest_run(text, char="`"):
    runs = re.findall("%s+" % re.escape(char), text)
    return max([len(r) for r in runs] or [0])


def atx_headings(text):
    """``[(line number, level, title)]`` for every ATX heading outside a fenced block (0-based line numbers)."""
    inside = set()
    for b in fenced_blocks(text):
        inside.update(range(b["start"], b["end"] + 1))
    found = []
    for n, line in enumerate(text.split("\n")):
        m = re.match(r"^(#{1,6}) +(.*?)\s*$", line)
        if m and n not in inside:
            found.append((n, len(m.group(1)), m.group(2)))
    return found


def numbered_sections(text):
    """``[(number, title)]`` for each ``## <n>. <title>`` heading, in file order."""
    return [(int(m.group(1)), m.group(2)) for _, level, title in atx_headings(text) if level == 2
            for m in [re.match(r"^(\d+)\. (.+)$", title)] if m]


def section_text(text, number):
    """The text under ``## <number>. ...`` up to the next ``## `` heading (heading line excluded)."""
    lines = text.split("\n")
    heads = [(n, title) for n, level, title in atx_headings(text) if level == 2]
    for k, (n, title) in enumerate(heads):
        if re.match(r"^%d\. " % number, title):
            end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
            return "\n".join(lines[n + 1:end])
    raise AssertionError("no section %d in the report" % number)


def frontmatter_of(text):
    """The report's YAML frontmatter, bare or inside a ```yaml fence (the template's two shapes)."""
    m = re.match(r"\A\s*---[ \t]*\n(.*?)\n---[ \t]*\n", text, re.S) or re.search(r"```yaml[ \t]*\n---[ \t]*\n(.*?)\n---[ \t]*\n```", text, re.S)
    assert m is not None, "the report has no frontmatter"
    return yaml.safe_load(m.group(1))


def template_titles():
    """``{number: title}`` of the template's ``## <n>. <title>`` sections: the assembler's titles follow the template (T113 aligns it)."""
    text = TEMPLATE.read_text(encoding="utf-8")
    return {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"(?m)^## (\d+)\. (.+)$", text)}


# --------------------------------------------------------------------------- running the entry

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


_ENTRY = {}


class LazyEntry(object):
    """The entry, loaded when a test first calls ``main``. A script that does not exist yet then fails that one test, by name, in its
    body (a fixture that failed would report an error in the test's setup instead), and the harness tests above never touch it."""

    def __init__(self, request):
        self.request = request

    def load(self):
        """The loaded module. A test that replaces one of its internals (the staged-file backstop) takes it from here, so it changes the module that ``main`` runs."""
        if not ASSEMBLER.is_file():
            pytest.fail("scripts/assemble-report.py does not exist yet: T108 and T109 write it to these tests (TDD), and %s needs it" % self.request.node.name,
                        pytrace=False)
        if "module" not in _ENTRY:
            _ENTRY["module"] = _load_hyphenated_script("assemble_report_under_test", "assemble-report.py")
        return _ENTRY["module"]

    def main(self, argv=None):
        return self.load().main(argv)


@pytest.fixture
def assembler(request):
    """``scripts/assemble-report.py``, loaded on first use (``LazyEntry``)."""
    return LazyEntry(request)


def tree_state(root):
    """``{relative path: sha256}`` for every file under ``root``, to prove that nothing there changed."""
    root = Path(root)
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, doc):
    """Write a JSON document the way the planner does (sorted keys, two-space indent) and return its SHA-256."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(data)
    return tp.sha256_hex(data)


def plan_input(path):
    data = Path(path).read_bytes()
    return {"path": str(path), "sha256": tp.sha256_hex(data), "bytes": len(data)}


# --------------------------------------------------------------------------- narrative fragments (digit-free: ADR-050 D3's numeral ban)

_WORDS = dict(zip("0123456789", "zero one two three four five six seven eight nine".split()))


def digit_free(text):
    return "".join(_WORDS.get(c, c) for c in text)


def marker(section, key):
    """A fragment's text: unique to its section and key, and with no digit outside a slot."""
    return "Marker for %s %s." % (section, digit_free(key))


# --------------------------------------------------------------------------- the world

class World(object):
    """One synthetic run: ``run/`` is ``--run-dir``, ``baseline/`` the earlier run, and the stages' plans, batch inputs and parts are
    written from the contracts' key sets (``tachi_parts.KEY_SETS``), with no help from the script under test.

    ``rule`` picks the scenario: ``no-baseline`` (a first run, every tree generated), ``rule1`` (all UNCHANGED: trees with a
    baseline file are carried, the others generated), ``rule2`` (mixed statuses, every tree generated, Rule 3 reconciling the UNCHANGED
    ones) and ``no-op`` (no Critical or High finding). ``build("trees")`` writes the trees stage and ``build("report")`` the trees
    stage, the merged trees and manifest as the assembler's ``trees`` mode should leave them, and the report stage.
    """

    def __init__(self, root, rule="no-baseline", per_batch=4, patterns=False, outcome=OUTCOME_ZERO, planned_chains=False, groups=(),
                 findings=None, resolved=None, no_baseline_tree=None, rule3=None, compliance=False, themes=1, threats_extra="",
                 ticks_for=None, drop_units=(), extra_units=(), baseline_source="baseline/threats.md", trees_id=TREES_ID, report_id=REPORT_ID,
                 pattern_of=None, overview=False, per_report_batch=None, drop_row_keys=(), flaws=()):
        self.root, self.rule, self.per_batch = Path(root), rule, per_batch
        self.out, self.baseline = self.root / "run", self.root / "baseline"
        self.patterns, self.outcome, self.planned_chains = patterns, outcome, planned_chains
        self.groups, self.compliance, self.themes, self.threats_extra = list(groups), compliance, themes, threats_extra
        self.overview, self.per_report_batch, self.drop_row_keys = overview, per_report_batch, tuple(drop_row_keys)
        self.flaws = set(flaws)   # a planner that planned differently from the contract: ``no-item:<ID>``, ``no-summary:<category>``, ``extra-summary:<category>``, ...
        self.baseline_source = baseline_source
        self.ticks_for = dict(ticks_for or {})
        self.ids = {"trees": trees_id, "report": report_id}
        self.findings = list(findings) if findings is not None else findings_for(rule, patterns)
        self.findings = [f._replace(pattern=pattern_of[f.id]) if f.id in (pattern_of or {}) else f for f in self.findings]
        self.resolved = list(RESOLVED if (resolved is None and rule == "rule2") else (resolved or []))
        self.has_baseline = rule in ("rule1", "rule2")
        self.status_of = {f.id: f.status for f in self.findings}
        ch = [f.id for f in manifest_order(self.findings)]
        self.ch_ids = ch
        if rule == "rule1":
            lacking = set(("I-1",) if no_baseline_tree is None else no_baseline_tree)
            self.baseline_tree_ids = [i for i in ch if i not in lacking]
            self.generated = [i for i in ch if i in lacking]
        elif rule == "rule2":
            self.baseline_tree_ids = [i for i in ch if self.status_of[i] == "UNCHANGED"]
            self.generated = list(ch)
        else:
            self.baseline_tree_ids, self.generated = [], (list(ch) if rule == "no-baseline" else [])
        # A planner that planned differently: ``drop_units`` leaves a Critical or High finding with no tree, ``extra_units`` plans a tree
        # for a finding that has none to make.
        self.generated = [i for i in self.generated if i not in set(drop_units)] + [i for i in extra_units if i not in self.generated]
        planned = set(self.generated) | set(self.baseline_tree_ids)
        self.tree_ids = [i for i in ch if i in planned] + [i for i in sorted(planned, key=s2) if i not in ch]
        if rule3 is None and rule == "rule2":
            rule3 = {"T-2": ("carried_forward", 0.93), "OI-1": ("regenerated", 0.41)}
        self.rule3 = dict(rule3 or {})
        self.digest = {}
        self.fresh, self.base_bytes = {}, {}
        self.threats_text = ""
        self.last = None

    # ---- layout (RD-3)
    def plan_id(self, mode):
        return self.ids[mode]

    def stage_dir(self, mode):
        return self.out / ".tachi-build" / mode

    def plan_dir(self, mode):
        return self.stage_dir(mode) / self.ids[mode]

    def plan_path(self, mode):
        return self.plan_dir(mode) / "plan.json"

    def pointer_path(self, mode):
        return self.stage_dir(mode) / "current.json"

    def input_path(self, mode, batch_id):
        return self.plan_dir(mode) / "inputs" / ("%s.json" % batch_id)

    def part_path(self, mode, batch_id, attempt=1):
        return self.plan_dir(mode) / "parts" / ("%s.a%d.json" % (batch_id, attempt))

    def record_path(self, mode):
        return self.plan_dir(mode) / "stage-record.json"

    @property
    def threats_path(self):
        return self.out / "threats.md"

    @property
    def chains_path(self):
        return self.out / "attack-chains.md"

    @property
    def manifest_path(self):
        return self.out / "attack-trees" / ".manifest.json"

    @property
    def report_path(self):
        return self.out / "threat-report.md"

    def tree_path(self, finding_id):
        return self.out / "attack-trees" / tree_name(finding_id)

    def source_tree_path(self, finding_id):
        return self.plan_dir("trees") / "trees" / tree_name(finding_id)

    def baseline_tree_path(self, finding_id):
        return self.baseline / "attack-trees" / tree_name(finding_id)

    def batch_ids(self, mode):
        return [entry["batch_id"] for entry in read_json(self.plan_path(mode))["batches"]]

    def record(self, mode):
        return read_json(self.record_path(mode))

    @property
    def report_text(self):
        return self.report_path.read_text(encoding="utf-8")

    # ---- the plans' shared pieces (RD-4, RD-10)
    def params(self, mode):
        digest = reference_digest(self.threats_text)
        if mode == "trees":
            return {"scoring_date": DATE, "rule_applied": RULE_NAME[self.rule], "reference_digest": digest}
        return {"scoring_date": DATE, "reference_digest": digest, "trees_plan_id": self.ids["trees"]}

    def refs(self, mode):
        return {"baseline_dir": str(self.baseline)} if (mode == "trees" and self.has_baseline) else {}

    def write_threats(self):
        baseline = (self.baseline_source, BASELINE_DATE, len(self.findings) + len(self.resolved), "2026-11-10T09-00-00") if self.has_baseline else None
        self.threats_text = make_threats_md(self.findings, self.resolved, self.groups, baseline, self.outcome, self.threats_extra)
        self.out.mkdir(parents=True, exist_ok=True)
        self.threats_path.write_text(self.threats_text, encoding="utf-8")

    def write_batch(self, mode, batch_id, finding_ids, units, items, fragments=(), tree_paths=None):
        """One batch's input and part (attempt 1), and the input's digest for the plan's entry."""
        plan_id = self.ids[mode]
        batch_input = {
            "schema": tp.BATCH_INPUT_SCHEMA, "plan_id": plan_id, "batch_id": batch_id, "stage": mode, "agent_type": STAGE_AGENT[mode],
            "finding_ids": list(finding_ids), "attempt": 1, "part_path": str(self.part_path(mode, batch_id)),
            "tree_paths": dict(tree_paths or {}), "units": units, "refs": self.refs(mode), "params": self.params(mode),
        }
        digest = write_json(self.input_path(mode, batch_id), batch_input)
        part = {"schema": tp.PART_SCHEMA, "plan_id": plan_id, "batch_id": batch_id, "stage": mode, "agent_type": STAGE_AGENT[mode],
                "finding_ids": list(finding_ids), "items": items, "fragments": list(fragments)}
        write_json(self.part_path(mode, batch_id), part)
        return {"batch_id": batch_id, "parent": None, "attempt": 1, "finding_ids": list(finding_ids), "input_sha256": digest, "state": "done"}

    def write_plan(self, mode, batches, unit_count, inputs, batch_size):
        plan = {
            "schema": tp.PLAN_SCHEMA, "plan_id": self.ids[mode], "stage": mode, "agent_type": STAGE_AGENT[mode], "created_utc": CREATED,
            "tachi_version": tp.VERSION, "inputs": inputs, "refs": self.refs(mode), "architecture_warning": None, "params": self.params(mode),
            "batch_size": batch_size, "unit_count": unit_count, "preimage": {}, "out_snapshot": None,
            "retry_budget": {"limit": 2 * len(batches), "used": 0}, "batches": batches,
        }
        self.digest[mode] = write_json(self.plan_path(mode), plan)
        write_json(self.pointer_path(mode), {"schema": tp.POINTER_SCHEMA, "plan_id": self.ids[mode]})

    # ---- the trees stage (T108)
    def planned_action(self, finding_id):
        return "regenerated" if (self.rule == "rule2" and self.status_of[finding_id] == "UNCHANGED") else "generated_fresh"

    def item_action(self, finding_id):
        return self.rule3[finding_id][0] if finding_id in self.rule3 else self.planned_action(finding_id)

    def final_action(self, finding_id):
        return self.item_action(finding_id) if finding_id in self.generated else "carried_forward"

    def part_item(self, finding_id):
        item = {"finding_id": finding_id, "delta_status": self.status_of[finding_id], "action": self.item_action(finding_id)}
        if finding_id in self.rule3:
            item["similarity_score"] = self.rule3[finding_id][1]
        return item

    def make_tree(self, finding_id, variant):
        ticks = self.ticks_for.get(finding_id, 0)
        return tree_file(finding_id, tree_source(finding_id, variant, ticks), fence=max(3, ticks + 1), label=variant).encode("utf-8")

    def build_trees(self):
        self.write_threats()
        for finding_id in self.baseline_tree_ids:
            self.base_bytes[finding_id] = self.make_tree(finding_id, "baseline")
            path = self.baseline_tree_path(finding_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.base_bytes[finding_id])
        if self.has_baseline:
            self.baseline.mkdir(parents=True, exist_ok=True)
        ordered = sorted(self.generated, key=s2)
        chunks = [ordered[i:i + self.per_batch] for i in range(0, len(ordered), self.per_batch)]
        batches = []
        for number, chunk in enumerate(chunks, 1):
            tree_paths = {}
            for finding_id in chunk:
                self.fresh[finding_id] = self.make_tree(finding_id, "fresh")
                tree_paths[finding_id] = str(self.source_tree_path(finding_id))
                self.source_tree_path(finding_id).parent.mkdir(parents=True, exist_ok=True)
                self.source_tree_path(finding_id).write_bytes(self.fresh[finding_id])
            units = [{"finding_id": i, "delta_status": self.status_of[i], "action": self.planned_action(i)} for i in chunk]
            batches.append(self.write_batch("trees", "B%03d" % number, chunk, units, [self.part_item(i) for i in chunk], tree_paths=tree_paths))
        self.write_plan("trees", batches, len(ordered), {"threats": plan_input(self.threats_path)}, self.per_batch if ordered else None)

    def expected_bytes(self, finding_id):
        """The bytes that ``attack-trees/<id>-attack-tree.md`` must hold after ``trees``: a copy of the fresh tree, or of the baseline's."""
        return self.fresh[finding_id] if self.final_action(finding_id) != "carried_forward" else self.base_bytes[finding_id]

    def expected_manifest(self):
        """The merged schema-1.0 manifest (threat-model-records.md): Critical first, then High, each in S-2 order."""
        trees = []
        for finding_id in self.tree_ids:
            entry = {"finding_id": finding_id, "delta_status": self.status_of[finding_id], "action": self.final_action(finding_id)}
            if finding_id in self.rule3:
                entry["similarity_score"] = self.rule3[finding_id][1]
            entry["file_path"] = "attack-trees/" + tree_name(finding_id)
            trees.append(entry)
        counts = collections.Counter(entry["action"] for entry in trees)
        return {"schema_version": "1.0", "rule_applied": RULE_NAME[self.rule], "attack_tree_count": len(trees), "trees": trees,
                "summary": {"fresh": counts["generated_fresh"], "carried_forward": counts["carried_forward"], "regenerated": counts["regenerated"]}}

    def materialize_trees(self):
        """Leave ``attack-trees/`` as a right ``trees`` run does, so the report stage's tests don't depend on that mode."""
        directory = self.out / "attack-trees"
        directory.mkdir(parents=True, exist_ok=True)
        for finding_id in self.tree_ids:
            self.tree_path(finding_id).write_bytes(self.expected_bytes(finding_id))
        write_json(self.manifest_path, self.expected_manifest())

    # ---- the report stage (T109)
    def open_ids(self):
        return sorted((f.id for f in self.findings), key=s2)

    def roadmap_ids(self):
        """The roadmap's rows: every open finding but a group's non-primary members, by D8 (``parse_correlation_groups``, the open IDs)."""
        groups = tachi_parsers.parse_correlation_groups(self.threats_text, self.open_ids())["groups"]
        peers = {m for g in groups for m in g["members"][1:]}
        return [i for i in self.open_ids() if i not in peers]

    def section7_row(self, finding_id):
        """Section 7's row of a finding as ``tachi-stage.py``'s ``_unit_row`` has it (RD-12): the reference set's keys, decoded."""
        f = next(f for f in self.findings if f.id == finding_id)
        return {"finding_id": f.id, "component": tachi_parsers.decode_references(f.component), "threat": tachi_parsers.decode_references(f.threat),
                "risk_level": f.risk, "mitigation": tachi_parsers.decode_references(f.mitigation), "agentic_pattern": "none" if f.pattern == DASH else f.pattern,
                "delta_status": f.status}

    def category_row(self, finding_id):
        """A finding's row of its category table (Section 3 or 4) as the planner's ``_category_rows`` has it (RD-22): decoded, under ``tachi_parts``' item keys and
        without the ID, in the table's order. The two AI tables have ``owasp_reference``, and a STRIDE table has none. ``drop_row_keys`` blanks some, as a table that
        lacks the column gives ``""`` there."""
        f = next(f for f in self.findings if f.id == finding_id)
        cells = collections.OrderedDict([("status", f.status), ("component", f.component), ("maestro_layer", f.layer), ("threat", f.threat)])
        if category_of(f.id) in ("agentic", "llm"):
            cells["owasp_reference"] = OWASP_OF.get(f.id, DASH)
        cells.update([("likelihood", f.likelihood), ("impact", f.impact), ("risk_level", f.risk), ("mitigation", f.mitigation)])
        return {name: ("" if name in self.drop_row_keys else tachi_parsers.decode_references(value)) for name, value in cells.items()}

    def finding_row(self, section, finding_id, **extra):
        """A findings batch's unit row, as ``tachi-stage.py plan --stage report`` writes it (T092): Section 7's row, ``section``, and the category-table row under
        ``category_row`` (RD-22), then what the section adds (``tree``; for a group's primary ``group_id`` and ``members``)."""
        return dict(self.section7_row(finding_id), section=section, category_row=self.category_row(finding_id), **extra)

    def group_primaries(self):
        """``{primary ID: group}`` for the groups of Section 4a, by D8 (``parse_correlation_groups`` with the open IDs)."""
        groups = tachi_parsers.parse_correlation_groups(self.threats_text, self.open_ids())["groups"]
        return {group["members"][0]: group for group in groups}

    def rule_narrated(self):
        """The findings that the contract narrates one by one: every open finding of a run of at most 30, and the Critical and High ones of a larger run."""
        risk = {f.id: f.risk for f in self.findings}
        return [i for i in self.open_ids() if len(self.findings) <= NARRATE_LIMIT or risk[i] in ("Critical", "High")]

    def narrated_ids(self):
        """The findings that this plan's analysis parts narrate: the contract's, less the ones that a ``no-item`` flaw leaves out."""
        return [i for i in self.rule_narrated() if "no-item:" + i not in self.flaws]

    def summary_categories(self):
        """The categories whose ``threat_categories`` units include a ``summary.<key>``, in the template's order: the ones that hold a summarized finding, with the
        flaws applied."""
        narrated = set(self.rule_narrated())
        wanted = [c for c in CATEGORY_ORDER if any(category_of(f.id) == c and f.id not in narrated for f in self.findings) and "no-summary:" + c not in self.flaws]
        return wanted + [c for c in CATEGORY_ORDER if "extra-summary:" + c in self.flaws and c not in wanted]

    def section_plan(self):
        """``[(section, [(key, required)])]`` for the section parts this run plans, in the template's order (part-files.md)."""
        categories = [c for c in CATEGORY_ORDER if any(category_of(f.id) == c for f in self.findings)]
        out = [("exec_summary", [("risk_posture", True), ("top_threats", True), ("key_recommendations", True), ("compliance", False)]),
               ("architecture_overview", [("system_context", True), ("trust_boundaries", True)]),
               ("threat_categories", [("overview", False)] + [("category." + c, True) for c in categories]
                + [("summary." + c, True) for c in self.summary_categories()]),
               ("cross_cutting_themes", [("themes", False)])]
        if self.planned_chains:
            out.append(("attack_chains", [("chain." + chain_id, True) for chain_id, _ in CHAINS]))
        values = sorted({f.pattern for f in self.findings if f.pattern != DASH})
        units = [("pattern." + v, True) for v in values if v != "multiple"] + ([("multi", True)] if "multiple" in values else [])   # `multi`, never `pattern.multiple`
        if "no-multi" in self.flaws:
            units = [unit for unit in units if unit[0] != "multi"]
        if "extra-multi" in self.flaws and "multiple" not in values:
            units.append(("multi", True))
        if "extra-patterns" in self.flaws and not units:
            units = [("pattern.agent_collusion", True)]
        if units and "no-patterns" not in self.flaws:
            out.append(("agentic_patterns", units))
        if (self.has_baseline and "no-delta" not in self.flaws) or (not self.has_baseline and "extra-delta" in self.flaws):
            out.append(("delta_summary", [("progress", True)]))
        return out

    def fragments_of(self, section, units):
        fragments = []
        for key, required in units:
            if section == "cross_cutting_themes":
                for n in range(1, self.themes + 1):
                    fragments.append({"slot_key": "theme.%d.title" % n, "text": "Marker for theme title %s." % digit_free(str(n))})
                    fragments.append({"slot_key": "theme.%d.body" % n, "text": "Marker for theme body %s." % digit_free(str(n))})
            elif required or (key == "compliance" and self.compliance) or (key == "overview" and self.overview):
                fragments.append({"slot_key": key, "text": marker(section, key)})
        return fragments

    def section_batch(self, section):
        """The batch ID of ``section``'s part in the report plan (its first, when the plan holds several)."""
        for batch_id in self.batch_ids("report"):
            if read_json(self.input_path("report", batch_id))["units"][0]["section"] == section:
                return batch_id
        raise AssertionError("the report plan holds no %s part" % section)

    def build_report(self):
        if self.planned_chains:
            self.chains_path.write_text(make_attack_chains_md(CHAINS), encoding="utf-8")
        batches, units_total, number = [], 0, 0
        for section, units in self.section_plan():
            number += 1
            rows = [{"section": section, "key": key} for key, _ in units]
            batches.append(self.write_batch("report", "B%03d" % number, [], rows, [], fragments=self.fragments_of(section, units)))
            units_total += len(rows)

        def chunked(ids):
            size = self.per_report_batch or max(len(ids), 1)
            return [ids[start:start + size] for start in range(0, len(ids), size)]

        for chunk in chunked(self.narrated_ids()):
            number += 1
            items = [{"finding_id": i, "narrative": "Marker narrative for {{finding:%s}}." % i,
                      "tree_summary": ("Marker summary for {{finding:%s}}." % i) if i in self.ch_ids else None} for i in chunk]
            rows = [self.finding_row("threat_analysis", i, tree=(i in self.ch_ids)) for i in chunk]
            batches.append(self.write_batch("report", "B%03d" % number, chunk, rows, items))
            units_total += len(rows)
        roadmap = self.roadmap_ids()
        self.roadmap_items = {i: {"effort": ("Low", "Medium", "High")[n % 3], "dependencies": (None if n % 2 else "Marker dependency for {{finding:%s}}." % i)}
                              for n, i in enumerate(roadmap)}
        primaries = self.group_primaries()
        for chunk in chunked(roadmap):
            number += 1
            items = [dict(finding_id=i, **self.roadmap_items[i]) for i in chunk]
            rows = [self.finding_row("remediation_roadmap", i, **({"group_id": primaries[i]["group_id"], "members": [self.section7_row(m) for m in primaries[i]["members"]]}
                                                                    if i in primaries else {})) for i in chunk]
            batches.append(self.write_batch("report", "B%03d" % number, chunk, rows, items))
            units_total += len(rows)
        inputs = {"threats": plan_input(self.threats_path), "trees_plan": plan_input(self.plan_path("trees")), "tree_manifest": plan_input(self.manifest_path)}
        if self.planned_chains and self.chains_path.exists():
            inputs["attack_chains"] = plan_input(self.chains_path)
        self.write_plan("report", batches, units_total, inputs, None)

    def build(self, mode):
        """Everything ``mode`` needs. Returns ``self``."""
        self.build_trees()
        if mode == "report":
            self.materialize_trees()
            self.build_report()
        return self

    # ---- running the entry, and changing the world between the plan and the run
    def argv(self, mode, plan_id=None, digest=None):
        return [mode, "--run-dir", self.out, "--plan", plan_id or self.ids[mode], "--plan-digest", digest or self.digest[mode]]

    def run(self, module, mode, plan_id=None, digest=None):
        self.last = invoke(module, self.argv(mode, plan_id, digest), self.root)
        return self.last

    def rewrite_plan(self, mode, mutate):
        """Edit the plan document and re-pin it: the digest the command would pass is the new file's, so only D3's content checks refuse it."""
        doc = read_json(self.plan_path(mode))
        mutate(doc)
        self.digest[mode] = write_json(self.plan_path(mode), doc)
        return doc

    def rewrite_json(self, path, mutate):
        doc = read_json(path)
        mutate(doc)
        write_json(path, doc)
        return doc

    def edit_input(self, mode, batch_id, mutate):
        """Edit a batch input and re-pin its digest in the plan, as a planner that had written it so would have."""
        self.rewrite_json(self.input_path(mode, batch_id), mutate)
        digest = tp.file_digest(self.input_path(mode, batch_id))

        def repin(doc):
            for entry in doc["batches"]:
                if entry["batch_id"] == batch_id:
                    entry["input_sha256"] = digest

        self.rewrite_plan(mode, repin)

    def append(self, path, text):
        with open(str(path), "a", encoding="utf-8", newline="") as handle:
            handle.write(text)


def assert_failure(res, mode, plan_id=None):
    """D4's message (RD-2): the banner, a remedy and, when the plan is known, the directory kept for diagnosis."""
    assert re.search(r"(?m)^%s " % re.escape(FAILED_BANNER[mode]), res.err), res.describe()
    assert "Remedy:" in res.err, res.describe()
    if plan_id is not None:  # one ID, or several: a ``report`` run reads two plans, and either directory may be the one it keeps
        ids = [plan_id] if isinstance(plan_id, str) else list(plan_id)
        assert re.search(r"Kept for diagnosis: .*(%s)" % "|".join(re.escape(i) for i in ids), res.err), res.describe()


# S1P-A20's scenario. CG-1's first listed member (R-9) is RESOLVED, so D8's primary is the first member left (T-1). CG-3's first
# member (S-1) is claimed by CG-2, so its primary is LLM-1. CG-4 keeps one open member and emits nothing. The text that S1P-A20
# replaced ("its first member in Section 4a") would name R-9 and S-1.
A20_GROUPS = [("CG-1", ["R-9", "T-1", "T-2"]), ("CG-2", ["S-1", "I-1"]), ("CG-3", ["S-1", "LLM-1", "AG-1"]), ("CG-4", ["E-1", "D-9"])]
A20_EXPECTED = [("CG-1", "T-1", ["T-1", "T-2"]), ("CG-2", "S-1", ["S-1", "I-1"]), ("CG-3", "LLM-1", ["LLM-1", "AG-1"])]
A20_ROADMAP = ["S-1", "T-1", "D-1", "E-1", "LLM-1", "OI-1"]


@pytest.fixture
def make(tmp_path):
    """``make(mode, **options)`` builds one world under ``tmp_path`` and returns it, each in a directory of its own."""
    count = [0]

    def build(mode, **options):
        count[0] += 1
        return World(tmp_path / ("w%d" % count[0]), **options).build(mode)

    return build


# =============================================================================
# 0. The harness: no entry needed. These check the synthetic inputs against the contracts and the shared readers.
# =============================================================================

def test_harness_threats_md_reads_back_as_the_reference_set(tmp_path):
    world = World(tmp_path, rule="rule2")
    world.write_threats()
    rs = tachi_parsers.parse_reference_set(world.threats_text)
    assert sorted((tp.canonical_finding_id(row["id"]) for row in rs["open"]), key=s2) == world.open_ids()
    assert [row["id"] for row in rs["resolved"]] == ["R-9"]
    rows = {row["id"]: row for row in rs["open"]}
    for f in world.findings:
        row = rows[f.id]
        assert (row["component"], row["threat"], row["risk_level"], row["mitigation"], row["delta_status"]) == (
            f.component, f.threat, f.risk, f.mitigation, f.status), f.id
    assert tachi_parsers.parse_baseline_frontmatter(world.threats_text)["source"] == "baseline/threats.md"


def test_harness_a_first_run_has_no_baseline(tmp_path):
    world = World(tmp_path, rule="no-baseline")
    world.write_threats()
    assert tachi_parsers.parse_baseline_frontmatter(world.threats_text)["has_baseline"] is False
    assert {row["delta_status"] for row in tachi_parsers.parse_reference_set(world.threats_text)["open"]} == {"NEW"}


def test_harness_the_reference_digest_covers_sections_7_and_4c_only(tmp_path):
    """RD-9: the populator's block and a rewritten outcome record (Steps 2.5-2.8) leave the digest alone, and a changed Section 7 row moves it."""
    world = World(tmp_path, rule="rule2")
    world.write_threats()
    base = reference_digest(world.threats_text)
    populated = world.threats_text + "\n## Affected Assets\n\n| Finding ID | Affected Assets |\n|---|---|\n| S-1 | Gateway |\n"
    assert reference_digest(populated) == base
    assert reference_digest(world.threats_text.replace(OUTCOME_ZERO, OUTCOME_SKIPPED)) == base
    assert reference_digest(world.threats_text.replace("| High | Encode all model output |", "| Critical | Encode all model output |")) != base


def test_harness_the_a20_scenario_has_the_primaries_d8_gives(tmp_path):
    world = World(tmp_path, rule="rule2", groups=A20_GROUPS)
    world.write_threats()
    parsed = tachi_parsers.parse_correlation_groups(world.threats_text, world.open_ids())
    assert [(g["group_id"], g["primary"], g["members"]) for g in parsed["groups"]] == A20_EXPECTED
    assert world.roadmap_ids() == A20_ROADMAP
    assert [entry["id"] for entry in parsed["repeated"]] == ["S-1"], "S-1 is listed twice: the claim rule, reported elsewhere (S1P-A19)"
    unfiltered = tachi_parsers.parse_correlation_groups(world.threats_text)["groups"]
    assert [g["primary"] for g in unfiltered] == ["R-9", "S-1", "LLM-1", "E-1"], "without the open IDs, CG-1 and CG-4 lead with the first member listed"


@pytest.mark.parametrize("rule,expected", [("no-baseline", 7), ("rule1", 7), ("rule2", 7), ("no-op", 0)])
def test_harness_each_scenario_builds_and_has_the_expected_critical_and_high_findings(make, rule, expected):
    world = make("report", rule=rule)
    assert len(world.ch_ids) == expected
    assert len(list(world.out.glob("attack-trees/*.md"))) == expected
    assert world.manifest_path.is_file() and world.report_path.exists() is False


@pytest.mark.parametrize("mode", MODES)
def test_harness_documents_use_the_closed_key_sets(make, mode):
    world = make("report", rule="rule2", patterns=True, planned_chains=True, outcome=OUTCOME_WRITTEN)
    plan = read_json(world.plan_path(mode))
    assert set(plan) == set(tp.KEY_SETS["plan"][0]) | set(tp.KEY_SETS["plan"][1])
    assert (plan["schema"], plan["stage"], plan["agent_type"]) == (tp.PLAN_SCHEMA, mode, STAGE_AGENT[mode])
    assert read_json(world.pointer_path(mode)) == {"schema": tp.POINTER_SCHEMA, "plan_id": world.plan_id(mode)}
    assert plan["batches"], "this scenario plans batches in both stages"
    for entry in plan["batches"]:
        assert set(entry) == set(tp.KEY_SETS["plan-batch"][0])
        batch_input = read_json(world.input_path(mode, entry["batch_id"]))
        assert set(batch_input) == set(tp.KEY_SETS["batch-input"][0])
        assert batch_input["part_path"] == str(world.part_path(mode, entry["batch_id"]))
        assert (batch_input["stage"], batch_input["agent_type"], batch_input["attempt"]) == (mode, STAGE_AGENT[mode], 1)
        part = read_json(world.part_path(mode, entry["batch_id"]))
        assert set(part) == set(tp.KEY_SETS["part"][0])
        assert (part["plan_id"], part["batch_id"], part["stage"]) == (world.plan_id(mode), entry["batch_id"], mode)
        assert part["finding_ids"] == entry["finding_ids"] == batch_input["finding_ids"]


@pytest.mark.parametrize("mode", MODES)
def test_harness_digests_pin_the_files(make, mode):
    world = make("report", rule="rule2")
    plan = read_json(world.plan_path(mode))
    assert world.digest[mode] == tp.file_digest(world.plan_path(mode))
    for entry in plan["batches"]:
        assert entry["input_sha256"] == tp.file_digest(world.input_path(mode, entry["batch_id"])) and entry["state"] == "done"
    for name, entry in plan["inputs"].items():
        assert (entry["sha256"], entry["bytes"]) == (tp.file_digest(entry["path"]), Path(entry["path"]).stat().st_size), name
    assert plan["params"]["reference_digest"] == reference_digest(world.threats_text)
    if mode == "report":
        assert plan["inputs"]["trees_plan"]["sha256"] == world.digest["trees"] and plan["params"]["trees_plan_id"] == world.plan_id("trees")
        assert plan["batch_size"] is None and plan["unit_count"] == sum(len(read_json(world.input_path(mode, b))["units"]) for b in world.batch_ids(mode))


def test_harness_every_tree_file_holds_one_mermaid_block_and_an_inner_run_is_out_fenced(make):
    world = make("trees", rule="rule2", ticks_for={"S-1": 3, "T-1": 5})
    paths = sorted(world.plan_dir("trees").glob("trees/*.md")) + sorted(world.baseline.glob("attack-trees/*.md"))
    assert len(paths) == 7 + 2
    for path in paths:
        text = path.read_text(encoding="utf-8")
        blocks = [b for b in fenced_blocks(text) if b["info"] == "mermaid"]
        assert len(blocks) == 1 and blocks[0]["closed"], path.name
        assert blocks[0]["fence"] > longest_run(blocks[0]["source"]), path.name
    text = world.source_tree_path("T-1").read_text(encoding="utf-8")
    block = fenced_blocks(text)[0]
    assert (longest_run(block["source"]), block["fence"]) == (5, 6)
    assert "Café" in text and "\t" in text and "   \n" in text, "byte-exactness probes: non-ASCII, a tab and trailing spaces"
    assert "\r" not in text


def test_harness_the_fence_reader_follows_commonmark():
    text = "intro\n````mermaid\ngraph TD\nA[\"```\"]\n````\n\n```text\nx\n```\n~~~\ntilde\n~~~\n```mermaid\nnever closed\n"
    assert [(b["info"], b["fence"], b["source"], b["closed"]) for b in fenced_blocks(text)] == [
        ("mermaid", 4, 'graph TD\nA["```"]', True), ("text", 3, "x", True), ("", 3, "tilde", True), ("mermaid", 3, "never closed\n", False)]
    assert mermaid_sources("```mermaid\na\n```\n```text\nb\n```\n") == ["a"]
    assert [(n, t) for n, t in numbered_sections("## 1. One\n```\n## 2. Fenced\n```\n## 3. Three\n### 3.1 Sub\n")] == [(1, "One"), (3, "Three")]


def test_harness_the_expected_manifest_is_in_the_contracts_order_and_shape(make):
    manifest = make("trees", rule="rule2").expected_manifest()
    assert list(manifest) == ["schema_version", "rule_applied", "attack_tree_count", "trees", "summary"]
    assert [e["finding_id"] for e in manifest["trees"]] == ["S-1", "T-1", "LLM-1", "T-2", "I-1", "AG-1", "OI-1"]
    assert (manifest["attack_tree_count"], manifest["rule_applied"]) == (7, "Rule 2")
    assert manifest["summary"] == {"fresh": 5, "carried_forward": 1, "regenerated": 1}
    by_id = {e["finding_id"]: e for e in manifest["trees"]}
    assert "similarity_score" not in by_id["S-1"] and by_id["T-2"]["similarity_score"] == 0.93 and by_id["OI-1"]["action"] == "regenerated"
    assert by_id["T-2"]["file_path"] == "attack-trees/t-2-attack-tree.md" and by_id["T-1"]["delta_status"] == "UPDATED"
    rule1 = make("trees", rule="rule1").expected_manifest()
    assert (rule1["rule_applied"], rule1["summary"]) == ("Rule 1", {"fresh": 1, "carried_forward": 6, "regenerated": 0})
    assert make("trees", rule="no-op").expected_manifest() == {
        "schema_version": "1.0", "rule_applied": "no-op", "attack_tree_count": 0, "trees": [], "summary": {"fresh": 0, "carried_forward": 0, "regenerated": 0}}


def test_harness_a_plan_with_no_units_keeps_its_refs(make):
    """Every Critical and High finding is carried, so the plan has no batch (the case that put ``refs`` in the plan, ruled at W2)."""
    world = make("trees", rule="rule1", no_baseline_tree=())
    plan = read_json(world.plan_path("trees"))
    assert (plan["batches"], plan["unit_count"], plan["batch_size"]) == ([], 0, None)
    assert plan["refs"] == {"baseline_dir": str(world.baseline)} and plan["params"]["rule_applied"] == "Rule 1"
    assert len(list(world.baseline.glob("attack-trees/*.md"))) == 7


@pytest.mark.parametrize("name,char", FORBIDDEN_SAMPLES)
def test_harness_each_forbidden_sample_is_one_the_predicate_returns(name, char):
    assert tp.forbidden_character("a" + char + "b") == char


@pytest.mark.parametrize("name,char", ALLOWED_SAMPLES)
def test_harness_each_allowed_sample_passes_the_predicate(name, char):
    assert tp.forbidden_character("a" + char + "b") is None


def test_harness_the_template_has_the_nine_sections_the_numbering_tests_start_from():
    titles = template_titles()
    assert sorted(titles) == list(range(1, 10))
    assert (titles[1], titles[5], titles[7]) == ("Executive Summary", "Attack Trees", "Remediation Roadmap")


@pytest.mark.parametrize("mode", MODES)
def test_harness_documents_pass_the_shared_validators_once_the_stages_exist(make, mode):
    if mode not in tp.STAGE_AGENTS:
        pytest.skip("T091's first slice adds the stage %s to tachi_parts.STAGE_AGENTS; until then its validators refuse it" % mode)
    world = make("report", rule="rule2")
    tp.validate_plan(read_json(world.plan_path(mode)))
    tp.validate_pointer(read_json(world.pointer_path(mode)))
    for batch_id in world.batch_ids(mode):
        tp.validate_batch_input(read_json(world.input_path(mode, batch_id)))


def run_refused(world, assembler, mode, code, known_plan=True, **kwargs):
    """Run ``mode`` and require exit ``code``, D4's message and an untouched run directory (RD-7: a refused run writes nothing)."""
    before = tree_state(world.out)
    res = world.run(assembler, mode, **kwargs)
    assert res.code in (code if isinstance(code, tuple) else (code,)), res.describe()
    kept = [world.plan_id(mode)] + ([world.plan_id("trees")] if mode == "report" else [])
    assert_failure(res, mode, kept if known_plan else None)
    assert tree_state(world.out) == before, "a refused run changes no file under --run-dir:\n" + res.describe()
    return res


def repin_trees_plan(world):
    """The report plan pins the trees plan's file, so a test that edits that plan re-pins it: the digest check then passes, and only the check under test refuses."""
    size = world.plan_path("trees").stat().st_size
    world.rewrite_plan("report", lambda doc: doc["inputs"]["trees_plan"].update(sha256=world.digest["trees"], bytes=size))


# =============================================================================
# 1. The entry: arguments and the exit table (cli.md, RD-1, RD-2)
# =============================================================================

def test_cli_help_and_version_are_supported(assembler, tmp_path):
    helped = invoke(assembler, ["--help"], tmp_path)
    assert helped.code == 0, helped.describe()
    for word in ("trees", "report", "--run-dir", "--plan", "--plan-digest"):
        assert word in helped.out, "%s is in the usage text: %s" % (word, helped.out)
    versioned = invoke(assembler, ["--version"], tmp_path)
    assert versioned.code == 0, versioned.describe()
    assert tp.VERSION in versioned.out + versioned.err  # reading: cli.md says tests may accept either stream
    assert "%d.%d" % sys.version_info[:2] in versioned.out + versioned.err, "the interpreter's version too"


USAGE_CASES = {
    "no mode": lambda out: [],
    "unknown mode": lambda out: ["publish", "--run-dir", out, "--plan", TREES_ID, "--plan-digest", "0" * 64],
    "no run dir": lambda out: ["trees", "--plan", TREES_ID, "--plan-digest", "0" * 64],
    "no plan": lambda out: ["trees", "--run-dir", out, "--plan-digest", "0" * 64],
    "trees without a digest": lambda out: ["trees", "--run-dir", out, "--plan", TREES_ID],
    "report without a digest": lambda out: ["report", "--run-dir", out, "--plan", REPORT_ID],
}


@pytest.mark.parametrize("case", sorted(USAGE_CASES))
def test_cli_a_usage_error_exits_2_and_writes_nothing(assembler, tmp_path, case):
    (tmp_path / "run").mkdir()
    res = invoke(assembler, USAGE_CASES[case](tmp_path / "run"), tmp_path)
    assert res.code == 2, res.describe()
    assert tree_state(tmp_path) == {}


@pytest.mark.parametrize("mode", MODES)
def test_cli_a_run_directory_with_no_plan_is_a_missing_input(assembler, tmp_path, mode):
    run = tmp_path / "run"
    run.mkdir()
    res = invoke(assembler, [mode, "--run-dir", run, "--plan", TREES_ID if mode == "trees" else REPORT_ID, "--plan-digest", "0" * 64], tmp_path)
    assert res.code == 1, res.describe()
    assert_failure(res, mode)
    assert tree_state(run) == {}


@pytest.mark.parametrize("what", ["nothing at that path", "a regular file"])
@pytest.mark.parametrize("mode", MODES)
def test_cli_a_run_dir_that_is_not_a_directory_is_exit_1_in_the_shared_words_and_comes_before_the_plan_checks(assembler, tmp_path, mode, what):
    """S1P-A42: the directory option is the first check of every entry, so a bad ``--plan`` and a bad digest beside it are never reached."""
    target = tmp_path / "run"
    if what == "a regular file":
        target.write_text("not a directory", encoding="utf-8")
    before = tree_state(tmp_path)
    res = invoke(assembler, [mode, "--run-dir", target, "--plan", "not-a-plan", "--plan-digest", "not-a-digest"], tmp_path)
    assert res.code == 1, res.describe()
    assert_failure(res, mode)
    assert "--run-dir is not a directory" in res.err and "Remedy: create it or correct --run-dir" in res.err, res.describe()
    assert tree_state(tmp_path) == before
    assert target.exists() is (what == "a regular file"), "nothing is created at the path"


@pytest.mark.parametrize("mode", MODES)
def test_cli_the_plan_checks_follow_the_directory_check_each_in_the_contracts_words_and_exit_2(assembler, tmp_path, mode):
    run = tmp_path / "run"
    run.mkdir()
    plan_id = {"trees": TREES_ID, "report": REPORT_ID}[mode]
    bad_plan = invoke(assembler, [mode, "--run-dir", run, "--plan", plan_id.upper(), "--plan-digest", "0" * 64], tmp_path)
    assert bad_plan.code == 2, bad_plan.describe()
    assert_failure(bad_plan, mode)
    assert "--plan is not a plan ID" in bad_plan.err and "Remedy: pass the plan ID that plan printed" in bad_plan.err, bad_plan.describe()
    bad_digest = invoke(assembler, [mode, "--run-dir", run, "--plan", plan_id, "--plan-digest", "G" * 64], tmp_path)
    assert bad_digest.code == 2, bad_digest.describe()
    assert_failure(bad_digest, mode)
    assert "--plan-digest is not a SHA-256 in lowercase hex" in bad_digest.err, bad_digest.describe()
    assert "Remedy: pass the digest that the last plan or reconcile printed" in bad_digest.err, bad_digest.describe()
    assert tree_state(run) == {}


# =============================================================================
# 2. RR3: both modes check their plan before they read a part (ADR-050 D6; part-files.md, "The assembler's checks")
# =============================================================================

@pytest.mark.parametrize("mode", MODES)
def test_guard_a_plan_digest_that_differs_exits_2_and_writes_nothing(assembler, make, mode):
    world = make("report")
    run_refused(world, assembler, mode, 2, digest="0" * 64)


@pytest.mark.parametrize("digest", ["not-a-digest", "A" * 64, "0" * 63])
def test_guard_a_digest_that_is_not_64_lowercase_hex_exits_2(assembler, make, digest):
    world = make("trees")
    before = tree_state(world.out)
    res = world.run(assembler, "trees", digest=digest)  # argparse may refuse it as a usage error, so only the code and the untouched directory are pinned
    assert res.code == 2, res.describe()
    assert tree_state(world.out) == before


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_plan_that_current_json_does_not_name_exits_2(assembler, make, mode):
    world = make("report")
    write_json(world.pointer_path(mode), {"schema": tp.POINTER_SCHEMA, "plan_id": OTHER_ID})  # a newer plan replaced the pointer
    res = run_refused(world, assembler, mode, 2)
    assert OTHER_ID in res.err, "the message names the plan that current.json holds: " + res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_plan_file_that_names_another_plan_exits_2(assembler, make, mode):
    world = make("report")
    world.rewrite_plan(mode, lambda doc: doc.update(plan_id=OTHER_ID))  # re-pinned, so only the content check refuses it
    run_refused(world, assembler, mode, 2)


@pytest.mark.parametrize("state", ["pending", "failed"])
@pytest.mark.parametrize("mode", MODES)
def test_guard_a_batch_that_is_not_done_exits_2_and_the_script_never_returns_3(assembler, make, mode, state):
    world = make("report")
    world.rewrite_plan(mode, lambda doc: doc["batches"][0].update(state=state))
    res = run_refused(world, assembler, mode, 2)
    assert "B001" in res.err, "the message names the batch: " + res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_batch_input_edited_after_the_plan_exits_2(assembler, make, mode):
    world = make("report")
    path = world.input_path(mode, "B001")
    path.write_bytes(path.read_bytes() + b"\n")
    run_refused(world, assembler, mode, 2)


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_batch_input_that_became_a_link_exits_2(assembler, make, mode):
    world = make("report")
    path = world.input_path(mode, "B001")
    real = world.root / "elsewhere.json"
    real.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(real)
    run_refused(world, assembler, mode, 2)


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_part_that_is_missing_exits_1(assembler, make, mode):
    world = make("report")
    world.part_path(mode, "B001").unlink()
    res = run_refused(world, assembler, mode, 1)
    assert "B001" in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_part_of_another_plan_exits_2(assembler, make, mode):
    world = make("report")
    world.rewrite_json(world.part_path(mode, "B001"), lambda doc: doc.update(plan_id=OTHER_ID))
    run_refused(world, assembler, mode, 2)


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_part_of_an_earlier_attempt_never_counts(assembler, make, mode):
    """Only the plan's current attempt counts: the plan says attempt 2 and the part on disk is attempt 1's."""
    world = make("report")

    def second(doc):
        doc["batches"][0]["attempt"] = 2

    world.rewrite_plan(mode, second)
    run_refused(world, assembler, mode, (1, 2))  # reading: no part (1), or a plan and batch input that disagree on the attempt (2); never a pass


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_part_that_is_not_json_exits_2(assembler, make, mode):
    world = make("report")
    world.part_path(mode, "B001").write_bytes(b"{this is not json")
    run_refused(world, assembler, mode, 2)


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_reference_set_that_changed_since_the_plan_exits_2(assembler, make, mode):
    """A Section 7 row that changed is a different run: the plan's ``params.reference_digest`` (RD-9) no longer matches."""
    world = make("report")
    text = world.threats_path.read_text(encoding="utf-8")
    assert "| Medium | Rate limit each client |" in text
    world.threats_path.write_text(text.replace("| Medium | Rate limit each client |", "| High | Rate limit each client |"), encoding="utf-8")
    run_refused(world, assembler, mode, 2)


@pytest.mark.parametrize("what", ["the plan pointer", "plan.json"])
@pytest.mark.parametrize("mode", MODES)
def test_guard_a_plan_pointer_or_plan_file_that_is_gone_is_a_missing_input_exit_1(assembler, make, mode, what):
    world = make("report")
    {"the plan pointer": world.pointer_path, "plan.json": world.plan_path}[what](mode).unlink()
    res = run_refused(world, assembler, mode, 1, known_plan=(what == "plan.json"))
    assert ("%s is missing" % what) in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_plan_file_that_is_a_link_exits_2_naming_the_path_guard(assembler, make, mode):
    world = make("report")
    path = world.plan_path(mode)
    real = world.root / "elsewhere-plan.json"
    real.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(real)
    res = run_refused(world, assembler, mode, 2)
    assert "path guard" in res.err and "symlink" in res.err, res.describe()


@pytest.mark.parametrize("what", ["the plan pointer", "plan.json"])
def test_report_a_pinned_trees_plan_that_is_gone_fails_as_a_report_failure(assembler, make, what):
    """The report plan pins the trees plan's file as an input, so a file that vanished is the guard's "changed (or vanished)"; a pointer that did is a missing input."""
    world = make("report")
    {"the plan pointer": world.pointer_path, "plan.json": world.plan_path}[what]("trees").unlink()
    res = run_refused(world, assembler, "report", 1 if what == "the plan pointer" else 2, known_plan=False)
    assert ("the plan pointer is missing" if what == "the plan pointer" else "trees_plan changed (or vanished) since plan") in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_batch_input_whose_finding_ids_are_not_the_plans_exits_2(assembler, make, mode):
    """The input is edited and re-pinned, so it passes its own contract and the digest, and only the comparison with the plan's entry refuses it."""
    world = make("report")
    batch = world.batch_ids(mode)[0 if mode == "trees" else -2]   # a batch of findings: the first trees batch, and the threat_analysis batch of the report
    world.edit_input(mode, batch, lambda doc: doc.update(finding_ids=list(reversed(doc["finding_ids"]))))
    res = run_refused(world, assembler, mode, 2)
    assert "is for another batch" in res.err and batch in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_threats_md_that_is_not_strict_utf_8_exits_2(assembler, make, mode):
    world = make("report")
    world.threats_path.write_bytes(world.threats_path.read_bytes() + b"\xff\xfe\n")
    if mode == "trees":   # the trees plan pins the file's bytes, so the plan has to be re-pinned for the check on its content to be the one that refuses it
        world.rewrite_plan("trees", lambda doc: doc["inputs"].update(threats=plan_input(world.threats_path)))
    res = run_refused(world, assembler, mode, 2)
    assert "threats.md is not strict UTF-8" in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_threats_md_without_section_7_exits_2_with_the_readers_words(assembler, make, mode):
    world = make("report")
    text = world.threats_path.read_text(encoding="utf-8")
    assert "## 7. Recommended Actions" in text
    world.threats_path.write_text(text.replace("## 7. Recommended Actions", "## 7. Something else"), encoding="utf-8")
    if mode == "trees":
        world.rewrite_plan("trees", lambda doc: doc["inputs"].update(threats=plan_input(world.threats_path)))
    res = run_refused(world, assembler, mode, 2)
    assert "threats.md" in res.err and "Section 7" in res.err and "is missing" in res.err and "Remedy:" in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_threats_md_that_is_gone_is_exit_2_where_the_plan_pins_it_and_exit_1_where_it_does_not(assembler, make, mode):
    """RD-19. ``trees`` pins the file's bytes, so a file that vanished is the guard's "changed (or vanished)". ``report`` reads it when it needs it (RR3)."""
    world = make("report")
    world.threats_path.unlink()
    res = run_refused(world, assembler, mode, {"trees": 2, "report": 1}[mode])
    assert "threats" in res.err, res.describe()
    assert ("since plan" in res.err) is (mode == "trees"), res.describe()


def test_report_threats_md_over_the_size_cap_exits_2(assembler, make):
    world = make("report")
    with open(str(world.threats_path), "ab") as handle:
        handle.write(b"#" * (tp.MAX_AGENT_INPUT_BYTES + 1))
    res = run_refused(world, assembler, "report", 2)
    assert "threats.md is over the size cap" in res.err, res.describe()


@pytest.mark.parametrize("mode", MODES)
def test_guard_a_trees_plan_with_no_valid_rule_exits_2(assembler, make, mode):
    world = make("report")
    world.rewrite_plan("trees", lambda doc: doc["params"].update(rule_applied="Rule 9"))
    if mode == "report":
        repin_trees_plan(world)
    res = run_refused(world, assembler, mode, 2)
    assert "params.rule_applied" in res.err, res.describe()


def test_trees_a_plan_with_no_threats_input_exits_2(assembler, make):
    world = make("trees")
    world.rewrite_plan("trees", lambda doc: doc["inputs"].pop("threats"))
    res = run_refused(world, assembler, "trees", 2)
    assert "no threats input" in res.err, res.describe()


@pytest.mark.parametrize("what", ["pins no trees plan", "pins no manifest"])
def test_report_a_plan_that_does_not_pin_the_trees_plan_and_the_manifest_exits_2(assembler, make, what):
    world = make("report")
    world.rewrite_plan("report", lambda doc: doc["inputs"].pop("trees_plan" if what == "pins no trees plan" else "tree_manifest"))
    res = run_refused(world, assembler, "report", 2)
    assert "doesn't pin a trees plan and a tree manifest" in res.err, res.describe()


@pytest.mark.parametrize("name", ["trees_plan", "tree_manifest", "threats"])
def test_report_a_plan_input_that_is_not_the_file_the_run_directory_holds_exits_2(assembler, make, name):
    """A pinned input is read where the plan says, so a plan that points one at a copy elsewhere is refused even when the copy has the same bytes."""
    world = make("report")
    own = Path(read_json(world.plan_path("report"))["inputs"][name]["path"])
    other = world.root / ("copy-of-" + own.name.lstrip("."))
    other.write_bytes(own.read_bytes())
    world.rewrite_plan("report", lambda doc: doc["inputs"][name].update(path=str(other)))
    res = run_refused(world, assembler, "report", 2)
    assert ("%s input is not" % name) in res.err, res.describe()


@pytest.mark.parametrize("section", ["exec_summary", "cross_cutting_themes"])
def test_report_a_plan_with_no_part_for_a_required_section_exits_2(assembler, make, section):
    world = make("report")
    index = next(n for n, section_plan in enumerate(world.section_plan()) if section_plan[0] == section)
    world.rewrite_plan("report", lambda doc: doc["batches"].pop(index))
    res = run_refused(world, assembler, "report", 2)
    assert ("holds no %s part" % section) in res.err, res.describe()


# =============================================================================
# 3. assemble-report.py trees (T108; ADR-050 D14; FR-K5.3, FR-K5.6, and FR-K5.5 applied early)
# =============================================================================

def trees_ok(world, assembler):
    res = world.run(assembler, "trees")
    assert res.code == 0, res.describe()
    return res


def test_trees_copies_every_generated_tree_byte_for_byte_from_its_batch_input_path(assembler, make):
    world = make("trees")
    trees_ok(world, assembler)
    for finding_id in world.ch_ids:
        assert world.tree_path(finding_id).read_bytes() == world.fresh[finding_id], finding_id
        assert world.source_tree_path(finding_id).read_bytes() == world.fresh[finding_id], "a copy, so the agent's file stays where it is"
    assert sorted(p.name for p in (world.out / "attack-trees").iterdir()) == sorted([".manifest.json"] + [tree_name(i) for i in world.ch_ids])


def test_trees_copies_every_carried_tree_from_the_baseline_byte_for_byte(assembler, make):
    world = make("trees", rule="rule1")
    baseline_before = tree_state(world.baseline)
    trees_ok(world, assembler)
    assert world.baseline_tree_ids == [i for i in world.ch_ids if i != "I-1"]
    for finding_id in world.baseline_tree_ids:
        assert world.tree_path(finding_id).read_bytes() == world.base_bytes[finding_id], finding_id
    assert world.tree_path("I-1").read_bytes() == world.fresh["I-1"], "no baseline file for it, so the planner generated it (Rule 1's isolated fallback)"
    assert tree_state(world.baseline) == baseline_before, "the baseline is read, never written"


def test_trees_with_every_tree_carried_the_plan_has_no_batch_and_the_copy_still_happens(assembler, make):
    """RD-5: the plan keeps its ``refs``, so the assembler still finds the baseline when no batch was ever planned."""
    world = make("trees", rule="rule1", no_baseline_tree=())
    assert world.batch_ids("trees") == []
    trees_ok(world, assembler)
    for finding_id in world.ch_ids:
        assert world.tree_path(finding_id).read_bytes() == world.base_bytes[finding_id], finding_id
    assert read_json(world.manifest_path) == world.expected_manifest()
    record = world.record("trees")
    assert record["counts"] == {"units": 0, "carried": 7, "rendered": 7}
    assert record["batches"] == {"planned": 0, "dispatched": 0, "done": 0, "retried": 0, "split": 0, "exhausted": 0}


def test_trees_rule_3_copies_the_baseline_tree_that_the_part_decided_to_carry(assembler, make):
    """RD-6: T-2's part says ``carried_forward`` with a score, so the baseline's bytes are the ones copied. OI-1's says ``regenerated``."""
    world = make("trees", rule="rule2")
    assert world.fresh["T-2"] != world.base_bytes["T-2"], "premise: the agent's fresh tree and the baseline's differ"
    trees_ok(world, assembler)
    assert world.tree_path("T-2").read_bytes() == world.base_bytes["T-2"]
    assert world.tree_path("OI-1").read_bytes() == world.fresh["OI-1"]
    entries = {e["finding_id"]: e for e in read_json(world.manifest_path)["trees"]}
    assert (entries["T-2"]["action"], entries["T-2"]["similarity_score"]) == ("carried_forward", 0.93)
    assert (entries["OI-1"]["action"], entries["OI-1"]["similarity_score"]) == ("regenerated", 0.41)
    assert all("similarity_score" not in entries[i] for i in ("S-1", "T-1", "LLM-1", "I-1", "AG-1")), "omitted, not null, outside Rule 3"


@pytest.mark.parametrize("rule", ["no-baseline", "rule1", "rule2"])
def test_trees_the_merged_manifest_is_the_schema_1_0_merge_of_the_batch_manifests(assembler, make, rule):
    world = make("trees", rule=rule)
    trees_ok(world, assembler)
    manifest = read_json(world.manifest_path)
    assert manifest == world.expected_manifest()
    assert manifest["schema_version"] == "1.0" and set(manifest) == {"schema_version", "rule_applied", "attack_tree_count", "trees", "summary"}
    on_disk = [p for p in (world.out / "attack-trees").iterdir() if p.suffix == ".md"]
    assert len(manifest["trees"]) == manifest["attack_tree_count"] == len(on_disk) == sum(manifest["summary"].values())


def test_trees_the_manifest_merges_every_batch_with_critical_findings_before_high_ones(assembler, make):
    world = make("trees", per_batch=2)
    assert len(world.batch_ids("trees")) == 4
    trees_ok(world, assembler)
    assert [e["finding_id"] for e in read_json(world.manifest_path)["trees"]] == ["S-1", "T-1", "LLM-1", "T-2", "I-1", "AG-1", "OI-1"]


def test_trees_a_run_with_no_critical_or_high_finding_writes_an_empty_manifest(assembler, make):
    world = make("trees", rule="no-op")
    trees_ok(world, assembler)
    assert read_json(world.manifest_path) == world.expected_manifest()
    assert [p for p in (world.out / "attack-trees").iterdir() if p.suffix == ".md"] == []
    assert world.record("trees")["counts"] == {"units": 0, "carried": 0, "rendered": 0}


def test_trees_the_stage_record_is_the_closed_one_for_the_stage(assembler, make):
    world = make("trees", rule="rule1")
    trees_ok(world, assembler)
    record = world.record("trees")
    assert set(record) == set(tp.KEY_SETS["stage-record"][0])
    assert (record["schema"], record["stage"], record["plan_id"]) == (tp.STAGE_RECORD_SCHEMA, "trees", world.plan_id("trees"))
    assert (record["status"], record["error"], record["tachi_version"]) == ("success", None, tp.VERSION)
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", record["input_digest"]) and record["started_utc"] <= record["finished_utc"]
    assert record["counts"] == {"units": 1, "carried": 6, "rendered": 7}
    assert record["batches"] == {"planned": 1, "dispatched": 1, "done": 1, "retried": 0, "split": 0, "exhausted": 0}
    assert (record["overflow_events"], record["retries"], record["warnings"], record["undeclared_paths"]) == ([], [], [], [])
    assert {"path": "attack-trees/.manifest.json", "sha256": tp.file_digest(world.manifest_path)} in record["outputs"]  # reading: RD-13
    assert tp.file_digest(world.plan_path("trees")) == world.digest["trees"], "the assembler never rewrites plan.json"
    if "trees" in tp.STAGE_AGENTS:
        tp.validate_stage_record(record)


def test_trees_a_first_run_counts_every_tree_as_generated(assembler, make):
    world = make("trees")
    trees_ok(world, assembler)
    assert world.record("trees")["counts"] == {"units": 7, "carried": 0, "rendered": 7}


def test_trees_writes_only_the_trees_the_manifest_and_its_stage_record(assembler, make):
    world = make("trees", rule="rule2")
    before = tree_state(world.out)
    trees_ok(world, assembler)
    after = tree_state(world.out)
    assert all(after.get(path) == digest for path, digest in before.items()), "no earlier file is changed or removed"
    plan_prefix = ".tachi-build/trees/%s/" % world.plan_id("trees")
    outside_the_plan = {path for path in after if path not in before and not path.startswith(plan_prefix)}
    assert outside_the_plan == {"attack-trees/.manifest.json"} | {"attack-trees/" + tree_name(i) for i in world.ch_ids}
    assert (world.out / plan_prefix / "stage-record.json").is_file()


def test_trees_two_runs_over_the_same_input_give_the_same_bytes(assembler, make):
    """NFR-2: the plan ID, which differs, is in no output."""
    first, second = make("trees", rule="rule2"), make("trees", rule="rule2", trees_id=OTHER_ID)
    trees_ok(first, assembler)
    trees_ok(second, assembler)
    assert tree_state(first.out / "attack-trees") == tree_state(second.out / "attack-trees")


def test_trees_a_refused_run_leaves_the_world_as_it_was_so_the_repaired_input_then_passes(assembler, make):
    world = make("trees")
    path = world.source_tree_path("LLM-1")
    data = path.read_bytes()
    path.unlink()
    run_refused(world, assembler, "trees", 4)
    path.write_bytes(data)
    trees_ok(world, assembler)
    assert read_json(world.manifest_path) == world.expected_manifest()


def halve_first_batch(world, mode="trees"):
    """Rewrite B001 as ``reconcile`` leaves a batch it halved: the parent is ``split`` with no part, and two children, one attempt on,
    each hold half its units, with the retry budget spent (ADR-050 D6; part-files.md, "Readings ruled at W1")."""
    parent = read_json(world.plan_path(mode))["batches"][0]
    ids = parent["finding_ids"]
    half = max(1, len(ids) // 2)
    batch_input, part = read_json(world.input_path(mode, "B001")), read_json(world.part_path(mode, "B001"))
    children = []
    for batch_id, chunk in (("B001-1", ids[:half]), ("B001-2", ids[half:])):
        child = dict(batch_input, batch_id=batch_id, finding_ids=chunk, attempt=2, part_path=str(world.part_path(mode, batch_id, 2)),
                     tree_paths={i: batch_input["tree_paths"][i] for i in chunk}, units=[u for u in batch_input["units"] if u["finding_id"] in chunk])
        digest = write_json(world.input_path(mode, batch_id), child)
        write_json(world.part_path(mode, batch_id, 2), dict(part, batch_id=batch_id, finding_ids=chunk, items=[i for i in part["items"] if i["finding_id"] in chunk]))
        children.append({"batch_id": batch_id, "parent": "B001", "attempt": 2, "finding_ids": chunk, "input_sha256": digest, "state": "done"})
    world.part_path(mode, "B001").unlink()

    def edit(doc):
        doc["batches"][0]["state"] = "split"
        doc["batches"][1:1] = children
        doc["retry_budget"]["used"] = 2

    world.rewrite_plan(mode, edit)


def test_trees_a_halved_batch_is_read_through_its_children_and_counted_in_the_record(assembler, make):
    world = make("trees")
    halve_first_batch(world)
    trees_ok(world, assembler)
    assert read_json(world.manifest_path) == world.expected_manifest()
    assert world.record("trees")["batches"] == {"planned": 2, "dispatched": 4, "done": 3, "retried": 2, "split": 1, "exhausted": 0}


# ---- the per-file checks (D14: one Mermaid block, a size cap, the forbidden-character predicate, the ID before it becomes a path)

def broken_tree_text(variant, finding_id):
    good = tree_file(finding_id, tree_source(finding_id, "broken"), label="broken")
    return {
        "no block": "# Attack Tree: %s\n\nNo diagram was written.\n" % finding_id,
        "two blocks": good + "\n" + good,
        "not mermaid": good.replace("```mermaid", "```text"),
        "unclosed": good[:good.rindex("```")],  # reading: a fence that never closes is not a Mermaid block
        # S1P-A70: a block with no line between its fences holds no diagram, whatever copy of ``attack_tree_source`` is loaded (the parser names it
        # ``empty-block``, and until that copy lands the script fails a source of ``""`` itself).
        "empty block": "# Attack Tree: %s\n\n```mermaid\n```\n" % finding_id,
    }[variant]


def tree_to_break(world, where):
    """``(finding, path)`` of a tree that the assembler reads: a carried one (S-1, from the baseline) or a generated one (I-1)."""
    return ("S-1", world.baseline_tree_path("S-1")) if where == "carried" else ("I-1", world.source_tree_path("I-1"))


@pytest.mark.parametrize("variant", ["no block", "two blocks", "not mermaid", "unclosed", "empty block"])
@pytest.mark.parametrize("where", ["carried", "generated"])
def test_trees_a_tree_file_without_exactly_one_mermaid_block_exits_2_naming_the_finding(assembler, make, where, variant):
    world = make("trees", rule="rule1")
    finding_id, path = tree_to_break(world, where)
    path.write_bytes(broken_tree_text(variant, finding_id).encode("utf-8"))
    res = run_refused(world, assembler, "trees", 2)
    assert finding_id in res.err, res.describe()


def test_trees_a_mermaid_block_with_an_inner_backtick_run_is_still_one_block(assembler, make):
    world = make("trees", rule="rule1", ticks_for={"I-1": 3, "S-1": 5})
    trees_ok(world, assembler)
    assert world.tree_path("I-1").read_bytes() == world.fresh["I-1"] and world.tree_path("S-1").read_bytes() == world.base_bytes["S-1"]
    assert len(mermaid_sources(world.tree_path("S-1").read_text(encoding="utf-8"))) == 1


@pytest.mark.parametrize("where", ["carried", "generated"])
def test_trees_a_tree_over_the_size_cap_exits_2(assembler, make, where):
    world = make("trees", rule="rule1")
    finding_id, path = tree_to_break(world, where)
    path.write_bytes(tree_file(finding_id, tree_source(finding_id, "big") + "\n    %% " + "p" * tp.MAX_AGENT_INPUT_BYTES, label="big").encode("utf-8"))
    assert path.stat().st_size > tp.MAX_AGENT_INPUT_BYTES
    res = run_refused(world, assembler, "trees", 2)
    assert finding_id in res.err, res.describe()


@pytest.mark.parametrize("where", ["plan", "batch input", "part"])
def test_trees_a_finding_id_outside_the_allow_list_never_becomes_a_path(assembler, make, where):
    world = make("trees")
    bad = "../escape-1"
    if where == "plan":
        world.rewrite_plan("trees", lambda doc: doc["batches"][0]["finding_ids"].__setitem__(0, bad))
    elif where == "batch input":
        def edit(doc):
            doc["finding_ids"][0] = bad
            doc["units"][0]["finding_id"] = bad
            doc["tree_paths"][bad] = doc["tree_paths"].pop("S-1")

        world.edit_input("trees", "B001", edit)
    else:
        world.rewrite_json(world.part_path("trees", "B001"), lambda doc: doc["items"][0].update(finding_id=bad))
    run_refused(world, assembler, "trees", 2)
    assert not list(world.root.rglob("*escape*")), "nothing was created from the bad ID"


@pytest.mark.parametrize("how", ["inside the run but outside the plan's trees directory", "outside the run", "a link"])
def test_trees_a_tree_path_that_leaves_the_plans_trees_directory_or_runs_through_a_link_exits_2(assembler, make, how):
    world = make("trees")
    source = world.source_tree_path("S-1")
    if how == "a link":
        real = world.root / "elsewhere.md"
        real.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(real)
    else:
        decoy = (world.out / "decoy-attack-tree.md") if how.startswith("inside") else (world.root / "decoy-attack-tree.md")
        decoy.write_bytes(source.read_bytes())
        world.edit_input("trees", "B001", lambda doc: doc["tree_paths"].update({"S-1": str(decoy)}))
    res = run_refused(world, assembler, "trees", 2)
    assert "S-1" in res.err, res.describe()


@pytest.mark.parametrize("how", ["another finding's file in the plan's trees directory", "its own name, in another run's plan directory"])
def test_trees_a_batch_input_that_names_another_file_as_a_tree_exits_2_naming_the_finding(assembler, make, how):
    """The batch input's path is held to the one the script builds from ``--run-dir``, the stage, the plan and the ID. The contract's own test of the path (its last
    three parts) passes both of these, so only that comparison refuses them. Nothing is copied from the file that the input names."""
    world = make("trees")
    if how.startswith("another"):
        named = world.source_tree_path("T-1")
    else:
        named = world.root / "elsewhere" / world.plan_id("trees") / "trees" / tree_name("S-1")
        named.parent.mkdir(parents=True)
        named.write_bytes(world.source_tree_path("S-1").read_bytes())
    world.edit_input("trees", "B001", lambda doc: doc["tree_paths"].update({"S-1": str(named)}))
    res = run_refused(world, assembler, "trees", 2)
    assert "S-1" in res.err and "not the plan's own trees/ path" in res.err, res.describe()


def test_trees_two_batches_that_hold_an_item_for_one_finding_exit_2_naming_it_and_the_second_batch(assembler, make):
    """One tree can't be written by two batches. B002's plan entry, batch input and part all name S-1 as well, as a planner that listed it twice would have written them."""
    world = make("trees")
    first_input = read_json(world.input_path("trees", "B001"))
    unit = next(u for u in first_input["units"] if u["finding_id"] == "S-1")
    item = next(i for i in read_json(world.part_path("trees", "B001"))["items"] if i["finding_id"] == "S-1")

    def edit_input(doc):
        doc["finding_ids"].append("S-1")
        doc["units"].append(unit)
        doc["tree_paths"]["S-1"] = first_input["tree_paths"]["S-1"]

    def edit_part(doc):
        doc["finding_ids"].append("S-1")
        doc["items"].append(item)

    world.edit_input("trees", "B002", edit_input)
    world.rewrite_plan("trees", lambda doc: next(e for e in doc["batches"] if e["batch_id"] == "B002")["finding_ids"].append("S-1"))
    world.rewrite_json(world.part_path("trees", "B002"), edit_part)
    res = run_refused(world, assembler, "trees", 2)
    assert "two batches hold an item for S-1" in res.err and "B002" in res.err, res.describe()


# ---- the baseline that a carried tree comes from (R-6: a ``refs`` path is a candidate, never trusted, D3)

@pytest.mark.parametrize("how", ["a directory outside the working directory", "a link to a directory outside it"])
def test_trees_a_baseline_directory_that_leaves_the_working_directory_exits_2(assembler, make, how):
    """The copy outside holds every carried tree, so the run would pass if nothing checked where the baseline is."""
    world = make("trees", rule="rule1")
    outside = world.root.parent / ("outside-" + world.root.name)
    shutil.copytree(str(world.baseline), str(outside))
    if how.startswith("a link"):
        shutil.rmtree(str(world.baseline))
        world.baseline.symlink_to(outside)
    else:
        world.rewrite_plan("trees", lambda doc: doc["refs"].update(baseline_dir=str(outside)))
    res = run_refused(world, assembler, "trees", 2)
    assert "baseline" in res.err.lower(), res.describe()


def test_trees_a_baseline_directory_that_is_gone_leaves_every_carried_tree_missing_and_exits_4(assembler, make):
    world = make("trees", rule="rule1")
    shutil.rmtree(str(world.baseline))
    res = run_refused(world, assembler, "trees", 4)
    assert "FR-K5.5" in res.err and "S-1" in res.err, res.describe()


# ---- FR-K5.5, applied early: a tree still missing exits 4

def test_trees_a_generated_tree_that_was_never_written_exits_4_naming_it(assembler, make):
    world = make("trees")
    world.source_tree_path("LLM-1").unlink()
    res = run_refused(world, assembler, "trees", 4)
    assert "LLM-1" in res.err, res.describe()


def test_trees_a_carried_tree_that_the_baseline_lacks_exits_4_naming_it(assembler, make):
    world = make("trees", rule="rule1")
    world.baseline_tree_path("S-1").unlink()
    res = run_refused(world, assembler, "trees", 4)
    assert "S-1" in res.err, res.describe()


def test_trees_a_critical_finding_that_is_neither_generated_nor_carried_exits_4(assembler, make):
    world = make("trees", drop_units=("S-1",))
    res = run_refused(world, assembler, "trees", 4)
    assert "S-1" in res.err, res.describe()


def test_trees_a_tree_for_a_finding_that_is_not_critical_or_high_exits_4(assembler, make):
    """Section 5 holds exactly one tree per Critical and High finding (FR-K5.5), and D-1 is Medium."""
    world = make("trees", extra_units=("D-1",))
    res = run_refused(world, assembler, "trees", 4)
    assert "D-1" in res.err, res.describe()


# ---- where ``trees`` writes: attack-trees/ is written directly, so what is in its way and what a failed write leaves are pinned (RD-7, RD-20)

def test_trees_an_attack_trees_directory_that_is_a_link_exits_2_and_nothing_is_written_through_it(assembler, make):
    world = make("trees")
    target = world.root / "elsewhere-trees"
    target.mkdir()
    (world.out / "attack-trees").symlink_to(target)
    res = run_refused(world, assembler, "trees", 2)
    assert "attack-trees/ is a symbolic link" in res.err, res.describe()
    assert list(target.iterdir()) == [], "the link's target is untouched"


def test_trees_an_attack_trees_name_that_is_a_file_exits_4_and_the_remedy_says_to_run_trees_again(assembler, make):
    world = make("trees")
    (world.out / "attack-trees").write_text("in the way", encoding="utf-8")
    res = run_refused(world, assembler, "trees", 4)
    assert "attack-trees/ could not be created" in res.err and "run assemble-report.py trees again" in res.err, res.describe()


def test_trees_a_write_that_fails_part_way_exits_4_with_the_manifest_unwritten_and_no_stage_record(assembler, make, monkeypatch):
    """The trees go first and the manifest last (RD-20), so a manifest on disk is never newer than the trees it lists, and there is no record of a stage that didn't end."""
    world = make("trees")
    real, calls = tp.atomic_write, []

    def failing(path, data, mode_of=None):
        calls.append(os.fspath(path))
        if len(calls) == 3:
            raise OSError(28, "No space left on device")
        return real(path, data, mode_of=mode_of)

    monkeypatch.setattr(tp, "atomic_write", failing)
    res = world.run(assembler, "trees")
    assert res.code == 4, res.describe()
    assert_failure(res, "trees", world.plan_id("trees"))
    assert "the trees could not be written (No space left on device)" in res.err and "run assemble-report.py trees again" in res.err, res.describe()
    assert not world.manifest_path.exists() and not world.record_path("trees").exists()
    assert sorted(p.name for p in (world.out / "attack-trees").iterdir()) == sorted(tree_name(i) for i in world.ch_ids[:2]), "the two before the failure, whole"


# ---- S1P-A18: the forbidden-character predicate, at the tree checks (exit 2, D4)

def put_character(path, char):
    """Plant ``char`` in the first label of a tree file, as a hostile agent or a forged baseline would."""
    data = path.read_bytes()
    assert b"Goal" in data
    path.write_bytes(data.replace(b"Goal", ("Go" + char + "al").encode("utf-8"), 1))


@pytest.mark.parametrize("name,char", FORBIDDEN_SAMPLES)
def test_trees_a_carried_tree_with_a_forbidden_character_exits_2_naming_the_finding_and_the_remedy(assembler, make, name, char):
    world = make("trees", rule="rule1")
    put_character(world.baseline_tree_path("S-1"), char)
    res = run_refused(world, assembler, "trees", 2)
    assert "S-1" in res.err and "regenerate" in res.err.lower(), res.describe()


@pytest.mark.parametrize("name,char", [s for s in FORBIDDEN_SAMPLES if s[0] in ("escape", "right-to-left-override", "tag-letter-a", "line-separator")])
def test_trees_a_generated_tree_with_a_forbidden_character_exits_2_naming_the_finding(assembler, make, name, char):
    world = make("trees", rule="rule1")
    put_character(world.source_tree_path("I-1"), char)
    res = run_refused(world, assembler, "trees", 2)
    assert "I-1" in res.err, res.describe()


@pytest.mark.parametrize("name,char", ALLOWED_SAMPLES)
def test_trees_a_character_the_predicate_allows_is_copied_as_it_is(assembler, make, name, char):
    world = make("trees", rule="rule1")
    path = world.baseline_tree_path("S-1")
    put_character(path, char)
    trees_ok(world, assembler)
    assert world.tree_path("S-1").read_bytes() == path.read_bytes()


# =============================================================================
# 4. assemble-report.py report (T109; ADR-050 D14; FR-K5.2, FR-K5.3, FR-K5.5, FR-K5.7; RR3)
# =============================================================================

THREAT_OF = {f.id: f.threat for f in FINDINGS}
COMPONENT_OF = {f.id: f.component for f in FINDINGS}


def report_ok(world, assembler):
    res = world.run(assembler, "report")
    assert res.code == 0, res.describe()
    return res


def title_number(text, title_part):
    return next(n for n, title in numbered_sections(text) if title_part in title)


def roadmap_rows(world):
    """The roadmap table's rows, read as every later reader reads a table (references decoded)."""
    text = world.report_text
    number = title_number(text, "Remediation Roadmap")
    title = dict(numbered_sections(text))[number]
    rows = tachi_parsers.parse_markdown_table(text, "## %d. %s" % (number, title))
    assert rows, "the roadmap section holds a table with rows"
    return rows


# ---- RR3: the report plan pins the trees plan, and threats.md is checked by its reference set

def test_report_a_trees_plan_that_is_no_longer_the_current_one_exits_2(assembler, make):
    world = make("report")
    write_json(world.pointer_path("trees"), {"schema": tp.POINTER_SCHEMA, "plan_id": OTHER_ID})
    run_refused(world, assembler, "report", 2)


def test_report_a_trees_plan_file_that_changed_since_the_report_plan_exits_2(assembler, make):
    world = make("report")
    path = world.plan_path("trees")
    path.write_bytes(path.read_bytes() + b"\n")
    run_refused(world, assembler, "report", 2)


def test_report_a_trees_plan_with_a_batch_that_is_not_done_exits_2(assembler, make):
    """The pinned plan is held to RR3's checks as well, so a digest that was re-pinned still meets the content check."""
    world = make("report")
    world.rewrite_plan("trees", lambda doc: doc["batches"][0].update(state="pending"))
    size = world.plan_path("trees").stat().st_size
    world.rewrite_plan("report", lambda doc: doc["inputs"]["trees_plan"].update(sha256=world.digest["trees"], bytes=size))
    run_refused(world, assembler, "report", 2)


def test_report_a_trees_part_that_fails_its_checks_exits_2(assembler, make):
    world = make("report")
    world.rewrite_json(world.part_path("trees", "B001"), lambda doc: doc.update(plan_id=OTHER_ID))
    run_refused(world, assembler, "report", 2)


def test_report_a_trees_part_that_is_missing_exits_1(assembler, make):
    world = make("report")
    world.part_path("trees", "B001").unlink()
    run_refused(world, assembler, "report", 1)


def _outside_baseline(world):
    outside = world.root.parent / ("outside-" + world.root.name)
    shutil.copytree(str(world.baseline), str(outside))
    world.rewrite_plan("trees", lambda doc: doc["refs"].update(baseline_dir=str(outside)))
    repin_trees_plan(world)


TREES_PLAN_REFUSALS = {
    "a batch that is not done": lambda world: (world.rewrite_plan("trees", lambda doc: doc["batches"][0].update(state="pending")), repin_trees_plan(world)),
    "no valid rule": lambda world: (world.rewrite_plan("trees", lambda doc: doc["params"].update(rule_applied="Rule 9")), repin_trees_plan(world)),
    "a reference digest that differs": lambda world: (world.rewrite_plan("trees", lambda doc: doc["params"].update(reference_digest="0" * 64)), repin_trees_plan(world)),
    "a baseline outside the working directory": _outside_baseline,
    "a part that is gone": lambda world: world.part_path("trees", "B001").unlink(),
}


@pytest.mark.parametrize("case", sorted(TREES_PLAN_REFUSALS))
def test_report_what_it_refuses_about_the_trees_plan_is_kept_for_diagnosis_where_that_plan_is(assembler, make, case):
    """S1P-A47: the report holds the plan it pins to the checks of its own, under its own banner, and a refusal about that plan names that plan's directory.
    (Any other refusal names the report plan's, which every other test of this mode shows through ``run_refused``.)"""
    world = make("report", rule="rule1")
    TREES_PLAN_REFUSALS[case](world)
    res = world.run(assembler, "report")
    assert res.code in (1, 2), res.describe()
    assert_failure(res, "report")
    kept = re.search(r"(?m)^Kept for diagnosis: (.*)$", res.err)
    assert kept is not None and world.plan_id("trees") in kept.group(1) and world.plan_id("report") not in kept.group(1), res.describe()


def test_report_a_manifest_that_changed_since_the_plan_exits_2(assembler, make):
    """An input's digest is checked, so even a whitespace change to the merged manifest ends the run before any part is read."""
    world = make("report")
    world.append(world.manifest_path, "\n")
    run_refused(world, assembler, "report", 2)


def test_report_threats_md_may_gain_the_populators_block_after_the_plan(assembler, make):
    """Steps 2.5 to 2.8 rewrite ``threats.md`` on every run, so its bytes are not checked: its reference set is (RR3, RD-9)."""
    world = make("report")
    world.append(world.threats_path, "\n## Affected Assets\n\n| Finding ID | Affected Assets |\n|---|---|\n| S-1 | Gateway |\n")
    report_ok(world, assembler)


# ---- the sections, in template order (T109: "numbers the sections in template order, the conditional ones included")

def expected_titles(patterns, baseline):
    titles = template_titles()
    expected = [titles[n] for n in (1, 2, 3, 4, 5, 6)]  # reading: RD-11, Section 6 is on every run
    if patterns:
        expected.append("Agentic Pattern Analysis")
    expected += [titles[7], titles[8]]
    if baseline:
        expected.append(titles[9])
    return expected


@pytest.mark.parametrize("patterns", [False, True])
@pytest.mark.parametrize("rule", ["no-baseline", "rule2"])
def test_report_numbers_the_sections_present_in_template_order(assembler, make, rule, patterns):
    world = make("report", rule=rule, patterns=patterns)
    report_ok(world, assembler)
    text = world.report_text
    sections = numbered_sections(text)
    assert sections == list(enumerate(expected_titles(patterns, rule == "rule2"), 1)), sections
    assert not re.search(r"(?m)^## \d+[a-z]\. ", text), "a conditional section takes the next number, never a suffix (RD-11)"


def test_report_the_attack_trees_section_is_5_and_the_executive_summary_is_1_whatever_is_conditional(assembler, make):
    world = make("report", rule="rule2", patterns=True, planned_chains=True, outcome=OUTCOME_WRITTEN)
    report_ok(world, assembler)
    titles = template_titles()
    assert dict(numbered_sections(world.report_text))[1] == titles[1] and dict(numbered_sections(world.report_text))[5] == titles[5]


@pytest.mark.parametrize("compliance", [False, True])
def test_report_the_compliance_subsection_exists_only_with_its_fragment(assembler, make, compliance):
    world = make("report", compliance=compliance)
    report_ok(world, assembler)
    headings = [title for _, level, title in atx_headings(section_text(world.report_text, 1)) if level == 3]
    assert ("Compliance Relevance" in headings) is compliance, headings
    for name in ("Risk Posture", "Top 5 Threats by Business Impact", "Key Recommendations", "Remediation Timeline"):
        assert name in headings, headings


def test_report_each_fragment_lands_in_its_own_section_and_only_there(assembler, make):
    world = make("report", rule="rule2", patterns=True, planned_chains=True, outcome=OUTCOME_WRITTEN, compliance=True, themes=2)
    report_ok(world, assembler)
    text = world.report_text
    titles = template_titles()
    where = {"exec_summary": titles[1], "architecture_overview": titles[2], "threat_categories": titles[3], "cross_cutting_themes": titles[4],
             "attack_chains": titles[6], "agentic_patterns": "Agentic Pattern Analysis", "delta_summary": titles[9]}
    bodies = {title: section_text(text, number) for number, title in numbered_sections(text)}
    seen = 0
    for section, units in world.section_plan():
        for fragment in world.fragments_of(section, units):
            holders = [title for title, body in bodies.items() if fragment["text"] in body]
            assert holders == [where[section]], (section, fragment["slot_key"], holders)
            seen += 1
    assert seen >= 15, "every planned fragment was checked"


def test_report_themes_get_a_numbered_heading_and_a_body_and_none_gets_the_templates_note(assembler, make):
    world = make("report", themes=2)
    report_ok(world, assembler)
    section = section_text(world.report_text, 4)
    for n, word in ((1, "one"), (2, "two")):
        heading = re.search(r"(?m)^#{3,4} Theme %d: Marker for theme title %s\.$" % (n, word), section)
        assert heading is not None, section
        assert section.index("Marker for theme body %s." % word) > heading.start()
    empty = make("report", themes=0)
    report_ok(empty, assembler)
    assert "No cross-cutting themes identified." in section_text(empty.report_text, 4)


def test_report_findings_text_lands_in_its_own_section(assembler, make):
    world = make("report", rule="rule2")
    report_ok(world, assembler)
    text = world.report_text
    roadmap = title_number(text, "Remediation Roadmap")
    for finding_id in world.open_ids():
        assert "Marker narrative for %s." % finding_id in section_text(text, 3), finding_id
    for finding_id in world.ch_ids:
        assert "Marker summary for %s." % finding_id in section_text(text, 5), finding_id
    for finding_id, item in world.roadmap_items.items():
        if item["dependencies"]:
            assert "Marker dependency for %s." % finding_id in section_text(text, roadmap), finding_id
    assert "Marker summary" not in section_text(text, 3) and "Marker narrative" not in section_text(text, 5)


# ---- Section 5, from the standalone files (FR-K5.2)

def test_report_section_5_holds_each_trees_mermaid_source_byte_for_byte_and_out_fences_any_inner_run(assembler, make):
    world = make("report", rule="rule2", ticks_for={"S-1": 3, "T-1": 5})
    report_ok(world, assembler)
    standalone = [mermaid_sources(world.tree_path(i).read_text(encoding="utf-8"))[0] for i in world.ch_ids]
    blocks = [b for b in fenced_blocks(section_text(world.report_text, 5)) if b["info"] == "mermaid"]
    assert [b["source"] for b in blocks] == standalone, "one block for each Critical and High finding, in manifest order, equal to its file's source"
    for block in blocks:
        assert block["closed"] and block["fence"] >= 3 and block["fence"] > longest_run(block["source"]), block["source"][:60]
    assert [longest_run(s) for s in standalone[:2]] == [3, 5], "premise: S-1 and T-1 carry inner runs of three and five"


def test_report_section_5_orders_each_trees_heading_then_its_summary_then_its_fence(assembler, make):
    world = make("report", rule="rule2")
    report_ok(world, assembler)
    section = section_text(world.report_text, 5)
    lines = section.split("\n")
    headings = [(n, title) for n, level, title in atx_headings(section) if level == 3]
    assert [title for _, title in headings] == ["%s: %s" % (i, THREAT_OF[i]) for i in world.ch_ids], "manifest order, one heading each (RD-14)"
    blocks = [b for b in fenced_blocks(section) if b["info"] == "mermaid"]
    for k, (start, _title) in enumerate(headings):
        end = headings[k + 1][0] if k + 1 < len(headings) else len(lines)
        summary = [n for n in range(start, end) if "Marker summary for %s." % world.ch_ids[k] in lines[n]]
        mine = [b for b in blocks if start < b["start"] < end]
        assert len(summary) == 1 and len(mine) == 1 and summary[0] < mine[0]["start"], world.ch_ids[k]


def test_report_section_5_with_no_critical_or_high_finding_prints_the_templates_note(assembler, make):
    world = make("report", rule="no-op")
    report_ok(world, assembler)
    section = section_text(world.report_text, 5)
    assert "No Critical or High findings identified." in section and mermaid_sources(section) == []  # reading: the template's note
    assert frontmatter_of(world.report_text)["attack_tree_count"] in (0, "0")


# ---- the stamp, the overwrite and the bytes (D4, FR-K5.7)

@pytest.mark.parametrize("earlier", ["no stamp", "a forged stamp"])
def test_report_stamps_the_file_and_overwrites_any_report_an_agent_wrote(assembler, make, earlier):
    world = make("report")
    forged = "<!-- tachi-provenance: renderer=assemble-report.py; version=%s; input-digest=sha256:%s -->\n" % (tp.VERSION, "0" * 64)
    world.report_path.write_text("# Threat Report\n\nAn agent wrote this.\n" + (forged if earlier == "a forged stamp" else ""), encoding="utf-8")
    report_ok(world, assembler)
    text = world.report_text
    assert "An agent wrote this." not in text
    stamp = tp.read_stamp(text)
    assert stamp is not None and (stamp["renderer"], stamp["version"]) == ("assemble-report.py", tp.VERSION)
    assert stamp["input_digest"] != "sha256:" + "0" * 64 and text.count("tachi-provenance") == 1
    assert text.rstrip("\n").split("\n")[-1].startswith("<!-- tachi-provenance:"), "the stamp ends the file (D4)"
    assert world.record("report")["input_digest"] == stamp["input_digest"], "the stamp and the stage record carry one digest"


def test_report_two_runs_over_the_same_input_give_the_same_bytes(assembler, make):
    """NFR-2: the plan IDs differ, and so do the directories, and neither is in the file."""
    first = make("report", rule="rule2", patterns=True, groups=A20_GROUPS)
    second = make("report", rule="rule2", patterns=True, groups=A20_GROUPS, trees_id=OTHER_ID, report_id="20261124T130000Z-dddddddddddd")
    report_ok(first, assembler)
    report_ok(second, assembler)
    assert first.report_path.read_bytes() == second.report_path.read_bytes()


def test_report_the_stamps_input_digest_follows_the_parts(assembler, make):
    first, second = make("report"), make("report")
    path = second.part_path("report", "B001")

    def reword(doc):
        doc["fragments"][0]["text"] = "Another passage with the same shape."

    second.rewrite_json(path, reword)
    report_ok(first, assembler)
    report_ok(second, assembler)
    assert tp.read_stamp(first.report_text)["input_digest"] != tp.read_stamp(second.report_text)["input_digest"]


def test_report_writes_only_the_report_and_its_own_plan_directory(assembler, make):
    world = make("report", rule="rule2", patterns=True)
    before = tree_state(world.out)
    report_ok(world, assembler)
    after = tree_state(world.out)
    assert all(after.get(path) == digest for path, digest in before.items()), "no earlier file is changed or removed"
    plan_prefix = ".tachi-build/report/%s/" % world.plan_id("report")
    assert {path for path in after if path not in before and not path.startswith(plan_prefix)} == {"threat-report.md"}
    assert (world.out / plan_prefix / "stage-record.json").is_file() and tp.file_digest(world.plan_path("report")) == world.digest["report"]


def test_report_a_refused_run_leaves_the_agents_report_where_it_was(assembler, make):
    world = make("report")
    world.report_path.write_text("# Threat Report\n\nAn agent wrote this.\n", encoding="utf-8")
    (world.out / "attack-trees" / "extra-attack-tree.md").write_bytes(world.expected_bytes("S-1"))  # FR-K5.7: unlisted
    run_refused(world, assembler, "report", 4)
    assert world.report_text == "# Threat Report\n\nAn agent wrote this.\n"


# ---- Section 6: the chains for ``chains written``, the outcome line otherwise (PM-T3, D13)

def test_report_section_6_for_chains_written_holds_each_surfaced_chain_in_rank_order(assembler, make):
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    report_ok(world, assembler)
    section = section_text(world.report_text, 6)
    positions = []
    for chain_id, title in CHAINS:
        heading = re.search(r"(?m)^#{3,4} %s: %s$" % (chain_id, re.escape(title)), section)
        assert heading is not None, section
        assert marker("attack_chains", "chain." + chain_id) in section[heading.end():]
        positions.append(heading.start())
    assert positions == sorted(positions), "rank order is the chain file's order"
    assert "CHAIN-007" not in section, "only the surfaced chains are reported, never a consolidated one in Section 3's table of the chain file"


@pytest.mark.parametrize("outcome", [OUTCOME_ZERO, OUTCOME_SKIPPED])
def test_report_section_6_for_any_other_outcome_prints_the_outcome_line(assembler, make, outcome):
    world = make("report", outcome=outcome)
    report_ok(world, assembler)
    section = section_text(world.report_text, 6)
    assert outcome in section and not re.search(r"(?m)^#{3,4} CHAIN-", section)


def test_report_a_chain_check_rewrite_after_the_plan_drops_the_chain_part_and_prints_the_outcome(assembler, make):
    """R-24: ``attack-chains.py check`` rewrote the record as skipped and quarantined the file, after the plan counted on ``chains written``."""
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    world.threats_path.write_text(world.threats_path.read_text(encoding="utf-8").replace(OUTCOME_WRITTEN, OUTCOME_SKIPPED), encoding="utf-8")
    world.chains_path.unlink()
    report_ok(world, assembler)
    text = world.report_text
    assert OUTCOME_SKIPPED in section_text(text, 6)
    assert not re.search(r"(?m)^#{3,4} CHAIN-", text)
    for chain_id, _ in CHAINS:
        assert marker("attack_chains", "chain." + chain_id) not in text, "the planned part is left out, never half used"


@pytest.mark.parametrize("held", ["one chain missing", "an extra chain", "another chain"])
def test_report_chains_written_but_the_chain_file_does_not_hold_the_planned_chains_exits_2(assembler, make, held):
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    chains = {"one chain missing": CHAINS[:1], "an extra chain": CHAINS + [("CHAIN-003", "A third chain")],
              "another chain": [CHAINS[0], ("CHAIN-009", "Another chain")]}[held]
    world.chains_path.write_text(make_attack_chains_md(chains), encoding="utf-8")
    run_refused(world, assembler, "report", 2)


@pytest.mark.parametrize("how", ["gone", "a link"])
def test_report_chains_written_but_the_chain_file_is_gone_or_a_link_is_refused(assembler, make, how):
    """The plan lists ``attack-chains.md`` as an input for ``chains written``, so a missing one is a missing input (exit 1). A link is a guard failure (exit 2)."""
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    if how == "gone":
        world.chains_path.unlink()
    else:
        real = world.root / "elsewhere-chains.md"
        real.write_bytes(world.chains_path.read_bytes())
        world.chains_path.unlink()
        world.chains_path.symlink_to(real)
    res = run_refused(world, assembler, "report", 1 if how == "gone" else 2)
    assert "attack-chains.md fails the path guard" in res.err, res.describe()


@pytest.mark.parametrize("outcome", [None, "chains written (abc)", OUTCOME_SKIPPED + "\n**Attack chain outcome**: " + OUTCOME_ZERO], ids=["absent", "malformed", "multiple"])
def test_report_section_6_for_an_outcome_record_that_cannot_be_read_prints_the_fixed_sentence_and_no_chain(assembler, make, outcome):
    """``attack-chains.py check`` rewrites such a record before Step 2.9, so this only holds if the check didn't run. The report neither guesses a chain nor stops."""
    world = make("report", outcome=outcome)
    report_ok(world, assembler)
    section = section_text(world.report_text, 6)
    assert "No attack chain outcome record is readable in threats.md." in section and not re.search(r"(?m)^#{3,4} CHAIN-", section)


# ---- FR-K5.3, FR-K5.5 and FR-K5.7: each exits 4 (ADR-050 D14)

@pytest.mark.parametrize("rule,finding_id", [("rule1", "S-1"), ("rule2", "T-2")])
def test_report_a_carried_tree_that_differs_from_its_baseline_file_exits_4_naming_it(assembler, make, rule, finding_id):
    """FR-K5.3 holds for a tree that Rule 1 carried and for one that Rule 3 carried alike."""
    world = make("report", rule=rule)
    path = world.tree_path(finding_id)
    path.write_bytes(path.read_bytes() + b"\n")
    res = run_refused(world, assembler, "report", 4)
    assert finding_id in res.err, res.describe()


def test_report_a_regenerated_tree_is_not_compared_with_the_baseline(assembler, make):
    world = make("report", rule="rule2")
    assert world.tree_path("OI-1").read_bytes() != world.base_bytes["OI-1"], "premise: the regenerated tree differs from its baseline"
    report_ok(world, assembler)


def test_report_a_tree_file_that_is_missing_exits_4_naming_it(assembler, make):
    world = make("report")
    world.tree_path("T-1").unlink()
    res = run_refused(world, assembler, "report", 4)
    assert "T-1" in res.err, res.describe()


def test_report_a_critical_finding_that_has_no_tree_exits_4_against_threats_md_not_the_manifest(assembler, make):
    """The manifest and the files agree here, and still S-1 is Critical in Section 7 (FR-K5.5)."""
    world = make("report", drop_units=("S-1",))
    assert "S-1" not in [e["finding_id"] for e in read_json(world.manifest_path)["trees"]]
    res = run_refused(world, assembler, "report", 4)
    assert "S-1" in res.err, res.describe()


def test_report_a_tree_for_a_finding_that_is_not_critical_or_high_exits_4(assembler, make):
    world = make("report", extra_units=("D-1",))
    assert "D-1" in [e["finding_id"] for e in read_json(world.manifest_path)["trees"]]
    res = run_refused(world, assembler, "report", 4)
    assert "D-1" in res.err, res.describe()


def test_report_a_markdown_file_in_attack_trees_that_the_manifest_does_not_list_exits_4_naming_it(assembler, make):
    world = make("report")
    (world.out / "attack-trees" / "zz-9-attack-tree.md").write_bytes(world.expected_bytes("S-1"))
    res = run_refused(world, assembler, "report", 4)
    assert "zz-9-attack-tree.md" in res.err, res.describe()


def test_report_a_file_that_is_not_markdown_is_not_an_unlisted_tree(assembler, make):
    """The shipped samples keep a rendered ``.png`` beside a tree, and the manifest itself is a ``.json`` file."""
    world = make("report")
    (world.out / "attack-trees" / "s-1-attack-tree.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    report_ok(world, assembler)


def test_report_a_manifest_that_is_not_the_merge_of_the_batch_manifests_exits_4(assembler, make):
    """Re-pinned in the report plan, so the digest check passes and only FR-K5.7's recomputed merge catches it."""
    world = make("report", rule="rule2")
    world.rewrite_json(world.manifest_path, lambda doc: doc["trees"][0].update(delta_status="UPDATED"))
    pinned = plan_input(world.manifest_path)
    world.rewrite_plan("report", lambda doc: doc["inputs"].update(tree_manifest=pinned))
    run_refused(world, assembler, "report", 4)


def test_report_a_trees_part_that_changed_after_the_merge_makes_the_manifest_stale_and_exits_4(assembler, make):
    world = make("report", rule="rule2")

    def rescore(doc):
        next(item for item in doc["items"] if item["finding_id"] == "T-2")["similarity_score"] = 0.5

    world.rewrite_json(world.part_path("trees", "B001"), rescore)
    run_refused(world, assembler, "report", 4)


MANIFEST_DAMAGE = {
    "not JSON": b"{this is not json",
    "a duplicate key": b'{"schema_version": "1.0", "schema_version": "1.0"}',
    "a NaN": b'{"schema_version": "1.0", "attack_tree_count": NaN}',
    "nested too deep": b"[" * 100000,
    "not UTF-8": b"\xff\xfe{}",
    "no list of trees": b'{"schema_version": "1.0", "trees": 3}',
    "a tree with no finding ID": b'{"schema_version": "1.0", "trees": [{"finding_id": "not-an-id"}]}',
}


@pytest.mark.parametrize("damage", sorted(MANIFEST_DAMAGE))
def test_report_a_manifest_that_is_not_the_schema_1_0_json_exits_4(assembler, make, damage):
    """FR-K5.7. The report plan is re-pinned over the damaged file, so the digest check passes and the manifest's own check is the one that refuses it."""
    world = make("report")
    world.manifest_path.write_bytes(MANIFEST_DAMAGE[damage])
    pinned = plan_input(world.manifest_path)
    world.rewrite_plan("report", lambda doc: doc["inputs"].update(tree_manifest=pinned))
    res = run_refused(world, assembler, "report", 4)
    assert "FR-K5.7" in res.err, res.describe()


@pytest.mark.parametrize("gone", ["the file", "the directory"])
def test_report_a_carried_tree_whose_baseline_file_is_gone_exits_4_naming_it(assembler, make, gone):
    """FR-K5.3 compares each carried tree with its baseline file, so a baseline that is missing is a failed comparison, not a skipped one."""
    world = make("report", rule="rule1")
    if gone == "the file":
        world.baseline_tree_path("S-1").unlink()
    else:
        shutil.rmtree(str(world.baseline))
    res = run_refused(world, assembler, "report", 4)
    assert "FR-K5.3" in res.err and "S-1" in res.err and "has no baseline file" in res.err, res.describe()


def test_report_a_baseline_directory_that_leaves_the_working_directory_exits_2(assembler, make):
    world = make("report", rule="rule1")
    outside = world.root.parent / ("outside-" + world.root.name)
    shutil.copytree(str(world.baseline), str(outside))
    world.rewrite_plan("trees", lambda doc: doc["refs"].update(baseline_dir=str(outside)))
    repin_trees_plan(world)
    res = run_refused(world, assembler, "report", 2)
    assert "baseline" in res.err.lower(), res.describe()


def test_report_a_tree_file_that_is_a_link_exits_2_naming_the_finding(assembler, make):
    world = make("report")
    path = world.tree_path("S-1")
    real = world.root / "elsewhere-tree.md"
    real.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(real)
    res = run_refused(world, assembler, "report", 2)
    assert "S-1" in res.err and "path guard" in res.err, res.describe()


def test_report_an_attack_trees_directory_that_is_a_link_exits_2(assembler, make):
    """With no tree to guard one by one, the directory itself is what is checked: a listing through a link would show files that aren't this run's."""
    world = make("report", rule="no-op")
    moved = world.root / "elsewhere-trees"
    (world.out / "attack-trees").rename(moved)
    (world.out / "attack-trees").symlink_to(moved)
    res = run_refused(world, assembler, "report", 2)
    assert "attack-trees/ is a symbolic link" in res.err, res.describe()


# ---- the roadmap and S1P-A20: a group's primary is D8's, never "its first member in Section 4a"

def test_report_the_roadmap_has_one_row_for_each_open_finding_in_risk_component_and_id_order(assembler, make):
    world = make("report", rule="rule2")
    report_ok(world, assembler)
    rows = roadmap_rows(world)
    assert [row["Finding ID"] for row in rows] == ["S-1", "T-1", "LLM-1", "I-1", "T-2", "AG-1", "OI-1", "D-1", "E-1"]
    for row in rows:
        finding_id = row["Finding ID"]
        f = next(f for f in world.findings if f.id == finding_id)
        item = world.roadmap_items[finding_id]
        assert (row["Component"], row["Mitigation"], row["Effort"]) == (f.component, f.mitigation, item["effort"]), finding_id
        assert row["Dependencies"] == (item["dependencies"].replace("{{finding:%s}}" % finding_id, finding_id) if item["dependencies"] else "None"), finding_id


def test_report_a_groups_roadmap_row_names_the_primary_that_d8_gives(assembler, make):
    """S1P-A20. CG-1 lists RESOLVED R-9 first, CG-3 lists S-1 first and CG-2 claims it, and CG-4 keeps one open member."""
    world = make("report", rule="rule2", groups=A20_GROUPS)
    report_ok(world, assembler)
    rows = roadmap_rows(world)
    assert [row["Finding ID"] for row in rows] == ["S-1", "T-1", "LLM-1", "OI-1", "D-1", "E-1"], "peers have no row of their own, and R-9 none at all"
    by_id = {row["Finding ID"]: row for row in rows}
    members = {"T-1": ("CG-1", ["T-1", "T-2"]), "S-1": ("CG-2", ["S-1", "I-1"]), "LLM-1": ("CG-3", ["LLM-1", "AG-1"])}
    for primary, (group, ids) in members.items():
        row = by_id[primary]
        assert row["Component"] == COMPONENT_OF[primary], "a group's row takes its primary's component"
        assert row["Dependencies"].startswith("Correlated:") and "(%s)" % group in row["Dependencies"], row["Dependencies"]
        assert all(i in row["Dependencies"] for i in ids), row["Dependencies"]
        at = [row["Mitigation"].index(i) for i in ids]
        mitigations = [row["Mitigation"].index(next(f.mitigation for f in FINDINGS if f.id == i)) for i in ids]
        assert at[0] < mitigations[0] < at[1] < mitigations[1], "each member's mitigation, verbatim, in member order, led by its ID: " + row["Mitigation"]
    assert "CG-3" not in by_id["S-1"]["Dependencies"] and "R-9" not in "".join(by_id[i]["Dependencies"] + by_id[i]["Mitigation"] for i in by_id)
    for plain in ("E-1", "D-1", "OI-1"):
        assert not by_id[plain]["Dependencies"].startswith("Correlated:"), plain
    assert by_id["E-1"]["Mitigation"] == "Enforce least privilege", "CG-4 emitted nothing, so E-1 is an ordinary row"


def test_report_a_group_row_sorts_by_the_groups_highest_risk_level_and_takes_the_primarys_component(assembler, make):
    """E-1 (Low) leads CG-1 and OI-1 (High) is its peer, so the row stands among the High rows, and first there: "Admin Console" sorts first."""
    world = make("report", rule="rule2", groups=[("CG-1", ["E-1", "OI-1"])])
    report_ok(world, assembler)
    rows = roadmap_rows(world)
    assert [row["Finding ID"] for row in rows] == ["S-1", "T-1", "LLM-1", "E-1", "I-1", "T-2", "AG-1", "D-1"]
    row = rows[3]
    assert row["Component"] == "Admin Console" and "(CG-1)" in row["Dependencies"] and "OI-1" in row["Dependencies"]
    assert row["Mitigation"].index("Enforce least privilege") < row["Mitigation"].index("Encode all model output")


@pytest.mark.parametrize("change", ["a group that the plan did not have", "a group that the plan had and the file has lost"])
def test_report_a_roadmap_whose_rows_changed_since_the_plan_exits_2_naming_both_sets(assembler, make, change):
    """Section 4a is outside the reference digest (RD-9), so a plan can stand while the groups change. Then a peer has an item and no row, or a row has no item, and
    the table would hold a finding twice or leave one out. The report refuses it."""
    if change.startswith("a group that the plan did not"):
        world = make("report", rule="rule2")
        world.groups = [("CG-1", ["T-1", "T-2"])]
    else:
        world = make("report", rule="rule2", groups=A20_GROUPS)
        world.groups = []
    world.write_threats()
    res = run_refused(world, assembler, "report", 2)
    assert "the roadmap parts hold items for" in res.err and "Section 4a" in res.err, res.describe()


# ---- the sinks (ADR-050 D3, "Output"): every cell takes the cell sink and every fragment the prose sink

def test_report_a_roadmap_cell_takes_the_cell_sink_so_markup_from_threats_md_stays_text(assembler, make):
    """threats.md is rendered text, so S-1's mitigation is stored escaped. It reads back as ``Use a | b <i>x</i> & `code```, and the report
    writes it escaped again, so no raw pipe splits the row and no raw tag reaches a viewer."""
    stored = "Use a &#124; b &lt;i&gt;x&lt;/i&gt; &amp; &#96;code&#96;"
    findings = [f._replace(mitigation=stored) if f.id == "S-1" else f for f in findings_for("rule2")]
    world = make("report", rule="rule2", findings=findings)
    report_ok(world, assembler)
    row = next(r for r in roadmap_rows(world) if r["Finding ID"] == "S-1")
    assert row["Mitigation"] == tachi_parsers.decode_references(stored) == "Use a | b <i>x</i> & `code`"
    section = section_text(world.report_text, title_number(world.report_text, "Remediation Roadmap"))
    assert "<i>" not in section and "&lt;i&gt;" in section


def test_report_a_fragment_cannot_forge_a_heading_or_open_a_code_fence(assembler, make):
    """D3, P0-1: a prose line that starts with ``#`` or ``~`` is written with a character reference, so it can't add a section or hide the rest."""
    world = make("report", rule="rule2", patterns=True)
    reword(world, "risk_posture", "Intro line\n## Forged heading\n~~~\nOutro line")
    report_ok(world, assembler)
    text = world.report_text
    assert numbered_sections(text) == list(enumerate(expected_titles(True, True), 1)), "no section was added or hidden"
    assert not any(title == "Forged heading" for _, _, title in atx_headings(text))
    assert "Intro line" in text and "Outro line" in text and "&#35;" in text and "&#126;" in text


# ---- S1P-A18: the forbidden-character predicate where the assembler takes a value from an input that is not a part (exit 2, D4)

def hostile_findings(field, char):
    """The findings with ``char`` planted inside S-1's ``field``, away from the edges (a reader strips edge whitespace before it looks)."""
    def plant(f):
        value = getattr(f, field)
        return f._replace(**{field: value[:4] + char + value[4:]}) if f.id == "S-1" else f

    return [plant(f) for f in findings_for("rule2")]


@pytest.mark.parametrize("field", ["component", "threat", "mitigation"])
@pytest.mark.parametrize("name,char", [s for s in FORBIDDEN_SAMPLES if s[0] in ("escape", "right-to-left-override", "tag-letter-a")])
def test_report_a_forbidden_character_in_a_threats_md_value_exits_2_naming_the_finding_the_field_and_the_remedy(assembler, make, field, name, char):
    world = make("report", rule="rule2", findings=hostile_findings(field, char))  # planned over the hostile file, so only the intake refuses it
    res = run_refused(world, assembler, "report", 2)
    assert "S-1" in res.err and field in res.err.lower() and "regenerate" in res.err.lower(), res.describe()


@pytest.mark.parametrize("name,char", FORBIDDEN_SAMPLES)
def test_report_every_character_the_predicate_returns_is_refused_in_a_threats_md_value(assembler, make, name, char):
    """S1P-A18: the whole set. A whitespace-class character (a carriage return, NEL, a separator) may meet the table reader before the
    intake does, so only the exit code is pinned here; the named message is the three tests above."""
    world = make("report", rule="rule2", findings=hostile_findings("mitigation", char))
    run_refused(world, assembler, "report", 2)


@pytest.mark.parametrize("name,char", [s for s in FORBIDDEN_SAMPLES if s[0] in ("escape", "right-to-left-override")])
def test_report_a_forbidden_character_in_the_baseline_source_of_the_frontmatter_exits_2(assembler, make, name, char):
    world = make("report", rule="rule2", baseline_source="baseline/threats.md" + char)
    res = run_refused(world, assembler, "report", 2)
    assert "regenerate" in res.err.lower(), res.describe()


@pytest.mark.parametrize("name,char", [s for s in FORBIDDEN_SAMPLES if s[0] in ("escape", "right-to-left-override", "tag-letter-a")])
def test_report_a_forbidden_character_in_a_standalone_tree_exits_2_naming_the_finding(assembler, make, name, char):
    world = make("report")
    put_character(world.tree_path("S-1"), char)
    res = run_refused(world, assembler, "report", 2)
    assert "S-1" in res.err, res.describe()


@pytest.mark.parametrize("name,char", FORBIDDEN_SAMPLES)
def test_report_every_character_the_predicate_returns_is_refused_in_a_standalone_tree(assembler, make, name, char):
    world = make("report")
    put_character(world.tree_path("S-1"), char)
    run_refused(world, assembler, "report", 2)


def test_report_a_forbidden_character_in_a_chain_title_exits_2_naming_the_chain(assembler, make):
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    world.chains_path.write_text(make_attack_chains_md(CHAINS).replace("Token replay", "Token \u202e replay"), encoding="utf-8")
    res = run_refused(world, assembler, "report", 2)
    assert "CHAIN-001" in res.err, res.describe()


@pytest.mark.parametrize("where", ["fragment", "narrative", "a lone surrogate, as a JSON escape"])
def test_report_a_part_that_holds_a_forbidden_character_fails_the_part_checks_with_exit_2(assembler, make, where):
    world = make("report")
    if where == "fragment":
        world.rewrite_json(world.part_path("report", "B001"), lambda doc: doc["fragments"][0].update(text=doc["fragments"][0]["text"] + "\x1b"))
    elif where.startswith("a lone"):
        world.rewrite_json(world.part_path("report", "B001"), lambda doc: doc["fragments"][0].update(text=doc["fragments"][0]["text"] + "\ud800"))
        assert b"\\ud800" in world.part_path("report", "B001").read_bytes()
    else:
        batch = world.batch_ids("report")[-2]  # the threat_analysis findings part
        world.rewrite_json(world.part_path("report", batch), lambda doc: doc["items"][0].update(narrative=doc["items"][0]["narrative"] + "\u202e"))
    run_refused(world, assembler, "report", 2)


def test_report_a_forbidden_character_in_a_batch_input_row_exits_2_naming_the_finding(assembler, make):
    """A findings batch input holds rows of ``threats.md`` as data. The plan pins the file by its digest, but the row is still a value taken from an input that
    isn't a part (S1P-A18), and the lead is built from it."""
    world = make("report")
    batch = world.batch_ids("report")[-2]
    world.edit_input("report", batch, lambda doc: doc["units"][0].update(threat="Session \x1b token replay"))
    res = run_refused(world, assembler, "report", 2)
    assert "S-1" in res.err, res.describe()


@pytest.mark.parametrize("where", ["the category row of an analysis unit", "the category row of a roadmap unit", "a group's member rows in a roadmap unit"])
def test_report_a_forbidden_character_nested_in_a_unit_row_exits_2_naming_the_finding(assembler, make, where):
    """T092's units nest the category-table cells under ``category_row`` and a group's member rows under ``members``, and the walk for step 10's set reaches them."""
    world = make("report", rule="rule2", groups=[("CG-1", ["T-1", "T-2"])])
    if where.startswith("the category row of an analysis"):
        batch, finding = world.section_batch("threat_analysis"), "S-1"
        edit = lambda unit: unit["category_row"].update(maestro_layer="L4\x1b")    # noqa: E731
    elif where.startswith("the category row of a roadmap"):
        batch, finding = world.section_batch("remediation_roadmap"), "S-1"
        edit = lambda unit: unit["category_row"].update(likelihood="HI" + chr(0x202E) + "GH")   # noqa: E731
    else:
        batch, finding = world.section_batch("remediation_roadmap"), "T-1"
        edit = lambda unit: unit["members"][1].update(mitigation="Sign \x00 it")   # noqa: E731
    world.edit_input("report", batch, lambda doc: edit(next(u for u in doc["units"] if u["finding_id"] == finding)))
    res = run_refused(world, assembler, "report", 2)
    assert finding in res.err, res.describe()


def rename_in_findings_batch(world, batch_id, old, new):
    """Make ``old`` read as ``new`` in one findings batch of the report: its entry in the plan, the batch input and the part, as a planner and an agent that had
    meant ``new`` would have written them."""
    def renamed(ids):
        return [new if i == old else i for i in ids]

    def edit_input(doc):
        doc["finding_ids"] = renamed(doc["finding_ids"])
        for unit in doc["units"]:
            if unit["finding_id"] == old:
                unit["finding_id"] = new

    def edit_part(doc):
        doc["finding_ids"] = renamed(doc["finding_ids"])
        for item in doc["items"]:
            if item["finding_id"] == old:
                item["finding_id"] = new

    world.edit_input("report", batch_id, edit_input)
    world.rewrite_plan("report", lambda doc: [entry.update(finding_ids=renamed(entry["finding_ids"])) for entry in doc["batches"] if entry["batch_id"] == batch_id])
    world.rewrite_json(world.part_path("report", batch_id), edit_part)


def test_report_an_analysis_item_for_a_finding_that_is_not_open_exits_2_naming_it(assembler, make):
    """E-9 is a finding that no row of Section 7 holds. Its part and its batch input agree with the plan, so only the check against the reference set sees it."""
    world = make("report")
    rename_in_findings_batch(world, world.batch_ids("report")[-2], "E-1", "E-9")
    res = run_refused(world, assembler, "report", 2)
    assert "E-9" in res.err and "not an open finding" in res.err, res.describe()


def test_report_a_critical_or_high_finding_with_no_tree_summary_exits_2_naming_it(assembler, make):
    """The batch input and the part agree that S-1 has no tree, but the merged manifest has one for it, so Section 5 would have no one-sentence summary to show."""
    world = make("report")
    batch = world.batch_ids("report")[-2]
    world.edit_input("report", batch, lambda doc: next(unit for unit in doc["units"] if unit["finding_id"] == "S-1").update(tree=False))
    world.rewrite_json(world.part_path("report", batch), lambda doc: next(item for item in doc["items"] if item["finding_id"] == "S-1").update(tree_summary=None))
    res = run_refused(world, assembler, "report", 2)
    assert "no tree summary for S-1" in res.err, res.describe()


# ---- what the file's frontmatter takes from the reference set, the manifest and threats.md (part-files.md, "The assembler's layout")

FRONT_CASES = {
    "no-baseline": (None, None, None),
    "rule1": ("baseline/threats.md", BASELINE_DATE, {"new": 0, "unchanged": 9, "updated": 0, "resolved": 0}),
    "rule2": ("baseline/threats.md", BASELINE_DATE, {"new": 4, "unchanged": 4, "updated": 1, "resolved": 1}),
}


@pytest.mark.parametrize("rule", sorted(FRONT_CASES))
def test_report_the_frontmatter_is_the_templates_shape_with_the_counts_of_the_reference_set(assembler, make, rule):
    world = make("report", rule=rule)
    report_ok(world, assembler)
    front = frontmatter_of(world.report_text)
    source, date, delta = FRONT_CASES[rule]
    assert (str(front["schema_version"]), str(front["date"]), int(front["finding_count"]), int(front["attack_tree_count"])) == ("1.1", DATE, 9, 7)
    assert str(front["source_file"]).endswith("threats.md")
    distribution = {str(level).lower(): int(count) for level, count in front["risk_distribution"].items()}
    assert [distribution[level] for level in ("critical", "high", "medium", "low")] == [3, 4, 1, 1]
    assert (front["baseline_source"], None if front["baseline_date"] is None else str(front["baseline_date"])) == (source, date)
    counts = front["delta_counts"]
    if delta is None:
        assert counts is None or all(value is None for value in counts.values()), counts
    else:
        assert {key: int(counts[key]) for key in ("new", "unchanged", "updated", "resolved")} == delta


# ---- the stage record, written on 0 (RR3; part-files.md §5)

def test_report_the_stage_record_is_the_closed_one_for_the_stage(assembler, make):
    world = make("report", rule="rule2", patterns=True, planned_chains=True, outcome=OUTCOME_WRITTEN, compliance=True)
    report_ok(world, assembler)
    record, plan = world.record("report"), read_json(world.plan_path("report"))
    assert set(record) == set(tp.KEY_SETS["stage-record"][0])
    assert (record["schema"], record["stage"], record["plan_id"]) == (tp.STAGE_RECORD_SCHEMA, "report", world.plan_id("report"))
    assert (record["status"], record["error"], record["tachi_version"]) == ("success", None, tp.VERSION)
    counts = record["counts"]
    assert set(counts) == {"units", "rendered", "narrative_fallbacks", "truncations"}
    assert counts["units"] == plan["unit_count"] and 0 < counts["rendered"] <= counts["units"] and (counts["narrative_fallbacks"], counts["truncations"]) == (0, 0)
    batches = len(plan["batches"])
    assert record["batches"] == {"planned": batches, "dispatched": batches, "done": batches, "retried": 0, "split": 0, "exhausted": 0}
    assert (record["overflow_events"], record["retries"], record["warnings"], record["undeclared_paths"]) == ([], [], [], [])
    assert {"path": "threat-report.md", "sha256": tp.file_digest(world.report_path)} in record["outputs"]  # reading: RD-13
    if "report" in tp.STAGE_AGENTS:
        tp.validate_stage_record(record)


# ---- the trees mode's output is the report mode's input

def test_report_accepts_what_the_trees_mode_leaves(assembler, make):
    world = make("trees", rule="rule2")
    trees_ok(world, assembler)
    world.build_report()  # the report plan pins the trees plan and the manifest that the assembler wrote
    report_ok(world, assembler)
    assert len(mermaid_sources(section_text(world.report_text, 5))) == 7
    assert frontmatter_of(world.report_text)["attack_tree_count"] in (7, "7")


# ---- narrative fragments: the prose sink, the slots, the fixed sentence and the cut (ADR-050 D3; T110 holds the other slot kinds)

def reword(world, key, text, batch="B001"):
    def edit(doc):
        next(fragment for fragment in doc["fragments"] if fragment["slot_key"] == key).update(text=text)

    world.rewrite_json(world.part_path("report", batch), edit)


def test_report_fragments_take_the_prose_sink_and_their_slots_resolve_against_the_reference_set(assembler, make):
    world = make("report", rule="rule2")
    reword(world, "risk_posture", "The model holds {{count:open}} open findings, {{count:critical}} of them Critical, led by {{finding:S-1}} on "
                                  "{{name:component:S-1}} & <b>bold</b>.")
    report_ok(world, assembler)
    section = section_text(world.report_text, 1)
    assert "The model holds 9 open findings, 3 of them Critical, led by S-1 on Gateway &amp; &lt;b&gt;bold&lt;/b&gt;." in section
    assert "<b>" not in section


def test_report_a_fragment_that_breaks_the_numeral_ban_takes_the_fixed_sentence_and_is_counted(assembler, make):
    world = make("report")
    reword(world, "top_threats", "There are 12 findings in all.")
    report_ok(world, assembler)
    section = section_text(world.report_text, 1)
    assert "This passage is not shown because the text the agent wrote broke the narrative rules." in section and "12 findings" not in section
    assert world.record("report")["counts"]["narrative_fallbacks"] == 1


def test_report_a_fragment_over_its_limit_is_cut_at_the_limit_and_counted(assembler, make):
    world = make("report")
    reword(world, "risk_posture", "word " * 400)  # 2,000 characters against Risk Posture's 1,500
    report_ok(world, assembler)
    assert section_text(world.report_text, 1).count("word") == 300
    assert world.record("report")["counts"]["truncations"] == 1


def test_report_a_slot_that_does_not_resolve_takes_the_fields_fixed_sentence_in_its_own_sink_and_is_counted(assembler, make):
    """``S-99`` and ``D-99`` pass the slot grammar, so each part stands. Neither is a row of the reference set, so the lookup returns ``None`` and the field falls back at
    assembly (D3's table): a fragment and a finding's narrative in the prose sink, and a roadmap cell in the cell sink. Nothing the agent wrote for them is kept."""
    world = make("report")
    reword(world, "risk_posture", "Start with {{finding:S-99}}.")
    analysis, roadmap = world.batch_ids("report")[-2:]
    world.rewrite_json(world.part_path("report", analysis), lambda doc: doc["items"][0].update(narrative="On {{name:component:S-99}} the plan is clear."))
    world.rewrite_json(world.part_path("report", roadmap), lambda doc: doc["items"][0].update(dependencies="Blocked by {{band:risk:D-99}}."))
    report_ok(world, assembler)
    text = world.report_text
    assert "This passage is not shown because the text the agent wrote broke the narrative rules." in section_text(text, 1)
    assert "No narrative is shown for this finding because the text the agent wrote broke the narrative rules." in section_text(text, 3)
    row = roadmap_rows(world)[0]
    assert row["Finding ID"] == "S-1" and row["Dependencies"] == "No dependency note is shown because the text the agent wrote broke the narrative rules."
    assert "S-99" not in text and "D-99" not in text and "Start with" not in text and "the plan is clear" not in text
    assert world.record("report")["counts"]["narrative_fallbacks"] == 3


# ---- the staged-file backstop (RD-21): the file is read back from disk and checked before it replaces anything (D4; P0-4)

BACKSTOP = {
    "a character from step 10's set": (lambda text: text.replace("## 1. ", "## 1. \x1b", 1), "U+001B"),
    "no provenance stamp": (lambda text: "\n".join(line for line in text.split("\n") if not line.startswith("<!-- tachi-provenance")), "provenance stamp"),
    "another run's provenance stamp": (lambda text: re.sub(r"input-digest=sha256:[0-9a-f]{64}", "input-digest=sha256:" + "0" * 64, text), "provenance stamp"),
    "a tree whose source differs from its file's": (lambda text: text.replace("Goal[", "Goal [", 1), "Mermaid source of S-1"),
    "sections that are not numbered in order": (lambda text: text.replace("## 3. ", "## 9. ", 1), "not numbered 1 to 8 in order"),   # six sections, the roadmap and the appendix
}


@pytest.mark.parametrize("case", sorted(BACKSTOP))
def test_report_a_staged_file_that_fails_its_check_exits_4_and_replaces_nothing(assembler, make, monkeypatch, case):
    """Through a part no such text can be built, because the intake refuses what each check looks for, so the builder is replaced by one that damages its text. The
    staged copy stays under the plan for diagnosis, and the agent's report, every earlier file and the stage record are as they were."""
    mutate, expected = BACKSTOP[case]
    world = make("report")
    world.report_path.write_text("# Threat Report\n\nAn agent wrote this.\n", encoding="utf-8")
    module = assembler.load()
    real = module._assemble
    monkeypatch.setattr(module, "_assemble", lambda *args: mutate(real(*args)))
    before = tree_state(world.out)
    res = world.run(assembler, "report")
    assert res.code == 4, res.describe()
    assert_failure(res, "report", world.plan_id("report"))
    assert "a completeness or parity check failed on the staged files" in res.err and expected in res.err, res.describe()
    after = tree_state(world.out)
    assert all(after.get(path) == digest for path, digest in before.items()), "the agent's report and every other file stand"
    assert {path for path in after if path not in before} == {".tachi-build/report/%s/staged/threat-report.md" % world.plan_id("report")}
    assert not world.record_path("report").exists()


# =============================================================================
# 5. T110, contingency O-gamma: the richer `report` payload. Its validator cases, then what the assembler lays out from it (part-files.md, "Stage payload: report")
#
# Section 4 above holds what T109 lists: the numbering, Section 5, Section 6's outline, the roadmap's rows, the frontmatter, the sinks and the checks. This section holds the
# payload's content: the leads, the category summaries, the pattern subsections, the roadmap's group rows, the appendix, Section 9, Section 1's timeline and the slots.
# The readings, each pinned here and listed in the lane's results file:
#
# * RD-22, the unit rows. A findings batch's unit row holds Section 7's row and the category-table row, "decoded" (part-files.md), and the contract names no key for
#   the second. T092's planner writes it under ``category_row``, with ``threats-md``'s item keys inside (``tachi_parts.THREATS_MD_SECTIONS``): ``status``,
#   ``component``, ``maestro_layer``, ``threat``, ``likelihood``, ``impact``, ``risk_level``, ``mitigation`` and, in the two AI tables, ``owasp_reference``. The
#   harness builds its rows that way, and the assembler reads ``category_row``'s ``maestro_layer``, ``likelihood``, ``impact`` and ``owasp_reference`` and no other
#   cell. A column that its table lacks is ``""`` there (the planner's ``row.get(header, "")``), a finding with no row in any table has ``{}``, and the lead shows a
#   dash for both. ``tree`` (``threat_analysis``), and ``group_id`` and ``members`` (a group's primary in ``remediation_roadmap``) are the planner's other unit keys.
# * RD-23, the lead is ``**<ID>**: <component> | **MAESTRO Layer**: <layer> | **Likelihood**: <value> | **Impact**: <value> | **Risk Level**: <level>``, then
#   `` | **Status**: <status>`` in a baseline run, on one line before the narrative.
# * RD-24, a ``ref`` slot. Its argument is one of the taxonomy IDs of the item's own finding in a findings part, and of any finding that has a unit row in a section
#   fragment. A finding's IDs are the tokens of its OWASP Reference cell that start with a letter and hold a digit, and its MAESTRO layer's code. Any other argument
#   takes the field's fixed sentence.
# * RD-25, the plan against the reference set. The analysis items are exactly the narrated findings, the summary units exactly the categories that hold a summarized
#   finding, the pattern units exactly the patterns that Section 7 holds, and the delta part is there exactly when the run has a baseline, or the run is exit 2.
# * RD-26, a group's roadmap row. Its Mitigation is ``<ID>: <mitigation>`` for each member, in member order, joined by ``; ``, each mitigation as the reference set
#   reads it, and its Dependencies are ``Correlated: <IDs> (<group>).``, then the item's note when it has one.
# * RD-27, the forms that the contract leaves to the assembler: Section 7's intro sentence, the appendix's rows (Section number, then the heading's text) and
#   Section 9's tables, as the template shows them.
# =============================================================================

PATTERN_OF = {"LLM-1": "trust_exploitation", "OI-1": "communication_vulnerability", "T-2": "communication_vulnerability", "AG-1": "agent_collusion",
              "I-1": "emergent_behavior", "D-1": "temporal_attack", "E-1": "resource_competition", "S-1": "multiple"}
# Subsections, in the order that FR-013 gives them: LLM-1 is Critical, so Trust Exploitation is first. Communication Vulnerabilities and Agent Collusion share the
# High band, and the first has two findings. Emergent Behavior is third in that band because Agent Collusion precedes it in the enum, with the same count.
PATTERN_ORDER = ["trust_exploitation", "communication_vulnerability", "agent_collusion", "emergent_behavior", "temporal_attack", "resource_competition"]
RICH = dict(rule="rule2", pattern_of=PATTERN_OF, planned_chains=True, outcome=OUTCOME_WRITTEN, compliance=True, themes=2, overview=True)
SCENARIOS = {
    "a run of nine": RICH,
    "a run of thirty-four": dict(RICH, findings=big_findings("rule2")),
    "findings parts of three": dict(RICH, per_report_batch=3),
    "a first run": dict(RICH, rule="no-baseline"),
}
SECTION_OF_KEY = {"risk_posture": "exec_summary", "top_threats": "exec_summary", "key_recommendations": "exec_summary", "compliance": "exec_summary",
                  "system_context": "architecture_overview", "trust_boundaries": "architecture_overview", "overview": "threat_categories",
                  "multi": "agentic_patterns", "progress": "delta_summary"}


def section_of_key(key):
    """The section part that holds fragment ``key``."""
    if key in SECTION_OF_KEY:
        return SECTION_OF_KEY[key]
    return {"category": "threat_categories", "summary": "threat_categories", "theme": "cross_cutting_themes", "chain": "attack_chains",
            "pattern": "agentic_patterns"}[key.partition(".")[0]]


def reword_in(world, key, text):
    """Replace the text of fragment ``key`` in the section part that holds it."""
    reword(world, key, text, batch=world.section_batch(section_of_key(key)))


def reword_item(world, section, finding_id, **fields):
    """Change fields of one finding's item in ``section``'s findings part (the part that holds it, when the section has several)."""
    for batch_id in world.batch_ids("report"):
        if read_json(world.input_path("report", batch_id))["units"][0]["section"] != section:
            continue
        part = read_json(world.part_path("report", batch_id))
        for item in part["items"]:
            if item["finding_id"] == finding_id:
                item.update(fields)
                write_json(world.part_path("report", batch_id), part)
                return
    raise AssertionError("no %s item for %s" % (section, finding_id))


def validate_batch(world, batch_id):
    """``tachi_parts.read_part`` on a report batch's part against its batch input's units: the check that D3's guard repeats for each ``done`` batch."""
    entry = next(e for e in read_json(world.plan_path("report"))["batches"] if e["batch_id"] == batch_id)
    units = read_json(world.input_path("report", batch_id))["units"]
    return tp.read_part(world.part_path("report", batch_id), world.out, world.plan_id("report"), batch_id, "report", STAGE_AGENT["report"], entry["finding_ids"], units)


# ---- the validator cases: what the shared validators hold the richer payload to (T091's key sets), shown on this module's own parts

@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_validator_every_part_of_the_richer_payload_passes_the_shared_validators_with_nothing_cut_or_replaced(make, scenario):
    world = make("report", **SCENARIOS[scenario])
    seen = set()
    for batch_id in world.batch_ids("report"):
        result = validate_batch(world, batch_id)
        assert result.state == "done", (batch_id, result.detail)
        assert result.counts == {"narrative_fallbacks": 0, "truncations": 0} and result.flags == {}, "the report prints no flag, and nothing here is cut"
        seen.add(read_json(world.input_path("report", batch_id))["units"][0]["section"])
    assert seen == {section for section, _ in tp.REPORT_PARTS} - (set() if world.has_baseline else {"delta_summary"}), "every part of the contract's table is planned"


def test_validator_a_findings_part_holds_the_contracts_item_keys_and_a_section_part_holds_no_item_and_no_finding(make):
    world = make("report", **RICH)
    keys = {"threat_analysis": set(tp.KEY_SETS["analysis-item"][0]), "remediation_roadmap": set(tp.KEY_SETS["roadmap-item"][0])}
    assert keys == {"threat_analysis": {"finding_id", "narrative", "tree_summary"}, "remediation_roadmap": {"finding_id", "effort", "dependencies"}}
    for batch_id in world.batch_ids("report"):
        part = read_json(world.part_path("report", batch_id))
        section = read_json(world.input_path("report", batch_id))["units"][0]["section"]
        if dict(tp.REPORT_PARTS)[section] == "findings":
            assert part["items"] and part["fragments"] == [] and part["finding_ids"] == [item["finding_id"] for item in part["items"]]
            assert all(set(item) == keys[section] for item in part["items"]), section
        else:
            assert part["items"] == [] and part["finding_ids"] == [] and part["fragments"], section
            assert all(set(fragment) == set(tp.KEY_SETS["fragment"][0]) for fragment in part["fragments"])
            assert all(tp.report_fragment_limit(section, fragment["slot_key"]) is not None for fragment in part["fragments"]), "each key has a limit"


def drop_fragment(key):
    return lambda part: part.update(fragments=[f for f in part["fragments"] if f["slot_key"] != key])


def add_fragment(key, text="A passage of prose."):
    return lambda part: part["fragments"].append({"slot_key": key, "text": text})


def first_item(**fields):
    return lambda part: part["items"][0].update(fields)


def item_of(finding_id, **fields):
    return lambda part: next(i for i in part["items"] if i["finding_id"] == finding_id).update(fields)


def renumber_theme(old, new):
    return lambda part: [f.update(slot_key=f["slot_key"].replace("theme.%d." % old, "theme.%d." % new)) for f in part["fragments"]]


# Each case changes one thing in a part that passes, and the shared validator refuses the result. ``section`` names the part. RICH plans every part, a
# Critical finding S-1 with a tree and a Medium finding D-1 with none, two themes, two chains and all six patterns with ``multi``.
VALIDATOR_CASES = {
    "a required paragraph is missing": ("exec_summary", drop_fragment("top_threats")),
    "a paragraph that the batch did not plan": ("exec_summary", add_fragment("system_context")),
    "a key twice": ("exec_summary", add_fragment("risk_posture")),
    "a fragment with another key": ("exec_summary", lambda part: part["fragments"][0].update(note="x")),
    "a fragment with no text": ("exec_summary", lambda part: part["fragments"][0].pop("text")),
    "text of whitespace": ("exec_summary", lambda part: part["fragments"][0].update(text="  \n ")),
    "an item in a section part": ("exec_summary", lambda part: part.update(items=[{"finding_id": "S-1"}])),
    "a finding ID in a section part": ("exec_summary", lambda part: part.update(finding_ids=["S-1"])),
    "a category with an open finding and no paragraph": ("threat_categories", drop_fragment("category.llm")),
    "a summary that no unit planned": ("threat_categories", add_fragment("summary.llm")),
    "a category key that no category has": ("threat_categories", add_fragment("category.bogus")),
    "a category key with a band": ("threat_categories", add_fragment("category.llm.high")),
    "a theme title with no body": ("cross_cutting_themes", drop_fragment("theme.2.body")),
    "themes numbered with a gap": ("cross_cutting_themes", renumber_theme(2, 3)),
    "a seventh theme": ("cross_cutting_themes", lambda part: part["fragments"].extend([{"slot_key": "theme.7.title", "text": "T"}, {"slot_key": "theme.7.body", "text": "B"}])),
    "a chain that no unit planned": ("attack_chains", add_fragment("chain.CHAIN-009")),
    "a planned chain with no paragraph": ("attack_chains", drop_fragment("chain.CHAIN-002")),
    "a chain key that isn't a chain ID": ("attack_chains", add_fragment("chain.chain-001")),
    "a pattern paragraph that is missing": ("agentic_patterns", drop_fragment("pattern.temporal_attack")),
    "a pattern key that isn't one of the six": ("agentic_patterns", add_fragment("pattern.multiple")),
    "the multi paragraph missing": ("agentic_patterns", drop_fragment("multi")),
    "no progress paragraph": ("delta_summary", drop_fragment("progress")),
    "a progress paragraph twice": ("delta_summary", add_fragment("progress")),
    "a fragment in a findings part": ("threat_analysis", lambda part: part.update(fragments=[{"slot_key": "risk_posture", "text": "x"}])),
    "a tree summary for a finding with no tree": ("threat_analysis", item_of("D-1", tree_summary="A summary of nothing.")),
    "no tree summary for a finding that has a tree": ("threat_analysis", item_of("S-1", tree_summary=None)),
    "an empty narrative": ("threat_analysis", first_item(narrative="")),
    "a narrative that isn't text": ("threat_analysis", first_item(narrative=["a", "b"])),
    "a lead that the assembler writes": ("threat_analysis", first_item(risk_level="Critical")),
    "an item for a finding that the batch did not plan": ("threat_analysis", lambda part: part["items"].append(dict(part["items"][0], finding_id="S-9"))),
    "an effort that is none of the three": ("remediation_roadmap", first_item(effort="Huge")),
    "an effort in lower case": ("remediation_roadmap", first_item(effort="low")),
    "no dependencies key": ("remediation_roadmap", lambda part: part["items"][0].pop("dependencies")),
    "empty dependencies": ("remediation_roadmap", first_item(dependencies="")),
    "a narrative in a roadmap item": ("remediation_roadmap", first_item(narrative="x")),
    "another plan's part": ("exec_summary", lambda part: part.update(plan_id=OTHER_ID)),
    "another batch's part": ("remediation_roadmap", lambda part: part.update(batch_id="B099")),
}


@pytest.mark.parametrize("case", sorted(VALIDATOR_CASES))
def test_validator_a_part_that_breaks_the_richer_payloads_closed_keys_or_values_is_invalid_and_the_assembler_exits_2(assembler, make, case):
    section, mutate = VALIDATOR_CASES[case]
    world = make("report", **RICH)
    batch = world.section_batch(section)
    world.rewrite_json(world.part_path("report", batch), mutate)
    assert validate_batch(world, batch).state == "invalid", "premise: the shared validator refuses it"
    res = run_refused(world, assembler, "report", 2)
    assert "the part of batch %s is invalid" % batch in res.err, res.describe()


def test_validator_no_findings_part_spans_two_sections_and_the_appendix_has_no_part(assembler, make):
    """T088's ruling, O-gamma: a part holds the units of one report section. The contract's table has two findings sections, each with a part of its own, and the
    appendix is code alone."""
    assert [section for section, kind in tp.REPORT_PARTS if kind == "findings"] == ["threat_analysis", "remediation_roadmap"]
    assert "appendix" not in dict(tp.REPORT_PARTS)
    world = make("report", rule="rule2")
    batch = world.section_batch("threat_analysis")
    world.edit_input("report", batch, lambda doc: doc["units"][-1].update(section="remediation_roadmap"))   # one batch, units of two sections
    assert validate_batch(world, batch).state == "invalid"
    res = run_refused(world, assembler, "report", 2)
    assert "the part of batch %s is invalid" % batch in res.err, res.describe()
    other = make("report", rule="rule2")
    batch = other.section_batch("remediation_roadmap")
    other.edit_input("report", batch, lambda doc: [unit.update(section="appendix") for unit in doc["units"]])   # the appendix has no part
    assert validate_batch(other, batch).state == "invalid"
    res = run_refused(other, assembler, "report", 2)
    assert "the part of batch %s is invalid" % batch in res.err, res.describe()


@pytest.mark.parametrize("units", ["a unit that is not an object", "no tree flag in an analysis unit", "a tree flag that is not a boolean"])
def test_validator_a_findings_batch_input_whose_units_do_not_fit_the_plan_makes_its_part_invalid(assembler, make, units):
    world = make("report", rule="rule2")
    batch = world.section_batch("threat_analysis")

    def damage(doc):
        if units == "a unit that is not an object":
            doc["units"][0] = "S-1"
        elif units == "no tree flag in an analysis unit":
            doc["units"][0].pop("tree")
        else:
            doc["units"][0]["tree"] = 1

    world.edit_input("report", batch, damage)
    assert validate_batch(world, batch).state == "invalid"
    run_refused(world, assembler, "report", 2)


@pytest.mark.parametrize("text", ["There are 12 findings in all.", "{{count:bogus}}", "{{pct:spoofing}}", "{{band:severity}}", "An unterminated {{count:open"])
def test_validator_a_narrative_that_breaks_the_slot_grammar_or_the_numeral_ban_takes_the_fixed_sentence_and_the_part_stays_done(assembler, make, text):
    """Step 11, shown through a section fragment, a finding's narrative and a roadmap note: the part is done, the field has its fixed sentence, and the report
    counts it."""
    world = make("report", rule="rule2")
    reword_in(world, "top_threats", text)
    reword_item(world, "threat_analysis", "S-1", narrative=text)
    reword_item(world, "remediation_roadmap", "S-1", dependencies=text)
    for batch_id in (world.section_batch("exec_summary"), world.section_batch("threat_analysis"), world.section_batch("remediation_roadmap")):
        result = validate_batch(world, batch_id)
        assert result.state == "done" and result.counts["narrative_fallbacks"] == 1, (batch_id, result.detail)
    report_ok(world, assembler)
    sentences = tp.REPORT_FALLBACKS
    assert sentences["fragment"] in section_text(world.report_text, 1)
    assert sentences["narrative"] in section_text(world.report_text, 3)
    assert next(r for r in roadmap_rows(world) if r["Finding ID"] == "S-1")["Dependencies"] == sentences["dependencies"]
    assert world.record("report")["counts"]["narrative_fallbacks"] == 3


# ---- helpers for what the assembler lays out

PATTERN_REFERENCE = REPO_ROOT / ".claude" / "skills" / "tachi-shared" / "references" / "maestro-agentic-patterns-shared.md"


def shared_patterns():
    """``[(display name, definition)]`` of the six canonical patterns, from Section 1 of the shared reference, in its order (1.1 to 1.6)."""
    text = PATTERN_REFERENCE.read_text(encoding="utf-8")
    body = text.split("## Section 1: Six Canonical Pattern Definitions", 1)[1].split("\n## Section 2", 1)[0]
    return [(name.strip(), definition.strip()) for name, definition in re.findall(r"(?m)^### 1\.[1-6] (.+)\n\n\*\*Definition\*\*: (.+)$", body)]


def template_subsections():
    """The template's eight Section 3 headings, ``3.1 Spoofing`` to ``3.8 LLM Threats``."""
    found = re.findall(r"(?m)^### (3\.[1-8] .+)$", TEMPLATE.read_text(encoding="utf-8"))
    assert len(found) == 8
    return found


def subsection_lines(text, level, title):
    """The lines under the ATX heading of ``level`` whose title starts with ``title``, up to the next heading of that level or a higher one."""
    lines, heads = text.split("\n"), atx_headings(text)
    for k, (n, lvl, found) in enumerate(heads):
        if lvl == level and found.startswith(title):
            end = next((m for m, other, _ in heads[k + 1:] if other <= level), len(lines))
            return lines[n + 1:end]
    raise AssertionError("no heading %r of level %d" % (title, level))


def nonblank(lines):
    return [line for line in lines if line.strip()]


def lead_line(f, baseline=True, **cells):
    """RD-23: the lead of a narrated finding. ``cells`` overrides the category-table values (``layer``, ``likelihood``, ``impact``), as a dash does when its table lacks one."""
    values = dict({"layer": f.layer, "likelihood": f.likelihood, "impact": f.impact}, **cells)
    fields = ["**%s**: %s" % (f.id, f.component), "**MAESTRO Layer**: %s" % values["layer"], "**Likelihood**: %s" % values["likelihood"],
              "**Impact**: %s" % values["impact"], "**Risk Level**: %s" % f.risk]
    if baseline:
        fields.append("**Status**: %s" % f.status)
    return " | ".join(fields)


def open_order(findings):
    """Sections 3 and 4's order: the eight category tables in turn, and S-2 order within one."""
    return sorted((f.id for f in findings), key=lambda i: (CATEGORY_ORDER.index(category_of(i)), s2(i)))


# ---- Section 1: the Remediation Timeline, in the form that extract-report-data.py reads

TIER_OF = (("Critical", "Immediate"), ("High", "Short-term"), ("Medium", "Medium-term"), ("Low", "Backlog"), ("Note", "Backlog"))


def expected_timeline(findings):
    """One line for each band that has an open finding: Immediate for Critical, Short-term for High, Medium-term for Medium, and Backlog for Low and for Note."""
    return ["- **%s** (%d %s findings)" % (tier, count, level) for level, tier in TIER_OF for count in [sum(1 for f in findings if f.risk == level)] if count]


@pytest.mark.parametrize("scenario", ["a run of nine", "a run of thirty-four"])
def test_section_1_the_remediation_timeline_has_one_line_for_each_band_with_open_findings_and_the_extractor_reads_it(assembler, make, extract_report_data, scenario):
    world = make("report", **SCENARIOS[scenario])
    report_ok(world, assembler)
    text = world.report_text
    expected = expected_timeline(world.findings)
    assert nonblank(subsection_lines(section_text(text, 1), 3, "Remediation Timeline")) == expected
    assert len(expected) == (4 if scenario == "a run of nine" else 5), "the thirty-four hold a Note finding, which the nine don't"
    read = extract_report_data.parse_threat_report_md(text)["remediation_timeline"]
    assert read == [{"timeline": tier, "count": sum(1 for f in world.findings if f.risk == level), "severity": level}
                    for level, tier in TIER_OF if any(f.risk == level for f in world.findings)], "the same lines, read as the PDF's extractor reads them"


def test_section_1_the_timeline_is_code_and_follows_the_reference_set_whatever_the_agent_wrote(assembler, make):
    world = make("report", rule="rule2")
    reword_in(world, "key_recommendations", "- **Immediate** (many Critical findings)")   # an agent's own timeline line is only prose
    report_ok(world, assembler)
    lines = subsection_lines(section_text(world.report_text, 1), 3, "Remediation Timeline")
    assert nonblank(lines) == expected_timeline(world.findings)


def test_section_1_names_its_subsections_as_the_extractor_reads_them_and_in_order(assembler, make):
    world = make("report", compliance=True)
    report_ok(world, assembler)
    headings = [title for _, level, title in atx_headings(section_text(world.report_text, 1)) if level == 3]
    assert headings == ["Risk Posture", "Top 5 Threats by Business Impact", "Key Recommendations", "Compliance Relevance", "Remediation Timeline"]
    for key, title in (("risk_posture", "Risk Posture"), ("top_threats", "Top 5 Threats by Business Impact"), ("key_recommendations", "Key Recommendations"),
                       ("compliance", "Compliance Relevance")):
        assert nonblank(subsection_lines(section_text(world.report_text, 1), 3, title)) == [marker("exec_summary", key)], title


# ---- Section 3: the subsections, the leads and the narratives

def test_section_3_has_the_eight_subsections_on_every_run_and_an_empty_one_says_so(assembler, make):
    world = make("report", rule="no-op")   # D-1 and E-1 only
    report_ok(world, assembler)
    section = section_text(world.report_text, 3)
    template = template_subsections()
    assert [title for _, level, title in atx_headings(section) if level == 3] == template
    held = {category_of(f.id) for f in world.findings}
    assert held == {"denial_of_service", "elevation_of_privilege"}
    for index, key in enumerate(CATEGORY_ORDER):
        body = "\n".join(subsection_lines(section, 3, template[index]))
        sentence = "No %s threats were identified in this threat model." % CATEGORY_TITLE[key]
        assert (sentence in body) is (key not in held), key
        if key in held:
            assert "Marker narrative for" in body


@pytest.mark.parametrize("rule,baseline", [("rule2", True), ("rule1", True), ("no-baseline", False)])
def test_section_3_each_narrated_finding_has_a_lead_from_its_category_table_row_and_then_its_narrative(assembler, make, rule, baseline):
    world = make("report", rule=rule)
    report_ok(world, assembler)
    lines = section_text(world.report_text, 3).split("\n")
    for f in world.findings:
        at = [n for n, line in enumerate(lines) if line == lead_line(f, baseline)]
        assert len(at) == 1, (f.id, "the lead is one line: its ID, component, layer, likelihood, impact and risk level, and its status in a baseline run")
        assert lines[at[0] + 1] == "" and lines[at[0] + 2] == "Marker narrative for %s." % f.id
    assert ("**Status**" in "\n".join(lines)) is baseline


def test_section_3_a_lead_shows_a_dash_for_a_value_that_its_category_table_lacks(assembler, make):
    """RD-22: a table without the column gives ``""`` in ``category_row``, and the lead still has the field."""
    world = make("report", rule="rule2", drop_row_keys=("maestro_layer", "likelihood"))
    assert read_json(world.input_path("report", world.section_batch("threat_analysis")))["units"][0]["category_row"]["maestro_layer"] == ""
    report_ok(world, assembler)
    lines = section_text(world.report_text, 3).split("\n")
    for f in world.findings:
        assert lead_line(f, True, layer=DASH, likelihood=DASH) in lines, f.id
    assert "**MAESTRO Layer**: %s |" % DASH in "\n".join(lines) and "**Impact**: HIGH" in "\n".join(lines), "only the missing cells are dashes"


@pytest.mark.parametrize("how", ["no category row at all", "the cells at the top of the unit, not in category_row"])
def test_section_3_the_lead_reads_the_category_cells_from_category_row_and_nowhere_else(assembler, make, how):
    """A finding with no row in any category table has ``{}`` there, and a lead made of dashes. The cells are read from ``category_row`` alone, as T092 writes them, so
    the same cells at the top of the unit are not read."""
    world = make("report", rule="rule2")
    batch = world.section_batch("threat_analysis")

    def damage(doc):
        unit = next(u for u in doc["units"] if u["finding_id"] == "S-1")
        cells = unit.pop("category_row")
        if how == "no category row at all":
            unit["category_row"] = {}
        else:
            unit.update(cells)

    world.edit_input("report", batch, damage)
    report_ok(world, assembler)
    f = next(f for f in world.findings if f.id == "S-1")
    assert lead_line(f, True, layer=DASH, likelihood=DASH, impact=DASH) in section_text(world.report_text, 3).split("\n")


def test_section_3_a_lead_cell_takes_the_cell_sink(assembler, make):
    """The lead is built from cells of rendered text: the component from Section 7 (stored escaped, read decoded) and the layer from the batch input (decoded). A
    pipe or a tag in either stays text, and can't split the line."""
    findings = [f._replace(component="Gate &#124; &lt;b&gt;way&lt;/b&gt;") if f.id == "S-1" else f for f in findings_for("rule2")]
    world = make("report", rule="rule2", findings=findings)
    world.edit_input("report", world.section_batch("threat_analysis"), lambda doc: next(u for u in doc["units"] if u["finding_id"] == "S-1")["category_row"].update(
        maestro_layer="L4 | <i>x</i>"))
    report_ok(world, assembler)
    lead = next(line for line in section_text(world.report_text, 3).split("\n") if line.startswith("**S-1**: "))
    assert "<b>" not in lead and "<i>" not in lead, lead
    assert lead.startswith("**S-1**: Gate &#124; &lt;b&gt;way&lt;/b&gt; | **MAESTRO Layer**: L4 &#124; &lt;i&gt;x&lt;/i&gt; | **Likelihood**: HIGH"), lead
    assert lead.count(" | ") == 5, "the lead's five delimiters and no more"


def test_section_3_a_subsection_holds_its_category_paragraph_then_its_findings_in_s2_order(assembler, make):
    world = make("report", rule="rule2", overview=True)
    report_ok(world, assembler)
    section = section_text(world.report_text, 3)
    first = section.index("### 3.1")
    overview = marker("threat_categories", "overview")
    assert overview in section[:first] and section.count(overview) == 1, "the overview is Section 3's, before the first subsection"
    template, by_id = template_subsections(), {f.id: f for f in world.findings}
    for index, key in enumerate(CATEGORY_ORDER):
        ids = [f.id for f in sorted(world.findings, key=lambda f: s2(f.id)) if category_of(f.id) == key]
        body = nonblank(subsection_lines(section, 3, template[index]))
        if not ids:
            assert body == ["No %s threats were identified in this threat model." % CATEGORY_TITLE[key]], key
            continue
        expected = [marker("threat_categories", "category." + key)]
        for i in ids:
            expected += [lead_line(by_id[i]), "Marker narrative for %s." % i]
        assert body == expected, key


# ---- more than 30 open findings: the Medium, Low and Note findings of a category are one summary (T088)

def test_a_run_of_more_than_30_narrates_its_critical_and_high_findings_and_summarizes_the_rest_by_category(assembler, make):
    world = make("report", **SCENARIOS["a run of thirty-four"])
    report_ok(world, assembler)
    section = section_text(world.report_text, 3)
    narrated = set(world.rule_narrated())
    assert len(world.findings) == 34 and narrated == {f.id for f in world.findings if f.risk in ("Critical", "High")} and len(narrated) == 7
    leads = re.findall(r"(?m)^\*\*([A-Z]+-[0-9]+)\*\*: ", section)
    assert sorted(leads, key=s2) == sorted(narrated, key=s2), "a lead for each narrated finding and for no other"
    for f in world.findings:
        assert ("Marker narrative for %s." % f.id in section) is (f.id in narrated), f.id
    assert world.summary_categories() == [c for c in CATEGORY_ORDER if c != "llm"], "every category but LLM holds a summarized finding"
    template = template_subsections()
    for index, key in enumerate(CATEGORY_ORDER):
        body = nonblank(subsection_lines(section, 3, template[index]))
        summary = marker("threat_categories", "summary." + key)
        own = [f for f in sorted(world.findings, key=lambda f: s2(f.id)) if category_of(f.id) == key and f.id in narrated]
        expected = [marker("threat_categories", "category." + key)]
        for f in own:
            expected += [lead_line(f), "Marker narrative for %s." % f.id]
        if key != "llm":
            expected.append(summary)
        assert body == expected, "the category paragraph, each narrated finding, then the summary: " + key
    assert sum(section.count(marker("threat_categories", "summary." + key)) for key in CATEGORY_ORDER) == 7


def test_a_run_of_more_than_30_still_lists_every_finding_in_the_roadmap_and_the_appendix(assembler, make):
    world = make("report", **SCENARIOS["a run of thirty-four"])
    report_ok(world, assembler)
    text = world.report_text
    by_id = {f.id: f for f in world.findings}
    assert [row["Finding ID"] for row in roadmap_rows(world)] == sorted(
        by_id, key=lambda i: (RISK_RANK[by_id[i].risk], by_id[i].component.casefold(), by_id[i].component, s2(i))), "one row for each of the 34, by risk, component and S-2"
    number = title_number(text, "Appendix")
    rows = tachi_parsers.parse_markdown_table(text, "## %d. Appendix: Finding Reference" % number)
    template = template_subsections()
    in_section_3 = {row["Finding ID"]: row["Heading Reference"] for row in rows if int(row["Report Section"]) == 3}
    assert in_section_3 == {f.id: template[CATEGORY_ORDER.index(category_of(f.id))] for f in world.findings}, "the appendix puts a summarized finding in its subsection"
    assert {row["Finding ID"] for row in rows} == {f.id for f in world.findings}, "zero finding loss"


def named(ids, limit=5):
    """How the assembler names a set in a message: the first few, then ``and N more``."""
    return ", ".join(ids[:limit]) + (" and %d more" % (len(ids) - limit) if len(ids) > limit else "")


@pytest.mark.parametrize("left_out", ["D-1", "E-1"])
def test_a_plan_that_leaves_out_a_narrated_finding_is_exit_2_naming_both_sets(assembler, make, left_out):
    """RD-25. The reference set says that D-1 (Medium) and E-1 (Low) are narrated in a run of at most 30, but no analysis part holds an item for one. The report
    would print no lead and no narrative for it, and the appendix would still show its Section 3 row. (Neither has a tree, so the tree-summary check doesn't meet it first.)"""
    world = make("report", rule="rule2", flaws=("no-item:" + left_out,))
    held = [i for i in world.rule_narrated() if i != left_out]
    res = run_refused(world, assembler, "report", 2)
    assert "the analysis parts hold items for %s, and Section 7's narration rule gives %s" % (named(held), named(world.rule_narrated())) in res.err, res.describe()
    assert "Remedy: re-run Phase 5, so that the report plan is made over this threats.md" in res.err


def test_a_plan_that_narrates_a_finding_that_the_rule_summarizes_is_exit_2(assembler, make):
    """A run of 34: D-1 (Medium) is summarized, so an item for it means a plan that was made over another reference set."""
    world = make("report", **SCENARIOS["a run of thirty-four"])
    batch = world.section_batch("threat_analysis")
    item = {"finding_id": "D-1", "narrative": "Marker narrative for {{finding:D-1}}.", "tree_summary": None}   # as a planner that narrated D-1 would have written it
    row = world.finding_row("threat_analysis", "D-1", tree=False)
    world.edit_input("report", batch, lambda doc: (doc["units"].append(row), doc["finding_ids"].append("D-1")))
    world.rewrite_plan("report", lambda doc: next(e for e in doc["batches"] if e["batch_id"] == batch)["finding_ids"].append("D-1"))
    world.rewrite_json(world.part_path("report", batch), lambda doc: (doc["items"].append(item), doc["finding_ids"].append("D-1")))
    assert validate_batch(world, batch).state == "done", "premise: the part is valid, so only the comparison with the reference set refuses it"
    res = run_refused(world, assembler, "report", 2)
    held = sorted(world.rule_narrated() + ["D-1"], key=s2)
    assert "the analysis parts hold items for %s, and Section 7's narration rule gives %s" % (named(held), named(world.rule_narrated())) in res.err, res.describe()


@pytest.mark.parametrize("case", ["no-summary:spoofing", "extra-summary:llm"])
def test_a_plan_whose_category_summaries_are_not_the_categories_with_a_summarized_finding_is_exit_2(assembler, make, case):
    world = make("report", **dict(SCENARIOS["a run of thirty-four"], flaws=(case,)))
    wanted = [c for c in CATEGORY_ORDER if c != "llm"]
    res = run_refused(world, assembler, "report", 2)
    assert "the report plan holds category summaries for %s, and Section 7 has summarized findings in %s" % (
        named(world.summary_categories()), named(wanted)) in res.err, res.describe()


def test_a_plan_with_a_summary_in_a_run_that_summarizes_nothing_is_exit_2(assembler, make):
    world = make("report", rule="rule2", flaws=("extra-summary:spoofing",))
    res = run_refused(world, assembler, "report", 2)
    assert "the report plan holds category summaries for spoofing, and Section 7 has summarized findings in no category" in res.err, res.describe()


@pytest.mark.parametrize("flaw,kwargs", [
    ("no-patterns", RICH), ("no-multi", RICH), ("extra-multi", dict(RICH, pattern_of={"AG-1": "agent_collusion"})), ("extra-patterns", dict(rule="rule2")),
])
def test_a_plan_whose_pattern_units_are_not_the_patterns_that_section_7_holds_is_exit_2(assembler, make, flaw, kwargs):
    world = make("report", **dict(kwargs, flaws=(flaw,)))
    res = run_refused(world, assembler, "report", 2)
    assert "the report plan holds pattern units " in res.err and ", and Section 7 gives " in res.err, res.describe()
    assert ("holds pattern units none," in res.err) is (flaw == "no-patterns")
    assert ("Section 7 gives none" in res.err) is (flaw == "extra-patterns")


@pytest.mark.parametrize("flaw,kwargs,message", [
    ("no-delta", RICH, "the report plan holds no delta summary, and the run has a baseline"),
    ("extra-delta", dict(rule="no-baseline"), "the report plan holds a delta summary, and the run has no baseline"),
])
def test_a_plan_that_holds_a_delta_summary_only_for_a_run_with_a_baseline_or_it_is_exit_2(assembler, make, flaw, kwargs, message):
    world = make("report", **dict(kwargs, flaws=(flaw,)))
    res = run_refused(world, assembler, "report", 2)
    assert message in res.err, res.describe()


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_a_plan_that_agrees_with_the_reference_set_is_never_refused(assembler, make, scenario):
    """The comparison is not a new way to fail: each scenario of this section is one that the contract plans, and it assembles."""
    world = make("report", **SCENARIOS[scenario])
    report_ok(world, assembler)


# ---- Section 4: a theme's cited findings reach the appendix

def appendix_rows(world):
    """The appendix's rows as ``[(finding ID, section number, heading)]``, read as every later reader reads a table."""
    text = world.report_text
    rows = tachi_parsers.parse_markdown_table(text, "## %d. Appendix: Finding Reference" % title_number(text, "Appendix"))
    return [(row["Finding ID"], int(row["Report Section"]), row["Heading Reference"]) for row in rows]


def test_section_4_a_theme_that_cites_findings_through_finding_slots_places_them_in_the_appendix_under_its_own_heading(assembler, make):
    world = make("report", rule="rule2", themes=2)
    reword_in(world, "theme.1.body", "Both {{finding:S-1}} and {{finding:T-1}} start at {{name:component:S-1}}.")
    reword_in(world, "theme.2.body", "Here {{finding:AG-1}} meets {{finding:S-99}}.")   # S-99 isn't in the reference set, so the whole body takes the fixed sentence
    report_ok(world, assembler)
    section = section_text(world.report_text, 4)
    assert "Both S-1 and T-1 start at Gateway." in section and tp.REPORT_FALLBACKS["fragment"] in section and "Here AG-1" not in world.report_text
    assert {row for row in appendix_rows(world) if row[1] == 4} == {("S-1", 4, "Theme 1: Marker for theme title one."), ("T-1", 4, "Theme 1: Marker for theme title one.")}, \
        "a body that shows the fixed sentence discusses no finding, so it places none"
    assert world.record("report")["counts"]["narrative_fallbacks"] == 1


# ---- Section 6: the chains from the chain file

def test_section_6_a_chain_holds_its_facts_its_narrative_its_control_the_disclaimer_and_its_members_from_the_chain_file(assembler, make):
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    report_ok(world, assembler)
    section = section_text(world.report_text, 6)
    disclaimer = re.search(r"(?m)^> _Disclaimer: .+_$", TEMPLATE.read_text(encoding="utf-8")).group(0)
    for chain_id, title in CHAINS:
        members = CHAIN_MEMBERS[chain_id]
        target, layer, recommendation = CHAIN_CONTROL[chain_id]
        assert nonblank(subsection_lines(section, 3, "%s: %s" % (chain_id, title))) == [
            "**Layers**: %s | **Max Severity**: Critical | **Findings**: %d | **Converging chains**: 1" % (" → ".join(CHAIN_LAYERS[chain_id]), len(members)),
            marker("attack_chains", "chain." + chain_id),
            "**Chain-Breaking Control**: %s at layer %s. %s" % (target, layer, recommendation),
            disclaimer,
            "**Impacted Findings**: " + "; ".join("%s (%s, %s)" % (m[0], m[1], m[2]) for m in members)], chain_id
    assert "CHAIN-007" not in section


def test_section_6_the_control_is_the_chain_files_recommendation_verbatim_and_escaped_again(assembler, make):
    """The file stores the recommendation escaped, as its renderer wrote it. The reader decodes it, and the report writes it again, so a pipe doesn't split a cell
    and a tag stays text, and the control reads back as the chain file's own."""
    world = make("report", planned_chains=True, outcome=OUTCOME_WRITTEN)
    stored = "Verify each order &#124; reject &lt;b&gt;unsigned&lt;/b&gt; ones &amp; log them"
    world.chains_path.write_text(world.chains_path.read_text(encoding="utf-8").replace(CHAIN_CONTROL["CHAIN-001"][2], stored), encoding="utf-8")
    report_ok(world, assembler)
    line = next(l for l in section_text(world.report_text, 6).split("\n") if l.startswith("**Chain-Breaking Control**: T-1"))
    assert line.endswith(stored) and "<b>" not in line
    assert tachi_parsers.decode_references(line).endswith("Verify each order | reject <b>unsigned</b> ones & log them")


# ---- Agentic Pattern Analysis

def test_pattern_analysis_opens_with_its_boilerplate_and_the_multi_pattern_findings_then_one_subsection_for_each_pattern_in_fr_013_order(assembler, make):
    world = make("report", **RICH)
    report_ok(world, assembler)
    text = world.report_text
    number = title_number(text, "Agentic Pattern Analysis")
    assert number == 7, "Section 6 is on every run, so the section follows it and the roadmap, the appendix and the delta summary move up (RD-11)"
    section = section_text(text, number)
    shared = dict(zip(tp.REPORT_PATTERNS, shared_patterns()))
    assert [title for _, level, title in atx_headings(section) if level == 3] == ["Multi-Pattern Findings"] + [shared[v][0] for v in PATTERN_ORDER]
    assert section.lstrip("\n").startswith("This section enumerates threats by CSA MAESTRO canonical agentic pattern.")
    assert nonblank(subsection_lines(section, 3, "Multi-Pattern Findings")) == [marker("agentic_patterns", "multi"), "Impacted findings: S-1"]
    by_id = {f.id: f for f in world.findings}
    for value in PATTERN_ORDER:
        name, definition = shared[value]
        ids = [i for i in open_order(world.findings) if by_id[i].pattern == value]
        counts = " | ".join("%s: %d" % (level, sum(1 for i in ids if by_id[i].risk == level)) for level in ("Critical", "High", "Medium", "Low"))
        assert nonblank(subsection_lines(section, 3, name)) == [definition, counts, "Impacted findings: " + ", ".join(ids), marker("agentic_patterns", "pattern." + value)], value
    assert "Critical: 0 | High: 2 | Medium: 0 | Low: 0" in section and "Impacted findings: T-2, OI-1" in section, "two High findings, in Section 3 and 4's order"


def test_pattern_analysis_a_multiple_finding_is_listed_under_multi_pattern_findings_only(assembler, make):
    world = make("report", **RICH)
    report_ok(world, assembler)
    section = section_text(world.report_text, 7)
    lines = [line for line in section.split("\n") if line.startswith("Impacted findings: ")]
    assert lines.count("Impacted findings: S-1") == 1 and not any("S-1" in line for line in lines if line != "Impacted findings: S-1")
    assert {row[2] for row in appendix_rows(world) if row[0] == "S-1" and row[1] == 7} == {"Multi-Pattern Findings"}


def test_pattern_analysis_a_pattern_with_no_finding_has_no_subsection_and_no_multi_block_without_a_multiple_finding(assembler, make):
    world = make("report", rule="rule2", pattern_of={"AG-1": "agent_collusion"})
    report_ok(world, assembler)
    section = section_text(world.report_text, 7)
    assert [title for _, level, title in atx_headings(section) if level == 3] == ["Agent Collusion"]
    assert nonblank(subsection_lines(section, 3, "Agent Collusion"))[1:3] == ["Critical: 0 | High: 1 | Medium: 0 | Low: 0", "Impacted findings: AG-1"]


def test_pattern_analysis_a_run_with_only_multiple_findings_has_the_multi_block_and_no_pattern_subsection(assembler, make):
    world = make("report", rule="rule2", pattern_of={"AG-1": "multiple", "LLM-1": "multiple"})
    report_ok(world, assembler)
    section = section_text(world.report_text, 7)
    assert [title for _, level, title in atx_headings(section) if level == 3] == ["Multi-Pattern Findings"]
    assert nonblank(subsection_lines(section, 3, "Multi-Pattern Findings")) == [marker("agentic_patterns", "multi"), "Impacted findings: AG-1, LLM-1"]


def test_pattern_analysis_is_absent_from_a_run_where_no_finding_has_a_pattern(assembler, make):
    world = make("report", rule="rule2")
    report_ok(world, assembler)
    assert "Agentic Pattern Analysis" not in world.report_text and "Multi-Pattern Findings" not in world.report_text


# ---- Section 7, the roadmap

def expected_roadmap_intro(world):
    """RD-27: the intro's sentence, computed from the findings and the groups with none of the assembler's code."""
    groups = tachi_parsers.parse_correlation_groups(world.threats_text, world.open_ids())["groups"]
    group_of = {member: group for group in groups for member in group["members"]}
    risk = {f.id: f.risk for f in world.findings}
    tiers = dict(TIER_OF)
    per_tier = collections.Counter()
    for i in world.roadmap_ids():
        members = group_of[i]["members"] if i in group_of else [i]
        per_tier[tiers[min((risk[m] for m in members), key=RISK_RANK.get)]] += 1
    components = collections.Counter(f.component for f in world.findings)
    most = min(components, key=lambda name: (-components[name], name))
    shown = ", ".join("%d %s" % (per_tier[tier], tier) for tier in ("Immediate", "Short-term", "Medium-term", "Backlog") if per_tier[tier])
    return ("The roadmap lists %d rows, ordered by risk level and then by component: %s. The most impacted component is %s, with %d open findings."
            % (len(world.roadmap_ids()), shown, most, components[most]))


ALPHA = [f._replace(component="Alpha Service") if f.id in ("T-1", "T-2") else f for f in findings_for("rule2")]
INTRO_CASES = {
    "nine findings, three components tie for most": dict(rule="rule2"),
    "a tie that is broken by name, not by order": dict(rule="rule2", findings=ALPHA),
    "groups that fold some findings into one row": dict(rule="rule2", groups=A20_GROUPS),
    "thirty-four findings": SCENARIOS["a run of thirty-four"],
}


@pytest.mark.parametrize("case", sorted(INTRO_CASES))
def test_section_7_opens_with_the_row_count_the_rows_per_tier_and_the_most_impacted_component(assembler, make, case):
    world = make("report", **INTRO_CASES[case])
    report_ok(world, assembler)
    text = world.report_text
    lines = [line for line in section_text(text, title_number(text, "Remediation Roadmap")).split("\n") if line.strip()]
    assert lines[0] == expected_roadmap_intro(world), lines[0]
    if case.startswith("nine"):
        assert lines[0].endswith("3 Immediate, 4 Short-term, 1 Medium-term, 1 Backlog. The most impacted component is Gateway, with 2 open findings."), "Gateway sorts first"
    if case.startswith("a tie"):
        assert "The most impacted component is Alpha Service, with 2 open findings." in lines[0]


def test_section_7_ends_with_the_templates_priority_tier_and_effort_scale_tables(assembler, make):
    world = make("report", rule="rule2")
    report_ok(world, assembler)
    text = world.report_text
    section = section_text(text, title_number(text, "Remediation Roadmap"))
    template = TEMPLATE.read_text(encoding="utf-8")
    for label in ("Priority tiers:", "Effort scale:"):
        block = re.search(r"(?m)^\*\*%s\*\*\n\n((?:\|.*\n)+)" % re.escape(label), template)
        assert block is not None and "**%s**\n\n%s" % (label, block.group(1)) in section + "\n", label
    assert section.index("**Priority tiers:**") < section.index("**Effort scale:**") and section.index("| S-1 |") < section.index("**Priority tiers:**")


def test_section_7_a_groups_row_lists_each_members_mitigation_verbatim_in_member_order_each_led_by_its_id(assembler, make):
    """RD-26. The mitigations are stored escaped, as the joiner writes them, and read decoded: the row writes each one again, so each reads back as it was stored."""
    stored = {"T-1": "Sign every order &#124; reject &lt;b&gt;unsigned&lt;/b&gt; ones", "T-2": "Authenticate queue producers &amp; consumers",
              "OI-1": "Encode all model output"}
    findings = [f._replace(mitigation=stored[f.id]) if f.id in stored else f for f in findings_for("rule2")]
    world = make("report", rule="rule2", findings=findings, groups=[("CG-1", ["T-1", "T-2", "OI-1"])])
    report_ok(world, assembler)
    rows = roadmap_rows(world)
    assert [r["Finding ID"] for r in rows if r["Finding ID"] in stored] == ["T-1"], "the primary's row stands for the group; its peers have none"
    row = next(r for r in rows if r["Finding ID"] == "T-1")
    decoded = {i: tachi_parsers.decode_references(text) for i, text in stored.items()}
    assert row["Mitigation"] == "; ".join("%s: %s" % (i, decoded[i]) for i in ("T-1", "T-2", "OI-1"))
    assert "<b>" not in world.report_text and "Authenticate queue producers &amp; consumers" in world.report_text, "written again, as it was stored"
    assert row["Component"] == "Order Service" and row["Effort"] == world.roadmap_items["T-1"]["effort"]
    item = world.roadmap_items["T-1"]["dependencies"]
    note = "Correlated: T-1, T-2, OI-1 (CG-1)."
    assert row["Dependencies"] == (note if item is None else note + " " + item.replace("{{finding:T-1}}", "T-1")), row["Dependencies"]


def test_section_7_two_group_rows_each_take_their_highest_risk_level_and_sort_by_their_primarys_component_among_that_levels_rows(assembler, make):
    world = make("report", rule="rule2", groups=[("CG-1", ["E-1", "OI-1"]), ("CG-2", ["D-1", "T-2"])])
    report_ok(world, assembler)
    assert [r["Finding ID"] for r in roadmap_rows(world)] == ["S-1", "T-1", "LLM-1", "E-1", "D-1", "I-1", "AG-1"], \
        "E-1 (Low) stands among the High rows for OI-1, and D-1 (Medium) for T-2, which is High, so it sorts by component with them"


def test_section_7_a_group_with_a_member_the_run_resolved_lists_only_its_open_members(assembler, make):
    world = make("report", rule="rule2", groups=[("CG-1", ["R-9", "T-1", "T-2"])])
    report_ok(world, assembler)
    row = next(r for r in roadmap_rows(world) if r["Finding ID"] == "T-1")
    assert row["Mitigation"].startswith("T-1: ") and "R-9" not in row["Mitigation"] + row["Dependencies"] and row["Dependencies"].startswith("Correlated: T-1, T-2 (CG-1).")


# ---- Section 8, the appendix: one row for each place that the report puts a finding

NUMBER_WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def section_numbers(world):
    """Each section's number in this run: 1 to 6 are on every run (RD-11), the patterns follow when a finding has one, then the roadmap, the appendix and, in a run
    with a baseline, the delta summary."""
    names = ["exec", "architecture", "threats", "themes", "trees", "chains"]
    if any(f.pattern != DASH for f in world.findings):
        names.append("patterns")
    names += ["roadmap", "appendix"] + (["delta"] if world.has_baseline else [])
    return {name: n for n, name in enumerate(names, 1)}


def expected_appendix(world, themes=None):
    """RD-27, from the contract and not the assembler: a finding's Section 3 subsection, each theme whose body cites it, its tree, each surfaced chain it belongs to, its
    pattern subsection, and its roadmap row, or for a peer its group's row. ``themes`` maps a theme's number to the IDs that its body cites."""
    number, template = section_numbers(world), template_subsections()
    shared = dict(zip(tp.REPORT_PATTERNS, shared_patterns()))
    groups = tachi_parsers.parse_correlation_groups(world.threats_text, world.open_ids())["groups"]
    group_of = {member: group for group in groups for member in group["members"]}
    places = collections.defaultdict(set)
    for f in world.findings:
        places[f.id].add((number["threats"], template[CATEGORY_ORDER.index(category_of(f.id))]))
        if f.id in world.ch_ids:
            places[f.id].add((number["trees"], "%s: %s" % (f.id, f.threat)))
        if f.pattern == "multiple":
            places[f.id].add((number["patterns"], "Multi-Pattern Findings"))
        elif f.pattern != DASH:
            places[f.id].add((number["patterns"], shared[f.pattern][0]))
    if world.planned_chains:
        for chain_id, title in CHAINS:
            for member in CHAIN_MEMBERS[chain_id]:
                places[member[0]].add((number["chains"], "%s: %s" % (chain_id, title)))
    for n, ids in (themes or {}).items():
        for i in ids:
            places[i].add((number["themes"], "Theme %d: Marker for theme title %s." % (n, NUMBER_WORD[n])))
    for i in world.roadmap_ids():
        for member in (group_of[i]["members"] if i in group_of else [i]):
            places[member].add((number["roadmap"], "Remediation Roadmap"))
    return [(i, n, heading) for i in world.open_ids() for n, heading in sorted(places[i])]


APPENDIX_SCENARIOS = dict(SCENARIOS, **{"groups in a run of nine": dict(RICH, groups=A20_GROUPS)})


@pytest.mark.parametrize("scenario", sorted(APPENDIX_SCENARIOS))
def test_the_appendix_has_one_row_for_each_place_that_the_report_puts_a_finding(assembler, make, scenario):
    world = make("report", **APPENDIX_SCENARIOS[scenario])
    reword_in(world, "theme.1.body", "Cites {{finding:S-1}} and {{finding:LLM-1}}.")
    reword_in(world, "theme.2.body", "Cites {{finding:T-2}}.")
    report_ok(world, assembler)
    rows = appendix_rows(world)
    assert rows == expected_appendix(world, themes={1: ["S-1", "LLM-1"], 2: ["T-2"]})
    number = section_numbers(world)
    for f in world.findings:
        mine = {(n, heading) for i, n, heading in rows if i == f.id}
        assert any(n == number["threats"] for n, _ in mine) and (number["roadmap"], "Remediation Roadmap") in mine, "zero finding loss: %s has its Section 3 and its roadmap row" % f.id


def test_the_appendix_names_a_peer_in_its_groups_roadmap_row(assembler, make):
    world = make("report", **dict(RICH, groups=[("CG-1", ["T-1", "T-2"])]))
    report_ok(world, assembler)
    number = section_numbers(world)["roadmap"]
    assert ("T-2", number, "Remediation Roadmap") in appendix_rows(world), "T-2 has no row of its own in the roadmap, and the appendix still sends the reader to it"
    assert not any(row["Finding ID"] == "T-2" for row in roadmap_rows(world))


# ---- Section 9, the delta summary

def test_section_9_has_the_lifecycle_breakdown_the_progress_paragraph_and_the_baseline_reference(assembler, make):
    world = make("report", rule="rule2")
    reword_in(world, "progress", "The run resolved {{finding:R-9}} on {{name:component:R-9}}, so {{count:resolved}} fewer.")
    report_ok(world, assembler)
    text = world.report_text
    section = section_text(text, title_number(text, "Delta Summary"))
    assert [title for _, level, title in atx_headings(section) if level == 3] == ["Finding Lifecycle Breakdown", "Remediation Progress", "Baseline Reference"]
    counts = collections.Counter(f.status for f in world.findings)
    assert (counts["NEW"], counts["UNCHANGED"], counts["UPDATED"], len(world.resolved)) == (4, 4, 1, 1)
    assert nonblank(subsection_lines(section, 3, "Finding Lifecycle Breakdown")) == [
        "| Status | Count | Description |", "|---|---|---|",
        "| NEW | 4 | Findings discovered in this run with no baseline match |",
        "| UNCHANGED | 4 | Findings identical to baseline (same component, threat, assessment) |",
        "| UPDATED | 1 | Findings with changed context since baseline |",
        "| RESOLVED | 1 | Baseline findings no longer applicable (from Section 4c) |",
        "| **Total** | 10 | Sum of all findings (active + resolved) |"]
    assert nonblank(subsection_lines(section, 3, "Remediation Progress")) == ["The run resolved R-9 on Legacy Cache, so 1 fewer."]
    reference = [line for line in nonblank(subsection_lines(section, 3, "Baseline Reference")) if not line.startswith("<!-- tachi-provenance")]   # the stamp ends the file
    assert reference == ["| Field | Value |", "|---|---|", "| Source | baseline/threats.md |", "| Date | %s |" % BASELINE_DATE, "| Baseline Findings | 10 |",
                         "| Run ID | 2026-11-10T09-00-00 |"]


def test_section_9_the_breakdown_counts_come_from_section_7_and_4c_for_a_run_with_only_unchanged_findings(assembler, make):
    world = make("report", rule="rule1")
    report_ok(world, assembler)
    text = world.report_text
    lines = nonblank(subsection_lines(section_text(text, title_number(text, "Delta Summary")), 3, "Finding Lifecycle Breakdown"))
    assert "| NEW | 0 |" in lines[2] and "| UNCHANGED | 9 |" in lines[3] and "| UPDATED | 0 |" in lines[4] and "| RESOLVED | 0 |" in lines[5] and "| **Total** | 9 |" in lines[6]


# ---- slots: every kind of the contract's `report` table, against the reference set

BANDS = ("critical", "high", "medium", "low", "note")


def hamilton(counts):
    """Integer shares that sum to 100 by the largest remainder, ties to the label that sorts first (D5), written here and not imported."""
    total = sum(counts.values())
    shares = {label: 100 * n // total for label, n in counts.items()}
    for label in sorted(counts, key=lambda label: (-(100 * counts[label] % total), label))[:100 - sum(shares.values())]:
        shares[label] += 1
    return shares


def slot_values(world):
    """Every ``count`` slot's value, from the findings and the RESOLVED list alone."""
    values = {"open": len(world.findings), "resolved": len(world.resolved)}
    for status in ("new", "unchanged", "updated"):
        values[status] = sum(1 for f in world.findings if f.status == status.upper())
    for band in BANDS:
        values[band] = sum(1 for f in world.findings if f.risk.lower() == band)
    for key in CATEGORY_ORDER:
        values[key] = sum(1 for f in world.findings if category_of(f.id) == key)
        for band in BANDS:
            values["%s.%s" % (key, band)] = sum(1 for f in world.findings if category_of(f.id) == key and f.risk.lower() == band)
    return values


@pytest.mark.parametrize("scenario", ["a run of nine", "a run of thirty-four"])
def test_slots_count_resolves_every_argument_of_the_contracts_table_and_pct_gives_the_shares_by_largest_remainder(assembler, make, scenario):
    world = make("report", **SCENARIOS[scenario])
    values = slot_values(world)
    status = ["open", "resolved", "new", "unchanged", "updated"]
    pairs = ["%s.%s" % (key, band) for key in CATEGORY_ORDER for band in BANDS]
    shares = hamilton({band: values[band] for band in BANDS})
    assert sum(shares.values()) == 100
    if scenario == "a run of nine":
        assert shares == {"critical": 33, "high": 45, "medium": 11, "low": 11, "note": 0}, "by hand: 3, 4, 1, 1 and 0 of 9; the spare point goes to High's largest remainder"
    reword_in(world, "risk_posture", " ".join("{{count:%s}}" % key for key in status) + " and " + " ".join("{{pct:%s}}" % band for band in BANDS))
    reword_in(world, "top_threats", " ".join("{{count:%s}}" % key for key in list(BANDS) + list(CATEGORY_ORDER)))
    reword_in(world, "key_recommendations", " ".join("{{count:%s}}" % key for key in pairs))
    report_ok(world, assembler)
    section = section_text(world.report_text, 1)
    assert nonblank(subsection_lines(section, 3, "Risk Posture")) == [" ".join(str(values[key]) for key in status) + " and " + " ".join(str(shares[b]) for b in BANDS)]
    assert nonblank(subsection_lines(section, 3, "Top 5 Threats")) == [" ".join(str(values[key]) for key in list(BANDS) + list(CATEGORY_ORDER))]
    assert nonblank(subsection_lines(section, 3, "Key Recommendations")) == [" ".join(str(values[key]) for key in pairs)]
    assert world.record("report")["counts"]["narrative_fallbacks"] == 0
    if scenario == "a run of thirty-four":
        assert (values["open"], values["note"], values["repudiation"], values["llm"], values["llm.high"]) == (34, 8, 4, 2, 1)


def test_slots_finding_name_and_band_resolve_against_the_reference_set_and_a_finding_may_be_a_resolved_one(assembler, make):
    world = make("report", rule="rule2")
    reword_in(world, "top_threats", "{{finding:S-1}} on {{name:component:S-1}} is {{band:risk:S-1}}, and {{finding:E-1}} on {{name:component:E-1}} is {{band:risk:E-1}}.")
    reword_in(world, "key_recommendations", "Start with {{finding:T-01}} and {{finding:AG-1}}.")
    reword_in(world, "progress", "{{finding:R-9}} on {{name:component:R-9}} is resolved, {{count:resolved}} in all.")
    report_ok(world, assembler)
    text = world.report_text
    assert nonblank(subsection_lines(section_text(text, 1), 3, "Top 5 Threats")) == ["S-1 on Gateway is Critical, and E-1 on Admin Console is Low."]
    assert nonblank(subsection_lines(section_text(text, 1), 3, "Key Recommendations")) == ["Start with T-1 and AG-1."], "a finding slot is canonicalized"
    assert nonblank(subsection_lines(section_text(text, title_number(text, "Delta Summary")), 3, "Remediation Progress")) == ["R-9 on Legacy Cache is resolved, 1 in all."]
    assert world.record("report")["counts"]["narrative_fallbacks"] == 0


@pytest.mark.parametrize("slot", ["{{band:risk:R-9}}", "{{band:risk:S-99}}", "{{finding:S-99}}", "{{name:component:S-99}}", "{{ref:CWE-89}}", "{{ref:L5}}"])
def test_slots_one_that_does_not_resolve_gives_the_field_its_fixed_sentence_and_is_counted(assembler, make, slot):
    """R-9 is RESOLVED, so a band is not its to give. S-99 is no finding. No finding of this run carries CWE-89, or a layer 5 (the layers are 1, 2, 3, 4 and 7)."""
    world = make("report", rule="rule2")
    reword_in(world, "top_threats", "Start with " + slot + " here.")
    report_ok(world, assembler)
    assert nonblank(subsection_lines(section_text(world.report_text, 1), 3, "Top 5 Threats")) == [tp.REPORT_FALLBACKS["fragment"]]
    assert "Start with" not in world.report_text and world.record("report")["counts"]["narrative_fallbacks"] == 1


# ---- the `ref` slot: a taxonomy ID of the item's own finding in a findings part, of any finding in a section fragment (RD-24)

def test_slots_a_ref_in_a_findings_part_must_be_one_of_the_items_own_findings_taxonomy_ids(assembler, make):
    findings = [f._replace(layer="L1 — Foundation Model") if f.id == "LLM-1" else f for f in findings_for("rule2")]
    world = make("report", rule="rule2", findings=findings)
    reword_item(world, "threat_analysis", "LLM-1", narrative="It cites {{ref:LLM01:2026}}, {{ref:CWE-77}} and {{ref:L1}}.", tree_summary="It also cites {{ref:L1}}.")
    reword_item(world, "threat_analysis", "S-1", narrative="It cites {{ref:L4}} and {{ref:LLM01:2026}}.")   # the second is LLM-1's, and not S-1's
    reword_item(world, "remediation_roadmap", "LLM-1", dependencies="Needs {{ref:CWE-77}}.")
    reword_item(world, "remediation_roadmap", "S-1", dependencies="Needs {{ref:CWE-77}}.")                    # not S-1's either
    report_ok(world, assembler)
    text = world.report_text
    section = section_text(text, 3)
    assert "It cites LLM01:2026, CWE-77 and L1." in section
    assert "It cites L4" not in section and tp.REPORT_FALLBACKS["narrative"] in section, "one cited ID that S-1 doesn't carry takes the whole field's fixed sentence"
    assert "It also cites L1." in section_text(text, 5)
    rows = {row["Finding ID"]: row for row in roadmap_rows(world)}
    assert rows["LLM-1"]["Dependencies"] == "Needs CWE-77." and rows["S-1"]["Dependencies"] == tp.REPORT_FALLBACKS["dependencies"]
    assert world.record("report")["counts"]["narrative_fallbacks"] == 2


def test_slots_a_ref_in_a_section_fragment_may_be_any_findings_taxonomy_id_that_has_a_unit_row(assembler, make):
    world = make("report", rule="rule2")
    reword_in(world, "top_threats", "Across the run {{ref:LLM01:2026}}, {{ref:ASI02:2026}}, {{ref:CWE-77}}, {{ref:LLM05:2026}} and {{ref:L7}} are cited.")
    reword_in(world, "key_recommendations", "Only {{ref:CWE-89}} is cited.")   # no finding carries it
    report_ok(world, assembler)
    section = section_text(world.report_text, 1)
    assert nonblank(subsection_lines(section, 3, "Top 5 Threats")) == ["Across the run LLM01:2026, ASI02:2026, CWE-77, LLM05:2026 and L7 are cited."]
    assert nonblank(subsection_lines(section, 3, "Key Recommendations")) == [tp.REPORT_FALLBACKS["fragment"]]


def test_slots_a_cell_that_its_table_lacks_gives_no_taxonomy_id(assembler, make):
    """RD-22. A unit row with no ``owasp_reference`` carries its layer alone, and one with no ``maestro_layer`` carries what its reference cell lists."""
    world = make("report", rule="rule2", drop_row_keys=("owasp_reference",))
    reword_item(world, "threat_analysis", "LLM-1", narrative="It cites {{ref:LLM01:2026}}.")
    reword_item(world, "threat_analysis", "AG-1", narrative="It cites {{ref:L3}}.")
    report_ok(world, assembler)
    section = section_text(world.report_text, 3)
    assert "It cites L3." in section and "It cites LLM01:2026." not in section and tp.REPORT_FALLBACKS["narrative"] in section
    other = make("report", rule="rule2", drop_row_keys=("maestro_layer",))
    reword_item(other, "threat_analysis", "LLM-1", narrative="It cites {{ref:LLM01:2026}} and {{ref:CWE-77}}.")
    reword_item(other, "threat_analysis", "S-1", narrative="It cites {{ref:L4}}.")
    report_ok(other, assembler)
    section = section_text(other.report_text, 3)
    assert "It cites LLM01:2026 and CWE-77." in section and "It cites L4." not in section and tp.REPORT_FALLBACKS["narrative"] in section


# ---- drift: the assembler's copies of fixed text are the shared reference's and the template's

def test_drift_the_six_pattern_names_and_definitions_are_the_shared_references(assembler):
    module, shared = assembler.load(), shared_patterns()
    assert len(shared) == 6
    assert [(display, definition) for _, display, definition in module.PATTERNS] == shared
    assert tuple(value for value, _, _ in module.PATTERNS) == tp.REPORT_PATTERNS, "the enum's order is the reference's order (FR-013's tertiary key)"
    assert [display for _, display, _ in module.PATTERNS] == ["Agent Collusion", "Emergent Behavior", "Temporal Attacks", "Trust Exploitation", "Communication Vulnerabilities",
                                                           "Resource Competition"]


def test_drift_the_fixed_sentences_and_tables_are_the_templates(assembler):
    module, template = assembler.load(), TEMPLATE.read_text(encoding="utf-8")
    assert module.TITLES == template_titles()
    assert module.NO_TREE_NOTE in template and module.NO_THEMES_NOTE in template and module.CHAIN_DISCLAIMER in template
    assert "\n".join(module.TIER_TABLE) in template and "\n".join(module.EFFORT_TABLE) in template
    assert all(description in template for _, description in module.LIFECYCLE) and [status for status, _ in module.LIFECYCLE] == ["NEW", "UNCHANGED", "UPDATED", "RESOLVED"]
    assert [level for level, _ in module.TIERS] == list(tp.RISK_LEVELS) and dict(module.TIERS) == dict(TIER_OF)
    assert [key for key, _, _ in module.CATEGORIES] == list(CATEGORY_ORDER) == list(tp.REPORT_CATEGORY_KEYS)
    assert ["3.%d %s" % (n, heading) for n, (_, heading, _) in enumerate(module.CATEGORIES, 1)] == template_subsections()


# ---- the plan's batching is not in the report

def test_findings_parts_split_over_batches_give_the_same_report_bytes_as_one_part_each(assembler, make):
    """The input digest follows the units' content in plan order, never how they were batched (NFR-2), and the file holds no plan ID."""
    whole = make("report", **RICH)
    split = make("report", **dict(RICH, per_report_batch=3, trees_id=OTHER_ID, report_id="20261124T130000Z-dddddddddddd"))
    report_ok(whole, assembler)
    report_ok(split, assembler)
    assert len(split.batch_ids("report")) == len(whole.batch_ids("report")) + 2 + 2, "nine narrated findings in three parts, and nine roadmap rows in three"
    assert whole.report_path.read_bytes() == split.report_path.read_bytes()


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_every_planned_unit_of_the_rich_scenarios_has_its_content_in_the_file(assembler, make, scenario):
    """``rendered`` counts the units whose content the file holds: here all of them, the optional overview, the compliance paragraph and the themes included."""
    world = make("report", **SCENARIOS[scenario])
    report_ok(world, assembler)
    counts = world.record("report")["counts"]
    assert counts["rendered"] == counts["units"] == read_json(world.plan_path("report"))["unit_count"] > 20, counts
