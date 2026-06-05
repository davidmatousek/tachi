use std::collections::{BTreeMap, HashMap, HashSet};

use crate::parsers::{parse_markdown_table, strip_bold, SeverityCounts};

const STRIDE_PREFIXES: [(&str, &str); 8] = [
    ("S-", "Spoofing"),
    ("T-", "Tampering"),
    ("R-", "Repudiation"),
    ("I-", "Information Disclosure"),
    ("D-", "Denial of Service"),
    ("E-", "Elevation of Privilege"),
    ("AG-", "Agentic Threats"),
    ("LLM-", "LLM Threats"),
];

#[derive(Debug, Clone, PartialEq, Default)]
pub struct CompensatingControlsData {
    pub findings: Vec<CompensatingControlFinding>,
    pub coverage_matrix: Vec<CoverageMatrixRow>,
    pub controls: Vec<CoverageControl>,
    pub coverage_summary: CoverageSummary,
    pub severity: SeverityCounts,
    pub risk_reduction: Option<f64>,
    pub inherent_score: Option<f64>,
    pub residual_score: Option<f64>,
    pub control_coverage_pct: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct CompensatingControlFinding {
    pub id: String,
    pub component: String,
    pub threat: String,
    pub residual_score: String,
    pub residual_severity: String,
    pub control_status: String,
    pub recommendation: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct CoverageMatrixRow {
    pub category: String,
    pub found: usize,
    pub partial: usize,
    pub missing: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct CoverageControl {
    pub component: String,
    pub category: String,
    pub status: String,
    pub evidence: String,
    pub effectiveness: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct CoverageSummary {
    pub total_found: usize,
    pub total_partial: usize,
    pub total_missing: usize,
}

pub fn parse_compensating_controls_md(content: &str) -> CompensatingControlsData {
    let mut result = CompensatingControlsData::default();

    if content.trim().is_empty() {
        return result;
    }

    result.inherent_score = parse_metric_pair(content, "**Risk Reduction**:", 0);
    result.residual_score = parse_metric_pair(content, "**Risk Reduction**:", 1);
    result.risk_reduction = parse_metric_pair(content, "**Risk Reduction**:", 2);
    result.control_coverage_pct = parse_metric_percent(content, "**Coverage**:");

    let mut recommendations = HashMap::<String, String>::new();
    if let Some((start, end)) = section_bounds(content, "## 4. Recommendations") {
        let lines: Vec<&str> = content.split('\n').collect();
        let mut current_threat_id: Option<String> = None;

        let mut index = start;
        while index < end {
            let line = lines[index].trim();
            if let Some(threat_id) = parse_recommendation_heading(line) {
                current_threat_id = Some(threat_id);
                index += 1;
                continue;
            }

            if let Some(threat_id) = current_threat_id.clone() {
                if let Some(rec_text) = line.strip_prefix("**What to Implement**:") {
                    let mut text = rec_text.trim().to_string();
                    let mut lookahead = index + 1;
                    while lookahead < end {
                        let next_line = lines[lookahead].trim();
                        if next_line.is_empty()
                            || next_line.starts_with("**")
                            || next_line.starts_with("####")
                            || next_line.starts_with("###")
                            || next_line.starts_with("---")
                        {
                            break;
                        }
                        if !text.is_empty() {
                            text.push(' ');
                        }
                        text.push_str(next_line);
                        lookahead += 1;
                    }
                    recommendations.insert(threat_id, text.trim().to_string());
                    current_threat_id = None;
                    index = lookahead;
                    continue;
                }
            }

            index += 1;
        }
    }

    let mut findings = Vec::new();
    let mut seen_ids = HashSet::<String>::new();
    let mut misclassified_count = 0usize;

    for severity_label in ["Critical", "High", "Medium", "Low"] {
        let header = format!("### {severity_label} Residual Severity");
        for row in parse_markdown_table(content, &header) {
            let threat_id = row.get("Threat ID").cloned().unwrap_or_default();
            let residual_score = row.get("Residual Score").cloned().unwrap_or_default();
            let row_severity = row.get("Residual Severity").cloned().unwrap_or_default();
            let score_band = score_to_band(&residual_score);

            let resolved_severity = if let Some(score_band) = score_band {
                if score_band != severity_label {
                    misclassified_count += 1;
                }
                score_band
            } else if row_severity.is_empty() {
                severity_label.to_string()
            } else {
                row_severity
            };

            if !seen_ids.insert(threat_id.clone()) {
                continue;
            }

            findings.push(CompensatingControlFinding {
                id: threat_id.clone(),
                component: row.get("Component").cloned().unwrap_or_default(),
                threat: row.get("Threat").cloned().unwrap_or_default(),
                residual_score,
                residual_severity: resolved_severity,
                control_status: row.get("Control Status").cloned().unwrap_or_default(),
                recommendation: recommendations.get(&threat_id).cloned().unwrap_or_default(),
            });
        }
    }

    if misclassified_count > 0 {
        let _ = misclassified_count;
    }

    result.severity.total = findings.len();
    for finding in &findings {
        match finding.residual_severity.as_str() {
            "Critical" => result.severity.critical += 1,
            "High" => result.severity.high += 1,
            "Medium" => result.severity.medium += 1,
            "Low" => result.severity.low += 1,
            "Note" => result.severity.note += 1,
            _ => {}
        }
    }

    let mut stride_counts: BTreeMap<String, CoverageMatrixRow> = BTreeMap::new();
    for finding in &findings {
        let category = stride_category_for_id(&finding.id);
        let entry = stride_counts
            .entry(category.clone())
            .or_insert_with(|| CoverageMatrixRow {
                category: category.clone(),
                found: 0,
                partial: 0,
                missing: 0,
            });

        let status = finding.control_status.to_ascii_lowercase();
        if status.contains("partial") {
            entry.partial += 1;
        } else if status.contains("found") && !status.contains("no") {
            entry.found += 1;
        } else {
            entry.missing += 1;
        }
    }

    for (_, category) in STRIDE_PREFIXES {
        if let Some(row) = stride_counts.remove(category) {
            result.coverage_matrix.push(row);
        }
    }
    if let Some(row) = stride_counts.remove("Other") {
        result.coverage_matrix.push(row);
    }

    let coverage_rows = parse_markdown_table(content, "Coverage Distribution");
    let coverage_rows = if coverage_rows.is_empty() {
        parse_markdown_table(content, "## 1. Executive Summary")
    } else {
        coverage_rows
    };

    let mut found_summary = false;
    for row in coverage_rows {
        let status = row.get("Status").cloned().unwrap_or_default();
        let count = parse_int(row.get("Count").map(String::as_str).unwrap_or_default());
        if status.contains("Partial") {
            result.coverage_summary.total_partial = count;
            found_summary = true;
        } else if status.contains("No Control") || status.contains("Missing") {
            result.coverage_summary.total_missing = count;
            found_summary = true;
        } else if status.contains("Found") {
            result.coverage_summary.total_found = count;
            found_summary = true;
        }
    }

    if !found_summary && !findings.is_empty() {
        for finding in &findings {
            let status = finding.control_status.to_ascii_lowercase();
            if status.contains("partial") {
                result.coverage_summary.total_partial += 1;
            } else if status.contains("found") && !status.contains("no") {
                result.coverage_summary.total_found += 1;
            } else {
                result.coverage_summary.total_missing += 1;
            }
        }
    }

    if let Some((start, end)) = section_bounds(content, "## 3. Control Details") {
        let lines: Vec<&str> = content.split('\n').collect();
        let mut current_category = String::new();
        let mut index = start;

        while index < end {
            let line = lines[index].trim();

            if let Some(category) = line.strip_prefix("### ") {
                current_category = category.trim().to_string();
                index += 1;
                continue;
            }

            if line.contains("**Status**:") && line.contains("**Effectiveness**:") {
                let status = extract_field(line, "**Status**:").unwrap_or_default();
                let effectiveness = extract_field(line, "**Effectiveness**:").unwrap_or_default();
                let category = extract_field(line, "**Category**:")
                    .unwrap_or_else(|| current_category.clone());

                let mut evidence = String::new();
                let mut component = String::new();
                let mut lookahead = index + 1;
                while lookahead < end {
                    let next_line = lines[lookahead].trim();
                    if next_line.starts_with("####") || next_line.starts_with("### ") {
                        break;
                    }
                    if let Some(value) = next_line.strip_prefix("**Detected in**:") {
                        evidence = value.trim().trim_matches('`').trim().to_string();
                    }

                    if next_line.contains("Threats Mitigated") {
                        let mut table_index = lookahead + 1;
                        while table_index < end && !lines[table_index].trim().starts_with('|') {
                            table_index += 1;
                        }
                        if table_index + 2 < end {
                            table_index += 2;
                        }
                        if table_index < end && lines[table_index].trim().starts_with('|') {
                            let cells = split_table_row(lines[table_index]);
                            if cells.len() >= 2 {
                                component = strip_bold(&cells[1]);
                            }
                        }
                    }

                    lookahead += 1;
                }

                result.controls.push(CoverageControl {
                    component,
                    category,
                    status,
                    evidence,
                    effectiveness,
                });
            }

            index += 1;
        }
    }

    result.findings = findings;
    result
}

fn score_to_band(score_str: &str) -> Option<String> {
    let score = score_str.parse::<f64>().ok()?;
    if score >= 9.0 {
        Some(String::from("Critical"))
    } else if score >= 7.0 {
        Some(String::from("High"))
    } else if score >= 4.0 {
        Some(String::from("Medium"))
    } else {
        Some(String::from("Low"))
    }
}

fn section_bounds(content: &str, section_heading: &str) -> Option<(usize, usize)> {
    let lines: Vec<&str> = content.split('\n').collect();
    let mut start = None;
    let mut end = lines.len();

    for (index, line) in lines.iter().enumerate() {
        if line.trim() == section_heading {
            start = Some(index + 1);
        } else if start.is_some()
            && line.trim_start().starts_with("## ")
            && line.trim() != section_heading
        {
            end = index;
            break;
        }
    }

    start.map(|start| (start, end))
}

fn parse_metric_pair(content: &str, marker: &str, index: usize) -> Option<f64> {
    let line = content.lines().find(|line| line.contains(marker))?;
    let after_marker = line.split_once(marker)?.1.trim();
    let mut parts = after_marker.split("->");
    let inherent = parts
        .next()?
        .split_whitespace()
        .next()?
        .parse::<f64>()
        .ok()?;
    let residual_part = parts.next()?.trim();
    let residual = residual_part
        .split_whitespace()
        .next()?
        .parse::<f64>()
        .ok()?;
    let reduction = line
        .split("(**")
        .nth(1)
        .and_then(|part| part.split('%').next())
        .and_then(|part| part.parse::<f64>().ok())?;

    match index {
        0 => Some(inherent),
        1 => Some(residual),
        2 => Some(reduction),
        _ => None,
    }
}

fn parse_metric_percent(content: &str, marker: &str) -> Option<f64> {
    let line = content.lines().find(|line| line.contains(marker))?;
    let after_marker = line.split_once(marker)?.1.trim();
    let percent_part = after_marker.split('%').next()?.trim();
    percent_part.split_whitespace().next()?.parse::<f64>().ok()
}

fn parse_recommendation_heading(line: &str) -> Option<String> {
    let heading = line.strip_prefix("#### ")?;
    let (_, rest) = heading.split_once(". ")?;
    Some(rest.split_whitespace().next()?.to_string())
}

fn extract_field(line: &str, marker: &str) -> Option<String> {
    let start = line.find(marker)? + marker.len();
    let rest = line[start..].trim();
    Some(rest.split('|').next().unwrap_or(rest).trim().to_string())
}

fn parse_int(s: &str) -> usize {
    let digits: String = s.chars().filter(|ch| ch.is_ascii_digit()).collect();
    digits.parse::<usize>().unwrap_or(0)
}

fn split_table_row(line: &str) -> Vec<String> {
    line.trim()
        .trim_matches('|')
        .split('|')
        .map(|cell| cell.trim().to_string())
        .collect()
}

fn stride_category_for_id(id: &str) -> String {
    for (prefix, category) in STRIDE_PREFIXES {
        if id.starts_with(prefix) {
            return category.to_string();
        }
    }
    String::from("Other")
}
