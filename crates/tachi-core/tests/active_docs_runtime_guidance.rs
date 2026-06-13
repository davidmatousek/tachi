use std::fs;
use std::path::{Path, PathBuf};

#[test]
fn active_docs_do_not_instruct_running_retired_python_entrypoints() {
    let root = workspace_root();

    let active_docs = [
        ".claude/agents/tachi/report-assembler.md",
        ".claude/commands/tachi.infographic.md",
        ".claude/skills/aod-orchestrate/SKILL.md",
        "docs/architecture/00_Tech_Stack/README.md",
        "docs/architecture/01_system_design/README.md",
        "docs/guides/GETTING_STARTED_PATH_B.md",
        "docs/guides/SMOKE_TEST.md",
        "docs/standards/CLAUDE_MD_ORGANIZATION.md",
        "docs/standards/CLAUDE_PERMISSIONS.md",
        "docs/standards/PRECOMMIT_HOOKS.md",
        "docs/standards/EVAL_CONVENTIONS.md",
        "docs/devops/01_Local/README.md",
        "docs/devops/CI_CD_GUIDE.md",
        "README.md",
        ".github/workflows/tachi-pytest.yml",
        "docs/devops/environment-variables.md",
    ];

    let retired_refs = [
        "python3 scripts/extract-report-data.py",
        "python3 scripts/extract-infographic-data.py",
        "pip install -r requirements-dev.txt",
        "python3 -m pytest tests/",
        "pytest src/api/tests/",
        "Run `pytest` before committing",
        "Bash(pip install:*)",
        "pip install pre-commit",
        "Requires Python 3.11+",
        "python3 -m json.tool",
        "python3 -c",
        "pip install pre-commit",
        "third-party Python package",
        "pytest-level timeout",
        "requirements-dev.txt",
        "pyproject.toml",
        "make test",
        "tests/scripts/test_init_sh_*.py",
    ];

    for doc in active_docs {
        let content =
            fs::read_to_string(root.join(doc)).unwrap_or_else(|err| panic!("read {doc}: {err}"));
        for retired in retired_refs {
            assert!(
                !content.contains(retired),
                "active doc {doc} should no longer instruct running retired Python guidance: {retired}"
            );
        }
    }
}

#[test]
fn active_devops_docs_and_architecture_summary_frames_are_rust_init_matrix_based() {
    let root = workspace_root();

    let devops_readme = read_lines(&root.join("docs/devops/README.md"), 1, 180);
    assert!(
        devops_readme.contains("Rust init matrix"),
        "active devops README summary should describe the Rust init matrix"
    );
    assert!(
        !devops_readme.contains("tachi-pytest.yml"),
        "active devops README summary should not frame the host-runner workflow as pytest-based"
    );

    let feature_248 = read_lines(&root.join("docs/devops/README.md"), 292, 346);
    assert!(
        feature_248.contains("Rust init matrix"),
        "feature 248 summary should describe the Rust init matrix"
    );
    assert!(
        !feature_248.contains("tachi-pytest.yml"),
        "feature 248 summary should not mention the retired pytest workflow filename"
    );

    let feature_282 = read_lines(&root.join("docs/devops/README.md"), 334, 344);
    assert!(
        feature_282.contains("Rust init matrix path-filter delta"),
        "feature 282 summary should describe the Rust init matrix path-filter delta"
    );
    assert!(
        !feature_282.contains("tachi-pytest.yml"),
        "feature 282 summary should not mention the retired pytest workflow filename"
    );

    let env_vars = read_lines(&root.join("docs/devops/environment-variables.md"), 1, 120);
    assert!(
        env_vars.contains("Rust init matrix workflow"),
        "active environment-variable guidance should describe the Rust init matrix workflow"
    );
    assert!(
        !env_vars.contains("tachi-pytest.yml"),
        "active environment-variable guidance should not name the workflow as pytest-based"
    );

    let local_devops = read_lines(&root.join("docs/devops/01_Local/README.md"), 212, 228);
    assert!(
        local_devops.contains("brew install pre-commit"),
        "local devops guidance should point at the package-manager install path"
    );
    assert!(
        !local_devops.contains("pip install pre-commit"),
        "local devops guidance should not suggest Python-package installation"
    );

    let ci_guide = read_lines(&root.join("docs/devops/CI_CD_GUIDE.md"), 224, 240);
    assert!(
        ci_guide.contains("Outer test harness"),
        "CI guide timing note should name the outer harness instead of pytest"
    );
    assert!(
        !ci_guide.contains("pytest-level timeout"),
        "CI guide timing note should not use pytest-level timeout wording"
    );
    assert!(
        !ci_guide.contains("pytest dependency"),
        "CI guide should not frame the Rust tests as removing a pytest dependency"
    );

    let ci_guide_tail = read_lines(&root.join("docs/devops/CI_CD_GUIDE.md"), 260, 268);
    assert!(
        !ci_guide_tail.contains("Python `pytest` dependency"),
        "CI guide should not call the legacy test dependency pytest"
    );

    let architecture_gate = read_lines(
        &root.join("docs/architecture/00_Tech_Stack/README.md"),
        228,
        240,
    );
    assert!(
        architecture_gate.contains("Rust init matrix"),
        "architecture CI gate guidance should describe the Rust init matrix"
    );
    assert!(
        !architecture_gate.contains("tachi-pytest.yml"),
        "architecture CI gate guidance should not name the matrix as pytest-based"
    );
}

#[test]
fn active_devops_readme_no_longer_names_the_retired_tachi_pytest_workflow_in_live_guidance() {
    let root = workspace_root();

    let devops_readme = read_lines(&root.join("docs/devops/README.md"), 300, 326);
    assert!(
        devops_readme.contains("Rust init matrix"),
        "devops README should describe the Rust init matrix in the live guidance sentence"
    );
    assert!(
        !devops_readme.contains("tachi-pytest"),
        "devops README should not name the retired tachi-pytest workflow in live guidance"
    );
}

#[test]
fn active_git_workflow_doc_uses_rust_test_invocation_in_the_quality_example() {
    let root = workspace_root();

    let git_workflow = read_lines(&root.join("docs/standards/GIT_WORKFLOW.md"), 472, 486);
    assert!(
        git_workflow.contains("cargo test -q"),
        "git workflow quality example should show a Rust test command"
    );
    assert!(
        !git_workflow.contains("run: make test"),
        "git workflow quality example should not use the retired make test command"
    );
}

#[test]
fn active_devops_ci_guide_frames_the_rust_init_matrix_without_pytest_invocation_language() {
    let root = workspace_root();

    let ci_guide = read_lines(&root.join("docs/devops/CI_CD_GUIDE.md"), 140, 265);
    assert!(
        ci_guide.contains("Rust init matrix"),
        "CI guide should frame the workflow as the Rust init matrix"
    );
    assert!(
        ci_guide.contains("cargo test -q -p tachi-shell --test init_substitution"),
        "CI guide should show the Rust test invocation"
    );
    assert!(
        !ci_guide.contains("python -m pytest"),
        "CI guide should not describe the Rust workflow with pytest invocation language"
    );
    assert!(
        !ci_guide.contains("pytest invocation"),
        "CI guide should not keep the old pytest invocation framing"
    );
}

#[test]
fn active_git_workflow_doc_no_longer_uses_make_test_in_the_quality_example() {
    let root = workspace_root();

    let git_workflow = read_lines(&root.join("docs/standards/GIT_WORKFLOW.md"), 472, 486);
    assert!(
        !git_workflow.contains("run: make test"),
        "git workflow quality example should not use the retired make test command"
    );
}

#[test]
fn active_architecture_system_design_ci_section_uses_rust_init_matrix_language() {
    let root = workspace_root();

    let arch_ci = read_lines(
        &root.join("docs/architecture/01_system_design/README.md"),
        3346,
        3356,
    );
    assert!(
        arch_ci.contains("Rust init matrix"),
        "architecture CI section should describe the Rust init matrix"
    );
    assert!(
        !arch_ci.contains("tachi-pytest.yml"),
        "architecture CI section should not name the workflow as pytest-based"
    );
    assert!(
        !arch_ci.contains("pytest invocation"),
        "architecture CI section should not describe the Rust workflow with pytest invocation language"
    );
}

#[test]
fn active_devops_readme_performance_note_avoids_naming_the_python_pytest_dependency() {
    let root = workspace_root();

    let devops_readme = read_lines(&root.join("docs/devops/README.md"), 304, 309);
    assert!(
        devops_readme.contains("Rust suite removes the legacy test dependency"),
        "devops README performance note should describe the dependency generically"
    );
    assert!(
        !devops_readme.contains("Python test dependency"),
        "devops README performance note should not name Python as the dependency"
    );
    assert!(
        !devops_readme.contains("pytest"),
        "devops README performance note should not name pytest as the dependency"
    );
}

#[test]
fn active_tachi_init_matrix_workflow_header_avoids_retired_pytest_framing() {
    let root = workspace_root();

    let workflow_header = read_lines(&root.join(".github/workflows/tachi-pytest.yml"), 1, 24);
    assert!(
        workflow_header.contains("Rust init + doc guard suites"),
        "workflow header should describe the Rust init + doc guard suites generically"
    );
    assert!(
        !workflow_header.contains("retired pytest"),
        "workflow header should not describe the workflow as replacing pytest"
    );
}

#[test]
fn active_devops_ci_guide_does_not_frame_the_workflow_file_as_pytest_based() {
    let root = workspace_root();

    let ci_guide = read_lines(&root.join("docs/devops/CI_CD_GUIDE.md"), 140, 218);
    assert!(
        ci_guide.contains("Rust init matrix"),
        "CI guide should frame the workflow as the Rust init matrix"
    );
    assert!(
        !ci_guide.contains(".github/workflows/tachi-pytest.yml"),
        "CI guide should not frame the workflow file as pytest-based"
    );
}

#[test]
fn active_devops_ci_guide_uses_rust_init_matrix_language_for_the_workflow_file_label() {
    let root = workspace_root();

    let ci_guide = read_lines(&root.join("docs/devops/CI_CD_GUIDE.md"), 32, 38);
    assert!(
        ci_guide.contains("Rust init matrix workflow"),
        "CI guide workflow table should use the Rust init matrix workflow label"
    );
    assert!(
        !ci_guide.contains("tachi-pytest.yml"),
        "CI guide workflow table should not name the retired workflow file"
    );
}

#[test]
fn active_makefile_test_target_uses_rust_test_invocation() {
    let root = workspace_root();

    let makefile = read_lines(&root.join("Makefile"), 33, 42);
    assert!(
        makefile.contains("cargo test -q"),
        "Makefile test target should show a Rust test invocation"
    );
    assert!(
        !makefile.contains("pytest tests/scripts/"),
        "Makefile test target should not invoke the retired pytest suite"
    );
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read_lines(path: &Path, start_line: usize, end_line: usize) -> String {
    assert!(start_line >= 1, "start_line must be 1-based");
    assert!(end_line >= start_line, "end_line must be >= start_line");
    let content =
        fs::read_to_string(path).unwrap_or_else(|err| panic!("read {}: {err}", path.display()));
    content
        .lines()
        .skip(start_line - 1)
        .take(end_line - start_line + 1)
        .collect::<Vec<_>>()
        .join("\n")
}
