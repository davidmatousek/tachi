use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::coverage_audit::{collect_audit, render};

fn unique_temp_dir(prefix: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock should be monotonic")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{nanos}"))
}

fn write_file(path: &Path) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent directories");
    }
    fs::write(path, "").expect("write test file");
}

#[test]
fn collect_audit_classifies_active_and_fixture_copies() {
    let root = unique_temp_dir("tachi-coverage-audit");

    write_file(&root.join("tests/scripts/test_smoke.py"));
    write_file(&root.join("tests/scripts/test_example_unit.py"));
    write_file(&root.join("tests/scripts/test_example_integration.py"));
    write_file(&root.join("tests/fixtures/init-baseline-tree/tests/scripts/test_fixture_unit.py"));

    let audit = collect_audit(&root);

    assert_eq!(audit.active.len(), 3);
    assert_eq!(audit.fixture_copies.len(), 1);
    assert_eq!(audit.smoke.len(), 1);
    assert_eq!(audit.unit.len(), 1);
    assert_eq!(audit.integration.len(), 1);
    assert_eq!(audit.e2e.len(), 0);
    assert_eq!(audit.support.len(), 0);

    let rendered = render(&audit, &root);
    assert!(rendered.contains("Active test modules: 3"));
    assert!(rendered.contains("Fixture-copy modules (excluded from active suite): 1"));
    assert!(rendered.contains("Smoke: 1"));
    assert!(rendered.contains("Unit: 1"));
    assert!(rendered.contains("Integration: 1"));
}

#[test]
fn collect_audit_includes_rust_test_modules_as_active_integration_coverage() {
    let root = unique_temp_dir("tachi-coverage-audit-rust");

    write_file(&root.join("tests/scripts/test_smoke.py"));
    write_file(&root.join("crates/tachi-core/tests/assets.rs"));
    write_file(&root.join("crates/tachi-shell/tests/infographic_data.rs"));
    write_file(&root.join("tests/fixtures/init-baseline-tree/tests/scripts/test_fixture_unit.py"));

    let audit = collect_audit(&root);

    assert_eq!(audit.active.len(), 3);
    assert_eq!(audit.fixture_copies.len(), 1);
    assert_eq!(audit.smoke.len(), 1);
    assert_eq!(audit.integration.len(), 2);
    assert_eq!(audit.unit.len(), 0);
    assert_eq!(audit.e2e.len(), 0);
    assert_eq!(audit.support.len(), 0);

    let rendered = render(&audit, &root);
    assert!(rendered.contains("Active test modules: 3"));
    assert!(rendered.contains("Integration: 2"));
    assert!(rendered.contains("Smoke: 1"));
}

#[test]
fn collect_audit_classifies_rust_smoke_canary_as_smoke_coverage() {
    let root = unique_temp_dir("tachi-coverage-audit-rust-smoke");

    write_file(&root.join("crates/tachi-core/tests/coverage_attestation_pagination.rs"));
    write_file(&root.join("crates/tachi-shell/tests/infographic_data.rs"));
    write_file(&root.join("tests/fixtures/init-baseline-tree/tests/scripts/test_fixture_unit.py"));

    let audit = collect_audit(&root);

    assert_eq!(audit.active.len(), 2);
    assert_eq!(audit.fixture_copies.len(), 1);
    assert_eq!(audit.smoke.len(), 1);
    assert_eq!(audit.integration.len(), 1);
    assert_eq!(audit.unit.len(), 0);
    assert_eq!(audit.e2e.len(), 0);
    assert_eq!(audit.support.len(), 0);

    let rendered = render(&audit, &root);
    assert!(rendered.contains("Smoke: 1"));
    assert!(rendered.contains("Integration: 1"));
}

#[test]
fn collect_audit_classifies_inline_source_tests_as_unit_coverage() {
    let root = unique_temp_dir("tachi-coverage-audit-unit");

    write_file(&root.join("crates/tachi-core/src/report_data.rs"));
    write_file(&root.join("crates/tachi-shell/tests/infographic_data.rs"));
    write_file(&root.join("tests/fixtures/init-baseline-tree/tests/scripts/test_fixture_unit.py"));

    fs::write(
        root.join("crates/tachi-core/src/report_data.rs"),
        "#[cfg(test)]\nmod tests {}\n",
    )
    .expect("write inline unit source");

    let audit = collect_audit(&root);

    assert_eq!(audit.active.len(), 2);
    assert_eq!(audit.fixture_copies.len(), 1);
    assert_eq!(audit.unit.len(), 1);
    assert_eq!(audit.integration.len(), 1);
    assert_eq!(audit.smoke.len(), 0);
    assert_eq!(audit.e2e.len(), 0);
    assert_eq!(audit.support.len(), 0);

    let rendered = render(&audit, &root);
    assert!(rendered.contains("Unit: 1"));
    assert!(rendered.contains("Integration: 1"));
}
