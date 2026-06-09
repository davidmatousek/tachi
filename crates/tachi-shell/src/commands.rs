use std::path::{Path, PathBuf};
use std::process::Command;
use std::process::Output;

use tachi_core::coverage_audit::{collect_audit, render};
use tachi_core::infographic::build_infographic_payload;
use tachi_core::parsers::parse_threats_findings;
use tachi_core::report_data::build_report_data_typst;
use tachi_core::risk_scores::{
    build_risk_scores_sarif, parse_risk_md_section2, parse_risk_md_section3, parse_risk_md_section4,
};
use tachi_core::sarif_common::{parse_component_metadata, prefix_for};
use tachi_core::threats_sarif::{build_threats_sarif, ThreatSarifFinding};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ThreatsSarifOutput {
    pub sarif: String,
    pub findings_count: usize,
    pub ag8_status: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RiskScoresSarifOutput {
    pub sarif: String,
    pub results_count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommandOutput {
    pub status: i32,
    pub stdout: String,
    pub stderr: String,
}

fn run_script_command(
    script_dir: &Path,
    script_name: &str,
    args: &[&str],
    repo_root: &Path,
) -> CommandOutput {
    let script_path = script_dir.join(script_name);
    let cwd = script_dir.parent().unwrap_or(repo_root);

    let result = Command::new(&script_path)
        .current_dir(cwd)
        .args(args)
        .output();

    match result {
        Ok(Output {
            status,
            stdout,
            stderr,
        }) => CommandOutput {
            status: status.code().unwrap_or(1),
            stdout: String::from_utf8_lossy(&stdout).to_string(),
            stderr: String::from_utf8_lossy(&stderr).to_string(),
        },
        Err(err) => CommandOutput {
            status: 1,
            stdout: String::new(),
            stderr: format!("failed to execute {script_name}: {err}\n"),
        },
    }
}

fn script_dir_for_repo_root(repo_root: &Path) -> PathBuf {
    let mut current = repo_root;
    while current != current.parent().unwrap_or(current) {
        let candidate = current.join("scripts");
        if candidate.exists() {
            return current.to_path_buf().join("scripts");
        }
        current = current.parent().unwrap_or(current);
    }

    repo_root.join("scripts")
}

pub fn control_plane_scripts_dir(repo_root: &Path) -> PathBuf {
    script_dir_for_repo_root(repo_root)
}

pub fn coverage_audit_output(root: &Path) -> String {
    let audit = collect_audit(root);
    render(&audit, root)
}

pub fn infographic_data_output(root: &Path, template: &str) -> Result<String, String> {
    let payload = build_infographic_payload(root, template)?;
    serde_json::to_string_pretty(&payload)
        .map_err(|err| format!("failed to serialize infographic payload: {err}"))
}

pub fn report_data_output(target_dir: &Path, template_dir: &Path) -> String {
    build_report_data_typst(target_dir, template_dir)
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
    let sarif = serde_json::to_string_pretty(&sarif)
        .map_err(|err| format!("failed to serialize threats SARIF: {err}"))?;

    Ok(ThreatsSarifOutput {
        sarif,
        findings_count: sarif_findings.len(),
        ag8_status,
    })
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
    let sarif = serde_json::to_string_pretty(&sarif)
        .map_err(|err| format!("failed to serialize risk scores SARIF: {err}"))?;

    Ok(RiskScoresSarifOutput {
        sarif,
        results_count: findings.len(),
    })
}

pub fn install_output(root: &Path, args: &[&str]) -> CommandOutput {
    let scripts_dir = control_plane_scripts_dir(root);
    run_script_command(&scripts_dir, "install.sh", args, root)
}

pub fn init_output(root: &Path, args: &[&str]) -> CommandOutput {
    let scripts_dir = control_plane_scripts_dir(root);
    run_script_command(&scripts_dir, "init.sh", args, root)
}

pub fn update_output(root: &Path, args: &[&str]) -> CommandOutput {
    let scripts_dir = control_plane_scripts_dir(root);
    run_script_command(&scripts_dir, "update.sh", args, root)
}

pub fn bootstrap_output(root: &Path, args: &[&str]) -> CommandOutput {
    let mut bootstrap_args = Vec::with_capacity(args.len() + 1);
    bootstrap_args.push("--bootstrap");
    bootstrap_args.extend_from_slice(args);

    let scripts_dir = control_plane_scripts_dir(root);
    run_script_command(&scripts_dir, "update.sh", &bootstrap_args, root)
}
