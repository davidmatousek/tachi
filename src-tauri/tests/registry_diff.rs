use pretty_assertions::assert_eq;
use tachi_tauri::{collect_cli_commands, collect_tauri_commands, diff_registry, RegistryDiff};

#[test]
fn registry_diff_reports_matching_control_plane_surface() {
    assert_eq!(collect_cli_commands(), collect_tauri_commands());

    let diff = diff_registry(collect_cli_commands(), collect_tauri_commands());
    assert_eq!(
        diff,
        RegistryDiff {
            shared_commands: vec![
                String::from("bootstrap"),
                String::from("infographic-data"),
                String::from("init"),
                String::from("install"),
                String::from("update"),
            ],
            cli_only_commands: Vec::new(),
            tauri_only_commands: Vec::new(),
        }
    );
}

#[test]
fn registry_diff_reports_missing_and_extra_commands() {
    let diff = diff_registry(
        &["install", "init", "update", "bootstrap", "infographic-data", "report-data"],
        &["install", "init", "update", "bootstrap", "infographic-data", "sync-status"],
    );

    assert_eq!(
        diff,
        RegistryDiff {
            shared_commands: vec![
                String::from("bootstrap"),
                String::from("infographic-data"),
                String::from("init"),
                String::from("install"),
                String::from("update"),
            ],
            cli_only_commands: vec![String::from("report-data")],
            tauri_only_commands: vec![String::from("sync-status")],
        }
    );
}
