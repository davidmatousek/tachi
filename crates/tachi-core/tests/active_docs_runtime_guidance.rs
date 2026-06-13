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

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}
