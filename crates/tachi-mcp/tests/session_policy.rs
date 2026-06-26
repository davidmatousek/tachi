use std::fs;
use std::path::PathBuf;

use serde_json::json;

use tachi_mcp::server::McpServer;
use tachi_mcp::tools::{McpOutputMode, McpRequestContext};

fn temp_root(name: &str) -> PathBuf {
    std::env::temp_dir().join(format!(
        "tachi-mcp-session-{name}-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ))
}

#[test]
fn request_id_is_preserved_through_tool_invocation() {
    let server = McpServer::default();
    let root = temp_root("request-id");
    fs::create_dir_all(&root).expect("create temp root");

    let result = server
        .invoke_json(
            &McpRequestContext::new("req-session-1"),
            "tachi.coverage-audit",
            &json!({
                "repo_root": root.to_string_lossy().to_string(),
                "output_mode": "in-band",
            }),
        )
        .expect("tool invocation");

    assert_eq!(result.request_id, "req-session-1");
    assert_eq!(result.output_mode, McpOutputMode::InBand);
    assert!(!result.cancelled);
}

#[test]
fn cancelled_request_fails_closed_without_writing_artifacts() {
    let server = McpServer::default();
    let root = temp_root("cancelled");
    fs::create_dir_all(&root).expect("create temp root");
    let artifact_path = root.join("target").join("mcp").join("coverage-audit.txt");

    let err = server
        .invoke_json(
            &McpRequestContext {
                request_id: String::from("req-session-cancelled"),
                cancelled: true,
            },
            "tachi.coverage-audit",
            &json!({
                "repo_root": root.to_string_lossy().to_string(),
                "output_mode": "artifact",
            }),
        )
        .expect_err("cancelled request should fail closed");

    assert!(err.contains("cancelled"));
    assert!(!artifact_path.exists());
}
