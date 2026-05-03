#!/usr/bin/env python3
"""T009 iteration-1 — build the verbatim Gemini prompt for the second-brain-mcp dataset.

Reads:
  - spec.json (the executive-architecture payload from extract-infographic-data.py)
  - .claude/skills/tachi-infographics/references/executive-architecture.md (the
    VERBATIM-locked prompt block, FR-212-6)

Writes:
  - prompt.txt (the substituted prompt, ready to send to Gemini)

Per FR-212-6: the locked text is copied verbatim; only the bracketed <<...>>
slots are substituted with payload data.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path("/Users/david/Projects/tachi")
ITER = REPO / "specs/212-improve-executive-architecture-infographic/artifacts/iteration-1"
TEMPLATE_REF = REPO / ".claude/skills/tachi-infographics/references/executive-architecture.md"

BEGIN_MARKER = "=== BEGIN VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ==="
END_MARKER = "=== END VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ==="

# Project name for the second-brain-mcp dataset. The producer payload does not
# emit a project_name field for executive-architecture, so derive from the
# source file path. (The dataset directory is the canonical name for this run.)
PROJECT_NAME = "second-brain-mcp"


def extract_verbatim_block(template_md: Path) -> str:
    text = template_md.read_text(encoding="utf-8")
    begin_idx = text.index(BEGIN_MARKER)
    end_idx = text.index(END_MARKER, begin_idx)
    # Slice from the start of BEGIN_MARKER to the end of END_MARKER.
    return text[begin_idx : end_idx + len(END_MARKER)]


def render_layer_block(layers: list[dict]) -> str:
    """Compose <<layer_block>> from the layers[] payload.

    Each layer becomes a top-to-bottom stanza listing the layer name, its
    components (rendered as nodes), any qualifying callouts attached to that
    layer's components, and the optional overflow annotation.
    """
    lines: list[str] = []
    for layer in layers:
        name = layer["name"]
        position = layer["position"]
        components: list[str] = layer.get("components", []) or []
        overflow = layer.get("layer_overflow")
        lines.append(f"LAYER {position} (pastel index {position % 5}): {name}")
        if components:
            lines.append("  Components (each rendered as a rounded-rectangle node):")
            for comp in components:
                lines.append(f"    - {comp}")
        if overflow:
            lines.append(f"  Overflow annotation: {overflow}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_callout_block(callouts: list[dict]) -> str:
    """Compose <<callout_block>> from the callouts[] payload.

    Each entry includes the finding ID, severity word, the affected component
    (the leader-line anchor), and the raw description (Gemini will rewrite to
    <=25 words at render time).
    """
    if not callouts:
        return "(no qualifying Critical/High callouts in this dataset)"
    lines: list[str] = []
    for c in callouts:
        fid = c["finding_id"]
        sev = c["severity"]
        comp = c["affected_component"]
        layer = c["layer_name"]
        raw = c["raw_description"]
        lines.append(
            f"- [{fid}] {sev} (anchor: {comp} in layer \"{layer}\"): {raw}"
        )
    return "\n".join(lines)


def render_empty_layer_block(layers: list[dict], callouts: list[dict]) -> str:
    """Compose <<empty_layer_block>> — one badge per layer with zero qualifying findings."""
    layers_with_callouts = {c["layer_name"] for c in callouts}
    empty_layers = [l for l in layers if l["name"] not in layers_with_callouts]
    if not empty_layers:
        return "(none — every layer has at least one qualifying Critical/High finding)"
    lines: list[str] = []
    for layer in empty_layers:
        lines.append(
            f"- {layer['name']}: render as compact factual badge (<=15% page height) "
            f"containing the literal text \"0 High/Critical findings in this layer\"."
        )
    return "\n".join(lines)


def render_single_zone_caption(layers: list[dict]) -> str:
    """Compose <<single_zone_caption>> — empty unless exactly one layer."""
    if len(layers) == 1:
        return f"(Single-zone caption: \"All components reside in the {layers[0]['name']} trust zone\")"
    return ""


def main() -> int:
    payload = json.loads((ITER / "spec.json").read_text(encoding="utf-8"))
    layers = payload.get("layers", [])
    callouts = payload.get("callouts", [])

    block = extract_verbatim_block(TEMPLATE_REF)

    # Substitutions — ONLY the bracketed <<...>> slots, per FR-212-6.
    substitutions = {
        "<<project_name>>": PROJECT_NAME,
        "<<layer_block>>": render_layer_block(layers),
        "<<callout_block>>": render_callout_block(callouts),
        "<<empty_layer_block>>": render_empty_layer_block(layers, callouts),
        "<<single_zone_caption>>": render_single_zone_caption(layers),
    }

    rendered = block
    for slot, value in substitutions.items():
        if slot not in rendered:
            print(f"WARN: slot {slot} not found in verbatim block", file=sys.stderr)
        rendered = rendered.replace(slot, value)

    # Sanity: no <<...>> placeholders should remain unsubstituted.
    leftovers = re.findall(r"<<[A-Za-z_]+>>", rendered)
    if leftovers:
        print(f"ERROR: unsubstituted placeholders: {leftovers}", file=sys.stderr)
        return 1

    out = ITER / "prompt.txt"
    out.write_text(rendered, encoding="utf-8")
    print(f"prompt.txt written ({len(rendered)} chars) to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
