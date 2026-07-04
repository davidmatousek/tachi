"""Shared SARIF helpers for the tachi pipeline.

Provides the canonical `PREFIX_TO_RULE` mapping (single source of truth for
rule URIs across `generate-threats-sarif.py` and `generate-risk-scores-sarif.py`),
the severity-to-SARIF-level mapping, finding-ID prefix extraction, and a
threats.md → component metadata parser shared by both generators. Per-script
emit shape (logicalLocations array vs logicalLocation object, kind label
vocabulary) remains in each generator to preserve byte-identity (ADR-021).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tachi_parsers import parse_scope_data  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent


SARIF_SCHEMA_URI = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/"
    "schema/sarif-schema-2.1.0.json"
)


PREFIX_TO_RULE = {
    "S": "tachi/stride/spoofing",
    "T": "tachi/stride/tampering",
    "R": "tachi/stride/repudiation",
    "I": "tachi/stride/information-disclosure",
    "D": "tachi/stride/denial-of-service",
    "E": "tachi/stride/elevation-of-privilege",
    "AG": "tachi/ai/agentic",
    "AGP": "tachi/ai/agentic",
    "LLM": "tachi/ai/llm",
    "OI": "tachi/ai/llm",
    "MI": "tachi/ai/llm",
}


SEVERITY_TO_LEVEL = {
    "Critical": "error",
    "High": "error",
    "Medium": "warning",
    "Low": "note",
    "Note": "note",
}


def prefix_for(finding_id: str) -> str:
    return finding_id.rsplit("-", 1)[0] if "-" in finding_id else finding_id


def level_for_band(band: str) -> str:
    return SEVERITY_TO_LEVEL.get(band, "warning")


def parse_component_metadata(threats_md: str) -> dict[str, dict[str, str]]:
    """Map component name → {'zone': <trust zone>, 'dfd_type': <DFD type>}.

    Single canonical traversal of threats.md Sections 1 (Components) and 2
    (Trust Zones) via `tachi_parsers.parse_scope_data`. Replaces the
    hardcoded `COMPONENT_ZONE` dict in `generate-threats-sarif.py` (which
    silently desynced from threats.md when components changed) and the
    bespoke regex parsers `parse_trust_zones` + `parse_component_kinds` in
    `generate-risk-scores-sarif.py`. Caller is responsible for translating
    `dfd_type` (e.g. "Data Store") into its emit-specific kind label
    ("data" vs "data-store") to preserve per-script SARIF byte-identity.
    """
    scope = parse_scope_data(threats_md)
    out: dict[str, dict[str, str]] = {}
    for comp in scope["components"]:
        name = comp["name"]
        if not name:
            continue
        out[name] = {"zone": "Application Zone", "dfd_type": comp["type"]}
    for tb in scope["trust_boundaries"]:
        zone = tb["zone"]
        if not zone:
            continue
        for member in (m.strip() for m in tb["components"].split(",")):
            if member and member in out:
                out[member]["zone"] = zone
    return out


# Header cell of the populator's "## Affected Assets" table, byte-matching
# `populate-affected-assets.py` (`_COL_FINDING_ID`). Used to skip the header
# row during the inverse parse; kept local so this module stays self-contained.
_COL_FINDING_ID = "Finding ID"

_AFFECTED_ASSETS_BLOCK_PATTERN = re.compile(
    r"^##[ \t]+Affected Assets[ \t]*$(?P<body>.*?)(?=^#{1,2}[ \t]|\Z)",
    re.MULTILINE | re.DOTALL,
)
_AFFECTED_ASSETS_ROW_PATTERN = re.compile(r"^\|(?P<id>[^|]*)\|(?P<assets>[^|]*)\|")


def parse_affected_assets(threats_content: str) -> dict[str, list[str]]:
    """Map finding ID → list of asset tags from the threats.md block.

    The inverse of the deterministic populator
    (`scripts/populate-affected-assets.py` → `render_affected_assets_block`):
    it parses the always-present `## Affected Assets` markdown table back into
    `{finding_id: [tags]}`, the exact round-trip of the block the populator
    emits (`| S-1 | [phi, pii] |` → `{"S-1": ["phi", "pii"]}`; `| T-2 | [] |`
    → `{"T-2": []}`). This is the single canonical extractor the SARIF
    regeneration scripts (`generate-threats-sarif.py`,
    `generate-risk-scores-sarif.py`) and the cross-format test consume, so the
    verification tier reads one value source instead of independently
    re-deriving from `component_asset_map` (mirrors the `parse_component_metadata`
    desync-fix precedent above). Order is preserved verbatim from the block
    (already sorted ascending by the populator — this does NOT re-sort or dedup).
    Returns `{}` when no `## Affected Assets` block is present (graceful).
    """
    match = _AFFECTED_ASSETS_BLOCK_PATTERN.search(threats_content)
    if not match:
        return {}
    out: dict[str, list[str]] = {}
    for line in match.group("body").splitlines():
        row = _AFFECTED_ASSETS_ROW_PATTERN.match(line.strip())
        if not row:
            continue
        finding_id = row.group("id").replace("**", "").strip()
        # Skip the header row ("Finding ID" / "Affected Assets") and the
        # separator row ("|---|---|"); neither is a real finding.
        if not finding_id or finding_id == _COL_FINDING_ID or set(finding_id) <= {"-", ":"}:
            continue
        inner = row.group("assets").replace("**", "").strip()
        inner = inner[1:-1] if inner.startswith("[") and inner.endswith("]") else inner
        out[finding_id] = [tag.strip() for tag in inner.split(",") if tag.strip()]
    return out


def build_sarif_envelope(
    driver: dict,
    taxonomies: list[dict],
    results: list[dict],
    *,
    schema_first: bool = False,
) -> dict:
    """Assemble the SARIF 2.1.0 root document.

    `schema_first=True` emits `$schema` before `version` (threats.sarif
    legacy ordering); default emits `version` before `$schema`
    (risk-scores.sarif ordering). Field order matters for byte-identity
    under stable JSON serialization.
    """
    if schema_first:
        envelope = {
            "$schema": SARIF_SCHEMA_URI,
            "version": "2.1.0",
        }
    else:
        envelope = {
            "version": "2.1.0",
            "$schema": SARIF_SCHEMA_URI,
        }
    envelope["runs"] = [
        {
            "tool": {"driver": driver},
            "taxonomies": taxonomies,
            "results": results,
        }
    ]
    return envelope
