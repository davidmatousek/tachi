use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use serde::Serialize;

use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, build_threats_sarif, collect_audit,
    parse_component_metadata, parse_risk_md_section2, parse_risk_md_section3,
    parse_risk_md_section4, parse_threats_findings, prefix_for, render, ThreatSarifFinding,
};
use tachi_core::risk_scores::build_risk_scores_sarif;

use crate::progress::{CancellationToken, NoopProgressReporter, ProgressReporter};

mod runtime_helpers;
mod script_executor;

pub const CONTROL_PLANE_COMMANDS: [&str; 9] = [
    "install",
    "init",
    "update",
    "bootstrap",
    "infographic-data",
    "coverage-audit",
    "report-data",
    "risk-scores-sarif",
    "threats-sarif",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CommandOutputKind {
    Plain,
    CoverageSummary,
    Json,
    Typst,
    ThreatsSarif,
    RiskScoresSarif,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CommandDispatchKind {
    ControlPlane,
    CoverageAudit,
    InfographicData,
    ReportData,
    ThreatsSarif,
    RiskScoresSarif,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CommandSpec {
    pub name: &'static str,
    pub dispatch_kind: CommandDispatchKind,
    pub output_kind: CommandOutputKind,
}

#[derive(Debug, Clone, Copy)]
pub struct CommandRegistry {
    specs: &'static [CommandSpec],
}

pub const COMMAND_SPECS: [CommandSpec; 9] = [
    CommandSpec {
        name: "install",
        dispatch_kind: CommandDispatchKind::ControlPlane,
        output_kind: CommandOutputKind::Plain,
    },
    CommandSpec {
        name: "init",
        dispatch_kind: CommandDispatchKind::ControlPlane,
        output_kind: CommandOutputKind::Plain,
    },
    CommandSpec {
        name: "update",
        dispatch_kind: CommandDispatchKind::ControlPlane,
        output_kind: CommandOutputKind::Plain,
    },
    CommandSpec {
        name: "bootstrap",
        dispatch_kind: CommandDispatchKind::ControlPlane,
        output_kind: CommandOutputKind::Plain,
    },
    CommandSpec {
        name: "infographic-data",
        dispatch_kind: CommandDispatchKind::InfographicData,
        output_kind: CommandOutputKind::Json,
    },
    CommandSpec {
        name: "coverage-audit",
        dispatch_kind: CommandDispatchKind::CoverageAudit,
        output_kind: CommandOutputKind::CoverageSummary,
    },
    CommandSpec {
        name: "report-data",
        dispatch_kind: CommandDispatchKind::ReportData,
        output_kind: CommandOutputKind::Typst,
    },
    CommandSpec {
        name: "risk-scores-sarif",
        dispatch_kind: CommandDispatchKind::RiskScoresSarif,
        output_kind: CommandOutputKind::RiskScoresSarif,
    },
    CommandSpec {
        name: "threats-sarif",
        dispatch_kind: CommandDispatchKind::ThreatsSarif,
        output_kind: CommandOutputKind::ThreatsSarif,
    },
];

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

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct CommandOutput {
    pub status: i32,
    pub stdout: String,
    pub stderr: String,
}

pub fn control_plane_commands() -> &'static [&'static str] {
    &CONTROL_PLANE_COMMANDS
}

pub const fn command_registry() -> CommandRegistry {
    CommandRegistry::new(&COMMAND_SPECS)
}

pub fn command_spec(command: &str) -> Option<&'static CommandSpec> {
    command_registry().spec(command)
}

pub fn command_output_kind(command: &str) -> Option<CommandOutputKind> {
    command_spec(command).map(|spec| spec.output_kind)
}

pub fn command_dispatch_kind(command: &str) -> Option<CommandDispatchKind> {
    command_spec(command).map(|spec| spec.dispatch_kind)
}

impl CommandRegistry {
    pub const fn new(specs: &'static [CommandSpec]) -> Self {
        Self { specs }
    }

    pub const fn specs(&self) -> &'static [CommandSpec] {
        self.specs
    }

    pub fn names(&self) -> Vec<&'static str> {
        self.specs.iter().map(|spec| spec.name).collect()
    }

    pub fn spec(&self, command: &str) -> Option<&'static CommandSpec> {
        self.specs.iter().find(|spec| spec.name == command)
    }

    pub fn validate_unique(&self) -> Result<(), String> {
        let mut seen = BTreeSet::new();

        for spec in self.specs {
            if !seen.insert(spec.name) {
                return Err(format!("duplicate command in registry: {}", spec.name));
            }
        }

        Ok(())
    }
}

fn run_script_command(
    script_dir: &Path,
    script_name: &str,
    args: &[&str],
    repo_root: &Path,
) -> CommandOutput {
    let token = CancellationToken::new();
    let mut reporter = NoopProgressReporter;
    run_script_command_with_progress(
        script_dir,
        script_name,
        args,
        repo_root,
        &token,
        &mut reporter,
    )
}

pub(crate) fn run_script_command_with_progress(
    script_dir: &Path,
    script_name: &str,
    args: &[&str],
    repo_root: &Path,
    token: &CancellationToken,
    reporter: &mut dyn ProgressReporter,
) -> CommandOutput {
    script_executor::run_script_command_with_progress_using(
        &script_executor::SystemScriptExecutor,
        script_dir,
        script_name,
        args,
        repo_root,
        token,
        reporter,
    )
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

pub fn infographic_data_output(root: &Path, template: &str) -> Result<String, String> {
    let payload = build_infographic_payload(root, template)?;
    serde_json::to_string_pretty(&payload)
        .map_err(|err| format!("failed to serialize infographic payload: {err}"))
}

pub fn report_data_output(target_dir: &Path, template_dir: &Path) -> String {
    render_report_data_result(&report_data_result(target_dir, template_dir))
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

#[cfg(test)]
mod tests {
    use super::bootstrap_control_plane_args;

    #[test]
    fn bootstrap_control_plane_args_prepends_bootstrap_flag_without_mutating_input() {
        let args = vec!["--upstream-url=https://example.com/upstream.git", "--yes"];

        let shaped = bootstrap_control_plane_args(&args);

        assert_eq!(
            shaped,
            vec![
                String::from("--bootstrap"),
                String::from("--upstream-url=https://example.com/upstream.git"),
                String::from("--yes"),
            ]
        );
        assert_eq!(
            args,
            vec!["--upstream-url=https://example.com/upstream.git", "--yes"]
        );
    }
}

pub(crate) fn bootstrap_control_plane_args(args: &[&str]) -> Vec<String> {
    let mut bootstrap_args = Vec::with_capacity(args.len() + 1);
    bootstrap_args.push(String::from("--bootstrap"));
    bootstrap_args.extend(args.iter().map(|arg| (*arg).to_string()));
    bootstrap_args
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
    let bootstrap_args = bootstrap_control_plane_args(args);
    let scripts_dir = control_plane_scripts_dir(root);
    let bootstrap_args = bootstrap_args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>();
    run_script_command(&scripts_dir, "update.sh", &bootstrap_args, root)
}
