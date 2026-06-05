use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use crate::parsers::{parse_markdown_table, strip_bold, SeverityCounts, SEVERITY_ORDER};

pub const SEVERITY_COLORS: [(&str, &str); 5] = [
    ("Critical", "#DC2626"),
    ("High", "#EA580C"),
    ("Medium", "#CA8A04"),
    ("Low", "#2563EB"),
    ("Note", "#6B7280"),
];

pub const MAESTRO_LAYERS: [&str; 7] = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"];

const SCAFFOLD_TEMPLATES: [&str; 5] = [
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

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct PromptScaffold {
    pub preamble: String,
    pub postamble: String,
    pub found: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MaestroLayerDistribution {
    pub layer_id: String,
    pub layer_name: String,
    pub finding_count: usize,
    pub highest_severity: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MaestroFinding {
    pub id: String,
    pub component: String,
    pub maestro_layer: String,
    pub risk_level: String,
    pub threat: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MaestroHeatmapRow {
    pub component: String,
    pub layers: BTreeMap<String, Option<String>>,
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

pub fn parse_maestro_layer_distribution(threats_content: &str) -> Vec<MaestroLayerDistribution> {
    let rows = parse_markdown_table(threats_content, "#### Risk by MAESTRO Layer");
    if rows.is_empty() {
        return Vec::new();
    }

    let mut result = Vec::with_capacity(rows.len());

    for row in rows {
        let layer_raw = row.get("MAESTRO Layer").map_or("", |value| value.trim());
        if layer_raw.is_empty() {
            continue;
        }

        let (layer_id, layer_name) = split_maestro_layer(layer_raw);
        let finding_count = row
            .get("Finding Count")
            .and_then(|value| value.trim().parse::<usize>().ok())
            .unwrap_or(0);
        let highest_severity = row
            .get("Highest Severity")
            .map(|value| value.trim().to_string())
            .unwrap_or_default();

        result.push(MaestroLayerDistribution {
            layer_id,
            layer_name,
            finding_count,
            highest_severity,
        });
    }

    result
}

pub fn compute_most_exposed_layer(layer_distribution: &[MaestroLayerDistribution]) -> String {
    let Some(top) = layer_distribution.iter().max_by(|left, right| {
        left.finding_count
            .cmp(&right.finding_count)
            .then_with(|| {
                severity_rank(&left.highest_severity).cmp(&severity_rank(&right.highest_severity))
            })
            .then_with(|| right.layer_id.cmp(&left.layer_id))
    }) else {
        return String::new();
    };

    if top.layer_name.is_empty() {
        top.layer_id.clone()
    } else {
        format!("{} — {}", top.layer_id, top.layer_name)
    }
}

pub fn parse_per_finding_maestro(threats_content: &str) -> Vec<MaestroFinding> {
    let lines: Vec<&str> = threats_content.lines().collect();
    let mut findings = Vec::new();

    for (start_idx, line) in lines.iter().enumerate() {
        if !is_maestro_agent_section(line) {
            continue;
        }

        let mut header_cols: Option<Vec<String>> = None;

        for raw_line in lines.iter().skip(start_idx + 1) {
            let stripped = raw_line.trim();
            if stripped.starts_with("## ") || stripped.starts_with("### ") {
                break;
            }
            if !stripped.starts_with('|') {
                continue;
            }

            let cells = split_table_row(stripped);
            if cells.is_empty() {
                continue;
            }

            if header_cols.is_none() {
                if is_separator_row(&cells) {
                    continue;
                }

                if cells
                    .first()
                    .map(|value| value.eq_ignore_ascii_case("id"))
                    .unwrap_or(false)
                {
                    header_cols = Some(cells);
                }
                continue;
            }

            if is_separator_row(&cells) {
                continue;
            }

            let Some(headers) = header_cols.as_ref() else {
                continue;
            };

            let Some(id_idx) = column_index(headers, "ID") else {
                continue;
            };
            let id = cells
                .get(id_idx)
                .map(|value| strip_bold(value).trim().to_string())
                .unwrap_or_default();
            if id.is_empty()
                || !id
                    .chars()
                    .next()
                    .map(|c| c.is_ascii_uppercase())
                    .unwrap_or(false)
            {
                continue;
            }

            let component = column_value(headers, &cells, "Component");
            let threat = column_value(headers, &cells, "Threat");
            let risk_level = column_value(headers, &cells, "Risk Level");
            let maestro_layer = column_value(headers, &cells, "MAESTRO Layer");

            if maestro_layer.is_empty() {
                continue;
            }

            findings.push(MaestroFinding {
                id,
                component,
                maestro_layer,
                risk_level,
                threat,
            });
        }
    }

    findings
}

pub fn compute_maestro_heatmap(per_finding_data: &[MaestroFinding]) -> Vec<MaestroHeatmapRow> {
    let mut cell_severity: BTreeMap<(String, String), String> = BTreeMap::new();
    let mut component_counts: BTreeMap<String, usize> = BTreeMap::new();

    for finding in per_finding_data {
        let component = finding.component.trim();
        let layer_raw = finding.maestro_layer.trim();
        let risk_level = finding.risk_level.trim();

        if component.is_empty() || layer_raw.is_empty() {
            continue;
        }

        let (layer_id, _) = split_maestro_layer(layer_raw);
        if !MAESTRO_LAYERS.contains(&layer_id.as_str()) {
            continue;
        }

        *component_counts.entry(component.to_string()).or_insert(0) += 1;

        let key = (component.to_string(), layer_id.clone());
        let should_replace = cell_severity
            .get(&key)
            .map(|existing| severity_rank(risk_level) > severity_rank(existing))
            .unwrap_or(true);

        if should_replace {
            cell_severity.insert(key, risk_level.to_string());
        }
    }

    let mut sorted_components: Vec<String> = component_counts.keys().cloned().collect();
    sorted_components.sort_by(|left, right| {
        component_counts[right]
            .cmp(&component_counts[left])
            .then_with(|| left.cmp(right))
    });
    sorted_components.truncate(10);

    let mut result = Vec::with_capacity(sorted_components.len());
    for component in sorted_components {
        let mut layers = BTreeMap::new();
        for layer_id in MAESTRO_LAYERS {
            let value = cell_severity
                .get(&(component.clone(), layer_id.to_string()))
                .cloned();
            layers.insert(layer_id.to_string(), value);
        }

        result.push(MaestroHeatmapRow { component, layers });
    }

    result
}

pub fn extract_prompt_scaffold(template_name: &str, repo_root: Option<&Path>) -> PromptScaffold {
    if !SCAFFOLD_TEMPLATES.contains(&template_name) {
        return PromptScaffold::default();
    }

    let repo_root =
        repo_root.unwrap_or_else(|| Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap());
    let Some(template_file) = TEMPLATE_FILES
        .iter()
        .find(|(name, _)| *name == template_name)
        .map(|(_, file)| *file)
    else {
        return PromptScaffold::default();
    };

    let template_path = repo_root
        .join("templates")
        .join("tachi")
        .join("infographics")
        .join(template_file);
    let Ok(content) = fs::read_to_string(template_path) else {
        return PromptScaffold::default();
    };

    let mut in_prompt_section = false;
    let mut in_fence = false;
    let mut fence_lines = Vec::new();
    let mut prompt_text = None;

    for line in content.lines() {
        let stripped = line.trim();
        if !in_prompt_section
            && stripped.starts_with("##")
            && stripped.contains("Gemini")
            && stripped.contains("Prompt")
        {
            in_prompt_section = true;
            continue;
        }

        if in_prompt_section && !in_fence && stripped.starts_with("```") {
            in_fence = true;
            continue;
        }

        if in_fence && stripped.starts_with("```") {
            prompt_text = Some(fence_lines.join("\n"));
            break;
        }

        if in_fence {
            fence_lines.push(line.to_string());
        }
    }

    let Some(prompt_text) = prompt_text else {
        return PromptScaffold::default();
    };

    let marker = "DATA CONTENT (render this";
    let Some(marker_idx) = prompt_text.find(marker) else {
        return PromptScaffold::default();
    };

    let marker_line_end = prompt_text[marker_idx..]
        .find('\n')
        .map(|offset| marker_idx + offset)
        .unwrap_or(prompt_text.len());

    let preamble = format!("{}\n", prompt_text[..marker_line_end].trim_end());

    let footer_idx = prompt_text
        .find("\nFOOTER")
        .or_else(|| prompt_text.find("FOOTER"))
        .unwrap_or(prompt_text.len());
    let postamble = prompt_text[footer_idx..].trim().to_string();

    PromptScaffold {
        preamble,
        postamble,
        found: true,
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

fn split_table_row(line: &str) -> Vec<String> {
    line.trim_matches('|')
        .split('|')
        .map(|cell| cell.trim().to_string())
        .collect()
}

fn is_separator_row(cells: &[String]) -> bool {
    !cells.is_empty()
        && cells
            .iter()
            .all(|cell| !cell.is_empty() && cell.chars().all(|ch| matches!(ch, '-' | ':' | ' ')))
}

fn column_index(headers: &[String], name: &str) -> Option<usize> {
    headers.iter().position(|header| header == name)
}

fn column_value(headers: &[String], cells: &[String], name: &str) -> String {
    column_index(headers, name)
        .and_then(|index| cells.get(index))
        .map(|value| value.trim().to_string())
        .unwrap_or_default()
}

fn is_maestro_agent_section(line: &str) -> bool {
    let trimmed = line.trim();
    trimmed.starts_with("### 3.") || trimmed.starts_with("### 4.")
}

fn split_maestro_layer(layer_raw: &str) -> (String, String) {
    let (layer_id, layer_name) = layer_raw
        .split_once('—')
        .or_else(|| layer_raw.split_once('–'))
        .map(|(id, name)| (id.trim().to_string(), name.trim().to_string()))
        .unwrap_or_else(|| (layer_raw.trim().to_string(), String::new()));

    (layer_id, layer_name)
}

fn severity_rank(label: &str) -> usize {
    SEVERITY_ORDER
        .iter()
        .position(|candidate| *candidate == label)
        .map(|index| SEVERITY_ORDER.len().saturating_sub(index))
        .unwrap_or(0)
}
