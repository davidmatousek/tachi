use std::path::{Path, PathBuf};

use tachi_shell::tauri_bridge::{dispatch_command, dispatch_command_with_progress};

pub mod error;
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
    if let Err(err) = validate_invoke_input_typed(command, repo_root, args).map(|_| ()) {
        return err.into_command_output(command);
    }

    let output = dispatch_command(command, repo_root, args);
    if let Err(err) = validate_invoke_output_typed(command, &output) {
        return err.into_command_output(command);
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
    if let Err(err) = validate_invoke_input_typed(command, repo_root, args).map(|_| ()) {
        return err.into_command_output(command);
    }

    let output = dispatch_command_with_progress(command, repo_root, args, token, reporter);
    if let Err(err) = validate_invoke_output_typed(command, &output) {
        return err.into_command_output(command);
    }

    output
}

pub fn registered_commands() -> &'static [&'static str] {
    &DESKTOP_COMMANDS
}

#[tauri::command]
fn desktop_registered_commands() -> &'static [&'static str] {
    registered_commands()
}

#[tauri::command]
fn dispatch_desktop_command_owned(
    command: String,
    repo_root: PathBuf,
    args: Vec<String>,
) -> CommandOutput {
    let borrowed_args = args.iter().map(String::as_str).collect::<Vec<_>>();
    dispatch_desktop_command(&command, &repo_root, &borrowed_args)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            desktop_registered_commands,
            dispatch_desktop_command_owned
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

pub use error::{DesktopError, DesktopErrorKind};
pub use offline::{
    bootstrap_from_cache, bootstrap_from_cache_typed, check_for_update, check_for_update_typed,
    restore_offline_cache, restore_offline_cache_typed, BootstrapReport, OfflineRestoreReport,
    UpdateCheck,
};
pub use registry::{collect_cli_commands, collect_tauri_commands, diff_registry, RegistryDiff};
pub use release_artifacts::{
    build_release_manifest, build_release_manifest_typed, validate_package_contents,
    validate_package_contents_typed, verify_checksum_matrix, verify_checksum_matrix_typed,
    PackageContentReport, ReleaseArtifact, ReleaseManifest,
};
pub use schema::{
    render_schema_error, validate_invoke_input, validate_invoke_input_typed,
    validate_invoke_output, validate_invoke_output_typed, DesktopInvokeInput,
};
pub use tachi_shell::commands::CommandOutput;
pub use tachi_shell::progress::{
    cancel_running_command, emit_progress_event, invoke_with_progress, CancellationToken,
    NoopProgressReporter, ProgressEvent, ProgressReporter,
};
