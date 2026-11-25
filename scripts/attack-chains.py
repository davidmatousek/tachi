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

Exit codes are ``contracts/cli.md``'s. For ``plan``: 0 done (``written`` or ``zero``); 1 an input is missing or unreadable (``--run-dir``
not a directory, or a ``skipped`` outcome whose input can't be read); 2 a guard or validation failure (``.tachi-build`` or ``chains`` is a
link, ``chains.json`` can't be written, or a ``skipped`` outcome whose input is there but unusable); 4 a defect in this script (an
unexpected error, or a document that fails its own contract), which writes nothing. The orchestrator ignores them all (R-24), and a
``skipped`` outcome writes ``chains.json`` before it exits. Nothing here reads the clock, and the output depends on the inputs' content
alone, never on where the run is or on dictionary order. Standard library plus the shared helpers, and Python 3.9 syntax.
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
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402

STAGE = "attack-chains"          # the banner of D4's failure message
RENDERER = "attack-chains.py"    # the stamp's name: the installed file name, as a literal (contracts/cli.md)
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
        self.reference: Dict[str, Any] = {}   # ``parse_reference_set``'s dict, once Section 7 is read
        self.layers: Dict[str, str] = {}
        self.reference_digest: Optional[str] = None
        self.inventory: Dict[str, Any] = {}   # the validated ``tachi.phase1-inventory/1``, once it is read
        self.inventory_digest: Optional[str] = None
        self.skip: Optional[Tuple[str, int, str, str]] = None


def _read_section_7(run_dir: str, found: Inputs) -> Optional[Tuple[str, int, str, str]]:
    """The compiled ``threats.md``: its reference set, each finding's own layer and the set's digest. A file that can't be read is exit 1,
    and one that is there but isn't strict UTF-8 or has no usable Section 7 is exit 2."""
    raw, reason = tp.read_capped(os.path.join(run_dir, THREATS), tp.MAX_AGENT_INPUT_BYTES)
    if raw is None:
        return SKIP_SECTION_7, 1, "%s could not be read (%s)" % (THREATS, reason), REGENERATE
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return SKIP_SECTION_7, 2, "%s is not strict UTF-8" % THREATS, REGENERATE
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


def _run_render(args: argparse.Namespace) -> int:
    tp.directory_argument(STAGE, args.run_dir, option="--run-dir")
    raise tp.StageFailure(4, STAGE, "render is not built yet (F-374 T117)", "this build of %s has plan only" % RENDERER)


def _run_check(args: argparse.Namespace) -> int:
    tp.directory_argument(STAGE, args.run_dir, option="--run-dir", code=2)   # cli.md gives check no exit 1
    tp.plan_id_argument(STAGE, args.plan)
    raise tp.StageFailure(4, STAGE, "check is not built yet (F-374 T117)", "this build of %s has plan only" % RENDERER)


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
