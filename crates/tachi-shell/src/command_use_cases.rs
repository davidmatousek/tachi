use std::path::Path;

use serde_json::to_string_pretty;

use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, build_threats_sarif, collect_audit,
    parse_component_metadata, parse_risk_md_section2, parse_risk_md_section3,
    parse_risk_md_section4, parse_threats_findings, prefix_for, render, ThreatSarifFinding,
};
use tachi_core::risk_scores::build_risk_scores_sarif;

pub fn coverage_audit_output(root: &Path) -> String {
    let audit = collect_audit(root);
    render(&audit, root)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReportDataResult {
    pub typst: String,
}

pub fn report_data_result(target_dir: &Path, template_dir: &Path) -> ReportDataResult {
    ReportDataResult {
        typst: build_report_data_typst(target_dir, template_dir),
    }
}

pub fn validate_report_data_result(result: &ReportDataResult) -> Result<(), String> {
    if result.typst.starts_with("#let project-name =") {
        Ok(())
    } else {
        Err(String::from(
            "report-data typed result missing project-name binding",
        ))
    }
}

pub fn render_report_data_result(result: &ReportDataResult) -> String {
    result.typst.clone()
}

pub fn report_data_output(target_dir: &Path, template_dir: &Path) -> String {
    render_report_data_result(&report_data_result(target_dir, template_dir))
}

pub fn infographic_data_output(root: &Path, template: &str) -> Result<String, String> {
    let payload = build_infographic_payload(root, template)?;
    to_string_pretty(&payload).map_err(|err| format!("failed to serialize infographic payload: {err}"))
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ThreatsSarifOutput {
    pub sarif: String,
    pub findings_count: usize,
    pub ag8_status: Option<String>,
}

pub fn threats_sarif_output(input: &Path) -> Result<ThreatsSarifOutput, String> {
    let threats_md = std::fs::read_to_string(input)
        .map_err(|err| format!("failed to read {}: {err}", input.display()))?;
    let findings = parse_threats_findings(&threats_md)?;
    let component_meta = parse_component_metadata(&threats_md);
    let ag8_status = findings
        .iter()
        .find(|finding| finding.id == "AG-8")
        .and_then(|finding| finding.delta_status.clone());

    let sarif_findings = findings
        .into_iter()
        .map(|finding| ThreatSarifFinding {
            id: finding.id.clone(),
            prefix: prefix_for(&finding.id),
            status: finding.delta_status.unwrap_or_default(),
            component: finding.component,
            maestro: String::new(),
            agentic_pattern: finding.agentic_pattern,
            threat: finding.threat,
            owasp_ref: String::new(),
            likelihood: finding.likelihood,
            impact: finding.impact,
            risk_level: finding.risk_level,
            mitigation: finding.mitigation,
        })
        .collect::<Vec<_>>();
    let sarif = build_threats_sarif(&sarif_findings, &component_meta);
    let sarif = to_string_pretty(&sarif)
        .map_err(|err| format!("failed to serialize threats SARIF: {err}"))?;

    Ok(ThreatsSarifOutput {
        sarif,
        findings_count: sarif_findings.len(),
        ag8_status,
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RiskScoresSarifOutput {
    pub sarif: String,
    pub results_count: usize,
}

pub fn risk_scores_sarif_output(
    risk_scores: &Path,
    threats: &Path,
) -> Result<RiskScoresSarifOutput, String> {
    let risk_md = std::fs::read_to_string(risk_scores)
        .map_err(|err| format!("failed to read {}: {err}", risk_scores.display()))?;
    let threats_md = std::fs::read_to_string(threats)
        .map_err(|err| format!("failed to read {}: {err}", threats.display()))?;

    let findings = parse_risk_md_section2(&risk_md);
    let section3 = parse_risk_md_section3(&risk_md);
    let section4 = parse_risk_md_section4(&risk_md);
    let threat_findings = parse_threats_findings(&threats_md)?;

    let threats_status = threat_findings
        .iter()
        .filter_map(|finding| {
            finding.delta_status.as_ref().map(|status| {
                (
                    finding.id.clone(),
                    status
                        .trim()
                        .trim_start_matches('[')
                        .trim_end_matches(']')
                        .to_string(),
                )
            })
        })
        .collect();
    let threats_full = threat_findings
        .iter()
        .map(|finding| {
            (
                finding.id.clone(),
                (finding.threat.clone(), finding.mitigation.clone()),
            )
        })
        .collect();
    let source_attribution = threat_findings
        .iter()
        .filter_map(|finding| {
            finding
                .source_attribution
                .clone()
                .map(|records| (finding.id.clone(), records))
        })
        .collect();
    let component_meta = parse_component_metadata(&threats_md);

    let sarif = build_risk_scores_sarif(
        &findings,
        &section3,
        &section4,
        &threats_status,
        &threats_full,
        &source_attribution,
        &component_meta,
    );
    let sarif = to_string_pretty(&sarif)
        .map_err(|err| format!("failed to serialize risk scores SARIF: {err}"))?;

    Ok(RiskScoresSarifOutput {
        sarif,
        results_count: findings.len(),
    })
}
