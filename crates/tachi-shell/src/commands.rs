use std::path::{Path, PathBuf};
use std::collections::BTreeSet;
use std::process::Command;
use std::process::Stdio;
use std::time::Instant;
use std::thread::sleep;
use std::time::Duration;
use std::io::{BufReader, Read};

#[cfg(unix)]
use std::os::unix::process::CommandExt;

use tachi_core::facade::{
    build_infographic_payload, build_report_data_typst, build_threats_sarif, collect_audit,
    parse_component_metadata, parse_risk_md_section2, parse_risk_md_section3,
    parse_risk_md_section4, parse_threats_findings, prefix_for, render, ThreatSarifFinding,
};
use tachi_core::risk_scores::build_risk_scores_sarif;

use crate::progress::{
    emit_progress_event, CancellationToken, NoopProgressReporter, ProgressReporter,
};

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

const DEFAULT_EXECUTION_TIMEOUT: Duration = Duration::from_secs(30);
const DEFAULT_OUTPUT_CAP_BYTES: usize = 64 * 1024;
const POLL_INTERVAL: Duration = Duration::from_millis(10);

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
    let timeout = execution_timeout();
    let output_cap = execution_output_cap();

    emit_progress_event(reporter, script_name, "starting");
    if token.is_cancelled() {
        emit_progress_event(reporter, script_name, "cancelled");
        return CommandOutput {
            status: 130,
            stdout: String::new(),
            stderr: format!("{script_name} cancelled\n"),
        };
    }

    let script_path = script_dir.join(script_name);
    let cwd = script_dir.parent().unwrap_or(repo_root);

    let spawn_result = Command::new(&script_path)
        .current_dir(cwd)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .process_group(0)
        .spawn();

    let mut child = match spawn_result {
        Ok(child) => child,
        Err(err) => {
            emit_progress_event(reporter, script_name, "failed");
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("failed to execute {script_name}: {err}\n"),
            };
        }
    };
    let stdout = child.stdout.take().expect("child stdout piped");
    let stderr = child.stderr.take().expect("child stderr piped");
    let stdout_handle = std::thread::spawn(move || capture_stream(stdout, output_cap));
    let stderr_handle = std::thread::spawn(move || capture_stream(stderr, output_cap));
    let start = Instant::now();
    let mut running_emitted = false;

    loop {
        if token.is_cancelled() {
            terminate_process_group(&mut child);
            return finalize_script_output(
                script_name,
                reporter,
                child.wait(),
                stdout_handle,
                stderr_handle,
                130,
                "cancelled",
            );
        }

        if start.elapsed() >= timeout {
            terminate_process_group(&mut child);
            return finalize_script_output(
                script_name,
                reporter,
                child.wait(),
                stdout_handle,
                stderr_handle,
                124,
                "timed out",
            );
        }

        match child.try_wait() {
            Ok(Some(status)) => {
                let stdout = stdout_handle.join().unwrap_or_default();
                let stderr = stderr_handle.join().unwrap_or_default();
                emit_progress_event(reporter, script_name, "completed");
                return CommandOutput {
                    status: status.code().unwrap_or(1),
                    stdout: String::from_utf8_lossy(&stdout).to_string(),
                    stderr: String::from_utf8_lossy(&stderr).to_string(),
                };
            }
            Ok(None) => {
                if !running_emitted {
                    emit_progress_event(reporter, script_name, "running");
                    running_emitted = true;
                }
                sleep(POLL_INTERVAL);
            }
            Err(err) => {
                terminate_process_group(&mut child);
                emit_progress_event(reporter, script_name, "failed");
                let stdout = stdout_handle.join().unwrap_or_default();
                let stderr = stderr_handle.join().unwrap_or_default();
                return CommandOutput {
                    status: 1,
                    stdout: String::from_utf8_lossy(&stdout).to_string(),
                    stderr: format!(
                        "failed to monitor {script_name}: {err}\n{}",
                        String::from_utf8_lossy(&stderr)
                    ),
                };
            }
        }
    }
}

fn finalize_script_output(
    script_name: &str,
    reporter: &mut dyn ProgressReporter,
    wait_result: std::io::Result<std::process::ExitStatus>,
    stdout_handle: std::thread::JoinHandle<Vec<u8>>,
    stderr_handle: std::thread::JoinHandle<Vec<u8>>,
    status: i32,
    phase: &str,
) -> CommandOutput {
    let stdout = stdout_handle.join().unwrap_or_default();
    let stderr = stderr_handle.join().unwrap_or_default();
    emit_progress_event(reporter, script_name, phase);
    match wait_result {
        Ok(output_status) => CommandOutput {
            status: if status == 130 || status == 124 {
                status
            } else {
                output_status.code().unwrap_or(1)
            },
            stdout: String::from_utf8_lossy(&stdout).to_string(),
            stderr: String::from_utf8_lossy(&stderr).to_string(),
        },
        Err(err) => CommandOutput {
            status,
            stdout: String::from_utf8_lossy(&stdout).to_string(),
            stderr: format!("{script_name} {phase}: {err}\n{}", String::from_utf8_lossy(&stderr)),
        },
    }
}

fn capture_stream<R: Read>(reader: R, cap: usize) -> Vec<u8> {
    let mut reader = BufReader::new(reader);
    let mut buffer = [0u8; 4096];
    let mut collected = Vec::new();

    loop {
        match reader.read(&mut buffer) {
            Ok(0) => break,
            Ok(read) => {
                let remaining = cap.saturating_sub(collected.len());
                if remaining > 0 {
                    collected.extend_from_slice(&buffer[..read.min(remaining)]);
                }
            }
            Err(_) => break,
        }
    }

    collected
}

fn execution_timeout() -> Duration {
    std::env::var("TACHI_EXECUTION_TIMEOUT_MS")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .map(Duration::from_millis)
        .unwrap_or(DEFAULT_EXECUTION_TIMEOUT)
}

fn execution_output_cap() -> usize {
    std::env::var("TACHI_EXECUTION_OUTPUT_CAP_BYTES")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(DEFAULT_OUTPUT_CAP_BYTES)
}

#[cfg(unix)]
fn terminate_process_group(child: &mut std::process::Child) {
    let _ = Command::new("kill")
        .arg("-TERM")
        .arg(format!("-{}", child.id()))
        .status();
    let _ = child.kill();
}

#[cfg(not(unix))]
fn terminate_process_group(child: &mut std::process::Child) {
    let _ = child.kill();
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
