use std::path::Path;

use tachi_shell::commands::CommandOutput;
use tachi_shell::tauri_bridge::{dispatch_command, dispatch_command_with_progress};

pub mod offline;
pub mod release_artifacts;

pub const DESKTOP_COMMANDS: [&str; 5] =
    ["install", "init", "update", "bootstrap", "infographic-data"];

pub fn dispatch_desktop_command(command: &str, repo_root: &Path, args: &[&str]) -> CommandOutput {
    dispatch_command(command, repo_root, args)
}

pub fn dispatch_desktop_command_with_progress(
    command: &str,
    repo_root: &Path,
    args: &[&str],
    token: &tachi_shell::progress::CancellationToken,
    reporter: &mut dyn tachi_shell::progress::ProgressReporter,
) -> CommandOutput {
    dispatch_command_with_progress(command, repo_root, args, token, reporter)
}

pub fn registered_commands() -> &'static [&'static str] {
    &DESKTOP_COMMANDS
}

pub fn run() {}

pub use tachi_shell::progress::{
    cancel_running_command, emit_progress_event, invoke_with_progress, CancellationToken,
    NoopProgressReporter, ProgressEvent, ProgressReporter,
};
pub use offline::{
    bootstrap_from_cache, check_for_update, restore_offline_cache, BootstrapReport,
    OfflineRestoreReport, UpdateCheck,
};
pub use release_artifacts::{
    build_release_manifest, validate_package_contents, verify_checksum_matrix,
    PackageContentReport, ReleaseArtifact, ReleaseManifest,
};
