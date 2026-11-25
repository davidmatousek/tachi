#!/usr/bin/env python3
"""Copy the attack trees and assemble the threat report from their parts (F-374; ADR-050 D14, RR3).

Two modes, each on its own stage's plan (``contracts/cli.md``):

    python3 scripts/assemble-report.py trees  --run-dir DIR --plan ID --plan-digest HEX
    python3 scripts/assemble-report.py report --run-dir DIR --plan ID --plan-digest HEX

**``trees``** runs once the ``trees`` stage reconciles to 0. It holds every tree to D14's checks and then copies it, byte for byte, to
``attack-trees/<id>-attack-tree.md``: a generated tree from the path its batch input names, and a carried tree (Rule 1's, and Rule 3's
``carried_forward`` decision, S1P-A43) from the baseline. It merges the batch manifests into the schema-1.0 ``attack-trees/.manifest.json``
(FR-K5.6). Everything is checked before anything is written (RD-7): a tree that fails a per-file check (one Mermaid block, the size cap,
no character that ``tachi_parts.forbidden_character`` returns, the ID on the allow-list before it becomes a path, no link) is exit 2, and a
tree that is still missing, or a Critical and High set that differs from the generated and carried trees, is exit 4, which applies FR-K5.5
early. So is a ``.md`` name in ``attack-trees/`` that this run does not write, as an earlier run's tree would be: FR-K5.7 applied early (S1P-A91). Nothing
is moved or deleted, and an earlier file under a name that this run writes is replaced. It stages nothing: once every check has passed it writes
``attack-trees/`` with the atomic write (``STAGED_OUTPUTS["trees"]`` is ``()``).

**``report``** runs at Step 2.9, after the chain check and the provenance check. It checks the report plan and the trees plan that it pins as
D3 checks any plan, except that ``threats.md`` and ``attack-chains.md``, which Steps 2.5 to 2.8 change by design, are checked by the reference
set's digest (``params.reference_digest``) and by the final outcome record (RR3, S1P-A47). It then runs FR-K5.5, FR-K5.7 and FR-K5.3 (exit 4),
builds the file in code (Section 5 from the standalone tree files, re-fenced longer than any backtick run inside the source, FR-K5.2),
stamps it, and replaces any ``threat-report.md`` an agent wrote.

Both modes write their stage's record on 0 and never rewrite ``plan.json``. Exit codes are ``contracts/cli.md``'s: 0 done, 1 an input is
missing or unreadable, 2 a validation, usage or guard failure, 4 a completeness or parity check failed or a file could not be written. The
script never returns 3 or 5. A failure prints D4's four-line message on stderr, and a refused run writes nothing.

**The layout of the report** is ``contracts/part-files.md``'s, "The assembler's layout". Sections are numbered by position, as
``## <n>. <title>`` (S1P-A45): 1 to 6 are on every run, so their numbers never move, and Agentic Pattern Analysis, when it is planned,
takes 7. Every cell takes D3's cell sink, every fragment its prose sink, and each slot resolves against the reference set: a ``ref`` slot against the
taxonomy IDs that the item's own finding carries in its unit row (an OWASP Reference cell's IDs and its MAESTRO layer), or, in a section fragment, any
finding's that has one. A value that this script takes from an input that isn't a part, a ``threats.md`` value, a tree file, a chain title, a unit row,
is refused where it is taken when it holds a character in D3's step 10 set (P0-4, S1P-A18). The report plan must hold the units that the reference
set implies, which ``_check_plan`` states: the findings that are narrated one by one, the category summaries, the pattern units and the delta part.

Standard library plus the shared helpers, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("assemble-report.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import collections
import json
import os
import re
from pathlib import Path
from typing import Any, Collection, Dict, List, Mapping, Optional, Sequence, Tuple

sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402
import tachi_scoring as ts  # noqa: E402
import tachi_scoring_rules as rules  # noqa: E402

RENDERER = "assemble-report.py"  # the stamp's name: the installed file name, as a literal (contracts/cli.md)
TREE_DIR = "attack-trees"
MANIFEST = TREE_DIR + "/.manifest.json"
REPORT = "threat-report.md"
DASH = "\u2014"
RULES = ("Rule 1", "Rule 2", "no-baseline", "no-op")  # the manifest's `rule_applied`, which the plan records
RISK_RANK = {level: rank for rank, level in enumerate(tp.RISK_LEVELS)}
REGENERATE = "regenerate threats.md with /tachi.threat-model, or edit the value"
# `trees` writes attack-trees/ directly, with no staging (RD-7), so a write that fails part way leaves some of the new files in place. Running it again replaces
# every file it writes, which is what `tp.RETRY_REMEDY` ("the earlier outputs were left or put back") would not say.
WRITE_REMEDY = "fix the cause that the message gives, then run assemble-report.py trees again: it replaces every file it writes"
# The report assembler's plans pin every input by digest but two (RR3): Steps 2.5 to 2.8 rewrite threats.md and may quarantine attack-chains.md.
# The reference set's digest and the final outcome record stand in for them.
UNPINNED_REPORT = ("threats", "attack_chains")
UNPINNED_TREES_IN_REPORT = ("threats",)
# A run with more open findings than this summarizes its Medium, Low and Note findings by category, and narrates the rest one by one (the template's guidance,
# part-files.md "Narrated or summarized").
NARRATE_LIMIT = 30

# The template's nine sections, by their number in the template (output-schemas/threat-report.md). A report numbers the sections it holds by position.
TITLES = {1: "Executive Summary", 2: "Architecture Overview", 3: "Threat Analysis", 4: "Cross-Cutting Themes", 5: "Attack Trees",
          6: "Cross-Layer Attack Chains", 7: "Remediation Roadmap", 8: "Appendix: Finding Reference", 9: "Delta Summary"}
PATTERN_TITLE = "Agentic Pattern Analysis"
# Section 3's eight subsections: the category key (`tachi_parts.REPORT_CATEGORY_KEYS`), the template's heading and the name that "no threats" uses.
CATEGORIES = (("spoofing", "Spoofing", "Spoofing"), ("tampering", "Tampering", "Tampering"), ("repudiation", "Repudiation", "Repudiation"),
              ("information_disclosure", "Information Disclosure", "Information Disclosure"),
              ("denial_of_service", "Denial of Service", "Denial of Service"),
              ("elevation_of_privilege", "Elevation of Privilege", "Elevation of Privilege"),
              ("agentic", "Agentic Threats", "Agentic"), ("llm", "LLM Threats", "LLM"))
CATEGORY_OF_PREFIX = {"S": "spoofing", "T": "tampering", "R": "repudiation", "I": "information_disclosure", "D": "denial_of_service",
                      "E": "elevation_of_privilege", "AG": "agentic", "AGP": "agentic", "TE": "agentic", "LLM": "llm", "OI": "llm", "MI": "llm"}
CATEGORY_INDEX = {key: index for index, (key, _, _) in enumerate(CATEGORIES)}
# Section 1's remediation timeline: the tier of each risk level (the form `extract-report-data.py` reads).
TIERS = (("Critical", "Immediate"), ("High", "Short-term"), ("Medium", "Medium-term"), ("Low", "Backlog"), ("Note", "Backlog"))
# The six canonical patterns, in `tachi_parts.REPORT_PATTERNS`' order: the display name and the definition, copied from
# `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` (Section 1; a drift test pins them).
PATTERNS = (
    ("agent_collusion", "Agent Collusion",
     "Multiple compromised agents coordinate to achieve malicious objectives that no single agent could accomplish alone \u2014 exfiltrating data "
     "across shared channels, jointly manipulating planning outputs, or circumventing policies by distributing actions below per-agent detection "
     "thresholds."),
    ("emergent_behavior", "Emergent Behavior",
     "Attackers exploit unpredictable behaviors that arise only from the interaction of multiple agents (cascading failures, feedback "
     "amplification, behavioral drift) \u2014 behaviors that are invisible in per-agent analysis and manifest only when agents act in concert."),
    ("temporal_attack", "Temporal Attacks",
     "Attacks that exploit persistent state to achieve delayed or time-gated effects \u2014 sleeper agents activating under specific triggers, "
     "gradual corruption of learned parameters, seasonal exploitation patterns, or poisoned training data that surfaces only during re-training "
     "cycles."),
    ("trust_exploitation", "Trust Exploitation",
     "Attacks that subvert the trust relationships between agents \u2014 identity spoofing between cooperating agents, reputation manipulation in "
     "agent registries, trust chain attacks that pivot from a weakly-trusted agent to a highly-trusted peer, and impersonation of supervisor "
     "agents."),
    ("communication_vulnerability", "Communication Vulnerabilities",
     "Attacks against the inter-agent messaging substrate \u2014 interception of messages on shared channels, protocol manipulation that degrades "
     "authentication or integrity guarantees, routing attacks that divert messages to adversary-controlled agents, and replay attacks on "
     "agent-to-agent communication."),
    ("resource_competition", "Resource Competition",
     "Attacks that exploit contention between agents for shared resources \u2014 resource monopolization by one agent starving peers, priority "
     "manipulation in shared schedulers, coordination disruption that induces resource-use conflicts, and quota-exhaustion attacks that degrade "
     "peer agents' availability."),
)
PATTERN_INTRO = ("This section enumerates threats by CSA MAESTRO canonical agentic pattern. Patterns are assigned during Phase 3.6 (Pattern Synthesis "
                 "Engine) and surface cross-cutting agentic risks that emerge from multi-agent coordination, persistent state, or inter-agent "
                 "communication \u2014 distinct from per-component STRIDE threats.")
# The template's fixed sentences and tables.
NO_TREE_NOTE = "> No Critical or High findings identified. Attack trees are generated only for Critical and High severity findings."
NO_THEMES_NOTE = ("> No cross-cutting themes identified. All findings represent independent threats without shared patterns across agent "
                  "categories.")
CHAIN_DISCLAIMER = ("> _Disclaimer: Chain-breaking controls are structurally derived from graph centrality analysis and should be validated "
                    "against the specific deployment context._")
TIER_TABLE = ["**Priority tiers:**", "", "| Risk Level | Priority Tier | Timeline |", "|------------|---------------|----------|",
              "| Critical | Immediate | Before deployment |", "| High | Short-term | Current development cycle |",
              "| Medium | Medium-term | Upcoming planning cycle |", "| Low | Backlog | Future consideration |"]
EFFORT_TABLE = ["**Effort scale:**", "", "| Effort | Description |", "|--------|-------------|",
                "| Low | Single-component change, well-understood fix, minimal testing |",
                "| Medium | Multi-component coordination, moderate complexity, standard testing |",
                "| High | Architectural change, cross-system impact, extensive testing required |"]
LIFECYCLE = (("NEW", "Findings discovered in this run with no baseline match"),
             ("UNCHANGED", "Findings identical to baseline (same component, threat, assessment)"),
             ("UPDATED", "Findings with changed context since baseline"),
             ("RESOLVED", "Baseline findings no longer applicable (from Section 4c)"))


# =============================================================================
# One run, the plan's guard and the batches
# =============================================================================

class Run(object):
    """One invocation: its mode, the run directory, and the stop that it raises (D4's four-line message under the mode's banner)."""

    def __init__(self, stage: str, out: str, plan_id: str) -> None:
        self.stage, self.out, self.cwd = stage, out, os.getcwd()
        self.kept = tp.plan_dir(out, stage, plan_id)

    def stop(self, code: int, reason: str, remedy: str = "re-run the command", batch: Optional[Tuple[str, str]] = None,
             kept: Optional[str] = None) -> tp.StageFailure:
        return tp.StageFailure(code, self.stage, reason, remedy, batch, None, kept or self.kept)


def _named(ids: Sequence[str], limit: int = 5) -> str:
    """The first few IDs, then ``and N more``."""
    return ", ".join(ids[:limit]) + (" and %d more" % (len(ids) - limit) if len(ids) > limit else "")


def _guard(run: Run, stage: str, plan_id: str, digest: str, unpinned: Tuple[str, ...] = (),
           pinned_by: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, bytes]]:
    """D3's guard for one plan, complete, with its pinned inputs read: ``(plan, bytes of each pinned input)``. It is ``tachi_parts.trusted_plan`` (S1P-A90).

    Every refusal is named under this mode's banner, so the trees plan that ``report`` holds to the same checks as its own fails as a ``report``
    failure, and keeps its own directory (S1P-A47). ``unpinned`` names the inputs that change after the plan by design (RR3, ``UNPINNED_REPORT``): the
    guard neither checks nor reads them, and the caller checks them by the reference set's digest. ``pinned_by`` is the plan that pins this one, for the
    two refusals that would otherwise name a ``--plan`` and a ``--plan-digest`` that the user never passed for it.
    """
    return tp.trusted_plan(stage, run.out, plan_id, digest, complete=True, read_inputs=True, kept=True, unpinned=unpinned, banner=run.stage,
                           pinned_by=pinned_by)


def _batches(run: Run, stage: str, plan: Mapping[str, Any]) -> List[Tuple[Dict[str, Any], Dict[str, Any], Any]]:
    """Every done batch with its batch input and its re-validated part: ``[(plan entry, batch input, PartResult)]``, in plan order.

    A halved parent holds no part of its own, so only the batches that are ``done`` are read, each at its current attempt. These stages' parts are
    valid only against the batch input's ``units`` (S1P-A43), so ``read_part`` gets them. A failure names the batch.
    """
    held, found = tp.plan_dir(run.out, stage, plan["plan_id"]), []
    for entry in plan["batches"]:
        if entry["state"] != "done":
            continue
        batch_id, ids = entry["batch_id"], entry["finding_ids"]
        named = (batch_id, ", ".join(ids))
        try:
            document = tp.read_document(tp.input_path(run.out, stage, plan["plan_id"], batch_id), run.out, tp.BATCH_INPUT_SCHEMA)
        except tp.PartError as exc:
            raise run.stop(1 if exc.kind == "missing" else 2, "the batch input %s is not acceptable (%s)" % (batch_id, exc.detail),
                           "re-run the command", batch=named, kept=held) from None
        if (document["plan_id"], document["batch_id"], document["stage"], document["finding_ids"]) != (plan["plan_id"], batch_id, stage, ids):
            raise run.stop(2, "the batch input %s is for another batch" % batch_id, batch=named, kept=held)
        result = tp.read_part(tp.part_path(run.out, stage, plan["plan_id"], batch_id, entry["attempt"]), run.out, plan["plan_id"], batch_id,
                              stage, plan["agent_type"], ids, document["units"])
        if result.state != "done":
            raise run.stop(1 if result.state == "missing" else 2, "the part of batch %s is %s (%s)" % (batch_id, result.state, result.detail),
                           "re-run the command: only a part that validates counts", batch=named, kept=held)
        found.append((entry, document, result))
    return found


def _read_text(run: Run, path: str, label: str) -> str:
    """A text input that is not a part: a regular file through no link, at most 16 MiB, strict UTF-8. Missing or unreadable is exit 1."""
    data, reason = tp.read_capped(path, tp.MAX_AGENT_INPUT_BYTES, tp.RENDERER_READ_REASONS)
    if data is None:
        raise run.stop(2 if reason == "too-large" else 1, "%s is %s" % (label, "over the size cap" if reason == "too-large" else reason),
                       "re-run the earlier steps, which write it")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise run.stop(2, "%s is not strict UTF-8" % label, "regenerate it with its command") from None


# =============================================================================
# The reference set: threats.md as this run reads it (D-4, S-12)
# =============================================================================

def _level(row: Mapping[str, Any]) -> str:
    return str(row.get("risk_level", "")).strip().title()


class Reference(object):
    """``threats.md``'s reference set: the open and the resolved findings, by canonical ID, in S-2 order, with its frontmatter's baseline block."""

    def __init__(self, text: str, parsed: Mapping[str, Any]) -> None:
        self.text = text
        self.open: List[Dict[str, Any]] = list(parsed["open"])
        self.resolved: List[Dict[str, Any]] = list(parsed["resolved"])
        self.by_id: Dict[str, Dict[str, Any]] = {tp.canonical_finding_id(row["id"]): row for row in self.open + self.resolved}
        self.ids: List[str] = [tp.canonical_finding_id(row["id"]) for row in self.open]
        self.baseline = tachi_parsers.parse_baseline_frontmatter(text)

    def shown(self, finding_id: str) -> str:
        """The ID as Section 7 spells it (``findingId/v1`` keeps that spelling)."""
        return str(self.by_id[finding_id]["id"])

    def level(self, finding_id: str) -> str:
        return _level(self.by_id[finding_id])

    def status(self, finding_id: str) -> Optional[str]:
        status = self.by_id[finding_id].get("delta_status")
        return None if status is None else str(status).upper()

    def category(self, finding_id: str) -> str:
        return CATEGORY_OF_PREFIX[finding_id.partition("-")[0]]

    def order(self, finding_id: str) -> Tuple[int, int, int]:
        """Sections 3 and 4's order: the category tables in turn, then S-2 within one."""
        return (CATEGORY_INDEX[self.category(finding_id)],) + tp.finding_sort_key(finding_id)

    def count(self, level: Optional[str] = None, category: Optional[str] = None, status: Optional[str] = None) -> int:
        return sum(1 for fid in self.ids if (level is None or self.level(fid).lower() == level) and
                   (category is None or self.category(fid) == category) and (status is None or self.status(fid) == status))


def _reference(run: Run, text: str, planned: Sequence[Tuple[str, str, str]]) -> Reference:
    """The reference set of ``text``, held to every digest it was planned over, with every value that it gives checked (S1P-A18).

    ``planned`` is ``[(plan's name, its params.reference_digest, its directory)]``, and a digest that differs keeps that plan's directory (S1P-A47). A reference
    set that D4's reader refuses is exit 2, as is one whose digest differs (RD-9): it is a different run. Each open and resolved row, and the
    frontmatter's baseline block, is then searched for a character that D3's step 10 forbids, which is refused here, where it is taken, naming the finding
    and the field.
    """
    try:
        parsed = tachi_parsers.parse_reference_set(text)
    except tachi_parsers.ReferenceSetError as exc:
        raise run.stop(2, exc.reason, exc.remedy) from None
    current = tp.reference_digest(parsed)
    for plan_name, expected, held in planned:
        if current != expected:
            raise run.stop(2, "the reference set of threats.md differs from the one %s was planned over (params.reference_digest)" % plan_name,
                           "re-run Phase 5, so that the plan is made over this threats.md", kept=held)
    reference = Reference(text, parsed)
    for row in reference.open + reference.resolved:
        problem = tp.forbidden_problem("threats.md", row["id"], row, json_only=True)
        if problem is not None:
            raise run.stop(2, problem, REGENERATE)
    problem = tp.forbidden_problem("threats.md", "its baseline block", reference.baseline, json_only=True)
    if problem is not None:
        raise run.stop(2, problem, REGENERATE)
    return reference


def _tree_findings(reference: Reference) -> List[Tuple[str, Dict[str, Any]]]:
    """The open Critical and High findings, in the manifest's order: Critical first, then High, each in S-2 order (FR-K5.5's one set)."""
    chosen = [(fid, reference.by_id[fid]) for fid in reference.ids if reference.level(fid) in ("Critical", "High")]
    return sorted(chosen, key=lambda pair: (RISK_RANK[_level(pair[1])], tp.finding_sort_key(pair[0])))


# =============================================================================
# The tree files (D14; S1P-A44, S1P-A48, S1P-A60)
# =============================================================================

def tree_name(finding_id: str) -> str:
    """``<id-lowercase>-attack-tree.md``. ``finding_id`` is canonical, so it has passed the allow-list before it becomes part of a path."""
    return "%s-attack-tree.md" % finding_id.lower()


def _check_listing(run: Run, directory: str, written: Collection[str], why: str) -> None:
    """FR-K5.7's listing rule, one predicate for both modes (S1P-A91): a name in ``directory`` that ends in ``.md``, a directory's included, is in ``written``.

    ``trees`` applies it before it writes anything, over the trees it is about to write, so that an earlier run's tree, or a file that a helper put
    there during the tree batches, stops the run before the report batches. ``report`` applies it over the manifest's trees, for a file that appeared
    after ``trees``. Exit 4 names the first five. Nothing is moved or deleted: ``attack-trees/`` has no pre-image (D4), so a move would leave a failed
    run's earlier directory short of its trees, and the remedy is the user's. A name that doesn't end in ``.md``, the manifest or an image, is no tree
    file to FR-K5.7. A name reaches the message as ``ascii`` writes it, so that a character which drives a terminal can't ride in on a file name.
    """
    unlisted = [name for name in sorted(os.listdir(directory)) if name.endswith(".md") and name not in written]
    if unlisted:
        raise run.stop(4, "FR-K5.7: attack-trees/ holds %s, which %s" % (_named([ascii(name)[1:-1] for name in unlisted]), why),
                       "move the file out of attack-trees/ and re-run the command")


def _tree_file(run: Run, path: str, root: str, finding_id: str, where: str) -> Optional[Tuple[bytes, str]]:
    """One tree file after D14's per-file checks: ``(its bytes, its Mermaid source)``, or ``None`` when the file is missing.

    The file is a regular file under ``root`` with no link below it, read as bytes at most ``MAX_PART_BYTES``, and
    ``tachi_parsers.attack_tree_source`` makes the content checks (strict UTF-8, no forbidden character, exactly one closed, non-empty Mermaid
    block), so ``reconcile`` and this script hold a tree to one rule. Any problem it names fails the tree, whichever it is. A tree that fails is
    exit 2 and names the finding; a missing one is the caller's exit 4 (FR-K5.5 applied early).
    """
    problem = tp.path_guard_problem(path, root)
    if problem == "missing":
        return None
    if problem is not None:
        raise run.stop(2, "the %s tree of %s fails the path guard (%s)" % (where, finding_id, problem), "regenerate the tree")
    data, reason = tp.read_capped(path, tp.MAX_PART_BYTES)
    if data is None:   # the guard found a regular file, so this is a file over the cap, or one that changed while we read it
        raise run.stop(2, "the %s tree of %s can't be read (%s)" % (where, finding_id, reason), "regenerate the tree")
    source, problem = tachi_parsers.attack_tree_source(data)
    if problem is not None:
        raise run.stop(2, "the %s tree of %s fails its check (%s)" % (where, finding_id, problem),
                       "regenerate the tree with /tachi.threat-model, or edit the file")
    return data, str(source)


class Baseline(object):
    """The baseline run directory that a trees plan names (``refs.baseline_dir``), once R-6's checks have passed it (D3: a ``refs`` path is a
    candidate, never trusted). It is resolved the first time a carried tree is needed, so a run that carries none never reads it. ``kept`` is the trees
    plan's directory, which a refusal about its ``refs`` names."""

    def __init__(self, run: Run, refs: Mapping[str, str], kept: str) -> None:
        self.run, self.flag, self.kept = run, refs.get("baseline_dir"), kept
        self._directory: Optional[Tuple[Optional[str]]] = None

    def directory(self) -> Optional[str]:
        """The directory, or ``None`` when no baseline is named or it is gone (a carried tree is then missing). Any other refusal is exit 2."""
        if self._directory is None:
            resolution = rules.resolve_baseline(flag=self.flag, baseline_source=None, cwd=Path(self.run.cwd))
            if resolution.run_dir is None and resolution.reason not in ("not-named", "missing"):
                raise self.run.stop(2, "the baseline directory that the plan names fails R-6's checks (%s)" % resolution.reason,
                                    "re-run Phase 5 with a baseline directory inside the working directory", kept=self.kept)
            self._directory = (None if resolution.run_dir is None else os.fspath(resolution.run_dir),)
        return self._directory[0]

    def _path(self, finding_id: str) -> Optional[str]:
        base = self.directory()
        return None if base is None else os.path.join(base, TREE_DIR, tree_name(finding_id))

    def tree(self, finding_id: str) -> Optional[Tuple[bytes, str]]:
        """The baseline's tree of ``finding_id`` after the per-file checks, or ``None`` when it has none. The file is guarded from the working
        directory down, as R-6 guards a baseline file, so a baseline directory that is a link is no way out of it."""
        path = self._path(finding_id)
        return None if path is None else _tree_file(self.run, path, self.run.cwd, finding_id, "baseline")

    def raw(self, finding_id: str) -> Optional[bytes]:
        """The baseline's tree file as it is, for FR-K5.3's byte comparison, or ``None`` when it has none."""
        path = self._path(finding_id)
        if path is None or tp.path_guard_problem(path, self.run.cwd) is not None:
            return None
        return tp.read_capped(path, tp.MAX_PART_BYTES)[0]


def _merge(rule: str, wanted: Sequence[Tuple[str, Mapping[str, Any]]], items: Mapping[str, Mapping[str, Any]],
           reference: Reference) -> Dict[str, Any]:
    """The schema-1.0 manifest that the batch manifests merge into (``threat-model-records.md``; FR-K5.6): Critical first, then High.

    A finding with a batch item takes the item's ``delta_status``, ``action`` and, under Rule 3 alone, ``similarity_score`` (a float, S1P-A43). A
    finding with none is carried from the baseline (Rule 1), and takes Section 7's status. ``report`` recomputes this and compares it with the
    file on disk (FR-K5.7), so the one function writes and checks.
    """
    entries: List[Dict[str, Any]] = []
    for fid, _ in wanted:
        item = items.get(fid)
        if item is not None:
            entry = {"finding_id": fid, "delta_status": item["delta_status"], "action": item["action"]}
            if "similarity_score" in item:
                entry["similarity_score"] = item["similarity_score"]
        else:
            entry = {"finding_id": fid, "delta_status": reference.status(fid) or "NEW", "action": "carried_forward"}
        entry["file_path"] = "%s/%s" % (TREE_DIR, tree_name(fid))
        entries.append(entry)
    counts = {action: sum(1 for entry in entries if entry["action"] == action) for action in tp.TREE_ACTIONS}
    return {"schema_version": "1.0", "rule_applied": rule, "attack_tree_count": len(entries), "trees": entries,
            "summary": {"fresh": counts["generated_fresh"], "carried_forward": counts["carried_forward"], "regenerated": counts["regenerated"]}}


def _plan_rule(run: Run, plan: Mapping[str, Any]) -> str:
    rule = plan["params"].get("rule_applied")
    if rule not in RULES:
        raise run.stop(2, "the trees plan holds no valid params.rule_applied", "re-run the plan step", kept=tp.plan_dir(run.out, "trees", plan["plan_id"]))
    return str(rule)


def _tree_items(run: Run, batches: Sequence[Tuple[Dict[str, Any], Dict[str, Any], Any]]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    """The trees plan's items by canonical ID, and the path that each one's batch input names for its tree."""
    items: Dict[str, Dict[str, Any]] = {}
    paths: Dict[str, str] = {}
    for entry, document, result in batches:
        listed = {tp.canonical_finding_id(name): path for name, path in document["tree_paths"].items()}
        for item in result.part["items"]:
            fid = item["finding_id"]
            if fid in items:
                raise run.stop(2, "two batches hold an item for %s" % fid, "re-run the plan step", batch=(entry["batch_id"], ", ".join(entry["finding_ids"])),
                               kept=tp.plan_dir(run.out, "trees", document["plan_id"]))
            items[fid], paths[fid] = item, listed[fid]
    return items, paths


# =============================================================================
# trees
# =============================================================================

def _trees(run: Run, args: argparse.Namespace) -> int:
    plan, inputs = _guard(run, "trees", args.plan, args.plan_digest)
    rule = _plan_rule(run, plan)
    batches = _batches(run, "trees", plan)
    items, paths = _tree_items(run, batches)
    if "threats" not in inputs:
        raise run.stop(2, "the trees plan has no threats input", "re-run the plan step")
    try:
        text = inputs["threats"].decode("utf-8")
    except UnicodeDecodeError:
        raise run.stop(2, "threats.md is not strict UTF-8", REGENERATE) from None
    reference = _reference(run, text, [("the trees plan", plan["params"]["reference_digest"], run.kept)])
    wanted = _tree_findings(reference)
    wanted_ids = {fid for fid, _ in wanted}
    baseline = Baseline(run, plan["refs"], run.kept)
    trees_dir = os.path.join(tp.plan_dir(run.out, "trees", plan["plan_id"]), "trees")

    found: Dict[str, bytes] = {}
    missing: List[str] = []
    for fid in sorted(set(items) | wanted_ids, key=tp.finding_sort_key):
        item = items.get(fid)
        if item is not None and item["action"] != "carried_forward":
            expected = os.path.join(trees_dir, tree_name(fid))
            if os.path.realpath(paths[fid]) != os.path.realpath(expected):
                raise run.stop(2, "the batch input names %s as the tree of %s, which is not the plan's own trees/ path" % (paths[fid], fid),
                               "re-run the plan step")
            tree = _tree_file(run, expected, run.out, fid, "generated")
        else:   # a Rule 1 tree that no batch generated, or a Rule 3 tree that the agent decided to carry: the baseline's file is the copy
            tree = baseline.tree(fid)
        if tree is None:
            missing.append(fid)
        else:
            found[fid] = tree[0]
    if missing:
        raise run.stop(4, "FR-K5.5: the tree of %s is missing, so Section 7's Critical and High findings, the manifest and the tree files "
                          "are not one set" % _named(missing), "regenerate the missing trees, then run trees again")
    extra = sorted(set(items) - wanted_ids, key=tp.finding_sort_key)
    if extra:
        raise run.stop(4, "FR-K5.5: trees were generated for %s, which are not open Critical or High findings" % _named(extra),
                       "re-run Phase 5, so that the trees plan is made over this threats.md")

    manifest = _merge(rule, wanted, items, reference)
    directory = os.path.join(run.out, TREE_DIR)
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as exc:
        raise run.stop(4, "attack-trees/ could not be created (%s)" % (exc.strerror or "error"), WRITE_REMEDY) from None
    if os.path.islink(directory) or not tp.under(run.out, directory):
        raise run.stop(2, "attack-trees/ is a symbolic link or lies outside --run-dir", "remove it and re-run")
    _check_listing(run, directory, {tree_name(entry["finding_id"]) for entry in manifest["trees"]}, "this run does not write")   # FR-K5.7, early (S1P-A91)
    try:   # the trees first and the manifest last, so the manifest that this run writes lists only trees that are already in place
        for entry in manifest["trees"]:
            tp.atomic_write(os.path.join(run.out, entry["file_path"]), found[entry["finding_id"]])
        tp.atomic_write(os.path.join(run.out, MANIFEST), json.dumps(manifest, indent=2) + "\n")
    except OSError as exc:
        raise run.stop(4, "the trees could not be written (%s)" % (exc.strerror or "error"), WRITE_REMEDY) from None

    accepted = [item for _, _, result in batches for item in result.part["items"]]
    sources = {"threats": tp.sha256_hex(inputs["threats"]), "trees": {fid: tp.sha256_hex(data) for fid, data in found.items()}}
    digest = tp.input_digest({"sources": sources, "params": plan["params"], "items": accepted, "fragments": []})
    counts = {"units": plan["unit_count"], "carried": manifest["summary"]["carried_forward"], "rendered": manifest["attack_tree_count"]}
    record = tp.write_stage_record("trees", RENDERER, run.out, plan, digest, counts, tp.output_entries(run.out, [MANIFEST]), [], [], run.kept)
    print(json.dumps({"stage": "trees", "plan_id": plan["plan_id"], "counts": counts, "outputs": [MANIFEST],
                      "record": tp.stage_record_path(run.out, "trees", plan["plan_id"]), "status": record["status"]}, sort_keys=True))
    return 0


# =============================================================================
# report: the narrative, the parts and the checks
# =============================================================================

_TAXON = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,63}")   # the slot grammar's argument alphabet and length, from a letter on
_LAYER = re.compile(r"L[1-7](?![0-9A-Za-z])")             # a MAESTRO layer's code at the start of its cell: ``L3``, or ``L3 -- Agent Frameworks``


def _category_cells(unit: Mapping[str, Any]) -> Mapping[str, Any]:
    """The cells of a finding's row in its category table (Section 3 or 4) that a findings unit holds under ``category_row``, as ``tachi-stage.py plan --stage
    report`` writes them (T092): decoded, under ``tachi_parts``' item keys, so ``maestro_layer``, ``likelihood``, ``impact`` and, in the two AI tables,
    ``owasp_reference``. A table that lacks a column gives ``""`` there, and a finding with no row in any table gives ``{}``: both read as a value that its table
    lacks. ``part-files.md`` says only that a unit holds "its category-table row", so the outer key is the planner's reading and the inner keys the contract's."""
    cells = unit.get("category_row")
    return cells if isinstance(cells, dict) else {}


def _taxonomy_ids(unit: Mapping[str, Any]) -> frozenset:
    """The taxonomy IDs that a finding carries, as its unit holds them (ADR-050 D3's ``ref`` row): each token of its OWASP Reference cell, and its MAESTRO
    layer's code. A token starts with a letter and holds a digit (``LLM01:2026``, ``CWE-89``, ``T1190``), so the cell's words (``OWASP``) are none. A STRIDE
    table has no reference cell, so its findings carry the layer alone, and a value that its table lacks gives nothing."""
    cells, found = _category_cells(unit), set()
    for token in _TAXON.findall(str(cells.get("owasp_reference") or "")):
        token = token.rstrip(".:-_")
        if any(char.isdigit() for char in token):
            found.add(token)
    layer = _LAYER.match(str(cells.get("maestro_layer") or "").strip())
    if layer is not None:
        found.add(layer.group(0))
    return frozenset(found)


class Narrator(object):
    """Fills a fragment's slots against the reference set, and counts the fields that fall back at assembly (D3's per-field fallback).

    A text that broke the slot grammar or the numeral ban already took its fixed sentence when the part was read. What can still fail here is a
    slot that doesn't resolve: a finding that is not in the reference set, or a ``ref`` that the finding doesn't carry. ``taxa`` maps a finding to its
    taxonomy IDs (``_taxonomy_ids``). In a findings part the text is one finding's, and its ``ref`` must be one of that finding's own; in a section
    fragment, which has no finding, it may be one of any finding that has a unit row (part-files.md, "Stage payload: report").
    """

    def __init__(self, reference: Reference, taxa: Optional[Mapping[str, frozenset]] = None) -> None:
        self.ref, self.fallbacks = reference, 0
        self.taxa: Mapping[str, frozenset] = taxa or {}
        self.any_refs: frozenset = frozenset().union(*self.taxa.values()) if self.taxa else frozenset()

    def lookup(self, kind: str, name: str, finding: Optional[str] = None) -> Optional[str]:
        """The ``report`` slot table's resolutions (part-files.md, "Stage payload: report"). ``None`` when a slot doesn't resolve. ``finding`` is the
        canonical ID of the findings-part item that holds the text, and ``None`` for a section fragment."""
        ref = self.ref
        if kind == "finding":
            return name if name in ref.by_id else None   # the grammar canonicalized it, and it must be in the reference set
        if kind == "name" and name.startswith("component:"):
            row = ref.by_id.get(tp.canonical_finding_id(name[len("component:"):]))
            return None if row is None else str(row["component"])
        if kind == "band" and name.startswith("risk:"):
            fid = tp.canonical_finding_id(name[len("risk:"):])
            return ref.level(fid) if fid in ref.ids else None
        if kind == "count":
            return self._count(name)
        if kind == "pct" and name in tp.REPORT_BANDS:
            shares = ts.largest_remainder({band: ref.count(level=band) for band in tp.REPORT_BANDS})
            return str(shares[name])
        if kind == "ref":
            return name if name in (self.any_refs if finding is None else self.taxa.get(finding, frozenset())) else None
        return None   # pragma: no cover  (a part's grammar admits no other kind here, so only a slot table that grew without this lookup could reach it)

    def _count(self, name: str) -> Optional[str]:
        ref = self.ref
        if name == "open":
            return str(len(ref.ids))
        if name == "resolved":
            return str(len(ref.resolved))
        if name in ("new", "unchanged", "updated"):
            return str(ref.count(status=name.upper()))
        category, _, band = name.partition(".")
        if not band and name in tp.REPORT_BANDS:
            return str(ref.count(level=name))
        if category in tp.REPORT_CATEGORY_KEYS and (not band or band in tp.REPORT_BANDS):
            return str(ref.count(level=band or None, category=category))
        return None   # pragma: no cover  (the part's grammar admits only the arguments above)

    def text(self, value: str, field: str, sink: str = "prose", finding: Optional[str] = None) -> str:
        """``value`` with its slots filled and escaped for ``sink``, or the field's fixed sentence (counted) when a slot doesn't resolve. ``finding`` is
        the canonical ID of the findings-part item that holds ``value``, which scopes its ``ref`` slots; a section fragment passes none."""
        resolved = tp.resolve_narrative(value, "report", lambda kind, name: self.lookup(kind, name, finding), sink)
        if resolved is None:
            self.fallbacks += 1
            sentence = tp.report_fallback(field)
            return tp.escape_prose(sentence) if sink == "prose" else tp.escape_cell(sentence)
        return resolved


class Parts(object):
    """What the report plan's parts hold: the fragments of each section part, the items of each findings part, and the units that they cover."""

    def __init__(self, batches: Sequence[Tuple[Dict[str, Any], Dict[str, Any], Any]]) -> None:
        self.units: Dict[str, List[str]] = {}            # section -> the planned fragment keys, in plan order
        self.fragments: Dict[str, Dict[str, str]] = {}   # section -> fragment key -> text
        self.analysis: Dict[str, Dict[str, Any]] = {}    # canonical ID -> threat_analysis item
        self.rows: Dict[str, Dict[str, Any]] = {}        # canonical ID -> its threat_analysis unit row (the lead's category-table values)
        self.roadmap_rows: Dict[str, Dict[str, Any]] = {}  # canonical ID -> its remediation_roadmap unit row
        self.taxa: Dict[str, frozenset] = {}             # canonical ID -> the taxonomy IDs its unit rows carry (a `ref` slot's allowed set)
        self.roadmap: Dict[str, Dict[str, Any]] = {}     # canonical ID -> remediation_roadmap item
        self.fallbacks = self.truncations = 0
        self.items: List[Dict[str, Any]] = []
        self.listed: List[Tuple[str, str, str]] = []     # (section, key, text) in plan order, for the input digest
        for entry, document, result in batches:
            section = document["units"][0]["section"]
            self.fallbacks += result.counts["narrative_fallbacks"]
            self.truncations += result.counts["truncations"]
            if dict(tp.REPORT_PARTS)[section] == "findings":
                for item in result.part["items"]:
                    (self.analysis if section == "threat_analysis" else self.roadmap)[item["finding_id"]] = item
                    self.items.append(item)
                for unit in document["units"]:
                    fid = tp.canonical_finding_id(unit["finding_id"])
                    (self.rows if section == "threat_analysis" else self.roadmap_rows)[fid] = unit
                    self.taxa[fid] = self.taxa.get(fid, frozenset()) | _taxonomy_ids(unit)
            else:
                self.units.setdefault(section, []).extend(unit["key"] for unit in document["units"])
                for fragment in result.part["fragments"]:
                    self.fragments.setdefault(section, {})[fragment["slot_key"]] = fragment["text"]
                    self.listed.append((section, fragment["slot_key"], fragment["text"]))

    def fragment(self, section: str, key: str) -> Optional[str]:
        return self.fragments.get(section, {}).get(key)


def _strict_json(raw: bytes) -> Any:
    """The manifest's JSON, strictly: no duplicate key, no ``NaN`` or ``Infinity``. ``ValueError`` when it isn't."""
    def unique(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        found: Dict[str, Any] = {}
        for name, value in pairs:
            if name in found:
                raise ValueError("duplicate key")
            found[name] = value
        return found

    def refuse(name: str) -> None:
        raise ValueError(name)

    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=refuse)


def _verify_trees(run: Run, reference: Reference, raw_manifest: bytes, tplan: Mapping[str, Any],
                  items: Mapping[str, Mapping[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Tuple[bytes, str]]]:
    """FR-K5.5, FR-K5.7 and FR-K5.3 (exit 4) and the tree files' own checks (exit 2): ``(manifest, {ID: (file bytes, Mermaid source)})``.

    * **FR-K5.5:** Section 7's Critical and High open IDs, the manifest and the tree files are one set.
    * **FR-K5.7:** every ``.md`` file in ``attack-trees/`` is listed, and the manifest equals its recomputed merge.
    * **FR-K5.3:** every carried tree equals its baseline file.

    Each tree file is a regular file under ``--run-dir`` that passes ``attack_tree_source``, because Section 5 takes its source from the file.
    """
    wanted = _tree_findings(reference)
    wanted_ids = [fid for fid, _ in wanted]
    try:
        manifest = _strict_json(raw_manifest)
    except (ValueError, RecursionError):
        raise run.stop(4, "FR-K5.7: the tree manifest is not strict JSON", "run assemble-report.py trees again") from None
    entries = manifest.get("trees") if isinstance(manifest, dict) else None
    if not isinstance(entries, list) or not all(isinstance(entry, dict) and tp.id_matches("finding", entry.get("finding_id")) for entry in entries):
        raise run.stop(4, "FR-K5.7: the tree manifest is not the schema-1.0 manifest", "run assemble-report.py trees again")
    listed = [tp.canonical_finding_id(entry["finding_id"]) for entry in entries]
    absent = [fid for fid in wanted_ids if fid not in set(listed)]
    extra = [fid for fid in listed if fid not in set(wanted_ids)]
    if absent or extra:
        raise run.stop(4, "FR-K5.5: Section 7's open Critical and High findings and the manifest are not one set (no tree for %s; a tree for %s that is "
                          "no Critical or High finding)" % (_named(absent) or "none", _named(extra) or "none"),
                       "re-run Phase 5, so that the trees are made over this threats.md")
    files = {fid: os.path.join(run.out, TREE_DIR, tree_name(fid)) for fid in listed}
    gone = []
    for fid in listed:
        problem = tp.path_guard_problem(files[fid], run.out)
        if problem == "missing":
            gone.append(fid)
        elif problem is not None:
            raise run.stop(2, "the tree file of %s fails the path guard (%s)" % (fid, problem), "regenerate the tree")
    if gone:
        raise run.stop(4, "FR-K5.5: the tree file of %s is listed in the manifest and missing" % _named(gone), "run assemble-report.py trees again")
    directory = os.path.join(run.out, TREE_DIR)
    if os.path.islink(directory):
        raise run.stop(2, "attack-trees/ is a symbolic link", "remove it and run assemble-report.py trees again")
    _check_listing(run, directory, {tree_name(fid) for fid in listed}, "the manifest does not list")
    if manifest != _merge(_plan_rule(run, tplan), wanted, items, reference):
        raise run.stop(4, "FR-K5.7: the tree manifest is not the merge of the batch manifests that the trees plan holds",
                       "run assemble-report.py trees again")
    trees: Dict[str, Tuple[bytes, str]] = {}
    for fid in listed:
        tree = _tree_file(run, files[fid], run.out, fid, "standalone")
        if tree is None:   # pragma: no cover  (the check above found this file, so it can only be gone if something removed it since)
            raise run.stop(4, "FR-K5.5: the tree file of %s is listed in the manifest and missing" % fid, "run assemble-report.py trees again")
        trees[fid] = tree
    baseline = Baseline(run, tplan["refs"], tp.plan_dir(run.out, "trees", tplan["plan_id"]))
    for entry in entries:
        fid = tp.canonical_finding_id(entry["finding_id"])
        if entry["action"] == "carried_forward":
            original = baseline.raw(fid)
            if original is None or original != trees[fid][0]:
                raise run.stop(4, "FR-K5.3: the carried tree of %s %s" % (fid, "has no baseline file" if original is None else "differs from its baseline file"),
                               "run assemble-report.py trees again")
    return manifest, trees


def _chain_sections(text: str) -> Dict[str, int]:
    """Each chain's ``**Converging chains**: k`` line from the file's Chain Details, by chain ID. ``parse_attack_chains`` doesn't return it."""
    found: Dict[str, int] = {}
    current = None
    for line in text.split("\n"):
        heading = re.match(r"^###\s+(CHAIN-[0-9]{3,6}):", line.strip())
        if heading is not None:
            current = heading.group(1)
            continue
        count = re.match(r"\*\*Converging chains\*\*:\s*([0-9]{1,6})", line.strip())
        if current is not None and count is not None:
            found.setdefault(current, int(count.group(1)))
    return found


def _chains(run: Run, reference: Reference, parts: Parts) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Optional[str]]:
    """The final outcome record, for ``chains written`` the surfaced chains of ``attack-chains.md``, and that file's digest (ADR-050 D13; PM-T3).

    The record in ``threats.md`` governs: Step 2.8's check may have rewritten it as ``skipped`` after the plan was made (R-24), so a planned
    ``attack_chains`` part is then left out and Section 6 prints the outcome. For ``chains written`` the file must hold exactly the planned surfaced
    chains, in the planned order, or the run is exit 2. Each value that this script takes from the file is checked for a forbidden character.
    """
    outcome = tachi_parsers.parse_chain_outcome(reference.text)
    if outcome["form"] != "written":
        return outcome, [], None
    path = os.path.join(run.out, "attack-chains.md")
    problem = tp.path_guard_problem(path, run.out)
    if problem is not None:   # a file the plan lists as an input is missing (exit 1), or it is a link or no regular file (exit 2)
        raise run.stop(1 if problem == "missing" else 2,
                       "the outcome says chains were written, but attack-chains.md fails the path guard (%s)" % problem,
                       "run attack-chains.py check, which rewrites the record, or regenerate attack-chains.md")
    text = _read_text(run, path, "attack-chains.md")
    surfaced = [chain for chain in tachi_parsers.parse_attack_chains(text) if chain["surfaced"]]
    planned = [key[len("chain."):] for key in parts.units.get("attack_chains", [])]
    if [chain["chain_id"] for chain in surfaced] != planned:
        raise run.stop(2, "attack-chains.md does not hold exactly the planned surfaced chains (it holds %s; the plan has %s)" % (
            _named([chain["chain_id"] for chain in surfaced]) or "none", _named(planned) or "none"),
            "re-run Phase 5, so that the report plan is made over this attack-chains.md")
    converging = _chain_sections(text)
    for chain in surfaced:
        chain["converging"] = converging.get(chain["chain_id"])
        problem = tp.forbidden_problem("attack-chains.md", chain["chain_id"], {
            "title": chain["title"], "layers": chain["layers"], "max_severity": chain["max_severity"], "findings": chain["findings"],
            "chain_breaking_controls": chain["chain_breaking_controls"]}, json_only=True)
        if problem is not None:
            raise run.stop(2, problem, "regenerate attack-chains.md with attack-chains.py render, or edit the value")
    return outcome, surfaced, tp.sha256_hex(text.encode("utf-8"))


# =============================================================================
# report: the sections
# =============================================================================

class Doc(object):
    """What the section builders read and write: the inputs, the section numbers, and what the report puts where."""

    def __init__(self, run: Run, reference: Reference, parts: Parts, manifest: Mapping[str, Any], trees: Mapping[str, Tuple[bytes, str]],
                 outcome: Mapping[str, Any], chains: Sequence[Mapping[str, Any]]) -> None:
        self.run, self.ref, self.parts, self.manifest, self.trees, self.outcome, self.chains = run, reference, parts, manifest, trees, outcome, chains
        self.narr = Narrator(reference, parts.taxa)
        groups = tachi_parsers.parse_correlation_groups(reference.text, reference.ids)["groups"]
        self.group_of = {member: group for group in groups for member in group["members"]}   # the first group that lists an ID claims it
        self.used: set = set()                                                                 # the units whose content the file holds
        self.places: Dict[str, List[Tuple[int, str]]] = {}                                     # finding -> (section number, heading) for the appendix
        self.has_patterns = "agentic_patterns" in parts.units
        self.has_delta = "delta_summary" in parts.units
        order = ["exec", "architecture", "threats", "themes", "trees", "chains"] + (["patterns"] if self.has_patterns else []) + [
            "roadmap", "appendix"] + (["delta"] if self.has_delta else [])
        self.number = {name: position for position, name in enumerate(order, 1)}

    def place(self, finding_id: str, number: int, heading: str) -> None:
        self.places.setdefault(finding_id, []).append((number, heading))

    def fragment(self, section: str, key: str, sink: str = "prose") -> Optional[str]:
        """A section part's fragment with its slots filled and escaped, or ``None`` when the part holds none for ``key``."""
        text = self.parts.fragment(section, key)
        if text is None:
            return None
        self.used.add((section, key))
        return self.narr.text(text, key, sink)

    def peers_of(self, finding_id: str) -> List[str]:
        group = self.group_of.get(finding_id)
        return [] if group is None else [member for member in group["members"] if member != finding_id]


def _heading(number: int, title: str) -> List[str]:
    return ["## %d. %s" % (number, title), ""]


def _section_executive(doc: Doc) -> List[str]:
    number = doc.number["exec"]
    lines = _heading(number, TITLES[1])
    for title, key in (("Risk Posture", "risk_posture"), ("Top 5 Threats by Business Impact", "top_threats"),
                       ("Key Recommendations", "key_recommendations"), ("Compliance Relevance", "compliance")):
        text = doc.fragment("exec_summary", key)
        if text is not None:
            lines += ["### " + title, "", text, ""]
    lines += ["### Remediation Timeline", ""]
    for level, tier in TIERS:
        count = doc.ref.count(level=level.lower())
        if count:
            lines.append("- **%s** (%d %s findings)" % (tier, count, level))
    return lines + [""]


def _section_architecture(doc: Doc) -> List[str]:
    lines = _heading(doc.number["architecture"], TITLES[2])
    for title, key in (("System Context", "system_context"), ("Trust Boundary Summary", "trust_boundaries")):
        lines += ["### " + title, "", doc.fragment("architecture_overview", key) or "", ""]
    return lines


def _lead(doc: Doc, finding_id: str) -> str:
    """A narrated finding's lead: its ID, component, MAESTRO layer, likelihood, impact and risk level, and its status in a baseline run, with a dash
    for a value that its category table lacks (the batch input's ``category_row`` holds the category-table values; Section 7's row the rest)."""
    row = _category_cells(doc.parts.rows.get(finding_id, {}))

    def cell(name: str) -> str:
        return tp.escape_cell(str(row.get(name) or DASH))

    fields = ["**%s**: %s" % (doc.ref.shown(finding_id), tp.escape_cell(str(doc.ref.by_id[finding_id]["component"]))),
              "**MAESTRO Layer**: " + cell("maestro_layer"), "**Likelihood**: " + cell("likelihood"), "**Impact**: " + cell("impact"),
              "**Risk Level**: " + tp.escape_cell(doc.ref.level(finding_id))]
    if doc.ref.baseline["has_baseline"]:
        fields.append("**Status**: " + tp.escape_cell(doc.ref.status(finding_id) or DASH))
    return " | ".join(fields)


def _section_threats(doc: Doc) -> List[str]:
    number = doc.number["threats"]
    lines = _heading(number, TITLES[3])
    overview = doc.fragment("threat_categories", "overview")
    if overview is not None:
        lines += [overview, ""]
    for index, (key, heading, short) in enumerate(CATEGORIES, 1):
        title = "3.%d %s" % (index, heading)
        lines += ["### " + title, ""]
        findings = [fid for fid in doc.ref.ids if doc.ref.category(fid) == key]
        if not findings:
            lines += ["No %s threats were identified in this threat model." % short, ""]
            continue
        overview = doc.fragment("threat_categories", "category." + key)
        if overview is not None:
            lines += [overview, ""]
        for fid in findings:
            doc.place(fid, number, title)
            item = doc.parts.analysis.get(fid)
            if item is not None:   # a summarized finding has no item of its own: its category's summary covers it
                doc.used.add(("threat_analysis", fid))
                lines += [_lead(doc, fid), "", doc.narr.text(item["narrative"], "narrative", finding=fid), ""]
        summary = doc.fragment("threat_categories", "summary." + key)
        if summary is not None:
            lines += [summary, ""]
    return lines


def _themes(doc: Doc) -> List[Tuple[int, str, str, Optional[str]]]:
    """``[(n, title, body, raw body)]`` for each theme that the part holds, in order. The title takes the cell sink, a heading being one line.

    ``raw body`` is the text whose ``finding`` slots the appendix reads, and it is ``None`` when the body fell back at assembly: a body that shows the fixed
    sentence discusses no finding, so it places none."""
    found = []
    number = 1
    while doc.parts.fragment("cross_cutting_themes", "theme.%d.title" % number) is not None:
        title = doc.narr.text(doc.parts.fragment("cross_cutting_themes", "theme.%d.title" % number), "theme.%d.title" % number, "cell")
        raw = doc.parts.fragment("cross_cutting_themes", "theme.%d.body" % number)
        before = doc.narr.fallbacks
        body = doc.narr.text(raw, "theme.%d.body" % number)
        found.append((number, title, body, raw if doc.narr.fallbacks == before else None))
        number += 1
    return found


def _section_themes(doc: Doc) -> List[str]:
    number = doc.number["themes"]
    lines = _heading(number, TITLES[4])
    themes = _themes(doc)
    if not themes:
        return lines + [NO_THEMES_NOTE, ""]
    doc.used.add(("cross_cutting_themes", "themes"))
    for n, title, body, raw in themes:
        heading = "Theme %d: %s" % (n, title)
        lines += ["### " + heading, "", body, ""]
        for cited in sorted(set(re.findall(r"\{\{finding:([A-Za-z0-9_.:-]{1,64})\}\}", raw or "")), key=str):
            if tp.id_matches("finding", cited) and tp.canonical_finding_id(cited) in doc.ref.by_id:
                doc.place(tp.canonical_finding_id(cited), number, heading)
    return lines


def _section_trees(doc: Doc) -> List[str]:
    number = doc.number["trees"]
    lines = _heading(number, TITLES[5])
    if not doc.manifest["trees"]:
        return lines + [NO_TREE_NOTE, ""]
    baseline = doc.ref.baseline
    for entry in doc.manifest["trees"]:
        fid = entry["finding_id"]
        row = doc.ref.by_id[fid]
        heading = "%s: %s" % (doc.ref.shown(fid), tp.escape_cell(str(row["threat"])))
        item = doc.parts.analysis.get(fid)
        summary = None if item is None else item["tree_summary"]
        meta = ["**Risk Level**: " + tp.escape_cell(doc.ref.level(fid)), "**Component**: " + tp.escape_cell(str(row["component"]))]
        if baseline["has_baseline"]:
            meta.append("**Status**: " + tp.escape_cell(doc.ref.status(fid) or DASH))
        source = doc.trees[fid][1]
        fence = tp.fence_for(source)
        lines += ["### " + heading, "", " | ".join(meta), ""]
        if summary is not None:
            lines += [doc.narr.text(summary, "tree_summary", finding=fid), ""]
        lines += [fence + "mermaid", source, fence, ""]
        if baseline["has_baseline"]:
            if entry["action"] == "carried_forward":
                lines += ["> _Unchanged from baseline (%s)._" % tp.escape_cell(str(baseline["date"] or DASH)), ""]
            else:
                lines += ["> _Context changed since baseline " + DASH + " attack tree regenerated._", ""]
        peers = doc.peers_of(fid)
        if peers:
            lines += ["> Correlated with %s (%s)." % (", ".join(doc.ref.shown(peer) for peer in peers), doc.group_of[fid]["group_id"]), ""]
        doc.place(fid, number, heading)
    return lines


def _section_chains(doc: Doc) -> List[str]:
    number = doc.number["chains"]
    lines = _heading(number, TITLES[6])
    if not doc.chains:
        text = doc.outcome["text"]
        if text is None:   # no record, several, or one that is no form: the line's own text never leaves the parser
            return lines + ["No attack chain outcome record is readable in threats.md.", ""]
        return lines + ["No cross-layer attack chains are reported. The attack chain outcome is: %s." % text, ""]
    for chain in doc.chains:
        heading = "%s: %s" % (chain["chain_id"], tp.escape_cell(chain["title"]))
        narrative = doc.fragment("attack_chains", "chain." + chain["chain_id"])
        facts = ["**Layers**: " + tp.escape_cell(" \u2192 ".join(chain["layers"])), "**Max Severity**: " + tp.escape_cell(chain["max_severity"]),
                 "**Findings**: %d" % len(chain["findings"])]
        if chain["converging"] is not None:
            facts.append("**Converging chains**: %d" % chain["converging"])
        lines += ["### " + heading, "", " | ".join(facts), "", narrative or "", ""]
        for control in chain["chain_breaking_controls"][:1]:
            where = " at layer " + tp.escape_cell(control["target_layer"]) if control["target_layer"] else ""
            lines += ["**Chain-Breaking Control**: %s%s. %s" % (tp.escape_cell(control["target_finding_id"]), where,
                                                                 tp.escape_cell(control["recommendation"])), ""]
        lines += [CHAIN_DISCLAIMER, "", "**Impacted Findings**: " + "; ".join(
            "%s (%s, %s)" % tuple(tp.escape_cell(member[name]) for name in ("finding_id", "maestro_layer", "role")) for member in chain["findings"]), ""]
        for member in chain["findings"]:
            if tp.id_matches("finding", member["finding_id"]) and tp.canonical_finding_id(member["finding_id"]) in doc.ref.by_id:
                doc.place(tp.canonical_finding_id(member["finding_id"]), number, heading)
    return lines


def _section_patterns(doc: Doc) -> List[str]:
    number = doc.number["patterns"]
    title = PATTERN_TITLE
    lines = _heading(number, title) + [PATTERN_INTRO, ""]
    ref = doc.ref
    multiple = [fid for fid in sorted(ref.ids, key=ref.order) if ref.by_id[fid].get("agentic_pattern") == "multiple"]
    if multiple:
        lines += ["### Multi-Pattern Findings", "", doc.fragment("agentic_patterns", "multi") or "",
                  "", "Impacted findings: " + ", ".join(tp.escape_cell(ref.shown(fid)) for fid in multiple), ""]
        for fid in multiple:
            doc.place(fid, number, "Multi-Pattern Findings")
    held = []
    for index, (value, display, definition) in enumerate(PATTERNS):
        findings = [fid for fid in sorted(ref.ids, key=ref.order) if ref.by_id[fid].get("agentic_pattern") == value]
        if findings:
            rank = min(RISK_RANK.get(ref.level(fid), len(RISK_RANK)) for fid in findings)
            held.append((rank, -len(findings), index, value, display, definition, findings))
    for _, _, _, value, display, definition, findings in sorted(held):
        counts = " | ".join("%s: %d" % (level, sum(1 for fid in findings if ref.level(fid) == level)) for level in tp.RISK_LEVELS[:4])
        lines += ["### " + display, "", definition, "", counts, "", "Impacted findings: " + ", ".join(tp.escape_cell(ref.shown(fid)) for fid in findings),
                  "", doc.fragment("agentic_patterns", "pattern." + value) or "", ""]
        for fid in findings:
            doc.place(fid, number, display)
    return lines


def _roadmap(doc: Doc) -> List[Dict[str, Any]]:
    """The roadmap's rows: every open finding but a correlation group's non-primary member (D8, S1P-A20), ordered by risk level, then component, then
    S-2. A group's row stands for the group: it takes the primary's component and the group's highest risk level."""
    ref = doc.ref
    rows = []
    for fid in ref.ids:
        group = doc.group_of.get(fid)
        if group is not None and group["primary"] != fid:
            continue
        members = group["members"] if group is not None else [fid]
        level = min((ref.level(member) for member in members), key=lambda name: RISK_RANK.get(name, len(RISK_RANK)))
        rows.append({"id": fid, "members": members, "group": None if group is None else group["group_id"], "level": level,
                     "component": str(ref.by_id[fid]["component"])})
    return sorted(rows, key=lambda row: (RISK_RANK.get(row["level"], len(RISK_RANK)), row["component"].casefold(), row["component"],
                                         tp.finding_sort_key(row["id"])))


def _section_roadmap(doc: Doc) -> List[str]:
    number = doc.number["roadmap"]
    ref = doc.ref
    rows = _roadmap(doc)
    items = doc.parts.roadmap
    if set(items) != {row["id"] for row in rows}:
        raise doc.run.stop(2, "the roadmap parts hold items for %s, and Section 7 and Section 4a give rows for %s" % (
            _named(sorted(items, key=tp.finding_sort_key)) or "none", _named([row["id"] for row in rows]) or "none"),
            "re-run Phase 5, so that the report plan is made over this threats.md")
    tiers = dict(TIERS)
    per_tier = collections.Counter(tiers.get(row["level"], "Backlog") for row in rows)
    components = collections.Counter(str(row["component"]) for row in ref.open)
    most = min(components, key=lambda name: (-components[name], name)) if components else None
    lines = _heading(number, TITLES[7])
    lines += ["The roadmap lists %d rows, ordered by risk level and then by component: %s. The most impacted component is %s, with %d open "
              "findings." % (len(rows), ", ".join("%d %s" % (per_tier[tier], tier) for tier in ("Immediate", "Short-term", "Medium-term", "Backlog")
                                                   if per_tier[tier]) or "none", DASH if most is None else tp.escape_cell(most),
                              0 if most is None else components[most]), "",
              "| Finding ID | Component | Mitigation | Effort | Dependencies |", "|---|---|---|---|---|"]
    for row in rows:
        fid, item = row["id"], items[row["id"]]
        if row["group"] is None:
            mitigation = str(ref.by_id[fid]["mitigation"])
            dependencies = None if item["dependencies"] is None else doc.narr.text(item["dependencies"], "dependencies", "cell", finding=fid)
        else:
            mitigation = "; ".join("%s: %s" % (ref.shown(member), ref.by_id[member]["mitigation"]) for member in row["members"])
            note = "Correlated: %s (%s)." % (", ".join(ref.shown(member) for member in row["members"]), row["group"])
            dependencies = note if item["dependencies"] is None else note + " " + doc.narr.text(item["dependencies"], "dependencies", "cell", finding=fid)
        lines.append("| %s | %s | %s | %s | %s |" % (tp.escape_cell(ref.shown(fid)), tp.escape_cell(row["component"]), tp.escape_cell(mitigation),
                                                    item["effort"], "None" if dependencies is None else dependencies))
        doc.used.add(("remediation_roadmap", fid))
        for member in row["members"]:
            doc.place(member, number, TITLES[7])
    return lines + [""] + TIER_TABLE + [""] + EFFORT_TABLE + [""]


def _section_appendix(doc: Doc) -> List[str]:
    lines = _heading(doc.number["appendix"], TITLES[8])
    lines += ["| Finding ID | Report Section | Heading Reference |", "|---|---|---|"]
    for fid in doc.ref.ids:
        for number, heading in sorted(set(doc.places.get(fid, []))):
            lines.append("| %s | %d | %s |" % (tp.escape_cell(doc.ref.shown(fid)), number, tp.escape_cell(heading)))
    return lines + [""]


def _section_delta(doc: Doc) -> List[str]:
    ref, baseline = doc.ref, doc.ref.baseline
    counts = {"NEW": ref.count(status="NEW"), "UNCHANGED": ref.count(status="UNCHANGED"), "UPDATED": ref.count(status="UPDATED"),
              "RESOLVED": len(ref.resolved)}
    lines = _heading(doc.number["delta"], TITLES[9]) + ["### Finding Lifecycle Breakdown", "", "| Status | Count | Description |", "|---|---|---|"]
    lines += ["| %s | %d | %s |" % (status, counts[status], description) for status, description in LIFECYCLE]
    lines += ["| **Total** | %d | Sum of all findings (active + resolved) |" % sum(counts.values()), "",
              "### Remediation Progress", "", doc.fragment("delta_summary", "progress") or "", "", "### Baseline Reference", "",
              "| Field | Value |", "|---|---|"]
    for field, key in (("Source", "source"), ("Date", "date"), ("Baseline Findings", "finding_count"), ("Run ID", "run_id")):
        lines.append("| %s | %s |" % (field, tp.escape_cell(str(baseline[key] if baseline[key] is not None else DASH))))
    return lines + [""]


def _frontmatter(doc: Doc, date: str, source_file: str) -> List[str]:
    ref, baseline = doc.ref, doc.ref.baseline
    delta = ({"new": ref.count(status="NEW"), "unchanged": ref.count(status="UNCHANGED"), "updated": ref.count(status="UPDATED"),
              "resolved": len(ref.resolved)} if baseline["has_baseline"] else {name: None for name in ("new", "unchanged", "updated", "resolved")})
    lines = ["```yaml", "---", 'schema_version: "1.1"', 'date: "%s"' % date, "source_file: " + tp.yaml_quoted(source_file),
             "finding_count: %d" % len(ref.ids), "risk_distribution:"]
    lines += ["  %s: %d" % (level, ref.count(level=level.lower())) for level in tp.RISK_LEVELS[:4]]
    lines += ["attack_tree_count: %d" % doc.manifest["attack_tree_count"], "baseline_source: " + tp.yaml_quoted(baseline["source"]),
              "baseline_date: " + tp.yaml_quoted(baseline["date"]), "delta_counts:"]
    lines += ["  %s: %s" % (name, "null" if value is None else value) for name, value in delta.items()]
    return lines + ["---", "```", ""]


def _assemble(doc: Doc, date: str, source_file: str, digest: str) -> str:
    """The whole file: the frontmatter, the sections in template order, and the provenance stamp (D4), ending in one newline."""
    builders = [("exec", _section_executive), ("architecture", _section_architecture), ("threats", _section_threats),
                ("themes", _section_themes), ("trees", _section_trees), ("chains", _section_chains)]
    if doc.has_patterns:
        builders.append(("patterns", _section_patterns))
    builders += [("roadmap", _section_roadmap)]
    sections = {name: build(doc) for name, build in builders}
    # The appendix and the delta summary read the places that the sections above recorded, so they come last and are put in their own order.
    sections["appendix"] = _section_appendix(doc)
    if doc.has_delta:
        sections["delta"] = _section_delta(doc)
    lines = _frontmatter(doc, date, source_file)
    for name in sorted(sections, key=doc.number.get):
        lines += sections[name]
    return "\n".join(lines + [tp.stamp_comment(RENDERER, digest), ""])


def _check_staged(doc: Doc, digest: str) -> Any:
    """The from-disk check of the staged file (P1-4: it compares with the sources, never with a second read by its own reader): no character of
    step 10's set (P0-4's backstop), the stamp, the section list, and each tree's source embedded as its standalone file holds it (FR-K5.2)."""
    def check(staged: Mapping[str, str]) -> List[str]:
        text = staged[REPORT]
        problems = []
        bad = tp.forbidden_character(text)
        if bad is not None:
            problems.append("the staged report holds the character U+%04X, which the part contract forbids" % ord(bad))
        stamp = tp.read_stamp(text)
        if stamp is None or (stamp["renderer"], stamp["input_digest"]) != (RENDERER, digest):
            problems.append("the staged report's provenance stamp is missing or is not this run's")
        outside = text
        for fid, (_, source) in doc.trees.items():   # FR-K5.2: each tree's source is in the file as its standalone file holds it
            fence = tp.fence_for(source)
            block = "%smermaid\n%s\n%s\n" % (fence, source, fence)
            if block not in outside:
                problems.append("the staged report does not hold the Mermaid source of %s as its standalone file does" % fid)
            outside = outside.replace(block, "", 1)   # a tree's own lines are no heading, whatever they say
        numbered = [int(found) for found in re.findall(r"(?m)^## ([0-9]{1,2})\. ", outside)]
        if numbered != list(range(1, len(doc.number) + 1)):
            problems.append("the staged report's sections are not numbered 1 to %d in order" % len(doc.number))
        return problems

    return check


def _check_plan(run: Run, reference: Reference, parts: Parts) -> None:
    """The report plan against the reference set that it was planned over (part-files.md, "Stage payload: report"; exit 2).

    The reference digest says that Section 7 hasn't changed since the plan, so what the plan holds must be what that reference set implies. A plan that
    differs is a planner's defect, and the report would lose a finding's text or print a section that has none, silently: the appendix is built from where
    the file puts a finding, so it can't show a narrative that was never written. Four rules:

    * **Narrated or summarized.** With more than ``NARRATE_LIMIT`` open findings, a Medium, Low or Note finding is summarized, and every other open
      finding is narrated one by one (the contract's words, so a finding with another risk level is narrated). The analysis parts hold an item for each
      narrated finding and for no other.
    * **Summaries.** ``threat_categories`` plans ``summary.<category>`` for each category that has a summarized finding, and for no other.
    * **Patterns.** ``agentic_patterns`` is planned when an open finding has a pattern. Its units are ``pattern.<value>`` for each of the six values that
      Section 7 holds, and ``multi`` when it holds ``multiple``.
    * **Delta.** ``delta_summary`` is planned when the run has a baseline.
    """
    ids = reference.ids
    narrated = [fid for fid in ids if len(ids) <= NARRATE_LIMIT or reference.level(fid) not in ("Medium", "Low", "Note")]
    held = {tp.canonical_finding_id(fid) for fid in parts.analysis}
    if held != set(narrated):
        raise run.stop(2, "the analysis parts hold items for %s, and Section 7's narration rule gives %s" % (
            _named(sorted(held, key=tp.finding_sort_key)) or "none", _named(sorted(narrated, key=tp.finding_sort_key)) or "none"),
            "re-run Phase 5, so that the report plan is made over this threats.md")
    summarized = sorted({reference.category(fid) for fid in ids if fid not in set(narrated)}, key=CATEGORY_INDEX.get)
    units = parts.units.get("threat_categories", [])
    planned = sorted({key[len("summary."):] for key in units if key.startswith("summary.")}, key=lambda name: CATEGORY_INDEX.get(name, len(CATEGORY_INDEX)))
    if planned != summarized:
        raise run.stop(2, "the report plan holds category summaries for %s, and Section 7 has summarized findings in %s" % (
            _named(planned) or "no category", _named(summarized) or "no category"), "re-run Phase 5, so that the report plan is made over this threats.md")
    values = {str(reference.by_id[fid].get("agentic_pattern")) for fid in ids}
    wanted = (["pattern." + value for value in tp.REPORT_PATTERNS if value in values] + (["multi"] if "multiple" in values else []))
    if sorted(parts.units.get("agentic_patterns", [])) != sorted(wanted):
        raise run.stop(2, "the report plan holds pattern units %s, and Section 7 gives %s" % (
            _named(parts.units.get("agentic_patterns", [])) or "none", _named(wanted) or "none"),
            "re-run Phase 5, so that the report plan is made over this threats.md")
    if ("delta_summary" in parts.units) != bool(reference.baseline["has_baseline"]):
        raise run.stop(2, "the report plan holds %s delta summary, and the run has %s baseline" % (
            "a" if "delta_summary" in parts.units else "no", "a" if reference.baseline["has_baseline"] else "no"),
            "re-run Phase 5, so that the report plan is made over this threats.md")


def _report(run: Run, args: argparse.Namespace) -> int:
    plan, inputs = _guard(run, "report", args.plan, args.plan_digest, UNPINNED_REPORT)
    params = plan["params"]
    trees_id, pinned = params.get("trees_plan_id"), plan["inputs"].get("trees_plan")
    date = params.get("scoring_date")
    if not tp.id_matches("plan", trees_id) or pinned is None or not isinstance(date, str) or "tree_manifest" not in inputs:
        raise run.stop(2, "the report plan doesn't pin a trees plan and a tree manifest, or has no date", "re-run the plan step")
    for name, own in (("trees_plan", tp.plan_path(run.out, "trees", trees_id)), ("tree_manifest", os.path.join(run.out, MANIFEST))):
        if os.path.realpath(plan["inputs"][name]["path"]) != os.path.realpath(own):   # a pinned input is read where the plan says, so it must be the run's own file
            raise run.stop(2, "the report plan's %s input is not the file that --run-dir holds" % name, "re-run the plan step")
    tplan, _ = _guard(run, "trees", trees_id, pinned["sha256"], UNPINNED_TREES_IN_REPORT, "the report plan")
    tbatches, rbatches = _batches(run, "trees", tplan), _batches(run, "report", plan)
    titems, _ = _tree_items(run, tbatches)

    threats = os.path.join(run.out, "threats.md")
    named = plan["inputs"].get("threats")   # the file is read from --run-dir, so the plan must name that one
    if named is None or os.path.realpath(named["path"]) != os.path.realpath(threats):
        raise run.stop(2, "the report plan's threats input is not threats.md in --run-dir", "re-run the plan step")
    reference = _reference(run, _read_text(run, threats, "threats.md"),
                           [("the report plan", params["reference_digest"], run.kept),
                            ("the trees plan", tplan["params"]["reference_digest"], tp.plan_dir(run.out, "trees", tplan["plan_id"]))])
    parts = Parts(rbatches)
    for section in ("exec_summary", "architecture_overview", "threat_categories", "cross_cutting_themes"):
        if section not in parts.units:
            raise run.stop(2, "the report plan holds no %s part" % section, "re-run the plan step")
    for row in list(parts.rows.values()) + list(parts.roadmap_rows.values()):
        problem = tp.forbidden_problem("a batch input", row.get("finding_id"), row, json_only=True)
        if problem is not None:
            raise run.stop(2, problem, "re-run the plan step over a regenerated threats.md")
    outcome, chains, chains_digest = _chains(run, reference, parts)
    manifest, trees = _verify_trees(run, reference, inputs["tree_manifest"], tplan, titems)
    for fid in parts.analysis:
        if fid not in reference.ids:
            raise run.stop(2, "the analysis part holds an item for %s, which is not an open finding" % fid, "re-run Phase 5")
    for entry in manifest["trees"]:
        item = parts.analysis.get(entry["finding_id"])
        if item is None or item["tree_summary"] is None:
            raise run.stop(2, "the analysis parts hold no tree summary for %s" % entry["finding_id"], "re-run Phase 5")
    _check_plan(run, reference, parts)

    doc = Doc(run, reference, parts, manifest, trees, outcome, chains)
    sources = {"tree_manifest": tp.sha256_hex(inputs["tree_manifest"]), "reference": params["reference_digest"], "outcome": outcome["text"],
               "trees": {fid: tp.sha256_hex(data) for fid, (data, _) in trees.items()}, "attack_chains": chains_digest}
    digest = tp.input_digest({"sources": sources, "params": {name: value for name, value in params.items() if name != "trees_plan_id"},
                              "items": parts.items,
                              "fragments": [list(entry) for entry in parts.listed if chains or entry[0] != "attack_chains"]})
    text = _assemble(doc, date, tp.relative_path(threats, run.cwd) or "threats.md", digest)
    tp.stage_and_move("report", run.out, plan["plan_id"], {REPORT: text}, _check_staged(doc, digest), run.kept)
    counts = {"units": plan["unit_count"], "rendered": len(doc.used), "narrative_fallbacks": parts.fallbacks + doc.narr.fallbacks,
              "truncations": parts.truncations}
    record = tp.write_stage_record("report", RENDERER, run.out, plan, digest, counts, tp.output_entries(run.out, [REPORT]), [], [], run.kept)
    print(json.dumps({"stage": "report", "plan_id": plan["plan_id"], "counts": counts, "outputs": [REPORT],
                      "record": tp.stage_record_path(run.out, "report", plan["plan_id"]), "status": record["status"]}, sort_keys=True))
    return 0


# =============================================================================
# The command line
# =============================================================================

def _build_parser() -> argparse.ArgumentParser:
    parser = tp.build_parser(RENDERER, "Copy the attack trees (trees) or assemble the threat report (report) from their parts (F-374, ADR-050 D14).", out=False)
    parser.add_argument("mode", choices=("trees", "report"), help="trees: copy the trees and merge the manifests; report: assemble threat-report.md")
    parser.add_argument("--run-dir", required=True, help="the run's output directory; everything is written under it")
    return parser


def _run(args: argparse.Namespace) -> int:
    out = tp.entry_arguments(args.mode, args.run_dir, args.plan, args.plan_digest, option="--run-dir")
    run = Run(args.mode, out, args.plan)
    return _trees(run, args) if args.mode == "trees" else _report(run, args)


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    return tp.run_entry(args.mode, RENDERER, args, _run, option="--run-dir")


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_runtime_floor_374.py, test_write_confinement.py)
    raise SystemExit(main())
