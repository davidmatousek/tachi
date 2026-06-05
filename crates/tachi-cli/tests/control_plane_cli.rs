use std::fs;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::Value;

const TEMPLATE_DIR: &str = "templates/tachi/infographics";
const THREATS_MD: &str = r#"
# Agentic AI Application

### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| LLM Agent Orchestrator | Service | L2 — Foundation Model |
| MCP Tool Server | Service | L2 — Foundation Model |
| Guardrails Service | Service | L5 — Infrastructure Controls |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
| --- | --- | --- |
| L2 — Foundation Model | 2 | High |
| L5 — Infrastructure Controls | 1 | Critical |

## 7. Recommended Actions

| Finding ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L2 — Foundation Model | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L2 — Foundation Model | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L5 — Infrastructure Controls | Critical | Model output exfiltration | Enforce egress controls |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 1 |
| High | 1 |
| Medium | 1 |
| Low | 0 |
| Note | 0 |
| Total | 3 |
"#;

fn write_executable_file(path: &Path, content: &str) {
    fs::write(path, content).expect("write temporary script");
    #[cfg(unix)]
    {
        let mut perms = fs::metadata(path).expect("read metadata").permissions();
        perms.set_mode(0o755);
        fs::set_permissions(path, perms).expect("set executable mode");
    }
}

fn fixture_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-control-plane-cli-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(root.join("scripts")).expect("create fixture scripts");
    root
}

fn fixture_infographic_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-infographic-cli-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(&root).expect("create fixture root");
    fs::write(root.join("threats.md"), THREATS_MD).expect("write threats");

    let template_dir = root.join(TEMPLATE_DIR);
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::write(
        template_dir.join("infographic-maestro-stack.md"),
        r##"## Gemini Prompt
```text
DATA CONTENT (render this)
FOOTER
```"##,
    )
    .expect("write stack template");

    root
}

fn binary_path(binary_name: &str) -> PathBuf {
    std::env::var(format!("CARGO_BIN_EXE_{binary_name}"))
        .unwrap_or_else(|_| panic!("CARGO_BIN_EXE_{binary_name} should be provided by cargo"))
        .into()
}

#[test]
fn install_binary_forwards_flags_and_root_path() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/install.sh"),
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\"",
    );

    let output = Command::new(binary_path("install"))
        .args([
            "--root",
            root.to_string_lossy().as_ref(),
            "--source",
            "/tmp/source",
            "--version",
            "v1.2.3",
        ])
        .output()
        .expect("run install binary");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    let lines: Vec<_> = stdout.lines().collect();
    assert_eq!(
        lines,
        vec!["--source", "/tmp/source", "--version", "v1.2.3"]
    );
}

#[test]
fn init_binary_prints_help() {
    let binary = binary_path("init");
    let output = Command::new(binary)
        .arg("--help")
        .output()
        .expect("run init help");

    assert!(output.status.success());
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("usage: init"));
}

#[test]
fn update_binary_forwards_flags() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done",
    );

    let output = Command::new(binary_path("update"))
        .args([
            "--root",
            root.to_string_lossy().as_ref(),
            "--dry-run",
            "--yes",
        ])
        .output()
        .expect("run update binary");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("--dry-run"));
    assert!(stdout.contains("--yes"));
}

#[test]
fn bootstrap_binary_forwards_bootstrap_prefix() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done",
    );

    let output = Command::new(binary_path("bootstrap"))
        .args(["--root", root.to_string_lossy().as_ref(), "--yes"])
        .output()
        .expect("run bootstrap binary");

    assert!(output.status.success());
    let bootstrap_stdout = String::from_utf8_lossy(&output.stdout);
    let lines: Vec<_> = bootstrap_stdout.lines().collect();
    assert_eq!(lines, vec!["--bootstrap", "--yes"]);
}

#[test]
fn infographic_data_binary_returns_json_payload_for_template() {
    let repo_root = fixture_infographic_repo();
    let output = Command::new(binary_path("infographic-data"))
        .args([
            "--root",
            repo_root.to_string_lossy().as_ref(),
            "--template",
            "maestro-stack",
        ])
        .output()
        .expect("run infographic-data binary");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    let value: Value = serde_json::from_str(&stdout).expect("valid JSON");
    assert_eq!(value["template"], "maestro-stack");
    assert!(value["template_data"]["has_maestro_data"]
        .as_bool()
        .unwrap_or(false));
}

#[test]
fn infographic_data_binary_prints_help_to_stderr() {
    let output = Command::new(binary_path("infographic-data"))
        .arg("--help")
        .output()
        .expect("run infographic-data help");

    assert!(output.status.success());
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("usage: infographic-data"));
}
