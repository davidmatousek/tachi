use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use serde::Serialize;

use crate::progress::{CancellationToken, NoopProgressReporter, ProgressReporter};

pub use crate::command_use_cases::{
    coverage_audit_output, infographic_data_output, render_report_data_result,
    report_data_output, report_data_result, risk_scores_sarif_output, threats_sarif_output,
    validate_report_data_result, ReportDataResult, RiskScoresSarifOutput, ThreatsSarifOutput,
};

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
        script_executor::ScriptCommandRunRequest {
            executor: &script_executor::SystemScriptExecutor,
            sink: &runtime_helpers::SystemScriptOutputSink,
            script_dir,
            script_name,
            args,
            repo_root,
            token,
            reporter,
        },
    )
}

fn script_dir_for_repo_root(repo_root: &Path) -> PathBuf {
    repo_root.join("scripts")
}

pub fn control_plane_scripts_dir(repo_root: &Path) -> PathBuf {
    script_dir_for_repo_root(repo_root)
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

#[cfg(test)]
mod tests {
    use super::bootstrap_control_plane_args;
    use super::control_plane_scripts_dir;
    use std::fs;

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

    #[test]
    fn control_plane_scripts_dir_stays_within_repo_root() {
        let root = std::env::temp_dir().join(format!(
            "tachi-shell-scripts-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .expect("clock")
                .as_nanos()
        ));
        let parent = root.join("parent");
        let repo_root = parent.join("repo");

        fs::create_dir_all(parent.join("scripts")).expect("create parent scripts");
        fs::create_dir_all(&repo_root).expect("create repo root");

        let scripts_dir = control_plane_scripts_dir(&repo_root);

        assert_eq!(scripts_dir, repo_root.join("scripts"));
        assert!(scripts_dir.starts_with(&repo_root));
        assert_ne!(scripts_dir, parent.join("scripts"));

        let _ = fs::remove_dir_all(&root);
    }
}
