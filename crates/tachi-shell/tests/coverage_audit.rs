use std::path::PathBuf;

use tachi_shell::commands::coverage_audit_output;

#[test]
fn coverage_audit_output_preserves_category_labels_on_repo_root() {
    let repo_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..");

    let output = coverage_audit_output(&repo_root);

    assert!(output.contains("Active test modules:"));
    assert!(output.contains("Fixture-copy modules (excluded from active suite):"));
    assert!(output.contains("Unit:"));
    assert!(output.contains("Integration:"));
    assert!(output.contains("Smoke:"));
    assert!(output.contains("True end-to-end:"));
    assert!(output.contains("Support / regression:"));
}
