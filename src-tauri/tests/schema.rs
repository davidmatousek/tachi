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

    let coverage = validate_invoke_input("coverage-audit", &root, &["--root", "custom"])
        .expect("coverage-audit schema");
    assert_eq!(
        coverage,
        DesktopInvokeInput::CoverageAudit {
            root: "custom".into(),
        }
    );

    let infographic = validate_invoke_input(
        "infographic-data",
        &root,
        &[
            "--root",
            "report",
            "--template",
            "maestro-stack",
            "--output",
            "out.json",
        ],
    )
    .expect("infographic-data schema");
    assert_eq!(
        infographic,
        DesktopInvokeInput::InfographicData {
            root: "report".into(),
            template: "maestro-stack".into(),
            output: Some("out.json".into()),
        }
    );

    let threats = validate_invoke_input(
        "threats-sarif",
        &root,
        &["--input", "threats.md", "--output", "threats.sarif"],
    )
    .expect("threats-sarif schema");
    assert_eq!(
        threats,
        DesktopInvokeInput::ThreatsSarif {
            input: "threats.md".into(),
            output: "threats.sarif".into(),
        }
    );

    let risk_scores = validate_invoke_input(
        "risk-scores-sarif",
        &root,
        &[
            "--risk-scores",
            "risk-scores.md",
            "--threats",
            "threats.md",
            "--output",
            "risk.sarif",
        ],
    )
    .expect("risk-scores-sarif schema");
    assert_eq!(
        risk_scores,
        DesktopInvokeInput::RiskScoresSarif {
            risk_scores: "risk-scores.md".into(),
            threats: "threats.md".into(),
            output: "risk.sarif".into(),
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

    let err = validate_invoke_input("coverage-audit", &root, &["--help"])
        .expect_err("reject help payload");
    assert!(err.contains("help is not an invocation payload"));

    let err = validate_invoke_input("infographic-data", &root, &["--template"])
        .expect_err("missing template value");
    assert!(err.contains("--template requires a path argument"));

    let err = validate_invoke_input("infographic-data", &root, &["--wat"])
        .expect_err("unknown infographic arg");
    assert!(err.contains("unrecognized argument: --wat"));

    let err = validate_invoke_input("threats-sarif", &root, &["--input", "threats.md"])
        .expect_err("missing threats output");
    assert!(err.contains("--output is required"));

    let err = validate_invoke_input(
        "risk-scores-sarif",
        &root,
        &["--risk-scores", "risk-scores.md", "--help"],
    )
    .expect_err("reject risk help payload");
    assert!(err.contains("help is not an invocation payload"));
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

    let failed_command = tachi_shell::commands::CommandOutput {
        status: 2,
        stdout: String::new(),
        stderr: String::from("bad input"),
    };
    validate_invoke_output("report-data", &failed_command).expect("non-zero output is caller-visible");

    let invalid_coverage = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: String::from("not a coverage audit"),
        stderr: String::new(),
    };
    let err = validate_invoke_output("coverage-audit", &invalid_coverage)
        .expect_err("reject malformed coverage output");
    assert!(err.contains("coverage audit output missing expected summary fields"));

    let invalid_infographic = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: json!({"template": "maestro-stack"}).to_string(),
        stderr: String::new(),
    };
    let err = validate_invoke_output("infographic-data", &invalid_infographic)
        .expect_err("reject missing template data");
    assert!(err.contains("infographic JSON output missing template fields"));

    let valid_threats_sarif = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: String::new(),
        stderr: String::from("OK: wrote threats.sarif"),
    };
    validate_invoke_output("threats-sarif", &valid_threats_sarif)
        .expect("valid threats sarif marker");

    let invalid_risk_scores = tachi_shell::commands::CommandOutput {
        status: 0,
        stdout: String::from("unexpected"),
        stderr: String::new(),
    };
    let err = validate_invoke_output("risk-scores-sarif", &invalid_risk_scores)
        .expect_err("reject malformed risk scores sarif marker");
    assert!(err.contains("risk scores SARIF output missing completion marker"));
}

#[test]
fn render_schema_error_includes_command_and_reason() {
    let err = render_schema_error("threats-sarif", "--input is required");
    assert!(err.contains("threats-sarif"));
    assert!(err.contains("--input is required"));
}
