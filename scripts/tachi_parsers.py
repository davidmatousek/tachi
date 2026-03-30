"""Shared parser module for tachi pipeline artifacts.

Provides deterministic parsers for markdown tables, YAML frontmatter, severity
distributions, findings, scope data, and compensating controls extracted from
tachi pipeline outputs (threats.md, risk-scores.md, compensating-controls.md).

Used by extract-report-data.py and extract-infographic-data.py to ensure
consistent, cross-output-identical parsing of the same source artifacts.
"""

import re
import sys
from pathlib import Path

# =============================================================================
# Shared Constants
# =============================================================================

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


def _parse_int(s: str) -> int:
    """Safely parse an integer from a string, stripping non-numeric chars."""
    match = re.search(r"\d+", s)
    return int(match.group()) if match else 0


# =============================================================================
# Generic Table Parsers
# =============================================================================

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
                # Found the right table -- parse it
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

            # Wrong table -- skip past it
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
    Handles "N (M raw)" format in Total row -- uses raw count.
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
# Compensating Controls Parser
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
            # Match: #### 1. S-3 -- Component (Composite: 9.2, Critical)
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
