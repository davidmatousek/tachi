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
