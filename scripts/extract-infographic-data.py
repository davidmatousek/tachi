#!/usr/bin/env python3
"""Deterministic extraction of structured infographic data from tachi pipeline markdown artifacts.

Reads threats.md, risk-scores.md, and compensating-controls.md from a target
directory and writes a JSON data file with all variable bindings needed by
the infographic templates (baseball-card, system-architecture, risk-funnel).

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
import os
import re
import sys
from pathlib import Path

# Ensure tachi_parsers is importable from the same directory as this script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tachi_parsers import (
    EXIT_SUCCESS,
    EXIT_MISSING_ARTIFACT,
    EXIT_VALIDATION_FAILURE,
    SEVERITY_ORDER,
    STRIDE_PREFIXES,
    parse_markdown_table,
    _find_table_with_column,
    parse_frontmatter,
    parse_project_name,
    detect_artifacts,
    determine_tier,
    parse_threats_severity,
    parse_risk_scores_severity,
    _empty_severity,
    _accumulate_severity_rows,
    _parse_int,
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

# Severity ordinal for Tier 3 scoring
_SEVERITY_ORDINAL = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Note": 0}


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

def extract_severity(target_dir, tier, threats_content, artifacts):
    """Extract severity counts, findings, and compensating controls data based on tier.

    Args:
        target_dir: Path to directory containing pipeline artifacts.
        tier: Data source tier (1, 2, or 3).
        threats_content: Full text content of threats.md.
        artifacts: Dict of detected artifact booleans.

    Returns:
        Tuple of (severity_dict, findings_list, cc_data_or_None).
        - severity_dict: {critical, high, medium, low, note, total}
        - findings_list: List of finding dicts (structure varies by tier)
        - cc_data: Full compensating controls data for Tier 1, None otherwise
    """
    cc_data = None

    if tier == 1:
        cc_content = (target_dir / "compensating-controls.md").read_text(encoding="utf-8")
        cc_data = parse_compensating_controls_md(cc_content)
        severity = cc_data["severity"]
        findings = cc_data["findings"]
    elif tier == 2:
        rs_content = (target_dir / "risk-scores.md").read_text(encoding="utf-8")
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
# T029-T031: Risk Funnel Computation
# =============================================================================

def compute_risk_funnel(target_dir, tier, severity, threats_content, artifacts):
    """Compute 4-tier risk funnel data with reduction percentages and missing enrichments.

    Tier 0: Total threats from threats.md Section 6 Risk Summary.
    Tier 1: Count from risk-scores.md severity distribution (null if absent).
    Tier 2: Count from compensating-controls.md findings (null if absent).
    Tier 3: Residual risk count — sum of residual severity (Critical+High+Medium+Low)
             from compensating-controls.md (null if absent).

    Args:
        target_dir: Path to directory containing pipeline artifacts.
        tier: Data source tier (1, 2, or 3).
        severity: Current severity dict (from extract_severity, used for Tier 3 residual).
        threats_content: Full text content of threats.md.
        artifacts: Dict of detected artifact booleans.

    Returns:
        Dict with funnel_tiers, reduction_percentages, and missing_enrichments.
    """
    # --- Tier 0: Threats Identified (always available) ---
    tier0_severity = parse_threats_severity(threats_content)
    tier0_count = tier0_severity["total"]
    tier0 = {
        "tier": 0,
        "label": "Threats Identified",
        "count": tier0_count,
        "source": "threats.md Section 6",
    }

    # --- Tier 1: Inherent Risk Scored (risk-scores.md) ---
    tier1 = None
    if artifacts["risk_scores_md"]:
        rs_content = (target_dir / "risk-scores.md").read_text(encoding="utf-8")
        rs_severity = parse_risk_scores_severity(rs_content)
        tier1 = {
            "tier": 1,
            "label": "Inherent Risk Scored",
            "count": rs_severity["total"],
            "source": "risk-scores.md",
        }

    # --- Tier 2: Controls Applied (compensating-controls.md) ---
    tier2 = None
    if artifacts["compensating_controls_md"]:
        cc_content = (target_dir / "compensating-controls.md").read_text(encoding="utf-8")
        cc_data = parse_compensating_controls_md(cc_content)
        tier2 = {
            "tier": 2,
            "label": "Controls Applied",
            "count": cc_data["severity"]["total"],
            "source": "compensating-controls.md",
        }

    # --- Tier 3: Residual Risk (compensating-controls.md residual severity) ---
    tier3 = None
    if artifacts["compensating_controls_md"]:
        # Residual risk = sum of Critical+High+Medium+Low (excluding Note)
        # Use cc_data already parsed for Tier 2
        cc_sev = cc_data["severity"]
        residual_count = cc_sev["critical"] + cc_sev["high"] + cc_sev["medium"] + cc_sev["low"]
        tier3 = {
            "tier": 3,
            "label": "Residual Risk",
            "count": residual_count,
            "source": "compensating-controls.md residual",
        }

    funnel_tiers = [tier0, tier1, tier2, tier3]

    # --- T030: Reduction percentages between adjacent non-null tiers ---
    reduction_percentages = _compute_reduction_percentages(funnel_tiers)

    # --- T031: Missing enrichments ---
    missing_enrichments = _compute_missing_enrichments(artifacts)

    return {
        "funnel_tiers": funnel_tiers,
        "reduction_percentages": reduction_percentages,
        "missing_enrichments": missing_enrichments,
    }


def _compute_reduction_percentages(funnel_tiers):
    """Compute percentage reduction between adjacent non-null funnel tiers.

    Each reduction is an individual value (not a distribution summing to a target),
    so standard rounding is used: int(round(pct)).

    Args:
        funnel_tiers: List of 4 tier dicts (some may be None).

    Returns:
        List of dicts with from_tier, to_tier, percentage (integer).
    """
    # Collect non-null tiers in order
    non_null = [t for t in funnel_tiers if t is not None]

    reductions = []
    for i in range(len(non_null) - 1):
        prev = non_null[i]
        curr = non_null[i + 1]

        prev_count = prev["count"]
        curr_count = curr["count"]

        if prev_count == 0:
            pct = 0
        else:
            pct = int(round(((prev_count - curr_count) / prev_count) * 100))

        reductions.append({
            "from_tier": prev["tier"],
            "to_tier": curr["tier"],
            "percentage": pct,
        })

    return reductions


def _compute_missing_enrichments(artifacts):
    """Compute list of missing enrichment commands.

    Args:
        artifacts: Dict of detected artifact booleans.

    Returns:
        List of command strings for absent artifacts, ordered:
        /risk-score before /compensating-controls.
    """
    missing = []
    if not artifacts["risk_scores_md"]:
        missing.append("/risk-score")
    if not artifacts["compensating_controls_md"]:
        missing.append("/compensating-controls")
    return missing


# =============================================================================
# T018: Build JSON Output
# =============================================================================

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
    }

    # Add template to metadata
    output["metadata"]["template"] = template

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
        choices=["baseball-card", "system-architecture", "risk-funnel"],
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

    # Read threats.md content
    threats_content = (target_dir / "threats.md").read_text(encoding="utf-8")

    # Parse frontmatter and project name
    frontmatter = parse_frontmatter(threats_content)
    project_name = parse_project_name(threats_content)

    # Parse scope data
    scope = parse_scope_data(threats_content)

    # --- Core pipeline ---

    # Extract severity, findings, and cc_data
    severity, findings, cc_data = extract_severity(target_dir, tier, threats_content, artifacts)

    # Compute severity percentages
    severity_distribution = compute_severity_percentages(severity)

    # Compute heat map
    heat_map = compute_heat_map(findings, scope["components"], tier)

    # Select top findings
    top_findings = select_top_findings(findings, tier)

    # Compute component risk weights
    risk_weights = compute_component_risk_weights(heat_map)

    # Deduplicate findings for ID validation
    dedup = deduplicate_findings(threats_content)

    # Build findings ID set for validation (from actual parsed findings)
    findings_ids = {f.get("id", "") for f in findings}

    # Compute metadata
    metadata = compute_metadata(
        threats_content, frontmatter, tier, severity, scope["components"], project_name
    )

    # Build template-specific data
    template_data = {}
    if args.template == "baseball-card":
        template_data = {"risk_weights": risk_weights}
    elif args.template == "system-architecture":
        arch_overlay = compute_architecture_overlay(scope, findings, tier, heat_map)
        template_data = {
            "risk_weights": risk_weights,
            "trust_zones": arch_overlay["trust_zones"],
            "data_flows": arch_overlay["data_flows"],
            "boundary_crossings": arch_overlay["boundary_crossings"],
        }
    elif args.template == "risk-funnel":
        funnel = compute_risk_funnel(target_dir, tier, severity, threats_content, artifacts)
        template_data = {
            "risk_weights": risk_weights,
            "funnel_tiers": funnel["funnel_tiers"],
            "reduction_percentages": funnel["reduction_percentages"],
            "missing_enrichments": funnel["missing_enrichments"],
        }

    # Assemble data dict
    data = {
        "metadata": metadata,
        "severity_distribution": severity_distribution,
        "heat_map": heat_map,
        "top_findings": top_findings,
        "findings_ids": findings_ids,
        "template_data": template_data,
    }

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
