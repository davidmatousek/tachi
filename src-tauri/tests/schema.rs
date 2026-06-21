use pretty_assertions::assert_eq;
use serde_json::json;
use tachi_tauri::{
    render_schema_error, validate_invoke_input, validate_invoke_output, DesktopInvokeInput,
};

fn workspace_root() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("workspace root")
        .to_path_buf()
}

#[test]
fn validate_invoke_input_returns_typed_requests() {
    let root = workspace_root();

    let report = validate_invoke_input(
        "report-data",
        &root,
        &["--target-dir", "target", "--template-dir", "templates"],
    )
    .expect("report-data schema");

    assert_eq!(
        report,
        DesktopInvokeInput::ReportData {
            target_dir: "target".into(),
            template_dir: "templates".into(),
            output: None,
        }
    );
}

#[test]
fn validate_invoke_input_rejects_missing_required_fields_and_unknown_commands() {
    let root = workspace_root();

    let err = validate_invoke_input("report-data", &root, &["--target-dir", "target"])
        .expect_err("missing template-dir");
    assert!(err.contains("schema validation failed for report-data"));
    assert!(err.contains("--template-dir is required"));

    let err = validate_invoke_input("unknown-command", &root, &[]).expect_err("unknown command");
    assert!(err.contains("unsupported command"));
}

#[test]
fn validate_invoke_output_rejects_schema_drift() {
    let valid = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: "#let project-name = \"Demo\"\n".into(),
        stderr: String::from("report-data.typ generated\n"),
    };
    validate_invoke_output("report-data", &valid).expect("valid report-data output");

    let invalid = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: String::new(),
        stderr: String::new(),
    };
    let err = validate_invoke_output("report-data", &invalid).expect_err("reject empty output");
    assert!(err.contains("schema validation failed for report-data"));

    let infographic = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: json!({
            "template": "maestro-stack",
            "template_data": {}
        })
        .to_string(),
        stderr: String::new(),
    };
    validate_invoke_output("infographic-data", &infographic).expect("valid infographic output");
}

#[test]
fn render_schema_error_includes_command_and_reason() {
    let err = render_schema_error("threats-sarif", "--input is required");
    assert!(err.contains("threats-sarif"));
    assert!(err.contains("--input is required"));
}
