use std::fs;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, OnceLock};

use serde_json::json;

use tachi_mcp::server::McpServer;
use tachi_mcp::tools::{tool_registry, McpAuthorizationPolicy, McpOutputMode, McpRequestContext};

static CLEANUP_ROOT: OnceLock<Mutex<Option<PathBuf>>> = OnceLock::new();
static CLEANUP_CALLS: AtomicUsize = AtomicUsize::new(0);

fn cleanup_root_slot() -> &'static Mutex<Option<PathBuf>> {
    CLEANUP_ROOT.get_or_init(|| Mutex::new(None))
}

fn record_cancel_cleanup(_context: &McpRequestContext) {
    CLEANUP_CALLS.fetch_add(1, Ordering::SeqCst);
    if let Some(root) = cleanup_root_slot()
        .lock()
        .expect("cleanup root lock")
        .take()
    {
        let _ = fs::remove_dir_all(root.join("target").join("mcp"));
    }
}

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

#[test]
fn cancelled_request_invokes_cleanup_hook_and_removes_artifacts() {
    CLEANUP_CALLS.store(0, Ordering::SeqCst);
    let root = temp_root("cleanup");
    fs::create_dir_all(root.join("target").join("mcp")).expect("create cleanup root");
    let artifact_path = root.join("target").join("mcp").join("coverage-audit.txt");
    fs::write(&artifact_path, "stale artifact").expect("seed stale artifact");
    *cleanup_root_slot().lock().expect("cleanup root lock") = Some(root.clone());

    let server = McpServer::new(
        tool_registry(),
        McpAuthorizationPolicy::allow_all(),
        Some(record_cancel_cleanup),
    );

    let err = server
        .invoke_json(
            &McpRequestContext {
                request_id: String::from("req-session-cleanup"),
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
    assert_eq!(CLEANUP_CALLS.load(Ordering::SeqCst), 1);
    assert!(!artifact_path.exists());
    assert!(!root.join("target").join("mcp").exists());
}
