use std::collections::BTreeMap;

use crate::parsers::{parse_markdown_table, ThreatFinding};

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct ThreatReportData {
    pub executive_narrative: Option<String>,
    pub remediation_timeline: Vec<RemediationTimelineEntry>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RemediationTimelineEntry {
    pub timeline: String,
    pub count: usize,
    pub severity: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct RemediationFinding {
    pub id: String,
    pub threat: String,
    pub recommendation: String,
    pub control_status: String,
    pub residual_severity: String,
    pub severity: String,
    pub risk_level: String,
    pub mitigation: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RemediationAction {
    pub severity: String,
    pub finding_id: String,
    pub finding_name: String,
    pub recommendation: String,
    pub sla: String,
    pub status: String,
}

pub fn parse_threat_report_md(content: &str) -> ThreatReportData {
    let mut result = ThreatReportData::default();

    if content.trim().is_empty() {
        return result;
    }

    let lines: Vec<&str> = content.split('\n').collect();
    let mut sec1_start = None;
    let mut sec1_end = lines.len();

    for (index, line) in lines.iter().enumerate() {
        if is_heading(line, "## 1. Executive Summary") {
            sec1_start = Some(index + 1);
        } else if sec1_start.is_some() && is_section_heading(line) {
            sec1_end = index;
            break;
        }
    }

    let Some(sec1_start) = sec1_start else {
        return result;
    };

    let mut subsections: Vec<(String, usize, usize)> = Vec::new();

    for (index, line) in lines.iter().enumerate().take(sec1_end).skip(sec1_start) {
        if let Some(name) = parse_subsection_heading(line) {
            if let Some(last) = subsections.last_mut() {
                last.2 = index;
            }
            subsections.push((name, index + 1, sec1_end));
        }
    }

    let narrative_sections = [
        "Risk Posture",
        "Top 5 Threats by Business Impact",
        "Key Recommendations",
    ];

    let mut narrative_parts = Vec::new();
    for wanted in narrative_sections {
        if let Some((_, start, end)) = subsections.iter().find(|(name, _, _)| name == wanted) {
            let text = lines[*start..*end].join("\n").trim().to_string();
            if !text.is_empty() {
                narrative_parts.push(text);
            }
        }
    }

    if narrative_parts.is_empty() {
        let mut prose_end = sec1_end;
        if let Some((_, start, _)) = subsections
            .iter()
            .find(|(name, _, _)| name == "Remediation Timeline")
        {
            prose_end = prose_end.min(start.saturating_sub(1));
        }
        let prose_text = lines[sec1_start..prose_end].join("\n").trim().to_string();
        if !prose_text.is_empty() {
            narrative_parts.push(prose_text);
        }
    }

    if !narrative_parts.is_empty() {
        let mut narrative = narrative_parts.join("\n\n");
        if narrative.len() > 2000 {
            narrative.truncate(2000);
        }
        result.executive_narrative = Some(narrative);
    }

    if let Some((_, start, end)) = subsections
        .iter()
        .find(|(name, _, _)| name == "Remediation Timeline")
    {
        for line in &lines[*start..*end] {
            if let Some(entry) = parse_timeline_entry(line.trim()) {
                result.remediation_timeline.push(entry);
            }
        }
    }

    result
}

pub fn build_remediation_actions(
    findings: &[RemediationFinding],
    tier: u8,
    has_compensating_controls: bool,
    tr_data: Option<&ThreatReportData>,
) -> Option<Vec<RemediationAction>> {
    if findings.is_empty() {
        return None;
    }

    if tier == 1 && has_compensating_controls {
        let actions = findings
            .iter()
            .map(|finding| RemediationAction {
                severity: finding.residual_severity.clone(),
                finding_id: finding.id.clone(),
                finding_name: finding.threat.clone(),
                recommendation: finding.recommendation.clone(),
                sla: sla_for_severity(&finding.residual_severity),
                status: if finding.control_status.is_empty() {
                    String::from("pending")
                } else {
                    finding.control_status.clone()
                },
            })
            .collect::<Vec<_>>();
        return Some(actions);
    }

    if let Some(tr_data) = tr_data {
        if !tr_data.remediation_timeline.is_empty() {
            let actions = findings
                .iter()
                .map(|finding| {
                    let (severity, recommendation) = if tier == 2 {
                        (finding.severity.clone(), finding.threat.clone())
                    } else {
                        (finding.risk_level.clone(), finding.mitigation.clone())
                    };

                    RemediationAction {
                        severity: severity.clone(),
                        finding_id: finding.id.clone(),
                        finding_name: finding.threat.clone(),
                        recommendation,
                        sla: sla_for_severity(&severity),
                        status: String::from("pending"),
                    }
                })
                .collect::<Vec<_>>();
            return Some(actions);
        }
    }

    None
}

fn is_heading(line: &str, heading: &str) -> bool {
    line.trim() == heading
}

fn is_section_heading(line: &str) -> bool {
    line.trim_start().starts_with("## ")
}

fn parse_subsection_heading(line: &str) -> Option<String> {
    let trimmed = line.trim_start();
    trimmed
        .strip_prefix("### ")
        .map(|rest| rest.trim().to_string())
}

fn parse_timeline_entry(line: &str) -> Option<RemediationTimelineEntry> {
    let rest = line.strip_prefix("- **")?;
    let (timeline, after_timeline) = rest.split_once("**")?;
    let after_timeline = after_timeline.trim_start();
    let after_timeline = after_timeline.strip_prefix('(')?;
    let (count_part, after_count) = after_timeline.split_once(' ')?;
    let count = count_part.parse::<usize>().ok()?;
    let after_count = after_count.trim_start();
    let (severity, after_severity) = after_count.split_once(' ')?;
    if !after_severity.starts_with("finding") {
        return None;
    }

    Some(RemediationTimelineEntry {
        timeline: timeline.trim().to_string(),
        count,
        severity: severity.to_string(),
    })
}

fn sla_for_severity(severity: &str) -> String {
    match severity {
        "Critical" => String::from("7d"),
        "High" => String::from("14d"),
        "Medium" => String::from("30d"),
        "Low" => String::from("90d"),
        _ => String::from("90d"),
    }
}

pub fn merge_delta_status(findings: &mut [ThreatFinding], threats_content: &str) {
    let rows = parse_markdown_table(threats_content, "## 7. Recommended Actions");
    if rows.is_empty() {
        return;
    }

    let mut status_by_id = BTreeMap::new();
    for row in rows {
        let fid = row
            .get("Finding ID")
            .cloned()
            .unwrap_or_default()
            .trim()
            .to_string();
        let status = row
            .get("Status")
            .cloned()
            .unwrap_or_default()
            .trim()
            .to_string();
        if !fid.is_empty() && !status.is_empty() {
            status_by_id.insert(fid, status);
        }
    }

    if status_by_id.is_empty() {
        return;
    }

    for finding in findings {
        if let Some(status) = status_by_id.get(&finding.id) {
            finding.delta_status = Some(status.clone());
        }
    }
}
