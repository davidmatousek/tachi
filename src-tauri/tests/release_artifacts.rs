use std::fs;
use std::path::{Path, PathBuf};

use pretty_assertions::assert_eq;
use tachi_tauri::{
    build_release_manifest, validate_package_contents, verify_checksum_matrix, PackageContentReport,
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

fn write_file(root: &Path, relative: &str, contents: &str) {
    let path = root.join(relative);
    fs::create_dir_all(path.parent().expect("parent")).expect("create parent");
    fs::write(path, contents).expect("write fixture file");
}

#[test]
fn build_release_manifest_is_stable_for_identical_inputs() {
    let left = fixture_root("release-manifest-left");
    let right = fixture_root("release-manifest-right");

    for root in [&left, &right] {
        write_file(
            root,
            "dist/tachi-rust-linux-x86_64.tar.gz",
            "artifact-bytes",
        );
        write_file(
            root,
            "dist/tachi-rust-linux-x86_64.tar.gz.sha256",
            "sha-placeholder",
        );
        write_file(
            root,
            "release/release-manifest.json",
            "{\"version\":\"1.0.0\"}\n",
        );
    }

    let left_manifest = build_release_manifest(
        &left,
        &[
            "release/release-manifest.json",
            "dist/tachi-rust-linux-x86_64.tar.gz",
            "dist/tachi-rust-linux-x86_64.tar.gz.sha256",
        ],
    )
    .expect("build left manifest");
    let right_manifest = build_release_manifest(
        &right,
        &[
            "dist/tachi-rust-linux-x86_64.tar.gz.sha256",
            "dist/tachi-rust-linux-x86_64.tar.gz",
            "release/release-manifest.json",
        ],
    )
    .expect("build right manifest");

    assert_eq!(left_manifest, right_manifest);
    verify_checksum_matrix(&left, &left_manifest).expect("verify left manifest");
}

#[test]
fn verify_checksum_matrix_detects_mutated_artifact_bytes() {
    let root = fixture_root("release-manifest-mutation");

    write_file(&root, "dist/tachi-rust-macos-aarch64.zip", "original-bytes");
    write_file(
        &root,
        "release/release-manifest.json",
        "{\"version\":\"1.0.0\"}\n",
    );

    let manifest = build_release_manifest(
        &root,
        &[
            "dist/tachi-rust-macos-aarch64.zip",
            "release/release-manifest.json",
        ],
    )
    .expect("build manifest");

    write_file(&root, "dist/tachi-rust-macos-aarch64.zip", "tampered-bytes");

    let err = verify_checksum_matrix(&root, &manifest).expect_err("detect tamper");
    assert!(err.contains("checksum mismatch"), "{err}");
}

#[test]
fn validate_package_contents_reports_missing_and_unexpected_files() {
    let root = fixture_root("release-package-contents");

    write_file(&root, "dist/tachi-rust-windows-x86_64.msi", "msi-bytes");
    write_file(
        &root,
        "release/release-manifest.json",
        "{\"version\":\"1.0.0\"}\n",
    );
    write_file(&root, "notes/keep.txt", "unexpected");

    let report = validate_package_contents(
        &root,
        &[
            "dist/tachi-rust-windows-x86_64.msi",
            "dist/tachi-rust-windows-x86_64.msi.sha256",
            "release/release-manifest.json",
        ],
    )
    .expect("validate package contents");

    assert_eq!(
        report,
        PackageContentReport {
            expected_files: vec![
                root.join("dist/tachi-rust-windows-x86_64.msi"),
                root.join("dist/tachi-rust-windows-x86_64.msi.sha256"),
                root.join("release/release-manifest.json"),
            ],
            actual_files: vec![
                root.join("dist/tachi-rust-windows-x86_64.msi"),
                root.join("notes/keep.txt"),
                root.join("release/release-manifest.json"),
            ],
            missing_files: vec![root.join("dist/tachi-rust-windows-x86_64.msi.sha256")],
            unexpected_files: vec![root.join("notes/keep.txt")],
        }
    );
}
