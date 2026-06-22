use std::fs;
use std::path::PathBuf;

use tachi_tauri::{
    build_release_manifest_typed, dispatch_desktop_command, restore_offline_cache_typed,
    validate_invoke_input_typed, verify_checksum_matrix_typed, DesktopErrorKind,
};

fn fixture_root(prefix: &str) -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-{prefix}-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));
    fs::create_dir_all(&root).expect("create fixture root");
    root
}

#[test]
fn typed_validation_and_command_output_share_stable_codes() {
    let root = fixture_root("error-taxonomy-schema");
    let err = validate_invoke_input_typed("report-data", &root, &["--target-dir", "target"])
        .expect_err("missing template-dir");
    assert_eq!(err.kind(), DesktopErrorKind::Validation);
    assert_eq!(err.code(), 2);
    assert!(err.message().contains("--template-dir is required"));

    let output = dispatch_desktop_command("report-data", &root, &["--target-dir", "target"]);
    assert_eq!(output.status, 2);
    assert!(output.stderr.contains("schema validation failed for report-data"));
}

#[test]
fn typed_policy_and_io_failures_use_distinct_codes() {
    let repo_root = fixture_root("error-taxonomy-offline");
    let cache_root = fixture_root("error-taxonomy-cache");
    let policy_err =
        restore_offline_cache_typed(&repo_root.join(".."), &cache_root).expect_err("reject root traversal");
    assert_eq!(policy_err.kind(), DesktopErrorKind::Policy);
    assert_eq!(policy_err.code(), 3);

    let release_root = fixture_root("error-taxonomy-release");
    let io_err = build_release_manifest_typed(
        &release_root,
        &["dist/missing.tar.gz"],
    )
    .expect_err("missing artifact");
    assert_eq!(io_err.kind(), DesktopErrorKind::Io);
    assert_eq!(io_err.code(), 4);
    assert!(io_err.message().contains("failed to read"));
}

#[test]
fn typed_release_policy_and_internal_codes_are_distinct() {
    let root = fixture_root("error-taxonomy-release-policy");
    fs::create_dir_all(root.join("dist")).expect("create dist dir");
    fs::write(root.join("dist/artifact.tar.gz"), "original").expect("write artifact");
    let manifest = build_release_manifest_typed(&root, &["dist/artifact.tar.gz"])
        .expect("build manifest");
    fs::write(root.join("dist/artifact.tar.gz"), "tampered").expect("tamper artifact");

    let policy_err = verify_checksum_matrix_typed(&root, &manifest).expect_err("detect tamper");
    assert_eq!(policy_err.kind(), DesktopErrorKind::Policy);
    assert_eq!(policy_err.code(), 3);

    let internal = tachi_tauri::DesktopError::internal("desktop boundary failure");
    assert_eq!(internal.kind(), DesktopErrorKind::Internal);
    assert_eq!(internal.code(), 1);
    assert!(internal.message().contains("desktop boundary failure"));
}
