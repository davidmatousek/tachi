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
    let active = extract_count(&stdout, "Active test modules: ");
    let fixture_copies = extract_count(
        &stdout,
        "Fixture-copy modules (excluded from active suite): ",
    );
    let smoke = extract_count(&stdout, "Smoke: ");
    let unit = extract_count(&stdout, "Unit: ");
    let integration = extract_count(&stdout, "Integration: ");
    let e2e = extract_count(&stdout, "True end-to-end: ");
    let support = extract_count(&stdout, "Support / regression: ");

    assert!(stdout.contains("Active test modules:"));
    assert!(stdout.contains("Fixture-copy modules (excluded from active suite):"));
    assert!(stdout.contains("Smoke:"));
    assert!(stdout.contains("Unit:"));
    assert!(stdout.contains("Integration:"));
    assert!(stdout.contains("True end-to-end:"));
    assert!(stdout.contains("Support / regression:"));
    assert!(active >= smoke + unit + integration + e2e + support);
    assert!(active >= fixture_copies);
}

fn extract_count(stdout: &str, prefix: &str) -> usize {
    stdout
        .lines()
        .find_map(|line| line.strip_prefix(prefix))
        .and_then(|value| value.trim().parse::<usize>().ok())
        .expect("count should be present in coverage-audit output")
}
