use std::fs;
use std::path::{Path, PathBuf};

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("repo root")
        .to_path_buf()
}

fn read(path: impl AsRef<Path>) -> String {
    let path = repo_root().join(path);
    fs::read_to_string(&path).unwrap_or_else(|err| panic!("read {}: {err}", path.display()))
}

#[test]
fn tauri_shell_declares_config_and_least_privilege_capability() {
    let config = read("src-tauri/tauri.conf.json");
    let capability = read("src-tauri/capabilities/main.json");

    for required in [
        "\"identifier\"",
        "\"productName\"",
        "\"windows\"",
        "\"security\"",
        "\"csp\"",
    ] {
        assert!(
            config.contains(required),
            "tauri.conf.json must declare {required}"
        );
    }

    for required in [
        "\"identifier\": \"main-capability\"",
        "\"windows\": [\"main\"]",
        "\"permissions\"",
        "\"core:default\"",
    ] {
        assert!(
            capability.contains(required),
            "main capability must declare {required}"
        );
    }

    assert!(
        !capability.contains("\"fs:allow"),
        "main capability must not grant filesystem permissions before AQ-023"
    );
    assert!(
        !capability.contains("\"shell:allow"),
        "main capability must not grant shell permissions before typed command policy"
    );
}

#[test]
fn tauri_run_is_not_empty_scaffold() {
    let lib_rs = read("src-tauri/src/lib.rs");

    assert!(
        !lib_rs.contains("pub fn run() {}"),
        "src-tauri run() must not remain an empty scaffold"
    );
    assert!(
        lib_rs.contains("registered_commands()"),
        "run boundary should stay tied to the shared registered command surface"
    );
}

#[test]
fn tauri_run_exposes_a_real_desktop_dispatch_entrypoint() {
    let lib_rs = read("src-tauri/src/lib.rs");

    assert!(
        lib_rs.contains("dispatch_desktop_command_owned"),
        "run boundary must register a typed desktop dispatch command"
    );
    assert!(
        lib_rs.contains("generate_handler![")
            && lib_rs.contains("desktop_registered_commands")
            && lib_rs.contains("dispatch_desktop_command_owned"),
        "desktop app must expose the shared registry plus the typed dispatcher"
    );
}
