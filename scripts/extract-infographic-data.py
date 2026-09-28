#!/usr/bin/env python3
"""Deterministic extraction of structured infographic data from tachi pipeline markdown artifacts.

Reads threats.md, risk-scores.md, and compensating-controls.md from a target
directory and writes a JSON data file with all variable bindings needed by
the infographic templates (baseball-card, system-architecture, risk-funnel,
maestro-stack, maestro-heatmap).

Imports shared parsers from tachi_parsers.py for cross-output consistency
with extract-report-data.py.

Exit codes:
  0 — success
  1 — missing required artifact (threats.md)
  2 — validation failure (severity sum mismatch, ID mismatch, etc.)
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tachi_parsers import (
    EXIT_SUCCESS,
    EXIT_MISSING_ARTIFACT,
    EXIT_VALIDATION_FAILURE,
    SEVERITY_ORDER,
    SEVERITY_ORDINAL,
    MAESTRO_LAYERS,
    parse_frontmatter,
    parse_baseline_frontmatter,
    parse_resolved_findings,
    compute_delta_counts,
    delta_status_by_id,
    apply_delta_status,
    warn_delta_scope,
    compute_risk_posture,
    parse_score,
    classify_maestro_coverage_state,
    parse_markdown_table,
    match_heading,
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
    strip_bold,
)

# =============================================================================
# Constants
# =============================================================================

SEVERITY_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#CA8A04",
    "Low": "#2563EB",
    "Note": "#6B7280",
}

_SEVERITY_ORDINAL = SEVERITY_ORDINAL

_QUALIFYING_SEVERITIES = frozenset({"Critical", "High"})
_SEVERITY_FIELD_PREFERENCE = ("severity", "residual_severity", "risk_level")
_TIER_SOURCE_LABEL = {1: "compensating-controls", 2: "risk-scores", 3: "threats"}

# K11 (T021, data-model.md §4.1, PD-4): risk-funnel width algorithm constants.
# FLOOR + 3*STEP = 60 <= 100 (FR-K11.5).
_FUNNEL_STEP = Decimal("10")
_FUNNEL_FLOOR = Decimal("30")


def _canonical_severity(finding):
    for key in _SEVERITY_FIELD_PREFERENCE:
        val = finding.get(key)
        if val:
            return str(val).strip().title()
    return ""


# =============================================================================
# Gemini Prompt Scaffold Extraction
# =============================================================================

# Templates that have a Gemini prompt section with the standard
# PREAMBLE → DATA CONTENT → POSTAMBLE structure.
_SCAFFOLD_TEMPLATES = frozenset({
    "baseball-card", "risk-funnel", "system-architecture",
    "maestro-stack", "maestro-heatmap",
})

_TEMPLATE_FILES = {
    "baseball-card": "infographic-baseball-card.md",
    "risk-funnel": "infographic-risk-funnel.md",
    "system-architecture": "infographic-system-architecture.md",
    "maestro-stack": "infographic-maestro-stack.md",
    "maestro-heatmap": "infographic-maestro-heatmap.md",
}


def extract_prompt_scaffold(template_name: str, repo_root: Path = None) -> dict:
    """Extract the fixed Gemini prompt scaffold from an infographic template.

    Reads the template file, locates the Gemini prompt section (between
    triple-backtick fences), and splits it at the "DATA CONTENT" marker.

    Returns:
        Dict with:
        - preamble: everything from prompt start through "DATA CONTENT (render
          this as visible text):" — includes opening aesthetic instruction,
          IMPORTANT note, and STYLING DIRECTIVES block.
        - postamble: the FOOTER line through the closing aesthetic instruction.
        - found: True if scaffold was successfully extracted.

    If the template file or prompt section is not found, returns
    found=False with empty strings (graceful degradation — agent falls
    back to its own prompt construction).
    """
    result = {"preamble": "", "postamble": "", "found": False}

    if template_name not in _SCAFFOLD_TEMPLATES:
        return result

    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    template_path = repo_root / "templates" / "tachi" / "infographics" / _TEMPLATE_FILES[template_name]
    if not template_path.exists():
        return result

    content = template_path.read_text(encoding="utf-8")

    # Extract the Gemini prompt block (first triple-backtick fence after
    # a heading containing "Gemini" and "Prompt")
    prompt_text = None
    lines = content.split("\n")
    in_prompt_section = False
    in_fence = False
    fence_lines = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^#{1,4}\s+.*[Gg]emini.*[Pp]rompt", stripped):
            in_prompt_section = True
            continue
        if in_prompt_section and not in_fence and stripped.startswith("```"):
            in_fence = True
            continue
        if in_fence and stripped.startswith("```"):
            prompt_text = "\n".join(fence_lines)
            break
        if in_fence:
            fence_lines.append(line)

    if not prompt_text:
        return result

    # Split at the standalone "DATA CONTENT" section marker, anchored to
    # line start (PD-6). The phrase "DATA CONTENT" also appears inside the
    # IMPORTANT note ("...specified in the DATA CONTENT sections."), so an
    # unanchored substring search can find that prose reference instead of
    # the real marker (for example when a hard-wrapped sentence elsewhere in
    # the preamble happens to contain the same words). re.MULTILINE anchors
    # "^" to the start of every line, not just the start of the string.
    marker_match = re.search(r"^DATA CONTENT \(render this", prompt_text, re.MULTILINE)
    marker_idx = marker_match.start() if marker_match else -1
    if marker_idx == -1:
        # Bare-marker fallback (N8, kept per L14): unreachable while the
        # primary marker above matches (true on all five shipped templates),
        # retained only as a safety net for a future preamble whose marker
        # line drops the "(render this" suffix. Still line-anchored, and
        # still skips the IMPORTANT note's own "...DATA CONTENT sections."
        # reference.
        for m in re.finditer(r"^DATA CONTENT", prompt_text, re.MULTILINE):
            # Skip if this is the IMPORTANT note reference
            line_end = prompt_text.find("\n", m.start())
            line = prompt_text[m.start():line_end if line_end != -1 else len(prompt_text)]
            if "sections." not in line:
                marker_idx = m.start()
                break
    if marker_idx == -1:
        return result

    # Find the full marker line end
    marker_line_end = prompt_text.find("\n", marker_idx)
    if marker_line_end == -1:
        marker_line_end = len(prompt_text)

    preamble = prompt_text[:marker_line_end + 1].rstrip() + "\n"

    # Postamble: from "FOOTER" to end of prompt. Searched only after the
    # marker line (PD-6), so a "FOOTER" appearing earlier — for example
    # inside a hard-wrapped K15 layout-label sentence whose wrap point lands
    # a "FOOTER)" at a line start — can't produce a false match. The
    # no-newline find("FOOTER") fallback is dropped: without the marker-line
    # floor it could match "FOOTER" mid-preamble with no preceding newline at
    # all, corrupting the split silently.
    footer_marker = "\nFOOTER"
    footer_idx = prompt_text.find(footer_marker, marker_line_end)
    if footer_idx != -1:
        postamble = prompt_text[footer_idx:].strip()
    else:
        postamble = ""

    result["preamble"] = preamble
    result["postamble"] = postamble
    result["found"] = True
    return result


# =============================================================================
# T009: Largest Remainder Method
# =============================================================================

def largest_remainder(percentages_map, target=100):
    """Compute integer percentages that sum to exactly `target` using the Largest Remainder Method.

    Args:
        percentages_map: Dict mapping labels to raw counts (e.g., {"Critical": 5, "High": 14}).
        target: Target sum for percentages (default 100).

    Returns:
        Dict mapping labels to integer percentages summing to exactly `target`.
        Deterministic: ties broken by label ascending (lexicographic).
    """
    total = sum(percentages_map.values())
    if total == 0:
        return {label: 0 for label in percentages_map}

    # Compute exact percentages
    exact = {label: (count / total) * target for label, count in percentages_map.items()}

    # Take floor of each
    floors = {label: math.floor(val) for label, val in exact.items()}

    # Compute remainder to distribute
    remainder = target - sum(floors.values())

    # Sort by fractional part descending, then label ascending for ties
    fractional = {label: exact[label] - floors[label] for label in exact}
    sorted_labels = sorted(
        fractional.keys(),
        key=lambda label: (-fractional[label], label),
    )

    # Distribute +1 to top N items where N = remainder
    result = dict(floors)
    for i in range(remainder):
        result[sorted_labels[i]] += 1

    return result


# =============================================================================
# T010: Severity Extraction Pipeline
# =============================================================================

def extract_severity(tier, threats_content, rs_content=None, cc_content=None):
    """Extract severity counts, findings, and compensating controls data based on tier.

    Args:
        tier: Data source tier (1, 2, or 3).
        threats_content: Full text content of threats.md.
        rs_content: Pre-read content of risk-scores.md (required for tier 2;
            also consulted at tier 1 for the K11 inherent-score join when
            present).
        cc_content: Pre-read content of compensating-controls.md (required for tier 1).

    Returns:
        Tuple of (severity_dict, findings_list, cc_data_or_None).
        - severity_dict: {critical, high, medium, low, note, total}
        - findings_list: List of finding dicts (structure varies by tier)
        - cc_data: Full compensating controls data for Tier 1, None otherwise
    """
    cc_data = None

    if tier == 1:
        # K11 (data-model.md §3, F2): join risk-scores composites onto rows
        # whose Coverage Matrix has no Inherent Score/Inherent column.
        composites_by_id = None
        if rs_content:
            composites_by_id = {
                f["id"]: parse_score(f["composite_score"])
                for f in parse_risk_scores_findings(rs_content)
                if f.get("id")
            }
        cc_data = parse_compensating_controls_md(cc_content, composites_by_id=composites_by_id)
        severity = cc_data["severity"]
        findings = cc_data["findings"]
    elif tier == 2:
        severity = parse_risk_scores_severity(rs_content)
        findings = parse_risk_scores_findings(rs_content)
    else:  # tier == 3
        # Per architect C-3 decision: derive severity from Section 7 findings array,
        # NOT Section 6 Risk Summary. This matches extract-report-data.py behavior.
        findings = parse_threats_findings(threats_content)
        severity = _empty_severity()
        for f in findings:
            key = f.get("risk_level", "").lower()
            if key in severity:
                severity[key] += 1
        severity["total"] = len(findings)

    return severity, findings, cc_data


# =============================================================================
# T011: Severity Percentages
# =============================================================================

def compute_severity_percentages(severity):
    """Compute severity distribution with integer percentages and color codes.

    Excludes Note severity from percentage calculation.

    Args:
        severity: Dict with critical/high/medium/low/note/total keys.

    Returns:
        List of dicts with label, count, percentage, color — in SEVERITY_ORDER
        (Critical, High, Medium, Low). Note is excluded.
    """
    # Build counts dict excluding Note
    counts = {
        "Critical": severity["critical"],
        "High": severity["high"],
        "Medium": severity["medium"],
        "Low": severity["low"],
    }

    percentages = largest_remainder(counts)

    result = []
    for label in SEVERITY_ORDER:
        if label == "Note":
            continue
        result.append({
            "label": label,
            "count": counts[label],
            "percentage": percentages[label],
            "color": SEVERITY_COLORS[label],
        })

    return result


# =============================================================================
# T012: Heat Map
# =============================================================================

def compute_heat_map(findings, scope_components, tier):
    """Build component x severity cross-tabulation heat map.

    Args:
        findings: List of finding dicts from extract_severity().
        scope_components: List of component dicts with "name" key from parse_scope_data().
        tier: Data source tier (1, 2, or 3).

    Returns:
        List of row dicts: {component, critical, high, medium, low, total}.
        Sorted by total descending, component name ascending for ties.
        Max 8 rows: top 7 + "Other" aggregation when >8 components.
    """
    # Initialize all components from scope with zero counts
    component_counts = {}
    for comp in scope_components:
        name = comp["name"]
        if name:
            component_counts[name] = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    # Tally findings into components
    for f in findings:
        comp = f.get("component", "")
        if not comp:
            continue

        # Get severity label based on tier
        if tier == 1:
            sev_label = f.get("residual_severity", "").lower()
        elif tier == 2:
            sev_label = f.get("severity", "").lower()
        else:  # tier == 3
            sev_label = f.get("risk_level", "").lower()

        # Exclude Note severity from heat map
        if sev_label == "note":
            continue

        # Initialize component if not in scope (finding references unknown component)
        if comp not in component_counts:
            component_counts[comp] = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        if sev_label in component_counts[comp]:
            component_counts[comp][sev_label] += 1

    # Build rows with totals
    rows = []
    for comp_name, counts in component_counts.items():
        total = counts["critical"] + counts["high"] + counts["medium"] + counts["low"]
        rows.append({
            "component": comp_name,
            "critical": counts["critical"],
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"],
            "total": total,
        })

    # Sort: total descending, component name ascending for ties
    rows.sort(key=lambda r: (-r["total"], r["component"]))

    # When >8 components: keep top 7, aggregate remaining into "Other"
    if len(rows) > 8:
        top_rows = rows[:7]
        other_rows = rows[7:]
        other = {
            "component": "Other",
            "critical": sum(r["critical"] for r in other_rows),
            "high": sum(r["high"] for r in other_rows),
            "medium": sum(r["medium"] for r in other_rows),
            "low": sum(r["low"] for r in other_rows),
            "total": sum(r["total"] for r in other_rows),
        }
        top_rows.append(other)
        rows = top_rows

    return rows


# =============================================================================
# T013: Top Findings Selection
# =============================================================================

def select_top_findings(findings, tier, n=5):
    """Select top N findings with deterministic ranking.

    Args:
        findings: List of finding dicts from extract_severity().
        tier: Data source tier (1, 2, or 3).
        n: Number of top findings to select (default 5).

    Returns:
        List of dicts: {id, component, threat, risk_level, score}.
        Sorted by score descending, threat ID ascending for ties.
        Note severity findings excluded.
    """
    scored = []
    for f in findings:
        fid = f.get("id", "")
        comp = f.get("component", "")
        threat = f.get("threat", "")

        # Determine severity label and score based on tier
        if tier == 1:
            sev_label = f.get("residual_severity", "")
            try:
                score = float(f.get("residual_score", 0))
            except (ValueError, TypeError):
                score = 0.0
        elif tier == 2:
            sev_label = f.get("severity", "")
            try:
                score = float(f.get("composite_score", 0))
            except (ValueError, TypeError):
                score = 0.0
        else:  # tier == 3
            sev_label = f.get("risk_level", "")
            score = float(_SEVERITY_ORDINAL.get(sev_label, 0))

        # Exclude Note severity
        if sev_label.lower() == "note":
            continue

        scored.append({
            "id": fid,
            "component": comp,
            "threat": threat,
            "risk_level": sev_label,
            "score": score,
        })

    # Sort: score descending, threat ID ascending for ties
    scored.sort(key=lambda f: (-f["score"], f["id"]))

    return scored[:n]


# =============================================================================
# T014: Component Risk Weights
# =============================================================================

def compute_component_risk_weights(heat_map):
    """Compute weighted risk score and classification for each component.

    Args:
        heat_map: List of heat map row dicts from compute_heat_map().

    Returns:
        List of dicts: {component, weight, score, annotation}.
        Sorted by score descending, component name ascending for ties.
    """
    result = []
    for row in heat_map:
        total = row["total"]
        if total == 0:
            score = 0.0
        else:
            score = (row["critical"] * 4 + row["high"] * 3 + row["medium"] * 2 + row["low"] * 1) / total

        # Classify
        if score >= 3.0:
            weight = "high"
        elif score >= 2.0:
            weight = "medium"
        else:
            weight = "low"

        # Generate annotation with non-zero severity levels
        parts = []
        if row["critical"] > 0:
            parts.append(f"{row['critical']} Critical")
        if row["high"] > 0:
            parts.append(f"{row['high']} High")
        if row["medium"] > 0:
            parts.append(f"{row['medium']} Medium")
        if row["low"] > 0:
            parts.append(f"{row['low']} Low")

        # Build annotation: "{high} High + {critical} Critical findings"
        annotation = " + ".join(parts) + " findings" if parts else "No findings"

        result.append({
            "component": row["component"],
            "weight": weight,
            "score": round(score, 1),
            "annotation": annotation,
        })

    # Sort: score descending, component name ascending for ties
    result.sort(key=lambda r: (-r["score"], r["component"]))

    return result


# =============================================================================
# T015: Deduplicate Findings
# =============================================================================

def deduplicate_findings(threats_content):
    """Parse Section 3 agent tables and Section 4a correlation groups for deduplication.

    Args:
        threats_content: Full text content of threats.md.

    Returns:
        Dict: {unique_ids: set, raw_count: int, has_correlations: bool}.
        raw_count is from Section 6 total.
    """
    lines = threats_content.split("\n")

    # Parse all Section 3 (and Section 4 AI) agent tables: find all ### 3.X and ### 4.X subsections
    all_threat_ids = set()

    # Find agent table subsections (### 3.X and ### 4.X, but not ### 4a)
    agent_sections = []
    for i, line in enumerate(lines):
        if re.match(r"^###\s+[34]\.\d+\s+", line):
            agent_sections.append(i)

    for sec_start in agent_sections:
        # Scan forward for the table in this subsection
        for i in range(sec_start + 1, len(lines)):
            stripped = lines[i].strip()
            # Stop at next section header
            if stripped.startswith("## ") or stripped.startswith("### "):
                break
            # Look for table rows with threat IDs in first column
            if stripped.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", stripped):
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if cells and cells[0] and not cells[0].lower().startswith("id"):
                    # First cell is the threat ID
                    tid = strip_bold(cells[0])
                    if tid and re.match(r"^[A-Z]", tid):
                        all_threat_ids.add(tid)

    # Parse Section 4a correlation groups if present
    has_correlations = False
    sec4a_start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+4a\.", line) or re.match(r"^###\s+4a\.", line):
            sec4a_start = i
            break

    if sec4a_start is not None:
        has_correlations = True
        # Extract threat IDs from correlation group table
        for i in range(sec4a_start + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("## ") and not stripped.startswith("## 4a"):
                break
            if stripped.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", stripped):
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                # Findings column (index 1) contains comma-separated IDs
                if len(cells) >= 2 and not cells[0].lower().startswith("group"):
                    findings_cell = cells[1]
                    for tid in re.findall(r"[A-Z]+-\d+", findings_cell):
                        all_threat_ids.add(tid)
    else:
        print("Note: No correlation groups found; using raw finding counts.", file=sys.stderr)

    # Get raw count from Section 6 total
    severity = parse_threats_severity(threats_content)
    raw_count = severity.get("total", 0)

    return {
        "unique_ids": all_threat_ids,
        "raw_count": raw_count,
        "has_correlations": has_correlations,
    }


# =============================================================================
# T016: Metadata Computation
# =============================================================================

def compute_metadata(threats_content, frontmatter, tier, severity, scope_components, project_name):
    """Compute infographic metadata fields.

    Args:
        threats_content: Full text content of threats.md.
        frontmatter: Parsed frontmatter dict from parse_frontmatter().
        tier: Data source tier (1, 2, or 3).
        severity: Severity dict with critical/high/medium/low/note/total keys.
        scope_components: List of component dicts with "name" key.
        project_name: Project name string.

    Returns:
        Dict with metadata fields.
    """
    # scan_date from frontmatter
    scan_date = frontmatter.get("date", "Unknown")

    # agent_count: count distinct ### 3.X and ### 4.X subsections (STRIDE + AI agents)
    agent_count = len(re.findall(r"^###\s+[34]\.\d+\s+", threats_content, re.MULTILINE))

    # risk_posture: deterministic template string
    tier_labels = {
        1: "Residual risk",
        2: "Inherent risk",
        3: "Severity assessment",
    }
    tier_label = tier_labels.get(tier, "Unknown")
    component_count = len(scope_components)
    risk_posture = (
        f"{tier_label} \u2014 {severity['critical']} Critical and "
        f"{severity['high']} High findings across {component_count} components"
    )

    # schema_version from frontmatter
    schema_version = frontmatter.get("schema_version", "1.0")

    # data_source_type
    source_types = {
        1: "compensating-controls",
        2: "risk-scores",
        3: "threats",
    }
    data_source_type = source_types.get(tier, "threats")

    return {
        "project_name": project_name,
        "scan_date": scan_date,
        "tier": tier,
        "data_source_type": data_source_type,
        "total_findings": severity["total"],
        "note_count": severity.get("note", 0),
        "agent_count": agent_count,
        "risk_posture": risk_posture,
        "schema_version": schema_version,
    }


# =============================================================================
# T017: Validation
# =============================================================================

def validate_infographic(data):
    """Validate internal consistency of infographic data.

    Checks:
    1. Severity sum: sum of severity_distribution[].count must equal
       metadata.total_findings - metadata.note_count.
    2. Top findings IDs: every ID in top_findings must exist in the parsed findings set.
    3. Heat map row consistency: critical + high + medium + low must equal total per row.

    Args:
        data: Dict with metadata, severity_distribution, heat_map, top_findings, findings_ids.

    Returns:
        List of error strings. Empty list means valid.
    """
    errors = []

    # Check 1: severity sum
    sev_sum = sum(entry["count"] for entry in data["severity_distribution"])
    expected = data["metadata"]["total_findings"] - data["metadata"]["note_count"]
    if sev_sum != expected:
        errors.append(
            f"Validation error: Severity sum mismatch \u2014 expected {expected}, got {sev_sum}"
        )

    # Check 2: top findings IDs must exist in findings set
    findings_ids = data.get("findings_ids", set())
    for tf in data["top_findings"]:
        if tf["id"] not in findings_ids:
            errors.append(
                f"Validation error: Top finding ID {tf['id']} not found in findings set"
            )

    # Check 3: heat map row consistency
    for row in data["heat_map"]:
        row_sum = row["critical"] + row["high"] + row["medium"] + row["low"]
        if row_sum != row["total"]:
            errors.append(
                f"Validation error: Heat map row '{row['component']}' — "
                f"expected total {row['total']}, got {row_sum}"
            )

    return errors


# =============================================================================
# T024: System Architecture Overlay
# =============================================================================

# Trust level sort key: highest trust first (trusted=0, semi-trusted=1, untrusted=2)
_TRUST_LEVEL_ORDER = {"trusted": 0, "semi-trusted": 1, "untrusted": 2}


def compute_architecture_overlay(scope_data, findings, tier, heat_map):
    """Compute system-architecture template overlay: trust zones, data flows, boundary crossings.

    Args:
        scope_data: Dict from parse_scope_data() with trust_boundaries, data_flows, boundary_crossings.
        findings: List of finding dicts from extract_severity().
        tier: Data source tier (1, 2, or 3).
        heat_map: List of heat map row dicts from compute_heat_map().

    Returns:
        Dict with trust_zones (list or None), data_flows (list), boundary_crossings (list).
    """
    # Build component severity lookup from heat_map for data flow coloring
    comp_severity = {}
    for row in heat_map:
        comp_severity[row["component"]] = row

    # --- Trust Zones ---
    trust_zones = _compute_trust_zones(scope_data)

    # --- Data Flows ---
    data_flows = _compute_data_flows(scope_data, comp_severity)

    # --- Boundary Crossings ---
    boundary_crossings = _compute_boundary_crossings(scope_data, comp_severity)

    return {
        "trust_zones": trust_zones,
        "data_flows": data_flows,
        "boundary_crossings": boundary_crossings,
    }


def _compute_trust_zones(scope_data):
    """Parse trust boundaries into trust zone groupings.

    Returns list of zone dicts ordered by trust level descending (highest trust first),
    components sorted alphabetically within each zone.
    Returns None when no trust boundaries exist (T025 fallback).
    """
    boundaries = scope_data.get("trust_boundaries", [])

    if not boundaries:
        # T025: Trust zone absence fallback
        print("Note: No trust zones found; using flat component layout.", file=sys.stderr)
        return None

    zones = []
    for tb in boundaries:
        zone_name = tb.get("zone", "")
        trust_level = tb.get("trust-level", "")
        components_str = tb.get("components", "")

        # Parse comma-separated component names, strip whitespace, sort alphabetically
        components = sorted(
            [c.strip() for c in components_str.split(",") if c.strip()]
        )

        zones.append({
            "name": zone_name,
            "trust_level": trust_level.lower(),
            "components": components,
        })

    # Sort by trust level descending (highest trust first): trusted < semi-trusted < untrusted
    # Use _TRUST_LEVEL_ORDER mapping; unknown levels sort last (value 99)
    zones.sort(key=lambda z: (_TRUST_LEVEL_ORDER.get(z["trust_level"], 99), z["name"]))

    return zones


def _normalize_component_name(name):
    """Collapse component names so "API Gateway", "api-gateway", "api_gateway" all match."""
    if not name:
        return ""
    return (
        name.strip()
        .lower()
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
    )


def _compute_dfd_type_layers(scope_data):
    """Fallback layer derivation: group Section 1 components by DFD type when no trust zones exist."""
    components = scope_data.get("components", [])
    if not components:
        return None

    by_type = {}
    for comp in components:
        ctype = (comp.get("type") or "").strip()
        cname = (comp.get("name") or "").strip()
        if not ctype or not cname:
            continue
        by_type.setdefault(ctype, []).append(cname)

    if not by_type:
        return None

    layers = []
    for position, ctype in enumerate(sorted(by_type.keys())):
        comp_names = sorted(by_type[ctype])
        if not comp_names:
            continue
        layers.append({
            "name": ctype,
            "position": position,
            "components": comp_names,
            "component_count": len(comp_names),
            "source_kind": "dfd_type",
        })

    return layers if layers else None


def _extract_composite_score(finding):
    """Prefer composite_score, fall back to residual_score; return float or None."""
    for key in ("composite_score", "residual_score"):
        raw = finding.get(key)
        if raw is None or raw == "":
            continue
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return None


def _extract_description(finding):
    """Prefer description, fall back to threat, fall back to mitigation."""
    for key in ("description", "threat", "mitigation"):
        val = finding.get(key)
        if val:
            return str(val).strip()
    return ""


_TOTAL_CAP = 8
_PER_LAYER_CEILING = 4


def _qualifying_per_layer(findings, layers):
    """Group qualifying (Critical/High) findings by their resolved layer.

    Returns ``(per_layer, comp_to_layer)`` where ``per_layer`` is a dict of
    ``layer_name → list[finding]`` containing only qualifying findings whose
    component maps into one of ``layers`` (orphans are dropped).
    """
    comp_to_layer = {}
    for idx, layer in enumerate(layers):
        for comp in layer.get("components", []):
            key = _normalize_component_name(comp)
            if key and key not in comp_to_layer:
                comp_to_layer[key] = (layer["name"], idx)

    per_layer = {layer["name"]: [] for layer in layers}
    for finding in findings:
        severity = _canonical_severity(finding)
        if severity not in _QUALIFYING_SEVERITIES:
            continue
        component = finding.get("component") or ""
        key = _normalize_component_name(component)
        if not key or key not in comp_to_layer:
            continue
        layer_name, _idx = comp_to_layer[key]
        per_layer[layer_name].append(finding)

    return per_layer, comp_to_layer


def _callout_sort_key(f):
    """Per-finding tie-break: severity desc → composite score desc → id asc."""
    severity = _canonical_severity(f)
    composite = _extract_composite_score(f)
    return (
        -_SEVERITY_ORDINAL.get(severity, 0),
        -(composite if composite is not None else 0.0),
        f.get("id", ""),
    )


def _allocate_callouts_per_layer(per_layer):
    """Allocate callout slots across qualifying layers via Largest Remainder Method.

    Invariants enforced (FR-212-8 / FR-212-9 / FR-212-12):
      - Total cap: ``sum(allocation.values()) <= _TOTAL_CAP``.
      - System-wide density (FR-212-8): when total qualifying findings >= 6
        emit 6-8 callouts; when < 6 emit exactly that many (no synthetic
        inflation).
      - Per-layer floor: when ``len(qualifying_layers) <= _TOTAL_CAP``, every
        qualifying layer receives >= 1 slot (suspended when more qualifying
        layers exist than the total cap permits).
      - Per-layer ceiling: no layer receives more than
        ``min(_PER_LAYER_CEILING, qualifying_count_for_layer)``.
      - Determinism: float-tie ordering broken by case-insensitive layer name
        ascending so two runs on identical input produce byte-identical output
        under SOURCE_DATE_EPOCH=1700000000.

    Returns ``allocation`` as a dict mapping ``layer_name → int`` (zero when
    a layer is non-qualifying or when the >8-layer branch trims it). Returns
    an empty dict when there are no qualifying findings at all.
    """
    qualifying_per_layer = {
        name: len(items) for name, items in per_layer.items() if items
    }
    if not qualifying_per_layer:
        return {}

    qualifying_layer_names = list(qualifying_per_layer.keys())
    total_qualifying = sum(qualifying_per_layer.values())
    target_total = min(total_qualifying, _TOTAL_CAP)
    n_qualifying = len(qualifying_layer_names)

    if n_qualifying > _TOTAL_CAP:
        # Per-layer floor suspended (more qualifying layers than total-cap
        # permits). Pick top _TOTAL_CAP layers by qualifying count desc
        # (tie-break: layer name ascending case-insensitive); allocate 1 each;
        # remaining qualifying layers receive 0. No remainder phase — the
        # cap is fully consumed by the per-layer-floor allocations of the
        # selected layers.
        ranked = sorted(
            qualifying_layer_names,
            key=lambda n: (-qualifying_per_layer[n], n.lower()),
        )
        allocation = {name: 0 for name in qualifying_layer_names}
        for name in ranked[:_TOTAL_CAP]:
            allocation[name] = 1
        return allocation

    # Per-layer floor of 1 for every qualifying layer.
    allocation = {name: 1 for name in qualifying_layer_names}
    current_total = n_qualifying

    if current_total >= target_total:
        # Edge case: total_qualifying == n_qualifying (every layer has exactly
        # one qualifying finding). No remainder slots to distribute.
        return allocation

    # Largest-Remainder-Method remainder distribution.
    # quota[name] = (layer's qualifying share) * target_total.
    # Layers with the largest fractional remainder get extra slots first; ties
    # break by layer name ascending (case-insensitive) for determinism.
    quotas = {
        name: (qualifying_per_layer[name] / total_qualifying) * target_total
        for name in qualifying_layer_names
    }
    ranked_by_remainder = sorted(
        qualifying_layer_names,
        key=lambda n: (
            -(quotas[n] - math.floor(quotas[n])),
            n.lower(),
        ),
    )

    slots_left = target_total - current_total
    while slots_left > 0:
        added = 0
        for name in ranked_by_remainder:
            if slots_left == 0:
                break
            cap = min(_PER_LAYER_CEILING, qualifying_per_layer[name])
            if allocation[name] < cap:
                allocation[name] += 1
                slots_left -= 1
                added += 1
        if added == 0:
            # Every layer at its ceiling — cannot allocate further. This
            # happens when target_total exceeds the sum of per-layer caps,
            # which only occurs in deeply-pathological inputs (e.g., 8 layers
            # each with a single qualifying finding requiring target_total=8
            # — already satisfied by the floor=1 path above). Defensive
            # break preserves termination.
            break

    return allocation


def _select_critical_high_callouts(findings, layers, per_layer=None):
    """Select up to _TOTAL_CAP=8 Critical/High callouts via Largest Remainder Method.

    Replaces the pre-F-212 per-layer-dedup logic (1 callout per layer) with
    system-wide allocation that satisfies FR-212-8 / FR-212-9 / FR-212-10 /
    FR-212-12:
      - 6-8 callouts when total qualifying findings >= 6.
      - Exactly ``total_qualifying`` callouts when < 6 (no synthetic
        inflation).
      - Every qualifying layer represented with >= 1 callout when the
        qualifying-layer count is <= _TOTAL_CAP (per-layer floor).
      - No layer over _PER_LAYER_CEILING=4 callouts.
      - Within each layer: severity desc -> composite score desc -> finding
        id ascending tie-break.
      - Across layers: emit in existing layer position order (no new
        layer-sort semantics introduced by L2).

    Findings whose component does not resolve to any of ``layers`` are
    dropped. The output record shape matches the pre-F-212 contract:
    ``{layer_name, finding_id, severity, raw_description, composite_score,
    affected_component}``.

    ``per_layer`` is an optional pre-computed mapping from
    ``_qualifying_per_layer(findings, layers)`` — when supplied, the second
    traversal of findings × components is skipped (perf optimisation for
    callers that already need the mapping for follow-on work). When None,
    the mapping is computed inline so the helper remains independently
    callable from tests and future call sites.
    """
    if per_layer is None:
        per_layer, _comp_to_layer = _qualifying_per_layer(findings, layers)
    allocation = _allocate_callouts_per_layer(per_layer)

    if not allocation:
        return []

    callouts = []
    for layer in layers:
        name = layer["name"]
        n = allocation.get(name, 0)
        if n <= 0:
            continue
        items_sorted = sorted(per_layer[name], key=_callout_sort_key)
        for top in items_sorted[:n]:
            callouts.append({
                "layer_name": name,
                "finding_id": top.get("id", ""),
                "severity": _canonical_severity(top),
                "raw_description": _extract_description(top),
                "composite_score": _extract_composite_score(top),
                "affected_component": (top.get("component") or None),
            })

    return callouts


def _build_flow_edges(scope_data):
    """Build the L3 ``flow_edges[]`` array for the executive-architecture payload.

    Reads ``scope_data["data_flows"]`` (produced by ``parse_scope_data`` in
    ``scripts/tachi_parsers.py:927``) and emits one record per entry with the
    consumer-locked field names ``source``, ``destination`` (NOT ``target`` —
    Architect MEDIUM-2 lock), ``data``, ``protocol``. Sorts ascending by
    ``(source.casefold(), destination.casefold())``; truncates to the first 50
    entries after sort and logs a warning to stderr when the producer emitted
    more (FR-212-17). Returns ``[]`` when the source key is absent or empty.
    """
    flows = scope_data.get("data_flows", []) or []
    edges = []
    for df in flows:
        edges.append({
            "source": df.get("source", "") or "",
            "destination": df.get("destination", "") or "",
            "data": df.get("data", "") or "",
            "protocol": df.get("protocol", "") or "",
        })
    edges.sort(key=lambda e: (e["source"].casefold(), e["destination"].casefold()))
    if len(edges) > 50:
        emitted = len(edges)
        edges = edges[:50]
        print(
            f"Warning: flow_edges truncated to 50 entries "
            f"({emitted} emitted by producer)",
            file=sys.stderr,
        )
    return edges


def _build_clusters(scope_data):
    """Build the L3 ``clusters[]`` array for the executive-architecture payload.

    Reads ``scope_data["trust_boundaries"]`` (produced by ``parse_scope_data``
    in ``scripts/tachi_parsers.py:937``) and emits one record per entry with
    consumer-aligned keys: ``name`` (from ``zone``), ``members`` (parsed from
    the comma-separated ``components`` string, stripped, and sorted ascending
    case-insensitively), ``trust_level`` (renamed from producer's
    ``trust-level`` via hyphen→underscore and lowercased to match the
    ``_TRUST_LEVEL_ORDER`` lookup convention used by ``_compute_trust_zones``).

    Sorts ascending by ``(_TRUST_LEVEL_ORDER.get(trust_level, 99),
    name.casefold())`` mirroring ``_compute_trust_zones:784``. Returns ``[]``
    when the source key is absent or empty.
    """
    boundaries = scope_data.get("trust_boundaries", []) or []
    clusters = []
    for tb in boundaries:
        zone_name = tb.get("zone", "") or ""
        trust_level = (tb.get("trust-level", "") or "").lower()
        components_str = tb.get("components", "") or ""
        members = sorted(
            [c.strip() for c in components_str.split(",") if c.strip()],
            key=str.casefold,
        )
        clusters.append({
            "name": zone_name,
            "members": members,
            "trust_level": trust_level,
        })
    clusters.sort(
        key=lambda c: (
            _TRUST_LEVEL_ORDER.get(c["trust_level"], 99),
            c["name"].casefold(),
        )
    )
    return clusters


def _build_executive_architecture_payload(tier, findings, scope_data, source_file,
                                           risk_posture_level=None, risk_posture_label=None):
    """Assemble the ExecutiveArchitecturePayload.

    Derives layers from trust zones (preferred) or falls back to grouping components by
    DFD type. Returns ``{"error": "no_scope_data"}`` when neither source yields layers;
    the caller translates that into exit code 2.

    ``risk_posture_level``/``risk_posture_label`` (K13-posture, T025, data-model.md
    §5) are optional so direct callers that predate this field keep working;
    ``main()`` always supplies both, computed once from the tier's severity
    counts via :func:`compute_risk_posture`.
    """
    trust_zones = _compute_trust_zones(scope_data)
    fallback_used = False
    layers = []

    if trust_zones:
        # Trust zones arrive sorted trusted-first; the executive view places the most
        # exposed layer at position 0, so reverse into untrusted-first order.
        ordered = list(reversed(trust_zones))
        for position, zone in enumerate(ordered):
            comp_names = list(zone.get("components") or [])
            if not comp_names:
                continue
            layers.append({
                "name": zone.get("name") or "",
                "position": position,
                "components": comp_names,
                "component_count": len(comp_names),
                "source_kind": "trust_zone",
            })
    else:
        dfd_layers = _compute_dfd_type_layers(scope_data)
        if dfd_layers:
            fallback_used = True
            layers = dfd_layers

    layers = [layer for layer in layers if layer.get("component_count", 0) > 0]

    if not layers:
        return {"error": "no_scope_data"}

    critical_count = 0
    high_count = 0
    for f in findings:
        sev = _canonical_severity(f)
        if sev == "Critical":
            critical_count += 1
        elif sev == "High":
            high_count += 1
    total_qualifying = critical_count + high_count

    # Compute the qualifying-per-layer mapping ONCE and pass it through to
    # both the callout selector and the overflow annotation below. The
    # mapping iterates findings x components and was previously called
    # twice per payload build (once inside _select_critical_high_callouts,
    # once for layer_overflow annotation); caching here removes one full
    # traversal. Defensive perf hygiene aligned with SC-212-8.
    per_layer_qualifying, _comp_to_layer = _qualifying_per_layer(findings, layers)
    callouts = _select_critical_high_callouts(
        findings, layers, per_layer=per_layer_qualifying
    )
    total_after_layer_dedup = len(callouts)

    # Annotate each layer with a layer_overflow field per FR-212-9. When the
    # qualifying-finding count for a layer exceeds the number of callouts
    # actually allocated, surface the residual via a compact "+ N more in
    # this layer" string so the rendered page communicates that the page is
    # not the full diagnosis. Otherwise the field is None.
    callouts_per_layer = {}
    for callout in callouts:
        callouts_per_layer[callout["layer_name"]] = (
            callouts_per_layer.get(callout["layer_name"], 0) + 1
        )
    for layer in layers:
        qualifying_count = len(per_layer_qualifying.get(layer["name"], []))
        allocated = callouts_per_layer.get(layer["name"], 0)
        if qualifying_count > allocated:
            layer["layer_overflow"] = (
                f"+ {qualifying_count - allocated} more in this layer"
            )
        else:
            layer["layer_overflow"] = None

    skip_image = (total_qualifying == 0)
    generation_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    metadata = {
        "template_name": "executive-architecture",
        "tier_source": tier,
        "source_file": str(source_file),
        "generation_timestamp": generation_timestamp,
        "qualifying_layer_count": len(layers),
        "total_filtered_count": total_qualifying,
        "skip_image": skip_image,
        "fallback_used": fallback_used,
    }
    # K13-posture (T025, data-model.md §5): metadata.risk_posture_{level,label}
    # on every infographic JSON, executive-architecture included. Kept apart
    # from the `return` dict below, where T027's `allow_list` key will land,
    # so a future K15 revert never touches these two lines (LOW-4).
    if risk_posture_level is not None:
        metadata["risk_posture_level"] = risk_posture_level
        metadata["risk_posture_label"] = risk_posture_label

    severity_distribution = {
        "critical_count": critical_count,
        "high_count": high_count,
        "total_qualifying": total_qualifying,
        "total_after_layer_dedup": total_after_layer_dedup,
    }

    flow_edges = _build_flow_edges(scope_data)
    clusters = _build_clusters(scope_data)

    # K15 (T027, data-model.md §8): the top-level allow-list, added to the
    # return dict below rather than near the K13-posture lines above this
    # function's `metadata` block (LOW-4) — a TW-6 revert of this commit
    # then applies cleanly on top of the K13-posture commit.
    allow_list = compute_allow_list(
        "executive-architecture", findings, scope_data, payload={"callouts": callouts}
    )

    return {
        "metadata": metadata,
        "layers": layers,
        "callouts": callouts,
        "severity_distribution": severity_distribution,
        "flow_edges": flow_edges,
        "clusters": clusters,
        "allow_list": allow_list,
    }


def _compute_data_flows(scope_data, comp_severity):
    """Compute data flow severity coloring based on destination component's highest severity.

    Args:
        scope_data: Dict from parse_scope_data() with data_flows.
        comp_severity: Dict mapping component name to heat map row.

    Returns:
        List of data flow dicts with source, destination, severity_color, label.
        Sorted by source ascending, then destination ascending for determinism.
    """
    flows = []
    for df in scope_data.get("data_flows", []):
        source = df.get("source", "")
        destination = df.get("destination", "")
        label = df.get("data", "")

        # Determine severity color from destination component's heat map entry
        severity_color = _component_severity_color(comp_severity, destination)

        flows.append({
            "source": source,
            "destination": destination,
            "severity_color": severity_color,
            "label": label,
        })

    # Sort deterministically: source ascending, destination ascending
    flows.sort(key=lambda f: (f["source"], f["destination"]))

    return flows


def _compute_boundary_crossings(scope_data, comp_severity):
    """Compute boundary crossing annotations with finding counts.

    Args:
        scope_data: Dict from parse_scope_data() with boundary_crossings.
        comp_severity: Dict mapping component name to heat map row.

    Returns:
        List of boundary crossing dicts with from_zone, to_zone, crossing_point, finding_count.
        Sorted by from_zone ascending, to_zone ascending for determinism.
    """
    crossings = []
    for bc in scope_data.get("boundary_crossings", []):
        from_zone = bc.get("from-zone", "")
        to_zone = bc.get("to-zone", "")
        crossing_point = bc.get("components", "")

        # Count findings for crossing point components from heat map
        # The "components" field may contain comma-separated component names
        finding_count = 0
        for comp_name in [c.strip() for c in crossing_point.split(",") if c.strip()]:
            row = comp_severity.get(comp_name, {})
            finding_count += (
                row.get("critical", 0)
                + row.get("high", 0)
                + row.get("medium", 0)
                + row.get("low", 0)
            )

        crossings.append({
            "from_zone": from_zone,
            "to_zone": to_zone,
            "crossing_point": crossing_point,
            "finding_count": finding_count,
        })

    # Sort deterministically: from_zone ascending, to_zone ascending
    crossings.sort(key=lambda c: (c["from_zone"], c["to_zone"]))

    return crossings


def _component_severity_color(comp_severity, component_name):
    """Determine the severity color for a component based on its highest-severity findings.

    Args:
        comp_severity: Dict mapping component name to heat map row dict.
        component_name: Name of the component to look up.

    Returns:
        Hex color string from SEVERITY_COLORS.
    """
    row = comp_severity.get(component_name, {})

    if row.get("critical", 0) > 0:
        return SEVERITY_COLORS["Critical"]
    elif row.get("high", 0) > 0:
        return SEVERITY_COLORS["High"]
    elif row.get("medium", 0) > 0:
        return SEVERITY_COLORS["Medium"]
    elif row.get("low", 0) > 0:
        return SEVERITY_COLORS["Low"]
    else:
        return SEVERITY_COLORS["Note"]


# =============================================================================
# K11 Risk Funnel Computation (F-373 T021, data-model.md §4, D-2, PD-4/5/18)
# =============================================================================

def compute_risk_funnel(tier, threats_content, cc_data=None, rs_content=None):
    """Compute the 4-entry risk funnel per data-model.md §4 (K11, D-2).

    JSON tier k is funnel Tier k+1 (0 = Threats Identified through 3 =
    Residual Risk) — this is not the data source ``tier``. Tiers 2-4 (JSON
    indices 1-3) are always summed over D-2's "one row set":
    compensating-controls.md's Coverage Matrix rows in 4-tier mode
    (``tier == 1``), or risk-scores.md's Scored Threat Table rows in 3-tier
    mode (``tier == 2``). ``tier == 3`` (threats-only) has no row set at
    all, so JSON indices 1-3 are all ghost.

    Args:
        tier: Data source tier (1, 2, or 3) from determine_tier().
        threats_content: Full text content of threats.md.
        cc_data: Pre-parsed compensating-controls.md data (from
            extract_severity's tier==1 branch; the K11 inherent join is
            already applied there). Only consulted when tier == 1.
        rs_content: Pre-read content of risk-scores.md. Only consulted when
            tier == 2.

    Returns:
        Dict with ``funnel_tiers`` (always 4 objects), ``reduction_percentages``
        (always 3 entries), and the row-derived ``risk_reduction`` /
        ``inherent_score`` / ``residual_score`` (Tier 2->4; null outside
        4-tier mode, and whenever volumes are unavailable — data-model.md
        §4.3/§4.4).
    """
    tier0_severity = parse_threats_severity(threats_content)
    tier0 = {
        "tier": 0,
        "label": "Threats Identified",
        "source": "threats.md Section 6",
        "ghost": False,
        "count": tier0_severity["total"],
        "volume": None,
        "severity_mix": {k: tier0_severity[k] for k in ("critical", "high", "medium", "low")},
        "width": 100,
    }

    if tier == 1:
        tiers, reductions, totals = _funnel_4tier_mode(cc_data, rs_content)
    elif tier == 2:
        tiers, reductions, totals = _funnel_3tier_mode(rs_content)
    else:
        tiers, reductions, totals = _funnel_threats_only_mode()

    risk_reduction, inherent_score, residual_score = totals
    return {
        "funnel_tiers": [tier0] + tiers,
        "reduction_percentages": reductions,
        "risk_reduction": risk_reduction,
        "inherent_score": inherent_score,
        "residual_score": residual_score,
    }


def _funnel_quantize(value):
    """Quantize a Decimal volume or percentage to 1 dp, ROUND_HALF_UP (PD-5)."""
    return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def _funnel_width(raw, lo, hi):
    """Clamp a raw Decimal width ratio to ``[lo, hi]``, then round half-up to int.

    FR-K11.5 / PD-4: the clamp bounds must be ``Decimal`` — ``min(max(x, 40),
    80)`` returns a bare ``int`` when a bound wins, and a following
    ``.quantize()`` on that bare int then raises.
    """
    clamped = min(max(raw, lo), hi)
    return int(clamped.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _funnel_reduction_pct(from_volume, to_volume):
    """(from - to) / from * 100, quantized to 1 dp. Zero denominator -> 0.0 (PD-5)."""
    if from_volume == 0:
        return Decimal("0.0")
    return _funnel_quantize((from_volume - to_volume) / from_volume * 100)


def _funnel_severity_mix(bands):
    """Count Title Case severity bands into a {critical, high, medium, low} mix.

    A falsy band (``None`` or ``""``) is skipped, so that row is absent from
    this mix only (data-model.md §4.1).
    """
    mix = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for band in bands:
        if not band:
            continue
        key = band.strip().lower()
        if key in mix:
            mix[key] += 1
    return mix


def _funnel_section1_comparand_warnings(cc_data, totals):
    """Warn per field (data-model.md §4.5) when compensating-controls.md's
    Section 1 stated total differs from the row-derived value by more than
    0.1. One line per differing field — never aggregated, since §4.5 is
    explicit this class is "per field, not aggregated" — and silent when
    either side is unavailable (no Section 1 line to compare against, or
    volumes unavailable so the row-derived side is None).
    """
    reduction, inherent, residual = totals
    fields = (
        ("inherent score", (cc_data or {}).get("inherent_score"), inherent, ""),
        ("residual score", (cc_data or {}).get("residual_score"), residual, ""),
        ("risk reduction", (cc_data or {}).get("risk_reduction"), reduction, "%"),
    )
    for label, stated, derived, suffix in fields:
        if stated is None or derived is None:
            continue
        if abs(stated - derived) > 0.1:
            print(
                f"Warning: controls Section 1 {label} {stated}{suffix} "
                f"differs from row-derived {derived}{suffix}; using rows",
                file=sys.stderr,
            )


def _funnel_4tier_mode(cc_data, rs_content=None):
    """JSON tiers 1-3 from the compensating-controls.md one row set (4-tier mode).

    V2 = sum(inherent), V3 = sum(residual if found else inherent), V4 =
    sum(residual), all over rows with an inherent score (data-model.md
    §4.1). Volumes are unavailable when no row carries one, or the
    quantized V2 is 0 (§4.3): every volume and reduction is null, and
    widths fall back to the plain STEP cascade, with one warning.

    Also emits two more data-model.md §4.5 warnings: a controls/risk-scores
    row-count mismatch when ``rs_content`` is supplied, and the Section 1
    comparand (:func:`_funnel_section1_comparand_warnings`).
    """
    findings = (cc_data or {}).get("findings", [])
    rows_with_inherent = [f for f in findings if f.get("inherent") is not None]

    v2 = v3 = v4 = None
    if rows_with_inherent:
        v2_candidate = _funnel_quantize(sum(f["inherent"] for f in rows_with_inherent))
        if v2_candidate != 0:
            v2 = v2_candidate
            v3 = _funnel_quantize(sum(
                (parse_score(f["residual_score"]) if f["status_class"] == "found" else f["inherent"])
                for f in rows_with_inherent
            ))
            v4 = _funnel_quantize(sum(parse_score(f["residual_score"]) for f in rows_with_inherent))
    volumes_available = v2 is not None

    if not volumes_available:
        print(
            "Warning: no controls row carries an inherent score; funnel "
            "volumes and risk reduction are unavailable",
            file=sys.stderr,
        )

    count = len(findings)
    if rs_content:
        rs_row_count = len(parse_risk_scores_findings(rs_content))
        if rs_row_count != count:
            print(
                f"Warning: controls rows ({count}) differ from risk-scores "
                f"rows ({rs_row_count})",
                file=sys.stderr,
            )
    tier1_mix = _funnel_severity_mix(f.get("inherent_severity") for f in findings)
    tier2_mix = _funnel_severity_mix(
        (f.get("residual_severity") if f.get("status_class") == "found" else f.get("inherent_severity"))
        for f in findings
    )
    tier3_mix = _funnel_severity_mix(f.get("residual_severity") for f in findings)

    w2 = 100 - int(_FUNNEL_STEP)
    if volumes_available:
        w3 = _funnel_width(
            Decimal(w2) * v3 / v2,
            _FUNNEL_FLOOR + _FUNNEL_STEP, Decimal(w2) - _FUNNEL_STEP,
        )
        w4 = _funnel_width(
            Decimal(w2) * v4 / v2,
            _FUNNEL_FLOOR, Decimal(w3) - _FUNNEL_STEP,
        )
    else:
        w3 = w2 - int(_FUNNEL_STEP)
        w4 = w3 - int(_FUNNEL_STEP)

    tiers = [
        {
            "tier": 1, "label": "Inherent Risk Scored", "source": "compensating-controls.md",
            "ghost": False, "count": count,
            "volume": float(v2) if v2 is not None else None,
            "severity_mix": tier1_mix, "width": w2,
        },
        {
            "tier": 2, "label": "Controls Applied", "source": "compensating-controls.md",
            "ghost": False, "count": count,
            "volume": float(v3) if v3 is not None else None,
            "severity_mix": tier2_mix, "width": w3,
        },
        {
            "tier": 3, "label": "Residual Risk", "source": "compensating-controls.md",
            "ghost": False, "count": count,
            "volume": float(v4) if v4 is not None else None,
            "severity_mix": tier3_mix, "width": w4,
        },
    ]
    reductions = [
        {"from_tier": 0, "to_tier": 1, "percentage": 0.0},
        {
            "from_tier": 1, "to_tier": 2,
            "percentage": float(_funnel_reduction_pct(v2, v3)) if volumes_available else None,
        },
        {
            "from_tier": 2, "to_tier": 3,
            "percentage": float(_funnel_reduction_pct(v3, v4)) if volumes_available else None,
        },
    ]
    if volumes_available:
        totals = (float(_funnel_reduction_pct(v2, v4)), float(v2), float(v4))
    else:
        totals = (None, None, None)

    _funnel_section1_comparand_warnings(cc_data, totals)

    return tiers, reductions, totals


def _funnel_3tier_mode(rs_content):
    """JSON tiers 1-2 from risk-scores.md; JSON tier 3 is always ghost (3-tier mode).

    V2 = sum(composite scores). JSON tier 2 ("Unmitigated Risk") volume
    mirrors V2 exactly, since no controls have been applied yet
    (data-model.md §4.1); the (1->2) reduction is therefore always 0.0 once
    that identity is in place. ``risk_reduction`` stays null: there is no
    residual data in 3-tier mode (data-model.md §4.4).
    """
    rs_findings = parse_risk_scores_findings(rs_content) if rs_content else []
    composites = [
        c for c in (parse_score(f.get("composite_score", "")) for f in rs_findings)
        if c is not None
    ]

    v2 = v3 = None
    if composites:
        v2_candidate = _funnel_quantize(sum(composites))
        if v2_candidate != 0:
            v2 = v2_candidate
            v3 = v2
            # AOD-SIMPLIFICATION: no dedicated warning on a degenerate
            # empty/zero-composite risk-scores.md in 3-tier mode — upgrade:
            # add a 3-tier-scoped warning stem if this proves common in the
            # field (data-model.md §4.3's stem is worded for the 4-tier
            # controls-row case only).
    volumes_available = v2 is not None

    count = len(rs_findings)
    tier1_mix = _funnel_severity_mix(f.get("severity", "") for f in rs_findings)
    tier2_mix = dict(tier1_mix)

    w2 = 100 - int(_FUNNEL_STEP)
    if volumes_available:
        w3 = _funnel_width(
            Decimal(w2) * v3 / v2,
            _FUNNEL_FLOOR + _FUNNEL_STEP, Decimal(w2) - _FUNNEL_STEP,
        )
    else:
        w3 = w2 - int(_FUNNEL_STEP)
    w4 = w3 - int(_FUNNEL_STEP)  # JSON tier 3 has no residual data; always ghost.

    tiers = [
        {
            "tier": 1, "label": "Inherent Risk Scored", "source": "risk-scores.md",
            "ghost": False, "count": count,
            "volume": float(v2) if v2 is not None else None,
            "severity_mix": tier1_mix, "width": w2,
        },
        {
            "tier": 2, "label": "Unmitigated Risk",
            "source": "risk-scores.md (no controls applied)",
            "ghost": False, "count": count,
            "volume": float(v3) if v3 is not None else None,
            "severity_mix": tier2_mix, "width": w3,
        },
        {
            "tier": 3, "label": "Residual Risk", "source": None, "ghost": True,
            "count": None, "volume": None, "severity_mix": None, "width": w4,
        },
    ]
    reductions = [
        {"from_tier": 0, "to_tier": 1, "percentage": 0.0},
        {
            "from_tier": 1, "to_tier": 2,
            "percentage": float(_funnel_reduction_pct(v2, v3)) if volumes_available else None,
        },
        {"from_tier": 2, "to_tier": 3, "percentage": None},
    ]
    return tiers, reductions, (None, None, None)


def _funnel_threats_only_mode():
    """JSON tiers 1-3 are all ghost (threats-only mode).

    Neither risk-scores.md nor compensating-controls.md is present. Widths
    follow the plain STEP cascade; every reduction is null because a ghost
    tier wins over "(0->1) is 0.0 by definition" (data-model.md §4.2).
    """
    w2 = 100 - int(_FUNNEL_STEP)
    w3 = w2 - int(_FUNNEL_STEP)
    w4 = w3 - int(_FUNNEL_STEP)
    tiers = [
        {
            "tier": 1, "label": "Inherent Risk Scored", "source": None, "ghost": True,
            "count": None, "volume": None, "severity_mix": None, "width": w2,
        },
        {
            "tier": 2, "label": "Controls Applied", "source": None, "ghost": True,
            "count": None, "volume": None, "severity_mix": None, "width": w3,
        },
        {
            "tier": 3, "label": "Residual Risk", "source": None, "ghost": True,
            "count": None, "volume": None, "severity_mix": None, "width": w4,
        },
    ]
    reductions = [
        {"from_tier": 0, "to_tier": 1, "percentage": None},
        {"from_tier": 1, "to_tier": 2, "percentage": None},
        {"from_tier": 2, "to_tier": 3, "percentage": None},
    ]
    return tiers, reductions, (None, None, None)


def _compute_missing_enrichments(artifacts):
    """Compute list of missing enrichment commands.

    Args:
        artifacts: Dict of detected artifact booleans.

    Returns:
        List of command strings for absent artifacts, ordered:
        /tachi.risk-score before /tachi.compensating-controls.
    """
    missing = []
    if not artifacts["risk_scores_md"]:
        missing.append("/tachi.risk-score")
    if not artifacts["compensating_controls_md"]:
        missing.append("/tachi.compensating-controls")
    return missing


# =============================================================================
# MAESTRO Layer Extraction (T003–T011)
# =============================================================================

# Alias for shared constant
_MAESTRO_LAYERS = MAESTRO_LAYERS


_MAESTRO_HEADING = r"^#{3,4}\s+Risk by MAESTRO Layer"


def parse_maestro_layer_distribution(threats_content):
    """Parse Section 6 "Risk by MAESTRO Layer" table.

    Matches the heading at level 3 or level 4 (K10, FR-K10.1): some inputs
    render it as ``### Risk by MAESTRO Layer`` rather than the canonical
    ``####``. Returns list of dicts: {layer_id, layer_name, finding_count,
    highest_severity}. Returns empty list if the table is absent (pre-084
    output).
    """
    start = match_heading(_MAESTRO_HEADING, threats_content)
    rows = parse_markdown_table(threats_content, start_line=start) if start is not None else []
    if not rows:
        return []

    result = []
    for row in rows:
        layer_raw = row.get("MAESTRO Layer", "").strip()
        if not layer_raw:
            continue
        # Parse "L1 — Foundation Model" → layer_id="L1", layer_name="Foundation Model"
        # Handle both em-dash (—) and en-dash (–) for robustness
        parts = layer_raw.split("—", 1)
        if len(parts) < 2:
            parts = layer_raw.split("–", 1)
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

        result.append({
            "layer_id": layer_id,
            "layer_name": layer_name,
            "finding_count": finding_count,
            "highest_severity": highest_severity,
        })

    return result


def parse_component_layer_mapping(threats_content):
    """Parse Section 1 Components table for MAESTRO Layer column.

    Returns dict mapping component_name → layer_string (e.g., "L1 — Foundation Model").
    Returns empty dict if no MAESTRO Layer column exists.
    """
    rows = parse_markdown_table(threats_content, "### Components")
    mapping = {}
    for row in rows:
        comp = row.get("Component", "").strip()
        layer = row.get("MAESTRO Layer", "").strip()
        if comp and layer:
            mapping[comp] = layer
    return mapping


def parse_per_finding_maestro(threats_content):
    """Parse Section 3 and Section 4 agent tables for per-finding MAESTRO layer.

    Returns list of dicts: {id, component, maestro_layer, risk_level, threat}.
    Handles both 8-column STRIDE tables and 9-column AI tables.
    Returns empty list if no MAESTRO data found.
    """
    lines = threats_content.split("\n")
    findings = []

    # Find all agent table subsections (### 3.X and ### 4.X, but not ### 4a)
    agent_sections = []
    for i, line in enumerate(lines):
        if re.match(r"^###\s+[34]\.\d+\s+", line):
            agent_sections.append(i)

    for sec_start in agent_sections:
        header_cols = None
        for i in range(sec_start + 1, len(lines)):
            stripped = lines[i].strip()
            # Stop at next section header
            if stripped.startswith("## ") or stripped.startswith("### "):
                break
            if not stripped.startswith("|"):
                continue
            # Parse header row
            if header_cols is None:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if cells and cells[0].lower() == "id":
                    header_cols = cells
                continue
            # Skip separator row
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            # Data row
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not cells or not cells[0]:
                continue
            fid = strip_bold(cells[0])
            if not fid or not re.match(r"^[A-Z]", fid):
                continue

            # Find MAESTRO Layer column index dynamically
            maestro_idx = None
            if header_cols:
                for idx, col in enumerate(header_cols):
                    if col == "MAESTRO Layer":
                        maestro_idx = idx
                        break

            maestro_layer = ""
            if maestro_idx is not None and maestro_idx < len(cells):
                maestro_layer = cells[maestro_idx].strip()

            # Determine other fields by header position
            comp_idx = None
            threat_idx = None
            risk_idx = None
            if header_cols:
                for idx, col in enumerate(header_cols):
                    if col == "Component":
                        comp_idx = idx
                    elif col == "Threat":
                        threat_idx = idx
                    elif col == "Risk Level":
                        risk_idx = idx

            component = cells[comp_idx].strip() if comp_idx is not None and comp_idx < len(cells) else ""
            threat = cells[threat_idx].strip() if threat_idx is not None and threat_idx < len(cells) else ""
            risk_level = cells[risk_idx].strip() if risk_idx is not None and risk_idx < len(cells) else ""

            findings.append({
                "id": fid,
                "component": component,
                "maestro_layer": maestro_layer,
                "risk_level": risk_level,
                "threat": threat,
            })

    return findings


def compute_maestro_heatmap(per_finding_data, component_layer_map):
    """Build component-layer intersection matrix.

    Each cell = highest severity at that (component, layer) pair.
    Components capped at top 10 by total finding count.

    Returns list of dicts: {component, layers: {L1: severity|null, ...}}.
    """
    # Build intersection grid: (component, layer_id) → highest severity
    grid = {}
    comp_counts = {}

    for f in per_finding_data:
        comp = f.get("component", "")
        layer_raw = f.get("maestro_layer", "")
        risk_level = f.get("risk_level", "")
        if not comp or not layer_raw:
            continue

        # Extract layer ID from "L1 — Foundation Model"
        layer_id = layer_raw.split("—")[0].strip().split("–")[0].strip()
        if layer_id not in _MAESTRO_LAYERS:
            continue

        comp_counts[comp] = comp_counts.get(comp, 0) + 1

        key = (comp, layer_id)
        existing = grid.get(key, "")
        if not existing or _SEVERITY_ORDINAL.get(risk_level, 0) > _SEVERITY_ORDINAL.get(existing, 0):
            grid[key] = risk_level

    # Sort components by finding count descending, name ascending
    sorted_comps = sorted(comp_counts.keys(), key=lambda c: (-comp_counts[c], c))

    # Cap at 10 components
    sorted_comps = sorted_comps[:10]

    result = []
    for comp in sorted_comps:
        layers = {}
        for lid in _MAESTRO_LAYERS:
            layers[lid] = grid.get((comp, lid), None)
        result.append({
            "component": comp,
            "layers": layers,
        })

    return result


def compute_most_exposed_layer(layer_distribution):
    """Determine the most-exposed MAESTRO layer.

    Layer with highest finding_count. Ties broken by highest severity, then layer_id ascending.

    Returns string like "L1 — Foundation Model" or "" if no data.
    """
    if not layer_distribution:
        return ""

    def sort_key(entry):
        return (
            -entry["finding_count"],
            -_SEVERITY_ORDINAL.get(entry["highest_severity"], 0),
            entry["layer_id"],
        )

    sorted_layers = sorted(layer_distribution, key=sort_key)
    top = sorted_layers[0]
    return f"{top['layer_id']} — {top['layer_name']}" if top["layer_name"] else top["layer_id"]


def extract_maestro_data(threats_content):
    """Extract all MAESTRO data from threats.md. Returns empty/null values when absent.

    Returns dict with:
      - maestro_layer_distribution: list of layer dicts
      - most_exposed_layer: string
      - component_layer_map: dict
      - per_finding_maestro: list of finding dicts
      - maestro_heatmap: list of component-layer intersection dicts
      - has_maestro_data: bool
    """
    layer_dist = parse_maestro_layer_distribution(threats_content)
    comp_layer_map = parse_component_layer_mapping(threats_content)
    per_finding = parse_per_finding_maestro(threats_content)
    heatmap = compute_maestro_heatmap(per_finding, comp_layer_map)
    most_exposed = compute_most_exposed_layer(layer_dist)

    has_data = bool(layer_dist) or any(f.get("maestro_layer") for f in per_finding)

    return {
        "maestro_layer_distribution": layer_dist,
        "most_exposed_layer": most_exposed,
        "component_layer_map": comp_layer_map,
        "per_finding_maestro": per_finding,
        "maestro_heatmap": heatmap,
        "has_maestro_data": has_data,
    }


# =============================================================================
# T018: Build JSON Output
# =============================================================================

def compute_allow_list(template, findings, scope, template_data=None, payload=None):
    """Compute the K15 allow-list (data-model.md §8, PD-17).

    ``finding_ids`` is exactly the set of IDs ``template``'s prompt renders:
    the full tier finding-ID set for baseball-card/system-architecture
    (either can name any finding), the per-layer top-findings IDs for
    maestro-stack (from ``template_data``), none for maestro-heatmap/
    risk-funnel (neither renders a finding ID), and the callout IDs for
    executive-architecture (from ``payload["callouts"]`` — that template
    builds its own payload rather than a ``template_data`` dict, so it is
    threaded through separately).

    ``component_names`` is one common set, identical for every template: the
    scope components, trust-zone members and zone names, data-flow
    endpoints, and the tier findings' ``component`` values. It does not
    reuse :func:`_compute_trust_zones`, which prints a "no trust zones"
    note on empty input — a second call here would double that note for
    templates that already call it (system-architecture, executive-
    architecture); the flat name/member extraction below is the plain
    parse of ``scope["trust_boundaries"]`` without the grouping or the
    print.

    Both lists are sorted, unique, with empty strings dropped.

    AR-3 (laziness-ladder rung 2): NOT a ``tachi_parsers.py`` shared helper
    — it has exactly one consumer, this file (extraction-data-contract.md).
    """
    if template in ("baseball-card", "system-architecture"):
        finding_ids = {f.get("id", "") for f in findings}
    elif template == "maestro-stack":
        finding_ids = {
            tf.get("id", "")
            for layer in (template_data or {}).get("per_layer_summaries", [])
            for tf in layer.get("top_findings", [])
        }
    elif template == "executive-architecture":
        finding_ids = {
            c.get("finding_id", "") for c in (payload or {}).get("callouts", [])
        }
    else:  # maestro-heatmap, risk-funnel: no finding ID is rendered
        finding_ids = set()

    component_names = {c.get("name", "") for c in scope.get("components", [])}
    for tb in scope.get("trust_boundaries", []):
        component_names.add(tb.get("zone", ""))
        component_names.update(
            c.strip() for c in tb.get("components", "").split(",") if c.strip()
        )
    for flow in scope.get("data_flows", []):
        component_names.add(flow.get("source", ""))
        component_names.add(flow.get("destination", ""))
    component_names.update(f.get("component", "") for f in findings)

    return {
        "finding_ids": sorted(fid for fid in finding_ids if fid),
        "component_names": sorted(name for name in component_names if name),
    }


def build_json_output(data, template):
    """Assemble the complete JSON output structure.

    Args:
        data: Dict containing all computed data.
        template: Template name string.

    Returns:
        JSON string with sort_keys=True, indent=2 for deterministic output.
    """
    output = {
        "metadata": data["metadata"],
        "severity_distribution": data["severity_distribution"],
        "heat_map": data["heat_map"],
        "top_findings": data["top_findings"],
        "template_data": data.get("template_data", {}),
        # K15 (T027, data-model.md §8): the top-level allow-list. Placed in
        # the initial literal, apart from the K13-posture lines below (LOW-4)
        # — a TW-6 revert of this commit then applies cleanly on top of the
        # K13-posture commit.
        "allow_list": data["allow_list"],
    }

    # Add delta data when baseline present
    if "delta" in data:
        output["delta"] = data["delta"]

    # Add prompt scaffold when extracted from template
    if "prompt_scaffold" in data:
        output["prompt_scaffold"] = data["prompt_scaffold"]

    # Add template to metadata
    output["metadata"]["template"] = template
    # K13-posture (T025, data-model.md §5): risk_posture_{level,label} in
    # every infographic JSON. Kept apart from where T027's top-level
    # `allow_list` key will land (near the `output = {...}` literal above),
    # so a future K15 revert never touches these two lines (LOW-4).
    output["metadata"]["risk_posture_level"] = data["risk_posture_level"]
    output["metadata"]["risk_posture_label"] = data["risk_posture_label"]

    return json.dumps(output, sort_keys=True, indent=2)


# =============================================================================
# T008: CLI & Main Pipeline
# =============================================================================

def main():
    """Main entry point: parse CLI, detect artifacts, compute, validate, write JSON."""
    parser = argparse.ArgumentParser(
        description="Extract structured infographic data from tachi pipeline artifacts."
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        help="Directory containing tachi pipeline markdown artifacts",
    )
    parser.add_argument(
        "--template",
        required=True,
        choices=["baseball-card", "system-architecture", "risk-funnel", "maestro-stack", "maestro-heatmap", "executive-architecture"],
        help="Infographic template to generate data for",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the JSON output file",
    )
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()
    output_path = Path(args.output).resolve()

    # Detect artifacts
    artifacts = detect_artifacts(target_dir)

    # Check threats.md exists (required for all templates)
    if not artifacts["threats_md"]:
        print(f"Error: threats.md not found in {target_dir}", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACT)

    # Determine tier
    tier = determine_tier(artifacts)

    # Pre-read artifact contents (each file read at most once)
    threats_content = (target_dir / "threats.md").read_text(encoding="utf-8")
    rs_content = None
    if artifacts["risk_scores_md"]:
        rs_content = (target_dir / "risk-scores.md").read_text(encoding="utf-8")
    cc_content = None
    if artifacts["compensating_controls_md"]:
        cc_content = (target_dir / "compensating-controls.md").read_text(encoding="utf-8")

    # Parse frontmatter and project name
    frontmatter = parse_frontmatter(threats_content)
    project_name = parse_project_name(threats_content, target_dir=target_dir)

    # Parse baseline metadata for delta-aware output
    baseline = parse_baseline_frontmatter(threats_content)
    has_baseline = baseline["has_baseline"]

    # Parse scope data
    scope = parse_scope_data(threats_content)

    # --- Core pipeline ---

    # Extract severity, findings, and cc_data
    severity, findings, cc_data = extract_severity(tier, threats_content, rs_content, cc_content)

    # K13-posture (T025, data-model.md §5): the single risk-posture rubric,
    # computed once from this tier's severity counts (residual after K11's
    # clamp at tier 1, inherent at tier 2, qualitative at tier 3) and reused
    # by both the executive-architecture early exit below and the regular
    # template path further down.
    risk_posture_level, risk_posture_label = compute_risk_posture(severity)

    if args.template == "executive-architecture":
        payload = _build_executive_architecture_payload(
            tier=_TIER_SOURCE_LABEL.get(tier, "threats"),
            findings=findings,
            scope_data=scope,
            source_file=(target_dir / "threats.md"),
            risk_posture_level=risk_posture_level,
            risk_posture_label=risk_posture_label,
        )

        if isinstance(payload, dict) and payload.get("error") == "no_scope_data":
            print(
                "[extract-infographic-data] ERROR: executive-architecture template "
                "requires parseable scope data (trust boundaries or DFD-type "
                "components); both are missing in threats.md",
                file=sys.stderr,
            )
            sys.exit(EXIT_VALIDATION_FAILURE)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, sort_keys=True, indent=2),
            encoding="utf-8",
        )
        print(
            "executive-architecture payload generated "
            f"({payload['severity_distribution']['total_qualifying']} Critical/High "
            f"findings, {len(payload['layers'])} layers, Tier {tier})",
            file=sys.stderr,
        )
        sys.exit(EXIT_SUCCESS)

    # Compute severity percentages
    severity_distribution = compute_severity_percentages(severity)

    # Compute heat map
    heat_map = compute_heat_map(findings, scope["components"], tier)

    # Select top findings
    top_findings = select_top_findings(findings, tier)

    # Build findings ID set (validation below, and the K12 scope warning).
    findings_ids = {f.get("id", "") for f in findings}

    # K12 (T017, data-model.md §6): stamp top_findings[].delta_status and
    # warn on a scope mismatch, on baseline runs only. delta_status_by_id is
    # called once here; its map is reused for delta_counts below (the same
    # normalized map on both call sites, FR-K12.1/K12.2).
    if has_baseline:
        status_by_id, has_status_column, row_count = delta_status_by_id(threats_content)
        if tier in (1, 2):
            # Tiers 1/2 findings carry no delta_status until stamped here —
            # unlike Tier 3, whose parse_threats_findings already sets it
            # per row, so Tier 3 keeps copying from `findings` below.
            apply_delta_status(top_findings, status_by_id)
        else:
            findings_by_id = {f.get("id", ""): f for f in findings}
            for tf in top_findings:
                source = findings_by_id.get(tf["id"], {})
                ds = source.get("delta_status", "")
                if ds:
                    tf["delta_status"] = ds
        warn_delta_scope(has_baseline, has_status_column, status_by_id, row_count, findings_ids)

    # Compute component risk weights
    risk_weights = compute_component_risk_weights(heat_map)

    # Compute metadata
    metadata = compute_metadata(
        threats_content, frontmatter, tier, severity, scope["components"], project_name
    )

    # Extract MAESTRO data only when needed (avoids unnecessary parsing for other templates)
    if args.template in ("maestro-stack", "maestro-heatmap"):
        maestro = extract_maestro_data(threats_content)
    else:
        maestro = {"has_maestro_data": False, "maestro_layer_distribution": [], "most_exposed_layer": "", "component_layer_map": {}, "per_finding_maestro": [], "maestro_heatmap": []}

    # K11 (T021, data-model.md §4.4/S-9): the baseball card and the funnel
    # share ONE computation of risk_reduction/inherent_score/residual_score
    # (row-derived, Tier 2->4) — computed once, here, so both surfaces agree
    # by construction and any volumes-unavailable (or other §4.5) warning
    # prints exactly once per run. Guarded to the two templates that need it.
    funnel = None
    if args.template in ("baseball-card", "risk-funnel"):
        funnel = compute_risk_funnel(tier, threats_content, cc_data=cc_data, rs_content=rs_content)

    # Build template-specific data
    template_data = {}
    if args.template == "baseball-card":
        # K11/S-9 (data-model.md §4.4): risk metrics are row-derived — the
        # same values the risk-funnel template emits — not Section 1's
        # stated figures. Null in 3-tier/threats-only modes and whenever
        # volumes are unavailable, same as the funnel (§4.3).
        template_data = {
            "risk_weights": risk_weights,
            "risk_reduction": funnel.get("risk_reduction"),
            "inherent_score": funnel.get("inherent_score"),
            "residual_score": funnel.get("residual_score"),
            "control_coverage_pct": cc_data.get("control_coverage_pct") if cc_data else None,
        }
    elif args.template == "system-architecture":
        arch_overlay = compute_architecture_overlay(scope, findings, tier, heat_map)
        template_data = {
            "risk_weights": risk_weights,
            "trust_zones": arch_overlay["trust_zones"],
            "data_flows": arch_overlay["data_flows"],
            "boundary_crossings": arch_overlay["boundary_crossings"],
        }
    elif args.template == "risk-funnel":
        # K11 (T021, data-model.md §4): `funnel` is computed once, above,
        # shared with the baseball-card branch (S-9). `missing_enrichments`
        # and `control_coverage_pct` are untouched legacy fields, not part
        # of §4 — computed directly here rather than threaded through
        # compute_risk_funnel's return shape.
        template_data = {
            "risk_weights": risk_weights,
            "funnel_tiers": funnel["funnel_tiers"],
            "reduction_percentages": funnel["reduction_percentages"],
            "missing_enrichments": _compute_missing_enrichments(artifacts),
            "risk_reduction": funnel.get("risk_reduction"),
            "inherent_score": funnel.get("inherent_score"),
            "residual_score": funnel.get("residual_score"),
            "control_coverage_pct": cc_data.get("control_coverage_pct") if cc_data else None,
        }
    elif args.template == "maestro-stack":
        # FR-003 backfill (LOCAL to this block — see FR-004): present all seven
        # canonical MAESTRO layers. Layers absent from the parsed Section-6 table
        # (table-less / pre-F-098 / partial input) are synthesized at
        # finding_count 0 so the rendered stack always shows L1..L7. This backfill
        # MUST stay local here and never enter the shared extract_maestro_data,
        # because the maestro-heatmap payload also carries
        # maestro_layer_distribution and must remain byte-identical (FR-004).
        #
        # Canonical layer names mirror populate-maestro-coverage.py:71-79 and the
        # segment the table parser produces (the part AFTER the em-dash in
        # "L1 — Foundation Model"), so backfilled names match parsed names.
        _MAESTRO_LAYER_NAMES = {
            "L1": "Foundation Model",
            "L2": "Data Operations",
            "L3": "Agent Framework",
            "L4": "Deployment Infrastructure",
            "L5": "Evaluation and Observability",
            "L6": "Security and Compliance",
            "L7": "Agent Ecosystem",
        }
        _parsed_by_id = {
            e["layer_id"]: e for e in maestro["maestro_layer_distribution"]
        }
        backfilled_distribution = []
        for lid in MAESTRO_LAYERS:
            if lid in _parsed_by_id:
                # D4 (ADR-047) backfill survival: a present row keeps its carried
                # Section-6 token verbatim — including the n/a token — so the merge
                # never overwrites an authored not_applicable back to clean/empty.
                backfilled_distribution.append(_parsed_by_id[lid])
            else:
                # Absent (table-less / pre-F-098 / partial input) layer: synthesize
                # at finding_count 0 with an empty token. The classifier maps the
                # empty token to "clean" (D4 default — preserves today's behavior
                # when applicability is unknowable; never silently "findings").
                backfilled_distribution.append({
                    "layer_id": lid,
                    "layer_name": _MAESTRO_LAYER_NAMES.get(lid, ""),
                    "finding_count": 0,
                    "highest_severity": "",
                })

        # Per-layer finding summaries: up to 2 top findings per layer. Driven by
        # the backfilled 7-entry distribution so every canonical layer gets a
        # summary (empty layers carry an empty top_findings list).
        per_layer_summaries = []
        for layer in backfilled_distribution:
            lid = layer["layer_id"]
            layer_findings = [
                f for f in maestro["per_finding_maestro"]
                if f.get("maestro_layer", "").startswith(lid)
            ]
            # Sort by severity descending, then ID ascending
            layer_findings.sort(
                key=lambda f: (-_SEVERITY_ORDINAL.get(f.get("risk_level", ""), 0), f.get("id", ""))
            )
            top_2 = layer_findings[:2]
            # coverage_state (ADR-047 D2 / D3 FENCE): the maestro-stack state is a
            # function of THIS layer's carried Section-6 token (finding_count +
            # highest_severity) via the shared classifier ALONE. It is deliberately
            # NOT derived from parse_component_layer_mapping()/component_layer_map —
            # that Section-1 derivation is fenced to the maestro-heatmap only
            # (consumed solely by compute_maestro_heatmap above). Routing it here
            # would reintroduce a second applicability authority and desync the
            # surfaces. coverage_state ∈ {findings, clean, not_applicable}.
            coverage_state = classify_maestro_coverage_state(
                layer["finding_count"], layer["highest_severity"]
            )
            per_layer_summaries.append({
                "layer_id": lid,
                "layer_name": layer["layer_name"],
                "finding_count": layer["finding_count"],
                "highest_severity": layer["highest_severity"],
                "coverage_state": coverage_state,
                "top_findings": [
                    {"id": f["id"], "threat": f["threat"][:120]} for f in top_2
                ],
            })

        # FR-002 code-computed counts (never agent-counted). Identity holds:
        # layers_with_findings + empty_layers == layer_count == 7.
        layers_with_findings = sum(
            1 for layer in backfilled_distribution if layer["finding_count"] > 0
        )
        layer_count = len(MAESTRO_LAYERS)  # always 7
        empty_layers = layer_count - layers_with_findings

        # NOTE (Architect LOW-8): {most_exposed_count} is intentionally NOT emitted
        # here — it is left agent-rendered and sits OUTSIDE FR-002's enumerated
        # count set (layers_with_findings / empty_layers / layer_count). Do not add
        # it to this payload without a corresponding spec change.
        template_data = {
            "maestro_layer_distribution": backfilled_distribution,
            "most_exposed_layer": maestro["most_exposed_layer"],
            "per_layer_summaries": per_layer_summaries,
            "has_maestro_data": maestro["has_maestro_data"],
            "layers_with_findings": layers_with_findings,
            "empty_layers": empty_layers,
            "layer_count": layer_count,
        }
    elif args.template == "maestro-heatmap":
        template_data = {
            "maestro_heatmap": maestro["maestro_heatmap"],
            "maestro_layer_distribution": maestro["maestro_layer_distribution"],
            "has_maestro_data": maestro["has_maestro_data"],
        }

    # K15 (T027, data-model.md §8): the allow-list this template's prompt is
    # permitted to render, computed once template_data is final (maestro-stack
    # reads its per_layer_summaries from it).
    allow_list = compute_allow_list(args.template, findings, scope, template_data)

    # Compute delta counts when baseline present. Counted over the
    # normalized Section 7 map (K12, FR-K12.1/K12.2), never over `findings`,
    # which has no delta_status key at all on Tier 1/2 and an unnormalized
    # one on Tier 3 (architect re-review NM-1). `status_by_id` was computed
    # once above, alongside the top_findings stamping and the scope warning
    # (T017); this call site reuses that same map for the counts.
    delta_data = None
    if has_baseline:
        resolved = parse_resolved_findings(threats_content)
        delta_data = {
            "has_baseline": True,
            "baseline_source": baseline["source"],
            "baseline_date": baseline["date"],
            "delta_counts": compute_delta_counts(status_by_id, resolved),
        }

    # Extract prompt scaffold from template file (Option D: locked styling,
    # flexible data narrative). The scaffold contains the opening aesthetic
    # instruction, STYLING DIRECTIVES, and closing statement — all the fixed
    # visual directives that must not be rewritten by the agent.
    scaffold = extract_prompt_scaffold(args.template)
    if scaffold["found"]:
        print(f"Prompt scaffold extracted from template ({args.template})", file=sys.stderr)

    # Assemble data dict
    data = {
        "metadata": metadata,
        "severity_distribution": severity_distribution,
        "heat_map": heat_map,
        "top_findings": top_findings,
        "findings_ids": findings_ids,
        "template_data": template_data,
        "allow_list": allow_list,
        "risk_posture_level": risk_posture_level,
        "risk_posture_label": risk_posture_label,
    }
    if scaffold["found"]:
        data["prompt_scaffold"] = {
            "preamble": scaffold["preamble"],
            "postamble": scaffold["postamble"],
        }
    if delta_data:
        data["delta"] = delta_data

    # Validate
    errors = validate_infographic(data)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        sys.exit(EXIT_VALIDATION_FAILURE)

    # Build JSON output
    json_output = build_json_output(data, args.template)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json_output, encoding="utf-8")

    finding_count = len(findings)
    print(
        f"infographic-data.json generated ({finding_count} findings, Tier {tier}, template={args.template})",
        file=sys.stderr,
    )
    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
