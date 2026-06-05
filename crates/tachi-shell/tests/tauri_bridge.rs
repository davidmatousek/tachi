use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;

use tachi_shell::tauri_bridge::dispatch_command;

fn fixture_repo() -> PathBuf {
    let root = std::env::temp_dir().join(format!(
        "tachi-rust-tauri-bridge-{}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(root.join("scripts")).expect("create fixture scripts");
    root
}

fn write_executable_file(path: &PathBuf, content: &str) {
    fs::write(path, content).expect("write temporary script");
    let mut perms = fs::metadata(path).expect("read metadata").permissions();
    perms.set_mode(0o755);
    fs::set_permissions(path, perms).expect("set executable mode");
}

#[test]
fn dispatch_command_routes_bootstrap_to_update_with_prefix() {
    let root = fixture_repo();
    write_executable_file(
        &root.join("scripts/update.sh"),
        "#!/usr/bin/env bash\nfor arg in \"$@\"; do printf '%s\\n' \"$arg\"; done\n",
    );

    let output = dispatch_command("bootstrap", &root, &["--yes"]);

    assert_eq!(output.status, 0);
    let lines: Vec<_> = output.stdout.lines().collect();
    assert_eq!(lines, vec!["--bootstrap", "--yes"]);
}

#[test]
fn dispatch_command_rejects_unknown_command() {
    let root = fixture_repo();

    let output = dispatch_command("unknown", &root, &[]);

    assert_ne!(output.status, 0);
    assert!(output.stderr.contains("unsupported command"));
}
