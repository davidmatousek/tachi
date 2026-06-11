#!/usr/bin/env /usr/bin/python3
"""Extract the T029 CWE-blocked restore set (Feature 185, W0-b — T003/T005).

Contract: specs/185-cwe-catalog-expansion/contracts/restored-edges.schema.md

Removed-set = edges present in `git show e58f247:schemas/taxonomy/crosswalk.yaml`
(source blob, pre-T029, 551 edges) but absent from
`git show 991e1ee:schemas/taxonomy/crosswalk.yaml` (control blob, post-T029,
438 edges), compared by full edge content (set semantics — edges whose exact
content survives in the control blob are dedupe collapses, NOT removals).

Filter: target.taxonomy == "cwe" AND target.id NOT in the frozen-53 (the 53
IDs in live schemas/taxonomy/cwe.yaml).

Output: specs/185-cwe-catalog-expansion/restored-edges.yaml — header provenance
comment + 67 edge entries byte-copied from the source blob (edge_type /
confidence / citation UNMODIFIED, including the single `confidence: low` edge
T1070.006 -> CWE-1269) + per-edge `_blocked_on` working annotation (= the
missing target CWE ID; stripped before W1-2 insertion).

Counts are verified by YAML parse only (never grep — a commented header line
makes `grep -c "edge_type:"` over-count +1).
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

SOURCE_SHA = "e58f247"   # pre-T029 blob: 551 edges
CONTROL_SHA = "991e1ee"  # post-T029 blob: 438 edges
CROSSWALK_PATH = "schemas/taxonomy/crosswalk.yaml"
EXTRACTION_DATE = "2026-06-11"
SCRIPT_REPO_PATH = "specs/185-cwe-catalog-expansion/scripts/extract_restore_set.py"
ARTIFACT_REPO_PATH = "specs/185-cwe-catalog-expansion/restored-edges.yaml"

# Contract guarantees (restored-edges.schema.md section 1)
EXPECTED_SOURCE_EDGES = 551
EXPECTED_CONTROL_EDGES = 438
EXPECTED_TOTAL = 67
EXPECTED_OWASP = 65
EXPECTED_MITRE_ATTACK = 2
EXPECTED_DISTINCT_BLOCKED = 40
EXPECTED_CONFIDENCE = {"high": 34, "medium": 32, "low": 1}
EXPECTED_FROZEN = 53
EXPECTED_LOW_EDGE = ("T1070.006", "CWE-1269")
EXPECTED_MITRE_PAIR = {("T1070.006", "CWE-1269"), ("T1562", "CWE-693")}

REPO_ROOT = Path(__file__).resolve().parents[3]


def git_show(sha: str) -> str:
    """Return the crosswalk.yaml content stored in the given commit."""
    result = subprocess.run(
        ["git", "show", f"{sha}:{CROSSWALK_PATH}"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    return result.stdout


def content_key(edge: dict) -> str:
    """Full-content identity key (set semantics for the removed-set)."""
    return json.dumps(edge, sort_keys=True)


def split_raw_blocks(blob_text: str, parsed_edges: list) -> list:
    """Split the raw blob into per-edge text blocks, byte-aligned with the parse.

    Each top-level list item in crosswalk.yaml starts with '- ' at column 0.
    Block i spans from its '- ' line up to (not including) the next '- ' line;
    trailing blank lines and full-line comments (slice headers belonging to the
    NEXT section) are trimmed. Field lines are returned byte-identical.
    """
    lines = blob_text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith("- ")]
    if len(starts) != len(parsed_edges):
        sys.exit(
            f"FATAL: raw-block count {len(starts)} != parsed edge count "
            f"{len(parsed_edges)} — blob structure assumption violated"
        )
    blocks = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        block = lines[start:end]
        while block and (block[-1].strip() == "" or block[-1].lstrip().startswith("#")):
            block.pop()
        # Fidelity check: the raw block must re-parse to exactly the parsed edge.
        reparsed = yaml.safe_load("\n".join(block))
        if reparsed != [parsed_edges[n]]:
            sys.exit(f"FATAL: raw block {n} does not re-parse to its parsed edge")
        blocks.append("\n".join(block))
    return blocks


def main() -> None:
    source_text = git_show(SOURCE_SHA)
    control_text = git_show(CONTROL_SHA)
    source_edges = yaml.safe_load(source_text)
    control_edges = yaml.safe_load(control_text)

    if len(source_edges) != EXPECTED_SOURCE_EDGES:
        sys.exit(f"FATAL: source blob has {len(source_edges)} edges, expected {EXPECTED_SOURCE_EDGES}")
    if len(control_edges) != EXPECTED_CONTROL_EDGES:
        sys.exit(f"FATAL: control blob has {len(control_edges)} edges, expected {EXPECTED_CONTROL_EDGES}")

    # Frozen-53: the CWE IDs currently in the live catalog.
    cwe_path = REPO_ROOT / "schemas" / "taxonomy" / "cwe.yaml"
    with open(cwe_path, encoding="utf-8") as f:
        cwe_records = yaml.safe_load(f)
    frozen_ids = {record["id"] for record in cwe_records}
    if len(cwe_records) != EXPECTED_FROZEN or len(frozen_ids) != EXPECTED_FROZEN:
        sys.exit(
            f"FATAL: live cwe.yaml has {len(cwe_records)} records "
            f"({len(frozen_ids)} unique ids), expected exactly {EXPECTED_FROZEN}"
        )

    raw_blocks = split_raw_blocks(source_text, source_edges)

    # Removed-set (set semantics) then the CWE-blocked filter.
    control_keys = {content_key(e) for e in control_edges}
    selected = [
        (edge, raw_blocks[i])
        for i, edge in enumerate(source_edges)
        if content_key(edge) not in control_keys
        and edge["target"]["taxonomy"] == "cwe"
        and edge["target"]["id"] not in frozen_ids
    ]

    # ── Contract verification (hard gate — exit non-zero on any mismatch) ──
    edges = [e for e, _ in selected]
    failures = []
    if len(edges) != EXPECTED_TOTAL:
        failures.append(f"total {len(edges)} != {EXPECTED_TOTAL}")
    source_tax = Counter(e["source"]["taxonomy"] for e in edges)
    if source_tax.get("owasp", 0) != EXPECTED_OWASP or source_tax.get("mitre-attack", 0) != EXPECTED_MITRE_ATTACK:
        failures.append(f"source split {dict(source_tax)} != owasp:{EXPECTED_OWASP}/mitre-attack:{EXPECTED_MITRE_ATTACK}")
    if set(source_tax) - {"owasp", "mitre-attack"}:
        failures.append(f"unexpected source taxonomies: {set(source_tax) - {'owasp', 'mitre-attack'}}")
    confidence = Counter(e["confidence"] for e in edges)
    if dict(confidence) != EXPECTED_CONFIDENCE:
        failures.append(f"confidence {dict(confidence)} != {EXPECTED_CONFIDENCE}")
    non_primary = [e for e in edges if e["edge_type"] != "primary"]
    if non_primary:
        failures.append(f"{len(non_primary)} non-primary edges")
    blocked_ids = sorted({e["target"]["id"] for e in edges})
    if len(blocked_ids) != EXPECTED_DISTINCT_BLOCKED:
        failures.append(f"distinct _blocked_on {len(blocked_ids)} != {EXPECTED_DISTINCT_BLOCKED}")
    low_edges = {(e["source"]["id"], e["target"]["id"]) for e in edges if e["confidence"] == "low"}
    if low_edges != {EXPECTED_LOW_EDGE}:
        failures.append(f"low-confidence edge(s) {low_edges} != {{{EXPECTED_LOW_EDGE}}}")
    mitre_pair = {(e["source"]["id"], e["target"]["id"]) for e in edges if e["source"]["taxonomy"] == "mitre-attack"}
    if mitre_pair != EXPECTED_MITRE_PAIR:
        failures.append(f"mitre-attack pair {mitre_pair} != {EXPECTED_MITRE_PAIR}")
    # Exclusions: no frozen-53 targets, no non-cwe targets, nothing surviving in control.
    if any(e["target"]["id"] in frozen_ids for e in edges):
        failures.append("artifact contains a frozen-53 target (drift edge leaked in)")
    if any(e["target"]["taxonomy"] != "cwe" for e in edges):
        failures.append("artifact contains a non-cwe target")
    if any(content_key(e) in control_keys for e in edges):
        failures.append("artifact contains an edge still present in the control blob (dedupe leak)")
    if failures:
        sys.exit("FATAL: contract verification failed:\n  - " + "\n  - ".join(failures))

    # ── Emit the artifact ──
    header = "\n".join(
        [
            "# Restore-Set Artifact — Feature 185 (Issue #185, F-A1.2): T029 CWE-blocked edge restoration",
            "# Contract: specs/185-cwe-catalog-expansion/contracts/restored-edges.schema.md",
            "#",
            "# Provenance:",
            f"#   source blob:  git show {SOURCE_SHA}:{CROSSWALK_PATH}  (pre-T029, {EXPECTED_SOURCE_EDGES} edges)",
            f"#   control blob: git show {CONTROL_SHA}:{CROSSWALK_PATH}  (post-T029, {EXPECTED_CONTROL_EDGES} edges)",
            "#   filter: removed-set (present in source, absent from control by full edge content)",
            f"#           AND target.taxonomy == \"cwe\" AND target.id NOT in frozen-53 (live schemas/taxonomy/cwe.yaml)",
            f"#   counts: {EXPECTED_TOTAL} edges = {EXPECTED_OWASP} owasp->cwe + {EXPECTED_MITRE_ATTACK} mitre-attack->cwe;",
            f"#           confidence {EXPECTED_CONFIDENCE['high']} high / {EXPECTED_CONFIDENCE['medium']} medium / {EXPECTED_CONFIDENCE['low']} low; all edge_type: primary;",
            f"#           {EXPECTED_DISTINCT_BLOCKED} distinct _blocked_on CWE IDs",
            "#   exclusions (absent by construction): 1 other-drift cwe-target edge, 20 non-CWE-target",
            "#           removals, 25 dedupe collapses",
            f"#   extraction date: {EXTRACTION_DATE}",
            f"#   extraction script: {SCRIPT_REPO_PATH}",
            "#",
            "# Edge fields (edge_type/confidence/citation) are byte-copied from the source blob —",
            "# no re-authoring, no upgrades (the single `confidence: low` edge T1070.006 -> CWE-1269",
            "# stays low). `_blocked_on` is a working annotation (= the missing target CWE ID) and",
            "# MUST be stripped before W1-2 insertion (crosswalk forbids extra edge keys).",
            "",
            "",
        ]
    )
    body = "\n\n".join(
        f"{block}\n  _blocked_on: {edge['target']['id']}" for edge, block in selected
    )
    artifact_path = REPO_ROOT / ARTIFACT_REPO_PATH
    artifact_path.write_text(header + body + "\n", encoding="utf-8")

    # ── Verification summary (captured into pre-state evidence at T005) ──
    print(f"wrote {ARTIFACT_REPO_PATH}")
    print(f"total edges: {len(edges)}")
    print(
        "source-taxonomy split: owasp->cwe = "
        f"{source_tax['owasp']}, mitre-attack->cwe = {source_tax['mitre-attack']}"
    )
    print(
        f"confidence: high = {confidence['high']}, medium = {confidence['medium']}, "
        f"low = {confidence['low']}"
    )
    print(f"edge_type: primary = {len(edges) - len(non_primary)} (all primary)")
    print(f"distinct _blocked_on IDs: {len(blocked_ids)}")
    print(f"low edge preserved as-is: {EXPECTED_LOW_EDGE[0]} -> {EXPECTED_LOW_EDGE[1]} (confidence: low)")
    print("mitre-attack pair: " + ", ".join(f"{s} -> {t}" for s, t in sorted(mitre_pair)))
    print(
        "exclusions absent: 0 artifact targets in frozen-53; 0 non-cwe targets; "
        f"0 artifact edges present in control blob {CONTROL_SHA}"
    )
    print(f"frozen-53 check: live schemas/taxonomy/cwe.yaml has exactly {len(cwe_records)} records")
    print("contract verification: PASS")


if __name__ == "__main__":
    main()
