use std::fs;
use std::path::{Path, PathBuf};

#[test]
fn infographic_command_dispatch_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root.join("tests/scripts/test_command_dispatch.py").exists(),
        "infographic command-dispatch coverage should live in Rust tests, not pytest"
    );

    let command_path = root.join(".claude/commands/tachi.infographic.md");
    let content = fs::read_to_string(&command_path).expect("read infographic command file");

    let expansion_line = content
        .lines()
        .find(|line| line.to_ascii_lowercase().contains("\"all\" expands to:"))
        .expect("command file should document the all shorthand expansion");
    assert!(
        expansion_line.contains("executive-architecture"),
        "`all` shorthand expansion must include executive-architecture; found {expansion_line:?}"
    );

    let exec_alias_lines = content
        .lines()
        .filter(|line| line_has_standalone_exec_token(line))
        .collect::<Vec<_>>();
    assert!(
        !exec_alias_lines.is_empty(),
        "command file should document standalone exec as an alias"
    );
    assert!(
        exec_alias_lines
            .iter()
            .any(|line| line.contains("executive-architecture")),
        "exec alias must explicitly map to executive-architecture; found {exec_alias_lines:?}"
    );
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn line_has_standalone_exec_token(line: &str) -> bool {
    line.split(|ch: char| !(ch.is_ascii_alphanumeric() || ch == '-'))
        .any(|token| token == "exec")
}
