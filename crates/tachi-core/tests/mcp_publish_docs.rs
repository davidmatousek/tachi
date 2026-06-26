use std::fs;
use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read_doc(path: &str) -> String {
    fs::read_to_string(repo_root().join(path))
        .unwrap_or_else(|err| panic!("read doc {path}: {err}"))
}

#[test]
fn mcp_publish_docs_share_the_same_install_and_validation_contract() {
    let readme = read_doc("README.md");
    let compatibility = read_doc("docs/platform-compatibility.md");
    let guide = read_doc("docs/guides/DEVELOPER_GUIDE_TACHI.md");

    for doc in [&readme, &compatibility, &guide] {
        assert!(
            doc.contains("cargo build -p tachi-mcp --features stdio"),
            "doc must describe building the standalone MCP server"
        );
        assert!(
            doc.contains("cargo run -p tachi-mcp --features stdio -- --stdio"),
            "doc must describe running the standalone MCP server in stdio mode"
        );
        assert!(
            doc.contains("tachi.coverage-audit"),
            "doc must name the canonical MCP tool surface"
        );
        assert!(
            doc.contains("target/mcp/coverage-audit.txt"),
            "doc must keep canonical MCP artifact paths stable"
        );
        assert!(
            doc.contains("cargo test -p tachi-mcp --test contract_snapshot --test schema_snapshot --test tools_registration --test session_policy --test stdio"),
            "doc must point at the MCP validation suite"
        );
    }
}
