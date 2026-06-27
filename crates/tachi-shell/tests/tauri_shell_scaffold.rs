use std::path::PathBuf;

#[test]
fn src_tauri_shell_scaffold_exists() {
    let repo_root = repo_root();
    assert!(repo_root.join("crates/tachi-desktop/Cargo.toml").is_file());
    assert!(repo_root.join("crates/tachi-desktop/src/lib.rs").is_file());
    assert!(repo_root.join("src-tauri/Cargo.toml").is_file());
    assert!(repo_root.join("src-tauri/src/main.rs").is_file());
}

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|path| path.parent())
        .expect("repo root")
        .to_path_buf()
}
