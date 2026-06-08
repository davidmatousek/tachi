use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use crate::artifacts::{detect_artifacts, determine_tier};
use crate::coverage_taxonomy::{normalize_maestro_layer_label, MAESTRO_LAYERS};
use crate::parsers::{
    parse_markdown_table, parse_project_name, parse_scope_data, parse_threats_findings,
    parse_threats_severity, strip_bold, SeverityCounts, ThreatFinding, SEVERITY_ORDER,
};
use serde::Serialize;
use serde_json::{json, Map, Value};

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

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct MaestroLayerDistribution {
    pub layer_id: String,
    pub layer_name: String,
    pub finding_count: usize,
    pub highest_severity: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct MaestroFinding {
    pub id: String,
    pub component: String,
    pub maestro_layer: String,
    pub risk_level: String,
    pub threat: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct MaestroHeatmapRow {
    pub component: String,
    pub layers: BTreeMap<String, Option<String>>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct MaestroFindingsByLayer {
    pub layer_id: String,
    pub layer_name: String,
    pub findings: Vec<MaestroFinding>,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct MaestroData {
    pub maestro_layer_distribution: Vec<MaestroLayerDistribution>,
    pub most_exposed_layer: String,
    pub component_layer_map: BTreeMap<String, String>,
    pub per_finding_maestro: Vec<MaestroFinding>,
    pub maestro_heatmap: Vec<MaestroHeatmapRow>,
    pub has_maestro_data: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct SeverityPercentage {
    pub label: String,
    pub count: usize,
    pub percentage: usize,
    pub color: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct PerLayerTopFinding {
    pub id: String,
    pub threat: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct PerLayerSummary {
    pub layer_id: String,
    pub layer_name: String,
    pub finding_count: usize,
    pub highest_severity: String,
    pub top_findings: Vec<PerLayerTopFinding>,
}

#[derive(Debug, Clone, Serialize)]
pub struct InfographicPayload {
    pub template: String,
    pub metadata: InfographicMetadata,
    pub severity_distribution: Vec<SeverityPercentage>,
    pub heat_map: Vec<HeatMapRow>,
    pub top_findings: Vec<TopFinding>,
    pub findings_ids: Vec<String>,
    pub template_data: Value,
    pub has_maestro_data: bool,
    pub prompt_scaffold: Option<PromptScaffoldPayload>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PromptScaffoldPayload {
    pub preamble: String,
    pub postamble: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct TopFinding {
    pub id: String,
    pub component: String,
    pub risk_level: String,
    pub score: f64,
    pub threat: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct HeatMapRow {
    pub component: String,
    pub critical: usize,
    pub high: usize,
    pub medium: usize,
    pub low: usize,
    pub total: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct InfographicMetadata {
    pub agent_count: usize,
    pub data_source_type: String,
    pub note_count: usize,
    pub project_name: String,
    pub risk_posture: String,
    pub scan_date: String,
    pub schema_version: String,
    pub template: String,
    pub tier: u8,
    pub total_findings: usize,
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

        let normalized_layer = normalize_maestro_layer_label(layer_raw);
        let (layer_id, layer_name) = split_maestro_layer(&normalized_layer);
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

pub fn parse_component_layer_mapping(threats_content: &str) -> BTreeMap<String, String> {
    parse_markdown_table(threats_content, "### Components")
        .into_iter()
        .filter_map(|row| {
            let component = row
                .get("Component")
                .map(|value| value.trim())
                .filter(|value| !value.is_empty())?;
            let layer = row
                .get("MAESTRO Layer")
                .map(|value| value.trim())
                .filter(|value| !value.is_empty())?;

            Some((
                String::from(component),
                normalize_maestro_layer_label(layer),
            ))
        })
        .collect()
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
            let maestro_layer =
                normalize_maestro_layer_label(&column_value(headers, &cells, "MAESTRO Layer"));

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

pub fn extract_maestro_data(threats_content: &str) -> MaestroData {
    let maestro_layer_distribution = parse_maestro_layer_distribution(threats_content);
    let component_layer_map = parse_component_layer_mapping(threats_content);
    let per_finding_maestro = parse_per_finding_maestro(threats_content);
    let maestro_heatmap = compute_maestro_heatmap(&per_finding_maestro);
    let most_exposed_layer = compute_most_exposed_layer(&maestro_layer_distribution);

    let has_maestro_data =
        !maestro_layer_distribution.is_empty() || !per_finding_maestro.is_empty();

    MaestroData {
        maestro_layer_distribution,
        most_exposed_layer,
        component_layer_map,
        per_finding_maestro,
        maestro_heatmap,
        has_maestro_data,
    }
}

pub fn group_maestro_findings_by_layer(data: &MaestroData) -> Vec<MaestroFindingsByLayer> {
    let mut groups: BTreeMap<String, MaestroFindingsByLayer> = BTreeMap::new();

    for layer in &data.maestro_layer_distribution {
        groups.insert(
            layer.layer_id.clone(),
            MaestroFindingsByLayer {
                layer_id: layer.layer_id.clone(),
                layer_name: layer.layer_name.clone(),
                findings: Vec::new(),
            },
        );
    }

    for finding in &data.per_finding_maestro {
        let layer_raw = normalize_maestro_layer_label(&finding.maestro_layer);
        let (layer_id, layer_name) = if layer_raw.is_empty() {
            (String::from("Unclassified"), String::from("Unclassified"))
        } else {
            split_maestro_layer(&layer_raw)
        };

        let entry = groups
            .entry(layer_id.clone())
            .or_insert_with(|| MaestroFindingsByLayer {
                layer_id: layer_id.clone(),
                layer_name: layer_name.clone(),
                findings: Vec::new(),
            });

        if entry.layer_name.is_empty() {
            entry.layer_name = layer_name;
        }

        entry.findings.push(finding.clone());
    }

    let mut grouped: Vec<_> = groups.into_values().collect();
    grouped.sort_by(|left, right| {
        maestro_layer_sort_key(&left.layer_id).cmp(&maestro_layer_sort_key(&right.layer_id))
    });
    grouped.retain(|group| !group.findings.is_empty());
    grouped
}

pub fn compute_maestro_heatmap(per_finding_data: &[MaestroFinding]) -> Vec<MaestroHeatmapRow> {
    let mut cell_severity: BTreeMap<(String, String), String> = BTreeMap::new();
    let mut component_counts: BTreeMap<String, usize> = BTreeMap::new();

    for finding in per_finding_data {
        let component = finding.component.trim();
        let layer_raw = normalize_maestro_layer_label(&finding.maestro_layer);
        let risk_level = finding.risk_level.trim();

        if component.is_empty() || layer_raw.is_empty() {
            continue;
        }

        let (layer_id, _) = split_maestro_layer(&layer_raw);
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

pub fn build_infographic_payload(root: &Path, template: &str) -> Result<Value, String> {
    let normalized_template = template.trim();

    if normalized_template.is_empty() {
        return Err(String::from("template is required"));
    }

    let threats_path = root.join("threats.md");
    let threats_content = fs::read_to_string(&threats_path)
        .map_err(|err| format!("failed to read {}: {err}", threats_path.display()))?;
    if threats_content.trim().is_empty() {
        return Err(String::from("threats.md is empty"));
    }

    let findings = parse_threats_findings(&threats_content).unwrap_or_default();
    if findings.is_empty() {
        return Err(String::from("no findings parsed from threats.md"));
    }

    let artifacts = detect_artifacts(root);
    let tier = determine_tier(&artifacts);

    let severity = parse_threats_severity(&threats_content);
    let mut severity = if severity.total == 0 {
        derive_severity_counts_from_findings(&findings)
    } else {
        severity
    };
    if severity.total == 0 {
        severity.total = findings.len();
    }

    let scope = parse_scope_data(&threats_content);
    let project_name = parse_project_name(&threats_content, None, Some(root));
    let component_count = scope.components.len();
    let risk_posture = compute_risk_posture(tier, component_count, &severity);
    let severity_distribution = compute_severity_percentages(&severity);

    let heat_map = build_heat_map(&findings);
    let (findings_ids, top_findings) = build_top_findings(&findings);

    let maestro_data = extract_maestro_data(&threats_content);

    let template_data = match normalized_template {
        "maestro-stack" => build_maestro_stack_template_data(&maestro_data),
        "maestro-heatmap" => build_maestro_heatmap_template_data(&maestro_data),
        "baseball-card" | "system-architecture" | "risk-funnel" => {
            json!({"has_maestro_data": false})
        }
        _ => {
            return Err(format!("unsupported template: {normalized_template}"));
        }
    };

    let has_maestro_data = template_data
        .get("has_maestro_data")
        .and_then(Value::as_bool)
        .unwrap_or(false);

    let data_source_type = match tier {
        1 => "compensating-controls",
        2 => "risk-scores",
        _ => "threats-only",
    };

    let scaffold = extract_prompt_scaffold(normalized_template, Some(root));
    let prompt_scaffold = scaffold.found.then_some(PromptScaffoldPayload {
        preamble: scaffold.preamble,
        postamble: scaffold.postamble,
    });

    let metadata = InfographicMetadata {
        agent_count: component_count,
        data_source_type: String::from(data_source_type),
        note_count: severity.note,
        project_name,
        risk_posture,
        scan_date: String::from("unknown"),
        schema_version: String::from("1.1"),
        template: normalized_template.to_string(),
        tier,
        total_findings: findings.len(),
    };

    let payload = InfographicPayload {
        template: normalized_template.to_string(),
        metadata,
        severity_distribution,
        heat_map,
        top_findings,
        findings_ids,
        template_data,
        has_maestro_data,
        prompt_scaffold,
    };

    serde_json::to_value(payload).map_err(|err| format!("failed to build payload: {err}"))
}

fn compute_risk_posture(tier: u8, component_count: usize, severity: &SeverityCounts) -> String {
    let tier_label = match tier {
        1 => "Residual risk",
        2 => "Inherent risk",
        _ => "Severity assessment",
    };
    let critical = severity.critical;
    let high = severity.high;
    let total_components = std::cmp::max(component_count, 1);
    format!(
        "{tier_label} — {critical} Critical and {high} High findings across {total_components} components"
    )
}

fn derive_severity_counts_from_findings(findings: &[ThreatFinding]) -> SeverityCounts {
    let mut counts = SeverityCounts::default();

    for finding in findings {
        match finding.risk_level.as_str() {
            "Critical" => counts.critical += 1,
            "High" => counts.high += 1,
            "Medium" => counts.medium += 1,
            "Low" => counts.low += 1,
            "Note" => counts.note += 1,
            _ => {}
        }
        counts.total += 1;
    }

    counts
}

fn build_top_findings(findings: &[ThreatFinding]) -> (Vec<String>, Vec<TopFinding>) {
    let mut ranked = findings.to_vec();
    ranked.sort_by(|left, right| {
        severity_rank(&right.risk_level)
            .cmp(&severity_rank(&left.risk_level))
            .then_with(|| left.id.cmp(&right.id))
    });

    let top_findings = ranked
        .iter()
        .take(5)
        .map(|finding| TopFinding {
            id: finding.id.clone(),
            component: finding.component.clone(),
            risk_level: finding.risk_level.clone(),
            score: 0.0,
            threat: finding.threat.clone(),
        })
        .collect::<Vec<_>>();

    let findings_ids = ranked.iter().map(|finding| finding.id.clone()).collect();

    (findings_ids, top_findings)
}

fn build_heat_map(findings: &[ThreatFinding]) -> Vec<HeatMapRow> {
    let mut matrix: BTreeMap<String, HeatMapRow> = BTreeMap::new();

    for finding in findings {
        let row = matrix
            .entry(finding.component.clone())
            .or_insert_with(|| HeatMapRow {
                component: finding.component.clone(),
                critical: 0,
                high: 0,
                medium: 0,
                low: 0,
                total: 0,
            });

        match finding.risk_level.as_str() {
            "Critical" => row.critical += 1,
            "High" => row.high += 1,
            "Medium" => row.medium += 1,
            "Low" => row.low += 1,
            _ => {}
        }
        row.total += 1;
    }

    let mut rows = matrix.into_values().collect::<Vec<_>>();
    rows.sort_by(|left, right| {
        right
            .total
            .cmp(&left.total)
            .then_with(|| left.component.cmp(&right.component))
    });
    rows
}

fn build_maestro_stack_template_data(maestro_data: &MaestroData) -> Value {
    let per_layer_summaries = maestro_data
        .maestro_layer_distribution
        .iter()
        .map(|layer| {
            let mut layer_findings = maestro_data
                .per_finding_maestro
                .iter()
                .filter(|f| {
                    normalize_maestro_layer_label(&f.maestro_layer).starts_with(&layer.layer_id)
                })
                .collect::<Vec<_>>();

            layer_findings.sort_by(|left, right| {
                severity_rank(&right.risk_level)
                    .cmp(&severity_rank(&left.risk_level))
                    .then_with(|| left.id.cmp(&right.id))
            });

            let top = layer_findings
                .iter()
                .take(2)
                .map(|finding| PerLayerTopFinding {
                    id: finding.id.clone(),
                    threat: finding.threat.chars().take(120).collect(),
                });

            json!({
                "layer_id": layer.layer_id,
                "layer_name": layer.layer_name,
                "finding_count": layer.finding_count,
                "highest_severity": layer.highest_severity,
                "top_findings": top.collect::<Vec<_>>(),
            })
        })
        .collect::<Vec<_>>();

    json!({
        "maestro_layer_distribution": to_value_layer_distribution(&maestro_data.maestro_layer_distribution),
        "most_exposed_layer": maestro_data.most_exposed_layer,
        "per_layer_summaries": per_layer_summaries,
        "has_maestro_data": maestro_data.has_maestro_data,
    })
}

fn build_maestro_heatmap_template_data(maestro_data: &MaestroData) -> Value {
    json!({
        "maestro_heatmap": to_value_heatmap(&maestro_data.maestro_heatmap),
        "maestro_layer_distribution": to_value_layer_distribution(&maestro_data.maestro_layer_distribution),
        "has_maestro_data": maestro_data.has_maestro_data,
    })
}

fn to_value_layer_distribution(layers: &[MaestroLayerDistribution]) -> Vec<Value> {
    layers
        .iter()
        .map(|layer| {
            json!({
                "layer_id": layer.layer_id,
                "layer_name": layer.layer_name,
                "finding_count": layer.finding_count,
                "highest_severity": layer.highest_severity,
            })
        })
        .collect()
}

fn to_value_heatmap(heatmap: &[MaestroHeatmapRow]) -> Vec<Value> {
    let mut rows = Vec::new();

    for row in heatmap {
        let mut value_map: Map<String, Value> = Map::new();
        value_map.insert(
            String::from("component"),
            Value::String(row.component.clone()),
        );

        for layer in MAESTRO_LAYERS {
            value_map.insert(
                layer.to_string(),
                match row.layers.get(layer) {
                    Some(Some(score)) => Value::String(score.clone()),
                    _ => Value::Null,
                },
            );
        }

        rows.push(Value::Object(value_map));
    }

    rows
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
    let normalized = layer_raw.trim();
    for separator in ['—', '–', '-'] {
        if let Some((layer_id, layer_name)) = normalized.split_once(separator) {
            return (layer_id.trim().to_string(), layer_name.trim().to_string());
        }
    }

    (normalized.to_string(), String::new())
}

fn maestro_layer_sort_key(layer_id: &str) -> (u8, usize, String) {
    if let Some(position) = MAESTRO_LAYERS
        .iter()
        .position(|candidate| *candidate == layer_id)
    {
        return (0, position, String::new());
    }

    if layer_id == "Unclassified" {
        return (1, 0, String::new());
    }

    (2, 0, layer_id.to_string())
}

fn severity_rank(label: &str) -> usize {
    SEVERITY_ORDER
        .iter()
        .position(|candidate| *candidate == label)
        .map(|index| SEVERITY_ORDER.len().saturating_sub(index))
        .unwrap_or(0)
}
