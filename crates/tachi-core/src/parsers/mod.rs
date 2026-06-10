use std::fs;
use std::path::Path;

pub mod findings;
pub mod mermaid;
pub mod scope;
pub mod table;

pub use findings::{
    compute_delta_counts, compute_has_source_attribution, parse_component_distribution,
    parse_finding_pattern, parse_risk_scores_findings, parse_risk_scores_severity,
    parse_resolved_findings, parse_threats_findings, parse_threats_severity,
    validate_source_attribution, ResolvedFinding, RiskScoreFinding, SeverityCounts,
    SourceAttributionRecord, ThreatFinding, ValidationError, SEVERITY_ORDER,
    VALID_AGENTIC_PATTERNS, VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS,
    VALID_SOURCE_ATTRIBUTION_TAXONOMIES,
};
pub use mermaid::{parse_component_asset_map, VALID_ASSET_TAGS};
pub use scope::{
    parse_scope_data, BoundaryCrossing, DataFlow, ScopeComponent, ScopeData, TrustBoundary,
};
pub use table::{is_separator_row, parse_markdown_table, split_table_row};

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
    } else if pieces[0].eq_ignore_ascii_case("Architecture")
        || pieces[0].eq_ignore_ascii_case("Security Architecture")
    {
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
