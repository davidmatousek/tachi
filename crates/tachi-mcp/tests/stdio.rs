use std::io::Cursor;

use serde_json::json;

use tachi_mcp::server::McpServer;
use tachi_mcp::stdio::{serve, startup_mode_from_args, StdioWireResponse};
use tachi_mcp::tools::McpOutputMode;

#[test]
fn stdio_startup_requires_explicit_flag() {
    let err = startup_mode_from_args(&["tachi-mcp".to_string()])
        .expect_err("stdio mode should require an explicit flag");
    assert!(err.contains("--stdio"));
}

#[test]
fn stdio_startup_accepts_explicit_flag() {
    let args = vec!["tachi-mcp".to_string(), "--stdio".to_string()];
    assert!(startup_mode_from_args(&args).is_ok());
}

#[test]
fn stdio_transport_serves_one_tool_call() {
    let server = McpServer::default();
    let temp_root = std::env::temp_dir().join(format!("tachi-mcp-stdio-{}", std::process::id()));
    let request = json!({
        "id": "1",
        "tool": "tachi.coverage-audit",
        "input": {
            "repo_root": temp_root,
            "output_mode": "artifact"
        }
    });
    let mut output = Vec::new();
    serve(Cursor::new(format!("{}\n", request)), &mut output, &server).expect("serve request");
    let response: StdioWireResponse = serde_json::from_slice(&output).expect("decode response");
    assert!(response.ok);
    let result = response.result.expect("tool result");
    assert_eq!(result.output_mode, McpOutputMode::Artifact);
    assert_eq!(result.tool_name, "tachi.coverage-audit");
}
