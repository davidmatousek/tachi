use std::fs;
use std::path::PathBuf;

use serde_json::json;

use tachi_mcp::server::McpServer;
use tachi_mcp::tools::{McpOutputMode, McpRequestContext};

fn temp_root(name: &str) -> PathBuf {
    std::env::temp_dir().join(format!(
        "tachi-mcp-{name}-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}

fn context(request_id: &str) -> McpRequestContext {
    McpRequestContext::new(request_id)
}

#[test]
fn registered_tools_match_the_analysis_surface_only() {
    let server = McpServer::default();
    let expected = [
        ("tachi.coverage-audit", "coverage-audit", "coverage-summary"),
        ("tachi.infographic-data", "infographic-data", "json"),
        ("tachi.report-data", "report-data", "typst"),
        ("tachi.risk-scores-sarif", "risk-scores-sarif", "sarif"),
        ("tachi.threats-sarif", "threats-sarif", "sarif"),
    ];

    assert_eq!(
        server.registered_tool_names(),
        expected
            .iter()
            .map(|(tool, _, _)| *tool)
            .collect::<Vec<_>>()
    );

    for (spec, (tool_name, command_name, output_kind)) in
        server.registered_tools().iter().zip(expected)
    {
        assert_eq!(spec.tool_name, tool_name);
        assert_eq!(spec.command_name, command_name);
        assert_eq!(spec.output_kind, output_kind);
    }
}

#[test]
fn coverage_audit_writes_canonical_artifact_and_returns_metadata() {
    let server = McpServer::default();
    let root = temp_root("coverage-audit");
    fs::create_dir_all(&root).expect("create temp root");

    let result = server
        .invoke_json(
            &context("req-coverage-audit"),
            "tachi.coverage-audit",
            &json!({
                "repo_root": root.to_string_lossy().to_string(),
                "output_mode": "artifact",
            }),
        )
        .expect("tool invocation");

    assert_eq!(result.tool_name, "tachi.coverage-audit");
    assert_eq!(result.request_id, "req-coverage-audit");
    assert_eq!(result.command_name, "coverage-audit");
    assert_eq!(result.output_mode, McpOutputMode::Artifact);
    assert!(!result.cancelled);

    let artifact_path = result.artifact_path.expect("artifact path");
    assert_eq!(
        artifact_path,
        root.join("target").join("mcp").join("coverage-audit.txt")
    );
    let written = fs::read_to_string(&artifact_path).expect("artifact content");
    assert_eq!(written, result.payload);
    assert!(!written.is_empty());
}

#[test]
fn unknown_tool_calls_fail_closed() {
    let server = McpServer::default();
    let err = server
        .invoke_json(&context("req-unknown"), "tachi.install", &json!({}))
        .expect_err("unknown tool should fail closed");

    assert!(err.contains("authorization error"));
}
