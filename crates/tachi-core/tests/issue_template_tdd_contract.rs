use std::fs;
use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read(path: &str) -> String {
    fs::read_to_string(repo_root().join(path)).unwrap_or_else(|err| panic!("read {path}: {err}"))
}

#[test]
fn issue_templates_require_tdd_acceptance_evidence() {
    for path in [
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
    ] {
        let text = read(path);

        for required in [
            "Failing test first",
            "Exact validation gate",
            "Positive case",
            "Negative/adversarial case",
            "Property/golden/mutation applicability",
        ] {
            assert!(text.contains(required), "{path} must require `{required}`");
        }
    }
}

#[test]
fn pull_request_template_requires_tdd_and_publish_gate_evidence() {
    let text = read(".github/pull_request_template.md");

    for required in [
        "Failing test first",
        "Exact validation gate",
        "Positive case",
        "Negative/adversarial case",
        "Property/golden/mutation applicability",
        "make publish-gate",
    ] {
        assert!(
            text.contains(required),
            "pull request template must require `{required}`"
        );
    }
}
