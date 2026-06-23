use std::fs;
use std::path::Path;

use serde_json::Value;

use crate::artifacts::{detect_artifacts, determine_tier};
use crate::metadata::resolve_report_project_name;

use super::{
    build_heat_map, build_maestro_heatmap_template_data, build_maestro_stack_template_data,
    build_top_findings, compute_risk_posture, compute_severity_percentages,
    derive_severity_counts_from_findings, extract_prompt_scaffold, InfographicMetadata,
    InfographicPayload, PromptScaffold, PromptScaffoldPayload,
};

pub fn build_infographic_payload_from_content(
    threats_content: &str,
    tier: u8,
    project_name: String,
    scaffold: Option<PromptScaffold>,
    source_file: Option<&Path>,
    template: &str,
) -> Result<Value, String> {
    let normalized_template = template.trim();

    if normalized_template.is_empty() {
        return Err(String::from("template is required"));
    }

    let findings = crate::parsers::parse_threats_findings(threats_content).unwrap_or_default();
    if findings.is_empty() {
        return Err(String::from("no findings parsed from threats.md"));
    }

    let severity = crate::parsers::parse_threats_severity(threats_content);
    let mut severity = if severity.total == 0 {
        derive_severity_counts_from_findings(&findings)
    } else {
        severity
    };
    if severity.total == 0 {
        severity.total = findings.len();
    }

    let scope = crate::parsers::parse_scope_data(threats_content);
    let component_count = scope.components.len();
    let risk_posture = compute_risk_posture(tier, component_count, &severity);
    let severity_distribution = compute_severity_percentages(&severity);

    let heat_map = build_heat_map(&findings);
    let (findings_ids, top_findings) = build_top_findings(&findings);

    let maestro_data = super::extract_maestro_data(threats_content);

    let template_data = match normalized_template {
        "executive-architecture" => {
            super::executive_architecture::build_executive_architecture_template_data(
                threats_content,
                tier,
                source_file,
                &findings,
            )?
        }
        "maestro-stack" => build_maestro_stack_template_data(&maestro_data),
        "maestro-heatmap" => build_maestro_heatmap_template_data(&maestro_data),
        "baseball-card" | "system-architecture" | "risk-funnel" => {
            serde_json::json!({"has_maestro_data": false})
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

    let prompt_scaffold = scaffold.map(|s| PromptScaffoldPayload {
        preamble: s.preamble,
        postamble: s.postamble,
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

pub fn build_infographic_payload(root: &Path, template: &str) -> Result<Value, String> {
    let normalized_template = template.trim();

    let threats_path = root.join("threats.md");
    let threats_content = fs::read_to_string(&threats_path)
        .map_err(|err| format!("failed to read {}: {err}", threats_path.display()))?;
    if threats_content.trim().is_empty() {
        return Err(String::from("threats.md is empty"));
    }

    let artifacts = detect_artifacts(root);
    let tier = determine_tier(&artifacts);
    let project_name = resolve_report_project_name(&threats_content, None, Some(root));
    let scaffold_raw = extract_prompt_scaffold(normalized_template, Some(root));
    let scaffold = if scaffold_raw.found {
        Some(scaffold_raw)
    } else {
        None
    };

    build_infographic_payload_from_content(
        &threats_content,
        tier,
        project_name,
        scaffold,
        Some(&threats_path),
        template,
    )
}
