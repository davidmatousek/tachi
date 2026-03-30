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

from tachi_parsers import (
    EXIT_SUCCESS,
    EXIT_MISSING_ARTIFACT,
    EXIT_VALIDATION_FAILURE,
    escape_typst_string,
    parse_frontmatter,
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
    esc = escape_typst_string

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
