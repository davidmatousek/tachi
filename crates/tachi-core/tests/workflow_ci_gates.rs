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
    let text = workflow_text("rust-workspace.yml");

    assert!(
        workflow_declares_unfiltered_event(&text, "pull_request"),
        "rust-workspace workflow must run on unfiltered pull_request events"
    );
    assert!(
        workflow_job_runs_command(&text, "cargo-test:", "cargo test --workspace --all-targets"),
        "cargo-test job must run cargo test --workspace --all-targets"
    );
    assert!(
        workflow_job_runs_command(&text, "cargo-test:", "sudo apt-get install -y ripgrep"),
        "cargo-test job must install ripgrep because workspace tests invoke rg-backed scripts"
    );
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

fn workflow_declares_unfiltered_event(text: &str, event: &str) -> bool {
    let lines = text.lines().collect::<Vec<_>>();
    let Some(event_index) = lines
        .iter()
        .position(|line| line.trim() == format!("{event}:"))
    else {
        return false;
    };

    let event_indent = indentation(lines[event_index]);

    for line in lines.iter().skip(event_index + 1) {
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let indent = indentation(line);
        if indent <= event_indent && trimmed.ends_with(':') {
            break;
        }

        if matches!(trimmed, "paths:" | "paths-ignore:") {
            return false;
        }
    }

    true
}

fn workflow_job_runs_command(text: &str, job: &str, command: &str) -> bool {
    let lines = text.lines().collect::<Vec<_>>();
    let Some(job_index) = lines.iter().position(|line| line.trim() == job) else {
        return false;
    };

    let job_indent = indentation(lines[job_index]);

    for line in lines.iter().skip(job_index + 1) {
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        let indent = indentation(line);
        if indent <= job_indent && trimmed.ends_with(':') {
            break;
        }

        if trimmed == format!("run: {command}") || trimmed == command {
            return true;
        }
    }

    false
}

fn indentation(line: &str) -> usize {
    line.chars().take_while(|character| *character == ' ').count()
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
