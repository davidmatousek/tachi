use std::collections::BTreeSet;

use tachi_shell::commands::control_plane_commands;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RegistryDiff {
    pub shared_commands: Vec<String>,
    pub cli_only_commands: Vec<String>,
    pub tauri_only_commands: Vec<String>,
}

pub fn collect_cli_commands() -> &'static [&'static str] {
    control_plane_commands()
}

pub fn collect_tauri_commands() -> &'static [&'static str] {
    super::registered_commands()
}

pub fn diff_registry(cli_commands: &[&str], tauri_commands: &[&str]) -> RegistryDiff {
    let cli_set = cli_commands.iter().copied().collect::<BTreeSet<_>>();
    let tauri_set = tauri_commands.iter().copied().collect::<BTreeSet<_>>();

    let shared_commands = cli_set
        .intersection(&tauri_set)
        .map(|command| (*command).to_string())
        .collect::<Vec<_>>();
    let cli_only_commands = cli_set
        .difference(&tauri_set)
        .map(|command| (*command).to_string())
        .collect::<Vec<_>>();
    let tauri_only_commands = tauri_set
        .difference(&cli_set)
        .map(|command| (*command).to_string())
        .collect::<Vec<_>>();

    RegistryDiff {
        shared_commands,
        cli_only_commands,
        tauri_only_commands,
    }
}
