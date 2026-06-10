use std::fs;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::Value;

const TEMPLATE_DIR: &str = "templates/tachi/infographics";
const REPORT_TEMPLATE_DIR: &str = "templates/tachi/security-report";
const REPORT_TARGET_DIR: &str = "examples/agentic-app/sample-report";
const PNG_MAGIC: &[u8] = b"\x89PNG\r\n\x1a\n";
const JPEG_MAGIC: &[u8] = b"\xff\xd8\xff\xe0\x00\x10JFIF";
const RISK_SCORES_MD: &str = r#"
## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AG-8 | Agent | Prompt injection | 9.1 | 9.0 | 8.5 | 8.0 | 8.8 | High | 7 | Monitor |

## 3. Dimensional Breakdown

### AG-8: Prompt injection

**Component**: Agent
**Category**: Agentic Threats
**MAESTRO Layer**: L3 Triage
**CVSS Vector**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`
**Correlation Group**: Scores inherited from primary finding AG-3
*Score source: correlation primary*

## 4. Governance Fields

| ID | Owner | SLA | Disposition | Review Date |
| --- | --- | --- | --- | --- |
| AG-8 | Alice | 7 | Monitor | 2026-06-06 |
"#;
const THREATS_SARIF_MD: &str = r#"
# Agentic AI Application

### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| Agent | Service | L3 - Control Plane |

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| AG-8 | Agent | Prompt injection | High | Harden prompts | [NEW] |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| High | 1 |
| Total | 1 |
"#;
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

fn fixture_report_data_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-report-data-cli-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    let target_dir = root.join(REPORT_TARGET_DIR);
    let template_dir = root.join(REPORT_TEMPLATE_DIR);
    fs::create_dir_all(&target_dir).expect("create target dir");
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::write(
        target_dir.join("threat-executive-architecture.jpg"),
        [JPEG_MAGIC, b"payload"].concat(),
    )
    .expect("write executive architecture image");

    root
}

fn fixture_threats_sarif_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-threats-sarif-cli-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(&root).expect("create fixture root");
    fs::write(root.join("threats.md"), THREATS_SARIF_MD).expect("write threats");
    root
}

fn fixture_risk_scores_sarif_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-risk-scores-sarif-cli-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(&root).expect("create fixture root");
    fs::write(root.join("risk-scores.md"), RISK_SCORES_MD).expect("write risk scores");
    fs::write(root.join("threats.md"), THREATS_SARIF_MD).expect("write threats");
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

#[test]
fn report_data_binary_returns_typst_payload_for_executive_architecture() {
    let repo_root = fixture_report_data_repo();
    let output = Command::new(binary_path("report-data"))
        .args([
            "--target-dir",
            repo_root.join(REPORT_TARGET_DIR).to_string_lossy().as_ref(),
            "--template-dir",
            repo_root
                .join(REPORT_TEMPLATE_DIR)
                .to_string_lossy()
                .as_ref(),
        ])
        .output()
        .expect("run report-data binary");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("#let has-executive-architecture = true"));
    let path_line = stdout
        .lines()
        .find(|line| line.starts_with("#let executive-architecture-image-path"))
        .expect("executive architecture path line");
    assert!(path_line.contains("threat-executive-architecture.jpg"));
}

#[test]
fn report_data_binary_writes_output_file_when_requested() {
    let repo_root = fixture_report_data_repo();
    let output_path = repo_root.join("generated/report-data.typ");
    let output = Command::new(binary_path("report-data"))
        .args([
            "--target-dir",
            repo_root.join(REPORT_TARGET_DIR).to_string_lossy().as_ref(),
            "--template-dir",
            repo_root
                .join(REPORT_TEMPLATE_DIR)
                .to_string_lossy()
                .as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ])
        .output()
        .expect("run report-data binary");

    assert!(output.status.success());
    assert!(
        output_path.exists(),
        "report-data binary should write the requested output file"
    );

    let file_content = fs::read_to_string(&output_path).expect("read output file");
    assert!(file_content.contains("#let has-executive-architecture = true"));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("report-data.typ generated"));
}

#[test]
fn report_data_binary_warns_when_correcting_mislabeled_png() {
    let repo_root = fixture_report_data_repo();
    let target_dir = repo_root.join(REPORT_TARGET_DIR);
    fs::write(
        target_dir.join("threat-executive-architecture.jpg"),
        [PNG_MAGIC, b"payload"].concat(),
    )
    .expect("write mislabeled png");

    let output = Command::new(binary_path("report-data"))
        .args([
            "--target-dir",
            target_dir.to_string_lossy().as_ref(),
            "--template-dir",
            repo_root
                .join(REPORT_TEMPLATE_DIR)
                .to_string_lossy()
                .as_ref(),
        ])
        .output()
        .expect("run report-data binary");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("threat-executive-architecture.png"));
    assert!(target_dir
        .join("threat-executive-architecture.png")
        .exists());

    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("Image format mismatch"));
    assert!(stderr.contains("PNG bytes"));
}

#[test]
fn report_data_binary_keeps_clean_jpeg_without_format_warning() {
    let repo_root = fixture_report_data_repo();
    let target_dir = repo_root.join(REPORT_TARGET_DIR);
    let output = Command::new(binary_path("report-data"))
        .args([
            "--target-dir",
            target_dir.to_string_lossy().as_ref(),
            "--template-dir",
            repo_root
                .join(REPORT_TEMPLATE_DIR)
                .to_string_lossy()
                .as_ref(),
        ])
        .output()
        .expect("run report-data binary");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("threat-executive-architecture.jpg"));
    assert!(!target_dir
        .join("threat-executive-architecture.png")
        .exists());

    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(!stderr.contains("Image format mismatch"));
}

#[test]
fn threats_sarif_binary_writes_sarif_file_and_marks_ag8_metadata() {
    let repo_root = fixture_threats_sarif_repo();
    let output_path = repo_root.join("generated/threats.sarif");
    let output = Command::new(binary_path("threats-sarif"))
        .args([
            "--input",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ])
        .output()
        .expect("run threats-sarif binary");

    assert!(output.status.success());
    assert!(
        output_path.exists(),
        "threats-sarif binary should write the requested output file"
    );

    let sarif: Value =
        serde_json::from_str(&fs::read_to_string(&output_path).expect("read threats sarif output"))
            .expect("valid SARIF JSON");
    let result = &sarif["runs"][0]["results"][0];
    assert_eq!(result["partialFingerprints"]["findingId/v1"], "AG-8");
    assert_eq!(result["properties"]["asi07_emission"], true);
    assert_eq!(result["properties"]["pattern_category"], 9);
    assert!(String::from_utf8_lossy(&output.stderr).contains("wrote 1 findings"));
}

#[test]
fn risk_scores_sarif_binary_writes_sarif_file_and_marks_ag8_metadata() {
    let repo_root = fixture_risk_scores_sarif_repo();
    let output_path = repo_root.join("generated/risk-scores.sarif");
    let output = Command::new(binary_path("risk-scores-sarif"))
        .args([
            "--risk-scores",
            repo_root.join("risk-scores.md").to_string_lossy().as_ref(),
            "--threats",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ])
        .output()
        .expect("run risk-scores-sarif binary");

    assert!(output.status.success());
    assert!(
        output_path.exists(),
        "risk-scores-sarif binary should write the requested output file"
    );

    let sarif: Value = serde_json::from_str(
        &fs::read_to_string(&output_path).expect("read risk scores sarif output"),
    )
    .expect("valid SARIF JSON");
    let result = &sarif["runs"][0]["results"][0];
    assert_eq!(result["partialFingerprints"]["findingId/v1"], "AG-8");
    assert_eq!(result["properties"]["security-severity"], "8.8");
    assert_eq!(result["properties"]["score-source"], "inherited");
    assert_eq!(result["properties"]["asi07_emission"], true);
    assert!(String::from_utf8_lossy(&output.stderr).contains("wrote 1 results"));
}
