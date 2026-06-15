use std::fs;
use std::path::{Path, PathBuf};

#[test]
fn install_manifest_lists_existing_assets_only() {
    let root = workspace_root();
    let manifest_path = root.join("INSTALL_MANIFEST.md");
    let manifest = fs::read_to_string(&manifest_path).expect("read INSTALL_MANIFEST.md");

    let mut in_section = false;
    let mut missing: Vec<String> = Vec::new();

    for line in manifest.lines() {
        if line == "<!-- BEGIN MANIFEST -->" {
            in_section = true;
            continue;
        }
        if line == "<!-- END MANIFEST -->" {
            break;
        }
        if !in_section {
            continue;
        }
        if line.trim().is_empty() || line.starts_with('#') {
            continue;
        }

        let entry = root.join(line);
        if line.ends_with('/') {
            if !entry.is_dir() {
                missing.push(line.to_string());
            }
            continue;
        }
        if !entry.is_file() {
            missing.push(line.to_string());
        }
    }

    assert!(
        missing.is_empty(),
        "install manifest contains missing entries:\n{}",
        missing.join("\n")
    );
}

#[test]
fn adapter_commands_include_all_tachi_user_commands() {
    let root = workspace_root();
    let adapter_commands = root.join("adapters").join("claude-code").join("commands");
    let command_names = [
        "tachi.threat-model.md",
        "tachi.risk-score.md",
        "tachi.compensating-controls.md",
        "tachi.infographic.md",
        "tachi.security-report.md",
        "tachi.architecture.md",
    ];

    assert!(
        adapter_commands.is_dir(),
        "adapter command directory missing: {}",
        adapter_commands.display()
    );

    for command_name in command_names {
        assert!(
            adapter_commands.join(command_name).is_file(),
            "adapter command file missing: adapters/claude-code/commands/{}",
            command_name
        );
    }
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}
