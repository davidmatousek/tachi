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
import os
import re
import sys
from pathlib import Path

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_ARTIFACT = 1
EXIT_VALIDATION_FAILURE = 2

# Severity ordering for deterministic output
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Note"]

# STRIDE prefix mapping for coverage matrix derivation
STRIDE_PREFIXES = {
    "S-": "Spoofing",
    "T-": "Tampering",
    "R-": "Repudiation",
    "I-": "Information Disclosure",
    "D-": "Denial of Service",
    "E-": "Elevation of Privilege",
    "AG-": "Agentic Threats",
    "LLM-": "LLM Threats",
}

# SLA mapping by severity for remediation actions
SLA_BY_SEVERITY = {
    "Critical": "7d",
    "High": "14d",
    "Medium": "30d",
    "Low": "90d",
}


# =============================================================================
# Utility Functions
# =============================================================================

def escape_typst_string(s: str) -> str:
    """Escape a string for Typst string literals.

    Handles: backslash -> \\, double quote -> \", newline -> \\n
    """
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    return s


def strip_bold(s: str) -> str:
    """Strip markdown bold markers (**) from a string."""
    return s.replace("**", "")


def parse_markdown_table(content: str, section_header: str) -> list:
    """Parse a markdown table found after a section header.

    Args:
        content: Full markdown file content.
        section_header: The section header to search for (e.g., "## 6. Risk Summary").

    Returns:
        List of dicts, one per row, with keys from the header row.
        Returns empty list if table not found.
    """
    lines = content.split("\n")
    # Find the section header
    header_idx = None
    for i, line in enumerate(lines):
        if section_header in line:
            header_idx = i
            break
    if header_idx is None:
        return []

    # Scan forward for the first table row (starts with |)
    table_header_idx = None
    for i in range(header_idx + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith("|") and "|" in line[1:]:
            table_header_idx = i
            break
        # Stop if we hit another section header
        if line.startswith("## ") or line.startswith("# "):
            break

    if table_header_idx is None:
        return []

    # Parse header row for column names
    header_line = lines[table_header_idx].strip()
    columns = [strip_bold(c.strip()) for c in header_line.split("|")[1:-1]]
    columns = [c for c in columns if c]  # Remove empty entries

    if not columns:
        return []

    # Skip separator row (|---|---|...)
    data_start = table_header_idx + 1
    if data_start < len(lines):
        sep_line = lines[data_start].strip()
        if re.match(r"^\|[\s\-:|]+\|$", sep_line):
            data_start += 1

    # Parse data rows
    rows = []
    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        if not line.startswith("|"):
            break
        cells = [strip_bold(c.strip()) for c in line.split("|")[1:-1]]
        if len(cells) < len(columns):
            print(f"Warning: skipping malformed row at line {i + 1}: expected {len(columns)} columns, got {len(cells)}", file=sys.stderr)
            continue
        row = {}
        for j, col in enumerate(columns):
            row[col] = cells[j] if j < len(cells) else ""
        rows.append(row)

    return rows


def _find_table_with_column(content: str, section_header: str, required_column: str) -> list:
    """Find a markdown table within a section that has a specific column header.

    Scans all tables after section_header and returns the first one
    whose header row contains required_column.
    """
    lines = content.split("\n")
    header_idx = None
    for i, line in enumerate(lines):
        if section_header in line:
            header_idx = i
            break
    if header_idx is None:
        return []

    section_end = len(lines)
    for i in range(header_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## ") or stripped.startswith("# "):
            section_end = i
            break

    i = header_idx + 1
    while i < section_end:
        stripped = lines[i].strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            columns = [strip_bold(c.strip()) for c in stripped.split("|")[1:-1]]
            columns = [c for c in columns if c]

            if columns and required_column in columns:
                # Found the right table — parse it
                data_start = i + 1
                if data_start < section_end:
                    sep = lines[data_start].strip()
                    if re.match(r"^\|[\s\-:|]+\|$", sep):
                        data_start += 1

                rows = []
                for j in range(data_start, section_end):
                    row_line = lines[j].strip()
                    if not row_line.startswith("|"):
                        break
                    cells = [strip_bold(c.strip()) for c in row_line.split("|")[1:-1]]
                    if len(cells) < len(columns):
                        continue
                    row = {}
                    for k, col in enumerate(columns):
                        row[col] = cells[k] if k < len(cells) else ""
                    rows.append(row)
                return rows

            # Wrong table — skip past it
            i += 1
            while i < section_end and lines[i].strip().startswith("|"):
                i += 1
            continue

        i += 1

    return []


# =============================================================================
# Frontmatter Parser
# =============================================================================

def parse_frontmatter(content: str) -> dict:
    """Extract key-value pairs from YAML frontmatter between --- delimiters.

    Handles both standard frontmatter and code-fenced frontmatter (```yaml ... ```).
    Only extracts top-level scalar values needed for the report.
    """
    result = {"date": "Unknown", "classification": None, "schema_version": "1.0"}

    # Try standard frontmatter first (--- ... ---)
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        # Try code-fenced frontmatter (```yaml\n---\n...\n---\n```)
        match = re.search(r"```yaml\s*\n---\s*\n(.*?)\n---\s*\n```", content, re.DOTALL)

    if not match:
        return result

    frontmatter_text = match.group(1)

    # Extract top-level key: value pairs (skip nested keys by checking indentation)
    for line in frontmatter_text.split("\n"):
        # Skip empty lines, comments, and indented (nested) lines
        if not line.strip() or line.strip().startswith("#") or line.startswith(" ") or line.startswith("\t"):
            continue
        kv_match = re.match(r'^(\w[\w_]*)\s*:\s*"?([^"]*?)"?\s*$', line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if key == "date":
                result["date"] = value
            elif key == "classification":
                result["classification"] = value if value else None
            elif key == "schema_version":
                result["schema_version"] = value

    return result


# =============================================================================
# Project Name Parser
# =============================================================================

def parse_project_name(content: str, title_override: str = None) -> str:
    """Extract project name from # Threat Model: {name} heading.

    Args:
        content: threats.md content.
        title_override: If provided, use this instead of auto-detected name.

    Returns:
        Project name string.
    """
    if title_override:
        return title_override

    match = re.search(r"^#\s+Threat Model:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return "Unknown Project"


# =============================================================================
# Artifact Detection
# =============================================================================

def detect_artifacts(target_dir: Path) -> dict:
    """Scan target directory for tachi pipeline artifacts.

    Returns dict with boolean flags for each artifact type.
    """
    artifacts = {
        "threats_md": False,
        "risk_scores_md": False,
        "compensating_controls_md": False,
        "threat_report_md": False,
        "funnel_image": False,
        "baseball_image": False,
        "architecture_image": False,
    }

    files = {
        "threats_md": "threats.md",
        "risk_scores_md": "risk-scores.md",
        "compensating_controls_md": "compensating-controls.md",
        "threat_report_md": "threat-report.md",
        "funnel_image": "threat-risk-funnel.jpg",
        "baseball_image": "threat-baseball-card.jpg",
        "architecture_image": "threat-system-architecture.jpg",
    }

    for key, filename in files.items():
        filepath = target_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            if size > 0:
                artifacts[key] = True
            else:
                print(f"Warning: skipping {filename}: file is empty (0 bytes)", file=sys.stderr)

    return artifacts


# =============================================================================
# Tier Selection
# =============================================================================

def determine_tier(artifacts: dict) -> int:
    """Determine data source tier from detected artifacts.

    Tier 1: compensating-controls.md exists
    Tier 2: risk-scores.md exists (no compensating-controls.md)
    Tier 3: threats.md only
    """
    if artifacts["compensating_controls_md"]:
        return 1
    elif artifacts["risk_scores_md"]:
        return 2
    else:
        return 3


# =============================================================================
# Severity Parsers
# =============================================================================

def parse_threats_severity(content: str) -> dict:
    """Parse Section 6 Risk Summary table from threats.md.

    Extracts Critical, High, Medium, Low, Note counts and total.
    Handles "N (M raw)" format in Total row — uses raw count.
    Note: Section 6 may contain a calibration matrix before the severity table.
    """
    rows = parse_markdown_table(content, "## 6. Risk Summary")
    # Section 6 may have a calibration matrix before the severity table.
    # Check if the found table has "Risk Level" column; if not, find the right one.
    if rows and "Risk Level" not in rows[0]:
        rows = _find_table_with_column(content, "## 6. Risk Summary", "Risk Level")
    if not rows:
        rows = parse_markdown_table(content, "Risk Summary")
    if rows and "Risk Level" not in rows[0]:
        rows = []
    if not rows:
        print("Warning: could not find Risk Summary table in threats.md", file=sys.stderr)
        return _empty_severity()

    return _accumulate_severity_rows(rows, "Risk Level")


def parse_risk_scores_severity(content: str) -> dict:
    """Parse risk-scores.md Section 1 severity distribution table.

    Preferred over threats.md when Tier 2.
    """
    rows = parse_markdown_table(content, "Severity Distribution")
    if not rows:
        rows = parse_markdown_table(content, "## 1. Executive Summary")
    if not rows:
        print("Warning: could not find severity distribution in risk-scores.md", file=sys.stderr)
        return _empty_severity()

    return _accumulate_severity_rows(rows, "Severity")


def _empty_severity() -> dict:
    """Create a zeroed severity dict derived from SEVERITY_ORDER."""
    sev = {s.lower(): 0 for s in SEVERITY_ORDER}
    sev["total"] = 0
    return sev


def _accumulate_severity_rows(rows: list, level_column: str) -> dict:
    """Accumulate severity counts from parsed table rows.

    Args:
        rows: List of row dicts from parse_markdown_table().
        level_column: Column name containing severity level (e.g., "Risk Level", "Severity").
    """
    severity = _empty_severity()
    for row in rows:
        level = row.get(level_column, "").strip()
        count_str = row.get("Count", "").strip()

        if level.lower() == "total" or level.startswith("Total"):
            total_match = re.match(r"(\d+)(?:\s*\((\d+)\s*raw\))?", count_str)
            if total_match:
                raw = total_match.group(2)
                severity["total"] = int(raw) if raw else int(total_match.group(1))
        else:
            key = level.lower()
            if key in severity:
                severity[key] = _parse_int(count_str)
    return severity


def _parse_int(s: str) -> int:
    """Safely parse an integer from a string, stripping non-numeric chars."""
    match = re.search(r"\d+", s)
    return int(match.group()) if match else 0


# =============================================================================
# Findings Parsers
# =============================================================================

def parse_threats_findings(content: str) -> list:
    """Parse Section 7 Recommended Actions table for Tier 3 findings.

    Returns list of finding dicts with Tier 3 keys.
    """
    rows = parse_markdown_table(content, "## 7. Recommended Actions")
    if not rows:
        print("Warning: could not find Recommended Actions table in threats.md", file=sys.stderr)
        return []

    findings = []
    for row in rows:
        findings.append({
            "id": row.get("Finding ID", "").strip(),
            "component": row.get("Component", "").strip(),
            "threat": row.get("Threat", "").strip(),
            "likelihood": "\u2014",  # em dash
            "impact": "\u2014",
            "risk_level": row.get("Risk Level", "").strip(),
            "mitigation": row.get("Mitigation", "").strip(),
        })
    return findings


def parse_risk_scores_findings(content: str) -> list:
    """Parse risk-scores.md Section 2 Scored Threat Table for Tier 2 findings."""
    rows = parse_markdown_table(content, "## 2. Scored Threat Table")
    if not rows:
        print("Warning: could not find Scored Threat Table in risk-scores.md", file=sys.stderr)
        return []

    findings = []
    for row in rows:
        findings.append({
            "id": row.get("ID", "").strip(),
            "component": row.get("Component", "").strip(),
            "threat": row.get("Threat", "").strip(),
            "composite_score": row.get("Composite", "").strip(),
            "severity": row.get("Severity", "").strip(),
            "cvss": row.get("CVSS", "").strip(),
            "exploitability": row.get("Exploit.", "").strip(),
        })
    return findings


# =============================================================================
# Component Distribution
# =============================================================================

def parse_component_distribution(findings: list) -> list:
    """Count findings per component, sorted by count descending."""
    counts = {}
    for f in findings:
        comp = f.get("component", "")
        if comp:
            counts[comp] = counts.get(comp, 0) + 1

    # Sort by count descending, then by name ascending for determinism
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))


# =============================================================================
# Scope Data Parser
# =============================================================================

def parse_scope_data(content: str) -> dict:
    """Parse scope data from threats.md Sections 1-2.

    Extracts components, data flows, trust zones, and boundary crossings.
    """
    result = {
        "components": [],
        "data_flows": [],
        "trust_boundaries": [],
        "boundary_crossings": [],
    }

    # Section 1: Components table
    comp_rows = parse_markdown_table(content, "### Components")
    for row in comp_rows:
        result["components"].append({
            "name": row.get("Component", "").strip(),
            "type": row.get("Type", "").strip(),
            "description": row.get("Description", "").strip(),
        })

    # Section 1: Data Flows table
    df_rows = parse_markdown_table(content, "### Data Flows")
    for row in df_rows:
        result["data_flows"].append({
            "source": row.get("Source", "").strip(),
            "destination": row.get("Destination", "").strip(),
            "data": row.get("Data", "").strip(),
            "protocol": row.get("Protocol", "").strip(),
        })

    # Section 2: Trust Zones table
    tz_rows = parse_markdown_table(content, "### Trust Zones")
    for row in tz_rows:
        result["trust_boundaries"].append({
            "zone": row.get("Zone", "").strip(),
            "trust-level": row.get("Trust Level", "").strip(),
            "components": row.get("Components", "").strip(),
        })

    # Section 2: Boundary Crossings table
    bc_rows = parse_markdown_table(content, "### Boundary Crossings")
    for row in bc_rows:
        result["boundary_crossings"].append({
            "crossing": row.get("Crossing", "").strip(),
            "from-zone": row.get("From Zone", "").strip(),
            "to-zone": row.get("To Zone", "").strip(),
            "components": row.get("Components", "").strip(),
            "controls": row.get("Controls", "").strip(),
        })

    if not result["components"] and not result["data_flows"]:
        print("Warning: scope data not found in threats.md — scope page will show limited data", file=sys.stderr)

    return result


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

    # Build executive narrative from: Risk Posture, Top 5 Threats, Key Recommendations
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
# Compensating Controls Parser (T022)
# =============================================================================

def parse_compensating_controls_md(content: str) -> dict:
    """Parse compensating-controls.md for Tier 1 data.

    Extracts:
    - Tier 1 findings from Section 2 Coverage Matrix (by residual severity)
    - STRIDE coverage matrix (derived from findings by threat ID prefix)
    - Coverage summary from Section 1 Coverage Distribution
    - Controls from Section 3 Control Details
    - Recommendations from Section 4 (merged into findings)
    - Severity counts from residual severity of findings
    """
    result = {
        "findings": [],
        "coverage_matrix": [],
        "controls": [],
        "coverage_summary": {"total-found": 0, "total-partial": 0, "total-missing": 0},
        "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0, "note": 0, "total": 0},
    }

    if not content or not content.strip():
        return result

    lines = content.split("\n")

    # ---- Section 4: Recommendations (parse first to merge into findings) ----
    recommendations = {}  # threat_id -> recommendation text
    sec4_start = None
    sec4_end = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^##\s+4\.\s+Recommendations", line):
            sec4_start = i + 1
        elif sec4_start is not None and re.match(r"^##\s+\d+\.", line):
            sec4_end = i
            break

    if sec4_start is not None:
        current_threat_id = None
        for i in range(sec4_start, sec4_end):
            line = lines[i].strip()
            # Match: #### 1. S-3 — Component (Composite: 9.2, Critical)
            heading_match = re.match(r"^####\s+\d+\.\s+(\S+)\s+[—\-]", line)
            if heading_match:
                current_threat_id = heading_match.group(1)
                continue
            # Match: **What to Implement**: text
            if current_threat_id and line.startswith("**What to Implement**:"):
                rec_text = line.replace("**What to Implement**:", "").strip()
                # Read continuation lines until next marker
                for j in range(i + 1, sec4_end):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith("**") or next_line.startswith("####") or next_line.startswith("###") or next_line.startswith("---"):
                        break
                    rec_text += " " + next_line
                recommendations[current_threat_id] = rec_text.strip()
                current_threat_id = None

    # ---- Section 2: Coverage Matrix findings ----
    for severity_label in ["Critical", "High", "Medium", "Low"]:
        header = f"### {severity_label} Residual Severity"
        rows = parse_markdown_table(content, header)
        for row in rows:
            threat_id = row.get("Threat ID", "").strip()
            result["findings"].append({
                "id": threat_id,
                "component": row.get("Component", "").strip(),
                "threat": row.get("Threat", "").strip(),
                "residual_score": row.get("Residual Score", "").strip(),
                "residual_severity": row.get("Residual Severity", severity_label).strip(),
                "control_status": row.get("Control Status", "").strip(),
                "recommendation": recommendations.get(threat_id, ""),
            })

    # ---- Compute Tier 1 severity counts from residual severity ----
    for f in result["findings"]:
        key = f["residual_severity"].lower()
        if key in result["severity"]:
            result["severity"][key] += 1
    result["severity"]["total"] = len(result["findings"])

    # ---- Derive STRIDE coverage matrix from findings ----
    stride_counts = {}
    for f in result["findings"]:
        fid = f["id"]
        category = None
        for prefix, cat_name in STRIDE_PREFIXES.items():
            if fid.startswith(prefix):
                category = cat_name
                break
        if category is None:
            category = "Other"

        if category not in stride_counts:
            stride_counts[category] = {"found": 0, "partial": 0, "missing": 0}

        status = f["control_status"].lower()
        if "partial" in status:
            stride_counts[category]["partial"] += 1
        elif "found" in status and "no" not in status:
            stride_counts[category]["found"] += 1
        else:
            stride_counts[category]["missing"] += 1

    stride_order = [
        "Spoofing", "Tampering", "Repudiation", "Information Disclosure",
        "Denial of Service", "Elevation of Privilege", "Agentic Threats", "LLM Threats",
    ]
    for cat in stride_order:
        if cat in stride_counts:
            result["coverage_matrix"].append({
                "category": cat,
                "found": stride_counts[cat]["found"],
                "partial": stride_counts[cat]["partial"],
                "missing": stride_counts[cat]["missing"],
            })
    if "Other" in stride_counts:
        result["coverage_matrix"].append({
            "category": "Other",
            "found": stride_counts["Other"]["found"],
            "partial": stride_counts["Other"]["partial"],
            "missing": stride_counts["Other"]["missing"],
        })

    # ---- Coverage Summary from Section 1 Coverage Distribution ----
    found_summary = False
    cov_rows = parse_markdown_table(content, "Coverage Distribution")
    if not cov_rows:
        cov_rows = parse_markdown_table(content, "## 1. Executive Summary")

    for row in cov_rows:
        status = row.get("Status", "").strip()
        count_str = row.get("Count", "").strip()
        count = _parse_int(count_str)

        if "Partial" in status:
            result["coverage_summary"]["total-partial"] = count
            found_summary = True
        elif "No Control" in status or "Missing" in status:
            result["coverage_summary"]["total-missing"] = count
            found_summary = True
        elif "Found" in status:
            result["coverage_summary"]["total-found"] = count
            found_summary = True

    # Fallback: derive from findings if table not found
    if not found_summary and result["findings"]:
        for f in result["findings"]:
            status = f["control_status"].lower()
            if "partial" in status:
                result["coverage_summary"]["total-partial"] += 1
            elif "found" in status and "no" not in status:
                result["coverage_summary"]["total-found"] += 1
            else:
                result["coverage_summary"]["total-missing"] += 1

    # ---- Section 3: Control Details ----
    sec3_start = None
    sec3_end = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^##\s+3\.\s+Control Details", line):
            sec3_start = i + 1
        elif sec3_start is not None and re.match(r"^##\s+\d+\.", line):
            sec3_end = i
            break

    if sec3_start is not None:
        current_category = ""
        i = sec3_start
        while i < sec3_end:
            line = lines[i].strip()

            # Category heading (### level)
            cat_match = re.match(r"^###\s+(.+)", line)
            if cat_match:
                current_category = cat_match.group(1).strip()
                i += 1
                continue

            # Control metadata: **Category**: X | **Status**: Y | **Effectiveness**: Z
            if "**Status**:" in line and "**Effectiveness**:" in line:
                status_match = re.search(r"\*\*Status\*\*:\s*([\w\s]+?)(?:\s*\||\s*$)", line)
                eff_match = re.search(r"\*\*Effectiveness\*\*:\s*(\w+)", line)
                cat_match2 = re.search(r"\*\*Category\*\*:\s*([\w\s/]+?)(?:\s*\||\s*$)", line)

                status = status_match.group(1).strip() if status_match else ""
                effectiveness = eff_match.group(1).strip() if eff_match else ""
                category = cat_match2.group(1).strip() if cat_match2 else current_category

                # Look ahead for evidence and component
                evidence = ""
                component = ""
                for j in range(i + 1, min(i + 30, sec3_end)):
                    next_line = lines[j].strip()
                    if next_line.startswith("####") or next_line.startswith("### "):
                        break
                    if "**Detected in**:" in next_line:
                        ev_match = re.search(r"\*\*Detected in\*\*:\s*`([^`]+)`", next_line)
                        if ev_match:
                            evidence = ev_match.group(1)
                    # Get component from first row of Threats Mitigated table
                    if "Threats Mitigated" in next_line:
                        k = j + 1
                        while k < sec3_end and not lines[k].strip().startswith("|"):
                            k += 1
                        # Skip header + separator (with bounds check)
                        if k + 2 < sec3_end:
                            k += 2
                        if k < sec3_end and lines[k].strip().startswith("|"):
                            cells = [c.strip() for c in lines[k].split("|")[1:-1]]
                            if len(cells) >= 2:
                                component = strip_bold(cells[1])

                result["controls"].append({
                    "component": component,
                    "category": category,
                    "status": status,
                    "evidence": evidence,
                    "effectiveness": effectiveness,
                })

            i += 1

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

def detect_images(target_dir: Path, template_dir: Path) -> dict:
    """Compute image paths relative to template directory."""
    # Compute relative path from template_dir to target_dir
    # Template files are at templates/tachi/security-report/
    # Images are at {target_dir}/threat-*.jpg
    # Relative path: ../../{target_dir}/
    try:
        rel_target = os.path.relpath(str(target_dir), str(template_dir))
    except ValueError:
        # Fallback for cross-drive paths on Windows
        rel_target = str(target_dir)

    images = {
        "funnel_image_path": "",
        "baseball_image_path": "",
        "architecture_image_path": "",
    }

    image_files = {
        "funnel_image_path": "threat-risk-funnel.jpg",
        "baseball_image_path": "threat-baseball-card.jpg",
        "architecture_image_path": "threat-system-architecture.jpg",
    }

    for key, filename in image_files.items():
        filepath = target_dir / filename
        if filepath.exists() and filepath.stat().st_size > 0:
            images[key] = rel_target + "/" + filename

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

    # 3p: Page Visibility
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
    esc = escape_typst_string  # shorthand

    def _v(key, default=""):
        return esc(f.get(key, default))

    if tier == 1:
        return (
            'id: "' + _v("id") + '", '
            'component: "' + _v("component") + '", '
            'threat: "' + _v("threat") + '", '
            'residual_score: "' + _v("residual_score") + '", '
            'residual_severity: "' + _v("residual_severity") + '", '
            'control_status: "' + _v("control_status") + '", '
            'recommendation: "' + _v("recommendation") + '"'
        )
    elif tier == 2:
        return (
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
        return (
            'id: "' + _v("id") + '", '
            'component: "' + _v("component") + '", '
            'threat: "' + _v("threat") + '", '
            'likelihood: "' + _v("likelihood", em_dash) + '", '
            'impact: "' + _v("impact", em_dash) + '", '
            'risk_level: "' + _v("risk_level") + '", '
            'mitigation: "' + _v("mitigation") + '"'
        )


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
    project_name = parse_project_name(threats_content, args.title)

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
