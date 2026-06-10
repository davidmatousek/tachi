use std::path::PathBuf;
use std::process::Command;

#[test]
fn coverage_audit_binary_reports_current_suite_classification() {
    let repo_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..");

    let binary = std::env::var("CARGO_BIN_EXE_coverage-audit")
        .expect("CARGO_BIN_EXE_coverage-audit should be provided by cargo");

    let output = Command::new(binary)
        .current_dir(&repo_root)
        .output()
        .expect("run coverage-audit binary");

    assert!(
        output.status.success(),
        "coverage-audit binary should run successfully. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("Active test modules: 71"));
    assert!(stdout.contains("Fixture-copy modules (excluded from active suite): 3"));
    assert!(stdout.contains("Unit: 0"));
    assert!(stdout.contains("Integration: 44"));
    assert!(stdout.contains("Smoke: 2"));
    assert!(stdout.contains("True end-to-end: 1"));
    assert!(stdout.contains("Support / regression: 24"));
}
