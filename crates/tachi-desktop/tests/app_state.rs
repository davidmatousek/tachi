use std::env;
use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::Path;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

use pretty_assertions::assert_eq;
use tachi_desktop::app::DesktopApp;
use tachi_desktop::app::DesktopAppState;
use tachi_shell::commands::command_registry;

static FIXTURE_COUNTER: AtomicU64 = AtomicU64::new(0);

fn test_temp_root() -> PathBuf {
    fs::canonicalize(env::temp_dir()).expect("canonicalize temporary directory")
}

fn fixture_repo() -> PathBuf {
    let root = test_temp_root().join(format!(
        "tachi-desktop-app-state-{}-{}",
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos(),
        FIXTURE_COUNTER.fetch_add(1, Ordering::Relaxed)
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

fn temp_fixture_dir(name: &str) -> PathBuf {
    let root = test_temp_root().join(format!(
        "tachi-desktop-fixture-{}-{}",
        name,
        FIXTURE_COUNTER.fetch_add(1, Ordering::Relaxed)
    ));
    fs::create_dir_all(&root).expect("create temp fixture dir");
    root
}

fn read_bytes(path: &Path) -> Vec<u8> {
    fs::read(path).expect("read artifact bytes")
}

#[test]
fn desktop_app_state_tracks_repo_root_and_catalog() {
    let repo_root = PathBuf::from("/tmp/tachi-desktop-fixture");
    let state = DesktopAppState::new(repo_root.clone());

    assert_eq!(state.repo_root(), repo_root.as_path());
    assert_eq!(state.repo_root_input(), repo_root.display().to_string());
    assert_eq!(state.command_catalog(), command_registry().names());
}

#[test]
fn repo_root_selection_updates_visible_state() {
    let mut state = DesktopAppState::new(PathBuf::from("/tmp/initial-root"));
    let next_root = PathBuf::from("/tmp/selected-root");

    state.set_repo_root(next_root.clone());

    assert_eq!(state.repo_root(), next_root.as_path());
    assert_eq!(state.repo_root_input(), next_root.display().to_string());
}

#[test]
fn render_text_lists_repo_root_and_commands() {
    let repo_root = PathBuf::from("/tmp/render-root");
    let app = DesktopApp::new(repo_root.clone());
    let rendered = app.render_text();

    assert!(rendered.contains("Tachi Desktop"));
    assert!(rendered.contains(&format!("Repository root: {}", repo_root.display())));
    assert!(rendered.contains("Command catalog:"));
    assert!(rendered.lines().any(|line| line == "- bootstrap"));
}

#[test]
fn command_runs_are_captured_and_rendered() {
    let repo_root = fixture_repo();
    write_executable_file(
        &repo_root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nprintf 'bootstrap-ok\\n'\n",
    );
    let mut app = DesktopApp::new(repo_root);
    let output = app.run_command("bootstrap", &["--yes"]);

    assert_eq!(output.status, 0);
    assert_eq!(
        app.state()
            .last_command()
            .map(|snapshot| snapshot.command.as_str()),
        Some("bootstrap")
    );
    assert!(app.render_text().contains("Latest command:"));
    assert!(app.render_text().contains("Command: bootstrap"));
    assert!(app.render_text().contains("Status: 0"));
    assert_eq!(app.state().command_history().len(), 1);
    assert!(app.render_text().contains("Command history:"));
    assert!(app.render_text().contains("bootstrap [0]"));
}

#[test]
fn command_history_persists_after_repo_root_updates() {
    let repo_root = fixture_repo();
    write_executable_file(
        &repo_root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nprintf 'bootstrap-ok\\n'\n",
    );
    let mut app = DesktopApp::new(repo_root.clone());
    let output = app.run_command("bootstrap", &["--yes"]);

    assert_eq!(output.status, 0);
    let next_root = repo_root.join("nested/root");
    app.state_mut().set_repo_root(next_root.clone());

    assert_eq!(app.state().repo_root(), next_root.as_path());
    assert_eq!(app.state().command_history().len(), 1);
    assert_eq!(
        app.state()
            .last_command()
            .map(|snapshot| snapshot.command.as_str()),
        Some("bootstrap")
    );
    assert!(app.render_text().contains("Command history:"));
    assert!(app.render_text().contains("bootstrap [0]"));
}

#[test]
fn command_failures_are_captured_without_panic() {
    let repo_root = fixture_repo();
    let mut app = DesktopApp::new(repo_root);
    let output = app.run_command("not-a-real-command", &[]);

    assert_ne!(output.status, 0);
    assert!(app.render_text().contains("Latest command:"));
    assert!(app.render_text().contains("not-a-real-command"));
}

#[test]
fn report_data_preview_and_save_match() {
    let fixture_root = temp_fixture_dir("report-data");
    let target_dir = fixture_root.join("examples/agentic-app/sample-report");
    let template_dir = fixture_root.join("templates/tachi/security-report");
    fs::create_dir_all(&target_dir).expect("create target dir");
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::write(
        target_dir.join("threats.md"),
        "# Threat Model: Bridge Coverage\n",
    )
    .expect("write threats");

    let repo_root = fixture_root.clone();
    let mut preview_app = DesktopApp::new(repo_root.clone());
    let preview = preview_app.run_command(
        "report-data",
        &[
            "--target-dir",
            target_dir.to_string_lossy().as_ref(),
            "--template-dir",
            template_dir.to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(preview.status, 0, "preview stderr: {}", preview.stderr);
    assert!(preview.stdout.contains("#let project-name ="));

    let output_path = fixture_root.join("generated/report-data.typ");
    let mut save_app = DesktopApp::new(repo_root);
    let saved = save_app.run_command(
        "report-data",
        &[
            "--target-dir",
            target_dir.to_string_lossy().as_ref(),
            "--template-dir",
            template_dir.to_string_lossy().as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(saved.status, 0, "saved stderr: {}", saved.stderr);
    assert_eq!(read_bytes(&output_path), preview.stdout.as_bytes());
}

#[test]
fn infographic_preview_and_save_match() {
    let fixture_root = temp_fixture_dir("infographic");
    fs::create_dir_all(&fixture_root).expect("create fixture root");
    fs::write(
        fixture_root.join("threats.md"),
        "# Agentic AI Application

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| AG-8 | Agent | Prompt injection | High | Harden prompts | [NEW] |
",
    )
    .expect("write threats fixture");

    let repo_root = fixture_root.clone();
    let mut preview_app = DesktopApp::new(repo_root.clone());
    let preview = preview_app.run_command(
        "infographic-data",
        &[
            "--root",
            fixture_root.to_string_lossy().as_ref(),
            "--template",
            "maestro-stack",
        ],
    );

    assert_eq!(preview.status, 0, "preview stderr: {}", preview.stderr);
    let preview_value: serde_json::Value =
        serde_json::from_str(&preview.stdout).expect("valid infographic JSON");
    assert_eq!(preview_value["template"], "maestro-stack");
    let output_path = fixture_root.join("generated/infographic.json");
    let mut save_app = DesktopApp::new(repo_root);
    let saved = save_app.run_command(
        "infographic-data",
        &[
            "--root",
            fixture_root.to_string_lossy().as_ref(),
            "--template",
            "maestro-stack",
            "--output",
            output_path.to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(saved.status, 0, "saved stderr: {}", saved.stderr);
    assert_eq!(read_bytes(&output_path), preview.stdout.as_bytes());
}
#[test]
fn sarif_artifact_saves_match_preview_and_fail_closed_on_escape() {
    let repo_root = temp_fixture_dir("sarif");
    fs::write(
        repo_root.join("threats.md"),
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n| AG-8 | Agent | Prompt injection | High | Harden prompts | [NEW] |\n| AG-9 | Guardrails | Prompt leakage | Medium | Apply egress filters | [NEW] |\n",
    )
    .expect("write threats fixture");
    let mut preview_app = DesktopApp::new(repo_root.clone());
    let preview_output_path = repo_root.join("generated/threats-preview.sarif");
    let preview = preview_app.run_command(
        "threats-sarif",
        &[
            "--input",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            preview_output_path.to_string_lossy().as_ref(),
        ],
    );
    assert_eq!(preview.status, 0, "preview stderr: {}", preview.stderr);
    assert!(preview.stdout.is_empty());

    let output_path = repo_root.join("generated/threats.sarif");
    let mut save_app = DesktopApp::new(repo_root.clone());
    let saved = save_app.run_command(
        "threats-sarif",
        &[
            "--input",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ],
    );
    assert_eq!(saved.status, 0, "saved stderr: {}", saved.stderr);
    assert!(saved.stdout.is_empty());
    assert_eq!(read_bytes(&output_path), read_bytes(&preview_output_path));

    let escape_path = output_path
        .parent()
        .expect("temp parent")
        .join("../escape.sarif");
    let mut escape_app = DesktopApp::new(repo_root.clone());
    let escaped = escape_app.run_command(
        "threats-sarif",
        &[
            "--input",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            escape_path.to_string_lossy().as_ref(),
        ],
    );

    assert_ne!(escaped.status, 0);
    assert!(!escape_path.exists());
}

#[test]
fn risk_scores_preview_and_save_match() {
    let repo_root = temp_fixture_dir("risk-scores");
    fs::write(
        repo_root.join("risk-scores.md"),
        "## 2. Scored Threat Table\n\n| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| AG-8 | Agent | Prompt injection | 9.1 | 9.0 | 8.5 | 8.0 | 8.8 | High | 7 | Monitor |\n| AG-9 | Guardrails | Prompt leakage | 7.2 | 6.8 | 6.4 | 6.0 | 6.6 | Medium | 14 | Monitor |\n\n## 3. Dimensional Breakdown\n\n### AG-8: Prompt injection\n\n**Component**: Agent\n**Category**: Agentic Threats\n**MAESTRO Layer**: L3 Triage\n**CVSS Vector**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`\n**Correlation Group**: Scores inherited from primary finding AG-3\n*Score source: correlation primary*\n\n## 4. Governance Fields\n\n| ID | Owner | SLA | Disposition | Review Date |\n| --- | --- | --- | --- | --- |\n| AG-8 | Alice | 7 | Monitor | 2026-06-06 |\n| AG-9 | Bob | 14 | Monitor | 2026-06-13 |\n",
    )
    .expect("write risk scores fixture");
    fs::write(
        repo_root.join("threats.md"),
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n| AG-8 | Agent | Prompt injection | High | Harden prompts | [NEW] |\n| AG-9 | Guardrails | Prompt leakage | Medium | Apply egress filters | [NEW] |\n",
    )
    .expect("write threats fixture");
    let mut preview_app = DesktopApp::new(repo_root.clone());
    let preview_output_path = repo_root.join("generated/risk-scores-preview.sarif");
    let preview = preview_app.run_command(
        "risk-scores-sarif",
        &[
            "--risk-scores",
            repo_root.join("risk-scores.md").to_string_lossy().as_ref(),
            "--threats",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            preview_output_path.to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(preview.status, 0, "preview stderr: {}", preview.stderr);
    assert!(preview.stdout.is_empty());
    let output_path = repo_root.join("generated/risk-scores.sarif");
    let mut save_app = DesktopApp::new(repo_root.clone());
    let saved = save_app.run_command(
        "risk-scores-sarif",
        &[
            "--risk-scores",
            repo_root.join("risk-scores.md").to_string_lossy().as_ref(),
            "--threats",
            repo_root.join("threats.md").to_string_lossy().as_ref(),
            "--output",
            output_path.to_string_lossy().as_ref(),
        ],
    );

    assert_eq!(saved.status, 0, "saved stderr: {}", saved.stderr);
    assert!(saved.stdout.is_empty());
    assert_eq!(read_bytes(&output_path), read_bytes(&preview_output_path));
}
