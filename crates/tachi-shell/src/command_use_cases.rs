use std::path::Path;

use serde_json::to_string_pretty;

use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, build_risk_scores_sarif,
    build_threats_sarif, collect_audit, parse_component_metadata, parse_risk_md_section2,
    parse_risk_md_section3, parse_risk_md_section4, parse_threats_findings, prefix_for, render,
    RiskScoreSarifInputs, ThreatSarifFinding,
};

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
    to_string_pretty(&payload)
        .map_err(|err| format!("failed to serialize infographic payload: {err}"))
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
    let source_threats_uri = input.display().to_string();
    let sarif = build_threats_sarif(&sarif_findings, &component_meta, &source_threats_uri);
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

    let findings = parse_risk_md_section2(&risk_md)?;
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
    let source_threats_uri = threats.display().to_string();

    let sarif = build_risk_scores_sarif(
        &findings,
        &RiskScoreSarifInputs {
            section3: &section3,
            section4: &section4,
            threats_status: &threats_status,
            threats_full: &threats_full,
            source_attribution: &source_attribution,
            component_meta: &component_meta,
            source_threats_uri: &source_threats_uri,
        },
    );
    let sarif = to_string_pretty(&sarif)
        .map_err(|err| format!("failed to serialize risk scores SARIF: {err}"))?;

    Ok(RiskScoresSarifOutput {
        sarif,
        results_count: findings.len(),
    })
}

#[cfg(test)]
mod tests {
    use super::risk_scores_sarif_output;
    use serde_json::Value;
    use std::path::PathBuf;

    fn unique_temp_dir(name: &str) -> PathBuf {
        let suffix = format!(
            "{}-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .expect("clock")
                .as_nanos(),
            name
        );
        std::env::temp_dir().join(format!("tachi-{suffix}"))
    }

    #[test]
    fn risk_scores_sarif_output_returns_err_on_malformed_scores() {
        let root = unique_temp_dir("risk-scores");
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(&root).expect("create temp root");

        let risk_scores = root.join("risk.md");
        let threats = root.join("threats.md");
        std::fs::write(
            &risk_scores,
            r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------------|--------------|--------------|-----------|----------|-----|-------------|
| AG-8 | Agent | Prompt injection | malformed_score | 9.0 | 8.5 | 8.0 | 8.8 | High | 7 | Monitor |
"#,
        )
        .expect("write malformed risk scores");
        std::fs::write(&threats, "# Threat Model\n").expect("write threats");

        let err = risk_scores_sarif_output(&risk_scores, &threats)
            .expect_err("malformed scores should fail closed");
        assert!(
            err.contains("failed to parse CVSS score for AG-8"),
            "unexpected error: {err}"
        );

        let _ = std::fs::remove_dir_all(&root);
    }

    #[test]
    fn risk_scores_sarif_output_uses_threats_input_path_as_source_uri() {
        let root = unique_temp_dir("risk-scores-uri");
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(&root).expect("create temp root");

        let risk_scores = root.join("risk.md");
        let threats = root.join("custom-threats.md");
        std::fs::write(
            &risk_scores,
            r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------------|--------------|--------------|-----------|----------|-----|-------------|
| AG-8 | Agent | Prompt injection | 9.1 | 9.0 | 8.5 | 8.0 | 8.8 | High | 7 | Monitor |
"#,
        )
        .expect("write risk scores");
        std::fs::write(&threats, "# Threat Model\n").expect("write threats");

        let payload =
            risk_scores_sarif_output(&risk_scores, &threats).expect("risk scores should serialize");
        let sarif: Value = serde_json::from_str(&payload.sarif).expect("parse SARIF");
        assert_eq!(
            sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]
                ["uri"],
            threats.display().to_string()
        );

        let _ = std::fs::remove_dir_all(&root);
    }
}
