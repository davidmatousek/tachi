use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::Path;

use crate::normalization::{
    normalize_lower_text, normalize_optional_text, normalize_upper_text, stable_trim_text,
};
use crate::parsers::table::parse_markdown_table;

pub const VALID_AGENTIC_PATTERNS: [&str; 8] = [
    "agent_collusion",
    "emergent_behavior",
    "temporal_attack",
    "trust_exploitation",
    "communication_vulnerability",
    "resource_competition",
    "none",
    "multiple",
];

pub const SEVERITY_ORDER: [&str; 5] = ["Critical", "High", "Medium", "Low", "Note"];
pub const VALID_SOURCE_ATTRIBUTION_TAXONOMIES: [&str; 5] =
    ["owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"];
pub const VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS: [&str; 3] = ["primary", "related", "derived"];

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct SeverityCounts {
    pub critical: usize,
    pub high: usize,
    pub medium: usize,
    pub low: usize,
    pub note: usize,
    pub total: usize,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ResolvedFinding {
    pub id: String,
    pub component: String,
    pub threat: String,
    pub risk_level: String,
    pub resolution_reason: String,
    pub delta_status: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct RiskScoreFinding {
    pub id: String,
    pub component: String,
    pub threat: String,
    pub composite_score: String,
    pub severity: String,
    pub cvss: String,
    pub exploitability: String,
}

#[derive(Clone, Debug, Default, serde::Serialize, serde::Deserialize, PartialEq, Eq)]
pub struct SourceAttributionRecord {
    pub taxonomy: String,
    pub id: String,
    pub relationship: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ThreatFinding {
    pub id: String,
    pub component: String,
    pub threat: String,
    pub likelihood: String,
    pub impact: String,
    pub risk_level: String,
    pub mitigation: String,
    pub agentic_pattern: String,
    pub delta_status: Option<String>,
    pub source_attribution: Option<Vec<SourceAttributionRecord>>,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ValidationError {
    pub finding_id: String,
    pub record: SourceAttributionRecord,
    pub target_yaml_path: String,
    pub reason: String,
}

pub fn parse_finding_pattern(input: Option<&str>) -> String {
    let Some(raw) = input
        .map(stable_trim_text)
        .filter(|value| !value.is_empty())
    else {
        return String::from("none");
    };

    let normalized = normalize_lower_text(raw).replace('-', "_");
    if normalized == "—" || normalized == "none" || normalized == "_" {
        return String::from("none");
    }

    if VALID_AGENTIC_PATTERNS
        .iter()
        .any(|pattern| *pattern == normalized)
    {
        normalized
    } else {
        String::from("none")
    }
}

pub fn parse_component_distribution(findings: &[BTreeMap<String, String>]) -> Vec<(String, usize)> {
    let mut counts: BTreeMap<String, usize> = BTreeMap::new();

    for finding in findings {
        if let Some(component) = finding
            .get("component")
            .filter(|component| !component.is_empty())
        {
            *counts.entry(component.clone()).or_insert(0) += 1;
        }
    }

    let mut rows: Vec<(String, usize)> = counts.into_iter().collect();
    rows.sort_by(|left, right| right.1.cmp(&left.1).then_with(|| left.0.cmp(&right.0)));
    rows
}

pub fn parse_threats_severity(content: &str) -> SeverityCounts {
    let mut rows = parse_markdown_table(content, "## 6. Risk Summary");
    if !rows.is_empty() && !rows[0].contains_key("Risk Level") {
        rows = parse_markdown_table(content, "Risk Summary");
    }

    if rows.is_empty() || !rows[0].contains_key("Risk Level") {
        return SeverityCounts::default();
    }

    accumulate_severity_rows(&rows, "Risk Level")
}

pub fn parse_risk_scores_severity(content: &str) -> SeverityCounts {
    let mut rows = parse_markdown_table(content, "Severity Distribution");
    if rows.is_empty() {
        rows = parse_markdown_table(content, "## 1. Executive Summary");
    }

    if rows.is_empty() {
        return SeverityCounts::default();
    }

    accumulate_severity_rows(&rows, "Severity")
}

pub fn parse_risk_scores_findings(content: &str) -> Vec<RiskScoreFinding> {
    let rows = parse_markdown_table(content, "## 2. Scored Threat Table");
    if rows.is_empty() {
        return Vec::new();
    }

    rows.into_iter()
        .map(|row| RiskScoreFinding {
            id: row.get("ID").cloned().unwrap_or_default(),
            component: row.get("Component").cloned().unwrap_or_default(),
            threat: row.get("Threat").cloned().unwrap_or_default(),
            composite_score: row.get("Composite").cloned().unwrap_or_default(),
            severity: row.get("Severity").cloned().unwrap_or_default(),
            cvss: row.get("CVSS").cloned().unwrap_or_default(),
            exploitability: row
                .get("Exploit.")
                .cloned()
                .or_else(|| row.get("Exploitability").cloned())
                .unwrap_or_default(),
        })
        .collect()
}

pub fn compute_delta_counts(
    findings: &[ThreatFinding],
    resolved_findings: &[ResolvedFinding],
) -> BTreeMap<String, usize> {
    let mut counts = BTreeMap::from([
        (String::from("new"), 0),
        (String::from("unchanged"), 0),
        (String::from("updated"), 0),
        (String::from("resolved"), resolved_findings.len()),
    ]);

    for finding in findings {
        if let Some(status) = finding.delta_status.as_ref() {
            match normalize_upper_text(status).as_str() {
                "NEW" => {
                    if let Some(total) = counts.get_mut("new") {
                        *total += 1;
                    }
                }
                "UNCHANGED" => {
                    if let Some(total) = counts.get_mut("unchanged") {
                        *total += 1;
                    }
                }
                "UPDATED" => {
                    if let Some(total) = counts.get_mut("updated") {
                        *total += 1;
                    }
                }
                _ => {}
            }
        }
    }

    counts
}

pub fn parse_resolved_findings(content: &str) -> Vec<ResolvedFinding> {
    let rows = parse_markdown_table(content, "## 4b. Resolved Findings");
    if rows.is_empty() {
        return Vec::new();
    }

    let mut findings = Vec::new();
    for row in rows {
        findings.push(ResolvedFinding {
            id: row.get("ID").cloned().unwrap_or_default(),
            component: row.get("Component").cloned().unwrap_or_default(),
            threat: row.get("Threat").cloned().unwrap_or_default(),
            risk_level: row.get("Last Risk Level").cloned().unwrap_or_default(),
            resolution_reason: row.get("Resolution Reason").cloned().unwrap_or_default(),
            delta_status: String::from("RESOLVED"),
        });
    }

    findings
}

fn accumulate_severity_rows(
    rows: &[BTreeMap<String, String>],
    level_column: &str,
) -> SeverityCounts {
    let mut severity = SeverityCounts::default();

    for row in rows {
        let level = row.get(level_column).cloned().unwrap_or_default();
        let count_str = row.get("Count").cloned().unwrap_or_default();

        if level.eq_ignore_ascii_case("total") || level.starts_with("Total") {
            if let Some((total, raw)) = parse_total_count(&count_str) {
                severity.total = raw.unwrap_or(total);
            }
            continue;
        }

        match level.as_str() {
            "Critical" => severity.critical = parse_count(&count_str),
            "High" => severity.high = parse_count(&count_str),
            "Medium" => severity.medium = parse_count(&count_str),
            "Low" => severity.low = parse_count(&count_str),
            "Note" => severity.note = parse_count(&count_str),
            _ => {}
        }
    }

    severity
}

fn parse_count(value: &str) -> usize {
    stable_trim_text(value).parse::<usize>().unwrap_or(0)
}

fn parse_total_count(value: &str) -> Option<(usize, Option<usize>)> {
    let value = stable_trim_text(value);
    let start = value
        .chars()
        .take_while(|ch| ch.is_ascii_digit())
        .collect::<String>();
    let total = start.parse::<usize>().ok()?;
    if let Some(open_idx) = value.find('(') {
        let inner = &value[open_idx..];
        let raw_digits = inner
            .chars()
            .filter(|ch| ch.is_ascii_digit())
            .collect::<String>();
        let raw = raw_digits.parse::<usize>().ok();
        Some((total, raw))
    } else {
        Some((total, None))
    }
}

pub fn parse_threats_findings(content: &str) -> Result<Vec<ThreatFinding>, String> {
    let rows = parse_markdown_table(content, "## 7. Recommended Actions");
    if rows.is_empty() {
        return Ok(Vec::new());
    }

    let pattern_key = rows[0]
        .keys()
        .find(|key| {
            let lowered = normalize_lower_text(key);
            lowered == "pattern" || lowered == "agentic pattern"
        })
        .cloned();

    let source_attribution_block = extract_source_attribution_block(content)?;
    let mut findings = Vec::new();

    for row in rows {
        let id = row.get("Finding ID").cloned().unwrap_or_default();
        if id.trim().is_empty() {
            continue;
        }
        let source_attribution = source_attribution_block
            .as_ref()
            .and_then(|block| block.get(&id).cloned());

        let finding = ThreatFinding {
            id: id.clone(),
            component: row.get("Component").cloned().unwrap_or_default(),
            threat: row.get("Threat").cloned().unwrap_or_default(),
            likelihood: String::from("—"),
            impact: String::from("—"),
            risk_level: row.get("Risk Level").cloned().unwrap_or_default(),
            mitigation: row.get("Mitigation").cloned().unwrap_or_default(),
            agentic_pattern: pattern_key
                .as_ref()
                .map(|key| parse_finding_pattern(row.get(key).map(|s| s.as_str())))
                .unwrap_or_else(|| String::from("none")),
            delta_status: normalize_optional_text(row.get("Status").map(|status| status.as_str())),
            source_attribution,
        };

        findings.push(finding);
    }

    Ok(findings)
}

pub fn validate_source_attribution(
    findings: &[ThreatFinding],
    taxonomy_dir: &Path,
) -> Vec<ValidationError> {
    let mut catalog_cache: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut errors = Vec::new();

    for finding in findings {
        let Some(records) = finding.source_attribution.as_ref() else {
            continue;
        };

        for record in records {
            let taxonomy = record.taxonomy.clone();
            let ids = catalog_cache
                .entry(taxonomy.clone())
                .or_insert_with(|| load_catalog_ids(&taxonomy, taxonomy_dir));

            if !ids.contains(&record.id) {
                errors.push(ValidationError {
                    finding_id: finding.id.clone(),
                    record: record.clone(),
                    target_yaml_path: taxonomy_dir
                        .join(format!("{taxonomy}.yaml"))
                        .display()
                        .to_string(),
                    reason: format!(
                        "id {:?} not found as a top-level '- id:' key in the catalog",
                        record.id
                    ),
                });
            }
        }
    }

    errors
}

pub fn compute_has_source_attribution(findings: &[ThreatFinding]) -> bool {
    findings.iter().any(|finding| {
        finding
            .source_attribution
            .as_ref()
            .map(|records| !records.is_empty())
            .unwrap_or(false)
    })
}

fn load_catalog_ids(taxonomy: &str, taxonomy_dir: &Path) -> BTreeSet<String> {
    let catalog_path = taxonomy_dir.join(format!("{taxonomy}.yaml"));
    let text = fs::read_to_string(catalog_path).unwrap_or_default();
    let mut ids = BTreeSet::new();

    for line in text.lines() {
        let trimmed = line.trim();
        if let Some(rest) = trimmed.strip_prefix("- id: ") {
            ids.insert(rest.trim().to_string());
        }
    }

    ids
}

fn extract_source_attribution_block(
    content: &str,
) -> Result<Option<BTreeMap<String, Vec<SourceAttributionRecord>>>, String> {
    let Some(header_idx) = content
        .lines()
        .enumerate()
        .find_map(|(idx, line)| (line.trim() == "## 9. Source Attribution").then_some(idx))
    else {
        return Ok(None);
    };

    let mut lines = content.lines().skip(header_idx + 1);
    let mut seen_fence = false;
    let mut body = Vec::new();

    for line in lines.by_ref() {
        let trimmed = line.trim_end();
        if !seen_fence {
            if trimmed.trim_start().starts_with("```yaml") {
                seen_fence = true;
            }
            continue;
        }
        if trimmed.trim() == "```" {
            break;
        }
        body.push(trimmed.to_string());
    }

    if !seen_fence {
        return Ok(Some(BTreeMap::new()));
    }

    let mut result: BTreeMap<String, Vec<SourceAttributionRecord>> = BTreeMap::new();
    let mut current_id: Option<String> = None;

    for line in body {
        let trimmed = line.trim();
        if let Some(id) = parse_empty_source_attribution_entry(trimmed) {
            result.insert(id, Vec::new());
            current_id = None;
            continue;
        }

        if let Some(id) = parse_block_source_attribution_key(trimmed) {
            current_id = Some(id.clone());
            result.entry(id).or_default();
            continue;
        }

        if let Some(record) = parse_source_attribution_list_item(trimmed)? {
            if let Some(id) = current_id.as_ref() {
                result.entry(id.clone()).or_default().push(record);
            }
        }
    }

    Ok(Some(result))
}

fn parse_empty_source_attribution_entry(line: &str) -> Option<String> {
    let (lhs, rhs) = line.split_once(':')?;
    if rhs.trim() != "[]" {
        return None;
    }
    let id = lhs.trim();
    if finding_id_like(id) {
        Some(id.to_string())
    } else {
        None
    }
}

fn parse_block_source_attribution_key(line: &str) -> Option<String> {
    let (lhs, rhs) = line.split_once(':')?;
    if !rhs.trim().is_empty() {
        return None;
    }
    let id = lhs.trim();
    if finding_id_like(id) {
        Some(id.to_string())
    } else {
        None
    }
}

fn finding_id_like(value: &str) -> bool {
    value.chars().any(|ch| ch == '-')
        && value
            .chars()
            .all(|ch| ch.is_ascii_uppercase() || ch.is_ascii_digit() || ch == '-')
}

fn parse_source_attribution_list_item(
    line: &str,
) -> Result<Option<SourceAttributionRecord>, String> {
    let stripped = line.trim_start();
    let Some(body) = stripped
        .strip_prefix("- {")
        .and_then(|value| value.strip_suffix('}'))
    else {
        return Ok(None);
    };
    let mut taxonomy = String::new();
    let mut id = String::new();
    let mut relationship = String::from("primary");

    for part in body.split(',') {
        let mut pieces = part.splitn(2, ':');
        let key = pieces
            .next()
            .ok_or_else(|| String::from("malformed source attribution record"))?
            .trim();
        let value = pieces
            .next()
            .ok_or_else(|| String::from("malformed source attribution record"))?
            .trim()
            .trim_matches('"')
            .trim_matches('\'');
        match key {
            "taxonomy" => taxonomy = value.to_string(),
            "id" => id = value.to_string(),
            "relationship" => relationship = value.to_string(),
            _ => {}
        }
    }

    if taxonomy.is_empty() || id.is_empty() {
        return Err(String::from(
            "missing taxonomy or id in source attribution record",
        ));
    }

    if relationship.is_empty() {
        relationship = String::from("primary");
    }

    if !VALID_SOURCE_ATTRIBUTION_TAXONOMIES.contains(&taxonomy.as_str()) {
        return Err(format!(
            "invalid taxonomy {:?}. Allowed: {:?}",
            taxonomy, VALID_SOURCE_ATTRIBUTION_TAXONOMIES
        ));
    }

    if !VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS.contains(&relationship.as_str()) {
        return Err(format!(
            "invalid relationship {:?}. Allowed: {:?}",
            relationship, VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS
        ));
    }

    Ok(Some(SourceAttributionRecord {
        taxonomy,
        id,
        relationship,
    }))
}

#[cfg(test)]
mod tests {
    use super::{parse_finding_pattern, parse_threats_findings};

    #[test]
    fn parse_finding_pattern_normalizes_sentinels_and_hyphenated_values() {
        assert_eq!(parse_finding_pattern(Some(" AGENT-COLLUSION ")), "agent_collusion");
        assert_eq!(parse_finding_pattern(Some("multiple")), "multiple");
        assert_eq!(parse_finding_pattern(Some("—")), "none");
        assert_eq!(parse_finding_pattern(Some("_")), "none");
        assert_eq!(parse_finding_pattern(Some("unknown")), "none");
        assert_eq!(parse_finding_pattern(None), "none");
    }

    #[test]
    fn parse_threats_findings_returns_empty_without_recommended_actions_section() {
        let empty = parse_threats_findings("# Threat Model\n\nNothing here.").expect("parse empty");
        assert!(empty.is_empty());

        let missing_header = parse_threats_findings(
            "## 7. Recommended Actions\n\n## 9. Source Attribution\n```yaml\n```",
        )
        .expect("parse missing header");
        assert!(missing_header.is_empty());
    }

    #[test]
    fn parse_threats_findings_rejects_bad_source_attribution_records() {
        let markdown = r#"
## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
| --- | --- | --- | --- | --- |
| S-1 | API | Broken auth | High | Fix it |

## 9. Source Attribution
```yaml
S-1:
  - {taxonomy: "bogus", id: "X", relationship: "primary"}
```
"#;

        let err = parse_threats_findings(markdown).expect_err("bad attribution");
        assert!(err.contains("invalid taxonomy"));
    }
}
