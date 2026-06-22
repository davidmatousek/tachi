use std::path::Path;

use tachi_shell::tauri_bridge::{dispatch_command, dispatch_command_with_progress};

pub mod offline;
pub mod registry;
pub mod release_artifacts;
pub mod schema;

pub const DESKTOP_COMMANDS: [&str; 9] = [
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

pub fn dispatch_desktop_command(command: &str, repo_root: &Path, args: &[&str]) -> CommandOutput {
    if let Err(message) = validate_invoke_input(command, repo_root, args).map(|_| ()) {
        return schema_error_output(command, message, 2);
    }

    let output = dispatch_command(command, repo_root, args);
    if let Err(message) = validate_invoke_output(command, &output) {
        return schema_error_output(command, message, 1);
    }

    output
}

pub fn dispatch_desktop_command_with_progress(
    command: &str,
    repo_root: &Path,
    args: &[&str],
    token: &tachi_shell::progress::CancellationToken,
    reporter: &mut dyn tachi_shell::progress::ProgressReporter,
) -> CommandOutput {
    if let Err(message) = validate_invoke_input(command, repo_root, args).map(|_| ()) {
        return schema_error_output(command, message, 2);
    }

    let output = dispatch_command_with_progress(command, repo_root, args, token, reporter);
    if let Err(message) = validate_invoke_output(command, &output) {
        return schema_error_output(command, message, 1);
    }

    output
}

pub fn registered_commands() -> &'static [&'static str] {
    &DESKTOP_COMMANDS
}

pub fn run() {
    let _registered_commands = registered_commands();
}

pub use tachi_shell::progress::{
    cancel_running_command, emit_progress_event, invoke_with_progress, CancellationToken,
    NoopProgressReporter, ProgressEvent, ProgressReporter,
};
pub use offline::{
    bootstrap_from_cache, check_for_update, restore_offline_cache, BootstrapReport,
    OfflineRestoreReport, UpdateCheck,
};
pub use registry::{collect_cli_commands, collect_tauri_commands, diff_registry, RegistryDiff};
pub use release_artifacts::{
    build_release_manifest, validate_package_contents, verify_checksum_matrix,
    PackageContentReport, ReleaseArtifact, ReleaseManifest,
};
pub use schema::{
    render_schema_error, validate_invoke_input, validate_invoke_output, DesktopInvokeInput,
};
pub use tachi_shell::commands::CommandOutput;

fn schema_error_output(command: &str, message: String, status: i32) -> CommandOutput {
    CommandOutput {
        status,
        stdout: String::new(),
        stderr: format!("{}\n", render_schema_error(command, &message)),
    }
}
