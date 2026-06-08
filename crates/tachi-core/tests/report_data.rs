use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::report_data::build_report_data_typst;

const PNG_MAGIC: &[u8] = b"\x89PNG\r\n\x1a\n";
const JPEG_MAGIC: &[u8] = b"\xff\xd8\xff\xe0\x00\x10JFIF";

fn unique_temp_dir(prefix: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock should be monotonic")
        .as_nanos();
    std::env::temp_dir().join(format!("{prefix}-{nanos}"))
}

fn write_bytes(path: &Path, bytes: &[u8]) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent directories");
    }
    fs::write(path, bytes).expect("write test file");
}

#[test]
fn build_report_data_typst_sets_executive_architecture_flags_and_relative_path() {
    let root = unique_temp_dir("tachi-report-data");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_bytes(
        &target_dir.join("threat-executive-architecture.jpg"),
        &[JPEG_MAGIC, b"payload"].concat(),
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    assert!(rendered.contains("#let has-executive-architecture = true"));
    let path_line = rendered
        .lines()
        .find(|line| line.starts_with("#let executive-architecture-image-path"))
        .expect("executive architecture path line");
    assert!(path_line.contains("threat-executive-architecture.jpg"));
    assert!(!path_line.contains("://"));
    assert!(!path_line.contains(" = \"/"));
    assert!(rendered.contains("#let has-funnel-image = false"));
}

#[test]
fn build_report_data_typst_treats_zero_byte_executive_architecture_images_as_absent() {
    let root = unique_temp_dir("tachi-report-data-zero");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_bytes(&target_dir.join("threat-executive-architecture.jpg"), &[]);

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    assert!(rendered.contains("#let has-executive-architecture = false"));
    assert!(rendered.contains("#let executive-architecture-image-path = \"\""));
    assert!(!rendered.contains("#let has-executive-architecture = true"));
}

#[test]
fn build_report_data_typst_corrects_mislabeled_pngs_to_png_siblings() {
    let root = unique_temp_dir("tachi-report-data-png");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_bytes(
        &target_dir.join("threat-executive-architecture.jpg"),
        &[PNG_MAGIC, b"payload"].concat(),
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    assert!(rendered.contains("#let has-executive-architecture = true"));
    let path_line = rendered
        .lines()
        .find(|line| line.starts_with("#let executive-architecture-image-path"))
        .expect("executive architecture path line");
    assert!(path_line.contains("threat-executive-architecture.png"));
    assert!(!path_line.contains("://"));
    assert!(target_dir.join("threat-executive-architecture.png").exists());
}
