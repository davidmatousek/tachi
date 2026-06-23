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
        text.contains("name: cargo test -p ${{ matrix.package }} --all-targets"),
        "cargo-test job must use a package matrix"
    );
    for package in ["tachi-core", "tachi-shell", "tachi-cli", "tachi-tauri"] {
        if package == "tachi-shell" {
            continue;
        }
        assert!(
            text.contains(&format!("- package: {package}")),
            "cargo-test job must include {package} in the matrix"
        );
    }
    assert!(
        text.contains("cargo test -p ${{ matrix.package }} --all-targets"),
        "cargo-test job must run package-scoped cargo test --all-targets"
    );
    assert!(
        text.contains("name: cargo test -p tachi-shell (${{ matrix.suite }})"),
        "shell tests must run in a dedicated split matrix"
    );
    for suite in ["shell-smoke", "shell-init", "shell-integration"] {
        assert!(
            text.contains(&format!("suite: {suite}")),
            "shell test matrix must include {suite}"
        );
    }
    for command in [
        "cargo test -p tachi-shell --test command_registry --test coverage_audit --test infographic_data --test report_data_result --test tauri_shell_scaffold --test control_plane",
        "cargo test -p tachi-shell --test init_adversarial --test init_constitution --test init_defaults_env --test init_manifest_paths --test init_precommit_matrix --test init_substitution --test init_timing_trace --test init_trace_summary",
        "cargo test -p tachi-shell --test tauri_bridge --test template_config_load --test template_git_clone_timeout",
    ] {
        assert!(
            text.contains(command),
            "shell test matrix must run {command}"
        );
    }
    assert!(
        text.contains("sudo apt-get install -y ripgrep"),
        "cargo-test job must install ripgrep because workspace tests invoke rg-backed scripts"
    );
    assert!(
        text.contains("libglib2.0-dev")
            && text.contains("libgtk-3-dev")
            && text.contains("libsoup-3.0-dev")
            && text.contains("libwebkit2gtk-4.1-dev")
            && text.contains("pkg-config"),
        "cargo-test job must install Linux GUI deps because workspace tests invoke rg-backed scripts"
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

fn indentation(line: &str) -> usize {
    line.chars()
        .take_while(|character| *character == ' ')
        .count()
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
