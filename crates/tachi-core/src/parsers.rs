use std::collections::BTreeMap;
use std::collections::BTreeSet;
use std::fs;
use std::path::Path;

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

pub fn escape_typst_string(input: &str) -> String {
    input
        .replace('\\', "\\\\")
        .replace('\"', "\\\"")
        .replace('\n', "\\n")
}

pub fn strip_bold(input: &str) -> String {
    let trimmed = input.trim();
    if let Some(stripped) = trimmed
        .strip_prefix("**")
        .and_then(|s| s.strip_suffix("**"))
    {
        stripped.to_string()
    } else {
        input.to_string()
    }
}

pub fn parse_finding_pattern(input: Option<&str>) -> String {
    let Some(raw) = input.map(str::trim).filter(|value| !value.is_empty()) else {
        return String::from("none");
    };

    let normalized = raw.to_ascii_lowercase().replace('-', "_");
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

pub fn parse_markdown_table(content: &str, section_header: &str) -> Vec<BTreeMap<String, String>> {
    let mut in_section = false;
    let mut header: Option<Vec<String>> = None;
    let mut rows = Vec::new();

    for raw_line in content.lines() {
        let line = raw_line.trim();
        if line == section_header {
            in_section = true;
            header = None;
            continue;
        }

        if !in_section {
            continue;
        }

        if line.starts_with('#') && line != section_header {
            break;
        }

        if !line.starts_with('|') {
            continue;
        }

        let cells = split_table_row(line);
        if cells.is_empty() {
            continue;
        }

        if header.is_none() {
            if is_separator_row(&cells) {
                continue;
            }
            header = Some(cells);
            continue;
        }

        if is_separator_row(&cells) {
            continue;
        }

        let Some(header_cells) = header.as_ref() else {
            continue;
        };

        let mut row = BTreeMap::new();
        for (idx, key) in header_cells.iter().enumerate() {
            let value = cells.get(idx).cloned().unwrap_or_default();
            row.insert(key.clone(), value);
        }
        rows.push(row);
    }

    rows
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ScopeData {
    pub components: Vec<ScopeComponent>,
    pub data_flows: Vec<DataFlow>,
    pub trust_boundaries: Vec<TrustBoundary>,
    pub boundary_crossings: Vec<BoundaryCrossing>,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ScopeComponent {
    pub name: String,
    pub kind: String,
    pub description: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct DataFlow {
    pub source: String,
    pub destination: String,
    pub data: String,
    pub protocol: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct TrustBoundary {
    pub zone: String,
    pub trust_level: String,
    pub components: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct BoundaryCrossing {
    pub crossing: String,
    pub from_zone: String,
    pub to_zone: String,
    pub components: String,
    pub controls: String,
}

pub fn parse_scope_data(content: &str) -> ScopeData {
    let mut result = ScopeData::default();

    for row in parse_markdown_table(content, "### Components") {
        result.components.push(ScopeComponent {
            name: row.get("Component").cloned().unwrap_or_default(),
            kind: row.get("Type").cloned().unwrap_or_default(),
            description: row.get("Description").cloned().unwrap_or_default(),
        });
    }

    for row in parse_markdown_table(content, "### Data Flows") {
        result.data_flows.push(DataFlow {
            source: row.get("Source").cloned().unwrap_or_default(),
            destination: row.get("Destination").cloned().unwrap_or_default(),
            data: row.get("Data").cloned().unwrap_or_default(),
            protocol: row.get("Protocol").cloned().unwrap_or_default(),
        });
    }

    for row in parse_markdown_table(content, "### Trust Zones") {
        result.trust_boundaries.push(TrustBoundary {
            zone: row.get("Zone").cloned().unwrap_or_default(),
            trust_level: row.get("Trust Level").cloned().unwrap_or_default(),
            components: row.get("Components").cloned().unwrap_or_default(),
        });
    }

    for row in parse_markdown_table(content, "### Boundary Crossings") {
        result.boundary_crossings.push(BoundaryCrossing {
            crossing: row.get("Crossing").cloned().unwrap_or_default(),
            from_zone: row.get("From Zone").cloned().unwrap_or_default(),
            to_zone: row.get("To Zone").cloned().unwrap_or_default(),
            components: row.get("Components").cloned().unwrap_or_default(),
            controls: row.get("Controls").cloned().unwrap_or_default(),
        });
    }

    result
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
            match status.to_ascii_uppercase().as_str() {
                "NEW" => *counts.get_mut("new").expect("key exists") += 1,
                "UNCHANGED" => *counts.get_mut("unchanged").expect("key exists") += 1,
                "UPDATED" => *counts.get_mut("updated").expect("key exists") += 1,
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
    value.trim().parse::<usize>().unwrap_or(0)
}

fn parse_total_count(value: &str) -> Option<(usize, Option<usize>)> {
    let value = value.trim();
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

#[derive(Clone, Debug, Default, PartialEq, Eq)]
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

pub fn parse_threats_findings(content: &str) -> Result<Vec<ThreatFinding>, String> {
    let rows = parse_markdown_table(content, "## 7. Recommended Actions");
    if rows.is_empty() {
        return Ok(Vec::new());
    }

    let pattern_key = rows[0]
        .keys()
        .find(|key| {
            let lowered = key.trim().to_ascii_lowercase();
            lowered == "pattern" || lowered == "agentic pattern"
        })
        .cloned();

    let source_attribution_block = extract_source_attribution_block(content)?;
    let mut findings = Vec::new();

    for row in rows {
        let id = row.get("Finding ID").cloned().unwrap_or_default();
        let source_attribution = source_attribution_block
            .as_ref()
            .and_then(|block| block.get(&id).cloned());

        let mut finding = ThreatFinding {
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
            delta_status: row
                .get("Status")
                .cloned()
                .filter(|status| !status.trim().is_empty()),
            source_attribution,
        };

        if let Some(delta_status) = finding.delta_status.as_ref() {
            if delta_status.trim().is_empty() {
                finding.delta_status = None;
            }
        }

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

pub const VALID_SOURCE_ATTRIBUTION_TAXONOMIES: [&str; 5] =
    ["owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe"];
pub const VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS: [&str; 3] = ["primary", "related", "derived"];

pub fn parse_project_name(
    content: &str,
    title_override: Option<&str>,
    target_dir: Option<&Path>,
) -> String {
    if let Some(override_name) = title_override
        .map(str::trim)
        .filter(|name| !name.is_empty())
    {
        return override_name.to_string();
    }

    if let Some(name) = parse_threats_h1(content) {
        return name;
    }

    if let Some(dir) = target_dir {
        let architecture_path = dir.join("architecture.md");
        if let Ok(architecture) = fs::read_to_string(architecture_path) {
            if let Some(name) = parse_architecture_heading(&architecture) {
                return name;
            }
        }
    }

    String::from("Unknown Project")
}

fn split_table_row(line: &str) -> Vec<String> {
    line.trim_matches('|')
        .split('|')
        .map(|cell| cell.trim().to_string())
        .collect()
}

fn is_separator_row(cells: &[String]) -> bool {
    !cells.is_empty()
        && cells.iter().all(|cell| {
            let stripped = cell.replace(' ', "");
            !stripped.is_empty() && stripped.chars().all(|c| c == '-' || c == ':')
        })
}

fn parse_threats_h1(content: &str) -> Option<String> {
    for line in content.lines() {
        let trimmed = line.trim();
        if !trimmed.starts_with('#') {
            continue;
        }

        let heading = trimmed.trim_start_matches('#').trim();
        if let Some(name) = heading.strip_suffix(" Threat Model") {
            return normalize_project_name(name);
        }
        if let Some(name) = heading.strip_prefix("Threat Model: ") {
            return normalize_project_name(name);
        }
    }

    None
}

fn parse_architecture_heading(content: &str) -> Option<String> {
    let first_h1 = content.lines().find_map(|line| {
        let trimmed = line.trim();
        trimmed.strip_prefix('#').map(|rest| rest.trim())
    })?;

    let pieces: Vec<&str> = first_h1.split('—').map(|part| part.trim()).collect();
    if pieces.len() != 2 {
        return None;
    }

    if pieces[1].eq_ignore_ascii_case("Architecture") {
        normalize_project_name(pieces[0])
    } else if pieces[0].eq_ignore_ascii_case("Architecture") {
        normalize_project_name(pieces[1])
    } else {
        None
    }
}

fn normalize_project_name(value: &str) -> Option<String> {
    let normalized = value.trim();
    if normalized.is_empty() {
        None
    } else {
        Some(normalized.to_string())
    }
}
