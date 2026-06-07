use std::path::Path;

use tachi_shell::commands::CommandOutput;
use tachi_shell::tauri_bridge::dispatch_command;

pub const DESKTOP_COMMANDS: [&str; 5] =
    ["install", "init", "update", "bootstrap", "infographic-data"];

pub fn dispatch_desktop_command(command: &str, repo_root: &Path, args: &[&str]) -> CommandOutput {
    dispatch_command(command, repo_root, args)
}

pub fn registered_commands() -> &'static [&'static str] {
    &DESKTOP_COMMANDS
}

pub fn run() {}
