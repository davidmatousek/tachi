#!/usr/bin/env python3
"""Deterministic extraction of structured data from tachi pipeline markdown artifacts.

Reads threats.md, risk-scores.md, compensating-controls.md, and threat-report.md
from a target directory and writes a Typst data file (report-data.typ) with all
variable bindings needed by the security report templates.

Exit codes:
  0 — success
  1 — missing required artifact (threats.md)
  2 — validation failure (severity sum mismatch, duplicate IDs, etc.)
"""

import argparse
import functools
import os
import re
import concurrent.futures
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tachi_parsers import (
    EXIT_SUCCESS,
    EXIT_MISSING_ARTIFACT,
    EXIT_VALIDATION_FAILURE,
    SEVERITY_ORDER,
    SEVERITY_ORDINAL,
    MAESTRO_LAYERS,
    escape_typst_string,
    parse_frontmatter,
    parse_baseline_frontmatter,
    parse_resolved_findings,
    compute_delta_counts,
    parse_markdown_table,
    parse_project_name,
    detect_artifacts,
    determine_tier,
    parse_threats_severity,
    parse_risk_scores_severity,
    _empty_severity,
    parse_threats_findings,
    parse_risk_scores_findings,
    parse_component_distribution,
    parse_scope_data,
    parse_compensating_controls_md,
    parse_attack_chains,
    strip_bold,
    _extract_source_attribution_block,
    _extract_source_attribution,
)

# SLA mapping by severity for remediation actions
SLA_BY_SEVERITY = {
    "Critical": "7d",
    "High": "14d",
    "Medium": "30d",
    "Low": "90d",
}


# =============================================================================
# Threat Report Parser (T021)
# =============================================================================

def parse_threat_report_md(content: str) -> dict:
    """Parse threat-report.md for executive narrative and remediation timeline.

    Extracts:
    - Executive narrative from Section 1: Risk Posture + Top 5 Threats + Key Recommendations
      (truncated to 2000 chars)
    - Remediation timeline entries from Section 1: Remediation Timeline subsection
    """
    result = {
        "executive_narrative": None,
        "remediation_timeline": [],
    }

    if not content or not content.strip():
        return result

    lines = content.split("\n")

    # Find Section 1 boundaries
    sec1_start = None
    sec1_end = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^##\s+1\.\s+Executive Summary", line):
            sec1_start = i + 1
        elif sec1_start is not None and re.match(r"^##\s+\d+\.", line):
            sec1_end = i
            break

    if sec1_start is None:
        return result

    # Identify subsection boundaries within Section 1
    subsections = {}  # name -> [start_line, end_line]
    sub_order = []
    for i in range(sec1_start, sec1_end):
        match = re.match(r"^###\s+(.+)", lines[i])
        if match:
            name = match.group(1).strip()
            subsections[name] = [i + 1, sec1_end]
            sub_order.append(name)
            # Close previous subsection
            if len(sub_order) >= 2:
                subsections[sub_order[-2]][1] = i

    # Build executive narrative. Preferred shape: Risk Posture / Top 5 Threats /
    # Key Recommendations ### subsections (for threat-report agent versions that
    # emit them). Fallback: the entire prose block under ## 1. Executive Summary
    # — the current agent writes a single narrative with bold-label paragraphs
    # (**Risk profile**, **Most critical unresolved exposure**, **New findings**)
    # rather than labeled subsections.
    narrative_sections = [
        "Risk Posture",
        "Top 5 Threats by Business Impact",
        "Key Recommendations",
    ]
    narrative_parts = []
    for name in narrative_sections:
        if name in subsections:
            start, end = subsections[name]
            text = "\n".join(lines[start:end]).strip()
            if text:
                narrative_parts.append(text)

    if not narrative_parts:
        # Remediation Timeline is parsed structurally below; exclude it from
        # the narrative fallback to avoid duplication when the agent happens
        # to emit both prose and a ### Remediation Timeline subsection.
        prose_end = sec1_end
        if "Remediation Timeline" in subsections:
            prose_end = min(prose_end, subsections["Remediation Timeline"][0] - 1)
        prose_text = "\n".join(lines[sec1_start:prose_end]).strip()
        if prose_text:
            narrative_parts.append(prose_text)

    if narrative_parts:
        narrative = "\n\n".join(narrative_parts)
        if len(narrative) > 2000:
            narrative = narrative[:2000]
        result["executive_narrative"] = narrative

    # Parse Remediation Timeline
    if "Remediation Timeline" in subsections:
        start, end = subsections["Remediation Timeline"]
        for i in range(start, end):
            line = lines[i].strip()
            if line.startswith("- **"):
                match = re.match(
                    r"^-\s+\*\*(\w[\w\-]*)\*\*\s+\((\d+)\s+(\w+)\s+findings?\)",
                    line,
                )
                if match:
                    result["remediation_timeline"].append({
                        "timeline": match.group(1),
                        "count": int(match.group(2)),
                        "severity": match.group(3),
                    })

    return result


# =============================================================================
# Remediation Actions (T023)
# =============================================================================

def build_remediation_actions(findings: list, tier: int,
                               cc_data: dict = None,
                               tr_data: dict = None) -> list:
    """Build remediation actions using source priority.

    Priority:
    1. compensating-controls.md recommendations (Tier 1 — findings have recommendation field)
    2. threat-report.md Remediation Timeline (Tier 2/3 — severity-based SLA)
    3. None (no remediation source available)
    """
    if not findings:
        return None

    # Source 1: Compensating controls (Tier 1)
    if tier == 1 and cc_data is not None:
        actions = []
        for f in findings:
            severity = f.get("residual_severity", "")
            actions.append({
                "severity": severity,
                "finding-id": f.get("id", ""),
                "finding-name": f.get("threat", ""),
                "recommendation": f.get("recommendation", ""),
                "sla": SLA_BY_SEVERITY.get(severity, "90d"),
                "status": f.get("control_status", "pending"),
            })
        return actions if actions else None

    # Source 2: Threat report with remediation timeline
    if tr_data is not None and tr_data.get("remediation_timeline"):
        actions = []
        for f in findings:
            if tier == 2:
                severity = f.get("severity", "")
                rec_text = f.get("threat", "")
            else:  # tier == 3
                severity = f.get("risk_level", "")
                rec_text = f.get("mitigation", "")
            actions.append({
                "severity": severity,
                "finding-id": f.get("id", ""),
                "finding-name": f.get("threat", ""),
                "recommendation": rec_text,
                "sla": SLA_BY_SEVERITY.get(severity, "90d"),
                "status": "pending",
            })
        return actions if actions else None

    # Source 3: No remediation source
    return None


# =============================================================================
# MAESTRO Data Parsing
# =============================================================================

# Aliases for shared constants
_MAESTRO_LAYERS = MAESTRO_LAYERS
_SEVERITY_ORDINAL = SEVERITY_ORDINAL


def parse_maestro_data(threats_content):
    """Parse MAESTRO layer data from threats.md for report-data.typ.

    Extracts:
    - Section 6 "Risk by MAESTRO Layer" table for per-layer aggregates
    - Section 3/4 agent tables for per-finding MAESTRO layer assignment
    - Groups findings by layer for the MAESTRO findings page

    Returns dict with:
      - has_maestro_data (bool)
      - maestro_layer_distribution (list of dicts)
      - most_exposed_layer (str)
      - maestro_findings_by_layer (list of layer groups)
    """
    result = {
        "has_maestro_data": False,
        "maestro_layer_distribution": [],
        "most_exposed_layer": "",
        "maestro_findings_by_layer": [],
    }

    if not threats_content or not threats_content.strip():
        return result

    # --- Parse Section 6 layer distribution table ---
    layer_dist = parse_markdown_table(threats_content, "#### Risk by MAESTRO Layer")
    parsed_layers = []
    for row in layer_dist:
        layer_raw = row.get("MAESTRO Layer", "").strip()
        if not layer_raw:
            continue
        # Handle both em-dash (—) and en-dash (–) for robustness
        parts = layer_raw.split("\u2014", 1)  # em-dash
        if len(parts) < 2:
            parts = layer_raw.split("\u2013", 1)  # en-dash fallback
        if len(parts) == 2:
            layer_id = parts[0].strip()
            layer_name = parts[1].strip()
        else:
            layer_id = layer_raw
            layer_name = ""

        try:
            finding_count = int(row.get("Finding Count", "0").strip())
        except ValueError:
            finding_count = 0

        highest_severity = row.get("Highest Severity", "").strip()

        parsed_layers.append({
            "layer_id": layer_id,
            "layer_name": layer_name,
            "finding_count": finding_count,
            "highest_severity": highest_severity,
        })

    result["maestro_layer_distribution"] = parsed_layers

    # --- Parse Section 3/4 per-finding MAESTRO layer ---
    lines = threats_content.split("\n")
    per_finding = []

    agent_sections = []
    for i, line in enumerate(lines):
        if re.match(r"^###\s+[34]\.\d+\s+", line):
            agent_sections.append(i)

    for sec_start in agent_sections:
        header_cols = None
        for i in range(sec_start + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("## ") or stripped.startswith("### "):
                break
            if not stripped.startswith("|"):
                continue
            # Parse header row
            if header_cols is None:
                cells = [strip_bold(c.strip()) for c in stripped.split("|")[1:-1]]
                if cells and cells[0].lower() == "id":
                    header_cols = cells
                continue
            # Skip separator row
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            # Data row
            cells = [strip_bold(c.strip()) for c in stripped.split("|")[1:-1]]
            if not cells or not cells[0]:
                continue
            fid = cells[0]
            if not fid or not re.match(r"^[A-Z]", fid):
                continue

            # Find column indices dynamically
            maestro_idx = None
            comp_idx = None
            threat_idx = None
            risk_idx = None
            if header_cols:
                for idx, col in enumerate(header_cols):
                    if col == "MAESTRO Layer":
                        maestro_idx = idx
                    elif col == "Component":
                        comp_idx = idx
                    elif col == "Threat":
                        threat_idx = idx
                    elif col == "Risk Level":
                        risk_idx = idx

            maestro_layer = ""
            if maestro_idx is not None and maestro_idx < len(cells):
                maestro_layer = cells[maestro_idx].strip()

            component = cells[comp_idx].strip() if comp_idx is not None and comp_idx < len(cells) else ""
            threat = cells[threat_idx].strip() if threat_idx is not None and threat_idx < len(cells) else ""
            risk_level = cells[risk_idx].strip() if risk_idx is not None and risk_idx < len(cells) else ""

            per_finding.append({
                "id": fid,
                "component": component,
                "maestro_layer": maestro_layer,
                "severity": risk_level,
                "threat": threat,
            })

    # --- Group findings by MAESTRO layer ---
    # Build layer_id -> {layer_name, findings} mapping
    layer_groups = {}

    # Pre-populate from distribution table to preserve canonical ordering
    for layer in parsed_layers:
        lid = layer["layer_id"]
        layer_groups[lid] = {
            "layer_id": lid,
            "layer_name": layer["layer_name"],
            "findings": [],
        }

    # Assign findings to layer groups
    for f in per_finding:
        layer_raw = f.get("maestro_layer", "")
        if not layer_raw:
            lid = "Unclassified"
            lname = "Unclassified"
        else:
            parts = layer_raw.split("\u2014", 1)
            lid = parts[0].strip().split("\u2013")[0].strip()  # handle both em-dash and en-dash
            lname = parts[1].strip() if len(parts) == 2 else lid

        if lid not in layer_groups:
            layer_groups[lid] = {
                "layer_id": lid,
                "layer_name": lname,
                "findings": [],
            }

        layer_groups[lid]["findings"].append({
            "id": f["id"],
            "component": f["component"],
            "severity": f["severity"],
            "threat": f["threat"],
        })

    # Sort layers: L1-L7 in canonical order, then Unclassified, then any others
    def layer_sort_key(lid):
        if lid in _MAESTRO_LAYERS:
            return (0, _MAESTRO_LAYERS.index(lid))
        elif lid == "Unclassified":
            return (1, 0)
        else:
            return (2, lid)

    sorted_layer_ids = sorted(layer_groups.keys(), key=layer_sort_key)
    findings_by_layer = [layer_groups[lid] for lid in sorted_layer_ids if layer_groups[lid]["findings"]]

    result["maestro_findings_by_layer"] = findings_by_layer

    # --- Compute most exposed layer ---
    if parsed_layers:
        best = max(
            parsed_layers,
            key=lambda l: (
                l["finding_count"],
                _SEVERITY_ORDINAL.get(l["highest_severity"], 0),
            ),
        )
        if best["layer_name"]:
            result["most_exposed_layer"] = f"{best['layer_id']} \u2014 {best['layer_name']}"
        else:
            result["most_exposed_layer"] = best["layer_id"]

    # --- Determine if MAESTRO data is present ---
    has_data = bool(parsed_layers) or any(f.get("maestro_layer") for f in per_finding)
    result["has_maestro_data"] = has_data

    return result


# =============================================================================
# Attack Tree Parsing
# =============================================================================

def parse_attack_trees(target_dir: Path, findings: list, tr_content: str = None) -> list:
    """Parse attack tree files and cross-reference with findings data.

    Scans {target_dir}/attack-trees/ for all .md files (the attack-tree-delta
    agent emits {ID}-{slug}.md; _parse_attack_tree_file skips unrelated files
    by returning None when no Finding ID or Mermaid block is present). Falls
    back to inline trees in threat-report.md Section 5. Filters to Critical
    and High severity only, sorted by severity (Critical first) then finding ID.

    Args:
        target_dir: Directory containing tachi pipeline artifacts.
        findings: Parsed findings list for cross-referencing severity/mitigation.
        tr_content: Pre-loaded threat-report.md content (avoids redundant read).

    Returns:
        List of dicts with keys: id, component, severity, title, mermaid_code,
        mitigation, narrative, remediation.
    """
    # Build a lookup from finding ID to finding data
    findings_by_id = {}
    for f in findings:
        fid = f.get("id", "")
        if fid:
            findings_by_id[fid] = f

    entries = []
    attack_trees_dir = target_dir / "attack-trees"

    # Primary source: standalone attack tree files. The attack-tree-delta agent
    # writes files as {ID}-{slug}.md (e.g. "AG-1-mcp-stdio-no-human-gate.md").
    # Glob all .md files and let _parse_attack_tree_file filter by structure —
    # it returns None for files without a parseable Finding ID or Mermaid block.
    if attack_trees_dir.is_dir():
        tree_files = sorted(attack_trees_dir.glob("*.md"))
        for tree_file in tree_files:
            entry = _parse_attack_tree_file(tree_file, findings_by_id)
            if entry:
                entries.append(entry)

    # Fallback: inline trees from threat-report.md Section 5
    if not entries:
        if tr_content is None:
            tr_path = target_dir / "threat-report.md"
            if tr_path.exists():
                tr_content = tr_path.read_text(encoding="utf-8")
        if tr_content:
            entries = _parse_inline_attack_trees(tr_content, findings_by_id)

    # Filter to Critical and High only (ordinal >= 3)
    _MIN_ATTACK_PATH_SEVERITY = 3
    entries = [e for e in entries if SEVERITY_ORDINAL.get(e["severity"], 0) >= _MIN_ATTACK_PATH_SEVERITY]

    # Sort: highest severity first, then by finding ID
    entries.sort(key=lambda e: (-SEVERITY_ORDINAL.get(e["severity"], 0), e["id"].lower()))

    # Add narrative and remediation for each entry
    for entry in entries:
        entry["narrative"] = _build_narrative(entry)
        entry["remediation"] = _build_remediation(entry.get("mitigation", ""))

    return entries


def _parse_attack_tree_file(filepath: Path, findings_by_id: dict) -> dict:
    """Parse a single attack tree markdown file.

    Expected format:
      # Attack Tree: {ID} -- {Title}
      | Field | Value |
      |-------|-------|
      | Finding ID | {ID} |
      | Component | {component} |
      | Risk Level | {severity} |
      | Threat | {title} |
      ```mermaid
      ...
      ```
    """
    content = filepath.read_text(encoding="utf-8")

    # Parse metadata table
    meta = {}
    lines = content.split("\n")
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("| Field"):
            in_table = True
            continue
        if in_table and stripped.startswith("|---"):
            continue
        if in_table and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cells) >= 2:
                meta[cells[0]] = cells[1]
        elif in_table and not stripped.startswith("|"):
            in_table = False

    finding_id = meta.get("Finding ID", "").strip()
    component = meta.get("Component", "").strip()
    file_severity = meta.get("Risk Level", "").strip()
    title = meta.get("Threat", "").strip()

    # Fallback: extract finding ID and title from H1 heading when the metadata
    # table is absent. Supports "# Attack Tree: AG-1 -- Title" and "# AG-1: Title".
    if not finding_id:
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("# "):
                continue
            heading = stripped[2:].strip()
            m = re.match(r"^Attack Tree:\s+(\S+?):?\s+[-\u2014]+\s+(.*)$", heading)
            if m:
                finding_id = m.group(1)
                title = title or m.group(2).strip()
                break
            m = re.match(r"^([A-Za-z]+-\d+):\s+(.*)$", heading)
            if m:
                finding_id = m.group(1)
                title = title or m.group(2).strip()
                break
        if not finding_id:
            return None

    # Extract Mermaid code block
    mermaid_code = _extract_mermaid_block(content)
    if not mermaid_code:
        return None

    # Cross-reference with findings for authoritative severity and mitigation
    finding = findings_by_id.get(finding_id, {})
    # Authoritative severity from findings data
    severity = _get_finding_severity(finding) or file_severity
    component = component or finding.get("component", "")
    title = title or finding.get("threat", "")
    mitigation = _get_finding_mitigation(finding)

    return {
        "id": finding_id,
        "component": component,
        "severity": severity,
        "title": title,
        "mermaid_code": mermaid_code,
        "mitigation": mitigation,
    }


def _parse_inline_attack_trees(content: str, findings_by_id: dict) -> list:
    """Extract inline attack trees from threat-report.md Section 5."""
    entries = []
    lines = content.split("\n")

    # Find Section 5 boundaries
    sec5_start = None
    sec5_end = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^##\s+5\.\s+Attack Tree", line):
            sec5_start = i
        elif sec5_start is not None and re.match(r"^##\s+\d+\.", line):
            sec5_end = i
            break

    if sec5_start is None:
        return entries

    # Find each attack tree subsection: "## Attack Tree: {ID}" or "### {ID}"
    # Captured IDs may carry a trailing colon from the "### AG-1: Title" form, so
    # strip it before use — otherwise the findings_by_id lookup silently misses.
    current_id = None
    current_start = None

    for i in range(sec5_start, sec5_end):
        line = lines[i].strip()
        id_match = re.match(r"^###?\s+(?:Attack Tree:\s*)?(\S+)", line)
        if id_match and i > sec5_start:
            if current_id and current_start:
                block = "\n".join(lines[current_start:i])
                entry = _parse_inline_tree_block(current_id, block, findings_by_id)
                if entry:
                    entries.append(entry)
            current_id = id_match.group(1).rstrip(":")
            current_start = i

    # Handle last block
    if current_id and current_start:
        block = "\n".join(lines[current_start:sec5_end])
        entry = _parse_inline_tree_block(current_id, block, findings_by_id)
        if entry:
            entries.append(entry)

    return entries


def _parse_inline_tree_block(finding_id: str, block: str, findings_by_id: dict) -> dict:
    """Parse a single inline attack tree block from threat-report.md."""
    mermaid_code = _extract_mermaid_block(block)
    if not mermaid_code:
        return None

    finding = findings_by_id.get(finding_id, {})
    severity = _get_finding_severity(finding)
    component = finding.get("component", "")
    title = finding.get("threat", "")
    mitigation = _get_finding_mitigation(finding)

    return {
        "id": finding_id,
        "component": component,
        "severity": severity or "Unknown",
        "title": title,
        "mermaid_code": mermaid_code,
        "mitigation": mitigation,
    }


def _extract_mermaid_block(content: str) -> str:
    """Extract the first Mermaid code block from content."""
    match = re.search(r"```mermaid\s*\n(.*?)```", content, re.DOTALL)
    return match.group(1).strip() if match else ""


def _get_finding_severity(finding: dict) -> str:
    """Get authoritative severity from a finding dict (tier-aware)."""
    # Tier 1: residual_severity, Tier 2: severity, Tier 3: risk_level
    return (finding.get("residual_severity")
            or finding.get("severity")
            or finding.get("risk_level")
            or "")


def _get_finding_mitigation(finding: dict) -> str:
    """Get mitigation text from a finding dict (tier-aware)."""
    return (finding.get("recommendation")
            or finding.get("mitigation")
            or "")


def _build_narrative(entry: dict) -> str:
    """Construct a 2-4 sentence narrative from attack tree data."""
    component = entry.get("component", "") or "the system"
    title = entry.get("title", "") or "achieve unauthorized access"
    mermaid = entry.get("mermaid_code", "")

    # Parse root node label
    root_label = title
    root_match = re.search(r'\["([^"]+)"\]', mermaid)
    if root_match:
        root_label = root_match.group(1)

    # Detect OR/AND gates
    gates = re.findall(r'\{\{"(OR|AND)"\}\}', mermaid)

    # Extract leaf node labels (nodes with no outgoing edges)
    all_nodes = {}
    for m in re.finditer(r'(\w+)\["([^"]+)"\]', mermaid):
        all_nodes[m.group(1)] = m.group(2)
    for m in re.finditer(r'(\w+)\{\{"[^"]*"\}\}', mermaid):
        all_nodes.pop(m.group(1), None)

    # Find source nodes (nodes that appear on left side of -->)
    sources = set()
    for m in re.finditer(r'(\w+)\s*-->', mermaid):
        sources.add(m.group(1))

    # Leaf nodes are those not in sources
    leaf_labels = [label for nid, label in all_nodes.items() if nid not in sources]

    narrative = f"An attacker targets {component} by attempting to {root_label.lower()}."

    if gates:
        gate_type = "any of" if "OR" in gates else "all of"
        if "OR" in gates and "AND" in gates:
            gate_type = "combinations of"
        narrative += f" The attack proceeds through {gate_type} several attack paths."

    if leaf_labels:
        actions = leaf_labels[:3]
        action_text = ", ".join(f'"{a}"' for a in actions)
        if len(leaf_labels) > 3:
            action_text += f", and {len(leaf_labels) - 3} additional actions"
        narrative += f" Required attacker actions include {action_text}."

    return narrative


def _build_remediation(mitigation: str) -> list:
    """Split mitigation text into a list of remediation steps."""
    if not mitigation:
        return ["Review and implement appropriate security controls."]

    # Split at sentence boundaries or semicolons
    parts = re.split(r'(?<=[.!])\s+|;\s*', mitigation)
    steps = [p.strip() for p in parts if p.strip() and len(p.strip()) > 5]

    return steps if steps else [mitigation.strip()]


# =============================================================================
# Mermaid Rendering
# =============================================================================

# Per-invocation render context. Module-level (not closed-over) so
# _render_single keeps a 2-arg signature that test fixtures can patch.
_render_attack_trees_dir: "Path | None" = None
_render_rel_target: "str | None" = None


def _build_error_record(fid: str, failure_class: str, stderr_bytes, subdir: str = "attack-trees") -> dict:
    raw = stderr_bytes if stderr_bytes is not None else b""
    if isinstance(raw, str):
        excerpt = raw[:200]
    else:
        excerpt = raw[:200].decode("utf-8", errors="replace")
    return {
        "id": fid,
        "file_path": f"{subdir}/{fid.lower()}.mmd",
        "failure_class": failure_class,
        "stderr_excerpt": excerpt,
    }


def _render_single(entry, tmp_path):
    """Render one Mermaid entry to PNG. Returns ``(entry, success, value)``.

    On success, ``value`` is the relative image path string for Typst.
    On failure, ``value`` is a structured error-record dict with keys
    ``id``, ``file_path``, ``failure_class`` (``"exit:<code>"``, ``"timeout"``,
    or ``"signal"``), and ``stderr_excerpt`` (first 200 bytes).
    """
    fid = entry["id"]
    fid_lower = fid.lower()
    mermaid_code = entry.get("mermaid_code", "")
    if not mermaid_code:
        return (entry, False, "")

    mmd_file = tmp_path / f"{fid_lower}.mmd"
    png_file = tmp_path / f"{fid_lower}.png"
    mmd_file.write_text(mermaid_code, encoding="utf-8")

    try:
        subprocess.run(
            ["mmdc", "-i", str(mmd_file), "-o", str(png_file), "-s", "2", "-b", "transparent"],
            capture_output=True,
            timeout=30,
            check=True,
        )
        dest_png = _render_attack_trees_dir / f"{fid_lower}-attack-tree.png"
        shutil.copy2(str(png_file), str(dest_png))
        return (entry, True, _render_rel_target + "/attack-trees/" + f"{fid_lower}-attack-tree.png")
    except subprocess.CalledProcessError as e:
        failure_class = "signal" if e.returncode < 0 else f"exit:{e.returncode}"
        return (entry, False, _build_error_record(fid, failure_class, e.stderr))
    except subprocess.TimeoutExpired as e:
        return (entry, False, _build_error_record(fid, "timeout", e.stderr))


def render_mermaid_to_png(attack_trees: list, target_dir: Path, template_dir: Path):
    """Render Mermaid code blocks to PNG images via mmdc.

    Modifies attack_trees entries in-place, setting has_image and image_path.
    Preflight gate: raises RuntimeError if mmdc is not on PATH.
    Mid-render aggregator: raises RuntimeError with a per-finding failure list
    if any individual render fails after the preflight gate has passed.

    Args:
        attack_trees: List of attack tree dicts (must have id, mermaid_code keys).
        target_dir: Directory containing the attack-trees/ subdirectory.
        template_dir: Typst template directory (for relative path calculation).
    """
    if not attack_trees:
        return

    if not shutil.which("mmdc"):
        raise RuntimeError(
            "Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).\n"
            "Install with: npm install -g @mermaid-js/mermaid-cli\n"
            "Then re-run /tachi.security-report."
        )

    # Compute relative path from template_dir to target_dir
    try:
        rel_target = os.path.relpath(str(target_dir), str(template_dir))
    except ValueError:
        rel_target = str(target_dir)

    attack_trees_dir = target_dir / "attack-trees"
    attack_trees_dir.mkdir(exist_ok=True)

    global _render_attack_trees_dir, _render_rel_target
    _render_attack_trees_dir = attack_trees_dir
    _render_rel_target = rel_target

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(_render_single, entry, tmp_path) for entry in attack_trees]
            failures = []
            for future in concurrent.futures.as_completed(futures):
                entry, success, value = future.result()
                if success:
                    entry["has_image"] = True
                    entry["image_path"] = value
                else:
                    entry["has_image"] = False
                    entry["image_path"] = ""
                    if isinstance(value, dict):
                        failures.append(value)

            if failures:
                lines = [f"Attack path rendering failed for {len(failures)} findings:"]
                for rec in failures:
                    lines.append(f"  - {rec['id']} ({rec['file_path']})")
                    lines.append(f"    failure: {rec['failure_class']}")
                    lines.append(f"    stderr: {rec['stderr_excerpt']}")
                raise RuntimeError("\n".join(lines))


# =============================================================================
# Attack Chain Processing
# =============================================================================

# Canonical MAESTRO layer names for Mermaid diagram node labels.
_MAESTRO_LAYER_NAMES = {
    "L1": "Foundation Model",
    "L2": "Data Operations",
    "L3": "Agent Framework",
    "L4": "Deployment Infrastructure",
    "L5": "Evaluation and Observability",
    "L6": "Security and Compliance",
    "L7": "Agent Ecosystem",
}

# Mermaid node colors per MAESTRO layer (distinct from attack tree red/orange).
_MAESTRO_LAYER_COLORS = {
    "L1": "#6366f1",  # indigo
    "L2": "#8b5cf6",  # violet
    "L3": "#a855f7",  # purple
    "L4": "#3b82f6",  # blue
    "L5": "#06b6d4",  # cyan
    "L6": "#14b8a6",  # teal
    "L7": "#f59e0b",  # amber
}


def generate_chain_mermaid(chain: dict) -> str:
    """Generate a Mermaid flowchart TD diagram for a single attack chain.

    Produces a vertical MAESTRO layer stack with L1 at top, L7 at bottom,
    downward attack progression arrows with causal labels between layers.

    Args:
        chain: Parsed chain dict from parse_attack_chains().

    Returns:
        Mermaid flowchart source string.
    """
    findings = chain.get("findings", [])
    if not findings:
        return ""

    lines = ["flowchart TD"]

    # Define nodes for each finding in layer order
    for f in findings:
        raw_layer = f.get("maestro_layer", "")
        finding_id = f.get("finding_id", "")
        component = f.get("component", "")
        category = f.get("category", "")
        # Normalize long-form "L1 — Foundation Model" to short-form "L1"
        layer_match = re.match(r"(L\d)", raw_layer)
        layer = layer_match.group(1) if layer_match else raw_layer
        layer_name = _MAESTRO_LAYER_NAMES.get(layer, layer)
        color = _MAESTRO_LAYER_COLORS.get(layer, "#64748b")

        # Node ID uses normalized short-form layer code (safe for Mermaid identifiers)
        node_id = layer
        label = f"{layer}: {layer_name}"
        if finding_id:
            label += f"<br/>{finding_id}"
        if component:
            label += f"<br/>{component}"

        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    style {node_id} fill:{color},stroke:#1e293b,color:#fff")

    # Define edges between consecutive findings with causal labels
    for i in range(len(findings) - 1):
        raw_src = findings[i].get("maestro_layer", "")
        raw_dst = findings[i + 1].get("maestro_layer", "")
        src_match = re.match(r"(L\d)", raw_src)
        dst_match = re.match(r"(L\d)", raw_dst)
        src = src_match.group(1) if src_match else raw_src.replace(" ", "")
        dst = dst_match.group(1) if dst_match else raw_dst.replace(" ", "")
        lines.append(f'    {src} -->|"enables"| {dst}')

    return "\n".join(lines)


def prepare_attack_chains(target_dir: Path, findings: list, template_dir: Path) -> tuple:
    """Parse attack chains, generate Mermaid diagrams, and render to PNG.

    Follows the same pattern as parse_attack_trees + render_mermaid_to_png
    but generates Mermaid code from structured chain data.

    Args:
        target_dir: Directory containing attack-chains.md artifact.
        findings: Parsed findings list for cross-referencing.
        template_dir: Typst template directory (for relative path calculation).

    Returns:
        (has_attack_chains: bool, chains: list of chain dicts with rendering data)
    """
    chains_file = target_dir / "attack-chains.md"
    if not chains_file.exists():
        return False, []

    content = chains_file.read_text(encoding="utf-8")
    chains = parse_attack_chains(content)

    if not chains:
        return False, []

    # Filter to surfaced chains only (Critical/High) for PDF rendering
    surfaced = [c for c in chains if c.get("surfaced", False)]

    if not surfaced:
        return True, chains  # chains exist but none surfaced for PDF

    # Generate Mermaid code for each surfaced chain
    for chain in surfaced:
        chain["mermaid_code"] = generate_chain_mermaid(chain)

    # Prepare rendering entries (adapt to render_mermaid_to_png interface)
    render_entries = []
    for chain in surfaced:
        if chain.get("mermaid_code"):
            render_entries.append({
                "id": chain["chain_id"],
                "mermaid_code": chain["mermaid_code"],
            })

    if render_entries:
        _render_chain_diagrams(render_entries, target_dir, template_dir)
        # Map rendered paths back to chains
        rendered_map = {e["id"]: e for e in render_entries}
        for chain in surfaced:
            entry = rendered_map.get(chain["chain_id"])
            if entry:
                chain["has_image"] = entry.get("has_image", False)
                chain["image_path"] = entry.get("image_path", "")
            else:
                chain["has_image"] = False
                chain["image_path"] = ""
    else:
        for chain in surfaced:
            chain["has_image"] = False
            chain["image_path"] = ""

    return True, chains


def compute_has_source_attribution(findings: list[dict]) -> bool:
    """Return True iff any finding has a non-empty source_attribution array.

    Gate predicate for the coverage-attestation section. False MUST omit the
    section entirely from the PDF to preserve byte-identity on non-attributed
    baselines (ADR-021 determinism convention).
    """
    for finding in findings or ():
        attribution = finding.get("source_attribution")
        if attribution is not None and len(attribution) > 0:
            return True
    return False


def _merge_source_attribution(findings: list, threats_content: str) -> None:
    """Merge source_attribution from threats.md Section 9 onto findings in-place.

    parse_threats_findings already attaches source_attribution at Tier 3. This
    helper bridges the gap at Tier 1 (findings from parse_compensating_controls_md)
    and Tier 2 (findings from parse_risk_scores_findings) — neither of those
    parsers reads Section 9, so attribution would otherwise be invisible to the
    F-B aggregator.
    """
    block = _extract_source_attribution_block(threats_content)
    if block is None:
        return
    for finding in findings:
        attribution = _extract_source_attribution(finding["id"], block)
        if attribution is not None:
            finding["source_attribution"] = attribution


def _merge_delta_status(findings: list, threats_content: str) -> None:
    """Merge delta_status from threats.md Section 7 onto findings in-place.

    parse_threats_findings already attaches delta_status at Tier 3 (reads the
    Status column of Section 7 Recommended Actions). Tier 1 (compensating
    controls) and Tier 2 (risk scores) parsers don't read threats.md, so
    delta annotations are otherwise invisible to compute_delta_counts — every
    finding would render without a NEW / UPDATED / UNCHANGED badge even when
    the threat model clearly declares a baseline diff.
    """
    rows = parse_markdown_table(threats_content, "## 7. Recommended Actions")
    if not rows:
        return
    status_by_id = {}
    for row in rows:
        fid = row.get("Finding ID", "").strip()
        status = row.get("Status", "").strip()
        if fid and status:
            status_by_id[fid] = status
    if not status_by_id:
        return
    for finding in findings:
        fid = finding.get("id", "")
        if fid in status_by_id:
            finding["delta_status"] = status_by_id[fid]


# Coverage attestation aggregator: joins source_attribution arrays on findings
# against schemas/taxonomy/ catalogs and emits per-finding rows + per-framework
# aggregates for the coverage-attestation Typst template.

SCHEMAS_TAXONOMY_DIR = Path(__file__).resolve().parent.parent / "schemas" / "taxonomy"

ORDERED_FRAMEWORKS = ("owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe")

MITRE_PREFIXES = {"mitre-attack": "ATT&CK:", "mitre-atlas": "ATLAS:"}

TAXONOMY_REF_GROUPS = (
    ("owasp_refs", ("owasp",)),
    ("mitre_refs", ("mitre-attack", "mitre-atlas")),
    ("nist_refs", ("nist-ai-rmf",)),
    ("cwe_refs", ("cwe",)),
)


@functools.lru_cache(maxsize=None)
def _load_framework_yaml_records(
    framework_name: str, in_scope_only: bool = False
) -> list:
    """Return top-level records from schemas/taxonomy/{framework_name}.yaml.

    Wraps yaml.safe_load with a fail-loud RuntimeError that names the offending
    framework + path. Empty YAML yields an empty list (zero-denominator case).

    yaml is imported lazily inside the function body so the module loads
    without pyyaml installed — required by the stdlib-only module-load
    invariant in sibling tachi_parsers (which uses regex `_load_catalog_ids`
    for the ids-only case). An ids-only caller should prefer
    `tachi_parsers._load_catalog_ids`; this helper returns full record
    dicts in YAML order, which is what the aggregator needs.

    Result is memoized via ``functools.lru_cache`` so repeated calls within
    the same process return the cached records without re-parsing the YAML
    file. The returned list is shared across callers — do not mutate it.
    Tests that need to bypass the cache (e.g. the YAMLError fail-loud test
    that patches ``yaml.safe_load``) must call
    ``_load_framework_yaml_records.cache_clear()`` explicitly.

    When ``in_scope_only=True``: records carrying ``out_of_scope: true`` are
    filtered out before return. Records that omit the ``out_of_scope`` key are
    treated as in-scope (default ``False`` per backward-compat). The filter is
    applied here at the lowest level so the in-scope-record-count semantic
    flows uniformly through every downstream aggregator code path.
    """
    import yaml

    path = SCHEMAS_TAXONOMY_DIR / f"{framework_name}.yaml"
    try:
        with path.open() as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise RuntimeError(
            f"Failed to load taxonomy YAML for framework {framework_name!r} "
            f"({path}): {exc}"
        ) from exc
    if data is None:
        return []
    records = list(data)
    if in_scope_only:
        records = [
            r for r in records
            if not (isinstance(r, dict) and r.get("out_of_scope", False))
        ]
    return records


def load_framework_yaml_record_counts() -> dict:
    """Return ``{framework_name: top_level_record_count}`` for the 5 external frameworks.

    Returns RAW counts (including ``out_of_scope: true`` records) for
    traceability. The Typst data contract emits this value as
    ``yaml-record-count`` so external auditors can inspect the full taxonomy
    inventory size against the in-scope-only denominator (emitted as
    ``in-scope-record-count``).

    Tests monkeypatch this function to inject zero-denominator scenarios
    without touching disk.
    """
    return {fw: len(_load_framework_yaml_records(fw)) for fw in ORDERED_FRAMEWORKS}


def load_framework_yaml_in_scope_record_counts() -> dict:
    """Return ``{framework_name: in_scope_record_count}`` for the 5 external frameworks.

    F-241 Stream 4 / FR-024: the coverage-percentage denominator filters out
    ``out_of_scope: true`` records so the aggregator measures real-world
    detectability rather than penalizing tachi for STIX taxonomy entries that
    the design-time threat-modeling layer cannot reach (runtime tactics,
    cloud account abuse, etc — see data-model.md §5 for tactic enumeration).

    Tests monkeypatch this function to inject zero-denominator scenarios
    (entirely-Out-of-Scope framework) without touching disk.
    """
    return {
        fw: len(_load_framework_yaml_records(fw, in_scope_only=True))
        for fw in ORDERED_FRAMEWORKS
    }


def classify_framework_items(
    findings: list, framework_name: str, framework_records: list
) -> list:
    """Classify each top-level YAML record into Covered / Partial / Gap.

    Rule:
      - Covered → ≥1 finding cites this id with relationship = primary
      - Partial → zero primary citations AND ≥1 related/derived citation
      - Gap → zero citations
    Order-preserving: emitted items mirror ``framework_records`` iteration order.
    """
    items = []
    for record in framework_records:
        record_id = record.get("id") if isinstance(record, dict) else None
        if record_id is None:
            continue
        relationships = set()
        for finding in findings or ():
            for ref in finding.get("source_attribution") or ():
                if ref.get("taxonomy") == framework_name and ref.get("id") == record_id:
                    relationships.add(ref.get("relationship", "primary"))
        if "primary" in relationships:
            classification = "covered"
        elif "related" in relationships or "derived" in relationships:
            classification = "partial"
        else:
            classification = "gap"
        items.append({"id": record_id, "classification": classification})
    return items


def _build_per_framework_aggregate(
    framework_name: str,
    items: list,
    yaml_record_count: int,
    in_scope_yaml_record_count: int,
) -> dict:
    """Combine classified items + denominators into a Per-Framework Aggregate Record.

    Partition invariant (post-F-241 Stream 4): ``covered_count + partial_count +
    gap_count == in_scope_yaml_record_count``. The ``items`` list is filtered
    to in-scope records only by the upstream caller (see
    ``build_per_framework_aggregates``), so the partition holds against the
    in-scope denominator. The raw ``yaml_record_count`` is preserved on the
    record for external-auditor traceability (data-model.md §3 / FR-024 /
    Architect M-2).

    Coverage percentage formatting:
      - "X.XX%" when in_scope_yaml_record_count > 0 (numerator = covered_count only)
      - "N/A"   when in_scope_yaml_record_count == 0 (entirely-Out-of-Scope edge case)
    Zero-numerator with non-zero denominator yields "0.00%" via normal arithmetic.
    """
    covered_count = sum(1 for it in items if it["classification"] == "covered")
    partial_count = sum(1 for it in items if it["classification"] == "partial")
    gap_count = sum(1 for it in items if it["classification"] == "gap")
    if in_scope_yaml_record_count == 0:
        coverage_percentage = "N/A"
    else:
        coverage_percentage = (
            f"{(covered_count / in_scope_yaml_record_count) * 100:.2f}%"
        )
    return {
        "framework": framework_name,
        "yaml_record_count": yaml_record_count,
        "in_scope_yaml_record_count": in_scope_yaml_record_count,
        "covered_count": covered_count,
        "partial_count": partial_count,
        "gap_count": gap_count,
        "coverage_percentage": coverage_percentage,
        "items": items,
    }


def build_per_framework_aggregates(findings: list) -> list:
    """Emit exactly 5 Per-Framework Aggregate Records in fixed framework order.

    Order: owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe.
    Calls ``load_framework_yaml_record_counts`` for the raw denominator
    (preserved as ``yaml_record_count`` for external-auditor traceability) and
    ``load_framework_yaml_in_scope_record_counts`` for the in-scope-only
    denominator (used as the coverage-percentage divisor per FR-024 /
    Architect M-2). Classification iterates the in-scope-only record set so
    the partition invariant holds against ``in_scope_yaml_record_count``.

    Per F-241 T046 edge case: findings citing Out-of-Scope items still render
    on the per-finding attribution table (built separately in
    ``build_per_finding_rows`` from ``finding.source_attribution``) but those
    OOS records do NOT appear in the per-framework matrix items list and do
    NOT increment ``covered_count``.
    """
    raw_counts = load_framework_yaml_record_counts()
    in_scope_counts = load_framework_yaml_in_scope_record_counts()
    aggregates = []
    for framework_name in ORDERED_FRAMEWORKS:
        yaml_record_count = raw_counts.get(framework_name, 0)
        in_scope_count = in_scope_counts.get(framework_name, 0)
        if in_scope_count == 0:
            items = []
        else:
            records = _load_framework_yaml_records(
                framework_name, in_scope_only=True
            )
            items = classify_framework_items(findings, framework_name, records)
        aggregates.append(
            _build_per_framework_aggregate(
                framework_name,
                items,
                yaml_record_count,
                in_scope_count,
            )
        )
    return aggregates


def build_per_finding_rows(findings: list) -> list:
    """Emit one Per-Finding Attribution Row per finding, preserving input order.

    Every finding produces one row, including findings without attribution
    (4 ref arrays present as empty lists). The MITRE column merges
    ``mitre-attack`` + ``mitre-atlas`` with per-ref prefix ``ATT&CK:`` /
    ``ATLAS:`` to disambiguate; the merge applies to the per-finding column
    only, NOT to per-framework matrix pages.
    """
    rows = []
    for finding in findings or ():
        ref_buckets = {key: [] for key, _ in TAXONOMY_REF_GROUPS}
        for ref in finding.get("source_attribution") or ():
            taxonomy = ref.get("taxonomy")
            ref_id = ref.get("id", "")
            relationship = ref.get("relationship", "primary")
            for bucket_key, taxonomies in TAXONOMY_REF_GROUPS:
                if taxonomy in taxonomies:
                    if taxonomy in MITRE_PREFIXES:
                        display_id = f"{MITRE_PREFIXES[taxonomy]}{ref_id}"
                    else:
                        display_id = ref_id
                    ref_buckets[bucket_key].append(
                        {"id": display_id, "relationship": relationship}
                    )
                    break
        severity = finding.get("severity") or finding.get("risk_level", "")
        rows.append({
            "id": finding.get("id", ""),
            "title": finding.get("title") or finding.get("threat", ""),
            "severity": str(severity).lower(),
            "owasp_refs": ref_buckets["owasp_refs"],
            "mitre_refs": ref_buckets["mitre_refs"],
            "nist_refs": ref_buckets["nist_refs"],
            "cwe_refs": ref_buckets["cwe_refs"],
        })
    return rows


def _render_chain_diagrams(entries: list, target_dir: Path, template_dir: Path):
    """Render chain Mermaid diagrams to PNG, following render_mermaid_to_png pattern.

    Writes PNGs to {target_dir}/attack-chains/ directory.
    """
    if not entries:
        return

    if not shutil.which("mmdc"):
        raise RuntimeError(
            "Attack chain rendering requires @mermaid-js/mermaid-cli (mmdc).\n"
            "Install with: npm install -g @mermaid-js/mermaid-cli\n"
            "Then re-run /tachi.security-report."
        )

    try:
        rel_target = os.path.relpath(str(target_dir), str(template_dir))
    except ValueError:
        rel_target = str(target_dir)

    chains_dir = target_dir / "attack-chains"
    chains_dir.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [
                pool.submit(_render_chain_single, entry, tmp_path, chains_dir, rel_target)
                for entry in entries
            ]
            failures = []
            for future in concurrent.futures.as_completed(futures):
                entry, success, value = future.result()
                if success:
                    entry["has_image"] = True
                    entry["image_path"] = value
                else:
                    entry["has_image"] = False
                    entry["image_path"] = ""
                    if isinstance(value, dict):
                        failures.append(value)

            if failures:
                lines = [f"Attack chain rendering failed for {len(failures)} chains:"]
                for rec in failures:
                    lines.append(f"  - {rec['id']} ({rec['file_path']})")
                    lines.append(f"    failure: {rec['failure_class']}")
                    lines.append(f"    stderr: {rec['stderr_excerpt']}")
                raise RuntimeError("\n".join(lines))


def _render_chain_single(entry, tmp_path, chains_dir, rel_target):
    """Render one chain Mermaid diagram to PNG. Returns (entry, success, value)."""
    cid = entry["id"]
    cid_lower = cid.lower()
    mermaid_code = entry.get("mermaid_code", "")
    if not mermaid_code:
        return (entry, False, "")

    mmd_file = tmp_path / f"{cid_lower}.mmd"
    png_file = tmp_path / f"{cid_lower}.png"
    mmd_file.write_text(mermaid_code, encoding="utf-8")

    try:
        subprocess.run(
            ["mmdc", "-i", str(mmd_file), "-o", str(png_file), "-s", "2", "-b", "transparent"],
            capture_output=True,
            timeout=30,
            check=True,
        )
        dest_png = chains_dir / f"{cid_lower}-attack-chain.png"
        shutil.copy2(str(png_file), str(dest_png))
        return (entry, True, rel_target + "/attack-chains/" + f"{cid_lower}-attack-chain.png")
    except subprocess.CalledProcessError as e:
        failure_class = "signal" if e.returncode < 0 else f"exit:{e.returncode}"
        return (entry, False, _build_error_record(cid, failure_class, e.stderr, subdir="attack-chains"))
    except subprocess.TimeoutExpired as e:
        return (entry, False, _build_error_record(cid, "timeout", e.stderr, subdir="attack-chains"))


# =============================================================================
# Validation
# =============================================================================

def validate(data: dict) -> list:
    """Validate internal consistency of extracted data.

    Returns list of error messages. Empty list means valid.
    """
    errors = []
    sev = data["severity"]

    # Check severity sum: critical + high + medium + low == total - note
    expected = sev["critical"] + sev["high"] + sev["medium"] + sev["low"]
    actual = sev["total"] - sev["note"]
    if expected != actual:
        errors.append(
            f"Severity sum mismatch: critical({sev['critical']}) + high({sev['high']}) + "
            f"medium({sev['medium']}) + low({sev['low']}) = {expected}, "
            f"but total({sev['total']}) - note({sev['note']}) = {actual}"
        )

    # Check finding ID uniqueness
    ids = [f["id"] for f in data["findings"]]
    seen = set()
    for fid in ids:
        if fid in seen:
            errors.append(f"Duplicate finding ID: {fid}")
        seen.add(fid)

    # Scope counts are derived from len() at generation time, so they are
    # self-consistent by construction. No separate validation needed.

    return errors


# =============================================================================
# Image and Brand Asset Detection
# =============================================================================

_IMAGE_FORMAT_TO_EXT = {"jpeg": ".jpg", "png": ".png"}


def _file_format(path: Path) -> "str | None":
    """Return 'png', 'jpeg', or None based on magic bytes."""
    try:
        with path.open("rb") as f:
            head = f.read(8)
    except OSError:
        return None
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    return None


def detect_images(target_dir: Path, template_dir: Path) -> dict:
    """Compute image paths relative to template directory.

    The infographic agent writes images whose extension is supposed to match
    the Gemini MIME type, but the `gemini-2.5-flash-image` fallback model has
    historically returned PNG bytes saved into `.jpg` files. Typst's decoder
    rejects bytes that don't match the filename. Probe each candidate's magic
    bytes (not just its extension) and pick the path whose filename matches
    its content. If only a mislabeled candidate exists, write a corrected
    sibling and emit that path so Typst compiles on the first attempt.
    """
    try:
        rel_target = os.path.relpath(str(target_dir), str(template_dir))
    except ValueError:
        rel_target = str(target_dir)

    images = {
        "funnel_image_path": "",
        "baseball_image_path": "",
        "architecture_image_path": "",
        "maestro_stack_image_path": "",
        "maestro_heatmap_image_path": "",
        "executive_architecture_image_path": "",
    }

    image_stems = {
        "funnel_image_path": "threat-risk-funnel",
        "baseball_image_path": "threat-baseball-card",
        "architecture_image_path": "threat-system-architecture",
        "maestro_stack_image_path": "threat-maestro-stack",
        "maestro_heatmap_image_path": "threat-maestro-heatmap",
        "executive_architecture_image_path": "threat-executive-architecture",
    }

    for key, stem in image_stems.items():
        candidates = []
        for ext in (".jpg", ".png"):
            fp = target_dir / f"{stem}{ext}"
            if fp.exists() and fp.stat().st_size > 0:
                candidates.append((ext, fp))
        if not candidates:
            continue

        chosen = None
        for ext, fp in candidates:
            if _IMAGE_FORMAT_TO_EXT.get(_file_format(fp)) == ext:
                chosen = fp
                break

        if chosen is None:
            for ext, fp in candidates:
                fmt = _file_format(fp)
                if fmt is None:
                    continue
                target_path = target_dir / f"{stem}{_IMAGE_FORMAT_TO_EXT[fmt]}"
                print(
                    f"Image format mismatch: {fp.name} contains {fmt.upper()} bytes; "
                    f"writing corrected sibling {target_path.name}",
                    file=sys.stderr,
                )
                shutil.copyfile(fp, target_path)
                chosen = target_path
                break

        if chosen is not None:
            images[key] = rel_target + "/" + chosen.name

    return images


def detect_brand_assets(template_dir: Path) -> dict:
    """Check for brand logo files and compute relative paths."""
    brand_dir = Path("brand/final")
    result = {
        "has_logo_primary": False,
        "has_logo_horizontal": False,
        "logo_primary_path": None,
        "logo_primary_dark_path": None,
        "logo_horizontal_path": None,
    }

    try:
        rel_brand = os.path.relpath(str(brand_dir), str(template_dir))
    except ValueError:
        rel_brand = str(brand_dir)

    logo_files = {
        "logo_primary_path": "tachi-logo-primary.png",
        "logo_primary_dark_path": "tachi-logo-primary-dark.png",
        "logo_horizontal_path": "tachi-logo-horizontal.png",
    }

    for key, filename in logo_files.items():
        filepath = brand_dir / filename
        if filepath.exists() and filepath.stat().st_size > 0:
            result[key] = rel_brand + "/" + filename

    if result["logo_primary_path"]:
        result["has_logo_primary"] = True
    if result["logo_horizontal_path"]:
        result["has_logo_horizontal"] = True

    return result


# =============================================================================
# Typst Output Generation
# =============================================================================

def generate_report_data_typ(data: dict) -> str:
    """Generate complete report-data.typ content from parsed data."""
    lines = []

    # 3a: Header
    lines.append("// =============================================================================")
    lines.append("// Report Data: Auto-generated by tachi extract-report-data.py")
    lines.append("// =============================================================================")
    lines.append("// This file is generated at runtime and imported by main.typ.")
    lines.append("// Do NOT edit manually — it will be overwritten on next generation.")
    lines.append("// =============================================================================")
    lines.append("")

    # 3b: Metadata
    lines.append("// --- Metadata ----------------------------------------------------------------")
    lines.append(f'#let project-name = "{escape_typst_string(data["project_name"])}"')
    lines.append(f'#let assessment-date = "{escape_typst_string(data["assessment_date"])}"')
    if data["classification"]:
        lines.append(f'#let classification = "{escape_typst_string(data["classification"])}"')
    else:
        lines.append("#let classification = none")
    lines.append("")

    # 3c: Severity Counts
    sev = data["severity"]
    lines.append("// --- Severity Counts ---------------------------------------------------------")
    lines.append(f"#let critical-count = {sev['critical']}")
    lines.append(f"#let high-count = {sev['high']}")
    lines.append(f"#let medium-count = {sev['medium']}")
    lines.append(f"#let low-count = {sev['low']}")
    lines.append(f"#let note-count = {sev['note']}")
    lines.append(f"#let total-findings = {sev['total']}")
    lines.append("")

    # 3c2: Baseline / Delta Data
    lines.append("// --- Baseline / Delta Data ---------------------------------------------------")
    lines.append(f"#let has-baseline = {_typst_bool(data.get('has_baseline', False))}")
    lines.append(f'#let baseline-source = "{escape_typst_string(data.get("baseline_source", ""))}"')
    lines.append(f'#let baseline-date = "{escape_typst_string(data.get("baseline_date", ""))}"')
    lines.append(f'#let baseline-finding-count = {data.get("baseline_finding_count", "0")}')
    lines.append(f'#let baseline-run-id = "{escape_typst_string(data.get("baseline_run_id", ""))}"')
    dc = data.get("delta_counts", {"new": 0, "unchanged": 0, "updated": 0, "resolved": 0})
    lines.append(f"#let delta-new-count = {dc['new']}")
    lines.append(f"#let delta-unchanged-count = {dc['unchanged']}")
    lines.append(f"#let delta-updated-count = {dc['updated']}")
    lines.append(f"#let delta-resolved-count = {dc['resolved']}")
    # Resolved findings list
    resolved = data.get("resolved_findings", [])
    if resolved:
        lines.append("#let resolved-findings = (")
        for rf in resolved:
            lines.append(
                f'  (id: "{escape_typst_string(rf["id"])}", '
                f'component: "{escape_typst_string(rf["component"])}", '
                f'threat: "{escape_typst_string(rf["threat"])}", '
                f'risk-level: "{escape_typst_string(rf["risk_level"])}", '
                f'resolution-reason: "{escape_typst_string(rf["resolution_reason"])}"),')
        lines.append(")")
    else:
        lines.append("#let resolved-findings = ()")
    lines.append("")

    # 3d: Page Inclusion Flags
    art = data["artifacts"]
    lines.append("// --- Page Inclusion Flags ----------------------------------------------------")
    lines.append(f"#let has-threat-report = {_typst_bool(art['threat_report_md'])}")
    lines.append(f"#let has-risk-scores = {_typst_bool(art['risk_scores_md'])}")
    lines.append(f"#let has-compensating-controls = {_typst_bool(art['compensating_controls_md'])}")
    lines.append(f"#let has-funnel-image = {_typst_bool(art['funnel_image'])}")
    lines.append(f"#let has-baseball-image = {_typst_bool(art['baseball_image'])}")
    lines.append(f"#let has-architecture-image = {_typst_bool(art['architecture_image'])}")
    lines.append("")

    # 3e: Data Source Tier
    lines.append("// --- Data Source Tier ---------------------------------------------------------")
    lines.append(f"#let data-source-tier = {data['tier']}")
    lines.append("")

    # 3f: Image Paths
    lines.append("// --- Image Paths (relative to templates/tachi/security-report/) --------------------")
    lines.append(f'#let funnel-image-path = "{escape_typst_string(data["funnel_image_path"])}"')
    lines.append(f'#let baseball-image-path = "{escape_typst_string(data["baseball_image_path"])}"')
    lines.append(f'#let architecture-image-path = "{escape_typst_string(data["architecture_image_path"])}"')
    lines.append(f"#let has-executive-architecture = {_typst_bool(bool(data.get('executive_architecture_image_path', '')))}")
    lines.append(f'#let executive-architecture-image-path = "{escape_typst_string(data.get("executive_architecture_image_path", ""))}"')
    lines.append("")

    # 3g: Executive Narrative
    lines.append("// --- Executive Narrative -----------------------------------------------------")
    if data["executive_narrative"]:
        lines.append(f'#let executive-narrative = "{escape_typst_string(data["executive_narrative"])}"')
    else:
        lines.append("#let executive-narrative = none")
    lines.append("")

    # 3h: Component Distribution
    lines.append("// --- Component Distribution --------------------------------------------------")
    if data["component_distribution"]:
        lines.append("#let component-distribution = (")
        for name, count in data["component_distribution"]:
            lines.append(f'  ("{escape_typst_string(name)}", {count}),')
        lines.append(")")
    else:
        lines.append("#let component-distribution = none")
    lines.append("")

    # 3i: Findings Array
    tier = data["tier"]
    lines.append(f"// --- Findings (Tier {tier}) -----------------------------------------------------")
    findings = data["findings"]
    if findings:
        lines.append("#let findings = (")
        for f in findings:
            lines.append(f"  ({_format_finding(f, tier)}),")
        lines.append(")")
    else:
        lines.append("#let findings = ()")
    lines.append("")

    # 3j: Coverage Matrix
    lines.append("// --- Coverage Matrix ---------------------------------------------------------")
    if data["coverage_matrix"]:
        lines.append("#let coverage-matrix = (")
        for entry in data["coverage_matrix"]:
            lines.append(f'  (category: "{escape_typst_string(entry["category"])}", found: {entry["found"]}, partial: {entry["partial"]}, missing: {entry["missing"]}),')
        lines.append(")")
    else:
        lines.append("#let coverage-matrix = ()")
    lines.append("")

    # 3k: Controls
    lines.append("// --- Detailed Controls -------------------------------------------------------")
    if data["controls"]:
        lines.append("#let controls = (")
        for c in data["controls"]:
            lines.append(f'  (component: "{escape_typst_string(c["component"])}", category: "{escape_typst_string(c["category"])}", status: "{escape_typst_string(c["status"])}", evidence: "{escape_typst_string(c["evidence"])}", effectiveness: "{escape_typst_string(c["effectiveness"])}"),')
        lines.append(")")
    else:
        lines.append("#let controls = ()")
    lines.append("")

    # 3l: Coverage Summary
    cs = data["coverage_summary"]
    lines.append("// --- Coverage Summary --------------------------------------------------------")
    lines.append("#let coverage-summary = (")
    lines.append(f"  total-found: {cs['total-found']},")
    lines.append(f"  total-partial: {cs['total-partial']},")
    lines.append(f"  total-missing: {cs['total-missing']},")
    lines.append(")")
    lines.append("")

    # 3m: Remediation Actions
    lines.append("// --- Remediation Actions -----------------------------------------------------")
    if data["remediation_actions"]:
        lines.append("#let remediation-actions = (")
        for r in data["remediation_actions"]:
            lines.append(f'  (severity: "{escape_typst_string(r["severity"])}", finding-id: "{escape_typst_string(r["finding-id"])}", finding-name: "{escape_typst_string(r["finding-name"])}", recommendation: "{escape_typst_string(r["recommendation"])}", sla: "{escape_typst_string(r["sla"])}", status: "{escape_typst_string(r["status"])}"),')
        lines.append(")")
    else:
        lines.append("#let remediation-actions = none")
    lines.append("")

    # 3n: Scope Data
    lines.append("// --- Scope Data (from threats.md Sections 1-2) ------------------------------")
    _append_scope_array(lines, "scope-components", data["scope_components"],
                        ["name", "type", "description"])
    lines.append("")
    _append_scope_array(lines, "scope-data-flows", data["scope_data_flows"],
                        ["source", "destination", "data", "protocol"])
    lines.append("")
    _append_scope_array(lines, "scope-trust-boundaries", data["scope_trust_boundaries"],
                        ["zone", "trust-level", "components"])
    lines.append("")
    _append_scope_array(lines, "scope-boundary-crossings", data["scope_boundary_crossings"],
                        ["crossing", "from-zone", "to-zone", "components", "controls"])
    lines.append("")
    lines.append(f"#let scope-component-count = {len(data['scope_components'])}")
    lines.append(f"#let scope-data-flow-count = {len(data['scope_data_flows'])}")
    lines.append(f"#let scope-trust-boundary-count = {len(data['scope_trust_boundaries'])}")
    lines.append("")

    # 3o: Brand Assets
    lines.append("// --- Brand Assets -----------------------------------------------------------")
    lines.append(f"#let has-logo-primary = {_typst_bool(data['has_logo_primary'])}")
    lines.append(f"#let has-logo-horizontal = {_typst_bool(data['has_logo_horizontal'])}")
    lines.append(f"#let logo-primary-path = {_typst_str_or_none(data['logo_primary_path'])}")
    lines.append(f"#let logo-primary-dark-path = {_typst_str_or_none(data['logo_primary_dark_path'])}")
    lines.append(f"#let logo-horizontal-path = {_typst_str_or_none(data['logo_horizontal_path'])}")
    lines.append("")

    # 3p: MAESTRO Data
    lines.append("// --- MAESTRO Data -----------------------------------------------------------")
    lines.append(f"#let has-maestro-data = {_typst_bool(data.get('has_maestro_data', False))}")
    if data.get("maestro_layer_distribution"):
        lines.append("#let maestro-layer-distribution = (")
        for layer in data["maestro_layer_distribution"]:
            lines.append(
                f'  (layer-id: "{escape_typst_string(layer["layer_id"])}", '
                f'layer-name: "{escape_typst_string(layer["layer_name"])}", '
                f'finding-count: {layer["finding_count"]}, '
                f'highest-severity: "{escape_typst_string(layer["highest_severity"])}"),')
        lines.append(")")
    else:
        lines.append("#let maestro-layer-distribution = ()")
    lines.append(f'#let most-exposed-layer = "{escape_typst_string(data.get("most_exposed_layer", ""))}"')
    if data.get("maestro_findings_by_layer"):
        lines.append("#let maestro-findings-by-layer = (")
        for group in data["maestro_findings_by_layer"]:
            lines.append(
                f'  (layer-id: "{escape_typst_string(group["layer_id"])}", '
                f'layer-name: "{escape_typst_string(group["layer_name"])}", '
                f'findings: (')
            for f in group["findings"]:
                lines.append(
                    f'    (id: "{escape_typst_string(f["id"])}", '
                    f'component: "{escape_typst_string(f["component"])}", '
                    f'severity: "{escape_typst_string(f["severity"])}", '
                    f'threat: "{escape_typst_string(f["threat"])}"),')
            lines.append("  )),")
        lines.append(")")
    else:
        lines.append("#let maestro-findings-by-layer = ()")
    lines.append(f"#let has-maestro-stack-image = {_typst_bool(bool(data.get('maestro_stack_image_path', '')))}")
    lines.append(f'#let maestro-stack-image-path = "{escape_typst_string(data.get("maestro_stack_image_path", ""))}"')
    lines.append(f"#let has-maestro-heatmap-image = {_typst_bool(bool(data.get('maestro_heatmap_image_path', '')))}")
    lines.append(f'#let maestro-heatmap-image-path = "{escape_typst_string(data.get("maestro_heatmap_image_path", ""))}"')
    lines.append("")

    # 3q: Attack Tree Data
    lines.append("// --- Attack Tree Data --------------------------------------------------------")
    lines.append(f"#let has-attack-trees = {_typst_bool(data.get('has_attack_trees', False))}")
    attack_trees = data.get("attack_trees", [])
    if attack_trees:
        lines.append("#let attack-trees = (")
        for at in attack_trees:
            remediation_items = at.get("remediation", [])
            rem_typst = ", ".join(f'"{escape_typst_string(r)}"' for r in remediation_items)
            if rem_typst:
                rem_typst += ","
            lines.append(
                f'  (id: "{escape_typst_string(at["id"])}", '
                f'component: "{escape_typst_string(at.get("component", ""))}", '
                f'severity: "{escape_typst_string(at.get("severity", ""))}", '
                f'title: "{escape_typst_string(at.get("title", ""))}", '
                f'image-path: "{escape_typst_string(at.get("image_path", ""))}", '
                f'has-image: {_typst_bool(at.get("has_image", False))}, '
                f'mermaid-text: "{escape_typst_string(at.get("mermaid_code", ""))}", '
                f'narrative: "{escape_typst_string(at.get("narrative", ""))}", '
                f'remediation: ({rem_typst})),')
        lines.append(")")
    else:
        lines.append("#let attack-trees = ()")
    lines.append("")

    # 3r: Attack Chain Data
    lines.append("// --- Attack Chain Data -------------------------------------------------------")
    lines.append(f"#let has-attack-chains = {_typst_bool(data.get('has_attack_chains', False))}")
    attack_chains = data.get("attack_chains", [])
    surfaced_chains = [c for c in attack_chains if c.get("surfaced", False)]
    if surfaced_chains:
        lines.append("#let attack-chains = (")
        for chain in surfaced_chains:
            chain_id = escape_typst_string(chain.get("chain_id", ""))
            title = escape_typst_string(chain.get("title", ""))
            layers = chain.get("layers", [])
            layers_str = " → ".join(layers)
            max_sev = escape_typst_string(chain.get("max_severity", ""))
            narrative = escape_typst_string(chain.get("narrative", ""))
            has_img = _typst_bool(chain.get("has_image", False))
            img_path = escape_typst_string(chain.get("image_path", ""))
            # Collect finding IDs
            finding_ids = [f.get("finding_id", "") for f in chain.get("findings", [])]
            finding_ids_typst = ", ".join(f'"{escape_typst_string(fid)}"' for fid in finding_ids if fid)
            if finding_ids_typst:
                finding_ids_typst += ","
            lines.append(
                f'  (id: "{chain_id}", '
                f'title: "{title}", '
                f'layers: "{escape_typst_string(layers_str)}", '
                f'max-severity: "{max_sev}", '
                f'has-image: {has_img}, '
                f'image-path: "{img_path}", '
                f'narrative: "{narrative}", '
                f'finding-ids: ({finding_ids_typst})),')
        lines.append(")")
    else:
        lines.append("#let attack-chains = ()")
    lines.append("")

    # 3t: Coverage Attestation Data
    # Always emitted so main.typ default-value guards have something to bind;
    # empty arrays when the gate is false, populated otherwise.
    lines.append("// --- Coverage Attestation Data ----------------------------------------------")
    lines.append(
        f"#let has-source-attribution = {_typst_bool(data.get('has_source_attribution', False))}"
    )
    per_finding_rows = data.get("per_finding_rows", [])
    if per_finding_rows:
        lines.append("#let per-finding-rows = (")
        for row in per_finding_rows:
            row_id = escape_typst_string(row.get("id", ""))
            title = escape_typst_string(row.get("title", ""))
            severity = escape_typst_string(row.get("severity", ""))
            ref_parts = []
            for ref_key, hyphen_key in (
                ("owasp_refs", "owasp-refs"),
                ("mitre_refs", "mitre-refs"),
                ("nist_refs", "nist-refs"),
                ("cwe_refs", "cwe-refs"),
            ):
                refs = row.get(ref_key, []) or ()
                if refs:
                    inner = ", ".join(
                        f'(id: "{escape_typst_string(r["id"])}", '
                        f'relationship: "{escape_typst_string(r["relationship"])}")'
                        for r in refs
                    )
                    ref_parts.append(f"{hyphen_key}: ({inner},)")
                else:
                    ref_parts.append(f"{hyphen_key}: ()")
            lines.append(
                f'  (id: "{row_id}", title: "{title}", severity: "{severity}", '
                f'{", ".join(ref_parts)}),'
            )
        lines.append(")")
    else:
        lines.append("#let per-finding-rows = ()")
    per_framework_aggregates = data.get("per_framework_aggregates", [])
    if per_framework_aggregates:
        lines.append("#let per-framework-aggregates = (")
        for agg in per_framework_aggregates:
            framework = escape_typst_string(agg.get("framework", ""))
            yaml_count = int(agg.get("yaml_record_count", 0))
            in_scope_count = int(
                agg.get("in_scope_yaml_record_count", yaml_count)
            )
            covered = int(agg.get("covered_count", 0))
            partial = int(agg.get("partial_count", 0))
            gap = int(agg.get("gap_count", 0))
            pct = escape_typst_string(agg.get("coverage_percentage", "N/A"))
            items = agg.get("items", []) or ()
            if items:
                items_inner = ", ".join(
                    f'(id: "{escape_typst_string(it["id"])}", '
                    f'classification: "{escape_typst_string(it["classification"])}")'
                    for it in items
                )
                items_typst = f"({items_inner},)"
            else:
                items_typst = "()"
            lines.append(
                f'  (framework: "{framework}", yaml-record-count: {yaml_count}, '
                f'in-scope-record-count: {in_scope_count}, '
                f'covered-count: {covered}, partial-count: {partial}, '
                f'gap-count: {gap}, coverage-percentage: "{pct}", '
                f'items: {items_typst}),'
            )
        lines.append(")")
    else:
        lines.append("#let per-framework-aggregates = ()")
    lines.append("")

    # 3u: Page Visibility
    lines.append("// --- Page Visibility (defaults, overridden by report-config.typ) ------------")
    lines.append("#let show-disclaimer = true")
    lines.append("#let show-methodology = true")
    lines.append("")

    return "\n".join(lines)


def _typst_bool(value: bool) -> str:
    return "true" if value else "false"


def _typst_str_or_none(value) -> str:
    if value is None:
        return "none"
    return f'"{escape_typst_string(str(value))}"'


def _format_finding(f: dict, tier: int) -> str:
    """Format a single finding dict as a Typst dictionary literal."""
    esc = escape_typst_string

    def _v(key, default=""):
        return esc(f.get(key, default))

    if tier == 1:
        base = (
            'id: "' + _v("id") + '", '
            'component: "' + _v("component") + '", '
            'threat: "' + _v("threat") + '", '
            'residual_score: "' + _v("residual_score") + '", '
            'residual_severity: "' + _v("residual_severity") + '", '
            'control_status: "' + _v("control_status") + '", '
            'recommendation: "' + _v("recommendation") + '"'
        )
    elif tier == 2:
        base = (
            'id: "' + _v("id") + '", '
            'component: "' + _v("component") + '", '
            'threat: "' + _v("threat") + '", '
            'composite_score: "' + _v("composite_score") + '", '
            'severity: "' + _v("severity") + '", '
            'cvss: "' + _v("cvss") + '", '
            'exploitability: "' + _v("exploitability") + '"'
        )
    else:  # tier == 3
        em_dash = "\u2014"
        base = (
            'id: "' + _v("id") + '", '
            'component: "' + _v("component") + '", '
            'threat: "' + _v("threat") + '", '
            'likelihood: "' + _v("likelihood", em_dash) + '", '
            'impact: "' + _v("impact", em_dash) + '", '
            'risk_level: "' + _v("risk_level") + '", '
            'mitigation: "' + _v("mitigation") + '"'
        )
    # Include delta_status when present (backward compatible across tiers). For
    # Tier 1/2 this field is populated by _merge_delta_status reading threats.md
    # Section 7; for Tier 3 it comes from parse_threats_findings directly.
    ds = f.get("delta_status", "")
    if ds:
        base += ', delta_status: "' + esc(ds) + '"'
    return base


def _append_scope_array(lines: list, var_name: str, items: list, keys: list):
    """Append a Typst array of dicts for scope data."""
    if items:
        lines.append(f"#let {var_name} = (")
        for item in items:
            parts = ", ".join(
                f'{k}: "{escape_typst_string(str(item.get(k, "")))}"' for k in keys
            )
            lines.append(f"  ({parts}),")
        lines.append(")")
    else:
        lines.append(f"#let {var_name} = ()")


# =============================================================================
# CLI Entry Point
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract structured data from tachi pipeline artifacts into a Typst data file."
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        help="Directory containing tachi pipeline artifacts (threats.md, etc.)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the generated report-data.typ file",
    )
    parser.add_argument(
        "--template-dir",
        required=True,
        help="Path to templates/tachi/security-report/ directory",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Title override for the report project name",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    output_path = Path(args.output)
    template_dir = Path(args.template_dir)

    # Artifact detection
    artifacts = detect_artifacts(target_dir)

    if not artifacts["threats_md"]:
        print(f"Error: threats.md not found in {target_dir}", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACT)

    # Tier selection
    tier = determine_tier(artifacts)
    print(f"Tier {tier} selected, parsing artifacts...", file=sys.stderr)

    # Read threats.md (always required)
    threats_content = (target_dir / "threats.md").read_text(encoding="utf-8")

    # Parse frontmatter
    frontmatter = parse_frontmatter(threats_content)

    # Parse project name
    project_name = parse_project_name(threats_content, args.title, target_dir)

    # Parse baseline metadata for delta-aware output
    baseline = parse_baseline_frontmatter(threats_content)
    has_baseline = baseline["has_baseline"]

    # Parse resolved findings from Section 4b (empty when no baseline)
    resolved_findings = parse_resolved_findings(threats_content)

    # Schema version check
    if frontmatter["schema_version"] == "1.0":
        print("Info: Schema v1.0 detected — correlated findings omitted", file=sys.stderr)

    # Initialize data dict that accumulates all parsed data
    data = {
        "project_name": project_name,
        "assessment_date": frontmatter["date"],
        "classification": frontmatter["classification"],
        "tier": tier,
        "artifacts": artifacts,
        "target_dir": str(target_dir),
        "template_dir": str(template_dir),
    }

    # Defaults for non-Tier-1 scenarios (Tier 1 overwrites these)
    data["coverage_matrix"] = []
    data["controls"] = []
    data["coverage_summary"] = {"total-found": 0, "total-partial": 0, "total-missing": 0}

    # Parse severity counts and findings based on tier
    cc_data = None
    if tier == 1:
        cc_content = (target_dir / "compensating-controls.md").read_text(encoding="utf-8")
        cc_data = parse_compensating_controls_md(cc_content)
        data["severity"] = cc_data["severity"]
        data["findings"] = cc_data["findings"]
        data["coverage_matrix"] = cc_data["coverage_matrix"]
        data["controls"] = cc_data["controls"]
        data["coverage_summary"] = cc_data["coverage_summary"]
    elif tier == 2:
        rs_content = (target_dir / "risk-scores.md").read_text(encoding="utf-8")
        data["severity"] = parse_risk_scores_severity(rs_content)
        data["findings"] = parse_risk_scores_findings(rs_content)
    else:  # tier == 3
        data["findings"] = parse_threats_findings(threats_content)
        # Derive severity counts from findings array for consistency.
        # Section 6 Risk Summary uses deduplication (correlation groups) which
        # causes counts to diverge from the raw findings in Section 7.
        sev = _empty_severity()
        for f in data["findings"]:
            key = f.get("risk_level", "").lower()
            if key in sev:
                sev[key] += 1
        sev["total"] = len(data["findings"])
        data["severity"] = sev

    # parse_threats_findings attaches source_attribution + delta_status at Tier 3,
    # but cc/rs parsers don't read threats.md. Without these merges, F-B's gate
    # stays false (silently omitting coverage-attestation) and compute_delta_counts
    # returns zeros (silently suppressing NEW / UPDATED badges) on every real
    # pipeline run that has cc.md or rs.md.
    if tier in (1, 2):
        _merge_source_attribution(data["findings"], threats_content)
        _merge_delta_status(data["findings"], threats_content)

    # Component distribution (from whichever findings source is active)
    data["component_distribution"] = parse_component_distribution(data["findings"])

    # Scope data from threats.md Sections 1-2
    scope = parse_scope_data(threats_content)
    data["scope_components"] = scope["components"]
    data["scope_data_flows"] = scope["data_flows"]
    data["scope_trust_boundaries"] = scope["trust_boundaries"]
    data["scope_boundary_crossings"] = scope["boundary_crossings"]

    # Executive narrative from threat-report.md
    tr_data = None
    tr_content = None
    if artifacts["threat_report_md"]:
        tr_content = (target_dir / "threat-report.md").read_text(encoding="utf-8")
        tr_data = parse_threat_report_md(tr_content)
        data["executive_narrative"] = tr_data["executive_narrative"]
    else:
        data["executive_narrative"] = None

    # Remediation actions with source priority (T023)
    data["remediation_actions"] = build_remediation_actions(
        data["findings"], tier, cc_data, tr_data
    )

    # Image paths (relative from template dir to target dir)
    images = detect_images(target_dir, template_dir)
    data["funnel_image_path"] = images["funnel_image_path"]
    data["baseball_image_path"] = images["baseball_image_path"]
    data["architecture_image_path"] = images["architecture_image_path"]
    data["maestro_stack_image_path"] = images["maestro_stack_image_path"]
    data["maestro_heatmap_image_path"] = images["maestro_heatmap_image_path"]
    data["executive_architecture_image_path"] = images["executive_architecture_image_path"]

    # MAESTRO data from threats.md
    maestro = parse_maestro_data(threats_content)
    data["has_maestro_data"] = maestro["has_maestro_data"]
    data["maestro_layer_distribution"] = maestro["maestro_layer_distribution"]
    data["most_exposed_layer"] = maestro["most_exposed_layer"]
    data["maestro_findings_by_layer"] = maestro["maestro_findings_by_layer"]

    # Attack tree data — try standalone files first, fall back to inline in threat-report.md
    if artifacts.get("has_attack_trees") or artifacts.get("threat_report_md"):
        attack_trees = parse_attack_trees(target_dir, data["findings"], tr_content=tr_content)
        render_mermaid_to_png(attack_trees, target_dir, template_dir)
        data["has_attack_trees"] = len(attack_trees) > 0
        data["attack_trees"] = attack_trees
        if attack_trees:
            print(f"Attack trees: {len(attack_trees)} Critical/High entries extracted", file=sys.stderr)
    else:
        data["has_attack_trees"] = False
        data["attack_trees"] = []

    # Attack chain data (cross-layer correlation)
    if artifacts.get("has_attack_chains"):
        has_chains, chains = prepare_attack_chains(target_dir, data["findings"], template_dir)
        data["has_attack_chains"] = has_chains
        data["attack_chains"] = chains
        surfaced = [c for c in chains if c.get("surfaced", False)]
        if surfaced:
            print(f"Attack chains: {len(surfaced)} surfaced chain(s) extracted", file=sys.stderr)
    else:
        data["has_attack_chains"] = False
        data["attack_chains"] = []

    # Empty arrays on the false branch so the Typst consumer's `.len() > 0`
    # check fires safely even when the gate is false.
    data["has_source_attribution"] = compute_has_source_attribution(data["findings"])
    if data["has_source_attribution"]:
        data["per_finding_rows"] = build_per_finding_rows(data["findings"])
        data["per_framework_aggregates"] = build_per_framework_aggregates(data["findings"])
        print(
            f"Coverage attestation: gate=true, "
            f"{len(data['per_finding_rows'])} per-finding row(s), "
            f"{len(data['per_framework_aggregates'])} per-framework aggregate(s)",
            file=sys.stderr,
        )
    else:
        data["per_finding_rows"] = []
        data["per_framework_aggregates"] = []

    # Delta / baseline data
    data["has_baseline"] = has_baseline
    data["baseline_source"] = baseline["source"] or ""
    data["baseline_date"] = baseline["date"] or ""
    data["baseline_finding_count"] = baseline["finding_count"] or "0"
    data["baseline_run_id"] = baseline["run_id"] or ""
    data["resolved_findings"] = resolved_findings

    # Delta counts (computed from active findings + resolved)
    if has_baseline:
        data["delta_counts"] = compute_delta_counts(data["findings"], resolved_findings)
    else:
        data["delta_counts"] = {"new": 0, "unchanged": 0, "updated": 0, "resolved": 0}

    # Brand assets
    brand = detect_brand_assets(template_dir)
    data["has_logo_primary"] = brand["has_logo_primary"]
    data["has_logo_horizontal"] = brand["has_logo_horizontal"]
    data["logo_primary_path"] = brand["logo_primary_path"]
    data["logo_primary_dark_path"] = brand["logo_primary_dark_path"]
    data["logo_horizontal_path"] = brand["logo_horizontal_path"]

    # Validate internal consistency
    validation_errors = validate(data)
    if validation_errors:
        for err in validation_errors:
            print(f"Validation error: {err}", file=sys.stderr)
        sys.exit(EXIT_VALIDATION_FAILURE)

    # Generate Typst output
    typst_output = generate_report_data_typ(data)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(typst_output, encoding="utf-8")

    finding_count = len(data["findings"])
    print(f"report-data.typ generated ({finding_count} findings, Tier {tier})", file=sys.stderr)
    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
