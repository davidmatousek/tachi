use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

use crate::parsers::ScopeComponent;
use crate::parsers::{SeverityCounts, SEVERITY_ORDER};

pub const SCAFFOLD_TEMPLATES: [&str; 5] = [
    "baseball-card",
    "risk-funnel",
    "system-architecture",
    "maestro-stack",
    "maestro-heatmap",
];

const TEMPLATE_FILES: [(&str, &str); 5] = [
    ("baseball-card", "infographic-baseball-card.md"),
    ("risk-funnel", "infographic-risk-funnel.md"),
    ("system-architecture", "infographic-system-architecture.md"),
    ("maestro-stack", "infographic-maestro-stack.md"),
    ("maestro-heatmap", "infographic-maestro-heatmap.md"),
];

pub const SEVERITY_COLORS: [(&str, &str); 5] = [
    ("Critical", "#DC2626"),
    ("High", "#EA580C"),
    ("Medium", "#CA8A04"),
    ("Low", "#2563EB"),
    ("Note", "#6B7280"),
];

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct PromptScaffold {
    pub preamble: String,
    pub postamble: String,
    pub found: bool,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct InfographicMetadata {
    pub project_name: String,
    pub scan_date: String,
    pub tier: usize,
    pub data_source_type: String,
    pub total_findings: usize,
    pub note_count: usize,
    pub agent_count: usize,
    pub risk_posture: String,
    pub schema_version: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SeverityDistributionEntry {
    pub label: String,
    pub count: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HeatMapRow {
    pub component: String,
    pub critical: usize,
    pub high: usize,
    pub medium: usize,
    pub low: usize,
    pub total: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct TopFinding {
    pub id: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct InfographicValidationData {
    pub metadata: InfographicMetadata,
    pub severity_distribution: Vec<SeverityDistributionEntry>,
    pub heat_map: Vec<HeatMapRow>,
    pub top_findings: Vec<TopFinding>,
    pub findings_ids: std::collections::BTreeSet<String>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct ComponentRiskWeight {
    pub component: String,
    pub weight: String,
    pub score: f64,
    pub annotation: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MaestroLayerDistributionEntry {
    pub layer_id: String,
    pub layer_name: String,
    pub finding_count: usize,
    pub highest_severity: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SeverityPercentage {
    pub label: String,
    pub count: usize,
    pub percentage: usize,
    pub color: &'static str,
}

pub fn largest_remainder(
    percentages_map: &BTreeMap<String, usize>,
    target: usize,
) -> BTreeMap<String, usize> {
    let total: usize = percentages_map.values().sum();
    if percentages_map.is_empty() {
        return BTreeMap::new();
    }

    if total == 0 {
        return percentages_map
            .keys()
            .cloned()
            .map(|label| (label, 0))
            .collect();
    }

    let mut floors = BTreeMap::new();
    let mut remainders: Vec<(String, u128)> = Vec::with_capacity(percentages_map.len());
    let mut floor_sum = 0usize;
    let total = total as u128;
    let target_value = target;
    let target = target as u128;

    for (label, count) in percentages_map {
        let scaled = (*count as u128) * target;
        let floor = (scaled / total) as usize;
        let remainder = scaled % total;

        floor_sum += floor;
        floors.insert(label.clone(), floor);
        remainders.push((label.clone(), remainder));
    }

    let remaining = target_value.saturating_sub(floor_sum);
    remainders.sort_by(|left, right| right.1.cmp(&left.1).then_with(|| left.0.cmp(&right.0)));

    for (label, _) in remainders.into_iter().take(remaining) {
        if let Some(value) = floors.get_mut(&label) {
            *value += 1;
        }
    }

    floors
}

pub fn extract_prompt_scaffold(template_name: &str, repo_root: Option<&Path>) -> PromptScaffold {
    let mut result = PromptScaffold::default();
    if !SCAFFOLD_TEMPLATES.contains(&template_name) {
        return result;
    }

    let repo_root = repo_root
        .map(Path::to_path_buf)
        .unwrap_or_else(default_repo_root);
    let Some(template_file) = TEMPLATE_FILES
        .iter()
        .find(|(name, _)| *name == template_name)
        .map(|(_, file)| file)
    else {
        return result;
    };

    let template_path = repo_root
        .join("templates")
        .join("tachi")
        .join("infographics")
        .join(template_file);
    let Ok(content) = fs::read_to_string(template_path) else {
        return result;
    };

    let Some(prompt_text) = extract_prompt_text(&content) else {
        return result;
    };

    let Some(marker_idx) = find_data_marker(&prompt_text) else {
        return result;
    };

    let marker_line_end = prompt_text[marker_idx..]
        .find('\n')
        .map(|offset| marker_idx + offset)
        .unwrap_or(prompt_text.len());
    result.preamble = prompt_text[..marker_line_end].trim_end().to_string() + "\n";

    result.postamble = extract_postamble(&prompt_text);
    result.found = true;
    result
}

pub fn compute_severity_percentages(severity: &SeverityCounts) -> Vec<SeverityPercentage> {
    let counts = BTreeMap::from([
        (String::from("Critical"), severity.critical),
        (String::from("High"), severity.high),
        (String::from("Medium"), severity.medium),
        (String::from("Low"), severity.low),
    ]);

    let percentages = largest_remainder(&counts, 100);
    let mut result = Vec::with_capacity(SEVERITY_ORDER.len().saturating_sub(1));

    for label in SEVERITY_ORDER {
        if label == "Note" {
            continue;
        }

        let color = severity_color(label);
        result.push(SeverityPercentage {
            label: label.to_string(),
            count: *counts.get(label).unwrap_or(&0),
            percentage: *percentages.get(label).unwrap_or(&0),
            color,
        });
    }

    result
}

pub fn compute_metadata(
    threats_content: &str,
    frontmatter: &BTreeMap<String, String>,
    tier: usize,
    severity: &SeverityCounts,
    scope_components: &[ScopeComponent],
    project_name: &str,
) -> InfographicMetadata {
    let scan_date = frontmatter
        .get("date")
        .cloned()
        .unwrap_or_else(|| String::from("Unknown"));
    let schema_version = frontmatter
        .get("schema_version")
        .cloned()
        .unwrap_or_else(|| String::from("1.0"));
    let agent_count = threats_content
        .lines()
        .filter(|line| {
            let trimmed = line.trim_start();
            trimmed.starts_with("### 3.") || trimmed.starts_with("### 4.")
        })
        .count();
    let tier_label = match tier {
        1 => "Residual risk",
        2 => "Inherent risk",
        3 => "Severity assessment",
        _ => "Unknown",
    };
    let data_source_type = match tier {
        1 => "compensating-controls",
        2 => "risk-scores",
        3 => "threats",
        _ => "threats",
    };
    let risk_posture = format!(
        "{tier_label} — {} Critical and {} High findings across {} components",
        severity.critical,
        severity.high,
        scope_components.len()
    );

    InfographicMetadata {
        project_name: project_name.to_string(),
        scan_date,
        tier,
        data_source_type: data_source_type.to_string(),
        total_findings: severity.total,
        note_count: severity.note,
        agent_count,
        risk_posture,
        schema_version,
    }
}

pub fn validate_infographic(data: &InfographicValidationData) -> Vec<String> {
    let mut errors = Vec::new();

    let sev_sum: usize = data
        .severity_distribution
        .iter()
        .map(|entry| entry.count)
        .sum();
    let expected = data
        .metadata
        .total_findings
        .saturating_sub(data.metadata.note_count);
    if sev_sum != expected {
        errors.push(format!(
            "Validation error: Severity sum mismatch — expected {expected}, got {sev_sum}"
        ));
    }

    for finding in &data.top_findings {
        if !data.findings_ids.contains(&finding.id) {
            errors.push(format!(
                "Validation error: Top finding ID {} not found in findings set",
                finding.id
            ));
        }
    }

    for row in &data.heat_map {
        let row_sum = row.critical + row.high + row.medium + row.low;
        if row_sum != row.total {
            errors.push(format!(
                "Validation error: Heat map row '{}' — expected total {}, got {}",
                row.component, row.total, row_sum
            ));
        }
    }

    errors
}

pub fn compute_component_risk_weights(heat_map: &[HeatMapRow]) -> Vec<ComponentRiskWeight> {
    let mut result = Vec::with_capacity(heat_map.len());

    for row in heat_map {
        let score = if row.total == 0 {
            0.0
        } else {
            (row.critical * 4 + row.high * 3 + row.medium * 2 + row.low) as f64 / row.total as f64
        };

        let weight = if score >= 3.0 {
            "high"
        } else if score >= 2.0 {
            "medium"
        } else {
            "low"
        };

        let mut parts = Vec::new();
        if row.critical > 0 {
            parts.push(format!("{} Critical", row.critical));
        }
        if row.high > 0 {
            parts.push(format!("{} High", row.high));
        }
        if row.medium > 0 {
            parts.push(format!("{} Medium", row.medium));
        }
        if row.low > 0 {
            parts.push(format!("{} Low", row.low));
        }

        let annotation = if parts.is_empty() {
            String::from("No findings")
        } else {
            format!("{} findings", parts.join(" + "))
        };

        result.push(ComponentRiskWeight {
            component: row.component.clone(),
            weight: weight.to_string(),
            score: (score * 10.0).round() / 10.0,
            annotation,
        });
    }

    result.sort_by(|left, right| {
        right
            .score
            .partial_cmp(&left.score)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| left.component.cmp(&right.component))
    });

    result
}

pub fn compute_most_exposed_layer(layer_distribution: &[MaestroLayerDistributionEntry]) -> String {
    if layer_distribution.is_empty() {
        return String::new();
    }

    let mut sorted_layers = layer_distribution.to_vec();
    sorted_layers.sort_by(|left, right| {
        right
            .finding_count
            .cmp(&left.finding_count)
            .then_with(|| {
                severity_rank(&right.highest_severity).cmp(&severity_rank(&left.highest_severity))
            })
            .then_with(|| left.layer_id.cmp(&right.layer_id))
    });

    let top = &sorted_layers[0];
    if top.layer_name.is_empty() {
        top.layer_id.clone()
    } else {
        format!("{} — {}", top.layer_id, top.layer_name)
    }
}

fn severity_rank(severity: &str) -> usize {
    match severity {
        "Critical" => 4,
        "High" => 3,
        "Medium" => 2,
        "Low" => 1,
        "Note" => 0,
        _ => 0,
    }
}

fn severity_color(label: &str) -> &'static str {
    match label {
        "Critical" => "#DC2626",
        "High" => "#EA580C",
        "Medium" => "#CA8A04",
        "Low" => "#2563EB",
        "Note" => "#6B7280",
        _ => "#6B7280",
    }
}

fn default_repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|path| path.parent())
        .expect("repo root")
        .to_path_buf()
}

fn extract_prompt_text(content: &str) -> Option<String> {
    let mut in_prompt_section = false;
    let mut in_fence = false;
    let mut fence_lines = Vec::new();

    for line in content.lines() {
        let stripped = line.trim();
        let lowered = stripped.to_ascii_lowercase();
        if lowered.starts_with('#') && lowered.contains("gemini") && lowered.contains("prompt") {
            in_prompt_section = true;
            continue;
        }
        if in_prompt_section && !in_fence && stripped.starts_with("```") {
            in_fence = true;
            continue;
        }
        if in_fence && stripped.starts_with("```") {
            return Some(fence_lines.join("\n"));
        }
        if in_fence {
            fence_lines.push(line);
        }
    }

    None
}

fn find_data_marker(prompt_text: &str) -> Option<usize> {
    let marker = "DATA CONTENT (render this";
    if let Some(index) = prompt_text.find(marker) {
        return Some(index);
    }

    for (index, _) in prompt_text.match_indices("DATA CONTENT") {
        let line_end = prompt_text[index..]
            .find('\n')
            .map(|offset| index + offset)
            .unwrap_or(prompt_text.len());
        let line_text = &prompt_text[index..line_end];
        if !line_text.contains("sections.") {
            return Some(index);
        }
    }

    None
}

fn extract_postamble(prompt_text: &str) -> String {
    if let Some(index) = prompt_text.find("\nFOOTER") {
        return prompt_text[index + 1..].trim().to_string();
    }
    if let Some(index) = prompt_text.find("FOOTER") {
        return prompt_text[index..].trim().to_string();
    }
    String::new()
}
