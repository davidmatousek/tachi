use std::fs;
use std::path::PathBuf;

use serde_json::json;

use tachi_mcp::server::McpServer;
use tachi_mcp::tools::{tool_registry, McpAuthorizationPolicy, McpRequestContext};

fn temp_root(name: &str) -> PathBuf {
    std::env::temp_dir().join(format!(
        "tachi-mcp-policy-{name}-{}-{}",
        std::process::id(),
        std::thread::current().name().unwrap_or("thread")
    ))
}

#[test]
fn policy_allowlist_rejects_unknown_and_disallowed_tools_without_execution() {
    let server = McpServer::new(
        tool_registry(),
        McpAuthorizationPolicy::allow_tools(["tachi.coverage-audit"]),
        None,
    );
    let root = temp_root("deny");
    let _ = fs::remove_dir_all(&root);
    fs::create_dir_all(&root).expect("create temp root");

    let denied = server
        .invoke_json(
            &McpRequestContext::new("req-policy-deny"),
            "tachi.report-data",
            &json!({
                "target_dir": root.to_string_lossy().to_string(),
                "template_dir": root.join("templates").to_string_lossy().to_string(),
                "output_mode": "artifact",
            }),
        )
        .expect_err("policy mismatch should fail closed");
    assert!(denied.contains("authorization error"));
    assert!(!root.join("mcp").exists());

    let unknown = server
        .invoke_json(
            &McpRequestContext::new("req-policy-unknown"),
            "tachi.install",
            &json!({}),
        )
        .expect_err("unknown tool should fail closed");
    assert!(unknown.contains("authorization error"));
    assert!(!root.join("mcp").exists());

    let _ = fs::remove_dir_all(&root);
}
