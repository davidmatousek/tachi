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
ITER = REPO / "specs/212-improve-executive-architecture-infographic/artifacts/final"
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


def _trust_rank_via_clusters(layer_name: str, clusters: list[dict]) -> int:
    """Cross-reference clusters[] to derive a trust-direction rank for a layer.

    Returns 0 for most-untrusted (top of page), 1 for intermediate (middle),
    2 for most-trusted (bottom of page). Falls back to 1 when the layer name
    has no matching cluster or when the cluster's trust_level is unrecognized.
    Handles trust levels with descriptive suffixes like ``trusted (managed
    infrastructure)`` and ``semi-trusted (service-role auth)`` correctly.
    """
    for c in clusters:
        if c.get("name") == layer_name:
            tl = (c.get("trust_level", "") or "").lower()
            if "untrusted" in tl:
                return 0
            if "semi" in tl:
                return 1
            if "trusted" in tl:
                return 2
            return 1
    return 1


def render_layer_block(layers: list[dict], clusters: list[dict] | None = None) -> str:
    """Compose <<layer_block>> from the layers[] payload.

    Each layer becomes a top-to-bottom stanza listing the layer name, its
    components (rendered as nodes), any qualifying callouts attached to that
    layer's components, and the optional overflow annotation. Layers are
    re-sorted for visual rendering by trust direction (most-untrusted at top,
    most-trusted at bottom) when ``clusters`` cross-reference is available;
    otherwise the payload's native order is preserved. The position label and
    pastel index assigned to each layer in the rendered prompt match the
    visual order top-to-bottom rather than the payload index, so Gemini reads
    a deterministic top-down stack.
    """
    clusters = clusters or []
    visual_layers = sorted(
        layers,
        key=lambda layer: (
            _trust_rank_via_clusters(layer.get("name", ""), clusters),
            layer.get("position", 0),
        ),
    )
    position_labels = ["TOP-OF-PAGE (most untrusted/external)",
                       "MIDDLE-OF-PAGE (intermediate)",
                       "BOTTOM-OF-PAGE (most trusted/internal)"]
    lines: list[str] = []
    for visual_index, layer in enumerate(visual_layers):
        name = layer["name"]
        components: list[str] = layer.get("components", []) or []
        overflow = layer.get("layer_overflow")
        if visual_index == 0:
            position_label = position_labels[0]
        elif visual_index == len(visual_layers) - 1 and len(visual_layers) > 1:
            position_label = position_labels[2]
        else:
            position_label = position_labels[1]
        lines.append(
            f"LAYER {visual_index} ({position_label}, pastel index "
            f"{visual_index % 5}): {name}"
        )
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


def render_flow_edges_block(flow_edges: list[dict]) -> str:
    """Compose <<flow_edges_block>> from the F-212 L3 flow_edges[] payload.

    Each entry becomes one ``source → destination [data via protocol]`` line so
    Gemini can draw an explicit directional arrow per edge. Empty string when
    the array is empty (handled by the prompt directive's fallback clause).
    """
    if not flow_edges:
        return "(no explicit data flows in payload — fall back to inter-layer arrow directive)"
    lines: list[str] = []
    for e in flow_edges:
        src = e.get("source", "") or ""
        dst = e.get("destination", "") or ""
        data = e.get("data", "") or ""
        proto = e.get("protocol", "") or ""
        if data and proto:
            label = f" [{data} via {proto}]"
        elif data:
            label = f" [{data}]"
        elif proto:
            label = f" [via {proto}]"
        else:
            label = ""
        lines.append(f"- {src} → {dst}{label}")
    return "\n".join(lines)


def render_clusters_block(clusters: list[dict]) -> str:
    """Compose <<clusters_block>> from the F-212 L3 clusters[] payload.

    Each entry becomes one ``name (trust_level): member1, member2, ...`` line
    so Gemini can draw a dashed sub-group boundary per cluster. Empty string
    when the array is empty.
    """
    if not clusters:
        return "(no trust-zone clusters in payload — omit dashed sub-group boundaries)"
    lines: list[str] = []
    for c in clusters:
        name = c.get("name", "") or ""
        tl = c.get("trust_level", "") or ""
        members = ", ".join(c.get("members", []) or [])
        lines.append(f"- {name} ({tl}): {members}")
    return "\n".join(lines)


def main() -> int:
    payload = json.loads((ITER / "spec.json").read_text(encoding="utf-8"))
    layers = payload.get("layers", [])
    callouts = payload.get("callouts", [])
    flow_edges = payload.get("flow_edges", [])
    clusters = payload.get("clusters", [])

    block = extract_verbatim_block(TEMPLATE_REF)

    # Substitutions — ONLY the bracketed <<...>> slots, per FR-212-6.
    substitutions = {
        "<<project_name>>": PROJECT_NAME,
        "<<layer_block>>": render_layer_block(layers, clusters),
        "<<callout_block>>": render_callout_block(callouts),
        "<<empty_layer_block>>": render_empty_layer_block(layers, callouts),
        "<<single_zone_caption>>": render_single_zone_caption(layers),
        "<<flow_edges_block>>": render_flow_edges_block(flow_edges),
        "<<clusters_block>>": render_clusters_block(clusters),
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
