use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;

use pretty_assertions::assert_eq;
use tachi_tauri::{dispatch_desktop_command, registered_commands};

fn fixture_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-tauri-shell-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(root.join("scripts")).expect("create fixture scripts");
    root
}

fn write_executable_file(path: &PathBuf, content: &str) {
    fs::write(path, content).expect("write temporary script");
    let mut perms = fs::metadata(path).expect("read metadata").permissions();
    perms.set_mode(0o755);
    fs::set_permissions(path, perms).expect("set executable mode");
}

#[test]
fn registered_commands_expose_shared_shell_surface() {
    assert_eq!(
        registered_commands(),
        &["install", "init", "update", "bootstrap", "infographic-data"]
    );
}

#[test]
fn dispatch_desktop_command_reuses_shared_bridge_for_bootstrap() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let output = dispatch_desktop_command("bootstrap", &root, &["--yes"]);

    assert_eq!(output.status, 0);
    let lines: Vec<_> = output.stdout.lines().collect();
    assert_eq!(lines, vec!["--bootstrap", "--yes"]);
}

#[test]
fn dispatch_desktop_command_routes_infographic_data_through_shared_shell_surface() {
    let root = fixture_infographic_repo();

    let output = dispatch_desktop_command(
        "infographic-data",
        &root,
        &[
            "--root",
            root.to_string_lossy().as_ref(),
            "--template",
            "maestro-stack",
        ],
    );

    assert_eq!(output.status, 0);
    assert!(output.stderr.is_empty());
    let payload: serde_json::Value =
        serde_json::from_str(&output.stdout).expect("valid infographic JSON");
    assert_eq!(payload["template"], "maestro-stack");
    assert!(payload["template_data"].is_object());
}

fn fixture_infographic_repo() -> PathBuf {
    let root = fixture_repo();
    let template_dir = root.join("templates/tachi/infographics");
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::write(
        root.join("threats.md"),
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |\n| --- | --- | --- | --- | --- | --- |\n| S-1 | Orchestrator | L2 — Foundation Model | High | Prompt override risk | Harden instruction guards |\n",
    )
    .expect("write threats");
    fs::write(
        template_dir.join("infographic-maestro-stack.md"),
        "## Gemini Prompt\n```text\nDATA CONTENT (render this)\nFOOTER\n```",
    )
    .expect("write template");
    fs::write(
        template_dir.join("infographic-executive-architecture.md"),
        "## Gemini Prompt\n```text\nDATA CONTENT (render this)\nFOOTER\n```",
    )
    .expect("write template");
    root
}
