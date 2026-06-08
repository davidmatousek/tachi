use std::path::{Path, PathBuf};
use std::process::Command;
use std::process::Output;

use tachi_core::coverage_audit::{collect_audit, render};
use tachi_core::infographic::build_infographic_payload;
use tachi_core::report_data::build_report_data_typst;

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
