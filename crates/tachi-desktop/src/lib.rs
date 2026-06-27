pub mod app;

use std::path::Path;
use std::path::PathBuf;

use tachi_shell::commands::control_plane_commands;
use tachi_shell::commands::CommandOutput;
use tachi_shell::progress::CancellationToken;
use tachi_shell::progress::NoopProgressReporter;
use tachi_shell::progress::ProgressReporter;
use tachi_shell::tauri_bridge::dispatch_command;
use tachi_shell::tauri_bridge::dispatch_command_with_progress;

#[derive(Debug, Default, Clone, Copy)]
pub struct DesktopHost;

impl DesktopHost {
    pub const fn new() -> Self {
        Self
    }

    pub fn registered_commands(self) -> &'static [&'static str] {
        registered_commands()
    }

    pub fn dispatch_command(self, command: &str, repo_root: &Path, args: &[&str]) -> CommandOutput {
        dispatch_desktop_command(command, repo_root, args)
    }

    pub fn dispatch_command_with_progress(
        self,
        command: &str,
        repo_root: &Path,
        args: &[&str],
        token: &CancellationToken,
        reporter: &mut dyn ProgressReporter,
    ) -> CommandOutput {
        dispatch_desktop_command_with_progress(command, repo_root, args, token, reporter)
    }
}

pub fn registered_commands() -> &'static [&'static str] {
    control_plane_commands()
}

pub fn dispatch_desktop_command(command: &str, repo_root: &Path, args: &[&str]) -> CommandOutput {
    dispatch_command(command, repo_root, args)
}

pub fn dispatch_desktop_command_with_progress(
    command: &str,
    repo_root: &Path,
    args: &[&str],
    token: &CancellationToken,
    reporter: &mut dyn ProgressReporter,
) -> CommandOutput {
    dispatch_command_with_progress(command, repo_root, args, token, reporter)
}

pub fn dispatch_desktop_command_owned(
    command: &str,
    repo_root: PathBuf,
    args: Vec<String>,
) -> CommandOutput {
    let borrowed_args = args.iter().map(String::as_str).collect::<Vec<_>>();
    dispatch_desktop_command(command, &repo_root, &borrowed_args)
}

pub fn dispatch_desktop_command_with_noop_progress(
    command: &str,
    repo_root: &Path,
    args: &[&str],
) -> CommandOutput {
    let token = CancellationToken::new();
    let mut reporter = NoopProgressReporter;
    dispatch_desktop_command_with_progress(command, repo_root, args, &token, &mut reporter)
}

pub use tachi_shell::commands::CommandOutput as DesktopCommandOutput;
pub use tachi_shell::progress::CancellationToken as DesktopCancellationToken;
pub use tachi_shell::progress::ProgressEvent;
pub use tachi_shell::progress::ProgressReporter as DesktopProgressReporter;
