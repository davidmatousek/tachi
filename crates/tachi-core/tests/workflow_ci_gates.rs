use std::fs;
use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn workflow_text(name: &str) -> String {
    fs::read_to_string(repo_root().join(".github/workflows").join(name))
        .unwrap_or_else(|err| panic!("read workflow {name}: {err}"))
}

#[test]
fn workspace_cargo_test_pr_gate_runs_full_workspace_suite() {
    let workflows_dir = repo_root().join(".github/workflows");
    let mut matching_workflows = Vec::new();

    for entry in fs::read_dir(&workflows_dir).expect("read workflows directory") {
        let entry = entry.expect("workflow entry");
        let path = entry.path();
        if path.extension().and_then(|extension| extension.to_str()) != Some("yml") {
            continue;
        }

        let text = fs::read_to_string(&path).expect("read workflow file");
        if workflow_runs_command(&text, "cargo test --workspace --all-targets") {
            matching_workflows.push((path, text));
        }
    }

    assert!(
        !matching_workflows.is_empty(),
        "PR CI must include a cargo test --workspace --all-targets workflow"
    );

    for (path, text) in matching_workflows {
        assert!(
            text.contains("pull_request:"),
            "{} must run on pull_request",
            path.display()
        );
        assert!(
            !text.contains("paths:"),
            "{} must not path-filter the full workspace behavioral gate",
            path.display()
        );
    }
}

#[test]
fn clippy_sarif_workflow_fails_closed_without_losing_upload() {
    let text = workflow_text("rust-clippy.yml");

    assert!(
        !text.contains("continue-on-error: true"),
        "clippy workflow must not mask lint failures with continue-on-error"
    );
    assert!(
        text.contains("-- -D warnings"),
        "clippy workflow must deny warnings"
    );
    assert!(
        workflow_step_has_line(&text, "Upload analysis results to GitHub", "if: always()"),
        "clippy SARIF upload step must still run after clippy failures"
    );
    assert!(
        text.contains("exit \"$CLIPPY_STATUS\""),
        "clippy workflow must re-emit the captured clippy exit status"
    );
}

fn workflow_runs_command(text: &str, command: &str) -> bool {
    text.lines()
        .map(str::trim)
        .any(|line| line == format!("run: {command}") || line == command)
}

fn workflow_step_has_line(text: &str, step_name: &str, required_line: &str) -> bool {
    let mut in_step = false;

    for line in text.lines().map(str::trim) {
        if line.starts_with("- name: ") {
            in_step = line == format!("- name: {step_name}");
            continue;
        }

        if in_step && line == required_line {
            return true;
        }
    }

    false
}
