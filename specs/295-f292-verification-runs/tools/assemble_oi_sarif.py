#!/usr/bin/env python3
"""Assemble a comparison SARIF file from raw tachi-output-integrity YAML finding blocks.

Specs-scoped verification tool (F-295 T005) -- NOT product code (ADR-046 tier
boundary; specs/295-*/tools/ keeps scripts/ product-tier clean). Reuses the
production SARIF envelope/result builders via importlib
(tests/scripts/test_affected_assets_wiring.py:520-536 precedent) so the
comparison SARIF's D-1 gate fields (partialFingerprints["findingId/v1"],
locations[].logicalLocations[].name, message.text) are built by the exact same
code that authors production threats.sarif -- no reimplementation, no drift
(contracts/oi-extraction-contract.md D-A: "assembler-tier envelope" is the
only new attribution class this path introduces).

Usage:
    python3 assemble_oi_sarif.py <findings-yaml-path> > fresh-oi.sarif

Input: a text file containing one or more ```yaml fenced code blocks (or, as a
fallback, a bare `---`-separated YAML document stream), each block a single
finding conforming to schemas/finding.yaml (v1.9), as returned verbatim by the
tachi-output-integrity agent -- see
.claude/agents/tachi/output-integrity.md "Example Findings" for the exact
per-finding block shape this parses.

Fail-closed (contracts/oi-extraction-contract.md SS2; code-economy.md
error-handling carve-out): a missing file, zero parsed finding blocks, a
malformed YAML block, or a finding missing a required gate-relevant field
each cause a non-zero exit with a message on stderr -- NEVER an
empty-but-valid SARIF on stdout.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common  # noqa: E402 -- scripts/ on sys.path above; plain module, not hyphenated


def _load_script_module(filename: str, modname: str):
    """Load a hyphenated ``scripts/<filename>`` module by file location.

    Mirrors the ``tests/scripts/test_affected_assets_wiring.py:520-536``
    precedent -- hyphenated generator filenames are not importable via
    ``import``. Loading by real file location (not a copy) means the
    generator's own ``from sarif_common import ...`` line resolves against
    the actual ``scripts/`` directory, since ``scripts/`` is already on
    ``sys.path`` (above).
    """
    path = SCRIPTS_DIR / filename
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gen_threats = _load_script_module("generate-threats-sarif.py", "generate_threats_sarif")


_YAML_FENCE_RE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL)

# Required per finding-format-shared.md "Required Fields" table -- the subset
# needed to build a comparison result via build_result(). Optional fields
# (references, dfd_element_type, maestro_layer, agentic_pattern, ...) are read
# defensively with .get() below and are never required.
_REQUIRED_FIELDS = ("id", "component", "threat", "likelihood", "impact", "risk_level", "mitigation")


def _extract_yaml_blocks(text: str) -> list[str]:
    """Return the raw text of every fenced ```yaml block in `text`, in order."""
    return [m.group(1) for m in _YAML_FENCE_RE.finditer(text)]


def _coerce_docs(parsed_docs: list) -> list[dict]:
    out: list[dict] = []
    for doc in parsed_docs:
        if doc is None:
            continue
        if isinstance(doc, list):
            out.extend(doc)
        elif isinstance(doc, dict):
            out.append(doc)
        else:
            raise ValueError(f"unexpected YAML shape: {type(doc).__name__} (expected a finding mapping or list of mappings)")
    return out


def parse_raw_findings(path: Path) -> list[dict]:
    """Parse fenced or bare YAML finding blocks from `path` into raw finding dicts.

    Primary path: extract every ```yaml fenced block and parse each
    independently (matches the tachi-output-integrity agent's own
    "Example Findings" emission style -- one fenced block per finding,
    optionally preceded by a markdown header). Fallback: no fenced blocks
    found -- parse the whole file as a bare `---`-separated YAML document
    stream (or a single top-level list), covering a findings file saved
    without markdown fencing.
    """
    text = path.read_text(encoding="utf-8")
    blocks = _extract_yaml_blocks(text)

    if blocks:
        return _coerce_docs([yaml.safe_load(block) for block in blocks])
    return _coerce_docs(list(yaml.safe_load_all(text)))


def _to_parsed_row(raw: dict) -> dict:
    """Adapt one schemas/finding.yaml (v1.9) finding dict to the parsed-row
    shape ``generate-threats-sarif.py::build_result`` expects (the shape its
    own ``parse_findings()`` produces from a threats.md table row).
    """
    missing = [f for f in _REQUIRED_FIELDS if not raw.get(f)]
    if missing:
        raise ValueError(f"finding {raw.get('id', '<no id>')!r} missing required field(s): {missing}")

    finding_id = str(raw["id"])

    owasp_ref = next(
        (ref.strip() for ref in (raw.get("references") or []) if isinstance(ref, str) and ref.strip().startswith("OWASP")),
        "",
    )

    agentic_pattern = raw.get("agentic_pattern")
    if agentic_pattern in (None, "none"):
        agentic_pattern = None

    return {
        "id": finding_id,
        "prefix": sarif_common.prefix_for(finding_id),
        "status": "[NEW]",  # fresh single-agent dispatch carries no baseline (plan D-A)
        "component": raw["component"],
        # AOD-SIMPLIFICATION: maestro_layer left blank -- single-agent OI
        # dispatch bypasses orchestrator Phase 1 classification, so the raw
        # finding never carries this field (confirmed: absent from the
        # agent's own "Example Findings"). build_result renders "Unclassified"
        # for a falsy value, which is the honest state here, not a guess.
        "maestro": raw.get("maestro_layer") or "",
        "agentic_pattern": agentic_pattern,
        "threat": raw["threat"],
        "owasp_ref": owasp_ref,
        "likelihood": raw["likelihood"],
        "impact": raw["impact"],
        "risk_level": raw["risk_level"],
        "mitigation": raw["mitigation"],
    }


def build_comparison_sarif(raw_findings: list[dict]) -> dict:
    parsed_rows = [_to_parsed_row(f) for f in raw_findings]

    # AOD-SIMPLIFICATION: component_meta left empty -- build_result()'s own
    # fallback ({"zone": "Application Zone", "dfd_type": "Process"}) is
    # already correct for every OI finding (dfd_targets: [Process] per
    # .claude/agents/tachi/output-integrity.md metadata); upgrade: derive
    # per-component dfd_type from each finding's dfd_element_type if a future
    # OI emission ever targets a non-Process element.
    component_meta: dict[str, dict[str, str]] = {}
    # affected_assets is a full-pipeline populator concern (Phase 3.7), not
    # something a single-agent dispatch authors -- [] for every finding is the
    # honest state, not a guess (contract SS5 F-260b drift class).
    affected_assets_by_id: dict[str, list[str]] = {}

    results = [_gen_threats.build_result(row, component_meta, affected_assets_by_id) for row in parsed_rows]

    driver = {
        "name": "tachi-oi-assembler",
        "semanticVersion": "0.1",
        "informationUri": "https://github.com/davidmatousek/tachi",
        "rules": [],
    }
    return sarif_common.build_sarif_envelope(driver, [], results, schema_first=True)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: assemble_oi_sarif.py <findings-yaml-path>", file=sys.stderr)
        return 1

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        raw_findings = parse_raw_findings(input_path)
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {input_path}: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not raw_findings:
        print(f"ERROR: zero finding blocks parsed from {input_path}", file=sys.stderr)
        return 1

    try:
        sarif = build_comparison_sarif(raw_findings)
    except (ValueError, KeyError) as exc:
        print(f"ERROR: failed to build comparison SARIF: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(sarif, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
