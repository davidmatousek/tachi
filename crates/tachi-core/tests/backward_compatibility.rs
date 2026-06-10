use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use tachi_core::report_data::build_report_data_typst;

const SOURCE_DATE_EPOCH: &str = "1700000000";
const BASELINE_EXAMPLES: &[&str] = &[
    "web-app",
    "microservices",
    "ascii-web-api",
    "mermaid-agentic-app",
    "free-text-microservice",
    "maestro-reference",
];

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

fn command_available(binary: &str) -> bool {
    Command::new(binary)
        .arg("--version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}

fn hex_context(data: &[u8], offset: usize, window: usize) -> String {
    let start = offset.saturating_sub(window);
    let end = (offset + window + 1).min(data.len());
    let chunk = &data[start..end];
    let hex_repr = chunk
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<Vec<_>>()
        .join(" ");
    format!("bytes[{start}:{end}] = {hex_repr}")
}

fn first_divergence(a: &[u8], b: &[u8]) -> usize {
    let min_len = a.len().min(b.len());
    for idx in 0..min_len {
        if a[idx] != b[idx] {
            return idx;
        }
    }
    min_len
}

#[test]
fn backward_compatibility_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root
            .join("tests/scripts/test_backward_compatibility.py")
            .exists(),
        "backward compatibility coverage should live in Rust tests, not pytest"
    );
}

#[test]
fn unmodified_examples_byte_identical_pdfs() {
    if !command_available("typst") {
        return;
    }

    let workspace = workspace_root();
    let template_dir = workspace.join("templates/tachi/security-report");
    let report_data_path = template_dir.join("report-data.typ");
    let report_data_guard = ReportDataBackup::new(report_data_path.clone());

    for example_name in BASELINE_EXAMPLES {
        let target_dir = workspace.join("examples").join(example_name);
        let baseline_pdf = target_dir.join("security-report.pdf.baseline");
        let generated_pdf =
            unique_temp_dir("tachi-backward-compatibility").join("security-report.pdf");

        assert!(
            baseline_pdf.exists(),
            "baseline PDF missing for example {example_name:?}: {}",
            baseline_pdf.display()
        );

        let rendered = build_report_data_typst(&target_dir, &template_dir);
        fs::write(&report_data_path, rendered).expect("write report-data.typ");

        let result = Command::new("typst")
            .arg("compile")
            .arg(template_dir.join("main.typ"))
            .arg(&generated_pdf)
            .arg("--root")
            .arg(&workspace)
            .current_dir(&workspace)
            .env("SOURCE_DATE_EPOCH", SOURCE_DATE_EPOCH)
            .output()
            .expect("run typst compile");

        assert!(
            result.status.success(),
            "typst compile should succeed for example {example_name:?}. stdout={:?} stderr={:?}",
            String::from_utf8_lossy(&result.stdout),
            String::from_utf8_lossy(&result.stderr)
        );

        let baseline_bytes = fs::read(&baseline_pdf).expect("read baseline pdf");
        let generated_bytes = fs::read(&generated_pdf).expect("read generated pdf");

        if baseline_bytes == generated_bytes {
            continue;
        }

        let divergence = first_divergence(&baseline_bytes, &generated_bytes);
        let baseline_ctx = hex_context(&baseline_bytes, divergence, 16);
        let generated_ctx = hex_context(&generated_bytes, divergence, 16);

        panic!(
            "PDF byte mismatch for example {example_name:?}.\n\
             Baseline size:  {} bytes ({})\n\
             Generated size: {} bytes ({})\n\
             First divergence at byte offset: {}\n\
             Baseline context:  {}\n\
             Generated context: {}\n\
             SOURCE_DATE_EPOCH={} (determinism pin).",
            baseline_bytes.len(),
            baseline_pdf.display(),
            generated_bytes.len(),
            generated_pdf.display(),
            divergence,
            baseline_ctx,
            generated_ctx,
            SOURCE_DATE_EPOCH,
        );
    }

    drop(report_data_guard);
}
