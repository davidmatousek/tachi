use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::report_data::build_report_data_typst;

const PNG_MAGIC: &[u8] = b"\x89PNG\r\n\x1a\n";
const JPEG_MAGIC: &[u8] = b"\xff\xd8\xff\xe0\x00\x10JFIF";
const LEGACY_IMAGE_FLAGS: &[(&str, &str)] = &[
    ("threat-risk-funnel.jpg", "#let has-funnel-image = true"),
    ("threat-baseball-card.jpg", "#let has-baseball-image = true"),
    (
        "threat-system-architecture.jpg",
        "#let has-architecture-image = true",
    ),
    (
        "threat-maestro-stack.jpg",
        "#let has-maestro-stack-image = true",
    ),
    (
        "threat-maestro-heatmap.jpg",
        "#let has-maestro-heatmap-image = true",
    ),
];

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

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
fn build_report_data_typst_emits_project_name_from_threat_model() {
    let root = unique_temp_dir("tachi-report-data-project");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_bytes(
        &target_dir.join("threats.md"),
        b"# Threat Model: Report Data App\n",
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    assert!(rendered.contains("#let project-name = \"Report Data App\""));
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
    assert!(target_dir
        .join("threat-executive-architecture.png")
        .exists());
}

#[test]
fn build_report_data_typst_matches_retired_image_binding_pytest_contract() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_extract_report_data.py")
            .exists(),
        "report-data image binding coverage should live in Rust tests, not pytest"
    );

    let root = unique_temp_dir("tachi-report-data-legacy-flags");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    for (filename, _) in LEGACY_IMAGE_FLAGS {
        write_bytes(
            &target_dir.join(filename),
            &[JPEG_MAGIC, b"payload"].concat(),
        );
    }

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    for (_, flag_line) in LEGACY_IMAGE_FLAGS {
        assert!(
            rendered.lines().any(|line| line == *flag_line),
            "expected legacy image flag line {flag_line:?}"
        );
    }
}

#[test]
fn build_report_data_typst_emits_coverage_attestation_payload_when_source_attribution_exists() {
    let root = unique_temp_dir("tachi-report-data-source-attribution");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_bytes(
        &target_dir.join("threats.md"),
        br#"# Agentic AI Application

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| AG-1 | Component | Threat | High | Mitigation | [NEW] |

## 9. Source Attribution

```yaml
AG-1:
  - {taxonomy: "owasp", id: "A01", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-79", relationship: "related"}
```
"#,
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    assert!(rendered.contains("#let has-source-attribution = true"));
    assert!(rendered.contains("#let per-finding-rows = ("));
    assert!(rendered.contains("#let per-framework-aggregates = ("));
    assert!(!rendered.contains("ATT&CK:"));
}

#[test]
fn build_report_data_typst_prefers_self_consistent_png_over_stale_jpg() {
    let root = unique_temp_dir("tachi-report-data-mixed-extension");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_bytes(
        &target_dir.join("threat-executive-architecture.jpg"),
        &[PNG_MAGIC, b"stale"].concat(),
    );
    write_bytes(
        &target_dir.join("threat-executive-architecture.png"),
        &[PNG_MAGIC, b"fresh"].concat(),
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    let path_line = rendered
        .lines()
        .find(|line| line.starts_with("#let executive-architecture-image-path"))
        .expect("executive architecture path line");
    assert!(path_line.ends_with("threat-executive-architecture.png\""));
}
