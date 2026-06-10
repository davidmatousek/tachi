use std::path::PathBuf;

use tachi_shell::commands::coverage_audit_output;

#[test]
fn coverage_audit_output_matches_core_counts_on_repo_root() {
    let repo_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..");

    let output = coverage_audit_output(&repo_root);

    assert!(output.contains("Active test modules: 75"));
    assert!(output.contains("Fixture-copy modules (excluded from active suite): 3"));
    assert!(output.contains("Unit: 3"));
    assert!(output.contains("Integration: 40"));
    assert!(output.contains("Smoke: 3"));
    assert!(output.contains("True end-to-end: 1"));
}
