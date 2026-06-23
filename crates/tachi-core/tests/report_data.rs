use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::build_report_data_typst;

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

fn write_text(path: &Path, content: &str) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).expect("create parent directories");
    }
    fs::write(path, content).expect("write test file");
}

struct ReportDataBackup {
    path: PathBuf,
    backup: Option<Vec<u8>>,
}

impl ReportDataBackup {
    fn new(path: PathBuf) -> Self {
        let backup = path
            .exists()
            .then(|| fs::read(&path).expect("backup report-data.typ"));
        Self { path, backup }
    }
}

impl Drop for ReportDataBackup {
    fn drop(&mut self) {
        if let Some(previous) = &self.backup {
            let _ = fs::write(&self.path, previous);
        } else if self.path.exists() {
            let _ = fs::remove_file(&self.path);
        }
    }
}

fn command_available(binary: &str) -> bool {
    Command::new(binary)
        .arg("--version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}

fn extract_pdf_strings(pdf_path: &Path) -> Vec<String> {
    let output = Command::new("strings")
        .arg(pdf_path)
        .output()
        .expect("run strings on PDF");

    assert!(
        output.status.success(),
        "strings should run successfully. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );

    String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(|line| line.to_string())
        .collect()
}

fn find_first_line_with_heading(lines: &[String], heading: &str) -> Option<usize> {
    lines
        .iter()
        .position(|line| line.contains(heading))
        .map(|idx| idx + 1)
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
fn build_report_data_typst_marks_empty_source_attribution_reports_as_false() {
    let root = unique_temp_dir("tachi-report-data-empty-source");
    let target_dir = root.join("examples/agentic-app/sample-report");
    let template_dir = root.join("templates/tachi/security-report");

    write_text(
        &target_dir.join("threats.md"),
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n| AG-1 | Component | Threat | High | Mitigation | [NEW] |\n",
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);

    assert!(rendered.contains("#let has-source-attribution = false"));
}

#[test]
fn build_report_data_typst_keeps_typst_compilable_when_report_data_lacks_new_bindings() {
    let typst = match Command::new("typst").arg("--version").output() {
        Ok(output) if output.status.success() => "typst",
        _ => return,
    };
    let _ = typst;

    let workspace = unique_temp_dir("tachi-report-data-typst-copy");
    let template_dir = workspace.join("templates/tachi/security-report");
    copy_dir_all(
        &workspace_root().join("templates/tachi/security-report"),
        &template_dir,
    );
    let report_data_path = template_dir.join("report-data.typ");
    let target_dir = workspace.join("examples/agentic-app/sample-report");
    write_text(
        &target_dir.join("threats.md"),
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n| AG-1 | Component | Threat | High | Mitigation | [NEW] |\n\n## 9. Source Attribution\n\n```yaml\nAG-1:\n  - {taxonomy: \"owasp\", id: \"A01\", relationship: \"primary\"}\n```\n",
    );

    let rendered = build_report_data_typst(&target_dir, &template_dir);
    let stripped = rendered
        .lines()
        .filter(|line| {
            let trimmed = line.trim_start();
            !trimmed.starts_with("#let has-source-attribution")
                && !trimmed.starts_with("#let per-finding-rows")
                && !trimmed.starts_with("#let per-framework-aggregates")
        })
        .collect::<Vec<_>>()
        .join("\n")
        + "\n";

    write_text(&report_data_path, &stripped);
    let result = Command::new("typst")
        .arg("compile")
        .arg(template_dir.join("main.typ"))
        .arg(workspace.join("out.pdf"))
        .arg("--root")
        .arg(&workspace)
        .current_dir(&workspace)
        .output()
        .expect("run typst compile");

    assert!(
        result.status.success(),
        "typst compile should succeed with stale report-data.typ. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&result.stdout),
        String::from_utf8_lossy(&result.stderr)
    );
}

fn copy_dir_all(src: &Path, dst: &Path) {
    fs::create_dir_all(dst).expect("create destination directory");
    for entry in fs::read_dir(src).expect("read source directory") {
        let entry = entry.expect("read source entry");
        let src_path = entry.path();
        let dst_path = dst.join(entry.file_name());
        if entry.file_type().expect("source entry type").is_dir() {
            copy_dir_all(&src_path, &dst_path);
        } else {
            fs::copy(&src_path, &dst_path).expect("copy source file");
        }
    }
}

#[test]
fn build_report_data_typst_renders_executive_architecture_page_between_summary_and_attack_path() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_pdf_page_positioning.py")
            .exists(),
        "pdf page positioning coverage should live in Rust tests, not pytest"
    );

    if !command_available("typst") {
        return;
    }

    let workspace = workspace_root();
    let target_dir = workspace.join("examples/agentic-app/sample-report");
    let template_dir = workspace.join("templates/tachi/security-report");
    let report_data_path = template_dir.join("report-data.typ");
    let report_data_guard = ReportDataBackup::new(report_data_path.clone());

    let rendered = build_report_data_typst(&target_dir, &template_dir);
    fs::write(&report_data_path, rendered).expect("write report-data.typ");

    let output_pdf = unique_temp_dir("tachi-pdf-page-positioning").join("security-report.pdf");
    if let Some(parent) = output_pdf.parent() {
        fs::create_dir_all(parent).expect("create temp pdf dir");
    }

    let result = Command::new("typst")
        .arg("compile")
        .arg(template_dir.join("main.typ"))
        .arg(&output_pdf)
        .arg("--root")
        .arg(&workspace)
        .current_dir(&workspace)
        .output()
        .expect("run typst compile");

    assert!(
        result.status.success(),
        "typst compile should succeed for the agentic-app sample. stdout={:?} stderr={:?}",
        String::from_utf8_lossy(&result.stdout),
        String::from_utf8_lossy(&result.stderr)
    );
    assert!(
        output_pdf.exists()
            && fs::metadata(&output_pdf)
                .map(|metadata| metadata.len() > 0)
                .unwrap_or(false)
    );

    let lines = extract_pdf_strings(&output_pdf);
    assert!(!lines.is_empty(), "expected PDF strings output");

    let exec_summary_pos = find_first_line_with_heading(&lines, "Executive Summary")
        .expect("Executive Summary heading");
    let exec_architecture_pos =
        find_first_line_with_heading(&lines, "Executive Threat Architecture")
            .expect("Executive Threat Architecture heading");
    let attack_progression_pos = find_first_line_with_heading(&lines, "Attack Progression")
        .expect("Attack Progression heading");

    assert!(
        exec_architecture_pos > exec_summary_pos,
        "Executive Threat Architecture must appear after Executive Summary"
    );
    assert!(
        exec_architecture_pos < attack_progression_pos,
        "Executive Threat Architecture must appear before the attack progression content"
    );

    drop(report_data_guard);
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
