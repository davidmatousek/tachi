#!/usr/bin/env python3
"""Form Phase 3.5's attack chains, render ``attack-chains.md`` and check it (F-374; ADR-050 D13; S-2 and S-3 of the spec).

    python3 scripts/attack-chains.py plan   --run-dir DIR
    python3 scripts/attack-chains.py render --run-dir DIR
    python3 scripts/attack-chains.py check  --run-dir DIR --plan ID

A model can't meet S-3(g)'s bound or SC-2's determinism at fixture scale (C-2), so shipped code forms the chains and the orchestrator
writes a title and a narrative for each surfaced chain only (R-19). ``plan`` and ``render`` run in the orchestrator's Phase 3.5, after the
join, and the orchestrator carries on whatever they return (R-24). ``check`` runs in the main session. Every mode takes ``--run-dir``, the
run's output directory, and writes only under it.

**plan** reads Section 7 of the compiled ``threats.md`` through the reference-set wrapper (``tachi_parsers.parse_reference_set``) and the
persisted Phase 1 inventory (``.tachi-build/phase1/inventory.json``), forms the chains and writes ``.tachi-build/chains/chains.json``
(``tachi.chains/1``), on every run, unusable inputs included. It prints one JSON object: the outcome, the three counts and the surfaced
chains, which are the ones the orchestrator writes narratives for. It writes nothing else.

- **The finding set.** The findings of Section 7 with a STRIDE prefix (S, T, R, I, D, E) on a layer from L1 to L7. A finding's layer is
  the first of these that holds one: Section 7's MAESTRO Layer cell, its own row in a per-finding table (both read by
  ``tachi_parsers.parse_finding_layers``), or its component's layer in the inventory. A value that is not L1 to L7, such as
  ``Unclassified``, leaves the finding out. Component names are compared after casefolding and collapsing whitespace.
- **Links (S-3(b)).** F_a -> F_b is a link when the two findings are on different layers, one component is reachable from the other through
  the flow graph's transitive closure, in either direction (a direct flow is one hop), and (category, layer) -> (category, layer) is a row
  of ``TRANSITIONS``. Narrowing the closure or the table changes which findings can link, so it goes to the PM first (R-21).
- **Assembly (S-3(c)).** Findings are taken by severity, highest first, then in S-2 order. Each one with an outgoing link starts one
  chain, which extends from its last finding to the first candidate, in that order, on a layer the chain doesn't have yet. C is the number
  of chains assembled.
- **Consolidation (S-3(d)).** Chains with identical finding sets keep the higher-ranked one. A chain needs a Critical or High finding.
  A chain whose ordered findings are a contiguous run of a longer surviving chain is folded into it. N is what remains.
- **Ranking and IDs (S-3(e)).** By max severity, then layer count, then the ordered finding IDs in S-2 order, so no two chains tie.
  ``CHAIN-`` and the rank, padded to three digits.
- **Surfacing (S-3(f)).** In rank order, a chain surfaces unless a surfaced chain ends at the same terminal-impact finding, until five
  have. Each one records ``converging``: how many other consolidated chains end at its terminal-impact finding. S is the number surfaced.
- **The chain-breaking target (orchestrator Step 4).** Two findings: the higher severity, the first on a tie. Three: the middle one.
  Four or more: the intermediate finding with the greatest i x (n - 1 - i), then the higher severity, then the earlier. Its Mitigation,
  verbatim from Section 7, is the recommendation, and ``render`` reads it under ``reference_digest``, so ``chains.json`` carries only the
  target's ID (its key set is closed, S1P-A30).
- **The outcome.** ``written`` when N >= 1. Otherwise ``zero``, with the first of four reasons that applies (no STRIDE finding in Section 7;
  fewer than two layers among the findings on a layer; no candidate link; no chain with a Critical or High finding). ``skipped`` when an
  input is unusable (Section 7 unreadable, inventory missing, inventory invalid), which is also ``chains.json``'s outcome, so ``render``
  upserts the record from it.
- **The digests.** ``reference_digest`` is ``tachi_parts.reference_digest`` of the reference set, null when Section 7 can't be read, and
  ``inventory_digest`` is the SHA-256 of the inventory's bytes, null when the file can't be read. ``render`` refuses a ``chains.json``
  whose digests differ from its own reads. The inventory's digest is taken before its content is read, so a file that changes in
  between can only make ``render`` refuse it.

**render** runs once the orchestrator has written ``chains/narratives.json``: a ``{title, narrative}`` for each surfaced chain, and for those only.

- **What it refuses**, with exit 2 and nothing written: a ``chains.json`` that fails its contract (exit 1 when it is missing); one whose two digests
  aren't those of its own reads of Section 7 and the inventory; one whose chains disagree with Section 7 (a member that isn't a STRIDE finding on that
  layer, or a maximum severity or a breaking target that the members don't give); narratives for an ID that isn't a surfaced chain of it; and a component
  or a Mitigation of a surfaced chain that holds a character that D3 forbids (P0-4).
- **The narratives** are narrative text (D3): a title of at most 120 characters and a narrative of at most 2,000, the ``chain-narratives`` slots, and no
  numeral outside a slot. A chain whose text fails takes a fixed title and narrative, built from its members and never from the failed text, and
  ``render`` names it under ``narrative_fallbacks``, so that the orchestrator can rewrite it once and run ``render`` again. Every surfaced chain fails
  alike when the file is missing or fails its key set. Valid text is escaped for its place, so it adds no heading, row, fence or markup (NFR-10).
- **The file.** For ``written`` it writes ``attack-chains.md`` at schema 1.1: the frontmatter (the date of ``threats.md`` and the three counts), the
  surfaced chains in a summary and in full, a compact row for each other chain that ``chains.json`` lists, the remainder line, and the provenance
  comment. Section 7 gives each member's component and level, and the breaking target's Mitigation is the recommendation, verbatim.
- **The record.** For every outcome it upserts the outcome record in ``threats.md``. ``zero`` and ``skipped`` write no chain file, and leave an earlier
  run's one where it is, for ``check`` to move aside. It replaces exactly the lines that ``tachi_parsers.parse_chain_outcome`` names. With none, the
  record goes under ``## Attack Chain Outcome``, directly before ``## 5. Coverage Matrix``, else before ``## Affected Assets``, else at the end of the
  file, and each anchor is a line outside code fences (S1P-A22). The new text is read back through the parser before anything is written.

**check** runs in the main session (FR-K4.1b, R-24). It reads the record through ``parse_chain_outcome``. ``chains written (N)`` passes when
``attack-chains.md`` has S full chains, ``min(100, N - S)`` compact rows, the remainder line last and frontmatter counts equal to the record's; ``0
chains`` and ``skipped`` pass when the file is absent. Like FR-K5.7, it confirms consistency and not provenance: it reads neither the provenance stamp
nor ``schema_version`` (S1P-A93). A record that is absent, malformed or repeated, or a file that disagrees, is rewritten as ``skipped (<reason>)``, the
file is renamed to ``attack-chains.inconsistent.md``, and the hand-off (``tachi.check-handoff/1``, under the run-level plan's ``checks/``) holds one
``chain-outcome:rewritten`` warning. A second check on the rewritten record passes. The hand-off's place is checked before anything changes, so a
refusal changes nothing.

- **An earlier run's chain file (S1P-A91).** A run that reuses its output directory and ends in ``0 chains`` or ``skipped`` writes no chain file, so
  the earlier run's one is still there. When its SHA-256 is the run-level plan's ``preimage["attack-chains.md"]``, this run never touched it: ``check``
  renames it to ``attack-chains.inconsistent.md``, the record stands, true, and the hand-off holds one ``chain-outcome:earlier-file-moved`` warning
  (exit 5). ``fail`` puts the file back from the pre-image. Any other file takes the rewrite above: one that appeared or changed during this run, and any
  file when the plan is missing, doesn't load or holds no pre-image for the name. The plan that ``--plan`` names is read through the strict loader, best
  effort, and its own digest isn't checked: a forged plan can only keep a true record in place of the rewrite, because the file is renamed either way.
  Nothing is deleted, and ``render`` moves nothing: only ``check`` holds the plan and the hand-off.

Exit codes are ``contracts/cli.md``'s. For ``plan``: 0 done (``written`` or ``zero``); 1 an input is missing or can't be read (``--run-dir``
not a directory, or a ``skipped`` outcome whose input is missing, a link, not a regular file or unreadable); 2 a guard or validation failure
(``.tachi-build`` or ``chains`` is a link, ``chains.json`` can't be written, or a ``skipped`` outcome whose input is there but unusable: a
``threats.md`` over the size cap, not strict UTF-8 or without a usable Section 7, or an inventory that fails its loader); 4 a defect in this script (an
unexpected error, or a document that fails its own contract), which writes nothing. The orchestrator ignores them all (R-24), and a
``skipped`` outcome writes ``chains.json`` before it exits. For ``render``: 0 done, whatever the outcome (a ``skipped`` outcome's failure was
``plan``'s) and narrative fallbacks included; 1 the run directory, ``chains.json`` or ``threats.md`` is missing or can't be read; 2 a refusal above, a
``threats.md`` over the size cap or not strict UTF-8, or a write that fails; 4 a defect. For ``check``: 0 passes; 5 rewrote the record or moved an
earlier run's file; 2 anything else, a defect included, because its codes are 0, 2 and 5 and the command prints a 2 and goes on. ``render`` and
``check`` print one JSON object. Nothing here reads the clock, and the output depends on the inputs' content alone, never on where the run is or on
dictionary order. Standard library plus the shared helpers, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("attack-chains.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import collections
import os
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402

STAGE = "attack-chains"          # the banner of D4's failure message
RENDERER = "attack-chains.py"    # the stamp's name: the installed file name, as a literal (contracts/cli.md)
THREAT_MODEL = "threat-model"    # the run-level plan's stage: ``check`` takes its hand-off place and its pre-image from it
THREATS = "threats.md"
SURFACE_LIMIT = 5                # S-3(f)
COMPACT_LIMIT = 100              # S-3(g): chains.json lists the surfaced chains and at most this many others, as attack-chains.md does
HIGH = tachi_parsers.SEVERITY_ORDINAL["High"]   # a chain needs a finding at this rank or above (S-3(d))

# The reasons of D13 and ``contracts/threat-model-records.md``. ``tachi_parts.validate_chains`` holds the closed lists, and ``plan`` runs it
# on everything it writes, so a reason that drifts from them fails there.
ZERO_NO_STRIDE = "no STRIDE findings"
ZERO_ONE_LAYER = "fewer than two layers with STRIDE findings"
ZERO_NO_LINKS = "no candidate links"
ZERO_NO_SEVERE = "no chain with a Critical or High finding"
SKIP_SECTION_7 = "Section 7 unreadable"
SKIP_NO_INVENTORY = "inventory missing"
SKIP_BAD_INVENTORY = "inventory invalid"
REGENERATE = "regenerate threats.md with /tachi.threat-model, or correct Section 7"
REPLAN = "run /tachi.threat-model again, so that Phase 1 writes the inventory"

# What ``render`` writes and ``check`` reads (ADR-050 D13, D15; contracts/threat-model-records.md).
CHAIN_FILE = "attack-chains.md"
QUARANTINED = "attack-chains.inconsistent.md"   # where ``check`` moves a chain file that its record doesn't account for (a declared path, S1P-A62)
RECORD_HEADING = "## Attack Chain Outcome"
REMAINDER_LABEL = "**Consolidated chains not listed**: "
FILE_VERSION = "1.1"                            # attack-chains.md's schema_version
TITLE_LIMIT, NARRATIVE_LIMIT = 120, 2000        # ``chain-text``: a title's and a narrative's characters, before their slots resolve
NARRATIVE_STAGE = "chain-narratives"            # D3's slot table for chain titles and narratives
REWRITTEN_CODE = "chain-outcome:rewritten"      # ``check``'s hand-off warning when it rewrote the record (S1P-A52)
MOVED_CODE = "chain-outcome:earlier-file-moved"  # ... and when it moved an earlier run's chain file aside and the record stands (S1P-A91)
ARROW = " → "
DASH = "—"
NOTE = "This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness."
NO_MITIGATION = "No mitigation is recorded for this finding in Section 7."
FIXED_NARRATIVE = "No narrative is shown for this chain because the text written for it broke the narrative rules."

# The layer names of ``maestro-layers-shared.md`` and the category names of ``attack-chain-patterns-shared.md``, as today's chain files write them.
# ``test_chain_script.py`` compares both with the references, through the member tables of a file that ``render`` writes.
LAYER_NAMES = {"L1": "Foundation Model", "L2": "Data Operations", "L3": "Agent Framework", "L4": "Deployment Infrastructure",
               "L5": "Evaluation and Observability", "L6": "Security and Compliance", "L7": "Agent Ecosystem"}
CATEGORY_NAMES = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Info-Disclosure", "D": "Denial-of-Service",
                  "E": "Privilege-Escalation"}

_DETAIL = re.compile(r"### CHAIN-[0-9]{3,6}: ", re.ASCII)       # a full chain's heading, and a compact row's start, as ``check`` counts them
_ROW = re.compile(r"\| CHAIN-[0-9]{3,6} \|", re.ASCII)
_COUNT = re.compile(r"[0-9]{1,6}", re.ASCII)
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.ASCII)

# S-3(b): (category, layer) -> the (category, layer) pairs that a finding may be followed by. One entry for each source category and layer
# of ``attack-chain-patterns-shared.md``'s "Transition Lookup Table", whose 40 rows these are (S spoofing, T tampering, R repudiation,
# I information disclosure, D denial of service, E privilege escalation). ``test_chain_script.py`` compares the two, pair by pair.
TRANSITIONS: Dict[Tuple[str, int], Tuple[Tuple[str, int], ...]] = {
    ("T", 1): (("T", 2), ("S", 3), ("E", 3)),
    ("I", 1): (("I", 2), ("I", 7)),
    ("T", 2): (("T", 1), ("S", 3), ("T", 3), ("E", 3)),
    ("I", 2): (("I", 3), ("I", 7)),
    ("S", 3): (("S", 7),),
    ("T", 3): (("T", 2), ("T", 4)),
    ("I", 3): (("I", 7),),
    ("D", 3): (("D", 4),),
    ("E", 3): (("T", 2), ("E", 4), ("E", 7)),
    ("T", 4): (("T", 3), ("T", 6)),
    ("I", 4): (("I", 3), ("I", 6)),
    ("D", 4): (("D", 3), ("D", 7)),
    ("E", 4): (("E", 3),),
    ("T", 5): (("T", 6),),
    ("R", 5): (("R", 6), ("R", 3)),
    ("D", 5): (("D", 6),),
    ("S", 6): (("S", 3), ("S", 7)),
    ("T", 6): (("E", 3),),
    ("I", 6): (("I", 3),),
    ("E", 6): (("E", 3), ("E", 7)),
    ("S", 7): (("S", 3), ("S", 6)),
    ("T", 7): (("T", 3), ("T", 2)),
}

# The renderers' reading of a layer cell (``render-risk-scores.py``), so that one finding has one layer in every file.
_LAYER = re.compile(r"L[1-7](?![0-9])", re.ASCII)
_RISK_LEVELS = {level.casefold(): level for level in tp.RISK_LEVELS}

# One finding of the finding set: ``id`` as Section 7 spells it, its STRIDE ``category`` letter, its ``layer`` (1 to 7), its ``component``
# (folded), its ``risk`` level and that level's ``rank`` (Critical 4 to Note 0), and ``key``, S-2's order for its ID.
Node = collections.namedtuple("Node", "id category layer component risk rank key")


def _fold(name: str) -> str:
    """A component name as ADR-050 D13 compares it: casefolded, each run of whitespace one space (the inventory's own uniqueness rule)."""
    return " ".join(name.casefold().split())


# =============================================================================
# The inputs
# =============================================================================

class Inputs(object):
    """What ``plan`` reads from a run directory: Section 7 and the inventory, each with its digest, or the first unusable input.

    ``skip`` is ``None`` when both are usable, and otherwise ``(reason, exit code, detail, remedy)`` for the first one that isn't, in the
    contract's order (Section 7, then the inventory). Both are always read, so each digest is null only when its own input can't be read.
    """

    def __init__(self) -> None:
        self.text: Optional[str] = None       # threats.md as it was read, once it is: ``render`` upserts its record into this very text
        self.reference: Dict[str, Any] = {}   # ``parse_reference_set``'s dict, once Section 7 is read
        self.layers: Dict[str, str] = {}
        self.reference_digest: Optional[str] = None
        self.inventory: Dict[str, Any] = {}   # the validated ``tachi.phase1-inventory/1``, once it is read
        self.inventory_digest: Optional[str] = None
        self.skip: Optional[Tuple[str, int, str, str]] = None


def _threats_text(run_dir: str) -> Tuple[Optional[str], int, str]:
    """``(the text of threats.md, 0, "")``, or ``(None, an exit code, the detail)``: 1 for a file that can't be read (missing, a link, not a regular file,
    or a read that fails), and 2 for one that is there but unusable, over the size cap or not strict UTF-8. That is D4's code for the input and the one
    that the generator and the assembler give it (S1P-A86), so a file over the cap is 2 here too."""
    raw, reason = tp.read_capped(os.path.join(run_dir, THREATS), tp.MAX_AGENT_INPUT_BYTES)
    if raw is None:
        if reason == "too-large":
            return None, 2, "%s is over the size cap of %d bytes" % (THREATS, tp.MAX_AGENT_INPUT_BYTES)
        return None, 1, "%s could not be read (%s)" % (THREATS, reason)
    try:
        return raw.decode("utf-8"), 0, ""
    except UnicodeDecodeError:
        return None, 2, "%s is not strict UTF-8" % THREATS


def _read_section_7(run_dir: str, found: Inputs) -> Optional[Tuple[str, int, str, str]]:
    """The compiled ``threats.md``: its reference set, each finding's own layer and the set's digest. A file that can't be read is exit 1,
    and one that is there but unusable, over the size cap, not strict UTF-8 or with no usable Section 7, is exit 2."""
    text, code, detail = _threats_text(run_dir)
    if text is None:
        return SKIP_SECTION_7, code, detail, REGENERATE
    found.text = text
    try:
        found.reference = tachi_parsers.parse_reference_set(text, THREATS)
    except tachi_parsers.ReferenceSetError as exc:
        return SKIP_SECTION_7, 2, exc.reason, exc.remedy
    found.layers = tachi_parsers.parse_finding_layers(text)
    found.reference_digest = tp.reference_digest(found.reference)
    return None


def _read_inventory(run_dir: str, found: Inputs) -> Optional[Tuple[str, int, str, str]]:
    """``phase1/inventory.json`` through D3's loader: the planned path and its guard, the size cap, strict UTF-8 and JSON, and the key set.

    The digest is taken first, over the file's bytes, so a file that changes before it is read makes the digest older than the content, and
    ``render``, which reads the file again, refuses it. The other order could pair new bytes' chains with old bytes' digest."""
    path = os.path.join(run_dir, tp.BUILD_DIR, "phase1", "inventory.json")
    found.inventory_digest = tp.digest_or_none(path, run_dir)
    try:
        found.inventory = tp.read_document(path, run_dir, tp.INVENTORY_SCHEMA)
    except tp.PartError as exc:
        if exc.kind == "missing":
            return SKIP_NO_INVENTORY, 1, "phase1/inventory.json is missing", REPLAN
        return SKIP_BAD_INVENTORY, 2, "phase1/inventory.json is not acceptable (%s)" % exc.detail, REPLAN
    return None


def _read_inputs(run_dir: str) -> Inputs:
    found = Inputs()
    section_7, inventory = _read_section_7(run_dir, found), _read_inventory(run_dir, found)
    found.skip = section_7 or inventory
    return found


# =============================================================================
# The finding set, the links and the chains (S-3)
# =============================================================================

def _finding_set(found: Inputs) -> Tuple[int, List[Node]]:
    """``(the STRIDE findings of Section 7, the findings on a layer from L1 to L7)``, the second in S-3(c)'s order: severity, highest first,
    then S-2. A risk level that is none of the five ranks as Note, the lowest, as the extractors rank one they don't know."""
    by_component = {_fold(c["name"]): c["maestro_layer"] for c in found.inventory["components"]}
    stride, nodes = 0, []
    for row in found.reference["open"]:
        canonical = tp.canonical_finding_id(row["id"])
        category = canonical.partition("-")[0]
        if category not in tp.STRIDE_LETTERS:
            continue
        stride += 1
        component = _fold(row["component"])
        layer = _LAYER.match(found.layers.get(canonical) or by_component.get(component) or "")
        if layer is None:
            continue
        risk = _RISK_LEVELS.get(" ".join(row["risk_level"].split()).casefold(), "Note")
        nodes.append(Node(row["id"], category, int(layer.group(0)[1:]), component, risk, tachi_parsers.SEVERITY_ORDINAL[risk],
                          tp.finding_sort_key(canonical)))
    nodes.sort(key=lambda node: (-node.rank, node.key))
    return stride, nodes


def _reach(inventory: Dict[str, Any], names: Set[str]) -> Dict[str, Set[str]]:
    """For each name, every component that its data flows reach in one hop or more: the flow graph's transitive closure. A flow's ends
    aren't checked against the components (``validate_phase1_inventory``), so a name that no component has is still a place in the graph."""
    ahead: Dict[str, List[str]] = {}
    for flow in inventory["data_flows"]:
        ahead.setdefault(_fold(flow["source"]), []).append(_fold(flow["destination"]))
    reach: Dict[str, Set[str]] = {}
    for name in names:
        seen: Set[str] = set()
        stack = list(ahead.get(name, ()))
        while stack:
            step = stack.pop()
            if step not in seen:
                seen.add(step)
                stack.extend(ahead.get(step, ()))
        reach[name] = seen
    return reach


# AOD-SIMPLIFICATION: tests every pair of findings in two linked groups and keeps every link, so tens of thousands of connected findings in a few groups cost seconds and hundreds of MB (6,000 take 0.3 s) — upgrade: find each group's first connected finding lazily, or test components, not findings
def _candidates(nodes: Sequence[Node], inventory: Dict[str, Any]) -> List[List[int]]:
    """For each finding, the findings it links to (S-3(b)), as positions in ``nodes`` and so in S-3(c)'s order. Every table row joins two
    layers, so no finding links to itself."""
    reach = _reach(inventory, {node.component for node in nodes})
    groups: Dict[Tuple[str, int], List[int]] = {}
    for position, node in enumerate(nodes):
        groups.setdefault((node.category, node.layer), []).append(position)
    found: List[List[int]] = []
    for node in nodes:
        links = []
        for target in TRANSITIONS.get((node.category, node.layer), ()):
            for position in groups.get(target, ()):
                other = nodes[position].component
                if other in reach[node.component] or node.component in reach[other]:
                    links.append(position)
        found.append(sorted(links))
    return found


def _assemble(nodes: Sequence[Node], candidates: Sequence[Sequence[int]]) -> List[Tuple[int, ...]]:
    """S-3(c): each finding with an outgoing link starts one chain, and the chain goes on to the first of its last finding's candidates that is
    on a layer the chain doesn't have yet. A chain has at most one finding on each layer, so at most seven."""
    chains = []
    for start, links in enumerate(candidates):
        if not links:
            continue
        chain, layers = [start], {nodes[start].layer}
        while True:
            step = next((position for position in candidates[chain[-1]] if nodes[position].layer not in layers), None)
            if step is None:
                break
            chain.append(step)
            layers.add(nodes[step].layer)
        chains.append(tuple(chain))
    return chains


def _consolidate(nodes: Sequence[Node], chains: Sequence[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    """S-3(d) and (e): the consolidated chains in rank order. Identical finding sets keep the higher-ranked chain, the filter keeps a chain with
    a Critical or High finding, and a chain that is a contiguous run of a longer survivor is folded into it. Ranking is by max severity, then
    layer count, then the ordered IDs in S-2 order, so it is total once identical sets are gone."""
    def rank(chain: Tuple[int, ...]) -> Tuple[Any, ...]:
        return (-max(nodes[i].rank for i in chain), -len(chain), tuple(nodes[i].key for i in chain))

    best: Dict[frozenset, Tuple[Tuple[Any, ...], Tuple[int, ...]]] = {}
    for chain in chains:
        keyed = (rank(chain), chain)
        found = frozenset(chain)
        if found not in best or keyed < best[found]:
            best[found] = keyed
    survivors = [keyed for keyed in best.values() if max(nodes[i].rank for i in keyed[1]) >= HIGH]
    runs = set()   # every contiguous run of a survivor, shorter than the survivor
    for _, chain in survivors:
        for first in range(len(chain)):
            for last in range(first + 2, min(len(chain), first + len(chain) - 1) + 1):
                runs.add(chain[first:last])
    return [chain for _, chain in sorted(keyed for keyed in survivors if keyed[1] not in runs)]


def _breaking_target(nodes: Sequence[Node], chain: Sequence[int]) -> int:
    """Step 4 of the orchestrator's Phase 3.5: the finding whose remediation breaks the chain."""
    size = len(chain)
    if size == 2:
        return chain[1] if nodes[chain[1]].rank > nodes[chain[0]].rank else chain[0]
    if size == 3:
        return chain[1]
    return chain[max(range(1, size - 1), key=lambda i: (i * (size - 1 - i), nodes[chain[i]].rank, -i))]


def _chain_entry(nodes: Sequence[Node], chain: Sequence[int], rank: int, converging: Optional[int]) -> Dict[str, Any]:
    """One ``chains.json`` entry: ``converging`` is the count of a surfaced chain and ``None`` for any other."""
    last = len(chain) - 1
    return {"chain_id": "CHAIN-%03d" % rank, "surfaced": converging is not None, "converging": converging,
            "max_severity": max((nodes[i] for i in chain), key=lambda node: node.rank).risk,
            "members": [{"finding_id": nodes[i].id, "layer": "L%d" % nodes[i].layer,
                         "role": "initial_exploit" if place == 0 else "terminal_impact" if place == last else "intermediate_cascade"}
                        for place, i in enumerate(chain)],
            "breaking_target": nodes[_breaking_target(nodes, chain)].id}


def _outcome(found: Inputs) -> Dict[str, Any]:
    """The ``chains.json`` document for inputs that are usable: S-3 over the finding set, and D13's outcome and reason."""
    stride, nodes = _finding_set(found)
    document: Dict[str, Any] = {"schema": tp.CHAINS_SCHEMA, "outcome": "zero", "reason": None, "chain_count": 0, "candidate_count": 0,
                                "surfaced_count": 0, "reference_digest": found.reference_digest,
                                "inventory_digest": found.inventory_digest, "chains": []}
    if not stride:
        document["reason"] = ZERO_NO_STRIDE
        return document
    if len({node.layer for node in nodes}) < 2:
        document["reason"] = ZERO_ONE_LAYER
        return document
    assembled = _assemble(nodes, _candidates(nodes, found.inventory))
    consolidated = _consolidate(nodes, assembled)
    document["candidate_count"] = len(assembled)
    if not assembled:
        document["reason"] = ZERO_NO_LINKS
        return document
    if not consolidated:
        document["reason"] = ZERO_NO_SEVERE
        return document
    ending = collections.Counter(chain[-1] for chain in consolidated)
    surfaced: Set[int] = set()
    shown: Set[int] = set()
    for place, chain in enumerate(consolidated):
        if len(surfaced) < SURFACE_LIMIT and chain[-1] not in shown:
            surfaced.add(place)
            shown.add(chain[-1])
    listed, others = [], 0
    for place, chain in enumerate(consolidated):
        if place in surfaced:
            listed.append(_chain_entry(nodes, chain, place + 1, ending[chain[-1]] - 1))
        elif others < COMPACT_LIMIT:
            others += 1
            listed.append(_chain_entry(nodes, chain, place + 1, None))
    document.update(outcome="written", chain_count=len(consolidated), surfaced_count=len(surfaced), chains=listed)
    return document


def _document(found: Inputs) -> Dict[str, Any]:
    """What ``plan`` writes to ``chains.json``, checked against its own contract (``tachi_parts.validate_chains``) before it is written: a
    document that fails is this script's defect, which ends as D4's exit 4, never a file that ``render`` would refuse."""
    if found.skip is not None:
        document: Dict[str, Any] = {"schema": tp.CHAINS_SCHEMA, "outcome": "skipped", "reason": found.skip[0], "chain_count": None,
                                    "candidate_count": None, "surfaced_count": None, "reference_digest": found.reference_digest,
                                    "inventory_digest": found.inventory_digest, "chains": []}
    else:
        document = _outcome(found)
    try:
        tp.validate_chains(document)
    except tp.PartError as exc:
        raise tp.StageFailure(4, STAGE, "the computed chains fail their own contract (%s)" % exc.detail,
                              "report this as a bug in %s; nothing was written" % RENDERER) from None
    return document


# =============================================================================
# The modes
# =============================================================================

def _write_chains(run_dir: str, document: Dict[str, Any]) -> None:
    """Write ``chains/chains.json`` under ``.tachi-build``, through no link: each directory is checked before it is made or entered, and a
    link at the file's own name is replaced, never followed (``atomic_write``)."""
    directory = run_dir
    for name in (tp.BUILD_DIR, "chains"):
        directory = os.path.join(directory, name)
        if os.path.islink(directory) or (os.path.lexists(directory) and not os.path.isdir(directory)):
            raise tp.StageFailure(2, STAGE, "%s is a symbolic link or not a directory" % os.path.relpath(directory, run_dir),
                                  "remove it and re-run")
    try:
        os.makedirs(directory, exist_ok=True)
        tp.atomic_write(os.path.join(directory, "chains.json"), tp.dump_json(document))
    except OSError as exc:
        raise tp.StageFailure(2, STAGE, "chains/chains.json could not be written (%s)" % (exc.strerror or "error"),
                              "re-run the command") from None


def _run_plan(args: argparse.Namespace) -> int:
    run_dir = tp.directory_argument(STAGE, args.run_dir, option="--run-dir")
    found = _read_inputs(run_dir)
    document = _document(found)
    _write_chains(run_dir, document)
    shown = {key: document[key] for key in ("outcome", "reason", "chain_count", "candidate_count", "surfaced_count")}
    shown["surfaced"] = [chain for chain in document["chains"] if chain["surfaced"]]
    sys.stdout.write(tp.dump_json(shown))
    if found.skip is None:
        return 0
    reason, code, detail, remedy = found.skip
    sys.stderr.write(tp.StageFailure(code, STAGE, "%s: %s" % (reason, detail[:300]), remedy).text() + "\n")
    return code


# =============================================================================
# The outcome record in threats.md (D13, S1P-A22), shared by render and check
# =============================================================================

def _outcome_text(document: Dict[str, Any]) -> str:
    """OUTCOME of ``contracts/threat-model-records.md``'s grammar, for a ``chains.json``'s outcome, reason and counts."""
    if document["outcome"] == "written":
        return "chains written (%d); candidates %d; surfaced %d" % (document["chain_count"], document["candidate_count"], document["surfaced_count"])
    if document["outcome"] == "zero":
        return "0 chains passed filter (%s); candidates %d" % (document["reason"], document["candidate_count"])
    return "skipped (%s)" % document["reason"]


def _upsert_record(text: str, outcome: str) -> str:
    """``text`` with its outcome record set to ``outcome``, read back through the parser before it is returned (S1P-A22).

    The lines that ``parse_chain_outcome`` names are the record, whatever their form: the first becomes the new line, and any other is dropped, so one
    record is left. With none, the record goes under ``## Attack Chain Outcome``, found if it is there, else made directly before ``## 5. Coverage
    Matrix``, else before ``## Affected Assets``, else at the end of the file. Each anchor is a line outside code fences (``match_heading``'s fence rule), so
    a heading that evidence quotes is no anchor and a fenced record is no record. A file whose lines end in CRLF gets the new lines in CRLF.
    """
    eol = "\r" if "\r\n" in text else ""
    record = tachi_parsers.CHAIN_OUTCOME_LABEL + outcome + eol
    lines = text.split("\n")
    named = tachi_parsers.parse_chain_outcome(text)["lines"]
    if named:
        dropped = set(named[1:])
        lines[named[0]] = record
        lines = [line for place, line in enumerate(lines) if place not in dropped]
    else:
        heading = tachi_parsers.match_heading(r"^%s\r?$" % re.escape(RECORD_HEADING), text, outside_fences=True)
        if heading is not None:
            lines[heading + 1:heading + 1] = [eol, record]
        else:
            anchors = (tachi_parsers.match_heading(pattern, text, outside_fences=True)
                       for pattern in (r"^## 5\. Coverage Matrix\r?$", r"^## Affected Assets\r?$"))
            anchor = next((place for place in anchors if place is not None), None)
            if anchor is not None:
                lines[anchor:anchor] = [RECORD_HEADING + eol, eol, record, eol, "---" + eol, eol]
            else:
                body = lines[:-1] if lines[-1] == "" else lines   # the last newline of a file ends its last line and starts none
                gap = ([] if not body[-1].strip() else [eol]) + ["---" + eol, eol] if body else []   # one blank line, a rule, one blank line
                lines = body + gap + [RECORD_HEADING + eol, eol, record, ""]
    result = "\n".join(lines)
    read = tachi_parsers.parse_chain_outcome(result)
    if read["form"] == "absent":
        raise tp.StageFailure(2, STAGE, "the outcome record would not read back from threats.md: a code fence that nothing closes covers its place",
                              "close the fence in threats.md, or regenerate it with /tachi.threat-model")
    if len(read["lines"]) != 1 or read["text"] != outcome:
        raise RuntimeError("the outcome record does not read back as it was written")
    return result


def _frontmatter(lines: Sequence[str]) -> Dict[str, str]:
    """The top-level ``key: value`` pairs between a file's opening ``---`` and the next one, with their quotes taken off. It is a linear scan on purpose:
    ``threats.md`` is a file that the scanned repository can influence, and ``tachi_parsers.parse_frontmatter``'s pattern is quadratic on a long line."""
    front: Dict[str, str] = {}
    if lines and lines[0].rstrip("\r") == "---":
        for line in lines[1:]:
            line = line.rstrip("\r")
            if line == "---":
                break
            key, colon, value = line.partition(":")
            if colon and not key[:1].isspace():
                front[key.strip()] = value.strip().strip('"')
    return front


def _write_text(path: str, text: str) -> None:
    """Write one output of this script through no link (``atomic_write`` replaces a link and never follows it), or exit 2."""
    try:
        tp.atomic_write(path, text)
    except OSError as exc:
        raise tp.StageFailure(2, STAGE, "%s could not be written (%s)" % (os.path.basename(path), exc.strerror or "error"),
                              "re-run the command") from None


# =============================================================================
# render
# =============================================================================

def _chains_match_section_7(document: Dict[str, Any], nodes: Sequence[Node]) -> None:
    """``chains.json`` against Section 7 and the inventory, as ``validate_chains`` leaves it to ``render``: each member is a STRIDE finding on the layer it
    names, and each chain's maximum severity and breaking target are the ones that its members give. A forged or damaged file stops here, with exit 2."""
    at = {node.id: place for place, node in enumerate(nodes)}
    for chain in document["chains"]:
        places = [at.get(member["finding_id"]) for member in chain["members"]]
        if (None in places or any("L%d" % nodes[place].layer != member["layer"] for place, member in zip(places, chain["members"]))
                or max(nodes[place].rank for place in places) != tachi_parsers.SEVERITY_ORDINAL[chain["max_severity"]]
                or nodes[_breaking_target(nodes, places)].id != chain["breaking_target"]):
            raise tp.StageFailure(2, STAGE, "chains/chains.json disagrees with Section 7 at %s" % chain["chain_id"], "run attack-chains.py plan again")


def _refuse_forbidden(document: Dict[str, Any], rows: Dict[str, Dict[str, Any]]) -> None:
    """P0-4: the component of each member of a surfaced chain, and its target's Mitigation, are the text that reaches the file from ``threats.md``.
    A character that D3 forbids in any of them is exit 2, and the reason never carries the character."""
    for chain in document["chains"]:
        if chain["surfaced"]:
            for member in chain["members"]:
                row = rows[member["finding_id"]]
                value = {"component": row["component"]}
                if member["finding_id"] == chain["breaking_target"]:
                    value["mitigation"] = row["mitigation"]
                problem = tp.forbidden_problem(THREATS, member["finding_id"], value)
                if problem is not None:
                    raise tp.StageFailure(2, STAGE, problem, REGENERATE)


def _fixed_text(chain: Dict[str, Any]) -> Tuple[str, str]:
    """The title and the narrative of a chain whose own text failed (D13): built from its members alone, so it can't carry the failed text."""
    members = chain["members"]
    steps = ", ".join("%s on %s" % (member["finding_id"], member["layer"]) for member in members)
    return ("Attack chain from %s to %s" % (members[0]["finding_id"], members[-1]["finding_id"]),
            "%s Its findings, in order from the initial exploit to the terminal impact, are %s." % (FIXED_NARRATIVE, steps))


def _lookup(chain: Dict[str, Any], rows: Dict[str, Dict[str, Any]]) -> Callable[[str, str], Optional[str]]:
    """What a slot of this chain's title or narrative resolves to (D3's table for chain narratives), or ``None`` when it names nothing that the chain has:
    a count of its members, layers or converging chains; a finding, a component or a layer of one of its members."""
    members = {tp.canonical_finding_id(member["finding_id"]): member for member in chain["members"]}
    layers = {member["layer"] for member in chain["members"]}
    counts = {"members": len(chain["members"]), "layers": len(layers), "converging": chain["converging"]}

    def lookup(kind: str, argument: str) -> Optional[str]:
        if kind == "count":
            return str(counts[argument])
        if kind == "finding":
            return argument if argument in members else None
        if kind == "ref":
            return argument if argument in layers else None
        member = members.get(tp.canonical_finding_id(argument.partition(":")[2]))   # name: ``component:<finding ID>``
        return None if member is None else rows[member["finding_id"]]["component"]

    return lookup


def _resolve(entry: Dict[str, str], lookup: Callable[[str, str], Optional[str]]) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
    """One chain's ``{title, narrative}``, resolved and escaped (a title for a cell, a narrative for prose): ``((title, narrative), None)``, or ``(None, the
    first problem)``. The problems are words and never the text: ``title-empty``, ``forbidden-character``, ``narrative-too-long``, one of ``tachi_parts``'
    grammar problems (``slot-syntax``, ``slot-kind``, ``slot-argument``, ``numeral``), or ``slot-unresolved``."""
    for name, limit in (("title", TITLE_LIMIT), ("narrative", NARRATIVE_LIMIT)):
        text = entry[name]
        if not text.strip():
            return None, "%s-empty" % name
        if tp.forbidden_character(text) is not None:
            return None, "forbidden-character"
        if len(text) > limit:
            return None, "%s-too-long" % name
        problem = tp.narrative_problem(text, NARRATIVE_STAGE)
        if problem is not None:
            return None, problem
    title = tp.resolve_narrative(entry["title"], NARRATIVE_STAGE, lookup, "cell")
    narrative = tp.resolve_narrative(entry["narrative"], NARRATIVE_STAGE, lookup, "prose")
    if title is None or narrative is None:
        return None, "slot-unresolved"
    return (title.strip(), narrative.strip()), None


def _narratives(run_dir: str, document: Dict[str, Any],
                rows: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Tuple[str, str]], Dict[str, Any], List[Dict[str, str]]]:
    """``(each surfaced chain's title and narrative, the agent text that was used, the chains that took the fixed text)`` (D13).

    A chain whose entry is missing or fails validation takes its fixed text, and so does every surfaced chain when ``narratives.json`` is missing or fails
    its key set. ``render`` is stateless: the orchestrator's one rewrite is its own, after it reads which chains fell back. An ID that isn't a surfaced chain
    of ``chains.json`` is refused, because the file maps the surfaced chains and only those."""
    surfaced = [chain for chain in document["chains"] if chain["surfaced"]]
    entries: Dict[str, Any] = {}
    unusable = None
    try:
        entries = tp.read_document(os.path.join(run_dir, tp.BUILD_DIR, "chains", "narratives.json"), run_dir, tp.CHAIN_NARRATIVES_SCHEMA)["narratives"]
    except tp.PartError as exc:
        unusable = "narratives-missing" if exc.kind == "missing" else "narratives-invalid"
    wanted = {chain["chain_id"] for chain in surfaced}
    for key in entries:
        if key not in wanted:
            raise tp.StageFailure(2, STAGE, "chains/narratives.json names %s, which is not a surfaced chain of chains.json"
                                  % (key if tp.id_matches("chain", key) else "a key that is no chain ID"),
                                  "write narratives for the surfaced chains that plan printed, and for no other chain")
    texts: Dict[str, Tuple[str, str]] = {}
    used: Dict[str, Any] = {}
    fallbacks: List[Dict[str, str]] = []
    for chain in surfaced:
        chain_id, entry = chain["chain_id"], entries.get(chain["chain_id"])
        resolved, problem = (None, unusable or "missing") if entry is None else _resolve(entry, _lookup(chain, rows))
        if resolved is None:
            fallbacks.append({"chain_id": chain_id, "problem": str(problem)})
            resolved = _fixed_text(chain)
        else:
            used[chain_id] = entry
        texts[chain_id] = resolved
    return texts, used, fallbacks


def _side(group: Sequence[Dict[str, Any]], word: str) -> str:
    """``1 upstream finding (S-1 at L7)``: how many findings a breaking target cuts off, the way today's chain files say it."""
    listed = " (%s)" % ", ".join("%s at %s" % (member["finding_id"], member["layer"]) for member in group) if group else ""
    return "%d %s %s%s" % (len(group), word, "finding" if len(group) == 1 else "findings", listed)


def _detail(chain: Dict[str, Any], title: str, narrative: str, rows: Dict[str, Dict[str, Any]], nodes: Dict[str, Node]) -> List[str]:
    """One surfaced chain's section of ``attack-chains.md``: today's keys, and its converging count."""
    members, target = chain["members"], chain["breaking_target"]
    place = [member["finding_id"] for member in members].index(target)
    mitigation = rows[target]["mitigation"]
    lines = ["### %s: %s" % (chain["chain_id"], title), "", "**Layers**: %s" % _layers(chain), "**Max Severity**: %s" % chain["max_severity"],
             "**Surfaced**: Yes", "**Converging chains**: %d" % chain["converging"], "", "#### Member Findings", "",
             "| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |", "|---|---|---|---|---|---|"]
    for member in members:
        found = member["finding_id"]
        lines.append("| %s | %s | %s | %s | %s | %s |" % (found, _layer_cell(member["layer"]), member["role"], tp.escape_cell(rows[found]["component"]),
                                                         CATEGORY_NAMES[found.partition("-")[0]], nodes[found].risk))
    lines += ["", "#### Attack Progression", "", narrative, "", "#### Chain-Breaking Controls", "",
              "**Target**: %s (%s)" % (target, _layer_cell(members[place]["layer"])),
              "**Rationale**: Removing this finding at %s disconnects %s from %s in the chain"
              % (members[place]["layer"], _side(members[:place], "upstream"), _side(members[place + 1:], "downstream")),
              "**Recommendation**: %s" % (tp.escape_cell(mitigation) if mitigation.strip() else NO_MITIGATION), "**Note**: %s" % NOTE, ""]
    return lines


def _layers(chain: Dict[str, Any]) -> str:
    return ARROW.join(member["layer"] for member in chain["members"])


def _layer_cell(layer: str) -> str:
    return "%s %s %s" % (layer, DASH, LAYER_NAMES[layer])


def _chain_file(document: Dict[str, Any], found: Inputs, rows: Dict[str, Dict[str, Any]], nodes: Dict[str, Node],
                texts: Dict[str, Tuple[str, str]], digest: str) -> str:
    """``attack-chains.md`` at 1.1 (S-3(g)): the surfaced chains in a summary and in full, a compact row for each other chain that ``chains.json`` lists, the
    remainder line last, and the provenance comment. The date is ``threats.md``'s, or ``Unknown`` when its frontmatter has none that reads as a date."""
    surfaced = [chain for chain in document["chains"] if chain["surfaced"]]
    others = [chain for chain in document["chains"] if not chain["surfaced"]]
    date = _frontmatter((found.text or "").split("\n")).get("date", "")
    lines = ["---", 'schema_version: "%s"' % FILE_VERSION, 'date: "%s"' % (date if _DATE.fullmatch(date) else "Unknown"),
             "chain_count: %d" % document["chain_count"], "surfaced_count: %d" % document["surfaced_count"],
             "candidate_count: %d" % document["candidate_count"], "---", "", "# Cross-Layer Attack Chains", "", "## 1. Chain Summary", "",
             "| Chain ID | Title | Layers | Max Severity | Finding Count | Chain-Breaking Target | Converging Chains |", "|---|---|---|---|---|---|---|"]
    for chain in surfaced:
        lines.append("| %s | %s | %s | %s | %d | %s | %d |" % (chain["chain_id"], texts[chain["chain_id"]][0], _layers(chain), chain["max_severity"],
                                                              len(chain["members"]), chain["breaking_target"], chain["converging"]))
    lines += ["", "---", "", "## 2. Chain Details", ""]
    for chain in surfaced:
        lines += _detail(chain, texts[chain["chain_id"]][0], texts[chain["chain_id"]][1], rows, nodes) + ["---", ""]
    lines += ["## 3. Other Consolidated Chains", "", "| Chain ID | Layers | Findings | Max Severity | Chain-Breaking Target |", "|---|---|---|---|---|"]
    for chain in others:
        lines.append("| %s | %s | %s | %s | %s |" % (chain["chain_id"], _layers(chain), ARROW.join(member["finding_id"] for member in chain["members"]),
                                                    chain["max_severity"], chain["breaking_target"]))
    lines += ["", REMAINDER_LABEL + str(document["chain_count"] - document["surfaced_count"] - len(others)), "", tp.stamp_comment(RENDERER, digest)]
    return "\n".join(lines) + "\n"


def _refuse_changed_inputs(document: Dict[str, Any], found: Inputs) -> None:
    """The digests of ``chains.json`` are those of ``render``'s own reads of Section 7 and the inventory, and the document's outcome is what the inputs
    give: a ``skipped`` one has the first unusable input's reason. Anything else is a stale or damaged ``chains.json``: exit 2, nothing written."""
    if (document["reference_digest"], document["inventory_digest"]) != (found.reference_digest, found.inventory_digest):
        raise tp.StageFailure(2, STAGE, "chains/chains.json is stale: Section 7 or the inventory changed since plan", "run attack-chains.py plan again")
    skipped = document["outcome"] == "skipped"
    if skipped != (found.skip is not None) or (found.skip is not None and found.skip[0] != document["reason"]):
        raise tp.StageFailure(2, STAGE, "chains/chains.json does not match what its inputs give", "run attack-chains.py plan again")


def _run_render(args: argparse.Namespace) -> int:
    run_dir = tp.directory_argument(STAGE, args.run_dir, option="--run-dir")
    document = tp.entry_document(STAGE, os.path.join(run_dir, tp.BUILD_DIR, "chains", "chains.json"), run_dir, tp.CHAINS_SCHEMA, "chains/chains.json")
    found = _read_inputs(run_dir)
    _refuse_changed_inputs(document, found)
    if found.text is None:   # nowhere to put the record: threats.md can't be read, so Section 7 is the unusable input, and ``skip`` says how (1 or 2)
        reason, code, detail, remedy = found.skip or (SKIP_SECTION_7, 1, "%s could not be read" % THREATS, REGENERATE)
        raise tp.StageFailure(code, STAGE, "%s: %s" % (reason, detail[:300]), remedy)
    outcome = _outcome_text(document)
    chain_file, fallbacks = None, []
    if document["outcome"] == "written":
        nodes = _finding_set(found)[1]
        _chains_match_section_7(document, nodes)
        rows = {row["id"]: row for row in found.reference["open"]}
        _refuse_forbidden(document, rows)
        texts, used, fallbacks = _narratives(run_dir, document, rows)
        digest = tp.input_digest({"chains": document, "narratives": used})
        chain_file = _chain_file(document, found, rows, {node.id: node for node in nodes}, texts, digest)
    threats = _upsert_record(found.text, outcome)
    if chain_file is not None:
        _write_text(os.path.join(run_dir, CHAIN_FILE), chain_file)
    _write_text(os.path.join(run_dir, THREATS), threats)
    shown = {key: document[key] for key in ("outcome", "reason", "chain_count", "candidate_count", "surfaced_count")}
    shown.update(record=outcome, chain_file=CHAIN_FILE if chain_file is not None else None, narrative_fallbacks=fallbacks)
    sys.stdout.write(tp.dump_json(shown))
    for fallback in fallbacks:
        sys.stderr.write("WARNING narrative-fallback: the text of %s broke the narrative rules (%s), so its fixed text is used; "
                         "rewrite it once and run render again\n" % (fallback["chain_id"], fallback["problem"]))
    return 0


# =============================================================================
# check
# =============================================================================

# AOD-SIMPLIFICATION: counts a chain file's headings and rows by their text, blind to code fences like ``parse_attack_chains`` — upgrade: skip fenced lines if a chain file ever holds a fence
def _read_chain_file(text: str) -> Tuple[Dict[str, str], int, int, Optional[int]]:
    """``(the frontmatter's keys, the full chains, the compact rows, the remainder)`` of an ``attack-chains.md``, as the check counts them: a full chain is a
    ``### CHAIN-`` heading under ``## 2. Chain Details``, a compact row a ``| CHAIN-`` line under ``## 3. Other Consolidated Chains``, and the remainder
    the number on the last line that isn't blank or the provenance comment, or ``None`` when that line isn't the remainder line."""
    lines = [line.rstrip("\r") for line in text.split("\n")]
    front = _frontmatter(lines)
    section, full, rows = "", 0, 0
    for line in lines:
        if line.startswith("## "):
            section = line.rstrip()
        elif section == "## 2. Chain Details" and _DETAIL.match(line):
            full += 1
        elif section == "## 3. Other Consolidated Chains" and _ROW.match(line):
            rows += 1
    content = [line for line in lines if line.strip()]
    if content and tp.read_stamp(content[-1]) is not None:
        content.pop()
    last = content[-1].rstrip() if content else ""
    remainder = int(last[len(REMAINDER_LABEL):]) if last.startswith(REMAINDER_LABEL) and _COUNT.fullmatch(last[len(REMAINDER_LABEL):]) else None
    return front, full, rows, remainder


def _file_problem(path: str, outcome: Dict[str, Any]) -> Optional[str]:
    """Why ``attack-chains.md`` doesn't account for a ``chains written (N)`` record, in the check's words, or ``None`` when it does (FR-K4.1b): S full
    chains, ``min(100, N - S)`` compact rows, a last line that states the rest, and frontmatter counts that are the record's."""
    raw, reason = tp.read_capped(path, tp.MAX_AGENT_INPUT_BYTES)
    if raw is None:
        return "%s %s" % (CHAIN_FILE, "missing" if reason == "missing" else "unreadable")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "%s unreadable" % CHAIN_FILE
    front, full, rows, remainder = _read_chain_file(text)
    chains, surfaced, candidates = outcome["chain_count"], outcome["surfaced_count"], outcome["candidate_count"]
    listed = min(COMPACT_LIMIT, chains - surfaced)
    if full != surfaced:
        return "full chains %d expected %d" % (full, surfaced)
    if rows != listed:
        return "compact rows %d expected %d" % (rows, listed)
    if remainder != chains - surfaced - listed:
        return "remainder %s expected %d" % ("missing" if remainder is None else remainder, chains - surfaced - listed)
    if [front.get(key) for key in ("chain_count", "surfaced_count", "candidate_count")] != [str(chains), str(surfaced), str(candidates)]:
        return "frontmatter counts differ"
    return None


def _disagreement(path: str, outcome: Dict[str, Any]) -> Optional[str]:
    """What the record and the artifacts disagree about, as the reason of a rewritten ``skipped (<reason>)``, or ``None`` when they agree (D13)."""
    form = outcome["form"]
    if form in ("absent", "malformed", "multiple"):
        return {"absent": "no outcome recorded", "malformed": "outcome record malformed", "multiple": "multiple outcome records"}[form]
    if form == "written":
        return _file_problem(path, outcome)
    return "%s unexpected" % CHAIN_FILE if os.path.lexists(path) else None   # 0 chains and skipped need the file to be absent


def _handoff_directory(run_dir: str, plan_id: str) -> str:
    """``threat-model/<plan_id>/checks`` under ``.tachi-build``: the run-level plan's directory must be there, through no link, and ``checks`` must be a
    directory or absent. Checked before the check changes anything, so a refusal (exit 2) leaves the run as it was."""
    directory = run_dir
    for name in (tp.BUILD_DIR, THREAT_MODEL, plan_id):
        directory = os.path.join(directory, name)
        if os.path.islink(directory) or not os.path.isdir(directory):
            raise tp.StageFailure(2, STAGE, "the run-level plan %s has no directory under %s/%s" % (plan_id, tp.BUILD_DIR, THREAT_MODEL),
                                  "pass the run-level plan's ID, which Step 1.5 printed")
    checks = os.path.join(directory, "checks")
    if os.path.islink(checks) or (os.path.lexists(checks) and not os.path.isdir(checks)):
        raise tp.StageFailure(2, STAGE, "%s/%s/%s/checks is a symbolic link or not a directory" % (tp.BUILD_DIR, THREAT_MODEL, plan_id), "remove it and re-run")
    return checks


def _earlier_file(run_dir: str, plan_id: str, path: str) -> bool:
    """Whether ``path`` is the chain file that an earlier run left in this output directory (ADR-050 D13, S1P-A91): its SHA-256 is the run-level plan's
    ``preimage["attack-chains.md"]``, so nothing in this run wrote it.

    The plan is read through D3's strict loader, best effort and without its own digest. A plan that is missing or doesn't load, a null pre-image, a file that
    can't be read (a link, not a regular file, over the cap) and a file with other bytes all give ``False``, and the check then takes D13's rewrite. A forged plan
    could only keep a true record in place of that rewrite, because the file is renamed either way."""
    try:
        plan = tp.read_document(tp.plan_path(run_dir, THREAT_MODEL, plan_id), run_dir, tp.PLAN_SCHEMA)
    except tp.PartError:
        return False
    raw, _ = tp.read_capped(path, tp.MAX_AGENT_INPUT_BYTES)
    return raw is not None and tp.sha256_hex(raw) == plan["preimage"].get(CHAIN_FILE)   # a null pre-image is no digest, so it never matches


# AOD-SIMPLIFICATION: a file already at the quarantine name is replaced, as D13's rewrite always did, so a fixed output directory that alternates between outcomes keeps only the last file moved — upgrade: refuse when the name is taken, or keep each file under a name of its own, if a ruling says that nothing in a reused directory is ever replaced
def _quarantine(run_dir: str, record: str) -> None:
    """Rename ``attack-chains.md`` to the declared name that the check keeps for it, or exit 2 and say what state the record is left in. A link is renamed,
    never followed, and nothing is deleted: the file keeps its bytes under the new name."""
    try:
        os.replace(os.path.join(run_dir, CHAIN_FILE), os.path.join(run_dir, QUARANTINED))
    except OSError as exc:
        raise tp.StageFailure(2, STAGE, "%s, but %s could not be renamed (%s)" % (record, CHAIN_FILE, exc.strerror or "error"),
                              "rename it to %s, or run the check again" % QUARANTINED) from None


def _check(run_dir: str, plan_id: str) -> int:
    handoff = _handoff_directory(run_dir, plan_id)
    text, _, detail = _threats_text(run_dir)
    if text is None:
        raise tp.StageFailure(2, STAGE, detail, REGENERATE)
    outcome = tachi_parsers.parse_chain_outcome(text)
    chain_path = os.path.join(run_dir, CHAIN_FILE)
    problem = _disagreement(chain_path, outcome)
    record, warnings = outcome["text"], []
    if problem is not None and outcome["form"] in ("zero", "skipped") and _earlier_file(run_dir, plan_id, chain_path):
        _quarantine(run_dir, "the record stands")   # a record with no chain file is true: this run wrote none, and the earlier run's is kept, aside
        warnings.append(tp.record_warning(MOVED_CODE, "an earlier run's %s was renamed to %s; the outcome record '%s' stands" % (CHAIN_FILE, QUARANTINED, record)))
    elif problem is not None:
        record = "skipped (%s)" % problem
        rewritten = _upsert_record(text, record)
        moved = os.path.lexists(chain_path)
        _write_text(os.path.join(run_dir, THREATS), rewritten)
        if moved:
            _quarantine(run_dir, "the record is now '%s'" % record)
        warnings.append(tp.record_warning(REWRITTEN_CODE, "the outcome record was rewritten as '%s'; %s" % (
            record, "%s was renamed to %s" % (CHAIN_FILE, QUARANTINED) if moved else "there was no %s to rename" % CHAIN_FILE)))
    document = {"schema": tp.HANDOFF_SCHEMA, "check": "attack-chains", "plan_id": plan_id, "status": "warn" if warnings else "pass", "counts": None,
                "batches": None, "warnings": warnings, "error": None}
    tp.validate_check_handoff(document)
    try:
        os.makedirs(handoff, exist_ok=True)
    except OSError as exc:
        raise tp.StageFailure(2, STAGE, "checks/ could not be made (%s)" % (exc.strerror or "error"), "re-run the command") from None
    _write_text(os.path.join(handoff, "attack-chains.json"), tp.dump_json(document))
    sys.stdout.write(tp.dump_json({"status": document["status"], "outcome": record, "warnings": warnings}))
    for warning in warnings:
        sys.stderr.write("WARNING %s: %s\n" % (warning["code"], warning["detail"]))
    return 5 if warnings else 0


def _run_check(args: argparse.Namespace) -> int:
    run_dir = tp.directory_argument(STAGE, args.run_dir, option="--run-dir", code=2)   # cli.md gives check no exit 1
    tp.plan_id_argument(STAGE, args.plan)
    try:
        return _check(run_dir, args.plan)
    except tp.StageFailure:
        raise
    except Exception as exc:   # check's codes are 0, 2 and 5 (D4's exception), so a defect is a 2 that says so, never a 4
        failure = tp.entry_defect(STAGE, RENDERER, exc, None)
        raise tp.StageFailure(2, STAGE, failure.reason, failure.remedy) from None


def _build_parser() -> argparse.ArgumentParser:
    parser = tp.build_parser(RENDERER, "Form Phase 3.5's attack chains, render attack-chains.md and check it (F-374, ADR-050 D13).",
                             out=False, plan=False)
    modes = parser.add_subparsers(dest="mode", metavar="{plan,render,check}")
    modes.required = True
    for mode, summary in (("plan", "form the chains and write chains/chains.json; print the surfaced chains"),
                          ("render", "write attack-chains.md and the outcome record from chains.json and the narratives"),
                          ("check", "check the outcome record against attack-chains.md, and rewrite one that disagrees")):
        sub = modes.add_parser(mode, help=summary, description=summary[0].upper() + summary[1:] + ".")
        sub.add_argument("--run-dir", required=True, help="the run's output directory; everything is read from and written under it")
        if mode == "check":
            sub.add_argument("--plan", required=True, help="the run-level plan ID, for the check's hand-off file")
    return parser


def _run(args: argparse.Namespace) -> int:
    return {"plan": _run_plan, "render": _run_render, "check": _run_check}[args.mode](args)


def main(argv: Optional[List[str]] = None) -> int:
    return tp.run_entry(STAGE, RENDERER, _build_parser().parse_args(argv), _run, option="--run-dir")


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_chain_script.py's last test)
    sys.exit(main())
