use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use crate::parsers::{parse_markdown_table, SeverityCounts, SEVERITY_ORDER};

pub const SEVERITY_COLORS: [(&str, &str); 5] = [
    ("Critical", "#DC2626"),
    ("High", "#EA580C"),
    ("Medium", "#CA8A04"),
    ("Low", "#2563EB"),
    ("Note", "#6B7280"),
];

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
