use crate::parsers::parse_markdown_table;

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct AttackChain {
    pub chain_id: String,
    pub title: String,
    pub layers: Vec<String>,
    pub max_severity: String,
    pub findings: Vec<AttackChainFinding>,
    pub narrative: String,
    pub chain_breaking_controls: Vec<ChainBreakingControl>,
    pub surfaced: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct AttackChainFinding {
    pub finding_id: String,
    pub maestro_layer: String,
    pub role: String,
    pub component: String,
    pub category: String,
    pub severity: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct ChainBreakingControl {
    pub target_finding_id: String,
    pub target_layer: String,
    pub rationale: String,
    pub recommendation: String,
}

pub fn parse_attack_chains(content: Option<&str>) -> Vec<AttackChain> {
    let Some(content) = content.map(str::trim).filter(|value| !value.is_empty()) else {
        return Vec::new();
    };

    let lines: Vec<&str> = content.split('\n').collect();
    let mut chain_starts = Vec::new();

    for (index, line) in lines.iter().enumerate() {
        let trimmed = line.trim();
        if let Some((chain_id, title)) = parse_chain_heading(trimmed) {
            chain_starts.push((index, chain_id, title));
        }
    }

    if chain_starts.is_empty() {
        return Vec::new();
    }

    let mut chains = Vec::new();
    for (idx, (start_line, chain_id, title)) in chain_starts.iter().enumerate() {
        let end_line = chain_starts
            .get(idx + 1)
            .map(|(next_start, _, _)| *next_start)
            .unwrap_or(lines.len());

        let section_lines = &lines[*start_line..end_line];
        let section_text = section_lines.join("\n");

        let layers = parse_layers(&section_text);
        let max_severity = parse_max_severity(&section_text);
        let surfaced = parse_surfaced(&section_text);
        let findings = parse_member_findings(&section_text);
        let narrative = parse_chain_narrative(section_lines);
        let chain_breaking_controls = parse_chain_breaking_controls(&section_text);

        chains.push(AttackChain {
            chain_id: chain_id.clone(),
            title: title.clone(),
            layers,
            max_severity,
            findings,
            narrative,
            chain_breaking_controls,
            surfaced,
        });
    }

    chains
}

fn parse_chain_heading(line: &str) -> Option<(String, String)> {
    let heading = line.strip_prefix("### ")?;
    let (chain_id, title) = heading.split_once(':')?;
    let chain_id = chain_id.trim();
    if !chain_id.starts_with("CHAIN-") {
        return None;
    }

    Some((chain_id.to_string(), title.trim().to_string()))
}

fn parse_layers(section_text: &str) -> Vec<String> {
    let Some(line) = section_text
        .lines()
        .find(|line| line.trim_start().starts_with("**Layers**:"))
    else {
        return Vec::new();
    };

    let layers_str = line
        .split_once(':')
        .map(|(_, rest)| rest.trim())
        .unwrap_or_default();
    if layers_str.is_empty() {
        return Vec::new();
    }

    layers_str
        .replace("—>", "|")
        .replace("->", "|")
        .replace('→', "|")
        .split('|')
        .map(str::trim)
        .filter(|layer| !layer.is_empty())
        .map(str::to_string)
        .collect()
}

fn parse_max_severity(section_text: &str) -> String {
    section_text
        .lines()
        .find(|line| line.trim_start().starts_with("**Max Severity**:"))
        .and_then(|line| {
            line.split_once(':')
                .map(|(_, rest)| rest.trim().to_string())
        })
        .and_then(|value| value.split_whitespace().next().map(str::to_string))
        .unwrap_or_default()
}

fn parse_surfaced(section_text: &str) -> bool {
    section_text
        .lines()
        .find(|line| line.trim_start().starts_with("**Surfaced**:"))
        .and_then(|line| {
            line.split_once(':')
                .map(|(_, rest)| rest.trim().to_string())
        })
        .map(|value| matches!(value.to_ascii_lowercase().as_str(), "yes" | "true"))
        .unwrap_or(false)
}

fn parse_member_findings(section_text: &str) -> Vec<AttackChainFinding> {
    parse_markdown_table(section_text, "#### Member Findings")
        .into_iter()
        .map(|row| AttackChainFinding {
            finding_id: row.get("Finding ID").cloned().unwrap_or_default(),
            maestro_layer: row.get("MAESTRO Layer").cloned().unwrap_or_default(),
            role: row.get("Role").cloned().unwrap_or_default(),
            component: row.get("Component").cloned().unwrap_or_default(),
            category: row.get("Category").cloned().unwrap_or_default(),
            severity: row.get("Severity").cloned().unwrap_or_default(),
        })
        .collect()
}

fn parse_chain_narrative(section_lines: &[&str]) -> String {
    let mut text_start = None;
    for (index, line) in section_lines.iter().enumerate() {
        if line.trim_start().starts_with("#### Attack Progression") {
            text_start = Some(index + 1);
            break;
        }
    }

    let Some(text_start) = text_start else {
        return String::new();
    };

    let mut text_lines = Vec::new();
    for line in section_lines.iter().skip(text_start) {
        let trimmed = line.trim();
        if trimmed.starts_with("####") || trimmed.starts_with("###") {
            break;
        }
        if !trimmed.is_empty() {
            text_lines.push(trimmed);
        }
    }

    text_lines.join(" ")
}

fn parse_chain_breaking_controls(section_text: &str) -> Vec<ChainBreakingControl> {
    let lines: Vec<&str> = section_text.split('\n').collect();
    let Some(ctrl_start) = lines
        .iter()
        .position(|line| {
            line.trim_start()
                .starts_with("#### Chain-Breaking Controls")
        })
        .map(|index| index + 1)
    else {
        return Vec::new();
    };

    let mut controls = Vec::new();
    let mut current: Option<ChainBreakingControl> = None;

    for line in lines.iter().skip(ctrl_start) {
        let trimmed = line.trim();
        if trimmed.starts_with("###") && !trimmed.starts_with("#### Chain-Breaking") {
            break;
        }
        if trimmed.starts_with("####") && !trimmed.starts_with("#### Chain-Breaking") {
            break;
        }

        if let Some((target_finding_id, target_layer)) = parse_target_line(trimmed) {
            if let Some(control) = current.take() {
                controls.push(control);
            }
            current = Some(ChainBreakingControl {
                target_finding_id,
                target_layer,
                rationale: String::new(),
                recommendation: String::new(),
            });
            continue;
        }

        if let Some(value) = trimmed.strip_prefix("**Rationale**:") {
            if let Some(control) = current.as_mut() {
                control.rationale = value.trim().to_string();
            }
            continue;
        }

        if let Some(value) = trimmed.strip_prefix("**Recommendation**:") {
            if let Some(control) = current.as_mut() {
                control.recommendation = value.trim().to_string();
            }
        }
    }

    if let Some(control) = current {
        controls.push(control);
    }

    controls
}

fn parse_target_line(line: &str) -> Option<(String, String)> {
    let rest = line.strip_prefix("**Target**:")?.trim();
    if let Some((finding_id, layer_part)) = rest.split_once('(') {
        let target_layer = layer_part.trim().trim_end_matches(')').trim();
        Some((finding_id.trim().to_string(), target_layer.to_string()))
    } else {
        Some((rest.to_string(), String::new()))
    }
}
