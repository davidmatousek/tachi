use std::fs;
use std::path::PathBuf;

use tachi_shell::commands::{
    render_report_data_result, report_data_output, report_data_result,
    validate_report_data_result, ReportDataResult,
};

fn workspace_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|path| path.parent())
        .expect("workspace root")
        .to_path_buf()
}

fn fixture_root() -> PathBuf {
    std::env::temp_dir().join(format!(
        "tachi-rust-report-data-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}

#[test]
fn report_data_result_validates_before_legacy_rendering() {
    let root = fixture_root();
    let target_dir = root.join("target");
    let template_dir = root.join("templates/tachi/security-report");
    fs::create_dir_all(&template_dir).expect("create template dir");
    fs::create_dir_all(&target_dir).expect("create target dir");
    fs::copy(
        workspace_root().join("tests/scripts/fixtures/report_data/image_absent/threats.md"),
        target_dir.join("threats.md"),
    )
    .expect("copy threats fixture");

    let result = report_data_result(&target_dir, &template_dir);
    validate_report_data_result(&result).expect("typed report-data result");
    assert_eq!(render_report_data_result(&result), report_data_output(&target_dir, &template_dir));
}

#[test]
fn report_data_result_rejects_missing_project_name_binding() {
    let err = validate_report_data_result(&ReportDataResult {
        typst: String::new(),
    })
    .expect_err("reject empty typed result");
    assert!(err.contains("project-name binding"));
}
